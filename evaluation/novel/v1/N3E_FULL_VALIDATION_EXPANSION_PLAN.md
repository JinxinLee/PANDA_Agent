# N3-E Full Validation Expansion Plan

Plan status: `EXPANSION_CURATED / HUMAN_REVIEW_PENDING`

Dataset line: `0.2.0` / `novel-v1-validation-0.2.0`

Identity: `novel-v1-validation-expansion`

Split state: `EXPANSION_IN_PROGRESS`

Release eligible: `false`

## Baseline

The N3 validation pilot is complete and immutable: 6/6 records are approved
and 6/6 are `split_frozen`. The frozen records are `n901`-`n906` in families
`vf001`-`vf006` under dataset version `0.1.0`. Full validation is not complete,
and validation measurement has not run.

Frozen `novel_dev` remains complete with 28 approved and 28 `split_frozen`
records. Its question and sidecar files are not modified by N3-E.

## Version transition

```text
0.1.0 validation pilot
->
0.2.0 validation expansion
```

The expansion carries the six frozen pilot records forward without changing
their information needs, Gold annotations, selectors, family assignments,
review metadata, or lifecycles. It adds six draft candidates, producing 12
loaded records while keeping the split incomplete and in human review.

## Expansion target

N3-E investigates approximately 6-8 viable new questions, quality first. Six
independently supported candidates survived the source and family-isolation
audit, so curation stops at 12 total records rather than manufacturing more
content toward the approximate 15-question planning center.

## Isolation requirements

### Against exposed Gold

A candidate is rejected only when it is a semantic duplicate, paraphrase,
trivial reformulation, or narrower/wider restatement of the same minimum user
information need. Shared intent, task archetype, subsystem, entity, file,
documentation page, or evidence is allowed when the requested information is
materially different. Each admitted record explicitly states the closest Gold
case, all material overlaps, and the independent minimum information need.

### Against frozen novel datasets

Strict semantic-family isolation applies against all 28 frozen `novel_dev`
families and all six frozen validation-pilot families. A different entity,
detector, method name, or path is never sufficient by itself. Each admitted
record identifies the closest families in both frozen splits and explains why
the underlying user need is not a narrow, wide, renamed, or substituted
variant.

## Outcome blindness

Candidate creation followed:

```text
locked corpus anchor
-> natural PANDA information need
-> exposed-Gold comparison
-> strict frozen-novel family isolation
-> independent Gold annotation
-> static selector verification
```

No novel-dev result, validation result, C8 result, reranker trace, candidate
selection trace, Agent-selected evidence, treatment/control outcome, or
holdout content was opened or used. N3-E performs T0 curation only.

## Static support audit

### Areas inspected

- Locked PANDA detector overview and PID theory in `li_2026`, including DIRC
  angular/momentum coverage and the iron/MDT muon range system.
- PandaRoot `pid/PidCorr`, focusing on the reconstructed-track to
  `PndPidCandidate` boundary and region-specific detector information.
- PandaRoot `field`, focusing on ordered multi-map selection and local-grid
  interpolation rather than track propagation.
- PandaRoot `tracking/PndMvdGemTrackFinderOnHits`, focusing on MVD/GEM input
  branch ownership and the produced track/candidate boundary.
- Locked RHO combinatorics documentation, focusing on decay-candidate
  composition, mass selection, and overlap suppression.
- All exposed Gold questions, all 28 frozen `novel_dev` questions/families,
  and all six frozen validation-pilot questions/families as curation
  comparison inputs only.

### Investigation signals

The pilot had no `algorithm_theory`, `data_flow`, or `module_structure`
records, no paper-only evidence, and no cross-repository footprint. These were
investigation signals, not quotas. The audit found strong natural support for
the three missing intents and for paper, documentation, and code evidence. It
did not find a natural two-repository minimum critical footprint, so no
cross-repository case was manufactured.

All admitted questions are naturally `answered`. No locked-source conflict,
natural ambiguity, or unresolved-but-useful information need justified another
status class.

### Candidate-rich areas

- Detector-system comparisons and causal detector-response explanations.
- Reconstruction-to-PID and detector-hit-to-track producer/consumer
  boundaries.
- Magnetic-field service implementation across map selection and lookup.
- Routine RHO composite-candidate operations.

### Admitted batch

| ID | Family | Intent | Information need | Minimum evidence |
|---|---|---|---|---|
| n907 | vf007 | algorithm_theory | Barrel versus Endcap Disc DIRC coverage and design | `li_2026`, pages 46-47 |
| n908 | vf008 | data_flow | `PndTrack` to `PidChargedCand` correlation flow | PandaRoot code |
| n909 | vf009 | algorithm_implementation | ordered field-piece selection and grid evaluation | two complementary PandaRoot code files |
| n910 | vf010 | module_structure | MVD/GEM hit-to-track module and branch boundary | PandaRoot code |
| n911 | vf011 | usage | RHO decay combinatorics, mass selection, and overlap control | locked Sphinx documentation |
| n912 | vf012 | algorithm_theory | pion/muon discrimination by iron/MDT range sampling | `li_2026`, page 48 |

All six candidates are recommended as representative under the two-signal
method. None required a substantive frontier property that would justify an
exploratory classification.

## Evidence-contract discipline

Every critical `any_of` list contains one selector. For n909, field-piece
selection and local-grid evaluation are complementary obligations and are
therefore separate critical evidence groups. No header is used as an
alternative to an implementation file when it would prove only an interface.
All answer points are narrow obligations needed by the stated information
need.

## Human review workflow

```text
N3-E curation
-> human review
-> correction if required
-> explicit re-review
-> decide whether accepted total is sufficient
-> separately authorized full-validation finalization/freeze
```

The six new records begin as `draft` with `reviewer: null`,
`reviewed_at: null`, and sidecar lifecycle `draft`. Codex recommendations are
advisory. No approval, freeze, measurement, or second expansion batch is
authorized by this plan.

## Discarded pre-ID ideas

- A standalone GEM hit-to-track chain was discarded because the admitted
  MVD/GEM integration boundary is a more substantive cross-detector need; a
  second GEM workflow would be family-adjacent.
- A second RHO fitting question was discarded because it would over-concentrate
  the batch on adjacent tutorial operations before human review.
- Event-time and burst-buffer ideas were discarded because the locked Sphinx
  stubs alone were too thin and a code-heavy expansion risked becoming a
  narrower variant of frozen time-ordering family `nf029`.
- A generic detector-package location inventory was discarded as mechanical
  detector substitution relative to source-location and repository-structure
  families.
- A cross-repository integration question was discarded because no natural
  minimum critical footprint required two repository identities.
- Artificial `insufficient_evidence`, `version_conflict`, and clarification
  ideas were discarded because they were status-diversity constructions rather
  than independently sampled user needs.

## Stop state

```text
N3 pilot: PASS / COMPLETE
validation pilot: 6 / 6 split_frozen
N3-E: EXPANSION_CURATED / HUMAN_REVIEW_PENDING
novel_validation: EXPANSION_IN_PROGRESS
loaded: 12
approved: 6
draft/pending: 6
frozen: 6
full validation: NOT COMPLETE
validation measurement: NOT RUN
```

Next task: human review of the N3-E expansion candidates.
