# Generic Answer-Obligation Completeness Development

Status: `COMPLETE / PASS / GENERIC_ANSWER_OBLIGATION_COMPLETENESS_IMPLEMENTED`

## Starting state and boundary

- Starting HEAD: `1b2e5600a8952a6f78601156a8ce2ee279616fad`
  (`Define F6 formal repeat policy`).
- Starting accepted product-behavior lineage:
  `d3a1b274b2784399a7dc51b094a17e466d208b50`.
- Starting normal mode: `legacy_question_core`.
- Known regenerable scratch `data/_a3_gold_args.txt` remained untracked and
  untouched.
- No Gold, novel dataset, holdout, F6-B, live model, judge, ablation, or
  composer empirical execution occurred.

## Architecture audit and decision

The legacy normal path represented the entire raw question as one
`question_core` answer point. That can verify factual support while failing to
represent an independently requested but omitted part. A supported partial
answer could therefore reach finalization without a first-class missing
obligation.

Option A, changing the default directly to `runtime_e1_v2`, was rejected. The
historical E2 activation failures and PE-LR1 promotion deferral remain binding,
and that mode also couples E3 candidate capture, post-verify retrieval, global
reselection, and retained-support behavior to the completeness change.

Option C, retaining the legacy default, was rejected because the existing
question-only E1 representation and E2 coverage/revision lifecycle already
provide a bounded, generic mechanism, and test-first contracts demonstrated a
safe smaller integration.

Option B was selected. Normal QA now uses the new candidate-bindable mode
`production_answer_obligations_v1`. It reuses the existing E1 decomposition,
E2 claim-to-point review, `missing_answer_point_ids`, one bounded revision, and
final coverage audit. It does not enable the E3 missing-point retrieval seam.
The legacy, shadow, and full experimental runtime modes remain explicit
internal paths.

## Generic obligation contract

The authoritative obligations come only from the raw user question. Existing
E1 v2 constraints remain unchanged: 1-5 points, exact question support spans,
independently satisfiable and omission-checkable needs, application-assigned
`point.N` identities, no retrieval input, no domain knowledge, and no hidden
prerequisites. A single request, a comparison, or an end-to-end workflow stays
one point unless the question independently requests more. Separate requested
targets or a location plus a reason can become separate points.

The production integration relabels the returned diagnostic projection as
`production_authoritative`; the standalone diagnostic entry point remains a
shadow diagnostic. Generation receives the projected semantic points. Review
maps each reviewable public claim to valid points and separately reports
missing points. Mapping presence alone does not establish completeness.

In semantic coverage modes, answer-point coverage remains the only answer
completeness authority. Legacy named requirements are absent from the
generation, review, and revision model-facing payloads and remain diagnostic
compatibility state only. Question-grounded source obligations remain separate.

## Verification, revision, and faithfulness

A supported answer may remain incomplete when the verifier reports a missing
explicit point. The graph permits one revision using the existing evidence.
The revision prompt may add only evidence-backed claims needed for missing
points and must not repeat verified claims. The revised draft passes through
the same deterministic citation/version/identifier checks and semantic review.

When the supplied evidence cannot support a missing point, revision may add
nothing. Existing supported claims can be safely salvaged, the missing point
remains visible in diagnostics, and no fact is invented. Unsupported claims are
removed; a narrower replacement is accepted only after the normal verifier
supports it.

The implementation did not change citation eligibility, wrong-version checks,
forbidden-evidence handling, unsupported-claim filtering, semantic verifier
authority, safe salvage, F4 role separation, F5 composer provenance, source
obligations, retrieval limits, or E3. Internal claim IDs/prefixes/markers remain
filtered before review and finalization. No prompt or schema version changed
because the existing E1/E2 prompts and schemas already express the selected
contract.

## Test-first matrix

Before the production edit, the new generic test file produced `10 failed`,
establishing RED against `legacy_question_core`.

| ID | Deterministic contract | Result |
| --- | --- | --- |
| T1 | Two supported obligations; initial A-only answer detects B and one revision adds B | PASS |
| T2 | A supported, B unsupported; B is not invented and remains missing | PASS |
| T3 | A genuine single request stays one point with no revision | PASS |
| T4 | A comparison stays one obligation | PASS |
| T5 | Separate “respectively” targets stay two obligations | PASS |
| T6 | An A-to-C workflow stays one point without guessed stages | PASS |
| T7 | Unsupported B is rejected; a narrower supported B can recover | PASS |
| T8 | Unsupported B without a recoverable replacement is removed | PASS |
| T9 | Legacy named requirements have no model-facing authority | PASS |
| T10 | Internal coverage bookkeeping never becomes public text | PASS |

Focused combined verification:

```text
PYTHONPATH=src python -m pytest \
  tests/unit/test_qa.py \
  tests/unit/test_generic_answer_obligation_completeness.py \
  tests/unit/test_question_decomposition.py \
  tests/unit/test_e2_a1_answer_point_coverage.py \
  tests/unit/test_e3_missing_point_retrieval.py \
  tests/unit/test_f6_release_identity.py -q

347 passed, 43 subtests passed
```

The complete deterministic execution log was:

1. RED before product implementation: T1-T10 `10 failed`.
2. First implementation iteration: T1-T10 `8 passed, 2 failed`; both failures
   exposed fixture-contract issues in the new T9/T10 tests, which were corrected.
3. Second iteration: T1-T10 `9 passed, 1 failed`; T9 incorrectly applied its
   assertion to the unrelated composer payload, and the assertion was narrowed
   to the three completeness-authority payloads.
4. Initial neighboring run: `132 passed, 10 failed`; failures were stale
   legacy-default assertions, fake clients without decomposition/coverage
   responses, two already-stale composer call-count assertions, and two
   historical source-comparison assertions in
   `test_e2_a3_runtime_activation.py` unrelated to the new mode.
5. Focused rerun after direct fixture updates: `130 passed, 1 failed`; the last
   failure was the stale composer payload assertion.
6. First expanded regression run: `331 passed, 43 subtests passed, 16 failed`;
   all failures were normal-path fake clients that still lacked the newly
   authoritative decomposition response.
7. `test_qa.py` after fake-client updates: `207 passed, 25 subtests passed, 3
   failed`; the remaining assertions still expected no normal coverage audit
   and no decomposition call.
8. Final focused/expanded run: `347 passed, 43 subtests passed`.

This covers the generic T1-T10 matrix, E1 decomposition, E2 coverage/revision,
E3 isolation and invariants, F2 compatibility boundaries, F4 generation versus
verification roles, F5 composer behavior, legacy explicit-mode availability,
and release-manifest mode binding. `git diff --check` passed.

## Exposed evidence boundary

Stored g013 observations were used only to identify the generic loss class and
to compare that class with the architecture. The literal question, entities,
paths, Gold ID, and rubric were not added to production code or acceptance
tests. g013 was not executed, scored, judged, or used to claim an empirical
fix.

## Product and lifecycle decision

Before this change, normal QA used one broad `question_core` completeness
objective. After this change, normal QA creates question-only semantic
obligations and carries them through generation, verification, bounded revision,
and final diagnostics. This can change user-visible answers by recovering an
evidence-supported requested part that the initial answer omitted. It is a real
normal-product behavior change, not a shadow-only or documentation change.

```text
MATERIAL_PRODUCT_CHANGE = true
NEW_CANDIDATE_DEVELOPMENT_HEAD = eda7d932a9b1b7b65436cba01e247859a6f9e056
ATTEMPT_5_ELIGIBILITY = ELIGIBLE_PENDING_FRESH_PREREGISTRATION_AND_CANDIDATE_FREEZE
```

Eligibility records that a materially changed, independently justified, and
deterministically verified candidate now exists. It does not establish
scientific benefit and does not authorize Attempt 5.

```text
candidate frozen = false
Attempt 5 preregistered = false
Attempt 5 executed = false

novel_validation = PRISTINE_FOR_CURRENT_LINEAGE
holdout access = 0
protected-content leakage = 0
F6-B execution = 0

PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## Limitations and next boundary

Deterministic tests establish the integration contract and faithfulness
boundaries only. They do not establish a better Gold score, an empirical g013
repair, generalization improvement, or release readiness. The new normal path
adds one question-decomposition model call and inherits decomposition
stochasticity. Scientific value and the historical activation-quality surface
must be assessed only under a fresh preregistration and immutable candidate
freeze.

```text
NEXT_TASK_RECOMMENDATION =
F6-A ATTEMPT 5 /
FRESH PREREGISTRATION, CANDIDATE FREEZE, AND CONTINUOUS PRE-RELEASE VALIDATION

NEXT_TASK_EXECUTION_AUTHORIZED = false
```
