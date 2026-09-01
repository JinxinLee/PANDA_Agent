# D3.5-A2 — Focused Evidence-Link Recovery Validation

## 1. Executive scientific verdict

**`PARTIAL / TARGETED_RECOVERY_MIXED`.** The frozen four-arm × six-case comparison completed validly (24/24 cells, 0 errors, 0 retries, 0 reruns). The frozen D3.5 bridge is **validated as a bounded, governed, additive pool-level injection mechanism** but is **not validated as an end-to-end final-evidence recovery mechanism**: on both positive cases the bridged candidates entered the candidate pool exactly as designed yet never survived the frozen fusion/rerank/selector into final evidence. No material control regression, no scope leakage, no abstention break, and zero prohibited-use counter violations were observed. D3.5 closes as `COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED` (end-to-end), and the D4 gate remains blocked.

| Aggregate (5 applicable cases; g041 NA in all arms) | LEGACY | ABLATION | STRUCTURED_UNBRIDGED | STRUCTURED_BRIDGED |
|---|---|---|---|---|
| Recall@5 | 0.8 | 0.5 | 0.4 | 0.5 |
| Recall@10 | 0.9 | 0.5 | 0.5 | 0.5 |
| Recall@20 | 0.9 | 0.5 | 0.5 | 0.5 |
| MRR | 0.5952 | 0.3400 | 0.3286 | 0.3667 |
| Combined candidate recall | 1.0 | 0.6 | 0.6 | **0.9** |
| Final evidence recall | 0.9 | 0.5 | 0.5 | 0.5 |
| Critical final evidence recall | 0.9 | 0.5 | 0.5 | 0.5 |

Primary causal contrasts (final evidence recall / combined candidate recall):

- `LEGACY − ABLATION` = **+0.4 / +0.4** — the two focused shortcuts remain materially responsible (g036 and g021: 1.0 → 0.0 when suppressed).
- `STRUCTURED_UNBRIDGED − ABLATION` = **0.0 / 0.0** — synchronized final D1 plus the pre-D3.5 structured path recovered nothing at either level; g021's Mechanism-C knowledge did not surface through the unbridged path.
- `STRUCTURED_BRIDGED − STRUCTURED_UNBRIDGED` = **0.0 final / +0.3 combined** — no incremental final-evidence recovery, but a real, causally identifiable pool-level contribution (g036 0.0 → 1.0, g021 0.0 → 0.5).
- `STRUCTURED_BRIDGED − LEGACY` = **−0.4 / −0.1** — bridged does not reach legacy parity.

`STRUCTURED_BRIDGED − ABLATION` (+0.3 combined / 0.0 final) is reported only as the combined final-D1 + old-structured + bridge contribution, never as a pure bridge effect.

## 2. Frozen preregistration and execution identity

| Item | Value |
|---|---|
| Execution manifest | `evaluation/d3_5_a2_focused_evidence_link_recovery_manifest.json` (committed pre-outcome) |
| Pre-outcome freeze commit | `470b62f823c3e65637604da2f614461c1a81d5b6` (manifest freeze) → runner/manifest committed at `9467061` |
| Git head during run | `9467061…` (evaluation-only commit; runtime identical to `9b5a84996c30eaf1a297924b36452a90fe6d84d2`) |
| Frozen runtime anchor | `9b5a84996c30eaf1a297924b36452a90fe6d84d2` — `git diff` on `src/panda_agent/retrieval.py`, `src/panda_agent/d3_structured.py`, and `configs/` empty before and after the run |
| Preregistration | `evaluation/d3_5_a0_structured_evidence_link_design.json` (`d3_5_a2_contract`) + A1 artifacts |
| Final repository D1 | `9b5a84996c30eaf1a297924b36452a90fe6d84d2` (24 objects / 16 accepted relations / 1 workflow step / 2 aliases) |
| Materialization | Dedicated development PostgreSQL (`host=127.0.0.1, port=55432, database=panda_qa`, role `DEDICATED_DEVELOPMENT_EVALUATION_STATE`); R3 receipt re-verified read-only before the first cell: all diff lists empty, 0 stale records |
| Source/index state | source manifest `9925ec31…`; Qdrant `panda_knowledge_v1` fingerprint `8172f9a6…`, 104,973 points; 133,077 SQL objects; no rebuild/reindex/re-embedding |
| Runner | `evaluation/scripts/d3_5_a2_runner.py` (evaluation-only; passes only the ordinary question + `D3_5ExperimentConfig` into the frozen runtime) |
| Raw records | `data/evaluation/runs/d3_5_a2_focused_20260901/records.jsonl` |

## 3. First-outcome-exposure boundary

The execution manifest was committed (`D3.5-A2 freeze focused recovery execution manifest`) with `formal_outcome_exposure = false` and `created_before_outcome_exposure = true`. The first formal cell (g036 / LEGACY, sequence 1) started at `2026-09-01T17:21:49+00:00` (run manifest `started_at_utc` `2026-09-01T17:21:48Z`), which is the instant `D3_5_OUTCOME_EXPOSURE` became `STARTED`. From that instant no runtime, D1, database, query-expansion, arm, case, metric, or classification state was modified. The comparison finished at `2026-09-01T17:32:09Z` (run manifest `finished_at_utc`).

## 4. Four-arm treatment

Exactly the frozen arms were executed; every per-cell treatment receipt matches the frozen flag matrix (verified programmatically for all 24 cells):

| Arm | Focused 2 rules | Structured path | D3.5 bridge |
|---|---|---|---|
| LEGACY | active | OFF | OFF |
| ABLATION | suppressed | OFF | OFF |
| STRUCTURED_UNBRIDGED | suppressed | ON | OFF |
| STRUCTURED_BRIDGED | suppressed | ON | ON (additive) |

Suppression scope: exactly `event_poca_handoff` and `restgas_profile_workflow` in the three treatment arms; all other query-expansion rules unchanged everywhere. The historical D3 seven-rule treatment was not used.

## 5. Six-case set

Frozen per the A0 contract; no additions, substitutions, or omissions:

| Case | Role | Dataset | Groups |
|---|---|---|---|
| g036 | existing-provenance reachability + materialization (Mechanism A+B class) | Gold v2.6 dev | 1 |
| g021 | independently governed genuine-coverage path (Mechanism C class) | Gold v2.6 dev | 2 |
| n006 | nearby nontrigger control | novel_dev | 2 |
| g041 | ambiguity/abstention and negative control | Gold v2.6 dev | 1 |
| g020 | same subsystem, no governed bridge required | Gold v2.6 dev | 2 |
| n004 | ordinary retrieval already succeeds | novel_dev | 1 |

## 6. Execution completeness

24 scheduled / 24 valid / 0 infrastructure failures / 0 retries / 0 discretionary reruns, in the frozen case-major order (g036 → g021 → n006 → g041 → g020 → n004, each over LEGACY → ABLATION → STRUCTURED_UNBRIDGED → STRUCTURED_BRIDGED). Cost: 24 analyzer + 24 reranker generation calls, 24 embedding calls, 458,979 tokens; QA/verifier/judge = 0; PostgreSQL D1 writes = 0; Qdrant writes = 0; ingestion/re-ingestion = 0. `novel_validation` UNSEEN; holdout SEALED_UNSEEN.

## 7. Aggregate metrics

See the table in §1. Denominators are 5 applicable cases (g041 is the frozen insufficient-evidence control and is metric-inapplicable identically in all four arms; it is retained for safety analysis). Case-level tables below are authoritative; averages never hide heterogeneity.

## 8. Case-level results (final evidence recall; combined candidate recall)

| Case | LEGACY | ABLATION | UNBRIDGED | BRIDGED | Shortcut dep. | Final-D1/old-structured | Incremental bridge | Bridged-vs-legacy |
|---|---|---|---|---|---|---|---|---|
| g036 | 1.0 / 1.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / **1.0** | confirmed | none | pool only (0.0 final / +1.0 pool) | not parity |
| g021 | 1.0 / 1.0 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / **0.5** | confirmed | none | pool only (0.0 final / +0.5 pool) | not parity |
| n006 | 0.5 / 1.0 | 0.5 / 1.0 | 0.5 / 1.0 | 0.5 / 1.0 | none | none | none | parity |
| g041 | NA | NA | NA | NA | — | — | — | — |
| g020 | 1.0 / 1.0 | 1.0 / 1.0 | 1.0 / 1.0 | 1.0 / 1.0 | none | none | none (pool neutral) | parity |
| n004 | 1.0 / 1.0 | 1.0 / 1.0 | 1.0 / 1.0 | 1.0 / 1.0 | none | none | none | parity |

Per-case interpretations (full text in the machine artifact):

- **g036** — Legacy dependency confirmed. The preregistered A+B path was observed with receipts: `event_poca` (Tier S, RESOLVED_UNIQUE) → `boost_root` (parent) → `workflow.restgas.first_pass_poca` (accepted relation / workflow step), and the bridge materialized `macro/target/ana_dpm.C` (+ `prod_aod_complete.C`, `pid_complete.C`) from accepted relation `evidence_object_ids`. Combined candidate recall 0.0 → 1.0. The ana_dpm.C candidate entered the graph channel at prefix position 3/16 (weight 0.8), scored below the fused top-30 rerank-pool cutoff, was never reranked, and never reached final evidence. No displacement (0), no control effects.
- **g021** — Legacy dependency confirmed. The bridge reached `workflow.restgas_profile_reconstruction` from the `configuration.restgas_profile` seed via the accepted Mechanism-C `PARAMETERIZES` edge and materialized its 62 governed evidence objects; 20 fit the bridge cap (including `macro/target/prod_sim_hvmaps.C`), 42 were capped out. Combined recall 0.0 → 0.5: group e1 (prod_sim_hvmaps.C) entered the pool; group e2 (`pgenerators/Target/PndTargetGenerator.cxx`) did not — its provenance-bearing edge originates from `file_pattern.restgas_profile_input`, which was not a D2 seed in this question (resolution: RESOLVED_UNIQUE 1, UNRESOLVED 2), so that edge was never reached under the frozen one-transition budget. The injected prod_sim_hvmaps.C candidate (graph position 9/20) also fell below the fused top-30 cutoff. 4 ordinary graph candidates were displaced at the graph limit (outcome-neutral).
- **n006** — Stable (0.5 in all arms; zero bridge activity). The R@5/MRR spread across arms is the documented temperature-0 analyzer/reranker variance class (cf. D3-A2 n022 e3); final evidence and R@10/20 are identical everywhere.
- **g041** — Ambiguity/abstention control preserved identically in all arms (metric-inapplicable, no abstention break, no ambiguity collapse, zero bridge activity).
- **g020** — Outcome-neutral (1.0 in all arms) but the largest displacement: the Tier-D ambiguous `boost_root` mention was admitted atomically (set size 2, within the cap-8 rule, no truncation) and the bridge injected 20 provenance-backed candidates (including ana_dpm.C), displacing all 20 ordinary graph candidates at the graph limit. Required evidence was satisfied through other channels; no scope leakage or regression.
- **n004** — Stable (1.0 everywhere; zero bridge activity).

## 9. g036 A+B analysis

Mechanism A (bounded structural reachability) and Mechanism B (exact provenance materialization) both worked exactly as preregistered, with complete receipts: 7 reachability receipts (all `REACHED`, phased budget 0→2 consumed), 8 bridge receipts (5 `GOVERNED_PROVENANCE_NOT_FOUND` on objects without provenance — fail-closed and correct; 3 `BRIDGED_CANDIDATE_INJECTED` from two accepted relation edges, each with exact frozen version `restgas_determination@11f1edc…`). The recovery chain `valid seed → bounded reachability → governed relation provenance → exact ana_dpm.C source-native candidate` executed without any case-specific mapping. The failure is strictly downstream: pool entry did not become final-evidence entry.

## 10. g021 Mechanism-C / bridge decomposition

- **Final-D1 / unbridged contribution: 0.** Even though final D1 now contains the Mechanism-C repairs, `STRUCTURED_UNBRIDGED` stayed at 0.0: the unbridged structured path injects governed *endpoint objects* (curated, not corpus files) that cannot satisfy the required selectors.
- **Incremental bridge contribution: pool-level only (+0.5).** The bridge reached the Mechanism-C `PARAMETERIZES` edge and materialized its provenance; e1 entered the pool. This is the first observable use of the Mechanism-C governed knowledge by the structured mechanism.
- **e2 was structurally unreachable** in this question: the `PRODUCES_INPUT_FOR` edge carrying `PndTargetGenerator.cxx` originates from `file_pattern.restgas_profile_input`, which the frozen D2 resolution did not seed for this query. Under frozen semantics no traversal could reach it; this is a seed-resolution coverage boundary, recorded as a limitation, not repaired here.
- Per the frozen interpretation contract, g021 improving in BRIDGED (pool) while UNBRIDGED stayed 0 does **not** by itself prove a general incremental bridge effect beyond what §8/§31 quantify — and at the final-evidence level the incremental effect is exactly 0.

## 11. Control analysis

No unexpected candidate injection into final evidence, no scope widening, no wrong-repository provenance, no control regression, no abstention break, and no unjustified bridge activity: n006/g041/n004 had zero bridge activity; g020's bridge activity was generically governed (accepted-relation provenance), retrieval-relevant, and outcome-neutral. The g020 20/20 graph-slot displacement is bounded by the existing graph cap and is recorded as a real displacement fact, not a violation.

## 12. Structured reachability diagnostics

Across the 12 structured-arm executions: every attempted seed resolved (`RESOLVED_UNIQUE` / atomic `AMBIGUOUS` admissions only); zero `NO_ELIGIBLE_STRUCTURED_SEED`, zero `STRUCTURAL_PATH_NOT_FOUND`, zero `STRUCTURAL_PATH_AMBIGUOUS` failures, zero `TRAVERSAL_BUDGET_EXHAUSTED`; phased budgets consumed ≤ 2 transitions per path; the g020 Tier-D ambiguity set (2) was admitted atomically with no truncation. D2 authority was unchanged (diagnostic accounting only).

## 13. Evidence bridge diagnostics

| Case (BRIDGED) | Bridged cands | Capped out | Injected includes | Displaced graph cands |
|---|---|---|---|---|
| g036 | 3 | 0 | `macro/target/ana_dpm.C`, `prod_aod_complete.C`, `pid_complete.C` | 0 |
| g021 | 20 | 42 | `macro/target/prod_sim_hvmaps.C` + 19 README-evidence objects | 4 |
| n006 | 0 | 0 | — | 0 |
| g041 | 0 | 0 | — | 0 |
| g020 | 20 | 92 | `macro/target/ana_dpm.C` + 19 more | 20 |
| n004 | 0 | 0 | — | 0 |
| **Total** | **43** | **134** | — | **24** |

All bridged candidates carried `GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE` authority, exact frozen source versions, and zero deduplicated overlap with the unbridged baseline. `VERSION_SCOPE_CONFLICT` never triggered. Zero dedup overlaps.

## 14. Graph displacement analysis

Total displaced graph candidates across the six BRIDGED runs: 24 (g021: 4; g020: 20; others 0). All displacement is within-graph-prefix displacement measured against the exact UNBRIDGED graph baseline, bounded by the graph candidate limit, and fully receipted (`displaced_object_ids` recorded per cell). No displaced object was required evidence on any control (control outcomes unchanged).

## 15. Shortcut dependency

`LEGACY − ABLATION = +0.4` final-evidence recall, entirely from g036 and g021 (both 1.0 → 0.0). The two focused shortcuts remain materially responsible for useful retrieval on their direct cases under the synchronized final-D1 state. Controls show no dependency (n004: LEGACY == ABLATION).

## 16. Final-D1 / unbridged contribution

`STRUCTURED_UNBRIDGED − ABLATION = 0.0` at both final-evidence and combined-pool levels. The synchronized final D1 plus the pre-D3.5 structured path contributed nothing measurable on this six-case set — including g021, whose Mechanism-C knowledge did not surface through the unbridged mechanism (its governed objects cannot satisfy corpus-file selectors).

## 17. Incremental bridge contribution

Causally identified at the combined-candidate-recall level: **+0.3 mean (g036 +1.0, g021 +0.5, all others 0.0)**. Not present at the final-evidence level: **0.0**. The contribution required the bridge (UNBRIDGED was 0.0 on both), so it is attributable to the bridge alone, not to final D1 or the old structured path.

## 18. Bridged-vs-legacy parity

`STRUCTURED_BRIDGED − LEGACY = −0.4` final-evidence recall: bridged does not reach legacy parity. At the pool level the gap narrows to −0.1. No arm reached legacy performance on the two dependent cases without the legacy shortcuts.

## 19. Anti-shortcut audit

`case_id → file mapping = 0`; `question_id → path = 0`; `bound_rule_id → route = 0`; `expected evidence → D1 link = 0`; `legacy payload reuse = 0`; `evaluation metadata runtime use = 0` (all five prohibited-use counters verified zero in all 12 structured-arm executions). Focused rule IDs appear only in the `D3_5ExperimentConfig` suppression constants (arm configuration); no semantic payload reuse exists. Static check: `git diff 9b5a849 -- src/panda_agent/retrieval.py src/panda_agent/d3_structured.py` is empty (no case IDs, no rule IDs in `retrieval.py` at all). Expected evidence was consumed only by the deterministic evaluator after candidate production.

## 20. Historical D3 context (non-interchangeable)

Historical D3 measured a three-arm comparison on the deployed 22/16/0 materialization; this experiment measured four arms on the synchronized 24/16/1/2 materialization. g036/g021 remain `1.0 / 0.0` in the LEGACY and ABLATION positions across both experiments, but no causal delta is computed across the two experiments and the historical D3 `STRUCTURED` arm is not treated as a counterfactual cell.

## 21. Limitations

See the machine artifact (`limitations`): six-case scale with one metric-inapplicable control (denominator 5); temperature-0 execution variance (n006 R@5/MRR spread, final-evidence stable); g020 exercised the bridge through an ambiguous Tier-D seed and displaced the full graph channel (outcome-neutral; displacement under heavier reach not stress-tested); g021 e2 unreachable under the frozen seed resolution and one-transition budget; single frozen materialization and ranking configuration — results do not speak to alternative fusion weights or channel budgets.

## 22. Scientific decision

**`PARTIAL / TARGETED_RECOVERY_MIXED`.** The intended positive mechanism is observably useful at the candidate-pool level and causally identifiable there; it is not validated end-to-end to final evidence under the frozen ranking configuration. No material control failure or scope leakage invalidates the measurement; anti-shortcut invariants hold; the execution is complete and frozen. The binding constraint is downstream of the bridge (single-channel graph weight 0.8 vs multi-channel fused top-30 rerank cutoff), not reachability, materialization, caps, or version qualification. Per the no-repair rule, nothing was changed in response to these outcomes; any future fusion/ranking or seed-resolution change requires a separately authorized preregistered stage.

## 23. Lifecycle and next step

- `D3.5-A2 = COMPLETE / PARTIAL / TARGETED_RECOVERY_MIXED`; `D3_5_OUTCOME_EXPOSURE = COMPLETE`; `FORMAL_D3_5_A2_RUNS = 24`.
- `D3.5 = COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED` (end-to-end validation criterion not met).
- `D4 = NOT_STARTED`, **gate blocked** (D4 requires the D3.5 bridge validated by A2).
- Exact next task: a separately authorized post-A2 decision stage (no D4 start). The machine artifact records candidate directions as authored, unauthorized context only.
