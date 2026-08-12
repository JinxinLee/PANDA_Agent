# English Gold Stratified Bootstrap Baseline

This package separates measured historical E2E evidence, current retrieval behavior, and current small-scale E2E behavior.
It is not a complete generalization, complete benchmark, or all-intent baseline.

## Measured artifacts

- Historical E2E: `m6-v2-36-qa-dev-rc3e` (80 questions).
- Current benchmark retrieval: `generalization-a3-stratified-retrieval-20260813` (24 questions).
- Current novel retrieval: `not run; no trustworthy novel dataset available` (0 questions).
- Current small E2E: `generalization-a3-stratified-qa-20260813` (16 questions; external judge disabled).

## Boundaries

- No fresh full 120-question E2E evaluation was run for this package.
- No full 120-question retrieval-only evaluation or T3 was run for this package.
- The empty novel artifacts are schemas/placeholders, not measured results.
- Planned roadmap acceptance targets are not baseline measurements.
- `data_flow`, `module_structure`, and `troubleshooting` are unevaluated because v2.6 has no eligible approved English Gold questions for those intents.

## Fixed comparison sets

- Retrieval IDs (24): `g001, g002, g003, g007, g012, g013, g014, g015, g025, g026, g027, g028, g029, g038, g041, g042, g043, g044, g045, g047, g057, g058, g059, g060`
- QA IDs (16): `g001, g007, g012, g013, g025, g026, g027, g038, g041, g042, g043, g044, g057, g058, g059, g060`
- Future before/after comparisons must reuse these IDs unchanged; a changed selection requires a new baseline manifest identity.

## Metrics

```json
{
  "benchmark_retrieval": {
    "cases_completed": 24,
    "citation_integrity": 1.0,
    "combined_candidate_recall": 0.95,
    "critical_final_evidence_recall": 0.9,
    "expected_status_accuracy": 0.8333333333333334,
    "final_evidence_recall": 0.9,
    "gold_recall_at_10": 0.9,
    "gold_recall_at_20": 0.9,
    "gold_recall_at_5": 0.8416666666666666,
    "intent_accuracy": 1.0,
    "mrr": 0.6866666666666666,
    "unhandled_exception_count": 0
  },
  "novel_retrieval": null,
  "small_e2e": {
    "cases_completed": 16,
    "citation_integrity": 1.0,
    "combined_candidate_recall": 0.875,
    "critical_final_evidence_recall": 0.7083333333333334,
    "expected_status_accuracy": 1.0,
    "final_evidence_recall": 0.7083333333333334,
    "gold_recall_at_10": 0.75,
    "gold_recall_at_20": 0.75,
    "gold_recall_at_5": 0.6041666666666666,
    "intent_accuracy": 1.0,
    "mrr": 0.65,
    "unhandled_exception_count": 0
  }
}
```
