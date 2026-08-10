# PANDA Research QA Agent

This directory contains the version-aware, evidence-grounded QA system for the
LuminosityFit, PandaRoot, and RestgasDetermination research software corpus.

The implementation and decision log is maintained in [QA_AGENT.md](QA_AGENT.md).
The three source PDFs remain in `raw_pdf/`; locked repositories and web snapshots
are acquired under ignored `data/sources/` paths. See `QA_AGENT.md` for exact
commits, hashes, architecture decisions, commands, and verified results.

## Quick start

From the `Agent_learn` workspace root, activate a Python 3.12 environment and
install the QA extra. The normal new-user path uses a prebuilt Bundle; it does
not rebuild the corpus or index.

```powershell
Set-Location .\PANDA_Agent
..\.venv\Scripts\python.exe -m pip install -e ".[qa]"
Copy-Item .env.example .env

# Start only the PostgreSQL and Qdrant dependencies.
docker compose up -d --wait postgres qdrant

$bundlePath = 'D:\panda-bundles\panda-kb-prototype-v2.0.0'
panda-qa-kb restore --bundle $bundlePath --project-root (Get-Location)
panda-qa-kb verify --bundle $bundlePath --project-root (Get-Location)
# Before registration, verify may report runtime_status=not_registered and still exit 0.
python -m alembic upgrade head
panda-qa-runtime register-runtime --bundle $bundlePath --project-root (Get-Location)
panda-qa-runtime verify --project-root (Get-Location)
panda-qa-api --project-root (Get-Location)
```

`panda-qa-api` listens on loopback `127.0.0.1:8000` with one Uvicorn worker.
After it is ready, send a question to `POST /v1/qa` (the input question is
trimmed and must be 1–10,000 characters):

```powershell
Invoke-RestMethod http://127.0.0.1:8000/v1/qa -Method Post `
  -ContentType 'application/json' -Body (@{question='How is event_poca used?'} | ConvertTo-Json)
```

The migration, registration receipt, route/error contract, and P0 limitations
are documented in [docs/M7_P0_IMPLEMENTATION.md](docs/M7_P0_IMPLEMENTATION.md).
M7 P0 is implemented in this working tree, but M7 overall is not passed: the
real four-question smoke and M7 P1 deadline/504, model-usage, and JSON-logging
checks remain outstanding. M8 has not started.

For a source-building workflow (which performs network crawling and indexing),
inspect the existing commands in [QA_AGENT.md](QA_AGENT.md) after the Bundle
quickstart. If an index process was interrupted, inspect `ingestion_runs` and
resume it:

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.index resume --run-id <RUN_ID>
```

The health check uses Application Default Credentials and the
`QA_GCP_PROJECT_ID`/`QA_VERTEX_LOCATION` values. Model IDs can be overridden with
`QA_GENERATION_MODEL_ID` and `QA_EMBEDDING_MODEL_ID`; the fixed embedding
contract requires `QA_EMBEDDING_DIMENSIONS=3072`.

## Knowledge bundle prototype

The local prototype can export, inspect, restore, and verify one fixed
PostgreSQL/Qdrant knowledge state with `panda-qa-kb`. The maintainer/user
workflow, exact manifest checks, clean-target preconditions, and current
limitations are documented in
[docs/KNOWLEDGE_BUNDLE_PROTOTYPE.md](docs/KNOWLEDGE_BUNDLE_PROTOTYPE.md).
New users who receive the code and a prebuilt bundle should follow the
[Chinese first-run guide](docs/NEW_USER_BUNDLE_GUIDE.md); it does not require
corpus parsing, document embedding, or indexing.
The matching public runtime package is
[PANDA Knowledge Bundle Prototype v2.0.0](https://github.com/JinxinLee/PANDA_Agent/releases/tag/panda-kb-prototype-v2.0.0).
The 2026-08-09 round2 record is a real live export → inspect → isolated restore
→ verify → three-smoke PASS. It is still a local prototype acceptance only,
not a public/release security gate or an offline replacement for Vertex dense
query embedding; see the linked document for exact hashes, counts, paths, and
smoke summaries.

From the project checkout (use a disposable target for restore), the command shape is:

```powershell
$bundlePath = 'D:\panda-bundles\panda-kb-prototype-v2.0.0'
..\.venv\Scripts\panda-qa-kb.exe export --bundle $bundlePath --project-root (Get-Location)
..\.venv\Scripts\panda-qa-kb.exe inspect --bundle $bundlePath
..\.venv\Scripts\panda-qa-kb.exe restore --bundle $bundlePath --project-root (Get-Location)
..\.venv\Scripts\panda-qa-kb.exe verify --bundle $bundlePath --project-root (Get-Location)
```

### Migration equivalence test

The frozen 10-question migration suite, clean-restore procedure, deterministic
replay gate, evaluator lookup A/B, and the two-role QA comparison are documented
in [docs/KNOWLEDGE_BUNDLE_MIGRATION_EVALUATION.md](docs/KNOWLEDGE_BUNDLE_MIGRATION_EVALUATION.md).
The latest run found `runtime_equivalent_but_model_variance_observed`: replay and
selector parity passed, and both 10-question QA roles completed without an
exception. This diagnostic does not replace the 80-question development gate.

## M6 benchmark record and current milestone status

按用户当前验收决定，M6 视为达标。120-question Gold dataset 已人工审核，
`validate --official` succeeds；下面的首次 80-question development run（Recall@10
`0.45`、intent accuracy `0.80`）仅作为历史质量基线保留，不改写当前验收口径。

当前状态统一为：M7 P0 已实现并验证；M7 整体尚未通过（M7 P1 与四道真实 smoke
尚未完成）；M8 尚未开始。这里不虚构 hidden acceptance 或尚未运行的 formal gate。

```powershell
..\.venv\Scripts\panda-qa-eval.exe validate
..\.venv\Scripts\panda-qa-eval.exe validate --official
```

The first command validates schema, exact distributions, and every Gold selector
against the locked normalized objects. The second command additionally requires
human approval for every question and now succeeds. Review rules remain recorded
in [evaluation/GOLD_REVIEW_GUIDE.md](evaluation/GOLD_REVIEW_GUIDE.md).
