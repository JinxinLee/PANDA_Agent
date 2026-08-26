# N3 — Novel Validation Curation Plan and Pilot Record

Plan status: `PILOT_COMPLETE / N3-E BATCH1_HUMAN_APPROVED / N3-E2 EXPANSION2_CURATED / HUMAN_REVIEW_PENDING`

N3: `PASS / COMPLETE`

Current dataset line: `0.2.0` / `novel-v1-validation-0.2.0`

Current identity: `novel-v1-validation-expansion`

Split state: frozen pilot preserved / `EXPANSION_IN_PROGRESS`

Release eligible: `false`

## 1. Purpose and evaluation role

`novel_validation` is a later-stage independent checkpoint after development
using exposed Gold/dev and, eventually, `novel_dev`. It is not another
development set, a clone of `novel_dev`, a hidden external holdout, or a
benchmark quota-matching exercise.

The role distinction is temporal and methodological rather than a promise that
validation is harder or more obscure:

- `novel_dev` is the frozen 28-question diagnostic development set that may
  later support generic repair after first exposure.
- `novel_validation` remains outcome-unseen during C8 and subsequent generic
  development until an explicit, later measurement authorization.
- `novel_holdout` remains externally curated; its protected content must not
  enter the normal repository development loop. The repository supplies only
  existing schema/loading support.

Validation question and Gold content may be repository-visible for curation
and human review. Validation system outcomes must remain unobserved until a
later explicit measurement. Repository visibility therefore does not make this
split a true external holdout.

## 2. Size and quality target

The full validation quality target is approximately 15 questions. This is a
quality target, not a quota: source support, family independence, Gold quality,
and human review override count.

N3 curates a pilot of six candidates. The pilot is intentionally within the
requested 6-8 range and does not complete or stand in for the full validation
split.

## 3. Outcome-blind sampling and Gold isolation

Every candidate follows anchor-first sampling:

```text
locked source/domain anchor
-> plausible independent PANDA user need
-> domain relevance
-> exposed Gold overlap check
-> all-28 frozen novel_dev family check
-> substantive novelty check
-> wording
-> independent Gold annotation from locked sources
-> static evidence verification
-> representativeness judgment
-> Codex recommendation
-> later human review
```

Coverage numbers may reveal gaps but never start a candidate. Gold annotation
comes only from locked-source inspection. No Agent-selected evidence,
retrieval trace, ranking, answer, verifier result, treatment/control result, or
per-question outcome may inform wording, selection, evidence, or admission.

## 4. Family isolation

One semantic family may occur in only one repository-visible novel split. A
validation candidate is rejected if its minimum information need is a
paraphrase, entity substitution, narrower/wider restatement, same workflow with
a different file, or same algorithm with another method name from any of the
28 frozen `novel_dev` families.

For each admitted record, the sidecar and review package name the closest
frozen or accepted family or families and explain the substantive difference.
Different paths alone never establish independence. The current validation
lineage uses `vf001`-`vf015`; every new family is also checked against the
frozen `nf001`-`nf031` lineage.

## 5. Dedicated ID namespace

The preferred `v###` question form is not compatible with the current strict
Gold model, whose ID pattern is `^[gn]\d{3}$`. Production evaluator source is
out of scope for N3, so the smallest schema-compatible dedicated namespace is
the visibly reserved high range `n901`-`n906`. This is not a continuation at
`n032`; it leaves the frozen lineage intact and remains distinguishable by both
ID range and `vf###` family namespace.

## 6. Representative and exploratory policy

Classification uses two independent signals:

1. benchmark-reference task-archetype fit; and
2. independent PANDA-domain relevance.

Exploratory admission additionally requires domain relevance plus at least one
substantive frontier property. The pilot produced six representative
candidates and no exploratory candidate. This is an observed classification,
not a required ratio or a claim about user-traffic frequency.

## 7. Status and repository-scope policy

All six supported questions are naturally `answered`. No legitimate
`insufficient_evidence`, `version_conflict`, or `clarification_required` need
arose, so status diversity was not manufactured and no clarification T0 was
needed.

All six minimum critical evidence footprints resolve to one repository
identity (`pandaroot`, including its locked documentation snapshot). No
candidate requires two repository identities, so the pilot contains no
`cross_repository` record. Repo plus documentation is not cross-repository.

## 8. Static support audit

### Areas inspected

- PandaRoot installation pages: external-package build integration, CVMFS,
  native/developer setup, and installation troubleshooting.
- Running and MasterTasks pages: generator configuration, event filtering,
  staged file production, target/transport options, and reconstruction tasks.
- RHO tutorials: data access, PID selection, combinatorics, MC truth, fitting,
  task analysis, tuples, and event filtering.
- Tools documentation: MCTrackAnalysis, MasterTasks, event time, burst
  building, filename helpers, and track-array merging.
- Locked PandaRoot source regions: EMC clustering/bump reconstruction,
  tracking utilities, PID correlation, MDT, GEM, timebased buffers, event
  display, and detector packages.
- Frozen `novel_dev` Gold and sidecar family definitions, inspected only as
  curation inputs; no novel outcome artifact was opened.

### Candidate-rich areas

External-package integration, RHO PID operations, MCTrackAnalysis
diagnosis, EMC reconstruction, reusable track-branch utilities, and
pre-transport filtering provided direct, bounded evidence and natural PANDA
user needs. These anchors yielded the six pilot records.

### Areas rejected for frozen-family overlap or weak support

- One-more-script or one-more-stage descriptions of the LMD workflow were
  rejected against `nf021`.
- Additional POCA artifacts or variables were rejected against `nf022`.
- Another ring-sorter or detector-specific sorter method was rejected against
  `nf029`.
- A question choosing one generator category in a macro was rejected against
  `nf031`; the admitted event-filter case instead concerns pre-transport
  rejection after generation.
- More detail on the fixed-step particle gun was rejected against `nf003`.
- Complete MC-truth tree matching with added particle-database setup was
  rejected as a narrower operational restatement of `nf018`, which already
  covers candidate truth inspection and whole-decay-tree matching.
- A generic sim/digi/reco/pid filename-chain question was rejected against
  `nf006` and the previously documented N2 stage-chain adjacency concern.
- Thin Sphinx stubs for burst building and event-time APIs were not admitted
  because they did not support sufficiently narrow answer obligations.
- PID-correlator and muon-chain drafts were deferred because a compact pilot
  question risked over-annotating a broad implementation surface.

### Status, cross-repository, and future support

The inspected anchors support answered cases only. No same-need authoritative
version conflict, natural ambiguity, or unresolved but useful information need
was found. No two-repository minimum footprint survived the frozen-family
check. Future full expansion may investigate unused detector reconstruction
packages, additional analysis task forms, locked thesis physics outside LMD
track-search/IP-alignment families, and repository structure anchors, but only
after pilot review and explicit authorization.

## 9. Pilot artifacts and lifecycle

The pilot uses dedicated artifacts:

- `novel_validation.yaml`
- `novel_validation_curation_metadata.yaml`
- `novel_validation_manifest.json`
- `novel_validation_coverage_report.json`
- `N3_VALIDATION_PILOT_REVIEW_PACKAGE.md`
- `N3_PILOT_FINALIZATION_REPORT.md`

During initial curation every record started as `split: novel_validation`,
`review_status: draft`, `reviewer: null`, `reviewed_at: null`, and sidecar
`lifecycle: draft`. After final human re-review, the manifest records six
questions, six families, six accepted, zero revised, zero rejected, zero
pending, six frozen, `human_approval: complete`, and `release_eligible: false`.

## 10. Freeze and measurement order

The only valid order is:

```text
pilot curation
-> human review
-> pilot correction if needed
-> pilot approval
-> full validation expansion
-> human review
-> complete validation freeze
-> later explicit validation measurement
```

No measurement is permitted before the complete split freeze. N3-F approves
and freezes this six-question pilot only; it does not expand the full
validation split or authorize measurement. Human review and the freeze remain
distinct from the future full-validation expansion.

## 11. Parallel C8 and immutable novel_dev boundaries

The N3 baseline is commit `b8f5a7b13b074d91bf4969a5c7b6e0b2ef00187f`.
It already contains the C8 A0/A1/A1R1 development history and the N2 freeze.
N3 preserves that history and the authoritative C8 lifecycle without opening
or using C8 outcomes. It does not modify C8 implementation, tests, or
artifacts.

Frozen `novel_dev.yaml` and `curation_metadata.yaml` remain untouched: 28
loaded, 28 approved, 28 split-frozen, status `COMPLETE`. No holdout question or
ID is created.

## 12. Historical N3-R1 stop state

After the N3-R1 corrections and deterministic T0 validation, N3 stops at:

```text
N3: PILOT_HUMAN_REVIEWED / R1_RE_REVIEW_PENDING
novel_validation: PILOT_IN_PROGRESS
human review: 4 ACCEPT / 2 REVISE / 0 REJECT
human-approved: 4
corrected and awaiting re-review: n904, n905
split-frozen: 0
full validation: NOT COMPLETE
validation measurement: NOT RUN
```

This was the pre-finalization state. The pilot remained unfrozen and no
expansion was authorized at that point.

## 13. N3-F finalization and freeze

Final human re-review by Li at `2026-08-26T00:21+02:00` accepted corrected
n904 and n905 from reviewed correction commit
`971a3d34abf92b89da2f2f13263b97313223ec35`. The final pilot decision is
6 ACCEPT / 0 REVISE / 0 REJECT / 0 PENDING.

```text
N3: PASS / COMPLETE
novel_validation: PILOT_COMPLETE / SPLIT_FROZEN
pilot: 6 / 6 approved, 6 / 6 split_frozen
pilot version: 0.1.0 / novel-v1-validation-0.1.0
full validation: NOT COMPLETE
N3-E full expansion: NEXT_ELIGIBLE / NOT_STARTED
validation measurement: NOT RUN
release_eligible: false
```

The six pilot records are now immutable measurement data. Full validation
expansion, holdout creation, and validation measurement remain outside this
task and require separate authorization.

## 14. N3-E full validation expansion

N3-E opened `0.2.0` / `novel-v1-validation-0.2.0`, identity
`novel-v1-validation-expansion`, while carrying frozen `n901`-`n906` and
`vf001`-`vf006` forward unchanged. Six new independently source-anchored
records (`n907`-`n912`, `vf007`-`vf012`) were curated and then accepted by Li
at `2026-08-26T15:36+02:00` from reviewed commit
`fa902109123c17b92297c6839fd4664c659ff3c5`. They are approved but not frozen.

```text
N3 pilot: PASS / COMPLETE
validation pilot: 6 / 6 approved and split_frozen
N3-E: BATCH1_HUMAN_APPROVED
novel_validation: EXPANSION_IN_PROGRESS
loaded: 12
approved: 12
draft/pending: 0
frozen: 6
full validation: NOT COMPLETE
validation measurement: NOT RUN
```

The current expansion plan is
`N3E_FULL_VALIDATION_EXPANSION_PLAN.md`; candidate decisions belong in
`N3E_VALIDATION_EXPANSION_REVIEW_PACKAGE.md`. N3-E human approval does not
split-freeze those records and does not authorize measurement.

## 15. N3-E2 final small expansion batch

N3-E2 retains the same `0.2.0` expansion lineage and adds three outcome-blind
drafts (`n913`-`n915`, `vf013`-`vf015`). The source-first audit stopped at
three strong candidates, matching the approximate-15 planning center without
treating it as a quota.

```text
N3 pilot: PASS / COMPLETE
N3-E: BATCH1_HUMAN_APPROVED
N3-E2: EXPANSION2_CURATED / HUMAN_REVIEW_PENDING
novel_validation: EXPANSION_IN_PROGRESS
loaded: 15
families: 15
approved: 12
draft/pending: 3
frozen: 6
full validation: NOT COMPLETE
validation measurement: NOT RUN
```

The current plan and review package are
`N3E2_FINAL_VALIDATION_EXPANSION_PLAN.md` and
`N3E2_VALIDATION_EXPANSION_REVIEW_PACKAGE.md`. n913-n915 are drafts with no
reviewer and must not be approved or frozen without separate human action.

Next task: human review of the N3-E2 candidates.
