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
frozen A5-R2 v2 selectivity (frozen selectivity_only_graph_ordering per case)
→ frozen graph merge (selected bridge candidates as graph-channel prefix,
  then ordinary unbridged graph candidates, graph_channel_limit = 20)
→ frozen fusion (weights exact 2.0 / dense 1.0 / sparse 1.0 / paper 1.15 /
  workflow 1.2 / graph 0.8; score = weight/(60+rank+1); non-graph channels
  unchanged from the frozen STRUCTURED_BRIDGED cell trace)
→ ordinary fused top-30 rerank pool
```

No reserved admission. **BASELINE is NOT** A2 STRUCTURED_BRIDGED (old 20-cap bridge), A5 v1, LEGACY, or ABLATION — the A6 scientific contrast is admission on top of repaired v2 selectivity. A Phase-0 read-only fusion probe confirmed this construction is deterministic: the same fusion code path reproduces the frozen `baseline_fused_ordering_full` top-30 exactly for all six cases when fed the old graph channel.

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

`DEFAULT_BUDGET_PREFERENCE = K2` (fewer ordinary candidates displaced). Across all evaluator-applicable required evidence groups, with `S2`/`S3` = applicable groups `STABLE_RETAINED` by K2/K3:

- `S2 == S3` → prefer K2;
- `S3 > S2` and K3 adds no `MATERIAL_CONTROL_REGRESSION` relative to K2 → prefer K3;
- `S3 > S2` but K3 introduces additional material regression → do not automatically prefer K3; verdict becomes PARTIAL / tradeoff;
- `S2 > S3` → prefer K2.

If `S2 == S3` and K3 only improves median rank / MRR-like diagnostics, `SELECTED_ADMISSION_BUDGET = 2` — rank quality alone never justifies the extra displaced slot. The budget is never chosen from positive-case identity.

## 18. Origin concentration diagnostics

Carried forward exactly: `selected_bridge_origin_count`, `selected_bridge_per_origin_counts`, `reserved_bridge_origin_count`, `reserved_bridge_per_origin_counts`, `ordinary_rerank_candidates_displaced`, `reserved_bridge_candidate_ids`, `reserved_candidate_origin_ids`. **Diagnostic-only**: no numeric failure threshold (never derived from g020's v2 `origins_after = 2` or the 4+4 attribution); A6 does not modify admission to enforce diversity; the v2 `PER_ORIGIN_CAP = 4` remains the selectivity-stage guard and no new per-origin admission cap is added — A6 tests its downstream consequence. Per treatment pool: `baseline_pool_object_ids`, `reserved_bridge_candidate_ids`, `baseline_overlap_bridge_ids`, `ordinary_rerank_candidates_displaced`, `displaced_object_ids`, `treatment_pool_object_ids`, `pool_size`, `pool_fingerprint`. Per reserved candidate: `object_id`, `source_id`, `source_version_id`, v2 selectivity position, `attributed_origin_id`, `already_in_baseline`, `reserved_slot_consumed`.

## 19. Anti-tuning boundary

Phase 0 made `REAL_CASE_RERANKER_CALLS = 0`: no "just to verify" treatment-pool run, no real-case baseline smoke test, no single-call variance probe — synthetic construction tests belong to Phase 1. K, repetition count, material-regression threshold, pool order, and decision semantics were frozen from generic criteria and are never tuned from exposed A5/R2 result details; g020's origin concentration may motivate required diagnostics only. Runtime admission and reranker construction consume no case role, positive/control label, or required evidence; case-role metadata may be used only for post-output scientific interpretation.

## 20. Outcome-exposure boundary

`A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED` until the **first real-case reranker call starts** — not when a result is persisted and not when a human reads it (PERSISTED_RESULT_EXPOSURE and HUMAN_RESULT_INSPECTION are later layers, per the corrected R2 semantics).

## 21. Verdict matrix

| Verdict | Condition |
|---|---|
| `PASS / BOUNDED_RERANK_ADMISSION_VALIDATED_FOR_DEVELOPMENT` | all of: protocol valid; exact preregistered arms executed; repetition protocol valid; candidate-authority invariants pass; pool-size/displacement invariants pass; ≥ 1 treatment budget gives additional stable retention of applicable bridge evidence over BASELINE; selected budget has no `MATERIAL_CONTROL_REGRESSION`; no runtime gold/case-role leakage; no post-exposure treatment mutation. Both arms PASS with `S2 == S3` → `SELECTED_ADMISSION_BUDGET = 2`; budget 3 only when `S3 > S2` with no additional material regression |
| `PARTIAL / ADMISSION_RECOVERY_WITH_CONTROL_REGRESSION` | additional stable retention exists but every otherwise-preferred effective treatment introduces material control regression; incomplete for downstream activation |
| `PARTIAL / ADMISSION_DID_NOT_VALIDATE_DOWNSTREAM_RECOVERY` | valid treatment pools, but neither K2 nor K3 improves stable applicable retention over BASELINE |
| `PARTIAL / ADMISSION_RECOVERY_NOT_STABLE_ACROSS_RERANKER_REPETITIONS` | recovery appears in one repetition but fails the ≥ 2/3 stability criterion |
| `FAIL / BOUNDED_ADMISSION_SAFETY_OR_CONSTRUCTION_FAILED` | pool-size invariant, duplicate-admission accounting, out-of-scope admission, candidate-authority violation, systematic control degradation, or implementation/preregistration mismatch — while the protocol remains interpretable |
| `INVALID` | reranker outcome seen before prereg freeze; K/repetition/decision rule changed after exposure; unregistered budget arm; gold/required evidence in pool construction; case-role branch in admission; reranker prompt/model/config changed during the experiment; outcome-guided reruns |

Identical pool fingerprints between a treatment and BASELINE mean identical reranker inputs: any output difference is `RERANKER_VARIANCE_REFERENCE`, never admission effect; admission effect is interpretable only when the fingerprints differ.

## 22. What A6 validates

Whether a very small reserved admission budget (2 or 3 of 30 rerank slots) lets already-selected governed bridge evidence compete in the **existing unchanged reranker** and achieve stable downstream evidence retention, under symmetric reranker-variance accounting, without material control regressions — a development-stage bounded admission mechanism.

## 23. What A6 does not validate

QA answer quality; production readiness (`PRODUCTION_ACTIVATION = false` even on PASS); a D4 start; reranker replacement; fusion-weight changes; generalization beyond the six exposed development cases (`POST_OUTCOME_MECHANISTIC_DEVELOPMENT`, never a fresh holdout).

## 24. Phase-1 contract

> **D3.5-A6 Phase 1 — Bounded Admission Prototype & Synthetic Construction Freeze**

Phase 1 may implement the deterministic BASELINE/K2/K3 pool construction, diagnostics, synthetic tests, and the formal runner **without executing real reranker calls** (`REAL_CASE_RERANKER_CALLS = 0`), then freeze the implementation. One anticipated mechanical task is recorded generically: the frozen payload registry covers the union of the old-cap fused top-30 and all bridge candidates, while v2 conditioning re-admits previously displaced ordinary graph candidates; the Phase-0 read-only probe found exactly one v2-conditioned top-30 member absent from the registry (`concept.restgas_longitudinal_efficiency`, g020; all other cases complete). If any arm's pool contains an unregistered candidate, Phase 1 must mechanically extend the registry additively from the frozen normalized corpus under the unchanged index-identity check, documented before any reranker outcome — a descriptive payload-availability repair, not a treatment or semantics change. The fixture itself is unchanged in Phase 0.

## 25. Phase-2 contract

> **D3.5-A6 Phase 2 — Paired Repeated Reranker Replay**

Only after the Phase-1 implementation freeze may the 54 formal reranker calls run. Phases 1 and 2 must not be merged unless explicitly authorized later.

## 26. Lifecycle

```
D3.5-A6         = IN_PROGRESS / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FROZEN
D3.5-A6-PHASE0  = COMPLETE / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FROZEN
D3.5-A6-PHASE1  = NOT_STARTED / READY_TO_IMPLEMENT
D3.5-A6-PHASE2  = NOT_STARTED / BLOCKED_UNTIL_PHASE1_FREEZE
D3.5-A5-R2      = COMPLETE / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT (unchanged)
D3.5            = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN
D4              = NOT_STARTED / BLOCKED
```

Execution accounting: real-case reranker calls 0; real-case selectivity runs 0; real-case treatment-pool constructions 0; analyzer/embedding/QA/verifier/judge calls 0; PostgreSQL/Qdrant writes 0; novel_validation/holdout untouched and unsealed-state unchanged; `src/`/`configs/`/fixture/A5-R2 artifacts unchanged. Protected datasets: `novel_validation = FROZEN / UNSEEN`, `novel_holdout = SEALED / UNSEEN`.

## 27. Exact next task

> **D3.5-A6 Phase 1 — Bounded Admission Prototype & Synthetic Construction Freeze** — deterministic pool construction, diagnostics, synthetic tests, formal runner without real reranker calls; Phase 2 (the 54 formal calls) remains blocked until the Phase-1 freeze.
