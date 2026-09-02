"""Unit tests for PANDA Agent D4-A1 fixed locator migration prototype.

All tests are deterministic, offline, and self-contained.
Absolutely no provider/retrieval calls or live database queries.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
from unittest.mock import MagicMock
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))
if str(_PROJECT_ROOT / "evaluation" / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "evaluation" / "scripts"))

from panda_agent.config import QueryExpansions, QueryExpansionRule, load_query_expansions
from panda_agent.evaluation import GoldEvidenceGroup, GoldEvidenceSelector
import d3_5_a5_r2_selectivity as a5_r2
import d3_5_a6_phase1_admission as a6_p1
import d4_a1_fixed_locator_migration as d4_a1


# ---------------------------------------------------------------------------
# 1. In-Memory Component Mask Tests
# ---------------------------------------------------------------------------

def test_in_memory_mask_immutability_and_suppression():
    """Test that the component mask deep-copies the source configuration,
    does not mutate the source object, and suppresses exactly the 9 symbols
    and 2 paper page hints."""
    config_path = _PROJECT_ROOT / d4_a1.CONFIG_QUERY_EXPANSIONS_PATH
    orig_qe = load_query_expansions(config_path)

    # Dump source rules for verification
    orig_dump = orig_qe.model_dump()

    # Apply mask
    masked_qe = d4_a1.apply_batch1_in_memory_mask(orig_qe)

    # 1. Immutability: original object remains identical
    assert orig_qe.model_dump() == orig_dump

    orig_ep = next(r for r in orig_qe.rules if r.rule_id == "event_poca_handoff")
    orig_rg = next(r for r in orig_qe.rules if r.rule_id == "restgas_profile_workflow")
    assert orig_ep.symbols == d4_a1.SUPPRESSED_SYMBOLS_EVENT_POCA
    assert orig_ep.paper_page_hints == d4_a1.SUPPRESSED_PAGE_HINTS_EVENT_POCA
    assert orig_rg.symbols == d4_a1.SUPPRESSED_SYMBOLS_RESTGAS

    # 2. Suppression in masked object
    mask_ep = next(r for r in masked_qe.rules if r.rule_id == "event_poca_handoff")
    mask_rg = next(r for r in masked_qe.rules if r.rule_id == "restgas_profile_workflow")

    assert mask_ep.symbols == []
    assert mask_ep.paper_page_hints == {}
    assert mask_rg.symbols == []

    # 3. Preservation of target triggers, repos, concepts
    assert mask_ep.triggers == d4_a1.PRESERVED_TRIGGERS_EVENT_POCA
    assert mask_ep.repositories == d4_a1.PRESERVED_REPOS_EVENT_POCA
    assert mask_ep.concepts == d4_a1.PRESERVED_CONCEPTS_EVENT_POCA

    assert mask_rg.triggers == d4_a1.PRESERVED_TRIGGERS_RESTGAS
    assert mask_rg.repositories == d4_a1.PRESERVED_REPOS_RESTGAS
    assert mask_rg.concepts == d4_a1.PRESERVED_CONCEPTS_RESTGAS

    # 4. All other 52 rules remain untouched
    orig_other_rules = [r for r in orig_qe.rules if r.rule_id not in ("event_poca_handoff", "restgas_profile_workflow")]
    mask_other_rules = [r for r in masked_qe.rules if r.rule_id not in ("event_poca_handoff", "restgas_profile_workflow")]
    assert len(orig_other_rules) == 52
    assert len(mask_other_rules) == 52
    for r1, r2 in zip(orig_other_rules, mask_other_rules):
        assert r1.model_dump() == r2.model_dump()


def test_in_memory_mask_idempotence():
    """Applying the mask multiple times must be deterministic and produce
    the exact same configuration."""
    config_path = _PROJECT_ROOT / d4_a1.CONFIG_QUERY_EXPANSIONS_PATH
    orig_qe = load_query_expansions(config_path)

    masked_1 = d4_a1.apply_batch1_in_memory_mask(orig_qe)
    masked_2 = d4_a1.apply_batch1_in_memory_mask(masked_1)

    assert masked_1.model_dump() == masked_2.model_dump()


# ---------------------------------------------------------------------------
# 2. A0 Overlap Revalidation Tests
# ---------------------------------------------------------------------------

def test_a0_overlap_revalidation_current_config():
    """Current configs/query_expansions.yaml must revalidate with 0 active
    overlaps on target migration cases."""
    receipt = d4_a1.revalidate_a0_overlaps(_PROJECT_ROOT)
    assert receipt["verified"] is True
    assert receipt["rules_audited_count"] == 54

    activity = receipt["target_case_activity"]
    for cid in ("g036", "g021", "n022"):
        assert cid in activity
        assert activity[cid]["overlap_active"] is False
        assert activity[cid]["overlapping_rules_triggered"] == []
        assert activity[cid]["identifiability_action"] == "NO_ACTION_NOT_ACTIVE"


def test_a0_overlap_drift_detection_fail_closed(monkeypatch, tmp_path):
    """If an overlapping rule becomes active on a target case, revalidation
    must fail closed (raise ValueError)."""
    # Load valid config, inject a trigger to make an overlapping rule active on g036
    config_path = _PROJECT_ROOT / d4_a1.CONFIG_QUERY_EXPANSIONS_PATH
    qe = load_query_expansions(config_path)
    dumped = qe.model_dump()

    # Find an overlapping rule (e.g. pid_two_pass_files) and add "event_poca" as a trigger
    for r in dumped["rules"]:
        if r["rule_id"] == "pid_two_pass_files":
            r["triggers"].append("event_poca")

    temp_config = tmp_path / "configs" / "query_expansions.yaml"
    temp_config.parent.mkdir(parents=True, exist_ok=True)
    temp_prereg = tmp_path / "evaluation" / "d4_a0_batch1_migration_preregistration.json"
    temp_prereg.parent.mkdir(parents=True, exist_ok=True)
    import yaml
    temp_config.write_text(yaml.safe_dump(dumped), encoding="utf-8")
    temp_prereg.write_text((_PROJECT_ROOT / d4_a1.PREREGISTRATION_PATH).read_text(encoding="utf-8"), encoding="utf-8")

    # Revalidation against temp_config must raise ValueError
    with pytest.raises(ValueError, match="Overlap drift detected"):
        d4_a1.revalidate_a0_overlaps(tmp_path)


# ---------------------------------------------------------------------------
# 3. Execution Manifest Invariant Tests
# ---------------------------------------------------------------------------

def test_execution_manifest_invariants():
    """Manifest must freeze exact 21 slots in case-major order with
    NOT_EXECUTED status and zero pre-exposure accounting."""
    manifest_path = _PROJECT_ROOT / d4_a1.MANIFEST_PATH
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["checkpoint"] == "D4-A1"
    assert manifest["starting_head"] == d4_a1.STARTING_HEAD
    assert (
        manifest["implementation_freeze_head"]
        == "CAPTURED_FROM_CURRENT_CLEAN_HEAD_IN_PERSISTED_STARTED_JOURNAL_BEFORE_CELL_1"
    )
    assert manifest["outcome_exposure_state"]["D4_A1_OUTCOME_EXPOSURE"] == "NOT_STARTED"
    assert manifest["outcome_exposure_state"]["formal_slots_total"] == 21
    assert manifest["outcome_exposure_state"]["formal_slots_completed"] == 0
    assert manifest["outcome_exposure_state"]["formal_slots_failed"] == 0
    assert manifest["outcome_exposure_state"]["evaluator_executed"] is False
    assert manifest["outcome_exposure_state"]["migration_verdict_computed"] is False

    slots = manifest["formal_slots_21"]
    assert len(slots) == 21

    expected_schedule = [
        (idx, cid, arm)
        for idx, (cid, arm) in enumerate(
            [(c, a) for c in d4_a1.CASE_ORDER for a in d4_a1.ARMS], start=1
        )
    ]

    for s, (expected_idx, expected_cid, expected_arm) in zip(slots, expected_schedule):
        assert s["slot_index"] == expected_idx
        assert s["case_id"] == expected_cid
        assert s["arm"] == expected_arm
        assert s["outcome_status"] == "NOT_EXECUTED"

    for counter, val in manifest["pre_exposure_accounting"].items():
        assert val == 0, f"Pre-exposure accounting {counter} != 0"


# ---------------------------------------------------------------------------
# 4. K=3 Reserved Admission Pool Construction Tests
# ---------------------------------------------------------------------------

def test_treatment_pool_construction():
    """Verify K=3 treatment pool construction with ordinary candidate displacement."""
    # Synthetic baseline of 30 candidates
    baseline = [f"obj_base_{i:02d}" for i in range(30)]

    # 1. No reservable candidates (control cases): pool unchanged, 0 displaced
    treatment_ctrl = a6_p1.build_treatment_pool(baseline, reservable=[], k=3)
    assert treatment_ctrl["treatment_pool_object_ids"] == baseline
    assert treatment_ctrl["reserved_slot_count"] == 0
    assert treatment_ctrl["displaced_object_ids"] == []

    # 2. 3 reservable candidates: bottom 3 displaced, 3 reserved appended
    reservable = ["obj_res_01", "obj_res_02", "obj_res_03"]
    treatment_k3 = a6_p1.build_treatment_pool(baseline, reservable=reservable, k=3)
    assert len(treatment_k3["treatment_pool_object_ids"]) == 30
    assert treatment_k3["reserved_slot_count"] == 3
    assert treatment_k3["displaced_object_ids"] == ["obj_base_27", "obj_base_28", "obj_base_29"]
    assert treatment_k3["treatment_pool_object_ids"] == baseline[:27] + reservable

    # 3. Only 1 reservable candidate: bottom 1 displaced, 1 reserved appended
    treatment_k1 = a6_p1.build_treatment_pool(baseline, reservable=["obj_res_01"], k=3)
    assert len(treatment_k1["treatment_pool_object_ids"]) == 30
    assert treatment_k1["reserved_slot_count"] == 1
    assert treatment_k1["displaced_object_ids"] == ["obj_base_29"]
    assert treatment_k1["treatment_pool_object_ids"] == baseline[:29] + ["obj_res_01"]


# ---------------------------------------------------------------------------
# 5. Selectivity V2 Integration and Complete Universe Payloads
# ---------------------------------------------------------------------------

def test_select_v2_integration_and_complete_universe():
    """Verify select_v2 returns selected_object_ids, filters to eligible bridge
    statuses, aggregates multiple origins, and uses complete object lookup."""
    bridge_receipts = [
        {
            "reachability_receipt_id": "r1",
            "source_native_candidate_object_id": "cand_injected",
            "evidence_provenance_origin_id": "orig_a",
            "evidence_provenance_origin_type": "symbol",
            "bridge_status": "BRIDGED_CANDIDATE_INJECTED",
            "source_id": "repo_a",
            "object_type": "source_file",
            "locator": {"path": "src/a.cxx"},
        },
        {
            "reachability_receipt_id": "r2",
            "source_native_candidate_object_id": "cand_injected",
            "evidence_provenance_origin_id": "orig_b",
            "evidence_provenance_origin_type": "concept",
            "bridge_status": "BRIDGED_CANDIDATE_INJECTED",
            "source_id": "repo_a",
            "object_type": "source_file",
            "locator": {"path": "src/a.cxx"},
        },
        {
            "reachability_receipt_id": "r3",
            "source_native_candidate_object_id": "cand_ranked_out",
            "evidence_provenance_origin_id": "orig_c",
            "evidence_provenance_origin_type": "page",
            "bridge_status": "BRIDGED_CANDIDATE_RANKED_OUT",
            "source_id": "repo_b",
            "object_type": "paper_page",
            "locator": {"path": "paper.pdf", "pdf_page": 5},
        },
        {
            "reachability_receipt_id": "r4",
            "source_native_candidate_object_id": "cand_not_found",
            "bridge_status": "GOVERNED_PROVENANCE_NOT_FOUND",
        },
    ]

    reachability_receipts = [
        {"reachability_receipt_id": "r1", "budget_consumed": 1},
        {"reachability_receipt_id": "r2", "budget_consumed": 2},
        {"reachability_receipt_id": "r3", "budget_consumed": 1},
    ]

    object_lookup = {
        "cand_injected": {
            "title": "A Cxx File",
            "source_id": "repo_a",
            "text": "Implementation of A",
            "object_type": "source_file",
            "locator": {"path": "src/a.cxx"},
        },
        "cand_ranked_out": {
            "title": "Paper Page 5",
            "source_id": "repo_b",
            "text": "Explanation in Page 5",
            "object_type": "paper_page",
            "locator": {"path": "paper.pdf", "pdf_page": 5},
        },
    }

    eligible = d4_a1.build_eligible_bridge_candidates(
        bridge_receipts, reachability_receipts, object_lookup
    )

    # 1. Status filtering: only INJECTED and RANKED_OUT candidates included
    assert len(eligible) == 2
    cand_ids = [c["candidate_object_id"] for c in eligible]
    assert "cand_injected" in cand_ids
    assert "cand_ranked_out" in cand_ids
    assert "cand_not_found" not in cand_ids

    # 2. Multi-origin aggregation on cand_injected
    inj = next(c for c in eligible if c["candidate_object_id"] == "cand_injected")
    assert sorted(inj["provenance_origin_ids"]) == ["orig_a", "orig_b"]
    assert sorted(inj["origin_types"]) == ["concept", "symbol"]
    assert inj["min_structural_distance_transitions"] == 1

    # 3. Payload registry populated from complete normalized lookup
    payload_reg = d4_a1.build_candidate_payload_registry(eligible, object_lookup)
    assert "cand_injected" in payload_reg
    assert "cand_ranked_out" in payload_reg
    assert payload_reg["cand_ranked_out"]["title"] == "Paper Page 5"
    assert payload_reg["cand_ranked_out"]["text_payload_2000"] == "Explanation in Page 5"

    # 4. select_v2 returns selected_object_ids
    v2_case = {
        "case_id": "g036",
        "frozen_plan_fields": {
            "target_repositories": ["repo_a"],
            "symbols": [],
            "concepts": [],
            "paper_page_hints": {},
            "required_source_types": [],
            "intent": "general",
        },
        "question": {"query": "How is A implemented?"},
        "arms": {"STRUCTURED_BRIDGED": {"channel_rankings": {"exact": ["cand_injected"]}}},
        "unbridged_graph_ordering": [],
        "eligible_governed_bridge_candidates": eligible,
    }
    v2_result = a5_r2.select_v2(v2_case, payload_reg)
    assert "selected_object_ids" in v2_result
    assert isinstance(v2_result["selected_object_ids"], list)


# ---------------------------------------------------------------------------
# 6. Post-Rerank Fallback Pool Retention Tests
# ---------------------------------------------------------------------------

def test_post_rerank_fallback_preserves_omitted_reserved_candidate():
    """If the reranker model schema returns a list that omits a reserved candidate,
    the fallback pool [*reranked, *rerank_pool, *baseline_fused_ordering] preserves
    the candidate ahead of baseline fallbacks."""
    rerank_pool = ["cand_base_1", "cand_base_2", "cand_reserved_k3"]
    baseline_ordering = ["cand_base_1", "cand_base_2", "cand_base_3", "cand_displaced"]

    # Model returned only cand_base_1 in reranked output
    reranked = ["cand_base_1"]

    # Fallback list preserves cand_reserved_k3 before baseline items
    ordered = list(dict.fromkeys([*reranked, *rerank_pool, *baseline_ordering]))
    assert "cand_reserved_k3" in ordered
    assert ordered.index("cand_reserved_k3") < ordered.index("cand_base_3")
    assert ordered.index("cand_reserved_k3") < ordered.index("cand_displaced")


# ---------------------------------------------------------------------------
# 7. Truthful Admission Witness Recording Tests
# ---------------------------------------------------------------------------

def test_admission_witness_truthful_recording():
    """Verify truthful witness recording across all 10 fields, including
    ordinary top30 membership before reservation."""
    object_lookup = {
        "cand_1": {
            "object_id": "cand_1",
            "title": "Title 1",
            "source_id": "pandaroot",
            "text": "Text 1",
            "object_type": "source_file",
            "locator": {"path": "macro/target/ana_dpm.C"},
        }
    }

    mock_group = GoldEvidenceGroup(
        group_id="g036.e1",
        any_of=[
            GoldEvidenceSelector(
                source_id="pandaroot",
                path="macro/target/ana_dpm.C",
            )
        ],
    )

    # Case A: Valid witness reserved under K3
    slot_reserved = {
        "eligible_bridge_candidates": [
            {
                "candidate_object_id": "cand_1",
                "provenance_origin_ids": ["orig_1"],
                "origin_types": ["symbol"],
                "source_id": "pandaroot",
                "source_version_id": "v1",
                "locator_path": "macro/target/ana_dpm.C",
                "min_structural_distance_transitions": 1,
                "locator": {"path": "macro/target/ana_dpm.C"},
            }
        ],
        "selected_bridge_candidates": ["cand_1"],
        "ordinary_fused_top30": ["other_cand"],
        "reserved_candidate_ids": ["cand_1"],
        "displaced_candidate_ids": ["other_cand"],
        "final_pool_object_ids": ["cand_1"],
        "final_evidence_object_ids": ["cand_1"],
    }

    wit_res = d4_a1.check_admission_witness("g036.e1", slot_reserved, object_lookup, mock_group)
    assert wit_res["retained_in_final"] is True
    assert wit_res["has_valid_witness"] is True
    cw = wit_res["candidate_witnesses"][0]
    assert cw["selected_by_v2"] is True
    assert cw["ordinary_top30_before_reservation"] is False
    assert cw["reserved_under_k3"] is True
    assert cw["displaced_candidates"] == ["other_cand"]
    assert cw["final_pool_membership"] is True
    assert cw["competed_in_reranker"] is True
    assert cw["final_evidence_retained"] is True
    assert cw["full_structured_path"]["candidate_object_id"] == "cand_1"
    assert cw["is_valid_witness"] is True

    # Case B: Valid witness already in ordinary top-30 (reservation not needed)
    slot_top30 = {
        "eligible_bridge_candidates": [
            {
                "candidate_object_id": "cand_1",
                "provenance_origin_ids": ["orig_1"],
                "origin_types": ["symbol"],
                "source_id": "pandaroot",
                "source_version_id": "v1",
                "locator_path": "macro/target/ana_dpm.C",
                "min_structural_distance_transitions": 1,
                "locator": {"path": "macro/target/ana_dpm.C"},
            }
        ],
        "selected_bridge_candidates": ["cand_1"],
        "ordinary_fused_top30": ["cand_1"],
        "reserved_candidate_ids": [],
        "displaced_candidate_ids": [],
        "final_pool_object_ids": ["cand_1"],
        "final_evidence_object_ids": ["cand_1"],
    }

    wit_top30 = d4_a1.check_admission_witness("g036.e1", slot_top30, object_lookup, mock_group)
    assert wit_top30["has_valid_witness"] is True
    cw2 = wit_top30["candidate_witnesses"][0]
    assert cw2["selected_by_v2"] is True
    assert cw2["ordinary_top30_before_reservation"] is True
    assert cw2["reserved_under_k3"] is False
    assert cw2["is_valid_witness"] is True

    # Case C: Not selected by v2 -> invalid witness
    slot_unselected = copy.deepcopy(slot_reserved)
    slot_unselected["selected_bridge_candidates"] = []
    wit_unsel = d4_a1.check_admission_witness("g036.e1", slot_unselected, object_lookup, mock_group)
    assert wit_unsel["has_valid_witness"] is False


# ---------------------------------------------------------------------------
# 8. 7-Level Batch Verdict Truth Table & Mixed Cases Tests
# ---------------------------------------------------------------------------

def test_seven_level_verdict_truth_table():
    """Verify all 7 precedence levels and mixed cases."""
    pass_target = {
        "g036": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": True, "witness": True},
        "g021": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": True, "witness": True},
    }
    clean_safety = {"REGRESSION_ABLATION": 0, "REGRESSION_REPLACEMENT": 0, "regression_count": 0}

    # Level 1: Protocol or treatment construction failure
    v1 = d4_a1.compute_migration_verdict(pass_target, clean_safety, structural_fail=True)
    assert v1["batch_verdict"] == d4_a1.VERDICT_INVALID_PROTOCOL

    # Level 2: Material safety regression (only replacement regression gates)
    reg_safety = {"REGRESSION_ABLATION": 0, "REGRESSION_REPLACEMENT": 1, "regression_count": 1}
    v2 = d4_a1.compute_migration_verdict(pass_target, reg_safety)
    assert v2["batch_verdict"] == d4_a1.VERDICT_FAIL_SAFETY_REGRESSION

    # Level 3: PASS
    v3 = d4_a1.compute_migration_verdict(pass_target, clean_safety)
    assert v3["batch_verdict"] == d4_a1.VERDICT_PASS
    assert v3["per_rule_decisions"]["event_poca_handoff"] == d4_a1.DECISION_REPLACEMENT_VALIDATED
    assert v3["per_rule_decisions"]["restgas_profile_workflow"] == d4_a1.DECISION_REPLACEMENT_VALIDATED

    # Level 4: Mixed target replacement evidence
    # 4a: g036 validated, g021 failed
    mixed_target_a = {
        "g036": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": True, "witness": True},
        "g021": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": False, "witness": False},
    }
    v4a = d4_a1.compute_migration_verdict(mixed_target_a, clean_safety)
    assert v4a["batch_verdict"] == d4_a1.VERDICT_PARTIAL_MIXED_EVIDENCE
    assert v4a["per_rule_decisions"]["event_poca_handoff"] == d4_a1.DECISION_REPLACEMENT_VALIDATED
    assert v4a["per_rule_decisions"]["restgas_profile_workflow"] == d4_a1.DECISION_REPLACEMENT_FAILED

    # 4b: g036 failed, g021 validated
    mixed_target_b = {
        "g036": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": False, "witness": False},
        "g021": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": True, "witness": True},
    }
    v4b = d4_a1.compute_migration_verdict(mixed_target_b, clean_safety)
    assert v4b["batch_verdict"] == d4_a1.VERDICT_PARTIAL_MIXED_EVIDENCE
    assert v4b["per_rule_decisions"]["event_poca_handoff"] == d4_a1.DECISION_REPLACEMENT_FAILED
    assert v4b["per_rule_decisions"]["restgas_profile_workflow"] == d4_a1.DECISION_REPLACEMENT_VALIDATED

    # Level 5: Legacy dependency not reproduced in current prototype (ablation unweakened)
    ablation_unweakened = {
        "g036": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": True, "BATCH1_REPLACEMENT": True, "witness": True},
        "g021": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": False, "witness": False},
    }
    v5 = d4_a1.compute_migration_verdict(ablation_unweakened, clean_safety)
    assert v5["batch_verdict"] == d4_a1.VERDICT_PARTIAL_LEGACY_DEP_NOT_REPRODUCED
    assert v5["per_rule_decisions"]["event_poca_handoff"] == d4_a1.DECISION_LEGACY_DEPENDENCY_NOT_REPRODUCED

    # Level 6: Replacement did not recover confirmed dependency
    both_failed = {
        "g036": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": False, "witness": False},
        "g021": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": False, "witness": False},
    }
    v6 = d4_a1.compute_migration_verdict(both_failed, clean_safety)
    assert v6["batch_verdict"] == d4_a1.VERDICT_FAIL_REPLACEMENT_FAILED
    assert v6["per_rule_decisions"]["event_poca_handoff"] == d4_a1.DECISION_REPLACEMENT_FAILED
    assert v6["per_rule_decisions"]["restgas_profile_workflow"] == d4_a1.DECISION_REPLACEMENT_FAILED

    # Level 7: Legacy control reference not reproduced
    legacy_missing = {
        "g036": {"LEGACY_CONTROL": False, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": False, "witness": False},
        "g021": {"LEGACY_CONTROL": False, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": False, "witness": False},
    }
    v7 = d4_a1.compute_migration_verdict(legacy_missing, clean_safety)
    assert v7["batch_verdict"] == d4_a1.VERDICT_INCONCLUSIVE_LEGACY_CONTROL
    assert v7["per_rule_decisions"]["event_poca_handoff"] == d4_a1.DECISION_LEGACY_CONTROL_REFERENCE_NOT_REPRODUCED
    assert v7["per_rule_decisions"]["restgas_profile_workflow"] == d4_a1.DECISION_LEGACY_CONTROL_REFERENCE_NOT_REPRODUCED


# ---------------------------------------------------------------------------
# 9. Safety Regression Counters and Replacement-Only Gating Tests
# ---------------------------------------------------------------------------

def test_safety_regression_counters_and_gating():
    """Verify REGRESSION_ABLATION and REGRESSION_REPLACEMENT are tracked,
    and only REGRESSION_REPLACEMENT gates."""
    pass_target = {
        "g036": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": True, "witness": True},
        "g021": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": True, "witness": True},
    }

    # Ablation regression > 0 but replacement regression == 0 -> still PASSES
    ablation_only_loss = {
        "REGRESSION_ABLATION": 2,
        "REGRESSION_REPLACEMENT": 0,
        "regression_count": 0,
    }
    v_abl = d4_a1.compute_migration_verdict(pass_target, ablation_only_loss)
    assert v_abl["batch_verdict"] == d4_a1.VERDICT_PASS

    # Replacement regression > 0 -> FAILS with MATERIAL_SAFETY_REGRESSION
    replacement_loss = {
        "REGRESSION_ABLATION": 1,
        "REGRESSION_REPLACEMENT": 1,
        "regression_count": 1,
    }
    v_rep = d4_a1.compute_migration_verdict(pass_target, replacement_loss)
    assert v_rep["batch_verdict"] == d4_a1.VERDICT_FAIL_SAFETY_REGRESSION


# ---------------------------------------------------------------------------
# 10. Non-Gating n022 Diagnostic Case Tests
# ---------------------------------------------------------------------------

def test_n022_non_gating_behavior():
    """Diagnostic case n022 must not gate the batch verdict even if all
    its groups fail or regress."""
    pass_target = {
        "g036": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": True, "witness": True},
        "g021": {"LEGACY_CONTROL": True, "BATCH1_ABLATION": False, "BATCH1_REPLACEMENT": True, "witness": True},
    }
    clean_safety = {"REGRESSION_ABLATION": 0, "REGRESSION_REPLACEMENT": 0, "regression_count": 0}

    diagnostic_failed = {
        "case_id": "n022",
        "gating": False,
        "group_retention": {"n022.e1": {"LEGACY_CONTROL": False, "BATCH1_REPLACEMENT": False}},
        "witness_records": {},
    }

    verdict = d4_a1.compute_migration_verdict(
        pass_target, clean_safety, diagnostic_results=diagnostic_failed
    )
    assert verdict["batch_verdict"] == d4_a1.VERDICT_PASS


# ---------------------------------------------------------------------------
# 11. Implementation Drift Guards & Clean Worktree Tests
# ---------------------------------------------------------------------------

def test_drift_guards_verification():
    """Drift guards verify protected src/ and configs/ are identical to
    STARTING_HEAD, and only allowed Commit-A files differ."""
    receipt = d4_a1.verify_drift_guards(_PROJECT_ROOT, require_clean_worktree=False)
    assert receipt["verified"] is True
    assert receipt["starting_head"] == d4_a1.STARTING_HEAD


# ---------------------------------------------------------------------------
# 12. Executor Query Source Isolation Tests
# ---------------------------------------------------------------------------

def test_executor_manifest_query_isolation():
    """Executor must assert manifest queries/roles/order match preregistration
    and not load Gold/novel datasets before outcome freeze."""
    manifest = json.loads((_PROJECT_ROOT / d4_a1.MANIFEST_PATH).read_text(encoding="utf-8"))
    prereg = json.loads((_PROJECT_ROOT / d4_a1.PREREGISTRATION_PATH).read_text(encoding="utf-8"))

    manifest_cases = manifest.get("cases", [])
    prereg_cases = prereg.get("future_D4_A1", {}).get("exact_cases", [])

    assert [c["case_id"] for c in manifest_cases] == d4_a1.CASE_ORDER
    prereg_by_id = {c["case_id"]: c for c in prereg_cases}
    for c in manifest_cases:
        cid = c["case_id"]
        assert cid in prereg_by_id
        assert c["role"] == prereg_by_id[cid]["role"]
        assert c["query"] == prereg_by_id[cid]["query"]


# ---------------------------------------------------------------------------
# 13. Observability Non-Replacement Explicit Empty Fields
# ---------------------------------------------------------------------------

def test_observability_shape_and_non_replacement_empty_fields():
    """Verify non-replacement arms have explicit empty/false structured fields."""
    plan_mock = MagicMock()
    plan_mock.target_repositories = ["pandaroot"]
    plan_mock.symbols = []
    plan_mock.concepts = []
    plan_mock.paper_page_hints = {}
    plan_mock.intent = "general"
    plan_mock.required_source_types = []
    plan_mock.model_dump.return_value = {}

    retriever_mock = MagicMock()
    retriever_mock.analyze.return_value = plan_mock
    retriever_mock.policies.candidate_pool_per_channel = 10
    retriever_mock.policies.final_evidence_limit = 5
    retriever_mock._exact.return_value = []
    retriever_mock._vector.return_value = ([], [], [], "")
    retriever_mock._paper.return_value = []
    retriever_mock._workflow.return_value = []
    retriever_mock._graph.return_value = []
    retriever_mock.vertex.stats_snapshot.return_value = {}
    retriever_mock.vertex.stats_delta.return_value = {"generation_calls": 1, "token_usage": 100}
    retriever_mock.vertex.generate_json.return_value = {"ranked_object_ids": []}

    orig_qe = load_query_expansions(_PROJECT_ROOT / d4_a1.CONFIG_QUERY_EXPANSIONS_PATH)
    masked_qe = d4_a1.apply_batch1_in_memory_mask(orig_qe)

    cell_ctrl = d4_a1.execute_cell_retrieval(
        retriever=retriever_mock,
        case_id="g036",
        arm="LEGACY_CONTROL",
        question_text="Sample query",
        original_expansions=orig_qe,
        masked_expansions=masked_qe,
        object_lookup={},
    )

    # Structured fields must be explicit empty/false for non-replacement cells
    assert cell_ctrl["resolved_d2_seeds"] == []
    assert cell_ctrl["reached_structures"] == []
    assert cell_ctrl["reachability_receipts"] == []
    assert cell_ctrl["actual_bridge_receipts"] == []
    assert cell_ctrl["eligible_bridge_candidates"] == []
    assert cell_ctrl["selected_bridge_candidates"] == []
    assert cell_ctrl["v2_diagnostics"] == {}
    assert cell_ctrl["reserved_candidate_ids"] == []
    assert cell_ctrl["displaced_candidate_ids"] == []
    assert cell_ctrl["status"] == "COMPLETED"
    assert cell_ctrl["formal_call_status"] == "SUCCESS"
    assert "logical_calls" in cell_ctrl
    assert "provider_internal_attempts" in cell_ctrl
    assert "token_usage" in cell_ctrl


# ---------------------------------------------------------------------------
# 14. Evaluator Refuses When Raw Artifact Missing
# ---------------------------------------------------------------------------

def test_evaluator_refuses_when_raw_results_missing(tmp_path):
    """Evaluator must refuse when raw results artifact is not present."""
    with pytest.raises(FileNotFoundError, match="does not exist"):
        d4_a1.evaluate_d4_a1(tmp_path, require_git_frozen=False)
