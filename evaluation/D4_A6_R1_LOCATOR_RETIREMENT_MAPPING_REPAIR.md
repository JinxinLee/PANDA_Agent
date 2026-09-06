# D4-A6-R1 — Validated-Subset Locator-Retirement Production Mapping Repair Report

- **Status**: `READY_FOR_VALIDATED_SUBSET_LOCATOR_RETIREMENT`
- **Starting HEAD**: `b038a9e2ced817231b7a25f98dc106965f1a2688` (D4-A6)
- **Starting Message**: `D4-A6 preregister validated-subset Batch2 runtime migration`
- **Direct Parent**: `b038a9e2ced817231b7a25f98dc106965f1a2688`
- **Historical D4-A6 Defect**: `PROSPECTIVE_MAPPING_ADDED_UNVALIDATED_STRUCTURED_REPLACEMENT_BEHAVIOR`

---

## 1. Executive Summary

D4-A6-R1 repairs the D4-A6 prospective production-mapping contract:
1. **Preserves governance conclusion**:
   - `effective_acceptance_pipeline` → **`MIGRATION_ELIGIBLE`**
   - `root_macro_usage` → **`MIGRATION_ELIGIBLE`**
   - `model_factory_theory` → **`HOLD`**
2. **Repairs production mapping**:
   - Supersedes defective mapping (`locator retirement + structured_replacement: true`).
   - Repaired mapping: **`validated selected-rule locator retirement only (symbols: []) + structured_replacement remains false/default`**.
   - No structured replacement field is inserted where absent.

---

## 2. Defect Reproduction & Proofs

- **Frozen D4-A4 Authority**: `structured_replacement_after_retirement = false` on all 3 Batch 2 rules.
- **Frozen D4-A5 Treatment**: `BATCH2_RETIREMENT` subtracted selected-rule locator origins from the shared plan while Batch 2 rules remained `structured_replacement = false` in production.
- **Historical D4-A6 Mismatch**: Proposed `structured_replacement: true` on eligible rules without scientific validation.

---

## 3. Full Config Drift & Independent Origin Seals

- **Full Current-Config Drift Seal**: 6/6 fields (`triggers`, `repositories`, `concepts`, `symbols`, `paper_page_hints`, `structured_replacement`) match frozen D4-A4 baseline with zero drift across all 3 rules.
- **Independent Origins Preserved**: Multi-origin locators (`model/PndLmdModelFactory.cxx`, `macro/target/prod_sim_hvmaps.C`, `data/PndLmdAcceptance.cxx`, etc.) remain independently contributed by other rules.
- **Held Rule Untouched**: `model_factory_theory` remains identical to current production.

---

## 4. Repaired Prospective Production Diff

```diff
--- a/configs/query_expansions.yaml
+++ b/configs/query_expansions.yaml
@@ -129,7 +129,7 @@
   - rule_id: effective_acceptance_pipeline
     triggers: ["effective acceptance", "restgas acceptance", "acceptance calculation", "有效接受度", "有效接受度"]
     repositories: [restgas_determination, luminosityfit]
-    symbols: [macro/target/prod_sim_hvmaps.C, data/PndLmdAcceptance.cxx, model/PndLmdModelFactory.cxx]
+    symbols: []
     concepts: [profile-dependent effective acceptance pipeline]
     paper_page_hints:
       li_2026: [83, 86, 89]
@@ -181,7 +181,7 @@
   - rule_id: root_macro_usage
     triggers: ["ROOT macro", "macro execution", "run a ROOT macro"]
     repositories: [pandaroot]
-    symbols: [Running/Macros.html, tools/MasterTasks/PndMasterRunSim.cxx]
+    symbols: []
     concepts: [PandaRoot macro invocation]
 
   - rule_id: restgas_workflow_usage

```

---

## 5. Decision & Next Stage

- **Decision**: `READY_FOR_VALIDATED_SUBSET_LOCATOR_RETIREMENT`
- **Batch 1 Status**: `ACTIVE`
- **Batch 2 Full Production Activation**: `false`
- **Next Stage**: `D4-A7 (Validated-Subset Runtime Migration Activation)` — requires explicit separate authorization.

---

## 6. Verification Seal Hardening Amend

- **AST Runtime Semantic Audit**: Verified that `Retriever` in `src/panda_agent/retrieval.py` extends symbols rule-locally (`parsed.symbols.extend(rule.symbols)`) and deduplicates post-merge (`parsed.symbols = list(dict.fromkeys(parsed.symbols))`), guaranteeing multi-origin locators survive.
- **Single Authority Prospective Validator**: `validate_prospective_mapping` enforces exact 2-rule symbol list truncation, no added `structured_replacement`, and 100% preservation of all other fields and rules.
- **Git Boundaries & Production Tree Immutability**: Enforces exact commit message (`D4-A6-R1 repair validated-subset production mapping contract`), direct parent (`b038a9e2`), 7-file cumulative diff, Git tree-object immutability for `src` and `configs`, Git blob immutability for D4-A4 authority and D4-A5 scientific artifacts, and immutability of the R1 decision/prereg JSON files.
