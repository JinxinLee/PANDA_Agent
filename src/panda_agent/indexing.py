"""M3 idempotent SQL/Qdrant indexing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from fastembed import SparseTextEmbedding
from qdrant_client import models

from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.storage import Storage, iter_jsonl, load_jsonl


class IndexIdentity(BaseModel):
    """Immutable vector-index contract; any field change requires migration."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    embedding_model: str
    embedding_dimensions: int
    distance: str
    sparse_model: str
    index_schema_version: str

    def fingerprint(self) -> str:
        payload = self.model_dump_json(exclude_none=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_settings(cls, settings: VertexSettings) -> "IndexIdentity":
        return cls(
            embedding_model=settings.embedding_model,
            embedding_dimensions=settings.embedding_dimensions,
            distance="cosine",
            sparse_model="Qdrant/bm25",
            index_schema_version="2",
        )


def normalized_dir(project_root: Path) -> Path:
    reports = list((project_root / "data" / "normalized").glob("*/ingestion_report.json"))
    if not reports: raise RuntimeError("M2 output not found")
    return max(reports, key=lambda path: path.stat().st_mtime).parent


def index_plan(project_root: Path) -> dict[str, int]:
    root = normalized_dir(project_root)
    objects = load_jsonl(root / "knowledge_objects.jsonl")
    eligible = [item for item in objects if item.get("embedding_eligible") and 10 <= item.get("token_count",0) <= 1800 and len(item["title"])+1+len(item["text"])<=4000]
    return {"objects": len(objects), "embedding_eligible": len(eligible), "relations": len(load_jsonl(root / "relation_edges.jsonl")), "relation_candidates": len(load_jsonl(root / "relation_candidates.jsonl")), "aliases": len(load_jsonl(root / "knowledge_aliases.jsonl")), "workflows": len(load_jsonl(root / "workflow_steps.jsonl"))}


def verify_index(project_root:Path)->dict[str,Any]:
    root=normalized_dir(project_root); storage=Storage(); objects=load_jsonl(root/"knowledge_objects.jsonl")
    report=json.loads((root/"ingestion_report.json").read_text(encoding="utf-8"))
    eligible=[item for item in objects if item.get("embedding_eligible") and 10<=item.get("token_count",0)<=1800 and len(item["title"])+1+len(item["text"])<=4000]
    expected={storage.point_id(item["object_id"]) for item in eligible}; actual=set(); cursor=None
    while True:
        points,cursor=storage.qdrant.scroll(collection_name=storage.settings.collection_name,limit=256,offset=cursor,with_payload=False,with_vectors=False)
        actual.update(str(point.id) for point in points)
        if cursor is None: break
    with storage.connect() as connection:
        sql_counts={"objects":connection.execute("select count(1) from knowledge_objects").fetchone()[0],"relations":connection.execute("select count(1) from relation_edges").fetchone()[0],"relation_candidates":connection.execute("select count(1) from relation_candidates").fetchone()[0],"aliases":connection.execute("select count(1) from knowledge_aliases").fetchone()[0],"workflows":connection.execute("select count(1) from workflow_steps").fetchone()[0]}
    expected_sql={"objects":report["object_count"],"relations":report["relation_count"],"relation_candidates":report["relation_candidate_count"],"aliases":report.get("alias_count",0),"workflows":report["workflow_count"]}
    return {"valid":expected==actual and sql_counts==expected_sql,"expected_points":len(expected),"actual_points":len(actual),"missing_points":len(expected-actual),"stale_points":len(actual-expected),"sql_counts":sql_counts,"expected_sql_counts":expected_sql}


def _apply_index(
    project_root: Path,
    *,
    limit: int | None = None,
    offset: int = 0,
    skip_sql_sync: bool = False,
) -> dict[str, Any]:
    root = normalized_dir(project_root); storage = Storage()
    vertex_settings = VertexSettings.from_env()
    identity = IndexIdentity.from_settings(vertex_settings)
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
            cached={row[0] for row in connection.execute("SELECT cache_key FROM embedding_records WHERE cache_key=ANY(%s)",(cache_keys,)).fetchall()}
        point_ids=[storage.point_id(item["object_id"]) for item in selected]
        existing=set()
        for start in range(0,len(point_ids),256):
            existing.update(str(point.id) for point in storage.qdrant.retrieve(collection_name=storage.settings.collection_name,ids=point_ids[start:start+256],with_payload=False,with_vectors=False))
        selected=[item for item,key in zip(selected,cache_keys) if not (key in cached and storage.point_id(item["object_id"]) in existing)]
    vertex = VertexAIClient(vertex_settings) if selected else None
    sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25",cache_dir=str(project_root/"data"/"cache"/"fastembed")) if selected else None
    indexed = 0
    batch_size=64
    for start in range(0, len(selected), batch_size):
        batch = selected[start:start+batch_size]; texts = [f"{item['title']}\n{item['text']}" for item in batch]
        dense = vertex.embed_documents(texts)
        sparse = list(sparse_model.embed(texts))
        points = []
        for item, dense_vector, sparse_vector, text in zip(batch, dense, sparse, texts):
            points.append(models.PointStruct(id=storage.point_id(item["object_id"]), vector={"dense": dense_vector, "sparse": models.SparseVector(indices=sparse_vector.indices.tolist(), values=sparse_vector.values.tolist())}, payload={"object_id":item["object_id"],"source_id":item["source_id"],"source_version_id":item["source_version_id"],"object_type":item["object_type"],"title":item["title"],"authority_level":item["authority_level"],"locator":item["locator"],"text":item["text"]}))
        storage.qdrant.upsert(collection_name=storage.settings.collection_name, points=points, wait=True); indexed += len(points)
        with storage.connect() as connection:
            for item, text in zip(batch, texts):
                text_hash = hashlib.sha256(text.encode()).hexdigest(); cache_key = hashlib.sha256(f"{identity.embedding_model}\x1fRETRIEVAL_DOCUMENT\x1f{text_hash}".encode()).hexdigest()
                connection.execute("INSERT INTO embedding_records(cache_key,object_id,model,task_type,text_hash,dimensions) VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(cache_key) DO NOTHING", (cache_key,item["object_id"],identity.embedding_model,"RETRIEVAL_DOCUMENT",text_hash,identity.embedding_dimensions))
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
