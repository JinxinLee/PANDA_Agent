# F6-A — Prerelease Validation & Generalization Gate: Preregistration (selector-defined)

Frozen before the first F6-A scientific model call. No measured outcome values
appear in this document. Machine-readable counterpart:
`evaluation/f6_a_prerelease_validation_preregistration.json`.

**Supersession note.** This preregistration supersedes the earlier
`evaluation/F6_A_PRE_RELEASE_VALIDATION_PREREGISTRATION.md` (and its JSON),
which scheduled a 120-question full-benchmark run. Under the corrected F6-A
protocol the formal Gold cohort is the exact formal-English product-scope
selector output defined below; "the benchmark contains 120 questions" is not a
cohort criterion. The earlier artifacts remain as historical records of the
superseded plan; the terminated 9-case partial run under that plan
(`data/evaluation/runs/f6a-rc1-gold-full-20260913`, preserved unmodified) is
not F6-A evidence.

## 1. Implementation and candidate identity

- Implementation HEAD at preregistration: `f30d907` ("Prepare selector-defined
  F6-A evaluation identity"; lineage includes the A0 infrastructure commits
  `6e92a37`, `7b02db2`, `c9227f8`).
- Candidate ID: `f6a-rc1-20260913` — refrozen after this preregistration
  commit against this HEAD (the earlier freeze under the superseded plan was
  never bound to any scientific run and its manifest is superseded).
- Runtime mode (primary): `legacy_question_core` (`runtime_e1_v2` remains
  explicit-selection-only and is NOT a competing arm).

## 2. Model / prompt / corpus identities

- Generation: `gemini-3.8-flash`; product semantic verification:
  `QA_VERIFICATION_MODEL_ID` absent → effective `gemini-3.8-flash` (same
  model, distinct F4 client paths); offline judge: `gemini-3.8-flash`;
  embedding `gemini-embedding-2` / 3072.
- Prompt set: `3.10.1`, hash
  `23d73b036646ec62f3095fac4bdfafdfc7ecf6676fd27d18475b86773db4e6d5`.
- Index fingerprint: `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`
  (collection `panda_knowledge_v1`).
- Packages: python 3.13.14, google-genai 2.13.0, langgraph 1.2.11, psycopg
  3.3.4, qdrant-client 1.19.0.
- Docker contract: Option A (release-critical; postgres + qdrant image
  identities captured non-empty).

## 3. Product-language calibration and exact formal Gold cohort

- Calibration identity: `phase_b_t3_product_language_scope_v3`, artifact SHA-256
  `f8d05d8769ff84ba2199117f1471a3b8f98cea87397c79ac655094d6815eccac`.
- Predecessor: `phase_b_t3_product_language_scope_v2` (bound to the
  pre-D4-A2-R1 Gold SHA `b5406e36…`), reconciled mechanically: the authorized
  g021 correction changed criticality metadata only, and re-derivation on the
  current dataset reproduces the declared classification exactly. No fresh
  human review claimed.
- Current Gold: m6-benchmark-v2.6, 120 questions total, dataset SHA-256
  `6f12d54b…`, approved, structurally valid.
- **Exact formal-English product-scope IDs (59, selector-derived; the count is
  derived data, not a normative constant)** — stored verbatim in the JSON
  counterpart under `formal_english_case_ids`:
  `g001–g037, g039–g042, g044, g047, g050–g052, g055, g057–g060, g105, g108,
  g110, g112–g115, g119` (full ordered list in JSON).
- Selector hash: `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5`
  (canonical sorted-ID JSON, recorded in the candidate manifest).
- Non-English dev IDs (21): outside the formal product gate; NOT executed in
  F6-A. Challenge/regression splits: NOT automatically executed (§10.3).
- Bootstrap reference `english_gold_stratified_bootstrap_v1.json` (24
  retrieval / 16 QA) is preserved unchanged as historical low-cost reference
  only.

## 4. Run IDs (fresh, immutable)

```text
f6a-rc1-gold-formal-full-20260913      (Stage A1 — formal Gold product gate, mode=full)
f6a-rc1-gold-formal-ablation-20260913  (Stage A2 — benchmark-dependency ablation, mode=full)
f6a-rc1-novel-dev-full-20260913        (Stage A3 — exposed-development diagnostic, mode=full)
f6a-rc1-novel-validation-full-20260913 (Stage A4 — pristine validation, mode=full)
f6a-rc1-composer-audit-20260913        (Stage A5 — composer empirical audit, evaluation-only judge)
```

## 5. Completeness contract

```text
executed_case_ids == formal_english_case_ids (exact set equality; no missing,
no extra, no duplicates) under the frozen candidate identity
```

No `--limit`. A partial cohort cannot PASS. The runner computes the product
gate from selector completeness (Stage A0 §5.5 semantics); full-dev execution
is not a prerequisite.

## 6. Release score formula

```text
expected_status == answered → case_release_score = answer_point_coverage
else → case_release_score = 1.0 if expected_status_correct else 0.0
release_score = mean over the complete formal cohort
```

None is never zero; missing required metrics make the case incomplete
(excluded from numerator AND denominator, reported by ID); exceptions are hard
completion failures; denominators always reported
(`evaluation_runner.f6a_release_score`).

## 7. Gold quality thresholds (preregistered, current evaluator semantics)

```text
gold_recall_at_10 >= 0.95
final_evidence_recall >= 0.90
critical_final_evidence_recall == 1.00
intent_accuracy >= 0.90
per_intent_gold_recall_at_10 >= 0.75
per_intent_intent_accuracy >= 0.80
expected_status_accuracy >= 0.975
citation_integrity == 1.00
wrong_version_evidence_count == 0
forbidden_evidence_count == 0
required_source_coverage_answered >= 0.97
identifier_hallucination_rate < 0.03
paper_code_dual_source_rate == 1.00 when applicable
answer_point_coverage >= 0.90
critical_answer_point_miss_count == 0
contradiction_count == 0
major_unsupported_claim_count == 0
unhandled_exception_count == 0
```

## 8. Cross-cohort hard safety invariants

For Gold (formal cohort), novel_dev, novel_validation where applicable:
citation_integrity == 1.0; wrong_version/forbidden evidence counts == 0;
contradictions == 0; major unsupported claims == 0; critical answer-point
misses == 0; unhandled exceptions == 0. Plus: no record corruption, no mixed
identities, no missing scheduled case. novel_dev hard-safety failure stops
before novel_validation.

## 9. Generalization Gap

```text
GENERALIZATION_GAP = formal_Gold_release_score - novel_validation_release_score
GENERALIZATION_GAP <= 0.10
```

Secondary diagnostics (reported, never substituting the primary): Recall@5/@10/
@20 gaps, MRR gap, final-evidence-recall gap, answer-point-coverage gap,
expected-status-accuracy gap.

## 10. Benchmark Dependency

```text
BENCHMARK_DEPENDENCY = formal_Gold_primary_release_score
                     - formal_Gold_ablation_release_score
BENCHMARK_DEPENDENCY <= 0.05
```

Ablation definition (evaluation-only runtime overlay, recorded in
`evaluation/f6a_ablation_manifest.json`):
`ablation_id = disable_query_expansion_injection` — the isolated ablation
process patches `Retriever.load_query_expansions` to an empty rule set,
disabling the D4-owned reviewed trigger-rule layer; everything else identical
to the frozen candidate. Static justification: F1/PF-LR1/F2/F3 retired the
benchmark-shaped semantics and fixed locators; the remaining approved
compatibility surface in the retrieval path is the reviewed query-expansion
trigger layer. No novel_validation ablation.

## 11. Composer empirical audit contract

- Eligible pairs: ANSWERED + composer accepted + >= 2 verified claims, from
  frozen Gold(formal) + novel_validation records; no product rerun; no holdout.
- Factuality: `composer_new_fact_rate == 0` (offline judge over verified
  claims vs composed answer) — else FAIL.
- Readability: blinded pairwise, counterbalanced by the first embedded case-ID
  number (even → composed labeled A); judge readability/organization only.
  Gate: `eligible_pairs >= 10 AND composed_preferred > deterministic_preferred`;
  `< 10` pairs → `INCONCLUSIVE / COMPOSER_READABILITY_EVIDENCE_INSUFFICIENT`;
  deterministic >= composed → FAIL.
- Reported: attempt/accept/fallback counts and rates.

## 12. Fail-fast order and no-holdout boundary

A1 (formal Gold full) → A2 (ablation) → A3 (novel_dev diagnostic) → A4
(novel_validation) → A5 (composer audit) → gate decision. Failure of any
preregistered gate freezes the terminal F6-A state and stops. F6-A never
discovers, mounts, or accesses the protected holdout; with no candidate frozen
`candidate_changes_after_freeze` = NOT_REACHED. Post-freeze: zero
behavior-changing edits until the verdict; candidate identity verified before
each primary stage; evaluation artifacts may leave the tree dirty without
invalidating the frozen identity.

## 13. Infrastructure / evaluator-defect rules

Infrastructure interruption may resume the same run ID/candidate/preregistration
with completed records reused; otherwise
`INCONCLUSIVE / INFRASTRUCTURE_INCOMPLETE`. Deterministic evaluator defects
after outcomes: immutable offline rescore only, provenance recorded, no
threshold change; if product behavior would need to change → the candidate is
invalid and F6-A does not continue as if unchanged.

## 14. Terminal outcome mapping

```text
PASS  → F6-A = COMPLETE / PASS / PRERELEASE_VALIDATION_AND_GENERALIZATION_GATE_PASSED
        F6-B = NOT_STARTED / READY_FOR_SEPARATE_AUTHORIZATION
FAIL  → F6-A = COMPLETE / FAIL / <failed gate>; F6-B = LOCKED / F6_A_DID_NOT_PASS
INCONCLUSIVE → F6-A = COMPLETE / INCONCLUSIVE / <reason>; F6-B = LOCKED
HOLD (pre-outcome) → F6-A = HOLD / <precondition>; scientific calls = 0
```

`DEFAULT_PROMOTION = NOT_PERFORMED_BY_F6_A`; Phase F is closed only by a
separately authorized F6-B.
