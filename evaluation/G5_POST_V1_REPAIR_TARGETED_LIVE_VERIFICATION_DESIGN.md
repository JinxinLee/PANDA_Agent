# G5 Post-V1-Repair Targeted Live Verification Design

## 1. Status, authority and present scope

**PASS / DESIGN COMPLETE / EXECUTION_READY, subject to separate execution authorization and the frozen preflight below.** This task performs offline design/review only. No live run, provider request, test execution, source/prompt/schema change or protected-data access occurred. Execution-ready describes a specified protocol, not authorization or an empirical result.

Starting clean `main` HEAD and product lineage: `5b9588ec552deb91a59a8176d6ce0429c2133b1e`, message `Clarify V1 proof-basis provenance contract`; parent `c1d6084045efe9b05d9d0073e48a846b6fe58e11`. Previous product lineage: `cd0a65df7576a736e83fdfe3da5998b766173ffc`.

Authority: [V1 repair design](G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_DESIGN.md), [V1 implementation](G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_IMPLEMENTATION.md), [failure-family review](G5_INTEGRATED_FAILURE_FAMILY_REVIEW.md), [D1 implementation](G5_D1_DIAGNOSTIC_METADATA_ROBUSTNESS_REPAIR_IMPLEMENTATION.md), [original G5 report](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION.md) and its [machine result](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION_RESULT.json), [separate n018 report](G5_N018_SEPARATELY_AUTHORIZED_RERUN.md) and [machine result](G5_N018_SEPARATELY_AUTHORIZED_RERUN_RESULT.json), [G1 design](G1_RELATIONSHIP_AWARE_ANSWER_OBLIGATION_DESIGN.md), [G2 design](G2_COVERAGE_REVIEW_LOCAL_FAILURE_ROBUSTNESS_DESIGN.md), current status/roadmap and actual source/raw stores. Historical records remain unchanged.

This document's delivery commit, `Design targeted post-V1 live verification`, advances repository history only. Resolve its SHA from Git history; delivery reports the exact value. Product lineage remains `5b9588...`.

## 2. Frozen product identity

```text
PRODUCT_LINEAGE = 5b9588ec552deb91a59a8176d6ce0429c2133b1e
PREVIOUS_PRODUCT_LINEAGE = cd0a65df7576a736e83fdfe3da5998b766173ffc
NORMAL_PRODUCT_MODE = production_answer_obligations_v1
PROMPT_SET_VERSION = 3.12.1
PROMPT_FINGERPRINT = 08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc
QUESTION_DECOMPOSITION_PROMPT_VERSION = 3.0.0
QUESTION_DECOMPOSITION_SCHEMA_VERSION = e1.question_decomposition.v3
COVERAGE_SATISFACTION_SCHEMA_VERSION = coverage-satisfaction-v2
SELECTED_V1_PROVENANCE_CONTRACT = ALL_TO_ALL_CHECK_PROOF_BASIS
HOST_ACCEPTANCE_RULE_CHANGE = false
```

The V1 implementation changes model-facing guidance, not host acceptance. Every supporter still individually cites every basis, contributes to the check, and the set collectively answers the full target. Quotes remain bounded exact substrings. No union acceptance, host proof selection, trimming, quote repair, new verifier/revision call or schema is permitted.

## 3. Verification question and evidence classification

Question: under this product lineage, does the real provider emit provenance-valid, semantically adequate first-pass V1 proof declarations on the exposed failure families that motivated the clarification?

Separate three layers:

1. V1 contract compliance and offline semantic adequacy: primary mechanism observation.
2. Coverage, legitimate A1/V2 and final-answer behavior: downstream diagnostics.
3. Fresh generalization and release readiness: outside this experiment.

All new observations are **EXPOSED_TARGETED_MECHANISM_EVIDENCE**. Primary cases informed the repair; supplemental n018 has additional rerun provenance; controls are already exposed. No result, including 3/3 primary successes, supplies an outcome-blind population estimate, isolated prompt causal effect, fresh validation, release evidence or G6 entry. D1 also changed since historical runs, and current retrieval/decomposition/generation may vary. There is no paired old-prompt live arm.

## 4. Frozen case set and minimum sufficient selection

```text
PRIMARY_TARGET_IDS = [n022, n025, n028]
SUPPLEMENTAL_IDS = [n018]
CONTROL_IDS = [n008, n019]
ALL_CASE_IDS = [n008, n018, n019, n022, n025, n028]
EXECUTION_ORDER = [n008, n018, n019, n022, n025, n028]
LOGICAL_ATTEMPTS_PER_CASE = 1
MAX_LOGICAL_CASE_ATTEMPTS = 6
```

The execution order follows the existing dataset-preserved ordering; preflight must confirm it exactly. The full selector is committed before any new outcome. Roles and order never change after launch.

| Role / ID | Offline raw evidence and inclusion reason | Historical target scope |
|---|---|---|
| Primary n022 | Original V1 PARTIAL `BAD_QUOTE`; source projection retains the two backticks omitted around `ana_dpm.C`. Other relation remains valid. | First-step output handed to the second POCA analysis step: historically `point.1.rel.1`. Test literal formatting reliability. |
| Primary n025 | Original V1 PARTIAL `INVALID_SUPPORTER`; ordinary efficiency check names claim.1/claim.3 with two basis, but claim.1 lacks one citation. First ordinary check is valid. | Raw question asks manageable triplet combinatorics while retaining displaced-vertex efficiency. Test ordinary necessary-check inventory and proof-set selection. |
| Primary n028 | Original V1 PARTIAL `INVALID_SUPPORTER`; exposure relation names claim.2/claim.3 with two basis; claim.2 lacks the macro citation. Production ordinary checks survive. | Downstream exposure of trigger decisions: historically `point.2.rel.1`. Test canonical-relation witness/basis selection. |
| Supplemental n018 | Separate authorized run reaches V1 but gets `INVALID_SUPPORTER` on claim_full_tree_mctruthmatch/claim_tree_match_preparation. Original G5 n018 instead fails in D1. | Whole decay-tree matching, historically `point.2.rel.1`, alongside candidate truth inspection. Shared adequate-source opportunity exists; a single complete witness was not established. |
| Control n008 | Original V1 ACCEPTED, no local codes. Required comparison has claim.2/claim.3 both citing one shared exact basis; ordinary identification also valid. | Both ordinary and canonical comparison paths; specifically preserve legitimate multi-supporter proof capacity. |
| Control n019 | Original V1 ACCEPTED, no local codes. Four checks each declare two basis, covering named input/output and ordinary fitter/hypothesis/persisted-result requests. Three quotes contain literal CRLF. | Preserve multi-basis closure and literal formatting on both completeness paths. |

The three primaries are the minimum nonredundant failure-family/path set: removing any drops quote reliability, ordinary proof selection, or canonical proof selection. n018 adds shared-source/preparation and D1 interaction information but is not a fourth primary gate. Two controls add distinct safety observations that none of the three failed targets can supply. The valid-V1 inventory was inspected offline across the original store; selection uses historical structural features, not new outcomes or final-answer quality. Other candidates (e.g. n010's shared-basis proof or n023's two-basis named proof) duplicate these features without n019's combined formatting/path coverage. No broader control cohort is selected.

Historical n008/n019 answers had independently documented completeness limitations. Their controls establish provenance nonregression only, not a semantic-completeness certification or Gold-derived gate. Control semantic inspection still checks for new underchecking relative to the raw question.

## 5. Exact historical comparison authority

Let `O = data/evaluation/runs/g5-integrated-candidate-novel-dev-v1` and `S = data/evaluation/runs/g5-n018-separately-authorized-rerun-v1`.

- n022/n025/n028/n008/n019: `O/records/<ID>.json` and `O/traces/<ID>.json`.
- n018 V1: `S/records/n018.json` and `S/traces/n018.json`.
- Original D1 context only: `O/records/n018.json`. **O/traces/n018.json does not exist**; no original semantic proposal or V1 was persisted. Do not reconstruct it or substitute S as its result.

Actual stage authority is `records/<ID>.json::diagnostics.qa_stage_trace`: `V1_INPUT` contains claims, canonical obligations and evidence references; `V1_OUTPUT` contains the raw response and validation; `evidence_registry` resolves exact projected text. The sibling retrieval trace supplies the raw question and retrieval flow. Use raw stored citations and quote bytes, not editorial aliases or remembered prose. Point/claim/evidence IDs are local to each run.

Original manifest evaluated repository HEAD `52c9fc6b2fc2c8e021973aefe8a6d92ceb616e1b`; separate n018 manifest evaluated `0b8e4c6605ebfeb1a1245319289e6b480763a23b`. Both used prior product lineage `047201166057edd9859292a1760bc2e9bbf173a2`, prompt 3.12.0 and fingerprint `5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce`. They cannot be merged into a single repaired G5 cohort. Original failure and supplemental outcome are both retained.

## 6. One-attempt and continuation rules

One fresh normal QA invocation per selected case, within one fresh runner invocation. `resume=false`. No best-of, model/prompt edits between cases, outcome-conditioned replay, replacements, promotion/demotion or omitted cases after favorable/unfavorable results. V2 cannot retroactively turn a malformed first V1 into first-pass success.

Ordinary per-case exceptions are saved by the existing runner and remaining frozen cases continue. A semantic/provenance failure does not stop the batch or authorize a retry. Only global preflight/protocol/infrastructure blockers specified below can stop remaining cases; unattempted IDs remain missing, never replaced. Even an infrastructure-tagged `retryable=true` record is a terminal observation for this protocol, not permission to resume it.

## 7. Environment freeze

Use only `C:\Users\Jinxin.DESKTOP-H6SSTQH\Desktop\Agent_learn\.venv\Scripts\python.exe` (repository-relative `..\.venv\Scripts\python.exe`). Read-only inspection during design observed:

| Field | Frozen expected value |
|---|---|
| Python | 3.12.14 |
| langgraph | 1.2.10 |
| qdrant-client | 1.15.1 |
| google-genai | 2.13.0 |
| psycopg | 3.3.4 |
| panda-research-qa-agent | 0.1.0 |
| Generation / effective verification | gemini-3.8-flash / gemini-3.8-flash |
| Configured judge | gemini-3.8-flash; never instantiated/called for mode qa |
| Embedding / dimensions | gemini-embedding-2 / 3072 |
| Vertex location / timeout | global / 120000 ms |
| max_targeted_retrievals | 1 |

Record `sys.executable`, Python and these package versions before scientific calls; record effective role/model settings without credentials. The role settings were resolved read-only after loading the existing root `.env` with the repository CLI's dotenv convention. No client/request was created. Shell-only `VertexSettings.from_env()` lacked project configuration until that existing environment file was loaded; this was a design inspection setup issue, not a required configuration repair.

At future preflight, any different interpreter, dependency version, effective model/region/dimension/timeout, retry policy or retrieval bound stops execution before provider calls. Do not install, recreate, upgrade, downgrade or modify environment/configuration. Use existing source/normalized corpus, embeddings and index. Existing manifest/index checks must match the original compatible identities; no reindex or new hash framework. Source, dataset, policies and query-expansion compatibility must be checked through existing manifest facilities, not invented receipts. Credentials may be renewed through normal access arrangements, but missing access blocks execution and never authorizes fallback models.

## 8. Lineage freeze and the documentation commit

Future product source must equal exact lineage `5b9588...` and the identity in section 2. This design necessarily creates a newer **documentation-only** HEAD. The future execution authorization must explicitly reconcile that design delivery SHA as launch HEAD with frozen product lineage `5b9588...`; do not silently treat the HEAD difference as irrelevant.

Before launch, verify clean tree, exact authorized launch HEAD, and that its diff from `5b9588...` consists only of this design and the two current-state documentation updates. Verify all source/tests/configuration/data-contract files unchanged and compute the active fingerprint through the existing authority. Record actual launch repository HEAD in the runner manifest separately from product lineage. Any additional HEAD change, dirty product file, prompt/schema drift or authorized implementation not incorporated into this design requires explicit reconciliation/updated authorization before scientific calls. No checkout of an arbitrary newer lineage, extra implementation or per-case edit is allowed. No frozen candidate or redundant identity manifest is needed for this non-formal development observation.

## 9. Normal retrieval policy

Run the current normal product path with live current retrieval and generation. Do not pin historical retrieval, inject historical evidence/claims, reuse V1 responses, force a check inventory, or change queries. Existing compatible stored corpus embeddings are reused; query embeddings are live as normal.

Retrieval/generation variation can remove a comparable proof opportunity. Report that explicitly through observability and semantic audit; do not manipulate inputs to recreate historical failure. Production E3 remains disabled. The existing pre-answer sufficiency-targeted retrieval is permitted within its one-pass bound, distinct from E3 and from outcome-conditioned rerunning.

## 10. Call geometry and frozen budget

Source derivation: `qa.py` graph initialization, `_targeted_retrieve`, production `_after_verify_route`, `_run_detailed`, `_compose_verified_answer`; `retrieval.py::analyze/retrieve/_vector`; `llm/vertex.py::generate_json/_embed`; runner exception/accounting loop. Current normal retrieval embeds the raw query once per retrieval, reuses its vector for paper retrieval, and does not execute the semantic shadow embedding. Targeted retrieval supplies the existing plan and does not rerun analysis.

| Logical operation | Maximum per case |
|---|---:|
| Question decomposition | 1 structured generation |
| Initial retrieval analyzer | 1 structured generation |
| Initial rerank | 1 structured generation |
| One pre-answer targeted retrieval rerank, if needed | 1 structured generation |
| A0 | 1 structured generation |
| V1 | 1 structured generation |
| Existing target-authorized A1 | 1 structured generation |
| Full original V2 after A1 | 1 structured generation |
| Composer and composer review, if normally eligible | 2 structured generations |
| Query embedding: initial plus optional targeted retrieval | 2 embeddings |
| External judge | 0 |

Thus at most **10 logical structured operations + 2 logical embedding operations per case**. Effective generation role supplies at most 7 structured operations (including retrieval); effective verification role supplies at most 3. Branches can end earlier. Historical runner records report n022/n025/n028 and supplemental n018 as 4 generation + 1 embedding; n008 as 5 + 1 and n019 as 6 + 1. These recorded counts are neither upper bounds nor complete dual-role invocation counts.

**Accounting limitation found during source review:** `evaluation_runner._stats_snapshot(engine)` reads only `engine.vertex` (generation role). Default QAAgent creates a distinct verification client even with the same model ID. Consequently existing runner counters omit verification invocations/tokens. `_execute_evaluation_case` also does not persist the detailed result's already-aggregated `model_usage`. Historical spending artifacts remain unchanged; do not recast their reported counts as newly certified totals.

The future execution must explicitly authorize a narrow **read-only orchestration accounting binding**: for this one `run_evaluation` invocation, temporarily bind its `_stats_snapshot` reader to existing `QAAgent._stats_snapshot()` for QA engines, retaining the existing Retriever reader for retrieval engines. The QA method sums each distinct role client exactly once and includes failed adapter attempts. Restore the original reader afterward. This is a process-local reporting/budget-input binding, not a source edit, shared-client injection, new storage framework, retry or QA behavior change. It also covers exceptions where the detailed QA return was never produced. No implementation code/helper is created in this design. If that binding is absent, not explicitly authorized, or cannot be verified at launch, stop before scientific calls; the unmodified runner's generation-only counter cannot satisfy this design's all-role accounting contract. Do not silently launch with undercounted guards or implement a permanent runner repair in the execution task.

Existing adapter limits are three structured request attempts and five embedding request attempts per logical operation, only when its transient-error classifier matches. Generation delays are 1/2 seconds; embedding delays 1/2/4/8 seconds. No retry on returned provenance/answer quality is added. `model_calls` and generation/embedding counters increment **before every adapter invocation**, including failed attempts.

Local installed google-genai 2.13.0 inspection confirms `HttpOptions(timeout=...)` has `retry_options=None`; SDK `_api_client.retry_args(None)` uses one HTTP attempt. No additional SDK retry multiplier is configured by the current adapter. Preserve this setting; a changed effective transport retry configuration invalidates the bound. Counts describe API invocations, not an assertion that every attempt is billable or that token metadata captures charges for failed requests.

```text
PER_CASE_MAX_GENERATION_PROVIDER_INVOCATIONS = 30
PER_CASE_MAX_EMBEDDING_PROVIDER_INVOCATIONS = 10
PER_CASE_MAX_TOTAL_PROVIDER_INVOCATIONS = 40
SIX_CASE_MAX_GENERATION_PROVIDER_INVOCATIONS = 180
SIX_CASE_MAX_EMBEDDING_PROVIDER_INVOCATIONS = 60
SIX_CASE_MAX_TOTAL_PROVIDER_INVOCATIONS = 240
EXTERNAL_JUDGE_CALLS = 0
```

Freeze runner `max_model_calls=240`, `max_token_usage=None`, `deadline_minutes=None`, with the explicit all-role accounting binding above. No hard token/dollar cap is claimed; actual available response token metadata is recorded. Any additional token/time cap requested in later authorization must be reconciled with stop/incomplete semantics before launch. Runner guards are between cases, not intra-call hard limiters. The 240 invocation bound follows from six attempts and the unchanged branch/retry maxima; setting the runner guard alone does not prove it. If preflight cannot establish those maxima, do not launch or claim the cap enforceable. Observed excess/protocol drift aborts further cases and invalidates mechanism acceptance.

Report logical case attempts, actual stage entries, structured/embedding provider invocations and retry accounting separately. Stage trace often omits a failed operation's response. For any failed case where logical-operation entry counts are unavailable, mark exact retry count `UNRESOLVED`; do not infer zero or divide API counts to fabricate it. Existing error context and stats still bound/account total invocations. No new retry logger or product code is introduced solely for this design.

## 11. Mutually exclusive reachability classes

Assign in this priority order, before choosing a provenance outcome:

1. **PRODUCT_ERROR**: terminal non-infrastructure runtime/schema/product exception yields no adequate persisted target observation. Product errors remain recorded failures; no replacement. Caught composer fallback with an intact V1 observation is not this class.
2. **INFRASTRUCTURE_ERROR**: terminal transport/service failure or unusable/corrupt capture prevents assessment. Distinguish from product errors with existing exception category; ambiguous category is explicitly unresolved, never success.
3. **V1_NOT_REACHED**: otherwise a legitimate pre-V1 route finalizes without a V1 invocation, e.g. insufficient admitted evidence after allowed retrieval. An upstream thrown exception is classified above, not here.
4. **TARGET_NOT_COMPARABLE**: V1 exists, but target semantics changed upstream, or no nonvacuous corresponding proof opportunity can be assessed from claims/evidence/checks. Missing trace data is infrastructure/capture failure above. A missing row for a canonical relation that *does exist in the new inventory* is assessable malformed output, not disappearance success or this class.
5. **V1_TARGET_OBSERVED**: persisted V1 target owner/inventory and supplied material permit an assessment of the corresponding question-defined need and its proof declaration. Missing/malformed owned rows are assessable failures. Ordinary inventory changes can remain comparable under section 14.

A terminal error record without a captured V1 cannot be promoted using assumptions about a stage that might have executed. A case without any relevant nonempty quote/citation proof challenge cannot count as success merely because it avoids the prior reason code. For controls, absence of the historical proof feature is recorded as a control comparability gap; a different adequate proof is not itself a regression, but cannot silently certify that unexercised feature.

## 12. Provenance outcome taxonomy

For `V1_TARGET_OBSERVED`, assess the entire relevant owner: the matched required relation for canonical primaries, the full necessary ordinary inventory for n025, and all checks for controls. Read the existing receipt plus raw declaration; never accept a silently reduced check.

- **PROVENANCE_VALID**: all relevant declared checks validate under unchanged host contract with no quote, evidence, admission, supporter, inventory/ownership or attributable aggregate defect. `VALID` does not mean satisfied or semantically sufficient. A legitimate admitted-backed unsatisfied check may be provenance-valid; section 13 must establish its honesty and nonvacuous comparability.
- **PROVENANCE_INVALID_SAME_FAMILY**: n022 has a nonexact `BAD_QUOTE`; n025/n028/n018 has individual supporter-to-basis citation closure failure. Inspect actual missing edges, not code alone: unsupported/wrong-parent/unknown supporter under the same `INVALID_SUPPORTER` code is a different subtype. If same and new defects coexist, assign this class and list all new defects separately.
- **PROVENANCE_INVALID_NEW_FAMILY**: no old-family failure, but another invalid proof/inventory/admission/supporter/owner declaration exists. Missing canonical rows, wrong completeness path, inadequate identity or unsupported-carrier violations do not become successes because the old code disappeared.

Unobserved/noncomparable cases have provenance `NOT_ASSESSABLE`, never valid. Whole-review mapping rejection counts as a new failure when its target ownership remains assessable; otherwise comparability is unresolved. Non-target sibling invalidity is recorded separately and is not hidden by target validity. For controls every new local provenance defect is a regression; final answer or historically incomplete semantics do not waive it.

## 13. Offline semantic-evasion audit

For every provenance-valid primary, and controls when assessing nonregression, inspect offline: raw question, new pre-retrieval canonical points/relations, A0 claims and existing citations, V1 checks, selected exact basis and its projected context. Use no model/judge call. Gold is historical answerability/completeness context only; it cannot create runtime needs or define mechanism success.

Record before/after basis IDs and quotes, supporter sets/citations, check meaning, raw-question/canonical need, and whether removed supporters/evidence were genuinely unnecessary. Preserve necessary combined meaning, direction, polarity and explanations. A one-claim witness must actually answer the full check; common citations alone do not prove a small basis adequate. Each supporter must contribute, not merely carry citations.

Outcomes:

- **NO_SEMANTIC_EVASION_OBSERVED**: the new inventory represents necessary raw-question content, evidence genuinely supports the selected meaning, and any smaller proof remains sufficient. A truthful unsatisfied disposition may qualify when the new supplied claims/evidence cannot form a complete closure-valid witness; report incomplete coverage independently.
- **SEMANTIC_EVASION_OR_UNDERCHECK_OBSERVED**: V1 drops necessary ordinary content, omits an existing canonical relation, invents an alternate path, selects an incomplete witness/inadequate basis, or declares unsatisfied despite an available complete closure-valid witness solely to avoid proof validation. Do not infer motive from unsatisfied alone: document the available witness and the missing substantive judgment.
- **SEMANTIC_COMPARABILITY_UNRESOLVED**: available artifacts cannot justify adequate scope/proof or truthful unsatisfaction. Do not assume disappearance of a malformed historical row proves adequacy. Upstream decomposition changes are separately attributed, not automatically blamed on the V1 prompt.

Available evidence that is genuinely inadequate, changed generation or retained distributed-proof overconstraint is not automatically evasion. No repair benefit is claimed from a vacuous empty/blocked row with no comparable proof opportunity. Unresolved semantics never enter the positive mechanism numerator.

## 14. Ordinary and canonical comparability

n022/n028/n018: new canonical relation IDs are fixed before retrieval **within the new run**. Their numeric IDs may change across decompositions; match meaning and literal raw-question support, direction/polarity and necessary explanation, not cross-run ID equality. Inspect all new relations covering that historical need and ensure none is omitted or weakened. Historical IDs are locator hints, not runtime constraints.

n025: its historical point is relation-free. Verifier-derived ordinary check text/count need not match old text bytes. Audit the entire new ordinary inventory for both combinatorial management and displaced-vertex efficiency requested by the raw question. Two genuinely independent necessary checks are legitimate if both validate; a reduced inventory omitting necessary meaning is underchecking. If the new question decomposition legitimately changes path, establish semantic equivalence explicitly or classify not comparable; do not force old rows into the product. A canonical relation may never be replaced with invented ordinary subchecks.

Controls use the same rules for their raw question-defined needs. Historical host acceptance is not a semantic oracle; inspect any change without importing previously missed Gold specifics as new runtime requirements.

## 15. Independent downstream and final observations

For every case record three dimensions separately:

1. V1 reachability, raw/receipt status, provenance class and semantic audit.
2. Target/point and whole-answer coverage; independently valid siblings; `revisionable_relationships` and unsupported-claim targets; A1 authorized/executed and why; full original V2 inventory, status and codes; revision count.
3. Final QA status (`answered`, `insufficient_evidence`, exception), retained/excluded claims, composition/fallback and spending.

Neither an answered status nor V2 acceptance repairs first-pass V1 evidence retrospectively. Valid V1 can coexist with legitimate incomplete coverage/final refusal. Relevant-generation/retrieval loss and unsupported detail remain independent. A malformed target cannot authorize its own A1; legitimate sibling targets may still use the existing one A1. These are observations of current behavior, not separate success gates based on final-answer recovery.

## 16. Frozen experiment verdict, exact precedence

Define a positive primary as `V1_TARGET_OBSERVED + PROVENANCE_VALID + NO_SEMANTIC_EVASION_OBSERVED` with a nonvacuous comparable proof declaration. A clean control has assessable equivalent question needs/proof feature, valid provenance on all checks, no new observed underchecking and resolved semantic interpretation. Supplemental results never add to the three-primary denominator or become a hidden gate.

Apply these mutually exclusive rules in order:

1. Protocol/lineage/budget/evidence-integrity breach: **TARGETED_V1_VERIFICATION_INCOMPLETE**, reason `PROTOCOL_INVALID`; no acceptance regardless of apparent passes.
2. Any observed primary/control semantic evasion, or any assessable control provenance regression: **TARGETED_V1_MECHANISM_NOT_SUPPORTED** (safety veto). Preserve all missing observations separately; a positive target cannot override this veto.
3. Any primary or required control observation is missing, errored, not comparable, or has unresolved semantic audit: **TARGETED_V1_VERIFICATION_INCOMPLETE**. Report observed positives/negatives without converting a partial denominator to PASS.
4. All three primaries positive and both controls clean: **TARGETED_V1_MECHANISM_SUPPORTED**.
5. All primary/control observations assessable, controls clean, one or two primaries positive and the remaining primary targets have malformed provenance: **TARGETED_V1_MECHANISM_PARTIAL**.
6. All observations assessable, controls clean, zero positive primaries: **TARGETED_V1_MECHANISM_NOT_SUPPORTED**.

No post-hoc percentages, subjective majority or supplemental substitution. A supplemental n018 exception or unresolved result alone cannot defeat or improve an otherwise assessable primary/control verdict. A global stop caused during any case can leave required observations incomplete. Report fixed denominator 3, observed denominator, both controls, supplemental separately and every unattempted ID. Mechanism-supported maps to PASS at this bounded scope; partial/not-supported maps to FAIL of the all-primary success criterion; incomplete maps to INCONCLUSIVE. None maps to a G5/G6 gate verdict.

## 17. Separate D1 interpretation for n018

Inspect new decomposition diagnostics independently of V1. A malformed/missing optional ambiguity may become host `unavailable` after semantic validation; valid clear/ambiguous diagnostics may simply mean the repaired fallback was not exercised. Lack of an exception alone is not a new demonstration of D1 fallback behavior.

Original failed semantics were never saved. A later valid semantic proposal cannot prove the original proposal was valid or that original n018 would have completed. V1 comparison uses only the separately authorized pre-repair realization. The new n018 remains supplemental mixed-provenance development evidence, including unresolved preparation/witness and generation limits. D1 and V1 claims remain separate.

## 18. Future run and report identities

```text
RUN_ID = g5-post-v1-repair-targeted-live-v1
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
FUTURE_REPORT = evaluation/G5_POST_V1_REPAIR_TARGETED_LIVE_VERIFICATION.md
```

Use existing programmatic `run_evaluation` and `EvaluationRunStore`: new `manifest.json`, `records/<ID>.json`, retrieval `traces/<ID>.json`, embedded QA stage trace/evidence registry, summaries/run status and call breakdown. Existing runner machine outputs may be retained; no unrelated second storage/result framework. Run ID must be unused; collision aborts, no silent overwrite or unapproved suffix. Historical O/S records are immutable. Existing stage tracing permits explicit non-formal `novel_dev` QA with no candidate; do not use a protected/formal path.

The runner's Gold-derived metrics and generic gate summaries remain machine diagnostics. The primary verdict comes from this frozen mechanism protocol, not generic `official_decision`, expected-answer status, or full-dev gate. No offline live judge is required or enabled.

## 19. Future execution procedure

1. Obtain explicit execution authorization for this frozen six-case protocol, 240 invocation bound, read-only all-role accounting binding and reconciled documentation launch HEAD/product lineage. This design grants none.
2. Read-only preflight: exact clean launch HEAD/allowed documentation-only diff; frozen source/prompt/schema/mode; sibling interpreter/packages, effective role settings/retries/policy; compatible corpus/index/dataset/raw-question identities; all historical selected comparison records, traces and required evidence registries available; new run directory unused. No protected files or provider health-check requests.
3. Record environment using existing manifest/report fields. Preflight model configuration alone does not establish endpoint availability; actual exceptions remain observations. No installation/reindex/environment repair.
4. Establish the section 10 temporary accounting-reader binding to the existing QA aggregate (no source edits, calls or client replacement); invoke existing runner once with section 18 parameters; restore the reader on completion/error. Confirm the runner-preserved case order matches the frozen order before its first scientific call. Use normal unchanged product QA; collect asynchronous execution to completion without outcome-conditioned resume or edits.
5. Preserve each raw record and trace and reconcile actual invocation/token counters. Classify every selected ID, including errors/missing results. Do not regenerate absent traces through a new QA call.
6. Perform offline raw-question/claim/basis semantic inspection, comparability mapping and historical before/after proof table. No provider/judge call and no Gold-defined runtime obligation.
7. Apply section 16 exactly; write the dedicated result report with original G5 authority unchanged. Future report/current-doc updates and delivery are subject to that execution task's authorized Git scope, not automatically performed by this design.

## 20. Stop conditions

Before scientific calls: missing authorization (including accounting binding), unknown/unreconciled HEAD, dirty product source, model/prompt/schema/package/policy drift, missing historical material, altered dataset/questions, incompatible index/corpus, missing access configuration, run-ID collision, selector/order mismatch, generation-only accounting or unverifiable call bound stops launch. Do not repair the environment to make preflight pass.

During execution: ordinary per-case malformed provenance, insufficient answer or saved product/transport exception remains a terminal case observation and the frozen runner continues to other cases. No result-conditioned stop. A global outage preventing record persistence, unrecoverable run-store failure, detected lineage/input mutation, invocation-bound breach, protected access attempt, unexpected judge/new stage, or explicit user stop halts further scientific work. Preserve attempted/error/missing IDs and report INCOMPLETE/protocol-invalid where applicable. No replacing skipped cases, automatic resume or retrospective increase of budget. Runner cap exhaustion is a stop with missing IDs, not completion.

## 21. Future result-report contract

Report actual launch SHA/product lineage, prompt identity, interpreter/packages/models/corpus/index/dataset identity, selected roles/order, start/end times, accounting-reader binding and one-attempt receipts through existing artifacts. Label new counters all-role and historical counters generation-client-only; no synthetic reconciliation of old missing verification usage. For every case provide raw paths and trace stage pointers; historical and new owner scope; observability; V1 raw/receipt status; exact reason codes and missing citation edges/quote membership; provenance outcome; before/after basis/supporters; semantic audit rationale and unresolved questions.

Separately report target/whole coverage, sibling containment, A1 authorization/execution, V2 original inventory, final status/claims/composition and actual call/token totals. Report logical attempts, generation/embedding invocations and supported retry accounting with unavailable metadata labeled. Distinguish complete/errored/unattempted cases; do not make observed-case percentages look like the fixed cohort.

Provide the frozen experiment verdict and evidence class. No claim that all four historical answers recovered, original G5 completed, all false insufficiency resolved, distributed-proof limits removed, or fresh/release readiness achieved. Narrow provider compliance support describes only the actual exposed observations, not a population probability or isolated causal attribution.

## 22. Lifecycle consequences and conditional next steps

Even future targeted PASS leaves original G5 `INCOMPLETE / PRODUCT ERROR`, integrated run incomplete, G6 not authorized, fresh generalization/release evidence false. It may establish `TARGETED_V1_PROMPT_MECHANISM=SUPPORTED_ON_EXPOSED_REPAIR_TARGETS` and `REAL_PROVIDER_CONTRACT_COMPLIANCE=SUPPORTED_IN_TARGETED_EXPOSED_OBSERVATION` only. No distributed-proof model change follows.

- Supported: recommend a separately authorized Phase-G evidence-boundary/fresh-development verification design; assess whether prerequisites permit G6 planning without treating exposed PASS as G5 gate completion. Do not automatically select full G5 or execute a fresh/protected lane.
- Partial/not supported: recommend offline owning-layer failure-family review of the actual new evidence; no automatic validator relaxation, prompt tuning or rerun.
- Incomplete: isolate the concrete environment/product/capture/comparability blocker in a separately authorized task. Preserve failed observations; any later new attempt requires a forward design and explicit authorization, not a replacement masquerading as the frozen run.

## 23. Present task zero counts and unchanged product

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
NEW_G5_RUNS = 0
TARGETED_LIVE_RUNS = 0
N018_LIVE_RERUNS = 0
QA_SCIENTIFIC_RUNS = 0
RETRIEVAL_EVALUATION_RUNS = 0
SCIENTIFIC_GENERATION_CALLS = 0
SCIENTIFIC_EMBEDDING_CALLS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```

Read-only Python parsing/package/configuration inspection and documentation/diff checks are design review, not test executions or model calls. No new run directory or scientific record was created.

## 24. Current design closeout

```text
G5_POST_V1_TARGETED_LIVE_VERIFICATION_DESIGN = COMPLETE / EXECUTION_READY
TARGETED_LIVE_EVIDENCE_CLASS = EXPOSED_TARGETED_MECHANISM_EVIDENCE
TARGETED_LIVE_EXECUTION = NOT_STARTED
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
PROVIDER_COMPLIANCE = NOT_EMPIRICALLY_ESTABLISHED
FALSE_INSUFFICIENCY_RECOVERY = NOT_EMPIRICALLY_ESTABLISHED
NEXT_TASK_RECOMMENDATION = G5 POST-V1-REPAIR TARGETED LIVE VERIFICATION EXECUTION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

Only this design and the authoritative current sections of `docs/EVALUATION_STATUS.md` and `docs/GENERALIZATION_ROADMAP.md` change. No implementation or live verification is executed. Product lineage remains exact `5b9588...`; commit history advances forward, no push.
