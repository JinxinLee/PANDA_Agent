from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from panda_agent.evaluation import (
    GoldQuestion,
    aggregate_metrics,
    apply_mode_metric_semantics,
    evaluate_development_gate,
    evaluate_quality_gate,
)
from panda_agent.evaluation_runner import (
    _execute_evaluation_case,
    evaluation_mode_boundaries,
)
from panda_agent.retrieval_trace import (
    RetrievalTrace,
    build_retrieval_trace,
    load_retrieval_trace,
    load_retrieval_traces,
    write_retrieval_trace,
)


class EvaluationModeBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case = GoldQuestion.model_validate(
            {
                "id": "g001",
                "split": "dev",
                "language": "en",
                "intent": "installation",
                "query": "How is PandaRoot installed?",
                "expected_status": "answered",
                "allowed_source_versions": ["pandaroot@test"],
                "required_evidence_groups": [
                    {"group_id": "e1", "any_of": [{"object_id": "object.test"}]}
                ],
                "required_answer_points": [
                    {"point_id": "p1", "text": "Explain installation."}
                ],
            }
        )

    def test_modes_do_not_cross_declared_pipeline_boundaries(self) -> None:
        self.assertEqual(
            evaluation_mode_boundaries("retrieval"),
            {
                "answer_generation": False,
                "runtime_verification": False,
                "external_judge": False,
            },
        )
        self.assertEqual(
            evaluation_mode_boundaries("qa"),
            {
                "answer_generation": True,
                "runtime_verification": True,
                "external_judge": False,
            },
        )
        self.assertEqual(
            evaluation_mode_boundaries("full"),
            {
                "answer_generation": True,
                "runtime_verification": True,
                "external_judge": True,
            },
        )

    @staticmethod
    def _diagnostics(intent: str) -> dict:
        return {
            "plan": {"intent": intent, "resolved_versions": {}},
            "rankings": {},
            "reranked_object_ids": [],
            "selected_evidence": [],
            "evidence": [],
        }

    def test_retrieval_executes_retriever_only(self) -> None:
        class FakeRetriever:
            def __init__(self, diagnostics: dict) -> None:
                self.diagnostics = diagnostics
                self.retrieve_calls = 0

            def retrieve(self, query: str) -> dict:
                self.retrieve_calls += 1
                return self.diagnostics

            def run_detailed(self, query: str) -> dict:
                raise AssertionError("retrieval mode entered QAAgent.run_detailed")

        engine = FakeRetriever(self._diagnostics(self.case.intent))
        with patch("panda_agent.evaluation_runner.judge_answer") as judge:
            _, _, metrics = _execute_evaluation_case(
                engine, None, mode="retrieval", case=self.case, object_lookup={}
            )
        self.assertEqual(engine.retrieve_calls, 1)
        judge.assert_not_called()
        self.assertNotIn("citation_integrity", metrics)
        self.assertFalse(metrics["metric_applicability"]["answer_point_coverage"])

    def test_qa_executes_qa_agent_without_external_judge(self) -> None:
        class FakeQAAgent:
            run_detailed_calls = 0

            def run_detailed(self, query: str) -> dict:
                self.run_detailed_calls += 1
                return {
                    "result": {
                        "status": "insufficient_evidence",
                        "answer": "",
                        "claims": [],
                        "evidence": [],
                        "resolved_versions": {},
                        "verification_errors": [],
                    },
                    "diagnostics": EvaluationModeBoundaryTests._diagnostics(
                        EvaluationModeBoundaryTests.case.intent
                    ),
                }

        engine = FakeQAAgent()
        with patch("panda_agent.evaluation_runner.judge_answer") as judge:
            _, _, metrics = _execute_evaluation_case(
                engine, None, mode="qa", case=self.case, object_lookup={}
            )
        self.assertEqual(engine.run_detailed_calls, 1)
        judge.assert_not_called()
        self.assertIn("citation_integrity", metrics)
        self.assertNotIn("answer_point_coverage", metrics)

    def test_full_executes_qa_agent_and_external_judge(self) -> None:
        class FakeQAAgent:
            run_detailed_calls = 0

            def run_detailed(self, query: str) -> dict:
                self.run_detailed_calls += 1
                return {
                    "result": {
                        "status": "insufficient_evidence",
                        "answer": "",
                        "claims": [],
                        "evidence": [],
                        "resolved_versions": {},
                        "verification_errors": [],
                    },
                    "diagnostics": EvaluationModeBoundaryTests._diagnostics(
                        EvaluationModeBoundaryTests.case.intent
                    ),
                }

        judged = {
            "answer_point_coverage": 1.0,
            "covered_point_ids": [],
            "critical_answer_points_missing": [],
            "contradictions": [],
            "unsupported_claim_ids": [],
            "major_unsupported_claim_ids": [],
            "minor_unsupported_claim_ids": [],
            "claim_verdicts": [],
        }
        engine = FakeQAAgent()
        with patch(
            "panda_agent.evaluation_runner.judge_answer", return_value=judged
        ) as judge:
            _, _, metrics = _execute_evaluation_case(
                engine, object(), mode="full", case=self.case, object_lookup={}
            )
        self.assertEqual(engine.run_detailed_calls, 1)
        judge.assert_called_once()
        self.assertEqual(metrics["answer_point_coverage"], 1.0)
        self.assertTrue(metrics["metric_applicability"]["contradictions"])


class RetrievalTraceTests(unittest.TestCase):
    def test_trace_round_trip_preserves_layered_candidates_and_raw_queries(self) -> None:
        diagnostics = {
            "plan": {
                "intent": "api",
                "concepts": ["track quality"],
                "symbols": ["PndLmdTrackQ"],
            },
            "rankings": {"dense": ["o2", "o1"], "exact": ["o1"]},
            "fusion_scores": {"o1": 0.3, "o2": 0.2},
            "reranked_object_ids": ["o2", "o1"],
            "selected_evidence": [
                {
                    "evidence_id": "e1",
                    "object_id": "o1",
                    "source_id": "pandaroot",
                    "source_version_id": "pandaroot@abc",
                    "text": "evidence",
                    "locator": {"path": "src/a.cxx", "start_line": 4, "end_line": 8},
                    "retrieval_channels": ["exact", "dense"],
                    "score": 0.3,
                    "authority_level": "primary",
                }
            ],
            "excluded": [{"object_id": "o3", "reason": "source_budget_cap"}],
        }
        object_lookup = {
            "o1": {
                "object_id": "o1",
                "source_id": "pandaroot",
                "source_version_id": "pandaroot@abc",
                "object_type": "function",
                "locator": {"path": "src/a.cxx", "start_line": 4, "end_line": 8},
            },
            "o2": {
                "object_id": "o2",
                "source_id": "luminosityfit",
                "source_version_id": "luminosityfit@def",
                "object_type": "class",
                "locator": {"path": "model/b.cxx"},
            },
        }
        trace = build_retrieval_trace(
            question_id="g001",
            run_id="trace-test",
            question="Where is PndLmdTrackQ implemented?",
            diagnostics=diagnostics,
            manifest={"mode": "retrieval", "prompt_version": "test"},
            object_lookup=object_lookup,
        )
        self.assertEqual(trace.dense_query_text, trace.raw_question)
        self.assertEqual(trace.sparse_query_text, trace.raw_question)
        self.assertEqual(trace.channel_candidates["exact"][0].source_id, "pandaroot")
        self.assertEqual(trace.fused_candidates[0].channels, ["dense", "exact"])
        self.assertEqual(trace.reranked_candidates[0].object_id, "o2")
        self.assertEqual(trace.final_evidence[0]["evidence_id"], "e1")

        with TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            path = write_retrieval_trace(run_dir, trace)
            self.assertEqual(load_retrieval_trace(path), trace)
            self.assertEqual(load_retrieval_traces(run_dir), [trace])

    def test_trace_default_marks_semantic_absent_and_keeps_raw_candidates(self) -> None:
        question = "How does the raw dense path work?"
        trace = build_retrieval_trace(
            question_id="g002",
            run_id="trace-default",
            question=question,
            diagnostics={
                "plan": {},
                "rankings": {"dense": ["raw-1"], "exact": []},
                "fusion_scores": {"raw-1": 0.4},
                "dense_candidates": {"raw": ["raw-1"], "semantic": None},
            },
            manifest={},
            object_lookup={},
        )

        self.assertEqual(trace.dense_query_text, question)
        self.assertEqual(trace.dense_queries["raw"]["text"], question)
        self.assertEqual(trace.dense_queries["raw"]["provenance"], "user_raw")
        self.assertIsNone(trace.dense_queries["semantic"])
        self.assertFalse(trace.dense_queries["semantic_active"])
        self.assertFalse(trace.dense_queries["semantic_executed"])
        self.assertEqual(trace.dense_candidates["raw"], ["raw-1"])
        self.assertIsNone(trace.dense_candidates["semantic"])

    def test_trace_shadow_candidates_and_contamination_remain_observable(self) -> None:
        question = "Where is the function defined?"
        raw_payload = {"object_id": "raw-1", "score": 0.9}
        semantic_payload = {"object_id": "semantic-only", "score": 0.8}
        diagnostics = {
            "plan": {},
            "dense_queries": {
                "raw": {"text": question, "provenance": "user_raw", "active": True},
                "semantic": {
                    "text": f"{question}\n\nSemantic focus:\nfunction",
                    "components": [
                        {"kind": "analyzer_concept", "value": "function", "provenance": "analyzer_accepted"}
                    ],
                    "provenance": "semantic_query",
                    "active": True,
                    "executed": True,
                },
                "semantic_active": True,
                "semantic_executed": True,
            },
            "dense_candidates": {"raw": [raw_payload], "semantic": [semantic_payload]},
            "rankings": {"dense": ["raw-1", "semantic-only"], "exact": []},
            "fusion_scores": {"raw-1": 0.9, "semantic-only": 0.8},
            "reranked_object_ids": ["semantic-only", "raw-1"],
        }
        trace = build_retrieval_trace(
            question_id="g003",
            run_id="trace-shadow",
            question=question,
            diagnostics=diagnostics,
            manifest={},
            object_lookup={},
        )

        self.assertEqual(trace.dense_queries["raw"]["text"], question)
        self.assertEqual(trace.dense_queries["semantic"]["text"], diagnostics["dense_queries"]["semantic"]["text"])
        self.assertEqual(trace.dense_candidates["raw"], [raw_payload])
        self.assertEqual(trace.dense_candidates["semantic"], [semantic_payload])
        self.assertEqual(
            [item.object_id for item in trace.channel_candidates["dense"]],
            ["raw-1", "semantic-only"],
        )
        self.assertEqual(
            [item.object_id for item in trace.fused_candidates],
            ["raw-1", "semantic-only"],
        )
        self.assertEqual(
            [item.object_id for item in trace.reranked_candidates],
            ["semantic-only", "raw-1"],
        )

    def test_legacy_trace_without_dense_fields_remains_loadable(self) -> None:
        legacy = {
            "question_id": "legacy",
            "run_id": "run",
            "implementation_identity": {},
            "raw_question": "legacy question",
            "retrieval_plan": {},
            "original_retrieval_query": "legacy question",
            "dense_query_text": "legacy question",
            "sparse_query_text": "legacy question",
        }

        trace = RetrievalTrace.model_validate(legacy)

        self.assertEqual(trace.dense_query_text, trace.raw_question)
        self.assertEqual(trace.dense_queries["raw"]["text"], trace.raw_question)
        self.assertIsNone(trace.dense_queries["semantic"])
        self.assertIsNone(trace.dense_candidates["semantic"])


class MetricApplicabilityTests(unittest.TestCase):
    @staticmethod
    def _record(metrics: dict) -> dict:
        return {
            "id": "g001",
            "intent": "installation",
            "expected_status": "answered",
            "required_source_types": [],
            "metrics": metrics,
        }

    def test_unjudged_metrics_are_not_synthetic_failures_or_clean_passes(self) -> None:
        metrics = apply_mode_metric_semantics(
            {
                "intent_correct": True,
                "expected_status_correct": True,
                "citation_integrity": True,
                "missing_identifiers": [],
                "identifier_mentions": [],
                "hallucinated_identifiers": [],
                "answer_point_coverage": 0.0,
                "contradictions": [],
                "unsupported_claim_ids": [],
            },
            mode="qa",
            external_judge=False,
        )
        aggregate = aggregate_metrics([self._record(metrics)])
        self.assertNotIn("answer_point_coverage", metrics)
        self.assertNotIn("contradictions", metrics)
        self.assertNotIn("unsupported_claim_ids", metrics)
        self.assertIsNone(aggregate["answer_point_coverage"])
        self.assertEqual(aggregate["answer_point_coverage_denominator"], 0)
        self.assertIsNone(aggregate["contradiction_count"])
        self.assertIsNone(aggregate["unsupported_claim_count"])
        self.assertFalse(aggregate["metric_applicability"]["contradictions"])
        development_gate = evaluate_development_gate(
            aggregate,
            [self._record(metrics)],
            mode="qa",
            complete_full_dev=False,
            all_questions_approved=True,
        )
        self.assertNotIn("answer_point_coverage", development_gate["checks"])
        self.assertNotIn("no_contradictions", development_gate["checks"])

    def test_full_judged_metrics_retain_measured_clean_zero_semantics(self) -> None:
        metrics = apply_mode_metric_semantics(
            {
                "intent_correct": True,
                "expected_status_correct": True,
                "citation_integrity": True,
                "missing_identifiers": [],
                "identifier_mentions": [],
                "hallucinated_identifiers": [],
                "answer_point_coverage": 1.0,
                "covered_point_ids": ["p1"],
                "critical_answer_points_missing": [],
                "contradictions": [],
                "unsupported_claim_ids": [],
                "major_unsupported_claim_ids": [],
                "minor_unsupported_claim_ids": [],
                "claim_verdicts": [],
            },
            mode="full",
            external_judge=True,
        )
        aggregate = aggregate_metrics([self._record(metrics)])
        self.assertEqual(aggregate["answer_point_coverage"], 1.0)
        self.assertEqual(aggregate["answer_point_coverage_denominator"], 1)
        self.assertEqual(aggregate["contradiction_count"], 0)
        self.assertEqual(aggregate["unsupported_claim_count"], 0)
        self.assertTrue(aggregate["metric_applicability"]["contradictions"])
        development_gate = evaluate_development_gate(
            aggregate,
            [self._record(metrics)],
            mode="full",
            complete_full_dev=False,
            all_questions_approved=True,
        )
        self.assertIn("answer_point_coverage", development_gate["checks"])
        self.assertTrue(development_gate["checks"]["no_contradictions"])

    def test_retrieval_answer_metrics_are_explicitly_not_applicable(self) -> None:
        metrics = apply_mode_metric_semantics(
            {
                "intent_correct": True,
                "expected_status_correct": True,
                "citation_integrity": True,
                "missing_identifiers": [],
                "identifier_mentions": [],
                "hallucinated_identifiers": [],
            },
            mode="retrieval",
            external_judge=False,
        )
        aggregate = aggregate_metrics([self._record(metrics)])
        self.assertNotIn("citation_integrity", metrics)
        self.assertIsNone(aggregate["citation_integrity"])
        self.assertIsNone(aggregate["identifier_hallucination_rate"])
        self.assertFalse(aggregate["metric_applicability"]["citation_integrity"])
        formal_gate = evaluate_quality_gate(
            aggregate,
            [self._record(metrics)],
            official=False,
            all_questions_approved=True,
        )
        self.assertFalse(formal_gate["passed"])


if __name__ == "__main__":
    unittest.main()
