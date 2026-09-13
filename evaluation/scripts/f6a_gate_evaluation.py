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
import json
from pathlib import Path

from panda_agent.evaluation import aggregate_metrics
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
        terminal_verdict_effect = (
            "NO_CHANGE / F6-A remains COMPLETE / FAIL / "
            "EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED"
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
        "per_intent_breakdown": aggregate.get("per_intent"),
        "measured_model_outputs": "immutable per-case records under data/evaluation/runs/"
        + args.run_id,
        "offline_derived_metrics": "everything in this file",
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, gate in gates.items():
        print(f"{name}: value={gate.get('value')} passed={gate.get('passed')}")
    print("failed_gate_count:", len(failed), failed)
    print("incomplete_gate_count:", len(incomplete), incomplete)


if __name__ == "__main__":
    main()
