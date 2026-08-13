from pathlib import Path
from copy import deepcopy
from types import SimpleNamespace
import unittest

from panda_agent.evaluation import load_gold_dataset
from panda_agent.evaluation_runner import default_gold_dataset_path, dry_rescore_run
from panda_agent.baseline import (
    BOOTSTRAP_DEVELOPMENT_SPLITS,
    select_stratified_case_ids,
    validate_baseline_consistency,
)


ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "m6-v2-36-qa-dev-rc3e"


class EvaluationRunnerTests(unittest.TestCase):
    def test_stratified_baseline_selection_is_deterministic_and_intent_balanced(self) -> None:
        dataset = ROOT / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
        first = select_stratified_case_ids(dataset, 24)
        second = select_stratified_case_ids(dataset, 24)
        self.assertEqual(first, second)
        self.assertEqual(len(first), len(set(first)))
        questions = {item.id: item for item in load_gold_dataset(dataset).questions}
        counts: dict[str, int] = {}
        eligible_counts: dict[str, int] = {}
        for item in questions.values():
            if (
                item.language == "en"
                and item.review_status == "approved"
                and item.split in BOOTSTRAP_DEVELOPMENT_SPLITS
            ):
                eligible_counts[item.intent] = eligible_counts.get(item.intent, 0) + 1
        for case_id in first:
            item = questions[case_id]
            self.assertEqual(item.language, "en")
            self.assertIn(item.split, BOOTSTRAP_DEVELOPMENT_SPLITS)
            counts[item.intent] = counts.get(item.intent, 0) + 1
        self.assertEqual(set(counts), set(eligible_counts))
        depleted = {
            intent for intent, available in eligible_counts.items() if counts[intent] == available
        }
        self.assertEqual(depleted, {"algorithm_implementation"})
        balanced_counts = [count for intent, count in counts.items() if intent not in depleted]
        self.assertLessEqual(max(balanced_counts) - min(balanced_counts), 1)

    @staticmethod
    def _baseline_payloads() -> tuple[dict, dict, dict]:
        retrieval = {
            "manifest": {
                "mode": "retrieval",
                "pipeline_boundaries": {"external_judge": False},
            },
            "records": [{"id": "r1"}, {"id": "r2"}],
            "traces": [
                SimpleNamespace(question_id="r1"),
                SimpleNamespace(question_id="r2"),
            ],
        }
        qa = {
            "manifest": {
                "mode": "qa",
                "pipeline_boundaries": {"external_judge": False},
            },
            "records": [
                {
                    "id": "q1",
                    "model_call_breakdown": {"judge": {"model_calls": 0}},
                }
            ],
            "traces": [SimpleNamespace(question_id="q1")],
        }
        fixed = {
            "retrieval": {"mode": "retrieval", "case_ids": ["r1", "r2"], "case_count": 2},
            "qa": {
                "mode": "qa",
                "external_judge": False,
                "case_ids": ["q1"],
                "case_count": 1,
            },
        }
        return fixed, retrieval, qa

    def test_baseline_consistency_accepts_matching_fixed_records_and_traces(self) -> None:
        fixed, retrieval, qa = self._baseline_payloads()
        validate_baseline_consistency(fixed, retrieval, qa)

    def test_baseline_consistency_rejects_boundary_id_trace_and_judge_mismatches(self) -> None:
        mutations = {
            "fixed IDs": lambda fixed, retrieval, qa: fixed["qa"]["case_ids"].append("q2"),
            "retrieval trace": lambda fixed, retrieval, qa: retrieval["traces"].pop(),
            "QA trace": lambda fixed, retrieval, qa: setattr(
                qa["traces"][0], "question_id", "wrong"
            ),
            "QA mode": lambda fixed, retrieval, qa: qa["manifest"].update(
                {"mode": "full"}
            ),
            "external judge boundary": lambda fixed, retrieval, qa: qa[
                "manifest"
            ]["pipeline_boundaries"].update({"external_judge": True}),
            "judge calls": lambda fixed, retrieval, qa: qa["records"][0][
                "model_call_breakdown"
            ]["judge"].update({"model_calls": 1}),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                fixed, retrieval, qa = deepcopy(self._baseline_payloads())
                mutate(fixed, retrieval, qa)
                with self.assertRaises(ValueError):
                    validate_baseline_consistency(fixed, retrieval, qa)

    def test_v26_is_default_and_signed_dry_rescore_preserves_real_failures(self) -> None:
        dataset = ROOT / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
        self.assertEqual(default_gold_dataset_path(ROOT), dataset)
        result = dry_rescore_run(
            ROOT,
            "m6-v2-36-qa-regression-rc3f",
            dataset,
            case_ids=[
                "g087", "g090", "g092", "g093", "g094", "g097", "g099",
                "g100", "g101", "g103", "g104", "g106", "g109", "g116",
            ],
        )
        records = {item["id"]: item for item in result["records"]}
        for case_id in (
            "g090", "g092", "g093", "g094", "g099", "g100", "g101",
            "g103", "g104", "g106", "g109",
        ):
            self.assertEqual(records[case_id]["metrics"]["final_evidence_recall"], 1.0)
        self.assertTrue(records["g094"]["metrics"]["intent_correct"])
        self.assertEqual(records["g109"]["metrics"]["hallucinated_identifiers"], [])
        for case_id in ("g087", "g097", "g116"):
            self.assertEqual(records[case_id]["rescore_provenance"]["human_adjudicated_fields"], [])
        self.assertEqual(records["g087"]["metrics"]["critical_answer_points_missing"], ["p1"])
        self.assertEqual(records["g097"]["metrics"]["critical_answer_points_missing"], ["p2"])
        self.assertEqual(
            records["g116"]["metrics"]["critical_answer_points_missing"],
            ["p1", "p2", "p3"],
        )
        self.assertEqual(result["rescore_model_calls"], 0)
        self.assertEqual(result["rescore_token_usage"], 0)
