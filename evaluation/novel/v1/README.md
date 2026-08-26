# Novel Dataset v1 — frozen novel_dev and validation expansion

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

## novel_validation expansion

N3 created and froze a six-question validation pilot without changing the
frozen `novel_dev` artifacts. N3-E carried that pilot unchanged into the
active expansion, and N3-E2 adds the final small draft batch:

- Dataset: `0.2.0` / `novel-v1-validation-0.2.0`, identity
  `novel-v1-validation-expansion`, status `EXPANSION_IN_PROGRESS`.
- Frozen pilot: 6 records (`n901`-`n906`) in 6 independent families
  (`vf001`-`vf006`), all approved and `split_frozen`. Their Gold, review
  metadata, and sidecar lifecycles are carried forward unchanged.
- N3-E approved records: 6 records (`n907`-`n912`) in 6 independent families
  (`vf007`-`vf012`). Li accepted all six at `2026-08-26T15:36+02:00` from
  reviewed commit `fa902109123c17b92297c6839fd4664c659ff3c5`; lifecycle is
  `approved`, not `split_frozen`.
- N3-E2 drafts: 3 records (`n913`-`n915`) in 3 independent families
  (`vf013`-`vf015`), all `review_status: draft`, with no reviewer and sidecar
  lifecycle `draft`.
- Total: 15 loaded / 15 families / 12 approved / 3 pending / 6 frozen.
  Human approval is partial and release eligibility remains false.
- The reserved high ID range remains the smallest dedicated namespace
  compatible with the strict `g###`/`n###` Gold schema; it is not a
  continuation at `n032`.
- N3 state: `PASS / COMPLETE`; validation pilot: `COMPLETE / SPLIT_FROZEN`.
- Human review by `Li` at `2026-08-25T23:18+02:00`: 4 ACCEPT
  (`n901`, `n902`, `n903`, `n906`) and 2 REVISE (`n904`, `n905`). After R1
  corrections, Li accepted n904 and n905 on final re-review at
  `2026-08-26T00:21+02:00`.
- N3-E is `BATCH1_HUMAN_APPROVED`; N3-E2 is
  `EXPANSION2_CURATED / HUMAN_REVIEW_PENDING`. The authoritative target is
  approximately 15 questions as a quality target, not a quota. Reaching 15
  loaded records does not make full validation complete: new drafts require
  human review, any required correction and explicit re-review, and a
  separately authorized final freeze.
- All 15 records are statically source-anchored and family-isolated against
  all 28 frozen `novel_dev` families and all other validation families. No
  validation measurement or novel-dev measurement ran, and no holdout content
  was created or inspected.

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
- `novel_validation.yaml` — evaluator-compatible 15-question validation
  expansion: six frozen pilot records, six N3-E approved-not-frozen records,
  and three N3-E2 human-review-pending drafts.
- `novel_validation_curation_metadata.yaml` — validation-only curation
  sidecar with `vf###` family isolation and explicit frozen, approved, and
  draft lifecycle distinctions.
- `novel_validation_manifest.json` and
  `novel_validation_coverage_report.json` — expansion counts, structural
  coverage, frozen/draft distinction, and no performance claim.
- `N3E_FULL_VALIDATION_EXPANSION_PLAN.md` — N3-E baseline, version transition,
  support audit, isolation policy, and review/freeze stop boundary.
- `N3E_VALIDATION_EXPANSION_REVIEW_PACKAGE.md` — per-candidate Gold,
  representativeness, Gold-overlap, strict frozen-family isolation, advisory
  recommendation, and Li's authoritative six-ACCEPT review history.
- `N3E2_FINAL_VALIDATION_EXPANSION_PLAN.md` — authoritative approximately-15
  quality target, final small-batch audit, isolation method, and stop rule.
- `N3E2_VALIDATION_EXPANSION_REVIEW_PACKAGE.md` — n913-n915 evidence,
  Gold-overlap review, strict family isolation, recommendations, and pending
  human decisions.
- `N3_PILOT_FINALIZATION_REPORT.md` — final human re-review, pilot freeze
  boundary, and explicit full-validation limitation.
- `N3_NOVEL_VALIDATION_CURATION_PLAN.md` — N3 role, sampling, isolation,
  support audit, freeze order, and stop boundary.
- `N3_VALIDATION_PILOT_REVIEW_PACKAGE.md` — authoritative first human-review
  decisions, R1 evidence-contract corrections, final human re-review, and
  advisory Codex recommendations; all six records are split_frozen.
- Full validation: `NOT COMPLETE`; the next task is human review of the N3-E2
  candidates.
- Validation measurement: `NOT RUN`.

Governance: `docs/NOVEL_DATASET_CURATION_CONTRACT.md`. Static validation:
`python evaluation/scripts/validate_novel_curation.py`; it reproduces the
Gold minimum-source-scope, topology, and difficulty assignments from source
selectors and static provenance. Validate the separate pilot with the same
script's `--dataset`, `--sidecar`, `--coverage`, `--manifest`, and
`--expected-split novel_validation` arguments documented in the script.
