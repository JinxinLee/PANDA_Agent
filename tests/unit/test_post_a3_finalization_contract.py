"""Contract tests for post-A3 stage finalization and gate evaluation.

Verifies:
1. resolve_expected_case_ids fails closed on missing declared dataset or hash mismatch,
   while explicit case_ids remain usable for fixtures without declared datasets.
2. resolve_candidate_binding compares stored manifest hash with verified hash and
   never guesses directories; candidate manifest supplies implementation commit.
3. evaluate_cohort_decision validates usable records by mode, rejects extras/duplicates/empty,
   preserves tri-state gate measurement (None), and ensures invalid candidate cannot PASS.
4. create_stage_receipt compares ALL immutable bound fields on repeat and reads persisted
   gate/metrics when arguments are omitted.
5. validate_stage_receipt catches edits to records contents, candidate, manifest, gates,
   traces, and usage (not just IDs/results).
6. f6a_gate_evaluation preserves None and INCONCLUSIVE, suppresses details when pending,
   seals receipt before output/printing, and uses forward-only receipt with --source-matrix.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from panda_agent.evaluation_finalization import (
    create_stage_receipt,
    evaluate_cohort_decision,
    finalize_stage_evaluation,
    resolve_candidate_binding,
    resolve_expected_case_ids,
    validate_stage_receipt,
)


class ExpectedCaseIdsContractTests(unittest.TestCase):
    def test_missing_declared_gold_dataset_fails_closed(self):
        manifest = {
            "gold_dataset_path": "nonexistent/gold.yaml",
            "case_ids": ["g001"],
        }
        with self.assertRaises(FileNotFoundError):
            resolve_expected_case_ids(Path.cwd(), manifest)

    def test_declared_dataset_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_file = root / "gold.yaml"
            data_file.write_text("questions: []\n", encoding="utf-8")
            manifest = {
                "gold_dataset_path": str(data_file),
                "gold_dataset_hash": "deadbeef" * 8,
                "case_ids": ["g001"],
            }
            with self.assertRaises(ValueError) as ctx:
                resolve_expected_case_ids(root, manifest)
            self.assertIn("mismatch", str(ctx.exception).lower())

    def test_explicit_case_ids_usable_without_declared_dataset(self):
        manifest = {
            "split": "dev",
            "case_ids": ["g001", "g002"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # evaluation/gold_questions.yaml does not exist in root
            ids = resolve_expected_case_ids(root, manifest)
            self.assertEqual(ids, ["g001", "g002"])

    def test_missing_dataset_fails_closed_when_case_ids_omitted(self):
        manifest = {
            "split": "dev",
            "case_ids": None,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(FileNotFoundError):
                resolve_expected_case_ids(root, manifest)


class CandidateBindingContractTests(unittest.TestCase):
    def test_official_run_without_candidate_id_fails_closed(self):
        manifest = {"official": True, "split": "dev"}
        cid, digest, valid = resolve_candidate_binding(Path.cwd(), manifest)
        self.assertIsNone(cid)
        self.assertIsNone(digest)
        self.assertFalse(valid)

    def test_non_official_run_without_candidate_id_is_dev_usable(self):
        manifest = {"official": False, "split": "dev"}
        cid, digest, valid = resolve_candidate_binding(Path.cwd(), manifest)
        self.assertIsNone(cid)
        self.assertIsNone(digest)
        self.assertIsNone(valid)

        # Dev usability: evaluate_cohort_decision must allow candidate_valid=None to PASS when complete
        records = [{"id": "g001", "result": {"status": "answered"}}]
        dec = evaluate_cohort_decision(
            records=records,
            expected_case_ids=["g001"],
            candidate_valid=valid,
            gates_passed=True,
        )
        self.assertEqual(dec["verdict"], "PASS")

    def test_candidate_manifest_hash_mismatch_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "official": True,
                "candidate_id": "cand-1",
                "candidate_manifest_sha256": "expected_hash_value",
            }
            with patch("panda_agent.candidate.verify_candidate") as mock_vc:
                mock_vc.return_value = {
                    "valid": True,
                    "manifest_sha256": "different_hash_value",
                }
                cid, digest, valid = resolve_candidate_binding(root, manifest)
                self.assertEqual(cid, "cand-1")
                self.assertEqual(digest, "different_hash_value")
                self.assertFalse(valid)


class EvaluateCohortDecisionContractTests(unittest.TestCase):
    def test_reject_empty_records_and_empty_expected_ids(self):
        # Empty records with nonempty expected is legitimate budget stop -> INCOMPLETE / RECOVERY_PENDING
        stop_dec = evaluate_cohort_decision(records=[], expected_case_ids=["g001"])
        self.assertEqual(stop_dec["status"], "INCOMPLETE")
        self.assertEqual(stop_dec["verdict"], "RECOVERY_PENDING")
        self.assertIsNone(stop_dec["passed"])
        self.assertEqual(stop_dec["missing_case_ids"], ["g001"])

        # Empty records with invalid candidate is INCONCLUSIVE, never PASS
        inconclusive_dec = evaluate_cohort_decision(
            records=[],
            expected_case_ids=["g001"],
            candidate_valid=False,
        )
        self.assertEqual(inconclusive_dec["status"], "INCOMPLETE")
        self.assertEqual(inconclusive_dec["verdict"], "INCONCLUSIVE")
        self.assertEqual(inconclusive_dec["decision_reason"], "INVALID_CANDIDATE_IDENTITY")

        # Empty expected must still be rejected
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(records=[], expected_case_ids=[])
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(
                records=[{"id": "g001", "result": {"status": "answered"}}],
                expected_case_ids=[],
            )

    def test_reject_duplicate_and_extra_case_ids(self):
        # Duplicates
        records = [
            {"id": "g001", "result": {"status": "answered"}},
            {"id": "g001", "result": {"status": "answered"}},
        ]
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(records=records, expected_case_ids=["g001"])

        # Extras
        records_extra = [
            {"id": "g001", "result": {"status": "answered"}},
            {"id": "g002", "result": {"status": "answered"}},
        ]
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(records=records_extra, expected_case_ids=["g001"])

    def test_reject_invalid_usable_mode_records(self):
        # Missing status in qa mode
        records_no_status = [
            {"id": "g001", "result": {"answer": "something without status"}},
        ]
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(
                records=records_no_status,
                expected_case_ids=["g001"],
                mode="qa",
            )

        # Illegal status in qa mode
        records_bogus_status = [
            {"id": "g001", "result": {"status": "bogus_status"}},
        ]
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(
                records=records_bogus_status,
                expected_case_ids=["g001"],
                mode="qa",
            )

        # Mode qa/full requires result dict; metrics alone is invalid
        records_metrics_only = [
            {"id": "g001", "metrics": {"gold_recall_at_10": 1.0}},
        ]
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(
                records=records_metrics_only,
                expected_case_ids=["g001"],
                mode="qa",
            )
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(
                records=records_metrics_only,
                expected_case_ids=["g001"],
                mode="full",
            )

        # Missing mode: backward compatible ordinary fixtures with metrics only are accepted
        compat_dec = evaluate_cohort_decision(
            records=records_metrics_only,
            expected_case_ids=["g001"],
            mode=None,
            gates_passed=True,
        )
        self.assertEqual(compat_dec["verdict"], "PASS")

        # Legal QAStatus is accepted in qa mode
        records_legal = [
            {"id": "g001", "result": {"status": "answered"}},
        ]
        qa_dec = evaluate_cohort_decision(
            records=records_legal,
            expected_case_ids=["g001"],
            mode="qa",
            gates_passed=True,
        )
        self.assertEqual(qa_dec["verdict"], "PASS")

        # Neither result nor metrics nor exception
        records_empty = [{"id": "g001"}]
        with self.assertRaises(ValueError):
            evaluate_cohort_decision(
                records=records_empty,
                expected_case_ids=["g001"],
            )

    def test_invalid_candidate_cannot_pass(self):
        records = [{"id": "g001", "result": {"status": "answered"}}]
        dec = evaluate_cohort_decision(
            records=records,
            expected_case_ids=["g001"],
            candidate_valid=False,
            gates_passed=True,
        )
        self.assertEqual(dec["verdict"], "INCONCLUSIVE")
        self.assertIsNone(dec["passed"])
        self.assertEqual(dec["decision_reason"], "INVALID_CANDIDATE_IDENTITY")

    def test_missing_gate_measurement_preserves_none_and_incomplete(self):
        records = [{"id": "g001", "result": {"status": "answered"}}]
        dec = evaluate_cohort_decision(
            records=records,
            expected_case_ids=["g001"],
            candidate_valid=True,
            gates_passed=None,
        )
        self.assertEqual(dec["status"], "COMPLETE")
        self.assertEqual(dec["verdict"], "INCOMPLETE")
        self.assertIsNone(dec["passed"])


class StageReceiptLifecycleContractTests(unittest.TestCase):
    def _create_run_dir(self, root: Path, run_id: str, case_ids: list[str]) -> Path:
        run_dir = root / "data" / "evaluation" / "runs" / run_id
        run_dir.mkdir(parents=True)
        manifest = {
            "schema_version": "1.0",
            "mode": "qa",
            "split": "dev",
            "case_ids": case_ids,
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        records = [{"id": cid, "result": {"status": "answered"}} for cid in case_ids]
        (run_dir / "results.jsonl").write_text(
            "\n".join(json.dumps(r) for r in records) + "\n",
            encoding="utf-8",
        )
        return run_dir

    def test_create_receipt_reads_persisted_gate_and_metrics_when_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = self._create_run_dir(root, "run-persisted", ["g001"])
            (run_dir / "gate.json").write_text(json.dumps({"passed": True}), encoding="utf-8")
            (run_dir / "metrics.json").write_text(json.dumps({"acc": 1.0}), encoding="utf-8")

            # Call create_stage_receipt without gate or metrics args
            receipt = create_stage_receipt(root, "run-persisted")
            self.assertTrue(receipt["gate_summary"]["passed"])
            self.assertEqual(receipt["execution_status"]["decision"], "PASS")

    def test_receipt_commit_derived_from_candidate_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cand_dir = root / "evaluation" / "candidates" / "cand-x"
            cand_dir.mkdir(parents=True)
            cand_manifest = {
                "candidate_id": "cand-x",
                "implementation_git_commit": "candidate_commit_abc123",
            }
            (cand_dir / "candidate_manifest.json").write_text(
                json.dumps(cand_manifest), encoding="utf-8"
            )

            run_dir = root / "data" / "evaluation" / "runs" / "run-cand"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
                "candidate_id": "cand-x",
                "repository_identity": {"commit": "repo_head_different"},
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (run_dir / "results.jsonl").write_text(
                json.dumps({"id": "g001", "result": {"status": "answered"}}) + "\n",
                encoding="utf-8",
            )

            with patch("panda_agent.candidate.verify_candidate") as mock_vc:
                mock_vc.return_value = {"valid": True, "manifest_sha256": "digest123"}
                receipt = create_stage_receipt(root, "run-cand", gate={"passed": True})
                self.assertEqual(
                    receipt["identities"]["implementation_git_commit"],
                    "candidate_commit_abc123",
                )

    def test_repeat_call_compares_all_immutable_bound_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = self._create_run_dir(root, "run-repeat", ["g001"])
            receipt1 = create_stage_receipt(root, "run-repeat", gate={"passed": True})

            # Exact repeat succeeds
            receipt2 = create_stage_receipt(root, "run-repeat", gate={"passed": True})
            self.assertEqual(receipt1["artifacts_and_hashes"], receipt2["artifacts_and_hashes"])

            # Mutating gate raises ValueError
            with self.assertRaises(ValueError):
                create_stage_receipt(root, "run-repeat", gate={"passed": False})

            # Mutating records content raises ValueError
            with self.assertRaises(ValueError):
                create_stage_receipt(
                    root,
                    "run-repeat",
                    gate={"passed": True},
                    records=[{"id": "g001", "result": {"status": "different_answer"}}],
                )


class ValidateStageReceiptContractTests(unittest.TestCase):
    def test_validate_detects_tampered_record_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "run-tamper"
            run_dir.mkdir(parents=True)
            manifest = {"schema_version": "1.0", "mode": "qa", "split": "dev", "case_ids": ["g001"]}
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            records_dir = run_dir / "records"
            records_dir.mkdir()
            rec1 = {"id": "g001", "result": {"status": "answered", "answer": "orig"}}
            (records_dir / "g001.json").write_text(json.dumps(rec1), encoding="utf-8")
            (run_dir / "results.jsonl").write_text(json.dumps(rec1) + "\n", encoding="utf-8")

            create_stage_receipt(root, "run-tamper", gate={"passed": True})
            # Valid receipt validates
            self.assertIsNotNone(validate_stage_receipt(root, "run-tamper"))

            # Tamper with record content in records/g001.json
            rec_tampered = {"id": "g001", "result": {"status": "answered", "answer": "tampered"}}
            (records_dir / "g001.json").write_text(json.dumps(rec_tampered), encoding="utf-8")

            with self.assertRaises(ValueError):
                validate_stage_receipt(root, "run-tamper")

    def test_validate_detects_tampered_manifest_gate_traces_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "run-tamper2"
            run_dir.mkdir(parents=True)
            manifest = {"schema_version": "1.0", "mode": "qa", "split": "dev", "case_ids": ["g001"]}
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (run_dir / "gate.json").write_text(json.dumps({"passed": True}), encoding="utf-8")
            (run_dir / "retrieval_traces.jsonl").write_text(json.dumps({"id": "g001", "trace": []}) + "\n", encoding="utf-8")
            (run_dir / "results.jsonl").write_text(
                json.dumps({"id": "g001", "result": {"status": "answered"}}) + "\n",
                encoding="utf-8",
            )

            create_stage_receipt(root, "run-tamper2")
            validate_stage_receipt(root, "run-tamper2")

            # Tamper gate.json
            (run_dir / "gate.json").write_text(json.dumps({"passed": False}), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_stage_receipt(root, "run-tamper2")

    def test_validate_detects_tampered_execution_status_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "run-fail-dec"
            run_dir.mkdir(parents=True)
            manifest = {"schema_version": "1.0", "mode": "qa", "split": "dev", "case_ids": ["g001"]}
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (run_dir / "gate.json").write_text(json.dumps({"passed": False}), encoding="utf-8")
            rec = {"id": "g001", "result": {"status": "answered"}}
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            receipt = create_stage_receipt(root, "run-fail-dec", gate={"passed": False})
            self.assertEqual(receipt["execution_status"]["decision"], "FAIL")
            validate_stage_receipt(root, "run-fail-dec")

            # Tamper stage_receipt.json in-place: edit decision to PASS
            receipt_path = run_dir / "stage_receipt.json"
            r_data = json.loads(receipt_path.read_text(encoding="utf-8"))
            r_data["execution_status"]["decision"] = "PASS"
            receipt_path.write_text(json.dumps(r_data), encoding="utf-8")

            with self.assertRaises(ValueError):
                validate_stage_receipt(root, "run-fail-dec")

    def test_validate_detects_tampered_gate_summary_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "run-fail-gate"
            run_dir.mkdir(parents=True)
            manifest = {"schema_version": "1.0", "mode": "qa", "split": "dev", "case_ids": ["g001"]}
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (run_dir / "gate.json").write_text(json.dumps({"passed": False}), encoding="utf-8")
            rec = {"id": "g001", "result": {"status": "answered"}}
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            receipt = create_stage_receipt(root, "run-fail-gate", gate={"passed": False})
            self.assertEqual(receipt["gate_summary"]["cohort_decision"]["verdict"], "FAIL")
            validate_stage_receipt(root, "run-fail-gate")

            # Tamper stage_receipt.json in-place: edit gate_summary verdict to PASS
            receipt_path = run_dir / "stage_receipt.json"
            r_data = json.loads(receipt_path.read_text(encoding="utf-8"))
            r_data["gate_summary"]["cohort_decision"]["verdict"] = "PASS"
            receipt_path.write_text(json.dumps(r_data), encoding="utf-8")

            with self.assertRaises(ValueError):
                validate_stage_receipt(root, "run-fail-gate")

    def test_validate_detects_tampered_attempts_ledger_same_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "run-attempts"
            run_dir.mkdir(parents=True)
            manifest = {"schema_version": "1.0", "mode": "qa", "split": "dev", "case_ids": ["g001"]}
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (run_dir / "gate.json").write_text(json.dumps({"passed": True}), encoding="utf-8")
            rec = {"id": "g001", "result": {"status": "answered"}}
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            # Ledger with 1 attempt
            attempt1 = {
                "id": "g001",
                "attempt_number": 1,
                "model_calls": 2,
                "token_usage": 150,
                "status": "failed",
                "error": "transient timeout",
            }
            (run_dir / "attempts.jsonl").write_text(json.dumps(attempt1) + "\n", encoding="utf-8")

            receipt = create_stage_receipt(root, "run-attempts", gate={"passed": True})
            self.assertIn("attempts_file_sha256", receipt["artifacts_and_hashes"])
            self.assertIsNotNone(receipt["artifacts_and_hashes"]["attempts_file_sha256"])
            validate_stage_receipt(root, "run-attempts")

            # Tamper attempts.jsonl: change error message while keeping same model_calls and token_usage
            tampered_attempt = {
                "id": "g001",
                "attempt_number": 1,
                "model_calls": 2,
                "token_usage": 150,
                "status": "failed",
                "error": "different message",
            }
            (run_dir / "attempts.jsonl").write_text(json.dumps(tampered_attempt) + "\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                validate_stage_receipt(root, "run-attempts")


class F6aGateEvaluationScriptContractTests(unittest.TestCase):
    def test_historical_source_matrix_uses_forward_only_receipt(self):
        from evaluation.scripts.f6a_gate_evaluation import main as gate_main

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "rc1-run"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            record = {
                "id": "g001",
                "intent": "usage",
                "split": "dev",
                "language": "en",
                "expected_status": "answered",
                "result": {"status": "answered"},
                "metrics": {
                    "gold_recall_at_10": 1.0,
                    "final_evidence_recall": 1.0,
                    "critical_final_evidence_recall": 1.0,
                    "intent_correct": True,
                    "expected_status_correct": True,
                    "citation_integrity": 1.0,
                    "wrong_version_evidence_count": 0,
                    "forbidden_evidence_count": 0,
                    "required_source_coverage_answered": 1.0,
                    "identifier_hallucination_rate": 0.0,
                    "paper_code_dual_source_rate": 1.0,
                    "answer_point_coverage": 1.0,
                    "critical_answer_point_miss_count": 0,
                    "contradiction_count": 0,
                    "major_unsupported_claim_count": 0,
                    "unhandled_exception_count": 0,
                    "per_intent": {
                        "usage": {"gold_recall_at_10": 1.0, "intent_accuracy": 1.0, "cases": 1}
                    },
                },
            }
            (run_dir / "records").mkdir()
            (run_dir / "records" / "g001.json").write_text(json.dumps(record), encoding="utf-8")
            (run_dir / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

            # Create prior matrix
            prior_matrix_path = root / "prior_matrix.json"
            prereg_path = root / "prereg.json"
            prereg = {
                "gold_quality_thresholds": {
                    "gold_recall_at_10": 0.8,
                    "final_evidence_recall": 0.8,
                    "critical_final_evidence_recall": 0.8,
                    "intent_accuracy": 0.8,
                    "per_intent_gold_recall_at_10": 0.7,
                    "per_intent_intent_accuracy": 0.7,
                    "expected_status_accuracy": 0.8,
                    "citation_integrity": 0.9,
                    "required_source_coverage_answered": 0.8,
                    "identifier_hallucination_rate": 0.05,
                    "paper_code_dual_source_rate": 0.8,
                    "answer_point_coverage": 0.8,
                }
            }
            prereg_path.write_text(json.dumps(prereg), encoding="utf-8")

            # First run gate evaluation to generate prior matrix
            out1 = root / "matrix1.json"
            old_argv = sys.argv
            try:
                sys.argv = [
                    "f6a_gate_eval",
                    "--project-root", str(root),
                    "--run-id", "rc1-run",
                    "--prereg", str(prereg_path),
                    "--output", str(out1),
                ]
                gate_main()
            finally:
                sys.argv = old_argv

            self.assertTrue(out1.exists())
            # Old run receipt should exist from initial gate evaluation
            old_receipt_path = root / "matrix1_receipt.json"
            self.assertTrue(old_receipt_path.exists())
            old_receipt_mtime = old_receipt_path.stat().st_mtime_ns

            # Now run with --source-matrix: MUST NOT TOUCH old run receipt
            out2 = root / "matrix2.json"
            try:
                sys.argv = [
                    "f6a_gate_eval",
                    "--project-root", str(root),
                    "--run-id", "rc1-run",
                    "--prereg", str(prereg_path),
                    "--source-matrix", str(out1),
                    "--output", str(out2),
                ]
                gate_main()
            finally:
                sys.argv = old_argv

            self.assertTrue(out2.exists())
            # Old run receipt must not have been modified!
            self.assertEqual(old_receipt_path.stat().st_mtime_ns, old_receipt_mtime)

    def test_gate_eval_suppresses_case_details_when_pending(self):
        from evaluation.scripts.f6a_gate_evaluation import main as gate_main

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "pending-run"
            run_dir.mkdir(parents=True)
            # Manifest expects g001 and g002, but only g001 is recorded
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001", "g002"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            record = {
                "id": "g001",
                "intent": "usage",
                "split": "dev",
                "language": "en",
                "expected_status": "answered",
                "result": {"status": "answered"},
                "metrics": {"gold_recall_at_10": 1.0},
            }
            (run_dir / "results.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            prereg = {
                "gold_quality_thresholds": {
                    "gold_recall_at_10": 0.8,
                    "final_evidence_recall": 0.8,
                    "critical_final_evidence_recall": 0.8,
                    "intent_accuracy": 0.8,
                    "per_intent_gold_recall_at_10": 0.7,
                    "per_intent_intent_accuracy": 0.7,
                    "expected_status_accuracy": 0.8,
                    "citation_integrity": 0.9,
                    "required_source_coverage_answered": 0.8,
                    "identifier_hallucination_rate": 0.05,
                    "paper_code_dual_source_rate": 0.8,
                    "answer_point_coverage": 0.8,
                }
            }
            prereg_path.write_text(json.dumps(prereg), encoding="utf-8")
            out = root / "matrix_pending.json"

            old_argv = sys.argv
            old_stdout = sys.stdout
            try:
                sys.stdout = buf = io.StringIO()
                sys.argv = [
                    "f6a_gate_eval",
                    "--project-root", str(root),
                    "--run-id", "pending-run",
                    "--prereg", str(prereg_path),
                    "--output", str(out),
                ]
                gate_main()
                printed = buf.getvalue()
            finally:
                sys.argv = old_argv
                sys.stdout = old_stdout

            # Receipt should NOT be sealed for pending run
            self.assertIn("stage_receipt_sealed: False", printed)
            self.assertIn("official_decision: RECOVERY_PENDING", printed)
            self.assertIn("NOTICE: evaluation recovery pending", printed)
            # Case details / failed gate count must be suppressed!
            self.assertNotIn("failed_gate_count:", printed)
            self.assertFalse((run_dir / "stage_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
