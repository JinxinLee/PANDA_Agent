"""Static validation and contract utilities for D4-A4 Second-Batch Low-Risk Locator Retirement.

Provides mechanical audit, provenance subtraction projection, evidence-group denominator
computation, and the complete deterministic verdict precedence evaluator for Batch 2.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence
import math


EXPECTED_HEAD = "631a66c125e8d58fee24bd448f868b4a8e423ab6"
EXPECTED_PARENT = "8c0971f20f9a2b2680451e3123fa1d95325816bc"
EXPECTED_RULE_COUNT = 54

BATCH1_MIGRATED_RULES = (
    "event_poca_handoff",
    "restgas_profile_workflow",
)

CANDIDATE_RULE_IDS = (
    "effective_acceptance_pipeline",
    "root_macro_usage",
    "model_factory_theory",
)

ALL_7_HISTORICAL_CASES = (
    "g052",
    "g055",
    "n003",
    "n004",
    "g007",
    "n014",
    "g060",
)

ANSWERED_CASES = (
    "g052",
    "g055",
    "n003",
    "n004",
    "n014",
    "g060",
)

NEGATIVE_CONTROL_CASES = (
    "g007",
)

FROZEN_RETIREMENT_MASKS: dict[str, dict[str, Any]] = {
    "effective_acceptance_pipeline": {
        "rule_id": "effective_acceptance_pipeline",
        "symbols_retired": [
            "macro/target/prod_sim_hvmaps.C",
            "data/PndLmdAcceptance.cxx",
            "model/PndLmdModelFactory.cxx",
        ],
        "paper_page_hints_retired": {},
        "symbols_preserved": [],
        "paper_page_hints_preserved": {
            "li_2026": [83, 86, 89],
        },
        "triggers_preserved": [
            "effective acceptance",
            "restgas acceptance",
            "acceptance calculation",
            "有效接受度",
            "有效接受度",
        ],
        "repositories_preserved": [
            "restgas_determination",
            "luminosityfit",
        ],
        "concepts_preserved": [
            "profile-dependent effective acceptance pipeline",
        ],
        "structured_replacement_after_retirement": False,
    },
    "root_macro_usage": {
        "rule_id": "root_macro_usage",
        "symbols_retired": [
            "Running/Macros.html",
            "tools/MasterTasks/PndMasterRunSim.cxx",
        ],
        "paper_page_hints_retired": {},
        "symbols_preserved": [],
        "paper_page_hints_preserved": {},
        "triggers_preserved": [
            "ROOT macro",
            "macro execution",
            "run a ROOT macro",
        ],
        "repositories_preserved": [
            "pandaroot",
        ],
        "concepts_preserved": [
            "PandaRoot macro invocation",
        ],
        "structured_replacement_after_retirement": False,
    },
    "model_factory_theory": {
        "rule_id": "model_factory_theory",
        "symbols_retired": [
            "model/PndLmdDPMAngModel1D.cxx",
            "model/PndLmdDPMAngModel2D.cxx",
            "model/PndLmdModelFactory.cxx",
        ],
        "paper_page_hints_retired": {
            "pflueger_2017": [51, 57, 65],
        },
        "symbols_preserved": [],
        "paper_page_hints_preserved": {},
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
    },
}

DEFAULT_METRIC_BOUNDED_TOLERANCES: dict[str, float] = {
    "recall_at_5": -0.05,
    "recall_at_10": -0.05,
    "recall_at_20": -0.05,
    "combined_candidate_recall": -0.05,
    "final_evidence_recall": -0.05,
    "critical_final_evidence_recall": 0.0,
}

PAIR_PHENOTYPES = {
    "PAIR_PRESERVED": "T/T",
    "PAIR_RETIREMENT_RECOVERY": "F/T",
    "PAIR_RETIREMENT_REGRESSION": "T/F",
    "PAIR_UNRESOLVED_BOTH": "F/F",
}

PER_RULE_DISPOSITIONS = (
    "RETIREMENT_VALIDATED",
    "DEPENDENCY_OBSERVED_RETAIN",
    "INCONCLUSIVE_BASELINE_NOT_REPRODUCED",
    "INVALID_PROTOCOL",
)

BATCH_VERDICT_LEVELS = {
    1: "INVALID / BATCH2_PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED",
    2: "INCONCLUSIVE / BATCH2_REFERENCE_BASELINE_NOT_REPRODUCED",
    3: "PARTIAL / SOME_RETIREMENT_CANDIDATES_RETAIN_DEPENDENCY",
    4: "FAIL / BATCH2_CRITICAL_OR_GROUNDING_REGRESSION",
    5: "PARTIAL / BATCH2_AGGREGATE_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE",
    6: "PASS / SECOND_BATCH_LOW_RISK_RETIREMENT_VALIDATED",
}


def audit_starting_boundary(rules: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Audit rule counts and Batch 1 production activation markers."""
    total_rules = len(rules)
    sr_true = [
        r.get("rule_id") for r in rules if r.get("structured_replacement") is True
    ]
    sr_other = [
        r.get("rule_id")
        for r in rules
        if r.get("structured_replacement") not in (False, None)
        and r.get("rule_id") not in sr_true
    ]
    valid = (
        total_rules == EXPECTED_RULE_COUNT
        and sorted(sr_true) == sorted(BATCH1_MIGRATED_RULES)
        and len(sr_other) == 0
    )
    return {
        "valid": valid,
        "total_rules": total_rules,
        "batch1_active_rules": sr_true,
        "unexpected_structured_replacement_rules": sr_other,
    }


def audit_candidate_drift(
    current_rules: Sequence[Mapping[str, Any]],
    d4_a0_inventory_rules: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Audit the 3 historical candidates for material semantic drift."""
    cur_map = {r.get("rule_id"): r for r in current_rules}
    inv_map = {r.get("rule_id"): r for r in d4_a0_inventory_rules}

    per_candidate = {}
    all_clean = True
    for cid in CANDIDATE_RULE_IDS:
        c_rule = cur_map.get(cid)
        i_rule = inv_map.get(cid)
        if c_rule is None or i_rule is None:
            all_clean = False
            per_candidate[cid] = {"exists": False}
            continue

        t_match = c_rule.get("triggers") == i_rule.get("triggers")
        r_match = c_rule.get("repositories") == i_rule.get("repositories")
        c_match = c_rule.get("concepts") == i_rule.get("concepts")
        s_match = c_rule.get("symbols") == i_rule.get("symbols")

        c_hints = c_rule.get("paper_page_hints") or {}
        i_hints = i_rule.get("paper_page_hints") or {}
        h_match = c_hints == i_hints

        sr_false = c_rule.get("structured_replacement") in (False, None)
        cand_clean = t_match and r_match and c_match and s_match and h_match and sr_false
        if not cand_clean:
            all_clean = False

        per_candidate[cid] = {
            "exists": True,
            "triggers_match": t_match,
            "repositories_match": r_match,
            "concepts_match": c_match,
            "symbols_match": s_match,
            "paper_page_hints_match": h_match,
            "structured_replacement_is_false": sr_false,
            "material_drift": not cand_clean,
            "disposition": "SELECTED" if cand_clean else "HOLD / CURRENT_STATE_DRIFT_REQUIRES_REASSESSMENT",
        }
    return {
        "all_clean": all_clean,
        "candidates": per_candidate,
    }


def audit_component_occurrences(
    rules: Sequence[Mapping[str, Any]],
    candidate_symbols: Sequence[str],
    candidate_page_hints: Sequence[tuple[str, Sequence[int]]],
) -> dict[str, Any]:
    """Audit occurrences of candidate locators across all rules."""
    symbol_audit = {}
    for sym in candidate_symbols:
        rules_with_sym = [r.get("rule_id") for r in rules if sym in (r.get("symbols") or [])]
        b2_rules = [r for r in rules_with_sym if r in CANDIDATE_RULE_IDS]
        non_b2_rules = [r for r in rules_with_sym if r not in CANDIDATE_RULE_IDS]
        symbol_audit[sym] = {
            "all_rules": rules_with_sym,
            "total_occurrences": len(rules_with_sym),
            "batch2_rules": b2_rules,
            "non_batch2_rules_untouched": non_b2_rules,
        }

    hint_audit = {}
    for paper, pages in candidate_page_hints:
        exact_matches = []
        for r in rules:
            h = r.get("paper_page_hints") or {}
            if paper in h and list(h[paper]) == list(pages):
                exact_matches.append(r.get("rule_id"))
        key = f"{paper}: {pages}"
        hint_audit[key] = {
            "paper": paper,
            "pages": list(pages),
            "exact_matching_rules": exact_matches,
            "batch2_rules": [r for r in exact_matches if r in CANDIDATE_RULE_IDS],
            "non_batch2_rules_untouched": [r for r in exact_matches if r not in CANDIDATE_RULE_IDS],
            "page_occurrences": {
                str(page): [r["rule_id"] for r in rules
                            if page in (r.get("paper_page_hints") or {}).get(paper, [])]
                for page in pages
            },
        }
    return {
        "symbols": symbol_audit,
        "paper_page_hints": hint_audit,
    }


def compute_deterministic_rule_matches(
    question: str,
    rules: Sequence[Mapping[str, Any]],
) -> list[str]:
    """Match rules via deterministic casefolded trigger substrings."""
    lowered = question.casefold()
    matched = []
    for r in rules:
        triggers = r.get("triggers", [])
        if any(str(t).casefold() in lowered for t in triggers):
            matched.append(str(r.get("rule_id")))
    return matched


def subtract_batch2_provenance(
    candidate_locators_with_provenance: Sequence[Mapping[str, Any]],
    matched_selected_batch2_rules: Sequence[str],
    retirement_masks: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Arm-specific execution projection with source-native provenance subtraction.

    Removes a locator contribution if and only if all its provenance sources belong
    to the retired mask of the active Batch-2 rules. If independently supported by
    a non-Batch2 rule or explicit query/analyzer origin, the locator is preserved.
    """
    masks = retirement_masks or FROZEN_RETIREMENT_MASKS

    retired_symbols_for_case: set[str] = set()
    retired_page_hints_for_case: set[tuple[str, int]] = set()
    for rid in matched_selected_batch2_rules:
        mask = masks.get(rid, {})
        for sym in mask.get("symbols_retired", []):
            retired_symbols_for_case.add(sym)
        for paper, pages in mask.get("paper_page_hints_retired", {}).items():
            for p in pages:
                retired_page_hints_for_case.add((paper, p))

    surviving_candidates: list[dict[str, Any]] = []
    for item in candidate_locators_with_provenance:
        item_copy = dict(item)
        origins = list(item_copy.get("provenance_origin_ids") or [])
        if not origins:
            raise ValueError("Complete contribution provenance is required before subtraction")
        locator_path = item_copy.get("locator_path") or item_copy.get("path")
        pdf_page = item_copy.get("pdf_page")
        source_id = item_copy.get("source_id")

        is_candidate_symbol = locator_path in retired_symbols_for_case
        is_candidate_hint = (source_id, pdf_page) in retired_page_hints_for_case

        if not is_candidate_symbol and not is_candidate_hint:
            surviving_candidates.append(item_copy)
            continue

        def retired_origin(origin: str) -> bool:
            if origin not in matched_selected_batch2_rules:
                return False
            mask = masks[origin]
            return (
                locator_path in mask.get("symbols_retired", [])
                or pdf_page in mask.get("paper_page_hints_retired", {}).get(source_id, [])
            )

        active_origins = [o for o in origins if not retired_origin(o)]
        if len(active_origins) > 0:
            item_copy["provenance_origin_ids"] = active_origins
            surviving_candidates.append(item_copy)
        else:
            pass

    return surviving_candidates


def classify_pair(before: bool, after: bool) -> str:
    if type(before) is not bool or type(after) is not bool:
        raise ValueError("Both evidence-presence inputs are required booleans")
    return {(True, True): "PAIR_PRESERVED", (False, True): "PAIR_RETIREMENT_RECOVERY",
            (True, False): "PAIR_RETIREMENT_REGRESSION", (False, False): "PAIR_UNRESOLVED_BOTH"}[(before, after)]


def classify_rule(*, protocol_valid: bool, baseline_reproduced: bool,
                  attributable_loss: bool) -> str:
    if any(type(v) is not bool for v in (protocol_valid, baseline_reproduced, attributable_loss)):
        return "INVALID_PROTOCOL"
    if not protocol_valid:
        return "INVALID_PROTOCOL"
    if attributable_loss:
        return "DEPENDENCY_OBSERVED_RETAIN"
    if not baseline_reproduced:
        return "INCONCLUSIVE_BASELINE_NOT_REPRODUCED"
    return "RETIREMENT_VALIDATED"


def evaluate_batch2_verdict(
    *,
    execution_valid: bool | None = None,
    protocol_violation: bool | None = None,
    missing_inputs: bool | None = None,
    plan_equality_all_verified: bool | None = None,
    analyzer_provider_calls_downstream: int | None = None,
    reference_baseline_valid: bool | None = None,
    per_rule_dispositions: Mapping[str, str] | None = None,
    critical_retirement_regressions: int | None = None,
    grounding_regressions: int | None = None,
    wrong_version_regressions: int | None = None,
    invalid_provenance_recoveries: int | None = None,
    metric_deltas: Mapping[str, float] | None = None,
    metric_tolerances: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Deterministic 6-level verdict precedence ladder for Batch 2 retirement validation."""
    flags = (execution_valid, protocol_violation, missing_inputs,
             plan_equality_all_verified, reference_baseline_valid)
    counters = (analyzer_provider_calls_downstream, critical_retirement_regressions,
                grounding_regressions, wrong_version_regressions, invalid_provenance_recoveries)
    complete = (
        all(type(flag) is bool for flag in flags)
        and all(type(count) is int and count >= 0 for count in counters)
        and isinstance(per_rule_dispositions, Mapping)
        and set(per_rule_dispositions) == set(CANDIDATE_RULE_IDS)
        and all(d in PER_RULE_DISPOSITIONS for d in per_rule_dispositions.values())
        and isinstance(metric_deltas, Mapping)
        and set(DEFAULT_METRIC_BOUNDED_TOLERANCES) <= set(metric_deltas)
        and all(type(metric_deltas[k]) in (int, float) and math.isfinite(metric_deltas[k])
                and -1 <= metric_deltas[k] <= 1 for k in DEFAULT_METRIC_BOUNDED_TOLERANCES)
        and (metric_tolerances is None or dict(metric_tolerances) == DEFAULT_METRIC_BOUNDED_TOLERANCES)
    )
    if not complete:
        return {"verdict_level": 1, "verdict": BATCH_VERDICT_LEVELS[1],
                "verdict_status": "INVALID", "verdict_reason": "Incomplete or malformed frozen evaluator inputs."}
    # Level 1: Protocol / Shared Plan Failure / Missing Inputs
    if (
        not execution_valid
        or protocol_violation
        or missing_inputs
        or not plan_equality_all_verified
        or analyzer_provider_calls_downstream > 0
        or per_rule_dispositions is None
        or len(per_rule_dispositions) == 0
        or any(d == "INVALID_PROTOCOL" for d in per_rule_dispositions.values())
    ):
        return {
            "verdict_level": 1,
            "verdict": BATCH_VERDICT_LEVELS[1],
            "verdict_status": "INVALID",
            "verdict_reason": "Protocol violation, execution invalid, missing inputs, shared plan inequality, or downstream Analyzer call observed.",
        }

    # Level 2: Reference Baseline Not Reproduced
    if (
        not reference_baseline_valid
        or any(d == "INCONCLUSIVE_BASELINE_NOT_REPRODUCED" for d in per_rule_dispositions.values())
    ):
        return {
            "verdict_level": 2,
            "verdict": BATCH_VERDICT_LEVELS[2],
            "verdict_status": "INCONCLUSIVE",
            "verdict_reason": "Reference baseline in CURRENT_COMPAT failed to reproduce expected evidence.",
        }

    # Safety checks
    has_safety_violation = (
        critical_retirement_regressions > 0
        or grounding_regressions > 0
        or wrong_version_regressions > 0
        or invalid_provenance_recoveries > 0
    )

    has_retained_dependency = any(
        d == "DEPENDENCY_OBSERVED_RETAIN" for d in per_rule_dispositions.values()
    )

    # Level 3: PARTIAL if some retirement candidates retain dependency WITHOUT safety violation
    if has_retained_dependency and not has_safety_violation:
        retained = [r for r, d in per_rule_dispositions.items() if d == "DEPENDENCY_OBSERVED_RETAIN"]
        return {
            "verdict_level": 3,
            "verdict": BATCH_VERDICT_LEVELS[3],
            "verdict_status": "PARTIAL",
            "verdict_reason": f"Observed retirement dependency on rule(s) {retained}; locator component(s) must be retained pending further decision.",
        }

    # Level 4: FAIL if any critical safety regression occurred (including safety + partial dependency)
    if has_safety_violation:
        violations = []
        if critical_retirement_regressions > 0:
            violations.append(f"critical_retirement_regressions={critical_retirement_regressions}")
        if grounding_regressions > 0:
            violations.append(f"grounding_regressions={grounding_regressions}")
        if wrong_version_regressions > 0:
            violations.append(f"wrong_version_regressions={wrong_version_regressions}")
        if invalid_provenance_recoveries > 0:
            violations.append(f"invalid_provenance_recoveries={invalid_provenance_recoveries}")
        return {
            "verdict_level": 4,
            "verdict": BATCH_VERDICT_LEVELS[4],
            "verdict_status": "FAIL",
            "verdict_reason": f"Strict retirement safety rule violated: {', '.join(violations)}.",
        }

    # Level 5: PARTIAL if aggregate bounded tolerance exceeded
    tols = dict(DEFAULT_METRIC_BOUNDED_TOLERANCES)
    if metric_tolerances:
        tols.update(metric_tolerances)

    has_aggregate_regression = False
    exceeded_metrics = []
    if metric_deltas is not None:
        for metric_name, tol in tols.items():
            delta = metric_deltas.get(metric_name)
            if delta is not None and delta < tol:
                has_aggregate_regression = True
                exceeded_metrics.append(f"{metric_name} delta {delta:.4f} < {tol:.4f}")

    if has_aggregate_regression:
        return {
            "verdict_level": 5,
            "verdict": BATCH_VERDICT_LEVELS[5],
            "verdict_status": "PARTIAL",
            "verdict_reason": f"Aggregate retrieval regression exceeds bounded tolerance: {', '.join(exceeded_metrics)}.",
        }

    # Level 6: PASS if all candidate rules validated and all gates satisfied
    if all(d == "RETIREMENT_VALIDATED" for d in per_rule_dispositions.values()):
        return {
            "verdict_level": 6,
            "verdict": BATCH_VERDICT_LEVELS[6],
            "verdict_status": "PASS",
            "verdict_reason": "Second-batch low-risk retirement validated: all candidates validated with zero critical/grounding/version/provenance regressions and all bounded tolerances satisfied.",
        }

    # Fallback to PARTIAL for any unclassified non-passing disposition
    return {
        "verdict_level": 3,
        "verdict": BATCH_VERDICT_LEVELS[3],
        "verdict_status": "PARTIAL",
        "verdict_reason": "Non-passing rule disposition without critical safety violation.",
    }
