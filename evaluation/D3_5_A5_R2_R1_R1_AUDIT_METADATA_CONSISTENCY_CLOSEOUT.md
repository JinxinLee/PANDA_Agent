# D3.5-A5-R2-R1-R1 — Audit Metadata Consistency Closeout

## 1. Executive closeout

**`R2_R1_R1_DECISION = AUDIT_METADATA_CONSISTENCY_CLOSED`.** Two residual parent-artifact wording inconsistencies were repaired, and the provenance of the pre-amend implementation-freeze identity `c4aebd84eb91a7a316c9f84e94eaeffb5d1e83a7` was clarified as a **local pre-amend Git object that is not remotely reachable**. All R2 scientific fields are verified unchanged. No scorer/evaluator/fixture/preregistration/runtime change occurred; no real-case scorer run; no model calls; no DB/Qdrant writes.

## 2. Parent R2/R2-R1 state

- `D3.5-A5-R2 = COMPLETE / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT` (result commit `2bddbbc…`; scientific verdict, six-case records, selected IDs, metrics, applicability classes — all immutable and re-verified unchanged).
- `D3.5-A5-R2-R1 = COMPLETE / OUTCOME_EXPOSURE_AND_EVALUATOR_WIRING_AUDIT_REPAIRED` (commit `716389b…`); `R2_EXECUTION_AUDIT_STATUS = PASS_WITH_AUDIT_REPAIR`; `R2_RERUN_REQUIRED = false`.

## 3. Residual metadata inconsistency

Independent audit identified two wording inconsistencies in the parent R2 result artifact:

1. The hashlib import repair was described as fixed "before any outcome exposure" — conflicting with the corrected chronology (treatment-execution exposure began during Invocation A, **before** the hashlib fix).
2. The `a2_matched_ids` failure was attributed to "the first replay invocation" — while R2-R1 established Invocation A = hashlib failure and Invocation B = a2_matched failure.

## 4. Hashlib timing correction

Corrected semantics (the stale phrase now appears only inside an explicitly marked `previous_incorrect_wording` field):

```
repair = hashlib_import
timing = POST_TREATMENT_EXECUTION_EXPOSURE / PRE_EVALUATOR_EXECUTION / PRE_INVOCATION_B
semantic_effect = NONE
```

Factual sequence: Invocation A (at the original pre-amend freeze commit `c4aebd8`) executed `select_v2` twice on g036 with the deterministic comparison completing, then crashed at determinism-receipt construction (`NameError: hashlib`) — before the evaluator started. The import fix was amended into the freeze commit `f498714`.

## 5. a2_matched invocation correction

Corrected attribution: **Invocation B** (the second failed real-case replay invocation, at the amended freeze `f498714`) crashed inside `evaluate_complete_universe` at the newly-visible diagnostic (`NameError: a2_matched_ids` not yet wired) after the g036 selector matching had completed in memory. Preserved: Invocation A = hashlib NameError after `select_v2` ×2 on g036; Invocation B = a2_matched NameError after `select_v2` ×2 on g036; Invocation C = successful 6/6 replay.

## 6. c4aebd8 provenance clarification

```
ORIGINAL_PRE_AMEND_IMPLEMENTATION_IDENTITY = c4aebd84eb91a7a316c9f84e94eaeffb5d1e83a7
IDENTITY_ROLE = LOCAL_PRE_AMEND_GIT_OBJECT_OBSERVED_DURING_R2
REMOTE_REPOSITORY_REACHABLE = false
```

Verified by inspection: `git branch -a --contains c4aebd8` lists no branch (local or remote); `git merge-base --is-ancestor c4aebd8 origin/main` exits 1; the object remains locally observable via the reflog. The `pre_amend_identity_provenance` clarification was added to the R2-R1 machine artifact (core chronology and decision untouched).

## 7. Remote reproducibility caveat

`REMOTE_REPLAYABILITY_OF_PRE_AMEND_GIT_OBJECT = NOT_AVAILABLE` — the pre-amend identity was available during the original local audit, but it is not part of the currently reachable remote Git history; a fresh clone cannot `git show c4aebd8`. This does **not** invalidate the R2 scientific result or the R2-R1 result-neutrality conclusion: `AUDIT_EVIDENCE_AT_REPAIR_TIME = SUFFICIENT` — the amended implementation freeze `f498714`, the final result implementation `2bddbbc`, the R2-R1 audit artifact with its recorded extracted-region identity checks, and the post-freeze evaluator-wiring diff are all preserved and reachable. No new SHA bookkeeping was introduced.

## 8. Scientific-field immutability

Verified unchanged against the parent result commit `2bddbbc`: `six_case_records`, selected object IDs, selected rank keys, candidate receipts, fan-out metrics, graph-displacement metrics, complete-universe evaluator results/applicability classes, determinism receipts, `scientific_verdict`, governance/scope invariants. Authorized metadata changes were limited to the two infrastructure-repair wording entries (with `timing` blocks added) and the appended closeout repair-history entry. Stale phrases survive only inside explicitly marked `previous_incorrect_wording` fields.

## 9. A6 readiness

```
A6_SCIENTIFIC_PREREGISTRATION_READINESS = YES
A6_AUDIT_PREREGISTRATION_READINESS      = YES
A6_EXECUTION_STARTED                    = false
```

The A6 origin-concentration diagnostic requirements remain frozen (`selected/reserved bridge origin counts`, `per-origin counts`, `ordinary_rerank_candidates_displaced`, `reserved bridge candidate/origin IDs`); no numeric concentration threshold was added and selectivity was not modified because of g020. Reranker execution remains prohibited until the A6 preregistration itself is frozen.

## 10. Lifecycle

```
D3.5-A5         = COMPLETE / SELECTIVITY_FANOUT_REDUCED_WITH_RELEVANCE_LOSS
D3.5-A5-R1      = COMPLETE / SELECTIVITY_RELEVANCE_RETENTION_REPAIR_DESIGN_FROZEN
D3.5-A5-R1-R1   = COMPLETE / RELEVANCE_FORMULA_AND_EXACT_MATCH_CONTRACT_REPAIRED
D3.5-A5-R2      = COMPLETE / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT
D3.5-A5-R2-R1   = COMPLETE / OUTCOME_EXPOSURE_AND_EVALUATOR_WIRING_AUDIT_REPAIRED
D3.5-A5-R2-R1-R1= COMPLETE / AUDIT_METADATA_CONSISTENCY_CLOSED
D3.5            = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN
D3.5-A6         = NOT_STARTED / READY_FOR_PREREGISTRATION
D4              = NOT_STARTED / BLOCKED
```

## 11. Exact next task

> **D3.5-A6 — Bounded Rerank-Admission Prototype & Paired Replay Validation** — the next task must begin with **design/preregistration**, not execution. A6 must freeze before any reranker call: the K=2/K=3 arms, exact baseline/treatment construction, decision semantics between K=2 and K=3, reranker repetition count, symmetric repeated execution, variance accounting, candidate displacement semantics, control material-regression interpretation, and the origin-concentration diagnostics.
