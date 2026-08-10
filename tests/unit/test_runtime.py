from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from panda_agent import kb_bundle, runtime


class RuntimeContractTests(unittest.TestCase):
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
                database=kb_bundle.DATABASE_NAME, revision="0004",
                table_counts={name: 1 for name in kb_bundle.SELECTED_TABLES}, index_fingerprint="f" * 64,
            ),
            qdrant=kb_bundle.QdrantState(
                collection=kb_bundle.COLLECTION_NAME, point_count=100,
                dense_config={"dense": {"size": 3072}}, sparse_config={"sparse": {}},
                payload_indexes={"source_id": {"data_type": "keyword"}},
            ),
            fastembed=kb_bundle.FastEmbedState(
                model="Qdrant/bm25", vector_name="sparse", language="english", fastembed_version="0.7.4",
            ),
            verification_samples=samples,
            postgres_dump=kb_bundle.ArtifactHash(filename="postgres.dump", bytes=1, sha256="a" * 64),
            qdrant_snapshot=kb_bundle.ArtifactHash(filename="qdrant.snapshot", bytes=1, sha256="b" * 64),
            evaluator_catalog=kb_bundle.EvaluatorCatalogState(
                path=kb_bundle.EVALUATOR_CATALOG_PATH.as_posix(), schema_version=kb_bundle.CATALOG_SCHEMA_VERSION,
                lookup_contract=kb_bundle.LOOKUP_CONTRACT, sha256="d" * 64, count=1,
                source_gold_sha256="e" * 64,
            ),
        )

    def _actual(self, manifest: kb_bundle.BundleManifest, revision: str = "0005") -> tuple[object, ...]:
        return (
            manifest.postgres.model_copy(update={"revision": revision}),
            manifest.qdrant,
            manifest.fastembed,
            runtime.EmbeddingIdentity(model="gemini-embedding-2", dimensions=3072),
        )

    def test_register_is_receipt_free_and_writes_identity_atomically(self) -> None:
        manifest = self._manifest()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "data" / "runtime" / "installed_bundle.json"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("not json", encoding="utf-8")
            with (
                patch.object(kb_bundle, "preflight_bundle", return_value=manifest),
                patch.object(runtime, "_collect_actual", return_value=self._actual(manifest)),
                patch.object(kb_bundle, "_verify_runtime", return_value=True),
                patch.object(kb_bundle, "sha256_file", return_value="b" * 64),
                patch.object(runtime.os, "replace", wraps=runtime.os.replace) as replace,
            ):
                result = runtime.register_runtime(root / "bundle", project_root=root)
            identity_path = runtime.runtime_identity_path(root)
            payload = runtime.RuntimeIdentity.model_validate_json(identity_path.read_text(encoding="utf-8"))
        self.assertTrue(result["valid"])
        self.assertEqual(result["runtime_status"], "registered")
        self.assertTrue(replace.called)
        self.assertEqual(payload.service_revision, "0005")
        self.assertEqual(payload.bundle_manifest_sha256, "b" * 64)
        self.assertIsNotNone(payload.registered_at)
        self.assertNotIn("installed_bundle", identity_path.name)
        self.assertNotIn("gold", payload.model_dump_json().lower())
        self.assertNotIn("prompt", payload.model_dump_json().lower())

    def test_registration_requires_actual_service_0005_and_does_not_write_on_failure(self) -> None:
        manifest = self._manifest()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(kb_bundle, "preflight_bundle", return_value=manifest),
                patch.object(runtime, "_collect_actual", return_value=self._actual(manifest, "0004")),
                patch.object(kb_bundle, "_verify_runtime", return_value=True),
            ):
                with self.assertRaisesRegex(runtime.RuntimeContractError, "service_revision"):
                    runtime.register_runtime(root / "bundle", project_root=root)
            self.assertFalse(runtime.runtime_identity_path(root).exists())

    def test_receipt_free_validator_is_the_registration_precondition(self) -> None:
        manifest = self._manifest()
        actual = self._actual(manifest)
        state = {"valid": True, "checks": {"service_revision": True}, "manifest": manifest, "actual": actual}
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(runtime, "validate_runtime_state_without_receipt", return_value=state) as validate,
                patch.object(kb_bundle, "sha256_file", return_value="b" * 64),
            ):
                runtime.register_runtime(root / "bundle", project_root=root)
        validate.assert_called_once()

    def test_runtime_verify_is_an_independent_readiness_gate(self) -> None:
        manifest = self._manifest()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(runtime.verify_runtime(project_root=root)["runtime_status"], "not_registered")
            identity = runtime.RuntimeIdentity(
                bundle_manifest_sha256="b" * 64, registered_at=datetime(2026, 8, 10, tzinfo=UTC),
                corpus_source_manifest_sha256=manifest.corpus_source_manifest_sha256,
                postgres=manifest.postgres,
                qdrant=manifest.qdrant,
                fastembed=manifest.fastembed,
                embedding=runtime.EmbeddingIdentity(model="gemini-embedding-2", dimensions=3072),
            )
            runtime._write_identity(runtime.runtime_identity_path(root), identity)
            with (
                patch.object(runtime, "_collect_actual", return_value=self._actual(manifest)),
                patch.object(kb_bundle, "_verify_runtime", return_value=True),
            ):
                result = runtime.verify_runtime(project_root=root)
        self.assertTrue(result["valid"])
        self.assertEqual(result["runtime_status"], "registered")


if __name__ == "__main__":
    unittest.main()
