from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, patch

from panda_agent import kb_bundle


class _Storage:
    def __init__(self) -> None:
        self.settings = type("Settings", (), {
            "qdrant_url": "http://qdrant", "collection_name": kb_bundle.COLLECTION_NAME,
        })()
        self.qdrant = MagicMock()

    @contextmanager
    def connect(self):
        yield MagicMock()


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


class _CandidateStorage:
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
    def _manifest(self) -> kb_bundle.BundleManifest:
        samples = [
            kb_bundle.VerificationSample(
                object_id=f"object-{index:03d}", point_id=f"point-{index:03d}",
                source_id="source", source_version_id="source@v1",
            )
            for index in range(kb_bundle.SAMPLE_SIZE)
        ]
        return kb_bundle.BundleManifest(
            schema_version=kb_bundle.BUNDLE_SCHEMA_VERSION,
            created_at=datetime(2026, 8, 10, tzinfo=UTC),
            corpus_source_manifest_sha256="c" * 64,
            postgres=kb_bundle.PostgresState(
                database=kb_bundle.DATABASE_NAME,
                revision=kb_bundle.KNOWLEDGE_REVISION,
                table_counts={name: 1 for name in kb_bundle.SELECTED_TABLES},
                index_fingerprint="f" * 64,
            ),
            qdrant=kb_bundle.QdrantState(
                collection=kb_bundle.COLLECTION_NAME,
                point_count=100,
                dense_config={"dense": {"size": 3072}},
                sparse_config={"sparse": {}},
                payload_indexes={"source_id": {"data_type": "keyword"}},
            ),
            fastembed=kb_bundle.FastEmbedState(
                model="Qdrant/bm25", vector_name="sparse", language="english", fastembed_version="0.7.4",
            ),
            verification_samples=samples,
            postgres_dump=kb_bundle.ArtifactHash(filename="postgres.dump", bytes=1, sha256="a" * 64),
            qdrant_snapshot=kb_bundle.ArtifactHash(filename="qdrant.snapshot", bytes=1, sha256="b" * 64),
            evaluator_catalog=kb_bundle.EvaluatorCatalogState(
                path=kb_bundle.EVALUATOR_CATALOG_PATH.as_posix(),
                schema_version=kb_bundle.CATALOG_SCHEMA_VERSION,
                lookup_contract=kb_bundle.LOOKUP_CONTRACT,
                sha256="d" * 64, count=1, source_gold_sha256="e" * 64,
            ),
        )

    def test_public_v2_manifest_remains_strict_and_runtime_receipt_is_separate(self) -> None:
        manifest = self._manifest()
        receipt = manifest.model_dump(mode="json")
        self.assertIn("evaluator_catalog", receipt)
        self.assertIn("source_gold_sha256", receipt["evaluator_catalog"])
        with self.assertRaises(Exception):
            kb_bundle.BundleManifest.model_validate(receipt | {"evaluator_catalog": {}})

    def test_preflight_requires_0004_and_public_v2_distribution_assets(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / kb_bundle.POSTGRES_DUMP_NAME).write_bytes(b"p")
            (root / kb_bundle.QDRANT_SNAPSHOT_NAME).write_bytes(b"q")
            runtime = root / kb_bundle.RUNTIME_BM25_PATH
            runtime.mkdir(parents=True)
            (runtime / "model.onnx").write_bytes(b"model")
            source = root / "knowledge_objects.jsonl"
            source.write_text('{"object_id":"object.one","locator":{},"metadata":{}}\n', encoding="utf-8")
            catalog = kb_bundle.write_evaluator_catalog(source, root / kb_bundle.EVALUATOR_CATALOG_PATH)
            manifest = self._manifest().model_copy(update={
                "postgres_dump": kb_bundle._artifact(root / kb_bundle.POSTGRES_DUMP_NAME, kb_bundle.POSTGRES_DUMP_NAME),
                "qdrant_snapshot": kb_bundle._artifact(root / kb_bundle.QDRANT_SNAPSHOT_NAME, kb_bundle.QDRANT_SNAPSHOT_NAME),
                "evaluator_catalog": kb_bundle.EvaluatorCatalogState(
                    path=kb_bundle.EVALUATOR_CATALOG_PATH.as_posix(), schema_version=catalog.schema_version,
                    lookup_contract=catalog.lookup_contract, sha256=catalog.sha256, count=catalog.count,
                    source_gold_sha256="e" * 64,
                ),
            })
            kb_bundle._write_manifest(root / kb_bundle.MANIFEST_NAME, manifest)
            self.assertEqual(kb_bundle.preflight_bundle(root), manifest)
            wrong = manifest.model_copy(update={"postgres": manifest.postgres.model_copy(update={"revision": "0005"})})
            kb_bundle._write_manifest(root / kb_bundle.MANIFEST_NAME, wrong)
            with self.assertRaisesRegex(kb_bundle.BundleError, "knowledge revision"):
                kb_bundle.preflight_bundle(root)

    def test_public_v2_catalog_hash_mismatch_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / kb_bundle.POSTGRES_DUMP_NAME).write_bytes(b"p")
            (root / kb_bundle.QDRANT_SNAPSHOT_NAME).write_bytes(b"q")
            runtime = root / kb_bundle.RUNTIME_BM25_PATH
            runtime.mkdir(parents=True)
            (runtime / "model.onnx").write_bytes(b"model")
            source = root / "objects.jsonl"
            source.write_text('{"object_id":"one","locator":{},"metadata":{}}\n', encoding="utf-8")
            receipt = kb_bundle.write_evaluator_catalog(source, root / kb_bundle.EVALUATOR_CATALOG_PATH)
            manifest = self._manifest().model_copy(update={
                "postgres_dump": kb_bundle._artifact(root / kb_bundle.POSTGRES_DUMP_NAME, kb_bundle.POSTGRES_DUMP_NAME),
                "qdrant_snapshot": kb_bundle._artifact(root / kb_bundle.QDRANT_SNAPSHOT_NAME, kb_bundle.QDRANT_SNAPSHOT_NAME),
                "evaluator_catalog": kb_bundle.EvaluatorCatalogState(
                    path=kb_bundle.EVALUATOR_CATALOG_PATH.as_posix(), schema_version=receipt.schema_version,
                    lookup_contract=receipt.lookup_contract, sha256=receipt.sha256, count=receipt.count,
                    source_gold_sha256="e" * 64,
                ),
            })
            kb_bundle._write_manifest(root / kb_bundle.MANIFEST_NAME, manifest)
            (root / kb_bundle.EVALUATOR_CATALOG_PATH).write_bytes(b"{}")
            with self.assertRaisesRegex(kb_bundle.BundleError, "evaluator catalog"):
                kb_bundle.preflight_bundle(root)

    def test_restore_keeps_public_v2_evaluator_distribution_install(self) -> None:
        manifest = self._manifest()
        storage = MagicMock()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(kb_bundle, "preflight_bundle", return_value=manifest),
                patch.object(kb_bundle, "_assert_evaluator_catalog_installable"),
                patch.object(kb_bundle, "Storage", return_value=storage),
                patch.object(kb_bundle, "_target_is_empty"),
                patch.object(kb_bundle, "_restore_postgres"),
                patch.object(kb_bundle, "_restore_qdrant"),
                patch.object(kb_bundle, "_install_runtime_from_bundle"),
                patch.object(kb_bundle, "_install_evaluator_catalog_from_bundle") as install_catalog,
            ):
                kb_bundle.restore_bundle(root / "bundle", project_root=root)
        install_catalog.assert_called_once_with(root / "bundle", root.resolve())

    def test_kb_verify_accepts_service_0005_and_does_not_gate_on_runtime_registration(self) -> None:
        manifest = self._manifest()
        actual_pg = manifest.postgres.model_copy(update={"revision": "0005"})
        storage = _Storage()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(kb_bundle, "preflight_bundle", return_value=manifest),
                patch.object(kb_bundle, "Storage", return_value=storage),
                patch.object(kb_bundle, "postgres_state", return_value=actual_pg),
                patch.object(kb_bundle, "qdrant_state", return_value=manifest.qdrant),
                patch.object(kb_bundle, "fastembed_state", return_value=manifest.fastembed),
                patch.object(kb_bundle, "_verify_sample", return_value=True) as sample,
                patch.object(kb_bundle, "_verify_runtime", return_value=True),
                patch.object(kb_bundle, "catalog_receipt", return_value=type("Receipt", (), {
                    "schema_version": manifest.evaluator_catalog.schema_version,
                    "lookup_contract": manifest.evaluator_catalog.lookup_contract,
                    "sha256": manifest.evaluator_catalog.sha256,
                    "count": manifest.evaluator_catalog.count,
                })()),
            ):
                result = kb_bundle.verify_bundle(root, project_root=root)
        self.assertTrue(result["valid"])
        self.assertEqual(result["runtime_status"], "not_registered")
        self.assertEqual(sample.call_count, kb_bundle.SAMPLE_SIZE)

    def test_kb_verify_fails_closed_for_unsupported_service_revision(self) -> None:
        manifest = self._manifest()
        actual_pg = manifest.postgres.model_copy(update={"revision": "0006"})
        storage = _Storage()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(kb_bundle, "preflight_bundle", return_value=manifest),
                patch.object(kb_bundle, "Storage", return_value=storage),
                patch.object(kb_bundle, "postgres_state", return_value=actual_pg),
                patch.object(kb_bundle, "qdrant_state", return_value=manifest.qdrant),
                patch.object(kb_bundle, "fastembed_state", return_value=manifest.fastembed),
                patch.object(kb_bundle, "_verify_sample", return_value=True),
                patch.object(kb_bundle, "_verify_runtime", return_value=True),
                patch.object(kb_bundle, "catalog_receipt", return_value=type("Receipt", (), {
                    "schema_version": manifest.evaluator_catalog.schema_version,
                    "lookup_contract": manifest.evaluator_catalog.lookup_contract,
                    "sha256": manifest.evaluator_catalog.sha256,
                    "count": manifest.evaluator_catalog.count,
                })()),
            ):
                result = kb_bundle.verify_bundle(root, project_root=root)
        self.assertFalse(result["valid"])
        self.assertFalse(result["checks"]["migration_compatible"])

    def test_kb_verify_fails_when_restored_distribution_assets_are_missing(self) -> None:
        manifest = self._manifest()
        storage = _Storage()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(kb_bundle, "preflight_bundle", return_value=manifest),
                patch.object(kb_bundle, "Storage", return_value=storage),
                patch.object(kb_bundle, "postgres_state", return_value=manifest.postgres),
                patch.object(kb_bundle, "qdrant_state", return_value=manifest.qdrant),
                patch.object(kb_bundle, "fastembed_state", return_value=manifest.fastembed),
                patch.object(kb_bundle, "_verify_sample", return_value=True),
                patch.object(kb_bundle, "_verify_runtime", return_value=False),
                patch.object(kb_bundle, "catalog_receipt", side_effect=FileNotFoundError()),
            ):
                result = kb_bundle.verify_bundle(root, project_root=root)
        self.assertFalse(result["valid"])
        self.assertFalse(result["checks"]["runtime_bm25"])
        self.assertFalse(result["checks"]["evaluator_catalog_distribution"])

    def test_0005_migration_is_service_only(self) -> None:
        migration = (Path(__file__).parents[2] / "migrations" / "versions" / "0005_qa_service_runtime.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('revision = "0005"', migration)
        self.assertIn('down_revision = "0004"', migration)
        self.assertIn("ALTER TABLE qa_runs", migration)
        for field in ("completed_at", "duration_ms", "intent", "error_code", "node_timings", "model_usage"):
            self.assertIn(field, migration)
        self.assertNotIn("knowledge_objects", migration)
        self.assertNotIn("index_identities", migration)

    def test_existing_sample_and_qdrant_contracts_remain_covered(self) -> None:
        session = MagicMock()
        session.post.return_value = _Response({"result": {"count": 42}})
        self.assertEqual(kb_bundle.exact_qdrant_count(session, "http://qdrant", "collection"), 42)
        self.assertEqual(session.post.call_args.kwargs["json"], {"exact": True})
        session.get.return_value = _Response({"result": {"status": None}})
        with self.assertRaisesRegex(kb_bundle.BundleError, "green"):
            kb_bundle._qdrant_info(session, "http://qdrant", "collection")
        rows = [(f"object-{index:03d}", "source", "source@v1") for index in range(100)]
        storage = _CandidateStorage(rows)
        self.assertEqual(kb_bundle.deterministic_sample_candidates(storage), rows)
        self.assertIn("md5(k.object_id::text)", storage.connection.sql)

    def test_existing_sample_selection_fail_closed_contracts_remain_covered(self) -> None:
        rows = [(f"object-{index:03d}", "source", "source@v1") for index in range(101)]
        storage = _CandidateStorage(rows)

        def retrieve(*, ids: list[str], **_: object) -> list[object]:
            return [
                type("Point", (), {"id": point_id, "payload": {
                    "object_id": point_id.removeprefix("point:"), "source_id": "source",
                    "source_version_id": "source@v1",
                }})()
                for point_id in ids if point_id != "point:object-000"
            ]

        storage.qdrant.retrieve.side_effect = retrieve
        selected = kb_bundle.select_verification_samples(storage)
        self.assertEqual([item.object_id for item in selected], [row[0] for row in rows[1:]])
        self.assertEqual(storage.connection.params[2], kb_bundle.SAMPLE_CANDIDATE_POOL_SIZE)
        bad_storage = _CandidateStorage(rows)
        bad_storage.qdrant.retrieve.return_value = [
            type("Point", (), {"id": "point:object-000", "payload": {"object_id": "wrong"}})()
        ]
        with self.assertRaisesRegex(kb_bundle.BundleError, "payload identity"):
            kb_bundle.select_verification_samples(bad_storage)

    def test_existing_restore_and_runtime_distribution_contracts_remain_covered(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / kb_bundle.MANIFEST_NAME).write_text("{}", encoding="utf-8")
            with patch.object(kb_bundle, "Storage") as storage:
                with self.assertRaises(kb_bundle.BundleError):
                    kb_bundle.restore_bundle(root, project_root=root)
            storage.assert_not_called()
            bundle = root / "bundle"
            source = bundle / kb_bundle.RUNTIME_BM25_PATH
            source.mkdir(parents=True)
            (source / "model.onnx").write_bytes(b"model")
            installed = kb_bundle._install_runtime_from_bundle(bundle, root)
            vector = type("Vector", (), {"values": [1.0]})()
            embedding = type("Embedding", (), {"query_embed": lambda self, text: iter([vector])})()
            with patch.object(kb_bundle, "create_sparse_encoder", return_value=(embedding, object())) as factory:
                self.assertTrue(kb_bundle._verify_runtime(root))
            self.assertEqual(factory.call_args.kwargs["model_path"], installed)

    def test_existing_restore_and_export_guards_remain_covered(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / kb_bundle.POSTGRES_DUMP_NAME).write_bytes(b"dump")
            calls: list[list[str]] = []
            kb_bundle._restore_postgres(root, root, lambda command, **_: calls.append(command))
        self.assertIn("--exit-on-error", calls[0])
        self.assertIn("--single-transaction", calls[0])
        with patch.object(kb_bundle, "verify_index", return_value={"valid": False}):
            with self.assertRaisesRegex(kb_bundle.BundleError, "index verification"):
                kb_bundle._export_preflight(Path("."), MagicMock())
        with self.assertRaises(ValueError):
            kb_bundle.PostgresState(
                database=kb_bundle.DATABASE_NAME, revision="0004", table_counts={}, index_fingerprint="x"
            )


if __name__ == "__main__":
    unittest.main()
