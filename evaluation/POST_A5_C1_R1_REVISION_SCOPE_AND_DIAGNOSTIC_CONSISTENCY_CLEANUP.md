# POST-A5 C1-R1: Revision Scope and Diagnostic Consistency Cleanup

Result: **PASS** for the bounded deterministic contract cleanup. Scientific effect not yet evaluated.

## Identity and lineage

- Starting HEAD: `89b9fac18acb07f181f5a7ccf8eb703c5ff2a7c7` (clean).
- Implementation commit and new behavior head: `6ed3ba361476b36744c72e76f5905733b1755f5c`.
- Previous behavior head: `5e0a3a3ae4828ea3b5831646e3d5d2c8f08cc9ed`.
- `final_head` at record creation: `6ed3ba361476b36744c72e76f5905733b1755f5c`. The subsequent docs-only closeout commit contains this record; its actual final repository HEAD is reported in the delivery message. A commit cannot embed its own SHA. The docs commit does not advance behavior lineage.
- Prompt version: `3.11.0` -> `3.11.0`.
- Canonical fingerprint before/after: `03e1bf270898b28127a42fa2e1ccb24cfc1d87e177eeba5428ba4680d426352c` (mechanically recomputed with starting-HEAD and current runner; prompt blobs unchanged).

## Corrections

- **R1-A:** Persist only eligible unsupported claims and their accepted verifier mappings; copy mappings into the private A1 claim projection without mutating draft/public claims. Empty mappings retain factual repair but add no point; changed mappings replace draft proposals; relationship IDs and verified repair mappings form an ordered unique union in runtime point order.
- **R1-B:** Use actual public result claims for rendered audit in C1 partial finalization; dropped claims remain false. Existing unrelated refusal/historical behavior unchanged.
- **R1-C:** An uncertain relationship requires uncertain point scope. ESTABLISHED plus visible-only stays valid, incomplete and non-revisionable. OVERFLOW stays incomplete and non-revisionable without forcing uncertainty; uncertain checks cannot contradict OVERFLOW.

Eligibility is unchanged: known reviewable, unsupported, non-irrelevant claim with nonempty entirely admitted citations. The bounded private mapping state is cleared when no eligible repairs exist. No public DTO, coverage schema fields/bounds/private version or prompt changed.

## Verification and cost

- RED before source edits: 6 failed, 2 passed, 69 deselected (`-k test_r1`). Failures directly exposed the three seams; mapping tests cover empty, changed and mixed cases plus deduplication.
- Final GREEN: all 77 C1 tests passed, including the 8 R1 cases, visible-only full flow, overflow, and one-revision bound.
- Existing focused regression batch: 421 passed, 49 subtests passed, one isolated pre-existing stale `v2_6` default assertion failed against actual `v2_11`. Runner, prompts and regression test were compared to starting-HEAD blobs; the starting-HEAD runner was loaded in memory and the same failure reproduced. No unrelated repair or full suite.
- Intermediate implementation runs and their corrected placement/encoding issue are recorded explicitly in the JSON; they are not presented as pre-change RED evidence.
- Source/test diff reviewed and `git diff --check` passed. Exactly `qa.py` and the focused C1 test changed in the implementation commit.
- Scientific/evaluation calls = **0**; tokens = **0**. All tests used deterministic fixtures/fake clients. No replay, rescore, external judge, embedding or real QA generation.

Focused regression files:

- `tests/unit/test_qa.py`
- `tests/unit/test_e2_a1_answer_point_coverage.py`
- `tests/unit/test_generic_answer_obligation_completeness.py`
- `tests/unit/test_post_a5_generic_product_repair.py`
- `tests/unit/test_post_a5_o1_observability.py`
- `tests/unit/test_post_a5_ea1_exact_backing.py`
- `tests/unit/test_evaluation_runner.py`
- `tests/unit/test_f6_release_identity.py`
- `tests/unit/test_e3_missing_point_retrieval.py`

## Preservation

- **max_revision:** 1
- **O1:** 33 focused tests pass; actual A1 scope is already observable in A1_INPUT; trace ON/OFF remains behavior-neutral; no event/schema expansion
- **EA1:** 52 focused tests pass; resolver, predicate, admission cache, storage queries and reason codes untouched
- **historical_modes:** Existing QA/answer-point/generic regressions pass; production-only guards preserve shadow_e1_v2, runtime_e1_v2 and legacy_question_core
- **model_retrieval_embedding:** No new stage or call site. Existing fake-client call ceilings and retrieval/embedding assertions pass; C1 recovered complete path remains seven model calls, one retrieval, zero embedding calls. Input correction may affect real model responses, not a claim of scientific output invariance.

## Materiality and lifecycle

`SOURCE_CHANGE = true`, `MATERIAL_PRODUCT_BEHAVIOR_CHANGE = true`, `MATERIAL_PRODUCT_CHANGE = true`.
Prompt/schema contract, fingerprint/version, public DTO, evaluator, Gold, calibration, retrieval policy, EA1 and D0 changes are all **false**.

C1 = IMPLEMENTED / DETERMINISTICALLY VERIFIED / MATERIAL PRODUCT CHANGE / C1-R1 CONTRACT CLEANUP COMPLETE / SCIENTIFIC EFFECT NOT YET EVALUATED.
C1 CONTRACT CLOSEOUT = PASS. The requested temporary `PASS_WITH_BOUNDED_R1_REQUIRED` literal was not present in the starting current-status docs; they are reconciled forward to this actual result. Historical C1 artifacts remain unchanged.

T1 remains COMPLETE / FAIL, 65 calls / 373,265 tokens. No g013/g023 fix is claimed.
`novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`; holdout access, protected-content leakage and F6-B execution = 0 (non-access preserved).
Candidate frozen = false; Attempt 6 preregistered/executed = false; `ATTEMPT_6_READINESS = NOT_READY`.

Limitations: model semantic correctness and scientific improvement remain unmeasured; the known unrelated stale test remains failing. This is not a formal acceptance comparison or the subsequent integration closeout.

Next recommendation: POST-A5 O1+EA1+C1 DETERMINISTIC INTEGRATION CLOSEOUT.
`NEXT_TASK_EXECUTION_AUTHORIZED = false`.
