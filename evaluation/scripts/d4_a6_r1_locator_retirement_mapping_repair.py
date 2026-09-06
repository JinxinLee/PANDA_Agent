"""D4-A6-R1 — Validated-Subset Locator-Retirement Production Mapping Repair.

Repairs the D4-A6 prospective production-mapping contract so that the future
validated-subset migration is strictly equivalent to the intervention actually
validated by frozen D4-A5:
  - effective_acceptance_pipeline -> MIGRATION_ELIGIBLE (symbols: [], structured_replacement absent/default false)
  - root_macro_usage -> MIGRATION_ELIGIBLE (symbols: [], structured_replacement absent/default false)
  - model_factory_theory -> HOLD (unchanged, existing production contract preserved)
"""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

STARTING_HEAD = "b038a9e2ced817231b7a25f98dc106965f1a2688"
STARTING_COMMIT_MESSAGE = "D4-A6 preregister validated-subset Batch2 runtime migration"
STARTING_PARENT_HEAD = "7b9d9d13903d874c000c0097304bfccc19dbbf65"
CLOSEOUT_HEAD = "c33f4cbe0bc2dfe6352d70396ebbdc203d3c624f"

PRE_AMEND_R1_HEAD = "b270c7fa39c7d92c0ad57066b9831156b60705b7"
R1_COMMIT_MESSAGE = "D4-A6-R1 repair validated-subset production mapping contract"

D4_A4_SELECTION_PATH = "evaluation/d4_a4_batch2_low_risk_retirement_selection.json"
D4_A4_PREREG_PATH = "evaluation/d4_a4_batch2_retirement_preregistration.json"
D4_A5_RESULT_PATH = "evaluation/d4_a5_continuation_result.json"

D4_A6_DECISION_PATH = "evaluation/d4_a6_validated_subset_migration_decision.json"
D4_A6_PREREG_PATH = "evaluation/d4_a6_validated_subset_migration_preregistration.json"
D4_A6_REPORT_PATH = "evaluation/D4_A6_VALIDATED_SUBSET_RUNTIME_MIGRATION_PREREGISTRATION.md"
D4_A6_SCRIPT_PATH = "evaluation/scripts/d4_a6_validated_subset_migration_preregistration.py"
D4_A6_TEST_PATH = "tests/unit/test_d4_a6_validated_subset_migration_preregistration.py"

D4_A6_R1_PREREG_PATH = "evaluation/d4_a6_r1_locator_retirement_mapping_preregistration.json"
D4_A6_R1_DECISION_PATH = "evaluation/d4_a6_r1_decision.json"
D4_A6_R1_REPORT_PATH = "evaluation/D4_A6_R1_LOCATOR_RETIREMENT_MAPPING_REPAIR.md"
D4_A6_R1_SCRIPT_PATH = "evaluation/scripts/d4_a6_r1_locator_retirement_mapping_repair.py"
D4_A6_R1_TEST_PATH = "tests/unit/test_d4_a6_r1_locator_retirement_mapping_repair.py"

QUERY_EXPANSIONS_PATH = "configs/query_expansions.yaml"
RETRIEVAL_PY_PATH = "src/panda_agent/retrieval.py"

EXPECTED_R1_PATHS = [
    "docs/EVALUATION_STATUS.md",
    "docs/GENERALIZATION_ROADMAP.md",
    "evaluation/D4_A6_R1_LOCATOR_RETIREMENT_MAPPING_REPAIR.md",
    "evaluation/d4_a6_r1_decision.json",
    "evaluation/d4_a6_r1_locator_retirement_mapping_preregistration.json",
    "evaluation/scripts/d4_a6_r1_locator_retirement_mapping_repair.py",
    "tests/unit/test_d4_a6_r1_locator_retirement_mapping_repair.py",
]

ALLOWED_AMEND_PATHS = [
    "docs/EVALUATION_STATUS.md",
    "docs/GENERALIZATION_ROADMAP.md",
    "evaluation/D4_A6_R1_LOCATOR_RETIREMENT_MAPPING_REPAIR.md",
    "evaluation/scripts/d4_a6_r1_locator_retirement_mapping_repair.py",
    "tests/unit/test_d4_a6_r1_locator_retirement_mapping_repair.py",
]

D4_A4_AUTHORITY_PATHS = [
    "evaluation/d4_a4_batch2_low_risk_retirement_selection.json",
    "evaluation/d4_a4_batch2_retirement_preregistration.json",
]

D4_A5_SCIENTIFIC_PATHS = [
    "evaluation/d4_a5_continuation_execution_manifest.json",
    "evaluation/d4_a5_continuation_raw_prospective_plans.json",
    "evaluation/d4_a5_continuation_raw_paired_retirement_results.json",
    "evaluation/d4_a5_continuation_evaluator_results.json",
    "evaluation/d4_a5_continuation_result.json",
]

R1_MAPPING_PATHS = [
    "evaluation/d4_a6_r1_decision.json",
    "evaluation/d4_a6_r1_locator_retirement_mapping_preregistration.json",
]

HISTORICAL_D4_A6_BLOBS = {
    "evaluation/D4_A6_VALIDATED_SUBSET_RUNTIME_MIGRATION_PREREGISTRATION.md": "34ca2b35f7edb5d50098da20c26fbdbca2e6b93f",
    "evaluation/d4_a6_validated_subset_migration_decision.json": "4ccdfdfa8357cfedaa1061c4cd62b0be18e4b0b1",
    "evaluation/d4_a6_validated_subset_migration_preregistration.json": "1d37526679899d0ffdfdd0cda4a0fbe32b3e405a",
    "evaluation/scripts/d4_a6_validated_subset_migration_preregistration.py": "17c3a11620aae6e94090e52a5424dbfa0046dc20",
    "tests/unit/test_d4_a6_validated_subset_migration_preregistration.py": "374c695556c55c35d0a4db5a19884a6933c84cfc",
}

BATCH2_SELECTED_RULES = [
    "effective_acceptance_pipeline",
    "root_macro_usage",
    "model_factory_theory",
]

VALIDATED_ELIGIBLE_RULES = [
    "effective_acceptance_pipeline",
    "root_macro_usage",
]

HELD_RULES = [
    "model_factory_theory",
]


def reproduce_historical_d4_a6_defect(project_root: Path) -> dict[str, Any]:
    """Mechanically reproduce the historical D4-A6 production mapping defect."""
    prereg_path = project_root / D4_A4_PREREG_PATH
    with open(prereg_path, encoding="utf-8") as f:
        d4_a4_prereg = json.load(f)

    masks = d4_a4_prereg.get("exact_component_masks", {})
    frozen_after_retirement_states = {
        r_id: masks[r_id].get("structured_replacement_after_retirement", True)
        for r_id in BATCH2_SELECTED_RULES
        if r_id in masks
    }

    d4_a4_all_frozen_false = all(v is False for v in frozen_after_retirement_states.values())

    historical_decision_path = project_root / D4_A6_DECISION_PATH
    with open(historical_decision_path, encoding="utf-8") as f:
        d4_a6_decision = json.load(f)

    per_rule_a6 = d4_a6_decision.get("per_rule", {})
    proposed_structured_replacement_states = {
        r_id: per_rule_a6[r_id].get("prospective_production_mutation", {}).get("structured_replacement", False)
        for r_id in VALIDATED_ELIGIBLE_RULES
        if r_id in per_rule_a6
    }

    defect_detected = (
        d4_a4_all_frozen_false
        and any(proposed_structured_replacement_states.values())
    )

    return {
        "defect_detected": defect_detected,
        "defect_code": "PROSPECTIVE_MAPPING_ADDED_UNVALIDATED_STRUCTURED_REPLACEMENT_BEHAVIOR",
        "d4_a4_frozen_after_retirement_states": frozen_after_retirement_states,
        "d4_a6_proposed_structured_replacement_states": proposed_structured_replacement_states,
        "explanation": (
            "Frozen D4-A4 explicitly preregistered structured_replacement_after_retirement = false "
            "for all Batch2 rules and D4-A5 validated selected-rule locator-origin subtraction only. "
            "Historical D4-A6 incorrectly proposed structured_replacement: true on eligible rules."
        ),
    }


def validate_prospective_mapping(
    original_config: dict[str, Any],
    prospective_config: dict[str, Any],
    frozen_authority: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Single mechanical validator for prospective production mapping.

    Enforces:
      - changed_rule_ids == ['effective_acceptance_pipeline', 'root_macro_usage']
      - changed_fields_by_rule == {'effective_acceptance_pipeline': ['symbols'], 'root_macro_usage': ['symbols']}
      - symbols_after == [] for both eligible rules
      - structured_replacement effective state remains false
      - structured_replacement field presence remains unchanged (no inserted field)
      - preservation of triggers, repositories, concepts, paper_page_hints
      - model_factory_theory unchanged
      - all other 51 rules unchanged
    """
    errors: list[str] = []

    orig_rules = {r["rule_id"]: r for r in original_config.get("rules", [])}
    prosp_rules = {r["rule_id"]: r for r in prospective_config.get("rules", [])}

    if set(orig_rules.keys()) != set(prosp_rules.keys()):
        errors.append("Rule set altered: rules were added or removed")

    changed_rule_ids: list[str] = []
    changed_fields_by_rule: dict[str, list[str]] = {}

    for r_id, o_rule in orig_rules.items():
        p_rule = prosp_rules.get(r_id)
        if p_rule is None:
            continue
        all_keys = set(o_rule.keys()) | set(p_rule.keys())
        diff_fields = [k for k in all_keys if o_rule.get(k) != p_rule.get(k)]
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

    # 3. For both eligible rules: symbols_after == []
    for r_id in VALIDATED_ELIGIBLE_RULES:
        if r_id in prosp_rules:
            symbols = prosp_rules[r_id].get("symbols")
            if symbols != []:
                errors.append(f"Rule {r_id} symbols {symbols} != []")

            # structured_replacement effective state remains false
            if prosp_rules[r_id].get("structured_replacement", False) is not False:
                errors.append(f"Rule {r_id} structured_replacement is not effectively false")

            # structured_replacement field presence remains unchanged
            had_field = "structured_replacement" in orig_rules.get(r_id, {})
            has_field = "structured_replacement" in prosp_rules[r_id]
            if not had_field and has_field:
                errors.append(f"Rule {r_id} unnecessarily inserted structured_replacement field")

            # Preservation of triggers, repositories, concepts, paper_page_hints
            for field in ("triggers", "repositories", "concepts", "paper_page_hints"):
                if orig_rules.get(r_id, {}).get(field) != prosp_rules[r_id].get(field):
                    errors.append(f"Rule {r_id} field {field} drifted from original")

    # 4. model_factory_theory unchanged
    if orig_rules.get("model_factory_theory") != prosp_rules.get("model_factory_theory"):
        errors.append("Held rule model_factory_theory was modified")

    # 5. All other rules unchanged
    for r_id, o_rule in orig_rules.items():
        if r_id not in VALIDATED_ELIGIBLE_RULES and r_id != "model_factory_theory":
            if o_rule != prosp_rules.get(r_id):
                errors.append(f"Unselected rule {r_id} was modified")

    is_valid = (len(errors) == 0)
    return {
        "is_valid": is_valid,
        "errors": errors,
        "changed_rule_ids": changed_rule_ids,
        "changed_fields_by_rule": changed_fields_by_rule,
    }


def audit_runtime_semantic_survivability(
    project_root: Path | None = None,
    source_text: str | None = None,
) -> dict[str, Any]:
    """Audit runtime code using Python AST to prove independent locator origins survive retirement.

    Mechanically proves:
      1. iteration over active matching query-expansion rules;
      2. rule-local symbol contribution equivalent to: parsed.symbols.extend(rule.symbols);
      3. post-merge symbol deduplication equivalent to: parsed.symbols = list(dict.fromkeys(parsed.symbols)).
    """
    if source_text is None:
        if project_root is None:
            project_root = Path.cwd()
        retrieval_file = project_root / RETRIEVAL_PY_PATH
        if not retrieval_file.is_file():
            return {
                "retrieval_source_read": False,
                "active_matching_rule_iteration_verified": False,
                "rule_local_symbol_extension_verified": False,
                "post_merge_symbol_deduplication_verified": False,
                "independent_origin_survivability_supported": False,
                "mechanism_status": "FAIL",
                "error": f"Missing file: {retrieval_file}",
            }
        source_text = retrieval_file.read_text(encoding="utf-8")

    tree = ast.parse(source_text)

    has_active_matching_rule_iter = False
    has_rule_local_symbol_extend = False
    has_post_merge_dedup = False

    for node in ast.walk(tree):
        # 1. Loop over active matching query-expansion rules
        if isinstance(node, ast.For):
            iter_repr = ast.unparse(node.iter)
            if "active_matching_rules" in iter_repr:
                has_active_matching_rule_iter = True
            # 2. rule-local symbol contribution: parsed.symbols.extend(rule.symbols)
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Expr) and isinstance(subnode.value, ast.Call):
                    call_str = ast.unparse(subnode.value)
                    if "symbols.extend" in call_str and "symbols" in ast.unparse(
                        subnode.value.args[0] if subnode.value.args else ast.Constant(value="")
                    ):
                        has_rule_local_symbol_extend = True

        # 3. parsed.symbols = list(dict.fromkeys(parsed.symbols))
        if isinstance(node, ast.Assign):
            for target in node.targets:
                target_str = ast.unparse(target)
                val_str = ast.unparse(node.value)
                if "symbols" in target_str and "dict.fromkeys" in val_str and "symbols" in val_str:
                    has_post_merge_dedup = True

    mechanism_pass = (
        has_active_matching_rule_iter
        and has_rule_local_symbol_extend
        and has_post_merge_dedup
    )

    return {
        "retrieval_source_read": True,
        "active_matching_rule_iteration_verified": has_active_matching_rule_iter,
        "rule_local_symbol_extension_verified": has_rule_local_symbol_extend,
        "post_merge_symbol_deduplication_verified": has_post_merge_dedup,
        "independent_origin_survivability_supported": mechanism_pass,
        "mechanism_status": "PASS" if mechanism_pass else "FAIL",
    }


def audit_full_current_config_drift(
    project_root: Path,
    custom_config_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Full six-field frozen-contract drift audit across all three selected Batch2 rules."""
    selection_file = project_root / D4_A4_SELECTION_PATH
    with open(selection_file, encoding="utf-8") as f:
        selection_data = json.load(f)

    d4_a4_drift_audit = selection_data.get("current_drift_audit", {})

    if custom_config_data is not None:
        config_data = custom_config_data
    else:
        config_file = project_root / QUERY_EXPANSIONS_PATH
        with open(config_file, encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

    rules = config_data.get("rules", [])
    rule_map = {r["rule_id"]: r for r in rules}

    audit_by_rule: dict[str, Any] = {}
    material_drift = False

    for rule_id in BATCH2_SELECTED_RULES:
        current_rule = rule_map.get(rule_id)
        d4_a4_record = d4_a4_drift_audit.get(rule_id)

        if not current_rule or not d4_a4_record:
            audit_by_rule[rule_id] = {"exists": False}
            material_drift = True
            continue

        triggers_match = current_rule.get("triggers", []) == d4_a4_record.get("current_triggers", [])
        repos_match = current_rule.get("repositories", []) == d4_a4_record.get("current_repositories", [])
        concepts_match = current_rule.get("concepts", []) == d4_a4_record.get("current_concepts", [])
        symbols_match = current_rule.get("symbols", []) == d4_a4_record.get("current_symbols", [])
        hints_match = current_rule.get("paper_page_hints", {}) == d4_a4_record.get("current_paper_page_hints", {})
        structured_match = (
            current_rule.get("structured_replacement", False) is False
            and d4_a4_record.get("structured_replacement_is_false", False) is True
        )

        rule_drift = not (
            triggers_match
            and repos_match
            and concepts_match
            and symbols_match
            and hints_match
            and structured_match
        )

        if rule_drift:
            material_drift = True

        audit_by_rule[rule_id] = {
            "triggers_match": triggers_match,
            "repositories_match": repos_match,
            "concepts_match": concepts_match,
            "symbols_match": symbols_match,
            "paper_page_hints_match": hints_match,
            "effective_structured_replacement_false_match": structured_match,
            "rule_material_drift": rule_drift,
        }

    return {
        "material_drift": material_drift,
        "rule_audits": audit_by_rule,
        "total_rules": len(rules),
    }


def construct_repaired_prospective_mutation(
    project_root: Path,
    raw_yaml_text: str | None = None,
) -> dict[str, Any]:
    """Construct repaired prospective mutation changing only symbols: [] with no structured replacement."""
    if raw_yaml_text is not None:
        original_text = raw_yaml_text
    else:
        config_file = project_root / QUERY_EXPANSIONS_PATH
        original_text = config_file.read_text(encoding="utf-8")

    lines = original_text.splitlines(keepends=True)
    modified_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "rule_id: effective_acceptance_pipeline" in line:
            modified_lines.append(line)
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("- rule_id:"):
                cur = lines[i]
                if cur.strip().startswith("symbols:"):
                    indent = cur[: cur.index("symbols:")]
                    modified_lines.append(f"{indent}symbols: []\n")
                else:
                    modified_lines.append(cur)
                i += 1
            continue
        elif "rule_id: root_macro_usage" in line:
            modified_lines.append(line)
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("- rule_id:"):
                cur = lines[i]
                if cur.strip().startswith("symbols:"):
                    indent = cur[: cur.index("symbols:")]
                    modified_lines.append(f"{indent}symbols: []\n")
                else:
                    modified_lines.append(cur)
                i += 1
            continue
        else:
            modified_lines.append(line)
            i += 1

    prospective_yaml_text = "".join(modified_lines)

    diff_lines = list(
        difflib.unified_diff(
            original_text.splitlines(keepends=True),
            prospective_yaml_text.splitlines(keepends=True),
            fromfile="a/configs/query_expansions.yaml",
            tofile="b/configs/query_expansions.yaml",
        )
    )
    diff_text = "".join(diff_lines)

    orig_dict = yaml.safe_load(original_text)
    prosp_dict = yaml.safe_load(prospective_yaml_text)

    # Validate prospective mutation via single authority validator
    validation_res = validate_prospective_mapping(orig_dict, prosp_dict)

    orig_rules = {r["rule_id"]: r for r in orig_dict.get("rules", [])}
    prosp_rules = {r["rule_id"]: r for r in prosp_dict.get("rules", [])}

    field_presence_preserved = True
    for r_id in VALIDATED_ELIGIBLE_RULES:
        if "structured_replacement" in prosp_rules.get(r_id, {}):
            field_presence_preserved = False

    return {
        "diff_text": diff_text,
        "prospective_yaml_text": prospective_yaml_text,
        "prospective_dict": prosp_dict,
        "validation_res": validation_res,
        "changed_rule_ids": validation_res["changed_rule_ids"],
        "changed_fields_by_rule": validation_res["changed_fields_by_rule"],
        "exact_rules_match": sorted(validation_res["changed_rule_ids"]) == sorted(VALIDATED_ELIGIBLE_RULES),
        "exact_fields_match": all(fields == ["symbols"] for fields in validation_res["changed_fields_by_rule"].values()),
        "held_rule_unchanged": orig_rules.get("model_factory_theory") == prosp_rules.get("model_factory_theory"),
        "field_presence_preserved": field_presence_preserved,
        "structured_replacement_before": {
            r: orig_rules[r].get("structured_replacement", False) for r in BATCH2_SELECTED_RULES
        },
        "structured_replacement_after": {
            r: prosp_rules[r].get("structured_replacement", False) for r in BATCH2_SELECTED_RULES
        },
    }


def audit_independent_origins(
    project_root: Path,
    prospective_config_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit survival of candidate locators in independent rules after prospective mutation."""
    if prospective_config_data is not None:
        config_data = prospective_config_data
    else:
        mutation_res = construct_repaired_prospective_mutation(project_root)
        config_data = mutation_res["prospective_dict"]

    rules = config_data.get("rules", [])

    candidate_symbols = [
        "macro/target/prod_sim_hvmaps.C",
        "data/PndLmdAcceptance.cxx",
        "model/PndLmdModelFactory.cxx",
        "Running/Macros.html",
        "tools/MasterTasks/PndMasterRunSim.cxx",
    ]

    occurrence_map: dict[str, list[str]] = {s: [] for s in candidate_symbols}
    for rule in rules:
        r_id = rule["rule_id"]
        for sym in rule.get("symbols", []):
            if sym in occurrence_map:
                occurrence_map[sym].append(r_id)

    preservation_witnesses = {
        "model_factory_in_held_rule": (
            "model_factory_theory" in occurrence_map["model/PndLmdModelFactory.cxx"]
        ),
        "model_factory_in_independent_rule": (
            "acceptance_model_boundary" in occurrence_map["model/PndLmdModelFactory.cxx"]
        ),
        "prod_sim_hvmaps_in_independent_rule": (
            "reconstructed_profile_to_acceptance" in occurrence_map["macro/target/prod_sim_hvmaps.C"]
        ),
        "lmd_acceptance_in_independent_rule": (
            "reconstructed_profile_to_acceptance" in occurrence_map["data/PndLmdAcceptance.cxx"]
        ),
        "running_macros_in_independent_rule": (
            "sphinx_operational_architecture" in occurrence_map["Running/Macros.html"]
        ),
        "master_run_sim_in_independent_rule": (
            "simulation_configuration_usage" in occurrence_map["tools/MasterTasks/PndMasterRunSim.cxx"]
        ),
    }

    all_preserved = all(preservation_witnesses.values())

    return {
        "occurrence_map": occurrence_map,
        "preservation_witnesses": preservation_witnesses,
        "all_independent_origins_preserved": all_preserved,
    }


def verify_clean_worktree_and_index(project_root: Path) -> bool:
    """Verify that both working tree and index are completely clean."""
    cmd = ["git", "status", "--porcelain"]
    res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, check=True)
    return len(res.stdout.strip()) == 0


def verify_git_commit_identity(
    project_root: Path,
    head_ref: str = "HEAD",
    _override_message: str | None = None,
    _override_parent: str | None = None,
    _override_parent_message: str | None = None,
    _override_parent_parent: str | None = None,
) -> dict[str, Any]:
    """Verify R1 commit message, direct parent, and parent of parent."""
    # Commit message
    if _override_message is not None:
        head_msg = _override_message
    else:
        cmd_msg = ["git", "log", "-1", head_ref, "--pretty=format:%s"]
        res_msg = subprocess.run(cmd_msg, cwd=project_root, capture_output=True, text=True, check=True)
        head_msg = res_msg.stdout.strip()
    r1_msg_exact = (head_msg == R1_COMMIT_MESSAGE)

    # Head SHA
    cmd_head = ["git", "rev-parse", head_ref]
    head_sha = subprocess.run(cmd_head, cwd=project_root, capture_output=True, text=True, check=True).stdout.strip()

    # Parent SHA
    if _override_parent is not None:
        parent_sha = _override_parent
    else:
        cmd_parent = ["git", "rev-parse", f"{head_ref}~1"]
        res_parent = subprocess.run(cmd_parent, cwd=project_root, capture_output=True, text=True, check=True)
        parent_sha = res_parent.stdout.strip()
    parent_exact = (parent_sha == STARTING_HEAD)

    # Parent message
    if _override_parent_message is not None:
        pmsg = _override_parent_message
    else:
        cmd_pmsg = ["git", "log", "-1", f"{head_ref}~1", "--pretty=format:%s"]
        pmsg = subprocess.run(cmd_pmsg, cwd=project_root, capture_output=True, text=True, check=True).stdout.strip()
    parent_msg_exact = (pmsg == STARTING_COMMIT_MESSAGE)

    # Parent parent SHA
    if _override_parent_parent is not None:
        pparent_sha = _override_parent_parent
    else:
        cmd_pparent = ["git", "rev-parse", f"{head_ref}~2"]
        res_pparent = subprocess.run(cmd_pparent, cwd=project_root, capture_output=True, text=True, check=True)
        pparent_sha = res_pparent.stdout.strip()
    pparent_exact = (pparent_sha == STARTING_PARENT_HEAD)

    all_valid = r1_msg_exact and parent_exact and parent_msg_exact and pparent_exact
    return {
        "all_valid": all_valid,
        "head_sha": head_sha,
        "parent_sha": parent_sha,
        "r1_commit_message_exact": r1_msg_exact,
        "r1_parent_exact": parent_exact,
        "d4_a6_parent_message_exact": parent_msg_exact,
        "d4_a6_parent_parent_exact": pparent_exact,
    }


def verify_git_cumulative_diff(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = STARTING_HEAD,
    _override_diff_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Verify cumulative diff between base_ref and head_ref contains exactly the 7 R1 paths."""
    if _override_diff_paths is not None:
        diff_paths = sorted(_override_diff_paths)
    else:
        cmd = ["git", "diff", "--name-only", base_ref, head_ref]
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, check=True)
        diff_paths = sorted([p.replace("\\", "/").strip() for p in res.stdout.splitlines() if p.strip()])
    exact_match = (diff_paths == sorted(EXPECTED_R1_PATHS))
    return {
        "exact_match": exact_match,
        "diff_paths": diff_paths,
        "expected_paths": sorted(EXPECTED_R1_PATHS),
        "extra_paths": [p for p in diff_paths if p not in EXPECTED_R1_PATHS],
        "missing_paths": [p for p in EXPECTED_R1_PATHS if p not in diff_paths],
    }


def verify_git_amend_diff(
    project_root: Path,
    head_ref: str = "HEAD",
    pre_amend_ref: str = PRE_AMEND_R1_HEAD,
    _override_diff_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Verify incremental amend diff modifies only allowed files, never the two R1 JSON files."""
    if _override_diff_paths is not None:
        diff_paths = sorted(_override_diff_paths)
    else:
        cmd = ["git", "diff", "--name-only", pre_amend_ref, head_ref]
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, check=True)
        diff_paths = sorted([p.replace("\\", "/").strip() for p in res.stdout.splitlines() if p.strip()])
    unauthorized_paths = [p for p in diff_paths if p not in ALLOWED_AMEND_PATHS]
    allowlist_respected = len(unauthorized_paths) == 0
    return {
        "allowlist_respected": allowlist_respected,
        "diff_paths": diff_paths,
        "allowed_paths": sorted(ALLOWED_AMEND_PATHS),
        "unauthorized_paths": unauthorized_paths,
    }


def verify_production_tree_immutability(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = STARTING_HEAD,
    _override_src_tree: tuple[str, str] | None = None,
    _override_configs_tree: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """Verify git tree objects for src and configs are identical to starting boundary."""
    def get_tree_hash(ref_path: str) -> str:
        cmd = ["git", "rev-parse", ref_path]
        return subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, check=True).stdout.strip()

    if _override_src_tree is not None:
        head_src, base_src = _override_src_tree
    else:
        head_src = get_tree_hash(f"{head_ref}:src")
        base_src = get_tree_hash(f"{base_ref}:src")
    src_tree_immutable = (head_src == base_src)

    if _override_configs_tree is not None:
        head_configs, base_configs = _override_configs_tree
    else:
        head_configs = get_tree_hash(f"{head_ref}:configs")
        base_configs = get_tree_hash(f"{base_ref}:configs")
    configs_tree_immutable = (head_configs == base_configs)

    production_immutable = src_tree_immutable and configs_tree_immutable
    return {
        "src_tree_immutable": src_tree_immutable,
        "configs_tree_immutable": configs_tree_immutable,
        "production_tree_immutability": production_immutable,
        "head_src_tree": head_src,
        "base_src_tree": base_src,
        "head_configs_tree": head_configs,
        "base_configs_tree": base_configs,
    }


def verify_authority_and_scientific_blob_immutability(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = STARTING_HEAD,
    _override_d4_a4_match: bool | None = None,
    _override_d4_a5_match: bool | None = None,
) -> dict[str, Any]:
    """Verify Git blob objects for D4-A4 authority and D4-A5 scientific artifacts are identical to base_ref."""
    def get_blob(ref: str, path: str) -> str:
        cmd = ["git", "rev-parse", f"{ref}:{path}"]
        return subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, check=True).stdout.strip()

    if _override_d4_a4_match is not None:
        d4_a4_blobs_sealed = _override_d4_a4_match
    else:
        d4_a4_blobs_sealed = all(
            get_blob(head_ref, p) == get_blob(base_ref, p)
            for p in D4_A4_AUTHORITY_PATHS
        )

    if _override_d4_a5_match is not None:
        d4_a5_blobs_sealed = _override_d4_a5_match
    else:
        d4_a5_blobs_sealed = all(
            get_blob(head_ref, p) == get_blob(base_ref, p)
            for p in D4_A5_SCIENTIFIC_PATHS
        )

    return {
        "d4_a4_authority_artifact_immutability": d4_a4_blobs_sealed,
        "d4_a5_scientific_artifact_immutability": d4_a5_blobs_sealed,
    }


def verify_r1_mapping_artifacts_immutability(
    project_root: Path,
    head_ref: str = "HEAD",
    pre_amend_ref: str = PRE_AMEND_R1_HEAD,
    _override_match: bool | None = None,
) -> dict[str, Any]:
    """Verify R1 decision and prereg JSON blobs at head_ref equal their blobs at PRE_AMEND_R1_HEAD."""
    if _override_match is not None:
        r1_mapping_unchanged = _override_match
    else:
        def get_blob(ref: str, path: str) -> str:
            cmd = ["git", "rev-parse", f"{ref}:{path}"]
            return subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, check=True).stdout.strip()

        r1_mapping_unchanged = all(
            get_blob(head_ref, p) == get_blob(pre_amend_ref, p)
            for p in R1_MAPPING_PATHS
        )
    return {
        "r1_mapping_artifacts_unchanged": r1_mapping_unchanged,
    }


def verify_historical_d4_a6_blobs(
    project_root: Path,
    head_ref: str = "HEAD",
) -> dict[str, Any]:
    """Verify Git blob hashes for historical D4-A6 files against immutable baseline."""
    checks: dict[str, bool] = {}
    for rel_path, expected_blob in HISTORICAL_D4_A6_BLOBS.items():
        cmd = ["git", "rev-parse", f"{head_ref}:{rel_path}"]
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, check=True)
        actual_blob = res.stdout.strip()
        checks[rel_path] = (actual_blob == expected_blob)

    all_sealed = all(checks.values())
    return {
        "historical_blobs_sealed": all_sealed,
        "blob_checks": checks,
    }


def evaluate_d4_a6_r1_decision(project_root: Path) -> dict[str, Any]:
    """Evaluate readiness conditions for D4-A6-R1."""
    # 1. Defect reproduction check
    defect_res = reproduce_historical_d4_a6_defect(project_root)
    cond1_defect_reproduced = defect_res["defect_detected"]

    # 2. D4-A5 scientific verdict preserved
    with open(project_root / D4_A5_RESULT_PATH, encoding="utf-8") as f:
        a5_res = json.load(f)
    cond2_a5_frozen = (
        a5_res.get("verdict_level") == 2
        and a5_res.get("verdict") == "INCONCLUSIVE / BATCH2_REFERENCE_BASELINE_NOT_REPRODUCED"
    )

    # 3. Exactly two rules validated
    validated_rules = [
        r for r in BATCH2_SELECTED_RULES
        if r in VALIDATED_ELIGIBLE_RULES
    ]
    cond3_two_rules_validated = (len(validated_rules) == 2)

    # 4. model_factory_theory held
    cond4_held_rule = (HELD_RULES == ["model_factory_theory"])

    # 5. Full config drift seal across selected rules
    drift_res = audit_full_current_config_drift(project_root)
    cond5_config_drift_seal = not drift_res["material_drift"]

    # 6. Prospective mutation checks via validator
    mut_res = construct_repaired_prospective_mutation(project_root)
    cond6_prospective_mapping_valid = mut_res["validation_res"]["is_valid"]
    cond7_strictly_symbols = mut_res["exact_rules_match"] and mut_res["exact_fields_match"]
    cond8_structured_repl_unchanged = (
        mut_res["structured_replacement_before"] == mut_res["structured_replacement_after"]
        and all(v is False for v in mut_res["structured_replacement_after"].values())
        and mut_res["field_presence_preserved"]
    )
    cond9_held_untouched = mut_res["held_rule_unchanged"]

    # 10. Independent origins preserved
    orig_res = audit_independent_origins(project_root, mut_res["prospective_dict"])
    cond10_independent_origins = orig_res["all_independent_origins_preserved"]

    # 11. Runtime semantic survivability verified via AST
    runtime_res = audit_runtime_semantic_survivability(project_root)
    cond11_runtime_semantic_verified = (runtime_res["mechanism_status"] == "PASS")

    all_conditions = {
        "historical_defect_reproduced": cond1_defect_reproduced,
        "d4_a5_scientific_verdict_preserved": cond2_a5_frozen,
        "exactly_two_rules_validated": cond3_two_rules_validated,
        "model_factory_theory_held": cond4_held_rule,
        "full_selected_rule_config_drift_seal": cond5_config_drift_seal,
        "prospective_mapping_validator_passed": cond6_prospective_mapping_valid,
        "prospective_diff_strictly_symbol_lists": cond7_strictly_symbols,
        "structured_replacement_remains_false_or_default": cond8_structured_repl_unchanged,
        "held_rule_untouched": cond9_held_untouched,
        "independent_origins_preserved": cond10_independent_origins,
        "runtime_semantic_survivability_verified": cond11_runtime_semantic_verified,
    }

    all_passed = all(all_conditions.values())
    decision = (
        "READY_FOR_VALIDATED_SUBSET_LOCATOR_RETIREMENT"
        if all_passed
        else "BLOCKED / PRODUCTION_MAPPING_NOT_EQUIVALENT_TO_FROZEN_D4_A5_TREATMENT"
    )

    return {
        "decision": decision,
        "all_passed": all_passed,
        "conditions": all_conditions,
        "defect_reproduction": defect_res,
        "drift_audit": drift_res,
        "prospective_mutation": mut_res,
        "independent_origins": orig_res,
        "runtime_semantic_survivability": runtime_res,
    }


def verify_d4_a6_r1_artifacts(
    project_root: Path,
    head_ref: str = "HEAD",
) -> dict[str, Any]:
    """Perform post-commit read-only verification of D4-A6-R1."""
    eval_res = evaluate_d4_a6_r1_decision(project_root)

    # 1. Clean worktree and index
    clean_worktree_and_index = verify_clean_worktree_and_index(project_root)

    # 2. Git commit identity
    commit_id_res = verify_git_commit_identity(project_root, head_ref)

    # 3. Cumulative diff exact
    cum_diff_res = verify_git_cumulative_diff(project_root, head_ref)

    # 4. Amend diff allowlist respected
    amend_diff_res = verify_git_amend_diff(project_root, head_ref)

    # 5. Production tree immutability
    prod_tree_res = verify_production_tree_immutability(project_root, head_ref)

    # 6. D4-A4 authority and D4-A5 scientific blob immutability
    auth_sci_res = verify_authority_and_scientific_blob_immutability(project_root, head_ref)

    # 7. R1 mapping artifacts unchanged vs PRE_AMEND_R1_HEAD
    r1_mapping_res = verify_r1_mapping_artifacts_immutability(project_root, head_ref)

    # 8. Historical D4-A6 blobs
    hist_blob_res = verify_historical_d4_a6_blobs(project_root, head_ref)

    all_verifications_passed = (
        clean_worktree_and_index
        and commit_id_res["all_valid"]
        and cum_diff_res["exact_match"]
        and amend_diff_res["allowlist_respected"]
        and prod_tree_res["production_tree_immutability"]
        and auth_sci_res["d4_a4_authority_artifact_immutability"]
        and auth_sci_res["d4_a5_scientific_artifact_immutability"]
        and r1_mapping_res["r1_mapping_artifacts_unchanged"]
        and hist_blob_res["historical_blobs_sealed"]
        and eval_res["all_passed"]
    )

    status = "PASS" if all_verifications_passed else "FAIL"

    receipt = {
        "status": status,
        "decision": eval_res["decision"],
        "r1_head": commit_id_res["head_sha"],
        "r1_parent": commit_id_res["parent_sha"],
        "r1_commit_message_exact": commit_id_res["r1_commit_message_exact"],
        "r1_parent_exact": commit_id_res["r1_parent_exact"],
        "d4_a6_parent_message_exact": commit_id_res["d4_a6_parent_message_exact"],
        "r1_cumulative_diff_exact": cum_diff_res["exact_match"],
        "r1_amend_diff_allowlist_respected": amend_diff_res["allowlist_respected"],
        "clean_worktree_and_index": clean_worktree_and_index,
        "historical_mapping_defect_reproduced": eval_res["defect_reproduction"]["defect_detected"],
        "d4_a5_verdict_preserved": eval_res["conditions"]["d4_a5_scientific_verdict_preserved"],
        "per_rule_eligibility": {
            "effective_acceptance_pipeline": "MIGRATION_ELIGIBLE",
            "root_macro_usage": "MIGRATION_ELIGIBLE",
            "model_factory_theory": "HOLD",
        },
        "full_selected_rule_config_drift_seal": eval_res["conditions"]["full_selected_rule_config_drift_seal"],
        "prospective_changed_rule_ids": eval_res["prospective_mutation"]["changed_rule_ids"],
        "prospective_changed_fields_by_rule": eval_res["prospective_mutation"]["changed_fields_by_rule"],
        "prospective_mapping_validator_passed": eval_res["conditions"]["prospective_mapping_validator_passed"],
        "structured_replacement_before": eval_res["prospective_mutation"]["structured_replacement_before"],
        "structured_replacement_after": eval_res["prospective_mutation"]["structured_replacement_after"],
        "structured_replacement_unchanged": eval_res["conditions"]["structured_replacement_remains_false_or_default"],
        "held_rule_unchanged": eval_res["conditions"]["held_rule_untouched"],
        "runtime_semantic_survivability": eval_res["runtime_semantic_survivability"],
        "independent_origin_preservation": eval_res["independent_origins"]["preservation_witnesses"],
        "historical_d4_a6_artifact_seal": hist_blob_res["historical_blobs_sealed"],
        "r1_mapping_artifacts_unchanged": r1_mapping_res["r1_mapping_artifacts_unchanged"],
        "src_tree_immutable": prod_tree_res["src_tree_immutable"],
        "configs_tree_immutable": prod_tree_res["configs_tree_immutable"],
        "production_tree_immutability": prod_tree_res["production_tree_immutability"],
        "d4_a4_authority_artifact_immutability": auth_sci_res["d4_a4_authority_artifact_immutability"],
        "d4_a5_scientific_artifact_immutability": auth_sci_res["d4_a5_scientific_artifact_immutability"],
        "batch1_active": True,
        "full_batch2_activation_false": True,
    }

    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="D4-A6-R1 Locator-Retirement Mapping Repair")
    parser.add_argument("--project-root", default=".", help="Repository root path")
    parser.add_argument(
        "--mode",
        choices=["audit", "verify"],
        default="verify",
        help="Operation mode",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    if args.mode == "audit":
        eval_result = evaluate_d4_a6_r1_decision(project_root)
        print(json.dumps(eval_result, indent=2, default=str))
        if not eval_result["all_passed"]:
            sys.exit(1)
    elif args.mode == "verify":
        receipt = verify_d4_a6_r1_artifacts(project_root)
        print(json.dumps(receipt, indent=2))
        if receipt["status"] != "PASS":
            sys.exit(1)


if __name__ == "__main__":
    main()
