# D3.5-A6 Phase 1 — Bounded Admission Prototype & Synthetic Construction Freeze

## 1. Executive implementation decision

**`A6_PHASE1_DECISION = BOUNDED_ADMISSION_PROTOTYPE_AND_REPLAY_IMPLEMENTATION_FROZEN`.** The finalized Phase-0 preregistration is mechanically implemented without semantic change: the complete production-parity replay surface is materialized (345 objects, 0 missing), the authoritative v2-conditioned graph channel plus deterministic fusion produce frozen BASELINE/K2/K3 pools for all six development cases (18 arm-pool manifests, 0 invariant violations), and the exact 54-slot Phase-2 call plan is frozen with every `outcome_status = NOT_EXECUTED`. Decision logic is implemented and synthetically validated (32 tests). **No reranker outcome has been generated**: `FORMAL_RERANKER_CALLS_EXECUTED = 0`, `PHASE1_SELECT_V2_RUNS = 0`, `A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED`.

## 2. Parent preregistration identity

Starting HEAD `9e56027` (Phase0-R1-R1). Authoritative chain: `D3.5-A6-PHASE0 = COMPLETE / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FINALIZED`; `-PHASE0-R1 = COMPLETE / REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIRED`; `-PHASE0-R1-R1 = COMPLETE / CAUSAL_BUDGET_SELECTION_AND_VERDICT_PRECEDENCE_REPAIRED`. The preregistration is authoritative; Phase 1 redesigned nothing.

## 3. Implementation scope

One compact evaluation-side script `evaluation/scripts/d3_5_a6_phase1_admission.py` (modes: `build-fixture`, `build-pools`, `build-call-plan`, `self-test`) plus synthetic tests in `tests/unit/test_d3_5_a6_phase1_admission.py`. `src/` and `configs/` unchanged; the historical A5/R2 fixture, the A5-R2 result, and the A5-R2 implementation are untouched — A6 derives from them.

## 4. Authoritative graph replay

For every case, `A6_BASELINE_GRAPH_CHANNEL_AUTHORITY` = the persisted A5-R2 `six_case_records[case_id].selectivity_only_graph_ordering`, consumed as-is (already the final bridge-prefix + ordinary-unbridged ordering under limit 20). Parity verification only: `merge_ids(selected_object_ids, unbridged_graph_ordering, 20) == persisted ordering` — **6/6**. `PHASE1_SELECT_V2_RUNS = 0`; no double merge.

## 5. Full fusion reconstruction

Deterministic RRF replay: frozen non-graph channel orderings in fixture key order (= production `exact → dense → sparse → workflow` traversal; graph last), weights `exact 2.0 / dense 1.0 / sparse 1.0 / paper 1.15 / workflow 1.2 / graph 0.8`, `score = weight/(60+rank+1)`, stable descending sort. Parity anchor: feeding the **old-cap** graph channel reproduces the parent fixture's `baseline_fused_ordering_full` **exactly for all six cases (full ordering, not only top-30)** — the fusion replay is provably production-equivalent. `FUSION_REPLAY_PARITY = 6/6`.

## 6. Replay-surface materialization

`POST_RERANK_REPLAY_REQUIRED_OBJECT_UNIVERSE` = member set of the full v2-conditioned fused ordering per case: g036 76, g021 47, n006 80, g041 60, g020 81, n004 67 (345 unique objects registry-wide). All selector fields materialized generically from the frozen normalized corpus (`data/normalized/9925ec31…/knowledge_objects.jsonl`, read-only): `missing_selector_replay_object_ids = []` for all six cases — **100% coverage**. n006's plan fields lacked empty-list keys dropped by A2 record compaction; generic empty defaults (`symbols = []` etc.) were materialized with no case-specific branch.

## 7. Reranker payload registry

`reranker_payload_registry`: exactly `object_id / title / source_id / text[:2000]` per candidate — no selector-only metadata. Coverage of every candidate that can appear in any of the 18 arm pools: **100%**.

## 8. Selector replay registry

`selector_replay_registry` (explicitly separated from the payload registry per Phase0-R1): per object `object_id, source_id, source_version_id, object_type, title, complete selector-visible frozen text (OPTION A), authority_level, complete raw locator dict, channel membership, fusion score`. Plan fields per case: `intent, target_repositories, resolved_versions, symbols, concepts, required_source_types, source_budgets, paper_page_hints, raw question text`. No locator keys omitted.

## 9. BASELINE construction

`BASELINE_POOL = first min(30, len(full_fused_ordering))` of the authoritative v2-conditioned fused ordering — 30 members for all six cases (universes 47–81). No reservation.

## 10. K2 construction

`reserved_K2 = first min(2, len(RESERVABLE_BRIDGE))` in frozen v2 order; exactly that many lowest-ranked (bottom-first) baseline members displaced; survivors keep relative fused order; reserved appended in v2 order. Reserved counts: g036 2, g021 1, n006/g041/n004 0, g020 2.

## 11. K3 construction

Identical semantics with ceiling 3. Reserved counts: g036 3, g021 1, controls 0, g020 3. No other difference from K2.

## 12. Frozen six-case pool manifest

`evaluation/d3_5_a6_phase1_pool_manifest.json` — 18 manifests, `pool_invariant_violations = []`, `duplicate_object_ids_per_pool = []` everywhere. Reservable bridges: g036 3, g021 1, g020 6, controls 0. **Overlap facts**: g021 has 3 of its 4 v2-selected bridge candidates already inside the v2-conditioned fused top-30 (zero reservation slots consumed), and g020 has 2 of 8 — recorded per arm with `baseline_overlap_bridge_ids`.

## 13. Origin-concentration diagnostics

All seven preregistered fields carried per case/arm (selected origin counts from the A5-R2 records; reserved per-origin counts from `attributed_origin_id`, e.g. g036 K3: `edge.a767…`×2 + `edge.2e09…`×1; g020 K3: `edge.ea3a…`×2 + `edge.8127…`×1). Diagnostic-only; no numeric threshold.

## 14. Production post-rerank replay implementation

`post_rerank_replay(...)` mirrors the production post-rerank block: `ordered = dedupe([*reranked, *full_fused_order])` → preferred-source logic → `symbol_first` → `required_first` → `hinted_first` → final dedupe → `ranked = ordered[:30]` → **imported production `select_final_evidence`** with `final_evidence_limit = 12`. Production code was not modified; `select_final_evidence` and `_source_type_of` are reused unchanged.

## 15. Production parity checks

`POST_RERANK_SELECTOR_PARITY = PASS`: (a) the selection core is the production function itself; (b) the wrapper mirror is anchored by `test_production_wrapper_expressions_still_present`, asserting the mirrored expressions exist verbatim in `retrieval.py`; (c) fusion replay is anchored 6/6 against the historical full fused ordering; (d) double-execution determinism over all six real frozen traces with fabricated model-free ranked sequences (identity/reverse): 12/12 receipts byte-identical. The original A2 model outputs were not persisted, so historical-output reproduction is not possible — parity is established exactly as preregistered (production core + mirrored wrapper + anchors).

## 16. Decision-logic implementation

Pure functions implemented without running on real outcomes: `STABLE_RETAINED`/`STABLE_LOST` (≥2/3, ≤1/3), `MATERIAL_CONTROL_REGRESSION` (baseline ≥2 AND treatment ≤1), `ADMISSION_APPLICABLE_BRIDGE_GROUP` classification (evaluator-only), `DELTA_K`, `CAUSAL_DELTA_K` (with the `0 <= CAUSAL_DELTA_K <= DELTA_K` invariant and the witness embedded), `NONCAUSAL_STABLE_DELTA_K`, `REGRESSION_K`, `MECHANISTIC_SAFE_EFFECTIVE`, the causal-safe `SELECTED_ADMISSION_BUDGET` hierarchy, `RESERVED_REQUIRED_CANDIDATE_RETAINED`/`STABLE_RESERVED_REQUIRED_WITNESS`, and the exact seven-level verdict precedence.

## 17. Synthetic/property tests

32 pytest tests, all passing (`tests/unit/test_d3_5_a6_phase1_admission.py`): pool construction (0/1/exactly-K/>K reservable, overlap zero-slot, duplicate protection, bottom 1/2/3 displacement, order preservation, universe < 30, identical-pool relations, validator flags); replay (full/partial orderings, repeated-ID dedup, fallback, symbol/preferred-source/required/hinted movement with discriminating constructions, final dedup, source budget cap 4, duplicate-locator suppression, limit 12, determinism, production source anchor); decision logic (9 truth-table cases including the frozen Phase0-R1-R1 synthetic edge case, budget hierarchy, `MCR`-never-auto-FAIL, exhaustive `CAUSAL_DELTA <= DELTA` bounds, 576-combination verdict uniqueness, witness semantics, applicable-group classification).

## 18. Phase-2 54-slot execution plan

`evaluation/d3_5_a6_phase1_execution_manifest.json`: 54 entries (6 cases × 3 repetitions × 3 arms) in the preregistered cyclic schedule, case-major, each with `formal_call_index, case_id, repetition, arm, ordered_pool_object_ids, ordered_reranker_payload (exact 4-field payload), pool_size, pool_identity (ordered ID list), model_contract_reference, outcome_status = NOT_EXECUTED`. Identical-pool slots (g021 K2≡K3; controls' all-equal arms) are retained as symmetric variance references and never collapsed.

## 19. Model/config freeze

Resolved through the existing settings path without any provider invocation: generation model `gemini-3.7-flash` (`VertexSettings.from_env()` / `QA_GENERATION_MODEL_ID` default), `temperature = 0.0`, system prompt `RERANK_SYSTEM_PROMPT` (imported unchanged), `ranked_object_ids` enum schema over the submitted pool, existing 3-attempt transient-retry policy. Provider-internal retries never create formal repetitions; an unrecoverable formal-call failure records the slot FAILED and stops Phase 2 before evaluator/verdict computation.

## 20. Anti-outcome boundary

`REAL_CASE_RERANKER_CALLS = 0`; `FORMAL_RERANKER_CALLS_EXECUTED = 0`; analyzer/embedding/QA/verifier/judge calls 0; `PHASE1_SELECT_V2_RUNS = 0`; no variance smoke test, no g021 probe, no "just verify" invocation. Gold/required evidence/case role were consumed nowhere in pool, payload, or call-plan construction. **No real-case `DELTA_K`/`CAUSAL_DELTA_K`/`REGRESSION_K`, budget selection, or verdict was computed** — those require Phase-2 outputs. Deterministic pool materialization ≠ outcome exposure: `A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED`.

## 21. Phase-2 execution protocol

All 54 formal calls execute first; raw `ranked_object_ids` persisted per formal slot; no real-case evaluator/DELTA/verdict computation until all 54 slots complete successfully; provider retries accounted separately; identical-pool differences are `RERANKER_VARIANCE_REFERENCE`, never admission effects.

## 22. Lifecycle

```
D3.5-A6              = IN_PROGRESS / BOUNDED_ADMISSION_PROTOTYPE_AND_REPLAY_IMPLEMENTATION_FROZEN
D3.5-A6-PHASE0       = COMPLETE / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FINALIZED
D3.5-A6-PHASE0-R1    = COMPLETE / REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIRED
D3.5-A6-PHASE0-R1-R1 = COMPLETE / CAUSAL_BUDGET_SELECTION_AND_VERDICT_PRECEDENCE_REPAIRED
D3.5-A6-PHASE1       = COMPLETE / BOUNDED_ADMISSION_PROTOTYPE_AND_REPLAY_IMPLEMENTATION_FROZEN
D3.5-A6-PHASE2       = NOT_STARTED / READY_FOR_PAIRED_REPEATED_RERANKER_REPLAY
D3.5                 = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN (unchanged)
D4                   = NOT_STARTED / BLOCKED
```

## 23. Exact next stage

> **D3.5-A6 Phase 2 — Paired Repeated Reranker Replay** — execute the frozen 54 formal slots exactly as planned, persist raw outputs, then run the evaluator stage and the frozen verdict logic. Requires separate explicit authorization; nothing is executed now.
