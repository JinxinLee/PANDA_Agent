# G4 Exposed novel_dev Post-Repair Regression

## Decision and completion

**G4 interpretation: SAFETY REGRESSION. Verification scope: FAIL (observed exposed completeness regression).**

The first current-lineage run attempted every existing exposed case once. All 28 have terminal records, but only **26/28 have QA results**; n002 and n018 are nonretryable product exceptions. The supported runner remains `INCOMPLETE / INCONCLUSIVE` (`PRE_RELEASE_EXECUTION_INCOMPLETE`), with no retryable cases and no supported recovery authorized for these terminal exceptions. This bounded safety finding is separate from a complete-cohort quality verdict. No full-cohort success or repair closeout is claimed.

Run: `g4-r2-post-repair-novel-dev-regression-v1`; `qa`, `novel_dev`, `official=false`, `candidate_id=none`, `allow_draft=true`, `capture_stage_trace=true`, no external judge. Dataset: `evaluation/novel/v1/novel_dev.yaml`, `novel-v1-dev-0.3.0`, all 28 IDs. Runner invocations 1; case attempts 28; supported resumes 0; retryable infrastructure attempts 0; terminal D1 exceptions 2.

Raw records, answers, stage traces and retrieval traces remain in the ignored run store. This report and the [machine result](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RESULT.json) do not overwrite them. The historical G3 store was read only.

## Identity and comparison limits

- Start/evaluated product lineage: `a22c8f70eeebe4a53490e11a4b6852561ca8afa6` (clean at preflight and execution).
- Historical G3 product lineage: `a0106bd5eff93646f34f5e50e161e8be8a49d680`; its manifest repository commit is `16dad6f52e266de88f9a218938f236d3ef6cd936`. These are distinct recorded concepts.
- Delivery is an analysis/documentation commit after the evaluated lineage; resolve its exact SHA from Git history. Product behavior is unchanged by delivery.

Preflight used the existing manifest builder before any scientific call and confirmed all selected IDs and execution boundaries. The actual new manifest agrees. G3 completion JSON and review overlay cross-check 28 completed QA cases, the old product lineage and admission `NO_CHANGE`. Full manifest identities are retained in the machine result.

| Identity | Old vs new |
|---|---|
| `source_manifest_hash` | MATCH |
| `normalized_manifest_hash` | MATCH |
| `normalized_output_hashes` | MATCH |
| `index_identity` | MATCH |
| `gold_dataset_hash` | MATCH |
| `gold_benchmark_version` | MATCH |
| `prompt_hash` | MATCH |
| `generation_model_id` | MATCH |
| `embedding_model_id` | MATCH |
| `retrieval_policy_hash` | MATCH |
| `query_expansion_hash` | MATCH |

Model IDs: generation/production semantic verification `gemini-3.8-flash`; embedding `gemini-embedding-2`, 3072 dimensions. `MODEL_CONFIG_IDENTITY_MATCH=true`. Product mode `production_answer_obligations_v1`; decomposition prompt/schema `3.0.0` / `e1.question_decomposition.v3`; coverage schema `coverage-satisfaction-v2`; prompt set `3.12.0`; fingerprint `5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce`. Active Gold/calibration: `m6-benchmark-v2.11` / `phase_b_t3_product_language_scope_v8`.

Runtime package differences were recorded before execution: Python 3.13.14 to 3.12.14; langgraph 1.2.11 to 1.2.10; qdrant-client 1.19.0 to 1.15.1. Other recorded packages match. These are comparison confounds; no dependency installation or change was performed.

`PAIRWISE_CAUSAL_INTERPRETATION=NONDETERMINISTIC_EXPOSED_REGRESSION`. Provider run nondeterminism remains present even with identical model IDs. General QA transitions are not paired causal estimates. The n024 pool displacement has stronger local mechanistic evidence because all channel rankings and the relevant authoritative RRF entry are identical. No additional reranker or QA counterfactual was executed.

## Classification and transitions

Production completeness uses the existing canonical runtime points: covered IDs divided by all canonical points, coverage 1.0, no missing required point, and a complete VALID production receipt without a whole-review rejection. This is not an external Gold-weighted score. A conservative bounded human review narrows n006 from production-complete to `ANSWERED_INCOMPLETE`: independently required critical Gold p2 suffix literals are absent. Raw metrics and receipts are unchanged. No success category is loosened.

| Category | Old all 28 | New all 28 | New expected answered (27) |
|---|---:|---:|---:|
| ANSWERED_COMPLETE | 19 | 19 | 18 |
| ANSWERED_INCOMPLETE | 0 | 1 | 1 |
| INSUFFICIENT_EVIDENCE | 9 | 6 | 6 |
| VERSION_CONFLICT | 0 | 0 | 0 |
| OTHER_ERROR | 0 | 2 | 2 |

The new raw production classification is 20 complete / 0 incomplete / 6 insufficient / 0 version conflict / 2 errors; the reviewed regression classification is 19 / 1 / 6 / 0 / 2. The all-case complete count includes n016, an **incorrect expected abstention in both runs** (expected insufficient, observed answered; abstention accuracy 0/1 to 0/1). No version-conflict case is applicable.

| Old \ New | Complete | Incomplete | Insufficient | Version conflict | Error |
|---|---:|---:|---:|---:|---:|
| ANSWERED_COMPLETE | 13 | 0 | 5 | 0 | 1 |
| ANSWERED_INCOMPLETE | 0 | 0 | 0 | 0 | 0 |
| INSUFFICIENT_EVIDENCE | 6 | 1 | 1 | 0 | 1 |
| VERSION_CONFLICT | 0 | 0 | 0 | 0 | 0 |
| OTHER_ERROR | 0 | 0 | 0 | 0 | 0 |

This matrix covers all 28 terminal outcomes, including the unchanged n016 abstention failure. For expected answered only, the complete-to-complete cell is 12 rather than 13. The insufficient-to-complete cases are n004, n008, n010, n017, n019, n027; insufficient-to-incomplete is n006; insufficient-to-error is n002; insufficient-to-insufficient is n001.

## R2 targets and other historical insufficient cases

| Case | Old status / runtime coverage | New status / runtime coverage | Frontier / final need |
|---|---|---|---|
| n002 | insufficient / 0.0 | error / unavailable | Unobserved: D1 fails before retrieval; no final evidence |
| n006 | insufficient / 0.5 | answered / 1.0; reviewed INCOMPLETE | 13 frontier entries; constructor still omitted; suffix need not established |
| n017 | insufficient / 0.0 | answered / 1.0; COMPLETE | 13 frontier entries; primary header retained, final and cited; need established |

**n002:** `_Ambiguity.status` receives `none`, while local schema permits `clear` or `ambiguous`; a nonretryable ValidationError ends decomposition before retrieval (one generation call, no embedding). No pool, final/cited evidence or critical relation review exists. Its prior R2 attribution is historical; this run cannot observe whether that need would reach R2 or final evidence.

**n006:** `object.2914485ff398f61e994c46d6` remains dense rank 9 and is absent from actual rerank offer and final evidence. The final cited header is `object.448ae767c7b20b7320ebbcbe`, `tools/PndFileNameCreator.h:25-72`, entered via frontier; a simulation macro is also cited. The answer lists fExt* attributes and getters, not constructor suffix values. Runtime missing points/relations are empty, but independently required critical `n006.p2` is missing. The earlier R2 loss is still visible and the production completeness acceptance is a safety concern; full Gold p1 completeness is not separately scored.

**n017:** `object.015bff352e03a5f5ee88c307` is dense rank 7, enters via `policy_role_frontier`, and is the final cited `pnddata/TrackData/PndTrack.h:23-126`. It establishes PndTrack, first/last fitted parameters and candidate/TRef fields. All three production points are VALID/complete, with no missing point/relation. The second historical chunk remains excluded, but the full primary header supplies the requested information. This is repair-consistent exposed observation combining prior attribution, accepted deterministic RED-to-GREEN and current capture; frontier presence alone is not a causal success test.

Full current target `rerank_pool_entries`, final/cited evidence locators and historical-object traversal are in the machine result. Raw answers/traces are not duplicated here.

| Other historical case | Observation | Ownership limit |
|---|---|---|
| n001 | insufficient 0.0 to insufficient 0.0; unsupported requested FairSoft | Q1 unchanged; known Gold/source shell discrepancy remains untouched |
| n010 | insufficient 0.5 to answered 1.0 | Prior Q1/R1 unresolved; no automatic R2 credit |
| n019 | insufficient 0.75 to answered 1.0 | Prior R2/Q2 unresolved; no automatic R2 credit |

## Safety and collateral regression

| Existing evaluator metric | Old | New |
|---|---|---|
| Citation integrity | 1.0 (28 cases) | 1.0 (26 cases) |
| Identifier hallucinations / mentions | 2/57 (3.5088%) | 1/61 (1.6393%) |
| Required-source coverage | 66.6667% / 27 | 80.0000% / 25 |
| Wrong-version evidence / forbidden evidence | 0 / 0 | 0 / 0 |
| Expected-status accuracy | 64.2857% / 28 | 73.0769% / 26 |
| Final-evidence recall | 0.425926 / 27 | 0.556667 / 25 |
| Gold-weighted point coverage / critical misses | NOT_MEASURED | NOT_MEASURED |
| Unsupported / major / minor claims; contradictions | NOT_MEASURED | NOT_MEASURED |

Semantic Gold metrics have denominator 0 in unjudged QA mode; null is not zero. Last runtime reviews flag no retained final claim as unsupported, but this does not establish independent semantic correctness or a contradiction-free cohort. Bounded review verifies at least one critical omission in an answered result, n006.p2; no global manual Gold score is claimed.

New identifier failure IDs relative to old: none. The one remaining raw flag is n004 `fairlogger/Logger.h`, explicitly present in both cited documents and in `identifier_supported_by_claim_evidence`; its external header path is absent from the locked corpus inventory. Keep the raw evaluator flag and distinguish it from an established new unsupported assertion. No new citation, wrong-version or forbidden-evidence failure is observed in available QA metrics. Required-source failures are n001, n005, n009, n022, n025; none is a new failure ID.

Runtime missing required points: 14 old to 8 new. New-case runtime coverage distribution: 0.0=1; 0.5=4; 2/3=1; 1.0=20; unavailable=2. Runtime missing-point cases are n001, n007, n014, n024, n028, n031; new runtime miss cases versus the old saved receipt are n007, n014, n024, n028, n031. These are not relabelled as judged Gold critical misses.

Previously complete candidate sentinels: n003, n005, n007, n009, n014, n015, n018, n020, n021, n022, n023, n024, n025, n026, n028, n029, n030, n031. They have complete VALID saved production coverage, citation integrity and no identifier/version/forbidden failure; 13 also pass the old required-source metric. Independent Gold semantic validity was not established for all 18. Six worsen: **n007, n014, n018, n024, n028, n031**. None becomes answered-incomplete; five become insufficient and n018 becomes a terminal error. n014 merits the explicit prior-answer validity caveat below.

| Worsened case | Earliest visible owner / review |
|---|---|
| n007 | V1/G2 deterministic qualified-identifier rejection despite admitted GetPath documentation; method claim filtered in V1 and V2 |
| n014 | Unresolved independent repository-description answerability; A0 absence assertion rejected by V1; old answer used thesis prose |
| n018 | D1 nonretryable ambiguity parsing, before retrieval |
| n024 | R2 collateral pool displacement; supported analytic-helix explanation no longer offered/final |
| n028 | V1/G2 LOCAL_INVALID / INVALID_SUPPORTER; relevant macro and header remain visible |
| n031 | V1/G2 LOCAL_INVALID / BAD_QUOTE; explicit generator-category source remains visible |

### n024: credible repair-related collateral completeness regression

Old and new **all channel rankings are identical**. The relevant `object.d6ef560b88c3926ecb32d3e1`, `tracking/PndHelixPropagator/PndHelixPropagator.h:24-124`, is dense rank 8, sparse rank 19 and authoritative RRF rank 18 in both traces, with identical score 0.027364110201042444. Historically it was reranked 2, final and cited. Its saved locked text supplies the radius formula, circle-center method and target propagation interfaces.

The new offer contains 16 ordinary RRF entries and 14 frontier entries and excludes this object. Current final evidence lacks it; V1 accepts the GEANE explanation and propagator names but rejects an absence assertion instead of an analytic-helix explanation, leaving point.3 missing (coverage 2/3). This directly identifies R2 pool displacement with high confidence. It is a generic completeness risk of dropping useful cross-channel RRF entries to make frontier room, even while the strict RRF-majority control remains satisfied. The observed full QA effect is still not a deterministic paired estimate.

## Frontier observability

Cases with frontier: 26; total case-level frontier entries: 276; structured supplements: 0; ordinary-only cases: 0.
All 26 cases that reached normal retrieval have the internal receipt. n002/n018 terminate before retrieval, so usage is unobserved; no generic missing-receipt defect is established. Repeated object IDs across cases are counted per case.

Entries per applicable case: n001=10, n003=9, n004=9, n005=12, n006=13, n007=9, n008=13, n009=9, n010=13, n014=14, n015=11, n016=6, n017=13, n019=5, n020=10, n021=14, n022=9, n023=14, n024=14, n025=12, n026=9, n027=9, n028=7, n029=14, n030=14, n031=4.

| Receipt/outcome | Complete | Incomplete | Insufficient | Version conflict | Error |
|---|---:|---:|---:|---:|---:|
| frontier_not_used | 0 | 0 | 0 | 0 | 0 |
| frontier_used | 19 | 1 | 6 | 0 | 0 |
| receipt_unobserved | 0 | 0 | 0 | 0 | 2 |

The complete column includes the unchanged n016 incorrect abstention. No no-frontier QA case exists here; the cross-tab is descriptive and cannot estimate frontier efficacy.

## Remaining false-insufficiency candidates

Independently pre-adjudicated current insufficient: n001 (Q1, known Gold discrepancy). Saved-source-supported new candidate insufficiencies: n007 (V1/G2 identifier filtering), n024 (R2 pool displacement), n028 (V1/G2 INVALID_SUPPORTER), n031 (V1/G2 BAD_QUOTE). For n028/n031, the visible review block is established; underlying false-rejection/validator defect is not forced from that fact. n014 remains unresolved for independently sufficient explicit repository description. None is repaired here.

## Usage, verification and protected boundary

```text
QA_RUNNER_INVOCATIONS = 1
QA_CASE_ATTEMPTS = 28
SCIENTIFIC_CALLS = 153
SCIENTIFIC_TOKENS = 1107119
GENERATION_CALLS = 126
EMBEDDING_CALLS = 27
EXTERNAL_JUDGE_CALLS = 0
```

These are cumulative repository request/token counters, including every case attempt. Returned usage is not a provider invoice or USD estimate; unavailable provider usage is not invented. This was a real-cost QA run.

No product test suite was rerun: source matched the accepted a22c8f70 candidate. Existing normal-path/R2 17 controls and G4 18 controls retain their accepted deterministic scope. Evaluation analyzer syntax, reproduction against the same read-only stores/review, category/transition/accounting checks and Git whitespace checks are the delivery verification; no new scientific invocation is used for them.

```text
PRODUCT_SOURCE_CHANGE = false
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
FRESH_GENERALIZATION_EVIDENCE = false
NOVEL_VALIDATION_EVIDENCE = false
RELEASE_EVIDENCE = false
```

Reproduce analysis only (no model calls):

```powershell
& '..\.venv\Scripts\python.exe' evaluation/g4_exposed_post_repair_regression.py --review evaluation/G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RESULT.json --output data/evaluation/g4-post-repair-reproduced.json
```

## Lifecycle and next step

G4 is not closed. Fresh Lane B curation/freeze is **OPTIONAL / DEFERRED**, superseding the earlier mandatory proposal without erasing it. The existing exposed regression is the current empirical development diagnostic; it is not fresh confirmation. The next recommended task is exactly **G4 R2 COLLATERAL RETENTION / COMPLETENESS FAILURE REVIEW**, scoped to saved evidence and generic failure review/design under separate authorization. No repair, retuning, new cohort or G5 work is executed.

```text
PHASE_G = IN_PROGRESS / G4_EXPOSED_POST_REPAIR_SAFETY_REGRESSION_REVIEW_REQUIRED
G4 = DETERMINISTIC HARNESS COMPLETE / EXPOSED DEVELOPMENT DIAGNOSTIC COMPLETE / GENERIC R2 FALSE_INSUFFICIENCY MECHANISM ESTABLISHED / R2 REPAIR IMPLEMENTED IN NORMAL PRODUCT PATH / NORMAL-PRODUCTION DETERMINISTIC RED→GREEN PASS / EXPOSED POST-REPAIR REGRESSION ATTEMPT TERMINATED / 26 OF 28 QA RESULTS / SAFETY REGRESSION / FRESH GENERALIZATION BENEFIT NOT_ESTABLISHED
NEXT_TASK_RECOMMENDATION = G4 R2 COLLATERAL RETENTION / COMPLETENESS FAILURE REVIEW
NEXT_TASK_EXECUTION_AUTHORIZED = false

STOP.
```
