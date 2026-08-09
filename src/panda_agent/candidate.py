"""Frozen-candidate manifests for reproducible M6 development runs."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from panda_agent.evaluation_runner import package_versions, prompt_fingerprint
from panda_agent.indexing import IndexIdentity, normalized_dir
from panda_agent.llm.vertex import VertexSettings
from panda_agent.storage import Storage


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return _sha256_bytes(path.read_bytes())


def _tree_hash(root: Path) -> str:
    entries: list[bytes] = []
    if not root.is_dir():
        raise FileNotFoundError(root)
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in {"__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        relative = path.relative_to(root).as_posix().encode("utf-8")
        entries.append(relative + b"\0" + path.read_bytes() + b"\0")
    return _sha256_bytes(b"".join(entries))


def _docker_images(project_root: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["docker", "compose", "images", "--format", "json"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "unavailable", "error": type(exc).__name__}
    if result.returncode != 0:
        return {"status": "unavailable", "error": result.stderr.strip()[:500]}
    try:
        raw = result.stdout.strip()
        if not raw:
            images: Any = []
        elif raw.startswith("["):
            images = json.loads(raw)
        else:
            images = [json.loads(line) for line in raw.splitlines() if line.strip()]
        return {"status": "ok", "images": images}
    except json.JSONDecodeError:
        return {"status": "unavailable", "error": "docker output was not JSON"}


def _qdrant_state(storage: Storage, expected_dimensions: int) -> dict[str, Any]:
    """Capture bounded collection identity without scanning all points."""
    try:
        collection = storage.qdrant.get_collection(storage.settings.collection_name)
        dense = collection.config.params.vectors.get("dense")
        points = storage.qdrant.count(
            collection_name=storage.settings.collection_name,
            exact=True,
        ).count
        dimensions = getattr(dense, "size", None)
        return {
            "status": "ok",
            "collection_name": storage.settings.collection_name,
            "points_count": int(points),
            "dense_dimensions": dimensions,
            "expected_dense_dimensions": expected_dimensions,
            "dimensions_match": dimensions == expected_dimensions,
        }
    except Exception as exc:
        return {
            "status": "unavailable",
            "collection_name": storage.settings.collection_name,
            "error_type": type(exc).__name__,
        }


def _current_manifest(project_root: Path, candidate_id: str) -> dict[str, Any]:
    settings = VertexSettings.from_env()
    source_manifest = project_root / "data" / "manifests" / "source_manifest.json"
    dataset = project_root / "evaluation" / "benchmarks" / "v2" / "gold_questions.yaml"
    audit = project_root / "evaluation" / "benchmarks" / "v2" / "audit_resolution.yaml"
    normalized = normalized_dir(project_root)
    ingestion_report = json.loads(
        (normalized / "ingestion_report.json").read_text(encoding="utf-8")
    )
    storage = Storage()
    try:
        with storage.connect() as connection:
            row = connection.execute(
                "SELECT fingerprint,payload FROM index_identities WHERE collection_name=%s",
                (storage.settings.collection_name,),
            ).fetchone()
    except Exception as exc:
        raise RuntimeError(
            f"index database is unavailable ({type(exc).__name__})"
        ) from exc
    if row is None:
        raise RuntimeError("index identity is missing; verify the index before freezing")
    expected_identity = IndexIdentity.from_settings(settings).fingerprint()
    if row[0] != expected_identity:
        raise RuntimeError(
            f"index identity mismatch: database={row[0]}, configured={expected_identity}"
        )
    protected_files = {
        "pyproject.toml": _sha256_file(project_root / "pyproject.toml"),
        ".env.example": _sha256_file(project_root / ".env.example"),
        "gold_questions.yaml": _sha256_file(dataset),
        "audit_resolution.yaml": _sha256_file(audit),
        "retrieval_policies.yaml": _sha256_file(
            project_root / "configs" / "retrieval_policies.yaml"
        ),
        "query_expansions.yaml": _sha256_file(
            project_root / "configs" / "query_expansions.yaml"
        ),
    }
    qdrant = _qdrant_state(storage, settings.embedding_dimensions)
    if qdrant.get("status") != "ok" or not qdrant.get("dimensions_match"):
        raise RuntimeError("Qdrant collection is unavailable or has the wrong dense dimension")
    return {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "status": "frozen",
        "frozen_at": datetime.now(UTC).isoformat(),
        "python_version": platform.python_version(),
        "package_versions": package_versions(),
        "source_manifest_hash": _sha256_file(source_manifest),
        "normalized_output_hashes": ingestion_report["output_hashes"],
        "normalized_report_hash": _sha256_file(normalized / "ingestion_report.json"),
        "index_identity": row[0],
        "index_fingerprint": row[0],
        "index_identity_payload": row[1],
        "qdrant": qdrant,
        "runtime_generation_model_id": settings.generation_model,
        "evaluation_judge_model_id": settings.evaluation_judge_model,
        "embedding_model_id": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
        "vertex_location": settings.location,
        "prompt_version": __import__("panda_agent.prompts", fromlist=["PROMPT_SET_VERSION"]).PROMPT_SET_VERSION,
        "prompt_hash": prompt_fingerprint(),
        "retrieval_policy_hash": protected_files["retrieval_policies.yaml"],
        "query_expansion_hash": protected_files["query_expansions.yaml"],
        "gold_dataset_hash": protected_files["gold_questions.yaml"],
        "audit_resolution_hash": protected_files["audit_resolution.yaml"],
        "protected_file_hashes": protected_files,
        "source_tree_hash": _tree_hash(project_root / "src"),
        "config_tree_hash": _tree_hash(project_root / "configs"),
        "migration_tree_hash": _tree_hash(project_root / "migrations"),
        "docker": _docker_images(project_root),
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def freeze_candidate(project_root: Path, candidate_id: str) -> dict[str, Any]:
    if not candidate_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in candidate_id):
        raise ValueError("candidate_id must contain only letters, digits, '-' or '_'")
    candidate_dir = project_root / "evaluation" / "candidates" / candidate_id
    manifest_path = candidate_dir / "candidate_manifest.json"
    manifest = _current_manifest(project_root, candidate_id)
    if manifest["docker"].get("status") != "ok":
        raise RuntimeError("Docker image digests are unavailable; candidate cannot be frozen")
    # Do not leave an empty candidate directory when the environment gate fails.
    candidate_dir.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        comparable_existing = {key: value for key, value in existing.items() if key != "frozen_at"}
        comparable_current = {key: value for key, value in manifest.items() if key != "frozen_at"}
        if comparable_existing != comparable_current:
            raise ValueError("candidate already exists with a different frozen identity")
    else:
        _write_json(manifest_path, manifest)
    digest = _sha256_file(manifest_path)
    (candidate_dir / "candidate_manifest.sha256").write_text(
        f"{digest}  candidate_manifest.json\n", encoding="utf-8"
    )
    (candidate_dir / "freeze.lock").write_text(
        json.dumps(
            {"candidate_id": candidate_id, "manifest_sha256": digest, "status": "frozen"},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"candidate_id": candidate_id, "manifest": str(manifest_path), "manifest_sha256": digest}


def verify_candidate(project_root: Path, candidate_id: str) -> dict[str, Any]:
    candidate_dir = project_root / "evaluation" / "candidates" / candidate_id
    manifest_path = candidate_dir / "candidate_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"candidate does not exist: {candidate_id}")
    expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = _current_manifest(project_root, candidate_id)
    immutable_keys = [key for key in expected if key != "frozen_at"]
    mismatches = [key for key in immutable_keys if expected.get(key) != current.get(key)]
    digest = _sha256_file(manifest_path)
    lock = json.loads((candidate_dir / "freeze.lock").read_text(encoding="utf-8"))
    valid = not mismatches and lock.get("manifest_sha256") == digest
    return {
        "candidate_id": candidate_id,
        "valid": valid,
        "manifest_sha256": digest,
        "mismatches": mismatches,
    }
