"""F6-A-R1 gate evaluator tests: canonical aggregation reuse, corrected
applicability/denominator semantics, per-intent gate evaluation, upper-bound
identifier gate, and zero-model-call operation."""

import unittest
from pathlib import Path

from panda_agent.evaluation import aggregate_metrics


class GateEvaluatorTests(unittest.TestCase):
    """F6-A-R1-R1: the gate evaluator reuses canonical aggregation, applies
    corrected applicability/denominator/upper-bound semantics, never converts
    a missing measurement into PASS, keeps every represented intent visible,
    and separates failed from incomplete gates."""

    @staticmethod
    def _load_module():
        import importlib
        import sys

        script_dir = Path(__file__).resolve().parents[2] / "evaluation" / "scripts"
        sys.path.insert(0, str(script_dir))
        return importlib.import_module("f6a_gate_evaluation")

    @staticmethod
    def _records():
        return [
            {
                "id": "g100",
                "intent": "usage",
                "expected_status": "answered",
                "metrics": {
                    "answer_point_coverage": 1.0,
                    "gold_recall_at_10": 1.0,
                    "intent_correct": True,
                    "expected_status_correct": True,
                    "citation_integrity": True,
                    "paper_code_dual_source": True,
                    "hallucinated_identifiers": [],
                    "identifier_mentions": ["a", "b"],
                    "metric_applicability": {"paper_code_dual_source": True},
                },
                "required_source_types": ["paper", "code"],
            },
            {
                "id": "g101",
                "intent": "usage",
                "expected_status": "answered",
                "metrics": {
                    "answer_point_coverage": 0.5,
                    "gold_recall_at_10": 0.9,
                    "intent_correct": True,
                    "expected_status_correct": True,
                    "citation_integrity": True,
                    "paper_code_dual_source": False,
                    "hallucinated_identifiers": ["ghost"],
                    "identifier_mentions": ["c"],
                    "metric_applicability": {"paper_code_dual_source": False},
                },
                "required_source_types": ["code"],
            },
            {
                "id": "g102",
                "intent": "api",
                "expected_status": "refusal",
                "metrics": {
                    "answer_point_coverage": None,
                    "gold_recall_at_10": None,
                    "intent_correct": False,
                    "expected_status_correct": True,
                    "citation_integrity": None,
                    "paper_code_dual_source": None,
                    "hallucinated_identifiers": [],
                    "identifier_mentions": [],
                    "metric_applicability": {"paper_code_dual_source": False},
                },
                "required_source_types": [],
            },
        ]

    @staticmethod
    def _prereg():
        return {
            "gold_quality_thresholds": {
                "gold_recall_at_10": 0.95,
                "final_evidence_recall": 0.90,
                "critical_final_evidence_recall": 1.00,
                "intent_accuracy": 0.90,
                "per_intent_gold_recall_at_10": 0.75,
                "per_intent_intent_accuracy": 0.80,
                "expected_status_accuracy": 0.975,
                "citation_integrity": 1.00,
                "wrong_version_evidence_count": 0,
                "forbidden_evidence_count": 0,
                "required_source_coverage_answered": 0.97,
                "identifier_hallucination_rate": 0.03,
                "paper_code_dual_source_rate": 1.00,
                "answer_point_coverage": 0.90,
                "critical_answer_point_miss_count": 0,
                "contradiction_count": 0,
                "major_unsupported_claim_count": 0,
                "unhandled_exception_count": 0,
            }
        }

    def test_dual_source_denominator_only_dual_required_answered_cases(self):
        gate_eval = self._load_module()
        records = self._records()
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        # Canonical applicability: answered + applicable + required paper&code
        # -> only g100. Its value is True -> rate 1.0, PASS.
        self.assertEqual(gates["paper_code_dual_source_rate"]["denominator"], 1)
        self.assertEqual(gates["paper_code_dual_source_rate"]["value"], 1.0)
        self.assertTrue(gates["paper_code_dual_source_rate"]["passed"])

    def test_dual_source_applicable_ids_reported(self):
        gate_eval = self._load_module()
        records = self._records()
        self.assertEqual(gate_eval.dual_source_applicable_ids(records), ["g100"])

    def test_identifier_hallucination_denominator_is_total_mentions(self):
        gate_eval = self._load_module()
        records = self._records()
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        # Total mentions = 2 + 1 = 3; hallucinations = 1 -> 1/3, FAIL (upper).
        self.assertEqual(gates["identifier_hallucination_rate"]["denominator"], 3)
        self.assertAlmostEqual(gates["identifier_hallucination_rate"]["value"], 1 / 3)
        self.assertFalse(gates["identifier_hallucination_rate"]["passed"])
        self.assertTrue(gates["identifier_hallucination_rate"]["upper_bound"])

    def test_identifier_upper_bound_accepts_zero_rate(self):
        gate_eval = self._load_module()
        records = self._records()
        for record in records:
            record["metrics"]["hallucinated_identifiers"] = []
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        self.assertTrue(gates["identifier_hallucination_rate"]["passed"])
        self.assertEqual(gates["identifier_hallucination_rate"]["value"], 0.0)

    def test_zero_gate_missing_measurement_is_incomplete_not_pass(self):
        gate_eval = self._load_module()
        records = self._records()
        for record in records:
            record["metrics"]["contradictions"] = None
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        self.assertIsNone(gates["contradiction_count"]["passed"])
        self.assertIsNone(gates["contradiction_count"]["value"])

    def test_zero_gate_numeric_zero_passes_and_nonzero_fails(self):
        gate_eval = self._load_module()
        records = self._records()
        for record in records:
            record["metrics"]["contradictions"] = []
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        self.assertTrue(gates["contradiction_count"]["passed"])
        for record in records:
            record["metrics"]["contradictions"] = ["x"]
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        self.assertFalse(gates["contradiction_count"]["passed"])

    def test_intent_accuracy_denominator_is_intent_case_count(self):
        gate_eval = self._load_module()
        records = self._records()
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        # intent-accuracy denominator = sum of represented per-intent cases
        # (2 usage + 1 api = 3), not expected_status_accuracy_denominator.
        self.assertEqual(gates["intent_accuracy"]["denominator"], 3)

    def test_per_intent_missing_metric_is_incomplete_not_pass(self):
        gate_eval = self._load_module()
        # A represented intent whose only case cannot measure recall or intent
        # accuracy must surface as INCOMPLETE, never silently disappear.
        records = [
            {
                "id": "g103",
                "intent": "installation",
                "expected_status": "answered",
                "metrics": {
                    "answer_point_coverage": 0.2,
                    "gold_recall_at_10": None,
                    "intent_accuracy": None,
                    "intent_correct": None,
                    "expected_status_correct": True,
                    "citation_integrity": True,
                    "paper_code_dual_source": None,
                    "hallucinated_identifiers": [],
                    "identifier_mentions": [],
                    "metric_applicability": {"paper_code_dual_source": False},
                },
                "required_source_types": [],
            }
        ]
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        self.assertIsNone(gates["per_intent_gold_recall_at_10"]["passed"])
        self.assertIsNone(gates["per_intent_intent_accuracy"]["passed"])
        details = {d["intent"]: d for d in gates["per_intent_gold_recall_at_10"]["per_intent_details"]}
        self.assertIn("installation", details)
        self.assertIsNone(details["installation"]["passed"])

    @staticmethod
    def _measured_extra_case(case_id, intent, recall, accuracy, intent_correct):
        return {
            "id": case_id,
            "intent": intent,
            "expected_status": "answered",
            "metrics": {
                "answer_point_coverage": 1.0,
                "gold_recall_at_10": recall,
                "intent_accuracy": accuracy,
                "intent_correct": intent_correct,
                "expected_status_correct": True,
                "citation_integrity": True,
                "paper_code_dual_source": None,
                "hallucinated_identifiers": [],
                "identifier_mentions": [],
                "metric_applicability": {"paper_code_dual_source": False},
            },
            "required_source_types": [],
        }

    def test_per_intent_one_failing_intent_fails_aggregate(self):
        gate_eval = self._load_module()
        records = [
            record for record in self._records() if record["intent"] != "api"
        ] + [self._measured_extra_case("g103", "installation", 0.1, 0.1, False)]
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        self.assertFalse(gates["per_intent_gold_recall_at_10"]["passed"])
        self.assertFalse(gates["per_intent_intent_accuracy"]["passed"])
        self.assertEqual(gates["per_intent_gold_recall_at_10"]["value"], 0.1)

    def test_per_intent_all_measured_passing_aggregate_passes(self):
        gate_eval = self._load_module()
        records = [
            record for record in self._records() if record["intent"] != "api"
        ] + [self._measured_extra_case("g103", "installation", 0.9, 0.9, True)]
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        self.assertTrue(gates["per_intent_gold_recall_at_10"]["passed"])
        self.assertTrue(gates["per_intent_intent_accuracy"]["passed"])

    def test_failed_and_incomplete_gate_counts_excluded_release_score(self):
        gate_eval = self._load_module()
        records = self._records()
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        # release_score is accounting, not a gate: it must not appear in the
        # failed/incomplete counts even though its own passed is null.
        self.assertIsNone(gates["release_score"].get("passed"))
        failed = sorted(
            name for name, gate in gates.items()
            if name != "release_score" and gate.get("passed") is False
        )
        incomplete = sorted(
            name for name, gate in gates.items()
            if name != "release_score" and gate.get("passed") is None
        )
        self.assertNotIn("release_score", failed + incomplete)
        self.assertTrue(failed or incomplete)


if __name__ == "__main__":
    unittest.main()
