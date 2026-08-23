"""C7-A2 frozen post-reranker capture infrastructure.

Every command mode is fail-closed. This module can construct and validate
future artifacts, but performs no live work without explicit injected inputs.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import argparse
import json
from pathlib import Path
import subprocess
from typing import Any, Callable, Iterator, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
PARENT_MANIFEST = ROOT / "evaluation/baselines/manifests/phase_c_c6_a2_frozen_fusion_policy_comparison_v1.json"
PLAN_REPLAY = ROOT / "evaluation/baselines/replay/phase_c_c6_current_plan_candidate_replay_v2.jsonl"
PREREGISTRATION_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c7_a2_frozen_selector_preregistration_v1.json"
CAPTURE_PATH = ROOT / "evaluation/baselines/replay/phase_c_c7_a2_post_reranker_capture_v1.jsonl"
EXPECTED_HEAD = "a6bec2776e55b824831e22b7fbebd68489158be5"
CHANNEL_ORDER = ("exact", "dense", "sparse", "paper", "workflow", "graph")
CHANNEL_WEIGHTS = {"exact": 2.0, "dense": 1.0, "sparse": 1.0, "paper": 1.15, "workflow": 1.2, "graph": 0.8}
RRF_K = 60
EXPECTED_PARENT_IDS = ("g001", "g002", "g003", "g004", "g005", "g006", "g010", "g013", "g014", "g015", "g017", "g019", "g027", "g028", "g029", "g030", "g031", "g044", "g047", "g050", "g051", "g052", "g059", "g060", "g105", "g110", "g112", "g113", "g114", "g115")
EXPECTED_COHORT_IDS = ("g001", "g002", "g003", "g010", "g013", "g014", "g027", "g028", "g029", "g044", "g047", "g050", "g059", "g060", "g105", "g110", "g112", "g113")
EXPECTED_INTENT_COUNTS = {"installation": 6, "usage": 6, "algorithm_theory": 5, "api": 5, "troubleshooting": 5, "algorithm_implementation": 2, "module_structure": 1}
EXPECTED_COHORT_INTENT_COUNTS = {"installation": 3, "usage": 3, "algorithm_theory": 3, "api": 3, "troubleshooting": 3, "algorithm_implementation": 2, "module_structure": 1}
FORBIDDEN_TOKENS = ("gold", "relevant", "critical", "s1", "win", "loss", "outcome")
A0_REFERENCE = "phase_c_c7_a0_selection_boundary_replay_inventory_v1.json"
A1_REFERENCE = "phase_c_c7_a1_explicit_selection_contract_v1.json#a1r1_semantics_correction"
PRIMARY_METRIC_DEFINITIONS = {
    "final_evidence_recall": {
        "definition": "relevant evidence groups represented in final selected evidence",
        "support": "existing relevant-group annotations",
        "aggregation": "micro group coverage and per-case value",
    },
    "critical_evidence_retention": {
        "definition": "critical evidence groups represented in final selected evidence",
        "support": "existing critical-group annotations where defined",
        "aggregation": "micro group coverage and per-case value",
    },
    "explicit_required_satisfaction": {
        "definition": "question-grounded explicit_query_reference REQUIRED constraints satisfied",
        "support": "frozen plan provenance and selected payload source IDs",
        "aggregation": "constraint satisfaction rate",
    },
    "selector_caused_relevant_displacement": {
        "definition": "relevant groups present in the full frozen candidate universe but absent after deterministic selection",
        "support": "relevant-group annotations and selector receipts; upstream-absent groups excluded",
        "aggregation": "count and rate per policy",
    },
    "protected_exact_retention": {
        "definition": "captured mandatory/protected exact object IDs retained",
        "support": "captured mandatory_symbol_ids",
        "aggregation": "object-ID retention rate",
    },
}
SECONDARY_METRIC_DEFINITIONS = {
    "supported_precision": "selected relevant object count / selected object count only with explicit negative completeness; otherwise NOT_SUPPORTED",
    "selected_relevant_count": "selected objects with at least one relevant group",
    "selected_critical_count": "selected objects with at least one critical group",
    "selected_evidence_count": "selected object count",
    "source_id_concentration": "selected counts by source_id",
    "source_type_concentration": "selected counts by source type",
    "source_type_diversity": "unique selected source IDs and source types",
    "maximum_exclusion_count": "MAXIMUM exclusions",
    "required_override_count": "required_override admissions",
    "protected_override_count": "protected_override admissions",
    "duplicate_exclusion_count": "duplicate exclusions",
    "final_limit_exclusion_count": "final-limit exclusions",
    "preference_match_count": "PREFERRED matches with admission_effect=false",
    "graph_channel_maximum_exposure": "graph RETRIEVAL_CHANNEL MAXIMUM exposure and caused membership difference",
    "workflow_type_channel_exposure": "workflow source-type/channel candidate and selected exposure",
    "first_relevant_final_rank": "one-based first relevant selected rank",
    "case_level_direction": "improved, unchanged, or regressed from primary metrics",
}
HARD_GATE_DEFINITIONS = {
    "GATE_1": {"name": "frozen_input_identity", "rule": "S0 and S1 use identical frozen question, plan, F, R, payload universe, channels, and exact stream"},
    "GATE_2": {"name": "no_upstream_regeneration", "rule": "retrieval, reranker, analyzer, DB, and Qdrant calls are all zero during A3"},
    "GATE_3": {"name": "final_evidence_recall", "rule": "S1 Final Evidence Recall >= S0"},
    "GATE_4": {"name": "critical_safety", "rule": "S1 introduces zero new critical evidence-group misses"},
    "GATE_5": {"name": "protected_exact_safety", "rule": "S1 introduces zero captured mandatory/protected exact losses"},
    "GATE_6": {"name": "required_safety", "rule": "S1 explicit REQUIRED satisfaction >= S0 and zero new misses"},
    "GATE_7": {"name": "selector_displacement", "rule": "S1 selector-caused relevant displacement <= S0"},
    "GATE_8": {"name": "version_source_safety", "rule": "S1 selects zero invalid, source-version-invalid, or unusable candidates"},
    "GATE_9": {"name": "forced_irrelevant_evidence", "rule": "with explicit negative completeness, zero known-irrelevant REQUIRED/PROTECTED-only admissions that displace relevant evidence; otherwise NOT_SUPPORTED"},
    "GATE_10": {"name": "determinism", "rule": "repeated S1 selected order, candidate receipts, and constraint receipts are identical; PREFERRED membership invariant holds"},
    "GATE_11": {"name": "no_benchmark_specific_rule", "rule": "policy ID, authoritative A1R1 contract, source identity, and static selector source prove no case, Gold, or benchmark-specific rule"},
    "GATE_12": {"name": "preregistration_integrity", "rule": "cohort, policies, metrics, gates, and boundaries match the frozen A2 preregistration before A3"},
}


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump(mode="json"))
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    return value


def _plan(row: Mapping[str, Any]) -> Mapping[str, Any]:
    return row.get("retrieval_plan", row)


def _intent(row: Mapping[str, Any]) -> str:
    value = row.get("intent") or _plan(row).get("intent")
    if not isinstance(value, str) or not value:
        raise ValueError("replay row has no executable intent")
    return value


def _object_id(value: str | Mapping[str, Any]) -> str:
    return value if isinstance(value, str) else str(value["object_id"])


def production_plan(row: Mapping[str, Any], plan_factory: Callable[[Mapping[str, Any]], Any] | None = None) -> Any:
    """Convert a frozen replay dictionary to the exact production plan model."""
    if plan_factory is None:
        from panda_agent.retrieval import RetrievalPlan
        plan_factory = RetrievalPlan.model_validate
    return plan_factory(_plan(row))


def normalize_ranking(values: Sequence[str | Mapping[str, Any]]) -> list[str]:
    """Freeze every retrieval stream as its ordered object-ID sequence."""
    return [_object_id(value) for value in values]


def intent_counts(case_ids: Sequence[str], rows: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case_id in case_ids:
        intent = _intent(rows[case_id])
        counts[intent] = counts.get(intent, 0) + 1
    return counts


def derive_cohort(parent_ids: Sequence[str], rows: Mapping[str, Mapping[str, Any]]) -> list[str]:
    by_intent: dict[str, list[str]] = {}
    for case_id in parent_ids:
        by_intent.setdefault(_intent(rows[case_id]), []).append(case_id)
    return sorted(case_id for ids in by_intent.values() for case_id in sorted(ids)[:3])


def index_replay_rows(rows: Sequence[Mapping[str, Any]], parent_ids: Sequence[str]) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        case_id = row.get("case_id")
        if case_id in parent_ids:
            if case_id in indexed:
                raise ValueError(f"duplicate frozen replay row for {case_id}")
            if not row.get("question") or not isinstance(_plan(row), Mapping):
                raise ValueError(f"incomplete frozen replay row for {case_id}")
            _intent(row)
            indexed[str(case_id)] = row
    missing = set(parent_ids) - set(indexed)
    if missing:
        raise ValueError(f"missing frozen replay rows: {sorted(missing)}")
    return indexed


def build_preregistration(parent_ids: Sequence[str], replay_rows: Sequence[Mapping[str, Any]], *, source_head: str, plan_factory: Callable[[Mapping[str, Any]], Any] | None = None) -> dict[str, Any]:
    """Build the complete A2 pre-live contract using frozen inputs only."""
    if source_head != EXPECTED_HEAD:
        raise ValueError("source HEAD does not equal the frozen C7-A2 baseline")
    if tuple(parent_ids) != EXPECTED_PARENT_IDS:
        raise ValueError("authoritative parent IDs differ from the frozen C6 cohort")
    rows = index_replay_rows(replay_rows, parent_ids)
    for case_id in parent_ids:
        production_plan(rows[case_id], plan_factory)
    parent_counts = intent_counts(parent_ids, rows)
    if parent_counts != EXPECTED_INTENT_COUNTS:
        raise ValueError(f"parent intent counts differ: {parent_counts}")
    cohort = derive_cohort(parent_ids, rows)
    cohort_counts = intent_counts(cohort, rows)
    if tuple(cohort) != EXPECTED_COHORT_IDS or cohort_counts != EXPECTED_COHORT_INTENT_COUNTS:
        raise ValueError("mechanically derived cohort does not equal preregistered C7-A2 cohort")
    return {
        "schema_version": "c7-a2-frozen-selector-preregistration-v1", "task": "C7-A2", "source_head": source_head, "a0_reference": A0_REFERENCE, "a1_a1r1_reference": A1_REFERENCE,
        "parent_population": {"case_ids": list(parent_ids), "intent_counts": parent_counts}, "frozen_plan_source": str(PLAN_REPLAY.relative_to(ROOT)),
        "deterministic_cohort_rule": "intent count <=3: all; otherwise lexicographic first 3; final lexical sort", "frozen_cohort_case_ids": cohort,
        "cohort_intent_counts": cohort_counts, "expected_cohort_size": 18, "actual_cohort_size": len(cohort), "cohort_frozen_before_live_capture": True,
        "no_gold_used_for_cohort": True, "live_capture_authorization": "required_explicit_execute_live", "production_fusion_identity": "P0 CURRENT",
        "reranker_role": "HELD_CONSTANT", "s0_identity": "CURRENT_SELECTOR", "s1_identity": "c7.explicit_selection.v1", "capture_schema": "c7-a2-post-reranker-capture-v1",
        "s0_replay_parity_requirement": "18/18",
        "primary_metrics": PRIMARY_METRIC_DEFINITIONS,
        "secondary_metrics": SECONDARY_METRIC_DEFINITIONS,
        "selector_displacement": "for each policy, relevant groups present in the full frozen candidate universe but absent from final evidence; upstream-absent groups excluded and receipt reason attributed",
        "hard_gates": HARD_GATE_DEFINITIONS,
        "meaningful_gain_rule": "all supported gates PASS; >=1 primary improvement; no primary regression", "graph_normalization": "RETRIEVAL_CHANNEL graph MAXIMUM is intentional S1 treatment delta",
        "preferred_semantics": "PREFERRED admission_effect=false; it cannot change admission membership by itself",
        "required_semantics": "default cardinality 1; earliest hard-eligible Stage-M representative; one candidate may satisfy multiple constraints; only representatives gain priority; required_override may bypass MAXIMUM but never validity, duplicate suppression, or final limit",
        "protected_semantics": "captured mandatory IDs only; protected_override may bypass MAXIMUM but never validity, duplicate suppression, or final limit",
        "exposed_gold_boundary": "A3 development evidence cannot alone authorize production activation", "a3_evaluator_path": "evaluation/scripts/evaluate_c7_a3_frozen_selectors.py", "outcome_evaluation_executed": False, "s1_real_cohort_execution": False,
        "a2_verdict": "NOT_EXECUTED", "a3_eligibility": "BLOCKED_PENDING_CAPTURE",
    }


def load_frozen_inputs(manifest_path: Path = PARENT_MANIFEST, replay_path: Path = PLAN_REPLAY) -> tuple[list[str], list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in replay_path.read_text(encoding="utf-8").splitlines() if line]
    return manifest["cohorts"]["global_policy_cohort"]["ids"], rows


def prepare_artifact(output_path: Path = PREREGISTRATION_PATH, *, parent_ids: Sequence[str] | None = None, replay_rows: Sequence[Mapping[str, Any]] | None = None, source_head: str | None = None) -> dict[str, Any]:
    """Write the preregistration before any live capture; injectable for tests."""
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite frozen preregistration: {output_path}")
    if parent_ids is None or replay_rows is None:
        parent_ids, replay_rows = load_frozen_inputs()
    preregistration = build_preregistration(parent_ids, replay_rows, source_head=source_head or _current_head())
    output_path.write_text(json.dumps(preregistration, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return preregistration


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def reconstruct_stage_f(channel_rankings: Mapping[str, Sequence[str | Mapping[str, Any]]]) -> tuple[list[str], dict[str, float]]:
    scores: dict[str, float] = {}; first_seen: dict[str, int] = {}; position = 0
    for channel in CHANNEL_ORDER:
        for rank, candidate in enumerate(channel_rankings.get(channel, ()), 1):
            object_id = _object_id(candidate); scores[object_id] = scores.get(object_id, 0.0) + CHANNEL_WEIGHTS[channel] / (RRF_K + rank)
            first_seen.setdefault(object_id, position); position += 1
    return sorted(scores, key=lambda oid: (-scores[oid], first_seen[oid])), scores


def reconstruct_stage_m(stage_r_order: Sequence[str], stage_f_order: Sequence[str]) -> list[str]:
    return list(dict.fromkeys([*stage_r_order, *stage_f_order]))


@contextmanager
def selector_spy(module: Any | None = None) -> Iterator[dict[str, Any]]:
    if module is None:
        import panda_agent.retrieval as module
    original = module.select_final_evidence; captured: dict[str, Any] = {}
    def wrapped(ordered: Any, payloads: Any, scores: Any, channels: Any, plan: Any, final_evidence_limit: Any, mandatory_symbol_ids: Any):
        captured["input"] = deepcopy({"ordered": ordered, "payloads": payloads, "scores": scores, "channels": channels, "plan": _jsonable(plan), "final_evidence_limit": final_evidence_limit, "mandatory_symbol_ids": sorted(mandatory_symbol_ids)})
        result = original(ordered, payloads, scores, channels, plan, final_evidence_limit, mandatory_symbol_ids)
        captured["return"] = deepcopy(_jsonable({"evidence": result[0], "excluded": result[1], "backfill_admissions": result[2]}))
        return result
    module.select_final_evidence = wrapped
    try: yield captured
    finally: module.select_final_evidence = original


def replay_s0(record: Mapping[str, Any], *, selector: Callable[..., Any] | None = None, plan_factory: Callable[[Mapping[str, Any]], Any] | None = None) -> dict[str, Any]:
    if selector is None or plan_factory is None:
        from panda_agent.retrieval import RetrievalPlan, select_final_evidence
        selector, plan_factory = selector or select_final_evidence, plan_factory or RetrievalPlan.model_validate
    selected, excluded, backfill = selector(record["stage_p_order"], record["candidate_payloads"], record["stage_f_scores"], record["retrieval_channels"], plan_factory(record["frozen_plan"]), record["final_evidence_limit"], set(record["mandatory_symbol_ids"]))
    return _jsonable({"selected_object_ids": [item.object_id if hasattr(item, "object_id") else item["object_id"] for item in selected], "evidence": selected, "excluded": excluded, "backfill_admissions": backfill})


def _forbidden(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_path = f"{path}.{key}" if path else str(key)
            if any(token in str(key).casefold() for token in FORBIDDEN_TOKENS): found.append(key_path)
            found.extend(_forbidden(item, key_path))
    elif isinstance(value, list):
        for index, item in enumerate(value): found.extend(_forbidden(item, f"{path}[{index}]"))
    return found


def validate_record(record: Mapping[str, Any], **dependencies: Any) -> dict[str, bool]:
    required = {"case_id", "question", "frozen_plan", "channel_rankings", "stage_f_order", "stage_f_scores", "stage_r_order", "stage_r_stage_f_ranks", "reranker_pool_ids", "stage_m_order", "stage_p_order", "candidate_payloads", "retrieval_channels", "exact_stream_order", "mandatory_symbol_ids", "current_s0", "final_evidence_limit", "capture_integrity"}
    if missing := required - set(record): raise ValueError(f"capture record missing fields: {sorted(missing)}")
    if bad := _forbidden(record): raise ValueError(f"capture record contains forbidden fields: {bad}")
    if record["stage_m_order"] != reconstruct_stage_m(record["stage_r_order"], record["stage_f_order"]): raise ValueError("Stage-M mismatch")
    replay = replay_s0(record, **dependencies); current = record["current_s0"]
    return {"selected": replay["selected_object_ids"] == current["selected_object_ids"], "excluded": replay["excluded"] == current["excluded"], "backfill": replay["backfill_admissions"] == current["backfill_admissions"]}


def validate_capture_bundle(preregistration: Mapping[str, Any], records: Sequence[Mapping[str, Any]], **dependencies: Any) -> dict[str, Any]:
    expected = list(preregistration.get("frozen_cohort_case_ids", ()))
    if expected != list(EXPECTED_COHORT_IDS) or preregistration.get("actual_cohort_size") != 18: raise ValueError("invalid frozen preregistration cohort")
    if len(records) != 18 or [row.get("case_id") for row in records] != expected: raise ValueError("capture rows are not the exact frozen 18-case order")
    failed = [row["case_id"] for row in records if row.get("capture_status") == "FAILED"]
    if failed:
        return {"status": "CAPTURE_INCOMPLETE/INCONCLUSIVE", "failed_case_ids": failed, "a3_eligibility": "BLOCKED"}
    ledger = preregistration.get("capture_call_ledger")
    if not isinstance(ledger, Mapping): raise ValueError("capture ledger is required")
    expected_ledger = {"retrieval_calls": 18, "reranker_calls": 18, "analyzer_calls": 0, "gold_evaluations": 0, "s1_real_cohort_calls": 0, "qa_calls": 0, "verifier_calls": 0, "judge_calls": 0}
    if any(ledger.get(key, 0) != value for key, value in expected_ledger.items()): raise ValueError("capture call ledger violates A2 boundaries")
    expected_integrity = {"frozen_plan_used": True, "analyzer_called": False, "production_selector_spy_captured": True, "stage_p_complete": True, "payload_universe_complete": True, "score_map_complete": True, "channel_map_complete": True, "exact_stream_complete": True, "external_reads_required_for_future_replay": False, "s0_selected_parity": True, "s0_excluded_parity": True, "s0_backfill_parity": True}
    for row in records:
        if row.get("schema_version") != "c7-a2-post-reranker-capture-v1" or row.get("source_head") != preregistration.get("source_head"): raise ValueError("capture identity mismatch")
        if not row.get("implementation_identity") or not row.get("frozen_plan"): raise ValueError("capture provenance or plan missing")
        rebuilt_order, rebuilt_scores = reconstruct_stage_f(row["channel_rankings"])
        if row["stage_f_order"] != rebuilt_order or any(abs(row["stage_f_scores"].get(oid, 0.0) - score) > 1e-12 for oid, score in rebuilt_scores.items()): raise ValueError("Stage-F reconstruction mismatch")
        if row["stage_r_stage_f_ranks"] != [{"object_id": oid, "stage_f_rank": rebuilt_order.index(oid) + 1} for oid in row["stage_r_order"]]: raise ValueError("Stage-R ranks mismatch")
        universe = set(row["stage_p_order"])
        if not set(row["exact_stream_order"]) <= universe or not universe <= set(row["candidate_payloads"]) or not universe <= set(row["retrieval_channels"]): raise ValueError("incomplete selector universe")
        if any(row["capture_integrity"].get(key) != value for key, value in expected_integrity.items()): raise ValueError("capture integrity mismatch")
    parity = {row["case_id"]: validate_record(row, **dependencies) for row in records}
    if not all(all(values.values()) for values in parity.values()): raise ValueError("S0 replay parity is not 18/18")
    return {"status": "PASS", "record_count": 18, "s0_replay_parity": "18/18", "a3_eligibility": "NEXT_ELIGIBLE / NOT_STARTED"}


def validate_artifacts(preregistration_path: Path = PREREGISTRATION_PATH, capture_path: Path = CAPTURE_PATH, **dependencies: Any) -> dict[str, Any]:
    """Validate the independently stored manifest and JSONL capture artifact."""
    preregistration = json.loads(preregistration_path.read_text(encoding="utf-8"))
    return validate_capture_bundle(preregistration, read_jsonl(capture_path), **dependencies)


def execute_live(retriever: Any, *, case_id: str, question: str, frozen_plan: Any, source_head: str, frozen_row: Mapping[str, Any] | None = None, selector_module: Any | None = None, replay_dependencies: Mapping[str, Any] | None = None) -> dict[str, Any]:
    with selector_spy(selector_module) as captured: result = retriever.retrieve(question, plan=frozen_plan)
    if set(captured) != {"input", "return"}: raise RuntimeError("production selector boundary was not captured")
    boundary = captured["input"]; channel_rankings = {channel: normalize_ranking(result["rankings"].get(channel, ())) for channel in CHANNEL_ORDER}
    stage_f, reconstructed_scores = reconstruct_stage_f(channel_rankings); authoritative_scores = boundary["scores"]
    if set(authoritative_scores) != set(reconstructed_scores) or any(abs(authoritative_scores[oid] - reconstructed_scores[oid]) > 1e-12 for oid in authoritative_scores): raise RuntimeError("authoritative full selector scores differ from CURRENT reconstruction")
    reported = result.get("fusion_scores", {})
    if list(reported) != stage_f[:len(reported)] or any(abs(reported[oid] - reconstructed_scores[oid]) > 1e-12 for oid in reported): raise RuntimeError("production Stage-F top prefix order/values differ")
    stage_r = list(result["reranked_object_ids"]); ranks = {oid: rank for rank, oid in enumerate(stage_f, 1)}; s0 = captured["return"]
    provenance = frozen_row or {}
    record = {"schema_version": "c7-a2-post-reranker-capture-v1", "case_id": case_id, "question": question, "source_head": source_head, "frozen_plan": _jsonable(frozen_plan), "implementation_identity": {"fusion_policy": "P0 CURRENT", "reranker_role": "HELD_CONSTANT", "selector_identity": "CURRENT_SELECTOR", "shadow_policy_identity": "c7.explicit_selection.v1", "capture_script": "capture_c7_a2_post_reranker.py", "source_index_identity": provenance.get("source_index_identity", provenance.get("frozen_plan_source", "frozen_replay_not_recorded")), "retrieval_prompt_version": provenance.get("frozen_plan_prompt_version", "frozen_replay_not_recorded"), "frozen_plan_source": provenance.get("frozen_plan_source", "frozen_replay_not_recorded"), "resolved_versions": _jsonable(_plan(provenance).get("resolved_versions", {}))}, "channel_rankings": channel_rankings, "stage_f_order": stage_f, "stage_f_scores": authoritative_scores, "stage_r_order": stage_r, "stage_r_stage_f_ranks": [{"object_id": oid, "stage_f_rank": ranks[oid]} for oid in stage_r], "reranker_pool_ids": stage_f[:30], "stage_m_order": reconstruct_stage_m(stage_r, stage_f), "stage_p_order": boundary["ordered"], "candidate_payloads": boundary["payloads"], "retrieval_channels": boundary["channels"], "exact_stream_order": channel_rankings["exact"], "mandatory_symbol_ids": boundary["mandatory_symbol_ids"], "final_evidence_limit": boundary["final_evidence_limit"], "current_s0": {"selected_object_ids": [item["object_id"] for item in s0["evidence"]], "evidence": s0["evidence"], "excluded": s0["excluded"], "backfill_admissions": s0["backfill_admissions"]}}
    universe = set(record["stage_p_order"]); record["capture_integrity"] = {"frozen_plan_used": boundary["plan"] == _jsonable(frozen_plan), "analyzer_called": False, "production_selector_spy_captured": True, "stage_p_complete": universe == set(boundary["ordered"]), "payload_universe_complete": universe <= set(boundary["payloads"]), "score_map_complete": universe <= set(authoritative_scores), "channel_map_complete": universe <= set(boundary["channels"]), "exact_stream_complete": isinstance(channel_rankings["exact"], list), "external_reads_required_for_future_replay": False}
    parity = validate_record(record, **(dict(replay_dependencies or {}))); record["capture_integrity"].update({f"s0_{name}_parity": value for name, value in parity.items()})
    if not all(parity.values()): raise RuntimeError("offline S0 replay parity failed")
    return record


def default_retriever_factory() -> Any:
    from dotenv import load_dotenv
    from panda_agent.retrieval import Retriever
    load_dotenv(ROOT / ".env")
    return Retriever(ROOT)


def run_live_capture(preregistration: Mapping[str, Any], row_lookup: Mapping[str, Mapping[str, Any]], retriever_factory: Callable[[], Any] = default_retriever_factory, *, source_head: str, output_path: Path | None = None, execute_one: Callable[..., dict[str, Any]] = execute_live, plan_factory: Callable[[Mapping[str, Any]], Any] | None = None) -> tuple[list[dict[str, Any]], dict[str, int]]:
    if preregistration.get("live_capture_authorization") != "required_explicit_execute_live": raise ValueError("live capture lacks frozen authorization")
    retriever = retriever_factory(); records: list[dict[str, Any]] = []
    ledger = {"retrieval_calls": 0, "reranker_calls": 0, "analyzer_calls": 0, "gold_evaluations": 0, "s1_real_cohort_calls": 0, "qa_calls": 0, "verifier_calls": 0, "judge_calls": 0}
    original_analyze = getattr(retriever, "analyze", None)
    original_generate = getattr(getattr(retriever, "vertex", None), "generate_json", None)
    def blocked_analyze(*args: Any, **kwargs: Any) -> Any:
        ledger["analyzer_calls"] += 1
        raise RuntimeError("analyzer invocation violates frozen-plan capture")
    def counted_generate(*args: Any, **kwargs: Any) -> Any:
        ledger["reranker_calls"] += 1
        return original_generate(*args, **kwargs)
    if original_analyze is not None: retriever.analyze = blocked_analyze
    if original_generate is not None: retriever.vertex.generate_json = counted_generate
    try:
        for case_id in preregistration["frozen_cohort_case_ids"]:
            row = row_lookup[case_id]
            reranker_calls_before = ledger["reranker_calls"]
            try:
                ledger["retrieval_calls"] += 1
                record = execute_one(retriever, case_id=case_id, question=row["question"], frozen_plan=production_plan(row, plan_factory), source_head=source_head, frozen_row=row)
                if ledger["reranker_calls"] - reranker_calls_before != 1:
                    raise RuntimeError("case did not execute exactly one reranker call")
                records.append(record)
            except Exception as error:
                records.append({"schema_version": "c7-a2-post-reranker-capture-v1", "case_id": case_id, "capture_status": "FAILED", "failure": str(error), "single_attempt": True, "replacement_case_id": None})
    finally:
        if original_analyze is not None: retriever.analyze = original_analyze
        if original_generate is not None: retriever.vertex.generate_json = original_generate
    preregistration["capture_call_ledger"] = ledger
    failed_ids = [record["case_id"] for record in records if record.get("capture_status") == "FAILED"]
    preregistration["capture_failed_case_ids"] = failed_ids
    preregistration["capture_attempted_case_ids"] = list(preregistration["frozen_cohort_case_ids"])
    preregistration["a2_verdict"] = "PASS" if not failed_ids and ledger["analyzer_calls"] == 0 else "CAPTURE_INCOMPLETE/INCONCLUSIVE"
    preregistration["a3_eligibility"] = "NEXT_ELIGIBLE / NOT_STARTED" if preregistration["a2_verdict"] == "PASS" else "BLOCKED"
    if output_path is not None:
        output_path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")
    return records, ledger


def _current_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(); modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare-only", action="store_true"); modes.add_argument("--validate-only", action="store_true"); modes.add_argument("--execute-live", action="store_true")
    parser.add_argument("--preregistration", type=Path); parser.add_argument("--capture-jsonl", type=Path); parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.prepare_only:
        prepared = prepare_artifact(args.output or PREREGISTRATION_PATH)
        print(json.dumps({"status": "PASS", "preregistration": str(args.output or PREREGISTRATION_PATH), "cohort_size": prepared["actual_cohort_size"]}, sort_keys=True)); return 0
    if args.validate_only:
        print(json.dumps(validate_artifacts(args.preregistration or PREREGISTRATION_PATH, args.capture_jsonl or CAPTURE_PATH), sort_keys=True)); return 0
    preregistration_path = args.preregistration or PREREGISTRATION_PATH
    preregistration = json.loads(preregistration_path.read_text(encoding="utf-8"))
    if preregistration.get("live_capture_authorization") != "required_explicit_execute_live": raise RuntimeError("frozen preregistration does not authorize capture")
    parent_ids, replay_rows = load_frozen_inputs(); row_lookup = index_replay_rows(replay_rows, parent_ids)
    records, ledger = run_live_capture(preregistration, row_lookup, source_head=_current_head(), output_path=args.output or CAPTURE_PATH)
    preregistration_path.write_text(json.dumps(preregistration, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": preregistration["a2_verdict"], "capture": str(args.output or CAPTURE_PATH), "ledger": ledger}, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
