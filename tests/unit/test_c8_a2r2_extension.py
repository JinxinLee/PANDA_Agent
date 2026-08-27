"""Focused tests for the C8-A2R2 applicability-extension adapter."""

from __future__ import annotations

from unittest.mock import Mock
import unittest

from evaluation.scripts import run_c8_a2r2_extension as extension


class C8A2R2ExtensionTests(unittest.TestCase):
    def test_extension_projection_order_and_original_case_exclusion(self) -> None:
        payload, records = extension.load_extension_projection()
        self.assertEqual(payload["artifact_role"], "C8_A2R2_SANITIZED_EXECUTION_PROJECTION_EXTENSION")
        self.assertEqual(len(records), 64)
        self.assertEqual(records[0]["case_id"], "g004")
        self.assertEqual(records[-1]["case_id"], "g116")
        self.assertEqual(
            [record["case_id"] for record in records],
            payload["extension_case_ids"],
        )
        self.assertTrue(
            set(record["case_id"] for record in records).isdisjoint(
                extension.ORIGINAL_24_CASE_IDS
            )
        )

    def test_existing_a2r1_records_are_loaded_read_only(self) -> None:
        records = extension.load_existing_a2r1_records()
        self.assertEqual(
            [record["case_id"] for record in records],
            ["g007", "g025", "g041", "g057"],
        )
        self.assertTrue(
            all(
                record["INITIAL"]["PassSnapshot"]["completeness"] == "COMPLETE"
                and record["TARGETED"]["PassSnapshot"]["completeness"] == "COMPLETE"
                and record["S0_replay_parity"]["parity"] is True
                for record in records
            )
        )

    def test_amendment_freezes_only_extension_boundary(self) -> None:
        projection, _ = extension.load_extension_projection()
        audit = extension.load_split_role_audit(projection)
        amendment = extension.build_amendment(projection, audit, source_head="fixture-head")
        fields = amendment["scientific_fields"]
        self.assertEqual(amendment["amendment_type"], extension.AMENDMENT_TYPE)
        self.assertEqual(fields["original_screened_count"], 24)
        self.assertEqual(fields["original_complete_targeted_count"], 4)
        self.assertEqual(fields["required_total_complete_targeted_count"], 6)
        self.assertEqual(fields["additional_complete_targeted_needed"], 2)
        self.assertEqual(fields["extension_population_size"], 64)
        self.assertFalse(fields["treatment_semantics_changed"])
        self.assertFalse(fields["targeted_characteristics_used_for_extension_selection"])
        self.assertFalse(fields["treatment_outcome_observed_before_amendment"])

    def test_combined_manifest_places_existing_cases_before_two_new_cases(self) -> None:
        existing = [{"case_id": case_id} for case_id in extension.EXPECTED_A2R1_TARGETED_CASE_IDS]
        new = [{"case_id": "g004"}, {"case_id": "g005"}]
        split_map = {
            "g007": "dev",
            "g025": "acceptance",
            "g041": "acceptance",
            "g057": "acceptance",
            "g004": "dev",
            "g005": "dev",
        }
        manifest = extension.build_combined_manifest(existing, new, split_map)
        self.assertEqual(
            [record["case_id"] for record in manifest["records"]],
            ["g007", "g025", "g041", "g057", "g004", "g005"],
        )
        self.assertEqual(manifest["cohort_label"], extension.COHORT_LABEL)
        self.assertTrue(manifest["all_s0_replay_parity"])

    def test_preflight_failure_consumes_no_live_attempt(self) -> None:
        amendment = Mock()
        live = Mock()

        def fail_preflight() -> dict[str, object]:
            raise RuntimeError("ADC unavailable")

        with self.assertRaisesRegex(RuntimeError, "ADC unavailable"):
            extension.gate_then_execute(fail_preflight, amendment, live)
        amendment.assert_not_called()
        live.assert_not_called()


if __name__ == "__main__":
    unittest.main()
