# D3-A2 Frozen Three-Arm Comparison & Migration Decision

## 1. Executive decision

- **Overall experiment verdict: `PASS`** — the frozen comparison ran exactly once, completely, and validly; every required paired cell is attributable; no prohibited safety counter fired. `PASS` does **not** mean the structured replacement is ready: **0 of the 5 directly identifiable rules earn `MIGRATION_SUPPORTED` today.**
- Three directly identifiable rules (`model_factory_theory`, `effective_acceptance_pipeline`, `root_macro_usage`) show **no meaningful legacy dependency**: their shortcuts were not materially responsible for useful retrieval.
- Two directly identifiable rules (`event_poca_handoff`, `restgas_profile_workflow`) show a **real, material legacy dependency that the generic structured path failed to reproduce** (`STRUCTURED_REGRESSION`): the shortcuts' useful behavior is exact-channel injection of answer-location file paths/symbols, and the accepted D1 graph has no evidence linkage from the correctly resolved governed objects to the answer-bearing corpus files.
- No unsafe retrieval regression, no control leakage, no prohibited shortcut encoding, no D2-boundary violation was observed anywhere.
- Production is unchanged. Recommended next stage (evidence-driven, separately authorized): **structured coverage-gap repair design** — bounded D1 evidence-linkage coverage for the two regression rules, then a focused re-comparison.

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

For both structured failures the retrieval-funnel attribution is identical and unambiguous:

1. **D2 resolution worked**: `event_poca` resolved Tier-S to `data_product.restgas.event_poca` (g036); `restgas_profile` resolved Tier-S to `configuration.restgas_profile` (g021). This is **not a D2 failure**.
2. **D1 relation traversal worked**: accepted non-SAME_AS edges were traversed (g036: boost_root, pid_root, second_pass_pid; g021: workflow.restgas_profile_reconstruction).
3. **Structured candidates were recalled and ranked very high**: g036 fused ranks 1–2; g021 fused ranks 1 and 3. This is **not** `STRUCTURED_CANDIDATE_RECALLED_BUT_RANKED_OUT` and not a fusion/ranking failure.
4. **The binding failure is evidence linkage**: the answer-bearing corpus files (the producing macro for `event_poca`; the restgas_profile configuration-usage/simulation-macro files) entered the candidate pool **only** through the LEGACY exact channel via the rules' path/symbol payloads. No accepted D1 edge or curated workflow participant connects the governed objects to those retrievable files, so once the payloads are suppressed the answer evidence never enters any channel.

Primary failure taxonomy counts (per case, 16 cases): `EVIDENCE_LINK_COVERAGE_GAP` 2 (g021, g036) · `STRUCTURED_PARITY` 14. Overlay accounting: `LEGACY_SHORTCUT_DEPENDENCY_CONFIRMED` on the same two cases; `LEGACY_SHORTCUT_NOT_MATERIALLY_USED` on n014/g052/n004; no `UNCLASSIFIED` was needed.

## 10. Known D1 vs D2 limitations

- Consistent with the preregistered boundary, the D1 accepted graph covers curated object-to-object structure only; it does not connect governed objects to corpus answer locations. The observed failures are **D1 evidence-linkage coverage gaps, not D2 resolution gaps** (per the frozen attribution rule, D2 is not blamed).
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

- `D3-A2 = COMPLETE / FROZEN_THREE_ARM_COMPARISON_COMPLETE`; `D3_OUTCOME_EXPOSURE = COMPLETE`; `FORMAL_D3_EXPERIMENT_VERDICT = PASS`; `D3 = COMPLETE / SHORTCUT_MIGRATION_EXPERIMENT_DECIDED`. Production unchanged.
- Exact recommended next task (not executed here): **structured coverage-gap repair design** — a separately authorized bounded stage to design D1 evidence-linkage coverage (governed object → retrievable answer-location corpus evidence) for the two `STRUCTURED_REGRESSION` rules (`event_poca_handoff`, `restgas_profile_workflow`), followed by a focused re-comparison of only those rules. The evidence basis is the single dominant failure class `EVIDENCE_LINK_COVERAGE_GAP`; D2 resolution and D1 traversal already work and ranking is not the binding constraint.
