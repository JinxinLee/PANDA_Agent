# D4-A5-R6 — Historical Baseline and Evaluator Lineage Preflight Repair

Status: `COMPLETE / PASS / HISTORICAL_BASELINE_AND_EVALUATOR_LINEAGE_PREFLIGHT_REPAIRED`
Date: 2026-09-05
Parent commit: `cc5db408929e82b29da76d92f1439ac53a4c8cf3` (`D4-A5-R5 seal raw-freeze evaluator integrity`)
R6 commit: `D4-A5-R6 repair historical baseline and evaluator lineage preflight`

R6 is a strictly **pre-exposure continuation-integrity repair**. It performs
zero provider/model/retrieval execution, zero plan acquisition, zero evaluator
execution, and zero production changes. R1 applicability, R2 bootstrap, R3
lineage/accounting, and the R5 raw-freeze allowlist/blob seal are preserved
exactly. No R4 stage is created or referenced.

---

## 1. Why R6 exists (independent audit findings)

R5 successfully sealed the plan-freeze → raw-freeze changed-file boundary and
the evaluator runner/test blobs, but a post-R5 independent audit found two
remaining evaluator-preflight defects:

1. **Wrong common historical baseline.** The evaluator preflight compared
   historical R1/R2/R3 artifacts against the single common baseline
   `A5_STOP_HEAD`. Because R1 artifacts were introduced after `A5_STOP_HEAD`
   (likewise R2 after R1, R3 after R2, R5 after R3), the real repository
   produces `git_blob(A5_STOP_HEAD, R1 artifact) = None` versus the real blob
   at raw-freeze HEAD — a false drift that would reject the valid real
   repository before any evaluator execution. Mechanically confirmed before
   any edit with `evaluation/d4_a5_r1_result.json`:
   `None` at `A5_STOP_HEAD`, `285e657e…` at `R1_HEAD` and at HEAD.
2. **Incomplete lineage proof.** The preflight did not independently
   re-establish the complete implementation-freeze → plan-freeze → raw-freeze
   parent chain; manifest-recorded heads could be accepted without Git proof.

R5's historical PASS artifact remains immutable; this record is forward-only.

## 2. Core repair A — per-stage historical artifact baselines

A small explicit contract (`historical_artifact_baselines()` /
`historical_baseline_drift()`) replaces the incorrect common-baseline check:

```text
A5_STOP_HEAD (dc679f8…) -> historical A5 first-attempt artifacts
R1_HEAD       (93ad95d…) -> R1 preregistration/result/report
R2_HEAD       (a53ca0a…) -> R2 preregistration/result/report
R3_HEAD       (447d03e…) -> R3 preregistration/result/report
R5_HEAD       (cc5db40…) -> R5 preregistration/result/report
```

Semantics: for every frozen historical artifact,
`blob(current raw-freeze HEAD, path) == blob(stage freeze commit, path)` must
hold. A later historical artifact is never required to exist at an earlier
lifecycle commit; an artifact missing at its owning stage freeze commit fails
closed, and an artifact that differs at raw-freeze fails closed. Git object
identity only — no SHA256 inventories, no generic provenance framework.

## 3. Core repair B — mechanically proven three-commit chain

Before any deterministic evaluator logic consumes retrieval outcomes, the
preflight now independently proves:

```text
R6 implementation freeze   message = D4-A5-R6 repair historical baseline and
                           evaluator lineage preflight; parent = R5_HEAD
    ↓ direct child
continuation plan-freeze   message = D4-A5 continuation freeze prospective
                           shared plans; parent = implementation freeze
    ↓ direct child
continuation raw-freeze    message = D4-A5 continuation freeze paired raw
                           retirement results (at current HEAD); parent =
                           plan freeze
```

Manifest-recorded heads (`continuation_implementation_freeze_head`,
`plan_freeze_head`) are treated only as candidate inputs and are cross-checked
against the Git-proven lineage: a manifest forged to claim the historical R5
head (or any unrelated commit) as the current implementation freeze is
rejected, as is a forged plan-freeze head. No skipped or intervening commit is
accepted. Git parentage and exact commit messages are authoritative.

## 4. Evaluator preflight ordering

1. raw-freeze commit/message/direct parent valid;
2. implementation-freeze identity valid (R6 message, parent = R5_HEAD);
3. plan-freeze direct parent = implementation freeze;
4. raw-freeze direct parent = plan freeze;
5. raw-freeze strict diff allowlist passes;
6. raw plans unchanged after plan freeze;
7. runner blob unchanged from the R6 implementation freeze;
8. focused-test blob unchanged from the R6 implementation freeze;
9. production/config/dataset paths unchanged;
10. historical artifacts equal their own stage baselines;
11. manifest lineage agrees with the mechanically established Git lineage;
12. evaluator/result artifacts not already present outside the expected
    lifecycle;
13. exposure state = RAW_RETRIEVAL_COMPLETE.

Only after all thirteen conditions hold may deterministic evaluation consume
raw scientific data.

## 5. R5 seal preserved

The strict raw-freeze diff allowlist
(`{continuation manifest, continuation raw paired retrieval results}`),
rejection of runner/focused-test/raw-plan/R5-R6-artifact/unrelated/
production drift, raw-plan immutability after plan freeze, and the runner/test
Git-object integrity checks are retained exactly — R6 only repairs the
historical baseline check and the complete lineage proof.

## 6. Realistic synthetic Git fixture

The R5-era fixture was too simplified (no historical artifacts at their stage
commits) and therefore missed the real-repository baseline defect. R6's fixture
creates every historical artifact at its own stage commit:

```text
A5 stop (historical A5 artifacts)
  ↓ R1 (R1 prereg/result/report)
  ↓ R2 (R2 artifacts)
  ↓ R3 (R3 artifacts)
  ↓ R5 (R5 artifacts)
  ↓ R6 (continuation manifest)
plan freeze (manifest PLANS_FROZEN + raw plans)
  ↓ raw freeze (manifest + raw results)
```

Minimal syntactically valid placeholders suffice for the Git identity checks.
The fixture reproduces the defect shape (R1 artifacts absent at
`A5_STOP_HEAD`) and the preflight passes under R6 per-stage baselines — it
would fail under the old common-baseline implementation. Per-stage drift tests
prove that drifting any single R1/R2/R3/R5/historical-A5 artifact is reported,
and a missing-at-owning-stage repository fails closed. The full-lineage matrix
proves: valid chain PASS; wrong implementation freeze (R5 head) FAIL; wrong
implementation message FAIL; wrong implementation parent FAIL; plan freeze not
a direct child of R6 FAIL; wrong plan-freeze message FAIL; raw freeze not a
direct child of plan freeze FAIL; forged manifest lineage FAIL. The critical
gates are never monkeypatched to success.

## 7. What did not change

Selected rules; D4-A4 masks (including
`model_factory_theory: pflueger_2017: [51, 57, 65]`); case order; 7-plan
protocol; 14-cell schedule; CURRENT_COMPAT/BATCH2_RETIREMENT arms; Batch-1
invariant; applicability tri-state; contribution-origin semantics; projection
logic; six per-rule dispositions; seven-level batch verdict; six primary
metrics; thresholds; MRR diagnostic-only; safety gates; accounting semantics;
unknown provider/token accounting; provider retry policy; the raw-freeze diff
allowlist. No case/rule/benchmark/locator-specific shortcut.

## 8. Zero exposure and verification

Zero Analyzer calls, plan acquisitions, embedding/reranker calls, retrieval
cells, QA/verifier/judge calls, scientific evaluator executions, DB/Qdrant
writes, and protected dataset access. `execute-phase-p`, `execute-phase-r`,
and `evaluate` were not run against the real scientific environment; only
synthetic temporary Git tests and read-only Git preflights were used.
Verification: 144 focused tests passing (11 added for R6), compile/static
checks, JSON parse, `git diff --check`, the exact R5→R6 changed-file audit,
protected historical/production Git-object identity checks, the real
read-only continuation-start preflight after the commit, the per-stage
baseline sanity check against the real repository (all five stages equal
their own freeze-commit blobs), and confirmation that the four future
scientific artifacts remain absent. No hash inventories.

## 9. Lifecycle state

```text
D4-A5 FIRST ATTEMPT   HISTORICAL / INVALID / PRE-OUTCOME STOP / PRESERVED
D4-A5-R1              HISTORICAL REPAIR RECORD PRESERVED
                      APPLICABILITY / PROVENANCE LOGIC RETAINED
D4-A5-R2              HISTORICAL REPAIR RECORD PRESERVED
                      CONTINUATION BOOTSTRAP REPAIR RETAINED
D4-A5-R3              HISTORICAL REPAIR RECORD PRESERVED
                      CONTINUATION LINEAGE / END-TO-END ACCOUNTING REPAIR RETAINED
D4-A5-R5              HISTORICAL REPAIR RECORD PRESERVED
                      RAW-FREEZE ALLOWLIST / EVALUATOR BLOB SEAL RETAINED
D4-A5-R6              COMPLETE / PASS / HISTORICAL_BASELINE_AND_EVALUATOR_LINEAGE_PREFLIGHT_REPAIRED
D4-A5                 BLOCKED / READY_FOR_SEPARATELY_AUTHORIZED_CONTINUATION
BATCH1                ACTIVE
BATCH2                SELECTED / FROZEN / NOT YET SCIENTIFICALLY VALIDATED
BATCH2 PRODUCTION     false
D4-A6                 NOT_STARTED
```

No R4 stage is added. D4-A5 is not marked scientifically PASS. The
continuation does not start automatically; it still requires separate
authorization.
