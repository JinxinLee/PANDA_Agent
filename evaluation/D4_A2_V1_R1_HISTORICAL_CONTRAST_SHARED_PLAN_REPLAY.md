# PANDA Agent — D4-A2-V1-R1: Historical Contrast Shared-Plan Replay Report

## 1. Executive Summary

- **Verdict**: `PASS / HISTORICAL_PLAN_SENSITIVITY_REPRODUCED_WITHOUT_TREATMENT_REGRESSION` (Level 6)
- **Lifecycle State**: `COMPLETE / PASS / HISTORICAL_PLAN_SENSITIVITY_REPRODUCED_WITHOUT_TREATMENT_REGRESSION`
- **Clean Factorial Pattern**: `T/T vs F/F`
- **Production Activation**: `False` (BLOCKED)
- **First-Batch Runtime Migration**: `BLOCKED`
- **D4-A3 State**: `NOT_STARTED / BLOCKED`
- **Exact Next Stage**: `D4-A2-V2 — Controlled Shared-Plan T2 Before/After Validation (NOT_STARTED / SEPARATELY_AUTHORIZED)`

> **Scientific Finding**: The historically observed n022.e2 availability contrast is reproduced by the frozen RetrievalPlan contrast under a common compatibility path, while no additional Batch-1 replacement regression is observed when each plan is shared across arms.

---

## 2. 2x2 Crossover Matrix Outcomes

| Cell | Historical Plan ID | Arm | Exact Retained | Top30 Retained | Final Pool Retained | Final Evidence Retained | Status |
|---|---|---|---|---|---|---|---|
| #1 | `HIST_A2_BEFORE_PLAN` | `BEFORE_COMPAT` | True | True | True | True | COMPLETED |
| #2 | `HIST_A2_BEFORE_PLAN` | `AFTER_BATCH1_REPLACEMENT` | True | True | True | True | COMPLETED |
| #3 | `HIST_A2_AFTER_PLAN` | `AFTER_BATCH1_REPLACEMENT` | False | False | False | False | COMPLETED |
| #4 | `HIST_A2_AFTER_PLAN` | `BEFORE_COMPAT` | False | False | False | False | COMPLETED |

---

## 3. Primary 2x2 Scientific Contrasts

### Contrast A — Historical Plan Effect under BEFORE_COMPAT
- Description: `HIST_A2_BEFORE_PLAN x BEFORE vs HIST_A2_AFTER_PLAN x BEFORE`
- BEFORE Plan Pre-rerank: `True`
- AFTER Plan Pre-rerank: `False`
- Historical Plan Sensitivity Reproduced: `True`
- Historical Exact-Recall Contrast Observed: `True`

### Contrast B — Historical Plan Effect under AFTER_BATCH1_REPLACEMENT
- Description: `HIST_A2_BEFORE_PLAN x AFTER vs HIST_A2_AFTER_PLAN x AFTER`
- BEFORE Plan Pre-rerank: `True`
- AFTER Plan Pre-rerank: `False`
- Contrast Observed: `True`

### Contrast C — Treatment Effect under HIST_A2_BEFORE_PLAN
- Description: `HIST_A2_BEFORE_PLAN: BEFORE vs AFTER`
- BEFORE_COMPAT Pre-rerank: `True`
- AFTER_BATCH1 Pre-rerank: `True`
- Classification: `PAIR_PRESERVED`

### Contrast D — Treatment Effect under HIST_A2_AFTER_PLAN
- Description: `HIST_A2_AFTER_PLAN: BEFORE vs AFTER`
- BEFORE_COMPAT Pre-rerank: `False`
- AFTER_BATCH1 Pre-rerank: `False`
- Classification: `PAIR_UNRESOLVED_BOTH`

---

## 4. Historical vs Replay Comparison

| Comparison | Historical Slot | Arm | Hist Exact | Replay Exact | Hist Pool | Replay Pool | Hist Final | Replay Final |
|---|---|---|---|---|---|---|---|---|
| Hist Slot 9 vs Cell 1 | 9 | `BEFORE_COMPAT` | True | True | True | True | True | True |
| Hist Slot 10 vs Cell 3 | 10 | `AFTER_BATCH1_REPLACEMENT` | False | False | False | False | False | False |

---

## 5. Formal Call and Resource Accounting

- **Formal Cases**: 1 (`n022`)
- **Historical Plans**: 2 (`HIST_A2_BEFORE_PLAN`, `HIST_A2_AFTER_PLAN`)
- **Arms**: 2 (`BEFORE_COMPAT`, `AFTER_BATCH1_REPLACEMENT`)
- **Formal Retrieval Cells**: 4 / 4 (0 failed)
- **Analyzer Calls**: 0 (Phase P absent; 0 provider calls in replay)
- **Embedding Calls**: 4 (`gemini-embedding-2`)
- **Reranker Calls**: 4 (`gemini-3.8-flash`)
- **Total Logical Model Calls**: 8
- **Provider Attempts**: 8 (0 retries)
- **Token Usage**: 67328
- **QA / Verifier / Judge Calls**: 0
- **PostgreSQL / Qdrant Writes**: 0
- **Protected Dataset Access**: 0 (0 novel validation, 0 novel holdout)

---

## 6. Key Scientific Metrics

- `HISTORICAL_EXACT_RECALL_CONTRAST_REPRODUCED = True`
- `HISTORICAL_PLAN_SENSITIVITY_REPRODUCED = True`
- `PAIR_TREATMENT_REGRESSION_COUNT = 0`
- `PAIR_TREATMENT_RECOVERY_COUNT = 0`
- `PAIR_PRESERVED_COUNT = 1`
- `PAIR_UNRESOLVED_BOTH_COUNT = 1`
- `FINAL_ONLY_REGRESSION_COUNT = 0`
- `FINAL_ONLY_RECOVERY_COUNT = 0`
- `CLEAN_FACTORIAL_PATTERN = T/T vs F/F`

---

## 7. Lifecycle Decision and Next Stage

```text
D4-A2-V1-R1 = COMPLETE / PASS / HISTORICAL_PLAN_SENSITIVITY_REPRODUCED_WITHOUT_TREATMENT_REGRESSION
PRODUCTION_ACTIVATION = false
FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED
D4-A3 = NOT_STARTED / BLOCKED
EXACT_NEXT_STAGE = D4-A2-V2 — Controlled Shared-Plan T2 Before/After Validation (NOT_STARTED / SEPARATELY_AUTHORIZED)
```
