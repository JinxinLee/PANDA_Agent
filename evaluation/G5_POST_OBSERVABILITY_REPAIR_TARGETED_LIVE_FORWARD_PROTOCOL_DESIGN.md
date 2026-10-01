# G5 Post-Observability-Repair Targeted Live Verification — Forward-Protocol Design

## 1. Status, scope and authority

**PASS / DESIGN COMPLETE / EXECUTION_READY**, subject to separate execution authorization and every frozen preflight below. Readiness means the forward protocol is specified; no provider availability or scientific result is established here. This task is DESIGN / REVIEW / DOCUMENTATION plus commit only. No execution script or source implementation is created.

Entry: clean `main` at `2e7cdf6378d381b629a5510380ef1e8d05e8022d`, message `Preserve failed QA partial diagnostics`. Delivery is the documentation-only commit `Design post-observability targeted live protocol`; resolve its exact SHA from Git history and the delivery report, without embedding a self-referential hash. No push.

Authorities reviewed: [corrected targeted design](G5_POST_V1_REPAIR_TARGETED_LIVE_VERIFICATION_DESIGN.md), [closed execution](G5_POST_V1_REPAIR_TARGETED_LIVE_VERIFICATION.md), [429 diagnosis](G5_TARGETED_PROVIDER_429_BLOCKER_DIAGNOSIS.md), [observability design](G5_FAILED_QA_OBSERVABILITY_REPAIR_DESIGN.md), [observability implementation](G5_FAILED_QA_OBSERVABILITY_REPAIR_IMPLEMENTATION.md), current status/roadmap, AGENTS.md, evaluation policy, and actual QA, runner, finalization, store, Vertex and relevant retrieval source. Installed SDK retry source and non-secret effective settings were inspected locally without constructing a client. No tests were run.

The future six-case QA observation is a bounded T1-sized exposed mechanism check, not T3, T5, release evaluation or formal candidate acceptance. This design does not grant execution authorization.

## 2. Identity and immutable historical state

```text
OBSERVABILITY_IMPLEMENTATION_HEAD = 2e7cdf6378d381b629a5510380ef1e8d05e8022d
PRODUCT_BEHAVIOR_LINEAGE_HEAD = 5b9588ec552deb91a59a8176d6ce0429c2133b1e
FORWARD_PROTOCOL_DESIGN_HEAD = delivery commit resolved from Git history
ACTUAL_LAUNCH_REPOSITORY_HEAD = to be recorded only in separately authorized execution
NORMAL_PRODUCT_MODE = production_answer_obligations_v1
PROMPT_SET_VERSION = 3.12.1
PROMPT_FINGERPRINT = 08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc
QUESTION_DECOMPOSITION_PROMPT_VERSION = 3.0.0
QUESTION_DECOMPOSITION_SCHEMA_VERSION = e1.question_decomposition.v3
COVERAGE_SATISFACTION_SCHEMA_VERSION = coverage-satisfaction-v2
SELECTED_V1_PROVENANCE_CONTRACT = ALL_TO_ALL_CHECK_PROOF_BASIS
HOST_ACCEPTANCE_RULE_CHANGE = false

G5_FAILED_QA_OBSERVABILITY_REPAIR_IMPLEMENTATION = COMPLETE / DETERMINISTIC VERIFICATION PASS
FAILED_QA_PARTIAL_DIAGNOSTICS_EXPORT = DETERMINISTICALLY_VERIFIED
LATE_FAILURE_PRESERVES_PRIOR_V1_TRACE = DETERMINISTICALLY_VERIFIED_WITH_FAKES
FAILED_QA_INTERMEDIATE_PERSISTENCE_BLIND_SPOT = REPAIRED_FOR_CAPTURE_SCOPED_ESCAPING_EXCEPTIONS
PROVIDER_429_RESOURCE_SUBTYPE = PROVIDER_RESOURCE_EXHAUSTED_SUBTYPE_UNRESOLVED
TARGETED_V1_VERDICT = TARGETED_V1_VERIFICATION_INCOMPLETE
TARGETED_V1_PROMPT_MECHANISM = NOT_ESTABLISHED
REAL_PROVIDER_CONTRACT_COMPLIANCE = NOT_ESTABLISHED / NO ASSESSABLE V1 OUTPUT
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
```

The repair guarantee requires `capture_stage_trace=True`, an escaping `Exception`, a live process and normal runner exception-record persistence. It is optional bounded capture, not crash durability, provider recovery or a semantic repair. Historical six-case failures occurred before A0/V1; no completed historical V1 was lost. Their 34 generation + 4 embedding invocations and 17,701 available metadata tokens remain historical only. Source-derived stage bounds and unresolved resource subtype remain unchanged.

## 3. Forward identity, store boundary and API

The historical `g5-post-v1-repair-targeted-live-v1` is closed. No reopening, write, retry, replacement, rewritten status or resume is permitted, including under its generic `RECOVERY_PENDING` label.

Freeze the new identity below. The exact run directory is absent at this design review; it is neither created nor consumed scientifically here.

```text
RUN_ID = g5-post-observability-repair-targeted-live-v2
MODE = qa
SPLIT = novel_dev
DATASET_PATH = evaluation/novel/v1/novel_dev.yaml
ALLOW_DRAFT = true
OFFICIAL = false
CANDIDATE_ID = none
RESUME = false
LIMIT = none
CAPTURE_STAGE_TRACE = true
CASE_IDS = [n008, n018, n019, n022, n025, n028]
MAX_MODEL_CALLS = 240
MAX_TOKEN_USAGE = none
DEADLINE_MINUTES = none
EVALUATOR_CATALOG_PATH = none
EVIDENCE_CLASS = EXPOSED_TARGETED_MECHANISM_EVIDENCE
FUTURE_REPORT = evaluation/G5_POST_OBSERVABILITY_REPAIR_TARGETED_LIVE_VERIFICATION.md
```

These names map to existing `run_evaluation(project_root, mode=..., split=..., run_id=..., allow_draft=True, resume=False, limit=None, case_ids=..., dataset_path=..., candidate_id=None, max_model_calls=240, max_token_usage=None, deadline_minutes=None, evaluator_catalog_path=None, capture_stage_trace=True)`. `official` is derived from `not allow_draft`, not a separate argument. The selector preserves dataset order, not the supplied list's order; verify the actual selected sequence before any canary.

Runner source constructs `EvaluationRunStore` before constructing QAAgent. Therefore the canary must run outside and before the sole scientific runner invocation. A read-only manifest compatibility preflight may use existing facilities without constructing a store or SDK client. Store creation is permitted only after static and provider preflight pass. The manifest retains actual launch HEAD and existing identity fields; record implementation/product/design identities separately in the execution report without inventing manifest fields or a new schema.

## 4. Frozen scientific cohort and attempts

| Role | IDs | Gate |
|---|---|---|
| Primary | n022, n025, n028 | Absolute first-pass provenance and semantic gate |
| Controls | n008, n019 | Absolute provenance; regression-relative semantic safety |
| Supplemental | n018 | NON-GATING; no primary substitution |

Execution order is exactly **n008 → n018 → n019 → n022 → n025 → n028**. Same repair mechanism, same control/primary semantics and no assessable V1 in the closed targeted run justify the same six exposed cases. Observability-only implementation supplies no reason to replace them.

```text
MAX_LOGICAL_ATTEMPTS_PER_CASE = 1
MAX_LOGICAL_CASE_ATTEMPTS = 6
SCIENTIFIC_RUNNER_INVOCATIONS_MAX = 1
RESUMES = 0
REPLACEMENTS = 0
```

No best-of, local rerun, outcome-conditioned second try, manual retry after 429, substituted case or later resume. Adapter retries are part of one logical case attempt. An ordinary saved exception is terminal for this protocol even if generic retryability is true. Absent a frozen global stop, persist it and continue the fixed order. Semantic/provenance outcomes never trigger additional calls or case selection.

Use normal unchanged retrieval and generation, compatible stored embeddings/index, and the existing one-pass pre-answer targeted retrieval. No reindex, forced historical evidence, injected claims, pinned historical retrieval, stage replay, changed query or E3 activation. Same exposed questions yield exposed mechanism evidence, never fresh generalization, novel_validation, holdout or release evidence, and never an isolated prompt causal estimate.

## 5. Zero-call static preflight and launch identity

Before any future client construction/canary, obtain explicit authorization for this exact protocol, accepted design commit, one canary, budgets and the bounded process-local bindings in section 9. This design authorizes none of them now.

Require exact clean accepted design HEAD. Verify its parent is the implementation head and its diff from that head contains only this design and the two current-state documentation updates. Product source, tests, prompts, schemas, configuration, dependencies and data contracts must match the implementation head; implementation history already establishes answer lineage `5b9588...`. Do not incorrectly require QA/runner source to equal pre-observability product lineage. Documentation-only descendants are acceptable only if their exact launch SHA and documentation diff have been explicitly accepted; no implicit latest-HEAD launch. Record actual launch, accepted design, implementation and product lineage separately.

Then verify through read-only existing facilities:

- Active prompt version/fingerprint via `evaluation_runner.prompt_fingerprint()`, normal mode and schema versions.
- Interpreter/package table below, effective generation/verification/embedding settings, routing/config identity, retry policy and one targeted-retrieval limit.
- Dataset `novel-v1-dev-0.3.0`, exact selected IDs/order and selected raw-question bytes against historical exposed traces.
- Existing dataset/source/normalized-corpus/index/embedding/policy/query-expansion/audit identities compatible with the previous targeted manifest and original O/S comparison authorities. Use existing manifest/index facilities, including their read-only database compatibility lookup; no new integrity manifest or per-file hashes.
- Required historical records, traces, V1 input/output/registry material available; new run directory unused; no protected content/outcome access.
- Accounting/observer/stop seams remain as inspected, and the 40/240 scientific geometry is derivable from unchanged source. All proposed bindings can be installed and their identities checked before scientific work.

Any mismatch is **STOP BEFORE CANARY**. No environment/package/configuration/index repair, fallback model, role-specific extra probe, new cohort or opportunistic suffix is permitted. Static failure is `FORWARD_TARGETED_EXECUTION_NOT_STARTED / STATIC_PREFLIGHT_FAILED`, with no new targeted scientific verdict or store. It ends that execution authorization; later execution requires a new explicit identity/protocol decision.

| Frozen setting | Expected value; statically observed in this design |
|---|---|
| Interpreter | `C:\Users\Jinxin.DESKTOP-H6SSTQH\Desktop\Agent_learn\.venv\Scripts\python.exe` |
| Python / langgraph / qdrant-client | 3.12.14 / 1.2.10 / 1.15.1 |
| google-genai / psycopg / panda-research-qa-agent | 2.13.0 / 3.3.4 / 0.1.0 |
| Generation / effective verification | gemini-3.8-flash / gemini-3.8-flash |
| Embedding / dimensions | gemini-embedding-2 / 3072 |
| Location / timeout | global / 120000 ms |
| max_targeted_retrievals | 1 |
| Adapter generation / embedding maxima | 3 / 5 |
| Effective SDK retry_options | None; SDK maps this to one HTTP attempt |

Read-only dotenv loading with `override=False` matches CLI convention. `VertexSettings.for_verification_model()` preserves project/location/config while changing generation_model to the effective verification ID; current role project/location/model equality is true. Keep the existing approved QA project/config and compare private project equality locally across canary and both scientific clients; report booleans, not credentials/private IDs. A changed routing configuration needs reconciliation before canary. Historical manifests do not record private project/location/timeout, so exact historical private-project equality remains unresolved and is not claimed here. No SDK client was instantiated during this review.

## 6. Provider availability prerequisite

```text
PROVIDER_AVAILABILITY_PREFLIGHT = GENERATION_ONLY_CANARY
GENERATION_CANARY_REQUIRED = true
EMBEDDING_CANARY_REQUIRED = false
FULL_HEALTH_CHECK_SELECTED = false
INFRASTRUCTURE_PREFLIGHT_LOGICAL_OPERATIONS_MAX = 1
INFRASTRUCTURE_PREFLIGHT_GENERATION_PROVIDER_INVOCATIONS_MAX = 3
```

Select exactly one existing `VertexAIClient.generation_health_check()` operation on a dedicated canary client with the frozen generation settings. It calls the existing deterministic health prompt/schema through `generate_json`, temperature 0, and reports status/model/location; it neither embeds nor touches case data. No invented health prompt/schema or second canary for an identically configured verification role. Before calling it, establish that the actual settings and SDK retry options match the static freeze. A generation/verification project/location/model mismatch fails static preflight rather than expanding the plan.

Historical terminal blocker is structured generation `429 RESOURCE_EXHAUSTED`, while four query embeddings returned successfully. Existing `health_check()` additionally embeds a query and document. Those operations do not address the demonstrated terminal blocker and are outside this minimal gate. No embedding availability guarantee is claimed by omitting probes.

**Pass requires normal helper return, `status == "ok"`, returned model/location equal the freeze, and unchanged matching config.** Exception, 429/resource exhaustion, 503, timeout, authentication failure, unexpected_response, malformed/missing return, wrong identity or accounting/budget anomaly fails the gate. One operation may use at most three unchanged adapter invocations; no outer retry/probe-until-pass. Passing establishes only that the endpoint accepted this bounded operation at that moment, not continuous capacity, full-batch quota health, QA correctness, V1 compliance or future success.

## 7. Canary accounting, failure and identity consumption

Use a separate client whose counters never enter scientific QA counters. Snapshot its existing `stats_snapshot()` before the operation and in `finally` after normal return or exception; retain deltas, available token metadata, return/status or effective exception, and identity-match booleans in the execution report. Initial counters must be zero; generation delta <=3, embedding delta 0. Failed requests without usage metadata have unknown billable token usage. Do not reset/mutate scientific role counters to erase a probe.

Future report fields:

```text
INFRASTRUCTURE_PREFLIGHT_LOGICAL_OPERATIONS
INFRASTRUCTURE_PREFLIGHT_GENERATION_PROVIDER_INVOCATIONS
INFRASTRUCTURE_PREFLIGHT_AVAILABLE_METADATA_TOKENS
INFRASTRUCTURE_PREFLIGHT_STATUS
SCIENTIFIC_RUN_STARTED
LOGICAL_CASE_ATTEMPTS
SCIENTIFIC_PROVIDER_INVOCATIONS
SCIENTIFIC_TOKENS
```

If the canary fails before store creation:

```text
FORWARD_TARGETED_EXECUTION_NOT_STARTED / PROVIDER_AVAILABILITY_PREFLIGHT_FAILED
SCIENTIFIC_RUN_STARTED = false
LOGICAL_CASE_ATTEMPTS = 0
SCIENTIFIC_PROVIDER_INVOCATIONS = 0
SCIENTIFIC_TOKENS = 0
SCIENTIFIC_RUN_STORE_CREATED = false
```

No case is consumed and no new targeted V1 verdict is measured. Historical targeted INCOMPLETE remains. **FAILED PREFLIGHT CONSUMES THE EXECUTION AUTHORIZATION, NOT THE SCIENTIFIC RUN STORE.** The reserved v2 is recorded as not executed; later authorization must choose a new forward execution/run identity rather than silently reusing v2, adding a suffix mid-execution or probing repeatedly. A canary success followed by pre-case orchestration/engine failure also ends the authorization without a second runner invocation; distinguish any created empty store and zero attempts explicitly.

Only after successful canary may the sole runner create the new store. Scientific accounting starts from fresh QA role counters after that success. Canary receipts are infrastructure preflight and never enter primary/control denominators, scientific spending or generic QA metrics.

## 8. Scientific geometry and budgets

Unchanged source supports at most these logical operations per case:

| Operation | Maximum |
|---|---:|
| D1, initial analyzer, initial rerank | 3 generation operations |
| Optional one pre-answer targeted rerank; supplied plan, no analyzer replay | 1 generation operation |
| A0, V1, target-authorized one A1, full original V2 | 4 generation operations |
| Composer and composer review if normally eligible | 2 generation operations |
| Initial and optional targeted query embedding; paper channel reuses vector | 2 embedding operations |
| External judge | 0 |

Ten structured operations × three adapter attempts =30; two embeddings × five =10. Production E3 is disabled; no semantic-shadow embedding or added stages. The SDK None retry branch adds no HTTP multiplier. Model-call counters increment before each SDK invocation, including failed adapter attempts. Preserve adapter retries/delays; no new retry on answer/provenance quality.

```text
MAX_SCIENTIFIC_GENERATION_PROVIDER_INVOCATIONS_PER_CASE = 30
MAX_SCIENTIFIC_EMBEDDING_PROVIDER_INVOCATIONS_PER_CASE = 10
MAX_SCIENTIFIC_PROVIDER_INVOCATIONS_PER_CASE = 40
MAX_SCIENTIFIC_GENERATION_PROVIDER_INVOCATIONS_TOTAL = 180
MAX_SCIENTIFIC_EMBEDDING_PROVIDER_INVOCATIONS_TOTAL = 60
MAX_SCIENTIFIC_PROVIDER_INVOCATIONS_TOTAL = 240
MAX_PREFLIGHT_PROVIDER_INVOCATIONS = 3
MAX_ALL_PROVIDER_INVOCATIONS = 243
MAX_TOKEN_USAGE = none
DEADLINE_MINUTES = none
EXTERNAL_JUDGE_CALLS = 0
```

243 is the absolute bound when all six scientific cases run, not an expected cost. No guessed token/quota cap: resource subtype remains unresolved. Record available response metadata independently of billed failed-request usage; no dollar/failed-token estimate is certified. Exact transport retry histories remain UNRESOLVED when not captured; do not infer them by dividing totals. Historical O/S counters remain generation-client-only, not comparable certified all-role cost totals.

Runner cap checks occur between cases, not within a provider operation. The bound rests on the frozen graph/retry geometry and six attempts. Reconcile each saved case against 30/10/40 and cumulative 180/60/240; a value **greater than** a bound is a protocol breach. Native `>=240` guard is preserved; exactly240 after all cases is not an overrun or automatically missing measurement. No hard intra-case limiter is claimed.

## 9. Bounded future orchestration: accounting and global stop

The runner reads only `engine.vertex`; default QA creates distinct generation/verification clients. Its default counter is insufficient. The runner also has no native recurrence callback. No permanent source change is needed: freeze these three narrow process-local bindings for the single future runner invocation, subject to that execution task's explicit authorization. They are specified, not implemented or installed now.

| Existing seam | Required temporary behavior |
|---|---|
| `evaluation_runner._stats_snapshot` | For QAAgent, return existing `QAAgent._stats_snapshot()`; for Retriever preserve original reader. Verify actual role settings/SDK retry identity, aggregate equals each distinct client's snapshot summed once, generation alias unchanged, retriever uses generation role, initial counters zero. Preserve all stage keys; check reader identity on every read. Failure/loss stops before subsequent scientific calls. |
| `EvaluationRunStore.record` | For only the exact new store, call original method once with unchanged record **first**. After all ordinary ledger/canonical/results writes return, inspect persisted `current_records[id]`, verify order/uniqueness, reconcile counters and update recurrence state. Other stores delegate normally. Never edit/inject results, reclassify exceptions or change successful/completed/retryable IDs. |
| `evaluation_runner._attempt_budget_stop_reason` | Call original with identical arguments, preserving native cap/token/deadline logic. At each existing pre/post-case boundary, check bindings/identity/input integrity and observer state. Return `protocol_invalid` for a discovered protocol breach, else `provider_generation_resource_recurrence` when the frozen threshold fires, else the original reason. No altered per-case QA or adapter behavior. |

Install/verify all references before invoking the runner, hold original references and restore **all three in `finally`** on every exit. Check all three installed identities at each stats read, persisted-record observation and loop boundary. Use a single process with no other concurrent evaluation. The first runner stats read verifies actual engine accounting before its first model call; static checks before canary already establish source/config viability. An absent/unverifiable binding forbids launch; a post-canary actual-engine mismatch forbids scientific calls even if the runner already created an empty store. Later binding loss or observer-integrity failure is protocol-invalid, never a zero-usage fallback.

The record observer does not throw an intentional recurrence exception: that would bypass normal runner finalization. Its bounded observation failure after successful persistence sets protocol-invalid state for the next boundary. Actual original store I/O failures remain unsuppressed and halt immediately; they may prevent ordinary finalization, so report surviving artifacts and the limitation without manufacturing a completed status. Stats-read failures likewise stop rather than launching another runner to salvage output.

After the second matching case is durably saved, the existing post-case stop check breaks the loop **before the next case**. The runner then normally loads records, evaluates cohort completeness, writes run_status and reports. Its native `status=budget_exhausted` for any non-null stop reason is a generic label, even for recurrence; retain raw status and interpret the exact `stop_reason` in the dedicated report. Generic RECOVERY_PENDING/missing IDs never authorize resume.

Boundary integrity checks cover accepted launch/source/clean tree, frozen input/config identities, installed readers/observer/guard, record order/closure and budgets. Any detected lineage mismatch, worktree/input mutation, binding loss, store corruption, budget breach, protected-access breach or evidence-integrity breach stops before another case. An in-flight request cannot be undone; this design claims boundary stopping, not a watchdog or intra-call interruption. No new schema, CLI flag, persistent hook, generic taxonomy/logger or checked-in execution script is required.

## 10. Exact provider recurrence rule

```text
GLOBAL_PROVIDER_RECURRENCE_STOP_RULE = TWO_CONSECUTIVE_CASE_LEVEL_TERMINAL_GENERATION_RESOURCE_ERRORS
REPEATED_PROVIDER_FAILURE_STOP_RULE = TWO_CONSECUTIVE_CASE_LEVEL_TERMINAL_GENERATION_RESOURCE_ERRORS
GLOBAL_PROVIDER_RECURRENCE_STOP_REASON = provider_generation_resource_recurrence
```

Only scientific cases after successful canary count. Maintain a consecutive counter in frozen execution order. A match requires all of:

1. A persisted case-level exception whose **effective saved** type is exactly `VertexCallError` and category is exactly `transport_provider_infrastructure`. Use the runner's saved original exception, not `QADetailedExecutionError` or arbitrary recursive SDK cause unwrapping.
2. Its message begins with the unchanged adapter prefix `structured generation failed for gemini-3.8-flash in global:` (casefold for matching only; preserve raw bytes).
3. The error suffix immediately after that prefix, ignoring leading whitespace, begins with numeric HTTP token `429` followed by whitespace and exact status token `RESOURCE_EXHAUSTED` (casefold only, token boundaries required). Both are required. A documentation URL mentioning429 or unrelated nested text alone is insufficient.
4. Frozen project/config/model/location identity remains verified, record order is intact and the case's single logical attempt has ended. All matching records share this one known family; no generic expansion to bare resource messages, 503, timeouts or other models.

Each matching case increments the consecutive count; **every** nonmatching case resets it to zero, including success, embedding failure, semantic ValueError, different provider/protocol error or an unclassifiable/truncated signature. Canary is never counted. A local store fault instead triggers immediate integrity stop, not recurrence. Thus error/success/error is not two consecutive errors; n008+n018 can trigger the rule even though n018 is scientifically non-gating.

On count2, preserve the second record's original error, optional partial diagnostics and all-role counters, then stop. This is terminal at case level even if `retryable=true`; it does not require finalization's `terminal_exception` class. One resource error alone continues: it could be transient, isolated or request-specific. Two satisfy a resource-protection rule, not proof of global outage, specific quota, rate limit or shared capacity. A repeated late A1/V2 generation fault may match while both prior V1 observations remain assessable.

Remaining IDs are reported `UNATTEMPTED_BY_PROTOCOL_STOP`; leave their records absent, with no synthetic exception/NOT_EXECUTED trace, replacement or later resume. Required missing observations normally trigger Rule4, unless already observed Rule2/3 safety veto applies; protocol-invalid conditions take Rule1 precedence. If no required observation is missing and earlier V1s satisfy assessability, apply the remaining mechanism rules independently of downstream failures. Triggering a stop after the final ID leaves zero unattempted IDs; do not invent missing observations.

## 11. Observability contract and failure analysis

For every failed captured QA case, report effective exception type/message/retryable/category, presence or absence of `failure_diagnostics`, its capture_status/failure_codes, canonical question_decomposition availability, exact trace events/statuses, projection-reference closure and all-role counters. Inspect `record.failure_diagnostics` separately from successful `record.diagnostics`; never pass it to scoring, metrics or judge work.

The optional five-field `qa-failure-diagnostics-v1` envelope is INCOMPLETE; trace remains qa-stage-trace-v1. It preserves actual CAPTURED/NOT_CAPTURED events and exact projection keys, not synthetic NOT_EXECUTED placeholders. Bounds: 16 events, 2,097,152-byte trace, 65,536-byte D1 export and 2,166,784-byte envelope. Oversize/copy/assembly failure can remove D1, trace or the entire optional field. No missing output is reconstructed or retried.

An absent event means no captured observation. INPUT means prepared input, not a completed provider request; raw OUTPUT means returned response, not validation. Counter/path-based reachability is permitted only with adequate verified all-role evidence and uniquely compatible source paths. No A0_INPUT is invented; no stage marker is added. D1 diagnostic quality and V1 mechanism claims remain separate. Null D1 export does not alone erase canonical targets actually preserved in V1_INPUT.

## 12. Preserved failed-case V1 assessability

Use successful `diagnostics.qa_stage_trace`, or for a failed case only its actually persisted `failure_diagnostics.qa_stage_trace`. Require **all four**, plus enough material for the complete frozen target audit:

1. `V1_INPUT`, round1, status CAPTURED: original question, canonical target inventory, normalized draft/claims, admitted evidence and deterministic input exclusions are inspectable to the extent needed for the target.
2. `V1_OUTPUT`, round1, status CAPTURED: raw first-pass response and full relevant proof declarations are present, without missing/trimmed owner/check content.
3. That OUTPUT payload includes the actual host validation update (`validation.status` ACCEPTED/PARTIAL/REJECTED and captured errors/error_codes needed to interpret the target). Raw response alone is insufficient; host acceptance is not a semantic oracle. A partial/rejected review can still be an assessable negative if ownership/proof material is complete enough.
4. Every referenced evidence projection resolves to exact preserved text/identity, and the available question/canonical inventory/claims/basis/quotes/supporter citations are sufficient for comparable nonvacuous provenance and semantic classification. Registry closure alone does not prove substantive adequacy.

If any requirement fails or target comparability/semantics cannot be resolved, `V1_TARGET_OBSERVATION=NOT_ASSESSABLE`; report the exact gap. Missing/malformed owned rows can be assessable negative declarations when their required owner is visible; missing trace fragments are not proof of invalid output. Neither an envelope's INCOMPLETE flag nor a late overall exception automatically makes a complete prior V1 unassessable. No private full coverage_receipt/answer_point_audit is assumed exported; where existing material cannot support a field, report UNAVAILABLE/UNRESOLVED.

**A later A1/V2/provider/assembly failure does not retroactively turn an assessable completed V1 into not reached.** It may contribute to first-pass primary/control gates under the frozen audit. The overall case remains failed/unscored; downstream completion and final QA answer are not inferred. Conversely A1/V2 acceptance cannot rescue malformed first-pass V1. This separates scientific observation from whole-case execution status without changing finalization/source behavior.

## 13. Primary provenance and absolute semantic gates

Primaries retain historical targets/faults: n022 BAD_QUOTE (formatting), n025 INVALID_SUPPORTER (ordinary proof citation closure), n028 INVALID_SUPPORTER (canonical exposure proof citation closure). Positive requires **V1_TARGET_OBSERVED + PROVENANCE_VALID + NO_SEMANTIC_EVASION_OBSERVED + nonvacuous comparable proof declaration**. No final-answer status substitutes for this absolute gate.

Retain four provenance outcomes: `PROVENANCE_VALID`, `PROVENANCE_INVALID_SAME_FAMILY`, `PROVENANCE_INVALID_NEW_FAMILY`, `NOT_ASSESSABLE`. Inspect actual quote membership, individual supporter-to-every-basis citation edges, per-supporter contribution, collective full-check completeness, known/admitted basis and owner/path validity. Same error code with a different missing/wrong-parent supporter mechanism is not automatically the historical family. If same/new defects coexist, label same-family and list new defects. Unsatisfied can be provenance-valid but is positive only with justified honesty and comparable nonvacuous proof opportunity.

Semantic audit checks raw-question-defined scope, necessary relation/check inventory, complete adequate witness/basis and truthful unsatisfaction. Empty/shrunken declarations, dropped/weakened canonical relations, alternate completeness paths or unsatisfied disposition avoiding an available adequate witness cannot count as improvement. Distinguish actual semantic evasion/undercheck from genuinely inadequate evidence, upstream variation or retained distributed-proof expressiveness limits. Unresolved comparability is missing measurement, not success or fabricated negative.

For n022/n028/n018 compare relation **meaning** using raw-question support, direction, polarity and explanation, not generated numeric IDs. Audit every relation owning that need. n025 is relation-free ordinary inventory covering combinatorial management and displaced-vertex efficiency. Changed ordinary wording/count is acceptable only if full necessary meaning remains; invented ordinary checks cannot replace a required canonical relation. Current/historical host acceptance never defines semantic truth.

## 14. Controls and supplemental baseline

For each control report A.new absolute semantic state, B.regression-relative interpretation, C.provenance, D.clean yes/no. Allowed semantic classes:

| Class | Clean eligibility, also requiring assessable feature and PROVENANCE_VALID |
|---|---|
| CONTROL_SEMANTIC_BASELINE_CLEAN | Yes, resolved baseline adequacy and no regression |
| CONTROL_PREEXISTING_SEMANTIC_LIMITATION_UNCHANGED | Yes, documented limitation persists without additional weakening; no absolute completeness claim |
| CONTROL_NEW_SEMANTIC_REGRESSION | No; observed safety veto |
| CONTROL_SEMANTIC_COMPARABILITY_UNRESOLVED | No; required observation incomplete |

Clean requires assessable target/proof feature, valid provenance on all relevant checks, no new question-defined semantic regression and resolved interpretation. A different adequate proof is not inherently a regression, but cannot silently certify an unexercised historical proof feature. New quote/basis/supporter/admission/owner/path invalidity is a provenance regression. Primary semantic veto remains absolute; control semantics are regression-relative.

**n019:** Raw question requires input PndTrack → fitted output, fitter selection, particle hypothesis and construction of persisted result. Historical inventory represented construction; the final answer did not explain actual construction. The known pre-existing limitation may remain clean for this provenance experiment if no additional weakening and the multi-basis/ordinary-plus-canonical/CRLF proof features remain assessable/valid. Report continued construction incompleteness explicitly; never call it absolutely complete or recovered. Any further loss is a new regression.

**n008:** Preserve raw-question algorithm identity and comparison, including historically realized identification/comparison meaning and shared-basis multi-supporter opportunity. Do not turn Gold-only numerical/source detail into new mandatory obligations. Additional identification/comparison weakening is regression.

**n018:** SUPPLEMENTAL / NON-GATING. Analyze D1 diagnostics, V1 common-basis/data-model ambiguity and preserved failure-stage observations against the separate baseline. It cannot substitute for a primary; its exception/unresolved result alone cannot improve or defeat the primary/control verdict. A global recurrence triggered during it can leave required cases unattempted; that effect is evaluated by Rule4, not a supplemental semantic veto.

## 15. Historical comparison authorities

O=`data/evaluation/runs/g5-integrated-candidate-novel-dev-v1`: n008/n019/n022/n025/n028 `records/<ID>.json::diagnostics.qa_stage_trace` plus `traces/<ID>.json::raw_question`. S=`data/evaluation/runs/g5-n018-separately-authorized-rerun-v1`: n018 corresponding record/trace. Inspect literal stored quotes/citations, V1_INPUT/V1_OUTPUT/validation and projection registry; IDs are run-local. Original O/n018 failed D1 with no retrieval trace; do not reconstruct its proposal or merge S into the original cohort.

Closed `data/evaluation/runs/g5-post-v1-repair-targeted-live-v1` supplies infrastructure/observability history only. Its absent V1 is not a semantic baseline. Earlier baseline product/prompts differ; current retrieval/decomposition/generation variation and D1 repair limit causal claims. Historical raw stores, reports, results and chronology remain immutable. No rescore/backfill or replacement is authorized.

## 16. Frozen verdict precedence: Rule 0–7

Apply in order. Required first-pass observations are three primaries and two controls; n018 has no gating denominator. Whole-case exceptions with assessable prior V1 do not automatically enter Rule4. Keep downstream incomplete execution separate.

| Rule | Condition | Result |
|---|---|---|
| 0 | Provider preflight fails before scientific store/run | FORWARD_TARGETED_EXECUTION_NOT_STARTED / PROVIDER_AVAILABILITY_PREFLIGHT_FAILED; no newly measured targeted V1 verdict; historical INCOMPLETE unchanged |
| 1 | Protocol/evidence-integrity violation after scientific run begins | TARGETED_V1_VERIFICATION_INCOMPLETE; reason PROTOCOL_INVALID; overrides apparent support or safety outcomes |
| 2 | Any assessable primary SEMANTIC_EVASION_OR_UNDERCHECK_OBSERVED | TARGETED_V1_MECHANISM_NOT_SUPPORTED |
| 3 | Any assessable control provenance regression or CONTROL_NEW_SEMANTIC_REGRESSION | TARGETED_V1_MECHANISM_NOT_SUPPORTED |
| 4 | Any required primary/control unattempted by global stop, errored without assessable V1, not comparable or semantic interpretation unresolved | TARGETED_V1_VERIFICATION_INCOMPLETE, unless earlier Rule2/3 veto applies |
| 5 | All three primaries positive and both controls clean | TARGETED_V1_MECHANISM_SUPPORTED |
| 6 | All required observations assessable, controls clean, one or two positive primaries, remaining primaries malformed provenance | TARGETED_V1_MECHANISM_PARTIAL |
| 7 | All required observations assessable, controls clean, zero positive primaries | TARGETED_V1_MECHANISM_NOT_SUPPORTED |

Static failure is the additional not-started status in section5; it is not a scientific targeted verdict. No majority/percentages, post-hoc denominator reduction or supplemental substitution. Report fixed denominator3, assessable count, positive count, both controls and all unattempted IDs separately. Resource recurrence is not itself mechanism failure or protocol invalidity. Supported maps to PASS at this bounded mechanism scope; partial/not-supported maps to FAIL of the all-primary criterion; incomplete maps to INCONCLUSIVE. None completes original G5 or advances G6.

## 17. Three reporting layers and execution receipt

For every attempted case, including errors, report:

1. **First-pass mechanism:** V1 reachability, observation source (success/failure diagnostics), raw declaration and captured validation, before/after owner/basis/supporters/citation/quote evidence, provenance taxonomy, semantic audit and assessability rationale. State capture gaps, D1 availability and projection closure. Controls additionally require all four absolute/relative/provenance/clean fields.
2. **Coverage/revision:** target/point/whole coverage, independently valid siblings, revisionable relationships, unsupported-claim targets, A1 authorization/execution, original-inventory V2 status and revision count. Use actual available fields; absent private audit material is UNRESOLVED, not inferred success/nonexecution.
3. **Final QA:** result status or effective exception, retained/excluded claims where present, composer/fallback and generation/embedding/all-role invocation and available token totals. Failed case remains failed/unscored despite assessable V1. No downstream recovery changes first-pass declaration validity.

Future report also records accepted design/actual launch/implementation/product/prompt identities, interpreter/packages/models/config equality, existing corpus/index/dataset compatibility, selected roles/order, canary receipts separate from science, one-attempt/no-resume ledger, bindings/restoration, raw stop_reason and native runner/cohort labels, matching recurrence pair, unattempted IDs, budget reconciliation, available retry limits/history and frozen verdict rationale. Preserve raw exception message/retryable/category and optional diagnostics; infer a resource subtype only if new explicit evidence supplies it, never from429 alone.

## 18. Protected and present design-only boundaries

No protected case/content/outcome listing, search or read. Existing exposed selected historical artifacts are the only comparison lane. No protected material may choose or interpret the cohort. Only this new design and the current authoritative sections of the two documents change; every prior current checkpoint paragraph and historical chronology remains.

```text
PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
PUBLIC_SCHEMA_CHANGE = false
MODEL_FACING_SCHEMA_CHANGE = false
CONFIG_CHANGE = false
DEPENDENCY_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
TEST_EXECUTIONS = 0
NEW_PROVIDER_PREFLIGHT_CALLS = 0
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

Static source/report/config/package inspection, existing prompt identity calculation, documentation consistency review and git diff/check are design validation, not tests or evaluations. No before/after scientific benefit metric is available. No SDK client, health-check operation, generation/embedding call, evaluation runner, new run/store or orchestration binding was instantiated/invoked here.

## 19. Lifecycle and next step

```text
G5_POST_OBSERVABILITY_REPAIR_TARGETED_LIVE_FORWARD_PROTOCOL_DESIGN = COMPLETE / EXECUTION_READY
FORWARD_TARGETED_RUN_ID = g5-post-observability-repair-targeted-live-v2
FORWARD_TARGETED_EXECUTION = NOT_STARTED
PROVIDER_AVAILABILITY_PREFLIGHT = GENERATION_ONLY_CANARY
REPEATED_PROVIDER_FAILURE_STOP_RULE = TWO_CONSECUTIVE_CASE_LEVEL_TERMINAL_GENERATION_RESOURCE_ERRORS
TEMPORARY_PROCESS_LOCAL_READ_ONLY_ALL_ROLE_ACCOUNTING_BINDING = REQUIRED
TEMPORARY_PROCESS_LOCAL_PERSISTED_CASE_OBSERVER_AND_STOP_BINDING = REQUIRED
TARGETED_V1_VERDICT = TARGETED_V1_VERIFICATION_INCOMPLETE
TARGETED_V1_PROMPT_MECHANISM = NOT_ESTABLISHED
REAL_PROVIDER_CONTRACT_COMPLIANCE = NOT_ESTABLISHED / NO ASSESSABLE V1 OUTPUT
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = G5 POST-OBSERVABILITY-REPAIR TARGETED LIVE VERIFICATION EXECUTION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

The single next recommendation requires separate explicit authorization of this accepted protocol/launch identity and its canary, scientific budget, accounting and observer/stop bindings. It is not started automatically. Future incomplete evidence calls for a separately authorized blocker review/new forward decision; supported exposed observations still supply no fresh/release evidence or original G5 completion. No full G5 rerun, protected lane, prompt tuning or G6 execution follows this design PASS.
