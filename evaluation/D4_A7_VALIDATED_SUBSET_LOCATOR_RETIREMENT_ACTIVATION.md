# D4-A7 — Validated-Subset Locator-Retirement Production Activation

## 0. Executive Summary

This document records the completed and verified production activation under lifecycle stage `D4-A7`.

Following the preregistration and verification seal established in `D4-A6-R1`, this stage applies the exact locator-retirement mutation to production configuration for the scientifically validated subset of Batch 2 query expansions.

### Key Lifecycle Principles

1. **Clear Separation Between Scientific Validation and Production Activation**:
   - **Scientific validation**: Frozen in `D4-A5` (Level 2 `INCONCLUSIVE / BATCH2_REFERENCE_BASELINE_NOT_REPRODUCED`). The scientific outcome across the entire Batch 2 candidate set remains Level 2 INCONCLUSIVE and is immutable.
   - **Production mapping governance**: Governed by `D4-A6-R1`, which established that the two rules with verified, positive retirement evidence (`effective_acceptance_pipeline` and `root_macro_usage`) are `MIGRATION_ELIGIBLE` for rule-local locator retirement, while `model_factory_theory` remains on strict `HOLD`.
   - **Production activation**: `D4-A7` performs zero new science, zero model calls, and zero recomputation. It is strictly the execution of the authorized configuration changes.

2. **Exact Production Mutation**:
   - Only a single production configuration file is mutated: `configs/query_expansions.yaml`.
   - Zero modifications to runtime Python code under `src/` (`src/panda_agent/config.py`, `src/panda_agent/retrieval.py`, `src/panda_agent/d3_structured.py`, etc.).
   - Exactly two rule-local symbol lists were emptied:
     - `effective_acceptance_pipeline`: `symbols: [macro/target/prod_sim_hvmaps.C, data/PndLmdAcceptance.cxx, model/PndLmdModelFactory.cxx]` -> `symbols: []`.
     - `root_macro_usage`: `symbols: [Running/Macros.html, tools/MasterTasks/PndMasterRunSim.cxx]` -> `symbols: []`.
   - The `structured_replacement` field remains completely absent (and effectively `false`) on both rules.
   - All other fields (`triggers`, `repositories`, `concepts`, and paper page hints `li_2026: [83, 86, 89]`) are strictly preserved.

3. **Held Rule Preserved**:
   - `model_factory_theory` remains completely untouched under its existing production contract.
   - Its symbols (`model/PndLmdDPMAngModel1D.cxx`, `model/PndLmdDPMAngModel2D.cxx`, `model/PndLmdModelFactory.cxx`) and paper hints (`pflueger_2017: [51, 57, 65]`) remain active.

4. **Batch 1 Preserved**:
   - The Batch 1 rules (`event_poca_handoff` and `restgas_profile_workflow`) remain active in production with `symbols: []` and `structured_replacement: true`.

5. **Independent Locator Origins Preserved**:
   - Multi-origin locators continue to be contributed by independent rules across the configuration:
     - `macro/target/prod_sim_hvmaps.C` in `reconstructed_profile_to_acceptance`.
     - `data/PndLmdAcceptance.cxx` in `reconstructed_profile_to_acceptance`.
     - `model/PndLmdModelFactory.cxx` in `model_factory_theory` and `acceptance_model_boundary`.
     - `Running/Macros.html` in `sphinx_operational_architecture`.
     - `tools/MasterTasks/PndMasterRunSim.cxx` in `simulation_configuration_usage`.

6. **Current Production State**:
   - `batch1_active = true`
   - `batch2_validated_subset_production_active = true`
   - `batch2_validated_subset_active_rules = ["effective_acceptance_pipeline", "root_macro_usage"]`
   - `batch2_held_rules = ["model_factory_theory"]`
   - `full_batch2_production_activation = false`

---

## 1. Lineage and Starting Boundary

- **Starting HEAD**: `41ca18f6b3348d7f20bc226867b0d628aaea2187`
- **Starting Message**: `D4-A6-R1 repair validated-subset production mapping contract`
- **Starting Parent**: `b038a9e2ced817231b7a25f98dc106965f1a2688`
- **Preflight Verification**: Executed `d4_a6_r1_locator_retirement_mapping_repair.py --mode verify` at starting HEAD, which confirmed `status = PASS` and `decision = READY_FOR_VALIDATED_SUBSET_LOCATOR_RETIREMENT`.

---

## 2. Production Mutation Details

### 2.1 effective_acceptance_pipeline
```yaml
   - rule_id: effective_acceptance_pipeline
     triggers: ["effective acceptance", "restgas acceptance", "acceptance calculation", "有效接受度", "有效接受度"]
     repositories: [restgas_determination, luminosityfit]
-    symbols: [macro/target/prod_sim_hvmaps.C, data/PndLmdAcceptance.cxx, model/PndLmdModelFactory.cxx]
+    symbols: []
     concepts: [profile-dependent effective acceptance pipeline]
     paper_page_hints:
       li_2026: [83, 86, 89]
```

### 2.2 root_macro_usage
```yaml
   - rule_id: root_macro_usage
     triggers: ["ROOT macro", "macro execution", "run a ROOT macro"]
     repositories: [pandaroot]
-    symbols: [Running/Macros.html, tools/MasterTasks/PndMasterRunSim.cxx]
+    symbols: []
     concepts: [PandaRoot macro invocation]
```

---

## 3. Immutability and Audit Seals

1. **Production Code Immutability**:
   - `tree(HEAD:src) == tree(R1_HEAD:src)`: Byte-identical, zero modifications.
2. **Configuration Change Scope**:
   - `git diff --name-only R1_HEAD HEAD -- configs` yields strictly `configs/query_expansions.yaml`.
3. **Historical Authority Blob Seals**:
   - All 5 D4-A6-R1 authority files are Git blob identical between HEAD and `R1_HEAD`:
     - `evaluation/d4_a6_r1_decision.json`
     - `evaluation/d4_a6_r1_locator_retirement_mapping_preregistration.json`
     - `evaluation/D4_A6_R1_LOCATOR_RETIREMENT_MAPPING_REPAIR.md`
     - `evaluation/scripts/d4_a6_r1_locator_retirement_mapping_repair.py`
     - `tests/unit/test_d4_a6_r1_locator_retirement_mapping_repair.py`
4. **Cumulative Diff Exact 7 Paths**:
   - `configs/query_expansions.yaml`
   - `docs/EVALUATION_STATUS.md`
   - `docs/GENERALIZATION_ROADMAP.md`
   - `evaluation/D4_A7_VALIDATED_SUBSET_LOCATOR_RETIREMENT_ACTIVATION.md`
   - `evaluation/d4_a7_validated_subset_locator_retirement_activation.json`
   - `evaluation/scripts/d4_a7_validated_subset_locator_retirement_activation.py`
   - `tests/unit/test_d4_a7_validated_subset_locator_retirement_activation.py`

---

## 4. Zero Provider Accounting

- Analyzer calls: 0
- Embedding calls: 0
- Reranker calls: 0
- QA calls: 0
- Verifier calls: 0
- Judge calls: 0
- Scientific evaluator calls: 0
- Retrieval cells: 0
- Database / Qdrant writes: 0
- Provider attempts: 0
- Tokens consumed: 0

---

## 5. Verification Verdict and Next Steps

- **Status**: `PASS`
- **Decision**: `VALIDATED_SUBSET_LOCATOR_RETIREMENT_ACTIVATED`
- **Next Stage**: Explicit STOP. No `D4-A8` is created. Any future work requires separate explicit authorization.
