# Novel Dataset v1 — N1 pilot (draft)

This directory holds the revised N1 pilot curation package: 16 active candidate
`novel_dev` questions (`n001`-`n012`, `n014`-`n017`), one per independent
active curation family. Draft n013/nf013 was withdrawn and replaced by
n017/nf017; its history is retained in the review documents.

Status: **REVISED_PILOT_READY_FOR_HUMAN_REVIEW**. It is not frozen Gold.
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
  history; superseded for current review).
- `N1R_REPRESENTATIVENESS_REVIEW.md` — N1-R representativeness recalibration
  (historical record; superseded by the N1-R1 correction).
- `N1R1_PROFILE_CORRECTION.md` — N1-R1 methodological correction: benchmark
  reference proxy semantics, task-archetype/answerability orthogonalization,
  and minimum-required source scope; corrected candidate reassessment.
- `N1R2_REVIEW_PACKAGE.md` — current repaired-candidate human review package,
  including the n013 withdrawal and independently sampled n017 replacement.
- `gold_representativeness_profile.json` — machine-readable analysis of the
  120 exposed Gold questions (schema v2 benchmark reference proxy: task
  archetypes, answerability classes, minimum-required source scope;
  analysis-only, no system performance).
- `manifest.json` — minimal dataset identity.

Governance: `docs/NOVEL_DATASET_CURATION_CONTRACT.md`. Static validation:
`python evaluation/scripts/validate_novel_curation.py`; it also reproduces all
120 Gold minimum-source-scope, topology, and difficulty assignments from source
selectors and static provenance.
