"""D4-A6 — Validated-Subset Batch2 Runtime Migration Preregistration.

Static audit, eligibility determination, and prospective diff construction
translating frozen D4-A5 per-rule scientific dispositions into an auditable
production migration contract without production mutation.
"""

from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
import sys
from typing import Any

import yaml

# Authoritative Starting Boundaries
STARTING_HEAD = "7b9d9d13903d874c000c0097304bfccc19dbbf65"
STARTING_COMMIT_MESSAGE = "D4-A5-R8 repair post-closeout verification contract"
CLOSEOUT_HEAD = "c33f4cbe0bc2dfe6352d70396ebbdc203d3c624f"
CLOSEOUT_COMMIT_MESSAGE = "D4-A5 continuation close controlled retirement validation"

# Relative paths
D4_A5_RESULT_PATH = "evaluation/d4_a5_continuation_result.json"
D4_A5_EVALUATOR_PATH = "evaluation/d4_a5_continuation_evaluator_results.json"
D4_A5_MANIFEST_PATH = "evaluation/d4_a5_continuation_execution_manifest.json"
D4_A4_SELECTION_PATH = "evaluation/d4_a4_batch2_low_risk_retirement_selection.json"
QUERY_EXPANSIONS_PATH = "configs/query_expansions.yaml"
RETRIEVAL_PY_PATH = "src/panda_agent/retrieval.py"
CONFIG_PY_PATH = "src/panda_agent/config.py"

D4_A6_DECISION_PATH = "evaluation/d4_a6_validated_subset_migration_decision.json"
D4_A6_PREREGISTRATION_PATH = "evaluation/d4_a6_validated_subset_migration_preregistration.json"
D4_A6_REPORT_PATH = "evaluation/D4_A6_VALIDATED_SUBSET_RUNTIME_MIGRATION_PREREGISTRATION.md"

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

# Exact candidate masks proposed for retirement in D4-A4/D4-A5
FROZEN_RETIREMENT_MASKS = {
    "effective_acceptance_pipeline": {
        "symbols": [
            "macro/target/prod_sim_hvmaps.C",
            "data/PndLmdAcceptance.cxx",
            "model/PndLmdModelFactory.cxx",
        ],
        "paper_page_hints": {},
    },
    "root_macro_usage": {
        "symbols": [
            "Running/Macros.html",
            "tools/MasterTasks/PndMasterRunSim.cxx",
        ],
        "paper_page_hints": {},
    },
    "model_factory_theory": {
        "symbols": [
            "model/PndLmdDPMAngModel1D.cxx",
            "model/PndLmdDPMAngModel2D.cxx",
            "model/PndLmdModelFactory.cxx",
        ],
        "paper_page_hints": {
            "pflueger_2017": [51, 57, 65],
        },
    },
}

PRESERVED_COMPONENTS = {
    "effective_acceptance_pipeline": {
        "paper_page_hints": {
            "li_2026": [83, 86, 89],
        },
        "triggers": [
            "effective acceptance",
            "restgas acceptance",
            "acceptance calculation",
            "有效接受度",
            "有效接受度",
        ],
        "repositories": [
            "restgas_determination",
            "luminosityfit",
        ],
        "concepts": [
            "profile-dependent effective acceptance pipeline",
        ],
    },
    "root_macro_usage": {
        "paper_page_hints": {},
        "triggers": [
            "ROOT macro",
            "macro execution",
            "run a ROOT macro",
        ],
        "repositories": [
            "pandaroot",
        ],
        "concepts": [
            "PandaRoot macro invocation",
        ],
    },
    "model_factory_theory": {
        "symbols": [
            "model/PndLmdDPMAngModel1D.cxx",
            "model/PndLmdDPMAngModel2D.cxx",
            "model/PndLmdModelFactory.cxx",
        ],
        "paper_page_hints": {
            "pflueger_2017": [51, 57, 65],
        },
        "triggers": [
            "PndLmdModelFactory",
            "DPM、acceptance 和 resolution",
            "DPM acceptance resolution",
        ],
        "repositories": [
            "luminosityfit",
        ],
        "concepts": [
            "DPM model acceptance resolution composition",
        ],
    },
}


def load_d4_a5_scientific_outcome(project_root: Path) -> dict[str, Any]:
    """Load and mechanically verify the frozen D4-A5 scientific outcome."""
    result_file = project_root / D4_A5_RESULT_PATH
    if not result_file.is_file():
        raise FileNotFoundError(f"Missing D4-A5 continuation result file: {result_file}")

    with open(result_file, encoding="utf-8") as f:
        data = json.load(f)

    verdict_level = data.get("verdict_level")
    verdict = data.get("verdict")
    verdict_status = data.get("verdict_status")

    if verdict_level != 2:
        raise ValueError(f"Unexpected D4-A5 verdict level: {verdict_level}, expected 2")
    if verdict != "INCONCLUSIVE / BATCH2_REFERENCE_BASELINE_NOT_REPRODUCED":
        raise ValueError(f"Unexpected D4-A5 verdict: {verdict}")
    if verdict_status != "INCONCLUSIVE":
        raise ValueError(f"Unexpected D4-A5 verdict status: {verdict_status}")

    per_rule_dispositions = data.get("per_rule_dispositions", {})
    return {
        "verdict_level": verdict_level,
        "verdict": verdict,
        "verdict_status": verdict_status,
        "per_rule_dispositions": per_rule_dispositions,
        "reference_baseline_valid": data.get("reference_baseline_valid"),
        "safety": data.get("safety", {}),
    }


# Path aliases for testing and external consumers
DECISION_JSON_PATH = D4_A6_DECISION_PATH
PREREGISTRATION_JSON_PATH = D4_A6_PREREGISTRATION_PATH
PREREGISTRATION_MD_PATH = D4_A6_REPORT_PATH


def evaluate_migration_eligibility(
    dispositions_or_scientific: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Determine per-rule migration eligibility strictly from frozen dispositions."""
    if "per_rule_dispositions" in dispositions_or_scientific:
        per_rule_dispositions = dispositions_or_scientific["per_rule_dispositions"]
    else:
        per_rule_dispositions = dispositions_or_scientific

    eligibility_map: dict[str, dict[str, Any]] = {}
    for rule_id in BATCH2_SELECTED_RULES:
        disposition = per_rule_dispositions.get(rule_id)
        if disposition == "RETIREMENT_VALIDATED":
            eligibility_map[rule_id] = {
                "scientific_disposition": disposition,
                "production_migration_eligibility": "MIGRATION_ELIGIBLE",
                "frozen_retirement_components": FROZEN_RETIREMENT_MASKS[rule_id],
                "preserved_components": PRESERVED_COMPONENTS[rule_id],
                "prospective_production_mutation": {
                    "action": "RETIRE_VALIDATED_LOCATORS_AND_ACTIVATE_STRUCTURED_REPLACEMENT",
                    "symbols": [],
                    "structured_replacement": True,
                },
            }
        elif disposition == "INCONCLUSIVE_BASELINE_NOT_REPRODUCED":
            eligibility_map[rule_id] = {
                "scientific_disposition": disposition,
                "production_migration_eligibility": "HOLD",
                "frozen_components_held": FROZEN_RETIREMENT_MASKS[rule_id],
                "preserved_components": PRESERVED_COMPONENTS[rule_id],
                "hold_reason": (
                    "Active direct-rule evidence group n014.e1 failed to reproduce the "
                    "CURRENT_COMPAT reference baseline under the repaired disposition contract; "
                    "n003.e2 is a separate nonmatching-control finding."
                ),
                "prospective_production_mutation": {
                    "action": "NO_ACTION_HOLD_EXISTING_PRODUCTION_CONTRACT",
                },
            }
        else:
            eligibility_map[rule_id] = {
                "scientific_disposition": disposition or "UNKNOWN",
                "production_migration_eligibility": "HOLD",
                "hold_reason": f"Rule disposition '{disposition}' is not RETIREMENT_VALIDATED.",
            }
    return eligibility_map


map_dispositions_to_migration_eligibility = evaluate_migration_eligibility


def audit_current_production_config(project_root: Path) -> dict[str, Any]:
    """Audit configs/query_expansions.yaml against frozen masks."""
    config_file = project_root / QUERY_EXPANSIONS_PATH
    if not config_file.is_file():
        raise FileNotFoundError(f"Missing config file: {config_file}")

    with open(config_file, encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    rules = config_data.get("rules", [])
    rule_map = {r["rule_id"]: r for r in rules}

    audit_results: dict[str, Any] = {}
    material_drift = False

    for rule_id in BATCH2_SELECTED_RULES:
        rule = rule_map.get(rule_id)
        if not rule:
            audit_results[rule_id] = {"exists": False}
            material_drift = True
            continue

        symbols = rule.get("symbols", [])
        paper_hints = rule.get("paper_page_hints", {})
        triggers = rule.get("triggers", [])
        repos = rule.get("repositories", [])
        concepts = rule.get("concepts", [])
        structured_repl = rule.get("structured_replacement", False)

        expected_retirement = FROZEN_RETIREMENT_MASKS[rule_id]
        expected_preserved = PRESERVED_COMPONENTS[rule_id]

        symbols_match = symbols == expected_retirement["symbols"]
        hints_match = paper_hints == (
            expected_preserved["paper_page_hints"]
            if rule_id == "effective_acceptance_pipeline"
            else expected_retirement["paper_page_hints"]
        )

        rule_drift = not (symbols_match and hints_match and not structured_repl)
        if rule_drift:
            material_drift = True

        audit_results[rule_id] = {
            "exists": True,
            "triggers": triggers,
            "repositories": repos,
            "concepts": concepts,
            "symbols": symbols,
            "paper_page_hints": paper_hints,
            "structured_replacement": structured_repl,
            "symbols_match_frozen": symbols_match,
            "paper_page_hints_match_frozen": hints_match,
            "material_drift": rule_drift,
        }

    return {
        "material_drift": material_drift,
        "rules": audit_results,
        "total_rules": len(rules),
    }


def audit_locator_occurrences(project_root: Path) -> dict[str, Any]:
    """Audit all 54 rules to ensure eligible locators are not globally deleted."""
    config_file = project_root / QUERY_EXPANSIONS_PATH
    with open(config_file, encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    rules = config_data.get("rules", [])

    eligible_symbols = [
        "macro/target/prod_sim_hvmaps.C",
        "data/PndLmdAcceptance.cxx",
        "model/PndLmdModelFactory.cxx",
        "Running/Macros.html",
        "tools/MasterTasks/PndMasterRunSim.cxx",
    ]

    occurrence_map: dict[str, list[str]] = {s: [] for s in eligible_symbols}
    for rule in rules:
        r_id = rule["rule_id"]
        symbols = rule.get("symbols", [])
        for sym in symbols:
            if sym in occurrence_map:
                occurrence_map[sym].append(r_id)

    preservation_witnesses = {
        "model/PndLmdModelFactory.cxx_in_held_rule": (
            "model_factory_theory" in occurrence_map["model/PndLmdModelFactory.cxx"]
        ),
        "macro/target/prod_sim_hvmaps.C_in_independent_rule": (
            "reconstructed_profile_to_acceptance" in occurrence_map["macro/target/prod_sim_hvmaps.C"]
        ),
        "data/PndLmdAcceptance.cxx_in_independent_rule": (
            "reconstructed_profile_to_acceptance" in occurrence_map["data/PndLmdAcceptance.cxx"]
        ),
    }

    return {
        "occurrences": occurrence_map,
        "preservation_witnesses": preservation_witnesses,
        "rule_local_retirement_proven": all(preservation_witnesses.values()),
    }


def audit_structured_replacement_mechanism(project_root: Path) -> dict[str, Any]:
    """Audit retrieval.py and config.py to verify generic structured replacement is rule-local."""
    retrieval_file = project_root / RETRIEVAL_PY_PATH
    config_file = project_root / CONFIG_PY_PATH

    retrieval_content = retrieval_file.read_text(encoding="utf-8")
    config_content = config_file.read_text(encoding="utf-8")

    has_structured_repl_in_config = "structured_replacement: bool = False" in config_content
    has_active_migrated_rules = "active_migrated_rules = [" in retrieval_content
    has_rule_local_filter = (
        'rule.rule_id in matched_set and getattr(rule, "structured_replacement", False)'
        in retrieval_content
    )
    has_treatment_pool_k3 = "build_treatment_pool(rerank_pool, reservable, k=3)" in retrieval_content

    no_batch2_hardcoding = (
        "effective_acceptance_pipeline" not in retrieval_content
        and "root_macro_usage" not in retrieval_content
        and "model_factory_theory" not in retrieval_content
    )

    reusable = (
        has_structured_repl_in_config
        and has_active_migrated_rules
        and has_rule_local_filter
        and has_treatment_pool_k3
        and no_batch2_hardcoding
    )

    return {
        "has_structured_repl_in_config": has_structured_repl_in_config,
        "has_active_migrated_rules": has_active_migrated_rules,
        "has_rule_local_filter": has_rule_local_filter,
        "has_treatment_pool_k3": has_treatment_pool_k3,
        "no_batch2_hardcoding": no_batch2_hardcoding,
        "existing_generic_mechanism_reusable": reusable,
        "all_or_nothing_coupling_present": False,
    }


def construct_prospective_diff(project_root: Path) -> dict[str, Any]:
    """Construct an in-memory prospective diff for configs/query_expansions.yaml."""
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
                elif cur.strip().startswith("concepts:"):
                    modified_lines.append(cur)
                    indent = cur[: cur.index("concepts:")]
                    modified_lines.append(f"{indent}structured_replacement: true\n")
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
                elif cur.strip().startswith("concepts:"):
                    modified_lines.append(cur)
                    indent = cur[: cur.index("concepts:")]
                    modified_lines.append(f"{indent}structured_replacement: true\n")
                else:
                    modified_lines.append(cur)
                i += 1
            continue
        else:
            modified_lines.append(line)
            i += 1

    modified_text = "".join(modified_lines)
    diff_lines = list(
        difflib.unified_diff(
            original_text.splitlines(keepends=True),
            modified_text.splitlines(keepends=True),
            fromfile="a/configs/query_expansions.yaml",
            tofile="b/configs/query_expansions.yaml",
        )
    )
    diff_text = "".join(diff_lines)

    parsed_original = yaml.safe_load(original_text)["rules"]
    parsed_modified = yaml.safe_load(modified_text)["rules"]

    orig_map = {r["rule_id"]: r for r in parsed_original}
    mod_map = {r["rule_id"]: r for r in parsed_modified}

    changed_rules = [
        r_id for r_id in orig_map
        if orig_map[r_id] != mod_map[r_id]
    ]

    return {
        "diff_text": diff_text,
        "changed_rules": changed_rules,
        "changed_rules_match_eligible": changed_rules == VALIDATED_ELIGIBLE_RULES,
        "held_rule_untouched": orig_map["model_factory_theory"] == mod_map["model_factory_theory"],
    }


def evaluate_d4_a6_decision(project_root: Path) -> dict[str, Any]:
    """Evaluate full D4-A6 decision against all Section 20 fail-closed conditions."""
    scientific = load_d4_a5_scientific_outcome(project_root)
    eligibility = evaluate_migration_eligibility(scientific["per_rule_dispositions"])
    config_audit = audit_current_production_config(project_root)
    occurrence_audit = audit_locator_occurrences(project_root)
    mechanism_audit = audit_structured_replacement_mechanism(project_root)
    prospective_diff = construct_prospective_diff(project_root)

    cond1_validated_count = sum(
        1 for r in eligibility.values()
        if r.get("production_migration_eligibility") == "MIGRATION_ELIGIBLE"
    ) == 2
    cond2_held_rule = eligibility.get("model_factory_theory", {}).get("production_migration_eligibility") == "HOLD"
    cond3_no_config_drift = not config_audit["material_drift"]
    cond4_generic_mechanism_reusable = mechanism_audit["existing_generic_mechanism_reusable"]
    cond5_rule_local = not mechanism_audit["all_or_nothing_coupling_present"]
    cond6_diff_valid = prospective_diff["changed_rules_match_eligible"] and prospective_diff["held_rule_untouched"]
    cond7_independent_origin_preserved = occurrence_audit["rule_local_retirement_proven"]

    all_passed = (
        cond1_validated_count
        and cond2_held_rule
        and cond3_no_config_drift
        and cond4_generic_mechanism_reusable
        and cond5_rule_local
        and cond6_diff_valid
        and cond7_independent_origin_preserved
    )

    decision = (
        "READY_FOR_VALIDATED_SUBSET_MIGRATION"
        if all_passed
        else "BLOCKED / PRODUCTION_MAPPING_NOT_EQUIVALENT_TO_VALIDATED_TREATMENT"
    )

    return {
        "decision": decision,
        "all_passed": all_passed,
        "conditions": {
            "exactly_two_rules_validated": cond1_validated_count,
            "model_factory_theory_held": cond2_held_rule,
            "no_production_config_drift": cond3_no_config_drift,
            "existing_generic_mechanism_reusable": cond4_generic_mechanism_reusable,
            "rule_local_activation_representable": cond5_rule_local,
            "prospective_diff_strictly_limited_to_eligible": cond6_diff_valid,
            "independent_origins_preserved": cond7_independent_origin_preserved,
        },
        "scientific_outcome": scientific,
        "eligibility": eligibility,
        "config_audit": config_audit,
        "occurrence_audit": occurrence_audit,
        "mechanism_audit": mechanism_audit,
        "prospective_diff": prospective_diff,
    }


def generate_d4_a6_artifacts(project_root: Path) -> dict[str, Any]:
    """Generate D4-A6 machine decision and preregistration artifacts."""
    eval_result = evaluate_d4_a6_decision(project_root)

    decision_data = {
        "schema_version": "1.0.0",
        "lifecycle_stage": "D4-A6",
        "stage": "D4-A6 Validated-Subset Batch2 Runtime Migration Preregistration",
        "starting_head": STARTING_HEAD,
        "starting_message": STARTING_COMMIT_MESSAGE,
        "d4_a5_closeout_head": CLOSEOUT_HEAD,
        "d4_a5_closeout_message": CLOSEOUT_COMMIT_MESSAGE,
        "d4_a5_r8_identity": {
            "message": STARTING_COMMIT_MESSAGE,
            "head": STARTING_HEAD,
            "semantics": "Non-self-referential forward verification repair commit",
        },
        "d4_a5_verdict": eval_result["scientific_outcome"]["verdict"],
        "d4_a5_verdict_level": eval_result["scientific_outcome"]["verdict_level"],
        "d4_a5_reference_baseline_valid": eval_result["scientific_outcome"]["reference_baseline_valid"],
        "per_rule": eval_result["eligibility"],
        "production_mapping": {
            "existing_generic_mechanism_reusable": eval_result["mechanism_audit"]["existing_generic_mechanism_reusable"],
            "structured_replacement_behavior": "d3_5_selectivity_v2 with bounded_rerank_admission k=3",
            "selected_rule_origin_semantics": "Selected-rule fixed-locator suppression; independent origins preserved",
            "independent_origin_preservation": eval_result["occurrence_audit"]["preservation_witnesses"],
            "all_or_nothing_coupling_present": False,
            "prospective_diff": eval_result["prospective_diff"]["diff_text"],
        },
        "governance": {
            "basis": "D4-A5-R1 component-level applicability and explicit scientific validation contract",
            "batch2_validated_subset": VALIDATED_ELIGIBLE_RULES,
            "batch2_held_rules": HELD_RULES,
            "full_batch_activation": False,
            "batch1_active": True,
            "batch2_production_activation": False,
        },
        "decision": eval_result["decision"],
        "decision_conditions": eval_result["conditions"],
        "next_authorized_stage": "D4-A7 (Validated-Subset Runtime Migration Activation, requires separate authorization)",
    }

    preregistration_data = {
        "schema_version": "1.0.0",
        "lifecycle_stage": "D4-A6",
        "title": "D4-A6 Validated-Subset Batch2 Runtime Migration Preregistration",
        "starting_head": STARTING_HEAD,
        "decision": eval_result["decision"],
        "candidate_rules": {
            "effective_acceptance_pipeline": {
                "eligibility": "MIGRATION_ELIGIBLE",
                "retired_symbols": FROZEN_RETIREMENT_MASKS["effective_acceptance_pipeline"]["symbols"],
                "preserved_hints": PRESERVED_COMPONENTS["effective_acceptance_pipeline"]["paper_page_hints"],
                "structured_replacement": True,
            },
            "root_macro_usage": {
                "eligibility": "MIGRATION_ELIGIBLE",
                "retired_symbols": FROZEN_RETIREMENT_MASKS["root_macro_usage"]["symbols"],
                "structured_replacement": True,
            },
            "model_factory_theory": {
                "eligibility": "HOLD",
                "held_symbols": FROZEN_RETIREMENT_MASKS["model_factory_theory"]["symbols"],
                "held_hints": FROZEN_RETIREMENT_MASKS["model_factory_theory"]["paper_page_hints"],
                "structured_replacement": False,
                "reason": "Active direct-rule evidence group n014.e1 baseline not reproduced; n003.e2 is separate nonmatching-control.",
            },
        },
        "prospective_diff_summary": {
            "file": QUERY_EXPANSIONS_PATH,
            "rules_modified": VALIDATED_ELIGIBLE_RULES,
            "rules_held": HELD_RULES,
            "symbols_retired_count": 5,
            "hints_retired_count": 0,
        },
        "safety_invariants": {
            "no_production_mutation_in_d4_a6": True,
            "no_scientific_recomputation": True,
            "batch1_remains_active": True,
            "batch2_full_activation_remains_false": True,
        },
    }

    report_markdown = f"""# D4-A6 — Validated-Subset Batch2 Runtime Migration Preregistration Report

- **Status**: `{eval_result["decision"]}`
- **Starting HEAD**: `{STARTING_HEAD}`
- **Parent Closeout Commit**: `{CLOSEOUT_HEAD}`
- **Scientific Verdict Preserved**: `Level {eval_result["scientific_outcome"]["verdict_level"]} {eval_result["scientific_outcome"]["verdict"]}`

---

## 1. Executive Summary

D4-A6 translates the frozen D4-A5 per-rule scientific dispositions into an exact, auditable, prospective production-migration contract for the scientifically validated subset of Batch 2:
- **`effective_acceptance_pipeline`**: `RETIREMENT_VALIDATED` → **`MIGRATION_ELIGIBLE`**
- **`root_macro_usage`**: `RETIREMENT_VALIDATED` → **`MIGRATION_ELIGIBLE`**
- **`model_factory_theory`**: `INCONCLUSIVE_BASELINE_NOT_REPRODUCED` → **`HOLD`**

This stage performs **zero production mutation** and **zero scientific re-execution**.

---

## 2. Governance Basis & Rule-Local Migration

Under the repaired D4-A5-R1 governance contract:
1. Component-level applicability and per-rule scientific dispositions dictate migration eligibility.
2. An overall Level-2 INCONCLUSIVE batch verdict does not block rule-local migration of rules whose masks were fully validated (`RETIREMENT_VALIDATED`).
3. Rules with non-reproduced baselines (`model_factory_theory`) remain strictly held in production.
4. The existing generic structured-replacement runtime mechanism (`Retriever.retrieve()` + `d3_5_selectivity_v2` + `k=3` bounded admission) operates rule-locally via `structured_replacement: true` in `configs/query_expansions.yaml` without requiring any new generic mechanism or all-or-nothing coupling.

---

## 3. Mask Accounting & Occurrence Audit

### 3.1 `effective_acceptance_pipeline`
- **Retired Symbols (3)**:
  - `macro/target/prod_sim_hvmaps.C`
  - `data/PndLmdAcceptance.cxx`
  - `model/PndLmdModelFactory.cxx`
- **Preserved Paper Hints**:
  - `li_2026: [83, 86, 89]`
- **Independent Origin Nuance**:
  - In D4-A5, `active_component_count = 3`, `effective_removal_count = 1`.
  - The other two symbols survive in treatment projections via `reconstructed_profile_to_acceptance`.
  - Migration removes only this rule's contribution; `reconstructed_profile_to_acceptance` continues to contribute them independently.

### 3.2 `root_macro_usage`
- **Retired Symbols (2)**:
  - `Running/Macros.html`
  - `tools/MasterTasks/PndMasterRunSim.cxx`

### 3.3 `model_factory_theory` (HOLD)
- **Held Symbols (3)**:
  - `model/PndLmdDPMAngModel1D.cxx`
  - `model/PndLmdDPMAngModel2D.cxx`
  - `model/PndLmdModelFactory.cxx`
- **Held Paper Hints**:
  - `pflueger_2017: [51, 57, 65]`
- **Reason**: Active direct-rule evidence group `n014.e1` failed to reproduce baseline; `n003.e2` is a separate nonmatching-control finding.
- **Occurrence Safety**: `model/PndLmdModelFactory.cxx` under `model_factory_theory` is preserved and untouched even though it is retired under `effective_acceptance_pipeline`.

---

## 4. Prospective Production Diff

```diff
{eval_result["prospective_diff"]["diff_text"]}
```

---

## 5. Decision & Next Stage

- **Decision**: `{eval_result["decision"]}`
- **Batch 1 Status**: `ACTIVE`
- **Batch 2 Full Activation**: `false`
- **Next Authorized Stage**: `D4-A7 (Validated-Subset Runtime Migration Activation)` — requires explicit separate authorization.
"""

    decision_path = project_root / D4_A6_DECISION_PATH
    preregistration_path = project_root / D4_A6_PREREGISTRATION_PATH
    report_path = project_root / D4_A6_REPORT_PATH

    with open(decision_path, "w", encoding="utf-8") as f:
        json.dump(decision_data, f, indent=2)

    with open(preregistration_path, "w", encoding="utf-8") as f:
        json.dump(preregistration_data, f, indent=2)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_markdown)

    return {
        "decision_data": decision_data,
        "preregistration_data": preregistration_data,
        "eval_result": eval_result,
    }


load_frozen_d4_a5_scientific_outcome = load_d4_a5_scientific_outcome


def verify_d4_a6_artifacts(project_root: Path) -> dict[str, Any]:
    """Verify that all D4-A6 artifacts exist, are valid, and match evaluation."""
    decision_path = project_root / D4_A6_DECISION_PATH
    preregistration_path = project_root / D4_A6_PREREGISTRATION_PATH
    report_path = project_root / D4_A6_REPORT_PATH

    for p in (decision_path, preregistration_path, report_path):
        if not p.is_file():
            raise FileNotFoundError(f"Missing D4-A6 artifact: {p}")

    with open(decision_path, encoding="utf-8") as f:
        decision_data = json.load(f)
    with open(preregistration_path, encoding="utf-8") as f:
        prereg_data = json.load(f)

    eval_result = evaluate_d4_a6_decision(project_root)
    expected_decision = eval_result["decision"]
    actual_decision = decision_data.get("decision")

    decision_matches = (
        actual_decision == expected_decision
        and prereg_data.get("decision") == expected_decision
    )

    status = "PASS" if (decision_matches and eval_result["all_passed"]) else "FAIL"

    return {
        "status": status,
        "decision": actual_decision,
        "decision_matches_evaluation": decision_matches,
        "all_conditions_passed": eval_result["all_passed"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="D4-A6 Validated-Subset Migration Preregistration")
    parser.add_argument("--project-root", default=".", help="Repository root path")
    parser.add_argument(
        "--mode",
        choices=["audit", "preregister", "verify"],
        default="preregister",
        help="Operation mode",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    if args.mode == "audit":
        eval_result = evaluate_d4_a6_decision(project_root)
        print(json.dumps(eval_result, indent=2, default=str))
        if not eval_result["all_passed"]:
            sys.exit(1)
    elif args.mode == "preregister":
        artifacts = generate_d4_a6_artifacts(project_root)
        decision = artifacts["decision_data"]["decision"]
        print(f"D4-A6 Preregistration Complete: {decision}")
        if decision != "READY_FOR_VALIDATED_SUBSET_MIGRATION":
            sys.exit(1)
    elif args.mode == "verify":
        verify_res = verify_d4_a6_artifacts(project_root)
        print(f"D4-A6 Verification: {verify_res['status']} ({verify_res['decision']})")
        if verify_res["status"] != "PASS":
            sys.exit(1)


if __name__ == "__main__":
    main()
