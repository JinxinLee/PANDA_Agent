"""Stage finalization and execution recovery helpers.

Implements generic infrastructure for:
1. Classifying evaluation case exceptions into:
   - completed (no exception)
   - retryable infrastructure exceptions (transport, 429, timeout, transient provider errors)
   - terminal non-retryable exceptions (contract errors, bad inputs, permanent faults)
2. Enforcing cohort-completeness decision rules:
   - Incomplete cohort with retryable exceptions -> RECOVERY_PENDING
   - Incomplete cohort unrecoverable under candidate -> INCONCLUSIVE / PRE_RELEASE_EXECUTION_INCOMPLETE
   - Complete cohort -> PASS, FAIL, or INCOMPLETE (if gate measurements missing)
   - Invalid candidate cannot PASS (verdict INCONCLUSIVE, passed None)
3. Generating immutable stage receipts binding exact stage inputs, results, IDs, candidate,
   usage, traces, and gate summaries BEFORE diagnostic report and failure inspection exposure.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Sequence

from panda_agent.models import QAStatus

LEGAL_QA_STATUS_VALUES = frozenset(status.value for status in QAStatus)

RETRY_CATEGORY_TRANSPORT_PROVIDER = "transport_provider_infrastructure"
RETRY_CATEGORY_UNPARSABLE_RESPONSE = "unparsable_response"

PERMANENT_ERROR_TOKENS = (
    "400",
    "401",
    "403",
    "404",
    "422",
    "unauthenticated",
    "permission_denied",
    "permission denied",
    "invalid_argument",
    "invalid argument",
    "unauthorized",
    "forbidden",
    "bad request",
    "api key not valid",
    "not_found",
    "failed_precondition",
)

TRANSIENT_STATUS_TOKENS = (
    "resource_exhausted",
    "temporarily unavailable",
    "timeout",
    "deadline",
    "unavailable",
    "connection reset",
    "socket closed",
    "rate limit",
    "overloaded",
    "internal server error",
)

TRANSIENT_HTTP_REGEX = re.compile(r"\b(429|500|502|503|504)\b")
PERMANENT_HTTP_REGEX = re.compile(r"\b(400|401|403|404|422)\b")


def _is_permanent_error_code(code: Any) -> bool:
    try:
        return int(code) in (400, 401, 403, 404, 422)
    except (TypeError, ValueError):
        return False


def _is_transient_error_code(code: Any) -> bool:
    try:
        return int(code) in (429, 500, 502, 503, 504)
    except (TypeError, ValueError):
        return False


def classify_evaluation_exception(
    exc_or_record: BaseException | dict[str, Any] | str | None,
) -> tuple[bool, str | None]:
    """Classify an exception or serialized exception record into retryable vs terminal.

    Returns (is_retryable, category_name).
    """
    if exc_or_record is None:
        return False, None

    if isinstance(exc_or_record, BaseException):
        exc_type_name = type(exc_or_record).__name__
        msg = str(exc_or_record).casefold()

        if isinstance(exc_or_record, json.JSONDecodeError):
            return True, RETRY_CATEGORY_UNPARSABLE_RESPONSE
        if isinstance(exc_or_record, ValueError):
            if "empty structured response" in msg or "must be a json object" in msg:
                return True, RETRY_CATEGORY_UNPARSABLE_RESPONSE
            return False, None

        if isinstance(exc_or_record, (ConnectionError, TimeoutError)):
            return True, RETRY_CATEGORY_TRANSPORT_PROVIDER

        cause = getattr(exc_or_record, "__cause__", None)
        code = (
            getattr(exc_or_record, "code", None)
            or getattr(exc_or_record, "status_code", None)
            or (getattr(cause, "code", None) if cause else None)
            or (getattr(cause, "status_code", None) if cause else None)
        )
        if callable(code):
            try:
                code = code()
            except Exception:
                code = None

        if _is_permanent_error_code(code):
            return False, None
        if _is_transient_error_code(code):
            return True, RETRY_CATEGORY_TRANSPORT_PROVIDER

        status = getattr(exc_or_record, "status", None) or (
            getattr(cause, "status", None) if cause else None
        )
        if callable(status):
            try:
                status = status()
            except Exception:
                status = None
        if status is not None:
            status_str = str(status).upper()
            if status_str in (
                "UNAUTHENTICATED",
                "PERMISSION_DENIED",
                "INVALID_ARGUMENT",
                "NOT_FOUND",
                "FAILED_PRECONDITION",
            ):
                return False, None
            if status_str in ("RESOURCE_EXHAUSTED", "UNAVAILABLE", "DEADLINE_EXCEEDED", "INTERNAL"):
                return True, RETRY_CATEGORY_TRANSPORT_PROVIDER

        if PERMANENT_HTTP_REGEX.search(msg) or any(tok in msg for tok in PERMANENT_ERROR_TOKENS):
            return False, None

        if exc_type_name in ("VertexCallError", "APIError", "GoogleAPICallError", "RuntimeError"):
            if TRANSIENT_HTTP_REGEX.search(msg) or any(tok in msg for tok in TRANSIENT_STATUS_TOKENS):
                return True, RETRY_CATEGORY_TRANSPORT_PROVIDER

        return False, None

    if isinstance(exc_or_record, dict):
        if "retryable" in exc_or_record and exc_or_record["retryable"] is not None:
            return bool(exc_or_record["retryable"]), exc_or_record.get("category")
        exc_type = str(exc_or_record.get("type", ""))
        msg = str(exc_or_record.get("message", "")).casefold()

        if PERMANENT_HTTP_REGEX.search(msg) or any(tok in msg for tok in PERMANENT_ERROR_TOKENS):
            return False, None

        if exc_type == "JSONDecodeError" or ("empty structured response" in msg or "must be a json object" in msg):
            return True, RETRY_CATEGORY_UNPARSABLE_RESPONSE

        if exc_type in ("ConnectionError", "TimeoutError"):
            return True, RETRY_CATEGORY_TRANSPORT_PROVIDER

        if exc_type in ("VertexCallError", "APIError", "GoogleAPICallError", "RuntimeError"):
            if TRANSIENT_HTTP_REGEX.search(msg) or any(tok in msg for tok in TRANSIENT_STATUS_TOKENS):
                return True, RETRY_CATEGORY_TRANSPORT_PROVIDER

        return False, None

    if isinstance(exc_or_record, str):
        msg = exc_or_record.casefold()
        if PERMANENT_HTTP_REGEX.search(msg) or any(tok in msg for tok in PERMANENT_ERROR_TOKENS):
            return False, None
        if TRANSIENT_HTTP_REGEX.search(msg) or any(tok in msg for tok in TRANSIENT_STATUS_TOKENS):
            return True, RETRY_CATEGORY_TRANSPORT_PROVIDER
        return False, None

    return False, None


def evaluation_record_state(record: dict[str, Any]) -> str:
    """Return 'completed', 'retryable_exception', or 'terminal_exception'."""
    exc = record.get("exception")
    if exc is None:
        return "completed"
    retryable, _ = classify_evaluation_exception(exc)
    return "retryable_exception" if retryable else "terminal_exception"


def evaluate_cohort_decision(
    *,
    records: Sequence[dict[str, Any]],
    expected_case_ids: Sequence[str] | set[str],
    candidate_valid: bool | None = True,
    gates_passed: bool | None = None,
    mode: str | None = None,
) -> dict[str, Any]:
    """Evaluate cohort completeness and derive official decision.

    Contract:
    1. Incomplete cohort with still-retryable infrastructure exceptions
       -> RECOVERY_PENDING before any gate decision.
    2. Incomplete cohort unrecoverable under candidate
       -> INCONCLUSIVE / PRE_RELEASE_EXECUTION_INCOMPLETE.
    3. Complete cohort (all expected cases scored without unhandled exceptions)
       -> PASS (if all gates pass) or FAIL (if any gate fails) or INCOMPLETE (if gate measurement None).
    4. Reject duplicate, malformed, extra, or empty records visibly.
    5. Invalid candidate identity can never PASS (verdict INCONCLUSIVE, passed None).
    """
    expected_set = set(str(cid) for cid in expected_case_ids)
    if not expected_set:
        raise ValueError("expected_case_ids cannot be empty")

    seen_ids: set[str] = set()
    actual_records_map: dict[str, dict[str, Any]] = {}

    for index, rec in enumerate(records or []):
        if not isinstance(rec, dict) or "id" not in rec or not str(rec["id"]).strip():
            raise ValueError(f"malformed evaluation record at index {index} missing valid id: {rec}")
        cid = str(rec["id"])
        if cid in seen_ids:
            raise ValueError(f"duplicate case ID in evaluation records: {cid}")
        seen_ids.add(cid)
        actual_records_map[cid] = rec

        exc = rec.get("exception")
        result = rec.get("result")
        metrics = rec.get("metrics")
        if exc is None:
            if not result and not metrics:
                raise ValueError(
                    f"malformed evaluation record for '{cid}': record has neither exception nor usable result/metrics"
                )
            if result is not None and not isinstance(result, dict):
                raise ValueError(
                    f"malformed evaluation record for '{cid}': result must be a dictionary"
                )
            if metrics is not None and not isinstance(metrics, dict):
                raise ValueError(
                    f"malformed evaluation record for '{cid}': metrics must be a dictionary"
                )
            if mode in ("qa", "full"):
                if result is None or not isinstance(result, dict):
                    raise ValueError(
                        f"malformed evaluation record for '{cid}': mode '{mode}' requires result dictionary, metrics alone invalid"
                    )
                status = result.get("status")
                status_str = status.value if isinstance(status, QAStatus) else status
                if not status_str or status_str not in LEGAL_QA_STATUS_VALUES:
                    raise ValueError(
                        f"malformed evaluation record for '{cid}': mode '{mode}' requires legal QAStatus in result['status'], got '{status}'"
                    )

    missing_ids = sorted(expected_set - set(actual_records_map.keys()))
    extra_ids = sorted(set(actual_records_map.keys()) - expected_set)
    if extra_ids:
        raise ValueError(f"unexpected extra case IDs in evaluation records: {extra_ids}")

    retryable_ids: list[str] = []
    terminal_exception_ids: list[str] = []
    scored_ids: list[str] = []

    for cid in sorted(actual_records_map.keys()):
        if cid not in expected_set:
            continue
        rec = actual_records_map[cid]
        state = evaluation_record_state(rec)
        if state == "completed":
            scored_ids.append(cid)
        elif state == "retryable_exception":
            retryable_ids.append(cid)
        else:
            terminal_exception_ids.append(cid)

    is_complete = not missing_ids and not extra_ids and not retryable_ids and not terminal_exception_ids

    # Invalid candidate identity must ALWAYS be INCONCLUSIVE and passed None
    if candidate_valid is False:
        return {
            "status": "COMPLETE" if is_complete else "INCOMPLETE",
            "verdict": "INCONCLUSIVE",
            "decision_reason": "INVALID_CANDIDATE_IDENTITY",
            "passed": None,
            "reason": (
                "evaluation candidate identity is invalid or unverified; "
                "cannot certify official evaluation verdict"
            ),
            "scored_case_count": len(scored_ids),
            "expected_case_count": len(expected_set),
            "retryable_case_ids": retryable_ids,
            "missing_case_ids": missing_ids,
            "terminal_exception_case_ids": terminal_exception_ids,
            "extra_case_ids": extra_ids,
        }

    if not is_complete:
        if retryable_ids or missing_ids:
            return {
                "status": "INCOMPLETE",
                "verdict": "RECOVERY_PENDING",
                "passed": None,
                "reason": (
                    f"incomplete cohort ({len(scored_ids)}/{len(expected_set)} scored) has "
                    f"{len(retryable_ids)} retryable exception(s) and {len(missing_ids)} missing case(s); "
                    "recovery pending before official decision"
                ),
                "scored_case_count": len(scored_ids),
                "expected_case_count": len(expected_set),
                "retryable_case_ids": retryable_ids,
                "missing_case_ids": missing_ids,
                "terminal_exception_case_ids": terminal_exception_ids,
                "extra_case_ids": extra_ids,
            }
        else:
            return {
                "status": "INCOMPLETE",
                "verdict": "INCONCLUSIVE",
                "decision_reason": "PRE_RELEASE_EXECUTION_INCOMPLETE",
                "passed": None,
                "reason": (
                    f"incomplete cohort ({len(scored_ids)}/{len(expected_set)} scored) cannot be recovered "
                    "under verified frozen candidate identity"
                ),
                "scored_case_count": len(scored_ids),
                "expected_case_count": len(expected_set),
                "retryable_case_ids": retryable_ids,
                "missing_case_ids": missing_ids,
                "terminal_exception_case_ids": terminal_exception_ids,
                "extra_case_ids": extra_ids,
            }

    if gates_passed is None:
        verdict = "INCOMPLETE"
        passed = None
        reason = f"complete cohort ({len(scored_ids)}/{len(expected_set)} scored) but gate measurement is missing (None)"
    elif gates_passed is True:
        verdict = "PASS"
        passed = True
        reason = f"complete cohort ({len(scored_ids)}/{len(expected_set)} scored); quality gates passed"
    else:
        verdict = "FAIL"
        passed = False
        reason = f"complete cohort ({len(scored_ids)}/{len(expected_set)} scored); quality gates failed"

    return {
        "status": "COMPLETE",
        "verdict": verdict,
        "passed": passed,
        "reason": reason,
        "scored_case_count": len(scored_ids),
        "expected_case_count": len(expected_set),
        "retryable_case_ids": [],
        "missing_case_ids": [],
        "terminal_exception_case_ids": [],
        "extra_case_ids": extra_ids,
    }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def resolve_expected_case_ids(project_root: Path, manifest: dict[str, Any]) -> list[str]:
    """Derive full expected case IDs from authoritative manifest or dataset/split/limit.

    Fails closed on missing declared dataset or declared hash mismatch.
    Explicit case_ids remain directly usable where fixture contracts supply them
    without declared dataset path or hash requirements.
    """
    manifest_dataset_path = manifest.get("gold_dataset_path")
    manifest_dataset_hash = manifest.get("gold_dataset_hash")

    # 1. Declared dataset path specified
    if manifest_dataset_path:
        dataset_path = Path(manifest_dataset_path)
        if not dataset_path.is_absolute():
            dataset_path = project_root / dataset_path
        if not dataset_path.exists():
            raise FileNotFoundError(
                f"declared gold dataset does not exist: {dataset_path}"
            )
        if manifest_dataset_hash:
            actual_hash = _sha256_file(dataset_path)
            if actual_hash != manifest_dataset_hash:
                raise ValueError(
                    f"gold dataset hash mismatch for {dataset_path}: "
                    f"expected {manifest_dataset_hash}, got {actual_hash}"
                )
        if manifest.get("case_ids"):
            return [str(cid) for cid in manifest["case_ids"]]
        from panda_agent.evaluation import load_gold_dataset
        from panda_agent.evaluation_runner import _selected_questions

        dataset = load_gold_dataset(dataset_path)
        selected = _selected_questions(dataset, manifest.get("split", "dev"))
        if manifest.get("limit"):
            selected = selected[: int(manifest["limit"])]
        return [str(getattr(q, "id", None) or q["id"]) for q in selected]

    # 2. Declared dataset hash specified without path -> resolve default and verify hash
    if manifest_dataset_hash:
        from panda_agent.evaluation_runner import default_gold_dataset_path

        try:
            dataset_path = default_gold_dataset_path(project_root)
        except Exception:
            dataset_path = project_root / "evaluation" / "gold_questions.yaml"
        if not dataset_path.exists():
            raise FileNotFoundError(
                f"cannot resolve gold dataset at {dataset_path} to verify declared hash"
            )
        actual_hash = _sha256_file(dataset_path)
        if actual_hash != manifest_dataset_hash:
            raise ValueError(
                f"gold dataset hash mismatch for {dataset_path}: "
                f"expected {manifest_dataset_hash}, got {actual_hash}"
            )
        if manifest.get("case_ids"):
            return [str(cid) for cid in manifest["case_ids"]]
        from panda_agent.evaluation import load_gold_dataset
        from panda_agent.evaluation_runner import _selected_questions

        dataset = load_gold_dataset(dataset_path)
        selected = _selected_questions(dataset, manifest.get("split", "dev"))
        if manifest.get("limit"):
            selected = selected[: int(manifest["limit"])]
        return [str(getattr(q, "id", None) or q["id"]) for q in selected]

    # 3. Neither declared path nor hash specified: explicit case_ids usable where fixture contract supplies them
    if manifest.get("case_ids"):
        return [str(cid) for cid in manifest["case_ids"]]

    # 4. Fallback to resolving default gold dataset
    from panda_agent.evaluation_runner import default_gold_dataset_path

    try:
        dataset_path = default_gold_dataset_path(project_root)
    except Exception:
        dataset_path = project_root / "evaluation" / "gold_questions.yaml"
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"cannot resolve gold dataset at {dataset_path} to determine expected case IDs"
        )
    from panda_agent.evaluation import load_gold_dataset
    from panda_agent.evaluation_runner import _selected_questions

    dataset = load_gold_dataset(dataset_path)
    selected = _selected_questions(dataset, manifest.get("split", "dev"))
    if manifest.get("limit"):
        selected = selected[: int(manifest["limit"])]
    return [str(getattr(q, "id", None) or q["id"]) for q in selected]


def resolve_candidate_binding(
    project_root: Path, manifest: dict[str, Any]
) -> tuple[str | None, str | None, bool | None]:
    """Safely resolve and verify candidate binding without guessing.

    Compares stored manifest hash with verified hash.
    Never guesses directory when candidate_id is omitted.
    Returns (candidate_id, candidate_manifest_sha256, is_valid).
    """
    candidate_id = manifest.get("candidate_id")
    if candidate_id:
        from panda_agent.candidate import verify_candidate

        try:
            res = verify_candidate(project_root, candidate_id)
            verified_hash = res.get("manifest_sha256")
            is_valid = bool(res.get("valid"))
            stored_hash = manifest.get("candidate_manifest_sha256") or manifest.get(
                "candidate_manifest_hash"
            )
            if stored_hash and verified_hash and stored_hash != verified_hash:
                is_valid = False
            return candidate_id, verified_hash, is_valid
        except Exception:
            return candidate_id, None, False

    # For non-official runs, candidate verification is not required for dev usability,
    # but does NOT imply frozen official validity.
    if not manifest.get("official", False):
        return None, None, None

    # Official runs without candidate_id fail closed; no guessing or directory scans.
    return None, None, False


def _result_content_hash(records: Sequence[dict[str, Any]]) -> str:
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
        for item in sorted(records, key=lambda value: str(value.get("id", "")))
    ]
    canonical = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _sha256_text(canonical)


def _load_run_records_internal(run_dir: Path) -> list[dict[str, Any]]:
    """Load atomic per-case records with results.jsonl fallback."""
    merged: dict[str, dict[str, Any]] = {}
    results_path = run_dir / "results.jsonl"
    if results_path.exists():
        for line in results_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                item = json.loads(line)
                merged[str(item["id"])] = item
    records_dir = run_dir / "records"
    if records_dir.is_dir():
        for p in sorted(records_dir.glob("*.json")):
            item = json.loads(p.read_text(encoding="utf-8"))
            merged[str(item["id"])] = item
    return [merged[k] for k in sorted(merged)]


def _get_run_usage(run_dir: Path, records: Sequence[dict[str, Any]]) -> tuple[int, int]:
    """Derive total model calls and token usage from attempts ledger or records."""
    attempts_path = run_dir / "attempts.jsonl"
    if attempts_path.exists():
        from panda_agent.evaluation import _load_jsonl_with_partial_tail

        attempt_lines = _load_jsonl_with_partial_tail(attempts_path)
        total_calls = sum(int(a.get("model_calls", 0)) for a in attempt_lines)
        total_tokens = sum(int(a.get("token_usage", 0)) for a in attempt_lines)
        return total_calls, total_tokens
    total_calls = sum(int(r.get("model_calls", 0)) for r in records)
    total_tokens = sum(int(r.get("token_usage", 0)) for r in records)
    return total_calls, total_tokens


def _build_stage_receipt(
    project_root: Path,
    run_id: str,
    *,
    metrics: dict[str, Any] | None = None,
    gate: dict[str, Any] | None = None,
    records: list[dict[str, Any]] | None = None,
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive the complete, deterministic stage receipt dictionary for a run."""
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    if manifest is None:
        manifest_path = run_dir / "manifest.json"
        manifest = (
            json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest_path.exists()
            else {}
        )

    gate_file = run_dir / "gate.json"
    if gate is None and gate_file.exists():
        try:
            gate = json.loads(gate_file.read_text(encoding="utf-8"))
        except Exception:
            gate = None

    metrics_file = run_dir / "metrics.json"
    if metrics is None and metrics_file.exists():
        try:
            metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
        except Exception:
            metrics = None

    if records is None:
        records = _load_run_records_internal(run_dir)

    results_path = run_dir / "results.jsonl"
    results_sha256 = _sha256_file(results_path) if results_path.exists() else None
    sorted_ids = sorted(str(r.get("id")) for r in records)
    case_id_set_sha256 = _sha256_text(json.dumps(sorted_ids, separators=(",", ":")))
    record_content_hash = _result_content_hash(records)

    expected_ids = resolve_expected_case_ids(project_root, manifest)
    candidate_id, candidate_manifest_sha256, candidate_valid = resolve_candidate_binding(
        project_root, manifest
    )

    total_calls, total_tokens = _get_run_usage(run_dir, records)

    traces_path = run_dir / "retrieval_traces.jsonl"
    traces_sha256 = _sha256_file(traces_path) if traces_path.exists() else None
    attempts_path = run_dir / "attempts.jsonl"
    attempts_sha256 = _sha256_file(attempts_path) if attempts_path.exists() else None
    manifest_file = run_dir / "manifest.json"
    manifest_file_sha256 = _sha256_file(manifest_file) if manifest_file.exists() else None
    gate_file_sha256 = _sha256_file(gate_file) if gate_file.exists() else None
    metrics_file_sha256 = _sha256_file(metrics_file) if metrics_file.exists() else None

    gates_passed = gate.get("passed") if isinstance(gate, dict) else None
    cohort_decision = evaluate_cohort_decision(
        records=records,
        expected_case_ids=expected_ids,
        candidate_valid=candidate_valid,
        gates_passed=gates_passed,
        mode=manifest.get("mode"),
    )

    candidate_impl_commit = None
    if candidate_id:
        c_manifest_path = (
            project_root
            / "evaluation"
            / "candidates"
            / candidate_id
            / "candidate_manifest.json"
        )
        if c_manifest_path.exists():
            try:
                c_data = json.loads(c_manifest_path.read_text(encoding="utf-8"))
                candidate_impl_commit = c_data.get("implementation_git_commit")
            except Exception:
                pass
    impl_commit = (
        candidate_impl_commit
        if candidate_id
        else (manifest.get("repository_identity") or {}).get("commit")
    )

    return {
        "schema_version": "stage-receipt-v1",
        "role": "archival stage receipt binding current results, gate summary, traces, and exact usage",
        "execution_status": {
            "run_id": run_id,
            "candidate_id": candidate_id,
            "candidate_valid": candidate_valid,
            "cohort_status": cohort_decision["status"],
            "decision": cohort_decision["verdict"],
            "scored_cases": cohort_decision["scored_case_count"],
            "expected_cases": cohort_decision["expected_case_count"],
            "terminal_label": cohort_decision["verdict"],
        },
        "identities": {
            "candidate_id": candidate_id,
            "candidate_manifest_sha256": candidate_manifest_sha256,
            "implementation_git_commit": impl_commit,
            "gold_benchmark_version": manifest.get("gold_benchmark_version"),
            "gold_dataset_hash": manifest.get("gold_dataset_hash"),
            "prompt_hash": manifest.get("prompt_hash"),
        },
        "artifacts_and_hashes": {
            "manifest_file_sha256": manifest_file_sha256,
            "case_id_set_sha256": case_id_set_sha256,
            "results_file_sha256": results_sha256,
            "result_content_hash": record_content_hash,
            "retrieval_traces_sha256": traces_sha256,
            "gate_file_sha256": gate_file_sha256,
            "metrics_file_sha256": metrics_file_sha256,
            "attempts_file_sha256": attempts_sha256,
            "record_count": len(records),
        },
        "usage": {
            "cumulative_model_calls": total_calls,
            "cumulative_token_usage": total_tokens,
        },
        "gate_summary": {
            "passed": gates_passed,
            "cohort_decision": cohort_decision,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


RECEIPT_BOUND_SECTIONS = (
    "schema_version",
    "execution_status",
    "identities",
    "artifacts_and_hashes",
    "usage",
    "gate_summary",
)


def _compare_receipt_sections(
    existing: dict[str, Any], recomputed: dict[str, Any]
) -> list[str]:
    return [sec for sec in RECEIPT_BOUND_SECTIONS if existing.get(sec) != recomputed.get(sec)]


def create_stage_receipt(
    project_root: Path,
    run_id: str,
    *,
    metrics: dict[str, Any] | None = None,
    gate: dict[str, Any] | None = None,
    records: list[dict[str, Any]] | None = None,
    manifest: dict[str, Any] | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Generate an immutable stage receipt binding exact run inputs, results, hashes, and decision.

    Must be generated before report.md or failure review diagnostics are exposed.
    Refuses to seal a final receipt if recovery is pending.
    Reads persisted gate/metrics files when arguments are omitted.
    Idempotent on identical receipt; raises ValueError on mismatched existing receipt.
    """
    receipt = _build_stage_receipt(
        project_root,
        run_id,
        metrics=metrics,
        gate=gate,
        records=records,
        manifest=manifest,
    )

    if receipt["execution_status"]["decision"] == "RECOVERY_PENDING":
        raise ValueError(
            f"cannot seal stage receipt while evaluation recovery is pending: "
            f"{receipt['gate_summary']['cohort_decision']['reason']}"
        )

    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    target = output_path or (run_dir / "stage_receipt.json")
    if target.exists():
        try:
            existing = json.loads(target.read_text(encoding="utf-8"))
            mismatches = _compare_receipt_sections(existing, receipt)
            if not mismatches:
                return existing
            raise ValueError(
                f"existing stage receipt {target} does not match current run state "
                f"(mismatched sections: {', '.join(mismatches)}); "
                "immutable stage receipts cannot be overwritten"
            )
        except json.JSONDecodeError:
            raise ValueError(f"existing stage receipt {target} is corrupted; cannot overwrite")

    target.parent.mkdir(parents=True, exist_ok=True)
    temp_target = target.parent / f".{target.name}.tmp"
    temp_target.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temp_target, target)
    return receipt


def validate_stage_receipt(
    project_root: Path,
    run_id: str,
    *,
    records: list[dict[str, Any]] | None = None,
    manifest: dict[str, Any] | None = None,
    receipt_path: Path | None = None,
    gate: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate that an existing stage receipt matches current run artifacts and identities.

    Catches edits to record contents, candidate, manifest, gates, traces, and usage.
    Recomputes and compares execution_status and full gate_summary.
    Raises FileNotFoundError if receipt does not exist.
    Raises ValueError if receipt is stale, corrupted, or mismatched.
    """
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    target = receipt_path or (run_dir / "stage_receipt.json")
    if not target.exists():
        raise FileNotFoundError(f"stage receipt does not exist: {target}")
    try:
        receipt = json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"stage receipt {target} is corrupted: {exc}") from exc

    if not isinstance(receipt, dict):
        raise ValueError(f"stage receipt {target} is corrupted: expected json object")

    if receipt.get("schema_version") != "stage-receipt-v1":
        raise ValueError(
            f"stage receipt {target} has unexpected schema version: {receipt.get('schema_version')}"
        )

    gate_file = run_dir / "gate.json"
    if gate is None:
        if gate_file.exists():
            try:
                gate = json.loads(gate_file.read_text(encoding="utf-8"))
            except Exception as exc:
                raise ValueError(f"stage receipt {target}: gate file {gate_file} is corrupted") from exc
        elif receipt.get("artifacts_and_hashes", {}).get("gate_file_sha256") is None:
            gate = {"passed": receipt.get("gate_summary", {}).get("passed")}

    metrics_file = run_dir / "metrics.json"
    if metrics is None:
        if metrics_file.exists():
            try:
                metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
            except Exception as exc:
                raise ValueError(f"stage receipt {target}: metrics file {metrics_file} is corrupted") from exc

    manifest_file = run_dir / "manifest.json"
    if manifest is None and manifest_file.exists():
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ValueError(f"stage receipt {target}: manifest file {manifest_file} is corrupted") from exc

    recomputed = _build_stage_receipt(
        project_root,
        run_id,
        metrics=metrics,
        gate=gate,
        records=records,
        manifest=manifest,
    )

    mismatches = _compare_receipt_sections(receipt, recomputed)
    if mismatches:
        raise ValueError(
            f"stage receipt {target} does not match current run state "
            f"(mismatched sections: {', '.join(mismatches)})"
        )

    return receipt


def finalize_stage_evaluation(
    project_root: Path,
    run_id: str,
    *,
    metrics: dict[str, Any],
    gate: dict[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Finalize an evaluation stage by generating the stage receipt before reports are generated.

    If evaluation recovery is pending, stage_receipt.json is not sealed.
    """
    run_dir = project_root / "data" / "evaluation" / "runs" / run_id
    manifest_path = run_dir / "manifest.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {}
    )
    expected_ids = resolve_expected_case_ids(project_root, manifest)
    _, _, candidate_valid = resolve_candidate_binding(project_root, manifest)
    gates_passed = gate.get("passed") if gate else None

    cohort_decision = evaluate_cohort_decision(
        records=records,
        expected_case_ids=expected_ids,
        candidate_valid=candidate_valid,
        gates_passed=gates_passed,
        mode=manifest.get("mode"),
    )

    if cohort_decision["verdict"] == "RECOVERY_PENDING":
        return None

    return create_stage_receipt(
        project_root,
        run_id,
        metrics=metrics,
        gate=gate,
        records=records,
        manifest=manifest,
    )
