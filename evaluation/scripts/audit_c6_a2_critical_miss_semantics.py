"""C6-A2R1 — Critical-miss semantics audit and Gate-5 correction.

Static audit over the already-written C6-A2 receipts: recomputes hard Gate 5
("no new critical evidence miss") at critical evidence-GROUP identity level
(Gold required_evidence_groups[*].critical) instead of the original aggregate
critical-coverage decline, then rebuilds policy labels and intent-aware
eligibility that depend on Gate 5. Zero fusion/retrieval/model calls; the
authoritative inputs are the frozen receipts plus Gold v2.6.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from panda_agent.c4_sparse_evaluation import TOP_K  # noqa: E402
from panda_agent.evaluation import load_gold_dataset  # noqa: E402

A2_MANIFEST = PROJECT_ROOT / "evaluation" / "baselines" / "manifests" / "phase_c_c6_a2_frozen_fusion_policy_comparison_v1.json"
RECEIPTS = PROJECT_ROOT / "evaluation" / "baselines" / "replay" / "phase_c_c6_a2_policy_receipts_v1.jsonl"
COVERAGE = PROJECT_ROOT / "evaluation" / "baselines" / "manifests" / "phase_c_c6_a1r2_current_plan_candidate_coverage_v1.json"
CORRECTION = PROJECT_ROOT / "evaluation" / "baselines" / "manifests" / "phase_c_c6_a1r2_semantic_cohort_correction_v1.json"
GOLD = PROJECT_ROOT / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
AUDIT_OUT = PROJECT_ROOT / "evaluation" / "baselines" / "manifests" / "phase_c_c6_a2_critical_miss_semantics_audit_v1.json"

GLOBAL_ALT = ("P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY")
POLICY_IDS = {
    "P0_CURRENT": "c6.current.v1",
    "P1_RAW_DENSE_CENTERED": "c6.raw_dense_centered.v1",
    "P2_EXACT_HEAVY": "c6.exact_heavy.v1",
    "P3_SPARSE_HEAVY": "c6.sparse_heavy.v1",
    "P4_SEMANTIC_AUXILIARY_25": "c6.semantic_aux25.v1",
    "P5_SEMANTIC_EXPANSION_ONLY": "c6.semantic_expansion_only.v1",
}
GATE_5_OLD = "5 no new critical evidence miss"


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=PROJECT_ROOT
    ).stdout.strip()


def critical_group_delta(
    p0_group_first_ranks: dict,
    policy_group_first_ranks: dict,
    critical_group_ids: list[str],
    top_k: int,
) -> tuple[list[str], list[str]]:
    """Group-identity critical delta: newly lost and newly recovered groups."""
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


def main() -> None:
    receipts = [json.loads(l) for l in RECEIPTS.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(receipts) == 144
    a2 = json.loads(A2_MANIFEST.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    core = sorted(coverage["pre_capture_preregistration"]["core_capture_cohort"]["case_ids"])
    sem = list(correction["deterministic_semantic_cohort_order"]["ordered_ids"])

    dataset = load_gold_dataset(GOLD)
    gold = {q.id: q for q in dataset.questions}
    critical_by_case = {
        cid: [g.group_id for g in gold[cid].required_evidence_groups if g.critical]
        for cid in set(core) | set(sem)
    }
    receipt_by_key = {
        (r["scope"], r["case_id"], r["policy_id"]): r for r in receipts
    }

    def audit_policy(scope: str, cohort: list[str], key: str) -> dict:
        pid = POLICY_IDS[key]
        case_reports = []
        classification = {"SAME_PASS": 0, "SAME_FAIL": 0, "OLD_FALSE_NEGATIVE": [], "OLD_FALSE_POSITIVE": []}
        for cid in cohort:
            p0 = receipt_by_key[(scope, cid, POLICY_IDS["P0_CURRENT"])]
            pol = receipt_by_key[(scope, cid, pid)]
            crit = critical_by_case[cid]
            assert set(pol["group_first_ranks"]) >= set(crit)
            groups = []
            for gid in crit:
                p0_rank = p0["group_first_ranks"].get(gid)
                pol_rank = pol["group_first_ranks"].get(gid)
                p0_hit = p0_rank is not None and p0_rank <= TOP_K
                pol_hit = pol_rank is not None and pol_rank <= TOP_K
                if p0_hit and pol_hit:
                    status = "retained"
                elif p0_hit and not pol_hit:
                    status = "newly_lost"
                elif not p0_hit and pol_hit:
                    status = "newly_recovered"
                else:
                    status = "missed_by_both"
                groups.append({
                    "group_id": gid,
                    "p0_first_rank": p0_rank,
                    "policy_first_rank": pol_rank,
                    "p0_hit_at_20": p0_hit,
                    "policy_hit_at_20": pol_hit,
                    "status": status,
                })
            lost = [g["group_id"] for g in groups if g["status"] == "newly_lost"]
            recovered = [g["group_id"] for g in groups if g["status"] == "newly_recovered"]
            old_flag = bool(pol["new_critical_miss"])
            new_flag = len(lost) > 0
            if old_flag and new_flag:
                classification["SAME_FAIL"] += 1
            elif not old_flag and not new_flag:
                classification["SAME_PASS"] += 1
            elif not old_flag and new_flag:
                classification["OLD_FALSE_NEGATIVE"].append(cid)
            else:
                classification["OLD_FALSE_POSITIVE"].append(cid)
            case_reports.append({
                "scope": scope,
                "case_id": cid,
                "intent": pol["intent"],
                "policy_id": pid,
                "critical_group_ids": crit,
                "critical_groups": groups,
                "new_critical_group_miss_ids": lost,
                "new_critical_group_miss_count": len(lost),
                "recovered_critical_group_ids": recovered,
                "recovered_critical_group_count": len(recovered),
            })
        total_lost = sum(c["new_critical_group_miss_count"] for c in case_reports)
        total_recovered = sum(c["recovered_critical_group_count"] for c in case_reports)
        affected = [c for c in case_reports if c["new_critical_group_miss_count"] > 0]
        old_matrix = (
            a2["global_hard_gate_matrix"][key] if scope == "global"
            else a2["semantic_p4_results"]["gate_matrix"]
        )
        old_gate5 = old_matrix["gates"][GATE_5_OLD]
        corrected_gate5 = "PASS" if total_lost == 0 else "FAIL"
        corrected_gates = dict(old_matrix["gates"])
        corrected_gates[GATE_5_OLD] = corrected_gate5
        all_pass = all(v == "PASS" for v in corrected_gates.values())
        return {
            "policy_key": key,
            "policy_id": pid,
            "old_gate_5": old_gate5,
            "corrected_gate_5": corrected_gate5,
            "total_new_critical_group_misses": total_lost,
            "total_newly_recovered_critical_groups": total_recovered,
            "affected_cases": [
                {"case_id": c["case_id"], "lost_group_ids": c["new_critical_group_miss_ids"]}
                for c in affected
            ],
            "recovered_cases": [
                {"case_id": c["case_id"], "recovered_group_ids": c["recovered_critical_group_ids"]}
                for c in case_reports if c["recovered_critical_group_count"] > 0
            ],
            "old_vs_corrected_case_classification": classification,
            "corrected_gate_matrix": {"gates": corrected_gates, "ALL_HARD_GATES_PASS": all_pass},
            "case_audit": case_reports,
        }

    audits = {}
    for key in GLOBAL_ALT:
        audits[key] = audit_policy("global", core, key)
    audits["P4_SEMANTIC_AUXILIARY_25"] = audit_policy("semantic", sem, "P4_SEMANTIC_AUXILIARY_25")

    # --- corrected global labels and passing set ---
    corrected_labels = {}
    for key in GLOBAL_ALT:
        corrected_labels[key] = (
            "PASS_ALL_GATES" if audits[key]["corrected_gate_matrix"]["ALL_HARD_GATES_PASS"]
            else "FAIL_HARD_GATES"
        )
    corrected_passing = [
        key for key in GLOBAL_ALT
        if audits[key]["corrected_gate_matrix"]["ALL_HARD_GATES_PASS"]
    ]
    p4_label = (
        "PASS_ALL_GATES" if audits["P4_SEMANTIC_AUXILIARY_25"]["corrected_gate_matrix"]["ALL_HARD_GATES_PASS"]
        else "FAIL_HARD_GATES"
    )

    # --- intent-level critical audit and preference recomputation ---
    intent_diagnostics = a2["intent_diagnostics"]
    per_intent_metrics = intent_diagnostics["per_intent_metrics"]
    intent_critical = {}
    preferred_corrected = {}
    for intent, block in per_intent_metrics.items():
        if intent not in intent_diagnostics["sufficiently_represented_intents"]:
            continue
        miss_counts = {}
        for key in GLOBAL_ALT:
            counts = sum(
                c["new_critical_group_miss_count"]
                for c in audits[key]["case_audit"]
                if c["case_id"] in {r["case_id"] for r in receipts
                                    if r["scope"] == "global" and r["intent"] == intent}
            )
            miss_counts[key] = counts
        intent_critical[intent] = miss_counts
        p0m = block["metrics"]["P0_CURRENT"]
        eligible = ["P0_CURRENT"]
        for key in GLOBAL_ALT:
            m = block["metrics"][key]
            improves = (
                m["fused_recall_at_10"] > p0m["fused_recall_at_10"] + 1e-12
                or m["mrr"] > p0m["mrr"] + 1e-12
            )
            no_r20_loss = m["fused_recall_at_20"] >= p0m["fused_recall_at_20"] - 1e-12
            no_new_critical = miss_counts[key] == 0
            d = m["directions"]
            if improves and no_r20_loss and no_new_critical and d["positive_direction_count"] > d["negative_direction_count"]:
                eligible.append(key)
        preferred_corrected[intent] = sorted(
            eligible,
            key=lambda k: (
                -block["metrics"][k]["fused_recall_at_10"],
                -block["metrics"][k]["fused_recall_at_20"],
                -block["metrics"][k]["mrr"],
                k != "P0_CURRENT",
            ),
        )[0]

    distinct = {p for p in preferred_corrected.values() if p != "P0_CURRENT"}

    def block_of(intent: str) -> dict:
        return per_intent_metrics[intent]

    intent_counts = intent_diagnostics["intent_distribution_frozen_labels"]
    conditions = {
        "1_at_least_3_sufficient_intents": len(intent_diagnostics["sufficiently_represented_intents"]) >= 3,
        "2_each_sufficient_intent_ge_4_cases": all(
            intent_counts[i] >= 4 for i in intent_diagnostics["sufficiently_represented_intents"]
        ),
        "3_at_least_2_intents_different_preferred_families": (
            len(distinct) + (1 if "P0_CURRENT" in preferred_corrected.values() else 0) >= 2
            and len(set(preferred_corrected.values())) >= 2
        ),
        "4_preferred_improves_r10_or_mrr_without_r20_loss_or_critical_miss": all(
            preferred_corrected[i] == "P0_CURRENT"
            or intent_critical[i][preferred_corrected[i]] == 0
            for i in preferred_corrected
        ),
        "5_positive_gt_negative_within_intent": all(
            preferred_corrected[i] == "P0_CURRENT"
            or block_of(i)["metrics"][preferred_corrected[i]]["directions"]["positive_direction_count"]
            > block_of(i)["metrics"][preferred_corrected[i]]["directions"]["negative_direction_count"]
            for i in preferred_corrected
        ),
        "6_preference_from_preregistered_global_policies_only": all(
            p in {"P0_CURRENT", *GLOBAL_ALT} for p in preferred_corrected.values()
        ),
    }
    intent_aware_eligible = all(conditions.values())
    mapping_corrected = (
        {
            i: (preferred_corrected[i] if i in intent_diagnostics["sufficiently_represented_intents"] else "P0_CURRENT")
            for i in sorted(intent_counts)
        }
        if intent_aware_eligible
        else None
    )

    audit = {
        "schema_version": 1,
        "task": "C6-A2R1 critical-miss semantics audit and Gate-5 correction",
        "artifact_id": "phase_c_c6_a2_critical_miss_semantics_audit_v1",
        "phase": "C6",
        "recorded_on": datetime.now(timezone.utc).isoformat(),
        "source_head": git_head(),
        "audit_timing": "after A2 evaluation, before A3",
        "reason_for_audit": (
            "post-A2 review found Gate 5 was implemented as aggregate critical-coverage "
            "decline (policy critical_evidence_coverage < P0), which can miss a critical-group "
            "swap where coverage stays equal but a specific P0-hit critical group is lost"
        ),
        "references": {
            "a2_manifest": A2_MANIFEST.relative_to(PROJECT_ROOT).as_posix(),
            "a2_receipts": RECEIPTS.relative_to(PROJECT_ROOT).as_posix(),
            "gold_v2_6": GOLD.relative_to(PROJECT_ROOT).as_posix(),
        },
        "old_gate5_definition": "per-case policy critical_evidence_coverage < P0 critical_evidence_coverage (aggregate coverage decline)",
        "corrected_gate5_definition": (
            "per-case critical evidence-GROUP identity loss: a new critical miss exists iff "
            "Gold required_evidence_groups[*].critical group g has P0 group_first_rank <= TOP_K "
            "and policy group_first_rank None or > TOP_K; Gate 5 PASS iff the cohort total of "
            "new critical group misses is 0; recovered groups never cancel lost groups"
        ),
        "top_k": TOP_K,
        "critical_group_source": "gold_questions.yaml required_evidence_groups[*].critical (exact Gold group IDs)",
        "audited_policies": ["P1_RAW_DENSE_CENTERED", "P2_EXACT_HEAVY", "P3_SPARSE_HEAVY", "P4_SEMANTIC_AUXILIARY_25"],
        "p5_note": "P5 has no ordinary Gate-5 entry: its scored prefix is P0-identical on 8/8 cases",
        "policy_audits": {
            key: {k: v for k, v in audits[key].items() if k != "case_audit"}
            for key in audits
        },
        "case_level_audit_receipts": {
            key: audits[key]["case_audit"] for key in audits
        },
        "corrected_global_policy_labels": corrected_labels,
        "corrected_global_passing_policy_set": corrected_passing,
        "corrected_p4_label": p4_label,
        "corrected_intent_critical_group_miss_counts": intent_critical,
        "corrected_preferred_policy_by_intent": preferred_corrected,
        "corrected_intent_aware_conditions": conditions,
        "corrected_INTENT_AWARE_ELIGIBLE": intent_aware_eligible,
        "corrected_C6_INTENT_AWARE_V1": mapping_corrected,
        "semanticdense_conclusion_unchanged": True,
        "semanticdense_boundary_note": (
            "the SemanticDense meaningful-contribution result (N_sem=8, threshold 2, observed "
            "unique relevant case count 1 -> INSUFFICIENT / KEEP_DISABLED) is independent of "
            "Gate 5 and was not recalculated; P4 also independently fails Recall@20 vs P0"
        ),
        "yield_label_note": (
            "A1 freezes the metric name 'semantic unique relevant yield' but not a denominator "
            "formula; the A2 value 1/160 counts relevant / all semantic candidates (8x20), while "
            "relevant / semantic-unique candidates = 1/41; both are recorded descriptively and "
            "the meaningful-contribution gate uses unique relevant CASE count, not yield"
        ),
        "ranking_metrics_unchanged": True,
        "directional_counts_unchanged": True,
        "cohort_unchanged": True,
        "policy_definitions_unchanged": True,
        "replay_v2_unchanged": True,
        "no_fusion_rerun": True,
        "live_model_call_ledger": "all zero (static file reads only)",
        "a2_methodology_verdict_after_audit": "PASS",
        "critical_miss_semantics_audit": "PASS",
        "a3_execution_eligibility": "NEXT_ELIGIBLE / NOT_STARTED",
    }

    AUDIT_OUT.write_text(json.dumps(audit, indent=1), encoding="utf-8")

    # --- add the correction section to the original A2 manifest (history preserved) ---
    a2["critical_miss_semantics_correction"] = {
        "audit_artifact": AUDIT_OUT.relative_to(PROJECT_ROOT).as_posix(),
        "superseded_gate5_interpretation": audit["old_gate5_definition"],
        "corrected_gate5_interpretation": audit["corrected_gate5_definition"],
        "corrected_global_gate_matrices": {
            key: audits[key]["corrected_gate_matrix"] for key in GLOBAL_ALT
        },
        "corrected_p4_gate_matrix": audits["P4_SEMANTIC_AUXILIARY_25"]["corrected_gate_matrix"],
        "corrected_policy_result_labels": {**corrected_labels, "P4_SEMANTIC_AUXILIARY_25": p4_label},
        "corrected_global_passing_policy_set": corrected_passing,
        "corrected_preferred_policy_by_intent": preferred_corrected,
        "corrected_INTENT_AWARE_ELIGIBLE": intent_aware_eligible,
        "corrected_C6_INTENT_AWARE_V1": mapping_corrected,
        "old_vs_corrected_changed_any_gate_or_label": (
            corrected_labels != a2["global_policy_result_labels"]
            or p4_label != a2["semantic_p4_results"]["result_label"]
            or preferred_corrected != intent_diagnostics["preferred_policy_by_intent"]
        ),
        "historical_note": (
            "the original A2 implementation used the aggregate-coverage Gate-5 reading; that "
            "record is preserved above and superseded only for Gate 5 and its dependent labels"
        ),
        "authoritative_after_audit": True,
    }
    A2_MANIFEST.write_text(json.dumps(a2, indent=1, default=str), encoding="utf-8")

    print(json.dumps({
        "policy_gates": {
            key: {
                "old": audits[key]["old_gate_5"],
                "corrected": audits[key]["corrected_gate_5"],
                "total_new_misses": audits[key]["total_new_critical_group_misses"],
                "affected": [c["case_id"] for c in audits[key]["affected_cases"]],
                "recovered": [c["case_id"] for c in audits[key]["recovered_cases"]],
                "label": corrected_labels.get(key, p4_label),
            }
            for key in audits
        },
        "old_vs_corrected": {
            key: audits[key]["old_vs_corrected_case_classification"] for key in audits
        },
        "corrected_passing": corrected_passing,
        "p3_still_passes_all_gates": "P3_SPARSE_HEAVY" in corrected_passing,
        "intent_critical": intent_critical,
        "preferred_before": intent_diagnostics["preferred_policy_by_intent"],
        "preferred_after": preferred_corrected,
        "intent_aware_eligible": intent_aware_eligible,
    }, indent=1))


if __name__ == "__main__":
    main()
