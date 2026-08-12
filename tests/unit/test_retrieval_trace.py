from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from panda_agent.evaluation_runner import evaluation_mode_boundaries
from panda_agent.retrieval_trace import (
    build_retrieval_trace,
    load_retrieval_trace,
    load_retrieval_traces,
    write_retrieval_trace,
)


class EvaluationModeBoundaryTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
