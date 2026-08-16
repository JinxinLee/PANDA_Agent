"""Stable, reusable retrieval-trace artifacts for evaluation runs."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import Field

from panda_agent.models import SourceLocator, StrictModel


class TraceCandidate(StrictModel):
    object_id: str
    source_id: str | None = None
    source_version_id: str | None = None
    object_type: str | None = None
    locator: SourceLocator = Field(default_factory=SourceLocator)
    rank: int = Field(ge=1)
    score: float | None = None
    channels: list[str] = Field(default_factory=list)


class RetrievalTrace(StrictModel):
    schema_version: str = "1.0"
    question_id: str
    run_id: str
    implementation_identity: dict[str, Any]
    raw_question: str
    retrieval_plan: dict[str, Any]
    original_retrieval_query: str
    dense_query_text: str
    sparse_query_text: str
    query_construction: str = "raw_question"
    resolved_concepts: list[str] = Field(default_factory=list)
    resolved_symbols: list[str] = Field(default_factory=list)
    channel_candidates: dict[str, list[TraceCandidate]] = Field(default_factory=dict)
    fused_candidates: list[TraceCandidate] = Field(default_factory=list)
    reranked_candidates: list[TraceCandidate] = Field(default_factory=list)
    final_evidence: list[dict[str, Any]] = Field(default_factory=list)
    excluded_candidates: list[dict[str, Any]] = Field(default_factory=list)
    soft_budget_admissions: list[dict[str, Any]] = Field(default_factory=list)


def _identity_from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "repository_identity",
        "prompt_version",
        "embedding_model_id",
        "embedding_dimensions",
        "index_identity",
        "generation_model_id",
        "retrieval_policy_hash",
        "query_expansion_hash",
        "gold_dataset_hash",
        "mode",
    )
    return {key: manifest.get(key) for key in keys}


def _candidate(
    object_id: str,
    rank: int,
    object_lookup: dict[str, dict[str, Any]],
    *,
    score: float | None = None,
    channels: list[str] | None = None,
) -> TraceCandidate:
    payload = object_lookup.get(object_id) or {}
    return TraceCandidate(
        object_id=object_id,
        source_id=payload.get("source_id"),
        source_version_id=payload.get("source_version_id"),
        object_type=payload.get("object_type"),
        locator=SourceLocator.model_validate(payload.get("locator") or {}),
        rank=rank,
        score=score,
        channels=list(channels or []),
    )


def build_retrieval_trace(
    *,
    question_id: str,
    run_id: str,
    question: str,
    diagnostics: dict[str, Any],
    manifest: dict[str, Any],
    object_lookup: dict[str, dict[str, Any]],
    result: dict[str, Any] | None = None,
) -> RetrievalTrace:
    """Build a faithful trace without changing or rerunning retrieval."""
    plan = dict(diagnostics.get("plan") or {})
    rankings = diagnostics.get("rankings") or {}
    channel_candidates = {
        channel: [
            _candidate(object_id, rank, object_lookup, channels=[channel])
            for rank, object_id in enumerate(object_ids, 1)
        ]
        for channel, object_ids in sorted(rankings.items())
    }
    channels_by_object: dict[str, list[str]] = {}
    for channel, candidates in channel_candidates.items():
        for candidate in candidates:
            channels_by_object.setdefault(candidate.object_id, []).append(channel)
    fusion_scores = diagnostics.get("fusion_scores") or {}
    fused_candidates = [
        _candidate(
            object_id,
            rank,
            object_lookup,
            score=float(score),
            channels=channels_by_object.get(object_id, []),
        )
        for rank, (object_id, score) in enumerate(fusion_scores.items(), 1)
    ]
    reranked_candidates = [
        _candidate(
            object_id,
            rank,
            object_lookup,
            score=(float(fusion_scores[object_id]) if object_id in fusion_scores else None),
            channels=channels_by_object.get(object_id, []),
        )
        for rank, object_id in enumerate(diagnostics.get("reranked_object_ids") or [], 1)
    ]
    final_evidence = list(diagnostics.get("selected_evidence") or [])
    if not final_evidence and result:
        final_evidence = list(result.get("evidence") or [])
    return RetrievalTrace(
        question_id=question_id,
        run_id=run_id,
        implementation_identity=_identity_from_manifest(manifest),
        raw_question=question,
        retrieval_plan=plan,
        original_retrieval_query=question,
        dense_query_text=question,
        sparse_query_text=question,
        resolved_concepts=list(plan.get("concepts") or []),
        resolved_symbols=list(plan.get("symbols") or []),
        channel_candidates=channel_candidates,
        fused_candidates=fused_candidates,
        reranked_candidates=reranked_candidates,
        final_evidence=final_evidence,
        excluded_candidates=list(diagnostics.get("excluded") or []),
        soft_budget_admissions=list(diagnostics.get("soft_budget_admissions") or []),
    )


def write_retrieval_trace(run_dir: Path, trace: RetrievalTrace) -> Path:
    """Persist an atomic per-question trace plus a convenient JSONL stream."""
    traces_dir = run_dir / "traces"
    traces_dir.mkdir(exist_ok=True)
    record = trace.model_dump(mode="json")
    text = json.dumps(record, ensure_ascii=False, sort_keys=True)
    path = traces_dir / f"{trace.question_id}.json"
    temporary = traces_dir / f".{trace.question_id}.json.tmp"
    temporary.write_text(text + "\n", encoding="utf-8")
    os.replace(temporary, path)
    stream_path = run_dir / "retrieval_traces.jsonl"
    with stream_path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(text + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return path


def load_retrieval_trace(path: Path) -> RetrievalTrace:
    return RetrievalTrace.model_validate_json(path.read_text(encoding="utf-8"))


def load_retrieval_traces(run_dir: Path) -> list[RetrievalTrace]:
    """Load frozen traces without invoking retrieval, QA, or Vertex."""
    traces_dir = run_dir / "traces"
    if traces_dir.is_dir():
        return [load_retrieval_trace(path) for path in sorted(traces_dir.glob("*.json"))]
    stream_path = run_dir / "retrieval_traces.jsonl"
    if not stream_path.is_file():
        return []
    return [
        RetrievalTrace.model_validate_json(line)
        for line in stream_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
