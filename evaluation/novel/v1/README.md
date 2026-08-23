# Novel Dataset v1 — N1 pilot (draft)

This directory holds the human-reviewed N1 pilot curation package: 16
active candidate `novel_dev` questions (`n001`-`n010`, `n014`-`n019`), one per
independent active curation family. Drafts n011/nf011, n012/nf012, and
n013/nf013 are withdrawn; their histories are retained in the review documents.

Status: **REVISION_REQUIRED_AFTER_HUMAN_REVIEW**. It is not frozen Gold.
Human reviewer `Li` accepted 14 questions and requested revisions to n002 and
n008. The requested corrections are applied, but those two records remain
`review_status: draft` pending explicit human re-acceptance; the other 14 are
`approved`. No record is `split_frozen`, `release_eligible` remains false, and
nothing here has been evaluated against PANDA Agent: no retrieval, QA, judge, or
runtime evaluation was run during curation or review.

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
- `N1R2_REVIEW_PACKAGE.md` — historical repaired-candidate review package,
  including the n013 withdrawal and independently sampled n017 replacement.
- `N1R2R1_REVIEW_PACKAGE.md` — final governance cleanup history, including
  factual corrections, withdrawn-draft lineage, and independent n019 sampling
  evidence.
- `N1_FINAL_HUMAN_REVIEW.md` — current per-item decision matrix for final human
  review; it records 14 ACCEPT and 2 REVISE decisions from reviewer `Li`.
- `N1_FINALIZATION_REPORT.md` — human decision record, applied amendment
  summary, counts, and the explicit non-freeze outcome.
- `gold_representativeness_profile.json` — machine-readable analysis of the
  120 exposed Gold questions (schema v2 benchmark reference proxy: task
  archetypes, answerability classes, minimum-required source scope;
  analysis-only, no system performance).
- `manifest.json` — minimal dataset identity.

Governance: `docs/NOVEL_DATASET_CURATION_CONTRACT.md`. Static validation:
`python evaluation/scripts/validate_novel_curation.py`; it also reproduces all
120 Gold minimum-source-scope, topology, and difficulty assignments from source
selectors and static provenance.
