"""Package low-cost, reusable Generalization Phase baselines."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from panda_agent.evaluation import (
    GoldQuestion,
    aggregate_metrics,
    load_gold_dataset,
    load_run_records,
    normalize_run_records,
)
from panda_agent.retrieval_trace import load_retrieval_traces


BOOTSTRAP_DEVELOPMENT_SPLITS = frozenset({"dev", "challenge", "regression"})


def select_stratified_case_ids(dataset_path: Path, size: int) -> list[str]:
    """Select approved English cases evenly by intent and diversely by status/split."""
    if size <= 0:
        raise ValueError("selection size must be positive")
    dataset = load_gold_dataset(dataset_path)
    eligible = sorted(
        (
            item
            for item in dataset.questions
            if item.language == "en" and item.review_status == "approved"
            and item.split in BOOTSTRAP_DEVELOPMENT_SPLITS
        ),
        key=lambda item: item.id,
    )
    if size > len(eligible):
        raise ValueError(f"selection size {size} exceeds {len(eligible)} eligible cases")
    by_intent: dict[str, list[GoldQuestion]] = {}
    for item in eligible:
        by_intent.setdefault(item.intent, []).append(item)

    intent_queues: dict[str, list[GoldQuestion]] = {}
    for intent, items in sorted(by_intent.items()):
        buckets: dict[tuple[str, str], list[GoldQuestion]] = {}
        for item in items:
            buckets.setdefault((item.expected_status.value, item.split), []).append(item)
        queue: list[GoldQuestion] = []
        keys = sorted(buckets)
        while any(buckets.values()):
            for key in keys:
                if buckets[key]:
                    queue.append(buckets[key].pop(0))
        intent_queues[intent] = queue

    selected: list[str] = []
    intents = sorted(intent_queues)
    while len(selected) < size:
        progressed = False
        for intent in intents:
            if intent_queues[intent] and len(selected) < size:
                selected.append(intent_queues[intent].pop(0).id)
                progressed = True
        if not progressed:
            break
    return selected


def _run_payload(project_root: Path, run_id: str) -> dict[str, Any]:
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"evaluation run does not exist: {run_id}")
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    status_path = run_dir / "run_status.json"
    status = (
        json.loads(status_path.read_text(encoding="utf-8"))
        if status_path.is_file()
        else {}
    )
    manifest_records = load_run_records(run_dir)
    records = normalize_run_records(manifest_records, manifest)
    return {
        "run_id": run_id,
        "run_dir": run_dir,
        "manifest": manifest,
        "metrics": aggregate_metrics(records),
        "status": status,
        "records": records,
        "traces": load_retrieval_traces(run_dir),
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, values: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(
            json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n"
            for item in values
        ),
        encoding="utf-8",
    )


def _portable_path(project_root: Path, value: str | Path | None) -> str | None:
    if value is None:
        return None
    path = Path(value)
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _portable_manifest(project_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    portable = json.loads(json.dumps(manifest))
    for field in ("gold_dataset_path", "evaluator_catalog_path"):
        if portable.get(field):
            portable[field] = _portable_path(project_root, portable[field])
    return portable


def _record_ids(payload: dict[str, Any], label: str) -> list[str]:
    ids = [str(item["id"]) for item in payload["records"]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{label} baseline records contain duplicate IDs")
    return ids


def _trace_ids(payload: dict[str, Any], label: str) -> list[str]:
    ids = [str(trace.question_id) for trace in payload["traces"]]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{label} retrieval traces contain duplicate question IDs")
    return ids


def validate_baseline_consistency(
    selection_manifest: dict[str, Any] | None,
    benchmark: dict[str, Any],
    small_e2e: dict[str, Any],
) -> None:
    """Validate package inputs without rerunning or modifying measured output."""
    if benchmark["manifest"].get("mode") != "retrieval":
        raise ValueError("benchmark retrieval baseline must use retrieval mode")
    if small_e2e["manifest"].get("mode") != "qa":
        raise ValueError("small E2E baseline must use qa mode")
    boundaries = small_e2e["manifest"].get("pipeline_boundaries") or {}
    if boundaries.get("external_judge") is not False:
        raise ValueError(
            "small E2E qa manifest must explicitly set pipeline_boundaries.external_judge=false"
        )

    retrieval_ids = _record_ids(benchmark, "retrieval")
    qa_ids = _record_ids(small_e2e, "QA")
    retrieval_trace_ids = _trace_ids(benchmark, "retrieval")
    qa_trace_ids = _trace_ids(small_e2e, "QA")
    if len(retrieval_trace_ids) != len(retrieval_ids) or set(retrieval_trace_ids) != set(
        retrieval_ids
    ):
        raise ValueError("retrieval trace IDs/count do not match retrieval record IDs/count")
    if len(qa_trace_ids) != len(qa_ids) or set(qa_trace_ids) != set(qa_ids):
        raise ValueError("QA trace IDs/count do not match QA record IDs/count")

    if selection_manifest is not None:
        fixed_retrieval = [str(value) for value in selection_manifest["retrieval"]["case_ids"]]
        fixed_qa = [str(value) for value in selection_manifest["qa"]["case_ids"]]
        if len(fixed_retrieval) != len(set(fixed_retrieval)):
            raise ValueError("fixed retrieval manifest contains duplicate IDs")
        if len(fixed_qa) != len(set(fixed_qa)):
            raise ValueError("fixed QA manifest contains duplicate IDs")
        if selection_manifest["retrieval"].get("case_count") != len(fixed_retrieval):
            raise ValueError("fixed retrieval manifest case_count does not match its IDs")
        if selection_manifest["qa"].get("case_count") != len(fixed_qa):
            raise ValueError("fixed QA manifest case_count does not match its IDs")
        if set(fixed_retrieval) != set(retrieval_ids) or len(fixed_retrieval) != len(
            retrieval_ids
        ):
            raise ValueError("retrieval record IDs/count do not match the fixed manifest")
        if set(fixed_qa) != set(qa_ids) or len(fixed_qa) != len(qa_ids):
            raise ValueError("QA record IDs/count do not match the fixed manifest")
        if selection_manifest["qa"].get("mode") != "qa":
            raise ValueError("fixed QA manifest must declare mode=qa")
        if selection_manifest["qa"].get("external_judge") is not False:
            raise ValueError("fixed QA manifest must explicitly set external_judge=false")

    breakdowns = [
        item["model_call_breakdown"]
        for item in small_e2e["records"]
        if "model_call_breakdown" in item
    ]
    if breakdowns and any(
        int((breakdown.get("judge") or {}).get("model_calls", 0)) != 0
        for breakdown in breakdowns
    ):
        raise ValueError("unjudged QA bootstrap records must have judge model_calls=0")


def _measured_metrics(
    metrics: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    keys = (
        "cases_completed",
        "intent_accuracy",
        "gold_recall_at_5",
        "gold_recall_at_10",
        "gold_recall_at_20",
        "mrr",
        "combined_candidate_recall",
        "final_evidence_recall",
        "critical_final_evidence_recall",
        "expected_status_accuracy",
        "citation_integrity",
        "unhandled_exception_count",
    )
    values = {
        key: metrics[key]
        for key in keys
        if key in metrics and metrics.get(key) is not None
    }
    boundaries = manifest.get("pipeline_boundaries") or {}
    external_judge = (
        boundaries.get("external_judge")
        if boundaries
        else manifest.get("mode") == "qa"
    )
    if external_judge and "answer_point_coverage" in metrics:
        values["answer_point_coverage"] = metrics["answer_point_coverage"]
    values["metric_applicability"] = dict(metrics.get("metric_applicability") or {})
    return values


def package_generalization_baseline(
    project_root: Path,
    *,
    baseline_id: str,
    historical_run_id: str,
    benchmark_retrieval_run_id: str,
    small_e2e_run_id: str,
    novel_retrieval_run_id: str | None = None,
    selection_manifest_path: Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Package existing measured runs without rerunning any model-backed stage."""
    historical = _run_payload(project_root, historical_run_id)
    benchmark = _run_payload(project_root, benchmark_retrieval_run_id)
    small_e2e = _run_payload(project_root, small_e2e_run_id)
    novel = _run_payload(project_root, novel_retrieval_run_id) if novel_retrieval_run_id else None
    if historical["manifest"].get("mode") not in {"qa", "full"}:
        raise ValueError("historical E2E reference must be a QA/full run")
    if novel and novel["manifest"].get("mode") != "retrieval":
        raise ValueError("novel retrieval baseline must use retrieval mode")
    selection_manifest: dict[str, Any] | None = None
    if selection_manifest_path is not None:
        selection_manifest = json.loads(selection_manifest_path.read_text(encoding="utf-8"))
    validate_baseline_consistency(selection_manifest, benchmark, small_e2e)

    output = project_root / "evaluation" / "baselines" / baseline_id
    if output.exists() and not overwrite:
        raise FileExistsError(f"baseline package already exists: {baseline_id}")
    existing_manifest_path = output / "baseline_manifest.json"
    existing_manifest = (
        json.loads(existing_manifest_path.read_text(encoding="utf-8"))
        if overwrite and existing_manifest_path.is_file()
        else {}
    )
    output.mkdir(parents=True, exist_ok=True)
    created_at = existing_manifest.get("created_at") or datetime.now(UTC).isoformat()
    current_manifest = benchmark["manifest"]
    measured_repository = current_manifest.get("repository_identity") or {}
    display_name = (
        selection_manifest.get("display_name")
        if selection_manifest
        else existing_manifest.get("display_name", "Generalization bootstrap baseline")
    )
    implementation_identity = {
        "schema_version": "1.0",
        "baseline_id": baseline_id,
        "display_name": display_name,
        "created_at": created_at,
        "evaluation_mode": "retrieval",
        "measured_execution_provenance": {
            "base_git_commit": measured_repository.get("commit"),
            "working_tree_dirty": measured_repository.get("dirty"),
            "interpretation": "The measurement represents the base Git commit plus the then-current working-tree changes.",
        },
        "prompt_set_version": current_manifest.get("prompt_version"),
        "embedding_model": current_manifest.get("embedding_model_id"),
        "embedding_dimensions": current_manifest.get("embedding_dimensions"),
        "sparse_configuration": (
            (current_manifest.get("index_identity_payload") or {}).get("sparse_model")
        ),
        "index_identity": current_manifest.get("index_identity"),
        "index_identity_payload": current_manifest.get("index_identity_payload"),
        "generation_model": current_manifest.get("generation_model_id"),
        "runtime_verifier_model_role": current_manifest.get("runtime_generation_model_id"),
        "evaluation_judge_model": current_manifest.get("evaluation_judge_model_id"),
        "retrieval_policy_identity": current_manifest.get("retrieval_policy_hash"),
        "query_expansion_identity": current_manifest.get("query_expansion_hash"),
        "dataset_identity": current_manifest.get("gold_dataset_hash"),
        "dataset_path": _portable_path(
            project_root, current_manifest.get("gold_dataset_path")
        ),
    }
    _write_json(output / "implementation_identity.json", implementation_identity)
    if selection_manifest:
        _write_json(output / "selection_manifest.json", selection_manifest)

    historical_manifest = _portable_manifest(project_root, historical["manifest"])
    historical_identity = historical_manifest.get("repository_identity")
    historical_record = {
        "schema_version": "1.0",
        "role": "historical_e2e_baseline",
        "source_run_id": historical_run_id,
        "source_manifest": historical_manifest,
        "measured_metrics": _measured_metrics(
            historical["metrics"], historical["manifest"]
        ),
        "matches_a3_measured_execution_exactly": bool(
            historical_identity
            and historical_identity.get("commit") == measured_repository.get("commit")
            and historical_identity.get("dirty") is False
            and measured_repository.get("dirty") is False
        ),
        "identity_limitation": (
            None
            if historical_identity
            else "The historical manifest predates explicit Git commit recording."
        ),
    }
    _write_json(output / "historical_e2e_metrics.json", historical_record)
    _write_jsonl(output / "benchmark_retrieval_baseline.jsonl", benchmark["records"])
    _write_jsonl(
        output / "benchmark_retrieval_traces.jsonl",
        [trace.model_dump(mode="json") for trace in benchmark["traces"]],
    )
    _write_jsonl(output / "small_e2e_baseline.jsonl", small_e2e["records"])
    _write_jsonl(
        output / "small_e2e_traces.jsonl",
        [trace.model_dump(mode="json") for trace in small_e2e["traces"]],
    )
    if novel:
        _write_jsonl(output / "novel_retrieval_baseline.jsonl", novel["records"])
        _write_jsonl(
            output / "novel_retrieval_traces.jsonl",
            [trace.model_dump(mode="json") for trace in novel["traces"]],
        )
    else:
        _write_jsonl(output / "novel_retrieval_baseline.jsonl", [])
        _write_jsonl(output / "novel_retrieval_traces.jsonl", [])

    package_manifest = {
        "schema_version": "1.0",
        "baseline_id": baseline_id,
        "display_name": implementation_identity["display_name"],
        "scope": (
            selection_manifest.get("scope")
            if selection_manifest
            else existing_manifest.get("scope")
        ),
        "fixed_selection_manifest": (
            _portable_path(project_root, selection_manifest_path)
            if selection_manifest_path
            else None
        ),
        "created_at": created_at,
        "historical_e2e_run_id": historical_run_id,
        "benchmark_retrieval_run_id": benchmark_retrieval_run_id,
        "novel_retrieval_run_id": novel_retrieval_run_id,
        "small_e2e_run_id": small_e2e_run_id,
        "full_120_question_e2e_rerun": False,
        "full_120_question_retrieval_run": False,
        "external_judge_used_for_small_e2e": False,
        "artifact_semantics": {
            "measurement_changed": False,
            "representation_or_provenance_metadata_corrected": overwrite,
        },
        "question_counts": {
            "historical_e2e": len(historical["records"]),
            "benchmark_retrieval": len(benchmark["records"]),
            "novel_retrieval": len(novel["records"]) if novel else 0,
            "small_e2e": len(small_e2e["records"]),
        },
        "selected_question_ids": {
            "benchmark_retrieval": [item["id"] for item in benchmark["records"]],
            "novel_retrieval": [item["id"] for item in novel["records"]] if novel else [],
            "small_e2e": [item["id"] for item in small_e2e["records"]],
        },
        "measured_metrics": {
            "benchmark_retrieval": _measured_metrics(
                benchmark["metrics"], benchmark["manifest"]
            ),
            "novel_retrieval": (
                _measured_metrics(novel["metrics"], novel["manifest"])
                if novel
                else None
            ),
            "small_e2e": _measured_metrics(
                small_e2e["metrics"], small_e2e["manifest"]
            ),
        },
        "run_usage": {
            "benchmark_retrieval": {
                "model_calls": benchmark["status"].get("model_calls"),
                "token_usage": benchmark["status"].get("token_usage"),
            },
            "novel_retrieval": (
                {
                    "model_calls": novel["status"].get("model_calls"),
                    "token_usage": novel["status"].get("token_usage"),
                }
                if novel
                else None
            ),
            "small_e2e": {
                "model_calls": small_e2e["status"].get("model_calls"),
                "token_usage": small_e2e["status"].get("token_usage"),
            },
        },
        "unevaluated_intents": (
            selection_manifest.get("unevaluated_intents", {})
            if selection_manifest
            else {}
        ),
    }
    if existing_manifest.get("superseded_by"):
        package_manifest["superseded_by"] = existing_manifest["superseded_by"]
    _write_json(output / "baseline_manifest.json", package_manifest)
    report = [
        f"# {implementation_identity['display_name']}",
        "",
        "This package separates measured historical E2E evidence, current retrieval behavior, and current small-scale E2E behavior.",
        "It is not a complete generalization, complete benchmark, or all-intent baseline.",
        "The source measurements are unchanged; this package corrects only metric applicability, portable paths, consistency metadata, and provenance wording.",
        "",
        (
            "## A3 measured execution provenance"
            if selection_manifest
            else "## Measured execution provenance"
        ),
        "",
        f"- Base Git commit: `{measured_repository.get('commit')}`.",
        f"- Working tree dirty: `{measured_repository.get('dirty')}`.",
        "- In prototype development this truthfully identifies the measured execution as the base commit plus the then-current working-tree changes; it is not a frozen candidate identity.",
        "- A later commit or newer HEAD does not invalidate this diagnostic baseline and does not require a rerun.",
        "",
        "## Measured artifacts",
        "",
        f"- Historical E2E: `{historical_run_id}` ({len(historical['records'])} questions).",
        f"- Current benchmark retrieval: `{benchmark_retrieval_run_id}` ({len(benchmark['records'])} questions).",
        f"- Current novel retrieval: `{novel_retrieval_run_id or 'not run; no trustworthy novel dataset available'}` ({len(novel['records']) if novel else 0} questions).",
        f"- Current small E2E: `{small_e2e_run_id}` ({len(small_e2e['records'])} questions; external judge disabled).",
        "",
        "## Boundaries",
        "",
        "- No fresh full 120-question E2E evaluation was run for this package.",
        "- No full 120-question retrieval-only evaluation or T3 was run for this package.",
        "- The empty novel artifacts are schemas/placeholders, not measured results.",
        "- Planned roadmap acceptance targets are not baseline measurements.",
        "- External-rubric answer-point, contradiction, and unsupported-claim metrics are N/A for the unjudged QA run.",
        "- `data_flow`, `module_structure`, and `troubleshooting` are unevaluated because v2.6 has no eligible approved English Gold questions for those intents.",
        "",
        "## Fixed comparison sets",
        "",
        f"- Retrieval IDs ({len(benchmark['records'])}): `{', '.join(item['id'] for item in benchmark['records'])}`",
        f"- QA IDs ({len(small_e2e['records'])}): `{', '.join(item['id'] for item in small_e2e['records'])}`",
        "- Future before/after comparisons must reuse these IDs unchanged; a changed selection requires a new baseline manifest identity.",
        "",
        "## Metrics",
        "",
        "```json",
        json.dumps(package_manifest["measured_metrics"], ensure_ascii=False, sort_keys=True, indent=2),
        "```",
    ]
    (output / "baseline_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return output
