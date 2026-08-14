"""M3 PostgreSQL schema and Qdrant collection adapters."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import psycopg
from psycopg.types.json import Jsonb
from qdrant_client import QdrantClient, models

from panda_agent.config import SPARSE_VECTOR_MODIFIER, SPARSE_VECTOR_NAME


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS source_versions (
  source_version_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, source_kind TEXT NOT NULL,
  version_label TEXT NOT NULL, content_hash TEXT NOT NULL, metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS knowledge_objects (
  object_id TEXT PRIMARY KEY, object_type TEXT NOT NULL, source_id TEXT NOT NULL,
  source_version_id TEXT NOT NULL, title TEXT NOT NULL, text TEXT NOT NULL,
  authority_level TEXT NOT NULL, locator JSONB NOT NULL, metadata JSONB NOT NULL,
  canonical_locator TEXT, token_count INTEGER NOT NULL, embedding_eligible BOOLEAN NOT NULL,
  content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS knowledge_aliases (
  alias_id TEXT PRIMARY KEY, alias_text TEXT NOT NULL, normalized_alias TEXT NOT NULL,
  target_object_id TEXT NOT NULL REFERENCES knowledge_objects(object_id) ON DELETE CASCADE,
  source_version_id TEXT NOT NULL, review_status TEXT NOT NULL, payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS knowledge_alias_normalized_idx ON knowledge_aliases(normalized_alias);
CREATE INDEX IF NOT EXISTS knowledge_source_idx ON knowledge_objects(source_id, source_version_id, object_type);
CREATE INDEX IF NOT EXISTS knowledge_title_idx ON knowledge_objects(lower(title));
CREATE INDEX IF NOT EXISTS knowledge_text_fts_idx ON knowledge_objects USING GIN(to_tsvector('english', left(title || ' ' || text, 250000)));
CREATE TABLE IF NOT EXISTS relation_edges (
  edge_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, predicate TEXT NOT NULL,
  object_id TEXT NOT NULL, confidence DOUBLE PRECISION NOT NULL, creation_method TEXT NOT NULL,
  review_status TEXT NOT NULL, payload JSONB NOT NULL,
  CONSTRAINT relation_subject_fk FOREIGN KEY(subject_id) REFERENCES knowledge_objects(object_id) ON DELETE CASCADE,
  CONSTRAINT relation_object_fk FOREIGN KEY(object_id) REFERENCES knowledge_objects(object_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS relation_subject_idx ON relation_edges(subject_id, predicate);
CREATE INDEX IF NOT EXISTS relation_object_idx ON relation_edges(object_id, predicate);
CREATE TABLE IF NOT EXISTS relation_candidates (
  candidate_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, predicate TEXT NOT NULL,
  raw_target TEXT NOT NULL, resolution_status TEXT NOT NULL, payload JSONB NOT NULL,
  CONSTRAINT relation_candidate_subject_fk FOREIGN KEY(subject_id) REFERENCES knowledge_objects(object_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS relation_candidate_subject_idx ON relation_candidates(subject_id, predicate);
CREATE INDEX IF NOT EXISTS relation_candidate_status_idx ON relation_candidates(resolution_status);
CREATE TABLE IF NOT EXISTS workflow_steps (
  step_id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, name TEXT NOT NULL, payload JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS ingestion_runs (
  run_id BIGSERIAL PRIMARY KEY, manifest_hash TEXT NOT NULL, started_at TIMESTAMPTZ DEFAULT now(),
  completed_at TIMESTAMPTZ, status TEXT NOT NULL, report JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS index_identities (
  collection_name TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, payload JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS embedding_records (
  cache_key TEXT PRIMARY KEY, object_id TEXT NOT NULL, model TEXT NOT NULL, task_type TEXT NOT NULL,
  text_hash TEXT NOT NULL, dimensions INTEGER NOT NULL, indexed_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS qa_runs (
  run_id UUID PRIMARY KEY, created_at TIMESTAMPTZ DEFAULT now(), question TEXT NOT NULL,
  status TEXT NOT NULL, trace JSONB NOT NULL
);
"""


@dataclass(frozen=True)
class StorageSettings:
    database_url: str = "postgresql://panda:panda@127.0.0.1:55432/panda_qa"
    qdrant_url: str = "http://127.0.0.1:6333"
    collection_name: str = "panda_knowledge_v1"

    @classmethod
    def from_env(cls) -> "StorageSettings":
        return cls(
            database_url=os.getenv("PANDA_DATABASE_URL", cls.database_url),
            qdrant_url=os.getenv("PANDA_QDRANT_URL", cls.qdrant_url),
            collection_name=os.getenv("PANDA_QDRANT_COLLECTION", cls.collection_name),
        )


class Storage:
    def __init__(self, settings: StorageSettings | None = None) -> None:
        self.settings = settings or StorageSettings.from_env()
        self.qdrant = QdrantClient(url=self.settings.qdrant_url, timeout=60)

    def connect(self):
        return psycopg.connect(self.settings.database_url)

    def initialize(self, index_identity: Any | None = None) -> None:
        if index_identity is not None and (
            index_identity.sparse_vector_name != SPARSE_VECTOR_NAME
            or index_identity.sparse_modifier != SPARSE_VECTOR_MODIFIER
        ):
            raise RuntimeError(
                "index identity sparse contract mismatch: "
                f"vector_name={index_identity.sparse_vector_name!r}, "
                f"modifier={index_identity.sparse_modifier!r}; "
                "use the supported B1 sparse contract or perform an explicit migration"
            )
        payload = None
        with self.connect() as connection:
            connection.execute(SCHEMA_SQL)
            if index_identity is not None:
                payload = index_identity.model_dump(mode="json")
                existing = connection.execute(
                    "SELECT fingerprint FROM index_identities WHERE collection_name=%s",
                    (self.settings.collection_name,),
                ).fetchone()
                if existing and existing[0] != index_identity.fingerprint():
                    raise RuntimeError(
                        "index identity mismatch; use a new collection or perform an explicit migration"
                    )
        dimensions = index_identity.embedding_dimensions if index_identity is not None else 3072
        if not self.qdrant.collection_exists(self.settings.collection_name):
            self.qdrant.create_collection(
                collection_name=self.settings.collection_name,
                vectors_config={"dense": models.VectorParams(size=dimensions, distance=models.Distance.COSINE)},
                sparse_vectors_config={
                    SPARSE_VECTOR_NAME: models.SparseVectorParams(
                        modifier=models.Modifier(SPARSE_VECTOR_MODIFIER)
                    )
                },
            )
        collection=self.qdrant.get_collection(self.settings.collection_name)
        dense_config = collection.config.params.vectors.get("dense")
        if dense_config is not None and dense_config.size != dimensions:
            raise RuntimeError(
                f"Qdrant dense dimension mismatch: existing={dense_config.size}, configured={dimensions}"
            )
        sparse_config = collection.config.params.sparse_vectors
        sparse_vector = (sparse_config or {}).get(SPARSE_VECTOR_NAME)
        modifier = getattr(sparse_vector, "modifier", None)
        modifier_value = getattr(modifier, "value", modifier)
        if modifier_value != SPARSE_VECTOR_MODIFIER:
            raise RuntimeError(
                "Qdrant sparse modifier mismatch: "
                f"existing={modifier_value!r}, configured={SPARSE_VECTOR_MODIFIER!r}; "
                "use a new collection or perform an explicit migration"
            )
        if index_identity is not None:
            with self.connect() as connection:
                connection.execute(
                    "INSERT INTO index_identities(collection_name,fingerprint,payload) VALUES(%s,%s,%s) "
                    "ON CONFLICT(collection_name) DO UPDATE SET fingerprint=excluded.fingerprint,payload=excluded.payload,updated_at=now()",
                    (self.settings.collection_name, index_identity.fingerprint(), Jsonb(payload)),
                )
        for field in ("source_id","source_version_id","object_type","authority_level"):
            if field not in collection.payload_schema:
                self.qdrant.create_payload_index(collection_name=self.settings.collection_name,field_name=field,field_schema=models.PayloadSchemaType.KEYWORD,wait=True)

    def upsert_objects(self, records: Iterable[dict[str, Any]]) -> None:
        sql = """INSERT INTO knowledge_objects
          (object_id,object_type,source_id,source_version_id,title,text,authority_level,locator,metadata,canonical_locator,token_count,embedding_eligible,content_hash)
          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
          ON CONFLICT (object_id) DO UPDATE SET title=excluded.title,text=excluded.text,locator=excluded.locator,
          metadata=excluded.metadata,token_count=excluded.token_count,embedding_eligible=excluded.embedding_eligible,content_hash=excluded.content_hash"""
        with self.connect() as connection:
            def rows():
              for item in records:
                content_hash = __import__("hashlib").sha256(item["text"].encode()).hexdigest()
                yield (item["object_id"],item["object_type"],item["source_id"],item["source_version_id"],item["title"],item["text"],item["authority_level"],Jsonb(item["locator"]),Jsonb(item.get("metadata",{})),item.get("canonical_locator"),item.get("token_count",0),item.get("embedding_eligible",True),content_hash)
            with connection.cursor() as cursor: cursor.executemany(sql,rows())

    def upsert_aliases(self, records: Iterable[dict[str, Any]]) -> None:
        sql = """INSERT INTO knowledge_aliases
          (alias_id,alias_text,normalized_alias,target_object_id,source_version_id,review_status,payload)
          VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(alias_id) DO UPDATE SET
          alias_text=excluded.alias_text,normalized_alias=excluded.normalized_alias,
          target_object_id=excluded.target_object_id,source_version_id=excluded.source_version_id,
          review_status=excluded.review_status,payload=excluded.payload"""
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(sql, (
                    (item["alias_id"], item["alias_text"], item["normalized_alias"],
                     item["target_object_id"], item["source_version_id"], item["review_status"], Jsonb(item))
                    for item in records
                ))

    def upsert_source_versions(self, manifest: dict[str, Any]) -> None:
        rows=[]
        for item in manifest["repositories"]: rows.append((f"{item['repo_id']}@{item['commit_sha']}",item["repo_id"],"git_repository",item["commit_sha"],item["commit_sha"],item))
        for item in manifest["papers"]: rows.append((f"{item['doc_id']}@{item['sha256']}",item["doc_id"],"pdf",item["sha256"],item["sha256"],item))
        for item in manifest["web_documents"]: rows.append((f"{item['doc_id']}@{item['snapshot_hash']}",item["doc_id"],"web_documentation",item["captured_at"],item["snapshot_hash"],item))
        with self.connect() as connection:
            for row in rows: connection.execute("INSERT INTO source_versions(source_version_id,source_id,source_kind,version_label,content_hash,metadata) VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(source_version_id) DO UPDATE SET metadata=excluded.metadata",(*row[:5],Jsonb(row[5])))

    def upsert_relations(self, records: Iterable[dict[str, Any]]) -> None:
        sql = """INSERT INTO relation_edges(edge_id,subject_id,predicate,object_id,confidence,creation_method,review_status,payload)
          VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(edge_id) DO UPDATE SET
          subject_id=excluded.subject_id,predicate=excluded.predicate,object_id=excluded.object_id,
          confidence=excluded.confidence,creation_method=excluded.creation_method,
          review_status=excluded.review_status,payload=excluded.payload"""
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(sql,((item["edge_id"],item["subject_id"],item["predicate"],item["object_id"],item["confidence"],item["creation_method"],item["review_status"],Jsonb(item)) for item in records))

    def upsert_relation_candidates(self, records: Iterable[dict[str, Any]]) -> None:
        sql = """INSERT INTO relation_candidates(candidate_id,subject_id,predicate,raw_target,resolution_status,payload)
          VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT(candidate_id) DO UPDATE SET
          subject_id=excluded.subject_id,predicate=excluded.predicate,raw_target=excluded.raw_target,
          resolution_status=excluded.resolution_status,payload=excluded.payload"""
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(sql,((item["candidate_id"],item["subject_id"],item["predicate"],item["raw_target"],item["resolution_status"],Jsonb(item)) for item in records))

    def upsert_workflows(self, records: Iterable[dict[str, Any]]) -> None:
        sql = """INSERT INTO workflow_steps(step_id,workflow_id,name,payload) VALUES(%s,%s,%s,%s)
          ON CONFLICT(step_id) DO UPDATE SET payload=excluded.payload"""
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(sql,((item["step_id"],item["workflow_id"],item["name"],Jsonb(item)) for item in records))

    def prune_table(self, table: str, key: str, valid_ids: Iterable[str]) -> int:
        allowed={"knowledge_objects":"object_id","knowledge_aliases":"alias_id","relation_edges":"edge_id","relation_candidates":"candidate_id","workflow_steps":"step_id"}
        if allowed.get(table)!=key: raise ValueError("unsupported prune target")
        with self.connect() as connection:
            connection.execute("CREATE TEMP TABLE current_ids(value TEXT PRIMARY KEY) ON COMMIT DROP")
            with connection.cursor().copy("COPY current_ids(value) FROM STDIN") as copy:
                for value in valid_ids: copy.write_row((value,))
            deleted=connection.execute(f"DELETE FROM {table} target WHERE NOT EXISTS (SELECT 1 FROM current_ids current WHERE current.value=target.{key}) RETURNING target.{key}").fetchall()
            if table=="knowledge_objects": connection.execute("DELETE FROM embedding_records e WHERE NOT EXISTS (SELECT 1 FROM knowledge_objects k WHERE k.object_id=e.object_id)")
        return len(deleted)

    @staticmethod
    def point_id(object_id: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"panda-qa:{object_id}"))


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return list(iter_jsonl(path))
