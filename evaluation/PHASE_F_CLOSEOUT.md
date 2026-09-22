# Phase F Final Closeout

## 1. Original purpose

Phase F, **Benchmark dependency cleanup and final answering**, covered residual dependency inventory (F1), generic guard and completeness cleanup (F2), fixed locator/fallback retirement (F3), generation/verification role separation (F4), a bounded safe answer composer (F5), and release/generalization evaluation (F6). Its engineering objectives were broader than the F6 release gate. Completing that bounded architecture and achieving release readiness are separate decisions.

This documentation-only closeout starts at `df60810262cb8c6967ef41816d8ba372b43d2f09` (`Record replacement T2 after Vertex compatibility repair`). It changes current lifecycle interpretation and future planning only. Historical records, contracts, verdicts, and usage remain unchanged; no new scientific observation is made.

## 2. F1–F5 terminal accomplishments

**F1 = COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED.** Established a bounded inventory of residual benchmark dependencies and their owners, without repeating already-reconciled D4 migrations. The inventory distinguished cleanup targets, retained general mechanisms, and deferred ownership. Evidence: [F1 inventory](F1_RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY.md) and [PF-LR1 scope reconciliation](PF_LR1_PHASE_F_SCOPE_RECONCILIATION.md).

**F2 = COMPLETE / PASS / GENERIC_BENCHMARK-SPECIFIC_GUARD_CLEANUP_COMPLETE.** Restored verifier whole-claim semantic authority and removed benchmark-specific deterministic support bypasses. Pointer/completeness targets derive from live questions; coverage modes no longer retain legacy completeness authority. Unsupported-symbol and refusal semantics were generalized, and source obligations derive from question requirements instead of fixed intent mappings within the accepted cleanup scope. The accepted F2-A1 through F2-A5 outcomes include their corrective R1 closeouts. Later F6 failures do not invalidate this bounded engineering acceptance. The [roadmap F2 record](../docs/GENERALIZATION_ROADMAP.md#f2--generalize-benchmark-specific-guards) retains the individual reports and limitations.

**F3 = COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED.** Removed the feedback fixed-page override, the `PndPidCorrelator.h` fixed fallback, and the `ana_dpm.C` / `event_poca` fixed fallback. Generic question-grounded behavior replaced those code-origin shortcuts without reopening the separate D4 inventory. Evidence: [F3 closeout](F3_FIXED_LOCATOR_FALLBACK_CLEANUP.md).

**F4 = COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED.** Established independent generation and semantic-verification client roles and role-specific accounting. Semantic entailment remains the verifier's responsibility; deterministic logic owns integrity and provenance checks. Separate client roles do not assert independent model errors or require different model IDs. Evidence: [F4](F4_GENERATION_VERIFICATION_ROLE_SEPARATION.md) and [F4-R1 role diagnostics](F4_R1_PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTION.md).

**F5 = COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED.** Established verified-claims-only composition, deterministic provenance checks, bounded semantic review, and safe deterministic fallback, with the F5-R1 exact-literal correction included. `READABILITY_BENEFIT = NOT_EMPIRICALLY_ESTABLISHED`: the safety acceptance does not establish empirical composer benefit. Evidence: [F5](F5_BOUNDED_ANSWER_COMPOSER.md) and [F5-R1](F5_R1_EXACT_LITERAL_IDENTIFIER_PROVENANCE_REPAIR.md).

## 3. F6 terminal release result

```text
F6 = COMPLETE / FAIL / EXPOSED_RELEASE_GATE_NOT_PASSED
F6_A = CLOSED / TERMINAL_EXPOSED_GATE_FAIL
F6_A_REPAIR_LOOP = CLOSED
ATTEMPT_6 = NOT_PLANNED / PHASE_F_CLOSED
F6_B = NOT_RUN / EXPOSED_RELEASE_GATE_NOT_PASSED
GENERALIZATION_RELEASE_EVIDENCE = NOT_ESTABLISHED
```

F6 was the release/generalization gate. Across its attempts and follow-up work, exposed observations prompted corrections to obvious refusal/status defects, evidence retention and evidence roles, Gold contracts, identifier evaluation, completeness handling, and release infrastructure/provenance. Those corrections did not produce a passing exposed release gate or establish release readiness.

Attempts [1](F6_A_PRERELEASE_VALIDATION_AND_GENERALIZATION_GATE.md), [2](F6_A2_PRERELEASE_VALIDATION_RESULT.md), [3](F6_A3_PRERELEASE_VALIDATION_RESULT.md), [4](F6_A4_PRERELEASE_VALIDATION_RESULT.md), and [5](F6_A5_PRERELEASE_VALIDATION_RESULT.md) never progressed beyond exposed Stage A1. Their historical FAIL outcomes remain unchanged.

| Later release stage | Terminal disposition |
|---|---|
| A2 ablation | NOT_REACHED |
| A3 release-stage novel_dev | NOT_REACHED |
| A4 novel_validation | NOT_REACHED |
| A5 composer empirical audit | NOT_REACHED |
| F6-B protected holdout | NOT_RUN |

F6-B was not executed and is not classified as failed. Historical repeat-policy eligibility remains a record of the earlier policy; it does not schedule an F6-A Attempt 6 continuation of this lineage. A future materially developed product may be considered for a new release-candidate evaluation under the transition rule in section 7.

## 4. Post-A5 interpretation

The Post-A5 line produced retained engineering improvements: O1 stage observability; EA1 exact backing for selected Sphinx parent-page evidence; C1 relationship-aware coverage-satisfaction review; C1-R1 verified revision authority and diagnostic consistency; and Vertex repairs restoring real-provider structured-schema compatibility. These remain product architecture, with their bounded engineering acceptance intact.

The [replacement T2](POST_A5_T2_REPLACEMENT_RESULT.md) nevertheless established `POST_A5_REPAIR_VALIDATION = COMPLETE / FAIL / REPLACEMENT_T2_VALIDATION`:

| Case | Historical replacement-T2 verdict |
|---|---|
| g011 | PASS |
| g010 | CONTROL_PASS |
| g013 | FAIL |
| g014 | CONTROL_PASS |
| g023 | FAIL |
| g022 | CONTROL_PASS |
| g047 | FAIL |
| g050 | CONTROL_FAIL |

g011's PASS applies to the requested negative-existence sentinel; its uncovered native-documentation evidence role remains separately reported and non-gating. The retained mechanisms are not sufficient proof of completeness recovery. Historical T1, infrastructure-invalid T2, replacement T2, and all compatibility-repair records remain immutable.

Replacement T2 remains exposed repair-target evidence, not independent generalization evidence. The late Phase-F lifecycle accumulated excessive validation/governance iteration around an exposed benchmark. Future development must target general mechanisms and increasingly fresh development evidence; repeated exposed-Gold release attempts must not be the normal product-development loop.

## 5. Protected-data state

`novel_validation` was not used for Phase-F repair tuning and remains `PRISTINE_FOR_CURRENT_LINEAGE`. Protected holdout access = `0`; protected leakage = `0`; F6-B execution = `0`. This task did not inspect protected question/Gold content, collect new evaluation data, or run any QA, retrieval, embedding, external judge, T2–T5, novel cohort, or release stage. These statements preserve the recorded exposure boundary; they are not new validation measurements.

## 6. Final Phase-F classification

```text
PHASE_F = COMPLETE / CORE_GENERALIZATION_ENGINEERING_COMPLETE / RELEASE_READINESS_NOT_ACHIEVED
```

This mixed terminal classification closes the bounded engineering phase while explicitly recording that release readiness and generalization release evidence were not achieved. Phase F as a whole is assigned neither PASS nor FAILED. F1–F5 retain their bounded PASS acceptance; F6 retains FAIL. Completing the documentation closeout does not upgrade either scientific result.

The product identity remains:

```text
CURRENT_PRODUCT_BEHAVIOR_LINEAGE_HEAD = 58bd53a86627ff0e0b668915076d974272e86233
NORMAL_PRODUCT_MODE = production_answer_obligations_v1
PROMPT_SET_VERSION = 3.11.2
PROMPT_FINGERPRINT = 878caffb022dd66111b3bc6e98c6e372340cb619db13aa856c09aaa09e8b8391
ACTIVE_GOLD = m6-benchmark-v2.11
ACTIVE_CALIBRATION = phase_b_t3_product_language_scope_v8

SOURCE_CHANGE = false
MATERIAL_PRODUCT_CHANGE = false
PROMPT_CHANGE = false
EVALUATOR_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
```

Verification scope is static documentation consistency and the three-file diff only. No tests or scientific evaluations are required or executed. This closeout adds no companion JSON, hashes, frozen candidate, or further lifecycle artifact family.

## 7. Transition rule to Phase G

[Phase G — Answer Semantics & Robustness](../docs/GENERALIZATION_ROADMAP.md#phase-g--answer-semantics--robustness) is `PLANNED / NOT_STARTED`. It is ordinary product development around question-derived relationships, local review failure containment, evidence-to-answer continuity, false-refusal control, fresh development evidence, and lean validation. The roadmap sequences G1 relationship-aware obligations, G2 local review robustness, G3 admission/answerability audit, G4 false-insufficiency regression, G5 compatible integration, and G6 fresh development evaluation. G3 policy changes require an established generic defect; G5 follows justified G1–G4 work.

Future development uses fresh `novel_dev` as its main empirical evidence. The old exposed eight-case cohort becomes `NON_GATING REGRESSION DIAGNOSTICS`, without changing its historical outcomes or making it the optimization target. Phase-level `novel_validation` requires satisfactory generic deterministic/adversarial checks, satisfactory fresh `novel_dev` evidence, no unacceptable exposed regression, and separate authorization. It remains pristine until that boundary.

Only after material future product development and phase-level validation should a separately authorized **Release Candidate Evaluation** be considered, potentially including protected `novel_holdout` under the release/T5 policy. It is not pre-named F6-A Attempt 6. No Phase-G implementation, candidate version reservation, scientific evaluation, or protected-data access is authorized by this closeout.

```text
NEXT_TASK_RECOMMENDATION = G1 RELATIONSHIP-AWARE ANSWER OBLIGATION DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
STOP.
```
