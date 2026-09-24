# G3 Novel-Dev QA Stage-Trace Observability Prerequisite

## Decision and starting state

**COMPLETE / DETERMINISTIC VERIFICATION PASS.** Starting HEAD:
`8b84d93484d390cd1cd06c90ea5d71926943724a`. The G3
[preflight](G3_TRACE_CAPABILITY_ARTIFACT_APPLICABILITY_PREFLIGHT.md) found that
the standard runner rejected explicit non-formal `novel_dev` QA stage tracing.
This task enables that existing observability path only. The G3 audit, cohort
selection, and empirical admission-gap classification remain unrun.

## Minimal implementation and boundary

`_configure_stage_trace()` in `src/panda_agent/evaluation_runner.py` now adds
`novel_dev` to the explicit development split allowlist. The existing guards
still require `capture_stage_trace=True`, `official=False`, no `candidate_id`,
and `mode` in `{qa, full}`. The existing programmatic
`run_evaluation(..., capture_stage_trace=True)` path persists the same
`capture_stage_trace` manifest field before runtime execution. No CLI flag,
manifest field, trace event, or trace schema was added.

| Trace request | Result |
|---|---|
| Non-formal, non-candidate `dev`, `challenge`, `regression`, or `novel_dev` QA | Allowed. |
| Non-formal, non-candidate `novel_dev` full | Allowed by the existing QA/full mode rule; no real full run was performed. |
| `novel_validation`, `novel_holdout`, or `acceptance` QA | Rejected. |
| Official/formal or candidate-bound `novel_dev` QA | Rejected. |
| Retrieval-only `novel_dev` trace request | Rejected. |

Trace-enabled `novel_dev` resume retains the saved choice; explicitly disabled
and legacy manifests cannot be retroactively enabled. The existing
`qa-stage-trace-v1` collector remains bounded and unchanged. This gate does
not alter question selection, retrieval, admission, A0/A1, V1/V2, G2 receipts,
composition, evaluation metrics, or judge routing.

## RED to GREEN and verification

Added synthetic tests to `tests/unit/test_post_a5_o1_observability.py` for the
allowed/rejected split matrix, manifest persistence before any runtime client,
resume forwarding, and disabled/legacy resume rejection. The first Python test
invocation lacked the local `PYTHONPATH` and failed at import; it was rerun with
the repository source/test paths before making the source change.

| Scope | Command (with `PYTHONPATH=src;tests/unit`) | Result |
|---|---|---|
| Pre-change focused RED | `python -m pytest 'tests/unit/test_post_a5_o1_observability.py::test_runner_allows_explicit_development_stage_trace[novel_dev-qa]' -q` | 1 failed: `_configure_stage_trace()` raised the expected split-guard `ValueError`. |
| Post-change focused GREEN | Same command | 1 passed. |
| Full O1 fake-only observability module | `python -m pytest tests/unit/test_post_a5_o1_observability.py -q` | 45 passed. Includes existing trace-on/off semantic-neutrality comparisons. |
| Neighboring synthetic store/resume tests | `python -m pytest 'tests/unit/test_post_a3_runner_lifecycle.py::PostA3RunnerLifecycleTests::test_store_reopen_stable_bytes_and_usage_after_successful_record' 'tests/unit/test_post_a3_runner_lifecycle.py::PostA3RunnerLifecycleTests::test_store_reopen_stable_bytes_and_usage_after_legacy_seed' -q` | 2 passed. |

No live evaluation, retrieval, QA, Vertex, judge, Gold, protected-split, old
T2, or full repository suite was run. Tests use synthetic/fake fixtures.
The changed source line is an allowlist gate only; `qa.py`, `retrieval.py`,
prompts, provider schemas, G1/G2 logic, and evaluator scoring are untouched.

## Identity, lifecycle, and accounting

The repository commit records the evaluation-runner capability change. The
product-behavior lineage remains G2
`a0106bd5eff93646f34f5e50e161e8be8a49d680`; mode
`production_answer_obligations_v1`, decomposition prompt/schema
`3.0.0` / `e1.question_decomposition.v3`, coverage schema
`coverage-satisfaction-v2`, prompt set `3.12.0`, prompt fingerprint
`5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce`,
Gold `m6-benchmark-v2.11`, and calibration
`phase_b_t3_product_language_scope_v8` are unchanged. The existing manifest
field and `qa-stage-trace-v1` schema are unchanged.

`PHASE_G = IN_PROGRESS / G3_OBSERVABILITY_PREREQUISITE_COMPLETE`.
`G3 = AUDIT DESIGN COMPLETE / TRACE-CAPABILITY PREFLIGHT COMPLETE /
OBSERVABILITY PREREQUISITE COMPLETE / SCOPED AUDIT READY /
PRODUCT CHANGE NOT_AUTHORIZED`.
`NEXT_TASK_RECOMMENDATION = G3 EVIDENCE ADMISSION / ANSWERABILITY GAP SCOPED AUDIT`.
`NEXT_TASK_EXECUTION_AUTHORIZED = false`.

```text
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
RETRIEVAL_RUNS = 0
QA_RUNS = 0
AUDIT_EXECUTED = false
AUDIT_CASES_COLLECTED = 0
NOVEL_DEV_CASE_CONTENT_ACCESS = 0
NOVEL_DEV_OUTCOME_ACCESS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```
