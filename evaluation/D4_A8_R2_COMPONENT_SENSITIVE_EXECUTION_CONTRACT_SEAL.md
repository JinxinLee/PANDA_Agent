# D4-A8-R2 — Component-Sensitive Model-Factory Execution Contract Seal

## 0. Task Classification and Authority

`D4-A8-R2` is a forward repair lifecycle stage directly child of `D4-A8-R1`.

- Full name: `D4-A8-R2 — Component-Sensitive Model-Factory Execution Contract Seal`
- This is NOT: `D4-A9`, `D4-A8-V1`, `D4-A7-R1`, a production activation, a scientific execution run, or a retrieval run.
- Starting boundary:
  - HEAD: `a357bfc4e0d846cefa295e98c5de0a8b2813cfa0`
  - Exact commit message: `D4-A8-R1 repair component-sensitive revalidation contract`
  - Direct parent: `ae2e744f6a05e711d407a02d0ae276e6e1422809` (`D4-A8 preregister model-factory symbol retirement revalidation`)
  - Clean working tree and index.

Historical lifecycle statuses:
- `D4-A8 = HISTORICAL / PARTIAL / TARGETED_REVALIDATION_COHORT_PREREGISTERED / THREE_SYMBOL_RETIREMENT_SENSITIVITY_INSUFFICIENT`
- `D4-A8-R1 = HISTORICAL / PARTIAL / COMPONENT_SENSITIVE_TARGET_MASK_CORRECT / PROVENANCE_REUSE_AND_EXECUTION_GATE_NOT_FULLY_SEALED`
- `D4-A8-R2 = COMPLETE / PASS / COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEALED`
- `D4-A9 = NOT_STARTED / ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_COMPONENT_SENSITIVE_EXECUTION`

---

## 1. Preservation of Accepted Scientific Target

`D4-A8-R2` preserves verbatim the scientific target mechanically derived in `D4-A8-R1`:

```text
COVERED_SYMBOL_MASK = [
  "model/PndLmdModelFactory.cxx"
]

UNCOVERED_SYMBOL_HOLD_MASK = [
  "model/PndLmdDPMAngModel1D.cxx",
  "model/PndLmdDPMAngModel2D.cxx"
]

PAGE_HINT_HOLD_MASK = {
  "pflueger_2017": [51, 57, 65]
}
```

Formal case cohort roles remain frozen:
- `g031`: `DIRECT_MODEL_FACTORY_TREATMENT_CASE` (covers `model/PndLmdModelFactory.cxx` via critical evidence group `g031.e1` `generateModel`).
- `g032`: `DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL` (adjacent component `model/PndLmdDPMAngModel1D.cxx` via `g032.e1`).
- `g033`: `DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL` (adjacent component `model/PndLmdDPMAngModel2D.cxx` via `g033.e1`).
- `g047`: `PAGE_HINT_ADJACENT_NONMATCHING_CONTROL` (adjacent page hint `pflueger_2017` page 51 via `g047.e1`).
- `g064`: Excluded diagnostic case (language `zh`, excluded from formal English benchmark gate).

Both DPM symbols and all Pflueger page hints remain strictly on `HOLD`. Future `D4-A9` (if authorized) can only validate the single covered symbol `model/PndLmdModelFactory.cxx`.

---

## 2. Defects in R1 Repaired by R2

`D4-A8-R2` repairs six substantive execution-contract defects identified in `D4-A8-R1`:

### 2.1 Real Provenance Model and Strict A5 Pure-Helper Binding
`D4-A8-R1` used a simplified ledger reconstruction primarily supporting query-expansion rules. In `D4-A8-R2`, silent fallback was eliminated and execution contracts are mechanically bound to the frozen `D4-A5` authority (`evaluation/scripts/d4_a5_batch2_controlled_retirement_validation.py`):
- Direct binding to pure A5 helpers: `build_contribution_ledger`, `validate_ledger_coverage`, `classify_component_applicability`, `build_retirement_projection_r1`, `compute_plan_signature`, `build_batch2_mask_entries`, `build_retirement_projection`.
- Origin typing gate (`validate_origin_type_consistency`): strict validation ensuring exact bijection between `provenance_origin_ids` and `origin_types`, with strict typing for `reviewed_expansion_rule`, `accepted_analyzer_semantic_output`, and `production_deterministic_override`.
- Mechanical equivalence fixtures: proves sole-origin subtraction, survival of Analyzer semantic delta (`accepted_analyzer_semantic_delta`), survival of independent reviewed rules (`model_factory_acceptance_methods`), and survival of runtime deterministic override (`li_2026#141`).

### 2.2 Complete Plan-Reuse Compatibility Contract
`D4-A8-R1` checked minimal fields. `D4-A8-R2` enforces the complete frozen plan contract with internal consistency:
- Exact `case_id` and query matching
- Complete `canonical_plan` schema (`symbols`, `concepts`, `target_repositories`, `paper_page_hints`)
- Canonical serialization internal consistency: `json.loads(canonical_serialization) == canonical_plan`
- Plan signature internal consistency: `plan_signature == a5.compute_plan_signature(canonical_plan)`
- Provider model contract explicit validation: `model_id == "gemini-3.8-flash"`, `temperature == 0.0`, `location == "global"`, `retries == 0`
- Matched-rule behavior compatibility: verifies historical matched rules match runtime query expansion selection for the gold question
- Complete `contribution_ledger` verified via `a5.validate_ledger_coverage` and `validate_origin_type_consistency`
- Provenance origin receipts and component applicability receipts

### 2.3 Reusable/Fresh Partition Support (No False All-Fresh Gate)
`D4-A8-R1` incorrectly required `all_require_fresh_acquisition == true` to PASS. `D4-A8-R2` accepts any valid partition $N = R + F$. If reusable plans exist, they must be reused; if absent, fresh acquisition is preregistered.

### 2.4 Unified Formal Case Eligibility Classifier
`D4-A8-R2` establishes `classify_formal_case_eligibility` as the single authority across Gold and Novel datasets:
- Gold: requires `language == "en"`, `review_status == "approved"`, `expected_status == "answered"`, `split in ("dev", "test")`.
- Novel Dev: classified as `DIAGNOSTIC_ONLY` under repository governance (does not possess production gating authority).

### 2.5 Provenance and Projection Compatibility Gates
`D4-A8-R2` proves mechanically that:
- Non-rule origins (`accepted_analyzer_semantic_delta`, `runtime_deterministic_override`) survive target-rule retirement.
- Independent rule origins (e.g. `model_factory_acceptance_methods`) survive target-rule retirement.
- Values are effectively removed if and only if zero origins survive.
- Held components (`model/PndLmdDPMAngModel1D.cxx`, `model/PndLmdDPMAngModel2D.cxx`, `pflueger_2017` page hints) and controls are never mutated.

### 2.6 Fail-Closed Component Evaluator
`D4-A8-R2` ensures that ambiguous provenance (`AMBIGUOUS_INVALID`), contradictory ledgers, or failed treatment constructions automatically produce Level 1 `INVALID_PROTOCOL` rather than falling through to baseline inconclusive or dependency observations. Baseline failure is reserved strictly for actual non-reproduction in the `A7_CURRENT` arm.

### 2.7 Committed Machine Artifacts Consistency Seal
Committed machine artifacts (`preregistration.json` and `result.json`) are verified against live deterministic audit results, ensuring zero drift in masks, cohort order, A5 compatibility flags, reuse decisions, budget, and governance booleans.

---

## 3. Plan-Bearing Artifacts Scan and Reusability Results

The plan reusability audit performed a deterministic scan of all candidate JSON artifacts in `evaluation/`, identifying 18 plan-bearing artifacts:
1. `evaluation/d3_5_a6_phase1_pool_manifest.json`
2. `evaluation/d3_5_a6_phase1_replay_fixture.json`
3. `evaluation/d3_5_a6_phase2_raw_reranker_results.json`
4. `evaluation/d3_5_downstream_replay_fixture.json`
5. `evaluation/d4_a1_execution_manifest.json`
6. `evaluation/d4_a1_raw_three_arm_results.json`
7. `evaluation/d4_a2_execution_manifest.json`
8. `evaluation/d4_a2_raw_before_after_results.json`
9. `evaluation/d4_a2_v1_r1_historical_plan_pair.json`
10. `evaluation/d4_a2_v1_raw_analyzer_plan_samples.json`
11. `evaluation/d4_a2_v2_execution_manifest.json`
12. `evaluation/d4_a2_v2_r3_execution_manifest.json`
13. `evaluation/d4_a2_v2_raw_plans.json`
14. `evaluation/d4_a2_v2_raw_results.json`
15. `evaluation/d4_a5_continuation_execution_manifest.json`
16. `evaluation/d4_a5_continuation_raw_paired_retirement_results.json`
17. `evaluation/d4_a5_continuation_raw_prospective_plans.json`
18. `evaluation/d4_a5_execution_manifest.json`

Audit results for formal cohort:
- `g031`: `NO_CANDIDATE_FROZEN_PLAN` (no frozen plan record found in scanned artifacts)
- `g032`: `NO_CANDIDATE_FROZEN_PLAN` (no frozen plan record found in scanned artifacts)
- `g033`: `NO_CANDIDATE_FROZEN_PLAN` (no frozen plan record found in scanned artifacts)
- `g047`: `NO_CANDIDATE_FROZEN_PLAN` (no frozen plan record found in scanned artifacts)

Summary:
- Total formal cases: $N = 4$
- Reusable plans: $R = 0$
- Fresh plans required: $F = 4$
- `plan_reusability_audit_complete = true`

---

## 4. Derived Provider Budget and Paired-Cell Contract

From $N = 4, R = 0, F = 4$:
- Analyzer model calls: $F = 4$
- Embedding model calls: $2 \times N = 8$
- Reranker model calls: $2 \times N = 8$
- QA model calls: $0$
- Verifier model calls: $0$
- Judge model calls: $0$
- Scientific evaluator model calls: $0$
- Retries: $0$
- Total logical model calls: $F + 4N = 4 + 16 = 20$

Paired-cell schedule (8 retrieval cells):
1. `g031`: `A7_CURRENT` / `COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`
2. `g032`: `A7_CURRENT` / `COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`
3. `g033`: `A7_CURRENT` / `COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`
4. `g047`: `A7_CURRENT` / `COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT`

Both arms for each case consume the exact same canonical plan acquired in Phase P. Zero analyzer redraw between arms.

---

## 5. Persistence-Before-Gate Integrity Contract

For any future fresh Analyzer acquisition in `D4-A9`, the system enforces a strict state machine (`transition_execution_state`):
```text
ACQUIRED -> PERSISTED -> GATED -> RETRIEVED
```
Direct jumps (e.g. `ACQUIRED -> GATED` or `ACQUIRED -> RETRIEVED`) are strictly rejected with `StateTransitionError`. The system must persist the complete plan acquisition record before any applicability or provenance gate can stop execution:
- `case_id`
- `question`
- `provider_model_contract`
- `raw_analyzer_response`
- `canonical_plan`
- `canonical_serialization`
- `contribution_ledger`
- `provenance_origin_receipts`
- `component_applicability_receipts`
- `current_execution_projection`
- `treatment_execution_projection`
- `plan_signature`
- `provider_accounting`
- `matched_rule_identities`

---

## 6. Precedence Hierarchy for Outcome Evaluation

1. **Level 1**: `INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED`
   - Triggered by any protocol failure, `AMBIGUOUS_INVALID` applicability, or malformed treatment construction.
2. **Level 2**: `INCONCLUSIVE / ALL_COVERED_COMPONENT_BASELINES_NOT_REPRODUCED`
   - Triggered only if all covered components fail to reproduce baseline in `A7_CURRENT`.
3. **Level 3**: `PARTIAL / DEPENDENCY_OBSERVED_FOR_COVERED_COMPONENTS_RETAIN`
   - Triggered if any covered component reproduces baseline but loses critical evidence under treatment (T/F).
4. **Level 4**: `FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION`
   - Triggered by control divergence or safety regressions.
5. **Level 5**: `INCONCLUSIVE / COVERED_COMPONENT_APPLICABILITY_INCOMPLETE`
   - Triggered if any covered component has `INACTIVE_NOT_IDENTIFIABLE` applicability.
6. **Level 6**: `PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD`
   - Successful partial outcome when covered component validates retirement (T/T). Full `RETIREMENT_VALIDATED` is strictly unreachable because DPM symbols and page hints are on HOLD.

---

## 7. Changed-File Allowlist and Blob Seals

Exactly seven files are created or modified in `D4-A8-R2`:
1. `docs/EVALUATION_STATUS.md`
2. `docs/GENERALIZATION_ROADMAP.md`
3. `evaluation/D4_A8_R2_COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEAL.md`
4. `evaluation/d4_a8_r2_component_sensitive_execution_preregistration.json`
5. `evaluation/d4_a8_r2_result.json`
6. `evaluation/scripts/d4_a8_r2_component_sensitive_execution_contract_seal.py`
7. `tests/unit/test_d4_a8_r2_component_sensitive_execution_contract_seal.py`

Historical Git-blob seals verified against `a357bfc4e0d846cefa295e98c5de0a8b2813cfa0`:
- `evaluation/D4_A8_R1_COMPONENT_SENSITIVE_REVALIDATION_CONTRACT_REPAIR.md`: `bf5ac0975503716295aab22439536ca8fee6d505`
- `evaluation/d4_a8_r1_component_sensitive_revalidation_preregistration.json`: `a72ca83da8eef6852db03376bdcfef89069e254b`
- `evaluation/d4_a8_r1_result.json`: `8207c55ed44c166c3cc8381aebe09a5a9ab49a3e`
- `evaluation/scripts/d4_a8_r1_component_sensitive_revalidation_contract_repair.py`: `585e95262b267bd5f7418835b7d7fa6d48c9e14c`
- `tests/unit/test_d4_a8_r1_component_sensitive_revalidation_contract_repair.py`: `3b3080fb5e31758e95686095bfd71236875b4ec7`

Production tree immutability:
- `HEAD:src` tree is byte-identical to starting tree.
- `HEAD:configs` tree is byte-identical to starting tree.

Zero provider accounting:
- 0 Analyzer calls, 0 Embedding calls, 0 Reranker calls, 0 QA calls, 0 Verifier calls, 0 Judge calls, 0 Tokens.

`D4-A9` remains strictly `NOT_STARTED`.
