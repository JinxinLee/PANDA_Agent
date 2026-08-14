from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from qdrant_client import models

from panda_agent.models import QAStatus
from panda_agent.retrieval_trace import RetrievalTrace, TraceCandidate
from panda_agent.sparse_evaluation import (
    BASELINE_MANIFEST_RELATIVE,
    build_frozen_query_filter,
    evaluate_sparse,
    identifier_heavy,
    rank_metrics,
)


def _case(case_id: str, *, status: QAStatus = QAStatus.ANSWERED, identifier: str | None = None):
    payload = {
        "id": case_id,
        "split": "dev",
        "language": "en",
        "intent": "api",
        "query": "How does PndTask::Run use config.yaml?" if identifier else "How does the API work?",
        "expected_status": status.value,
        "allowed_source_versions": ["pandaroot@v1"],
        "required_evidence_groups": [
            {
                "group_id": "g1",
                "any_of": [{"object_id": "object.relevant"}],
            }
        ],
        "required_answer_points": [{"point_id": "p1", "text": "A valid answer point"}],
        "required_identifiers": [identifier] if identifier else [],
    }
    from panda_agent.evaluation import GoldQuestion

    return GoldQuestion.model_validate(payload)


class _SparseEncoder:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def query_embed(self, text: str):
        self.queries.append(text)
        yield SimpleNamespace(indices=[3, 8], values=[0.4, 0.2])


class _Qdrant:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def query_points(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            points=[
                SimpleNamespace(payload={"object_id": "object.relevant"}),
                SimpleNamespace(payload={"object_id": "object.other"}),
            ]
        )


class SparseEvaluationTests(unittest.TestCase):
    def test_rank_metrics_and_identifier_rule(self) -> None:
        case = _case("g001", identifier="PndTask")
        lookup = {
            "object.relevant": {
                "object_id": "object.relevant",
                "source_id": "pandaroot",
                "source_version_id": "pandaroot@v1",
                "object_type": "class",
                "locator": {},
            }
        }
        old = rank_metrics(case, ["object.other", "object.relevant"], lookup)
        new = rank_metrics(case, ["object.relevant", "object.other"], lookup)
        self.assertEqual(old["first_relevant_rank"], 2)
        self.assertEqual(new["first_relevant_rank"], 1)
        self.assertEqual(old["recall_at_5"], 1.0)
        self.assertEqual(new["mrr"], 1.0)
        heavy, tokens = identifier_heavy(case)
        self.assertTrue(heavy)
        self.assertIn("PndTask::Run", tokens)
        self.assertIn("config.yaml", tokens)

    def test_filter_matches_frozen_vector_contract(self) -> None:
        query_filter = build_frozen_query_filter(
            {
                "target_repositories": ["pandaroot"],
                "resolved_versions": {"pandaroot": "v1"},
            },
            ["li_2026"],
        )
        self.assertIsInstance(query_filter, models.Filter)
        self.assertEqual(len(query_filter.should), 2)
        repository_scope = query_filter.should[0]
        self.assertEqual(repository_scope.must[0].key, "source_id")
        self.assertEqual(repository_scope.must[0].match.value, "pandaroot")
        self.assertEqual(repository_scope.must[1].match.value, "pandaroot@v1")
        context_scope = query_filter.should[1]
        self.assertIn("curated_panda_domain", context_scope.match.any)

    def test_end_to_end_uses_sparse_only_and_excludes_non_answered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = root / BASELINE_MANIFEST_RELATIVE
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps({"baseline_id": "test", "retrieval": {"case_ids": ["g001", "g002"]}}),
                encoding="utf-8",
            )
            baseline_dir = root / "baseline"
            baseline_dir.mkdir()
            traces = []
            for case_id in ("g001", "g002"):
                traces.append(
                    RetrievalTrace(
                        question_id=case_id,
                        run_id="run",
                        implementation_identity={},
                        raw_question="How does PndTask work?",
                        retrieval_plan={
                            "target_repositories": ["pandaroot"],
                            "resolved_versions": {"pandaroot": "v1"},
                        },
                        original_retrieval_query="How does PndTask work?",
                        dense_query_text="How does PndTask work?",
                        sparse_query_text=f"query {case_id}",
                        channel_candidates={
                            "sparse": [
                                TraceCandidate(object_id="object.other", rank=1),
                                TraceCandidate(object_id="object.relevant", rank=2),
                            ]
                        },
                    )
                )
            (baseline_dir / "benchmark_retrieval_traces.jsonl").write_text(
                "".join(trace.model_dump_json() + "\n" for trace in traces), encoding="utf-8"
            )
            (baseline_dir / "benchmark_retrieval_baseline.jsonl").write_text(
                json.dumps({"id": "g001", "result": {"status": "answered"}})
                + "\n"
                + json.dumps({"id": "g002", "result": {"status": "version_conflict"}})
                + "\n",
                encoding="utf-8",
            )
            dataset = type(
                "Dataset",
                (),
                {"questions": [_case("g001"), _case("g002", status=QAStatus.VERSION_CONFLICT)]},
            )()
            qdrant = _Qdrant()
            encoder = _SparseEncoder()
            with patch("panda_agent.llm.vertex.VertexAIClient") as vertex:
                result = evaluate_sparse(
                    root,
                    baseline_dir,
                    qdrant=qdrant,
                    embedder=encoder,
                    collection_name="test",
                    context_sources=["li_2026"],
                    gold_dataset=dataset,
                    object_lookup={
                        "object.relevant": {
                            "object_id": "object.relevant",
                            "source_id": "pandaroot",
                            "source_version_id": "pandaroot@v1",
                            "locator": {},
                        },
                        "object.other": {
                            "object_id": "object.other",
                            "source_id": "pandaroot",
                            "source_version_id": "pandaroot@v1",
                            "locator": {},
                        },
                    },
                )
            vertex.assert_not_called()
            self.assertEqual(len(qdrant.calls), 2)
            self.assertEqual(len(encoder.queries), 2)
            self.assertEqual(result["call_accounting"]["sparse_queries"], 2)
            self.assertEqual(result["call_accounting"]["sparse_encoder_calls"], 2)
            self.assertEqual(result["call_accounting"]["generation_calls"], 0)
            self.assertEqual(result["call_accounting"]["analyzer_calls"], 0)
            self.assertEqual(result["call_accounting"]["dense_embedding_calls"], 0)
            self.assertEqual(result["call_accounting"]["reranker_calls"], 0)
            self.assertEqual(result["call_accounting"]["answer_calls"], 0)
            self.assertEqual(result["call_accounting"]["runtime_verifier_calls"], 0)
            self.assertEqual(result["call_accounting"]["external_judge_calls"], 0)
            self.assertEqual(result["new"]["applicable_case_count"], 1)
            self.assertEqual(result["cases"][1]["applicability_reason"], "expected_status=version_conflict; frozen_result_status=version_conflict")
            self.assertEqual(result["cases"][0]["new"]["first_relevant_rank"], 1)
            self.assertEqual(qdrant.calls[0]["using"], "sparse")

    def test_trace_ids_must_match_manifest_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = root / BASELINE_MANIFEST_RELATIVE
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps({"retrieval": {"case_ids": ["g001"]}}), encoding="utf-8"
            )
            baseline_dir = root / "baseline"
            baseline_dir.mkdir()
            trace = RetrievalTrace(
                question_id="g002",
                run_id="run",
                implementation_identity={},
                raw_question="question",
                retrieval_plan={},
                original_retrieval_query="question",
                dense_query_text="question",
                sparse_query_text="question",
            )
            (baseline_dir / "benchmark_retrieval_traces.jsonl").write_text(
                trace.model_dump_json() + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "do not exactly match"):
                evaluate_sparse(
                    root,
                    baseline_dir,
                    qdrant=_Qdrant(),
                    embedder=_SparseEncoder(),
                    collection_name="test",
                    gold_dataset=type("Dataset", (), {"questions": []})(),
                    object_lookup={},
                )


if __name__ == "__main__":
    unittest.main()
