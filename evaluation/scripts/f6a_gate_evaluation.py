"""F6-A gate evaluation (evaluation-only, deterministic, zero model calls).

Aggregates the frozen formal-Gold run records through the canonical evaluator
aggregation (`evaluation.aggregate_metrics`) and derives the preregistered
F6-A gate matrix from its output. The release score remains the only
F6-A-specific arithmetic.

R1-R1 semantics: missing mandatory measurements can never silently PASS —
zero-count gates and per-intent gates distinguish PASS / FAIL / INCOMPLETE
(passed=null), every represented intent stays visible, and the global
intent-accuracy denominator is the intent-accuracy case count (sum of
represented per-intent cases), not another metric's denominator.

R1-R1-R1 semantics: per-intent intent-accuracy details emit a
measurement-derived ``applicable_denominator`` (canonical ``aggregate_metrics``
exposes per-intent denominators for recall metrics only). With
``--source-matrix`` the successor matrix additionally verifies that every
other gate datum matches the prior matrix exactly and refuses to write on any
divergence, so a NO_CHANGE verdict is checked, not assumed.

Usage:
  PYTHONPATH=src python evaluation/scripts/f6a_gate_evaluation.py \
      --run-id f6a-rc1-gold-formal-full-20260913 \
      --prereg evaluation/f6_a_prerelease_validation_preregistration.json \
      --source-matrix evaluation/f6a_gold_gate_matrix_r1_r1.json \
      --output evaluation/f6a_gold_gate_matrix_r1_r1_r1.json
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

from panda_agent.evaluation import aggregate_metrics
from panda_agent.evaluation_finalization import (
    _result_content_hash,
    evaluate_cohort_decision,
    resolve_candidate_binding,
    resolve_expected_case_ids,
)
from panda_agent.evaluation_runner import f6a_release_score, load_run_records


def dual_source_applicable_ids(records: list[dict]) -> list[str]:
    """Canonical dual-source applicability: expected answered + applicable +
    required source types contain both paper and code."""
    return sorted(
        str(record["id"])
        for record in records
        if record.get("expected_status") == "answered"
        and (record.get("metrics") or {}).get("metric_applicability", {}).get(
            "paper_code_dual_source", True
        )
        and {"paper", "code"}.issubset(set(record.get("required_source_types") or []))
    )


def per_intent_intent_accuracy_denominators(records: list[dict]) -> dict[str, int]:
    """Measurement-derived per-intent intent-accuracy applicability denominators.

    F6-A-R1-R1-R1: canonical ``aggregate_metrics`` exposes per-intent
    denominators for the recall metrics only, so the intent-accuracy
    applicability denominator is derived here from the same immutable records
    under the canonical measurement rule (``metric_applicability`` override
    plus a non-None ``intent_correct`` value — exactly the cases the canonical
    ``intent_accuracy`` mean includes). A represented intent with zero
    measurable cases therefore reports denominator 0 and stays INCOMPLETE.
    """
    counts: dict[str, int] = {}
    for record in records:
        metrics = record.get("metrics") or {}
        if metrics.get("intent_correct") is None:
            continue
        if not (metrics.get("metric_applicability") or {}).get("intent_correct", True):
            continue
        intent = str(record["intent"])
        counts[intent] = counts.get(intent, 0) + 1
    return counts


def derive_gate_matrix(aggregate: dict, records: list[dict], prereg: dict) -> dict:
    thresholds = prereg["gold_quality_thresholds"]
    release = f6a_release_score(records)
    gates: dict[str, dict] = {}

    def rate_gate(name: str, value, denominator, minimum: float, inclusive: bool, upper: bool = False):
        # ``upper=True`` marks an upper-bound gate (value must stay strictly
        # below the threshold, e.g. identifier_hallucination_rate < 0.03);
        # all other preregistered rate gates are lower bounds.
        if value is None:
            passed = None
        elif upper:
            passed = value < minimum
        else:
            passed = value >= minimum if inclusive else value > minimum
        gates[name] = {
            "value": value,
            "threshold": minimum,
            "inclusive": inclusive,
            "upper_bound": upper,
            "passed": passed,
            "denominator": denominator,
        }

    def zero_gate(name: str, count_key: str):
        # F6-A-R1-R1 (defect C): a missing measurement (None) is INCOMPLETE —
        # it must never silently become 0 and PASS. Only an actual numeric
        # zero passes a zero-count gate.
        value = aggregate.get(count_key)
        gates[name] = {
            "value": value,
            "threshold": 0,
            "passed": (value == 0) if value is not None else None,
        }

    def per_intent_gate(
        name: str,
        metric_key: str,
        threshold: float,
        inclusive: bool = True,
        denominators: dict[str, int] | None = None,
    ):
        # F6-A-R1-R1 (defect E): every represented intent stays visible. A
        # represented intent without a valid measurement is INCOMPLETE; the
        # aggregate gate FAILs if any intent fails, is INCOMPLETE if none fail
        # but some intent lacks the metric, and PASSes only when every
        # represented intent is measured and passes.
        # F6-A-R1-R1-R1: ``denominators`` supplies measurement-derived
        # applicability counts for metrics the canonical aggregation does not
        # expose a per-intent denominator for (intent_accuracy); without it the
        # canonical ``{metric_key}_denominator`` entry is used unchanged.
        per_intent = aggregate.get("per_intent") or {}
        details = []
        for intent in sorted(per_intent):
            entry = per_intent[intent]
            value = entry.get(metric_key)
            passed = None if value is None else (value >= threshold if inclusive else value > threshold)
            if denominators is not None:
                applicable_denominator = denominators.get(intent, 0)
            else:
                applicable_denominator = entry.get(f"{metric_key}_denominator")
            details.append(
                {
                    "intent": intent,
                    "case_count": entry.get("cases"),
                    "applicable_denominator": applicable_denominator,
                    "metric_value": value,
                    "threshold": threshold,
                    "passed": passed,
                }
            )
        measured = [detail["passed"] for detail in details if detail["passed"] is not None]
        if any(detail["passed"] is False for detail in details):
            passed = False
        elif len(measured) < len(details):
            passed = None
        else:
            passed = all(measured)
        minimum_value = min(
            (detail["metric_value"] for detail in details if detail["metric_value"] is not None),
            default=None,
        )
        gates[name] = {
            "value": minimum_value,
            "threshold": threshold,
            "inclusive": inclusive,
            "passed": passed,
            "per_intent_details": details,
        }

    rate_gate(
        "gold_recall_at_10",
        aggregate.get("gold_recall_at_10"),
        aggregate.get("gold_recall_at_10_denominator"),
        thresholds["gold_recall_at_10"],
        True,
    )
    rate_gate(
        "final_evidence_recall",
        aggregate.get("final_evidence_recall"),
        aggregate.get("final_evidence_recall_denominator"),
        thresholds["final_evidence_recall"],
        True,
    )
    rate_gate(
        "critical_final_evidence_recall",
        aggregate.get("critical_final_evidence_recall"),
        aggregate.get("critical_final_evidence_recall_denominator"),
        thresholds["critical_final_evidence_recall"],
        True,
    )
    rate_gate(
        "intent_accuracy",
        aggregate.get("intent_accuracy"),
        # F6-A-R1-R1 (defect D): the intent-accuracy denominator is the intent
        # accuracy's own case count (sum of represented per-intent cases), not
        # another metric's denominator field.
        sum(
            (entry.get("cases") or 0)
            for entry in (aggregate.get("per_intent") or {}).values()
        ) or aggregate.get("scored_cases"),
        thresholds["intent_accuracy"],
        True,
    )
    per_intent_gate(
        "per_intent_gold_recall_at_10",
        "gold_recall_at_10",
        thresholds["per_intent_gold_recall_at_10"],
        True,
    )
    per_intent_gate(
        "per_intent_intent_accuracy",
        "intent_accuracy",
        thresholds["per_intent_intent_accuracy"],
        True,
        denominators=per_intent_intent_accuracy_denominators(records),
    )
    rate_gate(
        "expected_status_accuracy",
        aggregate.get("expected_status_accuracy"),
        aggregate.get("expected_status_accuracy_denominator"),
        thresholds["expected_status_accuracy"],
        True,
    )
    rate_gate(
        "citation_integrity",
        aggregate.get("citation_integrity"),
        aggregate.get("citation_integrity_denominator"),
        thresholds["citation_integrity"],
        True,
    )
    zero_gate("wrong_version_evidence_count", "wrong_version_evidence_count")
    zero_gate("forbidden_evidence_count", "forbidden_evidence_count")
    rate_gate(
        "required_source_coverage_answered",
        aggregate.get("required_source_coverage_answered"),
        aggregate.get("required_source_coverage_answered_denominator"),
        thresholds["required_source_coverage_answered"],
        True,
    )
    rate_gate(
        "identifier_hallucination_rate",
        aggregate.get("identifier_hallucination_rate"),
        aggregate.get("identifier_hallucination_denominator"),
        thresholds["identifier_hallucination_rate"],
        False,
        upper=True,
    )
    rate_gate(
        "paper_code_dual_source_rate",
        aggregate.get("paper_code_dual_source_rate"),
        aggregate.get("paper_code_dual_source_denominator"),
        thresholds["paper_code_dual_source_rate"],
        True,
    )
    rate_gate(
        "answer_point_coverage",
        aggregate.get("answer_point_coverage"),
        aggregate.get("answer_point_coverage_denominator"),
        thresholds["answer_point_coverage"],
        True,
    )
    zero_gate("critical_answer_point_miss_count", "critical_answer_point_miss_count")
    zero_gate("contradiction_count", "contradiction_count")
    zero_gate("major_unsupported_claim_count", "major_unsupported_claim_count")
    zero_gate("unhandled_exception_count", "unhandled_exception_count")
    gates["release_score"] = {
        "value": release["release_score"],
        "denominator": release["denominator"],
        "incomplete_case_ids": release["incomplete_case_ids"],
        "note": "F6-A-specific gap/dependency accounting metric; not itself a gate",
    }
    return gates


def _gate_comparison_view(gates: dict) -> dict:
    """Return gates with the repaired ``applicable_denominator`` field stripped.

    F6-A-R1-R1-R1 source-matrix verification: every other gate datum (values,
    thresholds, passed states, canonical denominators, per-intent details) must
    match the prior matrix exactly; only this field is expected to differ.
    """
    normalized = copy.deepcopy(gates)
    for gate in normalized.values():
        for detail in gate.get("per_intent_details") or []:
            detail.pop("applicable_denominator", None)
    return normalized


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_gate_receipt(
    *,
    run_id: str,
    output_path: Path,
    output_sha256: str,
    prereg_path: Path,
    records: list[dict],
    manifest: dict,
    manifest_path: Path,
    run_dir: Path,
    candidate_id: str | None,
    candidate_manifest_sha256: str | None,
    candidate_valid: bool | None,
    cohort_decision: dict,
    gates_passed: bool | None,
    source_matrix_path: Path | None = None,
) -> dict:
    results_path = run_dir / "results.jsonl"
    results_sha256 = _sha256_file(results_path) if results_path.exists() else None
    manifest_sha256 = _sha256_file(manifest_path) if manifest_path.exists() else None
    prereg_sha256 = _sha256_file(prereg_path) if prereg_path.exists() else None
    source_matrix_sha256 = (
        _sha256_file(source_matrix_path)
        if source_matrix_path and source_matrix_path.exists()
        else None
    )

    sorted_ids = sorted(str(r.get("id")) for r in records)
    case_id_set_sha256 = _sha256_text(json.dumps(sorted_ids, separators=(",", ":")))
    content_hash = _result_content_hash(records)

    return {
        "schema_version": "f6a-gate-receipt-v1",
        "role": "forward-only gate receipt binding source results, manifest, prereg, and derived matrix output",
        "run_id": run_id,
        "candidate_id": candidate_id,
        "candidate_manifest_sha256": candidate_manifest_sha256,
        "candidate_valid": candidate_valid,
        "cohort_status": cohort_decision["status"],
        "decision": cohort_decision["verdict"],
        "gates_passed": gates_passed,
        "source_artifacts": {
            "manifest_sha256": manifest_sha256,
            "results_sha256": results_sha256,
            "record_content_hash": content_hash,
            "record_count": len(records),
            "case_id_set_sha256": case_id_set_sha256,
            "prereg_sha256": prereg_sha256,
            "source_matrix_sha256": source_matrix_sha256,
        },
        "derived_output": {
            "output_file": output_path.name,
            "derived_output_sha256": output_sha256,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def create_or_validate_gate_receipt(
    receipt_path: Path,
    receipt_data: dict,
) -> dict:
    if receipt_path.exists():
        try:
            existing = json.loads(receipt_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ValueError(f"existing gate receipt {receipt_path} is corrupted: {exc}") from exc

        mismatches = []
        for top_key in (
            "schema_version",
            "run_id",
            "candidate_id",
            "candidate_manifest_sha256",
            "candidate_valid",
            "cohort_status",
            "decision",
            "gates_passed",
        ):
            if existing.get(top_key) != receipt_data.get(top_key):
                mismatches.append(f"{top_key} (expected {receipt_data.get(top_key)}, got {existing.get(top_key)})")

        for art_key in (
            "manifest_sha256",
            "results_sha256",
            "record_content_hash",
            "record_count",
            "case_id_set_sha256",
            "prereg_sha256",
            "source_matrix_sha256",
        ):
            exp = receipt_data.get("source_artifacts", {}).get(art_key)
            act = (existing.get("source_artifacts") or {}).get(art_key)
            if exp != act:
                mismatches.append(f"source_artifacts.{art_key} (expected {exp}, got {act})")

        exp_derived = receipt_data.get("derived_output", {})
        act_derived = existing.get("derived_output") or {}
        if exp_derived.get("output_file") != act_derived.get("output_file"):
            mismatches.append(f"derived_output.output_file (expected {exp_derived.get('output_file')}, got {act_derived.get('output_file')})")
        if exp_derived.get("derived_output_sha256") != act_derived.get("derived_output_sha256"):
            mismatches.append(f"derived_output.derived_output_sha256 (expected {exp_derived.get('derived_output_sha256')}, got {act_derived.get('derived_output_sha256')})")

        if mismatches:
            raise ValueError(
                f"existing gate receipt {receipt_path} does not match current run inputs or derived output "
                f"(mismatched fields: {', '.join(mismatches)}); "
                "immutable gate receipts cannot be overwritten"
            )
        return existing

    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    temp_receipt = receipt_path.parent / f".{receipt_path.name}.tmp"
    temp_receipt.write_text(
        json.dumps(receipt_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temp_receipt, receipt_path)
    return receipt_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument(
        "--source-matrix",
        type=Path,
        default=None,
        help="prior gate matrix; when given, gate data must match exactly "
        "except the repaired applicable_denominator field, else no output "
        "is written",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.source_matrix is not None:
        if args.source_matrix.resolve() == args.output.resolve():
            raise ValueError(
                f"cannot replace source matrix input with output: {args.source_matrix}"
            )
    if args.prereg.resolve() == args.output.resolve():
        raise ValueError(
            f"cannot replace prereg input with output: {args.prereg}"
        )

    run_dir = args.project_root / "data" / "evaluation" / "runs" / args.run_id
    records = load_run_records(run_dir)
    prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
    aggregate = aggregate_metrics(records)
    gates = derive_gate_matrix(aggregate, records, prereg)
    # ``release_score`` is gap/dependency accounting, not a gate: it has no
    # passed semantics and is excluded from failed/incomplete gate counts.
    gate_names = [name for name in gates if name != "release_score"]
    failed = sorted(name for name in gate_names if gates[name].get("passed") is False)
    incomplete = sorted(name for name in gate_names if gates[name].get("passed") is None)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    expected_case_ids = resolve_expected_case_ids(args.project_root, manifest)
    candidate_id, candidate_manifest_sha256, candidate_valid = resolve_candidate_binding(
        args.project_root, manifest
    )
    if candidate_valid is False:
        gates_passed = None
    elif len(failed) > 0:
        gates_passed = False
    elif len(incomplete) > 0:
        gates_passed = None
    else:
        gates_passed = True

    cohort_decision = evaluate_cohort_decision(
        records=records,
        expected_case_ids=expected_case_ids,
        candidate_valid=candidate_valid,
        gates_passed=gates_passed,
        mode=manifest.get("mode"),
    )

    if cohort_decision["verdict"] == "RECOVERY_PENDING":
        print(f"cohort_status: {cohort_decision['status']}")
        print(f"official_decision: {cohort_decision['verdict']}")
        print("stage_receipt_sealed: False")
        print(f"NOTICE: evaluation recovery pending ({cohort_decision['reason']}); not a final gate decision.")
        return

    source_r1_r1_matrix = None
    terminal_verdict_effect = None
    if args.source_matrix is not None:
        prior = json.loads(args.source_matrix.read_text(encoding="utf-8"))
        divergence = []
        if prior.get("failed_gate_names") != failed:
            divergence.append("failed_gate_names")
        if prior.get("incomplete_gate_names") != incomplete:
            divergence.append("incomplete_gate_names")
        if _gate_comparison_view(prior.get("gates") or {}) != _gate_comparison_view(gates):
            divergence.append("gate values/passed states")
        if divergence:
            raise SystemExit(
                f"gate divergence from {args.source_matrix}: "
                f"{', '.join(divergence)}; successor matrix not written"
            )
        source_r1_r1_matrix = args.source_matrix.as_posix()
        prior_effect = prior.get("terminal_verdict_effect")
        if prior_effect:
            terminal_verdict_effect = (
                prior_effect
                if prior_effect.startswith("NO_CHANGE / ")
                else f"NO_CHANGE / {prior_effect}"
            )
        elif cohort_decision["verdict"] == "INCONCLUSIVE":
            terminal_verdict_effect = (
                f"NO_CHANGE / F6-A remains {cohort_decision['status']} / INCONCLUSIVE"
            )
        elif cohort_decision["verdict"] == "INCOMPLETE" or gates_passed is None:
            terminal_verdict_effect = (
                f"NO_CHANGE / F6-A remains {cohort_decision['status']} / INCOMPLETE / GATE_MEASUREMENT_MISSING"
            )
        else:
            terminal_verdict_effect = (
                f"NO_CHANGE / F6-A remains {cohort_decision['status']} / {cohort_decision['verdict']}"
            )
    else:
        if cohort_decision["status"] == "INCOMPLETE":
            if cohort_decision["verdict"] == "INCONCLUSIVE":
                terminal_verdict_effect = "INCONCLUSIVE / PRE_RELEASE_EXECUTION_INCOMPLETE"
            else:
                terminal_verdict_effect = f"INCOMPLETE / {cohort_decision['verdict']}"
        else:
            if cohort_decision["verdict"] == "PASS":
                terminal_verdict_effect = "COMPLETE / PASS"
            elif cohort_decision["verdict"] == "INCOMPLETE" or gates_passed is None:
                terminal_verdict_effect = "COMPLETE / INCOMPLETE / GATE_MEASUREMENT_MISSING"
            elif cohort_decision["verdict"] == "INCONCLUSIVE":
                terminal_verdict_effect = "COMPLETE / INCONCLUSIVE"
            else:
                terminal_verdict_effect = (
                    "COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED"
                )
    output = {
        "schema_version": "f6a-gate-matrix-r1r1r1-v1",
        "source_run_id": args.run_id,
        "source_record_count": len(records),
        "source_r1_r1_matrix": source_r1_r1_matrix,
        "evaluator_revision": "canonical aggregate_metrics (offline rescore; zero model calls; "
        "R1-R1 gate semantics; R1-R1-R1 measurement-derived per-intent "
        "intent-accuracy denominators)",
        "scientific_calls": 0,
        "scientific_tokens": 0,
        "aggregate_metrics": aggregate,
        "gates": gates,
        "per_intent_details": {
            name: gates[name]["per_intent_details"]
            for name in ("per_intent_gold_recall_at_10", "per_intent_intent_accuracy")
        },
        "dual_source_applicable_ids": dual_source_applicable_ids(records),
        "failed_gate_names": failed,
        "failed_gate_count": len(failed),
        "incomplete_gate_names": incomplete,
        "incomplete_gate_count": len(incomplete),
        "terminal_verdict_effect": terminal_verdict_effect,
        "cohort_decision": cohort_decision,
        "per_intent_breakdown": aggregate.get("per_intent"),
        "measured_model_outputs": "immutable per-case records under data/evaluation/runs/"
        + args.run_id,
        "offline_derived_metrics": "everything in this file",
    }
    output_content = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    output_sha256 = _sha256_text(output_content)

    gate_receipt_path = args.output.parent / f"{args.output.stem}_receipt.json"
    receipt_data = _build_gate_receipt(
        run_id=args.run_id,
        output_path=args.output,
        output_sha256=output_sha256,
        prereg_path=args.prereg,
        records=records,
        manifest=manifest,
        manifest_path=manifest_path,
        run_dir=run_dir,
        candidate_id=candidate_id,
        candidate_manifest_sha256=candidate_manifest_sha256,
        candidate_valid=candidate_valid,
        cohort_decision=cohort_decision,
        gates_passed=gates_passed,
        source_matrix_path=args.source_matrix,
    )
    create_or_validate_gate_receipt(gate_receipt_path, receipt_data)
    receipt_sealed = True

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = args.output.parent / f".{args.output.name}.tmp"
    temp_output.write_text(output_content, encoding="utf-8", newline="\n")
    os.replace(temp_output, args.output)

    print(f"cohort_status: {cohort_decision['status']}")
    print(f"official_decision: {cohort_decision['verdict']}")
    print(f"stage_receipt_sealed: {receipt_sealed}")
    for name, gate in gates.items():
        print(f"{name}: value={gate.get('value')} passed={gate.get('passed')}")
    print("failed_gate_count:", len(failed), failed)
    print("incomplete_gate_count:", len(incomplete), incomplete)


if __name__ == "__main__":
    main()
