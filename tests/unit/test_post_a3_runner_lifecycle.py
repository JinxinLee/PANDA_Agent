"""Focused tests for post-A3 runner lifecycle, store reopen stability, and review persistence.

Covers:
- Store reopen preserves exact bytes and cumulative usage after successful record
- Store reopen preserves exact bytes and cumulative usage after legacy attempts seeding
- Direct failure review persists computed metrics/gate before sealing stage receipt,
  ensuring subsequent report_evaluation produces a stable, non-mismatched receipt
- Actual run -> retryable exception -> resume only retries failed case with full
  attempt accounting and no record byte drift
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from panda_agent.evaluation import (
    EvaluationRunStore,
    sha256_file,
)
from panda_agent.evaluation_runner import (
    report_evaluation,
    resume_evaluation,
    run_evaluation,
    write_failure_review,
)
from panda_agent.llm.vertex import VertexCallError


class PostA3RunnerLifecycleTests(unittest.TestCase):
    def _base_manifest(self) -> dict:
        return {
            "schema_version": "1.0",
            "mode": "full",
            "split": "dev",
            "official": True,
            "prompt_hash": "a" * 64,
            "gold_dataset_hash": "b" * 64,
            "index_identity": "c" * 64,
            "repository_identity": {"commit": "1111111", "dirty": False},
        }

    def test_store_reopen_stable_bytes_and_usage_after_successful_record(self):
        """Store reopening must preserve exact results.jsonl/records bytes and usage without hash drift."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest()
            store = EvaluationRunStore(root, "run-stable-record", manifest)
            rec = {
                "id": "g001",
                "result": {"status": "answered", "answer": "text"},
                "model_calls": 3,
                "token_usage": 1000,
            }
            store.record(rec)

            results_bytes_before = store.results_path.read_bytes()
            record_bytes_before = (store.records_dir / "g001.json").read_bytes()
            usage_before = store.cumulative_usage()

            # Reopen in resume mode
            reopened = EvaluationRunStore(root, "run-stable-record", manifest, resume=True)

            results_bytes_after = reopened.results_path.read_bytes()
            record_bytes_after = (reopened.records_dir / "g001.json").read_bytes()
            usage_after = reopened.cumulative_usage()

            self.assertEqual(
                results_bytes_after,
                results_bytes_before,
                "results.jsonl bytes must be stable across store reopen without attempted_at drift",
            )
            self.assertEqual(
                record_bytes_after,
                record_bytes_before,
                "records/g001.json bytes must be stable across store reopen without attempted_at drift",
            )
            self.assertEqual(
                usage_after,
                usage_before,
                "cumulative usage must be stable across store reopen",
            )

    def test_store_reopen_stable_bytes_and_usage_after_legacy_seed(self):
        """Reopening a legacy run that required attempts seeding must not cause subsequent byte drift."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest()
            run_dir = root / "run-legacy-seed"
            run_dir.mkdir(parents=True)
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = {
                "id": "g001",
                "result": {"status": "answered", "answer": "text"},
                "model_calls": 5,
                "token_usage": 1500,
            }
            (run_dir / "results.jsonl").write_bytes((json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
            records_dir = run_dir / "records"
            records_dir.mkdir()
            (records_dir / "g001.json").write_bytes((json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))

            initial_results_bytes = (run_dir / "results.jsonl").read_bytes()
            initial_record_bytes = (records_dir / "g001.json").read_bytes()

            # First reopen: seeds attempts.jsonl
            store1 = EvaluationRunStore(root, "run-legacy-seed", manifest, resume=True)
            self.assertTrue(store1.attempts_path.exists())
            seeded_results_bytes = store1.results_path.read_bytes()
            seeded_record_bytes = (store1.records_dir / "g001.json").read_bytes()
            seeded_usage = store1.cumulative_usage()
            self.assertEqual(seeded_usage, (5, 1500))

            # Second reopen: must not drift bytes
            store2 = EvaluationRunStore(root, "run-legacy-seed", manifest, resume=True)
            reopened_results_bytes = store2.results_path.read_bytes()
            reopened_record_bytes = (store2.records_dir / "g001.json").read_bytes()
            reopened_usage = store2.cumulative_usage()

            self.assertEqual(
                seeded_results_bytes,
                initial_results_bytes,
                "seeding attempts ledger must not mutate existing results.jsonl",
            )
            self.assertEqual(
                seeded_record_bytes,
                initial_record_bytes,
                "seeding attempts ledger must not mutate existing records/g001.json",
            )
            self.assertEqual(
                reopened_results_bytes,
                seeded_results_bytes,
                "results.jsonl bytes must be stable across second reopen",
            )
            self.assertEqual(
                reopened_record_bytes,
                seeded_record_bytes,
                "records/g001.json bytes must be stable across second reopen",
            )
            self.assertEqual(
                reopened_usage,
                seeded_usage,
                "cumulative usage must be stable across second reopen",
            )

    def test_direct_review_before_report_stable_receipt(self):
        """write_failure_review called before report_evaluation must persist metrics/gate before sealing stage receipt."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-review-first"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "official": False,
                "gold_dataset_path": str(Path.cwd() / "evaluation" / "benchmarks" / "v2_9" / "gold_questions.yaml"),
                "case_ids": ["g001"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            record = {
                "id": "g001",
                "intent": "usage",
                "split": "dev",
                "language": "en",
                "expected_status": "answered",
                "result": {"status": "insufficient_evidence", "answer": "failed"},
                "metrics": {"answer_point_coverage": 0.0},
            }
            (run_dir / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
            (run_dir / "records").mkdir()
            (run_dir / "records" / "g001.json").write_text(json.dumps(record), encoding="utf-8")

            # Direct failure review invocation
            review_res = write_failure_review(root, "test-review-first")
            self.assertTrue(review_res["created"])

            # Computed metrics and gate MUST be persisted on disk before sealing
            metrics_path = run_dir / "metrics.json"
            gate_path = run_dir / "gate.json"
            receipt_path = run_dir / "stage_receipt.json"

            self.assertTrue(metrics_path.exists(), "metrics.json must be persisted before stage receipt seal")
            self.assertTrue(gate_path.exists(), "gate.json must be persisted before stage receipt seal")
            self.assertTrue(receipt_path.exists(), "stage_receipt.json must be created")

            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertIsNotNone(
                receipt["artifacts_and_hashes"]["metrics_file_sha256"],
                "metrics_file_sha256 must not be None when stage receipt is sealed",
            )
            self.assertIsNotNone(
                receipt["artifacts_and_hashes"]["gate_file_sha256"],
                "gate_file_sha256 must not be None when stage receipt is sealed",
            )

            # Subsequent report_evaluation must succeed cleanly and preserve the exact receipt
            report = report_evaluation(root, "test-review-first")
            self.assertIn("stage_receipt", report)

            receipt_after = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(
                receipt_after["artifacts_and_hashes"],
                receipt["artifacts_and_hashes"],
                "stage receipt hashes must remain unchanged after subsequent report_evaluation",
            )

    def test_actual_run_retryable_resume_only_failed_accounting_both_attempts(self):
        """run_evaluation -> retryable exception -> resume_evaluation only retries failed case and accounts both attempts."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gold_path = root / "gold.yaml"
            gold_content = (Path.cwd() / "evaluation" / "benchmarks" / "v2_9" / "gold_questions.yaml").read_text(
                encoding="utf-8"
            )
            gold_path.write_text(gold_content, encoding="utf-8")

            candidate_id = "f6a-rc3-20260914"
            run_id = "lifecycle-run-e2e"

            usage_tracker = {"calls": 0, "tokens": 0}
            fake_engine = MagicMock()
            fake_engine.vertex.stats_snapshot.side_effect = lambda: {
                "model_calls": usage_tracker["calls"],
                "token_usage": usage_tracker["tokens"],
            }

            executed_cases = []

            def fake_execute_case(engine, judge_vertex, *, mode, case, object_lookup):
                executed_cases.append(case.id)
                if case.id == "g001":
                    usage_tracker["calls"] += 2
                    usage_tracker["tokens"] += 200
                    return (
                        {"status": "answered", "answer": "installed ok"},
                        {"retrieved_count": 1},
                        {
                            "answer_point_coverage": 1.0,
                            "gold_recall_at_10": 1.0,
                            "final_evidence_recall": 1.0,
                            "critical_final_evidence_recall": 1.0,
                            "expected_status_correct": True,
                            "intent_correct": True,
                            "citation_integrity": 1.0,
                        },
                    )
                elif case.id == "g002":
                    if len([c for c in executed_cases if c == "g002"]) == 1:
                        usage_tracker["calls"] += 1
                        usage_tracker["tokens"] += 100
                        raise VertexCallError("429 RESOURCE_EXHAUSTED: rate limit exceeded")
                    else:
                        usage_tracker["calls"] += 3
                        usage_tracker["tokens"] += 400
                        return (
                            {"status": "answered", "answer": "recovered ok"},
                            {"retrieved_count": 1},
                            {
                                "answer_point_coverage": 1.0,
                                "gold_recall_at_10": 1.0,
                                "final_evidence_recall": 1.0,
                                "critical_final_evidence_recall": 1.0,
                                "expected_status_correct": True,
                                "intent_correct": True,
                                "citation_integrity": 1.0,
                            },
                        )
                raise ValueError(f"unexpected case {case.id}")

            def fake_build_manifest(proj_root, ds_path, *, mode, split, official):
                return {
                    "schema_version": "1.0",
                    "mode": mode,
                    "split": split,
                    "official": official,
                    "repository_identity": {"commit": "1111111", "dirty": False},
                    "prompt_hash": "a" * 64,
                    "gold_dataset_hash": sha256_file(ds_path),
                    "gold_dataset_path": str(ds_path),
                    "index_identity": "c" * 64,
                    "candidate_id": candidate_id,
                }

            cand_mock = {
                "candidate_id": candidate_id,
                "valid": True,
                "manifest_sha256": "cand" * 16,
                "mismatches": [],
            }

            with (
                patch("panda_agent.evaluation_runner.Retriever", return_value=fake_engine),
                patch("panda_agent.evaluation_runner._execute_evaluation_case", side_effect=fake_execute_case),
                patch("panda_agent.evaluation_runner.build_evaluation_manifest", side_effect=fake_build_manifest),
                patch("panda_agent.evaluation_runner.load_object_lookup", return_value={}),
                patch("panda_agent.candidate.verify_candidate", return_value=cand_mock),
                patch("panda_agent.evaluation.verify_candidate_identity", return_value=cand_mock),
            ):
                # Attempt 1: run_evaluation
                run_dir = run_evaluation(
                    root,
                    mode="retrieval",
                    split="dev",
                    run_id=run_id,
                    candidate_id=candidate_id,
                    case_ids=["g001", "g002"],
                    dataset_path=gold_path,
                )

                # Attempt 1 verification
                self.assertEqual(executed_cases, ["g001", "g002"])
                run_status_1 = json.loads((run_dir / "run_status.json").read_text(encoding="utf-8"))
                self.assertEqual(run_status_1["cohort_status"], "INCOMPLETE")
                self.assertEqual(run_status_1["official_decision"], "RECOVERY_PENDING")
                self.assertEqual(run_status_1["attempt_model_calls"], 3)
                self.assertEqual(run_status_1["attempt_token_usage"], 300)
                self.assertEqual(run_status_1["cumulative_model_calls"], 3)
                self.assertEqual(run_status_1["cumulative_token_usage"], 300)

                g001_record_before = (run_dir / "records" / "g001.json").read_bytes()

                # Attempt 2: resume_evaluation
                resume_dir = resume_evaluation(root, run_id)
                self.assertEqual(resume_dir, run_dir)

                # Only failed case g002 is executed on resume
                self.assertEqual(executed_cases, ["g001", "g002", "g002"])

                # Accounting across both attempts
                run_status_2 = json.loads((run_dir / "run_status.json").read_text(encoding="utf-8"))
                self.assertEqual(run_status_2["cohort_status"], "COMPLETE")
                self.assertEqual(run_status_2["attempt_model_calls"], 3)
                self.assertEqual(run_status_2["attempt_token_usage"], 400)
                self.assertEqual(run_status_2["cumulative_model_calls"], 6)
                self.assertEqual(run_status_2["cumulative_token_usage"], 700)

                # results.jsonl has exactly 2 records without duplicate IDs
                results_lines = [
                    json.loads(line)
                    for line in (run_dir / "results.jsonl").read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                self.assertEqual(len(results_lines), 2)
                self.assertEqual(sorted(r["id"] for r in results_lines), ["g001", "g002"])

                # attempts.jsonl has exactly 3 attempt entries
                attempts_lines = [
                    json.loads(line)
                    for line in (run_dir / "attempts.jsonl").read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                self.assertEqual(len(attempts_lines), 3)

                # Final stage receipt sealed
                receipt_file = run_dir / "stage_receipt.json"
                self.assertTrue(receipt_file.exists())
                receipt_data = json.loads(receipt_file.read_text(encoding="utf-8"))
                self.assertEqual(receipt_data["execution_status"]["cohort_status"], "COMPLETE")
                self.assertEqual(receipt_data["usage"]["cumulative_model_calls"], 6)
                self.assertEqual(receipt_data["usage"]["cumulative_token_usage"], 700)

                # Successful record g001 must not have drifted bytes on resume
                g001_record_after = (run_dir / "records" / "g001.json").read_bytes()
                self.assertEqual(
                    g001_record_after,
                    g001_record_before,
                    "successful record g001 must not drift bytes on resume",
                )


if __name__ == "__main__":
    unittest.main()
