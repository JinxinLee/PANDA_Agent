# G5 Integrated Candidate Exposed Regression

## Decision

**G5 = INCOMPLETE / PRODUCT ERROR.** The single authorized draft `qa` invocation attempted every approved `novel_dev` ID, but only 27 of 28 have usable QA results. `n018` terminated before retrieval with a nonretryable D1 `_Ambiguity.status` validation error. The frozen G5 precedence therefore makes `G5_INTEGRATED_RUN_COMPLETE = false` and `G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false`. No case was rerun or replaced. The 27 usable results still support the bounded failure inventory below; they do not convert this incomplete cohort into a complete-cohort FAIL or PASS.

The machine-readable [result](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION_RESULT.json) contains all 28 case decisions, raw-record/trace pointers, final and cited object locators, coverage receipts, stage counts, runner reports, and accounting. The unchanged raw run store is `data/evaluation/runs/g5-integrated-candidate-novel-dev-v1/` and remains Git-ignored. The decision follows the frozen [G5 design](G5_INTEGRATED_CANDIDATE_DESIGN.md).

## Identity and execution

| Item | Observed |
|---|---|
| Evaluated HEAD / start HEAD | `52c9fc6b2fc2c8e021973aefe8a6d92ceb616e1b`, clean at launch |
| Product-behavior lineage | `047201166057edd9859292a1760bc2e9bbf173a2`; no intervening behavior or material-input file change |
| Normal mode | `production_answer_obligations_v1`; no new runtime mode or candidate freezer |
| Run | `g5-integrated-candidate-novel-dev-v1`, one invocation, `qa`, `novel_dev`, `allow_draft=true`, stage traces enabled, `case_ids=none`, `limit=none`, `candidate_id=none` |
| Dataset | `evaluation/novel/v1/novel_dev.yaml`, `novel-v1-dev-0.3.0`, SHA256 `25ad18fcf76ab2796aa18ae961bdc4faf076f0c98a8a5226413ec95e58252223` |
| Approved set | `n001`–`n010`, `n014`–`n031` (28 distinct IDs; 27 expected answered, `n016` expected insufficient) |
| Guardrails | 450 model calls and 2,500,000 tokens; neither stopped execution |

Preflight passed before the scientific invocation. The proposed run ID was unused. Current source manifest, normalized corpus/output, index fingerprint and payload, prompt set/decomposition/schema/fingerprint, generation and embedding identity, retrieval policy, query expansion, and exact dataset/ID set matched the G4 current-lineage capture and frozen G5 design. The prompt fingerprint was `5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce`; generation used `gemini-3.8-flash`, embedding used `gemini-embedding-2` at 3072 dimensions. The initial local preflight command lacked loaded `.env` values and failed before any scientific call; explicit `.env` loading resolved it without changing the evaluated identity.

The G5 runtime used Python 3.12.14, `langgraph` 1.2.10, and `qdrant-client` 1.15.1, versus G4 target-run Python 3.13.14, `langgraph` 1.2.11, and `qdrant-client` 1.19.0. The read-only current Qdrant server version was 1.15.5. Material manifest identities match, but these package differences limit exact runtime comparison; no claim of independent G4 replication follows. `google-genai` 2.13.0 and `psycopg` 3.3.4 matched the G4 capture.

## Runner outcome and accounting

The runner's own `run_status.json` says `status=inconclusive`, `cohort_status=INCOMPLETE`, `official_decision=INCONCLUSIVE`, `decision_reason=PRE_RELEASE_EXECUTION_INCOMPLETE`, and `27/28` scored. All 28 IDs have one terminal record; missing, extra, and retryable ID sets are empty. The formal `gate.json` has `passed=false`. The development gate has `passed=false`, `complete_full_dev=false`, and the note `Focused or incomplete run: it can diagnose a layer but cannot pass the development gate.` The product-language gate has `compatible=false`, `passed=null`, with reason `incompatible product-language calibration: calibration Gold version does not match active dataset`. These raw verdicts are preserved verbatim in the machine result. Their official-`dev` and benchmark-calibration predicates do not replace the separate draft `novel_dev` G5 contract.

| Counter | Actual |
|---|---:|
| QA runner invocations / supported resumes | 1 / 0 |
| Case attempts / usable QA results / terminal records | 28 / 27 / 28 |
| Model calls / recorded tokens | 164 / 1,126,264 |
| Generation / embedding / external judge calls | 136 / 28 / 0 |
| Product exceptions | 1 (`n018`, 1 generation call, 1,974 tokens) |

The raw product statuses among usable results are 19 `answered` and 8 `insufficient_evidence`. `n018` has no QA result: a returned ambiguity value `none` violates the D1 schema literal `clear | ambiguous`. Its saved exception is `ValidationError`, `retryable=false`. No budget stop or provider-retry condition occurred, so the frozen protocol forbids replacing this record with an opportunistic retry.

## Independent exposed case review

Review used the unchanged answer, citations, final evidence, stage trace, runtime coverage, reviewed Gold, and allowed locked sources. The classification requires the meaning of critical points and relations, not Gold wording. Runtime coverage is diagnostic: it can say `VALID` while the answer omits critical source-supported detail. This is a bounded offline review without an external judge; the raw runner metrics remain separate.

| Class | IDs | Count |
|---|---|---:|
| `ANSWERED_COMPLETE` | n002, n004, n015, n017, n026, n027, n030 | 7 |
| `ANSWERED_INCOMPLETE` | n003, n005, n006, n008, n010, n019, n020, n021, n023, n024, n029, n031 | 12 |
| `INSUFFICIENT_EVIDENCE` | n001, n007, n009, n014, n016, n022, n025, n028 | 8 |
| `ERROR` | n018 | 1 |

Of the eight refusals, `n016` is a justified abstention: Linux/Unix material does not establish a complete native Windows procedure. The other seven are independently answerable from allowed locked material and constitute false insufficiency. The twelve answered-incomplete cases have critical semantic or evidence-role omissions. These are diagnostic secondary blockers because the run itself is incomplete.

| ID | Expected → actual; class | Critical observation | Earliest supported owner; secondary | R2 / authority |
|---|---|---|---|---|
| n001 | answered → insufficient; false insufficiency | `configSettings.sh` nominal pairs/paths/exports and as-written unmatched behavior remain unanswered | Q1; R3, high | Script reached pool; Gold branch-execution wording conflicts with as-written Bash syntax only for that dimension |
| n003 | answered → answered; incomplete | Per-event `ReadEvent` / `CalcActValues` increment and rollover omitted | R2; generation, medium | Implementation dense 16, absent pool; no proven G4 contract regression |
| n005 | answered → answered; incomplete | `eventDisplay.C` file-opening role and `PndMasterRunAna::Setup` mechanism omitted | R1; generation, medium | Macro absent trace; no contract contradiction |
| n006 | answered → answered; incomplete | Exact `trackF`, `idealTrackF`, `riemann`, `combRiemann`, `kalman`, `vertex` suffix defaults omitted | R2; generation, high | `.cxx` dense 9 but absent pool; historical quota residual, not proven contract regression |
| n007 | answered → insufficient; false insufficiency | `GetPath(shortID)` relation refused after `unsupported identifier PndGeoHandling::GetPath` | V1; generation, high | Required method in final/cited documentation; no R2 loss |
| n008 | answered → answered; incomplete | Low-hit requirement, theta distortion, and 1.5-versus-15 GeV/c contrast omitted | Generation; V1/G2, medium | Cited thesis supports part of comparison |
| n009 | answered → insufficient; false insufficiency | Required E760 model/uncertainty distinction incomplete | R1; Q1/Q2, medium | Relevant implementation absent trace; thesis final |
| n010 | answered → answered; incomplete | `PndFsmTrack` → detector `respond` → factory/response/cutAndSmear chain omitted | R1; generation, medium | Target class files absent trace |
| n014 | answered → insufficient; false insufficiency | Repository description refused | R1; generation, high | Locked `model_framework/README.md:1-4` resolves pre-frozen answerability uncertainty; no trace hit |
| n018 | answered → error | D1 ambiguity literal validation failed before retrieval | D1, high | R2 not reached; nonretryable product-quality/hard-safety blocker |
| n019 | answered → answered; incomplete | `Exec` per-track fitting/hypotheses and final branch/index omitted | R2; generation, medium | Relevant implementation body sparse 18–20, absent pool |
| n020 | answered → answered; incomplete | `PndRecoKalmanTask2` with `SetPropagateToIP(kFALSE)` omitted | Generation; V1/G2, high | Exact setting in cited final README/macro |
| n021 | answered → answered; incomplete | PandaRoot `detectors/lmd` build roles `LmdMC/LmdDigi/libLmdReco` omitted | R1; generation, medium | Build file absent trace |
| n022 | answered → insufficient; false insufficiency | Partial workflow then refusal; fallback detail missing | R1; V1, medium | `ana_dpm.C` absent trace; `BAD_QUOTE` observed, validator fault unproven |
| n023 | answered → answered; incomplete | `FtsTrackAnalytic` branch and distinct payload types omitted | R2; generation, medium | Finder `.cxx` dense 11, absent pool |
| n024 | answered → answered; incomplete | GEANE error/transport matrix and helix backward mode omitted | Generation; V1/G2, high | Repaired helix R2 retention observed; final/cited headers contain details; runtime coverage `VALID` is narrower than semantic review |
| n025 | answered → insufficient; false insufficiency | Up-to-eight tangent-circle solutions omitted, then refused | Generation; V1, high | Detail in final/cited evidence; `INVALID_SUPPORTER` observed, validator fault unproven |
| n028 | answered → insufficient; false insufficiency | Exact producer registration/tuple and consumer details missing | R2; V1, medium | Relevant `.cxx` channel hits missed pool; `INVALID_SUPPORTER` observed, contract contradiction unproven |
| n029 | answered → answered; incomplete | Named `PndRingSorter` cells, `AddElement`, `WriteOutElements`, timestamp multimap ordering omitted | R1; Q1/Q2, medium | Implementation exists in locked corpus but absent trace |
| n031 | answered → answered; incomplete | Prior `DPMGenerator` and random BoxGenerator versus fixed-step gun distinction omitted | Generation; V1/G2, high | Requested distinction in cited final source; runtime coverage accepted |

The other complete cases remain individually recorded in the machine result. `n004` retains the raw `fairlogger/Logger.h` identifier flag, but the literal appears in cited source snippets; the reviewed claim does not establish a major unsupported assertion. `n015` cites the official troubleshooting RST rather than the Gold Sphinx selector; its `cmake -DNOVC=1` and disabled-component facts are independently supported. `n027` likewise uses equivalent official Jupyter documentation. These observations are source-authority judgments, not Gold edits or case waivers.

No wrong-version evidence, forbidden evidence, or citation-integrity failure was observed across the 27 usable results. The bounded review established no additional major unsupported claim or observable contradiction; without an external judge it is not an exhaustive certification. `n022`, `n025`, and `n028` have visible review errors, but those receipts alone do not prove a validator defect. `n001`'s Gold/source conflict affects branch-execution assertions only and does not erase its separately established false refusal.

## G4 retention witnesses and causal signal

The G5 integrated run again shows `n002`'s two requirements objects (dense 7/8) admitted by `policy_role_frontier`, reranked and cited; its answer is complete. `n017`'s `PndTrack` object (dense 7) follows the same retained path and its answer is complete. `n024`'s helix header appears at dense 8/sparse 19, fused 18, enters the ordinary RRF pool, reranks 2, and reaches final/cited evidence. `n024` nevertheless omits critical supported details in generation. **These are G5 integrated observations, not independent G4 replication or replacements for `g4-r2-post-correction-exposed-target-v1`.** No observable contradiction of the accepted G4 R2 retention contract was established.

The candidate-level completeness signal is source detail available in final/cited evidence, followed by an incomplete answer with runtime coverage accepting it; `n020`, `n024`, and `n031` exhibit this pattern. It warrants a later generic owning-layer review, not a case-specific prompt rule or product change during this evaluation. Other cases show earlier channel/pool evidence-role losses. The older G4 28-case result and n002/n018 composite belong to a different product lineage and mixed provenance; they are directional history only, not G5 denominator or replacement evidence.

## Boundary and next step

The sole primary G5 blocker is the nonretryable `n018` product exception under the frozen incomplete-run precedence. Secondary diagnostic inventory: seven false insufficiencies, twelve answer-completeness blockers, one correct abstention, zero observed G4 R2 contract regressions, and the bounded n001 authority conflict. G6 entry requires G5 PASS, which was not obtained. The next recommended task is **G5 D1 NONRETRYABLE PRODUCT ERROR FAILURE REVIEW**, under separate authorization; it should address the generic owning layer before any new evaluation decision. No repair, G6 design, fresh cohort, release assessment, or protected-data access occurred here.

```text
PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
NEW_RUNTIME_MODE = false

NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0

EXPOSED_DEVELOPMENT_ONLY = true
FRESH_GENERALIZATION_EVIDENCE = false
NOVEL_VALIDATION_EVIDENCE = false
HOLDOUT_EVIDENCE = false
RELEASE_EVIDENCE = false

NEXT_TASK_EXECUTION_AUTHORIZED = false
```
