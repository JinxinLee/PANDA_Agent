"""C8-A1 shadow contract for cross-pass global candidate pools.

This module defines the DATA / PROVENANCE contract
``c8.global_candidate_pool.v1`` required for a faithful future cross-pass
global comparison of the initial and targeted retrieval passes.  It is a
pure, deterministic, dependency-light contract module:

- it defines NO global ranking policy (no pass weighting, no targeted or
  BOTH-origin bonus, no new RRF weights, no score/rank normalization, no
  global score, no global rank, no reranker prompt, no selector, no final
  evidence limit);
- it implements object-level consolidation ONLY;
- production code must not import or call it (UNWIRED / SHADOW-EVALUATION
  CONTRACT).  ``qa.py``, ``retrieval.py`` production paths, and the current
  targeted merge behavior are intentionally unchanged.

Cross-pass candidate identity is ``object_id``.  ``evidence_id`` is derived
in production from ``object_id`` plus the pass-local retrieval-channel set,
so the same object can carry different evidence_id values across passes;
evidence_id is therefore preserved as occurrence/output provenance only and
must never be used as the global candidate identity.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping

CONTRACT_ID = "c8.global_candidate_pool.v1"

# Explicit non-goals of this contract, echoed by every serialized pool.
GLOBAL_RANKING_DEFINED = False
GLOBAL_FUSION_IMPLEMENTED = False
GLOBAL_RERANKER_IMPLEMENTED = False
GLOBAL_SELECTOR_IMPLEMENTED = False

# The serialized candidate order is deterministic object_id ordering.  It is
# a serialization convention only and must never be read as relevance rank.
SERIALIZATION_ORDER = "object_id_lexicographic"
SERIALIZATION_ORDER_SEMANTICS = "serialization_order_only_not_relevance_ranking"

# Production executed-channel vocabulary.  ``semantic_dense`` and ``lexical``
# are computed query representations with dedicated shadow methods; they are
# NOT_EXECUTED production channels and are rejected as channel provenance.
EXECUTED_CHANNEL_VOCABULARY = frozenset(
    {"exact", "dense", "sparse", "paper", "workflow", "graph"}
)
_REPRESENTATION_ONLY_CHANNELS = frozenset({"semantic_dense", "lexical"})


class PassOrigin(str, Enum):
    """Provenance role of one retrieval pass; implies no ranking priority."""

    INITIAL = "INITIAL"
    TARGETED = "TARGETED"


class CandidateOrigin(str, Enum):
    """Descriptive cross-pass origin classification; alters no ranking."""

    INITIAL_ONLY = "INITIAL_ONLY"
    TARGETED_ONLY = "TARGETED_ONLY"
    BOTH = "BOTH"


class CompletenessState(str, Enum):
    """COMPLETE vs truncated observability of one pass snapshot."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"


@dataclass(frozen=True)
class ChannelCandidate:
    """One object's occurrence inside one executed channel stream."""

    channel: str
    object_id: str
    rank: int
    channel_score: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "object_id": self.object_id,
            "rank": self.rank,
            "channel_score": self.channel_score,
        }


@dataclass(frozen=True)
class PayloadProvenance:
    """Stable source provenance of one knowledge object.

    ``text`` or ``payload_ref`` (a stable reference sufficient for later
    reranking) must be present.  No new corpus identities are invented.
    """

    object_id: str
    source_id: str
    source_version_id: str
    object_type: str | None = None
    locator: Mapping[str, Any] | None = None
    title: str | None = None
    text: str | None = None
    payload_ref: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "source_id": self.source_id,
            "source_version_id": self.source_version_id,
            "object_type": self.object_type,
            "locator": dict(self.locator) if self.locator else None,
            "title": self.title,
            "text": self.text,
            "payload_ref": self.payload_ref,
        }


@dataclass(frozen=True)
class CandidateOccurrence:
    """One object's independent record within one pass.

    Initial and targeted ranks are never collapsed, averaged, or made
    authoritative against each other.
    """

    pass_origin: PassOrigin
    object_id: str
    channel_occurrences: tuple[ChannelCandidate, ...]
    stage_f_rank: int | None = None
    stage_f_score: float | None = None
    stage_r_rank: int | None = None
    stage_m_rank: int | None = None
    stage_p_rank: int | None = None
    stage_s_selected: bool = False
    evidence_id: str | None = None
    exclusion_receipts: tuple[Mapping[str, Any], ...] = ()
    backfill_admitted: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "pass_origin": self.pass_origin.value,
            "object_id": self.object_id,
            "channel_occurrences": [item.as_dict() for item in self.channel_occurrences],
            "stage_f_rank": self.stage_f_rank,
            "stage_f_score": self.stage_f_score,
            "stage_r_rank": self.stage_r_rank,
            "stage_m_rank": self.stage_m_rank,
            "stage_p_rank": self.stage_p_rank,
            "stage_s_selected": self.stage_s_selected,
            "evidence_id": self.evidence_id,
            "exclusion_receipts": [dict(item) for item in self.exclusion_receipts],
            "backfill_admitted": self.backfill_admitted,
        }


@dataclass(frozen=True)
class PassSnapshot:
    """Complete reusable representation of one retrieval pass.

    ``completeness`` distinguishes COMPLETE state from truncated
    observability.  COMPLETE requires the Stage-F order/scores, Stage-M
    order, and Stage-P order to cover the full channel-candidate universe;
    the current production diagnostic output (top-30 prefixes, ID-only
    rankings) is PARTIAL and must be declared as such.  Stage R is the
    reranker's own output and may cover a subset of Stage F.
    """

    pass_origin: PassOrigin
    completeness: CompletenessState
    query_text: str
    retrieval_plan: Mapping[str, Any]
    channel_candidates: tuple[ChannelCandidate, ...]
    stage_f_order: tuple[str, ...]
    stage_f_scores: Mapping[str, float]
    stage_r_order: tuple[str, ...]
    stage_m_order: tuple[str, ...]
    stage_p_order: tuple[str, ...]
    stage_s_selected_object_ids: tuple[str, ...]
    stage_s_evidence_ids: Mapping[str, str]
    exclusions: tuple[Mapping[str, Any], ...] = ()
    backfill_admissions: tuple[Mapping[str, Any], ...] = ()
    payloads: Mapping[str, PayloadProvenance] = field(default_factory=dict)
    completeness_notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "pass_origin": self.pass_origin.value,
            "completeness": self.completeness.value,
            "query_text": self.query_text,
            "retrieval_plan": dict(self.retrieval_plan),
            "channel_candidates": [item.as_dict() for item in self.channel_candidates],
            "stage_f_order": list(self.stage_f_order),
            "stage_f_scores": dict(self.stage_f_scores),
            "stage_r_order": list(self.stage_r_order),
            "stage_m_order": list(self.stage_m_order),
            "stage_p_order": list(self.stage_p_order),
            "stage_s_selected_object_ids": list(self.stage_s_selected_object_ids),
            "stage_s_evidence_ids": dict(self.stage_s_evidence_ids),
            "exclusions": [dict(item) for item in self.exclusions],
            "backfill_admissions": [dict(item) for item in self.backfill_admissions],
            "payloads": {key: value.as_dict() for key, value in sorted(self.payloads.items())},
            "completeness_notes": list(self.completeness_notes),
        }


@dataclass(frozen=True)
class TargetedTriggerContext:
    """Provenance of why and how the second pass was created.

    These fields are trigger/query provenance only; they must not be
    reinterpreted as answer points and do not implement E3 decomposition.
    """

    original_question: str
    initial_sufficient: bool
    initial_sufficiency_errors: tuple[str, ...]
    targeted_query_text: str
    targeted_retrieval_plan: Mapping[str, Any]
    targeted_plan_delta: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "original_question": self.original_question,
            "initial_sufficient": self.initial_sufficient,
            "initial_sufficiency_errors": list(self.initial_sufficiency_errors),
            "targeted_query_text": self.targeted_query_text,
            "targeted_retrieval_plan": dict(self.targeted_retrieval_plan),
            "targeted_plan_delta": dict(self.targeted_plan_delta),
        }


@dataclass(frozen=True)
class GlobalCandidate:
    """One object-level candidate consolidated across passes.

    Carries NO global score and NO global rank.  ``initial_occurrence`` and
    ``targeted_occurrence`` keep per-pass provenance independent.
    """

    object_id: str
    origin: CandidateOrigin
    payload: PayloadProvenance
    initial_occurrence: CandidateOccurrence | None = None
    targeted_occurrence: CandidateOccurrence | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "origin": self.origin.value,
            "payload": self.payload.as_dict(),
            "initial_occurrence": (
                self.initial_occurrence.as_dict() if self.initial_occurrence else None
            ),
            "targeted_occurrence": (
                self.targeted_occurrence.as_dict() if self.targeted_occurrence else None
            ),
        }


@dataclass(frozen=True)
class GlobalCandidatePool:
    """Object-level global candidate pool over the two pass snapshots.

    ``candidates`` uses deterministic object_id ordering for serialization
    only.  Counts are observability only.
    """

    contract_id: str
    initial_snapshot: PassSnapshot
    targeted_snapshot: PassSnapshot | None
    targeted_trigger: TargetedTriggerContext | None
    candidates: tuple[GlobalCandidate, ...]
    counts: Mapping[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "global_ranking_defined": GLOBAL_RANKING_DEFINED,
            "global_fusion_implemented": GLOBAL_FUSION_IMPLEMENTED,
            "global_reranker_implemented": GLOBAL_RERANKER_IMPLEMENTED,
            "global_selector_implemented": GLOBAL_SELECTOR_IMPLEMENTED,
            "serialization_order": SERIALIZATION_ORDER,
            "serialization_order_semantics": SERIALIZATION_ORDER_SEMANTICS,
            "global_candidate_identity": "object_id",
            "initial_snapshot": self.initial_snapshot.as_dict(),
            "targeted_snapshot": (
                self.targeted_snapshot.as_dict() if self.targeted_snapshot else None
            ),
            "targeted_trigger": (
                self.targeted_trigger.as_dict() if self.targeted_trigger else None
            ),
            "candidates": [candidate.as_dict() for candidate in self.candidates],
            "counts": dict(self.counts),
        }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"{CONTRACT_ID}: {message}")


def _channel_universe(snapshot: PassSnapshot) -> set[str]:
    return {item.object_id for item in snapshot.channel_candidates}


def _validate_no_duplicate_stream_entries(snapshot: PassSnapshot) -> None:
    seen: set[tuple[str, str]] = set()
    for item in snapshot.channel_candidates:
        key = (item.channel, item.object_id)
        _require(key not in seen, f"duplicate channel stream entry {key}")
        seen.add(key)


def _validate_membership(snapshot: PassSnapshot) -> None:
    universe = _channel_universe(snapshot)
    stage_f = list(snapshot.stage_f_order)
    _require(len(set(stage_f)) == len(stage_f), "stage_f_order has duplicates")
    _require(set(stage_f) <= universe, "stage_f_order has objects outside the channel universe")
    stage_r = list(snapshot.stage_r_order)
    _require(
        len(set(stage_r)) == len(stage_r),
        "stage_r_order has duplicates",
    )
    _require(
        set(stage_r) <= set(stage_f),
        "stage_r_order IDs must belong to Stage-F candidate membership",
    )
    stage_m = list(snapshot.stage_m_order)
    _require(len(set(stage_m)) == len(stage_m), "stage_m_order has duplicates")
    expected_m = set(stage_r) | set(stage_f)
    _require(
        set(stage_m) == expected_m,
        "stage_m_order membership must equal deduplicated R+F membership",
    )
    stage_p = list(snapshot.stage_p_order)
    _require(len(set(stage_p)) == len(stage_p), "stage_p_order has duplicates")
    _require(
        set(stage_p) == set(stage_m),
        "stage_p_order membership must equal Stage-M membership",
    )
    selected = list(snapshot.stage_s_selected_object_ids)
    _require(
        len(set(selected)) == len(selected),
        "stage_s_selected_object_ids has duplicates",
    )
    _require(
        set(selected) <= universe,
        "Stage-S selected IDs must belong to the pass candidate universe",
    )
    _require(
        set(snapshot.stage_s_evidence_ids) <= universe,
        "stage_s_evidence_ids keys must belong to the pass candidate universe",
    )
    _require(
        set(snapshot.stage_f_scores) == set(stage_f),
        "stage_f_scores must cover exactly the stage_f_order membership",
    )


def _validate_channel_provenance(snapshot: PassSnapshot) -> None:
    for item in snapshot.channel_candidates:
        _require(bool(item.object_id), "channel candidate lacks object_id")
        _require(item.rank >= 1, f"channel candidate {item.object_id} rank must be >= 1")
        if item.channel in _REPRESENTATION_ONLY_CHANNELS:
            raise ValueError(
                f"{CONTRACT_ID}: channel '{item.channel}' is a computed query "
                "representation (shadow-capable), not an executed production "
                "channel; remove it from executed channel provenance"
            )
        _require(
            item.channel in EXECUTED_CHANNEL_VOCABULARY,
            f"unknown executed channel '{item.channel}'",
        )


def _validate_payloads(snapshot: PassSnapshot) -> None:
    for object_id in sorted(_channel_universe(snapshot)):
        payload = snapshot.payloads.get(object_id)
        _require(
            payload is not None,
            f"candidate {object_id} ({snapshot.pass_origin.value} pass) lacks payload provenance",
        )
        _require(bool(payload.source_id), f"payload {object_id} lacks source_id")
        _require(
            bool(payload.source_version_id),
            f"payload {object_id} lacks source_version_id",
        )
        _require(
            payload.text is not None or payload.payload_ref is not None,
            f"payload {object_id} needs text or a stable payload_ref",
        )


def _validate_completeness(snapshot: PassSnapshot) -> None:
    if snapshot.completeness is CompletenessState.COMPLETE:
        universe = _channel_universe(snapshot)
        _require(
            set(snapshot.stage_f_order) == universe,
            "COMPLETE requires Stage-F order to cover the full channel universe; "
            "declare PARTIAL instead of treating truncated diagnostics as complete",
        )
        _require(
            set(snapshot.stage_m_order) == universe
            and set(snapshot.stage_p_order) == universe,
            "COMPLETE requires Stage-M and Stage-P orders to cover the full universe",
        )
    else:
        _require(
            bool(snapshot.completeness_notes),
            "PARTIAL snapshots must state what state is truncated or absent",
        )


def _validate_pass_snapshot(snapshot: PassSnapshot) -> None:
    _require(
        snapshot.pass_origin in (PassOrigin.INITIAL, PassOrigin.TARGETED),
        "pass origin must be INITIAL or TARGETED",
    )
    _validate_channel_provenance(snapshot)
    _validate_no_duplicate_stream_entries(snapshot)
    _validate_membership(snapshot)
    _validate_payloads(snapshot)
    _validate_completeness(snapshot)


def _validate_cross_pass_consistency(
    initial: PassSnapshot, targeted: PassSnapshot
) -> None:
    _require(
        targeted.pass_origin is PassOrigin.TARGETED,
        "second snapshot must have TARGETED pass origin",
    )
    for object_id in sorted(
        _channel_universe(initial) & _channel_universe(targeted)
    ):
        initial_payload = initial.payloads[object_id]
        targeted_payload = targeted.payloads[object_id]
        _require(
            initial_payload.source_id == targeted_payload.source_id
            and initial_payload.source_version_id == targeted_payload.source_version_id,
            f"object {object_id} maps to conflicting source/version identity across "
            f"passes ({initial_payload.source_id}@{initial_payload.source_version_id} "
            f"vs {targeted_payload.source_id}@{targeted_payload.source_version_id}); "
            "different versions must not be silently combined",
        )


def _occurrence_for(
    snapshot: PassSnapshot, object_id: str
) -> CandidateOccurrence:
    channel_occurrences = tuple(
        item for item in snapshot.channel_candidates if item.object_id == object_id
    )
    stage_f_rank = (
        snapshot.stage_f_order.index(object_id) + 1
        if object_id in snapshot.stage_f_order
        else None
    )
    stage_m_rank = (
        snapshot.stage_m_order.index(object_id) + 1
        if object_id in snapshot.stage_m_order
        else None
    )
    stage_p_rank = (
        snapshot.stage_p_order.index(object_id) + 1
        if object_id in snapshot.stage_p_order
        else None
    )
    stage_r_rank = (
        snapshot.stage_r_order.index(object_id) + 1
        if object_id in snapshot.stage_r_order
        else None
    )
    selected = object_id in set(snapshot.stage_s_selected_object_ids)
    return CandidateOccurrence(
        pass_origin=snapshot.pass_origin,
        object_id=object_id,
        channel_occurrences=channel_occurrences,
        stage_f_rank=stage_f_rank,
        stage_f_score=(
            float(snapshot.stage_f_scores[object_id])
            if object_id in snapshot.stage_f_scores
            else None
        ),
        stage_r_rank=stage_r_rank,
        stage_m_rank=stage_m_rank,
        stage_p_rank=stage_p_rank,
        stage_s_selected=selected,
        evidence_id=snapshot.stage_s_evidence_ids.get(object_id),
        exclusion_receipts=tuple(
            receipt
            for receipt in snapshot.exclusions
            if receipt.get("object_id") == object_id
        ),
        backfill_admitted=any(
            admission.get("object_id") == object_id
            for admission in snapshot.backfill_admissions
        ),
    )


def build_global_candidate_pool(
    initial: PassSnapshot,
    targeted: PassSnapshot | None = None,
    targeted_trigger: TargetedTriggerContext | None = None,
) -> GlobalCandidatePool:
    """Consolidate pass snapshots into one object-level candidate pool.

    Performs contract validation and object-level consolidation only.  No
    global fusion, reranking, selection, weighting, or ranking is defined or
    applied.  Deterministic: identical snapshots produce an identical pool.
    """
    _validate_pass_snapshot(initial)
    if targeted is None:
        _require(
            targeted_trigger is None,
            "targeted_trigger requires a targeted pass snapshot",
        )
    else:
        _require(
            targeted_trigger is not None,
            "a targeted pass snapshot requires its TargetedTriggerContext",
        )
        _validate_pass_snapshot(targeted)
        _validate_cross_pass_consistency(initial, targeted)

    universe = _channel_universe(initial) | (
        _channel_universe(targeted) if targeted else set()
    )
    candidates: list[GlobalCandidate] = []
    for object_id in sorted(universe):
        in_initial = object_id in _channel_universe(initial)
        in_targeted = bool(targeted and object_id in _channel_universe(targeted))
        origin = (
            CandidateOrigin.BOTH
            if in_initial and in_targeted
            else CandidateOrigin.INITIAL_ONLY
            if in_initial
            else CandidateOrigin.TARGETED_ONLY
        )
        # Canonical payload: identical by validation for BOTH-origin objects;
        # prefer the INITIAL occurrence deterministically.
        payload = (
            initial.payloads[object_id]
            if in_initial
            else targeted.payloads[object_id]  # type: ignore[union-attr]
        )
        candidates.append(
            GlobalCandidate(
                object_id=object_id,
                origin=origin,
                payload=payload,
                initial_occurrence=(
                    _occurrence_for(initial, object_id) if in_initial else None
                ),
                targeted_occurrence=(
                    _occurrence_for(targeted, object_id)
                    if in_targeted and targeted
                    else None
                ),
            )
        )
    counts = {
        "total": len(candidates),
        "initial_only": sum(
            1 for c in candidates if c.origin is CandidateOrigin.INITIAL_ONLY
        ),
        "targeted_only": sum(
            1 for c in candidates if c.origin is CandidateOrigin.TARGETED_ONLY
        ),
        "both": sum(1 for c in candidates if c.origin is CandidateOrigin.BOTH),
    }
    return GlobalCandidatePool(
        contract_id=CONTRACT_ID,
        initial_snapshot=initial,
        targeted_snapshot=targeted,
        targeted_trigger=targeted_trigger,
        candidates=tuple(candidates),
        counts=counts,
    )


def serialize_pool(pool: GlobalCandidatePool) -> str:
    """Deterministic JSON serialization (sorted keys; no relevance claim)."""
    return json.dumps(
        pool.as_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


__all__ = [
    "CONTRACT_ID",
    "GLOBAL_RANKING_DEFINED",
    "GLOBAL_FUSION_IMPLEMENTED",
    "GLOBAL_RERANKER_IMPLEMENTED",
    "GLOBAL_SELECTOR_IMPLEMENTED",
    "SERIALIZATION_ORDER",
    "SERIALIZATION_ORDER_SEMANTICS",
    "EXECUTED_CHANNEL_VOCABULARY",
    "PassOrigin",
    "CandidateOrigin",
    "CompletenessState",
    "ChannelCandidate",
    "PayloadProvenance",
    "CandidateOccurrence",
    "PassSnapshot",
    "TargetedTriggerContext",
    "GlobalCandidate",
    "GlobalCandidatePool",
    "build_global_candidate_pool",
    "serialize_pool",
    "asdict",
]
