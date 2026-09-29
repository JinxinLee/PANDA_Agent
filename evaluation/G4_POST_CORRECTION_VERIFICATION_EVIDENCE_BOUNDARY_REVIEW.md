# G4 Post-Correction Verification Evidence Boundary Review

## 1. Decision and scope

```text
G4_POST_CORRECTION_VERIFICATION_EVIDENCE_BOUNDARY_REVIEW = PASS / FORWARD VERIFICATION PROTOCOL RECONCILED
SELECTED_EVIDENCE_MODEL = MODEL_B
HISTORICAL_EXACT_INPUT_RECOVERABLE = false
EXACT_HISTORICAL_REPLAY_STATUS = UNAVAILABLE
EXACT_HISTORICAL_REPLAY_ROLE = NON_BLOCKING_CORROBORATION
GENERIC_DETERMINISTIC_CORRECTION_AUTHORITY = SUFFICIENT
TARGETED_LIVE_OBSERVATION_REQUIRED = true
TARGETED_LIVE_CASES = [n002, n017, n024]
N006_LIVE_GATE = false
FULL_28_CASE_RERUN = false
EXACT_REPLAY_REQUIRED_BEFORE_LIVE = false
PREVIOUS_INCONCLUSIVE_RESULT_PRESERVED = true
PREVIOUS_PROTOCOL_RETROACTIVELY_RELABELED = false
```

`GENERIC_DETERMINISTIC_CORRECTION_AUTHORITY = SUFFICIENT` applies only to mechanism-level repair evidence. It does not establish current exposed behavior or fresh generalization. This review changes evidence policy and the forward verification protocol, not the R2 implementation. The product-behavior lineage remains `047201166057edd9859292a1760bc2e9bbf173a2`.

## 2. Current lifecycle and the previous stop

The [historical exposed regression](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION.md), [authorized n002/n018 rerun](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RERUN.md), and [collateral review](G4_R2_COLLATERAL_RETENTION_COMPLETENESS_FAILURE_REVIEW.md) establish the old n024 collateral displacement under unchanged channel rankings and RRF order, n002/n017 repair-consistent recoveries, and n006's separate role-quota and V1/G2 residuals. The historical exposed safety-regression `FAIL` remains historical fact. The [correction result](G4_R2_COLLATERAL_RETENTION_IMPLEMENTATION_RESULT.md) records CR-1 RED before the change and GREEN afterward, CR-1–CR-10, R2-A–I, 31/31 focused R2 tests, 18/18 G4 dual-sided controls, and relevant neighboring checks. No current-lineage exposed QA result follows from those tests.

The [previous design](G4_R2_POST_CORRECTION_EXPOSED_VERIFICATION_DESIGN.md) legitimately required exact saved-state Layer A `PASS` before live Layer B. The [execution result](G4_R2_POST_CORRECTION_EXPOSED_VERIFICATION.md) correctly stopped: all four historical inputs were `NOT_REPRODUCIBLE`, Layer A was `INCONCLUSIVE / SAVED INPUT NOT_REPRODUCIBLE`, and Layer B was not run. Its [machine result](G4_R2_POST_CORRECTION_EXPOSED_VERIFICATION_RESULT.json), counts, and verdict are unchanged. This is a prospective methodology revision; it is not a retroactive Layer A pass or an R2 product failure.

## 3. Bounded exact-input audit

The audit examined the two historical G4 run stores named by the prior design, their saved case records, stage traces and manifests, existing G4 machine summaries and analysis previews, the normalized corpus and ingestion receipt, and the directly relevant retrieval/evaluation contracts. It found no lossless historical constructor-input receipt or indexed payload snapshot. The proposed run store for `g4-r2-post-correction-exposed-target-v1` does not exist at this review.

The old channel rows save IDs, ranks and metadata, but omit candidate text for many members of the full channel union, including n024's critical incumbent. Selected final-output text covers only a subset. The old offered-pool receipt proves some old admissions, but cannot establish the full corrected reject-and-continue sequence. Aligned workflow/graph `normal` versus `generic_fallback` origins and occurrence sidecars were not retained. Some origins can be inferred from the recorded plan and retrieval branches for n002, n017 and n024; n006's workflow origin remains ambiguous. Branch inference is not a substitute for a replay-complete historical receipt, and missing candidate text independently prevents exact reconstruction for all four cases.

The normalized corpus has object text, but `ingestion.py` constructs `object_id` from version/type/canonical locator rather than text; `storage.py` can update text for an existing `object_id`. `indexing.py` index identity does not bind every selected object payload. `evaluation_runner.py` records source/normalized/index identities but does not attest that each database row returned during the historical run matched the normalized file. Thus matching object ID, version, corpus hashes, or current text does not prove the payload consumed by that run. Existing analysis files and manifest identity comparisons add no per-candidate text or aligned origin receipt. No alternative authorized immutable source meets the required historical-consumption standard. The audit ends here; later logging cannot repair the old record.

```text
HISTORICAL_EXACT_INPUT_RECOVERABLE = false
EXACT_HISTORICAL_REPLAY_STATUS = UNAVAILABLE
EXACT_HISTORICAL_COUNTERFACTUAL = UNOBSERVABLE
```

## 4. Evidence hierarchy and necessity

| Claim | Available evidence | Present conclusion |
|---|---|---|
| A: generic collateral-displacement mechanism is corrected | Historical n024 causal diagnosis; CR-1 old RED/new GREEN; bidirectional CR-2/CR-5; full focused deterministic controls | Supported at mechanism level |
| B: the new policy would preserve the exact old n024 input state | Exact old candidate payloads and origins were not saved | Unobservable; no counterfactual pass claimed |
| C: corrected R2 behaves acceptably on current-lineage exposed sentinels | Requires a new targeted live run | Not tested |

Exact replay would uniquely support Claim B: a paired old-state, exact-case counterfactual. Neither a generic fixture nor a new stochastic run can supply that exact historical statement. G4's scoped development decision, however, asks whether the identified failure class is repaired in the mechanism and whether the corrected current product behaves acceptably on the exposed R2 targets. Claim A plus an appropriately observed Claim C can answer that narrower question while Claim B remains unavailable. Making B indispensable would leave G4 permanently undecidable on the retained artifacts without adding a decision-relevant requirement for the current product. This does not erase the historical failure or upgrade deterministic tests into empirical evidence.

| Model | Evidence and decision |
|---|---|
| A: deterministic + exact old-state replay + live | Strongest paired historical corroboration, but unattainable with existing immutable records. Its unique exact-case inference is not necessary for scoped current-lineage closure. |
| B: historical diagnosis + deterministic RED→GREEN and bidirectional controls + targeted current-lineage live observation | Selected. Tests both the generic policy rule and the present exposed R2 decision surface, with the exact historical counterfactual explicitly unknown. |
| C: deterministic evidence only | Insufficient for exposed-development closeout because no corrected current-lineage retrieval/QA behavior has been observed. |

```text
HISTORICAL_CAUSAL_DIAGNOSIS = ESTABLISHED
GENERIC_RED_GREEN = VERIFIED
BIDIRECTIONAL_DETERMINISTIC_CONTROLS = VERIFIED
EXACT_HISTORICAL_COUNTERFACTUAL = UNAVAILABLE
CURRENT_LIVE_OBSERVATION = NOT_RUN
POST_CORRECTION_VERIFICATION_AUTHORITY = DETERMINISTIC_MECHANISM_EVIDENCE + TARGETED_CURRENT_LINEAGE_LIVE_OBSERVATION
```

## 5. Forward targeted live protocol

The previous exact Layer A prerequisite is superseded **for future execution only**. The next task, if separately authorized, uses one supported runner invocation with:

```text
RUN_ID = g4-r2-post-correction-exposed-target-v1
MODE = qa
SPLIT = novel_dev
CASE_IDS = [n002, n017, n024]
ALLOW_DRAFT = true
CAPTURE_STAGE_TRACE = true
EXTERNAL_JUDGE = false
RUN_ID_CREATED_AT_THIS_REVIEW = false
```

Before scientific calls, confirm the run ID remains unused and compare the prospective source/product lineage, corpus/index, dataset/Gold, prompt, model and retrieval-policy identities with the historical manifests. A design-only descendant HEAD is acceptable; a material product or input identity change needs a new decision before this protocol is used. Do not compose cases from different runs or prune them after outcomes. Completed cases and nonretryable product exceptions are not rerun. Resume only retryable provider/infrastructure failures within the same run, preserving its provenance. A product exception makes that case incomplete/error; it is not replaced by a more favorable attempt.

For each case, record actual pre-R2 channel membership and ranks, role/source/version and text validity, legacy RRF base, current offered-pool membership and reason, rank-witness condition, and final/cited/answer status. The actual R2 decision is the mechanism observation; answer quality alone is not. Compare to the historical case only at the causal level: relevant evidence, or independently valid equivalent evidence for the same information need, reaches the R2 candidate union with qualifying role/channel eligibility and an observable offer/exchange decision. Exact historical ranks, entire pool identity, and identical downstream reranker/generation outputs are not required.

```text
EXACT_PAIRED_HISTORICAL_COMPARISON = UNAVAILABLE
CURRENT_LINEAGE_R2_BEHAVIOR = OBSERVABLE | NOT_OBSERVABLE
```

Minor rank movement changes the paired-comparison description, not the current R2 verdict. If n024's qualifying evidence reaches R2, inspect whether its rank witness/opportunity survives or is legally replaced by an equal-or-better witness under the corrected policy. Observable illegal loss is `FAIL`; a current retained or legally replaced opportunity supports the correction. For n002/n017, when qualifying evidence reaches R2, require a legitimate offer and no new R2 opportunity regression; ordinary-base preservation is valid and need not be called a frontier rescue. If a target's relevant evidence never reaches R2, attribute upstream absence and mark that target's mechanistic observation `NOT_OBSERVABLE`, not R2 `FAIL`. A product exception that prevents the decision is incomplete/error. Record QA, coverage, final and cited evidence separately and attribute non-R2 failures to their actual layer.

A future **scoped G4 post-correction PASS** requires the already verified deterministic mechanism, one completed three-case targeted run, an observable n024 current R2 decision with no illegal witness/opportunity loss, and no observable n002/n017 R2 opportunity regression where their evidence reaches R2. An unobservable n024 decision, an incomplete run, or an unattributed product exception is `INCONCLUSIVE`, not a pass. An observable R2 violation is `FAIL`. If n002/n017 are upstream-unobservable, disclose the missing live benefit observation; deterministic bidirectional controls remain the mechanism-level preservation authority. This PASS would establish exposed current-lineage R2 correction support only. It would not establish exact historical replay, full-cohort quality, fresh generalization, protected validation, or release readiness. Retain the runner's own quality verdict separately; this causal G4 classification does not relabel it.

n006 remains a documented role-quota residual and separate V1/G2 diagnostic, not a live success gate. No 28-case rerun, extra sentinels, new outcome-conditioned attempts, or external judge are part of this protocol.

## 6. Future observability and lifecycle

A future stage trace could carry one replay-complete R2 input receipt with only fields consumed by the constructor: selected payload validity fields, per-channel occurrences, aligned specialized origin, RRF scores and stable base order, eligible supplements, and relevant `RetrievalPlan` fields. This would enable later exact replay without storing unrelated payloads. It is optional future observability work, not a retroactive reconstruction or a prerequisite for this G4 review or its targeted live successor. No tracing change is implemented here.

```text
R2_REPLAY_COMPLETE_RECEIPT_RECOMMENDED = true
CURRENT_G4_BLOCKED_ON_OBSERVABILITY_CHANGE = false
G5_ENTRY_AFTER_TARGETED_LIVE_PASS = true
G5_ENTRY_AUTHORIZED_NOW = false
NOVEL_VALIDATION = NOT_RUN
FRESH_GENERALIZATION = NOT_ESTABLISHED
RELEASE_READINESS = NOT_ESTABLISHED
PHASE_G = IN_PROGRESS / G4_POST_CORRECTION_EVIDENCE_BOUNDARY_RECONCILED
G4 = DETERMINISTIC CORRECTION VERIFIED / HISTORICAL COLLATERAL REGRESSION ESTABLISHED / HISTORICAL EXACT REPLAY UNAVAILABLE / EXACT REPLAY NON_BLOCKING / TARGETED CURRENT-LINEAGE LIVE VERIFICATION REQUIRED / FRESH GENERALIZATION BENEFIT NOT_ESTABLISHED
NEXT_TASK_RECOMMENDATION = G4 POST-CORRECTION TARGETED LIVE VERIFICATION EXECUTION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

Only a later targeted live PASS can permit separately authorized G5 development integration. A live `FAIL` or `INCONCLUSIVE` keeps G5 blocked. Historical Layer A `INCONCLUSIVE` and historical exposed `FAIL` remain readable as their original results. Fresh Lane B, `novel_validation`, and release evaluation retain their separate authorization boundaries.

## 7. Accounting and protected boundary

```text
EVIDENCE_POLICY_CHANGE = true
VERIFICATION_PROTOCOL_CHANGE = true
PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
QA_RUNS = 0
RETRIEVAL_RUNS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```
