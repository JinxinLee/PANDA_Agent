# D4-A6 — Validated-Subset Batch2 Runtime Migration Preregistration Report

- **Status**: `READY_FOR_VALIDATED_SUBSET_MIGRATION`
- **Starting HEAD**: `7b9d9d13903d874c000c0097304bfccc19dbbf65`
- **Parent Closeout Commit**: `c33f4cbe0bc2dfe6352d70396ebbdc203d3c624f`
- **Scientific Verdict Preserved**: `Level 2 INCONCLUSIVE / BATCH2_REFERENCE_BASELINE_NOT_REPRODUCED`

---

## 1. Executive Summary

D4-A6 translates the frozen D4-A5 per-rule scientific dispositions into an exact, auditable, prospective production-migration contract for the scientifically validated subset of Batch 2:
- **`effective_acceptance_pipeline`**: `RETIREMENT_VALIDATED` → **`MIGRATION_ELIGIBLE`**
- **`root_macro_usage`**: `RETIREMENT_VALIDATED` → **`MIGRATION_ELIGIBLE`**
- **`model_factory_theory`**: `INCONCLUSIVE_BASELINE_NOT_REPRODUCED` → **`HOLD`**

This stage performs **zero production mutation** and **zero scientific re-execution**.

---

## 2. Governance Basis & Rule-Local Migration

Under the repaired D4-A5-R1 governance contract:
1. Component-level applicability and per-rule scientific dispositions dictate migration eligibility.
2. An overall Level-2 INCONCLUSIVE batch verdict does not block rule-local migration of rules whose masks were fully validated (`RETIREMENT_VALIDATED`).
3. Rules with non-reproduced baselines (`model_factory_theory`) remain strictly held in production.
4. The existing generic structured-replacement runtime mechanism (`Retriever.retrieve()` + `d3_5_selectivity_v2` + `k=3` bounded admission) operates rule-locally via `structured_replacement: true` in `configs/query_expansions.yaml` without requiring any new generic mechanism or all-or-nothing coupling.

---

## 3. Mask Accounting & Occurrence Audit

### 3.1 `effective_acceptance_pipeline`
- **Retired Symbols (3)**:
  - `macro/target/prod_sim_hvmaps.C`
  - `data/PndLmdAcceptance.cxx`
  - `model/PndLmdModelFactory.cxx`
- **Preserved Paper Hints**:
  - `li_2026: [83, 86, 89]`
- **Independent Origin Nuance**:
  - In D4-A5, `active_component_count = 3`, `effective_removal_count = 1`.
  - The other two symbols survive in treatment projections via `reconstructed_profile_to_acceptance`.
  - Migration removes only this rule's contribution; `reconstructed_profile_to_acceptance` continues to contribute them independently.

### 3.2 `root_macro_usage`
- **Retired Symbols (2)**:
  - `Running/Macros.html`
  - `tools/MasterTasks/PndMasterRunSim.cxx`

### 3.3 `model_factory_theory` (HOLD)
- **Held Symbols (3)**:
  - `model/PndLmdDPMAngModel1D.cxx`
  - `model/PndLmdDPMAngModel2D.cxx`
  - `model/PndLmdModelFactory.cxx`
- **Held Paper Hints**:
  - `pflueger_2017: [51, 57, 65]`
- **Reason**: Active direct-rule evidence group `n014.e1` failed to reproduce baseline; `n003.e2` is a separate nonmatching-control finding.
- **Occurrence Safety**: `model/PndLmdModelFactory.cxx` under `model_factory_theory` is preserved and untouched even though it is retired under `effective_acceptance_pipeline`.

---

## 4. Prospective Production Diff

```diff
--- a/configs/query_expansions.yaml
+++ b/configs/query_expansions.yaml
@@ -129,8 +129,9 @@
   - rule_id: effective_acceptance_pipeline
     triggers: ["effective acceptance", "restgas acceptance", "acceptance calculation", "有效接受度", "有效接受度"]
     repositories: [restgas_determination, luminosityfit]
-    symbols: [macro/target/prod_sim_hvmaps.C, data/PndLmdAcceptance.cxx, model/PndLmdModelFactory.cxx]
+    symbols: []
     concepts: [profile-dependent effective acceptance pipeline]
+    structured_replacement: true
     paper_page_hints:
       li_2026: [83, 86, 89]
 
@@ -181,8 +182,9 @@
   - rule_id: root_macro_usage
     triggers: ["ROOT macro", "macro execution", "run a ROOT macro"]
     repositories: [pandaroot]
-    symbols: [Running/Macros.html, tools/MasterTasks/PndMasterRunSim.cxx]
+    symbols: []
     concepts: [PandaRoot macro invocation]
+    structured_replacement: true
 
   - rule_id: restgas_workflow_usage
     triggers: ["two-pass reconstruction workflow", "restgas two-pass reconstruction"]

```

---

## 5. Decision & Next Stage

- **Decision**: `READY_FOR_VALIDATED_SUBSET_MIGRATION`
- **Batch 1 Status**: `ACTIVE`
- **Batch 2 Full Activation**: `false`
- **Next Authorized Stage**: `D4-A7 (Validated-Subset Runtime Migration Activation)` — requires explicit separate authorization.
