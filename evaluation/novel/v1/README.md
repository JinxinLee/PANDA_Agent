# Novel Dataset v1 — frozen novel_dev and reviewed validation pilot

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
- `novel_holdout`: not created and remains externally managed.
- No PANDA Agent retrieval, QA, judge, runtime evaluation, or novel
  evaluation has run for this curation. Any future novel measurement requires
  separate explicit authorization.

## novel_validation pilot

N3 adds a separate validation-only pilot without changing the frozen
`novel_dev` artifacts:

- Dataset: `0.1.0` / `novel-v1-validation-0.1.0`, identity
  `novel-v1-validation-pilot`, status `PILOT_IN_PROGRESS`.
- Pilot size: 6 candidates (`n901`-`n906`) in 6 independent validation
  families (`vf001`-`vf006`). The reserved high ID range is the smallest
  dedicated namespace compatible with the current strict `g###`/`n###` Gold
  schema; it is not a continuation at `n032`.
- N3 state: `PILOT_HUMAN_REVIEWED / R1_RE_REVIEW_PENDING`.
- Human review by `Li` at `2026-08-25T23:18+02:00`: 4 ACCEPT
  (`n901`, `n902`, `n903`, `n906`) and 2 REVISE (`n904`, `n905`). The two
  corrected records remain draft pending explicit human re-review.
- Human-approved: 4. Revise: 2. Rejected: 0. Pending: 0. Split-frozen: 0.
  Release eligible: false.
- The pilot is not the full approximately 12-18 question validation split.
  Its questions and Gold are visible for curation and review, but validation
  system outcomes have not been observed and may not be measured before a
  later complete split freeze and explicit authorization.
- All candidates are statically source-anchored and family-isolated against
  all 28 frozen `novel_dev` families. No holdout content was created.

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
- `novel_validation.yaml` — evaluator-compatible six-question validation
  pilot; four records are human-approved and two corrected records remain
  draft pending re-review.
- `novel_validation_curation_metadata.yaml` — validation-only curation
  sidecar with `vf###` family isolation; four lifecycles are `approved` and
  two remain `draft` pending re-review.
- `novel_validation_manifest.json` and
  `novel_validation_coverage_report.json` — pilot-only counts and structural
  coverage; no performance claim.
- `N3_NOVEL_VALIDATION_CURATION_PLAN.md` — N3 role, sampling, isolation,
  support audit, freeze order, and stop boundary.
- `N3_VALIDATION_PILOT_REVIEW_PACKAGE.md` — authoritative first human-review
  decisions, R1 evidence-contract corrections, and advisory Codex
  recommendations. Human re-review remains pending for n904 and n905.

Governance: `docs/NOVEL_DATASET_CURATION_CONTRACT.md`. Static validation:
`python evaluation/scripts/validate_novel_curation.py`; it reproduces the
Gold minimum-source-scope, topology, and difficulty assignments from source
selectors and static provenance. Validate the separate pilot with the same
script's `--dataset`, `--sidecar`, `--coverage`, `--manifest`, and
`--expected-split novel_validation` arguments documented in the script.
