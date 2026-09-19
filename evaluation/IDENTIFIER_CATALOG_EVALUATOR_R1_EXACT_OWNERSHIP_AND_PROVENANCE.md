# Identifier Evaluator R1 — Qualified-Symbol Exact-Ownership Boundary + Historical Rescore Record-Provenance Reconciliation

Status: `COMPLETE / PASS / QUALIFIED_SYMBOL_OWNERSHIP_AND_RESCORE_PROVENANCE_RECONCILED`

Zero scientific calls. Machine-readable companion: `evaluation/identifier_catalog_evaluator_r1_exact_ownership_and_provenance.json`. Forward-only per-attempt rescore artifacts reissued under `evaluation/identifier_catalog_evaluator_repair/` (schema `identifier-rescore-r1-v1`, superseding the `identifier-rescore-v1` artifacts from commit `cbb02fcd81f4894445e7a012dd018c3d31065e74`).

This R1 preserves every substantive conclusion of the previous repair: the six Attempt-5 events (g060 `LumiFit::THETA_X`/`LumiFit::THETA_Y`; g113 `LumiFit::MC`/`LumiFit::MC_ACC`/`LumiFit::RECO`/`LumiFit::THETA_X`) remain confirmed evaluator false positives; the Attempt-4 counterfactual 2/173 → 0/173 and Attempt-5 counterfactual 6/130 → 0/130 stand; `MATERIAL_PRODUCT_CHANGE = false`, `EVALUATOR_CONTRACT_CHANGE = true`; all five historical terminal verdicts are unchanged.

## 1. Residual exact-ownership defect

The previous repair's `_qualified_symbol_exists()` still contained a combinatorial fallback: a known qualification head (`head in namespaces`) combined with an independently known bare tail (`tail in catalog["symbols"]`) could validate a qualified identifier that never occurs in the locked corpus. Independent existence of `A` and `B` is not evidence that `B` belongs to `A`:

```text
known head + known unrelated tail != qualified identifier exists
```

## 2. R1 repair (smallest evidence-backed rule)

`src/panda_agent/evaluation.py` only:

- `_qualified_symbol_exists()` now implements exact-ownership semantics: a qualified identifier exists only when that exact qualified form is established by allowed locked-corpus evidence — verbatim text (the catalog harvests qualified literals matching the generic grammar) or locator/declaration metadata (which enters `catalog["symbols"]`/`paths` directly). The head+tail combinatorial fallback and the `namespaces` head set were removed.
- The qualified-literal grammar, `allowed_source_versions` filtering, cache semantics, and the existence/support separation are unchanged. No C++ parser, no product behavior change, no Gold/threshold change.

Why this does not overcorrect (protocol §7): the real identifiers the previous repair correctly recognized (`LumiFit::THETA_X`, `LumiFit::MC`, `PndLmdModelFactory::generate2DModel`, `Lmd::Data::TrackPairInfo`, and every other legitimate qualified symbol in Attempts 1–5) all have exact verbatim corpus evidence — the R1 offline rescore re-derived identical denominators and zero newly hallucinated events, proving the combinatorial fallback was never load-bearing for a real identifier in any stored claim.

## 3. RED → GREEN

New R1 tests in `tests/unit/test_identifier_catalog_repair.py::QualifiedOwnershipBoundaryTests`:

- **RED (before the repair): 1 failed / 13 passed** — `test_r1_t1_known_head_plus_unrelated_known_tail_is_hallucinated` FAILED (`'ExampleNS::VALUE_A' not found in []`: known head `ExampleNS` + independently known bare tail `VALUE_A` legitimized the fabricated `ExampleNS::VALUE_A`). R1-T3 (nested exact literal), R1-T5 (wrong member), and R1-T6 (wrong owner) already passed and guard against overcorrection.
- **GREEN (after the repair): 14/14** — all four R1 boundary tests plus the full prior matrix (T1–T8 controls, namespace spoof, allowed-version boundary, exists/support separation, and the production-corpus `Attempt5IdentifierRegressionTests` keeping all six Attempt-5 false positives cleared).

## 4. Attempt-5 regression (R1-T9)

All six confirmed false positives remain cleared under exact-ownership semantics: `LumiFit::THETA_X`, `LumiFit::THETA_Y`, `LumiFit::MC`, `LumiFit::MC_ACC`, `LumiFit::RECO` are recognized as existing in the locked corpus and none is classified as hallucinated (production-corpus test + rescore artifact `attempt_5_identifier_rescore.json`: 0/130, `hallucinated_by_case = {}`).

## 5. Record-provenance reconciliation

Independently derived from the immutable run stores (not from the prior report):

### Attempt 1 — the 60↔59 discrepancy resolved

```text
raw_rows_in_store = 60
unique_case_count = 59
duplicate_case_ids = {"g119": 2}
exception_case_ids = []
completed_case_count = 59
identifier_applicable_case_count = 60 rows (59 answered cases; g119 counted twice)
identifier_mentions_denominator = 121
```

The 60th row is a **complete duplicate execution of `g119`**: both rows carry a full result/metrics payload with no exception, status `insufficient_evidence`, answers of identical length, recorded 37 seconds apart (2026-09-13T00:23:15Z and 00:23:52Z). This is recovery residue from Attempt 1's documented external process terminations — the store is append-only, so the re-executed case appended a second complete row; the later row is the final record. The historical gate-matrix aggregation summed over stored rows, so its denominator (121) includes the duplicate row's mentions; the rescore aggregates the same way, which is why 121 reproduces exactly. Counting unique cases only would give a different (non-historical) denominator; the duplicate is disclosed rather than silently collapsed.

### Attempt 3 — the 59↔58 discrepancy resolved

```text
raw_rows_in_store = 59
unique_case_count = 59
duplicate_case_ids = {}
exception_case_ids = ["g013"]
exception_row_count = 1
completed_case_count = 58
identifier_applicable_case_count = 59 rows (58 completed + the g013 exception row)
identifier_mentions_denominator = 177
```

The store holds 59 unique-case rows, of which `g013` is the preserved Vertex-429 provider-exception row (no result payload, zero claims, zero mentions). 58 cases are completed/scored; the g013 row contributes nothing to the identifier denominator, so the rescored denominator (177) equals the historical one while the historical formal cohort state (58/59, INCOMPLETE) is preserved and no case is manufactured.

### Attempts 2, 4, 5

```text
raw_rows_in_store = 59; unique = 59; duplicates = {}; exceptions = []; completed = 59
```

## 6. R1 offline rescore (zero model calls)

| Attempt | Gold | provenance (rows/unique/dup/exceptions) | old count/rate | R1 count/rate | cleared | introduced |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | v2.6 | 60/59/g119×2/— | 0/121 (0.0) | 0/121 (0.0) | — | — |
| 2 | v2.6 | 59/59/—/— | 0/155 (0.0) | 0/155 (0.0) | — | — |
| 3 | v2.9 | 59/59/—/g013 | 0/177 (0.0) | 0/177 (0.0) | — | — |
| 4 | v2.10 | 59/59/—/— | 2/173 (0.011561) | 0/173 (0.0) | g060 ×2 | — |
| 5 | v2.10 | 59/59/—/— | 6/130 (0.046154) | 0/130 (0.0) | g060 ×2, g113 ×4 | — |

All five Gold identities re-verified against their run manifests (`gold_identity_matches_manifest = true`); all five denominators reproduce the historical matrices exactly; zero newly introduced hallucination events, so no false-negative/regression investigation is required (protocol §19). The Attempt-5 expected result 6/130 → 0/130 is re-verified mechanically.

## 7. Verdicts, counterfactuals, and protected state

- All identifier-gate counterfactual statuses remain `COUNTERFACTUAL / NON-AUTHORITATIVE`; Attempt 5's counterfactual PASS does not change its historical `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`.
- `MATERIAL_PRODUCT_CHANGE = false`; `EVALUATOR_CONTRACT_CHANGE = true`; no candidate frozen; no Attempt 6 preregistered or executed.
- `ATTEMPT_6_READINESS = NOT_READY` (blockers unchanged: g039 Gold reconciliation; critical-final-evidence construct reconciliation/redesign; two confirmed product defects; focused T0/T1/T2 development evidence; no materially new product candidate).
- The post-A5 causal-attribution erratum is preserved unchanged.
- `PANDA scientific/evaluation calls = 0`; `PANDA scientific/evaluation tokens = 0`.
- `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`; `holdout access = 0`; `protected-content leakage = 0`; `F6-B execution = 0`.

## 8. Known unrelated test debt

The two known `test_m6_evaluation.py` fixture-debt failures and the pre-existing stale v2.6-default-Gold assertion reproduce identically and are untouched by R1; recorded as pre-existing/non-blocking.

## 9. Next task recommendation

```text
F6-A EVALUATION-CONTRACT RECONCILIATION /
CRITICAL-EVIDENCE EQUIVALENCE + g039 GOLD CORRECTION + HARD-SAFETY RECLASSIFICATION
```

`NEXT_TASK_EXECUTION_AUTHORIZED = false`
