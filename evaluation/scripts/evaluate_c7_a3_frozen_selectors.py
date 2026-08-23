"""Frozen-only C7-A3 selector evaluator.

It accepts capture rows and A3-authorized annotations as injected data. Default
module import and CLI parsing never load annotations or execute a real cohort.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
import argparse
import ast
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Mapping, Sequence

from evaluation.scripts.capture_c7_a2_post_reranker import (
    A1_REFERENCE,
    EXPECTED_COHORT_IDS,
    EXPECTED_HEAD,
    HARD_GATE_DEFINITIONS,
    PRIMARY_METRIC_DEFINITIONS,
    SECONDARY_METRIC_DEFINITIONS,
)

S0_POLICY_ID = "CURRENT_SELECTOR"
S1_POLICY_ID = "c7.explicit_selection.v1"
PRIMARY_METRICS = tuple(PRIMARY_METRIC_DEFINITIONS)
SECONDARY_METRICS = tuple(SECONDARY_METRIC_DEFINITIONS)
GATE_NAMES = tuple(definition["name"] for definition in HARD_GATE_DEFINITIONS.values())
NOT_SUPPORTED = "NOT_SUPPORTED"
HIGHER_IS_BETTER = "HIGHER_IS_BETTER"
LOWER_IS_BETTER = "LOWER_IS_BETTER"
PRIMARY_METRIC_DIRECTIONS = {
    "final_evidence_recall": HIGHER_IS_BETTER,
    "critical_evidence_retention": HIGHER_IS_BETTER,
    "explicit_required_satisfaction": HIGHER_IS_BETTER,
    "selector_caused_relevant_displacement": LOWER_IS_BETTER,
    "protected_exact_retention": HIGHER_IS_BETTER,
}
A2R1_REPAIR_SOURCE_HEAD = "4a31540151b7b7cedb11da361ffce22907c9d34f"
MICRO_AGGREGATION_CONTRACT = {
    "final_evidence_recall": "micro retained case-scoped relevant groups / annotated case-scoped relevant groups; zero denominator value 1.0",
    "critical_evidence_retention": "micro retained case-scoped critical groups / annotated case-scoped critical groups; zero denominator value 1.0",
    "explicit_required_satisfaction": "micro satisfied case-scoped explicit-query-reference target repository constraints / total such constraints; zero denominator value 1.0",
    "selector_caused_relevant_displacement": "micro displaced case-scoped exposed relevant groups / exposed case-scoped relevant groups; zero denominator rate 0.0",
    "protected_exact_retention": "micro retained case-scoped captured mandatory object IDs / captured mandatory object IDs; zero denominator value 1.0",
}
IDENTITY_LEVEL_GATE_CORRECTIONS = {
    "GATE_4": "S0-retained minus S1-retained case-scoped critical group identities must be empty",
    "GATE_5": "S0-retained minus S1-retained case-scoped mandatory object identities must be empty",
    "GATE_6": "S1 micro satisfaction >= S0 and S0-satisfied minus S1-satisfied case-scoped REQUIRED identities must be empty",
}
SOURCE_TYPE_DIAGNOSTIC_CORRECTION = "classify with panda_agent.evidence_selection._source_type_of; report source ID and source type diversity separately"
ROOT = Path(__file__).resolve().parents[2]
A1_CONTRACT_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c7_a1_explicit_selection_contract_v1.json"
S1_SOURCE_PATH = ROOT / "src/panda_agent/evidence_selection.py"


def _forbidden(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(any(token in str(key).casefold() for token in ("gold", "relevant", "critical", "s1", "win", "loss", "outcome")) or _forbidden(item) for key, item in value.items())
    if isinstance(value, list): return any(_forbidden(item) for item in value)
    return False


def validate_capture_schema(record: Mapping[str, Any]) -> None:
    required = {"question", "frozen_plan", "stage_f_order", "stage_r_order", "stage_p_order", "candidate_payloads", "retrieval_channels", "exact_stream_order", "mandatory_symbol_ids", "current_s0", "final_evidence_limit"}
    if missing := required - set(record): raise ValueError(f"missing frozen selector input: {sorted(missing)}")
    if _forbidden(record): raise ValueError("A2 capture contains a forbidden outcome field")


def _policy_id_from_source(source: str) -> str | None:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "POLICY_ID":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        return node.value.value
    return None


def static_s1_contract_proof(
    preregistration: Mapping[str, Any],
    *,
    contract_path: Path = A1_CONTRACT_PATH,
    selector_path: Path = S1_SOURCE_PATH,
) -> dict[str, Any]:
    """Bind Gate 11 to the authoritative contract and unchanged selector source."""
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    correction = contract.get("a1r1_semantics_correction", {})
    source = selector_path.read_text(encoding="utf-8")
    relative_selector = selector_path.relative_to(ROOT).as_posix()
    source_unchanged = subprocess.run(
        ["git", "diff", "--quiet", str(preregistration.get("source_head", "")), "--", relative_selector],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    checks = {
        "preregistered_policy_id": preregistration.get("s1_identity") == S1_POLICY_ID,
        "authoritative_reference": preregistration.get("a1_a1r1_reference") == A1_REFERENCE,
        "contract_policy_id": contract.get("policy_id") == S1_POLICY_ID,
        "a1r1_authoritative": correction.get("authoritative_after_a1r1") is True,
        "source_policy_id": _policy_id_from_source(source) == S1_POLICY_ID,
        "source_unchanged_from_preregistered_head": source_unchanged,
        "no_case_gold_benchmark_rule": re.search(
            r"\bg\d{3}\b|\bgold\b|\bbenchmark\b", source, re.IGNORECASE
        ) is None,
    }
    return {"passed": all(checks.values()), "checks": checks}


def preregistration_integrity(preregistration: Mapping[str, Any]) -> dict[str, Any]:
    correction = preregistration.get("a2r1_evaluator_semantics_correction", {})
    checks = {
        "source_head": preregistration.get("source_head") == EXPECTED_HEAD,
        "cohort": preregistration.get("frozen_cohort_case_ids") == list(EXPECTED_COHORT_IDS),
        "cohort_frozen_before_capture": preregistration.get("cohort_frozen_before_live_capture") is True,
        "no_gold_cohort": preregistration.get("no_gold_used_for_cohort") is True,
        "s0_identity": preregistration.get("s0_identity") == S0_POLICY_ID,
        "s1_identity": preregistration.get("s1_identity") == S1_POLICY_ID,
        "primary_metrics": preregistration.get("primary_metrics") == PRIMARY_METRIC_DEFINITIONS,
        "secondary_metrics": preregistration.get("secondary_metrics") == SECONDARY_METRIC_DEFINITIONS,
        "hard_gates": preregistration.get("hard_gates") == HARD_GATE_DEFINITIONS,
        "outcomes_not_run_in_a2": preregistration.get("outcome_evaluation_executed") is False,
        "s1_not_run_in_a2": preregistration.get("s1_real_cohort_execution") is False,
        "correction_task": correction.get("task") == "C7-A2R1",
        "repair_source_head": correction.get("repair_source_head") == A2R1_REPAIR_SOURCE_HEAD,
        "pre_outcome_repair": correction.get("no_outcome_observed_before_repair") is True,
        "capture_reused": correction.get("capture_reused_unchanged") is True and correction.get("capture_rerun") is False,
        "metric_directions": correction.get("metric_direction_map") == PRIMARY_METRIC_DIRECTIONS,
        "micro_aggregation": correction.get("micro_aggregation_contract") == MICRO_AGGREGATION_CONTRACT,
        "identity_gates": correction.get("identity_level_gate_corrections") == IDENTITY_LEVEL_GATE_CORRECTIONS,
        "source_type_diagnostic": correction.get("source_type_diagnostic_correction") == SOURCE_TYPE_DIAGNOSTIC_CORRECTION,
        "production_unchanged": correction.get("production_behavior_changed") is False,
        "zero_gold": correction.get("gold_outcome_evaluations") == 0,
        "zero_real_s1": correction.get("real_cohort_s1_executions") == 0,
        "a2r1_pass": correction.get("a2r1_verdict") == "PASS",
        "a2r1_authoritative": correction.get("authoritative_after_a2r1") is True,
        "a2_pass_after_repair": preregistration.get("a2_verdict") == "PASS_AFTER_EVALUATOR_REPAIR",
        "a3_next": preregistration.get("a3_eligibility") == "NEXT_ELIGIBLE / NOT_STARTED",
    }
    return {"passed": all(checks.values()), "checks": checks}


def build_s1_frozen_input(record: Mapping[str, Any]) -> Any:
    validate_capture_schema(record)
    from panda_agent.evidence_selection import FrozenShadowInput
    return FrozenShadowInput(plan=record["frozen_plan"], stage_r_order=tuple(record["stage_r_order"]), stage_f_order=tuple(record["stage_f_order"]), payloads=record["candidate_payloads"], retrieval_channels=record["retrieval_channels"], mandatory_symbol_ids=frozenset(record["mandatory_symbol_ids"]))


def run_s1_offline(record: Mapping[str, Any]) -> dict[str, Any]:
    from panda_agent.evidence_selection import shadow_select, translate_current_policy
    frozen = build_s1_frozen_input(record); policy = translate_current_policy(frozen.plan, int(record["final_evidence_limit"]), frozen.mandatory_symbol_ids)
    if policy.policy_id != S1_POLICY_ID: raise ValueError("unexpected S1 policy identity")
    return shadow_select(frozen, policy).as_dict()


def run_s0_offline(record: Mapping[str, Any], *, runner: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None) -> Mapping[str, Any]:
    if runner is not None: return runner(record)
    from evaluation.scripts.capture_c7_a2_post_reranker import replay_s0
    return replay_s0(record)


def _groups(selected: Sequence[str], annotations: Mapping[str, Any], key: str) -> set[str]:
    object_groups = annotations.get(key, annotations.get("required_groups_by_object", {}) if key == "relevant_groups_by_object" else {})
    return {group for object_id in selected for group in object_groups.get(object_id, ())}


def _ratio(hits: set[str], universe: set[str]) -> float:
    return len(hits & universe) / len(universe) if universe else 1.0


def selector_displacement(selected: Sequence[str], annotations: Mapping[str, Any], receipts: Sequence[Mapping[str, Any]], candidate_universe: Sequence[str]) -> dict[str, Any]:
    """Measure relevant-group loss caused after the frozen candidate universe exists."""
    relevant_universe = set(annotations.get("relevant_groups", annotations.get("required_groups", ())))
    present_groups = _groups(candidate_universe, annotations, "relevant_groups_by_object") & relevant_universe
    selected_groups = _groups(selected, annotations, "relevant_groups_by_object") & relevant_universe
    displaced_groups = sorted(present_groups - selected_groups)
    receipt_by_id = {row["object_id"]: row for row in receipts}
    object_groups = annotations.get("relevant_groups_by_object", annotations.get("required_groups_by_object", {}))
    displaced_receipts = []
    for group in displaced_groups:
        candidate_ids = sorted(object_id for object_id in candidate_universe if group in object_groups.get(object_id, ()))
        displaced_receipts.append({
            "group": group,
            "candidate_ids": candidate_ids,
            "candidate_reasons": {
                object_id: receipt_by_id.get(object_id, {}).get("decision_reason", "not_selected")
                for object_id in candidate_ids
            },
        })
    return {
        "count": len(displaced_groups),
        "groups": displaced_groups,
        "present_groups": sorted(present_groups),
        "selected_groups": sorted(selected_groups),
        "receipts": displaced_receipts,
    }


def _forced_irrelevant_evidence(
    s0_selected: Sequence[str],
    s1_selected: Sequence[str],
    annotations: Mapping[str, Any],
    s1_receipts: Sequence[Mapping[str, Any]],
    s1_displacement: Mapping[str, Any],
) -> dict[str, Any]:
    known_irrelevant = set(annotations.get("known_irrelevant_object_ids", ()))
    if not annotations.get("negative_completeness") or not known_irrelevant:
        return {"status": NOT_SUPPORTED, "count": None, "candidate_ids": [], "displaced_relevant_groups": []}
    receipt_by_id = {row["object_id"]: row for row in s1_receipts}
    forced = []
    for object_id in sorted(set(s1_selected) - set(s0_selected)):
        receipt = receipt_by_id.get(object_id, {})
        override = (
            receipt.get("decision_reason") in {"required_override", "protected_override"}
            or receipt.get("required_override") is True
            or receipt.get("protected_override") is True
        )
        if object_id in known_irrelevant and override and s1_displacement.get("groups"):
            forced.append(object_id)
    return {
        "status": "SUPPORTED",
        "count": len(forced),
        "candidate_ids": forced,
        "displaced_relevant_groups": list(s1_displacement.get("groups", ())),
    }


def _explicit_required(plan: Mapping[str, Any]) -> set[str]:
    diagnostics = plan.get("analysis_diagnostics", {}) or {}
    provenance = diagnostics.get("deterministic_parse", {}).get("provenance", {}) if isinstance(diagnostics, Mapping) else {}
    targets = set(plan.get("target_repositories", ()) or ())
    return {row.get("value") for row in provenance.get("target_repositories", ()) if isinstance(row, Mapping) and row.get("source") == "explicit_query_reference" and row.get("value") in targets}


def _required_satisfaction(selected: Sequence[str], payloads: Mapping[str, Mapping[str, Any]], plan: Mapping[str, Any]) -> float:
    required = _explicit_required(plan)
    if not required: return 1.0
    selected_sources = {payloads[object_id].get("source_id") for object_id in selected}
    return len(required & selected_sources) / len(required)


def _source_type(payload: Mapping[str, Any]) -> str:
    from panda_agent.evidence_selection import _source_type_of
    return _source_type_of(payload)


def _source_diversity(selected: Sequence[str], payloads: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    return {
        "source_id_count": len({payloads[object_id].get("source_id") for object_id in selected}),
        "source_type_count": len({_source_type(payloads[object_id]) for object_id in selected}),
    }


def _first_relevant_rank(selected: Sequence[str], annotations: Mapping[str, Any]) -> int | None:
    for rank, object_id in enumerate(selected, 1):
        if annotations.get("relevant_groups_by_object", annotations.get("required_groups_by_object", {})).get(object_id, ()): return rank
    return None


def _concentration(selected: Sequence[str], payloads: Mapping[str, Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(Counter(str(payloads[object_id].get(field, "")) for object_id in selected))


def _source_type_concentration(selected: Sequence[str], payloads: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    return dict(Counter(_source_type(payloads[object_id]) for object_id in selected))


def _receipt_counts(receipts: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    reasons = [str(row.get("decision_reason", "")) for row in receipts]
    return {"maximum": sum(reason == "maximum" for reason in reasons), "required": sum(bool(row.get("required_representative")) for row in receipts), "protected": sum(bool(row.get("protected")) for row in receipts), "duplicate": sum(reason == "duplicate_locator" for reason in reasons), "final_limit": sum(reason == "final_evidence_limit" for reason in reasons), "preferred": sum(bool(row.get("preferred_match_without_admission_effect")) for row in receipts)}


def _channel_exposure(channel: str, selected: Sequence[str], record: Mapping[str, Any]) -> dict[str, Any]:
    candidates = [object_id for object_id, channels in record["retrieval_channels"].items() if channel in channels]
    return {"candidate_count": len(candidates), "selected_count": len(set(candidates) & set(selected)), "selected_object_ids": [object_id for object_id in selected if object_id in candidates]}


def _policy_checks(record: Mapping[str, Any], s1: Mapping[str, Any], rerun: Callable[[], Mapping[str, Any]]) -> dict[str, Any]:
    again = rerun()
    deterministic = all(
        s1.get(key) == again.get(key)
        for key in ("selected_object_ids", "candidate_receipts", "constraint_receipts")
    )
    graph_rows = [row for row in s1.get("constraint_receipts", ()) if row.get("dimension") == "RETRIEVAL_CHANNEL" and row.get("value") == "graph"]
    from panda_agent.evidence_selection import ConstraintType, translate_current_policy, shadow_select
    frozen = build_s1_frozen_input(record); policy = translate_current_policy(frozen.plan, int(record["final_evidence_limit"]), frozen.mandatory_symbol_ids)
    without_preferred = replace(policy, constraints=tuple(c for c in policy.constraints if c.constraint_type is not ConstraintType.PREFERRED))
    preferred_invariant = shadow_select(frozen, policy).selected_object_ids == shadow_select(frozen, without_preferred).selected_object_ids
    graph_maximum_rows = [row for row in graph_rows if row.get("constraint_type") == "MAXIMUM"]
    candidate_receipts = {row["object_id"]: row for row in s1.get("candidate_receipts", ())}
    graph_caused_membership_difference = any(
        candidate_receipts.get(object_id, {}).get("decision_reason") == "maximum"
        for row in graph_maximum_rows
        for object_id in row.get("matched_candidate_ids", ())
    )
    return {"deterministic": deterministic, "preferred_invariant": preferred_invariant, "graph_maximum_exposure": sum(len(row.get("matched_candidate_ids", ())) for row in graph_maximum_rows), "graph_caused_membership_difference": graph_caused_membership_difference, "graph_receipts": graph_maximum_rows}


def evaluate_frozen_case(record: Mapping[str, Any], annotations: Mapping[str, Any], *, s0_runner: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None, s1_runner: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Future A3-only same-input S0/S1 evaluation with injected annotations."""
    validate_capture_schema(record)
    s0 = run_s0_offline(record, runner=s0_runner)
    s1 = (s1_runner or run_s1_offline)(record)
    s1_again = lambda: (s1_runner or run_s1_offline)(record)
    s0_ids, s1_ids = list(s0["selected_object_ids"]), list(s1["selected_object_ids"])
    relevant = set(annotations.get("relevant_groups", annotations.get("required_groups", ())))
    critical = set(annotations.get("critical_groups", ()))
    final_s0 = _groups(s0_ids, annotations, "relevant_groups_by_object") & relevant
    final_s1 = _groups(s1_ids, annotations, "relevant_groups_by_object") & relevant
    critical_s0 = _groups(s0_ids, annotations, "critical_groups_by_object") & critical
    critical_s1 = _groups(s1_ids, annotations, "critical_groups_by_object") & critical
    candidate_universe = list(record["candidate_payloads"])
    protected = set(record["mandatory_symbol_ids"])
    retained_protected_s0, retained_protected_s1 = set(s0_ids) & protected, set(s1_ids) & protected
    explicit_required = _explicit_required(record["frozen_plan"])
    selected_sources_s0 = {record["candidate_payloads"][object_id].get("source_id") for object_id in s0_ids}
    selected_sources_s1 = {record["candidate_payloads"][object_id].get("source_id") for object_id in s1_ids}
    satisfied_required_s0 = explicit_required & selected_sources_s0
    satisfied_required_s1 = explicit_required & selected_sources_s1
    displacement = selector_displacement(s1_ids, annotations, s1.get("candidate_receipts", ()), candidate_universe)
    s0_displacement = selector_displacement(s0_ids, annotations, s0.get("candidate_receipts", ()), candidate_universe)
    if s0_displacement["present_groups"] != displacement["present_groups"]:
        raise ValueError("S0/S1 displacement denominator identity differs")
    checks = _policy_checks(record, s1, s1_again)
    s0_metrics = {"final_evidence_recall": _ratio(final_s0, relevant), "critical_evidence_retention": _ratio(critical_s0, critical), "protected_exact_retention": _ratio(retained_protected_s0, protected), "explicit_required_satisfaction": _ratio(satisfied_required_s0, explicit_required), "selector_caused_relevant_displacement": s0_displacement["count"]}
    s1_metrics = {"final_evidence_recall": _ratio(final_s1, relevant), "critical_evidence_retention": _ratio(critical_s1, critical), "protected_exact_retention": _ratio(retained_protected_s1, protected), "explicit_required_satisfaction": _ratio(satisfied_required_s1, explicit_required), "selector_caused_relevant_displacement": displacement["count"]}
    s0_support = {"relevant": {"universe": sorted(relevant), "hits": sorted(final_s0)}, "critical": {"universe": sorted(critical), "hits": sorted(critical_s0)}, "required": {"universe": sorted(explicit_required), "satisfied": sorted(satisfied_required_s0)}, "protected": {"universe": sorted(protected), "retained": sorted(retained_protected_s0)}, "displacement": {"exposed": s0_displacement["present_groups"], "displaced": s0_displacement["groups"]}}
    s1_support = {"relevant": {"universe": sorted(relevant), "hits": sorted(final_s1)}, "critical": {"universe": sorted(critical), "hits": sorted(critical_s1)}, "required": {"universe": sorted(explicit_required), "satisfied": sorted(satisfied_required_s1)}, "protected": {"universe": sorted(protected), "retained": sorted(retained_protected_s1)}, "displacement": {"exposed": displacement["present_groups"], "displaced": displacement["groups"]}}
    negative_complete = bool(annotations.get("negative_completeness"))
    relevant_by_object = annotations.get("relevant_groups_by_object", annotations.get("required_groups_by_object", {}))
    precision = lambda selected: sum(bool(relevant_by_object.get(object_id)) for object_id in selected) / len(selected) if selected else 1.0
    supported_precision = {"status": "SUPPORTED" if negative_complete else NOT_SUPPORTED, "s0": precision(s0_ids) if negative_complete else None, "s1": precision(s1_ids) if negative_complete else None}
    forced_irrelevant = _forced_irrelevant_evidence(s0_ids, s1_ids, annotations, s1.get("candidate_receipts", ()), displacement)
    return {"case_id": record.get("case_id"), "policies": {"s0": S0_POLICY_ID, "s1": S1_POLICY_ID}, "input_identity": {"stage_f": record["stage_f_order"], "stage_r": record["stage_r_order"], "payload_ids": sorted(record["candidate_payloads"]), "channels": record["retrieval_channels"], "exact_stream": record["exact_stream_order"]}, "s0": {"selected_object_ids": s0_ids, "metrics": s0_metrics, "metric_support": s0_support, "displacement": s0_displacement}, "s1": {"selected_object_ids": s1_ids, "metrics": s1_metrics, "metric_support": s1_support, "receipts": s1.get("candidate_receipts", ()), "constraint_receipts": s1.get("constraint_receipts", ()), "displacement": displacement}, "secondary": {"selected_set_delta": sorted(set(s0_ids) ^ set(s1_ids)), "evidence_counts": {"s0_selected": len(s0_ids), "s1_selected": len(s1_ids), "s0_relevant_groups": len(final_s0), "s1_relevant_groups": len(final_s1), "s0_critical_groups": len(critical_s0), "s1_critical_groups": len(critical_s1)}, "supported_precision": supported_precision, "forced_irrelevant_evidence": forced_irrelevant, "source_concentration": {"s0": {"source_id": _concentration(s0_ids, record["candidate_payloads"], "source_id"), "source_type": _source_type_concentration(s0_ids, record["candidate_payloads"])}, "s1": {"source_id": _concentration(s1_ids, record["candidate_payloads"], "source_id"), "source_type": _source_type_concentration(s1_ids, record["candidate_payloads"])}}, "source_diversity": {"s0": _source_diversity(s0_ids, record["candidate_payloads"]), "s1": _source_diversity(s1_ids, record["candidate_payloads"])}, "constraint_decision_counts": _receipt_counts(s1.get("candidate_receipts", ())), "required_receipts": [row for row in s1.get("constraint_receipts", ()) if row.get("constraint_type") == "REQUIRED"], "protected_receipts": [row for row in s1.get("constraint_receipts", ()) if row.get("constraint_type") == "PROTECTED"], "graph_exposure": {"s0": _channel_exposure("graph", s0_ids, record), "s1": _channel_exposure("graph", s1_ids, record)}, "workflow_exposure": {"s0": _channel_exposure("workflow", s0_ids, record), "s1": _channel_exposure("workflow", s1_ids, record)}, "first_relevant_rank": {"s0": _first_relevant_rank(s0_ids, annotations), "s1": _first_relevant_rank(s1_ids, annotations)}, "displacement_reasons": {"s0": s0_displacement, "s1": displacement}, **checks}}


def gate_matrix(s0: Mapping[str, Any], s1: Mapping[str, Any], *, forced_irrelevant_supported: bool = False) -> dict[str, str]:
    input_identity_pass = s0["input_identity"] == s1["input_identity"] and s1["displacement_denominator_identical"]
    displacement_pass = (
        s1["displacement_denominator_identical"]
        and s1["selector_displacement_count"] <= s0["selector_displacement_count"]
        and s1["selector_displacement_rate"] <= s0["selector_displacement_rate"]
    )
    return {
        GATE_NAMES[0]: "PASS" if input_identity_pass else "FAIL",
        GATE_NAMES[1]: "PASS" if not any(s1["upstream_calls"].values()) else "FAIL",
        GATE_NAMES[2]: "PASS" if s1["final_evidence_recall"] >= s0["final_evidence_recall"] else "FAIL",
        GATE_NAMES[3]: "PASS" if s1["new_critical_miss_count"] == 0 else "FAIL",
        GATE_NAMES[4]: "PASS" if s1["new_protected_loss_count"] == 0 else "FAIL",
        GATE_NAMES[5]: "PASS" if s1["explicit_required_satisfaction"] >= s0["explicit_required_satisfaction"] and s1["new_required_miss_count"] == 0 else "FAIL",
        GATE_NAMES[6]: "PASS" if displacement_pass else "FAIL",
        GATE_NAMES[7]: "PASS" if s1["version_source_violations"] == 0 else "FAIL",
        GATE_NAMES[8]: ("PASS" if s1["forced_irrelevant"] == 0 else "FAIL") if forced_irrelevant_supported else NOT_SUPPORTED,
        GATE_NAMES[9]: "PASS" if s1["deterministic"] and s1["preferred_invariant"] else "FAIL",
        GATE_NAMES[10]: "PASS" if s1["no_benchmark_specific_rule"] else "FAIL",
        GATE_NAMES[11]: "PASS" if s1["preregistration_intact"] else "FAIL",
    }


def _metric_value(metrics: Mapping[str, Any], name: str) -> float:
    value = metrics[name]
    return float(value["value"] if isinstance(value, Mapping) else value)


def _metric_changes(s0: Mapping[str, Any], s1: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    improved, regressed = [], []
    for name, direction in PRIMARY_METRIC_DIRECTIONS.items():
        before, after = _metric_value(s0, name), _metric_value(s1, name)
        if before == after:
            continue
        is_improvement = after > before if direction == HIGHER_IS_BETTER else after < before
        (improved if is_improvement else regressed).append(name)
    return improved, regressed


def meaningful_gain(s0: Mapping[str, Any], s1: Mapping[str, Any], gates: Mapping[str, str]) -> str:
    if any(value == "FAIL" for value in gates.values()):
        return "CURRENT_PREFERRED_GATE_FAILURE"
    improved, regressed = _metric_changes(s0, s1)
    return "DEVELOPMENT_SUPPORTED" if improved and not regressed else "NO_MEANINGFUL_GAIN/INCONCLUSIVE"


def case_direction(s0: Mapping[str, Any], s1: Mapping[str, Any]) -> str:
    improved, regressed = _metric_changes(s0, s1)
    return "regressed" if regressed else "improved" if improved else "unchanged"


def _case_scoped_identities(cases: Sequence[Mapping[str, Any]], policy: str, support: str, member: str) -> set[tuple[str, str]]:
    return {
        (str(row["case_id"]), str(value))
        for row in cases
        for value in row[policy]["metric_support"][support][member]
    }


def _identity_rows(identities: set[tuple[str, str]], identity_name: str) -> list[dict[str, str]]:
    return [{"case_id": case_id, identity_name: value} for case_id, value in sorted(identities)]


def aggregate_primary_metrics(cases: Sequence[Mapping[str, Any]], policy: str) -> dict[str, dict[str, Any]]:
    specifications = {
        "final_evidence_recall": ("relevant", "hits", "universe", 1.0, "group_id"),
        "critical_evidence_retention": ("critical", "hits", "universe", 1.0, "group_id"),
        "explicit_required_satisfaction": ("required", "satisfied", "universe", 1.0, "constraint_value"),
        "protected_exact_retention": ("protected", "retained", "universe", 1.0, "object_id"),
        "selector_caused_relevant_displacement": ("displacement", "displaced", "exposed", 0.0, "group_id"),
    }
    result: dict[str, dict[str, Any]] = {}
    for metric, (support, numerator_member, denominator_member, zero_value, identity_name) in specifications.items():
        numerator_ids = _case_scoped_identities(cases, policy, support, numerator_member)
        denominator_ids = _case_scoped_identities(cases, policy, support, denominator_member)
        if not numerator_ids <= denominator_ids:
            raise ValueError(f"{metric} numerator is not contained in its denominator")
        numerator, denominator = len(numerator_ids), len(denominator_ids)
        value = numerator / denominator if denominator else zero_value
        detail = {
            "value": value,
            "numerator": numerator,
            "denominator": denominator,
            "numerator_identities": _identity_rows(numerator_ids, identity_name),
            "denominator_identities": _identity_rows(denominator_ids, identity_name),
        }
        if metric == "selector_caused_relevant_displacement":
            detail.update({"count": numerator, "rate": value, "exposed_count": denominator})
        result[metric] = detail
    return result


def aggregate_receipts(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    directions = Counter(case_direction(row["s0"]["metrics"], row["s1"]["metrics"]) for row in cases)
    return {"case_count": len(cases), "direction_counts": dict(directions), "graph_maximum_exposure": sum(row["secondary"]["graph_maximum_exposure"] for row in cases), "selector_displacement_count": sum(row["s1"]["metrics"]["selector_caused_relevant_displacement"] for row in cases)}


def evaluate_frozen_cohort(records: Sequence[Mapping[str, Any]], annotations_by_case: Mapping[str, Mapping[str, Any]], *, s0_runner: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None, s1_runner: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None, preregistration: Mapping[str, Any]) -> dict[str, Any]:
    """Future A3 aggregate, limited to the same frozen A2 inputs for both policies."""
    cases = [evaluate_frozen_case(record, annotations_by_case[record["case_id"]], s0_runner=s0_runner, s1_runner=s1_runner) for record in records]
    s0_metrics = aggregate_primary_metrics(cases, "s0")
    s1_metrics = aggregate_primary_metrics(cases, "s1")
    s0_values = {metric: detail["value"] for metric, detail in s0_metrics.items()}
    s1_values = {metric: detail["value"] for metric, detail in s1_metrics.items()}
    frozen_identities = [row["input_identity"] for row in cases]
    invalid_selected = sum(
        any(
            object_id not in row_record["candidate_payloads"]
            or not row_record["candidate_payloads"][object_id].get("valid", True)
            or not row_record["candidate_payloads"][object_id].get("source_version_valid", True)
            or not row_record["candidate_payloads"][object_id].get("usable", True)
            for object_id in row["s1"]["selected_object_ids"]
        )
        for row, row_record in zip(cases, records)
    )
    contract_proof = static_s1_contract_proof(preregistration)
    preregistration_proof = preregistration_integrity(preregistration)
    forced_rows = [row["secondary"]["forced_irrelevant_evidence"] for row in cases]
    forced_irrelevant_supported = bool(forced_rows) and all(row["status"] == "SUPPORTED" for row in forced_rows)
    forced_irrelevant = sum(row["count"] or 0 for row in forced_rows) if forced_irrelevant_supported else None
    upstream_calls = {name: any(record.get("a3_call_ledger", {}).get(name, 0) for record in records) for name in ("retrieval", "reranker", "analyzer", "db", "qdrant")}
    s0_critical = _case_scoped_identities(cases, "s0", "critical", "hits")
    s1_critical = _case_scoped_identities(cases, "s1", "critical", "hits")
    s0_protected = _case_scoped_identities(cases, "s0", "protected", "retained")
    s1_protected = _case_scoped_identities(cases, "s1", "protected", "retained")
    s0_required = _case_scoped_identities(cases, "s0", "required", "satisfied")
    s1_required = _case_scoped_identities(cases, "s1", "required", "satisfied")
    new_critical_misses = s0_critical - s1_critical
    new_protected_losses = s0_protected - s1_protected
    new_required_misses = s0_required - s1_required
    s0_exposed = _case_scoped_identities(cases, "s0", "displacement", "exposed")
    s1_exposed = _case_scoped_identities(cases, "s1", "displacement", "exposed")
    displacement_denominator_identical = s0_exposed == s1_exposed
    gate_s0 = {"input_identity": frozen_identities, "final_evidence_recall": s0_values["final_evidence_recall"], "explicit_required_satisfaction": s0_values["explicit_required_satisfaction"], "selector_displacement_count": s0_metrics["selector_caused_relevant_displacement"]["count"], "selector_displacement_rate": s0_metrics["selector_caused_relevant_displacement"]["rate"]}
    gate_s1 = {"input_identity": frozen_identities, "upstream_calls": upstream_calls, "displacement_denominator_identical": displacement_denominator_identical, "final_evidence_recall": s1_values["final_evidence_recall"], "new_critical_miss_count": len(new_critical_misses), "new_protected_loss_count": len(new_protected_losses), "explicit_required_satisfaction": s1_values["explicit_required_satisfaction"], "new_required_miss_count": len(new_required_misses), "selector_displacement_count": s1_metrics["selector_caused_relevant_displacement"]["count"], "selector_displacement_rate": s1_metrics["selector_caused_relevant_displacement"]["rate"], "version_source_violations": invalid_selected, "forced_irrelevant": forced_irrelevant, "deterministic": all(row["secondary"]["deterministic"] for row in cases), "preferred_invariant": all(row["secondary"]["preferred_invariant"] for row in cases), "no_benchmark_specific_rule": contract_proof["passed"], "preregistration_intact": preregistration_proof["passed"]}
    gates = gate_matrix(gate_s0, gate_s1, forced_irrelevant_supported=forced_irrelevant_supported)
    identity_losses = {"new_critical_miss_count": len(new_critical_misses), "new_critical_miss_identities": _identity_rows(new_critical_misses, "group_id"), "new_protected_loss_count": len(new_protected_losses), "new_protected_loss_identities": _identity_rows(new_protected_losses, "object_id"), "new_required_miss_count": len(new_required_misses), "new_required_miss_identities": _identity_rows(new_required_misses, "constraint_value")}
    return {"per_case_receipts": cases, "aggregate": {**aggregate_receipts(cases), "s0_metrics": s0_metrics, "s1_metrics": s1_metrics, "s0_metric_values": s0_values, "s1_metric_values": s1_values, "identity_losses": identity_losses, "displacement_denominator_identical": displacement_denominator_identical, "forced_irrelevant_evidence": {"status": "SUPPORTED" if forced_irrelevant_supported else NOT_SUPPORTED, "count": forced_irrelevant}, "gate_11_static_proof": contract_proof, "gate_12_preregistration_proof": preregistration_proof}, "gates": gates, "role_decision": meaningful_gain(s0_metrics, s1_metrics, gates)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-a3", action="store_true", required=True)
    parser.add_argument("--capture-jsonl", type=Path, required=True)
    parser.add_argument("--annotations-json", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    args = parser.parse_args(argv)
    preregistration = json.loads(args.preregistration.read_text(encoding="utf-8"))
    if preregistration.get("a2_verdict") != "PASS_AFTER_EVALUATOR_REPAIR" or preregistration.get("a3_eligibility") != "NEXT_ELIGIBLE / NOT_STARTED":
        raise RuntimeError("A3 requires the authoritative pre-outcome A2R1 evaluator correction")
    from evaluation.scripts.capture_c7_a2_post_reranker import validate_artifacts
    if validate_artifacts(args.preregistration, args.capture_jsonl).get("status") != "PASS":
        raise RuntimeError("A3 requires a valid A2 manifest and capture JSONL")
    records = [json.loads(line) for line in args.capture_jsonl.read_text(encoding="utf-8").splitlines() if line]
    annotations = json.loads(args.annotations_json.read_text(encoding="utf-8"))
    print(json.dumps(evaluate_frozen_cohort(records, annotations, preregistration=preregistration), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
