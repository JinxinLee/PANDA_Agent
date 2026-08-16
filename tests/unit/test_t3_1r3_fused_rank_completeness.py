from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

from panda_agent.evaluation import stage_trace_for_object


def _synthetic_question(question_id: str) -> dict:
    return {
        "id": question_id,
        "split": "dev",
        "language": "en",
        "intent": "api",
        "query": f"Query for {question_id}?",
        "expected_status": "answered",
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


def _write_synthetic_dataset(root: Path, ids: list[str]) -> Path:
    gold_dir = root / "evaluation" / "benchmarks" / "synthetic"
    gold_dir.mkdir(parents=True)
    path = gold_dir / "gold_questions.yaml"
    data = {
        "schema_version": "2.0",
        "benchmark_version": "m6-benchmark-v2.6",
        "release_eligible": True,
        "acceptance_exposed": False,
        "expected_split_counts": {"dev": len(ids)},
        "questions": [_synthetic_question(cid) for cid in ids],
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def _write_run(
    root: Path,
    run_id: str,
    gold_path: Path,
    record_ids: list[str],
    *,
    case_ids: list[str] | None = None,
) -> Path:
    run_dir = root / "data" / "evaluation" / "runs" / run_id
    run_dir.mkdir(parents=True)
    manifest = {
        "mode": "retrieval",
        "split": "dev",
        "official": True,
        "limit": None,
        "case_ids": case_ids,
        "gold_dataset_path": str(gold_path),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    lines = []
    for cid in record_ids:
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
    return run_dir


class T31R3FusedRankProvenanceTests(unittest.TestCase):
    def _trace(self) -> dict:
        return {
            "rankings": {"dense": ["obj.a", "obj.target"]},
            "fusion_scores": {"obj.b": 0.9, "obj.a": 1.0, "obj.target": 0.8},
            "reranked_object_ids": ["obj.a", "obj.target"],
            "ranked_object_ids": ["obj.a", "obj.target"],
        }

    def test_dict_key_order_not_used_as_fused_rank(self) -> None:
        trace = self._trace()
        stage = stage_trace_for_object(trace, {"evidence": []}, "obj.target")
        self.assertIsNone(stage["fused_rank_1based"])
        self.assertEqual(stage["fused_rank_source"], "unavailable")

    def test_frozen_fused_candidates_produce_authoritative_rank(self) -> None:
        trace = self._trace()
        fused_candidates = [
            {"object_id": "obj.a", "rank": 1},
            {"object_id": "obj.target", "rank": 2},
        ]
        stage = stage_trace_for_object(
            trace, {"evidence": []}, "obj.target", fused_candidates=fused_candidates
        )
        self.assertEqual(stage["fused_rank_1based"], 2)
        self.assertEqual(stage["fused_rank_source"], "retrieval_trace_fused_candidates")

    def test_frozen_trace_order_wins_over_dict_key_order(self) -> None:
        trace = {
            "rankings": {"dense": ["obj.target", "obj.a"]},
            "fusion_scores": {"obj.a": 1.0, "obj.target": 0.5},
            "reranked_object_ids": ["obj.a", "obj.target"],
            "ranked_object_ids": ["obj.a", "obj.target"],
        }
        fused_candidates = [
            {"object_id": "obj.target", "rank": 1},
            {"object_id": "obj.a", "rank": 2},
        ]
        stage = stage_trace_for_object(
            trace, {"evidence": []}, "obj.target", fused_candidates=fused_candidates
        )
        self.assertEqual(stage["fused_rank_1based"], 1)

    def test_missing_frozen_fusion_order_keeps_other_ranks(self) -> None:
        trace = self._trace()
        stage = stage_trace_for_object(trace, {"evidence": []}, "obj.target")
        self.assertIsNone(stage["fused_rank_1based"])
        self.assertTrue(stage["combined_candidate_present"])
        self.assertEqual(stage["reranker_rank_1based"], 2)
        self.assertEqual(stage["final_ranked_rank_1based"], 2)


class T31R3DynamicDevCompletenessTests(unittest.TestCase):
    def _report(self, root: Path, run_id: str):
        from panda_agent.evaluation_runner import report_evaluation

        return report_evaluation(root, run_id)

    def test_synthetic_five_case_complete_no_case_ids(self) -> None:
        from panda_agent.evaluation_runner import report_evaluation

        ids = ["g001", "g002", "g003", "g004", "g005"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gold = _write_synthetic_dataset(root, ids)
            _write_run(root, "run", gold, ids)
            report = report_evaluation(root, "run")
            self.assertTrue(report["development_gate"]["checks"]["complete_full_dev"])

    def test_synthetic_five_case_explicit_complete_ids(self) -> None:
        ids = ["g001", "g002", "g003", "g004", "g005"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gold = _write_synthetic_dataset(root, ids)
            _write_run(root, "run", gold, ids, case_ids=ids)
            report = self._report(root, "run")
            self.assertTrue(report["development_gate"]["checks"]["complete_full_dev"])

    def test_synthetic_four_of_five_is_incomplete(self) -> None:
        ids = ["g001", "g002", "g003", "g004", "g005"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gold = _write_synthetic_dataset(root, ids)
            _write_run(root, "run", gold, ids[:4])
            report = self._report(root, "run")
            self.assertFalse(report["development_gate"]["checks"]["complete_full_dev"])

    def test_synthetic_foreign_extra_id_is_incomplete(self) -> None:
        ids = ["g001", "g002", "g003", "g004", "g005"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gold = _write_synthetic_dataset(root, ids)
            _write_run(root, "run", gold, ids + ["g999"])
            report = self._report(root, "run")
            self.assertFalse(report["development_gate"]["checks"]["complete_full_dev"])

    def test_no_hardcoded_80_or_59_dependency(self) -> None:
        # The synthetic dataset has 5 dev questions; if a hidden ==80 check
        # remained, this would fail.
        ids = ["g001", "g002", "g003", "g004", "g005"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gold = _write_synthetic_dataset(root, ids)
            _write_run(root, "run", gold, ids)
            report = self._report(root, "run")
            self.assertTrue(report["development_gate"]["checks"]["complete_full_dev"])


if __name__ == "__main__":
    unittest.main()
