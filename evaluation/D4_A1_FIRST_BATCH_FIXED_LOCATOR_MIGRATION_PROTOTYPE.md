# PANDA Agent — D4-A1: First-Batch Fixed-Locator Migration Prototype Report

## 1. Executive Decision & Scientific Verdict

```text
D4_A1_DECISION = PASS / FIRST_BATCH_FIXED_LOCATOR_REPLACEMENT_VALIDATED_FOR_DEVELOPMENT
D4-A1 = COMPLETE / PASS / FIRST_BATCH_FIXED_LOCATOR_REPLACEMENT_VALIDATED_FOR_DEVELOPMENT
D4 = IN_PROGRESS / INCREMENTAL_QUERY_EXPANSION_MIGRATION
D4-A2 = NOT_STARTED / READY_FOR_FIRST_BATCH_BEFORE_AFTER_VALIDATION
EXACT_NEXT_STAGE = D4-A2 — First-Batch Before/After Validation (separately authorized)

PER_RULE_DECISIONS:
  event_poca_handoff: REPLACEMENT_VALIDATED
  restgas_profile_workflow: REPLACEMENT_VALIDATED

SAFETY_METRICS:
  REGRESSION_ABLATION = 0
  REGRESSION_REPLACEMENT = 0
  REGRESSION_COUNT = 0

PARAPHRASE_DIAGNOSTIC (n022, non-gating):
  n022.e1: F/F/F (LEGACY: False, ABLATION: False, REPLACEMENT: False)
  n022.e2: T/T/T (LEGACY: True,  ABLATION: True,  REPLACEMENT: True)
  n022.e3: T/F/T (LEGACY: True,  ABLATION: False, REPLACEMENT: True)

OUTCOME_EXPOSURE = COMPLETE
PRODUCTION_ACTIVATION = false
```

The preregistered and frozen **D4-A1 — First-Batch Fixed-Locator Migration Prototype** has completed with full scientific validity, zero protocol defects, and a conclusive positive verdict.

All 21 formal slots across the frozen 7-case × 3-arm cohort were executed in strict case-major order under Google Vertex AI Gemini 3.8 Flash (`temperature = 0.0`). The raw execution outputs were frozen in dedicated audit Commit B (`d0921c87aa7542e6f84ec49ec04a28cd199a6050`) before running the deterministic evaluator.

The deterministic evaluator confirms:
1. **Confirmed Legacy Dependency:** Suppression of the fixed-locator components in `event_poca_handoff` and `restgas_profile_workflow` confirmed real dependency on both target evidence items under ablation:
   - `g036.e1` (`macro/target/ana_dpm.C`): `LEGACY_CONTROL = True` -> `BATCH1_ABLATION = False`
   - `g021.e1` (`macro/target/prod_sim_hvmaps.C`): `LEGACY_CONTROL = True` -> `BATCH1_ABLATION = False`
2. **Truthful Structured Replacement:** The generic structured replacement path (D2 governed resolution -> D1 accepted graph -> provenance materialization -> `d3_5_selectivity_v2` with caps 8/4 -> K=3 bounded rerank admission) successfully recovered both target items under `BATCH1_REPLACEMENT` (`T/F/T`):
   - `g036.e1`: `BATCH1_REPLACEMENT = True` with a verified truthful admission witness (`object.5cae2ceab6e67bb4c9065331`, reserved under K=3, competed in reranker at position 29, retained in final evidence)
   - `g021.e1`: `BATCH1_REPLACEMENT = True` with a verified truthful admission witness (`object.3ab0a90ae68e8ece071a9f22`, reserved under K=3, competed in reranker at position 29, retained in final evidence)
3. **Zero Safety Regressions:** Across all 5 BASELINE-stable safety groups in the four safety cases (`n006`, `g041`, `g020`, `n004`), neither ablation nor replacement caused any material control regressions (`REGRESSION_ABLATION = 0`, `REGRESSION_REPLACEMENT = 0`).
4. **Per-Rule Decisions:** Both target rules achieved `REPLACEMENT_VALIDATED`.
5. **Batch Verdict:** Under the frozen 7-level verdict precedence ladder, the outcome satisfies Level 3: **`PASS / FIRST_BATCH_FIXED_LOCATOR_REPLACEMENT_VALIDATED_FOR_DEVELOPMENT`**.
6. **Strict Development Boundary:** This prototype validates the replacement mechanism for development only; `PRODUCTION_ACTIVATION` remains `false`.

---

## 2. Git Lineage & Three-Commit Audit Boundary

The execution strictly observed the three-commit outcome-exposure audit boundary:

- **Starting HEAD:** `feecfdbebd933fbcf679b65432bd54d699594ecb` (*D4-A0 freeze expansion migration inventory and first batch*)
- **Commit A (Implementation Freeze):** `8481f3411ae7e277abd8056910eb737624b7666e` (*D4-A1 freeze first-batch migration prototype*)
  - Created prior to formal cell #1.
  - Freezes `evaluation/d4_a1_execution_manifest.json`, `evaluation/scripts/d4_a1_fixed_locator_migration.py`, and `tests/unit/test_d4_a1_fixed_locator_migration.py`.
- **Commit B (Raw Outcome Freeze):** `d0921c87aa7542e6f84ec49ec04a28cd199a6050` (*D4-A1 freeze first-batch raw migration outcomes*)
  - Created immediately upon completion of all 21 formal cells, before running any evaluator code.
  - Freezes `evaluation/d4_a1_raw_three_arm_results.json` (52,446 lines, 1.78 MB).
- **Commit C (Final Scientific Closeout):** *(this closeout commit)*
  - Closes untracked deterministic evaluator output `evaluation/d4_a1_evaluator_results.json`, result artifact `evaluation/d4_a1_result.json`, human-readable report `evaluation/D4_A1_FIRST_BATCH_FIXED_LOCATOR_MIGRATION_PROTOTYPE.md`, and status/roadmap tracking docs.

---

## 3. Experimental Design & Treatment Cohort

### 3.1 Three Evaluation-Only Arms

The prototype evaluated three arms under identical retriever configuration, prompts, and models:

1. **`LEGACY_CONTROL`:** Current query-expansion behavior without suppression and without D4 replacement path. All 54 rules active; structured replacement inactive; admission budget K = 0.
2. **`BATCH1_ABLATION`:** Batch-1 fixed-location components suppressed; structured replacement inactive; admission budget K = 0.
3. **`BATCH1_REPLACEMENT`:** Batch-1 fixed-location components suppressed; generic structured replacement path active with K = 3 bounded rerank admission.

### 3.2 Exact 7-Case Cohort

The cohort comprises 7 cases (6 development cases + 1 paraphrase diagnostic):

| Case ID | Role | Target Rule | Dataset | Gating | Primary Evaluation Function |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **`g036`** | TARGET_DEPENDENCY_CASE | `event_poca_handoff` | `gold_dev` | **True** | Test ablation of `ana_dpm.C` and recovery via structured bridge |
| **`g021`** | TARGET_DEPENDENCY_CASE | `restgas_profile_workflow` | `gold_dev` | **True** | Test ablation of `prod_sim_hvmaps.C` and recovery via structured bridge |
| **`n006`** | SAFETY_CONTROL_CASE | None | `novel_dev` | **True** | Detect ordinary-evidence regression in absence of bridge activity |
| **`g041`** | SAFETY_CONTROL_CASE | None | `gold_dev` | **True** | Detect ordinary-evidence regression in negative control |
| **`g020`** | SAFETY_CONTROL_CASE | None | `gold_dev` | **True** | Detect ordinary-evidence regression and verify non-target expansion stability |
| **`n004`** | SAFETY_CONTROL_CASE | None | `novel_dev` | **True** | Detect ordinary-evidence regression in non-target rule `root_macro_usage` |
| **`n022`** | PARAPHRASE_DIAGNOSTIC_CASE | `event_poca_handoff` | `novel_dev` | **False** | Approved D3 event_poca paraphrase diagnostic without literal trigger; non-gating |

### 3.3 Exact Component Suppression & Preservation Masks

#### Rule 1: `event_poca_handoff`
- **Suppressed Fixed Locators:**
  - Symbols (4): `macro/target/ana_dpm.C`, `macro/target/prod_aod_complete.C`, `POCA_VERTEX_FILE`, `PndPidCorrelator`
  - Paper page hints: `li_2026`: [131, 138]
- **Preserved Components:**
  - Triggers: `event_poca`, `poca_vertex_file`, `second-pass pid`, `第二遍 pid`
  - Repositories: `restgas_determination`, `pandaroot`
  - Concepts: `event POCA handoff`, `event-aligned second-pass propagation`

#### Rule 2: `restgas_profile_workflow`
- **Suppressed Fixed Locators:**
  - Symbols (5): `pgenerators/Target/PndTargetGenerator.cxx`, `macro/target/prod_sim_hvmaps.C`, `macro/target/reco_complete.C`, `macro/target/ana_complete.C`, `macro/target/correction/efficiency_correction_2.C`
  - Paper page hints: `{}`
- **Preserved Components:**
  - Triggers: `restgas_profile`, `restgas profile`, `corrected rho`, `修正后的 rho`
  - Repositories: `restgas_determination`, `pandaroot`
  - Concepts: `distributed target generation`, `longitudinal profile correction`

---

## 4. Authoritative Model & Governed Replacement Receipts

### 4.1 Model & Configuration Contract
- **Model Role:** `QA_GENERATION_MODEL_ID via VertexSettings.from_env()`
- **Analyzer Model ID:** `gemini-3.8-flash`
- **Reranker Model ID:** `gemini-3.8-flash`
- **Embedding Model Role:** `QA_EMBEDDING_MODEL_ID via VertexSettings.from_env()`
- **Embedding Model ID:** `gemini-embedding-2`
- **Vertex Location:** `global`
- **Temperature:** `0.0`
- **Reranker Prompt Authority:** `src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT`
- **Query Analyzer Prompt Authority:** `src/panda_agent/prompts.py:QUERY_ANALYZER_SYSTEM_PROMPT`
- **Retry Policy:** `VertexAIClient.generate_json` 3-attempt transient retry loop
- **Thinking Budget:** None (no reasoning/thinking parameter)

### 4.2 Governed Replacement Architecture
- **D1/D2 Authority:** D2 governed resolution -> D1 accepted objects, relations, and workflows. No fuzzy jumping, dense similarity search over unlinked graph nodes, or LLM-invented graph hops.
- **Bridge Semantics:** Bounded reachability: maximum 1 upward containment transition + maximum 1 predicate/type-gated relation/workflow transition. Governed provenance materialization to exact source and version evidence.
- **Candidate Selectivity Policy:** `d3_5_selectivity_v2` with `SELECTIVITY_CAP = 8` and `PER_ORIGIN_CAP = 4`. Model calls: 0.
- **Admission Budget:** K = 3 bounded rerank admission (ceiling-not-quota, pool size 30, bottom-first displacement).
- **Post-Rerank Fallback Pool:** Treatment pool `[*reranked, *rerank_pool, *baseline_fused_ordering]`.
- **Prohibited Shortcuts Enforced:**
  - No new scorer, weights, or reranker models.
  - No benchmark-specific mapping tables or lookup dicts.
  - No rule-ID to evidence-path mapping.
  - No question-ID to evidence-path mapping.
  - No silent re-injection of suppressed legacy locators into retrieval channels.

---

## 5. Execution Accounting & Audit Invariants

```text
FORMAL_CELLS_TOTAL = 21
FORMAL_CELLS_COMPLETED = 21
FORMAL_CELLS_FAILED = 0

LOGICAL_ANALYZER_CALLS = 21
LOGICAL_EMBEDDING_CALLS = 21
LOGICAL_RERANKER_CALLS = 21
TOTAL_LOGICAL_MODEL_CALLS = 63

PROVIDER_INTERNAL_ATTEMPTS = 63
TOTAL_TOKEN_USAGE = 406019

REAL_CASE_RETRIEVAL_RUNS = 21
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

POST_EXPOSURE_MODEL_MUTATIONS = 0
POST_EXPOSURE_PROMPT_MUTATIONS = 0
POST_EXPOSURE_MASK_MUTATIONS = 0
POST_EXPOSURE_SCHEDULE_MUTATIONS = 0
POST_EXPOSURE_REPLACEMENT_MUTATIONS = 0
POST_EXPOSURE_SCORER_MUTATIONS = 0
POST_EXPOSURE_VERDICT_LOGIC_MUTATIONS = 0
```

All 63 provider requests succeeded on the first attempt (0 transient retries). Zero mid-run evaluations occurred; execution ran start-to-finish in 7 minutes 34 seconds (`2026-09-02T20:30:42` to `2026-09-02T20:38:16`).

---

## 6. Scientific Outcomes & Truthful Admission Witnesses

### 6.1 Complete Group Retention Grid

Across all 12 evaluated evidence groups and all 3 arms:

| Evidence Group | Case ID | Role | LEGACY_CONTROL | BATCH1_ABLATION | BATCH1_REPLACEMENT | Pattern | Outcome Interpretation |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`g036.e1`** | `g036` | Target | **True** | **False** | **True** | **T / F / T** | Confirmed legacy dependency; recovered with truthful witness |
| **`g021.e1`** | `g021` | Target | **True** | **False** | **True** | **T / F / T** | Confirmed legacy dependency; recovered with truthful witness |
| `g021.e2` | `g021` | Target (secondary) | True | False | False | T / F / F | Secondary group; not targeted by Batch-1 bridge |
| **`n006.e1`** | `n006` | Safety | **True** | **True** | **True** | **T / T / T** | Stable; zero regression |
| `n006.e2` | `n006` | Safety (non-stable) | False | False | False | F / F / F | Unretained across all arms |
| **`g041.e1`** | `g041` | Safety | **True** | **True** | **True** | **T / T / T** | Stable; zero regression |
| **`g020.e1`** | `g020` | Safety | **True** | **True** | **True** | **T / T / T** | Stable; zero regression |
| **`g020.e2`** | `g020` | Safety | **True** | **True** | **True** | **T / T / T** | Stable; zero regression |
| **`n004.e1`** | `n004` | Safety | **True** | **True** | **True** | **T / T / T** | Stable; zero regression |
| `n022.e1` | `n022` | Diagnostic | False | False | False | F / F / F | Unretained across all arms |
| `n022.e2` | `n022` | Diagnostic | True | True | True | T / T / T | Stable across all arms |
| `n022.e3` | `n022` | Diagnostic | True | False | True | T / F / T | Non-gating diagnostic recovery (ordinary pool) |

---

### 6.2 Target Dependency Case 1: `g036` (`event_poca_handoff`)

- **Query:** *"Which macro produces event_poca?"*
- **Target Evidence:** `g036.e1` (Required locator: `macro/target/ana_dpm.C`, lines 1–938)
- **Outcomes by Arm:**
  - `LEGACY_CONTROL`: **True** (rank 4 in ordinary fused pool; retained in final evidence)
  - `BATCH1_ABLATION`: **False** (fixed locator suppressed; absent from fused pool and final evidence -> **Dependency confirmed**)
  - `BATCH1_REPLACEMENT`: **True** (recovered via structured bridge and admitted under K=3)
- **Truthful Admission Witness Details:**
  - `candidate_object_id`: `object.5cae2ceab6e67bb4c9065331`
  - `locator_path`: `macro/target/ana_dpm.C` (lines 1–938)
  - `source_id`: `restgas_determination`
  - `source_version_id`: `restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42`
  - `provenance_origin_ids`: `["edge.2e09628416a01ce2461d752a"]` (relation edge)
  - `min_structural_distance_transitions`: 2
  - `governed_path`: **True**
  - `selected_by_v2`: **True**
  - `ordinary_top30_before_reservation`: **False**
  - `reserved_under_k3`: **True**
  - `displaced_candidates`: `object.88d0d65c7dbf3c313f1fa5dd`, `object.2243fa2f42ac96009ac4ba42`, `object.9784e8cd299c611d20d298d4`
  - `final_pool_membership`: **True** (position 29)
  - `competed_in_reranker`: **True**
  - `final_evidence_retained`: **True**
  - `is_valid_witness`: **True**
- **Per-Rule Decision:** **`REPLACEMENT_VALIDATED`**

---

### 6.3 Target Dependency Case 2: `g021` (`restgas_profile_workflow`)

- **Query:** *"How is restgas_profile supplied to distributed-target simulation?"*
- **Target Evidence:** `g021.e1` (Required locator: `macro/target/prod_sim_hvmaps.C`, lines 1–203)
- **Outcomes by Arm:**
  - `LEGACY_CONTROL`: **True** (rank 4 in ordinary fused pool; retained in final evidence)
  - `BATCH1_ABLATION`: **False** (fixed locator suppressed; absent from fused pool and final evidence -> **Dependency confirmed**)
  - `BATCH1_REPLACEMENT`: **True** (recovered via structured bridge and admitted under K=3)
- **Truthful Admission Witness Details:**
  - `candidate_object_id`: `object.3ab0a90ae68e8ece071a9f22`
  - `locator_path`: `macro/target/prod_sim_hvmaps.C` (lines 1–203)
  - `source_id`: `restgas_determination`
  - `source_version_id`: `restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42`
  - `provenance_origin_ids`: `["edge.ea3a79d222f0ca6cc0e6df72"]` (relation edge)
  - `min_structural_distance_transitions`: 1
  - `governed_path`: **True**
  - `selected_by_v2`: **True**
  - `ordinary_top30_before_reservation`: **False**
  - `reserved_under_k3`: **True**
  - `displaced_candidates`: `object.54b5cf78ac656b14878ac4b6`
  - `final_pool_membership`: **True** (position 29)
  - `competed_in_reranker`: **True**
  - `final_evidence_retained`: **True**
  - `is_valid_witness`: **True**
- **Per-Rule Decision:** **`REPLACEMENT_VALIDATED`**

---

### 6.4 Safety Control Population & Regression Analysis

The safety population consists of the 5 frozen A6 safety evidence groups that exhibit stable retention under `LEGACY_CONTROL`:
1. `n006.e1` (Nontrigger control — `PndFileNameRegistry`): `LEGACY = True`, `ABLATION = True`, `REPLACEMENT = True`
2. `g041.e1` (Negative control — `PndPidCorrelator`): `LEGACY = True`, `ABLATION = True`, `REPLACEMENT = True`
3. `g020.e1` (Same-subsystem control — README): `LEGACY = True`, `ABLATION = True`, `REPLACEMENT = True`
4. `g020.e2` (Same-subsystem control — runall): `LEGACY = True`, `ABLATION = True`, `REPLACEMENT = True`
5. `n004.e1` (Ordinary retrieval control — logging): `LEGACY = True`, `ABLATION = True`, `REPLACEMENT = True`

**Safety Summary:**
- `safety_population`: 5 groups
- `ablation_regressions`: `[]` -> **`REGRESSION_ABLATION = 0`**
- `replacement_regressions`: `[]` -> **`REGRESSION_REPLACEMENT = 0`**
- `regression_count`: **0**

---

### 6.5 Paraphrase Diagnostic Case: `n022` (Non-Gating)

- **Query:** *"The restgas analysis determines the event vertex through a two-step POCA workflow. What does the first worker step leave behind for the second analysis step, and how is the fitted vertex fed into the reprocessing?"*
- **Role:** `PARAPHRASE_DIAGNOSTIC_CASE` (approved D3 event_poca paraphrase without literal trigger; non-gating).
- **Group Retention Outcomes:**
  - `n022.e1`: **F / F / F** (absent in all three arms; `has_valid_witness = False`)
  - `n022.e2`: **T / T / T** (retained in all three arms; candidate `object.10de6bfa07d20258e308d379` at position 19 entered through ordinary top-30 retrieval, not governed reservation; `has_valid_witness = False`)
  - `n022.e3`: **T / F / T** (retained in LEGACY and REPLACEMENT, lost in ABLATION; candidate `object.e29c4fcd17107cabea45f18e` at position 12 entered through ordinary top-30 retrieval; `has_valid_witness = False`)
- **Diagnostic Finding:** Confirms non-trigger stability and ordinary retrieval behavior without conflating with governed reservation witnesses. Does not gate PASS/FAIL.

---

## 7. Evaluator Verdict Precedence Ladder

The preregistered verdict precedence ladder resolves as follows:

1. **Protocol or treatment construction failed?**
   - No. All 21 cells executed in order, all invariant checks passed, zero mid-run evaluations, valid treatment construction.
2. **Material safety regression on any group under replacement (`REGRESSION_REPLACEMENT > 0`)?**
   - No. `REGRESSION_REPLACEMENT = 0` across all 5 safety groups.
3. **Both target rules `REPLACEMENT_VALIDATED` with reserved admission witness and zero replacement regression?**
   - **YES.**
   - `event_poca_handoff`: `REPLACEMENT_VALIDATED` (legacy dependency confirmed, truthful witness verified).
   - `restgas_profile_workflow`: `REPLACEMENT_VALIDATED` (legacy dependency confirmed, truthful witness verified).
   - `REGRESSION_REPLACEMENT = 0`.
   - Resulting Verdict: **`PASS / FIRST_BATCH_FIXED_LOCATOR_REPLACEMENT_VALIDATED_FOR_DEVELOPMENT`**.

---

## 8. Development Validation vs Production Authorization Boundary

```text
+-------------------------------------------------------------------------------+
|                        DEVELOPMENT VALIDATION BOUNDARY                         |
|                                                                               |
|  [D4-A1 Prototype: VALIDATED]                 [Production System: UNTOUCHED]  |
|  - event_poca_handoff: REPLACEMENT_VALIDATED  - configs/query_expansions.yaml |
|  - restgas_profile_workflow: REPLACEMENT_VAL    is 100% BYTE-IDENTICAL.       |
|  - REGRESSION_REPLACEMENT = 0                 - PRODUCTION_ACTIVATION = false |
|  - Bounded development migration ONLY.        - Default retriever unchanged.  |
+-------------------------------------------------------------------------------+
```

- **Evaluation-Only Status:** The D4-A1 prototype demonstrates that generic structured replacement safely and effectively replaces the fixed-location components of the two target rules in an isolated three-arm test.
- **Production Safety:** No changes have been made to `configs/query_expansions.yaml` or production runtime retrieval paths. Production activation remains strictly `false`.
- **Exact Next Stage:** **`D4-A2 — First-Batch Before/After Validation`** (requires separate, explicit user authorization before commencing).
