"""F6-A gate evaluation (evaluation-only, deterministic, zero model calls).

Aggregates the frozen formal-Gold run records through the canonical evaluator
aggregation (`evaluation.aggregate_metrics`) and derives the preregistered
F6-A gate matrix from its output. The release score remains the only
F6-A-specific arithmetic.

Usage:
  PYTHONPATH=src python evaluation/scripts/f6a_gate_evaluation.py \
      --run-id f6a-rc1-gold-formal-full-20260913 \
      --prereg evaluation/f6_a_prerelease_validation_preregistration.json \
      --output evaluation/f6a_gold_gate_matrix_r1.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from panda_agent.evaluation import aggregate_metrics
from panda_agent.evaluation_runner import f6a_release_score, load_run_records


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
        gates[name] = {
            "value": aggregate.get(count_key),
            "threshold": 0,
            "passed": (aggregate.get(count_key) or 0) == 0,
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
        aggregate.get("expected_status_accuracy_denominator"),
        thresholds["intent_accuracy"],
        True,
    )
    rate_gate(
        "per_intent_gold_recall_at_10",
        min(
            (
                entry.get("gold_recall_at_10")
                for entry in (aggregate.get("per_intent") or {}).values()
                if entry.get("gold_recall_at_10") is not None
            ),
            default=None,
        ),
        "per-intent minimum",
        thresholds["per_intent_gold_recall_at_10"],
        True,
    )
    rate_gate(
        "per_intent_intent_accuracy",
        min(
            (
                entry.get("intent_accuracy")
                for entry in (aggregate.get("per_intent") or {}).values()
                if entry.get("intent_accuracy") is not None
            ),
            default=None,
        ),
        "per-intent minimum",
        thresholds["per_intent_intent_accuracy"],
        True,
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.project_root / "data" / "evaluation" / "runs" / args.run_id
    records = load_run_records(run_dir)
    prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
    aggregate = aggregate_metrics(records)
    gates = derive_gate_matrix(aggregate, records, prereg)
    failed = sorted(name for name, gate in gates.items() if gate.get("passed") is False)
    output = {
        "schema_version": "f6a-gate-matrix-r1-v1",
        "run_id": args.run_id,
        "source_record_count": len(records),
        "evaluator_revision": "canonical aggregate_metrics (offline rescore; zero model calls)",
        "scientific_calls": 0,
        "scientific_tokens": 0,
        "aggregate_metrics": aggregate,
        "gates": gates,
        "failed_gate_names": failed,
        "failed_gate_count": len(failed),
        "per_intent_breakdown": aggregate.get("per_intent"),
        "measured_model_outputs": "immutable per-case records under data/evaluation/runs/"
        + args.run_id,
        "offline_derived_metrics": "everything in this file",
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, gate in gates.items():
        print(f"{name}: value={gate.get('value')} passed={gate.get('passed')}")
    print("failed_gate_count:", len(failed), failed)


if __name__ == "__main__":
    main()
