# G4 Post-Correction Targeted Live Verification

## 1. Decision and authority

```text
G4_POST_CORRECTION_TARGETED_LIVE_VERIFICATION = PASS / CURRENT-LINEAGE EXPOSED R2 CORRECTION SUPPORTED
SELECTED_EVIDENCE_MODEL = MODEL_B
IDENTITY_PREFLIGHT = PASS
EVALUATED_REPOSITORY_HEAD = e2c59740f5736bf520a2241d267364bae867d381
EVALUATED_PRODUCT_BEHAVIOR_LINEAGE = 047201166057edd9859292a1760bc2e9bbf173a2
EXACT_HISTORICAL_COUNTERFACTUAL = UNAVAILABLE
PREVIOUS_INCONCLUSIVE_RESULT_PRESERVED = true
PREVIOUS_PROTOCOL_RETROACTIVELY_RELABELED = false
FULL_28_CASE_POST_CORRECTION_REGRESSION = NOT_RUN
FRESH_GENERALIZATION_EVIDENCE = false
NOVEL_VALIDATION_EVIDENCE = false
RELEASE_EVIDENCE = false
```

This is the single targeted live execution authorized under the forward [G4 evidence-boundary review](G4_POST_CORRECTION_VERIFICATION_EVIDENCE_BOUNDARY_REVIEW.md). The [previous exact-replay execution](G4_R2_POST_CORRECTION_EXPOSED_VERIFICATION.md) remains `INCONCLUSIVE / SAVED INPUT NOT_REPRODUCIBLE`; no historical replay was retried or relabeled. The old [exposed safety regression](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION.md) remains a historical `FAIL`. The [deterministic correction](G4_R2_COLLATERAL_RETENTION_IMPLEMENTATION_RESULT.md) remains the mechanism-level RED→GREEN authority. This result adds current-lineage observations; it does not estimate an isolated QA effect or fresh generalization.

## 2. Identity preflight and run

At entry, Git HEAD was the expected `e2c59740f5736bf520a2241d267364bae867d381` and the worktree was clean. All descendants of product lineage `047201166057edd9859292a1760bc2e9bbf173a2` changed only G4 review/status/roadmap artifacts; product source, tests, configuration, prompts and data had no later Git changes. The proposed run directory did not exist before launch. The supported `build_evaluation_manifest()` read the configured index identity without a model call. Its current identity was compared with both historical G4 manifests before any scientific call.

| Identity dimension | Preflight result |
|---|---|
| Product-behavior lineage | `047201166057edd9859292a1760bc2e9bbf173a2` unchanged; current HEAD is a documentation-only descendant |
| Source manifest and normalized corpus/output identities | Match both historical G4 runs |
| Index fingerprint and identity payload | Match both historical G4 runs |
| `novel_dev` dataset hash and benchmark version | Match; `novel-v1-dev-0.3.0` |
| Prompt version and fingerprint | Match; `3.12.0` |
| Generation and embedding configuration | Match; `gemini-3.8-flash`, `gemini-embedding-2`, 3072 dimensions; judge configuration also matches but judge not invoked |
| Retrieval policy and query-expansion identities | Match both historical G4 runs |

Runtime packages differ from those historical runs: Python `3.12.14 -> 3.13.14`, LangGraph `1.2.10 -> 1.2.11`, and Qdrant client `1.15.1 -> 1.19.0`. Qdrant emitted a client/server compatibility warning for server `1.15.5`; the run completed. These are comparison confounds, not a silently changed product, corpus or index identity. No package was installed or downgraded. Provider nondeterminism remains a separate limit.

```text
RUN_ID = g4-r2-post-correction-exposed-target-v1
MODE = qa
SPLIT = novel_dev
CASE_IDS = [n002, n017, n024]
ALLOW_DRAFT = true
CAPTURE_STAGE_TRACE = true
EXTERNAL_JUDGE = false
QA_RUNNER_INVOCATIONS = 1
QA_CASE_ATTEMPTS = 3
SUPPORTED_RESUMES = 0
RUNNER_STATUS = COMPLETE / 3 OF 3 SCORED
RUNNER_QUALITY_VERDICT = FAIL
```

The supported runner's [manifest](../data/evaluation/runs/g4-r2-post-correction-exposed-target-v1/manifest.json), [status](../data/evaluation/runs/g4-r2-post-correction-exposed-target-v1/run_status.json), [report](../data/evaluation/runs/g4-r2-post-correction-exposed-target-v1/report.md), and individual `records/` and `traces/` under that run ID are the primary raw artifacts. The runner's exact cohort decision is `COMPLETE / FAIL` (`complete cohort (3/3 scored); quality gates failed`). Its focused draft run cannot pass the full development gate (`complete_full_dev=false`); intent accuracy is `2/3`, and the product-language development gate reports incompatible calibration Gold version for this dataset. This runner verdict is preserved, not relabeled as a full `novel_dev` result. The scoped G4 causal verdict below asks a narrower R2 question.

## 3. Current R2 observations

The current [machine result](G4_POST_CORRECTION_TARGETED_LIVE_VERIFICATION_RESULT.json) records each selected object's source/version, role/channel ranks, RRF membership, actual `rerank_pool_entries`, final/cited IDs, answer review and usage. The raw channel rankings, decomposition, plan, fused order, stage events and final evidence remain in the single run store. All three relevant information needs reached an observable R2 decision. Their witnesses use regular dense/sparse channels, so missing public specialized-origin sidecars do not affect these target observations. Each offered target matched its plan-resolved source version; frontier admissions passed the current constructor's payload-validity checks. The n024 final/cited header also has nonempty current text. The trace reports final pool membership and reason, but not each internal exchange's victim and rank-witness vector; none is inferred from answer quality.

| Case | Relevant current geometry | Legacy RRF / actual offer | Downstream | R2 verdict |
|---|---|---|---|---|
| n024 primary collateral target | `object.d6ef560b88c3926ecb32d3e1`, `PndHelixPropagator.h`, code/dense 8 and code/sparse 19; RRF rank 18, score `0.027364110201042444`. GEANE header is dense 5/sparse 20, RRF 15. | Both headers remain `ordinary_rrf` in a 19 ordinary / 11 frontier pool. The helix witness is not displaced. | Helix reranked 2, final and cited; GEANE reranked 1, final and cited. | `OBSERVABLE`; `ILLEGAL_R2_OPPORTUNITY_LOSS=false`. |
| n002 benefit sentinel | Two `requirements.txt` objects, code/dense ranks 7 and 8, resolved LuminosityFit version. | Both outside legacy RRF top 30; both admitted as `policy_role_frontier` in a 22 ordinary / 8 frontier pool. | Reranked 1 and 2; first final and cited. | `OBSERVABLE`; `R2_OPPORTUNITY_REGRESSION=false`; live benefit preservation observed. |
| n017 benefit sentinel | `object.015bff352e03a5f5ee88c307`, `PndTrack.h`, code/dense rank 7, resolved PandaRoot version. | Outside legacy RRF top 30; admitted as `policy_role_frontier` in a 19 ordinary / 11 frontier pool. | Reranked 1, final and cited. | `OBSERVABLE`; `R2_OPPORTUNITY_REGRESSION=false`; live benefit preservation observed. |

The n024 critical helix object has the same relevant dense/sparse ranks, RRF rank and score reported for the historical displacement, yet the current policy retains it through 11 frontier admissions. This is strong current-lineage local mechanism evidence, not a replay of the exact old constructor input: other current candidate payloads and provenance were not reconstructed as historical inputs. The ordinary-pool receipt plus current final/cited text establishes that this witnessed opportunity survived R2. No current observed pool behavior contradicts the deterministic rank-witness correction contract. n002/n017 show preserved single-channel benefit opportunities; this does not claim that their new answers are isolated causal effects of the correction.

## 4. Answer outcomes and causal ownership

The answer classification applies the existing G4 distinction between runtime canonical coverage and a bounded review against critical `novel_dev` Gold details. No external judge was called. All three runtime coverage receipts are `VALID`, with no missing canonical points, citation integrity `1.0`, and critical final-evidence recall `1.0` for this three-case run. Those metrics alone do not certify semantic completeness.

| Case | Bounded answer classification | Evidence and ownership |
|---|---|---|
| n002 | `ANSWERED_COMPLETE` | The cited `requirements.txt:1-12` supports all twelve listed packages and the file location. No supported omission; causal owner `null`. |
| n017 | `ANSWERED_COMPLETE` | The cited `PndTrack.h:23-126` supports the first/last `FairTrackParP` endpoints and embedded `PndTrackCand`/`TRef` links requested. No supported omission; causal owner `null`. |
| n024 | `ANSWERED_INCOMPLETE` under conservative Gold-detail review | The answer identifies both propagators and their main numerical/analytic mechanisms, but omits Gold-critical error/transport-matrix handling, circle-center/backward-propagation details, and the shared `PndPropagator` interface. These are visible in cited final headers. The earliest visible omission is `GENERATION`; V1/G2 accepted narrower canonical points as a secondary completeness concern. There is no R2 evidence loss. |

The n024 answer-level limitation cannot be counted as a remaining R2 collateral displacement: its critical header is in the actual rerank pool, final evidence and citation. Conversely, the improved answer cannot by itself prove the exact historical counterfactual. The targeted runner's `FAIL` and the scoped R2 `PASS` therefore answer different, explicitly recorded questions.

## 5. Decision and limits

The forward Model B scoped conditions are satisfied: preflight passed; one three-case run completed with no exception or resume; n024's relevant R2 decision is observable and preserves the previously lost witness; both benefit sentinels have observable legitimate offers; and no runtime pool decision contradicts the deterministic guard. The scoped result is:

```text
G4_POST_CORRECTION_TARGETED_LIVE_VERIFICATION = PASS / CURRENT-LINEAGE EXPOSED R2 CORRECTION SUPPORTED
N024_CURRENT_R2_OBSERVABILITY = OBSERVABLE
N024_ILLEGAL_R2_OPPORTUNITY_LOSS = false
N002_CURRENT_R2_OBSERVABILITY = OBSERVABLE
N002_LIVE_BENEFIT_PRESERVATION_OBSERVED = true
N017_CURRENT_R2_OBSERVABILITY = OBSERVABLE
N017_LIVE_BENEFIT_PRESERVATION_OBSERVED = true
N006_LIVE_GATE = false
FULL_28_CASE_RERUN = false
```

The result does **not** establish an exact old-state n024 counterfactual, a full 28-case post-correction regression pass, all-answer completeness, fresh generalization, `novel_validation`, release readiness, or product-language calibration compatibility. The exposed cohort and answer review are development diagnostics. The Qdrant client/server warning and package changes limit exact historical comparability, although the identity preflight and observed target geometry passed. No product repair or tuning follows from n024's answer-level omission in this task.

## 6. Scientific accounting, protected boundary, and lifecycle

The runner's cumulative counters match the three records: n002 `6 calls / 31,907 tokens`, n017 `6 / 129,893`, n024 `6 / 37,997`; each case used five generation calls and one embedding call. No external judge call or supported resume occurred.

```text
QA_RUNNER_INVOCATIONS = 1
QA_CASE_ATTEMPTS = 3
SUPPORTED_RESUMES = 0
SCIENTIFIC_CALLS = 18
SCIENTIFIC_TOKENS = 199797
GENERATION_CALLS = 15
EMBEDDING_CALLS = 3
EXTERNAL_JUDGE_CALLS = 0

NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0

PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false

PHASE_G = IN_PROGRESS / G4_COMPLETE_POST_CORRECTION_TARGETED_LIVE_VERIFIED
G4 = DETERMINISTIC CORRECTION VERIFIED / HISTORICAL COLLATERAL REGRESSION ESTABLISHED / HISTORICAL EXACT REPLAY UNAVAILABLE / CURRENT-LINEAGE EXPOSED R2 CORRECTION SUPPORTED / FRESH GENERALIZATION BENEFIT NOT_ESTABLISHED
G5_ENTRY_AFTER_TARGETED_LIVE_PASS = true
G5_EXECUTED = false
NOVEL_VALIDATION = NOT_RUN
FRESH_GENERALIZATION = NOT_ESTABLISHED
RELEASE_READINESS = NOT_ESTABLISHED
NEXT_TASK_RECOMMENDATION = G5 INTEGRATED CANDIDATE DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
