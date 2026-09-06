# D4-A5-R7 — Minimal Post-Plan-Freeze Gate Repair

Status: `COMPLETE / PASS / POST_PLAN_FREEZE_GATE_AND_EXECUTION_INTEGRITY_SEALED`
Date: 2026-09-06
Parent commit: `12b5dc6908e7dc22f6fa88fa189252099df8f3c6` (`D4-A5 continuation freeze prospective shared plans`)
R7 commit: `D4-A5-R7 repair post-plan-freeze gate and continuation handoff`

R7 is a strictly forward-only, minimal repair performed AFTER successful
prospective plan acquisition and AFTER the scientific plan-freeze boundary was
committed, but BEFORE any Phase-R paired retrieval exposure. It performs zero
provider calls, zero plan redraws, zero retrieval, and zero evaluator
execution.

---

## 1. The defect (mechanically confirmed before editing)

`verify_continuation_plan_freeze_gate()` compared R1 artifacts AND R2 repair
artifacts against `R1_HEAD`:

```python
git_paths_unchanged_between(project_root, R1_HEAD, head, [R1 artifacts, R2 artifacts])
```

R2 artifacts were introduced at `R2_HEAD`, which came after `R1_HEAD`.
Mechanical confirmation on the real repository:

```text
R2 artifacts @ R1_HEAD         = absent (None)
R2 artifacts @ R2_HEAD         = present (real blobs)
R2 artifacts @ plan-freeze     = identical to R2_HEAD blobs
→ None != valid R2 blob → false historical drift
```

This false drift blocked the real-repository plan-freeze verification after
successful Phase P. The finding is recorded forward-only; R1/R2 artifacts were
not modified.

Amend finding (independent audit, mechanically confirmed before editing): the
R7 historical-gate refactoring removed the previous clean-worktree/index seal.
Commit-to-commit Git checks could pass while Phase R or the evaluator consumed
dirty worktree files — the committed raw-plan blob can remain unchanged while
worktree raw-plan contents differ, and `execute_phase_r()` reads the worktree
raw plans (the evaluator reads the worktree raw results). Therefore commit-level
plan identity PASS + a dirty worktree could allow execution of unfrozen plan
contents. The same principle applies to dirty runner/test/manifest/raw-results
state before raw-freeze/evaluator consumption.

## 2. Core repair — per-stage baseline contract

The defective common-baseline block was removed and replaced with the already
accepted R6 per-stage baseline semantics (`historical_baseline_drift`):

```text
A5 artifacts -> A5_STOP_HEAD
R1 artifacts -> R1_HEAD
R2 artifacts -> R2_HEAD
R3 artifacts -> R3_HEAD
R5 artifacts -> R5_HEAD
```

Real historical drift still fails closed (missing at owning stage, or changed
after owning stage). Later-stage artifact absence at an earlier stage is not
drift. Git object identity only — no SHA256 inventories.

### Amend repair — clean-worktree/index execution seals

Both seals validate the worktree AND the index, and neither replaces the
commit-level Git-object checks (both layers are required):

```text
verify_phase_r_preflight            -> assert_clean_worktree FIRST, before any
                                       other authorization check
verify_continuation_raw_freeze_gate -> assert_clean_worktree FIRST; the
                                       evaluator preflight inherits the seal
                                       through its call chain
```

The historical `verify_continuation_plan_freeze_gate` stays head-independent
and gains no clean-worktree requirement: it validates the immutable
`12b5dc6…` boundary from a later descendant HEAD. Clean-worktree requirements
belong at execution boundaries only.

The R7 repair-diff allowlist is now exactly the 7-file R7 repair contract;
`evaluation/d4_a5_continuation_execution_manifest.json` is excluded, so an R7
commit that modifies the continuation manifest is rejected by the Phase-R
preflight repair-diff seal (executable policy, covered by a regression test).

## 3. Frozen seven plans untouched

The plan-freeze commit `12b5dc6…` and its raw-plan artifact
(`evaluation/d4_a5_continuation_raw_prospective_plans.json`) are immutable
scientific evidence. The raw plans Git object at every R7/future boundary
equals the blob at `12b5dc6…`. Mechanically confirmed:

```text
plans_planned = 7, plans_recorded = 7, plans_completed = 7
plans_reused = 0, plans_provider_failed = 0, plans_gate_stopped = 0
retries = 0; Analyzer logical calls = 7; provider attempts = 7
recorded token usage = 17,043; embedding = 0; reranker = 0
all 7 records: status = COMPLETED, provenance_gate.pass = true
```

No plan was reacquired, redrawn, edited, or replaced. Phase P was not rerun.

## 4. Post-plan lineage (minimal)

The immutable scientific topology is now:

```text
R6  plan-acquisition implementation freeze  e91c2bb…
    ↓ direct child
PLAN FREEZE                                 12b5dc6…
    ↓ direct child
R7  post-plan retrieval implementation freeze  <R7 HEAD>
    ↓ future direct child
RAW FREEZE                                  <future>
```

R6 remains the implementation that generated the seven plans; `12b5dc6…`
remains the authoritative scientific plan-freeze boundary; R7 is only the
post-plan continuation execution repair boundary. The raw-plan artifact's
existing R6 provenance fields are untouched. Forward lineage uses clear names
(`continuation_plan_acquisition_implementation_freeze_head`,
`continuation_plan_freeze_head`,
`continuation_retrieval_implementation_freeze_head`) without a schema
migration.

## 5. Phase-R preflight adaptation

`verify_phase_r_preflight()` is now executable while HEAD is R7. It proves:
a clean worktree AND index (execution-integrity seal, first check); R6
message/parent; plan-freeze message and parent = R6; the R6 → plan-freeze
diff limited to manifest + raw plans; R7 message and parent = the frozen
plan-freeze HEAD; raw plans at R7 identical to the plan freeze; 7 frozen plans
structurally complete; per-stage historical baselines; production/scientific
authorities unchanged; exposure = PLANS_FROZEN. Success: `READY_FOR_PHASE_R`.
Phase R itself is not executed.

## 6. Minimal downstream lineage

The future raw-freeze gate now requires: a clean worktree AND index (the
evaluator preflight inherits this seal through its call chain); parent
(raw-freeze) = R7; raw plans at raw-freeze == raw plans at `12b5dc6…`; strict
R7 → raw-freeze allowlist `{manifest, raw results}`. The future evaluator
preflight proves the minimal four-node chain R6 → plan-freeze → R7 → raw-freeze
with per-stage baselines, runner/test blob seal to R7, production immutability,
and manifest cross-check. No evaluator logic redesign.

## 7. Strict scientific non-scope

Analyzer logic, query expansion behavior, frozen Batch2 masks (including
`pflueger_2017: [51, 57, 65]`), case cohort/order, applicability semantics,
contribution ledger semantics, projections, retrieval, selectivity, reranker,
evidence selector, metrics, thresholds, dispositions, verdict logic,
accounting semantics, and retry policy are all unchanged. No `n014` or
`pflueger_2017` special case. The exposed Phase-P applicability outcomes (e.g.
n014's 3 ACTIVE + 3 INACTIVE/HOLD + 0 AMBIGUOUS) do not influence
implementation.

## 8. Zero exposure and verification

Zero Analyzer calls, plan acquisitions/redraws, embedding, reranker, retrieval
cells, QA/verifier/judge, scientific evaluator executions, DB/Qdrant writes,
Batch2 production activations. `execute-phase-p`, `execute-phase-r`, and
`evaluate` were not run. Verification: 140 focused tests passing (including
the seven dirty-worktree/index and R7 manifest-diff rejection regressions),
compile/static checks, JSON parse, `git diff --check`, the exact
plan-freeze→R7 changed-file audit (exactly the 7-file R7 repair contract; the
continuation manifest excluded), raw-plan Git-object identity, per-stage
historical identity, production identity, and the real post-amend read-only
Phase-R preflight reaching `READY_FOR_PHASE_R` at the amended R7 HEAD. No hash
inventories.

## 9. No self-referential SHA; manifest unchanged

Mandatory rule (task Section 5): the R7 SHA depends on the commit tree, so the
commit tree must not depend on the R7 SHA. No file committed by R7 contains the
R7 commit SHA; R7 identity is established only by Git (HEAD message, HEAD
parent, HEAD SHA after the commit exists). The stable R7 SHA is consumed only
later, at Phase-R runtime.

Accordingly, the continuation manifest is NOT modified in R7: it remains
byte-for-byte identical to the `12b5dc6…` plan-freeze version (PLANS_FROZEN,
7 plans complete, Phase R not started, Batch2 production false). The future
Phase-R runtime persists `retrieval_implementation_freeze_head` (= the R7 HEAD)
and `plan_freeze_head` (= `12b5dc6…`) into the manifest after the preflight
PASS and BEFORE the first retrieval call (verified by
`test_r7_runtime_provenance_handoff`). The future raw-freeze gate then requires
parent(raw-freeze) = R7, raw plans at raw-freeze == raw plans at `12b5dc6…`,
and runner/test at raw-freeze == runner/test at R7.

## 10. Lifecycle state

```text
D4-A5 CONTINUATION PHASE P  COMPLETE / 7_OF_7_PROSPECTIVE_SHARED_PLANS_FROZEN
PLAN FREEZE                 12b5dc6… PRESERVED / IMMUTABLE
D4-A5-R7                    COMPLETE / PASS /
                            POST_PLAN_FREEZE_GATE_AND_EXECUTION_INTEGRITY_SEALED
D4-A5 CONTINUATION          IN_PROGRESS /
                            READY_FOR_SEPARATELY_AUTHORIZED_PAIRED_RETRIEVAL
PHASE R                     NOT_STARTED
BATCH1                      ACTIVE
BATCH2 PRODUCTION           false
D4-A6                       NOT_STARTED
```

D4-A5 is not marked scientifically PASS. Phase R does not start
automatically; it still requires separate authorization.
