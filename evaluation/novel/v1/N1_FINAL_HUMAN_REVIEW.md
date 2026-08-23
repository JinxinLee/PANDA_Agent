# N1 Final Human Review

## Review boundary

This document records the explicit human decisions for the 16 active N1
Novel-Dev pilot items. Codex recommendations remain advisory only. Human reviewer
Li accepted 14 items in the initial review and requested revisions to n002 and
n008; after the requested corrections were implemented, Li re-reviewed both
items and accepted them. All 16 active items are now human-accepted and the
pilot is frozen.

- Initial curation baseline: `166c3f93d6640e5f150af3959d6c2330b8072de0`
- Human-decision package baseline: `5c1714bf9485f8f3e72e1d2bbb855104f0d2de8f`
- Active set: n001-n010 and n014-n019 (16 questions, 16 semantic families)
- Retired drafts: n011/nf011, n012/nf012, and n013/nf013 remain withdrawn
- Human reviewer identity: **Li**
- Initial human review timestamp: **2026-08-24T00:28:55+02:00**
- Human re-review timestamp (n002, n008): **2026-08-24T00:49:13+02:00**
- Formal human decisions recorded: **16** (14 initial ACCEPT + 2 re-review ACCEPT)

The two requested revisions were applied in the draft dataset, Li re-reviewed
the corrected versions, and both re-review decisions are explicit `ACCEPT`. All
16 accepted items now carry approved review metadata and `split_frozen`
lifecycle.

## Item review sheets

### n001 / nf001

- **Question:** I am building the RestgasDetermination fork on the GSI cluster.
  Which FairSoft/FairRoot pairs and paths are encoded in configSettings.sh,
  which environment variables does it assign, and what does the script actually
  do for unmatched input as written?
- **Intent:** `installation`
- **Primary task archetype:** `setup_environment`
- **Expected status:** `answered`
- **Difficulty:** `simple`
- **Selection class:** `representative`
- **Required answer points:** The nominal branches encode FairSoft `may16p1`
  with FairRoot `v-17.10b` and FairSoft `oct17` with FairRoot `dev`, including
  placeholder build/install paths. They export `SIMPATH` and `FAIRROOTPATH`.
  Because the bracket tests omit spaces around `==`, the first nonempty test is
  true in Bash; the nominal fallback only echoes values and does not enforce
  failure.
- **Critical evidence:** locked RestgasDetermination `configSettings.sh` and
  `INSTALL.GSI`.
- **Novelty rationale:** Exposed installation cases cover upstream PandaRoot
  documentation, not this fork-level script's version branches and actual shell
  behavior.
- **Representativeness rationale:** Environment pinning and setup-script
  behavior are plausible GSI build tasks analogous to exposed prerequisite
  questions.
- **Known historical repairs:** Corrected the shell-test semantics, fallback
  semantics, and workflow source-type classification.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n002 / nf002

- **Question:** What Python packages does the LuminosityFit repository declare
  in its Python requirements/tooling list, and where is that list located?
- **Intent:** `installation`
- **Primary task archetype:** `setup_environment`
- **Expected status:** `answered`
- **Difficulty:** `simple`
- **Selection class:** `representative`
- **Required answer points:** The repository's declared Python
  requirements/tooling list is `requirements.txt`. It lists `autopep8`, `attrs`,
  `black`, `cattrs`, `flake8`, `isort`, `mypy`, `pycodestyle`, `pytest`,
  `python-dotenv`, `uproot`, and `awkward`. The file does not establish that
  every entry is required at runtime by every analysis script or classify the
  entries by role.
- **Critical evidence:** locked LuminosityFit `requirements.txt`.
- **Novelty rationale:** No exposed case asks for LuminosityFit's repository-level
  Python requirements/tooling declaration.
- **Representativeness rationale:** Identifying a repository's declared Python
  requirements/tooling list is a plausible setup task with a direct exposed
  benchmark analogue.
- **Known historical repairs:** Removed unsupported runtime/development and
  package-role inferences.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT` (initial review: `REVISE`)
- **Human notes:** Initial review requested treating `requirements.txt` as the
  repository's declared Python requirements/tooling list, not as proof that
  every listed package is required by the analysis scripts. The requested
  correction was implemented; human reviewer Li re-reviewed the corrected
  version on 2026-08-24T00:49:13+02:00 and accepted it.

### n003 / nf003

- **Question:** For an acceptance scan I need single particles whose momentum
  and polar angle advance in fixed steps from one event to the next. Which
  PandaRoot event generator supports this, and how is the stepping configured?
- **Intent:** `usage`
- **Primary task archetype:** `component_usage`
- **Expected status:** `answered`
- **Difficulty:** `moderate`
- **Selection class:** `representative`
- **Required answer points:** `PndFixStepParticleGun` supports the scan;
  `SetPRange` and `SetThetaRange` configure start/stop/step values; `ReadEvent`
  calls `CalcActValues`, whose nested range progression increments and rolls
  over after the first event.
- **Critical evidence:** locked PandaRoot
  `pgenerators/particleguns/PndFixStepParticleGun.h/.cxx` and the corresponding
  locked documentation page.
- **Novelty rationale:** The exposed generator case concerns DPM selection, not
  fixed-step scan configuration or per-event range progression.
- **Representativeness rationale:** Momentum and angular scans are standard
  acceptance and efficiency study operations.
- **Known historical repairs:** Added implementation evidence and an explicit
  description of `CalcActValues` progression.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n004 / nf004

- **Question:** While debugging a running PandaRoot macro I want every log
  message to carry the severity and the file:line:function where it was emitted.
  How do I configure that, and what other logging controls does the framework
  documentation describe?
- **Intent:** `usage`
- **Primary task archetype:** `component_usage`
- **Expected status:** `answered`
- **Difficulty:** `simple`
- **Selection class:** `representative`
- **Required answer points:** Use `fair::Logger::SetVerbosity`; a
  `fair::VerbositySpec::Make(severity, file_line_function)` specification emits
  severity and source provenance. The documentation also describes console
  color and warns against retaining color escape sequences in file logs.
- **Critical evidence:** locked PandaRoot `Running/Logging.html` documentation.
- **Novelty rationale:** Runtime logging and provenance formatting are absent
  from exposed questions.
- **Representativeness rationale:** Logging configuration is a routine macro
  debugging operation.
- **Known historical repairs:** None after the prior static review; retained as
  the unchanged control item.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n005 / nf005

- **Question:** After running a simulation I would rather look at the events and
  the detector geometry than at histograms. What does PandaRoot provide for
  this, and how do I get my file open in it?
- **Intent:** `usage`
- **Primary task archetype:** `component_usage`
- **Expected status:** `answered`
- **Difficulty:** `moderate`
- **Selection class:** `representative`
- **Required answer points:** PandaRoot's FairEventDisplay/EVE-based event
  display renders geometry and reconstruction-stage objects. Run
  `macro/tools/eventDisplay.C` with the shared file prefix; the macro defaults
  to `../data/evtcomplete`, adds sim/digi/reco friend stages, and passes the
  prefix through `PndMasterRunAna::Setup` before display startup.
- **Critical evidence:** locked `EventDisplay/EventDisplay.html` and PandaRoot
  `macro/tools/eventDisplay.C`.
- **Novelty rationale:** Visualization tooling and its file-opening convention
  are not covered by exposed cases.
- **Representativeness rationale:** Event and geometry inspection is a plausible
  documented component-usage task.
- **Known historical repairs:** Replaced the earlier vague file-opening claim
  with the macro's actual shared-prefix and friend-stage behavior.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n006 / nf006

- **Question:** My analysis chain produces sim, digi, reco and pid files and I
  keep concatenating the stage names by hand. Does PandaRoot ship a helper that
  derives all these file names from the simulation file name, and which stage
  extensions does it define?
- **Intent:** `api`
- **Primary task archetype:** `component_usage`
- **Expected status:** `answered`
- **Difficulty:** `moderate`
- **Selection class:** `representative`
- **Required answer points:** `PndFileNameCreator` derives chain filenames and
  `GetCustomFileName` appends or replaces an extension. The implementation
  defines `par`, `sim`, `digi`, `reco`, `pid`, `trackF`, `idealTrackF`,
  `riemann`, `combRiemann`, `kalman`, and `vertex` suffixes.
- **Critical evidence:** locked PandaRoot `tools/PndFileNameCreator.h/.cxx` and
  matching documentation.
- **Novelty rationale:** This reusable chain-naming API is distinct from exposed
  single-artifact source-location questions.
- **Representativeness rationale:** Managing repeated stage filenames is a
  recurring practical analysis-chain task.
- **Known historical repairs:** Added the implementation source needed to
  support the concrete suffix inventory.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n007 / nf007

- **Question:** The MVD hits I read back from a file contain shortIDs instead of
  readable geometry paths. How can I resolve a shortID to the full detector path
  at analysis time, and what state must be initialized first?
- **Intent:** `api`
- **Primary task archetype:** `component_usage`
- **Expected status:** `answered`
- **Difficulty:** `moderate`
- **Selection class:** `representative`
- **Required answer points:** `PndGeoHandling::GetPath(Int_t)` performs the
  lookup and `GetShortID(TString)` provides the reverse mapping. Translation
  requires initialized `TGeoManager` and `PndSensorNamePar` state; the helper
  must be constructed during `SetParContainers` when parameter-database names
  are required.
- **Critical evidence:** locked PandaRoot `tools/PndGeoHandling.h` and matching
  documentation.
- **Novelty rationale:** The active shortID lookup API and initialization state
  are distinct from exposed detector-coordinate concepts.
- **Representativeness rationale:** Geometry-identifier decoding is a plausible
  MVD analysis task, although narrower than general analysis usage.
- **Known historical repairs:** Removed retired encrypted-path material and
  isolated the supported shortID API.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n008 / nf008

- **Question:** Before tracks can be fitted in the luminosity detector, the hits
  have to be grouped into track candidates. Which track-search approaches were
  developed for the LMD, and how do they compare?
- **Intent:** `algorithm_theory`
- **Primary task archetype:** `concept_comparison`
- **Expected status:** `answered`
- **Difficulty:** `moderate`
- **Selection class:** `representative`
- **Required answer points:** The LMD study developed track-following and
  cellular-automaton approaches. Its low hit count requires using all hits, and
  the comparison seeks to minimize both missed and fake tracks because both
  distort the reconstructed theta distribution used for luminosity. For the
  studied low-momentum, high-multiplicity cases at 1.5 GeV/c, the Cellular
  Automaton has significantly smaller track losses and handles high-multiplicity
  events better than Track Following; at 15 GeV/c their performance is similar.
- **Critical evidence:** locked Karavdina 2015 thesis, pages 72-78.
- **Novelty rationale:** Exposed LMD cases concern back-propagation, not
  hit-to-candidate track search or these two approaches.
- **Representativeness rationale:** Track-search strategy is a meaningful LMD
  reconstruction concept with an exposed concept-comparison analogue.
- **Known historical repairs:** The earlier Gold range was corrected to pages
  72-77; human review then requested the directly supported performance
  comparison, requiring a minimal extension through page 78.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT` (initial review: `REVISE`)
- **Human notes:** Initial review requested adding the thesis-supported
  conclusion that Cellular Automaton handles the studied low-energy/
  high-multiplicity cases better than Track Following. The correction and the
  page-78 evidence extension (locked selector now pages 72-78) were implemented;
  human reviewer Li re-reviewed the corrected version on
  2026-08-24T00:49:13+02:00 and accepted it.

### n009 / nf009

- **Question:** The luminosity fit leans on an elastic-scattering model. Besides
  DPM, which alternative was studied for PANDA luminosity, does it also exist as
  LuminosityFit code, and what does the thesis say about its intrinsic parameter
  uncertainty and the added beam-momentum uncertainty?
- **Intent:** `algorithm_theory`
- **Primary task archetype:** `theory_explanation`
- **Expected status:** `answered`
- **Difficulty:** `hard`
- **Selection class:** `representative`
- **Required answer points:** The alternative is E760 and corresponding E760
  and E760-like model code exists. For intrinsic parameter uncertainty,
  `sigma_T` and `rho` dominate at small `|t|`, `b` at large `|t|`, and the
  integrated uncertainty is below 0.5% over 2-8 GeV/c. Beam-momentum uncertainty
  is separate: near 5 GeV/c, `Delta P/P` around `10^-5` adds below 0.005%.
- **Critical evidence:** locked Karavdina 2015 thesis uncertainty sections and
  locked LuminosityFit `PndLmdE760ModelParametrization.cxx` and
  `PndLmdE760LikeModelParametrization.cxx`.
- **Novelty rationale:** The E760 choice, its uncertainty composition, and code
  existence are not the DPM-purpose information need measured by exposed Gold.
- **Representativeness rationale:** Model choice and systematic uncertainty are
  core luminosity-analysis concerns; evidence composition raises difficulty but
  does not make the task exploratory.
- **Known historical repairs:** Corrected the intrinsic-versus-beam uncertainty
  scope, dominant parameters, ranges, and numerical statements.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n010 / nf010

- **Question:** Full GEANT transport is too slow for my feasibility study of an
  analysis selection. How does PandaRoot's fast simulation produce detector
  responses instead, and which building blocks is it made of?
- **Intent:** `algorithm_implementation`
- **Primary task archetype:** `implementation_explanation`
- **Expected status:** `answered`
- **Difficulty:** `hard`
- **Selection class:** `representative`
- **Required answer points:** `PndFastSim` makes candidates from simulated
  particles, collects parameterized detector responses, combines them, and
  applies acceptance cuts and smearing. `PndFsmAbsDet::respond` is the detector
  contract, `PndFsmDetFactory` resolves named detectors, and `PndFsmResponse`
  carries detection, resolution/smearing, and detector/PID values. Efficiency
  belongs to `PndFsmAbsDet`, not `PndFsmResponse`.
- **Critical evidence:** locked PandaRoot `fastsim/PndFastSim.cxx`,
  `PndFsmAbsDet.h`, `PndFsmDetFactory.cxx`, and `PndFsmResponse.h`.
- **Novelty rationale:** No exposed case covers the fast-simulation response
  pipeline.
- **Representativeness rationale:** Parameterized simulation is a mainstream
  feasibility-study mechanism and matches exposed implementation-explanation
  forms.
- **Known historical repairs:** Corrected response-versus-efficiency ownership
  and removed an unnecessary broader subsystem inventory.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n014 / nf014

- **Question:** LuminosityFit has a model_framework directory and a native
  model/ directory. What does the repository explicitly say model_framework is,
  and what role does model/PndLmdModelFactory expose?
- **Intent:** `module_structure`
- **Primary task archetype:** `repository_structure`
- **Expected status:** `answered`
- **Difficulty:** `moderate`
- **Selection class:** `representative`
- **Required answer points:** The README calls `model_framework` a working copy
  of the archived ModelFramework without establishing a full architecture. The
  native `PndLmdModelFactory` header exposes the user-facing model factory and
  its general and 1D/2D generation helpers, combining framework model types with
  LuminosityFit data.
- **Critical evidence:** locked LuminosityFit `model_framework/README.md` and
  `model/PndLmdModelFactory.h`.
- **Novelty rationale:** The precise directory boundary differs from the exposed
  question about model-layer component composition.
- **Representativeness rationale:** Newcomers plausibly need to distinguish the
  framework working copy from the native factory entry point.
- **Known historical repairs:** Removed unsupported architecture and component
  inventory claims; retained only facts directly exposed by the two files.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n015 / nf015

- **Question:** Configuring PandaRoot on an ARM machine, cmake fails while
  compiling the legacy VC package. What does the documentation suggest, and
  what does the workaround disable as a side effect?
- **Intent:** `troubleshooting`
- **Primary task archetype:** `troubleshooting_diagnosis`
- **Expected status:** `answered`
- **Difficulty:** `moderate`
- **Selection class:** `representative`
- **Required answer points:** Configure with `cmake -DNOVC=1` to disable the
  legacy VC package; the documentation names Apple/ARM failures and notes macOS
  automatic handling. The workaround also disables `CAtracking` and
  `FtsCATracking` because they depend on that VC version.
- **Critical evidence:** locked PandaRoot
  `Installation/Troubleshooting.html`.
- **Novelty rationale:** Exposed troubleshooting cases concern runtime or
  analysis artifacts, not this configure-time failure and side effect.
- **Representativeness rationale:** Build failures and documented workarounds
  are natural PandaRoot support tasks.
- **Known historical repairs:** Removed an unsupported empirical-frequency
  claim from the representativeness rationale.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n016 / nf016

- **Question:** Do the locked PandaRoot Docker pages establish that the
  documented containers can run natively on a Windows host, and what host
  environment do their examples actually demonstrate?
- **Intent:** `troubleshooting`
- **Primary task archetype:** `setup_environment`
- **Expected status:** `insufficient_evidence`
- **Difficulty:** `simple`
- **Selection class:** `representative`
- **Required answer points:** The locked pages do not establish native Windows
  support or provide a Windows procedure. Their `/cvmfs`, Unix UID/GID,
  `/tmp/.X11-unix`, and Singularity/HPC examples are Unix-oriented; this does
  not prove Windows is unsupported or that Linux is strictly required.
- **Critical evidence:** locked PandaRoot `Docker/Docker.html` and
  `Docker/DevelopingInContainer.html`.
- **Novelty rationale:** This is a distinct, grounded platform-support
  insufficiency case analogous to an exposed hardware-requirement refusal.
- **Representativeness rationale:** Platform compatibility is a plausible setup
  need, with Windows as the less common instance.
- **Known historical repairs:** Corrected “unsupported” into the evidenced
  “not documented/established” boundary.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n017 / nf017

- **Question:** When tracing the reconstructed-track object handed between
  PandaRoot tracking tasks, where is that persistent object defined, and which
  fitted endpoints and track-candidate links does it store?
- **Intent:** `api`
- **Primary task archetype:** `source_location`
- **Expected status:** `answered`
- **Difficulty:** `simple`
- **Selection class:** `representative`
- **Required answer points:** Persistent `PndTrack` is defined in
  `pnddata/TrackData/PndTrack.h` as a `FairTimeStamp`-derived object. It stores
  first/last fitted `FairTrackParP` parameters, an embedded `PndTrackCand`, an
  optional `TRef` and candidate reference index, plus PID, quality, chi2, NDF,
  and track type metadata.
- **Critical evidence:** locked PandaRoot `pnddata/TrackData/PndTrack.h`.
- **Novelty rationale:** The persistent reconstructed-track object and its
  boundary are absent from exposed source-location questions and are not a
  mechanical class substitution.
- **Representativeness rationale:** `PndTrack` is a common artifact exchanged by
  tracking tasks, making its definition and links a natural developer need.
- **Known historical repairs:** Independently sampled replacement for retired
  n013; it does not reuse n013's identity or failed information need.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n018 / nf018

- **Question:** In PandaRoot analysis, how can I inspect the Monte Carlo truth
  counterpart of a reconstructed candidate and check whether an entire
  reconstructed decay tree matches the generated one?
- **Intent:** `usage`
- **Primary task archetype:** `component_usage`
- **Expected status:** `answered`
- **Difficulty:** `moderate`
- **Selection class:** `representative`
- **Required answer points:** Call `RhoCandidate::GetMcTruth()` and check its
  pointer because noise-only tracks may lack a counterpart. Use
  `PndAnalysis::McTruthMatch(candidate)` for a full decay tree; assign intended
  particle types during combinatorics and load the EvtGen PDG table so codes
  agree.
- **Critical evidence:** locked PandaRoot Monte Carlo Truth Match tutorial.
- **Novelty rationale:** No exposed usage case asks for candidate-level truth
  access or arbitrary reconstructed-tree truth matching.
- **Representativeness rationale:** Candidate and decay-tree truth checks are
  routine analysis operations directly supported by the tutorial.
- **Known historical repairs:** New n018/nf018 identity created after the
  information need changed from withdrawn n011; unsupported cross-stage trace
  claims were removed.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

### n019 / nf019

- **Question:** How does PndRecoKalmanTask turn input PndTrack objects into
  fitted output tracks, including fitter selection, particle-hypothesis choice,
  and the construction of each persisted result?
- **Intent:** `algorithm_implementation`
- **Primary task archetype:** `implementation_explanation`
- **Expected status:** `answered`
- **Difficulty:** `moderate`
- **Selection class:** `representative`
- **Required answer points:** `Init` configures Kalman or DAF, track
  representation, propagation, input, and output. `Exec` clears output, applies
  the busy-track cut, and selects a configured/charge-adjusted or MC-derived PDG
  hypothesis with pion fallbacks. For a nonzero selected PDG hypothesis, the
  configured fitter produces the fitted track; the task constructs the output
  `PndTrack` from endpoints, candidate, quality, chi2, NDF, and PID hypothesis,
  passing the input index and input-branch ID to that constructor.
- **Critical evidence:** locked PandaRoot
  `tracking/GenfitTools/recotasks/PndRecoKalmanTask.h/.cxx`.
- **Novelty rationale:** No exposed case covers this task's fitter dispatch,
  hypothesis selection, and fitted-output construction pipeline.
- **Representativeness rationale:** Fitting finder-produced tracks and creating
  persistent fitted output is a core reconstruction implementation need.
- **Known historical repairs:** Independently sampled replacement for withdrawn
  n012. Final pre-review correction makes fitter execution conditional on a
  nonzero selected PDG hypothesis and describes index/branch ID as constructor
  arguments rather than generic recorded state.
- **Codex recommendation:** `RECOMMEND_ACCEPT`
- **Human decision:** `ACCEPT`
- **Human notes:**

## Decision matrix

| ID | Codex recommendation | Human decision | Human notes |
|---|---|---|---|
| n001 | RECOMMEND_ACCEPT | ACCEPT | |
| n002 | RECOMMEND_ACCEPT | ACCEPT | Initial `REVISE` corrected; Li re-reviewed and accepted on 2026-08-24T00:49:13+02:00. |
| n003 | RECOMMEND_ACCEPT | ACCEPT | |
| n004 | RECOMMEND_ACCEPT | ACCEPT | |
| n005 | RECOMMEND_ACCEPT | ACCEPT | |
| n006 | RECOMMEND_ACCEPT | ACCEPT | |
| n007 | RECOMMEND_ACCEPT | ACCEPT | |
| n008 | RECOMMEND_ACCEPT | ACCEPT | Initial `REVISE` corrected (answer point + pages 72-78); Li re-reviewed and accepted on 2026-08-24T00:49:13+02:00. |
| n009 | RECOMMEND_ACCEPT | ACCEPT | |
| n010 | RECOMMEND_ACCEPT | ACCEPT | |
| n014 | RECOMMEND_ACCEPT | ACCEPT | |
| n015 | RECOMMEND_ACCEPT | ACCEPT | |
| n016 | RECOMMEND_ACCEPT | ACCEPT | |
| n017 | RECOMMEND_ACCEPT | ACCEPT | |
| n018 | RECOMMEND_ACCEPT | ACCEPT | |
| n019 | RECOMMEND_ACCEPT | ACCEPT | |

## Human decision counts

- Codex `RECOMMEND_ACCEPT`: 16
- Codex `RECOMMEND_REVISE`: 0
- Codex `RECOMMEND_REJECT`: 0
- Human `ACCEPT`: 16 (14 initial + 2 re-review)
- Human `REVISE`: 0
- Human `REJECT`: 0
- Human `PENDING`: 0

## Static-review conclusion

The initial review (2026-08-24T00:28:55+02:00) accepted 14 items and requested
revision of n002 and n008. Both requested content corrections were applied
within their original semantic families, and Li explicitly re-reviewed and
accepted the corrected versions on 2026-08-24T00:49:13+02:00. All 16 active
items are human-approved with `split_frozen` lifecycle; the pilot is frozen and
N1 is complete. Retired drafts n011/nf011, n012/nf012, and n013/nf013 remain
withdrawn historical records and are not part of the frozen active set.
