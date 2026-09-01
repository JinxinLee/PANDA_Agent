# D3.5-A1 — Bounded Structured Evidence-Link Bridging Prototype

## 1. Executive Summary & Checkpoint Status

| Item | Value |
|---|---|
| **Checkpoint** | `D3.5-A1` |
| **Status** | `BLOCKED / ISOLATED_MATERIALIZATION_UNAVAILABLE` |
| **Base Commit** | `0151786856d813661ab29962987f933d17e619c2` |
| **Preregistration Identity** | `evaluation/d3_5_a0_structured_evidence_link_design.json` (D3.5-A0-R2) |
| **Runtime Implementation Status** | Fully implemented and verified via comprehensive T0 unit/synthetic tests (29 tests PASS) |
| **D1 Repository Identity** | `24` objects / `16` accepted relations / `1` curated workflow step (Unchanged) |
| **Mechanism-C Outcome** | `NOT_PERFORMED / NO_CHANGE` (`D3_5_A1_REPOSITORY_D1_CHANGED = false`) |
| **Production Structured-State Writes** | `0` (Deployed production database completely untouched) |

---

## 2. Four-Arm Experimental Plumbing

The four-arm comparison framework has been implemented in `src/panda_agent/d3_structured.py` and `src/panda_agent/retrieval.py` while strictly preserving historical `D3Arm.STRUCTURED` compatibility:

1. **`LEGACY`**: All 54 query expansions active; structured treatment disabled; bridge disabled.
2. **`ABLATION`**: 7 selected query expansions suppressed; structured treatment disabled; bridge disabled.
3. **`STRUCTURED_UNBRIDGED`** (synonym `STRUCTURED`): 7 selected expansions suppressed; unbridged structured path active; bridge disabled.
4. **`STRUCTURED_BRIDGED`**: 7 selected expansions suppressed; structured treatment active; D3.5 reachability and evidence-link bridge active.

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
- **Graph Channel Integration**: Bridged source-native candidates are deduplicated by `object_id` and prefixed before ordinary graph candidates using `merge_exact_streams`.
- **No Independent Priority / Double Voting**: Candidate authority role is `GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE`; no new RRF vote, channel weight, or score tampering.
- **Seven Exact Displacement Diagnostics**:
  1. `bridged_candidate_count`
  2. `graph_candidates_before_bridge`
  3. `graph_candidates_after_bridge`
  4. `graph_candidates_displaced_by_prefix`
  5. `displaced_object_ids`
  6. `bridged_candidate_ids`
  7. `deduplicated_overlap_count`
  (Ensured `STRUCTURED_UNBRIDGED` and `STRUCTURED` do not mislabel ordinary structured candidates as bridged candidates).
- **Receipts**: Full `StructuredReachabilityReceipt` and `StructuredEvidenceBridgeReceipt` structured tracing.

---

## 4. D1 Repository Identity & Mechanism C Outcome

- **Starting Repository D1 Identity**: Commit `0151786856d813661ab29962987f933d17e619c2` across `configs/seed_objects.yaml`, `configs/seed_relations.yaml`, `configs/seed_workflows.yaml`.
- **Counts**: 24 objects / 16 accepted relations / 1 curated workflow step.
- **Mechanism C**: `NOT_PERFORMED / NO_CHANGE`. No D1 seed configuration change was performed.
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
   - Distinguishing configurable/in-memory isolation from an actually synchronized persistent DB:
     - `D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN = false`
     - `isolated_materialization_matches_final_repository_D1 = false`
     - `production_materialization_untouched_true = true`

---

## 6. Freeze Booleans & Lifecycle Decision

| Freeze Boolean | Value | Rationale |
|---|---|---|
| `D3_5_A1_IMPLEMENTATION_FROZEN` | `true` | Runtime Mechanism A & B, four arms, receipts, diagnostics repaired and fully tested (29 tests PASS) |
| `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY_FROZEN` | `true` | Repository D1 identity frozen at 24/16/1 with no changes |
| `D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN` | `false` | Persistent isolated evaluation DB was not provisioned (safety approval not granted) |
| `isolated_materialization_matches_final_repository_D1` | `false` | Persistent isolated evaluation DB not present |
| `production_materialization_untouched_true` | `true` | Deployed database completely untouched (0 writes) |

### Lifecycle Closeout Decision:
**`BLOCKED / ISOLATED_MATERIALIZATION_UNAVAILABLE`**

Per D3.5-A0-R2 Section 18, A1 closeout requires all four freeze conditions to be genuinely satisfied. While the prototype runtime implementation and comprehensive T0 unit tests are complete and frozen, transition to D3.5-A2 execution is blocked until an isolated persistent evaluation database is provisioned and synchronized under separate authorization. `D3.5-A2` remains `NOT_STARTED`.

---

## 7. Verification & Test Summary

- **`tests/unit/test_d3_5_structured_bridge.py`**: 21 tests, **PASS**.
- **`tests/unit/test_d3_structured_shortcut.py`**: 8 tests, **PASS**.
- **Total Tests Run**: 29 tests, 0 failures, 0 errors.
- **Anti-Leak Audit**: No formal case/question/expected-evidence metadata or new case-specific mapping occurs in runtime bridge logic. The pre-existing frozen D3 selected rule IDs remain only for nonsemantic arm suppression/configuration; Mechanism A/B have zero semantic dependency on them and `selected_legacy_payload_reuse_count = 0`.
- **Git Tree Status**: Writable workspace modified, **NOT COMMITTED**.
