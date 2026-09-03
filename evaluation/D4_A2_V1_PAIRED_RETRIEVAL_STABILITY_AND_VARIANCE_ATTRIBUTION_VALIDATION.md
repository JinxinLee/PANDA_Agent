# PANDA Agent — D4-A2-V1: Paired Retrieval Stability and Variance Attribution Validation

## 1. Executive Summary

```text
D4-A2-V1 VERDICT = PARTIAL / ANALYZER_VARIABILITY_OBSERVED_WITHOUT_EVIDENCE_SENSITIVITY
LEVEL = 6 / 7

ANALYZER_PLAN_DRAWS = 8 / 8
DISTINCT_PLAN_SIGNATURES = 8
R1_FEATURE_COMPLETE_COUNT = 6
R1_FEATURE_PARTIAL_COUNT = 2
R1_FEATURE_ABSENT_COUNT = 0

SHARED_PLAN_DOWNSTREAM_CELLS = 16 / 16
PHASE_R_ANALYZER_CALLS = 0 (GUARANTEED)

PAIR_PRESERVED_COUNT = 8
PAIR_UNRESOLVED_BOTH_COUNT = 0
PAIR_TREATMENT_REGRESSION_COUNT = 0
PAIR_TREATMENT_RECOVERY_COUNT = 0

FINAL_ONLY_REGRESSION_COUNT = 0
FINAL_ONLY_RECOVERY_COUNT = 0

PLAN_TO_EVIDENCE_SENSITIVITY_OBSERVED = False
R1_MECHANISM_REPRODUCED = False

PRODUCTION_ACTIVATION = false
FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED
D4-A3 = NOT_STARTED / BLOCKED
```

---

## 2. Scientific Objective and Attribution Findings

> Multiple analyzer plans observed (8 signatures), but n022.e2 pre-rerank availability remained invariant across all plans.

The historical D4-A2 evaluation confounded treatment comparison with independent Query Analyzer execution.
In D4-A2-V1, both arms were forced to receive the exact same frozen retrieval plan for each pair.

---

## 3. 8-Draw Analyzer Sampling & Phenotype Analysis

| Draw | Phenotype | Concepts Extracted | Distinct Signature |
|---|---|---|---|
| #1 | `R1_FEATURE_COMPLETE` | restgas analysis, event vertex, two-step POCA workflow, worker step, fitted vertex, reprocessing | Yes |
| #2 | `R1_FEATURE_PARTIAL` | restgas analysis, event vertex, two-step POCA workflow, first worker step, second analysis step, fitted vertex, reprocessing | Yes |
| #3 | `R1_FEATURE_COMPLETE` | event vertex, POCA workflow, worker step, analysis step, fitted vertex, reprocessing | Yes |
| #4 | `R1_FEATURE_COMPLETE` | restgas analysis, event vertex, POCA workflow, worker step, analysis step, fitted vertex, reprocessing | Yes |
| #5 | `R1_FEATURE_PARTIAL` | event vertex, POCA, first worker step, second analysis step, fitted vertex, reprocessing | Yes |
| #6 | `R1_FEATURE_COMPLETE` | restgas analysis, event vertex, two-step POCA workflow, worker step, analysis step, fitted vertex, reprocessing | Yes |
| #7 | `R1_FEATURE_COMPLETE` | restgas analysis, event vertex, POCA workflow, worker step, fitted vertex, reprocessing | Yes |
| #8 | `R1_FEATURE_COMPLETE` | restgas analysis, event vertex, two-step POCA workflow, worker step, fitted vertex, reprocessing | Yes |

---

## 4. 16-Cell Shared-Plan Replay Outcomes

| Plan | BEFORE Pre-Rerank | AFTER Pre-Rerank | Pre-Rerank Pair Class | BEFORE Final | AFTER Final | Final Evidence Class |
|---|---|---|---|---|---|---|
| Plan #1 | RETAINED | RETAINED | `PAIR_PRESERVED` | RETAINED | RETAINED | `FINAL_EVIDENCE_PRESERVED` |
| Plan #2 | RETAINED | RETAINED | `PAIR_PRESERVED` | RETAINED | RETAINED | `FINAL_EVIDENCE_PRESERVED` |
| Plan #3 | RETAINED | RETAINED | `PAIR_PRESERVED` | RETAINED | RETAINED | `FINAL_EVIDENCE_PRESERVED` |
| Plan #4 | RETAINED | RETAINED | `PAIR_PRESERVED` | RETAINED | RETAINED | `FINAL_EVIDENCE_PRESERVED` |
| Plan #5 | RETAINED | RETAINED | `PAIR_PRESERVED` | RETAINED | RETAINED | `FINAL_EVIDENCE_PRESERVED` |
| Plan #6 | RETAINED | RETAINED | `PAIR_PRESERVED` | RETAINED | RETAINED | `FINAL_EVIDENCE_PRESERVED` |
| Plan #7 | RETAINED | RETAINED | `PAIR_PRESERVED` | RETAINED | RETAINED | `FINAL_EVIDENCE_PRESERVED` |
| Plan #8 | RETAINED | RETAINED | `PAIR_PRESERVED` | RETAINED | RETAINED | `FINAL_EVIDENCE_PRESERVED` |

---

## 5. Formal Accounting

- **Formal Cases**: 1 (`n022`)
- **Analyzer Plan Draws**: 8 / 8
- **Downstream Cells**: 16 / 16
- **Logical Calls**: 40 (8 analyzer, 16 embedding, 16 reranker)
- **Provider Attempts**: 40
- **Retries**: 0
- **Token Usage**: 311393
- **QA / Verifier / Judge Calls**: 0
- **Database / Qdrant Writes**: 0
- **Protected Dataset Access**: 0

---

## 6. Lifecycle Transition

```text
PRODUCTION_ACTIVATION = false
FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED
D4-A3 = NOT_STARTED / BLOCKED
EXACT_NEXT_STAGE = D4-A2-V1-R1 — Expanded Analyzer Stability and Evidence-Sensitivity Validation (NOT_STARTED / SEPARATELY_AUTHORIZED)
```
