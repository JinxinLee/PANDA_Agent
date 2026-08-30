# D3-A0 Shortcut Migration Selection and Preregistration Freeze

## Status

- **Task:** D3-A0
- **State:** COMPLETE / PREOUTCOME_SELECTION_FROZEN
- **Verdict:** PASS
- **Source HEAD:** `6849c97f65090ccee5ff7e4af5aed6837ff20940`
- **Frozen date:** 2026-08-30
- **Selected batch:** 7 of 54 legacy rules
- **Comparison set:** 16 committed English development cases
- **D3 retrieval/model/API executions:** 0
- **D3-A1:** NOT_STARTED

This stage freezes selection and experimental semantics only. It does not implement, activate, or measure a migration.

## 1. Scope and evidence boundary

D3-A0 performed static inspection of the legacy query-expansion consumer, all 54 rules, accepted D1 objects/relations/workflows/aliases, the frozen D2-A3 role decision, Gold v2.6 development questions, and frozen `novel_dev` metadata. It did not inspect `novel_validation` or external holdout content.

No runtime code, configuration, D1/D2 artifact, production behavior, index, database, or query-expansion rule changed. No retrieval, QA, model, analyzer, embedding, reranker, verifier, or judge call ran.

## 2. Frozen legacy behavior

`src/panda_agent/retrieval.py::_preparse` applies every rule whose trigger is a case-insensitive literal substring of the raw question. Every match accumulates fixed reviewed repositories, symbols, concepts, and paper page hints into deterministic parsing and then the retrieval plan. The recorded provenance is `reviewed_expansion / fixed_reviewed_rule`.

D3 migration targets that fixed phrase-to-location dependency. A replacement must traverse already accepted identities, relations, workflows, and evidence provenance. Phrase-to-object, rule-ID-to-object, case-to-object, exact answer-path, or exact page maps are prohibited.

## 3. Complete legacy-rule inventory

Summary: 54 rules, 200 trigger strings, 51 rules injecting symbols, 54 injecting concepts, and 22 injecting paper-page hints. Every rule has a first-batch disposition in the machine-readable artifact.

| # | Rule | Family | Triggers | Symbols | Concepts | Page hints | D3-A0 disposition |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | `lmd_fit_data_chain` | CROSS_REPOSITORY_DATA_FLOW | 3 | 5 | 2 | 0 | SELECTED_FIRST_BATCH |
| 2 | `event_poca_handoff` | WORKFLOW_DATA_FLOW | 4 | 4 | 2 | 2 | SELECTED_FIRST_BATCH |
| 3 | `restgas_profile_workflow` | WORKFLOW_DATA_FLOW | 4 | 5 | 2 | 0 | SELECTED_FIRST_BATCH |
| 4 | `pid_two_pass_files` | WORKFLOW_DATA_FLOW | 3 | 3 | 1 | 0 | SELECTED_FIRST_BATCH |
| 5 | `luminosityfit_model_layers` | CONCEPT_IMPLEMENTATION | 3 | 6 | 3 | 0 | SELECTED_FIRST_BATCH |
| 6 | `resolution_models` | CONCEPT_IMPLEMENTATION | 5 | 3 | 3 | 3 | EXCLUDED_FIRST_BATCH |
| 7 | `resolution_api_locator` | DIRECT_API_FILE_LOCATOR | 1 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 8 | `displaced_tracking` | CONCEPT_IMPLEMENTATION | 5 | 3 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 9 | `angular_acceptance` | CONCEPT_IMPLEMENTATION | 4 | 1 | 1 | 3 | EXCLUDED_FIRST_BATCH |
| 10 | `longitudinal_efficiency` | CONCEPT_IMPLEMENTATION | 3 | 2 | 1 | 3 | EXCLUDED_FIRST_BATCH |
| 11 | `nonexistent_restgas_deconvolver` | PREMISE_CORRECTION | 1 | 1 | 1 | 2 | EXCLUDED_FIRST_BATCH |
| 12 | `lmd_reconstruction_to_qa` | WORKFLOW_DATA_FLOW | 3 | 3 | 1 | 3 | EXCLUDED_FIRST_BATCH |
| 13 | `target_pid_pipeline` | WORKFLOW_DATA_FLOW | 7 | 4 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 14 | `profile_generation_and_correction` | WORKFLOW_DATA_FLOW | 8 | 3 | 3 | 3 | EXCLUDED_FIRST_BATCH |
| 15 | `event_alignment` | WORKFLOW_DATA_FLOW | 5 | 4 | 1 | 2 | EXCLUDED_FIRST_BATCH |
| 16 | `luminosity_extraction_results` | WORKFLOW_DATA_FLOW | 4 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 17 | `target_track_to_poca` | WORKFLOW_DATA_FLOW | 5 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 18 | `effective_acceptance_pipeline` | CROSS_REPOSITORY_DATA_FLOW | 5 | 3 | 1 | 3 | SELECTED_FIRST_BATCH |
| 19 | `vertex_fit_boundary` | WORKFLOW_DATA_FLOW | 5 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 20 | `reconstructed_profile_to_acceptance` | CROSS_REPOSITORY_DATA_FLOW | 5 | 2 | 1 | 3 | EXCLUDED_FIRST_BATCH |
| 21 | `panda_luminosityfit_boundary` | CROSS_REPOSITORY_DATA_FLOW | 4 | 3 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 22 | `restgas_pandaroot_extension` | CROSS_REPOSITORY_DATA_FLOW | 4 | 4 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 23 | `target_macro_workflow_grouping` | WORKFLOW_DATA_FLOW | 5 | 7 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 24 | `sphinx_operational_architecture` | VERSION_DOCUMENTATION | 5 | 5 | 1 | 0 | SELECTED_FIRST_BATCH |
| 25 | `fit_data_troubleshooting` | TROUBLESHOOTING_COMPATIBILITY | 9 | 6 | 2 | 0 | EXCLUDED_FIRST_BATCH |
| 26 | `root_macro_usage` | USAGE_INSTALLATION | 3 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 27 | `restgas_workflow_usage` | WORKFLOW_DATA_FLOW | 2 | 3 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 28 | `installation_requirements` | USAGE_INSTALLATION | 4 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 29 | `simulation_configuration_usage` | USAGE_INSTALLATION | 3 | 3 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 30 | `fit_data_usage` | USAGE_INSTALLATION | 4 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 31 | `run_fit_usage` | USAGE_INSTALLATION | 4 | 4 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 32 | `acceptance_model_boundary` | CONCEPT_IMPLEMENTATION | 3 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 33 | `event_poca_troubleshooting` | TROUBLESHOOTING_COMPATIBILITY | 5 | 6 | 2 | 0 | EXCLUDED_FIRST_BATCH |
| 34 | `acceptance_efficiency_disambiguation` | TROUBLESHOOTING_COMPATIBILITY | 2 | 1 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 35 | `version_mismatch_troubleshooting` | TROUBLESHOOTING_COMPATIBILITY | 4 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 36 | `luminosity_equation_theory` | PAPER_PAGE_THEORY | 2 | 0 | 4 | 3 | EXCLUDED_FIRST_BATCH |
| 37 | `beam_divergence_theory` | CONCEPT_IMPLEMENTATION | 2 | 2 | 2 | 3 | EXCLUDED_FIRST_BATCH |
| 38 | `lmd_backpropagation_theory` | CONCEPT_IMPLEMENTATION | 3 | 1 | 1 | 3 | EXCLUDED_FIRST_BATCH |
| 39 | `restgas_poca_theory` | CONCEPT_IMPLEMENTATION | 3 | 2 | 2 | 3 | EXCLUDED_FIRST_BATCH |
| 40 | `pointlike_vs_restgas_acceptance` | CROSS_REPOSITORY_DATA_FLOW | 2 | 0 | 1 | 5 | EXCLUDED_FIRST_BATCH |
| 41 | `hv_maps_vertex_resolution` | CONCEPT_IMPLEMENTATION | 3 | 1 | 1 | 3 | EXCLUDED_FIRST_BATCH |
| 42 | `model_factory_theory` | CONCEPT_IMPLEMENTATION | 3 | 3 | 1 | 3 | EXCLUDED_FIRST_BATCH |
| 43 | `dpm_model_theory` | CONCEPT_IMPLEMENTATION | 2 | 0 | 1 | 3 | EXCLUDED_FIRST_BATCH |
| 44 | `target_generator_theory` | CONCEPT_IMPLEMENTATION | 2 | 2 | 1 | 2 | EXCLUDED_FIRST_BATCH |
| 45 | `displaced_tracking_theory` | CONCEPT_IMPLEMENTATION | 3 | 3 | 1 | 2 | EXCLUDED_FIRST_BATCH |
| 46 | `vertex_fit_boundary_theory` | CONCEPT_IMPLEMENTATION | 3 | 2 | 1 | 2 | EXCLUDED_FIRST_BATCH |
| 47 | `similarly_named_track_finders` | CONCEPT_IMPLEMENTATION | 4 | 2 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 48 | `dpm_angular_models` | CONCEPT_IMPLEMENTATION | 4 | 2 | 1 | 2 | EXCLUDED_FIRST_BATCH |
| 49 | `event_poca_workflow_alias` | WORKFLOW_DATA_FLOW | 3 | 5 | 2 | 0 | EXCLUDED_FIRST_BATCH |
| 50 | `reconstructed_profile_factory_alias` | CROSS_REPOSITORY_DATA_FLOW | 2 | 3 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 51 | `master_reconstruction_workflow` | WORKFLOW_DATA_FLOW | 3 | 4 | 2 | 0 | EXCLUDED_FIRST_BATCH |
| 52 | `target_generator_sampling_data_flow` | CROSS_REPOSITORY_DATA_FLOW | 4 | 6 | 4 | 0 | EXCLUDED_FIRST_BATCH |
| 53 | `model_factory_acceptance_methods` | CONCEPT_IMPLEMENTATION | 4 | 3 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 54 | `restgas_longitudinal_efficiency_contrast` | CONCEPT_IMPLEMENTATION | 4 | 2 | 2 | 0 | EXCLUDED_FIRST_BATCH |

The JSON artifact preserves every literal trigger, repository, symbol, concept, page hint, exact-trigger overlap, current consumer semantics, and the specific inclusion/exclusion reason.

## 4. Selected first batch

| # | Rule | Family | D1 support | Readiness |
|---:|---|---|---|---|
| 1 | `lmd_fit_data_chain` | CROSS_REPOSITORY_DATA_FLOW | PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP | READY_WITH_PREREGISTERED_COVERAGE_RISK |
| 2 | `event_poca_handoff` | WORKFLOW_DATA_FLOW | ACCEPTED_STRUCTURED_PATH | READY_FOR_BOUNDED_COMPARISON |
| 3 | `pid_two_pass_files` | WORKFLOW_DATA_FLOW | ACCEPTED_STRUCTURED_PATH | READY_FOR_BOUNDED_COMPARISON |
| 4 | `luminosityfit_model_layers` | CONCEPT_IMPLEMENTATION | PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP | READY_WITH_PREREGISTERED_COVERAGE_RISK |
| 5 | `effective_acceptance_pipeline` | CROSS_REPOSITORY_DATA_FLOW | PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP | READY_WITH_PREREGISTERED_COVERAGE_RISK |
| 6 | `restgas_profile_workflow` | WORKFLOW_DATA_FLOW | ACCEPTED_STRUCTURED_PATH | READY_FOR_BOUNDED_COMPARISON |
| 7 | `sphinx_operational_architecture` | VERSION_DOCUMENTATION | ACCEPTED_STRUCTURED_PATH | READY_FOR_BOUNDED_COMPARISON |

The seven rules cover cross-repository data flow, workflow handoff, file-pattern workflow, concept-to-implementation, physics concept-to-pipeline, configuration-to-workflow, and versioned documentation provenance. Direct locator and nonexistent-premise correction rules are deliberately excluded; overlapping rules are held out to keep attribution bounded.

### 1. `lmd_fit_data_chain`

- Selection: Representative cross-repository producer/consumer chain with accepted D1 edges and an intentionally preserved downstream coverage gap.
- Current dependency: 2 repositories, 5 symbols, 2 concepts, 0 paper-page hints.
- D1 status: PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP.
- Accepted objects: `workflow.pandaroot.lmd_reconstruction`, `data_product.pandaroot.lumi_trks_qa`, `subsystem.luminosityfit.panda_data_io`.
- Accepted relations: `workflow.pandaroot.lmd_reconstruction PRODUCES data_product.pandaroot.lumi_trks_qa`; `data_product.pandaroot.lumi_trks_qa PRODUCES_INPUT_FOR subsystem.luminosityfit.panda_data_io`.
- Alias/workflow boundary: none.
- Preserved gap: Accepted D1 structure covers reconstruction output through the LuminosityFit reader boundary, but not createLmdFitData/runLmdFit/extractLuminosityValues orchestration. D3-A1 must not backfill this gap from the selected evaluation cases.
- D2 boundary: Tier S may bind only a directly matched source-native record; Tier D may add advisory candidates but cannot canonicalize or restrict scope.

### 2. `event_poca_handoff`

- Selection: Representative event-aligned two-pass handoff with accepted workflow/data-product structure and exact identifier surfaces.
- Current dependency: 2 repositories, 4 symbols, 2 concepts, 2 paper-page hints.
- D1 status: ACCEPTED_STRUCTURED_PATH.
- Accepted objects: `workflow.restgas.first_pass_poca`, `data_product.restgas.boost_root`, `data_product.restgas.event_poca`, `workflow.restgas.second_pass_pid`, `data_product.restgas.pid_final_root`.
- Accepted relations: `workflow.restgas.first_pass_poca PRODUCES data_product.restgas.boost_root`; `data_product.restgas.event_poca PRODUCES_INPUT_FOR workflow.restgas.second_pass_pid`; `workflow.restgas.second_pass_pid PRODUCES data_product.restgas.pid_final_root`.
- Alias/workflow boundary: workflow.restgas_profile_reconstruction -> workflow.restgas.first_pass_poca (pid_root -> boost_root).
- Preserved gap: The accepted workflow models the event-POCA/second-pass handoff but does not encode question-specific JSON or environment-variable answer locations.
- D2 boundary: Exact identity is record-local; descriptive resolution is advisory and must preserve ambiguity/abstention.

### 3. `pid_two_pass_files`

- Selection: Representative file-pattern and two-pass workflow rule combining accepted D1 products, workflow structure, and a Tier-G true alias.
- Current dependency: 1 repositories, 3 symbols, 1 concepts, 0 paper-page hints.
- D1 status: ACCEPTED_STRUCTURED_PATH.
- Accepted objects: `data_product.restgas.pid_root`, `workflow.restgas.first_pass_poca`, `data_product.restgas.boost_root`, `data_product.restgas.event_poca`, `workflow.restgas.second_pass_pid`, `data_product.restgas.pid_final_root`.
- Accepted relations: `workflow.restgas.first_pass_poca CONSUMES data_product.restgas.pid_root`; `workflow.restgas.first_pass_poca PRODUCES data_product.restgas.boost_root`; `data_product.restgas.event_poca PRODUCES_INPUT_FOR workflow.restgas.second_pass_pid`; `workflow.restgas.second_pass_pid PRODUCES data_product.restgas.pid_final_root`.
- Alias/workflow boundary: workflow.restgas_profile_reconstruction -> workflow.restgas.first_pass_poca (pid_root -> boost_root); accepted true alias: *_pid_final.root -> data_product.restgas.pid_final_root.
- Preserved gap: No accepted identity maps generic descriptive phrases or *_pid.root directly to a canonical object.
- D2 boundary: Only the accepted Tier-G co-reference may canonicalize; exact source-native matches remain record-local and Tier D is nonauthoritative.

### 4. `luminosityfit_model_layers`

- Selection: Representative concept-to-implementation rule with an accepted IMPLEMENTS edge and bounded source-native identifiers.
- Current dependency: 1 repositories, 6 symbols, 3 concepts, 0 paper-page hints.
- D1 status: PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP.
- Accepted objects: `concept.luminosityfit.luminosity_fit_model`, `subsystem.luminosityfit.model_and_fit`.
- Accepted relations: `subsystem.luminosityfit.model_and_fit IMPLEMENTS concept.luminosityfit.luminosity_fit_model`.
- Alias/workflow boundary: none.
- Preserved gap: D1 represents the subsystem/factory evidence boundary, not every injected model source file. Source-native identifiers remain noncanonical unless Tier G explicitly governs co-reference.
- D2 boundary: No cross-record canonicalization from Tier S; descriptive model-layer wording cannot create canonical identity.

### 5. `effective_acceptance_pipeline`

- Selection: Representative cross-repository physics-concept-to-pipeline rule with accepted D1 relation support and descriptive terminology risk.
- Current dependency: 2 repositories, 3 symbols, 1 concepts, 3 paper-page hints.
- D1 status: PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP.
- Accepted objects: `concept.li_2026.restgas_effective_acceptance`, `workflow.restgas_aware_luminosity_acceptance`, `workflow.restgas_profile_reconstruction`.
- Accepted relations: `concept.li_2026.restgas_effective_acceptance IMPLEMENTED_AS_PIPELINE workflow.restgas_aware_luminosity_acceptance`; `workflow.restgas_profile_reconstruction PRODUCES_PROFILE_FOR workflow.restgas_aware_luminosity_acceptance`.
- Alias/workflow boundary: none.
- Preserved gap: Accepted D1 structure establishes the concept/pipeline relationship but does not encode evaluation-specific pages, exact answer locations, or every repository implementation file.
- D2 boundary: Tier D cannot narrow repository/source scope or suppress competing structured candidates.

### 6. `restgas_profile_workflow`

- Selection: Representative configuration/file-pattern-to-workflow rule with multiple accepted D1 edges.
- Current dependency: 2 repositories, 5 symbols, 2 concepts, 0 paper-page hints.
- D1 status: ACCEPTED_STRUCTURED_PATH.
- Accepted objects: `configuration.restgas_profile`, `file_pattern.restgas_profile_input`, `workflow.restgas_profile_reconstruction`, `workflow.restgas_aware_luminosity_acceptance`.
- Accepted relations: `configuration.restgas_profile PARAMETERIZES workflow.restgas_profile_reconstruction`; `file_pattern.restgas_profile_input PRODUCES_INPUT_FOR workflow.restgas_profile_reconstruction`; `workflow.restgas_profile_reconstruction PRODUCES_PROFILE_FOR workflow.restgas_aware_luminosity_acceptance`.
- Alias/workflow boundary: workflow.restgas_profile_reconstruction -> workflow.restgas.first_pass_poca (pid_root -> boost_root); corrective term only: restgas_profile.txt corrects to configuration.restgas_profile; it is not a true co-reference alias.
- Preserved gap: The corrective term may repair terminology only and cannot grant canonical identity or answer-location authority.
- D2 boundary: restgas_profile.txt is correction-only; it cannot canonicalize. Tier D remains additive and abstention-preserving.

### 7. `sphinx_operational_architecture`

- Selection: Representative versioned-document-to-operational-workflow rule with accepted D1 documentation provenance.
- Current dependency: 1 repositories, 5 symbols, 1 concepts, 0 paper-page hints.
- D1 status: ACCEPTED_STRUCTURED_PATH.
- Accepted objects: `document.pandaroot_sphinx_2023_08_25_dev`, `workflow.pandaroot.generic`.
- Accepted relations: `document.pandaroot_sphinx_2023_08_25_dev OPERATIONALLY_DOCUMENTS workflow.pandaroot.generic`.
- Alias/workflow boundary: none.
- Preserved gap: The accepted edge establishes versioned documentation provenance, not direct routing to any one installation/running page.
- D2 boundary: Versioned documentation identity may be direct-matched only; descriptive documentation terms cannot bypass version scope.


D1 gaps are frozen as risks, not invitations to add case-driven objects or edges. No D1 backfill is authorized inside D3-A1.

## 5. D2 authority boundary

The experiment preserves the D2-A3 decision exactly:

- Tier G is authoritative only for governed identity and accepted true co-reference.
- Tier S is authoritative only for a directly matched record and never for cross-record canonicalization.
- Tier D, ambiguity, abstention, and corrective terms are production-consumable but nonauthoritative/advisory.
- `RESOLVED_UNIQUE` alone grants no authority.
- Corrective `restgas_profile.txt` is not a true alias.
- Whole-question fallback remains prohibited.
- Query expansions remain nonauthoritative.

A structured arm may add eligible candidates through accepted structure, but it may not narrow repository/version/source scope, suppress competitors, or bypass abstention.

## 6. Frozen three-arm design

1. **LEGACY:** all 54 current rules remain active exactly as frozen. This is the compatibility reference and rollback target.
2. **STRUCTURED:** disable only the seven selected rules and use only already accepted D1 structure under frozen D2 authority. No selected-rule payload fallback.
3. **ABLATION:** disable only the seven selected rules and disable their D3 structured replacement. All ordinary unaffected retrieval components and nonselected rules remain unchanged.

Cases, source versions, candidate limits, evaluator semantics, and retrieval configuration must be identical across arms. Arm identity must be recorded per case. Incomplete or confounded pairs cannot be merged into a complete comparison.

## 7. Frozen comparison set

Selection used committed question/evidence metadata before any D3 outcome. It intentionally includes direct literals, paraphrases without literals, and nearby/negative controls. Gold cases are benchmark references without a separate representative/exploratory label; all selected `novel_dev` cases retain their frozen `representative` curation label.

| # | Case | Dataset | Bound rule | Role | Literal | Topology | Repository scope | Representativeness |
|---:|---|---|---|---|---|---|---|---|
| 1 | `g029` | Gold v2.6 dev | `lmd_fit_data_chain` | PARAPHRASE_RELEVANT | no | single_hop | single_repository | benchmark_reference_unlabelled |
| 2 | `n021` | novel_dev | `lmd_fit_data_chain` | PARAPHRASE_RELEVANT | no | multi_hop | cross_repository | representative |
| 3 | `g025` | Gold v2.6 dev | `lmd_fit_data_chain` | NEARBY_NEGATIVE_CONTROL | no | single_hop | single_repository | benchmark_reference_unlabelled |
| 4 | `g036` | Gold v2.6 dev | `event_poca_handoff` | DIRECT_LITERAL | yes | single_hop | single_repository | benchmark_reference_unlabelled |
| 5 | `n022` | novel_dev | `event_poca_handoff` | PARAPHRASE_RELEVANT | no | producer_consumer | single_repository | representative |
| 6 | `g020` | Gold v2.6 dev | `pid_two_pass_files` | PARAPHRASE_RELEVANT | no | multi_hop | single_repository | benchmark_reference_unlabelled |
| 7 | `n006` | novel_dev | `pid_two_pass_files` | NEARBY_NONTRIGGER_CONTROL | no | multi_hop | single_repository | representative |
| 8 | `g041` | Gold v2.6 dev | `pid_two_pass_files` | NEARBY_NEGATIVE_CONTROL | no | single_hop | cross_repository | benchmark_reference_unlabelled |
| 9 | `n014` | novel_dev | `luminosityfit_model_layers` | PARAPHRASE_RELEVANT | no | comparison | single_repository | representative |
| 10 | `g060` | Gold v2.6 dev | `luminosityfit_model_layers` | PARAPHRASE_RELEVANT | no | multi_hop | single_repository | benchmark_reference_unlabelled |
| 11 | `g052` | Gold v2.6 dev | `effective_acceptance_pipeline` | DIRECT_LITERAL | yes | single_hop | paper_only | benchmark_reference_unlabelled |
| 12 | `g055` | Gold v2.6 dev | `effective_acceptance_pipeline` | NEARBY_DISTINCTION_CONTROL | no | multi_hop | paper_only | benchmark_reference_unlabelled |
| 13 | `n003` | novel_dev | `effective_acceptance_pipeline` | NEARBY_NONTRIGGER_CONTROL | no | multi_hop | single_repository | representative |
| 14 | `g021` | Gold v2.6 dev | `restgas_profile_workflow` | DIRECT_LITERAL | yes | multi_hop | single_repository | benchmark_reference_unlabelled |
| 15 | `n004` | novel_dev | `sphinx_operational_architecture` | PARAPHRASE_RELEVANT | no | single_hop | single_repository | representative |
| 16 | `g007` | Gold v2.6 dev | `sphinx_operational_architecture` | NEARBY_NEGATIVE_CONTROL | no | single_hop | single_repository | benchmark_reference_unlabelled |

The complete manifest in JSON also records query text, intent, expected status from the source dataset, evidence-group counts, source IDs, challenge tags, and the exact pre-outcome selection basis. Historical expected status is selection metadata, not a D3 outcome.

## 8. Metrics and comparisons

| Metric | Unit | Direction | Frozen definition |
|---|---|---|---|
| `useful_retrieval_reproduction_rate` | case | higher | Among cases whose LEGACY arm retrieves at least one required evidence group in the final evidence, fraction for which STRUCTURED retrieves an equal or greater count of required evidence groups. |
| `final_evidence_recall` | required evidence group | higher | Evaluator-native required-evidence-group recall in final selected evidence, reported by arm and paired case. |
| `critical_evidence_recall` | critical required evidence group | higher | Evaluator-native recall over critical required evidence groups, reported by arm. |
| `selected_rule_dependency_rate` | case | descriptive | Fraction of cases where LEGACY final-evidence recall exceeds ABLATION final-evidence recall. |
| `structured_recovery_rate` | legacy-dependent case | higher | Among cases with LEGACY > ABLATION, fraction where STRUCTURED reaches or exceeds LEGACY final-evidence recall. |
| `regression_rate` | case | lower | Fraction of comparison cases where STRUCTURED final-evidence recall is below LEGACY. |

Secondary metrics are Recall@5/@10/@20, MRR, combined candidate recall, source-type/repository-scope satisfaction, structured contribution counts, legacy match counts, D2 status counts, and per-family/direct-paraphrase-control ledgers.

Required paired contrasts:

- STRUCTURED − LEGACY: migration regression or improvement.
- LEGACY − ABLATION: selected shortcut dependency.
- STRUCTURED − ABLATION: structured-path contribution.

Cells below five always show numerator, denominator, and per-case ledger; percentages alone are prohibited. D3-A0 freezes no numerical PASS threshold.

## 9. Outcome vocabulary and failure taxonomy

Task verdicts are exactly `PASS`, `FAIL`, or `INCONCLUSIVE`. Case/arm outcomes are `FULL_REPRODUCTION`, `PARTIAL_REPRODUCTION`, `NO_REPRODUCTION`, `IMPROVEMENT`, `REGRESSION`, `NOT_APPLICABLE`, `NOT_RUN`, or `INFRASTRUCTURE_FAILURE`.

Frozen failure labels:

- `STRUCTURED_CANDIDATE_RECALL_FAILURE`
- `RELATION_COVERAGE_GAP`
- `WORKFLOW_COVERAGE_GAP`
- `EVIDENCE_LINK_COVERAGE_GAP`
- `ENTITY_OR_TERMINOLOGY_RESOLUTION_FAILURE`
- `AMBIGUITY_OR_ABSTENTION`
- `REPOSITORY_OR_VERSION_SCOPE_FAILURE`
- `FUSION_OR_RANKING_FAILURE`
- `FINAL_SELECTOR_FAILURE`
- `LEGACY_DEPENDENCY_WITHOUT_STRUCTURED_RECOVERY`
- `CONTROL_LEAKAGE_OR_OVERMATCH`
- `PROHIBITED_SHORTCUT_ENCODING`
- `INFRASTRUCTURE_OR_ARTIFACT_FAILURE`

Infrastructure failures are never retrieval failures. Incomplete pairing, invalid artifacts, confounded arms, or insufficient attribution are `INCONCLUSIVE`, not a synthetic success or failure.

## 10. Hard constraints and rollback

- Do not add or modify D1 objects, relations, workflow steps, or aliases inside D3-A1 to fit selected cases.
- Do not encode selected phrases, rule IDs, case IDs, expected symbols, paths, pages, answers, source quotas, weights, or guards as replacements.
- Do not widen Tier G/S/D authority, convert corrective terms into true aliases, enable whole-question fallback, or suppress ambiguity/abstention.
- Do not alter nonselected query-expansion rules, production defaults, analyzer prompts, embeddings, fusion, reranking, selector behavior, evaluator semantics, or datasets as part of the comparison.
- Do not inspect or execute novel_validation or external holdout.
- Do not use QA generation or an external judge to measure retrieval migration.
- Do not interpret a static preregistration freeze as authorization for D3-A1 implementation or execution.

Rollback target: the LEGACY arm at the frozen source HEAD, with all 54 rules active. On confounding, prohibited encoding, material regression, unsafe control leakage, or D2-boundary violation, stop, retain/re-enable the selected rules, and repair only the owning generic resolver/schema layer under separate authorization. Do not add question-specific replacements or silently retain a mixed fallback.

## 11. Exposure and stop state

- New D3/Gold/`novel_dev` retrieval cases run: 0.
- `novel_validation` cases run or inspected: 0.
- External holdout cases run or inspected: 0.
- New model/embedding/analyzer/reranker/judge calls: 0.
- Production/Qdrant/database writes: 0.
- Runtime/config/D1/D2 changes: none.
- Next roadmap task: **D3-A1 — Implement and execute the frozen three-arm shortcut-migration experiment**.
- D3-A1 remains **NOT_STARTED** and requires separate explicit authorization.
