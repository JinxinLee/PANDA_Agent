# D3.5-A1 — Bounded Structured Evidence-Link Bridging Prototype (R1 Repaired)

## 1. Executive Summary & Checkpoint Status

| Item | Value |
|---|---|
| **Checkpoint** | `D3.5-A1-R1` |
| **Status** | `REPAIRED / AWAITING_R2_GOVERNANCE_AND_ISOLATION` |
| **Base Commit** | `d84b3c0fe7ffe4bd894990077a20651165cdcfdf` |
| **Preregistration Identity** | `evaluation/d3_5_a0_structured_evidence_link_design.json` (D3.5-A0-R2) |
| **Runtime Implementation Status** | Fully repaired and verified via comprehensive T0 unit/synthetic tests (35 tests PASS) |
| **D1 Repository Identity** | `24` objects / `16` accepted relations / `1` curated workflow step (Unchanged) |
| **Mechanism-C Outcome** | `PENDING_R2_GOVERNANCE_DISPOSITION` (`D3_5_A1_REPOSITORY_D1_CHANGED = false`) |
| **Production Structured-State Writes** | `0` (Deployed production database completely untouched) |

---

## 2. R1 Contract Defect Repairs

Four implementation-contract defects identified during audit have been repaired:

1. **Historical D3 vs D3.5 Arm Separation**:
   - Historical D3 (`D3Arm` / `D3ExperimentConfig`) maintains the frozen 7 rules (`lmd_fit_data_chain`, `event_poca_handoff`, `pid_two_pass_files`, `model_factory_theory`, `effective_acceptance_pipeline`, `restgas_profile_workflow`, `root_macro_usage`).
   - D3.5 (`D3_5Arm` / `D3_5ExperimentConfig`) manages the 2 focused rules (`event_poca_handoff`, `restgas_profile_workflow`).
   - The remaining 5 rules remain active background rules across all four D3.5 arms (`LEGACY`, `ABLATION`, `STRUCTURED_UNBRIDGED`, `STRUCTURED_BRIDGED`).
2. **Restoration of Unbridged Structured Baseline**:
   - `derive_unbridged_structured_seeds` preserves pre-A1 behavior: no 8-seed cap, admits all unique Tier G/S/D seeds, and admits all Tier-D ambiguity candidates without atomic budget constraints.
   - D3.5 bridge independently uses `derive_d3_5_bridge_seeds` (cap 8, atomic ambiguity constraint).
3. **Genuine Additive Bridge Composition**:
   - `STRUCTURED_BRIDGED` composes bridged candidates on top of the unbridged graph baseline (`unbridged_graph = merge_exact_streams(candidates, ordinary_graph)`).
   - Exact zero-bridge equivalence: when bridge produces 0 candidates, the `STRUCTURED_BRIDGED` graph channel exactly matches `STRUCTURED_UNBRIDGED`.
   - Prefix displacement is measured relative to `unbridged_graph`.
4. **Governed Source Qualification for Evidence Paths**:
   - `evidence_paths` requires explicit governed `evidence_source_ids` intersecting allowed plan/context scope; missing `evidence_source_ids` fails closed with `GOVERNED_PROVENANCE_INVALID` and reason `"evidence path lacks explicit governed source qualification"`.
   - `evidence_object_ids` performs exact indexed lookup without requiring `evidence_source_ids`.

---

## 3. Mechanism Implementation Details

### Mechanism A: Governed Structural Reachability
- **Seed Derivation & Priority**: Unique seeds admitted in authority order (`Tier G` -> `Tier S` -> `Tier D unique`). Excludes `UNRESOLVED`, `RESOLVED_MULTIPLE`, `SAME_AS`, and `whole_question_fallback`.
- **Atomic Tier-D Ambiguity Rule**: Tier-D ambiguity sets are evaluated atomically. If size $\le 8$ and fits remaining shared seed budget (cap 8), all seeds are admitted; otherwise none are admitted from that branch, and `AMBIGUITY_SET_EXCEEDS_SAFE_SEED_BUDGET` / `STRUCTURAL_PATH_AMBIGUOUS` is emitted.
- **Phased Typed Traversal per Root-to-Provenance Path**:
  - Phase 1: Up to 8 eligible seeds.
  - Phase 2: Upward `parent_object_id` containment context (0 or 1 child-to-parent transition with containment compatibility; parent-to-child fan-out prohibited).
  - Phase 3: Semantic reachability (0 or 1 accepted relation OR 1 curated workflow step; mutually exclusive per path; path budget consumed $\le 2$).
  - Predicate Endpoint Compatibility: Generic semantic type families (`_PROCESS_TYPES`, `_DATA_PRODUCT_TYPES`, `_CONCEPT_TYPES`, `_DOCUMENT_TYPES`, `_REPOSITORY_TYPES`, `_CONFIGURATION_TYPES`) strictly gate relation traversal.
  - Repository Provenance: `FORKED_FROM` requires explicit check that both repository endpoints and version locks are within RetrievalPlan/context scope (forward-only).
  - Global Reachable Structure Cap: Capped at 32 reachable structures. Paths exceeding cap deterministically emit `TRAVERSAL_BUDGET_EXHAUSTED` and do not admit candidates or collect provenance.

### Mechanism B: Terminal Evidence Provenance Materialization
- **Exact Provenance Resolution**: Resolves `evidence_object_ids` (exact indexed source-native object lookup) and `evidence_paths` (normalized canonical repo-relative path lookup) into source-native container objects (`source_file`, `macro`, etc.).
- **Strict Path Normalization**: Separator conversion to `/`, strip leading `./`, case-preserving. Absolute paths (`/`, `C:`) and directory traversal (`..`) are rejected closed (`GOVERNED_PROVENANCE_INVALID`).
- **Fail-Closed Resolution**:
  - Explicit `evidence_source_ids` not intersecting allowed plan/context scope fail closed (`VERSION_SCOPE_CONFLICT`, never falling back to plan targets).
  - Explicit `source_version_ids` conflicting with plan-locked versions fail closed (`VERSION_SCOPE_CONFLICT`).
  - Curated domain semantic objects in `evidence_object_ids` are rejected as bridged candidates (`GOVERNED_PROVENANCE_INVALID`, remaining anchor only).
  - Ambiguous path matches retain all matched `object_id`s in receipt locator and metadata (`PROVENANCE_SOURCE_OBJECT_AMBIGUOUS`).
  - Zero matches emit `PROVENANCE_SOURCE_OBJECT_NOT_FOUND`.
  - Reached origins carrying no evidence fields emit `GOVERNED_PROVENANCE_NOT_FOUND`.
- **Deduplication Before Cap Decision**: Deduplicated before candidate-cap decision so duplicate references do not consume candidate slots or cause false `BRIDGED_CANDIDATE_RANKED_OUT`.
- **Global Bridged Candidate Cap**: Capped at 20 source-native candidates.
- **Terminal Execution**: Materialized candidates do not become graph frontiers.

### Integration & Diagnostics
- **Graph Channel Integration**: Bridged source-native candidates are deduplicated by `object_id` and prefixed before the unbridged graph baseline using `merge_exact_streams`.
- **No Independent Priority / Double Voting**: Candidate authority role is `GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE`; no new RRF vote, channel weight, or score tampering.
- **Seven Exact Displacement Diagnostics**:
  1. `bridged_candidate_count`
  2. `graph_candidates_before_bridge`
  3. `graph_candidates_after_bridge`
  4. `graph_candidates_displaced_by_prefix`
  5. `displaced_object_ids`
  6. `bridged_candidate_ids`
  7. `deduplicated_overlap_count`
- **Receipts**: Full `StructuredReachabilityReceipt` and `StructuredEvidenceBridgeReceipt` structured tracing.

---

## 4. D1 Repository Identity & Mechanism C Outcome

- **Starting Repository D1 Identity**: Commit `0151786856d813661ab29962987f933d17e619c2` across `configs/seed_objects.yaml`, `configs/seed_relations.yaml`, `configs/seed_workflows.yaml`.
- **Counts**: 24 objects / 16 accepted relations / 1 curated workflow step.
- **Mechanism C**: `PENDING_R2_GOVERNANCE_DISPOSITION`.
- **`D3_5_A1_REPOSITORY_D1_CHANGED`**: `false`.
- **`starting_identity_equals_final_identity`**: `true`.

---

## 5. Isolation & Materialization Analysis

1. **Configurable / Implemented Isolation Mechanism**:
   - `StorageSettings(database_url=...)` supports targeting a distinct isolated database via `PANDA_DATABASE_URL`.
   - `PostgresD3StructuredGraphReader` connects through the provided `Storage` instance.
   - In-memory mock graph reader fixtures support complete exact T0 testing without database dependency.
2. **Deployed Production Database State**:
   - Production database writes performed: `0` (`PRODUCTION_STRUCTURED_STATE_WRITES = 0`).
   - Production database state remains untouched (`production_materialization_untouched_true = true`).
3. **Persistent Evaluation Database Status**:
   - An isolation mechanism is configured in code, but the persistent target database was not provisioned because safety approval permission was not granted in this execution environment.
   - `D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN = false`
   - `isolated_materialization_matches_final_repository_D1 = false`
   - `production_materialization_untouched_true = true`

---

## 6. Freeze Booleans & Lifecycle Decision

| Freeze Boolean | Value | Rationale |
|---|---|---|
| `D3_5_A1_IMPLEMENTATION_FROZEN` | `true` | Runtime Mechanism A & B, four arms, receipts, diagnostics repaired and fully tested (35 tests PASS) |
| `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY_FROZEN` | `false` | Pending D3.5-A1-R2 Mechanism-C governance disposition |
| `D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN` | `false` | Persistent isolated evaluation DB was not provisioned (safety approval not granted) |
| `isolated_materialization_matches_final_repository_D1` | `false` | Persistent isolated evaluation DB not present |
| `production_materialization_untouched_true` | `true` | Deployed database completely untouched (0 writes) |

### Lifecycle Closeout Decision:
**`REPAIRED / AWAITING_R2_GOVERNANCE_AND_ISOLATION`**

The D3.5-A1 runtime implementation and comprehensive T0 unit tests are repaired and frozen (`D3_5_A1_IMPLEMENTATION_FROZEN = true`). Next task: `D3.5-A1-R2 — Mechanism-C Governance Disposition & Isolated Materialization Freeze`.

---

## 7. Verification & Test Summary

- **`tests/unit/test_d3_5_structured_bridge.py`**: 27 tests, **PASS**.
- **`tests/unit/test_d3_structured_shortcut.py`**: 8 tests, **PASS**.
- **Total Tests Run**: 35 tests, 0 failures, 0 errors.
- **Anti-Leak Audit**: No formal case/question/expected-evidence metadata or new case-specific mapping occurs in runtime bridge logic. The pre-existing frozen D3 selected rule IDs remain only for nonsemantic arm suppression/configuration; Mechanism A/B have zero semantic dependency on them and `selected_legacy_payload_reuse_count = 0`.
- **Git Tree Status**: Writable workspace modified, **NOT COMMITTED**.
