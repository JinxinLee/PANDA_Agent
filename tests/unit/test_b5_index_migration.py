from __future__ import annotations

import hashlib
import json
import unittest
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import mock

from panda_agent.indexing import (
    _b5_filter_resume_selected,
    _b5_point_payload_matches_current,
    _b5_validate_reuse_locators,
    apply_b5_selective_index,
    plan_b5_reindex_impact_from_records,
)


def _object(object_id: str, text: str, *, eligible: bool = True) -> dict[str, object]:
    return {
        "object_id": object_id, "object_type": "function", "title": object_id,
        "text": text, "token_count": 12 if eligible else 2,
        "embedding_eligible": eligible,
    }


def _before(item: dict[str, object], *, point: bool = True, receipt: bool = True) -> dict[str, object]:
    dense = f"{item['title']}\n{item['text']}".encode("utf-8")
    return {
        "object_id": item["object_id"],
        "effective_embedding_eligibility": item["embedding_eligible"],
        "embedding_input_sha256": hashlib.sha256(dense).hexdigest(),
        "text_sha256": hashlib.sha256(str(item["text"]).encode()).hexdigest(),
        "deterministic_point_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"panda-qa:{item['object_id']}")),
        "qdrant_point_exists": point,
        "embedding_receipt_exists": receipt,
    }


def _full_object(object_id: str, text: str, **overrides: object) -> dict[str, object]:
    value = _object(object_id, text)
    value.update(
        {
            "source_id": "repo",
            "source_version_id": "repo@sha",
            "authority_level": "primary",
            "locator": {"path": "a.cc", "start_line": 1, "end_line": 1},
            "metadata": {},
            "canonical_locator": f"a.cc:{object_id}:1",
        }
    )
    value.update(overrides)
    return value


def _embedding_cache_key(identity: object, item: dict[str, object]) -> str:
    text = f"{item['title']}\n{item['text']}"
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    return hashlib.sha256(
        f"{identity.embedding_model}\x1fRETRIEVAL_DOCUMENT\x1f{text_hash}".encode()
    ).hexdigest()


def _point_id_storage() -> SimpleNamespace:
    return SimpleNamespace(point_id=_FakeStorage.point_id)


class B5ImpactPlanTests(unittest.TestCase):
    def test_unchanged_point_is_reused_without_receipt(self) -> None:
        item = _object("same", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([_before(item, receipt=False)], [item])
        self.assertEqual(result["categories"]["unchanged_eligible_reuse"], 1)
        self.assertEqual(result["vectors"]["dense_documents"], 0)
        self.assertEqual(result["vectors"]["receipt_missing_unchanged_reused"], 1)

    def test_changed_and_new_objects_are_selected_once(self) -> None:
        old = _object("changed", "one two three four five six seven eight nine ten eleven twelve")
        changed = _object("changed", "one two three four five six seven eight nine ten eleven updated")
        new = _object("new", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([_before(old)], [changed, new], batch_size=1)
        self.assertEqual(result["vectors"]["reembed_object_ids"], ["changed", "new"])
        self.assertEqual(result["vectors"]["batches"], 2)

    def test_eligibility_loss_marks_existing_point_stale(self) -> None:
        old = _object("lost", "one two three four five six seven eight nine ten eleven twelve")
        lost = _object("lost", "tiny", eligible=False)
        result = plan_b5_reindex_impact_from_records([_before(old)], [lost])
        self.assertEqual(result["categories"]["eligibility_lost_remove"], 1)
        self.assertEqual(result["categories"]["stale_live_points_remove"], 1)

    def test_duplicate_ids_are_rejected(self) -> None:
        item = _object("duplicate", "one two three four five six seven eight nine ten eleven twelve")
        with self.assertRaises(ValueError):
            plan_b5_reindex_impact_from_records([], [item, item])

    def test_new_object_is_an_sql_insert(self) -> None:
        item = _object("new", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([], [item])
        self.assertEqual(result["sql"]["insert_object_ids"], ["new"])

    def test_removed_object_is_an_sql_delete(self) -> None:
        item = _object("removed", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([_before(item)], [])
        self.assertEqual(result["sql"]["delete_object_ids"], ["removed"])

    def test_no_live_point_is_not_counted_as_reusable(self) -> None:
        item = _object("unwritten", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([_before(item, point=False)], [item])
        self.assertEqual(result["categories"]["changed_eligible_reembed"], 1)

    def test_sparse_and_dense_document_counts_match(self) -> None:
        item = _object("new", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([], [item])
        self.assertEqual(result["vectors"]["dense_documents"], result["vectors"]["sparse_documents"])

    def test_planner_never_calls_a_model(self) -> None:
        result = plan_b5_reindex_impact_from_records([], [])
        self.assertEqual(result["model_calls"], 0)

    def test_reuse_locator_disagreement_is_rejected(self) -> None:
        snapshot_item = _before(_object("same", "one two three four five six seven eight nine ten eleven twelve"))
        snapshot_item["locator"] = {"path": "a.cc", "start_line": 1, "end_line": 9}
        corpus_item = _object("same", "one two three four five six seven eight nine ten eleven twelve")
        corpus_item["locator"] = {"path": "a.cc", "start_line": 1, "end_line": 10}
        with self.assertRaises(RuntimeError):
            _b5_validate_reuse_locators([snapshot_item], [corpus_item], ["same"])


class B5ResumeSafetyTests(unittest.TestCase):
    def _payload(self, item: dict[str, object], **overrides: object) -> dict[str, object]:
        payload = {
            "object_id": item["object_id"],
            "source_id": item["source_id"],
            "source_version_id": item["source_version_id"],
            "object_type": item["object_type"],
            "title": item["title"],
            "text": item["text"],
            "locator": item["locator"],
        }
        payload.update(overrides)
        return payload

    def test_old_point_with_compatible_cache_is_not_skipped(self) -> None:
        item = _full_object("sel", "current text one two three four five six seven eight nine ten")
        identity = SimpleNamespace(embedding_model="gemini-embedding-2")
        key = _embedding_cache_key(identity, item)
        point_id = _FakeStorage.point_id(item["object_id"])
        point = SimpleNamespace(id=point_id, payload=self._payload(item, text="old b4 text"))
        kept, skipped = _b5_filter_resume_selected(
            [item], [key], {key: item["object_id"]}, {point_id: point}, _point_id_storage()
        )
        self.assertEqual(skipped, 0)
        self.assertEqual(kept, [item])

    def test_current_payload_with_same_object_receipt_may_be_skipped(self) -> None:
        item = _full_object("sel", "current text one two three four five six seven eight nine ten")
        identity = SimpleNamespace(embedding_model="gemini-embedding-2")
        key = _embedding_cache_key(identity, item)
        point_id = _FakeStorage.point_id(item["object_id"])
        point = SimpleNamespace(id=point_id, payload=self._payload(item))
        kept, skipped = _b5_filter_resume_selected(
            [item], [key], {key: item["object_id"]}, {point_id: point}, _point_id_storage()
        )
        self.assertEqual(skipped, 1)
        self.assertEqual(kept, [])

    def test_other_object_receipt_with_stale_payload_is_not_skipped(self) -> None:
        item = _full_object("sel", "current text one two three four five six seven eight nine ten")
        identity = SimpleNamespace(embedding_model="gemini-embedding-2")
        key = _embedding_cache_key(identity, item)
        point_id = _FakeStorage.point_id(item["object_id"])
        point = SimpleNamespace(id=point_id, payload=self._payload(item, text="old b4 text"))
        kept, skipped = _b5_filter_resume_selected(
            [item], [key], {key: "other-object"}, {point_id: point}, _point_id_storage()
        )
        self.assertEqual(skipped, 0)
        self.assertEqual(kept, [item])

    def test_missing_receipt_with_current_payload_reembeds(self) -> None:
        item = _full_object("sel", "current text one two three four five six seven eight nine ten")
        identity = SimpleNamespace(embedding_model="gemini-embedding-2")
        key = _embedding_cache_key(identity, item)
        point_id = _FakeStorage.point_id(item["object_id"])
        point = SimpleNamespace(id=point_id, payload=self._payload(item))
        kept, skipped = _b5_filter_resume_selected(
            [item], [key], {}, {point_id: point}, _point_id_storage()
        )
        self.assertEqual(skipped, 0)
        self.assertEqual(kept, [item])

    def test_unchanged_reuse_never_requires_cache_receipts(self) -> None:
        item = _full_object("same", "one two three four five six seven eight nine ten eleven twelve")
        snapshot = _before(item, receipt=False)
        result = plan_b5_reindex_impact_from_records([snapshot], [item])
        self.assertEqual(result["categories"]["unchanged_eligible_reuse"], 1)
        self.assertNotIn(item["object_id"], result["vectors"]["reembed_object_ids"])
        self.assertEqual(result["vectors"]["dense_documents"], 0)
        self.assertEqual(result["vectors"]["receipt_missing_unchanged_reused"], 1)

    def test_payload_matcher_requires_all_resume_fields(self) -> None:
        item = _full_object("sel", "current text one two three four five six seven eight nine ten")
        point = SimpleNamespace(id=_FakeStorage.point_id(item["object_id"]), payload=self._payload(item, locator={"path": "other"}))
        self.assertFalse(_b5_point_payload_matches_current(item, point))


class _FakeList(list):
    def tolist(self):
        return list(self)


class _FakeSparseVector(SimpleNamespace):
    def __init__(self):
        super().__init__(indices=_FakeList([0]), values=_FakeList([1.0]))


class _FakeSparseModel:
    def __init__(self) -> None:
        self.embedded_texts: list[str] = []

    def embed(self, texts):
        self.embedded_texts.extend(texts)
        return [_FakeSparseVector() for _ in texts]


class _FakeVertex:
    def __init__(self, settings) -> None:
        self.settings = settings
        self.embedded_texts: list[str] = []

    def embed_documents(self, texts):
        self.embedded_texts.extend(texts)
        return [[0.5] * 3072 for _ in texts]


class _FakeCopy:
    def __init__(self, sink) -> None:
        self._sink = sink

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def write_row(self, row):
        self._sink.add(row[0])


class _FakeCursor:
    def __init__(self, storage) -> None:
        self._storage = storage

    def executemany(self, sql, rows):
        for row in rows:
            if "INSERT INTO knowledge_objects" in sql:
                self._storage.object_ids.add(row[0])
            elif "INSERT INTO embedding_records" in sql:
                self._storage.cache_keys.add(row[0])
                self._storage.cache_owners[row[0]] = row[1]

    def copy(self, _statement):
        return _FakeCopy(self._storage.pending_valid_ids)


class _EmptyRows:
    def fetchone(self):
        return None

    def fetchall(self):
        return []


class _Rows:
    def __init__(self, rows) -> None:
        self._rows = list(rows)

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows


class _FakeConnection:
    def __init__(self, storage) -> None:
        self._storage = storage

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def cursor(self):
        return _FakeCursor(self._storage)

    def execute(self, sql, params=None):
        if "SELECT fingerprint,payload FROM index_identities" in sql:
            return _SingleRow(self._storage.index_identity_row())
        if "SELECT count(1) FROM knowledge_objects" in sql:
            return _SingleRow(self._storage.sql_objects)
        if "SELECT count(1) FROM relation_edges" in sql:
            return _SingleRow(self._storage.relation_count)
        if "SELECT cache_key, object_id FROM embedding_records" in sql:
            return _Rows(self._storage.cache_owners.items())
        if "INSERT INTO embedding_records" in sql:
            self._storage.cache_keys.add(params[0])
            self._storage.cache_owners[params[0]] = params[1]
        if "INSERT INTO ingestion_runs" in sql:
            self._storage.log.append(("sql", "insert_ingestion_run"))
            return _SingleRow(99)
        if "UPDATE ingestion_runs" in sql:
            self._storage.log.append(("sql", "update_ingestion_run"))
        return None


class _SingleRow:
    def __init__(self, value) -> None:
        self._value = value

    def fetchone(self):
        if isinstance(self._value, tuple):
            return self._value
        return (self._value,)

    def fetchall(self):
        if isinstance(self._value, tuple):
            return [self._value]
        return [(self._value,)]


class _FakeQdrant:
    def __init__(self, initial_point_ids, payloads=None) -> None:
        self.point_ids = set(initial_point_ids)
        self.payloads = dict(payloads or {})
        self.count_value = len(initial_point_ids)
        self.log: list[tuple] = []

    def count(self, _collection, exact=True):
        return SimpleNamespace(count=self.count_value)

    def get_collection(self, _collection):
        dense = SimpleNamespace(size=3072)
        modifier = SimpleNamespace(value="idf")
        sparse = SimpleNamespace(modifier=modifier)
        return SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(
            vectors={"dense": dense}, sparse_vectors={"sparse": sparse})))

    def retrieve(self, collection_name=None, ids=None, with_payload=False, with_vectors=False):
        return [
            SimpleNamespace(id=point_id, payload=self.payloads.get(point_id))
            for point_id in ids
            if point_id in self.point_ids
        ]

    def upsert(self, collection_name=None, points=None, wait=True):
        new_ids = [str(point.id) for point in points if str(point.id) not in self.point_ids]
        for point in points:
            self.point_ids.add(str(point.id))
            self.payloads[str(point.id)] = point.payload
        self.count_value += len(new_ids)
        self.log.append(("upsert", [str(point.id) for point in points]))

    def delete(self, collection_name=None, points_selector=None, wait=True):
        ids = list(points_selector.points)
        removed = [point_id for point_id in ids if point_id in self.point_ids]
        self.point_ids.difference_update(ids)
        for point_id in ids:
            self.payloads.pop(point_id, None)
        self.count_value -= len(removed)
        self.log.append(("delete", ids))


class _FakeStorage:
    def __init__(self, identity, qdrant) -> None:
        self.settings = SimpleNamespace(collection_name="panda_knowledge_v1")
        self.qdrant = qdrant
        self._identity = identity
        self.sql_objects = 3
        self.relation_count = 64561
        self.object_ids = set()
        self.cache_keys = set()
        self.cache_owners: dict[str, str] = {}
        self.pending_valid_ids = set()
        self.log: list[tuple] = []

    def connect(self):
        return _FakeConnection(self)

    @staticmethod
    def point_id(object_id):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"panda-qa:{object_id}"))

    def _verify_qdrant_sparse_config(self, receipt):
        return self.qdrant.get_collection(self.settings.collection_name)

    def index_identity_row(self):
        return (self._identity.fingerprint(), self._identity.model_dump(mode="json"))

    def upsert_objects(self, records):
        for item in records:
            self.object_ids.add(item["object_id"])
        self.sql_objects = len(self.object_ids)
        self.log.append(("sql", "upsert_objects"))

    def upsert_aliases(self, records):
        list(records)

    def upsert_relations(self, records):
        list(records)

    def upsert_relation_candidates(self, records):
        list(records)

    def upsert_workflows(self, records):
        list(records)

    def upsert_source_versions(self, manifest):
        self.log.append(("sql", "upsert_source_versions"))

    def prune_table(self, table, key, valid_ids):
        if table != "knowledge_objects":
            return 0
        before = len(self.object_ids)
        self.object_ids.intersection_update(valid_ids)
        self.sql_objects = len(self.object_ids)
        return before - len(self.object_ids)


class B5MockedApplyTests(unittest.TestCase):
    def _apply_mocked(self):
        from dotenv import load_dotenv
        load_dotenv()
        from panda_agent.indexing import (
            B5_EXPECTED_B4_QDRANT_POINTS,
            B5_EXPECTED_B4_SQL_OBJECTS,
            IndexIdentity,
            VertexSettings,
        )
        from panda_agent.sparse import sparse_receipt, sparse_settings

        real_root = Path(__file__).resolve().parents[2]
        real_settings = sparse_settings(real_root)
        real_receipt = sparse_receipt(real_settings)

        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            normalized = root / "data" / "normalized" / "hash01"
            normalized.mkdir(parents=True)
            (root / "data" / "manifests").mkdir(parents=True)
            (root / "data" / "tmp" / "b5").mkdir(parents=True)
            (root / "data" / "manifests" / "source_manifest.json").write_text("{}", encoding="utf-8")

            identity = IndexIdentity.from_settings(VertexSettings.from_env(), real_root)
            point_id = _FakeStorage.point_id
            reuse_text = "one two three four five six seven eight nine ten eleven twelve"
            changed_old_text = "old text words one two three four five six seven eight nine ten"
            changed_new_text = "new text words one two three four five six seven eight nine ten"
            locator = {"path": "a.cc", "start_line": 1, "end_line": 1}

            snapshot = [
                {
                    "object_id": "obj.reuse",
                    "object_type": "function",
                    "title": "reuse",
                    "text": reuse_text,
                    "effective_embedding_eligibility": True,
                    "embedding_input_sha256": hashlib.sha256(f"reuse\n{reuse_text}".encode()).hexdigest(),
                    "text_sha256": hashlib.sha256(reuse_text.encode()).hexdigest(),
                    "locator": locator,
                    "deterministic_point_id": point_id("obj.reuse"),
                    "qdrant_point_exists": True,
                    "embedding_receipt_exists": False,
                },
                {
                    "object_id": "obj.changed",
                    "object_type": "function",
                    "title": "changed",
                    "text": changed_old_text,
                    "effective_embedding_eligibility": True,
                    "embedding_input_sha256": hashlib.sha256(f"changed\n{changed_old_text}".encode()).hexdigest(),
                    "text_sha256": hashlib.sha256(changed_old_text.encode()).hexdigest(),
                    "locator": locator,
                    "deterministic_point_id": point_id("obj.changed"),
                    "qdrant_point_exists": True,
                    "embedding_receipt_exists": True,
                },
                {
                    "object_id": "obj.stale",
                    "object_type": "function",
                    "title": "stale",
                    "text": "stale text words one two three four five six seven eight nine ten",
                    "effective_embedding_eligibility": True,
                    "embedding_input_sha256": hashlib.sha256("stale\nstale text words one two three four five six seven eight nine ten".encode()).hexdigest(),
                    "text_sha256": hashlib.sha256("stale text words one two three four five six seven eight nine ten".encode()).hexdigest(),
                    "locator": locator,
                    "deterministic_point_id": point_id("obj.stale"),
                    "qdrant_point_exists": True,
                    "embedding_receipt_exists": True,
                },
            ]
            objects = [
                {
                    "object_id": "obj.reuse",
                    "object_type": "function",
                    "source_id": "repo",
                    "source_version_id": "repo@sha",
                    "title": "reuse",
                    "text": reuse_text,
                    "authority_level": "primary",
                    "locator": locator,
                    "metadata": {},
                    "canonical_locator": "a.cc:reuse:1",
                    "token_count": 12,
                    "embedding_eligible": True,
                },
                {
                    "object_id": "obj.changed",
                    "object_type": "function",
                    "source_id": "repo",
                    "source_version_id": "repo@sha",
                    "title": "changed",
                    "text": changed_new_text,
                    "authority_level": "primary",
                    "locator": locator,
                    "metadata": {},
                    "canonical_locator": "a.cc:changed:2",
                    "token_count": 12,
                    "embedding_eligible": True,
                },
            ]
            with open(normalized / "knowledge_objects.jsonl", "w", encoding="utf-8") as stream:
                for item in objects:
                    stream.write(json.dumps(item) + "\n")
            with open(root / "data" / "tmp" / "b5" / "b4_point_snapshot.jsonl", "w", encoding="utf-8") as stream:
                for item in snapshot:
                    stream.write(json.dumps(item) + "\n")
            for name in ("relation_edges.jsonl", "relation_candidates.jsonl", "knowledge_aliases.jsonl", "workflow_steps.jsonl"):
                (normalized / name).write_text("", encoding="utf-8")
            (normalized / "ingestion_report.json").write_text(json.dumps({
                "manifest_hash": "hash01", "object_count": 2, "relation_count": 64561,
                "relation_candidate_count": 0, "alias_count": 0, "workflow_count": 0,
                "parse_errors": [], "output_hashes": {},
            }), encoding="utf-8")

            qdrant = _FakeQdrant({point_id("obj.reuse"), point_id("obj.changed"), point_id("obj.stale")})
            storage = _FakeStorage(identity, qdrant)
            vertex = _FakeVertex(None)
            sparse_model = _FakeSparseModel()

            def vertex_factory(settings):
                vertex.settings = settings
                return vertex

            with mock.patch("panda_agent.indexing.Storage", return_value=storage), \
                    mock.patch("panda_agent.indexing.VertexAIClient", vertex_factory), \
                    mock.patch("panda_agent.indexing.sparse_settings", return_value=real_settings), \
                    mock.patch("panda_agent.indexing.sparse_receipt", return_value=real_receipt), \
                    mock.patch("panda_agent.indexing.create_sparse_encoder", return_value=(sparse_model, real_receipt)), \
                    mock.patch("panda_agent.indexing.B5_EXPECTED_B4_SQL_OBJECTS", 3), \
                    mock.patch("panda_agent.indexing.B5_EXPECTED_B4_QDRANT_POINTS", 3):
                result = apply_b5_selective_index(root, run=True)
            return result, storage, qdrant, vertex, sparse_model, changed_new_text

    def _build_single_changed_env(self):
        from dotenv import load_dotenv
        load_dotenv()
        from panda_agent.indexing import IndexIdentity, VertexSettings
        from panda_agent.sparse import sparse_receipt, sparse_settings

        real_root = Path(__file__).resolve().parents[2]
        real_settings = sparse_settings(real_root)
        real_receipt = sparse_receipt(real_settings)
        tmp = TemporaryDirectory()
        root = Path(tmp.name)
        normalized = root / "data" / "normalized" / "hash01"
        normalized.mkdir(parents=True)
        (root / "data" / "manifests").mkdir(parents=True)
        (root / "data" / "tmp" / "b5").mkdir(parents=True)
        (root / "data" / "manifests" / "source_manifest.json").write_text("{}", encoding="utf-8")

        identity = IndexIdentity.from_settings(VertexSettings.from_env(), real_root)
        point_id = _FakeStorage.point_id
        old_text = "old text words one two three four five six seven eight nine ten"
        new_text = "new text words one two three four five six seven eight nine ten"
        locator = {"path": "a.cc", "start_line": 1, "end_line": 1}
        snapshot = [{
            "object_id": "obj.changed",
            "object_type": "function",
            "title": "changed",
            "text": old_text,
            "effective_embedding_eligibility": True,
            "embedding_input_sha256": hashlib.sha256(f"changed\n{old_text}".encode()).hexdigest(),
            "text_sha256": hashlib.sha256(old_text.encode()).hexdigest(),
            "locator": locator,
            "deterministic_point_id": point_id("obj.changed"),
            "qdrant_point_exists": True,
            "embedding_receipt_exists": True,
        }]
        objects = [{
            "object_id": "obj.changed",
            "object_type": "function",
            "source_id": "repo",
            "source_version_id": "repo@sha",
            "title": "changed",
            "text": new_text,
            "authority_level": "primary",
            "locator": locator,
            "metadata": {},
            "canonical_locator": "a.cc:changed:2",
            "token_count": 12,
            "embedding_eligible": True,
        }]
        with open(normalized / "knowledge_objects.jsonl", "w", encoding="utf-8") as stream:
            for item in objects:
                stream.write(json.dumps(item) + "\n")
        with open(root / "data" / "tmp" / "b5" / "b4_point_snapshot.jsonl", "w", encoding="utf-8") as stream:
            for item in snapshot:
                stream.write(json.dumps(item) + "\n")
        for name in ("relation_edges.jsonl", "relation_candidates.jsonl", "knowledge_aliases.jsonl", "workflow_steps.jsonl"):
            (normalized / name).write_text("", encoding="utf-8")
        (normalized / "ingestion_report.json").write_text(json.dumps({
            "manifest_hash": "hash01", "object_count": 1, "relation_count": 0,
            "relation_candidate_count": 0, "alias_count": 0, "workflow_count": 0,
            "parse_errors": [], "output_hashes": {},
        }), encoding="utf-8")

        qdrant = _FakeQdrant({point_id("obj.changed")})
        storage = _FakeStorage(identity, qdrant)
        storage.sql_objects = 1
        storage.relation_count = 0
        return tmp, root, storage, qdrant, identity, real_settings, real_receipt, new_text

    def test_vertex_constructor_failure_happens_before_live_mutation(self) -> None:
        tmp, root, storage, qdrant, identity, real_settings, real_receipt, _ = self._build_single_changed_env()
        try:
            with mock.patch("panda_agent.indexing.Storage", return_value=storage), \
                    mock.patch("panda_agent.indexing.VertexAIClient", side_effect=RuntimeError("vertex config failed")), \
                    mock.patch("panda_agent.indexing.sparse_settings", return_value=real_settings), \
                    mock.patch("panda_agent.indexing.sparse_receipt", return_value=real_receipt), \
                    mock.patch("panda_agent.indexing.create_sparse_encoder", return_value=(_FakeSparseModel(), real_receipt)), \
                    mock.patch("panda_agent.indexing.B5_EXPECTED_B4_SQL_OBJECTS", 1), \
                    mock.patch("panda_agent.indexing.B5_EXPECTED_B4_QDRANT_POINTS", 1):
                with self.assertRaises(RuntimeError):
                    apply_b5_selective_index(root, run=True)
            self.assertEqual(
                [entry for entry in storage.log if entry[0] != "update_ingestion_run"],
                [],
            )
            self.assertEqual(qdrant.log, [])
            self.assertEqual(storage.sql_objects, 1)
        finally:
            tmp.cleanup()

    def test_sparse_constructor_failure_happens_before_live_mutation(self) -> None:
        tmp, root, storage, qdrant, identity, real_settings, real_receipt, _ = self._build_single_changed_env()
        try:
            with mock.patch("panda_agent.indexing.Storage", return_value=storage), \
                    mock.patch("panda_agent.indexing.VertexAIClient", return_value=_FakeVertex(None)), \
                    mock.patch("panda_agent.indexing.sparse_settings", return_value=real_settings), \
                    mock.patch("panda_agent.indexing.sparse_receipt", return_value=real_receipt), \
                    mock.patch("panda_agent.indexing.create_sparse_encoder", side_effect=RuntimeError("sparse constructor failed")), \
                    mock.patch("panda_agent.indexing.B5_EXPECTED_B4_SQL_OBJECTS", 1), \
                    mock.patch("panda_agent.indexing.B5_EXPECTED_B4_QDRANT_POINTS", 1):
                with self.assertRaises(RuntimeError):
                    apply_b5_selective_index(root, run=True)
            self.assertEqual(
                [entry for entry in storage.log if entry[0] != "update_ingestion_run"],
                [],
            )
            self.assertEqual(qdrant.log, [])
            self.assertEqual(storage.sql_objects, 1)
        finally:
            tmp.cleanup()

    def test_sparse_receipt_mismatch_happens_before_live_mutation(self) -> None:
        tmp, root, storage, qdrant, identity, real_settings, real_receipt, _ = self._build_single_changed_env()
        try:
            with mock.patch("panda_agent.indexing.Storage", return_value=storage), \
                    mock.patch("panda_agent.indexing.VertexAIClient", return_value=_FakeVertex(None)), \
                    mock.patch("panda_agent.indexing.sparse_settings", return_value=real_settings), \
                    mock.patch("panda_agent.indexing.sparse_receipt", return_value=real_receipt), \
                    mock.patch("panda_agent.indexing.create_sparse_encoder", return_value=(_FakeSparseModel(), SimpleNamespace())), \
                    mock.patch("panda_agent.indexing.B5_EXPECTED_B4_SQL_OBJECTS", 1), \
                    mock.patch("panda_agent.indexing.B5_EXPECTED_B4_QDRANT_POINTS", 1):
                with self.assertRaises(RuntimeError):
                    apply_b5_selective_index(root, run=True)
            self.assertEqual(
                [entry for entry in storage.log if entry[0] != "update_ingestion_run"],
                [],
            )
            self.assertEqual(qdrant.log, [])
            self.assertEqual(storage.sql_objects, 1)
        finally:
            tmp.cleanup()

    def test_mocked_run_true_apply_orchestration(self) -> None:
        result, storage, qdrant, vertex, sparse_model, changed_new_text = self._apply_mocked()

        self.assertFalse(result["dry_run"])
        self.assertEqual(result["dense_vectors_written"], 1)
        self.assertEqual(result["sparse_vectors_written"], 1)
        self.assertEqual(result["unchanged_vectors_reused"], 1)
        self.assertEqual(result["stale_vectors_deleted"], 1)
        self.assertFalse(result["collection_recreated"])

        self.assertIsNotNone(vertex.settings)
        self.assertEqual(vertex.settings.embedding_model, "gemini-embedding-2")
        self.assertEqual(vertex.embedded_texts, [f"changed\n{changed_new_text}"])
        self.assertEqual(sparse_model.embedded_texts, [f"changed\n{changed_new_text}"])

        upserts = [entry for entry in qdrant.log if entry[0] == "upsert"]
        deletes = [entry for entry in qdrant.log if entry[0] == "delete"]
        changed_point = _FakeStorage.point_id("obj.changed")
        stale_point = _FakeStorage.point_id("obj.stale")
        reuse_point = _FakeStorage.point_id("obj.reuse")
        self.assertEqual(upserts, [("upsert", [changed_point])])
        self.assertEqual(deletes, [("delete", [stale_point])])
        self.assertLess(qdrant.log.index(("upsert", [changed_point])), qdrant.log.index(("delete", [stale_point])))
        self.assertNotIn(reuse_point, [point_id for _, ids in upserts for point_id in ids])
        self.assertIn(reuse_point, qdrant.point_ids)
        self.assertNotIn(stale_point, qdrant.point_ids)
        self.assertEqual(qdrant.count_value, 2)
        self.assertEqual(storage.sql_objects, 2)
