"""Focused tests for the C8-A2R1 invocation-recovery adapter."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from evaluation.scripts import run_c8_a2r1_recovery as recovery
from evaluation.scripts.capture_c8_a2_two_pass import load_execution_projection


class C8A2R1RecoveryTests(unittest.TestCase):
    def test_preflight_failure_does_not_start_scientific_run(self) -> None:
        receipt = Mock()
        live = Mock()

        def fail_preflight() -> dict[str, object]:
            raise RuntimeError("ADC unavailable")

        with self.assertRaisesRegex(RuntimeError, "ADC unavailable"):
            recovery.gate_then_execute(fail_preflight, receipt, live)
        receipt.assert_not_called()
        live.assert_not_called()

    def test_recovery_restart_is_g001_and_paths_are_new(self) -> None:
        projection = load_execution_projection()
        self.assertEqual(projection[0]["case_id"], "g001")
        paths = recovery.recovery_paths()
        original_paths = {
            recovery.a2.PREREGISTRATION_PATH,
            recovery.a2.SCREENING_LEDGER_PATH,
            recovery.a2.CAPTURE_PATH,
            recovery.a2.CAPTURE_REPORT_PATH,
        }
        self.assertTrue(all(path not in original_paths for path in paths.values()))
        self.assertEqual(paths["receipt"].name, "phase_c_a2r1_invocation_recovery_receipt_v1.json")

    def test_existing_recovery_output_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "existing.json"
            existing.write_text("{}", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                recovery.assert_recovery_outputs_absent({"report": existing})

    def test_receipt_reuses_frozen_preregistration_without_scientific_duplicates(self) -> None:
        receipt = recovery.build_recovery_receipt(
            {"task": "C8-A2"},
            {
                "adc_resolution": "PASS",
                "synthetic_generation_health": "PASS",
                "synthetic_embedding_health": "PASS",
                "retriever_initialization": "PASS",
            },
            source_head="fixture-head",
        )
        self.assertEqual(receipt["task"], "C8-A2R1")
        self.assertEqual(
            receipt["frozen_preregistration_path"].replace("\\", "/"),
            "evaluation/baselines/manifests/phase_c_c8_a2_global_treatment_preregistration_v1.json",
        )
        self.assertTrue(receipt["frozen_preregistration_unchanged"])
        self.assertTrue(receipt["scientific_fields_authoritative"])
        self.assertNotIn("scientific_fields", receipt)
        self.assertNotIn("g1", receipt)
        self.assertNotIn("primary_metrics", receipt)


if __name__ == "__main__":
    unittest.main()
