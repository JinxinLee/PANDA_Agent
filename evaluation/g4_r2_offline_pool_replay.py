"""Reconstruct the offered pool from the three exposed G3 retrieval traces.

The historical traces contain candidate identity/locator metadata, not text or
specialized-channel origin bits. Placeholder text only satisfies the current
pool's payload-presence check; no text is sent to a model or used for ranking.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from panda_agent.models import RetrievalPlan
from panda_agent.retrieval import Retriever


ROOT = Path(__file__).resolve().parents[1]
TRACE_DIR = ROOT / "data/evaluation/runs/g3-evidence-admission-audit-novel-dev-v1/traces"
MANIFEST = ROOT / "data/manifests/source_manifest.json"
TARGETS = {
    "n002": ["object.a45779701b982aff3e7554da", "object.03af96b1110e782792253a18"],
    "n006": ["object.2914485ff398f61e994c46d6"],
    "n017": ["object.015bff352e03a5f5ee88c307", "object.10bfbd3c5c5a222bcdf5904d"],
}


class PoolReplayRetriever(Retriever):
    def __init__(self, context_sources: list[str]) -> None:
        self.vertex = None
        self.policies = SimpleNamespace(final_evidence_limit=12)
        self.context_sources = context_sources

    def _prioritize_and_select_evidence(self, **kwargs):
        return kwargs["ordered"], kwargs["ordered"][:30], [], [], [], []


def replay() -> list[dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    context_sources = [item["doc_id"] for item in [*manifest["papers"], *manifest["web_documents"]]]
    retriever = PoolReplayRetriever(context_sources)
    results = []
    for case_id, object_ids in TARGETS.items():
        trace = json.loads((TRACE_DIR / f"{case_id}.json").read_text(encoding="utf-8"))
        plan = RetrievalPlan.model_validate(trace["retrieval_plan"])
        rankings = {}
        for channel, items in trace["channel_candidates"].items():
            rankings[channel] = [
                {**item, "title": item["object_id"], "text": "Historical trace payload present"}
                for item in sorted(items, key=lambda item: item["rank"])
            ]
        snapshot = {"pass_origin": "historical_initial", "rankings": rankings, "supplemental_candidates": []}
        result = retriever.consolidate_and_select_candidates("Offline pool replay", plan, [snapshot])
        if result["status"] != "success":
            raise RuntimeError(f"{case_id}: {result['status']}: {result.get('failure_reason')}")
        reasons = {entry["object_id"]: entry["reason"] for entry in result["rerank_pool_entries"]}
        old_pool = {item["object_id"] for item in trace["fused_candidates"]}
        for object_id in object_ids:
            ranks = result["best_channel_ranks"].get(object_id)
            if not ranks:
                raise RuntimeError(f"{case_id}: target absent from frozen channels: {object_id}")
            results.append({
                "case_id": case_id,
                "object_id": object_id,
                "best_channel_ranks": ranks,
                "old_fused_pool": object_id in old_pool,
                "new_offered_pool": object_id in reasons,
                "entry_reason": reasons.get(object_id),
            })
    return results


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
