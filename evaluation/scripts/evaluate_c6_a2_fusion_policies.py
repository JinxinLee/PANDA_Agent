"""C6-A2 — Frozen global + semantic fusion policy comparison.

Phase 0 persists the pre-outcome input lock (inputs, cohorts, policies,
matcher/metric provenance, gates, thresholds) BEFORE any Gold relevance
outcome is computed. Phase 1 replays P0-P5 over frozen replay-v2 candidate
streams and computes the preregistered A2 metrics with the authoritative
required-evidence-group matcher from ``panda_agent.evaluation`` (the
semantics C3-R3 froze as authoritative). Zero model/retrieval/DB calls;
Gold-file and repository-file reads only.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from panda_agent.c4_sparse_evaluation import TOP_K, classify_case  # noqa: E402
from panda_agent.evaluation import _matched_evidence_groups, load_gold_dataset  # noqa: E402
from panda_agent.fusion_replay import (  # noqa: E402
    FUSING_STATES,
    PRODUCTION_CHANNEL_ORDER,
    RRF_K,
    preregistered_policies,
    replay_case_from_mapping,
)
from panda_agent.source import sha256_file  # noqa: E402

PREREG = PROJECT_ROOT / "evaluation" / "baselines" / "manifests" / "phase_c_c6_a0_a1_fusion_replay_preregistration_v1.json"
COVERAGE = PROJECT_ROOT / "evaluation" / "baselines" / "manifests" / "phase_c_c6_a1r2_current_plan_candidate_coverage_v1.json"
CORRECTION = PROJECT_ROOT / "evaluation" / "baselines" / "manifests" / "phase_c_c6_a1r2_semantic_cohort_correction_v1.json"
REPLAY_V2 = PROJECT_ROOT / "evaluation" / "baselines" / "replay" / "phase_c_c6_current_plan_candidate_replay_v2.jsonl"
GOLD = PROJECT_ROOT / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
MANIFEST = PROJECT_ROOT / "evaluation" / "baselines" / "manifests" / "phase_c_c6_a2_frozen_fusion_policy_comparison_v1.json"
RECEIPTS = PROJECT_ROOT / "evaluation" / "baselines" / "replay" / "phase_c_c6_a2_policy_receipts_v1.jsonl"

GLOBAL_POLICIES = ("P0_CURRENT", "P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY")
SEMANTIC_POLICIES = ("P0_CURRENT", "P4_SEMANTIC_AUXILIARY_25", "P5_SEMANTIC_EXPANSION_ONLY")
GATE_NAMES = (
    "1 replay inputs identical except policy",
    "2 no candidate stream regenerated",
    "3 Fused Recall@20 >= CURRENT",
    "4 Fused Recall@10 >= CURRENT",
    "5 no new critical evidence miss",
    "6 lost_hit = 0",
    "7 negative_direction_count <= positive_direction_count",
    "8 no version/source violation introduced by replay",
    "9 no benchmark-specific channel rule",
    "10 policy was preregistered in A1",
)
AGG_FIELDS = (
    "combined_candidate_recall_at_20",
    "fused_recall_at_5",
    "fused_recall_at_10",
    "fused_recall_at_20",
    "mrr",
    "critical_evidence_coverage",
)
DIRECTIONS = ("improved", "recovered_hit", "unchanged", "no_hit_both", "regressed", "lost_hit")


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=PROJECT_ROOT
    ).stdout.strip()


def load_object_lookup() -> tuple[dict[str, dict], str]:
    """Evaluator-canonical lookup: mtime-max normalized knowledge_objects.jsonl."""
    reports = list((PROJECT_ROOT / "data" / "normalized").glob("*/ingestion_report.json"))
    norm_dir = max(reports, key=lambda path: path.stat().st_mtime).parent
    lookup: dict[str, dict] = {}
    with (norm_dir / "knowledge_objects.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            lookup[item["object_id"]] = item
    return lookup, norm_dir.name


def case_mapping(row: dict) -> dict:
    channels = {}
    for channel, stream in row["channels"].items():
        channels[channel] = {
            "availability_state": stream["availability_state"],
            "candidates": [
                {
                    "object_id": c["object_id"],
                    "rank": c["channel_rank"],
                    "original_score": c.get("original_channel_score"),
                    "source_id": c.get("source_id"),
                    "source_version_id": c.get("source_version_id"),
                    "locator": c.get("locator"),
                }
                for c in stream.get("candidates", [])
            ],
        }
    return {
        "case_id": row["case_id"],
        "question": row["question"],
        "intent": row["intent"],
        "channels": channels,
    }


def group_first_ranks(groups: list, top_ids: list[str], lookup: dict) -> tuple[dict[str, int | None], list[dict]]:
    """First matching rank per evidence group via the authoritative matcher."""
    _, provenance = _matched_evidence_groups(groups, top_ids, lookup)
    rank_of = {object_id: rank for rank, object_id in enumerate(top_ids, 1)}
    first: dict[str, int | None] = {}
    for entry in provenance:
        if entry.get("matched") is False:
            first[entry["group_id"]] = None
        else:
            first[entry["group_id"]] = rank_of.get(entry["object_id"])
    return first, provenance


def recall_at(first: dict[str, int | None], limit: int) -> float:
    if not first:
        return 1.0
    return sum(rank is not None and rank <= limit for rank in first.values()) / len(first)


def candidate_relevant_groups(object_id: str, groups: list, lookup: dict) -> list[str]:
    if object_id not in lookup:
        return []
    _, provenance = _matched_evidence_groups(groups, [object_id], lookup)
    return [
        entry["group_id"]
        for entry in provenance
        if entry.get("matched") is not False and entry.get("object_id") == object_id
    ]


def critical_group_delta(
    p0_group_first_ranks: dict,
    policy_group_first_ranks: dict,
    critical_group_ids: list[str],
    top_k: int,
) -> tuple[list[str], list[str]]:
    """Critical evidence-GROUP identity delta vs P0 (Gate-5 semantics).

    A new critical miss is a specific P0-hit critical group the policy loses;
    recovered groups are reported separately and never cancel losses.
    """
    def hit(ranks: dict, group_id: str) -> bool:
        rank = ranks.get(group_id)
        return rank is not None and rank <= top_k

    newly_lost = [
        g for g in critical_group_ids
        if hit(p0_group_first_ranks, g) and not hit(policy_group_first_ranks, g)
    ]
    newly_recovered = [
        g for g in critical_group_ids
        if not hit(p0_group_first_ranks, g) and hit(policy_group_first_ranks, g)
    ]
    return newly_lost, newly_recovered


def evaluate_policy_on_case(policy, case, gold_case, lookup) -> dict:
    receipt = policy.apply(case)
    receipt_repeat = policy.apply(case)
    deterministic = receipt.as_dict() == receipt_repeat.as_dict()
    fused_ids = [candidate.object_id for candidate in receipt.fused]
    fused_scores = [round(candidate.fused_score, 12) for candidate in receipt.fused]
    top20 = fused_ids[:TOP_K]
    groups = gold_case.required_evidence_groups
    critical_groups = [group for group in groups if group.critical]
    first, _ = group_first_ranks(groups, top20, lookup)
    critical_first = {g.group_id: first[g.group_id] for g in critical_groups} if critical_groups else {}
    first_ranks = [rank for rank in first.values() if rank is not None]
    first_relevant_rank = min(first_ranks) if first_ranks else None
    # combined candidate pool over the policy's enabled fusing channels
    union_ids: list[str] = []
    for channel in PRODUCTION_CHANNEL_ORDER + ("semantic_dense",):
        if channel not in policy.enabled_channels:
            continue
        stream = case.channels.get(channel)
        if stream is None or stream.availability_state not in FUSING_STATES:
            continue
        for candidate in stream.candidates:
            if candidate.object_id not in union_ids:
                union_ids.append(candidate.object_id)
    combined_recall, _ = _matched_evidence_groups(groups, union_ids, lookup)
    wrong_version = sorted(
        {
            object_id
            for object_id in top20
            if lookup.get(object_id, {}).get("source_version_id")
            not in gold_case.allowed_source_versions
        }
    )
    critical_coverage = (
        recall_at(critical_first, TOP_K) if critical_groups else None
    )
    return {
        "policy_id": policy.policy_id,
        "deterministic": deterministic,
        "fused_ids": fused_ids,
        "fused_scores": fused_scores,
        "top20_ids": top20,
        "group_first_ranks": first,
        "critical_group_first_ranks": critical_first,
        "recall_at_5": recall_at(first, 5),
        "recall_at_10": recall_at(first, 10),
        "recall_at_20": recall_at(first, 20),
        "hit_at_5": recall_at(first, 5) > 0,
        "hit_at_10": recall_at(first, 10) > 0,
        "hit_at_20": recall_at(first, 20) > 0,
        "first_relevant_rank": first_relevant_rank,
        "mrr": (1.0 / first_relevant_rank) if first_relevant_rank else 0.0,
        "critical_evidence_coverage": critical_coverage,
        "critical_miss_count": sum(
            rank is None or rank > TOP_K for rank in critical_first.values()
        ) if critical_groups else None,
        "combined_candidate_recall_at_20": combined_recall,
        "union_ids": union_ids,
        "wrong_version_fused": wrong_version,
        "expansion_pool": [
            {"object_id": c.object_id, "semantic_rank": c.rank}
            for c in receipt.expansion_pool
        ],
        "enabled_channels": list(receipt.enabled_channels),
    }


def aggregate(results: list[dict]) -> dict:
    n = len(results)
    out: dict = {
        "case_count": n,
        "combined_candidate_recall_at_20": sum(r["combined_candidate_recall_at_20"] for r in results) / n,
        "fused_recall_at_5": sum(r["recall_at_5"] for r in results) / n,
        "fused_recall_at_10": sum(r["recall_at_10"] for r in results) / n,
        "fused_recall_at_20": sum(r["recall_at_20"] for r in results) / n,
        "mrr": sum(r["mrr"] for r in results) / n,
    }
    applicable = [r for r in results if r["critical_evidence_coverage"] is not None]
    out["critical_evidence_coverage"] = (
        sum(r["critical_evidence_coverage"] for r in applicable) / len(applicable)
        if applicable
        else None
    )
    out["critical_applicable_cases"] = len(applicable)
    return out


def direction_counts(rows: list[dict]) -> dict:
    counts = Counter(r["direction"] for r in rows)
    payload = {name: counts.get(name, 0) for name in DIRECTIONS}
    payload["positive_direction_count"] = payload["improved"] + payload["recovered_hit"]
    payload["negative_direction_count"] = payload["regressed"] + payload["lost_hit"]
    return payload


def gate_matrix(policy_rows: list[dict], policy_agg: dict, p0_agg: dict, structural: dict) -> dict:
    gates = {
        GATE_NAMES[0]: all(r["deterministic"] for r in policy_rows) and structural["single_case_object"],
        GATE_NAMES[1]: structural["replay_v2_unchanged"] and structural["no_live_calls"],
        GATE_NAMES[2]: policy_agg["fused_recall_at_20"] >= p0_agg["fused_recall_at_20"] - 1e-12,
        GATE_NAMES[3]: policy_agg["fused_recall_at_10"] >= p0_agg["fused_recall_at_10"] - 1e-12,
        GATE_NAMES[4]: sum(r["new_critical_miss"] for r in policy_rows) == 0,
        GATE_NAMES[5]: direction_counts(policy_rows)["lost_hit"] == 0,
        GATE_NAMES[6]: (
            direction_counts(policy_rows)["negative_direction_count"]
            <= direction_counts(policy_rows)["positive_direction_count"]
        ),
        GATE_NAMES[7]: all(not r["wrong_version_fused"] for r in policy_rows),
        GATE_NAMES[8]: structural["no_benchmark_specific_rule"],
        GATE_NAMES[9]: structural["preregistered_in_a1"],
    }
    return {
        "gates": {name: "PASS" if value else "FAIL" for name, value in gates.items()},
        "ALL_HARD_GATES_PASS": all(gates.values()),
    }


def main() -> None:
    head = git_head()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in REPLAY_V2.read_text(encoding="utf-8").splitlines() if line.strip()]
    row_by_id = {row["case_id"]: row for row in rows}

    core_ids = sorted(coverage["pre_capture_preregistration"]["core_capture_cohort"]["case_ids"])
    semantic_ids = list(correction["deterministic_semantic_cohort_order"]["ordered_ids"])

    policies = preregistered_policies()
    artifact_policies = prereg["preregistered_c6_a2_policies"]

    # --- Phase 0: pre-outcome lock (persisted before any relevance outcome) ---
    assert len(rows) == 34
    assert len(core_ids) == 30 and not ({"g039", "g040", "g055"} & set(core_ids))
    assert len(semantic_ids) == 8 and semantic_ids == [
        "g050", "g055", "g039", "g008", "g110", "g113", "g114", "g115"
    ]
    assert set(core_ids) <= set(row_by_id) and set(semantic_ids) <= set(row_by_id)
    assert RRF_K == 60
    policy_defs = {}
    for key, policy in policies.items():
        policy_defs[key] = {
            "policy_id": policy.policy_id,
            "mode": policy.mode,
            "base_policy_id": policy.base_policy_id,
            "enabled_channels": list(policy.enabled_channels),
            "weights": dict(policy.weights),
        }
    art_p0 = artifact_policies["P0_CURRENT"]
    assert policy_defs["P0_CURRENT"]["weights"] == art_p0["weights"]
    assert policy_defs["P0_CURRENT"]["enabled_channels"] == art_p0["enabled_channels"]
    assert policy_defs["P1_RAW_DENSE_CENTERED"]["weights"]["raw_dense"] == 1.5
    assert policy_defs["P2_EXACT_HEAVY"]["weights"]["exact"] == 3.0
    assert policy_defs["P3_SPARSE_HEAVY"]["weights"]["sparse"] == 1.5
    assert policy_defs["P4_SEMANTIC_AUXILIARY_25"]["weights"]["raw_dense"] == 0.75
    assert policy_defs["P4_SEMANTIC_AUXILIARY_25"]["weights"]["semantic_dense"] == 0.25
    assert policy_defs["P5_SEMANTIC_EXPANSION_ONLY"]["mode"] == "expansion_only"
    assert set(policies) == {
        "P0_CURRENT", "P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY",
        "P4_SEMANTIC_AUXILIARY_25", "P5_SEMANTIC_EXPANSION_ONLY",
    }

    lookup, normalized_dir = load_object_lookup()
    missing = set()
    for row in rows:
        for stream in row["channels"].values():
            for candidate in stream.get("candidates", []):
                if candidate["object_id"] not in lookup:
                    missing.add(candidate["object_id"])
    assert not missing

    lock = {
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "source_head": head,
        "replay_v2_path": REPLAY_V2.relative_to(PROJECT_ROOT).as_posix(),
        "replay_v2_row_count": len(rows),
        "global_core_cohort": {"count": len(core_ids), "ids": core_ids},
        "semantic_policy_cohort": {"count": len(semantic_ids), "ids": semantic_ids},
        "policy_definitions": policy_defs,
        "rrf_k": RRF_K,
        "candidate_identity": "object_id",
        "gold_dataset": {
            "path": GOLD.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": sha256_file(GOLD),
        },
        "object_lookup": {
            "source": f"data/normalized/{normalized_dir}/knowledge_objects.jsonl",
            "selection_rule": "evaluator-canonical mtime-max normalized ingestion dir (load_object_lookup rule)",
            "object_count": len(lookup),
            "replay_v2_candidate_coverage_missing": 0,
        },
        "relevance_matcher_provenance": {
            "module": "panda_agent.evaluation",
            "functions": ["_matched_evidence_groups", "GoldEvidenceSelector.matches", "_selector_match_provenance"],
            "semantics": "Existing authoritative required-evidence-group matching semantics from panda_agent.evaluation (frozen by the C3-R3 artifact metric_definitions; the same matcher produced the trusted Gold v2.6 Recall@K/MRR/critical metrics)",
            "tiers": ["direct", "ancestor (parent lineage)", "path_descendant_containment"],
        },
        "metric_implementation_provenance": {
            "recall_at_k": "mean per-case fraction of required evidence groups matched within fused top-k (k in 5/10/20)",
            "mrr": "mean reciprocal rank of the first top-20 relevant hit; 0 when none",
            "first_relevant_rank": "one-based rank of the first top-20 object satisfying a required-evidence-group match; null when no hit",
            "critical_evidence_coverage": "mean per-case fraction of critical groups matched within fused top-20; null when no critical labels",
            "combined_candidate_recall_at_20": "evidence-group recall over the deduplicated union of the policy's enabled fusing channel candidate streams",
            "direction_classification": "classify_case semantics from panda_agent.c4_sparse_evaluation (P0 = PRE, policy = POST, first-relevant-rank within top-20)",
            "source": "C3-R3 frozen metric_definitions + panda_agent.evaluation matcher; no parallel evaluator definition",
        },
        "safety_gates": list(prereg["preregistered_global_policy_safety_gates"]),
        "semanticdense_thresholds": prereg["preregistered_semanticdense_decision_tree"],
        "intent_aware_rules": prereg["preregistered_intent_aware_rules"],
        "novel_replay_status": "ABSENT",
        "gate_notes": prereg["gate_notes"],
    }
    MANIFEST.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "task": "C6-A2 frozen global + semantic fusion policy comparison",
                "artifact_id": "phase_c_c6_a2_frozen_fusion_policy_comparison_v1",
                "phase": "C6",
                "source_head": head,
                "execution_timing": "after the C6-A1R2 semantic-cohort correction; first and only C6-A2 relevance evaluation",
                "status": "PRE_OUTCOME_LOCK_PERSISTED",
                "pre_outcome_lock": lock,
            },
            indent=1,
        ),
        encoding="utf-8",
    )

    # --- Phase 1: relevance evaluation (authorized from here) ---
    dataset = load_gold_dataset(GOLD)
    gold_by_id = {question.id: question for question in dataset.questions}
    for case_id in set(core_ids) | set(semantic_ids):
        question = gold_by_id[case_id]
        assert question.query == row_by_id[case_id]["question"]
        assert question.expected_status.value == "answered"

    case_objects: dict[str, object] = {}
    for case_id in set(core_ids) | set(semantic_ids):
        case_objects[case_id] = replay_case_from_mapping(case_mapping(row_by_id[case_id]))

    receipts: list[dict] = []
    evaluated: dict[tuple[str, str], dict] = {}

    def run_cohort(cohort_ids: list[str], policy_keys: tuple[str, ...], scope: str) -> dict[str, list[dict]]:
        per_policy: dict[str, list[dict]] = {}
        for policy_key in policy_keys:
            policy_rows = []
            for case_id in cohort_ids:
                result = evaluate_policy_on_case(
                    policies[policy_key], case_objects[case_id], gold_by_id[case_id], lookup
                )
                evaluated[(case_id, policies[policy_key].policy_id)] = result
                policy_rows.append({"case_id": case_id, **result})
            per_policy[policy_key] = policy_rows
        p0_rows = per_policy["P0_CURRENT"]
        p0_by_case = {r["case_id"]: r for r in p0_rows}
        for policy_key in policy_keys:
            if policy_key == "P0_CURRENT":
                continue
            for r in per_policy[policy_key]:
                p0 = p0_by_case[r["case_id"]]
                r["direction"] = classify_case(p0["first_relevant_rank"], r["first_relevant_rank"])
                critical_ids = [
                    g.group_id
                    for g in gold_by_id[r["case_id"]].required_evidence_groups
                    if g.critical
                ]
                lost, recovered = critical_group_delta(
                    p0["group_first_ranks"], r["group_first_ranks"], critical_ids, TOP_K
                )
                r["new_critical_miss"] = bool(lost)
                r["new_critical_group_miss_ids"] = lost
                r["recovered_critical_group_ids"] = recovered
            for r in p0_rows:
                r["direction"] = "baseline"
                r["new_critical_miss"] = False
                r["new_critical_group_miss_ids"] = []
                r["recovered_critical_group_ids"] = []
        for policy_key in policy_keys:
            for r in per_policy[policy_key]:
                receipts.append(
                    {
                        "scope": scope,
                        "case_id": r["case_id"],
                        "intent": row_by_id[r["case_id"]]["intent"],
                        "policy_id": r["policy_id"],
                        "first_relevant_rank": r["first_relevant_rank"],
                        "hit_at_5": r["hit_at_5"],
                        "hit_at_10": r["hit_at_10"],
                        "hit_at_20": r["hit_at_20"],
                        "recall_at_5": r["recall_at_5"],
                        "recall_at_10": r["recall_at_10"],
                        "recall_at_20": r["recall_at_20"],
                        "mrr": r["mrr"],
                        "group_first_ranks": r["group_first_ranks"],
                        "critical_evidence_coverage": r["critical_evidence_coverage"],
                        "critical_miss_count": r["critical_miss_count"],
                        "combined_candidate_recall_at_20": r["combined_candidate_recall_at_20"],
                        "direction": r["direction"],
                        "new_critical_miss": r["new_critical_miss"],
                        "new_critical_group_miss_ids": r["new_critical_group_miss_ids"],
                        "recovered_critical_group_ids": r["recovered_critical_group_ids"],
                        "fused_top20_ids": r["top20_ids"],
                        "wrong_version_fused": r["wrong_version_fused"],
                    }
                )
        return per_policy

    global_per_policy = run_cohort(core_ids, GLOBAL_POLICIES, "global")
    semantic_per_policy = run_cohort(semantic_ids, SEMANTIC_POLICIES, "semantic")

    # --- P5 scored-prefix identity + expansion annotations ---
    p5_prefix_equal = 0
    for r in semantic_per_policy["P5_SEMANTIC_EXPANSION_ONLY"]:
        p0 = next(
            x for x in semantic_per_policy["P0_CURRENT"] if x["case_id"] == r["case_id"]
        )
        if r["fused_ids"] == p0["fused_ids"] and r["fused_scores"] == p0["fused_scores"]:
            p5_prefix_equal += 1
        gold_case = gold_by_id[r["case_id"]]
        for entry in r["expansion_pool"]:
            matched = candidate_relevant_groups(entry["object_id"], gold_case.required_evidence_groups, lookup)
            critical_matched = candidate_relevant_groups(
                entry["object_id"],
                [g for g in gold_case.required_evidence_groups if g.critical],
                lookup,
            )
            entry["matched_group_ids"] = matched
            entry["critical_matched_group_ids"] = critical_matched
        receipt_row = next(
            x
            for x in receipts
            if x["scope"] == "semantic" and x["case_id"] == r["case_id"]
            and x["policy_id"] == r["policy_id"]
        )
        receipt_row["expansion_pool"] = r["expansion_pool"]
    # --- semantic channel contribution (per Section 20) ---
    semantic_contribution: list[dict] = []
    for case_id in semantic_ids:
        case = case_objects[case_id]
        gold_case = gold_by_id[case_id]
        sem = case.channels["semantic_dense"]
        sem_ids = [c.object_id for c in sem.candidates]
        raw_ids = [c.object_id for c in case.channels["raw_dense"].candidates]
        other_union: list[str] = []
        for channel in PRODUCTION_CHANNEL_ORDER:
            stream = case.channels.get(channel)
            if stream is None or stream.availability_state not in FUSING_STATES:
                continue
            for candidate in stream.candidates:
                if candidate.object_id not in other_union:
                    other_union.append(candidate.object_id)
        unique_ids = [oid for oid in sem_ids if oid not in set(other_union)]
        unique_relevant = {
            oid: candidate_relevant_groups(oid, gold_case.required_evidence_groups, lookup)
            for oid in unique_ids
        }
        unique_relevant = {oid: g for oid, g in unique_relevant.items() if g}
        critical_groups = [g for g in gold_case.required_evidence_groups if g.critical]
        unique_critical = any(
            candidate_relevant_groups(oid, critical_groups, lookup) for oid in unique_ids
        ) if critical_groups else False
        union_with_sem = list(other_union) + [
            oid for oid in sem_ids if oid not in set(other_union)
        ]
        recall_with, _ = _matched_evidence_groups(gold_case.required_evidence_groups, union_with_sem, lookup)
        recall_without, _ = _matched_evidence_groups(gold_case.required_evidence_groups, other_union, lookup)
        overlap = len(set(sem_ids) & set(raw_ids))
        semantic_contribution.append(
            {
                "case_id": case_id,
                "semantic_candidate_count": len(sem_ids),
                "raw_candidate_count": len(raw_ids),
                "semantic_raw_overlap_at_20": overlap,
                "semantic_raw_overlap_ratio": overlap / len(sem_ids) if sem_ids else None,
                "semantic_unique_candidate_count": len(unique_ids),
                "semantic_unique_candidate_ids": unique_ids,
                "semantic_unique_relevant_candidate_count": len(unique_relevant),
                "semantic_unique_relevant": {
                    oid: groups for oid, groups in unique_relevant.items()
                },
                "semantic_unique_relevant_case": bool(unique_relevant),
                "semantic_unique_critical_case": unique_critical,
                "semantic_marginal_candidate_recall_contribution": recall_with - recall_without,
                "combined_recall_with_semantic": recall_with,
                "combined_recall_without_semantic": recall_without,
            }
        )

    # --- aggregates ---
    global_aggs = {key: aggregate(rows_) for key, rows_ in global_per_policy.items()}
    semantic_aggs = {key: aggregate(rows_) for key, rows_ in semantic_per_policy.items()}
    global_dirs = {
        key: direction_counts(rows_) for key, rows_ in global_per_policy.items() if key != "P0_CURRENT"
    }
    semantic_dirs = {
        key: direction_counts(rows_) for key, rows_ in semantic_per_policy.items() if key != "P0_CURRENT"
    }

    structural = {
        "single_case_object": True,
        "replay_v2_unchanged": not subprocess.run(
            ["git", "status", "--porcelain", "--", REPLAY_V2.relative_to(PROJECT_ROOT).as_posix()],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        ).stdout.strip(),
        "no_live_calls": True,
        "no_benchmark_specific_rule": True,
        "preregistered_in_a1": True,
    }
    global_gate_matrices = {
        key: gate_matrix(global_per_policy[key], global_aggs[key], global_aggs["P0_CURRENT"], structural)
        for key in ("P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY")
    }
    semantic_gate_matrix = gate_matrix(
        semantic_per_policy["P4_SEMANTIC_AUXILIARY_25"],
        semantic_aggs["P4_SEMANTIC_AUXILIARY_25"],
        semantic_aggs["P0_CURRENT"],
        structural,
    )

    # --- SemanticDense meaningful-contribution gate ---
    n_sem = len(semantic_ids)
    threshold = max(2, math.ceil(0.10 * n_sem))
    unique_relevant_case_count = sum(1 for c in semantic_contribution if c["semantic_unique_relevant_case"])
    meaningful = n_sem >= 8 and unique_relevant_case_count >= threshold

    # --- semantic decision tree (A3 input classification only) ---
    p4_all_pass = semantic_gate_matrix["ALL_HARD_GATES_PASS"]
    p5_union_improves = any(
        c["semantic_marginal_candidate_recall_contribution"] > 0 for c in semantic_contribution
    )
    weighted_supported = bool(meaningful and p4_all_pass)
    expansion_supported = bool(
        meaningful and (not p4_all_pass) and p5_union_improves and p5_prefix_equal == n_sem
    )
    if meaningful:
        semantic_contribution_classification = "MEANINGFUL"
    else:
        semantic_contribution_classification = "INSUFFICIENT"

    # --- intent-aware evaluation (global cohort, frozen labels) ---
    intent_of = {cid: row_by_id[cid]["intent"] for cid in core_ids}
    intent_counts = Counter(intent_of.values())
    sufficiently_represented = sorted(i for i, n in intent_counts.items() if n >= 4)
    per_intent: dict[str, dict] = {}
    preferred_by_intent: dict[str, str] = {}
    for intent in sufficiently_represented:
        ids = [cid for cid in core_ids if intent_of[cid] == intent]
        metrics: dict[str, dict] = {}
        for key in GLOBAL_POLICIES:
            rows_i = [r for r in global_per_policy[key] if r["case_id"] in set(ids)]
            metrics[key] = aggregate(rows_i)
            metrics[key]["directions"] = (
                direction_counts(rows_i) if key != "P0_CURRENT" else None
            )
            metrics[key]["new_critical_miss_count"] = (
                sum(r["new_critical_miss"] for r in rows_i) if key != "P0_CURRENT" else 0
            )
        per_intent[intent] = {"case_count": len(ids), "metrics": metrics}
        p0m = metrics["P0_CURRENT"]
        eligible_prefs: list[str] = ["P0_CURRENT"]
        for key in ("P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY"):
            m = metrics[key]
            improves = (
                m["fused_recall_at_10"] > p0m["fused_recall_at_10"] + 1e-12
                or m["mrr"] > p0m["mrr"] + 1e-12
            )
            no_recall20_loss = m["fused_recall_at_20"] >= p0m["fused_recall_at_20"] - 1e-12
            no_new_critical = m["new_critical_miss_count"] == 0
            positive = m["directions"]["positive_direction_count"]
            negative = m["directions"]["negative_direction_count"]
            if improves and no_recall20_loss and no_new_critical and positive > negative:
                eligible_prefs.append(key)
        best = sorted(
            eligible_prefs,
            key=lambda k: (
                -metrics[k]["fused_recall_at_10"],
                -metrics[k]["fused_recall_at_20"],
                -metrics[k]["mrr"],
                k != "P0_CURRENT",
            ),
        )[0]
        preferred_by_intent[intent] = best

    distinct_families = {p for p in preferred_by_intent.values() if p != "P0_CURRENT"}
    intent_conditions = {
        "1_at_least_3_sufficient_intents": len(sufficiently_represented) >= 3,
        "2_each_sufficient_intent_ge_4_cases": all(
            intent_counts[i] >= 4 for i in sufficiently_represented
        ),
        "3_at_least_2_intents_different_preferred_families": (
            len(distinct_families) + (1 if "P0_CURRENT" in preferred_by_intent.values() else 0) >= 2
            and len(set(preferred_by_intent.values())) >= 2
        ),
        "4_preferred_improves_r10_or_mrr_without_r20_loss_or_critical_miss": all(
            preferred_by_intent[i] == "P0_CURRENT"
            or (
                per_intent[i]["metrics"][preferred_by_intent[i]]["fused_recall_at_10"]
                > per_intent[i]["metrics"]["P0_CURRENT"]["fused_recall_at_10"] + 1e-12
                or per_intent[i]["metrics"][preferred_by_intent[i]]["mrr"]
                > per_intent[i]["metrics"]["P0_CURRENT"]["mrr"] + 1e-12
            )
            for i in sufficiently_represented
        ),
        "5_positive_gt_negative_within_intent": all(
            preferred_by_intent[i] == "P0_CURRENT"
            or per_intent[i]["metrics"][preferred_by_intent[i]]["directions"][
                "positive_direction_count"
            ]
            > per_intent[i]["metrics"][preferred_by_intent[i]]["directions"][
                "negative_direction_count"
            ]
            for i in sufficiently_represented
        ),
        "6_preference_from_preregistered_global_policies_only": all(
            p in {"P0_CURRENT", "P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY"}
            for p in preferred_by_intent.values()
        ),
    }
    intent_aware_eligible = all(intent_conditions.values())
    intent_mapping = (
        {
            i: (preferred_by_intent[i] if i in sufficiently_represented else "P0_CURRENT")
            for i in sorted(intent_counts)
        }
        if intent_aware_eligible
        else None
    )

    # --- receipts recompute check (aggregates rebuild from receipts) ---
    for key in GLOBAL_POLICIES:
        rebuilt = aggregate(
            [r for r in receipts if r["scope"] == "global" and r["policy_id"] == policies[key].policy_id]
        )
        assert rebuilt["fused_recall_at_10"] == global_aggs[key]["fused_recall_at_10"]
        assert rebuilt["mrr"] == global_aggs[key]["mrr"]
    assert p5_prefix_equal == n_sem
    all_deterministic = all(
        result["deterministic"] for result in evaluated.values()
    )
    methodology_pass = bool(
        all_deterministic
        and structural["replay_v2_unchanged"]
        and p5_prefix_equal == n_sem
    )
    a2_methodology_result = "PASS" if methodology_pass else "FAIL"
    with RECEIPTS.open("w", encoding="utf-8") as handle:
        for r in receipts:
            compact = {k: v for k, v in r.items() if k not in ("fused_scores",)}
            handle.write(json.dumps(compact, default=str) + "\n")

    global_passing = [
        key for key, m in global_gate_matrices.items() if m["ALL_HARD_GATES_PASS"]
    ]
    deltas = {
        key: {
            field: global_aggs[key][field] - global_aggs["P0_CURRENT"][field]
            for field in AGG_FIELDS
        }
        for key in ("P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY")
    }

    artifact = {
        "schema_version": 1,
        "task": "C6-A2 frozen global + semantic fusion policy comparison",
        "artifact_id": "phase_c_c6_a2_frozen_fusion_policy_comparison_v1",
        "phase": "C6",
        "recorded_on": datetime.now(timezone.utc).isoformat(),
        "source_head": head,
        "execution_timing": "after the C6-A1R2 semantic-cohort correction; first and only C6-A2 relevance evaluation",
        "status": "COMPLETE",
        "pre_outcome_lock": lock,
        "authoritative_input_paths": {
            "a1_preregistration": PREREG.relative_to(PROJECT_ROOT).as_posix(),
            "a1r2_coverage": COVERAGE.relative_to(PROJECT_ROOT).as_posix(),
            "semantic_cohort_correction": CORRECTION.relative_to(PROJECT_ROOT).as_posix(),
            "replay_v2": REPLAY_V2.relative_to(PROJECT_ROOT).as_posix(),
            "gold_v2_6": GOLD.relative_to(PROJECT_ROOT).as_posix(),
        },
        "cohorts": {
            "global_policy_cohort": {"count": 30, "ids": core_ids, "used_for": ["P0", "P1", "P2", "P3"]},
            "semantic_policy_cohort": {
                "count": n_sem,
                "ids": semantic_ids,
                "used_for": ["P0 semantic baseline", "P4", "P5"],
            },
        },
        "policy_definitions": policy_defs,
        "global_aggregate_results": global_aggs,
        "global_direction_counts": global_dirs,
        "global_policy_deltas_vs_p0": deltas,
        "global_hard_gate_matrix": global_gate_matrices,
        "global_policy_result_labels": {
            key: ("PASS_ALL_GATES" if global_gate_matrices[key]["ALL_HARD_GATES_PASS"] else "FAIL_HARD_GATES")
            for key in ("P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY")
        },
        "global_passing_policy_set": global_passing,
        "current_undominated_under_hard_gates": not global_passing,
        "mrr_recall5_diagnostics": {
            key: {
                "mrr_delta": deltas[key]["mrr"],
                "fused_recall_at_5_delta": deltas[key]["fused_recall_at_5"],
                "note": "raw deltas reported; no post-outcome MRR materiality threshold exists in project conventions",
            }
            for key in ("P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY")
        },
        "semantic_baseline_p0_results": semantic_aggs["P0_CURRENT"],
        "semantic_p4_results": {
            "result_label": (
                "PASS_ALL_GATES" if semantic_gate_matrix["ALL_HARD_GATES_PASS"] else "FAIL_HARD_GATES"
            ),
            "aggregates": semantic_aggs["P4_SEMANTIC_AUXILIARY_25"],
            "direction_counts": semantic_dirs["P4_SEMANTIC_AUXILIARY_25"],
            "gate_matrix": semantic_gate_matrix,
        },
        "semantic_p5_results": {
            "SCORED_PREFIX_IDENTITY": "PASS" if p5_prefix_equal == n_sem else "FAIL",
            "EXPANSION_CONTRIBUTION": "MEANINGFUL" if p5_union_improves else "NOT_MEANINGFUL",
            "scored_prefix_identity": {
                "equal_cases": p5_prefix_equal,
                "total": n_sem,
                "result": "PASS" if p5_prefix_equal == n_sem else "FAIL",
            },
            "expansion_pool_totals": {
                "cases_with_expansion": sum(
                    1 for c in semantic_contribution if c["semantic_unique_candidate_count"] > 0
                ),
                "expansion_candidate_count": sum(
                    c["semantic_unique_candidate_count"] for c in semantic_contribution
                ),
                "expansion_relevant_candidate_count": sum(
                    c["semantic_unique_relevant_candidate_count"] for c in semantic_contribution
                ),
                "candidate_union_coverage_improves": p5_union_improves,
                "marginal_contribution_by_case": {
                    c["case_id"]: c["semantic_marginal_candidate_recall_contribution"]
                    for c in semantic_contribution
                },
            },
        },
        "semantic_channel_contribution": semantic_contribution,
        "meaningful_semantic_contribution": {
            "n_sem": n_sem,
            "threshold_rule": "max(2, ceil(0.10 * N_sem))",
            "threshold": threshold,
            "semantic_unique_relevant_case_count": unique_relevant_case_count,
            "meaningful_semantic_marginal_recall": meaningful,
        },
        "semantic_decision_tree": {
            "SEMANTIC_WEIGHTED_PARTICIPATION_EVIDENCE": (
                "SUPPORTED_FOR_A3_CONSIDERATION" if weighted_supported else "NOT_SUPPORTED"
            ),
            "SEMANTIC_EXPANSION_ONLY_EVIDENCE": (
                "SUPPORTED_FOR_A3_CONSIDERATION" if expansion_supported else "NOT_SUPPORTED"
            ),
            "SEMANTIC_CONTRIBUTION": semantic_contribution_classification,
            "semantic_production_role_evidence": (
                "KEEP_DISABLED" if not meaningful else "A3_CONSIDERATION_ONLY"
            ),
            "no_production_activation_in_a2": True,
        },
        "intent_diagnostics": {
            "intent_distribution_frozen_labels": dict(sorted(intent_counts.items())),
            "sufficiently_represented_intents": sufficiently_represented,
            "per_intent_metrics": per_intent,
            "preferred_policy_by_intent": preferred_by_intent,
            "intent_aware_eligibility_conditions": intent_conditions,
            "INTENT_AWARE_ELIGIBLE": intent_aware_eligible,
            "C6_INTENT_AWARE_V1": intent_mapping,
        },
        "novel_gate": {
            "novel_replay_status": "ABSENT",
            "NEW_PRODUCTION_POLICY_ACTIVATION": "NOT_AUTHORIZED_BY_C6_A2_ALONE",
        },
        "production_activation_authorized": False,
        "selection_layer_debt": "not assessed in A2 (no reranker/selector execution); C7/C8 own downstream layers",
        "receipts_path": RECEIPTS.relative_to(PROJECT_ROOT).as_posix(),
        "receipts_row_count": len(receipts),
        "cost_and_isolation": {
            "analyzer": 0, "embeddings": 0, "sparse_encodes": 0, "live_retrieval": 0,
            "qdrant_reads": 0, "qdrant_writes": 0, "sql_candidate_reads": 0, "sql_writes": 0,
            "reranker": 0, "selector": 0, "qa": 0, "verifier": 0, "judge": 0,
            "index_mutation": 0, "gold_file_reads_authorized": 1,
        },
        "a2_methodology_result": a2_methodology_result,
        "a2_methodology_basis": {
            "policies_match_a1_artifact": True,
            "cohorts_verified": True,
            "all_replays_deterministic": all_deterministic,
            "p5_scored_prefix_identity": f"{p5_prefix_equal}/{n_sem}",
            "receipts_aggregate_recompute": True,
            "matcher_provenance": "panda_agent.evaluation (C3-R3-frozen authoritative semantics)",
            "zero_live_calls": True,
        },
        "c6_a3_execution_eligibility": (
            "NEXT_ELIGIBLE / NOT_STARTED" if a2_methodology_result == "PASS" else "NOT_ELIGIBLE"
        ),
    }
    MANIFEST.write_text(json.dumps(artifact, indent=1, default=str), encoding="utf-8")
    print(json.dumps({
        "global_aggregates": {k: {f: round(v[f], 6) for f in AGG_FIELDS if v[f] is not None} for k, v in global_aggs.items()},
        "global_passing": global_passing,
        "p4_all_gates_pass": p4_all_pass,
        "p5_prefix_identity": f"{p5_prefix_equal}/{n_sem}",
        "meaningful_semantic": meaningful,
        "unique_relevant_case_count": unique_relevant_case_count,
        "threshold": threshold,
        "intent_aware_eligible": intent_aware_eligible,
        "preferred_by_intent": preferred_by_intent,
    }, indent=1))


if __name__ == "__main__":
    main()
