# Post-A5 O1 behavior-neutral QA stage observability

Status: **COMPLETE / PASS / O1_BEHAVIOR_NEUTRAL_OBSERVABILITY_IMPLEMENTED_AND_DETERMINISTICALLY_VERIFIED**.
Verification scope is deterministic O1 implementation and applicable regressions,
not scientific model effectiveness. A pre-existing unrelated default-dataset test
failure is disclosed below; it is not reported as a passing test.

Starting/base HEAD: `4ba022c6f466b0f2d274417834315dc6c50de66e`; clean starting tree.
Implementation identity: the single commit containing this report, companion JSON,
two source changes, focused tests and lifecycle updates. Resolve its SHA from Git
history of this report; the final delivery supplies the full commit SHA. No
self-referential commit hash is fabricated in this committed artifact.
Product-behavior lineage remains `e79d3232ed132a224cbceaf3524e19a1406bd648`.

New PANDA scientific/evaluation usage: **0 calls / 0 tokens**. All exercised QA
clients and retrieval paths in O1 tests are deterministic fakes. Fake accounting
values are test data, not scientific usage. No T1 replay/rescore, T2 or Attempt 6.

## Implemented surfaces

- `src/panda_agent/qa.py`: private invocation-local collector and guarded capture
  helpers; private `_run_detailed(..., capture_stage_trace=False)`; QAState carries
  a per-call reference; capture at answer, verification, revision/merge and composer
  seams. Public `run(question)` and `run_detailed(question)` signatures/defaults
  remain unchanged and tracing stays off.
- `src/panda_agent/evaluation_runner.py`: programmatic run option
  `capture_stage_trace=False`, manifest binding, private QA dispatch only on opt-in,
  and preserved resume selection. No CLI or public product parameter was needed.
- `tests/unit/test_post_a5_o1_observability.py`: 33 focused deterministic tests,
  including paired exact payload/role-order comparisons, failure injection and
  existing-store round trips. Existing tests were not rewritten.

No new logging module/store/database. No EA1 resolver, structural backing lookup,
C1 relationship_checks, review-question addition, new refusal policy, RS redesign,
prompt/schema changes, or retrieval/ranking changes were implemented.

## Capture schema and stages

`diagnostics.qa_stage_trace`, schema_version=`qa-stage-trace-v1`:

- capture_status: COMPLETE or INCOMPLETE; optional top-level fixed reason_code for
  a minimal failure envelope; normal envelopes include bounded failure_codes.
- events: ordered records with stage, round, status, reason_code, payload. Status
  is CAPTURED, NOT_EXECUTED or NOT_CAPTURED. Skipped stages use NO_REVISION or
  STAGE_NOT_REACHED, not empty successful output.
- evidence_registry: trace-local exact evidence projections addressed by
  evidence_projection_ref. Same projection reuses a reference; different fields
  or text yield separate projections. Run/case/attempt identity remains in the
  enclosing evaluation record. Array ordinals preserve duplicate claim IDs.

| Stage | Implemented boundary / contents |
| --- | --- |
| EA_ADMISSION | After unchanged claim_evidence filter in A0/A1, before prompt serialization. Ordered selected/admitted/rejected IDs, current missing-locator reason fields, exact selected/offered projections. Round 0=A0, round 1=A1. |
| A0_OUTPUT | Immediately after parsed generation response, before model projection, augmentation or normalization. Raw response and claim ordinals. |
| V1_INPUT / V2_INPUT | Exact serialized reviewer input decoded into an auditable structured equivalent immediately before the existing call; normalized draft and deterministic claim errors separate from model payload. Rounds 1/2. |
| V1_OUTPUT / V2_OUTPUT | Raw parsed response before structural validation/fallback replacement; append ACCEPTED/REJECTED/NOT_APPLICABLE validation status and existing error. |
| A1_INPUT | Actual revision payload before the existing call; no changed missing points, scope, evidence or instructions. |
| A1_OUTPUT | Raw parsed response/ordinals plus post-normalization claims and positional transform mapping, before merge. Current transforms preserve list positions. |
| A1_POST_MERGE | Dispositions captured inside actual branches, supported-prefix input/retained snapshot and prefix dispositions, final ordered merged claims. |
| C_INPUT | Exact ordered composer claims/text and separate existing citation edges; no evidence added to the model input. |
| C_OUTPUT | Parsed composer response/review where available, existing validation/acceptance/fallback diagnostics and `final_answer_ref=result.answer`. Single-claim bypass and failed generation are distinguished in generation_status. |

Merge dispositions: MISSING_ID, IDENTICAL_UNSUPPORTED_REJECTED,
NORMALIZED_DUPLICATE, ID_COLLISION_RENAMED, RETAINED; supported-prefix skips use
OTHER_EXPLICIT_REASON plus actual MISSING_ID/DUPLICATE_ID reason. Each revised
input ordinal records old/new ID, retained flag, comparison target where applicable.
The branch order, normalization, collision suffix algorithm and semantic result
remain unchanged. No after-the-fact inference from final output.

No provider HTTP envelopes, credentials, environment dumps or hidden reasoning.
Existing parsed short reason fields are retained without new model instructions.
Public diagnostic projection remains an explicit allowlist; it does not expose
qa_stage_trace. The public QAResult schema remains unchanged.

## Bounds, failure isolation and persistence

Maximum **16 events / 2,097,152 UTF-8 JSON bytes** including registry. Normal full
one-revision flow requires 12 events, including two EA uses. Structured snapshots
are copied/serialized before admission to the trace. Overflow marks NOT_CAPTURED
with TRACE_SIZE_BOUND_EXCEEDED or records TRACE_EVENT_BOUND_EXCEEDED; no semantic
text is truncated and labeled captured. Final assembly checks the complete envelope
again and substitutes a minimal incomplete envelope if needed.

Copy/serialization/capture/initialization/final-assembly failures are isolated from
the answer path. They cause no retry, routing, revision, model-input or public-output
change. No collector is stored on QAAgent or globally; concurrent same-agent fake
requests have independent collectors/registries. Capture enablement does not alter
graph nodes/edges.

Persist through existing diagnostics -> EvaluationRunStore.record -> append-only
attempts.jsonl/current records/results.jsonl. Round-trip tests verify the same trace
in all three. Existing disk-store failures still propagate; they are not swallowed
as optional capture failures. Provider/parser exceptions that prevent a completed
QA result retain existing exception behavior; O1 does not promise a durable partial
trace on process/model failure. No secondary exception store or historical backfill.

## Runner opt-in and resume

`run_evaluation(..., capture_stage_trace=True)` is the explicit programmatic
development opt-in. New run manifests record true/false. Allowed only for non-formal
draft runs without candidate binding, qa/full mode and dev/challenge/regression
splits. Protected/acceptance/other splits, formal/candidate runs and retrieval-only
capture requests are rejected. No scientific run was invoked by this implementation.

Default execution still calls engine.run_detailed(query). Enabled execution calls
the private seam with the same DEFAULT_ANSWER_POINT_MODE and capture=true.
Resume restores the stored choice; a legacy absent field means disabled and remains
absent, preserving old manifest compatibility. Enabling capture retroactively on a
disabled/legacy run is rejected. No historical manifest is rewritten. Verdicts,
candidate gates and evaluation metrics are unchanged; RS remains deferred.

## RED, GREEN and regression evidence

Commands used `PYTHONPATH=src` (plus tests/unit for the one-off baseline comparison).
The initial invocation without PYTHONPATH failed import collection; this is an
environment setup issue, not RED evidence. A later optional FastAPI import check
could not run because FastAPI was absent; it was replaced by an AST allowlist
boundary check rather than installing unrelated dependencies.

| Verification | Observed result |
| --- | --- |
| Preimplementation O1 tests | RED: 2 failures, both missing `_run_detailed(capture_stage_trace=...)`; default public calls succeeded before the failure. |
| Final `python -m pytest tests/unit/test_post_a5_o1_observability.py -q` | GREEN: 33 passed. |
| Related existing suite: test_qa, test_e2_a1_answer_point_coverage, test_generic_answer_obligation_completeness, test_post_a5_generic_product_repair, test_evaluation_runner, test_f6_release_identity, test_evaluation_cli, two selected M6 store/resume tests | 290 passed, 49 subtests passed; one pre-existing stale default-dataset assertion failed (details below). |
| After supported-prefix instrumentation: test_qa and test_post_a5_generic_product_repair, selected revision/collision/duplicate/resurrection tests | 22 passed, 2 subtests passed, 200 deselected. These overlap the earlier regression count and are not added to it. |
| Starting-source vs final O1 comparison | 6 deterministic scenarios: public result, non-trace diagnostics, fake usage, exact serialized model prompt/schema/system kwargs and call order equal. Covers fallback/success/composer generation failure/review failure/rejection and collision revision. |
| Static source checks | Existing admission predicate, coverage validator, revision routing, claim normalization/identifier stripping, composer validators, retrieval/sufficiency methods and model JSON schemas AST-identical. |
| Unchanged file checks | prompts, D0, models/public DTO, retrieval, storage, evaluation persistence/finalization unchanged under standard Git CRLF/LF normalization and have no tracked diff. |

Known baseline failure, explicitly NOT GREEN:
`EvaluationRunnerTests.test_v26_is_default_and_signed_dry_rescore_preserves_real_failures`
expects v2_6 while both starting and current source select v2_11. Reproduced its
same failing assertion using evaluation_runner loaded from starting Git revision.
It fails before dry rescore; no rescore was executed. This unrelated stale benchmark
default expectation is outside O1 repair scope and is left unchanged. Applicable
O1/QA/runner transport/persistence/identity regressions pass; the broader command
is not described as entirely green.

Pairwise tests compare full result (status/answer/claims/evidence/errors), all
diagnostics except qa_stage_trace, model usage, retriever call count and exact
serialized prompt/schema/system/usage-stage call sequences. Separate generation
and verification clients also preserve role order. Only timing fields are excluded.
Coverage includes no/one revision, ID collision, anti-resurrection, normalized
duplicate, missing ID, repeated raw IDs, structural review fallback, composer
success/bypass/all fallback classes, early exit, capture failures, bounds, registry
identity/copy isolation, run option/resume, public projection and storage failure.

## Prompt, identity, materiality and gates

Before/after canonical fingerprint:
`0a5b2909ef586671d533148979fc681c64e37528ad53781a4566cb9044835ba2`.
Mechanically asserted in O1 tests and directly computed after implementation;
active prompt sources and model schemas are unchanged. Expected value was not edited.

SOURCE_CHANGE=true; MATERIAL_PRODUCT_BEHAVIOR_CHANGE=false;
MATERIAL_PRODUCT_CHANGE=false; PROMPT_FINGERPRINT_CHANGE=false;
PUBLIC_DTO_CHANGE=false; EVALUATOR_CONTRACT_CHANGE=false;
GOLD_CHANGE=false; CALIBRATION_CHANGE=false.

Implementation/repository identity changes in this commit. This is NOT a new
material product candidate; material behavior lineage stays e79d323. Trace-enabled
diagnostics change result/receipt hashes under existing hash semantics, not prompt
or public behavior. No new integrity manifest, candidate freeze or historical hash
regeneration. Ordinary Git identity provides development history.

O1-G1..G10 and O1-G12 PASS within deterministic test/static scope. O1-G11 PASS for
the applicable O1 regression scope, with the independently reproduced unrelated
baseline test failure explicitly excluded and retained as known debt. No claim
that the repository's entire test suite passes. No model effectiveness claim.

## Preserved lifecycle and next boundary

O1 = IMPLEMENTED / DETERMINISTICALLY VERIFIED / BEHAVIOR_NEUTRAL.
EA1 = DESIGN_COMPLETE / NOT_IMPLEMENTED; C1 = DESIGN_COMPLETE / NOT_IMPLEMENTED.
EA1/C1/RS and scientific validation remain unauthorized.

OVERALL_T1_VERDICT=FAIL, historical usage 65 calls / 373,265 tokens. No T1 raw-stage
trace is fabricated and no historical causal uncertainty is retroactively resolved.
g013/g023 FAIL, g047 PASS, g011 negative-existence safety PASS/native-documentation
role coverage FAIL, controls g010/g014/g022/g050 CONTROL_PASS remain unchanged.

novel_validation=PRISTINE_FOR_CURRENT_LINEAGE; holdout access=0;
protected-content leakage=0; F6-B execution=0. No protected content opened.
Candidate frozen=false; Attempt 6 preregistered=false/executed=false;
ATTEMPT_6_READINESS=NOT_READY.

Next recommendation: **POST-A5 EA1 EXACT-BACKING EVIDENCE-ADMISSION IMPLEMENTATION**.
It requires separate authorization and was not executed. No push or historical
amend/squash. Final static checks cover authorized seven-file scope, JSON parsing,
git diff --check, lifecycle consistency and unchanged forbidden/frozen files.

NEXT_TASK_EXECUTION_AUTHORIZED = false
STOP.
