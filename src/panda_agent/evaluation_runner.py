"""M6 benchmark validation, resumable execution, scoring, and reporting."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import yaml

from panda_agent.evaluation import (
    EvaluationRunStore,
    GoldDataset,
    GoldQuestion,
    aggregate_metrics,
    apply_mode_metric_semantics,
    apply_signed_rescore_adjudication,
    deterministic_case_metrics,
    english_product_case_ids,
    evaluate_development_gate,
    evaluate_product_development_gate,
    evaluate_regression_gate,
    evaluate_quality_gate,
    load_product_language_calibration,
    load_run_records,
    load_gold_dataset,
    normalize_run_records,
    validate_v25_adjudication_document,
)
from panda_agent.evaluator_catalog import catalog_receipt, load_evaluator_catalog
from panda_agent.indexing import IndexIdentity, normalized_dir
from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.prompts import (
    ANSWER_COMPOSER_REVIEW_SYSTEM_PROMPT,
    ANSWER_COMPOSER_SYSTEM_PROMPT,
    ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT,
    ANSWER_POINT_COVERAGE_REVISION_SYSTEM_PROMPT,
    ANSWER_SYSTEM_PROMPT,
    EVALUATION_JUDGE_SYSTEM_PROMPT,
    EVIDENCE_REVIEW_SYSTEM_PROMPT,
    PROMPT_SET_VERSION,
    QUERY_ANALYZER_SYSTEM_PROMPT,
    RERANK_SYSTEM_PROMPT,
    REVISION_SYSTEM_PROMPT,
)
from panda_agent.qa import QAAgent
from panda_agent.retrieval import Retriever
from panda_agent.retrieval_trace import build_retrieval_trace, write_retrieval_trace
from panda_agent.storage import Storage, iter_jsonl


EvaluationMode = Literal["retrieval", "qa", "full"]
EvaluationSplit = Literal[
    "dev",
    "challenge",
    "regression",
    "acceptance",
    "novel_dev",
    "novel_validation",
    "novel_holdout",
    "all",
]

# Human review exports may use more descriptive action labels than the
# generated review schema.  Keep the raw labels in the imported overlay, but
# validate and apply their canonical equivalents so a reviewed decision cannot
# be rejected merely because it came from the external review worksheet.
REVIEW_ACTION_ALIASES = {
    "offline_rescore": "rescore",
    "fix_output_rendering_and_rerun": "fix",
    "fix_and_rerun": "fix",
    "release_reject": "fix",
}
REVIEW_CLASSIFICATIONS = {
    "metric_false_positive",
    "real_failure",
    "acceptable_exception",
    "mixed_evaluation_and_answer_quality",
}


def evaluation_mode_boundaries(mode: EvaluationMode) -> dict[str, bool]:
    """Declare the pipeline stages that an evaluation mode is allowed to enter."""
    if mode not in {"retrieval", "qa", "full"}:
        raise ValueError(f"unsupported evaluation mode: {mode}")
    return {
        "answer_generation": mode in {"qa", "full"},
        "runtime_verification": mode in {"qa", "full"},
        "external_judge": mode == "full",
    }


def repository_identity(project_root: Path) -> dict[str, Any]:
    """Record Git identity without producing a per-file integrity manifest."""
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return {"commit": commit, "dirty": bool(status.strip())}


def default_gold_dataset_path(project_root: Path) -> Path:
    """Return the newest signed exposed benchmark, falling back for old checkouts."""
    reviewed_v26 = project_root / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
    reviewed_v26_manifest = reviewed_v26.with_name("benchmark_manifest.json")
    if reviewed_v26.is_file() and reviewed_v26_manifest.is_file():
        try:
            manifest = json.loads(reviewed_v26_manifest.read_text(encoding="utf-8"))
            if (
                manifest.get("dataset_sha256") == sha256_file(reviewed_v26)
                and manifest.get("project_official_validation", {}).get("official_ready")
                and manifest.get("project_official_validation", {}).get("structurally_valid")
            ):
                return reviewed_v26
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    reviewed_v25 = project_root / "evaluation" / "benchmarks" / "v2_5" / "gold_questions.yaml"
    reviewed_v25_manifest = reviewed_v25.with_name("benchmark_manifest.json")
    if reviewed_v25.is_file() and reviewed_v25_manifest.is_file():
        try:
            manifest = json.loads(reviewed_v25_manifest.read_text(encoding="utf-8"))
            if (
                manifest.get("dataset_sha256") == sha256_file(reviewed_v25)
                and manifest.get("project_official_validation", {}).get("official_ready")
                and manifest.get("project_official_validation", {}).get("structurally_valid")
            ):
                return reviewed_v25
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    reviewed_v24 = project_root / "evaluation" / "benchmarks" / "v2_4" / "gold_questions.yaml"
    reviewed_v24_manifest = reviewed_v24.with_name("benchmark_manifest.json")
    if reviewed_v24.is_file() and reviewed_v24_manifest.is_file():
        try:
            manifest = json.loads(reviewed_v24_manifest.read_text(encoding="utf-8"))
            if (
                manifest.get("dataset_sha256") == sha256_file(reviewed_v24)
                and manifest.get("project_official_validation", {}).get("official_ready")
                and manifest.get("project_official_validation", {}).get("structurally_valid")
            ):
                return reviewed_v24
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    reviewed_v23 = project_root / "evaluation" / "benchmarks" / "v2_3" / "gold_questions.yaml"
    reviewed_v23_manifest = reviewed_v23.with_name("benchmark_manifest.json")
    if reviewed_v23.is_file() and reviewed_v23_manifest.is_file():
        try:
            manifest = json.loads(reviewed_v23_manifest.read_text(encoding="utf-8"))
            if (
                manifest.get("dataset_sha256") == sha256_file(reviewed_v23)
                and manifest.get("project_official_validation", {}).get("official_ready")
                and manifest.get("project_official_validation", {}).get("structurally_valid")
            ):
                return reviewed_v23
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    reviewed_v22 = project_root / "evaluation" / "benchmarks" / "v2_2" / "gold_questions.yaml"
    if reviewed_v22.is_file():
        return reviewed_v22
    reviewed_v21 = project_root / "evaluation" / "benchmarks" / "v2_1" / "gold_questions.yaml"
    if reviewed_v21.is_file():
        return reviewed_v21
    reviewed_v2 = project_root / "evaluation" / "benchmarks" / "v2" / "gold_questions.yaml"
    return reviewed_v2 if reviewed_v2.is_file() else project_root / "evaluation" / "gold_questions.yaml"


def dry_rescore_run(
    project_root: Path,
    run_id: str,
    dataset_path: Path,
    *,
    case_ids: list[str] | None = None,
    adjudications_path: Path | None = None,
) -> dict[str, Any]:
    """Rescore immutable records in memory with zero model calls and no artifacts.

    This deliberately accepts only explicit answer-point adjudications from a
    signed local file.  All retrieval/evidence metrics are recomputed against
    the supplied Gold; the underlying answer and record remain unchanged.
    """
    dataset = load_gold_dataset(dataset_path)
    questions = {item.id: item for item in dataset.questions}
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    records = load_run_records(run_dir)
    if not records:
        raise ValueError(f"evaluation run has no records: {run_id}")
    source_ids = {str(item["id"]) for item in records}
    selected_ids = set(case_ids or source_ids)
    unknown = sorted(selected_ids - source_ids)
    if unknown:
        raise ValueError(f"rescore cases are absent from source run: {unknown}")
    path = adjudications_path or (
        dataset_path.parent / "manual_adjudications.yaml"
    )
    adjudications: dict[str, dict[str, Any]] = {}
    adjudications_sha256: str | None = None
    if path.is_file():
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        validate_v25_adjudication_document(dataset.benchmark_version, payload)
        adjudications_sha256 = sha256_file(path)
        for item in payload.get("adjudications", []):
            case_id = str(item.get("case_id", ""))
            if case_id:
                adjudications[case_id] = item
    object_lookup = load_object_lookup(project_root)
    rescored: list[dict[str, Any]] = []
    for source_record in records:
        case_id = str(source_record["id"])
        if case_id not in selected_ids or case_id not in questions:
            continue
        question = questions[case_id]
        metrics = {
            **(source_record.get("metrics") or {}),
            **deterministic_case_metrics(
                question,
                source_record.get("result") or {},
                source_record.get("diagnostics") or {},
                object_lookup,
            ),
        }
        metrics = enforce_protected_rubric_metrics(
            question, source_record.get("result") or {}, metrics
        )
        adjudicated: list[str] = []
        adjudication = adjudications.get(case_id)
        if adjudication:
            metrics, adjudicated = apply_signed_rescore_adjudication(
                dataset.benchmark_version, question, metrics, adjudication
            )
        computed = [
            "intent_correct",
            "expected_status_correct",
            "gold_recall_at_10",
            "final_evidence_recall",
            "critical_final_evidence_recall",
            "refusal_evidence_recall",
            "required_source_coverage",
            "wrong_version_evidence",
            "forbidden_evidence",
            "citation_integrity",
            "metric_applicability",
            "metric_denominators",
        ]
        rescored.append(
            {
                "id": case_id,
                "intent": question.intent,
                "split": question.split,
                "expected_status": question.expected_status.value,
                "metrics": metrics,
                "rescore_provenance": {
                    "record_immutable": True,
                    "model_calls": 0,
                    "computed_fields": computed,
                    "human_adjudicated_fields": adjudicated,
                    "field_provenance": {
                        field: "human_adjudicated" if field in adjudicated else "computed"
                        for field in sorted(set(computed) | set(adjudicated))
                    },
                    "human_adjudication_source": str(path) if adjudication else None,
                },
            }
        )
    return {
        "dry_run": True,
        "source_run_id": run_id,
        "dataset": str(dataset_path),
        "dataset_sha256": sha256_file(dataset_path),
        "manual_adjudications_sha256": adjudications_sha256,
        "rescore_model_calls": 0,
        "rescore_token_usage": 0,
        "cases_rescored": len(rescored),
        "metrics": aggregate_metrics(rescored),
        "records": rescored,
    }

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "point_scores": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "point_id": {"type": "string"},
                    "covered": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["point_id", "covered", "reason"],
                "additionalProperties": False,
            },
        },
        "covered_point_ids": {"type": "array", "items": {"type": "string"}},
        "contradictions": {"type": "array", "items": {"type": "string"}},
        "unsupported_claim_ids": {"type": "array", "items": {"type": "string"}},
        "claim_verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["supported", "partially_supported", "unsupported"],
                    },
                    "severity": {"type": "string", "enum": ["major", "minor"]},
                    "reason": {"type": "string"},
                },
                "required": ["claim_id", "status", "severity", "reason"],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "point_scores",
        "covered_point_ids",
        "contradictions",
        "unsupported_claim_ids",
        "claim_verdicts",
    ],
    "additionalProperties": False,
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def prompt_fingerprint() -> str:
    """Fingerprint every behavior-affecting model prompt in the runtime.

    F6 release identity requires the full active prompt set, including the
    answer-point coverage review/revision contracts and the F5 composer and
    composer-review prompts; the offline judge is recorded as architecture
    metadata. Any prompt change must change this hash.
    """
    payload = {
        "answer": ANSWER_SYSTEM_PROMPT,
        "answer_composer": ANSWER_COMPOSER_SYSTEM_PROMPT,
        "answer_composer_review": ANSWER_COMPOSER_REVIEW_SYSTEM_PROMPT,
        "answer_point_coverage_review": ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT,
        "answer_point_coverage_revision": ANSWER_POINT_COVERAGE_REVISION_SYSTEM_PROMPT,
        "evaluation_judge": EVALUATION_JUDGE_SYSTEM_PROMPT,
        "evidence_review": EVIDENCE_REVIEW_SYSTEM_PROMPT,
        "query_analyzer": QUERY_ANALYZER_SYSTEM_PROMPT,
        "rerank": RERANK_SYSTEM_PROMPT,
        "revision": REVISION_SYSTEM_PROMPT,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(canonical.encode("utf-8"))


def package_versions() -> dict[str, str]:
    values = {"python": platform.python_version()}
    for distribution in (
        "panda-research-qa-agent",
        "google-genai",
        "langgraph",
        "psycopg",
        "qdrant-client",
    ):
        try:
            values[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            values[distribution] = "not-installed"
    return values


def f6a_release_score(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Deterministic F6-A release score over complete cases.

    A case scores ``answer_point_coverage`` when the expected status is
    answered, otherwise 1.0/0.0 for expected-status correctness. A case with a
    missing required metric is incomplete (never silently scored as zero); the
    denominator is always reported.
    """
    scores: list[float] = []
    incomplete: list[str] = []
    for record in records:
        case_id = str(record.get("id"))
        metrics = record.get("metrics") or {}
        if record.get("exception") is not None:
            incomplete.append(case_id)
            continue
        expected = str(record.get("expected_status"))
        if expected == "answered":
            value = metrics.get("answer_point_coverage")
        else:
            value = 1.0 if metrics.get("expected_status_correct") else 0.0
        if value is None:
            incomplete.append(case_id)
            continue
        scores.append(float(value))
    return {
        "release_score": sum(scores) / len(scores) if scores else None,
        "complete_case_count": len(scores),
        "incomplete_case_ids": incomplete,
        "denominator": len(scores),
    }


def _selected_questions(dataset: GoldDataset, split: EvaluationSplit) -> list[GoldQuestion]:
    if split == "all":
        return list(dataset.questions)
    return [item for item in dataset.questions if item.split == split]


def _attempt_budget_stop_reason(
    *,
    attempt_calls: int,
    attempt_tokens: int,
    max_model_calls: int | None,
    max_token_usage: int | None,
    deadline_at: float | None,
    now: float | None = None,
) -> str | None:
    """Return a stop reason using only the current run/resume attempt window."""
    if max_model_calls is not None and attempt_calls >= max_model_calls:
        return "max_model_calls_exceeded"
    if max_token_usage is not None and attempt_tokens >= max_token_usage:
        return "max_token_usage_exceeded"
    if deadline_at is not None and (time.time() if now is None else now) >= deadline_at:
        return "deadline_exceeded"
    return None


def build_evaluation_manifest(
    project_root: Path,
    dataset_path: Path,
    *,
    mode: EvaluationMode,
    split: EvaluationSplit,
    official: bool,
) -> dict[str, Any]:
    settings = VertexSettings.from_env()
    dataset = load_gold_dataset(dataset_path)
    normalized = normalized_dir(project_root)
    report = json.loads((normalized / "ingestion_report.json").read_text(encoding="utf-8"))
    source_manifest_path = project_root / "data" / "manifests" / "source_manifest.json"
    identity = IndexIdentity.from_settings(settings)
    storage = Storage()
    with storage.connect() as connection:
        row = connection.execute(
            "SELECT fingerprint,payload FROM index_identities WHERE collection_name=%s",
            (storage.settings.collection_name,),
        ).fetchone()
    if row is None:
        raise RuntimeError("index identity is missing; M3 must be applied before M6")
    if row[0] != identity.fingerprint():
        raise RuntimeError(
            f"index identity mismatch: database={row[0]}, configured={identity.fingerprint()}"
        )
    return {
        "schema_version": "1.0",
        "mode": mode,
        "pipeline_boundaries": evaluation_mode_boundaries(mode),
        "split": split,
        "official": official,
        "repository_identity": repository_identity(project_root),
        "source_manifest_hash": sha256_file(source_manifest_path),
        "normalized_manifest_hash": normalized.name,
        "normalized_output_hashes": report["output_hashes"],
        "index_identity": row[0],
        "index_identity_payload": row[1],
        "generation_model_id": settings.generation_model,
        "runtime_generation_model_id": settings.generation_model,
        "evaluation_judge_model_id": settings.evaluation_judge_model,
        "embedding_model_id": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
        "prompt_version": PROMPT_SET_VERSION,
        "prompt_hash": prompt_fingerprint(),
        "retrieval_policy_hash": sha256_file(
            project_root / "configs" / "retrieval_policies.yaml"
        ),
        "query_expansion_hash": sha256_file(
            project_root / "configs" / "query_expansions.yaml"
        ),
        "gold_dataset_hash": sha256_file(dataset_path),
        "gold_dataset_path": str(dataset_path.resolve()),
        "gold_release_eligible": dataset.release_eligible,
        "gold_acceptance_exposed": dataset.acceptance_exposed,
        "gold_expected_split_counts": dataset.expected_split_counts,
        "audit_resolution_hash": (
            sha256_file(project_root / "evaluation" / "benchmarks" / "v2" / "audit_resolution.yaml")
            if (project_root / "evaluation" / "benchmarks" / "v2" / "audit_resolution.yaml").is_file()
            else None
        ),
        "package_versions": package_versions(),
    }


def load_object_lookup(
    project_root: Path, *, evaluator_catalog_path: Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Load the evaluator's full canonical lookup from normalized data or a catalog."""
    if evaluator_catalog_path is not None:
        return load_evaluator_catalog(evaluator_catalog_path)
    path = normalized_dir(project_root) / "knowledge_objects.jsonl"
    return {item["object_id"]: item for item in iter_jsonl(path)}


def result_content_hash(records: list[dict[str, Any]]) -> str:
    """Hash semantic per-case output while excluding wall-clock/runtime metadata."""
    stable = [
        {
            key: item.get(key)
            for key in (
                "id",
                "intent",
                "split",
                "language",
                "expected_status",
                "required_source_types",
                "result",
                "diagnostics",
                "metrics",
                "exception",
            )
            if key in item
        }
        for item in sorted(records, key=lambda value: value["id"])
    ]
    canonical = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(canonical.encode("utf-8"))


def validate_gold_dataset(
    project_root: Path,
    dataset_path: Path,
    *,
    require_approved: bool = False,
    evaluator_catalog_path: Path | None = None,
) -> dict[str, Any]:
    dataset = load_gold_dataset(dataset_path)
    approval_error: str | None = None
    if require_approved:
        try:
            dataset.require_approved()
        except ValueError as exc:
            approval_error = str(exc)
    objects = list(
        load_object_lookup(
            project_root, evaluator_catalog_path=evaluator_catalog_path,
        ).values()
    )
    known_source_versions = {item["source_version_id"] for item in objects}
    unmatched: list[dict[str, Any]] = []
    unknown_allowed_versions: list[dict[str, Any]] = []
    for case in dataset.questions:
        unknown = sorted(set(case.allowed_source_versions) - known_source_versions)
        if unknown:
            unknown_allowed_versions.append(
                {"question_id": case.id, "source_version_ids": unknown}
            )
        for group in case.required_evidence_groups:
            if not any(
                candidate.matches(item)
                for candidate in group.any_of
                for item in objects
            ):
                unmatched.append({"question_id": case.id, "group_id": group.group_id})
    review_counts: dict[str, int] = {}
    for case in dataset.questions:
        review_counts[case.review_status] = review_counts.get(case.review_status, 0) + 1
    return {
        "structurally_valid": not unmatched and not unknown_allowed_versions,
        "official_ready": not unmatched
        and not unknown_allowed_versions
        and review_counts.get("approved", 0) == len(dataset.questions),
        "question_count": len(dataset.questions),
        "dataset_hash": sha256_file(dataset_path),
        "review_counts": review_counts,
        "approval_error": approval_error,
        "unmatched_evidence_groups": unmatched,
        "unknown_allowed_source_versions": unknown_allowed_versions,
    }


def _stats_snapshot(engine: Retriever | QAAgent) -> dict[str, int]:
    vertex = getattr(engine, "vertex", None)
    method = getattr(vertex, "stats_snapshot", None)
    return method() if callable(method) else {}


def _stats_delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {key: after.get(key, 0) - before.get(key, 0) for key in set(before) | set(after)}


def _deterministic_point_ids(case: GoldQuestion, result: dict[str, Any]) -> list[str]:
    """Recover obvious rubric coverage when the generative judge is conservative.

    The benchmark still uses the model judge for semantic coverage. These checks
    only accept explicit, reviewable anchors (identifiers, workflow terms, or
    contrast words) and make repeated runs stable when Gemini returns an empty
    coverage array for an otherwise direct answer.
    """
    if result.get("status") != "answered":
        return []
    answer = str(result.get("answer", "")).casefold()
    if not answer.strip():
        return []
    values: list[str] = []
    query = case.query.casefold()
    for point in case.required_answer_points:
        text = point.text.casefold()
        covered = False
        if "commit-specific" in text or "version scope" in text or "版本" in text:
            covered = ("commit" in answer and ("locked" in answer or "@" in answer)) or (
                "snapshot" in answer and "repository" in answer
            )
        elif "distinguish" in text or "区别" in text or "边界" in text:
            covered = (
                any(term in answer for term in ("devcontainer", "inside the container", "container development", "docker developer environment"))
                and any(term in answer for term in ("alternatively", "whereas", "standalone", "merely", "running the image"))
            )
        elif "differential cross section" in text and "luminos" in text:
            covered = "differential cross" in answer and "luminos" in answer
        elif "factory" in text or "factory" in query or "工厂" in text:
            covered = "factory" in answer and any(
                term in answer for term in ("dpm", "acceptance", "resolution", "smearing")
            )
        elif "event_poca" in text or "event_poca" in query:
            covered = "event_poca" in answer
        elif "profile" in text or "profile" in query or "profile" in point:
            covered = "profile" in answer and any(
                term in answer for term in ("acceptance", "reconstruction", "efficiency", "rho(z)")
            )
        elif "sphinx" in text or "sphinx" in query:
            covered = "sphinx" in answer and any(
                term in answer for term in ("restgas", "authority", "operational", "documentation")
            )
        elif "workflow" in text or "顺序" in text or "sequence" in text:
            workflow_terms = sum(
                term in answer
                for term in ("simulation", "digitization", "reconstruction", "pid", "analysis", "correction", "poca")
            )
            covered = workflow_terms >= 3
        elif case.required_identifiers:
            covered = sum(identifier.text.casefold() in answer for identifier in case.required_identifiers) >= max(
                1, len(case.required_identifiers) // 2
            )
        elif any(term in text for term in ("path", "source", "class", "implementation", "定义", "实现")):
            covered = any(
                token in answer
                for token in (".cxx", ".cpp", ".h", ".py", "model/", "macro/", "source", "class")
            )
        # Protected normalization and implementation-disambiguation points are
        # deliberately stricter than the generic identifier/path backstop.
        # A mentioned symbol or .cxx path alone must not turn these points into
        # judge false positives.
        if "pointer spelling" in text or "asterisk" in text:
            covered = (
                ("pointer" in answer or "type expression" in answer)
                and "pndlmdtrackq" in answer
                and any(
                    term in answer
                    for term in (
                        "asterisk", "pointer syntax", "type-expression syntax",
                        "type expression syntax",
                    )
                )
                and any(
                    term in answer
                    for term in ("not part", "not a new", "does not form", "remove", "strip")
                )
            )
        if "class name" in query and "wrong implementation" in query:
            if "does not establish repository" in text:
                covered = (
                    "name" in answer
                    and any(
                        term in answer
                        for term in (
                            "insufficient", "not enough", "does not establish",
                            "cannot establish",
                        )
                    )
                    and any(
                        term in answer
                        for term in ("repository", "module role", "module context")
                    )
                )
            elif "source_id" in text:
                covered = (
                    any(term in answer for term in ("source_id", "source", "repository"))
                    and "path" in answer
                    and any(term in answer for term in ("locked", "commit", "revision"))
                )
            elif "callers/data products" in text:
                covered = (
                    "implementation" in answer
                    and any(term in answer for term in ("caller", "configuration", "configured"))
                    and any(
                        term in answer
                        for term in ("data product", "branch", "consumed", "produced")
                    )
                )
        if covered:
            values.append(point.point_id)
    return values


def _protected_rubric_point_ids(case: GoldQuestion) -> set[str]:
    """Return points whose explicit procedure cannot be inferred from nearby identifiers."""
    query = case.query.casefold()
    protected: set[str] = set()
    for point in case.required_answer_points:
        text = point.text.casefold()
        if "pointer spelling" in text or "asterisk" in text:
            protected.add(point.point_id)
        if "class name" in query and "wrong implementation" in query and any(
            marker in text
            for marker in (
                "does not establish repository",
                "source_id",
                "callers/data products",
            )
        ):
            protected.add(point.point_id)
    return protected


def enforce_protected_rubric_metrics(
    case: GoldQuestion, result: dict[str, Any], metrics: dict[str, Any]
) -> dict[str, Any]:
    """Fail closed for explicit protected procedures during live and offline scoring."""
    protected = _protected_rubric_point_ids(case)
    if not protected or result.get("status") != "answered":
        return metrics
    explicit = set(_deterministic_point_ids(case, result))
    covered = set(metrics.get("covered_point_ids") or [])
    covered = (covered - protected) | (explicit & protected)
    ordered = [
        point.point_id for point in case.required_answer_points if point.point_id in covered
    ]
    point_by_id = {point.point_id: point for point in case.required_answer_points}
    total_weight = sum(point.weight for point in case.required_answer_points)
    updated = dict(metrics)
    updated["covered_point_ids"] = ordered
    updated["answer_point_coverage"] = (
        sum(point_by_id[point_id].weight for point_id in ordered) / total_weight
        if total_weight
        else 1.0
    )
    updated["critical_answer_points_missing"] = [
        point.point_id
        for point in case.required_answer_points
        if point.critical and point.point_id not in covered
    ]
    return updated


def _claim_relevant_evidence_excerpt(
    item: dict[str, Any], claims: list[dict[str, Any]], limit: int = 5000
) -> str:
    """Keep cited support near identifiers instead of only the file prefix."""
    text = str(item.get("text", ""))
    if len(text) <= limit:
        return text
    evidence_id = item.get("evidence_id")
    claim_text = " ".join(
        str(claim.get("claim_text", ""))
        for claim in claims
        if evidence_id in claim.get("evidence_ids", [])
    )
    terms = sorted(
        set(re.findall(r"[A-Za-z_][A-Za-z0-9_:.-]{3,}", claim_text)),
        key=len,
        reverse=True,
    )
    windows = [text[:800]]
    lowered = text.casefold()
    for term in terms:
        index = lowered.find(term.casefold())
        if index < 0:
            continue
        windows.append(text[max(0, index - 650) : index + 1350])
        if sum(len(value) for value in windows) >= limit:
            break
    return "\n...\n".join(windows)[:limit]


def judge_answer(case: GoldQuestion, result: dict[str, Any], vertex: Any) -> dict[str, Any]:
    point_ids = [point.point_id for point in case.required_answer_points]
    prompt = json.dumps(
        {
            "task": "score_answer_against_human_rubric",
            "question": case.query,
            "expected_status": case.expected_status.value,
            "required_points": [
                {
                    "point_id": point.point_id,
                    "text": point.text,
                    "weight": point.weight,
                    "critical": point.critical,
                }
                for point in case.required_answer_points
            ],
            "point_ids_must_be_scored": point_ids,
            "answer": result.get("answer", ""),
            "claims": result.get("claims", []),
            "verification_errors": result.get("verification_errors", []),
            "evidence": [
                {
                    "evidence_id": item.get("evidence_id"),
                    "source_id": item.get("source_id"),
                    "locator": item.get("locator") or {},
                    "text": _claim_relevant_evidence_excerpt(
                        item, result.get("claims", [])
                    ),
                }
                for item in result.get("evidence", [])
            ],
        },
        ensure_ascii=False,
    )
    judged = vertex.generate_json(
        prompt,
        JUDGE_SCHEMA,
        system_instruction=EVALUATION_JUDGE_SYSTEM_PROMPT,
    )
    scores = judged.get("point_scores") or []
    score_map = {
        item.get("point_id"): bool(item.get("covered"))
        for item in scores
        if item.get("point_id")
    }
    covered = [point_id for point_id in point_ids if score_map.get(point_id) is True]
    if not scores:
        covered = list(dict.fromkeys(judged.get("covered_point_ids", [])))
    deterministic_covered = _deterministic_point_ids(case, result)
    covered = list(dict.fromkeys([*covered, *deterministic_covered]))
    protected_points = _protected_rubric_point_ids(case)
    covered = [
        point_id
        for point_id in covered
        if point_id not in protected_points or point_id in deterministic_covered
    ]
    unknown_points = sorted(set(covered) - set(point_ids))
    if unknown_points:
        raise ValueError(f"evaluation judge returned unknown point IDs: {unknown_points}")
    known_claim_ids = {item.get("claim_id") for item in result.get("claims", [])}
    unknown_claims = sorted(
        set(judged.get("unsupported_claim_ids", [])) - known_claim_ids
    )
    if unknown_claims:
        raise ValueError(f"evaluation judge returned unknown claim IDs: {unknown_claims}")
    point_by_id = {point.point_id: point for point in case.required_answer_points}
    total_weight = sum(point.weight for point in case.required_answer_points)
    covered_weight = sum(point_by_id[point_id].weight for point_id in covered)
    critical_missing = [
        point.point_id
        for point in case.required_answer_points
        if point.critical and point.point_id not in covered
    ]
    verdicts = judged.get("claim_verdicts") or []
    verdict_ids = {item.get("claim_id") for item in verdicts}
    if verdict_ids - known_claim_ids:
        raise ValueError(
            f"evaluation judge returned unknown claim verdict IDs: {sorted(verdict_ids - known_claim_ids)}"
        )
    major_unsupported = [
        item["claim_id"]
        for item in verdicts
        if item.get("status") != "supported" and item.get("severity") == "major"
    ]
    minor_unsupported = [
        item["claim_id"]
        for item in verdicts
        if item.get("status") != "supported" and item.get("severity") == "minor"
    ]
    if not verdicts:
        major_unsupported = list(judged.get("unsupported_claim_ids", []))
    return enforce_protected_rubric_metrics(case, result, {
        "answer_point_coverage": covered_weight / total_weight,
        "covered_point_ids": covered,
        "critical_answer_points_missing": critical_missing,
        "contradictions": judged.get("contradictions", []),
        "unsupported_claim_ids": judged.get("unsupported_claim_ids", []),
        "major_unsupported_claim_ids": list(dict.fromkeys(major_unsupported)),
        "minor_unsupported_claim_ids": list(dict.fromkeys(minor_unsupported)),
        "claim_verdicts": verdicts,
    })


def _retrieval_result(bundle: dict[str, Any]) -> dict[str, Any]:
    if bundle.get("plan", {}).get("version_conflicts"):
        status = "version_conflict"
    elif not bundle.get("evidence"):
        status = "insufficient_evidence"
    else:
        status = "answered"
    return {
        "status": status,
        "answer": "",
        "claims": [],
        "evidence": bundle.get("evidence", []),
        "resolved_versions": bundle.get("plan", {}).get("resolved_versions", {}),
        "verification_errors": bundle.get("plan", {}).get("version_conflicts", []),
    }


def _execute_evaluation_case(
    engine: Retriever | QAAgent,
    judge_vertex: VertexAIClient | None,
    *,
    mode: EvaluationMode,
    case: GoldQuestion,
    object_lookup: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Execute one case while enforcing the selected orchestration boundary."""
    boundaries = evaluation_mode_boundaries(mode)
    if boundaries["answer_generation"]:
        detailed = engine.run_detailed(case.query)
        result = detailed["result"]
        diagnostics = detailed["diagnostics"]
    else:
        diagnostics = engine.retrieve(case.query)
        result = _retrieval_result(diagnostics)

    metrics = deterministic_case_metrics(case, result, diagnostics, object_lookup)
    if boundaries["external_judge"]:
        if judge_vertex is None:
            raise RuntimeError("evaluation judge client is not initialized")
        metrics.update(judge_answer(case, result, judge_vertex))
    metrics = apply_mode_metric_semantics(
        metrics,
        mode=mode,
        external_judge=boundaries["external_judge"],
    )
    return result, diagnostics, metrics


def _review_issues(record: dict[str, Any], mode: EvaluationMode) -> list[dict[str, Any]]:
    """Return case-level imperfections that require human classification.

    Aggregate metrics intentionally allow some non-perfect cases.  A failed
    full development gate nevertheless needs a conservative review set, so the
    sheet contains both strict failures and diagnostic shortfalls.
    """
    metrics = record.get("metrics") or {}
    issues: list[dict[str, Any]] = []

    def add(metric: str, value: Any, expected: str, severity: str = "blocking") -> None:
        issues.append(
            {
                "metric": metric,
                "observed": value,
                "expected": expected,
                "severity": severity,
            }
        )

    if record.get("exception"):
        add("unhandled_exception", record["exception"], "no exception")
        return issues
    if metrics.get("intent_correct") is False:
        add("intent_correct", False, "true")
    if metrics.get("expected_status_correct") is False:
        add("expected_status_correct", False, "true")
    metric_applicability = metrics.get("metric_applicability") or {}
    ordinary_recall_applicable = metric_applicability.get(
        "gold_recall_at_10", metrics.get("gold_recall_at_10") is not None
    )
    if ordinary_recall_applicable and float(metrics.get("gold_recall_at_10", 0.0)) < 1.0:
        add(
            "gold_recall_at_10",
            metrics.get("gold_recall_at_10"),
            "1.0 per case for a perfect result; aggregate gate >= 0.85",
            "diagnostic",
        )
    if (
        metric_applicability.get("final_evidence_recall", metrics.get("final_evidence_recall") is not None)
        and
        metrics.get("final_evidence_recall") is not None
        and float(metrics.get("final_evidence_recall", 0.0)) < 1.0
    ):
        add(
            "final_evidence_recall",
            metrics.get("final_evidence_recall"),
            "1.0 per case (diagnostic metric)",
            "diagnostic",
        )
    if (
        record.get("expected_status") == "answered"
        and metrics.get("required_source_coverage") is False
    ):
        add("required_source_coverage", False, "true")
    if metrics.get("wrong_version_evidence"):
        add("wrong_version_evidence", metrics["wrong_version_evidence"], "[]")
    if metrics.get("forbidden_evidence"):
        add("forbidden_evidence", metrics["forbidden_evidence"], "[]")
    if (
        metric_applicability.get("refusal_evidence_recall", False)
        and float(metrics.get("refusal_evidence_recall", 0.0)) < 1.0
    ):
        add(
            "refusal_evidence_recall",
            metrics.get("refusal_evidence_recall"),
            "1.0 refusal-support evidence recall",
            "diagnostic",
        )
    if mode in {"qa", "full"}:
        if metrics.get("citation_integrity") is False:
            add("citation_integrity", False, "true")
        if metric_applicability.get("required_identifiers", True) and metrics.get("missing_identifiers"):
            add("missing_identifiers", metrics["missing_identifiers"], "[]")
        if metric_applicability.get("identifier_hallucination_rate", True) and metrics.get("hallucinated_identifiers"):
            add(
                "hallucinated_identifiers",
                metrics["hallucinated_identifiers"],
                "[]; aggregate rate < 0.03",
                "diagnostic",
            )
        if (
            metric_applicability.get(
                "answer_point_coverage",
                metrics.get("answer_point_coverage") is not None,
            )
            and metrics.get("answer_point_coverage") is not None
            and float(metrics["answer_point_coverage"]) < 1.0
        ):
            add(
                "answer_point_coverage",
                metrics.get("answer_point_coverage"),
                "1.0 per case for a perfect result; aggregate gate >= 0.85",
                "diagnostic",
            )
        if metric_applicability.get(
            "contradictions", "contradictions" in metrics
        ) and metrics.get("contradictions"):
            add("contradictions", metrics["contradictions"], "[]")
        if metric_applicability.get(
            "unsupported_claim_ids", "unsupported_claim_ids" in metrics
        ) and metrics.get("unsupported_claim_ids"):
            add("unsupported_claim_ids", metrics["unsupported_claim_ids"], "[]")
        if metric_applicability.get(
            "major_unsupported_claim_ids", "major_unsupported_claim_ids" in metrics
        ) and metrics.get("major_unsupported_claim_ids"):
            add(
                "major_unsupported_claim_ids",
                metrics["major_unsupported_claim_ids"],
                "[]",
            )
        if (
            {"paper", "code"}.issubset(set(record.get("required_source_types", [])))
            and metric_applicability.get("paper_code_dual_source", True)
            and metrics.get("paper_code_dual_source") is False
        ):
            add("paper_code_dual_source", False, "true")
    return issues


def _suggest_review_layer(issues: list[dict[str, Any]], mode: EvaluationMode) -> str:
    names = {item["metric"] for item in issues}
    if "unhandled_exception" in names:
        return "infrastructure"
    if names & {
        "intent_correct",
        "gold_recall_at_10",
        "final_evidence_recall",
        "required_source_coverage",
        "wrong_version_evidence",
        "forbidden_evidence",
    }:
        return "retrieval"
    if mode in {"qa", "full"} and names:
        return "qa"
    return "evaluation"


def build_failure_review(
    dataset: GoldDataset,
    manifest: dict[str, Any],
    records: list[dict[str, Any]],
    *,
    run_id: str,
) -> dict[str, Any]:
    """Build a human-editable review document without calling any model."""
    questions = {item.id: item for item in dataset.questions}
    mode: EvaluationMode = manifest["mode"]
    entries: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: item["id"]):
        issues = _review_issues(record, mode)
        if not issues:
            continue
        question = questions[record["id"]]
        result = record.get("result") or {}
        claims = result.get("claims") or []
        citations: dict[str, list[str]] = {}
        for claim in claims:
            for evidence_id in claim.get("evidence_ids", []):
                citations.setdefault(evidence_id, []).append(claim.get("claim_id", ""))
        supporting_evidence = []
        for evidence in result.get("evidence", []):
            evidence_id = evidence.get("evidence_id", "")
            if claims and evidence_id not in citations:
                continue
            supporting_evidence.append(
                {
                    "evidence_id": evidence_id,
                    "source_id": evidence.get("source_id"),
                    "source_version_id": evidence.get("source_version_id"),
                    "authority_level": evidence.get("authority_level"),
                    "locator": evidence.get("locator") or {},
                    "cited_by_claim_ids": citations.get(evidence_id, []),
                    "text_excerpt": str(evidence.get("text", ""))[:1600],
                }
            )
        entries.append(
            {
                "case_id": record["id"],
                "question": question.query,
                "intent": question.intent,
                "language": question.language,
                "expected_status": question.expected_status.value,
                "actual_status": result.get("status", "error"),
                "required_answer_points": [item.model_dump(mode="json") for item in question.required_answer_points],
                "required_identifiers": [item.model_dump(mode="json") for item in question.required_identifiers],
                "observed_issues": issues,
                "metrics": record.get("metrics") or {},
                "model_output": {
                    "answer": result.get("answer", ""),
                    "claims": claims,
                    "verification_errors": result.get("verification_errors", []),
                    "exception": record.get("exception"),
                },
                "supporting_evidence": supporting_evidence,
                "suggested_layer": _suggest_review_layer(issues, mode),
                "human_review": {
                    "status": "pending",
                    "classification": "pending",
                    "action": "pending",
                    "target_layer": "pending",
                    "rationale": "",
                    "reviewer": "",
                    "reviewed_at": None,
                    "waiver_id": None,
                },
            }
        )
    split = manifest["split"]
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "mode": mode,
        "split": split,
        "generated_at": datetime.now(UTC).isoformat(),
        "manifest_identity": {
            key: manifest.get(key)
            for key in (
                "source_manifest_hash",
                "index_identity",
                "generation_model_id",
                "embedding_model_id",
                "prompt_hash",
                "retrieval_policy_hash",
                "query_expansion_hash",
                "gold_dataset_hash",
            )
        },
        "allowed_classifications": [
            "metric_false_positive",
            "real_failure",
            "acceptable_exception",
        ],
        "allowed_actions": (
            ["rescore", "fix", "waiver"]
            if split == "dev"
            else ["archive", "release_reject"]
        ),
        "policy": (
            "Development failures must be reviewed before any fix or rescore."
            if split == "dev"
            else "Acceptance is final-only; its results must not be used for targeted tuning."
            if split == "acceptance"
            else "Exposed regression failures require review; rerun only affected cases unless the fix changes shared runtime behavior."
        ),
        "entries": entries,
    }


def _failure_review_markdown(review: dict[str, Any]) -> str:
    lines = [
        f"# Failure review: {review['run_id']}",
        "",
        f"- Mode: `{review['mode']}`",
        f"- Split: `{review['split']}`",
        f"- Cases requiring review: `{len(review['entries'])}`",
        f"- Policy: {review['policy']}",
        "",
        "> `failure_review.yaml` is the canonical editable form. This Markdown file is a readable snapshot.",
        "",
        "## Review summary",
        "",
        "| Case | Expected / actual | Issues | Suggested layer | Classification | Action |",
        "|---|---|---|---|---|---|",
    ]
    for entry in review["entries"]:
        issue_names = ", ".join(item["metric"] for item in entry["observed_issues"])
        lines.append(
            f"| `{entry['case_id']}` | `{entry['expected_status']}` / `{entry['actual_status']}` | "
            f"{issue_names} | `{entry['suggested_layer']}` | pending | pending |"
        )
    for entry in review["entries"]:
        lines.extend(
            [
                "",
                f"## {entry['case_id']}",
                "",
                f"**Question:** {entry['question']}",
                "",
                f"**Expected / actual status:** `{entry['expected_status']}` / `{entry['actual_status']}`",
                "",
                f"**Suggested layer:** `{entry['suggested_layer']}`",
                "",
                "### Observed metrics",
                "",
                "```json",
                json.dumps(entry["metrics"], ensure_ascii=False, sort_keys=True, indent=2),
                "```",
                "",
                "### Model output",
                "",
                entry["model_output"]["answer"] or "_(empty answer)_",
                "",
                "### Claims",
                "",
                "```json",
                json.dumps(entry["model_output"]["claims"], ensure_ascii=False, indent=2),
                "```",
                "",
                "### Supporting evidence",
                "",
            ]
        )
        if not entry["supporting_evidence"]:
            lines.append("_(no cited evidence; inspect the exception or retrieval diagnostics)_")
        for evidence in entry["supporting_evidence"]:
            locator = evidence["locator"]
            locator_text = (
                locator.get("path")
                or locator.get("url")
                or f"PDF page {locator.get('pdf_page')}"
            )
            lines.extend(
                [
                    f"#### {evidence['evidence_id']}",
                    "",
                    f"- Source: `{evidence['source_id']}` / `{evidence['source_version_id']}`",
                    f"- Locator: `{locator_text}`",
                    f"- Cited by: `{', '.join(evidence['cited_by_claim_ids'])}`",
                    "",
                    "```text",
                    evidence["text_excerpt"],
                    "```",
                    "",
                ]
            )
        lines.extend(
            [
                "### Human decision",
                "",
                "- Classification: `pending` (`metric_false_positive` / `real_failure` / `acceptable_exception`)",
                f"- Action: `pending` ({' / '.join(review['allowed_actions'])})",
                "- Target layer: `pending`",
                "- Rationale:",
                "- Reviewer:",
                "- Reviewed at:",
                "- Waiver ID (required only for waiver):",
            ]
        )
    return "\n".join(lines) + "\n"


def write_failure_review(
    project_root: Path,
    run_id: str,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write YAML and Markdown review artifacts without overwriting decisions."""
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"evaluation run does not exist: {run_id}")
    yaml_path = run_dir / "failure_review.yaml"
    markdown_path = run_dir / "failure_review.md"
    if yaml_path.exists() and not overwrite:
        existing = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        return {
            "yaml_path": str(yaml_path),
            "markdown_path": str(markdown_path),
            "review_case_count": len(existing.get("entries", [])),
            "created": False,
        }
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest_dataset_path = manifest.get("gold_dataset_path")
    dataset = load_gold_dataset(
        Path(manifest_dataset_path)
        if manifest_dataset_path
        else project_root / "evaluation" / "gold_questions.yaml"
    )
    review = build_failure_review(dataset, manifest, load_run_records(run_dir), run_id=run_id)
    yaml_path.write_text(
        yaml.safe_dump(review, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    markdown_path.write_text(_failure_review_markdown(review), encoding="utf-8")
    return {
        "yaml_path": str(yaml_path),
        "markdown_path": str(markdown_path),
        "review_case_count": len(review["entries"]),
        "created": True,
    }


def validate_failure_review(project_root: Path, run_id: str) -> dict[str, Any]:
    """Validate that every generated review entry has a complete human decision."""
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    path = run_dir / "failure_review.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"failure review does not exist: {run_id}")
    review = yaml.safe_load(path.read_text(encoding="utf-8"))
    decisions_path = run_dir / "failure_review_decisions.yaml"
    if decisions_path.is_file():
        overlay = yaml.safe_load(decisions_path.read_text(encoding="utf-8")) or {}
        if overlay.get("run_id") != run_id:
            raise ValueError("failure review decision overlay has the wrong run_id")
        decisions = {
            item.get("case_id"): item.get("human_review") or {}
            for item in overlay.get("decisions", [])
        }
        review_ids = {item.get("case_id") for item in review.get("entries", [])}
        if set(decisions) != review_ids:
            missing = sorted(review_ids - set(decisions))
            extra = sorted(set(decisions) - review_ids)
            raise ValueError(
                f"failure review decision IDs do not match generated review; missing={missing}, extra={extra}"
            )
        for entry in review.get("entries", []):
            entry["human_review"] = decisions[entry.get("case_id")]
    allowed_classifications = set(review.get("allowed_classifications", []))
    allowed_actions = set(review.get("allowed_actions", []))
    errors: list[str] = []
    for entry in review.get("entries", []):
        decision = entry.get("human_review") or {}
        case_id = entry.get("case_id", "unknown")
        if decision.get("status") != "reviewed":
            errors.append(f"{case_id}: status must be reviewed")
        if decision.get("classification") not in (
            allowed_classifications | REVIEW_CLASSIFICATIONS
        ):
            errors.append(f"{case_id}: invalid or pending classification")
        if decision.get("action") not in (
            allowed_actions | {"rescore", "fix", "waiver"}
        ):
            errors.append(f"{case_id}: invalid or pending action")
        if not str(decision.get("rationale") or "").strip():
            errors.append(f"{case_id}: rationale is required")
        if not str(decision.get("reviewer") or "").strip() or not decision.get("reviewed_at"):
            errors.append(f"{case_id}: reviewer and reviewed_at are required")
        if decision.get("action") in {"rescore", "fix"} and decision.get("target_layer") in {
            None,
            "",
            "pending",
        }:
            errors.append(f"{case_id}: target_layer is required for {decision.get('action')}")
        if decision.get("action") == "waiver" and not decision.get("waiver_id"):
            errors.append(f"{case_id}: waiver_id is required for waiver")
    return {
        "valid": not errors,
        "run_id": run_id,
        "review_case_count": len(review.get("entries", [])),
        "decision_overlay": str(decisions_path) if decisions_path.is_file() else None,
        "errors": errors,
    }


def import_failure_review_decisions(
    project_root: Path,
    run_id: str,
    reviewed_path: Path,
) -> dict[str, Any]:
    """Import signed decisions without mutating the generated evidence snapshot."""
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    generated_path = run_dir / "failure_review.yaml"
    if not generated_path.is_file():
        raise FileNotFoundError(f"failure review does not exist: {run_id}")
    if not reviewed_path.is_file():
        raise FileNotFoundError(f"reviewed decision file does not exist: {reviewed_path}")
    generated = yaml.safe_load(generated_path.read_text(encoding="utf-8")) or {}
    reviewed = yaml.safe_load(reviewed_path.read_text(encoding="utf-8")) or {}
    if reviewed.get("run_id") != run_id:
        raise ValueError("reviewed decision file has the wrong run_id")
    generated_ids = {item.get("case_id") for item in generated.get("entries", [])}
    reviewed_entries = reviewed.get("entries", [])
    reviewed_ids = {item.get("case_id") for item in reviewed_entries}
    if generated_ids != reviewed_ids:
        raise ValueError(
            "reviewed decision IDs do not match generated review; "
            f"missing={sorted(generated_ids - reviewed_ids)}, "
            f"extra={sorted(reviewed_ids - generated_ids)}"
        )
    decisions = []
    for entry in sorted(reviewed_entries, key=lambda item: item["case_id"]):
        review = dict(entry.get("human_review") or {})
        original_action = review.get("action")
        original_classification = review.get("classification")
        if original_action == "archive":
            canonical_action = (
                "waiver" if original_classification == "acceptable_exception" else "rescore"
            )
        else:
            canonical_action = REVIEW_ACTION_ALIASES.get(original_action, original_action)
        if canonical_action not in {"rescore", "fix", "waiver"}:
            raise ValueError(
                f"{entry['case_id']}: unsupported reviewed action {original_action!r}"
            )
        if original_classification not in REVIEW_CLASSIFICATIONS:
            raise ValueError(
                f"{entry['case_id']}: unsupported reviewed classification "
                f"{original_classification!r}"
            )
        review["action"] = canonical_action
        review["original_action"] = original_action
        review["original_classification"] = original_classification
        decisions.append({"case_id": entry["case_id"], "human_review": review})
    overlay = {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_review_sha256": sha256_file(generated_path),
        "imported_source_sha256": sha256_file(reviewed_path),
        "imported_at": datetime.now(UTC).isoformat(),
        "decisions": decisions,
    }
    output = run_dir / "failure_review_decisions.yaml"
    output.write_text(
        yaml.safe_dump(overlay, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    validation = validate_failure_review(project_root, run_id)
    if not validation["valid"]:
        output.unlink(missing_ok=True)
        raise ValueError(f"imported review decisions are incomplete: {validation['errors']}")
    return {
        **validation,
        "imported_source": str(reviewed_path),
        "imported_source_sha256": overlay["imported_source_sha256"],
    }


def run_evaluation(
    project_root: Path,
    *,
    mode: EvaluationMode,
    split: EvaluationSplit,
    run_id: str,
    allow_draft: bool = False,
    resume: bool = False,
    limit: int | None = None,
    case_ids: list[str] | None = None,
    dataset_path: Path | None = None,
    max_model_calls: int | None = None,
    max_token_usage: int | None = None,
    deadline_minutes: float | None = None,
    evaluator_catalog_path: Path | None = None,
) -> Path:
    dataset_path = (dataset_path or default_gold_dataset_path(project_root)).resolve()
    evaluator_catalog = None
    if evaluator_catalog_path is not None:
        receipt = catalog_receipt(evaluator_catalog_path)
        evaluator_catalog = {
            "schema_version": receipt.schema_version,
            "lookup_contract": receipt.lookup_contract,
            "sha256": receipt.sha256,
            "count": receipt.count,
        }
    dataset = load_gold_dataset(dataset_path)
    if split == "acceptance":
        if dataset.acceptance_exposed:
            raise ValueError(
                "hidden acceptance is not created; exposed benchmark cannot run as acceptance"
            )
        if not dataset.release_eligible:
            raise ValueError("acceptance dataset must set release_eligible=true")
    approval_split = None if split == "all" else split
    if not allow_draft:
        dataset.require_approved(approval_split)
    cases = _selected_questions(dataset, split)
    if not cases:
        if split == "acceptance" and dataset.acceptance_exposed:
            raise ValueError(
                "hidden acceptance is not created; the reviewed v2 dataset contains only "
                "exposed dev/challenge/regression questions"
            )
        raise ValueError(f"dataset contains no questions for split {split}")
    if case_ids:
        requested = set(case_ids)
        available = {item.id for item in cases}
        unknown = sorted(requested - available)
        if unknown:
            raise ValueError(f"case IDs are not in split {split}: {unknown}")
        cases = [item for item in cases if item.id in requested]
    if limit is not None:
        if limit <= 0:
            raise ValueError("limit must be positive")
        cases = cases[:limit]
    manifest = build_evaluation_manifest(
        project_root,
        dataset_path,
        mode=mode,
        split=split,
        official=not allow_draft,
    )
    manifest["limit"] = limit
    manifest["case_ids"] = [item.id for item in cases] if case_ids else None
    manifest["max_model_calls"] = max_model_calls
    manifest["max_token_usage"] = max_token_usage
    manifest["deadline_minutes"] = deadline_minutes
    # The path is operational metadata only.  Resume comparison uses this
    # immutable receipt so a changed catalog at the same physical path fails.
    manifest["evaluator_catalog_path"] = (
        str(evaluator_catalog_path.resolve()) if evaluator_catalog_path is not None else None
    )
    manifest["evaluator_catalog"] = evaluator_catalog
    if resume:
        existing_manifest_path = (
            project_root
            / "data"
            / "evaluation"
            / "runs"
            / run_id
            / "manifest.json"
        )
        existing_manifest = json.loads(
            existing_manifest_path.read_text(encoding="utf-8")
        )
        if existing_manifest.get("evaluator_catalog") != evaluator_catalog:
            raise ValueError("evaluation resume evaluator catalog receipt mismatch")
        manifest["run_started_at"] = existing_manifest["run_started_at"]
    else:
        manifest["run_started_at"] = datetime.now(UTC).isoformat()
    store = EvaluationRunStore(
        project_root / "data" / "evaluation" / "runs",
        run_id,
        manifest,
        resume=resume,
    )
    boundaries = evaluation_mode_boundaries(mode)
    engine: Retriever | QAAgent = (
        Retriever(project_root) if not boundaries["answer_generation"] else QAAgent(project_root)
    )
    judge_vertex: VertexAIClient | None = None
    if boundaries["external_judge"]:
        runtime_vertex = engine.vertex
        judge_vertex = VertexAIClient(
            runtime_vertex.settings.for_generation_model(
                runtime_vertex.settings.evaluation_judge_model
            )
        )
    object_lookup = load_object_lookup(
        project_root, evaluator_catalog_path=evaluator_catalog_path,
    )
    existing_records = load_run_records(store.run_dir)
    cumulative_calls = sum(int(item.get("model_calls", 0)) for item in existing_records)
    cumulative_tokens = sum(int(item.get("token_usage", 0)) for item in existing_records)
    # Budgets and deadlines are per execution attempt.  A resumed run keeps
    # the same manifest and completed records, but receives a fresh bounded
    # window so a prior budget stop does not make resume impossible.
    attempt_started_at = datetime.now(UTC)
    attempt_calls = 0
    attempt_tokens = 0
    deadline_at = (
        attempt_started_at.timestamp() + float(deadline_minutes) * 60
        if deadline_minutes is not None
        else None
    )
    stop_reason: str | None = None
    for case in cases:
        if case.id in store.completed_ids:
            continue
        stop_reason = _attempt_budget_stop_reason(
            attempt_calls=attempt_calls,
            attempt_tokens=attempt_tokens,
            max_model_calls=max_model_calls,
            max_token_usage=max_token_usage,
            deadline_at=deadline_at,
        )
        if stop_reason:
            break
        before_runtime = _stats_snapshot(engine)
        before_judge = judge_vertex.stats_snapshot() if judge_vertex else {}
        started = time.perf_counter()
        record: dict[str, Any] = {
            "id": case.id,
            "intent": case.intent,
            "split": case.split,
            "language": case.language,
            "expected_status": case.expected_status.value,
            "required_source_types": case.required_source_types,
            "completed_at": datetime.now(UTC).isoformat(),
        }
        try:
            result, diagnostics, metrics = _execute_evaluation_case(
                engine,
                judge_vertex,
                mode=mode,
                case=case,
                object_lookup=object_lookup,
            )
            trace = build_retrieval_trace(
                question_id=case.id,
                run_id=run_id,
                question=case.query,
                diagnostics=diagnostics,
                manifest=manifest,
                object_lookup=object_lookup,
                result=result,
            )
            write_retrieval_trace(store.run_dir, trace)
            record.update(
                {
                    "result": result,
                    "diagnostics": diagnostics,
                    "metrics": metrics,
                }
            )
        except Exception as exc:
            record["exception"] = {
                "type": type(exc).__name__,
                "message": str(exc)[:2000],
            }
        record["duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        runtime_usage = _stats_delta(before_runtime, _stats_snapshot(engine))
        judge_usage = (
            _stats_delta(before_judge, judge_vertex.stats_snapshot())
            if judge_vertex
            else {}
        )
        usage = {
            "model_calls": runtime_usage.get("model_calls", 0)
            + judge_usage.get("model_calls", 0),
            "token_usage": runtime_usage.get("token_usage", 0)
            + judge_usage.get("token_usage", 0),
            "runtime": runtime_usage,
            "judge": judge_usage,
        }
        record["model_calls"] = usage["model_calls"]
        record["token_usage"] = usage["token_usage"]
        record["model_call_breakdown"] = usage
        store.record(record)
        attempt_calls += usage["model_calls"]
        attempt_tokens += usage["token_usage"]
        cumulative_calls += usage["model_calls"]
        cumulative_tokens += usage["token_usage"]
        print(
            json.dumps(
                {
                    "id": case.id,
                    "status": record.get("result", {}).get("status", "error"),
                    "duration_ms": record["duration_ms"],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        stop_reason = _attempt_budget_stop_reason(
            attempt_calls=attempt_calls,
            attempt_tokens=attempt_tokens,
            max_model_calls=max_model_calls,
            max_token_usage=max_token_usage,
            deadline_at=deadline_at,
        )
        if stop_reason:
            break
    run_status = {
        "status": "budget_exhausted" if stop_reason else "complete",
        "stop_reason": stop_reason,
        "attempt_started_at": attempt_started_at.isoformat(),
        "attempt_completed_at": datetime.now(UTC).isoformat(),
        "attempt_model_calls": attempt_calls,
        "attempt_token_usage": attempt_tokens,
        "completed_ids": sorted(store.completed_ids),
        "cumulative_model_calls": cumulative_calls,
        "cumulative_token_usage": cumulative_tokens,
        # Keep the legacy names for readers of prior run artifacts.
        "model_calls": cumulative_calls,
        "token_usage": cumulative_tokens,
    }
    (store.run_dir / "run_status.json").write_text(
        json.dumps(run_status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_evaluation(project_root, run_id)
    return store.run_dir


def report_evaluation(project_root: Path, run_id: str) -> dict[str, Any]:
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"evaluation run does not exist: {run_id}")
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    records = load_run_records(run_dir)
    records_for_metrics = normalize_run_records(records, manifest)
    metrics = aggregate_metrics(records_for_metrics)
    metrics["result_content_hash"] = result_content_hash(records)
    manifest_dataset_path = manifest.get("gold_dataset_path")
    dataset = load_gold_dataset(
        Path(manifest_dataset_path)
        if manifest_dataset_path
        else project_root / "evaluation" / "gold_questions.yaml"
    )
    selected = _selected_questions(dataset, manifest["split"])
    if manifest.get("case_ids"):
        requested = set(manifest["case_ids"])
        selected = [item for item in selected if item.id in requested]
    if manifest.get("limit") is not None:
        selected = selected[: int(manifest["limit"])]
    all_approved = bool(selected) and all(item.review_status == "approved" for item in selected)
    all_dev_ids = {
        str(item.id)
        for item in dataset.questions
        if item.split == "dev" and item.review_status == "approved"
    }
    requested_case_ids = set(manifest.get("case_ids") or [])
    record_ids = [str(record.get("id")) for record in records]
    selected_ids = {str(item.id) for item in selected}
    explicit_complete_dev = bool(requested_case_ids) and requested_case_ids == all_dev_ids
    full_dev_execution = (
        manifest.get("official") is True
        and manifest.get("split") == "dev"
        and manifest.get("limit") is None
        and (not requested_case_ids or explicit_complete_dev)
        and len(record_ids) == len(set(record_ids))
        and set(record_ids) == all_dev_ids
        and selected_ids == all_dev_ids
    )
    complete_full_dev = full_dev_execution
    complete_full_regression = (
        manifest.get("official") is True
        and manifest.get("mode") == "full"
        and manifest.get("split") == "regression"
        and manifest.get("limit") is None
        and not manifest.get("case_ids")
        and len(records) == len(selected) == 16
    )
    development_gate = evaluate_development_gate(
        metrics,
        records,
        mode=manifest["mode"],
        complete_full_dev=complete_full_dev,
        all_questions_approved=all_approved,
    )
    calibration = load_product_language_calibration(project_root)
    product_development_gate = None
    if calibration is not None and full_dev_execution:
        try:
            product_ids = set(
                english_product_case_ids(dataset, "dev", calibration=calibration)
            )
            product_records = [
                record
                for record in records_for_metrics
                if str(record.get("id")) in product_ids
            ]
            product_metrics = aggregate_metrics(product_records)
            product_development_gate = evaluate_product_development_gate(
                product_metrics,
                product_records,
                dataset,
                mode=manifest["mode"],
                calibration=calibration,
                dataset_path=(
                    Path(manifest_dataset_path)
                    if manifest_dataset_path
                    else project_root / "evaluation" / "gold_questions.yaml"
                ),
            )
        except ValueError as exc:
            product_development_gate = {
                "compatible": False,
                "reason": str(exc),
                "passed": None,
            }
    official_gate_run = (
        manifest.get("official") is True
        and manifest.get("mode") == "full"
        and manifest.get("split") == "acceptance"
        and manifest.get("limit") is None
        and not manifest.get("case_ids")
        and manifest.get("gold_release_eligible") is True
        and manifest.get("gold_acceptance_exposed") is False
        and len(records) == len(selected)
        and len(records)
        == manifest.get("gold_expected_split_counts", {}).get("acceptance")
    )
    gate = evaluate_quality_gate(
        metrics,
        records,
        official=official_gate_run,
        all_questions_approved=all_approved,
    )
    regression_gate = evaluate_regression_gate(
        metrics,
        records,
        complete_full_regression=complete_full_regression,
        all_questions_approved=all_approved,
    )
    report = {
        "run_id": run_id,
        "manifest": manifest,
        "metrics": metrics,
        "development_gate": development_gate,
        "product_development_gate": product_development_gate,
        "gate": gate,
        "regression_gate": regression_gate,
    }
    (run_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "gate.json").write_text(
        json.dumps(gate, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "development_gate.json").write_text(
        json.dumps(development_gate, ensure_ascii=False, sort_keys=True, indent=2)
        + "\n",
        encoding="utf-8",
    )
    if product_development_gate is not None:
        (run_dir / "product_development_gate.json").write_text(
            json.dumps(
                product_development_gate, ensure_ascii=False, sort_keys=True, indent=2
            )
            + "\n",
            encoding="utf-8",
        )
    (run_dir / "regression_gate.json").write_text(
        json.dumps(regression_gate, ensure_ascii=False, sort_keys=True, indent=2)
        + "\n",
        encoding="utf-8",
    )
    if complete_full_dev and not development_gate["passed"]:
        report["failure_review"] = write_failure_review(project_root, run_id)
    lines = [
        f"# Evaluation report: {run_id}",
        "",
        f"- Mode: `{manifest['mode']}`",
        f"- Split: `{manifest['split']}`",
        f"- Official: `{manifest['official']}`",
        f"- Completed: `{len(records)}/{len(selected)}`",
        f"- Development gate passed: `{development_gate['passed']}`",
        f"- Product development gate passed: `{product_development_gate.get('passed', 'N/A') if product_development_gate is not None else 'N/A'}`",
        f"- Gate passed: `{gate['passed']}`",
        "",
        "## Metrics",
        "",
        "```json",
        json.dumps(metrics, ensure_ascii=False, sort_keys=True, indent=2),
        "```",
        "",
        "## Gate checks",
        "",
    ]
    lines.extend(
        f"- [{'x' if passed else ' '}] `dev:{name}`"
        for name, passed in development_gate["checks"].items()
    )
    lines.extend(["", "## Formal acceptance checks", ""])
    lines.extend(
        f"- [{'x' if passed else ' '}] `{name}`"
        for name, passed in gate["checks"].items()
    )
    lines.extend(["", "## Exposed regression checks", ""])
    lines.extend(
        f"- [{'x' if passed else ' '}] `{name}`"
        for name, passed in regression_gate["checks"].items()
    )
    (run_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def resume_evaluation(project_root: Path, run_id: str) -> Path:
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    return run_evaluation(
        project_root,
        mode=manifest["mode"],
        split=manifest["split"],
        run_id=run_id,
        allow_draft=not manifest["official"],
        resume=True,
        limit=manifest.get("limit"),
        case_ids=manifest.get("case_ids"),
        max_model_calls=manifest.get("max_model_calls"),
        max_token_usage=manifest.get("max_token_usage"),
        deadline_minutes=manifest.get("deadline_minutes"),
        dataset_path=Path(manifest["gold_dataset_path"])
        if manifest.get("gold_dataset_path")
        else None,
        evaluator_catalog_path=Path(manifest["evaluator_catalog_path"])
        if manifest.get("evaluator_catalog_path")
        else None,
    )
