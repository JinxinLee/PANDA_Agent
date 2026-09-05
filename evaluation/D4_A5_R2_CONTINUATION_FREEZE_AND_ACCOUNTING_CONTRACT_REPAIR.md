# D4-A5-R2 — Continuation Freeze and Accounting Contract Repair

Status: `COMPLETE / PASS / CONTINUATION_FREEZE_AND_ACCOUNTING_CONTRACT_REPAIRED`
Date: 2026-09-05
Parent commit: `93ad95d7f8808bc4e7ccdbb21a24457c0df30564` (`D4-A5-R1 repair retirement applicability contract`)
R2 commit: `D4-A5-R2 repair continuation freeze and accounting contract`

R2 is a strictly **pre-exposure contract/infrastructure repair**. It performs
zero provider calls, zero acquisitions, zero retrieval, zero evaluator
execution, and zero production changes. The scientific question, Batch-2 rule
selection, frozen masks, seven-case cohort, metrics, tolerances, applicability
semantics, and per-rule/batch verdict semantics are unchanged.

---

## 1. The bootstrap defect (independent audit finding)

The committed R1 continuation path was internally non-executable:

```text
prepare-continuation-manifest  -> creates an UNTRACKED continuation manifest
execute-phase-p                -> verify_r1_freeze_gate()
                                  -> requires the exact R1 HEAD
                                  -> requires a completely clean worktree
```

Leaving the manifest uncommitted made the worktree dirty (gate rejects);
committing it changed HEAD away from the exact R1 commit (gate rejects). The
focused Phase-P tests did not expose this because they monkeypatched the real
freeze gate.

## 2. The repair: continuation freeze inside the R2 commit

The continuation execution manifest
(`evaluation/d4_a5_continuation_execution_manifest.json`) is now a **committed
pre-exposure artifact of the R2 freeze commit itself**. The
`prepare-continuation-manifest` CLI mode is removed; no future scientific
execution command creates its own authority outside Git.

The implementation freeze uses a deterministic containing-commit contract: at
continuation start the gate mechanically establishes that (1) the manifest is
committed at HEAD and absent at the parent (introduced by the freeze commit),
(2) HEAD's message is exactly `D4-A5-R2 repair continuation freeze and
accounting contract`, (3) HEAD's parent is exactly `93ad95d…` (the R1 HEAD),
(4) the worktree/index are clean — so the executing runner is the R2-frozen
implementation blob, and (5) no descendant or intervening commit is accepted.
No adversarial cryptographic sealing, no SHA inventories.

## 3. Manifest authority repaired

The committed manifest no longer inherits contradictory first-attempt freeze
metadata. It now freezes:

- **Lifecycle lineage**: historical A5 starting boundary `cb0f8c3…`, executor
  freeze `8579cdc…`, stop `dc679f8…`, R1 parent boundary `93ad95d…`, R2
  continuation implementation freeze = the commit containing this manifest.
- **Repaired contract authority**: the R1 applicability repair preregistration;
  the frozen D4-A4 scientific selection/masks are referenced read-only and
  never replaced.
- **Exact continuation artifact paths** (manifest, raw plans, raw results,
  evaluator results, result).
- **Exact continuation freeze messages**: `D4-A5 continuation freeze
  prospective shared plans` / `D4-A5 continuation freeze paired raw retirement
  results` / `D4-A5 continuation close controlled retirement validation`. The
  old first-attempt messages (`D4-A5 freeze controlled retirement executor`, …)
  remain only as clearly labeled historical references and are not current
  gates.
- **Frozen reusability decision**: `REUSABLE_FROZEN_SCIENTIFIC_PLAN` = none;
  `HISTORICAL_ATTEMPT_NOT_REUSABLE` = g052, g055, n003, n004, g007, n014;
  `NEVER_EXECUTED` = g060; a future separately authorized continuation may
  reacquire exactly all seven plans; a historical `plan_signature` alone
  remains insufficient. R2 itself performs zero reacquisition.

## 4. Attempt-local and cumulative accounting

The R1 manifest builder initialized continuation/cumulative accounting, but
Phase P never maintained it. R2 adds one small deterministic helper
(`apply_continuation_accounting`) used by the execution code: each event delta
is applied to the continuation-attempt layer and the cumulative layer is
mechanically recomputed as **historical + continuation**. Historical unknown
n014 token usage stays explicitly unknown (tracked as a separate unknown
component, never collapsed into zero). Synthetic tests prove: one acquisition →
continuation 1 / cumulative 7; seven acquisitions → continuation 7 /
cumulative 13; tokens follow the same rule against the 10,303 recorded
historical tokens; reload/recompute does not double count.

## 5. Provider-failure persistence

The frozen retry policy remains `max_retries = 0`,
`max_provider_attempts_per_case = 1`. The repaired Phase P flow: (1) mark the
slot STARTED and persist; (2) snapshot provider stats; (3) initiate exactly one
`analyze()` call; (4) on return, persist accounting and all plan/ledger/
applicability/projection evidence, then evaluate the applicability gate; (5) on
a provider raise, do **not** retry — persist a durable provider-failure receipt,
preserve every mechanically available accounting value from the stats delta,
record unavailable values explicitly as unknown (never fabricated zero), mark
the slot with the explicit terminal state `PROVIDER_FAILED` (not an ambiguous
STARTED), and STOP the continuation. No generalized recovery framework; no
auto-restart. Verified synthetically, including the stats-unavailable case
(where attempts/tokens become `unknown` and the continuation-attempt layer
records the unknown-token event).

## 6. Real continuation-start verification

A shared read-only preflight (`verify_continuation_start`, CLI mode
`verify-continuation-start`) establishes all continuation-start conditions with
zero provider calls, and the real `execute_phase_p()` uses the same preflight.
The focused bootstrap tests do **not** monkeypatch the gate: they run the real
gate logic inside a temporary Git repository fixture (only the module-level
expected SHAs are remapped to local fixture SHAs), covering clean-HEAD pass,
uncommitted-drift fail, descendant-HEAD fail, wrong-parent fail, wrong-message
fail, missing-manifest fail, and protected-drift fail. A real-repo test
additionally proves the committed manifest was introduced by the R2 freeze
commit and matches the runner constants. After the R2 commit, the actual
read-only continuation-start verification is executed against the real
repository HEAD (see §8 of the result record).

## 7. What did not change

The 3 selected rules; the original D4-A4 masks (including
`model_factory_theory: pflueger_2017: [51, 57, 65]`); the exact seven-case
order; 7 prospective plans / 14 paired cells in the future continuation; the
CURRENT_COMPAT / BATCH2_RETIREMENT arms; active direct and control cases; the
six primary metrics and thresholds; MRR diagnostic-only; safety gates; the
three-state applicability semantics; the six-state disposition space; the
seven-level batch verdict; Batch 1 invariant; Batch 2 production false. No
n014/pflueger/case-ID/rule-ID/locator/benchmark/expected-outcome special
handling was added.

## 8. Historical records preserved

The first-attempt artifacts (`d4_a5_execution_manifest.json`, `d4_a5_result.json`,
A4 preregistration/selection) and all three R1 artifacts are untouched. R2 is a
forward-only repair prompted by a later independent audit finding; the R2
records explicitly state: *R1 applicability/provenance logic repair accepted,
but the continuation bootstrap/accounting contract was incomplete.* Historical
R1 timestamps are not rewritten; all new R2 timestamps are timezone-aware UTC.

## 9. Verification and boundary

105 focused tests passing (19 added for R2); compile/static checks; JSON parse
validation; Git diff inspection; `git diff --check`; production/historical path
identity checks; confirmation that the continuation raw plans/results/
evaluator/result artifacts are absent. Zero provider calls, zero acquisitions,
zero embedding/reranker, zero retrieval, zero evaluator execution, zero
scientific outcome exposure, zero DB/Qdrant writes, zero protected access. No
full suite run; no SHA256 inventories; no provider smoke tests.

## 10. Lifecycle state

```text
D4-A5 FIRST ATTEMPT   HISTORICAL / INVALID / PRE-OUTCOME STOP / PRESERVED
D4-A5-R1              HISTORICAL REPAIR RECORD PRESERVED
                      APPLICABILITY / PROVENANCE LOGIC REPAIR RETAINED
D4-A5-R2              COMPLETE / PASS / CONTINUATION_FREEZE_AND_ACCOUNTING_CONTRACT_REPAIRED
D4-A5                 BLOCKED / READY_FOR_SEPARATELY_AUTHORIZED_CONTINUATION
BATCH1                ACTIVE
BATCH2                SELECTED / FROZEN / NOT YET SCIENTIFICALLY VALIDATED
BATCH2 PRODUCTION     false
D4-A6                 NOT_STARTED
```

D4-A5 itself is not marked PASS. Batch 2 is not activated. D4-A6 is not
started. A D4-A5 continuation still requires separate authorization.
