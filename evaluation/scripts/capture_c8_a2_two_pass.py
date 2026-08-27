"""C8-A2 frozen two-pass capture and global-treatment preregistration.

The live path in this module is intentionally narrow: it reads the sanitized
execution projection, invokes the current production retrieval path for the
initial pass and (when production sufficiency triggers it) the targeted pass,
and stops before answer generation.  Capture is evaluation-only instrumentation
around the existing Retriever/QAAgent objects; production source files and
configuration are not modified.

The global treatment is prepared only in synthetic preflight.  No real capture
is passed to G1 and no global reranker call is made in C8-A2.
"""

from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterator, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from panda_agent.global_candidate_pool import (  # noqa: E402
    ChannelCandidate,
    CompletenessState,
    PassOrigin,
    PassSnapshot,
    PayloadProvenance,
    TargetedTriggerContext,
    build_global_candidate_pool,
    serialize_pool,
)
from panda_agent.llm.vertex import VertexAIClient, VertexSettings  # noqa: E402
from panda_agent.prompts import RERANK_SYSTEM_PROMPT  # noqa: E402
from panda_agent.qa import QAAgent  # noqa: E402
from panda_agent.retrieval import (  # noqa: E402
    RetrievalPlan,
    Retriever,
    select_final_evidence,
)


PROJECTION_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_execution_projection_v1.json"
PREREGISTRATION_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_global_treatment_preregistration_v1.json"
SCREENING_LEDGER_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_screening_ledger_v1.json"
CAPTURE_PATH = ROOT / "evaluation/baselines/replay/phase_c_c8_a2_two_pass_capture_v1.jsonl"
CAPTURE_REPORT_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_two_pass_capture_report_v1.json"

A1R1_ANCHOR = "1bc0dc6f8e93f88ab1787400d4417ba463e66685"
A2_P0_ANCHOR = "5d19a5d18b7f13c163b1d6c03284158a78b88f70"
CONTRACT_ID = "c8.global_candidate_pool.v1"
TREATMENT_ID = "C8_GLOBAL_BEST_RANK_RRF_V1"
S0_IDENTITY = "C8_CURRENT_APPEND_V1"
RRF_K = 60
FINAL_EVIDENCE_LIMIT = 12
CHANNEL_ORDER = ("exact", "dense", "sparse", "paper", "workflow", "graph")
CHANNEL_WEIGHTS = {
    "exact": 2.0,
    "dense": 1.0,
    "sparse": 1.0,
    "paper": 1.15,
    "workflow": 1.2,
    "graph": 0.8,
}

PRIMARY_CASE_IDS = (
    "g001", "g007", "g012", "g013", "g025", "g026", "g027", "g038",
    "g041", "g042", "g043", "g044", "g057", "g058", "g059", "g060",
)
EXPANSION_CASE_IDS = (
    "g002", "g003", "g014", "g015", "g028", "g029", "g045", "g047",
)
ALL_CASE_IDS = PRIMARY_CASE_IDS + EXPANSION_CASE_IDS

CALL_COUNTER_KEYS = (
    "analyzer_calls",
    "initial_retrieval_passes",
    "targeted_retrieval_passes",
    "dense_embedding_calls",
    "sparse_encoding_calls",
    "qdrant_read_calls",
    "current_reranker_calls",
    "model_generation_calls",
)
STATIC_ZERO_CALL_KEYS = (
    "qa_generation_calls",
    "verifier_calls",
    "judge_calls",
    "db_index_writes",
)

HISTORICAL_PRE_CAPTURE_ABORTS = [
    {
        "attempt": 1,
        "event": "accidental exposure of expected_status",
        "relevance_bearing_gold_exposed": False,
        "live_executions": 0,
        "preregistration": "none",
        "scientific_attempt_consumed": False,
    },
    {
        "attempt": 2,
        "event": "faulty multiline text projection exposed relevance-bearing Gold fields",
        "relevance_bearing_gold_exposed": True,
        "live_executions": 0,
        "preregistration": "none",
        "treatment_execution": 0,
        "scientific_attempt_consumed": False,
    },
]


class CaptureFidelityError(RuntimeError):
    """Raised when a production-exposed pass cannot be captured faithfully."""


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump(mode="json"))
    if hasattr(value, "as_dict"):
        return _jsonable(value.as_dict())
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    return value


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(value), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _current_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def load_execution_projection(path: Path = PROJECTION_PATH) -> list[dict[str, str]]:
    """Load and structurally validate only the safe execution projection."""

    payload = _read_json(path)
    if payload.get("artifact_role") != "C8_A2_SANITIZED_EXECUTION_PROJECTION":
        raise ValueError("unexpected execution projection artifact_role")
    if list(payload.get("primary_case_ids") or []) != list(PRIMARY_CASE_IDS):
        raise ValueError("projection primary_case_ids do not match the frozen order")
    if list(payload.get("expansion_case_ids") or []) != list(EXPANSION_CASE_IDS):
        raise ValueError("projection expansion_case_ids do not match the frozen order")
    raw_records = payload.get("records")
    if not isinstance(raw_records, list) or len(raw_records) != 24:
        raise ValueError("execution projection must contain exactly 24 records")
    records: list[dict[str, str]] = []
    for record in raw_records:
        if not isinstance(record, dict) or set(record) != {"case_id", "query", "intent"}:
            raise ValueError("projection records must have exactly case_id/query/intent keys")
        if not all(isinstance(record[key], str) and record[key] for key in ("case_id", "query", "intent")):
            raise ValueError("projection record fields must be non-empty strings")
        records.append({key: record[key] for key in ("case_id", "query", "intent")})
    if [record["case_id"] for record in records] != list(ALL_CASE_IDS):
        raise ValueError("projection records do not preserve the frozen primary/expansion order")
    return records


def projection_summary(path: Path = PROJECTION_PATH) -> dict[str, Any]:
    records = load_execution_projection(path)
    return {
        "path": str(path.relative_to(ROOT)),
        "artifact_role": "C8_A2_SANITIZED_EXECUTION_PROJECTION",
        "record_count": len(records),
        "primary_case_ids": list(PRIMARY_CASE_IDS),
        "expansion_case_ids": list(EXPANSION_CASE_IDS),
        "GOLD_FILE_ACCESSED": False,
        "P0_VALIDATOR_EXECUTED": False,
        "PROJECTION_MODIFIED": False,
    }


def frozen_scientific_fields() -> dict[str, Any]:
    """Return the exact pre-live scientific contract for the preregistration."""

    primary_metrics = {
        "P1_FINAL_EVIDENCE_RECALL": {
            "definition": "Gold evidence groups matched by final Evidence / all Gold evidence groups in the treatment cohort",
            "identity": "(case_id, Gold group ID)",
            "aggregation": "micro-aggregated numerator and denominator identities",
        },
        "P2_CRITICAL_EVIDENCE_RETENTION": {
            "definition": "critical Gold groups matched by final Evidence / all critical Gold groups in the treatment cohort",
            "identity": "(case_id, Gold group ID)",
            "aggregation": "micro-aggregated numerator and denominator identities",
        },
        "P3_TARGETED_RECOVERY_SURVIVAL": {
            "definition": "Gold groups absent from INITIAL Stage-S Evidence and present in the TARGETED pre-final candidate universe that are retained in final Evidence",
            "identity": "(case_id, Gold group ID)",
            "aggregation": "micro-aggregated numerator and denominator identities",
        },
        "P4_INITIAL_RELEVANT_RETENTION": {
            "definition": "Gold groups matched by INITIAL Stage-S Evidence that remain in final Evidence",
            "identity": "(case_id, Gold group ID)",
            "aggregation": "micro-aggregated numerator and denominator identities",
        },
    }
    hard_gates = {
        "GATE_1": "frozen input identity",
        "GATE_2": "zero upstream regeneration in A3",
        "GATE_3": "A2 S0 replay parity = 100%",
        "GATE_4": "G1 Final Evidence Recall >= S0",
        "GATE_5": "zero new critical misses at identity level",
        "GATE_6": "G1 Targeted Recovery Survival >= S0",
        "GATE_7": "G1 Initial Relevant Retention >= S0",
        "GATE_8": "zero new protected/exact losses preserved by S0 where identities are available",
        "GATE_9": "zero new invalid version, unusable locator, or source-lock violation",
        "GATE_10": "deterministic fusion/M/P/selector given fixed reranker output",
        "GATE_11": "no benchmark-specific or case-specific rule",
        "GATE_12": "A3 implementation matches frozen preregistration",
    }
    return {
        "cohort_order": {
            "primary_case_ids": list(PRIMARY_CASE_IDS),
            "expansion_case_ids": list(EXPANSION_CASE_IDS),
            "primary_then_expansion": True,
            "maximum_screened": 24,
            "minimum_targeted_treatment_cases": 6,
            "maximum_treatment_cases": 12,
            "treatment_selection": "first 12 targeted-triggering cases in frozen screening order",
        },
        "screening_stop_rule": {
            "primary_count": 16,
            "stop_when_targeted_count_reaches": 12,
            "after_primary_stop_if_targeted_at_least": 6,
            "use_expansion_if_after_primary_targeted_below": 6,
            "expansion_count": 8,
            "replace_cases": False,
            "resample_cases": False,
            "reorder_cases": False,
            "retry_cases": False,
        },
        "s0": {
            "identity": S0_IDENTITY,
            "input_order": "targeted selected Evidence then initial selected Evidence",
            "dedup_key": "evidence_id",
            "dict_behavior": "first insertion preserves position; later duplicate assignment replaces value",
            "final": "first 12 dict values",
            "post_merge_fusion": False,
            "post_merge_reranker": False,
            "post_merge_selector": False,
        },
        "g1": {
            "identity": TREATMENT_ID,
            "candidate_identity": "object_id",
            "origin_values": ["INITIAL_ONLY", "TARGETED_ONLY", "BOTH"],
            "origin_bonus": False,
            "pass_bonus": False,
            "channel_rank_rule": "minimum rank observed across INITIAL and TARGETED per object/channel",
            "one_contribution_per_object_channel": True,
            "rrf_k": RRF_K,
            "weights": dict(CHANNEL_WEIGHTS),
            "normalization": False,
            "global_reranker_top_k": 30,
            "global_reranker_question": "original question",
            "reranker_identity": "CURRENT reranker and CURRENT RERANK_SYSTEM_PROMPT/model/config",
            "final_plan": "actual TARGETED RetrievalPlan",
            "stage_p_question": "original question",
            "global_channel_membership": "union of production channels observed across both passes",
            "selector": "CURRENT_SELECTOR",
            "final_evidence_limit": FINAL_EVIDENCE_LIMIT,
        },
        "candidate_identity": {
            "global": "object_id",
            "occurrence_output": "evidence_id",
            "payload_consistency": [
                "source_id",
                "source_version_id",
                "object_type",
                "locator",
                "title when both values exist",
                "text when both values exist",
                "authority_level when both values exist",
            ],
        },
        "primary_metrics": primary_metrics,
        "secondary_diagnostics": [
            "unique global candidate count",
            "INITIAL_ONLY count",
            "TARGETED_ONLY count",
            "BOTH count",
            "final source-id diversity",
            "final source-type diversity",
            "targeted-only final selection count",
            "BOTH final selection count",
            "initial displacement identities",
            "targeted recovery-loss identities",
            "S0/G1 final overlap",
            "case direction: improved, unchanged, regressed",
        ],
        "hard_gates": hard_gates,
        "meaningful_gain_rule": {
            "development_supported_candidate": "all supported hard gates PASS, at least one primary metric strictly improves, and none regress",
            "no_meaningful_gain": "all gates PASS but no primary metric improves; CURRENT remains preferred",
            "gate_failure": "any non-regression or safety gate fails; CURRENT remains preferred",
            "maximum_exposed_development_conclusion": "DEVELOPMENT_SUPPORTED_CANDIDATE",
            "production_activation_authorized": False,
        },
        "a3_input_identity": {
            "load_frozen_a2_capture": True,
            "load_gold_only_in_a3": True,
            "zero_upstream_regeneration": True,
            "zero_retrieval": True,
            "zero_targeted_retrieval": True,
            "zero_analyzer": True,
            "zero_embeddings": True,
            "zero_sparse_encoding": True,
            "zero_qdrant": True,
            "zero_candidate_sql": True,
            "zero_qa_verifier_judge": True,
        },
    }


def build_preregistration(source_head: str) -> dict[str, Any]:
    scientific = frozen_scientific_fields()
    return {
        "schema_version": "c8-a2-global-treatment-preregistration-v1",
        "artifact_role": "C8_A2_GLOBAL_TREATMENT_PREREGISTRATION",
        "task": "C8-A2",
        "contract_id": CONTRACT_ID,
        "a1r1_anchor": A1R1_ANCHOR,
        "a2_p0_anchor": A2_P0_ANCHOR,
        "source_head_at_preregistration": source_head,
        "safe_projection": {
            "path": str(PROJECTION_PATH.relative_to(ROOT)),
            "artifact_role": "C8_A2_SANITIZED_EXECUTION_PROJECTION",
            "record_count": 24,
        },
        "live_capture_authorization": "required_explicit_execute_live",
        "written_before_live_start": True,
        "scientific_fields": scientific,
        "cohort": scientific["cohort_order"],
        "screening_stop_rule": scientific["screening_stop_rule"],
        "s0": scientific["s0"],
        "g1": scientific["g1"],
        "primary_metrics": scientific["primary_metrics"],
        "hard_gates": scientific["hard_gates"],
        "meaningful_gain_rule": scientific["meaningful_gain_rule"],
        "production_authority": {
            "fusion": "P0 CURRENT",
            "selector": "CURRENT_SELECTOR",
            "reranker_prompt": "CURRENT RERANK_SYSTEM_PROMPT",
            "targeted_query_semantics": "existing QAAgent._targeted_retrieve; leading whitespace behavior preserved",
        },
        "isolation": {
            "gold_file_access": False,
            "gold_relevance_labels_access": False,
            "gold_evaluations": 0,
            "novel_evaluations": 0,
            "real_g1_executions": 0,
            "real_global_reranker_calls": 0,
            "qa_generation_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "db_index_writes": 0,
            "production_behavior_changed": False,
        },
        "historical_pre_capture_aborts": HISTORICAL_PRE_CAPTURE_ABORTS,
    }


def prepare_preregistration(
    path: Path = PREREGISTRATION_PATH,
    *,
    source_head: str | None = None,
) -> dict[str, Any]:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite frozen preregistration: {path}")
    projection_summary()
    preregistration = build_preregistration(source_head or _current_head())
    _write_json(path, preregistration)
    return preregistration


def load_frozen_preregistration(path: Path = PREREGISTRATION_PATH) -> dict[str, Any]:
    """Load the pre-live file and reject any scientific-contract drift."""

    preregistration = _read_json(path)
    if preregistration.get("written_before_live_start") is not True:
        raise ValueError("preregistration is not marked as written before live start")
    if preregistration.get("scientific_fields") != frozen_scientific_fields():
        raise ValueError("preregistration scientific fields do not match the frozen C8-A2 contract")
    if preregistration.get("live_capture_authorization") != "required_explicit_execute_live":
        raise ValueError("preregistration lacks the explicit live-capture authorization")
    return preregistration


def _record_payloads(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for raw in rows:
        item = dict(_jsonable(raw))
        object_id = str(item.get("object_id") or "")
        if not object_id:
            raise CaptureFidelityError("executed channel payload lacks object_id")
        existing = payloads.get(object_id)
        if existing is not None and existing != item:
            raise CaptureFidelityError(f"conflicting payload within one pass for {object_id}")
        payloads[object_id] = item
    return payloads


def reconstruct_stage_f(
    channel_rows: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[list[str], dict[str, float]]:
    """Reconstruct the full current P0 Stage-F order and score map."""

    scores: dict[str, float] = {}
    first_seen: dict[str, int] = {}
    position = 0
    for channel in CHANNEL_ORDER:
        for rank, row in enumerate(channel_rows.get(channel, ()), 1):
            object_id = str(row["object_id"])
            contribution = CHANNEL_WEIGHTS[channel] / (RRF_K + rank)
            scores[object_id] = scores.get(object_id, 0.0) + contribution
            first_seen.setdefault(object_id, position)
            position += 1
    order = sorted(scores, key=lambda object_id: (-scores[object_id], first_seen[object_id]))
    return order, scores


def _payload_provenance(item: Mapping[str, Any]) -> PayloadProvenance:
    return PayloadProvenance(
        object_id=str(item["object_id"]),
        source_id=str(item["source_id"]),
        source_version_id=str(item["source_version_id"]),
        object_type=item.get("object_type"),
        locator=item.get("locator") or {},
        title=item.get("title"),
        text=item.get("text"),
        payload_ref=item.get("payload_ref"),
    )


def _evidence_dicts(value: Any) -> list[dict[str, Any]]:
    return [dict(_jsonable(item)) for item in list(value or [])]


def _selected_ids(evidence: Sequence[Mapping[str, Any]]) -> list[str]:
    return [str(item["object_id"]) for item in evidence]


def _evidence_ids(evidence: Sequence[Mapping[str, Any]]) -> list[str]:
    return [str(item["evidence_id"]) for item in evidence]


def _compare_evidence_fields(expected: Sequence[Mapping[str, Any]], actual: Sequence[Mapping[str, Any]]) -> None:
    if _evidence_ids(expected) != _evidence_ids(actual):
        raise CaptureFidelityError("Stage-S Evidence IDs/order differ from production")
    fields = (
        "object_id",
        "source_id",
        "source_version_id",
        "locator",
        "retrieval_channels",
        "score",
        "authority_level",
    )
    if len(expected) != len(actual):
        raise CaptureFidelityError("Stage-S selected evidence count differs from production")
    for index, (left, right) in enumerate(zip(expected, actual)):
        for field in fields:
            if field in left and field in right and left[field] != right[field]:
                raise CaptureFidelityError(f"Stage-S field mismatch at {index}: {field}")


@contextmanager
def production_selector_capture() -> Iterator[dict[str, Any]]:
    """Capture the selector input/output from the same production call."""

    import panda_agent.retrieval as retrieval_module

    original = retrieval_module.select_final_evidence
    captured: dict[str, Any] = {}

    def wrapped(
        ordered: list[str],
        payloads: dict[str, dict[str, Any]],
        scores: dict[str, float],
        channels: dict[str, list[str]],
        plan: Any,
        final_evidence_limit: int,
        mandatory_symbol_ids: set[str],
    ) -> tuple[list[Any], list[dict[str, Any]], list[dict[str, Any]]]:
        captured["input"] = {
            "ordered": list(ordered),
            "payloads": deepcopy(payloads),
            "scores": dict(scores),
            "channels": deepcopy(channels),
            "plan": _jsonable(plan),
            "final_evidence_limit": final_evidence_limit,
            "mandatory_symbol_ids": sorted(mandatory_symbol_ids),
        }
        result = original(ordered, payloads, scores, channels, plan, final_evidence_limit, mandatory_symbol_ids)
        captured["output"] = {
            "evidence": _evidence_dicts(result[0]),
            "excluded": _jsonable(result[1]),
            "backfill_admissions": _jsonable(result[2]),
        }
        return result

    retrieval_module.select_final_evidence = wrapped
    try:
        yield captured
    finally:
        retrieval_module.select_final_evidence = original


def build_pass_snapshot(pass_capture: Mapping[str, Any], pass_origin: PassOrigin) -> tuple[PassSnapshot, dict[str, Any]]:
    """Build and validate one COMPLETE snapshot from one production call."""

    result = dict(pass_capture["result"])
    raw_channels = {
        channel: [dict(_jsonable(item)) for item in rows]
        for channel, rows in (pass_capture.get("channel_rows") or {}).items()
        if channel in result.get("rankings", {})
    }
    for channel, rows in raw_channels.items():
        returned_ids = list(result["rankings"].get(channel) or [])
        captured_ids = [str(item["object_id"]) for item in rows]
        if returned_ids != captured_ids:
            raise CaptureFidelityError(f"{pass_origin.value} {channel} capture differs from production ranking stream")

    raw_payloads = _record_payloads([item for rows in raw_channels.values() for item in rows])
    channel_orders = {channel: [str(item["object_id"]) for item in rows] for channel, rows in raw_channels.items()}
    stage_f_order, stage_f_scores = reconstruct_stage_f(raw_channels)
    reported_fusion = dict(result.get("fusion_scores") or {})
    if list(reported_fusion) != stage_f_order[:len(reported_fusion)]:
        raise CaptureFidelityError(f"{pass_origin.value} Stage-F exposed prefix differs from reconstruction")
    for object_id, score in reported_fusion.items():
        if not math.isclose(float(score), stage_f_scores[object_id], rel_tol=0.0, abs_tol=1e-12):
            raise CaptureFidelityError(f"{pass_origin.value} Stage-F exposed score differs for {object_id}")

    stage_r_order = [str(item) for item in (result.get("reranked_object_ids") or [])]
    if len(stage_r_order) != len(set(stage_r_order)) or not set(stage_r_order) <= set(stage_f_order):
        raise CaptureFidelityError(f"{pass_origin.value} Stage-R is not a unique Stage-F subset")
    stage_m_order = list(dict.fromkeys([*stage_r_order, *stage_f_order]))
    channels_by_object: dict[str, list[str]] = {}
    for channel, object_ids in channel_orders.items():
        for object_id in object_ids:
            channels_by_object.setdefault(object_id, []).append(channel)
    from evaluation.c8_global_treatment import reconstruct_current_stage_p

    stage_p_preparation = reconstruct_current_stage_p(
        str(pass_capture["query_text"]),
        result["plan"],
        stage_m_order,
        channel_orders,
        raw_payloads,
        channels_by_object,
    )
    stage_p_order = list(stage_p_preparation["stage_p_order"])
    reported_stage_p = [str(item) for item in (result.get("ranked_object_ids") or [])]
    if reported_stage_p != stage_p_order[:len(reported_stage_p)]:
        raise CaptureFidelityError(f"{pass_origin.value} Stage-P exposed prefix differs from reconstruction")
    selector_capture = pass_capture.get("selector_capture") or {}
    selector_input = selector_capture.get("input")
    selector_output = selector_capture.get("output")
    if not isinstance(selector_input, Mapping) or not isinstance(selector_output, Mapping):
        raise CaptureFidelityError(f"{pass_origin.value} production selector boundary was not captured")
    if list(selector_input["ordered"]) != stage_p_order:
        raise CaptureFidelityError(f"{pass_origin.value} Stage-P reconstruction differs from production order")
    if dict(selector_input["scores"]) != stage_f_scores:
        raise CaptureFidelityError(f"{pass_origin.value} full Stage-F score map differs from production selector input")
    if dict(selector_input["payloads"]) != raw_payloads:
        raise CaptureFidelityError(f"{pass_origin.value} selector payload universe differs from captured channels")
    if dict(selector_input["channels"]) != channels_by_object:
        raise CaptureFidelityError(f"{pass_origin.value} selector channel membership differs from captured channels")

    actual_evidence = _evidence_dicts(result.get("evidence"))
    selector_evidence = _evidence_dicts(selector_output.get("evidence"))
    _compare_evidence_fields(selector_evidence, actual_evidence)
    if _jsonable(selector_output.get("excluded")) != _jsonable(result.get("excluded") or []):
        raise CaptureFidelityError(f"{pass_origin.value} exclusion receipts differ from selector output")
    if _jsonable(selector_output.get("backfill_admissions")) != _jsonable(result.get("backfill_admissions") or []):
        raise CaptureFidelityError(f"{pass_origin.value} backfill admissions differ from selector output")

    evidence_map = {item["object_id"]: item["evidence_id"] for item in actual_evidence}
    payloads = {object_id: _payload_provenance(item) for object_id, item in raw_payloads.items()}
    snapshot = PassSnapshot(
        pass_origin=pass_origin,
        completeness=CompletenessState.COMPLETE,
        query_text=str(pass_capture["query_text"]),
        retrieval_plan=dict(_jsonable(result["plan"])),
        channel_candidates=tuple(
            ChannelCandidate(
                channel=channel,
                object_id=str(item["object_id"]),
                rank=rank,
                channel_score=(
                    float(pass_capture.get("channel_scores", {}).get(channel, [None] * len(raw_channels.get(channel, ())))[rank - 1])
                    if pass_capture.get("channel_scores", {}).get(channel, [None] * len(raw_channels.get(channel, ())))[rank - 1] is not None
                    else None
                ),
            )
            for channel in CHANNEL_ORDER
            for rank, item in enumerate(raw_channels.get(channel, ()), 1)
        ),
        stage_f_order=tuple(stage_f_order),
        stage_f_scores=dict(stage_f_scores),
        stage_r_order=tuple(stage_r_order),
        stage_m_order=tuple(stage_m_order),
        stage_p_order=tuple(stage_p_order),
        stage_s_selected_object_ids=tuple(_selected_ids(actual_evidence)),
        stage_s_evidence_ids=evidence_map,
        exclusions=tuple(_jsonable(result.get("excluded") or [])),
        backfill_admissions=tuple(_jsonable(result.get("backfill_admissions") or [])),
        payloads=payloads,
    )
    return snapshot, {
        "raw_channels": raw_channels,
        "raw_payloads": raw_payloads,
        "channel_orders": channel_orders,
        "channels_by_object": channels_by_object,
        "stage_p_preparation": stage_p_preparation,
        "actual_evidence": actual_evidence,
        "selector_input": _jsonable(selector_input),
        "selector_output": _jsonable(selector_output),
        "parity": {
            "stage_f": True,
            "stage_p": True,
            "stage_s": True,
        },
    }


def replay_s0(targeted_selected_evidence: Sequence[Mapping[str, Any]], initial_selected_evidence: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Replay the exact current targeted-first evidence-level dict merge."""

    merged: dict[str, dict[str, Any]] = {}
    for item in [*targeted_selected_evidence, *initial_selected_evidence]:
        merged[str(item["evidence_id"])] = dict(_jsonable(item))
    return list(merged.values())[:FINAL_EVIDENCE_LIMIT]


def validate_s0_replay(
    targeted_selected_evidence: Sequence[Mapping[str, Any]],
    initial_selected_evidence: Sequence[Mapping[str, Any]],
    actual_merged_evidence: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    replayed = replay_s0(targeted_selected_evidence, initial_selected_evidence)
    actual = [dict(_jsonable(item)) for item in actual_merged_evidence]
    fields = (
        "object_id",
        "source_id",
        "source_version_id",
        "locator",
        "retrieval_channels",
        "score",
        "authority_level",
    )
    mismatches: list[dict[str, Any]] = []
    if _evidence_ids(replayed) != _evidence_ids(actual):
        mismatches.append({"field": "evidence_id/order", "expected": _evidence_ids(replayed), "actual": _evidence_ids(actual)})
    if len(replayed) != len(actual):
        mismatches.append({"field": "count", "expected": len(replayed), "actual": len(actual)})
    for index, (expected, observed) in enumerate(zip(replayed, actual)):
        for field in fields:
            if field in expected and field in observed and expected[field] != observed[field]:
                mismatches.append({"index": index, "field": field})
    return {
        "identity": S0_IDENTITY,
        "parity": not mismatches,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "replayed_evidence": replayed,
        "actual_evidence": actual,
    }


def validate_both_origin_payload_consistency(
    initial_payloads: Mapping[str, Mapping[str, Any]],
    targeted_payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    fields = ("source_id", "source_version_id", "object_type", "locator")
    optional_fields = ("title", "text", "authority_level")
    conflicts: list[dict[str, Any]] = []
    for object_id in sorted(set(initial_payloads) & set(targeted_payloads)):
        left = initial_payloads[object_id]
        right = targeted_payloads[object_id]
        for field in fields:
            if left.get(field) != right.get(field):
                conflicts.append({"object_id": object_id, "field": field, "initial": left.get(field), "targeted": right.get(field)})
        for field in optional_fields:
            if left.get(field) is not None and right.get(field) is not None and left.get(field) != right.get(field):
                conflicts.append({"object_id": object_id, "field": field, "initial": left.get(field), "targeted": right.get(field)})
    return {
        "checked_object_count": len(set(initial_payloads) & set(targeted_payloads)),
        "consistent": not conflicts,
        "conflicts": conflicts,
    }


class CountingVertex:
    """Delegate Vertex calls while counting only authorized live categories."""

    def __init__(self, delegate: VertexAIClient, owner: "CapturingRetriever") -> None:
        self._delegate = delegate
        self._owner = owner

    def generate_json(self, prompt: str, response_schema: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        task = None
        try:
            parsed = json.loads(prompt)
            if isinstance(parsed, dict):
                task = parsed.get("task")
        except (TypeError, ValueError):
            pass
        self._owner._increment("model_generation_calls")
        if task == "analyze_retrieval_question":
            self._owner._increment("analyzer_calls")
        elif task == "rerank_evidence":
            self._owner._increment("current_reranker_calls")
        return self._delegate.generate_json(prompt, response_schema, **kwargs)

    def embed_query(self, text: str) -> list[float]:
        self._owner._increment("dense_embedding_calls")
        return self._delegate.embed_query(text)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._delegate, name)


class CountingQdrant:
    def __init__(self, delegate: Any, owner: "CapturingRetriever") -> None:
        self._delegate = delegate
        self._owner = owner

    def query_points(self, *args: Any, **kwargs: Any) -> Any:
        self._owner._increment("qdrant_read_calls")
        return self._delegate.query_points(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._delegate, name)


class CapturingRetriever(Retriever):
    """Evaluation-only Retriever subclass that records one real pass."""

    def __init__(self, project_root: Path, delegate_vertex: VertexAIClient) -> None:
        self._total_counts = Counter({key: 0 for key in CALL_COUNTER_KEYS})
        self._active_counts: Counter[str] | None = None
        self._active_pass_origin: PassOrigin | None = None
        self._next_pass_origin: PassOrigin | None = None
        self._current_capture: dict[str, Any] | None = None
        self._case_passes: list[dict[str, Any]] = []
        wrapped_vertex = CountingVertex(delegate_vertex, self)
        super().__init__(project_root, vertex=wrapped_vertex)
        self.vertex = wrapped_vertex
        self.storage.qdrant = CountingQdrant(self.storage.qdrant, self)

    def begin_case(self) -> None:
        self._case_passes = []

    def prepare_pass(self, pass_origin: PassOrigin) -> None:
        if self._active_counts is not None:
            raise RuntimeError("a capture pass is already active")
        self._next_pass_origin = pass_origin
        self._active_counts = Counter()
        self._active_pass_origin = pass_origin

    def _increment(self, key: str) -> None:
        self._total_counts[key] += 1
        if self._active_counts is not None:
            self._active_counts[key] += 1

    def finish_pass(self) -> dict[str, Any]:
        if self._current_capture is None:
            raise RuntimeError("no capture pass is active")
        capture = self._current_capture
        capture["call_ledger"] = {key: int((self._active_counts or Counter()).get(key, 0)) for key in CALL_COUNTER_KEYS}
        capture["pass_origin"] = (self._active_pass_origin or PassOrigin.INITIAL).value
        self._case_passes.append(capture)
        self._current_capture = None
        self._active_counts = None
        self._active_pass_origin = None
        self._next_pass_origin = None
        return capture

    def case_passes(self) -> list[dict[str, Any]]:
        return list(self._case_passes)

    def total_counts(self) -> dict[str, int]:
        return {key: int(self._total_counts.get(key, 0)) for key in CALL_COUNTER_KEYS}

    def _record_rows(self, channel: str, rows: Sequence[Mapping[str, Any]], scores: Sequence[Any] | None = None) -> None:
        if self._current_capture is None:
            return
        score_values = list(scores or ())
        encoded = [dict(_jsonable(row)) for row in rows]
        self._current_capture.setdefault("channel_rows", {})[channel] = encoded
        self._current_capture.setdefault("channel_scores", {})[channel] = [
            score_values[index] if index < len(score_values) else None
            for index in range(len(encoded))
        ]

    def _exact(self, plan: RetrievalPlan, question: str, limit: int) -> list[dict[str, Any]]:
        rows = super()._exact(plan, question, limit)
        self._record_rows("exact", rows)
        return rows

    def _vector(self, question: str, plan: RetrievalPlan, limit: int) -> tuple[list[Any], list[Any], list[float], Any]:
        dense, sparse, query_vector, semantic_query = super()._vector(question, plan, limit)
        self._record_rows("dense", [hit.payload for hit in dense], [getattr(hit, "score", None) for hit in dense])
        self._record_rows("sparse", [hit.payload for hit in sparse], [getattr(hit, "score", None) for hit in sparse])
        return dense, sparse, query_vector, semantic_query

    def _sparse_query(self, text: str, query_filter: Any, limit: int) -> list[Any]:
        self._increment("sparse_encoding_calls")
        return super()._sparse_query(text, query_filter, limit)

    def _paper(self, query_vector: list[float], plan: RetrievalPlan, limit: int) -> list[dict[str, Any]]:
        rows = super()._paper(query_vector, plan, limit)
        self._record_rows("paper", rows)
        return rows

    def _workflow(self, question: str, plan: RetrievalPlan, limit: int) -> list[dict[str, Any]]:
        rows = super()._workflow(question, plan, limit)
        self._record_rows("workflow", rows)
        return rows

    def _graph(self, seeds: list[dict[str, Any]], plan: RetrievalPlan, limit: int) -> list[dict[str, Any]]:
        rows = super()._graph(seeds, plan, limit)
        self._record_rows("graph", rows)
        return rows

    def retrieve(self, question: str, plan: RetrievalPlan | None = None) -> dict[str, Any]:
        pass_origin = self._next_pass_origin or (PassOrigin.INITIAL if plan is None else PassOrigin.TARGETED)
        if self._current_capture is not None:
            raise RuntimeError("nested capture pass")
        self._current_capture = {
            "pass_origin": pass_origin.value,
            "query_text": question,
            "supplied_plan": plan is not None,
            "supplied_plan_value": _jsonable(plan) if plan is not None else None,
            "channel_rows": {},
        }
        self._increment("initial_retrieval_passes" if pass_origin is PassOrigin.INITIAL else "targeted_retrieval_passes")
        try:
            with production_selector_capture() as selector_capture:
                result = super().retrieve(question, plan=plan)
            self._current_capture["result"] = _jsonable(result)
            self._current_capture["selector_capture"] = selector_capture
            return result
        except Exception as exc:
            if self._current_capture is not None:
                self._current_capture["failure"] = f"{type(exc).__name__}: {exc}"
            raise


def _targeted_plan_delta(initial_plan: Mapping[str, Any], targeted_plan: Mapping[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    missing_symbols = [error.split("symbol:", 1)[1] for error in errors if "symbol:" in error]
    initial_symbols = list(initial_plan.get("symbols") or [])
    targeted_symbols = list(targeted_plan.get("symbols") or [])
    return {
        "missing_symbols": missing_symbols,
        "symbols_prepended": [symbol for symbol in targeted_symbols if symbol not in initial_symbols],
        "initial_symbols": initial_symbols,
        "targeted_symbols": targeted_symbols,
    }


def execute_case(
    agent: QAAgent,
    retriever: CapturingRetriever,
    row: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Execute one screening case once and return ledger entry + treatment row."""

    case_id = str(row["case_id"])
    question = str(row["query"])
    retriever.begin_case()
    initial_pass: dict[str, Any] | None = None
    targeted_pass: dict[str, Any] | None = None
    initial_state: dict[str, Any] = {"question": question}
    try:
        retriever.prepare_pass(PassOrigin.INITIAL)
        initial_pass = agent._retrieve(initial_state)["bundle"]
        initial_capture = retriever.finish_pass()
        initial_state["bundle"] = initial_pass
        initial_state.update(agent._sufficiency(initial_state))
        initial_sufficient = bool(initial_state.get("sufficient"))
        initial_errors = list(initial_state.get("errors") or [])
        plan_data = dict(initial_pass.get("plan") or {})
        target_allowed = (
            not initial_sufficient
            and int(getattr(retriever.policies, "max_targeted_retrievals", 0)) > 0
            and not plan_data.get("version_conflicts")
        )
        if not target_allowed:
            counts = dict(initial_capture.get("call_ledger") or {})
            return {
                "screening_position": None,
                "case_id": case_id,
                "initial_execution_completed": True,
                "targeted_triggered": False,
                "targeted_execution_completed": False,
                "complete_snapshot_valid": None,
                "treatment_cohort_included": False,
                "infrastructure_error": None,
                "measured_call_counts": counts,
            }, None

        retriever.prepare_pass(PassOrigin.TARGETED)
        with production_selector_capture() as targeted_selector_capture:
            targeted_update = agent._targeted_retrieve(initial_state)
        targeted_capture = retriever.finish_pass()
        targeted_capture["selector_capture"] = targeted_selector_capture
        targeted_capture["result"] = targeted_capture.get("result") or {}
        # The QA node returns the merged bundle, while the CapturingRetriever
        # retains the raw targeted retrieval result in its own capture.
        targeted_bundle = targeted_update["bundle"]
        post_state = dict(initial_state)
        post_state.update(targeted_update)
        post_state.update(agent._sufficiency(post_state))
        targeted_result = targeted_capture["result"]
        initial_snapshot, initial_aux = build_pass_snapshot(initial_capture, PassOrigin.INITIAL)
        targeted_snapshot, targeted_aux = build_pass_snapshot(targeted_capture, PassOrigin.TARGETED)
        consistency = validate_both_origin_payload_consistency(
            initial_aux["raw_payloads"], targeted_aux["raw_payloads"]
        )
        if not consistency["consistent"]:
            raise CaptureFidelityError("BOTH-origin payload consistency failed")
        trigger = TargetedTriggerContext(
            original_question=question,
            initial_sufficient=initial_sufficient,
            initial_sufficiency_errors=tuple(initial_errors),
            targeted_query_text=str(targeted_capture["query_text"]),
            targeted_retrieval_plan=dict(targeted_snapshot.retrieval_plan),
            targeted_plan_delta=_targeted_plan_delta(
                initial_snapshot.retrieval_plan,
                targeted_snapshot.retrieval_plan,
                initial_errors,
            ),
        )
        pool = build_global_candidate_pool(initial_snapshot, targeted_snapshot, trigger)
        initial_evidence = initial_aux["actual_evidence"]
        targeted_evidence = targeted_aux["actual_evidence"]
        merged_evidence = _evidence_dicts(targeted_bundle.get("evidence") or [])
        s0 = validate_s0_replay(targeted_evidence, initial_evidence, merged_evidence)
        if not s0["parity"]:
            raise CaptureFidelityError("S0 replay parity failed")
        case_counts = {
            key: int((initial_capture.get("call_ledger") or {}).get(key, 0))
            + int((targeted_capture.get("call_ledger") or {}).get(key, 0))
            for key in CALL_COUNTER_KEYS
        }
        execution_identity = {
            "task": "C8-A2",
            "contract_id": CONTRACT_ID,
            "treatment_preregistration_identity": TREATMENT_ID,
            "runtime_source_head": _current_head(),
            "production_fusion": "P0 CURRENT",
            "production_selector": "CURRENT_SELECTOR",
            "reranker_model": getattr(retriever.vertex.settings, "generation_model", None),
            "reranker_location": getattr(retriever.vertex.settings, "location", None),
            "reranker_prompt_identity": "panda_agent.prompts.RERANK_SYSTEM_PROMPT",
            "reranker_prompt_reference": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT",
            "capture_script": "evaluation/scripts/capture_c8_a2_two_pass.py",
            "answer_generation_executed": False,
            "g1_global_reranker_executed": False,
        }
        record = {
            "schema_version": "c8-a2-two-pass-capture-v1",
            "capture_status": "PASS",
            "case_id": case_id,
            "original_question": question,
            "question": question,
            "intent": row["intent"],
            "execution_identity": execution_identity,
            "INITIAL": {
                "PassSnapshot": initial_snapshot.as_dict(),
                "raw_selected_evidence": initial_evidence,
                "sufficiency": {
                    "sufficient": initial_sufficient,
                    "errors": initial_errors,
                },
                "capture_auxiliary": initial_aux,
                "call_ledger": initial_capture.get("call_ledger", {}),
            },
            "TARGETED": {
                "PassSnapshot": targeted_snapshot.as_dict(),
                "raw_selected_evidence": targeted_evidence,
                "sufficiency": {
                    "sufficient": bool(post_state.get("sufficient")),
                    "errors": list(post_state.get("errors") or []),
                },
                "capture_auxiliary": targeted_aux,
                "call_ledger": targeted_capture.get("call_ledger", {}),
            },
            "TargetedTriggerContext": trigger.as_dict(),
            "validated_global_candidate_pool": json.loads(serialize_pool(pool)),
            "actual_current_merged_evidence": merged_evidence,
            "S0_replay_evidence": s0["replayed_evidence"],
            "S0_replay_parity": s0,
            "raw_stable_payload_data": {
                "INITIAL": initial_aux["raw_payloads"],
                "TARGETED": targeted_aux["raw_payloads"],
            },
            "policy_config_identities": {
                "fusion": "P0 CURRENT",
                "selector": "CURRENT_SELECTOR",
                "reranker": execution_identity["reranker_model"],
                "rerank_system_prompt": execution_identity["reranker_prompt_identity"],
                "retrieval_policy": "configs/retrieval_policies.yaml",
            },
            "BOTH_origin_payload_consistency": consistency,
            "call_ledger": case_counts,
            "G1_real_execution": False,
        }
        screening = {
            "screening_position": None,
            "case_id": case_id,
            "initial_execution_completed": True,
            "targeted_triggered": True,
            "targeted_execution_completed": True,
            "complete_snapshot_valid": True,
            "treatment_cohort_included": True,
            "infrastructure_error": None,
            "measured_call_counts": case_counts,
        }
        return screening, record
    except Exception:
        if retriever._active_counts is not None and retriever._current_capture is not None:
            try:
                retriever.finish_pass()
            except Exception:
                pass
        raise


def _aggregate_counts(records: Sequence[Mapping[str, Any]], ledger_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    totals = {key: 0 for key in CALL_COUNTER_KEYS}
    for row in ledger_rows:
        for key in CALL_COUNTER_KEYS:
            totals[key] += int((row.get("measured_call_counts") or {}).get(key, 0))
    totals["sql_candidate_read_calls"] = "NOT_INSTRUMENTED"
    totals.update({key: 0 for key in STATIC_ZERO_CALL_KEYS})
    totals.update({
        "REAL_G1_EXECUTIONS": 0,
        "REAL_GLOBAL_RERANKER_CALLS": 0,
        "QA_GENERATION_CALLS": 0,
        "VERIFIER_CALLS": 0,
        "JUDGE_CALLS": 0,
        "DB_INDEX_WRITES": 0,
    })
    return totals


def _append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(_jsonable(record), ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def _write_screening_ledger(
    ledger_rows: Sequence[Mapping[str, Any]],
    *,
    targeted_count: int,
    treatment_ids: Sequence[str],
    expansion_used: bool,
    verdict: str,
) -> None:
    normalized = []
    for index, row in enumerate(ledger_rows, 1):
        value = dict(row)
        value["screening_position"] = index
        normalized.append(value)
    _write_json(
        SCREENING_LEDGER_PATH,
        {
            "schema_version": "c8-a2-screening-ledger-v1",
            "artifact_role": "C8_A2_SCREENING_LEDGER",
            "preregistration_identity": TREATMENT_ID,
            "safe_projection_identity": str(PROJECTION_PATH.relative_to(ROOT)),
            "screened_count": len(normalized),
            "targeted_trigger_count": targeted_count,
            "treatment_case_ids": list(treatment_ids),
            "expansion_used": expansion_used,
            "replacements": 0,
            "retries": 0,
            "verdict": verdict,
            "records": normalized,
            "call_ledger": _aggregate_counts((), normalized),
        },
    )


def _build_capture_report(
    preregistration: Mapping[str, Any],
    ledger_rows: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
    *,
    expansion_used: bool,
    infrastructure_failures: Sequence[Mapping[str, Any]],
    scientific_fields_changed: bool,
    verdict: str,
) -> dict[str, Any]:
    treatment_ids = [str(record["case_id"]) for record in records if record.get("capture_status") == "PASS"]
    treatment_count = len(treatment_ids)
    pass_counts = {
        "INITIAL": {"stage_f": 0, "stage_p": 0, "stage_s": 0, "complete": 0, "contract": 0},
        "TARGETED": {"stage_f": 0, "stage_p": 0, "stage_s": 0, "complete": 0, "contract": 0},
    }
    both_consistent = 0
    s0_parity_count = 0
    s0_mismatch_ids: list[str] = []
    for record in records:
        if record.get("capture_status") != "PASS":
            continue
        for pass_name in ("INITIAL", "TARGETED"):
            pass_counts[pass_name]["complete"] += int(record[pass_name]["PassSnapshot"]["completeness"] == "COMPLETE")
            parity = record[pass_name]["capture_auxiliary"]["parity"]
            pass_counts[pass_name]["stage_f"] += int(parity.get("stage_f"))
            pass_counts[pass_name]["stage_p"] += int(parity.get("stage_p"))
            pass_counts[pass_name]["stage_s"] += int(parity.get("stage_s"))
            pass_counts[pass_name]["contract"] += 1
        both_consistent += int(record["BOTH_origin_payload_consistency"]["consistent"])
        if record["S0_replay_parity"]["parity"]:
            s0_parity_count += 1
        else:
            s0_mismatch_ids.append(str(record["case_id"]))
    ledger_call_counts = _aggregate_counts(records, ledger_rows)
    report = {
        "schema_version": "c8-a2-two-pass-capture-report-v1",
        "artifact_role": "C8_A2_TWO_PASS_CAPTURE_REPORT",
        "task": "C8-A2",
        "preregistration_identity": TREATMENT_ID,
        "safe_projection_identity": projection_summary(),
        "source_runtime_head": preregistration.get("source_head_at_preregistration"),
        "screened_count": len(ledger_rows),
        "targeted_count": sum(int(bool(row.get("targeted_triggered"))) for row in ledger_rows),
        "treatment_case_count": treatment_count,
        "treatment_case_ids": treatment_ids,
        "expansion_used": expansion_used,
        "complete_initial_count": pass_counts["INITIAL"]["complete"],
        "complete_targeted_count": pass_counts["TARGETED"]["complete"],
        "contract_validation_count": min(pass_counts["INITIAL"]["contract"], pass_counts["TARGETED"]["contract"]),
        "stage_f_parity": {
            "INITIAL": f"{pass_counts['INITIAL']['stage_f']}/{treatment_count}",
            "TARGETED": f"{pass_counts['TARGETED']['stage_f']}/{treatment_count}",
        },
        "stage_p_parity": {
            "INITIAL": f"{pass_counts['INITIAL']['stage_p']}/{treatment_count}",
            "TARGETED": f"{pass_counts['TARGETED']['stage_p']}/{treatment_count}",
        },
        "stage_s_parity": {
            "INITIAL": f"{pass_counts['INITIAL']['stage_s']}/{treatment_count}",
            "TARGETED": f"{pass_counts['TARGETED']['stage_s']}/{treatment_count}",
        },
        "both_origin_payload_consistency": f"{both_consistent}/{treatment_count}",
        "S0_REPLAY_PARITY": {
            "identity": S0_IDENTITY,
            "count": s0_parity_count,
            "total": treatment_count,
            "rate": (s0_parity_count / treatment_count if treatment_count else 0.0),
            "mismatch_case_ids": s0_mismatch_ids,
        },
        "call_ledger": ledger_call_counts,
        "GOLD_FILE_ACCESSED": False,
        "GOLD_RELEVANCE_LABELS_ACCESSED": False,
        "GOLD_EVIDENCE_GROUPS_ACCESSED": False,
        "GOLD_ANSWER_RUBRICS_ACCESSED": False,
        "GOLD_EVALUATIONS": 0,
        "NOVEL_EVALUATIONS": 0,
        "REAL_G1_EXECUTIONS": 0,
        "REAL_GLOBAL_RERANKER_CALLS": 0,
        "QA_GENERATION_CALLS": 0,
        "VERIFIER_CALLS": 0,
        "JUDGE_CALLS": 0,
        "DB_INDEX_WRITES": 0,
        "prereg_scientific_fields_changed_after_live_start": scientific_fields_changed,
        "infrastructure_failures": list(infrastructure_failures),
        "historical_pre_capture_aborts": HISTORICAL_PRE_CAPTURE_ABORTS,
        "A2_verdict": verdict,
        "A3_eligibility": "NEXT_ELIGIBLE / NOT_STARTED" if verdict == "PASS" else "NOT_ELIGIBLE",
        "PRODUCTION_BEHAVIOR_CHANGED": False,
        "QA_RUNTIME_CHANGED": False,
        "RETRIEVER_RUNTIME_CHANGED": False,
        "CONFIG_CHANGED": False,
        "PRODUCTION_FUSION_CHANGED": False,
        "PRODUCTION_SELECTOR_CHANGED": False,
    }
    return report


def synthetic_preflight() -> dict[str, Any]:
    """Exercise G1 and capture helpers without retrieval or model calls."""

    from panda_agent.global_candidate_pool import (
        ChannelCandidate as PoolChannelCandidate,
        PassOrigin as PoolPassOrigin,
        PassSnapshot as PoolPassSnapshot,
        PayloadProvenance as PoolPayloadProvenance,
        build_global_candidate_pool as build_pool,
    )
    from evaluation.c8_global_treatment import (
        best_rank_fusion,
        prepare_global_m_p_selection,
        prepare_global_reranker_input,
    )

    def payload(object_id: str) -> PoolPayloadProvenance:
        return PoolPayloadProvenance(
            object_id=object_id,
            source_id="pandaroot",
            source_version_id="pandaroot@fixture",
            object_type="source_file",
            locator={"path": f"src/{object_id}.cxx"},
            title=object_id,
            text=f"fixture payload {object_id}",
        )

    def snapshot(origin: PoolPassOrigin, rows: Sequence[tuple[str, str]]) -> PoolPassSnapshot:
        channel_candidates = tuple(PoolChannelCandidate(channel, object_id, rank) for channel, object_id, rank in rows)
        universe = list(dict.fromkeys(object_id for _, object_id, _ in rows))
        stage_r = universe[:1]
        stage_m = list(dict.fromkeys([*stage_r, *universe]))
        stage_p = list(reversed(stage_m))
        selected = universe[:1]
        return PoolPassSnapshot(
            pass_origin=origin,
            completeness=CompletenessState.COMPLETE,
            query_text="fixture question",
            retrieval_plan={"intent": "api", "source_budgets": {"code": 1.0}, "symbols": [], "required_source_types": []},
            channel_candidates=channel_candidates,
            stage_f_order=tuple(universe),
            stage_f_scores={object_id: 1.0 for object_id in universe},
            stage_r_order=tuple(stage_r),
            stage_m_order=tuple(stage_m),
            stage_p_order=tuple(stage_p),
            stage_s_selected_object_ids=tuple(selected),
            stage_s_evidence_ids={object_id: f"evidence.{object_id}" for object_id in selected},
            payloads={object_id: payload(object_id) for object_id in universe},
        )

    initial = snapshot(PoolPassOrigin.INITIAL, (("dense", "obj-b", 1), ("exact", "obj-a", 1)))
    targeted = snapshot(PoolPassOrigin.TARGETED, (("dense", "obj-b", 1), ("sparse", "obj-c", 1)))
    trigger = TargetedTriggerContext("fixture question", False, ("missing",), "fixture targeted", {}, {})
    pool = build_pool(initial, targeted, trigger)
    fusion = best_rank_fusion(pool)
    reranker_input = prepare_global_reranker_input("fixture question", fusion, {candidate.object_id: candidate.payload.as_dict() for candidate in pool.candidates})
    global_preparation = prepare_global_m_p_selection(
        "fixture question",
        initial.retrieval_plan,
        fusion,
        {candidate.object_id: candidate.payload.as_dict() for candidate in pool.candidates},
        list(fusion.candidate_ids[:2]),
        final_evidence_limit=2,
    )
    if reranker_input["question"] != "fixture question" or reranker_input["executed"]:
        raise AssertionError("synthetic global reranker preparation violated question/isolation contract")
    if fusion.candidate_ids != tuple(sorted(fusion.candidate_ids, key=lambda object_id: (-fusion.score_map[object_id], object_id))):
        raise AssertionError("synthetic G1 ordering is not deterministic")
    if global_preparation["executed"]:
        raise AssertionError("synthetic global preparation must not execute")
    return {
        "status": "PASS",
        "retrieval_calls": 0,
        "model_calls": 0,
        "global_treatment": TREATMENT_ID,
        "real_g1_executions": 0,
    }


def run_authoritative_capture(
    preregistration: Mapping[str, Any],
    projection_records: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Run exactly one ordered live screening/capture attempt."""

    if CAPTURE_PATH.exists() or SCREENING_LEDGER_PATH.exists() or CAPTURE_REPORT_PATH.exists():
        raise FileExistsError("C8-A2 output exists; refusing a second scientific run")
    pre_live_scientific = deepcopy(preregistration["scientific_fields"])
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    delegate_vertex = VertexAIClient(VertexSettings.from_env())
    retriever = CapturingRetriever(ROOT, delegate_vertex)
    agent = QAAgent(ROOT, retriever=retriever, vertex=retriever.vertex)
    ledger_rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    infrastructure_failures: list[dict[str, Any]] = []
    targeted_count = 0
    expansion_used = False
    live_started = False

    def process(row: Mapping[str, str]) -> bool:
        nonlocal targeted_count, live_started
        position = len(ledger_rows) + 1
        try:
            live_started = True
            screening, record = execute_case(agent, retriever, row)
            screening["screening_position"] = position
            ledger_rows.append(screening)
            if screening["targeted_triggered"]:
                targeted_count += 1
            if record is not None:
                records.append(record)
                _append_jsonl(CAPTURE_PATH, record)
            _write_screening_ledger(
                ledger_rows,
                targeted_count=targeted_count,
                treatment_ids=[str(item["case_id"]) for item in records],
                expansion_used=expansion_used,
                verdict="IN_PROGRESS",
            )
            return True
        except Exception as exc:
            retriever_passes = retriever.case_passes()
            failure = {
                "screening_position": position,
                "case_id": str(row["case_id"]),
                "initial_execution_completed": any(item.get("pass_origin") == "INITIAL" and "result" in item for item in retriever_passes),
                "targeted_triggered": any(item.get("pass_origin") == "TARGETED" for item in retriever_passes),
                "targeted_execution_completed": any(item.get("pass_origin") == "TARGETED" and "result" in item for item in retriever_passes),
                "complete_snapshot_valid": False,
                "treatment_cohort_included": False,
                "infrastructure_error": f"{type(exc).__name__}: {exc}",
                "measured_call_counts": {
                    key: sum(int((item.get("call_ledger") or {}).get(key, 0)) for item in retriever_passes)
                    for key in CALL_COUNTER_KEYS
                },
            }
            ledger_rows.append(failure)
            infrastructure_failures.append({"screening_position": position, "case_id": row["case_id"], "error": failure["infrastructure_error"]})
            _append_jsonl(
                CAPTURE_PATH,
                {
                    "schema_version": "c8-a2-two-pass-capture-v1",
                    "capture_status": "FAILED",
                    "case_id": row["case_id"],
                    "question": row["query"],
                    "failure": failure["infrastructure_error"],
                    "single_attempt": True,
                    "replacement_case_id": None,
                    "partial_pass_count": len(retriever_passes),
                },
            )
            _write_screening_ledger(
                ledger_rows,
                targeted_count=targeted_count,
                treatment_ids=[str(item["case_id"]) for item in records],
                expansion_used=expansion_used,
                verdict="INCONCLUSIVE",
            )
            return False

    for row in projection_records[: len(PRIMARY_CASE_IDS)]:
        if not process(row):
            break
        if targeted_count >= 12:
            break
    if len(ledger_rows) == len(PRIMARY_CASE_IDS) and targeted_count < 6 and targeted_count < 12 and not infrastructure_failures:
        expansion_used = True
        for row in projection_records[len(PRIMARY_CASE_IDS) :]:
            if not process(row):
                break
            if targeted_count >= 12:
                break

    persisted_preregistration = _read_json(PREREGISTRATION_PATH)
    scientific_fields_changed = (
        persisted_preregistration.get("scientific_fields") != pre_live_scientific
        or preregistration.get("scientific_fields") != pre_live_scientific
    )
    screened_count = len(ledger_rows)
    if infrastructure_failures or scientific_fields_changed or targeted_count < 6 or screened_count > 24:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "PASS"
    if verdict == "PASS":
        if any(record.get("capture_status") != "PASS" for record in records):
            verdict = "INCONCLUSIVE"
        if len(records) != targeted_count or len(records) > 12:
            verdict = "INCONCLUSIVE"
    _write_screening_ledger(
        ledger_rows,
        targeted_count=targeted_count,
        treatment_ids=[str(item["case_id"]) for item in records],
        expansion_used=expansion_used,
        verdict=verdict,
    )
    report = _build_capture_report(
        preregistration,
        ledger_rows,
        records,
        expansion_used=expansion_used,
        infrastructure_failures=infrastructure_failures,
        scientific_fields_changed=scientific_fields_changed,
        verdict=verdict,
    )
    _write_json(CAPTURE_REPORT_PATH, report)
    return {
        "status": verdict,
        "screened_count": screened_count,
        "targeted_count": targeted_count,
        "treatment_case_ids": [str(item["case_id"]) for item in records],
        "expansion_used": expansion_used,
        "infrastructure_failures": infrastructure_failures,
        "prereg_scientific_fields_changed_after_live_start": scientific_fields_changed,
        "capture_report": str(CAPTURE_REPORT_PATH.relative_to(ROOT)),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare-only", action="store_true")
    modes.add_argument("--preflight-only", action="store_true")
    modes.add_argument("--run-live", action="store_true")
    args = parser.parse_args(argv)

    if args.prepare_only:
        prepared = prepare_preregistration()
        print(json.dumps({"status": "PASS", "preregistration": str(PREREGISTRATION_PATH.relative_to(ROOT)), "scientific_fields": len(prepared["scientific_fields"])}, ensure_ascii=False, sort_keys=True))
        return 0

    projection_records = load_execution_projection()
    preregistration = load_frozen_preregistration()
    if args.preflight_only:
        result = {"projection": projection_summary(), "synthetic": synthetic_preflight(), "preregistration": str(PREREGISTRATION_PATH.relative_to(ROOT))}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0

    synthetic = synthetic_preflight()
    result = run_authoritative_capture(preregistration, projection_records)
    result["synthetic_preflight"] = synthetic
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
