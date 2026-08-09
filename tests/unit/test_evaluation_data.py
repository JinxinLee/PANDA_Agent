from pathlib import Path
import unittest
import yaml


class EvaluationDataTests(unittest.TestCase):
    def test_m4_dataset_has_thirty_unique_questions(self):
        root=Path(__file__).resolve().parents[2]
        questions=yaml.safe_load((root/"evaluation"/"retrieval_questions.yaml").read_text(encoding="utf-8"))["questions"]
        self.assertGreaterEqual(len(questions),30)
        self.assertEqual(len({item["id"] for item in questions}),len(questions))
        self.assertEqual({item["intent"] for item in questions},{"installation","usage","api","algorithm_theory","algorithm_implementation","data_flow","module_structure","troubleshooting"})

    def test_m5_dataset_has_three_questions_per_intent(self):
        root=Path(__file__).resolve().parents[2]
        questions=yaml.safe_load((root/"evaluation"/"qa_questions.yaml").read_text(encoding="utf-8"))["questions"]
        counts={intent:sum(item["intent"]==intent for item in questions) for intent in {item["intent"] for item in questions}}
        self.assertTrue(all(count>=3 for count in counts.values()))
        self.assertEqual(len(counts),8)


if __name__ == "__main__": unittest.main()
