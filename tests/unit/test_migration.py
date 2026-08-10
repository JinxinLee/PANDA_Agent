from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from panda_agent.evaluator_catalog import write_evaluator_catalog
from panda_agent.migration import (
    MIGRATION_CASE_IDS,
    build_suite,
    capture_replay,
    compare_evaluators,
    compare_qa_records,
    compare_replays,
    load_suite,
    replay_capture,
    replay_backend,
    sanitized_endpoint_identity,
    write_comparison_artifact,
    write_report,
)
from panda_agent.cli import migration as migration_cli


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_GOLD = PROJECT_ROOT / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"


class MigrationTests(unittest.TestCase):
    def test_sanitized_backend_identity_never_serializes_credentials(self):
        identity = sanitized_endpoint_identity("postgresql://alice:secret@db.example:55433/panda")
        encoded = json.dumps(identity)
        self.assertNotIn("secret", encoded)
        self.assertNotIn("alice", encoded)
        self.assertEqual(identity["port"], 55433)

    def test_comparison_artifact_refuses_overwrite_and_report_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            path = temp / "compare.json"
            write_comparison_artifact(path, {"passed": True})
            with self.assertRaises(Exception):
                write_comparison_artifact(path, {"passed": True})
            suite = build_suite(CANONICAL_GOLD, temp / "suite.json")
            replay = {"passed": False, "cases": {}}
            evaluator = {"passed": True}
            qa = {"conclusion": "transfer_equivalent", "cases": {}}
            report_json, _ = write_report(temp / "report", suite=suite, replay=replay, evaluator=evaluator, qa=qa)
            self.assertEqual(json.loads(report_json.read_text(encoding="utf-8"))["global_conclusion"], "transfer_regression")
    def test_v1_migration_suite_has_frozen_case_ids(self) -> None:
        self.assertEqual(
            MIGRATION_CASE_IDS,
            ("g001", "g007", "g012", "g013", "g027", "g051", "g060", "g085", "g106", "g116"),
        )

    def test_suite_is_exactly_derived_from_canonical_gold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "suite.json"
            suite = build_suite(CANONICAL_GOLD, path)
            self.assertEqual(suite["canonical_gold_sha256"], "b5406e36c64ee664f9e2ff9c0f42e354feb7164c81d8f1c7551d8f2ed1d0b687")
            self.assertEqual([item["id"] for item in suite["cases"]], list(MIGRATION_CASE_IDS))
            self.assertEqual(load_suite(path, CANONICAL_GOLD)["suite_sha256"], suite["suite_sha256"])

    def test_capture_replay_and_tie_aware_comparison_are_model_free(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            suite = build_suite(CANONICAL_GOLD, temp / "suite.json")
            cases = {
                case_id: {
                    "plan": {"intent": "api"},
                    "vector_inputs": {"dense": [0.1], "sparse": {"indices": [1], "values": [1.0]}, "filter": {}},
                    "channels": {
                        "dense": [{"object_id": "b", "score": 1.0}, {"object_id": "a", "score": 1.0}],
                        "sparse": [],
                        "exact": [{"object_id": "a", "score": 0.0}],
                        "path": [],
                        "metadata": [],
                        "workflow": [{"object_id": "c", "score": 0.0}],
                        "graph": [],
                    },
                    "model_calls": 2,
                }
                for case_id in MIGRATION_CASE_IDS
            }
            capture = capture_replay(suite, cases, temp / "capture.json")
            replay = replay_capture(suite, temp / "capture.json", temp / "replay-a.json")
            self.assertEqual(capture["model_calls"], 20)
            self.assertEqual(replay["model_calls"], 0)
            # Replaying the same immutable capture is exact and model-free.
            replay_capture(suite, temp / "capture.json", temp / "replay-b.json")
            comparison = compare_replays(temp / "replay-a.json", temp / "replay-b.json")
            self.assertTrue(comparison["passed"])
            self.assertEqual(comparison["model_calls"], 0)

    def test_backend_replay_uses_explicit_storage_without_model_client(self) -> None:
        class Cursor:
            def fetchall(self):
                return []

        class Connection:
            def __enter__(self):
                return self

            def __exit__(self, *unused):
                return False

            def execute(self, query, params):
                return Cursor()

        class Qdrant:
            def __init__(self):
                self.calls = 0

            def query_points(self, **kwargs):
                self.calls += 1
                return SimpleNamespace(points=[])

        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            suite = build_suite(CANONICAL_GOLD, temp / "suite.json")
            cases = {
                case_id: {"plan": {"symbols": [], "concepts": [], "target_repositories": []}, "vector_inputs": {"dense": [0.1], "sparse": {"indices": [], "values": []}, "filter": {}}, "channels": {key: [] for key in ("dense", "sparse", "exact", "path", "metadata", "workflow", "graph")}}
                for case_id in MIGRATION_CASE_IDS
            }
            capture_replay(suite, cases, temp / "capture.json")
            qdrant = Qdrant()
            storage = SimpleNamespace(settings=SimpleNamespace(database_url="postgres://original", qdrant_url="http://original", collection_name="original"), qdrant=qdrant, connect=lambda: Connection())
            value = replay_backend(suite, temp / "capture.json", temp / "backend.json", storage=storage)
            self.assertEqual(value["model_calls"], 0)
            self.assertEqual(qdrant.calls, 20)

    def test_evaluator_ab_uses_exact_selector_parity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            item = {
                "object_id": "unrelated", "object_type": "source_file", "source_id": "pandaroot",
                "source_version_id": "pandaroot@locked", "title": "unrelated", "text": "", "authority_level": "primary",
                "locator": {"path": "x"}, "metadata": {}, "canonical_locator": "x", "token_count": 0,
                "embedding_eligible": True, "content_hash": "x",
            }
            normalized = temp / "objects.jsonl"
            normalized.write_text(json.dumps(item) + "\n", encoding="utf-8")
            catalog = temp / "catalog.json"
            write_evaluator_catalog(normalized, catalog)
            records = {
                case_id: {"id": case_id, "result": {"status": "answered", "answer": ""}, "diagnostics": {}}
                for case_id in MIGRATION_CASE_IDS
            }
            result = compare_evaluators(CANONICAL_GOLD, normalized, catalog, records=records)
            self.assertTrue(result["passed"])
            self.assertTrue(result["selector_parity"])
            self.assertTrue(result["saved_record_metric_parity"])

    def test_qa_gate_precedence_and_relative_regression(self) -> None:
        baseline = []
        restored = []
        for case_id in MIGRATION_CASE_IDS:
            common = {"id": case_id, "evaluator_identity": "same", "result": {"status": "answered"}}
            baseline.append({**common, "metrics": {"expected_status_correct": True, "citation_integrity": True, "required_source_coverage": 1.0, "answer_point_coverage": 1.0, "identifier_coverage": 1.0}})
            restored.append({**common, "metrics": {"expected_status_correct": True, "citation_integrity": True, "required_source_coverage": 0.0, "answer_point_coverage": 1.0, "identifier_coverage": 1.0}})
        result = compare_qa_records(baseline, restored)
        self.assertEqual(result["conclusion"], "transfer_regression")
        restored[0]["evaluator_identity"] = "different"
        self.assertEqual(compare_qa_records(baseline, restored)["conclusion"], "evaluator_not_comparable")

    def test_cli_live_qa_injects_explicit_storage_and_gold(self) -> None:
        fake_records = [
            {"id": case_id, "model_calls": 1, "token_usage": 2}
            for case_id in MIGRATION_CASE_IDS
        ]
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            suite_path = temp / "suite.json"
            build_suite(CANONICAL_GOLD, suite_path)
            output = temp / "baseline.json"
            argv = [
                "panda-qa-migration",
                "--project-root",
                str(PROJECT_ROOT),
                "run-qa",
                "--role",
                "baseline",
                "--suite",
                str(suite_path),
                "--live",
                "--canonical-gold",
                str(CANONICAL_GOLD),
                "--portable-catalog",
                str(temp / "catalog.json"),
                "--database-url",
                "postgresql://migration_user:secret@restore-db:55433/panda_qa",
                "--qdrant-url",
                "http://restore-qdrant:6335",
                "--collection",
                "restored_collection",
                "--output",
                str(output),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(migration_cli, "load_suite", return_value={"cases": []}),
                patch.object(migration_cli, "collect_live_qa", return_value=fake_records) as collect,
                patch.object(migration_cli, "score_qa_records", return_value=fake_records),
                patch("panda_agent.storage.Storage") as storage_cls,
            ):
                migration_cli.main()
            self.assertTrue(output.is_file())
            collect.assert_called_once()
            call = collect.call_args
            self.assertEqual(call.args[0], PROJECT_ROOT.resolve())
            self.assertEqual(call.args[2], "baseline")
            self.assertEqual(call.args[3], CANONICAL_GOLD.resolve())
            self.assertIs(call.kwargs["storage"], storage_cls.return_value)


if __name__ == "__main__":
    unittest.main()
