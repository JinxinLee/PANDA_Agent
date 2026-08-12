# PANDA Agent — Codex Development Instructions

This repository is an English-only, evidence-grounded PANDA QA system. Keep code, prompts, datasets, technical documentation, identifiers, and machine-readable artifacts in English.

## Sources of truth

- `AGENTS.md`: stable development and stop rules.
- `docs/GENERALIZATION_ROADMAP.md`: Generalization Phase architecture and task cards.
- `docs/EVALUATION_POLICY.md`: evaluation tiers, failure taxonomy, cost controls, and gates.
- `docs/EVALUATION_STATUS.md`: one current status followed by labelled historical records.

Code and actual artifacts are authoritative when documentation is stale.

## Development scope

- Implement only the roadmap task explicitly requested by the user, then stop. Do not automatically start the next task.
- Prefer the smallest general mechanism that addresses the observed failure class.
- Avoid unrelated refactoring and do not introduce future roadmap architecture early.
- Preserve existing behavior outside the requested scope where practical.
- Do not add multilingual or Chinese-query support unless product scope is explicitly changed.

## Generalization safety

Evaluation questions are measurement data, not implementation specifications. Do not add question-specific trigger phrases, expected symbols, paths, PDF pages, answers, source quotas, weights, or special-case guards solely because they occur in a failing evaluation question.

Every behavior change must be justified for a class of unseen questions. Repair the layer where the failure originates:

- candidate-recall failure → retrieval;
- entity-resolution failure → resolver;
- decomposition failure → decomposition;
- answer or verification failure → the corresponding answer layer.

Do not compensate at a downstream layer for an upstream failure.

## Evaluation and cost

- Follow `docs/EVALUATION_POLICY.md` and use the smallest tier that can test the current hypothesis.
- “Run tests”, “verify the change”, “make sure it works”, and “check regressions” do not authorize a full benchmark.
- T5 requires an explicit user instruction containing `T5` or `release evaluation`.
- T3 requires explicit authorization in the current task. A complete dataset or a request to establish/freeze A3 baseline does not authorize T3.
- Do not regenerate hashes merely because files changed.
- Do not perform a full reindex unless technically required.
- Reuse compatible embeddings and frozen intermediate artifacts.
- Do not call answer generation to test retrieval or an external judge to test runtime QA.

## Completion

After each roadmap task:

1. summarize implementation;
2. list changed files;
3. report every evaluation actually performed and its cost;
4. report before/after metrics where applicable;
5. state exactly `PASS`, `FAIL`, or `INCONCLUSIVE`;
6. list concrete limitations;
7. name the next roadmap task only;
8. stop.
