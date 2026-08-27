"""Evaluation-only C8 global-treatment preparation.

This module is deliberately disconnected from the production retrieval path.
It consumes a validated ``c8.global_candidate_pool.v1`` pool and prepares the
single preregistered G1 treatment for future offline A3 replay.  It never
retrieves, calls a model, writes an index, or selects a treatment from real
cases.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from collections.abc import Mapping, Sequence
from typing import Any, Callable

from panda_agent.global_candidate_pool import (
    CandidateOrigin,
    GlobalCandidate,
    GlobalCandidatePool,
)


TREATMENT_ID = "C8_GLOBAL_BEST_RANK_RRF_V1"
CANDIDATE_IDENTITY = "object_id"
CHANNEL_ORDER = ("exact", "dense", "sparse", "paper", "workflow", "graph")
CHANNEL_WEIGHTS = {
    "exact": 2.0,
    "dense": 1.0,
    "sparse": 1.0,
    "paper": 1.15,
    "workflow": 1.2,
    "graph": 0.8,
}
RRF_K = 60
GLOBAL_RERANKER_TOP_K = 30
FINAL_EVIDENCE_LIMIT = 12


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


def _pool_candidates(pool: GlobalCandidatePool | Mapping[str, Any]) -> list[Any]:
    candidates = pool.candidates if isinstance(pool, GlobalCandidatePool) else pool.get("candidates", [])
    return list(candidates)


def _candidate_value(candidate: Any, name: str, default: Any = None) -> Any:
    if isinstance(candidate, Mapping):
        return candidate.get(name, default)
    return getattr(candidate, name, default)


def _occurrence_value(occurrence: Any, name: str, default: Any = None) -> Any:
    if occurrence is None:
        return default
    if isinstance(occurrence, Mapping):
        return occurrence.get(name, default)
    return getattr(occurrence, name, default)


def _channel_occurrences(occurrence: Any) -> list[Any]:
    values = _occurrence_value(occurrence, "channel_occurrences", ())
    return list(values or ())


def _channel_value(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, Mapping):
        return item.get(name, default)
    return getattr(item, name, default)


def _payload_dict(candidate: Any) -> dict[str, Any]:
    payload = _candidate_value(candidate, "payload", {})
    value = _jsonable(payload)
    if not isinstance(value, dict):
        raise ValueError("global candidate payload must be a mapping")
    return value


def _candidate_origin(candidate: Any) -> str:
    origin = _candidate_value(candidate, "origin")
    return origin.value if isinstance(origin, CandidateOrigin) else str(origin)


@dataclass(frozen=True)
class GlobalFusionResult:
    """Deterministic G1 best-rank weighted-RRF receipt."""

    treatment_id: str
    candidate_ids: tuple[str, ...]
    score_map: Mapping[str, float]
    channel_ranks: Mapping[str, Mapping[str, int]]
    contributions: Mapping[str, tuple[Mapping[str, Any], ...]]
    channel_orders: Mapping[str, tuple[str, ...]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "treatment_id": self.treatment_id,
            "candidate_identity": CANDIDATE_IDENTITY,
            "rrf_k": RRF_K,
            "weights": dict(CHANNEL_WEIGHTS),
            "candidate_ids": list(self.candidate_ids),
            "score_map": dict(self.score_map),
            "channel_ranks": {
                object_id: dict(ranks)
                for object_id, ranks in sorted(self.channel_ranks.items())
            },
            "contributions": {
                object_id: [dict(item) for item in items]
                for object_id, items in sorted(self.contributions.items())
            },
            "channel_orders": {
                channel: list(order)
                for channel, order in self.channel_orders.items()
            },
            "rank_rule": "best_minimum_rank_across_INITIAL_and_TARGETED_per_object_channel",
            "one_contribution_per_object_channel": True,
            "origin_bonus": False,
            "pass_bonus": False,
            "tie_break": "object_id_lexicographic",
        }


def best_rank_fusion(
    pool: GlobalCandidatePool | Mapping[str, Any],
) -> GlobalFusionResult:
    """Apply the one frozen G1 treatment to a validated candidate pool.

    The minimum rank is taken independently for each object/channel across the
    two pass occurrences.  An object/channel contributes at most once, and
    ``BOTH`` has no score bonus.
    """

    ranks_by_object: dict[str, dict[str, int]] = {}
    origins: dict[str, str] = {}
    for candidate in _pool_candidates(pool):
        object_id = str(_candidate_value(candidate, "object_id"))
        if not object_id:
            raise ValueError("G1 candidate lacks object_id")
        origins[object_id] = _candidate_origin(candidate)
        ranks = ranks_by_object.setdefault(object_id, {})
        for occurrence_name in ("initial_occurrence", "targeted_occurrence"):
            occurrence = _candidate_value(candidate, occurrence_name)
            for item in _channel_occurrences(occurrence):
                channel = str(_channel_value(item, "channel"))
                rank = int(_channel_value(item, "rank"))
                if channel not in CHANNEL_WEIGHTS:
                    raise ValueError(f"G1 received non-production channel {channel!r}")
                if rank < 1:
                    raise ValueError(f"G1 rank must be >= 1 for {object_id}/{channel}")
                previous = ranks.get(channel)
                ranks[channel] = rank if previous is None else min(previous, rank)

    score_map: dict[str, float] = {}
    contributions: dict[str, tuple[Mapping[str, Any], ...]] = {}
    for object_id, ranks in ranks_by_object.items():
        items: list[Mapping[str, Any]] = []
        total = 0.0
        for channel in CHANNEL_ORDER:
            if channel not in ranks:
                continue
            rank = ranks[channel]
            weight = CHANNEL_WEIGHTS[channel]
            contribution = weight / (RRF_K + rank)
            total += contribution
            items.append(
                {
                    "channel": channel,
                    "rank": rank,
                    "weight": weight,
                    "contribution": contribution,
                }
            )
        score_map[object_id] = total
        contributions[object_id] = tuple(items)

    ordered = tuple(sorted(score_map, key=lambda object_id: (-score_map[object_id], object_id)))
    channel_orders: dict[str, tuple[str, ...]] = {}
    for channel in CHANNEL_ORDER:
        channel_orders[channel] = tuple(
            sorted(
                (object_id for object_id, ranks in ranks_by_object.items() if channel in ranks),
                key=lambda object_id: (ranks_by_object[object_id][channel], object_id),
            )
        )
    return GlobalFusionResult(
        treatment_id=TREATMENT_ID,
        candidate_ids=ordered,
        score_map=score_map,
        channel_ranks=ranks_by_object,
        contributions=contributions,
        channel_orders=channel_orders,
    )


def prepare_global_reranker_input(
    original_question: str,
    fusion: GlobalFusionResult,
    payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Prepare the future one-call global reranker input without calling it."""

    candidate_ids = list(fusion.candidate_ids[:GLOBAL_RERANKER_TOP_K])
    candidates = []
    for object_id in candidate_ids:
        payload = dict(payloads[object_id])
        candidates.append(
            {
                "object_id": object_id,
                "title": payload.get("title"),
                "source_id": payload.get("source_id"),
                "text": str(payload.get("text") or "")[:2000],
            }
        )
    return {
        "question": original_question,
        "candidate_ids": candidate_ids,
        "candidates": candidates,
        "question_rule": "original_question",
        "reranker_identity": "CURRENT_RERANKER_AND_CURRENT_RERANK_SYSTEM_PROMPT",
        "executed": False,
    }


def _plan_value(plan: Mapping[str, Any] | Any, name: str, default: Any) -> Any:
    if isinstance(plan, Mapping):
        return plan.get(name, default)
    return getattr(plan, name, default)


def _source_type_of(item: Mapping[str, Any]) -> str:
    source_id = item.get("source_id")
    if source_id in {"li_2026", "karavdina_2015", "pflueger_2017"}:
        return "paper"
    if "sphinx" in str(source_id or ""):
        return "documentation"
    locator = item.get("locator") or {}
    path = str(locator.get("path") or "").replace("\\", "/").lower()
    if path.startswith(("docs/", "doc/")):
        return "documentation"
    if item.get("object_type") in {"workflow", "python_script", "shell_script"}:
        return "workflow"
    if item.get("object_type") == "readme_section":
        return "readme"
    if item.get("object_type") == "python_script":
        return "workflow"
    return "code"


def reconstruct_current_stage_p(
    original_question: str,
    plan: Mapping[str, Any] | Any,
    stage_m_order: Sequence[str],
    channel_orders: Mapping[str, Sequence[str]],
    payloads: Mapping[str, Mapping[str, Any]],
    channels_by_object: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, Any]:
    """Reproduce the current Stage-P priority preparation on frozen data.

    This is a behavior-equivalent evaluation copy of the current priority
    construction.  The caller supplies the actual pass/future channel order;
    no question-specific rule is introduced here.
    """

    base_order = list(dict.fromkeys(stage_m_order))
    channels = {
        object_id: list(values)
        for object_id, values in (channels_by_object or {}).items()
    }
    if not channels:
        channels = {object_id: [] for object_id in payloads}
        for channel, object_ids in channel_orders.items():
            for object_id in object_ids:
                channels.setdefault(object_id, []).append(channel)

    target_repositories = list(_plan_value(plan, "target_repositories", []) or [])
    preferred_sources = list(target_repositories)
    lowered_question = original_question.casefold()
    if any(term in lowered_question for term in ("restgas", "off-ip", "event_poca", "poca", "displaced")):
        preferred_sources = ["restgas_determination", "pandaroot", "luminosityfit", *preferred_sources]
    elif "pandaroot" in lowered_question:
        preferred_sources = ["pandaroot", "restgas_determination", "luminosityfit", *preferred_sources]
    preferred_sources = list(dict.fromkeys(preferred_sources))
    source_rank = {source_id: rank for rank, source_id in enumerate(preferred_sources)}

    intent = str(_plan_value(plan, "intent", ""))
    def symbol_order(value: str) -> tuple[int, int]:
        normalized = value.replace("\\", "/").lower()
        if intent == "troubleshooting" and ("readme" in normalized or "running/" in normalized):
            return (0, 0)
        return (1, 0 if "/" in value or "." in value else 1)

    symbol_first: list[str] = []
    exact_order = list(channel_orders.get("exact", ()))
    for symbol in sorted(list(_plan_value(plan, "symbols", []) or []), key=symbol_order):
        literal = str(symbol).replace("*", "").replace("?", "")
        matches: list[Mapping[str, Any]] = []
        for object_id in exact_order:
            item = payloads[object_id]
            locator = item.get("locator") or {}
            if literal and (
                literal in str(item.get("title") or "")
                or literal in str(locator.get("symbol") or "")
                or literal in str(locator.get("path") or "")
                or literal in str(item.get("text") or "")
            ):
                matches.append(item)
        if matches:
            def match_priority(item: Mapping[str, Any]) -> tuple[int, int, int, str]:
                locator = item.get("locator") or {}
                path = str(locator.get("path") or "").replace("\\", "/")
                exact_path = int(bool(literal and (
                    path == literal or ("/" in literal and path.endswith("/" + literal))
                )))
                page_level = int(item.get("object_type") in {"sphinx_page", "source_file", "readme_section"})
                return (source_rank.get(str(item.get("source_id")), 999), -exact_path, -page_level, str(item["object_id"]))

            matches.sort(key=match_priority)
            symbol_first.append(str(matches[0]["object_id"]))

    required_first: list[str] = []
    required_source_types = list(_plan_value(plan, "required_source_types", []) or [])
    for required in required_source_types:
        for object_id in base_order:
            item = payloads[object_id]
            source_type = _source_type_of(item)
            if source_type == required or (
                required in {"workflow", "graph"} and required in channels.get(object_id, ())
            ):
                required_first.append(object_id)
                break

    hinted_first: list[str] = []
    paper_page_hints = _plan_value(plan, "paper_page_hints", {}) or {}
    for object_id in base_order:
        item = payloads[object_id]
        source_id = item.get("source_id")
        page = (item.get("locator") or {}).get("pdf_page")
        if source_id in paper_page_hints and page is not None and int(page) in paper_page_hints[source_id]:
            hinted_first.append(object_id)

    stage_p_order = list(dict.fromkeys([*hinted_first, *required_first, *symbol_first, *base_order]))
    return {
        "stage_m_order": base_order,
        "stage_p_order": stage_p_order,
        "hinted_first": hinted_first,
        "required_first": required_first,
        "symbol_first": symbol_first,
        "mandatory_symbol_ids": sorted(set(symbol_first)),
        "channels_by_object": channels,
    }


def prepare_global_m_p_selection(
    original_question: str,
    final_plan: Mapping[str, Any] | Any,
    fusion: GlobalFusionResult,
    payloads: Mapping[str, Mapping[str, Any]],
    global_reranked_object_ids: Sequence[str],
    *,
    final_evidence_limit: int = FINAL_EVIDENCE_LIMIT,
    mandatory_symbol_ids: Sequence[str] = (),
    selector: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Prepare fixed-output global M/P and CURRENT_SELECTOR inputs.

    ``global_reranked_object_ids`` represents a future fixed reranker output;
    this function itself makes no model call.  ``final_plan`` must be the
    actual TARGETED plan, while question-derived Stage-P semantics use the
    original question.
    """

    reranked = list(global_reranked_object_ids)
    fusion_ids = list(fusion.candidate_ids)
    allowed = set(fusion_ids[:GLOBAL_RERANKER_TOP_K])
    if not set(reranked) <= allowed:
        raise ValueError("global reranker output must be drawn from the unique G1 top-30")
    if len(reranked) != len(set(reranked)):
        raise ValueError("global reranker output must have unique object IDs")
    stage_m_order = list(dict.fromkeys([*reranked, *fusion_ids]))
    channels_by_object = {
        object_id: [channel for channel in CHANNEL_ORDER if channel in fusion.channel_ranks.get(object_id, {})]
        for object_id in fusion_ids
    }
    stage_p = reconstruct_current_stage_p(
        original_question,
        final_plan,
        stage_m_order,
        fusion.channel_orders,
        payloads,
        channels_by_object,
    )
    selected: Any = None
    excluded: Any = None
    backfill: Any = None
    if selector is None:
        from panda_agent.retrieval import RetrievalPlan, select_final_evidence

        selector = select_final_evidence
        plan_value = final_plan if isinstance(final_plan, RetrievalPlan) else RetrievalPlan.model_validate(final_plan)
    else:
        plan_value = final_plan
    selected, excluded, backfill = selector(
        stage_p["stage_p_order"],
        {object_id: dict(payloads[object_id]) for object_id in fusion_ids},
        dict(fusion.score_map),
        channels_by_object,
        plan_value,
        final_evidence_limit,
        set(mandatory_symbol_ids) or set(stage_p["mandatory_symbol_ids"]),
    )
    return {
        "treatment_id": TREATMENT_ID,
        "candidate_identity": CANDIDATE_IDENTITY,
        "global_fusion": fusion.as_dict(),
        "global_reranked_object_ids": reranked,
        "stage_m_order": stage_m_order,
        "stage_p_order": stage_p["stage_p_order"],
        "stage_p_preparation": stage_p,
        "selector_identity": "CURRENT_SELECTOR",
        "final_plan_identity": "actual_targeted_retrieval_plan",
        "question_identity": "original_question",
        "selected_evidence": _jsonable(selected),
        "excluded": _jsonable(excluded),
        "backfill_admissions": _jsonable(backfill),
        "final_evidence_limit": final_evidence_limit,
        "executed": False,
    }


def serialize_treatment(value: Any) -> str:
    """Stable serialization for synthetic receipts and future fixtures."""

    return json.dumps(_jsonable(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


__all__ = [
    "TREATMENT_ID",
    "CANDIDATE_IDENTITY",
    "CHANNEL_ORDER",
    "CHANNEL_WEIGHTS",
    "RRF_K",
    "GLOBAL_RERANKER_TOP_K",
    "FINAL_EVIDENCE_LIMIT",
    "GlobalFusionResult",
    "best_rank_fusion",
    "prepare_global_reranker_input",
    "reconstruct_current_stage_p",
    "prepare_global_m_p_selection",
    "serialize_treatment",
]
