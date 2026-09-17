"""Unit tests for standalone gate CLI receipt exposure and forward-only validation.

Verifies:
1. Pending recovery returns status only without writing detailed output file.
2. Terminal inconclusive does not call pending recovery notice.
3. Invalid candidate identity preserves tri-state None and INCONCLUSIVE.
4. Forward-only gate-input receipt adjacent to output binds prereg and derived matrix via SHA256.
5. Idempotent validation detects stale/tampered receipt and fails closed.
6. Standalone gate CLI does not mutate existing run receipt.
7. --source-matrix rejects replacing source matrix input itself.
8. --source-matrix preserves prior terminal verdict effect.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from evaluation.scripts.f6a_gate_evaluation import main as gate_main


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class PostA3GateCliTests(unittest.TestCase):
    def _create_minimal_prereg(self, path: Path) -> None:
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
                "wrong_version_evidence_count": 0,
                "forbidden_evidence_count": 0,
                "required_source_coverage_answered": 0.8,
                "identifier_hallucination_rate": 0.05,
                "paper_code_dual_source_rate": 0.8,
                "answer_point_coverage": 0.8,
                "critical_answer_point_miss_count": 0,
                "contradiction_count": 0,
                "major_unsupported_claim_count": 0,
                "unhandled_exception_count": 0,
            }
        }
        path.write_text(json.dumps(prereg, indent=2), encoding="utf-8")

    def _create_minimal_record(self, case_id: str = "g001", intent: str = "usage") -> dict:
        return {
            "id": case_id,
            "intent": intent,
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
                "hallucinated_identifiers": [],
                "identifier_mentions": [],
                "metric_applicability": {"paper_code_dual_source": False},
                "per_intent": {
                    intent: {"gold_recall_at_10": 1.0, "intent_accuracy": 1.0, "cases": 1}
                },
            },
            "required_source_types": [],
        }

    def _run_gate(self, args: list[str]) -> tuple[str, str]:
        old_argv = sys.argv
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        buf_out = io.StringIO()
        buf_err = io.StringIO()
        try:
            sys.argv = ["f6a_gate_eval"] + args
            sys.stdout = buf_out
            sys.stderr = buf_err
            gate_main()
            return buf_out.getvalue(), buf_err.getvalue()
        finally:
            sys.argv = old_argv
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def test_pending_recovery_suppresses_detail_output_and_seals_no_receipt(self):
        """When cohort recovery is pending, do not write detailed output file."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-pending"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001", "g002"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            out = root / "matrix_pending.json"
            receipt_path = root / "matrix_pending_receipt.json"

            stdout, _ = self._run_gate([
                "--project-root", str(root),
                "--run-id", "test-pending",
                "--prereg", str(prereg_path),
                "--output", str(out),
            ])

            self.assertIn("cohort_status: INCOMPLETE", stdout)
            self.assertIn("official_decision: RECOVERY_PENDING", stdout)
            self.assertIn("stage_receipt_sealed: False", stdout)
            self.assertIn("NOTICE: evaluation recovery pending", stdout)
            # Detail file must NOT be written!
            self.assertFalse(out.exists(), "detailed output file must not exist when recovery is pending")
            self.assertFalse(receipt_path.exists(), "gate receipt must not exist when recovery is pending")

    def test_terminal_inconclusive_does_not_call_pending_recovery_notice(self):
        """Terminal unrecoverable cohort should not print pending recovery notice."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-inconclusive"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = {
                "id": "g001",
                "intent": "usage",
                "split": "dev",
                "language": "en",
                "expected_status": "answered",
                "exception": {"type": "RuntimeError", "message": "unauthorized permanent error 401"},
            }
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            out = root / "matrix_inconclusive.json"

            stdout, _ = self._run_gate([
                "--project-root", str(root),
                "--run-id", "test-inconclusive",
                "--prereg", str(prereg_path),
                "--output", str(out),
            ])

            self.assertIn("official_decision: INCONCLUSIVE", stdout)
            self.assertNotIn("NOTICE: evaluation recovery pending", stdout)
            self.assertTrue(out.exists())
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["cohort_decision"]["verdict"], "INCONCLUSIVE")
            self.assertIsNone(data["cohort_decision"]["passed"])

    def test_invalid_candidate_identity_preserves_tri_state_none(self):
        """Invalid candidate identity can never PASS (verdict INCONCLUSIVE, passed None)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-invalid-cand"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
                "candidate_id": "bad-cand-id",
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            out = root / "matrix_invalid_cand.json"

            with patch("panda_agent.candidate.verify_candidate", return_value={"valid": False, "manifest_sha256": "bad"}):
                stdout, _ = self._run_gate([
                    "--project-root", str(root),
                    "--run-id", "test-invalid-cand",
                    "--prereg", str(prereg_path),
                    "--output", str(out),
                ])

            self.assertIn("official_decision: INCONCLUSIVE", stdout)
            self.assertNotIn("NOTICE: evaluation recovery pending", stdout)
            self.assertTrue(out.exists())
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["cohort_decision"]["verdict"], "INCONCLUSIVE")
            self.assertIsNone(data["cohort_decision"]["passed"])

    def test_forward_only_gate_receipt_adjacent_to_output_binds_prereg_and_matrix(self):
        """Gate receipt is created adjacent to output and binds prereg and derived matrix SHA256."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-bind"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            out = root / "matrix_bind.json"
            receipt_path = root / "matrix_bind_receipt.json"

            stdout, _ = self._run_gate([
                "--project-root", str(root),
                "--run-id", "test-bind",
                "--prereg", str(prereg_path),
                "--output", str(out),
            ])

            self.assertTrue(out.exists())
            self.assertTrue(receipt_path.exists())
            self.assertIn("stage_receipt_sealed: True", stdout)
            self.assertFalse((run_dir / "stage_receipt.json").exists())

            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            prereg_sha = _sha256_file(prereg_path)
            output_sha = _sha256_file(out)

            # Receipt binds prereg sha and derived output sha
            self.assertEqual(receipt["source_artifacts"]["prereg_sha256"], prereg_sha)
            self.assertEqual(receipt["derived_output"]["derived_output_sha256"], output_sha)
            self.assertEqual(receipt["derived_output"]["output_file"], out.name)
            self.assertEqual(receipt["run_id"], "test-bind")

    def test_idempotent_validation_fails_closed_on_stale_or_tampered_receipt(self):
        """Re-running with identical inputs passes; tampered receipt fails closed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-stale"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            out = root / "matrix_stale.json"
            receipt_path = root / "matrix_stale_receipt.json"

            # 1. First run creates receipt and output
            self._run_gate([
                "--project-root", str(root),
                "--run-id", "test-stale",
                "--prereg", str(prereg_path),
                "--output", str(out),
            ])
            self.assertTrue(receipt_path.exists())

            # 2. Re-run identically: must succeed idempotently
            self._run_gate([
                "--project-root", str(root),
                "--run-id", "test-stale",
                "--prereg", str(prereg_path),
                "--output", str(out),
            ])

            # 3. Tamper receipt derived_output_sha256 -> must fail closed
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["derived_output"]["derived_output_sha256"] = "0" * 64
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

            with self.assertRaises(ValueError):
                self._run_gate([
                    "--project-root", str(root),
                    "--run-id", "test-stale",
                    "--prereg", str(prereg_path),
                    "--output", str(out),
                ])

    def test_standalone_gate_does_not_mutate_existing_run_receipt(self):
        """Standalone gate execution must not overwrite or mutate existing run stage_receipt."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-nomutate"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            # Seed an existing runner report receipt in the run directory
            run_receipt_path = run_dir / "stage_receipt.json"
            run_receipt_data = {
                "schema_version": "stage-receipt-v1",
                "execution_status": {"decision": "PASS"},
                "gate_summary": {"passed": True, "cohort_decision": {"status": "COMPLETE", "verdict": "PASS"}},
            }
            run_receipt_path.write_text(json.dumps(run_receipt_data), encoding="utf-8")
            orig_mtime = run_receipt_path.stat().st_mtime_ns
            orig_content = run_receipt_path.read_text(encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            out = root / "matrix_nomutate.json"

            self._run_gate([
                "--project-root", str(root),
                "--run-id", "test-nomutate",
                "--prereg", str(prereg_path),
                "--output", str(out),
            ])

            self.assertTrue(out.exists())
            self.assertTrue((root / "matrix_nomutate_receipt.json").exists())
            # Run receipt in run_dir must be untouched
            self.assertEqual(run_receipt_path.stat().st_mtime_ns, orig_mtime)
            self.assertEqual(run_receipt_path.read_text(encoding="utf-8"), orig_content)

    def test_source_matrix_rejects_replacing_source_input_itself(self):
        """Passing source-matrix equal to output must be rejected."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-replace"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            prior = root / "prior_matrix.json"
            prior.write_text(json.dumps({"schema_version": "v1"}), encoding="utf-8")

            with self.assertRaises(ValueError):
                self._run_gate([
                    "--project-root", str(root),
                    "--run-id", "test-replace",
                    "--prereg", str(prereg_path),
                    "--source-matrix", str(prior),
                    "--output", str(prior),
                ])

    def test_source_matrix_preserves_prior_terminal_verdict_effect(self):
        """Historical source-matrix preserves prior terminal verdict effect."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-effect"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)

            # Generate initial matrix
            out1 = root / "matrix1.json"
            self._run_gate([
                "--project-root", str(root),
                "--run-id", "test-effect",
                "--prereg", str(prereg_path),
                "--output", str(out1),
            ])

            # Now run successor with --source-matrix out1
            out2 = root / "matrix2.json"
            self._run_gate([
                "--project-root", str(root),
                "--run-id", "test-effect",
                "--prereg", str(prereg_path),
                "--source-matrix", str(out1),
                "--output", str(out2),
            ])

            data1 = json.loads(out1.read_text(encoding="utf-8"))
            data2 = json.loads(out2.read_text(encoding="utf-8"))
            self.assertIn(data1["terminal_verdict_effect"], data2["terminal_verdict_effect"])
            self.assertTrue((root / "matrix2_receipt.json").exists())

    def test_gate_cli_loads_project_root_dotenv(self):
        """Standalone gate CLI must load project-root .env before resolving candidates."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-dotenv"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
                "official": True,
                "candidate_id": "cand-valid",
                "candidate_manifest_sha256": "candidate_sha",
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            out = root / "matrix_dotenv.json"

            # Write .env in project root
            test_var_name = "PANDA_TEST_GATE_DOTENV_LOADED"
            test_var_val = "loaded_val_42"
            env_file = root / ".env"
            env_file.write_text(f"{test_var_name}={test_var_val}\n", encoding="utf-8")

            old_val = os.environ.pop(test_var_name, None)
            try:
                with patch(
                    "panda_agent.candidate.verify_candidate",
                    return_value={"valid": True, "manifest_sha256": "candidate_sha"},
                ):
                    self._run_gate([
                        "--project-root", str(root),
                        "--run-id", "test-dotenv",
                        "--prereg", str(prereg_path),
                        "--output", str(out),
                    ])
                self.assertEqual(os.environ.get(test_var_name), test_var_val)
                receipt = json.loads(
                    (root / "matrix_dotenv_receipt.json").read_text(encoding="utf-8")
                )
                self.assertTrue(receipt["candidate_valid"])
                self.assertEqual(receipt["candidate_manifest_sha256"], "candidate_sha")
            finally:
                if old_val is not None:
                    os.environ[test_var_name] = old_val
                else:
                    os.environ.pop(test_var_name, None)

    def test_gate_cli_candidate_verification_exception_fails_before_output_or_receipt(self):
        """Candidate verification exception in standalone gate CLI must raise and seal no receipt."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-cand-exc"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
                "candidate_id": "cand-exc",
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            out = root / "matrix_cand_exc.json"
            receipt_path = root / "matrix_cand_exc_receipt.json"

            with patch(
                "panda_agent.candidate.verify_candidate",
                side_effect=RuntimeError("vertex credentials missing"),
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    self._run_gate([
                        "--project-root", str(root),
                        "--run-id", "test-cand-exc",
                        "--prereg", str(prereg_path),
                        "--output", str(out),
                    ])
                self.assertIn("vertex credentials missing", str(ctx.exception))

            self.assertFalse(out.exists(), "matrix must not be written when verification fails")
            self.assertFalse(receipt_path.exists(), "receipt must not be sealed when verification fails")

    def test_gate_cli_actually_invalid_candidate_preserves_output_and_receipt(self):
        """Actually invalid candidate (valid=False, no exception) writes output and seals receipt."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "data" / "evaluation" / "runs" / "test-cand-invalid"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": "1.0",
                "mode": "qa",
                "split": "dev",
                "case_ids": ["g001"],
                "candidate_id": "cand-invalid",
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            rec = self._create_minimal_record("g001")
            (run_dir / "results.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")

            prereg_path = root / "prereg.json"
            self._create_minimal_prereg(prereg_path)
            out = root / "matrix_cand_invalid.json"
            receipt_path = root / "matrix_cand_invalid_receipt.json"

            with patch(
                "panda_agent.candidate.verify_candidate",
                return_value={"valid": False, "manifest_sha256": "some_sha", "mismatches": ["git_commit"]},
            ):
                stdout, _ = self._run_gate([
                    "--project-root", str(root),
                    "--run-id", "test-cand-invalid",
                    "--prereg", str(prereg_path),
                    "--output", str(out),
                ])

            self.assertTrue(out.exists(), "matrix must be written for cleanly verified invalid candidate")
            self.assertTrue(receipt_path.exists(), "receipt must be sealed for cleanly verified invalid candidate")
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertFalse(receipt["candidate_valid"])
            self.assertEqual(receipt["decision"], "INCONCLUSIVE")

if __name__ == "__main__":
    unittest.main()
