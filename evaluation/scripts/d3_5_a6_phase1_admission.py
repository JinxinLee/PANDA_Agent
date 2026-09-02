"""D3.5-A6 Phase 1 — Bounded admission prototype & synthetic construction freeze.

Evaluation-only mechanical implementation of the finalized A6 Phase 0
preregistration (evaluation/d3_5_a6_bounded_rerank_admission_preregistration.json,
as repaired by Phase0-R1 and Phase0-R1-R1).  This script:

  * builds the derived A6 replay fixture from the frozen A5/R2 replay fixture,
    the persisted A5-R2 selectivity result, and the frozen normalized corpus
    (reranker_payload_registry + selector_replay_registry, explicitly
    separated per the Phase0-R1 contract);
  * constructs the deterministic BASELINE/K2/K3 arm pools for the six frozen
    development cases (18 formal arm-pool manifests);
  * freezes the exact 54-slot Phase-2 call plan without executing anything;
  * provides the production-parity deterministic post-rerank replay
    (production ``select_final_evidence`` is imported and reused unchanged);
  * provides the evaluator-side decision logic as pure functions (synthetic
    data only in Phase 1 — never run against real Phase-2 outcomes here).

Hard Phase-1 boundaries: no model call of any kind, ``PHASE1_SELECT_V2_RUNS
= 0`` (the persisted A5-R2 ``selectivity_only_graph_ordering`` is consumed
as-is and never re-merged with the bridge prefix), no PostgreSQL/Qdrant
writes, no D1/D2 changes, protected datasets untouched.

CLI (run with PYTHONPATH=src):
    python evaluation/scripts/d3_5_a6_phase1_admission.py \
        --project-root . --mode build-fixture   [--fixture-path PATH]
    python evaluation/scripts/d3_5_a6_phase1_admission.py \
        --project-root . --mode build-pools     [--fixture-path PATH]
    python evaluation/scripts/d3_5_a6_phase1_admission.py \
        --project-root . --mode build-call-plan [--fixture-path PATH] [--pools-path PATH]
    python evaluation/scripts/d3_5_a6_phase1_admission.py --project-root . --mode self-test
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from panda_agent.retrieval import _source_type_of, select_final_evidence

CASE_ORDER = ["g036", "g021", "n006", "g041", "g020", "n004"]
ARMS = ["BASELINE", "ADMISSION_K2", "ADMISSION_K3"]
RERANK_POOL_SIZE = 30
ADMISSION_BUDGETS = (2, 3)
GRAPH_CHANNEL_LIMIT = 20
DENOMINATOR_OFFSET = 60
WEIGHTS = {"exact": 2.0, "dense": 1.0, "sparse": 1.0, "paper": 1.15, "workflow": 1.2, "graph": 0.8}
FINAL_EVIDENCE_LIMIT = 12
RERANKER_REPETITIONS_PER_ARM_PER_CASE = 3
CYCLIC_SCHEDULE = {
    1: ["BASELINE", "ADMISSION_K2", "ADMISSION_K3"],
    2: ["ADMISSION_K2", "ADMISSION_K3", "BASELINE"],
    3: ["ADMISSION_K3", "BASELINE", "ADMISSION_K2"],
}

PARENT_FIXTURE = "evaluation/d3_5_downstream_replay_fixture.json"
PARENT_A5_R2_RESULT = "evaluation/d3_5_a5_r2_repaired_selectivity_revalidation.json"
PARENT_A6_PREREGISTRATION = "evaluation/d3_5_a6_bounded_rerank_admission_preregistration.json"
A2_RAW_RECORDS = "data/evaluation/runs/d3_5_a2_focused_20260901/records.jsonl"
FIXTURE_PATH = "evaluation/d3_5_a6_phase1_replay_fixture.json"
POOLS_PATH = "evaluation/d3_5_a6_phase1_pool_manifest.json"
CALL_PLAN_PATH = "evaluation/d3_5_a6_phase1_execution_manifest.json"

PASS_VERDICT = "PASS / BOUNDED_RERANK_ADMISSION_VALIDATED_FOR_DEVELOPMENT"
FAIL_VERDICT = "FAIL / BOUNDED_ADMISSION_CONSTRUCTION_OR_AUTHORITY_FAILED"
P_REGRESSION = "PARTIAL / ADMISSION_RECOVERY_WITH_CONTROL_REGRESSION"
P_POOL_PERTURBATION = "PARTIAL / POOL_PERTURBATION_ASSOCIATED_RECOVERY_WITHOUT_RESERVED_WITNESS"
P_UNSTABLE = "PARTIAL / ADMISSION_RECOVERY_NOT_STABLE_ACROSS_RERANKER_REPETITIONS"
P_NO_RECOVERY = "PARTIAL / ADMISSION_DID_NOT_VALIDATE_DOWNSTREAM_RECOVERY"
OUTCOME_VERDICTS = {PASS_VERDICT, P_REGRESSION, P_POOL_PERTURBATION, P_UNSTABLE, P_NO_RECOVERY}


# ---------------------------------------------------------------------------
# frozen fusion reconstruction (mirrors production traversal: exact -> dense ->
# sparse -> paper -> workflow -> graph, weight/(60+rank+1), stable sort)
# ---------------------------------------------------------------------------

def merge_ids_prefix(prefix: list[str], rows: list[str], limit: int) -> list[str]:
    """Exact semantic twin of the A5-R2 ``merge_ids`` (prefix fill + dedupe + limit)."""
    merged: list[str] = []
    seen: set[str] = set()
    for oid in [*prefix, *rows]:
        if oid in seen:
            continue
        seen.add(oid)
        merged.append(oid)
        if len(merged) >= limit:
            break
    return merged


def compute_fused_ordering(
    nongraph_channel_rankings: dict[str, list[str]], graph_channel: list[str]
) -> tuple[list[str], dict[str, float], dict[str, list[str]]]:
    """Deterministic RRF replay over the frozen channel orderings.

    ``nongraph_channel_rankings`` must preserve the frozen fixture key order
    (production builds rankings as exact -> dense -> sparse -> paper ->
    workflow -> graph); the graph channel is always traversed last.
    """
    scores: dict[str, float] = {}
    membership: dict[str, list[str]] = {}
    for channel, ids in nongraph_channel_rankings.items():
        weight = WEIGHTS[channel]
        for rank, oid in enumerate(ids):
            scores[oid] = scores.get(oid, 0.0) + weight / (DENOMINATOR_OFFSET + rank + 1)
            membership.setdefault(oid, []).append(channel)
    for rank, oid in enumerate(graph_channel):
        scores[oid] = scores.get(oid, 0.0) + WEIGHTS["graph"] / (DENOMINATOR_OFFSET + rank + 1)
        membership.setdefault(oid, []).append("graph")
    ordered = sorted(scores, key=scores.get, reverse=True)
    return ordered, scores, membership


# ---------------------------------------------------------------------------
# derived A6 replay fixture
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_a2_paper_page_hints(project_root: Path) -> dict[str, dict[str, list[int]]]:
    """Frozen plan ``paper_page_hints`` per case, read generically from the
    frozen A2 raw records; missing/null hints materialize as ``{}``."""
    records_path = project_root / A2_RAW_RECORDS
    hints: dict[str, dict[str, list[int]]] = {case: {} for case in CASE_ORDER}
    if not records_path.exists():
        return hints
    for line in records_path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        record = json.loads(line)
        if record.get("arm") != "STRUCTURED_BRIDGED":
            continue
        value = (record.get("plan_summary") or {}).get("paper_page_hints")
        if value:
            hints[record["case_id"]] = value
    return hints


def build_fixture(project_root: Path) -> dict[str, Any]:
    parent = _load_json(project_root / PARENT_FIXTURE)
    r2 = _load_json(project_root / PARENT_A5_R2_RESULT)
    manifest_id = parent["identity"]["source_manifest_sha256"]
    corpus_path = project_root / "data" / "normalized" / manifest_id / "knowledge_objects.jsonl"
    normalized: dict[str, dict[str, Any]] = {}
    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        if line:
            item = json.loads(line)
            normalized[item["object_id"]] = item
    paper_page_hints = _load_a2_paper_page_hints(project_root)

    cases: dict[str, Any] = {}
    graph_parity_receipts: list[dict[str, Any]] = []
    fusion_parity_receipts: list[dict[str, Any]] = []
    universe_registry_ids: list[str] = []
    seen_registry: set[str] = set()
    for case_id in CASE_ORDER:
        parent_case = parent["cases"][case_id]
        r2_case = r2["six_case_records"][case_id]
        channel_rankings = {
            key: value
            for key, value in parent_case["arms"]["STRUCTURED_BRIDGED"]["channel_rankings"].items()
            if key != "graph"
        }
        old_graph = parent_case["baseline_bridged_graph_ordering_recomputed"]
        unbridged = parent_case["unbridged_graph_ordering"]
        authoritative_graph = r2_case["selectivity_only_graph_ordering"]
        selected = r2_case["selected_object_ids"]

        merged = merge_ids_prefix(selected, unbridged, GRAPH_CHANNEL_LIMIT)
        graph_parity_receipts.append(
            {
                "case_id": case_id,
                "merge_ids_selected_unbridged_limit20": merged,
                "persisted_selectivity_only_graph_ordering": authoritative_graph,
                "parity": merged == authoritative_graph,
            }
        )

        old_ordered, _, _ = compute_fused_ordering(channel_rankings, old_graph)
        parent_full = [oid for oid, _ in parent_case["fusion_contract"]["baseline_fused_ordering_full"]]
        fusion_parity_receipts.append(
            {
                "case_id": case_id,
                "anchor": "parent baseline_fused_ordering_full (old-cap graph channel input)",
                "parity": old_ordered == parent_full,
            }
        )

        full_ordered, score_map, membership = compute_fused_ordering(channel_rankings, authoritative_graph)
        missing = [oid for oid in full_ordered if oid not in normalized]
        plan_fields = dict(parent_case["frozen_plan_fields"])
        # The A2 record compaction dropped empty list/dict plan fields; materialize
        # the generic empty defaults so the replay plan namespace is complete.
        plan_fields.setdefault("target_repositories", [])
        plan_fields.setdefault("resolved_versions", {})
        plan_fields.setdefault("symbols", [])
        plan_fields.setdefault("concepts", [])
        plan_fields.setdefault("required_source_types", [])
        plan_fields.setdefault("source_budgets", {})
        plan_fields.setdefault("paper_page_hints", paper_page_hints.get(case_id, {}))
        cases[case_id] = {
            "case_id": case_id,
            "question": parent_case["question"],
            "frozen_plan_fields": plan_fields,
            "nongraph_channel_rankings": channel_rankings,
            "exact_channel_ordering": channel_rankings.get("exact", []),
            "A6_BASELINE_GRAPH_CHANNEL_AUTHORITY": authoritative_graph,
            "unbridged_graph_ordering": unbridged,
            "v2_selected_bridge_order": selected,
            "selected_rank_keys": r2_case["selected_rank_keys"],
            "selected_bridge_origin_count": r2_case["number_of_origins_after"],
            "selected_bridge_per_origin_counts": r2_case["per_origin_attributed_counts"],
            "full_fused_ordering": [[oid, round(score_map[oid], 9)] for oid in full_ordered],
            "full_fused_object_count": len(full_ordered),
            "channel_membership": {oid: membership[oid] for oid in full_ordered},
            "post_rerank_replay_required_object_universe": list(full_ordered),
            "missing_selector_replay_object_ids": missing,
        }
        for oid in full_ordered:
            if oid not in seen_registry:
                seen_registry.add(oid)
                universe_registry_ids.append(oid)

    reranker_payload_registry: dict[str, dict[str, Any]] = {}
    selector_replay_registry: dict[str, dict[str, Any]] = {}
    for oid in universe_registry_ids:
        record = normalized[oid]
        reranker_payload_registry[oid] = {
            "object_id": oid,
            "title": record.get("title"),
            "source_id": record.get("source_id"),
            "text_payload_2000": (record.get("text") or "")[:2000],
        }
        selector_replay_registry[oid] = {
            "object_id": oid,
            "source_id": record.get("source_id"),
            "source_version_id": record.get("source_version_id"),
            "object_type": record.get("object_type"),
            "title": record.get("title"),
            "text": record.get("text") or "",
            "authority_level": record.get("authority_level"),
            "locator": record.get("locator") or {},
        }

    return {
        "schema_version": "1.0.0",
        "checkpoint": "D3.5-A6-PHASE1",
        "purpose": (
            "derived A6 replay fixture: complete reranker payload + selector replay "
            "surfaces for the six frozen development cases (mechanical, outcome-independent)"
        ),
        "identity": {
            "parent_fixture": PARENT_FIXTURE,
            "parent_fixture_schema": parent["fixture_schema_version"],
            "parent_A5_R2_result": PARENT_A5_R2_RESULT,
            "parent_A6_preregistration": PARENT_A6_PREREGISTRATION,
            "implementation_freeze_parent_head": _git_head(project_root),
            "frozen_case_order": CASE_ORDER,
            "normalized_corpus_manifest": manifest_id,
            "created_from_frozen_A2": True,
        },
        "fusion_contract": {
            "weights": WEIGHTS,
            "denominator_offset": DENOMINATOR_OFFSET,
            "graph_channel_limit": GRAPH_CHANNEL_LIMIT,
            "traversal_order": "frozen nongraph fixture key order, graph channel last",
        },
        "cases": cases,
        "reranker_payload_registry": reranker_payload_registry,
        "selector_replay_registry": selector_replay_registry,
        "builder_verification": {
            "graph_parity_receipts": graph_parity_receipts,
            "graph_parity": sum(1 for r in graph_parity_receipts if r["parity"]),
            "fusion_parity_receipts": fusion_parity_receipts,
            "fusion_parity_full_ordering": sum(1 for r in fusion_parity_receipts if r["parity"]),
            "universe_registry_ids_count": len(universe_registry_ids),
            "selector_replay_registry_count": len(selector_replay_registry),
            "reranker_payload_registry_count": len(reranker_payload_registry),
            "missing_selector_replay_object_ids": sorted(
                {oid for case in cases.values() for oid in case["missing_selector_replay_object_ids"]}
            ),
        },
    }


def _git_head(project_root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(project_root), capture_output=True, text=True, check=True
    )
    return completed.stdout.strip()


# ---------------------------------------------------------------------------
# deterministic arm-pool construction (BASELINE / ADMISSION_K2 / ADMISSION_K3)
# ---------------------------------------------------------------------------

def build_baseline_pool(full_fused_ordering: list[str]) -> list[str]:
    return list(full_fused_ordering)[: min(RERANK_POOL_SIZE, len(full_fused_ordering))]


def reservable_bridge(v2_selected_bridge_order: list[str], baseline_pool: list[str]) -> list[str]:
    baseline_ids = set(baseline_pool)
    return [oid for oid in v2_selected_bridge_order if oid not in baseline_ids]


def build_treatment_pool(baseline_pool: list[str], reservable: list[str], k: int) -> dict[str, Any]:
    """Frozen Phase-0 construction: reserve the first ``min(k, len(reservable))``
    candidates in frozen v2 order, displace exactly that many bottom baseline
    members (pure positional, bottom-first), keep surviving baseline candidates
    in their original fused order, append the reserved candidates in v2 order."""
    reserved = list(reservable[: min(k, len(reservable))])
    cut = len(baseline_pool) - len(reserved)
    surviving = list(baseline_pool[:cut])
    displaced = list(baseline_pool[cut:])
    pool = surviving + reserved
    return {
        "reserved_bridge_candidate_ids": reserved,
        "reserved_slot_count": len(reserved),
        "displaced_object_ids": displaced,
        "ordinary_rerank_candidates_displaced": len(displaced),
        "treatment_pool_object_ids": pool,
        "pool_size": len(pool),
    }


def build_case_pools(case_entry: dict[str, Any]) -> dict[str, Any]:
    baseline = build_baseline_pool([oid for oid, _ in case_entry["full_fused_ordering"]])
    overlap = [oid for oid in case_entry["v2_selected_bridge_order"] if oid in set(baseline)]
    reservable = reservable_bridge(case_entry["v2_selected_bridge_order"], baseline)
    rank_key_by_id = {k["candidate_object_id"]: k for k in case_entry["selected_rank_keys"]}
    arms: dict[str, Any] = {
        "BASELINE": {
            "arm": "BASELINE",
            "ordered_pool_object_ids": baseline,
            "pool_size": len(baseline),
            "baseline_overlap_bridge_ids": overlap,
            "reservable_bridge_ids": reservable,
            "reserved_bridge_candidate_ids": [],
            "reserved_slot_count": 0,
            "displaced_object_ids": [],
            "ordinary_rerank_candidates_displaced": 0,
        }
    }
    for k, arm in ((2, "ADMISSION_K2"), (3, "ADMISSION_K3")):
        built = build_treatment_pool(baseline, reservable, k)
        built["arm"] = arm
        built["ordered_pool_object_ids"] = built["treatment_pool_object_ids"]
        built["baseline_overlap_bridge_ids"] = overlap
        built["reservable_bridge_ids"] = reservable
        built["reserved_candidate_origin_ids"] = [
            rank_key_by_id[oid]["attributed_origin_id"] for oid in built["reserved_bridge_candidate_ids"]
        ]
        arms[arm] = built
    identity = lambda pool: list(pool)  # noqa: E731 - authoritative identity is the ordered ID list
    relations = {
        "K2_pool_equals_BASELINE": identity(arms["ADMISSION_K2"]["treatment_pool_object_ids"])
        == identity(baseline),
        "K3_pool_equals_BASELINE": identity(arms["ADMISSION_K3"]["treatment_pool_object_ids"])
        == identity(baseline),
        "K2_pool_equals_K3": identity(arms["ADMISSION_K2"]["treatment_pool_object_ids"])
        == identity(arms["ADMISSION_K3"]["treatment_pool_object_ids"]),
    }
    return {
        "case_id": case_entry["case_id"],
        "baseline_pool_object_ids": baseline,
        "arms": arms,
        "identical_pool_relations": relations,
        "origin_concentration_diagnostics": {
            "selected_bridge_origin_count": case_entry["selected_bridge_origin_count"],
            "selected_bridge_per_origin_counts": case_entry["selected_bridge_per_origin_counts"],
            "reserved_by_arm": {
                "ADMISSION_K2": per_arm_origin_summary(arms["ADMISSION_K2"]["reserved_candidate_origin_ids"]),
                "ADMISSION_K3": per_arm_origin_summary(arms["ADMISSION_K3"]["reserved_candidate_origin_ids"]),
            },
            "ordinary_rerank_candidates_displaced": {
                "ADMISSION_K2": arms["ADMISSION_K2"]["ordinary_rerank_candidates_displaced"],
                "ADMISSION_K3": arms["ADMISSION_K3"]["ordinary_rerank_candidates_displaced"],
            },
        },
    }


def _per_origin_counts(origin_ids: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for oid in origin_ids:
        counts[oid] = counts.get(oid, 0) + 1
    return counts


def per_arm_origin_summary(origin_ids: list[str]) -> dict[str, Any]:
    """Mechanical per-arm reserved-origin summary derived only from the arm's
    frozen reserved candidates and their frozen attributed origins
    (zero-reservation arms yield count 0 / empty table / empty list)."""
    return {
        "reserved_bridge_origin_count": len(set(origin_ids)),
        "reserved_bridge_per_origin_counts": _per_origin_counts(origin_ids),
        "reserved_candidate_origin_ids": list(origin_ids),
    }


def validate_pool(entry: dict[str, Any], baseline: list[str]) -> list[str]:
    problems: list[str] = []
    pool = entry["ordered_pool_object_ids"]
    if len(set(pool)) != len(pool):
        problems.append("duplicate_object_ids_in_pool")
    if entry["pool_size"] != len(pool) or entry["pool_size"] > RERANK_POOL_SIZE:
        problems.append("pool_size_violation")
    expected_displaced = entry["reserved_slot_count"]
    if len(entry["displaced_object_ids"]) != expected_displaced:
        problems.append("displacement_count_violation")
    if expected_displaced and entry["displaced_object_ids"] != baseline[-expected_displaced:]:
        problems.append("displacement_not_bottom_first")
    expected_pool = baseline[: len(baseline) - expected_displaced] + entry["reserved_bridge_candidate_ids"]
    if pool != expected_pool:
        problems.append("treatment_ordering_violation")
    if set(entry["reserved_bridge_candidate_ids"]) & set(baseline):
        problems.append("duplicate_admission_of_baseline_present_candidate")
    return problems


# ---------------------------------------------------------------------------
# production-parity deterministic post-rerank replay
# ---------------------------------------------------------------------------

def post_rerank_replay(
    reranked: list[str],
    full_fused_order: list[str],
    plan: SimpleNamespace,
    question_text: str,
    exact_channel_items: list[dict[str, Any]],
    payload_map: dict[str, dict[str, Any]],
    score_map: dict[str, float],
    channel_map: dict[str, list[str]],
    final_evidence_limit: int = FINAL_EVIDENCE_LIMIT,
) -> dict[str, Any]:
    """Deterministic replay of the production post-rerank stage.

    Mirrors ``src/panda_agent/retrieval.py`` (fallback merge, preferred-source
    logic, symbol_first, required_first, hinted_first, final dedupe) and calls
    the imported production ``select_final_evidence`` unchanged.
    """
    ordered = list(dict.fromkeys([*reranked, *full_fused_order]))
    preferred_sources = list(plan.target_repositories)
    lowered_question = question_text.casefold()
    if any(term in lowered_question for term in ("restgas", "off-ip", "event_poca", "poca", "displaced")):
        preferred_sources = ["restgas_determination", "pandaroot", "luminosityfit", *preferred_sources]
    elif "pandaroot" in lowered_question:
        preferred_sources = ["pandaroot", "restgas_determination", "luminosityfit", *preferred_sources]
    preferred_sources = list(dict.fromkeys(preferred_sources))
    source_rank = {source_id: rank for rank, source_id in enumerate(preferred_sources)}

    def symbol_order(value: str) -> tuple[int, int]:
        normalized = value.replace("\\", "/").lower()
        if plan.intent == "troubleshooting" and ("readme" in normalized or "running/" in normalized):
            return (0, 0)
        return (1, 0 if "/" in value or "." in value else 1)

    symbols = sorted(plan.symbols, key=symbol_order)
    symbol_first: list[str] = []
    for symbol in symbols:
        literal = symbol.replace("*", "").replace("?", "")
        matches = []
        for item in exact_channel_items:
            locator = item.get("locator") or {}
            if literal and (
                literal in (item.get("title") or "")
                or literal in (locator.get("symbol") or "")
                or literal in (locator.get("path") or "")
                or literal in (item.get("text") or "")
            ):
                matches.append(item)
        if matches:

            def match_priority(item: dict[str, Any]) -> tuple[int, int, int, str]:
                locator = item.get("locator") or {}
                path = (locator.get("path") or "").replace("\\", "/")
                exact_path = int(
                    bool(literal and (path == literal or ("/" in literal and path.endswith("/" + literal))))
                )
                page_level = int(item.get("object_type") in {"sphinx_page", "source_file", "readme_section"})
                return (source_rank.get(item.get("source_id"), 999), -exact_path, -page_level, item["object_id"])

            matches.sort(key=match_priority)
            symbol_first.append(matches[0]["object_id"])

    required_first: list[str] = []
    for required in plan.required_source_types:
        for oid in ordered:
            source_type = _source_type_of(payload_map[oid])
            if source_type == required or (required in {"workflow", "graph"} and required in channel_map[oid]):
                required_first.append(oid)
                break

    hinted_first: list[str] = []
    for oid in ordered:
        item = payload_map[oid]
        source_id = item.get("source_id")
        page = (item.get("locator") or {}).get("pdf_page")
        if source_id in plan.paper_page_hints and page is not None and int(page) in plan.paper_page_hints[source_id]:
            hinted_first.append(oid)

    ordered = list(dict.fromkeys([*hinted_first, *required_first, *symbol_first, *ordered]))
    ranked_object_ids = ordered[:30]
    selected, excluded, backfill_admissions = select_final_evidence(
        ordered,
        payload_map,
        score_map,
        channel_map,
        plan,
        final_evidence_limit,
        set(symbol_first),
    )
    return {
        "ordered_object_ids": ordered,
        "ranked_object_ids": ranked_object_ids,
        "evidence_object_ids": [item.object_id for item in selected],
        "excluded": excluded,
        "backfill_admissions": backfill_admissions,
    }


def replay_case_with_registry(
    case_entry: dict[str, Any], registry: dict[str, dict[str, Any]], reranked: list[str]
) -> dict[str, Any]:
    """Assemble the frozen replay inputs for one case and run the replay."""
    plan = SimpleNamespace(
        intent=case_entry["frozen_plan_fields"]["intent"],
        target_repositories=case_entry["frozen_plan_fields"]["target_repositories"],
        symbols=case_entry["frozen_plan_fields"]["symbols"],
        required_source_types=case_entry["frozen_plan_fields"]["required_source_types"],
        source_budgets=case_entry["frozen_plan_fields"]["source_budgets"],
        paper_page_hints=case_entry["frozen_plan_fields"]["paper_page_hints"],
    )
    payload_map = {oid: registry[oid] for oid in case_entry["post_rerank_replay_required_object_universe"]}
    full_order = [oid for oid, _ in case_entry["full_fused_ordering"]]
    score_map = {oid: score for oid, score in case_entry["full_fused_ordering"]}
    channel_map = dict(case_entry["channel_membership"])
    exact_items = [payload_map[oid] for oid in case_entry["exact_channel_ordering"]]
    return post_rerank_replay(
        reranked=reranked,
        full_fused_order=full_order,
        plan=plan,
        question_text=case_entry["question"]["query"],
        exact_channel_items=exact_items,
        payload_map=payload_map,
        score_map=score_map,
        channel_map=channel_map,
    )


def replay_case(case_entry: dict[str, Any], fixture: dict[str, Any], reranked: list[str]) -> dict[str, Any]:
    return replay_case_with_registry(case_entry, fixture["selector_replay_registry"], reranked)


# ---------------------------------------------------------------------------
# evaluator-side decision logic (pure functions; synthetic-only in Phase 1)
# ---------------------------------------------------------------------------

def retention_count(retained_per_repetition: list[bool]) -> int:
    return sum(1 for flag in retained_per_repetition if flag)


def stable_retained(retained_per_repetition: list[bool]) -> bool:
    return retention_count(retained_per_repetition) >= 2


def stable_lost(retained_per_repetition: list[bool]) -> bool:
    return retention_count(retained_per_repetition) <= 1


def material_control_regression(baseline_flags: list[bool], treatment_flags: list[bool]) -> bool:
    return retention_count(baseline_flags) >= 2 and retention_count(treatment_flags) <= 1


def compute_delta(
    applicable_groups: list[str],
    baseline_retention: dict[str, list[bool]],
    treatment_retention: dict[str, list[bool]],
) -> int:
    return sum(
        1
        for group in applicable_groups
        if stable_retained(treatment_retention[group]) and not stable_retained(baseline_retention[group])
    )


def compute_causal_delta(
    applicable_groups: list[str],
    baseline_retention: dict[str, list[bool]],
    treatment_retention: dict[str, list[bool]],
    stable_witness: dict[str, bool],
) -> int:
    """CAUSAL_DELTA_K: the DELTA_K subset whose groups also carry the stable
    actually-reserved required-candidate witness under treatment K."""
    delta_groups = [
        group
        for group in applicable_groups
        if stable_retained(treatment_retention[group]) and not stable_retained(baseline_retention[group])
    ]
    return sum(1 for group in delta_groups if stable_witness.get(group, False))


def mechanistic_safe_effective(causal_delta: int, regression_count: int) -> bool:
    return causal_delta > 0 and regression_count == 0


def select_budget(
    delta2: int, delta3: int, causal2: int, causal3: int, regression2: int, regression3: int
) -> int | None:
    """Frozen causal-safe K2/K3 selection hierarchy (smallest sufficient
    causally witnessed safe budget)."""
    mse2 = mechanistic_safe_effective(causal2, regression2)
    mse3 = mechanistic_safe_effective(causal3, regression3)
    if mse2 and mse3:
        return 3 if causal3 > causal2 else 2
    if mse2:
        return 2
    if mse3:
        return 3
    return None


def classify_unstable_recovery(
    applicable_groups: list[str],
    baseline_retention: dict[str, list[bool]],
    treatment_retention: dict[str, list[bool]],
) -> bool:
    """UNSTABLE_ADMISSION_RECOVERY: an applicable group retained in >= 1
    treatment repetition where the corresponding stable baseline state does not
    establish stable retention, without satisfying DELTA_K stable recovery
    (isolated reranker variance is never confused with stable treatment
    effect)."""
    for group in applicable_groups:
        base_stable = stable_retained(baseline_retention[group])
        treated = treatment_retention[group]
        if any(treated) and not base_stable and not stable_retained(treated):
            return True
    return False


def compute_verdict(
    delta2: int,
    delta3: int,
    causal2: int,
    causal3: int,
    regression2: int,
    regression3: int,
    unstable_recovery: bool,
    structural_fail: bool,
) -> str:
    """Frozen seven-level verdict precedence (total, non-overlapping)."""
    if structural_fail:
        return FAIL_VERDICT
    mse2 = mechanistic_safe_effective(causal2, regression2)
    mse3 = mechanistic_safe_effective(causal3, regression3)
    if mse2 or mse3:
        return PASS_VERDICT
    dpos = [k for k, d in ((2, delta2), (3, delta3)) if d > 0]
    if dpos and all((regression2 if k == 2 else regression3) > 0 for k in dpos):
        return P_REGRESSION
    safe = [k for k in (2, 3) if (regression2 if k == 2 else regression3) == 0]
    if any((delta2 if k == 2 else delta3) > 0 for k in safe) and not any(
        (causal2 if k == 2 else causal3) > 0 for k in safe
    ):
        return P_POOL_PERTURBATION
    if delta2 == 0 and delta3 == 0 and unstable_recovery:
        return P_UNSTABLE
    return P_NO_RECOVERY


def admission_applicable_bridge_groups(
    evaluator_matched_groups: dict[str, list[str]], reservable_ids: list[str]
) -> list[str]:
    """Evaluator-only classification (never a runtime input): a required
    evidence group is applicable iff the evaluator identifies at least one
    required candidate for it and at least one such candidate belongs to
    RESERVABLE_BRIDGE."""
    reservable = set(reservable_ids)
    return [
        group
        for group, candidates in evaluator_matched_groups.items()
        if candidates and any(candidate in reservable for candidate in candidates)
    ]


def stable_reserved_required_witness(
    witness_per_repetition: list[bool],
) -> bool:
    return sum(1 for flag in witness_per_repetition if flag) >= 2


# ---------------------------------------------------------------------------
# Phase-2 call plan (non-executing)
# ---------------------------------------------------------------------------

def resolve_model_contract(project_root: Path) -> dict[str, Any]:
    """Freeze the exact Phase-2 reranker configuration without any provider
    invocation (settings resolution + prompt/schema identity only)."""
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env")
    try:
        from panda_agent.llm.vertex import VertexSettings

        settings = VertexSettings.from_env()
        model_id = settings.generation_model
    except Exception as exc:  # noqa: BLE001 - surfaced as a BLOCKED state upstream
        return {"resolved": False, "error": f"{type(exc).__name__}: {exc}"}
    return {
        "resolved": True,
        "generation_model_id": model_id,
        "temperature": 0.0,
        "system_prompt_source": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT (imported unchanged)",
        "response_schema_contract": (
            '{"ranked_object_ids": [string...], "additionalProperties": false} with the '
            "schema enum restricted to the submitted pool member list"
        ),
        "payload_shape": [{"object_id": "…", "title": "…", "source_id": "…", "text": "text[:2000]"}],
        "provider_retry_policy": "existing vertex generate_json 3-attempt transient-retry loop, unchanged",
        "invocation": "NOT_CALLED_IN_PHASE1",
    }


def build_call_plan(fixture: dict[str, Any], pools: dict[str, Any], model_contract: dict[str, Any]) -> dict[str, Any]:
    registry = fixture["reranker_payload_registry"]
    entries: list[dict[str, Any]] = []
    index = 0
    for case_id in CASE_ORDER:
        case_pools = pools["cases"][case_id]
        for repetition in (1, 2, 3):
            for arm in CYCLIC_SCHEDULE[repetition]:
                index += 1
                pool_entry = case_pools["arms"][arm]
                pool_ids = pool_entry["ordered_pool_object_ids"]
                payload = [
                    {
                        "object_id": oid,
                        "title": registry[oid]["title"],
                        "source_id": registry[oid]["source_id"],
                        "text": registry[oid]["text_payload_2000"],
                    }
                    for oid in pool_ids
                ]
                entries.append(
                    {
                        "formal_call_index": index,
                        "case_id": case_id,
                        "repetition": repetition,
                        "arm": arm,
                        "ordered_pool_object_ids": pool_ids,
                        "ordered_reranker_payload": payload,
                        "pool_size": len(pool_ids),
                        "pool_identity": list(pool_ids),
                        "model_contract_reference": "model_configuration_contract (this manifest)",
                        "outcome_status": "NOT_EXECUTED",
                    }
                )
    return {
        "schema_version": "1.0.0",
        "checkpoint": "D3.5-A6-PHASE1",
        "purpose": "frozen 54-slot Phase-2 call plan (non-executing; outcome_status all NOT_EXECUTED)",
        "model_configuration_contract": model_contract,
        "execution_protocol": {
            "all_54_formal_calls_execute_first": True,
            "raw_ranked_object_ids_persisted_per_formal_slot": True,
            "no_evaluator_or_verdict_computation_until_all_54_slots_complete": True,
            "provider_internal_retries_not_formal_repetitions": True,
            "unrecoverable_formal_call_failure": (
                "record the formal slot as FAILED, mark Phase-2 execution incomplete, "
                "STOP before scientific evaluator/verdict computation; no ad hoc rerun, "
                "no repetition-count change"
            ),
            "identical_pool_variance_semantics": (
                "if a treatment pool identity equals the BASELINE pool identity, any "
                "separate reranker-output difference is RERANKER_VARIANCE_REFERENCE, not "
                "an admission effect; identical-pool slots are still executed (symmetric "
                "variance reference) and never collapsed"
            ),
        },
        "formal_call_count": len(entries),
        "entries": entries,
    }


# ---------------------------------------------------------------------------
# self-test / verification entry points
# ---------------------------------------------------------------------------

def run_self_tests(fixture: dict[str, Any]) -> dict[str, Any]:
    receipts: dict[str, Any] = {}
    receipts["graph_parity"] = fixture["builder_verification"]["graph_parity"]
    receipts["fusion_parity_full_ordering"] = fixture["builder_verification"]["fusion_parity_full_ordering"]
    receipts["missing_selector_replay_object_ids"] = fixture["builder_verification"]["missing_selector_replay_object_ids"]
    receipts["selector_replay_registry_count"] = fixture["builder_verification"]["selector_replay_registry_count"]

    # deterministic replay double-execution on real frozen traces with
    # fabricated model-free ranked sequences (identity / reverse / midpoint)
    determinism: list[dict[str, Any]] = []
    for case_id in CASE_ORDER:
        case_entry = fixture["cases"][case_id]
        pool = [oid for oid, _ in case_entry["full_fused_ordering"]][:30]
        for label, seq in (
            ("identity", list(pool)),
            ("reverse", list(reversed(pool))),
        ):
            first = replay_case(case_entry, fixture, seq)
            second = replay_case(case_entry, fixture, seq)
            determinism.append(
                {
                    "case_id": case_id,
                    "sequence": label,
                    "deterministic": first == second,
                    "evidence_count": len(first["evidence_object_ids"]),
                }
            )
    receipts["replay_determinism"] = determinism
    receipts["replay_deterministic_all"] = all(item["deterministic"] for item in determinism)
    return receipts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--mode",
        required=True,
        choices=["build-fixture", "build-pools", "build-call-plan", "self-test"],
    )
    parser.add_argument("--fixture-path", type=Path, default=None)
    parser.add_argument("--pools-path", type=Path, default=None)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    root = args.project_root.resolve()
    fixture_path = args.fixture_path or (root / FIXTURE_PATH)
    pools_path = args.pools_path or (root / POOLS_PATH)

    if args.mode == "build-fixture":
        fixture = build_fixture(root)
        fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(
            json.dumps(
                {
                    "fixture": str(fixture_path),
                    "graph_parity": fixture["builder_verification"]["graph_parity"],
                    "fusion_parity": fixture["builder_verification"]["fusion_parity_full_ordering"],
                    "registry_ids": fixture["builder_verification"]["universe_registry_ids_count"],
                    "missing": fixture["builder_verification"]["missing_selector_replay_object_ids"],
                    "per_case_universe": {
                        cid: c["full_fused_object_count"] for cid, c in fixture["cases"].items()
                    },
                }
            )
        )
    elif args.mode in {"build-pools", "build-call-plan"}:
        fixture = _load_json(fixture_path)
        pools = {
            "schema_version": "1.0.0",
            "checkpoint": "D3.5-A6-PHASE1",
            "formal_arm_pool_manifests": 18,
            "cases": {},
        }
        problems: list[list[str]] = []
        for case_id in CASE_ORDER:
            case_pools = build_case_pools(fixture["cases"][case_id])
            baseline = case_pools["baseline_pool_object_ids"]
            for arm in ARMS:
                problems.append(validate_pool(case_pools["arms"][arm], baseline))
            pools["cases"][case_id] = case_pools
        pools["pool_invariant_violations"] = [p for group in problems for p in group]
        if args.mode == "build-pools":
            pools_path.write_text(json.dumps(pools, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(
                json.dumps(
                    {
                        "pools": str(pools_path),
                        "manifests": 18,
                        "invariant_violations": pools["pool_invariant_violations"],
                        "identical_pool_relations": {
                            cid: pools["cases"][cid]["identical_pool_relations"] for cid in CASE_ORDER
                        },
                    }
                )
            )
        else:
            if pools_path.exists():
                pools = _load_json(pools_path)
            model_contract = resolve_model_contract(root)
            if not model_contract.get("resolved"):
                print(json.dumps({"BLOCKED": "RERANKER_CONFIGURATION_NOT_REPRODUCIBLE", "detail": model_contract}))
                sys.exit(2)
            plan = build_call_plan(fixture, pools, model_contract)
            (root / CALL_PLAN_PATH).write_text(
                json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
            )
            print(
                json.dumps(
                    {
                        "call_plan": str(root / CALL_PLAN_PATH),
                        "formal_call_count": plan["formal_call_count"],
                        "outcome_statuses": sorted({e["outcome_status"] for e in plan["entries"]}),
                        "model": model_contract["generation_model_id"],
                    }
                )
            )
    elif args.mode == "self-test":
        fixture = _load_json(fixture_path)
        print(json.dumps(run_self_tests(fixture), ensure_ascii=False))


if __name__ == "__main__":
    main()
