# PANDA Knowledge Bundle Prototype

Status: **live acceptance PASS (2026-08-09, round2).** The four local bundle
commands completed a real `export -> inspect -> isolated restore -> verify`
run, followed by all three fixed QA smoke questions. This is a local prototype
acceptance record only: it is not a public/release security gate, a signed
distribution, or an offline replacement for Vertex dense query embedding.

The schema-v2 runtime state is published as
[PANDA Knowledge Bundle Prototype v2.0.0](https://github.com/JinxinLee/PANDA_Agent/releases/tag/panda-kb-prototype-v2.0.0).
Its five assets contain the manifest, PostgreSQL dump, Qdrant snapshot,
portable BM25/evaluator assets, and SHA-256 checksums. The ZIP uses POSIX paths
and Unix directory permissions so it can be extracted directly on Windows,
macOS, and Linux. See [NEW_USER_BUNDLE_GUIDE.md](NEW_USER_BUNDLE_GUIDE.md) for
the exact download, hash-check, extraction, restore, and verification sequence.

This prototype is a trusted, local hand-off for one PANDA knowledge index. It
is intentionally small and explicit so that a maintainer can export a known
state and a user can restore it into a clean local target.

## Fixed target and contents

The prototype targets the PostgreSQL database `panda_qa` and the Qdrant
collection `panda_knowledge_v1`. An export directory contains:

- `bundle_manifest.json`, including the schema version, source-manifest hash,
  PostgreSQL state, Qdrant configuration/count, FastEmbed state, artifact
  hashes, and exactly 100 persisted verification samples;
- `postgres.dump`, a custom-format PostgreSQL dump of the knowledge tables
  (transient QA/ingestion data and embedding/relation-candidate data are not
  included as table data);
- `qdrant.snapshot`, a snapshot of the collection; and
- `runtime_assets/fastembed/bm25/`, the local English `Qdrant/bm25` runtime
  asset used for sparse retrieval.

Before writing an export, the implementation requires a passing current index
verification, no running ingestion run, the current Alembic head, a green
Qdrant collection, and 100 identity-matching sample points tied to the current
index model and dimensions. The Qdrant count is requested with the exact-count
API. An existing non-empty bundle directory is rejected.

### Recorded acceptance evidence

The accepted artifact and isolated restore are retained in the repository's
ignored temporary area:

- Bundle: `data/tmp/panda-kb-prototype-e2e-round2`.
- Schema: `panda-knowledge-bundle/v1`.
- Corpus source-manifest SHA-256:
  `9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94`.
- PostgreSQL `panda_qa`: revision `0004`; `source_versions=8`,
  `knowledge_objects=102875`, `knowledge_aliases=2`, `relation_edges=64561`,
  `workflow_steps=374`, `index_identities=1`; index fingerprint
  `c527bbf1d10c88969da02745d678c640a4544757258584110a5ddd7744be3cf2`.
- `postgres.dump`: `70,915,643` bytes, SHA-256
  `aadff5c1397317544160c6472d84e91994f7613466558116f589ef57bba21c64`.
- Qdrant `panda_knowledge_v1`: `80698` points; dense size `3072`, cosine;
  sparse `Qdrant/bm25`; `qdrant.snapshot`: `1,269,908,992` bytes, SHA-256
  `da592bb445f83d7ce7ee87e9e669831faa27b0f85942753719146bb81d1928c1`.
- The manifest persisted exactly `100` fixed cross-store identity samples.

The restore used the isolated Compose project `panda_bundle_restore_round2`
with PostgreSQL `127.0.0.1:55433` and Qdrant `127.0.0.1:6335`. The clean
target was `data/tmp/panda-kb-clean-runtime-round2`: `configs/`,
`data/manifests/source_manifest.json`, and `data/runtime/` are present, while
`data/normalized/`, `data/sources/`, and `raw_pdf/` are absent. In the restored database,
`ingestion_runs=0`, `embedding_records=0`, and `knowledge_objects=102875`.

`verify` returned `valid=true`, `sample_count=100`, and all `12` checks true.
The run used the true cross-store sample selection and QA database identifier
catalog fixes. No source parsing, document embedding, or indexing was run as
part of export, restore, verify, or this acceptance record; restore loaded the
PostgreSQL dump, Qdrant snapshot, and bundled BM25 runtime only.

Supporting candidate validation was recorded as full unit `138/138`, bundle
integration `4/4`, `compileall` pass, `pip check` pass, and `git diff --check`
pass. These are supporting code checks, not a claim that the prototype is a
public security or release gate.

The captured operation shape (from the `PANDA_Agent` checkout) was:

```powershell
$bundlePath = (Resolve-Path 'data/tmp/panda-kb-prototype-e2e-round2').Path
$restoreRoot = (Resolve-Path 'data/tmp/panda-kb-clean-runtime-round2').Path
..\.venv\Scripts\panda-qa-kb.exe export --bundle $bundlePath --project-root (Get-Location)
..\.venv\Scripts\panda-qa-kb.exe inspect --bundle $bundlePath

$env:PANDA_DATABASE_URL = 'postgresql://panda:panda@127.0.0.1:55433/panda_qa'
$env:PANDA_QDRANT_URL = 'http://127.0.0.1:6335'
docker compose -p panda_bundle_restore_round2 `
  -f tests/integration/docker-compose.bundle-restore.yml up -d --wait postgres qdrant
..\.venv\Scripts\panda-qa-kb.exe restore --bundle $bundlePath --project-root $restoreRoot
..\.venv\Scripts\panda-qa-kb.exe verify --bundle $bundlePath --project-root $restoreRoot
```

## Prerequisites

Run commands from the `PANDA_Agent` project directory with the project virtual
environment installed. The only service-start command in this prototype is:

```powershell
docker compose up -d --wait postgres qdrant
```

Do not run the bundle commands against a production or otherwise shared target.
Before restore, use a target whose PostgreSQL database has no
`knowledge_objects` table and whose fixed Qdrant collection is absent. The
destination `data/runtime/fastembed/bm25` directory must also be absent: the
implementation rejects it when the runtime is installed, after the store
restore steps, so checking it up front avoids a cross-store partial failure.

## Maintainer: export and inspect

Choose a new, empty bundle path. The path can be outside the repository; do
not reuse a directory containing an older bundle.

```powershell
$bundlePath = 'D:\panda-bundles\panda-kb-v1-YYYYMMDD'
..\.venv\Scripts\panda-qa-kb.exe export `
  --bundle $bundlePath `
  --project-root (Get-Location)
```

The command prints the JSON manifest after the PostgreSQL dump, Qdrant
snapshot, BM25 asset copy, and hash receipt have been written. A maintainer
should retain that output with the bundle. To re-check only the local receipt
and artifact/runtime presence:

```powershell
..\.venv\Scripts\panda-qa-kb.exe inspect `
  --bundle $bundlePath
```

`inspect` does not contact PostgreSQL, Qdrant, or Vertex; it checks the
manifest, dump/snapshot byte counts and SHA-256 hashes, and that the bundled
BM25 directory is non-empty.

## User: restore into a clean target

Use a disposable, clean `PANDA_Agent` checkout and start only the two services
shown above. Set `$bundlePath` to the maintainer's bundle, then preflight and
restore it:

```powershell
$bundlePath = 'D:\panda-bundles\panda-kb-v1-YYYYMMDD'
..\.venv\Scripts\panda-qa-kb.exe inspect `
  --bundle $bundlePath
..\.venv\Scripts\panda-qa-kb.exe restore `
  --bundle $bundlePath `
  --project-root (Get-Location)
```

`restore` validates both artifact hashes and the bundled BM25 asset before it
opens the target. It then checks the PostgreSQL/Qdrant emptiness precondition,
restores PostgreSQL in a single transaction with
`pg_restore --exit-on-error`, uploads the Qdrant snapshot, installs the local
BM25 asset, and writes
`data/runtime/installed_bundle.json`. The PostgreSQL and Qdrant operations are
not one cross-store transaction: if a later step fails, cleanup is manual in
this isolated prototype environment. There is no rollback or force option.

## Verify the restored target

Run verification from the same clean project after restore:

```powershell
..\.venv\Scripts\panda-qa-kb.exe verify `
  --bundle $bundlePath `
  --project-root (Get-Location)
```

The JSON result has a top-level `valid` value, a `checks` object, and
`sample_count`. A valid result requires all of the following to be true:

- PostgreSQL revision, selected-table counts, and index fingerprint match the
  manifest;
- Qdrant is green and its exact point count, dense/sparse configuration,
  payload indexes, and reported version match;
- the local FastEmbed state matches and a local-only BM25 query probe returns
  a non-empty vector; and
- all 100 persisted PostgreSQL/Qdrant identity samples match the manifest.

Verification is local-only. It does not call Vertex, does not use the
normalized corpus, and does not read the excluded `embedding_records` receipt.
The normal QA query path still uses Vertex for dense query embedding; restoring
the bundle does not make dense QA offline.

## Fixed QA smoke questions

The passed run used these exact three questions and recorded each JSON
answer/status with citations:

```text
How is event_poca used?
Where is PndPidCorrelator defined?
What inputs and outputs connect the target generator to the RestgasDetermination analysis?
```

Recorded smoke summaries:

| Question | Status | Evidence summary | `errors` |
|---|---|---|---|
| `How is event_poca used?` | `answered` | `POCA_VERTEX_FILE` hand-off, second-pass consumption, and GEANE citations | `[]` |
| `Where is PndPidCorrelator defined?` | `answered` | Locked PandaRoot `.h` and `.cxx` citations | `[]` |
| `What inputs and outputs connect the target generator to the RestgasDetermination analysis?` | `answered` | Density file → `ReadDensityFile`/`SampleInteractionVertex` → sim/digi/reco/POCA/correction/`rho_reco` citations | `[]` |

Run them through the ordinary QA CLI only when the target's Vertex
credentials/configuration are intentionally available:

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.qa ask 'How is event_poca used?'
..\.venv\Scripts\python.exe -m panda_agent.cli.qa ask 'Where is PndPidCorrelator defined?'
..\.venv\Scripts\python.exe -m panda_agent.cli.qa ask 'What inputs and outputs connect the target generator to the RestgasDetermination analysis?'
```

The smoke commands require the target's intentionally configured Vertex
credentials. They exercise the ordinary QA path; they do not turn the local
bundle into an offline dense-query service.

## Acceptance checklist

- [x] Work is performed in a named disposable test project, not production or
      the current/shared compose project.
- [x] The isolated services were started with
      `docker compose -p panda_bundle_restore_round2 -f tests/integration/docker-compose.bundle-restore.yml up -d --wait postgres qdrant`; the generic prototype shape is `docker compose up -d --wait postgres qdrant`.
- [x] Maintainer export completed from a passing index with no running
      ingestion, and `inspect` accepts the resulting manifest and hashes.
- [x] Restore was attempted only on a clean target and completed without a
      partial cross-store failure.
- [x] `verify` returned `valid: true`, `sample_count: 100`, and every check true.
- [x] All three fixed QA smoke questions were run with the intended Vertex
      configuration; answers have evidence/citations and no unsupported
      claims.
- [x] Command output, bundle path, and environment are recorded as live
      acceptance evidence in the round2 record above.

There is no routine cleanup command in this guide. A destructive
`docker compose down -v` is permitted only for an explicitly named disposable
test project (for example, `panda-kb-restore-smoke`); never use it on the
production or current/shared project.

## Explicit non-goals

This prototype does not provide signing, downloads, multiple-bundle selection,
rollback, a force-restore switch, or a public/release acceptance gate. It is a
local file hand-off with manual recovery for cross-store partial failure.
