from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from panda_agent.evaluation import (
    GoldDataset,
    GoldQuestion,
    aggregate_metrics,
    effective_product_language,
    english_product_case_ids,
    evaluate_product_development_gate,
    load_product_language_calibration,
    offline_rescore_records,
    validate_product_language_calibration,
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


def _calibration(overrides: list[dict], english_ids: list[str], non_ids: list[str]) -> dict:
    return {
        "calibration_id": "test_calibration_v1",
        "source_gold": {"version": "m6-benchmark-v2.6", "sha256": "x", "path": "gold.yaml"},
        "source_t3_manifest": "phase_b_t3_retrieval_v1",
        "source_run_id": "phase-b-t3-retrieval-20260816",
        "scope": {"split": "dev"},
        "classification_rule": "natural-language grammar",
        "raw_language_distribution": {"en": 0, "zh": 0, "mixed": 0},
        "reviewed_overrides": overrides,
        "formal_english_ids": english_ids,
        "non_english_ids": non_ids,
        "counts": {"formal_english": len(english_ids), "non_english": len(non_ids)},
    }


class T31R1ProductScopeTests(unittest.TestCase):
    def test_calibration_validation_accepts_valid_and_rejects_bad(self) -> None:
        cal = _calibration(
            [{"case_id": "g105", "raw_language": "mixed", "effective_product_language": "en", "reason": "x"}],
            ["g105"],
            ["g102"],
        )
        validate_product_language_calibration(cal)  # no raise
        bad = _calibration([], ["g105"], ["g105"])
        with self.assertRaises(ValueError):
            validate_product_language_calibration(bad)

    def test_mixed_reviewed_english_enters_formal_scope(self) -> None:
        ds = _dataset(
            [
                _question("g102", language="mixed"),
                _question("g105", language="mixed"),
            ]
        )
        cal = _calibration(
            [
                {"case_id": "g102", "raw_language": "mixed", "effective_product_language": "non_en", "reason": "zh grammar"},
                {"case_id": "g105", "raw_language": "mixed", "effective_product_language": "en", "reason": "en grammar"},
            ],
            ["g105"],
            ["g102"],
        )
        self.assertEqual(english_product_case_ids(ds, calibration=cal), ["g105"])

    def test_raw_zh_with_english_identifiers_stays_non_en(self) -> None:
        ds = _dataset([_question("g063", language="zh")])
        cal = _calibration([], [], ["g063"])
        self.assertEqual(effective_product_language(ds.questions[0], cal), "zh")
        self.assertEqual(english_product_case_ids(ds, calibration=cal), [])

    def test_formal_selector_derives_exact_expected_ids(self) -> None:
        ds = _dataset(
            [
                _question("g001", language="en"),
                _question("g105", language="mixed"),
                _question("g102", language="mixed"),
                _question("g063", language="zh"),
            ]
        )
        cal = _calibration(
            [
                {"case_id": "g105", "raw_language": "mixed", "effective_product_language": "en", "reason": "en"},
                {"case_id": "g102", "raw_language": "mixed", "effective_product_language": "non_en", "reason": "zh"},
            ],
            ["g001", "g105"],
            ["g063", "g102"],
        )
        self.assertEqual(english_product_case_ids(ds, calibration=cal), ["g001", "g105"])

    def test_missing_formal_record_fails_completeness(self) -> None:
        ds = _dataset([_question("g001", language="en"), _question("g002", language="en")])
        cal = _calibration([], ["g001", "g002"], [])
        records = [
            {
                "id": "g001",
                "intent": "api",
                "expected_status": "answered",
                "required_source_types": ["code"],
                "metrics": {"intent_correct": True, "gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True, "wrong_version_evidence": [], "forbidden_evidence": [], "expected_status_correct": True},
            }
        ]
        metrics = aggregate_metrics(records)
        gate = evaluate_product_development_gate(metrics, records, ds, calibration=cal)
        self.assertFalse(gate["product_scope"]["complete"])
        self.assertFalse(gate["passed"])

    def test_extra_non_scope_record_fails_exact_completeness(self) -> None:
        ds = _dataset([_question("g001", language="en"), _question("g102", language="mixed")])
        cal = _calibration(
            [{"case_id": "g102", "raw_language": "mixed", "effective_product_language": "non_en", "reason": "zh"}],
            ["g001"],
            ["g102"],
        )
        records = [
            {
                "id": "g001",
                "intent": "api",
                "expected_status": "answered",
                "required_source_types": ["code"],
                "metrics": {"intent_correct": True, "gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True, "wrong_version_evidence": [], "forbidden_evidence": [], "expected_status_correct": True},
            },
            {
                "id": "g102",
                "intent": "api",
                "expected_status": "answered",
                "required_source_types": ["code"],
                "metrics": {"intent_correct": True, "gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True, "wrong_version_evidence": [], "forbidden_evidence": [], "expected_status_correct": True},
            },
        ]
        metrics = aggregate_metrics(records)
        gate = evaluate_product_development_gate(metrics, records, ds, calibration=cal)
        self.assertFalse(gate["product_scope"]["complete"])

    def test_arbitrary_subset_cannot_pass_formal_gate(self) -> None:
        ds = _dataset([_question("g001", language="en"), _question("g002", language="en")])
        cal = _calibration([], ["g001", "g002"], [])
        record = {
            "id": "g001",
            "intent": "api",
            "expected_status": "answered",
            "required_source_types": ["code"],
            "metrics": {"intent_correct": True, "gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True, "wrong_version_evidence": [], "forbidden_evidence": [], "expected_status_correct": True},
        }
        metrics = aggregate_metrics([record])
        gate = evaluate_product_development_gate(metrics, [record], ds, calibration=cal)
        self.assertFalse(gate["product_scope"]["complete"])
        self.assertFalse(gate["passed"])

    def test_load_calibration_validates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "calibration.json"
            cal = _calibration([], ["g001"], [])
            path.write_text(json.dumps(cal), encoding="utf-8")
            loaded = load_product_language_calibration(Path(tmp), path=path)
            self.assertEqual(loaded["calibration_id"], "test_calibration_v1")

    def test_offline_rescore_zero_model_calls(self) -> None:
        case = _question("g001", expected_status="answered")
        ds = _dataset([case])
        source = {
            "id": "g001",
            "intent": "api",
            "expected_status": "answered",
            "result": {"status": "answered", "answer": "", "claims": [], "evidence": []},
            "diagnostics": {"plan": {"intent": "api"}, "ranked_object_ids": []},
            "model_calls": 3,
            "token_usage": 100,
        }
        rescored = offline_rescore_records([source], ds, {}, mode="retrieval")
        self.assertEqual(rescored[0]["model_calls"], 3)
        self.assertFalse(rescored[0]["metrics"]["metric_applicability"]["expected_status_correct"])

    def test_report_evaluation_emits_product_development_gate(self) -> None:
        from panda_agent.evaluation import load_gold_dataset
        from panda_agent.evaluation_runner import report_evaluation

        real_root = Path(__file__).resolve().parents[2]
        gold_path = real_root / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
        dataset = load_gold_dataset(gold_path)
        dev_ids = [
            str(item.id) for item in dataset.questions if item.split == "dev"
        ]
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "data" / "evaluation" / "runs" / "product-gate-test"
            run_dir.mkdir(parents=True)
            manifest = {
                "mode": "retrieval",
                "split": "dev",
                "official": True,
                "limit": None,
                "case_ids": None,
                "gold_dataset_path": str(gold_path),
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            lines = []
            for cid in dev_ids:
                lines.append(
                    json.dumps(
                        {
                            "id": cid,
                            "intent": "api",
                            "expected_status": "answered",
                            "required_source_types": ["code"],
                            "duration_ms": 1,
                            "metrics": {
                                "intent_correct": True,
                                "gold_recall_at_10": 1.0,
                                "final_evidence_recall": 1.0,
                                "critical_final_evidence_recall": 1.0,
                                "required_source_coverage": True,
                                "wrong_version_evidence": [],
                                "forbidden_evidence": [],
                                "expected_status_correct": True,
                            },
                        }
                    )
                )
            (run_dir / "results.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
            calibration = _calibration([], [], [])
            sentinel = {"passed": True, "product_scope": {"complete": True}}
            with mock.patch(
                "panda_agent.evaluation_runner.load_product_language_calibration",
                return_value=calibration,
            ), mock.patch(
                "panda_agent.evaluation_runner.evaluate_product_development_gate",
                return_value=sentinel,
            ), mock.patch(
                "panda_agent.evaluation_runner.write_failure_review",
                return_value={},
            ):
                report = report_evaluation(Path(tmp), "product-gate-test")
            self.assertEqual(report["product_development_gate"], sentinel)
            self.assertTrue((run_dir / "product_development_gate.json").exists())


if __name__ == "__main__":
    unittest.main()
