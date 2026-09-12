# F4 — Generation / Semantic-Verification Role Separation Closeout

> **CORRECTION / SUPERSESSION NOTICE (F4-R1).** The initial F4 routing
> architecture reported here was valid: distinct generation/verification client
> paths, independently configurable verification model, `_answer`/`_revise` →
> generation role, `_verify` → semantic-verification role, evaluation-judge
> isolation, role-specific usage accounting, and fail-closed cross-role behavior
> all stand. The terminal PASS was premature: the internal `model_roles`
> diagnostic receipt could misidentify the generation model when
> `QA_GENERATION_MODEL_ID != QA_VERIFICATION_MODEL_ID` (reporting B/B and
> `same_model_id=true` for an A/B configuration). F4-R1
> (`evaluation/F4_R1_PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTION.md`, commit
> "Repair F4 model role diagnostics") is the authoritative final correction:
> the receipt now reports each role client's actual model
> (`settings.generation_model`). Final F4 closure is achieved only after F4-R1.
> The historical body below is preserved unmodified.

Lifecycle identity: Phase F → F4 — Separate Answer-Generation and Semantic-Verification Roles.

Decision: **COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED.**

F4 validates architecture and deterministic routing only. No verifier-quality
claim is made: no model comparison, no scientific validation, and no promotion
evaluation were run. All PANDA scientific/evaluation calls and tokens are zero.

## 1. Starting state

- Starting HEAD: `ba521bbcf891769ee90ce1b2816a7f51e8ced420`
  ("Retire fixed locator fallbacks") — matched the expected baseline exactly;
  verified, not assumed.
- Worktree: clean before editing; no unrelated user work present; no resets,
  amends, squashes, or force operations.

## 2. Pre-F4 coupling reproduction (call-site matrix, §60)

| Model call site | Pre-F4 client | Pre-F4 prompt / model path | F4 role |
| --------------- | ------------- | -------------------------- | ------- |
| Query analysis (`Retriever.analyze`, retrieval.py) | the single `self.vertex` client passed in by `QAAgent` | `QUERY_ANALYZER_SYSTEM_PROMPT`, `settings.generation_model` | unchanged: existing retrieval/primary path (= generation-side client) |
| Embeddings / reranking (retrieval.py) | same injected client | — | unchanged: existing retrieval/embedding path |
| Question decomposition (`QAAgent.decompose_question` → `QuestionDecomposer(self.vertex)`) | `self.vertex` | — | unchanged: existing primary/decomposition path (now explicitly `self.generation_vertex`, same object) |
| `_answer` (qa.py ~1937) | `self.vertex.generate_json(...)` | `ANSWER_SYSTEM_PROMPT` | answer generation |
| `_verify` semantic review (qa.py ~2170, SINGLE call site shared by legacy review and coverage review) | `self.vertex.generate_json(...)` | `EVIDENCE_REVIEW_SYSTEM_PROMPT` / `ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT` | semantic verification |
| `_revise` (qa.py ~2434) | `self.vertex.generate_json(...)` | `REVISION_SYSTEM_PROMPT` / `ANSWER_POINT_COVERAGE_REVISION_SYSTEM_PROMPT` | answer generation (revision produces replacement claims; its input contains verifier errors but it is NOT verification) |
| Evaluation judge | not referenced anywhere in `qa.py` (only evaluation infrastructure + `VertexSettings` field) | `EVALUATION_JUDGE_SYSTEM_PROMPT` | unchanged: offline evaluation only |

Prompt separation already existed; role/client separation did not — that was
the F4 defect.

## 3. Role matrix after (§48)

| Operation | Role after F4 |
| --------- | ------------- |
| retrieval query analysis | existing retrieval/primary path (generation-side client, unlabeled) |
| embeddings | existing retrieval/embedding path (unlabeled) |
| reranking | existing retrieval/primary path (unlabeled) |
| question decomposition | existing primary/decomposition path (`self.generation_vertex`, unlabeled) |
| `_answer` | answer generation (`self.generation_vertex`, `usage_stage="qa_generation"`) |
| `_revise` | answer generation (`self.generation_vertex`, `usage_stage="qa_generation"`) |
| `_verify` semantic review | semantic verification (`self.verification_vertex`, `usage_stage="qa_semantic_verification"`) |
| coverage semantic review | semantic verification (same call site, shadow branch) |
| E3 second verify | semantic verification (re-enters `_verify`) |
| evaluation judge | offline evaluation only — never normal QA |

## 4. Settings / configuration change

`VertexSettings` (frozen dataclass) gained, as the LAST field (positional
construction compatibility preserved): `verification_model: str | None = None`.
`from_env()` reads the OPTIONAL `QA_VERIFICATION_MODEL_ID` (absent → `None`; no
new required variable, no new error path). New property
`effective_verification_model` returns `verification_model or
generation_model`. New helper `for_verification_model()` returns
`replace(self, generation_model=self.effective_verification_model)` — the
same-roles-may-share-a-model contract; idempotent; `verification_model` and
`evaluation_judge_model` fields ride along unchanged. `.env.example` documents
`QA_VERIFICATION_MODEL_ID=` with the three-role distinction. The three roles
remain conceptually distinct: `QA_GENERATION_MODEL_ID` (answer/revision),
`QA_VERIFICATION_MODEL_ID` (product semantic verifier; defaults to generation),
`QA_EVALUATION_JUDGE_MODEL_ID` (offline evaluation only).

## 5. Evaluation-judge boundary

`evaluation_judge_model` / `QA_EVALUATION_JUDGE_MODEL_ID` /
`EVALUATION_JUDGE_SYSTEM_PROMPT` remain unwired into product QA: `qa.py`
contains no reference to them (static sentinel T24), the judge field is not
repurposed as the verifier (`for_verification_model()` never reads it), and
`from_env()` still requires the judge variable only as before. Verifier and
evaluator were NOT collapsed.

## 6. Production client construction

With no injected client, `QAAgent.__init__` calls `VertexSettings.from_env()`
once and builds TWO distinct `VertexAIClient` objects:
`self.generation_vertex = VertexAIClient(settings)` and
`self.verification_vertex = VertexAIClient(settings.for_verification_model())`
— distinct client paths even when both effective model IDs are equal (§23
sentinel: same_model_id=true AND distinct_client_paths=true simultaneously).
`self.vertex = self.generation_vertex` remains as a legacy alias, and the
retriever receives the generation client exactly as before.

## 7. Injection / backward-compatibility contract (§21/§22)

- Production (no injection) → distinct generation/verification client paths.
- `verification_vertex=` → explicit role-specific injection (T6).
- Sole legacy `vertex=` injection with no verifier → that client serves both
  roles (`self.verification_vertex is self.vertex`), keeping every existing
  `vertex=FakeVertex()` test working without mass rewrites (T5). This seam is
  explicit, commented in the constructor, and is NOT the production-default
  architecture.

## 8–12. Routing audit

- `_answer` → `self.generation_vertex.generate_json(..., usage_stage="qa_generation")`
  (T7: generation fake +1, verification fake +0).
- `_revise` → `self.generation_vertex.generate_json(..., usage_stage="qa_generation")`
  (T8). Revision is generation even though its input contains verifier errors.
- `_verify` semantic review (the single call site covering legacy review,
  coverage review, and E3's re-entry) →
  `self.verification_vertex.generate_json(..., usage_stage="qa_semantic_verification")`
  (T9; coverage branch T10 asserts `ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT`
  goes through the verification fake; T11 asserts the initial and post-E3
  reviews both hit the verification fake).
- No other model-call ownership changed: query analysis, embeddings, reranking,
  and decomposition keep their existing path; routing is proven by client
  identity and explicit `usage_stage` accounting, not by prompt text (T23's
  static check: exactly three `usage_stage=` occurrences in qa.py).

## 13–14. Deterministic / semantic authority preservation

- Deterministic integrity checks in `_verify` (claim IDs, evidence-ID validity,
  code-version equality, code/paper/Sphinx locator completeness, identifier
  grounding, answer-point mapping structure) are unchanged and remain
  application authority: T12 (invalid evidence ID), T13 (wrong code version),
  and T14 (incomplete locator) all prove that a `supported=true` semantic
  verdict CANNOT waive the deterministic error.
- F2-A1/F2-A1-R1 is preserved: a deterministic-clean claim the semantic
  verifier marks unsupported stays rejected (T15), and a deterministic-clean
  supported claim still succeeds (T16). No lexical whole-claim bypass was
  restored. No new numeric policy was introduced (existing deterministic
  numeric/version guards untouched).

## 15–16. Usage accounting

- Adapter: `generate_json(..., usage_stage=...)` additively records
  `qa_generation_calls` / `qa_semantic_verification_calls` and, when response
  usage metadata carries `total_token_count`, `qa_generation_token_usage` /
  `qa_semantic_verification_token_usage` — alongside the unchanged aggregate
  `model_calls` / `generation_calls` / `embedding_calls` / `token_usage`.
  Unlabeled calls (all pre-existing call sites, embeddings, health checks)
  produce exactly the prior observable aggregate behavior, and the existing
  `stats_delta` exact-key test passes unmodified (T21/T22 + adapter compat
  tests). Tokens are taken from response metadata only; no local estimation.
- QA aggregation: `_role_clients()` deduplicates the role clients by object
  identity; `_stats_snapshot()` sums per-client snapshots;
  `_model_usage_delta()` reports the snapshot difference, which equals the sum
  of unique per-client deltas — never double-counting a shared injected client
  (T19: two clients → `model_calls` 3 = 2+1 with role keys; T20: one shared
  client → counted once). Fakes without stats keep the four aggregate keys at
  0, exactly as before. Retrieval/analyzer calls are not labeled as QA
  generation (T23).
- `run_detailed()` output shape is unchanged (`model_usage` remains a JSON
  dict); service.py needed no change because `_model_usage` merges the extra
  role keys into the existing JSONB usage field.
- Role diagnostics: `diagnostics["model_roles"]` reports
  `answer_generation_model`, `semantic_verification_model`, `same_model_id`
  (None when settings-less fakes), and `distinct_client_paths`. Internal only —
  no project IDs, credentials, prompts, or responses; role labels never appear
  in claims/answer/evidence/refusal text (T25).

## 17. Failure semantics

Fail-closed with no cross-role fallback: a verification-role failure
propagates and never falls back to the generator or treats claims as supported
(T17); a generation-role failure propagates and never invokes the verifier as
generator (T18). No role-level retries, alternate-model retries, or retry
orchestration were added; the adapter's existing transient retry is untouched.

## 18. Adversarial contract results (T1–T30)

New tests: 7 in `tests/unit/test_vertex.py` (`VertexTests` additions) and 24 in
`tests/unit/test_qa.py` (`TestGenerationVerificationRoleSeparation`).

| Test | Contract | Result |
| ---- | -------- | ------ |
| T1 | `QA_VERIFICATION_MODEL_ID` absent → effective verifier model = generation model | PASS (`test_verification_model_defaults_to_generation_model`) |
| T2 | explicit A/B override preserved in settings; `for_verification_model()` correct and idempotent | PASS (`test_explicit_verification_model_override`) |
| T3 | generation A / verification B / judge C all distinct, judge not repurposed | PASS (`test_three_model_roles_remain_distinct`) |
| T4 | production default builds distinct role client paths with equal model IDs (§23 sentinel: same_model_id=true, distinct_client_paths=true) | PASS (`test_production_default_builds_distinct_role_client_paths`) |
| T5 | legacy `vertex=`-only injection serves both roles; no mass test rewrites | PASS (`test_legacy_vertex_injection_serves_both_roles` + all pre-existing tests unmodified) |
| T6 | explicit two-client injection accepted per role | PASS (`test_explicit_two_client_injection`) |
| T7 | `_answer` → generation role only | PASS (`test_answer_routes_to_generation_role_only`) |
| T8 | `_revise` → generation role only | PASS (`test_revision_routes_to_generation_role_only`) |
| T9 | `_verify` semantic review → verification role | PASS (`test_verify_routes_to_verification_role`) |
| T10 | coverage review (shadow_e1_v2) → verification role with coverage prompt | PASS (`test_coverage_review_routes_to_verification_role`) |
| T11 | post-E3 second verify → verification role (initial + post-revision both) | PASS (`test_post_e3_review_uses_verification_role`) |
| T12 | deterministic invalid-evidence error cannot be waived by `supported=true` | PASS (`test_deterministic_invalid_evidence_cannot_be_waived`) |
| T13 | deterministic wrong-version error cannot be waived | PASS (`test_deterministic_wrong_version_cannot_be_waived`) |
| T14 | deterministic incomplete-locator error cannot be waived | PASS (`test_deterministic_incomplete_locator_cannot_be_waived`) |
| T15 | semantically unsupported claim still rejected (deterministic-clean) | PASS (`test_semantically_unsupported_claim_still_rejected`) |
| T16 | semantically supported claim still succeeds (deterministic-clean) | PASS (`test_semantically_supported_claim_succeeds`) |
| T17 | verification failure does not fall back to generator | PASS (`test_verification_failure_does_not_fall_back_to_generator`) |
| T18 | generation failure does not invoke verifier as generator | PASS (`test_generation_failure_does_not_invoke_verifier`) |
| T19 | aggregate usage sums both unique role clients (3 = 2+1; role keys present) | PASS (`test_aggregate_usage_sums_unique_role_clients`) |
| T20 | shared injected client counted exactly once | PASS (`test_shared_injected_client_counted_once`) |
| T21 | role call counters separate QA generation vs semantic verification | PASS (adapter `test_usage_stage_records_role_call_counters` + QA `test_role_call_counters_separate_qa_roles`) |
| T22 | role token counters follow actual response metadata | PASS (`test_usage_stage_attributes_tokens_to_role`) |
| T23 | retrieval/analyzer calls not mislabeled as QA generation | PASS (`test_retrieval_calls_not_labeled_qa_generation` + adapter unlabeled-compat tests) |
| T24 | evaluation judge never used by normal QA | PASS (`test_evaluation_judge_never_used_by_normal_qa`) |
| T25 | public QA result schema unchanged; no role strings in public content | PASS (`test_public_qa_result_schema_unchanged`) |
| T26 | `legacy_question_core` default unchanged | PASS (`test_default_mode_unchanged`) |
| T27 | F2-A1 semantic-support contract unchanged | PASS (pre-existing verifier suites, full-file run) |
| T28 | F2-A3 coverage-authority contract unchanged | PASS (pre-existing coverage suites, full-file run) |
| T29 | F2-A5 source-obligation contract unchanged | PASS (pre-existing suites; `tests/unit/test_retrieval.py` regression 59 passed + 27 subtests) |
| T30 | F3 fixed-locator retirement intact (no historical literals reintroduced) | PASS (`test_f3_fixed_locator_retirement_intact`) |

## 19. Public API / default preservation

`QAResult`, answer rendering, claim/evidence schemas, normal public API
response, and the default answer-point mode (`legacy_question_core`) are
unchanged. `runtime_e1_v2` remains VALIDATED_EXPERIMENTAL_PATH /
EXPLICIT_SELECTION_ONLY. E1/E2/E3 semantics (decomposition, answer-point
schemas, coverage modes, missing-point trigger, retained support, atomic
update, one-revision bound, verified-claim renderer) are untouched — F4 changed
role routing, not the scientific answer contract. All F2 outcomes and the F3
retirements are preserved.

## 20. Scientific / evaluation accounting

PANDA scientific/evaluation calls: **0**. PANDA scientific/evaluation tokens:
**0**. No T2/T3/T4/T5/release evaluation, LLM judge, protected holdout, model
comparison, or promotion evaluation was run. No live Vertex calls; unit tests
with fakes only.

## 21–22. F4 lifecycle decision and Phase-F state

F4 = COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED
(all sixteen §61 PASS conditions hold). Promotion materiality recorded only:
promotion evaluation not authorized; default unchanged. Phase F =
IN_PROGRESS / F4_COMPLETE_F5_NOT_STARTED. F5/F6 remain; Phase F is not marked
complete.

## 23. Next recommendation

F5 — Bounded Answer Composer. Recommendation only; not started.

## 24. Execution authorization

NEXT_TASK_EXECUTION_AUTHORIZED = false

## Verification record

- `PYTHONPATH=src python -m pytest tests/unit/test_vertex.py -q` → 20 passed
  (13 pre-existing unmodified + 7 new).
- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → 135 passed +
  19 subtests (111 pre-existing unmodified + 24 new).
- Integrated focused run `PYTHONPATH=src python -m pytest
  tests/unit/test_vertex.py tests/unit/test_qa.py -q` → 155 passed + 19
  subtests.
- `PYTHONPATH=src python -m pytest tests/unit/test_retrieval.py -q` → 59 passed
  + 27 subtests (F2-A5/F3 seam regression).
- Static: `git diff --check` clean; `git status --short` shows exactly the five
  authorized files (`.env.example`, `src/panda_agent/llm/vertex.py`,
  `src/panda_agent/qa.py`, `tests/unit/test_qa.py`, `tests/unit/test_vertex.py`).
  service.py/prompts.py needed no change and were not modified. No SHA256/hash
  bookkeeping generated.
