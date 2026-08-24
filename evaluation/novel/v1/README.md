# Novel Dataset v1 — N1 pilot frozen; N2-A expansion in progress

This directory holds the frozen N1 pilot plus the N2-A Batch 1 expansion
records: 22 loaded `novel_dev` records in 22 independent families — the 16
human-approved, `split_frozen` N1 questions (`n001`-`n010`, `n014`-`n019`)
and 6 Batch 1 expansion candidates (`n020`-`n025`).
Retired drafts n011/nf011, n012/nf012, and n013/nf013 remain historical
withdrawn records; their lineage is preserved in the review documents.

State:

- Loaded records: 22. Human-approved: 22 — the 16 frozen N1 questions plus
  the 6 Batch 1 expansion records (n020/n024/n025 accepted
  2026-08-24T01:50+02:00; corrected n021/n022/n023 accepted on re-review
  2026-08-24T02:05+02:00; all lifecycle `approved`).
- Frozen: 16 (only the original N1 pilot; the 6 approved expansion records
  are NOT yet `split_frozen`).
- N1: `PASS / COMPLETE`; N2: `IN_PROGRESS / PLAN_APPROVED`; N2-A:
  `BATCH1_APPROVED / NOT_SPLIT_FROZEN` (6 ACCEPT / 0 REVISE / 0 REJECT /
  0 PENDING).
- Dataset lineage: `0.3.0` expansion-in-progress (`novel-v1-dev-0.3.0`,
  identity `novel-v1-dev-expansion`, status `EXPANSION_IN_PROGRESS`).
  Git history preserves the frozen `0.2.0` pilot baseline; the original 16
  questions are content-identical and remain approved/frozen.
- `release_eligible: false`. The expanded `novel_dev` is NOT frozen and is
  NOT the complete ~30-question dataset; Batch 2 and freeze are future work.
- Nothing here has been evaluated against PANDA Agent: no retrieval, QA,
  judge, or runtime evaluation was run during curation, review,
  finalization, or expansion.

Files:

- `novel_dev.yaml` — evaluator-compatible dataset (strict Gold schema); the
  16 frozen pilot questions plus the 6 human-approved Batch 1 expansion
  records.
- `curation_metadata.yaml` — curation sidecar (schema v3): family, novelty,
  overlap, representativeness (two-signal: benchmark reference fit + domain
  relevance), coverage, origin, and lifecycle per question (Batch 1
  lifecycles `approved`, not yet `split_frozen`).
- `coverage_report.json` — coverage counts over all 22 loaded records,
  novelty/representativeness gaps, expansion-in-progress status, and the
  proposal-only (not frozen) targets for the future full `novel_dev`.
- `N2_FULL_NOVEL_DEV_EXPANSION_PLAN.md` — human-approved (Rev 1) expansion
  plan: corpus-support audit, soft targets, sampling protocol, batching,
  versioning, freeze criteria.
- `N2A_BATCH1_REVIEW_PACKAGE.md` — human-review artifact for the Batch 1
  candidates: first-review decisions (3 ACCEPT / 3 REVISE, reviewer `Li`,
  2026-08-24T01:50+02:00), R1 correction records, and the re-review
  acceptance of the corrected candidates (6 ACCEPT final total, reviewer
  `Li`, 2026-08-24T02:05+02:00).
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
- `N1_FINAL_HUMAN_REVIEW.md` — per-item human decision matrix for the frozen
  pilot: 16 ACCEPT after the initial review (14 ACCEPT / 2 REVISE) and
  reviewer `Li`'s re-review acceptance of the corrected n002 and n008.
- `N1_FINALIZATION_REPORT.md` — initial human decision record, the re-review
  and finalization record, freeze state, and dataset version transition.
- `gold_representativeness_profile.json` — machine-readable analysis of the
  120 exposed Gold questions (schema v2 benchmark reference proxy: task
  archetypes, answerability classes, minimum-required source scope;
  analysis-only, no system performance).
- `manifest.json` — dataset identity and expansion-in-progress review state.

Governance: `docs/NOVEL_DATASET_CURATION_CONTRACT.md`. Static validation:
`python evaluation/scripts/validate_novel_curation.py`; it also reproduces all
120 Gold minimum-source-scope, topology, and difficulty assignments from source
selectors and static provenance.
