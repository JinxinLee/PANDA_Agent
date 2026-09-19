# Identifier Catalog Evaluator Repair + Attempts 1–5 Historical Offline Identifier Rescore

Status: `COMPLETE / PASS / IDENTIFIER_EVALUATOR_REPAIRED_AND_HISTORY_RESCORED`

> **Superseded in part (R1):** `evaluation/IDENTIFIER_CATALOG_EVALUATOR_R1_EXACT_OWNERSHIP_AND_PROVENANCE.md` supersedes this record's identifier-metric values (exact-ownership semantics) and its record-count terminology (`records` / `records_in_store` are replaced by the normalized provenance fields `raw_rows_in_store` / `unique_case_count` / `completed_case_count` / `identifier_gold_applicable_case_count` / `identifier_measured_record_count`; the Attempt-1 60-row store holds one complete duplicate `g119` execution and Attempt 3's store holds the preserved `g013` provider-exception row, which is Gold-applicable but unmeasured). The generic repair, test matrix, six Attempt-5 false-positive corrections, and all verdict conclusions stand unchanged.

Zero scientific calls. Machine-readable summary: `evaluation/identifier_catalog_evaluator_repair_and_offline_rescore.json`; per-attempt forward-only rescore artifacts: `evaluation/identifier_catalog_evaluator_repair/attempt_{1..5}_identifier_rescore.json` plus `summary.json`.

## 1. Defect and root cause

`build_identifier_catalog()` collected only `locator.symbol` values, paths, and `class/struct/enum <Type>` declaration names from allowed locked-corpus objects. Namespace-scoped enum members and other qualified symbols that occur verbatim in corpus text (for example `LumiFit::THETA_X`) were invisible to the catalog, so a qualified identifier could be verbatim-present in allowed corpus text — even inside the very evidence object a claim cites — and still be classified as a hallucination. The pre-existing unqualified-tail fallback (`tail in catalog["symbols"]`) additionally allowed a fabricated namespace qualification to be legitimized by a bare corpus symbol.

## 2. Repair (generic, deterministic, small)

`src/panda_agent/evaluation.py` only:

- `build_identifier_catalog()` now also harvests qualified/scoped identifier literals matching the generic grammar `[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)+` verbatim from allowed locked-corpus object text into the symbol catalog, and records each qualification head (`Outer`, `Outer::Inner`) in a new `namespaces` set. No identifiers, namespaces, or case IDs are hardcoded.
- The qualified-symbol existence check is factored into `_qualified_symbol_exists()`: a qualified identifier exists when its exact literal is catalogued, or when its unqualified tail is a known symbol **and** its qualification head is a namespace actually seen in allowed corpus text (closing the namespace-spoof hole; the fallback was tightened, not broadened, because the T4 red test demonstrated the old fallback created hallucination false negatives).
- Existence and evidence support remain separate metrics: an identifier that exists but is not covered by the claim's cited evidence still lands in `unsupported_identifiers`.
- `allowed_source_versions` filtering is unchanged and applies to the new collection paths; symbols present only in disallowed versions stay nonexistent.
- The existing cache semantics are reused unchanged (the catalog is still built once per lookup/version scope).

`EVALUATOR_CONTRACT_CHANGE = true`; `MATERIAL_PRODUCT_CHANGE = false`. No product behavior changed; no new candidate; no Attempt 6.

## 3. Test-first sequence (RED → GREEN)

New suite `tests/unit/test_identifier_catalog_repair.py` (fixture-based, no production corpus dependency for the generic matrix):

- RED (before the repair, 5 failed / 4 passed): T1 `test_t1_qualified_literal_exists` FAILED (`'ExampleNS::VALUE_A' unexpectedly found in ['ExampleNS::VALUE_A']` — verbatim corpus identifier classified as hallucinated); T2 FAILED; T8 FAILED; T7 FAILED (existence/support separation broken); T4 FAILED (`FakeNS::VALUE_A` legitimized by a bare corpus symbol via the tail fallback). T3, T32, T5/T33, and T6 passed, confirming the controls targeted exactly the defect.
- GREEN (after the repair): all 9 generic tests pass, plus the production-corpus `Attempt5IdentifierRegressionTests` — 10/10.
- Coupled evaluator regressions: `test_evaluation.py`, `test_evaluation_runner.py`, `test_f6a_gate_evaluator.py`, `test_f6a_release_infrastructure.py`, `test_m6_evaluation.py` → 89 passed; the only failures are the two known pre-existing `test_m6_evaluation.py` fixture-debt tests and one pre-existing stale assertion (`test_v26_is_default_and_signed_dry_rescore_preserves_real_failures`, which expects v2.6 as the default Gold dataset — it fails identically on the unmodified tree and is unrelated to this repair).

## 4. Attempts 1–5 offline rescore (zero model calls)

Each rescore binds the historical run ID, mechanically verified original Gold identity (manifest `gold_dataset_hash` == dataset SHA-256), immutable stored records, and the repaired evaluator; only identifier-related deterministic fields are reinterpreted. Non-identifier metrics, receipts, matrices, and terminal verdicts are untouched. Attempt 3 remains historically incomplete (58/59) and no case was manufactured.

| Attempt | Gold | records | old count/denominator (rate) | new count/denominator (rate) | cleared events | introduced |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | v2.6 | 59 | 0/121 (0.0) | 0/121 (0.0) | — | — |
| 2 | v2.6 | 59 | 0/155 (0.0) | 0/155 (0.0) | — | — |
| 3 | v2.9 | 58 (g013 historically missing) | 0/177 (0.0) | 0/177 (0.0) | — | — |
| 4 | v2.10 | 59 | 2/173 (0.011561) | 0/173 (0.0) | g060: `LumiFit::THETA_X`, `LumiFit::THETA_Y` | — |
| 5 | v2.10 | 59 | 6/130 (0.046154) | 0/130 (0.0) | g060 ×2, g113 ×4 | — |

Denominators reproduce the historical gate matrices exactly (121/155/177/173/130), confirming the rescoring aggregation matches the original semantics. No new hallucination events were introduced by the tightened namespace check in any attempt.

### Attempt-5 expected check

The post-A5 review predicted `6/130 → 0/130` (COUNTERFACTUAL / NON-AUTHORITATIVE). Verified mechanically: repaired Attempt-5 `identifier_hallucination_count = 0`, `identifier_hallucination_rate = 0.0` on the identical 130-mention denominator; all six alleged hallucinations are now recognized as existing in the locked corpus.

## 5. Counterfactual gate impact (COUNTERFACTUAL / NON-AUTHORITATIVE)

| Attempt | Old identifier gate | Counterfactual repaired gate |
| --- | --- | --- |
| 1 | PASS | PASS |
| 2 | PASS | PASS |
| 3 | PASS | PASS |
| 4 | PASS | PASS |
| 5 | FAIL | PASS |

Historical terminal verdicts are unchanged in every case. Attempt 5 remains `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED` because `critical_final_evidence_recall` and `critical_answer_point_miss_count` still failed under its authoritative contract.

## 6. Post-A5 review erratum

Recorded forward-only in `evaluation/POST_A5_FAILURE_OWNERSHIP_AND_GATE_VALIDITY_REVIEW.md` (§16) and the review JSON (`erratum` key): the earlier mechanism wording overstate­d generator self-mapping as the coverage authority. Refined ownership: `g013.p3` = A1 bounded-revision recovery insufficiency; `g023.p3`/`g047.p1` = A1 answer-content omission with possible V2 semantic-coverage false acceptance; generator self-declared answer-point mappings = NOT ESTABLISHED AS THE CAUSAL COMPLETENESS AUTHORITY (product code: the semantic coverage reviewer independently remaps claims; `verified_mappings` comes from `_validate_answer_point_review` over the verifier-returned review). High-level classifications, gate dispositions, and the verdict are unchanged; the historical commit is not rewritten.

## 7. Accounting and protected state

- `PANDA scientific/evaluation calls = 0`; `PANDA scientific/evaluation tokens = 0`.
- `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`; `holdout access = 0`; `protected-content leakage = 0`; `F6-B execution = 0`.
- `candidate frozen = false`; `Attempt 6 preregistered = false`; `Attempt 6 executed = false`.

## 8. Attempt-6 readiness

```text
ATTEMPT_6_READINESS = NOT_READY
```

Remaining blockers (unchanged by this task): g039 Gold reconciliation; critical-final-evidence metric construct redesign/reconciliation; the two confirmed product defects; focused T0/T1/T2 development evidence; no materially new product candidate.

## 9. Next task recommendation

`F6-A EVALUATION-CONTRACT RECONCILIATION / CRITICAL-EVIDENCE EQUIVALENCE + g039 GOLD CORRECTION + HARD-SAFETY RECLASSIFICATION` — this next task must still not run Attempt 6.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`
