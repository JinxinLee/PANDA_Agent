# D3.5-A6 Phase 1-R2 — Pre-Exposure Reranker Model Contract Upgrade & Re-freeze

## 1. Executive decision

**`A6_PHASE1_R2_DECISION = PRE_EXPOSURE_RERANKER_MODEL_CONTRACT_UPGRADED_AND_REFROZEN`**
- `PHASE2_SCIENTIFIC_READINESS = YES`
- `PHASE2_AUDIT_READINESS = YES`
- `A6_PHASE2_RERANKER_MODEL = gemini-3.8-flash`
- `MODEL_CONTRACT_AUTHORITY = D3.5-A6-PHASE1-R2`
- `A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED`

The future execution contract for D3.5-A6 Phase 2 is upgraded and refrozen from `gemini-3.7-flash` to `gemini-3.8-flash`, reconciling the experiment contract with the centralized runtime environment single source of truth (`QA_GENERATION_MODEL_ID`). This upgrade was performed strictly pre-exposure (0 real reranker calls executed). All non-model scientific identities remain invariant: 18/18 arm pool identities, reserved candidates, displaced candidates, 54 call entries, ordered candidate payloads, prompts, temperature, schema, retry policy, post-rerank replay semantics, and decision logic.

## 2. Starting state

- **Starting HEAD:** `136e02144cd197da031ce99eef9cb7ad179ccf88` (*Centralize runtime model selection in environment configuration*)
- **A6 Predecessor Commit:** `b7868fba119b0b492db9d56fc8396e5cc5f06191` (*D3.5-A6 Phase1-R1 close replay metadata and per-arm origin diagnostics*)
- **Phase 1 Freeze Commit:** `b26b2d740d656079862d845a023e31142e99db32` (*D3.5-A6 Phase1 freeze bounded admission prototype and replay implementation*)
- Working directory was clean; legitimate engineering cleanup commit `136e021` is preserved.

## 3. Why the model contract changed

Engineering cleanup commit `136e021` removed hardcoded model fallbacks across the codebase (notably `DEFAULT_GENERATION_MODEL = "gemini-3.7-flash"` in `src/panda_agent/api.py` and dataclass defaults in `src/panda_agent/llm/vertex.py`), establishing process environment variables as the single authoritative source of truth for runtime model selection.

Under this configuration, the local and recommended runtime model is `gemini-3.8-flash`. However, the previously frozen A6 Phase-1 artifacts (`evaluation/d3_5_a6_phase1_execution_manifest.json` and `evaluation/d3_5_a6_phase1_implementation_freeze.json`) still recorded `gemini-3.7-flash`. To prevent Phase 2 from executing with an obsolete model contract or experiencing a runtime/environment mismatch, this Phase 1-R2 stage explicitly reconciles and re-freezes the model contract prior to exposure.

## 4. Runtime single-source-of-truth state

- `QA_GENERATION_MODEL_ID = gemini-3.8-flash`
- `QA_EVALUATION_JUDGE_MODEL_ID = gemini-3.8-flash`
- Resolution path: `VertexSettings.from_env()` reads directly from process environment variables without hardcoded fallback.
- **Judge role relevance:** `none`. A6 Phase 2 uses only the structured generation role for candidate reranking. `QA_EVALUATION_JUDGE_MODEL_ID` is runtime configuration and is not part of the A6 treatment. No judge calls are scheduled or permitted in A6 Phase 2.

## 5. Original A6 model contract

Frozen in Phase 1 (`evaluation/d3_5_a6_phase1_implementation_freeze.json`):
- `generation_model_id`: `gemini-3.7-flash`
- `temperature`: `0.0`
- `system_prompt_source`: `src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT`
- `response_schema_contract`: `{"ranked_object_ids": [string...], "additionalProperties": false}` with enum restricted to pool candidates
- `provider_retry_policy`: `existing VertexAIClient.generate_json 3-attempt transient-retry loop, unchanged`

The original 3.7 contract is preserved in repository history and noted as historical provenance; it is not falsified or erased.

## 6. Refrozen A6 model contract

Frozen in Phase 1-R2 (`evaluation/d3_5_a6_phase1_r2_pre_exposure_reranker_model_contract_refreeze.json`):
- `generation_model_id`: `gemini-3.8-flash`
- `temperature`: `0.0` (unchanged)
- `system_prompt_source`: `src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT` (imported unchanged)
- `response_schema_contract`: `{"ranked_object_ids": [string...], "additionalProperties": false}` with enum restricted to pool candidates (unchanged)
- `provider_retry_policy`: `existing VertexAIClient.generate_json 3-attempt transient-retry loop, unchanged`
- `authority`: `evaluation/d3_5_a6_phase1_r2_pre_exposure_reranker_model_contract_refreeze.json`

## 7. Pre-exposure timing

This upgrade occurred strictly **pre-exposure**:
- `REAL_RERANKER_CALLS_BEFORE_UPGRADE = 0`
- `REAL_RERANKER_CALLS_DURING_R2 = 0`
- `MODEL_SMOKE_TESTS = 0`
- No real-case data or model outputs have been generated or observed under either 3.7 or 3.8 for A6.

## 8. Reranker interface invariants

All reranker interface contracts remain strictly unchanged:
- `temperature = 0.0`
- `system_instruction = RERANK_SYSTEM_PROMPT` (byte-identical in `src/panda_agent/prompts.py`)
- `task = rerank_evidence`
- `request_structure = { task, untrusted_question, untrusted_candidates }`
- `candidate_payload = object_id, title, source_id, text[:2000]`
- `response_field = ranked_object_ids`
- `response_enum = formal slot pool object IDs`
- `provider_retry_policy = VertexAIClient.generate_json 3-attempt loop`
- **Thinking mode / reasoning effort:** None introduced. No `thinking`, `reasoning_effort`, or `thinking_budget` parameters are added.

## 9. Pool invariants

Mechanically verified across all 18 formal arm pools (`evaluation/d3_5_a6_phase1_pool_manifest.json`):
- `ordered_pool_object_ids`: 18 / 18 identical
- `reserved_bridge_candidate_ids`: unchanged across all arms
- `displaced_object_ids`: unchanged across all arms
- `pool_size`: exactly 30 for all 18 pools
- `pool_identity`: identical to `ordered_pool_object_ids`
- `identical_pool_relations`:
  - `g036`: all distinct (preserved)
  - `g021`: `K2 == K3` (preserved)
  - `n006`: `BASELINE == K2 == K3` (preserved)
  - `g041`: `BASELINE == K2 == K3` (preserved)
  - `g020`: all distinct (preserved)
  - `n004`: `BASELINE == K2 == K3` (preserved)

## 10. 54-slot execution-plan invariants

Mechanically verified across all 54 entries in `evaluation/d3_5_a6_phase1_execution_manifest.json`:
- `formal_call_index`: 1 to 54 unchanged
- `case_id`, `repetition`, `arm`: cyclic schedule perfectly preserved:
  - Case order: `g036, g021, n006, g041, g020, n004`
  - Repetition 1: `BASELINE → ADMISSION_K2 → ADMISSION_K3`
  - Repetition 2: `ADMISSION_K2 → ADMISSION_K3 → BASELINE`
  - Repetition 3: `ADMISSION_K3 → BASELINE → ADMISSION_K2`
- `ordered_pool_object_ids`: 54 / 54 unchanged
- `ordered_reranker_payload`: 54 / 54 byte-identical in scientific content (exact 4 fields `object_id, title, source_id, text[:2000]`)
- `pool_size`: 30 unchanged
- `pool_identity`: unchanged
- `outcome_status`: all 54 remain `NOT_EXECUTED`

## 11. Replay/evaluator invariants

- **Post-rerank replay:** `post_rerank_replay`, `replay_case_with_registry`, `replay_case`, `select_final_evidence`, and `_source_type_of` remain untouched.
- **Evaluator semantics:** Pure functions in `evaluation/scripts/d3_5_a6_phase1_admission.py` remain untouched:
  - `ADMISSION_APPLICABLE_BRIDGE_GROUP`
  - `STABLE_RETAINED` (≥2/3), `STABLE_LOST` (≤1/3)
  - `STABLE_RESERVED_REQUIRED_WITNESS`
  - `DELTA_K`, `CAUSAL_DELTA_K`, `NONCAUSAL_STABLE_DELTA_K`
  - `MATERIAL_CONTROL_REGRESSION`, `REGRESSION_K`
  - `MECHANISTIC_SAFE_EFFECTIVE`
  - `SELECTED_ADMISSION_BUDGET` (causal-safe hierarchy)
  - Seven-level verdict precedence (`INVALID` → `FAIL` → `PASS` → `PARTIAL × 3`)

## 12. Scientific-comparability note

> [!IMPORTANT]
> **Cross-Stage Comparability Provenance:**
> Historical A2 and A5 reranker executions used Gemini 3.7 Flash.
> A6 Phase 2 will use Gemini 3.8 Flash.
> Therefore, absolute cross-stage reranker rank and final-evidence differences between historical A2/A5 and A6 must not be attributed solely to the admission redesign.
> The primary A6 scientific contrast remains the strictly controlled within-A6 comparison:
> **`BASELINE vs ADMISSION_K2 vs ADMISSION_K3`**
> under the same Gemini 3.8 reranker contract.

## 13. Outcome-exposure accounting

- `A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED`
- `FORMAL_PHASE2_CALL_PLAN_ENTRIES = 54`
- `COMPLETED_FORMAL_SLOTS = 0`
- `PENDING_FORMAL_SLOTS = 54`
- `REAL_CASE_RERANKER_CALLS = 0`
- `FORMAL_RERANKER_CALLS_EXECUTED = 0`
- `MODEL_SMOKE_TESTS = 0`
- `ANALYZER_CALLS = 0`
- `EMBEDDING_CALLS = 0`
- `QA_CALLS = 0`
- `VERIFIER_CALLS = 0`
- `JUDGE_CALLS = 0`
- `PHASE1_SELECT_V2_RUNS = 0`
- `POSTGRESQL_WRITES = 0`
- `QDRANT_WRITES = 0`
- `INGESTION = 0`
- `REINDEX = 0`
- `NOVEL_VALIDATION_RUNS = 0`
- `NOVEL_HOLDOUT_RUNS = 0`
- `PROTECTED_DATASET_ACCESS = 0`

## 14. Lifecycle

```text
D3.5-A6-PHASE1 = COMPLETE / BOUNDED_ADMISSION_PROTOTYPE_AND_REPLAY_IMPLEMENTATION_FROZEN
D3.5-A6-PHASE1-R1 = COMPLETE / REPLAY_SURFACE_METADATA_AND_PER_ARM_ORIGIN_DIAGNOSTICS_CLOSED
D3.5-A6-PHASE1-R2 = COMPLETE / PRE_EXPOSURE_RERANKER_MODEL_CONTRACT_UPGRADED_AND_REFROZEN
D3.5-A6-PHASE2 = NOT_STARTED / READY_FOR_PAIRED_REPEATED_RERANKER_REPLAY
A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED
D4 = NOT_STARTED / BLOCKED
```

## 15. Exact next stage

The exact next stage is:

> **D3.5-A6 Phase 2 — Paired Repeated Reranker Replay**

Execution protocol:
1. Execute the 54 formal slots strictly in the frozen cyclic schedule.
2. Persist raw `ranked_object_ids` per slot.
3. Compute evaluator metrics (`DELTA_K`, `CAUSAL_DELTA_K`, `REGRESSION_K`, `SELECTED_ADMISSION_BUDGET`, scientific verdict) only after all 54 slots complete.
4. Requires separate explicit user authorization before execution.
