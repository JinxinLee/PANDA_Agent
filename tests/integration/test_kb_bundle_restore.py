"""Contract checks for the isolated bundle-restore compose harness and live read-only SQL.

Live invocation is intentionally opt-in and must use COMPOSE_PROJECT_NAME plus
docker-compose.bundle-restore.yml; these tests never touch the current services.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from panda_agent import kb_bundle
from panda_agent.storage import Storage, StorageSettings


class BundleRestoreHarnessTests(unittest.TestCase):
    def test_live_postgres_candidates_execute_with_distinct_md5_ordering(self) -> None:
        storage = Storage(StorageSettings())
        candidates = kb_bundle.deterministic_sample_candidates(storage, size=100)
        self.assertEqual(len(candidates), 100)
        self.assertEqual(len({object_id for object_id, _, _ in candidates}), 100)

    def test_live_qdrant_selection_replaces_missing_candidates_with_identity_matched_points(self) -> None:
        storage = Storage(StorageSettings())
        samples = kb_bundle.select_verification_samples(storage)
        self.assertEqual(len(samples), 100)
        self.assertEqual(len({sample.object_id for sample in samples}), 100)
        expected = {
            sample.point_id: (sample.object_id, sample.source_id, sample.source_version_id)
            for sample in samples
        }
        found: dict[str, tuple[object, object, object]] = {}
        for point_ids in kb_bundle._chunks(list(expected)):
            points = storage.qdrant.retrieve(
                collection_name=storage.settings.collection_name, ids=list(point_ids),
                with_payload=True, with_vectors=False,
            )
            for point in points:
                payload = point.payload or {}
                found[str(point.id)] = (
                    payload.get("object_id"), payload.get("source_id"), payload.get("source_version_id"),
                )
        self.assertEqual(found, expected)

    def test_harness_uses_dedicated_ports(self) -> None:
        compose = (Path(__file__).parent / "docker-compose.bundle-restore.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("55433", compose)
        self.assertIn("6335", compose)

    def test_restore_mock_contract_preflights_before_any_mutation(self) -> None:
        manifest = kb_bundle.BundleManifest(
            schema_version=kb_bundle.BUNDLE_SCHEMA_VERSION,
            created_at=datetime(2026, 8, 9, tzinfo=UTC),
            corpus_source_manifest_sha256="c" * 64,
            postgres=kb_bundle.PostgresState(
                database=kb_bundle.DATABASE_NAME,
                revision="0004",
                table_counts={name: 1 for name in kb_bundle.SELECTED_TABLES},
                index_fingerprint="f" * 64,
            ),
            qdrant=kb_bundle.QdrantState(
                collection=kb_bundle.COLLECTION_NAME,
                point_count=100,
                dense_config={}, sparse_config={"sparse": {}}, payload_indexes={},
            ),
            fastembed=kb_bundle.FastEmbedState(
                model="Qdrant/bm25", vector_name="sparse", language="english", fastembed_version="0.7.4",
            ),
            verification_samples=[
                kb_bundle.VerificationSample(
                    object_id=f"object-{index}", point_id=f"point-{index}", source_id="source", source_version_id="source@v1"
                ) for index in range(100)
            ],
            postgres_dump=kb_bundle.ArtifactHash(filename="postgres.dump", bytes=1, sha256="a" * 64),
            qdrant_snapshot=kb_bundle.ArtifactHash(filename="qdrant.snapshot", bytes=1, sha256="b" * 64),
            evaluator_catalog=kb_bundle.EvaluatorCatalogState(
                path=kb_bundle.EVALUATOR_CATALOG_PATH.as_posix(),
                schema_version=kb_bundle.CATALOG_SCHEMA_VERSION,
                lookup_contract=kb_bundle.LOOKUP_CONTRACT,
                sha256="d" * 64,
                count=2,
                source_gold_sha256="e" * 64,
            ),
        )
        events: list[str] = []
        storage = MagicMock()
        with (
            patch.object(kb_bundle, "preflight_bundle", side_effect=lambda _: events.append("preflight") or manifest),
            patch.object(kb_bundle, "Storage", return_value=storage),
            patch.object(kb_bundle, "_target_is_empty", side_effect=lambda *_: events.append("empty")),
            patch.object(kb_bundle, "_restore_postgres", side_effect=lambda *_: events.append("postgres")),
            patch.object(kb_bundle, "_restore_qdrant", side_effect=lambda *_: events.append("qdrant")),
            patch.object(kb_bundle, "_install_runtime_from_bundle", side_effect=lambda *_: events.append("runtime")),
            patch.object(kb_bundle, "_install_evaluator_catalog_from_bundle", side_effect=lambda *_: events.append("catalog")),
            patch.object(kb_bundle, "_installed_marker", side_effect=lambda *_: events.append("marker")),
        ):
            kb_bundle.restore_bundle(Path("bundle"), project_root=Path("project"), session=MagicMock())
        self.assertEqual(events, ["preflight", "empty", "postgres", "qdrant", "runtime", "catalog", "marker"])


if __name__ == "__main__":
    unittest.main()
