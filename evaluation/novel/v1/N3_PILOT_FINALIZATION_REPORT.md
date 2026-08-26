# N3 Validation Pilot Finalization Report

## Verdict

N3 validation pilot: **PASS / COMPLETE**

## Dataset identity

dataset_version: `0.1.0`

benchmark_version: `novel-v1-validation-0.1.0`

dataset_identity: `novel-v1-validation-pilot`

split: `novel_validation`

status: `PILOT_COMPLETE`

release_eligible: `false`

## Final pilot counts

- Loaded: 6
- Independent families: 6
- Human-approved: 6
- Split-frozen: 6
- Representative: 6
- Exploratory: 0

All six records (`n901`-`n906`, families `vf001`-`vf006`) retain their
accepted/corrected semantic content. No new question or family was added.

## Final human re-review

- Reviewer: Li
- Timestamp: `2026-08-26T00:21+02:00`
- Reviewed correction commit:
  `971a3d34abf92b89da2f2f13263b97313223ec35`
  (`apply N3 validation pilot review corrections`)
- n904: ACCEPT
- n905: ACCEPT
- Final pilot: 6 ACCEPT / 0 REVISE / 0 REJECT / 0 PENDING

## Review history

- Initial review by Li at `2026-08-25T23:18+02:00`: 4 ACCEPT / 2 REVISE / 0
  REJECT / 0 PENDING. Accepted records were n901, n902, n903, and n906;
  n904 and n905 were REVISE.
- N3-R1 corrected n904 and n905's Gold evidence annotations and selectors
  while preserving their information needs and semantic families; the
  resulting metadata changes were reviewed and accepted.
- Final re-review by Li at `2026-08-26T00:21+02:00`: n904 ACCEPT and n905
  ACCEPT.

## Freeze transition

Before N3-F:

- 4 approved
- 2 revise
- 0 split_frozen

After N3-F:

- 6 approved
- 0 revise
- 6 split_frozen

## Freeze boundary

After this commit, `n901`-`n906` are immutable pilot measurement data. Any
semantic change requires the curation contract's post-freeze amendment and
versioning rules. The freeze records the pilot only; it does not authorize
measurement or permit silent mutation during a later expansion.

## Important scope distinction

This freezes the validation **PILOT only**.

The full `novel_validation` split is **NOT COMPLETE**. The target remains
approximately 12-18 total questions. A later N3-E full validation expansion may
create a new validation version that includes this frozen pilot unchanged plus
new independently curated validation questions.

## Outcome blindness

- Validation outcomes observed: 0
- novel_dev outcomes used: 0
- C8 outcomes used: 0
- Agent-selected evidence used: 0

No PANDA retrieval, QA, verifier, judge, Vertex, embedding, Qdrant, SQL, or
runtime evaluation was run for this finalization.

## Measurement

Validation measurement: **NOT RUN / NOT AUTHORIZED**

## Holdout

novel_holdout: **NOT CREATED / EXTERNAL**

## Frozen novel_dev integrity

- Loaded: 28
- Human-approved: 28
- Split-frozen: 28
- Semantic changes: 0

The frozen `novel_dev.yaml` and `curation_metadata.yaml` files were not
modified.

## Next phase

N3-E — Full Validation Expansion

Status: **NEXT_ELIGIBLE / NOT_STARTED**

N3-E is not started or authorized by this task. It must preserve `n901`-`n906`
semantically unchanged, use a new validation version, remain outcome-blind,
and still not run validation measurement without separate authorization.
