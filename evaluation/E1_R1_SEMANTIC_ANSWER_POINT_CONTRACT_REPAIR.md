# E1-R1 — Semantic Answer-Point Contract Repair

## Decision and scope

COMPLETE / PASS / SHADOW_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIRED.
PASS applies to implementation and targeted T0 checks, not real-model semantic quality.
E1 remains IN_PROGRESS / REPAIR_IMPLEMENTED / REVALIDATION_PENDING.

Starting HEAD: `6bb43ec8b76069639c00ca4ff697056fbfd49d15`; initial working tree clean. Work follows the accepted E1-AR architecture. Changes are ordinary working-tree development, not a frozen candidate or scientific execution. No commit or push was requested for this task.

## Implemented contract

The standalone decomposition prompt is now `2.0.0`, with normalized output schema `e1.question_decomposition.v2`. Production `PROMPT_SET_VERSION` is unchanged. The explicit `QAAgent.decompose_question` seam continues to delegate to the module without any new QA graph invocation.

- The prompt defines an answer point as an explicit response obligation that is independently satisfiable and independently checkable for omission. Generic distributive location/contribution examples contrast with a single comparison or end-to-end flow. No runtime lexical rules, question-specific triggers, hidden stages or benchmark entities were introduced.
- Sort by earliest exact support-span position, then normalized casefolded text. Existing duplicate-text rejection supplies a deterministic tie-break. Assign `point.1`, `point.2`, etc. in that order. Taxonomy does not influence ordering or IDs. IDs are local to one decomposition trace, not cross-paraphrase semantic identifiers.
- `facet_type` is optional diagnostic metadata. The provider schema requests only known string labels when supplied; omission is allowed. Local normalization retains recognized labels and omits missing/null/unknown/non-string values without rejecting an otherwise valid semantic point. The tolerant validator is confined to this field; core text, spans, count, extra-field and model-generated-ID checks remain strict.
- Preserve raw-question-only input, 1–5 points, exact non-empty question spans, span deduplication, duplicate normalized-text rejection, diagnostic ambiguity, and shadow-only execution. No retry, new model role, configuration or infrastructure was added.

Only the explicitly called shadow decomposer uses this semantic contract. Production completeness still uses `question_core` and existing compatibility requirements; no claim coverage, E2/E3, retrieval, API or production activation changes were made.

## Focused verification

All commands used `PYTHONPATH=src` and deterministic model doubles. No full suite ran.

1. `python -m pytest tests/unit/test_question_decomposition.py -q`: 32 passed initially; 32 passed again after finalizing the optional metadata input schema.
2. `python -m pytest tests/unit/test_e1_a2_dynamic_question_decomposition_validation.py -q` against current v2: 23 passed, 1 failed. The frozen fake judge requires v1 IDs (`locator.1`, `cause_reason.1`), while the current decomposer deliberately returns v2 IDs. This is a version-incompatible historical test, not a passed v2 check. Its fixtures were not rewritten.
3. The same frozen E1-A2 test file, with only `panda_agent.question_decomposition` loaded in-memory from preregistration commit `77ea6bc27beb1657673e57be763b05419c98bc05` using `git show`: 24 passed. Pytest emitted one pre-import assertion-rewrite warning for `anyio`. This fake-only check confirms the original test/implementation pair remains usable; it is not a scientific rerun or regrading.
4. `git diff --check`: PASS. Changed-path review confirms no historical E1-A1/E1-A2/E1-AR artifact, frozen runner/test, normal QA source, production prompt, retrieval module or configuration changed.

V2 checks cover omitted/invalid diagnostic metadata, metadata-independent ordering and IDs including tied support positions, shuffled proposal order, question-only payload, strict semantic validation, count bounds, local ID uniqueness, and both normal QA entry points retaining only the existing fake answer/review calls. Synthetic location/contribution/comparison/flow proposals verify representation only.

The normalizer intentionally does not split a structurally valid broad point by lexical cues. T0 therefore cannot establish that the model will now recover independently requested obligations correctly. E1-R2 must measure that behavior prospectively.

## Compatibility and limitations

The v2 schema/ID change is intentional and visible. Historical E1-A2 runners and tests belong to their frozen implementation checkout; the old v1 fake-judge fixture is incompatible with the current v2 module. Do not run historical scientific acceptance against the current module or treat a mixed-version test as valid evidence. A future v2 evaluator must be separately preregistered.

E1-A2 remains COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED. Its original files and all E1-AR findings remain unchanged. No new reference recall, precision, atomicity accuracy, paraphrase stability or hidden-prerequisite rate was measured. No benchmark or novel source dataset was reopened, and no protected split was accessed.

## Cost and lifecycle

Analyzer calls = 0; Embedding calls = 0; Reranker calls = 0; QA live calls = 0; Decomposition live calls = 0; Judge calls = 0; Total live model calls = 0; Token usage = 0.

E1-R1 = COMPLETE / PASS / SHADOW_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIRED.
E1 = IN_PROGRESS / REPAIR_IMPLEMENTED / REVALIDATION_PENDING.
Phase E = IN_PROGRESS / E1. E2 and E3 remain NOT_STARTED. Production activation = false.
D4 remains PAUSED / ROADMAP_RECONCILIATION, overall completion UNDECIDED. F1 remains accepted and Phase F remains IN_PROGRESS / F1_COMPLETE.

Next recommendation: E1-R2 — Prospective Semantic Answer-Point Revalidation, with a fresh prospective acceptance cohort. E1-A2 cases may be exposed regression diagnostics, not the sole acceptance cohort. NEXT_TASK_EXECUTION_AUTHORIZED = false. No live validation or subsequent task was executed.
