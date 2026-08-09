# M6 Phase 6.0–6.7 Runbook

> **历史计划说明：** 本 Runbook 记录 2026-08-02 的 Lite RC1 执行契约。当前 runtime 已于 2026-08-03 恢复为 `gemini-3.6-flash`；当前焦点结果以 `docs/M6_PHASE6_0_7_RESULT.md` 为准。

## Scope

This runbook covers the runtime-model migration, candidate freeze, one complete
80-question development run, and the exposed 16-question regression run. It
does not create or run hidden acceptance and does not unlock M7.

## Model roles

The actual project setting is `QA_GENERATION_MODEL_ID`:

```env
QA_GENERATION_MODEL_ID=gemini-3.5-flash-lite
QA_EVALUATION_JUDGE_MODEL_ID=gemini-3.6-flash
QA_EMBEDDING_MODEL_ID=gemini-embedding-2
QA_EMBEDDING_DIMENSIONS=3072
```

Lite is used by analyzer, reranker, answer, evidence review, and revision.
The evaluation judge uses the separate `QA_EVALUATION_JUDGE_MODEL_ID` client.
Embedding remains unchanged.

## Required order

1. Run source, Gold, index, dependency, unit-test, and Vertex health gates.
2. If any environment gate fails, stop and classify it as `environment`; do not run model evaluation.
3. Run the 12 dev migration sentinels and regression `g098`.
4. Freeze and verify `m6-v2-lite-rc1`.
5. Run exactly one complete dev run with the same run ID on resume.
6. If the development gate passes, run exactly one complete regression run of 16 cases.
7. Do not run challenge or acceptance.

## Current execution status

As of the latest Phase 6 attempt:

- Docker Engine 29.3.1 and Docker Compose: passed in the approved non-sandbox context;
- source corpus, Gold official validation, PostgreSQL/Qdrant index, Lite/judge/embedding health: passed;
- compileall, `pip check`, and unit tests: passed, 71/71;
- focused `g085` and `g098`: passed;
- candidate `m6-v2-lite-rc1`: frozen and verified, manifest SHA `89167400400131be66746e590072d7e29bbc4df5f2503f3aa12153d4e06edacd`;
- full dev: completed 80/80, development gate failed;
- failure review: generated at `data/evaluation/runs/m6-v2-lite-qa-dev-rc1/failure_review.yaml` and `.md`;
- regression 16, challenge 24, acceptance, M7 and M8: not run.

The next action is human review of the failure table. Do not modify the frozen
candidate or start a new model run until `panda-qa-eval review --check` passes.

## Commands

```powershell
docker compose up -d --wait
..\.venv\Scripts\python.exe -m panda_agent.cli.source --project-root . verify
..\.venv\Scripts\python.exe -m panda_agent.cli.index --project-root . verify
..\.venv\Scripts\python.exe -m panda_agent.cli.evaluate --project-root . validate --official
..\.venv\Scripts\python.exe -m panda_agent.cli.healthcheck
```

Focus run:

```powershell
panda-qa-eval run qa --split dev --run-id m6-v2-lite-focused-rc1 `
  --case-id g001 --case-id g007 --case-id g012 --case-id g013 `
  --case-id g027 --case-id g051 --case-id g070 --case-id g076 `
  --case-id g077 --case-id g085 --case-id g105 --case-id g112 `
  --max-model-calls 100 --max-token-usage 1500000 --deadline-minutes 30

panda-qa-eval run qa --split regression --run-id m6-v2-lite-focused-regression-rc1 `
  --case-id g098 --max-model-calls 12 --max-token-usage 200000 --deadline-minutes 10
```

Freeze and verify:

```powershell
panda-qa-eval freeze --candidate-id m6-v2-lite-rc1
panda-qa-eval verify-candidate --candidate-id m6-v2-lite-rc1
```

Complete dev:

```powershell
panda-qa-eval run qa --split dev --run-id m6-v2-lite-qa-dev-rc1 `
  --max-model-calls 600 --max-token-usage 7500000 --deadline-minutes 90
```

Complete regression, only after dev passes:

```powershell
panda-qa-eval run qa --split regression --run-id m6-v2-lite-qa-regression-rc1 `
  --max-model-calls 140 --max-token-usage 1800000 --deadline-minutes 30
```

## Candidate and budget invariants

- Candidate manifests contain runtime and judge model IDs separately.
- Resume requires an identical manifest and never repeats completed cases.
- Budget exhaustion writes `run_status.json` with attempt and cumulative usage;
  resume uses a fresh bounded attempt window with the same run ID and never
  repeats completed cases.
- A code, Prompt, model, policy, index, evaluator, or Gold change invalidates the frozen candidate.
- A focused or partial run can diagnose a problem but cannot pass the development gate.

## Audit decision

The signed v2 YAML remains byte-for-byte unchanged. The accepted selector and
cluster interpretation is recorded in:

```text
evaluation/benchmarks/v2/audit_resolution.yaml
```

The decision applies only to exposed dev/challenge/regression data. It does not
authorize hidden acceptance or release.
