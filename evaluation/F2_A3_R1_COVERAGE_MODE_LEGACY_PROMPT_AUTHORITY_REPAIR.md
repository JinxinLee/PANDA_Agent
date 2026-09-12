# F2-A3-R1 — Coverage-Mode Legacy Prompt Authority Repair

Status: `COMPLETE / PASS / COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REMOVED`
Type: corrective bounded production repair of F2-A3 + deterministic
verification (PF-LR1 Group C). Zero PANDA scientific/evaluation calls; zero
protected-data access.

Task identity: F2-A3-R1 — Coverage-Mode Legacy Prompt Authority Repair.
Traceability: PF-LR1 Group C / F1 residuals R08, R09, R11 (provenance only).

## 1. Historical correction record

- F2-A3 (commit `7bf0df4`, "Reconcile E1 E2 compatibility authority") correctly
  retired the code-side compatibility authorities: deterministic
  missing-requirement enforcement, model-returned known missing-requirement
  consumption, requirement-driven revision, plan-driven dataflow augmentation,
  and boundary-locator payloads in coverage modes.
- An independent post-commit audit did **NOT** accept the original
  `COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED` closeout: the
  model-facing authority was still live. Generation, coverage review, and
  revision payloads still carried the full legacy `answer_requirements` (and
  requirement evidence), the inherited/coverage prompt contracts still treated
  them as a completeness axis, and a stale `supported=false` verdict explained
  only by legacy requirements could still create `global_review_failure`.
- F2-A3-R1 repairs exactly those remaining surfaces. No historical commit or
  result was rewritten; `7bf0df4` remains in history and this report is the
  authoritative final correction. The original F2-A3 report carries a
  correction/supersession notice distinguishing its valid changes from its
  premature final authority claim.

## 2. Starting state

```text
HEAD = 7bf0df48d0fd2e613bf34b952a6c11f5aa69f52f (Reconcile E1 E2 compatibility authority)
working tree = clean
F2-A3 = COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED (premature; corrected by this repair)
F2 = IN_PROGRESS / A1_A2_A3_COMPLETE
F3 = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A3_COMPLETE
normal default = legacy_question_core
default promotion = DEFERRED
```

## 3. Independent defect confirmation and pre-fix authority matrix

All four audited leaks were live at HEAD `7bf0df4`:

| Call | answer_requirements | requirement_evidence | missing_requirement_ids | missing_answer_point_ids | Controlling prompt |
|---|---|---|---|---|---|
| legacy generation | full legacy set | n/a | n/a | n/a | ANSWER_SYSTEM_PROMPT ("satisfy every applicable obligation") |
| coverage generation | **full legacy set (LEAK)** | n/a | n/a | runtime points | ANSWER_SYSTEM_PROMPT (same) |
| legacy review | full legacy set | full | model + deterministic, enforced | n/a | EVIDENCE_REVIEW_SYSTEM_PROMPT (requirements authoritative) |
| coverage review | **full legacy set (LEAK)** | **full (LEAK)** | model-returned, accepted-if-ignored | enforced | inherited legacy wording + "separate completeness axis" extension |
| legacy revision | full legacy set | filtered to missing | state missing ids, enforced | n/a | REVISION_SYSTEM_PROMPT ("apply every supplied answer_requirements") |
| coverage revision | **full legacy set (LEAK)** | **computed (LEAK)** | cleared (F2-A3) | enforced | inherited "apply every supplied..." + "and/or missing legacy requirements" |

Additionally, `review.supported=false` with no structural failure other than
stale legacy requirement ids still produced `global_review_failure` in coverage
modes (indirect whole-answer failure).

## 4. Repair (`src/panda_agent/qa.py`, `src/panda_agent/prompts.py`)

Authority representation: `answer_requirements` in state remains the full
legacy set (unknown-requirement guard, diagnostics, legacy execution); the
**model-facing** payloads in coverage modes carry none of it.

1. Generation: `_answer` computes the full legacy set, sends
   `answer_requirements = []` to the model in coverage modes, and stores the
   full legacy set in state. The shared generation prompt therefore has
   nothing legacy to enforce (empty-authoritative-payload shape preferred by
   the repair contract); legacy mode payload is unchanged.
2. Review: `_verify` sends `answer_requirements = []` and
   `requirement_evidence = {}` in coverage modes. The full legacy set still
   feeds `known_requirement_ids` (unknown-id guard). Legacy review payload
   unchanged.
3. `supported` reconciliation: in coverage modes, if `supported=false` has no
   structural failure (no unsupported, no irrelevant, no missing points, no
   accepted legacy requirements) and every returned
   `missing_requirement_ids` entry is a known legacy id (stale obsolete-axis
   explanation), the aggregate boolean is treated as obsolete: no
   `evidence review failed` error and no `global_review_failure`. Any other
   `supported=false` (no explanation, or unknown ids) keeps the conservative
   global failure. Structured fields only; no reason-text parsing. Unknown
   ids remain caught by coverage-review validation (`invalid answer-point
   coverage review`) before consumption.
4. Revision: `_revise` sends `answer_requirements = []`,
   `missing_requirement_ids = []`, `requirement_evidence = {}` in coverage
   modes (stale state-level ids cannot leak back); legacy payload unchanged.
5. Prompts (coverage-specific extensions only): the coverage review extension
   now states that named legacy answer requirements are not an authoritative
   completeness axis and `missing_requirement_ids` must be returned empty;
   the coverage revision extension now requests only
   `missing_answer_point_ids`-driven claims ("and/or missing legacy
   requirements" removed). Legacy `EVIDENCE_REVIEW_SYSTEM_PROMPT` /
   `REVISION_SYSTEM_PROMPT` contracts are unchanged.
   `PROMPT_SET_VERSION` 3.8.0 → 3.9.0 (test assertion updated consistently).

## 5. Post-fix authority matrix

| Call | answer_requirements | requirement_evidence | missing_requirement_ids | missing_answer_point_ids | Authority |
|---|---|---|---|---|---|
| legacy generation | full legacy set | n/a | n/a | n/a | legacy requirements authoritative |
| coverage generation | [] | n/a | n/a | runtime points | answer points only |
| legacy review | full legacy set | full | enforced | n/a | legacy requirements authoritative |
| coverage review | [] | {} | ignored for known ids; unknown ids guarded | enforced | answer-point coverage only |
| legacy revision | full legacy set | filtered | enforced | n/a | legacy missing requirements authoritative |
| coverage revision | [] | {} | [] | enforced | missing answer points + unsupported claims only |

## 6. Adversarial contract (T1–T12)

| Test | Contract | Result |
|---|---|---|
| T1/T8 `test_generation_payload_authority_is_mode_scoped` | plan-shaped requirement absent from coverage generation payloads (shadow+runtime); still present in legacy | PASS |
| T2 | covered by T1 legacy case | PASS |
| T3 `test_coverage_review_payload_has_no_legacy_axis` | coverage review payload: `answer_requirements == []`, `requirement_evidence == {}` | PASS |
| T4 `test_coverage_revision_payload_has_no_legacy_axis` | forced missing point: revision payload has `missing_answer_point_ids`, empty legacy axis, points-only scope; stale state ids cannot leak back | PASS |
| T5 `test_stale_legacy_missing_requirement_does_not_fail_coverage_answer` | `supported=false` explained only by known legacy ids → no global failure, claims supported, coverage complete/evaluable (shadow+runtime) | PASS |
| T6 `test_unknown_missing_requirement_remains_guarded` | unknown id caught by coverage-review validation; conservative failure retained | PASS |
| T7 `test_genuine_unsupported_claim_still_fails_in_coverage_mode` (+ existing unsupported/missing-point tests) | genuine semantic failures still fail/repair | PASS |
| T9 | legacy deterministic completeness still active (existing regression-protected requirement tests; legacy bridge tests) | PASS |
| T10 `test_dataflow_augmentation_is_mode_scoped` / `test_boundary_locators_are_mode_scoped` | F2-A3 R11 scoping intact | PASS |
| T11 `PointerNormalizationCompletenessTests` | F2-A2 intact | PASS |
| T12 `VerifierSupportSemanticTests` | F2-A1/F2-A1-R1 intact (no support-bypass return) | PASS |

## 7. Verification

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **76 passed,
  11 subtests passed** (includes T1–T12).
- `PYTHONPATH=src python -m pytest tests/unit/test_e2_a1_answer_point_coverage.py
  tests/unit/test_e3_missing_point_retrieval.py -q` → **91 passed** (49 focused
  E3 deterministic tests + 42 E2-A1 tests; shared `_verify`/`_revise`
  model-facing behavior regression only; E3 lifecycle not reopened).
- Combined focused run: **167 passed, 11 subtests passed**.
- `git diff --check` PASS; boundary audit: zero diff touches on R10 pointer
  contract, verifier-support machinery, `select_final_evidence`, planned-locator
  augmentation, E3 trigger/retained-support logic, retrieval, or selection.
- PANDA scientific/evaluation calls = 0; PANDA scientific/evaluation tokens = 0.

## 8. Limitations

- The legacy bridge (named-requirement derivation, evidence selection, and
  enforcement in `legacy_question_core`) is intentionally unchanged; it is the
  normal-default authority and not benchmark debt suitable for deletion now.
- Coverage-mode payload context no longer contains legacy requirements at all,
  so a legacy-trained reviewer has no requirement axis to reason about by
  design; the schema field remains for compatibility and must be returned
  empty.
- No scientific evaluation was run or authorized; behavior beyond the focused
  deterministic surface is unmeasured by design.

## 9. Lifecycle closeout

```text
F2-A3-R1 = COMPLETE / PASS / COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REMOVED
F2-A3    = COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED
           (final closure achieved only after this corrective repair)
F2       = IN_PROGRESS / A1_A2_A3_COMPLETE (F2 still incomplete)
F3       = NOT_STARTED / UNEXECUTED
Phase F  = IN_PROGRESS / F2_A3_COMPLETE
normal default = legacy_question_core (unchanged)
default promotion = DEFERRED (unchanged; promotion relevance != promotion authorization)
```

```text
NEXT_TASK_RECOMMENDATION = F2-A4 — Premise and Refusal Generalization
                           (PF-LR1 Group D / F1 residual R04)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
