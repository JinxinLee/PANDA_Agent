"""D3.5-A5 Phase 1 — mechanical replay-fixture builder and verifier.

Schema 1.1.0 (D3.5-A5-R2 additive evaluator-support extension): eligible candidate
entries and payload-registry entries additionally carry object_type and the full
frozen locator object, read mechanically from the frozen normalized corpus so the
complete-universe evaluator can run the existing GoldEvidenceSelector matching.
No existing field, candidate, ordering, or payload value is altered.

Builds the tracked repository-persistent downstream replay fixture from the
frozen D3.5-A2 raw records plus the frozen normalized corpus:

  evaluation/d3_5_downstream_replay_fixture.json

Construction is mechanical, deterministic, and outcome-label-independent: it
reads only the frozen A2 run records (channel rankings, structured receipts,
bridge receipts) and the normalized corpus (bounded reranker payloads).  It
never reads gold/evaluation datasets and never runs models.

Equivalence gates verified before the fixture is written:
  1. BRIDGED-cell fusion recomputed from the fixture's frozen channel
     rankings + frozen weights exactly reproduces the stored fusion_top30
     (scores to 6 decimals) and yields the recorded baseline top-30/cutoff.
  2. All persisted orderings equal the frozen record values verbatim.
  3. Bridge-candidate identities, origins, versions, and locators equal the
     frozen bridge receipts; the pre-cap eligible governed candidate universe
     is reconstructed from every INJECTED/RANKED_OUT receipt (the complete
     universe before the old provenance-order cap).
  4. Payload registry entries reconstruct the exact bounded reranker payload
     semantics (object_id/title/source_id/text[:2000]) from the normalized
     corpus.

CLI:
    PYTHONPATH=src python evaluation/scripts/d3_5_a5_build_replay_fixture.py \
        --project-root .
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

CASE_ORDER = ("g036", "g021", "n006", "g041", "g020", "n004")
STRUCTURED_ARMS = ("STRUCTURED_UNBRIDGED", "STRUCTURED_BRIDGED")
RUN_ID = "d3_5_a2_focused_20260901"
A2_RESULT_COMMIT = "e8e2d5aa532a6b54ebdcc728804b211e44fb2132"
FROZEN_A1_ANCHOR = "470b62f823c3e65637604da2f614461c1a81d5b6"
A2_PRE_OUTCOME_COMMIT = "9467061c81a288f2c3b01548b7eb39202f38e91c"
FROZEN_RUNTIME_SHA = "9b5a84996c30eaf1a297924b36452a90fe6d84d2"
FINAL_REPOSITORY_D1_SHA = "9b5a84996c30eaf1a297924b36452a90fe6d84d2"
FIXTURE_SCHEMA_VERSION = "1.1.0"

# Frozen fusion contract (frozen in the A2-era runtime; verified reproducing
# the stored fusion_top30 during D3.5-A3 and re-verified here per cell).
FUSION_WEIGHTS = {
    "exact": 2.0,
    "dense": 1.0,
    "sparse": 1.0,
    "paper": 1.15,
    "workflow": 1.2,
    "graph": 0.8,
}
FUSION_DENOMINATOR_OFFSET = 60
GRAPH_CHANNEL_LIMIT = 20  # configs/retrieval_policies.yaml candidate_pool_per_channel

# Frozen A2-era bridge receipt statuses that represent a governed,
# source/version-qualified materialized candidate (eligible for selectivity).
ELIGIBLE_BRIDGE_STATUSES = {"BRIDGED_CANDIDATE_INJECTED", "BRIDGED_CANDIDATE_RANKED_OUT"}
NON_CANDIDATE_BRIDGE_STATUSES = {
    "GOVERNED_PROVENANCE_NOT_FOUND",
    "GOVERNED_PROVENANCE_INVALID",
    "PROVENANCE_SOURCE_OBJECT_NOT_FOUND",
    "PROVENANCE_SOURCE_OBJECT_AMBIGUOUS",
    "VERSION_SCOPE_CONFLICT",
}

PLAN_FIELDS = (
    "intent",
    "target_repositories",
    "version_repositories",
    "resolved_versions",
    "symbols",
    "concepts",
    "concept_scopes",
    "required_source_types",
    "source_budgets",
    "requested_versions",
    "resolved_aliases",
)


def compact_plan(plan: dict[str, Any]) -> dict[str, Any]:
    return {key: plan.get(key) for key in PLAN_FIELDS if plan.get(key) not in (None, [], {})}


def recompute_fusion(channel_rankings: dict[str, list[str]]) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for channel, ids in channel_rankings.items():
        weight = FUSION_WEIGHTS.get(channel, 1.0)
        for rank, object_id in enumerate(ids):
            scores[object_id] = (
                scores.get(object_id, 0.0)
                + weight / (FUSION_DENOMINATOR_OFFSET + rank + 1)
            )
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def build_case_trace(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "arm": record["arm"],
        "execution_sequence": record["execution_sequence"],
        "treatment_receipt": record["treatment_receipt"],
        "question": record["question_identity"],
        "plan": compact_plan(record["plan_summary"]),
        "channel_rankings": record["channel_rankings"],
        "graph_ordering": (record["channel_rankings"] or {}).get("graph") or [],
        "structured_resolution_receipt": record.get("structured_resolution_receipt"),
        "structured_reachability_receipts": record.get("structured_reachability_receipts"),
        "structured_bridge_receipts": record.get("structured_bridge_receipts"),
        "baseline_bridged_displacement": record.get("bridge_displacement_diagnostics"),
        "structured_diagnostic_counters": record.get("structured_diagnostic_counters"),
        "final_ranked_object_ids": record.get("ranked_object_ids"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    records_path = project_root / "data" / "evaluation" / "runs" / RUN_ID / "records.jsonl"
    records = [
        json.loads(line)
        for line in records_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert len(records) == 24, f"expected 24 frozen A2 records, found {len(records)}"
    by_cell = {(r["case_id"], r["arm"]): r for r in records}

    normalized_path = project_root / "data" / "normalized" / "9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94" / "knowledge_objects.jsonl"
    normalized = {}
    for line in normalized_path.read_text(encoding="utf-8").splitlines():
        if line:
            item = json.loads(line)
            normalized[item["object_id"]] = item

    run_manifest = json.loads(
        (records_path.parent / "run_manifest.json").read_text(encoding="utf-8")
    )

    cases = {}
    payload_registry: dict[str, dict[str, Any]] = {}
    gate_failures: list[str] = []
    status_histogram: dict[str, int] = {}

    for case_id in CASE_ORDER:
        unbridged = by_cell[(case_id, "STRUCTURED_UNBRIDGED")]
        bridged = by_cell[(case_id, "STRUCTURED_BRIDGED")]

        # --- eligible governed bridge-candidate universe (pre-cap) -----------
        # The A2 runtime emits an INJECTED-status receipt both for a first
        # materialization and for a duplicate reference to an
        # already-injected candidate from another origin (reason_included
        # marks the duplicate).  The eligible universe is therefore the set
        # of UNIQUE candidate object IDs across INJECTED/RANKED_OUT
        # receipts, each carrying its full origin set (a candidate
        # independently produced by several governed structures belongs to
        # all of them — required for the per-origin diversity guard).
        reach_by_id = {
            item["reachability_receipt_id"]: item
            for item in (bridged.get("structured_reachability_receipts") or [])
        }
        a2_admitted_set = set(
            (bridged.get("bridge_displacement_diagnostics") or {}).get(
                "bridged_candidate_ids"
            )
            or []
        )
        candidates_acc: dict[str, dict[str, Any]] = {}
        for receipt in bridged.get("structured_bridge_receipts") or []:
            status = receipt.get("bridge_status")
            status_histogram[status] = status_histogram.get(status, 0) + 1
            if status not in ELIGIBLE_BRIDGE_STATUSES:
                if status not in NON_CANDIDATE_BRIDGE_STATUSES:
                    gate_failures.append(f"{case_id}: unexpected bridge status {status}")
                continue
            candidate_id = receipt.get("source_native_candidate_object_id")
            if not candidate_id:
                gate_failures.append(f"{case_id}: eligible receipt without candidate id")
                continue
            reach = reach_by_id.get(receipt.get("reachability_receipt_id")) or {}
            locator = receipt.get("locator") if isinstance(receipt.get("locator"), dict) else {}
            origin_id = receipt.get("evidence_provenance_origin_id")
            distance = reach.get("budget_consumed")
            entry = candidates_acc.get(candidate_id)
            if entry is None:
                candidates_acc[candidate_id] = {
                    "candidate_object_id": candidate_id,
                    "provenance_origin_ids": [origin_id],
                    "origin_types": [receipt.get("evidence_provenance_origin_type")],
                    "source_id": receipt.get("source_id"),
                    "source_version_id": receipt.get("source_version_id"),
                    "locator_path": locator.get("path"),
                    "min_structural_distance_transitions": distance,
                    "a2_disposition": "A2_ADMITTED"
                    if candidate_id in a2_admitted_set
                    else "A2_CAPPED_OUT",
                    "object_type": normalized.get(candidate_id, {}).get("object_type"),
                    "locator": normalized.get(candidate_id, {}).get("locator"),
                }
            else:
                if origin_id not in entry["provenance_origin_ids"]:
                    entry["provenance_origin_ids"].append(origin_id)
                if receipt.get("evidence_provenance_origin_type") not in entry["origin_types"]:
                    entry["origin_types"].append(receipt.get("evidence_provenance_origin_type"))
                if distance is not None:
                    entry["min_structural_distance_transitions"] = min(
                        entry["min_structural_distance_transitions"], distance
                    )
                if (
                    entry["source_id"] != receipt.get("source_id")
                    or entry["source_version_id"] != receipt.get("source_version_id")
                    or entry["locator_path"] != locator.get("path")
                ):
                    gate_failures.append(
                        f"{case_id}: inconsistent identity fields across duplicate receipts for {candidate_id}"
                    )
        eligible = sorted(candidates_acc.values(), key=lambda item: item["candidate_object_id"])
        if a2_admitted_set - {item["candidate_object_id"] for item in eligible}:
            gate_failures.append(
                f"{case_id}: displacement receipt references non-eligible candidate"
            )

        # --- fusion reproduction gate (BRIDGED cell) -------------------------
        fused = recompute_fusion(bridged["channel_rankings"])
        stored_top30 = bridged["fusion_top30"]
        recomputed_top30 = {oid: round(score, 6) for oid, score in fused[:30]}
        stored_rounded = {oid: round(score, 6) for oid, score in stored_top30.items()}
        if recomputed_top30 != stored_rounded:
            gate_failures.append(f"{case_id}: fusion top-30 reproduction failed")
        baseline_top30_ids = [oid for oid, _ in fused[:30]]
        if baseline_top30_ids != list(stored_top30.keys()):
            gate_failures.append(f"{case_id}: fused ordering mismatch vs stored top-30 keys")
        cutoff_score = round(fused[29][1], 6)
        baseline_fused_full = [[oid, round(score, 9)] for oid, score in fused]

        # --- ordering equality gates -----------------------------------------
        unbridged_trace = build_case_trace(unbridged)
        bridged_trace = build_case_trace(bridged)
        if bridged_trace["graph_ordering"] != (bridged["channel_rankings"] or {}).get("graph"):
            gate_failures.append(f"{case_id}: bridged graph ordering mismatch")
        if unbridged_trace["graph_ordering"] != (unbridged["channel_rankings"] or {}).get("graph"):
            gate_failures.append(f"{case_id}: unbridged graph ordering mismatch")

        # --- baseline bridge state (old provenance-order cap output) ---------
        # The displacement receipt's bridged_candidate_ids is the frozen A2
        # injection order (the exact prefix order used by the runtime merge).
        a2_admitted_injection_order = list(
            (bridged.get("bridge_displacement_diagnostics") or {}).get("bridged_candidate_ids") or []
        )
        admitted_from_universe = {
            item["candidate_object_id"]
            for item in eligible
            if item["a2_disposition"] == "A2_ADMITTED"
        }
        if set(a2_admitted_injection_order) != admitted_from_universe:
            gate_failures.append(
                f"{case_id}: A2 admitted bridge IDs mismatch vs A2_ADMITTED universe entries"
            )

        # --- deterministic baseline-bridged graph reconstruction -------------
        def merge_ids(prefix: list[str], rows: list[str], limit: int) -> list[str]:
            merged, seen = [], set()
            for oid in [*prefix, *rows]:
                if oid in seen:
                    continue
                seen.add(oid)
                merged.append(oid)
                if len(merged) >= limit:
                    break
            return merged

        unbridged_graph = unbridged_trace["graph_ordering"]
        baseline_bridged_graph_recomputed = merge_ids(
            a2_admitted_injection_order, unbridged_graph, GRAPH_CHANNEL_LIMIT
        )
        displaced_before = [
            oid for oid in unbridged_graph if oid not in baseline_bridged_graph_recomputed
        ]
        recorded_displaced = (
            bridged.get("bridge_displacement_diagnostics") or {}
        ).get("displaced_object_ids") or []
        if sorted(displaced_before) != sorted(recorded_displaced):
            gate_failures.append(f"{case_id}: baseline displacement reproduction failed")

        # --- payload registry -------------------------------------------------
        needed = set(baseline_top30_ids) | {item["candidate_object_id"] for item in eligible}
        for object_id in sorted(needed):
            if object_id in payload_registry:
                continue
            record = normalized.get(object_id)
            if record is None:
                gate_failures.append(f"{case_id}: payload object missing from normalized corpus: {object_id}")
                continue
            payload_registry[object_id] = {
                "object_id": object_id,
                "title": record.get("title"),
                "source_id": record.get("source_id"),
                "text_payload_2000": (record.get("text") or "")[:2000],
                "object_type": record.get("object_type"),
                "locator": record.get("locator"),
            }

        cases[case_id] = {
            "case_id": case_id,
            "question": bridged["question_identity"],
            "arms": {
                "STRUCTURED_UNBRIDGED": unbridged_trace,
                "STRUCTURED_BRIDGED": bridged_trace,
            },
            "frozen_plan_fields": compact_plan(bridged["plan_summary"]),
            "eligible_governed_bridge_candidates": eligible,
            "eligible_governed_bridge_candidate_count": len(eligible),
            "baseline_old_cap_admitted_ids_injection_order": a2_admitted_injection_order,
            "baseline_old_cap_admitted_count": len(a2_admitted_injection_order),
            "unbridged_graph_ordering": unbridged_graph,
            "baseline_bridged_graph_ordering_recomputed": baseline_bridged_graph_recomputed,
            "baseline_ordinary_graph_displaced_ids_before": displaced_before,
            "fusion_contract": {
                "weights": FUSION_WEIGHTS,
                "denominator_offset": FUSION_DENOMINATOR_OFFSET,
                "graph_channel_limit": GRAPH_CHANNEL_LIMIT,
                "baseline_fused_ordering_full": baseline_fused_full,
                "baseline_top30_member_ids": baseline_top30_ids,
                "baseline_top30_cutoff_score": cutoff_score,
                "reproduction_verified": True,
            },
        }

    unexpected_statuses = set(status_histogram) - (
        ELIGIBLE_BRIDGE_STATUSES | NON_CANDIDATE_BRIDGE_STATUSES
    )
    if unexpected_statuses:
        gate_failures.append(f"unexpected bridge statuses: {sorted(unexpected_statuses)}")

    if gate_failures:
        print("FIXTURE EQUIVALENCE GATE FAILURES:")
        for failure in gate_failures:
            print(" -", failure)
        return 2

    fixture = {
        "fixture_schema_version": FIXTURE_SCHEMA_VERSION,
        "checkpoint": "D3.5-A5",
        "purpose": "repository-persistent frozen upstream trace for downstream selectivity (A5) and bounded admission (A6) replay; outcome-label clean by construction",
        "created_from_frozen_A2": True,
        "identity": {
            "source_a2_result_commit": A2_RESULT_COMMIT,
            "source_a2_run_id": RUN_ID,
            "frozen_a1_scientific_state_anchor": FROZEN_A1_ANCHOR,
            "a2_pre_outcome_execution_commit": A2_PRE_OUTCOME_COMMIT,
            "frozen_runtime_sha": FROZEN_RUNTIME_SHA,
            "final_repository_d1_sha": FINAL_REPOSITORY_D1_SHA,
            "source_manifest_sha256": "9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94",
            "index_identity": {
                "qdrant_collection": "panda_knowledge_v1",
                "index_fingerprint": "8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9",
                "qdrant_points": 104973,
                "sql_objects": 133077,
            },
            "case_ids": list(CASE_ORDER),
            "cell_trace_identities": [
                {"case_id": case_id, "arm": arm, "execution_sequence": by_cell[(case_id, arm)]["execution_sequence"]}
                for case_id in CASE_ORDER
                for arm in STRUCTURED_ARMS
            ],
            "run_started_at_utc": run_manifest.get("started_at_utc"),
        },
        "cases": cases,
        "reranker_payload_registry": payload_registry,
        "builder_verification": {
            "fusion_reproduction": "BRIDGED-cell fusion recomputed from frozen channel rankings + frozen weights equals stored fusion_top30 for all six cases",
            "orderings": "all persisted orderings equal frozen record values verbatim",
            "eligible_universe": "complete pre-cap eligible governed bridge-candidate universe reconstructed from INJECTED/RANKED_OUT receipts",
            "bridge_status_histogram": status_histogram,
            "payload_registry_entries": len(payload_registry),
            "outcome_labels_present": False,
        },
    }

    out_path = project_root / "evaluation" / "d3_5_downstream_replay_fixture.json"
    out_path.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("fixture written:", out_path)
    print("size bytes:", out_path.stat().st_size)
    print("bridge status histogram:", json.dumps(status_histogram, sort_keys=True))
    print("payload registry entries:", len(payload_registry))
    print("eligible universe counts:", {c: cases[c]["eligible_governed_bridge_candidate_count"] for c in CASE_ORDER})
    print("ALL EQUIVALENCE GATES PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
