# D3.5-A1 — Bounded Structured Evidence-Link Bridging Prototype (R3 Frozen)

## 1. Executive Summary & Checkpoint Status

| Item | Value |
|---|---|
| **Checkpoint** | `D3.5-A1-R3` |
| **Status** | `COMPLETE / D3.5-A1 FROZEN / READY FOR D3.5-A2` |
| **Base Commit** | `45f58feb27b75d552b4797321bb688fb038f52da` |
| **Final Repository D1 Commit** | `9b5a84996c30eaf1a297924b36452a90fe6d84d2` |
| **Preregistration Identity** | `evaluation/d3_5_a0_structured_evidence_link_design.json` (D3.5-A0-R2) |
| **Runtime Implementation Status** | Fully repaired, exact-version qualified, and verified via T0 unit/synthetic tests (40 tests PASS); runtime frozen since R2 with 0 runtime changes in R3 |
| **Database Role** | `CURRENT_DATABASE_ROLE = DEDICATED_DEVELOPMENT_EVALUATION_STATE` (sanitized target: `host=127.0.0.1`, `port=55432`, `database=panda_qa`) |
| **Final Repository D1 Identity** | `24` objects / `16` accepted relations / `1` curated workflow step / `2` aliases (`D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY_FROZEN = true`) |
| **Mechanism-C Outcome** | `APPROVED_GOVERNED_CHANGE` (`MECHANISM_C_DISPOSITION_FROZEN = true`, `D3_5_A1_REPOSITORY_D1_CHANGED = true`) |
| **Development Materialization Status** | In-place synchronized, exact-diff verified via the R3 materialization receipt (`development_materialization_matches_final_repository_D1 = true`, all diff lists empty, stale records = 0, `D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN = true`) |
| **Production Structured-State Writes** | `0` (Deployed production database role clarified; dedicated development DB synchronized in place) |
| **Qdrant Vector Writes** | `0` (`QDRANT_WRITES = 0`) |
| **D3.5-A2 Lifecycle** | `NOT_STARTED / READY_TO_EXECUTE` (`FORMAL_D3_5_A2_RUNS = 0`, `D3_5_OUTCOME_EXPOSURE = NOT_STARTED`) |

---

## 2. Exact Version Qualification & R1/R2 Repairs

### Exact Version Qualification Boundary (R2)
Path-based source-native materialization strictly enforces:
$$\text{explicit governed } \texttt{source\_id} + \text{one exact frozen } \texttt{source\_version\_id} + \text{canonical repository-relative path}$$

1. **Active Frozen Version Resolution**: For any candidate source, the active frozen source version is resolved strictly from `RetrievalPlan.resolved_versions` or the immutable manifest identity (`source_manifest.json`: `commit_sha` for repositories, `sha256` for papers, `snapshot_hash` for web documents).
2. **Provenance Version Compatibility**: If provenance specifies `source_version_ids`, every referenced source version must be compatible with the active frozen version; any mismatch fails closed with `VERSION_SCOPE_CONFLICT`.
3. **Fail-Closed on Unversioned Sources**: If no exact frozen version is resolvable for a source, execution fails closed with `VERSION_SCOPE_CONFLICT` and injects zero candidates.
4. **No Context-Source Version Bypass**: Papers, web documents, and other context sources are not exempt from exact version qualification; missing manifest identities fail closed.
5. **Prohibition of Latest-Version Inference**: No heuristic inference of `latest`, `current`, `HEAD`, or newest available version is permitted.

### Prior Contract Defect Repairs (R1)
1. **Historical D3 vs D3.5 Arm Separation**: Historical D3 (`D3Arm` / `D3ExperimentConfig`) maintains the frozen 7 rules; D3.5 (`D3_5Arm` / `D3_5ExperimentConfig`) manages the 2 focused rules (`event_poca_handoff`, `restgas_profile_workflow`), with the remaining 5 rules active as background expansions across all four D3.5 arms.
2. **Restoration of Unbridged Structured Baseline**: `derive_unbridged_structured_seeds` preserves pre-A1 behavior without an 8-seed cap and admits all Tier-D ambiguity candidates without atomic budget constraints. `derive_d3_5_bridge_seeds` independently enforces the cap-8 and atomic budget constraints for the bridge branch.
3. **Genuine Additive Bridge Composition**: `STRUCTURED_BRIDGED` composes bridged candidates onto the unbridged graph baseline (`unbridged_graph = merge_exact_streams(candidates, ordinary_graph)`). Exact zero-bridge equivalence is preserved. Prefix displacement is measured relative to `unbridged_graph`.
4. **Governed Source Qualification for Evidence Paths**: `evidence_paths` requires explicit governed `evidence_source_ids` matching plan/context scope; missing `evidence_source_ids` fails closed with `GOVERNED_PROVENANCE_INVALID`.

---

## 3. Mechanism-C Governance Disposition

### Independent Domain Semantics Investigation
An independent source and domain inspection was conducted on the `RestgasDetermination` repository (`11f1edc49dcbaeb61d707491a6d3bbec390fcd42`) and associated workflow semantics, completely isolated from benchmark evaluation cases, gold answer locations, or legacy query-expansion payloads:

- `configuration.restgas_profile` selects the concrete distributed-target longitudinal density profile text file. In the simulation pipeline, `macro/target/prod_sim_hvmaps.C` is the primary macro accepting `restgas_profile`, validating its existence, setting `TargetMode=8`, and passing `restgas_profile` to `PndMasterRunSim`.
- `file_pattern.restgas_profile_input` represents concrete profile text files (`restgas_16012024_*.txt`). In the simulation generator layer, `pgenerators/Target/PndTargetGenerator.cxx` parses the profile file (`ReadDensityFile()`) and samples the interaction vertex distribution (`SampleInteractionVertex()`).

### Counterfactual Gate Evaluation
$$\text{Question: Would this governed evidence linkage still be correct, useful, and worth maintaining if g021 had never existed?}$$
$$\text{Verdict: } \mathbf{YES.}$$
The linkages truthfully reflect the core simulation entry points and C++ generator classes in `RestgasDetermination` for the restgas profile parameterization.

### Approved Governed Changes in `configs/seed_relations.yaml`:
1. `configuration.restgas_profile PARAMETERIZES workflow.restgas_profile_reconstruction`:
   - Added evidence path: `macro/target/prod_sim_hvmaps.C`
   - Governed source: `restgas_determination`
2. `file_pattern.restgas_profile_input PRODUCES_INPUT_FOR workflow.restgas_profile_reconstruction`:
   - Added evidence paths: `macro/target/prod_sim_hvmaps.C`, `pgenerators/Target/PndTargetGenerator.cxx`
   - Governed source: `restgas_determination`

- **Disposition**: `APPROVED_GOVERNED_CHANGE`
- **`D3_5_A1_REPOSITORY_D1_CHANGED`**: `true`
- **`MECHANISM_C_DISPOSITION_FROZEN`**: `true`

---

## 4. Final Approved Post-A1 Repository D1 Identity

- **Anchor Commit**: `9b5a84996c30eaf1a297924b36452a90fe6d84d2`
- **Authoritative Configuration Files**:
  - `configs/seed_objects.yaml` (24 objects)
  - `configs/seed_relations.yaml` (16 accepted relations)
  - `configs/seed_workflows.yaml` (1 curated workflow step)
  - `configs/aliases.yaml` (2 curated aliases)
- **Status**: `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY_FROZEN = true`

---

## 5. Dedicated Development PostgreSQL Database Materialization & Freeze

1. **Database Role Clarification**:
   - `CURRENT_DATABASE_ROLE = DEDICATED_DEVELOPMENT_EVALUATION_STATE`
   - Sanitized target identity: `host = 127.0.0.1`, `port = 55432`, `database = panda_qa` (credentials redacted from evaluation artifacts per R3 hygiene; runtime environment credentials unchanged)
   - Reused existing development PostgreSQL database in place. No second database was created.
2. **In-Place Synchronization**:
   - Ingested and updated normalized corpus (`manifest_hash = 9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94`).
   - Upserted all 24 objects, 16 accepted relations, 1 curated workflow step, 2 aliases.
   - Pruned stale/superseded curated records: `0` stale records remain.
3. **Semantic Verification**:
   - Verified that all 24 curated object IDs, 16 accepted relation SPO tuples & payload evidence links, and 1 curated workflow step match the final repository D1 identity.
   - `development_materialization_matches_final_repository_D1 = true`
   - `D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN = true`
   - `QDRANT_WRITES = 0`

---

## 6. D3.5-A1-R3 — Materialization Receipt & Lifecycle Consistency Repair

R3 is an auditability and lifecycle-consistency repair only. It changes no scientific result, no runtime behavior, no D1 configuration, and no database state.

1. **Read-Only Database Verification**: The dedicated development PostgreSQL database was queried exclusively over a `default_transaction_read_only = on` connection. `POSTGRESQL_WRITES = 0`, `QDRANT_WRITES = 0`, `INGESTION = 0`, `REINGESTION = 0`, and all model-call counters remained `0`. Sanitized target: `host = 127.0.0.1`, `port = 55432`, `database = panda_qa`, `role = DEDICATED_DEVELOPMENT_EVALUATION_STATE`.
2. **Exact Curated-State Receipt**: The machine artifact now embeds `development_materialization_receipt` — a persistent, independently inspectable record of the frozen curated D1 identity derived from the frozen seed configs plus the frozen normalized ingestion artifacts (`manifest_hash = 9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94`): all `24` exact curated object IDs, all `16` accepted curated relation identities (stable SPO tuple + stable `edge_id` + `review_status` + declared `evidence_paths`/`evidence_object_ids`/`evidence_source_ids` + resolved evidence object set + `source_version_ids`), the `1` curated workflow step (`workflow.restgas_profile_reconstruction` / `workflow.restgas.first_pass_poca` with entrypoint, inputs, outputs), and the `2` curated aliases (`alias.d113240c86097a54294a250b` `restgas_profile.txt` -> `configuration.restgas_profile`; `alias.d40bb866062a7cda6711f928` `*_pid_final.root` -> `data_product.restgas.pid_final_root`) with provenance object sets. Nothing is recorded only as a hash.
3. **Repository-vs-Database Diff**: The receipt's `repository_vs_database_diff` compares the repository-side curated identity field-by-field against the read-only extracted curated database state. All twelve diff lists are empty: `objects_missing_in_db`, `objects_extra_in_db`, `relations_missing_in_db`, `relations_extra_in_db`, `relation_payload_mismatches`, `workflow_steps_missing_in_db`, `workflow_steps_extra_in_db`, `workflow_payload_mismatches`, `aliases_missing_in_db`, `aliases_extra_in_db`, `alias_payload_mismatches`, `provenance_mismatches`. `stale_or_superseded_curated_records = 0` (database-side curated identification used exact governance identity: `metadata.curated_seed` for objects, `creation_method = curated` + `metadata.resolution_method = curated_seed` for relations, `metadata.curated_seed` for workflow steps, `metadata.creation_method = curated` for aliases — never counts, titles, or substring heuristics).
4. **Provenance Verification**: Every accepted curated relation's persisted database payload was compared in full (including resolved `evidence_object_ids` and `source_version_ids`), and every declared evidence path/object was re-derived from the database evidence objects' governed source identity and locator paths — no benchmark metadata was used. The two Mechanism-C repaired relations were verified explicitly in the database payload: `configuration.restgas_profile PARAMETERIZES workflow.restgas_profile_reconstruction` (`edge.ea3a79d222f0ca6cc0e6df72`) carries the approved evidence including `macro/target/prod_sim_hvmaps.C`, and `file_pattern.restgas_profile_input PRODUCES_INPUT_FOR workflow.restgas_profile_reconstruction` (`edge.81276373f106c8758d5aec92`) carries `macro/target/prod_sim_hvmaps.C` and `pgenerators/Target/PndTargetGenerator.cxx`, both governed by `restgas_determination` and grounded at `restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42`.
5. **Credential Redaction**: Credential-bearing database URLs were replaced in the evaluation artifacts by sanitized target identities (`postgresql://***@host:port/database` shape). Runtime environment credentials were not altered. `database_target_sanitized = true`.
6. **Lifecycle-Name Repair**: The canonical next-stage identifier is restored as `D3.5-A2 — Focused Evidence-Link Recovery Validation` (the descriptive phrase "Structured Evidence-Link Bridging Evaluation" is no longer used as the lifecycle identifier), and the A2 lifecycle state is recorded as `NOT_STARTED / READY_TO_EXECUTE` (`FORMAL_D3_5_A2_RUNS = 0`, `D3_5_OUTCOME_EXPOSURE = NOT_STARTED`). Stale isolation/separate-database wording was repaired in the current D3.5 roadmap section; historical predecessor sections remain untouched.
7. **No Mutation**: `RUNTIME_FILES_CHANGED = 0`, D1 config changes `0`, query expansion changes `0`. The gate `development_materialization_matches_final_repository_D1 = true` is set by the empty exact diff plus zero stale records — not by counts alone.

---

## 7. Freeze Booleans & Lifecycle Decision

| Freeze Boolean | Value | Rationale |
|---|---|---|
| `D3_5_A1_IMPLEMENTATION_FROZEN` | `true` | Runtime Mechanism A & B, four arms, exact version qualification, receipts, and diagnostics verified and frozen |
| `MECHANISM_C_DISPOSITION_FROZEN` | `true` | Independent governance disposition approved and committed (`APPROVED_GOVERNED_CHANGE`) |
| `D3_5_A2_FINAL_REPOSITORY_D1_IDENTITY_FROZEN` | `true` | Repository D1 identity anchored at commit `9b5a84996c30eaf1a297924b36452a90fe6d84d2` (24/16/1/2) |
| `D3_5_EVALUATION_D1_MATERIALIZATION_FROZEN` | `true` | Dedicated development database synchronized in place to final D1 and frozen |
| `development_materialization_matches_final_repository_D1` | `true` | R3 exact repository-vs-database diff verified: 24 objects, 16 accepted relations, 1 workflow step, 2 aliases, all diff lists empty, 0 stale records |
| `D3_5_A1_REPOSITORY_D1_CHANGED` | `true` | Governed provenance repaired on 2 restgas relations |

### Lifecycle Closeout Decision:
**`COMPLETE / D3.5-A1 FROZEN / READY FOR D3.5-A2`**

All implementation, exact-version qualification, governance disposition, repository D1 identity, and PostgreSQL development materialization requirements for D3.5-A1 are complete and frozen. The R3 materialization receipt makes the frozen match independently inspectable. `D3.5-A2 — Focused Evidence-Link Recovery Validation` is `NOT_STARTED / READY_TO_EXECUTE` and requires separate authorization.

---

## 8. Verification & Test Summary

- **`tests/unit/test_d3_5_structured_bridge.py`**: 32 tests, **PASS** (includes 5 focused exact-version qualification tests).
- **`tests/unit/test_d3_structured_shortcut.py`**: 8 tests, **PASS**.
- **Total Tests Run**: 40 tests, 0 failures, 0 errors (R2 runtime freeze; no runtime files changed in R3).
- **R3 Focused Checks**: machine artifact JSON parse **PASS**; read-only DB receipt generation **PASS**; exact repository-vs-database comparison **PASS** (all twelve diff lists empty); materialization diff empty **PASS** (`stale_or_superseded_curated_records = 0`); credential absence in active R3 artifacts **PASS**; roadmap/status lifecycle consistency **PASS**; canonical A2 stage name consistency **PASS**; `FORMAL_D3_5_A2_RUNS = 0` **PASS**; `git diff --check` **PASS**.
- **Scientific Guardrails Enforced**: 0 model calls, 0 Qdrant writes, 0 PostgreSQL writes, 0 formal benchmark comparison runs, 0 validation/holdout access.
