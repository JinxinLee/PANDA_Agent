# D3-A0 Shortcut Migration Selection and Preregistration Freeze

## Status

- **D3-A0:** COMPLETE / PREOUTCOME_SELECTION_FROZEN
- **D3-A0-R1:** COMPLETE / COMPARISON_IDENTIFIABILITY_AND_STAGE_BOUNDARY_REPAIRED
- **R1 task verdict:** PASS
- **Formal D3 experiment verdict:** NOT_RUN
- **Original source HEAD:** `6849c97f65090ccee5ff7e4af5aed6837ff20940`
- **R1 source HEAD:** `877935e`
- **Repair date:** 2026-08-31
- **Selected batch:** 7 of 54 legacy rules
- **Comparison set:** 16 committed English development cases
- **D3 outcome exposure:** NOT_STARTED
- **Formal D3 retrieval/model/API executions:** 0
- **D3-A1 / D3-A2:** NOT_STARTED / NOT_STARTED

This file preserves the original D3-A0 inventory and experiment design and records a pre-outcome R1 repair. It does not implement, activate, or measure a migration.

## D3-A0-R1 repair note

Audit found three defects before any D3 arm outcome: four original rules lacked a natural direct-trigger case, per-rule migration decisions were not separated from the overall verdict, and D3-A1 implementation was incorrectly collapsed with formal D3 execution. R1 repairs all three and isolates comparison metadata from runtime.

- Original selected rules: `lmd_fit_data_chain`, `event_poca_handoff`, `pid_two_pass_files`, `luminosityfit_model_layers`, `effective_acceptance_pipeline`, `restgas_profile_workflow`, `sphinx_operational_architecture`.
- Repaired selected rules: `lmd_fit_data_chain`, `event_poca_handoff`, `pid_two_pass_files`, `model_factory_theory`, `effective_acceptance_pipeline`, `restgas_profile_workflow`, `root_macro_usage`.
- Replacements: `luminosityfit_model_layers` → `model_factory_theory`; `sphinx_operational_architecture` → `root_macro_usage`.
- Deliberately retained generalization-only rules: `lmd_fit_data_chain`, `pid_two_pass_files`.
- Original/repaired manifest: 16 / 16 cases; added 0; removed 0.
- Changed bindings: `n014`, `g060`, `n004`, `g007`; changed roles: `n014`, `n004` from paraphrase to natural direct literal.
- Identifiable rules: 5/7 after R1, versus 3/7 before R1.

No D3 outcomes informed the repair. Static search used only approved English Gold v2.6 dev and frozen `novel_dev` question text under the current legacy case-insensitive substring semantics. Natural cases `g037` and `g051` were not added because they only duplicate direct coverage for already-identifiable rules.

## 1. Scope and evidence boundary

R1 performed static inspection of the legacy consumer, the preserved 54-rule/200-trigger inventory, accepted D1 structure, frozen D2 roles, Gold v2.6 dev, and frozen `novel_dev`. It did not inspect `novel_validation` or external holdout content.

No runtime code, configuration, D1/D2 knowledge artifact, production behavior, index, database, evaluator, or query-expansion rule changed. No retrieval, QA, model, analyzer, embedding, reranker, verifier, or judge call ran.

## 2. Frozen legacy behavior

`src/panda_agent/retrieval.py::_preparse` applies every rule whose trigger is a case-insensitive literal substring of the ordinary question. Every match accumulates reviewed repositories, symbols, concepts, and paper-page hints into deterministic parsing and then the retrieval plan.

D3 migration targets that fixed phrase-to-location dependency. Phrase-to-object, rule-ID-to-object, case-to-object, exact answer-path, or exact-page replacements remain prohibited.

## 3. Complete legacy-rule inventory

The preserved inventory contains 54 rules and 200 trigger strings. Every rule retains its literal triggers and fixed dependency payload. R1 changes only four first-batch dispositions.

| # | Rule | Family | Triggers | Symbols | Concepts | Page hints | R1 disposition |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | `lmd_fit_data_chain` | CROSS_REPOSITORY_DATA_FLOW | 3 | 5 | 2 | 0 | SELECTED_FIRST_BATCH |
| 2 | `event_poca_handoff` | WORKFLOW_DATA_FLOW | 4 | 4 | 2 | 2 | SELECTED_FIRST_BATCH |
| 3 | `restgas_profile_workflow` | WORKFLOW_DATA_FLOW | 4 | 5 | 2 | 0 | SELECTED_FIRST_BATCH |
| 4 | `pid_two_pass_files` | WORKFLOW_DATA_FLOW | 3 | 3 | 1 | 0 | SELECTED_FIRST_BATCH |
| 5 | `luminosityfit_model_layers` | CONCEPT_IMPLEMENTATION | 3 | 6 | 3 | 0 | EXCLUDED_FIRST_BATCH |
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
| 24 | `sphinx_operational_architecture` | VERSION_DOCUMENTATION | 5 | 5 | 1 | 0 | EXCLUDED_FIRST_BATCH |
| 25 | `fit_data_troubleshooting` | TROUBLESHOOTING_COMPATIBILITY | 9 | 6 | 2 | 0 | EXCLUDED_FIRST_BATCH |
| 26 | `root_macro_usage` | USAGE_INSTALLATION | 3 | 2 | 1 | 0 | SELECTED_FIRST_BATCH |
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
| 42 | `model_factory_theory` | CONCEPT_IMPLEMENTATION | 3 | 3 | 1 | 3 | SELECTED_FIRST_BATCH |
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

## 4. Repaired selected first batch

| # | Rule | Family | D1 support | Readiness |
|---:|---|---|---|---|
| 1 | `lmd_fit_data_chain` | CROSS_REPOSITORY_DATA_FLOW | PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP | READY_WITH_PREREGISTERED_COVERAGE_RISK |
| 2 | `event_poca_handoff` | WORKFLOW_DATA_FLOW | ACCEPTED_STRUCTURED_PATH | READY_FOR_BOUNDED_COMPARISON |
| 3 | `pid_two_pass_files` | WORKFLOW_DATA_FLOW | ACCEPTED_STRUCTURED_PATH | READY_FOR_BOUNDED_COMPARISON |
| 4 | `model_factory_theory` | CONCEPT_IMPLEMENTATION | PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP | READY_WITH_PREREGISTERED_COVERAGE_RISK |
| 5 | `effective_acceptance_pipeline` | CROSS_REPOSITORY_DATA_FLOW | PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP | READY_WITH_PREREGISTERED_COVERAGE_RISK |
| 6 | `restgas_profile_workflow` | WORKFLOW_DATA_FLOW | ACCEPTED_STRUCTURED_PATH | READY_FOR_BOUNDED_COMPARISON |
| 7 | `root_macro_usage` | USAGE_INSTALLATION | PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP | READY_WITH_PREREGISTERED_COVERAGE_RISK |

The batch retains nontrivial cross-repository and file-pattern/workflow coverage even though those two rules are not directly dependency-identifiable. The two replacements preserve their intended topology while making five of seven rules directly measurable without inventing cases.

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

### 4. `model_factory_theory`

- Selection: R1 replacement preserving concept-to-implementation coverage with accepted D1 IMPLEMENTS support and natural direct-trigger applicability in n014; selected without D3 outcome information.
- Current dependency: 1 repositories, 3 symbols, 1 concepts, 3 paper-page hints.
- D1 status: PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP.
- Accepted objects: `concept.luminosityfit.luminosity_fit_model`, `subsystem.luminosityfit.model_and_fit`.
- Accepted relations: `subsystem.luminosityfit.model_and_fit IMPLEMENTS concept.luminosityfit.luminosity_fit_model`.
- Alias/workflow boundary: none.
- Preserved gap: Accepted D1 structure supports the model concept-to-implementation boundary, but not a question-specific factory composition or the rule's paper-page hints. D3-A1 must not backfill this gap.
- D2 boundary: Tier S may bind only a directly matched source-native record; Tier D is additive and nonauthoritative, cannot canonicalize across records, and cannot restrict scope.

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

### 7. `root_macro_usage`

- Selection: R1 replacement preserving operational-documentation usage coverage with accepted D1 document-to-workflow support and natural direct-trigger applicability in n004; selected without D3 outcome information.
- Current dependency: 1 repositories, 2 symbols, 1 concepts, 0 paper-page hints.
- D1 status: PARTIAL_ACCEPTED_PATH_WITH_PRESERVED_GAP.
- Accepted objects: `document.pandaroot_sphinx_2023_08_25_dev`, `workflow.pandaroot.generic`.
- Accepted relations: `document.pandaroot_sphinx_2023_08_25_dev OPERATIONALLY_DOCUMENTS workflow.pandaroot.generic`.
- Alias/workflow boundary: none.
- Preserved gap: The accepted edge supports versioned operational documentation provenance but does not directly encode macro-invocation pages or PndMasterRunSim locations.
- D2 boundary: Generic ROOT-macro wording cannot grant canonical identity or bypass version/repository scope; Tier D ambiguity and abstention remain intact.


D1 gaps remain preregistered risks. D3-A1 cannot add objects, accepted relations, workflows, aliases, or evaluation-derived knowledge to close them.

## 4.1 Per-rule legacy-dependency identifiability

| Rule | Direct-trigger cases | Paraphrase | Controls | Status |
|---|---:|---:|---:|---|
| `lmd_fit_data_chain` | 0 (none) | 2 | 1 | PARTIALLY_IDENTIFIABLE |
| `event_poca_handoff` | 1 (g036) | 1 | 0 | IDENTIFIABLE |
| `pid_two_pass_files` | 0 (none) | 1 | 2 | PARTIALLY_IDENTIFIABLE |
| `model_factory_theory` | 1 (n014) | 1 | 0 | IDENTIFIABLE |
| `effective_acceptance_pipeline` | 1 (g052) | 0 | 2 | IDENTIFIABLE |
| `restgas_profile_workflow` | 1 (g021) | 0 | 0 | IDENTIFIABLE |
| `root_macro_usage` | 1 (n004) | 0 | 1 | IDENTIFIABLE |

`IDENTIFIABLE` means at least one frozen development-visible case naturally activates the rule, enabling an actual LEGACY − ABLATION dependency contrast. `PARTIALLY_IDENTIFIABLE` supports structured paraphrase/generalization analysis only. For partially identifiable rules, the D3-A2 per-rule migration decision is restricted to `INSUFFICIENT_EVIDENCE` unless a new pre-outcome preregistration establishes direct dependency.

## 5. D2 authority boundary

D2 authority is unchanged:

- Tier G: bounded authority for governed identity and accepted true co-reference.
- Tier S: direct matched-record identity only; no cross-record canonicalization.
- Tier D unique: nonauthoritative additive hint only.
- Tier D ambiguous: retain candidates; no collapse.
- UNRESOLVED: no negative filtering.
- Corrective terms: non-identity advisory only.
- SAME_AS and RESOLVED_MULTIPLE: unevaluated/inactive.
- Whole-question fallback: PRODUCTION_PROHIBITED.

No D3 exception exists.

## 6. Frozen three-arm design

1. **LEGACY:** all 54 rules active; D3 structured treatment disabled.
2. **ABLATION:** the seven selected rules disabled; D3 structured treatment disabled; nonselected rules unchanged.
3. **STRUCTURED:** the seven selected rules disabled; generic D3 structured treatment enabled; nonselected rules unchanged; no selected-rule legacy-payload fallback.

Cases, source versions, limits, evaluator semantics, and retrieval configuration must be identical across formal D3-A2 arms.

## 6.1 Restored D3 stage boundaries

**D3-A1 — Structured Shortcut-Replacement Prototype** is implementation-only. It may add experimental plumbing, selected-rule suppression, generic structured candidate contribution, deterministic provenance/diagnostics, T0 tests, and tiny non-evaluative plumbing smoke. It may not run the frozen manifest formally, compute paired arm metrics, inspect migration outcomes, retune from formal outcomes, or make migration decisions.

**D3-A2 — Frozen Three-Arm Comparison & Migration Decision** exclusively owns formal outcome exposure, paired metrics, legacy dependency, structured recovery/parity, failure classification, per-rule decisions, and the overall verdict. Before D3-A2 starts, `D3_A1_IMPLEMENTATION_FROZEN = true` and the ordinary Git implementation commit SHA must be recorded in its run manifest. If an implementation defect invalidates the run, stop and use `INCONCLUSIVE` as appropriate; do not patch and continue.

## 6.2 Runtime-input isolation

Structured runtime receives only:

- the ordinary production-style query and normal runtime context;
- experimental mode/config indicating which legacy rule IDs are disabled and whether generic D3 treatment is enabled.

`bound_rule_id` is grouping/reporting metadata only. It must never choose an object, relation path, structured seed, source, repository, path, or page. The same prohibition applies to case/question ID, comparison role, literal-trigger label, expected status, family, dataset/split, evidence IDs, representativeness, and selection metadata. Evaluation wrappers must strip all manifest metadata before runtime invocation.

## 7. Repaired frozen comparison set

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
| 9 | `n014` | novel_dev | `model_factory_theory` | DIRECT_LITERAL | yes | comparison | single_repository | representative |
| 10 | `g060` | Gold v2.6 dev | `model_factory_theory` | PARAPHRASE_RELEVANT | no | multi_hop | single_repository | benchmark_reference_unlabelled |
| 11 | `g052` | Gold v2.6 dev | `effective_acceptance_pipeline` | DIRECT_LITERAL | yes | single_hop | paper_only | benchmark_reference_unlabelled |
| 12 | `g055` | Gold v2.6 dev | `effective_acceptance_pipeline` | NEARBY_DISTINCTION_CONTROL | no | multi_hop | paper_only | benchmark_reference_unlabelled |
| 13 | `n003` | novel_dev | `effective_acceptance_pipeline` | NEARBY_NONTRIGGER_CONTROL | no | multi_hop | single_repository | representative |
| 14 | `g021` | Gold v2.6 dev | `restgas_profile_workflow` | DIRECT_LITERAL | yes | multi_hop | single_repository | benchmark_reference_unlabelled |
| 15 | `n004` | novel_dev | `root_macro_usage` | DIRECT_LITERAL | yes | single_hop | single_repository | representative |
| 16 | `g007` | Gold v2.6 dev | `root_macro_usage` | NEARBY_NEGATIVE_CONTROL | no | single_hop | single_repository | benchmark_reference_unlabelled |

Manifest history is explicit: 16 original cases, 16 repaired cases, no additions/removals, four changed bindings, and two role corrections. Each changed record contains its original/repaired binding, original/repaired role, and R1 reason. Historical dataset expected status remains evaluation metadata, not a D3 outcome.

## 8. Metrics and comparisons

| Metric | Unit | Direction | Frozen definition |
|---|---|---|---|
| `useful_retrieval_reproduction_rate` | case | higher | Among cases whose LEGACY arm retrieves at least one required evidence group in the final evidence, fraction for which STRUCTURED retrieves an equal or greater count of required evidence groups. |
| `final_evidence_recall` | required evidence group | higher | Evaluator-native required-evidence-group recall in final selected evidence, reported by arm and paired case. |
| `critical_evidence_recall` | critical required evidence group | higher | Evaluator-native recall over critical required evidence groups, reported by arm. |
| `selected_rule_dependency_rate` | case | descriptive | Fraction of cases where LEGACY final-evidence recall exceeds ABLATION final-evidence recall. |
| `structured_recovery_rate` | legacy-dependent case | higher | Among cases with LEGACY > ABLATION, fraction where STRUCTURED reaches or exceeds LEGACY final-evidence recall. |
| `regression_rate` | case | lower | Fraction of comparison cases where STRUCTURED final-evidence recall is below LEGACY. |

Required paired contrasts remain:

- STRUCTURED − LEGACY: migration regression or improvement.
- LEGACY − ABLATION: selected shortcut dependency.
- STRUCTURED − ABLATION: structured-path contribution.

Cells below five report numerator, denominator, and per-case ledger. R1 introduces no arbitrary numerical threshold.

## 9. Overall verdict versus per-rule migration decisions

Overall experiment verdict vocabulary is exactly:

- `PASS`
- `FAIL`
- `INCONCLUSIVE`

Per-rule migration decision vocabulary is exactly:

- `MIGRATION_SUPPORTED`
- `PARTIALLY_REPRODUCED`
- `STRUCTURED_REGRESSION`
- `NO_MEANINGFUL_LEGACY_DEPENDENCY`
- `INSUFFICIENT_EVIDENCE`

An overall PASS does not imply every rule is migration-supported. `MIGRATION_SUPPORTED` and `NO_MEANINGFUL_LEGACY_DEPENDENCY` require directly identifiable legacy dependency. A never-triggered rule cannot receive either label. The two R1 generalization-only rules must receive `INSUFFICIENT_EVIDENCE` for their migration decision unless a new preregistration makes dependency measurable.

Frozen failure labels remain:

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

## 10. Hard constraints and rollback

- Do not add or modify D1 objects, relations, workflow steps, or aliases inside D3-A1 to fit selected cases.
- Do not encode selected phrases, rule IDs, case IDs, expected symbols, paths, pages, answers, source quotas, weights, or guards as replacements.
- Do not widen Tier G/S/D authority, convert corrective terms into true aliases, enable whole-question fallback, or suppress ambiguity/abstention.
- Do not alter nonselected query-expansion rules, production defaults, analyzer prompts, embeddings, fusion, reranking, selector behavior, evaluator semantics, or datasets as part of the comparison.
- Do not inspect or execute novel_validation or external holdout.
- Do not use QA generation or an external judge to measure retrieval migration.
- Do not interpret this static preregistration repair as authorization for D3-A1 implementation or D3-A2 formal execution.
- D3-A1 cannot add D1 objects, accepted relations, workflow steps, aliases, or evaluation-derived knowledge. A generic D1 schema defect is a blocker requiring a separate authorization.
- Structured runtime must not receive bound_rule_id or any comparison-manifest metadata other than the ordinary query text.

Rollback remains the unchanged LEGACY state with all 54 rules active. On confounding, prohibited encoding, material regression, unsafe control leakage, or D2-boundary violation, stop and repair only under separate authorization. Do not add question-specific replacements or retain a silent mixed fallback.

## 11. Exposure and stop state

- `D3_OUTCOME_EXPOSURE = NOT_STARTED`.
- LEGACY / ABLATION / STRUCTURED formal arm runs: 0 / 0 / 0.
- New D3 Gold / `novel_dev` retrieval cases: 0 / 0.
- `novel_validation = UNSEEN`; external holdout = `SEALED_UNSEEN`.
- New model/analyzer/embedding/reranker/QA/verifier/judge calls: 0.
- Production/Qdrant/database writes: 0.
- Runtime/config/query-expansion/D1/D2 changes: none.
- Next task only: **D3-A1 — Structured Shortcut-Replacement Prototype**.
- D3-A1 and D3-A2 remain **NOT_STARTED** and require separate explicit authorization.
