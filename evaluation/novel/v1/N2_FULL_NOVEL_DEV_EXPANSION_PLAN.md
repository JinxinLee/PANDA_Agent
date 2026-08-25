# N2 — Full Novel-Dev Expansion Plan

Status: **APPROVED_FOR_EXECUTION** (2026-08-24).

Current execution status (2026-08-24, separated from the historical planning
rationale below): plan Rev 1 approved by `Li` at 2026-08-24T01:25+02:00.
N2-A Batch 1 = 6/6 human-approved (`BATCH1_APPROVED / NOT_SPLIT_FROZEN`;
n020-n025 approved by `Li` 2026-08-24T01:50/02:05+02:00, none yet
`split_frozen`). N2-B Batch 2 balancing curation authorized
2026-08-24T02:17+02:00 and executed: six draft candidates n026-n031
(`BATCH2_HUMAN_REVIEWED / R1_RE_REVIEW_PENDING`; 1 ACCEPT / 5 REVISE; see
`N2B_BATCH2_REVIEW_PACKAGE.md`). n027 is approved but not `split_frozen`;
n026, n028, n029, n030, and n031 were corrected after human REVISE decisions
and remain draft pending re-review. N2 overall remains `IN_PROGRESS`; the
full expanded novel_dev remains incomplete and unfrozen (28 loaded records =
23 human-approved + 5 corrected REVISE records awaiting re-review). C8
development proceeds in parallel under separate authorization; the N2
no-outcome contamination boundary remains unchanged. The planning rationale
and soft targets below are the approved historical content and are not
rewritten by execution progress.

Human approval record: reviewer `Li` re-reviewed Rev 1 and returned `ACCEPT`
at 2026-08-24T01:25+02:00 (approved commit
`08626661e3bb776c8f74c4f5b28c85ff2147c0fb`; prior review state 5/5 required
revisions resolved). This authorizes N2-A expansion execution. N2 overall
remains an active expansion lifecycle until the full expanded `novel_dev` is
human-reviewed and frozen; plan approval is not N2 completion and authorizes
no novel evaluation.

Revision history: Rev 1 (2026-08-24) applies the five required revisions from
the human review of the initial draft (REVISE decision; all other planning
decisions accepted): (1) `expected_split_counts`/`expected_status_counts`
semantics aligned with the runtime evaluator — they track all loaded question
records, not only approved ones (`docs/NOVEL_DATASET_CURATION_CONTRACT.md`
§11 updated accordingly); (2) exploratory admission relaxed to domain
relevance plus one or more substantive exploratory properties; (3)
Gold-proxy-derived numeric caps on `component_usage`, `setup_environment`,
and `documentation_navigation` removed — these are prioritization guidance,
not ceilings; (4) exploratory numeric targeting reframed as an investigation
pool rather than a required final accepted count, and the 25/50/25 difficulty
band identified as a pilot-derived heuristic, not a contract rule; (5) the
strict cross-repository definition is preserved, with final classification
contingent on the annotated minimum critical evidence footprint actually
requiring two repository identities. Awaiting re-review; N2-A must not begin
until the revised plan is re-approved.

This is a planning artifact only. It creates no question, no Gold record, no
evidence group, and no dataset-version change. Candidate sampling must not
begin until a human reviewer approves or revises this plan. Nothing here was
derived from PANDA Agent outcomes: no retrieval, QA, judge, or runtime
component was run, and no benchmark/novel outcome was inspected.

## 1. N1 frozen baseline and invariants

Baseline for this plan: commit `049b6d8` ("clean up N1 finalization metadata"),
on top of `a7109d9` ("finalize N1 novel-dev pilot").

- N1: `PASS / COMPLETE`. N0: `COMPLETE`.
- Frozen pilot: 16 active questions (`n001`-`n010`, `n014`-`n019`), 16
  independent active families, all `approved` by reviewer `Li`, all sidecar
  lifecycles `split_frozen`.
- Retired lineage `n011/nf011`, `n012/nf012`, `n013/nf013` stays historical;
  those IDs and families must never be reused.
- Dataset version `0.2.0`, benchmark version `novel-v1-dev-0.2.0`, identity
  `novel-v1-n1-pilot`, `release_eligible: false`.
- Full `novel_dev` is NOT complete; `novel_validation` is not started;
  `novel_holdout` is not created. No novel evaluation has been run.

Invariants the expansion must preserve:

- The 16 frozen questions, their Gold evidence, answer points, selectors,
  review metadata, and lifecycles are immutable except for the dataset-level
  version header described in §13. Annotation corrections follow the
  amendment rules in `docs/NOVEL_DATASET_CURATION_CONTRACT.md` §18.
- The locked authoritative corpus (3 repositories, 3 locked PDFs, the
  sphinx snapshot, `curated_panda_domain@1.0`) is frozen. N2 planning is
  question-distribution planning, not corpus-generalization planning.
- C8 remains `NEXT_ELIGIBLE / NOT_STARTED`.

## 2. Current coverage diagnosis

Frozen pilot distribution (from `coverage_report.json`):

| Dimension | Pilot (16) | Gold reference proxy (120) |
|---|---|---|
| intent installation | 2 (12.5%) | — |
| intent usage | 4 (25.0%) | — |
| intent api | 3 (18.8%) | — |
| intent algorithm_theory | 2 (12.5%) | — |
| intent algorithm_implementation | 2 (12.5%) | — |
| intent data_flow | 0 | — |
| intent module_structure | 1 (6.3%) | — |
| intent troubleshooting | 2 (12.5%) | — |
| primary archetype `source_location` | 1 (6.3%) | 17 (14.2%) |
| primary archetype `implementation_explanation` | 2 (12.5%) | 19 (15.8%) |
| primary archetype `producer_consumer_trace` | 0 | 15 (12.5%) |
| primary archetype `component_usage` | 6 (37.5%) | 10 (8.3%) |
| primary archetype `setup_environment` | 3 (18.8%) | 9 (7.5%) |
| primary archetype `documentation_navigation` | 0 | 3 (2.5%) |
| cross_repository | 0 | 12 of 120 (10.0%, incl. paper/docs variants) |
| exploratory | 0 | — (pilot-side class) |
| expected status | 15 answered / 1 insufficient | 102 / 10 / 8 (version_boundary) |

Major gaps, in planning priority order:

1. `data_flow` intent is 0 (explicit pilot gap after n011/n012 retirement).
2. `cross_repository` is 0.
3. `producer_consumer_trace` and `workflow_sequence` have no primary
   instances, although the pilot's usage questions contain adjacent content.
4. `documentation_navigation` archetype is 0.
5. `source_location` and `implementation_explanation` are underrepresented
   relative to the two largest Gold archetypes.
6. `component_usage` (37.5%) and `setup_environment` (18.8%) are heavily
   represented relative to the Gold reference proxy.
7. `exploratory` class is 0; status diversity beyond one
   `insufficient_evidence` case is absent.

These are sampling signals, not quotas. No frozen N1 question may be deleted,
weakened, or relabelled to improve percentages.

## 3. Gold-profile interpretation boundary

`gold_representativeness_profile.json` (schema v2) is a benchmark reference
proxy: a manually curated, intentionally balanced evaluation set. It is **not**
an empirical sample of production user-query frequencies
(`empirical_user_frequency: false`).

Rules for using it in expansion planning:

- Archetype percentages are a coverage prior that justifies *investigating*
  an area, never a target to reproduce numerically.
- Representativeness classification keeps the two-signal rule from N1-R1:
  Gold-reference fit **plus** independent PANDA-domain relevance. Either
  signal alone does not determine the class.
- Exact percentage matching and mechanical Gold-template reproduction with
  substituted entities are prohibited novelty failures (contract §6.2).
- Answerability is orthogonal to archetype: no pseudo-archetype such as
  "genuine_insufficiency"; version-boundary and insufficiency cases each carry
  a real task archetype plus an answerability class.

## 4. Locked-corpus support inventory

A compact static audit of the locked corpus (deterministic repository search,
source-tree and documentation inspection only; no PANDA Agent runtime). Every
anchor below was verified to exist in the locked snapshots during N2
planning. Anchors are source regions for *future independent sampling*, not
questions.

### 4.1 data_flow / producer-consumer — support: STRONG

1. `restgas_determination` `macro/target/`: two-step POCA analysis pipeline
   (`poca_step1_worker.py` -> `poca_step2_analysis.py`, plus `mc_step_worker.py`,
   `merge.py`/`merge_files.C`, `generate_configs.py`); README documents the
   event-by-event POCA hand-off.
2. `restgas_determination` README displaced-track recovery chain:
   `PndTrkTracking2` -> `PndUnassignedHitsTask` ->
   `PndApolloniusTripletTrackFinderTask` -> `PndSttSkewStrawPzFinderTask`
   (unassigned hits -> displaced trajectories -> longitudinal component).
3. `pandaroot` `macro/run/` stage-chain macros: `sim_complete.C`,
   `digi_complete.C`, `reco_complete.C`, `pid_complete.C` (also
   `digiOnly_complete.C`, `recoLocal_complete.C`, `sim_radwidth_complete.C`).
4. `restgas_determination` `macro/target/ConvertTrackToRhoCandList.C`:
   reconstructed-track to analysis-candidate hand-off.
5. sphinx `Running/MasterTasks.html` and `Running/Running_Sequence.html`:
   documentation-side evidence for task chaining and run ordering.

Verdict: at least 2, plausibly 3-4, natural data-flow needs without
relabeling component usage. Family isolation note: anchors 1-4 sit in the
restgas fork; questions drawn from them must express genuinely different
information needs (pipeline stage relation vs artifact hand-off vs run
ordering), not one need re-worded.

### 4.2 cross_repository — support: STRONG (pandaroot+luminosityfit), MODERATE (fork-comparison)

**Definition adopted for the expansion (binding for future curation):** a
question is `cross_repository` only when satisfying its critical information
need requires independently necessary evidence from at least two repository
identities. It is not enough that one source is a paper and one is code, that
two files lie in one repository, or that one repository historically depends
on another. `any_of` alternatives inside one critical group do not create
cross-repository scope; the minimum-required footprint decides. **Final
classification is contingent on annotation:** the planning-time anchor
suggests a candidate, but the question is `cross_repository` only if, after
Gold evidence annotation, the minimum critical evidence footprint (critical
groups with `any_of` read as alternatives) actually requires two repository
identities; otherwise the sidecar records the narrower scope the annotation
supports.

1. `luminosityfit` README installation and workflow sections require cloning
   PandaRoot alongside LuminosityFit; the documented "MC simulation,
   reconstruction and luminosity fit" workflow splits simulation/reconstruction
   (PandaRoot) from luminosity fitting (LuminosityFit apps such as
   `createLmdFitData`, `ExtractLuminosityValues`). Both identities are
   independently necessary for the workflow-level need. (The README also
   mentions an LMD-Alignment repository; it is **outside** the locked corpus
   and must not be used as evidence.)
2. `pandaroot` `detectors/lmd/` (`LmdMC`, `LmdDigi`, `LmdReco`, `LmdQA`)
   provides the PandaRoot-side implementation anchor for the same workflow.
3. Fork-vs-upstream comparison (restgas branch vs `pandaroot` dev): the
   restgas README declares the PandaRoot `oct19` base and branch-specific
   development. However, components named in its workflow also exist upstream
   (verified: `pgenerators/Target/PndTargetGenerator` and
   `tracking/PndApolloniusTripletTrackFinder` exist in locked `pandaroot`).
   A comparison question is therefore admissible only after dual-repository
   verification that the compared behavior actually differs between the two
   locked identities (candidate difference regions: `macro/target/` pipeline,
   `PndUnassignedHitsTask`, `houghPlusApolloniusTripletTrackFinder.C`).

Verdict: 1-2 strong workflow-level cross-repository needs
(pandaroot+luminosityfit); fork-comparison cases are possible but each
requires the dual-identity difference proof above. Papers do not count as a
repository identity; repo+paper stays `repo_plus_paper`.

### 4.3 source_location — support: STRONG

1. `pandaroot` `tracking/` tracker modules (`PndIdealTrackFinder`,
   `PndForwardTrackFinder`, `PndFtsTrackFinder`, `PndHoughTrackFinder`,
   `PndCurlingTrackFinder`, ...) — where-is-implemented needs distinct from
   the frozen `nf017` (PndTrack definition) and `nf019` (PndRecoKalmanTask
   pipeline) families.
2. `pandaroot` `detectors/lmd/` LmdDigi/LmdReco sources.
3. `pandaroot` `geometry/` and `gconfig/` trees (geometry/configuration file
   location needs).

Verdict: 2-3 natural cases. Constraint: must avoid becoming trivial
file-path lookup; prefer needs whose location answer also establishes *which
component owns* a responsibility.

### 4.4 implementation_explanation — support: STRONG

1. `pandaroot` `tracking/GenfitTools`, `tracking/PndGeanePropagator`,
   `tracking/PndHelixPropagator` (propagation implementation choices).
2. `pandaroot` `detectors/lmd/LmdReco` (LMD reconstruction implementation).
3. `restgas_determination` `tracking/PndApolloniusTripletTrackFinder/`
   (`PndApolloniusTriplet.cxx` triplet construction).
4. `luminosityfit` `fit/` implementation (fit options/models — orthogonal to
   the frozen `nf014` directory-role question).

Verdict: 2-3 natural cases; the corpus is code-heavy enough that annotation
effort, not material scarcity, is the limiting factor (consistent with the
pilot's `evidence_scarce_in_corpus` note outside the three core repos).

### 4.5 documentation_navigation — support: STRONG

The locked sphinx snapshot has 75 pages; the pilot touched only Logging
(`nf004`), EventDisplay (`nf005`), and Docker (`nf016`). Unexposed, naturally
supportive regions include the tutorial sequence (`tut_01`-`tut_06`,
`tut_outline`), `Running_Sequence`, `CVMFS`, `Jupyter/PandaRootPySim`,
`Building_Documentation`, `DalitzGui`, and the `Tools/` utility pages.

Verdict: 1-2 natural "which documented resource covers X / where is X
documented" needs are readily supportable. Documentation-navigation is
deprioritized relative to the larger structural gaps (small Gold archetype
share and lower pilot urgency), but this is prioritization guidance, not a
ceiling: additional high-quality cases are acceptable if independently
important.

### 4.6 exploratory — support: MODERATE-to-GOOD

1. `pandaroot` `softrig/` (`PndAnaWithTrigger`, `PndOnlineFilterInfo`):
   software-trigger/online-filter needs — rare but legitimately user-relevant.
2. `pandaroot` `timebased/Buffers` (`PndRingSorter`, `PndBufferTestTask`):
   time-based simulation buffering/ordering frontier.
3. Locked-thesis rare-chapter combinations (e.g. alignment with Millepede,
   KOALA-related material in `karavdina_2015` and the corresponding
   luminosity/monitoring topics in `li_2026`): chapter-level anchors;
   page-precise selectors are established during future evidence annotation,
   not here.

Verdict: 2-4 candidates plausible. Exploratory admission requires the §9
policy test (legitimate underrepresented need, plausible evidence
composition, domain relevance); obscure-symbol trivia and corpus-tail for its
own sake are rejected.

### 4.7 workflow_sequence and other underrepresented archetypes

`Running_Sequence` documentation plus the `macro/run` chain and restgas
`ana_complete.C` support 1-2 run-ordering needs (closely related to §4.1;
family isolation applies). `concept_comparison` (Gold 6/120, pilot 1) has
natural material in generator/tracker comparisons; `theory_explanation`
(Gold 13/120, pilot 1) has unexposed thesis chapters. These are Batch 2
balancing candidates, not Batch 1 priorities.

### 4.8 Status-class material

- `insufficient_evidence`: precedent `n016`; naturally arising when
  documentation genuinely lacks an answer. Support: adequate.
- `version_conflict`: the locked corpus has a real version boundary
  (restgas fork `oct19` vs upstream `dev`), and the restgas README records a
  unit-convention discrepancy between an older `README_RestGas` (mm) and the
  active branch (cm). Support exists but each case must be a genuine
  cross-version answer conflict, not a paraphrase of exposed Gold's
  commit-substitution pattern.
- `clarification_required`: ambiguous entities exist (similar task/class
  names across subsystems). Any future candidate keeps the contract §10
  generic T0 compatibility check before acceptance.

## 5. Proposed soft targets

Every number in this section is a **PROPOSED_SOFT_TARGET**. None is a
REQUIRED_QUOTA. Each is justified by the §4 audit; a target is abandoned for
this expansion if natural sampling cannot meet it with high-quality
questions.

| # | Target | Value | Justification |
|---|---|---|---|
| T1 | final `novel_dev` size | 28-32, centered near 30 | contract §4 ~30 quality target; 16 frozen + 12-16 new |
| T2 | new approved questions beyond the frozen 16 | 12-16, centered near 14 | T1 minus frozen 16; two batches of 6-8 (§11) |
| T3 | new `data_flow` intent | 2-4 | STRONG support (§4.1); zero in pilot |
| T4 | genuine `cross_repository` | 1-3 total after expansion, contingent on annotated footprint | STRONG for pandaroot+luminosityfit workflow needs; final classification only when the annotated minimum critical evidence footprint requires two repository identities (§4.2); fork-comparison only with dual-identity proof |
| T5 | new `source_location` primary archetype | 1-3 | STRONG support; Gold 14.2% vs pilot 6.3% (§4.3) |
| T6 | new `implementation_explanation` primary archetype | 1-3 | STRONG support; Gold 15.8% vs pilot 12.5% (§4.4) |
| T7 | `producer_consumer_trace` primary archetype | 1-3 total after expansion | Gold 12.5%, pilot 0; overlaps §4.1 anchors, family isolation applies |
| T8 | `documentation_navigation` primary archetype | deprioritized guidance: investigate 1-2, no numeric cap | 75 locked doc pages, 3 used (§4.5); prioritization guidance only — additional high-quality cases acceptable, Gold share is not a ceiling |
| T9 | exploratory class | investigation pool of 2-4 candidates; final accepted count is an outcome, not a target | MODERATE-to-GOOD support (§4.6); the pool size guides investigation effort; acceptance is gated by §9 policy; the contract's coarse 70-80% representative guidance implies room, not a count |
| T10 | new `component_usage` / `setup_environment` primaries | deprioritized guidance: add only independently important cases, no numeric cap | already over-weighted vs Gold proxy (§2); prioritization guidance only, not a ceiling |
| T11 | descriptive / identifier-free share (final) | >= 0.4 | already 0.81 in pilot; preserve while adding implementation-oriented cases |
| T12 | multi-evidence share (final) | >= 0.4 | already 0.50 in pilot; preserve |
| T13 | difficulty band (final) | roughly 25% simple / 50% moderate / 25% hard (pilot-derived heuristic, not a contract rule) | heuristic carried over from the pilot coverage proposal; contract §8 defines only the structural difficulty labels, not a band; pilot is 5/9/2 |
| T14 | `insufficient_evidence` additions | 0-1 | natural-only; one precedent exists |
| T15 | `version_conflict` additions | 0-1 | boundary material exists (§4.8), pattern-paraphrase prohibited |
| T16 | `clarification_required` additions | 0-1 | genuine ambiguity only; generic T0 check before acceptance |

Intent coverage expectation: all eight canonical intents present in the
final dataset where naturally supported — `data_flow` is the only currently
missing intent and has STRONG support, so T3 is expected to close it; no
other intent is at zero.

## 6. Explicit non-quota statement

**Coverage targets never justify a weak question.** A final dataset with 28
excellent questions is preferable to 30 questions where two exist only to
satisfy a table. A missing intent, status, archetype, or scope class is
acceptable whenever the locked corpus does not naturally support an
independent high-quality information need for it. Every PROPOSED_SOFT_TARGET
above yields to question quality at review time, and unmet targets are
recorded as findings, not failures.

## 7. Sampling protocol (for future execution)

Mandatory order per candidate; starting from the right-hand start points is
prohibited:

```text
source/domain anchor (from §4 or an independently justified region)
  -> natural user information need expressed for that anchor
  -> domain-relevance check (independent PANDA-domain judgment)
  -> closest exposed-Gold overlap review (information_need: high => reject)
  -> active novel-family overlap review (frozen 16 + new drafts)
  -> substantive novelty assessment (contract §6 taxonomy)
  -> candidate question draft
  -> independent Gold evidence annotation (static corpus inspection only)
  -> human review (curation / novelty / evidence / split)
  -> approval (reviewer decision recorded)
  -> split freeze
```

Prohibited starts:

- choosing a Gold question template and substituting an entity;
- choosing a known or suspected PANDA Agent failure and writing a question
  around it;
- selecting a desired answer first and inventing a question around it.

IDs: new candidates take `n020`+ (`nf020`+) only once a concrete independent
information need exists; `n011`-`n013`/`nf011`-`nf013` are never reused.

## 8. Semantic-family isolation procedure

Before any new candidate enters review, compare it against:

1. exposed Gold semantic equivalents (closest_exposed_cases review);
2. all 16 frozen N1 families (`nf001`-`nf010`, `nf014`-`nf019`);
3. all other new N2 draft families, including withdrawn drafts from the
   current expansion.

Trivial paraphrases and mechanical variants must share a family or be
rejected. One family belongs to at most one repository-visible novel split.
Special expansion watch-points (from §4): multiple questions drawn from the
restgas `macro/target` pipeline or the `macro/run` chain must be checked
against each other for distinct information needs (stage relation vs artifact
hand-off vs run order vs implementation detail); the cross-file authority is
`curation_family_id` in the sidecar, mirrored optionally by Gold `cluster_id`
within one load; the validator's cross-file family check stays mandatory.

## 9. Representative/exploratory policy

Classification stays two-signal (benchmark reference fit + independent domain
relevance) per N1-R1, recorded per question in the sidecar. The expansion
deliberately investigates exploratory candidates (T9) but never manufactures
them.

An exploratory candidate requires **domain relevance** (the need must be a
plausible PANDA-domain user need) **plus one or more substantive exploratory
properties**: a legitimate underrepresented user need; unusual but plausible
evidence composition; coverage-frontier value; or uncommon but
domain-relevant reasoning topology. One strong property with solid domain
relevance is sufficient; satisfying several is stronger. Rejection criteria
are unchanged: obscure symbol trivia; corpus tail for its own sake;
intentionally difficult wording; selection only because Gold omitted the
topic.

The representative subset remains the primary generalization-gap comparison;
exploratory results are reported separately.

## 10. Future status-selection policy

Expected status is chosen from the evidence, never for diversity:

- `answered` is the default for well-supported needs;
- `insufficient_evidence` only when the locked sources genuinely lack the
  answer a real user would seek (n016 precedent);
- `version_conflict` only when the locked version boundary produces a
  genuine conflicting answer across locked identities/versions — not a
  paraphrase of the exposed commit-substitution pattern;
- `clarification_required` only for genuine ambiguity or unresolved entity
  reference, never fabricated by deleting information; before acceptance the
  small generic T0 dataset/evaluator compatibility check from contract §10
  must pass (run in the future curation task, not now).

## 11. Batch 1 / Batch 2 execution design

**Batch 1 — gap-first (PROPOSED_SOFT_TARGET 6-8 candidates).** Concentrate
sampling on the strongest naturally supported gaps: `data_flow` intent and
producer-consumer needs (§4.1), genuine cross-repository workflow needs
(§4.2), `source_location` (§4.3), and `implementation_explanation` (§4.4).
These four areas have STRONG audit support and cover the pilot's largest
structural gaps. Anchor-first sampling: each candidate starts from a §4
anchor (or an equally verified region) and must survive the §7 protocol.

**Batch 2 — coverage balancing (PROPOSED_SOFT_TARGET 6-8 candidates).** Runs
only after human review of Batch 1. Inputs allowed for balancing: Batch 1
human decisions and rationale (accept/revise/reject reasoning), updated
coverage counts, and static corpus evidence. Inputs prohibited: any PANDA
Agent outcome on any novel question (§12). Batch 2 addresses what Batch 1
left naturally unfilled — expected areas: `documentation_navigation` (§4.5),
exploratory class (§4.6), `workflow_sequence`/`concept_comparison`/
`theory_explanation` balancing (§4.7), status-class natural cases (§4.8).

Why these batch sizes: 6-8 is large enough to cover the four Batch-1 gap
areas with more than one independent family each, small enough for one
coherent human review round, and matches the N1 pilot's reviewed scale
(16 items reviewed in one round; N1-R history showed semantic-repair churn
concentrates in the first batch of a new area). Two batches keep the second
round informed without outcome access. If Batch 1 review retires many
candidates, Batch 2 may grow toward 8; if quality anchors exhaust early,
the total may land at 28 rather than 30 (§6 governs).

## 12. No-outcome contamination boundary

Until the expanded `novel_dev` split is frozen:

- PANDA Agent must not be run on proposed, partially reviewed, or
  batch-frozen N2 questions — including "just the frozen Batch 1 subset".
- No benchmark or novel outcome material may be inspected to select, revise,
  or withdraw any expansion candidate.
- The preferred boundary order is fixed:

```text
complete expanded novel_dev curation
  -> human review of all candidates
  -> freeze the expanded split
  -> only then authorize novel_dev measurement in a separate task
```

Rationale: early system failures observed between batches would shape later
question selection, converting a question-distribution dataset into a
failure-targeted one. Human curation feedback may influence Batch 2; PANDA
Agent performance must not. Each curation record keeps
`agent_outcome_seen_before_freeze: false` and
`evidence_selected_from_agent_output: false`.

## 13. Versioning proposal

Proposal (requires human approval as part of this plan's review; not
pre-authorized by being written here):

- The frozen `0.2.0` pilot baseline is preserved by Git history
  (`a7109d9`, `049b6d8`) — immutable provenance without hash ceremonies.
  The expansion never rewrites the 16 frozen questions' content; only
  dataset-level headers advance.
- When the first expansion batch begins (future N2-A task), the dataset
  enters the **0.3.0 expansion lineage**: `dataset_version: 0.3.0` with new
  records present as `review_status: draft` / sidecar `lifecycle: draft`.
  Draft state is expressed by record-level review/lifecycle fields, not by a
  separate draft file, so the validator's cross-file family isolation keeps
  operating on one authoritative dataset file.
- As batches are approved, records move `draft -> approved`; expected counts
  track **all loaded question records** per the runtime evaluator semantics
  (contract §11 as aligned): during draft phases they include draft records
  and are updated whenever records are added, retired, or re-classified.
- The expanded full `novel_dev` freeze sets all lifecycles `split_frozen`
  under `dataset_version: 0.3.0` / `benchmark_version: novel-v1-dev-0.3.0`,
  with manifest and coverage report synchronized, in one freeze commit.
- Annotation corrections afterwards increment the patch segment (`0.3.1`)
  and record old/new value, reason, timestamp, reviewer; information-need
  changes create new question IDs (contract §18).
- Justification for `0.3.0`: consistent with the N1 precedent
  (`0.1.0` draft pilot -> `0.2.0` frozen pilot), where the minor segment
  marks a content-set transition and the `0.x` series reserves major-segment
  changes for schema-breaking evolution. The expanded dataset is a
  superset content transition, not a schema change.

## 14. Human-review workflow for new questions

Per candidate, mirroring the N1 final-review structure (four review lenses;
one reviewer may hold several for `novel_dev`):

- **curation review**: natural user need; product-scope fit; domain
  relevance (two-signal input).
- **novelty review**: closest exposed Gold cases; closest novel families
  (frozen 16 + current drafts); substantive, non-mechanical novelty.
- **evidence review**: locked source/version correctness; critical evidence
  groups with minimum-required scope semantics (`any_of` = alternatives);
  answer points; expected status; independent annotation (no agent output).
- **split review**: family isolation; representative/exploratory
  classification; coverage contribution against §5 targets (as guidance).

Codex/LLM output remains advisory throughout. Only explicit recorded human
decisions approve questions (`review_status: approved`, reviewer identity,
timestamp). Recommended artifacts per batch: a review package with per-item
ACCEPT/REVISE/REJECT recommendations, a human decision matrix, and a
finalization report on freeze — same shape as N1's
`N1_FINAL_HUMAN_REVIEW.md` / `N1_FINALIZATION_REPORT.md`.

## 15. Future freeze criteria

The expanded split may freeze only when all hold:

1. every expansion candidate is either human-approved (`approved`, reviewer,
   timestamp) or retired with recorded lineage (`WITHDRAWN_DRAFT` +
   replacement/no-replacement disposition);
2. final size is within 28-32, or the deviation is recorded with reasons
   (quality over target, §6);
3. `evaluation/scripts/validate_novel_curation.py` passes, including
   sidecar/dataset 1:1, family uniqueness, split hygiene, governance flags,
   selector availability, coverage/manifest count consistency, approved
   lifecycle consistency, and the 120-case Gold profile reproduction;
4. all active lifecycles are `split_frozen`; manifest and coverage report
   reflect the expanded state (`FROZEN`-equivalent status, version 0.3.0);
5. `agent_outcome_seen_before_freeze: false` and
   `evidence_selected_from_agent_output: false` remain true for every
   record;
6. exactly one freeze commit lands, and no novel evaluation has run.

## 16. Explicit out-of-scope list

This plan does not, and the future tasks it frames must not automatically:

- create `n020`+ questions, families, Gold records, answer points, or
  evidence groups (planning only);
- modify the frozen N1 dataset content or unfreeze anything;
- create `novel_validation` or `novel_holdout` content;
- promote `recommended_coverage_targets` in `coverage_report.json` into
   frozen/approved machine-readable targets (they remain proposal-only
   historical pilot output superseded by §5 upon human approval);
- run any PANDA Agent component, evaluation tier (T1-T5), or index change;
- inspect benchmark or novel outcomes;
- start C8 or any production behavior change;
- add repositories, source versions, PDF snapshots, or documentation
  snapshots;
- turn N2 into corpus-generalization planning.

## 17. Proposed next execution task

**N2-A — Expansion Batch 1 Curation (gap-first)**: curate 6-8 candidate
`novel_dev` questions (PROPOSED_SOFT_TARGET) under §7-§10, entering the
0.3.0 expansion lineage per §13, for human review. Precondition: this plan
is approved (or revised and re-approved) by the human reviewer. N2 itself
becomes `PASS / COMPLETE` only after the full expansion is frozen, not at
plan approval.
