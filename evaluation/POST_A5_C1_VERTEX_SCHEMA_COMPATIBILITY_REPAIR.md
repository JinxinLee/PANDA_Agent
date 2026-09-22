# Post-A5 C1 Vertex Structured-Schema Compatibility Repair

**HOLD / PRIMARY_KEYWORD_FIX_INSUFFICIENT**

This bounded repair removed the known unsupported provider-side schema keywords from the production C1 response schema and preserved the deterministic local validator. The focused deterministic suite passed, but one direct real-provider compatibility smoke still returned `400 INVALID_ARGUMENT`. Per the authorized stop rule, no further schema redesign, T2 execution, or T2 identity refresh was performed.

## Identity and scope

- Actual repository HEAD at task start: `1522d3993ba3787725f7867ad7bc8244540f01ef`.
- Expected historical T2-P0 identity: `269914bd2a87ee5889832c445c8024f5bc2ef0db`.
- Previous product behavior head: `6ed3ba361476b36744c72e76f5905733b1755f5c`.
- Implementation commit: `528499f3b42357f770c526f3e22d70f962d37b50`.
- New product behavior head: `528499f3b42357f770c526f3e22d70f962d37b50`.
- Prompt version: `3.11.0` -> `3.11.1`.
- Prompt fingerprint: `03e1bf270898b28127a42fa2e1ccb24cfc1d87e177eeba5428ba4680d426352c` -> `9135b73c517f4cfac50695b2b47264749145923b60c2e2ee590149a141eca9bf`.
- `COVERAGE_SATISFACTION_SCHEMA_VERSION` remains `coverage-satisfaction-v1`.

The task-bound pre-repair attempt consisted of the fixed cases `g011,g010,g013,g014,g023,g022`. All six were provider-invalid infrastructure executions, not answer-quality failures:

`T2_PRE_REPAIR_EXECUTION_ATTEMPT = ABORTED / INFRASTRUCTURE_INVALID / PROVIDER_STRUCTURED_SCHEMA_INVALID_ARGUMENT`

Scientifically valid completed cases: **0**. Scientific PASS cases: **0**. Scientific FAIL cases: **0**. Usage retained: **40 calls / 190,227 tokens**. `g047/g050 = NOT_EXECUTED_AFTER_SYSTEMIC_PROVIDER_FAILURE` for this classified attempt. The existing failed run directories were preserved; no T2 run was deleted, cleaned, resumed, or overwritten by this task.

## Static confirmation and bounded repair

The inspected call path passes `response_mime_type="application/json"` and `response_json_schema=response_schema` through `VertexAIClient.generate_json()`. The C1 production schema was bound into `prompt_fingerprint()`. `_validate_coverage_satisfaction()` independently retained the non-empty and length bounds for relationship text, necessity reasons, and quotes; duplicate supporter and basis-ID checks; relationship and supporter bounds; admission-state checks; and support/basis relationship checks.

The provider-facing C1 schema removed only `uniqueItems`, `minLength`, and `maxLength`. Supported structural bounds and the local semantic contract remain in place. The schema compatibility test was **RED** before the edit because all three keywords were observed, and **GREEN** after the edit.

## Deterministic verification

- `tests/unit/test_post_a5_c1_coverage_completeness.py`
- `tests/unit/test_post_a5_o1_ea1_c1_integration.py`
- `tests/unit/test_post_a5_o1_observability.py`
- `tests/unit/test_post_a5_ea1_exact_backing.py`

Result: **179 passed**. The focused prompt-version assertion in `tests/unit/test_qa.py` also passed: **1 passed, 209 deselected**. No historical `v2_6` stale assertion was changed.

## Real-provider compatibility smoke

One synthetic request used `VertexAIClient.generate_json()` with `VertexSettings.from_env().for_verification_model()`, the configured semantic-verification model `gemini-3.8-flash` in `global`, and the exact repaired `PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA`. It did not use Gold questions, retrieval, PANDA evidence, T2 cases, or an external judge.

The provider returned:

`VertexCallError: structured generation failed for gemini-3.8-flash in global: 400 INVALID_ARGUMENT. Request contains an invalid argument.`

Smoke result: **HOLD / PRIMARY_KEYWORD_FIX_INSUFFICIENT**. Direct-provider usage: **1 call / 0 reported tokens**; the 400 response supplied no usage metadata. A local import-path setup attempt failed before any provider request and is not counted. The smoke was not repeated.

## T2 and protected-state disposition

No T2 case was executed after the repair. The existing T2 preregistration was not refreshed because the smoke failed. No repaired-identity run IDs were created. The old six invalid executions remain non-scientific evidence and are not reused, resumed, or scored under the repaired identity.

Protected content was not accessed: holdout access `0`, protected leakage `0`, and F6-B execution `0`. `ATTEMPT_6 = DEFERRED / NOT_NEXT_STEP`.

Next single task: review the remaining provider-facing C1 schema incompatibility using the exact smoke error; do not execute T2 until a separately authorized compatibility repair and smoke PASS.
