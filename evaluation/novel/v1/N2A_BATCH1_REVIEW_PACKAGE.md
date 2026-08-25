# N2-A Batch 1 Review Package — Expansion Candidates n020-n025

Status: **BATCH1_HUMAN_APPROVED / SPLIT_FROZEN** (2026-08-25 finalization).

Human review record: reviewer `Li` reviewed commit
`99ef7bf3cf9bd972d04e9f2cf5389076b6a6c0a6` at 2026-08-24T01:50+02:00 with
decisions n020 ACCEPT, n021 REVISE, n022 REVISE, n023 REVISE, n024 ACCEPT,
n025 ACCEPT (3 ACCEPT / 3 REVISE / 0 REJECT / 0 PENDING). The three REVISE
corrections and a batch-wide malformed `pflueger_2017` source-identity fix
were applied in R1 (commit `516ba51abc628c63c90c41bc722a3b3825eb0269`), and
a generic validator rule now enforces the locked source-version universe.

Human re-review record: reviewer `Li` re-reviewed the corrected commit
`516ba51abc628c63c90c41bc722a3b3825eb0269` at 2026-08-24T02:05+02:00 and
accepted the corrected records n021 ACCEPT, n022 ACCEPT, n023 ACCEPT. Final
Batch 1 decisions: **6 ACCEPT / 0 REVISE / 0 REJECT / 0 PENDING**. All six
records are `approved` with reviewer `Li` and were made `split_frozen` during
N2 finalization. The historical first-review REVISE decisions and R1
correction records below are preserved unchanged.

Curation boundary: all six candidates were sampled from locked-source anchors
under the approved anchor-first protocol. No PANDA Agent component was run
and no benchmark or novel outcome was inspected. The 16 frozen N1 questions
are untouched; the six Batch 1 records are human-approved and split_frozen as
part of N2 finalization. The dataset lineage is complete and frozen
(`novel-v1-dev-0.3.0`, identity `novel-v1-dev-expansion`, status `COMPLETE`).

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
- **Human decision:** ACCEPT (Li, 2026-08-24T01:50+02:00; record now
  `approved` / lifecycle `approved`, not yet `split_frozen`)

## n021 / nf021 — PandaRoot + LuminosityFit luminosity workflow

- **Question (corrected in R1):** I want to trace the LMD workflow across
  PandaRoot and LuminosityFit. Where does PandaRoot implement the LMD
  simulation, digitization, and reconstruction side, and which LuminosityFit
  scripts orchestrate simulation/reconstruction and then the luminosity fit?
- **Intent:** usage — **Expected status:** answered — **Difficulty:** hard
- **Primary task archetype:** workflow_sequence (secondary
  producer_consumer_trace) — **Class:** representative (fit moderate /
  relevance strong / rare)
- **Scope:** cross_repository (pandaroot + luminosityfit); cross_source;
  topology multi_hop; descriptive.
- **Critical evidence (corrected in R1):** luminosityfit `README.md`
  (first-workflow section: runSimulationReconstruction.py,
  determineLuminosity.py); pandaroot `detectors/lmd/CMakeLists.txt`
  (implementation ownership: libLmd with LmdMC/LmdDigi sources and
  libLmdReco reconstruction tasks).
- **Answer-point summary:** (1) PandaRoot implements the LMD detector side
  under `detectors/lmd` (LmdMC detector/geometry sources, LmdDigi producers
  including PndLmdDigiTask, libLmdReco reconstruction tasks); (2)
  LuminosityFit orchestrates the user-facing workflow via
  runSimulationReconstruction.py then determineLuminosity.py.
- **Cross-repository minimum-footprint derivation (static, re-derived in
  R1):** critical groups e1 (luminosityfit) AND e2 (pandaroot); minimum
  footprint = {luminosityfit, pandaroot}, no single-repository footprint
  satisfies both obligations → `cross_repository` PASS.
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
- **Human decision:** REVISE (Li, 2026-08-24T01:50+02:00)

### n021 R1 correction record (CORRECTED / HUMAN_RE_REVIEW_PENDING)

- **Original human issue:** the initial Gold artificially established
  `cross_repository` by making a single PandaRoot header
  (`detectors/lmd/LmdDigi/PndLmdDigiTask.h`) critical even though the
  original wording could largely be answered from LuminosityFit documentation
  alone.
- **Corrected question wording:** "I want to trace the LMD workflow across
  PandaRoot and LuminosityFit. Where does PandaRoot implement the LMD
  simulation, digitization, and reconstruction side, and which LuminosityFit
  scripts orchestrate simulation/reconstruction and then the luminosity
  fit?" — the same information need, now phrased so both repository
  identities are naturally required.
- **Corrected evidence:** e1 luminosityfit `README.md` (workflow scripts
  obligation: runSimulationReconstruction.py, determineLuminosity.py); e2
  pandaroot `detectors/lmd/CMakeLists.txt` (implementation-ownership
  obligation: libLmd exposing LmdMC detector/geometry sources, LmdDigi
  producers including PndLmdDigiTask, and libLmdReco reconstruction tasks).
  The former python/Readme.md and PndLmdDigiTask.h groups were removed — no
  redundant group remains critical merely to manufacture a footprint.
- **Minimum critical footprint re-derivation (static):** critical groups =
  e1 (luminosityfit) AND e2 (pandaroot). Every valid minimum footprint
  contains both repository identities; no single-repository footprint
  satisfies both obligations.
- **Final proposed repository_scope:** `cross_repository` (retained on the
  re-derived footprint, not preserved for coverage reasons).
- **Codex post-correction recommendation:** RECOMMEND_ACCEPT
- **Human re-review:** ACCEPT (Li, 2026-08-24T02:05+02:00; record now `approved` / lifecycle `approved`, not yet `split_frozen`)

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
- **Critical evidence (corrected in R1):** `macro/target/ana_dpm.C`
  (produces `<prefix>_boost.root` with the `event_poca` tree and
  `<prefix>_vtx_fit.json`); `macro/target/poca_step2_analysis.py` (reads
  JSON means into `FIT_VERTEX_X/Y/Z`, points `POCA_VERTEX_FILE` at the
  boost ROOT file); `macro/target/README.md` (two-pass workflow semantics).
- **Answer-point summary (corrected in R1):** (1) ana_dpm.C produces both
  artifacts — the event-level `event_poca` tree in `<prefix>_boost.root`
  and fitted sample-level vertex means/widths in `<prefix>_vtx_fit.json`;
  (2) step 2 reads the JSON means into `FIT_VERTEX_X/Y/Z` and points
  `POCA_VERTEX_FILE` at the boost ROOT file; (3) the `event_poca` tree is
  the primary event-by-event back-propagation source, the fitted-mean
  variables are backwards-compatible fallback information.
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
- **Human decision:** REVISE (Li, 2026-08-24T01:50+02:00)

### n022 R1 correction record (CORRECTED / HUMAN_RE_REVIEW_PENDING)

- **Original human issue:** the initial Gold overemphasized
  `vtx_fit.json` + `FIT_VERTEX_X/Y/Z` and underrepresented the primary
  event-by-event POCA path.
- **event_poca vs vtx_fit.json distinction (verified in locked sources):**
  `macro/target/ana_dpm.C` writes the event-level `event_poca` tree into
  `<prefix>_boost.root` (lines 125/130) and exports fitted sample-level
  vertex means/widths to `<prefix>_vtx_fit.json` (line 895 ff.);
  `poca_step2_analysis.py` reads the JSON means into `FIT_VERTEX_X/Y/Z` and
  points `POCA_VERTEX_FILE` at the boost ROOT file; `macro/target/README.md`
  documents that the Pass-2 PID correlator reads the matching event ID from
  that tree and propagates each event's tracks to its own POCA.
- **Corrected evidence groups:** e1 `macro/target/ana_dpm.C` (production of
  both artifacts — direct implementation evidence); e2
  `macro/target/poca_step2_analysis.py` (step-2 consumption: FIT_VERTEX_*,
  POCA_VERTEX_FILE); e3 `macro/target/README.md` (two-pass workflow
  semantics). Source types are now `code` + `workflow`.
- **Corrected answer-point semantics:** (1) ana_dpm.C produces both
  `<prefix>_boost.root` with the `event_poca` tree and
  `<prefix>_vtx_fit.json` with fitted sample-level means/widths; (2) step 2
  reads the JSON means into `FIT_VERTEX_X/Y/Z` and points
  `POCA_VERTEX_FILE` at the boost ROOT file; (3) for the normal POCA
  workflow the `event_poca` tree is the primary event-by-event
  back-propagation source, with the fitted-mean variables retained as
  backwards-compatible / legacy fallback information.
- **Codex post-correction recommendation:** RECOMMEND_ACCEPT
- **Human re-review:** ACCEPT (Li, 2026-08-24T02:05+02:00; record now `approved` / lifecycle `approved`, not yet `split_frozen`)

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
- **Critical evidence (corrected in R1):** `tracking/PndFtsTrackFinder/README.MD` (package
  documentation); `tracking/PndFtsTrackFinder/PndFtsTrackFinderTask.cxx`
  (branch registration, default names, payload containers).
- **Answer-point summary (corrected in R1):** (1) implemented in
  `tracking/PndFtsTrackFinder` with PndFtsTrackFinderTask as the FairTask
  entry; (2) registers output branches `FtsTrack`, `FtsTrackCand`,
  `FtsTrackAnalytic` (configurable via `SetOutputBranchName`); (3) payload
  types `PndTrack`, `PndTrackCand`, and
  `PndFtsTrackFinder::PndFtsAnalyticTrack` respectively.
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
- **Human decision:** REVISE (Li, 2026-08-24T01:50+02:00)

### n023 R1 correction record (CORRECTED / HUMAN_RE_REVIEW_PENDING)

- **Original human issue:** the initial Gold answered the branch portion
  mainly with payload object types rather than ROOT branch names.
- **Actual branch names (verified in `PndFtsTrackFinderTask.cxx` lines
  21-22/47-49):** default output branches `FtsTrack`, `FtsTrackCand`, and
  `FtsTrackAnalytic` (configurable via `SetOutputBranchName`).
- **Payload/object types:** `FtsTrack` -> `PndTrack`; `FtsTrackCand` ->
  `PndTrackCand`; `FtsTrackAnalytic` ->
  `PndFtsTrackFinder::PndFtsAnalyticTrack` (line/circle equations of the
  candidates).
- **Removed irrelevant required answer point:** the Forward-Tracker-TDR
  (pp. 88-97) provenance point was factual but not required by the user's
  information need; it is removed from `required_answer_points` (it remains
  as non-critical context in the package documentation only).
- **Corrected evidence:** e1 `tracking/PndFtsTrackFinder/README.MD` (package
  documentation); e2 `tracking/PndFtsTrackFinder/PndFtsTrackFinderTask.cxx`
  (actual branch registration, default names, and payload containers).
- **Codex post-correction recommendation:** RECOMMEND_ACCEPT
- **Human re-review:** ACCEPT (Li, 2026-08-24T02:05+02:00; record now `approved` / lifecycle `approved`, not yet `split_frozen`)

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
- **Human decision:** ACCEPT (Li, 2026-08-24T01:50+02:00; record now
  `approved` / lifecycle `approved`, not yet `split_frozen`)

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
- **Human decision:** ACCEPT (Li, 2026-08-24T01:50+02:00; record now
  `approved` / lifecycle `approved`, not yet `split_frozen`)

---

## Batch-wide R1 correction: malformed source identity

All six N2-A records carried a malformed `pflueger_2017` allowed
source-version identity (two hexadecimal characters dropped during the
N2-A transcription). Corrected in n020-n025 to the locked identity
`pflueger_2017@1b6ec987fc1430be085f2a7ba631d634f6580115ff0a90dff090dfcba5e990f3`;
the N1 records already carried the correct identity. A generic validator
rule now rejects any `allowed_source_versions` entry outside the locked
authoritative source-version universe (authority: `data/manifests/source_manifest.json`
plus the declared `curated_panda_domain@1.0` catalog identity), verified by
a targeted negative check (malformed identity injection -> validator FAIL
naming the question and identity; restore -> PASS).

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

Final Batch 1 state (after the 2026-08-24T02:05+02:00 re-review): **6 ACCEPT
/ 0 REVISE / 0 REJECT / 0 PENDING** — n020/n024/n025 accepted at first
review (2026-08-24T01:50+02:00), corrected n021/n022/n023 accepted on
re-review (2026-08-24T02:05+02:00). All six records are `approved` with
reviewer `Li`; they became `split_frozen` during N2 finalization. The
batch-wide malformed
`pflueger_2017` identity is corrected and the generic
locked-source-universe validator rule is active. Priority areas covered:
data_flow/producer-consumer (n020, n022), genuine cross-repository (n021,
footprint re-derived on the corrected annotation), source_location (n023),
implementation_explanation (n024, n025). No exploratory candidates arose
naturally in Batch 1, matching the plan's assignment of exploratory
balancing to Batch 2. Expected status: all answered. Difficulty:
1 simple / 4 moderate / 1 hard.
