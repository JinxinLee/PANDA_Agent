"""Layer-level sparse retrieval comparison against a frozen baseline.

This module deliberately stops at the sparse Qdrant channel.  It reuses the
frozen retrieval traces for the old ranking and only constructs a local sparse
encoder plus one sparse Qdrant query per trace for the new ranking.  No
``Retriever`` or Vertex client is constructed here.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping, Sequence

from qdrant_client import models

from panda_agent.evaluation import (
    GoldDataset,
    GoldQuestion,
    classify_identifier_mention,
    evidence_group_recall,
    load_gold_dataset,
)
from panda_agent.evaluation_runner import load_object_lookup
from panda_agent.retrieval_trace import RetrievalTrace
from panda_agent.sparse import SparseEncoderReceipt, create_sparse_encoder
from panda_agent.storage import Storage, StorageSettings


BASELINE_MANIFEST_RELATIVE = Path(
    "evaluation/baselines/manifests/english_gold_stratified_bootstrap_v1.json"
)
GOLD_DATASET_RELATIVE = Path("evaluation/benchmarks/v2_6/gold_questions.yaml")
TRACE_FILENAME = "benchmark_retrieval_traces.jsonl"
RECORD_FILENAME = "benchmark_retrieval_baseline.jsonl"
QUERY_LIMIT = 20

_IDENTIFIER_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_:./*-]+")
IDENTIFIER_HEAVY_RULE = (
    "identifier-heavy iff Gold.required_identifiers is non-empty or a token from "
    "r'[A-Za-z_][A-Za-z0-9_:./*-]+' classifies as code_symbol/path via "
    "evaluation.classify_identifier_mention; this rule is independent of case IDs"
)
METRIC_NAMES = ("first_relevant_rank", "recall_at_5", "recall_at_10", "mrr")


def _as_path(project_root: str | Path, value: str | Path) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (Path(project_root).resolve() / path).resolve()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {path}:{line_number}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"JSONL record at {path}:{line_number} must be an object")
        rows.append(item)
    return rows


def _load_traces(path: Path) -> list[RetrievalTrace]:
    if not path.is_file():
        raise FileNotFoundError(f"frozen retrieval traces not found: {path}")
    traces: list[RetrievalTrace] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            traces.append(RetrievalTrace.model_validate_json(line))
        except ValueError as exc:
            raise ValueError(f"invalid retrieval trace at {path}:{line_number}") from exc
    return traces


def _context_sources(project_root: Path) -> list[str]:
    path = project_root / "data" / "manifests" / "source_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        str(item["doc_id"])
        for key in ("papers", "web_documents")
        for item in payload.get(key, [])
        if item.get("doc_id")
    ]


def build_frozen_query_filter(
    retrieval_plan: Mapping[str, Any], context_sources: Sequence[str]
) -> models.Filter | None:
    """Reproduce ``Retriever._vector``'s repository/version filter exactly."""
    repositories = [str(value) for value in retrieval_plan.get("target_repositories", [])]
    if not repositories:
        return None
    versions = retrieval_plan.get("resolved_versions") or {}
    scopes: list[Any] = []
    for repository in repositories:
        if repository not in versions:
            raise ValueError(
                f"frozen retrieval plan has no resolved version for target repository: {repository}"
            )
        scopes.append(
            models.Filter(
                must=[
                    models.FieldCondition(
                        key="source_id", match=models.MatchValue(value=repository)
                    ),
                    models.FieldCondition(
                        key="source_version_id",
                        match=models.MatchValue(value=f"{repository}@{versions[repository]}"),
                    ),
                ]
            )
        )
    scopes.append(
        models.FieldCondition(
            key="source_id",
            match=models.MatchAny(any=[*context_sources, "curated_panda_domain"]),
        )
    )
    return models.Filter(should=scopes)


def _vector_values(value: Any) -> list[Any]:
    values = value.tolist() if hasattr(value, "tolist") else value
    return list(values)


def sparse_query_vector(embedder: Any, text: str) -> models.SparseVector:
    """Encode one query with the supplied local sparse encoder."""
    encoded = next(iter(embedder.query_embed(text)))
    return models.SparseVector(
        indices=[int(value) for value in _vector_values(encoded.indices)],
        values=[float(value) for value in _vector_values(encoded.values)],
    )


def _hit_object_id(hit: Any) -> str | None:
    payload = getattr(hit, "payload", None)
    if isinstance(payload, Mapping):
        object_id = payload.get("object_id")
        if object_id:
            return str(object_id)
    object_id = getattr(hit, "id", None)
    return str(object_id) if object_id else None


def query_sparse_ranking(
    qdrant: Any,
    *,
    collection_name: str,
    vector: models.SparseVector,
    vector_name: str,
    query_filter: models.Filter | None,
    limit: int = QUERY_LIMIT,
) -> list[str]:
    """Run one sparse-only Qdrant query and return unique payload IDs."""
    result = qdrant.query_points(
        collection_name=collection_name,
        query=vector,
        using=vector_name,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    )
    points = getattr(result, "points", result or [])
    ranking: list[str] = []
    seen: set[str] = set()
    for hit in points:
        object_id = _hit_object_id(hit)
        if object_id and object_id not in seen:
            ranking.append(object_id)
            seen.add(object_id)
        if len(ranking) >= limit:
            break
    return ranking


def _trace_sparse_ids(trace: RetrievalTrace) -> list[str]:
    candidates = sorted(trace.channel_candidates.get("sparse", []), key=lambda item: item.rank)
    ranking: list[str] = []
    seen: set[str] = set()
    for candidate in candidates[:QUERY_LIMIT]:
        if candidate.object_id not in seen:
            ranking.append(candidate.object_id)
            seen.add(candidate.object_id)
    return ranking


def rank_metrics(
    case: GoldQuestion,
    ranked_object_ids: Sequence[str],
    object_lookup: dict[str, dict[str, Any]],
) -> dict[str, float | int | None]:
    """Compute sparse first-hit rank, Recall@5/@10 and MRR via Gold groups."""
    ranking = list(dict.fromkeys(str(value) for value in ranked_object_ids))[:QUERY_LIMIT]

    def recall(limit: int) -> float:
        return float(
            evidence_group_recall(case.required_evidence_groups, ranking[:limit], object_lookup)
        )

    first_rank: int | None = None
    for rank in range(1, len(ranking) + 1):
        if evidence_group_recall(case.required_evidence_groups, ranking[:rank], object_lookup) > 0:
            first_rank = rank
            break
    return {
        "first_relevant_rank": first_rank,
        "recall_at_5": recall(5),
        "recall_at_10": recall(10),
        "mrr": (1.0 / first_rank) if first_rank is not None else 0.0,
    }


def identifier_like_tokens(query: str) -> list[str]:
    return sorted(
        {
            token
            for token in _IDENTIFIER_TOKEN_RE.findall(query)
            if classify_identifier_mention(token)[0] in {"code_symbol", "path"}
        }
    )


def _required_identifier_texts(case: GoldQuestion) -> list[str]:
    values: list[str] = []
    for item in case.required_identifiers:
        text = getattr(item, "text", None)
        if text is None and isinstance(item, Mapping):
            text = item.get("text")
        if text:
            values.append(str(text))
    return sorted(set(values))


def identifier_heavy(case: GoldQuestion) -> tuple[bool, list[str]]:
    tokens = identifier_like_tokens(case.query)
    return bool(_required_identifier_texts(case) or tokens), tokens


def _status_text(value: Any) -> str:
    return str(getattr(value, "value", value))


def _applicability(case: GoldQuestion, record: Mapping[str, Any]) -> tuple[bool, str]:
    expected = _status_text(case.expected_status)
    frozen_status = ((record.get("result") or {}).get("status"))
    metric_applicability = (record.get("metrics") or {}).get("metric_applicability") or {}
    if "gold_recall_at_5" in metric_applicability:
        applicable = bool(metric_applicability["gold_recall_at_5"])
        return applicable, (
            "baseline metric_applicability.gold_recall_at_5="
            f"{str(applicable).lower()}"
        )
    # Match the evaluator's fallback semantics when old records lack the
    # applicability map: a refusal is excluded only when the frozen result
    # agrees with its non-answered expected status.
    excluded = expected != "answered" and frozen_status == expected
    if excluded:
        return False, f"expected_status={expected}; frozen_result_status={frozen_status}"
    return True, f"expected_status={expected}; frozen_result_status={frozen_status}"


def _mean_metric(cases: Sequence[dict[str, Any]], source: str, metric: str) -> float | None:
    values = [
        float(item[source][metric])
        for item in cases
        if item["applicable"] and item[source][metric] is not None
    ]
    return fmean(values) if values else None


def _aggregate(cases: Sequence[dict[str, Any]], source: str) -> dict[str, Any]:
    applicable = sum(1 for item in cases if item["applicable"])
    return {
        "case_count": len(cases),
        "applicable_case_count": applicable,
        **{metric: _mean_metric(cases, source, metric) for metric in METRIC_NAMES},
    }


def _delta(new: float | int | None, old: float | int | None) -> float | int | None:
    if new is None or old is None:
        return None
    return new - old


def _outcome(old_rank: int | None, new_rank: int | None) -> str:
    if old_rank is None and new_rank is None:
        return "unchanged"
    if old_rank is None:
        return "improved"
    if new_rank is None:
        return "regressed"
    if new_rank < old_rank:
        return "improved"
    if new_rank > old_rank:
        return "regressed"
    return "unchanged"


def _metric_outcomes(cases: Sequence[dict[str, Any]], metric: str) -> dict[str, int]:
    counts = {key: 0 for key in ("improved", "unchanged", "regressed")}
    for item in cases:
        if not item["applicable"]:
            continue
        old = item["old"][metric]
        new = item["new"][metric]
        if float(new) > float(old):
            key = "improved"
        elif float(new) < float(old):
            key = "regressed"
        else:
            key = "unchanged"
        counts[key] += 1
    return counts


def evaluate_sparse(
    project_root: str | Path,
    baseline_dir: str | Path,
    *,
    qdrant: Any | None = None,
    embedder: Any | None = None,
    sparse_receipt: SparseEncoderReceipt | None = None,
    collection_name: str | None = None,
    context_sources: Sequence[str] | None = None,
    gold_dataset: GoldDataset | None = None,
    object_lookup: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compare frozen sparse rankings with fresh local sparse-only queries."""
    root = Path(project_root).resolve()
    baseline_path = _as_path(root, baseline_dir)
    manifest_path = root / BASELINE_MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_ids = [str(value) for value in manifest.get("retrieval", {}).get("case_ids", [])]
    if not expected_ids:
        raise ValueError("baseline manifest has no retrieval case IDs")

    traces = _load_traces(baseline_path / TRACE_FILENAME)
    trace_ids = [trace.question_id for trace in traces]
    if trace_ids != expected_ids:
        raise ValueError(
            "frozen retrieval trace IDs do not exactly match baseline manifest: "
            f"expected={expected_ids}, actual={trace_ids}"
        )

    dataset_path = root / GOLD_DATASET_RELATIVE
    dataset = gold_dataset or load_gold_dataset(dataset_path)
    questions = {case.id: case for case in dataset.questions}
    missing_questions = sorted(set(expected_ids) - set(questions))
    if missing_questions:
        raise ValueError(f"canonical Gold v2_6 is missing retrieval cases: {missing_questions}")
    lookup = object_lookup if object_lookup is not None else load_object_lookup(root)

    record_rows = _load_jsonl(baseline_path / RECORD_FILENAME)
    record_ids = [str(item.get("id")) for item in record_rows]
    if record_ids != expected_ids:
        raise ValueError(
            "baseline retrieval record IDs do not exactly match manifest/traces: "
            f"expected={expected_ids}, actual={record_ids}"
        )
    records = {str(item["id"]): item for item in record_rows}
    if qdrant is None:
        storage = Storage()
        qdrant = storage.qdrant
        collection_name = collection_name or storage.settings.collection_name
    elif collection_name is None:
        collection_name = StorageSettings.from_env().collection_name
    if embedder is None:
        embedder, sparse_receipt = create_sparse_encoder(root)
    if sparse_receipt is None:
        raise ValueError("an injected sparse evaluator embedder requires its SparseEncoderReceipt")
    sources = list(context_sources) if context_sources is not None else _context_sources(root)

    cases: list[dict[str, Any]] = []
    for trace in traces:
        case = questions[trace.question_id]
        record = records[trace.question_id]
        frozen_status = ((record.get("result") or {}).get("status"))
        applicable, reason = _applicability(case, record)
        old_ids = _trace_sparse_ids(trace)
        query_filter = build_frozen_query_filter(trace.retrieval_plan, sources)
        vector = sparse_query_vector(embedder, trace.sparse_query_text)
        new_ids = query_sparse_ranking(
            qdrant,
            collection_name=collection_name,
            vector=vector,
            vector_name=sparse_receipt.vector_name,
            query_filter=query_filter,
            limit=QUERY_LIMIT,
        )
        old_metrics = rank_metrics(case, old_ids, lookup)
        new_metrics = rank_metrics(case, new_ids, lookup)
        heavy, query_tokens = identifier_heavy(case)
        case_delta = {metric: _delta(new_metrics[metric], old_metrics[metric]) for metric in METRIC_NAMES}
        cases.append(
            {
                "question_id": trace.question_id,
                "expected_status": _status_text(case.expected_status),
                "frozen_result_status": frozen_status,
                "applicable": applicable,
                "applicability_reason": reason,
                "identifier_heavy": heavy,
                "identifier_like_tokens": query_tokens,
                "required_identifiers": _required_identifier_texts(case),
                "sparse_query_text": trace.sparse_query_text,
                "retrieval_plan": trace.retrieval_plan,
                "query_executed": True,
                "old_ranking": old_ids,
                "new_ranking": new_ids,
                "old": old_metrics,
                "new": new_metrics,
                "delta": case_delta,
                "outcome": _outcome(
                    old_metrics["first_relevant_rank"], new_metrics["first_relevant_rank"]
                ),
            }
        )

    outcome_counts = {key: sum(item["outcome"] == key for item in cases if item["applicable"]) for key in ("improved", "unchanged", "regressed")}
    old_summary = _aggregate(cases, "old")
    new_summary = _aggregate(cases, "new")
    delta_summary = {
        metric: _delta(new_summary[metric], old_summary[metric]) for metric in METRIC_NAMES
    }
    heavy_cases = [item for item in cases if item["identifier_heavy"]]
    heavy_ids = [item["question_id"] for item in heavy_cases]
    heavy_old = _aggregate(heavy_cases, "old")
    heavy_new = _aggregate(heavy_cases, "new")
    return {
        "schema_version": "1.0",
        "baseline_id": manifest.get("baseline_id"),
        "baseline_manifest": str(manifest_path),
        "baseline_dir": str(baseline_path),
        "gold_dataset": str(dataset_path),
        "sparse_vector_name": sparse_receipt.vector_name,
        "query_limit": QUERY_LIMIT,
        "identifier_heavy": {
            "rule": IDENTIFIER_HEAVY_RULE,
            "case_ids": heavy_ids,
            "applicable_case_count": heavy_new["applicable_case_count"],
            "old": heavy_old,
            "new": heavy_new,
            "deltas": {
                metric: _delta(heavy_new[metric], heavy_old[metric])
                for metric in METRIC_NAMES
            },
        },
        "old": old_summary,
        "new": new_summary,
        "deltas": delta_summary,
        "improved": outcome_counts["improved"],
        "unchanged": outcome_counts["unchanged"],
        "regressed": outcome_counts["regressed"],
        "outcome_counts": outcome_counts,
        "metric_outcome_counts": {
            metric: _metric_outcomes(cases, metric)
            for metric in ("recall_at_5", "recall_at_10", "mrr")
        },
        "cases": cases,
        "call_accounting": {
            "model_calls": 0,
            "token_usage": 0,
            "generation_calls": 0,
            "embedding_calls": 0,
            "analyzer_calls": 0,
            "dense_embedding_calls": 0,
            "sparse_encoder_calls": len(cases),
            "sparse_queries": len(cases),
            "reranker_calls": 0,
            "answer_calls": 0,
            "runtime_verifier_calls": 0,
            "external_judge_calls": 0,
        },
    }


def run_sparse_evaluation(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Compatibility alias for callers that prefer an explicit run verb."""
    return evaluate_sparse(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare frozen and current sparse retrieval rankings")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args(argv)
    result = evaluate_sparse(args.project_root, args.baseline_dir)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.resolve().write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
