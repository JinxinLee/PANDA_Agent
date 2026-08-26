# N3-E Validation Expansion Review Package

Status: `BATCH1_HUMAN_APPROVED`

Dataset: `novel-v1-validation-0.2.0`

Frozen pilot: 6 approved / 6 `split_frozen`

N3-E expansion: 6 approved candidates / 6 independent families

Human decisions on N3-E candidates: 6 ACCEPT / 0 REVISE / 0 REJECT

Codex recommendations are advisory. The six new candidates were independently
annotated from locked sources without inspecting novel-dev, validation, or C8
outcomes. Human approval does not freeze these records.

## Authoritative human review

- **Reviewer:** Li
- **Timestamp:** `2026-08-26T15:36+02:00`
- **Reviewed commit:** `fa902109123c17b92297c6839fd4664c659ff3c5`
- **Decisions:** n907 `ACCEPT`; n908 `ACCEPT`; n909 `ACCEPT`; n910
  `ACCEPT`; n911 `ACCEPT`; n912 `ACCEPT`.
- **Totals:** 6 `ACCEPT`; 0 `REVISE`; 0 `REJECT`.
- **Lifecycle:** n907-n912 are human-approved but are not `split_frozen`.

## n907 / vf007 - Barrel and Endcap DIRC comparison

- **Question:** PANDA uses both a Barrel DIRC and an Endcap Disc DIRC for
  charged-hadron identification. How do their radiator and photon-readout
  geometries, angular coverage, and pion-kaon momentum reach complement each
  other?
- **Intent / status / difficulty:** `algorithm_theory` / `answered` /
  `moderate`.
- **Archetypes:** primary `concept_comparison`; secondary
  `theory_explanation`.
- **Classification:** `representative`. The Gold benchmark contains detector
  theory and concept-comparison task forms, and charged-hadron PID coverage is
  independently central to PANDA.
- **Source scope / topology:** paper-only, one locked `li_2026` source,
  comparison topology; single repository identity is not applicable and this
  is not cross-repository.
- **Critical evidence:** `li_2026`, PDF pages 46-47, jointly describes the
  shared fused-silica/MCP-PMT principle, Barrel bar/prism/lens geometry and
  22-140 degree coverage, and Endcap quadrant/plate/focusing-element geometry
  and 5-22 degree coverage.
- **Answer obligations:** contrast geometry/readout path; report the
  complementary angular ranges; distinguish the documented approximately
  3.5 and 4 GeV/c pion-kaon reaches.
- **Closest exposed Gold:** g051 and g053. Overlap: `algorithm_theory`,
  concept comparison, and detector-property explanation task forms. No DIRC
  entity, subsystem, page, or evidence overlap. The minimum need is the
  relationship between two PANDA DIRC designs, not an LMD concept distinction
  or sensor-property explanation.
- **Closest frozen novel_dev:** nf008 and nf031. nf008 compares LMD
  track-search algorithms; nf031 compares event-generator categories. The
  shared comparison form does not make the detector-PID information need the
  same family.
- **Closest frozen validation:** vf002 and vf004. vf002 names a DRC PID
  classifier while asking how RHO selects candidates; vf004 explains EMC
  clustering and bump splitting. Neither asks how two DIRC detector systems
  complement one another.
- **Novelty / rationale:** `relation`, `task_form`; it measures a new
  detector-system relation within a representative Gold-like question form.
- **Independent relevance:** analysts and detector developers need to know
  which PID device covers each angular and momentum region.
- **Minimum critical footprint:** one paper source, pages 46-47.
- **Cross-repository derivation:** not applicable; no repository source is
  required.
- **Known uncertainty:** the momentum reaches and geometry are version-bound
  to the locked thesis description and are not claims about later detector
  revisions.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `ACCEPT`.

## n908 / vf008 - Reconstructed-track to PID-candidate flow

- **Question:** In PandaRoot PID reconstruction, how does PndPidCorrelator turn
  a configured PndTrack branch into PidChargedCand records, and how does a
  track's barrel, forward, or combined type control the detector information
  attached to each candidate?
- **Intent / status / difficulty:** `data_flow` / `answered` / `moderate`.
- **Archetypes:** primary `producer_consumer_trace`; secondary
  `implementation_explanation`.
- **Classification:** `representative`; both source-location and
  producer-consumer traces recur in Gold, and the reconstruction-to-PID
  boundary is a routine analysis dependency.
- **Source scope / topology:** PandaRoot code, single repository,
  producer-consumer.
- **Critical evidence:** `pid/PidCorr/PndPidCorrelator.cxx` proves candidate
  construction and links, region-based detector-set selection, detector-info
  population, and `PidChargedCand` registration.
- **Answer obligations:** preserve input track association in each
  `PndPidCandidate`; select barrel/forward/both detector-info sets from
  `PndTrack::TrackType`; register the enriched candidate array under the
  configured output name.
- **Closest exposed Gold:** g028 and g087. Overlap with g028 is high for the
  `PndPidCorrelator` entity, file, and source; g028 asks only where it is
  implemented. g087 supplies the producer-consumer task analogue for an LMD
  adapter. Neither asks for the track-region-dependent PID enrichment flow.
- **Closest frozen novel_dev:** nf017 and nf019. nf017 defines fields on the
  persistent `PndTrack`; nf019 explains how a Kalman task produces fitted
  tracks. This candidate begins at those reconstructed tracks and traces a
  separate PID boundary.
- **Closest frozen validation:** vf002 and vf005. vf002 consumes PID
  probabilities through RHO `FillList`; vf005 aggregates homogeneous track
  arrays. Neither produces linked PID candidates or selects detector
  correlations by track region.
- **Novelty / rationale:** `relation`, `reasoning_topology`, `task_form`;
  entity and evidence overlap with Gold are intentionally retained because
  the minimum user operation is different.
- **Independent relevance:** downstream particle identification depends on
  auditable links from each PID candidate back to its reconstructed track and
  the detector information applicable to that track.
- **Minimum critical footprint:** one PandaRoot implementation file.
- **Cross-repository derivation:** one repository identity; not
  cross-repository.
- **Known uncertainty:** optional neutral-candidate behavior is outside the
  question and annotation.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `ACCEPT`.

## n909 / vf009 - Multi-part magnetic-field lookup

- **Question:** When PandaRoot uses a multi-part magnetic field, how does
  PndMultiField choose which field map supplies the value at a space point,
  and how does the selected PndFieldMap evaluate that global point on its
  grid?
- **Intent / status / difficulty:** `algorithm_implementation` / `answered` /
  `moderate`.
- **Archetypes:** primary `implementation_explanation`; no secondary
  archetype.
- **Classification:** `representative`; implementation cooperation is a
  recurring Gold task, and magnetic-field lookup is a general simulation and
  tracking service even though the code surface is less user-facing.
- **Source scope / topology:** PandaRoot code, one repository, multi-hop across
  two complementary implementation files.
- **Critical evidence:** group one uses `field/PndMultiField.cxx` for ordered
  z-coverage selection and the zero-field fallback; group two uses
  `field/PndFieldMap.cxx` for global-to-local translation, bounds/grid-cell
  selection, and interpolation. Neither file is an alternative for the other.
- **Answer obligations:** state first-covering-map precedence rather than map
  summation; explain center-position subtraction and bounds checking; explain
  interpolation from the eight grid-cell corners.
- **Closest exposed Gold:** g059 and g064. Overlap is the implementation
  explanation form only; entities, subsystem, sources, and evidence do not
  overlap. The minimum need is field-service lookup rather than detector
  smearing or fit-model assembly.
- **Closest frozen novel_dev:** nf024 and nf029. nf024 compares two track
  propagators that consume a magnetic field; nf029 explains time-ordering in
  a ring buffer. Neither defines how a field value is selected and
  interpolated.
- **Closest frozen validation:** vf004. Both are code-backed implementation
  explanations, but EMC clustering/bump splitting has no shared obligation
  with field lookup.
- **Novelty / rationale:** `relation`, `composition`,
  `reasoning_topology`; the information need composes an ordered service
  boundary with the selected map's coordinate evaluation.
- **Independent relevance:** field configuration and interpolation directly
  affect simulation and fitted-track transport without being a question about
  one specific propagator.
- **Minimum critical footprint:** two files in the same PandaRoot repository.
- **Cross-repository derivation:** minimum repository count is one.
- **Known uncertainty:** the annotation describes the locked implementation's
  precedence behavior; it does not generalize to other PandaRoot versions.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `ACCEPT`.

## n910 / vf010 - MVD/GEM tracking module boundary

- **Question:** Which PandaRoot tracking component joins MVD pixel and strip
  hits with GEM hits, what branch boundary does it expose, and how does it
  preserve the contributing detector hits in its track candidates?
- **Intent / status / difficulty:** `module_structure` / `answered` /
  `moderate`.
- **Archetypes:** primary `repository_structure`; secondary
  `producer_consumer_trace`.
- **Classification:** `representative`; source ownership and branch
  boundaries recur in Gold, while a combined MVD/GEM track candidate is an
  independently relevant reconstruction object.
- **Source scope / topology:** PandaRoot code, one repository,
  producer-consumer.
- **Critical evidence:** the single implementation
  `tracking/PndMvdGemTrackFinderOnHits/PndMvdGemTrackFinderOnHits.cxx`
  establishes all input branches, output types/names, and the branch-ID plus
  hit-index links added to each sorted candidate.
- **Answer obligations:** identify `PndMvdGemTrackFinderOnHits`; list
  `MVDHitsPixel`, `MVDHitsStrip`, and `GEMHit`; identify `MVDGEMTrack` and
  `MVDGEMTrackCand`; explain how contributing hits remain linked.
- **Closest exposed Gold:** g098 and g104. Overlap is module-boundary and
  producer-consumer task form. Gold covers framework/LuminosityFit and LMD
  reconstruction/QA boundaries, not this MVD/GEM component or evidence.
- **Closest frozen novel_dev:** nf017 and nf023. nf017 defines the resulting
  `PndTrack` object, and nf023 locates the FTS finder and lists its branches.
  This candidate instead asks which cross-detector module consumes three hit
  branches and preserves their identities in a track candidate.
- **Closest frozen validation:** vf005. vf005 merges completed `PndTrack`
  arrays; n910 is the earlier hit-to-track module boundary and is not an
  entity substitution for track aggregation.
- **Novelty / rationale:** `relation`, `composition`, `task_form`; the new
  relation is MVD/GEM detector-hit ownership within one tracking component.
- **Independent relevance:** developers integrating central and forward
  tracking need the exact branch contract and hit provenance.
- **Minimum critical footprint:** one PandaRoot implementation file.
- **Cross-repository derivation:** minimum repository count is one.
- **Known uncertainty:** the implementation contains legacy comments and
  placeholders; the annotation is limited to the explicit input/output and
  hit-link contract, not algorithm-quality claims.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `ACCEPT`.

## n911 / vf011 - RHO decay-candidate combinatorics

- **Question:** After filling particle lists in a RHO analysis, how can I build
  a J/psi-to-muon-pair candidate and then a psi(2S)-to-J/psi-pion-pair
  candidate, apply a J/psi mass window, and avoid reused daughters or
  double-counted combinations?
- **Intent / status / difficulty:** `usage` / `answered` / `moderate`.
- **Archetypes:** primary `component_usage`; secondary `workflow_sequence`.
- **Classification:** `representative`; decay-candidate construction is a
  normal RHO analysis operation and closely matches recurring Gold usage
  forms.
- **Source scope / topology:** locked PandaRoot Sphinx documentation, one
  repository-associated documentation identity, multi-hop within one page.
- **Critical evidence:** `Tutorials/tut_02_03_analysis_combinatorics.html`
  documents manual `RhoCandidate::Combine`, list-level
  `RhoCandList::Combine`, `RhoMassParticleSelector`, the complete two-stage
  decay combination, and overlap/double-count prevention.
- **Answer obligations:** show the two ordered `Combine` operations; apply the
  mass selector before parent construction; state the documented overlap and
  double-count behavior.
- **Closest exposed Gold:** g022 and g024. Overlap includes RHO documentation,
  analysis usage, and task form; g022 only locates data-access/PID pages and
  g024 explains FairTask-style analysis. Neither asks for decay-candidate
  combinatorics.
- **Closest frozen novel_dev:** nf018 and nf026. nf018 checks reconstructed
  trees against MC truth; nf026 navigates the tutorial sequence. Neither
  constructs composite candidates.
- **Closest frozen validation:** vf002. Both are RHO operations and have
  documentation/task overlap. vf002 fills particle lists and combines PID
  classifier probabilities; n911 combines already selected daughters into
  decay candidates and prevents candidate overlap.
- **Novelty / rationale:** `composition`, `task_form`; substantial source and
  subsystem overlap is allowed because the minimum user operation differs.
- **Independent relevance:** composite decay reconstruction is a core
  analysis step after particle selection.
- **Minimum critical footprint:** one locked documentation page.
- **Cross-repository derivation:** one PandaRoot-associated identity; not
  cross-repository.
- **Known uncertainty:** the tutorial's PID choices are illustrative and are
  not part of this Gold obligation.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `ACCEPT`.

## n912 / vf012 - Muon range-system principle

- **Question:** Why does PANDA use an iron-and-MDT range system to distinguish
  muons from pions when Cherenkov and time-of-flight detectors cannot, and
  what observable does that layered design reconstruct?
- **Intent / status / difficulty:** `algorithm_theory` / `answered` / `simple`.
- **Archetypes:** primary `theory_explanation`; no secondary archetype.
- **Classification:** `representative`; causal detector explanations recur in
  Gold and pion/muon separation is independently important to PANDA PID.
- **Source scope / topology:** paper-only, one locked `li_2026` source,
  single-hop.
- **Critical evidence:** `li_2026`, PDF page 48, explains pion absorption and
  hadronic showers versus penetrating muon ionization, the instrumented iron
  return yoke, and digital MDT depth sampling.
- **Answer obligations:** explain the material-interaction difference; identify
  the iron-MDT-iron layered design; identify reconstructed range as the
  discriminating observable.
- **Closest exposed Gold:** g043 and g053. Overlap is causal
  `algorithm_theory`/detector-property explanation. There is no muon-system
  entity, paper page, or evidence overlap, and the information need is not
  luminosity theory or HV-MAPS resolution.
- **Closest frozen novel_dev:** nf008 and nf030. Both are LMD-specific theory
  families with different algorithms and evidence.
- **Closest frozen validation:** vf007. Both are paper-backed PANDA PID-system
  questions, but vf007 compares DIRC pion-kaon geometry and coverage; n912
  asks why material penetration and depth sampling separate pions from muons.
- **Novelty / rationale:** `relation`, `reasoning_topology`; it traces the
  causal detector-response relation from particle interaction to range.
- **Independent relevance:** muon identification depends on a detector
  principle not supplied by Cherenkov or time-of-flight systems.
- **Minimum critical footprint:** one paper page.
- **Cross-repository derivation:** not applicable; no repository source is
  required.
- **Known uncertainty:** performance percentages and energy ranges on the page
  are deliberately not required because the question asks for the principle
  and observable.
- **Codex recommendation:** `RECOMMEND_ACCEPT`.
- **Human decision:** `ACCEPT`.

## Discarded pre-ID ideas

- Standalone GEM hit-to-track chain: discarded as family-adjacent to the
  stronger MVD/GEM integration boundary admitted as n910.
- Additional RHO fit tutorial operation: discarded to avoid an adjacent
  analysis-operation cluster before human review.
- Event-time and burst-buffer APIs: discarded because available documentation
  support was thin and code-level framing risked narrowing frozen time-ordering
  family nf029.
- Generic detector-package location inventory: discarded as a mechanical
  detector substitution for frozen source-location/module-structure needs.
- Forced two-repository workflow: discarded because the minimum critical
  footprint did not naturally require two repository identities.
- Manufactured unanswerable, conflict, ambiguity, or troubleshooting cases:
  discarded because the locked anchors supported answered needs and no status
  quota exists.

## Review closure

Li accepted all six N3-E records as represented in the reviewed commit. Their
semantic content is unchanged, their lifecycle is `approved`, and split freeze
remains a separate future action.
