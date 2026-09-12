# F2-A3 — E1/E2 Compatibility Retirement

> **CORRECTION / SUPERSESSION NOTICE (F2-A3-R1).** This report's initial
> terminal `COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED`
> closeout was subsequently found premature by an independent post-commit
> audit: while the code-side retirement steps below are valid and were
> preserved, legacy `answer_requirements` were still sent to the generation,
> coverage-review, and revision models in coverage modes, the coverage prompt
> contracts still treated them as a completeness axis, and a stale
> `supported=false` verdict explained only by legacy requirements could still
> create `global_review_failure`. That model-facing authority leak is repaired
> by `evaluation/F2_A3_R1_COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REPAIR.md`
> (F2-A3-R1 = `COMPLETE / PASS / COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REMOVED`),
> which is the authoritative final lifecycle record for this surface. The
> narrative below is preserved unchanged for historical transparency.

Status: `COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED`
Type: bounded cluster production cleanup + deterministic verification (PF-LR1
Group C). Zero PANDA scientific/evaluation calls; zero protected-data access.

Task identity: F2-A3 — E1/E2 Compatibility Retirement.
Traceability: PF-LR1 Group C / F1 residuals R08, R09, R11 (provenance only).

## 1. Starting state

```text
HEAD = d480fc29342286537d5acd1e131086cff8bac26c (Generalize pointer normalization completeness)
working tree = clean
F2-A1-R1 = COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED
F2-A1 = COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED
F2-A2 = COMPLETE / PASS / QUESTION_DERIVED_POINTER_NORMALIZATION_COMPLETENESS_ESTABLISHED
F2 = IN_PROGRESS / A1_A2_COMPLETE
F3 = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A2_COMPLETE
normal default = legacy_question_core
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
default promotion = DEFERRED
```

## 2. Group-C surface inventory and dispositions

| Surface | Pre-task authority | Question-derived? | Plan-derived? | Action |
|---|---|---|---|---|
| R08 `_answer_requirements` (13 named-requirement families) | authoritative in all modes | mixed: intent/vocabulary question-grounded; some plan-only activation paths (`workflow_or_operational_grounding` via required source types; `longitudinal_vs_angular_acceptance` plan-only path; `factory_composition` plan-vocabulary path) | partially | RETAIN_LEGACY_BRIDGE (derivation unchanged; consumed as non-authoritative context in coverage modes) |
| R08 requirement payload into generation/review/revision prompts | all modes | — | — | RETAIN_LEGACY_BRIDGE (context only in coverage modes) |
| R09 model-returned `missing_requirement_ids` consumption | all modes: error + bounded-revision driver | — | — | MODE_SCOPE: ignored for known ids in coverage modes; unknown-id hallucination guard retained |
| R09 `_deterministic_missing_requirement_ids` execution | all modes | requirement activation mixed | partially | MODE_SCOPE: not executed in coverage modes; fully active in legacy mode |
| R09 requirement-evidence selection / compaction | all modes (review/revision payload) | — | — | RETAIN_LEGACY_BRIDGE (payload context; non-authoritative in coverage modes) |
| R09 bounded revision via missing requirements | all modes | — | — | MODE_SCOPE: coverage-mode revision driven by `missing_answer_point_ids` only |
| R09 E3 second-verify deterministic-requirement view (`is_e3_second_verify` claim/valid-evidence projection) | runtime only | — | — | RETIRE (its only consumer — deterministic requirement enforcement in coverage modes — was retired; claim-level retained-ledger protection remains) |
| R11 `_augment_planned_locators` | all modes | yes (locator vocabulary in question AND question-named planned symbol; shadow uses `_unresolved_locator_mapping` exemption) | assisted | PRESERVE_QUESTION_GROUNDED |
| R11 `_augment_required_dataflow_evidence` A (`required_*` claims from required source types) | all modes (internal-filtered) | no (intent + required source types) | yes | MODE_SCOPE: skipped in coverage modes; retained as legacy bridge |
| R11 `_augment_required_dataflow_evidence` B (`dataflow_locator_*` claims from plan symbols) | all modes (internal-filtered) | no | yes | MODE_SCOPE (same function gate) |
| R11 `required_boundary_locators` into the generation prompt | all modes | partially (module_structure intent + boundary concept) | yes (plan symbols) | MODE_SCOPE: empty payload in coverage modes; plan symbols remain a legacy-mode generation hint |

## 3. Coverage-equivalence decisions

**MODE_SCOPE of named-requirement enforcement (R09).** Legacy responsibility:
whole-answer completeness enforced by named requirements (model-returned and
deterministic keyword predicates), independent of answer-point coverage. E1/E2
replacement in coverage modes: question-only E1 answer points → coverage review
validates claim→point mappings and collective completeness
(`missing_answer_point_ids`) → bounded revision driven by missing points.
Ownership-transfer seam tests: `E1E2CompatibilityAuthorityTests`
(`test_coverage_mode_legacy_requirement_is_non_authoritative` — a coverage-complete
answer for which the review still returns a legacy missing requirement passes
with zero legacy failure in `shadow_e1_v2` and `runtime_e1_v2`;
`test_legacy_requirements_are_non_authoritative_in_coverage_modes` in the E2-A1
suite). `test_legacy_default_still_enforces_requirements` proves the
`legacy_question_core` bridge still enforces the same requirement, so nothing
is lost where dynamic points do not exist.

**MODE_SCOPE of plan-driven augmentation and boundary locators (R11).** Legacy
responsibility: plan source types and plan symbols synthesize internal
`required_*`/`dataflow_locator_*` claims and enter the generation prompt as
`required_boundary_locators`. E1/E2 replacement: answer-point coverage defines
mandatory public content; plan suggestions remain retrieval/evidence assistance.
Seam tests: `test_dataflow_augmentation_is_mode_scoped` (no synthesized claims in
coverage modes; legacy bridge still synthesizes) and
`test_boundary_locators_are_mode_scoped` (empty `required_boundary_locators`
payload in coverage modes; plan symbols still injected in legacy mode).

**RETIRE of the E3 second-verify deterministic-requirement view.** Its only
consumer was deterministic requirement enforcement, which is now retired in
coverage modes. Claim-level retained-ledger protection (a new/modified claim
cannot cite ledger-only evidence → `invalid evidence`) is untouched and still
tested.

**PRESERVE_QUESTION_GROUNDED for `_augment_planned_locators`.** It fires only on
explicit locator questions (where/which file/path/defined/implementation) AND a
question-named planned symbol, adds at most one claim backed by already-selected
evidence, and uses the `_unresolved_locator_mapping` exemption in shadow mode.
It is question authority, not a plan suggestion; deleting it would break
legitimate locator questions (T4).

## 4. Final mode matrix

| Surface | legacy_question_core | shadow_e1_v2 | runtime_e1_v2 |
|---|---|---|---|
| named answer requirements | authoritative bridge | context only, non-authoritative | context only, non-authoritative |
| named requirement evidence | authoritative (payload) | context only | context only |
| deterministic missing requirements | enforced | not executed | not executed |
| model `missing_requirement_ids` | enforced | ignored (unknown-id guard kept) | ignored (unknown-id guard kept) |
| planned locator augmentation | active (question-named) | active (question-named, unresolved-mapping exemption) | active (question-named) |
| required dataflow augmentation | active (internal claims) | disabled | disabled |
| required_boundary_locators | plan symbols injected | empty | empty |
| answer-point coverage authority | none (single question_core point) | authoritative | authoritative (E3 seam unchanged) |

## 5. Implementation (`src/panda_agent/qa.py`, +59/−52)

1. `_verify`: deterministic missing-requirement merge and
   known-id acceptance are legacy-mode only; in coverage modes known
   `missing_requirement_ids` from the review are skipped (unknown ids still
   error), so no "missing answer requirement" failure or
   accepted-missing-requirement revision driver exists there.
2. `_verify`: deleted the E3 second-verify deterministic-requirement view
   (`is_e3_second_verify` valid-claim/ledger-evidence projection) whose only
   consumer was the retired coverage-mode enforcement.
3. `_revise`: coverage modes clear `missing_requirement_ids` and the revision
   scope asks only for `missing_answer_point_ids`; legacy mode unchanged.
4. `_augment_required_dataflow_evidence`: returns the draft unchanged in
   coverage modes (plan suggestions never synthesize claims there).
5. `_answer`: `required_boundary_locators` is an empty payload in coverage
   modes; legacy generation hint unchanged.

No prompts.py change was needed (payload keys unchanged). No
question_decomposition.py change. E1 decomposition, E2 mapping/validation
schemas, E3 trigger (`_check_e3_trigger` consumes `missing_points` only), and
retained-support claim-level semantics are untouched.

## 6. Plan-authority audit

Can a plan-only symbol/concept/source suggestion become an independent
mandatory public-answer requirement in `runtime_e1_v2`? **NO.** Deterministic
requirement enforcement does not run there; the review's legacy requirement
field is ignored for known ids; no plan-suggested claim is synthesized;
`required_boundary_locators` is empty. The only residual plan-shaped input in
coverage modes is the requirements/evidence context inside review/revision
payloads, which is informational and cannot by itself produce a failure, a
revision trigger, or public content.

## 7. Preservation and legacy bridge

Preserved: F2-A1/F2-A1-R1 (no support-bypass restoration), F2-A2 pointer
contract (its deterministic check still runs in legacy mode and its tests
pass), citation/version/locator integrity, unsupported-identifier checks,
semantic unsupported-claim review, claim sanitization, internal-claim filtering
(`required_*`/`dataflow_locator_*`/`scope_*` remain non-public), E1
decomposition, E2 mapping/coverage validation, one bounded revision, supported-
claim salvage, E3 trigger and retained-support claim-level semantics, refusal
semantics, retrieval, reranking, evidence selection, normal default, promotion.

Retained legacy bridge (explicitly recorded, not benchmark debt): the entire
named-requirement contract — derivation, evidence selection/compaction, and
enforcement — remains fully active in `legacy_question_core`, which has no
dynamic answer points and is the normal default. This is the bounded
compatibility bridge PF-LR1 anticipated; retirement of the bridge itself would
require default-mode promotion and is out of scope.

## 8. Verification

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **70 passed,
  6 subtests passed** (includes the new `E1E2CompatibilityAuthorityTests` seam
  tests T2/T3/T6/T7).
- `PYTHONPATH=src python -m pytest tests/unit/test_e2_a1_answer_point_coverage.py
  tests/unit/test_e3_missing_point_retrieval.py -q` → **91 passed** (49 focused
  E3 deterministic tests + 42 E2-A1 tests; three E3 and one E2 test were updated
  from asserting coverage-mode named-requirement authority to asserting the
  retired, mode-scoped semantics — the ownership-transfer record).
- Combined focused run: **161 passed, 6 subtests passed**.
- `git diff --check` PASS; diff audit: no changes to retrieval, reranking,
  evidence selection, prompts.py, question_decomposition.py, R04/R01/R14/F3/D4,
  default mode, or promotion.
- PANDA scientific/evaluation calls = 0; PANDA scientific/evaluation tokens = 0.

## 9. Limitations

- The legacy bridge means default-mode behavior is intentionally unchanged;
  equivalence claims are scoped to the coverage modes, where seam tests prove
  the ownership transfer.
- The requirement-derivation vocabulary itself (R08 families) was left
  unchanged; classifying/residual-cleaning individual legacy families beyond
  the mode boundary belongs to the bridge's future owner (default-mode
  promotion or Group C follow-up under separate authorization).
- Review-payload context still contains the legacy requirements in coverage
  modes (informational only).

## 10. Lifecycle closeout

```text
F2-A3  = COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED
F2     = IN_PROGRESS / A1_A2_A3_COMPLETE (F2 still incomplete)
F3     = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A3_COMPLETE
normal default = legacy_question_core (unchanged)
default promotion = DEFERRED (unchanged; promotion relevance != promotion authorization)
```

```text
NEXT_TASK_RECOMMENDATION = F2-A4 — Premise and Refusal Generalization
                           (PF-LR1 Group D / F1 residual R04)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
