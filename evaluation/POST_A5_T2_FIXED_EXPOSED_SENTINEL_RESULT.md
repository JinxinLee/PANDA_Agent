# Post-A5 T2 Fixed Exposed Sentinel Result

**COMPLETE / INCONCLUSIVE / VALIDATION_INCONCLUSIVE**

T2 executed from the exact preregistration HEAD `269914bd2a87ee5889832c445c8024f5bc2ef0db`, with the frozen eight-case cohort and order. No case produced a valid final answer or external evaluator result. This is an infrastructure execution failure, not a scientific FAIL and not evidence of product effectiveness or ineffectiveness.

## Execution identity and protocol

- T2-P0 / execution HEAD: `269914bd2a87ee5889832c445c8024f5bc2ef0db`.
- Product behavior head: `6ed3ba361476b36744c72e76f5905733b1755f5c`.
- Prompt: `3.11.0` / `03e1bf270898b28127a42fa2e1ccb24cfc1d87e177eeba5428ba4680d426352c`.
- Gold: `m6-benchmark-v2.11`, SHA256 `39943c6a3f2152e476109c0340acd066795c8de6ff3b6bb2eac6661ac480a417`.
- Calibration: `phase_b_t3_product_language_scope_v8`, selector SHA256 `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5`.
- Mode: `full`; split: `dev`; `allow_draft=true` only selected `official=false` for O1 tracing; `capture_stage_trace=true`; numerical quotas were unset as preregistered; existing external judge remained enabled.

Fixed order and run IDs:

`g011` (`post-a5-t2-g011`) → `g010` (`post-a5-t2-g010`) → `g013` (`post-a5-t2-g013`) → `g014` (`post-a5-t2-g014`) → `g023` (`post-a5-t2-g023`) → `g022` (`post-a5-t2-g022`) → `g047` (`post-a5-t2-g047`) → `g050` (`post-a5-t2-g050`).

All eight remained approved, `dev`, exposed, expected `answered` Gold objects. No substitutions, additions or replicate block occurred.

## Case outcomes

| Case | Execution | Result status | Critical misses | Revision | Calls | Tokens | Scientific verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| g011 | terminal `400 INVALID_ARGUMENT` | unavailable | n/a | n/a | 5 | 28,759 | not evaluable |
| g010 | terminal `400 INVALID_ARGUMENT` | unavailable | n/a | n/a | 5 | 22,516 | not evaluable |
| g013 | terminal `400 INVALID_ARGUMENT` | unavailable | n/a | n/a | 10 | 38,202 | not evaluable |
| g014 | terminal `400 INVALID_ARGUMENT` | unavailable | n/a | n/a | 7 | 30,136 | not evaluable |
| g023 | terminal `400 INVALID_ARGUMENT` | unavailable | n/a | n/a | 7 | 32,412 | not evaluable |
| g022 | terminal `400 INVALID_ARGUMENT` | unavailable | n/a | n/a | 6 | 38,202 | not evaluable |
| g047 | terminal `400 INVALID_ARGUMENT` | unavailable | n/a | n/a | 7 | 35,103 | not evaluable |
| g050 | first `500 INTERNAL`, same-identity resume then terminal `400 INVALID_ARGUMENT` | unavailable | n/a | n/a | 9 | 63,209 | not evaluable |

Totals: **56 model/provider calls, 288,539 tokens, 9 embedding calls, 0 judge calls, 1 transport recovery event**. The provider-level `400 INVALID_ARGUMENT` failures occurred before valid final answers and judge results. No `result.status`, missing-point count, revision count, hard-safety result or mechanism trace classification exists for any case.

The g011 negative-existence criterion and native-documentation role coverage are not evaluable. g013 and g023 mechanism labels are `NOT_OBSERVABLE`; `T2_MECHANISM_OBSERVABILITY = FAILED / REQUIRED_TARGET_TRACE_UNAVAILABLE`.

## Verdict and paired interpretation

`T2_SCIENTIFIC_OUTCOME = INCONCLUSIVE / EXECUTION_INCOMPLETE` because no valid scientific case result was formed and no valid scientific FAIL was established. `OVERALL_T2_VERDICT = INCONCLUSIVE / VALIDATION_INCONCLUSIVE`. The result is not converted to FAIL merely because the provider failed, and it is not converted to PASS by the absence of measured misses.

T1 remains the frozen historical baseline: `COMPLETE / FAIL`, 65 calls / 373,265 tokens; g013 and g023 failed their exposed p3 targets, g047 passed, g011 negative-existence safety passed, and all four controls were `CONTROL_PASS`. T2 supplies no valid paired transition and no statistical or generalization evidence.

T2 is exposed repair-target evidence, not independent generalization evidence.

## Lifecycle closeout

`POST_A5_REPAIR_VALIDATION = CLOSED / VALIDATION_INCONCLUSIVE`.

`F6_A_REPAIR_LOOP = CLOSED` regardless of this terminal infrastructure outcome. No automatic T2-R1, RCA, T3, repair cycle, integration closeout, Attempt 6 or F6-B follows. A future generic product improvement requires separate normal development authorization.

Protected data were not accessed: `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`, holdout access = 0, protected-content leakage = 0, F6-B execution = 0. Candidate frozen = false; Attempt 6 preregistered/executed = false; `ATTEMPT_6_READINESS = NOT_READY`; `F6_B = NOT_ENTERED / NOT_NEXT_STEP`.

The machine-readable record is `evaluation/post_a5_t2_fixed_exposed_sentinel_result.json`. Run directories remain operational evidence under `data/evaluation/runs/`; no source, prompt, Gold, calibration, evaluator or threshold file was changed.
