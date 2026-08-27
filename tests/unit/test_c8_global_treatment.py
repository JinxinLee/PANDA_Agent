"""Focused synthetic tests for the C8-A2 G1 treatment preparation."""

from __future__ import annotations

import unittest

from evaluation.c8_global_treatment import (
    CHANNEL_WEIGHTS,
    RRF_K,
    TREATMENT_ID,
    best_rank_fusion,
    prepare_global_m_p_selection,
    prepare_global_reranker_input,
)
from panda_agent.global_candidate_pool import (
    ChannelCandidate,
    CompletenessState,
    PassOrigin,
    PassSnapshot,
    PayloadProvenance,
    TargetedTriggerContext,
    build_global_candidate_pool,
)


def payload(object_id: str) -> PayloadProvenance:
    return PayloadProvenance(
        object_id=object_id,
        source_id="pandaroot",
        source_version_id="pandaroot@fixture",
        object_type="source_file",
        locator={"path": f"src/{object_id}.cxx"},
        title=object_id,
        text=f"synthetic payload {object_id}",
    )


def snapshot(origin: PassOrigin, streams: dict[str, list[str]]) -> PassSnapshot:
    channel_candidates = tuple(
        ChannelCandidate(channel, object_id, rank)
        for channel in ("exact", "dense", "sparse", "paper", "workflow", "graph")
        for rank, object_id in enumerate(streams.get(channel, []), 1)
    )
    universe = list(dict.fromkeys(item.object_id for item in channel_candidates))
    stage_r = universe[:2]
    stage_m = list(dict.fromkeys([*stage_r, *universe]))
    selected = universe[: min(2, len(universe))]
    return PassSnapshot(
        pass_origin=origin,
        completeness=CompletenessState.COMPLETE,
        query_text="synthetic question",
        retrieval_plan={
            "intent": "api",
            "source_budgets": {"code": 1.0},
            "required_source_types": [],
            "target_repositories": [],
            "symbols": [],
            "paper_page_hints": {},
        },
        channel_candidates=channel_candidates,
        stage_f_order=tuple(universe),
        stage_f_scores={object_id: float(index + 1) for index, object_id in enumerate(universe)},
        stage_r_order=tuple(stage_r),
        stage_m_order=tuple(stage_m),
        stage_p_order=tuple(stage_m),
        stage_s_selected_object_ids=tuple(selected),
        stage_s_evidence_ids={object_id: f"evidence.{object_id}" for object_id in selected},
        payloads={object_id: payload(object_id) for object_id in universe},
    )


def pool(initial_streams: dict[str, list[str]], targeted_streams: dict[str, list[str]] | None = None):
    initial = snapshot(PassOrigin.INITIAL, initial_streams)
    if targeted_streams is None:
        return build_global_candidate_pool(initial)
    targeted = snapshot(PassOrigin.TARGETED, targeted_streams)
    trigger = TargetedTriggerContext(
        original_question="synthetic question",
        initial_sufficient=False,
        initial_sufficiency_errors=("missing required source: code",),
        targeted_query_text="synthetic targeted question",
        targeted_retrieval_plan=targeted.retrieval_plan,
        targeted_plan_delta={"symbols_prepended": []},
    )
    return build_global_candidate_pool(initial, targeted, trigger)


class C8GlobalTreatmentTests(unittest.TestCase):
    def test_best_rank_same_channel_is_counted_once(self):
        candidate_pool = pool(
            {"dense": ["object-a", "object-b"]},
            {"dense": ["object-b"], "sparse": ["object-c"]},
        )
        fusion = best_rank_fusion(candidate_pool)
        self.assertEqual(fusion.channel_ranks["object-b"]["dense"], 1)
        self.assertEqual(len(fusion.contributions["object-b"]), 1)
        self.assertAlmostEqual(fusion.score_map["object-b"], 1.0 / (RRF_K + 1))

    def test_different_channels_accumulate_without_both_bonus(self):
        candidate_pool = pool(
            {"exact": ["object-a"]},
            {"dense": ["object-a"], "sparse": ["object-b"]},
        )
        fusion = best_rank_fusion(candidate_pool)
        self.assertEqual(len(fusion.contributions["object-a"]), 2)
        expected = CHANNEL_WEIGHTS["exact"] / 61 + CHANNEL_WEIGHTS["dense"] / 61
        self.assertAlmostEqual(fusion.score_map["object-a"], expected)

    def test_ties_use_object_id_and_top30_is_unique(self):
        candidate_pool = pool(
            {"exact": ["object-b"]},
            {"exact": ["object-a"]},
        )
        fusion = best_rank_fusion(candidate_pool)
        self.assertEqual(list(fusion.candidate_ids), ["object-a", "object-b"])

        many = pool({"dense": [f"object-{index:02d}" for index in range(35)]})
        many_fusion = best_rank_fusion(many)
        payloads = {candidate.object_id: candidate.payload.as_dict() for candidate in many.candidates}
        reranker_input = prepare_global_reranker_input("original question", many_fusion, payloads)
        self.assertEqual(len(reranker_input["candidate_ids"]), 30)
        self.assertEqual(len(set(reranker_input["candidate_ids"])), 30)

    def test_original_question_targeted_plan_and_fixed_output_are_deterministic(self):
        candidate_pool = pool(
            {"exact": ["object-a", "object-b"]},
            {"dense": ["object-c", "object-a"]},
        )
        fusion = best_rank_fusion(candidate_pool)
        payloads = {candidate.object_id: candidate.payload.as_dict() for candidate in candidate_pool.candidates}
        first = prepare_global_m_p_selection(
            "original question",
            candidate_pool.targeted_snapshot.retrieval_plan,
            fusion,
            payloads,
            list(fusion.candidate_ids[:2]),
            final_evidence_limit=2,
        )
        second = prepare_global_m_p_selection(
            "original question",
            candidate_pool.targeted_snapshot.retrieval_plan,
            fusion,
            payloads,
            list(fusion.candidate_ids[:2]),
            final_evidence_limit=2,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["question_identity"], "original_question")
        self.assertEqual(first["final_plan_identity"], "actual_targeted_retrieval_plan")
        self.assertEqual(first["selector_identity"], "CURRENT_SELECTOR")
        self.assertFalse(first["executed"])
        self.assertEqual(first["treatment_id"], TREATMENT_ID)


if __name__ == "__main__":
    unittest.main()
