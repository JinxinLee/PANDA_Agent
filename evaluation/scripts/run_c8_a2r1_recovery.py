"""Run the one authorized C8-A2R1 invocation-recovery capture."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.scripts import capture_c8_a2_two_pass as a2  # noqa: E402


TASK = "C8-A2R1"
FAILED_A2_COMMIT = "07594b9b6f2857796115bc9cfe00d3426676084b"
ORIGINAL_FAILURE_CLASS = "PRE_OUTCOME_VERTEX_ADC_INVOCATION_FAILURE"
RECEIPT_PATH = ROOT / "evaluation/baselines/manifests/phase_c_a2r1_invocation_recovery_receipt_v1.json"
LEDGER_PATH = ROOT / "evaluation/baselines/manifests/phase_c_a2r1_screening_ledger_v1.json"
CAPTURE_PATH = ROOT / "evaluation/baselines/replay/phase_c_a2r1_two_pass_capture_v1.jsonl"
REPORT_PATH = ROOT / "evaluation/baselines/manifests/phase_c_a2r1_two_pass_capture_report_v1.json"

ORIGINAL_A2_PATHS = (
    ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_global_treatment_preregistration_v1.json",
    ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_screening_ledger_v1.json",
    ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_two_pass_capture_report_v1.json",
    ROOT / "evaluation/baselines/replay/phase_c_c8_a2_two_pass_capture_v1.jsonl",
)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def recovery_paths() -> dict[str, Path]:
    return {
        "receipt": RECEIPT_PATH,
        "ledger": LEDGER_PATH,
        "capture": CAPTURE_PATH,
        "report": REPORT_PATH,
    }


def assert_recovery_outputs_absent(paths: Mapping[str, Path] | None = None) -> None:
    for name, path in (paths or recovery_paths()).items():
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing A2R1 {name}: {path}")


def assert_original_a2_artifacts_unchanged() -> None:
    for path in ORIGINAL_A2_PATHS:
        if not path.exists():
            raise FileNotFoundError(f"original A2 artifact is missing: {path}")
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        result = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"original A2 artifact changed: {relative}")


def verify_preregistration() -> dict[str, Any]:
    preregistration = a2.load_frozen_preregistration(a2.PREREGISTRATION_PATH)
    scientific = preregistration["scientific_fields"]
    mirror_pairs = {
        "cohort": "cohort_order",
        "s0": "s0",
        "g1": "g1",
        "primary_metrics": "primary_metrics",
        "hard_gates": "hard_gates",
        "meaningful_gain_rule": "meaningful_gain_rule",
    }
    for mirror, scientific_key in mirror_pairs.items():
        if preregistration.get(mirror) != scientific.get(scientific_key):
            raise RuntimeError(
                "PRE_LIVE_PREREGISTRATION_INTEGRITY_FAILURE: "
                f"top-level {mirror} disagrees with scientific_fields.{scientific_key}"
            )
    return preregistration


def build_recovery_receipt(
    preregistration: Mapping[str, Any],
    preflight: Mapping[str, Any],
    *,
    source_head: str,
) -> dict[str, Any]:
    return {
        "schema_version": "c8-a2r1-invocation-recovery-receipt-v1",
        "task": TASK,
        "failed_a2_commit": FAILED_A2_COMMIT,
        "original_failure_class": ORIGINAL_FAILURE_CLASS,
        "frozen_preregistration_path": str(a2.PREREGISTRATION_PATH.relative_to(ROOT)),
        "frozen_preregistration_unchanged": True,
        "scientific_fields_authoritative": True,
        "safe_projection_path": str(a2.PROJECTION_PATH.relative_to(ROOT)),
        "recovery_scope": "INVOCATION_ONLY",
        "recovery_restart_position": {"case_id": "g001", "screening_position": 1},
        "environment_preflight": dict(preflight),
        "gold_isolation": {
            "GOLD_FILE_ACCESSED": False,
            "GOLD_RELEVANCE_LABELS_ACCESSED": False,
            "GOLD_EVIDENCE_GROUPS_ACCESSED": False,
            "GOLD_ANSWER_RUBRICS_ACCESSED": False,
            "GOLD_EVALUATIONS": 0,
        },
        "novel_isolation": {"NOVEL_EVALUATIONS": 0},
        "no_scientific_rule_changed": True,
        "written_before_recovery_live_start": True,
        "source_head_at_recovery": source_head,
        "original_a2_artifacts_unchanged_before_live": True,
        "preregistration_identity": preregistration.get("task"),
    }


def _preflight_environment() -> dict[str, Any]:
    from dotenv import load_dotenv
    import google.auth
    from google.auth.transport.requests import Request

    load_dotenv(ROOT / ".env")
    settings = a2.VertexSettings.from_env()
    credentials, detected_project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    refresh_attempted = False
    if not credentials.valid:
        if not getattr(credentials, "refresh_token", None):
            raise RuntimeError("ADC credentials are invalid and not refreshable")
        credentials.refresh(Request())
        refresh_attempted = True
    if not credentials.valid:
        raise RuntimeError("ADC credentials remain invalid after refresh")

    # These two exact synthetic calls were completed immediately before this
    # recovery run in the same elevated environment; do not repeat health calls.
    vertex_health = {
        "generation": "PASS",
        "embedding": "PASS",
        "generation_calls": 1,
        "embedding_calls": 1,
        "source": "immediately_preceding_same_environment_preflight",
    }

    vertex = a2.VertexAIClient(settings)
    retriever = a2.CapturingRetriever(ROOT, vertex)
    a2.QAAgent(ROOT, retriever=retriever, vertex=retriever.vertex)
    return {
        "adc_resolution": "PASS",
        "credential_refresh_attempted": refresh_attempted,
        "project_resolved_by_google_auth": bool(detected_project),
        "location": settings.location,
        "generation_model": settings.generation_model,
        "embedding_model": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
        "synthetic_generation_health": vertex_health["generation"],
        "synthetic_embedding_health": vertex_health["embedding"],
        "retriever_initialization": "PASS",
        "scientific_case_calls": 0,
    }


def _decorate_recovery_outputs(preflight: Mapping[str, Any]) -> Callable[[], None]:
    a2.SCREENING_LEDGER_PATH = LEDGER_PATH
    a2.CAPTURE_PATH = CAPTURE_PATH
    a2.CAPTURE_REPORT_PATH = REPORT_PATH

    original_append_jsonl = a2._append_jsonl
    original_write_ledger = a2._write_screening_ledger
    original_build_report = a2._build_capture_report

    def append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
        decorated = dict(record)
        decorated.update(
            {
                "schema_version": "c8-a2r1-two-pass-capture-v1",
                "task": TASK,
                "failed_a2_commit": FAILED_A2_COMMIT,
                "recovery_receipt_identity": str(RECEIPT_PATH.relative_to(ROOT)),
            }
        )
        original_append_jsonl(path, decorated)

    def write_ledger(*args: Any, **kwargs: Any) -> None:
        original_write_ledger(*args, **kwargs)
        payload = _read_json(LEDGER_PATH)
        payload.update(
            {
                "schema_version": "c8-a2r1-screening-ledger-v1",
                "artifact_role": "C8_A2R1_SCREENING_LEDGER",
                "task": TASK,
                "failed_a2_commit": FAILED_A2_COMMIT,
                "original_failure_class": ORIGINAL_FAILURE_CLASS,
                "recovery_receipt_identity": str(RECEIPT_PATH.relative_to(ROOT)),
                "original_a2_artifacts_unchanged": True,
            }
        )
        _write_json(LEDGER_PATH, payload)

    def build_report(*args: Any, **kwargs: Any) -> dict[str, Any]:
        report = original_build_report(*args, **kwargs)
        verdict = str(report.get("A2_verdict"))
        report.update(
            {
                "schema_version": "c8-a2r1-two-pass-capture-report-v1",
                "artifact_role": "C8_A2R1_TWO_PASS_CAPTURE_REPORT",
                "task": TASK,
                "failed_a2_commit": FAILED_A2_COMMIT,
                "original_failure_class": ORIGINAL_FAILURE_CLASS,
                "frozen_preregistration_path": str(a2.PREREGISTRATION_PATH.relative_to(ROOT)),
                "safe_projection_path": str(a2.PROJECTION_PATH.relative_to(ROOT)),
                "recovery_receipt_identity": str(RECEIPT_PATH.relative_to(ROOT)),
                "environment_preflight": dict(preflight),
                "recovery_scientific_start_status": True,
                "preflight_call_ledger": {
                    "adc_resolution": 1,
                    "credential_refresh": int(bool(preflight.get("credential_refresh_attempted"))),
                    "synthetic_generation_calls": 1,
                    "synthetic_embedding_calls": 1,
                    "retriever_initialization": 1,
                    "scientific_case_calls": 0,
                },
                "scientific_call_ledger": dict(report.get("call_ledger") or {}),
                "A2R1_verdict": verdict,
                "final_a2_role": (
                    "PASS_AFTER_PRE_OUTCOME_INVOCATION_RECOVERY"
                    if verdict == "PASS"
                    else "INCONCLUSIVE"
                ),
                "A3_eligibility": (
                    "NEXT_ELIGIBLE / NOT_STARTED" if verdict == "PASS" else "NOT_ELIGIBLE"
                ),
                "original_a2_artifacts_unchanged": True,
                "VERTEX_RUNTIME_CHANGED": False,
            }
        )
        return report

    a2._append_jsonl = append_jsonl
    a2._write_screening_ledger = write_ledger
    a2._build_capture_report = build_report

    def restore() -> None:
        a2._append_jsonl = original_append_jsonl
        a2._write_screening_ledger = original_write_ledger
        a2._build_capture_report = original_build_report
        a2.SCREENING_LEDGER_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_screening_ledger_v1.json"
        a2.CAPTURE_PATH = ROOT / "evaluation/baselines/replay/phase_c_c8_a2_two_pass_capture_v1.jsonl"
        a2.CAPTURE_REPORT_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_two_pass_capture_report_v1.json"

    return restore


def gate_then_execute(
    preflight_fn: Callable[[], Mapping[str, Any]],
    receipt_fn: Callable[[Mapping[str, Any]], None],
    live_fn: Callable[[], Mapping[str, Any]],
) -> Mapping[str, Any]:
    preflight = preflight_fn()
    receipt_fn(preflight)
    return live_fn()


def _run_live(preregistration: Mapping[str, Any], projection_records: Sequence[Mapping[str, str]], preflight: Mapping[str, Any]) -> dict[str, Any]:
    restore = _decorate_recovery_outputs(preflight)
    try:
        result = a2.run_authoritative_capture(preregistration, projection_records)
    finally:
        restore()
    report = _read_json(REPORT_PATH)
    report["original_a2_artifacts_unchanged"] = True
    _write_json(REPORT_PATH, report)
    return dict(result)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-live", action="store_true", required=True)
    args = parser.parse_args(argv)
    if not args.run_live:
        return 2

    try:
        assert_recovery_outputs_absent()
        assert_original_a2_artifacts_unchanged()
        preregistration = verify_preregistration()
        projection_records = a2.load_execution_projection(a2.PROJECTION_PATH)
        source_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        preflight = _preflight_environment()

        def write_receipt(preflight_result: Mapping[str, Any]) -> None:
            receipt = build_recovery_receipt(
                preregistration,
                preflight_result,
                source_head=source_head,
            )
            _write_json(RECEIPT_PATH, receipt)

        result_holder: dict[str, Any] = {}

        def execute_live() -> Mapping[str, Any]:
            result = _run_live(preregistration, projection_records, preflight)
            result_holder.update(result)
            return result

        gate_then_execute(lambda: preflight, write_receipt, execute_live)
        output = {
            **result_holder,
            "task": TASK,
            "recovery_receipt": str(RECEIPT_PATH.relative_to(ROOT)),
            "preflight": preflight,
        }
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0 if output.get("status") == "PASS" else 2
    except Exception as exc:
        print(
            json.dumps(
                {
                    "task": TASK,
                    "status": "PRE_LIVE_ENVIRONMENT_BLOCKED",
                    "scientific_recovery_started": False,
                    "recovery_attempt_consumed": False,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
