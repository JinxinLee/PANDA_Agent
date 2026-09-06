"""Focused deterministic unit tests for D4-A7 Validated-Subset Locator-Retirement Activation.

Covers all 18 requirements specified in Section 21 of the D4-A7 contract:
  1. frozen R1 machine authority is accepted;
  2. exact valid two-rule activation mapping passes;
  3. failure to clear one eligible rule's symbols fails;
  4. inserting structured_replacement: true fails;
  5. inserting redundant structured_replacement: false fails;
  6. changing trigger/repository/concept/paper hint fails;
  7. modifying model_factory_theory fails;
  8. modifying a third/unselected rule fails;
  9. modifying either Batch1 rule fails;
  10. production config loads through load_query_expansions;
  11. all required independent-origin witnesses remain;
  12. missing independent-origin witness fails;
  13. wrong A7 commit message fails the Git helper;
  14. wrong A7 parent fails;
  15. unauthorized eighth changed file fails;
  16. production src tree drift fails;
  17. an additional configs/ file change fails;
  18. modified R1 authority blob fails.
"""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from evaluation.scripts.d4_a7_validated_subset_locator_retirement_activation import (
    A7_COMMIT_MESSAGE,
    EXPECTED_A7_PATHS,
    R1_AUTHORITY_PATHS,
    R1_HEAD,
    VALIDATED_ELIGIBLE_RULES,
    load_r1_decision,
    load_yaml_config,
    validate_activation_mapping,
    verify_clean_worktree_and_index,
    verify_configs_changed_paths,
    verify_git_commit_identity,
    verify_git_cumulative_diff,
    verify_independent_origins,
    verify_production_schema,
    verify_production_tree_immutability,
    verify_r1_authority_blob_seal,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def r1_decision() -> dict[str, Any]:
    return load_r1_decision(PROJECT_ROOT)


@pytest.fixture
def parent_config() -> dict[str, Any]:
    cmd = ["git", "show", f"{R1_HEAD}:configs/query_expansions.yaml"]
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, encoding="utf-8", check=True)
    return yaml.safe_load(res.stdout)


@pytest.fixture
def activated_config() -> dict[str, Any]:
    return load_yaml_config(PROJECT_ROOT / "configs/query_expansions.yaml")


# 1. frozen R1 machine authority is accepted
def test_01_frozen_r1_machine_authority_accepted(r1_decision: dict[str, Any]) -> None:
    assert r1_decision["decision"] == "READY_FOR_VALIDATED_SUBSET_LOCATOR_RETIREMENT"
    per_rule = r1_decision["per_rule"]
    assert per_rule["effective_acceptance_pipeline"]["production_migration_eligibility"] == "MIGRATION_ELIGIBLE"
    assert per_rule["root_macro_usage"]["production_migration_eligibility"] == "MIGRATION_ELIGIBLE"
    assert per_rule["model_factory_theory"]["production_migration_eligibility"] == "HOLD"
    assert r1_decision["governance"]["full_batch_activation"] is False


# 2. exact valid two-rule activation mapping passes
def test_02_exact_valid_two_rule_activation_mapping_passes(
    parent_config: dict[str, Any],
    activated_config: dict[str, Any],
    r1_decision: dict[str, Any],
) -> None:
    res = validate_activation_mapping(parent_config, activated_config, r1_decision)
    assert res["is_valid"] is True
    assert res["errors"] == []
    assert res["changed_rule_ids"] == VALIDATED_ELIGIBLE_RULES
    assert res["changed_fields_by_rule"] == {
        "effective_acceptance_pipeline": ["symbols"],
        "root_macro_usage": ["symbols"],
    }


# 3. failure to clear one eligible rule's symbols fails
def test_03_failure_to_clear_one_eligible_rule_symbols_fails(
    parent_config: dict[str, Any],
    activated_config: dict[str, Any],
    r1_decision: dict[str, Any],
) -> None:
    mutated = copy.deepcopy(activated_config)
    for rule in mutated["rules"]:
        if rule["rule_id"] == "root_macro_usage":
            rule["symbols"] = ["Running/Macros.html"]
    res = validate_activation_mapping(parent_config, mutated, r1_decision)
    assert res["is_valid"] is False
    assert any("symbols" in e and "root_macro_usage" in e for e in res["errors"])


# 4. inserting structured_replacement: true fails
def test_04_inserting_structured_replacement_true_fails(
    parent_config: dict[str, Any],
    activated_config: dict[str, Any],
    r1_decision: dict[str, Any],
) -> None:
    mutated = copy.deepcopy(activated_config)
    for rule in mutated["rules"]:
        if rule["rule_id"] == "effective_acceptance_pipeline":
            rule["structured_replacement"] = True
    res = validate_activation_mapping(parent_config, mutated, r1_decision)
    assert res["is_valid"] is False
    assert any("structured_replacement" in e for e in res["errors"])


# 5. inserting redundant structured_replacement: false fails
def test_05_inserting_redundant_structured_replacement_false_fails(
    parent_config: dict[str, Any],
    activated_config: dict[str, Any],
    r1_decision: dict[str, Any],
) -> None:
    mutated = copy.deepcopy(activated_config)
    for rule in mutated["rules"]:
        if rule["rule_id"] == "effective_acceptance_pipeline":
            rule["structured_replacement"] = False
    res = validate_activation_mapping(parent_config, mutated, r1_decision)
    assert res["is_valid"] is False
    assert any("unnecessarily inserted structured_replacement" in e for e in res["errors"])


# 6. changing trigger/repository/concept/paper hint fails
@pytest.mark.parametrize(
    "field,new_val",
    [
        ("triggers", ["altered trigger"]),
        ("repositories", ["altered_repo"]),
        ("concepts", ["altered concept"]),
        ("paper_page_hints", {"li_2026": [999]}),
    ],
)
def test_06_changing_trigger_repository_concept_paper_hint_fails(
    parent_config: dict[str, Any],
    activated_config: dict[str, Any],
    r1_decision: dict[str, Any],
    field: str,
    new_val: Any,
) -> None:
    mutated = copy.deepcopy(activated_config)
    for rule in mutated["rules"]:
        if rule["rule_id"] == "effective_acceptance_pipeline":
            rule[field] = new_val
    res = validate_activation_mapping(parent_config, mutated, r1_decision)
    assert res["is_valid"] is False
    assert any(f"field {field} drifted" in e for e in res["errors"])


# 7. modifying model_factory_theory fails
def test_07_modifying_model_factory_theory_fails(
    parent_config: dict[str, Any],
    activated_config: dict[str, Any],
    r1_decision: dict[str, Any],
) -> None:
    mutated = copy.deepcopy(activated_config)
    for rule in mutated["rules"]:
        if rule["rule_id"] == "model_factory_theory":
            rule["symbols"] = []
    res = validate_activation_mapping(parent_config, mutated, r1_decision)
    assert res["is_valid"] is False
    assert any("Held rule model_factory_theory was modified" in e for e in res["errors"])


# 8. modifying a third/unselected rule fails
def test_08_modifying_third_unselected_rule_fails(
    parent_config: dict[str, Any],
    activated_config: dict[str, Any],
    r1_decision: dict[str, Any],
) -> None:
    mutated = copy.deepcopy(activated_config)
    for rule in mutated["rules"]:
        if rule["rule_id"] == "lmd_fit_data_chain":
            rule["symbols"] = []
    res = validate_activation_mapping(parent_config, mutated, r1_decision)
    assert res["is_valid"] is False
    assert any("Unselected rule lmd_fit_data_chain was modified" in e for e in res["errors"])


# 9. modifying either Batch1 rule fails
@pytest.mark.parametrize("rule_id", ["event_poca_handoff", "restgas_profile_workflow"])
def test_09_modifying_either_batch1_rule_fails(
    parent_config: dict[str, Any],
    activated_config: dict[str, Any],
    r1_decision: dict[str, Any],
    rule_id: str,
) -> None:
    mutated = copy.deepcopy(activated_config)
    for rule in mutated["rules"]:
        if rule["rule_id"] == rule_id:
            rule["structured_replacement"] = False
    res = validate_activation_mapping(parent_config, mutated, r1_decision)
    assert res["is_valid"] is False
    assert any(rule_id in e for e in res["errors"])


# 10. production config loads through load_query_expansions
def test_10_production_config_loads_through_load_query_expansions() -> None:
    res = verify_production_schema(PROJECT_ROOT)
    assert res["schema_valid"] is True
    assert res["rule_count"] == 54
    assert res["error"] is None


# 11. all required independent-origin witnesses remain
def test_11_all_required_independent_origin_witnesses_remain(activated_config: dict[str, Any]) -> None:
    res = verify_independent_origins(activated_config)
    assert res["all_independent_origins_preserved"] is True
    witnesses = res["preservation_witnesses"]
    assert witnesses["prod_sim_hvmaps_in_independent_rule"] is True
    assert witnesses["lmd_acceptance_in_independent_rule"] is True
    assert witnesses["model_factory_in_held_rule"] is True
    assert witnesses["model_factory_in_independent_rule"] is True
    assert witnesses["running_macros_in_independent_rule"] is True
    assert witnesses["master_run_sim_in_independent_rule"] is True


# 12. missing independent-origin witness fails
def test_12_missing_independent_origin_witness_fails(activated_config: dict[str, Any]) -> None:
    mutated = copy.deepcopy(activated_config)
    for rule in mutated["rules"]:
        if rule["rule_id"] == "reconstructed_profile_to_acceptance":
            rule["symbols"] = []
    res = verify_independent_origins(mutated)
    assert res["all_independent_origins_preserved"] is False
    assert res["preservation_witnesses"]["prod_sim_hvmaps_in_independent_rule"] is False


# 13. wrong A7 commit message fails the Git helper
def test_13_wrong_a7_commit_message_fails_git_helper() -> None:
    res = verify_git_commit_identity(
        PROJECT_ROOT,
        _override_message="Wrong commit message",
        _override_parent=R1_HEAD,
    )
    assert res["a7_commit_message_exact"] is False
    assert res["all_valid"] is False


# 14. wrong A7 parent fails
def test_14_wrong_a7_parent_fails_git_helper() -> None:
    res = verify_git_commit_identity(
        PROJECT_ROOT,
        _override_message=A7_COMMIT_MESSAGE,
        _override_parent="0000000000000000000000000000000000000000",
    )
    assert res["a7_parent_exact"] is False
    assert res["all_valid"] is False


# 15. unauthorized eighth changed file fails
def test_15_unauthorized_eighth_changed_file_fails() -> None:
    res = verify_git_cumulative_diff(
        PROJECT_ROOT,
        _override_diff_paths=EXPECTED_A7_PATHS + ["unauthorized_eighth_file.txt"],
    )
    assert res["exact_match"] is False
    assert "unauthorized_eighth_file.txt" in res["extra_paths"]


# 16. production src tree drift fails
def test_16_production_src_tree_drift_fails() -> None:
    res = verify_production_tree_immutability(
        PROJECT_ROOT,
        _override_src_tree=("hash_head_modified", "hash_base_original"),
    )
    assert res["src_tree_immutable"] is False


# 17. an additional configs/ file change fails
def test_17_additional_configs_file_change_fails() -> None:
    res = verify_configs_changed_paths(
        PROJECT_ROOT,
        _override_configs_paths=[
            "configs/query_expansions.yaml",
            "configs/another_config.yaml",
        ],
    )
    assert res["configs_changed_paths_exact"] is False


# 18. modified R1 authority blob fails
def test_18_modified_r1_authority_blob_fails() -> None:
    overrides = {p: True for p in R1_AUTHORITY_PATHS}
    overrides["evaluation/d4_a6_r1_decision.json"] = False
    res = verify_r1_authority_blob_seal(
        PROJECT_ROOT,
        _override_matches=overrides,
    )
    assert res["r1_authority_artifact_seal"] is False
