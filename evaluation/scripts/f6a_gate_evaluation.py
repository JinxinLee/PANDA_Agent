"""F6-A gate evaluation (evaluation-only, deterministic).

Aggregates the frozen formal-Gold run records into the preregistered F6-A gate
matrix. No model calls.

Usage:
  PYTHONPATH=src python evaluation/scripts/f6a_gate_evaluation.py \
      --run-id f6a-rc1-gold-formal-full-20260913 \
      --prereg evaluation/f6_a_prerelease_validation_preregistration.json \
      --output evaluation/f6a_gold_gate_matrix.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from panda_agent.evaluation_runner import f6a_release_score, load_run_records


def _metric_values(records: list[dict], key: str) -> tuple[list[float], list[str]]:
    """Collect a metric over records where it is applicable (not None)."""
    values, inapplicable = [], []
    for record in records:
        value = (record.get("metrics") or {}).get(key)
        if value is None:
            inapplicable.append(str(record.get("id")))
        elif isinstance(value, bool):
            values.append(1.0 if value else 0.0)
        else:
            values.append(float(value))
    return values, inapplicable


def _count(records: list[dict], key: str) -> tuple[int, int]:
    """Count non-zero occurrences of a boolean/count/list metric; returns (count, applicable)."""
    total, applicable = 0, 0
    for record in records:
        value = (record.get("metrics") or {}).get(key)
        if value is None:
            continue
        applicable += 1
        if isinstance(value, bool):
            total += 1 if value else 0
        elif isinstance(value, (int, float)):
            total += int(value)
        elif isinstance(value, list):
            total += len(value)
    return total, applicable


def evaluate_gates(records: list[dict], prereg: dict) -> dict:
    thresholds = prereg["gold_quality_thresholds"]
    release = f6a_release_score(records)
    gates: dict[str, dict] = {}

    def rate_gate(name: str, key: str, minimum: float, inclusive: bool):
        values, inapplicable = _metric_values(records, key)
        if not values:
            gates[name] = {"value": None, "threshold": minimum, "passed": None, "inapplicable_ids": inapplicable}
            return
        value = sum(values) / len(values)
        passed = value >= minimum if inclusive else value > minimum
        gates[name] = {
            "value": value,
            "threshold": minimum,
            "inclusive": inclusive,
            "passed": passed,
            "denominator": len(values),
            "inapplicable_ids": inapplicable,
        }

    def zero_gate(name: str, key: str):
        total, applicable = _count(records, key)
        gates[name] = {"value": total, "threshold": 0, "passed": total == 0, "applicable_denominator": applicable}

    rate_gate("gold_recall_at_10", "gold_recall_at_10", thresholds["gold_recall_at_10"], True)
    rate_gate("final_evidence_recall", "final_evidence_recall", thresholds["final_evidence_recall"], True)
    rate_gate(
        "critical_final_evidence_recall",
        "critical_final_evidence_recall",
        thresholds["critical_final_evidence_recall"],
        True,
    )
    rate_gate("intent_accuracy", "intent_correct", thresholds["intent_accuracy"], True)
    rate_gate(
        "per_intent_gold_recall_at_10",
        "gold_recall_at_10",
        thresholds["per_intent_gold_recall_at_10"],
        True,
    )
    rate_gate(
        "per_intent_intent_accuracy",
        "intent_correct",
        thresholds["per_intent_intent_accuracy"],
        True,
    )
    rate_gate(
        "expected_status_accuracy",
        "expected_status_correct",
        thresholds["expected_status_accuracy"],
        True,
    )
    rate_gate("citation_integrity", "citation_integrity", thresholds["citation_integrity"], True)
    zero_gate("wrong_version_evidence_count", "wrong_version_evidence")
    zero_gate("forbidden_evidence_count", "forbidden_evidence")
    rate_gate(
        "required_source_coverage_answered",
        "required_source_coverage",
        thresholds["required_source_coverage_answered"],
        True,
    )
    hallucination_count, _ = _count(records, "hallucinated_identifiers")
    identifier_mentions, identifier_denominator_count = _count(records, "identifier_mentions")
    identifier_denominator = identifier_denominator_count
    gates["identifier_hallucination_rate"] = {
        "value": (hallucination_count / identifier_denominator) if identifier_denominator else None,
        "threshold": thresholds["identifier_hallucination_rate"],
        "inclusive": False,
        "passed": (
            (hallucination_count / identifier_denominator) < thresholds["identifier_hallucination_rate"]
            if identifier_denominator
            else None
        ),
        "hallucination_count": hallucination_count,
        "identifier_mentions": identifier_mentions,
        "denominator": identifier_denominator,
    }
    dual_values, dual_inapplicable = _metric_values(records, "paper_code_dual_source")
    gates["paper_code_dual_source_rate"] = {
        "value": (sum(dual_values) / len(dual_values)) if dual_values else None,
        "threshold": thresholds["paper_code_dual_source_rate"],
        "passed": (
            (sum(dual_values) / len(dual_values)) >= thresholds["paper_code_dual_source_rate"]
            if dual_values
            else None
        ),
        "denominator": len(dual_values),
        "inapplicable_ids": dual_inapplicable,
        "note": "applicable only to dual-source questions",
    }
    rate_gate("answer_point_coverage", "answer_point_coverage", thresholds["answer_point_coverage"], True)
    zero_gate("critical_answer_point_miss_count", "critical_answer_points_missing")
    zero_gate("contradiction_count", "contradictions")
    zero_gate("major_unsupported_claim_count", "major_unsupported_claim_ids")
    gates["unhandled_exception_count"] = {
        "value": len([r for r in records if r.get("exception")]),
        "threshold": 0,
        "passed": not any(r.get("exception") for r in records),
    }
    gates["release_score"] = release
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
    gates = evaluate_gates(records, prereg)
    output = {
        "schema_version": "f6a-gate-matrix-v1",
        "run_id": args.run_id,
        "record_count": len(records),
        "gates": gates,
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, gate in gates.items():
        print(f"{name}: value={gate.get('value')} passed={gate.get('passed')}")


if __name__ == "__main__":
    main()
