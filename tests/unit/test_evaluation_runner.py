from pathlib import Path
import unittest

from panda_agent.evaluation import load_gold_dataset
from panda_agent.evaluation_runner import default_gold_dataset_path, dry_rescore_run
from panda_agent.baseline import select_stratified_case_ids


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
            if item.language == "en" and item.review_status == "approved":
                eligible_counts[item.intent] = eligible_counts.get(item.intent, 0) + 1
        for case_id in first:
            item = questions[case_id]
            self.assertEqual(item.language, "en")
            counts[item.intent] = counts.get(item.intent, 0) + 1
        self.assertEqual(set(counts), set(eligible_counts))
        depleted = {
            intent for intent, available in eligible_counts.items() if counts[intent] == available
        }
        self.assertEqual(depleted, {"algorithm_implementation"})
        balanced_counts = [count for intent, count in counts.items() if intent not in depleted]
        self.assertLessEqual(max(balanced_counts) - min(balanced_counts), 1)

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
