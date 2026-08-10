"""Trusted local PANDA knowledge bundles; no remote embedding execution."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Callable, Literal, Sequence

import fastembed
from fastembed import SparseTextEmbedding
import requests
from pydantic import BaseModel, ConfigDict, Field, field_validator

from panda_agent.evaluator_catalog import (
    CATALOG_FILENAME,
    CATALOG_SCHEMA_VERSION,
    LOOKUP_CONTRACT,
    EvaluatorCatalogError,
    catalog_receipt,
    load_evaluator_catalog,
    write_evaluator_catalog,
)
from panda_agent.evaluation import load_gold_dataset
from panda_agent.evaluation_runner import default_gold_dataset_path, validate_gold_dataset
from panda_agent.indexing import normalized_dir, verify_index
from panda_agent.storage import Storage, StorageSettings


BUNDLE_SCHEMA_VERSION = "panda-knowledge-bundle/v2"
DATABASE_NAME = "panda_qa"
COLLECTION_NAME = "panda_knowledge_v1"
MANIFEST_NAME = "bundle_manifest.json"
POSTGRES_DUMP_NAME = "postgres.dump"
QDRANT_SNAPSHOT_NAME = "qdrant.snapshot"
RUNTIME_BM25_PATH = Path("runtime_assets") / "fastembed" / "bm25"
INSTALLED_RUNTIME_PATH = Path("data") / "runtime" / "fastembed" / "bm25"
EVALUATOR_CATALOG_PATH = Path("evaluator") / CATALOG_FILENAME
INSTALLED_EVALUATOR_CATALOG_PATH = Path("data") / "runtime" / "evaluator" / CATALOG_FILENAME
CANONICAL_GOLD_SHA256 = "b5406e36c64ee664f9e2ff9c0f42e354feb7164c81d8f1c7551d8f2ed1d0b687"
SAMPLE_SIZE = 100
SAMPLE_CANDIDATE_POOL_SIZE = SAMPLE_SIZE * 10
SELECTED_TABLES = (
    "source_versions", "knowledge_objects", "knowledge_aliases", "relation_edges", "workflow_steps",
    "index_identities",
)


class BundleError(RuntimeError):
    """A bundle contract precondition was not met."""


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ArtifactHash(_StrictModel):
    filename: Literal[POSTGRES_DUMP_NAME, QDRANT_SNAPSHOT_NAME, EVALUATOR_CATALOG_PATH.as_posix()]
    bytes: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class PostgresState(_StrictModel):
    database: Literal[DATABASE_NAME]
    revision: str
    table_counts: dict[str, int]
    index_fingerprint: str

    @field_validator("table_counts")
    @classmethod
    def exact_selected_tables(cls, value: dict[str, int]) -> dict[str, int]:
        if tuple(sorted(value)) != tuple(sorted(SELECTED_TABLES)) or any(count < 0 for count in value.values()):
            raise ValueError("table_counts must contain exactly the selected knowledge tables")
        return value


class FastEmbedState(_StrictModel):
    model: Literal["Qdrant/bm25"]
    vector_name: str
    language: Literal["english"]
    modifier: str | None = None
    fastembed_version: str


class QdrantState(_StrictModel):
    collection: Literal[COLLECTION_NAME]
    point_count: int = Field(ge=0)
    dense_config: dict[str, Any]
    sparse_config: dict[str, Any]
    payload_indexes: dict[str, Any]
    version: str | None = None


class VerificationSample(_StrictModel):
    object_id: str
    point_id: str
    source_id: str
    source_version_id: str


class EvaluatorCatalogState(_StrictModel):
    path: Literal[EVALUATOR_CATALOG_PATH.as_posix()]
    schema_version: Literal[CATALOG_SCHEMA_VERSION]
    lookup_contract: Literal[LOOKUP_CONTRACT]
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    count: int = Field(gt=0)
    source_gold_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class BundleManifest(_StrictModel):
    """Immutable receipt for an exactly local PANDA recovery bundle."""

    schema_version: Literal[BUNDLE_SCHEMA_VERSION]
    created_at: datetime
    corpus_source_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    postgres: PostgresState
    qdrant: QdrantState
    fastembed: FastEmbedState
    verification_samples: list[VerificationSample] = Field(min_length=SAMPLE_SIZE, max_length=SAMPLE_SIZE)
    postgres_dump: ArtifactHash
    qdrant_snapshot: ArtifactHash
    evaluator_catalog: EvaluatorCatalogState


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact(
    path: Path,
    filename: Literal[POSTGRES_DUMP_NAME, QDRANT_SNAPSHOT_NAME, EVALUATOR_CATALOG_PATH.as_posix()],
) -> ArtifactHash:
    return ArtifactHash(filename=filename, bytes=path.stat().st_size, sha256=sha256_file(path))


def _write_manifest(path: Path, manifest: BundleManifest) -> None:
    path.write_text(manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")


def load_manifest(bundle_dir: Path) -> BundleManifest:
    path = bundle_dir / MANIFEST_NAME
    try:
        return BundleManifest.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BundleError(f"bundle manifest is missing: {path}") from exc
    except ValueError as exc:
        raise BundleError(f"bundle manifest is invalid: {path}") from exc


def preflight_bundle(bundle_dir: Path) -> BundleManifest:
    """Validate local receipt and artefact hashes before any target interaction."""
    bundle_dir = bundle_dir.resolve()
    manifest = load_manifest(bundle_dir)
    for artefact in (manifest.postgres_dump, manifest.qdrant_snapshot):
        path = bundle_dir / artefact.filename
        if not path.is_file():
            raise BundleError(f"bundle artefact is missing: {path}")
        if path.stat().st_size != artefact.bytes or sha256_file(path) != artefact.sha256:
            raise BundleError(f"integrity mismatch for {artefact.filename}")
    runtime = bundle_dir / RUNTIME_BM25_PATH
    if not runtime.is_dir() or not any(runtime.iterdir()):
        raise BundleError(f"BM25 runtime asset is missing or empty: {runtime}")
    catalog_path = bundle_dir / manifest.evaluator_catalog.path
    try:
        receipt = catalog_receipt(catalog_path)
    except EvaluatorCatalogError as exc:
        raise BundleError(f"evaluator catalog is invalid: {exc}") from exc
    if (
        receipt.schema_version != manifest.evaluator_catalog.schema_version
        or receipt.lookup_contract != manifest.evaluator_catalog.lookup_contract
        or receipt.sha256 != manifest.evaluator_catalog.sha256
        or receipt.count != manifest.evaluator_catalog.count
    ):
        raise BundleError("evaluator catalog receipt mismatch")
    return manifest


def inspect_bundle(bundle_dir: Path) -> dict[str, Any]:
    return preflight_bundle(bundle_dir).model_dump(mode="json")


def exact_qdrant_count(session: requests.Session, qdrant_url: str, collection: str) -> int:
    response = session.post(
        f"{qdrant_url.rstrip('/')}/collections/{collection}/points/count",
        json={"exact": True}, timeout=60,
    )
    response.raise_for_status()
    return int(response.json()["result"]["count"])


def _qdrant_info(session: requests.Session, qdrant_url: str, collection: str) -> dict[str, Any]:
    response = session.get(f"{qdrant_url.rstrip('/')}/collections/{collection}", timeout=60)
    response.raise_for_status()
    result = response.json()["result"]
    if result.get("status") != "green":
        raise BundleError(f"Qdrant collection must be green, got: {result.get('status')!r}")
    return result


def _qdrant_version(session: requests.Session, qdrant_url: str) -> str | None:
    try:
        response = session.get(qdrant_url.rstrip("/"), timeout=60)
        response.raise_for_status()
        value = response.json().get("version")
        return str(value) if value is not None else None
    except (requests.RequestException, ValueError, KeyError):
        return None


def qdrant_state(session: requests.Session, qdrant_url: str, collection: str) -> QdrantState:
    info = _qdrant_info(session, qdrant_url, collection)
    params = info.get("config", {}).get("params", {})
    return QdrantState(
        collection=collection,
        point_count=exact_qdrant_count(session, qdrant_url, collection),
        dense_config=params.get("vectors", {}),
        sparse_config=params.get("sparse_vectors", {}),
        payload_indexes=info.get("payload_schema", {}),
        version=_qdrant_version(session, qdrant_url),
    )


def fastembed_state(qdrant: QdrantState) -> FastEmbedState:
    names = sorted(qdrant.sparse_config)
    if len(names) != 1:
        raise BundleError("Qdrant must have exactly one sparse vector configuration")
    sparse = qdrant.sparse_config[names[0]]
    modifier = sparse.get("modifier") if isinstance(sparse, dict) else None
    if modifier is not None and not isinstance(modifier, str):
        raise BundleError("Qdrant sparse modifier must be a string or null")
    return FastEmbedState(
        model="Qdrant/bm25", vector_name=names[0], language="english", modifier=modifier,
        fastembed_version=str(getattr(fastembed, "__version__", "unknown")),
    )


def _postgres_revision(connection: Any) -> str:
    has_alembic = connection.execute("SELECT to_regclass('public.alembic_version')").fetchone()[0]
    if not has_alembic:
        return "unversioned"
    row = connection.execute("SELECT version_num FROM alembic_version ORDER BY version_num LIMIT 1").fetchone()
    return str(row[0]) if row else "unversioned"


def migration_head(project_root: Path) -> str:
    revisions: list[str] = []
    for path in (project_root / "migrations" / "versions").glob("*.py"):
        match = re.search(r'^revision\s*=\s*["\']([^"\']+)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            revisions.append(match.group(1))
    if not revisions:
        raise BundleError("cannot determine Alembic migration head")
    return sorted(revisions)[-1]


def postgres_state(storage: Storage) -> PostgresState:
    with storage.connect() as connection:
        revision = _postgres_revision(connection)
        counts = {
            table: int(connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0])
            for table in SELECTED_TABLES
        }
        row = connection.execute(
            "SELECT fingerprint FROM index_identities WHERE collection_name=%s", (storage.settings.collection_name,)
        ).fetchone()
    if row is None:
        raise BundleError("index identity is missing; cannot create a trusted bundle")
    return PostgresState(
        database=DATABASE_NAME, revision=revision, table_counts=counts, index_fingerprint=str(row[0])
    )


def _current_index_identity(connection: Any, collection_name: str) -> tuple[str, int]:
    row = connection.execute(
        "SELECT payload FROM index_identities WHERE collection_name=%s", (collection_name,)
    ).fetchone()
    if row is None:
        raise BundleError("current index identity is missing")
    payload = row[0] if isinstance(row[0], dict) else json.loads(row[0])
    try:
        return str(payload["embedding_model"]), int(payload["embedding_dimensions"])
    except (KeyError, TypeError, ValueError) as exc:
        raise BundleError("current index identity payload is invalid") from exc


def deterministic_sample_candidates(
    storage: Storage, *, size: int = SAMPLE_SIZE, require_exact: bool = True,
) -> list[tuple[str, str, str]]:
    """Deterministic SQL candidates tied to the live index identity."""
    with storage.connect() as connection:
        model, dimensions = _current_index_identity(connection, storage.settings.collection_name)
        rows = connection.execute(
            "SELECT object_id,source_id,source_version_id FROM ("
            "SELECT DISTINCT k.object_id,k.source_id,k.source_version_id,md5(k.object_id::text) AS sample_order "
            "FROM embedding_records e JOIN knowledge_objects k ON k.object_id=e.object_id "
            "WHERE e.model=%s AND e.task_type='RETRIEVAL_DOCUMENT' AND e.dimensions=%s"
            ") AS candidates ORDER BY sample_order, object_id LIMIT %s",
            (model, dimensions, size),
        ).fetchall()
    candidates = [(str(row[0]), str(row[1]), str(row[2])) for row in rows]
    if require_exact and len(candidates) != size:
        raise BundleError(f"expected {size} deterministic sample candidates, found {len(candidates)}")
    return candidates


def _chunks(values: Sequence[Any], size: int = 64) -> Sequence[Sequence[Any]]:
    return [values[index:index + size] for index in range(0, len(values), size)]


def select_verification_samples(storage: Storage) -> list[VerificationSample]:
    candidates = deterministic_sample_candidates(
        storage, size=SAMPLE_CANDIDATE_POOL_SIZE, require_exact=False,
    )
    expected = {storage.point_id(object_id): (object_id, source_id, source_version_id) for object_id, source_id, source_version_id in candidates}
    found: dict[str, VerificationSample] = {}
    for point_ids in _chunks(list(expected)):
        points = storage.qdrant.retrieve(
            collection_name=storage.settings.collection_name, ids=list(point_ids),
            with_payload=True, with_vectors=False,
        )
        for point in points:
            point_id = str(point.id)
            candidate = expected.get(point_id)
            payload = point.payload or {}
            if candidate is None:
                continue
            object_id, source_id, source_version_id = candidate
            if (payload.get("object_id"), payload.get("source_id"), payload.get("source_version_id")) != (
                object_id, source_id, source_version_id,
            ):
                raise BundleError(f"Qdrant sample payload identity mismatch: {point_id}")
            found[point_id] = VerificationSample(
                object_id=object_id, point_id=point_id, source_id=source_id, source_version_id=source_version_id
            )
    if len(found) < SAMPLE_SIZE:
        raise BundleError(f"Qdrant confirmed {len(found)} of {SAMPLE_SIZE} deterministic sample points")
    selected: list[VerificationSample] = []
    for object_id, _, _ in candidates:
        sample = found.get(storage.point_id(object_id))
        if sample is not None:
            selected.append(sample)
        if len(selected) == SAMPLE_SIZE:
            return selected
    raise BundleError(f"Qdrant confirmed {len(selected)} of {SAMPLE_SIZE} deterministic sample points")


def _runtime_source(project_root: Path) -> Path:
    cache = project_root / "data" / "cache" / "fastembed" / "models--Qdrant--bm25"
    ref = cache / "refs" / "main"
    if not ref.is_file():
        raise BundleError(f"legacy BM25 cache ref is missing: {ref}")
    revision = ref.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[0-9A-Za-z._-]+", revision):
        raise BundleError("legacy BM25 cache ref is invalid")
    snapshot = cache / "snapshots" / revision
    if not snapshot.is_dir() or not any(snapshot.iterdir()):
        raise BundleError(f"legacy BM25 cache snapshot is missing or empty: {snapshot}")
    return snapshot


def _copy_runtime_to_bundle(project_root: Path, bundle_dir: Path) -> None:
    destination = bundle_dir / RUNTIME_BM25_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(_runtime_source(project_root), destination)


def _canonical_gold_path(project_root: Path) -> Path:
    """Require the signed v2.6 Gold selected by the evaluator contract."""
    path = default_gold_dataset_path(project_root)
    if path != project_root / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml":
        raise BundleError("canonical v2.6 Gold selector is unavailable")
    if sha256_file(path) != CANONICAL_GOLD_SHA256:
        raise BundleError("canonical v2.6 Gold hash does not match the bundle contract")
    return path


def _export_evaluator_catalog(project_root: Path, bundle_dir: Path) -> EvaluatorCatalogState:
    source = normalized_dir(project_root) / "knowledge_objects.jsonl"
    destination = bundle_dir / EVALUATOR_CATALOG_PATH
    try:
        receipt = write_evaluator_catalog(source, destination)
    except EvaluatorCatalogError as exc:
        raise BundleError(f"cannot export evaluator catalog: {exc}") from exc
    gold_path = _canonical_gold_path(project_root)
    return EvaluatorCatalogState(
        path=EVALUATOR_CATALOG_PATH.as_posix(),
        schema_version=receipt.schema_version,
        lookup_contract=receipt.lookup_contract,
        sha256=receipt.sha256,
        count=receipt.count,
        source_gold_sha256=sha256_file(gold_path),
    )


def _install_runtime_from_bundle(bundle_dir: Path, project_root: Path) -> Path:
    source = bundle_dir / RUNTIME_BM25_PATH
    destination = project_root / INSTALLED_RUNTIME_PATH
    if destination.exists():
        raise BundleError(f"runtime asset destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return destination


def _assert_evaluator_catalog_installable(project_root: Path) -> None:
    destination = project_root / INSTALLED_EVALUATOR_CATALOG_PATH
    if destination.exists():
        raise BundleError(f"evaluator catalog destination already exists: {destination}")


def _install_evaluator_catalog_from_bundle(bundle_dir: Path, project_root: Path) -> Path:
    source = bundle_dir / EVALUATOR_CATALOG_PATH
    destination = project_root / INSTALLED_EVALUATOR_CATALOG_PATH
    _assert_evaluator_catalog_installable(project_root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def _verify_runtime(project_root: Path) -> bool:
    model_path = project_root / INSTALLED_RUNTIME_PATH
    if not model_path.is_dir() or not any(model_path.iterdir()):
        return False
    try:
        model = SparseTextEmbedding(
            model_name="Qdrant/bm25", specific_model_path=str(model_path), local_files_only=True, language="english",
        )
        vector = next(iter(model.query_embed("PANDA local runtime verification")))
        values = getattr(vector, "values", vector)
        return len(values) > 0
    except Exception:
        return False


def _compose_command(*args: str) -> list[str]:
    return ["docker", "compose", *args]


def _dump_postgres(bundle_dir: Path, project_root: Path, runner: Callable[..., Any] = subprocess.run) -> None:
    command = _compose_command(
        "exec", "-T", "postgres", "pg_dump", "-U", "panda", "-d", DATABASE_NAME, "--format=custom",
        "--no-owner", "--no-privileges", "--exclude-table-data=qa_runs", "--exclude-table-data=ingestion_runs",
        "--exclude-table-data=embedding_records", "--exclude-table-data=relation_candidates",
    )
    with (bundle_dir / POSTGRES_DUMP_NAME).open("wb") as stream:
        runner(command, check=True, stdout=stream, cwd=project_root)


def _create_and_download_snapshot(bundle_dir: Path, session: requests.Session, qdrant_url: str, collection: str) -> None:
    created = session.post(f"{qdrant_url.rstrip('/')}/collections/{collection}/snapshots", timeout=60)
    created.raise_for_status()
    name = created.json()["result"]["name"]
    download = session.get(
        f"{qdrant_url.rstrip('/')}/collections/{collection}/snapshots/{name}", timeout=300, stream=True
    )
    download.raise_for_status()
    with (bundle_dir / QDRANT_SNAPSHOT_NAME).open("wb") as stream:
        for chunk in download.iter_content(chunk_size=1024 * 1024):
            if chunk:
                stream.write(chunk)


def _export_preflight(project_root: Path, storage: Storage) -> PostgresState:
    index_report = verify_index(project_root)
    if not index_report.get("valid"):
        raise BundleError("index verification must pass before bundle export")
    with storage.connect() as connection:
        running = bool(connection.execute("SELECT EXISTS(SELECT 1 FROM ingestion_runs WHERE status='running')").fetchone()[0])
    if running:
        raise BundleError("cannot export while an ingestion run is running")
    state = postgres_state(storage)
    expected_revision = migration_head(project_root)
    if state.revision == "unversioned" or state.revision != expected_revision:
        raise BundleError(f"PostgreSQL revision {state.revision!r} does not match Alembic head {expected_revision!r}")
    return state


def export_bundle(
    bundle_dir: Path, *, project_root: Path, settings: StorageSettings | None = None,
    session: requests.Session | None = None, runner: Callable[..., Any] = subprocess.run,
) -> BundleManifest:
    bundle_dir = bundle_dir.resolve()
    project_root = project_root.resolve()
    if bundle_dir.exists() and any(bundle_dir.iterdir()):
        raise BundleError(f"refusing to overwrite nonempty bundle directory: {bundle_dir}")
    bundle_dir.mkdir(parents=True, exist_ok=True)
    storage = Storage(settings)
    session = session or requests.Session()
    pg = _export_preflight(project_root, storage)
    qdrant = qdrant_state(session, storage.settings.qdrant_url, storage.settings.collection_name)
    samples = select_verification_samples(storage)
    _dump_postgres(bundle_dir, project_root, runner)
    _create_and_download_snapshot(bundle_dir, session, storage.settings.qdrant_url, storage.settings.collection_name)
    _copy_runtime_to_bundle(project_root, bundle_dir)
    source_manifest = project_root / "data" / "manifests" / "source_manifest.json"
    if not source_manifest.is_file():
        raise BundleError(f"corpus source manifest is missing: {source_manifest}")
    evaluator_catalog = _export_evaluator_catalog(project_root, bundle_dir)
    manifest = BundleManifest(
        schema_version=BUNDLE_SCHEMA_VERSION, created_at=datetime.now(UTC),
        corpus_source_manifest_sha256=sha256_file(source_manifest), postgres=pg, qdrant=qdrant,
        fastembed=fastembed_state(qdrant), verification_samples=samples,
        postgres_dump=_artifact(bundle_dir / POSTGRES_DUMP_NAME, POSTGRES_DUMP_NAME),
        qdrant_snapshot=_artifact(bundle_dir / QDRANT_SNAPSHOT_NAME, QDRANT_SNAPSHOT_NAME),
        evaluator_catalog=evaluator_catalog,
    )
    _write_manifest(bundle_dir / MANIFEST_NAME, manifest)
    return manifest


def _target_is_empty(storage: Storage, session: requests.Session) -> None:
    with storage.connect() as connection:
        table = connection.execute("SELECT to_regclass('public.knowledge_objects')").fetchone()[0]
    if table:
        raise BundleError("restore target already has a knowledge_objects table")
    response = session.get(
        f"{storage.settings.qdrant_url.rstrip('/')}/collections/{storage.settings.collection_name}/exists", timeout=60
    )
    response.raise_for_status()
    if bool(response.json()["result"]["exists"]):
        raise BundleError("restore target already has the PANDA knowledge collection")


def _restore_postgres(bundle_dir: Path, project_root: Path, runner: Callable[..., Any] = subprocess.run) -> None:
    command = _compose_command(
        "exec", "-T", "postgres", "pg_restore", "-U", "panda", "-d", DATABASE_NAME,
        "--exit-on-error", "--single-transaction", "--no-owner", "--no-privileges",
    )
    with (bundle_dir / POSTGRES_DUMP_NAME).open("rb") as stream:
        runner(command, check=True, stdin=stream, cwd=project_root)


def _restore_qdrant(bundle_dir: Path, storage: Storage, session: requests.Session) -> None:
    with (bundle_dir / QDRANT_SNAPSHOT_NAME).open("rb") as stream:
        response = session.post(
            f"{storage.settings.qdrant_url.rstrip('/')}/collections/{storage.settings.collection_name}/snapshots/upload",
            params={"priority": "snapshot"}, files={"snapshot": (QDRANT_SNAPSHOT_NAME, stream, "application/octet-stream")},
            timeout=300,
        )
    response.raise_for_status()


def _installed_marker(project_root: Path, manifest: BundleManifest) -> None:
    path = project_root / "data" / "runtime" / "installed_bundle.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical_json({"schema_version": manifest.schema_version, "created_at": manifest.created_at}) + "\n", encoding="utf-8")


def restore_bundle(
    bundle_dir: Path, *, project_root: Path, settings: StorageSettings | None = None,
    session: requests.Session | None = None, runner: Callable[..., Any] = subprocess.run,
) -> BundleManifest:
    manifest = preflight_bundle(bundle_dir)
    project_root = project_root.resolve()
    _assert_evaluator_catalog_installable(project_root)
    storage = Storage(settings)
    session = session or requests.Session()
    _target_is_empty(storage, session)
    _restore_postgres(bundle_dir, project_root, runner)
    _restore_qdrant(bundle_dir, storage, session)
    _install_runtime_from_bundle(bundle_dir, project_root)
    _install_evaluator_catalog_from_bundle(bundle_dir, project_root)
    _installed_marker(project_root, manifest)
    return manifest


def _verify_sample(storage: Storage, sample: VerificationSample) -> bool:
    with storage.connect() as connection:
        row = connection.execute(
            "SELECT object_id,source_id,source_version_id FROM knowledge_objects WHERE object_id=%s", (sample.object_id,)
        ).fetchone()
    if row is None or tuple(str(value) for value in row) != (sample.object_id, sample.source_id, sample.source_version_id):
        return False
    points = storage.qdrant.retrieve(
        collection_name=storage.settings.collection_name, ids=[sample.point_id], with_payload=True, with_vectors=False,
    )
    if len(points) != 1 or str(points[0].id) != sample.point_id:
        return False
    payload = points[0].payload or {}
    return (payload.get("object_id"), payload.get("source_id"), payload.get("source_version_id")) == (
        sample.object_id, sample.source_id, sample.source_version_id,
    )


def verify_bundle(
    bundle_dir: Path, *, project_root: Path, settings: StorageSettings | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Verify the restored local target; it never reads the excluded embedding receipt."""
    manifest = preflight_bundle(bundle_dir)
    project_root = project_root.resolve()
    storage = Storage(settings)
    session = session or requests.Session()
    pg = postgres_state(storage)
    qdrant = qdrant_state(session, storage.settings.qdrant_url, storage.settings.collection_name)
    sample_checks = [_verify_sample(storage, sample) for sample in manifest.verification_samples]
    catalog_path = project_root / INSTALLED_EVALUATOR_CATALOG_PATH
    try:
        receipt = catalog_receipt(catalog_path)
        catalog_lookup = load_evaluator_catalog(catalog_path)
        catalog_identity = (
            receipt.schema_version == manifest.evaluator_catalog.schema_version
            and receipt.lookup_contract == manifest.evaluator_catalog.lookup_contract
            and receipt.sha256 == manifest.evaluator_catalog.sha256
            and receipt.count == manifest.evaluator_catalog.count
        )
    except EvaluatorCatalogError:
        catalog_lookup = None
        catalog_identity = False
    gold_selector = False
    if catalog_lookup is not None:
        try:
            gold_path = _canonical_gold_path(project_root)
            gold = load_gold_dataset(gold_path)
            gold_validation = validate_gold_dataset(
                project_root, gold_path, evaluator_catalog_path=catalog_path,
            )
            gold_selector = (
                bool(gold.questions)
                and sha256_file(gold_path) == manifest.evaluator_catalog.source_gold_sha256
                and gold_validation["structurally_valid"]
            )
        except (BundleError, OSError, ValueError):
            gold_selector = False
    checks = {
        "postgres_revision": pg.revision == manifest.postgres.revision,
        "postgres_table_counts": pg.table_counts == manifest.postgres.table_counts,
        "postgres_fingerprint": pg.index_fingerprint == manifest.postgres.index_fingerprint,
        "qdrant_green": True,
        "qdrant_exact_count": qdrant.point_count == manifest.qdrant.point_count,
        "qdrant_dense_config": qdrant.dense_config == manifest.qdrant.dense_config,
        "qdrant_sparse_config": qdrant.sparse_config == manifest.qdrant.sparse_config,
        "qdrant_payload_indexes": qdrant.payload_indexes == manifest.qdrant.payload_indexes,
        "qdrant_version": qdrant.version == manifest.qdrant.version,
        "fastembed": fastembed_state(qdrant) == manifest.fastembed,
        "runtime_bm25": _verify_runtime(project_root),
        "verification_samples": len(sample_checks) == SAMPLE_SIZE and all(sample_checks),
        "evaluator_catalog_round_trip": catalog_identity,
        "gold_selector": gold_selector,
    }
    return {"valid": all(checks.values()), "checks": checks, "sample_count": len(sample_checks)}
