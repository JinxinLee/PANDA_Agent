# A1 Boundary Smoke Diagnostic

This package separates measured historical E2E evidence, current retrieval behavior, and current small-scale E2E behavior.
It is not a complete generalization, complete benchmark, or all-intent baseline.
The source measurements are unchanged; this package corrects only metric applicability, portable paths, consistency metadata, and provenance wording.

## Measured execution provenance

- Base Git commit: `e132accefc8181abba76e8d818a621dd03cd1c9c`.
- Working tree dirty: `True`.
- In prototype development this truthfully identifies the measured execution as the base commit plus the then-current working-tree changes; it is not a frozen candidate identity.
- A later commit or newer HEAD does not invalidate this diagnostic baseline and does not require a rerun.

## Measured artifacts

- Historical E2E: `m6-v2-36-qa-dev-rc3e` (80 questions).
- Current benchmark retrieval: `generalization-a1-retrieval-smoke-host` (1 questions).
- Current novel retrieval: `not run; no trustworthy novel dataset available` (0 questions).
- Current small E2E: `generalization-a1-qa-smoke-host` (1 questions; external judge disabled).

## Boundaries

- No fresh full 120-question E2E evaluation was run for this package.
- No full 120-question retrieval-only evaluation or T3 was run for this package.
- The empty novel artifacts are schemas/placeholders, not measured results.
- Planned roadmap acceptance targets are not baseline measurements.
- External-rubric answer-point, contradiction, and unsupported-claim metrics are N/A for the unjudged QA run.
- `data_flow`, `module_structure`, and `troubleshooting` are unevaluated because v2.6 has no eligible approved English Gold questions for those intents.

## Fixed comparison sets

- Retrieval IDs (1): `g001`
- QA IDs (1): `g001`
- Future before/after comparisons must reuse these IDs unchanged; a changed selection requires a new baseline manifest identity.

## Metrics

```json
{
  "benchmark_retrieval": {
    "cases_completed": 1,
    "combined_candidate_recall": 1.0,
    "critical_final_evidence_recall": 1.0,
    "expected_status_accuracy": 1.0,
    "final_evidence_recall": 1.0,
    "gold_recall_at_10": 1.0,
    "gold_recall_at_20": 1.0,
    "gold_recall_at_5": 1.0,
    "intent_accuracy": 1.0,
    "metric_applicability": {
      "answer_point_coverage": false,
      "citation_integrity": false,
      "contradictions": false,
      "critical_answer_points_missing": false,
      "identifier_hallucination_rate": false,
      "major_unsupported_claim_ids": false,
      "minor_unsupported_claim_ids": false,
      "required_identifiers": false,
      "unsupported_claim_ids": false
    },
    "mrr": 1.0,
    "unhandled_exception_count": 0
  },
  "novel_retrieval": null,
  "small_e2e": {
    "cases_completed": 1,
    "citation_integrity": 1.0,
    "combined_candidate_recall": 1.0,
    "critical_final_evidence_recall": 1.0,
    "expected_status_accuracy": 1.0,
    "final_evidence_recall": 1.0,
    "gold_recall_at_10": 1.0,
    "gold_recall_at_20": 1.0,
    "gold_recall_at_5": 1.0,
    "intent_accuracy": 1.0,
    "metric_applicability": {
      "answer_point_coverage": false,
      "citation_integrity": true,
      "contradictions": false,
      "critical_answer_points_missing": false,
      "identifier_hallucination_rate": true,
      "major_unsupported_claim_ids": false,
      "minor_unsupported_claim_ids": false,
      "required_identifiers": true,
      "unsupported_claim_ids": false
    },
    "mrr": 1.0,
    "unhandled_exception_count": 0
  }
}
```
