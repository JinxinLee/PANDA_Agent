# Novel Dataset v1 — N1 pilot (draft)

This directory holds the N1 pilot curation package: 16 candidate `novel_dev`
questions (`n001`-`n016`), one per independent curation family (`nf001`-`nf016`).

Status: **candidate package ready for human review**. It is not frozen Gold.
Every question carries `review_status: draft` with no reviewer, and
`release_eligible` is false. Nothing here has been evaluated against PANDA
Agent: no retrieval, QA, judge, or runtime evaluation was run during curation.

Files:

- `novel_dev.yaml` — evaluator-compatible draft dataset (strict Gold schema).
- `curation_metadata.yaml` — curation sidecar (schema v3): family, novelty,
  overlap, representativeness (two-signal: benchmark reference fit + domain
  relevance), coverage, origin, and lifecycle per question.
- `coverage_report.json` — pilot coverage counts, novelty gaps,
  representativeness classification, and proposed (not frozen) targets for
  the future full `novel_dev`.
- `N1_REVIEW_PACKAGE.md` — per-question human review package (initial draft
  QA).
- `N1R_REPRESENTATIVENESS_REVIEW.md` — N1-R representativeness recalibration
  (historical record; superseded by the N1-R1 correction).
- `N1R1_PROFILE_CORRECTION.md` — N1-R1 methodological correction: benchmark
  reference proxy semantics, task-archetype/answerability orthogonalization,
  and minimum-required source scope; corrected candidate reassessment.
- `gold_representativeness_profile.json` — machine-readable analysis of the
  120 exposed Gold questions (schema v2 benchmark reference proxy: task
  archetypes, answerability classes, minimum-required source scope;
  analysis-only, no system performance).
- `manifest.json` — minimal dataset identity.

Governance: `docs/NOVEL_DATASET_CURATION_CONTRACT.md`. Static validation:
`python evaluation/scripts/validate_novel_curation.py`.
