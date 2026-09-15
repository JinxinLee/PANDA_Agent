"""Focused tests for post-A3 execution recovery and finalization infrastructure.

Covers:
- Success records unchanged on resume
- Retryable infrastructure exceptions resumable
- Terminal non-retryable exceptions not retried
- Single current result per case without duplicate results in results.jsonl
- Multiple failed-attempt usage recoverable via forward-only attempts ledger
- Lifecycle-only git commit change allowed under verified candidate vs real identity drift failing closed
- Stage receipt created before report and diagnostic inspection
- Incomplete cohort evaluated as RECOVERY_PENDING / INCONCLUSIVE, never complete PASS or terminal FAIL
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from panda_agent.evaluation import (
    EvaluationRunStore,
    classify_evaluation_exception,
    evaluate_cohort_decision,
    evaluation_record_state,
    load_run_records,
)
from panda_agent.evaluation_finalization import (
    create_stage_receipt,
    finalize_stage_evaluation,
)
from panda_agent.llm.vertex import VertexCallError


class ExecutionRecoveryClassificationTests(unittest.TestCase):
    def test_classify_transient_infrastructure_exceptions(self):
        # 429 Resource Exhausted
        exc_429 = VertexCallError(
            "structured generation failed for gemini-3.8-flash: 429 RESOURCE_EXHAUSTED"
        )
        retryable, category = classify_evaluation_exception(exc_429)
        self.assertTrue(retryable)
        self.assertIn("transport_provider", category)

        # ConnectionError / TimeoutError
        retryable, category = classify_evaluation_exception(ConnectionError("Connection reset by peer"))
        self.assertTrue(retryable)

        retryable, category = classify_evaluation_exception(TimeoutError("Request timed out"))
        self.assertTrue(retryable)

        # Unparsable response / JSONDecodeError
        retryable, category = classify_evaluation_exception(
            ValueError("Vertex returned an empty structured response")
        )
        self.assertTrue(retryable)
        self.assertIn("unparsable", category)

    def test_classify_terminal_non_retryable_exceptions(self):
        # KeyError, TypeError, generic ValueError
        exc_key = KeyError("missing_field")
        retryable, category = classify_evaluation_exception(exc_key)
        self.assertFalse(retryable)
        self.assertIsNone(category)

        exc_type = TypeError("unsupported operand type")
        retryable, category = classify_evaluation_exception(exc_type)
        self.assertFalse(retryable)
        self.assertIsNone(category)

        exc_val = ValueError("Invalid case format for question")
        retryable, category = classify_evaluation_exception(exc_val)
        self.assertFalse(retryable)
        self.assertIsNone(category)

    def test_classify_serialized_records(self):
        # Serialized dict record with 429
        rec_retryable = {
            "id": "g013",
            "exception": {
                "type": "VertexCallError",
                "message": "429 RESOURCE_EXHAUSTED: quota exceeded",
            },
        }
        self.assertEqual(evaluation_record_state(rec_retryable), "retryable_exception")

        # Serialized dict record with KeyError
        rec_terminal = {
            "id": "g014",
            "exception": {
                "type": "KeyError",
                "message": "'target'",
            },
        }
        self.assertEqual(evaluation_record_state(rec_terminal), "terminal_exception")

        # Completed successful record
        rec_completed = {
            "id": "g001",
            "result": {"status": "answered", "answer": "text"},
            "metrics": {"answer_point_coverage": 1.0},
        }
        self.assertEqual(evaluation_record_state(rec_completed), "completed")


class ExecutionRecoveryRunStoreTests(unittest.TestCase):
    def _base_manifest(self):
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

    def test_success_unchanged_on_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest()
            store = EvaluationRunStore(root, "run-1", manifest)

            # Record a successful case
            success_rec = {
                "id": "g001",
                "result": {"status": "answered", "answer": "Good"},
                "model_calls": 5,
                "token_usage": 1000,
            }
            store.record(success_rec)

            # On resume with same manifest
            resumed_store = EvaluationRunStore(root, "run-1", manifest, resume=True)
            self.assertIn("g001", resumed_store.completed_ids)
            self.assertIn("g001", resumed_store.successful_ids)
            self.assertNotIn("g001", resumed_store.retryable_ids)

    def test_retryable_exception_resumable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest()
            store = EvaluationRunStore(root, "run-2", manifest)

            # Record a retryable exception case
            retryable_rec = {
                "id": "g013",
                "exception": {
                    "type": "VertexCallError",
                    "message": "429 RESOURCE_EXHAUSTED",
                },
                "model_calls": 2,
                "token_usage": 500,
            }
            store.record(retryable_rec)

            # On resume, g013 should NOT be in completed_ids, but in retryable_ids
            resumed_store = EvaluationRunStore(root, "run-2", manifest, resume=True)
            self.assertNotIn("g013", resumed_store.completed_ids)
            self.assertIn("g013", resumed_store.retryable_ids)

    def test_terminal_nonretryable_not_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest()
            store = EvaluationRunStore(root, "run-3", manifest)

            # Record a terminal non-retryable exception case
            terminal_rec = {
                "id": "g099",
                "exception": {
                    "type": "KeyError",
                    "message": "unexpected missing schema key",
                },
                "model_calls": 1,
                "token_usage": 100,
            }
            store.record(terminal_rec)

            # On resume, g099 should be in completed_ids (should NOT be retried)
            resumed_store = EvaluationRunStore(root, "run-3", manifest, resume=True)
            self.assertIn("g099", resumed_store.completed_ids)
            self.assertIn("g099", resumed_store.terminal_exception_ids)
            self.assertNotIn("g099", resumed_store.retryable_ids)

    def test_retry_one_failed_without_duplicate_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest()
            store = EvaluationRunStore(root, "run-4", manifest)

            # Step 1: Record 1 success and 1 retryable failure
            store.record({
                "id": "g001",
                "result": {"status": "answered"},
                "model_calls": 3,
                "token_usage": 1000,
            })
            store.record({
                "id": "g013",
                "exception": {"type": "VertexCallError", "message": "429 RESOURCE_EXHAUSTED"},
                "model_calls": 2,
                "token_usage": 500,
            })

            # Step 2: Resume and retry g013 with success
            resumed_store = EvaluationRunStore(root, "run-4", manifest, resume=True)
            resumed_store.record({
                "id": "g013",
                "result": {"status": "answered"},
                "model_calls": 4,
                "token_usage": 1200,
            })

            # Check results.jsonl contains exactly 2 lines (no duplicate g013!)
            results_lines = (resumed_store.results_path.read_text(encoding="utf-8").strip().splitlines())
            self.assertEqual(len(results_lines), 2)
            parsed = [json.loads(line) for line in results_lines]
            ids = [p["id"] for p in parsed]
            self.assertEqual(sorted(ids), ["g001", "g013"])
            self.assertEqual(len(ids), len(set(ids)), "results.jsonl must have no duplicate IDs")

            # The current record for g013 must be the success record
            g013_current = next(p for p in parsed if p["id"] == "g013")
            self.assertIsNone(g013_current.get("exception"))
            self.assertEqual(g013_current["result"]["status"], "answered")

    def test_multiple_failed_attempt_usage_recoverable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest()
            store = EvaluationRunStore(root, "run-5", manifest)

            # Attempt 1: g013 fails (2 calls, 500 tokens)
            store.record({
                "id": "g013",
                "exception": {"type": "VertexCallError", "message": "429 RESOURCE_EXHAUSTED"},
                "model_calls": 2,
                "token_usage": 500,
            })

            # Resume 1: g013 fails again (3 calls, 800 tokens)
            store_r1 = EvaluationRunStore(root, "run-5", manifest, resume=True)
            store_r1.record({
                "id": "g013",
                "exception": {"type": "VertexCallError", "message": "429 RESOURCE_EXHAUSTED"},
                "model_calls": 3,
                "token_usage": 800,
            })

            # Resume 2: g013 succeeds (4 calls, 1200 tokens)
            store_r2 = EvaluationRunStore(root, "run-5", manifest, resume=True)
            store_r2.record({
                "id": "g013",
                "result": {"status": "answered"},
                "model_calls": 4,
                "token_usage": 1200,
            })

            # All 3 attempts must be preserved in attempts ledger
            attempts_path = store_r2.run_dir / "attempts.jsonl"
            self.assertTrue(attempts_path.exists())
            attempt_lines = attempts_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(attempt_lines), 3)

            # Cumulative accounting should recover all 3 attempts:
            # Calls: 2 + 3 + 4 = 9 calls
            # Tokens: 500 + 800 + 1200 = 2500 tokens
            total_calls, total_tokens = store_r2.cumulative_usage()
            self.assertEqual(total_calls, 9)
            self.assertEqual(total_tokens, 2500)


class IdentityResumeGapTests(unittest.TestCase):
    def _base_manifest(self):
        return {
            "schema_version": "1.0",
            "mode": "full",
            "split": "dev",
            "official": True,
            "candidate_id": "f6a-rc3-20260914",
            "prompt_hash": "a" * 64,
            "gold_dataset_hash": "b" * 64,
            "index_identity": "c" * 64,
            "repository_identity": {"commit": "1111111", "dirty": False},
        }

    @patch("panda_agent.evaluation.subprocess.run")
    @patch("panda_agent.evaluation.verify_candidate_identity")
    def test_lifecycle_only_commit_change_allowed_under_verified_candidate(self, mock_verify, mock_sub):
        mock_sub.return_value = MagicMock(returncode=0)
        mock_verify.return_value = {"candidate_id": "f6a-rc3-20260914", "valid": True, "mismatches": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_manifest = self._base_manifest()
            store = EvaluationRunStore(root, "run-id-gap", old_manifest)

            # New manifest has only repository_identity.commit advanced (e.g. documentation/pause commit)
            new_manifest = self._base_manifest()
            new_manifest["repository_identity"] = {"commit": "2222222", "dirty": False}

            # With candidate verification passing, resume should succeed
            resumed = EvaluationRunStore(
                root,
                "run-id-gap",
                new_manifest,
                resume=True,
                project_root=Path.cwd(),
            )
            self.assertIsNotNone(resumed)

    @patch("panda_agent.evaluation.verify_candidate_identity")
    def test_real_identity_drift_fails_closed(self, mock_verify):
        mock_verify.return_value = {"candidate_id": "f6a-rc3-20260914", "valid": True, "mismatches": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_manifest = self._base_manifest()
            store = EvaluationRunStore(root, "run-id-drift", old_manifest)

            # 1. Prompt hash changed
            drifted_prompt = self._base_manifest()
            drifted_prompt["prompt_hash"] = "z" * 64
            with self.assertRaises(ValueError):
                EvaluationRunStore(root, "run-id-drift", drifted_prompt, resume=True)

            # 2. Candidate verification failed
            mock_verify.return_value = {
                "candidate_id": "f6a-rc3-20260914",
                "valid": False,
                "mismatches": ["source_tree_hash"],
            }
            new_commit_manifest = self._base_manifest()
            new_commit_manifest["repository_identity"] = {"commit": "3333333", "dirty": False}
            with self.assertRaises(ValueError):
                EvaluationRunStore(
                    root,
                    "run-id-drift",
                    new_commit_manifest,
                    resume=True,
                    project_root=Path.cwd(),
                )


class StageFinalizationReceiptTimingTests(unittest.TestCase):
    def test_receipt_before_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evaluation").mkdir(parents=True, exist_ok=True)
            (root / "evaluation" / "gold_questions.yaml").write_bytes(
                (Path.cwd() / "evaluation" / "gold_questions.yaml").read_bytes()
            )
            run_dir = root / "data" / "evaluation" / "runs" / "test-run"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "full",
                "split": "dev",
                "official": True,
                "candidate_id": "f6a-rc3-20260914",
                "repository_identity": {"commit": "1111111", "dirty": False},
                "case_ids": ["g001"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (run_dir / "results.jsonl").write_text(
                json.dumps({"id": "g001", "result": {"status": "answered"}}) + "\n",
                encoding="utf-8",
            )
            records = [{"id": "g001", "result": {"status": "answered"}}]

            # When finalize_stage_evaluation runs, stage_receipt.json must exist
            # before report.md is generated
            receipt_path = run_dir / "stage_receipt.json"
            report_path = run_dir / "report.md"

            # Finalize
            finalize_stage_evaluation(
                project_root=root,
                run_id="test-run",
                metrics={"gold_recall_at_10": 1.0},
                gate={"passed": True, "checks": {}},
                records=records,
            )

            self.assertTrue(receipt_path.exists(), "stage_receipt.json must be created")
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["schema_version"], "stage-receipt-v1")
            self.assertIn("case_id_set_sha256", receipt["artifacts_and_hashes"])


class CohortCompletenessDecisionRuleTests(unittest.TestCase):
    def test_incomplete_with_retryable_is_recovery_pending(self):
        records = [
            {"id": "g001", "result": {"status": "answered"}},
            {"id": "g013", "exception": {"type": "VertexCallError", "message": "429 RESOURCE_EXHAUSTED"}},
        ]
        decision = evaluate_cohort_decision(
            records=records,
            expected_case_ids={"g001", "g013"},
            candidate_valid=True,
            gates_passed=False,  # e.g. 3 mandatory metrics failed
        )
        # MUST NOT be complete PASS or terminal FAIL!
        self.assertEqual(decision["status"], "INCOMPLETE")
        self.assertEqual(decision["verdict"], "RECOVERY_PENDING")
        self.assertIsNone(decision["passed"])

    def test_incomplete_unrecoverable_is_inconclusive(self):
        records = [
            {"id": "g001", "result": {"status": "answered"}},
            {"id": "g013", "exception": {"type": "VertexCallError", "message": "429 RESOURCE_EXHAUSTED"}},
        ]
        decision = evaluate_cohort_decision(
            records=records,
            expected_case_ids={"g001", "g013"},
            candidate_valid=False,  # cannot reproduce frozen candidate
            gates_passed=False,
        )
        self.assertEqual(decision["status"], "INCOMPLETE")
        self.assertEqual(decision["verdict"], "INCONCLUSIVE")
        self.assertIsNone(decision["passed"])

    def test_complete_cohort_can_pass_or_fail(self):
        records_pass = [
            {"id": "g001", "result": {"status": "answered"}},
            {"id": "g013", "result": {"status": "answered"}},
        ]
        pass_dec = evaluate_cohort_decision(
            records=records_pass,
            expected_case_ids={"g001", "g013"},
            candidate_valid=True,
            gates_passed=True,
        )
        self.assertEqual(pass_dec["status"], "COMPLETE")
        self.assertEqual(pass_dec["verdict"], "PASS")
        self.assertTrue(pass_dec["passed"])

        fail_dec = evaluate_cohort_decision(
            records=records_pass,
            expected_case_ids={"g001", "g013"},
            candidate_valid=True,
            gates_passed=False,
        )
        self.assertEqual(fail_dec["status"], "COMPLETE")
        self.assertEqual(fail_dec["verdict"], "FAIL")
        self.assertFalse(fail_dec["passed"])


class RunnerAndCliIntegrationRecoveryTests(unittest.TestCase):
    def test_report_evaluation_generates_stage_receipt_before_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-runner-run"
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
                "result": {"status": "answered", "answer": "text"},
                "metrics": {
                    "answer_point_coverage": 1.0,
                    "gold_recall_at_10": 1.0,
                    "final_evidence_recall": 1.0,
                    "critical_final_evidence_recall": 1.0,
                    "expected_status_correct": True,
                    "intent_correct": True,
                    "citation_integrity": 1.0,
                },
                "model_calls": 2,
                "token_usage": 300,
            }
            (run_dir / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
            (run_dir / "records").mkdir()
            (run_dir / "records" / "g001.json").write_text(json.dumps(record), encoding="utf-8")

            from panda_agent.evaluation_runner import report_evaluation

            report = report_evaluation(root, "test-runner-run")
            self.assertIn("stage_receipt", report)
            receipt_file = run_dir / "stage_receipt.json"
            self.assertTrue(receipt_file.exists())
            receipt_data = json.loads(receipt_file.read_text(encoding="utf-8"))
            self.assertEqual(receipt_data["schema_version"], "stage-receipt-v1")
            self.assertEqual(receipt_data["artifacts_and_hashes"]["record_count"], 1)

    def test_write_failure_review_ensures_stage_receipt_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-review-run"
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

            from panda_agent.evaluation_runner import write_failure_review

            result = write_failure_review(root, "test-review-run")
            self.assertTrue(result["created"])
            # stage_receipt.json MUST have been generated!
            self.assertTrue((run_dir / "stage_receipt.json").exists())

    def test_cli_receipt_command_outputs_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evaluation").mkdir(parents=True, exist_ok=True)
            (root / "evaluation" / "gold_questions.yaml").write_bytes(
                (Path.cwd() / "evaluation" / "gold_questions.yaml").read_bytes()
            )
            run_dir = root / "data" / "evaluation" / "runs" / "test-cli-run"
            run_dir.mkdir(parents=True)
            manifest = {"schema_version": "1.0", "mode": "qa", "split": "dev", "case_ids": ["g001"]}
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (run_dir / "results.jsonl").write_text(
                json.dumps({"id": "g001", "result": {"status": "answered"}}) + "\n",
                encoding="utf-8",
            )

            import io
            import sys
            from panda_agent.cli.evaluate import main

            old_argv = sys.argv
            old_stdout = sys.stdout
            try:
                sys.stdout = buffer = io.StringIO()
                sys.argv = ["panda-qa-eval", "--project-root", str(root), "receipt", "--run-id", "test-cli-run"]
                main()
                output = buffer.getvalue()
                parsed = json.loads(output)
                self.assertEqual(parsed["schema_version"], "stage-receipt-v1")
            finally:
                sys.argv = old_argv
                sys.stdout = old_stdout


class PostA3AcceptanceBugRedTests(unittest.TestCase):
    def _base_manifest(self):
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

    def test_legacy_run_seeds_attempts_ledger_before_mutation(self):
        """Bug 1: Legacy run without attempts.jsonl must seed prior attempts so cumulative usage is preserved."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest()
            store = EvaluationRunStore(root, "legacy-run-1", manifest)

            # Record 2 cases in initial legacy run
            store.record({
                "id": "g001",
                "result": {"status": "answered"},
                "model_calls": 5,
                "token_usage": 1000,
            })
            store.record({
                "id": "g002",
                "exception": {"type": "VertexCallError", "message": "429 RESOURCE_EXHAUSTED"},
                "model_calls": 3,
                "token_usage": 600,
            })

            # Simulate legacy run state by removing attempts.jsonl
            if store.attempts_path.exists():
                store.attempts_path.unlink()
            self.assertFalse(store.attempts_path.exists())

            # Now resume and retry g002
            resumed = EvaluationRunStore(root, "legacy-run-1", manifest, resume=True)
            resumed.record({
                "id": "g002",
                "result": {"status": "answered"},
                "model_calls": 4,
                "token_usage": 800,
            })

            # The attempts ledger must exist and contain all 3 attempts (g001 initial, g002 initial, g002 retry)
            self.assertTrue(resumed.attempts_path.exists())
            attempt_lines = [
                json.loads(line)
                for line in resumed.attempts_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(attempt_lines), 3)

            # Cumulative usage must be 5 + 3 + 4 = 12 calls, 1000 + 600 + 800 = 2400 tokens
            calls, tokens = resumed.cumulative_usage()
            self.assertEqual(calls, 12)
            self.assertEqual(tokens, 2400)

    def test_stage_receipt_lifecycle_immutability_and_pending_guard(self):
        """Bug 2: create_stage_receipt must refuse to seal while RECOVERY_PENDING, and must not overwrite mismatched receipt."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evaluation").mkdir(parents=True, exist_ok=True)
            (root / "evaluation" / "gold_questions.yaml").write_bytes(
                (Path.cwd() / "evaluation" / "gold_questions.yaml").read_bytes()
            )
            run_dir = root / "data" / "evaluation" / "runs" / "pending-run"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001", "g002"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            # Only g001 is recorded; g002 is missing -> RECOVERY_PENDING
            (run_dir / "results.jsonl").write_text(
                json.dumps({"id": "g001", "result": {"status": "answered"}}) + "\n",
                encoding="utf-8",
            )
            records = [{"id": "g001", "result": {"status": "answered"}}]

            # Refuse to seal stage_receipt.json while recovery is pending!
            with self.assertRaises(ValueError):
                create_stage_receipt(
                    root,
                    "pending-run",
                    records=records,
                    gate={"passed": None},
                )

            # Now test complete cohort: can be sealed
            records_complete = [
                {"id": "g001", "result": {"status": "answered"}},
                {"id": "g002", "result": {"status": "answered"}},
            ]
            receipt1 = create_stage_receipt(
                root,
                "pending-run",
                records=records_complete,
                gate={"passed": True},
            )
            self.assertTrue((run_dir / "stage_receipt.json").exists())

            # Repeated call with identical state is idempotent
            receipt2 = create_stage_receipt(
                root,
                "pending-run",
                records=records_complete,
                gate={"passed": True},
            )
            self.assertEqual(receipt1["execution_status"], receipt2["execution_status"])

            # Overwriting existing receipt with mismatched content must raise ValueError
            with self.assertRaises(ValueError):
                create_stage_receipt(
                    root,
                    "pending-run",
                    records=records_complete,
                    gate={"passed": False},  # Mismatched gate!
                )

    def test_expected_ids_and_gate_measurement_none_contract(self):
        """Bug 3: Normal run without manifest case_ids must derive expected cases from dataset, not fall back to observed.
        Also missing gate measurement None must not become FAIL, and duplicate records rejected."""
        from panda_agent.evaluation_finalization import resolve_expected_case_ids

        project_root = Path.cwd()
        manifest_normal = {
            "mode": "qa",
            "split": "dev",
            "limit": 5,
            "case_ids": None,
        }
        expected = resolve_expected_case_ids(project_root, manifest_normal)
        self.assertEqual(len(expected), 5)

        # 2 observed records out of 5 expected -> must be INCOMPLETE / RECOVERY_PENDING, not COMPLETE
        partial_records = [
            {"id": expected[0], "result": {"status": "answered"}},
            {"id": expected[1], "result": {"status": "answered"}},
        ]
        decision = evaluate_cohort_decision(
            records=partial_records,
            expected_case_ids=expected,
            candidate_valid=True,
            gates_passed=True,
        )
        self.assertEqual(decision["status"], "INCOMPLETE")
        self.assertEqual(decision["verdict"], "RECOVERY_PENDING")
        self.assertEqual(len(decision["missing_case_ids"]), 3)

        # Complete cohort with gates_passed=None -> verdict must be INCOMPLETE, NOT FAIL!
        complete_records = [{"id": cid, "result": {"status": "answered"}} for cid in expected]
        decision_none = evaluate_cohort_decision(
            records=complete_records,
            expected_case_ids=expected,
            candidate_valid=True,
            gates_passed=None,
        )
        self.assertEqual(decision_none["verdict"], "INCOMPLETE")
        self.assertIsNone(decision_none["passed"])

        # Duplicate records must be rejected
        dup_records = complete_records + [complete_records[0]]
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(
                records=dup_records,
                expected_case_ids=expected,
            )

    def test_candidate_binding_and_historical_runs(self):
        """Bug 4: Do not hardcode candidate_valid=True. Unknown historical runs must fail closed (INCONCLUSIVE).
        Receipt must bind manifest and gate hashes."""
        # When candidate is invalid / unknown on incomplete run, verdict is INCONCLUSIVE
        decision = evaluate_cohort_decision(
            records=[{"id": "g001", "result": {"status": "answered"}}],
            expected_case_ids=["g001", "g002"],
            candidate_valid=False,
        )
        self.assertEqual(decision["verdict"], "INCONCLUSIVE")
        self.assertEqual(decision["status"], "INCOMPLETE")

    def test_exception_classification_permanent_vs_transient(self):
        """Bug 5: 401/403/400/InvalidArgument must be permanent; token 500 must not match arbitrary numbers."""
        # Permanent errors in VertexCallError
        exc_401 = VertexCallError("POST failed: 401 UNAUTHENTICATED: API key invalid")
        retryable, cat = classify_evaluation_exception(exc_401)
        self.assertFalse(retryable)
        self.assertIsNone(cat)

        exc_403 = VertexCallError("POST failed: 403 PERMISSION_DENIED: Access denied")
        retryable, cat = classify_evaluation_exception(exc_403)
        self.assertFalse(retryable)
        self.assertIsNone(cat)

        exc_400 = VertexCallError("POST failed: 400 INVALID_ARGUMENT: Bad request parameters")
        retryable, cat = classify_evaluation_exception(exc_400)
        self.assertFalse(retryable)
        self.assertIsNone(cat)

        # Message with number containing '500' (e.g. top_k=500 or 5000) is NOT a 500 server error
        exc_num = ValueError("Parsed 500 items from catalog")
        retryable, cat = classify_evaluation_exception(exc_num)
        self.assertFalse(retryable)

        # Real 500 Internal Server Error IS retryable
        exc_500 = VertexCallError("POST failed: 500 Internal Server Error: backend crash")
        retryable, cat = classify_evaluation_exception(exc_500)
        self.assertTrue(retryable)
        self.assertIn("transport_provider", cat)

        # Serialized record compatibility
        rec_403 = {"type": "VertexCallError", "message": "403 PERMISSION_DENIED"}
        self.assertEqual(evaluation_record_state({"id": "x", "exception": rec_403}), "terminal_exception")

    def test_corrupt_record_file_fails_visibly(self):
        """Bug 6: A corrupted record file in records/ must fail visibly with ValueError, not pass silently."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._base_manifest()
            run_dir = root / "corrupt-run"
            records_dir = run_dir / "records"
            records_dir.mkdir(parents=True)
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (records_dir / "g001.json").write_text("{this is corrupted json\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                EvaluationRunStore(root, "corrupt-run", manifest, resume=True)

    def test_resume_rejects_non_ancestor_commit_advance(self):
        """Bug 7: Manifest resume must verify old->new commit ancestry and fail closed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_manifest = self._base_manifest()
            old_manifest["candidate_id"] = "f6a-rc3-20260914"
            store = EvaluationRunStore(root, "run-ancestry", old_manifest)

            new_manifest = dict(old_manifest)
            new_manifest["repository_identity"] = {"commit": "unrelated_branch_commit", "dirty": False}

            with patch("subprocess.run") as mock_sub:
                # git merge-base --is-ancestor returns non-zero when not an ancestor
                mock_res = MagicMock()
                mock_res.returncode = 1
                mock_sub.return_value = mock_res

                with self.assertRaises(ValueError) as ctx:
                    EvaluationRunStore(root, "run-ancestry", new_manifest, resume=True, project_root=Path.cwd())
                self.assertIn("ancestor", str(ctx.exception).lower())

    def test_run_status_and_report_guard_recovery_pending(self):
        """Bug 8: report_evaluation and run_status must reflect RECOVERY_PENDING and guard premature failure reviews."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "pending-report-run"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "full",
                "split": "dev",
                "official": False,
                "gold_dataset_path": str(Path.cwd() / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"),
                "case_ids": ["g001", "g002"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            # Only g001 is present
            record = {
                "id": "g001",
                "intent": "usage",
                "split": "dev",
                "language": "en",
                "expected_status": "answered",
                "result": {"status": "answered", "answer": "text"},
                "metrics": {
                    "answer_point_coverage": 1.0,
                    "gold_recall_at_10": 1.0,
                    "final_evidence_recall": 1.0,
                    "critical_final_evidence_recall": 1.0,
                    "expected_status_correct": True,
                    "intent_correct": True,
                    "citation_integrity": 1.0,
                },
                "model_calls": 2,
                "token_usage": 300,
            }
            (run_dir / "records").mkdir()
            (run_dir / "records" / "g001.json").write_text(json.dumps(record), encoding="utf-8")
            (run_dir / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

            from panda_agent.evaluation_runner import report_evaluation

            report = report_evaluation(root, "pending-report-run")
            # Must reflect cohort decision
            self.assertEqual(report["cohort_decision"]["status"], "INCOMPLETE")
            self.assertEqual(report["cohort_decision"]["verdict"], "RECOVERY_PENDING")
            # stage_receipt.json must NOT be created for pending run
            self.assertFalse((run_dir / "stage_receipt.json").exists())
            # failure_review must NOT be generated for pending run
            self.assertNotIn("failure_review", report)


if __name__ == "__main__":
    unittest.main()
