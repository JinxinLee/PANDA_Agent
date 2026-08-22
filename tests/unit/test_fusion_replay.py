from __future__ import annotations

import json
import unittest
from pathlib import Path

from panda_agent.fusion_replay import (
    CORE_REQUIRED_CHANNELS,
    CURRENT_POLICY_ID,
    CURRENT_WEIGHTS,
    INVALID_OR_UNFAITHFUL,
    MISSING_NOT_CAPTURED,
    PRESENT_EMPTY,
    PRESENT_NONEMPTY,
    RRF_K,
    SKIPPED_BY_PLAN,
    FusionPolicy,
    FusionReplayCase,
    FrozenChannelCandidate,
    FrozenChannelStream,
    current_policy,
    load_replay_cases,
    preregistered_policies,
    replay_case_from_mapping,
    structural_parity,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _candidate(object_id: str, rank: int) -> FrozenChannelCandidate:
    return FrozenChannelCandidate(
        object_id=object_id, rank=rank, source_id="pandaroot", source_version_id="pandaroot@locked"
    )


def _stream(channel: str, object_ids: list[str], state: str = PRESENT_NONEMPTY) -> FrozenChannelStream:
    return FrozenChannelStream(
        channel=channel,
        availability_state=state,
        candidates=tuple(_candidate(oid, rank) for rank, oid in enumerate(object_ids, 1)),
    )


def _case(
    case_id: str = "t001",
    *,
    dense: list[str] | None = ("obj.a", "obj.b"),
    exact: list[str] | None = ("obj.b",),
    sparse: list[str] | None = ("obj.c",),
    paper: list[str] | None = None,
    workflow: list[str] | None = ("obj.d",),
    graph: list[str] | None = None,
    semantic: list[str] | None = None,
    overrides: dict[str, FrozenChannelStream] | None = None,
) -> FusionReplayCase:
    channels = {
        "exact": _stream("exact", list(exact) if exact else [], PRESENT_NONEMPTY if exact else PRESENT_EMPTY),
        "raw_dense": _stream("raw_dense", list(dense) if dense else [], PRESENT_NONEMPTY if dense else PRESENT_EMPTY),
        "sparse": _stream("sparse", list(sparse) if sparse else [], PRESENT_NONEMPTY if sparse else PRESENT_EMPTY),
        "paper": _stream("paper", list(paper) if paper else [], PRESENT_NONEMPTY if paper else PRESENT_EMPTY),
        "workflow": _stream("workflow", list(workflow) if workflow else [], PRESENT_NONEMPTY if workflow else PRESENT_EMPTY),
        "graph": _stream("graph", list(graph) if graph else [], PRESENT_NONEMPTY if graph else PRESENT_EMPTY),
    }
    if semantic is not None:
        channels["semantic_dense"] = _stream("semantic_dense", list(semantic))
    if overrides:
        channels.update(overrides)
    return FusionReplayCase(
        case_id=case_id, question="q?", intent="api", channels=channels
    )


class ReplayMathTests(unittest.TestCase):
    def test_single_channel_fusion(self):
        receipt = current_policy().apply(_case(dense=["obj.a", "obj.b"], exact=[], sparse=[], workflow=[], graph=[]))
        self.assertEqual(
            [c.object_id for c in receipt.fused], ["obj.a", "obj.b"]
        )
        self.assertAlmostEqual(receipt.fused[0].fused_score, 1.0 / (RRF_K + 1))

    def test_multi_channel_fusion_and_cross_channel_contributions(self):
        case = _case(dense=["obj.a", "obj.b"], exact=["obj.b"], sparse=["obj.a"])
        receipt = current_policy().apply(case)
        by_id = {c.object_id: c for c in receipt.fused}
        obj_a = by_id["obj.a"]
        expected = 1.0 / (RRF_K + 1) + 1.0 / (RRF_K + 1)  # dense rank1 + sparse rank1
        self.assertAlmostEqual(obj_a.fused_score, expected)
        self.assertEqual(
            sorted(item.channel for item in obj_a.contributions), ["raw_dense", "sparse"]
        )

    def test_stable_object_id_deduplication(self):
        case = _case(dense=["obj.a", "obj.b", "obj.c"], exact=["obj.c", "obj.a"], sparse=[], workflow=[], graph=[])
        receipt = current_policy().apply(case)
        ids = [c.object_id for c in receipt.fused]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {"obj.a", "obj.b", "obj.c"})

    def test_rank_convention_matches_production(self):
        # Production: weight / (60 + 0-based rank + 1) == weight / (RRF_K + 1-based rank).
        case = _case(dense=["obj.a", "obj.b"], exact=[], sparse=[], workflow=[], graph=[])
        receipt = current_policy().apply(case)
        self.assertAlmostEqual(receipt.fused[0].fused_score, CURRENT_WEIGHTS["raw_dense"] / (RRF_K + 1))
        self.assertAlmostEqual(receipt.fused[1].fused_score, CURRENT_WEIGHTS["raw_dense"] / (RRF_K + 2))

    def test_current_weights_match_production_identity(self):
        self.assertEqual(
            CURRENT_WEIGHTS,
            {"exact": 2.0, "raw_dense": 1.0, "sparse": 1.0, "paper": 1.15, "workflow": 1.2, "graph": 0.8},
        )
        self.assertEqual(RRF_K, 60)

    def test_deterministic_tie_behavior(self):
        # obj.a: exact rank1 only (2.0/61); obj.b: dense rank1 only (1.0/61).
        # Different scores.  For a genuine tie, give obj.c paper rank1 (1.15/61)
        # and obj.d workflow rank1 (1.2/62)?  Simpler exact tie: dense rank2 (1/62)
        # vs sparse rank2 (1/62) -> insertion order (dense before sparse) decides.
        case = _case(dense=["obj.x", "obj.tie"], exact=[], sparse=["obj.y", "obj.tie"], workflow=[], graph=[])
        receipt = current_policy().apply(case)
        order = [c.object_id for c in receipt.fused]
        tie_index_a, tie_index_b = order.index("obj.tie"), order.index("obj.y")
        # obj.tie (two contributions) outranks obj.y (single contribution).
        self.assertLess(tie_index_a, tie_index_b)
        repeated = current_policy().apply(
            _case(dense=["obj.x", "obj.tie"], exact=[], sparse=["obj.y", "obj.tie"], workflow=[], graph=[], case_id="t001b")
        )
        self.assertEqual(order, [c.object_id for c in repeated.fused])

    def test_disabled_channel_contributes_zero(self):
        case = _case(dense=["obj.a"], semantic=["obj.s", "obj.a"])
        receipt = current_policy().apply(case)
        self.assertNotIn("semantic_dense", receipt.enabled_channels)
        self.assertFalse(any("semantic_dense" in item.channel for c in receipt.fused for item in c.contributions))
        self.assertNotIn("obj.s", [c.object_id for c in receipt.fused])

    def test_semantic_candidate_exists_without_changing_current(self):
        case = _case(dense=["obj.a"], semantic=["obj.s", "obj.a"])
        receipt = current_policy().apply(case)
        baseline = current_policy().apply(_case(dense=["obj.a"]))
        self.assertEqual(
            [c.fused_score for c in receipt.fused], [c.fused_score for c in baseline.fused]
        )

    def test_receipt_contribution_sum_matches_fused_score(self):
        case = _case(dense=["obj.a", "obj.b"], exact=["obj.b", "obj.c"], sparse=["obj.a"], workflow=["obj.e"])
        receipt = current_policy().apply(case)
        for candidate in receipt.fused:
            self.assertAlmostEqual(
                candidate.fused_score,
                sum(item.contribution for item in candidate.contributions),
                places=12,
            )

    def test_candidate_provenance_and_metadata_round_trip(self):
        payload = {
            "case_id": "t009",
            "question": "where?",
            "intent": "api",
            "plan_provenance": {"source_run": "unit"},
            "channels": {
                "exact": {
                    "availability_state": PRESENT_NONEMPTY,
                    "candidates": [
                        {
                            "object_id": "obj.a",
                            "rank": 1,
                            "original_score": 0.5,
                            "source_id": "pandaroot",
                            "source_version_id": "pandaroot@locked",
                            "locator": {"path": "a.cxx"},
                        }
                    ],
                }
            },
        }
        case = replay_case_from_mapping(payload)
        candidate = case.channels["exact"].candidates[0]
        self.assertEqual(candidate.source_id, "pandaroot")
        self.assertEqual(candidate.source_version_id, "pandaroot@locked")
        self.assertEqual(candidate.original_score, 0.5)
        self.assertEqual(candidate.locator, {"path": "a.cxx"})
        round_trip = replay_case_from_mapping(case.as_dict())
        self.assertEqual(round_trip.channels["exact"].candidates[0].object_id, "obj.a")

    def test_trace_channel_alias_maps_dense_to_raw_dense(self):
        case = replay_case_from_mapping(
            {
                "case_id": "t010",
                "question": "q",
                "intent": "api",
                "channels": {"dense": {"availability_state": PRESENT_NONEMPTY, "candidates": [{"object_id": "obj.a", "rank": 1}]}},
            }
        )
        self.assertIn("raw_dense", case.channels)


class EligibilityTests(unittest.TestCase):
    def test_present_empty_is_valid(self):
        case = _case(dense=["obj.a"], exact=None, sparse=["obj.c"], workflow=None, graph=None, paper=None)
        self.assertTrue(case.core_replay_eligible)
        receipt = current_policy().apply(case)
        # An explicitly executed empty channel participates but contributes nothing.
        self.assertIn("paper", receipt.enabled_channels)
        self.assertFalse(
            any(
                item.channel == "paper"
                for candidate in receipt.fused
                for item in candidate.contributions
            )
        )

    def test_skipped_by_plan_is_valid(self):
        case = _case(graph=None, overrides={"graph": FrozenChannelStream("graph", SKIPPED_BY_PLAN)})
        self.assertTrue(case.core_replay_eligible)
        receipt = current_policy().apply(case)
        self.assertNotIn("graph", receipt.enabled_channels)

    def test_missing_not_capturedblocks_eligibility(self):
        case = _case(overrides={"sparse": FrozenChannelStream("sparse", MISSING_NOT_CAPTURED)})
        self.assertFalse(case.core_replay_eligible)

    def test_invalid_or_unfaithful_blocks_eligibility(self):
        case = _case(overrides={"exact": FrozenChannelStream("exact", INVALID_OR_UNFAITHFUL)})
        self.assertFalse(case.core_replay_eligible)

    def test_missing_required_channel_blocks_eligibility(self):
        case = _case()
        del case.channels["workflow"]
        self.assertFalse(case.core_replay_eligible)
        self.assertEqual(set(CORE_REQUIRED_CHANNELS), {"exact", "raw_dense", "sparse", "paper", "workflow", "graph"})


class PolicySetTests(unittest.TestCase):
    def test_preregistered_policy_ids_are_frozen(self):
        policies = preregistered_policies()
        self.assertEqual(
            sorted(policies),
            sorted(
                [
                    "P0_CURRENT",
                    "P1_RAW_DENSE_CENTERED",
                    "P2_EXACT_HEAVY",
                    "P3_SPARSE_HEAVY",
                    "P4_SEMANTIC_AUXILIARY_25",
                    "P5_SEMANTIC_EXPANSION_ONLY",
                ]
            ),
        )
        self.assertEqual(policies["P0_CURRENT"].policy_id, CURRENT_POLICY_ID)
        self.assertEqual(policies["P1_RAW_DENSE_CENTERED"].weights["raw_dense"], 1.5)
        self.assertEqual(policies["P2_EXACT_HEAVY"].weights["exact"], 3.0)
        self.assertEqual(policies["P3_SPARSE_HEAVY"].weights["sparse"], 1.5)
        self.assertEqual(policies["P4_SEMANTIC_AUXILIARY_25"].weights["raw_dense"], 0.75)
        self.assertEqual(policies["P4_SEMANTIC_AUXILIARY_25"].weights["semantic_dense"], 0.25)
        for name in ("P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY"):
            self.assertNotIn("semantic_dense", policies[name].enabled_channels)

    def test_semantic_expansion_only_preserves_current_ranking(self):
        case = _case(dense=["obj.a", "obj.b"], semantic=["obj.s", "obj.a", "obj.t"])
        policies = preregistered_policies()
        current = policies["P0_CURRENT"].apply(case)
        expansion = policies["P5_SEMANTIC_EXPANSION_ONLY"].apply(case)
        self.assertEqual(
            [(c.object_id, c.fused_score) for c in current.fused],
            [(c.object_id, c.fused_score) for c in expansion.fused],
        )
        self.assertEqual(
            [c.object_id for c in expansion.expansion_pool], ["obj.s", "obj.t"]
        )

    def test_no_gold_fields_required_by_replay(self):
        case = _case()
        receipt = current_policy().apply(case)
        payload = receipt.as_dict()
        self.assertNotIn("gold", json.dumps(payload))
        self.assertNotIn("evidence_group", json.dumps(payload))

    def test_repeated_replay_is_deterministic(self):
        case = _case(dense=["obj.a", "obj.b"], exact=["obj.b"], sparse=["obj.c"])
        first = current_policy().apply(case).as_dict()
        second = current_policy().apply(case).as_dict()
        self.assertEqual(first, second)


class NormalizedDataTests(unittest.TestCase):
    """Focused checks against the real normalized frozen replay data."""

    @classmethod
    def setUpClass(cls):
        cls.path = (
            PROJECT_ROOT
            / "evaluation"
            / "baselines"
            / "replay"
            / "phase_c_c6_frozen_channel_replay_v1.jsonl"
        )
        cls.cases = load_replay_cases(cls.path)

    def test_normalized_data_loads_with_expected_cohorts(self):
        self.assertEqual(len(self.cases), 80)
        self.assertTrue(all(case.core_replay_eligible for case in self.cases))
        semantic = [case for case in self.cases if case.semantic_stream_available]
        self.assertEqual(sorted(case.case_id for case in semantic), ["g039", "g055", "g113", "g114", "g115"])

    def test_current_replay_parity_on_real_traces(self):
        ok = 0
        for case in self.cases:
            receipt = current_policy().apply(case)
            trace = json.loads(
                (
                    PROJECT_ROOT
                    / "data"
                    / "evaluation"
                    / "runs"
                    / "phase-b-t3-retrieval-20260816"
                    / "traces"
                    / f"{case.case_id}.json"
                ).read_text(encoding="utf-8")
            )
            result = structural_parity(
                receipt,
                [c["object_id"] for c in trace["fused_candidates"]],
                {c["object_id"]: c["score"] for c in trace["fused_candidates"]},
            )
            self.assertTrue(result["order_match"], case.case_id)
            self.assertTrue(result["score_match"], case.case_id)
            ok += 1
        self.assertGreaterEqual(ok, 3)

    def test_no_model_or_retrieval_calls_in_module_import(self):
        import inspect

        import panda_agent.fusion_replay as module

        source = inspect.getsource(module)
        for forbidden in (
            "psycopg",
            "QdrantClient",
            "VertexAIClient",
            "generate_json",
            "embed_query",
            "requests.",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
