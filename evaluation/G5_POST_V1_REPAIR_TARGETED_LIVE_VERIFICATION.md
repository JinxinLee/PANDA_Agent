# G5 Post-V1-Repair Targeted Live Verification Execution

## 1. Decision and scope

**INCONCLUSIVE / TARGETED_V1_VERIFICATION_INCOMPLETE. Frozen Rule 4 fired.** The separately authorized, single runner invocation attempted all six frozen cases in order. All six produced saved `VertexCallError` infrastructure observations ending in `429 RESOURCE_EXHAUSTED`; none returned a persisted QA result or V1 target observation. The required primary/control observations are therefore errored and not assessable. No primary semantic veto or control regression can be established from absent output. No protocol-invalid condition was detected.

Execution is finished for this one-attempt protocol. The generic runner labels the six exceptions retryable and its status `RECOVERY_PENDING`; those raw labels remain unchanged, but they do **not** authorize resuming this frozen experiment. No rerun, replacement, second runner invocation, health-check request, external judge or further provider call was made.

Authority: the [corrected targeted-live design](G5_POST_V1_REPAIR_TARGETED_LIVE_VERIFICATION_DESIGN.md), the user's explicit authorization of launch HEAD, six cases, 240-invocation bound and process-local all-role accounting binding; [V1 repair design](G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_DESIGN.md), [implementation](G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_IMPLEMENTATION.md), [failure-family review](G5_INTEGRATED_FAILURE_FAMILY_REVIEW.md), [D1 implementation](G5_D1_DIAGNOSTIC_METADATA_ROBUSTNESS_REPAIR_IMPLEMENTATION.md), [original G5 report/result](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION.md) and [separate n018 report/result](G5_N018_SEPARATELY_AUTHORIZED_RERUN.md). Historical results are not replaced.

All new observations are `EXPOSED_TARGETED_MECHANISM_EVIDENCE`. This infrastructure-limited execution does not establish provider contract compliance, repair efficacy, answer recovery, fresh generalization, release readiness, original G5 completion or G6 readiness.

## 2. Repository and execution identity

| Field | Actual |
|---|---|
| Starting / launch repository HEAD | `e313ea77a27ce23eeb475ec3889111635de184dd` |
| Launch message / branch / tree | `Correct targeted V1 control semantic baseline` / `main` / clean |
| Product behavior lineage | `5b9588ec552deb91a59a8176d6ce0429c2133b1e` |
| Previous product lineage | `cd0a65df7576a736e83fdfe3da5998b766173ffc` |
| Normal product mode | `production_answer_obligations_v1` |
| Prompt set / fingerprint | `3.12.1` / `08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc` |
| Question decomposition | Prompt `3.0.0`; schema `e1.question_decomposition.v3` |
| Coverage schema / provenance contract | `coverage-satisfaction-v2` / `ALL_TO_ALL_CHECK_PROOF_BASIS` |
| Run ID / mode / split | `g5-post-v1-repair-targeted-live-v1` / `qa` / `novel_dev` |
| Dataset | `evaluation/novel/v1/novel_dev.yaml`; `novel-v1-dev-0.3.0` |
| Dataset identity from existing manifest facility | `25ad18fcf76ab2796aa18ae961bdc4faf076f0c98a8a5226413ec95e58252223` |
| Frozen order, also actual attempt-ledger order | `n008, n018, n019, n022, n025, n028` |
| Selection | Primary `n022/n025/n028`; supplemental `n018`; controls `n008/n019` |
| Runner settings | `allow_draft=true`, `official=false`, `resume=false`, `limit=None`, `candidate_id=None`, `capture_stage_trace=true` |
| Runner caps | `max_model_calls=240`, `max_token_usage=None`, `deadline_minutes=None` |
| Runner attempt start / end (UTC) | `2026-10-01T18:30:15.236237+00:00` / `2026-10-01T18:32:59.428269+00:00` |
| Execution delivery commit | `Run targeted post-V1 live verification`; resolve exact SHA from Git history, reported on delivery |
| Push | Not performed |

The diff from product lineage to launch HEAD contained only the targeted design and the two current-state documents. No source/tests/configuration/data changes followed that lineage. Active prompt identity was computed through `evaluation_runner.prompt_fingerprint()`, not a new identity system.

## 3. Read-only preflight

**PASS before the first scientific request.** The designated run directory was absent; repository identity was exact and clean; filtering the frozen dataset with the runner's selector returned the frozen order. Selected raw questions matched historical retrieval-trace `raw_question` bytes.

| Environment / effective setting | Observed frozen value |
|---|---|
| Interpreter | `C:\Users\Jinxin.DESKTOP-H6SSTQH\Desktop\Agent_learn\.venv\Scripts\python.exe` |
| Python | `3.12.14` |
| langgraph | `1.2.10` |
| qdrant-client | `1.15.1` |
| google-genai | `2.13.0` |
| psycopg | `3.3.4` |
| panda-research-qa-agent | `0.1.0` |
| Generation / effective verification models | `gemini-3.8-flash` / `gemini-3.8-flash` |
| Role paths | Actual QAAgent had two distinct clients; existing generation alias retained |
| Embedding / dimensions | `gemini-embedding-2` / `3072` |
| Vertex location / timeout | `global` / `120000 ms` |
| max_targeted_retrievals | `1` |
| Adapter retry maxima / SDK HTTP attempts | Structured `3`, embedding `5`; default SDK `retry_options=None`, one HTTP attempt |

Existing repository `.env` loading was used with dotenv; no credentials or project secrets were printed. No provider health check, installation, environment change, dependency repair, index rebuild or model switch occurred. Configuration matching does not establish available provider capacity; the actual run subsequently encountered 429 responses.

`build_evaluation_manifest()` performed the existing database index-identity compatibility check. Its source manifest, normalized corpus/output identities, index fingerprint/payload, embedding identity/dimensions, retrieval-policy and query-expansion identities, dataset hash/version and audit-resolution identity matched both original G5 and separate n018 manifests. Relevant existing identities were:

- Source / normalized manifest: `9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94`.
- Index: `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`.
- Retrieval policy: `fb2cd99bf500d5924931cf0fa6d5ea801efc7939b4c469fad8fbc0b5b082ced9`.
- Query expansion: `84c93c94e70e8e7819a2cd8ecdd18f8fce41996d616d5ebc34fe2deb823e039a`.

All selected historical records, retrieval traces and embedded V1 evidence registries existed. Original G5 n018 had its error record and **no** retrieval trace; separate n018 supplied only its separately authorized V1 comparison. No missing original semantics were reconstructed. Protected datasets/outcomes were not opened.

Two orchestration-only inspection mistakes were corrected before scientific execution: a historical record was initially assumed to have a `query` key (the authoritative field is retrieval-trace `raw_question`), and an unnecessary `RetrievalPolicies` import was removed (the module exposes `load_retrieval_policies`). Neither issued a scientific request or changed the repository/environment. There was exactly one subsequent runner invocation.

## 4. Accounting binding and invocation reconciliation

For this process only, `evaluation_runner._stats_snapshot` was bound to a reader that returned existing `QAAgent._stats_snapshot()` for QA engines and retained the original reader for Retriever engines. No clients, prompts, graph, retries or QA state were replaced or changed; no helper/source file was added. The original function was restored in `finally` after the runner returned.

Before the first request, the reader verified the actual QAAgent's two distinct role clients, matching model settings and disabled SDK retry multiplier; compared its aggregate against the sum of each distinct client's counters exactly once; verified zero initial calls and the one-pass retrieval bound. Every runner before/after read used that aggregate. Per-case deltas were independently reconciled and checked against 30 generation / 10 embedding / 40 total, with cumulative total checked against 240. Every case and the total remained within bounds. This is accounting instrumentation, not an intra-case hard limiter or a product repair.

| Case, in attempt order | Logical attempts | Generation invocations | Embedding invocations | Total invocations | Available token metadata | Exact transport-retry count |
|---|---:|---:|---:|---:|---:|---|
| n008 | 1 | 5 | 1 | 6 | 3,783 | UNRESOLVED |
| n018 | 1 | 6 | 1 | 7 | 3,919 | UNRESOLVED |
| n019 | 1 | 3 | 0 | 3 | 0 | UNRESOLVED |
| n022 | 1 | 4 | 0 | 4 | 1,853 | UNRESOLVED |
| n025 | 1 | 8 | 1 | 9 | 4,260 | UNRESOLVED |
| n028 | 1 | 8 | 1 | 9 | 3,886 | UNRESOLVED |
| **Total** | **6** | **34** | **4** | **38** | **17,701** | **UNRESOLVED** |

Counters include failed adapter invocations across both generation and verification roles. Tokens are the response metadata actually recorded; absent usage on failed requests is not proof of zero billable usage. Per-operation entry/response receipts were not persisted for the failed detailed QA invocations, so precise retry counts and failed stage cannot be recovered merely from aggregate calls. Existing adapter retries are within each single logical case attempt; no extra logical attempts occurred.

Historical O/S accounting remains **generation-client-only** where applicable. Its missing verification-role usage is not retroactively estimated or certified. Historical selected counters (generation + embedding) were n008 5+1, n019 6+1, n022/n025/n028 and separate n018 4+1. Comparing those historical counters numerically with new all-role totals is not a cost-improvement measurement.

## 5. Raw persistence and runner diagnostics

Run store: `data/evaluation/runs/g5-post-v1-repair-targeted-live-v1/`, using existing `EvaluationRunStore`. Preserved normal artifacts: `manifest.json`, `attempts.jsonl`, `results.jsonl`, six `records/<ID>.json`, `run_status.json`, `metrics.json`, generic gate files and runner `report.md`. Repository convention ignores these raw stores; they remain local, with durable observations/locators summarized in this committed report. No historical directory was overwritten, and no parallel storage framework was created.

All six records contain `exception.category=transport_provider_infrastructure`, `type=VertexCallError`, `retryable=true`, ending in structured generation `429 RESOURCE_EXHAUSTED` for `gemini-3.8-flash` in `global`. This is a provider capacity observation, not evidence of a validator or prompt defect. The batch continued after each ordinary saved exception, as authorized; no global stop was raised and `stop_reason=null`.

The exception records contain no `result`, `diagnostics.qa_stage_trace`, evidence registry, V1 raw output/receipt or retrieval trace sidecar. The runner saves these only after the detailed QA invocation returns. Consequently an internal stage may have been entered without a persisted response; neither absence of a trace nor a plausible call count establishes which stage failed. No stage was replayed to reconstruct missing material.

Runner diagnostics, retained verbatim in the store:

- `status=recovery_pending`, `cohort_status=INCOMPLETE`, `official_decision=RECOVERY_PENDING`.
- `scored_case_count=0`, `expected_case_count=6`; six retryable exception IDs; no missing or extra case record; `completed_ids=[]` under the runner's successful/terminal-nonretryable convention.
- Formal and development generic gates `passed=false`; product-language gate `compatible=false`, `passed=null`, because its calibration Gold version does not match this draft novel dataset. These generic gate predicates do not define this frozen mechanism verdict.
- Per-case record timestamps have `completed_at` earlier than `attempted_at`, with the field interval approximately matching the recorded case duration. Preserve this existing runner artifact limitation. Use the attempt ledger for order and `run_status` start/end for batch chronology; do not use the inverted per-record fields to infer stage timing.

Protocol accounting: six attempted and terminal-for-this-protocol infrastructure observations, zero completed QA results, zero unattempted IDs, zero resumes. `RECOVERY_PENDING` does not supersede the explicit one-attempt/no-resume rule.

## 6. Per-case mechanism and downstream observations

`NOT_ASSESSABLE` below denotes absent persisted proof, not an empty or invalid declaration. No new V1 reason code is observed. The saved error code is the provider's `429 RESOURCE_EXHAUSTED`.

| Case / role | Historical V1 family | Reachability | New provenance / V1 codes | Semantic interpretation | Coverage / A1 / V2 | Final QA result |
|---|---|---|---|---|---|---|
| n008 / control | ACCEPTED; shared-basis multi-supporter ordinary + canonical paths | INFRASTRUCTURE_ERROR | NOT_ASSESSABLE; no V1 receipt/codes | CONTROL_SEMANTIC_COMPARABILITY_UNRESOLVED | No persisted coverage, revision targets, A1/V2 execution or full-inventory receipt; UNRESOLVED | Exception; no QA result |
| n018 / supplemental | Separate run INVALID_SUPPORTER citation closure | INFRASTRUCTURE_ERROR | NOT_ASSESSABLE; no V1 receipt/codes | SEMANTIC_COMPARABILITY_UNRESOLVED | Same capture limitation; UNRESOLVED | Exception; no QA result |
| n019 / control | ACCEPTED; multi-basis ordinary + canonical paths, literal CRLF | INFRASTRUCTURE_ERROR | NOT_ASSESSABLE; no V1 receipt/codes | CONTROL_SEMANTIC_COMPARABILITY_UNRESOLVED | Same capture limitation; UNRESOLVED | Exception; no QA result |
| n022 / primary | BAD_QUOTE formatting | INFRASTRUCTURE_ERROR | NOT_ASSESSABLE; no V1 receipt/codes | SEMANTIC_COMPARABILITY_UNRESOLVED | Same capture limitation; UNRESOLVED | Exception; no QA result |
| n025 / primary | INVALID_SUPPORTER citation closure, ordinary inventory | INFRASTRUCTURE_ERROR | NOT_ASSESSABLE; no V1 receipt/codes | SEMANTIC_COMPARABILITY_UNRESOLVED | Same capture limitation; UNRESOLVED | Exception; no QA result |
| n028 / primary | INVALID_SUPPORTER citation closure, canonical exposure relation | INFRASTRUCTURE_ERROR | NOT_ASSESSABLE; no V1 receipt/codes | SEMANTIC_COMPARABILITY_UNRESOLVED | Same capture limitation; UNRESOLVED | Exception; no QA result |

For every case, point/relation completeness, valid-sibling containment, `revisionable_relationships`, revisionable unsupported claims, A1 authorization/execution, V2 execution/full original inventory, revision count, retained/excluded claims and composition/fallback behavior are **UNRESOLVED / NOT PERSISTED**. There is no final `answered` or `insufficient_evidence` observation. Do not report absent A1/V2 receipts as proof those stages never executed, or provider failure as semantic regression.

Raw new record pointers are `data/evaluation/runs/g5-post-v1-repair-targeted-live-v1/records/{n008,n018,n019,n022,n025,n028}.json`; `exception` and `model_call_breakdown.runtime` provide the saved observations and usage. Historical proof pointers remain the corresponding O/S `records/<ID>.json::diagnostics.qa_stage_trace.events[V1_INPUT/V1_OUTPUT]` plus evidence registry and `traces/<ID>.json::raw_question`.

### Historical-to-new proof declarations

Let `O=data/evaluation/runs/g5-integrated-candidate-novel-dev-v1` and `S=data/evaluation/runs/g5-n018-separately-authorized-rerun-v1`. IDs are local to those historical realizations, never forced into this run. There is no new proof declaration to compare; all new basis/quotes/supporters are **NOT PERSISTED**, not a smaller successful proof.

| Case / historical store | Historical target basis IDs | Historical target supporters | New basis / quotes / supporters |
|---|---|---|---|
| n008 / O | Ordinary identity and canonical comparison both use `evidence.81899e455750bec5144ebcbe` | Identity `[claim.1]`; comparison `[claim.2, claim.3]` | NOT PERSISTED |
| n018 / S | `point.2.rel.1`: `evidence.0e87ee452eca4d3f8a836620`, `evidence.aef1029b460a3b22035622ff` | `[claim_full_tree_mctruthmatch, claim_tree_match_preparation]`; preparation lacks first basis citation | NOT PERSISTED |
| n019 / O | Input/fitter/hypothesis checks: `evidence.e64e35c449c930169a1ec1bb`, `evidence.92ec891ad49c1be0b86d0dbc`; persisted-result check: `evidence.92ec891ad49c1be0b86d0dbc`, `evidence.244a1832474013c70565536f` | Respectively `[claim_1]`, `[claim_2]`, `[claim_3]`, `[claim_4]`; three quote declarations contain literal CRLF | NOT PERSISTED |
| n022 / O | `point.1.rel.1`: `evidence.a152b9210e11fce51b717112` | `[claim_1]`; submitted full quote removes backticks around `ana_dpm.C` | NOT PERSISTED |
| n025 / O | Efficiency ordinary check: `evidence.a663a0e2c5fc6797b863c488`, `evidence.1b1c6c7f25d05af9ea662bd5`; combinatorics sibling uses `evidence.290b6e9b34847abb5fcc3836` | Efficiency `[claim.1, claim.3]`, claim.1 lacks second basis citation; sibling `[claim.1, claim.2]` | NOT PERSISTED |
| n028 / O | `point.2.rel.1`: `evidence.5aec65f04ec751097c07fbd4`, `evidence.e50ba941687f3ad1f64ff9d6` | `[claim.2, claim.3]`; claim.2 lacks first basis citation | NOT PERSISTED |

Historical exact quote bodies and citation edges remain in their immutable raw authorities and the V1 design analysis. No new quote-membership or witness-adequacy comparison is possible. Absence of BAD_QUOTE/INVALID_SUPPORTER in an exception record is not disappearance of the historical failure family.

## 7. Primary audit

The absolute gate remains `V1_TARGET_OBSERVED + PROVENANCE_VALID + NO_SEMANTIC_EVASION_OBSERVED` with nonvacuous comparable proof. n022, n025 and n028 are each **not a positive primary / NOT_ESTABLISHED** because none has an adequate persisted target observation. No smaller-basis success, truthful unsatisfied disposition or semantic evasion is established. The fixed denominator is 3; the assessable primary denominator is 0 and observed positive count is 0. This is missing measurement, not a measured 0/3 mechanism failure.

## 8. Control audit

Primary semantics stay absolute; control semantics remain regression-relative with absolute valid provenance required.

| Control field | n008 | n019 |
|---|---|---|
| Historical semantic baseline | Algorithm identity and comparison, including TF/CA and multiplicity tradeoffs. Historical low-hit/finer quantitative omissions do not create new Gold-derived numerical obligations. | Raw question requests input PndTrack to fitted output, fitter selection, hypothesis and construction of each persisted result. D1 represents four requests; A0 omits actual Exec construction, V1 accepts 4/4, final answer remains incomplete. This predates the provenance repair. |
| New absolute semantic observation | No persisted QA semantic realization; adequacy/incompleteness UNRESOLVED | No persisted QA semantic realization; persistence, improvement or worsening of the historical construction limitation UNRESOLVED |
| Regression-relative class | CONTROL_SEMANTIC_COMPARABILITY_UNRESOLVED | CONTROL_SEMANTIC_COMPARABILITY_UNRESOLVED |
| Provenance status | NOT_ASSESSABLE; neither valid nor a demonstrated regression | NOT_ASSESSABLE; neither valid nor a demonstrated regression |
| Clean for this experiment? | No: assessability/validity/resolved interpretation not established | No: assessability/validity/resolved interpretation not established |

The n019 historical limitation remains visible and acknowledged. Its persistence alone would not veto this targeted provenance control, and a future unchanged-limitation classification would not certify semantic recovery. This run supplies no new answer with which to decide persistence or additional underchecking. No control is silently marked clean, and no absent control observation is labeled a new semantic/provenance regression.

## 9. Supplemental n018, explicitly non-gating

The new n018 is one infrastructure exception with no persisted D1 diagnostic/semantic inventory, V1 declaration/receipt, coverage or final QA result. D1 fallback exercise, semantic validity and downstream behavior are not established. Its provider response tokens do not reconstruct missing semantics.

The original G5 n018 D1 error and missing original trace remain unchanged. S remains the separate historical V1 comparison, with its citation-closure failure and incomplete preparation account. No merge or replacement is made. n018 never enters the primary denominator or control gate; its failure does not independently determine the experiment verdict.

## 10. Frozen experiment verdict

Apply precedence without override:

1. No detected protocol/lineage/budget/evidence-integrity breach: Rule 1 does not fire. Exception capture limits are explicitly reported, not concealed.
2. No assessable observed primary semantic evasion: Rule 2 does not fire.
3. No assessable control provenance or new semantic regression: Rule 3 does not fire.
4. All three required primaries and both controls have infrastructure errors and lack assessable target observations: **Rule 4 fires: TARGETED_V1_VERIFICATION_INCOMPLETE**.
5. Supported/partial/zero-positive assessable rules 5-7 are not reached. Unobserved outcomes cannot be converted into an assessable negative denominator.

Bounded verification status is **INCONCLUSIVE**. Prompt mechanism and real-provider contract compliance are **NOT_ESTABLISHED**. Actual provider invocations are established, but compliant V1 proof output is not. No before/after semantic/provenance benefit can be measured. Original G5 remains `INCOMPLETE / PRODUCT ERROR` for its historical reason.

## 11. Product, scientific and protected boundaries

```text
PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
SCHEMA_CHANGE = false
CONFIG_CHANGE = false
DEPENDENCY_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
NEW_RUNTIME_MODE = false
TEST_EXECUTIONS = 0
NEW_G5_FULL_RUNS = 0
TARGETED_LIVE_RUNS = 1
RUNNER_INVOCATIONS = 1
RESUMES = 0
LOGICAL_CASE_ATTEMPTS = 6
QA_RESULTS_COMPLETED = 0
INFRASTRUCTURE_EXCEPTION_RECORDS = 6
UNATTEMPTED_CASES = 0
SCIENTIFIC_GENERATION_PROVIDER_INVOCATIONS = 34
SCIENTIFIC_EMBEDDING_PROVIDER_INVOCATIONS = 4
SCIENTIFIC_PROVIDER_INVOCATIONS = 38
SCIENTIFIC_TOKENS = 17701
EXTERNAL_JUDGE_CALLS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```

Only the dedicated report and current-state sections of the two documents are delivery changes. The corrected design, product files, historical documents/results and O/S raw stores remain unchanged. Static file/ledger inspection, frozen identity comparisons and `git diff --check` are non-scientific checks, not pytest or additional QA evaluations. No scientific work follows the finished invocation.

## 12. Lifecycle and next recommendation

```text
G5_POST_V1_TARGETED_LIVE_VERIFICATION_DESIGN = COMPLETE / CORRECTED / EXECUTION_READY
PRIMARY_SEMANTIC_GATE = ABSOLUTE
CONTROL_SEMANTIC_GATE = REGRESSION_RELATIVE
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
NEXT_TASK_RECOMMENDATION = BOUNDED BLOCKER DIAGNOSIS OF TARGETED PROVIDER 429 / MISSING PERSISTED V1 OBSERVATIONS
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

The next recommendation is bounded diagnosis of the observed provider capacity blocker and resulting unavailable target observations under separate authorization. It does not authorize provider probes, switching models, runtime capture/source changes, replaying missing stages, resuming/replacing these failed observations, a new evaluation, prompt tuning, validator relaxation or protected access. Any future attempt needs forward protocol authorization. G6 remains blocked.
