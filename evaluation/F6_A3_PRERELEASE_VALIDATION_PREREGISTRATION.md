# F6-A Attempt 3 — Prerelease Validation & Generalization Gate (Preregistration)

Preregistered BEFORE the first scientific call; this artifact is immutable
after commit (freeze-time identity lives in the candidate manifest / freeze
receipt). Companion contract:
`evaluation/f6_a3_prerelease_validation_preregistration.json`.

## 1. Attempt identity

- Candidate ID: `f6a-rc3-20260914` (fresh; f6a-rc1/rc2 identities and all
  prior run IDs are never reused).
- Preregistration baseline HEAD: `1f03bbd`
  ("Reconcile Gold-9 release authority bindings").
- Product-behavior lineage HEAD: `d323f79` ("Repair FR2 source obligation
  boundaries" — Cluster A + Cluster D, accepted by FR2-R1); `d323f79..HEAD`
  contains no product QA drift (verified in A0).
- Continuous execution after the historical Attempt-3 preflight HOLD
  (zero outcome) and the GOLD-9 authority reconciliation.

## 2. Frozen scientific contracts

- **Gold:** m6-benchmark-v2.9 (`evaluation/benchmarks/v2_9/gold_questions.yaml`),
  120-question universe, `dataset_sha256 = eaacd3ed…`, status
  `approved_exposed_development_benchmark_v2_9`, official-ready and
  structurally valid; authority resolution shared by freezer/evaluator via
  `newest_signed_exposed_gold_dir` (GOLD-9).
- **Calibration:** `phase_b_t3_product_language_scope_v6`
  (`fe56d4ca…`), compatible with v2.9 (version + file SHA + split +
  overrides + declared/derived ID equality).
- **Formal-English selector:** derived **59 IDs**,
  `sha256 = e27ef67a…` (count derived, not hard-coded); 21 non-English dev
  IDs excluded. `executed_case_ids == formal_product_scope_ids` required.
- **Models:** generation = `gemini-3.8-flash`; effective verification =
  `gemini-3.8-flash` (no separate verification model configured); offline
  judge = `gemini-3.8-flash`; embedding = `gemini-embedding-2` (3072 dims);
  distinct generation/verification client paths.
- **Prompts:** set version `3.10.1`, fingerprint `23d73b03…` (FR2-R1 changed
  no prompt).
- **Corpus/runtime:** index fingerprint `8172f9a6…`
  (`panda_knowledge_v1`); Docker `postgres:17-alpine` + `qdrant:v1.15.5`
  (running, healthy).
- **Mode:** `legacy_question_core` (actual production default; no silent
  promotion of coverage modes).
- **Thresholds:** identical to the Attempt-1/2 preregistered set — no
  relaxation; gate evaluation uses the corrected R1/R1-R1/R1-R1-R1 semantics
  (`f6a_gate_evaluation.py` over canonical `aggregate_metrics`); missing
  mandatory measurement is INCOMPLETE.
- **Release score:** answered → answer_point_coverage; else 1.0/0.0 by
  expected-status correctness; mean over the complete cohort (aggregate, not
  itself a gate).
- **A2 ablation:** `disable_query_expansion_injection` runtime overlay on the
  exact same cohort; `BENCHMARK_DEPENDENCY ≤ 0.05`; runs only if A1 passes.
- **A4 Generalization Gap:** formal Gold release score − novel_validation
  release score ≤ 0.10; novel_dev is not the gap cohort.
- **A5 composer audit:** `composer_new_fact_rate == 0`; ≥ 10 eligible pairs
  and composed preferred > deterministic preferred; pairs only from this
  attempt's frozen records; insufficient applicability → INCONCLUSIVE.

## 3. Stage order and fail-fast

```text
A1 Gold formal full (f6a-rc3-gold-formal-full-20260914, mode=full)
  → A2 ablation (f6a-rc3-gold-formal-ablation-20260914)
  → A3 novel_dev (f6a-rc3-novel-dev-full-20260914)
  → A4 novel_validation (f6a-rc3-novel-validation-full-20260914)
  → A5 composer audit (f6a-rc3-composer-audit-20260914)
  → gate decision
```

Any mandatory gate failure stops scientific execution immediately. No repair,
no pass chasing, no candidate mutation. Immutable receipts are created
immediately after each completed stage, before case-level diagnosis.
Resume only under identical frozen identity (candidate/preregistration/run
ID/models/prompt/Gold/selector/index/runtime); 429-style provider errors may
be retried under the established infrastructure-recovery contract with
failed-attempt usage counted.

## 4. Protected cohorts and accounting

novel_validation = PRISTINE_FOR_CURRENT_LINEAGE until the first Attempt-3 A4
outcome; the exposure transition is recorded explicitly if A4 runs. Holdout
access = 0 throughout; F6-B is not authorized in this task. Zero scientific
calls before freeze; exact Attempt-3 usage reported at closeout with
stage/role breakdown (unrecoverable sub-roles reported as
NOT_SEPARATELY_RECOVERABLE_FROM_STORED_RECORDS); Attempt-1/2 usage never
merged.
