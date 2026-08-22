"""Deterministic frozen-candidate fusion replay for C6 (A1).

Pure evaluation-only module: replays weighted reciprocal-rank fusion over
frozen channel candidate streams without any retrieval, model, storage, or
Qdrant call.  Production retrieval must not import this module.  The
``CURRENT`` policy reproduces the exact production fusion semantics
(inspected in ``Retriever.retrieve``): per-channel iteration in production
dict-insertion order, ``weight / (60 + rank)`` with 1-based ranks, stable
sort over the insertion-ordered score map, ``object_id`` candidate identity.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# C6 authoritative channel names.  Historical traces recorded the production
# dense channel as "dense"; the C6 name is "raw_dense".
CHANNELS = (
    "exact",
    "raw_dense",
    "semantic_dense",
    "sparse",
    "paper",
    "workflow",
    "graph",
)
TRACE_CHANNEL_ALIASES = {"dense": "raw_dense"}

# Production dict-insertion order of ``rankings`` in Retriever.retrieve.
PRODUCTION_CHANNEL_ORDER = (
    "exact",
    "raw_dense",
    "sparse",
    "paper",
    "workflow",
    "graph",
)

RRF_K = 60
CURRENT_WEIGHTS = {
    "exact": 2.0,
    "raw_dense": 1.0,
    "sparse": 1.0,
    "paper": 1.15,
    "workflow": 1.2,
    "graph": 0.8,
}
CURRENT_POLICY_ID = "c6.current.v1"

PRESENT_NONEMPTY = "PRESENT_NONEMPTY"
PRESENT_EMPTY = "PRESENT_EMPTY"
SKIPPED_BY_PLAN = "SKIPPED_BY_PLAN"
MISSING_NOT_CAPTURED = "MISSING_NOT_CAPTURED"
INVALID_OR_UNFAITHFUL = "INVALID_OR_UNFAITHFUL"

ELIGIBLE_STATES = frozenset({PRESENT_NONEMPTY, PRESENT_EMPTY, SKIPPED_BY_PLAN})
FUSING_STATES = frozenset({PRESENT_NONEMPTY, PRESENT_EMPTY})
CORE_REQUIRED_CHANNELS = ("exact", "raw_dense", "sparse", "paper", "workflow", "graph")


@dataclass(frozen=True)
class FrozenChannelCandidate:
    """One frozen candidate with its historical rank and optional metadata."""

    object_id: str
    rank: int
    original_score: float | None = None
    source_id: str | None = None
    source_version_id: str | None = None
    locator: Mapping[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "rank": self.rank,
            "original_score": self.original_score,
            "source_id": self.source_id,
            "source_version_id": self.source_version_id,
            "locator": dict(self.locator) if self.locator else None,
        }


@dataclass(frozen=True)
class FrozenChannelStream:
    """One channel's frozen availability state and candidate stream."""

    channel: str
    availability_state: str
    candidates: tuple[FrozenChannelCandidate, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "availability_state": self.availability_state,
            "candidates": [candidate.as_dict() for candidate in self.candidates],
        }


@dataclass
class FusionReplayCase:
    """One replayable case with its frozen channel streams."""

    case_id: str
    question: str
    intent: str
    plan_provenance: Mapping[str, Any] = field(default_factory=dict)
    channels: dict[str, FrozenChannelStream] = field(default_factory=dict)

    @property
    def core_replay_eligible(self) -> bool:
        return all(
            self.channels.get(channel).availability_state in ELIGIBLE_STATES
            if channel in self.channels
            else False
            for channel in CORE_REQUIRED_CHANNELS
        )

    @property
    def semantic_stream_available(self) -> bool:
        stream = self.channels.get("semantic_dense")
        return stream is not None and stream.availability_state in ELIGIBLE_STATES

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "question": self.question,
            "intent": self.intent,
            "plan_provenance": dict(self.plan_provenance),
            "channels": {
                channel: stream.as_dict() for channel, stream in self.channels.items()
            },
        }


@dataclass(frozen=True)
class ChannelContribution:
    """One channel's weighted-RRF contribution to a fused candidate."""

    channel: str
    rank: int
    weight: float
    contribution: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "rank": self.rank,
            "weight": self.weight,
            "contribution": self.contribution,
        }


@dataclass(frozen=True)
class FusedCandidate:
    """One fused candidate with the full contribution audit."""

    object_id: str
    fused_rank: int
    fused_score: float
    contributions: tuple[ChannelContribution, ...]
    unique_channel: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "fused_rank": self.fused_rank,
            "fused_score": self.fused_score,
            "contributions": [item.as_dict() for item in self.contributions],
            "channel_count": len(self.contributions),
            "unique_channel": self.unique_channel,
        }


@dataclass(frozen=True)
class FusionReceipt:
    """Auditable result of replaying one policy on one case."""

    policy_id: str
    policy_version: str
    case_id: str
    enabled_channels: tuple[str, ...]
    fused: tuple[FusedCandidate, ...] = ()
    expansion_pool: tuple[FrozenChannelCandidate, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "case_id": self.case_id,
            "enabled_channels": list(self.enabled_channels),
            "fused": [candidate.as_dict() for candidate in self.fused],
            "expansion_pool": [
                {
                    "object_id": candidate.object_id,
                    "semantic_rank": candidate.rank,
                    "source_id": candidate.source_id,
                    "source_version_id": candidate.source_version_id,
                }
                for candidate in self.expansion_pool
            ],
        }


@dataclass(frozen=True)
class FusionPolicy:
    """One preregistered fusion policy.

    ``mode="weighted_rrf"`` fuses the enabled channels with their weights.
    ``mode="expansion_only"`` keeps the ``base`` policy's scored fusion
    unchanged and appends only unique semantic candidates to an expansion
    pool in semantic rank order.
    """

    policy_id: str
    policy_version: str
    mode: str = "weighted_rrf"
    weights: Mapping[str, float] = field(default_factory=lambda: dict(CURRENT_WEIGHTS))
    enabled_channels: Sequence[str] = PRODUCTION_CHANNEL_ORDER
    base_policy_id: str | None = None

    def apply(self, case: FusionReplayCase) -> FusionReceipt:
        if self.mode == "expansion_only":
            return self._apply_expansion_only(case)
        return self._apply_weighted(case)

    def _apply_weighted(self, case: FusionReplayCase) -> FusionReceipt:
        scores: dict[str, float] = {}
        contributions: dict[str, list[ChannelContribution]] = {}
        enabled: list[str] = []
        for channel in PRODUCTION_CHANNEL_ORDER + ("semantic_dense",):
            if channel not in self.enabled_channels:
                continue
            stream = case.channels.get(channel)
            if stream is None or stream.availability_state not in FUSING_STATES:
                continue
            enabled.append(channel)
            weight = float(self.weights[channel])
            for candidate in stream.candidates:
                contribution = weight / (RRF_K + candidate.rank)
                scores[candidate.object_id] = (
                    scores.get(candidate.object_id, 0.0) + contribution
                )
                contributions.setdefault(candidate.object_id, []).append(
                    ChannelContribution(
                        channel=channel,
                        rank=candidate.rank,
                        weight=weight,
                        contribution=contribution,
                    )
                )
        fused_order = sorted(scores, key=scores.get, reverse=True)
        fused = tuple(
            FusedCandidate(
                object_id=object_id,
                fused_rank=rank,
                fused_score=scores[object_id],
                contributions=tuple(contributions.get(object_id, ())),
                unique_channel=(
                    contributions[object_id][0].channel
                    if len(contributions.get(object_id, ())) == 1
                    else None
                ),
            )
            for rank, object_id in enumerate(fused_order, 1)
        )
        return FusionReceipt(
            policy_id=self.policy_id,
            policy_version=self.policy_version,
            case_id=case.case_id,
            enabled_channels=tuple(enabled),
            fused=fused,
        )

    def _apply_expansion_only(self, case: FusionReplayCase) -> FusionReceipt:
        base_receipt = self._apply_weighted(case)
        base_ids = {candidate.object_id for candidate in base_receipt.fused}
        semantic = case.channels.get("semantic_dense")
        expansion: list[FrozenChannelCandidate] = []
        if semantic is not None and semantic.availability_state in FUSING_STATES:
            seen: set[str] = set()
            for candidate in sorted(semantic.candidates, key=lambda item: item.rank):
                if candidate.object_id in base_ids or candidate.object_id in seen:
                    continue
                seen.add(candidate.object_id)
                expansion.append(candidate)
        return FusionReceipt(
            policy_id=self.policy_id,
            policy_version=self.policy_version,
            case_id=case.case_id,
            enabled_channels=base_receipt.enabled_channels,
            fused=base_receipt.fused,
            expansion_pool=tuple(expansion),
        )


def current_policy() -> FusionPolicy:
    """P0 — exact current production fusion (semantic_dense disabled)."""
    return FusionPolicy(
        policy_id=CURRENT_POLICY_ID,
        policy_version="v1",
        weights=dict(CURRENT_WEIGHTS),
        enabled_channels=PRODUCTION_CHANNEL_ORDER,
    )


def preregistered_policies() -> dict[str, FusionPolicy]:
    """The frozen C6-A2 policy set P0-P5 (defined before any A2 outcome)."""

    policies: dict[str, FusionPolicy] = {}

    policies["P0_CURRENT"] = current_policy()

    raw_centered = dict(CURRENT_WEIGHTS)
    raw_centered["raw_dense"] = CURRENT_WEIGHTS["raw_dense"] * 1.5
    policies["P1_RAW_DENSE_CENTERED"] = FusionPolicy(
        policy_id="c6.raw_dense_centered.v1",
        policy_version="v1",
        weights=raw_centered,
        enabled_channels=PRODUCTION_CHANNEL_ORDER,
    )

    exact_heavy = dict(CURRENT_WEIGHTS)
    exact_heavy["exact"] = CURRENT_WEIGHTS["exact"] * 1.5
    policies["P2_EXACT_HEAVY"] = FusionPolicy(
        policy_id="c6.exact_heavy.v1",
        policy_version="v1",
        weights=exact_heavy,
        enabled_channels=PRODUCTION_CHANNEL_ORDER,
    )

    sparse_heavy = dict(CURRENT_WEIGHTS)
    sparse_heavy["sparse"] = CURRENT_WEIGHTS["sparse"] * 1.5
    policies["P3_SPARSE_HEAVY"] = FusionPolicy(
        policy_id="c6.sparse_heavy.v1",
        policy_version="v1",
        weights=sparse_heavy,
        enabled_channels=PRODUCTION_CHANNEL_ORDER,
    )

    semantic_aux = dict(CURRENT_WEIGHTS)
    semantic_aux["raw_dense"] = CURRENT_WEIGHTS["raw_dense"] * 0.75
    semantic_aux["semantic_dense"] = CURRENT_WEIGHTS["raw_dense"] * 0.25
    policies["P4_SEMANTIC_AUXILIARY_25"] = FusionPolicy(
        policy_id="c6.semantic_aux25.v1",
        policy_version="v1",
        weights=semantic_aux,
        enabled_channels=(*PRODUCTION_CHANNEL_ORDER, "semantic_dense"),
    )

    policies["P5_SEMANTIC_EXPANSION_ONLY"] = FusionPolicy(
        policy_id="c6.semantic_expansion_only.v1",
        policy_version="v1",
        mode="expansion_only",
        weights=dict(CURRENT_WEIGHTS),
        enabled_channels=PRODUCTION_CHANNEL_ORDER,
        base_policy_id=CURRENT_POLICY_ID,
    )
    return policies


def replay_case_from_mapping(payload: Mapping[str, Any]) -> FusionReplayCase:
    """Build a FusionReplayCase from the normalized JSONL record shape."""

    channels: dict[str, FrozenChannelStream] = {}
    for channel, stream in (payload.get("channels") or {}).items():
        normalized = TRACE_CHANNEL_ALIASES.get(channel, channel)
        candidates = tuple(
            FrozenChannelCandidate(
                object_id=str(item["object_id"]),
                rank=int(item["rank"]),
                original_score=item.get("original_score"),
                source_id=item.get("source_id"),
                source_version_id=item.get("source_version_id"),
                locator=item.get("locator"),
            )
            for item in stream.get("candidates", [])
        )
        channels[normalized] = FrozenChannelStream(
            channel=normalized,
            availability_state=str(stream["availability_state"]),
            candidates=candidates,
        )
    return FusionReplayCase(
        case_id=str(payload["case_id"]),
        question=str(payload.get("question", "")),
        intent=str(payload.get("intent", "")),
        plan_provenance=dict(payload.get("plan_provenance") or {}),
        channels=channels,
    )


def load_replay_cases(source: str | Path) -> list[FusionReplayCase]:
    """Load normalized frozen replay cases from a JSONL path."""
    path = Path(source)
    cases = [
        replay_case_from_mapping(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return cases


def structural_parity(
    receipt: FusionReceipt, historical_order: Sequence[str], historical_scores: Mapping[str, float] | None = None
) -> dict[str, Any]:
    """Structural-only comparison against a recorded fused order."""
    replayed = [candidate.object_id for candidate in receipt.fused]
    limit = min(len(replayed), len(historical_order))
    order_match = replayed[:limit] == list(historical_order)[:limit]
    score_match: bool | None = None
    if historical_scores:
        score_map = {candidate.object_id: candidate.fused_score for candidate in receipt.fused}
        score_match = all(
            abs(score_map.get(object_id, -1.0) - float(score)) < 1e-9
            for object_id, score in historical_scores.items()
            if object_id in score_map
        )
    return {
        "case_id": receipt.case_id,
        "order_match": order_match,
        "score_match": score_match,
        "compared_count": limit,
    }


__all__ = [
    "CHANNELS",
    "PRODUCTION_CHANNEL_ORDER",
    "RRF_K",
    "CURRENT_WEIGHTS",
    "CURRENT_POLICY_ID",
    "PRESENT_NONEMPTY",
    "PRESENT_EMPTY",
    "SKIPPED_BY_PLAN",
    "MISSING_NOT_CAPTURED",
    "INVALID_OR_UNFAITHFUL",
    "ELIGIBLE_STATES",
    "FUSING_STATES",
    "CORE_REQUIRED_CHANNELS",
    "FrozenChannelCandidate",
    "FrozenChannelStream",
    "FusionReplayCase",
    "ChannelContribution",
    "FusedCandidate",
    "FusionReceipt",
    "FusionPolicy",
    "current_policy",
    "preregistered_policies",
    "replay_case_from_mapping",
    "load_replay_cases",
    "structural_parity",
]
