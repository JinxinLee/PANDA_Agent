# PANDA Agent — D4-A3: First-Batch Runtime Migration Closeout Report

## 1. Executive Summary & Authoritative Status

```text
D4-A2-V2: COMPLETE / PASS / CONTROLLED_SHARED_PLAN_T2_VALIDATED (AUTHORITATIVE VIA D4-A2-V2-R3)
D4-A3: COMPLETE / PASS / FIRST_BATCH_RUNTIME_MIGRATION_ACTIVATED

FIRST_BATCH_RUNTIME_MIGRATION = ACTIVE
BATCH1_MIGRATED_RULES = event_poca_handoff, restgas_profile_workflow
BATCH1_FIXED_LOCATORS_REMOVED = 10 components
PRODUCTION_ACTIVATION = true
D4_OVERALL_STATUS = IN_PROGRESS / INCREMENTAL_QUERY_EXPANSION_MIGRATION
NEXT_BATCH_STATE = NOT_STARTED / SEPARATELY_GOVERNED
```

This closeout report documents the complete production activation of the **D4-A3 First-Batch Runtime Migration**. Following the authoritative acceptance of D4-A2-V2-R3 (`PASS / CONTROLLED_SHARED_PLAN_T2_VALIDATED`), the first batch of hard-coded query expansion shortcuts has been transitioned from evaluation prototype into standard runtime behavior in `src/panda_agent`.

---

## 2. Why Migration Was Authorized

Under the D4 Query Expansion Generalization Program:
1. **Scientific Validation Basis**: In D4-A2-V2-R3 (parent commit `8c0971f20f9a2b2680451e3123fa1d95325816bc`), prospective shared-plan T2 validation proved that:
   - Target evidence replacement reproduced 2/2 across both migrated targets.
   - Batch 1 dependency removal was identifiable and demonstrated 2/2.
   - 0 shared-plan critical regressions occurred.
   - 0 grounding regressions, 0 version violations, and 0 invalid provenance recoveries were observed.
   - All six primary metric deltas were strictly zero (no degradation in recall@5, recall@10, recall@20, candidate recall, final evidence recall, or critical final evidence recall).
2. **Authorization Boundary**: R3 PASS established eligibility. The user separately and explicitly authorized this D4-A3 runtime activation; validation alone did not authorize it.

---

## 3. The 10 Fixed Locator Components Removed

The Batch 1 migration removed exactly **10 hard-coded fixed-locator components** across two target query expansion rules in `configs/query_expansions.yaml`:

### Rule 1: `event_poca_handoff` (5 components removed)
- **Symbols removed (4)**:
  1. `macro/target/ana_dpm.C`
  2. `macro/target/prod_aod_complete.C`
  3. `POCA_VERTEX_FILE`
  4. `PndPidCorrelator`
- **Paper page hints removed (1)**:
  5. `li_2026: [131, 138]`

### Rule 2: `restgas_profile_workflow` (5 components removed)
- **Symbols removed (5)**:
  1. `pgenerators/Target/PndTargetGenerator.cxx`
  2. `macro/target/prod_sim_hvmaps.C`
  3. `macro/target/reco_complete.C`
  4. `macro/target/ana_complete.C`
  5. `macro/target/correction/efficiency_correction_2.C`
- **Paper page hints removed (0)**: None existed.

**Total components removed**: 4 + 1 + 5 = **10 components**.

---

## 4. Preserved Vocabulary and Scoping

The migration did **not** delete these rules or strip their semantic routing vocabulary. Both rules retain their full query matching triggers, repository scopes, and conceptual descriptors:

### `event_poca_handoff`
- **Triggers**: `event_poca`, `poca_vertex_file`, `second-pass pid`, `第二遍 pid`
- **Repositories**: `restgas_determination`, `pandaroot`
- **Concepts**: `event POCA handoff`, `event-aligned second-pass propagation`
- **Symbols**: `[]` (migrated to structured replacement)
- **Structured Replacement**: `true`

### `restgas_profile_workflow`
- **Triggers**: `restgas_profile`, `restgas profile`, `corrected rho`, `修正后的 rho`
- **Repositories**: `restgas_determination`, `pandaroot`
- **Concepts**: `distributed target generation`, `longitudinal profile correction`
- **Symbols**: `[]` (migrated to structured replacement)
- **Structured Replacement**: `true`

No changes were made to the shared terminology in non-Batch-1 rules. Files that happen to appear in other query expansion rules remain intact there; Batch 1 scope was strictly enforced.

---

## 5. Generic Structured Replacement Path in Production

Prior to D4-A3, `Retriever.retrieve(question)` lacked the complete governed D4 treatment pipeline by default. The validated mechanism has now been productionized cleanly under `src/panda_agent`:

1. **Production Activation Marker**:
   - Added `structured_replacement: bool = False` to `QueryExpansionRule` in `src/panda_agent/config.py`.
   - In `configs/query_expansions.yaml`, only `event_poca_handoff` and `restgas_profile_workflow` have `structured_replacement: true`.
   - The query analyzer records matched migrated rule IDs into `RetrievalPlan.analysis_diagnostics["structured_replacement_rules"]`.
2. **Default Runtime Execution**:
   - External callers simply invoke `Retriever.retrieve(question)` without passing `d3_config` or experimental flags.
   - Ordinary RRF fusion across standard channels (`exact`, `dense`, `sparse`, `paper`, `workflow`, `graph`) is computed first, establishing the baseline candidate ordering.
   - When a matched rule requests structured replacement, `Retriever.retrieve()` automatically invokes the governed structured bridge via `build_structured_contribution_from_storage(...)`.
   - Candidates pass through `d3_5_selectivity_v2` and enter the 30-slot rerank pool through K=3 bounded admission.
3. **Auditable Diagnostic Receipt**:
   - When active, the retrieval result contains `"structured_replacement"` recording active rule IDs, resolution receipts, reachability counts, eligible candidates, selected IDs, reservable IDs, reserved IDs, displaced ordinary baseline IDs, and final rerank pool IDs.

---

## 6. Selectivity-v2 and Bounded Admission K=3 Mechanics

The productionized algorithms in `src/panda_agent/d3_structured.py` strictly preserve the frozen contracts from D3.5-A5 and D3.5-A6:

### Selectivity-v2 (`d3_5_selectivity_v2`)
- **Caps**: `SELECTIVITY_CAP = 8`, `PER_ORIGIN_CAP = 4`, `MIN_PRIMARY_SCORE = 1`.
- **Hard Filters**: Governed candidate universe, RetrievalPlan repository/source scope compatibility (fail-closed), lexical gate (path/title overlap >= 1).
- **Ranking Hierarchy**:
  1. `symbol_exact_tier` descending
  2. `rarity_weighted_overlap` descending (universe-local IDF: `idf(t) = log2((|U|+1)/(df(t)+1))`)
  3. `basename_coverage` descending
  4. `text_presence` descending
  5. `support_rank` ascending (non-graph channel support)
  6. `structural_distance` ascending
  7. `candidate_object_id` ascending (deterministic lexical tie-break)
- **Origin Attribution**: Least-used eligible provenance origin (tie: lexical origin ID).

### Bounded Admission K=3
- **Baseline Pool**: `fused_order[:30]` (ordinary RRF).
- **Reservable**: Selected structured candidates not already present in `baseline_pool`.
- **Reservation**: At most `min(3, len(reservable))` candidates reserved in frozen v2 selectivity order.
- **Displacement**: Exactly the bottom ordinary baseline candidates are displaced (bottom-first positional cut).
- **Invariants**:
  - Pool size is bounded by 30.
  - Zero duplicate candidates.
  - No new RRF channel or modified channel weights.
  - Reranker call count remains exactly one per retrieval.

---

## 7. Non-Batch 1 Invariance & Absence of Dual-Mode Fallbacks

- **Zero Dual-Mode Runtime Fallback**: No runtime fallback switches or dual-path fallbacks were added for rollback. The codebase maintains a single clean production path. Rollback is governed strictly by Git.
- **Non-Batch 1 Untouched**: All 52 non-migrated rules in `configs/query_expansions.yaml` retain their exact configuration and `structured_replacement: false`.
- **Explicit Historical Arms Preserved**: Existing D3/D3.5 experimental configurations (`d3_config`) remain intact for backward compatibility and do not interfere with the production default path.

---

## 8. Focused Verification Performed

Comprehensive unit tests were implemented in `tests/unit/test_d4_a3_batch1_runtime_migration.py` covering all 29 verification requirements and semantic parity checks:

| Verification Group | Requirements | Tests | Status |
| :--- | :--- | :--- | :--- |
| **Config Migration** | Req 1–6 | 6 tests | **PASS** |
| **Production Policy & Activation** | Req 7–10 | 4 tests | **PASS** |
| **Selectivity-v2 Semantics** | Req 11–15 | 5 tests | **PASS** |
| **Admission-K3 Semantics** | Req 16–21 | 6 tests | **PASS** |
| **Runtime Integration** | Req 22–26 | 9 tests | **PASS** |
| **Anti-Shortcut Invariants** | Req 27–29 | 3 tests | **PASS** |
| **Frozen Algorithm Parity** | Section 19 | 5 tests | **PASS** |
| **Total Focused Suite** | **All 29 Requirements** | **38 tests** | **PASS (38/38)** |

In addition, the entire focused test suite (`test_d4_a3_batch1_runtime_migration.py`, `test_retrieval.py`, `test_retrieval_trace.py`, `test_d3_structured_shortcut.py`, `test_d3_5_structured_bridge.py`, `test_config.py`) passed cleanly: **134 passed, 7 subtests passed in 5.19s**.

`git diff --check` confirmed zero whitespace or formatting errors.

---

## 9. Rollback Boundary & Git Discipline

- **Starting Parent Commit**: `8c0971f20f9a2b2680451e3123fa1d95325816bc` (`D4-A2-V2-R3 close evaluator contract repair`).
- **Rollback Boundary**: To revert this migration, revert the single final migration commit to return the repository to HEAD `8c0971f20f9a2b2680451e3123fa1d95325816bc`.
- **Working Tree State**: This artifact belongs to the single migration commit `D4-A3 activate first-batch runtime migration`, whose direct parent is the starting boundary above. The controller performs read-only Git verification after committing.

---

## 10. Next Lifecycle State & Scope Guard

- **Batch 1 Runtime Migration**: **ACTIVE**.
- **Batch 2 Status**: **NOT STARTED**.
- **Lifecycle Directive**: D4-A3 activation is complete. No additional query expansions are classified or migrated. No scientific evaluations, benchmarks, or novel holdout runs are initiated. Controller acceptance is based on focused offline checks. No subsequent batch starts.

## 11. Controller Verification and Limitations

The controller corrected the receipt vocabulary, verified every non-Batch-1 rule against the starting Git blob, and strengthened tests for real analyzer code with provider stubs, the default retrieval entry, external normal plans, current policy switches, and selectivity rank/receipt parity. The production analyzer prompt context was preserved. An unnecessary database-refetch fallback was removed; all eligible payloads come from governed bridge materialization, including candidates beyond the old injection cap.

Changed Python files passed compile/AST checks. Exact source comparison confirmed unchanged ordinary RRF, historical D3/D3.5 treatment, reranker payload/schema/call, and final selector AST. The first added integration fixtures lacked required schema fields (4 test failures); those fixtures were corrected before the final passing runs. A pytest cache permission warning was avoided by disabling caching.

PANDA scientific/provider calls, provider tokens, database/Qdrant writes, and benchmark/novel runs were all zero. AGY coding delegation is separate; its token consumption was not measured. No live runtime or new scientific evaluation was performed, so activation relies on the prior R3 scientific basis plus offline implementation verification.

Selectivity reads canonical source-native bridge payloads even if ordinary retrieval already contains the same object with different projected text. The overlap test confirms canonical text scoring and zero extra admission slots. Final controller run: 134 tests and 7 subtests passed (38 migration tests included).
