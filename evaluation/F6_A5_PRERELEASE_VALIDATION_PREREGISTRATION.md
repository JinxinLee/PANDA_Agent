# F6-A Attempt 5 — Fresh Preregistration, Candidate Freeze, and Continuous Pre-Release Validation

## Status

`PREREGISTERED / NO SCIENTIFIC OUTCOME OBSERVED`

This artifact freezes the Attempt-5 execution contract before candidate freeze and before any scientific/model-backed call. The machine-readable authority is `evaluation/f6_a5_prerelease_validation_preregistration.json`.

## Fresh-attempt legitimacy

`SAME_PRODUCT_LINEAGE_FORMAL_REPEAT = PROHIBITED`. Attempt 5 is eligible only because a material product change occurred after the Attempt-4 lineage: generic answer-obligation completeness (`production_answer_obligations_v1`), accepted at product-development HEAD `eda7d932a9b1b7b65436cba01e247859a6f9e056`. The subsequent release-identity repair `8f61aee414aa9fa2da0e3a6bbb2f767eadb7da4c` is identity/provenance-only and completes the freeze authority for that candidate; it does not replace the product-behavior lineage HEAD. Attempt 5 validates the new candidate, not another stochastic realization of the old one.

- Previous product-behavior lineage HEAD: `d3a1b274b2784399a7dc51b094a17e466d208b50` (Attempt 4).
- Current product-behavior lineage HEAD: `eda7d932a9b1b7b65436cba01e247859a6f9e056`.

## Material product change

Normal QA now runs `raw question → QuestionDecomposer → 1–5 question-only semantic obligations → generation with authoritative answer points → support + coverage verification → missing_answer_point_ids → at most one bounded evidence-backed revision → final verification / coverage audit` under `production_answer_obligations_v1`. The production path intentionally does not promote E3 missing-point retrieval, candidate capture, cross-pass global reselection, or the retained-support ledger.

## Frozen authority and identity

- Starting HEAD: `8f61aee414aa9fa2da0e3a6bbb2f767eadb7da4c`.
- Candidate ID: `f6a-rc5-20260919`.
- Runtime answer-point mode: `production_answer_obligations_v1`.
- Gold: `m6-benchmark-v2.10`, `evaluation/benchmarks/v2_10/gold_questions.yaml`, SHA-256 `bdce5cbdc0a6f1645d7350b87bc2f289265c3d67311dab4b12e488b9dc499513`, `official_ready = true`, `structurally_valid = true`.
- Calibration: `phase_b_t3_product_language_scope_v7`, SHA-256 `ad68df096fc82d6c52bd984e44e99573e6b47e5047b3d522ae750a93188c49cd`, compatible with Gold v2.10.
- Formal-English selector: 59 IDs, SHA-256 `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5`; non-English cohort 21 IDs.
- Prompt set: `3.10.1`; canonical corrected `prompt_fingerprint()` SHA-256 `35f1dd3cbcd6cb636e2e92e7af28cb95415787e8d920c99c3b070eae86a8f097`, binding `QUESTION_DECOMPOSITION_SYSTEM_PROMPT`, `QUESTION_DECOMPOSITION_PROMPT_VERSION = 2.0.0`, and `QUESTION_DECOMPOSITION_SCHEMA_VERSION = e1.question_decomposition.v2` together with all other active formal model prompts. `candidate_manifest.prompt_hash == evaluation_manifest.prompt_hash == prompt_fingerprint()` is required.
- Generation/effective verification/runtime composer/evaluation judge: `gemini-3.8-flash`; embedding: `gemini-embedding-2`, 3072 dimensions.
- Index fingerprint: `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`; collection `panda_knowledge_v1`; 104,973 points; PostgreSQL 17-alpine and Qdrant v1.15.5.
- Source manifest SHA-256 `9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94`; retrieval policy SHA-256 `fb2cd99bf500d5924931cf0fa6d5ea801efc7939b4c469fad8fbc0b5b082ced9`; query expansion SHA-256 `84c93c94e70e8e7819a2cd8ecdd18f8fce41996d616d5ebc34fe2deb823e039a`.

## Ordered execution contract

1. A1 runs the complete 59-case formal-English Gold cohort in full mode under the frozen candidate. `executed_case_ids == formal_product_scope_ids` is required; no missing, extra, duplicate, or reused Attempt-4 records. Any failed or incomplete mandatory gate terminates the downstream chain.
2. A2, only after A1 PASS, applies `disable_query_expansion_injection` to the identical cohort with a fresh run ID. `A1 release score - A2 release score <= 0.05` is mandatory.
3. A3, only after A2 PASS, runs the complete authoritative `novel_dev` cohort. All hard-safety invariants are mandatory; no tuning follows observation.
4. A4, only after all predecessors pass, first verifies `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`, then accesses the complete authoritative `novel_validation` cohort with no subset selection, steering, replacement, product tuning, or quality retries. The first scientific result permanently records `novel_validation = EXPOSED_FOR_CURRENT_LINEAGE`. `A1 release score - A4 release score <= 0.10` and all frozen validation gates are mandatory.
5. A5, only after A4 PASS, audits eligible composer pairs already present in A1 and A4. `composer_new_fact_rate == 0` is mandatory. Readability is applicable only with at least 10 eligible pairs; no new QA runs may manufacture pairs.

The release-score formula is frozen as: answered cases use answer-point coverage; other expected statuses use 1.0 for a correct status and 0.0 otherwise; the stage score is the arithmetic mean over a complete cohort. It is not an additional gate.

## New decomposition accounting

Normal production now calls `QuestionDecomposer` per case. These calls count toward formal Attempt-5 usage. Where stored accounting allows, decomposition usage is reported separately; if it cannot be separately recovered, the record states `NOT_SEPARATELY_RECOVERABLE_FROM_STORED_RECORDS` and is never estimated.

## Recovery and receipt contract

Retryable provider or transport failures remain resumable under the identical frozen candidate, preregistration, and run identity (`RECOVERY_PENDING` while recoverable). Successful cases are never rerun for quality, terminal exceptions do not loop, and every failed attempt remains in cumulative usage. An irrecoverable incomplete cohort is `COMPLETE / INCONCLUSIVE / PRE_RELEASE_EXECUTION_INCOMPLETE`; no PASS/FAIL decision is made on a still-recoverable incomplete cohort.

Every scientific stage follows this chronology: complete the stage and permitted recovery, establish cohort completeness, persist gate inputs and outputs, seal the immutable receipt, validate it, and only then expose case-level diagnostics. Standalone gate invocation uses the repaired environment/bootstrap path. A receipt failure prevents diagnostic interpretation and downstream execution.

## Stop and protection rules

After A0 there are no product, retrieval, prompt, decomposition-semantic, evaluator, recovery, Gold, calibration, threshold, model, ablation, novel-cohort, or composer-contract changes within Attempt 5. PASS, FAIL, HOLD, and INCONCLUSIVE are legitimate outcomes; there is no pass chasing and no cost-aware protocol change inside this attempt.

Attempt-4 case-level comparison is allowed only after receipt sealing, for diagnosis only, and no difference may be attributed solely to the completeness mechanism without establishing attribution. No tuning follows from such observations inside Attempt 5.

Protected holdout access, protected-content leakage, and F6-B execution remain zero. Even a terminal `COMPLETE / PASS / HOLDOUT_ELIGIBLE` outcome does not authorize F6-B; it requires separate explicit authorization.

At preregistration time, PANDA scientific/evaluation usage is `0 calls / 0 tokens`, and `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`.
