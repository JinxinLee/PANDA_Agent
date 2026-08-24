"""Focused synthetic tests for the C8-A1 global candidate-pool contract.

All tests are deterministic and use synthetic snapshots only: no retrieval,
no model calls, no storage, no QA runtime.  They pin the contract semantics
of ``c8.global_candidate_pool.v1`` (src/panda_agent/global_candidate_pool.py).
"""

from __future__ import annotations

import json
import unittest

from panda_agent.global_candidate_pool import (
    ChannelCandidate,
    CandidateOrigin,
    CompletenessState,
    GlobalCandidatePool,
    PassOrigin,
    PassSnapshot,
    PayloadProvenance,
    TargetedTriggerContext,
    build_global_candidate_pool,
    serialize_pool,
)


def payload(object_id, *, version=None, text=None):
    return PayloadProvenance(
        object_id=object_id,
        source_id="pandaroot",
        source_version_id=version or "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
        object_type="class",
        locator={"path": f"pid/{object_id}.h", "start_line": 1, "end_line": 4},
        title=object_id,
        text=text if text is not None else f"text of {object_id}",
    )


def snapshot(
    pass_origin,
    *,
    exact_ids=(),
    dense_ids=(),
    selected=(),
    evidence_ids=None,
    exclusions=(),
    version=None,
    completeness=CompletenessState.COMPLETE,
    completeness_notes=(),
    stage_r_override=None,
    stage_s_override=None,
):
    """Build one internally consistent COMPLETE (by default) pass snapshot."""
    evidence_ids = evidence_ids or {}
    channels = [
        ChannelCandidate("exact", object_id, rank)
        for rank, object_id in enumerate(exact_ids, 1)
    ] + [
        ChannelCandidate("dense", object_id, rank, channel_score=0.5)
        for rank, object_id in enumerate(dense_ids, 1)
    ]
    universe = sorted({item.object_id for item in channels})
    # Deterministic complete Stage F: exact members first, then dense-only.
    stage_f = []
    for object_id in [*exact_ids, *dense_ids]:
        if object_id not in stage_f:
            stage_f.append(object_id)
    stage_r = list(stage_r_override if stage_r_override is not None else stage_f[:2])
    stage_m = []
    for object_id in [*stage_r, *stage_f]:
        if object_id not in stage_m:
            stage_m.append(object_id)
    stage_p = list(reversed(stage_m))
    selected_ids = list(stage_s_override if stage_s_override is not None else selected)
    return PassSnapshot(
        pass_origin=pass_origin,
        completeness=completeness,
        completeness_notes=completeness_notes,
        query_text=f"query for {pass_origin.value}",
        retrieval_plan={"intent": "api", "symbols": []},
        channel_candidates=tuple(channels),
        stage_f_order=tuple(stage_f),
        stage_f_scores={object_id: 1.0 / (rank + 1) for rank, object_id in enumerate(stage_f)},
        stage_r_order=tuple(stage_r),
        stage_m_order=tuple(stage_m),
        stage_p_order=tuple(stage_p),
        stage_s_selected_object_ids=tuple(selected_ids),
        stage_s_evidence_ids={key: value for key, value in evidence_ids.items()},
        exclusions=tuple(exclusions),
        backfill_admissions=(),
        payloads={object_id: payload(object_id, version=version) for object_id in universe},
    )


def trigger():
    return TargetedTriggerContext(
        original_question="Where is Foo?",
        initial_sufficient=False,
        initial_sufficiency_errors=("missing required source: code",),
        targeted_query_text="Where is Foo?\nTarget missing evidence sources: code.",
        targeted_retrieval_plan={"intent": "api", "symbols": []},
        targeted_plan_delta={"symbols_prepended": []},
    )


def initial_pass(**kwargs):
    return snapshot(PassOrigin.INITIAL, **kwargs)


def targeted_pass(**kwargs):
    return snapshot(PassOrigin.TARGETED, **kwargs)


class GlobalCandidatePoolContractTests(unittest.TestCase):
    def test_initial_only_object_becomes_initial_only_candidate(self):
        pool = build_global_candidate_pool(
            initial_pass(exact_ids=["objA"], selected=["objA"])
        )
        self.assertEqual(len(pool.candidates), 1)
        self.assertEqual(pool.candidates[0].origin, CandidateOrigin.INITIAL_ONLY)
        self.assertEqual(
            dict(pool.counts),
            {"total": 1, "initial_only": 1, "targeted_only": 0, "both": 0},
        )

    def test_targeted_only_object_becomes_targeted_only_candidate(self):
        pool = build_global_candidate_pool(
            initial_pass(exact_ids=["objA"]),
            targeted_pass(dense_ids=["objB"]),
            targeted_trigger=trigger(),
        )
        by_id = {c.object_id: c for c in pool.candidates}
        self.assertEqual(by_id["objB"].origin, CandidateOrigin.TARGETED_ONLY)
        self.assertEqual(pool.counts["targeted_only"], 1)

    def test_same_object_in_both_passes_becomes_one_both_candidate(self):
        pool = build_global_candidate_pool(
            initial_pass(exact_ids=["objA", "objB"]),
            targeted_pass(exact_ids=["objA"], dense_ids=["objC"]),
            targeted_trigger=trigger(),
        )
        by_id = {c.object_id: c for c in pool.candidates}
        self.assertEqual(len(pool.candidates), 3)
        self.assertEqual(by_id["objA"].origin, CandidateOrigin.BOTH)
        self.assertIsNotNone(by_id["objA"].initial_occurrence)
        self.assertIsNotNone(by_id["objA"].targeted_occurrence)
        self.assertEqual(pool.counts["both"], 1)

    def test_different_evidence_ids_for_same_object_still_merge(self):
        pool = build_global_candidate_pool(
            initial_pass(
                exact_ids=["objA"], selected=["objA"],
                evidence_ids={"objA": "evidence.aaa"},
            ),
            targeted_pass(
                exact_ids=["objA"], selected=["objA"],
                evidence_ids={"objA": "evidence.bbb"},
            ),
            targeted_trigger=trigger(),
        )
        candidate = pool.candidates[0]
        self.assertEqual(candidate.object_id, "objA")
        self.assertEqual(candidate.origin, CandidateOrigin.BOTH)
        # Both occurrence-level evidence_id values survive as provenance.
        self.assertEqual(candidate.initial_occurrence.evidence_id, "evidence.aaa")
        self.assertEqual(candidate.targeted_occurrence.evidence_id, "evidence.bbb")

    def test_pass_channel_and_rank_provenance_remain_independent(self):
        # objA is exact-rank 2 in the initial pass but exact-rank 1 in the
        # targeted pass; both channel ranks and both Stage-F ranks survive
        # independently, never collapsed or averaged.
        pool = build_global_candidate_pool(
            initial_pass(exact_ids=["objB", "objA"]),
            targeted_pass(exact_ids=["objA"], dense_ids=["objA", "objC"]),
            targeted_trigger=trigger(),
        )
        candidate = {c.object_id: c for c in pool.candidates}["objA"]
        initial_exact = next(
            c for c in candidate.initial_occurrence.channel_occurrences
            if c.channel == "exact"
        )
        targeted_exact = next(
            c for c in candidate.targeted_occurrence.channel_occurrences
            if c.channel == "exact"
        )
        self.assertEqual(initial_exact.rank, 2)
        self.assertEqual(targeted_exact.rank, 1)
        self.assertEqual(candidate.initial_occurrence.stage_f_rank, 2)
        self.assertEqual(candidate.targeted_occurrence.stage_f_rank, 1)
        # Channel membership itself is per-pass provenance.
        self.assertEqual(
            sorted(c.channel for c in candidate.initial_occurrence.channel_occurrences),
            ["exact"],
        )
        self.assertEqual(
            sorted(c.channel for c in candidate.targeted_occurrence.channel_occurrences),
            ["dense", "exact"],
        )

    def test_stage_s_provenance_remains_pass_specific(self):
        pool = build_global_candidate_pool(
            initial_pass(
                exact_ids=["objA"], selected=["objA"],
                evidence_ids={"objA": "evidence.aaa"},
            ),
            targeted_pass(
                exact_ids=["objA"], selected=[],
                exclusions=({"object_id": "objA", "reason": "source_budget_cap"},),
            ),
            targeted_trigger=trigger(),
        )
        candidate = pool.candidates[0]
        self.assertTrue(candidate.initial_occurrence.stage_s_selected)
        self.assertFalse(candidate.targeted_occurrence.stage_s_selected)
        self.assertEqual(candidate.targeted_occurrence.exclusion_receipts[0]["reason"], "source_budget_cap")

    def test_conflicting_source_version_fails_clearly(self):
        with self.assertRaises(ValueError) as ctx:
            build_global_candidate_pool(
                initial_pass(exact_ids=["objA"]),
                targeted_pass(exact_ids=["objA"], version="pandaroot@deadbeef"),
                targeted_trigger=trigger(),
            )
        self.assertIn("conflicting source/version", str(ctx.exception))

    def test_serialization_deterministic_and_claims_no_global_rank(self):
        args = (
            initial_pass(exact_ids=["objA", "objB"]),
            targeted_pass(dense_ids=["objB", "objC"]),
            trigger(),
        )
        first = serialize_pool(build_global_candidate_pool(*args))
        second = serialize_pool(build_global_candidate_pool(*args))
        self.assertEqual(first, second)
        data = json.loads(first)
        # Deterministic object_id serialization order, explicitly labeled.
        self.assertEqual(
            [c["object_id"] for c in data["candidates"]],
            ["objA", "objB", "objC"],
        )
        self.assertEqual(
            data["serialization_order_semantics"],
            "serialization_order_only_not_relevance_ranking",
        )
        self.assertFalse(data["global_ranking_defined"])
        # No field anywhere in the serialized structure claims a global
        # score/rank; the explicit false flags are the only "global_*" keys.
        forbidden_keys = {"global_score", "global_rank", "relevance_score", "combined_score"}

        def keys(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    yield key
                    yield from keys(value)
            elif isinstance(node, list):
                for item in node:
                    yield from keys(item)

        self.assertFalse(forbidden_keys & set(keys(data)))

    def test_stage_r_outside_stage_f_fails(self):
        broken = initial_pass(exact_ids=["objA"])
        object.__setattr__(broken, "stage_r_order", ("objGHOST",))
        with self.assertRaises(ValueError) as ctx:
            build_global_candidate_pool(broken)
        self.assertIn("Stage-F", str(ctx.exception))

    def test_stage_s_selection_outside_universe_fails(self):
        broken = initial_pass(exact_ids=["objA"])
        object.__setattr__(broken, "stage_s_selected_object_ids", ("objGHOST",))
        with self.assertRaises(ValueError) as ctx:
            build_global_candidate_pool(broken)
        self.assertIn("candidate universe", str(ctx.exception))

    def test_missing_payload_fails(self):
        broken = initial_pass(exact_ids=["objA"])
        object.__setattr__(broken, "payloads", {})
        with self.assertRaises(ValueError) as ctx:
            build_global_candidate_pool(broken)
        self.assertIn("lacks payload provenance", str(ctx.exception))

    def test_complete_with_truncated_stage_f_fails(self):
        broken = initial_pass(exact_ids=["objA", "objB"])
        object.__setattr__(broken, "stage_f_order", ("objA",))
        object.__setattr__(broken, "stage_f_scores", {"objA": 1.0})
        object.__setattr__(broken, "stage_r_order", ("objA",))
        object.__setattr__(broken, "stage_m_order", ("objA",))
        object.__setattr__(broken, "stage_p_order", ("objA",))
        with self.assertRaises(ValueError) as ctx:
            build_global_candidate_pool(broken)
        self.assertIn("PARTIAL", str(ctx.exception))

    def test_partial_with_notes_allowed(self):
        pool = build_global_candidate_pool(
            initial_pass(
                exact_ids=["objA", "objB"],
                completeness=CompletenessState.PARTIAL,
                completeness_notes=("stage_f_order truncated to top 30",),
            )
        )
        self.assertIsInstance(pool, GlobalCandidatePool)
        self.assertEqual(pool.initial_snapshot.completeness, CompletenessState.PARTIAL)

    def test_targeted_snapshot_requires_trigger_context(self):
        with self.assertRaises(ValueError) as ctx:
            build_global_candidate_pool(
                initial_pass(exact_ids=["objA"]),
                targeted_pass(exact_ids=["objB"]),
            )
        self.assertIn("TargetedTriggerContext", str(ctx.exception))

    def test_representation_only_channel_rejected(self):
        broken = initial_pass(exact_ids=["objA"])
        object.__setattr__(
            broken,
            "channel_candidates",
            (ChannelCandidate("semantic_dense", "objA", 1),),
        )
        with self.assertRaises(ValueError) as ctx:
            build_global_candidate_pool(broken)
        self.assertIn("not an executed production channel", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
