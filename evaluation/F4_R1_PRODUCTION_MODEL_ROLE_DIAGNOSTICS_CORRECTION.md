# F4-R1 — Production Model-Role Diagnostics Correction Closeout

Lifecycle identity: Phase F → F4 → F4-R1 — Production Model-Role Diagnostics Correction.

Decision: **COMPLETE / PASS / PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTED.**

Corrected parent: `F4 = COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED`
(final closure achieved only after F4-R1). All PANDA scientific/evaluation
calls and tokens are zero. Deterministic diagnostics correction only; mocks and
fakes only; no model comparison and no verifier-quality claim.

## 1. Starting state

- Starting HEAD: `a9f389704580a24ac5e88e8e6d4b937b484113e0`
  ("Separate QA generation and verification roles") — matched the expected
  baseline exactly; verified, not assumed.
- Worktree: clean before editing; no unrelated user work; no resets, amends,
  squashes, or force operations.
- Initial F4 terminal state treated as PARTIAL / CORRECTION_REQUIRED until R1
  closed; F5 remained NOT_READY / UNEXECUTED during the correction.

## 2. Production-shaped defect reproduction (before the fix)

Reproduced at starting HEAD with the real production construction path —
`VertexSettings(project="test", generation_model="model-A",
verification_model="model-B", evaluation_judge_model="model-C")`, the default
`QAAgent` construction (generation client receives the base settings, the
verification client receives `settings.for_verification_model()`), with only
`VertexSettings.from_env` / `VertexAIClient` / `Retriever` mocked:

```text
generation client actual model  = model-A   (settings.generation_model)
verification client actual model = model-B  (settings.generation_model)
distinct client paths           = True
PRE-FIX receipt = {
  "answer_generation_model": "model-B",
  "semantic_verification_model": "model-B",
  "same_model_id": True,
  "distinct_client_paths": True,
}
```

The receipt misidentified the generation role as model-B and claimed the roles
share one model ID — exactly the authorized defect.

## 3. Root cause

`_model_roles_diagnostics().role_model()` computed
`settings.verification_model or settings.generation_model` for BOTH role
clients. `verification_model` is a base-settings CONFIGURATION field meaning
"which model to use when deriving the verification client"; it is not "which
model this client actually sends `generate_json` calls to". The actual model of
any role client is `client.settings.generation_model` (that is the field
`VertexAIClient.generate_json` passes to Vertex). For the production A/B shape
the generation client carries the base settings (`generation_model=model-A`,
`verification_model=model-B`), so the old expression reported model-B for the
generation role and collapsed `same_model_id` to true.

## 4. Exact repair

Inside `QAAgent._model_roles_diagnostics()` only: `role_model()` now returns
`settings.generation_model` for each role client (with the settings-less →
`None` marker unchanged) and no longer consults `verification_model`. No
special-cased names, no new role field on clients, no role-routing change, no
abstraction added. After the fix the same reproduction reports:

```text
POST-FIX receipt = {
  "answer_generation_model": "model-A",
  "semantic_verification_model": "model-B",
  "same_model_id": False,
  "distinct_client_paths": True,
}
```

## 5. Why routing itself was already correct

The defect was reporting-only. Actual execution always used
`client.settings.generation_model`: `self.generation_vertex` (base settings →
model-A) for `_answer`/`_revise`, `self.verification_vertex`
(`for_verification_model()` settings → model-B) for the `_verify` semantic
review including coverage review and E3's re-entry. The production diff of R1
touches only the diagnostic helper; routing, client construction, usage
accounting (`_role_clients`, identity dedup, aggregate snapshot summing,
`usage_stage` labels and counters), and failure semantics have zero diff.

## 6–9. Model-role matrix (all verified)

| Configuration | Actual role models | Diagnostic receipt |
| ------------- | ------------------ | ------------------ |
| Production A / no verification override (T2) | A / A | `answer_generation_model=A, semantic_verification_model=A, same_model_id=true, distinct_client_paths=true` (valid deployment) |
| Production A / B override, judge C (T1, central regression) | A / B | `A / B, same_model_id=false, distinct_client_paths=true` |
| Explicit two-client injection G / V (T3) | G / V | reports each client's actual `settings.generation_model`; fakes are NOT required to expose `verification_model` |
| Settings-less injected fakes (T4) | unknown | `None / None, same_model_id=None`, `distinct_client_paths` by object identity; no invented IDs |

## 10–12. Preservation

- Role usage counters (`qa_generation_calls`, `qa_generation_token_usage`,
  `qa_semantic_verification_calls`, `qa_semantic_verification_token_usage`),
  aggregate accounting, shared-client dedup, and `generate_json(usage_stage=...)`
  are unchanged (T11/T12; existing usage tests pass unmodified).
- Deterministic authority (invalid evidence / wrong version / incomplete
  locator cannot be waived by `supported=true`) and semantic unsupported
  authority are unchanged (T13/T14; existing authority tests pass unmodified).
- Evaluation-judge isolation unchanged: the receipt still covers only the two
  product QA roles; no judge metadata was added to normal QA (T10).
- Vertex settings semantics unchanged: `QA_GENERATION_MODEL_ID`,
  `QA_VERIFICATION_MODEL_ID` (optional, defaulting to generation),
  `QA_EVALUATION_JUDGE_MODEL_ID`, `effective_verification_model`, and
  `for_verification_model()` keep their F4 behavior (vertex.py zero diff).

## 13. Public schema / default preservation

`model_roles` remains internal diagnostics. No role model IDs were added to
public claims, answer, evidence, QAResult schema, or refusal text; no public
API change; normal default `legacy_question_core` unchanged (T15/T16).

## 14. Focused test results

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **136 passed +
  19 subtests** (135 pre-existing unmodified + 1 new central regression
  `test_production_ab_config_diagnostics_report_actual_role_models`, which
  asserts the exact corrected receipt for the production-shaped A/B/C base
  settings and that both role clients were built with their actual models
  A and B).
- `tests/unit/test_vertex.py` was NOT rerun because `vertex.py` has zero diff
  (§25 conditional).
- T1–T18 mapping: T1 = the new central regression; T2/T3/T4 = existing
  diagnostics tests (`test_production_default_builds_distinct_role_client_paths`,
  `test_aggregate_usage_sums_unique_role_clients`, 
  `test_model_roles_diagnostics_markers`); T5–T18 = existing F4 routing,
  failure-authority, usage-aggregation, judge-isolation, public-schema, default,
  F2, and F3-retirement sentinels, all passing unmodified.
- Static: `git diff --check` clean; `git status --short` shows exactly the two
  authorized files (`src/panda_agent/qa.py`, `tests/unit/test_qa.py`). No
  SHA256/hash bookkeeping generated.

## 15. Scientific / evaluation accounting

PANDA scientific/evaluation calls: **0**. PANDA scientific/evaluation tokens:
**0**. No model comparison, live Vertex QA evaluation, T2/T3/T4/T5 scientific
evaluation, LLM judge, protected holdout, promotion, or release evaluation.

## 16–18. Historical correction and lifecycle result

- Initial F4 commit `a9f3897` is preserved unamended; the original F4 report
  `evaluation/F4_GENERATION_VERIFICATION_ROLE_SEPARATION.md` carries a
  CORRECTION / SUPERSESSION NOTICE at the top (history body untouched).
- F4-R1 = COMPLETE / PASS / PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTED.
- F4 = COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED
  (final closure achieved only after F4-R1).
- Phase F = IN_PROGRESS / F4_COMPLETE_F5_NOT_STARTED. F5/F6 remain; Phase F is
  not marked complete.

## 19–21. Next recommendation and authorization

F5 — Bounded Answer Composer. Recommendation only; not started.

NEXT_TASK_EXECUTION_AUTHORIZED = false
