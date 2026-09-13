# F6-A Attempt 2 — Prerelease Validation & Generalization Gate (Preregistration)

Preregistered BEFORE the first scientific call. Companion machine-readable
contract: `evaluation/f6_a2_prerelease_validation_preregistration.json`.

## 1. Attempt identity

- Candidate ID: `f6a-rc2-20260913` (fresh; attempt-1 identities
  `f6a-rc1-20260913` / `f6a-rc1-gold-formal-full-20260913` are never reused).
- Preregistration baseline HEAD: `619128b`
  ("Prepare F6-A attempt 2 release identity" — roadmap ten→nine correction
  only; no product change).
- Intervening development: F6-A-FR1 PASS; product-fix commit `45f14ba`
  ("Repair generic refusal and version-conflict handling").
- FR1 change-boundary audit (`557327e..HEAD`, src/ + configs/): exactly the
  two authorized behavior changes (repository-identity exclusion in the
  premise guard; bounded prepositional version-repository binding); zero
  unexpected changes to prompts, composer, verification role, ranking,
  expansions, Gold, thresholds, candidate mode, or calibration semantics.

## 2. Frozen scientific contracts

- **Gold:** m6-benchmark-v2.6, 120-question universe,
  `dataset_sha256 = 6f12d54b…`, manifest status
  `approved_exposed_development_benchmark_v2_6`.
- **Calibration:** `phase_b_t3_product_language_scope_v3`
  (`f8d05d87…`), compatibility verified (version + file SHA + split +
  overrides + declared/derived ID equality).
- **Formal-English selector:** `english_product_case_ids(dataset, "dev",
  calibration v3)` — derived count **59**,
  `sha256 = e27ef67a…` (identical to the attempt-1 selector identity; 59 is a
  derived result, not a hard-coded constant). 21 non-English dev IDs excluded.
- **Models:** generation = `gemini-3.8-flash`; no separate verification model
  configured (effective verification = `gemini-3.8-flash`); offline
  evaluation judge = `gemini-3.8-flash`; embedding = `gemini-embedding-2`
  (3072 dims); distinct generation/verification client paths.
- **Prompts:** prompt set version `3.10.1`, fingerprint `23d73b03…`.
- **Corpus/runtime:** index fingerprint `8172f9a6…` (collection
  `panda_knowledge_v1`, identity match verified); Docker release-critical
  runtime `postgres:17-alpine` + `qdrant:v1.15.5` (running, healthy).
- **Thresholds:** byte-identical to the attempt-1 preregistration; no
  relaxation after the attempt-1 FAIL. Gate evaluation uses the corrected
  R1/R1-R1/R1-R1-R1 semantics (canonical `aggregate_metrics` +
  `evaluation/scripts/f6a_gate_evaluation.py`).
- **Release score:** answered → answer_point_coverage; else
  1.0/0.0 by expected-status correctness; mean over the complete cohort;
  missing measurement is INCOMPLETE, not zero.
- **Benchmark dependency (A2):** primary − ablation release score ≤ 0.05;
  ablation = `disable_query_expansion_injection` runtime overlay on the exact
  same selector cohort; runs only if A1 passes.
- **Generalization gap (A4):** formal Gold release score −
  novel_validation release score ≤ 0.10; novel_dev is not the gap cohort.
- **Composer audit (A5):** `composer_new_fact_rate == 0`; readability gate
  requires ≥ 10 eligible pairs and composed preferred > deterministic
  preferred; pairs only from this attempt's frozen ANSWERED records; no QA
  rerun to manufacture pairs; insufficient applicability → INCONCLUSIVE.

## 3. Stage order and fail-fast

```text
A1 Gold formal full (selector cohort, mode=full, fresh run
    f6a-rc2-gold-formal-full-20260913)
  → A2 Gold ablation (same cohort, f6a-rc2-gold-formal-ablation-20260913)
  → A3 novel_dev (full manifest cohort; exposed development diagnostic)
  → A4 novel_validation (full frozen cohort; first model outcome ends
    PRISTINE_FOR_CURRENT_LINEAGE — transition recorded)
  → A5 composer audit (immutable attempt-2 records only)
  → gate decision
```

Any mandatory gate failure stops scientific execution immediately. No repair,
no pass-chasing, no candidate change until the verdict is frozen. Resume
after infrastructure interruption only under the established contract (same
candidate/preregistration/run ID, no behavior change, failed attempts
preserved and counted).

## 4. Usage accounting

Zero scientific/evaluation calls before candidate freeze. Exact totals
reported at closeout, broken down by Gold primary / ablation / novel_dev /
novel_validation / composer audit / runtime / verifier / judge. Attempt-1
historical usage (formal 383 calls / 3,348,432 tokens; superseded 9/120 plan
61 calls / 339,150 tokens) is reported separately and never merged.

## 5. Protected cohorts

novel_validation = PRISTINE_FOR_CURRENT_LINEAGE until the first attempt-2
A4 outcome. Protected holdout access = 0 for the entire attempt; F6-B is not
authorized in this task.
