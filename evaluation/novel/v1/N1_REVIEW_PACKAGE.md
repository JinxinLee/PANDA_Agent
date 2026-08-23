# N1 Review Package — novel-v1-n1-pilot-draft

16 candidate `novel_dev` questions (`n001`-`n016`), each an independent
curation family (`nf001`-`nf016`), curated without running PANDA Agent and
without observing any system outcome (`agent_outcome_seen_before_freeze:
false`, `evidence_selected_from_agent_output: false` for every record).

All evidence was established by static inspection of the locked corpus
(repositories at locked commits, thesis PDFs, Sphinx snapshot) using
deterministic search only.

**Every ACCEPT / REVISE / REJECT below is a Codex curator recommendation
only. Human decision: PENDING for all 16 candidates.**

Quick table:

| ID | Intent | Novelty | Difficulty | Family | Expected Status | Codex Recommendation |
|------|-------------------------|------------------------------------|------------|--------|------------------------|----------------------|
| n001 | installation | entity | simple | nf001 | answered | ACCEPT |
| n002 | installation | entity | simple | nf002 | answered | ACCEPT |
| n003 | usage | entity, relation | simple | nf003 | answered | ACCEPT |
| n004 | usage | entity, task_form | simple | nf004 | answered | ACCEPT |
| n005 | usage | entity, nontrivial_expression | simple | nf005 | answered | ACCEPT |
| n006 | api | entity, task_form | moderate | nf006 | answered | ACCEPT |
| n007 | api | entity, relation, nontrivial_expression | moderate | nf007 | answered | ACCEPT |
| n008 | algorithm_theory | entity, reasoning_topology, nontrivial_expression | moderate | nf008 | answered | ACCEPT |
| n009 | algorithm_theory | relation, composition, reasoning_topology | hard | nf009 | answered | ACCEPT |
| n010 | algorithm_implementation | entity, composition | moderate | nf010 | answered | ACCEPT |
| n011 | data_flow | entity, reasoning_topology | moderate | nf011 | answered | ACCEPT |
| n012 | data_flow | relation, composition, reasoning_topology | hard | nf012 | answered | ACCEPT |
| n013 | module_structure | composition, reasoning_topology | moderate | nf013 | ACCEPT (see concern) |
| n014 | module_structure | entity, relation | moderate | nf014 | ACCEPT (see concern) |
| n015 | troubleshooting | task_form, composition | moderate | nf015 | answered | ACCEPT |
| n016 | troubleshooting | failure_mode | simple | nf016 | insufficient_evidence | ACCEPT |

---

## n001 — restgas fork GSI environment pinning

**Question:** I am building the RestgasDetermination fork on the GSI cluster.
Which FairSoft and FairRoot version combinations does its setup script
recognize, and which environment variables am I expected to export for the
external packages?

**Intent:** installation
**Expected status:** answered

**Why this is novel:** all 12 exposed installation questions target the
upstream PandaRoot documentation; the fork's own environment pinning (which
FairSoft/FairRoot pairs `configSettings.sh` accepts, SIMPATH/FAIRROOTPATH) is
an unexposed fork-level need.

**Closest Gold:** g002 (documented build prerequisites, upstream docs) — same
intent, different source and information need.

**Required answer:**
- p1: two recognized pairs — FairSoft may16p1 + FairRoot v-17.10b, FairSoft
  oct17 + FairRoot dev; anything else errors out.
- p2: the environment is defined by SIMPATH (external FairSoft packages) and
  FAIRROOTPATH (FairRoot installation).

**Gold evidence:**
- e1: `restgas_determination/configSettings.sh` — the version-pair branches
  and the error path.
- e2: `restgas_determination/configSettings.sh` (alternative:
  `INSTALL.GSI`) — SIMPATH/FAIRROOTPATH export lines. See curation note 6:
  `INSTALL.GSI` is in the locked repo but absent from the current
  KnowledgeObject decomposition, so `configSettings.sh` is the primary
  selector.

**Coverage:** single repo (restgas fork), code, descriptive, single-hop, simple.
**Difficulty:** simple.
**Potential concern:** none; both files are small and unambiguous.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n002 — LuminosityFit Python dependencies

**Question:** What Python packages do the LuminosityFit analysis scripts
expect, and where in the repository are they declared?

**Intent:** installation
**Expected status:** answered

**Why this is novel:** no exposed case covers LuminosityFit's Python-level
dependency stack; exposed usage questions enter at the C++/macro workflow
level (createLmdFitData, runLmdFit).

**Closest Gold:** g002 (upstream build prerequisites) — different repository
and layer.

**Required answer:**
- p1: declared in `requirements.txt` — uproot and awkward for columnar ROOT
  data, python-dotenv, plus dev tooling (black, flake8, mypy, pytest, ...).
- p2: `python/Readme.md` documents the script workflow these support.

**Gold evidence:**
- e1: `luminosityfit/requirements.txt`.
- e2: `luminosityfit/python/Readme.md`.

**Coverage:** single repo (luminosityfit), code, descriptive, single-hop, simple.
**Difficulty:** simple.
**Potential concern:** answer point p1 enumerates representative packages; the
reviewer may prefer the full list verbatim.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n003 — fixed-step particle gun for acceptance scans

**Question:** For an acceptance scan I need single particles whose momentum
and polar angle advance in fixed steps from one event to the next. Which
PandaRoot event generator supports this, and how is the stepping configured?

**Intent:** usage
**Expected status:** answered

**Why this is novel:** g016 selects DPM; the generator-choice need here is a
different entity (fixed-step scanning gun) with distinct stepping semantics
(range start/stop/step) for an acceptance-scan purpose.

**Closest Gold:** g016 — same task family (choose a generator), different
generator and behavior.

**Required answer:**
- p1: `PndFixStepParticleGun` (a `PndTargetGenerator` subclass).
- p2: `SetPRange(pmin, pmax, pstep)` and `SetThetaRange(min, max, step)`.

**Gold evidence:**
- e1: `pandaroot/pgenerators/particleguns/PndFixStepParticleGun.h`
  (alternative: Sphinx `EventGenerators/FixStepParticleGun.html`, which is
  generated from this header).

**Coverage:** pandaroot, code+documentation, descriptive, single-hop, simple.
**Difficulty:** simple.
**Potential concern:** none.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n004 — logger verbosity with file:line:function

**Question:** While debugging a running PandaRoot macro I want every log
message to carry the severity and the file:line:function where it was
emitted. How do I configure that, and what other logging controls does the
framework documentation describe?

**Intent:** usage
**Expected status:** answered

**Why this is novel:** no exposed question touches runtime logging or the
fair logger API; the operation (configure per-message provenance) is an
unexposed task form.

**Closest Gold:** none_found — no exposed case concerns logging/verbosity.

**Required answer:**
- p1: `fair::Logger::SetVerbosity` with predefined levels (verylow..veryhigh)
  or custom user1-4 specs; a `fair::VerbositySpec::Make(severity,
  file_line_function)` spec yields `[severity][file:line:function]`.
- p2: `SetConsoleColor(true)` for colored output; disable when logging to a
  file.

**Gold evidence:**
- e1: Sphinx `Running/Logging.html` ("Using the Logger from Fair" section).

**Coverage:** pandaroot documentation, implementation-oriented, single-hop,
simple.
**Difficulty:** simple.
**Potential concern:** none.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n005 — visualizing events and geometry (event display)

**Question:** After running a simulation I would rather look at the events and
the detector geometry than at histograms. What does PandaRoot provide for
this, and how do I get my file open in it?

**Intent:** usage
**Expected status:** answered

**Why this is novel:** visualization tooling is absent from the exposed set,
and the question is deliberately identifier-free (no class names), exercising
descriptive recognition.

**Closest Gold:** g010 ("Is a Jupyter-based PandaRoot workflow documented,
and where?") — structurally similar "is X documented" form, different
subsystem.

**Required answer:**
- p1: an event display based on FairEventDisplay/EVE renders the detector
  geometry and reconstruction-stage data objects.
- p2: events are browsed via the EVE browser / FairEventManager (Update
  button or Current Event selector); disable or make geometry transparent
  while browsing.

**Gold evidence:**
- e1: Sphinx `EventDisplay/EventDisplay.html`.
- e2: Sphinx `EventDisplay/EventDisplay_Events.html` (alternative:
  `EventDisplay_DetectorGeometry.html`).

**Coverage:** pandaroot documentation, descriptive/identifier-free,
single-hop, simple.
**Difficulty:** simple.
**Potential concern:** "how do I get my file open" is answered at the level
the documentation supports (macro start / Eve browser); reviewer should
confirm this satisfies the phrasing.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n006 — deriving stage file names (PndFileNameCreator)

**Question:** My analysis chain produces sim, digi, reco and pid files and I
keep concatenating the stage names by hand. Does PandaRoot ship a helper that
derives all these file names from the simulation file name, and which stage
extensions does it define?

**Intent:** api
**Expected status:** answered

**Why this is novel:** exposed api questions locate specific artifacts
(g036/g037: event_poca producer/consumer macros); this asks for the general
naming utility across the whole simulation chain — a reusable tool-lookup
need.

**Closest Gold:** g036/g037 — locator-style questions about single artifacts.

**Required answer:**
- p1: `PndFileNameCreator` appends predefined stage extensions to the
  simulation file name; `GetCustomFileName` for custom stages; `cut` replaces
  an existing trailing extension.
- p2: extensions cover parameter, sim, digi, reco, pid, track-finding,
  Riemann, combined-Riemann, ideal-track-finding, Kalman, and vertex stages.

**Gold evidence:**
- e1: `pandaroot/tools/PndFileNameCreator.h` (alternative: Sphinx
  `Tools/PndFileNameCreator.html`).

**Coverage:** pandaroot, code+documentation, implementation-oriented,
single-hop, moderate (extension vocabulary spans many stages).
**Difficulty:** moderate.
**Potential concern:** p2 lists many getters; reviewer may trim to the stages
the question names (sim/digi/reco/pid) plus a representative extra.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n007 — decoding compact MVD volume identifiers

**Question:** The MVD hits I read back from a file contain compact volume
identifiers instead of readable volume paths. How can I translate such an
identifier into the full detector path at analysis time, and what does that
translation need?

**Intent:** api
**Expected status:** answered

**Why this is novel:** identifier-free runtime question about the
shortID-to-geometry-path relation and its TGeoManager/parameter-container
preconditions; the exposed coordinate-transformation question (g056) is about
LuminosityFit model theory, a different layer.

**Closest Gold:** g056 — shares only the broad "coordinate/geometry" theme.

**Required answer:**
- p1: `PndGeoHandling` converts encrypted per-hit paths (e.g. `/1_1/34_2/101_1/`)
  or shortIds into full TGeoManager paths (`GetPath`, `GetShortID`).
- p2: needs an initialized TGeoManager (e.g. FAIRGeom file); for shortIds the
  sensor-name parameter container — hence create the instance in
  `SetParContainers` of a task.

**Gold evidence:**
- e1: `pandaroot/tools/PndGeoHandling.h` (alternative: Sphinx
  `Tools/PndGeoHandling.html`).

**Coverage:** pandaroot, code+documentation, descriptive/identifier-free,
single-hop, moderate.
**Difficulty:** moderate.
**Potential concern:** none.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n008 — LMD track-search algorithm comparison

**Question:** Before tracks can be fitted in the luminosity detector, the
hits have to be grouped into track candidates. Which track-search approaches
were developed for the LMD, and how do they compare?

**Intent:** algorithm_theory
**Expected status:** answered

**Why this is novel:** exposed LMD-reconstruction theory covers
back-propagation to the IP (g048/g054/g061/g062); track search (hit grouping)
and the track-following vs cellular-automaton comparison are unexposed, and
the question is identifier-free.

**Closest Gold:** g048 — adjacent reconstruction chain, different stage and
need.

**Required answer:**
- p1: two approaches — track following and cellular automaton — with a
  performance comparison.
- p2: LMD has few hits per track so all must be used (contrast: up to a
  hundred hits per track in general detectors).
- p3: quality goal is minimizing missed and fake tracks, which otherwise
  distort the reconstructed theta distribution the luminosity depends on.

**Gold evidence:**
- e1: `karavdina_2015` PDF pages 72-77 ("Track search", "Track Following",
  "Cellular Automaton", "Comparison of performance").

**Coverage:** paper, descriptive, comparison topology, single-source,
moderate.
**Difficulty:** moderate.
**Potential concern:** none.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n009 — elastic-model alternative and model uncertainty (E760)

**Question:** The luminosity fit leans on an elastic-scattering model.
Besides DPM, which alternative model was studied for PANDA luminosity, does
it also exist as code, and what dominates the model uncertainty?

**Intent:** algorithm_theory
**Expected status:** answered

**Why this is novel:** g047 asks DPM's theoretical purpose. This asks the
model-choice question: the studied alternative (E760), its presence as
LuminosityFit code, and the uncertainty budget (beam momentum uncertainty;
sub-2% in the Coulomb-dominated low-momentum regime) — a paper+code
composition need.

**Closest Gold:** g047 — shared background entity (DPM), different
information need (alternative + uncertainty + code presence).

**Required answer:**
- p1: E760 parametrization studied as the alternative; exists in code as
  `PndLmdE760ModelParametrization` (and an E760-like variant).
- p2: model uncertainty dominated by beam momentum uncertainty mapped onto
  momentum transfer; quantified as cross-section uncertainty in theta ranges.
- p3: below ~3.5 GeV/c (Coulomb-dominated) the expected uncertainty stays
  under roughly 2%.

**Gold evidence:**
- e1: `karavdina_2015` pages 50-53 (DPM) or 54-59 (E760) — the model
  alternatives.
- e2: `karavdina_2015` pages 61-62 — "Model uncertainty caused by the
  momentum uncertainty".
- e3: `luminosityfit/model/PndLmdE760ModelParametrization.cxx` (alternative:
  `PndLmdE760LikeModelParametrization.cxx`).

**Coverage:** paper+code (cross-source), single repository, comparison
topology, hard.
**Difficulty:** hard (three required groups, cross-source).
**Potential concern:** p3's numeric bound (2%, 3.5 GeV/c) comes from one
figure discussion; reviewer should confirm the wording matches the thesis
intent.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n010 — fast simulation building blocks

**Question:** Full GEANT transport is too slow for my feasibility study of an
analysis selection. How does PandaRoot's fast simulation produce detector
responses instead, and which building blocks is it made of?

**Intent:** algorithm_implementation
**Expected status:** answered

**Why this is novel:** the fastsim subsystem is entirely absent from the
exposed set; the question asks how parametrized responses replace transport
and how the components compose.

**Closest Gold:** none_found — no exposed case mentions fast simulation.

**Required answer:**
- p1: `PndFastSim` is a FairTask (PndPersistencyTask) applying parametrized
  detector responses instead of full transport.
- p2: detectors added via `AddDetector` (by name+params or as
  `PndFsmAbsDet` implementations): MVD, EMC, DIRC, STT, TOF, RICH, MDT, ...
- p3: per-detector `PndFsmResponse` objects are summed and applied to
  `PndFsmTrack` candidates (cut-and-smear), with split-off, neutral-cluster
  merging, and bremsstrahlung options.

**Gold evidence:**
- e1: `pandaroot/fastsim/PndFastSim.h`.
- e2: `pandaroot/fastsim/PndFsmAbsDet.h` (alternative: `PndFsmResponse.h`).

**Coverage:** pandaroot code, descriptive, single-hop, moderate.
**Difficulty:** moderate.
**Potential concern:** the subsystem list in p2 is read from the fastsim
directory contents; reviewer may prefer naming three representative
detectors.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n011 — MC truth from generation into analysis

**Question:** How does Monte Carlo truth information survive from the event
generator into my analysis, and how can I check whether a reconstructed decay
tree matches the generated one?

**Intent:** data_flow
**Expected status:** answered

**Why this is novel:** exposed data-flow questions trace specific restgas/LMD
artifacts; the generic MC-truth channel and the reconstructed-vs-generated
tree match are unexposed and span tutorial documentation plus the
PndMCTrackAna tooling (multi-hop).

**Closest Gold:** none_found — no exposed case covers MC-truth matching.

**Required answer:**
- p1: truth is retained via link machinery; the tutorial covers accessing MC
  truth, the full MC truth tree match, and the MC truth list.
- p2: `tools/PndMCTrackAna` (`PndMCTrackInfo`, `PndMCTrackInfoTask`) provides
  the track-level MC information such checks build on.

**Gold evidence:**
- e1: Sphinx `Tutorials/tut_02_04_analysis_mctruth.html` ("2.4. Monte Carlo
  Truth Match").
- e2: `pandaroot/tools/PndMCTrackAna/PndMCTrackInfo.h` (alternative:
  `PndMCTrackInfoTask.h`).

**Coverage:** documentation+code (cross-source), multi-hop, moderate.
**Difficulty:** moderate.
**Potential concern:** "link machinery" wording — the tutorial speaks of
FairLinks; reviewer may want the term stated explicitly in p1.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n012 — where alignment corrections come from

**Question:** The luminosity determination assumes the LMD geometry is
perfectly aligned. Where do alignment corrections come from before a
luminosity determination, and where do they enter the workflow?

**Intent:** data_flow
**Expected status:** answered

**Why this is novel:** alignment is absent from the exposed pipeline
questions (g079 traces Lumi_TrksQA onward; g091 orders fit ingredients); this
asks the producer (Millepede-based internal alignment in the thesis) and the
pipeline entry point (an alignment process ahead of the documented
LuminosityFit steps) — a cross-source producer-to-entry relation.

**Closest Gold:** g079 — same overall pipeline, alignment need not measured.

**Required answer:**
- p1: module misalignment degrades track reconstruction; internal alignment
  is constrained with Millepede, needing on the order of 10^4 tracks (a plain
  global matrix inversion at that size is infeasible).
- p2: LuminosityFit's python Readme notes a possible alignment process that
  should run before the IP-distribution and luminosity-determination steps.

**Gold evidence:**
- e1: `karavdina_2015` pages 114-129 ("Modules alignment", "Introduction to
  Millepede", misalignment limits).
- e2: `luminosityfit/python/Readme.md`.

**Coverage:** paper+code (cross-source), multi-hop, hard.
**Difficulty:** hard (cross-source, producer-to-pipeline reasoning).
**Potential concern:** the two evidence loci are from different documents and
different eras (2015 thesis vs current fork README); the reviewer should
confirm the composition reads as one coherent user need.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n013 — genfit, genfit2, genfit2-remote

**Question:** The PandaRoot source tree ships a genfit, a genfit2 and a
genfit2-remote directory. Which of them does a default build actually
compile, and what does the genfit2-remote recipe build?

**Intent:** module_structure
**Expected status:** answered

**Why this is novel:** GenFit and its three-directory layout appear nowhere
in the exposed set; the question asks a build-wiring comparison (default
add_subdirectory set vs the remote recipe's target).

**Closest Gold:** none_found — no exposed case concerns genfit or build
wiring.

**Required answer:**
- p1: the default build adds only `genfit` and `genfit2` as
  subdirectories; `genfit2-remote` is not in the top-level add_subdirectory
  set.
- p2: the genfit2-remote CMakeLists is an alternative recipe compiling the
  genfit2 sources (core, fields, fitters, measurements, trackReps, ...) into
  a library target named libgenfit — it ships no sources of its own.

**Gold evidence:**
- e1: `pandaroot/CMakeLists.txt` (top level, add_subdirectory lines).
- e2: `pandaroot/genfit2-remote/CMakeLists.txt`.

**Coverage:** pandaroot code, identifier-heavy, comparison, moderate.
**Difficulty:** moderate.
**Potential concern:** the *purpose* of genfit2-remote (remote/standalone
build variant) is inferred from its CMake content; the question was phrased
to ask only what the recipe builds, which is directly evidenced. If the
reviewer wants the historical purpose answered, this candidate needs revision
or corpus evidence beyond the snapshot.
**Recommendation:** ACCEPT (as phrased) — Human decision: PENDING.

---

## n014 — model_framework vs the model layer

**Question:** LuminosityFit has its own model classes under model/ and a
separate model_framework directory. What is model_framework, and how does it
differ from the model layer?

**Intent:** module_structure
**Expected status:** answered

**Why this is novel:** g097 inventories the model layer's core modules; this
asks the role of the separately vendored `model_framework` (an archived
upstream working copy) and its relation to the native `model/` classes — a
need g097 does not measure. Entity/evidence overlap is partial and
information-need overlap is medium (same subsystem), documented in the
sidecar rationale.

**Closest Gold:** g097 — model-layer composition inventory.

**Required answer:**
- p1: `model_framework` is a vendored working copy of ModelFramework,
  archived upstream in the meantime; it supplies generic 1D/2D model,
  operator, and fitting infrastructure.
- p2: `model/` holds the concrete LuminosityFit models (DPM and E760
  parametrizations, smearing/convolution models) that `PndLmdModelFactory`
  assembles.

**Gold evidence:**
- e1: `luminosityfit/model_framework/README.md` (vendored/archived status).
- e2: `luminosityfit/model/PndLmdModelFactory.h` (native layer anchor).

**Coverage:** luminosityfit code, descriptive, comparison, moderate.
**Difficulty:** moderate.
**Potential concern:** e1 is a two-line README; the "generic 1D/2D model and
operator infrastructure" half of p1 rests on the directory layout
(models1d/models2d/operators1d/operators2d/fit). Reviewer should confirm this
reading, and weigh the medium information-need overlap against g097.
**Recommendation:** ACCEPT (see concern) — Human decision: PENDING.

---

## n015 — legacy VC build failure and its workaround's side effect

**Question:** Configuring PandaRoot on an ARM machine, cmake fails while
compiling the legacy VC package. What does the documentation suggest, and
what does the workaround disable as a side effect?

**Intent:** troubleshooting
**Expected status:** answered

**Why this is novel:** exposed troubleshooting cases (g109-g115) diagnose
runtime/analysis artifacts; no exposed case is a build-configuration failure,
and none has this workaround-with-side-effect structure.

**Closest Gold:** none_found — no exposed build-failure diagnosis.

**Required answer:**
- p1: configure with `cmake -DNOVC=1` (failure known on Apple/ARM machines;
  MacOS handled automatically).
- p2: side effect — CAtracking and FtsCATracking are disabled too, since they
  depend on the legacy VC.

**Gold evidence:**
- e1: Sphinx `Installation/Troubleshooting.html` (the VC/NOVC entry).

**Coverage:** pandaroot documentation, descriptive, single-hop, moderate.
**Difficulty:** moderate.
**Potential concern:** none.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## n016 — Docker on Windows (legitimate refusal)

**Question:** Can I run the documented PandaRoot Docker containers natively
on Windows, or is a Linux host required? What does the locked documentation
actually say about supported host platforms?

**Intent:** troubleshooting
**Expected status:** insufficient_evidence

**Why this is novel:** same legitimate-refusal class as g007 (unstated
hardware requirement) applied to host-platform support: the corpus simply
does not state Windows support anywhere. Deterministic search over the whole
locked corpus: the only "windows" hits are "mass windows" in a tutorial and
build-config boilerplate — nothing about Windows as a container host.

**Closest Gold:** g007 (unstated GPU-memory requirement) — same refusal
class, different requirement.

**Required answer:**
- p1: state that the locked corpus does not establish native Windows
  support; the container docs assume the documented Linux-based workflow, and
  no Windows-host instructions exist in the corpus.

**Gold evidence:**
- e1: Sphinx `Docker/Docker.html` (alternative: `Docker/DevelopingInContainer.html`)
  — the nearest container documentation that does not address host-platform
  support.

**Coverage:** pandaroot documentation, descriptive, single-hop, simple.
**Difficulty:** simple.
**Potential concern:** proving absence relies on corpus-wide deterministic
search performed during curation; reviewer should spot-check the Docker pages
and confirm they are comfortable with an insufficient-evidence expectation.
**Recommendation:** ACCEPT — Human decision: PENDING.

---

## Curation notes for the reviewer

1. **Scope decision — ComPWA helicity formalism dropped.** The Pflueger 2017
   second half (ComPWA helicity-formalism implementation) is inside the
   frozen PDF corpus but outside the PANDA software user-question space this
   product serves; it was considered and dropped as a theory anchor to avoid
   testing corpus-coverage corners instead of PANDA question distribution.
2. **No cross-repository candidate survived naturalness filtering.** A
   fork-vs-upstream directory-diff question was drafted but rejected as too
   close to g099 ("How does RestgasDetermination extend PandaRoot?").
   Recorded as a coverage gap with a proposed minimum for the full dataset.
3. **Difficulty labels** were assigned from question/evidence structure only
   (band 6 simple / 8 moderate / 2 hard; simple is one case above the 3-5
   guidance band — flagged rather than inflated).
4. **Sidecar mirror:** each Gold `cluster_id` mirrors the sidecar
   `curation_family_id` (`nf001`-`nf016`); cross-file family isolation is
   enforced by `evaluation/scripts/validate_novel_curation.py`, which scans
   any `novel_*.yaml` present in this directory.
5. **Static validation performed (T0 only):** Gold schema parse, sidecar
   consistency, ID/family uniqueness, duplicate-query check, selector
   structure, deterministic path existence and PDF page-range bounds,
   coverage-report count consistency, plus a KB cross-match confirming every
   critical evidence group matches at least one existing knowledge object.
   No retrieval, QA, judge, embedding, or index operations were run.
6. **Corpus/representation observation (no system change made):** the current
   KnowledgeObject decomposition types `configSettings.sh` as `shell_script`
   and sub-directory Readmes as `readme_section` rather than `source_file`,
   and `restgas_determination/INSTALL.GSI` is not represented at all. Gold
   selectors were written to match the current objects (path-based, without
   object_type constraints for these files); `INSTALL.GSI` is kept only as an
   inert `any_of` alternative pointing at real locked-corpus content. If the
   derived representation is regenerated later, these selectors remain valid.
