"""Local runtime registration and readiness checks.

Knowledge bundle verification deliberately stops before this boundary.  Runtime
registration records only the verified knowledge and service identities, never
evaluation or prompt receipts.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from typing import Any, Literal
from datetime import UTC, datetime

import requests
from pydantic import BaseModel, ConfigDict, Field

from panda_agent import kb_bundle
from panda_agent.storage import Storage, StorageSettings


RUNTIME_SCHEMA_VERSION = "panda-runtime-identity/v1"
RUNTIME_IDENTITY_PATH = Path("data") / "runtime" / "runtime_identity.json"
SERVICE_REVISION = "0005"
EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 3072


class RuntimeContractError(RuntimeError):
    """The local runtime does not meet the frozen registration contract."""


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EmbeddingIdentity(_StrictModel):
    model: str
    dimensions: int = Field(gt=0)


class RuntimeIdentity(_StrictModel):
    schema_version: Literal[RUNTIME_SCHEMA_VERSION] = RUNTIME_SCHEMA_VERSION
    service_revision: Literal[SERVICE_REVISION] = SERVICE_REVISION
    knowledge_revision: Literal[kb_bundle.KNOWLEDGE_REVISION] = kb_bundle.KNOWLEDGE_REVISION
    bundle_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    registered_at: datetime
    corpus_source_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    postgres: kb_bundle.PostgresState
    qdrant: kb_bundle.QdrantState
    fastembed: kb_bundle.FastEmbedState
    embedding: EmbeddingIdentity


def runtime_identity_path(project_root: Path) -> Path:
    return project_root.resolve() / RUNTIME_IDENTITY_PATH


def _embedding_identity(storage: Storage) -> EmbeddingIdentity:
    with storage.connect() as connection:
        model, dimensions = kb_bundle._current_index_identity(connection, storage.settings.collection_name)
    return EmbeddingIdentity(model=model, dimensions=dimensions)


def _dense_dimensions(qdrant: kb_bundle.QdrantState) -> int | None:
    dense = qdrant.dense_config.get("dense")
    if isinstance(dense, dict):
        value = dense.get("size")
        return int(value) if isinstance(value, int) else None
    return None


def _collect_actual(
    settings: StorageSettings | None, session: requests.Session | None,
) -> tuple[kb_bundle.PostgresState, kb_bundle.QdrantState, kb_bundle.FastEmbedState, EmbeddingIdentity]:
    storage = Storage(settings)
    session = session or requests.Session()
    postgres = kb_bundle.postgres_state(storage)
    qdrant = kb_bundle.qdrant_state(session, storage.settings.qdrant_url, storage.settings.collection_name)
    return postgres, qdrant, kb_bundle.fastembed_state(qdrant), _embedding_identity(storage)


def _registration_checks(
    manifest: kb_bundle.BundleManifest,
    actual: tuple[kb_bundle.PostgresState, kb_bundle.QdrantState, kb_bundle.FastEmbedState, EmbeddingIdentity],
    project_root: Path,
) -> dict[str, bool]:
    postgres, qdrant, fastembed, embedding = actual
    return {
        "service_revision": postgres.revision == SERVICE_REVISION,
        "knowledge_revision": manifest.postgres.revision == kb_bundle.KNOWLEDGE_REVISION,
        "postgres_table_counts": postgres.table_counts == manifest.postgres.table_counts,
        "postgres_fingerprint": postgres.index_fingerprint == manifest.postgres.index_fingerprint,
        "qdrant_config": (
            qdrant.collection == manifest.qdrant.collection
            and qdrant.dense_config == manifest.qdrant.dense_config
            and qdrant.sparse_config == manifest.qdrant.sparse_config
            and qdrant.payload_indexes == manifest.qdrant.payload_indexes
        ),
        "qdrant_count": qdrant.point_count == manifest.qdrant.point_count,
        "fastembed": fastembed == manifest.fastembed,
        "bm25": kb_bundle._verify_runtime(project_root),
        "embedding_identity": (
            embedding.model == EMBEDDING_MODEL
            and embedding.dimensions == EMBEDDING_DIMENSIONS
            and _dense_dimensions(qdrant) == embedding.dimensions
        ),
    }


def _write_identity(path: Path, identity: RuntimeIdentity) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(identity.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=".runtime_identity.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def validate_runtime_state_without_receipt(
    bundle_dir: Path, *, project_root: Path, settings: StorageSettings | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Validate live runtime state without reading any prior runtime receipt."""
    manifest = kb_bundle.preflight_bundle(bundle_dir)
    actual = _collect_actual(settings, session)
    checks = _registration_checks(manifest, actual, project_root.resolve())
    return {"valid": all(checks.values()), "checks": checks, "manifest": manifest, "actual": actual}


def register_runtime(
    bundle_dir: Path, *, project_root: Path, settings: StorageSettings | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Strictly verify the live runtime, then atomically register its identity."""
    project_root = project_root.resolve()
    state = validate_runtime_state_without_receipt(
        bundle_dir, project_root=project_root, settings=settings, session=session,
    )
    if not state["valid"]:
        checks = state["checks"]
        failed = ", ".join(name for name, passed in checks.items() if not passed)
        raise RuntimeContractError(f"runtime registration checks failed: {failed}")
    manifest = state["manifest"]
    actual = state["actual"]
    checks = state["checks"]
    _, qdrant, fastembed, embedding = actual
    identity = RuntimeIdentity(
        corpus_source_manifest_sha256=manifest.corpus_source_manifest_sha256,
        bundle_manifest_sha256=kb_bundle.sha256_file(bundle_dir.resolve() / kb_bundle.MANIFEST_NAME),
        registered_at=datetime.now(UTC),
        postgres=manifest.postgres,
        qdrant=qdrant,
        fastembed=fastembed,
        embedding=embedding,
    )
    _write_identity(runtime_identity_path(project_root), identity)
    return {"valid": True, "runtime_status": "registered", "checks": checks}


def _load_identity(path: Path) -> RuntimeIdentity:
    try:
        return RuntimeIdentity.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeContractError(f"runtime identity is invalid: {path}") from exc


def verify_runtime(
    *, project_root: Path, settings: StorageSettings | None = None, session: requests.Session | None = None,
) -> dict[str, Any]:
    """Return runtime readiness; this is intentionally independent of kb verify."""
    path = runtime_identity_path(project_root)
    if not path.is_file():
        return {"valid": False, "runtime_status": "not_registered", "checks": {"registered": False}}
    try:
        identity = _load_identity(path)
        actual = _collect_actual(settings, session)
        postgres, qdrant, fastembed, embedding = actual
        checks = {
            "registered": True,
            "service_revision": postgres.revision == SERVICE_REVISION == identity.service_revision,
            "knowledge_revision": identity.knowledge_revision == kb_bundle.KNOWLEDGE_REVISION,
            "postgres_table_counts": postgres.table_counts == identity.postgres.table_counts,
            "postgres_fingerprint": postgres.index_fingerprint == identity.postgres.index_fingerprint,
            "qdrant_config": (
                qdrant.collection == identity.qdrant.collection
                and qdrant.dense_config == identity.qdrant.dense_config
                and qdrant.sparse_config == identity.qdrant.sparse_config
                and qdrant.payload_indexes == identity.qdrant.payload_indexes
            ),
            "qdrant_count": qdrant.point_count == identity.qdrant.point_count,
            "fastembed": fastembed == identity.fastembed,
            "bm25": kb_bundle._verify_runtime(project_root.resolve()),
            "embedding_identity": (
                embedding == identity.embedding
                and embedding.model == EMBEDDING_MODEL
                and embedding.dimensions == EMBEDDING_DIMENSIONS
                and _dense_dimensions(qdrant) == embedding.dimensions
            ),
        }
    except RuntimeContractError as exc:
        return {"valid": False, "runtime_status": "invalid_identity", "checks": {"registered": False}, "error": str(exc)}
    return {"valid": all(checks.values()), "runtime_status": "registered", "checks": checks}
