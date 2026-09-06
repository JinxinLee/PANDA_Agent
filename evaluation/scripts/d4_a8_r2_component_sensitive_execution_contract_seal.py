"""D4-A8-R2 — Component-Sensitive Model-Factory Execution Contract Seal.

Static audit, preregistration, and verification script for sealing the execution
contract for future D4-A9 targeted scientific validation.

Preserves the accepted D4-A8-R1 scientific target:
  - COVERED_SYMBOL_MASK: ['model/PndLmdModelFactory.cxx']
  - UNCOVERED_SYMBOL_HOLD_MASK: ['model/PndLmdDPMAngModel1D.cxx', 'model/PndLmdDPMAngModel2D.cxx']
  - PAGE_HINT_HOLD_MASK: {'pflueger_2017': [51, 57, 65]}
  - Formal cohort: ['g031', 'g032', 'g033', 'g047']

Hardened execution-contract seals:
  1. Direct binding to frozen D4-A5 pure authority (no silent fallback permitted).
  2. Component-sensitive A9 mask conforming strictly to A5 mask semantics.
  3. Narrow origin-type consistency gate enforcing valid provenance typing.
  4. Full ledger coverage preceding any projection.
  5. Enforceable persistence-before-gate state machine (ACQUIRED -> PERSISTED -> GATED -> RETRIEVED).
  6. Internally consistent plan-reuse compatibility contract (canonical serialization, plan signature, model contract, matched rules).
  7. Deterministic discovery of plan-bearing artifacts with truthful accounting.
  8. Committed machine artifacts consistency seal against live deterministic audit.
  9. Zero provider execution (0 tokens, 0 API invocations).
  10. Production tree and configs immutable.
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
if str(_PROJECT_ROOT / "evaluation" / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "evaluation" / "scripts"))

# ---------------------------------------------------------------------------
# Boundaries and Authorities
# ---------------------------------------------------------------------------

STARTING_HEAD = "a357bfc4e0d846cefa295e98c5de0a8b2813cfa0"
STARTING_COMMIT_MESSAGE = "D4-A8-R1 repair component-sensitive revalidation contract"
STARTING_PARENT_HEAD = "ae2e744f6a05e711d407a02d0ae276e6e1422809"
PARENT_COMMIT_MESSAGE = "D4-A8 preregister model-factory symbol retirement revalidation"

R2_COMMIT_MESSAGE = "D4-A8-R2 seal component-sensitive execution contract"

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

# Frozen scientific target from D4-A8-R1
FROZEN_COVERED_SYMBOL_MASK = ["model/PndLmdModelFactory.cxx"]
FROZEN_UNCOVERED_SYMBOL_HOLD_MASK = [
    "model/PndLmdDPMAngModel1D.cxx",
    "model/PndLmdDPMAngModel2D.cxx",
]
FROZEN_PAGE_HINT_HOLD_MASK: dict[str, list[int]] = {"pflueger_2017": [51, 57, 65]}
FROZEN_FORMAL_CASE_ORDER = ["g031", "g032", "g033", "g047"]

EXPECTED_R2_PATHS = [
    "docs/EVALUATION_STATUS.md",
    "docs/GENERALIZATION_ROADMAP.md",
    "evaluation/D4_A8_R2_COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEAL.md",
    "evaluation/d4_a8_r2_component_sensitive_execution_preregistration.json",
    "evaluation/d4_a8_r2_result.json",
    "evaluation/scripts/d4_a8_r2_component_sensitive_execution_contract_seal.py",
    "tests/unit/test_d4_a8_r2_component_sensitive_execution_contract_seal.py",
]

HISTORICAL_R1_BLOBS = {
    "evaluation/D4_A8_R1_COMPONENT_SENSITIVE_REVALIDATION_CONTRACT_REPAIR.md": "bf5ac0975503716295aab22439536ca8fee6d505",
    "evaluation/d4_a8_r1_component_sensitive_revalidation_preregistration.json": "a72ca83da8eef6852db03376bdcfef89069e254b",
    "evaluation/d4_a8_r1_result.json": "8207c55ed44c166c3cc8381aebe09a5a9ab49a3e",
    "evaluation/scripts/d4_a8_r1_component_sensitive_revalidation_contract_repair.py": "585e95262b267bd5f7418835b7d7fa6d48c9e14c",
    "tests/unit/test_d4_a8_r1_component_sensitive_revalidation_contract_repair.py": "3b3080fb5e31758e95686095bfd71236875b4ec7",
}

HISTORICAL_A8_BLOBS = {
    "evaluation/D4_A8_MODEL_FACTORY_THEORY_SYMBOL_RETIREMENT_REVALIDATION_PREREGISTRATION.md": "cc8e08143231cb8884685c85dae3fb39e5899605",
    "evaluation/d4_a8_model_factory_theory_case_selection.json": "d710ac2f26985092c9f1e9addc1adf186b5e5c88",
    "evaluation/d4_a8_model_factory_theory_symbol_retirement_preregistration.json": "392a32fbc7b33fed83b4cb559cfb2cc8826e2d13",
    "evaluation/scripts/d4_a8_model_factory_theory_symbol_retirement_preregistration.py": "1fb9233b2a3e94dd4bd3a9647ddfd8d16b413339",
    "tests/unit/test_d4_a8_model_factory_theory_symbol_retirement_preregistration.py": "392502324e3ef136d223542419d2246306f40efc",
}

# Real D4-A5 Origin Categories
ORIGIN_ACCEPTED_ANALYZER_DELTA = "accepted_analyzer_semantic_delta"
ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE = "runtime_deterministic_override"
ORIGIN_TYPE_REVIEWED_RULE = "reviewed_expansion_rule"
ORIGIN_TYPE_ANALYZER_DELTA = "accepted_analyzer_semantic_output"
ORIGIN_TYPE_RUNTIME_OVERRIDE = "production_deterministic_override"

# Applicability States
APPLICABILITY_ACTIVE = "ACTIVE_IDENTIFIABLE"
APPLICABILITY_INACTIVE = "INACTIVE_NOT_IDENTIFIABLE"
APPLICABILITY_AMBIGUOUS = "AMBIGUOUS_INVALID"
APPLICABILITY_HOLD = "HOLD_NOT_APPLICABLE"

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

# Plan reuse classification states
PLAN_REUSE_COMPATIBLE = "REUSABLE_FROZEN_SCIENTIFIC_PLAN"
PLAN_REUSE_NO_CANDIDATE = "NO_CANDIDATE_FROZEN_PLAN"
PLAN_REUSE_INCOMPLETE = "CANDIDATE_PLAN_INCOMPLETE"
PLAN_REUSE_BEHAVIOR_INCOMPATIBLE = "CANDIDATE_PLAN_BEHAVIOR_INCOMPATIBLE"
PLAN_REUSE_PROVENANCE_INCOMPATIBLE = "CANDIDATE_PLAN_PROVENANCE_INCOMPATIBLE"
PLAN_REUSE_SERIALIZATION_INCONSISTENT = "CANDIDATE_PLAN_SERIALIZATION_INCONSISTENT"
PLAN_REUSE_SIGNATURE_MISMATCH = "CANDIDATE_PLAN_SIGNATURE_MISMATCH"
PLAN_REUSE_PROVIDER_CONTRACT_INCOMPLETE = "CANDIDATE_PLAN_PROVIDER_CONTRACT_INCOMPLETE"
PLAN_REUSE_PROVIDER_CONTRACT_INCOMPATIBLE = "CANDIDATE_PLAN_PROVIDER_CONTRACT_INCOMPATIBLE"

# Component-sensitive A9 retirement mask strictly adhering to A5 mask schema
COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS: dict[str, dict[str, Any]] = {
    TARGET_RULE_ID: {
        "rule_id": TARGET_RULE_ID,
        "symbols_retired": list(FROZEN_COVERED_SYMBOL_MASK),
        "paper_page_hints_retired": {},
        "symbols_preserved": list(FROZEN_UNCOVERED_SYMBOL_HOLD_MASK),
        "paper_page_hints_preserved": dict(FROZEN_PAGE_HINT_HOLD_MASK),
        "triggers_preserved": [
            "PndLmdModelFactory",
            "DPM、acceptance 和 resolution",
            "DPM acceptance resolution",
        ],
        "repositories_preserved": [
            "luminosityfit",
        ],
        "concepts_preserved": [
            "DPM model acceptance resolution composition",
        ],
        "structured_replacement_after_retirement": False,
    }
}


class TargetedValidationProtocolError(Exception):
    """Raised when targeted validation protocol or treatment construction fails."""
    pass


class StateTransitionError(Exception):
    """Raised when an invalid execution state transition is attempted."""
    pass


# ---------------------------------------------------------------------------
# Strict A5 Authority Loader (No Silent Fallback)
# ---------------------------------------------------------------------------

A5_REQUIRED_HELPERS = [
    "build_contribution_ledger",
    "validate_ledger_coverage",
    "classify_component_applicability",
    "build_retirement_projection_r1",
    "compute_plan_signature",
    "build_batch2_mask_entries",
    "build_retirement_projection",
]


def load_a5_authority() -> Any:
    """Load the frozen D4-A5 batch2 controlled retirement validation authority.

    Fails closed if the module cannot be imported or any required pure helper
    is unavailable. Broad silent fallback is strictly prohibited.
    """
    try:
        import d4_a5_batch2_controlled_retirement_validation as a5
    except ImportError as exc:
        raise RuntimeError(f"A5_PROVENANCE_AUTHORITY_UNAVAILABLE: {exc}") from exc

    missing = [h for h in A5_REQUIRED_HELPERS if not hasattr(a5, h)]
    if missing:
        raise RuntimeError(
            f"A5_PROVENANCE_COMPATIBILITY_NOT_PROVEN: missing required helpers: {missing}"
        )
    return a5


# ---------------------------------------------------------------------------
# Data Loaders
# ---------------------------------------------------------------------------

def load_gold_questions(project_root: Path) -> list[dict[str, Any]]:
    full_path = project_root / GOLD_QUESTIONS_PATH
    if not full_path.exists():
        raise FileNotFoundError(f"gold_questions.yaml not found at {full_path}")
    with open(full_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("questions", [])


def load_novel_questions(project_root: Path) -> list[dict[str, Any]]:
    full_path = project_root / NOVEL_DEV_PATH
    if not full_path.exists():
        return []
    with open(full_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("questions", [])


# ---------------------------------------------------------------------------
# Unified Formal Eligibility Classifier (Section 16-20)
# ---------------------------------------------------------------------------

def classify_formal_case_eligibility(
    q: dict[str, Any],
    dataset_name: str = "gold",
) -> dict[str, Any]:
    """Classify a question's formal evaluation eligibility."""
    case_id = q.get("id", "")
    lang = q.get("language")
    review_status = q.get("review_status")
    expected_status = q.get("expected_status")
    split = q.get("split")

    if dataset_name == "gold":
        is_formal = (
            lang == "en"
            and review_status == "approved"
            and expected_status == "answered"
            and split in ("dev", "test")
        )
        if is_formal:
            classification = "FORMAL_ELIGIBLE"
            reason = "GOLD_CRITERIA_SATISFIED"
        elif lang != "en":
            classification = "EXCLUDED"
            reason = "NON_ENGLISH_OUTSIDE_PRODUCT_SCOPE"
        else:
            classification = "EXCLUDED"
            reason = f"METADATA_CRITERIA_FAILED (review={review_status}, expected={expected_status}, split={split})"
        return {
            "case_id": case_id,
            "dataset": dataset_name,
            "classification": classification,
            "formal_eligible": is_formal,
            "reason": reason,
        }

    if dataset_name == "novel_dev":
        if lang == "en" and expected_status == "answered":
            classification = "DIAGNOSTIC_ONLY"
            reason = "NOVEL_DEV_EXPLORATORY_WITHOUT_FORMAL_AUTHORITY"
        elif lang != "en":
            classification = "EXCLUDED"
            reason = "NON_ENGLISH"
        else:
            classification = "EXCLUDED"
            reason = "NOT_ANSWERED"
        return {
            "case_id": case_id,
            "dataset": dataset_name,
            "classification": classification,
            "formal_eligible": False,
            "reason": reason,
        }

    return {
        "case_id": case_id,
        "dataset": dataset_name,
        "classification": "EXCLUDED",
        "formal_eligible": False,
        "reason": f"UNRECOGNIZED_DATASET: {dataset_name}",
    }


# ---------------------------------------------------------------------------
# Audits: Case Eligibility and Component-Sensitive Coverage
# ---------------------------------------------------------------------------

def audit_case_eligibility(gold_questions: list[dict[str, Any]]) -> dict[str, Any]:
    """Audit formal eligibility for benchmark candidate cases using the unified helper."""
    case_map = {q["id"]: q for q in gold_questions}
    results: dict[str, Any] = {}
    errors: list[str] = []

    # 1. g031 (ModelFactory.cxx direct candidate)
    g031 = case_map.get("g031")
    if not g031:
        errors.append("g031 not found in gold_questions.yaml")
    else:
        elig = classify_formal_case_eligibility(g031, "gold")
        has_evidence = any(
            eg.get("group_id") == "g031.e1"
            and any(
                ev.get("path") == "model/PndLmdModelFactory.cxx"
                and ev.get("symbol") == "generateModel"
                for ev in eg.get("any_of", [])
            )
            for eg in g031.get("required_evidence_groups", [])
        )
        valid = elig["formal_eligible"] and has_evidence
        if not valid:
            errors.append("g031 failed eligibility or evidence validation")
        results["g031"] = {
            "valid": valid,
            "classification": elig["classification"],
            "formal_role": "DIRECT_MODEL_FACTORY_TREATMENT_CASE",
            "required_component": "model/PndLmdModelFactory.cxx",
            "evidence_groups": ["g031.e1"],
        }

    # 2. g032 (DPM1D adjacent control)
    g032 = case_map.get("g032")
    if not g032:
        errors.append("g032 not found in gold_questions.yaml")
    else:
        elig = classify_formal_case_eligibility(g032, "gold")
        has_evidence = any(
            eg.get("group_id") == "g032.e1"
            and any(
                ev.get("path") == "model/PndLmdDPMAngModel1D.cxx"
                for ev in eg.get("any_of", [])
            )
            for eg in g032.get("required_evidence_groups", [])
        )
        valid = elig["formal_eligible"] and has_evidence
        if not valid:
            errors.append("g032 failed eligibility or evidence validation")
        results["g032"] = {
            "valid": valid,
            "classification": elig["classification"],
            "formal_role": "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
            "adjacent_component": "model/PndLmdDPMAngModel1D.cxx",
            "evidence_groups": ["g032.e1"],
        }

    # 3. g033 (DPM2D adjacent control)
    g033 = case_map.get("g033")
    if not g033:
        errors.append("g033 not found in gold_questions.yaml")
    else:
        elig = classify_formal_case_eligibility(g033, "gold")
        has_evidence = any(
            eg.get("group_id") == "g033.e1"
            and any(
                ev.get("path") == "model/PndLmdDPMAngModel2D.cxx"
                for ev in eg.get("any_of", [])
            )
            for eg in g033.get("required_evidence_groups", [])
        )
        valid = elig["formal_eligible"] and has_evidence
        if not valid:
            errors.append("g033 failed eligibility or evidence validation")
        results["g033"] = {
            "valid": valid,
            "classification": elig["classification"],
            "formal_role": "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
            "adjacent_component": "model/PndLmdDPMAngModel2D.cxx",
            "evidence_groups": ["g033.e1"],
        }

    # 4. g047 (Pflueger page 51 adjacent control)
    g047 = case_map.get("g047")
    if not g047:
        errors.append("g047 not found in gold_questions.yaml")
    else:
        elig = classify_formal_case_eligibility(g047, "gold")
        has_evidence = any(
            eg.get("group_id") == "g047.e1"
            and any(
                ev.get("source_id") == "pflueger_2017" and ev.get("pdf_page") == 51
                for ev in eg.get("any_of", [])
            )
            for eg in g047.get("required_evidence_groups", [])
        )
        valid = elig["formal_eligible"] and has_evidence
        if not valid:
            errors.append("g047 failed eligibility or evidence validation")
        results["g047"] = {
            "valid": valid,
            "classification": elig["classification"],
            "formal_role": "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL",
            "adjacent_page_hint": {"source_id": "pflueger_2017", "pdf_page": 51},
            "evidence_groups": ["g047.e1"],
        }

    # 5. g064 (excluded non-English diagnostic case)
    g064 = case_map.get("g064")
    if not g064:
        errors.append("g064 not found in gold_questions.yaml")
    else:
        elig = classify_formal_case_eligibility(g064, "gold")
        results["g064"] = {
            "valid": True,
            "classification": elig["classification"],
            "language": g064.get("language"),
            "excluded": True,
            "reason": elig["reason"],
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
    """Audit mechanical coverage of model_factory_theory symbol components."""
    from panda_agent.config import load_query_expansions
    from panda_agent.d3_structured import select_matching_query_expansions

    qe = load_query_expansions(project_root / QUERY_EXPANSIONS_PATH)
    case_map = {q["id"]: q for q in gold_questions}

    matching_info: dict[str, Any] = {}
    for cid in FROZEN_FORMAL_CASE_ORDER:
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

    component_coverage: dict[str, dict[str, Any]] = {}
    for sym in ORIGINAL_MODEL_FACTORY_THEORY_SYMBOLS:
        direct_cases: list[dict[str, Any]] = []
        for q in gold_questions:
            elig = classify_formal_case_eligibility(q, "gold")
            if not elig["formal_eligible"]:
                continue
            q_text = q.get("query", "")
            dec = select_matching_query_expansions(q_text, qe.rules, None)
            matched = [r.rule_id for r in dec.active_matching_rules]
            if TARGET_RULE_ID in matched:
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
                "coverage_status": "NO_DIRECT_TREATMENT_COVERAGE_IN_APPROVED_ENGLISH_GOLD",
                "direct_cases": [],
                "targetable": False,
            }

    covered_symbols = [s for s, d in component_coverage.items() if d["targetable"]]
    uncovered_symbols = [s for s, d in component_coverage.items() if not d["targetable"]]

    target_mask_matches = (
        covered_symbols == FROZEN_COVERED_SYMBOL_MASK
        and sorted(uncovered_symbols) == sorted(FROZEN_UNCOVERED_SYMBOL_HOLD_MASK)
    )

    return {
        "r1_target_mask_preserved": target_mask_matches,
        "covered_symbol_mask": covered_symbols,
        "uncovered_symbol_hold_mask": uncovered_symbols,
        "page_hint_hold_mask": FROZEN_PAGE_HINT_HOLD_MASK,
        "component_coverage": component_coverage,
        "matching_info": matching_info,
    }


def audit_page_hint_coverage_gap_approval_aware(project_root: Path) -> dict[str, Any]:
    """Audit page-hint coverage gap for model_factory_theory."""
    from panda_agent.config import load_query_expansions
    from panda_agent.d3_structured import select_matching_query_expansions

    qe = load_query_expansions(project_root / QUERY_EXPANSIONS_PATH)
    formal_eligible_candidates: list[dict[str, Any]] = []
    diagnostic_only_candidates: list[dict[str, Any]] = []
    excluded_candidates: list[dict[str, Any]] = []

    gold_questions = load_gold_questions(project_root)
    for q in gold_questions:
        q_text = q.get("query", "")
        dec = select_matching_query_expansions(q_text, qe.rules, None)
        matched = [r.rule_id for r in dec.active_matching_rules]
        if TARGET_RULE_ID in matched:
            elig = classify_formal_case_eligibility(q, "gold")
            intent = q.get("intent")
            allows_hints = intent in ("algorithm_theory", "algorithm_implementation")
            info = {
                "id": q.get("id"),
                "dataset": "gold",
                "language": q.get("language"),
                "intent": intent,
                "allows_hints": allows_hints,
                "review_status": q.get("review_status"),
                "classification": elig["classification"],
            }
            if elig["formal_eligible"] and allows_hints:
                formal_eligible_candidates.append(info)
            elif elig["classification"] == "EXCLUDED":
                excluded_candidates.append(info)

    novel_questions = load_novel_questions(project_root)
    for q in novel_questions:
        q_text = q.get("query") or q.get("question", "")
        dec = select_matching_query_expansions(q_text, qe.rules, None)
        matched = [r.rule_id for r in dec.active_matching_rules]
        if TARGET_RULE_ID in matched:
            elig = classify_formal_case_eligibility(q, "novel_dev")
            intent = q.get("intent")
            allows_hints = intent in ("algorithm_theory", "algorithm_implementation")
            info = {
                "id": q.get("id"),
                "dataset": "novel_dev",
                "language": q.get("language"),
                "intent": intent,
                "allows_hints": allows_hints,
                "review_status": q.get("review_status"),
                "classification": elig["classification"],
            }
            if elig["classification"] == "DIAGNOSTIC_ONLY":
                diagnostic_only_candidates.append(info)
            else:
                excluded_candidates.append(info)

    status_str = "OPEN"
    result_str = (
        "EXISTING_APPROVED_ENGLISH_CASE_FOUND"
        if formal_eligible_candidates
        else "NO_EXISTING_APPROVED_ENGLISH_CASE_FOUND"
    )

    return {
        "status": status_str,
        "result": result_str,
        "formal_eligible_candidates": formal_eligible_candidates,
        "diagnostic_only_candidates": diagnostic_only_candidates,
        "excluded_candidates": excluded_candidates,
        "explanation": (
            "No formally eligible English question matches model_factory_theory under an intent "
            "(algorithm_theory or algorithm_implementation) that allows paper page hints "
            "to survive production plan formation. Therefore pflueger_2017 [51, 57, 65] "
            "remain strictly on HOLD."
        ),
    }


# ---------------------------------------------------------------------------
# Provenance Typing Gate (Section 10)
# ---------------------------------------------------------------------------

def validate_origin_type_consistency(
    ledger: list[dict[str, Any]],
    known_rule_ids: set[str] | list[str] | None = None,
) -> tuple[bool, str | None]:
    """Validate origin-type consistency for every ledger entry.

    Verifies:
      1. Every provenance_origin_id has exactly one entry in origin_types.
      2. No unknown extra origin-type keys in origin_types.
      3. Reviewed rule origins use 'reviewed_expansion_rule'.
      4. accepted_analyzer_semantic_delta uses 'accepted_analyzer_semantic_output'.
      5. runtime_deterministic_override uses 'production_deterministic_override'.
      6. No unknown scientific origin ID is accepted.
      7. plan_present is of boolean type.
      8. contribution_ids are unique across entries.
    """
    seen_cids: set[str] = set()
    for idx, entry in enumerate(ledger):
        cid = entry.get("contribution_id")
        if not cid or not isinstance(cid, str):
            return False, f"Entry {idx} missing or invalid contribution_id: {cid}"
        if cid in seen_cids:
            return False, f"Duplicate contribution_id: {cid}"
        seen_cids.add(cid)

        if not isinstance(entry.get("plan_present"), bool):
            return False, f"Entry {cid} plan_present is not a boolean: {entry.get('plan_present')}"

        origins = entry.get("provenance_origin_ids")
        if not isinstance(origins, list):
            return False, f"Entry {cid} provenance_origin_ids is not a list: {origins}"

        origin_types = entry.get("origin_types")
        if not isinstance(origin_types, dict):
            return False, f"Entry {cid} origin_types is not a dict: {origin_types}"

        # 1 & 2: Exact key-set equivalence
        if set(origins) != set(origin_types.keys()):
            return False, (
                f"Entry {cid} provenance_origin_ids {origins} and origin_types keys "
                f"{list(origin_types.keys())} do not match exactly."
            )

        for orig_id in origins:
            orig_type = origin_types[orig_id]
            if orig_id == ORIGIN_ACCEPTED_ANALYZER_DELTA:
                if orig_type != ORIGIN_TYPE_ANALYZER_DELTA:
                    return False, (
                        f"Entry {cid} origin {orig_id} has wrong type {orig_type}, "
                        f"expected {ORIGIN_TYPE_ANALYZER_DELTA}"
                    )
            elif orig_id == ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE:
                if orig_type != ORIGIN_TYPE_RUNTIME_OVERRIDE:
                    return False, (
                        f"Entry {cid} origin {orig_id} has wrong type {orig_type}, "
                        f"expected {ORIGIN_TYPE_RUNTIME_OVERRIDE}"
                    )
            else:
                if known_rule_ids is not None and orig_id not in known_rule_ids:
                    return False, f"Entry {cid} contains unknown scientific origin ID: {orig_id}"
                if orig_type != ORIGIN_TYPE_REVIEWED_RULE:
                    return False, (
                        f"Entry {cid} rule origin {orig_id} has wrong type {orig_type}, "
                        f"expected {ORIGIN_TYPE_REVIEWED_RULE}"
                    )

    return True, None


# ---------------------------------------------------------------------------
# Enforceable Persistence-Before-Gate State Contract (Section 15-16)
# ---------------------------------------------------------------------------

STATE_ACQUIRED = "ACQUIRED"
STATE_PERSISTED = "PERSISTED"
STATE_GATED = "GATED"
STATE_RETRIEVED = "RETRIEVED"

VALID_STATE_TRANSITIONS: dict[str, list[str]] = {
    STATE_ACQUIRED: [STATE_PERSISTED],
    STATE_PERSISTED: [STATE_GATED],
    STATE_GATED: [STATE_RETRIEVED],
    STATE_RETRIEVED: [],
}


def transition_execution_state(current_state: str, next_state: str) -> str:
    """Validate and execute a formal lifecycle state transition."""
    allowed = VALID_STATE_TRANSITIONS.get(current_state)
    if allowed is None:
        raise StateTransitionError(f"Unknown current execution state: {current_state}")
    if next_state not in allowed:
        raise StateTransitionError(
            f"Invalid state transition: {current_state} -> {next_state}. "
            f"Allowed transitions from {current_state}: {allowed}"
        )
    return next_state


def validate_persistence_receipt(receipt: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate that a persistence receipt contains all required fields."""
    if not isinstance(receipt, dict):
        return False, "Persistence receipt must be a dictionary."
    required_keys = [
        "case_id",
        "persisted_record_path",
        "persistence_completed",
        "canonical_plan",
        "contribution_ledger",
        "provider_accounting",
    ]
    for k in required_keys:
        if k not in receipt:
            return False, f"Missing required key in persistence receipt: {k}"
    if receipt.get("persistence_completed") is not True:
        return False, "persistence_completed must be True."
    if not isinstance(receipt.get("canonical_plan"), dict) or not receipt["canonical_plan"]:
        return False, "canonical_plan must be a non-empty dictionary."
    if not isinstance(receipt.get("contribution_ledger"), list) or not receipt["contribution_ledger"]:
        return False, "contribution_ledger must be a non-empty list."
    if not isinstance(receipt.get("provider_accounting"), dict):
        return False, "provider_accounting must be a dictionary."
    return True, None


def audit_persistence_before_gate_contract() -> dict[str, Any]:
    """Mechanically audit the persistence-before-gate state contract."""
    acquired_to_gated_rejected = False
    try:
        transition_execution_state(STATE_ACQUIRED, STATE_GATED)
    except StateTransitionError:
        acquired_to_gated_rejected = True

    acquired_to_retrieved_rejected = False
    try:
        transition_execution_state(STATE_ACQUIRED, STATE_RETRIEVED)
    except StateTransitionError:
        acquired_to_retrieved_rejected = True

    persisted_to_retrieved_rejected = False
    try:
        transition_execution_state(STATE_PERSISTED, STATE_RETRIEVED)
    except StateTransitionError:
        persisted_to_retrieved_rejected = True

    valid_sequence_accepted = False
    try:
        s1 = transition_execution_state(STATE_ACQUIRED, STATE_PERSISTED)
        s2 = transition_execution_state(s1, STATE_GATED)
        s3 = transition_execution_state(s2, STATE_RETRIEVED)
        valid_sequence_accepted = (s3 == STATE_RETRIEVED)
    except StateTransitionError:
        valid_sequence_accepted = False

    ok_empty, _ = validate_persistence_receipt({})
    missing_receipt_rejected = not ok_empty

    incomplete_receipt = {
        "case_id": "g031",
        "persisted_record_path": "path/to/record.json",
        "persistence_completed": True,
    }
    ok_inc, _ = validate_persistence_receipt(incomplete_receipt)
    incomplete_receipt_rejected = not ok_inc

    valid_receipt = {
        "case_id": "g031",
        "persisted_record_path": "evaluation/d4_a9_raw_plans/g031_plan.json",
        "persistence_completed": True,
        "canonical_plan": {"intent": "api", "symbols": ["model/PndLmdModelFactory.cxx"]},
        "contribution_ledger": [{"contribution_id": "symbol::model/PndLmdModelFactory.cxx"}],
        "provider_accounting": {"model_id": "gemini-3.8-flash", "tokens": 100},
    }
    ok_val, _ = validate_persistence_receipt(valid_receipt)
    valid_receipt_accepted = ok_val

    all_verified = (
        acquired_to_gated_rejected
        and acquired_to_retrieved_rejected
        and persisted_to_retrieved_rejected
        and valid_sequence_accepted
        and missing_receipt_rejected
        and incomplete_receipt_rejected
        and valid_receipt_accepted
    )

    return {
        "persistence_before_gate_contract_verified": all_verified,
        "acquired_to_gated_rejected": acquired_to_gated_rejected,
        "acquired_to_retrieved_rejected": acquired_to_retrieved_rejected,
        "persisted_to_retrieved_rejected": persisted_to_retrieved_rejected,
        "valid_sequence_accepted": valid_sequence_accepted,
        "missing_receipt_rejected": missing_receipt_rejected,
        "incomplete_receipt_rejected": incomplete_receipt_rejected,
        "valid_receipt_accepted": valid_receipt_accepted,
    }


# ---------------------------------------------------------------------------
# Pure A5 Authority Wrappers & Projection (Section 7)
# ---------------------------------------------------------------------------

def build_real_contribution_ledger(
    canonical_plan: dict[str, Any],
    rules_by_id: dict[str, dict[str, Any]],
    matched_rule_ids: list[str],
) -> list[dict[str, Any]]:
    """Authoritative D4-A5 contribution ledger implementation.

    Binds strictly to frozen A5 build_contribution_ledger. Silent fallback is prohibited.
    """
    a5 = load_a5_authority()
    return a5.build_contribution_ledger(canonical_plan, rules_by_id, matched_rule_ids)


def classify_component_applicability(
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    configured_entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Authoritative D4-A5 component-level applicability classifier.

    Binds strictly to frozen A5 classify_component_applicability. Silent fallback is prohibited.
    """
    a5 = load_a5_authority()
    return a5.classify_component_applicability(canonical_plan, ledger, configured_entries)


def project_component_sensitive_treatment(
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    covered_symbol_mask: list[str],
    matched_rule_ids: list[str],
    *,
    case_id: str = "g031",
    expected_case_role: str = "TREATMENT",
    masks: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Thin wrapper around frozen A5 build_retirement_projection_r1 using component-sensitive mask.

    Subtraction and provenance semantics remain entirely A5 authority.
    """
    a5 = load_a5_authority()
    effective_masks = masks or COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS

    # 1. Full ledger coverage validation
    ok_cov, err_cov = a5.validate_ledger_coverage(canonical_plan, ledger)
    if not ok_cov:
        raise ValueError(f"Ledger coverage incomplete: {err_cov}")

    # 2. Origin typing consistency
    ok_orig, err_orig = validate_origin_type_consistency(ledger)
    if not ok_orig:
        raise ValueError(f"Origin typing inconsistent: {err_orig}")

    target_rule_matched = TARGET_RULE_ID in matched_rule_ids
    if expected_case_role == "CONTROL" and target_rule_matched:
        raise ValueError(f"Control case matched target rule: {matched_rule_ids}")

    # 3. Build component mask entries using A5 helper
    mask_entries = a5.build_batch2_mask_entries(
        case_id,
        [r for r in matched_rule_ids if r in effective_masks],
        masks=effective_masks,
    )

    # 4. Classify component applicability using A5 helper
    component_receipts, summary = a5.classify_component_applicability(
        canonical_plan, ledger, mask_entries
    )

    if any(r["applicability_status"] == APPLICABILITY_AMBIGUOUS for r in component_receipts):
        raise ValueError("Ambiguous component applicability in treatment construction")

    # 5. Build retirement projection using A5 helper
    projected_plan, receipts = a5.build_retirement_projection_r1(
        canonical_plan,
        ledger,
        component_receipts,
        [r for r in matched_rule_ids if r in effective_masks],
        masks=effective_masks,
    )

    # Verification: canonical plan was never mutated and held components untouched
    for sym in FROZEN_UNCOVERED_SYMBOL_HOLD_MASK:
        if sym in (canonical_plan.get("symbols") or []):
            if sym not in (projected_plan.get("symbols") or []):
                raise ValueError(f"Held DPM symbol was improperly modified: {sym}")

    return projected_plan, receipts


def construct_component_sensitive_treatment_or_raise(
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    matched_rule_ids: list[str],
    case_id: str,
    *,
    case_role: str = "TREATMENT",
    masks: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fail-closed treatment constructor for D4-A9 targeted revalidation.

    Uses real A5 pure helpers under component-sensitive mask.
    Fails closed with TargetedValidationProtocolError (Level 1 INVALID_PROTOCOL)
    upon any protocol, provenance, or construction defect.
    """
    try:
        a5 = load_a5_authority()
    except Exception as exc:
        raise TargetedValidationProtocolError(f"A5 authority unavailable: {exc}") from exc

    effective_masks = masks or COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS

    # Full ledger coverage check
    ok_cov, err_cov = a5.validate_ledger_coverage(canonical_plan, ledger)
    if not ok_cov:
        raise TargetedValidationProtocolError(f"Ledger coverage incomplete: {err_cov}")

    # Origin typing check
    ok_orig, err_orig = validate_origin_type_consistency(ledger)
    if not ok_orig:
        raise TargetedValidationProtocolError(f"Origin typing malformed: {err_orig}")

    canonical_before = copy.deepcopy(canonical_plan)

    if case_role == "TREATMENT":
        if TARGET_RULE_ID not in matched_rule_ids:
            raise TargetedValidationProtocolError("Treatment case did not match target rule")

        mask_entries = a5.build_batch2_mask_entries(
            case_id,
            [r for r in matched_rule_ids if r in effective_masks],
            masks=effective_masks,
        )
        component_receipts, _ = a5.classify_component_applicability(
            canonical_plan, ledger, mask_entries
        )

        for r in component_receipts:
            if r["applicability_status"] == APPLICABILITY_AMBIGUOUS:
                raise TargetedValidationProtocolError(
                    f"Component applicability AMBIGUOUS_INVALID: {r.get('provenance_ambiguity_reason')}"
                )

        target_receipts = [
            r for r in component_receipts if r["component_value"] in FROZEN_COVERED_SYMBOL_MASK
        ]
        if not target_receipts or target_receipts[0]["applicability_status"] != APPLICABILITY_ACTIVE:
            raise TargetedValidationProtocolError("Covered target symbol not ACTIVE_IDENTIFIABLE")

        try:
            projected_plan, receipts = a5.build_retirement_projection_r1(
                canonical_plan,
                ledger,
                component_receipts,
                [r for r in matched_rule_ids if r in effective_masks],
                masks=effective_masks,
            )
        except Exception as exc:
            raise TargetedValidationProtocolError(f"Projection failed: {exc}") from exc

        # Verify held components untouched
        for sym in FROZEN_UNCOVERED_SYMBOL_HOLD_MASK:
            if (sym in (canonical_plan.get("symbols") or [])) != (sym in (projected_plan.get("symbols") or [])):
                raise TargetedValidationProtocolError(f"Held DPM symbol mutated in projection: {sym}")
        for paper, pages in FROZEN_PAGE_HINT_HOLD_MASK.items():
            orig_pages = (canonical_plan.get("paper_page_hints") or {}).get(paper, [])
            proj_pages = (projected_plan.get("paper_page_hints") or {}).get(paper, [])
            if sorted(orig_pages) != sorted(proj_pages):
                raise TargetedValidationProtocolError(f"Held page hint mutated: {paper}")

        # Verify canonical plan was not mutated
        if canonical_plan != canonical_before:
            raise TargetedValidationProtocolError("Canonical plan was mutated during projection")

        return projected_plan, receipts

    elif case_role == "CONTROL":
        if TARGET_RULE_ID in matched_rule_ids:
            raise TargetedValidationProtocolError("Control case unexpectedly matched target rule")

        mask_entries = a5.build_batch2_mask_entries(
            case_id,
            [r for r in matched_rule_ids if r in effective_masks],
            masks=effective_masks,
        )
        component_receipts, _ = a5.classify_component_applicability(
            canonical_plan, ledger, mask_entries
        )
        projected_plan, receipts = a5.build_retirement_projection_r1(
            canonical_plan,
            ledger,
            component_receipts,
            [r for r in matched_rule_ids if r in effective_masks],
            masks=effective_masks,
        )
        if projected_plan != canonical_plan:
            raise TargetedValidationProtocolError("Control case received non-zero target subtraction")

        return projected_plan, receipts

    else:
        raise TargetedValidationProtocolError(f"Unknown case role: {case_role}")


# ---------------------------------------------------------------------------
# Mechanical A5 Equivalence Audit (Section 8, 11, 12, 27)
# ---------------------------------------------------------------------------

def audit_a5_execution_semantic_compatibility(
    rules_by_id: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute real A5 pure helpers on deterministic fixtures to prove semantic compatibility."""
    try:
        a5 = load_a5_authority()
    except Exception as exc:
        return {
            "authority_loaded": False,
            "required_helpers_present": False,
            "ledger_coverage_verified": False,
            "origin_type_consistency_verified": False,
            "applicability_equivalence_verified": False,
            "sole_origin_projection_verified": False,
            "independent_rule_origin_verified": False,
            "analyzer_origin_verified": False,
            "runtime_origin_semantics_verified": False,
            "held_component_preservation_verified": False,
            "control_noop_verified": False,
            "a5_provenance_compatibility_verified": False,
            "a5_applicability_compatibility_verified": False,
            "a5_projection_compatibility_verified": False,
            "non_rule_origin_preservation_verified": False,
        }

    missing_helpers = [h for h in A5_REQUIRED_HELPERS if not hasattr(a5, h)]
    if missing_helpers:
        return {
            "authority_loaded": True,
            "required_helpers_present": False,
            "missing_helpers": missing_helpers,
            "ledger_coverage_verified": False,
            "origin_type_consistency_verified": False,
            "applicability_equivalence_verified": False,
            "sole_origin_projection_verified": False,
            "independent_rule_origin_verified": False,
            "analyzer_origin_verified": False,
            "runtime_origin_semantics_verified": False,
            "held_component_preservation_verified": False,
            "control_noop_verified": False,
            "a5_provenance_compatibility_verified": False,
            "a5_applicability_compatibility_verified": False,
            "a5_projection_compatibility_verified": False,
            "non_rule_origin_preservation_verified": False,
            "error": f"Missing required A5 helpers: {missing_helpers}",
        }

    mock_rules: dict[str, Any] = {
        TARGET_RULE_ID: {
            "symbols": [
                "model/PndLmdModelFactory.cxx",
                "model/PndLmdDPMAngModel1D.cxx",
                "model/PndLmdDPMAngModel2D.cxx",
            ],
            "concepts": ["DPM model acceptance resolution composition"],
            "repositories": ["luminosityfit"],
            "paper_page_hints": {"pflueger_2017": [51, 57, 65]},
        },
        "model_factory_acceptance_methods": {
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "repositories": ["luminosityfit"],
            "paper_page_hints": {},
        },
        "r_control": {
            "symbols": ["data/PndLmdAcceptance.cxx"],
            "concepts": [],
            "repositories": ["pandaroot"],
            "paper_page_hints": {},
        },
    }
    if rules_by_id:
        mock_rules.update(rules_by_id)

    # Fixture 1: Sole selected origin on model/PndLmdModelFactory.cxx
    plan_sole = {
        "intent": "api",
        "symbols": ["model/PndLmdModelFactory.cxx", "model/PndLmdDPMAngModel1D.cxx"],
        "concepts": ["DPM model acceptance resolution composition"],
        "target_repositories": ["luminosityfit"],
        "paper_page_hints": {"pflueger_2017": [51]},
    }
    ledger_sole = a5.build_contribution_ledger(plan_sole, mock_rules, [TARGET_RULE_ID])
    ok_cov, err_cov = a5.validate_ledger_coverage(plan_sole, ledger_sole)
    ok_orig, err_orig = validate_origin_type_consistency(ledger_sole, set(mock_rules.keys()))
    mask_entries_sole = a5.build_batch2_mask_entries(
        "g031", [TARGET_RULE_ID], masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
    )
    receipts_sole, summary_sole = a5.classify_component_applicability(
        plan_sole, ledger_sole, mask_entries_sole
    )
    proj_sole, rec_sole = a5.build_retirement_projection_r1(
        plan_sole, ledger_sole, receipts_sole, [TARGET_RULE_ID], masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
    )
    sole_origin_verified = (
        ok_cov
        and ok_orig
        and summary_sole["active"] == 1
        and "model/PndLmdModelFactory.cxx" not in proj_sole["symbols"]
        and "model/PndLmdDPMAngModel1D.cxx" in proj_sole["symbols"]
        and proj_sole["paper_page_hints"] == {"pflueger_2017": [51]}
    )

    # Fixture 2: Independent reviewed-rule origin
    ledger_indep = a5.build_contribution_ledger(
        plan_sole, mock_rules, [TARGET_RULE_ID, "model_factory_acceptance_methods"]
    )
    receipts_indep, summary_indep = a5.classify_component_applicability(
        plan_sole, ledger_indep, mask_entries_sole
    )
    proj_indep, _ = a5.build_retirement_projection_r1(
        plan_sole, ledger_indep, receipts_indep, [TARGET_RULE_ID], masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
    )
    indep_rule_verified = (
        summary_indep["active"] == 1
        and "model/PndLmdModelFactory.cxx" in proj_indep["symbols"]
    )

    # Fixture 3: Analyzer delta origin
    plan_analyzer = copy.deepcopy(plan_sole)
    plan_analyzer["analysis_diagnostics"] = {
        "analyzer_accepted_semantic_delta": {
            "symbols": ["model/PndLmdModelFactory.cxx"]
        }
    }
    ledger_analyzer = a5.build_contribution_ledger(plan_analyzer, mock_rules, [TARGET_RULE_ID])
    receipts_analyzer, summary_analyzer = a5.classify_component_applicability(
        plan_analyzer, ledger_analyzer, mask_entries_sole
    )
    proj_analyzer, _ = a5.build_retirement_projection_r1(
        plan_analyzer, ledger_analyzer, receipts_analyzer, [TARGET_RULE_ID], masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
    )
    analyzer_origin_verified = (
        summary_analyzer["active"] == 1
        and "model/PndLmdModelFactory.cxx" in proj_analyzer["symbols"]
    )

    # Fixture 4: Runtime deterministic override (A5 defines runtime override on paper_page_hints li_2026: 141)
    plan_runtime = copy.deepcopy(plan_sole)
    plan_runtime["paper_page_hints"] = {"li_2026": [141]}
    ledger_runtime = a5.build_contribution_ledger(plan_runtime, mock_rules, [TARGET_RULE_ID])
    runtime_entry = [e for e in ledger_runtime if e["kind"] == "paper_page_hint" and e["value"] == "li_2026#141"]
    has_runtime_origin = (
        len(runtime_entry) == 1
        and ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE in runtime_entry[0]["provenance_origin_ids"]
        and runtime_entry[0]["origin_types"].get(ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE) == ORIGIN_TYPE_RUNTIME_OVERRIDE
    )
    receipts_runtime, _ = a5.classify_component_applicability(
        plan_runtime, ledger_runtime, mask_entries_sole
    )
    proj_runtime, _ = a5.build_retirement_projection_r1(
        plan_runtime, ledger_runtime, receipts_runtime, [TARGET_RULE_ID], masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
    )
    runtime_semantics_verified = (
        has_runtime_origin
        and proj_runtime["paper_page_hints"] == {"li_2026": [141]}
    )

    # Fixture 5: Held DPM symbols and page hints preservation
    plan_held = {
        "intent": "api",
        "symbols": [
            "model/PndLmdModelFactory.cxx",
            "model/PndLmdDPMAngModel1D.cxx",
            "model/PndLmdDPMAngModel2D.cxx",
        ],
        "concepts": ["DPM model acceptance resolution composition"],
        "target_repositories": ["luminosityfit"],
        "paper_page_hints": {"pflueger_2017": [51, 57, 65]},
    }
    ledger_held = a5.build_contribution_ledger(plan_held, mock_rules, [TARGET_RULE_ID])
    mask_entries_held = a5.build_batch2_mask_entries(
        "g031", [TARGET_RULE_ID], masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
    )
    receipts_held, _ = a5.classify_component_applicability(plan_held, ledger_held, mask_entries_held)
    proj_held, _ = a5.build_retirement_projection_r1(
        plan_held, ledger_held, receipts_held, [TARGET_RULE_ID], masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
    )
    held_preservation_verified = (
        "model/PndLmdModelFactory.cxx" not in proj_held["symbols"]
        and "model/PndLmdDPMAngModel1D.cxx" in proj_held["symbols"]
        and "model/PndLmdDPMAngModel2D.cxx" in proj_held["symbols"]
        and proj_held["paper_page_hints"] == {"pflueger_2017": [51, 57, 65]}
    )

    # Fixture 6: Control no-op
    plan_ctrl = {
        "intent": "api",
        "symbols": ["data/PndLmdAcceptance.cxx"],
        "concepts": [],
        "target_repositories": ["pandaroot"],
        "paper_page_hints": {},
    }
    ledger_ctrl = a5.build_contribution_ledger(plan_ctrl, mock_rules, [])
    mask_entries_ctrl = a5.build_batch2_mask_entries("g032", [], masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
    receipts_ctrl, summary_ctrl = a5.classify_component_applicability(plan_ctrl, ledger_ctrl, mask_entries_ctrl)
    proj_ctrl, _ = a5.build_retirement_projection_r1(
        plan_ctrl, ledger_ctrl, receipts_ctrl, [], masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
    )
    control_noop_verified = (
        len(mask_entries_ctrl) == 0
        and summary_ctrl["active"] == 0
        and proj_ctrl == plan_ctrl
    )

    # Fixture 7: Inactive applicability fixture
    plan_inact = {
        "intent": "api",
        "symbols": ["model/PndLmdModelFactory.cxx"],
        "concepts": [],
        "target_repositories": ["luminosityfit"],
        "paper_page_hints": {},
    }
    ledger_inact = a5.build_contribution_ledger(plan_inact, mock_rules, ["model_factory_acceptance_methods"])
    receipts_inact, summary_inact = a5.classify_component_applicability(
        plan_inact, ledger_inact, mask_entries_sole
    )
    inactive_applicability_verified = (
        summary_inact["inactive"] == 1
        and receipts_inact[0]["applicability_status"] == APPLICABILITY_INACTIVE
    )

    # Fixture 8: Ambiguous applicability fixture
    ledger_ambig = copy.deepcopy(ledger_inact)
    ledger_ambig[0]["plan_present"] = False  # Contradicts plan_inact
    receipts_ambig, summary_ambig = a5.classify_component_applicability(
        plan_inact, ledger_ambig, mask_entries_sole
    )
    ambiguous_applicability_verified = (
        summary_ambig["ambiguous"] == 1
        and receipts_ambig[0]["applicability_status"] == APPLICABILITY_AMBIGUOUS
    )

    applicability_equivalence_verified = (
        summary_sole["active"] == 1
        and inactive_applicability_verified
        and ambiguous_applicability_verified
    )

    a5_provenance_compat = (
        sole_origin_verified
        and indep_rule_verified
        and analyzer_origin_verified
        and runtime_semantics_verified
    )

    a5_projection_compat = (
        a5_provenance_compat
        and held_preservation_verified
        and control_noop_verified
    )

    return {
        "authority_loaded": True,
        "required_helpers_present": True,
        "ledger_coverage_verified": ok_cov,
        "origin_type_consistency_verified": ok_orig,
        "applicability_equivalence_verified": applicability_equivalence_verified,
        "sole_origin_projection_verified": sole_origin_verified,
        "independent_rule_origin_verified": indep_rule_verified,
        "analyzer_origin_verified": analyzer_origin_verified,
        "runtime_origin_semantics_verified": runtime_semantics_verified,
        "held_component_preservation_verified": held_preservation_verified,
        "control_noop_verified": control_noop_verified,
        "a5_provenance_compatibility_verified": a5_provenance_compat,
        "a5_applicability_compatibility_verified": applicability_equivalence_verified,
        "a5_projection_compatibility_verified": a5_projection_compat,
        "non_rule_origin_preservation_verified": (analyzer_origin_verified and runtime_semantics_verified and indep_rule_verified),
    }


# ---------------------------------------------------------------------------
# Complete Plan Reusability Audit (Section 17-26)
# ---------------------------------------------------------------------------

def check_plan_record_complete_contract(
    record: dict[str, Any],
    expected_case_id: str,
    gold_q: dict[str, Any],
    project_root: Path,
    rules_by_id: dict[str, Any] | None = None,
) -> tuple[bool, str, str]:
    """Check whether a plan candidate satisfies the complete frozen plan contract.

    Returns:
      (is_compatible, classification_code, failure_reason)
    """
    if not isinstance(record, dict):
        return False, PLAN_REUSE_INCOMPLETE, "RECORD_NOT_DICT"

    # 1. Exact case_id
    cid = record.get("case_id") or record.get("question_id") or record.get("id")
    if cid != expected_case_id:
        return False, PLAN_REUSE_INCOMPLETE, f"CASE_ID_MISMATCH: {cid} != {expected_case_id}"

    # 2. Exact question text
    expected_query = gold_q.get("query", "").strip()
    actual_query = (record.get("question") or record.get("query") or "").strip()
    if actual_query != expected_query:
        return False, PLAN_REUSE_BEHAVIOR_INCOMPATIBLE, "QUESTION_TEXT_MISMATCH"

    # 3. Canonical plan presence and schema
    canonical = record.get("canonical_plan") or record.get("plan")
    if not isinstance(canonical, dict):
        return False, PLAN_REUSE_INCOMPLETE, "CANONICAL_PLAN_MISSING_OR_NOT_DICT"
    for field in ("symbols", "concepts", "target_repositories", "paper_page_hints"):
        if field not in canonical:
            return False, PLAN_REUSE_INCOMPLETE, f"CANONICAL_PLAN_FIELD_MISSING: {field}"

    # 4. Canonical serialization internal consistency (Section 18)
    canonical_ser = record.get("canonical_serialization")
    if not canonical_ser or not isinstance(canonical_ser, str):
        return False, PLAN_REUSE_SERIALIZATION_INCONSISTENT, "CANONICAL_SERIALIZATION_MISSING"
    try:
        parsed_ser = json.loads(canonical_ser)
    except Exception as e:
        return False, PLAN_REUSE_SERIALIZATION_INCONSISTENT, f"CANONICAL_SERIALIZATION_INVALID_JSON: {e}"
    if parsed_ser != canonical:
        return False, PLAN_REUSE_SERIALIZATION_INCONSISTENT, "CANONICAL_SERIALIZATION_DOES_NOT_MATCH_PLAN"

    # 5. Plan signature internal consistency (Section 19)
    sig = record.get("plan_signature")
    if not sig:
        return False, PLAN_REUSE_INCOMPLETE, "PLAN_SIGNATURE_MISSING"
    a5 = load_a5_authority()
    computed_sig, _ = a5.compute_plan_signature(canonical)
    if sig != computed_sig:
        return False, PLAN_REUSE_SIGNATURE_MISMATCH, f"SIGNATURE_MISMATCH: stored {sig} != computed {computed_sig}"

    # 6. Provider model contract explicit validation (Section 20)
    accounting = record.get("provider_accounting") or record.get("accounting")
    if not isinstance(accounting, dict):
        return False, PLAN_REUSE_INCOMPLETE, "PROVIDER_ACCOUNTING_MISSING"

    model_id = record.get("model_id") or accounting.get("model_id")
    if model_id != "gemini-3.8-flash":
        return False, PLAN_REUSE_PROVIDER_CONTRACT_INCOMPATIBLE, f"MODEL_INCOMPATIBLE: {model_id} != gemini-3.8-flash"

    temperature = record.get("temperature") if "temperature" in record else accounting.get("temperature")
    if temperature is None:
        return False, PLAN_REUSE_PROVIDER_CONTRACT_INCOMPLETE, "TEMPERATURE_MISSING"
    if float(temperature) != 0.0:
        return False, PLAN_REUSE_PROVIDER_CONTRACT_INCOMPATIBLE, f"TEMPERATURE_INCOMPATIBLE: {temperature} != 0.0"

    location = record.get("location") if "location" in record else accounting.get("location")
    if location is None:
        return False, PLAN_REUSE_PROVIDER_CONTRACT_INCOMPLETE, "LOCATION_MISSING"
    if location != "global":
        return False, PLAN_REUSE_PROVIDER_CONTRACT_INCOMPATIBLE, f"LOCATION_INCOMPATIBLE: {location} != global"

    retries = record.get("retries") if "retries" in record else accounting.get("retries")
    if retries is None:
        return False, PLAN_REUSE_PROVIDER_CONTRACT_INCOMPLETE, "RETRIES_MISSING"
    if int(retries) != 0:
        return False, PLAN_REUSE_PROVIDER_CONTRACT_INCOMPATIBLE, f"RETRY_POLICY_INCOMPATIBLE: {retries} != 0"

    # 7. Matched-rule behavior compatibility (Section 21)
    matched_rules_hist = record.get("matched_rule_identities") or record.get("matched_rules")
    if matched_rules_hist is None or not isinstance(matched_rules_hist, list):
        return False, PLAN_REUSE_BEHAVIOR_INCOMPATIBLE, "MATCHED_RULE_IDENTITIES_MISSING"

    from panda_agent.config import load_query_expansions
    from panda_agent.d3_structured import select_matching_query_expansions

    qe = load_query_expansions(project_root / QUERY_EXPANSIONS_PATH)
    cur_dec = select_matching_query_expansions(gold_q.get("query", ""), qe.rules, None)
    cur_matched = [r.rule_id for r in cur_dec.active_matching_rules]
    if sorted(matched_rules_hist) != sorted(cur_matched):
        return False, PLAN_REUSE_BEHAVIOR_INCOMPATIBLE, f"MATCHED_RULES_DRIFT: hist {matched_rules_hist} != cur {cur_matched}"

    # 8. Complete contribution ledger and origin typing
    ledger = record.get("contribution_ledger") or record.get("contributions")
    if not isinstance(ledger, list) or len(ledger) == 0:
        return False, PLAN_REUSE_PROVENANCE_INCOMPATIBLE, "CONTRIBUTION_LEDGER_MISSING_OR_EMPTY"

    ok_cov, err_cov = a5.validate_ledger_coverage(canonical, ledger)
    if not ok_cov:
        return False, PLAN_REUSE_PROVENANCE_INCOMPATIBLE, f"LEDGER_COVERAGE_FAILED: {err_cov}"

    ok_orig, err_orig = validate_origin_type_consistency(ledger, set(cur_matched))
    if not ok_orig:
        return False, PLAN_REUSE_PROVENANCE_INCOMPATIBLE, f"ORIGIN_TYPES_INCONSISTENT: {err_orig}"

    # 9. Provenance origin receipts & applicability receipts
    if "provenance_origin_receipts" not in record and "provenance_receipts" not in record:
        return False, PLAN_REUSE_PROVENANCE_INCOMPATIBLE, "PROVENANCE_ORIGIN_RECEIPTS_MISSING"
    if "component_applicability_receipts" not in record and "applicability_receipts" not in record:
        return False, PLAN_REUSE_PROVENANCE_INCOMPATIBLE, "COMPONENT_APPLICABILITY_RECEIPTS_MISSING"

    return True, PLAN_REUSE_COMPATIBLE, "ALL_COMPATIBILITY_CHECKS_PASSED"


def audit_plan_reusability(
    project_root: Path,
    formal_cohort: list[str] | None = None,
) -> dict[str, Any]:
    """Perform deterministic discovery and audit of plan-bearing artifacts."""
    if formal_cohort is None:
        formal_cohort = FROZEN_FORMAL_CASE_ORDER

    gold_questions = load_gold_questions(project_root)
    gold_map = {q["id"]: q for q in gold_questions}

    eval_dir = project_root / "evaluation"
    discovered = sorted([str(p.relative_to(project_root)).replace("\\", "/") for p in eval_dir.glob("*.json")])

    considered: list[str] = []
    scanned: list[str] = []
    rejected_and_reason: dict[str, str] = {}
    found_candidates_by_case: dict[str, list[dict[str, Any]]] = {cid: [] for cid in formal_cohort}

    for rel_path in discovered:
        considered.append(rel_path)
        if "holdout" in rel_path or "novel_holdout" in rel_path:
            rejected_and_reason[rel_path] = "PROTECTED_OR_HOLDOUT_ASSET"
            continue

        p = project_root / rel_path
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            rejected_and_reason[rel_path] = f"JSON_LOAD_ERROR: {e}"
            continue

        has_plans = False
        extracted_records: list[dict[str, Any]] = []

        if isinstance(data, dict):
            for key in (
                "plans",
                "canonical_plans",
                "raw_plans",
                "plan_samples",
                "cases",
                "phase_p_slots_7",
                "raw_plan_records",
                "draws",
                "slots",
            ):
                if key in data:
                    val = data[key]
                    if isinstance(val, list):
                        extracted_records.extend(val)
                        has_plans = True
                    elif isinstance(val, dict):
                        extracted_records.extend(list(val.values()))
                        has_plans = True
            if "HIST_A2_BEFORE_PLAN" in data and isinstance(data["HIST_A2_BEFORE_PLAN"], dict):
                extracted_records.append(data["HIST_A2_BEFORE_PLAN"])
                has_plans = True
            if "HIST_A2_AFTER_PLAN" in data and isinstance(data["HIST_A2_AFTER_PLAN"], dict):
                extracted_records.append(data["HIST_A2_AFTER_PLAN"])
                has_plans = True
        elif isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict) and ("canonical_plan" in data[0] or "plan" in data[0]):
                extracted_records.extend(data)
                has_plans = True

        if has_plans:
            scanned.append(rel_path)
            for rec in extracted_records:
                if isinstance(rec, dict):
                    cid = rec.get("case_id") or rec.get("question_id") or rec.get("id")
                    if cid in found_candidates_by_case:
                        found_candidates_by_case[cid].append({
                            "source_artifact": rel_path,
                            "record": rec,
                        })
        else:
            rejected_and_reason[rel_path] = "NO_EXPOSED_PLAN_RECORD_SCHEMA"

    # Evaluate each formal case
    reusability_results: dict[str, str] = {}
    rejection_reasons_by_case: dict[str, list[dict[str, str]]] = {}
    reusable_plan_case_ids: list[str] = []
    fresh_plan_case_ids: list[str] = []

    for cid in formal_cohort:
        candidates = found_candidates_by_case[cid]
        gold_q = gold_map.get(cid, {})

        if not candidates:
            reusability_results[cid] = PLAN_REUSE_NO_CANDIDATE
            rejection_reasons_by_case[cid] = [{"reason": "NO_FROZEN_PLAN_RECORD_FOUND_IN_SCANNED_ARTIFACTS"}]
            fresh_plan_case_ids.append(cid)
        else:
            compatible_found = False
            case_rejections: list[dict[str, str]] = []
            for cand in candidates:
                src = cand["source_artifact"]
                rec = cand["record"]
                is_compat, code, detail = check_plan_record_complete_contract(rec, cid, gold_q, project_root)
                if is_compat:
                    compatible_found = True
                    break
                case_rejections.append({
                    "source_artifact": src,
                    "classification": code,
                    "reason": detail,
                })

            if compatible_found:
                reusability_results[cid] = PLAN_REUSE_COMPATIBLE
                reusable_plan_case_ids.append(cid)
            else:
                primary_code = case_rejections[0]["classification"] if case_rejections else PLAN_REUSE_INCOMPLETE
                reusability_results[cid] = primary_code
                rejection_reasons_by_case[cid] = case_rejections
                fresh_plan_case_ids.append(cid)

    n = len(formal_cohort)
    r = len(reusable_plan_case_ids)
    f = n - r

    budget = {
        "N_formal_cases": n,
        "R_reusable_plans": r,
        "F_fresh_plans": f,
        "analyzer_calls": f,
        "embedding_calls": 2 * n,
        "reranker_calls": 2 * n,
        "qa_calls": 0,
        "verifier_calls": 0,
        "judge_calls": 0,
        "scientific_evaluator_calls": 0,
        "retries": 0,
        "total_logical_model_calls": f + 4 * n,
    }

    audit_complete = (
        len(reusability_results) == n
        and all(cid in reusability_results for cid in formal_cohort)
        and (r + f == n)
    )

    return {
        "artifacts_discovered": discovered,
        "artifacts_considered": considered,
        "artifacts_scanned": scanned,
        "artifacts_rejected_and_reason": rejected_and_reason,
        "reusability_results": reusability_results,
        "rejection_reasons_by_case": rejection_reasons_by_case,
        "reusable_plan_case_ids": reusable_plan_case_ids,
        "fresh_plan_case_ids": fresh_plan_case_ids,
        "plan_reusability_audit_complete": audit_complete,
        "total_formal_cases": n,
        "reusable_count": r,
        "fresh_count": f,
        "derived_provider_budget": budget,
    }


# ---------------------------------------------------------------------------
# Fail-Closed Evaluator Precedence (Section 14)
# ---------------------------------------------------------------------------

def evaluate_component_sensitive_hypothetical_outcome(
    covered_symbols: list[str],
    uncovered_hold_symbols: list[str],
    page_hint_hold: dict[str, list[int]],
    observed_case_outcomes: dict[str, Any],
    *,
    protocol_error: bool = False,
    malformed_treatment: bool = False,
    baseline_reproduced: bool = True,
    control_divergence: bool = False,
    safety_regression: bool = False,
) -> dict[str, Any]:
    """Fail-closed evaluator resolving outcomes with strict precedence.

    Precedence:
      Level 1: INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED
      Level 2: INCONCLUSIVE / ALL_COVERED_COMPONENT_BASELINES_NOT_REPRODUCED
      Level 3: PARTIAL / DEPENDENCY_OBSERVED_FOR_COVERED_COMPONENTS_RETAIN
      Level 4: FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION
      Level 5: INCONCLUSIVE / COVERED_COMPONENT_APPLICABILITY_INCOMPLETE
      Level 6: PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD
    """
    any_ambiguous = any(
        info.get("applicability") == APPLICABILITY_AMBIGUOUS
        for info in observed_case_outcomes.values()
    )

    # Level 1: Protocol / Provenance failure
    if protocol_error or malformed_treatment or any_ambiguous:
        return {
            "overall_outcome": OUTCOME_LEVEL_1_INVALID,
            "level": 1,
            "decision": "INVALID_PROTOCOL",
            "component_dispositions": {
                s: DISPOSITION_INVALID_PROTOCOL for s in covered_symbols
            },
            "reason": "Protocol error, malformed treatment construction, or ambiguous provenance encountered.",
        }

    # Level 2: Baseline not reproduced (A7 critical evidence failure on g031.e1)
    any_baseline_failed = (not baseline_reproduced) or any(
        info.get("baseline_reproduced") is False
        for sym, info in observed_case_outcomes.items()
        if sym in covered_symbols
    )
    if any_baseline_failed:
        return {
            "overall_outcome": OUTCOME_LEVEL_2_BASELINE,
            "level": 2,
            "decision": "INCONCLUSIVE_BASELINE_NOT_REPRODUCED",
            "component_dispositions": {
                s: DISPOSITION_BASELINE_NOT_REPRODUCED for s in covered_symbols
            },
            "reason": "A7 baseline critical evidence could not be reproduced on covered component.",
        }

    component_dispositions: dict[str, str] = {}
    for sym in covered_symbols:
        case_info = observed_case_outcomes.get(sym, {})
        app = case_info.get("applicability")
        if app == APPLICABILITY_INACTIVE:
            component_dispositions[sym] = DISPOSITION_APPLICABILITY_INCOMPLETE
        elif case_info.get("dependency_observed", False):
            component_dispositions[sym] = DISPOSITION_DEPENDENCY_OBSERVED
        elif case_info.get("retirement_validated", False) or (
            case_info.get("treatment_presence")
            and case_info.get("origin_subtracted")
            and not case_info.get("dependency_observed", False)
        ):
            component_dispositions[sym] = DISPOSITION_RETIREMENT_VALIDATED
        else:
            component_dispositions[sym] = DISPOSITION_DEPENDENCY_OBSERVED

    for sym in uncovered_hold_symbols:
        component_dispositions[sym] = DISPOSITION_COVERAGE_GAP

    for source_id, pages in page_hint_hold.items():
        component_dispositions[f"{source_id}:{sorted(pages)}"] = DISPOSITION_OUTSIDE_SCOPE

    # Level 3: Dependency observed for any covered component
    any_dependency = any(
        component_dispositions.get(sym) == DISPOSITION_DEPENDENCY_OBSERVED
        for sym in covered_symbols
    )
    if any_dependency:
        return {
            "overall_outcome": OUTCOME_LEVEL_3_DEPENDENCY,
            "level": 3,
            "decision": "DEPENDENCY_OBSERVED_RETAIN",
            "component_dispositions": component_dispositions,
        }

    # Level 4: Control divergence or safety regression
    if control_divergence or safety_regression:
        return {
            "overall_outcome": OUTCOME_LEVEL_4_REGRESSION,
            "level": 4,
            "decision": "FAIL_REGRESSION",
            "component_dispositions": component_dispositions,
        }

    # Level 5: Applicability incomplete
    any_applicability_incomplete = any(
        component_dispositions.get(sym) == DISPOSITION_APPLICABILITY_INCOMPLETE
        for sym in covered_symbols
    )
    if any_applicability_incomplete:
        return {
            "overall_outcome": OUTCOME_LEVEL_5_APPLICABILITY,
            "level": 5,
            "decision": "INCONCLUSIVE_APPLICABILITY_INCOMPLETE",
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
            "decision": "MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD",
            "component_dispositions": component_dispositions,
        }

    return {
        "overall_outcome": "INCONCLUSIVE / UNRECOGNIZED_STATE",
        "level": 99,
        "decision": "UNRECOGNIZED_STATE",
        "component_dispositions": component_dispositions,
    }


# ---------------------------------------------------------------------------
# Verification Helpers (Git, Immutability & Committed Artifacts)
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
    expected_msg: str = R2_COMMIT_MESSAGE,
) -> dict[str, Any]:
    """Verify git commit message and parent for R2 commit."""
    cmd_msg = ["git", "log", "-1", "--pretty=format:%s", head_ref]
    actual_msg = subprocess.run(cmd_msg, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    cmd_parent = ["git", "rev-parse", f"{head_ref}~1"]
    actual_parent = subprocess.run(cmd_parent, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    msg_exact = (actual_msg == expected_msg)
    parent_exact = (actual_parent == expected_parent)

    return {
        "all_valid": msg_exact and parent_exact,
        "r2_commit_message_exact": msg_exact,
        "r2_parent_exact": parent_exact,
        "actual_msg": actual_msg,
        "actual_parent": actual_parent,
    }


def verify_git_cumulative_diff(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = STARTING_HEAD,
    _override_diff_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Verify cumulative diff between base_ref and head_ref contains exactly the 7 R2 paths."""
    if _override_diff_paths is not None:
        diff_paths = sorted(_override_diff_paths)
    else:
        cmd = ["git", "diff", "--name-only", base_ref, head_ref]
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
        diff_paths = sorted([p.replace("\\", "/").strip() for p in res.stdout.splitlines() if p.strip()])

    exact_match = (diff_paths == sorted(EXPECTED_R2_PATHS))
    return {
        "exact_match": exact_match,
        "diff_paths": diff_paths,
        "expected_paths": sorted(EXPECTED_R2_PATHS),
        "extra_paths": [p for p in diff_paths if p not in EXPECTED_R2_PATHS],
        "missing_paths": [p for p in EXPECTED_R2_PATHS if p not in diff_paths],
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


def verify_historical_r1_immutability(project_root: Path, head_ref: str = "HEAD") -> dict[str, Any]:
    """Verify that historical R1 artifacts are sealed and unchanged from STARTING_HEAD."""
    mismatches: list[str] = []
    blob_hashes: dict[str, str] = {}

    for rel_path, expected_blob in HISTORICAL_R1_BLOBS.items():
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
        "batch2_validated_subset_active": (
            (eff.symbols == [] and root_macro.symbols == []) if (eff and root_macro) else False
        ),
        "full_batch2_production_activation_false": True,
    }


def verify_committed_artifacts_consistency(
    project_root: Path,
    audit_results: dict[str, Any],
) -> dict[str, Any]:
    """Verify committed preregistration and result artifacts agree with live audit (Section 30)."""
    mismatches: list[str] = []

    prereg_path = project_root / "evaluation" / "d4_a8_r2_component_sensitive_execution_preregistration.json"
    result_path = project_root / "evaluation" / "d4_a8_r2_result.json"

    if not prereg_path.exists():
        mismatches.append("preregistration.json does not exist")
        return {"consistent": False, "mismatches": mismatches}
    if not result_path.exists():
        mismatches.append("result.json does not exist")
        return {"consistent": False, "mismatches": mismatches}

    try:
        with open(prereg_path, "r", encoding="utf-8") as f:
            prereg = json.load(f)
        with open(result_path, "r", encoding="utf-8") as f:
            res = json.load(f)
    except Exception as e:
        mismatches.append(f"Failed to load committed JSON artifacts: {e}")
        return {"consistent": False, "mismatches": mismatches}

    # Checks against preregistration.json
    if prereg.get("covered_symbol_mask") != audit_results.get("covered_symbol_mask"):
        mismatches.append("prereg covered_symbol_mask drift")
    if prereg.get("uncovered_symbol_hold_mask") != audit_results.get("uncovered_symbol_hold_mask"):
        mismatches.append("prereg uncovered_symbol_hold_mask drift")
    if prereg.get("page_hint_hold_mask") != audit_results.get("page_hint_hold_mask"):
        mismatches.append("prereg page_hint_hold_mask drift")
    if prereg.get("formal_case_order") != audit_results.get("formal_cohort"):
        mismatches.append("prereg formal_case_order drift")
    if prereg.get("page_hint_gap_audit", {}).get("result") != audit_results.get("page_hint_gap_result"):
        mismatches.append("prereg page_hint_gap_result drift")
    if prereg.get("plan_reusability_results") != audit_results.get("plan_reusability_results"):
        mismatches.append("prereg plan_reusability_results drift")
    if prereg.get("reusable_plan_case_ids") != audit_results.get("reusable_plan_case_ids"):
        mismatches.append("prereg reusable_plan_case_ids drift")
    if prereg.get("fresh_plan_case_ids") != audit_results.get("fresh_plan_case_ids"):
        mismatches.append("prereg fresh_plan_case_ids drift")
    if prereg.get("derived_provider_budget") != audit_results.get("derived_provider_budget"):
        mismatches.append("prereg derived_provider_budget drift")
    if prereg.get("production_activation_authorized") is not False:
        mismatches.append("prereg production_activation_authorized is not False")
    if prereg.get("d4_a9_authorized") is not False:
        mismatches.append("prereg d4_a9_authorized is not False")

    # Checks against result.json
    if res.get("status") != "PASS":
        mismatches.append("result status is not PASS")
    if res.get("decision") != "COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEALED":
        mismatches.append("result decision drift")
    if res.get("covered_symbol_mask") != audit_results.get("covered_symbol_mask"):
        mismatches.append("result covered_symbol_mask drift")
    if res.get("uncovered_symbol_hold_mask") != audit_results.get("uncovered_symbol_hold_mask"):
        mismatches.append("result uncovered_symbol_hold_mask drift")
    if res.get("page_hint_hold_mask") != audit_results.get("page_hint_hold_mask"):
        mismatches.append("result page_hint_hold_mask drift")
    if res.get("formal_cohort") != audit_results.get("formal_cohort"):
        mismatches.append("result formal_cohort drift")
    if res.get("page_hint_gap_result") != audit_results.get("page_hint_gap_result"):
        mismatches.append("result page_hint_gap_result drift")
    if res.get("a5_provenance_compatibility_verified") != audit_results.get("a5_provenance_compatibility_verified"):
        mismatches.append("result a5_provenance_compatibility_verified drift")
    if res.get("a5_applicability_compatibility_verified") != audit_results.get("a5_applicability_compatibility_verified"):
        mismatches.append("result a5_applicability_compatibility_verified drift")
    if res.get("a5_projection_compatibility_verified") != audit_results.get("a5_projection_compatibility_verified"):
        mismatches.append("result a5_projection_compatibility_verified drift")
    if res.get("persistence_before_gate_contract_verified") != audit_results.get("persistence_before_gate_contract_verified"):
        mismatches.append("result persistence_before_gate_contract_verified drift")
    if res.get("fail_closed_evaluator_verified") != audit_results.get("fail_closed_evaluator_verified"):
        mismatches.append("result fail_closed_evaluator_verified drift")
    if res.get("per_case_reuse_dispositions") != audit_results.get("plan_reusability_results"):
        mismatches.append("result per_case_reuse_dispositions drift")
    if res.get("reusable_plan_case_ids") != audit_results.get("reusable_plan_case_ids"):
        mismatches.append("result reusable_plan_case_ids drift")
    if res.get("fresh_plan_case_ids") != audit_results.get("fresh_plan_case_ids"):
        mismatches.append("result fresh_plan_case_ids drift")
    if res.get("derived_provider_budget") != audit_results.get("derived_provider_budget"):
        mismatches.append("result derived_provider_budget drift")
    if res.get("production_activation_authorized") is not False:
        mismatches.append("result production_activation_authorized is not False")
    if res.get("d4_a9_authorized") is not False:
        mismatches.append("result d4_a9_authorized is not False")

    consistent = (len(mismatches) == 0)
    return {
        "consistent": consistent,
        "mismatches": mismatches,
    }


# ---------------------------------------------------------------------------
# High-Level Audit and Verification Dispatchers
# ---------------------------------------------------------------------------

def audit_execution_contract(project_root: Path) -> dict[str, Any]:
    """Run full audit for D4-A8-R2 execution contract seal."""
    gold_questions = load_gold_questions(project_root)
    case_audit = audit_case_eligibility(gold_questions)
    coverage_audit = audit_component_sensitive_coverage(project_root, gold_questions)
    gap_audit = audit_page_hint_coverage_gap_approval_aware(project_root)

    # Mechanical A5 authority audit
    a5_audit = audit_a5_execution_semantic_compatibility()

    # Enforceable persistence-before-gate state contract audit
    persistence_audit = audit_persistence_before_gate_contract()

    # Plan reusability audit with deterministic discovery
    plan_reuse = audit_plan_reusability(project_root, FROZEN_FORMAL_CASE_ORDER)
    prod_state = verify_production_state(project_root)

    # Fail-closed evaluator check
    eval_fail_closed = evaluate_component_sensitive_hypothetical_outcome(
        FROZEN_COVERED_SYMBOL_MASK,
        FROZEN_UNCOVERED_SYMBOL_HOLD_MASK,
        FROZEN_PAGE_HINT_HOLD_MASK,
        {"model/PndLmdModelFactory.cxx": {"applicability": APPLICABILITY_AMBIGUOUS}},
    )
    evaluator_fail_closed_sealed = (
        eval_fail_closed["level"] == 1
        and eval_fail_closed["overall_outcome"] == OUTCOME_LEVEL_1_INVALID
    )

    all_pass = (
        case_audit["all_valid"]
        and coverage_audit["r1_target_mask_preserved"]
        and gap_audit["status"] == "OPEN"
        and gap_audit["result"] == "NO_EXISTING_APPROVED_ENGLISH_CASE_FOUND"
        and a5_audit.get("authority_loaded", False)
        and a5_audit.get("required_helpers_present", False)
        and a5_audit["a5_provenance_compatibility_verified"]
        and a5_audit["a5_applicability_compatibility_verified"]
        and a5_audit["a5_projection_compatibility_verified"]
        and persistence_audit["persistence_before_gate_contract_verified"]
        and plan_reuse["plan_reusability_audit_complete"]
        and evaluator_fail_closed_sealed
        and prod_state["production_state_valid"]
    )

    return {
        "status": "PASS" if all_pass else "FAIL",
        "decision": (
            "COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEALED"
            if all_pass
            else "EXECUTION_CONTRACT_AUDIT_FAILED"
        ),
        "case_eligibility_audit": case_audit["all_valid"],
        "r1_target_mask_preserved": coverage_audit["r1_target_mask_preserved"],
        "covered_symbol_mask": coverage_audit["covered_symbol_mask"],
        "uncovered_symbol_hold_mask": coverage_audit["uncovered_symbol_hold_mask"],
        "page_hint_hold_mask": coverage_audit["page_hint_hold_mask"],
        "page_hint_gap_status": gap_audit["status"],
        "page_hint_gap_result": gap_audit["result"],
        "formal_cohort": FROZEN_FORMAL_CASE_ORDER,
        "a5_authority_audit": a5_audit,
        "a5_provenance_compatibility_verified": a5_audit["a5_provenance_compatibility_verified"],
        "a5_applicability_compatibility_verified": a5_audit["a5_applicability_compatibility_verified"],
        "a5_projection_compatibility_verified": a5_audit["a5_projection_compatibility_verified"],
        "non_rule_origin_preservation_verified": a5_audit["non_rule_origin_preservation_verified"],
        "persistence_audit": persistence_audit,
        "persistence_before_gate_contract_verified": persistence_audit["persistence_before_gate_contract_verified"],
        "plan_reusability_audit_complete": plan_reuse["plan_reusability_audit_complete"],
        "plan_reusability_results": plan_reuse["reusability_results"],
        "reusable_plan_case_ids": plan_reuse["reusable_plan_case_ids"],
        "fresh_plan_case_ids": plan_reuse["fresh_plan_case_ids"],
        "derived_provider_budget": plan_reuse["derived_provider_budget"],
        "fail_closed_evaluator_verified": evaluator_fail_closed_sealed,
        "production_state_valid": prod_state["production_state_valid"],
        "zero_provider_execution": True,
        "batch1_active": prod_state["batch1_active"],
        "batch2_validated_subset_active": prod_state["batch2_validated_subset_active"],
        "full_batch2_production_activation_false": prod_state["full_batch2_production_activation_false"],
        "d4_a9_authorized": False,
        "production_activation_authorized": False,
        "errors": case_audit["errors"],
    }


def verify_execution_contract(project_root: Path) -> dict[str, Any]:
    """Run verification mode on committed R2 tree."""
    audit_res = audit_execution_contract(project_root)
    clean_wt = verify_clean_worktree(project_root)
    commit_ident = verify_git_commit_identity(project_root)
    cum_diff = verify_git_cumulative_diff(project_root)
    src_tree = verify_production_tree_immutability(project_root)
    configs_diff = verify_configs_immutability(project_root)
    hist_r1 = verify_historical_r1_immutability(project_root)
    hist_a8 = verify_historical_a8_immutability(project_root)
    committed_consistency = verify_committed_artifacts_consistency(project_root, audit_res)

    all_pass = (
        audit_res["status"] == "PASS"
        and clean_wt
        and commit_ident["all_valid"]
        and cum_diff["exact_match"]
        and src_tree["src_tree_immutable"]
        and configs_diff["configs_immutable"]
        and hist_r1["all_match"]
        and hist_a8["all_match"]
        and committed_consistency["consistent"]
    )

    errors = list(audit_res.get("errors", []))
    if not clean_wt:
        errors.append("Working tree or index is dirty")
    if not commit_ident["all_valid"]:
        errors.append(f"Commit message or parent mismatch: msg={commit_ident['actual_msg']}, parent={commit_ident['actual_parent']}")
    if not cum_diff["exact_match"]:
        errors.append(f"Cumulative diff mismatch: {cum_diff['diff_paths']}")
    if not src_tree["src_tree_immutable"]:
        errors.append("src tree modified")
    if not configs_diff["configs_immutable"]:
        errors.append("configs directory modified")
    if not hist_r1["all_match"]:
        errors.append(f"Historical R1 blob mismatch: {hist_r1['mismatches']}")
    if not hist_a8["all_match"]:
        errors.append(f"Historical A8 blob mismatch: {hist_a8['mismatches']}")
    if not committed_consistency["consistent"]:
        errors.append(f"Committed artifacts drift (R2_MACHINE_ARTIFACT_DRIFT): {committed_consistency['mismatches']}")

    return {
        "status": "PASS" if all_pass else "FAIL",
        "decision": (
            "COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEALED"
            if all_pass
            else "EXECUTION_CONTRACT_VERIFICATION_FAILED"
        ),
        "audit_status": audit_res["status"],
        "clean_worktree": clean_wt,
        "r2_commit_message_exact": commit_ident["r2_commit_message_exact"],
        "r2_parent_exact": commit_ident["r2_parent_exact"],
        "r2_cumulative_diff_exact": cum_diff["exact_match"],
        "src_tree_immutable": src_tree["src_tree_immutable"],
        "configs_tree_immutable": configs_diff["configs_immutable"],
        "historical_r1_artifact_seal": hist_r1["all_match"],
        "historical_a8_artifact_seal": hist_a8["all_match"],
        "committed_artifacts_consistent": committed_consistency["consistent"],
        "r1_target_mask_preserved": audit_res["r1_target_mask_preserved"],
        "covered_symbol_mask": audit_res.get("covered_symbol_mask", []),
        "uncovered_symbol_hold_mask": audit_res.get("uncovered_symbol_hold_mask", []),
        "page_hint_hold_mask": audit_res.get("page_hint_hold_mask", {}),
        "formal_case_order": audit_res.get("formal_cohort", []),
        "formal_eligibility_complete": audit_res.get("case_eligibility_audit", False),
        "page_hint_gap_audit_complete": audit_res.get("page_hint_gap_status") == "OPEN",
        "a5_provenance_compatibility_verified": audit_res.get("a5_provenance_compatibility_verified", False),
        "a5_applicability_compatibility_verified": audit_res.get("a5_applicability_compatibility_verified", False),
        "a5_projection_compatibility_verified": audit_res.get("a5_projection_compatibility_verified", False),
        "non_rule_origin_preservation_verified": audit_res.get("non_rule_origin_preservation_verified", False),
        "persistence_before_gate_contract_verified": audit_res.get("persistence_before_gate_contract_verified", False),
        "plan_reusability_audit_complete": audit_res.get("plan_reusability_audit_complete", False),
        "plan_reusability_results": audit_res.get("plan_reusability_results", {}),
        "reusable_plan_case_ids": audit_res.get("reusable_plan_case_ids", []),
        "fresh_plan_case_ids": audit_res.get("fresh_plan_case_ids", []),
        "derived_provider_budget": audit_res.get("derived_provider_budget", {}),
        "fail_closed_evaluator_verified": audit_res.get("fail_closed_evaluator_verified", False),
        "zero_provider_execution": True,
        "batch1_active": audit_res.get("batch1_active", False),
        "batch2_validated_subset_active": audit_res.get("batch2_validated_subset_active", False),
        "full_batch2_production_activation_false": audit_res.get("full_batch2_production_activation_false", True),
        "d4_a9_authorized": False,
        "production_activation_authorized": False,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="D4-A8-R2 Execution Contract Seal Runner")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--mode", choices=["audit", "verify"], default="verify")
    args = parser.parse_args()

    project_root = args.project_root.resolve()

    if args.mode == "audit":
        res = audit_execution_contract(project_root)
    else:
        cmd_head = ["git", "rev-parse", "HEAD"]
        head_sha = subprocess.run(cmd_head, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
        if head_sha == STARTING_HEAD:
            res = audit_execution_contract(project_root)
        else:
            res = verify_execution_contract(project_root)

    print(json.dumps(res, indent=2))
    if res.get("status") != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
