# N3 Validation Pilot Review Package

Status: `PILOT_CURATED / HUMAN_REVIEW_PENDING`

Dataset: `novel-v1-validation-0.1.0`

Pilot: 6 draft candidates / 6 independent families

Human-approved: 0

Frozen: 0

This package presents source-anchor-first candidate and Gold annotation for
human review. Codex recommendations are advisory. No candidate is approved or
split-frozen by this package, and no PANDA Agent, novel, validation, or C8
outcome informed selection.

## n901 / vf001 — External package integration

- **Question:** I maintain an external analysis package that must compile
  against an installed PandaRoot. Which setup script must I source, which
  CMake module and setup macro connect the package to PandaRoot, FairRoot, and
  VMC, and where does the example install by default?
- **Intent / expected status / difficulty:** `installation` / `answered` /
  `moderate`.
- **Primary archetype:** `setup_environment`; no secondary archetype.
- **Representativeness recommendation:** `representative` — strong benchmark
  setup-task fit and strong independent software-development relevance.
- **Source/repository scope:** locked PandaRoot Sphinx documentation; one
  source snapshot associated with one repository identity;
  `single_repository`, not cross-repository.
- **Evidence topology:** `multi_hop` within one page: installed environment
  export plus external-package CMake/install contract.
- **Critical evidence summary:** `Building_ExternalPackage.html` documents
  sourcing `bin/PandaRootConfig.sh -a`, exported PandaRoot paths, the manual
  `FindPandaROOT.cmake` step, `PandaRootSetup` / `pandaroot_setup()`, and the
  default 3rdParty install prefix.
- **Answer-point summary:** name the environment script and exports; describe
  the CMake discovery/setup chain into FairRoot and VMC; state the default
  install-prefix behavior and re-source step.
- **Closest exposed Gold cases:** g001 and g002 (PandaRoot installation and
  prerequisites).
- **Closest frozen novel_dev families:** nf001 and nf015.
- **Why independent:** nf001 audits the RestgasDetermination fork's malformed
  version-pair shell branches; nf015 diagnoses ARM VC compilation. Neither
  addresses a separately maintained package's PandaRoot/FairRoot/VMC CMake
  boundary or its install prefix.
- **Novelty types / rationale:** `relation`, `task_form`; the new relation is
  external-package-to-installed-framework integration, not another PandaRoot
  installation procedure.
- **Independent domain relevance:** Panda analysis developers routinely build
  packages against an installed framework and need the documented exported
  paths and CMake entry point.
- **Cross-repository minimum-footprint derivation:** not applicable. Both
  critical groups resolve to the PandaRoot documentation identity; minimum
  repository count is one.
- **Known uncertainty:** the page says `FindPandaROOT.cmake` must *currently*
  be copied manually, so this annotation is intentionally version-bound to the
  locked snapshot and makes no claim about newer PandaRoot.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `PENDING`.

## n902 / vf002 — RHO PID selection and combination

- **Question:** In a RHO analysis, how do I request positively charged kaon
  candidates with a PID threshold, choose a particular detector algorithm,
  and combine several PID algorithms?
- **Intent / expected status / difficulty:** `usage` / `answered` / `moderate`.
- **Primary archetype:** `component_usage`; no secondary archetype.
- **Representativeness recommendation:** `representative` — strong benchmark
  component-usage fit and strong independent analysis relevance.
- **Source/repository scope:** locked RHO PID tutorial page; one PandaRoot
  documentation identity; `single_repository`.
- **Evidence topology:** `multi_hop`: selection keyword/threshold semantics
  plus named classifier and probability-combination semantics.
- **Critical evidence summary:** `tut_02_02_analysis_pid.html` documents
  `FillList`, charge/type/criterion keywords, named PID algorithms as the
  third parameter, and semicolon-separated algorithm products.
- **Answer-point summary:** show `KaonTightPlus` and an arbitrary threshold;
  identify the third argument with a detector algorithm; explain that listed
  classifier probabilities are multiplied per particle hypothesis.
- **Closest exposed Gold cases:** g022 (RHO data-access/PID documentation) and
  g024 (analysis task form).
- **Closest frozen novel_dev family:** nf026.
- **Why independent:** nf026 only identifies and summarizes the official RHO
  tutorial sequence. Its minimum answer does not contain a `FillList` keyword,
  threshold, classifier selection, or combination rule.
- **Novelty types / rationale:** `relation`, `composition`, `task_form`; the
  candidate composes particle selection, detector classifier choice, and
  multi-classifier probability handling into one operational need.
- **Independent domain relevance:** charged-hadron PID selection is a routine
  reconstruction-analysis operation for PANDA channels.
- **Cross-repository minimum-footprint derivation:** not applicable; both
  critical groups resolve to one locked PandaRoot documentation source.
- **Known uncertainty:** the tutorial explicitly notes that default criterion
  thresholds can be parameter-database controlled and that `VeryLoose` then
  equals `All`; the Gold asks only for the documented selection semantics and
  does not generalize beyond the locked page.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `PENDING`.

## n903 / vf003 — MCTrackAnalysis reconstruction-loss diagnosis

- **Question:** I need to find the reconstruction stage at which a simulated
  decay channel loses events. What two-stage MCTrackAnalysis workflow does
  PandaRoot document, what information is attached first, and how are decay
  and reconstruction requirements expressed for the diagnosis?
- **Intent / expected status / difficulty:** `troubleshooting` / `answered` /
  `moderate`.
- **Primary archetype:** `troubleshooting_diagnosis`; secondary
  `workflow_sequence`.
- **Representativeness recommendation:** `representative` — moderate benchmark
  diagnostic-task fit, strong domain relevance, and a
  `representative_but_rare` corpus anchor.
- **Source/repository scope:** locked MCTrackAnalysis documentation; one
  PandaRoot documentation identity; `single_repository`.
- **Evidence topology:** `multi_hop`: MC-track enrichment feeds declarative
  event/particle requirements and structured failure reporting.
- **Critical evidence summary:** `MCTrackAna.html` documents
  `PndMCTrackInfoTask`, attached decay/link/reconstruction/PID information,
  `PndEventRequirements` with `PndParticleRequirements`, and the result,
  point-of-failure, and interesting-event outputs.
- **Answer-point summary:** explain stage-one enrichment; define mandatory and
  optional stage-two requirements; explain how the output localizes loss.
- **Closest exposed Gold cases:** g024 (analysis in a task) and g110
  (workflow troubleshooting).
- **Closest frozen novel_dev families:** nf018, nf019, and nf026.
- **Why independent:** nf018 performs candidate and whole-tree truth matching,
  nf019 explains one fitting task's execution, and nf026 navigates a tutorial
  sequence. None diagnoses survival across the entire reconstruction chain
  using linked MC objects and requirement positions.
- **Novelty types / rationale:** `composition`, `reasoning_topology`,
  `task_form`; it combines enrichment, declarative decay structure, and staged
  failure localization.
- **Independent domain relevance:** identifying where signal events disappear
  is a direct reconstruction-validation need for simulated decay studies.
- **Cross-repository minimum-footprint derivation:** not applicable; both
  critical obligations use one PandaRoot documentation identity.
- **Known uncertainty:** the page contains an external presentation link, but
  the Gold relies only on the locked page content and does not require that
  external presentation.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `PENDING`.

## n904 / vf004 — EMC cluster-to-bump reconstruction boundary

- **Question:** In PandaRoot EMC reconstruction, how are calorimeter digis
  turned into clusters, and why is a later bump-splitting stage needed?
- **Intent / expected status / difficulty:** `algorithm_implementation` /
  `answered` / `moderate`.
- **Primary archetype:** `implementation_explanation`; secondary
  `producer_consumer_trace`.
- **Representativeness recommendation:** `representative` — moderate Gold
  implementation-task fit and strong central-detector relevance.
- **Source/repository scope:** locked PandaRoot code under
  `detectors/emc/EmcReco`; one repository identity; `single_repository`.
- **Evidence topology:** `producer_consumer`: `PndEmcMakeCluster` produces
  `EmcCluster`; `PndEmcMakeBump` / `PndEmcExpClusterSplitter` consume cluster
  local maxima and produce bump/shared-digi objects.
- **Critical evidence summary:** cluster headers/implementation document
  section thresholds, spatial adjacency, timestamp handling, and cluster
  merging; bump/splitter implementation documents `LocalMaxMap`, `EmcBump`,
  and `EmcSharedDigi` creation.
- **Answer-point summary:** describe thresholded adjacency clustering; explain
  why multiple local maxima require bump splitting; describe the shared-digi
  apportioning boundary.
- **Closest exposed Gold cases:** none found; g059/g065 are task-form analogues
  only.
- **Closest frozen novel_dev families:** nf010 and nf029.
- **Why independent:** nf010 is parameterized fast simulation, not calorimeter
  reconstruction. nf029 is generic time ordering; timestamp behavior is
  incidental to this family's spatial clustering and local-maximum split.
- **Novelty types / rationale:** `relation`, `composition`,
  `reasoning_topology`; this new producer-consumer relation joins two distinct
  EMC reconstruction stages.
- **Independent domain relevance:** clustering and shower separation are
  central calorimeter reconstruction operations, not an obscure symbol lookup.
- **Cross-repository minimum-footprint derivation:** not applicable; both
  critical groups require only the locked PandaRoot source identity.
- **Known uncertainty:** the implementation carries event-based and
  timestamp-based branches. The Gold states their shared spatial boundary and
  only the directly documented time condition; it does not attempt a full EMC
  algorithm inventory.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `PENDING`.

## n905 / vf005 — PndTrackArrayMerger branch aggregation

- **Question:** I have several PandaRoot branches containing `PndTrack` objects
  and need a single track branch for downstream tasks. What does
  `PndTrackArrayMerger` accept, what does it produce by default, and how does it
  handle unavailable or wrong-type inputs?
- **Intent / expected status / difficulty:** `api` / `answered` / `simple`.
- **Primary archetype:** `component_usage`; no secondary archetype.
- **Representativeness recommendation:** `representative` — moderate
  benchmark-reference fit and moderate independent relevance;
  `representative_but_rare`.
- **Source/repository scope:** locked `tools/PndTrackArrayMerger.h/.cxx`; one
  PandaRoot code identity; `single_repository`.
- **Evidence topology:** `single_hop` interface/implementation lookup.
- **Critical evidence summary:** the class exposes input/output/persistency
  setters, defaults the output to `ALLTracks`, accepts only `PndTrack` arrays,
  skips missing inputs, and calls `AbsorbObjects` during execution.
- **Answer-point summary:** configure named inputs and optional output; state
  default output and storage control; explain missing/type filtering and
  execution aggregation.
- **Closest exposed Gold cases:** none found; g023/g028 are only usage/location
  analogues.
- **Closest frozen novel_dev families:** nf017 and nf023.
- **Why independent:** nf017 defines the persistent `PndTrack` object and
  nf023 describes FTS branch production. Aggregating arbitrary homogeneous
  `PndTrack` branches into one destination is a different downstream operation.
- **Novelty types / rationale:** `entity`, `relation`, `task_form`; the
  independently sampled utility relates multiple producer branches to one
  consumer-facing branch and includes explicit type acceptance behavior.
- **Independent domain relevance:** combining central/forward or alternative
  track collections is a plausible reconstruction-chain integration need.
- **Cross-repository minimum-footprint derivation:** not applicable; one code
  file pair in one repository identity suffices.
- **Known uncertainty:** the source comment says “copies,” while the
  implementation specifically calls ROOT `AbsorbObjects`; the Gold reports the
  implementation call and does not infer ownership semantics beyond it.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `PENDING`.

## n906 / vf006 — Pre-transport event filtering

- **Question:** Can I reject generated events before detector transport in a
  PandaRoot MasterTasks simulation, and how does the documented example require
  at least four charged particles?
- **Intent / expected status / difficulty:** `usage` / `answered` / `simple`.
- **Primary archetype:** `component_usage`; secondary `workflow_sequence`.
- **Representativeness recommendation:** `representative` — strong benchmark
  MasterTasks fit and strong simulation-cost relevance.
- **Source/repository scope:** locked PandaRoot MasterTasks documentation; one
  repository identity; `single_repository`.
- **Evidence topology:** `single_hop` configuration procedure.
- **Critical evidence summary:** `MasterTasks.html` documents obtaining the
  filtered primary generator, creating a single-particle-count filter,
  configuring a minimum charged multiplicity, and attaching it before
  simulation.
- **Answer-point summary:** state the pre-transport purpose and hook; give the
  exact filter class, `AndMinCharge` call, and `AndFilter` registration.
- **Closest exposed Gold cases:** g015 and g089.
- **Closest frozen novel_dev families:** nf003 and nf031.
- **Why independent:** nf003 controls per-event particle-gun stepping and nf031
  compares generator categories. This need operates after a generator is
  configured and before detector transport, rejecting whole events by a
  physics multiplicity condition.
- **Novelty types / rationale:** `relation`, `task_form`; it asks how generated
  content gates transport, not which generator produced it.
- **Independent domain relevance:** rejecting unusable background events before
  transport directly reduces compute and storage for analysis studies.
- **Cross-repository minimum-footprint derivation:** not applicable; the one
  critical group resolves to one PandaRoot documentation identity.
- **Known uncertainty:** the page supplies one charged-multiplicity example;
  the Gold does not claim to enumerate all available FairRoot filter classes.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `PENDING`.

## Discarded pre-ID ideas

No ID was consumed for these ideas:

- **One more LMD workflow script:** rejected as the same minimum information
  need as nf021 despite a different file path.
- **Another POCA handoff artifact:** rejected as a narrower restatement of
  nf022.
- **Detector-specific ring sorter method:** rejected as mechanical entity
  substitution within nf029's time-ordering family.
- **One generator category used by a macro:** rejected as a narrower form of
  nf031; this is why n906 starts from the filter boundary, not a generator
  choice.
- **More fixed-step gun configuration:** rejected as nf003 overlap.
- **Complete MC-truth tree matching with extra setup details:** rejected as a
  narrower operational restatement of nf018, which already asks how to inspect
  a reconstructed candidate's truth counterpart and match the entire decay
  tree. Extra `TDatabasePDG` preparation does not create a new minimum
  information need.
- **Generic sim/digi/reco/pid stage files:** rejected for adjacency to nf006 and
  the earlier N2 stage-chain discard; different macro paths do not establish a
  new family.
- **Burst-builder and event-time stubs:** rejected for insufficient
  authoritative detail to support a narrow, nontrivial Gold answer.
- **Broad PID-correlator/muon chain:** deferred because a pilot-sized question
  risked over-annotating a large implementation surface.
- **Second cross-repository case:** rejected as artificial construction; no
  independently sampled need required two repository identities after complete
  Gold annotation.
- **Forced insufficient/conflict/clarification case:** rejected as artificial
  status diversity; no natural locked-corpus anchor supported it.

## Review request

The human reviewer should return `ACCEPT`, `REVISE`, or `REJECT` for each
candidate and may revise the N3 planning assumptions. Acceptance in a later
task must add reviewer identity and timestamp and update lifecycle explicitly;
it must not silently freeze the pilot or authorize full expansion or
measurement.
