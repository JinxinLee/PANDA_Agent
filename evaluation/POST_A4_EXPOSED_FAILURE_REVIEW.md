# Post-Attempt-4 Exposed Failure Review

## Terminal state

`COMPLETE / PASS / FAILURES_CLASSIFIED_PRODUCT_RESIDUALS_DEFERRED_INFRASTRUCTURE_REPAIRED`

This review uses only immutable stored records, traces, Gold v2.10, source/index artifacts, and repository code. No PANDA scientific or evaluation call was made.

## Starting and immutable state

- Starting HEAD: `9c26efde1c1be3b5892f30ea446d0cc15a100444` (`Record F6-A attempt 4 result`).
- The only starting worktree item was the regenerable untracked `data/_a3_gold_args.txt`.
- Attempt 4 remains `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED` on `m6-benchmark-v2.10` and calibration `phase_b_t3_product_language_scope_v7`.
- A1 scored 59/59 records. Release score was `0.9717514124293786`; critical final-evidence recall was `0.9285714285714286`; critical answer-point misses were `g013.p3` and `g037.p1`.
- A2-A5 remained `NOT_REACHED`. Official Attempt-4 usage remains 388 calls / 3,647,993 tokens.
- Accepted product-development HEAD remains `d3a1b274b2784399a7dc51b094a17e466d208b50` because this task changes evaluation infrastructure only.

## Case-level root-cause matrix

| Case | Primary classification | Disposition | Stored-evidence conclusion |
|---|---|---|---|
| g013 | PRODUCT_DEFECT | DEFERRED_NO_SAFE_GENERIC_FIX | The candidate pool matched both Gold groups, but selected context contained no PndMasterRunSim implementation capable of supporting event-loop orchestration. The live question was represented only by legacy question_core rather than a tracked lifecycle obligation. Supported setup and macro claims survived without revision; no supported p3 claim ever existed, so final evidence could not recover it. A separate citation-choice loss omitted g013.e1 despite selected Macros documentation. |
| g037 | EXPECTED_STOCHASTIC_VARIATION | NO_PRODUCT_ACTION | Gold code was rank 1 and selected together with the downstream PndMasterMultiPidTask consumer. Stored diagnostics show no user-visible claims, one revision, and a correct safe fallback after no supported claim was produced. Attempt 3 answered correctly from the same stored retrieval context, so the isolated loss is located in model claim generation rather than deterministic retrieval or salvage code. |
| g011 | PRODUCT_DEFECT | DEFERRED_NO_SAFE_GENERIC_FIX | Both native-installation and container Gold evidence were retrieved and selected. The complete final comparison cited only Docker documentation that substantively covered both sides, leaving the separately selected native-installation source uncited. This is recurrent selective citation convergence, not retrieval or pruning loss. |
| g044 | PRODUCT_DEFECT | DEFERRED_NO_SAFE_GENERIC_FIX | The required Pflueger thesis page was retrieved and selected at the top of context, but complete supported claims cited the Li 2026 thesis and curated concept instead. No evidence pruning occurred. This repeats a stable peer-authority citation preference already governed as a product residual. |
| g059 | EXPECTED_STOCHASTIC_VARIATION | NO_PRODUCT_ACTION | Both Gold code files were retrieved and selected. After one revision, the complete answer cited factory and facade code but omitted the dedicated convolution-class implementation. Attempt 3 cited both Gold groups, so this isolated citation consolidation is not a stable deterministic defect. |

## Cluster A: content and evidence jointly missing

### g013

The combined pool matched both Gold evidence groups, and selected context contained installation, macro, Master Tasks overview, and macro README material. It did not contain the `PndMasterRunSim` implementation needed to explain configuration and event-loop orchestration. Runtime requirements did not preserve a dedicated lifecycle obligation: final claim audit entries were attached only to `question_core`. The generator made supported setup and invocation claims plus a supported statement that lifecycle internals were not documented; verification accepted those claims and no revision ran. Safe salvage removed nothing. Consequently no supported `p3` claim ever existed, and final evidence could not recover the absent content. A second loss omitted selected `Running/Macros` evidence from final citations.

The post-A3 diagnostic and Attempt 4 independently produced the same `0.6667` answer-point coverage, `0.5` final-evidence recall, and the same three final documents. This establishes a product residual at candidate/obligation granularity, but it does not establish a safe generic repair: a phrase-to-class mapping would be case-specific, forced citation retention is forbidden, and a new semantic resolver would exceed the bounded task.

### g037

The Gold macro was rank 1 and selected with the downstream implementation that reads `POCA_VERTEX_FILE`. Stored diagnostics record `no user-visible claims`, one revision, and then a faithful insufficient-evidence fallback with no claims or citations. Safe salvage behaved correctly because there was no supported claim to retain. Attempt 3 produced a fully correct answer from the same retrieval context. The single A4 refusal therefore remains expected model variation rather than a deterministic product defect.

## Cluster B: critical final evidence missing

`g011` and `g044` share a stable downstream citation-selection residual. Both had full candidate recall, full substantive answer coverage, and selected Gold support; both repeatedly cited alternate valid support rather than every Gold-pinned source. `g011` converged on Docker documentation that covered both native and container paths. `g044` preferred the Li 2026 thesis over the selected Pflueger thesis. Existing governance for these two cases remains unchanged.

`g059` has the same metric symptom but weaker recurrence. Attempt 3 cited both Gold code groups; Attempt 4 still answered all points after one revision but consolidated citations onto factory/facade code and omitted the dedicated convolution implementation. This is classified as expected stochastic citation variation, not part of the stable `g011`/`g044` mechanism.

## Product decision

`NO_SAFE_GENERIC_FIX`

No product file changed. Positive comparison (`g037` and `g059` in Attempt 3) demonstrates that identical support can yield complete results; recurrent controls (`g011`, `g013`, and `g044`) localize stable residuals. Those controls do not justify source-specific triggers, Gold-aware runtime behavior, forced attach-all evidence, citation quotas, verifier weakening, or a parallel planning/verifier pipeline. Faithfulness, version checks, forbidden-evidence filtering, semantic verification, safe salvage, coverage-mode authority, question-grounded source obligations, generation/verifier separation, and composer provenance boundaries remain unchanged.

## A4-PD1 forward-only repair

Root cause: `evaluation/scripts/f6a_gate_evaluation.py` did not use the repository environment bootstrap, while `resolve_candidate_binding` converted every verification exception into `candidate_valid = false`. The first Attempt-4 invocation therefore sealed a misleading candidate-invalid receipt.

Repair in commit `83a51ff`:

- load `<project-root>/.env` before candidate resolution;
- add opt-in strict exception propagation to candidate binding;
- use strict binding only in the standalone gate path;
- preserve clean verification results where `valid = false` as an `INCONCLUSIVE` identity outcome;
- abort environment/verification exceptions before writing a matrix or receipt.

The initial A4-PD1 matrix and receipt were not changed. Existing `--source-matrix` forward-only validation and gate-value preservation remain covered.

## Stage-receipt identity repair

Root cause: `build_evaluation_manifest` loaded the Gold dataset but omitted `dataset.benchmark_version`; `_build_stage_receipt` correctly read `manifest.gold_benchmark_version`, which was therefore null.

Future run manifests now bind `gold_benchmark_version` directly from the loaded dataset while retaining the existing `gold_dataset_hash`. Legacy resumes harmonize absent/null version fields before immutable manifest comparison. No fallback was added to historical receipt recomputation, so the Attempt-4 null remains immutable.

## Verification

Test-first RED evidence before implementation: 5 failed and 35 passed in the focused gate/finalization files. After implementation and supervisor integration, the focused acceptance command passed 105 tests across gate CLI, finalization contract, runner lifecycle, execution recovery, F6-A release infrastructure, and F6 release identity. One existing Qdrant client/server compatibility warning was emitted. `git diff --check` passed. The two declared legacy fixture-debt tests were outside scope and were neither run nor changed.

An independent AGY read-only review accepted the five-file infrastructure patch and found no blocking defect; its only non-blocking observation was the absence of a direct legacy-resume branch test. The lifecycle and recovery suites passed, and the branch is a narrow manifest-field harmonization.

## Governance, readiness, and protected state

No objective Gold contract defect or evaluator defect was established. Gold v2.10 remains frozen and coherent; no successor was created. Attempts 1-4 and the post-terminal diagnostic remain immutable.

`ATTEMPT_5_READINESS = READY`

This means the execution-artifact blockers are repaired and no high-confidence safe generic product repair remains before a fresh run. It is not a prediction that Attempt 5 will pass.

- `PANDA scientific/evaluation calls = 0`
- `PANDA scientific/evaluation tokens = 0`
- `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`
- `holdout access = 0`
- `protected-content leakage = 0`
- `F6-B execution = 0`
- `candidate frozen = false`
- `Attempt 5 preregistered = false`
- `Attempt 5 executed = false`
- `push performed = false`
