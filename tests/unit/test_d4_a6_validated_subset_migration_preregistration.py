"""Unit tests for D4-A6 Validated-Subset Batch2 Runtime Migration Preregistration.

Tests 1 to 10 covering:
1. Starting boundary & identity check
2. Frozen D4-A5 verdict consumption check
3. Per-rule disposition mapping check
4. Frozen retirement masks audit check
5. Independent origins and occurrences check
6. Production mechanism audit check
7. Prospective diff validation check
8. Readiness conditions and decision check
9. Preregistration artifacts verification check
10. Immutability and zero production mutation check
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EVAL_SCRIPTS = _REPO_ROOT / "evaluation" / "scripts"
for _p in (str(_EVAL_SCRIPTS), str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import d4_a6_validated_subset_migration_preregistration as a6


def test_1_starting_boundary_and_identity() -> None:
    """Test 1: Verify starting HEAD, commit message, and parent closeout commit."""
    assert a6.STARTING_HEAD == "7b9d9d13903d874c000c0097304bfccc19dbbf65"
    assert a6.STARTING_COMMIT_MESSAGE == "D4-A5-R8 repair post-closeout verification contract"
    assert a6.CLOSEOUT_HEAD == "c33f4cbe0bc2dfe6352d70396ebbdc203d3c624f"
    assert a6.CLOSEOUT_COMMIT_MESSAGE == "D4-A5 continuation close controlled retirement validation"

    # Verify actual git log matches expected starting head and closeout head
    cmd = ["git", "rev-parse", "HEAD"]
    res = subprocess.run(cmd, cwd=_REPO_ROOT, capture_output=True, text=True, check=True)
    current_head = res.stdout.strip()

    if current_head == a6.STARTING_HEAD:
        starting_head = current_head
        cmd_parent = ["git", "rev-parse", "HEAD~1"]
        parent_head = subprocess.run(cmd_parent, cwd=_REPO_ROOT, capture_output=True, text=True, check=True).stdout.strip()
    else:
        # Already committed D4-A6
        cmd_start = ["git", "rev-parse", "HEAD~1"]
        starting_head = subprocess.run(cmd_start, cwd=_REPO_ROOT, capture_output=True, text=True, check=True).stdout.strip()
        cmd_closeout = ["git", "rev-parse", "HEAD~2"]
        parent_head = subprocess.run(cmd_closeout, cwd=_REPO_ROOT, capture_output=True, text=True, check=True).stdout.strip()

    assert starting_head == a6.STARTING_HEAD
    assert parent_head == a6.CLOSEOUT_HEAD


def test_2_frozen_d4_a5_verdict_consumption() -> None:
    """Test 2: Verify D4-A5 scientific verdict is consumed directly without recomputation."""
    scientific = a6.load_frozen_d4_a5_scientific_outcome(_REPO_ROOT)
    assert scientific["verdict_level"] == 2
    assert scientific["verdict"] == "INCONCLUSIVE / BATCH2_REFERENCE_BASELINE_NOT_REPRODUCED"
    assert scientific["reference_baseline_valid"] is None
    assert "effective_acceptance_pipeline" in scientific["per_rule_dispositions"]
    assert "root_macro_usage" in scientific["per_rule_dispositions"]
    assert "model_factory_theory" in scientific["per_rule_dispositions"]


def test_3_per_rule_disposition_mapping() -> None:
    """Test 3: Verify per-rule disposition mapping to migration eligibility."""
    scientific = a6.load_frozen_d4_a5_scientific_outcome(_REPO_ROOT)
    eligibility = a6.map_dispositions_to_migration_eligibility(scientific)

    # effective_acceptance_pipeline
    eap = eligibility["effective_acceptance_pipeline"]
    assert eap["scientific_disposition"] == "RETIREMENT_VALIDATED"
    assert eap["production_migration_eligibility"] == "MIGRATION_ELIGIBLE"
    assert eap["prospective_production_mutation"]["action"] == (
        "RETIRE_VALIDATED_LOCATORS_AND_ACTIVATE_STRUCTURED_REPLACEMENT"
    )
    assert eap["prospective_production_mutation"]["structured_replacement"] is True
    assert eap["prospective_production_mutation"]["symbols"] == []

    # root_macro_usage
    rmu = eligibility["root_macro_usage"]
    assert rmu["scientific_disposition"] == "RETIREMENT_VALIDATED"
    assert rmu["production_migration_eligibility"] == "MIGRATION_ELIGIBLE"
    assert rmu["prospective_production_mutation"]["action"] == (
        "RETIRE_VALIDATED_LOCATORS_AND_ACTIVATE_STRUCTURED_REPLACEMENT"
    )
    assert rmu["prospective_production_mutation"]["structured_replacement"] is True
    assert rmu["prospective_production_mutation"]["symbols"] == []

    # model_factory_theory
    mft = eligibility["model_factory_theory"]
    assert mft["scientific_disposition"] == "INCONCLUSIVE_BASELINE_NOT_REPRODUCED"
    assert mft["production_migration_eligibility"] == "HOLD"
    assert mft["prospective_production_mutation"]["action"] == (
        "NO_ACTION_HOLD_EXISTING_PRODUCTION_CONTRACT"
    )
    assert "n014.e1" in mft["hold_reason"]
    assert "n003.e2" in mft["hold_reason"]


def test_4_frozen_retirement_masks_audit() -> None:
    """Test 4: Verify production configs/query_expansions.yaml matches frozen D4-A4 masks."""
    audit = a6.audit_current_production_config(_REPO_ROOT)
    assert not audit["material_drift"]
    assert audit["total_rules"] == 54

    rules = audit["rules"]
    for r_id in a6.BATCH2_SELECTED_RULES:
        assert rules[r_id]["exists"]
        assert rules[r_id]["symbols_match_frozen"]
        assert rules[r_id]["paper_page_hints_match_frozen"]
        assert not rules[r_id]["structured_replacement"]
        assert not rules[r_id]["material_drift"]

    # Verify specific symbols match frozen
    assert rules["effective_acceptance_pipeline"]["symbols"] == [
        "macro/target/prod_sim_hvmaps.C",
        "data/PndLmdAcceptance.cxx",
        "model/PndLmdModelFactory.cxx",
    ]
    assert rules["effective_acceptance_pipeline"]["paper_page_hints"] == {
        "li_2026": [83, 86, 89],
    }
    assert rules["root_macro_usage"]["symbols"] == [
        "Running/Macros.html",
        "tools/MasterTasks/PndMasterRunSim.cxx",
    ]
    assert rules["model_factory_theory"]["symbols"] == [
        "model/PndLmdDPMAngModel1D.cxx",
        "model/PndLmdDPMAngModel2D.cxx",
        "model/PndLmdModelFactory.cxx",
    ]
    assert rules["model_factory_theory"]["paper_page_hints"] == {
        "pflueger_2017": [51, 57, 65],
    }


def test_5_independent_origins_and_occurrences() -> None:
    """Test 5: Verify multi-origin locators survive in independent rules."""
    occ_audit = a6.audit_locator_occurrences(_REPO_ROOT)
    assert occ_audit["rule_local_retirement_proven"]

    occurrences = occ_audit["occurrences"]
    # model/PndLmdModelFactory.cxx is in held model_factory_theory AND acceptance_model_boundary
    assert "model_factory_theory" in occurrences["model/PndLmdModelFactory.cxx"]
    assert "acceptance_model_boundary" in occurrences["model/PndLmdModelFactory.cxx"]

    # macro/target/prod_sim_hvmaps.C is in reconstructed_profile_to_acceptance
    assert "reconstructed_profile_to_acceptance" in occurrences["macro/target/prod_sim_hvmaps.C"]

    # data/PndLmdAcceptance.cxx is in reconstructed_profile_to_acceptance
    assert "reconstructed_profile_to_acceptance" in occurrences["data/PndLmdAcceptance.cxx"]

    # All preservation witnesses pass
    witnesses = occ_audit["preservation_witnesses"]
    assert witnesses["model/PndLmdModelFactory.cxx_in_held_rule"]
    assert witnesses["macro/target/prod_sim_hvmaps.C_in_independent_rule"]
    assert witnesses["data/PndLmdAcceptance.cxx_in_independent_rule"]


def test_6_production_mechanism_audit() -> None:
    """Test 6: Verify generic structured replacement mechanism is rule-local and reusable."""
    mech = a6.audit_structured_replacement_mechanism(_REPO_ROOT)
    assert mech["has_structured_repl_in_config"]
    assert mech["has_active_migrated_rules"]
    assert mech["has_rule_local_filter"]
    assert mech["has_treatment_pool_k3"]
    assert mech["no_batch2_hardcoding"]
    assert mech["existing_generic_mechanism_reusable"]
    assert not mech["all_or_nothing_coupling_present"]


def test_7_prospective_diff_validation() -> None:
    """Test 7: Verify prospective diff strictly affects only eligible rules."""
    diff_res = a6.construct_prospective_diff(_REPO_ROOT)
    assert diff_res["changed_rules_match_eligible"]
    assert diff_res["held_rule_untouched"]
    assert set(diff_res["changed_rules"]) == {"effective_acceptance_pipeline", "root_macro_usage"}

    diff_text = diff_res["diff_text"]
    assert "effective_acceptance_pipeline" in diff_text
    assert "root_macro_usage" in diff_text
    assert "model_factory_theory" not in diff_text
    assert "-    symbols: [macro/target/prod_sim_hvmaps.C, data/PndLmdAcceptance.cxx, model/PndLmdModelFactory.cxx]" in diff_text
    assert "+    symbols: []" in diff_text
    assert "+    structured_replacement: true" in diff_text
    assert "-    symbols: [Running/Macros.html, tools/MasterTasks/PndMasterRunSim.cxx]" in diff_text
    # Ensure paper_page_hints on effective_acceptance_pipeline are NOT removed
    assert "-    paper_page_hints:" not in diff_text


def test_8_readiness_conditions_and_decision() -> None:
    """Test 8: Verify all 7 readiness conditions pass and evaluate to READY."""
    eval_res = a6.evaluate_d4_a6_decision(_REPO_ROOT)
    assert eval_res["all_passed"]
    assert eval_res["decision"] == "READY_FOR_VALIDATED_SUBSET_MIGRATION"

    conditions = eval_res["conditions"]
    assert conditions["exactly_two_rules_validated"]
    assert conditions["model_factory_theory_held"]
    assert conditions["no_production_config_drift"]
    assert conditions["existing_generic_mechanism_reusable"]
    assert conditions["rule_local_activation_representable"]
    assert conditions["prospective_diff_strictly_limited_to_eligible"]
    assert conditions["independent_origins_preserved"]


def test_9_preregistration_artifacts_verification() -> None:
    """Test 9: Verify artifacts generation and verification logic."""
    verify_res = a6.verify_d4_a6_artifacts(_REPO_ROOT)
    assert verify_res["status"] == "PASS"
    assert verify_res["decision"] == "READY_FOR_VALIDATED_SUBSET_MIGRATION"
    assert verify_res["decision_matches_evaluation"]

    # Verify files exist on disk
    decision_path = _REPO_ROOT / a6.DECISION_JSON_PATH
    prereg_path = _REPO_ROOT / a6.PREREGISTRATION_JSON_PATH
    md_path = _REPO_ROOT / a6.PREREGISTRATION_MD_PATH

    assert decision_path.is_file()
    assert prereg_path.is_file()
    assert md_path.is_file()

    with open(decision_path, encoding="utf-8") as f:
        decision_data = json.load(f)
    assert decision_data["lifecycle_stage"] == "D4-A6"
    assert decision_data["decision"] == "READY_FOR_VALIDATED_SUBSET_MIGRATION"
    assert decision_data["governance"]["batch1_active"] is True
    assert decision_data["governance"]["batch2_production_activation"] is False

    with open(prereg_path, encoding="utf-8") as f:
        prereg_data = json.load(f)
    assert prereg_data["lifecycle_stage"] == "D4-A6"
    assert prereg_data["decision"] == "READY_FOR_VALIDATED_SUBSET_MIGRATION"


def test_10_immutability_and_zero_production_mutation() -> None:
    """Test 10: Verify zero mutation to production files and prior scientific artifacts."""
    cmd = ["git", "status", "--porcelain"]
    res = subprocess.run(cmd, cwd=_REPO_ROOT, capture_output=True, text=True, check=True)
    lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]

    # Production paths that must never be modified
    forbidden_modified_prefixes = [
        "configs/",
        "src/",
        "evaluation/d4_a5",
        "evaluation/d4_a4",
        "evaluation/d3",
    ]

    for line in lines:
        status = line[:2]
        path = line[3:]
        for prefix in forbidden_modified_prefixes:
            assert not path.startswith(prefix), f"Forbidden modification detected in {path} ({status})"
