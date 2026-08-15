from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from panda_agent.indexing import IndexIdentity, sync_b4_locator_metadata
from panda_agent.sparse import SparseEncoderReceipt


class _Result:
    def __init__(self, rows):
        self.rows = list(rows)

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


class _Connection:
    def __init__(self, storage):
        self.storage = storage

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, statement, params=None):
        compact = " ".join(statement.split())
        if compact.startswith("SELECT fingerprint,payload"):
            return _Result([(self.storage.fingerprint, self.storage.identity.model_dump(mode="json"))])
        if compact == "SELECT count(1) FROM knowledge_objects":
            return _Result([(len(self.storage.rows),)])
        if "FROM knowledge_objects WHERE object_id=ANY" in compact:
            return _Result([self.storage.sql_row(object_id) for object_id in params[0] if object_id in self.storage.rows])
        if compact.startswith("UPDATE knowledge_objects SET locator="):
            locator, object_id, object_type, source_id, source_version_id, title, text, authority, canonical, tokens, eligible, content_hash = params
            item = self.storage.rows.get(object_id)
            if item is None:
                return _Result([])
            invariant = (
                item["object_type"], item["source_id"], item["source_version_id"], item["title"],
                item["text"], item["authority_level"], item.get("canonical_locator"), item["token_count"], item["embedding_eligible"],
                hashlib.sha256(item["text"].encode()).hexdigest(),
            )
            if invariant != (object_type, source_id, source_version_id, title, text, authority, canonical, tokens, eligible, content_hash):
                return _Result([])
            item["locator"] = getattr(locator, "obj", locator)
            self.storage.sql_update_calls += 1
            return _Result([(object_id,)])
        raise AssertionError(f"unexpected SQL: {compact}")


class _Qdrant:
    def __init__(self, storage):
        self.storage = storage
        self.retrieve_calls = 0
        self.batch_update_calls = []
        self.upsert_called = False

    def count(self, *_args, **_kwargs):
        return SimpleNamespace(count=len(self.storage.points))

    def retrieve(self, collection_name, ids, **_kwargs):
        assert collection_name == "collection"
        self.retrieve_calls += 1
        return [self.storage.points[point_id] for point_id in ids if point_id in self.storage.points]

    def batch_update_points(self, *, collection_name, update_operations, wait):
        self.batch_update_calls.append(
            {"collection_name": collection_name, "update_operations": update_operations, "wait": wait}
        )
        for operation in update_operations:
            set_payload = operation.set_payload
            assert set(set_payload.payload) == {"locator"}
            for point_id in set_payload.points:
                self.storage.points[point_id].payload.update(set_payload.payload)

    def set_payload(self, *_args, **_kwargs):
        raise AssertionError("B4 locator synchronization must use batched SetPayloadOperation")

    def upsert(self, *_args, **_kwargs):
        self.upsert_called = True
        raise AssertionError("B4 locator synchronization must not upsert vectors")


class _Storage:
    def __init__(self, identity, rows, point_payload_overrides=None):
        self.identity = identity
        self.fingerprint = identity.fingerprint()
        self.settings = SimpleNamespace(collection_name="collection")
        self.rows = {item["object_id"]: {**item, "locator": dict(item["old_locator"])} for item in rows}
        self.sql_update_calls = 0
        self.points = {}
        for item in rows:
            if item["eligible"]:
                payload = {
                    "object_id": item["object_id"],
                    "object_type": item["object_type"],
                    "source_id": item["source_id"],
                    "source_version_id": item["source_version_id"],
                    "title": item["title"],
                    "text": item["text"],
                    "locator": dict(item["old_locator"]),
                }
                payload.update((point_payload_overrides or {}).get(item["object_id"], {}))
                self.points[self.point_id(item["object_id"])] = SimpleNamespace(
                    id=self.point_id(item["object_id"]), payload=payload
                )
        self.qdrant = _Qdrant(self)
        self.collection = SimpleNamespace(
            config=SimpleNamespace(
                params=SimpleNamespace(vectors={"dense": SimpleNamespace(size=3072)})
            )
        )

    def connect(self):
        return _Connection(self)

    def point_id(self, object_id):
        return f"point:{object_id}"

    def _verify_qdrant_sparse_config(self, receipt):
        assert receipt == self.identity.sparse
        return self.collection

    def sql_row(self, object_id):
        item = self.rows[object_id]
        return (
            object_id, item["object_type"], item["source_id"], item["source_version_id"], item["title"], item["text"],
            item["authority_level"], item["locator"], item.get("canonical_locator"), item["token_count"],
            item["embedding_eligible"], hashlib.sha256(item["text"].encode()).hexdigest(),
        )


def _identity() -> IndexIdentity:
    return IndexIdentity(
        embedding_model="gemini-embedding-2",
        embedding_dimensions=3072,
        distance="cosine",
        sparse=SparseEncoderReceipt(
            model_name="Qdrant/bm25", language="english", vector_name="sparse", modifier="idf",
            fastembed_version="test", mmh3_version="test", py_rust_stemmers_version="test",
            tokenizer="test", token_max_length=40, stopwords_sha256="a" * 64, stemmer="test",
            hash_function="test", avg_len=256.0, k=1.2, b=0.75, disable_stemmer=False,
        ),
        index_schema_version="4",
    )


def _records():
    old = {"path": "old.cc", "start_line": 1, "end_line": 99}
    return [
        {
            "object_id": "object.eligible", "object_type": "function", "authority_level": "primary", "source_id": "repo", "source_version_id": "repo@sha",
            "title": "Eligible", "text": "eligible text", "canonical_locator": "old.cc:1",
            "token_count": 10, "embedding_eligible": True, "eligible": True,
            "old_locator": old, "locator": {"path": "old.cc", "start_line": 5, "end_line": 8},
        },
        {
            "object_id": "object.not-eligible", "object_type": "source_file", "authority_level": "primary", "source_id": "repo", "source_version_id": "repo@sha",
            "title": "Not eligible", "text": "short", "canonical_locator": "short.txt:1",
            "token_count": 1, "embedding_eligible": True, "eligible": False,
            "old_locator": {"path": "short.txt", "start_line": 1, "end_line": 20},
            "locator": {"path": "short.txt", "start_line": 1, "end_line": 2},
        },
    ]


class B4LocatorSyncTests(TestCase):
    def _run(self, storage, records, *, run=False):
        identity = storage.identity
        with (
            patch("panda_agent.indexing.Storage", return_value=storage),
            patch("panda_agent.indexing.VertexSettings.from_env"),
            patch("panda_agent.indexing.IndexIdentity.from_settings", return_value=identity),
            patch("panda_agent.indexing.normalized_dir", return_value=Path("normalized")),
            patch("panda_agent.indexing.iter_jsonl", return_value=iter(records)),
            patch("panda_agent.indexing.B4_EXPECTED_INDEX_FINGERPRINT", identity.fingerprint()),
        ):
            return sync_b4_locator_metadata(Path("."), run=run)

    def test_dry_run_validates_all_state_without_writes(self):
        identity = _identity()
        storage = _Storage(identity, _records())

        report = self._run(storage, _records())

        self.assertTrue(report["valid"])
        self.assertTrue(report["dry_run"])
        self.assertEqual(report["locator_changes"], 2)
        self.assertEqual(report["planned_qdrant_payloads"], 1)
        self.assertEqual(report["sql_rows_changed"], 0)
        self.assertEqual(report["qdrant_payloads_changed"], 0)
        self.assertEqual(report["vectors_changed"], 0)
        self.assertEqual(storage.sql_update_calls, 0)
        self.assertEqual(storage.qdrant.batch_update_calls, [])
        self.assertFalse(storage.qdrant.upsert_called)

    def test_explicit_apply_updates_only_locator_payload_and_sql_locator(self):
        identity = _identity()
        records = _records()
        storage = _Storage(identity, records)

        report = self._run(storage, records, run=True)

        self.assertFalse(report["dry_run"])
        self.assertEqual(report["sql_rows_changed"], 2)
        self.assertEqual(report["qdrant_payloads_changed"], 1)
        self.assertEqual(storage.sql_update_calls, 2)
        self.assertEqual(len(storage.qdrant.batch_update_calls), 1)
        operation = storage.qdrant.batch_update_calls[0]["update_operations"][0]
        self.assertEqual(operation.set_payload.payload, {"locator": records[0]["locator"]})
        self.assertEqual(operation.set_payload.points, ["point:object.eligible"])
        self.assertEqual(storage.rows["object.eligible"]["locator"], records[0]["locator"])
        self.assertEqual(storage.points["point:object.eligible"].payload["locator"], records[0]["locator"])
        self.assertFalse(storage.qdrant.upsert_called)

    def test_unknown_qdrant_locator_fails_even_when_sql_is_already_normalized(self):
        identity = _identity()
        records = _records()
        storage = _Storage(
            identity, records,
            {"object.eligible": {"locator": {"path": "unknown.cc", "start_line": 3, "end_line": 4}}},
        )
        storage.rows["object.eligible"]["locator"] = records[0]["locator"]

        with self.assertRaisesRegex(RuntimeError, "Qdrant locator mismatch"):
            self._run(storage, records)

        self.assertEqual(storage.sql_update_calls, 0)
        self.assertEqual(storage.qdrant.batch_update_calls, [])

    def test_persisted_identity_mismatch_fails_before_payload_access(self):
        identity = _identity()
        storage = _Storage(identity, _records())
        storage.fingerprint = "wrong"

        with self.assertRaisesRegex(RuntimeError, "persisted index identity mismatch"):
            self._run(storage, _records())

        self.assertEqual(storage.qdrant.retrieve_calls, 0)
        self.assertEqual(storage.qdrant.batch_update_calls, [])

    def test_semantic_mismatch_fails_before_any_write(self):
        identity = _identity()
        records = _records()
        storage = _Storage(identity, records)
        storage.rows["object.eligible"]["text"] = "changed text"

        with self.assertRaisesRegex(RuntimeError, "semantic mismatch"):
            self._run(storage, records)

        self.assertEqual(storage.sql_update_calls, 0)
        self.assertEqual(storage.qdrant.batch_update_calls, [])

    def test_qdrant_point_payload_mismatch_fails_before_any_write(self):
        identity = _identity()
        records = _records()
        storage = _Storage(identity, records, {"object.eligible": {"text": "wrong"}})

        with self.assertRaisesRegex(RuntimeError, "Qdrant payload mismatch"):
            self._run(storage, records)

        self.assertEqual(storage.sql_update_calls, 0)
        self.assertEqual(storage.qdrant.batch_update_calls, [])

    def test_unknown_qdrant_locator_fails_when_sql_is_still_old(self):
        identity = _identity()
        records = _records()
        storage = _Storage(
            identity, records,
            {"object.eligible": {"locator": {"path": "unknown.cc", "start_line": 3, "end_line": 4}}},
        )

        with self.assertRaisesRegex(RuntimeError, "Qdrant locator mismatch"):
            self._run(storage, records)

        self.assertEqual(storage.sql_update_calls, 0)
        self.assertEqual(storage.qdrant.batch_update_calls, [])
