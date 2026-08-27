"""Focused synthetic tests for the C8-A2 capture helpers."""

from __future__ import annotations

import unittest

from evaluation.scripts.capture_c8_a2_two_pass import (
    CaptureFidelityError,
    build_pass_snapshot,
    load_execution_projection,
    replay_s0,
    synthetic_preflight,
    validate_both_origin_payload_consistency,
    validate_s0_replay,
)
from panda_agent.global_candidate_pool import PassOrigin
from panda_agent.retrieval import select_final_evidence
from panda_agent.models import RetrievalPlan


def payload(object_id: str, *, source_id: str = "pandaroot") -> dict:
    return {
        "object_id": object_id,
        "source_id": source_id,
        "source_version_id": f"{source_id}@fixture",
        "object_type": "source_file",
        "title": object_id,
        "text": f"synthetic payload {object_id}",
        "authority_level": "primary",
        "locator": {"path": f"src/{object_id}.cxx"},
    }


def passing_capture() -> dict:
    channels = {"exact": [payload("a"), payload("b")], "dense": [payload("b"), payload("c")]}
    rankings = {channel: [item["object_id"] for item in rows] for channel, rows in channels.items()}
    scores = {"b": 2 / 62 + 1 / 61, "a": 2 / 61, "c": 1 / 62}
    stage_f = ["b", "a", "c"]
    stage_r = ["b", "a"]
    stage_m = ["b", "a", "c"]
    plan = {
        "intent": "api",
        "source_budgets": {"code": 1.0},
        "required_source_types": [],
        "target_repositories": [],
        "symbols": [],
        "paper_page_hints": {},
    }
    selector_input = {
        "ordered": stage_m,
        "payloads": {object_id: payload(object_id) for object_id in ("a", "b", "c")},
        "scores": scores,
        "channels": {"a": ["exact"], "b": ["exact", "dense"], "c": ["dense"]},
        "plan": plan,
        "final_evidence_limit": 12,
        "mandatory_symbol_ids": [],
    }
    selected, excluded, backfill = select_final_evidence(
        stage_m,
        selector_input["payloads"],
        scores,
        selector_input["channels"],
        RetrievalPlan.model_validate(plan),
        12,
        set(),
    )
    result = {
        "plan": plan,
        "rankings": rankings,
        "fusion_scores": scores,
        "reranked_object_ids": stage_r,
        "ranked_object_ids": stage_m,
        "excluded": excluded,
        "backfill_admissions": backfill,
        "evidence": [item.model_dump(mode="json") for item in selected],
    }
    return {
        "query_text": "synthetic question",
        "result": result,
        "channel_rows": channels,
        "channel_scores": {"exact": [None, None], "dense": [0.9, 0.8]},
        "selector_capture": {
            "input": selector_input,
            "output": {
                "evidence": result["evidence"],
                "excluded": excluded,
                "backfill_admissions": backfill,
            },
        },
    }


class C8A2CaptureTests(unittest.TestCase):
    def test_safe_projection_structural_loading(self):
        rows = load_execution_projection()
        self.assertEqual(len(rows), 24)
        self.assertEqual(rows[0]["case_id"], "g001")
        self.assertEqual(rows[-1]["case_id"], "g047")
        self.assertEqual(set(rows[0]), {"case_id", "query", "intent"})

    def test_complete_capture_reconstructs_f_m_p_s(self):
        snapshot, aux = build_pass_snapshot(passing_capture(), PassOrigin.INITIAL)
        self.assertEqual(snapshot.completeness.value, "COMPLETE")
        self.assertEqual(list(snapshot.stage_f_order), ["b", "a", "c"])
        self.assertEqual(list(snapshot.stage_m_order), ["b", "a", "c"])
        self.assertEqual(list(snapshot.stage_p_order), ["b", "a", "c"])
        self.assertTrue(all(aux["parity"].values()))

    def test_stage_f_exposed_prefix_mismatch_is_rejected(self):
        broken = passing_capture()
        broken["result"]["fusion_scores"] = {"b": 9.0, "a": 8.0, "c": 7.0}
        with self.assertRaises(CaptureFidelityError):
            build_pass_snapshot(broken, PassOrigin.INITIAL)

    def test_stage_p_exposed_prefix_mismatch_is_rejected(self):
        broken = passing_capture()
        broken["result"]["ranked_object_ids"] = ["a", "b", "c"]
        with self.assertRaises(CaptureFidelityError):
            build_pass_snapshot(broken, PassOrigin.INITIAL)

    def test_stage_s_mismatch_is_rejected(self):
        broken = passing_capture()
        broken["result"]["evidence"] = list(reversed(broken["result"]["evidence"]))
        with self.assertRaises(CaptureFidelityError):
            build_pass_snapshot(broken, PassOrigin.INITIAL)

    def test_s0_preserves_first_position_and_last_payload(self):
        initial = [{"evidence_id": "e1", "object_id": "initial", "text": "initial"}]
        targeted = [{"evidence_id": "e1", "object_id": "targeted", "text": "targeted"}, {"evidence_id": "e2", "object_id": "second"}]
        replay = replay_s0(targeted, initial)
        self.assertEqual([item["evidence_id"] for item in replay], ["e1", "e2"])
        self.assertEqual(replay[0]["object_id"], "initial")
        self.assertEqual(replay[0]["text"], "initial")

    def test_s0_parity_and_payload_consistency(self):
        initial = [{**payload("a"), "evidence_id": "evidence.a"}]
        targeted = [{**payload("b"), "evidence_id": "evidence.b"}]
        result = validate_s0_replay(targeted, initial, [{**payload("b"), "evidence_id": "evidence.b"}, {**payload("a"), "evidence_id": "evidence.a"}])
        self.assertTrue(result["parity"])
        self.assertEqual(result["identity"], "C8_CURRENT_APPEND_V1")
        self.assertEqual(validate_both_origin_payload_consistency({"a": payload("a")}, {"a": payload("a")})["consistent"], True)
        conflict = payload("a", source_id="restgas_determination")
        self.assertFalse(validate_both_origin_payload_consistency({"a": payload("a")}, {"a": conflict})["consistent"])

    def test_synthetic_preflight_has_no_live_or_g1_execution(self):
        result = synthetic_preflight()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["retrieval_calls"], 0)
        self.assertEqual(result["model_calls"], 0)
        self.assertEqual(result["real_g1_executions"], 0)


if __name__ == "__main__":
    unittest.main()
