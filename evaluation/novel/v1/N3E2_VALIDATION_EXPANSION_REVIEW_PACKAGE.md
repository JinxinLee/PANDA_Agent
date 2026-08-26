# N3-E2 Validation Expansion Review Package

Status: `EXPANSION2_HUMAN_APPROVED / SPLIT_FROZEN`

Dataset: `novel-v1-validation-0.2.0`

Starting approved base: 12 questions / 12 independent families

New candidates: 3 questions / 3 independent families

Human decisions on N3-E2 candidates: 3 `ACCEPT`

Codex recommendations are advisory. The candidates were annotated from locked
sources without inspecting novel-dev, validation, C8, or holdout outcomes.

## n913 / vf013 - RhoTuple row construction and persistence

- **Question:** In a PandaRoot RHO analysis, how do I create candidate-level
  n-tuple rows without predeclaring every branch, keep missing values
  consistent, and persist the finished tree?
- **Intent / status / difficulty:** `api` / `answered` / `simple`.
- **Archetypes:** primary `component_usage`; secondary `workflow_sequence`.
- **Classification:** `representative`. Candidate-level TTree output is a
  routine analysis operation, and Gold already represents RHO documentation
  and analysis-in-task usage forms.
- **Source scope / topology:** one locked PandaRoot Sphinx page,
  documentation-only, single repository, single-hop; not cross-repository.
- **Critical evidence:**
  `Tutorials/tut_04_ntuple.html`, section "Using RhoTuple", independently
  states the Column default/branch behavior, DumpData row commit, and internal
  tree write sequence.
- **Required answer points:** construct `RhoTuple`; use `Column` with stable
  early branch creation and the correct overload; call `DumpData` per
  candidate; write `GetInternalTree()` to the output file.
- **Closest Gold:** g022 and g024.
- **Gold overlap:** intent/task-form overlap is high; RHO entity and the locked
  Sphinx snapshot overlap partially; the exact page and evidence obligation do
  not overlap.
- **Why the Gold information need differs:** g022 asks where RHO data-access
  and PID documentation lives, and g024 asks how analysis is embedded in a
  FairTask. Neither asks how a candidate row is formed and persisted.
- **Closest novel_dev:** nf018 and nf026.
- **Closest validation:** vf002 and vf011.
- **Strict family isolation:** nf018 is MC-truth matching and nf026 is tutorial
  navigation. vf002 selects PID lists and vf011 forms composite candidates.
  The complete vf001-vf012 audit found no family whose minimum answer is the
  `Column` -> `DumpData` -> TTree persistence lifecycle.
- **Novelty types:** `relation`, `task_form`.
- **Domain relevance:** strong; analysis results routinely require
  candidate-level storage for later interactive cuts and correlations.
- **Minimum critical evidence footprint:** one documentation page and one
  critical evidence group.
- **Cross-repository derivation:** not applicable; the minimum footprint uses
  one PandaRoot documentation identity.
- **Uncertainty:** none material. The QA helper inventory on the same page is
  deliberately excluded because it is not needed to answer this API question.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `ACCEPT` by Li at `2026-08-26T17:13+02:00`.

## n914 / vf014 - Runtime-parameter registration and access flow

- **Question:** When adding a custom PandaRoot runtime-parameter set, what
  responsibilities do `PndTutPar`, `PndTutContFact`, and
  `PndTutAccessRTDBTask` have from parameter serialization through container
  registration to task access?
- **Intent / status / difficulty:** `data_flow` / `answered` / `moderate`.
- **Archetypes:** primary `producer_consumer_trace`; secondary
  `implementation_explanation`.
- **Classification:** `representative`. Parameter-container integration is a
  normal FairRoot/PandaRoot framework boundary, while its concrete lifecycle
  is less common in Gold than end-user analysis APIs.
- **Source scope / topology:** three locked PandaRoot source files, one
  repository identity, multi-hop composition; not cross-repository.
- **Critical evidence:**
  `tutorials/rtdb/PndTutPar.cxx` proves named parameter serialization and
  deserialization; `tutorials/rtdb/PndTutContFact.cxx` proves static factory
  registration, accepted contexts, and `PndTutPar` construction;
  `tutorials/rtdb/PndTutAccessRTDBTask.cxx` proves task retrieval, missing-
  container checks, reinitialization, and use. Each group is complementary;
  no source is presented as an interchangeable alternative.
- **Required answer points:** describe `putParams`/`getParams`; describe the
  factory's `FairRuntimeDb` registration, names, contexts, and construction;
  describe `SetParContainers`, `Init`, `ReInit`, and use by the task.
- **Closest Gold:** g089, g098, and g106.
- **Gold overlap:** producer-consumer and module-boundary task forms overlap;
  entities, source files, and minimum evidence do not.
- **Why the Gold information need differs:** those Gold cases trace simulation
  configuration or repository/workflow boundaries. None asks how the runtime
  database materializes a context-qualified parameter object and supplies it
  to a task.
- **Closest novel_dev:** nf014 and nf017.
- **Closest validation:** vf009 and vf010.
- **Strict family isolation:** nf014 compares model-layer ownership and nf017
  defines the persistent `PndTrack` boundary. vf009 resolves magnetic-field
  queries and vf010 joins detector-hit branches in a tracker. All vf001-vf012
  were checked; none requires the parameter serialization/factory/access
  lifecycle.
- **Novelty types:** `relation`, `composition`, `reasoning_topology`.
- **Domain relevance:** strong; reconstruction tasks routinely depend on
  runtime conditions and parameter containers.
- **Minimum critical evidence footprint:** three code files and three critical
  evidence groups. Removing any group loses serialization, registration, or
  consumption respectively.
- **Cross-repository derivation:** not applicable; multiple files within
  PandaRoot do not create a cross-repository case.
- **Uncertainty:** the tutorial factory header carries an inherited stale MVD
  comment, so only executable factory behavior is annotated; the comment is
  not an answer obligation.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `ACCEPT` by Li at `2026-08-26T17:13+02:00`.

## n915 / vf015 - Dalitz interference and projection diagnostics

- **Question:** While studying a three-body decay with PandaRoot's DalitzGUI,
  how can interference leave a resonance band visible in the Dalitz plot while
  its peak moves or disappears in a one-dimensional projection, and which
  built-in views expose the coherent-versus-incoherent effect?
- **Intent / status / difficulty:** `algorithm_theory` / `answered` /
  `moderate`.
- **Archetypes:** primary `theory_explanation`; secondary `component_usage`.
- **Classification:** `representative_but_rare` within the representative
  class. Three-body resonance interpretation is a credible PANDA analysis need
  documented by an official tool, without claiming empirical frequency.
- **Source scope / topology:** one locked PandaRoot Sphinx page,
  documentation-only, single repository, causal single-hop; not
  cross-repository.
- **Critical evidence:** `Tutorials/DalitzGui.html` defines the resonance
  amplitude and phase controls; identifies coherent/incoherent, difference,
  phase, Dalitz, and projection views; and gives didactic examples in which
  interference moves or removes a projected peak while the band remains in
  the Dalitz plot.
- **Required answer points:** explain relative-phase interference; explain
  projections and reflections; identify `Dalitz`, `Dalitz (scat)`, `Dalitz
  In`, `Dalitz Diff`, `Dalitz Ph`, and the mass-squared projections as the
  relevant comparisons; the source defines `Dalitz Diff` only as the
  difference between coherent and incoherent sums, so no sign convention is
  asserted.
- **Closest Gold:** g043 and g045.
- **Gold overlap:** the `algorithm_theory` intent and causal explanation form
  overlap; entity, source, evidence, and minimum answer do not.
- **Why the Gold information need differs:** g043 explains a luminosity-
  extraction equation and g045 explains detector-resolution convolution.
  Neither concerns coherent decay amplitudes or projection artifacts.
- **Closest novel_dev:** nf009 and nf026.
- **Closest validation:** vf007 and vf011.
- **Strict family isolation:** nf009 compares elastic-scattering models and
  nf026 navigates the analysis tutorial sequence. vf007 compares two detector
  systems and vf011 constructs decay candidates. The vf001-vf012 audit found
  no family about interference-driven resonance visibility or Dalitz
  projection interpretation.
- **Novelty types:** `relation`, `reasoning_topology`, `task_form`.
- **Domain relevance:** moderate; the need is specific but directly tied to
  PANDA three-body amplitude analysis.
- **Minimum critical evidence footprint:** one documentation page and one
  critical evidence group.
- **Cross-repository derivation:** not applicable; one PandaRoot documentation
  identity suffices.
- **Uncertainty:** the tool is specialized. Classification therefore remains
  representative-but-rare rather than a representative-core claim.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `ACCEPT` by Li at `2026-08-26T17:13+02:00`.

## Discarded pre-ID ideas

- **QuickAna one-line workflow:** discarded because the minimum answer would
  broadly repackage vf002 PID selection and vf011 decay combinatorics, with
  fitting options layered on top. That boundary was not sufficiently isolated
  for this final small batch.
- **PndPrintFairLinks branch printer:** discarded because its Sphinx page is a
  thin API stub and the code-driven question naturally became a niche branch-
  filter inventory rather than a strong user information need.
- **Additional RHO fitter operation:** retained as a discard from the N3-E
  audit; it remains adjacent to vf011 and to Gold analysis-in-task coverage.
- **Event-time/buffer utility:** retained as a discard because it risks
  narrowing frozen time-ordering family nf029.
- **Detector-specific parameter-container substitution:** discarded in favor
  of the generic runtime-database tutorial. Replacing the detector name would
  not create a new family.
- **Forced non-answered, exploratory, or cross-repository record:** discarded
  because no natural locked-source need required those classifications.

## Authoritative human review

Reviewer: `Li`
Reviewed commit: `f100f357e83b56e2799c2bb5bf89f2073b1c5872`
Reviewed at: `2026-08-26T17:13+02:00`

Authoritative decisions:

- n913: `ACCEPT`
- n914: `ACCEPT`
- n915: `ACCEPT`

Totals: `3 ACCEPT / 0 REVISE / 0 REJECT`.

The accepted semantic records and their evidence contracts were retained
unchanged. Their dataset review status is now `approved`, reviewer is `Li`,
and the sidecar lifecycle is `approved` at review time. N3-VF then finalized
these three records as `split_frozen`; this review does not itself authorize
measurement.

## Review boundary

The authoritative decision covers each question, critical evidence, answer
points, Gold comparison, strict family isolation, representativeness, and
sidecar metadata. No revised or rejected record remains in this batch.
