# E1-A1 — Dynamic Question Decomposition Contract

## Decision

COMPLETE / PASS / QUESTION_ONLY_DIAGNOSTIC_DECOMPOSITION_IMPLEMENTED.
E1-A1 PASS does not mean E1 PASS: semantic decomposition quality remains unmeasured.

## Starting state

Actual starting HEAD: `80b5aa29ac81cc294c2d72e8fe3234d218da3ed0`; working tree clean. F1 accepted, Phase F IN_PROGRESS / F1_COMPLETE, Phase E not started. D4 PAUSED / ROADMAP_RECONCILIATION with overall completion UNDECIDED. No material lifecycle conflict.

## Architecture implemented

`question_decomposition.py` owns `QuestionDecomposer`, its structured schema, prompt version `1.0.0`, and normalized output version `e1.question_decomposition.v1`. The existing Vertex `generate_json` abstraction produces a proposal; local strict validation and normalization produce the diagnostic dictionary. No extra retry, router, cache, configuration, or infrastructure was added. Production `PROMPT_SET_VERSION` remains unchanged.

## Question-only boundary

The generation payload contains exactly `task: decompose_user_question` and `untrusted_question: <raw question>`. No retrieval plan, evidence, requirements, Gold, labels, annotations, or answers enter it. The system prompt reuses the common security boundary and requests minimal explicit needs, never hidden domain prerequisites or answers.

## Answer-point contract

One to five points, including when a fake bypasses provider schema enforcement. Generic facets: definition, mechanism, implementation, data_flow, comparison, locator, workflow, cause_reason, api_behavior, constraint. Each point has non-empty text and at least one exact non-empty original-question support span. Any invalid span rejects the entire result; duplicate spans retain first-occurrence order. Text whitespace is normalized; casefolded duplicate text is rejected. Extra fields, including model-generated IDs, are rejected. Ambiguity status is clear or ambiguous, with a string reason, and has diagnostic meaning only.

## Stable-ID policy

Sort by earliest question support position, then facet type and normalized casefolded text. Duplicate-text rejection makes the tie-break independent of proposal order. Assign facet-local ordinals starting at 1, for example `locator.1` and `locator.2`. IDs are unique by construction. No model IDs, UUIDs, random values, or hashes. This does not establish semantic paraphrase stability.

## Shadow/runtime boundary

`QAAgent.decompose_question(question)` explicitly delegates using the existing Vertex client. It is not called by the production graph, `run`, or `run_detailed`; no service/API/evaluation activation or new endpoint was added. Default QA gains zero decomposition calls. Output mode is `shadow_diagnostic`; no diagnostic ambiguity changes QA status, retrieval, or generation.

## Compatibility behavior retained

`_runtime_answer_points` still returns `question_core`. Existing answer/review/revision schemas and prompts, `_answer_requirements`, `_requirement_evidence`, deterministic missing-requirement checks, locator/data-flow augmentation, and required boundary locators are unchanged. No F1 debt repair, E2 coverage mapping, or E3 retrieval logic was implemented.

## Focused verification

T0 only, synthetic questions and deterministic fake Vertex responses:

- `python -m pytest tests/unit/test_question_decomposition.py -q`: first attempt stopped at collection because `panda_agent` was not importable. With `PYTHONPATH=src`, 19 passed. After strengthening default-QA assertions, rerun: 19 passed.
- `python -m pytest tests/unit/test_qa.py -q -k 'test_answered_path_is_bounded_and_cited or test_agent_core_run_has_no_service_import_or_database_persistence'` with `PYTHONPATH=src`: 2 passed, 36 deselected.
- `git diff --check`: PASS.

Contracts cover single/multiple points, proposal-order normalization, same-facet ordinals and tie-breaks, duplicate text/spans, invalid support, count limits, invalid facets/text/model IDs, question-only payload, ambiguity, explicit QA seam, unchanged `question_core`, and no default invocation. Both normal QA entry points complete with answered status and only two existing fake model calls (answer and review).

## Cost

Analyzer calls = 0; Embedding calls = 0; Reranker calls = 0; Answer generation live calls = 0; Decomposition live calls = 0; Judge calls = 0; Total live model calls = 0; Token usage = 0. Scientific evaluations = 0. No benchmark/novel dataset or Gold annotation was accessed.

## Limitations

T0 establishes schema, input boundaries, validation, deterministic IDs, counts, lexical support, and non-activation. It does not measure real-model accuracy, provider schema acceptance, Gold recall, semantic over/under-decomposition, paraphrase stability, or benchmark-versus-novel generalization. Exact spans do not prove semantic adequacy. No before/after semantic metrics exist for this task.

## Lifecycle closeout

E1-A1 COMPLETE / PASS. E1 IN_PROGRESS / DIAGNOSTIC_IMPLEMENTATION_COMPLETE / VALIDATION_PENDING. Phase E IN_PROGRESS / E1. D4 remains PAUSED / ROADMAP_RECONCILIATION, overall completion UNDECIDED. F1 remains accepted; Phase F IN_PROGRESS / F1_COMPLETE. Production activation, E2, and E3 remain unimplemented.

## Next task recommendation

E1-A2 — Targeted Dynamic Question Decomposition Validation.
NEXT_TASK_EXECUTION_AUTHORIZED = false. Stop after E1-A1 and its normal Git commit.
