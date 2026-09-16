# Post-A3 Residual Completeness and Gold Governance Reconciliation

## Terminal verdict

COMPLETE / PASS / PRODUCT_REPAIR_DEFERRED_GOLD_GOVERNANCE_RECONCILED

Starting HEAD: b8dea8f7e5a3da26ba3eccae4c6b4dfc0f57b4a7. Accepted infrastructure repair: 74af96ae7d2ce18e44c6c9e6e7d1ad93d593fdd0. Accepted product-development HEAD: d3a1b274b2784399a7dc51b094a17e466d208b50. The initial worktree contained only the regenerable data/_a3_gold_args.txt scratch file.

Attempt 1, Attempt 2, and Attempt 3 remain historical COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED outcomes. Attempt-3 accounting remains 397 calls / 3,783,197 tokens for 59 records (58 scored and one g013 provider-429 exception). The post-terminal g013 diagnostic remains separate at 10 calls / 62,370 tokens and was not rescored into Attempt 3.

## Product residual evidence

| Case | Evidence and requirements | Verification and exact loss point | Disposition |
|---|---|---|---|
| g022 | Both RHO pages reached selected context and combined candidate recall was 1.0, but the legacy path derived no independent obligation for the two requested pages. | The single data-access claim was supported, so no missing-requirement signal targeted the PID page. Loss occurred in conjunctive obligation representation and initial claim generation. | DEFERRED_NO_SAFE_GENERIC_FIX |
| g023 | Task and workflow-order evidence reached selected context; workflow_order was represented. | The initial ordering claim was correctly rejected. Revision did not produce a verifiable replacement, and safe salvage removed only the unsupported claim. Faithfulness controls operated correctly. | DEFERRED_NO_SAFE_GENERIC_FIX |
| g013 diagnostic | Both groups reached candidate recall (1.0); final evidence recall was 0.5 and answer-point coverage was 0.6667. | Locally supported broad claims left no targeted missing-lifecycle signal. Loss occurred in answer granularity and obligation specificity. | DEFERRED_NO_SAFE_GENERIC_FIX / DIAGNOSTIC_ONLY |

The cases share the symptom that available evidence can disappear before the final answer, but they do not establish one deterministic defect. g022 lacks a tracked conjunctive obligation; g023 has the obligation but correctly preserves faithfulness when revision fails; g013 is a diagnostic granularity gap. A conjunction splitter would over-split compound phrases, weakening verification would violate faithfulness, and promoting experimental coverage architecture would exceed F2-A3-R1 authority.

## Product repair

NO_SAFE_GENERIC_FIX. No product, prompt, verifier, retrieval, composer, or coverage-mode file changed. The default remains legacy_question_core; shadow_e1_v2 and runtime_e1_v2 retain their accepted authority boundaries.

## Gold governance matrix

| Case | Literal requirement and Gold contract | Source-level and cohort finding | Decision |
|---|---|---|---|
| g011 | Compare generic native and container setup; Gold requires both documentation roles. | GSI-specific installation is not equivalent to the generic native path. The answer dropped generic/container evidence. | KEEP_AS_IS / PRODUCT_RESIDUAL |
| g044 | Explain angular acceptance; Gold pins Pflueger 2017 theory. | Li 2026 is topically supportive, but exact authoritative equivalence to the foundational proposition was not established. | KEEP_AS_IS / PRODUCT_RESIDUAL |
| g060 | Explain implementation; Gold v2.9 requires paper plus two code groups. | Code fully supports p1-p3; the paper adds no indispensable point. Direct peer g059 has the same implementation form and is code-only. The paper obligation conflicts with F2-A5 raw-question semantics. | CODE_ONLY_REQUIRED_SOURCE / FORWARD_ONLY_CORRECTION |
| g115 | Explain a troubleshooting confusion; Gold includes an operational disambiguation check. | Troubleshooting peers g109, g114, and g116 also require actionable checks, so p3 is cohort-consistent. | KEEP_AS_IS / PRODUCT_RESIDUAL |

The general governance principle is that a hard source obligation must be entailed by the raw question and contribute indispensable content, with direct peer cases applying the same rule. A failed run alone never justifies relaxing Gold.

## Gold authority

m6-benchmark-v2.10 is the forward-only authority for a future authorized attempt.

- Dataset SHA-256: bdce5cbdc0a6f1645d7350b87bc2f289265c3d67311dab4b12e488b9dc499513.
- Base v2.9 SHA-256: eaacd3ed6595821b24b28823c6344abc4dfb954eb71846e682080b42c2f689be.
- Changed case: g060 only.
- Removed: g060.e1 and the hard paper source obligation.
- Preserved: g060.e2/e3, query, intent, status, split, language, answer points, identifier, and review metadata.
- Counts remain 120 questions, 80/24/16 splits, and 102/10/8 statuses.
- Patch SHA-256: b5383c943723ca3de216287c800044c087cd52072fa7bdad34edca29eab637d6.
- Change-report SHA-256: ff7e2c9c70bea21d71fb643ce951a9d967582b6cda954f44ed761f533da59d66.

Gold v2.9 remains byte-identical and is the exclusive Attempt-3 authority. Attempt 3 was not rescored.

## Calibration authority

phase_b_t3_product_language_scope_v7 is bound to v2.10.

- Artifact SHA-256: ad68df096fc82d6c52bd984e44e99573e6b47e5047b3d522ae750a93188c49cd.
- Formal-English IDs: 59; non-English IDs: 21.
- Selector SHA-256: e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5.
- Membership, classifications, and overrides are identical to v6.
- Compatibility validation passed.

## Verification

Gold validation reported 120 approved questions, structurally valid, official-ready, zero unknown source versions, and zero unmatched evidence groups. Semantic comparison found all 119 non-g060 cases identical and the exact intended g060 delta. Authority resolution selected v2.10 and calibration v7.

Five direct authority regression tests passed. The coupled filtered suite passed 92 tests and 18 subtests with two known unrelated failures deselected. The complete coupled suite reported 92 passed, 18 subtests passed, and two failures that were already present in the pre-edit AGY baseline: test_aggregate_metrics_and_gate_are_deterministic and test_development_gate_is_mode_aware_and_requires_full_dev. The stale v2.6 authority expectation found by that baseline was corrected and now passes. Git diff checks passed.

## Scientific and protected accounting

PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0

novel_validation = PRISTINE_FOR_CURRENT_LINEAGE
holdout access = 0
protected-content leakage = 0
F6-B execution = 0

## Candidate and readiness state

NEW_CANDIDATE_DEVELOPMENT_HEAD = d3a1b274b2784399a7dc51b094a17e466d208b50

candidate frozen = false
Attempt 4 preregistered = false
Attempt 4 executed = false
ATTEMPT_4_READINESS = READY

Readiness means no additional safe, high-confidence generic product repair was established, Gold v2.10 and calibration v7 are coherent, change-relevant deterministic validation passes, and no governance defect invalidates a mandatory gate. It does not predict PASS or authorize execution.

Gold governance commit: 208d0ed68020ae509ec1cfe2d848a339b2c6a996 (Reconcile forward Gold contracts). No product repair commit was created. Nothing was pushed.

NEXT_TASK_RECOMMENDATION = F6-A ATTEMPT 4 / FRESH PREREGISTRATION, CANDIDATE FREEZE, AND CONTINUOUS PRE-RELEASE VALIDATION

NEXT_TASK_EXECUTION_AUTHORIZED = false
