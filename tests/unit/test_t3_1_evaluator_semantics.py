from __future__ import annotations

import unittest

from panda_agent.evaluation import (
    GoldDataset,
    GoldQuestion,
    aggregate_metrics,
    apply_mode_metric_semantics,
    deterministic_case_metrics,
    english_product_case_ids,
    evaluate_development_gate,
    evaluate_product_development_gate,
    offline_rescore_records,
)


def _question(
    question_id: str,
    *,
    language: str = "en",
    expected_status: str = "answered",
    intent: str = "api",
) -> GoldQuestion:
    return GoldQuestion.model_validate(
        {
            "id": question_id,
            "split": "dev",
            "language": language,
            "intent": intent,
            "query": f"Query for {question_id}?",
            "expected_status": expected_status,
            "allowed_source_versions": ["repo@locked"],
            "required_evidence_groups": [
                {
                    "group_id": f"{question_id}.e1",
                    "role": "required",
                    "critical": True,
                    "any_of": [{"object_id": f"object.{question_id}"}],
                }
            ],
            "required_answer_points": [
                {"point_id": "p1", "text": "Explain.", "weight": 1.0, "critical": True}
            ],
            "review_status": "approved",
            "reviewer": "reviewer",
            "reviewed_at": "2026-01-01T00:00:00Z",
        }
    )


def _dataset(questions: list[GoldQuestion]) -> GoldDataset:
    return GoldDataset(
        schema_version="2.0",
        benchmark_version="m6-benchmark-v2.6",
        questions=questions,
        release_eligible=True,
        acceptance_exposed=False,
        expected_split_counts={"dev": len(questions)},
        expected_status_counts={},
    )


def _perfect_metrics() -> dict:
    return {
        "intent_correct": True,
        "expected_status_correct": True,
        "gold_recall_at_10": 1.0,
        "final_evidence_recall": 1.0,
        "critical_final_evidence_recall": 1.0,
        "required_source_coverage": True,
        "wrong_version_evidence": [],
        "forbidden_evidence": [],
        "unhandled_exception_count": 0,
        "metric_applicability": {
            "gold_recall_at_10": True,
            "final_evidence_recall": True,
            "critical_final_evidence_recall": True,
            "required_source_coverage": True,
            "expected_status_correct": True,
            "refusal_evidence_recall": False,
        },
        "metric_denominators": {
            "gold_recall_at_10": 1,
            "final_evidence_recall": 1,
            "critical_final_evidence_recall": 1,
            "required_source_coverage": 1,
            "expected_status_correct": 1,
            "refusal_evidence_recall": 0,
        },
    }


class T31EvaluatorSemanticsTests(unittest.TestCase):
    def test_retrieval_mode_expected_status_is_not_applicable(self) -> None:
        metrics = apply_mode_metric_semantics(
            _perfect_metrics(), mode="retrieval", external_judge=False
        )
        self.assertFalse(metrics["metric_applicability"]["expected_status_correct"])
        self.assertEqual(metrics["metric_denominators"]["expected_status_correct"], 0)
        self.assertIsNone(metrics.get("expected_status_accuracy"))

    def test_qa_and_full_keep_expected_status_applicable_and_gated(self) -> None:
        for mode in ("qa", "full"):
            metrics = apply_mode_metric_semantics(
                _perfect_metrics(), mode=mode, external_judge=False
            )
            self.assertTrue(metrics["metric_applicability"]["expected_status_correct"])
            self.assertEqual(metrics["metric_denominators"]["expected_status_correct"], 1)

    def test_retrieval_gate_does_not_hard_gate_expected_status(self) -> None:
        records = [
            {
                "id": "g001",
                "intent": "api",
                "expected_status": "version_conflict",
                "required_source_types": ["code"],
                "duration_ms": 1,
                "metrics": {
                    **_perfect_metrics(),
                    "expected_status_correct": True,
                    "metric_applicability": {
                        **_perfect_metrics()["metric_applicability"],
                        "expected_status_correct": False,
                    },
                    "metric_denominators": {
                        **_perfect_metrics()["metric_denominators"],
                        "expected_status_correct": 0,
                    },
                },
            },
            {
                "id": "g002",
                "intent": "api",
                "expected_status": "answered",
                "required_source_types": ["code"],
                "duration_ms": 1,
                "metrics": {
                    **_perfect_metrics(),
                    "expected_status_correct": True,
                    "metric_applicability": {
                        **_perfect_metrics()["metric_applicability"],
                        "expected_status_correct": False,
                    },
                    "metric_denominators": {
                        **_perfect_metrics()["metric_denominators"],
                        "expected_status_correct": 0,
                    },
                },
            },
        ]
        metrics = aggregate_metrics(records)
        gate = evaluate_development_gate(
            metrics,
            [
                {
                    "id": "g001",
                    "expected_status": "version_conflict",
                    "metrics": {"expected_status_correct": True},
                },
                {
                    "id": "g002",
                    "expected_status": "answered",
                    "metrics": {"expected_status_correct": True},
                },
            ],
            mode="retrieval",
            complete_full_dev=True,
            all_questions_approved=True,
        )
        self.assertNotIn("expected_status_accuracy", gate["checks"])
        self.assertTrue(gate["passed"])

    def test_version_conflict_rejection_remains_hard_in_retrieval(self) -> None:
        metrics = aggregate_metrics(
            [
                {
                    "id": "g001",
                    "intent": "api",
                    "expected_status": "version_conflict",
                    "required_source_types": ["code"],
                    "duration_ms": 1,
                    "metrics": {
                        **_perfect_metrics(),
                        "expected_status_correct": False,
                        "metric_applicability": {
                            **_perfect_metrics()["metric_applicability"],
                            "expected_status_correct": False,
                        },
                        "metric_denominators": {
                            **_perfect_metrics()["metric_denominators"],
                            "expected_status_correct": 0,
                        },
                    },
                }
            ]
        )
        gate = evaluate_development_gate(
            metrics,
            [
                {
                    "id": "g001",
                    "expected_status": "version_conflict",
                    "metrics": {"expected_status_correct": False},
                }
            ],
            mode="retrieval",
            complete_full_dev=True,
            all_questions_approved=True,
        )
        self.assertFalse(gate["passed"])
        self.assertFalse(gate["checks"]["dev_version_conflicts_rejected"])

    def test_insufficient_evidence_never_becomes_ordinary_answered(self) -> None:
        case = _question("g001", expected_status="insufficient_evidence")
        synthetic_answered = {
            "status": "answered",
            "answer": "",
            "claims": [],
            "evidence": [],
        }
        diagnostics = {"plan": {"intent": "api"}, "ranked_object_ids": []}
        metrics = deterministic_case_metrics(case, synthetic_answered, diagnostics, {})
        self.assertFalse(metrics["metric_applicability"]["gold_recall_at_10"])
        self.assertIsNone(metrics["gold_recall_at_10"])
        self.assertIsNone(metrics["mrr"])

    def test_applicability_does_not_depend_on_status_correctness(self) -> None:
        case = _question("g001", expected_status="insufficient_evidence")
        correct_refusal = {"status": "insufficient_evidence", "answer": "", "claims": [], "evidence": []}
        incorrect_answered = {"status": "answered", "answer": "", "claims": [], "evidence": []}
        diagnostics = {"plan": {"intent": "api"}, "ranked_object_ids": []}
        correct_metrics = deterministic_case_metrics(case, correct_refusal, diagnostics, {})
        incorrect_metrics = deterministic_case_metrics(case, incorrect_answered, diagnostics, {})
        self.assertFalse(correct_metrics["metric_applicability"]["gold_recall_at_10"])
        self.assertFalse(incorrect_metrics["metric_applicability"]["gold_recall_at_10"])

    def test_english_product_selector_selects_all_and_only_en(self) -> None:
        ds = _dataset(
            [
                _question("g001", language="en"),
                _question("g002", language="zh"),
                _question("g003", language="mixed"),
                _question("g004", language="en"),
            ]
        )
        self.assertEqual(english_product_case_ids(ds), ["g001", "g004"])

    def test_zh_mixed_remain_outside_formal_product_gate(self) -> None:
        ds = _dataset(
            [
                _question("g001", language="en"),
                _question("g002", language="zh"),
                _question("g003", language="mixed"),
            ]
        )
        product_ids = set(english_product_case_ids(ds))
        self.assertEqual(product_ids, {"g001"})
        self.assertIn("g002", {q.id for q in ds.questions})
        self.assertIn("g003", {q.id for q in ds.questions})

    def test_product_completeness_rejects_missing_and_arbitrary_subset(self) -> None:
        ds = _dataset(
            [
                _question("g001", language="en", expected_status="version_conflict"),
                _question("g002", language="en"),
            ]
        )
        full_records = [
            {
                "id": "g001",
                "intent": "api",
                "expected_status": "version_conflict",
                "required_source_types": ["code"],
                "metrics": {**_perfect_metrics(), "expected_status_correct": True},
            },
            {
                "id": "g002",
                "intent": "api",
                "expected_status": "answered",
                "required_source_types": ["code"],
                "metrics": {**_perfect_metrics(), "expected_status_correct": True},
            },
        ]
        metrics = aggregate_metrics(full_records)
        full_gate = evaluate_product_development_gate(metrics, full_records, ds)
        self.assertTrue(full_gate["product_scope"]["complete"])

        subset_records = [full_records[1]]
        subset_metrics = aggregate_metrics(subset_records)
        subset_gate = evaluate_product_development_gate(subset_metrics, subset_records, ds)
        self.assertFalse(subset_gate["product_scope"]["complete"])
        self.assertFalse(subset_gate["passed"])

    def test_offline_rescore_uses_immutable_records_zero_model_calls(self) -> None:
        case = _question("g001", expected_status="answered")
        ds = _dataset([case])
        source = {
            "id": "g001",
            "intent": "api",
            "expected_status": "answered",
            "result": {
                "status": "answered",
                "answer": "",
                "claims": [],
                "evidence": [],
            },
            "diagnostics": {"plan": {"intent": "api"}, "ranked_object_ids": []},
            "model_calls": 3,
            "token_usage": 100,
        }
        rescored = offline_rescore_records([source], ds, {}, mode="retrieval")
        self.assertEqual(len(rescored), 1)
        self.assertEqual(rescored[0]["id"], "g001")
        self.assertEqual(rescored[0]["model_calls"], 3)
        self.assertFalse(
            rescored[0]["metrics"]["metric_applicability"]["expected_status_correct"]
        )
        self.assertEqual(source["result"], rescored[0]["result"])
        self.assertEqual(source["diagnostics"], rescored[0]["diagnostics"])


if __name__ == "__main__":
    unittest.main()
