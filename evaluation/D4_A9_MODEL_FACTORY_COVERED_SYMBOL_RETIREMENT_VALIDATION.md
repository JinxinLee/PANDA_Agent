# D4-A9 — Component-Sensitive Model-Factory Covered-Symbol Retirement Targeted Validation

## 0. Lifecycle Classification & Authority

- **Lifecycle Stage:** `D4-A9`
- **Full Title:** `D4-A9 — Component-Sensitive Model-Factory Covered-Symbol Retirement Targeted Validation`
- **Classification:** NEW forward scientific execution stage.
- **Consumed Machine Authority:** `D4-A8-R2` commit `06f853d9613c5170676d77261cc2d7b82d50958c` (`COMPLETE / PASS / COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEALED`).
- **Production Status:** `src/` and `configs/` are strictly immutable; `FULL_BATCH2_PRODUCTION_ACTIVATION = false`.

---

## 1. Frozen Scientific Scope & Target Masks

### Covered Scientific Target
```text
COVERED_SYMBOL_MASK = [
  model/PndLmdModelFactory.cxx
]
```
- Direct treatment coverage established via approved English case `g031` requiring critical evidence group `g031.e1` (`generateModel`).

### Held Uncovered Components & Page Hints
```text
UNCOVERED_SYMBOL_HOLD_MASK = [
  model/PndLmdDPMAngModel1D.cxx,
  model/PndLmdDPMAngModel2D.cxx
]
Disposition: HOLD_DIRECT_TREATMENT_COVERAGE_GAP

PAGE_HINT_HOLD_MASK = {
  pflueger_2017: [51, 57, 65]
}
Disposition: HOLD_OUTSIDE_TREATMENT_SCOPE
```

---

## 2. Formal Cohort & Case Roles

The formal evaluation cohort is closed, ordered, and exact ($N=4$):
1. **`g031`** — `DIRECT_MODEL_FACTORY_TREATMENT_CASE`
   - Query: *"Where does PndLmdModelFactory assemble the fit model?"*
   - Covered component: `model/PndLmdModelFactory.cxx`
   - Critical evidence group: `g031.e1`
   - Matched rules: `model_factory_theory`, `model_factory_acceptance_methods`
2. **`g032`** — `DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL`
   - Query: *"Which source implements the 1D DPM angular model?"*
   - Critical evidence group: `g032.e1` (`model/PndLmdDPMAngModel1D.cxx`)
   - Pre-retrieval projection: exact no-op identity projection.
3. **`g033`** — `DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL`
   - Query: *"Which source implements the 2D DPM angular model?"*
   - Critical evidence group: `g033.e1` (`model/PndLmdDPMAngModel2D.cxx`)
   - Pre-retrieval projection: exact no-op identity projection.
4. **`g047`** — `PAGE_HINT_ADJACENT_NONMATCHING_CONTROL`
   - Query: *"What is the theoretical purpose of the DPM elastic-scattering model?"*
   - Critical evidence group: `g047.e1` (`pflueger_2017` page 51)
   - Pre-retrieval projection: exact no-op identity projection.

Excluded from formal cohort: `g064` (language `zh`, excluded from English benchmark scope).

---

## 3. Provider Contract & Execution Accounting

- **Query Analyzer:** `gemini-3.8-flash`, `temperature = 0.0`, location `global`, `max_retries = 0`.
- **Dense Embedding:** `gemini-embedding-2`.
- **Reranker:** production reranker contract.
- **Evaluator:** 0 provider calls, 0 judge calls, 0 QA calls, 0 verifier calls.

### Actual Provider Accounting
- **Phase P (Plan Acquisition):**
  - Analyzer logical calls: 4
  - Analyzer provider attempts: 4
  - Retries: 0
  - Token usage: 7,199 tokens
- **Phase R (Paired Retrieval):**
  - Embedding calls: 8
  - Reranker calls: 8
  - Model calls: 16
  - Retries: 0
  - Token usage: 131,070 tokens
- **Evaluator:**
  - Model calls: 0
  - Tokens: 0
- **Cumulative Lifecycle Total:**
  - Total logical model calls: 20 (budget: 20)
  - Total provider attempts: 20
  - Retries: 0
  - Total token usage: 138,269 tokens

---

## 4. Execution Protocol & Checkpoints

### Persistence Before Gating
State progression:
$$\text{ACQUIRED} \longrightarrow \text{PERSISTED} \longrightarrow \text{GATED} \longrightarrow \text{RETRIEVAL\_ELIGIBLE}$$
All 14 frozen fields were durably written to `evaluation/d4_a9_raw_prospective_plans.json` before any applicability gate could terminate execution.

### Shared Canonical Plan
For each case, exactly one prospective Analyzer plan was acquired and shared across both evaluation arms:
1. `A7_CURRENT`
2. `COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`

### Paired Retrieval Schedule (8 Cells)
1. `g031 / A7_CURRENT`: completed (12 evidence items, `g031.e1` reproduced)
2. `g031 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`: completed (12 evidence items, `g031.e1` reproduced)
3. `g032 / A7_CURRENT`: completed (12 evidence items, `g032.e1` reproduced)
4. `g032 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`: completed (12 evidence items, `g032.e1` reproduced)
5. `g033 / A7_CURRENT`: completed (12 evidence items, `g033.e1` reproduced)
6. `g033 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`: completed (12 evidence items, `g033.e1` reproduced)
7. `g047 / A7_CURRENT`: completed (12 evidence items, `g047.e1` reproduced)
8. `g047 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`: completed (12 evidence items, `g047.e1` reproduced)

---

## 5. Evaluation Outcomes & Scientific Verdict

### Evidence Retention Analysis
1. **`g031` Direct Baseline & Treatment:**
   - `g031 / A7_CURRENT` reproduced critical evidence `g031.e1` (`model/PndLmdModelFactory.cxx generateModel`).
   - `g031 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT` reproduced critical evidence `g031.e1`.
   - The selected origin `model_factory_theory` was successfully subtracted from `symbol::model/PndLmdModelFactory.cxx`.
   - Independent origin `model_factory_acceptance_methods` survived, validly maintaining the literal symbol in the plan.
2. **Control Cases (`g032`, `g033`, `g047`):**
   - Critical evidence retention: 1.0/1.0 across all 3 controls in both current and treatment arms.
   - Regressions: 0 critical regressions, 0 grounding regressions, 0 version violations.

### Component Dispositions
- `model/PndLmdModelFactory.cxx`: `RETIREMENT_VALIDATED_COMPONENT`
- `model/PndLmdDPMAngModel1D.cxx`: `HOLD_DIRECT_TREATMENT_COVERAGE_GAP`
- `model/PndLmdDPMAngModel2D.cxx`: `HOLD_DIRECT_TREATMENT_COVERAGE_GAP`
- `pflueger_2017:[51, 57, 65]`: `HOLD_OUTSIDE_TREATMENT_SCOPE`

### Overall Scientific Verdict
```text
Level 6: PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD
```

### Consequences
- The rule-local `model_factory_theory` origin for `model/PndLmdModelFactory.cxx` is scientifically validated for future retirement.
- Both DPM symbols and Pflueger 2017 page hints remain strictly on `HOLD`.
- Full `model_factory_theory` retirement is NOT validated.
- Full Batch 2 production activation remains `false`.
- Production activation authorized: `false`.
