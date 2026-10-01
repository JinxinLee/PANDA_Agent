# G5 Targeted Provider 429 / Missing Persisted V1 Observation — Bounded Blocker Diagnosis

## 1. Status and authorized scope

**PASS / OFFLINE DIAGNOSIS COMPLETE.** Two separate blockers are established: terminal generation-provider resource errors during the six-case window, with the resource subtype unresolved; and a confirmed failed-QA intermediate-persistence blind spot. Recommendation: **MINIMAL FAILED-QA OBSERVABILITY REPAIR DESIGN**, separately authorized, before considering another live attempt. No repair or new attempt is performed here.

Starting clean `main` HEAD: `49a0168fc7ff6ae33e2f4dc863341a05ca6d0eb8`, message `Run targeted post-V1 live verification`. Product behavior lineage remains `5b9588ec552deb91a59a8176d6ce0429c2133b1e`. The local raw store exists and was inspected read-only. The diagnosis delivery commit is `Diagnose targeted provider 429 blocker`; resolve its SHA from Git history, with exact SHA reported on delivery. No push.

This is diagnosis/review only. No product function, provider request, health check, runner/resume, QAAgent or live Retriever invocation, console/API probe, test suite, environment change, model/region switch or protected-content access occurred. Local scripts only read/parse artifacts, configuration and source. No new machine-result format, hash inventory or logging framework is created.

## 2. Authority and immutable execution

Primary authorities: [targeted execution report](G5_POST_V1_REPAIR_TARGETED_LIVE_VERIFICATION.md), [corrected frozen design](G5_POST_V1_REPAIR_TARGETED_LIVE_VERIFICATION_DESIGN.md), [V1 repair implementation](G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_IMPLEMENTATION.md), current status/roadmap, and unchanged `llm/vertex.py`, `qa.py`, `question_decomposition.py`, `retrieval.py`, `evaluation_runner.py`, `evaluation.py` and `evaluation_finalization.py`. Product source matches the frozen lineage. Installed google-genai 2.13.0 source was read locally; no SDK model call was executed.

The closed run is `data/evaluation/runs/g5-post-v1-repair-targeted-live-v1/`, launched at clean repository HEAD `e313ea77a27ce23eeb475ec3889111635de184dd`, under `production_answer_obligations_v1`, prompt set 3.12.1 / fingerprint `08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc`, `qa`, non-official draft `novel_dev`. The one-attempt order is n008, n018, n019, n022, n025, n028. Actual historical spending remains 34 generation + 4 embedding = 38 provider invocations and 17,701 available metadata tokens.

The original targeted verdict remains `TARGETED_V1_VERIFICATION_INCOMPLETE`, frozen Rule 4. Source-derived reachability refinements below do not create a V1 response, change the verdict, rewrite the execution report or authorize resuming its `RECOVERY_PENDING` store.

## 3. Evidence inventory

Read all six `records/<ID>.json`, `manifest.json`, `attempts.jsonl`, `results.jsonl`, `run_status.json`, `metrics.json`, existing gate files and runner `report.md`. The two ledgers and six canonical records contain equivalent observations. Each ID occurs once in the attempt ledger; all have a saved exception, no result/diagnostics and no retrieval-trace sidecar. No hidden trace or evidence registry exists in this store.

`metrics.cases_completed=6` and runner report `Completed: 6/6` count records, while `scored_cases=0` and the cohort decision are incomplete. Those labels are not six completed QA results. The generic gate/calibration artifacts contain no additional provider metadata or intermediate-stage receipts.

Evidence vocabulary used throughout:

- **PERSISTED:** a field/byte actually present in the unchanged raw store or historical report.
- **DERIVABLE_FROM_SOURCE:** a consequence of those observations plus the exact frozen call path/counter implementation; not a persisted stage marker or model output.
- **PLAUSIBLE_BUT_UNRECOVERABLE:** information that might have existed in a live exception/response or invocation-local state, but is not available after process exit.
- **UNKNOWN:** neither persisted nor uniquely implied; no reconstruction or live probe is used.

## 4. Exact saved provider observations

All six exceptions are identical in type, classification and message:

```text
exception.type = VertexCallError
exception.category = transport_provider_infrastructure
exception.retryable = true
```

Exact common message, 302 characters (below the runner's 2,000-character limit):

```text
structured generation failed for gemini-3.8-flash in global: 429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Resource exhausted. Please try again later. Please refer to https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429 for more details.', 'status': 'RESOURCE_EXHAUSTED'}}
```

The embedded body has only `error.code`, `error.message` and `error.status`. It has no `details`, quota metric/location/limit, requests-per-minute or tokens-per-minute limit, consumer, `google.rpc.QuotaFailure`, `google.rpc.ErrorInfo`, structured reason/domain/metadata, capacity subtype or Retry-After value. The message does not say quota exceeded, rate limit or shared/model capacity. The documentation URL is part of the saved error, not a resource-subtype diagnosis; it was not opened.

**Q1 answer:** `PROVIDER_RESOURCE_EXHAUSTED_SUBTYPE_UNRESOLVED`. The 429 occurrence is confirmed. Project/account/daily/per-minute quota exhaustion, rate limiting, shared/model capacity and another specific resource limit cannot be distinguished offline from this body. No quota number or quota adjustment is justified by this evidence.

## 5. Outer error, provider cause and retention boundary

| Information | Evidence class / retention |
|---|---|
| Structured generation, model, location and final 429/status/body text | PERSISTED in the outer message; no observed runner message truncation |
| `VertexCallError` wrapping policy | DERIVABLE_FROM_SOURCE: `vertex.py:197-203` raises the outer error `from last_error`; the class itself has no extra fields |
| SDK provider attributes | DERIVABLE_FROM_SOURCE: local `google/genai/errors.py:44-66` retains `response`, `details`, `message`, `status`, `code`; its exception string includes code/status/details |
| Exact live cause class and object | Not serialized; UNKNOWN after exit. Normal SDK 4xx handling constructs a ClientError, but this record stores only the outer type |
| Response headers, request IDs and other response-object fields | PLAUSIBLE_BUT_UNRECOVERABLE if present; neither presence nor values are established |
| Earlier adapter-attempt exceptions / statuses | UNKNOWN; only final `last_error` survives the adapter wrapper |
| Specific quota/capacity metadata | Not present in the saved body. Do not assert it was available in memory and lost |
| `usage_stage`, request operation or role on the outer exception | Not attached by the current adapter; absent from serialized exception |

`evaluation_finalization.py:84-153` may inspect live `__cause__.code/status` as well as message tokens to classify infrastructure errors. `evaluation_runner.py:1845-1852` then stores only outer type, bounded `str(exc)`, retryable and category. It does not serialize the cause, traceback, response object, headers or individual retry history. The classification is a recovery policy, not proof of the particular resource subtype. Re-reading the record cannot recover an unpersisted live object.

## 6. Retry semantics and SDK multiplier

`vertex.py:162-203` attempts structured generation at most three times; `_record_request` precedes each SDK invocation. A transient failure at attempts 1/2 sleeps 1/2 seconds and continues; a non-transient failure stops early. Therefore a **generic VertexCallError does not necessarily imply all three attempts**.

For these particular errors, the final message contains 429/RESOURCE_EXHAUSTED, which always matches the adapter's transient classifier. An exception with that final cause cannot stop at the first or second adapter iteration under this unchanged source. **DERIVABLE_FROM_SOURCE:** each terminal logical generation operation consumed all three adapter attempts; none returned successfully from `generate_json`. The first two attempts' causes are unknown and need not have been 429. A provider response could also have returned before a local structured-response failure; do not equate every failed adapter iteration with a proven HTTP error.

Embedding permits five adapter attempts with 1/2/4/8-second delays (`vertex.py:230-273`). There is no terminal embedding error in this run. The four single embedding invocations belong to successful query-embedding returns on the uniquely compatible paths below; there is no embedding retry invocation in their counters. This does not establish continuous embedding availability outside these four requests.

The launch report records verified actual client `retry_options=None`; local installed `_api_client.py:525-536` maps None to `stop_after_attempt(1)`. The SDK's separate `_RETRY_ATTEMPTS=5` constant applies to configured retry options, not the None path used here. Thus there is no SDK HTTP retry multiplier in the frozen derivation. No current SDK/client was instantiated to test availability.

**EXACT_TRANSPORT_RETRY_COUNT = UNRESOLVED.** The failed logical operation's three adapter iterations / two retry-loop continuations are source-derived, but there is no raw per-request retry/status receipt. Do not report an exact batch transport-error/retry history or allocate preceding failures to stages by arithmetic alone. Successful earlier logical operations can themselves have consumed multiple adapter attempts.

## 7. Exhaustive persisted usage-counter dimensions

Every `model_call_breakdown.runtime` contains exactly these four keys; all are shown below. Top-level `model_calls/token_usage` and breakdown totals agree with runtime, and every `judge` dictionary is empty.

| ID | generation_calls | embedding_calls | model_calls | token_usage | duration_ms |
|---|---:|---:|---:|---:|---:|
| n008 | 5 | 1 | 6 | 3,783 | 28,595.742 |
| n018 | 6 | 1 | 7 | 3,919 | 24,103.244 |
| n019 | 3 | 0 | 3 | 0 | 17,666.229 |
| n022 | 4 | 0 | 4 | 1,853 | 7,553.873 |
| n025 | 8 | 1 | 9 | 4,260 | 44,779.502 |
| n028 | 8 | 1 | 9 | 3,886 | 41,417.519 |
| Total | 34 | 4 | 38 | 17,701 | 164,116.109 |

No row contains `qa_generation_calls`, `qa_semantic_verification_calls`, `qa_composer_calls` or their token-usage keys. Those fields are **absent, not explicitly stored zero**. That absence is informative under the verified all-role reader:

1. `vertex.py:111-117` creates each supplied usage-stage call key before a request; `stats_snapshot()` returns all Counter keys, not only its four base defaults.
2. Existing QA aggregation sums every key of each distinct client, and runner `_stats_delta` retains the union of before/after keys. Keys are not filtered or reset per case.
3. All actual QA model call sites provide a usage stage: A0/A1 use `qa_generation` (`qa.py:3001`, `3597`); V1/V2 use `qa_semantic_verification` (`3260`); composer/review use `qa_composer` (`3751`, `3782`). An attempted failed request would still create its key.
4. D1 (`question_decomposition.py:146`), initial analyzer (`retrieval.py:1161`) and rerank (`1946`) do not supply a usage stage. Their calls remain only in the base counters.

Consequently A0/A1/V1/V2/composer **provider stages are STAGE_CONFIRMED_NOT_REACHED in all six cases, DERIVABLE_FROM_SOURCE**. This is not based solely on total call counts. No canonical inventory, semantic adequacy or V1 output is recovered by this finding. Positive token metadata establishes some returned provider responses for five cases; zero tokens for n019 does not on its own prove that every request had zero billable usage.

## 8. Compatible execution paths and diagnostic bounds

The source sequence is D1 before graph invocation, then initial analyzer, then query embedding/channel collection, then optional initial rerank; only after retrieval return/sufficiency can the tagged QA stages run. Initial retrieve always calls `_vector`, which calls one query embedding; paper retrieval reuses that vector. A targeted retrieval would require a second embedding before its rerank. E3 is inactive in this production mode; its separate global-rerank call is not a compatible branch. All-role counters exclude tagged QA calls, and the outer exception says generation rather than embedding.

These jointly make the failing **stage** unique for each record. The following are exhaustive adapter-attempt count paths under frozen source, not invented request logs. Let `D(d)` and `A(a)` mean D1/analyzer returning successfully on their d-th/a-th adapter invocation; `E(1)` is one successful query embedding; `R!3` is initial rerank failing after three adapter iterations.

| ID | Compatible paths | Earliest definitely reached | Latest definitely reached / unique failure stage | V1 provider reachability |
|---|---|---|---|---|
| n008 | `D(1) -> A(1) -> E(1) -> R!3` | D1 | Initial rerank | CONFIRMED_NOT_REACHED |
| n018 | `D(1) -> A(2) -> E(1) -> R!3` **or** `D(2) -> A(1) -> E(1) -> R!3` | D1 | Initial rerank | CONFIRMED_NOT_REACHED |
| n019 | `D!3` | D1 | D1; graph not invoked | CONFIRMED_NOT_REACHED |
| n022 | `D(1) -> A!3` | D1 | Initial analyzer; channels/embedding not reached | CONFIRMED_NOT_REACHED |
| n025 | `D(2) -> A(3) -> E(1) -> R!3` **or** `D(3) -> A(2) -> E(1) -> R!3` | D1 | Initial rerank | CONFIRMED_NOT_REACHED |
| n028 | Same two count paths as n025 | D1 | Initial rerank | CONFIRMED_NOT_REACHED |

For the four one-embedding cases, final generation failure cannot be D1/analyzer, since embedding occurs only after both returned. It cannot be targeted rerank, since that requires another embedding, or A0/later QA, since their attempted calls would carry stage keys. Initial rerank is the only remaining source call. Its nonempty rerank pool/channel collection is therefore reached, but selected final evidence and successful retrieval return are not established. For n019, all three generation calls are consumed by the failing first D1 operation. For n022, the three failing analyzer calls leave exactly one successful D1 call and no embedding.

**Q2 answer:** counts differ because cases terminate at different untagged pre-answer operations, and some preceding D1/analyzer operations return after more than one adapter invocation. The allocation for n018/n025/n028 remains unresolved between the listed alternatives, including earlier error codes, request timing, response content and exact transport history. No additional later stage is merely assumed `POSSIBLY_REACHED`; all compatible paths here stop before initial retrieval completion/A0/V1. Failure stage is uniquely source-derived, not a persisted stage label.

This forward diagnosis narrows the execution report's conservative unresolved-stage account using exhaustive counter-key inspection and branch constraints. It preserves every historical receipt and still assigns infrastructure-error reachability under the frozen exception-first taxonomy.

## 9. Timing and persistence during the batch

`run_status` start/end are `2026-10-01T18:30:15.236237+00:00` and `2026-10-01T18:32:59.428269+00:00`: **164.192032 seconds**, approximately 2 minutes 44 seconds. The attempt ledger gives the six-case order; durations above sum to 164.116109 seconds. The reported aggregate difference is approximately **0.075923 seconds**, covering non-case loop/persistence/boundary overhead. Exact individual inter-attempt gaps are not separately recorded and remain UNRESOLVED; no per-provider timestamps or Retry-After values can be inferred.

The timestamp inversion is explained by source: runner `completed_at` is set before entering the case (`evaluation_runner.py:1817`), while store `attempted_at` is added when recording its finished observation (`evaluation.py:2278`). Neither is used as an accurately named provider-attempt timestamp. No provider timing is reconstructed from those fields and no timestamp is rewritten.

Six terminal logical operations end in 429 throughout this ordered execution window: **PROVIDER_429_PERSISTENCE_DURING_BATCH = CONFIRMED** at that bounded observation level. Successful intervening operations show this was not a proven total service outage. The evidence does not establish uninterrupted exhaustion, a global outage, daily/project/account quota, or persistence outside this window.

## 10. Provider diagnosis and historical infrastructure context

Generation-provider blocking is confirmed for the untagged generation-role D1/analyzer/rerank operations using `gemini-3.8-flash` in `global`. Verification-role stages were not reached. Four query embeddings returned successfully for `gemini-embedding-2`; n019/n022 did not reach embedding. An embedding-service blocker is not supported as the terminal cause.

Read-only current non-secret configuration matches the launch report: generation/effective verification `gemini-3.8-flash`, embedding `gemini-embedding-2`, 3072 dimensions, global, timeout 120000 ms. Role separation and retry settings are those of unchanged source and recorded launch verification. No `.env` edit or request-routing change occurred.

Historical exposed stores O (`g5-integrated-candidate-novel-dev-v1`) and S (`g5-n018-separately-authorized-rerun-v1`) completed provider operations and persisted QA/V1 results with the same generation/embedding model IDs, dimensions and recorded package versions. Their prompts/product lineage differ and their historical counters remain generation-client-only. Their manifests do not record private project identity, location or timeout, so exact historical project/region equality is **UNRESOLVED** from those artifacts. No private project identifier is read out or printed. Historical availability does not establish current capacity or require this batch to succeed; no historical quality verdict changes.

## 11. Missing intermediate persistence: confirmed architecture blind spot

**Q3 answer: PERSISTENCE_BLIND_SPOT_CONFIRMED.** The relevant causal chain is:

1. `_run_detailed` creates invocation-local `_QAStageTrace` before D1 (`qa.py:4137-4141`); decomposition and graph run may raise before diagnostics assembly.
2. `_QAStageTrace.record()` copies bounded parsed events/evidence projections into Python memory only (`1879-1963`). `_trace()` records QA events best-effort. It is not a disk writer or exception export. D1 canonical output is a separate local variable, not an existing D1 event in this collector.
3. `self.graph = graph.compile()` has no checkpointer (`2150`). The timed-node wrapper records timing only after a node returns; it supplies no failed-node receipt or incremental persistence. Inspection found no QA file writer, durability callback or failure-path export of the collector.
4. Only after D1, graph invocation and result validation return does `_run_detailed` assemble diagnostics, call collector `finish()` and return the detailed envelope (`4144-4232`). The trace-assembly try/except is after the graph; it does not catch a prior provider failure and cannot salvage its state.
5. `_execute_evaluation_case` waits for that whole return before exposing result/diagnostics (`evaluation_runner.py:959-997`). A thrown VertexCallError unwinds this call before its tuple return.
6. Runner retrieval-trace construction/writing and `record.update(result/diagnostics/metrics)` occur after that return (`1821-1844`), so the exception skips both. Its exception branch stores only error summary; all-role counters are read afterward and the terminal record is persisted.

Thus provider invocations and some successful D1/analyzer/embedding returns coexist with no durable canonical decomposition, analyzer plan, channel/rerank material, QA trace or evidence registry. This is an expected limitation of the current persistence boundary, not run-store corruption or a missing scientific rerun.

For **these six cases**, V1 proof output was not created: the unique source paths fail before V1. The blind spot must not be described as losing an actually completed V1 here. However, the same architecture would discard existing V1_INPUT and any completed V1_OUTPUT/receipt/registry if a **future** invocation throws later, for example during an authorized A1 operation, before full detailed QA return. Composer failures normally fall back locally, so they are not assumed to propagate in that example. Both the present lost pre-answer detail and the possible loss of a completed V1 on later failure are material to a future targeted experiment's interpretability.

## 12. Root-cause confidence table and two-blocker separation

| Candidate cause / finding | Verdict | Evidence | Limitation |
|---|---|---|---|
| Provider 429 occurred | CONFIRMED | Six identical final saved code/status bodies | Final provider errors only |
| 429 persisted across the execution window | CONFIRMED | Six ordered terminal outcomes within 164.192 s | Not continuous outage or global persistence |
| Quota exhaustion | UNRESOLVED | No quota details/metric/limit in saved body | Cannot identify project/account/daily/per-minute quota |
| Rate limiting | UNRESOLVED | No rate metric or rate-specific message | 429 alone does not distinguish this |
| Shared/model capacity exhaustion | UNRESOLVED | No capacity-specific detail | Do not treat the earlier report's generic capacity wording as a confirmed subtype |
| Other specific resource limit | UNRESOLVED | Only RESOURCE_EXHAUSTED | No cause-specific metadata |
| Credential/authentication defect as terminal cause | NOT_SUPPORTED | Saved terminal status is 429, no 401/403 or auth message; preceding operations returned in five cases | Earlier unrecorded failures and future access are not certified |
| Terminal logical generation adapter retry exhaustion | CONFIRMED | Final transient 429 plus unchanged three-iteration loop | Earlier two error causes unknown; exact transport history UNRESOLVED |
| SDK extra HTTP retries | NOT_SUPPORTED | Recorded None options and local SDK one-attempt branch | Not a statement about undocumented network internals/billing |
| Embedding-service blocker as terminal cause | NOT_SUPPORTED | All terminal messages are structured generation; four one-call embedding returns | No availability certification beyond those calls |
| Generation-service blocker | CONFIRMED | Final structured generation failure and source-derived pre-answer paths | Exact resource subtype unresolved; verification role unexercised |
| Product prompt/schema defect as demonstrated cause | NOT_SUPPORTED | No persisted invalid-prompt/schema response; final code is resource exhaustion | Does not certify all prompts/schemas or rule out indirect request-size effects |
| Failed-QA intermediate-persistence blind spot | CONFIRMED | Invocation-local collector; success-only return/persistence; no failure export/checkpointer | No actual completed V1 lost in these six cases |
| V1 provider stage reached in this run | NOT_SUPPORTED | No tagged QA-stage keys under exhaustive all-role accounting; unique pre-answer paths | No recovered semantic inventory/output |

Provider blocker: a structured model operation cannot finish because its final attempt receives resource exhaustion. Observability blocker: failing detailed QA calls do not export completed intermediate state and structured failure context. Better capture cannot provide provider capacity; improved availability alone leaves this capture loss possible on a different late exception.

## 13. What remains unknown

Resource subtype, quota numbers, shared-capacity state, Retry-After/request IDs, private project comparison, individual earlier exception causes, precise transport retry history and provider latency remain unknown. n018/n025/n028 preceding retry allocation has the two compatible paths above. D1 semantic quality, retrieved content, V1 proof compliance and repair benefit cannot be reconstructed. This diagnosis adds no V1 evidence and does not select a new cohort or run identity.

## 14. Proportionate future observability options — design candidates only

| Option | What it would close | Proportionality / limitation |
|---|---|---|
| A: safe VertexCallError context | Terminal operation/usage-stage/role, provider code/status and allowlisted structured details when available | Useful small error receipt; alone cannot preserve an earlier completed V1 proof. Untagged D1/retrieval call sites also need explicit context considered in the future design. Never blindly serialize raw response objects/headers/details. |
| B: full incremental evaluation-stage persistence | Completed state survives later exceptions and potentially process crashes | More invasive than this observed caught-exception need; no new checkpoint/logger subsystem is justified here. |
| B, narrower variant: failure-boundary export of existing bounded state | Export already accumulated QA trace/registry and available decomposition on a caught failure, then use the existing runner/store path | Minimum candidate for preserving earlier V1 observations without per-event disk writes. Distinguish attempted/failed/not-captured from genuinely not-executed; do not manufacture success or replay output. It would not recover a process crash before export. |
| C: minimal stage/role failure marker | Removes ambiguity about the terminal operation | Alone cannot preserve substantive proof/coverage evidence from an earlier V1. |
| D: no capture change | No new engineering | Leaves demonstrated intermediate loss and future late-V1 interpretability risk; insufficient for the requested robust next failure observation. |

Prefer a future **minimal failed-QA observability repair design** centered on the narrow failure-boundary export through existing records, plus the smallest safe operation/provider-error context needed to interpret it. That design should retain original error propagation/classification, bounded collector semantics, all-role accounting, successful-path behavior, prompts/schemas, retries and QA decisions. It should use no new manifest/hash framework, generic logging subsystem or model call. This diagnosis does not authorize implementation or finalize a new runtime receipt schema.

## 15. Minimum next action

**Q4 answer: BOTH_PROVIDER_AND_OBSERVABILITY_BLOCKERS.** The provider constraint is observed but its subtype cannot be differentiated offline. The capture boundary is independently demonstrated and materially reduces both current diagnostic value and future late-failure interpretability. Cases B/C of the authorized recommendation logic therefore select:

```text
NEXT_TASK_RECOMMENDATION = MINIMAL FAILED-QA OBSERVABILITY REPAIR DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

External provider availability remains an independent prerequisite for any later live attempt; this evidence does not justify increasing quota, changing model/region or issuing probes. After any separately authorized design/repair and external blocker resolution, a future attempt would require a separately authorized **new forward protocol and run identity**. The closed original run must not be resumed or replaced. No such future identity, request or implementation is created now.

## 16. Boundaries, validation and lifecycle

Only this diagnosis and the two authoritative current-state sections change. The execution/design/implementation records, product/source/tests/configuration/prompt/schema/data/dependency files and every existing raw run artifact remain unchanged. Static local artifact/source inspection and `git diff --check` validate this documentation scope; no pytest or scientific evaluation is performed. PASS means diagnosis delivery complete, not provider recovery or a targeted mechanism pass.

```text
G5_TARGETED_PROVIDER_429_BLOCKER_DIAGNOSIS = COMPLETE / PASS / BOTH_PROVIDER_AND_OBSERVABILITY_BLOCKERS
PROVIDER_429_OBSERVATION = CONFIRMED
PROVIDER_429_PERSISTENCE_DURING_BATCH = CONFIRMED
PROVIDER_429_RESOURCE_SUBTYPE = PROVIDER_RESOURCE_EXHAUSTED_SUBTYPE_UNRESOLVED
FAILED_QA_INTERMEDIATE_PERSISTENCE_BLIND_SPOT = CONFIRMED
TARGETED_V1_PROVIDER_STAGE = CONFIRMED_NOT_REACHED
EXACT_TRANSPORT_RETRY_COUNT = UNRESOLVED

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

HISTORICAL_TARGETED_LIVE_RUNS = 1
HISTORICAL_LOGICAL_CASE_ATTEMPTS = 6
HISTORICAL_SCIENTIFIC_PROVIDER_INVOCATIONS = 38
HISTORICAL_SCIENTIFIC_TOKENS_AVAILABLE_METADATA = 17701

G5_POST_V1_TARGETED_LIVE_VERIFICATION_DESIGN = COMPLETE / CORRECTED / EXECUTION_READY
TARGETED_LIVE_EXECUTION = EXECUTED / SIX ATTEMPTS / SIX INFRASTRUCTURE ERRORS / INCOMPLETE
TARGETED_LIVE_EVIDENCE_CLASS = EXPOSED_TARGETED_MECHANISM_EVIDENCE
TARGETED_V1_VERDICT = TARGETED_V1_VERIFICATION_INCOMPLETE
TARGETED_V1_PROMPT_MECHANISM = NOT_ESTABLISHED
REAL_PROVIDER_CONTRACT_COMPLIANCE = NOT_ESTABLISHED / NO ASSESSABLE V1 OUTPUT
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = MINIMAL FAILED-QA OBSERVABILITY REPAIR DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
