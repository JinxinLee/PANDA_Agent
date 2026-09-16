# F6-A Attempt 4 — Continuous Prerelease Validation Preregistration

## Status

`PREREGISTERED / NO SCIENTIFIC OUTCOME OBSERVED`

This artifact freezes the Attempt-4 execution contract before candidate freeze and before any scientific/model-backed call. The machine-readable authority is `evaluation/f6_a4_prerelease_validation_preregistration.json`.

## Frozen authority and identity

- Starting HEAD: `cedebea9261db68b532c0e5477c52ddc3a8a7d1c`.
- Product behavior lineage: `d3a1b274b2784399a7dc51b094a17e466d208b50`.
- Candidate ID: `f6a-rc4-20260916`.
- Gold: `m6-benchmark-v2.10`, `evaluation/benchmarks/v2_10/gold_questions.yaml`, SHA-256 `bdce5cbdc0a6f1645d7350b87bc2f289265c3d67311dab4b12e488b9dc499513`.
- Calibration: `phase_b_t3_product_language_scope_v7`, SHA-256 `ad68df096fc82d6c52bd984e44e99573e6b47e5047b3d522ae750a93188c49cd`.
- Formal-English selector: 59 IDs, SHA-256 `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5`.
- Runtime answer-point mode: `legacy_question_core`.
- Prompt set: `3.10.1`, SHA-256 `23d73b036646ec62f3095fac4bdfafdfc7ecf6676fd27d18475b86773db4e6d5`.
- Generation/effective verification/evaluation judge: `gemini-3.8-flash`; embedding: `gemini-embedding-2`, 3072 dimensions.
- Index fingerprint: `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`.
- Runtime data services: `postgres:17-alpine` and `qdrant/qdrant:v1.15.5`.

## Ordered execution contract

1. A1 runs the complete 59-case formal-English Gold cohort in full mode. Any failed or incomplete mandatory gate terminates the downstream chain.
2. A2, only after A1 PASS, applies `disable_query_expansion_injection` to the identical cohort. `A1 release score - A2 release score <= 0.05` is mandatory.
3. A3, only after A2 PASS, runs the complete authoritative `novel_dev` cohort. All hard-safety invariants are mandatory; no tuning follows observation.
4. A4, only after A3 PASS, accesses the complete authoritative `novel_validation` cohort. Its first model result permanently changes the lineage state to `EXPOSED_FOR_CURRENT_LINEAGE`. `A1 release score - A4 release score <= 0.10` and all frozen validation gates are mandatory.
5. A5, only after A4 PASS, audits eligible composer pairs already present in A1 and A4. `composer_new_fact_rate == 0` is mandatory. Readability is applicable only with at least 10 eligible pairs; no new QA runs may manufacture pairs.

The release-score formula is frozen as: answered cases use answer-point coverage; other expected statuses use 1.0 for a correct status and 0.0 otherwise; the stage score is the arithmetic mean over a complete cohort. It is not an additional gate.

## Recovery and receipt contract

Retryable provider or transport failures remain resumable under the identical frozen candidate and run identity. Successful cases are never rerun for quality, terminal exceptions do not loop, and every failed attempt remains in cumulative usage. A recoverable incomplete cohort is `RECOVERY_PENDING`, while an irrecoverable incomplete cohort is `COMPLETE / INCONCLUSIVE / PRE_RELEASE_EXECUTION_INCOMPLETE`.

Every scientific stage follows this chronology: complete the stage and permitted recovery, establish cohort completeness, persist gate inputs and outputs, seal the immutable receipt, validate it, and only then expose case-level diagnostics. A receipt failure prevents diagnostic interpretation and downstream execution.

## Stop and protection rules

After A0 there are no product, retrieval, prompt, evaluator, recovery, Gold, calibration, threshold, model, ablation, cohort, or composer-contract changes within Attempt 4. PASS, FAIL, HOLD, and INCONCLUSIVE are legitimate outcomes; there is no pass chasing.

Protected holdout access, protected-content leakage, and F6-B execution remain zero. Even a terminal `COMPLETE / PASS / HOLDOUT_ELIGIBLE` outcome does not authorize F6-B.

At preregistration time, PANDA scientific/evaluation usage is `0 calls / 0 tokens`, and `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`.
