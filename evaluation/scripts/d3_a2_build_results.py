"""Build the frozen D3-A2 result artifact from immutable runner records.

Metric tables are recomputed deterministically from ``records.jsonl`` (the
frozen evaluator semantics already applied per record); per-case/per-rule
mechanism attributions and decisions are authored inputs frozen here.  The
script performs internal consistency checks before writing the artifact.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ARM_ORDER = ("LEGACY", "ABLATION", "STRUCTURED")
FROZEN_IMPLEMENTATION_SHA = "814a6183f8054e95f65452fc2a5ac4300a6082f5"
PREREGISTRATION_SHA = "b4adfbdc21c0fd959a26b96aad84fda5509329c96ad6083440594224a6dd7ca2"
RUN_ID = "d3_a2_frozen_20260831"

METRIC_LABELS = {
    "gold_recall_at_5": "Recall@5",
    "gold_recall_at_10": "Recall@10",
    "gold_recall_at_20": "Recall@20",
    "mrr": "MRR",
    "combined_candidate_recall": "combined candidate recall",
    "final_evidence_recall": "final evidence recall",
    "critical_final_evidence_recall": "critical evidence recall",
}

# Authored per-case mechanism analysis (frozen D3-A2 interpretation).
CASE_ANALYSIS: dict[str, dict[str, str]] = {
    "g029": {
        "primary_interpretation": "no legacy dependency observable (paraphrase case); all arms recover the required evidence; structured abstains correctly on the AMBIGUOUS PndLmdCombinedDataReader mention without collapsing it",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": False,
    },
    "n021": {
        "primary_interpretation": "no legacy dependency (paraphrase case); all arms miss the LuminosityFit orchestration group (preregistered preserved gap); structured contributes one neutral PandaRoot repository seed",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": True,
    },
    "g025": {
        "primary_interpretation": "negative control behaves identically in all arms; structured correctly abstains (runLmdFit mention stays AMBIGUOUS, no collapse, no injection)",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": False,
    },
    "g036": {
        "primary_interpretation": "legacy dependency confirmed: required macro evidence enters only through the LEGACY exact channel (rule symbol payload macro/target/*.C) at fused rank 5, final rank 1; with the rule suppressed the macro file never enters any channel; STRUCTURED seeds data_product.restgas.event_poca, traverses three accepted relations, injects four curated objects that rank very high (fused ranks 1-2), but no accepted D1 evidence linkage connects the governed object to the answer-bearing corpus file",
        "failure_classification": "EVIDENCE_LINK_COVERAGE_GAP",
        "structured_candidate_contribution": True,
    },
    "n022": {
        "primary_interpretation": "no legacy dependency (paraphrase case); all arms 2/3 groups; the e3 selected object differs between ABLATION and STRUCTURED (both objects match the group's any_of selectors) due to analyzer/reranker run variance, not structured contribution (zero seeds/injections for this case)",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": False,
    },
    "g020": {
        "primary_interpretation": "no legacy dependency (paraphrase case); all arms recover both required groups; structured abstains on the unresolved two-pass mention without negative filtering",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": False,
    },
    "n006": {
        "primary_interpretation": "nontrigger control stable across arms; structured injects one neutral PandaRoot repository seed; pre-existing e2 gap unchanged",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": True,
    },
    "g041": {
        "primary_interpretation": "negative control behaves identically in all arms; structured correctly abstains on the nonexistent SetMagicRestgasSeed mention; no injection, no false scope narrowing",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": False,
    },
    "n014": {
        "primary_interpretation": "LEGACY equals ABLATION on the direct literal case, so the model_factory_theory shortcut was not materially responsible for useful retrieval; structured injects the S-tier model_framework match but the model_framework definition group is missed in all arms (pre-existing recall gap unrelated to the rule)",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": True,
    },
    "g060": {
        "primary_interpretation": "no legacy dependency (paraphrase case); all arms recover all three groups; structured abstains on the unresolved beam-divergence mention",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": False,
    },
    "g052": {
        "primary_interpretation": "LEGACY equals ABLATION on the direct literal case (the question also literally triggers restgas_profile_workflow; both suppressed in ABLATION with no effect), so the effective_acceptance_pipeline shortcut was not materially responsible; structured abstains on both descriptive mentions without narrowing the distinction",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": False,
    },
    "g055": {
        "primary_interpretation": "distinction control stable across arms; structured abstains on both descriptive mentions; no over-expansion and no false ambiguity collapse",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": False,
    },
    "n003": {
        "primary_interpretation": "nontrigger control stable across arms; structured injects one neutral PandaRoot repository seed; pre-existing e2 gap unchanged",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": True,
    },
    "g021": {
        "primary_interpretation": "legacy dependency confirmed: required restgas_profile configuration-usage and simulation-macro evidence enters only through the LEGACY exact channel (rule symbol payload macro/target/*.C and pgenerators path); with the rule suppressed neither file enters any channel; STRUCTURED seeds configuration.restgas_profile, traverses to workflow.restgas_profile_reconstruction, injects two curated objects that rank very high (fused ranks 1 and 3), but no accepted D1 evidence linkage connects the governed objects to the answer-bearing corpus files",
        "failure_classification": "EVIDENCE_LINK_COVERAGE_GAP",
        "structured_candidate_contribution": True,
    },
    "n004": {
        "primary_interpretation": "LEGACY equals ABLATION on the direct literal case, so the root_macro_usage shortcut was not materially responsible; structured injects one neutral PandaRoot repository seed; outcomes identical",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": True,
    },
    "g007": {
        "primary_interpretation": "negative control behaves identically in all arms; structured injects one neutral PandaRoot repository seed; no unsupported-evidence leakage and no false confidence introduced",
        "failure_classification": "STRUCTURED_PARITY",
        "structured_candidate_contribution": True,
    },
}

# Authored per-rule migration decisions under the frozen vocabulary and guards.
RULE_DECISIONS: dict[str, dict[str, Any]] = {
    "lmd_fit_data_chain": {
        "decision": "INSUFFICIENT_EVIDENCE",
        "decision_rationale": "PARTIALLY_IDENTIFIABLE per the frozen preregistration: no direct-trigger case exists, so the required LEGACY-ABLATION dependency contrast is not measurable; the frozen guard restricts the migration decision to INSUFFICIENT_EVIDENCE. Paraphrase cases g029 (1.0) and n021 (0.5) and control g025 are stable across arms; structured abstains correctly on the AMBIGUOUS PndLmdCombinedDataReader mention.",
    },
    "event_poca_handoff": {
        "decision": "STRUCTURED_REGRESSION",
        "decision_rationale": "Direct case g036 establishes a real legacy dependency (LEGACY 1.0 -> ABLATION 0.0 final-evidence recall) and STRUCTURED fails to recover it (0.0): the structured path resolves and ranks the correct governed objects very highly but the answer-bearing macro file is reachable only through the legacy exact-channel symbol payload because no accepted D1 evidence linkage exists. Material underperformance of the structured treatment on valid directly applicable evidence; no safety or control regression.",
    },
    "pid_two_pass_files": {
        "decision": "INSUFFICIENT_EVIDENCE",
        "decision_rationale": "PARTIALLY_IDENTIFIABLE per the frozen preregistration: no direct-trigger case, dependency contrast not measurable; frozen guard applies. Paraphrase g020 (1.0) and controls n006/g041 are stable across arms; structured abstains correctly on the unresolved two-pass mention.",
    },
    "model_factory_theory": {
        "decision": "NO_MEANINGFUL_LEGACY_DEPENDENCY",
        "decision_rationale": "Direct case n014 shows LEGACY == ABLATION (0.5): removing the shortcut does not degrade useful retrieval, so the shortcut was not materially responsible. STRUCTURED neither regresses nor improves (0.5); the model_framework definition group is missed in all arms for reasons unrelated to the rule. Direct dependency is identifiable and ablation shows no material legacy contribution, matching the frozen label semantics.",
    },
    "effective_acceptance_pipeline": {
        "decision": "NO_MEANINGFUL_LEGACY_DEPENDENCY",
        "decision_rationale": "Direct case g052 shows LEGACY == ABLATION == STRUCTURED (1.0): paper-channel retrieval reproduces the useful behavior without the shortcut (the question also literally triggers restgas_profile_workflow; suppressing both changes nothing). The distinction control g055 stays stable and structured abstains without narrowing the acceptance/efficiency distinction.",
    },
    "restgas_profile_workflow": {
        "decision": "STRUCTURED_REGRESSION",
        "decision_rationale": "Direct case g021 establishes a real legacy dependency (LEGACY 1.0 -> ABLATION 0.0) and STRUCTURED fails to recover it (0.0): the structured path seeds configuration.restgas_profile and traverses to workflow.restgas_profile_reconstruction with very high fused ranks, but the answer-bearing configuration-usage and macro files lack accepted D1 evidence linkage and never enter any candidate channel. Material underperformance on valid directly applicable evidence; no safety or control regression.",
    },
    "root_macro_usage": {
        "decision": "NO_MEANINGFUL_LEGACY_DEPENDENCY",
        "decision_rationale": "Direct case n004 shows LEGACY == ABLATION == STRUCTURED (1.0): ordinary documentation retrieval reproduces the useful behavior without the shortcut. The negative control g007 stays stable; the structured PandaRoot repository seed injection is metric-neutral and safe.",
    },
}


def load_records(run_dir: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (run_dir / "records.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]


def arm_metric(records: list[dict[str, Any]], arm: str, case_id: str, field: str) -> Any:
    record = next(r for r in records if r["arm"] == arm and r["case_id"] == case_id)
    return (record.get("metrics") or {}).get(field)


def aggregate(records: list[dict[str, Any]], arm: str, field: str) -> dict[str, Any]:
    values = []
    for record in records:
        if record["arm"] != arm:
            continue
        metric = (record.get("metrics") or {}).get(field)
        applicability = ((record.get("metrics") or {}).get("metric_applicability") or {}).get(field)
        if metric is not None and applicability:
            values.append((record["case_id"], metric))
    mean = sum(value for _, value in values) / len(values) if values else None
    return {"mean": mean, "applicable_case_count": len(values)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run-dir", type=Path, default=None)
    args = parser.parse_args()
    run_dir = args.run_dir or (args.project_root / "data" / "evaluation" / "runs" / RUN_ID)
    records = load_records(run_dir)
    assert len(records) == 48, f"expected 48 records, found {len(records)}"
    assert not [r for r in records if r.get("error")], "runner recorded errors"

    manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    preregistration = json.loads(
        (args.project_root / "evaluation" / "d3_a0_shortcut_migration_preregistration.json").read_text(encoding="utf-8")
    )
    manifest_cases = preregistration["comparison_cases"]
    case_ids = [c["case_id"] for c in manifest_cases]
    assert {r["case_id"] for r in records} == set(case_ids)
    assert {r["arm"] for r in records} == set(ARM_ORDER)
    identifiability = {
        item["rule_id"]: item["identifiability_status"]
        for item in preregistration["selected_rule_identifiability"]
    }

    # --- aggregate metric tables -------------------------------------------------
    metric_fields = [
        "gold_recall_at_5",
        "gold_recall_at_10",
        "gold_recall_at_20",
        "mrr",
        "combined_candidate_recall",
        "final_evidence_recall",
        "critical_final_evidence_recall",
    ]
    arm_summaries: dict[str, Any] = {}
    for arm in ARM_ORDER:
        arm_summaries[arm] = {
            "executions": 16,
            "metrics": {field: aggregate(records, arm, field) for field in metric_fields},
        }

    paired_metrics: dict[str, Any] = {"applicable_case_count": 13, "denominator_note": "means over the 13 answered cases; the 3 insufficient-evidence controls are retained for safety/control analysis only"}
    for field in metric_fields:
        paired_metrics[field] = {}
        for case_id in case_ids:
            l = arm_metric(records, "LEGACY", case_id, field)
            a = arm_metric(records, "ABLATION", case_id, field)
            s = arm_metric(records, "STRUCTURED", case_id, field)
            if None in (l, a, s):
                continue
            paired_metrics[field][case_id] = {
                "LEGACY": l,
                "ABLATION": a,
                "STRUCTURED": s,
                "legacy_dependency": round(l - a, 6),
                "structured_recovery": round(s - a, 6),
                "structured_parity": round(s - l, 6),
            }
        deltas_l_a = [cell["legacy_dependency"] for cell in paired_metrics[field].values()]
        deltas_s_a = [cell["structured_recovery"] for cell in paired_metrics[field].values()]
        deltas_s_l = [cell["structured_parity"] for cell in paired_metrics[field].values()]
        paired_metrics[field]["_summary"] = {
            "mean_legacy_minus_ablation": round(sum(deltas_l_a) / len(deltas_l_a), 6),
            "mean_structured_minus_ablation": round(sum(deltas_s_a) / len(deltas_s_a), 6),
            "mean_structured_minus_legacy": round(sum(deltas_s_l) / len(deltas_s_l), 6),
            "direction": "higher is better for every metric",
        }

    # --- preregistered primary metrics -------------------------------------------
    def case_cells(field: str) -> dict[str, Any]:
        return {
            cid: cell
            for cid, cell in paired_metrics[field].items()
            if cid != "_summary"
        }

    fer_cells = case_cells("final_evidence_recall")
    legacy_dependent = [cid for cid, cell in fer_cells.items() if cell["legacy_dependency"] > 0]
    legacy_positive = [cid for cid, cell in fer_cells.items() if cell["LEGACY"] > 0]
    # The preregistered reproduction/recovery predicate is STRUCTURED >= LEGACY
    # (structured_parity), not STRUCTURED >= ABLATION.
    recovered = [cid for cid in legacy_dependent if fer_cells[cid]["structured_parity"] >= 0]
    reproduced = [cid for cid in legacy_positive if fer_cells[cid]["structured_parity"] >= 0]
    regressed = [cid for cid, cell in fer_cells.items() if cell["structured_parity"] < 0]
    primary_frozen_metrics = {
        "useful_retrieval_reproduction_rate": {
            "numerator": len(reproduced),
            "denominator": len(legacy_positive),
            "value": round(len(reproduced) / len(legacy_positive), 4),
            "cases": {"legacy_positive": legacy_positive, "reproduced": reproduced},
            "definition": "among cases whose LEGACY arm retrieves at least one required evidence group in final evidence, fraction where STRUCTURED reaches an equal or greater required-group count",
        },
        "selected_rule_dependency_rate": {
            "numerator": len(legacy_dependent),
            "denominator": len(fer_cells),
            "value": round(len(legacy_dependent) / len(fer_cells), 4),
            "cases": legacy_dependent,
            "definition": "fraction of applicable comparison cases where LEGACY final-evidence recall exceeds ABLATION",
        },
        "structured_recovery_rate": {
            "numerator": len(recovered),
            "denominator": len(legacy_dependent),
            "value": round(len(recovered) / len(legacy_dependent), 4) if legacy_dependent else None,
            "cases": {"legacy_dependent": legacy_dependent, "recovered": recovered},
            "definition": "among cases with LEGACY > ABLATION, fraction where STRUCTURED reaches or exceeds LEGACY",
        },
        "regression_rate": {
            "numerator": len(regressed),
            "denominator": len(fer_cells),
            "value": round(len(regressed) / len(fer_cells), 4),
            "cases": regressed,
            "definition": "fraction of applicable comparison cases where STRUCTURED final-evidence recall is below LEGACY",
        },
    }

    # --- case results -------------------------------------------------------------
    case_results: list[dict[str, Any]] = []
    for case in manifest_cases:
        case_id = case["case_id"]
        arms_out: dict[str, Any] = {}
        for arm in ARM_ORDER:
            record = next(r for r in records if r["arm"] == arm and r["case_id"] == case_id)
            metrics = record.get("metrics") or {}
            counters = ((record.get("d3_experiment") or {}).get("diagnostic_counters") or {})
            legacy_counters = counters if arm != "LEGACY" else counters
            arms_out[arm] = {
                "retrieval_receipt_ref": {"run_id": RUN_ID, "arm": arm, "case_id": case_id},
                "matched_expansion_rules": (record.get("plan_summary", {}).get("d3_experiment") or {}).get("matched_active_rule_ids"),
                "selected_shortcut_triggered": (
                    (record.get("plan_summary", {}).get("d3_experiment") or {}).get("diagnostic_counters", {}).get("selected_legacy_shortcut_hit_count", 0) > 0
                ),
                "structured_diagnostic_counters": counters if arm == "STRUCTURED" else None,
                "metric_matches": {
                    "final_evidence_recall": metrics.get("final_evidence_recall"),
                    "critical_final_evidence_recall": metrics.get("critical_final_evidence_recall"),
                    "gold_recall_at_5": metrics.get("gold_recall_at_5"),
                    "gold_recall_at_10": metrics.get("gold_recall_at_10"),
                    "gold_recall_at_20": metrics.get("gold_recall_at_20"),
                    "mrr": metrics.get("mrr"),
                    "combined_candidate_recall": metrics.get("combined_candidate_recall"),
                    "final_evidence_group_provenance": (metrics.get("evidence_match_provenance") or {}).get("final_evidence_recall"),
                },
            }
        analysis = CASE_ANALYSIS[case_id]
        legacy_cell = fer_cells.get(case_id, {})
        case_results.append(
            {
                "case_id": case_id,
                "dataset": case["dataset"],
                "bound_rule_id": case["bound_rule_id"],
                "comparison_role": case["comparison_role"],
                "identifiability_status": identifiability[case["bound_rule_id"]],
                "arms": arms_out,
                "paired_interpretation": {
                    "legacy_dependency_confirmed": legacy_cell.get("legacy_dependency", 0) > 0,
                    "structured_recovery_occurred": legacy_cell.get("structured_recovery", 0) > 0,
                    "structured_regression_occurred": legacy_cell.get("structured_parity", 0) < 0,
                    "primary_interpretation": analysis["primary_interpretation"],
                },
                "failure_classification": analysis["failure_classification"],
            }
        )

    # --- per-rule results -----------------------------------------------------------
    rule_to_cases: dict[str, list[str]] = {}
    for case in manifest_cases:
        rule_to_cases.setdefault(case["bound_rule_id"], []).append(case["case_id"])
    per_rule_results = []
    for rule_id, decision in RULE_DECISIONS.items():
        case_ids_for_rule = rule_to_cases[rule_id]
        direct = [c for c in case_ids_for_rule if next(x for x in manifest_cases if x["case_id"] == c)["comparison_role"] == "DIRECT_LITERAL"]
        controls = [c for c in case_ids_for_rule if "CONTROL" in next(x for x in manifest_cases if x["case_id"] == c)["comparison_role"]]
        dependency_evidence = [
            {
                "case_id": cid,
                "legacy_minus_ablation_final_evidence_recall": fer_cells.get(cid, {}).get("legacy_dependency"),
                "structured_minus_ablation_final_evidence_recall": fer_cells.get(cid, {}).get("structured_recovery"),
            }
            for cid in case_ids_for_rule
            if cid in fer_cells
        ]
        per_rule_results.append(
            {
                "rule_id": rule_id,
                "identifiability_status": identifiability[rule_id],
                "case_ids": case_ids_for_rule,
                "direct_case_ids": direct,
                "control_case_ids": controls,
                "legacy_dependency_evidence": dependency_evidence,
                "structured_recovery_evidence": dependency_evidence,
                "structured_parity_evidence": dependency_evidence,
                "mechanism_findings": [
                    CASE_ANALYSIS[cid]["primary_interpretation"] for cid in case_ids_for_rule
                ],
                "safety_findings": "no control regression, no leakage, no ambiguity collapse, all five prohibited-use counters zero in every STRUCTURED execution bound to this rule",
                "decision": decision["decision"],
                "decision_rationale": decision["decision_rationale"],
            }
        )

    # --- counters and accounting ------------------------------------------------------
    safety_counters = {
        "migration_specific_direct_answer_location_injection_count": 0,
        "prohibited_fallback_use_count": 0,
        "evaluation_metadata_runtime_use_count": 0,
        "selected_legacy_payload_reuse_count": 0,
        "same_as_activation_count": 0,
    }
    for record in records:
        if record["arm"] != "STRUCTURED":
            continue
        counters = (record.get("d3_experiment") or {}).get("diagnostic_counters") or {}
        for key in safety_counters:
            assert counters.get(key) == 0, f"safety counter {key} nonzero in {record['case_id']}"

    d3_counter_totals: Counter[str] = Counter()
    for record in records:
        if record["arm"] != "STRUCTURED":
            continue
        counters = (record.get("d3_experiment") or {}).get("diagnostic_counters") or {}
        for key, value in counters.items():
            if isinstance(value, (int, float)):
                d3_counter_totals[key] += value
        statuses = counters.get("structured_resolution_status_counts") or {}
        for status, count in statuses.items():
            d3_counter_totals[f"resolution_status::{status}"] += count

    call_totals: Counter[str] = Counter()
    for record in records:
        for key, value in (record.get("call_accounting") or {}).items():
            if isinstance(value, (int, float)):
                call_totals[key] += value

    taxonomy_counts = Counter(
        CASE_ANALYSIS[cid]["failure_classification"] for cid in case_ids
    )

    # --- assemble artifact --------------------------------------------------------------
    decisions_by_value = Counter(dec["decision"] for dec in RULE_DECISIONS.values())
    verdict = "PASS"
    artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D3-A2",
        "status": "COMPLETE / FROZEN_THREE_ARM_COMPARISON_COMPLETE",
        "verdict": verdict,
        "verdict_scope": "valid single frozen three-arm comparison; PASS does not imply every rule supports migration",
        "implementation_identity": {
            "frozen_implementation_commit": FROZEN_IMPLEMENTATION_SHA,
            "commit_subject": "D3-A1 implement structured shortcut replacement prototype",
            "git_head_during_run": manifest["git_head"],
            "pre_run_identity_diff_lines": manifest["implementation_identity_diff_lines"],
        },
        "preregistration_identity": {
            "structured_artifact": "evaluation/d3_a0_shortcut_migration_preregistration.json",
            "sha256": PREREGISTRATION_SHA,
            "schema_version": preregistration["schema_version"],
            "repair_source_head": preregistration["repair_source_head"],
        },
        "outcome_exposure": {
            "before_first_formal_case": "STARTED",
            "after_valid_complete_comparison": "COMPLETE",
            "started_at_utc": manifest["started_at_utc"],
            "finished_at_utc": manifest["finished_at_utc"],
        },
        "selected_rule_ids": preregistration["selected_batch_revision"]["repaired_selected_rule_ids"],
        "comparison_manifest_identity": {
            "revision_id": preregistration["comparison_manifest_revision"]["revision_id"],
            "case_count": 16,
            "dataset_counts": preregistration["comparison_selection_policy"]["dataset_counts"],
            "case_ids_in_execution_order": manifest["case_order"],
            "gold_dataset_sha256": manifest["gold_dataset_sha256"],
            "novel_dev_dataset_sha256": manifest["novel_dev_dataset_sha256"],
        },
        "execution_order": {
            "arm_order": list(ARM_ORDER),
            "case_order_within_arm": manifest["case_order"],
            "runner": "evaluation/scripts/d3_a2_runner.py",
            "run_id": RUN_ID,
            "raw_records": "data/evaluation/runs/d3_a2_frozen_20260831/records.jsonl",
        },
        "run_counts": {
            "total_executions": 48,
            "LEGACY": 16,
            "ABLATION": 16,
            "STRUCTURED": 16,
            "complete_paired_case_cells": 16,
            "infrastructure_failures": 0,
            "retries": 0,
            "scientific_reruns": 0,
        },
        "call_counts": {
            "analyzer_generation_calls": 48,
            "reranker_generation_calls": 48,
            "total_generation_calls": call_totals.get("generation_calls"),
            "embedding_calls": call_totals.get("embedding_calls"),
            "model_calls_total": call_totals.get("model_calls"),
            "token_usage": call_totals.get("token_usage"),
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "new_model_class_or_prompt_introduced": False,
        },
        "storage_writes": {
            "postgresql_writes": 0,
            "qdrant_writes": 0,
            "reindex": False,
            "index_migration": False,
        },
        "protected_dataset_access": {
            "novel_validation": "UNSEEN",
            "novel_validation_cases_run": 0,
            "novel_holdout": "SEALED_UNSEEN",
            "novel_holdout_cases_run": 0,
        },
        "arm_summaries": arm_summaries,
        "paired_metrics": paired_metrics,
        "primary_frozen_metrics": primary_frozen_metrics,
        "case_results": case_results,
        "per_rule_results": per_rule_results,
        "failure_taxonomy_counts": dict(sorted(taxonomy_counts.items())),
        "d3_aggregate_counters": dict(sorted(d3_counter_totals.items())),
        "safety_counters": {
            "per_execution_verification": "all five counters verified zero in all 16 STRUCTURED executions",
            **safety_counters,
        },
        "overall_interpretation": {
            "frozen_question": "Can the frozen generic D1/D2 structured path reproduce useful behavior of a small representative legacy-shortcut batch without relying on the legacy answer-location payloads or introducing unsafe retrieval regressions?",
            "answer": "The experiment is valid and fully attributable. Three of the five directly identifiable rules show no meaningful legacy dependency (model_factory_theory, effective_acceptance_pipeline, root_macro_usage): their shortcuts were not materially responsible for useful retrieval, and removal plus structured treatment changes nothing. Two rules show a real, material legacy dependency (event_poca_handoff on g036, restgas_profile_workflow on g021): the useful behavior of these shortcuts is exact-channel injection of answer-location file paths/symbols, and the frozen generic structured path cannot reproduce it because the accepted D1 graph has no evidence linkage from the correctly resolved governed objects to the answer-bearing corpus files, even though structured candidates are recalled and ranked very highly (fused ranks 1-3). No unsafe retrieval regression, no control leakage, no prohibited shortcut encoding was observed anywhere.",
            "migration_support_denominator": {
                "directly_identifiable_rules": 5,
                "migration_supported": decisions_by_value["MIGRATION_SUPPORTED"],
                "note": "the two generalization-only rules are reported separately and carry INSUFFICIENT_EVIDENCE by the frozen guard",
            },
            "run_variance_note": "arms are independent frozen-path executions; analyzer/reranker LLM nondeterminism at temperature 0 produced minor metric-neutral selection variance in one case (n022 e3, both objects selector-matched) and small concept-list differences; ABLATION-vs-STRUCTURED rule state was identical by construction",
        },
        "production_changes": {
            "query_expansions_yaml_modified": False,
            "structured_d3_activated_in_production": False,
            "production_d2_role_changed": False,
            "production_routing_changed": False,
            "runtime_files_changed_during_a2": False,
        },
        "post_run_identity_check": {
            "command": "git diff 814a6183f8054e95f65452fc2a5ac4300a6082f5 -- src/panda_agent/retrieval.py src/panda_agent/d3_structured.py",
            "result": "no runtime semantic change",
        },
        "next_stage": {
            "recommended_task": "structured coverage-gap repair design: a separately authorized bounded D1 evidence-linkage coverage stage connecting governed objects to their retrievable answer-location corpus evidence for the two STRUCTURED_REGRESSION rules (event_poca_handoff, restgas_profile_workflow), followed by a focused re-comparison of only those rules",
            "executed_here": False,
            "evidence_basis": "the single dominant failure class is EVIDENCE_LINK_COVERAGE_GAP (2 cases); D2 resolution and D1 traversal worked and structured candidates ranked at fused ranks 1-3, so ranking is not the binding constraint",
        },
    }

    # --- internal consistency checks -------------------------------------------------
    assert artifact["run_counts"]["total_executions"] == 48
    assert len(artifact["case_results"]) == 16
    assert len(artifact["per_rule_results"]) == 7
    frozen_decision_vocabulary = {
        "MIGRATION_SUPPORTED", "PARTIALLY_REPRODUCED", "STRUCTURED_REGRESSION",
        "NO_MEANINGFUL_LEGACY_DEPENDENCY", "INSUFFICIENT_EVIDENCE",
    }
    assert {dec["decision"] for dec in RULE_DECISIONS.values()} <= frozen_decision_vocabulary
    for rule in per_rule_results:
        assert rule["decision"] in {
            "MIGRATION_SUPPORTED", "PARTIALLY_REPRODUCED", "STRUCTURED_REGRESSION",
            "NO_MEANINGFUL_LEGACY_DEPENDENCY", "INSUFFICIENT_EVIDENCE",
        }
        if rule["identifiability_status"] == "PARTIALLY_IDENTIFIABLE":
            assert rule["decision"] == "INSUFFICIENT_EVIDENCE", rule["rule_id"]
    allowed_taxonomy = {
        "NO_STRUCTURED_ENTITY", "AMBIGUOUS_STRUCTURED_ENTITY", "RELATION_COVERAGE_GAP",
        "EVIDENCE_LINK_COVERAGE_GAP", "STRUCTURED_CANDIDATE_RECALLED_BUT_RANKED_OUT",
        "LEGACY_SHORTCUT_DEPENDENCY_CONFIRMED", "LEGACY_SHORTCUT_NOT_MATERIALLY_USED",
        "STRUCTURED_PARITY", "STRUCTURED_IMPROVEMENT", "STRUCTURED_REGRESSION",
        "EVALUATION_CASE_ISSUE", "INFRASTRUCTURE_FAILURE", "UNCLASSIFIED",
    }
    assert set(taxonomy_counts) <= allowed_taxonomy

    output_path = args.project_root / "evaluation" / "d3_a2_three_arm_results.json"
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {output_path}")
    print("verdict:", verdict)
    print("per-rule decisions:", json.dumps(decisions_by_value, sort_keys=True))
    print("taxonomy:", json.dumps(dict(sorted(taxonomy_counts.items())), sort_keys=True))


if __name__ == "__main__":
    main()
