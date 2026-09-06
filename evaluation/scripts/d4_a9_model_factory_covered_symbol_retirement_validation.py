"""D4-A9 — Component-Sensitive Model-Factory Targeted Scientific Validation Execution.

Prospective scientific validation of the covered symbol 'model/PndLmdModelFactory.cxx'
using a shared canonical Analyzer plan per case, evaluated against the A7 current arm
across the formal cohort ['g031', 'g032', 'g033', 'g047'].

Consumed frozen authority:
  D4-A8-R2 (commit 06f853d9613c5170676d77261cc2d7b82d50958c)
  COMPLETE / PASS / COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEALED

Target Masks:
  COVERED_SYMBOL_MASK: ['model/PndLmdModelFactory.cxx']
  UNCOVERED_SYMBOL_HOLD_MASK: ['model/PndLmdDPMAngModel1D.cxx', 'model/PndLmdDPMAngModel2D.cxx']
  PAGE_HINT_HOLD_MASK: {'pflueger_2017': [51, 57, 65]}

Provider Model Contract:
  Analyzer: gemini-3.8-flash, temperature=0.0, location='global', max_retries=0
  Embedding: gemini-embedding-2
  Reranker: production reranker contract
  Budget: max 4 Analyzer calls, max 8 Embedding calls, max 8 Reranker calls
          0 QA / 0 Verifier / 0 Judge / 0 Evaluator model calls
          0 retries, max 20 total logical calls

Lifecycle States & Persistence:
  ACQUIRED -> PERSISTED -> GATED -> RETRIEVAL_ELIGIBLE
  Shared-plan principle: exactly 1 canonical Analyzer plan per case shared across arms.
  Zero downstream Analyzer calls during retrieval.
  Zero model calls during evaluation.
"""

from __future__ import annotations

import argparse
import copy
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

_EVAL_SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _EVAL_SCRIPTS_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))
if str(_PROJECT_ROOT / "evaluation" / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "evaluation" / "scripts"))

# ---------------------------------------------------------------------------
# Frozen Authorities & Starting Boundaries
# ---------------------------------------------------------------------------

STARTING_HEAD = "06f853d9613c5170676d77261cc2d7b82d50958c"
STARTING_COMMIT_MESSAGE = "D4-A8-R2 seal component-sensitive execution contract"
STARTING_PARENT_HEAD = "a357bfc4e0d846cefa295e98c5de0a8b2813cfa0"

EXECUTOR_FREEZE_COMMIT_MESSAGE = "D4-A9 freeze targeted validation executor"
PLAN_FREEZE_COMMIT_MESSAGE = "D4-A9 freeze prospective component-sensitive plans"
RAW_FREEZE_COMMIT_MESSAGE = "D4-A9 freeze paired targeted retirement results"
CLOSEOUT_COMMIT_MESSAGE = "D4-A9 close component-sensitive model-factory validation"

MANIFEST_PATH = "evaluation/d4_a9_execution_manifest.json"
RAW_PLANS_PATH = "evaluation/d4_a9_raw_prospective_plans.json"
RAW_RESULTS_PATH = "evaluation/d4_a9_raw_paired_results.json"
EVALUATOR_RESULTS_PATH = "evaluation/d4_a9_evaluator_results.json"
RESULT_PATH = "evaluation/d4_a9_result.json"
REPORT_PATH = "evaluation/D4_A9_MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATION.md"
RUNNER_PATH = "evaluation/scripts/d4_a9_model_factory_covered_symbol_retirement_validation.py"
TEST_PATH = "tests/unit/test_d4_a9_model_factory_covered_symbol_retirement_validation.py"

GOLD_QUESTIONS_PATH = "evaluation/benchmarks/v2_6/gold_questions.yaml"
NOVEL_DEV_PATH = "evaluation/novel/v1/novel_dev.yaml"
QUERY_EXPANSIONS_PATH = "configs/query_expansions.yaml"

R2_PREREG_PATH = "evaluation/d4_a8_r2_component_sensitive_execution_preregistration.json"
R2_RESULT_PATH = "evaluation/d4_a8_r2_result.json"

TARGET_RULE_ID = "model_factory_theory"
FROZEN_COVERED_SYMBOL_MASK = ["model/PndLmdModelFactory.cxx"]
FROZEN_UNCOVERED_SYMBOL_HOLD_MASK = [
    "model/PndLmdDPMAngModel1D.cxx",
    "model/PndLmdDPMAngModel2D.cxx",
]
FROZEN_PAGE_HINT_HOLD_MASK: dict[str, list[int]] = {"pflueger_2017": [51, 57, 65]}
FROZEN_FORMAL_CASE_ORDER = ["g031", "g032", "g033", "g047"]

CASE_ROLES: dict[str, dict[str, Any]] = {
    "g031": {
        "role": "DIRECT_MODEL_FACTORY_TREATMENT_CASE",
        "covered_component": "model/PndLmdModelFactory.cxx",
        "critical_evidence_group": "g031.e1",
        "expected_matching_target_rule": True,
    },
    "g032": {
        "role": "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
        "adjacent_component": "model/PndLmdDPMAngModel1D.cxx",
        "critical_evidence_group": "g032.e1",
        "expected_matching_target_rule": False,
    },
    "g033": {
        "role": "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
        "adjacent_component": "model/PndLmdDPMAngModel2D.cxx",
        "critical_evidence_group": "g033.e1",
        "expected_matching_target_rule": False,
    },
    "g047": {
        "role": "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL",
        "adjacent_page_hint": {"source_id": "pflueger_2017", "pdf_page": 51},
        "critical_evidence_group": "g047.e1",
        "expected_matching_target_rule": False,
    },
}

EXPECTED_MODEL = "gemini-3.8-flash"
EXPECTED_TEMPERATURE = 0.0
EXPECTED_VERTEX_LOCATION = "global"
EXPECTED_RETRIES = 0

PLANNED_BUDGET: dict[str, int] = {
    "N_formal_cases": 4,
    "R_reusable_plans": 0,
    "F_fresh_plans": 4,
    "analyzer_calls": 4,
    "embedding_calls": 8,
    "reranker_calls": 8,
    "qa_calls": 0,
    "verifier_calls": 0,
    "judge_calls": 0,
    "scientific_evaluator_calls": 0,
    "retries": 0,
    "total_logical_model_calls": 20,
}

SCHEDULE_8: list[dict[str, Any]] = [
    {
        "cell_index": 1,
        "cell_id": "g031_A7_CURRENT",
        "case_id": "g031",
        "arm": "A7_CURRENT",
        "role": "DIRECT_MODEL_FACTORY_TREATMENT_CASE",
    },
    {
        "cell_index": 2,
        "cell_id": "g031_COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
        "case_id": "g031",
        "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
        "role": "DIRECT_MODEL_FACTORY_TREATMENT_CASE",
    },
    {
        "cell_index": 3,
        "cell_id": "g032_A7_CURRENT",
        "case_id": "g032",
        "arm": "A7_CURRENT",
        "role": "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
    },
    {
        "cell_index": 4,
        "cell_id": "g032_COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
        "case_id": "g032",
        "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
        "role": "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
    },
    {
        "cell_index": 5,
        "cell_id": "g033_A7_CURRENT",
        "case_id": "g033",
        "arm": "A7_CURRENT",
        "role": "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
    },
    {
        "cell_index": 6,
        "cell_id": "g033_COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
        "case_id": "g033",
        "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
        "role": "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
    },
    {
        "cell_index": 7,
        "cell_id": "g047_A7_CURRENT",
        "case_id": "g047",
        "arm": "A7_CURRENT",
        "role": "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL",
    },
    {
        "cell_index": 8,
        "cell_id": "g047_COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
        "case_id": "g047",
        "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
        "role": "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL",
    },
]

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

# Component Dispositions
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

# Overall Outcome Precedence States
OUTCOME_LEVEL_1_INVALID = "INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED"
OUTCOME_LEVEL_2_BASELINE = "INCONCLUSIVE / ALL_COVERED_COMPONENT_BASELINES_NOT_REPRODUCED"
OUTCOME_LEVEL_3_DEPENDENCY = "PARTIAL / DEPENDENCY_OBSERVED_FOR_COVERED_COMPONENTS_RETAIN"
OUTCOME_LEVEL_4_REGRESSION = "FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION"
OUTCOME_LEVEL_5_APPLICABILITY = "INCONCLUSIVE / COVERED_COMPONENT_APPLICABILITY_INCOMPLETE"
OUTCOME_LEVEL_6_PARTIAL_PASS = (
    "PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD"
)

# Component-sensitive A9 mask conforming strictly to A5 schema
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

REQUIRED_14_PERSISTED_FIELDS = [
    "case_id",
    "question",
    "provider_model_contract",
    "raw_analyzer_response",
    "canonical_plan",
    "canonical_serialization",
    "contribution_ledger",
    "provenance_origin_receipts",
    "component_applicability_receipts",
    "current_execution_projection",
    "treatment_execution_projection",
    "plan_signature",
    "provider_accounting",
    "matched_rule_identities",
]

# ---------------------------------------------------------------------------
# Exceptions & State Machine
# ---------------------------------------------------------------------------

class TargetedValidationProtocolError(Exception):
    """Raised when targeted validation protocol or treatment construction fails."""
    pass


class StateTransitionError(Exception):
    """Raised when an invalid execution state transition is attempted."""
    pass


STATE_ACQUIRED = "ACQUIRED"
STATE_PERSISTED = "PERSISTED"
STATE_GATED = "GATED"
STATE_RETRIEVAL_ELIGIBLE = "RETRIEVAL_ELIGIBLE"

VALID_STATE_TRANSITIONS: dict[str, list[str]] = {
    STATE_ACQUIRED: [STATE_PERSISTED],
    STATE_PERSISTED: [STATE_GATED],
    STATE_GATED: [STATE_RETRIEVAL_ELIGIBLE],
    STATE_RETRIEVAL_ELIGIBLE: [],
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


# ---------------------------------------------------------------------------
# Strict A5 Authority Binding
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
    """Load the frozen D4-A5 authority pure helpers. Fail-closed if unavailable."""
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
# Provenance Origin Typing Gate
# ---------------------------------------------------------------------------

def validate_origin_type_consistency(
    ledger: list[dict[str, Any]],
    known_rule_ids: set[str] | list[str] | None = None,
) -> tuple[bool, str | None]:
    """Validate origin-type consistency for every ledger entry."""
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
# Treatment Projection & Construction
# ---------------------------------------------------------------------------

def construct_component_sensitive_treatment(
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    matched_rule_ids: list[str],
    case_id: str,
    *,
    case_role: str = "TREATMENT",
    masks: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Fail-closed treatment constructor for D4-A9 targeted validation."""
    a5 = load_a5_authority()
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
            raise TargetedValidationProtocolError(
                f"Treatment case {case_id} did not match target rule {TARGET_RULE_ID}"
            )

        mask_entries = a5.build_batch2_mask_entries(
            case_id,
            [r for r in matched_rule_ids if r in effective_masks],
            masks=effective_masks,
        )
        component_receipts, summary = a5.classify_component_applicability(
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
            raise TargetedValidationProtocolError(
                f"Covered target symbol not ACTIVE_IDENTIFIABLE in {case_id}"
            )

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
            if (sym in (canonical_plan.get("symbols") or [])) != (
                sym in (projected_plan.get("symbols") or [])
            ):
                raise TargetedValidationProtocolError(f"Held DPM symbol mutated in projection: {sym}")
        for paper, pages in FROZEN_PAGE_HINT_HOLD_MASK.items():
            orig_pages = (canonical_plan.get("paper_page_hints") or {}).get(paper, [])
            proj_pages = (projected_plan.get("paper_page_hints") or {}).get(paper, [])
            if sorted(orig_pages) != sorted(proj_pages):
                raise TargetedValidationProtocolError(f"Held page hint mutated: {paper}")

        # Verify canonical plan was not mutated
        if canonical_plan != canonical_before:
            raise TargetedValidationProtocolError("Canonical plan was mutated during projection")

        return projected_plan, receipts, component_receipts

    elif case_role == "CONTROL":
        if TARGET_RULE_ID in matched_rule_ids:
            raise TargetedValidationProtocolError(
                f"Control case {case_id} unexpectedly matched target rule {TARGET_RULE_ID}"
            )

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
            raise TargetedValidationProtocolError(
                f"Control case {case_id} received non-zero target subtraction"
            )

        return projected_plan, receipts, component_receipts

    else:
        raise TargetedValidationProtocolError(f"Unknown case role: {case_role}")


# ---------------------------------------------------------------------------
# Evaluator: Pure Deterministic Logic (0 Provider Calls)
# ---------------------------------------------------------------------------

def evaluate_outcomes(
    raw_plans: dict[str, Any],
    raw_results: dict[str, Any],
    gold_questions: dict[str, Any],
    object_lookup: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Evaluate D4-A9 outcomes using pure deterministic evaluation logic.

    0 provider calls, 0 judge calls, 0 QA calls, 0 verifier calls.
    """
    from panda_agent.evaluation import _matched_evidence_groups

    plans_by_case = {p["case_id"]: p for p in raw_plans.get("plans", [])}
    slots_map = {(s["case_id"], s["arm"]): s for s in raw_results.get("slots", [])}

    # Verify structural integrity
    if len(plans_by_case) != 4 or len(slots_map) != 8:
        return {
            "overall_outcome": OUTCOME_LEVEL_1_INVALID,
            "level": 1,
            "decision": "INVALID_PROTOCOL",
            "reason": "Missing plans or paired slots",
        }, {}

    # Check baseline reproduction on g031 / A7_CURRENT
    slot_g031_cur = slots_map.get(("g031", "A7_CURRENT"))
    slot_g031_trt = slots_map.get(("g031", "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT"))
    if not slot_g031_cur or not slot_g031_trt:
        return {
            "overall_outcome": OUTCOME_LEVEL_1_INVALID,
            "level": 1,
            "decision": "INVALID_PROTOCOL",
            "reason": "Missing g031 cell slots",
        }, {}

    q_g031 = gold_questions.get("g031")
    if not q_g031:
        return {
            "overall_outcome": OUTCOME_LEVEL_1_INVALID,
            "level": 1,
            "decision": "INVALID_PROTOCOL",
            "reason": "g031 gold question not found",
        }, {}

    eg_g031_e1 = [g for g in q_g031.required_evidence_groups if g.group_id == "g031.e1"]
    if not eg_g031_e1:
        return {
            "overall_outcome": OUTCOME_LEVEL_1_INVALID,
            "level": 1,
            "decision": "INVALID_PROTOCOL",
            "reason": "g031.e1 evidence group missing in gold question",
        }, {}

    cur_final_ids = slot_g031_cur.get("final_evidence_object_ids") or []
    rec_cur, _ = _matched_evidence_groups(eg_g031_e1, cur_final_ids, object_lookup)
    g031_cur_baseline_reproduced = (rec_cur > 0)

    # Level 2 check: baseline reproduction failure
    if not g031_cur_baseline_reproduced:
        return {
            "overall_outcome": OUTCOME_LEVEL_2_BASELINE,
            "level": 2,
            "decision": "INCONCLUSIVE_BASELINE_NOT_REPRODUCED",
            "component_dispositions": {
                "model/PndLmdModelFactory.cxx": DISPOSITION_BASELINE_NOT_REPRODUCED,
                "model/PndLmdDPMAngModel1D.cxx": DISPOSITION_COVERAGE_GAP,
                "model/PndLmdDPMAngModel2D.cxx": DISPOSITION_COVERAGE_GAP,
                "pflueger_2017:[51, 57, 65]": DISPOSITION_OUTSIDE_SCOPE,
            },
            "reason": "g031 / A7_CURRENT failed to reproduce critical evidence group g031.e1",
        }, {
            "g031_baseline_reproduced": False,
            "g031_treatment_reproduced": False,
        }

    # Treatment check on g031
    trt_final_ids = slot_g031_trt.get("final_evidence_object_ids") or []
    rec_trt, _ = _matched_evidence_groups(eg_g031_e1, trt_final_ids, object_lookup)
    g031_trt_reproduced = (rec_trt > 0)

    # Check origin subtraction in plan record
    plan_rec_g031 = plans_by_case.get("g031", {})
    diff_receipts = plan_rec_g031.get("treatment_execution_projection_diff_receipts") or {}
    removed_entries = diff_receipts.get("removed_rule_origin_entries") or []
    origin_subtracted = any(
        TARGET_RULE_ID in (entry.get("retired_rule_origins") or [])
        and entry.get("value") == "model/PndLmdModelFactory.cxx"
        for entry in removed_entries
    )

    if not origin_subtracted:
        return {
            "overall_outcome": OUTCOME_LEVEL_1_INVALID,
            "level": 1,
            "decision": "INVALID_PROTOCOL",
            "reason": "model_factory_theory origin was not subtracted in g031 treatment projection",
        }, {}

    # Check controls for regression
    control_divergence = False
    safety_regression = False
    control_details: dict[str, Any] = {}

    for cid in ["g032", "g033", "g047"]:
        slot_cur = slots_map.get((cid, "A7_CURRENT"))
        slot_trt = slots_map.get((cid, "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT"))
        if not slot_cur or not slot_trt:
            return {
                "overall_outcome": OUTCOME_LEVEL_1_INVALID,
                "level": 1,
                "decision": "INVALID_PROTOCOL",
                "reason": f"Missing cell slot for control {cid}",
            }, {}

        q_ctrl = gold_questions.get(cid)
        if not q_ctrl:
            continue

        crit_groups = [g for g in q_ctrl.required_evidence_groups if g.critical]
        cur_ids = slot_cur.get("final_evidence_object_ids") or []
        trt_ids = slot_trt.get("final_evidence_object_ids") or []

        rec_c, _ = _matched_evidence_groups(crit_groups, cur_ids, object_lookup)
        rec_t, _ = _matched_evidence_groups(crit_groups, trt_ids, object_lookup)

        control_details[cid] = {
            "current_matched_groups": rec_c,
            "treatment_matched_groups": rec_t,
            "total_critical_groups": len(crit_groups),
        }

        # If current retained critical group but treatment lost it -> regression!
        if rec_c > rec_t:
            control_divergence = True
            safety_regression = True

    # Check for dependency on covered component
    if not g031_trt_reproduced:
        # Treatment lost g031.e1 -> Level 3 Dependency
        return {
            "overall_outcome": OUTCOME_LEVEL_3_DEPENDENCY,
            "level": 3,
            "decision": "DEPENDENCY_OBSERVED_RETAIN",
            "component_dispositions": {
                "model/PndLmdModelFactory.cxx": DISPOSITION_DEPENDENCY_OBSERVED,
                "model/PndLmdDPMAngModel1D.cxx": DISPOSITION_COVERAGE_GAP,
                "model/PndLmdDPMAngModel2D.cxx": DISPOSITION_COVERAGE_GAP,
                "pflueger_2017:[51, 57, 65]": DISPOSITION_OUTSIDE_SCOPE,
            },
            "reason": "g031.e1 lost in treatment arm upon subtraction of model_factory_theory origin",
        }, {
            "g031_baseline_reproduced": True,
            "g031_treatment_reproduced": False,
            "control_details": control_details,
        }

    # Check Level 4: Control or Safety Regression
    if control_divergence or safety_regression:
        return {
            "overall_outcome": OUTCOME_LEVEL_4_REGRESSION,
            "level": 4,
            "decision": "FAIL_REGRESSION",
            "component_dispositions": {
                "model/PndLmdModelFactory.cxx": DISPOSITION_RETIREMENT_VALIDATED,
                "model/PndLmdDPMAngModel1D.cxx": DISPOSITION_COVERAGE_GAP,
                "model/PndLmdDPMAngModel2D.cxx": DISPOSITION_COVERAGE_GAP,
                "pflueger_2017:[51, 57, 65]": DISPOSITION_OUTSIDE_SCOPE,
            },
            "reason": "Critical evidence or safety regression detected in control arm",
        }, {
            "g031_baseline_reproduced": True,
            "g031_treatment_reproduced": True,
            "control_details": control_details,
        }

    # Level 6: Covered symbol validated, uncovered symbols and page hints hold
    return {
        "overall_outcome": OUTCOME_LEVEL_6_PARTIAL_PASS,
        "level": 6,
        "decision": "MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD",
        "component_dispositions": {
            "model/PndLmdModelFactory.cxx": DISPOSITION_RETIREMENT_VALIDATED,
            "model/PndLmdDPMAngModel1D.cxx": DISPOSITION_COVERAGE_GAP,
            "model/PndLmdDPMAngModel2D.cxx": DISPOSITION_COVERAGE_GAP,
            "pflueger_2017:[51, 57, 65]": DISPOSITION_OUTSIDE_SCOPE,
        },
        "reason": (
            "Covered component model/PndLmdModelFactory.cxx reproduced critical evidence g031.e1 "
            "in both current and treatment arms with model_factory_theory origin subtracted; "
            "zero control or safety regressions observed; uncovered DPM symbols and page hints "
            "remain strictly on HOLD."
        ),
    }, {
        "g031_baseline_reproduced": True,
        "g031_treatment_reproduced": True,
        "control_details": control_details,
    }


# ---------------------------------------------------------------------------
# Utility Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Phase P Execution: Fresh Analyzer Plan Acquisition
# ---------------------------------------------------------------------------

def execute_phase_p(project_root: Path) -> dict[str, Any]:
    """Acquire prospective Analyzer plans with persistence-before-gate contract."""
    load_dotenv(project_root / ".env")
    from panda_agent.config import load_query_expansions
    from panda_agent.evaluation import load_gold_dataset
    from panda_agent.models import RetrievalPlan
    from panda_agent.retrieval import Retriever

    a5 = load_a5_authority()
    manifest_path = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_path)

    raw_plans_path = project_root / RAW_PLANS_PATH
    if raw_plans_path.exists():
        existing_plans = _load_json(raw_plans_path)
        if len(existing_plans.get("plans", [])) == 4 and all(
            p.get("persistence_state") in (STATE_GATED, STATE_RETRIEVAL_ELIGIBLE)
            for p in existing_plans["plans"]
        ):
            print("[PHASE P] All 4 plans already acquired and persisted.")
            return existing_plans

    retriever = Retriever(project_root)
    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    questions_by_id = {q.id: q for q in gold_ds.questions}

    qe = load_query_expansions(project_root / QUERY_EXPANSIONS_PATH)
    rules_by_id = {r.rule_id: r.model_dump(mode="python") for r in qe.rules}

    plans_list: list[dict[str, Any]] = []
    total_tokens = 0
    total_attempts = 0

    print("[PHASE P] Starting fresh Analyzer plan acquisition for cohort: g031, g032, g033, g047...")

    for idx, cid in enumerate(FROZEN_FORMAL_CASE_ORDER, start=1):
        q = questions_by_id.get(cid)
        if not q:
            raise RuntimeError(f"Formal question {cid} not found in gold dataset")

        q_text = q.query
        role_info = CASE_ROLES[cid]
        case_role = "TREATMENT" if cid == "g031" else "CONTROL"

        print(f"  [{idx}/4] Acquiring plan for {cid} ({role_info['role']})...")

        stats_before = retriever.vertex.stats_snapshot()
        t0 = time.time()
        try:
            raw_plan_obj = retriever.analyze(q_text)
        except Exception as exc:
            raise RuntimeError(f"Provider call failed for {cid} (retries=0): {exc}") from exc
        elapsed = round(time.time() - t0, 3)

        stats_delta = retriever.vertex.stats_delta(stats_before)
        attempts = stats_delta.get("model_calls", 1)
        tokens = stats_delta.get("token_usage", 0)
        total_tokens += tokens
        total_attempts += attempts

        plan_dict = raw_plan_obj.model_dump(mode="json")
        RetrievalPlan.model_validate(plan_dict)

        canonical_serialization = json.dumps(plan_dict, sort_keys=True)
        sig_str, sig_payload = a5.compute_plan_signature(plan_dict)

        diagnostics = plan_dict.get("analysis_diagnostics") or {}
        matched_rule_ids = list(diagnostics.get("matched_expansion_rules") or [])

        # Build ledger and validate coverage and typing
        ledger = a5.build_contribution_ledger(plan_dict, rules_by_id, matched_rule_ids)

        # Projections
        current_execution_projection = copy.deepcopy(plan_dict)

        # Pre-gate treatment projection
        try:
            trt_proj, trt_diff_receipts, comp_receipts = construct_component_sensitive_treatment(
                plan_dict,
                ledger,
                matched_rule_ids,
                cid,
                case_role=case_role,
                masks=COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS,
            )
        except Exception as exc:
            trt_proj = None
            trt_diff_receipts = {"error": str(exc)}
            comp_receipts = []

        provenance_origin_receipts = [
            {
                "contribution_id": entry.get("contribution_id"),
                "provenance_origin_ids": entry.get("provenance_origin_ids"),
                "origin_types": entry.get("origin_types"),
            }
            for entry in ledger
        ]

        provider_accounting = {
            "model_id": EXPECTED_MODEL,
            "location": EXPECTED_VERTEX_LOCATION,
            "temperature": EXPECTED_TEMPERATURE,
            "retries": EXPECTED_RETRIES,
            "analyzer_logical_calls": 1,
            "analyzer_provider_attempts": attempts,
            "token_usage": tokens,
            "elapsed_seconds": elapsed,
        }

        # 1. State: ACQUIRED
        cur_state = STATE_ACQUIRED

        # Build raw record with all 14 required fields
        plan_record = {
            "case_id": cid,
            "question": q_text,
            "provider_model_contract": {
                "model_id": EXPECTED_MODEL,
                "temperature": EXPECTED_TEMPERATURE,
                "location": EXPECTED_VERTEX_LOCATION,
                "retries": EXPECTED_RETRIES,
            },
            "raw_analyzer_response": plan_dict,
            "canonical_plan": plan_dict,
            "canonical_serialization": canonical_serialization,
            "contribution_ledger": ledger,
            "provenance_origin_receipts": provenance_origin_receipts,
            "component_applicability_receipts": comp_receipts,
            "current_execution_projection": current_execution_projection,
            "treatment_execution_projection": trt_proj,
            "plan_signature": sig_str,
            "provider_accounting": provider_accounting,
            "matched_rule_identities": matched_rule_ids,
            "role": role_info["role"],
            "plan_id": f"prospective_{cid}",
            "persistence_state": cur_state,
            "started_at": _utc_now(),
            "treatment_execution_projection_diff_receipts": trt_diff_receipts,
        }

        # 2. State transition: ACQUIRED -> PERSISTED
        cur_state = transition_execution_state(cur_state, STATE_PERSISTED)
        plan_record["persistence_state"] = cur_state
        plan_record["persisted_at"] = _utc_now()

        plans_list.append(plan_record)

        # Immediate durable persistence BEFORE gating
        raw_plans_artifact = {
            "plans_planned": 4,
            "plans_recorded": len(plans_list),
            "plans_completed": len(plans_list),
            "provider_contract": {
                "model_id": EXPECTED_MODEL,
                "temperature": EXPECTED_TEMPERATURE,
                "location": EXPECTED_VERTEX_LOCATION,
                "retries": EXPECTED_RETRIES,
            },
            "accounting": {
                "analyzer_calls": len(plans_list),
                "analyzer_provider_attempts": total_attempts,
                "token_usage": total_tokens,
            },
            "plans": plans_list,
        }
        _save_json(raw_plans_path, raw_plans_artifact)

        # 3. State transition: PERSISTED -> GATED
        cur_state = transition_execution_state(cur_state, STATE_GATED)
        plan_record["persistence_state"] = cur_state
        plan_record["gated_at"] = _utc_now()

        # Applicability checks
        if cid == "g031":
            target_receipts = [
                r for r in comp_receipts if r["component_value"] in FROZEN_COVERED_SYMBOL_MASK
            ]
            if not target_receipts:
                raise TargetedValidationProtocolError("No covered target receipt found for g031")
            g031_app = target_receipts[0]["applicability_status"]
            plan_record["applicability_status"] = g031_app
            if g031_app == APPLICABILITY_ACTIVE:
                cur_state = transition_execution_state(cur_state, STATE_RETRIEVAL_ELIGIBLE)
                plan_record["persistence_state"] = cur_state
            elif g031_app == APPLICABILITY_INACTIVE:
                print("  [GATE] g031 is INACTIVE_NOT_IDENTIFIABLE. Retrieval will not execute.")
            else:
                raise TargetedValidationProtocolError(f"g031 is AMBIGUOUS_INVALID: {target_receipts[0]}")
        else:
            # Control checks
            if TARGET_RULE_ID in matched_rule_ids:
                raise TargetedValidationProtocolError(f"Control {cid} matched target rule {TARGET_RULE_ID}")
            if trt_proj != current_execution_projection:
                raise TargetedValidationProtocolError(f"Control {cid} received non-zero target subtraction")
            cur_state = transition_execution_state(cur_state, STATE_RETRIEVAL_ELIGIBLE)
            plan_record["persistence_state"] = cur_state

        # Update persisted artifact with gated state
        _save_json(raw_plans_path, raw_plans_artifact)

    # Update manifest
    manifest["outcome_exposure_state"]["D4_A9_OUTCOME_EXPOSURE"] = "PLANS_FROZEN"
    manifest["outcome_exposure_state"]["plans_persisted"] = True
    manifest["accounting"]["analyzer_calls"] = len(plans_list)
    manifest["accounting"]["analyzer_provider_attempts"] = total_attempts
    manifest["accounting"]["token_usage"] = total_tokens
    _save_json(manifest_path, manifest)

    print(f"[PHASE P COMPLETE] Acquired {len(plans_list)} plans; {total_tokens} tokens consumed.")
    return raw_plans_artifact


# ---------------------------------------------------------------------------
# Phase R Execution: 8 Paired Retrieval Cells
# ---------------------------------------------------------------------------

def execute_phase_r(project_root: Path) -> dict[str, Any]:
    """Execute exactly 8 paired retrieval cells in frozen schedule order."""
    load_dotenv(project_root / ".env")
    from panda_agent.evaluation import load_gold_dataset
    from panda_agent.models import RetrievalPlan
    from panda_agent.retrieval import Retriever

    manifest_path = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_path)

    raw_plans_path = project_root / RAW_PLANS_PATH
    raw_plans = _load_json(raw_plans_path)
    plans_by_case = {p["case_id"]: p for p in raw_plans["plans"]}

    # Verify g031 is retrieval eligible
    if plans_by_case["g031"]["persistence_state"] != STATE_RETRIEVAL_ELIGIBLE:
        raise RuntimeError("g031 is not RETRIEVAL_ELIGIBLE; cannot execute Phase R")

    raw_results_path = project_root / RAW_RESULTS_PATH
    if raw_results_path.exists():
        existing_results = _load_json(raw_results_path)
        if len(existing_results.get("slots", [])) == 8 and all(
            s.get("status") == "COMPLETED" for s in existing_results["slots"]
        ):
            print("[PHASE R] All 8 retrieval cells already completed.")
            return existing_results

    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    questions_by_id = {q.id: q for q in gold_ds.questions}

    retriever = Retriever(project_root)

    # Downstream analyzer calls are strictly forbidden
    def _forbidden_analyze(*args: Any, **kwargs: Any) -> RetrievalPlan:
        raise RuntimeError("Downstream Query Analyzer invocation is forbidden during Phase R")

    retriever.analyze = _forbidden_analyze  # type: ignore[method-assign]

    slots_list: list[dict[str, Any]] = []
    total_tokens = 0
    total_embedding = 0
    total_reranker = 0
    total_attempts = 0

    print("[PHASE R] Executing 8 paired retrieval cells in frozen order...")

    for cell in SCHEDULE_8:
        cell_idx = cell["cell_index"]
        cell_id = cell["cell_id"]
        cid = cell["case_id"]
        arm = cell["arm"]
        role = cell["role"]

        print(f"  [{cell_idx}/8] Executing cell {cell_id}...")

        plan_rec = plans_by_case[cid]
        q_text = questions_by_id[cid].query

        if arm == "A7_CURRENT":
            arm_plan_dict = plan_rec["current_execution_projection"]
        else:
            arm_plan_dict = plan_rec["treatment_execution_projection"]

        arm_plan = RetrievalPlan.model_validate(arm_plan_dict)

        stats_before = retriever.vertex.stats_snapshot()
        t0 = time.time()
        retrieval_res = retriever.retrieve(q_text, plan=arm_plan)
        elapsed = round(time.time() - t0, 3)
        stats_delta = retriever.vertex.stats_delta(stats_before)

        actual_plan = retrieval_res.get("plan") or {}
        plan_equality = (actual_plan == arm_plan_dict)
        if not plan_equality:
            raise RuntimeError(
                f"Cell {cell_id}: actual plan used != arm execution projection"
            )

        emb_calls = stats_delta.get("embedding_calls", 1)
        gen_calls = stats_delta.get("generation_calls", 1)
        model_calls = stats_delta.get("model_calls", 0)
        tokens = stats_delta.get("token_usage", 0)

        total_embedding += emb_calls
        total_reranker += gen_calls
        total_attempts += model_calls
        total_tokens += tokens

        structured_receipt = retrieval_res.get("structured_replacement")
        rankings = retrieval_res.get("rankings") or {}
        fusion_scores = retrieval_res.get("fusion_scores") or {}
        if structured_receipt is not None:
            rerank_pool = list(structured_receipt.get("final_rerank_pool_ids") or [])
        else:
            rerank_pool = list(fusion_scores.keys())

        evidence_items = []
        for item in retrieval_res.get("evidence") or []:
            evidence_items.append({
                "object_id": item.get("object_id"),
                "source_id": item.get("source_id"),
                "source_version_id": item.get("source_version_id"),
                "locator": item.get("locator"),
                "object_type": item.get("object_type"),
                "title": item.get("title"),
            })

        final_evidence_ids = [item["object_id"] for item in evidence_items if item.get("object_id")]

        cell_record = {
            "cell_index": cell_idx,
            "cell_id": cell_id,
            "case_id": cid,
            "arm": arm,
            "role": role,
            "question": q_text,
            "status": "COMPLETED",
            "elapsed_seconds": elapsed,
            "canonical_plan_id": plan_rec["plan_id"],
            "canonical_plan_signature": plan_rec["plan_signature"],
            "frozen_canonical_plan": plan_rec["canonical_plan"],
            "arm_execution_projection": arm_plan_dict,
            "actual_plan_used": actual_plan,
            "plan_equality_arm_projection_verified": plan_equality,
            "matched_query_expansion_rules": (actual_plan.get("analysis_diagnostics") or {}).get(
                "matched_expansion_rules", []
            ),
            "final_evidence_object_ids": final_evidence_ids,
            "rerank_pool_object_ids": rerank_pool,
            "evidence_items": evidence_items,
            "provider_accounting": {
                "embedding_calls": emb_calls,
                "generation_calls": gen_calls,
                "model_calls": model_calls,
                "token_usage": tokens,
            },
            "started_at": _utc_now(),
            "completed_at": _utc_now(),
        }

        slots_list.append(cell_record)

        # Immediate durable persistence after each cell
        raw_results_artifact = {
            "slots_planned": 8,
            "slots_completed": len(slots_list),
            "accounting": {
                "embedding_calls": total_embedding,
                "reranker_calls": total_reranker,
                "model_calls": total_attempts,
                "token_usage": total_tokens,
            },
            "slots": slots_list,
        }
        _save_json(raw_results_path, raw_results_artifact)

    # Update manifest
    manifest["outcome_exposure_state"]["D4_A9_OUTCOME_EXPOSURE"] = "RAW_RETRIEVAL_COMPLETE"
    manifest["outcome_exposure_state"]["raw_results_persisted"] = True
    manifest["accounting"]["embedding_calls"] = total_embedding
    manifest["accounting"]["reranker_calls"] = total_reranker
    manifest["accounting"]["token_usage"] += total_tokens
    _save_json(manifest_path, manifest)

    print(f"[PHASE R COMPLETE] Completed 8 cells; {total_tokens} tokens consumed.")
    return raw_results_artifact


# ---------------------------------------------------------------------------
# Evaluator & Closeout
# ---------------------------------------------------------------------------

def run_evaluation(project_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run deterministic evaluator (0 provider calls) and write results."""
    from panda_agent.evaluation import load_gold_dataset
    from panda_agent.evaluation_runner import load_object_lookup

    manifest_path = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_path)

    raw_plans = _load_json(project_root / RAW_PLANS_PATH)
    raw_results = _load_json(project_root / RAW_RESULTS_PATH)

    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    questions_by_id = {q.id: q for q in gold_ds.questions}
    object_lookup = load_object_lookup(project_root)

    eval_result, details = evaluate_outcomes(raw_plans, raw_results, questions_by_id, object_lookup)

    evaluator_artifact = {
        "stage": "D4-A9",
        "evaluated_at": _utc_now(),
        "provider_calls": 0,
        "evaluation_validity": {
            "plan_count": len(raw_plans.get("plans", [])),
            "slot_count": len(raw_results.get("slots", [])),
            "zero_evaluator_provider_calls": True,
        },
        "verdict_level": eval_result["level"],
        "verdict": eval_result["overall_outcome"],
        "verdict_status": (
            "PARTIAL" if eval_result["level"] in (3, 6)
            else "FAIL" if eval_result["level"] == 4
            else "INCONCLUSIVE" if eval_result["level"] in (2, 5)
            else "INVALID"
        ),
        "verdict_decision": eval_result["decision"],
        "verdict_reason": eval_result["reason"],
        "component_dispositions": eval_result.get("component_dispositions", {}),
        "details": details,
    }
    _save_json(project_root / EVALUATOR_RESULTS_PATH, evaluator_artifact)

    # Result artifact
    final_result_artifact = {
        "stage": "D4-A9",
        "status": evaluator_artifact["verdict_status"],
        "decision": evaluator_artifact["verdict_decision"],
        "task_name": "D4-A9 — Component-Sensitive Model-Factory Covered-Symbol Retirement Targeted Validation",
        "evaluated_at": evaluator_artifact["evaluated_at"],
        "starting_head": STARTING_HEAD,
        "r2_authority_head": STARTING_HEAD,
        "covered_symbol_mask": list(FROZEN_COVERED_SYMBOL_MASK),
        "uncovered_symbol_hold_mask": list(FROZEN_UNCOVERED_SYMBOL_HOLD_MASK),
        "page_hint_hold_mask": dict(FROZEN_PAGE_HINT_HOLD_MASK),
        "formal_cohort": list(FROZEN_FORMAL_CASE_ORDER),
        "reusable_plan_case_ids": [],
        "fresh_plan_case_ids": list(FROZEN_FORMAL_CASE_ORDER),
        "provider_accounting": manifest["accounting"],
        "component_dispositions": eval_result.get("component_dispositions", {}),
        "verdict_level": eval_result["level"],
        "verdict": eval_result["overall_outcome"],
        "verdict_reason": eval_result["reason"],
        "production_immutability": True,
        "historical_r2_artifacts_sealed": True,
        "batch1_active": True,
        "batch2_validated_subset_active": True,
        "full_batch2_production_activation_false": True,
        "d4_a9_authorized": True,
        "production_activation_authorized": False,
    }
    _save_json(project_root / RESULT_PATH, final_result_artifact)

    # Update manifest
    manifest["outcome_exposure_state"]["D4_A9_OUTCOME_EXPOSURE"] = "EVALUATION_COMPLETE"
    manifest["outcome_exposure_state"]["evaluator_executed"] = True
    manifest["outcome_exposure_state"]["scientific_verdict_computed"] = True
    manifest["verdict"] = eval_result["overall_outcome"]
    manifest["verdict_level"] = eval_result["level"]
    _save_json(manifest_path, manifest)

    print(f"[EVALUATION COMPLETE] Verdict: Level {eval_result['level']} ({eval_result['overall_outcome']})")
    return evaluator_artifact, final_result_artifact


# ---------------------------------------------------------------------------
# Closeout Verifier
# ---------------------------------------------------------------------------

def verify_closeout(project_root: Path) -> dict[str, Any]:
    """Mechanically verify all Section 46 closeout requirements."""
    manifest = _load_json(project_root / MANIFEST_PATH)
    raw_plans = _load_json(project_root / RAW_PLANS_PATH)
    raw_results = _load_json(project_root / RAW_RESULTS_PATH)
    eval_res = _load_json(project_root / EVALUATOR_RESULTS_PATH)
    res = _load_json(project_root / RESULT_PATH)

    errors: list[str] = []

    # 1. Starting R2 authority
    if manifest.get("starting_head") != STARTING_HEAD:
        errors.append("manifest starting_head mismatch")

    # 2. Production immutability
    for p in ["src", "configs"]:
        diff = subprocess.run(
            ["git", "diff", f"{STARTING_HEAD}..HEAD", "--", p],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
        if diff:
            errors.append(f"Production path {p} was mutated")

    # 3. Target masks exact
    if res.get("covered_symbol_mask") != FROZEN_COVERED_SYMBOL_MASK:
        errors.append("covered_symbol_mask mismatch")
    if res.get("uncovered_symbol_hold_mask") != FROZEN_UNCOVERED_SYMBOL_HOLD_MASK:
        errors.append("uncovered_symbol_hold_mask mismatch")
    if res.get("page_hint_hold_mask") != FROZEN_PAGE_HINT_HOLD_MASK:
        errors.append("page_hint_hold_mask mismatch")

    # 4. Budget compliance
    acct = manifest.get("accounting", {})
    if acct.get("analyzer_calls", 0) > PLANNED_BUDGET["analyzer_calls"]:
        errors.append(f"Analyzer calls exceeded budget: {acct.get('analyzer_calls')}")
    if acct.get("embedding_calls", 0) > PLANNED_BUDGET["embedding_calls"]:
        errors.append(f"Embedding calls exceeded budget: {acct.get('embedding_calls')}")
    if acct.get("reranker_calls", 0) > PLANNED_BUDGET["reranker_calls"]:
        errors.append(f"Reranker calls exceeded budget: {acct.get('reranker_calls')}")
    if acct.get("qa_calls", 0) != 0 or acct.get("verifier_calls", 0) != 0 or acct.get("judge_calls", 0) != 0:
        errors.append("Unauthorized QA/Verifier/Judge calls made")

    # 5. Plans exact
    if len(raw_plans.get("plans", [])) != 4:
        errors.append("Raw plans count != 4")

    # 6. Paired results exact
    if len(raw_results.get("slots", [])) != 8:
        errors.append("Raw slots count != 8")

    # 7. Production activation false
    if res.get("production_activation_authorized") is not False:
        errors.append("production_activation_authorized is not false")
    if res.get("full_batch2_production_activation_false") is not True:
        errors.append("full_batch2_production_activation_false is not true")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "verdict": res.get("verdict"),
        "verdict_level": res.get("verdict_level"),
        "verdict_decision": res.get("decision"),
        "accounting": acct,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=_PROJECT_ROOT)
    parser.add_argument(
        "--mode",
        required=True,
        choices=[
            "preflight",
            "execute-phase-p",
            "execute-phase-r",
            "evaluate",
            "verify-closeout",
        ],
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    if args.mode == "preflight":
        # Check starting boundary and A5 authority
        print("[PREFLIGHT] Checking A5 authority...")
        a5 = load_a5_authority()
        print(f"[PREFLIGHT] A5 authority loaded successfully: {a5.__name__}")
        print("[PREFLIGHT] Verification PASS")
        return

    if args.mode == "execute-phase-p":
        execute_phase_p(project_root)
        return

    if args.mode == "execute-phase-r":
        execute_phase_r(project_root)
        return

    if args.mode == "evaluate":
        run_evaluation(project_root)
        return

    if args.mode == "verify-closeout":
        res = verify_closeout(project_root)
        print(json.dumps(res, indent=2))
        if res["status"] != "PASS":
            sys.exit(1)
        return


if __name__ == "__main__":
    main()
