# N1-R1 — Representativeness Profile Correction

Methodological correction of the N1-R recalibration. The N1-R framework
direction (novelty × representativeness dual constraint, representative vs
exploratory classes, analogue/closest-case separation, human review pending,
no runtime outcome use) is retained. Three method errors in the Gold
reference profile are corrected here. Dataset-design analysis only: no
PANDA Agent component ran, no runtime outcome was inspected, no questions
were generated, approved, or frozen. The original N1-R analysis remains in
`N1R_REPRESENTATIVENESS_REVIEW.md` as a historical record with a correction
notice; this document supersedes its numbers.

## Correction A — Gold is a benchmark reference proxy, not user frequency

The 120 exposed Gold questions are a manually curated, intentionally
balanced development benchmark — not a random sample of production user
logs. All v1 wording that could read as "Gold archetype percentage = real
user frequency" is withdrawn. The rebuilt profile
(`gold_representativeness_profile.json`, schema
`novel-representativeness-profile-v2`) declares
`profile_role: benchmark_reference_proxy` and
`empirical_user_frequency: false`, and representativeness assessment is now
defined as two independent signals:

1. **Benchmark reference fit** — recurring benchmark task archetype,
   comparable intent family and question operation.
2. **Domain relevance** — independent judgment whether the need belongs to
   routine PandaRoot / LuminosityFit / RestgasDetermination usage and the
   luminosity/restgas main workflow, versus a corpus corner.

The sidecar (schema `novel-curation-sidecar-v3`) records both:
`benchmark_reference_fit` (renamed from `distribution_fit`) and the new
`domain_relevance`.

## Correction B — task archetype separated from answerability

`genuine_insufficiency` and `version_boundary` are answerability /
expected-status conditions, not user information tasks, and are removed
from the task taxonomy. All 18 previously pseudo-archetyped questions were
reassigned to their actual task form (e.g. g007 → `setup_environment` +
`answerability_class: corpus_insufficiency`; g042 → `source_location` +
`version_boundary`; g118/g119 → `troubleshooting_diagnosis` +
`corpus_insufficiency`; g095/g096 → `producer_consumer_trace`). The
corrected taxonomy has 11 task archetypes, and the profile reports
`counts_by_answerability_class` separately:
`answerable 102, corpus_insufficiency 10, version_boundary 8,
clarification_needed 0`.

Corrected Gold reference task-archetype distribution (120 questions):

| Task archetype | Count | Share |
|---|---|---|
| implementation_explanation | 19 | 15.8% |
| source_location | 17 | 14.2% |
| producer_consumer_trace | 15 | 12.5% |
| theory_explanation | 13 | 10.8% |
| troubleshooting_diagnosis | 12 | 10.0% |
| repository_structure | 11 | 9.2% |
| component_usage | 10 | 8.3% |
| setup_environment | 9 | 7.5% |
| concept_comparison | 6 | 5.0% |
| workflow_sequence | 5 | 4.2% |
| documentation_navigation | 3 | 2.5% |

## Correction C — source scope is the minimum required footprint

The v1 scope computation unioned every `source_id` appearing in selectors,
which treats `any_of` alternatives (docs OR repo; upstream OR fork) as
cumulative requirements. The corrected computation finds, per question, the
smallest source footprint that satisfies **all critical evidence groups**
(groups are AND requirements; selectors within a group are OR alternatives;
ties resolve to the least complex scope category; workflow/repository
object ids map deterministically to their owning repository; opaque
`object.<hash>` selectors are resolved from static provenance and are never
treated as unconstrained or zero-cost).

Corrected `minimum_required_source_scope` distribution:

| Scope | v1 (selector-availability) | v2 (minimum obligation) |
|---|---|---|
| single_repo | 55 | 60 |
| docs_only | 14 | 16 |
| paper_only | 15 | 15 |
| repo_plus_paper | 18 | 13 |
| repo_plus_docs | 10 | 4 |
| cross_repo | 8 | 5 |
| cross_repo_plus_paper | (hidden in repo_plus_paper) | 5 |
| cross_repo_plus_docs | (hidden in repo_plus_docs) | 2 |

The old numbers were selector-availability based; the new numbers are
minimum-obligation based. Both directions of error existed: any_of
alternatives across upstream/fork inflated "cross" (single_repo rose to
60), while genuinely multi-repository-plus-paper obligations were hidden
inside coarse `repo_plus_*` labels (cross-repo-requiring total is 12/120,
not 8/120). Evidence topology and the difficulty proxy were recomputed on
the same minimum-footprint semantics
(`single_evidence 49 / multi_evidence_single_scope 40 /
multi_evidence_cross_scope 31`; difficulty proxy `simple 49 / moderate 43 /
hard 28`).

N1-R2 made this derivation repository-reproducible in
`evaluation/scripts/validate_novel_curation.py`. A fresh static derivation now
checks every stored assignment and aggregate distribution. It reproduces
`120/120` Gold assignments with `0` unresolved opaque selectors; therefore the
v2 distribution above remains unchanged.

## N1 reassessment under the corrected method

| ID | Task archetype | Benchmark ref fit | Domain relevance | Class | Disposition |
|---|---|---|---|---|---|
| n001 | setup_environment | moderate | strong | representative | KEEP_REPRESENTATIVE |
| n002 | setup_environment | strong | strong | representative | KEEP_REPRESENTATIVE |
| n003 | component_usage | strong | strong | representative | KEEP_REPRESENTATIVE |
| n004 | component_usage | moderate | strong | representative | KEEP_REPRESENTATIVE |
| n005 | component_usage | moderate | moderate | representative | KEEP_REPRESENTATIVE |
| n006 | component_usage | moderate | moderate | representative | KEEP_REPRESENTATIVE |
| n007 | component_usage | moderate | moderate | representative | KEEP_REPRESENTATIVE |
| n008 | concept_comparison | moderate | moderate | representative | KEEP_REPRESENTATIVE |
| n009 | theory_explanation | moderate | strong | representative | KEEP_REPRESENTATIVE |
| n010 | implementation_explanation | strong | strong | representative | KEEP_REPRESENTATIVE |
| n011 | producer_consumer_trace | strong | strong | representative | KEEP_REPRESENTATIVE |
| n012 | producer_consumer_trace | moderate | strong | representative | KEEP_REPRESENTATIVE |
| n013 | repository_structure | weak | weak | exploratory | REPLACE |
| n014 | repository_structure | weak | moderate | exploratory | REVISE_TO_REPRESENTATIVE |
| n015 | troubleshooting_diagnosis | strong | strong | representative | KEEP_REPRESENTATIVE |
| n016 | setup_environment (answerability: corpus_insufficiency) | moderate | moderate | representative | KEEP_REPRESENTATIVE |

Changes vs N1-R:

- **n009 reclassified representative** (was exploratory): under the
  corrected two-signal method, its theory-of-model-choice task and strong
  domain relevance make it representative; the composed paper+code
  evidence affects difficulty (hard), not the task class.
- **n016** received a real task archetype (`setup_environment`) with
  `answerability_class: corpus_insufficiency`, instead of being carried by
  the withdrawn `genuine_insufficiency` pseudo-archetype; classification
  was re-derived from the task archetype plus Docker/platform domain
  relevance, not from Gold's insufficiency count.
- Dispositions otherwise unchanged: 14 KEEP_REPRESENTATIVE, 1
  REVISE_TO_REPRESENTATIVE (n014), 1 REPLACE (n013).

## Pilot drift — relative to the exposed Gold reference profile

(Not a claim about production user frequency.)

- Absent task archetypes: `source_location` (reference 14.2%),
  `workflow_sequence` (4.2%), `documentation_navigation` (2.5%).
- Under-represented: `implementation_explanation` (reference 15.8%, pilot
  6.3%).
- Over-weighted: `component_usage` (reference 8.3%, pilot 31.3%),
  `setup_environment` (reference 7.5%, pilot 18.8%).
- Answerability gap (orthogonal dimension): no `version_boundary`
  answerability case in the pilot (reference 8/120).

The N1-R replacement guidance stands, now worded against the reference
profile: n013's replacement should fill `source_location` or
`implementation_explanation` (or be an exploratory cross-repository case —
reference cross-repo-requiring scope 12/120, pilot 0). Exact proportional
matching is explicitly not required for a 16-question pilot; the profile is
used only to identify omissions, severe over-concentration, and drift.

## Governance synchronization

- `docs/NOVEL_DATASET_CURATION_CONTRACT.md` §6.2 extended with: Gold
  reference limitation (curated proxy, not population-frequency estimate),
  dual-source representativeness (benchmark similarity + independent
  domain-relevance judgment), orthogonal answerability (insufficient/
  version-conflict/clarification do not define task archetypes), and
  minimum-required evidence scope (`any_of` alternatives are not cumulative
  requirements).
- `docs/EVALUATION_POLICY.md` §6 wording tightened: Representative Novel
  approximates intended question-space coverage using the Gold benchmark as
  one reference proxy plus independent domain-relevance review.
- Sidecar schema `novel-curation-sidecar-v3`; profile schema
  `novel-representativeness-profile-v2`; validator extended (profile role,
  banned pseudo-archetypes, answerability↔status consistency, minimum
  scope presence, sidecar two-signal fields, coverage counters).
- No known factual/annotation issues in n001–n016 were touched; they
  remain for the follow-up revision task.
