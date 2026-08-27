"""Run the single C8-A2R2 applicability-extension capture."""

from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.scripts import capture_c8_a2_two_pass as a2  # noqa: E402


TASK = "C8-A2R2"
A2R2_P0_COMMIT = "15d251e482753e83b906b35c77c79866318d8aa2"
A2R2_S0_COMMIT = "dedaef5a8216201781628fbccf28e5823adab513"
A2R1_RESULT_COMMIT = "5f2b4b78e8cc98b297fcc38f2cdba8491cecf04c"
FAILED_A2_COMMIT = "07594b9b6f2857796115bc9cfe00d3426676084b"
AMENDMENT_TYPE = "PRE_TREATMENT_OUTCOME_APPLICABILITY_EXTENSION"
COHORT_LABEL = "MIXED_PROVENANCE_EXPOSED_APPLICABILITY_COHORT"

EXTENSION_PROJECTION_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c8_a2r2_execution_projection_extension_v1.json"
SPLIT_ROLE_AUDIT_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c8_a2r2_split_role_audit_v1.json"
AMENDMENT_PATH = ROOT / "evaluation/baselines/manifests/phase_c_a2r2_applicability_extension_amendment_v1.json"
LEDGER_PATH = ROOT / "evaluation/baselines/manifests/phase_c_a2r2_screening_ledger_v1.json"
CAPTURE_PATH = ROOT / "evaluation/baselines/replay/phase_c_a2r2_two_pass_capture_v1.jsonl"
REPORT_PATH = ROOT / "evaluation/baselines/manifests/phase_c_a2r2_two_pass_capture_report_v1.json"
COMBINED_MANIFEST_PATH = ROOT / "evaluation/baselines/manifests/phase_c_a2r2_combined_treatment_manifest_v1.json"

A2R1_CAPTURE_PATH = ROOT / "evaluation/baselines/replay/phase_c_a2r1_two_pass_capture_v1.jsonl"
A2R1_CAPTURE_RELATIVE = str(A2R1_CAPTURE_PATH.relative_to(ROOT)).replace("\\", "/")
FROZEN_PREREGISTRATION_PATH = ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_global_treatment_preregistration_v1.json"

ORIGINAL_24_CASE_IDS = tuple(a2.PRIMARY_CASE_IDS + a2.EXPANSION_CASE_IDS)
EXPECTED_A2R1_TARGETED_CASE_IDS = ("g007", "g025", "g041", "g057")
EXPECTED_EXTENSION_RECORD_KEYS = {"case_id", "query", "intent"}
PROTECTED_PATHS = (
    FROZEN_PREREGISTRATION_PATH,
    ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_screening_ledger_v1.json",
    ROOT / "evaluation/baselines/manifests/phase_c_c8_a2_two_pass_capture_report_v1.json",
    ROOT / "evaluation/baselines/replay/phase_c_c8_a2_two_pass_capture_v1.jsonl",
    A2R1_CAPTURE_PATH,
    ROOT / "src/panda_agent/qa.py",
    ROOT / "src/panda_agent/retrieval.py",
    ROOT / "src/panda_agent/evidence_selection.py",
    ROOT / "src/panda_agent/llm/vertex.py",
    ROOT / "configs/retrieval_policies.yaml",
)


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact must be an object: {path}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL record must be an object: {path}:{line_number}")
        rows.append(value)
    return rows


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _append_jsonl(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def _current_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def _assert_commit_exists(commit: str) -> None:
    subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )


def _protected_bytes() -> dict[Path, bytes]:
    missing = [path for path in PROTECTED_PATHS if not path.exists()]
    if missing:
        raise FileNotFoundError(f"protected artifact is missing: {missing[0]}")
    return {path: path.read_bytes() for path in PROTECTED_PATHS}


def _assert_protected_unchanged(before: Mapping[Path, bytes]) -> None:
    for path, original in before.items():
        if path.read_bytes() != original:
            raise RuntimeError(f"protected file changed: {_relative(path)}")
        result = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", _relative(path)],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"protected worktree path changed: {_relative(path)}")


def _assert_new_outputs_absent() -> None:
    paths = (
        AMENDMENT_PATH,
        LEDGER_PATH,
        CAPTURE_PATH,
        REPORT_PATH,
        COMBINED_MANIFEST_PATH,
    )
    existing = [path for path in paths if path.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite existing A2R2 artifact: {_relative(existing[0])}")


def load_extension_projection() -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Load and structurally validate only the committed safe projection."""

    payload = _read_json(EXTENSION_PROJECTION_PATH)
    if payload.get("artifact_role") != "C8_A2R2_SANITIZED_EXECUTION_PROJECTION_EXTENSION":
        raise ValueError("unexpected A2R2 extension projection artifact_role")
    split_role_audit = payload.get("split_role_audit")
    if not isinstance(split_role_audit, dict):
        raise ValueError("A2R2 extension projection lacks split-role audit metadata")
    if split_role_audit.get("commit") != A2R2_S0_COMMIT:
        raise ValueError("A2R2 extension projection split-role audit commit mismatch")
    if split_role_audit.get("population_outcome") != "DEV_ONLY_EXTENSION_SUPPORTED":
        raise ValueError("A2R2 extension projection does not have the dev-only outcome")
    source = payload.get("source")
    if not isinstance(source, dict) or source.get("authorized_split") != "dev":
        raise ValueError("A2R2 extension projection is not authorized for dev")
    if payload.get("extension_count") != 64:
        raise ValueError("A2R2 extension projection must contain 64 cases")
    if payload.get("existing_targeted_complete_count") != 4:
        raise ValueError("A2R2 extension projection must preserve four existing targeted cases")
    if payload.get("required_total_targeted_complete_count") != 6:
        raise ValueError("A2R2 extension projection must preserve the six-case minimum")
    if payload.get("additional_targeted_complete_needed") != 2:
        raise ValueError("A2R2 extension projection must require two additional cases")

    extension_case_ids = payload.get("extension_case_ids")
    raw_records = payload.get("records")
    if not isinstance(extension_case_ids, list) or len(extension_case_ids) != 64:
        raise ValueError("A2R2 extension_case_ids must contain exactly 64 records")
    if not isinstance(raw_records, list) or len(raw_records) != 64:
        raise ValueError("A2R2 extension records must contain exactly 64 records")
    if list(extension_case_ids) != [record.get("case_id") for record in raw_records if isinstance(record, dict)]:
        raise ValueError("A2R2 extension order does not match record order")
    if set(extension_case_ids) & set(ORIGINAL_24_CASE_IDS):
        raise ValueError("A2R2 extension contains a case from the immutable original 24")
    if len(set(extension_case_ids)) != 64:
        raise ValueError("A2R2 extension case IDs must be unique")

    records: list[dict[str, str]] = []
    for record in raw_records:
        if not isinstance(record, dict) or set(record) != EXPECTED_EXTENSION_RECORD_KEYS:
            raise ValueError("A2R2 extension records must have exactly case_id/query/intent keys")
        if not all(isinstance(record[key], str) and record[key] for key in EXPECTED_EXTENSION_RECORD_KEYS):
            raise ValueError("A2R2 extension records must contain non-empty strings")
        records.append({key: str(record[key]) for key in ("case_id", "query", "intent")})
    return payload, records


def load_split_role_audit(projection: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the committed split-role audit without consulting Gold."""

    audit = _read_json(SPLIT_ROLE_AUDIT_PATH)
    if audit.get("artifact_role") != "C8_A2R2_SPLIT_ROLE_AUDIT":
        raise ValueError("unexpected A2R2 split-role audit artifact_role")
    if audit.get("future_extension_population_outcome") != "DEV_ONLY_EXTENSION_SUPPORTED":
        raise ValueError("split-role audit does not authorize the dev-only extension")
    if audit.get("allowed_extension_splits") != ["dev"]:
        raise ValueError("split-role audit allowed extension split mismatch")
    if audit.get("TARGETED_CHARACTERISTICS_USED_FOR_POPULATION_SELECTION") is not False:
        raise ValueError("split-role audit indicates targeted characteristics were used")
    if audit.get("scientific_rules_changed") is not False:
        raise ValueError("split-role audit indicates scientific rules changed")
    if audit.get("prior_screened_case_count") != 24 or audit.get("targeted_case_count") != 4:
        raise ValueError("split-role audit prior counts mismatch")
    if audit.get("gold_relevance_exposure") is not False:
        raise ValueError("split-role audit indicates relevance exposure")
    dev_inventory = audit.get("dev_inventory")
    if not isinstance(dev_inventory, dict):
        raise ValueError("split-role audit lacks dev inventory")
    if list(dev_inventory.get("remaining_case_ids") or []) != list(projection.get("extension_case_ids") or []):
        raise ValueError("split-role audit remaining dev order disagrees with safe projection")
    checks = audit.get("audit_checks") or {}
    required_checks = (
        "prior_ids_unique",
        "targeted_subset_of_prior",
        "prior_counts_sum_to_24",
        "targeted_counts_sum_to_4",
        "dev_partition_complete",
        "dev_partition_intersection_empty",
        "relevance_bearing_gold_serialized",
    )
    for key in required_checks:
        expected = False if key == "relevance_bearing_gold_serialized" else True
        if checks.get(key) is not expected:
            raise ValueError(f"split-role audit check failed: {key}")
    return audit


def load_existing_a2r1_records() -> list[dict[str, Any]]:
    """Load the four immutable A2R1 records read-only."""

    records = _read_jsonl(A2R1_CAPTURE_PATH)
    if tuple(record.get("case_id") for record in records) != EXPECTED_A2R1_TARGETED_CASE_IDS:
        raise ValueError("A2R1 capture case IDs are not the frozen four-case order")
    for record in records:
        if record.get("capture_status") != "PASS":
            raise ValueError("A2R1 capture contains a non-PASS treatment record")
        if record.get("INITIAL", {}).get("PassSnapshot", {}).get("completeness") != "COMPLETE":
            raise ValueError("A2R1 INITIAL capture is not COMPLETE")
        if record.get("TARGETED", {}).get("PassSnapshot", {}).get("completeness") != "COMPLETE":
            raise ValueError("A2R1 TARGETED capture is not COMPLETE")
        if record.get("S0_replay_parity", {}).get("parity") is not True:
            raise ValueError("A2R1 S0 replay parity is not true")
    return records


def verify_frozen_preregistration() -> dict[str, Any]:
    preregistration = a2.load_frozen_preregistration(FROZEN_PREREGISTRATION_PATH)
    scientific = preregistration["scientific_fields"]
    mirrors = {
        "cohort": "cohort_order",
        "s0": "s0",
        "g1": "g1",
        "primary_metrics": "primary_metrics",
        "hard_gates": "hard_gates",
        "meaningful_gain_rule": "meaningful_gain_rule",
    }
    for mirror, scientific_key in mirrors.items():
        if preregistration.get(mirror) != scientific.get(scientific_key):
            raise ValueError(f"frozen preregistration mirror mismatch: {mirror}")
    if scientific["cohort_order"]["minimum_targeted_treatment_cases"] != 6:
        raise ValueError("frozen minimum targeted treatment count is not six")
    if scientific["s0"]["identity"] != a2.S0_IDENTITY:
        raise ValueError("frozen S0 identity mismatch")
    if scientific["g1"]["identity"] != a2.TREATMENT_ID:
        raise ValueError("frozen G1 identity mismatch")
    return preregistration


def build_amendment(
    projection: Mapping[str, Any],
    audit: Mapping[str, Any],
    *,
    source_head: str,
) -> dict[str, Any]:
    return {
        "schema_version": "c8-a2r2-applicability-extension-amendment-v1",
        "artifact_role": "C8_A2R2_PRE_TREATMENT_OUTCOME_APPLICABILITY_EXTENSION_AMENDMENT",
        "task": TASK,
        "amendment_type": AMENDMENT_TYPE,
        "a2r2_p0_commit": A2R2_P0_COMMIT,
        "a2r2_s0_audit_commit": A2R2_S0_COMMIT,
        "a2r1_result_commit": A2R1_RESULT_COMMIT,
        "failed_a2_commit": FAILED_A2_COMMIT,
        "source_head_at_amendment": source_head,
        "original_frozen_preregistration": _relative(FROZEN_PREREGISTRATION_PATH),
        "safe_extension_projection": _relative(EXTENSION_PROJECTION_PATH),
        "split_role_audit": _relative(SPLIT_ROLE_AUDIT_PATH),
        "written_before_live_start": True,
        "scientific_fields": {
            "amendment_type": AMENDMENT_TYPE,
            "original_screened_count": 24,
            "original_complete_targeted_count": 4,
            "required_total_complete_targeted_count": 6,
            "additional_complete_targeted_needed": 2,
            "extension_population": "exact committed remaining-dev safe projection",
            "extension_population_source": _relative(EXTENSION_PROJECTION_PATH),
            "extension_population_split": "dev",
            "extension_population_size": 64,
            "extension_order": "exact committed projection order",
            "maximum_extension_cases_screened": 64,
            "maximum_total_historical_screening_exposure": 88,
            "stop_rule": "stop immediately once 2 NEW COMPLETE targeted cases are obtained",
            "original_24_cases_rerun": False,
            "acceptance_split_used_for_extension": False,
            "treatment_semantics_changed": False,
            "g1_s0_metrics_gates_changed": False,
            "s0_identity": a2.S0_IDENTITY,
            "g1_identity": a2.TREATMENT_ID,
            "targeted_characteristics_used_for_extension_selection": False,
            "treatment_outcome_observed_before_amendment": False,
        },
        "rationale": [
            "The original 24-case cohort yielded only 4 genuine targeted cases.",
            "The minimum treatment count of 6 remains unchanged.",
            "The extension source population was determined independently by the completed split-role audit.",
            "The extension uses only remaining development-visible dev cases.",
            "Existing targeted-case characteristics were not used to select or order extension cases.",
            "No G1 treatment result had been observed when the amendment was defined.",
        ],
        "pre_treatment_outcome_boundary": {
            "decision_timing": "AFTER_APPLICABILITY_FREQUENCY_OBSERVATION_BEFORE_TREATMENT_EFFECT_OBSERVATION",
            "REAL_G1_EXECUTIONS": 0,
            "REAL_GLOBAL_RERANKER_CALLS": 0,
            "GOLD_EVALUATIONS": 0,
            "A3_TREATMENT_COMPARISON": 0,
        },
        "source_projection_summary": {
            "artifact_role": projection["artifact_role"],
            "extension_count": projection["extension_count"],
            "first_case_id": projection["extension_case_ids"][0],
            "last_case_id": projection["extension_case_ids"][-1],
            "split_role_population_outcome": audit["future_extension_population_outcome"],
        },
    }


def preflight_environment() -> dict[str, Any]:
    """Perform only synthetic Vertex and object-initialization checks."""

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

    vertex = a2.VertexAIClient(settings)
    generation = vertex.generation_health_check()
    if generation.get("status") != "ok":
        raise RuntimeError("synthetic generation health check returned an unexpected status")
    embedding = vertex.embed_query("C8 A2R2 environment preflight")
    if len(embedding) != settings.embedding_dimensions:
        raise RuntimeError(
            f"synthetic embedding dimension mismatch: {len(embedding)} != {settings.embedding_dimensions}"
        )
    retriever = a2.CapturingRetriever(ROOT, vertex)
    a2.QAAgent(ROOT, retriever=retriever, vertex=retriever.vertex)
    return {
        "adc_resolution": "PASS",
        "credential_refresh_attempted": refresh_attempted,
        "credentials_valid_after_refresh": True,
        "project_resolved_by_google_auth": bool(detected_project),
        "location": settings.location,
        "generation_model": settings.generation_model,
        "embedding_model": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
        "generation_health": "PASS",
        "embedding_health": "PASS",
        "synthetic_generation_calls": 1,
        "synthetic_embedding_calls": 1,
        "retriever_initialization": "PASS",
        "scientific_case_calls": 0,
        "preflight_call_ledger": {
            "adc_resolution": 1,
            "credential_refresh": int(refresh_attempted),
            "synthetic_generation_calls": 1,
            "synthetic_embedding_calls": 1,
            "retriever_initialization": 1,
            "scientific_case_calls": 0,
        },
        "synthetic_generation_request_model": generation.get("generation_model"),
        "synthetic_generation_request_location": generation.get("location"),
    }


def gate_then_execute(
    preflight_fn: Callable[[], Mapping[str, Any]],
    amendment_fn: Callable[[Mapping[str, Any]], None],
    live_fn: Callable[[], Mapping[str, Any]],
) -> Mapping[str, Any]:
    preflight = preflight_fn()
    amendment_fn(preflight)
    return live_fn()


def _decorate_capture_record(
    record: Mapping[str, Any],
    row: Mapping[str, str],
    *,
    extension_position: int,
) -> dict[str, Any]:
    decorated = deepcopy(dict(record))
    decorated.update(
        {
            "schema_version": "c8-a2r2-two-pass-capture-v1",
            "task": TASK,
            "amendment_identity": _relative(AMENDMENT_PATH),
            "safe_extension_projection_identity": _relative(EXTENSION_PROJECTION_PATH),
            "split_provenance": "dev",
            "provenance_stage": "A2R2",
            "extension_position": extension_position,
            "a2r1_result_commit": A2R1_RESULT_COMMIT,
        }
    )
    identity = dict(decorated.get("execution_identity") or {})
    identity.update(
        {
            "task": TASK,
            "amendment_identity": _relative(AMENDMENT_PATH),
            "safe_extension_projection_identity": _relative(EXTENSION_PROJECTION_PATH),
            "treatment_preregistration_identity": a2.TREATMENT_ID,
            "a2r1_result_commit": A2R1_RESULT_COMMIT,
            "extension_position": extension_position,
            "extension_split": "dev",
        }
    )
    decorated["execution_identity"] = identity
    if decorated.get("case_id") != row.get("case_id"):
        raise RuntimeError("capture case ID disagrees with extension projection")
    return decorated


def _failure_screening_row(
    retriever: a2.CapturingRetriever,
    row: Mapping[str, str],
    *,
    extension_position: int,
    error: Exception,
) -> dict[str, Any]:
    passes = retriever.case_passes()
    counts = {
        key: sum(int((item.get("call_ledger") or {}).get(key, 0)) for item in passes)
        for key in a2.CALL_COUNTER_KEYS
    }
    return {
        "extension_position": extension_position,
        "case_id": str(row["case_id"]),
        "initial_execution_completed": any(
            item.get("pass_origin") == "INITIAL" and "result" in item for item in passes
        ),
        "targeted_triggered": any(item.get("pass_origin") == "TARGETED" for item in passes),
        "targeted_execution_completed": any(
            item.get("pass_origin") == "TARGETED" and "result" in item for item in passes
        ),
        "complete_snapshot_valid": False,
        "new_treatment_case_included": False,
        "stop_condition_reached": False,
        "infrastructure_error": f"{type(error).__name__}: {error}",
        "measured_call_counts": counts,
        "single_attempt": True,
    }


def _successful_screening_row(
    screening: Mapping[str, Any],
    row: Mapping[str, str],
    *,
    extension_position: int,
    included: bool,
    stop_condition_reached: bool,
) -> dict[str, Any]:
    return {
        "extension_position": extension_position,
        "case_id": str(row["case_id"]),
        "initial_execution_completed": bool(screening.get("initial_execution_completed")),
        "targeted_triggered": bool(screening.get("targeted_triggered")),
        "targeted_execution_completed": bool(screening.get("targeted_execution_completed")),
        "complete_snapshot_valid": screening.get("complete_snapshot_valid"),
        "new_treatment_case_included": included,
        "stop_condition_reached": stop_condition_reached,
        "infrastructure_error": screening.get("infrastructure_error"),
        "measured_call_counts": dict(screening.get("measured_call_counts") or {}),
        "single_attempt": True,
    }


def _verdict_reason(verdict: str, stop_reason: str | None) -> str | None:
    if verdict == "PASS":
        return None
    if stop_reason == "EXTENSION_EXHAUSTED_BEFORE_SECOND_NEW_COMPLETE_TARGETED_CASE":
        return "TARGETED_APPLICABILITY_TOO_SPARSE_AFTER_DEV_EXTENSION"
    if stop_reason == "MATERIAL_INFRASTRUCTURE_OR_CAPTURE_FAILURE":
        return "MATERIAL_INFRASTRUCTURE_OR_CAPTURE_FAILURE"
    return "A2R2_VALIDATION_FAILURE"


def _write_screening_ledger(
    ledger_rows: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
    *,
    stop_reason: str | None,
    verdict: str,
    infrastructure_failures: Sequence[Mapping[str, Any]],
) -> None:
    targeted_count = sum(int(bool(row.get("targeted_triggered"))) for row in ledger_rows)
    new_ids = [str(record["case_id"]) for record in records]
    payload = {
        "schema_version": "c8-a2r2-screening-ledger-v1",
        "artifact_role": "C8_A2R2_SCREENING_LEDGER",
        "task": TASK,
        "amendment_identity": _relative(AMENDMENT_PATH),
        "safe_extension_projection_identity": _relative(EXTENSION_PROJECTION_PATH),
        "split_role_audit_identity": _relative(SPLIT_ROLE_AUDIT_PATH),
        "a2r1_capture_identity": A2R1_CAPTURE_RELATIVE,
        "existing_complete_targeted_count": 4,
        "required_total_complete_targeted_count": 6,
        "extension_population": "remaining dev",
        "extension_population_size": 64,
        "maximum_extension_cases_screened": 64,
        "screened_count": len(ledger_rows),
        "targeted_trigger_count": targeted_count,
        "new_targeted_trigger_count": targeted_count,
        "new_complete_targeted_count": len(new_ids),
        "new_treatment_case_ids": new_ids,
        "combined_complete_targeted_count": 4 + len(new_ids),
        "stop_condition_reached": any(bool(row.get("stop_condition_reached")) for row in ledger_rows),
        "stop_reason": stop_reason,
        "verdict_reason": _verdict_reason(verdict, stop_reason),
        "remaining_projection_count_after_stop": max(0, 64 - len(ledger_rows)),
        "unexecuted_extension_tail_count": max(0, 64 - len(ledger_rows)),
        "retries": 0,
        "replacements": 0,
        "recaptures": 0,
        "original_24_rerun_count": 0,
        "extension_order_unchanged": [row.get("case_id") for row in ledger_rows]
        == list(_read_json(EXTENSION_PROJECTION_PATH).get("extension_case_ids", []))[: len(ledger_rows)],
        "infrastructure_failures": list(infrastructure_failures),
        "verdict": verdict,
        "call_ledger": a2._aggregate_counts((), ledger_rows),
        "records": [dict(row) for row in ledger_rows],
    }
    _write_json(LEDGER_PATH, payload)


def _capture_fidelity(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = {
        "INITIAL": {"COMPLETE": 0, "contract": 0, "stage_f": 0, "stage_p": 0, "stage_s": 0},
        "TARGETED": {"COMPLETE": 0, "contract": 0, "stage_f": 0, "stage_p": 0, "stage_s": 0},
    }
    both_consistent = 0
    s0_parity = 0
    mismatches: list[str] = []
    contract_ids: list[str] = []
    for record in records:
        case_id = str(record["case_id"])
        if record.get("capture_status") != "PASS":
            continue
        pool = record.get("validated_global_candidate_pool") or {}
        contract_ids.append(str(pool.get("contract_id")))
        for pass_name in ("INITIAL", "TARGETED"):
            current = record[pass_name]
            snapshot = current["PassSnapshot"]
            counts[pass_name]["COMPLETE"] += int(snapshot.get("completeness") == "COMPLETE")
            parity = current.get("capture_auxiliary", {}).get("parity") or {}
            counts[pass_name]["stage_f"] += int(bool(parity.get("stage_f")))
            counts[pass_name]["stage_p"] += int(bool(parity.get("stage_p")))
            counts[pass_name]["stage_s"] += int(bool(parity.get("stage_s")))
            counts[pass_name]["contract"] += int(
                snapshot.get("pass_origin") in {"INITIAL", "TARGETED"}
                and isinstance(snapshot.get("stage_f_order"), list)
                and isinstance(snapshot.get("stage_p_order"), list)
                and isinstance(snapshot.get("stage_s_selected_object_ids"), list)
            )
        both_consistent += int(
            (record.get("BOTH_origin_payload_consistency") or {}).get("consistent") is True
        )
        parity = (record.get("S0_replay_parity") or {}).get("parity") is True
        s0_parity += int(parity)
        if not parity:
            mismatches.append(case_id)
    total = len(records)
    return {
        "INITIAL": counts["INITIAL"],
        "TARGETED": counts["TARGETED"],
        "BOTH_origin_consistency": f"{both_consistent}/{total}",
        "S0_replay_parity": {
            "identity": a2.S0_IDENTITY,
            "count": s0_parity,
            "total": total,
            "rate": s0_parity / total if total else 0.0,
            "mismatch_case_ids": mismatches,
        },
        "contract_validation": {
            "identity": a2.CONTRACT_ID,
            "count": sum(int(value == a2.CONTRACT_ID) for value in contract_ids),
            "total": total,
        },
    }


def build_combined_manifest(
    existing_records: Sequence[Mapping[str, Any]],
    new_records: Sequence[Mapping[str, Any]],
    split_map: Mapping[str, str],
) -> dict[str, Any]:
    if len(existing_records) != 4 or len(new_records) != 2:
        raise ValueError("combined manifest requires exactly four existing and two new records")
    combined: list[dict[str, Any]] = []
    for index, record in enumerate(existing_records, 1):
        case_id = str(record["case_id"])
        combined.append(
            {
                "case_id": case_id,
                "source_capture_path": A2R1_CAPTURE_RELATIVE,
                "source_record_index": index,
                "provenance_stage": "A2R1",
                "split_provenance": split_map[case_id],
                "completeness": "COMPLETE",
                "S0_replay_parity": True,
            }
        )
    for index, record in enumerate(new_records, 1):
        case_id = str(record["case_id"])
        combined.append(
            {
                "case_id": case_id,
                "source_capture_path": _relative(CAPTURE_PATH),
                "source_record_index": index,
                "provenance_stage": "A2R2",
                "split_provenance": split_map[case_id],
                "completeness": "COMPLETE",
                "S0_replay_parity": True,
            }
        )
    case_ids = [item["case_id"] for item in combined]
    if len(case_ids) != 6 or len(set(case_ids)) != 6:
        raise ValueError("combined treatment case IDs are not six unique cases")
    return {
        "schema_version": "c8-a2r2-combined-treatment-manifest-v1",
        "artifact_role": "C8_A2R2_COMBINED_TREATMENT_MANIFEST",
        "task": TASK,
        "amendment_identity": _relative(AMENDMENT_PATH),
        "original_frozen_preregistration": _relative(FROZEN_PREREGISTRATION_PATH),
        "cohort_label": COHORT_LABEL,
        "treatment_semantics_changed": False,
        "combined_order": "existing A2R1 frozen order followed by A2R2 screening order",
        "total": 6,
        "existing": 4,
        "new": 2,
        "unique": True,
        "records": combined,
        "all_complete": True,
        "all_s0_replay_parity": True,
        "REAL_G1_EXECUTIONS": 0,
        "REAL_GLOBAL_RERANKER_CALLS": 0,
        "GOLD_EVALUATIONS": 0,
        "NOVEL_EVALUATIONS": 0,
        "DB_INDEX_WRITES": 0,
    }


def _build_report(
    *,
    amendment: Mapping[str, Any],
    projection: Mapping[str, Any],
    audit: Mapping[str, Any],
    existing_records: Sequence[Mapping[str, Any]],
    new_records: Sequence[Mapping[str, Any]],
    ledger_rows: Sequence[Mapping[str, Any]],
    preflight: Mapping[str, Any],
    scientific_fields_changed: bool,
    preregistration_unchanged: bool,
    amendment_scientific_fields_changed: bool,
    protected_unchanged: bool,
    projection_unchanged: bool,
    audit_unchanged: bool,
    original_a2r1_unchanged: bool,
    stop_reason: str,
    infrastructure_failures: Sequence[Mapping[str, Any]],
    verdict: str,
) -> dict[str, Any]:
    fidelity = _capture_fidelity(new_records)
    new_ids = [str(record["case_id"]) for record in new_records]
    combined_ids = [str(record["case_id"]) for record in existing_records] + new_ids
    scientific_ledger = a2._aggregate_counts(new_records, ledger_rows)
    return {
        "schema_version": "c8-a2r2-two-pass-capture-report-v1",
        "artifact_role": "C8_A2R2_TWO_PASS_CAPTURE_REPORT",
        "task": TASK,
        "amendment_identity": _relative(AMENDMENT_PATH),
        "amendment_type": AMENDMENT_TYPE,
        "safe_extension_projection_identity": {
            "path": _relative(EXTENSION_PROJECTION_PATH),
            "commit": A2R2_P0_COMMIT,
            "artifact_role": projection["artifact_role"],
            "extension_count": projection["extension_count"],
        },
        "split_role_audit_identity": {
            "path": _relative(SPLIT_ROLE_AUDIT_PATH),
            "commit": A2R2_S0_COMMIT,
            "population_outcome": audit["future_extension_population_outcome"],
        },
        "a2r1_capture_identity": {
            "path": A2R1_CAPTURE_RELATIVE,
            "commit": A2R1_RESULT_COMMIT,
            "existing_complete_targeted_count": len(existing_records),
        },
        "historical_existing_complete_targeted_count": 4,
        "extension_screened_count": len(ledger_rows),
        "new_targeted_trigger_count": sum(int(bool(row.get("targeted_triggered"))) for row in ledger_rows),
        "new_complete_targeted_count": len(new_records),
        "new_treatment_case_ids": new_ids,
        "combined_complete_targeted_count": 4 + len(new_records),
        "combined_treatment_case_ids": combined_ids,
        "stop_reason": stop_reason,
        "unexecuted_extension_tail_count": max(0, 64 - len(ledger_rows)),
        "retries": 0,
        "replacements": 0,
        "recaptures": 0,
        "original_24_rerun_count": 0,
        "extension_order_unchanged": [row.get("case_id") for row in ledger_rows]
        == list(projection.get("extension_case_ids") or [])[: len(ledger_rows)],
        "capture_fidelity": fidelity,
        "preflight": dict(preflight),
        "preflight_call_ledger": dict(preflight.get("preflight_call_ledger") or {}),
        "scientific_call_ledger": scientific_ledger,
        "GOLD_FILE_ACCESSED": False,
        "GOLD_RELEVANCE_LABELS_ACCESSED": False,
        "GOLD_EVIDENCE_GROUPS_ACCESSED": False,
        "GOLD_ANSWER_RUBRICS_ACCESSED": False,
        "GOLD_EVALUATIONS": 0,
        "NOVEL_EVALUATIONS": 0,
        "REAL_G1_EXECUTIONS": 0,
        "REAL_GLOBAL_RERANKER_CALLS": 0,
        "QA_GENERATION_CALLS": 0,
        "VERIFIER_CALLS": 0,
        "JUDGE_CALLS": 0,
        "DB_INDEX_WRITES": 0,
        "G1_IDENTITY": a2.TREATMENT_ID,
        "G1_CHANGED": False,
        "original_preregistration_unchanged": preregistration_unchanged,
        "amendment_scientific_fields_changed_after_live_start": amendment_scientific_fields_changed,
        "amendment_written_before_live_start": amendment.get("written_before_live_start") is True,
        "safe_projection_unchanged": projection_unchanged,
        "split_role_audit_unchanged": audit_unchanged,
        "original_a2r1_capture_unchanged": original_a2r1_unchanged,
        "protected_paths_unchanged": protected_unchanged,
        "PRODUCTION_BEHAVIOR_CHANGED": False,
        "QA_RUNTIME_CHANGED": False,
        "RETRIEVER_RUNTIME_CHANGED": False,
        "VERTEX_RUNTIME_CHANGED": False,
        "CONFIG_CHANGED": False,
        "PRODUCTION_FUSION_CHANGED": False,
        "PRODUCTION_SELECTOR_CHANGED": False,
        "infrastructure_failures": list(infrastructure_failures),
        "A2R2_verdict": verdict,
        "A2R2_verdict_reason": _verdict_reason(verdict, stop_reason),
        "final_a2_role": (
            "PASS_AFTER_TRANSPARENT_PRE_TREATMENT_OUTCOME_APPLICABILITY_EXTENSION"
            if verdict == "PASS"
            else "INCONCLUSIVE"
        ),
        "A3_eligibility": "NEXT_ELIGIBLE / NOT_STARTED" if verdict == "PASS" else "NOT_ELIGIBLE",
        "cohort_label": COHORT_LABEL if verdict == "PASS" else None,
    }


def run_extension(
    preregistration: Mapping[str, Any],
    projection_payload: Mapping[str, Any],
    projection_records: Sequence[Mapping[str, str]],
    audit: Mapping[str, Any],
    existing_records: Sequence[Mapping[str, Any]],
    amendment: Mapping[str, Any],
    preflight: Mapping[str, Any],
    *,
    protected_before: Mapping[Path, bytes],
    preregistration_before: Mapping[str, Any],
    projection_before: Mapping[str, Any],
    audit_before: Mapping[str, Any],
    a2r1_capture_before: bytes,
) -> dict[str, Any]:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    delegate_vertex = a2.VertexAIClient(a2.VertexSettings.from_env())
    retriever = a2.CapturingRetriever(ROOT, delegate_vertex)
    agent = a2.QAAgent(ROOT, retriever=retriever, vertex=retriever.vertex)
    CAPTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CAPTURE_PATH.write_text("", encoding="utf-8")

    ledger_rows: list[dict[str, Any]] = []
    new_records: list[dict[str, Any]] = []
    infrastructure_failures: list[dict[str, Any]] = []
    stop_reason: str | None = None

    for extension_position, row in enumerate(projection_records, 1):
        try:
            screening, record = a2.execute_case(agent, retriever, row)
        except Exception as exc:
            failure = _failure_screening_row(
                retriever,
                row,
                extension_position=extension_position,
                error=exc,
            )
            ledger_rows.append(failure)
            infrastructure_failures.append(
                {
                    "extension_position": extension_position,
                    "case_id": row["case_id"],
                    "error": failure["infrastructure_error"],
                }
            )
            stop_reason = "MATERIAL_INFRASTRUCTURE_OR_CAPTURE_FAILURE"
            _write_screening_ledger(
                ledger_rows,
                new_records,
                stop_reason=stop_reason,
                verdict="INCONCLUSIVE",
                infrastructure_failures=infrastructure_failures,
            )
            break

        if record is not None:
            decorated = _decorate_capture_record(
                record,
                row,
                extension_position=extension_position,
            )
            new_records.append(decorated)
            included = True
        else:
            included = False
        stop_now = len(new_records) == 2
        ledger_rows.append(
            _successful_screening_row(
                screening,
                row,
                extension_position=extension_position,
                included=included,
                stop_condition_reached=stop_now,
            )
        )
        if record is not None:
            _append_jsonl(CAPTURE_PATH, new_records[-1])
        if stop_now:
            stop_reason = "SECOND_NEW_COMPLETE_TARGETED_CASE"
            _write_screening_ledger(
                ledger_rows,
                new_records,
                stop_reason=stop_reason,
                verdict="IN_PROGRESS",
                infrastructure_failures=infrastructure_failures,
            )
            break
        _write_screening_ledger(
            ledger_rows,
            new_records,
            stop_reason=None,
            verdict="IN_PROGRESS",
            infrastructure_failures=infrastructure_failures,
        )
    else:
        stop_reason = "EXTENSION_EXHAUSTED_BEFORE_SECOND_NEW_COMPLETE_TARGETED_CASE"

    if stop_reason is None:
        stop_reason = "EXTENSION_EXHAUSTED_BEFORE_SECOND_NEW_COMPLETE_TARGETED_CASE"

    projection_after = _read_json(EXTENSION_PROJECTION_PATH)
    audit_after = _read_json(SPLIT_ROLE_AUDIT_PATH)
    preregistration_after = _read_json(FROZEN_PREREGISTRATION_PATH)
    amendment_after = _read_json(AMENDMENT_PATH)
    projection_unchanged = projection_after == projection_before
    audit_unchanged = audit_after == audit_before
    scientific_fields_changed = (
        preregistration_after.get("scientific_fields") != preregistration_before.get("scientific_fields")
        or preregistration.get("scientific_fields") != preregistration_before.get("scientific_fields")
    )
    preregistration_unchanged = preregistration_after == preregistration_before
    amendment_scientific_fields_changed = (
        amendment_after.get("scientific_fields") != amendment.get("scientific_fields")
        or amendment_after.get("rationale") != amendment.get("rationale")
    )
    original_a2r1_unchanged = A2R1_CAPTURE_PATH.read_bytes() == a2r1_capture_before
    protected_unchanged = False
    try:
        _assert_protected_unchanged(protected_before)
        protected_unchanged = True
    except (FileNotFoundError, RuntimeError):
        protected_unchanged = False

    fidelity = _capture_fidelity(new_records)
    all_fidelity = (
        len(new_records) == 2
        and fidelity["INITIAL"]["COMPLETE"] == 2
        and fidelity["TARGETED"]["COMPLETE"] == 2
        and fidelity["INITIAL"]["contract"] == 2
        and fidelity["TARGETED"]["contract"] == 2
        and fidelity["BOTH_origin_consistency"] == "2/2"
        and fidelity["S0_replay_parity"]["count"] == 2
        and not fidelity["S0_replay_parity"]["mismatch_case_ids"]
        and fidelity["contract_validation"]["count"] == 2
    )
    exact_stop = stop_reason == "SECOND_NEW_COMPLETE_TARGETED_CASE" and len(ledger_rows) <= 64
    original_ids_rerun = set(row["case_id"] for row in ledger_rows) & set(ORIGINAL_24_CASE_IDS)
    order_unchanged = [row["case_id"] for row in ledger_rows] == list(projection_before["extension_case_ids"])[: len(ledger_rows)]
    scientific_ledger = a2._aggregate_counts(new_records, ledger_rows)
    no_forbidden_calls = all(
        scientific_ledger.get(key, 0) == 0
        for key in (
            "qa_generation_calls",
            "verifier_calls",
            "judge_calls",
            "db_index_writes",
            "REAL_G1_EXECUTIONS",
            "REAL_GLOBAL_RERANKER_CALLS",
            "QA_GENERATION_CALLS",
            "VERIFIER_CALLS",
            "JUDGE_CALLS",
            "DB_INDEX_WRITES",
        )
    )
    verdict = "PASS" if (
        not infrastructure_failures
        and len(new_records) == 2
        and exact_stop
        and all_fidelity
        and projection_unchanged
        and audit_unchanged
        and preregistration_unchanged
        and not scientific_fields_changed
        and not amendment_scientific_fields_changed
        and original_a2r1_unchanged
        and protected_unchanged
        and not original_ids_rerun
        and order_unchanged
        and no_forbidden_calls
    ) else "INCONCLUSIVE"

    split_map = {
        str(item["case_id"]): str(item["split"])
        for item in (audit.get("targeted_cases") or [])
        if isinstance(item, dict) and "case_id" in item and "split" in item
    }
    for record in new_records:
        split_map[str(record["case_id"])] = "dev"

    if verdict == "PASS":
        combined_manifest = build_combined_manifest(existing_records, new_records, split_map)
        _write_json(COMBINED_MANIFEST_PATH, combined_manifest)

    _write_screening_ledger(
        ledger_rows,
        new_records,
        stop_reason=stop_reason,
        verdict=verdict,
        infrastructure_failures=infrastructure_failures,
    )
    report = _build_report(
        amendment=amendment_after,
        projection=projection_after,
        audit=audit_after,
        existing_records=existing_records,
        new_records=new_records,
        ledger_rows=ledger_rows,
        preflight=preflight,
        scientific_fields_changed=scientific_fields_changed,
        preregistration_unchanged=preregistration_unchanged,
        amendment_scientific_fields_changed=amendment_scientific_fields_changed,
        protected_unchanged=protected_unchanged,
        projection_unchanged=projection_unchanged,
        audit_unchanged=audit_unchanged,
        original_a2r1_unchanged=original_a2r1_unchanged,
        stop_reason=stop_reason,
        infrastructure_failures=infrastructure_failures,
        verdict=verdict,
    )
    report.update(
        {
            "scientific_execution_started": True,
            "scientific_attempt_consumed": True,
            "new_capture_jsonl_record_count": len(_read_jsonl(CAPTURE_PATH)) if CAPTURE_PATH.exists() else 0,
            "combined_manifest_path": _relative(COMBINED_MANIFEST_PATH) if verdict == "PASS" else None,
            "amendment_scientific_fields_frozen_before_live": True,
            "original_24_case_ids_rerun": sorted(original_ids_rerun),
            "A2R1_existing_s0_replay_parity": "4/4",
            "current_head_after_live": _current_head(),
        }
    )
    _write_json(REPORT_PATH, report)
    return {
        "task": TASK,
        "status": verdict,
        "screened_count": len(ledger_rows),
        "new_targeted_trigger_count": sum(int(bool(row.get("targeted_triggered"))) for row in ledger_rows),
        "new_complete_targeted_count": len(new_records),
        "new_treatment_case_ids": [str(record["case_id"]) for record in new_records],
        "stop_reason": stop_reason,
        "unexecuted_extension_tail_count": max(0, 64 - len(ledger_rows)),
        "capture_report": _relative(REPORT_PATH),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-live", action="store_true", required=True)
    args = parser.parse_args(argv)
    if not args.run_live:
        return 2

    try:
        _assert_commit_exists(A2R2_P0_COMMIT)
        _assert_commit_exists(A2R2_S0_COMMIT)
        _assert_commit_exists(A2R1_RESULT_COMMIT)
        _assert_commit_exists(FAILED_A2_COMMIT)
        _assert_new_outputs_absent()
        protected_before = _protected_bytes()
        preregistration_before = _read_json(FROZEN_PREREGISTRATION_PATH)
        projection_before, projection_records = load_extension_projection()
        audit_before = load_split_role_audit(projection_before)
        existing_records = load_existing_a2r1_records()
        preregistration = verify_frozen_preregistration()
        source_head = _current_head()
        preflight = preflight_environment()
        amendment = build_amendment(projection_before, audit_before, source_head=source_head)
        a2r1_capture_before = A2R1_CAPTURE_PATH.read_bytes()

        def write_amendment(_: Mapping[str, Any]) -> None:
            _write_json(AMENDMENT_PATH, amendment)

        result = gate_then_execute(
            lambda: preflight,
            write_amendment,
            lambda: run_extension(
                preregistration,
                projection_before,
                projection_records,
                audit_before,
                existing_records,
                amendment,
                preflight,
                protected_before=protected_before,
                preregistration_before=preregistration_before,
                projection_before=projection_before,
                audit_before=audit_before,
                a2r1_capture_before=a2r1_capture_before,
            ),
        )
        print(json.dumps({**result, "preflight": preflight}, ensure_ascii=False, sort_keys=True))
        return 0 if result.get("status") == "PASS" else 2
    except Exception as exc:
        print(
            json.dumps(
                {
                    "task": TASK,
                    "status": "PRE_LIVE_ENVIRONMENT_BLOCKED",
                    "scientific_execution_started": False,
                    "scientific_attempt_consumed": False,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
