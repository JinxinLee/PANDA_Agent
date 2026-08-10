"""Offline, auditable replay tools for the v2.6 knowledge-base migration.

This module deliberately has no Vertex, database, or Qdrant dependency.  A
capture made by an operational environment contains every model-produced input
and every channel output needed for deterministic replay.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

import yaml
from qdrant_client import models

from panda_agent.evaluation import deterministic_case_metrics, load_gold_dataset
from panda_agent.evaluator_catalog import catalog_receipt, load_evaluator_catalog, load_normalized_lookup
from panda_agent.storage import Storage, StorageSettings


MIGRATION_SCHEMA_VERSION = "panda-migration/v1"
CANONICAL_GOLD_SHA256 = "b5406e36c64ee664f9e2ff9c0f42e354feb7164c81d8f1c7551d8f2ed1d0b687"
MIGRATION_CASE_IDS = (
    "g001", "g007", "g012", "g013", "g027", "g051", "g060", "g085", "g106", "g116",
)
FUSION_WEIGHTS = {
    "exact": 2.0, "path": 2.0, "metadata": 1.0, "dense": 1.0, "sparse": 1.0, "paper": 1.15,
    "workflow": 1.2, "graph": 0.8,
}


class MigrationError(RuntimeError):
    """A migration artifact is malformed, incompatible, or would be overwritten."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _case_hash(case: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(case))


def _new_json(path: Path, value: Any) -> Path:
    if path.exists():
        raise MigrationError(f"refusing to overwrite artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))
    return path


def write_comparison_artifact(path: Path, value: Mapping[str, Any]) -> Path:
    """Write a canonical, non-overwriting comparison receipt."""
    return _new_json(path, dict(value))


def sanitized_endpoint_identity(url: str) -> dict[str, str | int | None]:
    """Return endpoint provenance without serializing userinfo or a password."""
    parsed = urlsplit(url)
    return {"scheme": parsed.scheme, "host": parsed.hostname, "port": parsed.port, "database": parsed.path.lstrip("/") or None}


def build_suite(canonical_gold: Path, output: Path) -> dict[str, Any]:
    """Derive the fixed ten-case suite from the exact signed v2.6 Gold file."""
    actual_hash = sha256_file(canonical_gold)
    if actual_hash != CANONICAL_GOLD_SHA256:
        raise MigrationError(
            f"canonical Gold SHA mismatch: expected {CANONICAL_GOLD_SHA256}, got {actual_hash}"
        )
    raw = yaml.safe_load(canonical_gold.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("questions"), list):
        raise MigrationError("canonical Gold has no questions list")
    by_id = {item.get("id"): item for item in raw["questions"] if isinstance(item, dict)}
    missing = [case_id for case_id in MIGRATION_CASE_IDS if case_id not in by_id]
    if missing:
        raise MigrationError(f"canonical Gold misses migration cases: {missing}")
    cases = [
        {"id": case_id, "canonical_case_sha256": _case_hash(by_id[case_id]), "gold": by_id[case_id]}
        for case_id in MIGRATION_CASE_IDS
    ]
    payload = {
        "schema_version": MIGRATION_SCHEMA_VERSION,
        "kind": "frozen_migration_suite",
        "canonical_gold_sha256": actual_hash,
        "case_ids": list(MIGRATION_CASE_IDS),
        "cases": cases,
    }
    payload["suite_sha256"] = sha256_bytes(canonical_bytes(payload))
    _new_json(output, payload)
    return payload


def load_suite(path: Path, canonical_gold: Path | None = None) -> dict[str, Any]:
    try:
        suite = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MigrationError(f"migration suite is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise MigrationError(f"migration suite is invalid JSON: {path}") from exc
    if suite.get("schema_version") != MIGRATION_SCHEMA_VERSION or suite.get("kind") != "frozen_migration_suite":
        raise MigrationError("unsupported migration suite")
    if suite.get("canonical_gold_sha256") != CANONICAL_GOLD_SHA256:
        raise MigrationError("suite is not derived from the canonical v2.6 Gold")
    if tuple(suite.get("case_ids", [])) != MIGRATION_CASE_IDS:
        raise MigrationError("suite case IDs differ from the frozen migration set")
    cases = suite.get("cases")
    if not isinstance(cases, list) or [item.get("id") for item in cases] != list(MIGRATION_CASE_IDS):
        raise MigrationError("suite cases are incomplete or unordered")
    expected = dict(suite)
    claimed = expected.pop("suite_sha256", None)
    if claimed != sha256_bytes(canonical_bytes(expected)):
        raise MigrationError("suite SHA does not match its content")
    for item in cases:
        if not isinstance(item.get("gold"), dict) or item.get("canonical_case_sha256") != _case_hash(item["gold"]):
            raise MigrationError(f"invalid canonical case receipt: {item.get('id')}")
    if canonical_gold is not None:
        if sha256_file(canonical_gold) != CANONICAL_GOLD_SHA256:
            raise MigrationError("provided canonical Gold does not have the required SHA")
        source = yaml.safe_load(canonical_gold.read_text(encoding="utf-8"))
        source_cases = {item["id"]: item for item in source["questions"]}
        for item in cases:
            if item["gold"] != source_cases[item["id"]]:
                raise MigrationError(f"suite case differs from canonical Gold: {item['id']}")
    return suite


def stable_channel_order(items: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Make channel ordering portable when a backend returns equal scores."""
    normalized = [dict(item) for item in items]
    if any(not isinstance(item.get("object_id"), str) for item in normalized):
        raise MigrationError("all replay candidates need a string object_id")
    return sorted(normalized, key=lambda item: (-float(item.get("score", 0.0)), item["object_id"]))


def pre_llm_fusion(rankings: Mapping[str, Iterable[Mapping[str, Any]]]) -> dict[str, Any]:
    """RRF fusion only; no reranking model is involved.

    Structured channels retain a stable score/id order, and fusion ties are
    resolved by object ID.  This gives replay a meaningful exact identity.
    """
    scores: dict[str, float] = {}
    output: dict[str, list[str]] = {}
    for channel in sorted(rankings):
        if channel not in FUSION_WEIGHTS:
            raise MigrationError(f"unsupported replay channel: {channel}")
        ordered = stable_channel_order(rankings[channel])
        output[channel] = [item["object_id"] for item in ordered]
        for rank, item in enumerate(ordered, start=1):
            object_id = item["object_id"]
            scores[object_id] = scores.get(object_id, 0.0) + FUSION_WEIGHTS[channel] / (60 + rank)
    ordered_ids = sorted(scores, key=lambda object_id: (-scores[object_id], object_id))
    return {
        "rankings": output,
        "channel_scores": {channel: [{"object_id": item["object_id"], "score": float(item.get("score", 0.0))} for item in stable_channel_order(rankings[channel])] for channel in sorted(rankings)},
        "fusion_scores": {object_id: scores[object_id] for object_id in ordered_ids},
        "ranked_object_ids": ordered_ids,
        "model_calls": 0,
    }


def _capture_identity(capture: Mapping[str, Any]) -> str:
    copy = dict(capture)
    copy.pop("capture_sha256", None)
    return sha256_bytes(canonical_bytes(copy))


def capture_replay(suite: Mapping[str, Any], cases: Mapping[str, Mapping[str, Any]], output: Path) -> dict[str, Any]:
    """Persist fixed plans/vector inputs and raw channel outputs from an original run.

    The caller is responsible for any live original-environment collection. The
    stored artifact separately accounts for model calls and makes subsequent
    replay/compare unable to call a model.
    """
    ids = set(MIGRATION_CASE_IDS)
    if set(cases) != ids:
        raise MigrationError("capture must contain exactly the frozen migration cases")
    normalized: dict[str, dict[str, Any]] = {}
    for case_id in MIGRATION_CASE_IDS:
        item = dict(cases[case_id])
        vector_inputs = item.get("vector_inputs")
        if not isinstance(item.get("plan"), dict) or not isinstance(vector_inputs, dict):
            raise MigrationError(f"capture case needs fixed plan and vector_inputs: {case_id}")
        if set(("dense", "sparse", "filter")) - set(vector_inputs):
            raise MigrationError(f"capture vector inputs need dense/sparse/filter: {case_id}")
        channels = item.get("channels")
        if not isinstance(channels, dict) or not channels:
            raise MigrationError(f"capture case needs channel outputs: {case_id}")
        required_channels = {"dense", "sparse", "exact", "path", "metadata", "workflow", "graph"}
        if required_channels - set(channels):
            raise MigrationError(f"capture channels need vector and structured phases: {case_id}")
        normalized[case_id] = item
    payload = {
        "schema_version": MIGRATION_SCHEMA_VERSION,
        "kind": "retrieval_capture",
        "suite_sha256": suite["suite_sha256"],
        "model_calls": int(sum(int(item.get("model_calls", 0)) for item in normalized.values())),
        "cases": normalized,
    }
    payload["capture_sha256"] = _capture_identity(payload)
    _new_json(output, payload)
    return payload


def collect_live_capture(project_root: Path, suite: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Capture original-run fixed plans and vector inputs; model use is receipt-only."""
    from panda_agent.retrieval import Retriever

    retriever = Retriever(project_root)
    output: dict[str, dict[str, Any]] = {}
    for suite_case in suite["cases"]:
        case_id, question = suite_case["id"], suite_case["gold"]["query"]
        before = retriever.vertex.stats_snapshot()
        plan = retriever.analyze(question)
        dense_hits, sparse_hits, dense_vector = retriever._vector(question, plan, retriever.policies.candidate_pool_per_channel)
        sparse_vector = next(iter(retriever.sparse.query_embed(question)))
        version_scopes = [models.Filter(must=[models.FieldCondition(key="source_id", match=models.MatchValue(value=repo)), models.FieldCondition(key="source_version_id", match=models.MatchValue(value=f"{repo}@{plan.resolved_versions[repo]}"))]) for repo in plan.target_repositories]
        version_scopes.append(models.FieldCondition(key="source_id", match=models.MatchAny(any=[*retriever.context_sources, "curated_panda_domain"])))
        query_filter = models.Filter(should=version_scopes) if plan.target_repositories else None
        exact = retriever._exact(plan, question, retriever.policies.candidate_pool_per_channel)
        workflow = retriever._workflow(question, plan, retriever.policies.candidate_pool_per_channel)
        graph = retriever._graph([*exact, *[point.payload for point in dense_hits], *[point.payload for point in sparse_hits]], plan, retriever.policies.candidate_pool_per_channel)
        after = retriever.vertex.stats_snapshot()
        model_calls = max(0, int(after.get("model_calls", 0)) - int(before.get("model_calls", 0)))
        output[case_id] = {
            "plan": plan.model_dump(mode="json"),
            "vector_inputs": {"dense": list(dense_vector), "sparse": {"indices": sparse_vector.indices.tolist(), "values": sparse_vector.values.tolist()}, "filter": query_filter.model_dump(mode="json") if query_filter else {}},
            "channels": {"dense": [{**point.payload, "score": float(point.score)} for point in dense_hits], "sparse": [{**point.payload, "score": float(point.score)} for point in sparse_hits], "exact": exact, "path": [], "metadata": [], "workflow": workflow, "graph": graph},
            "model_calls": model_calls,
        }
    return output


def replay_capture(suite: Mapping[str, Any], capture_path: Path, output: Path) -> dict[str, Any]:
    """Replay a capture with zero model calls and persist inputs, outputs, identity."""
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    if capture.get("kind") != "retrieval_capture" or capture.get("suite_sha256") != suite.get("suite_sha256"):
        raise MigrationError("capture and suite do not match")
    if capture.get("capture_sha256") != _capture_identity(capture):
        raise MigrationError("capture SHA does not match its content")
    results: dict[str, Any] = {}
    for case_id in MIGRATION_CASE_IDS:
        item = capture.get("cases", {}).get(case_id)
        if not isinstance(item, dict):
            raise MigrationError(f"capture misses case: {case_id}")
        results[case_id] = {
            "inputs": {"plan": item["plan"], "vector_inputs": item["vector_inputs"]},
            "outputs": pre_llm_fusion(item["channels"]),
        }
    payload = {
        "schema_version": MIGRATION_SCHEMA_VERSION,
        "kind": "retrieval_replay",
        "suite_sha256": suite["suite_sha256"],
        "capture_sha256": capture["capture_sha256"],
        "model_calls": 0,
        "cases": results,
    }
    payload["replay_sha256"] = sha256_bytes(canonical_bytes(payload))
    _new_json(output, payload)
    return payload


class BackendReplayAdapter:
    """Zero-LLM original/restored backend adapter using captured query inputs."""

    _columns = ("object_id", "source_id", "source_version_id", "object_type", "title", "text", "authority_level", "locator")

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    @classmethod
    def _objects(cls, rows: Iterable[Any]) -> list[dict[str, Any]]:
        return [dict(zip(cls._columns, row)) for row in rows]

    def _sql(self, query: str, params: list[Any]) -> list[dict[str, Any]]:
        with self.storage.connect() as connection:
            return self._objects(connection.execute(query, params).fetchall())

    def channels(self, item: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
        plan, vectors = item["plan"], item["vector_inputs"]
        filter_value = vectors["filter"]
        query_filter = models.Filter.model_validate(filter_value) if filter_value else None
        common = {"collection_name": self.storage.settings.collection_name, "query_filter": query_filter, "limit": 30, "with_payload": True}
        dense = self.storage.qdrant.query_points(query=vectors["dense"], using="dense", **common).points
        sparse_raw = vectors["sparse"]
        sparse = models.SparseVector(indices=sparse_raw["indices"], values=sparse_raw["values"])
        sparse_hits = self.storage.qdrant.query_points(query=sparse, using="sparse", **common).points
        terms = [str(value) for value in [*plan.get("symbols", []), *plan.get("concepts", [])] if str(value)][:24]
        sources = list(plan.get("target_repositories", []))
        params: list[Any] = [sources]
        scope = "source_id=ANY(%s)" if sources else "TRUE"
        exact_where = "FALSE" if not terms else " OR ".join("title ILIKE %s OR text ILIKE %s" for _ in terms)
        for term in terms:
            params.extend([f"%{term}%", f"%{term}%"])
        base = "SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator FROM knowledge_objects WHERE "
        exact = self._sql(base + f"({scope}) AND ({exact_where}) ORDER BY object_id LIMIT 30", params)
        path_params = [sources, *[f"%{term}%" for term in terms]]
        path_where = "FALSE" if not terms else " OR ".join("locator->>'path' ILIKE %s" for _ in terms)
        path = self._sql(base + f"({scope}) AND ({path_where}) ORDER BY object_id LIMIT 30", path_params)
        metadata = self._sql(base + f"({scope}) ORDER BY source_id,source_version_id,object_id LIMIT 30", [sources])
        workflow_scope = "k.source_id=ANY(%s)" if sources else "TRUE"
        workflow = self._sql("SELECT k.object_id,k.source_id,k.source_version_id,k.object_type,k.title,k.text,k.authority_level,k.locator FROM workflow_steps w JOIN knowledge_objects k ON k.object_id=w.payload->>'entrypoint_object_id' WHERE " + workflow_scope + " ORDER BY k.object_id LIMIT 30", [sources])
        seed_ids = [point.payload["object_id"] for point in dense if point.payload and point.payload.get("object_id")][:30]
        graph = [] if not seed_ids else self._sql("SELECT DISTINCT k.object_id,k.source_id,k.source_version_id,k.object_type,k.title,k.text,k.authority_level,k.locator FROM relation_edges r JOIN knowledge_objects k ON k.object_id=CASE WHEN r.subject_id=ANY(%s) THEN r.object_id ELSE r.subject_id END WHERE r.subject_id=ANY(%s) OR r.object_id=ANY(%s) ORDER BY k.object_id LIMIT 30", [seed_ids, seed_ids, seed_ids])
        def points(values: Iterable[Any]) -> list[dict[str, Any]]:
            return [{**dict(point.payload), "score": float(point.score)} for point in values if point.payload]
        return {"dense": points(dense), "sparse": points(sparse_hits), "exact": exact, "path": path, "metadata": metadata, "workflow": workflow, "graph": graph}


def replay_backend(suite: Mapping[str, Any], capture_path: Path, output: Path, *, storage: Storage) -> dict[str, Any]:
    """Execute captured vector + structured queries on an explicit backend, no model calls."""
    capture = json.loads(capture_path.read_text(encoding="utf-8"))
    if capture.get("capture_sha256") != _capture_identity(capture) or capture.get("suite_sha256") != suite.get("suite_sha256"):
        raise MigrationError("capture and suite identity mismatch")
    adapter = BackendReplayAdapter(storage)
    cases: dict[str, Any] = {}
    for case_id in MIGRATION_CASE_IDS:
        item = capture["cases"].get(case_id)
        if not isinstance(item, dict):
            raise MigrationError(f"capture misses case: {case_id}")
        channels = adapter.channels(item)
        cases[case_id] = {"inputs": {"plan": item["plan"], "vector_inputs": item["vector_inputs"]}, "outputs": pre_llm_fusion(channels)}
    payload = {"schema_version": MIGRATION_SCHEMA_VERSION, "kind": "backend_replay", "probe_kind": "deterministic_storage_query_probe_not_full_runtime_retriever_reproduction", "suite_sha256": suite["suite_sha256"], "capture_sha256": capture["capture_sha256"], "model_calls": 0, "backend_identity": {"database": sanitized_endpoint_identity(storage.settings.database_url), "qdrant": sanitized_endpoint_identity(storage.settings.qdrant_url), "collection_name": storage.settings.collection_name}, "cases": cases}
    payload["replay_sha256"] = sha256_bytes(canonical_bytes(payload))
    _new_json(output, payload)
    return payload


def _tie_groups(scores: Mapping[str, Any], tolerance: float = 1e-6) -> list[set[str]]:
    ordered = sorted(((str(key), float(value)) for key, value in scores.items()), key=lambda item: (-item[1], item[0]))
    groups: list[set[str]] = []
    values: list[float] = []
    for object_id, score in ordered:
        if not groups or abs(values[-1] - score) > tolerance:
            groups.append({object_id})
            values.append(score)
        else:
            groups[-1].add(object_id)
    return groups


def compare_replays(left_path: Path, right_path: Path, tolerance: float = 1e-6) -> dict[str, Any]:
    """Compare ranked replay outputs, allowing permutations only inside ties."""
    left = json.loads(left_path.read_text(encoding="utf-8"))
    right = json.loads(right_path.read_text(encoding="utf-8"))
    if left.get("suite_sha256") != right.get("suite_sha256"):
        raise MigrationError("cannot compare replays from different suites")
    cases: dict[str, Any] = {}
    for case_id in MIGRATION_CASE_IDS:
        a = left.get("cases", {}).get(case_id, {}).get("outputs", {})
        b = right.get("cases", {}).get(case_id, {}).get("outputs", {})
        channels_equal = a.get("rankings") == b.get("rankings")
        channel_score_equal = True
        for channel in set(a.get("channel_scores", {})) | set(b.get("channel_scores", {})):
            a_scores = {item["object_id"]: item["score"] for item in a.get("channel_scores", {}).get(channel, [])}
            b_scores = {item["object_id"]: item["score"] for item in b.get("channel_scores", {}).get(channel, [])}
            if set(a_scores) != set(b_scores) or _tie_groups(a_scores, tolerance) != _tie_groups(b_scores, tolerance) or any(abs(float(a_scores[key]) - float(b_scores[key])) > tolerance for key in a_scores):
                channel_score_equal = False
        group_equal = _tie_groups(a.get("fusion_scores", {}), tolerance) == _tie_groups(b.get("fusion_scores", {}), tolerance)
        # Scores beyond the allowed tolerance must preserve exact rank; the
        # group comparison above intentionally treats near-equal ranks as sets.
        cases[case_id] = {"channels_equal": channels_equal, "channel_score_equal": channel_score_equal, "fusion_tie_groups_equal": group_equal, "passed": channels_equal and channel_score_equal and group_equal}
    return {"model_calls": 0, "passed": all(item["passed"] for item in cases.values()), "cases": cases}


def _selector_sets(gold: Path, lookup: Mapping[str, Mapping[str, Any]]) -> dict[str, list[list[str]]]:
    dataset = load_gold_dataset(gold)
    selected = {question.id: question for question in dataset.questions if question.id in MIGRATION_CASE_IDS}
    sets: dict[str, list[list[str]]] = {}
    for case_id in MIGRATION_CASE_IDS:
        question = selected[case_id]
        sets[case_id] = [
            sorted(object_id for object_id, item in lookup.items() if any(candidate.matches(item) for candidate in group.any_of))
            for group in question.required_evidence_groups
        ]
    return sets


def compare_evaluators(canonical_gold: Path, normalized_objects: Path, portable_catalog: Path, *, records: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Require exact selector and optional deterministic metric parity for A/B."""
    if sha256_file(canonical_gold) != CANONICAL_GOLD_SHA256:
        raise MigrationError("evaluator comparison requires canonical v2.6 Gold")
    a = load_normalized_lookup(normalized_objects)
    b = load_evaluator_catalog(portable_catalog)
    selectors_a, selectors_b = _selector_sets(canonical_gold, a), _selector_sets(canonical_gold, b)
    result: dict[str, Any] = {"model_calls": 0, "selector_parity": selectors_a == selectors_b, "selectors": {"normalized": selectors_a, "catalog": selectors_b}}
    if records is not None:
        questions = {item.id: item for item in load_gold_dataset(canonical_gold).questions}
        metrics_a = {case_id: deterministic_case_metrics(questions[case_id], records[case_id].get("result", {}), records[case_id].get("diagnostics", {}), a) for case_id in MIGRATION_CASE_IDS}
        metrics_b = {case_id: deterministic_case_metrics(questions[case_id], records[case_id].get("result", {}), records[case_id].get("diagnostics", {}), b) for case_id in MIGRATION_CASE_IDS}
        result["saved_record_metric_parity"] = metrics_a == metrics_b
        result["saved_record_metrics"] = {"normalized": metrics_a, "catalog": metrics_b}
    result["passed"] = result["selector_parity"] and result.get("saved_record_metric_parity", True)
    return result


def _record_map(value: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    records = {str(item["id"]): item for item in value}
    if set(records) != set(MIGRATION_CASE_IDS):
        raise MigrationError("QA records must contain exactly the frozen migration cases")
    return records


def load_records(path: Path) -> list[dict[str, Any]]:
    """Read either a records JSON array or line-delimited records artifact."""
    raw = path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = [json.loads(line) for line in raw.splitlines() if line.strip()]
    if isinstance(parsed, dict):
        parsed = parsed.get("records")
    if not isinstance(parsed, list) or not all(isinstance(item, dict) for item in parsed):
        raise MigrationError(f"records must be a JSON array or JSONL: {path}")
    return parsed


def collect_live_qa(project_root: Path, suite: Mapping[str, Any], role: str, canonical_gold: Path, *, storage: Storage | None = None) -> list[dict[str, Any]]:
    """Collect one role's live QA outputs without touching evaluation-run storage.

    This is intentionally the only migration command path permitted to invoke
    models.  It uses the suite's embedded canonical questions and writes a
    separate receipt supplied by the CLI; re-scoring and comparison remain
    model-free.
    """
    if role not in {"baseline", "restored"}:
        raise MigrationError("live QA role must be baseline or restored")
    from panda_agent.evaluation_runner import judge_answer
    from panda_agent.llm.vertex import VertexAIClient
    from panda_agent.qa import QAAgent
    from panda_agent.retrieval import Retriever

    retriever = Retriever(project_root, storage=storage) if storage is not None else Retriever(project_root)
    agent = QAAgent(project_root, retriever=retriever)
    judge = VertexAIClient(agent.vertex.settings.for_generation_model(agent.vertex.settings.evaluation_judge_model))
    questions = {item.id: item for item in load_gold_dataset(canonical_gold).questions}
    output: list[dict[str, Any]] = []
    for case_id in MIGRATION_CASE_IDS:
        question = questions[case_id]
        runtime_before, judge_before = agent.vertex.stats_snapshot(), judge.stats_snapshot()
        try:
            detailed = agent.run_detailed(question.query)
            metrics = {**dict(detailed.get("metrics") or {}), **judge_answer(question, detailed["result"], judge)}
            runtime_after, judge_after = agent.vertex.stats_snapshot(), judge.stats_snapshot()
            runtime = {key: int(runtime_after.get(key, 0)) - int(runtime_before.get(key, 0)) for key in ("model_calls", "token_usage")}
            judge_usage = {key: int(judge_after.get(key, 0)) - int(judge_before.get(key, 0)) for key in ("model_calls", "token_usage")}
            output.append({
                "id": case_id,
                "role": role,
                "result": detailed["result"],
                "diagnostics": detailed["diagnostics"],
                "metrics": metrics,
                "model_calls": runtime["model_calls"] + judge_usage["model_calls"],
                "token_usage": runtime["token_usage"] + judge_usage["token_usage"],
                "model_call_breakdown": {"runtime": runtime, "judge": judge_usage},
            })
        except Exception as exc:  # receipt must preserve a per-case runtime failure
            output.append({"id": case_id, "role": role, "result": {}, "diagnostics": {}, "exception": {"type": type(exc).__name__, "message": str(exc)[:2000]}})
    return output


def score_qa_records(canonical_gold: Path, catalog: Path, records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Rescore one role's saved live QA records with the portable catalog only."""
    if sha256_file(canonical_gold) != CANONICAL_GOLD_SHA256:
        raise MigrationError("QA scoring requires canonical v2.6 Gold")
    lookup = load_evaluator_catalog(catalog)
    receipt = catalog_receipt(catalog)
    questions = {item.id: item for item in load_gold_dataset(canonical_gold).questions}
    output: list[dict[str, Any]] = []
    for case_id, record in _record_map(records).items():
        item = dict(record)
        deterministic = deterministic_case_metrics(
            questions[case_id], item.get("result", {}), item.get("diagnostics", {}), lookup
        )
        metrics = {**dict(item.get("metrics") or {}), **deterministic}
        required_count = len(questions[case_id].required_identifiers)
        missing = metrics.get("missing_identifiers") or []
        metrics["identifier_coverage"] = 1.0 if not required_count else (required_count - len(missing)) / required_count
        item["metrics"] = metrics
        item["evaluator_identity"] = receipt.sha256
        item["rescore_model_calls"] = 0
        item["rescore_token_usage"] = 0
        output.append(item)
    return sorted(output, key=lambda item: item["id"])


def compare_qa_records(baseline: Iterable[Mapping[str, Any]], restored: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Separate absolute safety failures from relative transfer regression."""
    base, rest = _record_map(baseline), _record_map(restored)
    safety_fields = ("expected_status_correct", "citation_integrity")
    cases: dict[str, Any] = {}
    for case_id in MIGRATION_CASE_IDS:
        baseline_result = dict(base[case_id].get("result") or {})
        restored_result = dict(rest[case_id].get("result") or {})
        baseline_metrics = dict(base[case_id].get("metrics") or {})
        restored_metrics = dict(rest[case_id].get("metrics") or {})
        absolute = []
        if rest[case_id].get("exception"):
            absolute.append("exception")
        for field in safety_fields:
            if restored_metrics.get(field) is not True:
                absolute.append(field)
        if restored_metrics.get("wrong_version_evidence"):
            absolute.append("wrong_version_evidence")
        if restored_metrics.get("contradictions"):
            absolute.append("contradictions")
        if restored_metrics.get("major_unsupported_claim_ids"):
            absolute.append("major_unsupported_claim_ids")
        regressions = []
        if bool(baseline_metrics.get("required_source_coverage")) and not bool(restored_metrics.get("required_source_coverage")):
            regressions.append("required_source_coverage")
        if float(restored_metrics.get("answer_point_coverage", 0.0)) < float(baseline_metrics.get("answer_point_coverage", 0.0)):
            regressions.append("answer_point_coverage")
        if set(restored_metrics.get("missing_identifiers") or []) - set(baseline_metrics.get("missing_identifiers") or []):
            regressions.append("missing_identifiers")
        if set(restored_metrics.get("critical_answer_points_missing") or []) - set(baseline_metrics.get("critical_answer_points_missing") or []):
            regressions.append("critical_answer_points_missing")
        cases[case_id] = {
            "absolute_failures": absolute,
            "transfer_regressions": regressions,
            "status": restored_metrics.get("status") or restored_result.get("status"),
            "intent_correct": restored_metrics.get("intent_correct"),
            "gold_recall_at_10": restored_metrics.get("gold_recall_at_10"),
            "final_evidence_recall": restored_metrics.get("final_evidence_recall"),
            "expected_status_correct": restored_metrics.get("expected_status_correct"),
            "citation_integrity": restored_metrics.get("citation_integrity"),
            "answer_point_coverage": restored_metrics.get("answer_point_coverage"),
            "required_source_coverage": restored_metrics.get("required_source_coverage"),
            "missing_identifiers": sorted(restored_metrics.get("missing_identifiers") or []),
            "critical_answer_points_missing": sorted(
                restored_metrics.get("critical_answer_points_missing") or []
            ),
            "major_unsupported_claim_ids": sorted(
                restored_metrics.get("major_unsupported_claim_ids") or []
            ),
            "baseline": {
                "status": baseline_metrics.get("status") or baseline_result.get("status"),
                "intent_correct": baseline_metrics.get("intent_correct"),
                "gold_recall_at_10": baseline_metrics.get("gold_recall_at_10"),
                "final_evidence_recall": baseline_metrics.get("final_evidence_recall"),
                "answer_point_coverage": baseline_metrics.get("answer_point_coverage"),
                "required_source_coverage": baseline_metrics.get("required_source_coverage"),
            },
        }
    evaluator_not_comparable = any(base[item].get("evaluator_identity") != rest[item].get("evaluator_identity") for item in MIGRATION_CASE_IDS if base[item].get("evaluator_identity") is not None or rest[item].get("evaluator_identity") is not None)
    has_regression = any(item["transfer_regressions"] for item in cases.values())
    has_absolute = any(item["absolute_failures"] for item in cases.values())
    # A quality failure existing in baseline must not be misattributed to the migration.
    baseline_bad = any((base[item].get("metrics") or {}).get("expected_status_correct") is not True for item in MIGRATION_CASE_IDS)
    variance = any(base[item].get("result") != rest[item].get("result") for item in MIGRATION_CASE_IDS)
    if evaluator_not_comparable:
        conclusion = "evaluator_not_comparable"
    elif has_regression:
        conclusion = "transfer_regression"
    elif baseline_bad or has_absolute:
        conclusion = "agent_variance_or_existing_quality_issue"
    elif variance:
        conclusion = "runtime_equivalent_but_model_variance_observed"
    else:
        conclusion = "transfer_equivalent"
    return {
        "model_calls": sum(
            int(base[item].get("model_calls", 0)) + int(rest[item].get("model_calls", 0))
            for item in MIGRATION_CASE_IDS
        ),
        "token_usage": sum(
            int(base[item].get("token_usage", 0)) + int(rest[item].get("token_usage", 0))
            for item in MIGRATION_CASE_IDS
        ),
        "cases": cases,
        "absolute_safety_passed": not has_absolute,
        "relative_transfer_passed": not has_regression,
        "conclusion": conclusion,
    }


def write_report(output_dir: Path, *, suite: Mapping[str, Any], replay: Mapping[str, Any] | None = None, evaluator: Mapping[str, Any] | None = None, qa: Mapping[str, Any] | None = None) -> tuple[Path, Path]:
    """Write non-overwriting JSON and Markdown receipts for migration decisions."""
    replay_bad = replay is not None and not replay.get("passed", False)
    evaluator_bad = evaluator is not None and not evaluator.get("passed", False)
    qa_conclusion = (qa or {}).get("conclusion")
    if qa_conclusion == "evaluator_not_comparable" or evaluator_bad:
        conclusion = "evaluator_not_comparable"
    elif replay_bad or qa_conclusion == "transfer_regression":
        conclusion = "transfer_regression"
    elif qa_conclusion == "agent_variance_or_existing_quality_issue":
        conclusion = qa_conclusion
    elif qa_conclusion == "runtime_equivalent_but_model_variance_observed":
        conclusion = qa_conclusion
    else:
        conclusion = "transfer_equivalent"
    case_table = []
    for case_id in MIGRATION_CASE_IDS:
        qa_case = (qa or {}).get("cases", {}).get(case_id, {})
        case_table.append(
            {
                "id": case_id,
                "replay_passed": (replay or {}).get("cases", {}).get(case_id, {}).get("passed"),
                "absolute_safety": not bool(qa_case.get("absolute_failures")),
                "transfer_regression": bool(qa_case.get("transfer_regressions")),
                "status": qa_case.get("status"),
                "gold_recall_at_10": qa_case.get("gold_recall_at_10"),
                "final_evidence_recall": qa_case.get("final_evidence_recall"),
                "baseline_gold_recall_at_10": (qa_case.get("baseline") or {}).get("gold_recall_at_10"),
                "baseline_final_evidence_recall": (qa_case.get("baseline") or {}).get("final_evidence_recall"),
                "answer_point_coverage": qa_case.get("answer_point_coverage"),
                "source_coverage": qa_case.get("required_source_coverage"),
                "missing_identifiers": qa_case.get("missing_identifiers", []),
                "critical_answer_points_missing": qa_case.get(
                    "critical_answer_points_missing", []
                ),
                "major_unsupported_claim_ids": qa_case.get(
                    "major_unsupported_claim_ids", []
                ),
            }
        )
    totals = {"model_calls": sum(int((item or {}).get("model_calls", 0)) for item in (replay, evaluator, qa)), "token_usage": sum(int((item or {}).get("token_usage", 0)) for item in (replay, evaluator, qa))}
    report = {"schema_version": MIGRATION_SCHEMA_VERSION, "global_conclusion": conclusion, "suite_identity": {"suite_sha256": suite["suite_sha256"], "canonical_gold_sha256": suite["canonical_gold_sha256"]}, "replay_gate": replay, "evaluator_gate": evaluator, "qa_gate": qa, "model_usage": totals, "cases": case_table}
    report["report_sha256"] = sha256_bytes(canonical_bytes(report))
    json_path = _new_json(output_dir / "migration_report.json", report)
    lines = [
        "# Migration report",
        "",
        f"- Conclusion: `{conclusion}`",
        f"- Suite SHA-256: `{suite['suite_sha256']}`",
        f"- Canonical Gold SHA-256: `{suite['canonical_gold_sha256']}`",
        "- Backend replay is a deterministic storage-query probe, not an exact reproduction of every runtime retriever implementation detail.",
        "- Model calls and token usage are retained as operational receipts; replay and evaluator comparison add zero model calls.",
        "",
        "| Case | Replay | Safety | Transfer regression | Status | Gold@10 (B→R) | Final evidence (B→R) | AP coverage | Source coverage | Missing identifiers | Missing critical points |",
        "|---|---:|---:|---:|---|---:|---:|---:|---:|---|---|",
    ]
    lines.extend(
        "| {id} | {replay_passed} | {absolute_safety} | {transfer_regression} | {status} | {gold_before}→{gold_after} | {final_before}→{final_after} | {ap} | {source} | {identifiers} | {critical} |".format(
            id=item["id"],
            replay_passed=item["replay_passed"],
            absolute_safety=item["absolute_safety"],
            transfer_regression=item["transfer_regression"],
            status=item["status"],
            gold_before=item["baseline_gold_recall_at_10"],
            gold_after=item["gold_recall_at_10"],
            final_before=item["baseline_final_evidence_recall"],
            final_after=item["final_evidence_recall"],
            ap=item["answer_point_coverage"],
            source=item["source_coverage"],
            identifiers=", ".join(item["missing_identifiers"]),
            critical=", ".join(item["critical_answer_points_missing"]),
        )
        for item in case_table
    )
    markdown_path = output_dir / "migration_report.md"
    if markdown_path.exists():
        raise MigrationError(f"refusing to overwrite artifact: {markdown_path}")
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, markdown_path
