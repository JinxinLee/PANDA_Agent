"""F6-A-R1 gate evaluator tests: canonical aggregation reuse, corrected
applicability/denominator semantics, per-intent gate evaluation, upper-bound
identifier gate, and zero-model-call operation."""

import unittest
from pathlib import Path

from panda_agent.evaluation import aggregate_metrics


class GateEvaluatorTests(unittest.TestCase):
    """The gate evaluator must reuse canonical aggregation and apply the
    corrected applicability/denominator/upper-bound semantics."""

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

    def test_per_intent_gates_use_per_intent_minima(self):
        gate_eval = self._load_module()
        records = self._records()
        records.append(
            {
                "id": "g103",
                "intent": "installation",
                "expected_status": "answered",
                "metrics": {
                    "answer_point_coverage": 0.2,
                    "gold_recall_at_10": 0.1,
                    "intent_correct": False,
                    "expected_status_correct": True,
                    "citation_integrity": True,
                    "paper_code_dual_source": None,
                    "hallucinated_identifiers": [],
                    "identifier_mentions": [],
                    "metric_applicability": {"paper_code_dual_source": False},
                },
                "required_source_types": [],
            }
        )
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        # usage recall = (1.0 + 0.9)/2 = 0.95; installation recall = 0.1.
        # The per-intent gate evaluates the minimum across intents, not the
        # global mean.
        self.assertAlmostEqual(aggregate["per_intent"]["usage"]["gold_recall_at_10"], 0.95)
        self.assertEqual(gates["per_intent_gold_recall_at_10"]["value"], 0.1)
        self.assertFalse(gates["per_intent_gold_recall_at_10"]["passed"])
        self.assertEqual(gates["per_intent_intent_accuracy"]["value"], 0.0)
        self.assertFalse(gates["per_intent_intent_accuracy"]["passed"])

    def test_failed_gate_list_derives_from_corrected_matrix(self):
        gate_eval = self._load_module()
        records = self._records()
        aggregate = aggregate_metrics(records)
        gates = gate_eval.derive_gate_matrix(aggregate, records, self._prereg())
        failed = sorted(name for name, gate in gates.items() if gate.get("passed") is False)
        self.assertIn("intent_accuracy", failed)  # g102 intent_correct=False -> 2/3 < 0.90
        self.assertIn("identifier_hallucination_rate", failed)  # 1/3 > 0.03 (upper bound)
        self.assertNotIn("paper_code_dual_source_rate", failed)
        self.assertEqual(sorted(gates), sorted(set(gates)))

    def test_gate_evaluation_requires_no_model_calls(self):
        script_path = (
            Path(__file__).resolve().parents[2]
            / "evaluation" / "scripts" / "f6a_gate_evaluation.py"
        )
        source = script_path.read_text(encoding="utf-8")
        self.assertNotIn("generate_json", source)
        self.assertNotIn("VertexAIClient", source)
        self.assertNotIn("generate_content", source)


if __name__ == "__main__":
    unittest.main()
