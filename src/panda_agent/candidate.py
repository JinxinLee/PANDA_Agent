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

from panda_agent.evaluation import newest_signed_exposed_gold_dir
from panda_agent.evaluation_runner import package_versions, prompt_fingerprint, repository_identity
from panda_agent.indexing import IndexIdentity, normalized_dir
from panda_agent.llm.vertex import VertexSettings
from panda_agent.qa import DEFAULT_ANSWER_POINT_MODE
from panda_agent.storage import Storage


# F6-A authoritative exposed benchmark: the freezer must bind the same signed
# identity the evaluator resolves (m6-benchmark-v2.6), not the historical v2.
# F6-A Docker contract (Option A): the compose-managed PostgreSQL/Qdrant
# services materially define the evaluated runtime's data infrastructure, so
# their image identities are release-critical and must be captured non-empty.
REQUIRED_DOCKER_SERVICES = ("postgres", "qdrant")


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
    """Capture the identities of the currently running data-infrastructure
    containers (the compose-managed PostgreSQL/Qdrant pair), independent of the
    compose project name context."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "json"],
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
        images: Any = []
        if raw:
            for line in raw.splitlines():
                if not line.strip():
                    continue
                entry = json.loads(line)
                if isinstance(entry, dict):
                    images.append(
                        {
                            "Name": entry.get("Names") or entry.get("Name"),
                            "Image": entry.get("Image"),
                            "ID": entry.get("ID"),
                            "State": entry.get("State"),
                        }
                    )
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


def _benchmark_identity(project_root: Path) -> dict[str, Any]:
    """Validate and record the signed exposed-benchmark identity for the freeze.

    Enforces the same authority contract as the evaluator: the manifest's
    dataset hash must match the file, the official-validation flags must both
    be true, and the version must be the current authoritative benchmark.
    """
    # GOLD-9: the freezer binds the same signed exposed benchmark the
    # evaluator resolves — the newest directory with a consistent
    # official-ready manifest — never a hard-coded older authority.
    benchmark_dir = newest_signed_exposed_gold_dir(project_root)
    manifest_path = benchmark_dir / "benchmark_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dataset_hash = _sha256_file(benchmark_dir / manifest["dataset"])
    if manifest.get("dataset_sha256") != dataset_hash:
        raise RuntimeError(
            "benchmark manifest dataset hash mismatch for the resolved "
            f"{benchmark_dir.name} identity"
        )
    official = manifest.get("project_official_validation") or {}
    if official.get("official_ready") is not True or official.get("structurally_valid") is not True:
        raise RuntimeError(
            "benchmark manifest is not official-ready/structurally-valid for release identity"
        )
    return {
        "benchmark_manifest_sha256": _sha256_file(manifest_path),
        "benchmark_version": manifest["benchmark_version"],
        "benchmark_question_count": manifest["question_count"],
        "benchmark_dataset_sha256": dataset_hash,
        "benchmark_official_ready": True,
        "benchmark_structurally_valid": True,
        "benchmark_status": manifest["status"],
    }


def _docker_release_identity(images: dict[str, Any]) -> dict[str, Any]:
    """Enforce the Option-A Docker contract: required service images must be
    captured with concrete identities (no empty image set)."""
    if images.get("status") != "ok":
        return {"release_critical": True, "satisfied": False, "reason": "docker unavailable"}
    entries = images.get("images") or []
    if not entries:
        return {"release_critical": True, "satisfied": False, "reason": "no compose images recorded"}
    names = " ".join(
        str(entry.get("Service") or entry.get("Name") or entry.get("Image") or "")
        for entry in entries
        if isinstance(entry, dict)
    ).casefold()
    missing = [service for service in REQUIRED_DOCKER_SERVICES if service not in names]
    if missing:
        return {
            "release_critical": True,
            "satisfied": False,
            "reason": f"required compose services missing from image identity: {missing}",
        }
    return {"release_critical": True, "satisfied": True, "services": list(REQUIRED_DOCKER_SERVICES)}


def _implementation_git_commit(project_root: Path) -> str:
    """Record the exact implementation HEAD the candidate freezes from."""
    return repository_identity(project_root)["commit"]


def _product_scope_identity(project_root: Path) -> dict[str, Any]:
    """Record the reviewed product-language calibration identity and the exact
    formal-English selector output hash, enforcing the same calibration/dataset
    compatibility contract the evaluator enforces (freezer/evaluator authority
    equivalence, F6-A Stage A0 debt A)."""
    import hashlib as _hashlib

    from panda_agent.evaluation import (
        newest_signed_exposed_gold_dir,
        newest_product_language_calibration_path,
        calibration_compatibility,
        derive_product_language_ids,
        load_gold_dataset,
        load_product_language_calibration,
    )
    from panda_agent.evaluation_runner import default_gold_dataset_path

    calibration_path = newest_product_language_calibration_path(project_root)
    calibration = load_product_language_calibration(project_root)
    if calibration is None:
        return {"product_language_calibration_id": None, "formal_product_scope_selector_hash": None}
    dataset = load_gold_dataset(default_gold_dataset_path(project_root))
    compatibility = calibration_compatibility(
        calibration, dataset, dataset_path=default_gold_dataset_path(project_root)
    )
    if not compatibility["compatible"]:
        raise RuntimeError(
            f"product-language calibration incompatible with active Gold: "
            f"{compatibility['reason']}"
        )
    english_ids, _ = derive_product_language_ids(dataset, calibration)
    selector_canonical = json.dumps(sorted(english_ids), ensure_ascii=False)
    return {
        "product_language_calibration_id": calibration["calibration_id"],
        "product_language_calibration_sha256": _hashlib.sha256(
            calibration_path.read_bytes()
        ).hexdigest(),
        "formal_product_scope_selector_sha256": _hashlib.sha256(
            selector_canonical.encode("utf-8")
        ).hexdigest(),
        "formal_product_scope_selector_count": len(english_ids),
    }


def _current_manifest(project_root: Path, candidate_id: str) -> dict[str, Any]:
    settings = VertexSettings.from_env()
    source_manifest = project_root / "data" / "manifests" / "source_manifest.json"
    benchmark_dir = newest_signed_exposed_gold_dir(project_root)
    dataset = benchmark_dir / "gold_questions.yaml"
    adjudications = benchmark_dir / "manual_adjudications.yaml"
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
        "retrieval_policies.yaml": _sha256_file(
            project_root / "configs" / "retrieval_policies.yaml"
        ),
        "query_expansions.yaml": _sha256_file(
            project_root / "configs" / "query_expansions.yaml"
        ),
    }
    if adjudications.is_file():
        protected_files["manual_adjudications.yaml"] = _sha256_file(adjudications)
    qdrant = _qdrant_state(storage, settings.embedding_dimensions)
    if qdrant.get("status") != "ok" or not qdrant.get("dimensions_match"):
        raise RuntimeError("Qdrant collection is unavailable or has the wrong dense dimension")
    docker = _docker_images(project_root)
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
        "runtime_verification_model_id": settings.verification_model,
        "effective_verification_model_id": settings.effective_verification_model,
        "evaluation_judge_model_id": settings.evaluation_judge_model,
        "embedding_model_id": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
        "vertex_location": settings.location,
        "implementation_git_commit": _implementation_git_commit(project_root),
        "primary_answer_point_mode": DEFAULT_ANSWER_POINT_MODE,
        "prompt_version": __import__("panda_agent.prompts", fromlist=["PROMPT_SET_VERSION"]).PROMPT_SET_VERSION,
        "prompt_hash": prompt_fingerprint(),
        "retrieval_policy_hash": protected_files["retrieval_policies.yaml"],
        "query_expansion_hash": protected_files["query_expansions.yaml"],
        "gold_dataset_hash": protected_files["gold_questions.yaml"],
        "manual_adjudications_hash": protected_files.get("manual_adjudications.yaml"),
        **_benchmark_identity(project_root),
        **_product_scope_identity(project_root),
        "protected_file_hashes": protected_files,
        "source_tree_hash": _tree_hash(project_root / "src"),
        "config_tree_hash": _tree_hash(project_root / "configs"),
        "migration_tree_hash": _tree_hash(project_root / "migrations"),
        "docker": docker,
        "docker_release_identity": _docker_release_identity(docker),
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
    git_status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    if git_status.strip():
        raise RuntimeError(
            "implementation working tree must be clean when freezing a candidate; "
            "commit or stash implementation changes first (evaluation run artifacts "
            "generated after the freeze do not block verification)"
        )
    candidate_dir = project_root / "evaluation" / "candidates" / candidate_id
    manifest_path = candidate_dir / "candidate_manifest.json"
    manifest = _current_manifest(project_root, candidate_id)
    if manifest["docker"].get("status") != "ok":
        raise RuntimeError("Docker image digests are unavailable; candidate cannot be frozen")
    if not manifest["docker_release_identity"].get("satisfied"):
        raise RuntimeError(
            f"Docker release identity contract failed: "
            f"{manifest['docker_release_identity'].get('reason')}"
        )
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
    # The implementation HEAD may advance after the freeze through non-behavior
    # commits (preregistration bookkeeping, evaluation artifacts); the frozen
    # behavior identity (source/config/prompt/index hashes) is what must stay
    # identical. The recorded commit must simply be an ancestor of (or equal
    # to) the current HEAD so implementation rollback/branch switches fail.
    special_keys = {"implementation_git_commit"}
    mismatches = [
        key
        for key in immutable_keys
        if key not in special_keys and expected.get(key) != current.get(key)
    ]
    frozen_commit = expected.get("implementation_git_commit")
    current_commit = current.get("implementation_git_commit")
    if frozen_commit and current_commit:
        # The frozen implementation commit MAY be an ancestor of the current
        # HEAD (later documentation/evaluation-artifact commits are allowed),
        # but the source_tree_hash must match exactly: any src/ change after
        # the freeze invalidates current-checkout candidate verification
        # (F6-A-R1 §17). A post-run evaluator correction is recorded as a
        # separate offline rescore identity, never as byte-identity of the old
        # freeze.
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", frozen_commit, current_commit],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if ancestor.returncode != 0:
            mismatches.append("implementation_git_commit")
    elif frozen_commit != current_commit:
        mismatches.append("implementation_git_commit")
    digest = _sha256_file(manifest_path)
    lock = json.loads((candidate_dir / "freeze.lock").read_text(encoding="utf-8"))
    valid = not mismatches and lock.get("manifest_sha256") == digest
    return {
        "candidate_id": candidate_id,
        "valid": valid,
        "manifest_sha256": digest,
        "mismatches": mismatches,
    }
