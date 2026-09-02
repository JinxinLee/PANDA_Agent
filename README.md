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
panda-qa-ui --project-root (Get-Location)
```

After the Bundle has been restored and registered once, `panda-qa-ui` is the one-command
launcher: it starts the `postgres` and `qdrant` Compose services, verifies the registered
runtime, opens the browser, and serves the UI on `127.0.0.1:8000`. Press `Ctrl+C` to stop
the UI server; the two data services remain running. Use `--no-browser` for a headless
terminal. `panda-qa-api` remains available when dependency startup and browser opening
should be managed separately.

`panda-qa-api` and `panda-qa-ui` both listen on loopback `127.0.0.1:8000` with one Uvicorn worker.
M8 P0 also provides a server-rendered UI at
`http://127.0.0.1:8000/ui`. It uses the same process and `QAService` as the
JSON API; it does not parse, embed, index, or maintain a separate conversation
history. Open that URL in a browser, enter a question, and submit it. The
question is trimmed and must be 1–10,000 characters. The JSON API remains
available for scripts:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/v1/qa -Method Post `
  -ContentType 'application/json' -Body (@{question='How is event_poca used?'} | ConvertTo-Json)
```

The migration, registration receipt, route/error contract, and P0 boundary are
documented in [docs/M7_P0_IMPLEMENTATION.md](docs/M7_P0_IMPLEMENTATION.md).
M7 P1 is implemented and deterministically verified; its deadline/504,
timings/usage, JSON logging, readiness TTL, configuration and debugging contract
are in [docs/M7_P1_IMPLEMENTATION.md](docs/M7_P1_IMPLEMENTATION.md). The four real
API smoke cases have passed, so **M7 overall PASS**. M8 P0/P1 are implemented and
deterministically verified; **M8 overall PASS and M8 complete**. See the
[M8 P0 record](docs/M8_P0_IMPLEMENTATION.md), [M8 P1 record](docs/M8_P1_IMPLEMENTATION.md)
and [M8 overall result](docs/M8_OVERALL_RESULT.md).

The P1 defaults are `PANDA_QA_DEADLINE_SECONDS=300`,
`PANDA_READINESS_TTL_SECONDS=5` (`0` disables the readiness cache), and
`PANDA_LOG_LEVEL=INFO`. A deadline returns HTTP 504 `deadline_exceeded`; Python
threads are not forcibly cancelled, so the process gate remains held until the
worker exits and cleanup writes only timings/usage/trace fields.

M8 exposes `/` (redirect), `/ui`, `/ui/qa`, `/ui/health` and
`/v1/qa/diagnose` in addition to the JSON API. The UI uses local Jinja2 and
HTMX 2.0.7, calls the shared `QAService` once per question, and renders five
diagnostic tabs plus Copy answer and Download JSON actions. It remains
loopback-only; Jinja2 autoescape, same-origin checks, CSP and HTTPS-only
external evidence links are enforced. The real Edge E2E is deterministic and
uses a fake service; the Vertex/`qa_runs` eight-intent smoke is reproducible but
opt-in via `PANDA_RUN_LIVE_M8_UI=1` (and optional `PANDA_M8_LIVE_CASE_IDS`) because
it sends the question/locked snippets to Vertex and writes `qa_runs`.

For a source-building workflow (which performs network crawling and indexing),
inspect the existing commands in [QA_AGENT.md](QA_AGENT.md) after the Bundle
quickstart. If an index process was interrupted, inspect `ingestion_runs` and
resume it:

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.index resume --run-id <RUN_ID>
```

The health check uses Application Default Credentials and the
`QA_GCP_PROJECT_ID`/`QA_VERTEX_LOCATION` values. Runtime generation and evaluation
judge models must be configured via `QA_GENERATION_MODEL_ID` and `QA_EVALUATION_JUDGE_MODEL_ID`
(recommended values in `.env.example`). Embedding models can be customized with `QA_EMBEDDING_MODEL_ID`;
the fixed embedding contract requires `QA_EMBEDDING_DIMENSIONS=3072`.

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

当前状态统一为：M7 P0+P1 已实现并完成确定性验证，四道真实 API smoke 已通过，
因此 **M7 overall PASS**；M8 P0/P1 已实现并完成确定性验证，真实 Edge E2E 与经授权
的八意图 UI smoke 已通过，因此 **M8 overall PASS，M8 complete**。这里不把本机 loopback
能力扩展为多轮、账户、远程、上传、Coding/Debug Agent 或公开部署。完整 M8 证据见
[M8 overall 验收结果](docs/M8_OVERALL_RESULT.md)，实现细节见
[M8 P0](docs/M8_P0_IMPLEMENTATION.md) 与 [M8 P1](docs/M8_P1_IMPLEMENTATION.md)。

```powershell
..\.venv\Scripts\panda-qa-eval.exe validate
..\.venv\Scripts\panda-qa-eval.exe validate --official
```

The first command validates schema, exact distributions, and every Gold selector
against the locked normalized objects. The second command additionally requires
human approval for every question and now succeeds. Review rules remain recorded
in [evaluation/GOLD_REVIEW_GUIDE.md](evaluation/GOLD_REVIEW_GUIDE.md).
