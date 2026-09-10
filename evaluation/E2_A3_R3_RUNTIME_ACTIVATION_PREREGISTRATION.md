# E2-A3-R3: Bounded Runtime Activation Preregistration

## Authority and distinct identities

PRODUCT_CANDIDATE_COMMIT: `fd0aed4c7e491a569bf39271825cc0950630863d`.
This is the completed R2 product, with normal default `legacy_question_core`.
The user explicitly authorizes 28 fresh paired QA executions, 14 blinded
judgments, scientific closeout, and PASS-only selector activation without a
further approval checkpoint. No product repair is authorized in this task.

R3_PROTOCOL_COMMIT is the new commit containing this document, manifest,
readiness record, evaluator, evaluator tests and report draft. Its full SHA is
passed as `--protocol` and recorded in all scientific artifacts. It is distinct
from the product candidate. No scientific or other provider call precedes this
commit. Optional abstract AGY review is dispatched only after protocol freeze;
it receives no repository evidence, case content or scientific outcomes and
cannot edit files or change frozen decisions.

The five PASS-path commits are protocol, all raw, all judgments, scientific
result, then selector-only activation. FAIL/INCONCLUSIVE has only the first four.
No amend/squash across evidence boundaries, no failed-case rerun, no rejudge.

## Scientific question and carried-forward evidence

Does the repaired runtime meet bounded activation non-inferiority versus legacy,
without integrity, support, status, compatibility, runtime-boundary or cost damage?
This is an exposed-development decision, not a generalization confidence claim.
Historical A3 FAIL/Q7 and R1 FAIL/P2_P6 remain unchanged. R2 PASS is preserved.
P6 has no waiver and no product repair. E1 decomposition, E2 mapping and missing
point validation, A3 retrieval bootstrap and unaffected gates, FR1/R1 normalizer
evidence, and R2 144=106+38 reconciliation plus six fresh repair pairs are
carried-forward compatible historical evidence, not fresh R3 measurements.

No retrieval-only bootstrap is repeated: retrieval implementation/index/corpus
did not change in R1/R2/R3. Each fresh QA arm still performs independent normal
retrieval. Existing sufficiency-stage retrieval remains ordinary product behavior;
post-verification missing-point retrieval is forbidden. No E3 behavior is added.

## Cohort selection fixed before provider calls

Use the approved v2.6 benchmark and its reviewed effective-English dev language
calibration, using established compatibility and language-input identity checks.
Only approved English dev records are selection candidates. No novel dataset,
protected/holdout path or unapproved question is used. Existing benchmark risk
labels are historical metadata, not protected external holdout membership.
No historical quality outcome is loaded or used by selection.

There are 59 approved English dev candidates. Exclude exactly g013, g027, g112,
g002, g044, g110. The resulting pool has 53 records: 43 answered, 10 nonanswered.
Within each status partition, group by intent; sort intent names ascending and
IDs ascending within each intent; round-robin until exhausted. Take the first
10 answered and first four nonanswered. Fill a shortage from remaining answered
then remaining nonanswered in the same round-robin order. Final order is the
answered selection followed by nonanswered selection, then any shortage fill.
The manifest persists full round-robin accounting and exact approved references.

| Index | ID | Intent | Expected status |
| --- | --- | --- | --- |
| 0 | g059 | algorithm_implementation | answered |
| 1 | g047 | algorithm_theory | answered |
| 2 | g028 | api | answered |
| 3 | g001 | installation | answered |
| 4 | g105 | module_structure | answered |
| 5 | g113 | troubleshooting | answered |
| 6 | g014 | usage | answered |
| 7 | g060 | algorithm_implementation | answered |
| 8 | g050 | algorithm_theory | answered |
| 9 | g029 | api | answered |
| 10 | g057 | algorithm_theory | insufficient_evidence |
| 11 | g041 | api | insufficient_evidence |
| 12 | g007 | installation | insufficient_evidence |
| 13 | g108 | module_structure | version_conflict |

Exactly 14 unique questions, 10 answered and four nonanswered. Intent counts:
algorithm_implementation 2, algorithm_theory 3, api 3, installation 2,
module_structure 2, troubleshooting 1, usage 1. No R2 case is reused.

## Provider and execution protocol

Exact settings are frozen in the manifest: current configured generation and
judge gemini-3.8-flash, global location, embedding gemini-embedding-2/3072,
120000 ms timeout. Judge temperature zero; production generation parameters
and existing adapter behavior unchanged. Provider settings must match at every
phase; observed attempts/responses/tokens are counted separately.

Each case gets a fresh agent for legacy_question_core and runtime_e1_v2. Even
indices execute legacy then runtime; odd indices runtime then legacy. The same
mapping assigns A/B: even A legacy/B runtime, odd A runtime/B legacy.
Persist STARTED before each execution and COMPLETE after each attempt, including
exceptions. A persisted ambiguous STARTED record is never silently replayed.
Canonical JSON comparison prevents tuple/list representation differences.

Capture case/order/question/status expectation, public answer/claims/citations,
selected evidence and retrieval diagnostics, all reviews/errors, revision count,
runtime decomposition/coverage/missing points, timings, model event usage, raw
answer/revision responses and evaluator-only admission IDs. No public DTO change.
No intermediate outcome inspection, adaptive case replacement or repair.

After all 28 attempts, verify identities and commit raw before any judge call.
Run one strict blinded judgment per case only with a valid complete raw pair.
No failed-provider replay to manufacture a scoreable pair. Persist failed
judgment attempts as evidence; missing/malformed judgment prevents authority.
Commit all judgment records before unblinding/scoring, including failures if any.

Judge uses the unchanged A3 strict schema/prompt, also frozen in the manifest:
preferred A/B/equivalent, critical_regression boolean, A_supported/B_supported
booleans, and nonempty short reason. Extra fields are rejected; critical
equivalent is invalid. Input is only question, approved expected status/Gold
obligations, and A/B public status/answer/claims with cited evidence. No mode
names, decomposition, coverage audit, repair history or activation hypothesis.

## Readiness F1-F10

| Gate | Requirement |
| --- | --- |
| F1 | Exact R2 product candidate identity verified |
| F2 | No src/config/prompt/schema/corpus/index product delta |
| F3 | Deterministic 14 unique approved English dev cohort excludes R2 six |
| F4 | Exact provider settings fixed |
| F5 | Strict judge schema/prompt and G1-G13 fixed |
| F6 | Normal default legacy before verdict |
| F7 | R1 normalizer and R2 admission unchanged |
| F8 | Focused evaluator/static tests pass |
| F9 | Protected/holdout access zero |
| F10 | Scientific/provider calls before protocol freeze zero |

All must pass before live execution, otherwise BLOCKED /
PREREGISTRATION_OR_CANDIDATE_INTEGRITY_FAILURE. Product identity is checked by
Git ancestry/diff; the full current product matches the R2 candidate. Freeze
product, config, prompts, schemas, tests, Gold/calibration, runner and imported
helpers, manifest, readiness and preregistration until verdict. No product or
gate/cohort/provider edits are allowed after exposure.

## Activation gates G1-G13

| Gate | Frozen requirement |
| --- | --- |
| G1 | 14 complete valid legacy + 14 runtime; 14 authoritative judgments |
| G2 | Runtime expected-status correct >= legacy correct |
| G3 | No new runtime answered outcome on expected nonanswered cases relative to legacy |
| G4 | No new runtime refusal/nonanswer on expected answered cases relative to legacy |
| G5 | Per-case all-review runtime-minus-legacy critical verifier category set empty |
| G6 | Both arms: no public raw answer/revision claim cites ineligible Sphinx; no incomplete-web review errors; captured primary/auxiliary admission IDs match eligible projection |
| G7 | All runtime cases exactly one valid decomposition with 1..5 sequential nonempty point.N obligations; expected-and-final answered cases have evaluable/complete coverage and no unknown-point or structural review errors |
| G8 | Legacy decomposition zero; runtime revisions <=1; post-verify retrieval zero |
| G9 | All 14 runtime outputs supported by authoritative judge, even equivalent pairs |
| G10 | Critical runtime user-visible regressions zero after A/B mapping |
| G11 | Runtime worse <=1/14 and better+equivalent >=13/14 |
| G12 | Sum(runtime-legacy generation adapter calls)/14 <=2.0; exclude embeddings and retrieval |
| G13 | Public DTO/API, compatibility requirements, retrieval/corpus/index, normalizer, citation contract unchanged; default legacy before verdict |

G5 categories include wrong_version, unknown_evidence, incomplete_citation,
unsupported_identifier, structural_review and unknown_answer_point. Every review
counts, including errors later repaired. G7 permits false coverage_evaluable on
correct refusals; refusal coverage is diagnostic rather than automatically failing.
Critical means the nonpreferred output has severe damage under the frozen judge.
Unsupported runtime is independently failing irrespective of preference.

G11 preserves the original A3 tolerance rate: 2/28 = 1/14, approximately 7.14%.
Its basis is the original activation contract, not exposed g002. Ties are
equivalent, not wins. This bounded threshold has no statistical-confidence
interpretation and cannot waive any critical/support/status/integrity gate.
Latency median/p95 is diagnostic only.

The evaluator reuses established R1 numerical status/integrity/boundary accounting
and R2 admission capture, discarding their gate/sentinel decisions. R3 applies
only the above gates. Public DTO validation, accepted unknown point IDs, internal
claims receiving public coverage credit, and post-verify retrieval are explicit
zero-tolerance checks. All frozen file and authorization boundaries also apply.

## Verdict, activation and stop

PASS requires all readiness/activation gates, all authoritative evidence and no
zero-tolerance violation. Complete scoreable product failure is FAIL; do not
repair or rerun. Genuine provider/judge failure, ambiguous STARTED or corrupt
artifacts causing missing authority is INCONCLUSIVE. Observed product contract
violations remain FAIL. Persist scientific result/report/lifecycle in their own
commit before activation. Historical A3/R1 FAIL and R2 PASS remain untouched.

Only a committed PASS authorizes changing DEFAULT_ANSWER_POINT_MODE from legacy
to runtime_e1_v2. The only post-result product commit changes that selector,
directly necessary focused tests and lifecycle docs. Fake/static tests must
prove run/run_detailed default runtime, exactly one decomposition, point.N IDs,
internal-only audit, explicit legacy and shadow availability, <=1 revision,
no missing-point retrieval, active citation/normalizer repairs, compatibility
and public DTO preservation. No live calls after activation. If additional
semantics would be necessary, stop rather than hide a repair in activation.

PASS activation closes E2 as SEMANTIC_ANSWER_POINT_COVERAGE_RUNTIME_ACTIVATED;
Phase E becomes IN_PROGRESS/E2_COMPLETE/E3_NEXT. E3 remains NOT_STARTED and
not authorized. FAIL/INCONCLUSIVE keeps legacy and creates no activation commit;
the next review requires separate authorization. No E3/T3/T5/D4/F2/F3 or legacy
requirement retirement. Report separate legacy/runtime/judge logical operations,
returned responses, adapter attempts and observable tokens; embedding tokens
and monetary cost unavailable. STOP after the bounded R3 closeout.
