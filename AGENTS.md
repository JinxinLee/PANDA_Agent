# PANDA Agent — Codex Development Instructions

This repository is an English-only, evidence-grounded PANDA QA system. Keep code, prompts, datasets, technical documentation, identifiers, and machine-readable artifacts in English.

Prototype development does not require freezing every implementation state.

Do not create frozen candidates, integrity manifests, per-file hashes, or
clean-tree checkpoints during ordinary roadmap-task development.

When commits are requested or required by the authorized workflow, use normal Git commits as the primary development history. This instruction does not require a commit or a clean working tree to complete ordinary development work.

A strict frozen implementation identity is required only when:
- the user explicitly requests a frozen candidate;
- an explicitly authorized T3/T5 or formal phase-boundary evaluation requires immutable provenance;
- an explicitly authorized release or acceptance comparison requires immutable provenance.

Ordinary development checks are not formal acceptance comparisons. A provenance requirement does not itself authorize an evaluation.

Small targeted tests and ordinary before/after development checks may run
against the current working tree. Record relevant changes and limitations,
but do not turn them into formal frozen candidates.

## Sources of truth

- `AGENTS.md`: stable development and stop rules.
- `docs/GENERALIZATION_ROADMAP.md`: Generalization Phase architecture and task cards.
- `docs/EVALUATION_POLICY.md`: evaluation tiers, failure taxonomy, cost controls, and gates.
- `docs/EVALUATION_STATUS.md`: one current status followed by labelled historical records.

Use code and actual artifacts to establish implemented behavior and observed results when descriptive documentation is stale. They do not grant authorization or override explicit scope, evaluation, or lifecycle restrictions. Resolve descriptive discrepancies within the requested scope; ask only when a material authorization conflict remains.

## Development scope

- Complete the user's requested task, including necessary investigation, implementation, relevant documentation, proportionate verification, and fixes for failures caused by the change. A roadmap task ID is not required when the requested outcome is clear. Do not start a subsequent roadmap task or cross an explicit evaluation or lifecycle boundary without authorization.
- Resolve routine implementation details using repository conventions and reasonable assumptions. Ask for clarification only when missing information materially affects correctness, scope, or authorization and cannot be resolved from available context. Honor authorization already given for the same task; ask again only if the proposed action exceeds it. If a step is blocked, complete independent authorized work and report the blocked step, the reason, and the specific input or authorization needed.
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

A task is complete when all requested deliverables and authorized required steps are finished and proportionately verified. A status label does not substitute for completing remaining authorized work. If blocked, report completed work and outstanding steps separately. Apply PASS, FAIL, or INCONCLUSIVE to the stated verification scope; do not imply that unrun evaluations passed.

After each roadmap task:

1. summarize implementation;
2. list changed files;
3. report every evaluation actually performed and its cost;
4. report before/after metrics where applicable;
5. state exactly `PASS`, `FAIL`, or `INCONCLUSIVE`;
6. list concrete limitations;
7. identify the next roadmap task if it is established and relevant; do not execute it;
8. end after completing the current authorized scope or exhausting independent authorized work when blocked.
