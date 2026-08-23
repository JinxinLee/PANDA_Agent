# N2-A Batch 1 Review Package — Expansion Candidates n020-n025

Status: READY_FOR_HUMAN_REVIEW (2026-08-24). Codex recommendations below are
advisory only. No candidate carries a human decision yet; every `Human
decision` field is PENDING. The authorizing plan
(`N2_FULL_NOVEL_DEV_EXPANSION_PLAN.md`, Rev 1) was approved by reviewer `Li`
at 2026-08-24T01:25+02:00 (approved commit `08626661e3bb776c8f74c4f5b28c85ff2147c0fb`).

Curation boundary: all six candidates were sampled from locked-source anchors
under the approved anchor-first protocol. No PANDA Agent component was run
and no benchmark or novel outcome was inspected. The 16 frozen N1 questions
are untouched; the dataset enters the 0.3.0 expansion lineage
(`novel-v1-dev-0.3.0`, identity `novel-v1-dev-expansion`, status
`EXPANSION_IN_PROGRESS`).

---

## n020 / nf020 — restgas displaced-track recovery chain

- **Question:** In the restgas determination analysis, the standard track
  finder leaves part of the hits unassigned. Which task picks up those
  leftover hits, and what do the downstream displaced-track finder and
  z-recovery stages each contribute before the final fit?
- **Intent:** data_flow — **Expected status:** answered — **Difficulty:**
  moderate
- **Primary task archetype:** producer_consumer_trace — **Class:**
  representative (fit moderate / relevance strong / core)
- **Scope:** restgas_determination only; single_source; topology
  producer_consumer; descriptive.
- **Critical evidence:** restgas `README.md` (displaced-track reconstruction
  section: the five-stage chain); `tracking/PndUnassignedHits/PndUnassignedHitsTask.h`;
  `tracking/PndApolloniusTripletTrackFinder/PndApolloniusTripletTrackFinderTask.h`.
- **Answer-point summary:** (1) PndUnassignedHitsTask collects the hits the
  standard finder (PndTrkTracking2) left unassigned; (2) the triplet finder
  reconstructs displaced trajectories from STT drift-circle triplets plus
  MVD/GEM while PndSttSkewStrawPzFinderTask recovers the longitudinal
  component from skewed STT layers; (3) PndRecoKalmanTask2 fits the result
  with SetPropagateToIP(kFALSE) in the chain configured in
  `macro/target/reco_complete.C`.
- **Closest exposed Gold:** g070, g074 (producer-consumer archetype,
  different subsystems; information_need overlap low).
- **Closest frozen N1 family:** none equivalent — nf017 (PndTrack object
  definition) and nf019 (Kalman fitting pipeline) cover different needs;
  nf008 covers thesis-level track-search comparison.
- **Novelty:** relation + composition — the unassigned-hit hand-off and the
  composed recovery chain are not measured by any exposed case.
- **Domain relevance:** recovering displaced restgas secondaries is the core
  purpose of the locked branch.
- **Known uncertainty:** p3 attributes the disabled-IP fit to
  PndRecoKalmanTask2 as documented in the branch README; the reviewer may
  want to confirm the class name against `macro/target/reco_complete.C`.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n021 / nf021 — PandaRoot + LuminosityFit luminosity workflow

- **Question:** I want to go from simulated luminosity-detector events to a
  luminosity estimate using my PandaRoot and LuminosityFit installations.
  Which parts of that workflow belong to which repository, and which
  LuminosityFit scripts drive the combined chain?
- **Intent:** usage — **Expected status:** answered — **Difficulty:** hard
- **Primary task archetype:** workflow_sequence (secondary
  producer_consumer_trace) — **Class:** representative (fit moderate /
  relevance strong / rare)
- **Scope:** cross_repository (pandaroot + luminosityfit); cross_source;
  topology multi_hop; descriptive.
- **Critical evidence:** luminosityfit `README.md` (first-workflow section:
  runSimulationReconstruction.py, determineLuminosity.py); luminosityfit
  `python/Readme.md` ("these events have to be simulated using the PandaRoot
  framework"); pandaroot `detectors/lmd/LmdDigi/PndLmdDigiTask.h` (PandaRoot
  LMD digitization task).
- **Answer-point summary:** (1) simulation/reconstruction of LMD events is
  performed with the PandaRoot framework, which LuminosityFit scripts start
  directly; (2) the combined chain is driven by LuminosityFit's
  runSimulationReconstruction.py then determineLuminosity.py; (3) the PandaRoot
  side implements the luminosity monitor under `detectors/lmd` (LmdMC, LmdDigi,
  LmdReco).
- **Cross-repository minimum-footprint derivation (static):** critical groups
  e1 (luminosityfit README) AND e2 (luminosityfit python/Readme.md) AND e3
  (pandaroot LmdDigiTask.h). Minimum footprint = {luminosityfit, pandaroot};
  no single-repository footprint satisfies all three critical groups →
  `cross_repository` PASS.
- **Closest exposed Gold:** g091, g092 (workflow-sequence archetype,
  single-repository; information_need overlap low).
- **Closest frozen N1 family:** none equivalent — nf009 (elastic-model
  existence) and nf014 (model_framework directory role) are distinct needs.
- **Novelty:** reasoning_topology (cross-repository) + composition.
- **Domain relevance:** producing luminosity estimates from simulated LMD
  events is the central use case of the locked luminosity toolchain.
- **Known uncertainty:** p1/p2 rely on the repository's own README wording;
  the reviewer may verify the script names still match the locked tree
  (verified statically during curation).
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n022 / nf022 — two-step POCA artifact flow

- **Question:** The restgas analysis determines the event vertex through a
  two-step POCA workflow. What does the first worker step leave behind for
  the second analysis step, and how is the fitted vertex fed into the
  reprocessing?
- **Intent:** data_flow — **Expected status:** answered — **Difficulty:**
  moderate
- **Primary task archetype:** producer_consumer_trace — **Class:**
  representative (fit moderate / relevance strong / rare)
- **Scope:** restgas_determination only; single_source; topology
  producer_consumer; descriptive; source type workflow (Python scripts).
- **Critical evidence:** `macro/target/poca_step1_worker.py` (per-job sim →
  digi → reco → pid → ana_dpm.C, leaving `vtx_fit.json`);
  `macro/target/poca_step2_analysis.py` (reads vertex_x/y/z means from the
  JSON, exports FIT_VERTEX_X/Y/Z and POCA_VERTEX_FILE).
- **Answer-point summary:** (1) step 1 leaves stage outputs plus the
  vtx_fit.json vertex-fit artifact; (2) step 2 reads the fitted vertex means
  from that JSON; (3) step 2 exports them as environment variables that
  parameterize the back-propagated reprocessing.
- **Closest exposed Gold:** g079, g080 (producer-consumer archetype;
  information_need overlap low).
- **Closest frozen N1 family:** nf020 is the nearest — separated because
  nf020 covers the in-reconstruction task chain while n022 covers the
  analysis-level scripted artifact flow; the underlying information needs
  differ (stage hand-off vs cross-step artifact feedback).
- **Novelty:** relation + composition.
- **Domain relevance:** the POCA two-step pipeline is the operative
  vertex-determination workflow of the locked branch.
- **Known uncertainty:** p3's "drive the reprocessing" is evidenced by the
  environment-variable construction in step 2; the reviewer may confirm the
  consuming command in the remainder of the script.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n023 / nf023 — FTS track-finder ownership

- **Question:** I need to modify forward tracking for the forward
  spectrometer. Where in the PandaRoot source tree is the FTS track finder
  implemented, and which track branches does it write out?
- **Intent:** module_structure — **Expected status:** answered —
  **Difficulty:** simple
- **Primary task archetype:** source_location — **Class:** representative
  (fit strong / relevance strong / core)
- **Scope:** pandaroot only; single_source; topology single_hop;
  implementation_oriented.
- **Critical evidence:** `tracking/PndFtsTrackFinder/README.MD` (algorithm
  basis, version history, output branches); `tracking/PndFtsTrackFinder/PndFtsTrackFinderTask.h`.
- **Answer-point summary:** (1) implemented in `tracking/PndFtsTrackFinder`
  with PndFtsTrackFinderTask as the FairTask entry; (2) based on the PANDA
  Forward Tracker TDR algorithm (pp. 88-97); (3) writes PndTrackCand,
  PndTrack (two momentum-estimation methods, PndFtsContext), and
  PndTrackAnalytic branches.
- **Closest exposed Gold:** g027, g028 (source-location archetype, other
  subsystems; information_need overlap low).
- **Closest frozen N1 family:** none equivalent — nf017 (PndTrack
  definition), nf006 (filename helper), nf007 (shortID resolution) cover
  different needs.
- **Novelty:** entity + task_form.
- **Domain relevance:** routine developer need; forward-spectrometer
  tracking is a core subsystem.
- **Known uncertainty:** none material; evidence is direct package
  documentation.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n024 / nf024 — GEANE vs analytic-helix transport

- **Question:** PandaRoot can transport tracks through the magnetic field
  either with GEANE or with an analytic helix. What are the two propagators
  behind these options, and how does each determine the transported track
  state?
- **Intent:** algorithm_implementation — **Expected status:** answered —
  **Difficulty:** moderate
- **Primary task archetype:** implementation_explanation (secondary
  concept_comparison) — **Class:** representative (fit strong / relevance
  strong / core)
- **Scope:** pandaroot only; single_source; topology comparison;
  descriptive.
- **Critical evidence:** `tracking/PndGeanePropagator/PndGeanePro.h`
  ("Interface to GEANE", error/transport matrices, volume/plane modes);
  `tracking/PndHelixPropagator/PndHelixPropagator.h` ("Helix propagator",
  uniform-field radius/center/angle machinery, backward flag).
- **Answer-point summary:** (1) PndGeanePro interfaces GEANE with
  error-matrix and transport-matrix handling to volumes/planes; (2)
  PndHelixPropagator transports analytically on a helix under a homogeneous
  z-field; (3) both implement the common PndPropagator interface.
- **Closest exposed Gold:** g059, g060 (implementation-explanation
  archetype, LuminosityFit smearing; information_need overlap low).
- **Closest frozen N1 family:** nf019 is the nearest — separated because
  nf019 covers track *fitting* (Kalman/DAF dispatch) while n024 covers track
  *transport* (propagation); the propagator pair is not part of nf019's
  information need.
- **Novelty:** entity + composition (two-implementation comparison).
- **Domain relevance:** track transport underlies all PandaRoot
  reconstruction.
- **Known uncertainty:** p3's common-interface claim is evidenced by both
  headers subclassing PndPropagator; reviewer may sanity-check usage.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n025 / nf025 — Apollonius triplet geometry

- **Question:** The displaced-track finder in the restgas branch builds
  candidates from triplets of STT drift circles by solving the classical
  Apollonius tangency problem. How does it keep the triplet combinatorics
  manageable while staying efficient for displaced vertices?
- **Intent:** algorithm_implementation — **Expected status:** answered —
  **Difficulty:** moderate
- **Primary task archetype:** implementation_explanation — **Class:**
  representative (fit moderate / relevance strong / rare)
- **Scope:** restgas_determination only; single_source; topology
  single_hop; descriptive.
- **Critical evidence:** restgas `README.md` ("Apollonius track finding"
  subsection); `tracking/PndApolloniusTripletTrackFinder/PndApolloniusTriplet.h`.
- **Answer-point summary:** (1) three drift circles admit up to eight
  tangent-circle solutions via internal/external tangency; (2) combinatorics
  reduced by separated inner/middle/outer rows plus neighbor/topological and
  azimuthal compatibility; (3) candidates are grown with compatible hits and
  the best-matching populated trajectory is selected, avoiding a hard
  nominal-IP constraint.
- **Closest exposed Gold:** g061, g062 (implementation-explanation
  archetype; information_need overlap low).
- **Closest frozen N1 family:** nf020 (chain hand-off) and nf008
  (thesis track-search comparison) are both distinct from the geometric
  algorithm internals asked here.
- **Novelty:** entity + nontrivial_expression (descriptive geometric
  formulation, no symbol lookup).
- **Domain relevance:** the triplet finder is the core geometric
  reconstruction idea of the locked branch.
- **Known uncertainty:** none material.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

---

## Discarded sampling attempt (no ID consumed)

- **macro/run stage-chain macro question (data_flow/workflow_sequence):**
  a candidate asking what each of `sim_complete.C` → `digi_complete.C` →
  `reco_complete.C` → `pid_complete.C` consumes from the previous stage was
  drafted in preflight and discarded. Its family-adjacency risk against
  nf006 (stage-filename helper `PndFileNameCreator`) and its
  enumeration-flavored answer shape made it the weakest of the audited
  anchors; quality-over-count applies. The anchor remains available for
  Batch 2 reconsideration with a sharper information need.

## Batch summary for the reviewer

6 candidates (n020-n025 / nf020-nf025), all `review_status: draft`,
`reviewer: null`, sidecar `lifecycle: draft`. Priority areas covered:
data_flow/producer-consumer (n020, n022), genuine cross-repository (n021,
footprint-verified), source_location (n023), implementation_explanation
(n024, n025). No exploratory candidates arose naturally in Batch 1, matching
the plan's assignment of exploratory balancing to Batch 2. Expected status:
all answered. Difficulty: 1 simple / 4 moderate / 1 hard.
