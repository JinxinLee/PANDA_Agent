# PANDA Research QA Agent

This directory contains the version-aware, evidence-grounded QA system for the
LuminosityFit, PandaRoot, and RestgasDetermination research software corpus.

The implementation and decision log is maintained in [QA_AGENT.md](QA_AGENT.md).
The three source PDFs remain in `raw_pdf/`; locked repositories and web snapshots
are acquired under ignored `data/sources/` paths. See `QA_AGENT.md` for exact
commits, hashes, architecture decisions, commands, and verified results.

## Quick start

From the `Agent_learn` workspace root:

```powershell
Set-Location .\PANDA_Agent
..\.venv\Scripts\python.exe -m pip install -e ".[qa,ingestion,dev]"
docker compose up -d --wait
..\.venv\Scripts\alembic.exe upgrade head
..\.venv\Scripts\python.exe -m panda_agent.cli.source verify
..\.venv\Scripts\python.exe -m panda_agent.cli.index plan
..\.venv\Scripts\python.exe -m panda_agent.cli.index apply
..\.venv\Scripts\python.exe -m panda_agent.cli.index verify
..\.venv\Scripts\python.exe -m panda_agent.cli.qa ask "How is event_poca used?"
```

If an index process was interrupted, inspect `ingestion_runs` and resume it:

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.index resume --run-id <RUN_ID>
```

The health check uses Application Default Credentials and the existing
`GCP_PROJECT_ID`/`GCP_LOCATION` values. Model IDs can be overridden with
`QA_GENERATION_MODEL_ID` and `QA_EMBEDDING_MODEL_ID`.
The current index contract also requires `QA_EMBEDDING_DIMENSIONS=3072`.

## M6 benchmark gate

The 120-question Gold dataset has been human-reviewed and all 120 questions are
approved. `validate --official` succeeds. The first 80-question development
retrieval run is retained as a failed quality baseline (Recall@10 `0.45`, intent
accuracy `0.80`), so M6 has not passed and M7/M8 remain gated while retrieval is
being corrected and rerun.

```powershell
..\.venv\Scripts\panda-qa-eval.exe validate
..\.venv\Scripts\panda-qa-eval.exe validate --official
```

The first command validates schema, exact distributions, and every Gold selector
against the locked normalized objects. The second command additionally requires
human approval for every question and now succeeds. Review rules remain recorded
in [evaluation/GOLD_REVIEW_GUIDE.md](evaluation/GOLD_REVIEW_GUIDE.md).
