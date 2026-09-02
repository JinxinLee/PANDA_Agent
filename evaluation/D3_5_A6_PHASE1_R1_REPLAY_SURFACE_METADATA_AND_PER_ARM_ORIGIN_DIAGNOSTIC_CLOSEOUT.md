# D3.5-A6 Phase 1-R1 — Replay-Surface Metadata & Per-Arm Origin Diagnostic Closeout

## 1. Executive decision

**`A6_PHASE1_R1_DECISION = REPLAY_SURFACE_METADATA_AND_PER_ARM_ORIGIN_DIAGNOSTICS_CLOSED`.** Both audit-quality inconsistencies are repaired with proven semantic neutrality: the Phase-1 scientific implementation is unchanged (18/18 pool identities, reserved/displaced IDs, identical-pool relations, 54/54 execution-plan entries, reranker payloads, decision logic, and replay semantics all verified identical), the execution manifest required **zero change**, and `A6_PHASE1_R1_DECISION` closes the narrow scope. `PHASE2_SCIENTIFIC_READINESS = YES`, `PHASE2_AUDIT_READINESS = YES`, `A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED`.

## 2. Parent state

Starting HEAD `b26b2d74` = the Phase-1 implementation freeze. `A6_PHASE1_DECISION = BOUNDED_ADMISSION_PROTOTYPE_AND_REPLAY_IMPLEMENTATION_FROZEN` is accepted and unchanged: graph parity 6/6, fusion replay parity 6/6, `PHASE1_SELECT_V2_RUNS = 0`, replay coverage 100% with 0 missing objects, 18 formal arm pools with 0 invariant violations, reserved slots (g036 K2=2/K3=3, g021 1/1, controls 0/0, g020 2/3), identical-pool semantics (g021 K2≡K3; controls all-equal), 54 `NOT_EXECUTED` call-plan entries, 0 reranker calls.

## 3. Repair A — corrected replay-surface metadata model

The implementation stores static object metadata in `selector_replay_registry[object_id]` (`object_id, source_id, source_version_id, object_type, title, complete selector-visible frozen text, authority_level, complete raw locator dict`) and per-case selector state separately (`case["channel_membership"]`, `case["full_fused_ordering"]` / fused score map, `exact_channel_ordering`, frozen plan fields, raw question). The earlier artifact/report wording implied each registry entry also contained channel membership and fusion score. The corrected authoritative description is:

```
POST_RERANK_SELECTOR_REPLAY_SURFACE
= STATIC_OBJECT_METADATA_SURFACE
  + PER_CASE_SELECTOR_STATE_SURFACE
```

The implementation was already correct — it reconstructs replay as `payload_map` (static registry) + `score_map` (per case) + `channel_map` (per case) — so **no fields were moved**, no registry entry was changed, and only the metadata/report schema description was corrected. `fields_moved_into_registry_entries = false`; `implementation_effect = NONE`.

## 4. Repair B — per-arm reserved-origin diagnostics

The pre-R1 case-level summary collapsed K2/K3 into a union-like `reserved_bridge_origin_count` plus a K3-based per-origin table. The repaired schema materializes explicit per-arm summaries:

```
origin_concentration_diagnostics:
  selected_bridge_origin_count / selected_bridge_per_origin_counts   (case-level, from A5-R2)
  reserved_by_arm:
    ADMISSION_K2: { reserved_bridge_origin_count, reserved_bridge_per_origin_counts, reserved_candidate_origin_ids }
    ADMISSION_K3: { ... }
  ordinary_rerank_candidates_displaced: { ADMISSION_K2, ADMISSION_K3 }
```

Derivation is purely mechanical: per arm, the distinct-count / frequency table / ordered list of `attributed_origin_id` among that arm's frozen reserved candidates; zero-reservation arms yield `0 / {} / []`. No scoring, no re-attribution, no evaluator outcome, no case-role branch, no gold evidence, no thresholds, no diversity enforcement — and the K2 summary is never implicitly the K3 summary.

## 5. Mechanically verified examples (from the frozen manifest)

| Case | Arm | Reserved origin IDs | Count | Per-origin |
|---|---|---|---|---|
| g036 | K2 | `edge.a767…`, `edge.a767…` | 1 | `a767`: 2 |
| g036 | K3 | `edge.a767…`×2, `edge.2e096…` | 2 | `a767`: 2, `2e096`: 1 |
| g021 | K2 / K3 | `edge.ea3a…` | 1 / 1 | `ea3a`: 1 |
| g020 | K2 | `edge.ea3a…`, `edge.8127…` | 2 | `ea3a`: 1, `8127`: 1 |
| g020 | K3 | `edge.ea3a…`×2, `edge.8127…` | 2 | `ea3a`: 2, `8127`: 1 |
| controls | K2/K3 | — | 0 | {} |

None of these observed counts is turned into a failure threshold; concentration remains diagnostic-only.

## 6. Implementation-fidelity wording precision

The Phase-1 parity label was stronger-sounding than its evidence. The precise classification is now:

```
POST_RERANK_IMPLEMENTATION_FIDELITY =
PASS / PRODUCTION_CORE_REUSE_PLUS_SOURCE_ANCHORED_WRAPPER_MIRROR
```

claiming exactly: production `select_final_evidence`/`_source_type_of` imported directly; the surrounding deterministic wrapper mirrored in evaluation code with key production expressions source-anchored; synthetic behavioral tests covering movement/dedupe/caps/determinism; fusion replay anchored 6/6; replay determinism 12/12. **No full independent production-wrapper output-equality claim** is made (no such test exists; the A2 model outputs were not persisted). This is a wording precision repair, not a scientific downgrade.

## 7. Invariance verification

Pre/post snapshot comparison over the regenerated pool manifest: scientific fields identical for **18/18** arm manifests (ordered pool IDs, reserved candidate IDs, displaced IDs, slot counts, overlap/reservable lists, identical-pool relations). `evaluation/d3_5_a6_phase1_execution_manifest.json` required **zero change** — all 54 entries (`formal_call_index`, `case_id`, `repetition`, `arm`, `ordered_pool_object_ids`, `ordered_reranker_payload`, `pool_size`, `pool_identity`, `model_contract_reference`, `outcome_status`) and the model contract byte-identical. Decision logic (`compute_delta`, `compute_causal_delta`, `mechanistic_safe_effective`, `select_budget`, `material_control_regression`, `classify_unstable_recovery`, `compute_verdict`, `stable_reserved_required_witness`, `admission_applicable_bridge_groups`) and replay logic (`post_rerank_replay`, `replay_case_with_registry`, `replay_case`, production `select_final_evidence`, `_source_type_of`) untouched. The Phase-1 script change is confined to the diagnostic summarization block plus the new pure helper — `POOL_CONSTRUCTION_EFFECT = CALL_PLAN_EFFECT = REPLAY_EFFECT = DECISION_LOGIC_EFFECT = NONE`, proven by the snapshot comparison.

## 8. Focused tests

35 pytest tests passing (32 prior + 3 new): synthetic per-arm summaries (`[]` → 0/{}/[]; `[A,A]` → 1/{A:2}; `[A,A,B]` → 2/{A:2,B:1}), purity of the diagnostic derivation (cannot mutate reserved candidate IDs or pool ordering), and an integrated case verifying the explicit per-arm `reserved_by_arm` structure in `build_case_pools` output. No full suite, no formal calls, no provider APIs, no `select_v2`.

## 9. Execution accounting and lifecycle

`REAL_CASE_RERANKER_CALLS = 0`; `FORMAL_RERANKER_CALLS_EXECUTED = 0`; `PHASE1_SELECT_V2_RUNS = 0`; analyzer/embedding/QA/verifier/judge calls 0; PostgreSQL/Qdrant writes 0; novel_validation/holdout untouched and unopened. `A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED`.

```
D3.5-A6              = IN_PROGRESS / BOUNDED_ADMISSION_PROTOTYPE_AND_REPLAY_IMPLEMENTATION_FROZEN
D3.5-A6-PHASE0       = COMPLETE / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FINALIZED
D3.5-A6-PHASE0-R1    = COMPLETE / REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIRED
D3.5-A6-PHASE0-R1-R1 = COMPLETE / CAUSAL_BUDGET_SELECTION_AND_VERDICT_PRECEDENCE_REPAIRED
D3.5-A6-PHASE1       = COMPLETE / BOUNDED_ADMISSION_PROTOTYPE_AND_REPLAY_IMPLEMENTATION_FROZEN
D3.5-A6-PHASE1-R1    = COMPLETE / REPLAY_SURFACE_METADATA_AND_PER_ARM_ORIGIN_DIAGNOSTICS_CLOSED
D3.5-A6-PHASE2       = NOT_STARTED / READY_FOR_PAIRED_REPEATED_RERANKER_REPLAY
D4                   = NOT_STARTED / BLOCKED
```

## 10. Exact next stage

> **D3.5-A6 Phase 2 — Paired Repeated Reranker Replay** — execute the frozen 54 formal slots exactly as planned, persist raw outputs per slot, then run the evaluator stage and the frozen verdict logic. Requires a separate explicit authorization; Phase1-R1 does not start it.
