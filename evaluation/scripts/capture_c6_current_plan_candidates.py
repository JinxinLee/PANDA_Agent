"""C6-A1R2 live candidate capture over the frozen LIVE_CAPTURE_COHORT.

Evaluation-only: uses the current production channel implementations with
explicit frozen C2 prompt-3.7.0 RetrievalPlans.  Never calls analyze(),
retrieve(), the reranker, the selector, or any Gold data.  Output is a frozen
structural candidate dataset (no relevance labels).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from panda_agent.models import RetrievalPlan  # noqa: E402
from panda_agent.retrieval import (  # noqa: E402
    DenseQueryBundle,
    Retriever,
    build_semantic_query,
)

FROZEN = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_preregistration_frozen_v1.json"
OUTPUT = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "replay"
    / "phase_c_c6_current_plan_candidate_replay_v1.jsonl"
)

WRITE_VERBS = ("insert", "update", "delete", "drop", "alter", "create", "upsert")


class Counters:
    def __init__(self) -> None:
        self.sql_reads = 0
        self.qdrant_reads = 0
        self.sparse_encodes = 0

    def assert_read_only(self, sql: str) -> None:
        lowered = sql.casefold()
        if any(verb in lowered for verb in WRITE_VERBS):
            raise AssertionError(f"write statement in capture: {sql[:120]}")


def wrap(retriever: Retriever, counters: Counters) -> None:
    inner_connect = retriever.storage.connect
    inner_qdrant = retriever.storage.qdrant
    inner_sparse = retriever.sparse

    class CountingConnection:
        def __init__(self, conn) -> None:
            self._conn = conn

        def execute(self, sql, params=None):
            counters.assert_read_only(sql)
            counters.sql_reads += 1
            return self._conn.execute(sql, params)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    class CountingStorage:
        def __init__(self, storage) -> None:
            self._storage = storage
            self.qdrant = storage.qdrant
            self.settings = storage.settings

        def connect(self):
            return CountingConnection(inner_connect())

        def __getattr__(self, name):
            return getattr(self._storage, name)

    class CountingQdrant:
        def __init__(self, client) -> None:
            self._client = client

        def query_points(self, **kwargs):
            counters.qdrant_reads += 1
            return self._client.query_points(**kwargs)

        def __getattr__(self, name):
            return getattr(self._client, name)

    class CountingSparse:
        def __init__(self, encoder) -> None:
            self._encoder = encoder

        def query_embed(self, text):
            counters.sparse_encodes += 1
            return self._encoder.query_embed(text)

        def __getattr__(self, name):
            return getattr(self._encoder, name)

    retriever.storage = CountingStorage(retriever.storage)
    retriever.storage.qdrant = CountingQdrant(inner_qdrant)
    retriever.sparse = CountingSparse(inner_sparse)


def candidate_row(item: dict, rank: int, score=None) -> dict:
    locator = item.get("locator") or {}
    return {
        "object_id": item["object_id"],
        "channel_rank": rank,
        "original_channel_score": score,
        "source_id": item.get("source_id"),
        "source_version_id": item.get("source_version_id"),
        "object_type": item.get("object_type"),
        "title": item.get("title"),
        "locator": locator,
    }


def main() -> None:
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    live_cohort = frozen["live_capture_cohort"]
    core = set(frozen["core_capture_cohort"])
    semantic_active = frozen["semantic_active_by_case"]
    intent_by_case = frozen["intent_by_case"]
    question_by_case = frozen["question_by_case"]
    plan_by_case = frozen["plan_by_case"]
    plan_source_by_case = frozen["plan_source_by_case"]

    retriever = Retriever(PROJECT_ROOT)
    counters = Counters()
    wrap(retriever, counters)
    limit = retriever.policies.candidate_pool_per_channel

    rows: list[dict] = []
    statuses: dict[str, str] = {}
    vertex_before = retriever.vertex.stats_snapshot()

    for case_id in live_cohort:
        question = question_by_case[case_id]
        plan = RetrievalPlan.model_validate(plan_by_case[case_id])
        try:
            record = {
                "case_id": case_id,
                "question": question,
                "intent": intent_by_case[case_id],
                "formal_english_scope": True,
                "in_core_capture_cohort": case_id in core,
                "frozen_plan_source": plan_source_by_case[case_id],
                "frozen_plan_prompt_version": "3.7.0",
                "retrieval_plan": plan.model_dump(mode="json"),
                "channels": {},
            }
            query_filter = retriever._query_filter(plan)
            semantic_query = build_semantic_query(question, plan)
            bundle = DenseQueryBundle.from_semantic_query(question, semantic_query)

            exact_rows = retriever._exact(plan, question, limit)
            record["channels"]["exact"] = {
                "availability_state": "PRESENT_NONEMPTY" if exact_rows else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [candidate_row(item, i) for i, item in enumerate(exact_rows, 1)],
            }

            dense_hits, dense_vector = retriever._dense_query(question, query_filter, limit)
            record["channels"]["raw_dense"] = {
                "availability_state": "PRESENT_NONEMPTY" if dense_hits else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [
                    candidate_row(hit.payload, i, float(hit.score)) for i, hit in enumerate(dense_hits, 1)
                ],
            }

            sparse_hits = retriever._sparse_query(question, query_filter, limit)
            record["channels"]["sparse"] = {
                "availability_state": "PRESENT_NONEMPTY" if sparse_hits else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [
                    candidate_row(hit.payload, i, float(hit.score)) for i, hit in enumerate(sparse_hits, 1)
                ],
            }

            paper_rows = retriever._paper(dense_vector, plan, limit)
            record["channels"]["paper"] = {
                "availability_state": "PRESENT_NONEMPTY" if paper_rows else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [candidate_row(item, i) for i, item in enumerate(paper_rows, 1)],
            }

            workflow_rows = retriever._workflow(question, plan, limit)
            record["channels"]["workflow"] = {
                "availability_state": "PRESENT_NONEMPTY" if workflow_rows else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [candidate_row(item, i) for i, item in enumerate(workflow_rows, 1)],
            }

            graph_rows = retriever._graph(
                [*exact_rows, *[hit.payload for hit in dense_hits], *[hit.payload for hit in sparse_hits]],
                plan,
                limit,
            )
            record["channels"]["graph"] = {
                "availability_state": "PRESENT_NONEMPTY" if graph_rows else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [candidate_row(item, i) for i, item in enumerate(graph_rows, 1)],
            }

            if semantic_active.get(case_id) and bundle.semantic is not None:
                semantic_hits, _ = retriever._dense_query(
                    bundle.semantic.text, query_filter, limit
                )
                record["channels"]["semantic_dense"] = {
                    "availability_state": "PRESENT_NONEMPTY" if semantic_hits else "PRESENT_EMPTY",
                    "execution_status": "OK",
                    "semantic_view_active": True,
                    "semantic_query_text": bundle.semantic.text,
                    "semantic_query_components": [
                        {"kind": c.kind, "value": c.value, "provenance": c.provenance}
                        for c in bundle.semantic.components
                    ],
                    "candidates": [
                        candidate_row(hit.payload, i, float(hit.score))
                        for i, hit in enumerate(semantic_hits, 1)
                    ],
                }
            else:
                record["channels"]["semantic_dense"] = {
                    "availability_state": "SKIPPED_BY_PLAN",
                    "execution_status": "SKIPPED",
                    "semantic_view_active": False,
                    "skip_reason": "semantic_view_inactive",
                    "candidates": [],
                }

            rows.append(record)
            statuses[case_id] = "CAPTURE_COMPLETE"
            print(f"{case_id}: CAPTURE_COMPLETE", flush=True)
        except Exception as exc:  # noqa: BLE001 - record failure, never replace the case
            statuses[case_id] = f"CAPTURE_FAILED:{type(exc).__name__}:{exc}"
            rows.append(
                {
                    "case_id": case_id,
                    "question": question,
                    "intent": intent_by_case[case_id],
                    "formal_english_scope": True,
                    "in_core_capture_cohort": case_id in core,
                    "frozen_plan_source": plan_source_by_case[case_id],
                    "frozen_plan_prompt_version": "3.7.0",
                    "capture_status": statuses[case_id],
                }
            )
            print(f"{case_id}: CAPTURE_FAILED {type(exc).__name__}: {exc}", flush=True)

    vertex_after = retriever.vertex.stats_snapshot()
    embedding_delta = {
        key: vertex_after.get(key, 0) - vertex_before.get(key, 0)
        for key in ("model_calls", "embedding_calls", "generation_calls", "token_usage")
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, default=str) + "\n")

    ledger = {
        "cases": len(live_cohort),
        "statuses": statuses,
        "embedding_delta": embedding_delta,
        "sparse_encodes": counters.sparse_encodes,
        "sql_reads": counters.sql_reads,
        "qdrant_reads": counters.qdrant_reads,
    }
    (PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_capture_ledger_v1.json").write_text(
        json.dumps(ledger, indent=1), encoding="utf-8"
    )
    print(json.dumps(ledger, indent=1))


if __name__ == "__main__":
    main()
