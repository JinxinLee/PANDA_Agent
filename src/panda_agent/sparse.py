"""Authoritative local FastEmbed sparse encoder contract."""

from __future__ import annotations

import hashlib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from fastembed import SparseTextEmbedding
from pydantic import BaseModel, ConfigDict, Field

from panda_agent.config import (
    BM25_HASH,
    BM25_STEMMER,
    BM25_TOKENIZER,
    FastEmbedSettings,
    SPARSE_VECTOR_MODIFIER,
)


class SparseContractError(RuntimeError):
    """The local sparse encoder cannot satisfy the configured contract."""


class SparseEncoderReceipt(BaseModel):
    """Portable semantic identity for the installed English BM25 encoder."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    model_name: str
    language: str
    vector_name: str
    modifier: str
    k: float
    b: float
    avg_len: float = Field(gt=0)
    token_max_length: int = Field(gt=0)
    disable_stemmer: bool
    tokenizer: str
    stemmer: str
    hash_function: str
    fastembed_version: str
    mmh3_version: str
    py_rust_stemmers_version: str
    stopwords_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def _distribution_version(distribution: str) -> str:
    try:
        return version(distribution)
    except PackageNotFoundError as exc:
        raise SparseContractError(f"required sparse distribution is unavailable: {distribution}") from exc


def _stopwords_sha256(settings: FastEmbedSettings) -> str:
    path = settings.model_path / f"{settings.language}.txt"
    if not path.is_file():
        raise SparseContractError(f"FastEmbed stopword asset is missing: {path}")
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise SparseContractError(f"cannot read FastEmbed stopword asset: {path}") from exc


def sparse_receipt(settings: FastEmbedSettings) -> SparseEncoderReceipt:
    """Build the portable receipt without encoding text or downloading assets."""
    if not settings.model_path.is_dir():
        raise SparseContractError(
            f"FastEmbed model path does not exist or is not a directory: {settings.model_path}"
        )
    if not settings.local_files_only:
        raise SparseContractError("the PANDA sparse encoder must be local-files-only")
    return SparseEncoderReceipt(
        model_name=settings.model_name,
        language=settings.language,
        vector_name=settings.vector_name,
        modifier=SPARSE_VECTOR_MODIFIER,
        k=settings.k,
        b=settings.b,
        avg_len=settings.avg_len,
        token_max_length=settings.token_max_length,
        disable_stemmer=settings.disable_stemmer,
        tokenizer=BM25_TOKENIZER,
        stemmer=BM25_STEMMER,
        hash_function=BM25_HASH,
        fastembed_version=_distribution_version("fastembed"),
        mmh3_version=_distribution_version("mmh3"),
        py_rust_stemmers_version=_distribution_version("py-rust-stemmers"),
        stopwords_sha256=_stopwords_sha256(settings),
    )


def sparse_settings(project_root: str | Path, *, model_path: Path | None = None) -> FastEmbedSettings:
    """Return canonical settings for either the project or installed bundle runtime."""
    if model_path is None:
        return FastEmbedSettings.from_env(project_root)
    return FastEmbedSettings(model_path=Path(model_path).resolve())


def sparse_factory_kwargs(settings: FastEmbedSettings) -> dict[str, Any]:
    """Constructor arguments whose defaults are part of the receipt above."""
    return {
        "model_name": settings.model_name,
        "specific_model_path": str(settings.model_path),
        "local_files_only": True,
        "language": settings.language,
        "k": settings.k,
        "b": settings.b,
        "avg_len": settings.avg_len,
        "token_max_length": settings.token_max_length,
        "disable_stemmer": settings.disable_stemmer,
    }


def create_sparse_encoder(
    project_root: str | Path,
    *,
    model_path: Path | None = None,
    settings: FastEmbedSettings | None = None,
) -> tuple[SparseTextEmbedding, SparseEncoderReceipt]:
    """Construct the sole local-only encoder and its exact semantic receipt."""
    active = settings or sparse_settings(project_root, model_path=model_path)
    receipt = sparse_receipt(active)
    try:
        return SparseTextEmbedding(**sparse_factory_kwargs(active)), receipt
    except Exception as exc:
        raise SparseContractError("cannot construct the local FastEmbed sparse encoder") from exc
