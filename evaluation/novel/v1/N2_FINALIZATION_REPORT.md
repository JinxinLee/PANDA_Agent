# N2 Finalization Report

## Final verdict

N2: **PASS / COMPLETE**

## Dataset identity

dataset_version: `0.3.0`

benchmark_version: `novel-v1-dev-0.3.0`

dataset_identity: `novel-v1-dev-expansion`

split: `novel_dev`

status: `COMPLETE`

## Final counts

- Loaded: 28
- Independent families: 28
- Human-approved: 28
- Split-frozen: 28
- Rejected active records: 0
- Representative: 26
- Exploratory: 2

Retired historical drafts remain inactive: `n011`/`nf011`, `n012`/`nf012`,
and `n013`/`nf013`.

The representative/exploratory values are classification outcomes, not quota
fulfillment or empirical user-distribution claims.

## Human review history

- N1: 16 frozen pilot questions, including the accepted n002/n008 re-review.
- N2-A: 6 Batch 1 records accepted by Li; their historical first-review and
  re-review timestamps remain unchanged.
- N2-B first review: 1 ACCEPT / 5 REVISE / 0 REJECT / 0 PENDING at
  `2026-08-24T02:42+02:00`; n027 was accepted.
- N2-B R1: corrections were applied to n026, n028, n029, n030, and n031;
  their semantic content remained unchanged during finalization.
- N2-B final re-review: Li accepted n026, n028, n029, n030, and n031 at
  `2026-08-25T22:11:57+02:00`.
- Final Batch 2: 6 ACCEPT / 0 REVISE / 0 REJECT / 0 PENDING.

## Freeze boundary

Before this task, 16 active records were `split_frozen` and the 12 N2
expansion records were approved or corrected drafts. After this task, n020-
n031 are all `split_frozen`, and all 28 active novel_dev records are both
human-approved and `split_frozen`.

The 28-question `novel_dev` 0.3.0 is now immutable measurement data. Future
semantic edits require the curation contract's post-freeze amendment and
versioning rules; ordinary evaluation must not mutate this split.

## Coverage

The final structural profile is: intents installation 2, usage 9, api 3,
algorithm_theory 3, algorithm_implementation 5, data_flow 2,
module_structure 2, and troubleshooting 2; expected statuses are 27
`answered` and 1 `insufficient_evidence`. Evidence topology is 14
`single_hop`, 6 `multi_hop`, 5 `comparison`, and 3 `producer_consumer`.
Repository scope is 25 `single_repository`, 1 `cross_repository`, and 2
`paper_only`. These are structural curation facts, not performance results.

## Contamination boundary

- No novel PANDA Agent outcome was observed before freeze.
- No Agent-selected evidence was used for Gold.
- C8 development occurred in parallel, but no C8 outcome informed candidate
  selection, correction, or finalization.
- No novel evaluation was run during N2.

## Remaining dataset work

novel_validation: **NOT STARTED**

novel_holdout: **NOT CREATED / EXTERNALLY MANAGED**

## Evaluation authorization

Novel evaluation: **NOT AUTHORIZED BY THIS FREEZE TASK**. A separate explicit
user authorization is required.

## C8

The current authoritative C8 lifecycle at finalization is preserved without
outcome interpretation: `C8-A1R1 PASS`, `C8-A1
PASS_AFTER_CONTRACT_FIDELITY_REPAIR`, and `C8-A2 NEXT_ELIGIBLE /
NOT_STARTED`. No C8 files are included in the N2-F change.

## Finalization commit

The finalization commit SHA is recorded in the task completion report. No
per-file hashes or integrity manifests are created.
