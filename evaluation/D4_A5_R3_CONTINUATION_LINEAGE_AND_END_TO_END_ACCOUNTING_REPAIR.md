# D4-A5-R3 — Continuation Lineage and End-to-End Accounting Repair

Status: `COMPLETE / PASS / CONTINUATION_LINEAGE_AND_END_TO_END_ACCOUNTING_REPAIRED`
Date: 2026-09-05
Parent commit: `a53ca0ace5280c278e32e350f5a5051b810fa6f4` (`D4-A5-R2 repair continuation freeze and accounting contract`)
R3 commit: `D4-A5-R3 repair continuation lineage and end-to-end accounting`

R3 is a strictly **pre-exposure continuation-contract repair**. It performs zero
provider/model/retrieval execution, zero plan acquisition, zero evaluator
execution, and zero production changes. R1 applicability/provenance semantics
are unchanged; R2's committed continuation-manifest/bootstrap design is retained
and forward-repaired for the R3 freeze boundary.

---

## 1. Why R3 exists (independent audit findings)

R2 successfully repaired the continuation bootstrap boundary, but the post-plan
continuation lineage and end-to-end accounting contract remained incomplete:

- **Defect A — Phase P writes R2 lineage, Phase R reads stale R1 lineage.**
  Phase P wrote `exposure["r2_freeze_head"]` while Phase R read
  `exposure.get("r1_freeze_head")` and passed that stale field to the plan-freeze
  gate. A clean R2/R3 freeze → Phase P → 7 plans → plan freeze → Phase R flow
  would hard-fail on a missing `r1_freeze_head`.
- **Defect B — stale R1 provenance downstream.** Raw-retrieval artifacts and
  evaluator/result provenance still carried `r1_freeze_head` as if it were the
  current continuation implementation freeze.
- **Defect C — accounting wired only to Phase P.** The two-layer accounting
  helper updated Analyzer acquisitions but no retrieval accounting.
- **Defect D — provider-failure unknown accounting incomplete.** Aggregate
  accounting could silently add numeric zero for unknown provider attempts, and
  the logical-call semantics of failed acquisitions were unset.

All four are confirmed in the pre-repair code and closed by R3 without touching
any R1/R2 historical artifact.

## 2. One unambiguous lineage vocabulary

```text
historical_a5_starting_head            cb0f8c3…
historical_a5_executor_freeze_head     8579cdc…
historical_a5_stop_head                dc679f8…
historical_r1_head                     93ad95d…
historical_r2_head                     a53ca0a…
continuation_implementation_freeze_head  the R3 freeze commit
continuation_plan_freeze_head            direct child of the R3 freeze
continuation_raw_freeze_head             direct child of the plan-freeze commit
```

Historical R1/R2 heads are historical facts recorded separately; they never
drive current continuation gates and are never collapsed into the current
implementation-freeze field. The committed continuation manifest now carries
this vocabulary in a `continuation_lineage` block (plus `r2_parent_boundary` in
its repair lineage), and the start preflight verifies every field against the
runner contract.

## 3. Repaired handoff (Phase P → plan freeze → Phase R)

- **Phase P** freezes `continuation_implementation_freeze_head` (the R3 HEAD)
  from the shared preflight receipt; no misleading current `r1_freeze_head` (or
  `r2_freeze_head`) is written (tested by `test_r3_07`).
- **Plan-freeze gate** (`verify_continuation_plan_freeze_gate`): the plan-freeze
  commit (`D4-A5 continuation freeze prospective shared plans`) must be a direct
  child of the R3 implementation freeze; the committed raw-plan artifact must
  contain exactly the frozen 7-case cohort of completed provenance-gated plans;
  the R3→plan-freeze diff is limited to the frozen plan-acquisition artifacts
  (continuation manifest + raw plans); protected production/historical/R1/R2
  paths must be unchanged.
- **Phase R** consumes `continuation_implementation_freeze_head` and the
  plan-freeze head via the new read-only `verify_phase_r_preflight`; it requires
  no stale `r1_freeze_head` (source-scan tested by `test_r3_08`).
- **Raw-freeze gate**: the raw-freeze commit must be a direct child of the
  plan-freeze commit; evaluator/result provenance records the full seven-field
  lineage (`test_r3_13`).

The required synthetic lifecycle handoff test (`test_r3_09_10`) exercises the
real gates in a temporary Git repository — clean R3 freeze → completed Phase-P
state → plan-freeze commit → gate → Phase-R preflight succeeds — with zero
provider or retrieval calls, and specifically proves Phase R uses
`continuation_implementation_freeze_head`. `test_r3_11`/`test_r3_12` prove a
wrong plan-freeze parent and a stale R1-as-current-freeze input both fail.

## 4. End-to-end accounting

`apply_continuation_accounting` is now the single deterministic accounting path
for the whole continuation attempt. Phase R feeds each completed cell's ACTUAL
recorded stats (embedding calls, reranker calls, retrieval provider attempts,
known token usage) into the same helper — the expected 14/14 protocol outcome
must be derived from real receipts, never assumed. Cumulative values are always
recomputed as historical + continuation:

- 7 successful Analyzer acquisitions → continuation 7 / cumulative 13;
- 14 retrieval cells → continuation and cumulative embedding 14, reranker 14
  (historical embedding/reranker are 0);
- tokens and provider attempts accumulate from actual receipts only.

Unknown accounting stays explicit at the manifest layer:
`unknown_token_usage_events` and `unknown_provider_attempt_events` counters
(cumulative unknown = historical unknowns + continuation unknowns). Unknown
attempts never silently contribute numeric zero as if known. Frozen
logical-call semantics: a failed-but-invoked Analyzer acquisition counts
`analyzer logical calls += 1`; provider attempts remain a separate known-or-
unknown dimension; `max_retries = 0` / `max_provider_attempts_per_case = 1`
unchanged. Double counting is prevented by terminal slot/cell status
transitions; reload/recompute tests (`test_r3_18_19`, `test_r2_14`) prove
stability and that cumulative is a deterministic function of the two layers.

## 5. What did not change

The 3 selected rules; the D4-A4 masks (including
`model_factory_theory: pflueger_2017: [51, 57, 65]`); the exact case order; 7
plans / 14 cells; CURRENT_COMPAT / BATCH2_RETIREMENT arms; Batch 1 invariant;
three-state applicability; six-state dispositions; seven-level batch verdict;
six primary metrics and frozen tolerances; MRR diagnostic-only; safety gates;
Batch 2 production false. No n014/pflueger/case/rule/locator/expected-answer
special case was added (`test_r3_31`).

## 6. Boundary and verification

Zero exposure: no Analyzer provider calls, no acquisitions, no embedding,
no reranker, no retrieval cells, no QA/verifier/judge, no evaluator execution,
no scientific verdict, no DB/Qdrant writes, no protected access; `execute-phase-p`,
`execute-phase-r`, and `evaluate` were not run against the real scientific
environment. Verification: 113 focused tests passing (9 added for R3, existing
R2 tests retargeted to the R3 contract), compile/static checks, JSON parse,
`git diff --check`, exact R2→R3 changed-file audit, protected-path Git-object
identity checks, and the real read-only continuation-start preflight executed
after the commit. No hash inventories; no provider smoke tests.

## 7. Lifecycle state

```text
D4-A5 FIRST ATTEMPT   HISTORICAL / INVALID / PRE-OUTCOME STOP / PRESERVED
D4-A5-R1              HISTORICAL REPAIR RECORD PRESERVED
                      APPLICABILITY / PROVENANCE LOGIC RETAINED
D4-A5-R2              HISTORICAL REPAIR RECORD PRESERVED
                      CONTINUATION BOOTSTRAP REPAIR RETAINED
D4-A5-R3              COMPLETE / PASS / CONTINUATION_LINEAGE_AND_END_TO_END_ACCOUNTING_REPAIRED
D4-A5                 BLOCKED / READY_FOR_SEPARATELY_AUTHORIZED_CONTINUATION
BATCH1                ACTIVE
BATCH2                SELECTED / FROZEN / NOT YET SCIENTIFICALLY VALIDATED
BATCH2 PRODUCTION     false
D4-A6                 NOT_STARTED
```

D4-A5 is not marked scientifically PASS. The continuation does not start
automatically; it still requires separate authorization.
