# D4-A9-R2 — Post-Outcome Closeout Verification Recovery

Technical live audit: **PASS**, zero errors. Scientific verdict: **Level 6 / PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD**.

Closeout acceptance requires the post-commit verifier to pass; that command checks the exact two-commit topology and the entire committed machine result against a fresh deterministic audit. No scientific verdict was predetermined as a technical PASS condition.

## Incident interpretation and lineage

Starting commit: `1f52957099f3bfd41b9624d863dee0fdddb59ee4`, message `D4-A9-R2-Fail`, direct parent `07b8cc921b4e36dc2acf2ae4ba0b27f4b3edf115`. Its contents are the administrative failure record of the unaccepted D4-A9-R1 attempt. The misleading message is preserved; it is not a scientific R2 execution or scientific authority. The current user separately authorized this forward D4-A9-R2 recovery.

Starting local origin/main and the remote refs/heads/main both matched the incident commit; starting worktree was clean. No amend, rebase, reset, force push, or scientific rerun occurred.

Verifier-freeze commit: `a0b612f0abc3f5ee8cb6a8d2633c5504cfc485c0`.
Exact message: `D4-A9-R2 freeze recovered post-outcome closeout verifier`.
Direct parent: `1f52957099f3bfd41b9624d863dee0fdddb59ee4`.
After commit, exact message/parent/six-path diff and clean worktree were checked before any real outcome read.

The closeout commit containing this report has exact message `D4-A9-R2 close recovered post-outcome verification` and direct parent `a0b612f0abc3f5ee8cb6a8d2633c5504cfc485c0`. Its own SHA and remote main receipt are reported by the host after commit/verify/push; no self-referential SHA is embedded in this report.

## Pre-freeze isolation and first accepted live invocation

61 focused synthetic tests passed in 0.87 seconds. Contract-audit and static test-file audit passed, reporting outcome_files_read=0. All six outcomes were produced from synthetic Gold and in-memory plans/results. No old A9/R1 suite ran. Initial dependency collection failure was resolved by installing test dependencies into a temporary directory outside the repository; it did not read scientific evidence.

The first statement of each real entrypoint invokes `require_verifier_freeze_checkpoint`. The guard checks direct-parent incident identity, exact message, ancestry, exact six-path checkpoint, and immutable verifier/test/contract blobs before scientific readers. The real-root rejection test ran under builtin/io open tripwires for all four outcome-bearing A9 paths and a tripwire blocking all Git content readers. Synthetic evaluation works in tmp_path without repository data. Mocked Git tests reject wrong parents/messages/paths/semantics. Static AST inspection rejects unguarded/aliased real entrypoints and scientific content loading in tests.

Only after checkpoint identity was confirmed, the host first invoked:

```text
python evaluation/scripts/d4_a9_r2_post_outcome_closeout_verification_recovery.py --project-root . --mode live-audit
```

The machine result records the checkpoint and `first_live_audit_after_freeze=true`. It returned PASS, Level 6, and no errors. No verifier, contract, or test changes or test reruns occurred after that invocation. Only this report, current docs and the generated result changed after freeze.

## Exact final path boundary

1. docs/EVALUATION_STATUS.md
2. docs/GENERALIZATION_ROADMAP.md
3. evaluation/D4_A9_R2_POST_OUTCOME_CLOSEOUT_VERIFICATION_RECOVERY.md
4. evaluation/d4_a9_r2_post_outcome_closeout_verification_contract.json
5. evaluation/d4_a9_r2_result.json
6. evaluation/scripts/d4_a9_r2_post_outcome_closeout_verification_recovery.py
7. tests/unit/test_d4_a9_r2_post_outcome_closeout_verification_recovery.py

## Git seals

All eight historical A9 artifacts remain equal to A9 authority, all four R1 incident artifacts remain equal to the incident commit, and all five A8-R2 artifacts remain equal to their actual Git objects at `06f853d9613c5170676d77261cc2d7b82d50958c`. The incorrect R1 constants were not reused. The complete prior incident text in both docs is retained unchanged below new current status.

Raw plans: checkpoint `443d832258bf99a8f049ea524995b05922cdae80`, blob `99891321c0d3ba3e0f54158441f2d739eca2db6f`.
Raw paired results: checkpoint `2419d4f1818277656c1b3be93e423134e877657f`, blob `4f44ac31c9fd917c1212f8d64c59974f90e4cfd6`.
Both are checked at the original checkpoint, A9 closeout, incident commit, current HEAD, and working tree through historical seals. Gold v2.6 and evaluation.py are also equal to executor-freeze authority. src and configs trees and working files remain unchanged. Actual blob receipts are in d4_a9_r2_result.json.

## Cohort, plans and accounting

Formal order: g031, g032, g033, g047. Target: model_factory_theory / model/PndLmdModelFactory.cxx. HOLD masks are unchanged.

| Case | Frozen matched rules | Analyzer attempts | Analyzer tokens |
|---|---|---:|---:|
| g031 | model_factory_theory, model_factory_acceptance_methods | 1 | 1788 |
| g032 | [] | 1 | 1747 |
| g033 | [] | 1 | 1438 |
| g047 | dpm_model_theory | 1 | 2226 |

Analyzer total: 4 logical calls, 4 attempts, 7,199 tokens; all four successful plans persisted. Retrieval: 8 embedding calls, 8 reranker calls, 16 attempts, 131,070 tokens. Historical scientific total: 20 logical calls, 20 attempts, 138,269 tokens. QA/Verifier/Judge/Scientific-evaluator provider calls and retries are zero, cross-checked with the committed historical A9 result. Counts are reconstructed from per-plan/per-slot records and cross-checked with raw summaries, not inferred from slot count alone. Separate failure counters are absent in the raw schema; successful persisted plans and attempts equal logical calls bound observed failures/retries. Zero downstream Analyzer execution is also supported by the frozen executor's explicit rejection hook.

Exactly four plans, fourteen required persisted fields, canonical serialization/signatures, case roles, shared canonical identities and all actual-plan/arm-projection equalities passed. All controls have zero masks, zero removed origins, zero effective removals and equal current/treatment projections. This does not require equal retrieval outputs.

Exact schedule:

1. g031 / A7_CURRENT
2. g031 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT
3. g032 / A7_CURRENT
4. g032 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT
5. g033 / A7_CURRENT
6. g033 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT
7. g047 / A7_CURRENT
8. g047 / COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT

All indices, IDs, arms and COMPLETED states passed, with no duplicate/missing/ninth slot.

Persistence proof uses Git object `8e332acb8a1d4658a860ad5e251c9223319bfa42:evaluation/scripts/d4_a9_model_factory_covered_symbol_retirement_validation.py`: first raw write at line 919 precedes formal gate at line 927. All four persisted_at <= gated_at receipts and RETRIEVAL_ELIGIBLE states pass. This proves program order plus frozen receipt order, not disk reload or independent storage durability.

## Critical, grounding and version results

| Case | Critical group current -> treatment | Final evidence position current -> treatment | Lost critical groups |
|---|---|---|---:|
| g031 | 1.0 -> 1.0 | 1 -> 1 | 0 |
| g032 | 1.0 -> 1.0 | 1 -> 1 | 0 |
| g033 | 1.0 -> 1.0 | 2 -> 1 | 0 |
| g047 | 1.0 -> 1.0 | 1 -> 1 | 0 |

Both g031 arms reproduce g031.e1 by direct Gold selector match to `object.432011cd3810787037f8b091`, final evidence position 1. Selected model_factory_theory origin is removed from the ModelFactory symbol contribution; model_factory_acceptance_methods survives. The literal remains, so effectively_removed=false is correct and does not invalidate treatment.

Critical semantics: existing `_matched_evidence_groups` against critical Gold evidence groups. Grounding semantics: canonical object lookup resolution; object_id/source_id/source_version_id identity; direct Gold forbidden selectors; existing deterministic source_type/required_source_coverage predicates. Both arms independently compute unresolved, forbidden, canonical-identity and missing-source-type violations before treatment-only subtraction. No new overlap/score threshold was introduced. Version semantics: membership of every frozen final evidence source_version_id in Gold allowed_source_versions; missing IDs are invalid, not skipped.

All eight slots have 12 resolved, valid-version items each (96 total). Unresolved, forbidden, canonical identity mismatches, missing required source types, grounding violations and treatment-only regressions are all zero. Version violations=0, missing-invalid=0, not-governed=0.

## Diagnostic variance and precedence

All four pairs have different evidence sets/order. Non-critical additions/removals: g031 0/0, g032 2/2, g033 1/1, g047 1/1. In g031, differing IDs still match critical selectors; the critical group remains satisfied. These diagnostics impose no identity or ranking gate.

Frozen precedence excluded Level 1 protocol failure, Level 2 baseline failure, Level 3 dependency loss, Level 4 safety regression and Level 5 incomplete applicability, producing actual Level 6. Technical PASS is separate from scientific PARTIAL.

ModelFactory: RETIREMENT_VALIDATED_COMPONENT.
Both DPM symbols: HOLD_DIRECT_TREATMENT_COVERAGE_GAP.
Pflueger_2017 [51,57,65]: HOLD_OUTSIDE_TREATMENT_SCOPE.

Historical A9 stale booleans are superseded as HISTORICAL_RECEIPT_STALE_NON_AUTHORITATIVE. Git-derived receipts establish frozen plans, frozen paired results, eight completed slots and recorded deterministic evaluation. The old manifest/report is not edited.

## Costs, acceptance and limits

R2 scientific Analyzer/Embedding/Reranker/Retrieval/QA/Verifier-provider/Judge/Scientific-evaluator calls, retries, tokens and DB/Qdrant writes: zero. No AGY/staffer was invoked in R2; historical R1 AGY costs remain unavailable, not zero. No full suite, T3, T5, live scientific rerun or reindex occurred.

The local canonical catalog is selected using existing latest-ingestion-report semantics; its path is recorded in the machine result. Acceptance is bounded to frozen retrieval evidence and deterministic metadata, not generated answers or a new model grounding assessment. Final committed verify re-derives every deterministic result field and seal; the host will push normally only after it passes and remote main is confirmed unchanged.

FULL_BATCH2_PRODUCTION_ACTIVATION=false. PRODUCTION_ACTIVATION_AUTHORIZED=false. D4-A10=NOT_STARTED/NOT_AUTHORIZED. STOP.
