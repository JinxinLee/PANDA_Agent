from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from panda_agent.evaluation import (
    GoldDataset,
    GoldQuestion,
    calibration_compatibility,
    derive_product_language_ids,
    evaluate_product_development_gate,
    stage_trace_for_object,
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


def _dataset() -> GoldDataset:
    return GoldDataset(
        schema_version="2.0",
        benchmark_version="m6-benchmark-v2.6",
        questions=[
            _question("g001", language="en"),
            _question("g002", language="en"),
            _question("g102", language="mixed"),
            _question("g105", language="mixed"),
            _question("g063", language="zh"),
        ],
        release_eligible=True,
        acceptance_exposed=False,
        expected_split_counts={"dev": 5},
        expected_status_counts={},
    )


def _calibration(
    *,
    version: str = "m6-benchmark-v2.6",
    sha256: str = "active-hash",
    split: str = "dev",
    overrides: list | None = None,
    formal: list | None = None,
    non: list | None = None,
) -> dict:
    overrides = overrides if overrides is not None else [
        {
            "case_id": "g102",
            "raw_language": "mixed",
            "effective_product_language": "non_en",
            "reason": "zh grammar",
        },
        {
            "case_id": "g105",
            "raw_language": "mixed",
            "effective_product_language": "en",
            "reason": "en grammar",
        },
    ]
    formal = formal if formal is not None else ["g001", "g002", "g105"]
    non = non if non is not None else ["g063", "g102"]
    return {
        "calibration_id": "test_calibration_v2",
        "source_gold": {"version": version, "sha256": sha256, "path": "gold.yaml"},
        "source_t3_manifest": "phase_b_t3_retrieval_v1",
        "source_run_id": "phase-b-t3-retrieval-20260816",
        "scope": {"split": split},
        "classification_rule": "natural-language grammar",
        "raw_language_distribution": {"en": 2, "zh": 1, "mixed": 2},
        "reviewed_overrides": overrides,
        "formal_english_ids": formal,
        "non_english_ids": non,
        "counts": {"formal_english": len(formal), "non_english": len(non)},
    }


class T31R2CalibrationBindingTests(unittest.TestCase):
    def _compat(self, calibration: dict, dataset_path: Path | None = None):
        return calibration_compatibility(calibration, _dataset(), dataset_path)

    def test_compatible_calibration_passes(self) -> None:
        cal = _calibration()
        result = self._compat(cal)
        self.assertTrue(result["compatible"])

    def test_wrong_gold_version_fails(self) -> None:
        cal = _calibration(version="m6-benchmark-v2.5")
        self.assertFalse(self._compat(cal)["compatible"])

    def test_wrong_gold_sha_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gold.yaml"
            path.write_text("questions: []", encoding="utf-8")
            cal = _calibration(sha256=hashlib.sha256(b"other").hexdigest())
            self.assertFalse(self._compat(cal, path)["compatible"])

    def test_wrong_split_fails(self) -> None:
        cal = _calibration(split="challenge")
        self.assertFalse(self._compat(cal)["compatible"])

    def test_override_unknown_id_fails(self) -> None:
        cal = _calibration(overrides=[
            {"case_id": "nope", "raw_language": "mixed", "effective_product_language": "en", "reason": "x"}
        ])
        self.assertFalse(self._compat(cal)["compatible"])

    def test_override_raw_language_disagrees_fails(self) -> None:
        cal = _calibration(overrides=[
            {"case_id": "g102", "raw_language": "en", "effective_product_language": "non_en", "reason": "x"}
        ])
        self.assertFalse(self._compat(cal)["compatible"])

    def test_declared_formal_differs_from_derived_fails(self) -> None:
        cal = _calibration(formal=["g001", "g105"])  # missing g002
        self.assertFalse(self._compat(cal)["compatible"])

    def test_declared_non_english_differs_from_derived_fails(self) -> None:
        cal = _calibration(non=["g063"])  # missing g102
        self.assertFalse(self._compat(cal)["compatible"])

    def test_union_not_cover_scope_fails(self) -> None:
        cal = _calibration(formal=["g001", "g002", "g105"], non=["g063"])  # g102 missing from both
        self.assertFalse(self._compat(cal)["compatible"])

    def test_foreign_id_in_declared_set_fails(self) -> None:
        cal = _calibration(formal=["g001", "g002", "g105", "g999"], non=["g063", "g102"])
        self.assertFalse(self._compat(cal)["compatible"])

    def test_derived_ids_match_declared_for_valid_calibration(self) -> None:
        cal = _calibration()
        derived_en, derived_non = derive_product_language_ids(_dataset(), cal)
        self.assertEqual(derived_en, cal["formal_english_ids"])
        self.assertEqual(derived_non, cal["non_english_ids"])


class T31R2RankSemanticsTests(unittest.TestCase):
    def _trace(self) -> dict:
        return {
            "rankings": {
                "exact": ["obj.a"],
                "dense": ["obj.b", "obj.target"],
            },
            "fusion_scores": {"obj.a": 1.0, "obj.b": 0.8, "obj.target": 0.7},
            "reranked_object_ids": ["obj.a", "obj.target", "obj.b"],
            "ranked_object_ids": ["obj.a", "obj.b", "obj.target"],
        }

    def test_reranker_and_final_ranked_rank_are_separate(self) -> None:
        trace = self._trace()
        result = {"evidence": [{"object_id": "obj.target"}]}
        stage = stage_trace_for_object(trace, result, "obj.target")
        self.assertEqual(stage["reranker_rank_1based"], 2)
        self.assertEqual(stage["final_ranked_rank_1based"], 3)

    def test_reranker_rank_10_but_final_ranked_rank_11(self) -> None:
        reranked = [f"obj.{i}" for i in range(1, 10)] + ["obj.target", "obj.10"]
        final_ranked = [f"obj.{i}" for i in range(1, 11)] + ["obj.target"]
        trace = {
            "rankings": {"dense": ["obj.target"]},
            "fusion_scores": {oid: 1.0 for oid in final_ranked},
            "reranked_object_ids": reranked,
            "ranked_object_ids": final_ranked,
        }
        stage = stage_trace_for_object(trace, {"evidence": []}, "obj.target")
        self.assertEqual(stage["reranker_index_0based"], 9)
        self.assertEqual(stage["reranker_rank_1based"], 10)
        self.assertEqual(stage["final_ranked_index_0based"], 10)
        self.assertEqual(stage["final_ranked_rank_1based"], 11)
        self.assertFalse(stage["final_top10"])
        self.assertTrue(stage["final_top20"])

    def test_final_top10_uses_final_ranked_stage_not_reranker(self) -> None:
        trace = {
            "rankings": {"dense": ["obj.target"]},
            "fusion_scores": {"obj.target": 1.0},
            "reranked_object_ids": ["obj.target"],
            "ranked_object_ids": [f"obj.{i}" for i in range(1, 11)] + ["obj.target"],
        }
        stage = stage_trace_for_object(trace, {"evidence": []}, "obj.target")
        self.assertEqual(stage["reranker_rank_1based"], 1)
        self.assertEqual(stage["final_ranked_rank_1based"], 11)
        self.assertFalse(stage["final_top10"])

    def test_zero_based_and_one_based_agree(self) -> None:
        trace = {
            "rankings": {"dense": ["obj.target"]},
            "fusion_scores": {"obj.target": 1.0},
            "reranked_object_ids": ["obj.target"],
            "ranked_object_ids": [f"obj.{i}" for i in range(10)] + ["obj.target"],
        }
        stage = stage_trace_for_object(trace, {"evidence": []}, "obj.target")
        self.assertEqual(stage["reranker_index_0based"], 0)
        self.assertEqual(stage["reranker_rank_1based"], 1)
        self.assertEqual(stage["final_ranked_index_0based"], 10)
        self.assertEqual(stage["final_ranked_rank_1based"], 11)

    def test_missing_reranker_membership_is_null(self) -> None:
        trace = {
            "rankings": {"dense": ["obj.target"]},
            "fusion_scores": {"obj.target": 1.0},
            "reranked_object_ids": [],
            "ranked_object_ids": ["obj.target"],
        }
        stage = stage_trace_for_object(trace, {"evidence": []}, "obj.target")
        self.assertIsNone(stage["reranker_index_0based"])
        self.assertIsNone(stage["reranker_rank_1based"])
        self.assertEqual(stage["final_ranked_rank_1based"], 1)

    def test_critical_miss_list_only_genuine_misses(self) -> None:
        # Synthetic helper: use stage_trace_for_object to distinguish selected
        # vs not selected; a critical-miss list should keep only final_selected False.
        trace = {
            "rankings": {"dense": ["obj.miss", "obj.ok"]},
            "fusion_scores": {"obj.miss": 1.0, "obj.ok": 0.9},
            "reranked_object_ids": ["obj.miss", "obj.ok"],
            "ranked_object_ids": ["obj.miss", "obj.ok"],
        }
        result = {"evidence": [{"object_id": "obj.ok"}]}
        miss_stage = stage_trace_for_object(trace, result, "obj.miss")
        ok_stage = stage_trace_for_object(trace, result, "obj.ok")
        self.assertFalse(miss_stage["final_selected"])
        self.assertTrue(ok_stage["final_selected"])


class T31R2ReportingCompletenessTests(unittest.TestCase):
    def test_incompatible_calibration_is_not_silently_applied(self) -> None:
        from panda_agent.evaluation import load_gold_dataset
        from panda_agent.evaluation_runner import report_evaluation

        real_root = Path(__file__).resolve().parents[2]
        gold_path = real_root / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
        dataset = load_gold_dataset(gold_path)
        dev_ids = [
            str(item.id) for item in dataset.questions if item.split == "dev"
        ]
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "data" / "evaluation" / "runs" / "bad-cal-run"
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
            bad_cal = _calibration(version="wrong")
            with mock.patch(
                "panda_agent.evaluation_runner.load_product_language_calibration",
                return_value=bad_cal,
            ), mock.patch(
                "panda_agent.evaluation_runner.write_failure_review",
                return_value={},
            ):
                report = report_evaluation(Path(tmp), "bad-cal-run")
            self.assertIsNotNone(report["product_development_gate"])
            self.assertFalse(report["product_development_gate"]["compatible"])


if __name__ == "__main__":
    unittest.main()
