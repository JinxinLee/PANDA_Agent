"""Unit tests for D4-A6-R1 Validated-Subset Locator-Retirement Production Mapping Repair.

Comprehensive test suite covering:
  Group A: Prospective mapping validator (Tests 1-6)
  Group B: Runtime semantic source validation via AST (Tests 7-9)
  Group C: Git boundary verification and seals (Tests 10-15)
  Group D: Preservation, immutability, and governance invariants (Tests 16-21)
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EVAL_SCRIPTS = _REPO_ROOT / "evaluation" / "scripts"
for _p in (str(_EVAL_SCRIPTS), str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import d4_a6_r1_locator_retirement_mapping_repair as r1


# ---------------------------------------------------------------------------
# Group A: Prospective mapping validator (Tests 1-6)
# ---------------------------------------------------------------------------

def test_1_prospective_mapping_valid() -> None:
    """Test A.1: Valid locator-retirement-only mapping passes validate_prospective_mapping."""
    mut_res = r1.construct_repaired_prospective_mutation(_REPO_ROOT)
    with open(_REPO_ROOT / r1.QUERY_EXPANSIONS_PATH, encoding="utf-8") as f:
        orig_config = yaml.safe_load(f)
    prosp_config = mut_res["prospective_dict"]

    val_res = r1.validate_prospective_mapping(orig_config, prosp_config)
    assert val_res["is_valid"] is True
    assert val_res["errors"] == []
    assert sorted(val_res["changed_rule_ids"]) == sorted(r1.VALIDATED_ELIGIBLE_RULES)
    assert val_res["changed_fields_by_rule"] == {
        "effective_acceptance_pipeline": ["symbols"],
        "root_macro_usage": ["symbols"],
    }


def test_2_structured_replacement_activation_rejected() -> None:
    """Test A.2: structured_replacement = true on either eligible rule fails validator."""
    with open(_REPO_ROOT / r1.QUERY_EXPANSIONS_PATH, encoding="utf-8") as f:
        orig_config = yaml.safe_load(f)
    mut_res = r1.construct_repaired_prospective_mutation(_REPO_ROOT)

    # Variant 1: effective_acceptance_pipeline
    prosp1 = copy.deepcopy(mut_res["prospective_dict"])
    for r in prosp1["rules"]:
        if r["rule_id"] == "effective_acceptance_pipeline":
            r["structured_replacement"] = True
    val1 = r1.validate_prospective_mapping(orig_config, prosp1)
    assert val1["is_valid"] is False
    assert any("structured_replacement" in err for err in val1["errors"])

    # Variant 2: root_macro_usage
    prosp2 = copy.deepcopy(mut_res["prospective_dict"])
    for r in prosp2["rules"]:
        if r["rule_id"] == "root_macro_usage":
            r["structured_replacement"] = True
    val2 = r1.validate_prospective_mapping(orig_config, prosp2)
    assert val2["is_valid"] is False
    assert any("structured_replacement" in err for err in val2["errors"])


def test_3_structured_replacement_field_insertion_rejected() -> None:
    """Test A.3: Insertion of structured_replacement: false where absent fails validator."""
    with open(_REPO_ROOT / r1.QUERY_EXPANSIONS_PATH, encoding="utf-8") as f:
        orig_config = yaml.safe_load(f)
    mut_res = r1.construct_repaired_prospective_mutation(_REPO_ROOT)

    prosp = copy.deepcopy(mut_res["prospective_dict"])
    for r in prosp["rules"]:
        if r["rule_id"] == "effective_acceptance_pipeline":
            r["structured_replacement"] = False  # unnecessarily inserted
    val = r1.validate_prospective_mapping(orig_config, prosp)
    assert val["is_valid"] is False
    assert any("unnecessarily inserted" in err for err in val["errors"])


def test_4_trigger_repository_concept_hint_drift_rejected() -> None:
    """Test A.4: Any change to trigger/repository/concept/hint fails validator."""
    with open(_REPO_ROOT / r1.QUERY_EXPANSIONS_PATH, encoding="utf-8") as f:
        orig_config = yaml.safe_load(f)
    mut_res = r1.construct_repaired_prospective_mutation(_REPO_ROOT)

    # 1. trigger drift
    prosp_trig = copy.deepcopy(mut_res["prospective_dict"])
    for r in prosp_trig["rules"]:
        if r["rule_id"] == "effective_acceptance_pipeline":
            r["triggers"] = ["mutated_trigger"]
    assert r1.validate_prospective_mapping(orig_config, prosp_trig)["is_valid"] is False

    # 2. repository drift
    prosp_repo = copy.deepcopy(mut_res["prospective_dict"])
    for r in prosp_repo["rules"]:
        if r["rule_id"] == "root_macro_usage":
            r["repositories"] = ["mutated_repo"]
    assert r1.validate_prospective_mapping(orig_config, prosp_repo)["is_valid"] is False

    # 3. concept drift
    prosp_conc = copy.deepcopy(mut_res["prospective_dict"])
    for r in prosp_conc["rules"]:
        if r["rule_id"] == "effective_acceptance_pipeline":
            r["concepts"] = ["mutated_concept"]
    assert r1.validate_prospective_mapping(orig_config, prosp_conc)["is_valid"] is False

    # 4. hint drift
    prosp_hint = copy.deepcopy(mut_res["prospective_dict"])
    for r in prosp_hint["rules"]:
        if r["rule_id"] == "effective_acceptance_pipeline":
            r["paper_page_hints"] = {"li_2026": [999]}
    assert r1.validate_prospective_mapping(orig_config, prosp_hint)["is_valid"] is False


def test_5_mutation_of_model_factory_theory_rejected() -> None:
    """Test A.5: Any mutation of held rule model_factory_theory fails validator."""
    with open(_REPO_ROOT / r1.QUERY_EXPANSIONS_PATH, encoding="utf-8") as f:
        orig_config = yaml.safe_load(f)
    mut_res = r1.construct_repaired_prospective_mutation(_REPO_ROOT)

    prosp = copy.deepcopy(mut_res["prospective_dict"])
    for r in prosp["rules"]:
        if r["rule_id"] == "model_factory_theory":
            r["symbols"] = []
    val = r1.validate_prospective_mapping(orig_config, prosp)
    assert val["is_valid"] is False
    assert any("model_factory_theory" in err for err in val["errors"])


def test_6_third_rule_mutation_rejected() -> None:
    """Test A.6: Any third rule mutation outside the two eligible rules fails validator."""
    with open(_REPO_ROOT / r1.QUERY_EXPANSIONS_PATH, encoding="utf-8") as f:
        orig_config = yaml.safe_load(f)
    mut_res = r1.construct_repaired_prospective_mutation(_REPO_ROOT)

    prosp = copy.deepcopy(mut_res["prospective_dict"])
    for r in prosp["rules"]:
        if r["rule_id"] == "restgas_workflow_usage":
            r["symbols"] = []
    val = r1.validate_prospective_mapping(orig_config, prosp)
    assert val["is_valid"] is False
    assert any("restgas_workflow_usage" in err for err in val["errors"])


# ---------------------------------------------------------------------------
# Group B: Runtime semantic source validation via AST (Tests 7-9)
# ---------------------------------------------------------------------------

def test_7_runtime_semantic_retrieval_source_valid() -> None:
    """Test B.7: Actual current retrieval.py passes AST semantic inspection."""
    audit_res = r1.audit_runtime_semantic_survivability(_REPO_ROOT)
    assert audit_res["retrieval_source_read"] is True
    assert audit_res["active_matching_rule_iteration_verified"] is True
    assert audit_res["rule_local_symbol_extension_verified"] is True
    assert audit_res["post_merge_symbol_deduplication_verified"] is True
    assert audit_res["independent_origin_survivability_supported"] is True
    assert audit_res["mechanism_status"] == "PASS"


def test_8_runtime_semantic_missing_rule_local_extend_rejected() -> None:
    """Test B.8: Synthetic source without rule-local symbol extension fails AST inspection."""
    retrieval_file = _REPO_ROOT / r1.RETRIEVAL_PY_PATH
    orig_source = retrieval_file.read_text(encoding="utf-8")

    # Replace rule-local symbols.extend
    synthetic_source = orig_source.replace(
        "parsed.symbols.extend(rule.symbols)",
        "# parsed.symbols.extend(rule.symbols) removed",
    )
    audit_res = r1.audit_runtime_semantic_survivability(source_text=synthetic_source)
    assert audit_res["rule_local_symbol_extension_verified"] is False
    assert audit_res["independent_origin_survivability_supported"] is False
    assert audit_res["mechanism_status"] == "FAIL"


def test_9_runtime_semantic_missing_deduplication_rejected() -> None:
    """Test B.9: Synthetic source without post-merge deduplication fails AST inspection."""
    retrieval_file = _REPO_ROOT / r1.RETRIEVAL_PY_PATH
    orig_source = retrieval_file.read_text(encoding="utf-8")

    # Replace parsed.symbols deduplication
    synthetic_source = orig_source.replace(
        "parsed.symbols = list(dict.fromkeys(parsed.symbols))",
        "# parsed.symbols dedup removed",
    )
    audit_res = r1.audit_runtime_semantic_survivability(source_text=synthetic_source)
    assert audit_res["post_merge_symbol_deduplication_verified"] is False
    assert audit_res["independent_origin_survivability_supported"] is False
    assert audit_res["mechanism_status"] == "FAIL"


# ---------------------------------------------------------------------------
# Group C: Git boundary verification and seals (Tests 10-15)
# ---------------------------------------------------------------------------

def test_10_git_boundary_wrong_commit_message_rejected() -> None:
    """Test C.10: Wrong R1 commit message fails verify_git_commit_identity."""
    res = r1.verify_git_commit_identity(
        _REPO_ROOT,
        _override_message="Wrong commit message for R1",
    )
    assert res["r1_commit_message_exact"] is False
    assert res["all_valid"] is False


def test_11_git_boundary_wrong_parent_rejected() -> None:
    """Test C.11: Wrong R1 parent fails verify_git_commit_identity."""
    res = r1.verify_git_commit_identity(
        _REPO_ROOT,
        _override_parent="0000000000000000000000000000000000000000",
    )
    assert res["r1_parent_exact"] is False
    assert res["all_valid"] is False


def test_12_git_boundary_unauthorized_eighth_file_rejected() -> None:
    """Test C.12: Unauthorized eighth file in cumulative diff fails verify_git_cumulative_diff."""
    forged_diff = r1.EXPECTED_R1_PATHS + ["unauthorized/extra_file.py"]
    res = r1.verify_git_cumulative_diff(
        _REPO_ROOT,
        _override_diff_paths=forged_diff,
    )
    assert res["exact_match"] is False
    assert "unauthorized/extra_file.py" in res["extra_paths"]


def test_13_git_boundary_production_tree_changed_rejected() -> None:
    """Test C.13: Changed production tree fails verify_production_tree_immutability."""
    # Mismatch src tree
    res_src = r1.verify_production_tree_immutability(
        _REPO_ROOT,
        _override_src_tree=("forged_src_tree_hash", "actual_src_tree_hash"),
    )
    assert res_src["src_tree_immutable"] is False
    assert res_src["production_tree_immutability"] is False

    # Mismatch configs tree
    res_cfg = r1.verify_production_tree_immutability(
        _REPO_ROOT,
        _override_configs_tree=("forged_cfg_tree_hash", "actual_cfg_tree_hash"),
    )
    assert res_cfg["configs_tree_immutable"] is False
    assert res_cfg["production_tree_immutability"] is False


def test_14_git_boundary_d4_a5_scientific_artifact_changed_rejected() -> None:
    """Test C.14: Changed D4-A5 scientific artifact fails authority/scientific blob seal."""
    res = r1.verify_authority_and_scientific_blob_immutability(
        _REPO_ROOT,
        _override_d4_a5_match=False,
    )
    assert res["d4_a5_scientific_artifact_immutability"] is False


def test_15_git_boundary_r1_mapping_artifact_changed_rejected() -> None:
    """Test C.15: Changed R1 decision/prereg mapping artifact fails verify_r1_mapping_artifacts_immutability."""
    res = r1.verify_r1_mapping_artifacts_immutability(
        _REPO_ROOT,
        _override_match=False,
    )
    assert res["r1_mapping_artifacts_unchanged"] is False


# ---------------------------------------------------------------------------
# Group D: Preservation, immutability, and governance invariants (Tests 16-21)
# ---------------------------------------------------------------------------

def test_16_defect_reproduction() -> None:
    """Test D.16: Defect reproduction detects PROSPECTIVE_MAPPING_ADDED_UNVALIDATED_STRUCTURED_REPLACEMENT_BEHAVIOR."""
    defect_res = r1.reproduce_historical_d4_a6_defect(_REPO_ROOT)
    assert defect_res["defect_detected"] is True
    assert defect_res["defect_code"] == "PROSPECTIVE_MAPPING_ADDED_UNVALIDATED_STRUCTURED_REPLACEMENT_BEHAVIOR"
    assert defect_res["d4_a4_frozen_after_retirement_states"]["effective_acceptance_pipeline"] is False
    assert defect_res["d4_a4_frozen_after_retirement_states"]["root_macro_usage"] is False
    assert defect_res["d4_a4_frozen_after_retirement_states"]["model_factory_theory"] is False
    assert defect_res["d4_a6_proposed_structured_replacement_states"]["effective_acceptance_pipeline"] is True
    assert defect_res["d4_a6_proposed_structured_replacement_states"]["root_macro_usage"] is True


def test_17_governance_eligibility_preserved() -> None:
    """Test D.17: Governance preserves two eligible and one held rule."""
    eval_res = r1.evaluate_d4_a6_r1_decision(_REPO_ROOT)
    conds = eval_res["conditions"]
    assert conds["exactly_two_rules_validated"] is True
    assert conds["model_factory_theory_held"] is True
    assert conds["d4_a5_scientific_verdict_preserved"] is True
    assert conds["runtime_semantic_survivability_verified"] is True
    assert eval_res["decision"] == "READY_FOR_VALIDATED_SUBSET_LOCATOR_RETIREMENT"


def test_18_independent_origins_preserved() -> None:
    """Test D.18: Candidate locators survive in independent rules with all 6 witnesses verified."""
    orig_res = r1.audit_independent_origins(_REPO_ROOT)
    assert orig_res["all_independent_origins_preserved"] is True
    witnesses = orig_res["preservation_witnesses"]
    assert witnesses["model_factory_in_held_rule"] is True
    assert witnesses["model_factory_in_independent_rule"] is True
    assert witnesses["prod_sim_hvmaps_in_independent_rule"] is True
    assert witnesses["lmd_acceptance_in_independent_rule"] is True
    assert witnesses["running_macros_in_independent_rule"] is True
    assert witnesses["master_run_sim_in_independent_rule"] is True


def test_19_historical_a6_artifacts_preserved() -> None:
    """Test D.19: Historical D4-A6 artifacts remain sealed and immutable."""
    blob_res = r1.verify_historical_d4_a6_blobs(_REPO_ROOT)
    assert blob_res["historical_blobs_sealed"] is True
    for p, sealed in blob_res["blob_checks"].items():
        assert sealed is True, f"Historical blob drifted: {p}"


def test_20_no_production_write() -> None:
    """Test D.20: No uncommitted production modifications in configs/ or src/."""
    cmd = ["git", "status", "--porcelain"]
    res = subprocess.run(cmd, cwd=_REPO_ROOT, capture_output=True, text=True, check=True)
    lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
    for l in lines:
        path = l[3:]
        assert not path.startswith("configs/"), f"Production file modified: {path}"
        assert not path.startswith("src/"), f"Production file modified: {path}"


def test_21_live_commit_identity_and_tree_immutability() -> None:
    """Test D.21: Live repository verifies valid commit identity and committed production tree immutability."""
    commit_res = r1.verify_git_commit_identity(_REPO_ROOT)
    assert commit_res["r1_commit_message_exact"] is True
    assert commit_res["r1_parent_exact"] is True
    assert commit_res["d4_a6_parent_message_exact"] is True

    tree_res = r1.verify_production_tree_immutability(_REPO_ROOT)
    assert tree_res["src_tree_immutable"] is True
    assert tree_res["configs_tree_immutable"] is True
    assert tree_res["production_tree_immutability"] is True

    auth_sci_res = r1.verify_authority_and_scientific_blob_immutability(_REPO_ROOT)
    assert auth_sci_res["d4_a4_authority_artifact_immutability"] is True
    assert auth_sci_res["d4_a5_scientific_artifact_immutability"] is True

    mapping_res = r1.verify_r1_mapping_artifacts_immutability(_REPO_ROOT)
    assert mapping_res["r1_mapping_artifacts_unchanged"] is True
