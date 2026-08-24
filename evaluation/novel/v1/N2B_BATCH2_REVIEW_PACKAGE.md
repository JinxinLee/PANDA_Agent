# N2-B Batch 2 Review Package — Expansion Candidates n026-n031

Status: **BATCH2_DRAFTED / HUMAN_REVIEW_PENDING** (2026-08-24).

Human authorization: N2-B — Batch 2 Balancing Curation, authorized
2026-08-24T02:17+02:00. Codex recommendations below are advisory only; every
`Human decision` field is PENDING and no reviewer has inspected these
candidates. Batch 2 is the balancing round under the approved N2 plan
(`N2_FULL_NOVEL_DEV_EXPANSION_PLAN.md`, Rev 1): documentation_navigation,
exploratory, workflow/comparison/theory balancing. The Batch 1-discarded
macro/run stage-chain idea was NOT resurrected. The 22 existing records are
untouched; the dataset lineage remains 0.3.0 expansion-in-progress
(`novel-v1-dev-0.3.0`, identity `novel-v1-dev-expansion`, status
`EXPANSION_IN_PROGRESS`, 28 loaded records = 22 human-approved + 6 pending
drafts).

Curation boundary: no PANDA Agent component was run, and no benchmark,
novel, or C8 outcome was inspected or used for candidate selection. Parallel
C8 development (ACTIVE, C8-A0 PASS) was left untouched; only its lifecycle
status was preserved in shared documents. All evidence was established by
static locked-source inspection.

---

## n026 / nf026 — RHO analysis tutorial sequence

- **Question:** As a newcomer I want to learn PandaRoot analysis with the
  RHO framework properly. Which official tutorial sequence covers this, and
  what does it walk through from signal simulation to background filtering?
- **Intent:** usage — **Expected status:** answered — **Difficulty:**
  simple
- **Primary task archetype:** documentation_navigation — **Class:**
  representative (fit moderate / relevance strong / rare)
- **Scope:** locked sphinx snapshot only (single_source,
  single_repository); topology single_hop; descriptive; source type
  documentation.
- **Critical evidence:** `Tutorials/tut_outline.html` (the "Simulation and
  Analysis in PandaRoot with RHO" sequence with its six parts and
  tutorials/rho file location); `Tutorials/tut_02_00_analysis.html` (the
  analysis-section entry page of the same sequence).
- **Answer-point summary:** (1) the documented learning path is the RHO
  tutorial sequence with example files in tutorials/rho, starting from
  Preface/Requirements; (2) six parts — simulating signal events (including
  fast simulation), analysis of signal events, analysis in a task, n-tuple
  analysis with RhoTuple, quick analysis, and event filtering for background
  events; (3) the section also points to companion resources (DalitzGUI,
  event generators, tools, MC track analysis, event display, Jupyter,
  Docker).
- **Closest exposed Gold:** g009, g022 (documentation-navigation, other
  resources; information_need overlap low).
- **Closest active novel families:** none equivalent — no active family
  asks for the tutorial sequence (n027 below covers the separate Jupyter
  interface).
- **Novelty:** entity + task_form.
- **Domain relevance:** the documented onboarding path for PandaRoot
  analysis; a routine newcomer need.
- **Known uncertainty:** none material.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n027 / nf027 — Jupyter notebook interface

- **Question:** I would rather drive quick PandaRoot studies from Python
  notebooks than from ROOT macros. What does the documentation provide for
  using PandaRoot with Jupyter, and how can I start a kernel without
  installing anything extra?
- **Intent:** usage — **Expected status:** answered — **Difficulty:**
  simple
- **Primary task archetype:** documentation_navigation (secondary
  workflow_sequence) — **Class:** representative (fit moderate / relevance
  strong / rare)
- **Scope:** locked sphinx snapshot only (single_source,
  single_repository); topology single_hop; descriptive.
- **Critical evidence:** `Jupyter/Jupyter.html` (PyROOT / %%cpp mixing;
  kernel startup via config.sh and the two notebook environment variables);
  `Jupyter/notebooks/PandaRootPySim.html` (the shipped example notebook).
- **Answer-point summary:** (1) PandaRoot is natively C++ libraries driven
  through ROOT macros, but PyROOT bindings and the %%cpp magic allow mixing
  C++ into Python notebooks; (2) kernel startup without extra installation:
  source `<build>/config.sh -p`, export `JUPYTER_CONFIG_DIR` and
  `JUPYTER_PATH` to `$SIMPATH/etc/root/notebook`, then `jupyter notebook`;
  (3) the PandaRootPySim example notebook demonstrates a Python-style
  simulation.
- **Closest exposed Gold:** g009, g010 (documentation-navigation,
  information_need overlap low).
- **Closest active novel families:** nf026 is the nearest — separated
  because nf026 covers the RHO analysis tutorial sequence while n027 covers
  the notebook interface and kernel setup (different documented resources
  and different user goals).
- **Novelty:** entity + task_form.
- **Domain relevance:** notebook-driven quick studies are an increasingly
  common usage mode documented in the locked snapshot.
- **Known uncertainty:** none material.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n028 / nf028 — softrig trigger-style analysis (EXPLORATORY)

- **Question:** Can a PandaRoot analysis apply trigger-style event tagging
  before committing to full processing, and which softrig components carry
  the online-filter decisions?
- **Intent:** usage — **Expected status:** answered — **Difficulty:**
  moderate
- **Primary task archetype:** implementation_explanation — **Class:**
  EXPLORATORY (fit weak / relevance moderate / exploratory_tail /
  KEEP_EXPLORATORY)
- **Exploratory rationale:** domain relevance (event tagging and online
  filtering are real PANDA high-rate analysis needs) plus substantive
  exploratory properties: legitimate underrepresented need and
  coverage-frontier value — the softrig package is covered by no exposed
  Gold case (closest_case_assessment: none_found) and no active novel
  family.
- **Scope:** pandaroot only; single_source; single_hop; descriptive.
- **Critical evidence:** `softrig/PndAnaWithTrigger.h` (FairTask building a
  trigger-style analysis around PndAnalysis with RhoMassParticleSelector /
  RhoTuple / PndRhoTupleQA members); `softrig/PndOnlineFilterInfo.h`
  (online-filter result container: OFIMAXMODES 65 modes, per-mode tag
  counts, totals, Reset/Print).
- **Answer-point summary:** (1) PndAnaWithTrigger wraps PndAnalysis in a
  trigger-style FairTask constructed with beam momentum and output name;
  (2) PndOnlineFilterInfo carries the online-filter decisions as per-mode
  tag counts queryable without inspecting reconstructed objects.
- **Closest exposed Gold:** none_found.
- **Closest active novel families:** none equivalent.
- **Novelty:** entity + relation.
- **Known uncertainty:** answer points are grounded in the locked header
  declarations; the reviewer may confirm the Exec behaviour in
  PndAnaWithTrigger.cxx matches the task-role reading.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n029 / nf029 — timebased ring-buffer ordering (EXPLORATORY)

- **Question:** In time-based simulation, detector data from successive
  interactions arrives interleaved in time. How does PandaRoot's timebased
  buffering sort such data into processing order?
- **Intent:** algorithm_implementation — **Expected status:** answered —
  **Difficulty:** moderate
- **Primary task archetype:** implementation_explanation — **Class:**
  EXPLORATORY (fit weak / relevance moderate / exploratory_tail /
  KEEP_EXPLORATORY)
- **Exploratory rationale:** domain relevance (time-structured data is
  central to PANDA's continuous high-luminosity beam) plus substantive
  exploratory properties: uncommon but plausible mechanism question and
  coverage-frontier value — timebased buffering is unrepresented in Gold
  (none_found) and in the active novel set.
- **Scope:** pandaroot only; single_source; single_hop; descriptive.
- **Critical evidence:** `timebased/Buffers/PndRingSorter.h` (ring buffer
  with cellWidth bucketing, AddElement by timestamp,
  WriteOutElements/WriteOutAll ordered release, GetBufferSize);
  `timebased/Buffers/PndBufferTestTask.h` (usage-demonstrating task).
- **Answer-point summary:** (1) fixed-size ring buffer buckets timestamped
  elements into cells of configurable time width, so interleaved data is
  ordered by time rather than arrival; (2) WriteOutElements releases
  entries from the lower-bound pointer up to an index, handing the data to
  GetOutputData in time order; (3) abstract base class with type-specific
  CreateElement implementations; PndBufferTestTask demonstrates the usage.
- **Closest exposed Gold:** none_found.
- **Closest active novel families:** none equivalent.
- **Novelty:** entity + task_form.
- **Known uncertainty:** none material.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n030 / nf030 — luminosity IP-alignment preprocessing (EXPLORATORY)

- **Question:** Before the luminosity fit runs, the framework applies a
  coordinate-system preprocessing step to the track data. Why is the
  standard laboratory frame insufficient there, and what does the IP
  alignment transformation accomplish?
- **Intent:** algorithm_theory — **Expected status:** answered —
  **Difficulty:** moderate
- **Primary task archetype:** theory_explanation — **Class:** EXPLORATORY
  (fit weak / relevance strong / exploratory_tail / KEEP_EXPLORATORY)
- **Exploratory rationale:** domain relevance (interaction-point alignment
  directly conditions luminosity extraction) plus substantive exploratory
  properties: unusual but plausible single-source theory composition and
  coverage-frontier value (the alignment preprocessing step is unrepresented
  in Gold and the active novel set; none_found).
- **Scope:** li_2026 paper only (pdf_page 74); single_source; paper_only;
  single_hop; descriptive.
- **Critical evidence:** locked thesis page 74 ("IP Alignment and
  Coordinate Transformation": mean interaction point from POCA-coordinate
  arithmetic mean, global coordinate transformation before the luminosity
  fit, azimuthal-symmetry restoration for the 2D fit model).
- **Answer-point summary:** (1) the laboratory frame assumes the IP at the
  origin while the actual mean IP is measured from POCA coordinates;
  (2) a global coordinate transformation virtually shifts the detector
  system onto the measured IP before the fit; (3) this restores the
  azimuthal symmetry required by the 2D luminosity fit model.
- **Closest exposed Gold:** none_found (analogue g043 is a task-form
  analogue only).
- **Closest active novel families:** nf009 (elastic-model existence) and
  nf014 (directory roles) are distinct needs.
- **Novelty:** entity + nontrivial_expression.
- **Known uncertainty:** the page anchor is a single locked-thesis page;
  the reviewer may verify the surrounding chapter context.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

## n031 / nf031 — event-generator taxonomy

- **Question:** For different studies I need realistic background, one
  specific signal channel, and simple particle scans. How do PandaRoot's
  event-generator categories differ, and which generator is the current
  standard for background?
- **Intent:** usage — **Expected status:** answered — **Difficulty:**
  moderate
- **Primary task archetype:** concept_comparison (secondary
  component_usage) — **Class:** representative (fit moderate / relevance
  strong / core)
- **Scope:** sphinx documentation + pandaroot macro (cross_source,
  single_repository); topology comparison; descriptive.
- **Critical evidence:** sphinx `EventGenerators/EventGenerators.html`
  (three categories: background — FTF current standard, DPM previous still
  usable; event — EvtGen for one specific channel; box/particle guns —
  BoxGenerator random vs FixStepParticleGun fixed pattern);
  `macro/run/sim_complete.C` (inputGenerator selection syntax:
  dec-file / dpm / ftf / box:type(pdg,mult):p(...):tht(...):phi(...)).
- **Answer-point summary:** (1) the three documented generator categories
  and their roles, including FTFGenerator as the current standard
  background generator; (2) generators are selected in the simulation
  macros through the inputGenerator string.
- **Closest exposed Gold:** g011, g051 (concept-comparison, other pairs;
  information_need overlap low).
- **Closest active novel families:** nf003 is the nearest — separated
  because nf003 asks which generator suits a fixed-step acceptance scan
  (single-component selection), while n031 asks for the category taxonomy
  and the current background standard. Flagged for reviewer attention as
  the closest family pair in this batch.
- **Novelty:** entity + composition.
- **Domain relevance:** choosing the generator category is a routine
  prerequisite of every simulation study.
- **Known uncertainty:** family proximity to nf003 (see above); the
  taxonomy-level need is judged distinct from the scenario-level need.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** PENDING

---

## Discarded pre-ID sampling ideas (no IDs consumed)

- **macro/run stage-chain re-entry (workflow_sequence):** the Batch
  1-discarded idea was deliberately not resurrected; no sharper independent
  information need emerged during Batch 2 investigation beyond what n021
  (cross-repository workflow) and n022 (POCA artifact flow) already cover.
- **KOALA-related thesis material (exploratory):** keyword search of the
  locked li_2026 thesis found KOALA only as a background mention in the
  HESR layout description (pages 38/40) — insufficient substance for an
  information need; karavdina's Millepede/alignment chapters could not be
  page-verified from the available locked extractions within this round, so
  no candidate was forced.
- **Second cross-repository case:** no independently necessary two-identity
  information need arose outside the LuminosityFit/PandaRoot workflow
  already covered by n021; no candidate was manufactured.
- **version_conflict / clarification_required cases:** no genuine same-need
  cross-version conflict or genuine ambiguity case was statically
  demonstrated; no status-class candidate was manufactured.
- **luminosityfit Slurm-agent container workflow:** the README section
  could not be located with sufficient precision in the locked snapshot
  during this round; the idea is recorded for possible later investigation
  and no ID was consumed.

## Batch summary for the reviewer

6 candidates (n026-n031 / nf026-nf031), all `review_status: draft`,
`reviewer: null`, sidecar `lifecycle: draft`. Balancing coverage:
documentation_navigation 2 (n026, n027 — archetype moves 0 -> 2),
exploratory 3 (n028, n029, n030 — class moves 0 -> 3, each admitted under
domain relevance plus substantive exploratory properties),
concept_comparison +1 (n031), theory_explanation +1 (n030 primary).
Exploratory investigation pool: 4 regions investigated (softrig, timebased,
thesis rare topics, second cross-repo), 3 admitted, 1+ discarded as
recorded above. Expected status: all answered. Difficulty: 2 simple /
4 moderate / 0 hard. Total loaded dataset: 28 records (22 human-approved +
6 pending). This is structural curation coverage, not a performance
statement.
