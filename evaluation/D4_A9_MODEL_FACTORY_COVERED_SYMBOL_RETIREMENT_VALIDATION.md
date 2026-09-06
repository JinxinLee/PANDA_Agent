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

## 3. Provider Contract & Derived Budget

- **Query Analyzer:** `gemini-3.8-flash`, `temperature = 0.0`, location `global`, `max_retries = 0`.
- **Dense Embedding:** `gemini-embedding-2`.
- **Reranker:** production reranker contract.
- **Deterministic R2 Reusability Audit:** $N=4, R=0, F=4$.
- **Exact Budget:**
  - Analyzer calls: 4
  - Embedding calls: 8
  - Reranker calls: 8
  - QA calls: 0
  - Verifier calls: 0
  - Judge calls: 0
  - Scientific Evaluator calls: 0
  - Retries: 0
  - Total logical model calls: 20

---

## 4. Execution Protocol & Precedence Hierarchy

### Persistence Before Gating
State progression:
$$\text{ACQUIRED} \longrightarrow \text{PERSISTED} \longrightarrow \text{GATED} \longrightarrow \text{RETRIEVAL\_ELIGIBLE}$$
All 14 frozen fields are durably written to `evaluation/d4_a9_raw_prospective_plans.json` before any applicability gate can terminate execution.

### Shared Canonical Plan
For each case, exactly one prospective Analyzer plan is acquired and shared across both future evaluation arms:
1. `A7_CURRENT`
2. `COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`

### Paired Retrieval Schedule (8 Cells)
1. `g031 / A7_CURRENT`
2. `g031 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`
3. `g032 / A7_CURRENT`
4. `g032 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`
5. `g033 / A7_CURRENT`
6. `g033 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`
7. `g047 / A7_CURRENT`
8. `g047 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`

### Outcome Precedence Hierarchy (Frozen 6 Levels)
- **Level 1:** `INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED`
- **Level 2:** `INCONCLUSIVE / ALL_COVERED_COMPONENT_BASELINES_NOT_REPRODUCED`
- **Level 3:** `PARTIAL / DEPENDENCY_OBSERVED_FOR_COVERED_COMPONENTS_RETAIN`
- **Level 4:** `FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION`
- **Level 5:** `INCONCLUSIVE / COVERED_COMPONENT_APPLICABILITY_INCOMPLETE`
- **Level 6:** `PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD`
