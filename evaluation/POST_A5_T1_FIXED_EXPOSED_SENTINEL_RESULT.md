# Post-A5 T1 — Fixed Exposed Sentinel Result

Status: `COMPLETE / FAIL / SENTINEL_A_AND_B1_TARGETS_MISSED_AGAIN`

Machine-readable companion: `evaluation/post_a5_t1_fixed_exposed_sentinel_result.json`. Preregistration: `evaluation/POST_A5_T1_FIXED_EXPOSED_SENTINEL_PREREGISTRATION.md`, committed as `421c13a6efc76a845cfd61388e1e2520eea799a7` **before** every T1 scientific call. T1 is development evidence, not formal release authority; Attempt 5 remains `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`.

## 1. Execution

- Product-behavior head: `e79d3232ed132a224cbceaf3524e19a1406bd648`; prompt fingerprint `0a5b2909…`; Gold `m6-benchmark-v2.11`; calibration `phase_b_t3_product_language_scope_v8`; mode `production_answer_obligations_v1` — all unchanged from preregistration through execution.
- Fixed order executed exactly: `g011 → g010 → g013 → g014 → g023 → g022 → g047 → g050`, eight single-case official `panda-qa-eval` invocations (existing `--case-id` mechanism, run ids `post-a5-t1-<case_id>`), no runner/evaluator modification.
- All 8 executions completed scientifically; **zero transport-recovery events**; no reruns; no cohort edits.
- T1-only usage: **65 calls / 373,265 tokens** (external judge 8 / 44,042; runtime QA-generation-labeled 11 / 155,830; runtime QA-composer-labeled 10 / 11,143; 8 embedding calls; decomposition/verification/revision share the unlabeled runtime bucket — not estimated).

## 2. Sentinel verdicts

| Sentinel | Outcome | Evidence |
| --- | --- | --- |
| A — g013 completeness recovery | **FAIL** | `critical_answer_points_missing = ["p3"]`: the master-run-task/lifecycle obligation was missed again. Bounded revision was naturally triggered (`revision_count = 1`); the repaired recovery path's exercise is **NOT_OBSERVABLE** (the revision-round pre-merge payload is not retained, so whether an ID collision with surviving new content occurred cannot be determined). `A_REVISION_RECOVERY_RUNTIME_EFFECT = NOT_DIRECTLY_OBSERVED`. |
| B1 — g023 workflow completeness | **FAIL** | p3 (before PID in the generic workflow) judged missing again. The runtime coverage review **false-accepted again** (`coverage_complete = true`, `missing_answer_point_ids = []`, `revision_count = 0`) while the external judge found p3 uncovered; the final answer does not state the requested workflow position. |
| B2 — g047 relationship completeness | **PASS** | The critical relationship (elastic differential cross section ↔ luminosity extraction) judged covered; no hard-safety violation. |
| C — g011 negative-existence safety | **PASS** | The final answer **positively describes both the native and the container setup paths** and contains no unqualified corpus/documentation-wide negative-existence assertion; the historical false claim pattern did not recur; both claims verified supported. |

Workstream-specific effect fields (conservative, per preregistration): `A_REVISION_RECOVERY_RUNTIME_EFFECT = NOT_DIRECTLY_OBSERVED`; `B_RUNTIME_SEMANTIC_EFFECT = MIXED_SINGLE_OBSERVATION / NOT_YET_SCIENTIFICALLY_VALIDATED`; `C_RUNTIME_SAFETY_EFFECT = POSITIVE_SINGLE_OBSERVATION / NOT_YET_SCIENTIFICALLY_VALIDATED`. Single observations are not general proof of any repair effect.

## 3. Retrieval completeness (separate axis, mandatory separation)

`C_RETRIEVAL_COMPLETENESS = FAIL`: the native-documentation critical role (`g011.e1`) remained unmatched in the final evidence (`critical_final_evidence_recall = 0.5`; only `g011.e2` matched, via ancestor). This is the Workstream-D mechanism that remains `DEFERRED / NO_SAFE_GENERIC_REPAIR_ESTABLISHED` and is recorded separately — it does **not** classify the negative-existence safety repair as failed. Notably, the answer's positive native-path description was supported by cited evidence that the reconciled `g011.e1` selectors do not match, while the e1-pinned objects were again not selected.

## 4. Controls

All four fixed controls executed clean: `g010`, `g014`, `g022`, `g050` → **CONTROL_PASS ×4**; `CONTROL_REGRESSION_COUNT = 0`. No new inappropriate insufficient-evidence refusal, no hard-safety failure, no identifier hallucination, critical evidence roles satisfied (crit-ev 1.0 each).

## 5. Overall verdict

```text
OVERALL_T1_VERDICT = FAIL
```

Per the preregistered rule: `A_CASE_OUTCOME = FAIL` and `B1_G023_OUTCOME = FAIL`. B2 and `C_NEGATIVE_EXISTENCE_SAFETY` passed; all controls passed; no hard-safety/trustworthiness invariant failed anywhere in the fixed cohort. No same-task repair, no rerun of failed cases, no cohort or criterion edits.

## 6. Interpretation and limitations

- The negative-existence safety repair produced a positive single observation on its target case (no corpus-wide absence claim; both paths positively described) — but one exposed case is not general proof, and the retrieval role loss beneath it remains unresolved by design.
- The completeness-recovery repair was not directly observed in action: g013's revision ran, but the mechanism's exercise is unobservable from retained artifacts and the target obligation was still missed.
- The coverage false-acceptance class recurred on g023 despite the explicit per-point completeness contract — a single counter-observation that T1 was designed to be able to produce; the runtime semantic effect of the new contract remains not scientifically validated.
- These are bounded exposed-sentinel observations on eight cases; they neither prove nor disprove general repair effect, and they change no formal verdict.

## 7. State

- Protected: `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`; `holdout access = 0`; `protected-content leakage = 0`; `F6-B execution = 0`.
- Attempt 6: `candidate frozen = false`; `Attempt 6 preregistered = false`; `Attempt 6 executed = false`; `ATTEMPT_6_READINESS = NOT_READY`.
- Materiality: `MATERIAL_PRODUCT_CHANGE = false`; product-behavior lineage head unchanged (`e79d3232…`).
- Per the preregistered next-step mapping (T1 = FAIL): `NEXT_TASK_RECOMMENDATION = POST-A5 T1 FAILURE REVIEW / BOUNDED ROOT-CAUSE ANALYSIS`; `NEXT_TASK_EXECUTION_AUTHORIZED = false`.
