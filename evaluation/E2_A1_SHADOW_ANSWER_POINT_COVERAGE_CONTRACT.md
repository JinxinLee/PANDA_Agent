# E2-A1 — Shadow Answer-Point Coverage Contract

E2-A1 VERDICT = PASS

COMPLETE / PASS / SHADOW_ANSWER_POINT_COVERAGE_CONTRACT_IMPLEMENTED

Starting HEAD: `860faf60417fe099baa6d3a0b4ba59926363ca90`.
This is an ordinary implementation commit, not a frozen scientific candidate.

## Implemented contract

`QAAgent.run_answer_point_coverage_diagnostic(question)` invokes unchanged E1
decomposition and projects only `answer_point_id` and `text` into the existing
QA graph under `shadow_e1_v2`. Full decomposition remains diagnostic output;
taxonomy, ambiguity, spans, and other decomposition metadata do not drive QA.
Normal `run` and `run_detailed` never invoke decomposition and retain
`question_core`, the original prompts, schemas, and public result contract.
`PROMPT_SET_VERSION` is 3.8.0; separate shadow review/revision prompts are added.

There is no new mapper stage or coverage model call. The existing evidence
review checks evidence support, relevance, independently verified point mappings,
collective completeness, and legacy requirements together. Declared mappings are
untrusted proposals: valid but wrong IDs can be corrected semantically, while
unknown declarations remain deterministic defects. Claims with deterministic
mapping, evidence, version, provenance, or identifier defects are excluded before
shadow review. Internal synthetic claims remain excluded from user coverage.
Deterministic locator additions have unresolved empty declarations in shadow
and require reviewer mapping; no first-point assignment is hardcoded.

Review validation requires exactly one record for each reviewable claim, known
unique IDs, and no invented covered point without a supported relevant mapped
claim. A mapping alone does not imply completeness: the review independently
reports `missing_answer_point_ids`. Unsupported and irrelevant claims cannot
contribute. Shadow review cannot be overridden by deterministic code anchoring.
Malformed review decisions fail closed with an explicit error and unevaluable
coverage; there is no additional review retry.

## Audit and bounded revision

The final verify state supplies `answer_point_audit`: mode, projected
`answer_points`, `claim_mappings` (claim ID, declared IDs, verified IDs, evidence
IDs, supported and rendered flags), covered IDs, missing IDs,
`coverage_complete`, `coverage_evaluable`, and review error when applicable.
Declared IDs survive correction and the second verification; rendered flags
reflect final public claims. Unsupported mappings may remain as audited reviewer
decisions but cannot count toward coverage. Early refusal has no invented claim
mappings and `coverage_evaluable=false`; its all-points-missing placeholder is
not a semantic completeness judgment.

Missing points enter the existing single revision with their ID/text and the
existing evidence. Supported claims are preserved; revised claims undergo the
same review. Final audit reflects that final review, including remaining gaps.
`missing_requirement_ids` stays a separate compatibility channel. No missing-point
retrieval, second revision, public DTO/API change, or production activation is
implemented. Existing partial-answer/refusal semantics remain: an ANSWERED
result is not itself evidence of complete shadow coverage.

## Verification and cost

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py tests/unit/test_question_decomposition.py -q`: 70 passed (38 QA, 32 E1).
- `PYTHONPATH=src python -m pytest tests/unit/test_e2_a1_answer_point_coverage.py tests/unit/test_qa.py -q`: 80 passed (42 E2-A1, 38 QA).
- Static baseline comparison: every existing prompt constant except the version
  is unchanged; `ANSWER_SCHEMA` and `REVIEW_SCHEMA` are structurally unchanged.
- Tests cover projection, normal isolation, semantic correction, mapping versus
  completeness, claim eligibility, internal claims, unresolved locators, final
  audit after revision, malformed review, early refusal, separate legacy
  requirements, and bounded call/retrieval counts.
- No live decomposition, analyzer, embedding, reranker, retrieval provider,
  QA generation/review/revision, or judge calls: each 0; scientific tokens 0.
- AGY job `staffer-mtszoimt-e5ba0443` completed an abstract static design review.
  It received the supplied design only, with no repository inspection or edits.
  Routing was `gemini-3.8-flash-high`; the worker reported Gemini 3.8 Flash / High.
  Provider-attested model/effort and token usage were not returned by the
  collected result. Worker usage is separate from scientific usage and is not
  claimed to be zero. Its key design checks are covered by focused tests; this
  was not an independent implementation inspection or scientific validation.

No full suite, T2/T3/T5, real QA evaluation, reindex, frozen-artifact rewrite,
hash generation, or benchmark-specific implementation occurred. No scientific
before/after metrics exist for E2-A1. Fake decisions establish contract behavior,
not real semantic mapping accuracy or missing-point precision/recall.

## Lifecycle

E1 = COMPLETE / PASS / QUESTION_ONLY_SEMANTIC_ANSWER_POINT_DECOMPOSITION_VALIDATED.
Historical E1 outcomes remain unchanged, including E1-A2 FAIL.
E2 = IN_PROGRESS / SHADOW_COVERAGE_CONTRACT_IMPLEMENTED / TARGETED_VALIDATION_PENDING.
Phase E = IN_PROGRESS / E2. E3 = NOT_STARTED.
D4 remains PAUSED with overall completion UNDECIDED; F1 and Phase F are unchanged.

NEXT_TASK_RECOMMENDATION = E2-A2 — Targeted Claim-Mapping and Missing-Point Validation

NEXT_TASK_EXECUTION_AUTHORIZED = false

E2-A2 must establish real semantic mapping and missing-point quality under
separate authorization. E2-A1 PASS is limited to this shadow implementation and
its focused contract/regression verification; it is not E2 acceptance.
