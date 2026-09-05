# D4-A5-R5 — Raw-Freeze Evaluator Integrity Seal

Status: `COMPLETE / PASS / RAW_FREEZE_EVALUATOR_INTEGRITY_SEALED`
Date: 2026-09-05
Parent commit: `447d03e3cb9d3c1109d6f6070115f3ea4618bb7e` (`D4-A5-R3 repair continuation lineage and end-to-end accounting`)
R5 commit: `D4-A5-R5 seal raw-freeze evaluator integrity`

R5 is a strictly **pre-exposure continuation-integrity repair**. It performs
zero provider/model/retrieval execution, zero plan acquisition, zero evaluator
execution, and zero production changes. R1 applicability/provenance semantics,
R2 bootstrap design, and R3 lineage/accounting are unchanged.

---

## 1. Why R5 exists (independent audit finding)

R3 successfully repaired continuation lineage and end-to-end accounting, but
independent audit subsequently found that the continuation raw-freeze gate did
not fully seal the evaluator implementation against post-retrieval code drift:

```text
plan-freeze
    ↓ Phase R retrieves 14 cells
raw-freeze commit
    ↓ evaluator
```

The pre-repair raw-freeze gate verified the raw-freeze commit message, its
direct plan-freeze parent, committed raw plans/results, raw-plan immutability,
and a fixed protected-path list — but that list excluded the runner and
focused-test paths, and no plan-freeze → raw-freeze diff allowlist existed. A
raw-freeze commit could theoretically contain continuation raw results, the
continuation manifest, AND a runner modification, and still reach evaluator
execution — a code change occurring after retrieval outcomes had already been
exposed. R3's historical PASS artifact is not rewritten; R5 is forward-only.

## 2. The R5 implementation freeze

`D4-A5-R5 seal raw-freeze evaluator integrity` (direct parent
`447d03e…`, the R3 HEAD) becomes the current continuation implementation
freeze. The committed continuation manifest is forward-updated accordingly:
`implementation_freeze_contract` now points to the R5 message with the R3 HEAD
as expected parent, and the plan-freeze contract expects a direct child of R5.
Future continuation start requires: HEAD is the R5 freeze commit, exact R5
message, direct parent = R3 HEAD, manifest committed at HEAD, clean
worktree/index (so the executing runner is the frozen R5 implementation),
production/historical paths unchanged, and no descendant commit dynamically
accepted. No SHA256 inventories; no cryptographic sealing.

## 3. Lineage update (minimal)

Only the current implementation boundary advances. The lineage vocabulary now
records `historical_r3_head = 447d03e…` alongside the historical A5/R1/R2
heads; no `historical_r4_head` is invented and no R4 lifecycle artifact is
created or referenced. Historical R1/R2/R3 heads remain provenance only and
never drive current continuation gates.

## 4. Core repair — strict raw-freeze diff allowlist

The raw-freeze commit message remains
`D4-A5 continuation freeze paired raw retirement results` with the plan-freeze
commit as its direct parent. The exact plan-freeze → raw-freeze changed-file
set must be a subset of exactly:

```text
evaluation/d4_a5_continuation_execution_manifest.json
evaluation/d4_a5_continuation_raw_paired_retirement_results.json
```

No other path is permitted. This explicitly rejects modifications to the
runner, the focused tests, the continuation raw plans, the R5 artifacts, all
historical R1/R2/R3 artifacts, and any production/config/dataset path. Because
the strict allowlist proves the same property for the retrieval window, the
gate no longer maintains a redundant broad frozen-path list — the smallest
auditable implementation. Upstream gates (continuation-start preflight and the
plan-freeze gate with its own {manifest, raw plans} allowlist) cover the
earlier windows, so production/historical integrity holds transitively for the
whole continuation.

## 5. Explicit evaluator-runner integrity checks

`evaluate_d4_a5` now calls a real read-only evaluator preflight
(`verify_continuation_evaluator_preflight`) before any deterministic evaluator
logic consumes retrieval outcomes. The preflight mechanically establishes:

- the raw-freeze gate (message, direct plan-freeze parent, committed raw
  plans/results, strict diff allowlist, raw-plan immutability);
- `runner blob at raw-freeze HEAD == runner blob at
  continuation_implementation_freeze_head`;
- `focused test blob at raw-freeze HEAD == focused test blob at
  continuation_implementation_freeze_head`;
- `continuation raw plans blob at raw-freeze HEAD == continuation raw plans
  blob at plan-freeze HEAD`;
- production/config/dataset paths unchanged across the whole retrieval window
  (implementation freeze → raw freeze);
- historical A5/R1/R2/R3 artifacts unchanged;
- manifest lineage internally consistent with the R5 contract and exposure =
  RAW_RETRIEVAL_COMPLETE;
- no evaluator/result artifact already mutated outside the expected lifecycle.

It uses normal Git object/path comparison only — no SHA256 inventory. It fails
closed before consuming any retrieval outcome. R5 itself does not execute the
evaluator.

## 6. What did not change

Applicability tri-state; selected-rule-origin provenance semantics; projection
logic; six-state per-rule dispositions; seven-level batch verdict; six primary
metrics and thresholds; MRR diagnostic-only; safety gates; Batch-1 behavior;
Batch-2 masks (including `model_factory_theory: pflueger_2017: [51, 57, 65]`);
case cohort; pair schedule; Analyzer/retrieval/unknown accounting semantics.
Selected rules remain exactly `effective_acceptance_pipeline`,
`root_macro_usage`, `model_factory_theory`. No n014, pflueger, rule-ID,
case-ID, locator, benchmark, or expected-outcome special handling. Phase P is
unchanged (reacquire all 7 frozen cases, one logical Analyzer acquisition per
case, no semantic redraw, `max_retries = 0`, persist before the
applicability/provenance gate, R3-style accounting and lineage). The stale
`--mode prepare-continuation-manifest` usage line was removed from the runner
docstring (the mode no longer exists); no broader documentation refactor.

## 7. Focused verification

131 focused tests passing (9 added for R5; existing tests retargeted to the R5
freeze boundary). The raw-freeze integrity matrix uses real Git in temporary
repositories, never monkeypatching the gate:

- `test_r5_13a` valid raw freeze (manifest + raw results only) → PASS;
- `test_r5_13b` runner mutation in the raw-freeze commit → FAIL;
- `test_r5_13c` focused-test mutation → FAIL;
- `test_r5_13d` raw-plan mutation → FAIL;
- `test_r5_13e` unrelated file → FAIL;
- `test_r5_13f` wrong raw-freeze parent → FAIL;
- `test_r5_14a` valid chain passes the real evaluator preflight;
- `test_r5_14b` runner drift fails before any retrieval outcome is consumed;
- `test_r5_14c` valid R5 → valid plan freeze → valid raw freeze → the evaluator
  passes the REAL gate and reaches the deterministic evaluation body
  (sentinel-proven), with provider construction forbidden and no scientific
  result produced.

Plus compile/static checks, JSON parse, `git diff --check`, the exact R3→R5
changed-file audit, protected historical/production Git-object identity checks,
the real read-only continuation-start verification after the commit, and
confirmation that the four future scientific artifacts remain absent. The
actual current pytest count is reported (131); historical R3 artifacts are not
rewritten to reconcile older narrative counts.

## 8. Zero exposure

Analyzer 0, plan acquisitions 0, embedding 0, reranker 0, retrieval cells 0,
QA/verifier/judge 0, evaluator execution 0, scientific verdict 0, DB/Qdrant
writes 0, protected dataset access 0. `execute-phase-p`, `execute-phase-r`,
and `evaluate` were not run against the real scientific environment; lifecycle
transition tests run in temporary Git repositories only.

## 9. Lifecycle state

```text
D4-A5 FIRST ATTEMPT   HISTORICAL / INVALID / PRE-OUTCOME STOP / PRESERVED
D4-A5-R1              HISTORICAL REPAIR RECORD PRESERVED
                      APPLICABILITY / PROVENANCE LOGIC RETAINED
D4-A5-R2              HISTORICAL REPAIR RECORD PRESERVED
                      CONTINUATION BOOTSTRAP REPAIR RETAINED
D4-A5-R3              HISTORICAL REPAIR RECORD PRESERVED
                      CONTINUATION LINEAGE / END-TO-END ACCOUNTING REPAIR RETAINED
D4-A5-R5              COMPLETE / PASS / RAW_FREEZE_EVALUATOR_INTEGRITY_SEALED
D4-A5                 BLOCKED / READY_FOR_SEPARATELY_AUTHORIZED_CONTINUATION
BATCH1                ACTIVE
BATCH2                SELECTED / FROZEN / NOT YET SCIENTIFICALLY VALIDATED
BATCH2 PRODUCTION     false
D4-A6                 NOT_STARTED
```

No D4-A5-R4 stage is created. D4-A5 is not marked scientifically PASS. The
continuation does not start automatically; it still requires separate
authorization.
