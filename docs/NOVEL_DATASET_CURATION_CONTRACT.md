# PANDA Agent — Novel Dataset Curation Contract v1

## 1. Authority and scope

This document is the authoritative curation contract for the PANDA Agent Novel Dataset v1. It extends the stable exposure rules in `docs/EVALUATION_POLICY.md` and uses the evaluator-compatible Gold contract implemented by `panda_agent.evaluation.GoldDataset` and `GoldQuestion`.

N0 defines how future novel questions are proposed, annotated, reviewed, exposed, versioned, frozen, and amended. It does not create a question, run PANDA Agent, inspect an outcome, authorize C8, or authorize any evaluation tier.

The Novel Dataset describes the PANDA user-question space, not the known weaknesses of the current PANDA Agent and not the behavior of any particular candidate policy. Questions must not be selected to prove or disprove P3 sparse-heavy, `C6_INTENT_AWARE_V1`, SemanticDense, `c7.explicit_selection.v1`, C8 global rerank, or any other treatment.

## 2. Measurement purpose

Novel Dataset v1 measures **question-distribution generalization**:

> Given the same locked authoritative PANDA source corpus, can PANDA Agent answer new information needs expressed through entities, relations, evidence combinations, wording, and reasoning structures that did not participate in exposed benchmark-driven development?

Novel v1 does not measure **corpus generalization**. It freezes the authoritative source corpus and source-version universe: repository identities and locked refs, PDF/documentation snapshots, and the source provenance boundary. Adding new authoritative source content, a new repository or source version, or a different paper/documentation snapshot would confound query generalization with corpus shift.

Novel v1 does **not** freeze the current derived representation. KnowledgeObject decomposition, chunks, index representation, and future Phase-D abstractions—including Concept, Symbol, Class, Function, File, Workflow, DataProduct, and derived entity/relation structures—may be added or reshaped provided every Gold evidence claim remains traceable to the same locked authoritative source content and versioned provenance.

```text
frozen:
- authoritative source truth
- repository identities and source versions
- PDF and documentation snapshots
- source provenance boundary

evolvable:
- KnowledgeObject representation and decomposition
- chunking
- index representation
- entity and relation abstractions
```

A future corpus-generalization dataset may be useful, but it must be designed, versioned, and reported as a separate evaluation scope.

## 3. Dataset units and compatibility layers

Each accepted question has two linked records:

1. **Evaluator question record.** Uses the existing strict `GoldQuestion` fields and semantics without extra fields: `id`, `split`, `language`, `intent`, optional `accepted_intents`, `query`, `expected_status`, `allowed_source_versions`, `required_evidence_groups`, `required_source_types`, `required_answer_points`, `required_identifiers`, `forbidden_evidence`, `concept_scopes`, optional `cluster_id` and `challenge_tags`, and review metadata.
2. **Curation metadata record.** A sidecar keyed by `question_id` holds `curation_family_id`, novelty, coverage, origin, lifecycle, exposure, and split-eligibility information. It is intentionally separate because the current Pydantic Gold model forbids unknown fields.

The repository-local v1 layout, created only as content becomes necessary, is:

```text
evaluation/novel/v1/
  README.md
  manifest.json
  novel_dev.yaml
  novel_validation.yaml
  curation_metadata.yaml
  coverage_report.json
  exposure_ledger.jsonl
```

N0 does not create empty placeholders. N1 should introduce only files needed by the pilot. Protected holdout question and Gold content must never be stored in this directory or elsewhere in the normal repository.

Novel question IDs use `n###`. IDs are unique across all novel splits and are not reused after an information need has been materially changed or withdrawn.

## 4. Split contract

Target sizes are approximately 30 `novel_dev`, 15 `novel_validation`, and 15 externally managed `novel_holdout` questions. These are quality targets, not quotas that justify artificial questions or weak annotations.

### 4.1 `novel_dev`

`novel_dev` is exposed development measurement data. Curators and developers may inspect questions, annotations, case outcomes, traces, and detailed failure classifications. Development may address a general failure class at its owning layer.

It must not introduce question-specific triggers, terms, entities, symbols, paths, pages, answers, source quotas, weights, or guards. A fix that cannot be justified for unseen questions is not eligible merely because it improves `novel_dev`.

### 4.2 `novel_validation`

`novel_validation` is phase-level and frozen-candidate comparison evidence. Its questions and Gold annotations may be repository-visible after approval, but ordinary roadmap development tasks must not inspect them unless the current task explicitly authorizes validation analysis.

A validation case is **pristine for a development lineage** only while its case-level question content, Gold annotations, and outcome material (including answers, traces, and retrieved evidence) have not been inspected and used to choose or modify system behavior for that lineage. Mere repository presence, developer access, or permission to access the file does not contaminate a case.

When case-specific validation information is actually inspected and used to guide implementation, prompting, routing, scoring, threshold, or policy work, the case becomes **exposed validation evidence**. This includes use of question content or Gold annotation before any outcome, as well as use of a case-level failure or output after evaluation. The question remains in the dataset; the exposure ledger records the transition. It must not subsequently be counted as pristine validation evidence for the affected development lineage. Aggregate metrics that do not reveal or use case-specific information do not by themselves contaminate every validation case.

### 4.3 `novel_holdout`

`novel_holdout` is protected and externally administered. Questions, Gold evidence, answer points, and hidden expected answers do not enter the repository or ordinary Codex development context. Generated or internally developed drafts are never promoted directly into this split.

The external package may be loaded only for an explicitly authorized release/T5 evaluation through the existing `--dataset <external-path>` boundary. The repository may record the schema version, external dataset/package identity, expected count, corpus identity, loader contract, and release procedure, but not protected content.

Holdout results may support reporting, archival, and release decisions. A case-level holdout result must not be used to modify the system and rerun the same frozen release attempt. A later repaired candidate requires a new explicitly authorized release attempt with distinct candidate identity.

External holdout curation must attest that holdout items were not intentionally derived from exposed `novel_dev` or `novel_validation` semantic families. This declaration does not require revealing holdout questions, Gold, or family assignments to the repository.

## 5. Pilot policy

N1 curates 12–16 **candidate `novel_dev` questions**. `pilot` is a curation activity, not a fourth split:

- accepted candidates enter `novel_dev`;
- rejected candidates are discarded or returned to draft for substantive revision;
- no permanent `pilot` split or parallel pilot dataset is maintained.

N1 must not generate validation or holdout content merely to complete a count.

## 6. Formal novelty taxonomy

Every accepted question must have at least one substantive novelty type. Multiple types may apply.

| Type | Meaning |
|---|---|
| `entity` | An independently sampled entity creates a genuinely different information need or evidence path. |
| `relation` | The question asks about a relationship not measured by the closest exposed cases, such as ownership, compatibility, dependency, or producer-to-consumer flow. |
| `composition` | Correctness requires combining multiple independently necessary evidence groups or perspectives. |
| `reasoning_topology` | The evidence traversal differs substantively, such as multi-hop, cross-source, cross-repository, comparison, or causal tracing. |
| `nontrivial_expression` | The same domain is addressed through a materially different descriptive, causal, implicit, or identifier-free expression that changes recognition demands. |
| `failure_mode` | The expected behavior is a legitimate refusal, version conflict, or clarification need not already represented by an equivalent exposed information need. It must not be reverse-designed from a current system failure. |
| `task_form` | The user asks for a substantively different operation, such as locating, explaining, comparing, tracing, diagnosing, or giving a bounded procedure. |

### 6.1 Exclusions

A trivial paraphrase is not novel:

```text
Exposed: What does FooReader do?
Draft:   Could you explain what FooReader does?
```

Mechanical entity substitution is not automatically novel:

```text
Exposed: What does FooReader do?
Draft:   What does BarReader do?
```

The second question qualifies as entity novelty only if BarReader was independently sampled, its evidence or implementation behavior is genuinely different, and the question represents an independent information need.

Evidence overlap is allowed. A novel question may cite a repository, file, documentation page, or KnowledgeObject already used by exposed Gold. **Evidence overlap is not question overlap.** Novelty is determined from the information need, relation, evidence combination, reasoning topology, and task form, not from a requirement for unseen objects.

## 7. Novelty rationale and overlap review

The curation sidecar for every accepted question records:

```yaml
question_id: n001
curation_family_id: nf023
novelty:
  types:
    - relation
    - composition
  closest_exposed_cases:
    - g042
  benchmark_overlap:
    wording: low
    entity: partial
    evidence: partial
    information_need: low
  rationale: >
    Human-reviewed explanation of the substantive novelty.
```

The curator must identify the closest exposed Gold case or explicitly record `none_found`, explain why the new information need remains substantive, and classify whether overlap occurs in wording, entity, evidence, or information need.

Embedding or lexical similarity may assist review, but it cannot determine the authoritative novelty verdict. A human reviewer makes and records that decision.

### 7.1 Semantic-family isolation

`curation_family_id` identifies a shared underlying information need or near-equivalent semantic family. Trivial paraphrases and mechanical variants must be assigned to the same family or rejected; assigning different IDs does not make equivalent questions independent samples.

One semantic family must belong to only one repository-visible novel split. Semantically equivalent or trivial-variant questions must not cross `novel_dev` and `novel_validation`. For example, “How does X pass data to Y?” and “Trace the handoff from X into Y.” cannot count as independent dev and validation samples when they express the same underlying information need.

The existing Gold `cluster_id` split check applies only within one `GoldDataset` load. Because `novel_dev.yaml` and `novel_validation.yaml` may be loaded separately, N1 and later manifest/sidecar consistency validation must explicitly check family isolation across all repository-visible novel dataset files. `curation_family_id` in the sidecar is the cross-file authority; a compatible Gold `cluster_id` may mirror it but does not replace the cross-file check.

## 8. Difficulty is independent of novelty

Difficulty is assigned before any PANDA Agent outcome is observed and is based on question/evidence structure:

- `simple`: explicit entity, one main evidence group, one source or repository, and a direct information need;
- `moderate`: descriptive entity, two genuinely required evidence groups, producer-to-consumer reasoning, or multiple sources;
- `hard`: cross-repository or multi-hop reasoning, genuine ambiguity, multi-stage workflow, or at least three genuinely required evidence groups.

These descriptions guide human judgment rather than define a score formula. A question is not hard because PANDA Agent fails it, and a hard question is not necessarily more novel.

## 9. Coverage model

Coverage metadata uses the current product intent taxonomy:

`installation`, `usage`, `api`, `algorithm_theory`, `algorithm_implementation`, `data_flow`, `module_structure`, and `troubleshooting`.

The sidecar records at least:

- primary intent and any evaluator-compatible accepted intents;
- repository scope;
- source types;
- expression form: `explicit`, `descriptive`, `causal`, `implementation_oriented`, `identifier_free`, or `identifier_heavy`;
- evidence topology: `single_hop`, `multi_hop`, `comparison`, `causal_trace`, `producer_consumer`, or another reviewed description;
- single-source versus cross-source;
- single-repository versus cross-repository;
- reasoning/task forms;
- expected status;
- novelty types;
- difficulty.

Coverage review prevents blind spots but does not justify synthetic or low-quality questions. The complete `novel_dev` should cover all product intents where the locked corpus supports natural questions, avoid domination by one easy intent, and avoid a collection made mostly of expression-only novelty, explicit-symbol lookup, or single-hop questions. It should include credible descriptive-entity, multi-evidence, and cross-repository cases.

N0 does not freeze per-dimension quotas. N1 uses the pilot evidence to propose practical quotas only after curators learn which combinations the locked corpus naturally supports.

## 10. Expected status contract

Novel v1 may use the four canonical `QAStatus` values:

- `answered`
- `insufficient_evidence`
- `version_conflict`
- `clarification_required`

The current model and loader accept `clarification_required`, but the current Gold v2 status distribution does not formally cover it. Before N1 accepts a `clarification_required` question, a small generic T0 check must verify dataset parsing and evaluator metric applicability for that status. Any incompatibility is repaired generically; no case-specific evaluator branch is allowed. N0 does not implement or run that check.

Clarification questions must represent genuine ambiguity, an under-specified entity, or an unresolved reference. They must not be fabricated by deleting information from an otherwise clear benchmark question.

## 11. Annotation contract

Correctness annotation remains evaluator-compatible Gold:

```yaml
schema_version: '2.0'
benchmark_version: novel-v1-dev-<dataset-version>
release_eligible: false
acceptance_exposed: true
expected_split_counts:
  novel_dev: <approved-count>
expected_status_counts:
  answered: <count>
questions:
  - id: n001
    split: novel_dev
    language: en
    intent: algorithm_implementation
    query: "<human-reviewed question>"
    expected_status: answered
    allowed_source_versions:
      - <locked source identity>
    required_evidence_groups:
      - group_id: n001.e1
        role: <semantic role>
        critical: true
        any_of:
          - source_id: <source>
            path: <path or null>
            symbol: <symbol or null>
    required_source_types:
      - code
    required_answer_points:
      - point_id: p1
        text: <reviewed answer requirement>
        weight: 1.0
        critical: true
    required_identifiers: []
    forbidden_evidence: []
    concept_scopes: {}
    review_status: approved
    reviewer: <human reviewer identity>
    reviewed_at: <timestamp>
```

This is a schema illustration, not a real question or Gold record. Dataset-level expected counts must match approved contents rather than a hard-coded target. `release_eligible` and `acceptance_exposed` reflect the actual split and exposure state.

Novelty, coverage, origin, and lifecycle metadata remain in the sidecar:

```yaml
question_id: n001
curation_family_id: nf023
coverage:
  repositories:
    - pandaroot
    - luminosityfit
  source_scope: cross_source
  repository_scope: cross_repository
  expression_form: descriptive
  evidence_topology: multi_hop
  reasoning_forms:
    - trace
  difficulty: hard
curation:
  origin: human_authored
  agent_outcome_seen_before_freeze: false
  evidence_selected_from_agent_output: false
  lifecycle: split_frozen
```

This is also illustrative metadata, not a real question. N1 must define and validate the exact sidecar schema before committing pilot records.

## 12. Gold annotation independence

Before question and Gold freeze, curators may read the locked repositories, PDFs, documentation, source records, and KnowledgeObjects; use deterministic text or code search; inspect database objects; and apply human reasoning.

They must not:

```text
run PANDA Agent
-> inspect retrieved candidates or answers
-> choose Gold evidence from those outputs
```

Current PANDA Agent output must not participate in defining its own ground truth. Validation and holdout questions also must not be generated case by case from current candidate failures.

Every curation record declares `agent_outcome_seen_before_freeze: false` and `evidence_selected_from_agent_output: false`. If either statement cannot be truthfully made, the draft is ineligible for pristine validation or holdout and requires explicit exposed-development handling.

## 13. LLM-assisted curation

An LLM may propose candidate questions, improve natural English, identify possible coverage gaps, suggest novelty classifications, assist evidence inspection, or draft annotations. Its output is always an untrusted proposal, never Gold.

A human reviewer must independently confirm the question, expected status, required evidence groups, answer points, source/version constraints, novelty rationale, and split eligibility. Generated drafts cannot directly become protected holdout content.

## 14. Review and exposure lifecycle

The lightweight curation lifecycle is:

```text
draft
-> curation_review
-> novelty_review
-> evidence_review
-> approved
-> split_frozen
-> evaluated
```

The sidecar records this lifecycle. The evaluator's existing `review_status` remains `draft`, `approved`, or `rejected`: it stays `draft` during intermediate review stages and becomes `approved` only after all required human reviews pass. `evaluated` records history and does not reopen or rewrite Gold.

Review responsibilities are:

- curation review: natural, answerable user information need and product-scope fit;
- novelty review: substantive novelty and overlap rationale;
- evidence review: independent Gold correctness, source/version constraints, evidence groups, and answer points;
- split review: exposure suitability and coverage contribution.

The same person may perform multiple reviews for `novel_dev`; validation should receive an independent second review when practical. Protected holdout review is externally governed.

## 15. Validation exposure ledger

`novel_validation` uses an append-only JSONL ledger. The minimum event shape is:

```json
{"schema_version":"novel-exposure-ledger-v1","question_id":"n041","event":"case_content_used_for_development","timestamp":"<RFC3339>","development_lineage":"<candidate-or-branch>","reason":"<general failure-class investigation>","effect":"no_longer_pristine_validation"}
{"schema_version":"novel-exposure-ledger-v1","question_id":"n042","event":"case_gold_used_for_development","timestamp":"<RFC3339>","development_lineage":"<candidate-or-branch>","reason":"<general failure-class investigation>","effect":"no_longer_pristine_validation"}
{"schema_version":"novel-exposure-ledger-v1","question_id":"n043","event":"case_outcome_used_for_development","timestamp":"<RFC3339>","development_lineage":"<candidate-or-branch>","reason":"<general failure-class investigation>","effect":"no_longer_pristine_validation"}
```

Record the applicable event when case-level question content, Gold annotation, or outcome material is actually inspected and used to guide development. Access without development use is not an exposure event. Aggregate-only metric viewing does not require one contamination event per case. Corrections are appended as new events; old entries are not rewritten. Exposure does not delete the question or its historical measurements.

Reports must distinguish pristine-validation results from exposed-validation diagnostics for the relevant development lineage.

## 16. Protected holdout loading boundary

The protected package boundary is:

```text
external protected path or package
-> explicit release/T5 authorization
-> existing dataset loader
-> immutable release-attempt records
```

The repository-side release manifest may declare:

- novel schema and dataset version;
- opaque external package identity and dataset-level content identity;
- expected question count;
- locked corpus/source identity;
- compatible loader/evaluator version or Git commit;
- release attempt and authorization identifiers.

No secret-management system is required by N0. Access control and external storage are responsibilities of the holdout administrator.

## 17. Versioning and freeze

Each repository-visible novel dataset records:

- schema version;
- dataset version;
- Git commit containing the dataset and curation metadata;
- locked corpus/source identities;
- approved split counts;
- dataset-level content identity when required by a formal gate;
- amendment history.

Normal curation uses Git history. Per-question hashes, per-file hashes, repeated frozen candidates, and clean-tree ceremonies are not required. A formal phase boundary, T5/release evaluation, acceptance comparison, or explicit frozen-candidate request may require immutable dataset- and implementation-level identities under `AGENTS.md` and `docs/EVALUATION_POLICY.md`.

Freeze occurs only after required reviews and before any outcome is observed for the intended comparison. Split changes after freeze require a new dataset version.

## 18. Amendment rules

An **annotation correction** preserves the question ID when the information need is unchanged, for example a locator line correction, evidence-selector repair, or reviewer metadata fix. It increments the dataset version and records the old value, new value, reason, timestamp, and reviewer.

An **information-need change** creates a new question ID. Changing “Where is X defined?” into “How does X propagate into Y?” changes evaluation semantics and is not an annotation correction.

Corrections made after outcomes are observed must state that exposure and must never be presented as the original frozen Gold result.

## 19. Relationship to downstream work

Novel Dataset v1 is a reusable generalization asset for C8, Phases D, E, and F, the eventual Generalization Gap and Benchmark Dependency measurements, and authorized T4/T5 evaluation. It is not a phase-specific proof set.

If a subsystem needs a targeted diagnostic set, that set must be labelled and governed separately. It must not be silently merged into the general novel splits or represented as independent corroboration.

## 20. N1 entry contract

N1 — Novel-Dev Pilot Curation may begin only under these rules:

1. Use the locked authoritative source corpus and source-version universe, while allowing derived representations to evolve under traceable provenance, and use the eight canonical intents.
2. Propose 12–16 candidate `novel_dev` questions without running PANDA Agent.
3. Create the evaluator-compatible dataset and exact curation-sidecar schema together.
4. Perform human curation, novelty, evidence, and split review.
5. Validate parsing, sidecar consistency, and cross-file semantic-family isolation with T0 only.
6. If any candidate uses `clarification_required`, first run the small generic status compatibility check.
7. Accept, reject, or rework candidates on question and annotation quality, not system outcomes.
8. Do not start novel evaluation, N2, C8, or any production change without separate authorization.

N0 is complete when these rules are documented consistently with the current runtime/evaluator architecture and pilot curation can begin without observing PANDA Agent novel outcomes. N0 completion makes no claim that PANDA Agent generalizes.
