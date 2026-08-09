from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, patch

from panda_agent import kb_bundle


class _Response:
    def __init__(self, payload: dict[object, object]) -> None:
        self.payload = payload
        self.raise_for_status = MagicMock()

    def json(self) -> dict[object, object]:
        return self.payload


class _Result:
    def __init__(self, one: object = None, all_rows: list[tuple[object, ...]] | None = None) -> None:
        self.one, self.all_rows = one, all_rows or []

    def fetchone(self) -> object:
        return self.one

    def fetchall(self) -> list[tuple[object, ...]]:
        return self.all_rows


class _CandidateConnection:
    def __init__(self, candidates: list[tuple[str, str, str]]) -> None:
        self.candidates, self.sql, self.params = candidates, "", None

    def execute(self, sql: str, params: object = None) -> _Result:
        self.sql, self.params = sql, params
        if "SELECT payload FROM index_identities" in sql:
            return _Result(({"embedding_model": "gemini-embedding-2", "embedding_dimensions": 3072},))
        return _Result(all_rows=self.candidates[:int(params[2])])


class _Storage:
    def __init__(self, candidates: list[tuple[str, str, str]]) -> None:
        self.connection = _CandidateConnection(candidates)
        self.settings = type("Settings", (), {"collection_name": kb_bundle.COLLECTION_NAME})()
        self.qdrant = MagicMock()

    @contextmanager
    def connect(self):
        yield self.connection

    @staticmethod
    def point_id(object_id: str) -> str:
        return f"point:{object_id}"


class KnowledgeBundleContractTests(unittest.TestCase):
    def _samples(self) -> list[kb_bundle.VerificationSample]:
        return [
            kb_bundle.VerificationSample(
                object_id=f"object-{index:03d}", point_id=f"point:object-{index:03d}",
                source_id="source", source_version_id="source@v1",
            )
            for index in range(100)
        ]

    def _manifest(self) -> kb_bundle.BundleManifest:
        return kb_bundle.BundleManifest(
            schema_version=kb_bundle.BUNDLE_SCHEMA_VERSION, created_at=datetime(2026, 8, 9, tzinfo=UTC),
            corpus_source_manifest_sha256="c" * 64,
            postgres=kb_bundle.PostgresState(
                database=kb_bundle.DATABASE_NAME, revision="0004",
                table_counts={name: 1 for name in kb_bundle.SELECTED_TABLES}, index_fingerprint="f" * 64,
            ),
            qdrant=kb_bundle.QdrantState(
                collection=kb_bundle.COLLECTION_NAME, point_count=100, dense_config={"dense": {"size": 3072}},
                sparse_config={"sparse": {}}, payload_indexes={"source_id": {"data_type": "keyword"}}, version="1.15.5",
            ),
            fastembed=kb_bundle.FastEmbedState(
                model="Qdrant/bm25", vector_name="sparse", language="english", fastembed_version="0.7.4",
            ),
            verification_samples=self._samples(),
            postgres_dump=kb_bundle.ArtifactHash(filename="postgres.dump", bytes=1, sha256="a" * 64),
            qdrant_snapshot=kb_bundle.ArtifactHash(filename="qdrant.snapshot", bytes=1, sha256="b" * 64),
        )

    def test_manifest_is_strict_and_persists_exactly_one_hundred_samples(self) -> None:
        manifest = self._manifest()
        self.assertEqual(len(manifest.verification_samples), 100)
        with self.assertRaises(Exception):
            kb_bundle.BundleManifest(schema_version="v1", unexpected=True)
        with self.assertRaises(Exception):
            manifest.model_copy(update={"verification_samples": manifest.verification_samples[:99]}).model_validate(
                manifest.model_dump() | {"verification_samples": manifest.model_dump()["verification_samples"][:99]}
            )

    def test_exact_qdrant_count_uses_exact_count_api_and_status_is_strict_green(self) -> None:
        session = MagicMock()
        session.post.return_value = _Response({"result": {"count": 42}})
        self.assertEqual(kb_bundle.exact_qdrant_count(session, "http://qdrant", "collection"), 42)
        self.assertEqual(session.post.call_args.kwargs["json"], {"exact": True})
        session.get.return_value = _Response({"result": {"status": None}})
        with self.assertRaisesRegex(kb_bundle.BundleError, "green"):
            kb_bundle._qdrant_info(session, "http://qdrant", "collection")

    def test_candidates_use_a_legal_distinct_subquery_for_md5_ordering(self) -> None:
        rows = [(f"object-{index:03d}", "source", "source@v1") for index in range(100)]
        storage = _Storage(rows)
        selected = kb_bundle.deterministic_sample_candidates(storage)
        self.assertEqual(selected, rows)
        sql = " ".join(storage.connection.sql.split())
        self.assertIn(
            "SELECT DISTINCT k.object_id,k.source_id,k.source_version_id,"
            "md5(k.object_id::text) AS sample_order",
            sql,
        )
        self.assertIn("FROM embedding_records e JOIN knowledge_objects k ON k.object_id=e.object_id", sql)
        self.assertIn("e.task_type='RETRIEVAL_DOCUMENT'", sql)
        self.assertIn("ORDER BY sample_order, object_id LIMIT %s", sql)
        self.assertNotIn(
            "SELECT DISTINCT k.object_id,k.source_id,k.source_version_id FROM embedding_records "
            "e JOIN knowledge_objects k ON k.object_id=e.object_id WHERE",
            sql,
        )

    def test_sample_selection_requires_payload_identity_and_with_payload(self) -> None:
        rows = [(f"object-{index:03d}", "source", "source@v1") for index in range(100)]
        storage = _Storage(rows)
        storage.qdrant.retrieve.return_value = [
            type("Point", (), {"id": "point:object-000", "payload": {"object_id": "wrong", "source_id": "source", "source_version_id": "source@v1"}})()
        ]
        with self.assertRaisesRegex(kb_bundle.BundleError, "payload identity"):
            kb_bundle.select_verification_samples(storage)
        self.assertTrue(storage.qdrant.retrieve.call_args.kwargs["with_payload"])

    def test_sample_selection_replaces_a_missing_early_point_from_stable_candidate_pool(self) -> None:
        rows = [(f"object-{index:03d}", "source", "source@v1") for index in range(101)]
        storage = _Storage(rows)

        def retrieve(*, ids: list[str], **_: object) -> list[object]:
            return [
                type("Point", (), {
                    "id": point_id,
                    "payload": {
                        "object_id": point_id.removeprefix("point:"),
                        "source_id": "source",
                        "source_version_id": "source@v1",
                    },
                })()
                for point_id in ids if point_id != "point:object-000"
            ]

        storage.qdrant.retrieve.side_effect = retrieve
        selected = kb_bundle.select_verification_samples(storage)
        self.assertEqual([sample.object_id for sample in selected], [row[0] for row in rows[1:]])
        self.assertEqual(storage.connection.params[2], kb_bundle.SAMPLE_CANDIDATE_POOL_SIZE)

    def test_sample_selection_fails_closed_when_candidate_pool_confirms_fewer_than_one_hundred(self) -> None:
        rows = [(f"object-{index:03d}", "source", "source@v1") for index in range(101)]
        storage = _Storage(rows)

        def retrieve(*, ids: list[str], **_: object) -> list[object]:
            return [
                type("Point", (), {
                    "id": point_id,
                    "payload": {
                        "object_id": point_id.removeprefix("point:"),
                        "source_id": "source",
                        "source_version_id": "source@v1",
                    },
                })()
                for point_id in ids if point_id not in {"point:object-000", "point:object-001"}
            ]

        storage.qdrant.retrieve.side_effect = retrieve
        with self.assertRaisesRegex(kb_bundle.BundleError, "confirmed 99 of 100"):
            kb_bundle.select_verification_samples(storage)

    def test_restore_hash_preflight_precedes_storage_or_mutation(self) -> None:
        with TemporaryDirectory() as directory:
            bundle = Path(directory)
            (bundle / kb_bundle.MANIFEST_NAME).write_text("{}", encoding="utf-8")
            with patch.object(kb_bundle, "Storage") as storage:
                with self.assertRaises(kb_bundle.BundleError):
                    kb_bundle.restore_bundle(bundle, project_root=bundle)
            storage.assert_not_called()

    def test_verify_uses_manifest_samples_not_excluded_embedding_records(self) -> None:
        manifest = self._manifest()
        storage = MagicMock()
        storage.settings = MagicMock(qdrant_url="http://qdrant", collection_name=kb_bundle.COLLECTION_NAME)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(kb_bundle, "preflight_bundle", return_value=manifest),
                patch.object(kb_bundle, "Storage", return_value=storage),
                patch.object(kb_bundle, "postgres_state", return_value=manifest.postgres),
                patch.object(kb_bundle, "qdrant_state", return_value=manifest.qdrant),
                patch.object(kb_bundle, "fastembed_state", return_value=manifest.fastembed),
                patch.object(kb_bundle, "_verify_runtime", return_value=True),
                patch.object(kb_bundle, "_verify_sample", return_value=True) as verify_sample,
                patch.object(kb_bundle, "deterministic_sample_candidates", side_effect=AssertionError("must not read embedding records")),
            ):
                result = kb_bundle.verify_bundle(root, project_root=root)
        self.assertTrue(result["valid"])
        self.assertEqual(verify_sample.call_count, 100)

    def test_wrong_persisted_sample_identity_fails_verify(self) -> None:
        manifest = self._manifest()
        storage = MagicMock()
        storage.settings = MagicMock(qdrant_url="http://qdrant", collection_name=kb_bundle.COLLECTION_NAME)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(kb_bundle, "preflight_bundle", return_value=manifest),
                patch.object(kb_bundle, "Storage", return_value=storage),
                patch.object(kb_bundle, "postgres_state", return_value=manifest.postgres),
                patch.object(kb_bundle, "qdrant_state", return_value=manifest.qdrant),
                patch.object(kb_bundle, "fastembed_state", return_value=manifest.fastembed),
                patch.object(kb_bundle, "_verify_runtime", return_value=True),
                patch.object(kb_bundle, "_verify_sample", side_effect=[False] + [True] * 99),
            ):
                self.assertFalse(kb_bundle.verify_bundle(root, project_root=root)["valid"])

    def test_runtime_install_destination_and_local_only_functional_probe(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = root / "bundle"
            source = bundle / kb_bundle.RUNTIME_BM25_PATH
            source.mkdir(parents=True)
            (source / "model.onnx").write_bytes(b"model")
            installed = kb_bundle._install_runtime_from_bundle(bundle, root)
            self.assertEqual(installed, root / kb_bundle.INSTALLED_RUNTIME_PATH)
            vector = type("Vector", (), {"values": [1.0]})()
            with patch.object(kb_bundle, "SparseTextEmbedding") as embedding:
                embedding.return_value.query_embed.return_value = iter([vector])
                self.assertTrue(kb_bundle._verify_runtime(root))
            self.assertEqual(embedding.call_args.kwargs["specific_model_path"], str(installed))
            self.assertTrue(embedding.call_args.kwargs["local_files_only"])
            self.assertEqual(embedding.call_args.kwargs["language"], "english")

    def test_pg_restore_has_exit_on_error_and_single_transaction(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / kb_bundle.POSTGRES_DUMP_NAME).write_bytes(b"dump")
            calls: list[list[str]] = []

            def runner(command: list[str], **_: object) -> None:
                calls.append(command)

            kb_bundle._restore_postgres(root, root, runner)
        self.assertIn("--exit-on-error", calls[0])
        self.assertIn("--single-transaction", calls[0])

    def test_export_preflight_requires_valid_index_before_dump(self) -> None:
        storage = MagicMock()
        with patch.object(kb_bundle, "verify_index", return_value={"valid": False}):
            with self.assertRaisesRegex(kb_bundle.BundleError, "index verification"):
                kb_bundle._export_preflight(Path("."), storage)

    def test_postgres_state_model_requires_all_selected_table_counts(self) -> None:
        with self.assertRaises(ValueError):
            kb_bundle.PostgresState(
                database=kb_bundle.DATABASE_NAME, revision="0004", table_counts={}, index_fingerprint="x"
            )


if __name__ == "__main__":
    unittest.main()
