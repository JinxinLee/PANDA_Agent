# D4-A8-R1 — Component-Sensitive Model-Factory Revalidation Contract Repair

## 0. Executive Summary & Task Classification

`D4-A8-R1` is a forward repair stage of the targeted scientific revalidation preregistration for `model_factory_theory` locators:

```text
Lifecycle stage: D4-A8-R1
Stage classification: Forward Repair Stage (child of D4-A8)
Starting HEAD: ae2e744f6a05e711d407a02d0ae276e6e1422809
Starting parent HEAD: 2da89b8223399ff184f4b2b3674f7c995ce8d390
Commit message: D4-A8-R1 repair component-sensitive revalidation contract
Authorizations: production_activation_authorized = false; d4_a9_authorized = false
```

This stage is NOT:
- an amend of historical D4-A8;
- D4-A9 (scientific execution);
- D4-A8-V1;
- production activation;
- a retrieval execution or provider call run.

Historical D4-A8 is preserved immutable as a historical record reclassified as:
`HISTORICAL / PARTIAL / TARGETED_REVALIDATION_COHORT_PREREGISTERED / THREE_SYMBOL_RETIREMENT_SENSITIVITY_INSUFFICIENT`.

---

## 1. Exact Scientific Defect Repaired

Historical D4-A8 established a targeted scientific revalidation direction for `model_factory_theory` but contained a substantive scientific contract defect:
> **Historical Defect:** D4-A8 allowed a single treatment-active direct case (`g031`) to authorize a retirement-validated outcome for all three symbol components of `model_factory_theory`:
> - `model/PndLmdDPMAngModel1D.cxx`
> - `model/PndLmdDPMAngModel2D.cxx`
> - `model/PndLmdModelFactory.cxx`
> even though `g031`'s critical evidence group (`g031.e1`) is sensitive only to `model/PndLmdModelFactory.cxx` (`generateModel`), while `g032` (requiring `PndLmdDPMAngModel1D.cxx`) and `g033` (requiring `PndLmdDPMAngModel2D.cxx`) do NOT match `model_factory_theory` under production query expansion rules and thus function purely as nonmatching no-op controls.

Under scientific principles of evidence-grounded validation:
1. No symbol component can ever receive a retirement-validating disposition unless it has explicit treatment-active direct critical-evidence coverage frozen before outcome exposure.
2. Nonmatching controls are safety sentinels only; their evidence retention can detect generic regressions, but cannot authorize retirement of the locators they mention.
3. The future treatment mask must be derived strictly from covered symbol components (`COVERED_SYMBOL_MASK`), while uncovered components (`UNCOVERED_SYMBOL_HOLD_MASK`) and paper page hints (`PAGE_HINT_HOLD_MASK`) remain strictly on `HOLD`.

---

## 2. Mechanical Component-Sensitive Coverage Audit

A mechanical audit was executed across all questions in the formal benchmark (`evaluation/benchmarks/v2_6/gold_questions.yaml`) and novel dev dataset (`evaluation/novel/v1/novel_dev.yaml`) using the production query expansion matcher `select_matching_query_expansions` from `panda_agent.d3_structured`.

### 2.1 Per-Component Coverage Findings

| Symbol Component | Deterministic Match | Approved English Benchmark Case | Critical Evidence Group | Coverage Status | Targetable in A9 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `model/PndLmdModelFactory.cxx` | Matches `model_factory_theory` | `g031` (`api`, approved, `en`) | `g031.e1` (`generateModel`) | `DIRECT_TREATMENT_COVERAGE_FOUND` | **YES (`COVERED_SYMBOL_MASK`)** |
| `model/PndLmdDPMAngModel1D.cxx` | **NO MATCH** (`g032` query does not match) | None (no approved English question matches) | `g032.e1` (adjacent nonmatching) | `DIRECT_TREATMENT_COVERAGE_GAP` | **NO (`UNCOVERED_SYMBOL_HOLD_MASK`)** |
| `model/PndLmdDPMAngModel2D.cxx` | **NO MATCH** (`g033` query does not match) | None (no approved English question matches) | `g033.e1` (adjacent nonmatching) | `DIRECT_TREATMENT_COVERAGE_GAP` | **NO (`UNCOVERED_SYMBOL_HOLD_MASK`)** |

### 2.2 Mechanically Derived Target Masks

- **`COVERED_SYMBOL_MASK`**:
  ```yaml
  - model/PndLmdModelFactory.cxx
  ```
- **`UNCOVERED_SYMBOL_HOLD_MASK`**:
  ```yaml
  - model/PndLmdDPMAngModel1D.cxx
  - model/PndLmdDPMAngModel2D.cxx
  ```
- **`PAGE_HINT_HOLD_MASK`**:
  ```yaml
  pflueger_2017: [51, 57, 65]
  ```

---

## 3. Formal Cohort and Case Roles

The formal case cohort is derived deterministically from the direct cases needed for `COVERED_SYMBOL_MASK` plus the frozen no-op controls:

1. **`g031`** (`DIRECT_MODEL_FACTORY_TREATMENT_CASE`):
   - Query: `"How does PndLmdModelFactory generate the luminosity model?"`
   - Intent: `api` | Language: `en` | Review status: `approved` | Expected status: `answered`.
   - Matching: matches `model_factory_theory`.
   - Critical evidence: `g031.e1` requiring `model/PndLmdModelFactory.cxx` (`generateModel`).
   - Role: Direct treatment case covering `model/PndLmdModelFactory.cxx`.

2. **`g032`** (`DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL`):
   - Query: `"How is the 1D DPM angular model implemented in PndLmdDPMAngModel1D?"`
   - Intent: `api` | Language: `en` | Review status: `approved` | Expected status: `answered`.
   - Matching: does NOT match `model_factory_theory`.
   - Evidence: `g032.e1` requiring `model/PndLmdDPMAngModel1D.cxx`.
   - Role: Safety sentinel only. Cannot authorize retirement of `PndLmdDPMAngModel1D.cxx`.

3. **`g033`** (`DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL`):
   - Query: `"How is the 2D DPM angular model implemented in PndLmdDPMAngModel2D?"`
   - Intent: `api` | Language: `en` | Review status: `approved` | Expected status: `answered`.
   - Matching: does NOT match `model_factory_theory`.
   - Evidence: `g033.e1` requiring `model/PndLmdDPMAngModel2D.cxx`.
   - Role: Safety sentinel only. Cannot authorize retirement of `PndLmdDPMAngModel2D.cxx`.

4. **`g047`** (`PAGE_HINT_ADJACENT_NONMATCHING_CONTROL`):
   - Query: `"What are the key theoretical assumptions of the DPM model in Pflueger 2017?"`
   - Intent: `algorithm_theory` | Language: `en` | Review status: `approved` | Expected status: `answered`.
   - Matching: does NOT match `model_factory_theory`.
   - Evidence: `g047.e1` requiring `pflueger_2017` page 51.
   - Role: Safety sentinel only.

5. **`g064`** (`EXCLUDED_DIAGNOSTIC`):
   - Language: `zh`. Excluded from the formal English evaluation gate.

---

## 4. Approval-Aware Page-Hint Coverage-Gap Audit

Production `analyze()` drops query-expansion rule page hints unless the accepted intent is `algorithm_theory` or `algorithm_implementation`.

An approval-aware audit of all benchmark and novel dev questions confirmed:
- Zero approved English questions match `model_factory_theory` under `algorithm_theory` or `algorithm_implementation`.
- `page_hint_gap_status = OPEN`.
- `page_hint_gap_result = NO_EXISTING_APPROVED_ENGLISH_CASE_FOUND`.
- `pflueger_2017: [51, 57, 65]` remain strictly on `HOLD`.

---

## 5. Real Frozen-Plan Reusability Audit & Budget Derivation

Rather than relying on a hard-coded stub, an actual static inspection of exposed plan-bearing artifacts was performed across:
- `evaluation/d4_a5_continuation_raw_prospective_plans.json`
- `evaluation/d4_a5_raw_prospective_plans.json`
- `evaluation/d4_a2_v2_raw_plans.json`
- `evaluation/d4_a2_v1_raw_analyzer_plan_samples.json`

Findings:
- None of `g031`, `g032`, `g033`, `g047` appear in any historical plan artifact.
- Reusability classifications:
  - `g031`: `NO_COMPATIBLE_FROZEN_PLAN`
  - `g032`: `NO_COMPATIBLE_FROZEN_PLAN`
  - `g033`: `NO_COMPATIBLE_FROZEN_PLAN`
  - `g047`: `NO_COMPATIBLE_FROZEN_PLAN`
- Counts: $N = 4$ formal cases, $R = 0$ reusable plans, $F = N - R = 4$ fresh plans required.

### Derived Future Provider Budget
- Analyzer calls: $F = 4$
- Embedding calls: $2 \times N = 8$
- Reranker calls: $2 \times N = 8$
- QA / Verifier / Judge / Evaluator calls: 0
- Retries: 0
- Total logical model calls: $F + 4N = 20$.

---

## 6. Real D4-A5 Contribution-Ledger Contract & Projection Semantics

Historical D4-A8 toy schemas (`canonical_plan["contributions"]`) are discarded. Future D4-A9 must consume the authoritative D4-A5 `contribution_ledger` schema:

```json
{
  "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
  "kind": "symbol",
  "value": "model/PndLmdModelFactory.cxx",
  "source_id": null,
  "pdf_page": null,
  "provenance_origin_ids": [
    "model_factory_theory"
  ],
  "origin_types": {
    "model_factory_theory": "reviewed_expansion_rule"
  },
  "plan_present": true
}
```

### Component-Sensitive Treatment Projection
1. For symbols in `COVERED_SYMBOL_MASK` (`model/PndLmdModelFactory.cxx`):
   - If `model_factory_theory` is in `provenance_origin_ids`, subtract that origin.
   - If independent origins remain (e.g. `model_factory_acceptance_methods`), the symbol survives and remains in the projected plan.
   - If no origins remain, the symbol is effectively removed from projected `symbols`.
2. Uncovered symbols (`PndLmdDPMAngModel1D.cxx`, `PndLmdDPMAngModel2D.cxx`) and paper page hints (`pflueger_2017: [51, 57, 65]`) are **NEVER subtracted** and remain untouched (`HOLD`).
3. Controls receive zero selected-origin removals; baseline projection equals treatment projection.

---

## 7. Component Dispositions and Precedence Hierarchy

### 7.1 Per-Component Scientific Dispositions
- `RETIREMENT_VALIDATED_COMPONENT`: Baseline reproduced (T), treatment retained (T), origin subtracted.
- `DEPENDENCY_OBSERVED_RETAIN`: Baseline reproduced (T), treatment lost (F) due to origin subtraction.
- `INCONCLUSIVE_BASELINE_NOT_REPRODUCED`: Direct case baseline failed.
- `INCONCLUSIVE_APPLICABILITY_INCOMPLETE`: Direct case component is `INACTIVE_NOT_IDENTIFIABLE`.
- `HOLD_DIRECT_TREATMENT_COVERAGE_GAP`: Assigned to uncovered symbols without treatment execution.
- `HOLD_OUTSIDE_TREATMENT_SCOPE`: Assigned to held paper page hints.
- `INVALID_PROTOCOL`: Protocol failure or ambiguous applicability.

### 7.2 Overall Outcome Precedence
- **Level 1**: `INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED`
- **Level 2**: `INCONCLUSIVE / ALL_COVERED_COMPONENT_BASELINES_NOT_REPRODUCED`
- **Level 3**: `PARTIAL / DEPENDENCY_OBSERVED_FOR_COVERED_COMPONENTS_RETAIN`
- **Level 4**: `FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION`
- **Level 5**: `INCONCLUSIVE / COVERED_COMPONENT_APPLICABILITY_INCOMPLETE`
- **Level 6**: `PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD`

Full `RETIREMENT_VALIDATED` is strictly unreachable under this repaired contract because uncovered symbols and page hints remain on HOLD.

---

## 8. Immutability and Accounting

- **Production code and configs**: `src/` tree and `configs/` tree are byte-identical to STARTING_HEAD.
- **Historical scientific artifacts**: D4-A4, D4-A5, D4-A6, D4-A7, and historical D4-A8 artifacts are verified against git blob seals and remain immutable.
- **Zero-provider contract**: exactly 0 Analyzer, 0 Embedding, 0 Reranker, 0 QA, 0 Verifier, 0 Judge, 0 Evaluator calls, 0 tokens in D4-A8-R1.
