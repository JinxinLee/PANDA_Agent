# Novel Dataset v1 — N1 pilot (human-reviewed and frozen)

This directory holds the finalized N1 pilot: 16 active `novel_dev` questions
(`n001`-`n010`, `n014`-`n019`), one per independent active curation family.
Retired drafts n011/nf011, n012/nf012, and n013/nf013 remain historical
withdrawn records; their lineage is preserved in the review documents.

State:

- Active: 16. Approved: 16 (reviewer `Li`; 14 accepted 2026-08-24T00:28:55+02:00,
  n002 and n008 accepted on re-review 2026-08-24T00:49:13+02:00 after their
  requested corrections).
- Frozen: 16 (all sidecar lifecycles `split_frozen`).
- N1: `PASS / COMPLETE`.
- Dataset version `0.2.0` (`novel-v1-dev-0.2.0`, identity `novel-v1-n1-pilot`).
- `release_eligible: false`.
- This is a frozen pilot, not the final ~30-question `novel_dev`; full
  `novel_dev` expansion is future work (N2).
- Nothing here has been evaluated against PANDA Agent: no retrieval, QA, judge,
  or runtime evaluation was run during curation, review, or finalization.

Files:

- `novel_dev.yaml` — evaluator-compatible frozen dataset (strict Gold schema).
- `curation_metadata.yaml` — curation sidecar (schema v3): family, novelty,
  overlap, representativeness (two-signal: benchmark reference fit + domain
  relevance), coverage, origin, and lifecycle per question.
- `coverage_report.json` — pilot coverage counts, novelty gaps,
  representativeness classification, and proposed (not frozen) targets for
  the future full `novel_dev`.
- `N1_REVIEW_PACKAGE.md` — per-question human review package (initial draft
  history; superseded for current review).
- `N1R_REPRESENTATIVENESS_REVIEW.md` — N1-R representativeness recalibration
  (historical record; superseded by the N1-R1 correction).
- `N1R1_PROFILE_CORRECTION.md` — N1-R1 methodological correction: benchmark
  reference proxy semantics, task-archetype/answerability orthogonalization,
  and minimum-required source scope; corrected candidate reassessment.
- `N1R2_REVIEW_PACKAGE.md` — historical repaired-candidate review package,
  including the n013 withdrawal and independently sampled n017 replacement.
- `N1R2R1_REVIEW_PACKAGE.md` — final governance cleanup history, including
  factual corrections, withdrawn-draft lineage, and independent n019 sampling
  evidence.
- `N1_FINAL_HUMAN_REVIEW.md` — per-item human decision matrix: 16 ACCEPT after
  the initial review (14 ACCEPT / 2 REVISE) and reviewer `Li`'s re-review
  acceptance of the corrected n002 and n008.
- `N1_FINALIZATION_REPORT.md` — initial human decision record, the re-review
  and finalization record, freeze state, and dataset version transition.
- `gold_representativeness_profile.json` — machine-readable analysis of the
  120 exposed Gold questions (schema v2 benchmark reference proxy: task
  archetypes, answerability classes, minimum-required source scope;
  analysis-only, no system performance).
- `manifest.json` — minimal dataset identity.

Governance: `docs/NOVEL_DATASET_CURATION_CONTRACT.md`. Static validation:
`python evaluation/scripts/validate_novel_curation.py`; it also reproduces all
120 Gold minimum-source-scope, topology, and difficulty assignments from source
selectors and static provenance.
