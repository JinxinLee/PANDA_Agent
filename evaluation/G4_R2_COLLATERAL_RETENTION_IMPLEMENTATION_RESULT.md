# G4 R2 Collateral Rank-Witness Retention — Deterministic Implementation Result

## Decision and boundary

```text
G4 R2 COLLATERAL RETENTION IMPLEMENTATION = PASS / DETERMINISTIC CORRECTION VERIFIED
SELECTED_ARCHITECTURE = BOUNDED_POLICY_ROLE_CHALLENGER_EXCHANGE_WITH_RANK_WITNESS_RETENTION
SHARED_POLICY = Retriever._r2_rerank_pool
FRONTIER_CAPACITY_SEMANTICS = UPPER_BOUND_ON_SUCCESSFUL_ADMISSIONS
DUPLICATE_POLICY_IMPLEMENTATION = false
MAGIC_THRESHOLD_INTRODUCED = false
RANK_WITNESS_COMPONENTWISE_RETENTION = implemented
CHARGED_ROLE_STRICT_IMPROVEMENT = implemented
REJECTED_CHALLENGER_CONSUMES_QUOTA = false
FRONTIER_CAN_BE_BELOW_CAPACITY = true
```

The separately authorized task implements the contract in the prior [collateral failure review](G4_R2_COLLATERAL_RETENTION_COMPLETENESS_FAILURE_REVIEW.md). It changes one shared retrieval constructor and its synthetic test module. No exposed case result, Gold answer, path, object ID, rank, or score is used by product code or new test fixtures. The previous product-behavior lineage is `a22c8f70eeebe4a53490e11a4b6852561ca8afa6`; the implementation commit becomes the new lineage only after the deterministic gates below pass. At task start `git rev-parse HEAD` returned `7949675de7be9289c0a15f7f83dcee4b71145bd9`, `git status --short` was empty, and the most recent commit was `Review G4 R2 collateral retention failure`. Resolve the implementation commit's exact SHA from Git history/delivery rather than embedding a self-referential hash here.

This is deterministic product acceptance only. The historical exposed post-repair safety regression remains a historical FAIL. n024 has **not** undergone post-correction QA verification, n006 recovery remains unpromised, and fresh generalization benefit remains unestablished. G3 admission `NO_CHANGE` and fresh Lane B `OPTIONAL / DEFERRED` are unchanged.

## CR-1: genuine pre-repair RED and post-repair GREEN

Before changing `src/panda_agent/retrieval.py`, the test module gained a fictional full-base fixture. Its ordinary incumbent has exact plus dense support, belongs to the legacy top-30, and is outside the current shortened backbone under valid multi-role frontier pressure. Its synthetic RRF position differs from the exposed witness. The normative assertion requires that incumbent to remain in the actual offered pool. A paired fixture permits an equal-or-better same-channel substitute and therefore does not freeze the incumbent's ID.

```text
PRE_REPAIR_PRODUCT_SOURCE_MODIFIED = false
CR1_PRE_REPAIR = RED
COMMAND = & '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_g4_r2_evidence_retention.py::test_r2_collateral_rank_witness_retention
RESULT = 1 failed; exit 1
FAILURE = AssertionError: fictional_cross_channel_incumbent was absent from offered IDs
SUBSTITUTION_PAIR_PRE_REPAIR = 1 passed; its approved expectation was fixed before source change
```

An immediate `git status --short` showed only `tests/unit/test_g4_r2_evidence_retention.py` modified; `git diff -- src/panda_agent/retrieval.py` was empty. This establishes that CR-1 RED came from the pre-correction product. The CR-1 fixture and its expectation were not changed after the source correction.

```text
CR1_POST_REPAIR = GREEN
COMMAND = & '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_g4_r2_evidence_retention.py::test_r2_collateral_rank_witness_retention
RESULT = 1 passed; exit 0
SUBSTITUTION_PAIR_POST_REPAIR = 1 passed; exit 0
```

## Implementation

The existing `Retriever._r2_rerank_pool()` remains the single seam for normal `Retriever.retrieve()` and global `consolidate_and_select_candidates()`. It retains supplement reservation, ordinary RRF order, existing validity and role queue rules, raw role ceilings, clipped admission limits, deterministic role order and queue sort, and the strict-majority cap. No RRF weight, policy, prompt, source budget, model input, final selector, or public receipt reason changes.

The constructor now starts with the complete non-supplement legacy RRF base. For each eligible ordinary object it records the minimum **qualifying** rank per active role/channel. Regular channels use their existing legitimacy rule; workflow/graph occurrences contribute only with `origin == normal`. Repeated normal occurrences in the same channel count once at the best qualifying rank. Generic fallback or absent specialized origin cannot manufacture a witness or challenger opportunity. The existing raw `q_r` ceiling determines the vector depth; absent entries are infinity.

Each role visit examines the next existing-queue challenger. It considers only remaining original ordinary incumbents, weakest RRF first. It accepts the first explicit exchange that leaves **every** active role/channel vector component non-worse and strictly improves at least one component for the charged role. A rejected offer advances its queue cursor without consuming the role or global successful-admission quota; traversal continues until the successful cap or all eligible queues are exhausted. A successful ID is added once, charged to one role, and cannot later be evicted. The final order remains surviving ordinary RRF IDs, successful frontier IDs, then supplements. There is no second implementation or broad retrieval refactor.

The pool therefore stays unique and at most 30; among non-supplement slots, ordinary RRF retains a strict majority. `frontier_capacity` is the ceiling on **successful** exchanges. It can remain unused when no legal victim exists. Existing structured-only displacement fields remain structured-only, while `final_rerank_pool_ids` continues to describe the actual offer.

## CR-1–CR-10 deterministic controls

| Gate | Result | Evidence |
|---|---|---|
| CR-1 collateral retention | PASS | Real RED→GREEN and substitute-pair acceptance; fictional dual-channel incumbent retained unless a legal replacement exists |
| CR-2 challenger recovery | PASS | Legitimate single-channel challenger enters while having lower RRF score than the ordinary victim; existing R2-A and normal/global recovery remain green |
| CR-3 residual opportunity | PASS | Rejected earlier role offer does not use quota and later feasible offer enters; successful earlier offer can exhaust unchanged quota and leave a later candidate out |
| CR-4 capacity not entitlement | PASS | Many eligible same-channel offers receive zero slots when no rank witness improves; equal vectors alone grant no slot |
| CR-5 weak tail exchange | PASS | A redundant RRF tail is displaced by a legitimate lower-RRF-score challenger |
| CR-6 bound/dedup/componentwise | PASS | Independent vectors are checked over four sequential one-exchange synthetic states; a dense gain cannot erase sparse support; unique IDs, strict majority, stable order and overlapping-role dedup are covered |
| CR-7 role generality | PASS | Required-only paper, ordinary-channel paper, code, documentation/readme, and normal specialized workflow/graph cases; no code-only route |
| CR-8 fallback safety | PASS | Normal versus fallback/missing graph provenance; a better-ranked fallback does not lower a normal witness; repeated normal occurrences use best qualifying rank |
| CR-9 structured supplements | PASS | Reduced residual capacity, 27 reserved supplements, correct one-exchange majority, and existing overlap/full-saturation/discovery/receipt controls |
| CR-10 shared callers | PASS | Equivalent normal/global snapshots yield identical actual offered IDs and reason receipts; fake reranker and detailed diagnostics observe the actual pool |

New CR-2–CR-10 tests were run with:

```text
& '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_g4_r2_evidence_retention.py -k 'single_channel_recovery or rejected_offer or successful_role_quota or many_eligible_same_channel or equal_rank_witness or componentwise_guard or specialized_witness or structured_reservation or required_only_paper or overlapping_roles or exchange_normal_and_global'
RESULT = 11 passed, 19 deselected; exit 0
```

During fixture authoring, a focused draft run identified source budgets that did not sum to 1.0 and an assertion that incorrectly demanded retention even when a better substitute legally replaced the incumbent. The fixtures were corrected to the already-reviewed contract before the accepted run. No product constant, invariant, or CR-1 normative expectation was weakened.

The additional sequential CR-6 control was run directly and passed 1/1; the final full R2 module includes it.

## Existing R2 controls and G4 baseline

| Existing control | Result | Scope |
|---|---|---|
| R2-A | PASS | Valid omitted single-channel evidence gets opportunity |
| R2-B | PASS | Role capacity excludes later noise |
| R2-C | PASS | Strict RRF majority across roles |
| R2-D | PASS | Full supplement reservation and pool bound |
| R2-E | PASS | Channel/pass/role/supplement overlap dedup |
| R2-F | PASS | Invalid payloads and specialized-origin exclusions |
| R2-G | PASS | Reservation can reduce frontier to zero |
| R2-H | PASS | Stable ties and repeated passes |
| R2-I | PASS | Paper and normal specialized roles; fallback does not gain privilege |

```text
COMMAND = & '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_g4_r2_evidence_retention.py
RESULT = 31 passed; exit 0

COMMAND = & '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_g4_false_insufficiency_regression.py
G4_DUAL_SIDED_BASELINE = 18/18 PASS; exit 0
```

The 31 R2 tests contain all 17 pre-existing tests and 14 new synthetic controls. No existing assertion was weakened. These are local fake-provider/deterministic tests, not CI certification or live QA.

## Focused retrieval neighbors

The shared `retrieval.py` edit warranted the directly adjacent retrieval, C8 global candidate-pool, E3 missing-point retrieval, trace, and fusion-replay modules. The R2 module itself contains the directly affected normal structured-replacement receipt and global supplement controls.

```text
COMMAND = & '..\.venv\Scripts\python.exe' -m pytest -q tests/unit/test_retrieval.py tests/unit/test_c8_global_candidate_pool.py tests/unit/test_e3_missing_point_retrieval.py tests/unit/test_retrieval_trace.py tests/unit/test_fusion_replay.py
RESULT = 173 passed, 27 subtests passed; exit 0
```

No full repository suite was run. Verification was proportionate to the one shared retrieval seam and its directly neighboring callers.

## Remaining empirical and non-R2 boundary

```text
N006_EXPOSED_RECOVERY_GUARANTEED = false
V1_G2_REPAIRED = false
EXPOSED_N024_POST_CORRECTION_QA_VERIFIED = false
FULL_NOVEL_DEV_RERUN = false
```

The corrected exchange may still exhaust a role before a later valid candidate; it does not retune n006's heterogeneous queue. n007/n028/n031 V1/G2 rejection concerns, n014 answerability, n018 completeness/generation, and the earlier D1 schema variability are outside this retrieval correction. Historical exposed QA results and their model variability remain unchanged. No n024/n006/n002/n017 live QA or any `novel_dev` run was performed.

## Materiality and accounting

```text
PRODUCT_SOURCE_CHANGE = true
PRODUCT_BEHAVIOR_CHANGE = true
RETRIEVAL_BEHAVIOR_CHANGE = true
R2_BEHAVIOR_CHANGE = true
NORMAL_PRODUCT_PATH_CHANGE = true
GLOBAL_CONSOLIDATION_PATH_CHANGE = true
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
TRACE_SCHEMA_CHANGE = false
ADMISSION_BEHAVIOR_CHANGE = false
VERIFIER_BEHAVIOR_CHANGE = false
FINALIZATION_BEHAVIOR_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
DENSE_REEMBED_REQUIRED = false
SPARSE_INDEX_REBUILD_REQUIRED = false
CORPUS_REINGEST_REQUIRED = false

QA_RUNS = 0
RETRIEVAL_RUNS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0

NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```

The QA/retrieval counters above refer to scientific or live product runs; synthetic unit calls to a fake reranker are test execution and generate no model cost. Prompt, schema, source corpus, embeddings, index, calibration, protected data, and all historical regression artifacts remain unchanged. No release or acceptance candidate is frozen by this ordinary development task.

## Lifecycle and next task

```text
PHASE_G = IN_PROGRESS / G4_R2_COLLATERAL_RETENTION_IMPLEMENTATION_COMPLETE
G4 = DETERMINISTIC HARNESS COMPLETE / EXPOSED R2 BENEFIT OBSERVED / HISTORICAL R2 COLLATERAL COMPLETENESS REGRESSION ESTABLISHED / COLLATERAL RETENTION CORRECTION IMPLEMENTED / DETERMINISTIC RED→GREEN PASS / EXISTING R2 CONTROLS PASS / G4 DUAL-SIDED SAFETY PASS / EXPOSED POST-CORRECTION EMPIRICAL RESULT NOT_YET_ESTABLISHED / FRESH GENERALIZATION BENEFIT NOT_ESTABLISHED
G3_ADMISSION = NO_CHANGE
FRESH_LANE_B = OPTIONAL / DEFERRED
NEXT_TASK_RECOMMENDATION = G4 POST-CORRECTION EXPOSED VERIFICATION DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

The next recommendation is design-only and requires separate authorization. It must decide the smallest exposed verification scope without assuming that either a targeted rerun or a complete 28-case rerun is already justified. No G5 or protected evaluation is authorized here.

STOP.
