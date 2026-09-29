# G4 R2 Normal-Product Pool-Integration Correction

## Decision and corrected checkpoint interpretation

`G4_R2_NORMAL_PRODUCTION_INTEGRATION_CORRECTION = PASS` for the deterministic integration scope. Starting HEAD was `642527e1cac611c68cca041748b39be47424c152`, with parent `9e5fd9ebdbbf258b0d09d3a4e0105a69ddf3dd7d` and a clean worktree. The forward `Integrate G4 R2 retention into normal retrieval` commit becomes the new product-behavior lineage; resolve its exact SHA from Git history.

The previous [implementation result](G4_R2_EVIDENCE_RETENTION_IMPLEMENTATION_RESULT.md) remains an unchanged historical record. It established the shared/global constructor, generic R2-A–I controls, origin propagation, and a non-gating exposed offline replay. It did not establish normal-product integration. Independent audit found that `production_answer_obligations_v1` follows `QAAgent.run_detailed -> _retrieve -> Retriever.retrieve`, whose local reranker still received the legacy `fused_order[:30]` treatment pool. The evaluation runner uses that same default mode. The earlier interpretation of complete normal-product R2 repair is superseded by this correction; the previous global controls and replay retain their actual scope.

## Required normal-path RED

Before any source correction, NP-1 called the real `Retriever.retrieve` with bounded fictional channels and a fake reranker. The necessary source/version-valid code candidate had dense rank 1. Thirty stronger consensus objects occupied the old pool; structured replacement did not rescue it. Command:

```text
..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_g4_r2_evidence_retention.py::test_r2_normal_retrieve_uses_policy_role_frontier
1 failed
```

`NORMAL_PRODUCT_R2_A_PRE_REPAIR = RED`: the assertion that the necessary candidate was among the fake reranker's offered IDs failed. Retrieval and fixture construction completed; this was not a plan, storage, version, source-role, fake-client, or final-selector error. The NP-1 fixture and expectation were unchanged after the RED. The identical command then returned `1 passed`, with entry reason `policy_role_frontier`.

## Correction

Normal `retrieve` now calls the existing `_r2_rerank_pool`; no second pool policy or new constants were introduced. A small shared `_channel_pass_occurrences` helper constructs one-based ranks and aligned specialized origin markers for both normal retrieval and global consolidation. Existing local weighted RRF scores and insertion-stable ordering, global minimum ranks and tie ordering, source/version validity, role capacities, strict majority formula, source budgets, channel bounds, and the 30-object offer limit are unchanged.

Structured discovery still calls `_apply_structured_replacement` with the counterfactual legacy `fused_order[:30]`. Its selected, reservable, reserved, eligible, and structured-displacement decisions remain unchanged and cannot depend on frontier membership. The returned eligible supplemental IDs feed the shared pool constructor, reserving slots before frontier allocation. The legacy treatment pool is no longer the final normal offer. Only `structured_replacement.final_rerank_pool_ids` is updated to the actual offered pool; `displaced_ordinary_ids` remains the narrower **structured-only displacement against the legacy discovery pool**, not all displacement caused by R2 frontier construction. `reserved_ids` and `eligible_supplemental_ids` retain their prior meanings. No receipt schema/version changed.

Normal retrieval returns ordered `rerank_pool_entries` matching the fake reranker offer. `QAAgent._run_detailed` carries that field into additive internal diagnostics. `QAResult`, service DTOs, formal retrieval/service trace schemas, and `fusion_scores` semantics are unchanged. Explicit D3 retrieval continues its previous pool behavior and does not invoke the new normal-path integration. R3, prompts, admission, verifier, and finalization are unchanged.

## Deterministic gates

| Gate | Result |
|---|---|
| NP-1 actual normal retrieval | RED -> GREEN; necessary candidate offered as `policy_role_frontier` |
| NP-2 supplement + frontier | PASS; supplements reserved first, unique pool <=30, strict RRF majority, truthful actual-pool receipt |
| NP-3 no eligible omission | PASS; ordinary offered IDs/order match the prior RRF pool |
| NP-4 specialized caller handoff | PASS; generic fallback and missing-origin workflow/graph candidates gain no frontier preference |
| Shared-policy equivalence | PASS; semantically equivalent single-pass normal/global inputs have matching pool entries, including RRF, frontier, and supplements |
| Normal QA diagnostics | PASS; default QA route carries actual pool entries internally and leaves public result unchanged |
| Existing R2-A–I | PASS; normative policy expectations unchanged |
| Existing G4 dual-sided baseline | 18/18 PASS |

Local commands and outcomes:

```text
..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_g4_r2_evidence_retention.py
17 passed

..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_retrieval.py tests/unit/test_c8_global_candidate_pool.py tests/unit/test_e3_missing_point_retrieval.py tests/unit/test_retrieval_trace.py tests/unit/test_fusion_replay.py tests/unit/test_d4_a3_batch1_runtime_migration.py
1 failed, 210 passed, 27 subtests passed

..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_d4_a3_batch1_runtime_migration.py::TestProductionPolicyAndActivation tests/unit/test_d4_a3_batch1_runtime_migration.py::TestAdmissionK3Semantics tests/unit/test_d4_a3_batch1_runtime_migration.py::TestRuntimeIntegration
19 passed

..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_g4_false_insufficiency_regression.py
18 passed
```

All five required neighboring modules passed within the combined run. The sole additional-module failure was `TestBatch1ConfigMigration::test_req6_non_batch1_rules_unchanged`, an obsolete equality assertion against `8c0971f...:configs/query_expansions.yaml`. A direct parsed-YAML comparison confirmed the worktree config equals starting HEAD, and starting HEAD already fails that historical comparison for `event_alignment`, `effective_acceptance_pipeline`, `root_macro_usage`, and `model_factory_theory`. This is a pre-existing config-history failure, not a retrieval or structured-replacement regression; the test and config were not changed. The directly affected structured activation/admission/runtime classes passed separately.

An additional QA-diagnostic fixture initially supplied an empty decomposition and failed the existing non-empty point contract. It was corrected to supply a synthetic point with exact support and no relations. This incidental fixture correction did not touch NP-1 or product expectations. Results above are local pytest evidence, not CI certification.

## Identity, materiality, and accounting

Normal mode remains `production_answer_obligations_v1`; decomposition prompt/schema remain `3.0.0` / `e1.question_decomposition.v3`; coverage schema remains `coverage-satisfaction-v2`; prompt set remains `3.12.0`; prompt fingerprint remains `5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce`. Gold/calibration remain `m6-benchmark-v2.11` / `phase_b_t3_product_language_scope_v8`.

`PRODUCT_SOURCE_CHANGE=true`, `PRODUCT_BEHAVIOR_CHANGE=true`, `RETRIEVAL_BEHAVIOR_CHANGE=true`, `R2_BEHAVIOR_CHANGE=true`, `NORMAL_PRODUCT_PATH_CHANGE=true`. Prompt, config, decomposition/coverage/trace/manifest schemas, admission, verifier, finalization, Gold, dataset, and calibration changes are false. Dense re-embedding, sparse-index rebuild, and corpus re-ingestion are not required. Existing retrieval-policy identity plus the new Git lineage distinguishes this integration behavior; no new hash or historical manifest rewrite was created.

`EXPOSED_REPLAY_RERUN=false`. No exposed case trace/record was reopened. `SCIENTIFIC_CALLS=0`, `SCIENTIFIC_TOKENS=0`, `QA_RUNS=0`, `LIVE_RETRIEVAL_RUNS=0`, `EXTERNAL_JUDGE_CALLS=0`. Fake unit retrieval/QA seams are not scientific/live runs. New novel-dev content access, novel-validation content/outcome access, holdout content/outcome access, and protected leakage are all zero. Historical implementation/replay artifacts are unchanged.

## Lifecycle and limitations

`PHASE_G = IN_PROGRESS / G4_R2_NORMAL_PRODUCT_INTEGRATION_COMPLETE`.

`G4 = DETERMINISTIC HARNESS COMPLETE / EXPOSED DEVELOPMENT DIAGNOSTIC COMPLETE / GENERIC R2 FALSE_INSUFFICIENCY MECHANISM ESTABLISHED / R2 REPAIR IMPLEMENTED IN NORMAL PRODUCT PATH / NORMAL-PRODUCTION DETERMINISTIC RED→GREEN PASS / EMPIRICAL REPAIR BENEFIT NOT_ESTABLISHED`.

The pool offers bounded opportunity only; it does not guarantee final evidence or empirical QA benefit. No live comparison or fresh Lane B cohort exists. Next recommendation: `G4 FRESH NOVEL_DEV LANE B CURATION / FREEZE DESIGN`, separately authorized and not executed. `NEXT_TASK_EXECUTION_AUTHORIZED=false`.
