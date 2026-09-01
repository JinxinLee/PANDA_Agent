# D3.5-A6 Phase 0 — Bounded Rerank-Admission Design & Preregistration

## 1. Executive preregistration decision

**`A6_PHASE0_DECISION = BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FROZEN`.** All Phase-0 readiness criteria are exact and implementation-unambiguous. This stage froze the A6 scientific question, the BASELINE/K2/K3 arm construction, the fixed 30-slot rerank-pool semantics, admission ordering and displacement semantics, the reranker repetition count (3), the symmetric cyclic execution schedule, evidence-retention aggregation, the generic K2-vs-K3 decision rule, material-control-regression semantics, origin-concentration diagnostics, and the outcome-exposure boundary — **before any reranker outcome exists**. `REAL_CASE_RERANKER_CALLS = 0`; no runner was implemented; `src/`, `configs/`, the replay fixture, and all A5/R2 scientific artifacts are unchanged. Machine artifact: `evaluation/d3_5_a6_bounded_rerank_admission_preregistration.json`.

## 2. Scientific question

> Can a very small reserved rerank-admission budget allow already-selected, governed bridge evidence to compete in the existing reranker and achieve stable downstream evidence retention, while preserving ordinary-candidate competition and avoiding material control regressions?

A6 does **not** ask: does QA answer quality improve; does the bridge become production-ready; should D4 start; should the reranker be replaced; should fusion weights change.

## 3. Upstream frozen state

| Parent | Identity | Status inherited |
|---|---|---|
| D3.5-A4 design | `evaluation/d3_5_a4_bridge_selectivity_admission_budget_design.json` (commit `e90604a`) | `STAGED_SELECTIVITY_THEN_ADMISSION`; `RERANK_POOL_SIZE = 30`; `ADMISSION_BUDGET_CANDIDATES = {2, 3}`; strategy R1; candidate-authority contract |
| D3.5-A5-R2 | freeze `f498714`, result `2bddbbc` | `PASS / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT`; frozen v2 selectivity (`PER_ORIGIN_CAP = 4`, `SELECTIVITY_CAP = 8`, unchanged gate) |
| D3.5-A5-R2-R1-R1 | commit `bb8b700` | `AUDIT_METADATA_CONSISTENCY_CLOSED`; A6 readiness `READY_FOR_PREREGISTRATION`, `A6_EXECUTION_STARTED = false`; the seven concentration diagnostics frozen |

## 4. Why admission is now identifiable

A5-R2 proved the repaired deterministic selectivity retains all applicable governed bridge evidence reaching the unchanged gate (g036.e1, g021.e1, g020.e1 all `APPLICABLE_AND_RETAINED`; 0 `APPLICABLE_AND_LOST`; 0 `GATE_RECALL_LIMITATION`) while bounding fan-out (g021 62→4, g020 67→8). The A2/A3 boundary (selected bridge evidence losing the fused top-30 competition, e.g. g036 fused rank 61) is exactly what a small reserved admission budget addresses. `SELECTIVITY_CAP` (how many governed candidates survive preselection) and `RERANK_ADMISSION_BUDGET` (how many non-baseline candidates get reserved slots) remain distinct; the S1 staged design is preserved — A6 uses only the validated v2 selectivity, adds no admission-only arm with unselected candidates, and does not reopen the A5 design.

## 5. BASELINE

```
persisted A5-R2 final v2-conditioned graph channel
  (six_case_records[case_id].selectivity_only_graph_ordering — already the
  final selected-bridge-prefix + ordinary-unbridged-graph ordering under
  GRAPH_CHANNEL_LIMIT = 20; consumed as-is, never re-merged)
→ frozen fusion with unchanged non-graph channels (weights exact 2.0 /
  dense 1.0 / sparse 1.0 / paper 1.15 / workflow 1.2 / graph 0.8;
  score = weight/(60+rank+1))
→ full fused ordering (deterministic recomputation; tie-breaking per the
  existing frozen fusion implementation, verified 6/6 by the Phase-0 probe)
→ top-30 BASELINE rerank pool
```

`A6_BASELINE_GRAPH_CHANNEL_AUTHORITY` = the persisted A5-R2 `selectivity_only_graph_ordering` — it is authoritative and already merged, so Phase 1 runs `select_v2` zero times, never applies the graph merge a second time, and may use the `merge_ids(selected_object_ids, unbridged_graph_ordering, 20)` reconstruction only as an all-six-cases equivalence check (parity failure ⇒ STOP BEFORE IMPLEMENTATION FREEZE). No reserved admission. **BASELINE is NOT** A2 STRUCTURED_BRIDGED (old 20-cap bridge), A5 v1, LEGACY, or ABLATION — the A6 scientific contrast is admission on top of repaired v2 selectivity. A Phase-0 read-only fusion probe confirmed this construction is deterministic: the same fusion code path reproduces the frozen `baseline_fused_ordering_full` top-30 exactly for all six cases when fed the old graph channel.

## 6. K2 arm

`ADMISSION_K2`: reserve **up to 2** candidates — the first `min(2, len(RESERVABLE_BRIDGE))` candidates of `RESERVABLE_BRIDGE` in frozen v2 order.

## 7. K3 arm

`ADMISSION_K3`: reserve **up to 3** candidates — the first `min(3, len(RESERVABLE_BRIDGE))` candidates in the same frozen v2 order.

## 8. Fixed pool construction

`RERANK_POOL_SIZE = 30` for every arm unless fewer than 30 unique candidates exist in the frozen candidate universe for that case; the pool is never globally expanded. `RESERVABLE_BRIDGE = V2_SELECTED_BRIDGE` (the exact frozen A5-R2 `selected_object_ids` ordering) **minus** candidates already in `BASELINE_TOP30`, deduplicated by stable object identity. Treatment pools keep exactly 30 members: all baseline members except the mechanically displaced ones, plus the reserved set.

## 9. Duplicate and displacement semantics

A v2-selected bridge candidate already in `BASELINE_TOP30` **stays in its ordinary baseline position and consumes 0 reserved slots**; the overlap is recorded (`baseline_overlap_bridge_ids`). Displacement follows the A4 rule, further frozen: displacement **starts from the bottom of BASELINE_TOP30** and is purely positional (exactly `len(reserved_set)` entries); bridge-derived status neither protects nor targets any candidate; no duplicate entries are ever created. All baseline candidates are displacement-eligible; no case-specific or gold-based protection exists. Empty reservable sets are valid (fail closed): the treatment pool then equals the baseline pool. Ceilings are **not quotas** — unused capacity is never filled with unrelated candidates.

## 10. Candidate authority

Every reserved candidate remains `GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE` with `IDENTITY_AUTHORITY = NONE`. Reservation grants only **permission to enter the ordinary reranker competition** — never answer authority, identity authority, automatic final selection, reranker priority, selector priority, or an extra RRF vote. Admission is computed only from v2-selected status + v2 ordering + K ceiling + baseline overlap; no new lexical score, no new embedding, no reranker pre-score, no case-specific selector, no gold signal.

## 11. Reranker interface freeze

The existing production reranker surface is reused unchanged: pool-ordered payload `[{object_id, title, source_id, text[:2000]}]`, the `ranked_object_ids` enum schema, `RERANK_SYSTEM_PROMPT`, `vertex.generate_json` at temperature 0.0, the environment-resolved generation model (default `gemini-3.7-flash` via `QA_GENERATION_MODEL_ID`), and the existing 3-attempt transient-retry loop. Phase 0/1 must not change prompt, parsing, payload shape, model, temperature, or retry policy; if the exact model/config cannot be recovered unambiguously the rule is **STOP BEFORE IMPLEMENTATION**; the Phase-1 runner manifest must record the resolved configuration actually used.

## 12. Reranker variance problem

`UPSTREAM_VARIANCE_CONTROL = FROZEN_TRACE_REPLAY` eliminates analyzer, D2, channel-retrieval, bridge-reachability, bridge-materialization, and fusion-input variance. The **only** intended non-deterministic component in Phase 2 is the existing reranker model execution. Reranker calls are independent model executions: "paired" means same frozen case + same frozen upstream trace + same preregistered repetition index + symmetric arm schedule — **not shared RNG**, and no such claim may be made.

## 13. Three-repetition rationale

`RERANKER_REPETITIONS_PER_ARM_PER_CASE = 3` (strategy R1 — symmetric repeated reranker evaluation, preserved from A4). One repetition cannot characterize variance; two are tie-prone with weak stability semantics; three is the minimal odd-number design supporting majority/median semantics; larger counts are unnecessary Monte-Carlo expansion for this mechanistic stage. The count is frozen from this generic rationale, **not** from A2/A5/R2 outcomes. Expected formal load: `EXPECTED_FORMAL_RERANKER_CALLS = 6 × 3 × 3 = 54`; internal provider retries are accounted separately and never counted as repetitions.

## 14. Symmetric execution schedule

Cyclic per case, case-major (all 3 repetitions of a case complete before the next case; case order `g036 → g021 → n006 → g041 → g020 → n004`):

| Repetition | Order |
|---|---|
| 1 | BASELINE → K2 → K3 |
| 2 | K2 → K3 → BASELINE |
| 3 | K3 → BASELINE → K2 |

No randomization; no order chosen after outcomes.

## 15. Evidence-retention aggregation

Required evidence group is the primary retention unit. Per arm/case/group/repetition the existing deterministic evaluator records `retained = true/false`; `STABLE_RETAINED` = retained in ≥ 2/3 repetitions; `STABLE_LOST` = retained in ≤ 1/3; no weighted probability, no p-values. Rank diagnostics: per-repetition reranked rank if retained, aggregated as median retained rank only, secondary; rank improvement alone never determines K selection. Required flow: reranker output → freeze the result → evaluator-only matching over the production-identical deterministic post-rerank surface (fallback merge with the unchanged baseline fused ordering, unchanged plan-driven reordering, unchanged `select_final_evidence` at the frozen `final_evidence_limit = 12`); QA/verifier/judge calls stay 0 and no answer generation is added.

## 16. Material control regression

`MATERIAL_CONTROL_REGRESSION` for a required/control group: `BASELINE retention_count >= 2 AND treatment retention_count <= 1` (baseline-stable evidence lost under treatment) — repetition-aware, filtering single-run reranker variance. Non-material fluctuations (`3/3→2/3`, `2/3→2/3`, `1/3→0/3`, `2/3→3/3`) are never automatically classified as material regressions unless another frozen primary invariant is violated.

## 17. K2-vs-K3 decision rule

`DEFAULT_BUDGET_PREFERENCE = K2` (fewer ordinary candidates displaced), corrected in Phase 0-R1 to smallest-sufficient-SAFE-budget and finalized in Phase 0-R1-R1 as the **smallest sufficient causally witnessed safe budget**. Benefit population = `ADMISSION_APPLICABLE_BRIDGE_GROUP`s (required evidence groups with ≥ 1 evaluator-identified required candidate of which ≥ 1 belongs to `RESERVABLE_BRIDGE` for that case; evaluator-only, classified after output freeze, never a runtime input). Safety population = all BASELINE-STABLE evaluator-required/control groups. With `DELTA_K` = admission-applicable groups `STABLE_RETAINED` under K and **not** under BASELINE, `CAUSAL_DELTA_K` = the subset of `DELTA_K` groups that also carry `STABLE_RESERVED_REQUIRED_WITNESS` under K (`0 <= CAUSAL_DELTA_K <= DELTA_K`; `NONCAUSAL_STABLE_DELTA_K = DELTA_K - CAUSAL_DELTA_K`, diagnostic only), `REGRESSION_K` = material control regressions under K, and `MECHANISTIC_SAFE_EFFECTIVE(K) = CAUSAL_DELTA_K > 0 AND REGRESSION_K == 0`:

- both K2 and K3 MECHANISTIC_SAFE_EFFECTIVE → `SELECTED_ADMISSION_BUDGET = 3` iff `CAUSAL_DELTA_3 > CAUSAL_DELTA_2`, else 2;
- only K2 MECHANISTIC_SAFE_EFFECTIVE → 2; only K3 MECHANISTIC_SAFE_EFFECTIVE → 3;
- neither MECHANISTIC_SAFE_EFFECTIVE → no budget is selected as PASS.

A budget with `CAUSAL_DELTA_K > 0` but `REGRESSION_K > 0` is not MECHANISTIC_SAFE_EFFECTIVE — safety still precedes budget minimality. K3 beats K2 **only on causal benefit**: a pure increase in `DELTA_K`, median rank, MRR-like diagnostics, or `NONCAUSAL_STABLE_DELTA_K` can never by itself justify K3. Frozen synthetic edge case (design-only, not a real-case test): K2 with `DELTA_2 = 1, CAUSAL_DELTA_2 = 1, REGRESSION_2 = 0` and K3 with `DELTA_3 = 2, CAUSAL_DELTA_3 = 0, REGRESSION_3 = 0` selects **budget 2** — only K2 provides causally witnessed bridge-admission recovery. The earlier `SAFE_EFFECTIVE(K) = DELTA_K > 0 AND REGRESSION_K == 0` (Phase 0-R1) is superseded for PASS selection and retained as a broader diagnostic. The budget is never chosen from positive-case identity.

## 18. Origin concentration diagnostics

Carried forward exactly: `selected_bridge_origin_count`, `selected_bridge_per_origin_counts`, `reserved_bridge_origin_count`, `reserved_bridge_per_origin_counts`, `ordinary_rerank_candidates_displaced`, `reserved_bridge_candidate_ids`, `reserved_candidate_origin_ids`. **Diagnostic-only**: no numeric failure threshold (never derived from g020's v2 `origins_after = 2` or the 4+4 attribution); A6 does not modify admission to enforce diversity; the v2 `PER_ORIGIN_CAP = 4` remains the selectivity-stage guard and no new per-origin admission cap is added — A6 tests its downstream consequence. Per treatment pool: `baseline_pool_object_ids`, `reserved_bridge_candidate_ids`, `baseline_overlap_bridge_ids`, `ordinary_rerank_candidates_displaced`, `displaced_object_ids`, `treatment_pool_object_ids`, `pool_size`, `pool_fingerprint`. Per reserved candidate: `object_id`, `source_id`, `source_version_id`, v2 selectivity position, `attributed_origin_id`, `already_in_baseline`, `reserved_slot_consumed`.

## 19. Anti-tuning boundary

Phase 0 made `REAL_CASE_RERANKER_CALLS = 0`: no "just to verify" treatment-pool run, no real-case baseline smoke test, no single-call variance probe — synthetic construction tests belong to Phase 1. K, repetition count, material-regression threshold, pool order, and decision semantics were frozen from generic criteria and are never tuned from exposed A5/R2 result details; g020's origin concentration may motivate required diagnostics only. Runtime admission and reranker construction consume no case role, positive/control label, or required evidence; case-role metadata may be used only for post-output scientific interpretation.

## 20. Outcome-exposure boundary

`A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED` until the **first real-case reranker call starts** — not when a result is persisted and not when a human reads it (PERSISTED_RESULT_EXPOSURE and HUMAN_RESULT_INSPECTION are later layers, per the corrected R2 semantics).

## 21. Verdict matrix

| Verdict | Condition |
|---|---|
| `PASS / BOUNDED_RERANK_ADMISSION_VALIDATED_FOR_DEVELOPMENT` | protocol valid; construction invariants pass; **at least one `MECHANISTIC_SAFE_EFFECTIVE` budget exists** (`CAUSAL_DELTA_K > 0 AND REGRESSION_K == 0`); `SELECTED_ADMISSION_BUDGET` chosen by the frozen causal-safe hierarchy; selected budget has `REGRESSION_K = 0` and `CAUSAL_DELTA_K > 0`; no runtime gold/case-role leakage; no post-exposure treatment mutation. The stable reserved-required-candidate witness is embedded in `CAUSAL_DELTA_K` and is not separately re-required after selection |
| `PARTIAL / ADMISSION_RECOVERY_WITH_CONTROL_REGRESSION` | stable `DELTA_K > 0` exists but every stable-recovery budget is unsafe (for every budget with `DELTA_K > 0`: `REGRESSION_K > 0`); may include causal or noncausal recovery; no PASS budget exists |
| `PARTIAL / POOL_PERTURBATION_ASSOCIATED_RECOVERY_WITHOUT_RESERVED_WITNESS` | at least one safe budget (`REGRESSION_K == 0`) has `DELTA_K > 0`, but no safe budget has `CAUSAL_DELTA_K > 0` — stable downstream recovery from the admission-modified pools was observed, but the experiment did not validate that an actually reserved required bridge candidate carried it; stronger than no recovery, weaker than mechanistic PASS |
| `PARTIAL / ADMISSION_RECOVERY_NOT_STABLE_ACROSS_RERANKER_REPETITIONS` | `DELTA_2 = DELTA_3 = 0` but `UNSTABLE_ADMISSION_RECOVERY` exists (an admission-applicable group recovered in ≥ 1 individual treatment repetition relative to baseline without satisfying `DELTA_K` stable recovery) |
| `PARTIAL / ADMISSION_DID_NOT_VALIDATE_DOWNSTREAM_RECOVERY` | `DELTA_2 = 0`, `DELTA_3 = 0`, and no `UNSTABLE_ADMISSION_RECOVERY` — the true residual no-recovery class |
| `FAIL / BOUNDED_ADMISSION_CONSTRUCTION_OR_AUTHORITY_FAILED` | structural/protocol implementation failures only: pool-size invariant, duplicate-admission or reserved-slot accounting, out-of-scope admission, candidate-authority violation, post-rerank replay parity failure discovered after implementation freeze, implementation/preregistration mismatch, or another deterministic construction/authority invariant failure. Ordinary `MATERIAL_CONTROL_REGRESSION` groups are scientific budget-safety outcomes handled by `REGRESSION_K` / `MECHANISTIC_SAFE_EFFECTIVE` / PARTIAL logic — **never** automatic FAIL triggers; the Phase-0 "systematic control degradation" trigger is removed with no new numeric threshold (previous label `BOUNDED_ADMISSION_SAFETY_OR_CONSTRUCTION_FAILED`, narrowed by Phase 0-R1-R1) |
| `INVALID` | reranker outcome seen before prereg freeze; K/repetition/decision rule changed after exposure; unregistered budget arm; gold/required evidence in pool construction; case-role branch in admission; reranker prompt/model/config changed during the experiment; outcome-guided reruns |

Verdicts are assigned by the frozen deterministic **7-level precedence** (total, non-overlapping, no outcome-dependent label selection): 1. INVALID; 2. FAIL (structural construction/authority/implementation invariant failure); 3. PASS (a MECHANISTIC_SAFE_EFFECTIVE budget exists); 4. PARTIAL / recovery-with-regression; 5. PARTIAL / pool-perturbation-recovery-without-reserved-witness; 6. PARTIAL / not-stable-across-repetitions; 7. PARTIAL / no-downstream-recovery (otherwise). `RESERVED_REQUIRED_CANDIDATE_RETAINED` records, per admission-applicable group/repetition, whether final evidence actually contains a required-evidence matching candidate that consumed a reserved slot in that treatment arm; `STABLE_RESERVED_REQUIRED_WITNESS` = retained in ≥ 2/3 repetitions; `NONCAUSAL_STABLE_DELTA_K = DELTA_K − CAUSAL_DELTA_K` quantifies stable pool-level recovery not backed by a stable witness (diagnostic only, no runtime effect).

Identical pool fingerprints between a treatment and BASELINE mean identical reranker inputs: any output difference is `RERANKER_VARIANCE_REFERENCE`, never admission effect; admission effect is interpretable only when the fingerprints differ.

## 22. What A6 validates

Whether a very small reserved admission budget (2 or 3 of 30 rerank slots) lets already-selected governed bridge evidence compete in the **existing unchanged reranker** and achieve stable downstream evidence retention, under symmetric reranker-variance accounting, without material control regressions — a development-stage bounded admission mechanism.

## 23. What A6 does not validate

QA answer quality; production readiness (`PRODUCTION_ACTIVATION = false` even on PASS); a D4 start; reranker replacement; fusion-weight changes; generalization beyond the six exposed development cases (`POST_OUTCOME_MECHANISTIC_DEVELOPMENT`, never a fresh holdout).

## 24. Phase-1 contract

> **D3.5-A6 Phase 1 — Bounded Admission Prototype & Synthetic Construction Freeze**

Phase 1 may implement the deterministic BASELINE/K2/K3 pool construction, diagnostics, synthetic tests, and the formal runner **without executing real reranker calls** (`REAL_CASE_RERANKER_CALLS = 0`), then freeze the implementation. Phase 1 must first **mechanically materialize the complete replay surface** (`COMPLETE_REPLAY_SURFACE_MATERIALIZATION_REQUIRED = true`): `POST_RERANK_REPLAY_REQUIRED_OBJECT_UNIVERSE` = the union of (1) every object in the full v2-conditioned fused ordering, (2) every frozen exact-channel member needed for `symbol_first`, (3) every reserved bridge candidate, (4) every additional object referenced by deterministic final-selector logic before `final_evidence_limit` can be satisfied — under the frozen fusion construction this equals the full fused-ordering member set (a mechanically computable complete superset; the reranker output and the fallback merge only ever contain fused-ordering members). Phase 0 recorded a generic problem class, not a case-specific branch: the registry covers the old-cap top-30 ∪ bridge candidates with `text[:2000]`/title/source_id/object_type/locator only, while v2 conditioning re-admits previously displaced ordinary graph candidates (the probe saw exactly one such top-30 member today: `concept.restgas_longitudinal_efficiency`, g020 — an example only, never special-cased) and the selector replay surface additionally needs `source_version_id`, `authority_level`, full selector-visible text, and the `paper_page_hints` plan field. Phase 1 materializes **all** missing objects/fields from the frozen normalized corpus under the unchanged index-identity check, with the gate conditions of `complete_replay_surface_gate` (100% coverage, all selector fields, unchanged source/version and full-locator identity, reproducible channel membership/fusion scores/exact-channel ordering, passing synthetic/parity tests) required before implementation freeze; runtime KeyError→add-one-object→rerun repair is prohibited. The fixture itself is unchanged in Phase 0.

## 25. Phase-2 contract

> **D3.5-A6 Phase 2 — Paired Repeated Reranker Replay**

Only after the Phase-1 implementation freeze may the 54 formal reranker calls run. Phases 1 and 2 must not be merged unless explicitly authorized later.

## 26. Lifecycle

```
D3.5-A6             = IN_PROGRESS / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FINALIZED
D3.5-A6-PHASE0      = COMPLETE / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FINALIZED
D3.5-A6-PHASE0-R1   = COMPLETE / REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIRED
D3.5-A6-PHASE0-R1-R1 = COMPLETE / CAUSAL_BUDGET_SELECTION_AND_VERDICT_PRECEDENCE_REPAIRED
D3.5-A6-PHASE1      = NOT_STARTED / READY_TO_IMPLEMENT
D3.5-A6-PHASE2      = NOT_STARTED / BLOCKED_UNTIL_PHASE1_FREEZE
D3.5-A5-R2          = COMPLETE / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT (unchanged)
D3.5                = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN
D4                  = NOT_STARTED / BLOCKED
```

Execution accounting: real-case reranker calls 0; real-case selectivity runs 0; real-case treatment-pool constructions 0; analyzer/embedding/QA/verifier/judge calls 0; PostgreSQL/Qdrant writes 0; novel_validation/holdout untouched and unsealed-state unchanged; `src/`/`configs/`/fixture/A5-R2 artifacts unchanged. Protected datasets: `novel_validation = FROZEN / UNSEEN`, `novel_holdout = SEALED / UNSEEN`.

## 27. Exact next task

> **D3.5-A6 Phase 1 — Bounded Admission Prototype & Synthetic Construction Freeze** — deterministic pool construction, diagnostics, synthetic tests, formal runner without real reranker calls; Phase 2 (the 54 formal calls) remains blocked until the Phase-1 freeze.

## 28. Phase 0-R1 — Replay-Surface & Budget-Decision Contract Repair (2026-09-02)

Independent audit found three preregistration-contract defects; all three are repaired in place (machine artifact updated with `repair_history[].D3.5-A6-PHASE0-R1_REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIR`; dedicated report `evaluation/D3_5_A6_PHASE0_R1_REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIR.md`). All accepted Phase-0 architecture (three arms, pool 30, K ∈ {2,3}, ceiling-not-quota, bottom-first displacement, v2 admission order, candidate authority, 3 repetitions, cyclic schedule, ≥2/3 stable retention, diagnostic-only origin concentration, no new scorer, no QA/verifier/judge, no production activation, D4 blocked) is unchanged.

**Post-rerank replay surface (defect A).** The Phase-0 contract partly conflated the reranker input payload with the post-rerank deterministic selector replay state. Two explicit data contracts are now frozen: `RERANKER_PAYLOAD_SURFACE` (object_id/title/source_id/`text[:2000]`, in exact treatment-pool order; exists only to call the unchanged reranker; no selector-only metadata in the model prompt) and `POST_RERANK_SELECTOR_REPLAY_SURFACE` (a separate deterministic surface carrying, per object: object_id, source_id, source_version_id, object_type, title, selector-visible text, authority_level, the **complete raw locator** — the duplicate-locator identity is the canonical JSON dump of the entire locator, so no key may be dropped — plus channel membership and fusion score, and the frozen plan fields including `paper_page_hints` and the raw question). Model-visible fields and selector-only fields must remain explicitly separated (e.g., distinct `reranker_payload_registry` / `selector_replay_registry`); exact Phase-1 schema is free, the semantic separation is frozen.

**Complete replay object universe.** Coverage is never "rerank top-30 only": production consumes `ordered = dedupe([*reranked, *full_fused_order])` and selection may continue beyond top-30. `POST_RERANK_REPLAY_REQUIRED_OBJECT_UNIVERSE` = full v2-conditioned fused ordering ∪ exact channel ∪ reserved bridge candidates ∪ any additional object referenced by deterministic selector logic — mechanically this equals the full fused-ordering member set (a complete superset, never outcome-shaped incremental filling).

**Selector-visible text semantics.** Repository inspection shows production consumes **full** text in three places: `symbol_first` matches plan symbols against exact-channel items' full text; `_evidence` builds `Evidence.text` from the full payload; the frozen evaluator's `title_contains` check searches the evidence item's full text. `text[:2000] == production selector text` therefore cannot be proven (needle occurrence beyond char 2000 is data-dependent), so **OPTION A** is frozen: persist the complete selector-visible frozen text for every universe object; the reranker model still receives `text[:2000]` only.

**Authoritative graph channel (defect C).** `A6_BASELINE_GRAPH_CHANNEL_AUTHORITY` = the persisted A5-R2 `selectivity_only_graph_ordering` — already the final v2-conditioned graph-channel ordering (bridge prefix + ordinary unbridged graph, limit 20). `PHASE1_SELECT_V2_RUNS = 0`; the double graph merge is prohibited; `merge_ids` reconstruction is an equivalence check only (all six cases; parity failure ⇒ STOP BEFORE IMPLEMENTATION FREEZE); the full fused ordering is recomputed deterministically from the authoritative channel + frozen non-graph channels + frozen weights.

**Incremental admission benefit & safety-first selection (defect B).** Benefit population = `ADMISSION_APPLICABLE_BRIDGE_GROUP`s (required group with ≥ 1 evaluator-identified required candidate, of which ≥ 1 is in `RESERVABLE_BRIDGE`; evaluator-only, post-output-freeze, never runtime). Safety population = all BASELINE-STABLE evaluator-required/control groups. Primary benefit metrics are `DELTA_2`/`DELTA_3` (applicable bridge groups stably retained under K but not under BASELINE); total stable retained counts are diagnostic only. Safety metrics `REGRESSION_2`/`REGRESSION_3` use the unchanged material-regression rule over the safety population. `SAFE_EFFECTIVE(K) = DELTA_K > 0 AND REGRESSION_K == 0` is evaluated **before** smallest-budget preference: both safe-effective → 3 iff `DELTA_3 > DELTA_2` else 2; only one safe-effective → that one; neither → no PASS budget. An unsafe smaller K2 can never win merely by being smaller, and rank-only K3 improvement can never override `DELTA_2 == DELTA_3`.

**Causal reserved-candidate witness.** PASS now requires, in addition to the Phase-0 conditions, that at least one `ADMISSION_APPLICABLE_BRIDGE_GROUP` has `DELTA_K` benefit **and** `STABLE_RESERVED_REQUIRED_WITNESS` (`RESERVED_REQUIRED_CANDIDATE_RETAINED` in ≥ 2/3 repetitions — final evidence actually contains a required-evidence matching candidate that consumed a reserved slot in that treatment arm). Improvement not carried by an actually reserved required candidate is `POOL_PERTURBATION_ASSOCIATED_RECOVERY`, diagnostic only.

**Verdict precedence.** Frozen total order with no outcome-dependent label selection: 1. INVALID; 2. FAIL; 3. PASS (a SAFE_EFFECTIVE budget exists with the required witness); 4. PARTIAL / ADMISSION_RECOVERY_WITH_CONTROL_REGRESSION (`DELTA_K > 0` exists but no effective budget is safe); 5. PARTIAL / ADMISSION_RECOVERY_NOT_STABLE_ACROSS_RERANKER_REPETITIONS (no stable `DELTA_K`, but `UNSTABLE_ADMISSION_RECOVERY` observed); 6. PARTIAL / ADMISSION_DID_NOT_VALIDATE_DOWNSTREAM_RECOVERY otherwise.

### 28.1 Phase 0-R1-R1 — Causal Budget Selection & Verdict Precedence Repair (2026-09-02)

Phase 0-R1 closed the broad benefit/safety split; this stage closes the final causal-selection edge case by moving the stable reserved-required-candidate witness **into the budget-eligibility metric itself**, and it resolves the material-regression-vs-FAIL conflation. The Phase 0-R1 bullet texts above (SAFE_EFFECTIVE hierarchy, 6-level precedence) are retained as historical provenance; the authoritative contracts are:

**`CAUSAL_DELTA_K` and `MECHANISTIC_SAFE_EFFECTIVE`.** `CAUSAL_DELTA_K` = the number of `ADMISSION_APPLICABLE_BRIDGE_GROUP`s that are (1) `STABLE_RETAINED` under treatment K and not under BASELINE **and** (2) carry `STABLE_RESERVED_REQUIRED_WITNESS` under K — i.e., stable incremental admission recovery with a stable actually-reserved required-candidate witness, with the invariant `0 <= CAUSAL_DELTA_K <= DELTA_K`. `NONCAUSAL_STABLE_DELTA_K = DELTA_K − CAUSAL_DELTA_K` (diagnostic only: stable improvement correlated with the admission-modified pool but not mechanistically carried by a reserved required candidate). `MECHANISTIC_SAFE_EFFECTIVE(K) = CAUSAL_DELTA_K > 0 AND REGRESSION_K == 0` replaces `SAFE_EFFECTIVE` as the PASS budget criterion (the older rule is retained as a broader diagnostic and marked superseded). Budget selection uses the frozen causal-safe hierarchy: both budgets MECHANISTIC_SAFE_EFFECTIVE → 3 iff `CAUSAL_DELTA_3 > CAUSAL_DELTA_2` else 2; only one → that one; neither → no PASS budget. A budget with `CAUSAL_DELTA_K > 0` but `REGRESSION_K > 0` is never eligible — safety precedes minimality; K3 beats K2 only on causal benefit (never on larger `DELTA_K`, rank, or `NONCAUSAL_STABLE_DELTA_K` alone). Frozen synthetic edge case: K2 (D=1, C=1, R=0) vs K3 (D=2, C=0, R=0) selects **budget 2** — design-only example, not a real-case test.

**Stable pool-perturbation PARTIAL.** New verdict class `PARTIAL / POOL_PERTURBATION_ASSOCIATED_RECOVERY_WITHOUT_RESERVED_WITNESS` — used when at least one safe budget (`REGRESSION_K == 0`) has `DELTA_K > 0` but no safe budget has `CAUSAL_DELTA_K > 0`: the admission-modified pools produced stable downstream recovery that the experiment did not validate as carried by an actually reserved required bridge candidate.

**Material regression vs FAIL.** `MATERIAL_CONTROL_REGRESSION` is a **scientific budget-safety outcome**, never by itself a FAIL-level structural invariant failure; it is handled through `REGRESSION_K`, `MECHANISTIC_SAFE_EFFECTIVE`, and the recovery-with-regression PARTIAL. FAIL is narrowed to structural/protocol implementation failures only (pool-size invariant, duplicate-admission or reserved-slot accounting, out-of-scope admission, candidate-authority violation, post-rerank replay parity failure discovered after implementation freeze, implementation/preregistration mismatch, other deterministic construction/authority invariant failures), relabeled `FAIL / BOUNDED_ADMISSION_CONSTRUCTION_OR_AUTHORITY_FAILED` (previous label recorded); the "systematic control degradation" trigger is removed with no new numeric threshold. The recovery-with-regression PARTIAL scope is now exact (exists K with `DELTA_K > 0` and every `DELTA_K > 0` budget has `REGRESSION_K > 0`); the not-stable PARTIAL applies only when `DELTA_2 = DELTA_3 = 0` with `UNSTABLE_ADMISSION_RECOVERY`; the no-recovery PARTIAL is the true residual class.

**Final verdict precedence (authoritative, total, non-overlapping).** 1. INVALID; 2. FAIL / BOUNDED_ADMISSION_CONSTRUCTION_OR_AUTHORITY_FAILED; 3. PASS / BOUNDED_RERANK_ADMISSION_VALIDATED_FOR_DEVELOPMENT (at least one MECHANISTIC_SAFE_EFFECTIVE budget exists); 4. PARTIAL / ADMISSION_RECOVERY_WITH_CONTROL_REGRESSION (stable `DELTA_K > 0` exists but every stable-recovery budget is unsafe); 5. PARTIAL / POOL_PERTURBATION_ASSOCIATED_RECOVERY_WITHOUT_RESERVED_WITNESS (a safe budget has `DELTA_K > 0` but no safe budget has `CAUSAL_DELTA_K > 0`); 6. PARTIAL / ADMISSION_RECOVERY_NOT_STABLE_ACROSS_RERANKER_REPETITIONS (`DELTA_2 = DELTA_3 = 0` but `UNSTABLE_ADMISSION_RECOVERY` exists); 7. PARTIAL / ADMISSION_DID_NOT_VALIDATE_DOWNSTREAM_RECOVERY (otherwise). PASS no longer separately re-requires the witness after budget selection — it is embedded in `CAUSAL_DELTA_K`.

Dedicated artifacts: `evaluation/d3_5_a6_phase0_r1_r1_causal_budget_selection_verdict_precedence_repair.json` and `evaluation/D3_5_A6_PHASE0_R1_R1_CAUSAL_BUDGET_SELECTION_AND_VERDICT_PRECEDENCE_REPAIR.md`.
