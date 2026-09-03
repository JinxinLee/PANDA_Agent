# PANDA Agent — D4-A2-R1: Critical-Regression Diagnosis & Repair Decision

## 1. Executive Decision

```text
D4-A2-R1 LIFECYCLE DECISION =
PASS / BENCHMARK_CORRECTION_AND_REGRESSION_ATTRIBUTION_COMPLETE

EVALUATION BOUNDARY:
  MODEL_CALLS = 0
  RETRIEVAL_RUNS = 0
  PROTECTED_DATASET_ACCESS = 0

HISTORICAL D4-A2 VERDICT =
COMPLETE / FAIL / CRITICAL_OR_GROUNDING_REGRESSION (IMMUTABLE)

FORWARD-CORRECTED CONTRACT CRITICAL REGRESSIONS = 1 (n022.e2)
FORWARD-CORRECTED NONCRITICAL REGRESSIONS = 1 (g021.e2)

n022.e2 ATTRIBUTION TAXONOMY =
ORDINARY_FRESH_RUN_VARIANCE_DOMINATED
(Preferred wording: fresh-run ordinary retrieval divergence)

n022.e2 FIRST DIVERGENCE LAYER =
Layer 1 — Query Analyzer / retrieval plan (concept extraction variance)

REPAIR-OWNER DECISION:
  g021.e2: BENCHMARK_CONTRACT (Completed in R1)
  n022.e2: QUERY_ANALYZER (Mechanistic divergence origin) /
           NO_GENERIC_REPAIR_YET (No immediate architecture/fusion modification;
           paired stability/attribution validation required)

PRODUCTION_ACTIVATION = false
FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED
D4-A3 = NOT_STARTED / BLOCKED

EXACT NEXT LIFECYCLE STAGE =
D4-A2-V1 — Paired Retrieval Stability and Variance Attribution Validation
(NOT_STARTED / SEPARATELY_AUTHORIZED)
```

---

## 2. Historical D4-A2 State

The predecessor stage **D4-A2 (First-Batch Before/After Validation)** completed with the authoritative frozen verdict:

```text
D4-A2 = COMPLETE / FAIL / CRITICAL_OR_GROUNDING_REGRESSION
TARGET_REPLACEMENT_REPRODUCED = 2 / 2
BATCH1_FIXED_LOCATOR_DEPENDENCY_REMOVED = 2 / 2
CRITICAL_GROUP_REGRESSIONS = [n022.e2, g021.e2]
PRODUCTION_ACTIVATION = false
```

Pre-exposure implementation freeze commit: `1bda8cbfe393c30a74581bed1411573100487ea2`  
Raw outcome freeze commit: `bbbea0eac8ce3badf42b4832f36487520354ecee`  
Scientific closeout commit: `9220c744126d0db9365006c9896cfd44abfc9d34`

Historical truth remains immutable. The historical raw traces (`evaluation/d4_a2_raw_before_after_results.json`), evaluator results (`evaluation/d4_a2_evaluator_results.json`), result artifact (`evaluation/d4_a2_result.json`), and comprehensive human report (`evaluation/D4_A2_FIRST_BATCH_BEFORE_AFTER_VALIDATION.md`) are immutable historical evidence and have **not** been retroactively altered.

---

## 3. Why R1 Exists

Subsequent human expert review established that the two historical critical regressions cannot be treated identically:

```text
g021.e2 =
VALID_SUPPORTING_EVIDENCE /
CRITICALITY_OVER_SPECIFIED_FOR_CURRENT_QUESTION

n022.e2 =
VALID_REQUIRED_CRITICAL_EVIDENCE /
MECHANISTIC_ATTRIBUTION_REQUIRED
```

Treating both regressions as architectural failures of generic structured replacement would lead to erroneous architecture churn. Stage **D4-A2-R1** was authorized to execute exactly two scientific tasks:
1. Apply a forward-only benchmark contract correction for `g021.e2`, removing its mandatory-critical status while preserving it as supporting evidence;
2. Determine the first meaningful divergence explaining `n022.e2` using only the frozen D4-A2 raw traces and deterministic offline reconstruction, without invoking models or running fresh retrieval.

---

## 4. Evidence-Requirement Review

### 4.1 `n021.e2` (`detectors/lmd/CMakeLists.txt`)
- **Question**: "I want to trace the LMD workflow across PandaRoot and LuminosityFit. Where does PandaRoot implement the LMD simulation, digitization, and reconstruction side, and which LuminosityFit scripts orchestrate simulation/reconstruction and then the luminosity fit?"
- **Role**: `pandaroot_lmd_implementation_ownership`
- **Decision**: `REQUIRED_CRITICAL`
- **Rationale**: The question explicitly asks for the PandaRoot-side implementation ownership in addition to the LuminosityFit orchestration scripts.
- **Selector Breadth Review**: `POSSIBLY_NARROW_BUT_NOT_A_D4_A2_BLOCKER`.
- **Action in R1**: Left **byte-unchanged** in `evaluation/novel/v1/novel_dev.yaml`.

### 4.2 `n022.e2` (`macro/target/poca_step2_analysis.py`)
- **Question**: "The restgas analysis determines the event vertex through a two-step POCA workflow. What does the first worker step leave behind for the second analysis step, and how is the fitted vertex fed into the reprocessing?"
- **Role**: `step2_artifact_consumption`
- **Decision**: `REQUIRED_CRITICAL`
- **Rationale**: The question explicitly asks what the first worker step leaves behind for the second analysis step and how the fitted vertex is fed into reprocessing. `poca_step2_analysis.py` directly implements reading the vertex file produced by step 1 (`get_vertex_from_file`) and orchestrating the reprocessing parameters.
- **Action in R1**: Left **byte-unchanged** in `evaluation/novel/v1/novel_dev.yaml`. No downgrade, deletion, or broadening.

### 4.3 `g021.e2` (`pgenerators/Target/PndTargetGenerator.cxx`)
- **Question**: "How is restgas_profile supplied to distributed-target simulation?"
- **Role**: `pnd_target_generator_implementation`
- **Decision**: `VALID_SUPPORTING_EVIDENCE / NONCRITICAL_FOR_CURRENT_QUESTION`
- **Rationale**: The question asks how the configuration key `restgas_profile` is supplied to distributed-target simulation. The direct core evidence is `macro/target/prod_sim_hvmaps.C` (`g021.e1`), which receives the configuration parameter, configures `TargetMode=8`, and passes it to the simulation runner. `PndTargetGenerator.cxx` (`g021.e2`) reflects the internal generator implementation of how the density profile is parsed and sampled. While valid supporting evidence, it is not mandatory-critical for answering how the profile is supplied.

---

## 5. `g021` Benchmark Correction

A consistent forward-only benchmark contract correction was applied to `evaluation/benchmarks/v2_6/gold_questions.yaml` for `g021`:

| Contract Element | Role / Text | Pre-R1 Criticality | Post-R1 Criticality | Status |
|---|---|---|---|---|
| `g021.e1` | `prod_sim_hvmaps_implementation` (`macro/target/prod_sim_hvmaps.C`) | `true` | `true` | Retained Critical |
| `g021.e2` | `pnd_target_generator_implementation` (`pgenerators/Target/PndTargetGenerator.cxx`) | `true` | `false` | Relaxed to Supporting |
| Answer Point `p1` | Identify `restgas_profile` as concrete density input | `true` | `true` | Retained Critical |
| Answer Point `p2` | Explain macro enabling distributed-target mode & run path | `true` | `true` | Retained Critical |
| Answer Point `p3` | Explain `PndTargetGenerator` density sampling | `true` | `false` | Relaxed to Supporting |
| Identifier | `PndTargetGenerator` (`code_symbol`) | `true` | `false` | Relaxed to Supporting |

`g021.e2`, answer point `p3`, and identifier `PndTargetGenerator` remain present and scored as required/supporting elements, but no longer generate an independent mandatory critical-evidence failure.

---

## 6. Historical-vs-Forward Contract Boundary

- **Provenance Label**: `POST_D4_A2_FORWARD_ONLY_BENCHMARK_CONTRACT_CORRECTION`
- **Historical Evidence**: Immutable commit-addressable evidence is preserved. D4-A2 raw, evaluator, result, and report artifacts are unchanged.
- **Contract Boundary**: D4-A2 was executed against the pre-exposure frozen benchmark contract and historically failed with 2 critical regressions. R1 provides a forward contract correction for future runs and a post-hoc diagnostic re-evaluation of frozen traces.

---

## 7. `n022` BEFORE/AFTER Raw Trace Comparison

The two frozen formal cells from `evaluation/d4_a2_raw_before_after_results.json` were inspected:
- Cell 1: `n022 / BEFORE_COMPAT` (slot 16)
- Cell 2: `n022 / AFTER_BATCH1_REPLACEMENT` (slot 20)

### Target Evidence Candidates in Corpus
The selector `path: macro/target/poca_step2_analysis.py` matches 8 knowledge objects in the corpus:
- `object.10de6bfa07d20258e308d379`: `get_vertex_from_file` (lines 14–41)
- `object.88f0fa939d8a56760c9d44c4`: `main` (lines 95–156)
- `object.680ec8c4923afd75cc85f593`: `run_poca_analysis_steps` (lines 43–93)
- `object.1016250c6407105b7be17e37`: `get_paths` (lines 56–59)
- `object.bceaba21c5feba37017d7a1e`: `check_and_run` (lines 7–12)
- `object.413e0577242baebffee4aba6`: top-level region 1 (lines 1–5)
- `object.1aa2717d5980f5976c3ff5cc`: top-level region 2 (lines 158–159)
- `object.b3373cf8ef5733fbcf7521b5`: full file (lines 1–159)

---

## 8. First-Divergence Analysis

Following the mandatory comparison order:

### Layer 0 — Treatment Applicability
- `matched_query_expansion_rules`: `[]` in BEFORE, `[]` in AFTER.
- `target_batch1_rules_triggered`: `false` in both arms (neither `event_poca_handoff` nor `restgas_profile_workflow` matched query tokens).
- `effective_suppressed_components`: `{}`.
- **DID_BATCH1_COMPONENT_MASK_DIRECTLY_CHANGE_N022_EXPANSION_INPUTS?**  
  **`false`**. The in-memory mask had zero direct effect on `n022`.

### Layer 1 — Query Analyzer / Retrieval Plan
- Intent: `data_flow` in both arms.
- Target repositories: `["luminosityfit", "pandaroot", "restgas_determination"]` in both arms.
- Symbols: `[]` in both arms.
- **Concepts**:
  - `BEFORE_COMPAT`: `["restgas analysis", "event vertex", "POCA workflow", "worker step", "fitted vertex", "reprocessing"]` (6 concepts)
  - `AFTER_BATCH1_REPLACEMENT`: `["restgas analysis", "event vertex", "two-step POCA workflow", "reprocessing"]` (4 concepts)
- **Classification**: **`PLAN_DIVERGENCE`**.
  The LLM Query Analyzer exhibited run-to-run concept extraction divergence: BEFORE extracted "worker step" and "fitted vertex"; AFTER extracted "two-step POCA workflow" but omitted "worker step" and "fitted vertex".

### Layer 2 — Ordinary Recall Channels
- **`exact` Channel**:
  - Query terms in `_exact` are derived from `[*plan.symbols, *plan.concepts]`.
  - In BEFORE: "worker step" and "fitted vertex" triggered text matches that retrieved `object.10de6bfa07d20258e308d379` (`get_vertex_from_file`) at **rank 9 / 20**.
  - In AFTER: neither "worker step" nor "fitted vertex" was in `plan.concepts`. The channel returned only 12 items, and `object.10de6bfa07d20258e308d379` was **not recalled**.
- **`sparse` Channel**:
  - Both arms retrieved `object.88f0fa939d8a56760c9d44c4` (`main`) at **rank 17 / 20** (identically).
- **`dense`, `workflow`, `graph` Channels**:
  - Neither target object was recalled by dense, workflow, or graph channels in either arm.

### Layer 3 — Structured Graph Contribution
- In AFTER: 4 mentions resolved to D2 seeds; reachability traversed 23 graph nodes; 3 bridge candidates were eligible (`ana_dpm.C`, `prod_aod_complete.C`, `pid_complete.C`), but all 3 were **gate-rejected** by `d3_5_selectivity_v2`.
- Selected bridge candidates: 0. Reserved candidates: 0. Displaced candidates: 0.
- Channel `graph` contained 2 reached data products (`event_poca`, `pid_final_root`). Structured additions did not bridge to `poca_step2_analysis.py` and did not displace any target candidates.

### Layer 4 — Fusion
- In BEFORE:
  - `object.10de6bfa07d20258e308d379` received RRF score `2.0 / (60 + 9) = 0.028986` from `exact`, placing it at **fused rank 18** (in top-30: `true`).
  - `object.88f0fa939d8a56760c9d44c4` received RRF score `1.0 / (60 + 17) = 0.012987` from `sparse`, placing it at **fused rank 46** (in top-30: `false`).
- In AFTER:
  - `object.10de6bfa07d20258e308d379` was absent from all channels (score `0.0`).
  - `object.88f0fa939d8a56760c9d44c4` received score `0.012987` from `sparse`, placing it at **fused rank 40** (below top-30 cutoff of score `0.015385`).

### Layer 5 — Reserved Admission
- In BEFORE: `object.10de6bfa07d20258e308d379` was in the final pool at rank 18.
- In AFTER: target candidates were already absent from top-30 prior to admission. Bounded admission reserved 0 candidates and displaced 0 candidates.

### Layer 6 — Reranker / Final Selector
- In BEFORE: `object.10de6bfa07d20258e308d379` was ranked 3 by the reranker and selected as final evidence item 2 (retained).
- In AFTER: target never reached the rerank pool. Downstream reranker / final selector layers did not cause the loss.

**First Divergence Finding**: The earliest scientifically meaningful divergence occurred at **Layer 1 — Query Analyzer / retrieval plan**, where stochastic concept extraction variance between the two single runs determined whether "worker step" and "fitted vertex" entered the `exact` retrieval channel.

---

## 9. Offline Counterfactual Reconstruction

A deterministic, zero-model offline counterfactual was executed over the frozen AFTER cell:

$$\text{AFTER\_NO\_STRUCTURED\_COMPETITION}$$

- **Method**: Removed all structured graph channel additions from AFTER ordinary retrieval; recomputed RRF fusion using the frozen weights (`exact=2.0`, `dense=1.0`, `sparse=1.0`, `paper=1.15`, `workflow=1.2`).
- **Result**:
  - `object.88f0fa939d8a56760c9d44c4` (`main`) remained at **rank 40** (score `0.012987`), well below the counterfactual top-30 cutoff of rank 30 (score `0.014706`).
  - `object.10de6bfa07d20258e308d379` (`get_vertex_from_file`) remained **absent** from all channels (score `0.0`).
- **Counterfactual Answer**: **NO**, `n022.e2` does not re-enter the fused top-30 under AFTER ordinary retrieval results even when structured competition is completely removed. Generic structured competition was not the cause of the loss.

---

## 10. Attribution Decision

Based on the attribution taxonomy:

```text
n022_attribution_class =
ORDINARY_FRESH_RUN_VARIANCE_DOMINATED
(Preferred wording: fresh-run ordinary retrieval divergence)
```

**Justification**:
1. Batch-1 direct component mask was not the cause (`matched_query_expansion_rules = []`);
2. In AFTER, the target evidence failed the top-30 cutoff in ordinary retrieval alone;
3. In the faithful zero-model counterfactual (`AFTER_NO_STRUCTURED_COMPETITION`), removing structured additions did not restore the target to the top-30;
4. The loss originated in stochastic concept extraction variance in the Query Analyzer between single runs.

---

## 11. Generic Repair-Owner Decision

- For `g021.e2`:
  ```text
  REPAIR_OWNER = BENCHMARK_CONTRACT
  ```
  Completed in R1 via forward contract correction.

- For `n022.e2`:
  ```text
  MECHANISTIC_DIVERGENCE_OWNER = QUERY_ANALYZER
  REPAIR_DISPOSITION = NO_GENERIC_REPAIR_YET / PAIRED_STABILITY_VALIDATION_REQUIRED
  ```
  Per lifecycle guidelines: when regression is `ORDINARY_FRESH_RUN_VARIANCE_DOMINATED`, do **not** modify structured graph, fusion, or admission policies based on this one observation. A small paired stability/attribution validation must be performed before any architecture or prompt modification.

---

## 12. Forward-Corrected Diagnostic

Re-evaluating the frozen D4-A2 raw results under the forward-corrected contract yields:

### Group Regressions

| Metric | Historical Frozen | Forward-Corrected Diagnostic | Delta |
|---|---|---|---|
| Critical Group Regressions | 2 (`n022.e2`, `g021.e2`) | 1 (`n022.e2`) | -1 |
| Noncritical Group Regressions | 0 | 1 (`g021.e2`) | +1 |
| Grounding Regressions | 0 | 0 | 0 |
| Wrong-Version Regressions | 0 | 0 | 0 |

### Recall Metrics Across Cohort (13 Answered Cases)

| Metric | Arm | Historical Frozen | Forward-Corrected Diagnostic |
|---|---|---|---|
| Critical Final Evidence Recall | BEFORE_COMPAT | 0.820513 (32/39) | 0.820513 (32/39) |
| Critical Final Evidence Recall | AFTER_BATCH1 | 0.756410 (30/39) | 0.794872 (31/39) |
| **Critical Final Recall Delta** | **AFTER - BEFORE** | **-0.064103** | **-0.025641** |
| Final Evidence Recall (All Required) | BEFORE_COMPAT | 0.820513 | 0.820513 |
| Final Evidence Recall (All Required) | AFTER_BATCH1 | 0.756410 | 0.756410 |
| **Final Evidence Recall Delta** | **AFTER - BEFORE** | **-0.064103** | **-0.064103** |

### Gold Subset Diagnostic (7 Answered Cases)

| Metric | BEFORE_COMPAT | AFTER_BATCH1 | Delta |
|---|---|---|---|
| Gold Critical Final Evidence Recall | 1.000000 (21/21) | 1.000000 (21/21) | **0.000000** |
| Gold Critical Regressions Count | 1 (`g021.e2`) | **0** | **-1** |

Under the forward contract, the Gold benchmark subset exhibits **zero** critical evidence regressions and zero critical recall loss.

---

## 13. Lifecycle Decision

```text
D4-A2-R1 DECISION =
PASS / BENCHMARK_CORRECTION_AND_REGRESSION_ATTRIBUTION_COMPLETE
```

Criteria satisfied:
1. `g021` forward correction is internally consistent across evidence groups, answer points, and identifiers;
2. `n022` first-divergence attribution is conclusively supported by frozen raw traces and counterfactual reconstruction;
3. Generic repair owners and non-repair dispositions are explicitly assigned without benchmark-overfitting repairs.

---

## 14. Exact Next Stage

```text
PRODUCTION_ACTIVATION = false
FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED
D4-A3 = NOT_STARTED / BLOCKED

EXACT NEXT LIFECYCLE STAGE =
D4-A2-V1 — Paired Retrieval Stability and Variance Attribution Validation
(NOT_STARTED / SEPARATELY_AUTHORIZED)
```

The next stage must conduct a paired multi-run stability and variance attribution validation on `n022` to isolate analyzer concept-sampling variance from deterministic retrieval and structured competition, before any production runtime migration or D4-A3 progression can occur.
