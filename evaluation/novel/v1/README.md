# Novel Dataset v1 — full novel_dev frozen

This directory contains the complete frozen `novel_dev` split: 28 loaded
records in 28 independent families. The original 16-question N1 pilot
(`n001`-`n010`, `n014`-`n019`) remains preserved, and N2-A plus N2-B provide
the 12 approved expansion records (`n020`-`n031`). All 28 active records are
human-approved and `split_frozen`.

Retired drafts n011/nf011, n012/nf012, and n013/nf013 remain historical
withdrawn records; their lineage is preserved and they are not active.

State:

- Dataset: `0.3.0` / `novel-v1-dev-0.3.0`, identity
  `novel-v1-dev-expansion`, status `COMPLETE`.
- Loaded records: 28. Human-approved: 28. Split-frozen: 28. Rejected: 0.
- N1: `PASS / COMPLETE`; N2: `PASS / COMPLETE`; N2-A: `COMPLETE`;
  N2-B: `COMPLETE` (`6 ACCEPT / 0 REVISE / 0 REJECT / 0 PENDING`).
- Representativeness: 26 `representative`, 2 `exploratory`. These are
  classification outcomes, not quota fulfillment or empirical user-frequency
  claims.
- `release_eligible: false`. Freezing `novel_dev` does not complete the full
  generalization or release program.
- `novel_validation`: not started. `novel_holdout`: not created and remains
  externally managed.
- No PANDA Agent retrieval, QA, judge, runtime evaluation, or novel
  evaluation has run for this curation. Any future novel measurement requires
  separate explicit authorization.

Files:

- `novel_dev.yaml` — evaluator-compatible, frozen 28-question Gold dataset.
- `curation_metadata.yaml` — curation sidecar (schema v3) with family,
  novelty, representativeness, coverage, provenance, and frozen lifecycle.
- `coverage_report.json` — structural coverage and final curation provenance;
  proposal-only coverage targets remain descriptive, not quotas.
- `manifest.json` — final dataset identity, review state, frozen count, and
  retired-draft lineage.
- `N2_FINALIZATION_REPORT.md` — authoritative N2 finalization and freeze
  closeout.
- `N2_FULL_NOVEL_DEV_EXPANSION_PLAN.md` — approved N2 plan with final
  execution status; historical planning rationale is preserved.
- `N2A_BATCH1_REVIEW_PACKAGE.md` — Batch 1 review history and final frozen
  state.
- `N2B_BATCH2_REVIEW_PACKAGE.md` — Batch 2 first review, R1 corrections,
  final re-review, and frozen state.
- `N1_FINALIZATION_REPORT.md` — historical N1 pilot review and freeze record.
- `gold_representativeness_profile.json` — analysis-only benchmark reference
  proxy; it makes no system-performance claim.

Governance: `docs/NOVEL_DATASET_CURATION_CONTRACT.md`. Static validation:
`python evaluation/scripts/validate_novel_curation.py`; it reproduces the
Gold minimum-source-scope, topology, and difficulty assignments from source
selectors and static provenance.
