# H0 Holdout Corpus Preflight

## Scope

This is a static environment-readiness record for H0 on a new holdout device.
It contains no PANDA Agent outcomes and creates no real holdout content.

The locally present PANDA Knowledge Bundle Prototype v2.0.0 is a derived
artifact and is **not** authoritative for holdout curation. Holdout curation
must use the locked source corpus declared by
`data/manifests/source_manifest.json`.

## Repository snapshots

| Repository ID | Expected commit | Local availability | Exact-commit status | Path portability state |
|---|---|---|---|---|
| `luminosityfit` | `ddd83dcd1a74093bf48ef259a2849a67f9413f32` | PASS | PASS | STALE_ABSOLUTE_PATH_ONLY |
| `pandaroot` | `18c09e91100db27867ded30e708b4dae95bd8357` | PASS | PASS | STALE_ABSOLUTE_PATH_ONLY |
| `restgas_determination` | `11f1edc49dcbaeb61d707491a6d3bbec390fcd42` | PASS | PASS | STALE_ABSOLUTE_PATH_ONLY |

Each repository is present in the canonical repository-relative corpus
layout, has the intended origin URL, is detached at the exact manifest commit,
and has no untracked files. The restored working trees report tracked changes
caused solely by cross-platform line-ending representation: every repository
matches its commit when end-of-line whitespace is ignored. No newer branch tip
is substituted for a locked commit.

The manifest repository paths are absolute Windows paths from the old device
and are unusable on this device. Because the correct snapshots are locally
present at the exact commits, this is classified as
`STALE_ABSOLUTE_PATH_ONLY`, not `CORPUS_MISSING` or
`CORPUS_VERSION_MISMATCH`.

## Papers

| Document ID | Expected local file | Expected pages | Availability | Page-count status |
|---|---|---:|---|---|
| `li_2026` | `raw_pdf/thesis.pdf` | 164 | PASS | PASS (164) |
| `karavdina_2015` | `raw_pdf/Diss_2015_Karavdina_Anastasia.pdf` | 239 | PASS | PASS (239) |
| `pflueger_2017` | `raw_pdf/Diss_2017_Pflueger_Stefan.pdf` | 182 | PASS | PASS (182) |

All three files open as PDFs and match the manifest page counts. No new file
hashes were generated.

## Web snapshot

| Snapshot ID | Expected recorded size | Local availability | Snapshot status |
|---|---|---|---|
| `pandaroot_sphinx_2023_08_25_dev` | 75 pages, 118 assets | PASS | PASS |

All 193 manifest records are present under the locked local snapshot root:
75 HTML pages and 118 assets. No live website was used and no snapshot was
downloaded.

## Frozen static definitions

Static definition inspection, performed without outcome material, found:

- Gold: 120 questions, benchmark `m6-benchmark-v2.6`;
- `novel_dev`: dataset `0.3.0`, benchmark
  `novel-v1-dev-0.3.0`, identity `novel-v1-dev-expansion`, status `COMPLETE`,
  28 questions, 28 independent families, 28 approved, and 28
  `split_frozen` records;
- `novel_validation`: dataset `0.2.0`, benchmark
  `novel-v1-validation-0.2.0`, identity
  `novel-v1-validation-expansion`, status `COMPLETE`, 15 questions, 15
  independent families, 15 approved, and 15 `split_frozen` records.

The definitions match the H0 frozen-baseline precondition. Their runtime
outcomes were not inspected.

## Static validator portability blocker

The default existing static validator was invoked after the corpus became
available. It failed with 40 repository-path errors across all three
repository IDs. The validator constructs each repository root directly as
`Path(item["path"])` from `source_manifest.json`; on this device those values
are the unusable old-device absolute Windows paths. Representative paths
reported missing by the validator are present beneath the canonical local
snapshots, confirming that this is path resolution failure rather than corpus
absence.

Affected repository IDs:

- `luminosityfit`;
- `pandaroot`;
- `restgas_determination`.

The novel-validation validator was not run after the default validator
established the shared portability blocker. H0 does not rewrite the source
manifest, change validator semantics, or add a machine-specific workaround.

## Overall verdict

**INCONCLUSIVE — LOCKED CORPUS PRESENT / SOURCE-PATH PORTABILITY REPAIR REQUIRED**

Under the H0 stop condition, the governance plan, frozen-family collision
reference, and sanitized worker handoff were not created. Authorize and
complete the narrowly scoped H0-P portable locked-source path resolution task
before resuming H0. H1 is not eligible to start.

## H0-P resolution addendum

The original H0 blocker was `STALE_ABSOLUTE_PATH_ONLY`. H0-P added the shared
`resolve_manifest_repository_path()` resolver in `src/panda_agent/source.py`
and updated both source-manifest verification and the Novel static curation
validator to use it. Resolution now prefers the canonical local snapshot at
`data/sources/repos/<repo_id>/<commit_sha>/`; a manifest path is accepted only
as a compatibility fallback when it resolves within this project's repository
source root. Repository-identity traversal and external manifest paths are
rejected.

The source manifest is unchanged. Repository IDs, URLs, refs, commit SHAs,
paper identities, the Sphinx identity, and the locked-source universe are
unchanged. All three canonical local repository snapshots resolve
successfully.

Static validation after H0-P:

- resolver unit tests: PASS (8 tests);
- `novel_dev` static validator: PASS (28 questions, 28 independent families);
- `novel_validation` static validator: PASS (15 questions, 15 independent
  families);
- stale repository-path errors: 0;
- unresolved opaque selectors reported by each validator: 0.

The restored repository worktrees still exhibit cross-platform line-ending
differences under generic Git dirty-worktree inspection. H0-P did not alter or
weaken that independent integrity behavior. This is a separate, nonblocking
EOL note for the Novel curation validators.

**H0-P verdict: PASS — PORTABLE LOCKED-SOURCE PATH RESOLUTION COMPLETE**

This addendum does not mark full H0 as PASS. H0 governance artifacts remain
uncreated and require a separately resumed H0 task.

## Contamination and runtime accounting

- Real holdout questions created: 0
- Real Gold annotations created: 0
- Actual holdout families created: 0
- `novel_holdout.yaml` created: NO
- Novel-dev outcomes inspected: 0
- Novel-validation outcomes inspected: 0
- C8 outcomes inspected: 0
- Holdout outcomes inspected: 0
- Agent-selected evidence used: 0
- PANDA retrieval calls: 0
- QA calls: 0
- Judge calls: 0
- Vertex calls: 0
- Embedding calls: 0
- Qdrant calls: 0
- SQL retrieval calls: 0
