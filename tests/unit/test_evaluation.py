import unittest

from panda_agent.evaluation import GoldQuestion, deterministic_case_metrics


class EvaluationTests(unittest.TestCase):
    def test_novel_question_contract_accepts_external_novel_splits(self) -> None:
        case = GoldQuestion.model_validate(
            {
                "id": "n001",
                "split": "novel_dev",
                "language": "en",
                "intent": "api",
                "query": "Which component owns this API boundary?",
                "expected_status": "answered",
                "allowed_source_versions": ["pandaroot@abc"],
                "required_evidence_groups": [
                    {
                        "group_id": "n001.e1",
                        "role": "api_boundary",
                        "any_of": [{"source_id": "pandaroot"}],
                    }
                ],
                "required_answer_points": [
                    {"point_id": "p1", "text": "Identify the owning component."}
                ],
            }
        )
        self.assertEqual(case.id, "n001")
        self.assertEqual(case.split, "novel_dev")

    def test_accepted_intent_allows_a_reviewed_plan_intent(self) -> None:
        case = GoldQuestion.model_validate(
            {
                "id": "g998",
                "split": "dev",
                "language": "en",
                "intent": "algorithm_implementation",
                "accepted_intents": ["module_structure"],
                "query": "Why is this composition not a class?",
                "expected_status": "answered",
                "allowed_source_versions": ["repo@locked"],
                "required_evidence_groups": [
                    {
                        "group_id": "g998.e1",
                        "role": "reviewed_composition",
                        "critical": True,
                        "any_of": [{"object_id": "reviewed.object"}],
                    }
                ],
                "required_answer_points": ["Explain the reviewed composition."],
            }
        )
        metrics = deterministic_case_metrics(
            case,
            {"status": "answered", "answer": "It is composed from reviewed objects.", "claims": []},
            {"plan": {"intent": "module_structure"}, "ranked_object_ids": []},
            {},
        )
        self.assertTrue(metrics["intent_correct"])

    def test_final_evidence_uses_immutable_record_snapshot_when_lookup_is_rebuilt(self) -> None:
        case = GoldQuestion.model_validate(
            {
                "id": "g999",
                "split": "dev",
                "language": "en",
                "intent": "api",
                "query": "Where is the reviewed object?",
                "expected_status": "answered",
                "allowed_source_versions": ["repo@locked"],
                "required_evidence_groups": [
                    {
                        "group_id": "g999.e1",
                        "role": "reviewed_object",
                        "critical": True,
                        "any_of": [{"object_id": "immutable.object"}],
                    }
                ],
                "required_answer_points": ["Locate the reviewed object."],
            }
        )
        metrics = deterministic_case_metrics(
            case,
            {
                "status": "answered",
                "answer": "Located it.",
                "claims": [],
                "evidence": [
                    {
                        "evidence_id": "e1",
                        "object_id": "immutable.object",
                        "source_id": "repo",
                        "source_version_id": "repo@locked",
                        "locator": {"path": "reviewed.cxx"},
                    }
                ],
            },
            {"plan": {"intent": "api"}, "ranked_object_ids": []},
            {},
        )
        self.assertEqual(metrics["final_evidence_recall"], 1.0)
        self.assertEqual(
            metrics["evidence_match_provenance"]["final_evidence_recall"][0]["provenance"],
            "direct",
        )
