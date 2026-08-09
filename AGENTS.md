# PANDA Agent — Codex Development Instructions

This file defines how Codex should work in this repository during ordinary development.

The repository is under active prototype development. The default objective is to make the requested functionality work with the smallest useful change and the minimum validation needed to support the next development decision.

Formal benchmark evaluation is a separate workflow. Do not enter it automatically.

## 1. Sources of truth

Use the following files for different purposes:

- `AGENTS.md` — day-to-day development behavior and validation defaults.
- `docs/EVALUATION_POLICY.md` — stable rules for formal evaluation, candidate freezing, rescoring, gates, and acceptance.
- `docs/EVALUATION_STATUS.md` — current benchmark/evaluator/candidate state and historical evaluation results.

Do not copy transient candidate status, hashes, case lists, token counts, or dated evaluation results into this file.

For ordinary implementation tasks, do not read `docs/EVALUATION_STATUS.md` unless the task depends on the current evaluation state.

## 2. Default development mode: prototype first

For ordinary development tasks:

- Implement the requested change directly.
- Prefer the smallest reasonable change.
- Preserve existing behavior outside the requested scope where practical.
- Avoid unrelated refactoring, cleanup, formatting churn, or architectural redesign.
- Prefer an existing abstraction over creating a new one unless the current task clearly needs it.
- Do not add speculative compatibility layers, wrappers, retries, fallbacks, migration code, generalized validators, or broad exception handling for hypothetical future failures.
- Handle observed and likely runtime failures; do not harden every theoretical edge case during prototype work.
- Do not proactively add logging, instrumentation, benchmarks, documentation, or tests unrelated to the requested change.
- Once the requested behavior works and minimum useful validation is complete, stop.

When a possible production-hardening concern is discovered but is not required for the current task, mention it briefly rather than implementing it automatically.

## 3. Validation must be proportional to the change

Use the smallest validation surface that can meaningfully detect an error caused by the current change.

### 3.1 Documentation, comments, UI text, report formatting

Default:

- inspect the diff;
- run a formatter/link/markup check only if directly relevant.

Do not automatically run:

- Python compilation;
- the full unit-test suite;
- retrieval evaluation;
- QA evaluation;
- Vertex/model calls;
- hash verification;
- candidate freezing.

### 3.2 Small local code change

Examples: one function, one condition, one parser branch, one UI behavior, one configuration value.

Default:

1. inspect the changed code;
2. run the smallest directly relevant deterministic test/check if one exists;
3. stop if that provides sufficient confidence.

Do not automatically run project-wide validation.

### 3.3 Agent behavior change

Examples: query analysis, routing, retrieval, reranking, answer generation, sufficiency, claim verification, revision, prompt behavior.

Default:

1. run the directly affected case first;
2. if it fails, iterate on that case;
3. once it passes, optionally run 1–2 closely related cases or sentinels when useful;
4. stop.

Do not automatically expand a normal development edit into a 5–20 case regression.

A broader focused regression is a checkpoint operation, not the default inner development loop.

### 3.4 Cross-cutting or high-risk change

For changes that genuinely affect shared interfaces, multiple major modules, model configuration, index identity, or repository-wide behavior:

- run targeted deterministic tests for the affected modules;
- run a small representative focused evaluation when behavior is model-backed;
- expand validation only when evidence from the targeted checks justifies it.

## 4. Expensive model calls

Treat every Vertex/model-backed evaluation as expensive.

Before making additional model calls, ask:

> Will this result materially affect the next development decision?

If not, skip the call.

Prefer, in order:

1. static inspection;
2. deterministic local checks;
3. one affected case;
4. 1–2 related sentinels;
5. a focused checkpoint set;
6. a full benchmark run.

Do not move to a more expensive level merely for reassurance.

Reuse existing records whenever the relevant runtime identity has not changed and the evaluation policy permits reuse.

## 5. Tests are not automatically cumulative

A small change does not imply that all lower and higher validation layers must run.

For example, a local answer-rendering fix does not automatically require:

- corpus verification;
- index verification;
- the full retrieval suite;
- every intent sentinel;
- the full QA dev split;
- regression/challenge;
- acceptance.

Run only the affected dependency closure.

## 6. Hashes and candidate identity

Do not calculate, compare, record, or verify repository/file/model/prompt/index hashes during ordinary prototype work merely to prove that nothing changed.

Hashing and identity freezing belong to formal evaluation when they are required for reproducibility.

Hash/identity work is appropriate only when:

- explicitly requested;
- creating or verifying a frozen candidate;
- performing a formal full-dev/regression/acceptance run;
- the application itself depends on the hash;
- a specific reproducibility/debugging question requires it.

Do not begin an ordinary coding task by checking hashes or candidate manifests.

## 7. Formal evaluation is opt-in

Enter the formal evaluation workflow only when one of the following is true:

- the user explicitly requests an evaluation/checkpoint/gate/freeze/release run;
- a major development milestone is complete and the task specifically asks to validate it;
- the task is about evaluation infrastructure itself.

When formal evaluation is required, follow `docs/EVALUATION_POLICY.md`.

Do not infer that a code edit automatically authorizes:

- candidate freezing;
- full dev;
- full regression;
- challenge;
- hidden acceptance;
- M7/M8;
- release gating.

## 8. Evaluation-infrastructure changes

If a change affects only deterministic evaluation logic, such as:

- scorer/judge post-processing;
- Gold schema interpretation;
- selector matching;
- report generation;
- gate calculation;
- deterministic verifier logic;

prefer unit tests and offline recomputation/rescore of existing records.

Do not regenerate model answers unless answer-generation behavior actually changed.

## 9. Evaluation status

When a task depends on the currently approved Gold, evaluator version, unresolved failures, candidate identity, or which runs are authorized, read:

`docs/EVALUATION_STATUS.md`

Treat the newest section marked **Current authoritative state** as authoritative over older historical records.

Do not silently promote a diagnostic subset/composite into a complete benchmark result.

## 10. Completion rule

After completing a requested development change:

- summarize what changed;
- state the validation actually performed;
- mention any important broader validation deliberately not run;
- stop.

Do not continue with speculative hardening, cleanup, refactoring, hashing, benchmarking, report generation, or additional tests after the task is complete.
