"""Build the frozen D3.5-A2 result artifact from immutable runner records.

Metric tables, causal contrasts, and bridge diagnostics are recomputed
deterministically from ``records.jsonl`` (the frozen evaluator semantics
already applied per record); the scientific interpretation, verdict, and
lifecycle decision are authored inputs frozen here.  The script performs
internal consistency checks before writing the artifact.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ARM_ORDER = ("LEGACY", "ABLATION", "STRUCTURED_UNBRIDGED", "STRUCTURED_BRIDGED")
CASE_ORDER = ("g036", "g021", "n006", "g041", "g020", "n004")
RUN_ID = "d3_5_a2_focused_20260901"
FROZEN_IMPLEMENTATION_SHA = "9b5a84996c30eaf1a297924b36452a90fe6d84d2"

METRIC_FIELDS = [
    "gold_recall_at_5",
    "gold_recall_at_10",
    "gold_recall_at_20",
    "mrr",
    "combined_candidate_recall",
    "final_evidence_recall",
    "critical_final_evidence_recall",
]

SAFETY_COUNTER_KEYS = [
    "migration_specific_direct_answer_location_injection_count",
    "prohibited_fallback_use_count",
    "evaluation_metadata_runtime_use_count",
    "selected_legacy_payload_reuse_count",
    "same_as_activation_count",
]

CASE_ROLES = {
    "g036": "existing-provenance reachability plus materialization",
    "g021": "independently governed genuine-coverage path",
    "n006": "nearby nontrigger control",
    "g041": "ambiguity/abstention and negative control",
    "g020": "same subsystem with no governed evidence bridge required",
    "n004": "ordinary retrieval already succeeds",
}

# Authored per-case interpretation (post-outcome, honest decomposition).
# Mechanical contrast labels are computed from records; the prose below
# explains the mechanism behind each case's outcome.
CASE_INTERPRETATION: dict[str, str] = {
    "g036": (
        "Legacy dependency confirmed (LEGACY 1.0 -> ABLATION 0.0). The frozen A+B bridge "
        "worked mechanically end-to-end: the D2 seed data_product.restgas.event_poca "
        "(Tier S, RESOLVED_UNIQUE) reached workflow.restgas.first_pass_poca through the "
        "preregistered parent (boost_root) + accepted-relation/workflow-step paths, and the "
        "bridge materialized macro/target/ana_dpm.C (plus prod_aod_complete.C and "
        "pid_complete.C) from accepted relation evidence_object_ids into source-native "
        "candidates. Combined candidate recall rose 0.0 (UNBRIDGED) -> 1.0 (BRIDGED): the "
        "required evidence entered the candidate pool for the first time. But the ana_dpm.C "
        "candidate sat in the graph channel (prefix position 3/16, weight 0.8), scored below "
        "the frozen fused top-30 rerank pool cutoff, was never reranked, and never entered "
        "final evidence (final recall 0.0). No displacement, no control effects."
    ),
    "g021": (
        "Legacy dependency confirmed (LEGACY 1.0 -> ABLATION 0.0). The bridge reached "
        "workflow.restgas_profile_reconstruction from the configuration.restgas_profile seed "
        "via the accepted PARAMETERIZES edge and materialized its 62 governed evidence "
        "objects; 20 fit the bridge cap (including macro/target/prod_sim_hvmaps.C), 42 were "
        "ranked out at the cap. Combined candidate recall rose 0.0 -> 0.5: group e1 "
        "(prod_sim_hvmaps.C) entered the pool; group e2 (pgenerators/Target/PndTargetGenerator.cxx) "
        "did not, because its provenance-bearing edge originates from "
        "file_pattern.restgas_profile_input, which was not resolved as a D2 seed in this "
        "question (resolution statuses: RESOLVED_UNIQUE 1, UNRESOLVED 2), so that edge was "
        "never reached under the frozen one-transition budget. The injected prod_sim_hvmaps.C "
        "candidate entered the graph channel (position 9/20) but scored below the fused top-30 "
        "cutoff and never reached final evidence (final recall 0.0). The Mechanism-C governed "
        "knowledge was therefore partially usable through the bridge at pool level, and not "
        "usable at final-evidence level."
    ),
    "n006": (
        "Nontrigger control stable: final evidence recall 0.5 in all four arms (pre-existing "
        "e2 group gap preserved). Zero bridge activity (0 bridged candidates). The R@5/MRR "
        "spread across arms (LEGACY/UNBRIDGED 0.0@5 vs ABLATION/BRIDGED 0.5@5) is the "
        "documented temperature-0 analyzer/reranker execution-variance class (cf. D3-A2 "
        "n022 e3), not a bridge effect: final evidence and R@10/20 are identical in all arms."
    ),
    "g041": (
        "Ambiguity/abstention negative control preserved: metrics not applicable (frozen "
        "insufficient-evidence expectation) identically in all four arms; no abstention "
        "break, no ambiguity collapse, zero bridge activity."
    ),
    "g020": (
        "Same-subsystem control outcome-neutral: final evidence recall 1.0 in all four arms. "
        "The Tier-D ambiguous boost_root mention was admitted atomically (ambiguity set 2, "
        "within the cap-8 rule, no truncation) and the bridge injected 20 provenance-backed "
        "candidates (including ana_dpm.C), displacing all 20 ordinary graph candidates at the "
        "graph limit. The displacement was outcome-neutral: the required evidence groups were "
        "satisfied through other channels, and no harmful expansion, scope leakage, or "
        "regression was observed. This is the largest observed displacement (20/20 graph "
        "slots) and is recorded as a bounded-but-real displacement fact."
    ),
    "n004": (
        "Ordinary-retrieval control stable: 1.0 in all four arms; zero bridge activity; no "
        "expansion or regression."
    ),
}

# Authored aggregate interpretation and verdict (post-outcome).
OVERALL_INTERPRETATION = (
    "The experiment is valid, complete, and fully attributable (24/24 cells, 0 errors, 0 "
    "retries). At the final-evidence level the frozen bridge produced no incremental "
    "recovery: both positive cases stayed at 0.0 in ABLATION, STRUCTURED_UNBRIDGED, and "
    "STRUCTURED_BRIDGED, so BRIDGED - UNBRIDGED = 0.0 and BRIDGED - LEGACY = -0.4 on "
    "final evidence recall. The shortcut dependency is real and unchanged "
    "(LEGACY - ABLATION = +0.4, driven by g036 and g021). However, the bridge produced a "
    "real, causally identifiable incremental contribution one level earlier in the pipeline: "
    "combined candidate recall rose from 0.0 to 1.0 (g036) and 0.0 to 0.5 (g021), so "
    "BRIDGED - UNBRIDGED = +0.3 on combined candidate recall. Mechanism A (bounded "
    "structural reachability) and Mechanism B (exact provenance materialization) worked "
    "exactly as designed and as preregistered: the preregistered g036 path "
    "event_poca -> boost_root -> first_pass_poca -> ana_dpm.C was observed with receipts. "
    "The binding constraint is downstream of the bridge: provenance-backed source-native "
    "candidates enter only the graph channel (weight 0.8, single-channel), score below the "
    "fused top-30 rerank pool cutoff against multi-channel exact/dense/sparse competition, "
    "and therefore never reach the reranker, the selector, or final evidence. Controls show "
    "no material harm: n006/g020/n004 outcomes unchanged, g041 abstention preserved, zero "
    "safety-counter violations; the g020 20/20 graph-slot displacement was outcome-neutral "
    "and bounded by the existing graph cap. The bridge is therefore validated as a "
    "bounded, governed, additively-injective pool-level mechanism, but NOT validated as an "
    "end-to-end final-evidence recovery mechanism under the frozen ranking configuration."
)

VERDICT = "PARTIAL / TARGETED_RECOVERY_MIXED"
LIFECYCLE_DECISION = "D3.5 COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED"


def load_records(run_dir: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (run_dir / "records.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]


def aggregate(records: list[dict[str, Any]], arm: str, field: str) -> dict[str, Any]:
    values = []
    for record in records:
        if record["arm"] != arm:
            continue
        metrics = record.get("metrics") or {}
        metric = metrics.get(field)
        applicability = (metrics.get("metric_applicability") or {}).get(field)
        if metric is not None and applicability:
            values.append((record["case_id"], metric))
    mean = round(sum(value for _, value in values) / len(values), 6) if values else None
    return {"mean": mean, "applicable_case_count": len(values)}


def compact_reachability(receipts: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    compact = []
    for item in receipts or []:
        structural_path = item.get("structural_path") or {}
        compact.append(
            {
                "reachability_receipt_id": item.get("reachability_receipt_id"),
                "seed_object_id": item.get("seed_object_id"),
                "seed_authority_tier": item.get("seed_authority_tier"),
                "D2_resolution_status": item.get("D2_resolution_status"),
                "reachability_status": item.get("reachability_status"),
                "path": " -> ".join(structural_path.get("node_ids") or []),
                "transitions": " -> ".join(structural_path.get("transition_types") or []),
                "budget_consumed": item.get("budget_consumed"),
                "budget_remaining": item.get("budget_remaining"),
            }
        )
    return compact


def compact_bridge_receipts(receipts: list[dict[str, Any]] | None) -> dict[str, Any]:
    by_status = Counter(item.get("bridge_status") for item in receipts or [])
    injected = []
    for item in receipts or []:
        if item.get("bridge_status") == "BRIDGED_CANDIDATE_INJECTED":
            locator = item.get("locator") if isinstance(item.get("locator"), dict) else {}
            injected.append(
                {
                    "bridge_receipt_id": item.get("bridge_receipt_id"),
                    "origin_type": item.get("evidence_provenance_origin_type"),
                    "origin_id": item.get("evidence_provenance_origin_id"),
                    "source_id": item.get("source_id"),
                    "source_version_id": item.get("source_version_id"),
                    "candidate_object_id": item.get("source_native_candidate_object_id"),
                    "locator_path": locator.get("path"),
                }
            )
    return {
        "status_counts": dict(sorted(by_status.items())),
        "injected_candidates": injected,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run-dir", type=Path, default=None)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    run_dir = args.run_dir or (project_root / "data" / "evaluation" / "runs" / RUN_ID)
    records = load_records(run_dir)
    assert len(records) == 24, f"expected 24 records, found {len(records)}"
    assert not [r for r in records if r.get("error")], "runner recorded errors"
    assert [(r["case_id"], r["arm"]) for r in records] == [
        (case, arm) for case in CASE_ORDER for arm in ARM_ORDER
    ], "execution order does not match the frozen case-major order"

    run_manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    manifest_path = project_root / "evaluation" / "d3_5_a2_focused_evidence_link_recovery_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # --- aggregate metric tables -------------------------------------------------
    arm_summaries = {
        arm: {
            "executions": 6,
            "metrics": {field: aggregate(records, arm, field) for field in METRIC_FIELDS},
        }
        for arm in ARM_ORDER
    }

    # --- paired contrasts per case -------------------------------------------------
    paired_metrics: dict[str, Any] = {}
    for field in METRIC_FIELDS:
        paired_metrics[field] = {}
        for case_id in CASE_ORDER:
            cells = {
                arm: next(
                    (r.get("metrics") or {}).get(field)
                    for r in records
                    if r["arm"] == arm and r["case_id"] == case_id
                )
                for arm in ARM_ORDER
            }
            if any(value is None for value in cells.values()):
                paired_metrics[field][case_id] = {
                    "applicable": False,
                    "arm_values": cells,
                    "note": "frozen insufficient-evidence control; metrics not applicable in any arm",
                }
                continue
            paired_metrics[field][case_id] = {
                "applicable": True,
                **cells,
                "legacy_minus_ablation": round(cells["LEGACY"] - cells["ABLATION"], 6),
                "unbridged_minus_ablation": round(
                    cells["STRUCTURED_UNBRIDGED"] - cells["ABLATION"], 6
                ),
                "bridged_minus_unbridged": round(
                    cells["STRUCTURED_BRIDGED"] - cells["STRUCTURED_UNBRIDGED"], 6
                ),
                "bridged_minus_legacy": round(cells["STRUCTURED_BRIDGED"] - cells["LEGACY"], 6),
            }
        deltas = {
            "legacy_minus_ablation": [],
            "unbridged_minus_ablation": [],
            "bridged_minus_unbridged": [],
            "bridged_minus_legacy": [],
        }
        for case_id in CASE_ORDER:
            cell = paired_metrics[field][case_id]
            if cell.get("applicable"):
                for key in deltas:
                    deltas[key].append(cell[key])
        paired_metrics[field]["_summary"] = {
            key: round(sum(values) / len(values), 6) if values else None
            for key, values in deltas.items()
        }
        paired_metrics[field]["_summary"]["direction"] = "higher is better for every metric"

    # --- mechanical per-case contrast labels on the primary outcomes ---------------
    fer = paired_metrics["final_evidence_recall"]
    ccr = paired_metrics["combined_candidate_recall"]
    case_contrasts = {}
    for case_id in CASE_ORDER:
        f = fer[case_id]
        c = ccr[case_id]
        if not f.get("applicable"):
            case_contrasts[case_id] = {
                "final_evidence": "NOT_APPLICABLE_INSUFFICIENT_EVIDENCE_CONTROL",
                "combined_pool": "NOT_APPLICABLE_INSUFFICIENT_EVIDENCE_CONTROL",
            }
            continue
        case_contrasts[case_id] = {
            "legacy_dependency_final": f["legacy_minus_ablation"] > 0,
            "unbridged_recovery_final": f["unbridged_minus_ablation"] > 0,
            "incremental_bridge_final": f["bridged_minus_unbridged"] > 0,
            "bridge_regression_final": f["bridged_minus_unbridged"] < 0,
            "bridged_legacy_parity_final": f["bridged_minus_legacy"] >= 0,
            "incremental_bridge_pool": c["bridged_minus_unbridged"] > 0,
            "pattern": (
                "legacy_dependency_bridge_recovered_final"
                if f["legacy_minus_ablation"] > 0 and f["bridged_minus_unbridged"] > 0
                else "legacy_dependency_unbridged_recovered_final"
                if f["legacy_minus_ablation"] > 0 and f["unbridged_minus_ablation"] > 0
                else "legacy_dependency_no_structured_recovery_final"
                if f["legacy_minus_ablation"] > 0
                else "no_legacy_dependency"
            ),
        }

    # --- bridge diagnostics summary across BRIDGED runs -----------------------------
    bridge_summary: dict[str, Any] = {
        "total_bridged_candidates": 0,
        "cases_with_bridge_activity": [],
        "cases_with_zero_bridge_activity": [],
        "total_deduplicated_overlaps": 0,
        "total_graph_candidates_displaced": 0,
        "cases_with_displacement": [],
        "cases_with_traversal_budget_exhaustion": [],
        "cases_with_structural_ambiguity": [],
        "cases_with_provenance_failure": [],
        "cases_with_version_conflict": [],
        "cases_with_ranked_out_bridged_evidence": [],
        "per_case": {},
    }
    for case_id in CASE_ORDER:
        record = next(r for r in records if r["arm"] == "STRUCTURED_BRIDGED" and r["case_id"] == case_id)
        diagnostics = record.get("bridge_displacement_diagnostics") or {}
        counters = record.get("structured_diagnostic_counters") or {}
        receipts = record.get("structured_reachability_receipts") or []
        per_case = {
            "bridged_candidate_count": diagnostics.get("bridged_candidate_count", 0),
            "bridged_candidate_ranked_out_at_cap": counters.get(
                "bridged_candidate_ranked_out_count", 0
            ),
            "graph_candidates_displaced_by_prefix": diagnostics.get(
                "graph_candidates_displaced_by_prefix", 0
            ),
            "deduplicated_overlap_count": diagnostics.get("deduplicated_overlap_count", 0),
            "budget_exhaustion": any(
                item.get("reachability_status") == "TRAVERSAL_BUDGET_EXHAUSTED" for item in receipts
            ),
            "structural_ambiguity": "STRUCTURAL_PATH_AMBIGUOUS"
            in json.dumps(record.get("structured_reachability_receipts") or []),
            "provenance_failure": any(
                (item.get("bridge_status") or "").startswith("GOVERNED_PROVENANCE_NOT_FOUND")
                or (item.get("bridge_status") or "").startswith("GOVERNED_PROVENANCE_INVALID")
                for item in record.get("structured_bridge_receipts") or []
            ),
            "version_conflict": "VERSION_SCOPE_CONFLICT"
            in json.dumps(record.get("structured_bridge_receipts") or []),
        }
        bridge_summary["total_bridged_candidates"] += per_case["bridged_candidate_count"]
        bridge_summary["total_deduplicated_overlaps"] += per_case["deduplicated_overlap_count"]
        bridge_summary["total_graph_candidates_displaced"] += per_case[
            "graph_candidates_displaced_by_prefix"
        ]
        if per_case["bridged_candidate_count"] > 0:
            bridge_summary["cases_with_bridge_activity"].append(case_id)
        else:
            bridge_summary["cases_with_zero_bridge_activity"].append(case_id)
        if per_case["graph_candidates_displaced_by_prefix"] > 0:
            bridge_summary["cases_with_displacement"].append(case_id)
        if per_case["budget_exhaustion"]:
            bridge_summary["cases_with_traversal_budget_exhaustion"].append(case_id)
        if per_case["structural_ambiguity"]:
            bridge_summary["cases_with_structural_ambiguity"].append(case_id)
        if per_case["provenance_failure"]:
            bridge_summary["cases_with_provenance_failure"].append(case_id)
        if per_case["version_conflict"]:
            bridge_summary["cases_with_version_conflict"].append(case_id)
        if per_case["bridged_candidate_ranked_out_at_cap"] > 0:
            bridge_summary["cases_with_ranked_out_bridged_evidence"].append(case_id)
        bridge_summary["per_case"][case_id] = per_case

    # --- structured receipts for the positive cases (committed audit trail) --------
    positive_receipts = {}
    for case_id in ("g036", "g021"):
        record = next(r for r in records if r["arm"] == "STRUCTURED_BRIDGED" and r["case_id"] == case_id)
        positive_receipts[case_id] = {
            "reachability_receipts_compact": compact_reachability(
                record.get("structured_reachability_receipts")
            ),
            "bridge_receipts_compact": compact_bridge_receipts(
                record.get("structured_bridge_receipts")
            ),
            "displacement_diagnostics": record.get("bridge_displacement_diagnostics"),
            "diagnostic_counters": record.get("structured_diagnostic_counters"),
        }

    # --- per-case/per-arm results ----------------------------------------------------
    case_results = []
    for case_id in CASE_ORDER:
        arms_out = {}
        for arm in ARM_ORDER:
            record = next(r for r in records if r["arm"] == arm and r["case_id"] == case_id)
            metrics = record.get("metrics") or {}
            treatment = record.get("treatment_receipt") or {}
            arms_out[arm] = {
                "retrieval_receipt_ref": {"run_id": RUN_ID, "arm": arm, "case_id": case_id},
                "treatment_receipt": treatment,
                "metrics": {
                    field: metrics.get(field) for field in METRIC_FIELDS
                },
                "top10_object_ids": record.get("top10_object_ids"),
                "final_evidence_object_ids": record.get("final_evidence_object_ids"),
                "bridge_displacement_diagnostics": (
                    record.get("bridge_displacement_diagnostics")
                    if arm == "STRUCTURED_BRIDGED"
                    else None
                ),
                "structured_diagnostic_counters": (
                    record.get("structured_diagnostic_counters")
                    if arm in ("STRUCTURED_UNBRIDGED", "STRUCTURED_BRIDGED")
                    else None
                ),
            }
        case_results.append(
            {
                "case_id": case_id,
                "dataset": next(r["dataset"] for r in records if r["case_id"] == case_id),
                "case_role": CASE_ROLES[case_id],
                "bound_rule_id": next(r["bound_rule_id"] for r in records if r["case_id"] == case_id),
                "arms": arms_out,
                "contrast_labels": case_contrasts[case_id],
                "interpretation": CASE_INTERPRETATION[case_id],
            }
        )

    # --- safety counters and call accounting -----------------------------------------
    safety_verification = []
    for record in records:
        if record["arm"] in ("STRUCTURED_UNBRIDGED", "STRUCTURED_BRIDGED"):
            counters = record.get("structured_diagnostic_counters") or {}
            for key in SAFETY_COUNTER_KEYS:
                assert counters.get(key) == 0, (
                    f"safety counter {key} nonzero in {record['case_id']}/{record['arm']}"
                )
            safety_verification.append(
                {"case_id": record["case_id"], "arm": record["arm"], "all_zero": True}
            )
    call_totals: Counter[str] = Counter()
    for record in records:
        for key, value in (record.get("call_accounting") or {}).items():
            if isinstance(value, (int, float)):
                call_totals[key] += value

    # --- assemble artifact -------------------------------------------------------------
    artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D3.5-A2",
        "stage_name": "D3.5-A2 — Focused Evidence-Link Recovery Validation",
        "status": "COMPLETE / " + VERDICT,
        "verdict": VERDICT,
        "verdict_scope": (
            "valid, complete frozen four-arm comparison. PARTIAL: the bridge is validated as a "
            "bounded governed pool-level injection mechanism (Mechanisms A+B observed working "
            "with receipts, controls unharmed) but NOT validated as an end-to-end "
            "final-evidence recovery mechanism (zero incremental final-evidence recall on both "
            "positive cases under the frozen ranking configuration)."
        ),
        "scientific_question": (
            "Does the frozen generic structured evidence-link bridge recover useful "
            "source-native evidence beyond the existing synchronized structured baseline, "
            "while avoiding material regressions or uncontrolled expansion?"
        ),
        "execution_identity": {
            "execution_manifest": "evaluation/d3_5_a2_focused_evidence_link_recovery_manifest.json",
            "execution_manifest_sha256": run_manifest.get("execution_manifest_sha256"),
            "pre_outcome_freeze_commit": manifest.get("execution_head"),
            "git_head_during_run": run_manifest.get("git_head"),
            "frozen_implementation_sha": FROZEN_IMPLEMENTATION_SHA,
            "implementation_identity_diff_lines": run_manifest.get(
                "implementation_identity_diff_lines"
            ),
            "runner": "evaluation/scripts/d3_5_a2_runner.py",
            "run_id": RUN_ID,
            "raw_records": f"data/evaluation/runs/{RUN_ID}/records.jsonl",
        },
        "preregistration_identity": {
            "structured_artifact": "evaluation/d3_5_a0_structured_evidence_link_design.json",
            "sha256": manifest.get("configuration_identities", {}).get("frozen_a0_design_sha256"),
            "a1_artifact": "evaluation/d3_5_a1_bounded_structured_evidence_link_bridging_prototype.json",
            "a1_artifact_sha256": manifest.get("configuration_identities", {}).get(
                "frozen_a1_artifact_sha256"
            ),
        },
        "materialization_identity": {
            "final_repository_d1_sha": manifest.get("final_repository_d1_sha"),
            "development_materialization_source_sha": manifest.get(
                "development_materialization_source_sha"
            ),
            "receipt_reference": manifest.get("development_materialization_receipt_reference"),
            "database_role": manifest.get("database_role"),
            "database_target_sanitized": manifest.get("database_target_sanitized"),
        },
        "source_index_identities": {
            "source_manifest_sha256": manifest.get("source_manifest_identity", {}).get("sha256"),
            "qdrant_collection": manifest.get("retrieval_index_identities", {}).get(
                "qdrant_collection"
            ),
            "index_fingerprint": manifest.get("retrieval_index_identities", {}).get(
                "index_fingerprint"
            ),
            "qdrant_points": manifest.get("retrieval_index_identities", {}).get("qdrant_points"),
            "sql_objects": manifest.get("retrieval_index_identities", {}).get("sql_objects"),
        },
        "outcome_exposure": {
            "before_first_formal_cell": "NOT_STARTED (manifest committed pre-outcome at "
            + str(manifest.get("execution_head"))
            + ")",
            "started_at_utc": run_manifest.get("started_at_utc"),
            "finished_at_utc": run_manifest.get("finished_at_utc"),
            "after_valid_complete_comparison": "COMPLETE",
        },
        "frozen_arms": manifest.get("frozen_arms", {}).get("definitions"),
        "focused_rule_ids": manifest.get("focused_shortcut_ids"),
        "frozen_cases": CASE_ORDER,
        "case_roles": CASE_ROLES,
        "execution_order": {
            "contract": "case-major: for each case in frozen case order, run the four arms in frozen arm order",
            "cell_sequence": [
                {"sequence": record["execution_sequence"], "case_id": record["case_id"], "arm": record["arm"]}
                for record in records
            ],
        },
        "run_counts": {
            "total_executions": 24,
            "per_arm": {arm: 6 for arm in ARM_ORDER},
            "valid_cells": 24,
            "infrastructure_failures": 0,
            "retries": 0,
            "discretionary_reruns": 0,
        },
        "call_counts": {
            "analyzer_generation_calls": 24,
            "reranker_generation_calls": 24,
            "generation_calls_total": call_totals.get("generation_calls"),
            "embedding_calls": call_totals.get("embedding_calls"),
            "model_calls_total": call_totals.get("model_calls"),
            "token_usage": call_totals.get("token_usage"),
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "note": "normal frozen-pipeline retrieval calls only (analyzer + reranker generation, dense embeddings); no extra LLM diagnostics were introduced",
        },
        "storage_writes": {
            "postgresql_d1_writes": 0,
            "d1_ingestion": 0,
            "d1_reingestion": 0,
            "qdrant_writes": 0,
            "note": "the frozen development materialization was not mutated before, during, or after the comparison",
        },
        "protected_dataset_access": {
            "novel_validation": "UNSEEN",
            "novel_validation_cases_run": 0,
            "novel_holdout": "SEALED_UNSEEN",
            "novel_holdout_cases_run": 0,
        },
        "arm_summaries": arm_summaries,
        "paired_metrics": paired_metrics,
        "case_results": case_results,
        "bridge_diagnostic_summary": bridge_summary,
        "positive_case_bridge_receipts": positive_receipts,
        "primary_causal_conclusions": {
            "shortcut_dependency (LEGACY - ABLATION)": {
                "final_evidence_recall": "+0.4 mean (g036 +1.0, g021 +1.0): the two focused shortcuts remain materially responsible for useful retrieval on both direct cases",
            },
            "unbridged_structured_contribution (STRUCTURED_UNBRIDGED - ABLATION)": {
                "final_evidence_recall": "0.0: the synchronized final D1 plus the pre-D3.5 structured path recovered nothing at final-evidence level (g021's Mechanism-C knowledge did not surface through the unbridged path either)",
                "combined_candidate_recall": "0.0",
            },
            "incremental_bridge_effect (STRUCTURED_BRIDGED - STRUCTURED_UNBRIDGED)": {
                "final_evidence_recall": "0.0: no incremental final-evidence recovery",
                "combined_candidate_recall": "+0.3 mean (g036 +1.0, g021 +0.5): a real, causally identifiable pool-level contribution",
                "decomposition": "the bridge demonstrably materializes the governed provenance into source-native candidates, but they enter only the graph channel and score below the frozen fused top-30 rerank pool cutoff",
            },
            "final_legacy_parity (STRUCTURED_BRIDGED - LEGACY)": {
                "final_evidence_recall": "-0.4: bridged does not reach legacy parity on the positive cases; controls unchanged",
            },
            "identifiability_boundary_respected": (
                "STRUCTURED_BRIDGED - ABLATION (+0.3 combined / 0.0 final) is reported only as the "
                "combined final-D1 + old-structured + bridge contribution and is never described as "
                "a pure bridge effect; the pure bridge effect is BRIDGED - UNBRIDGED"
            ),
        },
        "safety_counters": {
            "per_execution_verification": "all five prohibited-use counters verified zero in all 12 structured-arm executions",
            "violations": 0,
        },
        "anti_shortcut_audit": {
            "case_id_to_file_mapping_count": 0,
            "question_id_to_path_count": 0,
            "bound_rule_id_to_route_count": 0,
            "expected_evidence_to_d1_link_count": 0,
            "legacy_payload_reuse_count": 0,
            "evaluation_metadata_runtime_use_count": 0,
            "focused_rule_ids_usage": "arm suppression/configuration only; no semantic payload reuse",
            "static_check": "runtime files (src/panda_agent/retrieval.py, src/panda_agent/d3_structured.py) unchanged since frozen commit 9b5a849 (git diff empty); focused rule IDs appear only in D3_5ExperimentConfig/d3_structured.py suppression constants",
            "runtime_treatment_receipt_check": "all 24 per-cell treatment receipts match the frozen arm flag matrix exactly",
        },
        "run_variance_note": (
            "arms are independent frozen-path executions; temperature-0 analyzer/reranker "
            "variance produced metric-neutral selection differences (n006 R@5 0.0 vs 0.5 "
            "across arms with final evidence identical; same class as D3-A2 n022 e3). Final "
            "evidence and R@10/20 are arm-stable on every control case."
        ),
        "historical_d3_comparison_caveat": (
            "historical D3 STRUCTURED ran on the deployed 22/16/0 materialization with a "
            "different three-arm contract and is not interchangeable with "
            "STRUCTURED_UNBRIDGED on the synchronized 24/16/1/2 materialization; no causal "
            "deltas were computed across the two experiments"
        ),
        "overall_interpretation": OVERALL_INTERPRETATION,
        "binding_constraint_analysis": {
            "observed": (
                "bridged candidates enter the graph channel via prefix merge "
                "(g036 ana_dpm.C at graph position 3/16; g021 prod_sim_hvmaps.C at graph "
                "position 9/20) but are single-channel graph candidates scored with weight "
                "0.8/(60+rank); both fell below the frozen fused top-30 rerank pool cutoff "
                "against exact(2.0)/dense(1.0)/sparse(1.0)/paper(1.15)/workflow(1.2) "
                "multi-channel competition and were never reranked or selected"
            ),
            "not_the_constraint": (
                "reachability (both preregistered paths reached with receipts), materialization "
                "(exact source-native candidates injected), candidate caps (no cap bound on the "
                "required candidates), or source/version qualification (all bridged candidates "
                "carried exact frozen source versions)"
            ),
            "repair_belongs_to": "a separately authorized post-A2 stage; no ranking/fusion/bridge change is permitted inside A2",
        },
        "scientific_decision": {
            "verdict": VERDICT,
            "d3_5_lifecycle": LIFECYCLE_DECISION,
            "d4_gate": (
                "BLOCKED: D4 requires D3.5 bridge validated by A2; the end-to-end validation "
                "criterion was not met (no incremental final-evidence recovery on the positive "
                "cases), so D4 remains NOT_STARTED"
            ),
            "mechanism_decomposition": {
                "mechanism_A_bounded_reachability": "VALIDATED_OBSERVED (preregistered paths reached with receipts; atomic Tier-D ambiguity admission observed on g020; no budget exhaustion or ambiguity collapse)",
                "mechanism_B_provenance_materialization": "VALIDATED_OBSERVED (exact governed provenance materialized into source-native candidates with exact frozen source versions; VERSION_SCOPE_CONFLICT never triggered)",
                "mechanism_C_governed_coverage_use": "PARTIALLY_OBSERVED (g021 e1 prod_sim_hvmaps.C reached and materialized via the Mechanism-C PARAMETERIZES edge; g021 e2 PndTargetGenerator.cxx unreachable because its provenance-bearing edge originates from file_pattern.restgas_profile_input, which was not a D2 seed in this question)",
                "end_to_end_final_evidence_recovery": "NOT_VALIDATED (bridge candidates never survive the frozen fusion/rerank/selector into final evidence)",
            },
        },
        "limitations": [
            "six focused cases with g041 metric-inapplicable in all arms; aggregates have denominator 5 and case-level heterogeneity is reported in full",
            "temperature-0 analyzer/reranker variance produces within-case R@5/MRR spread across independent arm executions (n006); final-evidence outcomes were arm-stable",
            "the g020 control exercised the bridge through an ambiguous Tier-D seed and displaced all 20 graph slots (outcome-neutral); displacement behavior under heavier structured reach remains bounded by the graph cap but was not stress-tested beyond this",
            "g021 e2 (PndTargetGenerator.cxx) was structurally unreachable under the frozen seed resolution and one-transition budget, so the bridge could not materialize it in this question",
            "single frozen materialization (24/16/1/2) and single frozen ranking configuration; results do not speak to alternative fusion weights or channel budgets",
        ],
        "next_stage": {
            "exact_next_task": "separately authorized post-A2 decision stage (no D4 start; D4 blocked by the A2 verdict)",
            "candidate_directions_authored_not_authorized": (
                "the binding constraint is downstream of the bridge: a future authorized stage "
                "would have to decide how provenance-backed source-native candidates can compete "
                "in fusion/reranking without violating the frozen authority boundaries; any such "
                "change requires a new preregistration and is not part of A2"
            ),
        },
    }

    # --- internal consistency checks ---------------------------------------------------
    assert artifact["run_counts"]["total_executions"] == 24
    assert len(artifact["case_results"]) == 6
    assert bridge_summary["cases_with_bridge_activity"] == ["g036", "g021", "g020"]
    assert bridge_summary["total_bridged_candidates"] == 43
    assert bridge_summary["total_graph_candidates_displaced"] == 24
    assert bridge_summary["cases_with_traversal_budget_exhaustion"] == []
    assert bridge_summary["cases_with_structural_ambiguity"] == []
    assert bridge_summary["cases_with_version_conflict"] == []
    assert bridge_summary["cases_with_zero_bridge_activity"] == ["n006", "g041", "n004"]
    fer_summary = paired_metrics["final_evidence_recall"]["_summary"]
    assert fer_summary["legacy_minus_ablation"] == 0.4
    assert fer_summary["unbridged_minus_ablation"] == 0.0
    assert fer_summary["bridged_minus_unbridged"] == 0.0
    assert fer_summary["bridged_minus_legacy"] == -0.4
    ccr_summary = paired_metrics["combined_candidate_recall"]["_summary"]
    assert ccr_summary["bridged_minus_unbridged"] == 0.3
    assert ccr_summary["unbridged_minus_ablation"] == 0.0
    assert arm_summaries["STRUCTURED_BRIDGED"]["metrics"]["final_evidence_recall"]["mean"] == 0.5
    assert arm_summaries["STRUCTURED_UNBRIDGED"]["metrics"]["final_evidence_recall"]["mean"] == 0.5
    assert arm_summaries["LEGACY"]["metrics"]["final_evidence_recall"]["mean"] == 0.9
    assert arm_summaries["ABLATION"]["metrics"]["final_evidence_recall"]["mean"] == 0.5
    # treatment receipts must match the frozen flag matrix
    expected_flags = {
        "LEGACY": (False, False, False),
        "ABLATION": (False, False, True),
        "STRUCTURED_UNBRIDGED": (True, False, True),
        "STRUCTURED_BRIDGED": (True, True, True),
    }
    for record in records:
        treatment = record["treatment_receipt"]
        expected = expected_flags[record["arm"]]
        assert treatment["structured_treatment_enabled"] is expected[0]
        assert treatment["bridge_enabled"] is expected[1]
        assert treatment["selected_legacy_rules_suppressed"] is expected[2]
        assert treatment["focused_rule_ids"] == ["event_poca_handoff", "restgas_profile_workflow"]
    assert artifact["scientific_decision"]["verdict"] == VERDICT

    output_path = (
        project_root / "evaluation" / "d3_5_a2_focused_evidence_link_recovery_validation.json"
    )
    output_path.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {output_path}")
    print("verdict:", VERDICT)
    print("arm final-evidence means:", {arm: arm_summaries[arm]["metrics"]["final_evidence_recall"]["mean"] for arm in ARM_ORDER})
    print("arm combined-pool means:", {arm: arm_summaries[arm]["metrics"]["combined_candidate_recall"]["mean"] for arm in ARM_ORDER})


if __name__ == "__main__":
    main()
