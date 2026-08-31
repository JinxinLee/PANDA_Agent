# D3-A2 Frozen Three-Arm Comparison & Migration Decision

> **D3-A2-R2 repair note (post-outcome reachability/attribution consistency repair; no scientific rerun).** R2 removes the residual blanket no-linkage wording, keeps every metric and migration decision unchanged, and separates g036's existing governed provenance from its two sequential limitations: the provenance-bearing `first_pass_poca` structure is not reachable from the D2-resolved `event_poca` seed under the frozen one-hop traversal, and A1 would not materialize relation-level provenance into retrievable source candidates even if reached. g021 remains the genuinely missing governed-evidence-link case. The separately authorized next stage is now **Structured Evidence-Link Reachability & Bridging Design**; no part of that design is implemented here.

## 1. Executive decision

> **D3-A2-R1 repair note (post-outcome attribution/provenance repair; scientific run not repeated; all original metrics and per-rule decisions unchanged).** R1 corrects three reporting/provenance defects in the original A2 artifact (`c6be168`): (1) the failure-taxonomy layer now uses only the frozen D3-A0-R1 taxonomy — `STRUCTURED_PARITY` and the `LEGACY_SHORTCUT_*` labels were descriptive outcomes, not failure classes, and now live in a separate paired-outcome layer; (2) the g036/g021 evidence-link mechanism was refined with audited diagnostic subtypes (`EXISTING_PROVENANCE_NOT_MATERIALIZED` for g036, `MISSING_GOVERNED_EVIDENCE_LINK` for g021) — the original blanket D1 no-linkage claim was overstated; (3) the runtime D1 knowledge state used by A2 was audited against the repository seed state (deployed 22 curated objects / 16 accepted relations / 0 curated workflow steps versus seed 24 / 16 / 1, with 4 relation-identity differences in each direction) and every missing item was proven outcome-neutral under the frozen A1 candidate-generation semantics. **`FORMAL_D3_EXPERIMENT_VERDICT` remains `PASS` with an explicit provenance limitation.** See section 14 for the full repair record; sections 2–13 below preserve the original A2 interpretation history with the repaired mechanism wording in sections 9.1/9.2.



- **Overall experiment verdict: `PASS`** — the frozen comparison ran exactly once, completely, and validly; every required paired cell is attributable; no prohibited safety counter fired. `PASS` does **not** mean the structured replacement is ready: **0 of the 5 directly identifiable rules earn `MIGRATION_SUPPORTED` today.**
- Three directly identifiable rules (`model_factory_theory`, `effective_acceptance_pipeline`, `root_macro_usage`) show **no meaningful legacy dependency**: their shortcuts were not materially responsible for useful retrieval.
- Two directly identifiable rules (`event_poca_handoff`, `restgas_profile_workflow`) show a **real, material legacy dependency that the generic structured path failed to reproduce** (`STRUCTURED_REGRESSION`), but for different evidence-link reasons: **g036** already has governed `ana_dpm.C` provenance in the repository seed, yet its provenance-bearing first-pass structure is not reachable from `event_poca` under the frozen one-hop path and A1 would not materialize relation-level provenance even if reached; **g021** has no governed provenance for its required answer-bearing files.
- No unsafe retrieval regression, no control leakage, no prohibited shortcut encoding, no D2-boundary violation was observed anywhere.
- Production is unchanged. Recommended next stage (evidence-driven, separately authorized): **Structured Evidence-Link Reachability & Bridging Design** — design the governed structural reachability, evidence-provenance materialization, and genuine evidence-link coverage mechanisms before any focused re-comparison.

## 2. Frozen experiment identity

- Frozen D3-A1 implementation commit: `814a6183f8054e95f65452fc2a5ac4300a6082f5` (`D3-A1 implement structured shortcut replacement prototype`); git HEAD during the run was identical; `git diff 814a618... -- src/panda_agent/retrieval.py src/panda_agent/d3_structured.py` was empty before and after the run.
- Preregistration: `evaluation/d3_a0_shortcut_migration_preregistration.json` (R1-repaired, sha256 `b4adfbdc21c0fd959a26b96aad84fda5509329c96ad6083440594224a6dd7ca2`).
- Selected rules (7, frozen): `lmd_fit_data_chain`, `event_poca_handoff`, `pid_two_pass_files`, `model_factory_theory`, `effective_acceptance_pipeline`, `restgas_profile_workflow`, `root_macro_usage`.
- Comparison manifest: D3-A0-R1, 16 English development cases (10 Gold v2.6 dev + 6 `novel_dev`), no additions/removals/substitutions.
- Execution: runner `evaluation/scripts/d3_a2_runner.py`, run id `d3_a2_frozen_20260831`, raw records `data/evaluation/runs/d3_a2_frozen_20260831/records.jsonl`, started `2026-08-30T23:34:42Z`, finished `2026-08-30T23:48:09Z`.
- Machine-readable results: `evaluation/d3_a2_three_arm_results.json`.

## 3. Execution validity

- Fixed order LEGACY → ABLATION → STRUCTURED, frozen manifest order inside each arm; 16 × 3 = 48 executions; 48/48 valid; 0 infrastructure failures; 0 retries; 0 scientific reruns.
- Outcome exposure: `D3_OUTCOME_EXPOSURE = STARTED` immediately before the first formal case and `COMPLETE` after the last; no runtime code, config, case, metric, taxonomy, or decision-rule change occurred after exposure.
- Retrieval-only: QA cases 0; verifier calls 0; judge calls 0. Calls actually made by the frozen retrieval path: 48 analyzer generation calls + 48 reranker generation calls (96 `generation_calls`, `model_calls` 144 including 48 embedding calls), ~925,870 tokens; no new model class or prompt.
- Storage: 0 PostgreSQL writes, 0 Qdrant writes, no reindex/index migration. `novel_validation` untouched; holdout sealed.

## 4. Three-arm aggregate results

Evaluator-native metrics over the 13 answered cases (the 3 `insufficient_evidence` controls are excluded from ordinary metrics and retained for safety/control analysis). Group-pooled final-evidence counts shown for count-level interpretation.

| Metric | LEGACY | ABLATION | STRUCTURED |
|---|---|---|---|
| Recall@5 | 0.769 | 0.615 | 0.615 |
| Recall@10 | 0.821 | 0.667 | 0.667 |
| Recall@20 | 0.821 | 0.667 | 0.667 |
| MRR | 0.705 | 0.641 | 0.641 |
| Combined candidate recall | 0.897 | 0.744 | 0.744 |
| Final evidence recall (case mean) | 0.821 | 0.667 | 0.667 |
| Final evidence recall (group-pooled) | 19/24 = 0.792 | 16/24 = 0.667 | 16/24 = 0.667 |
| Critical evidence recall (case mean) | 0.821 | 0.667 | 0.667 |

## 5. Paired metric deltas

Means over the 13 applicable cases; higher is better for every metric. (L−A = legacy dependency; S−A = structured contribution over ablation; S−L = structured parity.)

| Metric | L−A | S−A | S−L |
|---|---|---|---|
| Recall@5 | +0.154 | 0.000 | −0.154 |
| Recall@10 | +0.154 | 0.000 | −0.154 |
| Recall@20 | +0.154 | 0.000 | −0.154 |
| MRR | +0.064 | 0.000 | −0.064 |
| Combined candidate recall | +0.153 | 0.000 | −0.153 |
| Final evidence recall | +0.154 | 0.000 | −0.154 |

Per-case final-evidence-recall deltas are nonzero in exactly two cases (`g021`, `g036`): L−A = +1.0, S−A = 0.0, S−L = −1.0 in both; every other case is 0.0 on all three contrasts.

Preregistered primary metrics (numerator/denominator explicit):

| Metric | Value | Cases |
|---|---|---|
| `useful_retrieval_reproduction_rate` | 11/13 = 0.846 | recovered in all arms except g021, g036 |
| `selected_rule_dependency_rate` | 2/13 = 0.154 | g021, g036 |
| `structured_recovery_rate` | 0/2 = 0.000 | none recovered |
| `regression_rate` | 2/13 = 0.154 | g021, g036 |

## 6. Case-level comparison

| Case | Rule | Role | LEGACY | ABLATION | STRUCTURED | Selected shortcut fired (L)? | Structured attempted / injected | Interpretation |
|---|---|---|---|---|---|---|---|---|
| g029 | lmd_fit_data_chain | paraphrase | 1.0 | 1.0 | 1.0 | no | yes / 0 seeds (AMBIGUOUS retained) | parity |
| n021 | lmd_fit_data_chain | paraphrase | 0.5 | 0.5 | 0.5 | no | yes / 1 neutral seed | parity; preregistered LuminosityFit-side gap |
| g025 | lmd_fit_data_chain | neg. control | n/a | n/a | n/a | no | yes / 0 (abstain) | control safe |
| g036 | event_poca_handoff | direct literal | 1.0 | 0.0 | 0.0 | **yes** | yes / 4 curated candidates | legacy dependency; **structured recovery failed** |
| n022 | event_poca_handoff | paraphrase | 0.667 | 0.667 | 0.667 | no | yes / 0 seeds | parity (e3 selection variance, metric-neutral) |
| g020 | pid_two_pass_files | paraphrase | 1.0 | 1.0 | 1.0 | no | yes / 0 seeds | parity |
| n006 | pid_two_pass_files | nontrigger control | 0.5 | 0.5 | 0.5 | no | yes / 1 neutral seed | parity |
| g041 | pid_two_pass_files | neg. control | n/a | n/a | n/a | no | yes / 0 (abstain) | control safe |
| n014 | model_factory_theory | direct literal | 0.5 | 0.5 | 0.5 | yes | yes / 1 seed | shortcut not material; pre-existing e1 gap |
| g060 | model_factory_theory | paraphrase | 1.0 | 1.0 | 1.0 | no | yes / 0 seeds | parity |
| g052 | effective_acceptance_pipeline | direct literal | 1.0 | 1.0 | 1.0 | yes (2 selected rules) | yes / 0 seeds | shortcut not material |
| g055 | effective_acceptance_pipeline | distinction control | 1.0 | 1.0 | 1.0 | no | yes / 0 (abstain) | control safe; no ambiguity collapse |
| n003 | effective_acceptance_pipeline | nontrigger control | 0.5 | 0.5 | 0.5 | no | yes / 1 neutral seed | parity |
| g021 | restgas_profile_workflow | direct literal | 1.0 | 0.0 | 0.0 | **yes** | yes / 2 curated candidates | legacy dependency; **structured recovery failed** |
| n004 | root_macro_usage | direct literal | 1.0 | 1.0 | 1.0 | yes | yes / 1 neutral seed | shortcut not material |
| g007 | root_macro_usage | neg. control | n/a | n/a | n/a | no | yes / 1 neutral seed | control safe |

Top-k (Recall@10) status matches the final-evidence pattern in every applicable case (no candidate entered any channel in the two failures; no rank-out case occurred).

## 7. Per-rule migration decisions

Directly identifiable rules (the primary migration denominator is Y = 5):

| Rule | Direct case | Legacy dependency | Structured recovery | Safety | Decision |
|---|---|---|---|---|---|
| `event_poca_handoff` | g036 | **confirmed** (1.0 → 0.0) | failed (0.0) | clean | **STRUCTURED_REGRESSION** |
| `restgas_profile_workflow` | g021 | **confirmed** (1.0 → 0.0) | failed (0.0) | clean | **STRUCTURED_REGRESSION** |
| `model_factory_theory` | n014 | not material (0.5 → 0.5) | n/a (0.5) | clean | **NO_MEANINGFUL_LEGACY_DEPENDENCY** |
| `effective_acceptance_pipeline` | g052 | not material (1.0 → 1.0) | n/a (1.0) | clean | **NO_MEANINGFUL_LEGACY_DEPENDENCY** |
| `root_macro_usage` | n004 | not material (1.0 → 1.0) | n/a (1.0) | clean | **NO_MEANINGFUL_LEGACY_DEPENDENCY** |

Decision counts: `MIGRATION_SUPPORTED` 0 · `PARTIALLY_REPRODUCED` 0 · `STRUCTURED_REGRESSION` 2 · `NO_MEANINGFUL_LEGACY_DEPENDENCY` 3 · `INSUFFICIENT_EVIDENCE` 2. **0/5 directly identifiable rules support migration.**

## 8. Generalization-only rules (reported separately)

| Rule | Paraphrase behavior | Controls | Structured contribution | Decision |
|---|---|---|---|---|
| `lmd_fit_data_chain` | g029 1.0, n021 0.5 in all arms | g025 stable | correct abstention on AMBIGUOUS `PndLmdCombinedDataReader`; no collapse | **INSUFFICIENT_EVIDENCE** (frozen guard) |
| `pid_two_pass_files` | g020 1.0 in all arms | n006, g041 stable | correct abstention on unresolved "two-pass" mention | **INSUFFICIENT_EVIDENCE** (frozen guard) |

These two rules have no direct-trigger case, so no dependency contrast exists; they are excluded from the directly identifiable success rate and are not promoted to any stronger label from generalization-only evidence.

## 9. Structured mechanism diagnosis

*(Section 9.1/9.2 wording below is the R1/R2-repaired, evidence-audited attribution; the original A2 blanket D1 no-linkage wording was directionally correct for the executed runtime state but overstated repository-level coverage and is superseded here.)*

For both structured failures the retrieval-funnel attribution is identical at the top:

1. **D2 resolution worked**: `event_poca` resolved Tier-S to `data_product.restgas.event_poca` (g036); `restgas_profile` resolved Tier-S to `configuration.restgas_profile` (g021). This is **not a D2 failure**.
2. **D1 relation traversal worked**: accepted non-SAME_AS edges were traversed (g036: boost_root, pid_root, second_pass_pid; g021: workflow.restgas_profile_reconstruction).
3. **Structured candidates were recalled and ranked very high**: g036 fused ranks 1–2; g021 fused ranks 1 and 3. This is **not** `STRUCTURED_CANDIDATE_RECALLED_BUT_RANKED_OUT` and not a fusion/ranking failure.
4. **The binding failure is the governed-structure → retrievable-evidence boundary, with two distinct causes**: g036 has governed `ana_dpm.C` provenance in the repository seed but the frozen path cannot reach and materialize it; g021 has no governed provenance for its required files. In both cases the answer-bearing corpus files entered the candidate pool only through the LEGACY exact channel via the rules' path/symbol payloads.

### 9.1 g036 — diagnostic subtype `EXISTING_PROVENANCE_NOT_MATERIALIZED` (R2 refinement)

- g036 requires evidence at `macro/target/ana_dpm.C` (source `restgas_determination`, object_type function/source_file).
- **The repository governed seed D1 already carries `macro/target/ana_dpm.C` as relation-level evidence provenance** on two accepted relations: `workflow.restgas.first_pass_poca CONSUMES data_product.restgas.pid_root` (`edge.5a8a1deba5f20c052cdcb044`) and `workflow.restgas.first_pass_poca PRODUCES data_product.restgas.boost_root` (`edge.2e09628416a01ce2461d752a`), both with `evidence_paths: [macro/target/ana_dpm.C]`.
- **The provenance-bearing structure is not reachable from the resolved seed under the frozen path**: `data_product.restgas.event_poca` is the D2-resolved seed, `configs/retrieval_policies.yaml` fixes `max_relation_hops: 1`, and `Retriever` passes `min(2, policy) = 1`; the seed's reached relation is `event_poca PRODUCES_INPUT_FOR second_pass_pid`, not either `first_pass_poca` provenance edge.
- **The frozen A1 structured path does not consume that provenance**: `d3_structured.py` contains no reference to `evidence_paths`/`evidence_object_ids`/`evidence_source_ids`; `load_accepted_relations()` reads `payload` into its edge receipt, but the traversal uses only subject/object endpoints, relation-path provenance records only edge/predicate/endpoints/direction, and only governed endpoint objects are materialized as candidates. Relation-level evidence provenance is therefore read but neither preserved in structured candidate provenance nor materialized into retrievable source candidates.
- Additionally (runtime-state layer): the deployed materialization contains **neither** of those provenance-bearing edges (they are seed-only, see section 14), and none of its 16 materialized relation payloads carries any evidence provenance at all (`evidence_object_ids` empty on every curated-touching edge).
- Consequently: **g036 needs both generic reachability and materialization.** The governed evidence provenance already exists at the repository level, but the frozen structured path cannot reach the provenance-bearing first-pass structure from `event_poca` under the actual one-hop policy; even if reached, A1 would not materialize relation-level evidence provenance into retrievable source evidence. Neither step alone is sufficient, and the deployed runtime state has not materialized the provenance-bearing edges at all.

### 9.2 g021 — diagnostic subtype `MISSING_GOVERNED_EVIDENCE_LINK` (R2 preserved)

- g021 requires evidence at `macro/target/prod_sim_hvmaps.C` (e1) and `pgenerators/Target/PndTargetGenerator.cxx` (e2), source `restgas_determination`.
- **Neither path appears anywhere in governed D1 structure**: not in seed objects, not in any seed relation/workflow evidence provenance, not in the deployed runtime (whose relation payloads carry no evidence provenance). The only governed provenance near g021's topology points to `README.md`/`macro/target/README.md` (configuration.restgas_profile PARAMETERIZES workflow.restgas_profile_reconstruction).
- `prod_sim_hvmaps.C` exists only in the legacy `restgas_profile_workflow` rule payload — exactly the shortcut whose removal defines this comparison — so this is a genuinely missing governed evidence link, not an A1 materialization failure of existing provenance.

Primary failure taxonomy counts (per case, 16 cases, R1/R2-repaired): `EVIDENCE_LINK_COVERAGE_GAP` 2 (g021, g036); all other 14 cases carry `failure_classification = null`. Paired-outcome layer: `STRUCTURED_PARITY` 14, `STRUCTURED_REGRESSION` 2. Dependency interpretation: `LEGACY_DEPENDENCY_CONFIRMED` on g021/g036; `NOT_MATERIALLY_USED` on n014/g052/n004; no `UNCLASSIFIED` was needed. (The original A2 artifact counted `STRUCTURED_PARITY: 14` inside `failure_taxonomy_counts`; that was a non-frozen label in the failure layer and is corrected by R1.)

## 10. Known D1 vs D2 limitations

- Consistent with the preregistered boundary, the D1 accepted graph exposes curated object-to-object structure and, for g036 in the repository seed, relation-level `ana_dpm.C` provenance. The observed failures remain **D1 evidence-linkage boundary failures, not D2 resolution gaps**: g036 cannot reach and materialize existing provenance under the frozen path, while g021 lacks governed provenance altogether (per the frozen attribution rule, D2 is not blamed).
- The preregistered preserved gap for `lmd_fit_data_chain` (createLmdFitData/runLmdFit/extraction orchestration) remains visible as n021's e2 miss in all arms.
- n014's `model_framework`-definition group miss is a pre-existing recall gap present in all three arms, unrelated to the selected rule.

## 11. Control/safety analysis

- All five prohibited-use counters were mechanically zero in every STRUCTURED execution: direct answer-location injection 0, prohibited fallback 0, evaluation-metadata runtime use 0, selected legacy payload reuse 0, SAME_AS activation 0. No experiment-validity blocker fired.
- Negative/nontrigger/distinction controls (g025, g041, g007, g055, n003, n006): no irrelevant entity injection causing leakage, no over-expansion, no unsupported evidence entering final selection, no incorrect ambiguity narrowing (AMBIGUOUS mentions stayed ambiguous, e.g. `runLmdFit`, `PndLmdCombinedDataReader`), no insufficient-evidence case turned into false confidence, no negative filtering from UNRESOLVED.
- Neutral injections: a generic Tier-S "PandaRoot" repository seed was injected in g007/n003/n006/n021/n004; all were metric-neutral.
- Run variance note: arms are independent frozen-path executions; temperature-0 LLM nondeterminism produced one metric-neutral selection difference (n022 e3, both objects selector-matched) and small concept-list differences. ABLATION vs STRUCTURED rule state was identical by construction.

## 12. Production implications

- No production change: `configs/query_expansions.yaml` untouched (all 54 rules remain active), structured D3 not activated, production D2 role remains `SHADOW`, no routing change, no runtime file changed during A2 (verified post-run).
- No shortcut may be removed based on this experiment alone; even the three `NO_MEANINGFUL_LEGACY_DEPENDENCY` rules require a separately authorized cleanup stage.
- The experiment does not support "structured works, therefore remove all 54 shortcuts"; D3 is deliberately small.

## 13. Lifecycle and next step

- `D3-A2 = COMPLETE / FROZEN_THREE_ARM_COMPARISON_COMPLETE`; `D3-A2-R1 = COMPLETE / OUTCOME_ATTRIBUTION_AND_RUNTIME_STATE_REPAIRED`; `D3-A2-R2 = COMPLETE / EVIDENCE_LINK_REACHABILITY_AND_ATTRIBUTION_CONSISTENCY_REPAIRED`; `D3_OUTCOME_EXPOSURE = COMPLETE`; `FORMAL_D3_EXPERIMENT_VERDICT = PASS` (with the R1 runtime provenance limitation and R2 wording refinement); `D3 = COMPLETE / SHORTCUT_MIGRATION_EXPERIMENT_DECIDED`. Production unchanged.
- Exact recommended next task (not executed here; refined by R2): **Structured Evidence-Link Reachability & Bridging Design** — a separately authorized bounded design stage with three mechanisms:
  - **(A) Governed structural reachability:** design how a D2-resolved object may use existing `parent_object_id`, accepted relation direction, workflow-step participation, or bounded composition to reach provenance-bearing governed structure. A possible g036 hypothesis is `event_poca → parent_object_id → boost_root → accepted relation/workflow structure → first_pass_poca → governed evidence provenance → ana_dpm.C`; this is a hypothesis only, not an implementation or traversal-order decision.
  - **(B) Evidence provenance materialization:** once an accepted relation/workflow is reached, design conversion of its existing governed evidence provenance into a retrieval-addressable source-native evidence candidate; this is not sufficient for g036 without mechanism A.
  - **(C) Genuine evidence-link coverage:** where governed provenance truly does not exist, add narrowly justified governed evidence linkage (the g021-type case for `prod_sim_hvmaps.C` and `PndTargetGenerator.cxx`).
  - then, only after that design is separately authorized and implemented, a focused re-comparison of the two `STRUCTURED_REGRESSION` rules.
- The replacement shape must preserve `question → D2 resolved governed object → generic governed structural reachability → accepted governed relation/workflow → governed evidence provenance → retrievable source-native evidence candidate` and prohibit `trigger phrase → hardcoded file`, `selected rule ID → evidence_path`, `case ID → answer file`, `bound_rule_id → graph route`, and `question ID → relation path`. R2 does not decide `max_relation_hops`, parent-first order, or any concrete bridge algorithm.

## 14. D3-A2-R1 Attribution and Runtime-State Repair (2026-08-31)

**Scope:** post-outcome interpretation/provenance repair only. The scientific run was **not** repeated (0 new retrieval runs, 0 analyzer/embedding/reranker calls); all 48 arm-case result cells, every aggregate metric, every preregistered primary metric, and all seven per-rule decisions are mechanically verified unchanged against the original artifact at `c6be168`. Runtime files, `configs/query_expansions.yaml`, and all D1 seed configs are untouched. Original A2 interpretation history is preserved above; only the mechanism wording (sections 9.1/9.2) and the accounting layers were corrected.

### 14.1 Taxonomy repair

The frozen D3-A0-R1 failure taxonomy (13 values, from `evaluation/d3_a0_shortcut_migration_preregistration.json`) is now used exclusively in the failure layer: `STRUCTURED_CANDIDATE_RECALL_FAILURE`, `RELATION_COVERAGE_GAP`, `WORKFLOW_COVERAGE_GAP`, `EVIDENCE_LINK_COVERAGE_GAP`, `ENTITY_OR_TERMINOLOGY_RESOLUTION_FAILURE`, `AMBIGUITY_OR_ABSTENTION`, `REPOSITORY_OR_VERSION_SCOPE_FAILURE`, `FUSION_OR_RANKING_FAILURE`, `FINAL_SELECTOR_FAILURE`, `LEGACY_DEPENDENCY_WITHOUT_STRUCTURED_RECOVERY`, `CONTROL_LEAKAGE_OR_OVERMATCH`, `PROHIBITED_SHORTCUT_ENCODING`, `INFRASTRUCTURE_OR_ARTIFACT_FAILURE`.

The original A2 artifact placed `STRUCTURED_PARITY` (14 cases) inside `failure_classification`/`failure_taxonomy_counts`; those are descriptive outcomes, not frozen taxonomy values. Repaired case layer: `g036`/`g021` carry `failure_classification = EVIDENCE_LINK_COVERAGE_GAP` with `secondary_failure_classifications = [LEGACY_DEPENDENCY_WITHOUT_STRUCTURED_RECOVERY]`; the other 14 cases carry `failure_classification = null` with `paired_outcome = STRUCTURED_PARITY`. Repaired counts: failure taxonomy `EVIDENCE_LINK_COVERAGE_GAP` 2; paired outcomes `STRUCTURED_PARITY` 14 / `STRUCTURED_REGRESSION` 2. The preregistered arm-case outcome vocabulary is anchored as `REGRESSION` (g036, g021), `FULL_REPRODUCTION` (11 answered reproduced cases), `NOT_APPLICABLE` (3 controls).

### 14.2 Runtime D1 knowledge-state audit

| Item | Repository expected (seed configs @ 814a618) | A2 runtime materialized | Missing / unexpected |
|---|---|---|---|
| Curated objects | 24 (list in JSON artifact) | 22 | missing: `workflow.restgas.first_pass_poca`, `concept.luminosityfit.luminosity_fit_model`; unexpected: none |
| Accepted curated-touching relations | 16 | 16 (identities differ) | missing: 4 seed edges (`pflueger FORMALIZES concept` `edge.161980db…`; `model_and_fit IMPLEMENTS concept` `edge.4b871167…`; `first_pass_poca CONSUMES pid_root` `edge.5a8a1deb…`; `first_pass_poca PRODUCES boost_root` `edge.2e096284…`); unexpected: 4 D1-A1-era stand-in edges (`boost_root PRODUCES event_poca` `edge.8e335685…`; `pid_root PRODUCES_INPUT_FOR event_poca` `edge.f7d60136…`; `restgas_profile_reconstruction PRODUCES boost_root` `edge.878ae270…`; `pflueger FORMALIZES model_and_fit` `edge.2f95e61f…`) |
| Curated workflow steps | 1 (`workflow.restgas.first_pass_poca` under `workflow.restgas_profile_reconstruction`) | 0 (374 corpus steps, none curated) | missing: the one seed step; unexpected: none |
| Relation payload evidence provenance | seed relations carry `evidence_paths`/`evidence_object_ids` (incl. `ana_dpm.C`) | none: all 16 materialized payloads have `evidence_paths` absent and `evidence_object_ids` empty | — |

**Root cause (inspectable, not speculative):** the last completed ingestion (normalized corpus `9925ec31a612`, report 2026-08-16) predates the D1-A2 seed additions (commit `24e4e4b`, 2026-08-29) and the D1-A2R1 concept correction (`2fc947f`). No re-ingestion was authorized or performed afterward — correctly so, since D1-A3R1 recorded `FUTURE_REINGESTED_STRUCTURED_KNOWLEDGE_STATE_CHANGED = true` and D3 prohibits reindex/ingestion. The loader and DB write paths (seed workflow materialization with `metadata.curated_seed=true`, `upsert_workflows`, `upsert_relations`) were verified capable of handling the seed additions; the deployed DB simply predates them.

### 14.3 Materiality assessment (per missing item, evidence-backed)

- **`workflow.restgas.first_pass_poca` (object or workflow-step participant):** relevant only to g036/g021. As a candidate it would be a curated workflow object (source `curated_panda_domain`, object_type `workflow`) that can never satisfy the g036/g021 required selectors (source `restgas_determination`, specific corpus paths, object_type function/source_file). Its injection would change only engineering diagnostic counts, not group outcomes.
- **`concept.luminosityfit.luminosity_fit_model`:** relevant to n014/g060, whose decisions rest on arm equality (`LEGACY == ABLATION == STRUCTURED`). The concept was never a D2 match target in the run and its candidate object cannot match the n014 selectors.
- **4 seed-only relations (incl. the two `ana_dpm.C`-provenance edges):** the frozen hop budget is `max_relation_hops = 1`; `event_poca`'s only seed edge is `PRODUCES_INPUT_FOR second_pass_pid`, so the provenance-bearing edges would not have been traversed from the D2-resolved seed even under the intended seed state — and under A1 semantics relation payloads are never converted into candidates regardless.
- **4 runtime-only stand-in relations:** they made `boost_root`/`pid_root` reachable in g036; the injected curated objects ranked highly but matched no required selector.

**Conclusion:** no missing or drifted item could have changed any of the 48 frozen scientific outcomes or any per-rule decision under the frozen A1 candidate-generation semantics. The experiment did evaluate the preregistered frozen A1 structured capability; it evaluated it against the deployed 2026-08-16 materialization rather than the current D1-A2 seed state, which is recorded as a provenance limitation. **`FORMAL_D3_EXPERIMENT_VERDICT = PASS` is preserved.**

### 14.4 D3-A2-R2 Reachability and Attribution Consistency Repair (2026-08-31)

**Scope:** post-outcome wording and diagnostic-schema precision only. No retrieval, model, API, database, re-ingestion, or scientific rerun occurred; all 48 arm-case cells, metrics, seven decisions, taxonomy counts, and the R1 runtime-state conclusion remain unchanged.

- **g036:** `governed_provenance_exists = true`; the accepted seed relations `workflow.restgas.first_pass_poca CONSUMES data_product.restgas.pid_root` and `workflow.restgas.first_pass_poca PRODUCES data_product.restgas.boost_root` both carry `macro/target/ana_dpm.C`. `provenance_reachable_from_resolved_seed = false` with `reachability_status = NOT_REACHABLE_UNDER_FROZEN_TRAVERSAL` because the actual policy path is one hop from `data_product.restgas.event_poca`; `provenance_materialization_supported = false` with `materialization_status = NOT_SUPPORTED` because A1 materializes endpoint objects, not relation-level evidence provenance. Both reachability and materialization are required for recovery.
- **g021:** `governed_provenance_exists = false`; `macro/target/prod_sim_hvmaps.C` and `pgenerators/Target/PndTargetGenerator.cxx` remain absent from inspectable governed D1 evidence provenance, so the subtype remains `MISSING_GOVERNED_EVIDENCE_LINK`.
- The exact next task is **Structured Evidence-Link Reachability & Bridging Design**, with mechanism A (governed structural reachability), B (existing evidence-provenance materialization), and C (genuine evidence-link coverage). The design is not executed here and does not choose a hop count, traversal order, or implementation. Trigger/rule/case/question-to-file or graph-route encodings remain prohibited.
- Static checks after the repair: JSON parse, builder/artifact consistency, scientific-value invariance, stale-rationale search, next-stage-name consistency, runtime/D1/D2/query-expansion diff checks, and `git diff --check`; no full suite or formal evaluation was run.
