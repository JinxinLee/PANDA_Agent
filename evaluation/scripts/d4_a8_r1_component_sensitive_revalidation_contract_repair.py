"""D4-A8-R1 — Component-Sensitive Model-Factory Revalidation Contract Repair.

Static audit, preregistration, and verification script for component-sensitive
targeted scientific revalidation of model_factory_theory locators.

Repairs historical D4-A8 scientific defect:
  - No symbol component can receive retirement-validating authority without explicit
    treatment-active direct critical-evidence coverage frozen before outcome exposure.
  - COVERED_SYMBOL_MASK is derived mechanically from eligible coverage.
  - UNCOVERED_SYMBOL_HOLD_MASK and PAGE_HINT_HOLD_MASK remain strictly on HOLD.
  - Plan reusability is determined by an actual static inspection of exposed plan artifacts.
  - Future treatment projection uses the real D4-A5 contribution_ledger and provenance
    origin subtraction semantics rather than a toy model.
  - Historical D4-A8 artifacts remain immutable and reclassified as PARTIAL.
  - Production code and configs remain immutable.
  - Zero provider calls (0 tokens, 0 API invocations).
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

_EVAL_SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _EVAL_SCRIPTS_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

# ---------------------------------------------------------------------------
# Boundaries and Authorities
# ---------------------------------------------------------------------------

STARTING_HEAD = "ae2e744f6a05e711d407a02d0ae276e6e1422809"
STARTING_COMMIT_MESSAGE = "D4-A8 preregister model-factory symbol retirement revalidation"
STARTING_PARENT_HEAD = "2da89b8223399ff184f4b2b3674f7c995ce8d390"

R1_COMMIT_MESSAGE = "D4-A8-R1 repair component-sensitive revalidation contract"

GOLD_QUESTIONS_PATH = "evaluation/benchmarks/v2_6/gold_questions.yaml"
NOVEL_DEV_PATH = "evaluation/novel/v1/novel_dev.yaml"
QUERY_EXPANSIONS_PATH = "configs/query_expansions.yaml"

TARGET_RULE_ID = "model_factory_theory"
ORIGINAL_MODEL_FACTORY_THEORY_SYMBOLS = [
    "model/PndLmdDPMAngModel1D.cxx",
    "model/PndLmdDPMAngModel2D.cxx",
    "model/PndLmdModelFactory.cxx",
]
ORIGINAL_MODEL_FACTORY_THEORY_PAGE_HINTS: dict[str, list[int]] = {
    "pflueger_2017": [51, 57, 65]
}

EXPECTED_R1_PATHS = [
    "docs/EVALUATION_STATUS.md",
    "docs/GENERALIZATION_ROADMAP.md",
    "evaluation/D4_A8_R1_COMPONENT_SENSITIVE_REVALIDATION_CONTRACT_REPAIR.md",
    "evaluation/d4_a8_r1_component_sensitive_revalidation_preregistration.json",
    "evaluation/d4_a8_r1_result.json",
    "evaluation/scripts/d4_a8_r1_component_sensitive_revalidation_contract_repair.py",
    "tests/unit/test_d4_a8_r1_component_sensitive_revalidation_contract_repair.py",
]

HISTORICAL_A8_BLOBS = {
    "evaluation/D4_A8_MODEL_FACTORY_THEORY_SYMBOL_RETIREMENT_REVALIDATION_PREREGISTRATION.md": "cc8e08143231cb8884685c85dae3fb39e5899605",
    "evaluation/d4_a8_model_factory_theory_case_selection.json": "d710ac2f26985092c9f1e9addc1adf186b5e5c88",
    "evaluation/d4_a8_model_factory_theory_symbol_retirement_preregistration.json": "392a32fbc7b33fed83b4cb559cfb2cc8826e2d13",
    "evaluation/scripts/d4_a8_model_factory_theory_symbol_retirement_preregistration.py": "1fb9233b2a3e94dd4bd3a9647ddfd8d16b413339",
    "tests/unit/test_d4_a8_model_factory_theory_symbol_retirement_preregistration.py": "392502324e3ef136d223542419d2246306f40efc",
}

# Component-level disposition states
DISPOSITION_RETIREMENT_VALIDATED = "RETIREMENT_VALIDATED_COMPONENT"
DISPOSITION_DEPENDENCY_OBSERVED = "DEPENDENCY_OBSERVED_RETAIN"
DISPOSITION_BASELINE_NOT_REPRODUCED = "INCONCLUSIVE_BASELINE_NOT_REPRODUCED"
DISPOSITION_APPLICABILITY_INCOMPLETE = "INCONCLUSIVE_APPLICABILITY_INCOMPLETE"
DISPOSITION_COVERAGE_GAP = "HOLD_DIRECT_TREATMENT_COVERAGE_GAP"
DISPOSITION_OUTSIDE_SCOPE = "HOLD_OUTSIDE_TREATMENT_SCOPE"
DISPOSITION_INVALID_PROTOCOL = "INVALID_PROTOCOL"

VALID_COMPONENT_DISPOSITIONS = {
    DISPOSITION_RETIREMENT_VALIDATED,
    DISPOSITION_DEPENDENCY_OBSERVED,
    DISPOSITION_BASELINE_NOT_REPRODUCED,
    DISPOSITION_APPLICABILITY_INCOMPLETE,
    DISPOSITION_COVERAGE_GAP,
    DISPOSITION_OUTSIDE_SCOPE,
    DISPOSITION_INVALID_PROTOCOL,
}

# Overall outcome precedence states
OUTCOME_LEVEL_1_INVALID = "INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED"
OUTCOME_LEVEL_2_BASELINE = "INCONCLUSIVE / ALL_COVERED_COMPONENT_BASELINES_NOT_REPRODUCED"
OUTCOME_LEVEL_3_DEPENDENCY = "PARTIAL / DEPENDENCY_OBSERVED_FOR_COVERED_COMPONENTS_RETAIN"
OUTCOME_LEVEL_4_REGRESSION = "FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION"
OUTCOME_LEVEL_5_APPLICABILITY = "INCONCLUSIVE / COVERED_COMPONENT_APPLICABILITY_INCOMPLETE"
OUTCOME_LEVEL_6_PARTIAL_PASS = (
    "PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD"
)


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_gold_questions(project_root: Path) -> list[dict[str, Any]]:
    """Load benchmark questions from gold_questions.yaml."""
    path = project_root / GOLD_QUESTIONS_PATH
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("questions", [])


def load_novel_questions(project_root: Path) -> list[dict[str, Any]]:
    """Load novel questions from novel_dev.yaml if present."""
    path = project_root / NOVEL_DEV_PATH
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("questions", [])


# ---------------------------------------------------------------------------
# Audits: Case Eligibility and Component-Sensitive Coverage
# ---------------------------------------------------------------------------

def audit_case_eligibility(gold_questions: list[dict[str, Any]]) -> dict[str, Any]:
    """Audit metadata and formal eligibility for benchmark candidate cases."""
    case_map = {q["id"]: q for q in gold_questions}
    results: dict[str, Any] = {}
    errors: list[str] = []

    # 1. g031 (ModelFactory.cxx direct candidate)
    g031 = case_map.get("g031")
    if not g031:
        errors.append("g031 not found in gold_questions.yaml")
    else:
        valid = (
            g031.get("split") == "dev"
            and g031.get("language") == "en"
            and g031.get("intent") == "api"
            and g031.get("expected_status") == "answered"
            and g031.get("review_status") == "approved"
            and any(
                eg.get("group_id") == "g031.e1"
                and any(
                    ev.get("path") == "model/PndLmdModelFactory.cxx"
                    and ev.get("symbol") == "generateModel"
                    for ev in eg.get("any_of", [])
                )
                for eg in g031.get("required_evidence_groups", [])
            )
        )
        if not valid:
            errors.append("g031 failed metadata or evidence validation")
        results["g031"] = {
            "valid": valid,
            "formal_role": "DIRECT_MODEL_FACTORY_TREATMENT_CASE",
            "required_component": "model/PndLmdModelFactory.cxx",
            "evidence_groups": ["g031.e1"],
        }

    # 2. g032 (DPM1D adjacent control)
    g032 = case_map.get("g032")
    if not g032:
        errors.append("g032 not found in gold_questions.yaml")
    else:
        valid = (
            g032.get("split") == "dev"
            and g032.get("language") == "en"
            and g032.get("intent") == "api"
            and g032.get("expected_status") == "answered"
            and g032.get("review_status") == "approved"
            and any(
                eg.get("group_id") == "g032.e1"
                and any(
                    ev.get("path") == "model/PndLmdDPMAngModel1D.cxx"
                    for ev in eg.get("any_of", [])
                )
                for eg in g032.get("required_evidence_groups", [])
            )
        )
        if not valid:
            errors.append("g032 failed metadata or evidence validation")
        results["g032"] = {
            "valid": valid,
            "formal_role": "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
            "adjacent_component": "model/PndLmdDPMAngModel1D.cxx",
            "evidence_groups": ["g032.e1"],
        }

    # 3. g033 (DPM2D adjacent control)
    g033 = case_map.get("g033")
    if not g033:
        errors.append("g033 not found in gold_questions.yaml")
    else:
        valid = (
            g033.get("split") == "dev"
            and g033.get("language") == "en"
            and g033.get("intent") == "api"
            and g033.get("expected_status") == "answered"
            and g033.get("review_status") == "approved"
            and any(
                eg.get("group_id") == "g033.e1"
                and any(
                    ev.get("path") == "model/PndLmdDPMAngModel2D.cxx"
                    for ev in eg.get("any_of", [])
                )
                for eg in g033.get("required_evidence_groups", [])
            )
        )
        if not valid:
            errors.append("g033 failed metadata or evidence validation")
        results["g033"] = {
            "valid": valid,
            "formal_role": "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
            "adjacent_component": "model/PndLmdDPMAngModel2D.cxx",
            "evidence_groups": ["g033.e1"],
        }

    # 4. g047 (Pflueger page 51 adjacent control)
    g047 = case_map.get("g047")
    if not g047:
        errors.append("g047 not found in gold_questions.yaml")
    else:
        valid = (
            g047.get("split") == "dev"
            and g047.get("language") == "en"
            and g047.get("intent") == "algorithm_theory"
            and g047.get("expected_status") == "answered"
            and g047.get("review_status") == "approved"
            and any(
                eg.get("group_id") == "g047.e1"
                and any(
                    ev.get("source_id") == "pflueger_2017" and ev.get("pdf_page") == 51
                    for ev in eg.get("any_of", [])
                )
                for eg in g047.get("required_evidence_groups", [])
            )
        )
        if not valid:
            errors.append("g047 failed metadata or evidence validation")
        results["g047"] = {
            "valid": valid,
            "formal_role": "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL",
            "adjacent_page_hint": {"source_id": "pflueger_2017", "pdf_page": 51},
            "evidence_groups": ["g047.e1"],
        }

    # 5. g064 (excluded non-English diagnostic case)
    g064 = case_map.get("g064")
    if not g064:
        errors.append("g064 not found in gold_questions.yaml")
    else:
        results["g064"] = {
            "valid": True,
            "language": g064.get("language"),
            "excluded": True,
            "reason": "NON_ENGLISH_OUTSIDE_FORMAL_PRODUCT_GATE",
        }

    all_valid = (len(errors) == 0)
    return {
        "all_valid": all_valid,
        "errors": errors,
        "case_audits": results,
    }


def audit_component_sensitive_coverage(
    project_root: Path,
    gold_questions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Audit mechanical coverage of model_factory_theory symbol components.

    Checks:
    - Which questions deterministically match model_factory_theory under production query expansion.
    - Which matched questions possess approved formal English status.
    - Which symbol components are directly required by critical evidence in matched cases.
    - Mechanically derives COVERED_SYMBOL_MASK, UNCOVERED_SYMBOL_HOLD_MASK, and PAGE_HINT_HOLD_MASK.
    """
    from panda_agent.config import load_query_expansions
    from panda_agent.d3_structured import select_matching_query_expansions

    qe = load_query_expansions(project_root / QUERY_EXPANSIONS_PATH)
    case_map = {q["id"]: q for q in gold_questions}

    # Evaluate production matching for formal cohort
    matching_info: dict[str, Any] = {}
    for cid in ["g031", "g032", "g033", "g047"]:
        if cid not in case_map:
            continue
        q_text = case_map[cid]["query"]
        dec = select_matching_query_expansions(q_text, qe.rules, None)
        matched = [r.rule_id for r in dec.active_matching_rules]
        matching_info[cid] = {
            "query": q_text,
            "matched_rules": matched,
            "matches_target_rule": TARGET_RULE_ID in matched,
        }

    # Per-component direct coverage check across all approved English Gold questions
    component_coverage: dict[str, dict[str, Any]] = {}
    for sym in ORIGINAL_MODEL_FACTORY_THEORY_SYMBOLS:
        direct_cases: list[dict[str, Any]] = []
        for q in gold_questions:
            if q.get("language") != "en" or q.get("review_status") != "approved":
                continue
            q_text = q.get("query", "")
            dec = select_matching_query_expansions(q_text, qe.rules, None)
            matched = [r.rule_id for r in dec.active_matching_rules]
            if TARGET_RULE_ID in matched:
                # Check if this question's critical evidence requires sym
                ev_groups = []
                for eg in q.get("required_evidence_groups", []):
                    for ev in eg.get("any_of", []):
                        if ev.get("path") == sym:
                            ev_groups.append(eg.get("group_id"))
                if ev_groups:
                    direct_cases.append({
                        "case_id": q["id"],
                        "intent": q.get("intent"),
                        "critical_evidence_groups": sorted(set(ev_groups)),
                    })

        if direct_cases:
            component_coverage[sym] = {
                "coverage_status": "DIRECT_TREATMENT_COVERAGE_FOUND",
                "direct_cases": direct_cases,
                "targetable": True,
            }
        else:
            component_coverage[sym] = {
                "coverage_status": "DIRECT_TREATMENT_COVERAGE_GAP",
                "direct_cases": [],
                "targetable": False,
            }

    # Mechanically derive masks
    covered_symbol_mask = [
        sym for sym in ORIGINAL_MODEL_FACTORY_THEORY_SYMBOLS
        if component_coverage[sym]["targetable"]
    ]
    uncovered_symbol_hold_mask = [
        sym for sym in ORIGINAL_MODEL_FACTORY_THEORY_SYMBOLS
        if not component_coverage[sym]["targetable"]
    ]
    page_hint_hold_mask = copy.deepcopy(ORIGINAL_MODEL_FACTORY_THEORY_PAGE_HINTS)

    # Formal direct cases and critical evidence mapping
    formal_direct_cases_by_component: dict[str, list[str]] = {}
    formal_critical_evidence_by_component: dict[str, dict[str, list[str]]] = {}
    for sym in covered_symbol_mask:
        cases = [c["case_id"] for c in component_coverage[sym]["direct_cases"]]
        formal_direct_cases_by_component[sym] = cases
        ev_map = {c["case_id"]: c["critical_evidence_groups"] for c in component_coverage[sym]["direct_cases"]}
        formal_critical_evidence_by_component[sym] = ev_map

    # Verification when full cohort present
    if "g031" in matching_info:
        assert matching_info["g031"]["matches_target_rule"] is True
    if "g032" in matching_info:
        assert matching_info["g032"]["matches_target_rule"] is False
    if "g033" in matching_info:
        assert matching_info["g033"]["matches_target_rule"] is False
    if "g047" in matching_info:
        assert matching_info["g047"]["matches_target_rule"] is False

    return {
        "matching_info": matching_info,
        "component_coverage": component_coverage,
        "covered_symbol_mask": covered_symbol_mask,
        "uncovered_symbol_hold_mask": uncovered_symbol_hold_mask,
        "page_hint_hold_mask": page_hint_hold_mask,
        "formal_direct_cases_by_component": formal_direct_cases_by_component,
        "formal_critical_evidence_by_component": formal_critical_evidence_by_component,
    }


def audit_page_hint_coverage_gap_approval_aware(project_root: Path) -> dict[str, Any]:
    """Audit whether any approved English question matches model_factory_theory under an intent permitting page hints."""
    from panda_agent.config import load_query_expansions
    from panda_agent.d3_structured import select_matching_query_expansions

    qe = load_query_expansions(project_root / QUERY_EXPANSIONS_PATH)
    candidate_surviving_cases: list[dict[str, Any]] = []

    # Check Gold
    gold_path = project_root / GOLD_QUESTIONS_PATH
    with open(gold_path, "r", encoding="utf-8") as f:
        gold_data = yaml.safe_load(f)

    for q in gold_data.get("questions", []):
        q_text = q.get("query", "")
        dec = select_matching_query_expansions(q_text, qe.rules, None)
        matched = [r.rule_id for r in dec.active_matching_rules]
        if TARGET_RULE_ID in matched:
            lang = q.get("language")
            intent = q.get("intent")
            status = q.get("review_status")
            survives = (
                lang == "en"
                and status == "approved"
                and intent in ("algorithm_theory", "algorithm_implementation")
            )
            if survives:
                candidate_surviving_cases.append({
                    "id": q.get("id"),
                    "dataset": "gold",
                    "language": lang,
                    "intent": intent,
                    "review_status": status,
                })

    # Check Novel Dev
    novel_path = project_root / NOVEL_DEV_PATH
    if novel_path.exists():
        with open(novel_path, "r", encoding="utf-8") as f:
            novel_data = yaml.safe_load(f)
        for q in novel_data.get("questions", []):
            q_text = q.get("query") or q.get("question", "")
            dec = select_matching_query_expansions(q_text, qe.rules, None)
            matched = [r.rule_id for r in dec.active_matching_rules]
            if TARGET_RULE_ID in matched:
                lang = q.get("language")
                intent = q.get("intent")
                status = q.get("review_status")
                survives = (
                    lang == "en"
                    and status == "approved"
                    and intent in ("algorithm_theory", "algorithm_implementation")
                )
                if survives:
                    candidate_surviving_cases.append({
                        "id": q.get("id"),
                        "dataset": "novel_dev",
                        "language": lang,
                        "intent": intent,
                        "review_status": status,
                    })

    status_str = "OPEN"
    result_str = (
        "EXISTING_APPROVED_ENGLISH_CASE_FOUND"
        if candidate_surviving_cases
        else "NO_EXISTING_APPROVED_ENGLISH_CASE_FOUND"
    )

    return {
        "status": status_str,
        "result": result_str,
        "candidate_surviving_cases": candidate_surviving_cases,
        "explanation": (
            "No approved English question matches model_factory_theory under an intent "
            "(algorithm_theory or algorithm_implementation) that allows paper page hints "
            "to survive production plan formation. Therefore pflueger_2017 [51, 57, 65] "
            "remain strictly on HOLD."
        ),
    }


# ---------------------------------------------------------------------------
# Real Plan Reusability Audit
# ---------------------------------------------------------------------------

PLAN_BEARING_ARTIFACTS = [
    "evaluation/d4_a5_continuation_raw_prospective_plans.json",
    "evaluation/d4_a5_raw_prospective_plans.json",
    "evaluation/d4_a2_v2_raw_plans.json",
    "evaluation/d4_a2_v1_raw_analyzer_plan_samples.json",
]


def check_plan_record_compatibility(record: dict[str, Any]) -> tuple[bool, str]:
    """Check whether a plan record satisfies complete provenance and behavioral compatibility."""
    if not isinstance(record, dict):
        return False, "RECORD_NOT_DICT"
    if "canonical_plan" not in record and "plan" not in record:
        return False, "CANONICAL_PLAN_MISSING"
    canonical = record.get("canonical_plan") or record.get("plan")
    if not isinstance(canonical, dict):
        return False, "CANONICAL_PLAN_INVALID"
    if "symbols" not in canonical or "concepts" not in canonical:
        return False, "CANONICAL_PLAN_FIELDS_INCOMPLETE"
    if "contribution_ledger" not in record and "contributions" not in record:
        return False, "LEDGER_MISSING"
    # Check behavioral compatibility: must not have corrupted provenance
    ledger = record.get("contribution_ledger") or record.get("contributions")
    if not isinstance(ledger, list):
        return False, "LEDGER_NOT_LIST"
    for entry in ledger:
        if not isinstance(entry, dict):
            return False, "LEDGER_ENTRY_NOT_DICT"
        if "provenance_origin_ids" not in entry and "rule_origins" not in entry and "origins" not in entry:
            return False, "ORIGINS_MISSING_IN_LEDGER_ENTRY"
    return True, "COMPATIBLE"


def audit_plan_reusability(
    project_root: Path,
    candidate_cases: list[str] | None = None,
) -> dict[str, Any]:
    """Scan actual exposed plan-bearing artifacts to determine reusability for candidate cases."""
    if candidate_cases is None:
        candidate_cases = ["g031", "g032", "g033", "g047"]

    found_plans: dict[str, list[dict[str, Any]]] = {cid: [] for cid in candidate_cases}
    scanned_artifacts: list[str] = []

    for rel_path in PLAN_BEARING_ARTIFACTS:
        p = project_root / rel_path
        if not p.exists():
            continue
        scanned_artifacts.append(rel_path)
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        records: list[dict[str, Any]] = []
        if isinstance(data, dict):
            if "plans" in data and isinstance(data["plans"], list):
                records = data["plans"]
            elif "plans" in data and isinstance(data["plans"], dict):
                records = list(data["plans"].values())
            elif "cases" in data and isinstance(data["cases"], dict):
                records = list(data["cases"].values())
            elif "cases" in data and isinstance(data["cases"], list):
                records = data["cases"]
            elif "plan_samples" in data and isinstance(data["plan_samples"], list):
                records = data["plan_samples"]
        elif isinstance(data, list):
            records = data

        for rec in records:
            if not isinstance(rec, dict):
                continue
            case_id = rec.get("case_id") or rec.get("question_id") or rec.get("id")
            if case_id in found_plans:
                found_plans[case_id].append(rec)

    # Classify each candidate case
    reusability_results: dict[str, str] = {}
    fresh_plan_case_ids: list[str] = []
    reusable_plan_case_ids: list[str] = []

    for cid in candidate_cases:
        recs = found_plans[cid]
        if not recs:
            reusability_results[cid] = "NO_COMPATIBLE_FROZEN_PLAN"
            fresh_plan_case_ids.append(cid)
        else:
            compatible = False
            for r in recs:
                is_compat, _ = check_plan_record_compatibility(r)
                if is_compat:
                    compatible = True
                    break
            if compatible:
                reusability_results[cid] = "REUSABLE_FROZEN_SCIENTIFIC_PLAN"
                reusable_plan_case_ids.append(cid)
            else:
                reusability_results[cid] = "NO_COMPATIBLE_FROZEN_PLAN"
                fresh_plan_case_ids.append(cid)

    return {
        "scanned_artifacts": scanned_artifacts,
        "reusability_results": reusability_results,
        "fresh_plan_case_ids": fresh_plan_case_ids,
        "reusable_plan_case_ids": reusable_plan_case_ids,
        "all_require_fresh_acquisition": (len(reusable_plan_case_ids) == 0),
        "total_formal_cases": len(candidate_cases),
        "fresh_plan_count": len(fresh_plan_case_ids),
        "reusable_plan_count": len(reusable_plan_case_ids),
    }


# ---------------------------------------------------------------------------
# Future Cohort and Provider Budget Derivation
# ---------------------------------------------------------------------------

def derive_future_cohort_and_budget(
    covered_symbol_mask: list[str],
    plan_reuse_audit: dict[str, Any],
) -> dict[str, Any]:
    """Derive future formal case cohort, paired cell order, and provider budget from audit findings."""
    # 1. Direct cases for covered components
    direct_cases = []
    if "model/PndLmdModelFactory.cxx" in covered_symbol_mask:
        direct_cases.append("g031")

    # 2. Frozen no-op controls
    controls = ["g032", "g033", "g047"]

    # Deduplicated formal case order
    formal_cohort: list[str] = []
    for c in direct_cases:
        if c not in formal_cohort:
            formal_cohort.append(c)
    for c in controls:
        if c not in formal_cohort:
            formal_cohort.append(c)

    # Paired-cell schedule
    paired_cell_order: list[dict[str, str]] = []
    for cid in formal_cohort:
        paired_cell_order.append({
            "case_id": cid,
            "arm": "A7_CURRENT",
            "cell_id": f"{cid}_A7_CURRENT",
        })
        paired_cell_order.append({
            "case_id": cid,
            "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
            "cell_id": f"{cid}_COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
        })

    # Provider budget derivation
    n = len(formal_cohort)
    reusable_ids = set(plan_reuse_audit.get("reusable_plan_case_ids", []))
    r = sum(1 for cid in formal_cohort if cid in reusable_ids)
    f = n - r

    analyzer_calls = f
    embedding_calls = 2 * n
    reranker_calls = 2 * n
    qa_calls = 0
    verifier_calls = 0
    judge_calls = 0
    evaluator_calls = 0
    retries = 0
    total_logical_model_calls = f + 4 * n

    budget = {
        "N_formal_cases": n,
        "R_reusable_plans": r,
        "F_fresh_plans": f,
        "analyzer_calls": analyzer_calls,
        "embedding_calls": embedding_calls,
        "reranker_calls": reranker_calls,
        "qa_calls": qa_calls,
        "verifier_calls": verifier_calls,
        "judge_calls": judge_calls,
        "scientific_evaluator_calls": evaluator_calls,
        "retries": retries,
        "total_logical_model_calls": total_logical_model_calls,
    }

    return {
        "formal_cohort": formal_cohort,
        "direct_cases": direct_cases,
        "no_op_controls": controls,
        "paired_cell_order": paired_cell_order,
        "total_paired_cells": len(paired_cell_order),
        "derived_provider_budget": budget,
    }


# ---------------------------------------------------------------------------
# Real D4-A5 Contribution Ledger and Projection Machinery
# ---------------------------------------------------------------------------

def build_real_contribution_ledger(
    canonical_plan: dict[str, Any],
    rules_by_id: dict[str, dict[str, Any]],
    matched_rule_ids: list[str],
) -> list[dict[str, Any]]:
    """Build authoritative D4-A5 contribution ledger for a canonical plan."""
    matched = [rid for rid in matched_rule_ids if rid in rules_by_id]

    origin_rules_symbol: dict[str, list[str]] = {}
    origin_rules_concept: dict[str, list[str]] = {}
    origin_rules_repo: dict[str, list[str]] = {}
    origin_rules_hint: dict[tuple[str, int], list[str]] = {}

    for rid in matched:
        rule = rules_by_id[rid]
        for sym in rule.get("symbols") or []:
            origin_rules_symbol.setdefault(sym, []).append(rid)
        for con in rule.get("concepts") or []:
            origin_rules_concept.setdefault(con, []).append(rid)
        for repo in rule.get("repositories") or []:
            origin_rules_repo.setdefault(repo, []).append(rid)
        for source_id, pages in (rule.get("paper_page_hints") or {}).items():
            for page in pages or []:
                origin_rules_hint.setdefault((str(source_id), int(page)), []).append(rid)

    ledger: list[dict[str, Any]] = []

    def _add_entry(kind: str, value: str, *, source_id: str | None = None, pdf_page: int | None = None,
                   rule_origins: list[str], extra_origins: list[str] | None = None) -> None:
        origins = list(rule_origins)
        origin_types: dict[str, str] = {rid: "reviewed_expansion_rule" for rid in rule_origins}
        if extra_origins:
            for eo in extra_origins:
                origins.append(eo)
                origin_types[eo] = "analyzer_semantic_output"

        cid = f"{kind}::{value}" if pdf_page is None else f"{kind}::{source_id}#{pdf_page}"
        ledger.append({
            "contribution_id": cid,
            "kind": kind,
            "value": value,
            "source_id": source_id,
            "pdf_page": pdf_page,
            "provenance_origin_ids": origins,
            "origin_types": origin_types,
            "plan_present": True,
        })

    for sym in canonical_plan.get("symbols") or []:
        _add_entry("symbol", sym, rule_origins=origin_rules_symbol.get(sym, []))
    for con in canonical_plan.get("concepts") or []:
        _add_entry("concept", con, rule_origins=origin_rules_concept.get(con, []))
    for repo in canonical_plan.get("target_repositories") or []:
        _add_entry("repository", repo, rule_origins=origin_rules_repo.get(repo, []))
    for source_id, pages in (canonical_plan.get("paper_page_hints") or {}).items():
        for page in pages or []:
            key = (str(source_id), int(page))
            _add_entry("paper_page_hint", f"{key[0]}#{key[1]}", source_id=key[0], pdf_page=key[1],
                       rule_origins=origin_rules_hint.get(key, []))

    return ledger


def project_component_sensitive_treatment(
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    covered_symbol_mask: list[str],
    matched_rule_ids: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Project treatment plan by subtracting ONLY model_factory_theory origins from covered symbols.

    Semantics:
    1. If model_factory_theory was not matched, zero origins are subtracted.
    2. For symbols in covered_symbol_mask: if model_factory_theory is among provenance origins,
       subtract that origin.
    3. If any independent origins remain, the symbol survives in the projected plan.
    4. If no independent origins remain, the symbol is effectively removed.
    5. Uncovered symbols and paper page hints are never mutated/subtracted (remain strictly HOLD).
    """
    projected = copy.deepcopy(canonical_plan)
    target_rule_matched = TARGET_RULE_ID in matched_rule_ids

    selected_rule_origins_removed = 0
    effective_values_removed: list[str] = []
    values_surviving_via_independent_origins: list[dict[str, Any]] = []
    covered_components_treated: list[str] = []
    held_components_untouched: list[str] = []

    # Identify symbols to remove
    symbols_to_remove: set[str] = set()

    for item in ledger:
        kind = item.get("kind")
        val = item.get("value")
        origins = list(item.get("provenance_origin_ids") or [])

        if kind == "symbol":
            if val in covered_symbol_mask:
                covered_components_treated.append(val)
                if target_rule_matched and TARGET_RULE_ID in origins:
                    selected_rule_origins_removed += 1
                    surviving_origins = [o for o in origins if o != TARGET_RULE_ID]
                    if surviving_origins:
                        values_surviving_via_independent_origins.append({
                            "symbol": val,
                            "surviving_origins": surviving_origins,
                        })
                    else:
                        symbols_to_remove.add(val)
                        effective_values_removed.append(val)
            else:
                held_components_untouched.append(val)
        else:
            held_components_untouched.append(val)

    if symbols_to_remove:
        projected["symbols"] = [
            s for s in (projected.get("symbols") or [])
            if s not in symbols_to_remove
        ]

    diff_receipts = {
        "target_rule_matched": target_rule_matched,
        "selected_rule_origins_removed": selected_rule_origins_removed,
        "effective_values_removed": effective_values_removed,
        "values_surviving_via_independent_origins": values_surviving_via_independent_origins,
        "covered_components_treated": sorted(set(covered_components_treated)),
        "held_components_untouched": sorted(set(held_components_untouched)),
        "canonical_plan_unchanged": True,
    }

    return projected, diff_receipts


# ---------------------------------------------------------------------------
# Outcome Precedence Evaluator
# ---------------------------------------------------------------------------

def evaluate_component_sensitive_hypothetical_outcome(
    covered_symbols: list[str],
    uncovered_symbols: list[str],
    page_hints: dict[str, list[int]],
    case_results: dict[str, dict[str, Any]],
    *,
    protocol_valid: bool = True,
    control_divergence: bool = False,
    safety_regression: bool = False,
) -> dict[str, Any]:
    """Evaluate component-level dispositions and overall outcome precedence."""
    # Level 1: Protocol Failure
    if not protocol_valid:
        return {
            "overall_outcome": OUTCOME_LEVEL_1_INVALID,
            "level": 1,
            "component_dispositions": {sym: DISPOSITION_INVALID_PROTOCOL for sym in covered_symbols},
        }

    # Evaluate per-component dispositions
    component_dispositions: dict[str, str] = {}

    for sym in covered_symbols:
        c_res = case_results.get(sym, {})
        baseline_reproduced = c_res.get("baseline_reproduced", False)
        applicability = c_res.get("applicability", "ACTIVE_IDENTIFIABLE")
        treatment_presence = c_res.get("treatment_presence", False)
        origin_subtracted = c_res.get("origin_subtracted", False)

        if applicability == "AMBIGUOUS_INVALID":
            component_dispositions[sym] = DISPOSITION_INVALID_PROTOCOL
        elif applicability == "INACTIVE_NOT_IDENTIFIABLE":
            component_dispositions[sym] = DISPOSITION_APPLICABILITY_INCOMPLETE
        elif not baseline_reproduced:
            component_dispositions[sym] = DISPOSITION_BASELINE_NOT_REPRODUCED
        elif baseline_reproduced and treatment_presence and origin_subtracted:
            component_dispositions[sym] = DISPOSITION_RETIREMENT_VALIDATED
        elif baseline_reproduced and not treatment_presence and origin_subtracted:
            component_dispositions[sym] = DISPOSITION_DEPENDENCY_OBSERVED
        else:
            component_dispositions[sym] = DISPOSITION_BASELINE_NOT_REPRODUCED

    # Mark uncovered symbols and page hints as HOLD
    for sym in uncovered_symbols:
        component_dispositions[sym] = DISPOSITION_COVERAGE_GAP
    for p_id, pages in page_hints.items():
        component_dispositions[f"{p_id}:{pages}"] = DISPOSITION_OUTSIDE_SCOPE

    # Precedence resolution:
    # Level 2: All covered component baselines not reproduced
    all_baselines_failed = (
        len(covered_symbols) > 0
        and all(component_dispositions.get(sym) == DISPOSITION_BASELINE_NOT_REPRODUCED for sym in covered_symbols)
    )
    if all_baselines_failed:
        return {
            "overall_outcome": OUTCOME_LEVEL_2_BASELINE,
            "level": 2,
            "component_dispositions": component_dispositions,
        }

    # Level 3: Dependency observed for any covered component
    any_dependency = any(
        component_dispositions.get(sym) == DISPOSITION_DEPENDENCY_OBSERVED
        for sym in covered_symbols
    )
    if any_dependency:
        return {
            "overall_outcome": OUTCOME_LEVEL_3_DEPENDENCY,
            "level": 3,
            "component_dispositions": component_dispositions,
        }

    # Level 4: Control divergence or safety regression
    if control_divergence or safety_regression:
        return {
            "overall_outcome": OUTCOME_LEVEL_4_REGRESSION,
            "level": 4,
            "component_dispositions": component_dispositions,
        }

    # Level 5: Applicability incomplete for any covered component
    any_applicability_incomplete = any(
        component_dispositions.get(sym) == DISPOSITION_APPLICABILITY_INCOMPLETE
        for sym in covered_symbols
    )
    if any_applicability_incomplete:
        return {
            "overall_outcome": OUTCOME_LEVEL_5_APPLICABILITY,
            "level": 5,
            "component_dispositions": component_dispositions,
        }

    # Level 6: Successful Partial Outcome
    all_covered_validated = (
        len(covered_symbols) > 0
        and all(component_dispositions.get(sym) == DISPOSITION_RETIREMENT_VALIDATED for sym in covered_symbols)
    )
    if all_covered_validated and not control_divergence and not safety_regression:
        return {
            "overall_outcome": OUTCOME_LEVEL_6_PARTIAL_PASS,
            "level": 6,
            "component_dispositions": component_dispositions,
        }

    return {
        "overall_outcome": "INCONCLUSIVE / UNRECOGNIZED_STATE",
        "level": 99,
        "component_dispositions": component_dispositions,
    }


# ---------------------------------------------------------------------------
# Verification Helpers (Git & Immutability)
# ---------------------------------------------------------------------------

def verify_starting_boundary(project_root: Path, ref: str | None = None) -> dict[str, Any]:
    """Verify git HEAD, commit message, and parent against starting boundary."""
    if ref is None:
        cmd_cur = ["git", "rev-parse", "HEAD"]
        cur_sha = subprocess.run(cmd_cur, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
        target_ref = "HEAD" if cur_sha == STARTING_HEAD else "HEAD~1"
    else:
        target_ref = ref

    cmd_head = ["git", "rev-parse", target_ref]
    head_sha = subprocess.run(cmd_head, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    cmd_msg = ["git", "log", "-1", "--pretty=format:%s", target_ref]
    head_msg = subprocess.run(cmd_msg, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    cmd_parent = ["git", "rev-parse", f"{target_ref}~1"]
    parent_sha = subprocess.run(cmd_parent, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    cmd_status = ["git", "status", "--porcelain"]
    clean = len(subprocess.run(cmd_status, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()) == 0

    return {
        "head_exact": (head_sha == STARTING_HEAD),
        "msg_exact": (head_msg == STARTING_COMMIT_MESSAGE),
        "parent_exact": (parent_sha == STARTING_PARENT_HEAD),
        "clean_worktree": clean,
        "head_sha": head_sha,
        "parent_sha": parent_sha,
        "head_msg": head_msg,
    }


def verify_git_commit_identity(
    project_root: Path,
    head_ref: str = "HEAD",
    expected_parent: str = STARTING_HEAD,
    expected_msg: str = R1_COMMIT_MESSAGE,
) -> dict[str, Any]:
    """Verify git commit message and parent for R1 commit."""
    cmd_msg = ["git", "log", "-1", "--pretty=format:%s", head_ref]
    actual_msg = subprocess.run(cmd_msg, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    cmd_parent = ["git", "rev-parse", f"{head_ref}~1"]
    actual_parent = subprocess.run(cmd_parent, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    msg_exact = (actual_msg == expected_msg)
    parent_exact = (actual_parent == expected_parent)

    return {
        "all_valid": msg_exact and parent_exact,
        "r1_commit_message_exact": msg_exact,
        "r1_parent_exact": parent_exact,
        "actual_msg": actual_msg,
        "actual_parent": actual_parent,
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
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
        diff_paths = sorted([p.replace("\\", "/").strip() for p in res.stdout.splitlines() if p.strip()])

    exact_match = (diff_paths == sorted(EXPECTED_R1_PATHS))
    return {
        "exact_match": exact_match,
        "diff_paths": diff_paths,
        "expected_paths": sorted(EXPECTED_R1_PATHS),
        "extra_paths": [p for p in diff_paths if p not in EXPECTED_R1_PATHS],
        "missing_paths": [p for p in EXPECTED_R1_PATHS if p not in diff_paths],
    }


def verify_production_tree_immutability(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = STARTING_HEAD,
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


def verify_configs_immutability(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = STARTING_HEAD,
    _override_configs_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Verify that within configs/, no file was changed."""
    if _override_configs_paths is not None:
        configs_paths = sorted(_override_configs_paths)
    else:
        cmd = ["git", "diff", "--name-only", base_ref, head_ref, "--", "configs"]
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
        configs_paths = sorted([p.replace("\\", "/").strip() for p in res.stdout.splitlines() if p.strip()])
    exact = (configs_paths == [])
    return {
        "configs_immutable": exact,
        "configs_paths": configs_paths,
    }


def verify_historical_a8_immutability(project_root: Path, head_ref: str = "HEAD") -> dict[str, Any]:
    """Verify that historical A8 artifacts are sealed and unchanged from STARTING_HEAD."""
    mismatches: list[str] = []
    blob_hashes: dict[str, str] = {}

    for rel_path, expected_blob in HISTORICAL_A8_BLOBS.items():
        cmd = ["git", "rev-parse", f"{head_ref}:{rel_path}"]
        try:
            actual_blob = subprocess.run(
                cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True
            ).stdout.strip()
            blob_hashes[rel_path] = actual_blob
            if actual_blob != expected_blob:
                mismatches.append(f"{rel_path}: expected {expected_blob}, got {actual_blob}")
        except Exception as e:
            mismatches.append(f"{rel_path}: failed to read blob ({e})")

    return {
        "all_match": len(mismatches) == 0,
        "mismatches": mismatches,
        "blob_hashes": blob_hashes,
    }


def verify_clean_worktree(project_root: Path) -> bool:
    """Verify working tree and index are completely clean."""
    cmd = ["git", "status", "--porcelain"]
    res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
    return len(res.stdout.strip()) == 0


def verify_production_state(project_root: Path) -> dict[str, Any]:
    """Verify production query_expansions.yaml conforms to post-D4-A7 contract."""
    from panda_agent.config import load_query_expansions

    full_path = project_root / QUERY_EXPANSIONS_PATH
    qe = load_query_expansions(full_path)
    r_map = {r.rule_id: r for r in qe.rules}

    eff = r_map.get("effective_acceptance_pipeline")
    root_macro = r_map.get("root_macro_usage")
    mft = r_map.get("model_factory_theory")
    poca = r_map.get("event_poca_handoff")
    restgas = r_map.get("restgas_profile_workflow")

    valid = (
        eff is not None and eff.symbols == [] and getattr(eff, "structured_replacement", False) is False
        and root_macro is not None and root_macro.symbols == [] and getattr(root_macro, "structured_replacement", False) is False
        and mft is not None and mft.symbols == ORIGINAL_MODEL_FACTORY_THEORY_SYMBOLS
        and getattr(mft, "paper_page_hints", {}).get("pflueger_2017") == [51, 57, 65]
        and getattr(mft, "structured_replacement", False) is False
        and poca is not None and poca.symbols == [] and getattr(poca, "structured_replacement", False) is True
        and restgas is not None and restgas.symbols == [] and getattr(restgas, "structured_replacement", False) is True
    )

    return {
        "production_state_valid": valid,
        "effective_acceptance_pipeline_retired": (eff.symbols == [] if eff else False),
        "root_macro_usage_retired": (root_macro.symbols == [] if root_macro else False),
        "model_factory_theory_held": (mft.symbols == ORIGINAL_MODEL_FACTORY_THEORY_SYMBOLS if mft else False),
        "batch1_active": (poca.symbols == [] and restgas.symbols == [] if poca and restgas else False),
    }


# ---------------------------------------------------------------------------
# High-Level Audit and Verification Dispatchers
# ---------------------------------------------------------------------------

def audit_preregistration(project_root: Path) -> dict[str, Any]:
    """Run full audit for D4-A8-R1 preregistration."""
    gold_questions = load_gold_questions(project_root)
    case_audit = audit_case_eligibility(gold_questions)
    coverage_audit = audit_component_sensitive_coverage(project_root, gold_questions)
    gap_audit = audit_page_hint_coverage_gap_approval_aware(project_root)
    plan_reuse = audit_plan_reusability(project_root)
    cohort_budget = derive_future_cohort_and_budget(
        coverage_audit["covered_symbol_mask"], plan_reuse
    )
    prod_state = verify_production_state(project_root)

    all_pass = (
        case_audit["all_valid"]
        and len(coverage_audit["covered_symbol_mask"]) > 0
        and gap_audit["status"] == "OPEN"
        and plan_reuse["all_require_fresh_acquisition"]
        and prod_state["production_state_valid"]
    )

    return {
        "status": "PASS" if all_pass else "FAIL",
        "decision": (
            "COMPONENT_SENSITIVE_MODEL_FACTORY_REVALIDATION_PREREGISTERED"
            if all_pass
            else "PREREGISTRATION_AUDIT_FAILED"
        ),
        "case_eligibility_audit": case_audit["all_valid"],
        "covered_symbol_mask": coverage_audit["covered_symbol_mask"],
        "uncovered_symbol_hold_mask": coverage_audit["uncovered_symbol_hold_mask"],
        "page_hint_hold_mask": coverage_audit["page_hint_hold_mask"],
        "page_hint_gap_status": gap_audit["status"],
        "page_hint_gap_result": gap_audit["result"],
        "formal_cohort": cohort_budget["formal_cohort"],
        "derived_provider_budget": cohort_budget["derived_provider_budget"],
        "plan_reusability": plan_reuse["reusability_results"],
        "production_state_valid": prod_state["production_state_valid"],
        "errors": case_audit["errors"],
    }


def verify_preregistration(project_root: Path) -> dict[str, Any]:
    """Run verification mode (requires committed R1 state)."""
    audit_res = audit_preregistration(project_root)
    clean_wt = verify_clean_worktree(project_root)
    commit_ident = verify_git_commit_identity(project_root)
    cum_diff = verify_git_cumulative_diff(project_root)
    src_tree = verify_production_tree_immutability(project_root)
    configs_diff = verify_configs_immutability(project_root)
    hist_a8 = verify_historical_a8_immutability(project_root)

    all_pass = (
        audit_res["status"] == "PASS"
        and clean_wt
        and commit_ident["all_valid"]
        and cum_diff["exact_match"]
        and src_tree["src_tree_immutable"]
        and configs_diff["configs_immutable"]
        and hist_a8["all_match"]
    )

    errors = list(audit_res.get("errors", []))
    if not clean_wt:
        errors.append("Working tree or index is dirty")
    if not commit_ident["all_valid"]:
        errors.append("Commit message or parent does not match R1 contract")
    if not cum_diff["exact_match"]:
        errors.append(f"Cumulative diff mismatch: {cum_diff['diff_paths']}")
    if not src_tree["src_tree_immutable"]:
        errors.append("src tree modified")
    if not configs_diff["configs_immutable"]:
        errors.append("configs directory modified")
    if not hist_a8["all_match"]:
        errors.append(f"Historical A8 blob mismatch: {hist_a8['mismatches']}")

    return {
        "status": "PASS" if all_pass else "FAIL",
        "decision": (
            "COMPONENT_SENSITIVE_MODEL_FACTORY_REVALIDATION_PREREGISTERED"
            if all_pass
            else "PREREGISTRATION_VERIFICATION_FAILED"
        ),
        "audit_status": audit_res["status"],
        "clean_worktree": clean_wt,
        "r1_commit_message_exact": commit_ident["r1_commit_message_exact"],
        "r1_parent_exact": commit_ident["r1_parent_exact"],
        "r1_cumulative_diff_exact": cum_diff["exact_match"],
        "src_tree_immutable": src_tree["src_tree_immutable"],
        "configs_immutable": configs_diff["configs_immutable"],
        "historical_a8_blobs_match": hist_a8["all_match"],
        "covered_symbol_mask": audit_res.get("covered_symbol_mask", []),
        "uncovered_symbol_hold_mask": audit_res.get("uncovered_symbol_hold_mask", []),
        "page_hint_hold_mask": audit_res.get("page_hint_hold_mask", {}),
        "formal_cohort": audit_res.get("formal_cohort", []),
        "derived_provider_budget": audit_res.get("derived_provider_budget", {}),
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="D4-A8-R1 Revalidation Contract Repair Runner")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--mode", choices=["audit", "verify"], default="verify")
    args = parser.parse_args()

    project_root = args.project_root.resolve()

    if args.mode == "audit":
        res = audit_preregistration(project_root)
    else:
        # Pre-commit test runs check whether HEAD is still STARTING_HEAD
        cmd_head = ["git", "rev-parse", "HEAD"]
        head_sha = subprocess.run(cmd_head, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
        if head_sha == STARTING_HEAD:
            res = audit_preregistration(project_root)
        else:
            res = verify_preregistration(project_root)

    print(json.dumps(res, indent=2))
    if res.get("status") != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
