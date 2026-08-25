# N2-B Batch 2 Review Package — Expansion Candidates n026-n031

Status: **BATCH2_HUMAN_REVIEWED / R1_RE_REVIEW_PENDING** (2026-08-25).

Human authorization: N2-B — Batch 2 Balancing Curation, authorized
2026-08-24T02:17+02:00. Human review was performed by `Li` at
2026-08-24T02:42+02:00 against candidate commit
`d70eb1b85bc704e329207edd3874403bf4672d3b`. The authoritative decisions were
1 ACCEPT (`n027`) and 5 REVISE (`n026`, `n028`, `n029`, `n030`, `n031`);
there were no REJECT or PENDING decisions. The R1 corrections below are
Codex-prepared corrections and remain subject to explicit human re-review.
Batch 2 is the balancing round under the approved N2 plan
(`N2_FULL_NOVEL_DEV_EXPANSION_PLAN.md`, Rev 1): documentation_navigation,
exploratory, workflow/comparison/theory balancing. The Batch 1-discarded
macro/run stage-chain idea was NOT resurrected. The 22 existing records are
untouched; the dataset lineage remains 0.3.0 expansion-in-progress
(`novel-v1-dev-0.3.0`, identity `novel-v1-dev-expansion`, status
`EXPANSION_IN_PROGRESS`, 28 loaded records = 23 human-approved + 5 corrected
REVISE records awaiting re-review).

Curation boundary: no PANDA Agent component was run, and no benchmark,
novel, or C8 outcome was inspected or used for candidate selection. Parallel
C8 development (ACTIVE, `C8-A1R1 PASS`, `C8-A1
PASS_AFTER_CONTRACT_FIDELITY_REPAIR`, `C8-A2 NEXT_ELIGIBLE / NOT_STARTED`) was
left untouched; only its lifecycle status was preserved in shared documents.
All evidence was established by static locked-source inspection.

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
- **Critical evidence:** `Tutorials/tut_outline.html`, which names the
  "Simulation and Analysis in PandaRoot with RHO" sequence, its six parts,
  and the `tutorials/rho` file location. The outline alone supports
  the remaining answer obligations.
- **Answer-point summary:** (1) the documented learning path is the RHO
  tutorial sequence with example files in tutorials/rho, starting from
  Preface/Requirements; (2) six parts — simulating signal events (including
  fast simulation), analysis of signal events, analysis in a task, n-tuple
  analysis with RhoTuple, quick analysis, and event filtering for background
  events.
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
- **Human decision:** REVISE (Li, 2026-08-24T02:42+02:00)

### n026 R1 correction

- Removed the unasked companion-resource critical answer point.
- Removed `Tutorials/tut_02_00_analysis.html` from critical Gold evidence;
  `Tutorials/tut_outline.html` independently supports the sequence and
  progression that the question asks for.
- Post-correction Codex recommendation: `RECOMMEND_ACCEPT`.
- Human re-review: `PENDING`.

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
- **Human decision:** ACCEPT (Li, 2026-08-24T02:42+02:00)
- **Lifecycle:** `approved`; `review_status: approved`; not
  `split_frozen`. Query, Gold facts, evidence groups, family, novelty,
  representativeness, difficulty, and archetypes are unchanged.

## n028 / nf028 — softrig trigger-style analysis (EXPLORATORY)

- **Question:** How does PandaRoot's softrig workflow produce
  software-trigger tags, and how are those OnlineFilterInfo decisions exposed
  to a downstream analysis task?
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
- **Scope:** pandaroot only; single_source; producer_consumer; descriptive.
- **Critical evidence:** `softrig/PndSoftTriggerTask.cxx` (registers the
  OnlineFilterInfo branch and writes per-mode tag counts);
  `softrig/PndOnlineFilterInfo.h` (decision container with 65 modes,
  per-mode counts, and total-tag accessors); and
  `softrig/PndAnaWithTrigger.cxx` (downstream lookup through
  FairRootManager and reads of Tagged(), GetNTagTotal(), and GetNTag()).
- **Answer-point summary:** (1) PndSoftTriggerTask creates and registers the
  OnlineFilterInfo container, evaluates active trigger lines, and writes
  per-mode tag counts; (2) PndOnlineFilterInfo stores the resulting mode and
  total tag information; (3) PndAnaWithTrigger consumes those decisions from
  FairRootManager and exposes them in downstream analysis tuples.
- **Closest exposed Gold:** none_found.
- **Closest active novel families:** none equivalent.
- **Novelty:** entity + relation.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** REVISE (Li, 2026-08-24T02:42+02:00)

### n028 R1 correction

- Original problem: the question implied event rejection before full
  processing, while the annotation showed only a downstream analysis task and
  the result container.
- Corrected question: asks for the source-supported softrig
  producer/container/downstream-consumer relationship without claiming
  pre-processing rejection.
- Producer evidence: `PndSoftTriggerTask.cxx` creates
  `PndOnlineFilterInfo`, registers `OnlineFilterInfo`, and writes
  per-mode counts in `Exec`.
- Decision-container evidence: `PndOnlineFilterInfo.h` defines the
  65-mode per-mode and total tag accessors.
- Downstream consumer evidence: `PndAnaWithTrigger.cxx` retrieves
  `OnlineFilterInfo` from `FairRootManager` and reads the
  decision values.
- Exploratory classification remains justified: the corrected
  producer-to-consumer relation is domain-relevant and remains absent from
  exposed Gold and the active novel set.
- Post-correction Codex recommendation: `RECOMMEND_ACCEPT`.
- Human re-review: `PENDING`.

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
  `timebased/Buffers/PndRingSorter.cxx` (the implementation that
  advances the lower-bound window and emits timestamp-ordered entries).
- **Answer-point summary:** (1) fixed-size ring buffer buckets timestamped
  elements into cells of configurable time width, so interleaved data is
  ordered by time rather than arrival; (2) WriteOutElements releases
  entries from the lower-bound pointer up to an index, and
  WriteOutElement emits each cell's multimap entries in timestamp order to
  GetOutputData.
- **Closest exposed Gold:** none_found.
- **Closest active novel families:** none equivalent.
- **Novelty:** entity + task_form.
- **Known uncertainty:** none material.
- **Codex recommendation:** RECOMMEND_ACCEPT
- **Human decision:** REVISE (Li, 2026-08-24T02:42+02:00)

### n029 R1 correction

- Removed the unsupported claim that `PndBufferTestTask.h` demonstrates
  driving the buffer; the header is an empty task stub for this purpose.
- Added `timebased/Buffers/PndRingSorter.cxx` as critical implementation
  evidence.
- Corrected semantics: `AddElement` buckets timestamps by cell width;
  `WriteOutElements`/`WriteOutElement` release older cells from the
  lower-bound window, and the cell `std::multimap` emits entries by
  timestamp key.
- Post-correction Codex recommendation: `RECOMMEND_ACCEPT`.
- Human re-review: `PENDING`.

## n030 / nf030 — luminosity IP-alignment preprocessing (REPRESENTATIVE)

- **Question:** Before the luminosity fit runs, the framework applies a
  coordinate-system preprocessing step to the track data. Why is the
  standard laboratory frame insufficient there, and what does the IP
  alignment transformation accomplish?
- **Intent:** algorithm_theory — **Expected status:** answered —
  **Difficulty:** moderate
- **Primary task archetype:** theory_explanation — **Class:** representative
  (fit moderate / relevance strong / representative_but_rare /
  KEEP_REPRESENTATIVE)
- **Representativeness rationale:** the information need is a normal,
  domain-relevant explanation of a luminosity-analysis preprocessing
  requirement. Gold theory and explanation cases provide task-form analogues
  even though this exact interaction-point alignment topic is novel. Novelty
  does not by itself make the question exploratory.
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
- **Human decision:** REVISE (Li, 2026-08-24T02:42+02:00)

### n030 R1 correction

- Gold query, evidence selector, required answer points, intent, and family
  were unchanged.
- Corrected the sidecar classification from `exploratory` to
  `representative`.
- New values: benchmark reference fit `moderate`, domain relevance
  `strong`, corpus tail `representative_but_rare`, disposition
  `KEEP_REPRESENTATIVE`.
- Post-correction Codex recommendation: `RECOMMEND_ACCEPT`.
- Human re-review: `PENDING`.

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
- **Scope:** sphinx documentation only (single_source,
  single_repository); topology comparison; descriptive.
- **Critical evidence:** sphinx `EventGenerators/EventGenerators.html`
  (three categories: background — FTF current standard, DPM previous still
  usable; event — EvtGen for one specific channel; box/particle guns —
  BoxGenerator random vs FixStepParticleGun fixed pattern).
- **Answer-point summary:** the three documented generator categories and
  their roles: FTFGenerator is the current standard background generator,
  DPMGenerator is the previous still-usable background generator, EvtGen
  covers a specific signal channel, and BoxGenerator/FixStepParticleGun
  provide controlled particles rather than a full interaction.
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
- **Human decision:** REVISE (Li, 2026-08-24T02:42+02:00)

### n031 R1 correction

- Removed the unasked `macro/run/sim_complete.C` /
  `inputGenerator` configuration obligation and its critical evidence
  group.
- Preserved the taxonomy information need and its distinction from nf003.
- Resulting critical evidence topology: one documentation group,
  single-source/single-repository comparison.
- Post-correction Codex recommendation: `RECOMMEND_ACCEPT`.
- Human re-review: `PENDING`.

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

6 candidates (n026-n031 / nf026-nf031): n027 is human ACCEPTED with
`review_status: approved` / sidecar `lifecycle: approved`; the other
five are human REVISE decisions, corrected in R1 and remain
`review_status: draft` / `reviewer: null` / sidecar `lifecycle: draft`
pending re-review. Balancing coverage:
documentation_navigation 2 (n026, n027 — archetype moves 0 -> 2),
exploratory 2 (n028, n029), representative theory_explanation 1 (n030),
concept_comparison +1 (n031), theory_explanation +1 (n030 primary).
Exploratory investigation pool: 4 regions investigated (softrig, timebased,
thesis rare topics, second cross-repo), 2 admitted as exploratory and one
reclassified representative; discarded material is recorded above. Expected
status: all answered. Difficulty: 2 simple / 4 moderate / 0 hard. Total
loaded dataset: 28 records (23 human-approved + 5 corrected REVISE awaiting
re-review). This is structural curation coverage, not a performance
statement.
