# H0 Frozen Family Boundary Reference

> **THIS REFERENCE IS FOR POST-HOC COLLISION EXCLUSION ONLY.**
> **IT MUST NOT BE USED AS A SAMPLING-GAP MAP.**

This sanitized reference is reconstructed from the current frozen
`novel_dev` and `novel_validation` definitions and curation metadata. It
contains no outcomes, performance observations, weakness analysis, or future
sampling recommendations. A shared repository, source, entity, class,
subsystem, detector, or task archetype is not sufficient to establish a
collision. Family identity is assessed jointly across minimum information
need, requested relation, answer obligation, critical evidence composition,
reasoning topology, and semantic task structure. A candidate is in the same
family when these signals, considered together, express the same underlying
need. Individual overlap in one or more signals—including reasoning topology,
evidence shape, subsystem, class, or entity—is allowed and does not alone
establish a collision.

## Active `novel_dev` families (28)

| Split | Question | Family | Minimum information need | Semantic-family boundary |
|---|---|---|---|---|
| `novel_dev` | `n001` | `nf001` | Audit RestgasDetermination's GSI setup script: encoded FairSoft/FairRoot pairs, exported paths, and actual unmatched-input behavior. | Includes variants asking what this specific script selects or enforces, including its shell-condition behavior and fallback semantics. |
| `novel_dev` | `n002` | `nf002` | Locate and enumerate LuminosityFit's declared Python requirements/tooling list without inferring undocumented per-script runtime roles. | Includes variants whose obligation is the contents and location of this repository-level requirements list. |
| `novel_dev` | `n003` | `nf003` | Identify PandaRoot's fixed-step particle gun and explain momentum/theta range configuration plus per-event stepping and rollover. | Includes variants asking how `PndFixStepParticleGun` performs deterministic scan progression across configured ranges. |
| `novel_dev` | `n004` | `nf004` | Configure PandaRoot logging to show severity and file/line/function, and identify the documented verbosity, color, and file-output controls. | Includes variants centered on the documented logger verbosity-format configuration and its related console/file presentation controls. |
| `novel_dev` | `n005` | `nf005` | Identify PandaRoot's event display and explain how a simulation-chain file prefix is opened with its friend stages. | Includes variants asking how `eventDisplay.C` loads a sim/digi/reco chain for geometry and event visualization. |
| `novel_dev` | `n006` | `nf006` | Explain how `PndFileNameCreator` derives chain-stage filenames from a simulation filename and enumerate its defined suffixes. | Includes variants about this helper's stage-suffix mapping, replacement behavior, or generated chain filenames. |
| `novel_dev` | `n007` | `nf007` | Resolve an MVD geometry `shortID` to a full path and state the geometry/parameter state that must be initialized first. | Includes variants about `PndGeoHandling` shortID/path translation and its `TGeoManager` plus `PndSensorNamePar` initialization contract. |
| `novel_dev` | `n008` | `nf008` | Compare LMD Track Following and Cellular Automaton search approaches, including the low-hit constraint and momentum-dependent performance conclusion. | Includes variants whose answer must compare these two LMD candidate-search algorithms and their missed/fake-track implications. |
| `novel_dev` | `n009` | `nf009` | Relate the E760 alternative elastic model to LuminosityFit code and distinguish intrinsic parameter uncertainty from beam-momentum uncertainty. | Includes variants requiring the E760/E760-like implementation link and this two-part uncertainty obligation. |
| `novel_dev` | `n010` | `nf010` | Trace PandaRoot fast simulation from particle candidates through detector response parametrizations to combined acceptance cuts and smearing. | Includes variants asking how `PndFastSim`, detector implementations, the factory, and `PndFsmResponse` divide this response-production workflow. |
| `novel_dev` | `n014` | `nf014` | Distinguish the archived working-copy role of `model_framework` from the native LuminosityFit model factory's exposed creation role. | Includes variants whose obligation is this specific directory/factory responsibility boundary, not a general model inventory. |
| `novel_dev` | `n015` | `nf015` | Diagnose the legacy VC build failure on ARM and state the documented `NOVC` workaround plus the tracking components it disables. | Includes variants about this exact VC/ARM configuration failure and the CAtracking/FtsCATracking side effect. |
| `novel_dev` | `n016` | `nf016` | Determine what the locked Docker documentation does and does not establish about native Windows hosts and identify the demonstrated Unix environment. | Includes variants evaluating the support claim warranted by those Docker pages, including the distinction between absent evidence and proven non-support. |
| `novel_dev` | `n017` | `nf017` | Locate the persistent reconstructed-track class and enumerate its fitted endpoints, track-candidate links, and reconstruction metadata. | Includes variants about the persisted `PndTrack` representation and its stored parameter/candidate relationship. |
| `novel_dev` | `n018` | `nf018` | Inspect a reconstructed candidate's MC truth counterpart and verify a complete reconstructed decay tree against generated truth. | Includes variants about `GetMcTruth()` for candidate-level truth access together with `PndAnalysis::McTruthMatch()` for whole-tree matching. |
| `novel_dev` | `n019` | `nf019` | Explain how `PndRecoKalmanTask` selects fitter, propagation, and particle hypothesis and persists each fitted `PndTrack`. | Includes variants tracing this task's initialization, per-track hypothesis selection, fitting, and output-object construction. |
| `novel_dev` | `n020` | `nf020` | Trace Restgas displaced-track recovery from unassigned hits through Apollonius finding, skew-straw z recovery, and final fitting. | Includes variants whose obligation is the responsibility sequence among these specific recovery stages before the final fit. |
| `novel_dev` | `n021` | `nf021` | Locate PandaRoot's LMD simulation/digitization/reconstruction implementation and the LuminosityFit scripts orchestrating simulation/reconstruction and fitting. | Includes variants tracing this cross-repository LMD workflow boundary between detector implementation and user-facing orchestration. |
| `novel_dev` | `n022` | `nf022` | Explain the two-pass Restgas POCA vertex workflow, its ROOT/JSON intermediate products, and how event-level and fitted-mean vertices feed reprocessing. | Includes variants asking how pass 1 produces and pass 2 consumes these specific vertex artifacts and fallbacks. |
| `novel_dev` | `n023` | `nf023` | Locate the FTS track finder and identify its default output branches and the distinct payload type of each branch. | Includes variants about `PndFtsTrackFinderTask` source location and its track, candidate, and analytic-track branch contract. |
| `novel_dev` | `n024` | `nf024` | Compare PandaRoot's GEANE and analytic-helix propagators and explain how each computes transported track state. | Includes variants requiring the shared propagation interface and the numerical-versus-homogeneous-field transport distinction. |
| `novel_dev` | `n025` | `nf025` | Explain how the displaced finder controls Apollonius drift-circle triplet combinatorics while retaining displaced-vertex efficiency. | Includes variants about its row separation, topology/azimuth checks, candidate growth, and best-pattern selection strategy. |
| `novel_dev` | `n026` | `nf026` | Identify and summarize the official RHO tutorial sequence from signal simulation through analysis, tuples, quick analysis, and background filtering. | Includes variants whose obligation is the ordered learning path and scope of this specific tutorial series. |
| `novel_dev` | `n027` | `nf027` | Explain PandaRoot Jupyter/PyROOT support and the environment variables and setup command needed to launch its bundled ROOT kernel. | Includes variants about starting and using the documented PandaRoot notebook environment without an extra kernel installation. |
| `novel_dev` | `n028` | `nf028` | Trace software-trigger decisions from `PndSoftTriggerTask` into `PndOnlineFilterInfo` and downstream consumption by `PndAnaWithTrigger`. | Includes variants about this producer-container-consumer contract and its per-mode/total tag representation. |
| `novel_dev` | `n029` | `nf029` | Explain how `PndRingSorter` buckets interleaved timestamped data and flushes cells in processing order. | Includes variants about this ring buffer's time-cell insertion, ordered multimap output, wraparound, and covered time span. |
| `novel_dev` | `n030` | `nf030` | Explain why the laboratory frame is insufficient for the luminosity fit and how IP alignment restores the required azimuthal symmetry. | Includes variants about measuring the mean POCA-based interaction point and globally transforming track data to the fit origin. |
| `novel_dev` | `n031` | `nf031` | Distinguish PandaRoot background, channel-specific, and particle-gun generator categories and identify the current background standard. | Includes variants asking for this generator taxonomy and the roles of FTF, DPM, EvtGen, BoxGenerator, and FixStepParticleGun. |

## Active `novel_validation` families (15)

| Split | Question | Family | Minimum information need | Semantic-family boundary |
|---|---|---|---|---|
| `novel_validation` | `n901` | `vf001` | Explain how an external package connects to installed PandaRoot, FairRoot, and VMC and where the example installs by default. | Includes variants about `PandaRootConfig.sh -a`, `FindPandaROOT.cmake`, `PandaRootSetup`, `pandaroot_setup()`, and this external-package installation boundary. |
| `novel_validation` | `n902` | `vf002` | Configure RHO charged-kaon selection with charge, probability threshold, detector algorithm, and multi-algorithm combination. | Includes variants about `FillList` selection-key semantics and the multiplicative combination of named PID algorithms. |
| `novel_validation` | `n903` | `vf003` | Diagnose where a simulated decay channel is lost using the two-stage MCTrackAnalysis enrichment and declarative requirements workflow. | Includes variants about attaching `PndMCTrackInfo`, expressing particle/mother/reconstruction requirements, and reporting the failed requirement position. |
| `novel_validation` | `n904` | `vf004` | Trace EMC digis into connected clusters and explain why local maxima require a later bump-splitting stage with shared-digi accounting. | Includes variants about the responsibility boundary between `PndEmcMakeCluster` and `PndEmcExpClusterSplitter`. |
| `novel_validation` | `n905` | `vf005` | Explain how `PndTrackArrayMerger` validates multiple input branches and produces its default merged `PndTrack` output. | Includes variants about accepted branch types, missing/wrong-type handling, `ALLTracks`, persistence, and per-event absorption. |
| `novel_validation` | `n906` | `vf006` | Reject generated events before transport using the filtered primary generator and configure the example's minimum-four-charged-particle filter. | Includes variants about the MasterTasks pre-transport event-filter attachment and this single-particle-count condition. |
| `novel_validation` | `n907` | `vf007` | Compare Barrel and Endcap Disc DIRC radiator/readout geometry, angular coverage, and pion-kaon momentum reach. | Includes variants requiring this complementary detector comparison across geometry, acceptance, and separation range. |
| `novel_validation` | `n908` | `vf008` | Trace `PndPidCorrelator` from input `PndTrack` to `PidChargedCand` and explain track-type-dependent detector attachment. | Includes variants about preserving track association and choosing barrel, forward, or combined detector-info sets during candidate construction. |
| `novel_validation` | `n909` | `vf009` | Explain ordered field-piece selection in `PndMultiField` and local-grid interpolation by the chosen `PndFieldMap`. | Includes variants requiring both first-matching z-range precedence and the selected map's coordinate transform, bounds, and eight-corner interpolation. |
| `novel_validation` | `n910` | `vf010` | Identify the MVD/GEM hit track finder, its output branches, and how detector hit provenance is preserved in each candidate. | Includes variants about `PndMvdGemTrackFinderOnHits`, `MVDGEMTrack`/`MVDGEMTrackCand`, and branch-ID plus hit-index links. |
| `novel_validation` | `n911` | `vf011` | Build nested J/psi and psi(2S) RHO candidates, apply a mass selector, and prevent daughter reuse or double counting. | Includes variants about `RhoCandList::Combine`, optional explicit combination loops, mass-window selection, and overlap protection for this composition workflow. |
| `novel_validation` | `n912` | `vf012` | Explain how the iron/MDT range system separates pions from muons and which layered-depth observable it reconstructs. | Includes variants connecting differing pion/muon material interactions to the interleaved absorber/MDT range measurement. |
| `novel_validation` | `n913` | `vf013` | Create dynamic candidate-level `RhoTuple` rows with consistent defaults and correctly commit and persist the finished tree. | Includes variants about first-use branch creation, missing-value defaults, `DumpData`, and writing the internal tree. |
| `novel_validation` | `n914` | `vf014` | Trace a custom runtime-parameter set through serialization, factory registration/context creation, and task retrieval/reinitialization. | Includes variants about the responsibility chain among `PndTutPar`, `PndTutContFact`, and `PndTutAccessRTDBTask`. |
| `novel_validation` | `n915` | `vf015` | Explain how coherent interference in DalitzGUI changes one-dimensional projections while a two-dimensional band remains visible, and identify the comparison views. | Includes variants about amplitude phase interference, reflections, and the coherent/incoherent/difference/phase projection views used to expose it. |

## Historical withdrawn `novel_dev` lineages (3)

| Question | Family | Status | Reuse policy |
|---|---|---|---|
| `n011` | `nf011` | Withdrawn/inactive. | Never reusable. |
| `n012` | `nf012` | Withdrawn/inactive. | Never reusable. |
| `n013` | `nf013` | Withdrawn/inactive. | Never reusable. |

## Count declaration

- Active `novel_dev` families: 28
- Active `novel_validation` families: 15
- Active total: 43
- Historical withdrawn `novel_dev` lineages: 3

This reference is used only after a source-first candidate exists, to decide
whether another question would express the same semantic family. It provides
no direction about what future candidates to create.
