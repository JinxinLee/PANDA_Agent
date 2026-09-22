# Post-A5 C1 Vertex Structured-Schema Compatibility Repair

**COMPLETE / PASS / PROVIDER_SCHEMA_COMPATIBILITY_REPAIRED**

This bounded repair removed the remaining provider-side C1 array bounds that were accepted by the local contract but rejected by the configured Vertex structured-output path. The deterministic local validator and the C1 semantic contract were preserved. The exact committed production schema passed the final synthetic provider smoke, after which the authorized fixed eight-case replacement T2 was executed under the repaired identity.

## Identity and scope

- Actual repository HEAD at this task start: `1c1166e4e6e0cd15400271a49ae79ec10e772e3c`.
- Expected historical T2-P0 identity: `269914bd2a87ee5889832c445c8024f5bc2ef0db`.
- Previous product behavior head: `528499f3b42357f770c526f3e22d70f962d37b50`.
- Implementation commit: `58bd53a86627ff0e0b668915076d974272e86233`.
- Product behavior lineage during replacement T2: `58bd53a86627ff0e0b668915076d974272e86233`.
- Prompt version: `3.11.1` -> `3.11.2`.
- Prompt fingerprint: `9135b73c517f4cfac50695b2b47264749145923b60c2e2ee590149a141eca9bf` -> `878caffb022dd66111b3bc6e98c6e372340cb619db13aa856c09aaa09e8b8391`.
- `COVERAGE_SATISFACTION_SCHEMA_VERSION` remains `coverage-satisfaction-v1`.

The earlier invalid T2 execution remains historical evidence and was not rewritten. Its corrected accounting is eight attempted cases, zero scientifically valid cases, **56 calls / 288,539 tokens / 9 embedding calls / 0 judge calls**, and one transport recovery. In particular, `g047` ended in a retryable 400 structured-schema failure after 7 calls / 35,103 tokens and `g050` ended in a retryable 500 followed by a same-identity resume and final 400 after 9 calls / 63,209 tokens. The old run directories and the historical result artifact remain preserved.

## Isolation matrix and bounded repair

The diagnostic contract allowed at most four synthetic provider calls and excluded Gold, retrieval, evidence, judge, and T2 execution:

| Probe | Schema | Result | Usage |
|---|---|---|---:|
| S0 | Minimal object schema | PASS | 1 call / 172 tokens |
| S1 | `ANSWER_POINT_COVERAGE_REVIEW_SCHEMA` | PASS | 1 call / 960 tokens |
| S2 | Current production C1 schema with recursive `minItems`/`maxItems` removed in memory | PASS | 1 call / 1,792 tokens |
| S3 | Not run because S2 passed | NOT_RUN | 0 |

S0 and S1 establish that the provider path and the simpler coverage schema work. S2 passing after only the recursive `minItems`/`maxItems` removal supports those provider-side bounds as a sufficient compatibility trigger. The individual backend contribution of every schema feature is not uniquely isolated. The production repair therefore removed only those provider-facing array bounds; local validation still enforces the semantic and size contract.

The compatibility test was RED before the edit because `minItems`/`maxItems` were present and GREEN after the edit. Focused deterministic verification passed **179 tests**; the focused prompt-version subset passed **1 test / 209 deselected**. The extracted local validator was unchanged.

## Final provider smoke

One synthetic request used `VertexAIClient.generate_json()` with `VertexSettings.from_env().for_verification_model()`, model `gemini-3.8-flash`, location `global`, and the exact committed `PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA`. It did not use Gold questions, retrieval, PANDA evidence, T2 cases, or an external judge.

Result: **PASS**. The provider returned a parseable object containing the expected C1 review keys. Lower-level usage was **2 provider calls / 2,984 tokens / 0 embedding calls**; the call wrapper performed transparent transient recovery. This smoke was not repeated.

## Replacement T2 disposition

The smoke PASS triggered the fixed replacement T2 immediately. No tracked file changed between implementation commit `58bd53a...` and completion of the eight scientific calls. The fixed order was `g011,g010,g013,g014,g023,g022,g047,g050`; all eight run IDs are preserved under `data/evaluation/runs/post-a5-t2r-*`.

The replacement T2 is **COMPLETE / FAIL**. It is a valid repaired-identity execution with complete stage traces, and it establishes scientific failures rather than a provider-schema infrastructure invalidation:

- `g011`: **PASS** for answered + zero critical answer-point misses + negative-existence safety. The native-documentation evidence role was not covered (`critical_final_evidence_recall=0.5`); that role is reported separately and does not gate the negative-existence mechanism.
- `g010`: **CONTROL_PASS**.
- `g013`: **FAIL**. Final status `insufficient_evidence`, critical point `p3` missing, missing runtime point `point.3`. Trace is complete; the visible-only point was `C1_GAP_BLOCKED_VISIBLE_ONLY`, with `A1` and `V2` not executed.
- `g014`: **CONTROL_PASS**.
- `g023`: **FAIL**. Answered, but critical point `p3` is missing. The observed runtime trace was complete for its exposed point set; the required Gold `p3` was not present in the runtime trace, so causal recovery is `NOT_ESTABLISHED` and no C1 recovery is claimed.
- `g022`: **CONTROL_PASS**.
- `g047`: **FAIL**. Final status `insufficient_evidence`, critical point `p1` missing, and the required explicit elastic-differential-cross-section to luminosity-extraction relation was not fully established. One retryable 500 transport event was recovered under the same run identity; the final trace is complete.
- `g050`: **CONTROL_FAIL**. Final status `insufficient_evidence`, critical point `p1` missing, and coverage was not evaluable because the basis quote was not exact or exceeded the bound.

Replacement T2 usage was **63 model/provider calls / 345,411 tokens / 8 embedding calls / 10 judge calls**, with **one transport recovery event**. Per-case calls/tokens were `g011 8/34,719`, `g010 10/31,180`, `g013 7/43,807`, `g014 7/37,645`, `g023 7/42,103`, `g022 8/47,478`, `g047 9/40,965`, and `g050 7/67,514`.

The earlier T1 baseline remains historical **FAIL** (65 calls / 373,265 tokens). Replacement T2 is a post-F6-A compatibility-repair validation and does not reopen F6-A. **Replacement T2 remains exposed repair-target evidence, not independent generalization evidence.**

## Protected state and lifecycle

- Holdout access: `0`.
- Protected leakage: `0`.
- F6-B execution: `0`; F6-B remains locked.
- F6-A remains **CLOSED**; this replacement T2 is not a new F6-A attempt.
- Attempt 6: `DEFERRED / NOT_NEXT_STEP`.
- No T2-R1, T3, new candidate freeze, external judge redesign, or F6-B execution is authorized by this result.

Final status: **COMPLETE / FAIL** for the stated replacement-T2 validation scope. No further task execution is authorized in this task.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`

`STOP.`
