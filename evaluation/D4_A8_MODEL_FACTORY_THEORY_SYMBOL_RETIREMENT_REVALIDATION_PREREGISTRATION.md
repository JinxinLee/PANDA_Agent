# D4-A8 — Model-Factory-Theory Symbol-Retirement Targeted Revalidation Preregistration

## 0. Executive Summary

This document establishes the formal, targeted scientific revalidation preregistration for the three currently held symbol locators of `model_factory_theory` under lifecycle stage `D4-A8`.

### Core Lifecycle Principles

1. **Preregistration Only**:
   - `D4-A8` authorizes **zero** provider calls, **zero** retrieval cells, **zero** scientific outcome exposure, and **zero** production mutation.
   - Downstream paired retrieval and evaluation belong strictly to separately authorized `D4-A9`.

2. **Preservation of Authoritative Production Baseline (D4-A7)**:
   - Starting HEAD: `2da89b8223399ff184f4b2b3674f7c995ce8d390` (`D4-A7 activate validated-subset locator retirement`).
   - `configs/query_expansions.yaml` and `src/` remain byte-identical to `D4-A7`.
   - Batch 1 remains `ACTIVE`.
   - The Batch 2 validated subset (`effective_acceptance_pipeline` and `root_macro_usage`) remains active with symbols retired and `structured_replacement: false`.
   - Full Batch 2 production activation remains `false`.

3. **Narrowed Hypothesis Scope**:
   - **Targeted Mask** (`MODEL_FACTORY_THEORY_SYMBOL_MASK`):
     - `model/PndLmdDPMAngModel1D.cxx`
     - `model/PndLmdDPMAngModel2D.cxx`
     - `model/PndLmdModelFactory.cxx`
   - **Held Page Hints**:
     - `pflueger_2017: [51, 57, 65]` remain **HOLD** and are strictly outside the retirement treatment.
   - D4-A8 does **not** claim full validation of `model_factory_theory` or full Batch 2 activation.

---

## 1. Lineage and Historical Defect Attribution

### 1.1 Frozen Historical Outcome in D4-A5
In `D4-A5`, `model_factory_theory` was classified as `INCONCLUSIVE_BASELINE_NOT_REPRODUCED`:
- Direct case `n014.e1` (`luminosityfit/model_framework/README.md`) failed to reproduce the baseline under both arms (`CURRENT_COMPAT` and `BATCH2_RETIREMENT`), yielding `PAIR_UNRESOLVED_BOTH`.
- `n014.e2` (`luminosityfit/model/PndLmdModelFactory.h`) preserved `CURRENT_COMPAT` under both arms (`PAIR_PRESERVED`).

### 1.2 Why n014 Is Not Reused as the Sole Direct Gate
- `n014` asks about the distinction between the `model_framework/` directory and the native `model/` directory.
- Its critical evidence requirements (`model_framework/README.md` and `PndLmdModelFactory.h`) do not align with the symbols or paper page hints contributed by `model_factory_theory`.
- `n014` remains historical scientific evidence of the baseline reproduction problem, but it cannot serve as the sole direct targeted validation gate for `model_factory_theory` symbol retirement.

---

## 2. Formal Cohort Specification

The formal cohort is drawn strictly from approved, exposed English cases in `evaluation/benchmarks/v2_6/gold_questions.yaml`:

| Case ID | Split | Language | Intent | Expected Status | Formal Role | Critical Evidence Target |
|---|---|---|---|---|---|---|
| `g031` | dev | en | api | answered | `DIRECT_MODEL_FACTORY_TREATMENT_CASE` | `luminosityfit model/PndLmdModelFactory.cxx generateModel` (`g031.e1`) |
| `g032` | dev | en | api | answered | `DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL` | `luminosityfit model/PndLmdDPMAngModel1D.cxx` (`g032.e1`) |
| `g033` | dev | en | api | answered | `DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL` | `luminosityfit model/PndLmdDPMAngModel2D.cxx` (`g033.e1`) |
| `g047` | dev | en | algorithm_theory | answered | `PAGE_HINT_ADJACENT_NONMATCHING_CONTROL` | `pflueger_2017` page 51 (`g047.e1`) |

### 2.1 Mechanical Rule-Matching Audit
Audited using production query expansion trigger matching (`select_matching_query_expansions`):
- `g031`: Matches `model_factory_theory` and `model_factory_acceptance_methods` $\rightarrow$ Direct treatment case.
- `g032`: Does not match `model_factory_theory` $\rightarrow$ Deterministic no-op control.
- `g033`: Does not match `model_factory_theory` $\rightarrow$ Deterministic no-op control.
- `g047`: Matches `dpm_model_theory`; does not match `model_factory_theory` $\rightarrow$ Deterministic no-op control.

### 2.2 Exclusion of Diagnostic Asset g064
- Case `g064` matches `model_factory_theory` and addresses DPM, acceptance, and resolution composition.
- However, its language is Chinese (`zh`). Current product scope is English-only.
- `g064` is recorded as `EXISTING_NON_ENGLISH_DIAGNOSTIC_ASSET` and is excluded from the formal evaluation gate.

---

## 3. Page-Hint Coverage Gap Audit

- **Audit Question**: Does an existing approved English case naturally match `model_factory_theory` under an intent permitting page hints to survive normal production plan formation (`algorithm_theory` or `algorithm_implementation`)?
- **Finding**:
  - `g031`: intent `api` $\rightarrow$ page hints dropped by intent policy.
  - `n014`: intent `module_structure` $\rightarrow$ page hints dropped by intent policy.
  - `g064`: intent `algorithm_implementation` $\rightarrow$ language `zh` (non-English).
- **Result**: `NO_EXISTING_APPROVED_ENGLISH_CASE_FOUND`.
- **Status**: `MODEL_FACTORY_THEORY_PAGE_HINT_GAP = OPEN`.
- **Conclusion**: `pflueger_2017 [51, 57, 65]` cannot be evaluated under existing English cases and must remain strictly **HOLD**.

---

## 4. Prospective Experimental Design (D4-A9)

### 4.1 Arm Definitions
1. **`A7_CURRENT`**:
   - Prospective canonical shared RetrievalPlan generated under current A7 production behavior. Unmodified.
2. **`MODEL_FACTORY_SYMBOL_RETIREMENT`**:
   - Same frozen canonical plan.
   - Subtracts contribution-ledger origins where:
     - `rule_id == "model_factory_theory"`
     - `component_kind == "symbol"`
     - `component_value in ["model/PndLmdDPMAngModel1D.cxx", "model/PndLmdDPMAngModel2D.cxx", "model/PndLmdModelFactory.cxx"]`
     - `applicability == "ACTIVE_IDENTIFIABLE"`
   - Preserves all independent origins (e.g., `model/PndLmdModelFactory.cxx` contributed by `model_factory_acceptance_methods`).
   - Preserves all paper page hints, concepts, repositories, source budgets, and routing state.

### 4.2 Shared-Plan Protocol
- Exact prospective canonical shared plan per case.
- Zero downstream Analyzer calls after plan freeze.
- No plan redraw or post-hoc plan selection.

### 4.3 Plan Reusability Audit
- `g031`: `NO_COMPATIBLE_FROZEN_PLAN`
- `g032`: `NO_COMPATIBLE_FROZEN_PLAN`
- `g033`: `NO_COMPATIBLE_FROZEN_PLAN`
- `g047`: `NO_COMPATIBLE_FROZEN_PLAN`
- All 4 cases require fresh prospective plan acquisition in D4-A9 (4 plans, 8 retrieval cells).

### 4.4 Model Contract and Provider Budget
- **Analyzer Model**: `gemini-3.8-flash`
- **Embedding Model**: `gemini-embedding-2`
- **Vertex Location**: `global`, temperature: `0.0`, max_retries: `0`
- **Budget**:
  - Analyzer: 4 calls
  - Embedding: 8 calls
  - Reranker: 8 calls
  - QA / Verifier / Judge: 0 calls
  - Evaluator provider calls: 0
  - Total logical model calls: 20

---

## 5. Decision Gates and Outcome Precedence

1. **Level 1 — `INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED`**:
   Malformed inputs, provenance ambiguity, arm plan divergence, unexpected treatment on controls, downstream Analyzer call.
2. **Level 2 — `INCONCLUSIVE / TARGET_REFERENCE_BASELINE_NOT_REPRODUCED`**:
   `g031.e1` is not retained in `A7_CURRENT`.
3. **Level 3 — `DEPENDENCY_OBSERVED_RETAIN`**:
   Removal of active `model_factory_theory` symbol origins produces attributable T/F loss on `g031.e1`.
4. **Level 4 — `FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION`**:
   Treatment divergence on no-op controls (`g032`, `g033`, `g047`), critical retrieval regressions, grounding/version violations.
5. **Level 5 — `INCONCLUSIVE / SYMBOL_COMPONENT_APPLICABILITY_INCOMPLETE`**:
   Baseline reproduced, zero dependency/safety failure, but fewer than 3 target symbols are `ACTIVE_IDENTIFIABLE`.
6. **Level 6 — `PARTIAL / MODEL_FACTORY_SYMBOL_RETIREMENT_VALIDATED_PAGE_HINTS_HOLD`**:
   `g031` baseline reproduced; all 3 target symbols `ACTIVE_IDENTIFIABLE`; selected-rule symbol origins subtracted cleanly; zero T/F loss; all controls remain strict no-ops; zero safety regressions; page hints preserved.

---

## 6. Scope Boundary and Governance

- **Production Activation**: `false` (A8 authorizes zero production changes).
- **D4-A9 Execution**: `false` (Requires separate explicit authorization).
- **Page Hints**: Remain strictly on `HOLD`.
- **Batch 2 Full Activation**: Remains `false`.
