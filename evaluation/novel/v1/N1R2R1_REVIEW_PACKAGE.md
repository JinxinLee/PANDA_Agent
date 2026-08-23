# N1-R2R1 Final Gold Governance Cleanup Review Package

## Status

`READY_FOR_FINAL_HUMAN_APPROVAL / HUMAN_REVIEW_PENDING`

This package contains 16 active draft `novel_dev` questions in 16 independent
semantic families. It is not approved or frozen Gold. All active records retain
`review_status: draft`, `reviewer: null`, and `reviewed_at: null`.

## Governance corrections

- **n001 source type:** `configSettings.sh` is classified by the evaluator as a
  shell-script workflow object, so both the Gold record and sidecar now require
  `workflow`, not `code`.
- **n008 evidence range:** direct inspection of locked Karavdina PDF pages 72-81
  found that pages 72-77 are the minimum sufficient range. Pages 72-75 describe
  track following and cellular automaton construction; pages 76-77 establish
  the missed/fake-track objective, its luminosity consequence, and the realistic
  multiplicity context. Pages 78-81 add detailed plots and fake-track examples
  that are not required by the three answer points. Machine Gold and review
  wording therefore agree on pages 72-77.
- **n010 response semantics:** `PndFsmResponse` carries a detected flag,
  resolution/smearing values, and detector/PID response values. Detector
  efficiency is configured on `PndFsmAbsDet`; it is not a field carried by
  `PndFsmResponse`.
- **Information-need identity:** n011/nf011 and n012/nf012 are retired as
  `WITHDRAWN_DRAFT`. The repaired analysis-usage information need is a new
  question n018/nf018. n012's unsupported original information need is not
  migrated; n019/nf019 is an independently sampled replacement.

## Active candidate inventory

| ID | Family | Intent | Primary task archetype | Gold evidence summary |
|---|---|---|---|---|
| n001 | nf001 | installation | setup_environment | Restgas `configSettings.sh` and `INSTALL.GSI` |
| n002 | nf002 | installation | setup_environment | LuminosityFit `requirements.txt` |
| n003 | nf003 | usage | component_usage | fixed-step generator implementation and documentation |
| n004 | nf004 | usage | component_usage | locked FairLogger documentation |
| n005 | nf005 | usage | component_usage | event-display documentation and macro |
| n006 | nf006 | api | component_usage | filename-creator interface and implementation |
| n007 | nf007 | api | component_usage | `PndGeoHandling` interface and documentation |
| n008 | nf008 | algorithm_theory | concept_comparison | Karavdina PDF pages 72-77 |
| n009 | nf009 | algorithm_theory | theory_explanation | Karavdina PDF plus E760 model code |
| n010 | nf010 | algorithm_implementation | implementation_explanation | fastsim task, detector abstraction, factory, response object |
| n014 | nf014 | module_structure | repository_structure | ModelFramework README and native model factory header |
| n015 | nf015 | troubleshooting | troubleshooting_diagnosis | locked ARM build documentation |
| n016 | nf016 | troubleshooting | setup_environment | locked Docker documentation insufficiency boundary |
| n017 | nf017 | api | source_location | persistent `PndTrack` definition |
| n018 | nf018 | usage | component_usage | Monte Carlo Truth Match tutorial only |
| n019 | nf019 | algorithm_implementation | implementation_explanation | `PndRecoKalmanTask` header and implementation |

## n018 semantic repair

- **Question:** In PandaRoot analysis, how can I inspect the Monte Carlo truth
  counterpart of a reconstructed candidate and check whether an entire
  reconstructed decay tree matches the generated one?
- **Classification:** `usage` / `component_usage` / answerable.
- **Required answer points:** call `RhoCandidate::GetMcTruth()` and null-check
  the result; use `PndAnalysis::McTruthMatch(candidate)` for an arbitrary decay
  tree, with intended composite types and the tutorial's EvtGen PDG-table setup.
- **Evidence boundary:** locked Monte Carlo Truth Match tutorial only. No
  `PndMCTrackInfo`, generator-stage propagation, or producer-consumer trace is
  claimed.
- **Identity decision:** the final information need differs from the withdrawn
  n011 data-flow draft, so the contract requires the new n018/nf018 identity.

## n019 independent sampling record

Five locked-corpus anchors were inspected without using system outcomes:

| Anchor | Disposition | Reason |
|---|---|---|
| `PndRecoKalmanTask.h/.cxx` | selected as n019 | core, evidence-clean implementation pipeline absent from exposed Gold |
| `PndMasterRunSim` documentation/source | rejected | simulation-master use and orchestration are already exposed in Gold |
| `PndLmdTrackFinderCATask.cxx` | rejected | overlaps exposed g104/g116 and the n008 LMD track-search family |
| `PndTrack.h` / `PndTrackCand` boundary | rejected | already occupied by active n017 |
| Monte Carlo Truth Match tutorial | rejected for n019 | already allocated to the independently governed n018 usage family |

- **Question:** How does `PndRecoKalmanTask` turn input `PndTrack` objects into
  fitted output tracks, including fitter selection, particle-hypothesis choice,
  and the construction of each persisted result?
- **Classification:** `algorithm_implementation` /
  `implementation_explanation` / answerable.
- **Required answer points:** Init selects/configures Kalman versus DAF and the
  track representation; Exec chooses the configured or MC-derived particle
  hypothesis with documented fallbacks; for a nonzero selected PDG hypothesis,
  the configured fitter produces the fitted track, and the task constructs the
  output `PndTrack` from its endpoints, candidate, quality, fit statistics, and
  PID hypothesis while passing the input index and branch ID to the constructor.
- **Evidence:**
  `tracking/GenfitTools/recotasks/PndRecoKalmanTask.h` and
  `tracking/GenfitTools/recotasks/PndRecoKalmanTask.cxx` in the locked PandaRoot
  snapshot.
- **Novelty:** no exposed question names this task or asks for this composed
  configuration-to-output implementation path. The implementation question is
  not a class-name substitution for g059/g060.

## Retired draft lineage

| Retired ID/family | Status | Reason | Active replacement |
|---|---|---|---|
| n011/nf011 | WITHDRAWN_DRAFT | information need changed during semantic repair | n018/nf018 |
| n012/nf012 | WITHDRAWN_DRAFT | unsupported original information need replaced by new sampling | n019/nf019 |
| n013/nf013 | WITHDRAWN_DRAFT | prior representativeness and factual failure | n017/nf017 |

The retired IDs and families are historical and must not be reused. n019 is an
independent sample, not a semantic migration of n012.

## Coverage summary

- Active questions / families: 16 / 16.
- Canonical intents: installation 2; usage 4; api 3; algorithm_theory 2;
  algorithm_implementation 2; data_flow 0; module_structure 1;
  troubleshooting 2.
- Expected status: answered 15; insufficient_evidence 1.
- Difficulty: simple 5; moderate 9; hard 2.
- Representativeness: representative 16; exploratory 0. No active 12/4 quota.
- Explicit gap: no data-flow question remains after the governance retirements;
  the pilot does not fabricate a replacement merely to fill the intent.

## Human approval checklist

- Confirm the n001 workflow source-type correction.
- Confirm n008 pages 72-77 as the minimum sufficient Gold range.
- Confirm n010's separation of response fields from detector efficiency.
- Confirm n011/n012 withdrawal and the n018/n019 identity lineage.
- Confirm n019's independent sampling and implementation answer points.
- Confirm all 16 active questions and families are mutually distinct.
- If accepted, supply a human reviewer identity and review timestamp in a
  separate finalization task; this package does not self-approve.

## Static-only boundary

No PANDA retrieval, QA, judge, Vertex generation, dense embedding, sparse
encoding, Qdrant/SQL access, benchmark outcome inspection, novel outcome
inspection, or scientific evaluation was performed for N1-R2R1.
