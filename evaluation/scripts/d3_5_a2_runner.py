"""D3.5-A2 frozen four-arm focused recovery comparison runner (evaluation-only).

Executes the frozen D3.5-A2 contract exactly once per (case, arm) cell in the
frozen case-major order (six cases, each over LEGACY -> ABLATION ->
STRUCTURED_UNBRIDGED -> STRUCTURED_BRIDGED) using the frozen D3.5-A1
retrieval implementation.  The runner adds no retrieval semantics: it passes
only the ordinary question plus ``D3_5ExperimentConfig`` into the runtime,
captures retrieval receipts (including the frozen structured reachability and
evidence-bridge receipts and the seven displacement diagnostics), and
computes the preregistered metrics with the repository's existing
deterministic evaluator semantics.

Evaluation metadata (case_id, dataset, bound_rule_id, comparison_role,
expected status, required evidence) is used for scoring and reporting only
and never forwarded to the runtime.

CLI:
    PYTHONPATH=src python evaluation/scripts/d3_5_a2_runner.py \
        --project-root . \
        --run-id d3_5_a2_<suffix>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from panda_agent.d3_structured import D3_5Arm, D3_5ExperimentConfig
from panda_agent.evaluation import (
    apply_mode_metric_semantics,
    deterministic_case_metrics,
    load_gold_dataset,
)
from panda_agent.evaluation_runner import _retrieval_result, load_object_lookup
from panda_agent.retrieval import Retriever

FROZEN_A0_DESIGN = "evaluation/d3_5_a0_structured_evidence_link_design.json"
FROZEN_D3_PREREGISTRATION = "evaluation/d3_a0_shortcut_migration_preregistration.json"
FROZEN_IMPLEMENTATION_SHA = "9b5a84996c30eaf1a297924b36452a90fe6d84d2"
ARM_ORDER = ("LEGACY", "ABLATION", "STRUCTURED_UNBRIDGED", "STRUCTURED_BRIDGED")
CASE_ORDER = ("g036", "g021", "n006", "g041", "g020", "n004")
GOLD_DATASET = "evaluation/benchmarks/v2_6/gold_questions.yaml"
NOVEL_DEV_DATASET = "evaluation/novel/v1/novel_dev.yaml"

# Stored per-record text is a reference; full text is recoverable from the
# normalized corpus by object_id.
_EVIDENCE_TEXT_SNIPPET_CHARS = 240


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head(project_root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def _implementation_identity_diff(project_root: Path) -> list[str]:
    completed = subprocess.run(
        [
            "git", "diff", FROZEN_IMPLEMENTATION_SHA, "--",
            "src/panda_agent/retrieval.py",
            "src/panda_agent/d3_structured.py",
        ],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.splitlines()


def _trim_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    trimmed: list[dict[str, Any]] = []
    for item in evidence:
        trimmed.append(
            {
                "evidence_id": item.get("evidence_id"),
                "object_id": item.get("object_id"),
                "source_id": item.get("source_id"),
                "source_version_id": item.get("source_version_id"),
                "locator": item.get("locator"),
                "retrieval_channels": item.get("retrieval_channels"),
                "score": item.get("score"),
                "text_snippet": (item.get("text") or "")[:_EVIDENCE_TEXT_SNIPPET_CHARS],
            }
        )
    return trimmed


def _top20_detail(
    ranked_ids: list[str], object_lookup: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    detail = []
    for rank, object_id in enumerate(ranked_ids[:20], start=1):
        record = object_lookup.get(object_id) or {}
        detail.append(
            {
                "rank": rank,
                "object_id": object_id,
                "source_id": record.get("source_id"),
                "source_version_id": record.get("source_version_id"),
                "object_type": record.get("object_type"),
                "locator": record.get("locator"),
            }
        )
    return detail


def _compact_plan(plan: dict[str, Any]) -> dict[str, Any]:
    keep = (
        "intent",
        "target_repositories",
        "version_repositories",
        "resolved_versions",
        "symbols",
        "concepts",
        "concept_scopes",
        "paper_page_hints",
        "required_source_types",
        "source_budgets",
        "requested_versions",
        "premise_corrections",
        "resolved_aliases",
    )
    compact = {key: plan.get(key) for key in keep if plan.get(key) not in (None, [], {})}
    diagnostics = plan.get("analysis_diagnostics") or {}
    compact["d3_experiment"] = diagnostics.get("d3_experiment")
    return compact


def _build_record(
    *,
    sequence: int,
    arm: str,
    manifest_case: dict[str, Any],
    question: Any,
    query: str,
    implementation_sha: str,
    duration_seconds: float,
    stats_delta: dict[str, int],
    diagnostics: dict[str, Any] | None,
    metrics: dict[str, Any] | None,
    object_lookup: dict[str, dict[str, Any]],
    error: dict[str, Any] | None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "execution_sequence": sequence,
        "arm": arm,
        "case_id": manifest_case["case_id"],
        "dataset": manifest_case["dataset"],
        "case_role": manifest_case["case_role"],
        "bound_rule_id": manifest_case["bound_rule_id"],
        "historical_d3_comparison_role": manifest_case["historical_d3_comparison_role"],
        "question_identity": {
            "query": query,
            "query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
        },
        "retrieval_implementation_commit": implementation_sha,
        "execution": {
            "started_at_utc": None,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration_seconds, 3),
        },
        "call_accounting": stats_delta,
        "error": error,
    }
    if diagnostics is None:
        return record

    evidence = diagnostics.get("evidence", [])
    ranked_ids = diagnostics.get("ranked_object_ids", [])
    d3_receipt = diagnostics.get("d3_experiment") or {}
    plan_diagnostics = (diagnostics.get("plan") or {}).get("analysis_diagnostics") or {}
    plan_d3 = plan_diagnostics.get("d3_experiment") or {}
    record.update(
        {
            "treatment_receipt": {
                "d3_5_arm": d3_receipt.get("d3_arm"),
                "focused_rule_ids": d3_receipt.get("selected_rule_ids"),
                "structured_treatment_enabled": d3_receipt.get(
                    "structured_treatment_enabled"
                ),
                "bridge_enabled": d3_receipt.get("bridge_enabled"),
                "selected_legacy_rules_suppressed": d3_receipt.get(
                    "selected_legacy_rules_suppressed"
                ),
                "suppressed_selected_rule_ids": d3_receipt.get(
                    "suppressed_selected_rule_ids"
                ),
                "matched_active_rule_ids": plan_d3.get("matched_active_rule_ids"),
                "focused_shortcut_hit_count": (plan_d3.get("diagnostic_counters") or {}).get(
                    "selected_legacy_shortcut_hit_count"
                ),
            },
            "plan_summary": _compact_plan(diagnostics.get("plan", {})),
            "channel_rankings": diagnostics.get("rankings", {}),
            "channel_candidate_counts": {
                key: len(value) for key, value in (diagnostics.get("rankings") or {}).items()
            },
            "fusion_top30": diagnostics.get("fusion_scores", {}),
            "reranked_object_ids": diagnostics.get("reranked_object_ids", []),
            "ranked_object_ids": ranked_ids,
            "top5_object_ids": ranked_ids[:5],
            "top10_object_ids": ranked_ids[:10],
            "top20_object_ids": ranked_ids[:20],
            "top20_detail": _top20_detail(ranked_ids, object_lookup),
            "final_evidence": _trim_evidence(evidence),
            "final_evidence_object_ids": [
                item.get("object_id") for item in evidence if item.get("object_id")
            ],
            "excluded": diagnostics.get("excluded", []),
            "backfill_admissions": diagnostics.get("backfill_admissions", []),
            "d3_5_experiment": d3_receipt,
            "structured_resolution_receipt": d3_receipt.get("resolution_receipt"),
            "structured_reachability_receipts": d3_receipt.get("reachability_receipts"),
            "structured_bridge_receipts": d3_receipt.get("bridge_receipts"),
            "bridge_displacement_diagnostics": d3_receipt.get(
                "displacement_diagnostics"
            ),
            "structured_diagnostic_counters": d3_receipt.get("diagnostic_counters"),
            "dense_candidates_ref": {"count": len((diagnostics.get("dense_candidates") or {}).get("raw") or [])},
            "sparse_candidates_ref": {"count": len((diagnostics.get("sparse_candidates") or {}).get("raw") or [])},
            "metrics": metrics,
        }
    )
    return record


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    head = _git_head(project_root)
    drift = _implementation_identity_diff(project_root)
    if drift:
        print(
            "IMPLEMENTATION_IDENTITY_DRIFT: frozen runtime files differ from "
            f"{FROZEN_IMPLEMENTATION_SHA}; refusing to run.",
            file=sys.stderr,
        )
        sys.exit(2)

    manifest_path = project_root / "evaluation" / "d3_5_a2_focused_evidence_link_recovery_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("formal_outcome_exposure") is not False:
        raise ValueError("execution manifest is not marked pre-outcome")
    manifest_head = manifest.get("execution_head")
    merge_base = subprocess.run(
        ["git", "merge-base", "--is-ancestor", manifest_head, head],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if merge_base.returncode != 0:
        raise ValueError(
            f"execution manifest freeze commit {manifest_head} is not an ancestor of HEAD {head}"
        )
    frozen_state_drift = subprocess.run(
        [
            "git", "diff", manifest_head, "--",
            "src/",
            "configs/",
        ],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    if frozen_state_drift.stdout.strip():
        raise ValueError(
            f"runtime/D1/config state drifted since the manifest freeze commit {manifest_head}"
        )
    frozen_case_order = tuple(manifest["frozen_cases"]["case_ids_in_execution_order"])
    frozen_arm_order = tuple(manifest["frozen_arms"]["arm_order"])
    if frozen_case_order != CASE_ORDER or frozen_arm_order != ARM_ORDER:
        raise ValueError("manifest arm/case order does not match the frozen runner order")

    design = json.loads((project_root / FROZEN_A0_DESIGN).read_text(encoding="utf-8"))
    a2_contract = design["d3_5_a2_contract"]
    case_roles = {
        item["case_id"]: item["role"] for item in a2_contract["positive_cases"]
    }
    case_roles.update(
        {item["case_id"]: item["role"] for item in a2_contract["controls"]}
    )

    d3_prereg = json.loads(
        (project_root / FROZEN_D3_PREREGISTRATION).read_text(encoding="utf-8")
    )
    historical_roles = {
        case["case_id"]: case["comparison_role"]
        for case in d3_prereg["comparison_cases"]
    }
    historical_datasets = {
        case["case_id"]: case["dataset"] for case in d3_prereg["comparison_cases"]
    }
    historical_rules = {
        case["case_id"]: case["bound_rule_id"] for case in d3_prereg["comparison_cases"]
    }
    historical_group_counts = {
        case["case_id"]: case["required_evidence_group_count"]
        for case in d3_prereg["comparison_cases"]
    }

    manifest_cases = []
    for case_id in CASE_ORDER:
        manifest_cases.append(
            {
                "case_id": case_id,
                "dataset": historical_datasets[case_id],
                "case_role": case_roles[case_id],
                "bound_rule_id": historical_rules[case_id],
                "historical_d3_comparison_role": historical_roles[case_id],
                "required_evidence_group_count": historical_group_counts[case_id],
            }
        )

    gold = load_gold_dataset(project_root / GOLD_DATASET)
    novel = load_gold_dataset(project_root / NOVEL_DEV_DATASET)
    questions = {item.id: item for item in [*gold.questions, *novel.questions]}

    for case in manifest_cases:
        question = questions.get(case["case_id"])
        if question is None:
            raise ValueError(f"frozen case missing from datasets: {case['case_id']}")
        if len(question.required_evidence_groups) != case["required_evidence_group_count"]:
            raise ValueError(f"evidence group count mismatch for {case['case_id']}")

    object_lookup = load_object_lookup(project_root)

    run_dir = project_root / "data" / "evaluation" / "runs" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    records_path = run_dir / "records.jsonl"
    completed: set[tuple[str, str]] = set()
    if args.resume and records_path.exists():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            record = json.loads(line)
            if record.get("error") is None:
                completed.add((record["arm"], record["case_id"]))

    run_manifest = {
        "run_id": args.run_id,
        "checkpoint": "D3.5-A2",
        "purpose": "frozen four-arm focused evidence-link recovery comparison (retrieval-only)",
        "git_head": head,
        "frozen_implementation_sha": FROZEN_IMPLEMENTATION_SHA,
        "implementation_identity_diff_lines": len(drift),
        "execution_manifest": "evaluation/d3_5_a2_focused_evidence_link_recovery_manifest.json",
        "execution_manifest_sha256": _sha256_file(manifest_path),
        "frozen_a0_design_sha256": _sha256_file(project_root / FROZEN_A0_DESIGN),
        "frozen_case_order": list(CASE_ORDER),
        "frozen_arm_order": list(ARM_ORDER),
        "execution_order": "case-major: for each case in frozen case order, run the four arms in frozen arm order",
        "gold_dataset_sha256": _sha256_file(project_root / GOLD_DATASET),
        "novel_dev_dataset_sha256": _sha256_file(project_root / NOVEL_DEV_DATASET),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "resumed": bool(completed),
    }
    (run_dir / "run_manifest.json").write_text(
        json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8"
    )

    engine = Retriever(project_root)
    attempts: list[dict[str, Any]] = []
    sequence = 0

    with records_path.open("a", encoding="utf-8") as records_file:
        # Frozen case-major execution order (manifest section: 24-cell order).
        for case in manifest_cases:
            for arm in ARM_ORDER:
                sequence += 1
                key = (arm, case["case_id"])
                if key in completed:
                    print(json.dumps({"sequence": sequence, "arm": arm, "case_id": case["case_id"], "skipped": "already_completed"}), flush=True)
                    continue
                config = D3_5ExperimentConfig.for_arm(D3_5Arm(arm))
                query = questions[case["case_id"]].query
                stats_before = engine.vertex.stats_snapshot()
                started = time.perf_counter()
                started_at = datetime.now(timezone.utc).isoformat()
                diagnostics: dict[str, Any] | None = None
                metrics: dict[str, Any] | None = None
                error: dict[str, Any] | None = None
                try:
                    diagnostics = engine.retrieve(query, d3_config=config)
                    result = _retrieval_result(diagnostics)
                    metrics = deterministic_case_metrics(
                        questions[case["case_id"]], result, diagnostics, object_lookup
                    )
                    metrics = apply_mode_metric_semantics(
                        metrics, mode="retrieval", external_judge=False
                    )
                except Exception as exc:  # noqa: BLE001 - recorded, never repaired here
                    error = {
                        "error_type": type(exc).__name__,
                        "message": str(exc)[:2000],
                    }
                duration = time.perf_counter() - started
                stats_delta = engine.vertex.stats_delta(stats_before)
                record = _build_record(
                    sequence=sequence,
                    arm=arm,
                    manifest_case=case,
                    question=questions[case["case_id"]],
                    query=query,
                    implementation_sha=FROZEN_IMPLEMENTATION_SHA,
                    duration_seconds=duration,
                    stats_delta=stats_delta,
                    diagnostics=diagnostics,
                    metrics=metrics,
                    object_lookup=object_lookup,
                    error=error,
                )
                record["execution"]["started_at_utc"] = started_at
                if error is not None:
                    attempts.append(
                        {
                            "arm": arm,
                            "case_id": case["case_id"],
                            "error_type": error["error_type"],
                            "message": error["message"][:500],
                        }
                    )
                records_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                records_file.flush()
                summary_line = {
                    "sequence": sequence,
                    "arm": arm,
                    "case_id": case["case_id"],
                    "status": "error" if error else "ok",
                    "final_evidence_recall": (
                        None
                        if metrics is None
                        else metrics.get("final_evidence_recall")
                    ),
                    "duration_s": round(duration, 1),
                }
                if error:
                    summary_line["error"] = error["error_type"]
                print(json.dumps(summary_line), flush=True)

    finish_manifest = dict(run_manifest)
    finish_manifest["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    finish_manifest["attempts"] = attempts
    finish_manifest["records"] = len(CASE_ORDER) * len(ARM_ORDER)
    (run_dir / "run_manifest.json").write_text(
        json.dumps(finish_manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"run_dir": str(run_dir), "attempts_with_error": len(attempts)}), flush=True)


if __name__ == "__main__":
    main()
