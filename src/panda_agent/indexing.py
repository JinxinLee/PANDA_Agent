"""M3 idempotent SQL/Qdrant indexing."""

from __future__ import annotations

import hashlib
import json
import struct
import uuid
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict
from psycopg.types.json import Jsonb

from qdrant_client import models

from panda_agent.config import BM25_MODEL_NAME, SPARSE_VECTOR_MODIFIER, SPARSE_VECTOR_NAME
from panda_agent.chunking import DEFAULT_CHUNKING_POLICY
from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.sparse import SparseEncoderReceipt, create_sparse_encoder, sparse_receipt, sparse_settings
from panda_agent.storage import Storage, iter_jsonl, load_jsonl


B4_EXPECTED_INDEX_FINGERPRINT = (
    "8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9"
)
B4_LOCATOR_SYNC_BATCH_SIZE = 256


class IndexIdentity(BaseModel):
    """Immutable vector-index contract; any field change requires migration."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    embedding_model: str
    embedding_dimensions: int
    distance: str
    sparse: SparseEncoderReceipt
    index_schema_version: Literal["4"]

    def fingerprint(self) -> str:
        payload = self.model_dump_json(exclude_none=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_settings(
        cls, settings: VertexSettings, project_root: Path | None = None,
    ) -> "IndexIdentity":
        root = (project_root or Path(__file__).resolve().parents[2]).resolve()
        return cls(
            embedding_model=settings.embedding_model,
            embedding_dimensions=settings.embedding_dimensions,
            distance="cosine",
            sparse=sparse_receipt(sparse_settings(root)),
            index_schema_version="4",
        )


class LegacyIndexIdentity(BaseModel):
    """Exact schema-3 identity accepted only by the B3 metadata migration."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    embedding_model: str
    embedding_dimensions: int
    distance: str
    sparse_model: str
    sparse_vector_name: str
    sparse_modifier: str
    index_schema_version: str

    def fingerprint(self) -> str:
        return hashlib.sha256(self.model_dump_json(exclude_none=False).encode("utf-8")).hexdigest()

    @classmethod
    def from_settings(cls, settings: VertexSettings) -> "LegacyIndexIdentity":
        return cls(
            embedding_model=settings.embedding_model,
            embedding_dimensions=settings.embedding_dimensions,
            distance="cosine",
            sparse_model=BM25_MODEL_NAME,
            sparse_vector_name=SPARSE_VECTOR_NAME,
            sparse_modifier=SPARSE_VECTOR_MODIFIER,
            index_schema_version="3",
        )


def _compatible_cache_receipts(
    connection: Any, cache_keys: list[str], expected_dimensions: int
) -> dict[str, str]:
    """Return compatible dense receipts keyed by cache_key, with owning object_id.

    The cache_key is content-addressed, so the owning object_id is retained for
    resume-safety: a compatible receipt is only strong evidence for a selected
    object when that object_id also matches.
    """
    return {
        str(row[0]): str(row[1])
        for row in connection.execute(
            "SELECT cache_key, object_id FROM embedding_records "
            "WHERE cache_key=ANY(%s) AND dimensions=%s",
            (cache_keys, expected_dimensions),
        ).fetchall()
    }


def _compatible_cache_keys(
    connection: Any, cache_keys: list[str], expected_dimensions: int
) -> set[str]:
    """Return cache receipts that match the active dense-vector contract."""
    return set(
        _compatible_cache_receipts(connection, cache_keys, expected_dimensions)
    )


def _record_embedding_cache(
    connection: Any,
    *,
    cache_key: str,
    object_id: str,
    model: str,
    task_type: str,
    text_hash: str,
    dimensions: int,
) -> None:
    """Record the dimensions for a completed dense-vector write."""
    connection.execute(
        "INSERT INTO embedding_records(cache_key,object_id,model,task_type,text_hash,dimensions) "
        "VALUES(%s,%s,%s,%s,%s,%s) "
        "ON CONFLICT(cache_key) DO UPDATE SET "
        "object_id=excluded.object_id,model=excluded.model,task_type=excluded.task_type,"
        "text_hash=excluded.text_hash,dimensions=excluded.dimensions,indexed_at=now()",
        (cache_key, object_id, model, task_type, text_hash, dimensions),
    )


def normalized_dir(project_root: Path) -> Path:
    reports = list((project_root / "data" / "normalized").glob("*/ingestion_report.json"))
    if not reports: raise RuntimeError("M2 output not found")
    return max(reports, key=lambda path: path.stat().st_mtime).parent


def embedding_input(item: dict[str, Any]) -> str:
    """The one dense-input construction shared by B5 ingestion and indexing."""
    return DEFAULT_CHUNKING_POLICY.embedding_input(item["title"], item["text"])


def embedding_eligible(item: dict[str, Any]) -> bool:
    return bool(item.get("embedding_eligible")) and DEFAULT_CHUNKING_POLICY.embedding_input_is_valid(
        item["title"], item["text"], int(item.get("token_count", 0))
    )


def index_plan(project_root: Path) -> dict[str, int]:
    root = normalized_dir(project_root)
    objects = load_jsonl(root / "knowledge_objects.jsonl")
    eligible = [item for item in objects if embedding_eligible(item)]
    return {"objects": len(objects), "embedding_eligible": len(eligible), "relations": len(load_jsonl(root / "relation_edges.jsonl")), "relation_candidates": len(load_jsonl(root / "relation_candidates.jsonl")), "aliases": len(load_jsonl(root / "knowledge_aliases.jsonl")), "workflows": len(load_jsonl(root / "workflow_steps.jsonl"))}


def verify_index(project_root:Path)->dict[str,Any]:
    root=normalized_dir(project_root); storage=Storage(); objects=load_jsonl(root/"knowledge_objects.jsonl")
    report=json.loads((root/"ingestion_report.json").read_text(encoding="utf-8"))
    eligible=[item for item in objects if embedding_eligible(item)]
    expected={storage.point_id(item["object_id"]) for item in eligible}; actual=set(); cursor=None
    while True:
        points,cursor=storage.qdrant.scroll(collection_name=storage.settings.collection_name,limit=256,offset=cursor,with_payload=False,with_vectors=False)
        actual.update(str(point.id) for point in points)
        if cursor is None: break
    with storage.connect() as connection:
        sql_counts={"objects":connection.execute("select count(1) from knowledge_objects").fetchone()[0],"relations":connection.execute("select count(1) from relation_edges").fetchone()[0],"relation_candidates":connection.execute("select count(1) from relation_candidates").fetchone()[0],"aliases":connection.execute("select count(1) from knowledge_aliases").fetchone()[0],"workflows":connection.execute("select count(1) from workflow_steps").fetchone()[0]}
    expected_sql={"objects":report["object_count"],"relations":report["relation_count"],"relation_candidates":report["relation_candidate_count"],"aliases":report.get("alias_count",0),"workflows":report["workflow_count"]}
    return {"valid":expected==actual and sql_counts==expected_sql,"expected_points":len(expected),"actual_points":len(actual),"missing_points":len(expected-actual),"stale_points":len(actual-expected),"sql_counts":sql_counts,"expected_sql_counts":expected_sql}


def _b4_batches(records: Any, size: int = B4_LOCATOR_SYNC_BATCH_SIZE) -> Any:
    batch: list[dict[str, Any]] = []
    for record in records:
        batch.append(record)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def _b4_json(value: Any) -> dict[str, Any]:
    if value is None:
        raise RuntimeError("B4 locator sync encountered a missing locator JSON value")
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return parsed
    raise RuntimeError("B4 locator sync encountered a non-object JSON value")


def _b4_embedding_eligible(item: dict[str, Any]) -> bool:
    return embedding_eligible(item)


def _input_sha256(item: dict[str, Any]) -> str:
    return hashlib.sha256(embedding_input(item).encode("utf-8")).hexdigest()


def plan_b5_reindex_impact_from_records(
    b4_records: list[dict[str, Any]], b5_objects: list[dict[str, Any]], *, batch_size: int = 64,
) -> dict[str, Any]:
    """Classify a B5 normalized corpus without contacting SQL, Qdrant, or Vertex.

    A current point is reusable solely when its exact dense input remains the
    same.  Cache-receipt absence is deliberately not a re-embedding trigger.
    """
    before = {item["object_id"]: item for item in b4_records}
    after = {item["object_id"]: item for item in b5_objects}
    if len(before) != len(b4_records) or len(after) != len(b5_objects):
        raise ValueError("impact planning requires unique object IDs")
    unchanged_eligible: list[str] = []
    changed_eligible: list[str] = []
    new_eligible: list[str] = []
    eligibility_gained: list[str] = []
    eligibility_lost: list[str] = []
    unchanged_noneligible: list[str] = []
    stale_point_ids: list[str] = []
    receipt_missing_reused: list[str] = []
    for object_id in sorted(after):
        current = after[object_id]
        current_eligible = embedding_eligible(current)
        previous = before.get(object_id)
        if previous is None:
            if current_eligible:
                new_eligible.append(object_id)
            continue
        old_eligible = bool(previous.get("effective_embedding_eligibility"))
        old_input = previous.get("embedding_input_sha256")
        new_input = _input_sha256(current)
        point_exists = bool(previous.get("qdrant_point_exists"))
        if current_eligible and old_eligible and point_exists and old_input == new_input:
            unchanged_eligible.append(object_id)
            if not previous.get("embedding_receipt_exists"):
                receipt_missing_reused.append(object_id)
        elif current_eligible and old_eligible:
            changed_eligible.append(object_id)
        elif current_eligible:
            eligibility_gained.append(object_id)
        elif old_eligible:
            eligibility_lost.append(object_id)
        elif previous.get("text_sha256") == hashlib.sha256(current["text"].encode("utf-8")).hexdigest():
            unchanged_noneligible.append(object_id)
    expected_live_ids = {
        previous["deterministic_point_id"] for previous in before.values()
        if previous.get("qdrant_point_exists")
    }
    desired_ids = {
        str(uuid.uuid5(uuid.NAMESPACE_URL, f"panda-qa:{object_id}"))
        for object_id, item in after.items() if embedding_eligible(item)
    }
    stale_point_ids = sorted(expected_live_ids - desired_ids)
    selected_ids = sorted(changed_eligible + new_eligible + eligibility_gained)
    type_counts: dict[str, int] = {}
    for object_id in selected_ids:
        key = after[object_id]["object_type"]
        type_counts[key] = type_counts.get(key, 0) + 1
    before_live_points = sum(
        1 for previous in before.values() if previous.get("qdrant_point_exists")
    )
    b5_eligible_total = sum(1 for item in after.values() if embedding_eligible(item))
    return {
        "planner": "b5-selective-static-v1",
        "model_calls": 0,
        "network_calls": 0,
        "batch_size": batch_size,
        "categories": {
            "unchanged_eligible_reuse": len(unchanged_eligible),
            "changed_eligible_reembed": len(changed_eligible),
            "new_eligible_reembed": len(new_eligible),
            "eligibility_gained_reembed": len(eligibility_gained),
            "eligibility_lost_remove": len(eligibility_lost),
            "unchanged_noneligible": len(unchanged_noneligible),
            "stale_live_points_remove": len(stale_point_ids),
        },
        "closures": {
            "before_live_points": before_live_points,
            "reuse_plus_changed_plus_stale": len(unchanged_eligible) + len(changed_eligible) + len(stale_point_ids),
            "b5_eligible_total": b5_eligible_total,
            "reuse_plus_changed_plus_gained_plus_new": (
                len(unchanged_eligible) + len(changed_eligible) + len(eligibility_gained) + len(new_eligible)
            ),
            "sql_before_plus_inserts_minus_deletes": (
                len(before) + len(set(after) - set(before)) - len(set(before) - set(after))
            ),
            "sql_after": len(after),
        },
        "sql": {
            "insert_object_ids": sorted(set(after) - set(before)),
            "delete_object_ids": sorted(set(before) - set(after)),
            "upsert_object_ids": sorted(set(after)),
        },
        "vectors": {
            "reuse_object_ids": unchanged_eligible,
            "reembed_object_ids": selected_ids,
            "stale_point_ids": stale_point_ids,
            "dense_documents": len(selected_ids),
            "sparse_documents": len(selected_ids),
            "batches": (len(selected_ids) + batch_size - 1) // batch_size,
            "receipt_missing_unchanged_reused": len(receipt_missing_reused),
            "receipt_missing_unchanged_reuse_ids": receipt_missing_reused,
            "selected_by_object_type": dict(sorted(type_counts.items())),
        },
    }


B5_CHURN_CAUSE_ORDER = [
    "new_source_gap_coverage",
    "new_generic_file_coverage",
    "intentional_structural_rechunk",
    "eligibility_gain",
    "structural_container_policy_change",
    "full_source_parent_effect",
    "title_only_change",
    "text_boundary_change",
    "object_identity_churn",
    "other_explained",
]


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _whitespace_only_change(before_text: str | None, after_text: str) -> bool:
    return before_text is not None and before_text.split() == after_text.split() and before_text != after_text


def classify_b5_reembed_cause(
    previous: dict[str, Any] | None, current: dict[str, Any]
) -> str:
    """Exactly one deterministic primary cause for one re-embedding object.

    ``previous`` must carry the B4 title/text (for new objects it is None);
    the classification never depends on benchmark results.
    """
    metadata = current.get("metadata") or {}
    if previous is None:
        if metadata.get("b5_source_gap"):
            if metadata.get("region_kind") == "generic_text_block":
                return "new_generic_file_coverage"
            return "new_source_gap_coverage"
        if metadata.get("derived_from"):
            return "intentional_structural_rechunk"
        return "other_explained"
    old_eligible = bool(previous.get("effective_embedding_eligibility"))
    if not old_eligible and embedding_eligible(current):
        return "eligibility_gain"
    before_title = previous.get("title")
    before_text = previous.get("text")
    if before_title != current.get("title") and before_text == current.get("text"):
        return "title_only_change"
    if before_text != current.get("text"):
        if before_text is not None and current["text"].startswith(before_text) and current["object_type"] in {"source_file", "python_script"}:
            return "full_source_parent_effect"
        if current["object_type"].endswith("_chunk") or metadata.get("derived_from"):
            return "intentional_structural_rechunk"
        return "text_boundary_change"
    return "other_explained"


def b5_churn_attribution(
    before: list[dict[str, Any]], after: list[dict[str, Any]], reembed_ids: list[str],
) -> dict[str, Any]:
    """Offline primary-cause attribution; every re-embed ID gets exactly one cause."""
    before_map = {item["object_id"]: item for item in before}
    after_map = {item["object_id"]: item for item in after}
    causes: dict[str, list[str]] = {cause: [] for cause in B5_CHURN_CAUSE_ORDER}
    for object_id in reembed_ids:
        cause = classify_b5_reembed_cause(before_map.get(object_id), after_map[object_id])
        if cause not in causes:
            raise RuntimeError(f"unknown B5 churn cause: {cause}")
        causes[cause].append(object_id)
    by_type: dict[tuple[str, str], int] = {}
    for cause, ids in causes.items():
        for object_id in ids:
            key = (cause, after_map[object_id]["object_type"])
            by_type[key] = by_type.get(key, 0) + 1
    return {
        "model_calls": 0,
        "network_calls": 0,
        "reembed_total": len(reembed_ids),
        "unknown_or_unclassified": len(causes["other_explained"]),
        "cause_counts": {
            cause: len(ids) for cause, ids in causes.items() if ids
        },
        "cause_by_object_type": {
            f"{cause}|{object_type}": count
            for (cause, object_type), count in sorted(by_type.items())
        },
        "cause_object_ids": causes,
        "attributed_total": sum(len(ids) for ids in causes.values()),
        "closure": f"cause_total == reembed_total: {sum(len(ids) for ids in causes.values())} == {len(reembed_ids)}",
    }


def plan_b5_reindex_impact(
    project_root: Path, *, snapshot_path: Path | None = None, batch_size: int = 64,
) -> dict[str, Any]:
    snapshot = snapshot_path or project_root / "data" / "tmp" / "b5" / "b4_point_snapshot.jsonl"
    objects = load_jsonl(normalized_dir(project_root) / "knowledge_objects.jsonl")
    report = plan_b5_reindex_impact_from_records(load_jsonl(snapshot), objects, batch_size=batch_size)
    report["b4_snapshot_path"] = str(snapshot)
    report["normalized_dir"] = str(normalized_dir(project_root))
    report["b4_records"] = len(load_jsonl(snapshot))
    report["b5_objects"] = len(objects)
    return report


B5_EXPECTED_B4_SQL_OBJECTS = 102875
B5_EXPECTED_B4_QDRANT_POINTS = 80698
B5_EMBEDDING_BATCH_SIZE = 64


def _b5_validate_reuse_locators(
    snapshot: list[dict[str, Any]], objects: list[dict[str, Any]], reuse_ids: list[str],
) -> None:
    """A reused vector must keep its B4 payload locator byte-for-byte."""
    before = {item["object_id"]: item for item in snapshot}
    after = {item["object_id"]: item for item in objects}
    mismatched = [
        object_id for object_id in reuse_ids
        if before[object_id].get("locator") != after[object_id].get("locator")
    ]
    if mismatched:
        raise RuntimeError(
            "B5 reuse locator disagreement: reusing these vectors would leave a "
            f"stale Qdrant payload locator ({len(mismatched)} objects); "
            f"first={mismatched[:3]}"
        )


def _b5_validate_selected_inputs(objects_map: dict[str, dict[str, Any]], selected_ids: list[str]) -> None:
    """Every re-embed candidate must itself satisfy the shared embedding contract."""
    invalid = [
        object_id for object_id in selected_ids
        if not embedding_eligible(objects_map[object_id])
        or not str(objects_map[object_id].get("title", "")).strip()
        or not str(objects_map[object_id].get("text", "")).strip()
    ]
    if invalid:
        raise RuntimeError(
            f"B5 selective apply selected policy-invalid embedding inputs ({len(invalid)}); "
            f"first={invalid[:3]}"
        )


B5_RESUME_PAYLOAD_FIELDS = (
    "object_id",
    "source_id",
    "source_version_id",
    "object_type",
    "title",
    "text",
    "locator",
)


def _b5_point_payload_matches_current(item: dict[str, Any], point: Any) -> bool:
    """Return whether a Qdrant point payload already represents the B5 object.

    This is the smallest safe payload proof: exact equality of the fields that
    determine the embedding input and the object identity/locator written by a
    successful B5 selected-vector write.
    """
    payload = getattr(point, "payload", None)
    if not isinstance(payload, dict):
        return False
    return all(
        payload.get(field) == item.get(field) for field in B5_RESUME_PAYLOAD_FIELDS
    )


def _b5_filter_resume_selected(
    selected: list[dict[str, Any]],
    cache_keys: list[str],
    receipts: dict[str, str],
    existing_points: dict[str, Any],
    storage: Any,
) -> tuple[list[dict[str, Any]], int]:
    """Keep selected objects unless a completed B5 write is proven.

    A selected object may be skipped only when all of the following hold:
      1. the current Qdrant point exists;
      2. its payload exactly matches the current B5 object;
      3. title/text equality therefore proves the exact embedding input;
      4. a compatible receipt exists and is bound to this same object_id.

    Any uncertainty (missing receipt, mismatched payload, or receipt owned by a
    different object with identical input) causes a safe re-embed.
    """
    kept: list[dict[str, Any]] = []
    resume_skipped = 0
    for item, cache_key in zip(selected, cache_keys):
        point = existing_points.get(storage.point_id(item["object_id"]))
        if (
            cache_key in receipts
            and point is not None
            and receipts[cache_key] == item["object_id"]
            and _b5_point_payload_matches_current(item, point)
        ):
            resume_skipped += 1
        else:
            kept.append(item)
    return kept, resume_skipped


def _b5_preflight(
    root: Path,
) -> tuple[dict[str, Any], IndexIdentity, VertexSettings, Storage, Path, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Deterministic read-only preflight; must fail before any live mutation.

    Returns (report, identity, vertex_settings, storage, normalized,
    snapshot, objects, plan). No Vertex embedding is invoked here.
    """
    # 1. Settings and index identity are constructed exactly once.
    vertex_settings = VertexSettings.from_env()
    identity = IndexIdentity.from_settings(vertex_settings, root)
    # 2. Static sparse factory receipt must match the active identity before
    #    anything reads or writes the live index.
    if sparse_receipt(sparse_settings(root)) != identity.sparse:
        raise RuntimeError("B5 selective apply sparse factory receipt mismatch")
    storage = Storage()
    _b4_require_identity(storage, identity)

    snapshot_path = root / "data" / "tmp" / "b5" / "b4_point_snapshot.jsonl"
    normalized = normalized_dir(root)
    # 3. Normalized artifacts must be fully readable and internally consistent.
    snapshot = load_jsonl(snapshot_path)
    objects = load_jsonl(normalized / "knowledge_objects.jsonl")
    ingestion_report = json.loads((normalized / "ingestion_report.json").read_text(encoding="utf-8"))
    if int(ingestion_report["object_count"]) != len(objects):
        raise RuntimeError("B5 selective apply ingestion report object count mismatch")
    json.loads((root / "data" / "manifests" / "source_manifest.json").read_text(encoding="utf-8"))
    plan = plan_b5_reindex_impact_from_records(snapshot, objects, batch_size=B5_EMBEDDING_BATCH_SIZE)
    closures = plan["closures"]
    if closures["before_live_points"] != closures["reuse_plus_changed_plus_stale"]:
        raise RuntimeError("B5 selective apply B4 point closure mismatch")
    if closures["b5_eligible_total"] != closures["reuse_plus_changed_plus_gained_plus_new"]:
        raise RuntimeError("B5 selective apply B5 eligible closure mismatch")
    if closures["sql_before_plus_inserts_minus_deletes"] != closures["sql_after"]:
        raise RuntimeError("B5 selective apply SQL object closure mismatch")

    reuse_ids = plan["vectors"]["reuse_object_ids"]
    reembed_ids = plan["vectors"]["reembed_object_ids"]
    _b5_validate_reuse_locators(snapshot, objects, reuse_ids)
    after_map = {item["object_id"]: item for item in objects}
    _b5_validate_selected_inputs(after_map, reembed_ids)
    if len(reembed_ids) != len(set(reembed_ids)):
        raise RuntimeError("B5 selective apply duplicate re-embed object IDs")

    with storage.connect() as connection:
        sql_objects = int(
            connection.execute("SELECT count(1) FROM knowledge_objects").fetchone()[0]
        )
    qdrant_points = int(storage.qdrant.count(storage.settings.collection_name, exact=True).count)
    expected_final_points = len(reuse_ids) + len(reembed_ids)
    if sql_objects not in {B5_EXPECTED_B4_SQL_OBJECTS, len(objects)}:
        raise RuntimeError(
            "B5 selective apply found an unexpected SQL object count: "
            f"actual={sql_objects}, expected B4={B5_EXPECTED_B4_SQL_OBJECTS} or B5={len(objects)}"
        )
    if qdrant_points < B5_EXPECTED_B4_QDRANT_POINTS or qdrant_points > B5_EXPECTED_B4_QDRANT_POINTS + len(reembed_ids):
        raise RuntimeError(
            "B5 selective apply found an unexpected Qdrant point count: "
            f"actual={qdrant_points}, expected within "
            f"[{B5_EXPECTED_B4_QDRANT_POINTS}, {B5_EXPECTED_B4_QDRANT_POINTS + len(reembed_ids)}]"
        )

    report = {
        "planner": plan["planner"],
        "normalized_dir": normalized.name,
        "b4_snapshot_path": str(snapshot_path),
        "index_identity": identity.fingerprint(),
        "index_schema": identity.index_schema_version,
        "sql_objects_before": sql_objects,
        "qdrant_points_before": qdrant_points,
        "categories": plan["categories"],
        "vectors": {
            "reuse_object_ids": len(reuse_ids),
            "reembed_object_ids": len(reembed_ids),
            "stale_point_ids": len(plan["vectors"]["stale_point_ids"]),
            "dense_documents": plan["vectors"]["dense_documents"],
            "sparse_documents": plan["vectors"]["sparse_documents"],
            "batches": plan["vectors"]["batches"],
            "receipt_missing_unchanged_reused": plan["vectors"]["receipt_missing_unchanged_reused"],
            "selected_by_object_type": plan["vectors"]["selected_by_object_type"],
        },
        "expected_final_points": expected_final_points,
        "sql_inserts": len(plan["sql"]["insert_object_ids"]),
        "sql_deletes": len(plan["sql"]["delete_object_ids"]),
        "sql_upserts": len(plan["sql"]["upsert_object_ids"]),
    }
    return report, identity, vertex_settings, storage, normalized, snapshot, objects, plan


def apply_b5_selective_index(project_root: Path, *, run: bool = False) -> dict[str, Any]:
    """Selectively deploy the B5 normalized corpus over the live B4 index.

    Unchanged live points are preserved byte-for-byte and never re-embedded;
    cache-receipt absence alone never triggers re-embedding.  Only genuinely
    changed/new embedding inputs receive new dense and sparse vectors, and
    stale points are removed after the new points are verified.
    """
    root = project_root.resolve()
    (
        report,
        identity,
        vertex_settings,
        storage,
        normalized,
        snapshot,
        objects,
        plan,
    ) = _b5_preflight(root)
    report["dry_run"] = True
    if not run:
        return report

    reuse_ids = plan["vectors"]["reuse_object_ids"]
    reembed_ids = plan["vectors"]["reembed_object_ids"]
    stale_point_ids = plan["vectors"]["stale_point_ids"]
    expected_final_points = report["expected_final_points"]
    after = {item["object_id"]: item for item in objects}

    # Deterministic client/encoder construction must happen before any live SQL
    # or Qdrant mutation.  This preflight intentionally makes no embedding calls.
    vertex = None
    sparse_model = None
    if reembed_ids:
        vertex = VertexAIClient(vertex_settings)
        sparse_model, sparse_identity = create_sparse_encoder(root)
        if sparse_identity != identity.sparse:
            raise RuntimeError("sparse factory receipt changed during B5 selective apply")

    with storage.connect() as connection:
        connection.execute(
            "UPDATE ingestion_runs SET status='interrupted',completed_at=now(),"
            "report=report || '{\"error\":\"orphaned running process\"}'::jsonb WHERE status='running'"
        )
        run_id = connection.execute(
            "INSERT INTO ingestion_runs(manifest_hash,status,report) VALUES(%s,'running',%s) RETURNING run_id",
            (normalized.name, json.dumps({"kind": "b5_selective"})),
        ).fetchone()[0]

    try:
        manifest = json.loads((root / "data" / "manifests" / "source_manifest.json").read_text(encoding="utf-8"))
        storage.upsert_source_versions(manifest)
        storage.upsert_objects(iter_jsonl(normalized / "knowledge_objects.jsonl"))
        storage.upsert_aliases(iter_jsonl(normalized / "knowledge_aliases.jsonl"))
        storage.upsert_relations(iter_jsonl(normalized / "relation_edges.jsonl"))
        storage.upsert_relation_candidates(iter_jsonl(normalized / "relation_candidates.jsonl"))
        storage.upsert_workflows(load_jsonl(normalized / "workflow_steps.jsonl"))
        deleted_sql = 0
        deleted_sql += storage.prune_table("knowledge_objects", "object_id", (item["object_id"] for item in objects))
        deleted_sql += storage.prune_table("relation_edges", "edge_id", (item["edge_id"] for item in iter_jsonl(normalized / "relation_edges.jsonl")))
        deleted_sql += storage.prune_table("relation_candidates", "candidate_id", (item["candidate_id"] for item in iter_jsonl(normalized / "relation_candidates.jsonl")))
        deleted_sql += storage.prune_table("workflow_steps", "step_id", (item["step_id"] for item in load_jsonl(normalized / "workflow_steps.jsonl")))
        deleted_sql += storage.prune_table("knowledge_aliases", "alias_id", (item["alias_id"] for item in iter_jsonl(normalized / "knowledge_aliases.jsonl")))

        with storage.connect() as connection:
            relation_count = int(
                connection.execute("SELECT count(1) FROM relation_edges").fetchone()[0]
            )
        ingestion_report = json.loads((normalized / "ingestion_report.json").read_text(encoding="utf-8"))
        if relation_count != int(ingestion_report["relation_count"]):
            raise RuntimeError(
                f"B5 selective apply relation count changed unexpectedly: {relation_count}"
            )

        selected = [after[object_id] for object_id in reembed_ids]
        resume_skipped = 0
        if selected:
            cache_keys = []
            for item in selected:
                text = f"{item['title']}\n{item['text']}"
                text_hash = hashlib.sha256(text.encode()).hexdigest()
                cache_keys.append(hashlib.sha256(
                    f"{identity.embedding_model}\x1fRETRIEVAL_DOCUMENT\x1f{text_hash}".encode()
                ).hexdigest())
            with storage.connect() as connection:
                receipts = _compatible_cache_receipts(
                    connection, cache_keys, identity.embedding_dimensions
                )
            point_ids = [storage.point_id(item["object_id"]) for item in selected]
            existing_points: dict[str, Any] = {}
            for start in range(0, len(point_ids), 256):
                for point in storage.qdrant.retrieve(
                    collection_name=storage.settings.collection_name,
                    ids=point_ids[start:start + 256],
                    with_payload=True,
                    with_vectors=False,
                ):
                    existing_points[str(point.id)] = point
            selected, resume_skipped = _b5_filter_resume_selected(
                selected, cache_keys, receipts, existing_points, storage
            )

        indexed = 0
        batches_processed = 0
        for start in range(0, len(selected), B5_EMBEDDING_BATCH_SIZE):
            assert sparse_model is not None
            batches_processed += 1
            batch = selected[start:start + B5_EMBEDDING_BATCH_SIZE]
            texts = [f"{item['title']}\n{item['text']}" for item in batch]
            dense = vertex.embed_documents(texts)
            sparse_vectors = list(sparse_model.embed(texts))
            points = []
            for item, dense_vector, sparse_vector, text in zip(batch, dense, sparse_vectors, texts):
                points.append(models.PointStruct(
                    id=storage.point_id(item["object_id"]),
                    vector={
                        "dense": dense_vector,
                        sparse_identity.vector_name: models.SparseVector(
                            indices=sparse_vector.indices.tolist(),
                            values=sparse_vector.values.tolist(),
                        ),
                    },
                    payload={
                        "object_id": item["object_id"],
                        "source_id": item["source_id"],
                        "source_version_id": item["source_version_id"],
                        "object_type": item["object_type"],
                        "title": item["title"],
                        "authority_level": item["authority_level"],
                        "locator": item["locator"],
                        "text": item["text"],
                    },
                ))
            storage.qdrant.upsert(
                collection_name=storage.settings.collection_name, points=points, wait=True
            )
            indexed += len(points)
            with storage.connect() as connection:
                for item, text in zip(batch, texts):
                    text_hash = hashlib.sha256(text.encode()).hexdigest()
                    cache_key = hashlib.sha256(
                        f"{identity.embedding_model}\x1fRETRIEVAL_DOCUMENT\x1f{text_hash}".encode()
                    ).hexdigest()
                    _record_embedding_cache(
                        connection,
                        cache_key=cache_key,
                        object_id=item["object_id"],
                        model=identity.embedding_model,
                        task_type="RETRIEVAL_DOCUMENT",
                        text_hash=text_hash,
                        dimensions=identity.embedding_dimensions,
                    )

        deleted_vectors = 0
        if stale_point_ids:
            storage.qdrant.delete(
                collection_name=storage.settings.collection_name,
                points_selector=models.PointIdsList(points=stale_point_ids),
                wait=True,
            )
            deleted_vectors = len(stale_point_ids)

        final_points = int(storage.qdrant.count(storage.settings.collection_name, exact=True).count)
        if final_points != expected_final_points:
            raise RuntimeError(
                "B5 selective apply final Qdrant count mismatch: "
                f"actual={final_points}, expected={expected_final_points}"
            )
        with storage.connect() as connection:
            final_sql_objects = int(
                connection.execute("SELECT count(1) FROM knowledge_objects").fetchone()[0]
            )
        if final_sql_objects != len(objects):
            raise RuntimeError(
                "B5 selective apply final SQL object count mismatch: "
                f"actual={final_sql_objects}, expected={len(objects)}"
            )

        vertex_stats: dict[str, int] = {}
        if vertex is not None:
            snapshot = getattr(vertex, "stats_snapshot", None)
            if callable(snapshot):
                vertex_stats = snapshot()

        result = {
            **report,
            "dry_run": False,
            "run_id": run_id,
            "sql_objects_after": final_sql_objects,
            "qdrant_points_after": final_points,
            "sql_records_deleted": deleted_sql,
            "planned_selected_documents": len(reembed_ids),
            "resume_verified_selected_skipped": resume_skipped,
            "dense_documents_embedded": indexed,
            "sparse_documents_encoded": indexed,
            "qdrant_points_upserted": indexed,
            "application_batches_processed": batches_processed,
            "dense_vectors_written": indexed,
            "sparse_vectors_written": indexed,
            "unchanged_vectors_reused": len(reuse_ids),
            "unchanged_missing_receipt_reused": len(
                plan["vectors"]["receipt_missing_unchanged_reuse_ids"]
            ),
            "stale_vectors_deleted": deleted_vectors,
            "collection_recreated": False,
            "dense_model": identity.embedding_model,
            "dense_dimensions": identity.embedding_dimensions,
            "vertex_stats": vertex_stats,
        }
        with storage.connect() as connection:
            connection.execute(
                "UPDATE ingestion_runs SET status='completed',completed_at=now(),report=%s WHERE run_id=%s",
                (json.dumps(result), run_id),
            )
        return result
    except BaseException as exc:
        try:
            with storage.connect() as connection:
                connection.execute(
                    "UPDATE ingestion_runs SET status='failed',completed_at=now(),report=report || %s::jsonb "
                    "WHERE run_id=(SELECT run_id FROM ingestion_runs WHERE status='running' ORDER BY run_id DESC LIMIT 1)",
                    (json.dumps({"error": type(exc).__name__, "message": str(exc)[:2000]}),),
                )
        except Exception:
            pass
        raise


def _b4_require_identity(storage: Storage, identity: IndexIdentity) -> Any:
    """Read-only B4 gate for the exact B3 vector-index identity."""
    if (
        identity.index_schema_version != "4"
        or identity.fingerprint() != B4_EXPECTED_INDEX_FINGERPRINT
    ):
        raise RuntimeError(
            "B4 locator sync requires the exact schema-4 B3 index identity; "
            f"expected={B4_EXPECTED_INDEX_FINGERPRINT}, actual={identity.fingerprint()}"
        )
    with storage.connect() as connection:
        row = connection.execute(
            "SELECT fingerprint,payload FROM index_identities WHERE collection_name=%s",
            (storage.settings.collection_name,),
        ).fetchone()
    if row is None:
        raise RuntimeError("B4 locator sync requires a persisted index identity")
    fingerprint, raw_payload = row
    payload = _b4_json(raw_payload)
    if (
        fingerprint != B4_EXPECTED_INDEX_FINGERPRINT
        or payload != identity.model_dump(mode="json")
    ):
        raise RuntimeError(
            "B4 locator sync found a persisted index identity mismatch; "
            "metadata-only synchronization is unsafe"
        )
    collection = storage._verify_qdrant_sparse_config(identity.sparse)
    dense = collection.config.params.vectors.get("dense")
    if dense is None or dense.size != identity.embedding_dimensions:
        raise RuntimeError(
            "B4 locator sync found a Qdrant dense contract mismatch; "
            f"expected={identity.embedding_dimensions}, actual={getattr(dense, 'size', None)}"
        )
    return collection


def _b4_sql_rows(storage: Storage, object_ids: list[str]) -> dict[str, tuple[Any, ...]]:
    with storage.connect() as connection:
        rows = connection.execute(
            "SELECT object_id,object_type,source_id,source_version_id,title,text,authority_level,"
            "locator,canonical_locator,token_count,embedding_eligible,content_hash "
            "FROM knowledge_objects WHERE object_id=ANY(%s)",
            (object_ids,),
        ).fetchall()
    return {str(row[0]): row for row in rows}


def _b4_validate_sql_item(item: dict[str, Any], row: tuple[Any, ...]) -> dict[str, Any]:
    object_id, object_type, source_id, source_version_id, title, text, authority, locator, canonical, tokens, eligible, content_hash = row
    expected = (
        item["object_id"], item["object_type"], item["source_id"], item["source_version_id"],
        item["title"], item["text"], item["authority_level"], item.get("canonical_locator"), item.get("token_count", 0),
        item.get("embedding_eligible", True),
    )
    actual = (
        object_id, object_type, source_id, source_version_id, title, text, authority, canonical, tokens, eligible,
    )
    if actual != expected:
        raise RuntimeError(
            f"B4 locator sync semantic mismatch for {item['object_id']}; "
            "only locator changes are permitted"
        )
    expected_hash = hashlib.sha256(item["text"].encode()).hexdigest()
    if content_hash != expected_hash:
        raise RuntimeError(
            f"B4 locator sync content hash mismatch for {item['object_id']}; "
            "only locator changes are permitted"
        )
    return _b4_json(locator)


def _b4_qdrant_rows(storage: Storage, point_ids: list[str]) -> dict[str, Any]:
    points = storage.qdrant.retrieve(
        collection_name=storage.settings.collection_name,
        ids=point_ids,
        with_payload=True,
        with_vectors=False,
    )
    return {str(point.id): point for point in points}


def sync_b4_locator_metadata(project_root: Path, *, run: bool = False) -> dict[str, Any]:
    """Synchronize only normalized locators after a complete read-only preflight.

    This deliberately bypasses ``apply_index``: its embedding cache correctly avoids
    vector writes, but therefore cannot refresh an existing Qdrant payload.
    """
    root = project_root.resolve()
    normalized = normalized_dir(root)
    storage = Storage()
    identity = IndexIdentity.from_settings(VertexSettings.from_env(), root)
    _b4_require_identity(storage, identity)

    with storage.connect() as connection:
        sql_object_count = int(
            connection.execute("SELECT count(1) FROM knowledge_objects").fetchone()[0]
        )

    seen_ids: set[str] = set()
    object_count = 0
    eligible_count = 0
    sql_changes: list[dict[str, Any]] = []
    qdrant_changes: list[dict[str, Any]] = []
    for batch in _b4_batches(iter_jsonl(normalized / "knowledge_objects.jsonl")):
        object_ids = [str(item["object_id"]) for item in batch]
        if len(object_ids) != len(set(object_ids)) or any(
            object_id in seen_ids for object_id in object_ids
        ):
            raise RuntimeError("B4 locator sync found duplicate normalized object IDs")
        seen_ids.update(object_ids)
        object_count += len(batch)
        sql_rows = _b4_sql_rows(storage, object_ids)
        if set(sql_rows) != set(object_ids):
            missing = sorted(set(object_ids) - set(sql_rows))
            raise RuntimeError(
                "B4 locator sync SQL object identity mismatch; "
                f"missing={missing[:3]}"
            )

        eligible_items: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for item in batch:
            sql_locator = _b4_validate_sql_item(item, sql_rows[item["object_id"]])
            if _b4_embedding_eligible(item):
                eligible_count += 1
                eligible_items.append((item, sql_locator))
            elif sql_locator != item["locator"]:
                sql_changes.append({"item": item, "sql_locator": sql_locator})

        if eligible_items:
            point_ids = [storage.point_id(item["object_id"]) for item, _ in eligible_items]
            qdrant_rows = _b4_qdrant_rows(storage, point_ids)
            if set(qdrant_rows) != set(point_ids):
                missing = sorted(set(point_ids) - set(qdrant_rows))
                raise RuntimeError(
                    "B4 locator sync Qdrant point mapping mismatch; "
                    f"missing={missing[:3]}"
                )
            for (item, sql_locator), point_id in zip(eligible_items, point_ids):
                payload = qdrant_rows[point_id].payload or {}
                expected_payload = {
                    "object_id": item["object_id"],
                    "object_type": item["object_type"],
                    "source_id": item["source_id"],
                    "source_version_id": item["source_version_id"],
                    "title": item["title"],
                    "text": item["text"],
                }
                if any(payload.get(key) != value for key, value in expected_payload.items()):
                    raise RuntimeError(
                        f"B4 locator sync Qdrant payload mismatch for {item['object_id']}; "
                        "metadata-only synchronization is unsafe"
                    )
                point_locator = _b4_json(payload.get("locator"))
                if point_locator != sql_locator and point_locator != item["locator"]:
                    raise RuntimeError(
                        f"B4 locator sync Qdrant locator mismatch for {item['object_id']}; "
                        "it matches neither SQL nor normalized state"
                    )
                if sql_locator != item["locator"]:
                    sql_changes.append({"item": item, "sql_locator": sql_locator})
                if point_locator != item["locator"]:
                    qdrant_changes.append({"item": item, "point_id": point_id})

    if object_count != sql_object_count:
        raise RuntimeError(
            "B4 locator sync object-count mismatch; "
            f"normalized={object_count}, sql={sql_object_count}"
        )
    qdrant_count = int(
        storage.qdrant.count(storage.settings.collection_name, exact=True).count
    )
    if qdrant_count != eligible_count:
        raise RuntimeError(
            "B4 locator sync Qdrant count mismatch; "
            f"eligible={eligible_count}, qdrant={qdrant_count}"
        )

    changed_object_ids = {
        change["item"]["object_id"] for change in [*sql_changes, *qdrant_changes]
    }
    report = {
        "valid": True,
        "dry_run": not run,
        "normalized_dir": normalized.name,
        "object_count": object_count,
        "eligible_count": eligible_count,
        "locator_changes": len(changed_object_ids),
        "planned_sql_rows": len(sql_changes),
        "planned_qdrant_payloads": len(qdrant_changes),
        "sql_rows_changed": 0,
        "qdrant_payloads_changed": 0,
        "vectors_changed": 0,
        "index_identity": identity.fingerprint(),
    }
    if not run or not changed_object_ids:
        return report

    for batch in _b4_batches(qdrant_changes):
        storage.qdrant.batch_update_points(
            collection_name=storage.settings.collection_name,
            update_operations=[
                models.SetPayloadOperation(
                    set_payload=models.SetPayload(
                        payload={"locator": change["item"]["locator"]},
                        points=[change["point_id"]],
                    )
                )
                for change in batch
            ],
            wait=True,
        )
        points = _b4_qdrant_rows(
            storage, [change["point_id"] for change in batch]
        )
        for change in batch:
            point_id = change["point_id"]
            if _b4_json((points[point_id].payload or {}).get("locator")) != change["item"]["locator"]:
                raise RuntimeError(
                    f"B4 locator sync Qdrant update did not persist for {change['item']['object_id']}"
                )

    sql = """UPDATE knowledge_objects SET locator=%s
        WHERE object_id=%s AND object_type=%s AND source_id=%s AND source_version_id=%s
          AND title=%s AND text=%s AND authority_level=%s
          AND canonical_locator IS NOT DISTINCT FROM %s AND token_count=%s
          AND embedding_eligible=%s AND content_hash=%s RETURNING object_id"""
    with storage.connect() as connection:
        for change in sql_changes:
            item = change["item"]
            row = connection.execute(
                sql,
                (
                    Jsonb(item["locator"]), item["object_id"], item["object_type"],
                    item["source_id"], item["source_version_id"], item["title"], item["text"],
                    item["authority_level"], item.get("canonical_locator"), item.get("token_count", 0),
                    item.get("embedding_eligible", True),
                    hashlib.sha256(item["text"].encode()).hexdigest(),
                ),
            ).fetchone()
            if row is None:
                raise RuntimeError(
                    f"B4 locator sync SQL update lost semantic invariance for {item['object_id']}"
                )

    return {
        **report,
        "dry_run": False,
        "sql_rows_changed": len(sql_changes),
        "qdrant_payloads_changed": len(qdrant_changes),
    }


def _list_values(value: Any) -> list[Any]:
    return list(value.tolist()) if hasattr(value, "tolist") else list(value)


def _float32_equal(left: Any, right: Any) -> bool:
    return struct.pack("<f", float(left)) == struct.pack("<f", float(right))


def _assert_sparse_vector_equal(expected: Any, actual: Any) -> None:
    if actual is None:
        raise RuntimeError("B3 migration sample is missing its sparse vector")
    def values_by_index(vector: Any) -> dict[int, Any]:
        indices = [int(value) for value in _list_values(vector.indices)]
        values = _list_values(vector.values)
        if len(indices) != len(values) or len(indices) != len(set(indices)):
            raise RuntimeError("B3 migration sparse vector has duplicate or malformed indices")
        return dict(zip(indices, values))

    expected_values = values_by_index(expected)
    actual_values = values_by_index(actual)
    if set(expected_values) != set(actual_values):
        raise RuntimeError("B3 migration sparse vector index mismatch")
    if any(
        not _float32_equal(expected_values[index], actual_values[index])
        for index in expected_values
    ):
        raise RuntimeError("B3 migration sparse vector float32 value mismatch")


def _migration_sparse_samples(storage: Storage, vector_name: str) -> list[Any]:
    """Take the first eight Qdrant points in native deterministic scroll order."""
    cursor = None
    samples: list[Any] = []
    while len(samples) < 8:
        points, cursor = storage.qdrant.scroll(
            collection_name=storage.settings.collection_name,
            limit=8 - len(samples),
            offset=cursor,
            with_payload=True,
            with_vectors=[vector_name],
        )
        samples.extend(points)
        if cursor is None:
            break
    if len(samples) != 8:
        raise RuntimeError(f"B3 metadata migration requires exactly 8 deterministic Qdrant points, got {len(samples)}")
    return samples


def migrate_b3_sparse_identity(project_root: Path, *, run: bool = False) -> dict[str, Any]:
    """Validate eight existing vectors, then optionally replace only schema-3 metadata."""
    root = project_root.resolve()
    storage = Storage()
    vertex_settings = VertexSettings.from_env()
    expected_legacy = LegacyIndexIdentity.from_settings(vertex_settings)
    identity = IndexIdentity.from_settings(vertex_settings, root)
    with storage.connect() as connection:
        row = connection.execute(
            "SELECT fingerprint,payload FROM index_identities WHERE collection_name=%s",
            (storage.settings.collection_name,),
        ).fetchone()
    if row is None:
        raise RuntimeError("B3 metadata migration requires an existing schema-3 index identity")
    payload = row[1] if isinstance(row[1], dict) else json.loads(row[1])
    legacy = LegacyIndexIdentity.model_validate(payload)
    if (
        legacy != expected_legacy
        or payload != expected_legacy.model_dump(mode="json")
        or row[0] != expected_legacy.fingerprint()
    ):
        raise RuntimeError("B3 metadata migration requires the exact expected schema-3 identity")
    collection = storage._verify_qdrant_sparse_config(identity.sparse)
    dense = collection.config.params.vectors.get("dense")
    if dense is None or dense.size != identity.embedding_dimensions:
        raise RuntimeError("B3 metadata migration requires the expected dense Qdrant contract")
    samples = _migration_sparse_samples(storage, identity.sparse.vector_name)
    model, receipt = create_sparse_encoder(root)
    if receipt != identity.sparse:
        raise RuntimeError("B3 metadata migration sparse factory receipt changed during validation")
    texts: list[str] = []
    sample_point_ids: list[str] = []
    for point in samples:
        payload = point.payload or {}
        title, text = payload.get("title"), payload.get("text")
        if not isinstance(title, str) or not isinstance(text, str):
            raise RuntimeError(f"B3 migration sample payload lacks exact title/text: {point.id}")
        sample_point_ids.append(str(point.id))
        texts.append(f"{title}\n{text}")
    embedded = list(model.embed(texts))
    if len(embedded) != len(samples):
        raise RuntimeError("B3 metadata migration sparse encoder returned an unexpected sample count")
    for point, vector in zip(samples, embedded):
        vectors = point.vector or {}
        actual = vectors.get(identity.sparse.vector_name) if isinstance(vectors, dict) else None
        _assert_sparse_vector_equal(vector, actual)
    report = {
        "valid": True,
        "dry_run": not run,
        "migration": "b3_sparse_identity_schema3_to_schema4",
        "sample_count": len(samples),
        "sampling_rule": "first 8 Qdrant points in native scroll order with payload and sparse vector",
        "sample_point_ids": sample_point_ids,
        "old_fingerprint": expected_legacy.fingerprint(),
        "new_fingerprint": identity.fingerprint(),
        "vectors_changed": 0,
    }
    if not run:
        return report
    with storage.connect() as connection:
        updated = connection.execute(
            "UPDATE index_identities SET fingerprint=%s,payload=%s,updated_at=now() "
            "WHERE collection_name=%s AND fingerprint=%s RETURNING fingerprint",
            (
                identity.fingerprint(),
                Jsonb(identity.model_dump(mode="json")),
                storage.settings.collection_name,
                expected_legacy.fingerprint(),
            ),
        ).fetchone()
    if updated is None:
        raise RuntimeError("B3 metadata migration lost the expected schema-3 identity before update")
    return {**report, "dry_run": False, "updated": True}


def _apply_index(
    project_root: Path,
    *,
    limit: int | None = None,
    offset: int = 0,
    skip_sql_sync: bool = False,
) -> dict[str, Any]:
    root = normalized_dir(project_root); storage = Storage()
    vertex_settings = VertexSettings.from_env()
    identity = IndexIdentity.from_settings(vertex_settings, project_root)
    storage.initialize(identity)
    with storage.connect() as connection:
        connection.execute(
            "UPDATE ingestion_runs SET status='interrupted',completed_at=now(),"
            "report=report || '{\"error\":\"orphaned running process\"}'::jsonb WHERE status='running'"
        )
        run_id=connection.execute("INSERT INTO ingestion_runs(manifest_hash,status,report) VALUES(%s,'running',%s) RETURNING run_id",(root.name,json.dumps({"offset":offset,"limit":limit}))).fetchone()[0]
    manifest=json.loads((project_root/"data"/"manifests"/"source_manifest.json").read_text(encoding="utf-8")); storage.upsert_source_versions(manifest)
    objects = load_jsonl(root / "knowledge_objects.jsonl")
    aliases = load_jsonl(root / "knowledge_aliases.jsonl")
    workflows = load_jsonl(root / "workflow_steps.jsonl")
    relation_path = root / "relation_edges.jsonl"
    candidate_path = root / "relation_candidates.jsonl"
    ingestion_report = json.loads((root / "ingestion_report.json").read_text(encoding="utf-8"))
    relation_count = int(ingestion_report["relation_count"])
    relation_candidate_count = int(ingestion_report["relation_candidate_count"])
    if not skip_sql_sync:
        storage.upsert_objects(objects)
    storage.upsert_aliases(aliases)
    if not skip_sql_sync:
        storage.upsert_relations(iter_jsonl(relation_path))
        storage.upsert_relation_candidates(iter_jsonl(candidate_path))
        storage.upsert_workflows(workflows)
    deleted_sql=0
    if skip_sql_sync:
        deleted_sql += storage.prune_table(
            "knowledge_aliases", "alias_id", (item["alias_id"] for item in aliases)
        )
    if not skip_sql_sync and limit is None and offset==0:
        deleted_sql+=storage.prune_table("relation_edges","edge_id",(item["edge_id"] for item in iter_jsonl(relation_path)))
        deleted_sql+=storage.prune_table("relation_candidates","candidate_id",(item["candidate_id"] for item in iter_jsonl(candidate_path)))
        deleted_sql+=storage.prune_table("workflow_steps","step_id",(item["step_id"] for item in workflows))
        deleted_sql+=storage.prune_table("knowledge_aliases","alias_id",(item["alias_id"] for item in aliases))
        deleted_sql+=storage.prune_table("knowledge_objects","object_id",(item["object_id"] for item in objects))
    eligible = [item for item in objects if item.get("embedding_eligible") and 10 <= item.get("token_count",0) <= 1800 and len(item["title"])+1+len(item["text"])<=4000]
    selected = eligible[offset: offset + limit if limit else None]
    cached: set[str] = set()
    if selected:
        cache_keys=[]
        for item in selected:
            text=f"{item['title']}\n{item['text']}"; text_hash=hashlib.sha256(text.encode()).hexdigest()
            cache_keys.append(hashlib.sha256(f"{identity.embedding_model}\x1fRETRIEVAL_DOCUMENT\x1f{text_hash}".encode()).hexdigest())
        with storage.connect() as connection:
            cached = _compatible_cache_keys(
                connection, cache_keys, identity.embedding_dimensions
            )
        point_ids=[storage.point_id(item["object_id"]) for item in selected]
        existing=set()
        for start in range(0,len(point_ids),256):
            existing.update(str(point.id) for point in storage.qdrant.retrieve(collection_name=storage.settings.collection_name,ids=point_ids[start:start+256],with_payload=False,with_vectors=False))
        selected=[item for item,key in zip(selected,cache_keys) if not (key in cached and storage.point_id(item["object_id"]) in existing)]
    vertex = VertexAIClient(vertex_settings) if selected else None
    sparse_model, sparse_identity = create_sparse_encoder(project_root) if selected else (None, identity.sparse)
    if sparse_identity != identity.sparse:
        raise RuntimeError("sparse factory receipt changed during index initialization")
    indexed = 0
    batch_size=64
    for start in range(0, len(selected), batch_size):
        assert sparse_model is not None
        batch = selected[start:start+batch_size]; texts = [f"{item['title']}\n{item['text']}" for item in batch]
        dense = vertex.embed_documents(texts)
        sparse_vectors = list(sparse_model.embed(texts))
        points = []
        for item, dense_vector, sparse_vector, text in zip(batch, dense, sparse_vectors, texts):
            points.append(models.PointStruct(id=storage.point_id(item["object_id"]), vector={"dense": dense_vector, sparse_identity.vector_name: models.SparseVector(indices=sparse_vector.indices.tolist(), values=sparse_vector.values.tolist())}, payload={"object_id":item["object_id"],"source_id":item["source_id"],"source_version_id":item["source_version_id"],"object_type":item["object_type"],"title":item["title"],"authority_level":item["authority_level"],"locator":item["locator"],"text":item["text"]}))
        storage.qdrant.upsert(collection_name=storage.settings.collection_name, points=points, wait=True); indexed += len(points)
        with storage.connect() as connection:
            for item, text in zip(batch, texts):
                text_hash = hashlib.sha256(text.encode()).hexdigest(); cache_key = hashlib.sha256(f"{identity.embedding_model}\x1fRETRIEVAL_DOCUMENT\x1f{text_hash}".encode()).hexdigest()
                _record_embedding_cache(
                    connection,
                    cache_key=cache_key,
                    object_id=item["object_id"],
                    model=identity.embedding_model,
                    task_type="RETRIEVAL_DOCUMENT",
                    text_hash=text_hash,
                    dimensions=identity.embedding_dimensions,
                )
    deleted_vectors=0
    if limit is None and offset == 0:
        valid_ids={storage.point_id(item["object_id"]) for item in eligible}; stale=[]; cursor=None
        while True:
            points,cursor=storage.qdrant.scroll(collection_name=storage.settings.collection_name,scroll_filter=None,limit=256,offset=cursor,with_payload=False,with_vectors=False)
            stale.extend(str(point.id) for point in points if str(point.id) not in valid_ids)
            if cursor is None: break
        if stale:
            storage.qdrant.delete(collection_name=storage.settings.collection_name,points_selector=models.PointIdsList(points=stale),wait=True)
            deleted_vectors=len(stale)
    result={"sql_objects":len(objects),"sql_relations":relation_count,"sql_relation_candidates":relation_candidate_count,"sql_aliases":len(aliases),"indexed_vectors":indexed,"eligible_total":len(eligible),"cached_vectors":len(cached),"deleted_sql_records":deleted_sql,"deleted_vectors":deleted_vectors,"offset":offset,"index_identity":identity.fingerprint()}
    with storage.connect() as connection:
        connection.execute("UPDATE ingestion_runs SET status='completed',completed_at=now(),report=%s WHERE run_id=%s",(json.dumps(result),run_id))
    return result


def apply_index(
    project_root: Path,
    *,
    limit: int | None = None,
    offset: int = 0,
    skip_sql_sync: bool = False,
) -> dict[str, Any]:
    """Apply one idempotent run and fail any interrupted run explicitly."""
    try:
        return _apply_index(
            project_root, limit=limit, offset=offset, skip_sql_sync=skip_sql_sync
        )
    except BaseException as exc:
        try:
            storage = Storage()
            with storage.connect() as connection:
                connection.execute(
                    "UPDATE ingestion_runs SET status='failed',completed_at=now(),report=report || %s::jsonb "
                    "WHERE run_id=(SELECT run_id FROM ingestion_runs WHERE status='running' ORDER BY run_id DESC LIMIT 1)",
                    (json.dumps({"error": type(exc).__name__, "message": str(exc)[:2000]}),),
                )
        except Exception:
            pass
        raise


def resume_index(project_root: Path, run_id: int) -> dict[str, Any]:
    """Resume a failed run using its immutable manifest and original slice.

    Completed batches are skipped by the embedding cache plus Qdrant point check.
    """
    storage = Storage()
    with storage.connect() as connection:
        row = connection.execute(
            "SELECT manifest_hash,status,report FROM ingestion_runs WHERE run_id=%s", (run_id,)
        ).fetchone()
    if row is None:
        raise ValueError(f"index run does not exist: {run_id}")
    manifest_hash, status, report = row
    if status not in {"failed", "interrupted", "running"}:
        raise ValueError(f"only failed/interrupted/orphaned-running runs can resume; status={status}")
    if normalized_dir(project_root).name != manifest_hash:
        raise RuntimeError("normalized manifest differs from the failed run")
    return apply_index(
        project_root,
        limit=report.get("limit"),
        offset=int(report.get("offset", 0)),
        skip_sql_sync=True,
    )
