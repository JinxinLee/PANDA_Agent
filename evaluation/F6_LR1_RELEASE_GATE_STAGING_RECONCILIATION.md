# F6-LR1 — Release-Gate Staging Reconciliation

Decision: **F6-LR1 = COMPLETE / PASS / RELEASE_GATE_STAGING_RECONCILED.**

Type: static lifecycle / release-protocol reconciliation. Zero product code
changes; zero evaluator/freezer changes; zero benchmark or manifest changes;
zero model calls.

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## 1. Starting state

- Starting HEAD: `03fc400e54d66f24d9009f3ab7378c0d6dde0882`
  ("Record F6 holdout availability hold") — matched the expected baseline.
- Worktree clean; no unrelated user work; no history rewrites.
- Reconstructed lifecycle at start: F5/F5-R1 COMPLETE/PASS; F6 attempt 1 =
  HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET (zero outcome); Phase F =
  IN_PROGRESS / F5_COMPLETE_F6_HOLD.

## 2. Historical F6 attempt-1 HOLD (immutable)

`evaluation/F6_RELEASE_EVALUATION_AND_GENERALIZATION_GATE.md` and
`evaluation/f6_release_evaluation_result.json` remain untouched as attempt-1
historical evidence:

```text
F6 attempt 1 = HISTORICAL / HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET / ZERO_OUTCOME
scientific/evaluation calls = 0
scientific/evaluation tokens = 0
```

That HOLD was valid under the then-authorized protocol: attempt 1 treated
physical holdout availability as a prerequisite for ANY F6 scientific
execution, the package was absent, and the attempt correctly stopped before
outcomes. F6-LR1 does not relabel it PASS, FAIL, or "incorrect"; it records
"historical attempt valid; protocol staging subsequently reconciled by
F6-LR1". F6-LR1 is a prospective lifecycle correction — after it, the old HOLD
no longer blocks F6-A; it only records attempt-1 history.

## 3. Why the old prerequisite was over-strict

The old staging collapsed two independent concerns into one gate:

```text
OLD: physical protected holdout availability = prerequisite for all F6 scientific work
```

But the datasets involved have different exposure economics. Gold is an
exposed benchmark reference; novel_dev is already outcome-exposed development
material; novel_validation is a candidate-level pre-release gate whose value
does not depend on the holdout; only the sealed holdout is a scarce blind
resource whose protection requires physical/execution-boundary controls.
Requiring the mounted holdout package before touching any of the exposed or
validation cohorts blocked exactly the work whose purpose is to decide whether
the holdout budget should be consumed at all.

## 4. Root lifecycle correction

```text
NEW: holdout governance / metadata integrity = F6-A precondition
     physical protected holdout package availability = F6-B precondition only
```

Absence of a mounted holdout package must NOT block: exposed Gold evaluation;
exposed novel_dev diagnostics; pristine novel_validation; the preregistered
benchmark-dependency ablation; the composer release audit; or the F6-A
generalization decision.

## 5. New F6 structure

```text
F6
├── F6-A — Pre-Release Validation & Generalization Gate
└── F6-B — Protected Blind Release Gate
```

### F6-A — Pre-Release Validation & Generalization Gate

Purpose: determine whether a frozen release candidate is sufficiently strong
and generalizable to justify consuming protected holdout budget.

Allowed evidence: Gold v2.6; novel_dev; novel_validation; the approved
evaluation-only ablation; the composer release audit. F6-A explicitly excludes
protected holdout execution.

Terminal states:

```text
COMPLETE / PASS / HOLDOUT_ELIGIBLE
COMPLETE / FAIL / PRE_RELEASE_VALIDATION_GATE_FAILED
COMPLETE / INCONCLUSIVE / INSUFFICIENT_PRE_RELEASE_EVIDENCE
HOLD / PRE_RELEASE_PRECONDITION_NOT_MET
```

Primary purpose (§23 of the authorization): F6-A does not pass the release —
its positive terminal state is HOLDOUT_ELIGIBLE, i.e. the candidate has earned
the right to consume protected holdout budget.

Run order (§8):

```text
Stage A0 — zero-outcome infrastructure / identity preflight
Stage A1 — preregistration + candidate freeze
Stage A2 — Gold v2.6 full evaluation
Stage A3 — preregistered Gold benchmark-dependency ablation
Stage A4 — novel_dev exposed diagnostic
Stage A5 — novel_validation primary candidate-level validation
Stage A6 — composer empirical release audit
Stage A7 — F6-A gate decision
```

No protected holdout is used anywhere in F6-A.

### F6-B — Protected Blind Release Gate

Purpose: run the exact F6-A-passed frozen candidate once against the sealed
protected holdout and make the final blind release decision. F6-B is the only
protected blind release decision; only F6-B may close Phase F with
`COMPLETE / PASS / RELEASE_GENERALIZATION_GATE_PASSED` when all protected
release gates pass.

Terminal states:

```text
COMPLETE / PASS / PROTECTED_BLIND_RELEASE_GATE_PASSED
COMPLETE / FAIL / PROTECTED_BLIND_RELEASE_GATE_FAILED
COMPLETE / INCONCLUSIVE / PROTECTED_EXECUTION_INCOMPLETE
HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET
```

Run order (§9), only after `F6-A = COMPLETE / PASS / HOLDOUT_ELIGIBLE`:

```text
B0 — verify same frozen candidate identity
B1 — protected workspace / package availability preflight
B2 — verify sealed/frozen holdout identity
B3 — single blind full run
B4 — sanitized aggregate receipt
B5 — final protected release gate decision
```

No alternate candidate may be introduced between A and B.

## 6. Dataset-role matrix

| Dataset | Role | Holdout required? | Notes |
| ------- | ---- | ----------------- | ----- |
| Gold v2.6 (m6-benchmark-v2.6, 120) | EXPOSED_BENCHMARK_REFERENCE | No | reusable for exposed benchmark validation |
| novel_dev (novel-v1-dev-0.3.0, 28) | EXPOSED_DEVELOPMENT_GENERALIZATION_DIAGNOSTIC | No | outcome-exposed; reusable for diagnostics; never pristine evidence |
| novel_validation (novel-v1-validation-0.2.0, 15) | CANDIDATE_LEVEL_PRE_RELEASE_GENERALIZATION_GATE | No | used BEFORE holdout; see exposure semantics |
| novel_holdout (panda-novel-holdout-v1, 13, sealed) | FINAL_PROTECTED_BLIND_RELEASE_EVIDENCE | **Yes (F6-B only)** | remains sealed until F6-A PASS; not development data; mounting not required during F6-A |

## 7. Holdout-budget principle

```text
protected holdout is a scarce blind-evaluation budget
```

Once holdout outcomes influence development of a later candidate, the same
holdout can remain useful as a historical benchmark, regression diagnostic, or
retrospective evidence — but it cannot truthfully serve as pristine blind
evidence for that modified candidate. Therefore: do not consume holdout before
F6-A PASS; a failed F6-A must NOT trigger holdout (development/validation
absorb iteration cost; the holdout does not).

## 8. Candidate-identity continuity between A and B

```text
F6_A_candidate_identity == F6_B_candidate_identity
```

Between F6-A PASS and F6-B there must be no change to product code, prompts,
model identities, runtime mode, retrieval config, index/corpus identity,
thresholds, query expansions, or F5 composer behavior. Any behavior-affecting
identity change strips `HOLDOUT_ELIGIBLE` and requires a new F6-A before
holdout use. Future execution should verify the identical frozen candidate at
F6-B B0 before any protected call.

## 9. Validation exposure semantics

`novel_validation` is not indefinitely blind. Formalized states:

1. Before the first candidate-level run:
   `PRISTINE_FOR_CURRENT_LINEAGE` (current state per historical run records).
2. After aggregate-only outcome observation with no development response: it
   remains historical validation evidence for that candidate.
3. If case-level question/Gold/outcome information is inspected and used to
   guide development: exposure-ledger events are appended per the existing
   curation contract, and later candidates must distinguish pristine
   validation from exposed validation diagnostics. Exposure is never silently
   erased.

## 10. Holdout availability boundary

F6-A may proceed when: holdout governance exists; holdout metadata identity
exists (`panda-novel-holdout-v1`, FROZEN_SEALED, expected_count 13,
externally managed, loader contract `--dataset <external-path>`); the
repository records its protected/sealed role; and there is no evidence the
holdout has been exposed (`outcome_observed: false`). F6-A does NOT require a
local protected path, a mounted holdout package, or an online protected worker
workspace — those are F6-B prerequisites (B1/B2).

## 11. Pre-freeze engineering debt carried into F6-A Stage A0

The following findings from the attempt-1 preflight audit are carried forward
as F6-A Stage A0 work. They are NOT product defects and do NOT invalidate the
historical HOLD. F6-LR1 deliberately does NOT implement them (protocol
decision stays separate from implementation):

- **A. evaluator/freezer benchmark-authority equivalence**: the evaluator
  accepts v2.6 only when `dataset_sha256` matches and
  `official_ready`/`structurally_valid` are true; the candidate freezer must
  enforce the same authority contract so freezer and evaluator can never
  disagree.
- **B. benchmark manifest identity**: the freeze must record the benchmark
  manifest itself, at minimum `benchmark_manifest_hash`, `benchmark_version`,
  `benchmark_dataset_hash`, `benchmark_question_count`, `official_ready`,
  `structurally_valid`.
- **C. Docker identity semantics**: decide and enforce one contract before
  candidate freeze — either Docker image identity is mandatory (non-empty
  required digest set) or it is diagnostic-only documentation. The current
  `status=ok / images=[]` combination must not remain ambiguous.
- **D. candidate gate semantics**: with no candidate frozen,
  `candidate_changes_after_freeze` must be `NOT_REACHED` / `NOT_APPLICABLE`,
  not PASS.
- **E. benchmark post-signing amendment provenance**: the D4-A2-R1 `g021`
  forward correction must stay traceable (the attempt-1 preflight alignment
  record with previous/authorizing hashes already provides this); original
  review metadata is not rewritten; no Gold semantic content is modified in
  F6-LR1.

## 12. F6-A / F6-B artifact namespace (prospective)

Future execution uses distinct attempt artifacts and does not overwrite
attempt-1 records:

```text
evaluation/F6_A_PRE_RELEASE_VALIDATION_PREREGISTRATION.md
evaluation/f6_a_pre_release_validation_preregistration.json
evaluation/F6_A_PRE_RELEASE_VALIDATION_RESULT.md
evaluation/f6_a_pre_release_validation_result.json
```

F6-B likewise receives distinct protected-release artifacts.

## 13. Authorization boundary and accounting

F6-LR1 authorizes reconciliation only. It does NOT authorize F6-A scientific
execution, any Gold/novel_dev/novel_validation run, the composer release
audit, ablation, candidate freeze, preregistration, F6-B, or holdout access.

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## 14. Resulting lifecycle state

```text
F6 attempt 1 = HISTORICAL / HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET / ZERO_OUTCOME
F6-LR1 = COMPLETE / PASS / RELEASE_GATE_STAGING_RECONCILED
F6-A = NOT_STARTED / READY_FOR_SEPARATE_EXECUTION
F6-B = NOT_STARTED / LOCKED_PENDING_F6_A_PASS
Phase F = IN_PROGRESS / F6_A_READY
```

## 15. Next recommendation

F6-A — Pre-Release Validation & Generalization Gate (recommendation only;
requires separate explicit authorization; its Stage A0 must first resolve the
§11 engineering-debt items).

NEXT_TASK_EXECUTION_AUTHORIZED = false
