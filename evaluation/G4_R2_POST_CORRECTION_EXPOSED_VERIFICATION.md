# G4 R2 Post-Correction Exposed Verification: Saved-Input Boundary

## Decision

```text
G4 POST-CORRECTION EXPOSED VERIFICATION = INCONCLUSIVE / SAVED INPUT NOT_REPRODUCIBLE
LAYER_A_INPUT_REPRODUCIBILITY = NOT_REPRODUCIBLE
LAYER_A_REPLAY_EXECUTED = false
LAYER_A_CONSTRUCTOR_INVOCATIONS = 0
LAYER_B_AUTHORIZED = false
LAYER_B_EXECUTED = false
```

The [frozen design](G4_R2_POST_CORRECTION_EXPOSED_VERIFICATION_DESIGN.md) requires exact reconstruction of the historical R2 constructor input before replay, and Layer A `PASS` before any live QA. The selected historical records and traces exist, but they omit input fields that the corrected constructor uses. This is an evidence boundary, not a negative result for the rank-witness correction. No corrected pool was computed from these saved cases and no live run was created.

At entry, `git rev-parse HEAD` returned `a076e66938e41ffb7d33498af2d248841cbe5cee`, `git status --short` was empty, and the expected eight-commit history was present. The only intervening changes since product commit `047201166057edd9859292a1760bc2e9bbf173a2` were the frozen design and two documentation files. Product-behavior lineage is unchanged. The previous exposed regression remains a historical FAIL under `a22c8f70eeebe4a53490e11a4b6852561ca8afa6`.

## Read-only artifact qualification

The authorized historical stores are:

```text
data/evaluation/runs/g4-r2-post-repair-novel-dev-regression-v1
data/evaluation/runs/g4-r2-post-repair-n002-n018-rerun-v1
```

Use n002 from the successful rerun and n006/n017/n024 from the initial 28-case run. All four selected successful `records/<id>.json` and `traces/<id>.json` files exist. For each selected case, `results.jsonl` and `attempts.jsonl` contain the same case record, and `retrieval_traces.jsonl` contains the same retrieval trace as its case file; those copies add no omitted candidate payload or provenance fields. The two run manifests agree on source, normalized corpus/output, index, Gold/dataset, prompt, generation/embedding models and dimensions, retrieval policy, and query-expansion identities. Stage-trace capture is enabled in both runs.

The [initial regression result](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RESULT.json), [authorized rerun result](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RERUN_RESULT.json), and [collateral analysis](G4_R2_COLLATERAL_RETENTION_ANALYSIS.json) were also checked as immutable summaries. They contain no complete candidate-text map or aligned workflow/graph origin sidecar. The [collateral failure review](G4_R2_COLLATERAL_RETENTION_COMPLETENESS_FAILURE_REVIEW.md) had already identified conditional lower/upper specialized-origin reconstruction; that conditional agreement with old selected frontiers is not exact historical input recovery. The [implementation result](G4_R2_COLLATERAL_RETENTION_IMPLEMENTATION_RESULT.md) proves deterministic CR controls, not exact replay of these exposed cases.

## Exact missing inputs and why they matter

`Retriever._r2_rerank_pool()` calls `valid_challenger()` for each ordinary candidate. It requires a truthy selected payload `text` and `locator`, among other fields. It then builds each active role/channel witness only from valid payloads and, for workflow/graph occurrences, only from explicit `origin == "normal"`. Unknown text validity or specialized origin can change the challenger queues, the initial incumbent vectors, legal exchange victims, and final offer. The saved channel rows include object ID, rank, source/version, type, and locator metadata, but no `text`; the saved record/trace includes text for only a subset of final outputs. Neither record nor trace contains aligned specialized-origin fields. Current corpus text or guessed branch origin would not prove the actual historical selected payload or occurrence sidecar and is not a permitted substitute under the frozen design.

The counts below describe field **availability**, not assertions that the omitted objects had empty text. `Regular outside base` counts objects on exact/dense/sparse/paper channels outside the saved legacy top 30 for which no text is recorded in the selected record or trace. They show why even direct-channel challenger validity cannot be recovered for the complete old input. The saved historical offer can establish eligibility for some already offered IDs, but not for all omitted candidates that the corrected policy might visit after rejecting an earlier exchange.

| Case | Role | Channel-union IDs | IDs with text anywhere in case record/trace | IDs without recorded text | Regular outside-base IDs without text | Workflow/graph rows | Origin sidecar |
|---|---|---:|---:|---:|---:|---:|---|
| n002 | R2 benefit sentinel | 58 | 9 | 49 | 23 | 20 / 1 | absent |
| n006 | Quota residual diagnostic | 79 | 12 | 67 | 31 | 6 / 17 | absent |
| n017 | R2 benefit sentinel | 79 | 12 | 67 | 22 | 20 / 20 | absent |
| n024 | Primary collateral target | 85 | 10 | 75 | 25 | 20 / 15 | absent |

- **n002 — `NOT_REPRODUCIBLE`:** The second historical requirements object, `object.03af96b1110e782792253a18`, has no recorded text in the selected record/trace, although its old offered receipt shows it was once admitted. Another 23 regular-channel objects outside the legacy base lack recorded text, and specialized origins are absent. The receipt cannot establish the complete queue and witness state under the new reject-and-continue policy. `N002_REPLAY_OPPORTUNITY_PRESERVED` is unobserved.
- **n006 — `NOT_REPRODUCIBLE`:** The omitted constructor `object.2914485ff398f61e994c46d6` has no recorded text; 31 regular-channel outside-base objects also lack it. Workflow/graph origins are absent, and these channels participate in the historical overlapping role queues. The previous conditional queue-position account cannot certify the corrected exact exchange sequence. n006 remains `NOT_REPRODUCIBLE`, not a newly observed guard or quota outcome.
- **n017 — `NOT_REPRODUCIBLE`:** The primary target has selected-output text, but 22 other regular-channel outside-base IDs lack recorded text and specialized origins are absent. The target's own text does not make the full corrected pool input exact. `N017_REPLAY_OPPORTUNITY_PRESERVED` is unobserved.
- **n024 — `NOT_REPRODUCIBLE`:** The critical RRF-rank-18 helix header `object.d6ef560b88c3926ecb32d3e1` was removed from the old actual offer and has no text in the selected G4 record/trace. Its current-code witness validity therefore cannot be reconstructed from these stores. Another 25 regular-channel outside-base IDs lack recorded text; specialized origins are absent. Whether the corrected policy retains this object, legally replaces its witness, or permits illegal loss is unobserved. `N024_ILLEGAL_COLLATERAL_DISPLACEMENT_REPRODUCED` is unknown, not false.

The saved authoritative `fused_candidates` and old `rerank_pool_entries` provide the historical RRF top 30 and actual old offer. No lossless candidate input was available to independently reproduce the old pre-correction offer. Therefore `REPLAY_INPUT_REPRODUCIBILITY = NOT_REPRODUCIBLE`; the design's old-pool reproduction gate was not attempted and is not labelled `FAIL`. The corrected constructor was not invoked. No conditional lower/upper reconstruction was promoted into the exact replay gate.

## Layer B and scoped classification

```text
LAYER_A_VERDICT = INCONCLUSIVE / SAVED INPUT NOT_REPRODUCIBLE
LAYER_B_AUTHORIZED = false
LAYER_B_EXECUTED = false
PLANNED_RUN_ID = g4-r2-post-correction-exposed-target-v1
PLANNED_RUN_CREATED = false
QA_RUNNER_INVOCATIONS = 0
QA_CASE_ATTEMPTS = 0
SUPPORTED_RESUMES = 0
```

The frozen live cohort `[n002, n017, n024]` was not run. There are no current upstream-comparability findings, corrected pool entries, final/cited results, QA answer classifications, or runner quality verdict for that run. The absence of live results is required by the Layer A hard prerequisite. This task does not conclude that n024 was repaired or that n002/n017 regressed. Historical n006 quota and separate V1/G2 concerns retain their previous meaning.

The smallest next step is a separate **G4 POST-CORRECTION VERIFICATION EVIDENCE BOUNDARY REVIEW**: decide whether any authorized immutable source can prove the missing historical payload/provenance fields or whether the exact-replay prerequisite requires a forward design change. This execution does not relax the frozen gate, start a fresh run, change product policy, or enter G5.

## Accounting, materiality, and lifecycle

```text
QA_RUNS = 0
RETRIEVAL_RUNS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
GENERATION_CALLS = 0
EMBEDDING_CALLS = 0
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

FULL_28_CASE_POST_CORRECTION_REGRESSION = false
FRESH_GENERALIZATION_EVIDENCE = false
NOVEL_VALIDATION_EVIDENCE = false
RELEASE_EVIDENCE = false

PHASE_G = IN_PROGRESS / G4_POST_CORRECTION_VERIFICATION_INCONCLUSIVE
G4 = DETERMINISTIC CORRECTION VERIFIED / HISTORICAL COLLATERAL REGRESSION ESTABLISHED / POST-CORRECTION EXPOSED VERIFICATION INCONCLUSIVE / SAVED INPUT NOT_REPRODUCIBLE / LAYER B NOT_RUN / FRESH GENERALIZATION BENEFIT NOT_ESTABLISHED
G5_ENTRY_AUTHORIZED = false
FRESH_LANE_B = OPTIONAL / DEFERRED
NEXT_TASK_RECOMMENDATION = G4 POST-CORRECTION VERIFICATION EVIDENCE BOUNDARY REVIEW
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
