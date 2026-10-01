# G5 Minimal Failed-QA Observability Repair Design

## 1. Status, authority and scope

**PASS / DESIGN COMPLETE / IMPLEMENTATION_READY.** This freezes a documentation-only design, including the record schema, exception transport, bounds and deterministic fake acceptance matrix. It does not implement or verify the repair.

Entry is clean `main` at `69389cbed763052570b1d233f79bb68a8d84ea45`, message `Diagnose targeted provider 429 blocker`. Product behavior lineage remains `5b9588ec552deb91a59a8176d6ce0429c2133b1e`. Delivery is the commit `Design failed-QA observability repair`; resolve its exact SHA from Git history and the delivery report. No push.

Authorities inspected: [bounded diagnosis](G5_TARGETED_PROVIDER_429_BLOCKER_DIAGNOSIS.md), [targeted execution](G5_POST_V1_REPAIR_TARGETED_LIVE_VERIFICATION.md), [corrected targeted design](G5_POST_V1_REPAIR_TARGETED_LIVE_VERIFICATION_DESIGN.md), current status/roadmap, and relevant `qa.py`, `evaluation_runner.py`, `evaluation.py`, `evaluation_finalization.py`, `llm/vertex.py` and question-decomposition source. Existing O1 and recovery tests were read only. [O1 implementation](POST_A5_O1_BEHAVIOR_NEUTRAL_OBSERVABILITY_IMPLEMENTATION.md) supplies the existing trace contract and a precedent for retaining product lineage after an evaluation-only observability implementation.

Authorization is DESIGN / REVIEW / DOCUMENTATION and commit only. No source, test, prompt, schema, configuration, dependency, dataset or raw-run artifact changes; no tests, live invocation, health check, provider probe, retry, resume, new scientific run or protected access.

## 2. Confirmed blocker and scientific distinction

The frozen diagnosis is `COMPLETE / PASS / BOTH_PROVIDER_AND_OBSERVABILITY_BLOCKERS`. Its provider subtype is `PROVIDER_RESOURCE_EXHAUSTED_SUBTYPE_UNRESOLVED`; its failed-QA persistence blind spot is CONFIRMED. All six historical targeted cases failed before A0/V1, with `TARGETED_V1_PROVIDER_STAGE = CONFIRMED_NOT_REACHED`.

**Current missing V1 is caused by pre-A0/V1 provider failure. No completed V1 was lost in that batch.** The separate blind spot is that an escaping detailed-QA exception prevents export of invocation-local state; a future later failure could erase a previously observed V1 proof from the record. Neither better capture nor this design establishes provider availability or a resource subtype.

## 3. Objective and selected repair

```text
SELECTED_DIRECTION = FAILURE_BOUNDARY_PARTIAL_DIAGNOSTICS_EXPORT
SELECTED_REPAIR = CAPTURE_SCOPED_FAILURE_BOUNDARY_PARTIAL_DIAGNOSTICS_EXPORT
```

When `_run_detailed(..., capture_stage_trace=True)` raises an ordinary `Exception`, preserve already-existing bounded parsed state through the existing runner/store path, keeping the case failed. Do not recreate missing state, call D1 twice, retry a model, replay a stage or change an answer decision.

The minimum sufficient mechanism is: existing `_QAStageTrace` failure snapshot + available canonical decomposition + one dedicated exception transport + the current runner exception-record branch. It addresses caught escaping exceptions. It does not promise survival of process termination, cancellation, power loss or disk-write failure.

## 4. Alternatives and proportionality

| Candidate | Decision / reason |
|---|---|
| Failure-boundary export through existing records | SELECTED: state already exists inside QA; the runner already owns durable case records. |
| LangGraph checkpointing, per-event writes, new database or generic telemetry | REJECTED: adds execution/storage machinery for a caught-exception export problem; crash recovery is outside the objective. |
| Attach attributes to arbitrary original exceptions | REJECTED: exception classes need not permit mutation; creates implicit contracts and risks altering provider/product objects. |
| Return a failure object from detailed QA | REJECTED: changes successful-return semantics and could flow into QAResult validation or scoring. |
| Marker-only failure receipt | INSUFFICIENT: cannot retain substantive prior V1 input/output/proof evidence. |
| Enrich VertexCallError | NOT SELECTED: existing original error, preserved parsed trace and available usage counters close this state-loss problem. Provider subtype/precise operation history may remain unknown. No adapter redesign or new role/stage instrumentation is required. |
| No repair | INSUFFICIENT: retains demonstrated loss on escaping late exceptions. |

## 5. Architecture and ownership

```text
_run_detailed(capture_stage_trace=True)
  existing local decomposition + existing _QAStageTrace
  -> ordinary Exception
  -> bounded JSON-safe failure envelope
  -> QADetailedExecutionError(original_exception, failure_diagnostics)
  -> existing run_evaluation except branch
  -> original exception serialization + optional failure_diagnostics
  -> existing usage accounting + EvaluationRunStore.record
```

| Owner | Frozen responsibility |
|---|---|
| `qa.py` | Own the invocation-local collector/decomposition, bounded failure snapshot/envelope and dedicated wrapper. No file I/O. |
| `evaluation_runner.py` | Recognize only this wrapper, classify/serialize its original exception, optionally attach safe failure diagnostics, then use unchanged duration/usage/store flow. |
| `evaluation.py` | Existing store writes arbitrary JSON record fields to attempts, canonical records and results. No modification needed. |
| `evaluation_finalization.py` | Existing classification and exception-first cohort/recovery semantics. No modification needed. |

The wrapper travels through `_execute_evaluation_case` without a normal tuple return. No new callback, parallel trace model, shared-agent last-error field or external sidecar is introduced. Invocation ownership prevents concurrent calls from sharing mutable failure state.

## 6. Frozen failure envelope and record schema

The only new durable top-level key is optional `record["failure_diagnostics"]`. Its schema is the internal additive `qa-failure-diagnostics-v1`, independent of model/provider schemas and public QAResult. This document defines a future contract; no existing schema file changes now.

The envelope has exactly these five keys:

| Field | Contract |
|---|---|
| `schema_version` | Constant `qa-failure-diagnostics-v1`. |
| `capture_status` | Constant `INCOMPLETE`; never COMPLETE for an escaping invocation. |
| `failure_codes` | Unique fixed codes, at most 8; always includes `QA_EXECUTION_FAILED`. No dynamic exception messages. |
| `question_decomposition` | Exact JSON-safe copy of successfully available canonical decomposition within its export byte cap, otherwise null. |
| `qa_stage_trace` | Existing `qa-stage-trace-v1` failure snapshot or its existing minimal incomplete form; never a successful finished trace. |

Allowed envelope codes are `QA_EXECUTION_FAILED`, `DECOMPOSITION_UNAVAILABLE`, `DECOMPOSITION_NOT_APPLICABLE`, `DECOMPOSITION_SIZE_BOUND_EXCEEDED`, `DECOMPOSITION_COPY_FAILED`, `TRACE_SNAPSHOT_FAILED`, and `TRACE_COLLECTOR_UNAVAILABLE`. One decomposition-unavailability reason is selected, rather than contradictory codes. Trace-specific initialization/size reasons also remain in the nested trace's existing reason/failure fields.

Illustrative D1-failure payload (not a new run artifact):

```json
{
  "schema_version": "qa-failure-diagnostics-v1",
  "capture_status": "INCOMPLETE",
  "failure_codes": ["QA_EXECUTION_FAILED", "DECOMPOSITION_UNAVAILABLE"],
  "question_decomposition": null,
  "qa_stage_trace": {
    "schema_version": "qa-stage-trace-v1",
    "capture_status": "INCOMPLETE",
    "events": [],
    "evidence_registry": {},
    "failure_codes": ["QA_EXECUTION_FAILED"]
  }
}
```

The enclosing failed record retains its existing ID/context, `exception`, duration, top-level model_calls/token_usage and model_call_breakdown. It has **no `result`, `diagnostics` or `metrics` populated by this failed QA invocation**. Failure diagnostics are not passed to deterministic metrics, a judge, result validation, retrieval-trace construction or aggregate scoring.

If complete failure-envelope assembly/transport fails, omit `failure_diagnostics` entirely. Omission means capture unavailable, not that no stage ran. Legacy records without the field remain valid; no migration or historical backfill.

## 7. Failure snapshot semantics: reuse qa-stage-trace-v1

Add `_QAStageTrace.snapshot_on_failure()` in the future implementation. It is read-only with respect to the collector and returns a detached JSON-safe copy. Freeze:

1. Copy actual existing `CAPTURED` and `NOT_CAPTURED` events in their original order, including already-captured payload updates, and copy the existing projection registry with its keys unchanged.
2. Set capture_status to INCOMPLETE and include fixed `QA_EXECUTION_FAILED` alongside existing failure codes.
3. Do not invoke `finish()`, create stage placeholders, manufacture outputs or mark absent stages NOT_EXECUTED.
4. Exclude top-level event rows with status NOT_EXECUTED that `finish()` may already have synthesized before a later return-assembly failure. These are successful-completion placeholders, not captured observations. Do not filter a genuine captured payload's internal bypass/fallback fields.
5. Keep at most the existing 16 events and the existing 2,097,152-byte trace cap. Preserve evidence_projection_ref closure. Do not trim quotes, rename projection IDs or evict evidence to make an apparent complete proof fit.
6. If adding the failure code/copying makes the snapshot exceed the cap, emit the existing minimal `_trace_incomplete("TRACE_SIZE_BOUND_EXCEEDED")` form. If snapshot construction raises, the envelope builder substitutes the minimal incomplete trace with `CAPTURE_ASSEMBLY_FAILED`, adds TRACE_SNAPSHOT_FAILED and still tries to preserve bounded decomposition.
7. If the collector failed initialization, use the existing minimal CAPTURE_INITIALIZATION_FAILED trace. If setup failed before initialization was attempted, use a minimal CAPTURE_NOT_INITIALIZED trace. Add TRACE_COLLECTOR_UNAVAILABLE; do not mislabel an unattempted initialization as a failed one.

No v2 trace is needed: v1 already permits INCOMPLETE, NOT_CAPTURED, empty events and a fixed reason code on a minimal envelope. Event absence in a failure snapshot means **no captured observation**, not proof of nonexecution. A captured INPUT records prepared input, not by itself a completed provider invocation. A captured raw OUTPUT records a returned response, not necessarily host acceptance unless its validation update is also present.

## 8. Attempted versus not executed

The repair prevents false certainty by removing synthetic NOT_EXECUTED rows from the failure path. It does not invent a complete operation history or a provider-attempt marker.

| Observation | Permitted interpretation |
|---|---|
| Missing output event | Output not captured; attempted/failed/unreached remains unknown without additional evidence. |
| Existing NOT_CAPTURED event | Capture failed/bounded out according to its code; not a QA verdict. |
| Captured V1/A1/V2 input | That input construction/capture was reached; absence of output does not prove provider status alone. |
| Stage call counter under a verified relevant-role reader | A request was attempted because the adapter increments before calling the provider. |
| Source/path constraints plus complete counters | Reachability can be narrowed only when the compatible paths make it unique. |

A0 has no existing A0_INPUT trace event. Do not add one or change the successful trace. In the fake A0-provider-failure acceptance scenario, the generation counter plus fixed pre-revision path establishes A0 was attempted; no later semantic/composer calls are present under the verified fake reader. Its missing A0_OUTPUT must remain absent, and no later event gets a fabricated nonexecution label. If real counters or capture are insufficient, stage reachability stays unresolved.

The runner's default `_stats_snapshot` currently reads `engine.vertex` (generation client only). This repair does not silently promote it to all-role accounting or rewrite historical totals. The previous launch's separately authorized temporary QA aggregate reader remains a distinct protocol requirement; it is compatible with the wrapper and unchanged post-exception accounting. Fake tests must state whether their reader covers both roles before interpreting counter absence. Do not infer verification nonexecution from a generation-only counter view.

## 9. Canonical decomposition preservation and its bound

Use only the local `decomposition` assigned after successful D1 return. Never serialize a partially constructed proposal or revalidate/reconstruct it after failure. A D1 exception leaves it null; a later analyzer/rerank exception preserves the exact canonical object when within the export cap. A non-decomposition mode uses null with DECOMPOSITION_NOT_APPLICABLE.

Inspection shows the production contract bounds points to 5, relations to 3 per point/10 per question, relation text to 240 characters and relation support spans to 3. It **does not provide a complete byte bound**: point text, point support-span counts/lengths and diagnostic ambiguity reason are not fully bounded; spans also depend on unrestricted question length. The shadow contract likewise does not suffice as a serialized-size bound.

Freeze a failure-export-only decomposition cap of **65,536 UTF-8 JSON bytes (64 KiB)**. Copy with the same deterministic JSON convention as the trace (`ensure_ascii=False`, `sort_keys=True`, `allow_nan=False`). If the entire object exceeds the cap, omit its content as null with DECOMPOSITION_SIZE_BOUND_EXCEEDED. If serialization/copy fails, null with DECOMPOSITION_COPY_FAILED. No string truncation, partial inventory, schema change or change to D1 acceptance is allowed. Preserve the trace independently when decomposition export is unavailable.

## 10. Dedicated exception transport and original failure authority

Select `QADetailedExecutionError(RuntimeError)` in `qa.py` with two in-process attributes: `original_exception` (the exact Exception caught at the detailed-QA boundary) and owned, bounded, JSON-safe `failure_diagnostics`. Raise it `from original_exception`. Its message can be a fixed transport description; runner never serializes that transport type/message as the effective error. The live original object is for classification only and is not part of JSON.

Only capture-enabled execution creates this wrapper, at most once at its owning boundary. Do not attach attributes to the original, replace its __cause__, or traverse to the deepest SDK cause. In this design, "original/root" means the exception that would previously have escaped `_run_detailed` (often VertexCallError); its SDK cause remains intact.

The runner's existing except branch freezes this mapping:

| Saved field / action | Source |
|---|---|
| Classification | `classify_evaluation_exception(original_exception)` using the unchanged classifier. |
| exception.type | `type(original_exception).__name__`. |
| exception.message | `str(original_exception)[:2000]`, unchanged convention. |
| exception.retryable/category | Existing classifier return for that same original object. |
| failure_diagnostics | Only the recognized capture-scoped wrapper's bounded JSON payload, under the independent optional record field. |

Do not generically unwrap arbitrary exceptions by following __cause__. In particular, pass VertexCallError itself to classification so the current SDK cause-code/status inspection and existing type/message rules are preserved. An underlying 429 remains type VertexCallError / retryable true / transport_provider_infrastructure; a semantic ValueError remains terminal where the current classifier says so. No finalization change is needed.

## 11. Catch boundary and observability failures

Initialize local references to decomposition/collector before entering the execution guard, without changing normal operations or their order. Unsupported-mode validation keeps its existing immediate ValueError contract outside the execution guard. For supported modes, cover the current setup, D1, graph invocation, result validation, diagnostics/finish and return-envelope assembly, including a failure in model-usage delta assembly. Capture only `Exception`, not KeyboardInterrupt/SystemExit or other BaseException cancellation.

The execution except branch first retains the original exception. With capture disabled it immediately re-raises that exact object. With capture enabled it builds the bounded envelope and wrapper in an isolated optional-capture try. If that construction fails, re-raise the original from the enclosing execution except, not the capture exception. No second QA attempt and no recovery success object.

Component copy failures are isolated as defined above; complete envelope/wrapper failure causes original propagation with no envelope. The runner serializes/classifies the original first, then attempts the optional payload copy/byte check in a separate best-effort guard. A bad optional payload is omitted; it must not replace the saved exception or prevent its normal store path.

Disk I/O failures from `EvaluationRunStore.record` remain outside that optional-capture guard and propagate as today. Do not suppress a real durability failure or claim a record was saved after a failed write.

## 12. Bounds and security

| Item | Hard persisted bound / behavior |
|---|---|
| Trace | Existing 16-event and 2,097,152-byte limits, including projection registry and failure metadata. |
| Decomposition | 65,536 bytes; entire object preserved or null, never partial semantic text. |
| Envelope | At most **2,166,784 bytes** (trace cap + decomposition cap + 4,096 bytes metadata/separators); final whole-envelope check. |
| Envelope failure codes | Fixed allowlist, unique, at most 8; no arbitrary strings. |
| Copies | JSON round-trip / bounded serialization, no live aliases to events, registry or decomposition. |

Check serialized byte size before accepting a detached copy; stop bounded serialization when the cap is exceeded rather than retain an unbounded diagnostic copy. These are export/persistence bounds, not a new limit on the existing model response or a guarantee about peak memory already used by QA. If whole-envelope encoding/cap check fails, the original exception wins and optional diagnostics are unavailable.

Reuse existing evidence projections and parsed model-input trace payloads explicitly requested for scientific interpretation. Do not export full serialized prompts/system instructions, raw SDK requests/responses/exception objects, headers, stack traces, environment, credentials, private project IDs or full Retriever internals. Already captured parsed V1_INPUT/A1_INPUT evidence is not duplicated into a second retrieval bundle. Canonical support spans and projected quotes remain exact; this design adds no new payload source or secret-discovery operation.

## 13. Failure scenarios and durable scientific meaning

All rows assume the original exception escapes supported-mode `_run_detailed` with capture enabled, and ordinary capture/store succeeds within bounds.

| Failure | Preserved state | Missing state / prohibited inference |
|---|---|---|
| D1 | Empty incomplete existing trace; null decomposition; original error and usage. | No reconstructed D1 proposal, canonical inventory or QA output. |
| Initial analyzer/rerank after D1 | Exact bounded canonical decomposition; whatever trace already exists, possibly empty. | No complete retrieval internals, selected bundle reconstruction or fabricated A0/V1. |
| A0 provider | Decomposition and previously recorded EA_ADMISSION/projections. | No A0 output; absent event is not NOT_EXECUTED. Use counters/path evidence only when sufficient for attempted-stage claims. |
| V1 provider | Prior A0/admission evidence plus already captured V1_INPUT. | V1_OUTPUT absent; input alone is not completed verification. |
| A1 provider after successful V1 | Prior V1_INPUT/V1_OUTPUT with its captured validation update, existing evidence registry, EA_ADMISSION round 1 and A1_INPUT if captured. | No A1_OUTPUT or invented final answer. Prior V1 remains an assessable partial observation only to the extent its proof evidence was actually captured. |
| V2 provider | Prior V1/A1 output/merge events and existing V2_INPUT. | No fabricated V2 output, full-contract success or final answer. |
| Result/diagnostics/return assembly | Captured observations already present, with successful finish placeholders excluded. | No case completion even if a graph result existed locally. |

Existing V1_OUTPUT captures the raw parsed review and updates a validation summary (status/error/error_codes); V1_INPUT/registry hold canonical targets, claims and proof evidence. The full private coverage_receipt/answer_point_audit is not all in that event. Preserve exactly the material present, including raw all-to-all basis/supporter declarations and host validation summary; do not claim a complete receipt or add a duplicate state/audit export. A response without its validation update remains a raw response observation only.

The critical fake scenario needs a **valid first-pass V1 with a genuine missing target authorizing A1**, not an all-complete answer that would skip revision. Use neutral relations/claims and existing host validation/routing. Inject failure at the actual A1 model call after V1, then establish prior V1 proof inspection from persisted parsed input/output, validation and resolvable exact evidence projections. The overall case remains failed and unscored.

## 14. Composer and later runner failures are outside the change

Current composer generation/review exceptions are caught internally and return fallback behavior. Those invocations still complete QA normally; retain their existing successful trace and fallback diagnostics. Do not wrap or rethrow a caught composer error.

Failures after detailed QA has returned (deterministic metrics, external judge, retrieval sidecar writing, store I/O) are not `_run_detailed` failure-envelope cases. They retain the existing runner behavior. Expanding capture to those separate boundaries or crash recovery is outside this minimum repair.

## 15. Successful and capture-disabled invariants

For success, keep identical result, diagnostics fields, successful finish semantics/placeholders, projection keys, parsed trace data and model usage. Do not add failure_diagnostics to successful outputs/records. Keep model prompt/schema/system/role/temperature sequence, retries, retrieval, admission, coverage, revision authorization, full V2 and composer/finalization unchanged. Timing values are not required to be identical; semantic timing fields/ownership remain.

For capture disabled, public `run`, `run_detailed`, and default diagnostic calls retain original object/type/message/cause propagation, results and absence of failure diagnostics. No snapshot/envelope construction or new provider call occurs. Evaluation capture remains opt-in using the existing manifest/flag and resume compatibility checks; no new default flag or runtime mode.

## 16. Store, recovery and scoring compatibility

The current store serializes whole records into attempts.jsonl, records/<ID>.json and results.jsonl, then uses evaluation_record_state based on `exception`. The loader accepts the additive field, and normalize_run_records shallow-copies records without dropping it. Therefore no store or recovery migration is necessary.

Keep exception-first evaluation_record_state/evaluate_cohort_decision, scored-case exclusion, retryable IDs and RECOVERY_PENDING semantics unchanged. A partial V1 observation can support bounded offline inspection, never a completed-case score or a targeted mechanism verdict without its protocol's required observations. Generic retryable=true remains separate from scientific authorization to resume.

## 17. Exact future implementation scope

Only after separate implementation authorization:

1. `src/panda_agent/qa.py`: wrapper, bounded failure snapshot/envelope helper, capture-scoped execution guard. No changes to model-operation call sites or QA decisions.
2. `src/panda_agent/evaluation_runner.py`: import/recognize wrapper in existing case exception branch; serialize original; attach optional safe payload. Keep execution tuple, success scoring/sidecar and usage reader behavior.
3. `tests/unit/test_g5_failed_qa_observability.py`: one focused fake-only module for the frozen matrix, reusing O1/G1/G2 neutral fixtures where appropriate.

Existing O1/recovery tests may be exercised as targeted controls in the future implementation, not rewritten to weaken contracts. No edits to retrieval.py, question_decomposition.py, vertex.py, evaluation.py, evaluation_finalization.py, prompts, provider/public schemas, CLI flags, dependencies or protected data. Normal future implementation documentation/current-state updates are allowed only under that future task's authorization.

## 18. Identity and lineage plan

```text
MODEL_FACING_BEHAVIOR_CHANGE = false
PROMPT_CHANGE = false
PROMPT_FINGERPRINT_CHANGE = false
QA_ANSWER_SEMANTICS_CHANGE = false
PROVIDER_CALL_SEQUENCE_CHANGE = false
PRODUCT_BEHAVIOR_LINEAGE_CHANGE = false
CURRENT_PRODUCT_BEHAVIOR_LINEAGE_HEAD = 5b9588ec552deb91a59a8176d6ce0429c2133b1e
```

The design commit advances repository history only. A conforming future implementation also advances HEAD and changes evaluation capture source/record shape, while retaining model-facing/product-answer lineage. O1 explicitly retained lineage for a behavior-neutral capture implementation; no contradictory precedent is needed to override this default. The prompt_fingerprint payload covers prompts/declared model schemas and versions, not failure-export helpers. Keep the recorded 3.12.1 fingerprint `08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc` unchanged; no new hash inventory is generated here.

Future implementation acceptance must prove those invariants with fakes and static scope review. If implementation needs a semantic/model-facing change, stop and report the scope conflict rather than silently advance lineage or alter this contract. Any later live protocol must identify its actual new repository implementation HEAD separately from the unchanged product lineage and optional diagnostics schema; no historical identity is rewritten.

## 19. Deterministic RED/GREEN acceptance matrix (not executed)

All fixtures are neutral synthetic questions/evidence, temporary test stores and fake provider/retrieval clients. No targeted IDs/raw datasets/protected content, no real SDK/client initialization, Google requests, judge calls, embeddings or live QA. Inspect exact fake call logs, counters and detached payloads. Fake calls/tokens are fixtures, not scientific cost.

| Test | Before implementation expectation (not observed here) | Required GREEN evidence |
|---|---|---|
| A: successful capture | Existing behavior control may already pass. | Equal result/nonfailure diagnostics and successful trace; exact fake model/retrieval sequence and usage; no failure field. Cover no-revision and one-revision paths. |
| B: D1 failure | RED for missing bounded failure envelope. | Original 429 wrapper type/message/category/retryability persisted, decomposition null, empty incomplete trace, no result/diagnostics/metrics. Parameterize a terminal semantic ValueError. |
| C: post-D1 retrieval failure | RED for lost decomposition. | Analyzer and rerank faults retain exact canonical decomposition, no QA success; root cause preserved. |
| D: A0 provider failure | RED for lost prior capture. | Admission/projections retained; no A0_OUTPUT or synthetic NOT_EXECUTED; verified fake counters/logs distinguish attempted A0 from later uncalled stages without deriving nonexecution from event absence. |
| E: V1 provider failure | RED for lost V1_INPUT. | A0_OUTPUT and exact V1_INPUT retained, V1_OUTPUT absent, original exception authoritative; check distinct verification role. |
| F: late A1 provider failure | Critical RED for erased prior V1. | Genuine host-accepted V1 with revisionable missing target, then actual A1 fake call throws; persisted V1 input/output/validation and evidence references allow prior proof inspection, A1_INPUT retained, A1_OUTPUT absent, failed/unscored case. |
| G: capture failures | Some guards may already pass; no claimed baseline run. | Force collector initialization, snapshot, decomposition copy and whole envelope/wrapper construction faults; original exception wins. Component loss is explicit; complete construction failure omits the field. Runner payload-copy failure cannot mask original error. |
| H: capture disabled | Existing exception control may already pass. | Exact original object/type/message/cause escapes public/default and internal capture-false paths; no wrapper, snapshot or failure field. |
| I: V2 provider failure | RED for lost earlier stages. | Prior V1/A1/merge and V2_INPUT survive; V2_OUTPUT absent; no fabricated full-contract or final success. |
| J: bounds, aliases and projection closure | New failure-snapshot controls. | Trace <=16 events/2 MiB; decomposition 64 KiB boundary and multibyte oversized omission; whole envelope cap; JSON-safe no-NaN; mutation of original objects cannot alter snapshot; all projection refs resolve. Oversize trace fallback is explicitly incomplete, not an apparent proof. |
| K: transport/store/recovery | New end-to-end failed-record contract. | Mock runner dependencies with neutral cases; wrapper crosses _execute_evaluation_case without tuple/metrics/judge/sidecar, and actual runner handler writes the optional payload identically to all three store representations. Same classification/cohort/scored exclusion as baseline original error. Legacy no-field records remain valid; ordinary non-QA exceptions unchanged. Real fake-store I/O fault still propagates. |
| L: late assembly and composer control | Targeted compatibility controls. | Throw after finish during return assembly; failure snapshot contains only real capture rows, not successful placeholders. Composer generation/review failures retain normal fallback success and no failure envelope. |

At future implementation entry, write the focused failing tests and run the minimal decisive pre-edit RED cases (at least B/E/F); record actual outcomes. After the smallest source repair, run this module plus directly relevant existing O1 and recovery contracts. No full suite by default, no live targeted rerun. An unanticipated failed control must be investigated within scope; do not change scientific fixtures to pass.

## 20. Implementation acceptance criteria

Implementation is accepted only if all required fake scenarios and relevant existing controls pass, the critical F record preserves inspectable prior V1 proof after actual A1 provider failure, and scope/identity/exception checks confirm:

- Successful/capture-disabled behavior and exact fake call geometry are unchanged.
- Failure snapshots contain only existing capture state, no synthetic missing-stage claims, no aliasing, and bounded JSON payloads with intact evidence references when exported.
- Original error classification/type/message/retryability are unchanged for transient, semantic, cause-code-only and ordinary nonwrapped failures.
- Failure records remain exceptions with no completed result/diagnostics/metrics; no judge/trace-sidecar work follows a failed QA return.
- Capture failure never masks original failure; real store failure is not swallowed.
- Three store representations preserve the optional field; historical records and recovery semantics remain compatible and unchanged.
- No prompt/schema/model/region/retry change, provider call or product-answer lineage advance occurs.

Future PASS may establish `FAILED_QA_PARTIAL_DIAGNOSTICS_EXPORT = DETERMINISTICALLY_VERIFIED` and `LATE_FAILURE_PRESERVES_PRIOR_V1_TRACE = DETERMINISTICALLY_VERIFIED_WITH_FAKES`. These are planned acceptance statements, **not current achievements**.

## 21. Scientific limitations and independent provider boundary

Bounded capture may itself be unavailable or incomplete; exports cannot restore an absent output, repair a bad proof, establish that a missing stage was unexecuted, retain every private graph variable or guarantee crash durability. Root-error subtype, precise retry history and operation detail may remain unresolved; this is why Vertex enrichment is not claimed as a solved provider-diagnosis problem.

The previous raw run and its six failures remain immutable. Even after future implementation PASS, provider recovery/429 resolution, empirical V1 repair benefit, targeted live mechanism support, G5 completion, G6 readiness, fresh generalization and release readiness remain unestablished. Provider availability remains an independent prerequisite. No quota adjustment, model/region switch, probe or retry experiment is designed.

The closed `g5-post-v1-repair-targeted-live-v1` must not be resumed by this repair. Any later live work needs a new forward protocol, new run identity and new explicit authorization. No future live identity is created now.

## 22. Current lifecycle and next step

```text
G5_FAILED_QA_OBSERVABILITY_REPAIR_DESIGN = COMPLETE / IMPLEMENTATION_READY
SELECTED_FAILED_QA_OBSERVABILITY_REPAIR = CAPTURE_SCOPED_FAILURE_BOUNDARY_PARTIAL_DIAGNOSTICS_EXPORT
FAILED_QA_INTERMEDIATE_PERSISTENCE_BLIND_SPOT = CONFIRMED
TARGETED_V1_PROVIDER_STAGE = CONFIRMED_NOT_REACHED
PROVIDER_429_RESOURCE_SUBTYPE = PROVIDER_RESOURCE_EXHAUSTED_SUBTYPE_UNRESOLVED
TARGETED_LIVE_EXECUTION = EXECUTED / SIX ATTEMPTS / SIX INFRASTRUCTURE ERRORS / INCOMPLETE
TARGETED_V1_VERDICT = TARGETED_V1_VERIFICATION_INCOMPLETE
TARGETED_V1_PROMPT_MECHANISM = NOT_ESTABLISHED
REAL_PROVIDER_CONTRACT_COMPLIANCE = NOT_ESTABLISHED / NO ASSESSABLE V1 OUTPUT
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = G5 MINIMAL FAILED-QA OBSERVABILITY REPAIR IMPLEMENTATION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

Recommendation is the single separately authorized implementation task defined above. No implementation or later live task starts here.

## 23. Design-only boundary receipt

Only this design and the two current-state documentation sections change. Historical chronology/prior checkpoint prose and execution/diagnosis/design/raw records remain unchanged. Static review and Git diff checks apply to documentation scope; no development or scientific test is executed. No before/after QA metric is available.

```text
PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
SCHEMA_CHANGE = false
CONFIG_CHANGE = false
DEPENDENCY_CHANGE = false
DATASET_CHANGE = false
TEST_EXECUTIONS = 0
NEW_TARGETED_LIVE_RUNS = 0
NEW_LOGICAL_CASE_ATTEMPTS = 0
NEW_SCIENTIFIC_GENERATION_PROVIDER_INVOCATIONS = 0
NEW_SCIENTIFIC_EMBEDDING_PROVIDER_INVOCATIONS = 0
NEW_SCIENTIFIC_PROVIDER_INVOCATIONS = 0
NEW_SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```
