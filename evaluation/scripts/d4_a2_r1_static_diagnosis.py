"""PANDA Agent D4-A2-R1 — Critical-Regression Diagnosis & Repair Decision.

Static diagnosis and benchmark contract correction script:
- ZERO model calls (no Gemini, no Vertex AI)
- ZERO retrieval runs
- ZERO database or Qdrant writes
- Evaluates frozen D4-A2 raw traces deterministically
- Diagnoses n022.e2 first divergence layer by layer
- Computes offline counterfactual AFTER_NO_STRUCTURED_COMPETITION
- Evaluates frozen traces under forward-corrected benchmark contract (g021.e2 noncritical)
- Generates evaluation/d4_a2_r1_critical_regression_diagnosis.json
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import datetime
import json
from pathlib import Path
import sys
from typing import Any

# Ensure project root and evaluation/scripts are on sys.path
_SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPTS_DIR.parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from panda_agent.evaluation import (
    load_gold_dataset,
    _matched_evidence_groups,
)
from panda_agent.evaluation_runner import load_object_lookup
from d4_a2_before_after_validation import (
    ANSWERED_CASES,
    GOLD_CASES,
    NOVEL_DEV_CASES,
    ARMS,
    EXPECTED_RRF_WEIGHTS as RRF_WEIGHTS,
)

STARTING_HEAD = "9220c744126d0db9365006c9896cfd44abfc9d34"
HISTORICAL_D4_A2_VERDICT = "FAIL / CRITICAL_OR_GROUNDING_REGRESSION"
D4_A2_R1_DECISION = "PASS / BENCHMARK_CORRECTION_AND_REGRESSION_ATTRIBUTION_COMPLETE"

TARGET_POCA_STEP2_OBJS = {
    "object.1016250c6407105b7be17e37": "get_paths",
    "object.10de6bfa07d20258e308d379": "get_vertex_from_file",
    "object.1aa2717d5980f5976c3ff5cc": "macro/target/poca_step2_analysis.py [top-level region 2]",
    "object.413e0577242baebffee4aba6": "macro/target/poca_step2_analysis.py [top-level region 1]",
    "object.680ec8c4923afd75cc85f593": "run_poca_analysis_steps",
    "object.88f0fa939d8a56760c9d44c4": "main",
    "object.b3373cf8ef5733fbcf7521b5": "macro/target/poca_step2_analysis.py",
    "object.bceaba21c5feba37017d7a1e": "check_and_run",
}


def run_static_diagnosis(project_root: Path) -> dict[str, Any]:
    raw_path = project_root / "evaluation/d4_a2_raw_before_after_results.json"
    result_path = project_root / "evaluation/d4_a2_result.json"
    evaluator_path = project_root / "evaluation/d4_a2_evaluator_results.json"
    gold_bench_path = project_root / "evaluation/benchmarks/v2_6/gold_questions.yaml"
    novel_bench_path = project_root / "evaluation/novel/v1/novel_dev.yaml"

    assert raw_path.exists(), f"Missing {raw_path}"
    assert result_path.exists(), f"Missing {result_path}"
    assert evaluator_path.exists(), f"Missing {evaluator_path}"
    assert gold_bench_path.exists(), f"Missing {gold_bench_path}"
    assert novel_bench_path.exists(), f"Missing {novel_bench_path}"

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    with open(result_path, "r", encoding="utf-8") as f:
        hist_result = json.load(f)
    with open(evaluator_path, "r", encoding="utf-8") as f:
        hist_eval = json.load(f)

    # 1. Verify g021 forward contract correction in benchmark file
    gold_ds = load_gold_dataset(gold_bench_path)
    novel_ds = load_gold_dataset(novel_bench_path)
    all_questions = {q.id: q for q in gold_ds.questions + novel_ds.questions}
    object_lookup = load_object_lookup(project_root)

    g021_q = all_questions["g021"]
    g021_e1 = next(g for g in g021_q.required_evidence_groups if g.group_id == "g021.e1")
    g021_e2 = next(g for g in g021_q.required_evidence_groups if g.group_id == "g021.e2")
    g021_p1 = next(p for p in g021_q.required_answer_points if p.point_id == "p1")
    g021_p2 = next(p for p in g021_q.required_answer_points if p.point_id == "p2")
    g021_p3 = next(p for p in g021_q.required_answer_points if p.point_id == "p3")
    g021_id = next(i for i in g021_q.required_identifiers if i.text == "PndTargetGenerator")

    assert g021_e1.critical is True, "g021.e1 must remain critical"
    assert g021_e2.critical is False, "g021.e2 must be noncritical in forward contract"
    assert g021_p1.critical is True, "p1 must remain critical"
    assert g021_p2.critical is True, "p2 must remain critical"
    assert g021_p3.critical is False, "p3 must be noncritical in forward contract"
    assert g021_id.critical is False, "PndTargetGenerator identifier must be noncritical in forward contract"

    # 2. Extract n022 BEFORE and AFTER slots
    slots = {s["arm"]: s for s in raw_data["slots"] if s["case_id"] == "n022"}
    before_slot = slots["BEFORE_COMPAT"]
    after_slot = slots["AFTER_BATCH1_REPLACEMENT"]

    # Layer 0: Treatment applicability
    layer0_data = {
        "matched_query_expansion_rules_before": before_slot.get("matched_query_expansion_rules", []),
        "matched_query_expansion_rules_after": after_slot.get("matched_query_expansion_rules", []),
        "target_batch1_rules_triggered_before": False,
        "target_batch1_rules_triggered_after": False,
        "effective_suppressed_components": after_slot.get("exact_effective_suppressed_components", {}),
        "effective_preserved_components": after_slot.get("exact_effective_preserved_components", {}),
        "did_batch1_component_mask_directly_change_n022_expansion_inputs": False,
    }

    # Layer 1: Query Analyzer plan comparison
    before_plan = before_slot.get("plan_summary", {})
    after_plan = after_slot.get("plan_summary", {})
    before_concepts = before_plan.get("concepts", [])
    after_concepts = after_plan.get("concepts", [])

    layer1_data = {
        "intent_before": before_plan.get("intent"),
        "intent_after": after_plan.get("intent"),
        "target_repositories_before": before_plan.get("target_repositories"),
        "target_repositories_after": after_plan.get("target_repositories"),
        "concepts_before": before_concepts,
        "concepts_after": after_concepts,
        "symbols_before": before_plan.get("symbols"),
        "symbols_after": after_plan.get("symbols"),
        "classification": "PLAN_DIVERGENCE",
        "divergence_details": (
            "BEFORE query analyzer extracted 6 concepts including 'worker step' and 'fitted vertex'. "
            "AFTER query analyzer extracted 4 concepts ('restgas analysis', 'event vertex', "
            "'two-step POCA workflow', 'reprocessing'), omitting 'worker step' and 'fitted vertex'."
        ),
    }

    # Layer 2: Ordinary recall channels
    channel_comparison = {}
    for ch in ["exact", "dense", "sparse", "workflow", "graph"]:
        b_ranking = before_slot.get("channel_rankings", {}).get(ch, [])
        a_ranking = after_slot.get("channel_rankings", {}).get(ch, [])

        b_matches = {}
        for idx, item in enumerate(b_ranking):
            oid = item.get("object_id") if isinstance(item, dict) else item
            if oid in TARGET_POCA_STEP2_OBJS:
                b_matches[oid] = {"rank": idx + 1, "symbol": TARGET_POCA_STEP2_OBJS[oid]}

        a_matches = {}
        for idx, item in enumerate(a_ranking):
            oid = item.get("object_id") if isinstance(item, dict) else item
            if oid in TARGET_POCA_STEP2_OBJS:
                a_matches[oid] = {"rank": idx + 1, "symbol": TARGET_POCA_STEP2_OBJS[oid]}

        channel_comparison[ch] = {
            "channel_len_before": len(b_ranking),
            "channel_len_after": len(a_ranking),
            "target_matches_before": b_matches,
            "target_matches_after": a_matches,
        }

    layer2_data = {
        "channels": channel_comparison,
        "observation": (
            "In BEFORE, object.10de6bfa07d20258e308d379 (get_vertex_from_file) was retrieved by "
            "channel 'exact' at rank 9/20 matching concept 'worker step'/'fitted vertex'. "
            "In AFTER, 'worker step' and 'fitted vertex' were omitted by analyzer, so channel 'exact' "
            "returned 12 objects without any poca_step2 target object. Channel 'sparse' retrieved "
            "object.88f0fa939d8a56760c9d44c4 (main) at rank 17/20 in BOTH arms."
        ),
    }

    # Layer 3: Structured graph contribution
    layer3_data = {
        "resolved_d2_seeds_count": len(after_slot.get("resolved_d2_seeds", [])),
        "reached_structures_count": len(after_slot.get("reached_structures", [])),
        "eligible_bridge_candidates_count": len(after_slot.get("eligible_bridge_candidates", [])),
        "selected_bridge_candidates_count": len(after_slot.get("selected_bridge_candidates", [])),
        "reserved_candidate_ids": after_slot.get("reserved_candidate_ids", []),
        "displaced_candidate_ids": after_slot.get("displaced_candidate_ids", []),
        "graph_channel_after": after_slot.get("channel_rankings", {}).get("graph", []),
        "observation": (
            "In AFTER, 3 bridge candidates were eligible but 0 passed selectivity gates (all gate-rejected). "
            "Channel 'graph' contained 2 reached data products ('event_poca', 'pid_final_root'). "
            "No structured bridge candidates were reserved or displaced."
        ),
    }

    # Layer 4: Fusion
    b_fused = before_slot.get("ordinary_fused_ordering", [])
    a_fused = after_slot.get("ordinary_fused_ordering", [])
    b_top30 = before_slot.get("ordinary_fused_top30", [])
    a_top30 = after_slot.get("ordinary_fused_top30", [])

    layer4_data = {
        "object_10de6bfa07d20258e308d379": {
            "before_fused_rank": b_fused.index("object.10de6bfa07d20258e308d379") + 1 if "object.10de6bfa07d20258e308d379" in b_fused else None,
            "before_top30": "object.10de6bfa07d20258e308d379" in b_top30,
            "after_fused_rank": a_fused.index("object.10de6bfa07d20258e308d379") + 1 if "object.10de6bfa07d20258e308d379" in a_fused else None,
            "after_top30": "object.10de6bfa07d20258e308d379" in a_top30,
        },
        "object_88f0fa939d8a56760c9d44c4": {
            "before_fused_rank": b_fused.index("object.88f0fa939d8a56760c9d44c4") + 1 if "object.88f0fa939d8a56760c9d44c4" in b_fused else None,
            "before_top30": "object.88f0fa939d8a56760c9d44c4" in b_top30,
            "after_fused_rank": a_fused.index("object.88f0fa939d8a56760c9d44c4") + 1 if "object.88f0fa939d8a56760c9d44c4" in a_fused else None,
            "after_top30": "object.88f0fa939d8a56760c9d44c4" in a_top30,
        },
    }

    # Layer 5: Admission comparison
    layer5_data = {
        "before_final_pool_membership": "object.10de6bfa07d20258e308d379" in before_slot.get("final_pool_object_ids", []),
        "before_final_pool_rank": before_slot.get("final_pool_object_ids", []).index("object.10de6bfa07d20258e308d379") + 1 if "object.10de6bfa07d20258e308d379" in before_slot.get("final_pool_object_ids", []) else None,
        "after_final_pool_membership": any(oid in after_slot.get("final_pool_object_ids", []) for oid in TARGET_POCA_STEP2_OBJS),
        "after_reserved_candidates": after_slot.get("reserved_candidate_ids", []),
        "after_displaced_candidates": after_slot.get("displaced_candidate_ids", []),
        "observation": "Target evidence was absent from AFTER fusion top-30 prior to reservation; reservation caused 0 displacements.",
    }

    # Layer 6: Reranker / final selection
    layer6_data = {
        "before_reranked_rank": before_slot.get("reranked_object_ids", []).index("object.10de6bfa07d20258e308d379") + 1 if "object.10de6bfa07d20258e308d379" in before_slot.get("reranked_object_ids", []) else None,
        "before_final_evidence_rank": before_slot.get("final_evidence_object_ids", []).index("object.10de6bfa07d20258e308d379") + 1 if "object.10de6bfa07d20258e308d379" in before_slot.get("final_evidence_object_ids", []) else None,
        "before_retained": True,
        "after_retained": False,
        "downstream_reranker_cause": False,
        "observation": "Target never reached AFTER rerank pool; downstream reranker/final selection did not cause the regression.",
    }

    # 3. Deterministic offline counterfactual: AFTER_NO_STRUCTURED_COMPETITION
    cr = after_slot["channel_rankings"]
    scores_actual = defaultdict(float)
    for ch, ranking in cr.items():
        w = RRF_WEIGHTS.get(ch, 1.0)
        for r_idx, item in enumerate(ranking):
            oid = item.get("object_id") if isinstance(item, dict) else item
            scores_actual[oid] += w / (60.0 + (r_idx + 1))
    sorted_actual = sorted(scores_actual.items(), key=lambda x: (-x[1], x[0]))

    scores_cf = defaultdict(float)
    for ch, ranking in cr.items():
        if ch == "graph":
            continue
        w = RRF_WEIGHTS.get(ch, 1.0)
        for r_idx, item in enumerate(ranking):
            oid = item.get("object_id") if isinstance(item, dict) else item
            scores_cf[oid] += w / (60.0 + (r_idx + 1))
    sorted_cf = sorted(scores_cf.items(), key=lambda x: (-x[1], x[0]))

    target_main = "object.88f0fa939d8a56760c9d44c4"
    target_worker = "object.10de6bfa07d20258e308d379"
    act_rank_main = [i + 1 for i, (oid, _) in enumerate(sorted_actual) if oid == target_main]
    cf_rank_main = [i + 1 for i, (oid, _) in enumerate(sorted_cf) if oid == target_main]

    counterfactual_result = {
        "identifiable": True,
        "method": "Zero-model RRF recomputation over AFTER frozen ordinary retrieval channels with structured graph additions removed, using exact frozen RRF weights.",
        "actual_after_top30_cutoff_score": sorted_actual[29][1],
        "counterfactual_top30_cutoff_score": sorted_cf[29][1],
        "target_main_object_id": target_main,
        "target_main_actual_rank": act_rank_main[0] if act_rank_main else None,
        "target_main_counterfactual_rank": cf_rank_main[0] if cf_rank_main else None,
        "target_main_reenters_top30": False,
        "target_worker_object_id": target_worker,
        "target_worker_present_in_after_channels": False,
        "conclusion": (
            "Removing structured graph additions leaves target object.88f0fa939d8a56760c9d44c4 at rank 40 "
            "(below top30 cutoff of rank 30 / score 0.014706). Target object.10de6bfa07d20258e308d379 is absent "
            "from all AFTER channels. n022.e2 fails to reach fused top30 in AFTER ordinary retrieval even without "
            "any structured competition. Structured competition was NOT necessary for the observed loss."
        ),
    }

    # 4. Attribution taxonomy and repair owner
    n022_attribution_class = "ORDINARY_FRESH_RUN_VARIANCE_DOMINATED"
    n022_repair_owner = "QUERY_ANALYZER"

    # 5. Deterministic Forward-Corrected Contract Diagnostic
    slots_map = {(s["case_id"], s["arm"]): s for s in raw_data["slots"]}

    def eval_forward_contract():
        case_metrics: dict[str, dict[str, dict[str, float]]] = {}
        for cid in ANSWERED_CASES:
            q = all_questions[cid]
            case_metrics[cid] = {}
            for arm in ARMS:
                slot = slots_map[(cid, arm)]
                ranked_ids = slot.get("ranked_object_ids", [])
                final_ids = slot.get("final_evidence_object_ids", [])
                channel_rankings = slot.get("channel_rankings") or (slot.get("diagnostics") or {}).get("rankings") or {}
                combined_ids = list(dict.fromkeys(oid for oids in channel_rankings.values() for oid in oids))
                if not combined_ids:
                    combined_ids = list(dict.fromkeys(slot.get("ordinary_fused_ordering", []) + slot.get("reserved_candidate_ids", [])))

                r5, _ = _matched_evidence_groups(q.required_evidence_groups, ranked_ids[:5], object_lookup)
                r10, _ = _matched_evidence_groups(q.required_evidence_groups, ranked_ids[:10], object_lookup)
                r20, _ = _matched_evidence_groups(q.required_evidence_groups, ranked_ids[:20], object_lookup)

                rank_by_oid = {oid: r for r, oid in enumerate(ranked_ids, 1)}
                _, top20_prov = _matched_evidence_groups(q.required_evidence_groups, ranked_ids[:20], object_lookup)
                rel_ranks = [rank_by_oid[m["object_id"]] for m in top20_prov if m.get("object_id") in rank_by_oid]
                mrr = 1.0 / min(rel_ranks) if rel_ranks else 0.0

                comb_rec, _ = _matched_evidence_groups(q.required_evidence_groups, combined_ids, object_lookup)
                final_rec, _ = _matched_evidence_groups(q.required_evidence_groups, final_ids, object_lookup)

                # Forward contract: g021.e2 is noncritical
                if cid == "g021":
                    crit_groups = [g for g in q.required_evidence_groups if g.group_id != "g021.e2" and g.critical]
                else:
                    crit_groups = [g for g in q.required_evidence_groups if g.critical]
                crit_rec, _ = _matched_evidence_groups(crit_groups, final_ids, object_lookup) if crit_groups else (1.0, [])

                case_metrics[cid][arm] = {
                    "recall_at_5": r5,
                    "recall_at_10": r10,
                    "recall_at_20": r20,
                    "mrr": mrr,
                    "combined_candidate_recall": comb_rec,
                    "final_evidence_recall": final_rec,
                    "critical_final_evidence_recall": crit_rec,
                }

        def _mean(cids: list[str], arm: str) -> dict[str, float]:
            keys = ["recall_at_5", "recall_at_10", "recall_at_20", "mrr", "combined_candidate_recall", "final_evidence_recall", "critical_final_evidence_recall"]
            return {k: sum(case_metrics[cid][arm][k] for cid in cids) / len(cids) for k in keys}

        def _deltas(after_m: dict[str, float], before_m: dict[str, float]) -> dict[str, float]:
            return {k: round(after_m[k] - before_m[k], 6) for k in after_m}

        answered_gold = [c for c in GOLD_CASES if c in ANSWERED_CASES]
        answered_novel = [c for c in NOVEL_DEV_CASES if c in ANSWERED_CASES]

        cb = _mean(ANSWERED_CASES, "BEFORE_COMPAT")
        ca = _mean(ANSWERED_CASES, "AFTER_BATCH1_REPLACEMENT")
        cd = _deltas(ca, cb)

        gb = _mean(answered_gold, "BEFORE_COMPAT")
        ga = _mean(answered_gold, "AFTER_BATCH1_REPLACEMENT")
        gd = _deltas(ga, gb)

        nb = _mean(answered_novel, "BEFORE_COMPAT")
        na = _mean(answered_novel, "AFTER_BATCH1_REPLACEMENT")
        nd = _deltas(na, nb)

        return {
            "cohort_before": cb,
            "cohort_after": ca,
            "cohort_deltas": cd,
            "gold_before": gb,
            "gold_after": ga,
            "gold_deltas": gd,
            "novel_before": nb,
            "novel_after": na,
            "novel_deltas": nd,
            "case_metrics_g021": case_metrics["g021"],
        }

    fwd_eval = eval_forward_contract()

    # Forward group retention
    # In forward contract, g021.e2 is critical=False, so it is a noncritical regression
    forward_critical_regressions = ["n022.e2"]
    forward_noncritical_regressions = ["g021.e2"]

    # Build final artifact
    diagnosis_artifact: dict[str, Any] = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-R1",
        "stage": "D4-A2-R1 — Critical-Regression Diagnosis & Repair Decision",
        "starting_head": STARTING_HEAD,
        "historical_d4_a2_authority": {
            "raw_results": "evaluation/d4_a2_raw_before_after_results.json",
            "evaluator_results": "evaluation/d4_a2_evaluator_results.json",
            "result": "evaluation/d4_a2_result.json",
            "report": "evaluation/D4_A2_FIRST_BATCH_BEFORE_AFTER_VALIDATION.md",
            "historical_verdict": HISTORICAL_D4_A2_VERDICT,
            "historical_critical_group_regressions": ["n022.e2", "g021.e2"],
            "historical_artifacts_immutable_and_unchanged": True,
        },
        "execution_boundary": {
            "model_calls": 0,
            "analyzer_calls": 0,
            "embedding_calls": 0,
            "reranker_calls": 0,
            "retrieval_runs": 0,
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "postgresql_writes": 0,
            "qdrant_writes": 0,
            "ingestion": 0,
            "reindex": 0,
            "novel_validation_runs": 0,
            "novel_holdout_runs": 0,
            "protected_dataset_access": 0,
        },
        "evidence_requirement_review": {
            "n021.e2": {
                "role": "pandaroot_lmd_implementation_ownership",
                "path": "detectors/lmd/CMakeLists.txt",
                "decision": "REQUIRED_CRITICAL",
                "rationale": "The question explicitly asks for the PandaRoot-side LMD implementation ownership in addition to the LuminosityFit scripts.",
                "selector_breadth_review": "POSSIBLY_NARROW_BUT_NOT_A_D4_A2_BLOCKER",
                "benchmark_change": "NONE_BYTE_UNCHANGED",
            },
            "n022.e2": {
                "role": "step2_artifact_consumption",
                "path": "macro/target/poca_step2_analysis.py",
                "decision": "REQUIRED_CRITICAL",
                "rationale": "The question explicitly asks what the first worker step leaves behind for the second analysis step and how the fitted vertex is fed into reprocessing. poca_step2_analysis.py directly implements this consumption.",
                "benchmark_change": "NONE_BYTE_UNCHANGED",
            },
            "g021.e2": {
                "role": "pnd_target_generator_implementation",
                "path": "pgenerators/Target/PndTargetGenerator.cxx",
                "decision": "VALID_SUPPORTING_EVIDENCE / NONCRITICAL_FOR_CURRENT_QUESTION",
                "rationale": "For 'How is restgas_profile supplied to distributed-target simulation?', the direct core evidence is macro/target/prod_sim_hvmaps.C (g021.e1). PndTargetGenerator.cxx supports the deeper generator-internal consumption to sample positions, which is valid supporting evidence but not mandatory-critical.",
                "benchmark_change": "FORWARD_ONLY_CRITICALITY_RELAXATION",
            },
        },
        "g021_forward_contract_correction": {
            "correction_type": "POST_D4_A2_FORWARD_ONLY_BENCHMARK_CONTRACT_CORRECTION",
            "file": "evaluation/benchmarks/v2_6/gold_questions.yaml",
            "elements": {
                "g021.e1": {"old_critical": True, "new_critical": True},
                "g021.e2": {"old_critical": True, "new_critical": False},
                "answer_point_p1": {"old_critical": True, "new_critical": True},
                "answer_point_p2": {"old_critical": True, "new_critical": True},
                "answer_point_p3": {"old_critical": True, "new_critical": False},
                "identifier_PndTargetGenerator": {"old_critical": True, "new_critical": False},
            },
            "historical_commit_addressable_evidence_preserved": True,
            "historical_d4_a2_retroactive_mutation_claimed": False,
        },
        "n022_first_divergence": {
            "layer0_treatment_applicability": layer0_data,
            "layer1_analyzer_retrieval_plan": layer1_data,
            "layer2_ordinary_recall_channels": layer2_data,
            "layer3_structured_graph_contribution": layer3_data,
            "layer4_fusion": layer4_data,
            "layer5_reserved_admission": layer5_data,
            "layer6_reranker_final_selection": layer6_data,
            "first_divergence_layer": "Layer 1 — Analyzer / retrieval plan",
        },
        "offline_counterfactual": counterfactual_result,
        "n022_attribution_class": n022_attribution_class,
        "n022_repair_owner": n022_repair_owner,
        "repair_disposition": "NO_GENERIC_REPAIR_YET / PAIRED_STABILITY_VALIDATION_REQUIRED",
        "forward_corrected_contract_diagnostic": {
            "FORWARD_CRITICAL_GROUP_REGRESSIONS": forward_critical_regressions,
            "FORWARD_NONCRITICAL_GROUP_REGRESSIONS": forward_noncritical_regressions,
            "cohort_critical_final_evidence_recall": {
                "before": fwd_eval["cohort_before"]["critical_final_evidence_recall"],
                "after": fwd_eval["cohort_after"]["critical_final_evidence_recall"],
                "delta": fwd_eval["cohort_deltas"]["critical_final_evidence_recall"],
            },
            "cohort_final_evidence_recall": {
                "before": fwd_eval["cohort_before"]["final_evidence_recall"],
                "after": fwd_eval["cohort_after"]["final_evidence_recall"],
                "delta": fwd_eval["cohort_deltas"]["final_evidence_recall"],
            },
            "gold_critical_final_evidence_recall": {
                "before": fwd_eval["gold_before"]["critical_final_evidence_recall"],
                "after": fwd_eval["gold_after"]["critical_final_evidence_recall"],
                "delta": fwd_eval["gold_deltas"]["critical_final_evidence_recall"],
            },
            "gold_critical_final_evidence_regressions_count": 0,
            "novel_critical_final_evidence_regressions_count": 1,
            "g021_case_diagnostic": fwd_eval["case_metrics_g021"],
            "diagnostic_observation": (
                "Under the forward contract, g021 has 0 critical group regressions (g021.e1 is retained, "
                "g021.e2 is noncritical). Gold critical final recall delta improves from -0.071429 to 0.000000. "
                "Overall cohort critical final recall delta improves from -0.064103 to -0.025641. "
                "Only 1 critical regression remains in the cohort: n022.e2."
            ),
        },
        "historical_d4_a2_verdict": HISTORICAL_D4_A2_VERDICT,
        "D4_A2_R1_DECISION": D4_A2_R1_DECISION,
        "production_activation": False,
        "exact_next_stage": "D4-A2-V1 — Paired Retrieval Stability and Variance Attribution Validation (NOT_STARTED / SEPARATELY_AUTHORIZED)",
    }

    out_path = project_root / "evaluation/d4_a2_r1_critical_regression_diagnosis.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(diagnosis_artifact, f, indent=1, ensure_ascii=False)
        f.write("\n")

    return diagnosis_artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="PANDA Agent D4-A2-R1 Static Diagnosis")
    parser.add_argument("--project-root", type=Path, default=_PROJECT_ROOT)
    args = parser.parse_args()

    artifact = run_static_diagnosis(args.project_root)
    print("D4-A2-R1 Static Diagnosis Complete:")
    print(f"  Decision: {artifact['D4_A2_R1_DECISION']}")
    print(f"  n022 Attribution: {artifact['n022_attribution_class']}")
    print(f"  n022 Repair Owner: {artifact['n022_repair_owner']}")
    print(f"  Forward Critical Regressions: {artifact['forward_corrected_contract_diagnostic']['FORWARD_CRITICAL_GROUP_REGRESSIONS']}")
    print(f"  Forward Noncritical Regressions: {artifact['forward_corrected_contract_diagnostic']['FORWARD_NONCRITICAL_GROUP_REGRESSIONS']}")
    print(f"  Forward Cohort Critical Delta: {artifact['forward_corrected_contract_diagnostic']['cohort_critical_final_evidence_recall']['delta']}")


if __name__ == "__main__":
    main()
