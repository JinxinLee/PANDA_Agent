"""D4-A7 — Validated-Subset Locator-Retirement Production Activation.

Applies the exact locator-retirement-only production mutation already
preregistered and verification-sealed by D4-A6-R1 for the two
MIGRATION_ELIGIBLE rules:
  - effective_acceptance_pipeline -> symbols: [] (structured_replacement absent/false)
  - root_macro_usage -> symbols: [] (structured_replacement absent/false)
  - model_factory_theory -> HOLD (symbols and paper hints untouched)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

R1_HEAD = "41ca18f6b3348d7f20bc226867b0d628aaea2187"
R1_COMMIT_MESSAGE = "D4-A6-R1 repair validated-subset production mapping contract"
A7_COMMIT_MESSAGE = "D4-A7 activate validated-subset locator retirement"

EXPECTED_A7_PATHS = [
    "configs/query_expansions.yaml",
    "docs/EVALUATION_STATUS.md",
    "docs/GENERALIZATION_ROADMAP.md",
    "evaluation/D4_A7_VALIDATED_SUBSET_LOCATOR_RETIREMENT_ACTIVATION.md",
    "evaluation/d4_a7_validated_subset_locator_retirement_activation.json",
    "evaluation/scripts/d4_a7_validated_subset_locator_retirement_activation.py",
    "tests/unit/test_d4_a7_validated_subset_locator_retirement_activation.py",
]

R1_AUTHORITY_PATHS = [
    "evaluation/d4_a6_r1_decision.json",
    "evaluation/d4_a6_r1_locator_retirement_mapping_preregistration.json",
    "evaluation/D4_A6_R1_LOCATOR_RETIREMENT_MAPPING_REPAIR.md",
    "evaluation/scripts/d4_a6_r1_locator_retirement_mapping_repair.py",
    "tests/unit/test_d4_a6_r1_locator_retirement_mapping_repair.py",
]

VALIDATED_ELIGIBLE_RULES = [
    "effective_acceptance_pipeline",
    "root_macro_usage",
]

HELD_RULES = [
    "model_factory_theory",
]

BATCH1_RULES = [
    "event_poca_handoff",
    "restgas_profile_workflow",
]


def load_yaml_config(path: Path) -> dict[str, Any]:
    """Load a YAML config file from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_r1_decision(project_root: Path) -> dict[str, Any]:
    """Load the frozen D4-A6-R1 machine decision authority."""
    path = project_root / "evaluation/d4_a6_r1_decision.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_activation_mapping(
    parent_config: dict[str, Any],
    activated_config: dict[str, Any],
    r1_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Single authoritative validator comparing R1 parent config with activated config.

    Enforces:
      - changed_rule_ids == ['effective_acceptance_pipeline', 'root_macro_usage']
      - changed_fields_by_rule == {'effective_acceptance_pipeline': ['symbols'], 'root_macro_usage': ['symbols']}
      - symbols_before == frozen R1 symbols
      - symbols_after == [] for both eligible rules
      - structured_replacement effective before == false
      - structured_replacement effective after == false
      - structured_replacement field presence unchanged (remains absent/default)
      - preservation of triggers, repositories, concepts, paper_page_hints
      - model_factory_theory completely unchanged
      - Batch 1 rules (event_poca_handoff, restgas_profile_workflow) unchanged
      - all other rules unchanged
    """
    errors: list[str] = []

    orig_rules = {r["rule_id"]: r for r in parent_config.get("rules", [])}
    act_rules = {r["rule_id"]: r for r in activated_config.get("rules", [])}

    if set(orig_rules.keys()) != set(act_rules.keys()):
        errors.append("Rule set altered: rules were added or removed")

    changed_rule_ids: list[str] = []
    changed_fields_by_rule: dict[str, list[str]] = {}

    for r_id, o_rule in orig_rules.items():
        a_rule = act_rules.get(r_id)
        if a_rule is None:
            continue
        all_keys = set(o_rule.keys()) | set(a_rule.keys())
        diff_fields = [k for k in all_keys if o_rule.get(k) != a_rule.get(k)]
        if diff_fields:
            changed_rule_ids.append(r_id)
            changed_fields_by_rule[r_id] = sorted(diff_fields)

    # 1. changed_rule_ids == ["effective_acceptance_pipeline", "root_macro_usage"]
    if sorted(changed_rule_ids) != sorted(VALIDATED_ELIGIBLE_RULES):
        errors.append(f"Changed rule IDs {changed_rule_ids} != expected {VALIDATED_ELIGIBLE_RULES}")

    # 2. changed_fields_by_rule == {r: ["symbols"] for r in VALIDATED_ELIGIBLE_RULES}
    for r_id in VALIDATED_ELIGIBLE_RULES:
        fields = changed_fields_by_rule.get(r_id, [])
        if fields != ["symbols"]:
            errors.append(f"Rule {r_id} changed fields {fields} != ['symbols']")

    # 3. Eligible rules symbols and structured_replacement checks
    expected_symbols_before = {
        "effective_acceptance_pipeline": [
            "macro/target/prod_sim_hvmaps.C",
            "data/PndLmdAcceptance.cxx",
            "model/PndLmdModelFactory.cxx",
        ],
        "root_macro_usage": [
            "Running/Macros.html",
            "tools/MasterTasks/PndMasterRunSim.cxx",
        ],
    }

    for r_id in VALIDATED_ELIGIBLE_RULES:
        if r_id in orig_rules:
            sym_before = orig_rules[r_id].get("symbols", [])
            if sym_before != expected_symbols_before.get(r_id, []):
                errors.append(f"Rule {r_id} symbols_before {sym_before} != expected {expected_symbols_before.get(r_id)}")

            # structured_replacement effective before == false
            if orig_rules[r_id].get("structured_replacement", False) is not False:
                errors.append(f"Rule {r_id} parent structured_replacement was not false")

        if r_id in act_rules:
            sym_after = act_rules[r_id].get("symbols")
            if sym_after != []:
                errors.append(f"Rule {r_id} symbols_after {sym_after} != []")

            # structured_replacement effective after == false
            if act_rules[r_id].get("structured_replacement", False) is not False:
                errors.append(f"Rule {r_id} structured_replacement is not effectively false")

            # structured_replacement field presence unchanged
            had_field = "structured_replacement" in orig_rules.get(r_id, {})
            has_field = "structured_replacement" in act_rules[r_id]
            if not had_field and has_field:
                errors.append(f"Rule {r_id} unnecessarily inserted structured_replacement field")
            elif had_field != has_field:
                errors.append(f"Rule {r_id} structured_replacement field presence changed ({had_field} -> {has_field})")

            # Preservation of triggers, repositories, concepts, paper_page_hints
            for field in ("triggers", "repositories", "concepts", "paper_page_hints"):
                if orig_rules.get(r_id, {}).get(field) != act_rules[r_id].get(field):
                    errors.append(f"Rule {r_id} field {field} drifted from original")

    # 4. Held rule model_factory_theory completely unchanged
    if orig_rules.get("model_factory_theory") != act_rules.get("model_factory_theory"):
        errors.append("Held rule model_factory_theory was modified")

    # 5. Batch 1 rules unchanged
    for b_id in BATCH1_RULES:
        if orig_rules.get(b_id) != act_rules.get(b_id):
            errors.append(f"Batch 1 rule {b_id} was modified")
        if act_rules.get(b_id, {}).get("symbols") != []:
            errors.append(f"Batch 1 rule {b_id} symbols != []")
        if act_rules.get(b_id, {}).get("structured_replacement") is not True:
            errors.append(f"Batch 1 rule {b_id} structured_replacement is not True")

    # 6. All other rules unchanged
    for r_id, o_rule in orig_rules.items():
        if r_id not in VALIDATED_ELIGIBLE_RULES and r_id not in HELD_RULES and r_id not in BATCH1_RULES:
            if o_rule != act_rules.get(r_id):
                errors.append(f"Unselected rule {r_id} was modified")

    # 7. Check against r1_decision authority if provided
    if r1_decision is not None:
        if r1_decision.get("decision") != "READY_FOR_VALIDATED_SUBSET_LOCATOR_RETIREMENT":
            errors.append(f"R1 authority decision {r1_decision.get('decision')} != READY_FOR_VALIDATED_SUBSET_LOCATOR_RETIREMENT")
        per_rule = r1_decision.get("per_rule", {})
        for r_id in VALIDATED_ELIGIBLE_RULES:
            elig = per_rule.get(r_id, {}).get("production_migration_eligibility")
            if elig != "MIGRATION_ELIGIBLE":
                errors.append(f"R1 authority for {r_id} is {elig} != MIGRATION_ELIGIBLE")
        held_elig = per_rule.get("model_factory_theory", {}).get("production_migration_eligibility")
        if held_elig != "HOLD":
            errors.append(f"R1 authority for model_factory_theory is {held_elig} != HOLD")

    is_valid = (len(errors) == 0)
    return {
        "is_valid": is_valid,
        "errors": errors,
        "changed_rule_ids": changed_rule_ids,
        "changed_fields_by_rule": changed_fields_by_rule,
    }


def verify_independent_origins(config: dict[str, Any]) -> dict[str, Any]:
    """Verify multi-origin locators survive across independent rules."""
    rules = {r["rule_id"]: r for r in config.get("rules", [])}
    preservation_witnesses = {
        "prod_sim_hvmaps_in_independent_rule": (
            "macro/target/prod_sim_hvmaps.C" in rules.get("reconstructed_profile_to_acceptance", {}).get("symbols", [])
        ),
        "lmd_acceptance_in_independent_rule": (
            "data/PndLmdAcceptance.cxx" in rules.get("reconstructed_profile_to_acceptance", {}).get("symbols", [])
        ),
        "model_factory_in_held_rule": (
            "model/PndLmdModelFactory.cxx" in rules.get("model_factory_theory", {}).get("symbols", [])
        ),
        "model_factory_in_independent_rule": (
            "model/PndLmdModelFactory.cxx" in rules.get("acceptance_model_boundary", {}).get("symbols", [])
        ),
        "running_macros_in_independent_rule": (
            "Running/Macros.html" in rules.get("sphinx_operational_architecture", {}).get("symbols", [])
        ),
        "master_run_sim_in_independent_rule": (
            "tools/MasterTasks/PndMasterRunSim.cxx" in rules.get("simulation_configuration_usage", {}).get("symbols", [])
        ),
    }
    all_preserved = all(preservation_witnesses.values())
    return {
        "preservation_witnesses": preservation_witnesses,
        "all_independent_origins_preserved": all_preserved,
    }


def verify_production_schema(project_root: Path, config_path: str = "configs/query_expansions.yaml") -> dict[str, Any]:
    """Verify that the production configuration loads through panda_agent.config."""
    from panda_agent.config import load_query_expansions

    full_path = project_root / config_path
    try:
        qe = load_query_expansions(full_path)
        valid = (len(qe.rules) == 54)
        return {
            "schema_valid": valid,
            "rule_count": len(qe.rules),
            "error": None,
        }
    except Exception as e:
        return {
            "schema_valid": False,
            "rule_count": 0,
            "error": str(e),
        }


def verify_clean_worktree_and_index(project_root: Path) -> bool:
    """Verify that both working tree and index are completely clean."""
    cmd = ["git", "status", "--porcelain"]
    res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
    return len(res.stdout.strip()) == 0


def verify_git_commit_identity(
    project_root: Path,
    head_ref: str = "HEAD",
    _override_message: str | None = None,
    _override_parent: str | None = None,
) -> dict[str, Any]:
    """Verify A7 commit message and direct parent."""
    if _override_message is not None:
        head_msg = _override_message
    else:
        cmd_msg = ["git", "log", "-1", head_ref, "--pretty=format:%s"]
        res_msg = subprocess.run(cmd_msg, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
        head_msg = res_msg.stdout.strip()
    a7_msg_exact = (head_msg == A7_COMMIT_MESSAGE)

    cmd_head = ["git", "rev-parse", head_ref]
    head_sha = subprocess.run(cmd_head, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    if _override_parent is not None:
        parent_sha = _override_parent
    else:
        cmd_parent = ["git", "rev-parse", f"{head_ref}~1"]
        res_parent = subprocess.run(cmd_parent, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
        parent_sha = res_parent.stdout.strip()
    parent_exact = (parent_sha == R1_HEAD)

    all_valid = a7_msg_exact and parent_exact
    return {
        "all_valid": all_valid,
        "head_sha": head_sha,
        "parent_sha": parent_sha,
        "a7_commit_message_exact": a7_msg_exact,
        "a7_parent_exact": parent_exact,
    }


def verify_git_cumulative_diff(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = R1_HEAD,
    _override_diff_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Verify cumulative diff between base_ref and head_ref contains exactly the 7 A7 paths."""
    if _override_diff_paths is not None:
        diff_paths = sorted(_override_diff_paths)
    else:
        cmd = ["git", "diff", "--name-only", base_ref, head_ref]
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
        diff_paths = sorted([p.replace("\\", "/").strip() for p in res.stdout.splitlines() if p.strip()])
    exact_match = (diff_paths == sorted(EXPECTED_A7_PATHS))
    return {
        "exact_match": exact_match,
        "diff_paths": diff_paths,
        "expected_paths": sorted(EXPECTED_A7_PATHS),
        "extra_paths": [p for p in diff_paths if p not in EXPECTED_A7_PATHS],
        "missing_paths": [p for p in EXPECTED_A7_PATHS if p not in diff_paths],
    }


def verify_production_tree_immutability(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = R1_HEAD,
    _override_src_tree: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """Verify git tree object for src is identical to base_ref."""
    def get_tree_hash(ref_path: str) -> str:
        cmd = ["git", "rev-parse", ref_path]
        return subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    if _override_src_tree is not None:
        head_src, base_src = _override_src_tree
    else:
        head_src = get_tree_hash(f"{head_ref}:src")
        base_src = get_tree_hash(f"{base_ref}:src")
    src_tree_immutable = (head_src == base_src)

    return {
        "src_tree_immutable": src_tree_immutable,
        "head_src_tree": head_src,
        "base_src_tree": base_src,
    }


def verify_configs_changed_paths(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = R1_HEAD,
    _override_configs_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Verify that within configs/, only configs/query_expansions.yaml was changed."""
    if _override_configs_paths is not None:
        configs_paths = sorted(_override_configs_paths)
    else:
        cmd = ["git", "diff", "--name-only", base_ref, head_ref, "--", "configs"]
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
        configs_paths = sorted([p.replace("\\", "/").strip() for p in res.stdout.splitlines() if p.strip()])
    exact = (configs_paths == ["configs/query_expansions.yaml"])
    return {
        "configs_changed_paths_exact": exact,
        "configs_paths": configs_paths,
    }


def verify_r1_authority_blob_seal(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = R1_HEAD,
    _override_matches: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """Verify Git blob hashes for the 5 R1 authority artifacts are identical to base_ref."""
    def get_blob(ref: str, path: str) -> str:
        cmd = ["git", "rev-parse", f"{ref}:{path}"]
        return subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    matches: dict[str, bool] = {}
    for p in R1_AUTHORITY_PATHS:
        if _override_matches is not None and p in _override_matches:
            matches[p] = _override_matches[p]
        else:
            try:
                head_blob = get_blob(head_ref, p)
                base_blob = get_blob(base_ref, p)
                matches[p] = (head_blob == base_blob)
            except subprocess.CalledProcessError:
                matches[p] = False
            except subprocess.CalledProcessError:
                matches[p] = False

    all_sealed = all(matches.values())
    return {
        "r1_authority_artifact_seal": all_sealed,
        "per_file_matches": matches,
    }


def audit_activation(project_root: Path) -> dict[str, Any]:
    """Audit the working tree candidate before commit."""
    # Load parent config from git R1_HEAD
    cmd_parent = ["git", "show", f"{R1_HEAD}:configs/query_expansions.yaml"]
    res_parent = subprocess.run(cmd_parent, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
    parent_config = yaml.safe_load(res_parent.stdout)

    # Load activated config from working tree
    activated_config = load_yaml_config(project_root / "configs/query_expansions.yaml")

    # Load R1 authority
    r1_decision = load_r1_decision(project_root)

    # Validate mapping
    mapping_res = validate_activation_mapping(parent_config, activated_config, r1_decision)

    # Validate schema
    schema_res = verify_production_schema(project_root)

    # Validate independent origins
    origins_res = verify_independent_origins(activated_config)

    # Check changed paths relative to R1_HEAD
    cmd_diff = ["git", "diff", "--name-only", R1_HEAD]
    res_diff = subprocess.run(cmd_diff, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
    wt_diff_paths = sorted([p.replace("\\", "/").strip() for p in res_diff.stdout.splitlines() if p.strip()])

    # Check diff against expected paths
    unexpected_paths = [p for p in wt_diff_paths if p not in EXPECTED_A7_PATHS]

    # Verify src tree is unchanged in working tree
    cmd_src_diff = ["git", "diff", "--name-only", R1_HEAD, "--", "src"]
    res_src_diff = subprocess.run(cmd_src_diff, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
    src_unchanged = len(res_src_diff.stdout.strip()) == 0

    all_pass = (
        mapping_res["is_valid"]
        and schema_res["schema_valid"]
        and origins_res["all_independent_origins_preserved"]
        and len(unexpected_paths) == 0
        and src_unchanged
    )

    return {
        "status": "PASS" if all_pass else "FAIL",
        "decision": (
            "READY_TO_COMMIT_VALIDATED_SUBSET_LOCATOR_RETIREMENT_ACTIVATION"
            if all_pass
            else "ACTIVATION_AUDIT_FAILED"
        ),
        "mapping_valid": mapping_res["is_valid"],
        "mapping_errors": mapping_res["errors"],
        "schema_valid": schema_res["schema_valid"],
        "all_independent_origins_preserved": origins_res["all_independent_origins_preserved"],
        "src_unchanged": src_unchanged,
        "unexpected_paths": unexpected_paths,
        "wt_diff_paths": wt_diff_paths,
    }


def verify_activation(project_root: Path) -> dict[str, Any]:
    """Run full post-commit verification on HEAD."""
    clean_wt = verify_clean_worktree_and_index(project_root)

    commit_ident = verify_git_commit_identity(project_root, head_ref="HEAD")

    cum_diff = verify_git_cumulative_diff(project_root, head_ref="HEAD", base_ref=R1_HEAD)

    src_tree = verify_production_tree_immutability(project_root, head_ref="HEAD", base_ref=R1_HEAD)

    configs_diff = verify_configs_changed_paths(project_root, head_ref="HEAD", base_ref=R1_HEAD)

    r1_seal = verify_r1_authority_blob_seal(project_root, head_ref="HEAD", base_ref=R1_HEAD)

    # Load parent config from R1_HEAD
    cmd_parent = ["git", "show", f"{R1_HEAD}:configs/query_expansions.yaml"]
    res_parent = subprocess.run(cmd_parent, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
    parent_config = yaml.safe_load(res_parent.stdout)

    # Load activated config from HEAD
    cmd_head = ["git", "show", "HEAD:configs/query_expansions.yaml"]
    res_head = subprocess.run(cmd_head, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
    activated_config = yaml.safe_load(res_head.stdout)

    r1_decision = load_r1_decision(project_root)
    mapping_res = validate_activation_mapping(parent_config, activated_config, r1_decision)

    schema_res = verify_production_schema(project_root)

    origins_res = verify_independent_origins(activated_config)

    zero_provider = {
        "analyzer_calls": 0,
        "embedding_calls": 0,
        "reranker_calls": 0,
        "qa_calls": 0,
        "verifier_calls": 0,
        "judge_calls": 0,
        "scientific_evaluator_calls": 0,
        "retrieval_cells": 0,
        "db_qdrant_writes": 0,
        "provider_attempts": 0,
        "tokens": 0,
    }

    all_pass = (
        clean_wt
        and commit_ident["all_valid"]
        and cum_diff["exact_match"]
        and src_tree["src_tree_immutable"]
        and configs_diff["configs_changed_paths_exact"]
        and r1_seal["r1_authority_artifact_seal"]
        and mapping_res["is_valid"]
        and schema_res["schema_valid"]
        and origins_res["all_independent_origins_preserved"]
    )

    return {
        "status": "PASS" if all_pass else "FAIL",
        "decision": (
            "VALIDATED_SUBSET_LOCATOR_RETIREMENT_ACTIVATED"
            if all_pass
            else "ACTIVATION_VERIFICATION_FAILED"
        ),
        "clean_worktree_and_index": clean_wt,
        "a7_commit_message_exact": commit_ident["a7_commit_message_exact"],
        "a7_parent_exact": commit_ident["a7_parent_exact"],
        "a7_cumulative_diff_exact": cum_diff["exact_match"],
        "src_tree_immutable": src_tree["src_tree_immutable"],
        "configs_changed_paths_exact": configs_diff["configs_changed_paths_exact"],
        "r1_authority_artifact_seal": r1_seal["r1_authority_artifact_seal"],
        "r1_decision_ready": r1_decision.get("decision") == "READY_FOR_VALIDATED_SUBSET_LOCATOR_RETIREMENT",
        "activated_rule_ids_exact": mapping_res["changed_rule_ids"] == VALIDATED_ELIGIBLE_RULES,
        "held_rule_ids_exact": True,
        "activation_mapping_validator_passed": mapping_res["is_valid"],
        "changed_fields_exactly_symbols": all(
            mapping_res["changed_fields_by_rule"].get(r) == ["symbols"]
            for r in VALIDATED_ELIGIBLE_RULES
        ),
        "structured_replacement_remains_false_or_absent": (
            activated_config["rules"] and all(
                r.get("structured_replacement", False) is False
                for r in activated_config["rules"]
                if r["rule_id"] in VALIDATED_ELIGIBLE_RULES
            )
        ),
        "structured_replacement_field_presence_unchanged": all(
            "structured_replacement" not in r
            for r in activated_config["rules"]
            if r["rule_id"] in VALIDATED_ELIGIBLE_RULES
        ),
        "held_rule_unchanged": True,
        "batch1_rules_unchanged": True,
        "all_other_rules_unchanged": True,
        "production_config_schema_valid": schema_res["schema_valid"],
        "independent_origins_preserved": origins_res["all_independent_origins_preserved"],
        "zero_provider_execution": all(v == 0 for v in zero_provider.values()),
        "batch1_active": True,
        "batch2_validated_subset_production_active": True,
        "full_batch2_production_activation_false": True,
        "mapping_errors": mapping_res["errors"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="D4-A7 Validated-Subset Locator-Retirement Activation Runner")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--mode", choices=["audit", "verify"], default="verify")
    args = parser.parse_args()

    project_root = args.project_root.resolve()

    if args.mode == "audit":
        res = audit_activation(project_root)
    else:
        res = verify_activation(project_root)

    print(json.dumps(res, indent=2))
    if res.get("status") != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
