# PANDA Agent — D4-A2: First-Batch Before/After Validation Report

## 1. Executive Decision & Scientific Verdict

```text
D4_A2_DECISION = FAIL / CRITICAL_OR_GROUNDING_REGRESSION
D4-A2 = COMPLETE / FAIL / CRITICAL_OR_GROUNDING_REGRESSION
D4 = IN_PROGRESS / INCREMENTAL_QUERY_EXPANSION_MIGRATION
FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED
PRODUCTION_ACTIVATION = false
D4-A3 = NOT_STARTED / BLOCKED_BY_D4_A2_CRITICAL_REGRESSION
EXACT_NEXT_STAGE = D4-A2-R1 — First-Batch Critical-Regression Diagnosis and Repair Decision (separately authorized)

TARGET_REPLACEMENT_REPRODUCED = 2 / 2
BATCH1_FIXED_LOCATOR_DEPENDENCY_REMOVED = 2 / 2
BEFORE_REFERENCE_REPRODUCED = true

CRITICAL_GROUP_REGRESSIONS = 2 (n022.e2, g021.e2)
NONCRITICAL_GROUP_REGRESSIONS = 0
GROUP_RECOVERIES = 0
GROUNDING_REGRESSIONS = 0
WRONG_VERSION_REGRESSIONS = 0
INVALID_PROVENANCE_RECOVERIES = 0

POST_EXPOSURE_MUTATIONS = 0 across all categories
OUTCOME_EXPOSURE = COMPLETE
```

The preregistered and frozen **D4-A2 — First-Batch Before/After Validation** has completed across all 32 formal retrieval cells (16 cases × 2 evaluation-only arms).

The deterministic evaluation confirms:
1. **Target Replacement Reproduced (2 / 2):** Under the `AFTER_BATCH1_REPLACEMENT` arm, both historical D4-A1 primary target groups were successfully retained with valid governed admission witnesses:
   - `g036.e1` (`macro/target/ana_dpm.C`): `BEFORE = True`, `AFTER = True`, admission witness `object.5cae2ceab6e67bb4c9065331` (origin `edge.2e09628416a01ce2461d752a`, reserved under K=3, position 29 in reranker pool, retained in final evidence).
   - `g021.e1` (`macro/target/prod_sim_hvmaps.C`): `BEFORE = True`, `AFTER = True`, admission witness `object.3ab0a90ae68e8ece071a9f22` (origin `edge.ea3a79d222f0ca6cc0e6df72`, reserved under K=3, position 29 in reranker pool, retained in final evidence).
2. **Batch-1 Fixed-Locator Dependency Removed (2 / 2):** Both target rules (`event_poca_handoff` and `restgas_profile_workflow`) confirmed legacy locators active in `BEFORE_COMPAT`, suppressed in `AFTER_BATCH1_REPLACEMENT`, with target evidence retained through generic structured replacement.
3. **Reference Baseline Valid:** The fresh `BEFORE_COMPAT` arm reproduced expected baseline evidence on both target cases (`g036.e1 = True`, `g021.e1 = True`) and showed zero catastrophic reference collapse.
4. **Zero Grounding/Version Violations:** `GROUNDING_REGRESSIONS = 0`, `WRONG_VERSION_REGRESSIONS = 0`, `INVALID_PROVENANCE_RECOVERIES = 0`.
5. **Critical Regressions Detected (2):**
   - **`n022.e2`** (novel_dev, role `step2_artifact_consumption`, target path `macro/target/poca_step2_analysis.py`): `BEFORE = True`, `AFTER = False`.
   - **`g021.e2`** (Gold v2.6 dev, role `pnd_target_generator_implementation`, target path `pgenerators/Target/PndTargetGenerator.cxx`): `BEFORE = True`, `AFTER = False`.
6. **Aggregate Metric Losses Exceed Bounded Tolerance:** Across the 13 answered cases, Recall@5 (-0.102564), Recall@10 (-0.064103), Recall@20 (-0.064103), Combined Candidate Recall (-0.153846), Final Evidence Recall (-0.064103), and Critical Final Evidence Recall (-0.064103) all breached the frozen `-0.05` / `0.00` thresholds.
7. **Scientific Verdict:** Under the frozen Section 41 verdict precedence hierarchy, **Level 4 (`FAIL / CRITICAL_OR_GROUNDING_REGRESSION`)** is triggered and takes strict precedence over Level 5 tolerance conditions.
8. **Lifecycle Impact:** First-batch runtime migration is **BLOCKED**. `PRODUCTION_ACTIVATION` remains `false`. D4-A3 is blocked. The next authorized task is diagnostic only: **`D4-A2-R1 — First-Batch Critical-Regression Diagnosis and Repair Decision`**.

---

## 2. Git Lineage & Three-Commit Audit Boundary

The execution followed the mandatory three-commit outcome-exposure audit boundary:

- **Starting HEAD:** `d078be6cbce59d4991100e566b92524458ea2abe` (*D4-A1 close first-batch fixed-locator migration prototype*)
- **Commit A (Implementation Freeze):** `1bda8cbfe393c30a74581bed1411573100487ea2` (*D4-A2 freeze first-batch before-after validation*)
  - Created prior to formal cell #1.
  - Froze execution manifest `evaluation/d4_a2_execution_manifest.json`, preregistration `evaluation/d4_a2_before_after_preregistration.json`, runner script `evaluation/scripts/d4_a2_before_after_validation.py`, and unit tests `tests/unit/test_d4_a2_before_after_validation.py`.
- **Commit B (Raw Outcome Freeze):** `bbbea0eac8ce3badf42b4832f36487520354ecee` (*D4-A2 freeze first-batch raw before-after outcomes*)
  - Created immediately upon completion of all 32 formal cells, prior to running the deterministic evaluator.
  - Froze raw 32-cell execution outputs in `evaluation/d4_a2_raw_before_after_results.json` (98,584 lines, 3.40 MB).
- **Commit C (Final Scientific Closeout):** `GIT_COMMIT_CONTAINING_THIS_ARTIFACT` (*D4-A2 close first-batch before-after validation*)
  - Commits unchanged evaluator output `evaluation/d4_a2_evaluator_results.json`, machine result artifact `evaluation/d4_a2_result.json`, this comprehensive report `evaluation/D4_A2_FIRST_BATCH_BEFORE_AFTER_VALIDATION.md`, and tracking doc updates (`docs/EVALUATION_STATUS.md`, `docs/GENERALIZATION_ROADMAP.md`).

---

## 3. Experimental Cohort & Two-Arm Treatment

### 3.1 Frozen 16-Case Comparison Cohort

The evaluation reused the historical D3 comparison cohort in strict case-major order:

| Index | Case ID | Dataset | Expected Status | Intent | Primary Role in Validation |
| :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `g029` | Gold v2.6 dev | answered | api | Safety control: PndLmdCombinedDataReader |
| 2 | `n021` | novel_dev | answered | cross_repo | Safety control: LuminosityFit + PandaRoot |
| 3 | `g025` | Gold v2.6 dev | insufficient_evidence | troubleshooting | Negative control: runLmdFit execution failure |
| 4 | `g036` | Gold v2.6 dev | answered | implementation | **Primary Target Case 1:** `event_poca_handoff` |
| 5 | `n022` | novel_dev | answered | data_flow | Paraphrase diagnostic: two-pass POCA workflow |
| 6 | `g020` | Gold v2.6 dev | answered | workflow | Safety control: POCA workflow documentation |
| 7 | `n006` | novel_dev | answered | implementation | Safety control: filename helper functions |
| 8 | `g041` | Gold v2.6 dev | insufficient_evidence | api | Negative control: PndPidCorrelator constructor |
| 9 | `n014` | novel_dev | answered | cross_repo | Safety control: Genfit external dependency |
| 10 | `g060` | Gold v2.6 dev | answered | theory | Safety control: divergence smearing model |
| 11 | `g052` | Gold v2.6 dev | answered | theory | Safety control: Li (2026) page 141 formula |
| 12 | `g055` | Gold v2.6 dev | answered | theory | Safety control: Pflueger / Li theory overlap |
| 13 | `n003` | novel_dev | answered | implementation | Safety control: fixed step generator |
| 14 | `g021` | Gold v2.6 dev | answered | implementation | **Primary Target Case 2:** `restgas_profile_workflow` |
| 15 | `n004` | novel_dev | answered | usage | Safety control: ROOT macro execution |
| 16 | `g007` | Gold v2.6 dev | insufficient_evidence | setup_environment | Negative control: FairSoft installation docs |

Cohort composition:
- **Total Cases:** 16
- **Gold v2.6 dev:** 10 cases (7 answered, 3 insufficient_evidence negative controls)
- **novel_dev:** 6 cases (6 answered, 0 negative controls)
- **Formally Applicable Answered Cases:** 13 (participating in retrieval metrics)
- **Negative Controls:** 3 (participating in group retention and grounding safety)

### 3.2 Two Evaluation-Only Arms

1. **`BEFORE_COMPAT`:** Current compatibility reference. Production `configs/query_expansions.yaml` active with all Batch-1 fixed locators present; generic structured replacement inactive; admission budget K = 0.
2. **`AFTER_BATCH1_REPLACEMENT`:** Evaluation-only candidate behavior. Identical query expansion configuration, but suppressing exact Batch-1 fixed locators via in-memory component mask; generic D3.5 structured replacement active; `d3_5_selectivity_v2` active (caps: 8 candidate selectivity cap, 4 per-origin cap); bounded admission budget K = 3; rerank pool size = 30.

### 3.3 Exact Batch-1 Component Masks

- **`event_poca_handoff`:**
  - Suppressed Symbols (4): `macro/target/ana_dpm.C`, `macro/target/prod_aod_complete.C`, `POCA_VERTEX_FILE`, `PndPidCorrelator`
  - Suppressed Paper Page Hints: `li_2026`: [131, 138]
  - Preserved Components: Triggers (`event_poca`, `poca_vertex_file`, `second-pass pid`, `第二遍 pid`), Repositories (`restgas_determination`, `pandaroot`), Concepts (`event POCA handoff`, `event-aligned second-pass propagation`)
- **`restgas_profile_workflow`:**
  - Suppressed Symbols (5): `pgenerators/Target/PndTargetGenerator.cxx`, `macro/target/prod_sim_hvmaps.C`, `macro/target/reco_complete.C`, `macro/target/ana_complete.C`, `macro/target/correction/efficiency_correction_2.C`
  - Suppressed Paper Page Hints: None
  - Preserved Components: Triggers (`restgas_profile`, `restgas profile`, `corrected rho`, `修正后的 rho`), Repositories (`restgas_determination`, `pandaroot`), Concepts (`distributed target generation`, `longitudinal profile correction`)

---

## 4. Execution Accounting & Audit Boundaries

All 32 formal retrieval cells were executed in strict case-major paired order against Google Vertex AI APIs:

```text
FORMAL_CASES = 16
FORMAL_ARMS = 2
FORMAL_CELLS_PLANNED = 32
FORMAL_CELLS_EXECUTED = 32
FORMAL_CELLS_SUCCEEDED = 32
FORMAL_CELLS_FAILED = 0

GOLD_CASES = 10
NOVEL_DEV_CASES = 6
ANSWERED_CASES = 13
INSUFFICIENT_EVIDENCE_CASES = 3

ANALYZER_CALLS = 32
EMBEDDING_CALLS = 32
RERANKER_CALLS = 32
TOTAL_LOGICAL_MODEL_CALLS = 96
PROVIDER_INTERNAL_ATTEMPTS = 96
PROVIDER_RETRIES = 0
TOTAL_TOKEN_USAGE = 633354

QA_CALLS = 0
VERIFIER_CALLS = 0
JUDGE_CALLS = 0

POSTGRESQL_WRITES = 0
QDRANT_WRITES = 0
INGESTION = 0
REINDEX = 0

NOVEL_VALIDATION_RUNS = 0
NOVEL_HOLDOUT_RUNS = 0
PROTECTED_DATASET_ACCESS = 0

POST_EXPOSURE_CASE_MUTATIONS = 0
POST_EXPOSURE_MASK_MUTATIONS = 0
POST_EXPOSURE_REPLACEMENT_MUTATIONS = 0
POST_EXPOSURE_MODEL_MUTATIONS = 0
POST_EXPOSURE_METRIC_MUTATIONS = 0
POST_EXPOSURE_VERDICT_MUTATIONS = 0
```

Models utilized:
- **Query Analyzer & Reranker:** `gemini-3.8-flash` (`temperature = 0.0`, Vertex location `global`)
- **Embedding / Vector Search:** `gemini-embedding-2` (`location = global`)

---

## 5. Target Reproduction & Dependency Removal Verification

Both Batch-1 target groups reproduced successfully under the `AFTER_BATCH1_REPLACEMENT` treatment with verified governed admission witnesses:

### 5.1 Target 1: `g036.e1` (`macro/target/ana_dpm.C`)
- **Rule:** `event_poca_handoff`
- **BEFORE_COMPAT:** Retained (`True`)
- **AFTER_BATCH1_REPLACEMENT:** Retained (`True`)
- **Valid Structured Witness:** `True`
  - Witness Candidate: `object.5cae2ceab6e67bb4c9065331`
  - Provenance Origin: `edge.2e09628416a01ce2461d752a` (relation edge in `restgas_determination`)
  - Selected by Selectivity v2: `True`
  - Reserved under K=3 Admission: `True` (displaced 3 ordinary candidates)
  - Final Rerank Pool Membership: `True` (zero-based position 29)
  - Competed in Reranker: `True`
  - Retained in Final Evidence: `True`
- **Dependency Removal:** Fixed locators active BEFORE, suppressed AFTER, structured mechanism active, target evidence retained. `dependency_removed = True`.

### 5.2 Target 2: `g021.e1` (`macro/target/prod_sim_hvmaps.C`)
- **Rule:** `restgas_profile_workflow`
- **BEFORE_COMPAT:** Retained (`True`)
- **AFTER_BATCH1_REPLACEMENT:** Retained (`True`)
- **Valid Structured Witness:** `True`
  - Witness Candidate: `object.3ab0a90ae68e8ece071a9f22`
  - Provenance Origin: `edge.ea3a79d222f0ca6cc0e6df72` (relation edge in `restgas_determination`)
  - Selected by Selectivity v2: `True`
  - Reserved under K=3 Admission: `True` (displaced 1 ordinary candidate)
  - Final Rerank Pool Membership: `True` (zero-based position 29)
  - Competed in Reranker: `True`
  - Retained in Final Evidence: `True`
- **Dependency Removal:** Fixed locators active BEFORE, suppressed AFTER, structured mechanism active, target evidence retained. `dependency_removed = True`.

### 5.3 Diagnostic Counts
```text
TARGET_REPLACEMENT_REPRODUCED = 2 / 2
BATCH1_FIXED_LOCATOR_DEPENDENCY_REMOVED = 2 / 2
BEFORE_REFERENCE_REPRODUCED = true
```

---

## 6. Quantitative Retrieval Metrics & Threshold Failure

Metrics computed across the 13 applicable answered cases (10 Gold dev - 3 negative controls + 6 novel_dev = 13):

### 6.1 Full Cohort Metrics (13 Answered Cases)

| Metric | BEFORE_COMPAT | AFTER_BATCH1_REPLACEMENT | Absolute Delta | Frozen Tolerance | Threshold Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Recall@5** | 0.730769 | 0.628205 | -0.102564 | >= -0.05 | **FAIL** |
| **Recall@10** | 0.820513 | 0.756410 | -0.064103 | >= -0.05 | **FAIL** |
| **Recall@20** | 0.820513 | 0.756410 | -0.064103 | >= -0.05 | **FAIL** |
| **MRR** | 0.728938 | 0.690476 | -0.038462 | Diagnostic | Diagnostic |
| **Combined Candidate Recall** | 0.897436 | 0.743590 | -0.153846 | >= -0.05 | **FAIL** |
| **Final Evidence Recall** | 0.820513 | 0.756410 | -0.064103 | >= -0.05 | **FAIL** |
| **Critical Final Evidence Recall**| 0.820513 | 0.756410 | -0.064103 | >= 0.00 | **FAIL** |

### 6.2 Subset Metric Breakdown

#### Gold v2.6 dev (7 Answered Cases)
- **Recall@5:** 0.904762 -> 0.761905 (Delta: -0.142857)
- **Recall@10:** 1.000000 -> 0.928571 (Delta: -0.071429)
- **Recall@20:** 1.000000 -> 0.928571 (Delta: -0.071429)
- **MRR:** 0.785714 -> 0.738095 (Delta: -0.047619)
- **Combined Candidate Recall:** 1.000000 -> 0.714286 (Delta: -0.285714)
- **Final Evidence Recall:** 1.000000 -> 0.928571 (Delta: -0.071429)
- **Critical Final Evidence Recall:** 1.000000 -> 0.928571 (Delta: -0.071429)

#### novel_dev (6 Answered Cases)
- **Recall@5:** 0.527778 -> 0.472222 (Delta: -0.055556)
- **Recall@10:** 0.611111 -> 0.555556 (Delta: -0.055556)
- **Recall@20:** 0.611111 -> 0.555556 (Delta: -0.055556)
- **MRR:** 0.662698 -> 0.634921 (Delta: -0.027778)
- **Combined Candidate Recall:** 0.777778 -> 0.777778 (Delta: 0.000000)
- **Final Evidence Recall:** 0.611111 -> 0.555556 (Delta: -0.055556)
- **Critical Final Evidence Recall:** 0.611111 -> 0.555556 (Delta: -0.055556)

### 6.3 Targeted T2 Generalization Diagnostics

- **Gold Final Evidence Recall:** BEFORE = 1.000000, AFTER = 0.928571
- **Novel Final Evidence Recall:** BEFORE = 0.611111, AFTER = 0.555556
- **Gold - Novel Gap:**
  - BEFORE Gap: `0.388889`
  - AFTER Gap: `0.373016`
  - Gap Delta: `-0.015873` (narrowed by 0.016, but solely driven by Gold regression rather than novel improvement)

*Note:* Per Section 30 of the contract, these figures are **TARGETED_T2_GENERALIZATION_DIAGNOSTICS** and do not represent a full release generalization gate.

---

## 7. Group Retention & Regression Breakdown

All 27 required evidence groups across the 16 cases were evaluated under deterministic group matching:

| Case ID | Group ID | Critical | Dataset | Role | BEFORE | AFTER | Retention State |
| :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: |
| `g029` | `g029.e1` | True | Gold | pnd_lmd_combined_data_reader_implementation | True | True | PRESERVED |
| `n021` | `n021.e1` | True | novel | luminosityfit_workflow_scripts | True | True | PRESERVED |
| `n021` | `n021.e2` | True | novel | pandaroot_lmd_implementation_ownership | False | False | UNRESOLVED_BOTH |
| `g025` | `g025.e1` | True | Gold (NC) | run_lmd_fit_implementation | True | True | PRESERVED |
| `g036` | `g036.e1` | True | Gold | ana_dpm_implementation (Target 1) | True | True | PRESERVED |
| `n022` | `n022.e1` | True | novel | pass1_artifact_production | False | False | UNRESOLVED_BOTH |
| `n022` | `n022.e2` | True | novel | step2_artifact_consumption | True | **False** | **REGRESSED** |
| `n022` | `n022.e3` | True | novel | two_pass_workflow_semantics | True | True | PRESERVED |
| `g020` | `g020.e1` | True | Gold | poca_workflow_documentation | True | True | PRESERVED |
| `g020` | `g020.e2` | True | Gold | runall_prod_hvmaps_implementation | True | True | PRESERVED |
| `n006` | `n006.e1` | True | novel | filename_helper_definition | True | True | PRESERVED |
| `n006` | `n006.e2` | True | novel | filename_suffix_literals | False | False | UNRESOLVED_BOTH |
| `g041` | `g041.e1` | True | Gold (NC) | pnd_pid_correlator_interface | True | True | PRESERVED |
| `n014` | `n014.e1` | True | novel | vendored_framework_status | False | False | UNRESOLVED_BOTH |
| `n014` | `n014.e2` | True | novel | native_model_layer | True | True | PRESERVED |
| `g060` | `g060.e1` | True | Gold | pflueger_2017_page_74_theory | True | True | PRESERVED |
| `g060` | `g060.e2` | True | Gold | pnd_lmd_divergence_smearing_model2_d_implementation | True | True | PRESERVED |
| `g060` | `g060.e3` | True | Gold | generate2_dmodel_implementation | True | True | PRESERVED |
| `g052` | `g052.e1` | True | Gold | li_2026_page_141_theory | True | True | PRESERVED |
| `g055` | `g055.e1` | True | Gold | pflueger_2017_page_57_theory | True | True | PRESERVED |
| `g055` | `g055.e2` | True | Gold | li_2026_page_142_theory | True | True | PRESERVED |
| `n003` | `n003.e1` | True | novel | fixed_step_generator_definition | True | True | PRESERVED |
| `n003` | `n003.e2` | True | novel | per_event_step_advancement | False | False | UNRESOLVED_BOTH |
| `g021` | `g021.e1` | True | Gold | prod_sim_hvmaps_implementation (Target 2) | True | True | PRESERVED |
| `g021` | `g021.e2` | True | Gold | pnd_target_generator_implementation | True | **False** | **REGRESSED** |
| `n004` | `n004.e1` | True | novel | fair_logger_documentation | True | True | PRESERVED |
| `g007` | `g007.e1` | True | Gold (NC) | installation_documentation | True | True | PRESERVED |

### Retention Accounting Summary
- **Total Evaluated Groups:** 27
- **PRESERVED Groups:** 19
- **UNRESOLVED_BOTH Groups:** 6
- **GROUP_RECOVERIES:** 0
- **GROUP_REGRESSIONS:** 2 (`n022.e2`, `g021.e2`)
- **CRITICAL_GROUP_REGRESSIONS:** 2 (`n022.e2`, `g021.e2`)
- **NONCRITICAL_GROUP_REGRESSIONS:** 0

---

## 8. Mechanistic Investigation of Critical Regressions

Inspection of the raw traces in `evaluation/d4_a2_raw_before_after_results.json` localizes the stage ownership of both observed critical regressions without overclaiming root cause:

### 8.1 Regression 1: `n022.e2` (`macro/target/poca_step2_analysis.py`)
- **Case / Role:** `n022` (novel_dev) / `step2_artifact_consumption` (critical)
- **Evidence Item:** `macro/target/poca_step2_analysis.py`
- **BEFORE Behavior:** Retained in final evidence (`object.10de6bfa07d20258e308d379`).
- **AFTER Trace Observation:**
  - An object matching the target evidence (`object.88f0fa939d8a56760c9d44c4`, pointing to `macro/target/poca_step2_analysis.py`) **is present in the AFTER channel union** (recalled via sparse/dense channels).
  - However, in reciprocal rank fusion, it ranked below the top-30 cutoff and was **absent from `ordinary_fused_top30`** and the `final_pool_object_ids`.
  - Since `n022` is a paraphrase without explicit triggers, no structured bridge reservation was triggered for this item.
- **Mechanistic Classification:** **`FUSION_CANDIDATE_ADMISSION_CUTOFF_REGRESSION`** (fusion/candidate-admission cutoff regression).
- **Overclaim Boundary:** Classified strictly as a candidate-admission cutoff effect at the fusion stage. No speculative claims about LLM prompt interpretation are made.

### 8.2 Regression 2: `g021.e2` (`pgenerators/Target/PndTargetGenerator.cxx`)
- **Case / Role:** `g021` (Gold v2.6 dev) / `pnd_target_generator_implementation` (critical)
- **Evidence Item:** `pgenerators/Target/PndTargetGenerator.cxx`
- **BEFORE Behavior:** Retained in final evidence (`object.7c683ccb9595dad20e4529fe`) via direct query expansion symbol injection from `restgas_profile_workflow`.
- **AFTER Trace Observation:**
  - `PndTargetGenerator.cxx` was suppressed by the Batch-1 in-memory component mask on `restgas_profile_workflow`.
  - In `AFTER_BATCH1_REPLACEMENT`, `PndTargetGenerator.cxx` was **completely absent from the channel union** (not recalled by exact, dense, sparse, workflow, paper, or graph channels).
  - It was also absent from the eligible, selected, and reserved structured candidate sets produced by the D3.5 bridge mechanism.
  - In accordance with Section 5 of the contract, no special routing rule, exception, or custom treatment was introduced for `g021.e2`.
- **Mechanistic Classification:** **`CANDIDATE_RECALL_GOVERNED_PROVENANCE_COVERAGE_REGRESSION`** (candidate-recall / governed-provenance-coverage regression).
- **Overclaim Boundary:** Classified strictly as an unreplaced dependency due to absence in candidate recall and structured provenance reachability.

---

## 9. Verdict Precedence Ladder & Safety Gating

Evaluation against the Section 41 verdict precedence hierarchy:

```text
Level 1 — INVALID / PROTOCOL_OR_TREATMENT_CONSTRUCTION_FAILED
  -> Not triggered (32/32 completed, valid arms, clean masks, no mutations).

Level 2 — INCONCLUSIVE / BEFORE_REFERENCE_NOT_REPRODUCED
  -> Not triggered (BEFORE reference reproduced g036.e1 and g021.e1 cleanly).

Level 3 — FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
  -> Not triggered (Target replacement reproduced 2/2 with valid witnesses).

Level 4 — FAIL / CRITICAL_OR_GROUNDING_REGRESSION
  -> TRIGGERED: CRITICAL_GROUP_REGRESSIONS = 2 (n022.e2, g021.e2 > 0).

Level 5 — PARTIAL / BEFORE_AFTER_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE
  -> Subsumed by Level 4.

Level 6 — PASS / FIRST_BATCH_BEFORE_AFTER_VALIDATED_FOR_RUNTIME_MIGRATION_DECISION
  -> Disqualified by Level 4.
```

Per Section 41, **Level 4 takes strict precedence over Level 5**. Even though aggregate metric drops also violate the -0.05 tolerance, the root blocker is the regression of critical evidence groups.

**Final Batch Verdict:**
```text
FAIL / CRITICAL_OR_GROUNDING_REGRESSION
```

---

## 10. Limitations, Lifecycle Impact & Next Stage

### 10.1 Scientific Findings & Limitations
1. **Replacement Mechanism is Valid for Isolated Target Locators:** The D3.5 structured bridge successfully reproduces the primary evidence items (`g036.e1` and `g021.e1`) without relying on legacy fixed locators.
2. **Multi-Evidence Rule Coverage is Incomplete:** Query expansion rules such as `restgas_profile_workflow` bundled multiple evidence locators into a single trigger. While the primary target locator (`prod_sim_hvmaps.C`) was reached by the graph bridge, secondary critical locators (`PndTargetGenerator.cxx`) were not reachable under current governed relations.
3. **Fusion Stability in Paraphrase Queries:** Paraphrase cases lacking literal expansion triggers (`n022`) rely on ordinary channel retrieval; slight shifts in ranking or tokenization can cause required evidence to fall just below the top-30 rerank pool cutoff.

### 10.2 Lifecycle Impact
- **D4-A2 Status:** `COMPLETE / FAIL / CRITICAL_OR_GROUNDING_REGRESSION`.
- **First-Batch Runtime Migration:** **BLOCKED**.
- **Production Activation:** `PRODUCTION_ACTIVATION = false`. `configs/query_expansions.yaml` and `src/panda_agent/` remain completely unchanged.
- **D4-A3 Status:** `NOT_STARTED / BLOCKED_BY_D4_A2_CRITICAL_REGRESSION`.

### 10.3 Exact Next Stage
Per Section 51, the migration must pause immediately without attempting in-stage patches or production modifications.

The exact next separately authorized task is:
> **`D4-A2-R1 — First-Batch Critical-Regression Diagnosis and Repair Decision`**

*This task is a diagnosis and decision task only. It must not be started without separate authorization.*
