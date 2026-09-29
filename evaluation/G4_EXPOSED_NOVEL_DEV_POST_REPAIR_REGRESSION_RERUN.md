# G4 Exposed Regression: Authorized n002 / n018 Rerun

## Decision and provenance

**G4 EXPOSED POST-REPAIR REGRESSION = SAFETY REGRESSION. Verification scope: FAIL.**

The user explicitly authorized rerunning n002 and n018 after the initial terminal D1 exceptions. The supported `run_evaluation` runner executed only those two cases once, with no product repair or tuning. Both returned `answered`. The focused runner is **COMPLETE / FAIL**, with 2/2 scored and no exceptions; its existing quality-gate verdict is preserved separately from production answer completeness.

The updated selection covers **28/28 QA results**: 26 unchanged initial QA records plus the two authorized rerun records. Selection always uses the authorized rerun for both targets, regardless of outcome; it is not best-of selection. The initial runner remains **INCOMPLETE / INCONCLUSIVE**, with its original 26/28 scored and two terminal exceptions. Under `docs/EVALUATION_POLICY.md` section 9, this mixed-provenance composite is diagnostic and cannot pass a full development, regression or release gate.

- Initial run: `g4-r2-post-repair-novel-dev-regression-v1`.
- Rerun: `g4-r2-post-repair-n002-n018-rerun-v1`.
- Rerun start HEAD: `3b26d8d622d11c3438c98ee63938ebe062477998`, clean at invocation.
- Evaluated product behavior lineage: `a22c8f70eeebe4a53490e11a4b6852561ca8afa6`; intervening Git changes were evaluation analysis/documentation only.
- Mode/split: `qa` / `novel_dev`; `official=false`, `candidate_id=none`, `allow_draft=true`, `capture_stage_trace=true`, external judge disabled.
- Dataset: `evaluation/novel/v1/novel_dev.yaml`, `novel-v1-dev-0.3.0`.
- Rerun UTC: 2026-09-29 14:51:45 to 14:54:30.
- Total runner invocations 2; total case attempts 30; n002/n018 have two attempts each, all others one. Supported resumes 0; retryable infrastructure attempts 0.

Source/normalized manifests and output identities, index identity/payload, dataset, prompt, generation/embedding IDs, retrieval/query-expansion policies and package versions all match the initial run. `MODEL_CONFIG_IDENTITY_MATCH=true`. Models remain `gemini-3.8-flash` and `gemini-embedding-2` (3072 dimensions). Prior G3-to-G4 package confounds remain recorded in the [initial report](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION.md).

`PAIRWISE_CAUSAL_INTERPRETATION=NONDETERMINISTIC_EXPOSED_REGRESSION`; provider nondeterminism remains a methodological limitation. Returning successfully does not prove the initial D1 schema failure is fixed.

## Target rerun review

| Case | Initial G4 to rerun | Completeness | Frontier / final evidence |
|---|---|---|---|
| n002 | OTHER_ERROR to ANSWERED_COMPLETE | Two canonical points VALID, runtime coverage 1.0; no missing point/relation or observed critical Gold p1 omission | 9 frontier entries; requirements.txt:1-12 final/cited |
| n018 | OTHER_ERROR to ANSWERED_INCOMPLETE | Runtime coverage 1.0/VALID, but critical Gold p1/p2 content is incomplete | 10 frontier entries; relevant MC-truth tutorial already final/cited |

**n002:** the historical lost objects `object.a45779701b982aff3e7554da` and `object.03af96b1110e782792253a18` are dense ranks 7 and 8, both offered via `policy_role_frontier` and reranked 1 and 2. The first is final and cited. Its saved requirements.txt text and the answer list all twelve declared packages and the file location without unsupported runtime-role assertions. The previously identified information need reaches the answer. Combining prior R2 attribution, accepted deterministic controls and this capture supports a repair-consistent exposed observation, not an isolated causal estimate.

**n018:** the answer identifies GetMcTruth and PndAnalysis::McTruthMatch, but omits checking the returned pointer / possible no-counterpart case, composite particle-type assignment and EvtGen PDG initialization. Those conditions appear in the unchanged critical Gold p1/p2 and the cited saved tutorial. Conservatively narrow the regression category to `ANSWERED_INCOMPLETE`; keep its raw production receipt and evaluator metrics unchanged. Relative to saved G3, null checking and composite-type preparation disappear; explicit EvtGen PDG initialization was already absent in the saved G3 answer. Do not independently certify the old Gold completeness or count every current omission as newly introduced. The earliest generic owner remains unresolved; visible stages are A0 omission and V1/G2 acceptance of narrower canonical runtime obligations. No R2 evidence loss is established here.

n006 and n017 are unchanged: n006 remains manually incomplete for critical suffix literals with its constructor excluded; n017 remains production-complete with its primary PndTrack header final/cited. n001 remains Q1 with its historical Gold discrepancy; n010 and n019 remain improved but causally unresolved. The [machine result](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RERUN_RESULT.json) includes all 28 comparisons, selected raw-record provenance, actual target pool entries, evidence locators and bounded review.

## Updated categories and transitions

| Category | Initial G4 | Updated all 28 | Updated expected answered (27) |
|---|---:|---:|---:|
| ANSWERED_COMPLETE | 19 | 20 | 19 |
| ANSWERED_INCOMPLETE | 1 | 2 | 2 |
| INSUFFICIENT_EVIDENCE | 6 | 6 | 6 |
| VERSION_CONFLICT | 0 | 0 | 0 |
| OTHER_ERROR | 2 | 0 | 0 |

Raw production labels are 22 complete / 0 incomplete / 6 insufficient; bounded review narrows n006 and n018. The complete count includes n016, which is an incorrect expected abstention in both G3 and G4 (0/1 correct). No version-conflict case applies. Runtime coverage distribution is 0.0=1, 0.5=4, 2/3=1, 1.0=22; runtime missing required points remain 8 across n001, n007, n014, n024, n028 and n031.

| Saved G3 to updated G4 | Complete | Incomplete | Insufficient | Version conflict | Error |
|---|---:|---:|---:|---:|---:|
| ANSWERED_COMPLETE | 13 | 1 | 5 | 0 | 0 |
| ANSWERED_INCOMPLETE | 0 | 0 | 0 | 0 | 0 |
| INSUFFICIENT_EVIDENCE | 7 | 1 | 1 | 0 | 0 |
| VERSION_CONFLICT | 0 | 0 | 0 | 0 | 0 |
| OTHER_ERROR | 0 | 0 | 0 | 0 | 0 |

The matrix includes n016; expected-answered complete-to-complete is 12. Insufficient-to-complete IDs are n002, n004, n008, n010, n017, n019, n027. n006 is insufficient-to-incomplete; n018 is complete-to-incomplete; n001 stays insufficient.

## Safety and frontier

Six saved production-complete candidate sentinels still worsen: **n007, n014, n018, n024, n028, n031**. n018 now becomes manually incomplete rather than an exception. Historical independent-validity caveats remain. The n024 mechanism is unchanged: identical channel rankings and the identical authoritative RRF-rank-18 helix header, formerly final/cited, are displaced from the 16 ordinary / 14 frontier offer. That credible generic R2 completeness regression still prevents G4 closeout.

| Existing evaluator metric | Saved G3 | Updated selection |
|---|---|---|
| Citation integrity | 1.0 / 28 | 1.0 / 28; 0 failures |
| Identifier hallucinations / mentions | 2/57 (3.5088%) | 1/64 (1.5625%) |
| Required-source coverage | 66.6667% / 27 | 81.4815% / 27 |
| Expected-status accuracy | 64.2857% / 28 | 75% / 28 |
| Final-evidence recall | 0.425926 / 27 | 0.589506 / 27 |
| Wrong-version / forbidden evidence | 0 / 0 | 0 / 0 |
| Gold-weighted coverage / critical misses | NOT_MEASURED | NOT_MEASURED |
| Unsupported / major / minor claims; contradictions | NOT_MEASURED | NOT_MEASURED |

There are no new citation, identifier, version, forbidden-evidence or required-source failure IDs. The existing n004 fairlogger/Logger.h raw flag and its citation-support caveat are unchanged. Required-source failures remain n001, n005, n009, n022, n025. Manual review confirms at least three partially/unfulfilled critical Gold points in answered results across n006.p2 and n018.p1/p2; this lower bound is not a global judged Gold score. Runtime reviews flag no retained final claim as unsupported, which does not establish independent cohort-wide semantic correctness.

All 28 selected cases have frontier receipts: 295 case-level entries, with n002=9 and n018=10 added to the original 276. Structured supplements 0; ordinary-only cases 0; unobserved receipts 0. Complete per-case entry counts are in the machine result.

| Receipt/outcome | Complete | Incomplete | Insufficient | Version conflict | Error |
|---|---:|---:|---:|---:|---:|
| frontier_used | 20 | 2 | 6 | 0 | 0 |
| frontier_not_used | 0 | 0 | 0 | 0 | 0 |
| receipt_unobserved | 0 | 0 | 0 | 0 | 0 |

This cross-tab is descriptive only. Remaining independently reviewed/candidate answerable insufficient cases remain n001 (Q1, Gold discrepancy), n007 (V1/G2), n024 (R2), n028 (V1/G2) and n031 (V1/G2). n014 answerability remains unresolved; n028/n031 visible review failures do not alone prove validator defects.

## Usage, delivery verification and boundaries

| Accounting scope | Calls | Tokens | Generation | Embedding | External judge |
|---|---:|---:|---:|---:|---:|
| Initial G4, all attempts | 153 | 1,107,119 | 126 | 27 | 0 |
| Authorized two-case rerun | 12 | 80,517 | 10 | 2 | 0 |
| Cumulative all attempts | 165 | 1,187,636 | 136 | 29 | 0 |

n002 uses 6 calls / 33,708 tokens; n018 uses 6 / 46,809. Selected-record aggregate usage excludes the two initial failed attempts (2 calls / 4,230 tokens), yielding 163 / 1,183,406; the cumulative accounting above includes them. Returned usage is not a provider invoice or USD estimate.

Delivery checks: analyzer AST; exact reproduction of the original committed result; exact rerun-result reproduction; selection provenance, matrix/category marginals and cumulative usage checks; raw-store output guard; complete tracked-diff review; Git whitespace check. No product test suite or accepted deterministic controls were rerun. Original run stores and initial report/result remain preserved; raw answers/traces stay in ignored stores.

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

Analysis-only reproduction, with no model calls:

```powershell
& '..\.venv\Scripts\python.exe' evaluation/g4_exposed_post_repair_regression.py --rerun-run-id g4-r2-post-repair-n002-n018-rerun-v1 --review evaluation/G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RERUN_RESULT.json --output data/evaluation/g4-target-rerun-reproduced.json
```

## Lifecycle

G4 remains open for safety-regression review. Fresh Lane B remains OPTIONAL / DEFERRED, not a mandatory gate. This rerun does not authorize tuning, product repair, another cohort or G5. The only recommended follow-up remains **G4 R2 COLLATERAL RETENTION / COMPLETENESS FAILURE REVIEW**.

```text
PHASE_G = IN_PROGRESS / G4_EXPOSED_POST_REPAIR_SAFETY_REGRESSION_REVIEW_REQUIRED
G4 = DETERMINISTIC HARNESS COMPLETE / EXPOSED DEVELOPMENT DIAGNOSTIC COMPLETE / GENERIC R2 FALSE_INSUFFICIENCY MECHANISM ESTABLISHED / R2 REPAIR IMPLEMENTED IN NORMAL PRODUCT PATH / NORMAL-PRODUCTION DETERMINISTIC RED→GREEN PASS / EXPOSED POST-REPAIR TARGET RERUN COMPLETE / 28 OF 28 SELECTED QA RESULTS / DIAGNOSTIC COMPOSITE; ORIGINAL COHORT INCOMPLETE / SAFETY REGRESSION / FRESH GENERALIZATION BENEFIT NOT_ESTABLISHED
NEXT_TASK_RECOMMENDATION = G4 R2 COLLATERAL RETENTION / COMPLETENESS FAILURE REVIEW
NEXT_TASK_EXECUTION_AUTHORIZED = false

STOP.
```
