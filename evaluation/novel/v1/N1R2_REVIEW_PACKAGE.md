# N1-R2 Review Package — revised novel-dev pilot

Current status: `REVISED_PILOT_READY_FOR_HUMAN_REVIEW`. This package contains
16 active draft questions and 16 independent active semantic families. No
question is approved or frozen. N1 remains `HUMAN_REVIEW_PENDING`.

N1-R2 used only locked source inspection, exposed Gold annotations, and static
validation. PANDA retrieval, runtime QA, model calls, external services, and
benchmark or novel outcome inspection were not used.

## Minimum-source-scope reproducibility

`evaluation/scripts/validate_novel_curation.py` now derives each Gold v2.6
minimum required source footprint from critical evidence groups (`AND`) and
their `any_of` alternatives (`OR`). Resolution follows explicit `source_id`,
`source_version_id`, static provenance, narrow known curated-object ownership,
and opaque-object provenance found in frozen static capture artifacts. Unknown
ownership is never treated as an empty or free source requirement.

The fresh derivation reproduced all 120 stored profile assignments, including
evidence topology and difficulty proxy. Opaque selectors unresolved: `0`.
The v2 minimum-scope distribution did not change.

## Active candidate table

| ID | Intent | Task archetype | Expected status | Benchmark fit | Domain relevance | Novelty | Difficulty | Codex recommendation |
|---|---|---|---|---|---|---|---|---|
| n001 | installation | setup_environment | answered | moderate | strong | entity | simple | READY_FOR_HUMAN_REVIEW |
| n002 | installation | setup_environment | answered | strong | strong | entity | simple | READY_FOR_HUMAN_REVIEW |
| n003 | usage | component_usage | answered | strong | strong | entity, relation | moderate | READY_FOR_HUMAN_REVIEW |
| n004 | usage | component_usage | answered | moderate | strong | entity, task_form | simple | READY_FOR_HUMAN_REVIEW |
| n005 | usage | component_usage | answered | moderate | moderate | entity, nontrivial_expression | moderate | READY_FOR_HUMAN_REVIEW |
| n006 | api | component_usage | answered | moderate | moderate | entity, task_form | moderate | READY_FOR_HUMAN_REVIEW |
| n007 | api | component_usage | answered | moderate | moderate | entity, relation, nontrivial_expression | moderate | READY_FOR_HUMAN_REVIEW |
| n008 | algorithm_theory | concept_comparison | answered | moderate | moderate | entity, reasoning_topology, nontrivial_expression | moderate | READY_FOR_HUMAN_REVIEW |
| n009 | algorithm_theory | theory_explanation | answered | moderate | strong | relation, composition, reasoning_topology | hard | READY_FOR_HUMAN_REVIEW |
| n010 | algorithm_implementation | implementation_explanation | answered | strong | strong | entity, composition | hard | READY_FOR_HUMAN_REVIEW |
| n011 | data_flow | producer_consumer_trace | answered | strong | strong | entity, relation | moderate | READY_FOR_HUMAN_REVIEW |
| n012 | data_flow | workflow_sequence | answered | moderate | strong | relation, composition, reasoning_topology | hard | READY_FOR_HUMAN_REVIEW |
| n014 | module_structure | repository_structure | answered | moderate | moderate | entity, relation | moderate | READY_FOR_HUMAN_REVIEW |
| n015 | troubleshooting | troubleshooting_diagnosis | answered | strong | strong | task_form, composition | moderate | READY_FOR_HUMAN_REVIEW |
| n016 | troubleshooting | setup_environment | insufficient_evidence | moderate | moderate | failure_mode | simple | READY_FOR_HUMAN_REVIEW |
| n017 | api | source_location | answered | strong | strong | entity, relation | simple | READY_FOR_HUMAN_REVIEW |

## Per-question review

### n001

- **Question:** Which FairSoft/FairRoot pairs and paths are encoded in the restgas setup script, which variables are assigned, and what does it actually do for unmatched input?
- **Intent / task archetype / answerability:** installation / setup_environment / answerable.
- **Required answer points:** intended version literals and placeholder paths; `SIMPATH` and `FAIRROOTPATH`; malformed Bash equality tests make the first branch win; the nominal fallback only echoes.
- **Gold evidence:** `restgas_determination/configSettings.sh`; `INSTALL.GSI` is an alternative for the environment-variable obligation.
- **Novelty rationale:** fork-local setup-script auditing is absent from exposed installation cases.
- **Representativeness rationale:** a directly relevant fork setup need, with strong domain relevance and moderate benchmark-reference fit.
- **Changes from previous draft:** corrected recognition/rejection claims to actual shell semantics. ID/family preserved because the setup-script information need is unchanged.
- **Remaining concern:** human reviewer should confirm that reporting intended literals plus actual malformed-test behavior is the desired answer emphasis.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n002

- **Question:** What Python packages do LuminosityFit scripts expect, and where are they declared?
- **Intent / task archetype / answerability:** installation / setup_environment / answerable.
- **Required answer points:** `requirements.txt` and its exact twelve-package list; the file does not classify packages or state their roles.
- **Gold evidence:** `luminosityfit/requirements.txt`.
- **Novelty rationale:** no exposed case asks for LuminosityFit's Python dependency declaration.
- **Representativeness rationale:** dependency discovery is a strong benchmark analogue and core setup need.
- **Changes from previous draft:** removed unsupported package-purpose labels and the unasked Python workflow obligation.
- **Remaining concern:** none beyond human wording preference.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n003

- **Question:** Which generator performs fixed-step momentum/polar-angle scans, and how is stepping configured?
- **Intent / task archetype / answerability:** usage / component_usage / answerable.
- **Required answer points:** `PndFixStepParticleGun`; `SetPRange` and `SetThetaRange`; per-event increment and range rollover in `CalcActValues`.
- **Gold evidence:** `PndFixStepParticleGun.h`, the locked FixStep documentation page, and `PndFixStepParticleGun.cxx`.
- **Novelty rationale:** the entity and fixed-step acceptance-scan operation are absent from exposed generator cases.
- **Representativeness rationale:** a strong component-usage analogue with strong acceptance-study relevance.
- **Changes from previous draft:** added direct implementation evidence for the claimed event-by-event semantics.
- **Remaining concern:** none identified.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n004

- **Question:** How can a macro enable severity and file/line/function logging, and what related controls exist?
- **Intent / task archetype / answerability:** usage / component_usage / answerable.
- **Required answer points:** verbosity specification and console-color behavior.
- **Gold evidence:** locked PandaRoot logging documentation.
- **Novelty rationale:** runtime logging configuration is absent from exposed cases.
- **Representativeness rationale:** plausible recurring debugging configuration.
- **Changes from previous draft:** sentinel; no content or metadata change.
- **Remaining concern:** none identified.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n005

- **Question:** What visual event/geometry tool does PandaRoot provide, and how is a file opened in it?
- **Intent / task archetype / answerability:** usage / component_usage / answerable.
- **Required answer points:** event-display role; invoking `macro/tools/eventDisplay.C` with the shared prefix; default prefix and sim/digi/reco friends.
- **Gold evidence:** locked EventDisplay overview and `pandaroot/macro/tools/eventDisplay.C`.
- **Novelty rationale:** event visualization and its file-prefix entry point are absent from exposed cases.
- **Representativeness rationale:** a documented, plausible inspection need with moderate domain relevance.
- **Changes from previous draft:** replaced post-start navigation advice with the critical file-open/start semantics the user asked for.
- **Remaining concern:** the macro's prefix convention may merit a small human wording refinement.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n006

- **Question:** Which helper derives chained stage filenames, and what suffixes does it define?
- **Intent / task archetype / answerability:** api / component_usage / answerable.
- **Required answer points:** `PndFileNameCreator`/`GetCustomFileName`; exact constructor suffix literals.
- **Gold evidence:** `PndFileNameCreator.h`, locked tool documentation, and `PndFileNameCreator.cxx`.
- **Novelty rationale:** reusable chain naming differs from exposed single-artifact location cases.
- **Representativeness rationale:** a moderate, practical tool-usage need.
- **Changes from previous draft:** added constructor implementation evidence and exact suffix values. Archetype remains component_usage because the question asks how to use the utility, not merely where it lives.
- **Remaining concern:** none identified.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n007

- **Question:** How is an MVD shortID resolved to a full geometry path, and what state must be initialized?
- **Intent / task archetype / answerability:** api / component_usage / answerable.
- **Required answer points:** `GetPath(Int_t)` and reverse `GetShortID`; initialized `TGeoManager` and `PndSensorNamePar`; construction during `SetParContainers`.
- **Gold evidence:** `PndGeoHandling.h` and its locked documentation page.
- **Novelty rationale:** active MVD shortID resolution is distinct from exposed coordinate-transform cases.
- **Representativeness rationale:** moderate benchmark/domain fit for MVD analysis tooling.
- **Changes from previous draft:** removed legacy encrypted-path mixing and limited obligations to the active shortID API.
- **Remaining concern:** none identified.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n008

- **Question:** Which LMD track-search approaches were developed, and how do they compare?
- **Intent / task archetype / answerability:** algorithm_theory / concept_comparison / answerable.
- **Required answer points:** track following versus cellular automaton; sparse-hit constraint; missed/fake-track relevance to the theta distribution.
- **Gold evidence:** Karavdina thesis pages 72-77.
- **Novelty rationale:** the specific theory comparison is absent from exposed cases.
- **Representativeness rationale:** moderate reference/domain fit for LMD reconstruction study.
- **Changes from previous draft:** sentinel content retained; N1-R2R1 later
  reconciled this review range with the machine Gold at the minimum sufficient
  pages 72-77.
- **Remaining concern:** none identified.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n009

- **Question:** Which E760 alternative exists, and what does the thesis say about intrinsic and beam-momentum uncertainty?
- **Intent / task archetype / answerability:** algorithm_theory / theory_explanation / answerable.
- **Required answer points:** E760/E760-like model and code; intrinsic dominant parameters and sub-0.5% result in 2-8 GeV/c; separate expected HESR momentum contribution below 0.005%.
- **Gold evidence:** Karavdina thesis pages 50-56 and 61-62; both LuminosityFit E760 parametrization sources.
- **Novelty rationale:** composes an unexposed alternative-model uncertainty need with distinct code evidence.
- **Representativeness rationale:** strong luminosity-domain relevance and moderate benchmark fit.
- **Changes from previous draft:** removed the incorrectly mixed DPM below-2% obligation and corrected the beam-momentum claim.
- **Remaining concern:** human reviewer should confirm the level of numerical detail desired.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n010

- **Question:** How does PandaRoot fast simulation build detector responses, and what are its implementation blocks?
- **Intent / task archetype / answerability:** algorithm_implementation / implementation_explanation / answerable.
- **Required answer points:** PndFsmTrack response pipeline; `PndFsmAbsDet::respond`; named detector factory; response aggregation and cut/smear application.
- **Gold evidence:** `PndFastSim.cxx`, `PndFsmAbsDet.h`, `PndFsmDetFactory.cxx`, and `PndFsmResponse.h`.
- **Novelty rationale:** the fast-simulation subsystem is absent from exposed implementation cases.
- **Representativeness rationale:** strong benchmark and domain fit for feasibility studies.
- **Changes from previous draft:** supplied the missing factory and response implementation chain and removed the unnecessary subsystem inventory.
- **Remaining concern:** the four-file chain makes this one of the harder pilot items, but every file supports an asked obligation.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n011

- **Question:** How can analysis inspect a reconstructed candidate's MC counterpart and match an entire decay tree?
- **Intent / task archetype / answerability:** data_flow / producer_consumer_trace / answerable.
- **Required answer points:** `RhoCandidate::GetMcTruth` plus null check; `PndAnalysis::McTruthMatch`; candidate types and EvtGen PDG-table preparation.
- **Gold evidence:** locked Monte Carlo Truth Match tutorial.
- **Novelty rationale:** reconstructed-candidate-to-truth inspection is absent from exposed data-flow cases.
- **Representativeness rationale:** strong benchmark and domain relevance for simulated-data analysis.
- **Changes from previous draft:** removed the unsupported generator-to-`PndMCTrackInfo` chain and retained only tutorial-supported analysis-boundary truth relations. ID/family preserved because the core need—checking reconstructed candidates and decay trees against generated truth—remains unchanged; only the unsupported upstream over-composition was removed.
- **Remaining concern:** none identified.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n012

- **Question:** What LMD alignment method was studied, and where does the current workflow place an alignment stage?
- **Intent / task archetype / answerability:** data_flow / workflow_sequence / answerable.
- **Required answer points:** track-based non-iterative Millepede method; current Readme places a possible alignment process before its listed IP-to-fit workflow; no asserted causal handoff.
- **Gold evidence:** Karavdina thesis pages 114-129 and `luminosityfit/python/Readme.md`.
- **Novelty rationale:** alignment method plus present workflow placement is absent from exposed cases.
- **Representativeness rationale:** strong luminosity-domain relevance and moderate workflow-sequence analogue.
- **Changes from previous draft:** removed the unproven historical-output-to-current-input link and reclassified the task from producer-consumer trace to workflow sequence. ID/family preserved because the original underlying need—alignment method plus its place before luminosity analysis—remains unchanged.
- **Remaining concern:** human reviewer should ensure the two-source, non-causal wording stays explicit.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n014

- **Question:** What does the repository explicitly say `model_framework` is, and what role does `PndLmdModelFactory` expose?
- **Intent / task archetype / answerability:** module_structure / repository_structure / answerable.
- **Required answer points:** working-copy and archived status stated by the README; native factory entry point and directly declared model-generation role.
- **Gold evidence:** `model_framework/README.md` and `model/PndLmdModelFactory.h`.
- **Novelty rationale:** overlaps the model subsystem but asks a distinct directory-boundary question.
- **Representativeness rationale:** legitimate newcomer structure need with moderate reference and domain fit.
- **Changes from previous draft:** removed unsupported generic architecture and complete concrete-model inventory; reclassified from exploratory/revise to representative/keep.
- **Remaining concern:** the README is intentionally terse, so the answer must not infer more than it states.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n015

- **Question:** What workaround addresses legacy VC build failure on ARM, and what does it disable?
- **Intent / task archetype / answerability:** troubleshooting / troubleshooting_diagnosis / answerable.
- **Required answer points:** `-DNOVC=1`; CAtracking and FtsCATracking side effect.
- **Gold evidence:** locked installation troubleshooting page.
- **Novelty rationale:** build-workaround diagnosis is absent from exposed runtime/analysis troubleshooting cases.
- **Representativeness rationale:** a directly relevant and plausibly recurring PandaRoot support need.
- **Changes from previous draft:** sentinel content unchanged; empirical-frequency overstatement removed from representativeness rationale.
- **Remaining concern:** none identified.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n016

- **Question:** Do locked Docker pages establish native Windows-host support, and what host environment do examples demonstrate?
- **Intent / task archetype / answerability:** troubleshooting / setup_environment / corpus_insufficiency.
- **Required answer points:** no Windows-host support statement or procedure; Unix-oriented examples; those examples do not prove Windows unsupported or Linux mandatory.
- **Gold evidence:** locked Docker and DevelopingInContainer pages.
- **Novelty rationale:** a distinct platform-support insufficiency case analogous to g007's evidence boundary.
- **Representativeness rationale:** plausible platform setup need with moderate reference/domain fit.
- **Changes from previous draft:** removed claims that Windows is unsupported, Linux is required, or absence was proven corpus-wide.
- **Remaining concern:** human reviewer should preserve the distinction between undocumented and impossible.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

### n017

- **Question:** Where is PandaRoot's persistent reconstructed-track object defined, and which fitted endpoints and candidate links does it store?
- **Intent / task archetype / answerability:** api / source_location / answerable.
- **Required answer points:** `PndTrack` in `pnddata/TrackData/PndTrack.h`; first/last `FairTrackParP`; embedded/reference-linked `PndTrackCand`; directly declared reconstruction metadata.
- **Gold evidence:** `pandaroot/pnddata/TrackData/PndTrack.h`.
- **Novelty rationale:** the class, file, persistent-data boundary, and stored relationship are absent from exposed Gold.
- **Representativeness rationale:** a common tracking data artifact with strong benchmark-reference and domain relevance.
- **Changes from previous draft:** new independent replacement for withdrawn n013.
- **Remaining concern:** human reviewer should confirm that the field-level boundary is sufficiently substantive beyond class location.
- **Codex recommendation:** READY_FOR_HUMAN_REVIEW.
- **Human decision:** PENDING.

#### Replacement rationale

- **Why this is representative:** `PndTrack` is a central persistent artifact exchanged by tracking code; locating its definition and data boundary is a natural developer task.
- **Why this is still novel:** exposed Gold contains no `PndTrack` or `pnddata/TrackData` obligation and does not ask which fitted endpoints and candidate links the persistent track stores.
- **Why this component was independently selected:** five natural locked-corpus anchors were considered before Gold novelty comparison. The event-display entry point, filename helper, MC-truth analysis boundary, and LuminosityFit model factory were not selected because active n005, n006, n011, and n014 already cover their semantic families. The persistent reconstructed-track boundary remained core, distinct, and evidence-clean.
- **Closest Gold analogue:** g029, because it combines source location with a data-boundary question.
- **Closest Gold novelty case:** g029; task form overlap is medium, while entity, evidence path, subsystem role, and concrete information need are distinct.

## Retired drafts

### n013

- **Disposition:** `WITHDRAWN_DRAFT`.
- **Reason:** representativeness and factual failure: vendored GenFit build corner, weak domain relevance, corpus-tail sampling, and incorrect annotation.
- **Replacement:** n017.
- **History:** n013 and nf013 remain visible in historical N1/N1-R/N1-R1 documents, are absent from the active dataset and sidecar, and must not be reused.

## Human-review boundary

All active records remain `review_status: draft`, `reviewer: null`, and
`reviewed_at: null`. Codex recommendations above mean only that static semantic
and evidence repair is complete enough for a human decision; they are not
approvals.
