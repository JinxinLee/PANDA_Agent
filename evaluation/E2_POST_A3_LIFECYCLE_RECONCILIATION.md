# E2-LR1 — Post-A3 Lifecycle Simplification and Roadmap Reconciliation

Documentation reconciliation: COMPLETE / PASS. Starting HEAD:
`fa8b8b6c1195019ed152ad08da2f63b6720ecc96` (clean).

## Decision

Three separate questions now govern E2 planning: mechanism implemented: yes;
targeted evidence sufficient to continue architecture development: yes;
acceptance for normal production default: no. Therefore E2 is COMPLETE /
CORE_MECHANISM_VALIDATED / DEFAULT_PROMOTION_DEFERRED, not scientific PASS.
The user-authorized lifecycle decision stops the immediate A3 activation loop;
it does not change an experiment or assert release/generalization acceptance.

## Preserved evidence

E1, E2-A1 and E2-A2 are COMPLETE / PASS. Existing mechanisms include semantic
decomposition, claim-to-point mapping, missing-point detection,
coverage_evaluable/coverage_complete semantics, bounded one-revision behavior,
and explicit runtime_e1_v2 execution. E2-A3-R2 is COMPLETE / PASS /
CITATION_ELIGIBLE_EVIDENCE_SELECTION_REPAIR_VALIDATED. Accepted trailing-colon
identifier normalization and citation-eligible Sphinx admission remain in place.

The bounded R3-R1 combined development evidence records correct statuses and
supported runtime outputs, zero critical runtime regressions/new critical verifier
categories, valid decomposition, complete applicable semantic coverage, bounded
revision and no post-verify E3 retrieval. These observations are not full Gold
completeness, release or generalization guarantees; the G11 review's g001 scope
omission and sanitizer finding remain recorded.

Immutable outcomes:

- E2-A3 = COMPLETE / FAIL / Q7.
- E2-A3-R1 = COMPLETE / FAIL / P2_P6.
- E2-A3-R2 = COMPLETE / PASS / CITATION_ELIGIBLE_EVIDENCE_SELECTION_REPAIR_VALIDATED.
- E2-A3-R3 = COMPLETE / INCONCLUSIVE / CONNECTION_TIMEOUT_AND_PROVIDER_429_INCOMPLETE_PAIRS.
- E2-A3-R3-R1 = COMPLETE / FAIL / G11; quality 1 better / 11 equivalent / 2 worse.
- E2-A3-R3-R1 G11 FAILURE REVIEW = COMPLETE / PASS / PRODUCT_REPAIR_AND_GATE_REDESIGN_RECOMMENDED.

The historical gate was correctly applied. No rescore or waiver is granted.
Reports and frozen raw/judged/result artifacts remain unchanged.

## Maintenance and promotion are separate

The shared pre-existing `_strip_nonessential_external_identifiers` bug can leave
`an internal support type<Type>` after partial template-head replacement. It is
ordinary QA maintenance affecting either mode depending on generated syntax,
not an E2 semantic-runtime-specific defect. QA-M1 — Generic Claim Sanitization
Repair covers a small generic fix, focused T0 and frozen/static impact scan,
without an activation decision. QA-M1 blocks neither E2 completion nor E3
architecturally. No repair is performed here.

The G11 review's proposed immediate combined E2-A3-R4 is NOT_STARTED /
SUPERSEDED_BY_LIFECYCLE_SIMPLIFICATION, not failed or cancelled. Its historical
recommendation is retained but superseded by this later roadmap decision.
Default promotion will be reconsidered only after a materially broader Phase-E
candidate, naturally after E3 or another explicit Phase-E completion decision.
Gate redesign is deferred to that boundary. The prior 28-question/two-judge/
material_noncritical_regression ideas and any new worse threshold are not active
gates; no future experiment is defined or frozen now.

## Architecture and production boundary

runtime_e1_v2 is a VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY, not
production-ready or release accepted. Explicit development/evaluation use still
requires the corresponding task and scientific-call authorization.
E3 is NOT_STARTED / ARCHITECTURALLY_UNBLOCKED: its future implementation can use
E1 points and E2 missing-point detection through explicit runtime or appropriate
internal experimental/shadow execution without first promoting the default.
Normal legacy QA retains existing retrieval behavior. Missing-point retrieval
must not silently enter ordinary production QA before a later explicit promotion
decision. This reconciliation adds no mode, code or retrieval behavior.

## Current planning state

```text
E2-LR1 = COMPLETE / PASS / POST_A3_LIFECYCLE_RECONCILED
E2-A3-R4 = NOT_STARTED / SUPERSEDED_BY_LIFECYCLE_SIMPLIFICATION
E2 = COMPLETE / CORE_MECHANISM_VALIDATED / DEFAULT_PROMOTION_DEFERRED
E2 DEFAULT PROMOTION = DEFERRED / ACTIVATION_ACCEPTANCE_NOT_MET
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
Normal default = legacy_question_core
E2 DEFAULT-PROMOTION GATE REDESIGN = DEFERRED / REVISIT_AT_PHASE_E_PROMOTION_BOUNDARY
Phase E = IN_PROGRESS / E2_CORE_COMPLETE / E3_NEXT
E3 = NOT_STARTED / ARCHITECTURALLY_UNBLOCKED
NEXT_TASK_RECOMMENDATION = QA-M1 — Generic Claim Sanitization Repair
NEXT_TASK_EXECUTION_AUTHORIZED = false
FOLLOWING_ARCHITECTURE_TASK = E3 — Missing-Point Targeted Retrieval
```

Recommended order is QA-M1 maintenance then E3 architecture, without reopening
E2. Neither task is executed or authorized by this reconciliation.
Only status, roadmap and this record change. Evaluation policy is unchanged;
its immutable-result, proportional-evaluation and authorization rules do not
conflict with separating lifecycle completion from default acceptance.
Offline checks cover historical labels, consistent planning state, unchanged
product/default and historical records, and git diff --check. QA, judge,
retrieval, embedding, provider calls and scientific tokens are all zero.
No AGY provider invocation, full suite, evaluator framework or new hashes.
One ordinary reconciliation commit, then stop.
