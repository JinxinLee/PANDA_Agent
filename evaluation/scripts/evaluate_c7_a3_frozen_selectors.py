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
        "a2_pass": preregistration.get("a2_verdict") == "PASS",
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
    present_groups = _groups(candidate_universe, annotations, "relevant_groups_by_object")
    selected_groups = _groups(selected, annotations, "relevant_groups_by_object")
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


def _source_diversity(selected: Sequence[str], payloads: Mapping[str, Mapping[str, Any]]) -> int:
    return len({payloads[object_id].get("source_id") for object_id in selected})


def _first_relevant_rank(selected: Sequence[str], annotations: Mapping[str, Any]) -> int | None:
    for rank, object_id in enumerate(selected, 1):
        if annotations.get("relevant_groups_by_object", annotations.get("required_groups_by_object", {})).get(object_id, ()): return rank
    return None


def _concentration(selected: Sequence[str], payloads: Mapping[str, Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(Counter(str(payloads[object_id].get(field, "")) for object_id in selected))


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
    s0 = run_s0_offline(record, runner=s0_runner); s1 = (s1_runner or run_s1_offline)(record)
    s1_again = lambda: (s1_runner or run_s1_offline)(record)
    s0_ids, s1_ids = list(s0["selected_object_ids"]), list(s1["selected_object_ids"])
    required = set(annotations.get("relevant_groups", annotations.get("required_groups", ()))); critical = set(annotations.get("critical_groups", ()))
    final_s0, final_s1 = _groups(s0_ids, annotations, "relevant_groups_by_object"), _groups(s1_ids, annotations, "relevant_groups_by_object")
    critical_s0, critical_s1 = _groups(s0_ids, annotations, "critical_groups_by_object"), _groups(s1_ids, annotations, "critical_groups_by_object")
    candidate_universe = list(record["candidate_payloads"])
    protected = set(record["mandatory_symbol_ids"])
    displacement = selector_displacement(s1_ids, annotations, s1.get("candidate_receipts", ()), candidate_universe)
    s0_displacement = selector_displacement(s0_ids, annotations, s0.get("candidate_receipts", ()), candidate_universe)
    checks = _policy_checks(record, s1, s1_again)
    s0_metrics = {"final_evidence_recall": _ratio(final_s0, required), "critical_evidence_retention": _ratio(critical_s0, critical), "protected_exact_retention": _ratio(set(s0_ids) & protected, protected), "explicit_required_satisfaction": _required_satisfaction(s0_ids, record["candidate_payloads"], record["frozen_plan"]), "selector_caused_relevant_displacement": s0_displacement["count"]}
    s1_metrics = {"final_evidence_recall": _ratio(final_s1, required), "critical_evidence_retention": _ratio(critical_s1, critical), "protected_exact_retention": _ratio(set(s1_ids) & protected, protected), "explicit_required_satisfaction": _required_satisfaction(s1_ids, record["candidate_payloads"], record["frozen_plan"]), "selector_caused_relevant_displacement": displacement["count"]}
    negative_complete = bool(annotations.get("negative_completeness"))
    relevant_by_object = annotations.get("relevant_groups_by_object", annotations.get("required_groups_by_object", {}))
    precision = lambda selected: sum(bool(relevant_by_object.get(object_id)) for object_id in selected) / len(selected) if selected else 1.0
    supported_precision = {"status": "SUPPORTED" if negative_complete else NOT_SUPPORTED, "s0": precision(s0_ids) if negative_complete else None, "s1": precision(s1_ids) if negative_complete else None}
    forced_irrelevant = _forced_irrelevant_evidence(s0_ids, s1_ids, annotations, s1.get("candidate_receipts", ()), displacement)
    return {"case_id": record.get("case_id"), "policies": {"s0": S0_POLICY_ID, "s1": S1_POLICY_ID}, "input_identity": {"stage_f": record["stage_f_order"], "stage_r": record["stage_r_order"], "payload_ids": sorted(record["candidate_payloads"]), "channels": record["retrieval_channels"], "exact_stream": record["exact_stream_order"]}, "s0": {"selected_object_ids": s0_ids, "metrics": s0_metrics, "displacement": s0_displacement}, "s1": {"selected_object_ids": s1_ids, "metrics": s1_metrics, "receipts": s1.get("candidate_receipts", ()), "constraint_receipts": s1.get("constraint_receipts", ()), "displacement": displacement}, "secondary": {"selected_set_delta": sorted(set(s0_ids) ^ set(s1_ids)), "evidence_counts": {"s0_selected": len(s0_ids), "s1_selected": len(s1_ids), "s0_relevant_groups": len(final_s0), "s1_relevant_groups": len(final_s1), "s0_critical_groups": len(critical_s0), "s1_critical_groups": len(critical_s1)}, "supported_precision": supported_precision, "forced_irrelevant_evidence": forced_irrelevant, "source_concentration": {"s0": {"source_id": _concentration(s0_ids, record["candidate_payloads"], "source_id"), "source_type": _concentration(s0_ids, record["candidate_payloads"], "object_type")}, "s1": {"source_id": _concentration(s1_ids, record["candidate_payloads"], "source_id"), "source_type": _concentration(s1_ids, record["candidate_payloads"], "object_type")}}, "source_diversity": {"s0": _source_diversity(s0_ids, record["candidate_payloads"]), "s1": _source_diversity(s1_ids, record["candidate_payloads"])}, "constraint_decision_counts": _receipt_counts(s1.get("candidate_receipts", ())), "required_receipts": [row for row in s1.get("constraint_receipts", ()) if row.get("constraint_type") == "REQUIRED"], "protected_receipts": [row for row in s1.get("constraint_receipts", ()) if row.get("constraint_type") == "PROTECTED"], "graph_exposure": {"s0": _channel_exposure("graph", s0_ids, record), "s1": _channel_exposure("graph", s1_ids, record)}, "workflow_exposure": {"s0": _channel_exposure("workflow", s0_ids, record), "s1": _channel_exposure("workflow", s1_ids, record)}, "first_relevant_rank": {"s0": _first_relevant_rank(s0_ids, annotations), "s1": _first_relevant_rank(s1_ids, annotations)}, "displacement_reasons": {"s0": s0_displacement, "s1": displacement}, **checks}}


def gate_matrix(s0: Mapping[str, Any], s1: Mapping[str, Any], *, forced_irrelevant_supported: bool = False) -> dict[str, str]:
    return {GATE_NAMES[0]: "PASS" if s0["input_identity"] == s1["input_identity"] else "FAIL", GATE_NAMES[1]: "PASS" if not any(s1["upstream_calls"].values()) else "FAIL", GATE_NAMES[2]: "PASS" if s1["final_evidence_recall"] >= s0["final_evidence_recall"] else "FAIL", GATE_NAMES[3]: "PASS" if s1["new_critical_misses"] == 0 else "FAIL", GATE_NAMES[4]: "PASS" if s1["new_protected_losses"] == 0 else "FAIL", GATE_NAMES[5]: "PASS" if s1["explicit_required_satisfaction"] >= s0["explicit_required_satisfaction"] and s1["new_required_misses"] == 0 else "FAIL", GATE_NAMES[6]: "PASS" if s1["selector_displacement"] <= s0["selector_displacement"] else "FAIL", GATE_NAMES[7]: "PASS" if s1["version_source_violations"] == 0 else "FAIL", GATE_NAMES[8]: ("PASS" if s1["forced_irrelevant"] == 0 else "FAIL") if forced_irrelevant_supported else NOT_SUPPORTED, GATE_NAMES[9]: "PASS" if s1["deterministic"] and s1["preferred_invariant"] else "FAIL", GATE_NAMES[10]: "PASS" if s1["no_benchmark_specific_rule"] else "FAIL", GATE_NAMES[11]: "PASS" if s1["preregistration_intact"] else "FAIL"}


def meaningful_gain(s0: Mapping[str, float], s1: Mapping[str, float], gates: Mapping[str, str]) -> str:
    if any(value == "FAIL" for value in gates.values()): return "CURRENT_PREFERRED_GATE_FAILURE"
    gains = [s1[name] > s0[name] for name in PRIMARY_METRICS[:-1]] + [s1[PRIMARY_METRICS[-1]] < s0[PRIMARY_METRICS[-1]]]
    regressions = [s1[name] < s0[name] for name in PRIMARY_METRICS[:-1]] + [s1[PRIMARY_METRICS[-1]] > s0[PRIMARY_METRICS[-1]]]
    return "DEVELOPMENT_SUPPORTED" if any(gains) and not any(regressions) else "NO_MEANINGFUL_GAIN/INCONCLUSIVE"


def case_direction(s0: Mapping[str, float], s1: Mapping[str, float]) -> str:
    gains = any(s1[name] > s0[name] for name in PRIMARY_METRICS[:-1]) or s1[PRIMARY_METRICS[-1]] < s0[PRIMARY_METRICS[-1]]
    regressions = any(s1[name] < s0[name] for name in PRIMARY_METRICS[:-1]) or s1[PRIMARY_METRICS[-1]] > s0[PRIMARY_METRICS[-1]]
    return "regressed" if regressions else "improved" if gains else "unchanged"


def aggregate_receipts(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    directions = Counter(case_direction(row["s0"]["metrics"], row["s1"]["metrics"]) for row in cases)
    return {"case_count": len(cases), "direction_counts": dict(directions), "graph_maximum_exposure": sum(row["secondary"]["graph_maximum_exposure"] for row in cases), "selector_displacement_count": sum(row["s1"]["metrics"]["selector_caused_relevant_displacement"] for row in cases)}


def evaluate_frozen_cohort(records: Sequence[Mapping[str, Any]], annotations_by_case: Mapping[str, Mapping[str, Any]], *, s0_runner: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None, s1_runner: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None, preregistration: Mapping[str, Any]) -> dict[str, Any]:
    """Future A3 aggregate, limited to the same frozen A2 inputs for both policies."""
    cases = [evaluate_frozen_case(record, annotations_by_case[record["case_id"]], s0_runner=s0_runner, s1_runner=s1_runner) for record in records]
    def mean(policy: str, metric: str) -> float:
        return sum(row[policy]["metrics"][metric] for row in cases) / len(cases) if cases else 0.0
    s0_metrics = {metric: mean("s0", metric) for metric in PRIMARY_METRICS}
    s1_metrics = {metric: mean("s1", metric) for metric in PRIMARY_METRICS}
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
    gate_s0 = {"input_identity": frozen_identities, "final_evidence_recall": s0_metrics["final_evidence_recall"], "explicit_required_satisfaction": s0_metrics["explicit_required_satisfaction"], "selector_displacement": s0_metrics["selector_caused_relevant_displacement"]}
    gate_s1 = {"input_identity": frozen_identities, "upstream_calls": upstream_calls, "final_evidence_recall": s1_metrics["final_evidence_recall"], "new_critical_misses": sum(row["s1"]["metrics"]["critical_evidence_retention"] < row["s0"]["metrics"]["critical_evidence_retention"] for row in cases), "new_protected_losses": sum(row["s1"]["metrics"]["protected_exact_retention"] < row["s0"]["metrics"]["protected_exact_retention"] for row in cases), "explicit_required_satisfaction": s1_metrics["explicit_required_satisfaction"], "new_required_misses": sum(row["s1"]["metrics"]["explicit_required_satisfaction"] < row["s0"]["metrics"]["explicit_required_satisfaction"] for row in cases), "selector_displacement": s1_metrics["selector_caused_relevant_displacement"], "version_source_violations": invalid_selected, "forced_irrelevant": forced_irrelevant, "deterministic": all(row["secondary"]["deterministic"] for row in cases), "preferred_invariant": all(row["secondary"]["preferred_invariant"] for row in cases), "no_benchmark_specific_rule": contract_proof["passed"], "preregistration_intact": preregistration_proof["passed"]}
    gates = gate_matrix(gate_s0, gate_s1, forced_irrelevant_supported=forced_irrelevant_supported)
    return {"per_case_receipts": cases, "aggregate": {**aggregate_receipts(cases), "s0_metrics": s0_metrics, "s1_metrics": s1_metrics, "forced_irrelevant_evidence": {"status": "SUPPORTED" if forced_irrelevant_supported else NOT_SUPPORTED, "count": forced_irrelevant}, "gate_11_static_proof": contract_proof, "gate_12_preregistration_proof": preregistration_proof}, "gates": gates, "role_decision": meaningful_gain(s0_metrics, s1_metrics, gates)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-a3", action="store_true", required=True)
    parser.add_argument("--capture-jsonl", type=Path, required=True)
    parser.add_argument("--annotations-json", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    args = parser.parse_args(argv)
    preregistration = json.loads(args.preregistration.read_text(encoding="utf-8"))
    if preregistration.get("a2_verdict") != "PASS" or preregistration.get("a3_eligibility") != "NEXT_ELIGIBLE / NOT_STARTED":
        raise RuntimeError("A3 requires an integrity-passing frozen A2 capture")
    from evaluation.scripts.capture_c7_a2_post_reranker import validate_artifacts
    if validate_artifacts(args.preregistration, args.capture_jsonl).get("status") != "PASS":
        raise RuntimeError("A3 requires a valid A2 manifest and capture JSONL")
    records = [json.loads(line) for line in args.capture_jsonl.read_text(encoding="utf-8").splitlines() if line]
    annotations = json.loads(args.annotations_json.read_text(encoding="utf-8"))
    print(json.dumps(evaluate_frozen_cohort(records, annotations, preregistration=preregistration), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
