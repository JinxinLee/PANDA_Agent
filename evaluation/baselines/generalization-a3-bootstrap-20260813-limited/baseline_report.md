# A1 Boundary Smoke Diagnostic

This preserved 1-question retrieval/QA package verifies A1/A2 boundaries and serialization only. It is not the A3 baseline and is superseded by `english-gold-stratified-bootstrap-v1-20260813` for before/after comparisons.

This package separates measured historical E2E evidence, current retrieval behavior, and current small-scale E2E behavior.

## Measured artifacts

- Historical E2E: `m6-v2-36-qa-dev-rc3e` (80 questions).
- Current benchmark retrieval: `generalization-a1-retrieval-smoke-host` (1 questions).
- Current novel retrieval: `not run; no trustworthy novel dataset available` (0 questions).
- Current small E2E: `generalization-a1-qa-smoke-host` (1 questions; external judge disabled).

## Boundaries

- No fresh full 120-question E2E evaluation was run for this package.
- The empty novel artifacts are schemas/placeholders, not measured results.
- Planned roadmap acceptance targets are not baseline measurements.

## Metrics

```json
{
  "benchmark_retrieval": {
    "answer_point_coverage": 0.0,
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
    "mrr": 1.0,
    "unhandled_exception_count": 0
  },
  "novel_retrieval": null,
  "small_e2e": {
    "answer_point_coverage": 0.0,
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
    "mrr": 1.0,
    "unhandled_exception_count": 0
  }
}
```
