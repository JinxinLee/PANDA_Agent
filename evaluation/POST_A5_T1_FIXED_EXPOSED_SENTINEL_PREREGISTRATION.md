# Post-A5 T1 — Fixed Exposed Sentinel Preregistration

Status: `PREREGISTERED / ZERO SCIENTIFIC CALLS / T1-P1 NOT STARTED`

Machine-readable authority: `evaluation/post_a5_t1_fixed_exposed_sentinel_preregistration.json`. This preregistration fixes the cohort, execution order, acceptance criteria, failure criteria, control-selection rule, and execution limit **before** any T1 scientific call. T1-P1 starts only after the preregistration commit.

T1 is development evidence, **not** formal release authority. It is not Attempt 6, not a candidate freeze, and not a formal release freeze.

## Frozen identity

- Repository HEAD before preregistration: `60a62fc9d954bfaaf48e3d5dae48d914c4b0ff21`.
- Product-behavior head: `e79d3232ed132a224cbceaf3524e19a1406bd648` (`Repair completeness recovery and negative-existence safety`); no post-repair product source changes (`git diff e79d323..HEAD -- src/panda_agent` empty).
- Prompt fingerprint: `0a5b2909ef586671d533148979fc681c64e37528ad53781a4566cb9044835ba2`.
- Gold: `m6-benchmark-v2.11`, SHA `39943c6a3f2152e476109c0340acd066795c8de6ff3b6bb2eac6661ac480a417`.
- Calibration: `phase_b_t3_product_language_scope_v8`; formal-English 59 / non-English 21; selector SHA `e27ef67a…`.
- Normal product mode: `production_answer_obligations_v1`.

## Fixed cohort and execution order

Affected sentinels (mandatory, immutable): `g011`, `g013`, `g023`, `g047`.

Deterministically matched controls (selected before any T1 scientific call from frozen Attempt-5 artifacts and the reconciled v2.11 contract; eligibility rule and tie-breaks recorded in the JSON):

| Affected | Intent | Control | Runner-up |
| --- | --- | --- | --- |
| g011 | installation | **g010** | g009 |
| g013 | usage | **g014** | g015 |
| g023 | usage | **g022** | g024 |
| g047 | algorithm_theory | **g050** | g051 |

Eligible pool: 38 formal-English cases. All four controls matched on the same intent without dropping any eligibility criterion. Controls are immutable after the preregistration commit.

Fixed execution order (interleaved, immutable once execution starts):

```text
g011 → g010 → g013 → g014 → g023 → g022 → g047 → g050
```

Execution mechanism: the existing `panda-qa-eval` infrastructure, mode `full`, split `dev`, official, one single-case `--case-id` invocation per fixed case in the order above (existing ID-list mechanism; no runner or evaluator modification), run ids `post-a5-t1-<case_id>`. Logical execution count: exactly **8**. Scientific reruns, stochastic replicates, and cohort edits are forbidden.

## Acceptance criteria (frozen before execution)

- **Sentinel A — g013 (completeness recovery):** `A_CASE_OUTCOME = PASS` only if all critical answer points are satisfied under the active v2.11 Gold and current evaluator contract — in particular the historically missed master-run-task/lifecycle obligation — with no hard-safety violation. If a bounded revision is naturally triggered, record whether the repaired recovery path (new-content survival across claim-ID collision) was exercised: `A_REVISION_MECHANISM_ACTIVATION = OBSERVED / NOT_OBSERVED / NOT_OBSERVABLE`. A complete answer without natural revision is `PASS` with `NOT_OBSERVED` and must never be reported as `REVISION_RECOVERY_RUNTIME_EFFECT_PROVEN`. If the lifecycle obligation is missed again: `FAIL`. No second scientific rerun.
- **Sentinel B1 — g023 (workflow completeness):** `PASS` only if all critical answer points are covered — especially p3 (before PID in the generic workflow) — with the workflow relation explicitly established, not merely relevant components mentioned. No hard-safety violation. Otherwise `FAIL`.
- **Sentinel B2 — g047 (relationship completeness):** `PASS` only if the critical point (relate the elastic differential cross section to luminosity extraction) is covered with no hard-safety violation; discussing the model without the luminosity-extraction relationship is insufficient. Otherwise `FAIL`.
- **Sentinel C — g011 (negative-existence safety), predeclared rule:** the final rendered answer must not contain an unqualified corpus/documentation-wide negative-existence assertion about the native installation/setup path (e.g. the historical false claim that the locked documentation has no independent native setup path) unless that absence is established by deterministic exact-lookup machinery referenced in the answer. A safe answer either positively describes both paths when supported or states scoped uncertainty limited to the supplied/selected evidence. Detection: deterministic inspection of the final rendered answer text plus stored verifier/claim-support evidence; **no new LLM judge**. `C_NEGATIVE_EXISTENCE_SAFETY = FAIL` if such an assertion survives.
- **C retrieval-completeness observation:** failure to retrieve sufficient native-installation evidence is recorded separately as `C_RETRIEVAL_COMPLETENESS = PASS/FAIL/NOT_APPLICABLE` and never misclassified as a negative-existence repair failure; Workstream D remains `DEFERRED`.
- **Control regression rule:** a control is `CONTROL_PASS` only with zero critical answer-point misses, no contradiction, no major unsupported claim, no forbidden evidence, no wrong-version evidence, no unhandled exception, and no new inappropriate insufficient-evidence refusal. Citation-source variation alone is not regression when an accepted v2.11 `any_of` role is satisfied.

## Verdict rule and limits

- `PASS`: all four sentinel criteria PASS, all four controls CONTROL_PASS, all 8 fixed executions completed scientifically, no hard-safety/trustworthiness invariant failure. `C_RETRIEVAL_COMPLETENESS = FAIL` does not fail T1 (Workstream D deliberately unresolved); `A_REVISION_MECHANISM_ACTIVATION = NOT_OBSERVED` does not fail T1 if g013 is complete without revision.
- `FAIL`: any scientifically valid fixed result shows a sentinel FAIL, a control FAIL, or a hard-safety/trustworthiness failure. No same-task repair, no rerun of failed cases.
- `INCONCLUSIVE`: only for infrastructure/observability reasons (including unrecoverable transport failure under the established recovery policy). An undesirable valid result is FAIL, not INCONCLUSIVE.

Transport/infrastructure recovery: only the repository's established bounded policy (same case, same product/prompt/Gold/calibration identity, fully recorded).

## Prohibited

novel_validation, protected holdout, PANDA_Agent_Holdout, F6-B, Attempt 6 (freeze/preregistration/execution), the 59-case formal cohort, T2, any product/prompt/evaluator/Gold/calibration/threshold modification after the first scientific output.

At preregistration time: `PANDA scientific/evaluation calls = 0`, `tokens = 0`; `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`; `ATTEMPT_6_READINESS = NOT_READY`.
