# D3.5-A6 Phase 2 — Paired Repeated Reranker Replay Report

## 1. Executive Decision & Scientific Verdict

- **`D3.5-A6-PHASE2 = COMPLETE / PASS`**
- **`FINAL_A6_PHASE2_VERDICT = PASS / BOUNDED_RERANK_ADMISSION_VALIDATED_FOR_DEVELOPMENT`**
- **`SELECTED_ADMISSION_BUDGET = 3`**
- **`PRODUCTION_ACTIVATION = false`**
- **`D4 = BLOCKED / NOT_STARTED`**

The preregistered and frozen **D3.5-A6 Phase 2 — Paired Repeated Reranker Replay** has completed with full scientific validity and zero protocol defects.

All 54 formal slots were executed in the frozen cyclic schedule against Google Vertex AI Gemini 3.8 Flash (`temperature = 0.0`, `RERANK_SYSTEM_PROMPT`). Raw model responses were frozen in a dedicated audit commit before any post-rerank replay or scientific evaluation was computed.

The deterministic evaluator confirms:
- **`DELTA_2 = 1`**, **`DELTA_3 = 2`** (applicable bridge groups stably recovered downstream).
- **`CAUSAL_DELTA_2 = 1`**, **`CAUSAL_DELTA_3 = 2`** (all recovered groups carry the preregistered `STABLE_RESERVED_REQUIRED_WITNESS` in 3/3 repetitions).
- **`NONCAUSAL_STABLE_DELTA_2 = 0`**, **`NONCAUSAL_STABLE_DELTA_3 = 0`** (zero un-witnessed pool-perturbation recovery).
- **`REGRESSION_2 = 0`**, **`REGRESSION_3 = 0`** (zero material control regressions across all 5 BASELINE-stable safety groups).
- Both budgets are `MECHANISTIC_SAFE_EFFECTIVE`.
- Under the frozen causal-safe selection hierarchy, `CAUSAL_DELTA_3 (2) > CAUSAL_DELTA_2 (1)`, selecting bounded admission budget **`K = 3`**.

---

## 2. Git Lineage & Two-Commit Audit Boundary

- **Starting HEAD:** `1b33c2ab0ca89240d51a47fc2d9b9c5b8ca562dc` (*D3.5-A6 Phase1-R2 refreeze reranker model contract for Gemini 3.8*)
- **Commit A (Raw 54-Slot Freeze):** `4e8335d` (*D3.5-A6 Phase2 freeze raw repeated reranker outcomes*)
  - Created immediately upon completion of all 54 formal slots, before running any replay or evaluator code.
  - Freezes `evaluation/d3_5_a6_phase2_raw_reranker_results.json`, `evaluation/scripts/d3_5_a6_phase2_executor.py`, and `tests/unit/test_d3_5_a6_phase2_executor.py`.
- **Commit B (Scientific Evaluation Closeout):** *(this closeout commit)*
  - Closes deterministic evaluation artifacts, human report, status documentation, and roadmap.

---

## 3. Model Contract Authority & Reranker Invariants

- **Authority:** `evaluation/d3_5_a6_phase1_r2_pre_exposure_reranker_model_contract_refreeze.json`
- **Reranker Model:** `gemini-3.8-flash`
- **Temperature:** `0.0`
- **System Instruction:** `src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT` (byte-identical)
- **Task:** `rerank_evidence`
- **Candidate Payload:** `object_id`, `title`, `source_id`, `text[:2000]`
- **Response Schema:** Structured JSON `ranked_object_ids` enum-constrained to submitted pool members
- **Retry Policy:** `VertexAIClient.generate_json` 3-attempt transient retry loop
- **Thinking Mode:** None (no thinking budget, no reasoning parameter)

---

## 4. Execution Accounting (Section 34)

```text
STARTING_HEAD = 1b33c2ab0ca89240d51a47fc2d9b9c5b8ca562dc
FINAL_HEAD = (Commit B)

MODEL_CONTRACT_AUTHORITY = evaluation/d3_5_a6_phase1_r2_pre_exposure_reranker_model_contract_refreeze.json
A6_PHASE2_RERANKER_MODEL = gemini-3.8-flash

FORMAL_ARM_POOL_MANIFESTS = 18
FORMAL_PHASE2_CALL_PLAN_ENTRIES = 54
FORMAL_RERANKER_CALLS_EXECUTED = 54
FORMAL_RERANKER_CALLS_SUCCEEDED = 54
FORMAL_RERANKER_CALLS_FAILED = 0

PROVIDER_INTERNAL_ATTEMPTS = 54
TOTAL_TOKEN_USAGE = 931012

REAL_CASE_RERANKER_CALLS = 54

PHASE2_SELECT_V2_RUNS = 0

ANALYZER_CALLS = 0
EMBEDDING_CALLS = 0
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
POST_EXPOSURE_POOL_MUTATIONS = 0
POST_EXPOSURE_SCHEDULE_MUTATIONS = 0
POST_EXPOSURE_REPLAY_MUTATIONS = 0
POST_EXPOSURE_SCORER_MUTATIONS = 0
POST_EXPOSURE_APPLICABILITY_SEMANTIC_MUTATIONS = 0
POST_EXPOSURE_VERDICT_LOGIC_MUTATIONS = 0
```

---

## 5. Outcome Exposure Lifecycle Boundary

- **Before formal call #1:**
  - `REAL_CASE_RERANKER_CALLS = 0`
  - `A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED`
  - Pre-exposure static invariance checks (Section 8) fully passed.
- **At formal call #1:**
  - `A6_RERANK_OUTCOME_EXPOSURE = STARTED` (persisted to raw execution record).
- **During execution:**
  - Zero intermediate evaluations were performed.
  - No scientific metrics, retention counts, DELTA values, or verdicts were computed or inspected.
- **After completion of call #54:**
  - `A6_RERANK_OUTCOME_EXPOSURE = COMPLETE`
  - All 54 raw outputs persisted and committed in Commit A (`4e8335d`).
  - Only after Commit A was the deterministic evaluator invoked.

---

## 6. Scientific Outcome & Decision Metrics

| Metric | K2 (`ADMISSION_K2`) | K3 (`ADMISSION_K3`) | Hierarchy & Role |
| :--- | :---: | :---: | :--- |
| **`DELTA_K`** | **1** | **2** | Primary incremental benefit (stable retained under K, not BASELINE) |
| **`CAUSAL_DELTA_K`** | **1** | **2** | Primary mechanistic benefit (DELTA with stable reserved witness) |
| **`NONCAUSAL_STABLE_DELTA_K`** | **0** | **0** | Diagnostic only (`DELTA - CAUSAL_DELTA`) |
| **`REGRESSION_K`** | **0** | **0** | Material control regressions over safety population |
| **`MECHANISTIC_SAFE_EFFECTIVE(K)`** | **True** | **True** | `CAUSAL_DELTA > 0 AND REGRESSION == 0` |
| **`SELECTED_ADMISSION_BUDGET`** | — | **3** | Selected: smallest sufficient causally witnessed safe budget |
| **`FINAL_A6_PHASE2_VERDICT`** | — | — | **`PASS / BOUNDED_RERANK_ADMISSION_VALIDATED_FOR_DEVELOPMENT`** |

---

## 7. Group-Level Stability & Causal Witness Breakdown

### 7.1 Admission-Applicable Bridge Groups

The evaluator identified exactly two `ADMISSION_APPLICABLE_BRIDGE_GROUP`s across the development cases:

1. **`g036.e1` (Case `g036` — macro `macro/target/ana_dpm.C`):**
   - **`BASELINE`:** `[False, False, False]` → `stable_retained = False`
   - **`ADMISSION_K2`:** `[False, False, False]` → `stable_retained = False`, `witness = [False, False, False]`.
     *(Explanation: in `g036`, `ana_dpm.C` was the 3rd reservable bridge candidate. Budget K=2 admitted candidates #1 and #2, displacing 2 baseline candidates, but did not admit `ana_dpm.C`. Thus `g036.e1` remained un-recovered.)*
   - **`ADMISSION_K3`:** `[True, True, True]` → `stable_retained = True`, `witness = [True, True, True]`.
     *(Explanation: budget K=3 admitted `ana_dpm.C` as the 3rd reserved candidate. The candidate competed in the reranker pool, survived into final evidence across all 3 repetitions, and established a 3/3 stable causal witness.)*
   - **Result:** Contributes to `CAUSAL_DELTA_3` (+1), does not contribute to `CAUSAL_DELTA_2` (0).

2. **`g021.e1` (Case `g021` — macro `macro/target/prod_sim_hvmaps.C`):**
   - **`BASELINE`:** `[False, False, False]` → `stable_retained = False`
   - **`ADMISSION_K2`:** `[True, True, True]` → `stable_retained = True`, `witness = [True, True, True]`.
     *(Explanation: `prod_sim_hvmaps.C` was reservable candidate #1 in `g021`. Both K=2 and K=3 admitted it. It survived reranking into final evidence across all 3 repetitions, establishing a 3/3 stable causal witness.)*
   - **`ADMISSION_K3`:** `[True, True, True]` → `stable_retained = True`, `witness = [True, True, True]`.
   - **Result:** Contributes to both `CAUSAL_DELTA_2` (+1) and `CAUSAL_DELTA_3` (+1).

### 7.2 Safety & Control Population

The safety population consists of all 5 evaluator groups that are stable in `BASELINE` (`retained >= 2/3`):

1. **`n006.e1` (Nontrigger control):** `BASELINE [True, True, True]`, `K2 [True, True, True]`, `K3 [True, True, True]` → `MCR = False`.
2. **`g041.e1` (Negative / insufficient-evidence control):** `BASELINE [True, True, True]`, `K2 [True, True, True]`, `K3 [True, True, True]` → `MCR = False`.
3. **`g020.e1` (Same-subsystem control — README):** `BASELINE [True, True, True]`, `K2 [True, True, True]`, `K3 [True, True, True]` → `MCR = False`.
4. **`g020.e2` (Same-subsystem control — runall):** `BASELINE [True, True, True]`, `K2 [True, True, True]`, `K3 [True, True, True]` → `MCR = False`.
5. **`n004.e1` (Ordinary retrieval control):** `BASELINE [True, True, True]`, `K2 [True, True, True]`, `K3 [True, True, True]` → `MCR = False`.

**Total Material Control Regressions:** `REGRESSION_2 = 0`, `REGRESSION_3 = 0`.

---

## 8. Identical-Pool Variance Reference Analysis

Per Section 15:
- In `n006`, `g041`, and `n004`, `BASELINE == ADMISSION_K2 == ADMISSION_K3` by frozen construction (empty reservable bridge).
- Across all 9 slots for each of these three cases, Gemini 3.8 Flash produced identical downstream final evidence retention (3/3 retention across all arms and repetitions).
- In `g021`, `ADMISSION_K2 == ADMISSION_K3` (only 1 reservable candidate). Both arms produced identical downstream recovery (3/3 retention of `g021.e1`).
- This confirms high reranker stability at temperature 0.0, and verifies that the observed recovery in `g036` and `g021` is an admission treatment effect, not reranker stochasticity.

---

## 9. Budget Selection Rationale

Per Section 23:
1. `K2` satisfies `MECHANISTIC_SAFE_EFFECTIVE` (`CAUSAL_DELTA_2 = 1 > 0`, `REGRESSION_2 = 0`).
2. `K3` satisfies `MECHANISTIC_SAFE_EFFECTIVE` (`CAUSAL_DELTA_3 = 2 > 0`, `REGRESSION_3 = 0`).
3. Comparing causal benefit: `CAUSAL_DELTA_3 (2) > CAUSAL_DELTA_2 (1)`.
4. Under the preregistered rule, when both budgets are safe and effective, K3 is selected if and only if `CAUSAL_DELTA_3 > CAUSAL_DELTA_2`. Because K=3 causally recovers both `g036.e1` and `g021.e1` whereas K=2 recovers only `g021.e1`, **`K = 3`** is selected as the smallest sufficient causally witnessed safe budget.

---

## 10. Protection Boundaries & Next Stage

- `PRODUCTION_ACTIVATION = false` (this development validation does not authorize production rollout).
- `D4 = BLOCKED / NOT_STARTED` (any D4 lifecycle consideration requires separate explicit authorization).
- `NOVEL_VALIDATION_RUNS = 0`, `NOVEL_HOLDOUT_RUNS = 0`, `PROTECTED_DATASET_ACCESS = 0`.
- All post-exposure mutation counts are `0`.
