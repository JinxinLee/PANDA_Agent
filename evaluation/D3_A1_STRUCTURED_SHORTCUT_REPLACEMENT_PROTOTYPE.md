# D3-A1 Structured Shortcut-Replacement Prototype

## 1. Objective and boundary

D3-A1 implements and freezes experimental retrieval plumbing only. It does not expose a formal D3 outcome, run a comparison case, calculate an arm metric, or make a migration decision. The starting implementation base is `a1d1408` (`D3-A0-R1 repair comparison identifiability and stage boundaries`).

## 2. Frozen preregistration inputs

The implementation follows `evaluation/d3_a0_shortcut_migration_preregistration.json` and `evaluation/D3_A0_SHORTCUT_MIGRATION_PREREGISTRATION.md` without changing their seven-rule selection, comparison bindings, authority contract, or stage boundary. The selected IDs are:

1. `lmd_fit_data_chain`
2. `event_poca_handoff`
3. `pid_two_pass_files`
4. `model_factory_theory`
5. `effective_acceptance_pipeline`
6. `restgas_profile_workflow`
7. `root_macro_usage`

## 3. Three-arm implementation

- `LEGACY`: all 54 configured rules remain active and structured treatment is disabled.
- `ABLATION`: exactly the selected seven are suppressed, all nonselected rules remain active, and structured treatment is disabled.
- `STRUCTURED`: exactly the selected seven are suppressed, all nonselected rules remain active, and generic structured treatment is enabled.

The config validator rejects a changed selected-ID set and rejects any arm/structured-enable combination that would create a fourth hybrid mode. Every explicit experimental receipt declares the arm, selected IDs, suppression state, and structured-treatment state.

## 4. Legacy-rule suppression

Rule matching is separated from payload application. In ABLATION and STRUCTURED, membership in the exact selected-ID set is checked before `repositories`, `symbols`, `concepts`, or `paper_page_hints` are accessed. Nonselected rules are not suppressed because of overlapping triggers, payloads, or topology. No query-expansion file was changed.

## 5. Generic structured path

STRUCTURED uses the ordinary question and `RetrievalPlan`, calls the existing D2 shadow resolver, derives governed/advisory seeds under the D2-A3 authority rules, traverses existing accepted D1 relations and curated workflow structure, and contributes the resulting source-native objects to the existing graph candidate channel. The implementation contains no phrase-to-object, rule-to-object, rule-to-path, case-to-object, or expected-evidence lookup.

## 6. D2 authority enforcement

- Tier G preserves bounded governed identity provenance.
- Tier S seeds only its directly matched record and forces `canonical_object_id = null`.
- Tier D unique is additive and nonauthoritative.
- Tier D ambiguous retains every governed Tier-D candidate seed without collapse.
- UNRESOLVED contributes no seed and performs no negative filtering.
- Corrective terms can contribute an advisory candidate but receive no identity authority and cannot initiate relation/workflow traversal.
- SAME_AS evidence does not choose the D3 tier and SAME_AS relations are excluded from traversal.
- RESOLVED_MULTIPLE is inactive.
- Whole-question fallback is detected and excluded.

Relations and graph proximity never confer canonical identity. Source-native candidates reached from a Tier-S seed remain noncanonical.

## 7. D1 traversal semantics

The policy is generic, deterministic, and shared by every query. It includes retrieval-addressable seeds, traverses accepted non-SAME_AS relation neighbors, and includes participants of already curated workflow steps. Relation predicates, endpoints, edge IDs, and traversal direction remain explicit in provenance. Pending/rejected relations are ignored. Candidate identity and deterministic frontier deduplication terminate cycles. Relation traversal is capped at `min(2, existing max_relation_hops)`.

No D1 objects, relations, workflows, or aliases were added or modified.

## 8. Candidate contribution

Structured candidates are prefixed into the existing graph stream through `merge_exact_streams`; ordinary graph candidates remain as fallback entries within the unchanged per-channel limit. Exact, dense, sparse, paper, workflow, and ordinary graph retrieval continue to run. No ordinary candidate is filtered because of a D2 result. Existing graph fusion weight, reranking, selection, and global limits are unchanged.

## 9. Provenance and diagnostics

Each structured candidate records query-grounded mention/support, resolution status, evidence tier, authority class, matched and permitted canonical IDs, seed ID, full relation path with original predicates, workflow step, candidate source/version/locator, identity authority, and inclusion reason.

Receipts expose legacy/selected shortcut hits; structured resolution attempts, status counts, hits, seeds, relation/workflow traversals, and injections; plus the mandatory safety counters. The implementation fixes these prohibited-use counters at zero:

- `migration_specific_direct_answer_location_injection_count`
- `prohibited_fallback_use_count`
- `evaluation_metadata_runtime_use_count`
- `selected_legacy_payload_reuse_count`
- `same_as_activation_count`

These are engineering diagnostics, not scientific D3 outcome metrics.

## 10. Runtime/evaluation metadata isolation

Runtime accepts only the ordinary question, normal plan/context, and `D3ExperimentConfig`. It does not load an evaluation artifact. Its API has no `case_id`, `question_id`, `bound_rule_id`, comparison role, expected status, or expected-evidence parameter. Python rejects evaluation-only fields if a wrapper attempts to forward them.

## 11. Default-production compatibility

No D3 config follows the pre-existing query-expansion and retrieval path and adds no D3 receipt. Explicit LEGACY preserves the same expansion semantics while adding arm provenance. ABLATION and STRUCTURED are reachable only through an explicit config. The production D2 role remains SHADOW and the structured prototype is not production-authoritative.

## 12. T0 verification

- New D3 T0 suite: 8 tests passed. It covers the real 54-rule inventory and exact seven-rule suppression, selected-payload non-access, default compatibility, explicit activation, plan/config consistency, runtime isolation, Tier G/S/D behavior, ambiguity, unresolved/corrective/fallback handling, accepted-edge and workflow traversal, SAME_AS exclusion, cycles, deduplication, bounded depth, provenance, and required zero counters.
- Focused existing retrieval regression: 5 directly relevant tests passed.
- Python compile/import check: passed.
- Static anti-shortcut audit and `git diff --check`: passed.
- No tiny smoke was needed because T0 tests already cover serializable three-arm plumbing with synthetic data.

One broader `test_retrieval.py` observation produced 33 passes and the already documented stale sparse-query stub failure (`analysis_diagnostics` absent on its `SimpleNamespace`). It is unrelated to D3 and was not changed. Ruff was unavailable in the existing environment and no dependency was installed.

No external model, analyzer, embedding, reranker, QA, verifier, or judge call occurred. No PostgreSQL/Qdrant write, reindex, or migration occurred.

## 13. Known structured coverage gaps

- `lmd_fit_data_chain`: D1 covers reconstruction output to LuminosityFit reader, not the whole create/run/extraction chain.
- `model_factory_theory`: D1 covers concept to model subsystem, not rule-specific factory composition or paper-page hints.
- `effective_acceptance_pipeline`: D1 covers concept/pipeline structure, not every legacy file/page payload.
- `root_macro_usage`: D1 covers operational-document to generic-workflow provenance, not direct macro-page/locator replacement.

These gaps were not filled from legacy payloads. `lmd_fit_data_chain` and `pid_two_pass_files` receive no special implementation branch because their partial identifiability is an A2 interpretation boundary.

## 14. Outcome-exposure statement

`D3_OUTCOME_EXPOSURE = NOT_STARTED`. Formal LEGACY / ABLATION / STRUCTURED runs are 0 / 0 / 0. Frozen comparison cases, new Gold D3 cases, and new novel_dev D3 cases run are all zero. No arm metric, legacy dependency, structured recovery, structured parity, per-rule decision, or overall experiment verdict was computed. `FORMAL_D3_EXPERIMENT_VERDICT = NOT_RUN`.

`novel_validation` remains UNSEEN. `novel_holdout` remains SEALED_UNSEEN.

## 15. Implementation freeze

`D3_A1_IMPLEMENTATION_FROZEN = true`.

The normal Git commit containing this implementation is the immutable D3-A1 identity. Its final SHA is intentionally not self-recorded here; D3-A2 must record it in the run manifest before any formal outcome exposure.

## 16. Next stage

The exact next stage is **D3-A2 — Frozen Three-Arm Comparison & Migration Decision**. It is NOT_STARTED and was not executed here.
