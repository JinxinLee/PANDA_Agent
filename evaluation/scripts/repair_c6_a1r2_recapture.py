"""C6-A1R2 provenance repair stage 2: live recapture of the six repair cases.

Uses the faithful C3-R3 full plans (guard-validated in stage 1) with the
current production channel implementations.  Never calls analyze(),
retrieve(), reranker, selector, or Gold.  Writes per-case capture records
plus a call ledger to data/tmp for replay-v2 assembly.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "evaluation" / "scripts"))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from plan_provenance import validate_executable_plan_payload  # noqa: E402
from panda_agent.models import RetrievalPlan  # noqa: E402
from panda_agent.retrieval import (  # noqa: E402
    DenseQueryBundle,
    Retriever,
    build_semantic_query,
)

FROZEN = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_repair_frozen_v1.json"
OUT_ROWS = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_repair_captured_rows_v1.json"
OUT_LEDGER = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_repair_capture_ledger_v1.json"

WRITE_VERBS = ("insert", "update", "delete", "drop", "alter", "create", "upsert")


class Counters:
    def __init__(self) -> None:
        self.sql_reads = 0
        self.qdrant_reads = 0
        self.sparse_encodes = 0

    def assert_read_only(self, sql: str) -> None:
        if any(verb in sql.casefold() for verb in WRITE_VERBS):
            raise AssertionError(f"write statement in repair capture: {sql[:120]}")


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
    return {
        "object_id": item["object_id"],
        "channel_rank": rank,
        "original_channel_score": score,
        "source_id": item.get("source_id"),
        "source_version_id": item.get("source_version_id"),
        "object_type": item.get("object_type"),
        "title": item.get("title"),
        "locator": item.get("locator") or {},
    }


def main() -> None:
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    assert frozen["identity_gate"]["result"] == "MATCH"
    repair_set = frozen["provenance_repair_set"]
    plans = frozen["plan_by_case"]
    provenance = frozen["plan_provenance_by_case"]
    semantic_active = frozen["semantic_active_by_case"]

    retriever = Retriever(PROJECT_ROOT)
    counters = Counters()
    wrap(retriever, counters)
    limit = retriever.policies.candidate_pool_per_channel
    vertex_before = retriever.vertex.stats_snapshot()

    rows: list[dict] = []
    statuses: dict[str, str] = {}
    for case_id in repair_set:
        question = provenance[case_id]["question"]
        try:
            validate_executable_plan_payload(plans[case_id])
            plan = RetrievalPlan.model_validate(plans[case_id])
            record = {
                "case_id": case_id,
                "question": question,
                "intent": plan.intent,
                "formal_english_scope": True,
                "frozen_plan_source": provenance[case_id]["full_plan_source"],
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
                "candidates": [candidate_row(i, r) for r, i in enumerate(exact_rows, 1)],
            }
            dense_hits, dense_vector = retriever._dense_query(question, query_filter, limit)
            record["channels"]["raw_dense"] = {
                "availability_state": "PRESENT_NONEMPTY" if dense_hits else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [candidate_row(h.payload, r, float(h.score)) for r, h in enumerate(dense_hits, 1)],
            }
            sparse_hits = retriever._sparse_query(question, query_filter, limit)
            record["channels"]["sparse"] = {
                "availability_state": "PRESENT_NONEMPTY" if sparse_hits else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [candidate_row(h.payload, r, float(h.score)) for r, h in enumerate(sparse_hits, 1)],
            }
            paper_rows = retriever._paper(dense_vector, plan, limit)
            record["channels"]["paper"] = {
                "availability_state": "PRESENT_NONEMPTY" if paper_rows else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [candidate_row(i, r) for r, i in enumerate(paper_rows, 1)],
            }
            workflow_rows = retriever._workflow(question, plan, limit)
            record["channels"]["workflow"] = {
                "availability_state": "PRESENT_NONEMPTY" if workflow_rows else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [candidate_row(i, r) for r, i in enumerate(workflow_rows, 1)],
            }
            graph_rows = retriever._graph(
                [*exact_rows, *[h.payload for h in dense_hits], *[h.payload for h in sparse_hits]],
                plan,
                limit,
            )
            record["channels"]["graph"] = {
                "availability_state": "PRESENT_NONEMPTY" if graph_rows else "PRESENT_EMPTY",
                "execution_status": "OK",
                "candidates": [candidate_row(i, r) for r, i in enumerate(graph_rows, 1)],
            }
            if semantic_active[case_id] and bundle.semantic is not None:
                semantic_hits, _ = retriever._dense_query(bundle.semantic.text, query_filter, limit)
                record["channels"]["semantic_dense"] = {
                    "availability_state": "PRESENT_NONEMPTY" if semantic_hits else "PRESENT_EMPTY",
                    "execution_status": "OK",
                    "semantic_view_active": True,
                    "semantic_query_text": bundle.semantic.text,
                    "semantic_query_components": [
                        {"kind": c.kind, "value": c.value, "provenance": c.provenance}
                        for c in bundle.semantic.components
                    ],
                    "candidates": [candidate_row(h.payload, r, float(h.score)) for r, h in enumerate(semantic_hits, 1)],
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
            print(case_id, "CAPTURE_COMPLETE", flush=True)
        except Exception as exc:  # noqa: BLE001
            statuses[case_id] = f"CAPTURE_FAILED:{type(exc).__name__}:{exc}"
            print(case_id, "CAPTURE_FAILED", type(exc).__name__, exc, flush=True)

    vertex_after = retriever.vertex.stats_snapshot()
    embedding_delta = {
        k: vertex_after.get(k, 0) - vertex_before.get(k, 0)
        for k in ("model_calls", "embedding_calls", "generation_calls", "token_usage")
    }
    OUT_ROWS.write_text(json.dumps(rows, default=str), encoding="utf-8")
    OUT_LEDGER.write_text(
        json.dumps(
            {
                "statuses": statuses,
                "embedding_delta": embedding_delta,
                "sparse_encodes": counters.sparse_encodes,
                "sql_reads": counters.sql_reads,
                "qdrant_reads": counters.qdrant_reads,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"statuses": statuses, "embedding_delta": embedding_delta,
                      "sparse_encodes": counters.sparse_encodes,
                      "sql_reads": counters.sql_reads, "qdrant_reads": counters.qdrant_reads}, indent=1))


if __name__ == "__main__":
    main()
