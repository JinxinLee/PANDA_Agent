# POST-A5 C1 Bounded Coverage-Completeness Implementation

**PASS** for deterministic C1 implementation and safety gates.

C1 = IMPLEMENTED / DETERMINISTICALLY VERIFIED / MATERIAL PRODUCT CHANGE / SCIENTIFIC EFFECT NOT YET EVALUATED.

## Identity and delivery

- Starting HEAD: `006bcbe226a99fb722b2b5f300b27da84a9e7607`; clean at start.
- C1 implementation commit: `5e0a3a3ae4828ea3b5831646e3d5d2c8f08cc9ed`.
- Final verified implementation HEAD at record creation: `5e0a3a3ae4828ea3b5831646e3d5d2c8f08cc9ed`.
- Previous behavior lineage (EA1): `60dff40a671e62bffcbe0eb82d38ea6e9aeb05c4`.
- Current behavior lineage: `5e0a3a3ae4828ea3b5831646e3d5d2c8f08cc9ed`.
- A documentation-only child commit closes this record and lifecycle docs. Its actual repository HEAD is reported in the final delivery; it is not the behavior head. The record cannot embed its containing commit's own SHA.
- No historical commit amended; no push.

Changed files:
- `src/panda_agent/qa.py`
- `src/panda_agent/prompts.py`
- `src/panda_agent/evaluation_runner.py`
- `tests/unit/test_post_a5_c1_coverage_completeness.py`
- `tests/unit/test_qa.py`
- `tests/unit/test_e2_a1_answer_point_coverage.py`
- `tests/unit/test_post_a5_o1_observability.py`
- `evaluation/POST_A5_C1_BOUNDED_COVERAGE_COMPLETENESS_IMPLEMENTATION.md`
- `evaluation/post_a5_c1_bounded_coverage_completeness_implementation.json`
- `docs/EVALUATION_STATUS.md`
- `docs/GENERALIZATION_ROADMAP.md`

## Production isolation and contract

Only `production_answer_obligations_v1` selects the new schema/prompts through
`_coverage_satisfaction_enabled`. Historical shadow/runtime/legacy semantics
remain available. D0 stays question-only and unchanged.

Private schema identity: `coverage-satisfaction-v1`. Existing eight top-level
review fields remain. All keys below are required; extras are forbidden:

- Point: `answer_point_id, supporting_claim_ids, complete, scope_status, relationship_checks`.
- Check: `relationship_text, necessity_reason, basis, supporting_claim_ids, satisfied, admission_state`.
- Basis: `evidence_id, quote`.
- Check identity: point ID plus ordinal, no separate relationship ID.
- Scope: `ESTABLISHED`, `INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE`, `OVERFLOW`.
- Admission: `ADMITTED_BACKING_AVAILABLE`, `VISIBLE_ONLY_WITHOUT_CITABLE_BACKING`, `INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE`.

| Bound | Implemented maximum |
| --- | --- |
| Checks per point / question | 4 / 20 |
| Distinct basis IDs and quotes per check | 2, one exact quote per ID |
| Total quotes | 40 |
| Supporter IDs per check / point | 8 / 32 |
| Relationship text | 1-240 characters |
| Necessity reason | 1-160 characters |
| Quote | 1-400 characters |
| Revision | 1 |
| Eligible unsupported repair IDs | 8, in reviewable order |

Declared semantic OVERFLOW is incomplete and non-revisionable. Literal violations
are invalid, never truncated into a valid complete judgment.

Production V1/V2 receives the raw untrusted question, exact EA admitted IDs and
private schema version alongside the existing points, claims and broader evidence.
The prompt requires both question relevance and evidence grounding for necessity,
not every available fact or claim-derived scope. Direct factual/location/definition
assertions are valid checks; no artificial binary relation is required. Gold,
case IDs, expected answers, external judge output and external knowledge have no
authority. Existing untrusted-data security remains.

## Validation, recovery and output

Exact fields/types/enums, one record per known point, known unique IDs, exact nonempty quotes in real review evidence, unique basis IDs, fixed bounds, whitespace-only duplicate relationship rejection, admitted-state consistency, supporter support/relevance/mapping/citations, ordered point supporter union and complete/missing complement. Semantic necessity/entailment/completeness remain model judgments.

Only validated ESTABLISHED + ADMITTED_BACKING_AVAILABLE + unsatisfied checks create recovery relationships. Eligible unsupported claims must have passed existing deterministic checks and cite admitted evidence. Invalid review is non-revisionable and unevaluable; visible-only, uncertain or overflow scope itself cannot trigger revision.

A1 receives only structured recovery relationships, their points, eligible unsupported claims, and the union of admitted basis/cited evidence. Blocked errors and other incomplete points are excluded. At most 8 eligible unsupported repair IDs, in reviewable order. All prior unsupported text still participates in anti-resurrection rejection, including non-repairable claims. No EA re-resolution/retrieval.

Production coverage_blocked prevents salvageable ANSWERED. Preserve independently supported relevant claims and actual citations, deterministic render plus fixed limitation notice, no composer. Invalid relationship structure may retain separately structurally valid positive support/mapping judgments; no fake valid relationship scope is generated. Unusable support judgments yield no claims. Existing hard guards precede this path.

Fixed system limitation notice (not a factual citation edge):

> The available citable evidence does not establish a complete answer to this request.

Complete answers retain the existing composer path. The seven-stage maximum is
D0/A0/V1/A1/V2/composer/composer review, with no new model stage, semantic retrieval,
embedding or E3 path. New completeness judgments can activate the existing single
A1; identical production usage on future real questions is not claimed.

Private audit records preserve scope/checks/admission reasons, recovery sets,
schema version and evaluability. Blocked counts are derivable from those records.
O1 captures actual inputs/raw outputs and validation failures. Invalid coverage is
not represented as fake valid relationship checks. Independently valid support
judgments can preserve partial claims, but cannot make coverage evaluable or invoke
A1. Public DTO and API diagnostic allowlist are unchanged.

## RED, GREEN and focused regressions

All execution used deterministic local fake clients; scientific cost **0 calls /
0 tokens**. Synthetic fake usage counters are not real scientific usage.

- RED before implementation: two failures: missing schema-version constant; old
  error-driven routing returned `revise` for non-revisionable invalid scope.
- Final C1 GREEN: **69 passed** in
  `tests/unit/test_post_a5_c1_coverage_completeness.py`.
- Focused existing regressions: **421 passed + 49 subtests passed**; includes
  **33 O1** and **52 EA1** cases. One unrelated baseline failure remains.
- Combined batch with the then-66 C1 tests: **487 passed, 49 subtests passed,
  1 baseline failure**. Three added C1 cases were subsequently covered by the
  full 69-case C1 run; counts are not summed as separate executions.
- Focused existing files: `test_qa.py`, `test_e2_a1_answer_point_coverage.py`, `test_generic_answer_obligation_completeness.py`, `test_post_a5_generic_product_repair.py`, `test_post_a5_o1_observability.py`, `test_post_a5_ea1_exact_backing.py`, `test_evaluation_runner.py`, `test_f6_release_identity.py`, `test_e3_missing_point_retrieval.py`.
- One mistyped pytest filename ran no tests; corrected immediately.
- Baseline failure:
  `test_evaluation_runner.py::EvaluationRunnerTests::test_v26_is_default_and_signed_dry_rescore_preserves_real_failures`.
  Starting-HEAD runner loaded in-process reproduces the same v2_6 expectation
  versus existing v2_11 default. No reset, Gold change or opportunistic repair.
- Production test doubles were updated to emit explicit new records when the
  production private version is present. Historical fake responses remain
  untouched. New C1 cases directly author their relationship judgments; test
  fixtures do not establish semantic effectiveness.

### Required T0 map

| Gate | Deterministic evidence |
| --- | --- |
| T0-A | production schema selector and historical mode payload tests; existing explicit legacy tests |
| T0-B | test_complete_composer_and_production_payload; mixed V1/V2 trace payloads |
| T0-C | test_complete_scope_and_optional_fact_omission; supporter/string boundary acceptance |
| T0-D | test_generic_relationship_shapes_and_topical_gap; recovered-complete flow |
| T0-E | test_generic_relationship_shapes_and_topical_gap |
| T0-F | test_visible_only_gap_alone_never_invokes_revision |
| T0-G | test_declared_blocked_scope_no_revision |
| T0-H | test_complete_scope_and_optional_fact_omission |
| T0-I | test_structural_rejection; twenty/twenty-one checks; supporter and string boundaries |
| T0-J | test_structural_rejection quote variants |
| T0-K | test_structural_rejection admission variants; mixed-scope flow |
| T0-L | test_structural_rejection supporter variants |
| T0-M | test_structural_rejection point_union and union_order |
| T0-N | test_structural_rejection missing_complement |
| T0-O | test_structural_rejection duplicate_text |
| T0-P | test_invalid_review_preserves_independent_claims_no_retry; empty invalid review |
| T0-Q | test_mixed_scope_revision_then_partial_and_trace_neutrality |
| T0-R | mixed-scope and unsupported-claim recovery tests |
| T0-S | test_unsupported_claim_recovery_requires_safe_admitted_citations |
| T0-T | mixed-scope and recovered-complete maximum-one-revision tests |
| T0-U | test_mixed_scope_revision_then_partial_and_trace_neutrality |
| T0-V | declared-blocked and mixed-scope partial rendering tests |
| T0-W | test_empty_invalid_review_no_placeholder |
| T0-X | test_hard_guard_precedes_c1_partial_policy; existing QA and negative-existence regressions |
| T0-Y | test_complete_composer_and_production_payload; recovered-complete flow |
| T0-Z | mixed OFF/ON parity; raw invalid review; existing 33 O1 tests |
| T0-AA | 52 EA1 tests unchanged; resolver/predicate AST equality |
| T0-AB | test_recovered_complete_path_keeps_seven_call_ceiling; one retrieval and zero fake embeddings |
| T0-AC | test_fingerprint_binds_production_prompts_schema_and_version |
| T0-AD | test_historical_mode_payload_schema; existing shadow/runtime/E3 and legacy tests |

C1-G1 through C1-G20: PASS within the stated deterministic scope. The isolated
obsolete test is not represented as passing.

## Preservation and fingerprint

AST equality against starting HEAD confirms the unchanged strict citation
predicate, EA1 resolver/backing validator/evidence lookup, historical coverage
validator, active runtime-point helper and composer function. Historical coverage,
security, answer and composer prompt values are unchanged. D0, retrieval, storage,
public models and evaluator files are unchanged. Source diff in evaluation_runner
is limited to fingerprint imports/registration.

Prompt-set version: **3.10.1 -> 3.11.0**.

- Old fingerprint: `0a5b2909ef586671d533148979fc681c64e37528ad53781a4566cb9044835ba2`
- New fingerprint: `03e1bf270898b28127a42fa2e1ccb24cfc1d87e177eeba5428ba4680d426352c`

Repeated calculation is deterministic. Mutation tests confirm the fingerprint binds
both new production prompts, the private schema version and JSON schema while
retaining historical components.

O1 remains IMPLEMENTED / DETERMINISTICALLY VERIFIED / BEHAVIOR_NEUTRAL.
EA1 remains IMPLEMENTED / DETERMINISTICALLY VERIFIED / MATERIAL PRODUCT CHANGE /
SCIENTIFIC EFFECT NOT YET EVALUATED. Selected bundle, rankings and retrieval trace
remain governed by unchanged EA1/retrieval behavior; its focused tests pass.

## Materiality and lifecycle

SOURCE_CHANGE = true
MATERIAL_PRODUCT_BEHAVIOR_CHANGE = true
MATERIAL_PRODUCT_CHANGE = true
PROMPT_SCHEMA_CONTRACT_CHANGE = true
PROMPT_FINGERPRINT_CHANGE = true

PUBLIC_DTO_CHANGE = false
EVALUATOR_CONTRACT_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
RETRIEVAL_POLICY_CHANGE = false
EA1_CONTRACT_CHANGE = false
D0_CHANGE = false

Historical T1 remains **COMPLETE / FAIL**, **65 calls / 373,265 tokens**. It ran the
pre-EA1/pre-C1 product; no replay, rescoring, or backfill was performed.

novel_validation = PRISTINE_FOR_CURRENT_LINEAGE; holdout access = 0;
protected-content leakage = 0; F6-B execution = 0. Protected content was not accessed.

Candidate frozen = false; Attempt 6 preregistered = false; Attempt 6 executed = false;
ATTEMPT_6_READINESS = NOT_READY. RS remains deferred; E3 is not promoted.

## Limitations and next recommendation

- Fake tests certify mechanics/enforcement, not live semantic necessity, entailment or omission detection.
- Exact quotes and ID/citation checks cannot prove that a relationship is necessary or that a claim entails it.
- Conservative scope bounds/partial rendering may increase abstention and token cost; neither runtime effectiveness nor token cost was scientifically measured.
- One independently reproduced stale baseline test remains failing.
- Provider/network/transport behavior was not exercised; existing transport failure/retry policy is unchanged.
- No g013/g023 fixes claimed; no scientific replay, candidate freeze, RS redesign, E3 promotion or subsequent integration closeout performed.

NEXT_TASK_RECOMMENDATION = POST-A5 O1+EA1+C1 DETERMINISTIC INTEGRATION CLOSEOUT
NEXT_TASK_EXECUTION_AUTHORIZED = false
