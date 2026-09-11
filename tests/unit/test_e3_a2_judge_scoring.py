"""Deterministic tests for the E3-A2 blinded judge contract and offline scorer.

Zero provider calls: the judge schema is validated with pydantic and the
frozen G1-G7 scoring semantics are exercised on synthetic raw/judged records.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "e3_a2_run", ROOT / "evaluation" / "run_e3_a2_targeted_recovery_validation.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)

POINTS = [
    {"answer_point_id": "p1", "text": "point one"},
    {"answer_point_id": "p2", "text": "point two"},
]


def arm_payload(errors=(), mprc=0, status="answered"):
    return {
        "status": status,
        "answer": "final answer",
        "claims": [{"claim_id": "c1", "claim_text": "claim", "evidence_ids": ["e1"]}],
        "evidence": [],
        "selected_evidence_ids": ["e1"],
        "answer_point_audit": {},
        "verification_errors": list(errors),
        "runtime_unsupported_claim_ids": [
            e.removeprefix("unsupported claim ")
            for e in errors
            if e.startswith("unsupported claim ")
        ],
        "runtime_citation_failures": [
            e
            for e in errors
            if e.startswith(
                (
                    "wrong code version ",
                    "incomplete code citation ",
                    "incomplete paper citation ",
                    "incomplete web citation ",
                    "invalid evidence for ",
                )
            )
        ],
        "revision_count": 1,
        "missing_point_retrieval_count": mprc,
    }


def e3_trace(new_evidence=True, atomic="success"):
    return {
        "targeted_candidate_object_ids": ["obj9"],
        "newly_admitted_object_ids": ["obj9"] if new_evidence else [],
        "displaced_selected_evidence_ids": [],
        "retained_support_evidence_ids": ["e1"],
        "atomic_update_status": atomic,
        "selected_evidence_count": 12,
    }


def make_raw(
    qid,
    *,
    applicable=True,
    missing=("p2",),
    covered=("p1",),
    control_errors=(),
    treatment_errors=(),
    new_evidence=True,
    atomic="success",
    mask=None,
    treatment_mprc=1,
):
    record = {
        "record_type": "e3_a2_case",
        "state": "COMPLETE",
        "question_id": qid,
        "mode": "runtime_e1_v2",
        "shared_first_verify": {
            "reached_first_verify": True,
            "runtime_answer_points": POINTS,
            "missing_answer_point_ids": list(missing),
            "covered_answer_point_ids": list(covered),
            "answer_point_audit": {},
            "selected_evidence_ids": ["e1"],
            "initial_claims": [],
            "supported_claims": [],
            "verification_errors": [],
            "plan": {},
        },
        "applicable": applicable,
        "trigger_reason": "genuine_missing_point" if applicable else "no_missing_answer_points",
        "control": None,
        "treatment": None,
        "usage": [
            {"phase": "shared", "stage": "qa_answer", "logical_calls": 1,
             "returned_model_calls": 1, "adapter_requests": 1, "generation_calls": 1,
             "embedding_calls": 0, "tokens": 100},
        ],
    }
    if applicable:
        record["control"] = arm_payload(errors=control_errors, mprc=0)
        treatment = arm_payload(errors=treatment_errors, mprc=treatment_mprc)
        treatment["e3_trace"] = e3_trace(new_evidence=new_evidence, atomic=atomic)
        treatment["original_plan_preserved"] = True
        record["treatment"] = treatment
        record["arm_mask"] = mask or mod.arm_assignment(qid)
    return record


def outcome(missing_verdicts, preserved_verdicts, unsupported=(), contradiction=False, citation=False):
    return {
        "missing_point_outcomes": [
            {"point_id": pid, "verdict": verdict, "reason": "r"}
            for pid, verdict in missing_verdicts.items()
        ],
        "preserved_point_outcomes": [
            {"point_id": pid, "verdict": verdict, "reason": "r"}
            for pid, verdict in preserved_verdicts.items()
        ],
        "unsupported_claim_ids": list(unsupported),
        "contradiction_present": contradiction,
        "wrong_version_or_citation_concern": citation,
    }


def make_judged(qid, mask, control_out, treatment_out, preference="equivalent"):
    arm_a = treatment_out if mask["A"] == "treatment" else control_out
    arm_b = control_out if mask["A"] == "treatment" else treatment_out
    judgment = {
        "arm_a": arm_a,
        "arm_b": arm_b,
        "overall_preference": preference,
        "reason": "reason",
    }
    return {
        "record_type": "e3_a2_judgment",
        "state": "COMPLETE",
        "question_id": qid,
        "judgment": judgment,
        "usage": [
            {"phase": "judge", "stage": "judge", "logical_calls": 1,
             "returned_model_calls": 1, "adapter_requests": 1, "generation_calls": 1,
             "embedding_calls": 0, "tokens": 50},
        ],
    }


def make_manifest(ids):
    return {
        "cohort_ids": list(ids),
        "candidate_head": "head",
        "dataset": {"benchmark_version": "novel-v1-dev-0.3.0"},
        "selector": {},
        "protected_data_access": False,
        "novel_validation_or_holdout_accessed": False,
    }


GIT_OK = {
    "preregistration_commit": "c0ffee",
    "no_product_edit_after_preregistration": True,
    "frozen_protocol_unchanged": True,
    "runtime_default_unchanged": True,
    "provider_complete": True,
}


def pass_pair(qid):
    """Applicable case: treatment recovers the missing point, control does not."""
    mask = mod.arm_assignment(qid)
    raw = make_raw(qid, mask=mask)
    control_out = outcome({"p2": "absent"}, {"p1": "preserved_supported"})
    treatment_out = outcome({"p2": "satisfied_supported"}, {"p1": "preserved_supported"})
    return raw, make_judged(qid, mask, control_out, treatment_out)


def test_passing_scenario(tmp_path=None):
    ids = ["n001", "n002", "n003", "n004"]
    raw = {}
    judged = {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid] = r
        judged[qid] = j
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "PASS"
    gates = result["gates"]
    assert gates["G3_missing_point_recovery_benefit"]["pass"] is True
    assert result["recovery"]["treatment_recovery_rate"] == 1.0
    assert result["recovery"]["control_recovery_rate"] == 0.0
    assert result["recovery"]["net_additional_recovered_points"] == 4
    assert gates["G6_retrieval_contribution_consistency"]["pass"] is True


def test_g3_margin_failure():
    ids = ["n001", "n002", "n003", "n004"]
    raw, judged = {}, {}
    for index, qid in enumerate(ids):
        mask = mod.arm_assignment(qid)
        raw[qid] = make_raw(qid, mask=mask)
        if index < 2:
            # Both arms recover: no net treatment benefit on these cases.
            control_out = outcome({"p2": "satisfied_supported"}, {"p1": "preserved_supported"})
            treatment_out = outcome({"p2": "satisfied_supported"}, {"p1": "preserved_supported"})
        else:
            control_out = outcome({"p2": "absent"}, {"p1": "preserved_supported"})
            treatment_out = outcome({"p2": "absent"}, {"p1": "preserved_supported"})
        judged[qid] = make_judged(qid, mask, control_out, treatment_out)
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "FAIL"
    assert result["gates"]["G3_missing_point_recovery_benefit"]["pass"] is False
    assert result["recovery"]["net_additional_recovered_points"] == 0
    assert result["recovery"]["treatment_recovery_rate"] == 0.5


def _swap_arm(judgment, mask, control_out, treatment_out):
    judgment["arm_a"] = treatment_out if mask["A"] == "treatment" else control_out
    judgment["arm_b"] = control_out if mask["A"] == "treatment" else treatment_out
    return judgment


def test_g4_treatment_only_loss_fails():
    ids = ["n001", "n002", "n003", "n004"]
    raw, judged = {}, {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    qid = ids[0]
    mask = mod.arm_assignment(qid)
    judged[qid]["judgment"] = _swap_arm(
        judged[qid]["judgment"],
        mask,
        outcome({"p2": "absent"}, {"p1": "preserved_supported"}),
        outcome({"p2": "satisfied_supported"}, {"p1": "lost_or_unsupported"}),
    )
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "FAIL"
    assert result["gates"]["G4_no_requested_content_regression"]["pass"] is False
    assert result["preservation"]["treatment_only_lost_points"] == [f"{qid}:p1"]


def test_g5_treatment_only_unsupported_claim_fails():
    ids = ["n001", "n002", "n003", "n004"]
    raw, judged = {}, {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    qid = ids[1]
    mask = mod.arm_assignment(qid)
    judged[qid]["judgment"] = _swap_arm(
        judged[qid]["judgment"],
        mask,
        outcome({"p2": "absent"}, {"p1": "preserved_supported"}),
        outcome(
            {"p2": "satisfied_supported"},
            {"p1": "preserved_supported"},
            unsupported=("c_new",),
        ),
    )
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "FAIL"
    assert result["gates"]["G5_no_new_unsupported_answer_regression"]["pass"] is False
    assert result["safety"]["treatment_only_unsupported_claims"] == ["c_new"]


def test_g5_runtime_citation_failure_union_dedup():
    ids = ["n001"]
    mask = mod.arm_assignment(ids[0])
    raw = {
        ids[0]: make_raw(
            ids[0],
            mask=mask,
            control_errors=("incomplete code citation e9",),
            treatment_errors=("incomplete code citation e9",),
        )
    }
    judged = {
        ids[0]: make_judged(
            ids[0],
            mask,
            outcome({"p2": "absent"}, {"p1": "preserved_supported"}),
            outcome({"p2": "satisfied_supported"}, {"p1": "preserved_supported"}),
        )
    }
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    # Same claim-level event on both arms is not treatment-only; G5 still passes
    # (the case is INCONCLUSIVE on applicability, G5 is evaluated but only
    # treatment-only events fail it).
    assert result["gates"]["G5_no_new_unsupported_answer_regression"]["pass"] is True
    assert result["safety"]["treatment_only_citation_failures"] == []


def test_g6_fails_only_when_all_recovery_cases_lack_new_evidence():
    ids = ["n001", "n002", "n003", "n004"]
    raw, judged = {}, {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    raw[ids[0]] = make_raw(ids[0], mask=mod.arm_assignment(ids[0]), new_evidence=False)
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "PASS"
    assert result["gates"]["G6_retrieval_contribution_consistency"]["pass"] is True

    for qid in ids:
        raw[qid] = make_raw(qid, mask=mod.arm_assignment(qid), new_evidence=False)
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "FAIL"
    assert result["gates"]["G6_retrieval_contribution_consistency"]["pass"] is False


def test_g7_bounded_execution_violation_fails():
    ids = ["n001", "n002", "n003", "n004"]
    raw, judged = {}, {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    raw[ids[2]] = make_raw(
        ids[2], mask=mod.arm_assignment(ids[2]), treatment_mprc=2
    )
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "FAIL"
    assert result["gates"]["G7_bounded_execution_integrity"]["pass"] is False
    assert result["bounded_execution"]["max_missing_point_retrieval_count"] == 2


def test_g2_insufficient_applicability_is_inconclusive():
    ids = ["n001", "n002", "n003"]
    raw, judged = {}, {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "INCONCLUSIVE"
    assert result["gates"]["G2_natural_applicability"]["pass"] is False


def test_infrastructure_failure_is_inconclusive_not_fail():
    ids = ["n001", "n002", "n003", "n004"]
    raw, judged = {}, {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    raw["n005"] = {"state": "INFRASTRUCTURE_FAILURE", "question_id": "n005"}
    manifest = make_manifest([*ids, "n005"])
    result = mod.compute_result(manifest, raw, judged, dict(GIT_OK))
    assert result["verdict"] == "INCONCLUSIVE"
    assert result["applicability"]["infrastructure_failures"] == ["n005"]


def test_non_applicable_cases_enter_denominator_without_judgment():
    ids = ["n001", "n002", "n003", "n004", "n005"]
    raw, judged = {}, {}
    for qid in ids[:4]:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    raw["n005"] = make_raw("n005", applicable=False, missing=(), covered=("p1", "p2"))
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["applicability"]["e3_applicable_cases"] == 4
    assert result["applicability"]["non_applicable"][0]["question_id"] == "n005"
    assert result["recovery"]["treatment_recovery_rate"] == 1.0


def test_usage_totals_by_phase():
    records = [pass_pair("n001")[0], pass_pair("n002")[0]]
    totals = mod.usage_totals(records)
    assert totals["shared"]["stages"]["qa_answer"]["logical_calls"] == 2
    assert totals["shared"]["model_calls"] == 2
    assert totals["shared"]["tokens"] == 200
    assert totals["control"]["model_calls"] == 0
    assert totals["judge"]["model_calls"] == 0


def test_judgment_schema_strictness():
    valid = mod.Judgment.model_validate(
        {
            "arm_a": {
                "missing_point_outcomes": [
                    {"point_id": "p2", "verdict": "satisfied_supported", "reason": "r"}
                ],
                "preserved_point_outcomes": [
                    {"point_id": "p1", "verdict": "preserved_supported", "reason": "r"}
                ],
                "unsupported_claim_ids": [],
                "contradiction_present": False,
                "wrong_version_or_citation_concern": False,
            },
            "arm_b": {
                "missing_point_outcomes": [
                    {"point_id": "p2", "verdict": "absent", "reason": "r"}
                ],
                "preserved_point_outcomes": [
                    {"point_id": "p1", "verdict": "preserved_supported", "reason": "r"}
                ],
                "unsupported_claim_ids": [],
                "contradiction_present": False,
                "wrong_version_or_citation_concern": False,
            },
            "overall_preference": "A",
            "reason": "treatment answered the missing point",
        }
    )
    assert valid.overall_preference == "A"
    with pytest.raises(ValidationError):
        mod.Judgment.model_validate(
            {
                "arm_a": {
                    "missing_point_outcomes": [],
                    "preserved_point_outcomes": [],
                    "unsupported_claim_ids": [],
                    "contradiction_present": False,
                    "wrong_version_or_citation_concern": False,
                    "extra_field": True,
                },
                "arm_b": {
                    "missing_point_outcomes": [],
                    "preserved_point_outcomes": [],
                    "unsupported_claim_ids": [],
                    "contradiction_present": False,
                    "wrong_version_or_citation_concern": False,
                },
                "overall_preference": "A",
                "reason": "x",
            }
        )
    with pytest.raises(ValidationError):
        mod.Judgment.model_validate(
            {
                "arm_a": {
                    "missing_point_outcomes": [
                        {"point_id": "p2", "verdict": "made_up_verdict", "reason": "r"}
                    ],
                    "preserved_point_outcomes": [],
                    "unsupported_claim_ids": [],
                    "contradiction_present": False,
                    "wrong_version_or_citation_concern": False,
                },
                "arm_b": {
                    "missing_point_outcomes": [],
                    "preserved_point_outcomes": [],
                    "unsupported_claim_ids": [],
                    "contradiction_present": False,
                    "wrong_version_or_citation_concern": False,
                },
                "overall_preference": "A",
                "reason": "x",
            }
        )


def test_validate_judgment_rejects_wrong_point_and_claim_sets():
    judgment = mod.Judgment.model_validate(
        {
            "arm_a": {
                "missing_point_outcomes": [
                    {"point_id": "p9", "verdict": "absent", "reason": "r"}
                ],
                "preserved_point_outcomes": [],
                "unsupported_claim_ids": [],
                "contradiction_present": False,
                "wrong_version_or_citation_concern": False,
            },
            "arm_b": {
                "missing_point_outcomes": [
                    {"point_id": "p2", "verdict": "absent", "reason": "r"}
                ],
                "preserved_point_outcomes": [],
                "unsupported_claim_ids": [],
                "contradiction_present": False,
                "wrong_version_or_citation_concern": False,
            },
            "overall_preference": "equivalent",
            "reason": "x",
        }
    )
    with pytest.raises(ValueError):
        mod.validate_judgment(judgment, ["p2"], ["p1"], ["c1"], ["c1"])
    with pytest.raises(ValueError):
        mod.validate_judgment(judgment, ["p2"], [], ["c1"], ["c1"])
    ok = mod.Judgment.model_validate(
        {
            "arm_a": {
                "missing_point_outcomes": [
                    {"point_id": "p2", "verdict": "absent", "reason": "r"}
                ],
                "preserved_point_outcomes": [
                    {"point_id": "p1", "verdict": "preserved_supported", "reason": "r"}
                ],
                "unsupported_claim_ids": ["c1"],
                "contradiction_present": False,
                "wrong_version_or_citation_concern": False,
            },
            "arm_b": {
                "missing_point_outcomes": [
                    {"point_id": "p2", "verdict": "absent", "reason": "r"}
                ],
                "preserved_point_outcomes": [
                    {"point_id": "p1", "verdict": "preserved_supported", "reason": "r"}
                ],
                "unsupported_claim_ids": [],
                "contradiction_present": False,
                "wrong_version_or_citation_concern": False,
            },
            "overall_preference": "equivalent",
            "reason": "x",
        }
    )
    mod.validate_judgment(ok, ["p2"], ["p1"], ["c1"], ["c1"])


def test_mask_arms_attribution_follows_raw_mask():
    mask = {"A": "treatment", "B": "control"}
    judgment = mod.Judgment.model_validate(
        {
            "arm_a": {
                "missing_point_outcomes": [
                    {"point_id": "p2", "verdict": "satisfied_supported", "reason": "r"}
                ],
                "preserved_point_outcomes": [],
                "unsupported_claim_ids": [],
                "contradiction_present": False,
                "wrong_version_or_citation_concern": False,
            },
            "arm_b": {
                "missing_point_outcomes": [
                    {"point_id": "p2", "verdict": "absent", "reason": "r"}
                ],
                "preserved_point_outcomes": [],
                "unsupported_claim_ids": [],
                "contradiction_present": False,
                "wrong_version_or_citation_concern": False,
            },
            "overall_preference": "A",
            "reason": "x",
        }
    )
    record = {"arm_mask": mask}
    attributed = mod.mask_arms(record, judgment)
    assert attributed["treatment"]["missing_point_outcomes"][0]["verdict"] == "satisfied_supported"
    assert attributed["control"]["missing_point_outcomes"][0]["verdict"] == "absent"
    record_even = {"arm_mask": {"A": "control", "B": "treatment"}}
    attributed_even = mod.mask_arms(record_even, judgment)
    assert attributed_even["control"]["missing_point_outcomes"][0]["verdict"] == "satisfied_supported"


def test_meter_embedding_wrapper_does_not_collide_with_base_dispatch():
    """P0 regression: Meter must not shadow VertexAIClient._embed.

    The base embed_query dispatches through self._embed; a Meter override with
    an incompatible signature used to raise TypeError on every embedding call.
    """
    from types import SimpleNamespace

    from panda_agent.llm.vertex import VertexSettings

    config = VertexSettings(
        project="p", generation_model="g", evaluation_judge_model="j"
    )
    meter = mod.Meter(config, client=SimpleNamespace())
    meter._embed = lambda texts, *, task_type, title=None: [[0.1, 0.2]]
    vector = meter.embed_query("hello")
    assert vector == [0.1, 0.2]
    assert meter.events and meter.events[-1]["stage"] == "embedding"
    assert meter.embed_documents(["a", "b"]) == [[0.1, 0.2]]


def test_judge_payload_is_blind_to_arms_and_trace():
    mask = {"A": "treatment", "B": "control"}
    raw = make_raw("n003", mask=mask)
    first_coverage = dict(raw["shared_first_verify"])
    first_coverage["question"] = "question text"
    gold = {"expected_status": "answered", "required_answer_points": []}
    arm_a = raw["control"] if mask["A"] == "control" else raw["treatment"]
    arm_b = raw["control"] if mask["B"] == "control" else raw["treatment"]
    payload = mod.judge_payload(gold, first_coverage, arm_a, arm_b)
    assert set(payload["arm_a"].keys()) == {"status", "claims", "cited_evidence"}
    assert set(payload["arm_b"].keys()) == {"status", "claims", "cited_evidence"}
    text = json.dumps(payload, ensure_ascii=False)
    for forbidden in (
        "e3_trace",
        "newly_admitted",
        "atomic_update_status",
        "missing_point_retrieval_count",
        "arm_mask",
        "retained_support",
    ):
        assert forbidden not in text


def test_judged_infrastructure_failure_is_inconclusive():
    ids = ["n001", "n002", "n003", "n004"]
    raw, judged = {}, {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    judged[ids[0]] = {
        "record_type": "e3_a2_judgment",
        "state": "INFRASTRUCTURE_FAILURE",
        "question_id": ids[0],
        "error": "judge schema violation",
        "usage": [],
    }
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "INCONCLUSIVE"
    assert result["applicability"]["judged_failures"] == [ids[0]]


def test_missing_judged_record_is_inconclusive():
    ids = ["n001", "n002", "n003", "n004"]
    raw, judged = {}, {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    del judged[ids[2]]
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "INCONCLUSIVE"
    assert result["applicability"]["judged_failures"] == [ids[2]]


def test_started_raw_record_is_inconclusive_not_crash():
    ids = ["n001", "n002", "n003", "n004"]
    raw, judged = {}, {}
    for qid in ids:
        r, j = pass_pair(qid)
        raw[qid], judged[qid] = r, j
    raw[ids[3]] = {
        "record_type": "e3_a2_case",
        "state": "STARTED",
        "question_id": ids[3],
        "usage": [],
    }
    result = mod.compute_result(make_manifest(ids), raw, judged, dict(GIT_OK))
    assert result["verdict"] == "INCONCLUSIVE"
    assert result["applicability"]["infrastructure_failures"] == [ids[3]]
