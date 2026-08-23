# N1-R — Representativeness Recalibration Review

Dataset-design analysis only: no PANDA Agent component was run, no novel or
benchmark runtime outcome was inspected, and no question was approved or
generated here. The input was the 120 exposed Gold questions/annotations
(`evaluation/benchmarks/v2_6/gold_questions.yaml`) and the current N1 draft
package. Machine-readable result: `gold_representativeness_profile.json`;
sidecar blocks: `representativeness:` in `curation_metadata.yaml`.

Core finding: the N1 pilot drifted away from the Gold question distribution.
The two largest Gold archetypes — `implementation_explanation` (14.2%) and
`source_location` (12.5%) — are nearly absent from the pilot (one case and
zero cases respectively), while tool/setup corner questions are
over-represented. High novelty was acting as an implicit sampling objective;
it must not be one.

---

# Gold Question Archetypes

13 coarse archetypes were induced from the 120 Gold questions (inductively,
not from a preset list). Archetypes describe the user's information task, not
the module named.

| Archetype | Count | Share | Definition | Gold examples |
|---|---|---|---|---|
| implementation_explanation | 17 | 14.2% | How is X implemented in code; how do components cooperate; why this design | g059, g064, g073, g078 |
| source_location | 15 | 12.5% | Where is a class/module/macro/behavior defined or implemented | g028, g032, g036, g066 |
| producer_consumer_trace | 13 | 10.8% | Trace an artifact/data product from producer to consumer | g079, g081, g084, g093 |
| theory_explanation | 11 | 9.2% | Why does a method step exist; conceptual role; physics behind it | g043, g045, g048, g052 |
| genuine_insufficiency | 10 | 8.3% | Corpus legitimately cannot support the request | g007, g041, g107, g118 |
| repository_structure | 9 | 7.5% | Module composition, layer boundaries, directory roles | g097, g098, g100, g105 |
| version_boundary | 8 | 6.7% | Request pinned outside the locked version universe | g012, g042, g077, g120 |
| component_usage | 8 | 6.7% | Invoke/configure/use a specific component, tool, or macro | g015, g016, g017, g023 |
| troubleshooting_diagnosis | 8 | 6.7% | Diagnose a failure or suspicious result; what to inspect | g110, g112, g114, g116 |
| setup_environment | 7 | 5.8% | Install/prepare/verify the working environment and prerequisites | g001, g002, g004, g008 |
| concept_comparison | 6 | 5.0% | Distinguish/compare two concepts, approaches, or paths | g011, g051, g094, g106 |
| workflow_sequence | 5 | 4.2% | Ordered end-to-end pipeline stages and their connections | g014, g020, g091, g092 |
| documentation_navigation | 3 | 2.5% | Where is a topic documented; which pages cover it | g009, g010, g022 |

Every Gold question has exactly one primary archetype (plus optional
secondaries); full assignments are in the profile JSON. These are curation
abstractions for representativeness analysis — they are **not** product
intents and do not replace the eight canonical intents.

# Gold Distribution Summary

From `gold_representativeness_profile.json` (120 questions):

- **Intent:** algorithm_implementation 20, data_flow 18, api 16,
  algorithm_theory 16, usage 14, installation 12, module_structure 12,
  troubleshooting 12.
- **Archetype:** table above.
- **Source scope (from Gold evidence selectors):** single_repo 55 (45.8%),
  repo_plus_paper 18 (15.0%), paper_only 15 (12.5%), docs_only 14 (11.7%),
  repo_plus_docs 10 (8.3%), cross_repo 8 (6.7%).
- **Evidence topology (structural):** single critical evidence group 49
  (40.8%), multiple groups within one source 37 (30.8%), groups spanning
  sources 34 (28.3%).
- **Expression style (coarse):** explicit_identifier 47 (39.2%),
  partially_descriptive 68 (56.7%), identifier_free 5 (4.2%).
- **Expected status:** answered 102, insufficient_evidence 10,
  version_conflict 8.
- **Difficulty proxy (structural rule, no system outcome):** simple 49
  (40.8%), moderate 43 (35.8%), hard 28 (23.3%). Rule: ≤1 critical group =
  simple; 2 groups (or 3 groups in one source) = moderate; ≥4 groups (or 3
  groups spanning sources) = hard.

Implications for novel sampling: a representative novel set should be
majority single-repository, code-plus-paper heavy, with roughly 40/40/20
single/multi-same-source/cross-source structure, a majority of
explicit/partially descriptive expressions, and hard cases around a quarter
— not the majority.

# N1 Candidate Reassessment

| ID | Intent | Primary archetype | Class | Distribution fit | Corpus tail | Disposition | Reason |
|---|---|---|---|---|---|---|---|
| n001 | installation | setup_environment | representative | moderate | representative_but_rare | KEEP_REPRESENTATIVE | Common setup archetype on the fork; version-pair pinning is the rare part; semantic fixes pending |
| n002 | installation | setup_environment | representative | strong | representative_core | KEEP_REPRESENTATIVE | Mirrors g002 prerequisites on an independently selected repository |
| n003 | usage | component_usage | representative | strong | representative_core | KEEP_REPRESENTATIVE | Same task type as g016, different generator and stepping semantics |
| n004 | usage | component_usage | representative | moderate | representative_core | KEEP_REPRESENTATIVE | Routine runtime configuration; archetype common, instance new |
| n005 | usage | component_usage | representative | moderate | representative_core | KEEP_REPRESENTATIVE | Routine visualization need; question-answer wording fix pending |
| n006 | api | component_usage | representative | moderate | representative_core | KEEP_REPRESENTATIVE | Recurring stage-naming need; extension precision fix pending |
| n007 | api | component_usage | representative | moderate | representative_but_rare | KEEP_REPRESENTATIVE | Genuine MVD analysis task, rarer population; shortID wording fix pending |
| n008 | algorithm_theory | concept_comparison | representative | moderate | representative_but_rare | KEEP_REPRESENTATIVE | Comparison archetype well covered by Gold; paper-only scope metadata fixed to paper_only |
| n009 | algorithm_theory | theory_explanation | exploratory | moderate | exploratory_tail | KEEP_EXPLORATORY | Core topic but composed paper+code obligation exceeds the representative theory pattern; deliberate stress case |
| n010 | algorithm_implementation | implementation_explanation | representative | strong | representative_core | KEEP_REPRESENTATIVE | Largest Gold archetype on a mainstream subsystem; selector completeness fix pending |
| n011 | data_flow | producer_consumer_trace | representative | strong | representative_core | KEEP_REPRESENTATIVE | Mirrors the most common Gold data-flow task on a different channel; over-composition fix pending |
| n012 | data_flow | producer_consumer_trace | representative | moderate | representative_but_rare | KEEP_REPRESENTATIVE | Trace archetype reused; cross-era composition needs semantic review |
| n013 | module_structure | repository_structure | exploratory | weak | exploratory_tail | REPLACE | Vendored-build corner chosen mainly because Gold had not touched genfit; factual annotation error; fills no distribution need |
| n014 | module_structure | repository_structure | exploratory | weak | exploratory_tail | REVISE_TO_REPRESENTATIVE | Legitimate newcomer need, current evidence overreach; trimming restores representative quality |
| n015 | troubleshooting | troubleshooting_diagnosis | representative | strong | representative_core | KEEP_REPRESENTATIVE | Most common real failure class; documented workaround structure |
| n016 | troubleshooting | genuine_insufficiency | representative | moderate | representative_but_rare | KEEP_REPRESENTATIVE | Gold insufficiency cases are deliberate probes; natural instance; wording fix pending |

Disposition counts: KEEP_REPRESENTATIVE 13, KEEP_EXPLORATORY 1,
REVISE_TO_REPRESENTATIVE 1, REPLACE 1.

Distribution comparison (pilot vs Gold, primary archetype):

- Missing entirely in the pilot: `source_location` (Gold 12.5%),
  `version_boundary` (6.7%), `workflow_sequence` (4.2%),
  `documentation_navigation` (2.5%).
- Under-represented: `implementation_explanation` (Gold 14.2% vs pilot 6.3%).
- Over-represented: `component_usage` (Gold 6.7% vs pilot 31.3%),
  `setup_environment` (5.8% vs 12.5%), `repository_structure` (7.5% vs
  12.5%, and both pilot cases are weak-fit corners).

The prior semantic-review findings (configSettings semantics, n002 answer
overreach, n005 mismatch, n007 shortID mixing, n011 over-composition, n012
over-linking, n013 libgenfit factual error, n014 evidence overreach, n016
wording, n010 selector completeness, n006 extension precision) remain valid
and are **not** fixed here; they belong to the follow-up revision task.

# Pilot Recomposition Recommendation

Target composition guidance: ~70–80% representative, ~20–30% exploratory
(12/4 for 16 questions), adjusted honestly rather than forced.

1. **n013 → REPLACE.** Replacement specification (generation happens in the
   follow-up task, not here):
   - Need: a representative case in one of the two largest missing/under-
     represented Gold archetypes.
   - Preferred archetype: `source_location` (Gold 12.5%, pilot 0%) — locate
     the implementation of a routinely relevant PANDA/LuminosityFit/Restgas
     component — or `implementation_explanation` (Gold 14.2%, pilot 6.3%).
   - Sampling constraint: choose a routinely relevant subsystem that a real
     user asks about weekly, not a vendored build corner; do not derive it
     from any Gold question by entity substitution; evidence must come from
     the locked corpus, independently.
   - Composition note: an **exploratory cross-repository** replacement
     (cross_repo is 6.7% in Gold, 0% in the pilot) would simultaneously move
     the pilot toward the 12/4 guidance; R2 should choose between the
     representative source_location slot and the exploratory cross-repo slot
     based on curation quality, not quota.
2. **n014 → REVISE_TO_REPRESENTATIVE.** Keep the newcomer question about
   `model_framework` vs the native `model/` layer but trim the answer points
   and evidence to what the two-line README and the factory header actually
   support (drop the directory-layout inference or evidence it explicitly).
3. **n009 stays the exploratory anchor** (composed cross-source theory+code
   stress case).
4. After (1) and (2), the pilot sits at roughly 15 representative / 1
   exploratory if the representative replacement is chosen, or 14/2 with the
   exploratory cross-repo replacement. R2 should treat 12–14 representative /
   2–4 exploratory as the acceptable band and prefer high-quality natural
   questions over exact ratios.
5. Future novel_dev curation rounds must sample **toward** the Gold archetype
   profile (especially source_location, implementation_explanation, and
   theory_explanation on core workflow concepts), and must not select topics
   merely because exposed Gold omitted them.

# Proposed Future Metrics

- **Primary: Representative Generalization Gap** = Gold score −
  Representative Novel score. Computed only after the novel_dev split is
  human-approved and frozen, under an explicitly authorized evaluation tier.
- **Secondary: Exploratory Novel Score**, reported separately as a coverage-
  frontier stress measurement.
- Optional: Overall Novel Score, reported but never as the sole headline.
- Interpretation rule: exploratory cases do not substitute for
  representative novel cases in generalization-gap claims.

None of these metrics were run in this task; this is evaluation design only.

# Governance synchronization

- `docs/NOVEL_DATASET_CURATION_CONTRACT.md` §6.2 (added): representativeness
  + novelty dual constraint; archetype reuse allowed; representative vs
  exploratory split semantics; primary gap uses the representative subset;
  questions must not be selected merely because Gold omitted a topic.
- `docs/EVALUATION_POLICY.md` (added): Representative Novel / Exploratory
  Novel evaluation interpretation.
- Sidecar schema bumped to `novel-curation-sidecar-v2` with the
  `representativeness:` block; `n008` repository_scope corrected to
  `paper_only` (paper-only questions must not be labeled single_repository).
