"""Package low-cost, reusable Generalization Phase baselines."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from panda_agent.evaluation import GoldQuestion, load_gold_dataset, load_run_records
from panda_agent.evaluation_runner import repository_identity
from panda_agent.retrieval_trace import load_retrieval_traces


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
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    status_path = run_dir / "run_status.json"
    status = (
        json.loads(status_path.read_text(encoding="utf-8"))
        if status_path.is_file()
        else {}
    )
    return {
        "run_id": run_id,
        "run_dir": run_dir,
        "manifest": manifest,
        "metrics": metrics,
        "status": status,
        "records": load_run_records(run_dir),
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
    values = {key: metrics.get(key) for key in keys if key in metrics}
    boundaries = manifest.get("pipeline_boundaries") or {}
    external_judge = (
        boundaries.get("external_judge")
        if boundaries
        else manifest.get("mode") == "qa"
    )
    if external_judge and "answer_point_coverage" in metrics:
        values["answer_point_coverage"] = metrics["answer_point_coverage"]
    return values


def freeze_generalization_baseline(
    project_root: Path,
    *,
    baseline_id: str,
    historical_run_id: str,
    benchmark_retrieval_run_id: str,
    small_e2e_run_id: str,
    novel_retrieval_run_id: str | None = None,
    selection_manifest_path: Path | None = None,
) -> Path:
    """Freeze measured runs without rerunning any model-backed stage."""
    historical = _run_payload(project_root, historical_run_id)
    benchmark = _run_payload(project_root, benchmark_retrieval_run_id)
    small_e2e = _run_payload(project_root, small_e2e_run_id)
    novel = _run_payload(project_root, novel_retrieval_run_id) if novel_retrieval_run_id else None
    if historical["manifest"].get("mode") not in {"qa", "full"}:
        raise ValueError("historical E2E reference must be a QA/full run")
    if benchmark["manifest"].get("mode") != "retrieval":
        raise ValueError("benchmark retrieval baseline must use retrieval mode")
    if small_e2e["manifest"].get("mode") != "qa":
        raise ValueError("small E2E baseline must use qa mode without the external judge")
    if novel and novel["manifest"].get("mode") != "retrieval":
        raise ValueError("novel retrieval baseline must use retrieval mode")
    selection_manifest: dict[str, Any] | None = None
    if selection_manifest_path is not None:
        selection_manifest = json.loads(selection_manifest_path.read_text(encoding="utf-8"))
        expected_retrieval = set(selection_manifest["retrieval"]["case_ids"])
        expected_qa = set(selection_manifest["qa"]["case_ids"])
        actual_retrieval = {item["id"] for item in benchmark["records"]}
        actual_qa = {item["id"] for item in small_e2e["records"]}
        if actual_retrieval != expected_retrieval:
            raise ValueError("retrieval run IDs do not match the fixed selection manifest")
        if actual_qa != expected_qa:
            raise ValueError("QA run IDs do not match the fixed selection manifest")

    output = project_root / "evaluation" / "baselines" / baseline_id
    if output.exists():
        raise FileExistsError(f"baseline package already exists: {baseline_id}")
    output.mkdir(parents=True)
    created_at = datetime.now(UTC).isoformat()
    current_repository = repository_identity(project_root)
    current_manifest = benchmark["manifest"]
    implementation_identity = {
        "schema_version": "1.0",
        "baseline_id": baseline_id,
        "display_name": (
            selection_manifest.get("display_name")
            if selection_manifest
            else "Generalization bootstrap baseline"
        ),
        "created_at": created_at,
        "evaluation_mode": "retrieval",
        "repository_identity": current_manifest.get("repository_identity", current_repository),
        "current_repository_identity_at_freeze": current_repository,
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
        "dataset_path": current_manifest.get("gold_dataset_path"),
    }
    _write_json(output / "implementation_identity.json", implementation_identity)
    if selection_manifest:
        _write_json(output / "selection_manifest.json", selection_manifest)

    historical_identity = historical["manifest"].get("repository_identity")
    historical_record = {
        "schema_version": "1.0",
        "role": "historical_e2e_baseline",
        "source_run_id": historical_run_id,
        "source_manifest": historical["manifest"],
        "measured_metrics": _measured_metrics(
            historical["metrics"], historical["manifest"]
        ),
        "matches_current_head_exactly": bool(
            historical_identity
            and historical_identity.get("commit") == current_repository["commit"]
            and historical_identity.get("dirty") is False
            and current_repository.get("dirty") is False
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
            selection_manifest.get("scope") if selection_manifest else None
        ),
        "fixed_selection_manifest": (
            str(selection_manifest_path.resolve()) if selection_manifest_path else None
        ),
        "created_at": created_at,
        "historical_e2e_run_id": historical_run_id,
        "benchmark_retrieval_run_id": benchmark_retrieval_run_id,
        "novel_retrieval_run_id": novel_retrieval_run_id,
        "small_e2e_run_id": small_e2e_run_id,
        "full_120_question_e2e_rerun": False,
        "full_120_question_retrieval_run": False,
        "external_judge_used_for_small_e2e": False,
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
    _write_json(output / "baseline_manifest.json", package_manifest)
    report = [
        f"# {implementation_identity['display_name']}",
        "",
        "This package separates measured historical E2E evidence, current retrieval behavior, and current small-scale E2E behavior.",
        "It is not a complete generalization, complete benchmark, or all-intent baseline.",
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
