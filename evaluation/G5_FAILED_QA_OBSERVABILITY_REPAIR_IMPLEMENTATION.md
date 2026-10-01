# G5 Minimal Failed-QA Observability Repair Implementation

## 1. Status and authorized scope

**PASS / COMPLETE / DETERMINISTIC VERIFICATION PASS.** Implemented the frozen [failure-boundary design](G5_FAILED_QA_OBSERVABILITY_REPAIR_DESIGN.md), with fake-only RED/GREEN and relevant existing controls. This is evaluation capture repair, not provider recovery or scientific V1 verification.

Entry was clean `main` at `fb11e5e54cdfac96f657a62427d892680c30db73`, message `Design failed-QA observability repair`. Delivery is the normal commit `Preserve failed QA partial diagnostics`; resolve its exact SHA from Git history and the delivery report. Product behavior lineage remains `5b9588ec552deb91a59a8176d6ce0429c2133b1e`; no push.

Source inspection matched the design assumptions; no scope redesign was needed. Only qa.py, evaluation_runner.py, the new focused fake test module, this report and the two current-state documentation sections change. Frozen design/diagnosis/execution reports, historical chronology and raw scientific stores remain unchanged.

## 2. Actual pre-edit RED

Before source editing, the new focused module ran this PowerShell command:

```powershell
& '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_g5_failed_qa_observability.py -k 'test_b_d1_failure or test_e_v1_provider_failure or test_f_late_a1_failure_preserves_v1'
```

**3 failed / 0 passed.** Each failed with `KeyError: 'failure_diagnostics'` on its persisted fake exception record. B failed after one actual fake D1 attempt, E after an actual distinct-role V1 fake call, and F after an actual authorized A1 fake call following first-pass V1. Existing exception classification and unscored behavior already held; the missing partial-state export was the RED cause. None unexpectedly passed. No test was weakened or fixture/assertion corrected to manufacture RED.

## 3. Exact implementation and source boundaries

Selected repair remains `CAPTURE_SCOPED_FAILURE_BOUNDARY_PARTIAL_DIAGNOSTICS_EXPORT`.

| File | Change |
|---|---|
| `src/panda_agent/qa.py` | Add bounded JSON export/copy and fixed envelope validation, failure snapshot, envelope assembly and QADetailedExecutionError; guard supported-mode detailed execution only for optional failure export. |
| `src/panda_agent/evaluation_runner.py` | Recognize the dedicated wrapper in the existing exception branch, classify/serialize original_exception and best-effort copy optional failure_diagnostics; duration/accounting/store flow unchanged. |
| `tests/unit/test_g5_failed_qa_observability.py` | 48 neutral fake tests spanning the frozen A-L matrix, with temporary stores and explicitly verified test-only all-role reader. |
| This report | Implementation, evidence, scope and limitations. |
| `docs/EVALUATION_STATUS.md`, `docs/GENERALIZATION_ROADMAP.md` | Current implementation state and forward next recommendation; previous checkpoints/chronology retained. |

No edits to retrieval, decomposition, Vertex adapter, finalization/classifier, EvaluationRunStore, prompts/provider/public schemas, CLI, dependencies, data, Gold or calibration. Default runner generation-only stats reader remains unchanged; no all-role accounting redesign.

## 4. Failure snapshot and decomposition

`_QAStageTrace.snapshot_on_failure()` returns detached parsed JSON observations with INCOMPLETE status, existing failure codes plus QA_EXECUTION_FAILED, original event order and original projection keys. It keeps CAPTURED/NOT_CAPTURED observations only, excluding top-level NOT_EXECUTED placeholders that successful finish might have inserted before a late return-assembly fault. Internal captured bypass/fallback fields remain intact. The method does not call finish(), mutate the collector, infer attempts, invent stages/output or trim scientific text.

The original canonical local decomposition is preserved when D1 returned successfully and its export fits. D1 failure yields null / DECOMPOSITION_UNAVAILABLE; a mode without D1 yields null / DECOMPOSITION_NOT_APPLICABLE. Oversize or copy failure yields null with the corresponding fixed code, without truncating points, relations, spans or ambiguity. No reconstruction, revalidation of partial proposals or second model call.

Failure envelope has exactly five keys: schema_version=`qa-failure-diagnostics-v1`, capture_status=INCOMPLETE, failure_codes, question_decomposition, qa_stage_trace. Codes are unique, allowlisted, at most 8 and include QA_EXECUTION_FAILED; decomposition-unavailability reasons are mutually exclusive. The nested trace remains qa-stage-trace-v1, including its existing minimal incomplete fallback form.

## 5. Exception transport, runner and isolation

QADetailedExecutionError retains the exact original Exception object and safe partial envelope, and is raised from that original. It does not mutate original __cause__ or recursively unwrap SDK causes. Runner uses original_exception for the unchanged classifier, type name, `str(original)[:2000]`, retryable and category. The transport wrapper's type/message is never the saved effective scientific failure.

The capture-enabled guard covers setup, D1, graph, result validation, diagnostics/finish and return/model-usage assembly. Unsupported-mode validation remains outside. It catches Exception, not KeyboardInterrupt/SystemExit. Capture disabled re-raises the exact original object; public run/run_detailed remain unchanged.

Collector/snapshot/decomposition failures have isolated fixed-code/minimal-trace fallbacks where possible. Complete envelope or wrapper construction failure re-raises the original from its enclosing exception context. Runner optional-payload failure omits failure_diagnostics after preserving the original exception fields. Real store I/O remains outside this best-effort guard and still propagates.

## 6. Durable record and compatibility

The sole additive field is optional `record["failure_diagnostics"]`. Failed QA invocations do not produce result, diagnostics or metrics. No deterministic metrics, judge, retrieval-trace build or sidecar write occurs after failed detailed QA. Exception-first state, retryability, scored exclusion, cohort decision and RECOVERY_PENDING semantics are unchanged.

The critical F test uses the actual runner handler and actual temporary EvaluationRunStore. Identical optional diagnostics survive attempts.jsonl, records/synthetic-failure.json and results.jsonl. A legacy record without the field is also written and loaded successfully, and produces the same classifier/cohort/aggregate semantics. No migration/backfill or historical raw-store change.

Successful no-revision and one-revision records contain no failure field. Successful captured traces retain normal finish placeholders; only failure snapshots omit them. Composer generation/review faults still yield ordinary successful fallback. A fault after detailed QA has returned, or a disk/process failure, remains outside this export repair's guarantee.

## 7. Hard bounds and payload safety

| Bound / invariant | Observed fake verification |
|---|---|
| 16 events | Extra record attempts remain bounded; failure snapshot preserves existing bound codes. |
| 2,097,152-byte trace | An exact-cap existing trace falls back to minimal TRACE_SIZE_BOUND_EXCEEDED when failure metadata pushes it over; original collector unchanged. |
| 65,536-byte decomposition | Exact boundary preserves the whole object; one-byte excess omits it. |
| Multibyte UTF-8 | A string below the character threshold but over the byte cap is omitted with DECOMPOSITION_SIZE_BOUND_EXCEEDED. |
| 2,166,784-byte envelope | Bounded encoder accepts its exact serialization limit and rejects one-byte excess; runner rejects oversized optional payloads. |
| JSON safety | Non-JSON objects and NaN cannot become durable diagnostics. |
| Copy isolation | Later mutation of original events, projection evidence and decomposition cannot change exported copies. |
| Projection closure | Prior V1 evidence references resolve without renaming or duplicate retrieval export; malformed unresolved references are rejected by runner copy validation. |

Serialization uses ensure_ascii=False, sort_keys=True, allow_nan=False and stops retaining chunks when their UTF-8 total exceeds the cap. The payload copy validator enforces the five-field contract, code/status consistency, bounded trace/decomposition and reference closure. It adds no generic logging/validation subsystem. No raw exception/SDK object, headers, stack trace, environment, credentials or full Retriever internals are exported.

## 8. Post-edit commands and exact counts

All tests are deterministic fakes/local contracts. No scientific provider calls or protected access. Exact commands below use the sibling project venv:

```powershell
& '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_g5_failed_qa_observability.py
& '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_post_a5_o1_observability.py
& '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_post_a3_execution_recovery.py
& '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_post_a3_finalization_contract.py
& '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_qa.py
& '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_g5_failed_qa_observability.py -k 'success_record_no_failure_fields or capture_construction_preserves_exact_original or root_cause_classification_and_legacy_record'
```

| Verification | Actual result / distinct count |
|---|---|
| First post-edit focused run (then 3 tests) | 3 passed, core RED cases GREEN. |
| Expanded focused module | 44 passed, 0 failed. |
| Final focused delta | 5 passed / 43 deselected: four added successful-record/exact-original cases and one augmented legacy round-trip case. |
| Final focused module distinct tests | **48 passed** across the above commands, no failed post-edit case. |
| Existing O1 | **45 passed**. |
| Existing execution recovery | **25 passed**. |
| Existing finalization contract | **27 passed**. |
| Existing QA execution | **210 passed**, plus **25 subtests passed**. |
| Total distinct post-edit pytest items | **355 passed / 0 failed**, plus 25 QA subtests; repeated core/legacy executions are not counted twice. |

No fixture/assertion correction was needed; source additions/guard refinements implement the frozen contract. The initial three tests were rerun by the required expanded matrix, and the augmented legacy case was checked again with the final new cases. Unchanged successful regression modules were not rerun; no full repository suite was run.

## 9. Frozen matrix results and critical scientific acceptance

A through L passed: successful no/one revision; transient/semantic D1; post-D1 analyzer/rerank fault injection; actual A0/V1/A1/V2 fake calls; capture-component/whole-envelope/wrapper/runner-copy faults; capture-disabled public/internal propagation; size/JSON/alias/ref limits; actual runner/store/recovery compatibility; late assembly and composer controls. B/E/F fail before editing for the intended missing-field reason and pass afterward.

Critical F uses valid first-pass V1 with a genuine backed missing point authorizing A1. The actual generation-role A1 fake call throws. The stored record retains **V1_INPUT, V1_OUTPUT, host validation ACCEPTED, exact resolvable evidence projection material and A1_INPUT**; A1_OUTPUT is absent. Its exception remains authoritative, retryable infrastructure classification is preserved, and scored_cases is zero. This demonstrates prior V1 observation durability after a later escaping fault **with fakes**, not empirical V1 correctness.

Existing V1 trace holds raw parsed proof declarations and captured validation summary, not the entire private coverage receipt. Tests inspect the existing basis quotes against projected input evidence; no extra receipt/model response is fabricated. Event absence still means not captured; attempted/unexecuted distinctions require independently adequate counters/path evidence. The A0 fixture explicitly counts before its fake provider fault and shows no later verification calls under the verified fake all-role reader.

## 10. Static review and identity

Local AST comparison against entry HEAD confirms existing definitions changed only QAAgent._run_detailed and run_evaluation. Every other existing QA/trace/counter/fingerprint/runner function remains AST-identical. The guarded successful execution body is AST-identical after moving safe local defaults; model-operation call sites, schemas, prompts, retrieval/coverage/A1/V2/composer logic are unchanged. git diff --check passes and the exact six-file scope is reviewed before commit.

```text
PRODUCT_SOURCE_CHANGE = true
TEST_CHANGE = true
MODEL_FACING_BEHAVIOR_CHANGE = false
PUBLIC_QA_RESULT_SCHEMA_CHANGE = false
MODEL_FACING_SCHEMA_CHANGE = false
PROVIDER_SCHEMA_CHANGE = false
PROMPT_SCHEMA_CHANGE = false
INTERNAL_EVALUATION_RECORD_SHAPE_CHANGE = ADDITIVE_OPTIONAL_FAILURE_DIAGNOSTICS
PROMPT_CHANGE = false
PROMPT_FINGERPRINT_CHANGE = false
QA_ANSWER_SEMANTICS_CHANGE = false
PROVIDER_CALL_SEQUENCE_CHANGE = false
PRODUCT_BEHAVIOR_LINEAGE_CHANGE = false
CURRENT_PRODUCT_BEHAVIOR_LINEAGE_HEAD = 5b9588ec552deb91a59a8176d6ce0429c2133b1e
PROMPT_SET_VERSION = 3.12.1
PROMPT_FINGERPRINT = 08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc
```

The prompt fingerprint was checked by focused/unchanged O1 controls; no per-file hash/manifest layer was added. Repository HEAD advances normally; this capture-only implementation retains product-answer lineage under the frozen design and O1 precedent.

## 11. Scientific limits and boundary receipt

The repaired scope is capture_stage_trace=True, an escaping Exception, process still alive and runner reaching normal exception-record persistence. Bounded/copy failures can still make some/all optional state unavailable, and no failed output is recoverable when it never existed. No crash durability, provider availability, 429 subtype resolution or precise retry-history recovery is claimed.

The historical six cases still failed before A0/V1; no completed V1 was lost there. Their missing V1 is not retroactively repaired or reclassified. Better future capture neither makes requests succeed nor grants permission to resume the closed run. Metrics are deterministic contract assertions, not before/after scientific QA effectiveness measurements.

```text
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

Fake calls/accounting and temporary stores are test fixtures, not scientific runs/attempts. No targeted identifiers were used as fixtures, no provider probe/health check/rerun/resume occurred, and no model/region/quota/configuration/dependency change was made after GREEN.

## 12. Current lifecycle and next recommendation

```text
G5_FAILED_QA_OBSERVABILITY_REPAIR_DESIGN = COMPLETE / IMPLEMENTATION_READY
G5_FAILED_QA_OBSERVABILITY_REPAIR_IMPLEMENTATION = COMPLETE / DETERMINISTIC VERIFICATION PASS
FAILED_QA_PARTIAL_DIAGNOSTICS_EXPORT = DETERMINISTICALLY_VERIFIED
LATE_FAILURE_PRESERVES_PRIOR_V1_TRACE = DETERMINISTICALLY_VERIFIED_WITH_FAKES
FAILED_QA_INTERMEDIATE_PERSISTENCE_BLIND_SPOT = REPAIRED_FOR_CAPTURE_SCOPED_ESCAPING_EXCEPTIONS
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
NEXT_TASK_RECOMMENDATION = G5 POST-OBSERVABILITY-REPAIR TARGETED LIVE VERIFICATION FORWARD-PROTOCOL DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

Next is a separately authorized forward-protocol design addressing independent external provider availability, a new run identity, a new one-attempt protocol and new explicit authorization. It is not started here. The closed historical targeted run must not be resumed.
