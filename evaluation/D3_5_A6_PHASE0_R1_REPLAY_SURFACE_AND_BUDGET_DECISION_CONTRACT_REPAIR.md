# D3.5-A6 Phase 0-R1 — Replay-Surface & Budget-Decision Contract Repair

## 1. Executive repair decision

**`A6_PHASE0_R1_DECISION = REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIRED`.** All three preregistration-contract defects found by independent audit are completely repaired in the Phase-0 machine preregistration (`repair_history[].D3.5-A6-PHASE0-R1_REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIR`) and human report, and all accepted Phase-0 architecture is unchanged. This was a narrow contract-repair stage: `evaluation/scripts/`, `src/`, `configs/`, and the replay fixture are unchanged; `REAL_CASE_RERANKER_CALLS = 0`, `REAL_CASE_SELECTIVITY_RUNS = 0`, all model calls 0, DB/Qdrant writes 0.

> **Phase 0-R1-R1 annotation (2026-09-02):** Phase0-R1 fixed the broad benefit/safety split (Repair A/B/C above remain unchanged and closed). Phase0-R1-R1 further closes the remaining causal-selection edge case by moving the stable reserved-required-candidate witness into the budget-eligibility metric itself: budget selection now uses `MECHANISTIC_SAFE_EFFECTIVE(K) = CAUSAL_DELTA_K > 0 AND REGRESSION_K == 0` instead of this report's `SAFE_EFFECTIVE(K) = DELTA_K > 0 AND REGRESSION_K == 0`, and the verdict precedence is extended to 7 levels with `PARTIAL / POOL_PERTURBATION_ASSOCIATED_RECOVERY_WITHOUT_RESERVED_WITNESS` and a narrowed FAIL scope. See `evaluation/D3_5_A6_PHASE0_R1_R1_CAUSAL_BUDGET_SELECTION_AND_VERDICT_PRECEDENCE_REPAIR.md`.

## 2. Parent Phase-0 state

Phase 0 (commit `54ac8ce`) froze the broad A6 architecture: `BASELINE / ADMISSION_K2 / ADMISSION_K3`; `RERANK_POOL_SIZE = 30`; `ADMISSION_BUDGET_CANDIDATES = [2, 3]`; `RERANKER_REPETITIONS_PER_ARM_PER_CASE = 3`; `EXPECTED_FORMAL_RERANKER_CALLS = 54`; `PER_ORIGIN_CAP` remains upstream selectivity-only; origin concentration remains diagnostic-only; `A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED`; `D4 = BLOCKED`. That architecture remains accepted.

## 3. Why Phase-0 needed repair

- **Defect A** — the Phase-0 contract partly conflated the *reranker input payload* with the *post-rerank deterministic selector replay state*; the replay metadata needed to reproduce production post-rerank behavior was not completely specified.
- **Defect B** — the K2/K3 benefit wording alternated between "all evaluator-applicable required evidence groups" and "applicable bridge evidence"; there was no incremental benefit metric, no explicit safety-before-minimality ordering, no causal admission witness, and the PARTIAL labels could overlap.
- **Defect C** — the BASELINE chain read "frozen v2 selectivity → frozen graph merge → frozen fusion" although the persisted `selectivity_only_graph_ordering` is **already** the final v2-conditioned graph-channel ordering — inviting an accidental double merge or an unnecessary `select_v2` rerun.

## 4. Reranker payload surface

`RERANKER_PAYLOAD_SURFACE` = the exact payload submitted to the existing reranker: per candidate `object_id`, `title`, `source_id`, `text[:2000]`, in exact treatment-pool order. It exists only to call the unchanged reranker; no selector-only metadata is added to the model prompt.

## 5. Post-rerank selector replay surface

`POST_RERANK_SELECTOR_REPLAY_SURFACE` is a separate deterministic surface sufficient to reproduce production post-rerank logic exactly: the reranked + fused fallback merge, preferred-source ordering, `symbol_first`, `required_first`, `hinted_first`, `select_final_evidence`, and evidence construction. Per object it must recover `object_id`, `source_id`, `source_version_id`, `object_type`, `title`, selector-visible text, `authority_level`, the **full locator** (the duplicate-locator identity is the canonical JSON dump of the entire locator dict, so no key may be dropped), channel membership, and fusion score; plus the frozen plan fields (`intent`, `target_repositories`, `resolved_versions`, `symbols`, `concepts`, `required_source_types`, `source_budgets`, `paper_page_hints`, raw question text). No required field is left implementation-defined. Model-visible and selector-only fields must be explicitly separated (e.g., `reranker_payload_registry` vs `selector_replay_registry`); the exact Phase-1 schema is free, the semantic separation is frozen now.

## 6. Complete replay object universe

`POST_RERANK_REPLAY_REQUIRED_OBJECT_UNIVERSE` = union of (1) every object in the full v2-conditioned fused ordering; (2) every frozen exact-channel member needed for `symbol_first`; (3) every reserved bridge candidate; (4) every additional object referenced by deterministic final-selector logic before `final_evidence_limit = 12` can be satisfied. Under the frozen fusion construction every channel member receives a fused score and `ordered = dedupe([*reranked, *full_fused_order])` only ever contains fused-ordering members, so the mechanically computed complete superset equals the full fused-ordering member set — computed deterministically per case in Phase 1, never outcome-shaped incremental filling. Coverage is never "rerank top-30 only".

## 7. Selector-visible text semantics

**OPTION A chosen — persist the complete selector-visible frozen text.** Repository inspection shows production consumes full text in three places: `symbol_first` matches plan symbols against exact-channel items' full text (`literal in item['text']`); `_evidence` builds `Evidence.text` from the full payload text; and the frozen evaluator's `title_contains` check searches the evidence item's full text joined with title and `section_path`. **OPTION B (prove `text[:2000]` equivalence) is rejected**: whether a plan symbol or `title_contains` needle occurs beyond character 2000 is data-dependent, so no generic mechanical equivalence proof exists, and assuming equality without proof is prohibited. The reranker model still receives `text[:2000]` only — `RERANKER_PAYLOAD_SURFACE` is unchanged.

## 8. Phase-1 materialization gate

`COMPLETE_REPLAY_SURFACE_MATERIALIZATION_REQUIRED = true`: before any Phase-2 reranker outcome, Phase 1 mechanically materializes the full required replay surface from the frozen normalized corpus and frozen trace state. Gate conditions before implementation freeze: 100% required object coverage; all required selector fields present; source/version identity unchanged; full locator identity unchanged; channel membership reproducible; fusion scores reproducible; exact-channel ordering reproducible; post-rerank deterministic selector replay synthetic/parity tests pass. Runtime `KeyError → add one object → rerun` repair is prohibited; the generic rule replaces the Phase-0 narrow contingency (mechanically materialize **all** missing required replay objects before Phase-2 exposure; no case-specific branch — the g020 `concept.restgas_longitudinal_efficiency` observation remains a disclosed example only).

## 9. Authoritative v2 graph channel

`A6_BASELINE_GRAPH_CHANNEL_AUTHORITY` = `evaluation/d3_5_a5_r2_repaired_selectivity_revalidation.json .six_case_records[case_id].selectivity_only_graph_ordering` — already the final `selected bridge prefix + ordinary unbridged graph + GRAPH_CHANNEL_LIMIT = 20` ordering produced by the frozen v2 implementation. Corrected BASELINE chain: persisted final graph channel (consumed as-is) → frozen fusion with unchanged non-graph channels → full fused ordering (deterministic recomputation, tie-breaking per the existing frozen fusion implementation) → top-30 BASELINE rerank pool. `PHASE1_SELECT_V2_RUNS = 0`; the double graph merge is prohibited; the `merge_ids(selected_object_ids, unbridged_graph_ordering, 20)` reconstruction may be used **only** as an all-six-cases equivalence check — the persisted ordering remains the runtime replay input, and parity failure ⇒ **STOP BEFORE IMPLEMENTATION FREEZE** (no opportunistic representation choice).

## 10. Incremental admission benefit

`DELTA_K` = number of `ADMISSION_APPLICABLE_BRIDGE_GROUP`s that are `STABLE_RETAINED` under treatment K **and not** under BASELINE. `DELTA_2`/`DELTA_3` are the primary admission-benefit counts; `TOTAL_STABLE_RETAINED_K2`/`K3` are diagnostic only. Budget selection is based on incremental benefit + safety, never on total stable retention.

## 11. Benefit vs safety populations

- **Benefit population** = `ADMISSION_APPLICABLE_BRIDGE_GROUP`s — required evidence groups for which the deterministic evaluator identifies ≥ 1 required candidate **and** ≥ 1 such candidate belongs to `RESERVABLE_BRIDGE` for that case. Evaluator-only, classified after pool construction/output freeze, never a runtime input. A required bridge candidate already in `BASELINE_TOP30` consumes zero reservation slots, so its group supports control/retention diagnostics but does not count as incremental reachability created by reserved admission.
- **Safety population** = all evaluator-required/control groups that are `BASELINE_STABLE` — not only admission-target groups. `REGRESSION_K` (material control regressions under budget K, rule unchanged: BASELINE retention ≥ 2 AND treatment ≤ 1) applies to this population.

## 12. SAFE_EFFECTIVE

`SAFE_EFFECTIVE(K) = DELTA_K > 0 AND REGRESSION_K == 0`. This safety filter occurs **before** smallest-budget preference.

## 13. K2/K3 decision hierarchy

```
if K2 is SAFE_EFFECTIVE and K3 is SAFE_EFFECTIVE:
    SELECTED_ADMISSION_BUDGET = 3 if DELTA_3 > DELTA_2 else 2
elif K2 is SAFE_EFFECTIVE:
    SELECTED_ADMISSION_BUDGET = 2
elif K3 is SAFE_EFFECTIVE:
    SELECTED_ADMISSION_BUDGET = 3
else:
    no budget is selected as PASS
```

This implements the **smallest sufficient SAFE budget**, not merely the smallest budget. `DELTA_2 == DELTA_3` with both safe-effective → K2, even if K3 improves median rank or MRR-like diagnostics (rank-only improvement cannot justify K3). Conversely `DELTA_2 == DELTA_3 → K2` is **prohibited** when `REGRESSION_2 > 0 AND REGRESSION_3 == 0` — an unsafe smaller K2 can never win merely because it is smaller; safety is evaluated before budget minimality. The budget is never chosen from positive-case identity.

## 14. Reserved-required-candidate witness

`RESERVED_REQUIRED_CANDIDATE_RETAINED` (evaluator-only): per admission-applicable group/repetition, whether final evidence actually contains a required-evidence matching candidate that consumed a reserved slot in that treatment arm. `STABLE_RESERVED_REQUIRED_WITNESS` = retained in ≥ 2/3 repetitions. **PASS requires** at least one admission-applicable group with `DELTA_K` benefit **and** this stable witness under the selected budget; without the witness, direct bridge-admission recovery is not claimed. Improvement not carried by an actually reserved required candidate is `POOL_PERTURBATION_ASSOCIATED_RECOVERY` — diagnostic only, never sufficient for the mechanistic PASS requirement.

## 15. Verdict precedence

Frozen deterministic total order, no outcome-dependent label selection:

```
1. INVALID
2. FAIL / construction-or-safety invariant failure
3. PASS if a SAFE_EFFECTIVE budget exists and the required stable reserved-candidate witness exists
4. PARTIAL / ADMISSION_RECOVERY_WITH_CONTROL_REGRESSION   (DELTA_K > 0 exists but no effective budget is safe)
5. PARTIAL / ADMISSION_RECOVERY_NOT_STABLE_ACROSS_RERANKER_REPETITIONS
   (no stable DELTA_K but UNSTABLE_ADMISSION_RECOVERY: an admission-applicable group
    recovered in >= 1 individual treatment repetition relative to baseline)
6. PARTIAL / ADMISSION_DID_NOT_VALIDATE_DOWNSTREAM_RECOVERY   (otherwise)
```

`UNSTABLE_ADMISSION_RECOVERY` is defined precisely (retained in ≥ 1 treatment repetition where the corresponding baseline repetition/stable baseline state does not establish stable retention, without satisfying `DELTA_K` stable recovery) so isolated reranker variance is never confused with stable treatment effect.

## 16. Anti-tuning preservation

The Phase-0 read-only fusion/payload probe remains what it was — deterministic frozen-trace feasibility inspection, never an experiment (`REAL_CASE_RERANKER_CALLS = 0`, `REAL_CASE_SELECTIVITY_RUNS = 0`). No origin threshold, admission scorer, K change, repetition change, or case-specific branch was introduced. Protected datasets remain `novel_validation = FROZEN / UNSEEN`, `novel_holdout = SEALED / UNSEEN`.

## 17. Lifecycle

```
D3.5-A6           = IN_PROGRESS / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_REPAIRED_AND_FROZEN
D3.5-A6-PHASE0    = COMPLETE / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_REPAIRED_AND_FROZEN
D3.5-A6-PHASE0-R1 = COMPLETE / REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIRED
D3.5-A6-PHASE1    = NOT_STARTED / READY_TO_IMPLEMENT
D3.5-A6-PHASE2    = NOT_STARTED / BLOCKED_UNTIL_PHASE1_FREEZE
D3.5              = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN (unchanged)
D4                = NOT_STARTED / BLOCKED
```

## 18. Exact next stage

> **D3.5-A6 Phase 1 — Bounded Admission Prototype & Synthetic Construction Freeze** — may materialize the complete replay surface mechanically, extend replay metadata generically, implement deterministic pool construction, post-rerank replay logic, diagnostics, synthetic/parity tests, and the formal runner skeleton — with `REAL_CASE_RERANKER_CALLS = 0` and `PHASE1_SELECT_V2_RUNS = 0` throughout, and the complete-replay-surface gate passed before implementation freeze.
