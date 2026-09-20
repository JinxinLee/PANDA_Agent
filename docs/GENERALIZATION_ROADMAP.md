# PANDA Agent — Generalization Roadmap

## Purpose and development principles

The Generalization Phase moves PANDA Agent away from benchmark-dependent behavior toward reusable question understanding, structured domain knowledge, retrieval, evidence selection, grounded claims, answer decomposition, and verification. Existing compatibility behavior remains until generic replacements have been measured.

The roadmap is governed by the following core development principles:

* **Measurement over specification:** Evaluation questions are measurement data, never implementation specifications.
* **Generic mechanisms over bespoke fixes:** Prefer generic architectural mechanisms over benchmark- or case-specific fixes.
* **Preserve domain knowledge:** Preserve legitimate terminology, aliases, normalization, and domain knowledge; do not treat all domain guidance as removable shortcuts.
* **Evidence-based retirement:** Retire shortcuts only when a generic replacement or safe retirement is sufficiently evidenced.
* **Proportional evaluation:** Use the smallest evaluation tier and cohort sufficient to answer the architectural question.
* **Valid non-positive outcomes:** `HOLD`, `DEFERRED`, and `INCONCLUSIVE` are valid and acceptable engineering outcomes when evidence or natural applicability is insufficient.
* **Lean execution:** Avoid unnecessary defensive programming; do not create unnecessary retries, broad tests, hash inventories, or redundant lifecycle stages.
* **Direct mechanical activation:** Once a validated production mapping is mechanically determined, it does not require redundant preregistration.
* **Protected evaluation ladder:** Maintain a strict evaluation hierarchy consisting of `novel_dev` (development-exposed), `novel_validation` (unseen validation), and `novel_holdout` (externally managed sealed holdout).

> **Roadmap governance:**
> This document is a planning roadmap, not a single implementation task.
> Implementation must address only the task explicitly requested and authorized.
> Statuses describe implementation state; acceptance targets remain planned until measured.
> Planning states do not authorize future execution.

## Current planning state

E1-CLOSURE-REVIEW = COMPLETE / PASS / REAL_PANDA_STYLE_CONFIRMATION_REQUIRED_BEFORE_CLOSURE.
E1-C1 = COMPLETE / PASS / REAL_PANDA_STYLE_EXPOSED_DEVELOPMENT_CONFIRMATION_PASSED.
E1 = COMPLETE / PASS / QUESTION_ONLY_SEMANTIC_ANSWER_POINT_DECOMPOSITION_VALIDATED.
E2-A1 = COMPLETE / PASS / SHADOW_ANSWER_POINT_COVERAGE_CONTRACT_IMPLEMENTED.
E2-A2 = COMPLETE / PASS / TARGETED_CLAIM_MAPPING_AND_MISSING_POINT_VALIDATION_PASSED.
E2-A2 report: `evaluation/E2_A2_TARGETED_CLAIM_MAPPING_VALIDATION.md`.
E2-A3 = COMPLETE / FAIL / Q7.
E2-A3 report: `evaluation/E2_A3_RUNTIME_ACTIVATION_REGRESSION.md`.
E2-A3 FAILURE REVIEW = COMPLETE / PASS / Q7_VERIFIER_IDENTIFIER_NORMALIZATION_REPAIR_JUSTIFIED.
Review: `evaluation/E2_A3_Q7_FAILURE_REVIEW.md`.
E2-A3-R1 = COMPLETE / FAIL / P2_P6.
R1 report: `evaluation/E2_A3_R1_IDENTIFIER_NORMALIZATION_REPAIR.md`.
E2-A3-R1 FAILURE REVIEW = COMPLETE / PASS / P2_REPAIR_REQUIRED_P6_NO_PRODUCT_REPAIR.
P2/P6 review: `evaluation/E2_A3_R1_P2_P6_FAILURE_REVIEW.md`.
E2-A3-R2 = COMPLETE / PASS / CITATION_ELIGIBLE_EVIDENCE_SELECTION_REPAIR_VALIDATED.
R2 report: `evaluation/E2_A3_R2_CITATION_ELIGIBLE_EVIDENCE_REPAIR.md`.
E2-A3-R3 = COMPLETE / INCONCLUSIVE / CONNECTION_TIMEOUT_AND_PROVIDER_429_INCOMPLETE_PAIRS.
E2-A3-R3-R1 = COMPLETE / FAIL / G11.
E2-A3-R3-R1 G11 FAILURE REVIEW = COMPLETE / PASS / PRODUCT_REPAIR_AND_GATE_REDESIGN_RECOMMENDED.
G11 review: `evaluation/E2_A3_R3_R1_G11_FAILURE_REVIEW.md`.
Recovery report: `evaluation/E2_A3_R3_R1_INFRASTRUCTURE_RECOVERY.md`.
R3 report: `evaluation/E2_A3_R3_RUNTIME_ACTIVATION_REASSESSMENT.md`.
Historical A3/R1 activation gates failed; R2 passed bounded repair validation only. No runtime default promotion occurred.
Normal default = `legacy_question_core`; runtime activation did not occur.
E2 = COMPLETE / CORE_MECHANISM_VALIDATED / DEFAULT_PROMOTION_DEFERRED.
E2-LR1 = COMPLETE / PASS / POST_A3_LIFECYCLE_RECONCILED.
QA-M1 = COMPLETE / PASS / GENERIC_CLAIM_SANITIZATION_REPAIR_VALIDATED.
Maintenance report: `evaluation/QA_M1_GENERIC_CLAIM_SANITIZATION_REPAIR.md`.
E3-A0 = COMPLETE / PASS / MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT_ESTABLISHED.
E3-A0 report: `evaluation/E3_A0_MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT.md`.
E3-A1 = COMPLETE / PASS / EXPERIMENTAL_MISSING_POINT_TARGETED_RETRIEVAL_IMPLEMENTED.
E3-A1 report: `evaluation/E3_A1_EXPERIMENTAL_MISSING_POINT_RETRIEVAL_IMPLEMENTATION.md`.
E3-A2 = COMPLETE / INCONCLUSIVE / INSUFFICIENT_NATURAL_MISSING_POINT_APPLICABILITY.
E3-A2 report: `evaluation/E3_A2_TARGETED_MISSING_POINT_RECOVERY_VALIDATION.md`.
E3-LR1 = COMPLETE / PASS / POST_A2_LIFECYCLE_RECONCILED.
E3-LR1 report: `evaluation/E3_LR1_POST_A2_LIFECYCLE_DECISION.md`.
E3 = COMPLETE / BOUNDED_LOW_FREQUENCY_FALLBACK_IMPLEMENTED / SCIENTIFIC_RECOVERY_BENEFIT_UNRESOLVED.
E2-A3-R4 = NOT_STARTED / SUPERSEDED_BY_LIFECYCLE_SIMPLIFICATION.
E2 DEFAULT PROMOTION = DEFERRED / ACTIVATION_ACCEPTANCE_NOT_MET.
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY.
E2 DEFAULT-PROMOTION GATE REDESIGN = CLOSED / NO_IMMEDIATE_REVALIDATION_DEFINED / REOPEN_ONLY_FOR_PROMOTION_RELEVANT_MATERIAL_CANDIDATE_OR_RELEASE_BOUNDARY.
DEFAULT_PROMOTION_RECONSIDERATION_TRIGGER = a promotion-relevant materially behavior-changing post-Phase-E candidate that either (1) materially affects the unresolved default-promotion failure surface (completeness, verification, compatibility, evidence-selection, or other behavior implicated in the failed activation lineage — normally Phase-F cleanup of F1-R08/R09/R11, R13, R10, R14, R04) or (2) otherwise creates a decision-relevant new integrated runtime candidate whose default acceptance needs assessment; OR (3) an explicitly authorized release/acceptance candidate evaluation requiring the normal-default decision.
PE-LR1 = COMPLETE / PASS / PHASE_E_CLOSED_PROMOTION_DEFERRED_UNTIL_MATERIAL_CANDIDATE.
PE-LR1 report: `evaluation/PE_LR1_PHASE_E_PROMOTION_BOUNDARY_RECONCILIATION.md`.
PF-LR1 = COMPLETE / PASS / PHASE_F_SCOPE_RECONCILED_BOUNDED_CLEANUP_PLAN_ESTABLISHED.
PF-LR1 report: `evaluation/PF_LR1_PHASE_F_SCOPE_RECONCILIATION.md`.
F2-A1 = COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED.
F2-A1 report: `evaluation/F2_A1_VERIFIER_SUPPORT_SEMANTIC_CLEANUP.md` (initial closeout corrected by F2-A1-R1).
F2-A1-R1 = COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED.
F2-A1-R1 report: `evaluation/F2_A1_R1_VERIFIER_SUPPORT_SEMANTIC_ENTAILMENT_REPAIR.md`.
F2-A2 = COMPLETE / PASS / QUESTION_DERIVED_POINTER_NORMALIZATION_COMPLETENESS_ESTABLISHED.
F2-A2 report: `evaluation/F2_A2_DETERMINISTIC_COMPLETENESS_SEMANTIC_CLEANUP.md`.
F2-A3 = COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED.
F2-A3 report: `evaluation/F2_A3_E1_E2_COMPATIBILITY_RETIREMENT.md` (initial closeout corrected by F2-A3-R1).
F2-A3-R1 = COMPLETE / PASS / COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REMOVED.
F2-A3-R1 report: `evaluation/F2_A3_R1_COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REPAIR.md`.
F2-A4 = COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED.
F2-A4 report: `evaluation/F2_A4_PREMISE_REFUSAL_GENERALIZATION.md` (initial closeout corrected by F2-A4-R1).
F2-A4-R1 = COMPLETE / PASS / QUESTION_GROUNDED_PREMISE_REFUSAL_BOUNDARY_ESTABLISHED.
F2-A4-R1 report: `evaluation/F2_A4_R1_QUESTION_GROUNDED_PREMISE_REFUSAL_REPAIR.md`.
F2-A5 = COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED.
F2-A5 report: `evaluation/F2_A5_SEMANTIC_SOURCE_OBLIGATION_GENERALIZATION.md` (initial closeout corrected by F2-A5-R1).
F2-A5-R1 = COMPLETE / PASS / SOURCE_OBLIGATION_MATCHING_BOUNDARY_ESTABLISHED.
F2-A5-R1 report: `evaluation/F2_A5_R1_SOURCE_OBLIGATION_BOUNDARY_REPAIR.md`.
Reconciliation: `evaluation/E2_POST_A3_LIFECYCLE_RECONCILIATION.md`.
E2-A1 report: `evaluation/E2_A1_SHADOW_ANSWER_POINT_COVERAGE_CONTRACT.md`.
C1 met all eight strict gates and the original pair09 atomicity sentinel. Per the
accepted closure decision, E1 is complete. E2-A2 passed targeted shadow validation. E2-A3 failed Q7; normal QA remains legacy. E3-A0 established the missing-point targeted retrieval contract; E3-A1 implemented the experimental mechanism under runtime_e1_v2; E3-A2 completed INCONCLUSIVE with insufficient natural applicability (1/11); E3-LR1 closed E3 as a bounded low-frequency fallback with standalone recovery benefit unresolved and no dedicated revalidation planned. PE-LR1 closed Phase E at the promotion boundary: architecture complete, normal default remains `legacy_question_core`, promotion deferred until a material candidate change or an explicitly authorized release-boundary decision.
Decision: `evaluation/E1_CLOSURE_SCOPE_REVIEW.md`.
Report: `evaluation/E1_C1_REAL_STYLE_CONFIRMATION.md`.
Preregistration: `2517b691245c38175222064e6ca546d06fd21e9a`.
Raw freeze: `7eab1e8fe099fed6ff06384c4fa0eb48dcf52677`.


Repository planning baseline:
ffedb2117f578515ea9d74eca92105956b8a3dcb (E2-A3 starting HEAD)

Latest accepted production action:
D4-A10
COMPLETE / PASS / VALIDATED_MODEL_FACTORY_LOCATOR_RETIREMENT_ACTIVATED

Phase A:
COMPLETE

Phase B:
COMPLETE
with explicitly deferred residual architecture work where already recorded

Phase C:
COMPLETE / WITH_DEFERRED_COMPONENTS

Phase D:
PAUSED / ROADMAP_RECONCILIATION

Phase E:
COMPLETE / CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED / DEFAULT_PROMOTION_DEFERRED

E1:
COMPLETE / PASS / QUESTION_ONLY_SEMANTIC_ANSWER_POINT_DECOMPOSITION_VALIDATED

E1-A1:
COMPLETE / PASS / QUESTION_ONLY_DIAGNOSTIC_DECOMPOSITION_IMPLEMENTED

E1-A2:
COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED

E1-AR:
COMPLETE / PASS / REVISED_SEMANTIC_ANSWER_POINT_CONTRACT_ESTABLISHED

E1-R1:
COMPLETE / PASS / SHADOW_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIRED

E1-R2:
COMPLETE / PASS / TARGETED_PROSPECTIVE_SEMANTIC_ANSWER_POINT_REVALIDATION_PASSED

E3-A0:
COMPLETE / PASS / MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT_ESTABLISHED

E3-A1:
COMPLETE / PASS / EXPERIMENTAL_MISSING_POINT_TARGETED_RETRIEVAL_IMPLEMENTED

E3-A2:
COMPLETE / INCONCLUSIVE / INSUFFICIENT_NATURAL_MISSING_POINT_APPLICABILITY

E3-LR1:
COMPLETE / PASS / POST_A2_LIFECYCLE_RECONCILED

E3:
COMPLETE / BOUNDED_LOW_FREQUENCY_FALLBACK_IMPLEMENTED / SCIENTIFIC_RECOVERY_BENEFIT_UNRESOLVED

PE-LR1:
COMPLETE / PASS / PHASE_E_CLOSED_PROMOTION_DEFERRED_UNTIL_MATERIAL_CANDIDATE

PF-LR1:
COMPLETE / PASS / PHASE_F_SCOPE_RECONCILED_BOUNDED_CLEANUP_PLAN_ESTABLISHED

F2-A1:
COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED

F2-A1-R1:
COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED

F2-A2:
COMPLETE / PASS / QUESTION_DERIVED_POINTER_NORMALIZATION_COMPLETENESS_ESTABLISHED

F2-A3:
COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED

F2-A3-R1:
COMPLETE / PASS / COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REMOVED

F2-A4:
COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED

F2-A4-R1:
COMPLETE / PASS / QUESTION_GROUNDED_PREMISE_REFUSAL_BOUNDARY_ESTABLISHED

F2-A5:
COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED

F2-A5-R1:
COMPLETE / PASS / SOURCE_OBLIGATION_MATCHING_BOUNDARY_ESTABLISHED

Phase F:
IN_PROGRESS / F6_A_ATTEMPT_3_FAILED

F1:
COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED

F2:
COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE

F3:
COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED

F4:
COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED

F4-R1:
COMPLETE / PASS / PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTED

F5:
COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED

F5-R1:
COMPLETE / PASS / EXACT_LITERAL_IDENTIFIER_PROVENANCE_BOUNDARY_ESTABLISHED

F6:
attempt 1 = HISTORICAL / HOLD (ZERO_OUTCOME); staged by F6-LR1
F6-LR1:
COMPLETE / PASS / RELEASE_GATE_STAGING_RECONCILED
F6-A Attempt 1:
COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.6, historical)
F6-A Attempt 2:
COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.6, historical)
F6-A Attempt 3 Preflight:
HISTORICAL / HOLD / PRE_RELEASE_PRECONDITION_NOT_MET (zero-outcome, unblocked by GOLD-9)
GOLD-9:
COMPLETE / PASS / RELEASE_AUTHORITY_CHAIN_RECONCILED
F6-A Attempt 3:
COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.9 terminal result)
F6-A Attempt 4:
COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.10; 59/59 complete; two mandatory A1 gates failed; A2-A5 NOT_REACHED; novel_validation pristine)
GENERIC ANSWER-OBLIGATION COMPLETENESS (MATERIAL PRODUCT CHANGE ACCEPTED):
COMPLETE / PASS / production_answer_obligations_v1 accepted at development HEAD eda7d932a9b1b7b65436cba01e247859a6f9e056; R1 decomposition prompt release-identity repair completed at 8f61aee414aa9fa2da0e3a6bbb2f767eadb7da4c (identity/provenance-only)
F6-A Attempt 5:
COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.10 under the materially new production_answer_obligations_v1 candidate f6a-rc5-20260919; 59/59 complete after one resume recovering ten retryable transport exceptions; three mandatory A1 gates failed: critical_final_evidence_recall 0.918367, identifier_hallucination_rate 0.046154, critical_answer_point_miss_count 4; release score 0.949153; 563 calls / 3,201,331 tokens; A2-A5 NOT_REACHED; novel_validation pristine)
F6-B:
LOCKED / F6_A_DID_NOT_PASS
POST-ATTEMPT-5 FAILURE OWNERSHIP & GATE VALIDITY REVIEW:
COMPLETE / PASS / FAILURE_OWNERSHIP_AND_GATE_VALIDITY_ESTABLISHED (zero scientific calls; decomposition under-splitting rejected for all four critical answer-point misses — three are A1 obligation-content gaps and g039.p1 is a Gold rubric clause beyond the literal question; five of six critical final-evidence misses are equivalent alternate-source citations against literal pinned groups and g011 is a genuine R2 rerank loss plus V2 corpus-negative false acceptance; all six identifier events are evaluator false positives from the catalog's missing enum-member coverage; gate dispositions: critical_final_evidence_recall REDEFINE_METRIC_REQUIRED, critical_answer_point_miss_count GOLD_RECONCILIATION_REQUIRED, identifier_hallucination_rate EVALUATOR_REPAIR_REQUIRED; all 18 thresholds are inherited frozen M6 constants with no recorded derivation; ATTEMPT_6_READINESS = NOT_READY)

F6-B:
LOCKED / F6_A_DID_NOT_PASS
IDENTIFIER CATALOG EVALUATOR REPAIR + ATTEMPTS 1–5 OFFLINE IDENTIFIER RESCORE:
COMPLETE / PASS / IDENTIFIER_EVALUATOR_REPAIRED_AND_HISTORY_RESCORED (zero scientific calls; `build_identifier_catalog` now harvests qualified scoped identifiers verbatim from allowed locked-corpus text with a namespace-head-guarded tail fallback; generic T1–T8 RED→GREEN suite plus production Attempt-5 regression; offline rescore 0/121→0/121, 0/155→0/155, 0/177→0/177 (58/59 stored), 2/173→0/173, 6/130→0/130 with zero events introduced and denominators reproducing the historical matrices exactly; Attempt-5 counterfactual identifier-gate PASS is COUNTERFACTUAL / NON-AUTHORITATIVE and all five terminal verdicts are unchanged; `MATERIAL_PRODUCT_CHANGE = false`, `EVALUATOR_CONTRACT_CHANGE = true`; a forward-only causal-attribution erratum was appended to the post-A5 review; `ATTEMPT_6_READINESS = NOT_READY`). Identifier metrics and count terminology superseded by the R1 record below.
IDENTIFIER EVALUATOR R1 — EXACT OWNERSHIP + RESCORE PROVENANCE RECONCILIATION:
COMPLETE / PASS / QUALIFIED_SYMBOL_OWNERSHIP_AND_RESCORE_PROVENANCE_RECONCILED (zero scientific calls; `_qualified_symbol_exists` tightened to exact-ownership semantics — a qualified identifier exists only when that exact qualified form is established by allowed locked-corpus evidence; the known-head + unrelated-known-tail combinatorial fallback removed; RED R1-T1 then GREEN 14/14; R1 rescore re-derived identical denominators 121/155/177/173/130 with zero introduced events and all six Attempt-5 false positives still cleared (0/130); provenance reconciled from immutable stores: Attempt 1 = 60 raw rows / 59 unique cases (complete duplicate g119 execution, append-only recovery residue; g119 is insufficient_evidence so neither duplicated row is applicable to the identifier metric), Attempt 3 = 59 rows / 59 unique with preserved g013 Vertex-429 exception row (58 completed; g013 is not a valid applicable identifier measurement record and contributes no identifier measurement), Attempts 2/4/5 clean 59/59; forward-only artifacts reissued as identifier-rescore-r1-v1; all five terminal verdicts unchanged; `ATTEMPT_6_READINESS = NOT_READY`). Provenance schema finalized afterwards: identifier_gold_applicable_case_count (Gold answered semantics, 49 per attempt) and identifier_measured_record_count (49 per attempt; 48 for Attempt 3 — g013 Gold-applicable but unmeasured provider exception) separated, legacy identifier_applicable_case_count removed; `IDENTIFIER PROVENANCE SCHEMA = COMPLETE / PASS / GOLD_APPLICABILITY_AND_MEASUREMENT_SEPARATED`

F6-A EVALUATION-CONTRACT RECONCILIATION — CRITICAL-EVIDENCE EQUIVALENCE + g039 GOLD CORRECTION + HARD-SAFETY RECLASSIFICATION:
COMPLETE / PASS / EVIDENCE_ROLE_GOLD_AND_GATE_CLASSIFICATION_RECONCILED (zero scientific calls; critical-evidence construct = required evidence roles with explicitly reviewed any_of equivalence — Option A, evaluator matching unchanged, threshold 1.00 unchanged; successor Gold m6-benchmark-v2.11 (SHA 39943c6a..., parent v2.10 byte-identical) changes exactly 6 objects: g039 p1 literal-scope correction plus audited role/any_of equivalence selectors for g013/g016/g020/g044/g110 (g044.e1 role renamed angular_acceptance_thesis_theory), g011 deliberately unchanged as the negative control; calibration successor phase_b_t3_product_language_scope_v8 with unchanged memberships and selector SHA; Attempt-5 counterfactual crit-ev 0.918367 -> 48/49 = 0.979592 still FAIL with g011 at 0.0, g039 governance adjudication counterfactual drops critical point misses to 4 -> 3 still FAIL, identifier counterfactual 0/130 PASS; all five formal verdicts unchanged; hard-safety/trustworthiness vs strict-release-quality/completeness gate categories separated for future contracts with thresholds unchanged; NUMERICAL_THRESHOLD_CHANGES = NONE; MATERIAL_PRODUCT_CHANGE = false, EVALUATION_CONTRACT_CHANGE = true, GOLD_SUCCESSOR_CREATED = true; ATTEMPT_6_READINESS = NOT_READY). Record: evaluation/F6_A_EVALUATION_CONTRACT_RECONCILIATION.md.

POST-A5 GENERIC PRODUCT REPAIR — COMPLETENESS RECOVERY + NEGATIVE-EXISTENCE SAFETY:
COMPLETE / PASS / COMPLETENESS_RECOVERY_AND_NEGATIVE_EXISTENCE_CONTRACTS_STRENGTHENED (zero scientific calls; bounded-revision recovery preserves genuinely new revised claims across local-ID collisions with F6-A2-FR2 anti-resurrection and the one-revision bound intact; coverage review now returns and validates a per-runtime-point completeness record separating relevance from completeness with generator mappings non-authoritative; generation and verification contracts forbid corpus-wide absence inferred from a non-exhaustive evidence subset while deterministic exact-absence refusal paths stay authoritative; rerank role preservation DEFERRED (rerank_pool=fused_order[:30] investigated; no safe generic repair; E3 not promoted); prompt fingerprint changed automatically to 0a5b2909... with release-identity tests passing; T0 suite 12/12 (RED 4/8), focused regressions green; current GENERIC_PRODUCT_REPAIR = IMPLEMENTED / DETERMINISTICALLY VERIFIED / T1 SCIENTIFIC EVIDENCE = MIXED / OVERALL T1 = FAIL / GENERAL EFFECT NOT ESTABLISHED; MATERIAL_PRODUCT_CHANGE = true with the product commit as the new behavior lineage head; ATTEMPT_6_READINESS = NOT_READY). Record: evaluation/POST_A5_GENERIC_PRODUCT_REPAIR.md.

POST-ATTEMPT-3 FAILURE & EXECUTION-RECOVERY REVIEW:
COMPLETE / PASS / FAILURES_CLASSIFIED_RECOVERY_INFRASTRUCTURE_REPAIRED_PRODUCT_RESIDUALS_DEFERRED

D4 overall completion:
UNDECIDED

Current task:
POST-A5 O1 BEHAVIOR-NEUTRAL OBSERVABILITY IMPLEMENTATION (COMPLETE / PASS; deterministic validation only; zero scientific calls)
POST_A5_O1 = IMPLEMENTED / DETERMINISTICALLY VERIFIED / BEHAVIOR_NEUTRAL (33 O1 tests PASS; applicable regressions PASS; one unrelated stale v2_6-default test failure reproduced at baseline and not repaired; prompt fingerprint unchanged; scientific usage 0 calls / 0 tokens; SOURCE_CHANGE=true, MATERIAL_PRODUCT_BEHAVIOR_CHANGE=false; behavior lineage remains e79d323). EA1/C1 = DESIGN_COMPLETE / NOT_IMPLEMENTED / NOT_AUTHORIZED; RS DEFER. Record: `evaluation/POST_A5_O1_BEHAVIOR_NEUTRAL_OBSERVABILITY_IMPLEMENTATION.md` (companion JSON).
POST_A5_BOUNDED_PRODUCT_REPAIR_DESIGN = COMPLETE / PASS / BOUNDED_PRODUCT_REPAIR_DESIGN_READY (DESIGN_ONLY; 0 scientific calls / 0 tokens; O1 -> EA1 -> C1 with independent T0 gates; exact unique same-version backing with strict fallback; coverage bounds 4/point, 20 total, 2 basis references/check; RS DEFER; no implementation or scientific validation). Record: `evaluation/POST_A5_BOUNDED_PRODUCT_REPAIR_DESIGN.md` (companion JSON).
POST_A5_T1_FAILURE_REVIEW = COMPLETE / PARTIAL / TRACE_OBSERVABILITY_AND_SEMANTIC_SCOPE_LIMITS_REMAIN (historical review at 09e7759; scientific findings preserved; causal taxonomy and chronology wording superseded forward by the contract reconciliation below).
POST_A5_T1_CONTRACT_RECONCILIATION = COMPLETE / PASS / EVIDENCE_ADMISSION_COVERAGE_SCOPE_AND_OBSERVABILITY_CONTRACT_RECONCILED (static design-only; 0 scientific calls / 0 tokens; EA is post-retrieval admission, not retrieval loss; generation/verification asymmetry INTENTIONAL_BUT_UNDER-SPECIFIED; g013 A1_RECOVERY_OUTCOME = UNSUCCESSFUL / CONFIRMED, A1_CAUSAL_DEFECT = NOT_ESTABLISHED; g023 EA exclusion CONFIRMED, unique/reviewer-only cause NOT_ESTABLISHED; question-only D0 retained, proposed evidence-grounded satisfaction scope belongs to V1/V2; proposed diagnostics.qa_stage_trace and development runner status separation are NOT_IMPLEMENTED). Record: `evaluation/POST_A5_T1_OBSERVABILITY_EVIDENCE_ADMISSION_AND_COVERAGE_SCOPE_RECONCILIATION.md` (companion JSON).
T1_PREREGISTRATION_CHRONOLOGY = VERIFIED_WITHIN_RETAINED_LOCAL_EVIDENCE; EXECUTION_REPOSITORY_HEAD = 421c13a6efc76a845cfd61388e1e2520eea799a7. No external trusted timestamp authority; frozen T1 verdict unchanged.
REVIEW_MATERIALITY: MATERIAL_PRODUCT_CHANGE = false; EVALUATOR_CONTRACT_CHANGE = false; GOLD_CHANGE = false; CALIBRATION_CHANGE = false. Candidate frozen = false; Attempt 6 preregistered = false; Attempt 6 executed = false; ATTEMPT_6_READINESS = NOT_READY.
POST_A5_T1 = COMPLETE / FAIL; g013 FAIL, g023 FAIL, g047 PASS, g011 negative-existence safety PASS; controls 4x CONTROL_PASS; historical usage 65 calls / 373,265 tokens, transport recovery 0. T1 result and Attempt-5 verdict unchanged.
ATTEMPT_5_STATUS = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (historical, immutable)
PREVIOUS_PRODUCT_BEHAVIOR_LINEAGE_HEAD = eda7d932a9b1b7b65436cba01e247859a6f9e056
CURRENT_PRODUCT_BEHAVIOR_LINEAGE_HEAD = e79d3232ed132a224cbceaf3524e19a1406bd648
GENERIC_PRODUCT_REPAIR = IMPLEMENTED / DETERMINISTICALLY VERIFIED / T1 SCIENTIFIC EVIDENCE = MIXED / OVERALL T1 = FAIL / GENERAL EFFECT NOT ESTABLISHED. A: g013 FAIL, revision recovery mechanism not directly observed, exact historical/T1 ID-collision causality NOT_ESTABLISHED. B: g023 FAIL with outcome-level false-acceptance recurrence, g047 PASS, mixed single observations; specific V1-only causality NOT_ESTABLISHED. C: g011 safety PASS, positive single observation, general effect not established; C_NATIVE_DOCUMENTATION_ROLE_COVERAGE = FAIL (legacy T1 C_RETRIEVAL_COMPLETENESS = FAIL means native-documentation role coverage, not no usable native-path information). D: DEFERRED.
NORMAL_PRODUCT_MODE = production_answer_obligations_v1
ATTEMPT_5_PREREGISTRATION_COMMIT = eacbf447eee2527b85e0e47073d8584c64a4a3f4
ATTEMPT_5_CANDIDATE_ID = f6a-rc5-20260919
ATTEMPT_5_CANDIDATE_MANIFEST_SHA256 = db8ba89bd8a7ab490d981c6a49c2ff30f0736bcee2f46e07881efe9979514cc4
ATTEMPT_5_SCIENTIFIC_USAGE = 563 calls / 3,201,331 tokens
ATTEMPT_5_A1 = 59/59 COMPLETE / FAIL (critical_final_evidence_recall 0.918367; identifier_hallucination_rate 0.046154; critical_answer_point_miss_count 4)
STAGES_A2_A5 = NOT_REACHED
PROTECTED_HOLDOUTS = PRISTINE (novel_validation pristine, holdout access = 0)
F6_B = LOCKED / F6_A_DID_NOT_PASS
ATTEMPT_5 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED

Next task recommendation:
POST-A5 EA1 EXACT-BACKING EVIDENCE-ADMISSION IMPLEMENTATION
(REQUIRES SEPARATE AUTHORIZATION; no C1/RS or scientific replay; NO ATTEMPT 6)

Current task authorization:
NEXT_TASK_EXECUTION_AUTHORIZED = false
The authorized O1 implementation is complete and behavior-neutral under deterministic validation. EA1 and C1 remain design-only and require separate authorization; RS remains deferred. The recommendation does not authorize implementation or scientific validation. No historical T1 stages were backfilled.

E3-A2 completed INCONCLUSIVE (1/11 natural applicability; the single applicable pair was descriptive only). E3-LR1 subsequently reconciled the lifecycle with zero scientific calls: E3 closes as a bounded low-frequency fallback (SCIENTIFIC_RECOVERY_BENEFIT_UNRESOLVED); dedicated revalidation is not planned; future E3 evidence accumulates opportunistically in broader authorized evaluations.

No D4-A11 exists.
No further D4 task is currently authorized.
Phase E is COMPLETE (closed by PE-LR1); no further Phase-E task exists. Phase-F scope reconciliation is complete (PF-LR1); F2-A1/F2-A1-R1 verifier-support repair, F2-A2 pointer-normalization completeness cleanup, and F2-A3 E1/E2 compatibility authority reconciliation (completed by F2-A3-R1) and F2-A4 premise/refusal generalization (completed by F2-A4-R1) and F2-A5 semantic source obligation generalization are complete; all five PF-LR1 F2 groups are closed (F2 = COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE). F3 fixed-locator/fallback cleanup (R03/R05/R06) is COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED. F4 generation/semantic-verification role separation is COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED (distinct production client paths, independently configurable verification model, judge isolated offline, role-specific usage accounting), with the role diagnostics corrected by F4-R1 (COMPLETE / PASS / PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTED: the receipt now reports each role client's actual `settings.generation_model`). F5 bounded answer composer is COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED (verified-claims-only input, deterministic provenance validation, one bounded semantic composition review, atomic deterministic fallback; READABILITY_BENEFIT = NOT_EMPIRICALLY_EVALUATED_IN_F5), with exact provenance established by F5-R1 (COMPLETE / PASS / EXACT_LITERAL_IDENTIFIER_PROVENANCE_BOUNDARY_ESTABLISHED: numeric literals and technical identifiers now compare exact extracted tokens with sign/spelling sensitivity and a bounded casing-alteration sentinel, replacing substring membership). F6 release evaluation attempt 1 is HISTORICAL / HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET / ZERO_OUTCOME (valid under the then-authorized protocol). F6-LR1 reconciled the staged release lifecycle (COMPLETE / PASS / RELEASE_GATE_STAGING_RECONCILED). F6-A then executed as the first staged stage (COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED): Stage A0 closed the carried release-freeze engineering debt (signed v2.6 freezer/evaluator authority equivalence, benchmark-manifest identity, Docker Option A, clean-tree freeze + ancestor-HEAD verification, selector-completeness product-gate semantics), the reviewed product-language calibration was mechanically reconciled as successor v3, and the exact 59-ID formal-English Gold cohort ran mode=full under frozen candidate f6a-rc1-20260913 (release score 0.8277). Ten preregistered gates failed — the dominant defect is a pattern of erroneous insufficient-evidence refusals on Gold-answered questions (four claiming "not defined in the locked corpus" against cited contrary evidence) plus two version-conflict handling errors — and the FAIL was frozen before exposing ablation/novel_dev/novel_validation/composer-audit cohorts (novel_validation remains pristine). F6-B is LOCKED; a repaired candidate requires a separately authorized post-F6-A failure review, new candidate work, and a new F6-A attempt.
No further Phase-F production task is currently authorized. POST-ATTEMPT-3 FAILURE AND EXECUTION-RECOVERY REVIEW is COMPLETE / PASS and its recovery/receipt mechanisms were used by F6-A Attempt 4. Attempt 4 is COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED on Gold v2.10: 59/59 complete after two retryable `g112` recoveries, release score 0.971751, mandatory failures in critical final-evidence recall and critical answer-point misses, 388 calls / 3,647,993 tokens. A2-A5 were not reached, novel_validation remains pristine, and F6-B stays locked. Report: `evaluation/F6_A4_PRERELEASE_VALIDATION_RESULT.md`. A materially new candidate (generic answer-obligation completeness, `production_answer_obligations_v1`, development HEAD `eda7d932a9b1b7b65436cba01e247859a6f9e056`, release-identity repair `8f61aee`) then legitimately opened Attempt 5 under the formal repeat policy. Attempt 5 is COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED on Gold v2.10: 59/59 complete after one resume recovering ten retryable transport exceptions, release score 0.949153, mandatory failures in critical final-evidence recall (0.918367), identifier hallucination rate (0.046154; LumiFit identifiers on g060/g113), and critical answer-point misses (4). A2-A5 were not reached, novel_validation remains pristine, and F6-B stays locked. Report: `evaluation/F6_A5_PRERELEASE_VALIDATION_RESULT.md`. Next recommendation is a separately authorized post-Attempt-5 exposed failure review; execution authorization is false.

## Phase overview

- **Phase A — Evaluation infrastructure and versioned baseline:** `COMPLETE`
  Evaluation boundaries (`retrieval`, `qa`, `full`), structured trace persistence, and reproducible bootstrap baseline established.

- **Phase B — Indexing and embedding correctness:** `COMPLETE`
  Sparse BM25 IDF contract, explicit 3072-dimensional dense contract, unified sparse encoder factory, precise chunk locators, and structure-aware chunking established. Residual downstream ranking/coverage mechanisms explicitly deferred.

- **Phase C — Retrieval generalization:** `COMPLETE / WITH_DEFERRED_COMPONENTS`
  Query-understanding decomposition and multi-channel retrieval mechanisms evaluated. RawDense remains production-authoritative; experimental semantic, lexical, and entity-first candidates remain shadow, deferred, or rejected. Production selector remains authoritative. Targeted retrieval candidate unification (C8) deferred.

- **Phase D — Concept and entity knowledge abstraction:** `PAUSED / ROADMAP_RECONCILIATION`
  Structured domain concept/entity representation, bounded resolver authority, and generic evidence-link bridging established. Bounded query-expansion migrations are active in production, while broader residual scope remains unreconciled.

- **Phase E — Answer generalization:** `COMPLETE / CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED / DEFAULT_PROMOTION_DEFERRED`
  Dynamic question decomposition, answer-point coverage, claim-to-evidence mapping, and targeted completeness recovery. E1 validated (shadow scope), E2 core complete, E3 closed as a bounded low-frequency fallback; PE-LR1 closed the phase at the promotion boundary with the normal default remaining `legacy_question_core` and promotion reconsideration gated on a material candidate change or an explicitly authorized release-boundary decision.

- **Phase F — Benchmark dependency cleanup and final answering:** `IN_PROGRESS / ATTEMPT_3_INFRASTRUCTURE_RECONCILED_READY_FOR_NEW_PREFLIGHT`
  F1 established the bounded non-D4 residual inventory without production cleanup. PF-LR1 reconciled the Phase-F scope into a bounded F2/F3 execution map. F2-A1 removed the benchmark-shaped verifier-support dependencies (R13), F2-A1-R1 removed the remaining whole-claim lexical semantic bypass (the initial F2-A1 closeout was corrected by R1), F2-A2 established question-derived pointer-normalization completeness (R10), and F2-A3 reconciled E1/E2 compatibility authority (R08/R09/R11: coverage modes own completeness, the named-requirement contract remains a legacy bridge); F2-A4 established generic question-grounded premise refusals through the locked-corpus catalog (R04), and F2-A5 established raw-question-grounded paper/code source obligations for the R01 intents (fixed config mappings retired; R02/HOLD mappings and all source budgets unchanged), with the matching boundary completed by F2-A5-R1 (bounded whole-token/phrase matching); with all five PF-LR1 F2 groups complete, F2 is closed. F3 retired the three PF-LR1 code-origin fixed locators (R03 feedback page override, R05 fixed-header unsupported-API fallback, R06 fixed-macro/event_poca deleted-runtime presentation) behind reviewed-expansion and question-grounded generic mechanisms with the D4 YAML untouched. F4 separated the answer/revision generation role from the product semantic-verification role at the settings, client-path, invocation, and usage-accounting levels (distinct production client paths, optional `QA_VERIFICATION_MODEL_ID` defaulting to the generation model, evaluation judge still offline-only, role-specific usage counters and internal role diagnostics) without changing any QA graph semantics or the public default.

## Phase A — Evaluation infrastructure and versioned baseline

### A1 — Explicit evaluation modes

- **Status:** COMPLETE / PASS
- **Goal:** Provide auditable `retrieval`, `qa`, and `full` boundaries without duplicating or changing production QA logic.
- **Outcome:** Decoupled retrieval evidence selection, answer generation with runtime verification, and external rubric evaluation. Run metadata explicitly records permitted execution stages, preventing boundary leaks.
- **Residual / deferred implication:** Established execution boundaries for all subsequent pipeline tests.
- **Evidence reference:** Evaluation runner and manifest schema.

### A2 — Structured retrieval traces and reusable intermediates

- **Status:** COMPLETE / PASS
- **Goal:** Persist deterministic, reloadable retrieval traces faithfully capturing query analysis, channel candidates, fusion, reranking, and evidence selection.
- **Outcome:** Structured trace format implemented in atomic JSON and JSONL, preserving query representations, channel candidates with scores, exclusions, and final selected evidence.
- **Residual / deferred implication:** Enables layer-isolated replay and before/after comparisons without recurring model costs.
- **Evidence reference:** Retrieval trace contract and serialization tests.

### A3 — Low-cost stratified bootstrap baseline

- **Status:** COMPLETE / PASS
- **Goal:** Create a reproducible reference baseline verifying evaluation infrastructure and providing a stable comparison point for early generalization stages.
- **Outcome:** Established the English Gold Stratified Bootstrap Baseline from reviewed benchmark Gold across representative question intents, persisting manifests, traces, and metrics.
- **Residual / deferred implication:** Serves as an initial directional baseline; full benchmark and novel evaluation remained deferred.
- **Evidence reference:** `evaluation/baselines/manifests/english_gold_stratified_bootstrap_v1.json`.

## Phase B — Indexing and embedding correctness

### B1 — Correct sparse BM25 / Qdrant IDF contract

- **Status:** COMPLETE / PASS
- **Goal:** Confirm installed sparse library contracts and ensure Qdrant collection indexing and querying use the correct BM25 IDF modifier.
- **Outcome:** Aligned FastEmbed `0.7.4` and Qdrant `1.15.5` with an explicit server-side `idf` modifier. In-place index migration updated collection identity to schema 3 without collection recreation, vector regeneration, or Vertex calls.
- **Residual / deferred implication:** Rare-identifier discrimination verified; sparse scoring stabilized prior to query tuning.
- **Evidence reference:** Schema 3 index identity.

### B2 — Explicit dense embedding dimensionality contract

- **Status:** COMPLETE / PASS
- **Goal:** Make embedding dimensionality explicit from API request through validation and storage, failing closed on mismatch.
- **Outcome:** Explicit 3072-dimension contract enforced across single, batch, and indexing requests with fail-closed vector validation. Live Qdrant collection verified at 3072 dimensions.
- **Residual / deferred implication:** Eliminated silent dimension drift without requiring re-embedding.
- **Evidence reference:** Ingestion and embedding configuration.

### B3 — Unified sparse encoder identity/factory

- **Status:** COMPLETE / PASS
- **Goal:** Establish a single authoritative factory and identity contract for sparse encoders across indexing and retrieval.
- **Outcome:** Consolidated sparse encoder construction in `create_sparse_encoder` (`src/panda_agent/sparse.py`), binding model, language, scoring modifier, stemmer, and stopword assets into schema-4 index identity (`8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`). Persisted receipts fail closed on mismatch.
- **Residual / deferred implication:** Guaranteed identical tokenization and scoring parameters between indexing and retrieval pipelines.
- **Evidence reference:** `SparseEncoderReceipt` and schema-4 index identity.

### B4 — Precise derived-chunk locators

- **Status:** COMPLETE / PASS
- **Goal:** Record the narrowest available path, line range, page, or section locators for derived code and document chunks to ensure citation precision.
- **Outcome:** Ingestion pipeline updated to track deterministic source offsets, eliminating overbroad parent ranges for functions, classes, scripts, and Sphinx sections. Metadata-only sync updated PostgreSQL and Qdrant payloads with zero vector mutations.
- **Residual / deferred implication:** Downstream evidence selection and citation generation carry precise line- and section-level provenance.
- **Evidence reference:** Ingestion locator audit and metadata sync receipts.

### B5 — Structure-aware, token-aware chunking and source-file coverage

- **Status:** COMPLETE / PASS
- **Goal:** Implement structure-aware, token-bounded chunking that covers non-function code context, configuration, and documentation sections without arbitrary splitting.
- **Outcome:** Deployed `ChunkingPolicy` with structural container rules and preamble gap regions. Selective index migration updated affected objects in place without collection recreation. The formal English retrieval gate remained FAIL due to critical evidence gaps; later deterministic replay remained INCONCLUSIVE and did not establish formal acceptance.
- **Residual / deferred implication:** Two-pass backfill closed as INCONCLUSIVE/partial. Generic coverage-aware evidence selection and optional ranking debt remain deferred; heuristic iteration stopped without case-specific repair.
- **Evidence reference:** `evaluation/baselines/manifests/phase_b_t3_retrieval_v1.json`, `phase_b_t3_product_language_scope_v2.json`.

## Phase C — Retrieval generalization

Phase C evaluated query-understanding decomposition, specialized channel query representations, multi-channel fusion policies, selection constraints, and targeted retrieval candidate unification.

Accepted phase-level outcomes:

* General retrieval infrastructure work planned for Phase C is complete, with unvalidated candidates deferred, rejected, or closed inconclusive.
* `RawDense` remains production-authoritative; `SemanticDense` remains auxiliary/experimental and disabled for production (`KEEP_DISABLED`).
* Production sparse retrieval remains the exact raw user question; `LexicalQuery` remains an experimental/shadow abstraction.
* Production exact retrieval remains `LEGACY_EXACT`; `EntityResolver` remains an experimental/shadow capability.
* Production fusion remains `CURRENT` (P0); P3 sparse-heavy and intent-aware routing are retained as development-supported candidates pending novel corroboration.
* Production evidence selection remains authoritative `CURRENT_SELECTOR`; `c7.explicit_selection.v1` was rejected as a global production replacement.
* C8 global targeted candidate unification was closed as deferred due to insufficient natural dev targeted applicability.
* Downstream coverage-aware evidence selection is deferred to Phase E rather than addressed through ad-hoc retrieval ranking rules.

### C1 — Deterministic parsing before expensive LLM analysis

- **Status:** COMPLETE / PASS
- **Goal:** Extract unambiguous identifiers, paths, repositories, versions, and high-confidence intents deterministically before invoking LLM query analysis.
- **Outcome:** `DeterministicQueryParse` extracts explicit symbols, repositories, and versions, providing structured deterministic context to the analyzer. High-confidence deterministic intents are authoritative; unresolved semantic fields remain LLM-owned.
- **Residual / deferred implication:** Provenance is tracked in `RetrievalPlan.analysis_diagnostics`; analyzer skipping occurs only when no required semantic field remains unresolved.
- **Evidence reference:** `evaluation/baselines/manifests/phase_c_c1_r1_fixed_fallback_ownership_closeout_v1.json`.

### C2 — Narrow and auditable query-analyzer contract

- **Status:** COMPLETE / PASS
- **Goal:** Restrict LLM query analysis to an additive semantic delta grounded in the question, preventing speculative drift and answer-location leakage.
- **Outcome:** Analyzer returns `AnalyzerSemanticDelta` for unresolved intent, concepts, and symbols with query support spans. Unsupported items are rejected; fixed deterministic fields take precedence.
- **Residual / deferred implication:** Query-understanding diagnostics distinguish deterministic, LLM, and fallback provenance; answer-location shortcuts are excluded from the analyzer contract.
- **Evidence reference:** `evaluation/baselines/manifests/phase_c_c2_narrow_auditable_analyzer_v1.json`.

### C3 — Dense query architecture (RawDense + SemanticDense)

- **Status:** COMPLETE / PASS
- **Goal:** Separate raw-question dense retrieval from concept-expanded semantic retrieval, maintaining raw-query authority while enabling auditable semantic evaluation.
- **Outcome:** RawDense preserves the exact raw question with `user_raw` provenance and is production-authoritative. SemanticDense encapsulates query-grounded concepts in an auxiliary, explicit shadow representation with zero default production cost.
- **Residual / deferred implication:** Production dense retrieval uses RawDense only. SemanticDense production efficacy was unvalidated in C3 and deferred to C6.
- **Evidence reference:** `evaluation/baselines/manifests/phase_c_c3a_raw_preserving_auxiliary_semantic_dense_v1.json`.

### C4 — LexicalQueryBuilder for sparse retrieval

- **Status:** CLOSED_INCONCLUSIVE
- **Goal:** Construct bounded lexical queries from grounded symbols, canonical entities, and technical terminology for BM25 retrieval.
- **Outcome:** Architecture contract passed (C4-A1 PASS), but screening did not establish the required treatment-qualified cohort. Sparse ranking was not observed.
- **Residual / deferred implication:** Production sparse retrieval remains the exact raw question. `LexicalQuery` is retained as an experimental/shadow abstraction. Further C4 sampling under the current contract is closed.
- **Evidence reference:** `evaluation/baselines/manifests/phase_c_c4_a3_architectural_closeout_v1.json`.

### C5 — Entity-first exact retrieval

- **Status:** CLOSED_INCONCLUSIVE
- **Goal:** Resolve exact symbols and accepted aliases to canonical entities before falling back to lexical search.
- **Outcome:** Resolver architecture verified in shadow mode (C5-A1 PASS), but diagnostic evaluation showed no recall improvement, MRR regression, and absence of descriptive alias cases.
- **Residual / deferred implication:** Architectural finding established: unique exact retrieval match does not equal canonical entity identity. Production exact remains `LEGACY_EXACT`; `EntityResolver` remains experimental/shadow; systematic entity modeling deferred to Phase D.
- **Evidence reference:** `evaluation/baselines/manifests/phase_c_c5_a3_architectural_closeout_identity_strength_v1.json`.

### C6 — Multi-channel fusion evaluation

- **Status:** COMPLETE / PASS
- **Goal:** Evaluate multi-channel fusion policies across valid production channels using aggregate benchmark evidence rather than single-case adjustments.
- **Outcome:** Frozen policy comparison across formal-English scope confirmed P0 CURRENT remains production-authoritative. P3 sparse-heavy and intent-aware routing validated as development-supported candidates, blocked from production activation by absent novel corroboration. SemanticDense candidate contribution proved insufficient (`KEEP_DISABLED`).
- **Residual / deferred implication:** Production fusion unchanged; development-supported candidates require independent novel evaluation prior to activation.
- **Evidence reference:** `evaluation/baselines/manifests/phase_c_c6_a3_frozen_production_role_decision_v1.json`.

### C7 — Clear source constraints and evidence diversity

- **Status:** COMPLETE / PASS
- **Goal:** Formalize evidence-selection constraints (`PROTECTED`, `REQUIRED`, `PREFERRED`, `MAXIMUM`) to ensure evidence diversity without enforcing artificial quotas.
- **Outcome:** Explicit selection contract evaluated against frozen post-reranker capture. Candidate policy `c7.explicit_selection.v1` failed hard gates, lost critical evidence, and was rejected as a global replacement. `CURRENT_SELECTOR` (`select_final_evidence`) remains production-authoritative.
- **Residual / deferred implication:** Constraint taxonomy and diagnostic trace mechanisms retained for architectural reference; production selector unchanged.
- **Evidence reference:** `evaluation/baselines/manifests/phase_c_c7_a4_production_role_closeout_v1.json`.

### C8 — Global rerank after targeted retrieval

- **Status:** DEFERRED / INSUFFICIENT_NATURAL_TARGETED_APPLICABILITY
- **Goal:** Unify initial and targeted retrieval candidates into a single deduplicated global reranking and selection pass.
- **Outcome:** Global candidate pool contract and data structures established (`c8.global_candidate_pool.v1`). Dev screening found insufficient natural targeted applicability for the preregistered treatment cohort.
- **Residual / deferred implication:** Targeted retrieval candidate unification deferred without algorithmic rejection. Upstream missing-evidence handling deferred to Phase E.
- **Evidence reference:** `evaluation/baselines/manifests/phase_c_c8_a2_applicability_closeout_v1.json`.

## Phase D — Concept and entity knowledge abstraction

Status:
PAUSED / ROADMAP_RECONCILIATION

Sub-stage summary:

- **D1 — Concept/entity schema:** `COMPLETE / PASS`
  Canonical concept, entity, relation, and workflow representations established in the knowledge graph.

- **D2 — Terminology and paraphrase resolver:** `ROLE_DECISION_COMPLETE`
  Resolver authority is bounded by mechanism; current production role remains `SHADOW`.

- **D3 — Small shortcut-migration experiment:** `COMPLETE / PASS`
  Controlled three-arm experiment established a generic structured replacement foundation.

- **D3.5 — Structured Evidence-Link Reachability & Bridging:** `COMPLETE / PASS`
  Bounded structured rerank admission validated for development.

- **D4 — Incremental migration of appropriate query expansions:** `PAUSED / ROADMAP_RECONCILIATION`
  Bounded query-expansion migrations are active in production, while broader residual scope remains unreconciled.

Phase D is paused for roadmap reconciliation. Overall completion is undecided, and no further Phase-D task is authorized.

### D1 — Concept/entity schema

- **Status:** COMPLETE / PASS
- **Goal:** Introduce structured domain entity, concept, relation, and workflow models extending the existing knowledge graph.
- **Outcome:** Materialized canonical models covering Concepts, DataProducts, SoftwareModules, Relations, and Workflows with versioned identity and real-corpus compatibility.
- **Residual / deferred implication:** D1 established representational foundations only; it did not implement query-time resolution or shortcut migration.
- **Evidence reference:** Phase D1 contracts and materialization receipts.

### D2 — Terminology and paraphrase resolver

- **Status:** COMPLETE / ROLE_DECISION_COMPLETE
- **Goal:** Resolve technical terminology, aliases, and descriptive references to canonical entities with bounded authority.
- **Outcome:** Evaluated shadow resolver across Tier G (governed identity/aliases), Tier S (exact symbols), and Tier D (governed descriptive inference). Identity-strength and abstention findings distinguish governed identity from weak retrieval matches; descriptive competition and unsafe whole-question fallback limit authority.
- **Residual / deferred implication:** Overall resolver role classified as bounded authority by mechanism; current production role remains `SHADOW`. Whole-question fallback prohibited in production.
- **Evidence reference:** `docs/PHASE_D2_A0_RESOLVER_CONTRACT.md`, `evaluation/d2_a3_role_decision.json`.

### D3 — Small shortcut-migration experiment

- **Status:** COMPLETE / PASS
- **Goal:** Experimentally evaluate replacing representative phrase-to-file/page shortcuts with structured concept/relation paths across legacy, ablation, and structured arms.
- **Outcome:** The completed structured replacement experiment established a generic foundation without phrase/rule/case-to-object answer-location mapping, while exposing evidence-link reachability and materialization gaps.
- **Residual / deferred implication:** Established the necessity of generic evidence-link bridging (D3.5) before expanding shortcut migrations.
- **Evidence reference:** `evaluation/d3_a0_shortcut_migration_preregistration.json`, `evaluation/d3_a2_three_arm_results.json`.

### D3.5 — Structured Evidence-Link Reachability & Bridging

- **Status:** COMPLETE / PASS
- **Goal:** Establish a typed, bounded path from valid D2 seeds through governed D1 structure to additive, retrievable source-native evidence.
- **Outcome:** Bounded structured candidate admission and reranking were validated for development, with selected admission budget 3. Detailed mechanism comparisons remain in the evaluation artifacts.
- **Residual / deferred implication:** Bounded rerank admission budget of 3 validated for development; did not constitute production activation.
- **Evidence reference:** `evaluation/d3_5_a6_phase2_result.json`.

### D4 — Incremental migration of appropriate query expansions

Status:
PAUSED / ROADMAP_RECONCILIATION

#### Problem

Some query-expansion rules encode legacy phrase-to-file/page or answer-location shortcuts. Other query-expansion content represents legitimate:

* terminology.
* aliases.
* normalization.
* domain routing.
* domain knowledge.

D4 must not treat all query expansions as removable shortcuts.

#### Goal

Migrate only components for which a generic replacement or safe retirement is sufficiently evidenced.

#### Design principles

* Operate at the smallest causally identifiable component and origin level.
* Preserve legitimate terminology, aliases, and query normalization.
* Preserve independent provenance origins when retiring specific rule contributions.
* Use shared-plan controlled comparisons where scientific before/after treatment is required.
* Require treatment-active coverage for component-level retirement claims.
* Treat `HOLD` as a valid outcome when direct coverage or generic replacement evidence is insufficient.

#### Production achievements

The following component migrations are currently active in production:

* `event_poca_handoff`:
  → fixed locator contribution retired
  → structured replacement active

* `restgas_profile_workflow`:
  → fixed locator contribution retired
  → structured replacement active

* `effective_acceptance_pipeline`:
  → validated locator retirement active

* `root_macro_usage`:
  → validated locator retirement active

* `model_factory_theory` / `model/PndLmdModelFactory.cxx`:
  → validated rule-local locator retirement active

#### Confirmed HOLD

The following components remain on confirmed HOLD:

* `model/PndLmdDPMAngModel1D.cxx`:
  → `HOLD_DIRECT_TREATMENT_COVERAGE_GAP`

* `model/PndLmdDPMAngModel2D.cxx`:
  → `HOLD_DIRECT_TREATMENT_COVERAGE_GAP`

* `pflueger_2017 [51, 57, 65]`:
  → `HOLD_OUTSIDE_TREATMENT_SCOPE`

#### Current ModelFactory production semantics

Current production semantics for `model_factory_theory` remain:

```yaml
symbols:
  - model/PndLmdDPMAngModel1D.cxx
  - model/PndLmdDPMAngModel2D.cxx
paper_page_hints:
  pflueger_2017: [51, 57, 65]
# structured_replacement is absent (default false)
```

Production activation removed only `model/PndLmdModelFactory.cxx` from `model_factory_theory.symbols`. Independent ModelFactory references remain elsewhere. `FULL_BATCH2_PRODUCTION_ACTIVATION = false`. The entire rule is not retired.

#### General mechanisms established

* Shared-plan controlled comparison across treatment and control arms.
* Component-level applicability and origin accounting.
* Provenance-aware contribution tracking distinguishing rule-specific from independent origins.
* Selected-origin subtraction with independent-origin preservation.
* Direct treatment-coverage requirement for retirement claims.

#### Current limitation

The broader original D4 inventory has not yet been reconciled against the current production state. The confirmed ModelFactory residual HOLDs are NOT assumed to represent the complete remaining D4 scope.

#### Planning boundary

It is currently undecided whether:

* another bounded D4 migration batch is worthwhile.
* remaining D4 candidates should stay on HOLD.
* or residual dependency work belongs in a redesigned Phase F.

No D4-A11 is authorized. Detailed scientific and repair provenance remains in `evaluation/D4_*`, machine-readable results, and Git history.

## Phase E — Answer generalization

Status:
COMPLETE / CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED / DEFAULT_PROMOTION_DEFERRED

Phase E addressed answer synthesis, facet coverage, claim-to-evidence grounding, and targeted recovery of missing answer
points. E2 core mechanism is complete; default promotion remains deferred. E3-A0 established the
missing-point targeted retrieval architecture and dependency contract. E3-A1 implemented the
experimental path through explicit runtime_e1_v2 execution without default promotion. E3-A2 completed
INCONCLUSIVE (insufficient natural applicability); E3-LR1 closed E3 as a bounded low-frequency fallback with
standalone recovery benefit unresolved. PE-LR1 closed the phase at the promotion boundary: architecture complete,
normal default remains `legacy_question_core`, promotion reconsideration is gated on
DEFAULT_PROMOTION_RECONSIDERATION_TRIGGER (a materially behavior-changing post-Phase-E candidate — normally from
Phase-F compatibility/benchmark-dependency cleanup — or an explicitly authorized release/acceptance candidate
evaluation requiring the normal-default decision). Normal legacy QA must
retain existing retrieval behavior; missing-point retrieval belongs only to the explicitly authorized
experimental path. No future cohort, judge
structure, schema or threshold is active or frozen by E2-LR1, E3-LR1, or PE-LR1; the E2 gate-redesign deferral is
closed.

### Architecture-level downstream requirements

* **Source and version constraints:** Grounded claims must respect locked repository and document version boundaries.
* **Stable evidence and locators:** Claims must map to stable object IDs and precise line/page/section locators.
* **Relational provenance:** Generated statements reflecting workflows or relations must reflect verified graph structure.
* **Analyzer boundary:** Deterministic vs LLM-derived question semantics must maintain clear provenance boundaries.
* **Query observability:** Distinguish lexical from semantic retrieval contributions during answer verification.
* **Independent answer requirements:** Answer requirements must be derived strictly from question understanding, never inferred post-hoc from retrieved evidence.

### E1 — Dynamic question decomposition

- **Status:** COMPLETE / PASS / QUESTION_ONLY_SEMANTIC_ANSWER_POINT_DECOMPOSITION_VALIDATED
- **E1-A1 outcome:** COMPLETE / PASS / QUESTION_ONLY_DIAGNOSTIC_DECOMPOSITION_IMPLEMENTED. Question-only 1–5 facet contract and explicit shadow diagnostic seam implemented; normal QA does not invoke it. Existing `question_core` remains authoritative and compatibility requirements remain active. Focused fake-based T0 checks passed. E1-A1 PASS is not E1 PASS.
- **E1-A2 outcome:** COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED. Frozen 24-case T2 cohort fully scored: valid 24/24, question-only reference recall 40/44, precision 40/40, under 4/24, over 0/24, exact count 20/24, hidden prerequisites 0. G7 type accuracy 28/40 (70%) and G8 strict reference-conformant pairs 7/12 failed; all other gates passed. Production and preregistration contracts remained unchanged. Small exposed-development results are not release generalization estimates; source and language are confounded.
- **E1-A2 evidence:** `evaluation/e1_a2_dynamic_question_decomposition_validation_result.json`, `evaluation/E1_A2_DYNAMIC_QUESTION_DECOMPOSITION_VALIDATION.md`; preregistration commit `77ea6bc27beb1657673e57be763b05419c98bc05`.
- **E1-AR outcome:** COMPLETE / PASS / REVISED_SEMANTIC_ANSWER_POINT_CONTRACT_ESTABLISHED. Static architectural diagnostics ignoring type: semantic-complete 20/24, semantic-slot stable pairs 10/12; taxonomy disagreements 12/40 matched points; granularity merges in 4 cases. E1-A2 remains FAIL under its original G7/G8; these are not new acceptance results. No implementation or scientific rerun occurred.
- **E1-AR evidence:** `evaluation/e1_architecture_review.json`, `evaluation/E1_ARCHITECTURE_REVIEW.md`.
- **E1-R1 outcome:** COMPLETE / PASS / SHADOW_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIRED. Prompt 2.0.0 / schema e1.question_decomposition.v2 implements obligation atomicity guidance, optional diagnostic taxonomy, and type-independent question-order IDs. Focused v2 T0: 32 passed; real-model repair quality remains unmeasured. Normal QA and compatibility requirements remain unchanged. Historical v1 test fixtures require their original implementation, as documented in the repair report.
- **E1-R1 evidence:** `evaluation/E1_R1_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIR.md`.
- **Evidence:** `evaluation/e1_a1_dynamic_question_decomposition_contract.json`, `evaluation/E1_A1_DYNAMIC_QUESTION_DECOMPOSITION_CONTRACT.md`.
- **E1-R2 outcome:** COMPLETE / PASS / TARGETED_PROSPECTIVE_SEMANTIC_ANSWER_POINT_REVALIDATION_PASSED. Human-approved fresh synthetic exploratory English cohort: 24/24 valid, semantic recall 54/54, precision 54/54, under/over 0, exact count 24/24, semantic-complete pairs 12/12, hidden prerequisites 0; all eight gates passed. Raw records were committed before judging. Preregistration `3d0d8ca650d159681fecec324a081d28e8e945eb`; raw freeze `a5275dfee6c4134f3ad790a5598ca0c0a51f1a58`. Report: `evaluation/E1_R2_SEMANTIC_ANSWER_POINT_REVALIDATION.md`; result: `evaluation/e1_r2_semantic_answer_point_revalidation_result.json`.
- **Next task recommendation (current):** Phase-F scope reconciliation and bounded benchmark-dependency cleanup planning; NOT AUTHORIZED. E1 is complete at bounded shadow decomposition scope; production compatibility requirements remain unchanged. (Historical chain: E3-A1 → E3-A2 → E3-LR1; Phase E closed by PE-LR1; see the Phase E and E3 sections.)
- **Problem:** A single `question_core` plus domain-specific requirements can be complete on known questions but miss unseen multi-part structure.
- **Goal:** Derive 1–5 evidence-independent, independently satisfiable explicit response obligations from the question itself, each independently checkable for omission.
- **Why this stage:** Retrieval generalization and structured knowledge must be established before asking decomposition to drive completeness.
- **Intended design:** Question-only semantic obligations with exact support spans and deterministic, type-independent question-order IDs; optional facet taxonomy and ambiguity are diagnostic metadata, not semantic correctness authority. Split independently satisfiable explicit obligations, not merely multiple entities or clauses; preserve a requested comparison or end-to-end flow as one unit absent separate asks. Remain shadow-only alongside existing compatibility requirements.
- **Functional requirements:** Question-only input, 1–5 points, unique code-assigned IDs independent of taxonomy in both sorting and identity, exact question support spans, semantic-slot paraphrase stability, over/under-decomposition checks, and trace/audit output. Literal ID equality across paraphrases is not required.
- **Explicit out of scope:** Deriving points from retrieved evidence, removing existing requirements, targeted retrieval, or benchmark templates.
- **Dependencies:** Phases C/D and curated answer-point annotations.
- **E1-C1 outcome:** COMPLETE / PASS / REAL_PANDA_STYLE_EXPOSED_DEVELOPMENT_CONFIRMATION_PASSED. Exact historical English novel_dev pairs07-12:12/12 valid,28/28 recall and precision,0 under/over,12/12 exact count,6/6 complete pairs,0 hidden prerequisites; pair09 both variants3/3 matched with3 predictions and no extras. Scientific calls24, returned tokens30099. Report: `evaluation/E1_C1_REAL_STYLE_CONFIRMATION.md`. Together with R2 this meets the accepted E1 closure condition; historical A2 FAIL remains. No representative generalization or production integration claim.
- **Future primary metrics:** Structural validity, question-only semantic reference-point recall, semantic prediction precision, under/over-decomposition, exact point count, semantic-slot paraphrase stability, and hidden-prerequisite inference. Legacy answer facts are not E1 ground truth.
- **Secondary diagnostics:** Exact facet-type agreement, taxonomy distribution and facet-label paraphrase stability; source-group gaps remain diagnostic. Historical E1-A2's strict reference-conformant pair gate remains unchanged and must not be presented as pure semantic paraphrase stability.
- **Acceptance criteria:** Decomposition captures required question facets generically without mirroring whatever evidence was found.
- **Failure handling:** Repair generic explicit-obligation granularity without benchmark or lexical triggers; keep taxonomy and ambiguity diagnostic and retain old requirements. Freeze any future repair before separately authorized prospective validation. Stop after the current authorized E1 task.

### E2 — Answer-point coverage and claim mapping

- **Status:** COMPLETE / CORE_MECHANISM_VALIDATED / DEFAULT_PROMOTION_DEFERRED
- **E2-A1 outcome:** COMPLETE / PASS / SHADOW_ANSWER_POINT_COVERAGE_CONTRACT_IMPLEMENTED. Explicit diagnostic entrypoint projects E1 IDs/text into the existing QA graph. The existing evidence review independently checks claim mapping and collective completeness; missing points reuse one revision with existing evidence. Normal QA, public DTOs, retrieval, and legacy requirements remain unchanged. Focused fake-based checks passed: 42 E2-A1 and 38 QA tests; 32 E1 decomposition tests also passed. No live scientific calls. Report: `evaluation/E2_A1_SHADOW_ANSWER_POINT_COVERAGE_CONTRACT.md`.
- **E2-A2 outcome:** COMPLETE / PASS / TARGETED_CLAIM_MAPPING_AND_MISSING_POINT_VALIDATION_PASSED. Twelve exposed English questions in two fresh repetitions: applicable 12/12 each; mapping precision 74/79, recall 74/75, exact claim mapping 68/74; coverage precision/recall 56/56. Controlled rep1 variants: 11 eligible, target detection/missing precision/exact missing set 11/11 each; one non-isolatable baseline. Zero structural or infrastructure failures. Five extra mapping edges and one missed edge remain. Scientific usage: 217 logical operations, 193 returned responses (169 generation and 24 embedding), 2,090,933 returned token-counter total; embedding token usage unavailable. Same-model-family blinded judge; targeted exposed evidence only. Report: `evaluation/E2_A2_TARGETED_CLAIM_MAPPING_VALIDATION.md`.
- **E2-A3 outcome:** COMPLETE / FAIL / Q7. Retrieval 24/24; paired QA 56/56; scoreable judgments 28/28. Gold status 14/16 in both arms; runtime better/equivalent/worse 6/21/1. Novel decomposition/evaluable/complete 12/12; pair09 three points. One new unsupported-identifier verifier category on g112 fails the all-reviews integrity gate despite final recovery. No default activation; normal QA remains legacy_question_core. Report: `evaluation/E2_A3_RUNTIME_ACTIVATION_REGRESSION.md`.
- **E2-A3-FR1 outcome:** COMPLETE / PASS / REPAIR_JUSTIFIED. V1 false rejection confirmed from frozen cited source and exact rejecting-loop counterfactual. One affected scoped/path token in 157 distinct claim snapshots; prior unsupported-token controls remain rejected. Recommend deterministic normalization only, then T0 plus five fresh paired cases under a new candidate. Historical A3 remains FAIL; no repair or activation performed. Report: `evaluation/E2_A3_Q7_FAILURE_REVIEW.md`.
- **E2-A3-R1 outcome:** COMPLETE / FAIL / P2_P6. Rejection-only normalization implemented; S1-S12 passed with one frozen rejection delta. Five fresh pairs and judgments completed: g112 sentinel passed, status 5/5 each, quality 2 better / 2 equivalent / 1 worse. g027 new incomplete citation fails P2; g002 worse judgment fails P6. No activation; default legacy_question_core. Report: `evaluation/E2_A3_R1_IDENTIFIER_NORMALIZATION_REPAIR.md`.
- **E2-A3-R1-FR1 outcome:** COMPLETE / PASS / P2_REPAIR_REQUIRED_P6_NO_PRODUCT_REPAIR. P2 is R3 citation-incomplete page admission, not lost page metadata or verifier false rejection. Frozen citation scan: 27 candidate edges, 3 incomplete, 18 final edges all complete. P6 optional-detail difference does not justify generic product repair. Historical A3/R1 FAIL and colon-repair success preserved; zero scientific calls; no waiver or activation. Report: `evaluation/E2_A3_R1_P2_P6_FAILURE_REVIEW.md`.
- **E2-A3-R2 outcome:** COMPLETE / PASS / CITATION_ELIGIBLE_EVIDENCE_SELECTION_REPAIR_VALIDATED. Admission-only Sphinx projection in answer/revision and revision requirement map; verifier, retrieval, E1/E2, compatibility and default preserved. Historical scan 144 = 106 retained + 38 excluded; three invalid historical candidate edges barred from admission. T0 126 passed. Six fresh pairs/judgments: status and support 6/6 each, incomplete-web errors 0, new runtime categories 0, quality 1 better / 5 equivalent / 0 worse, critical regressions 0, overhead 1.333333. Historical A3/R1 FAIL and P6 no-repair/no-waiver preserved. No activation; E2 remains in progress. Report: `evaluation/E2_A3_R2_CITATION_ELIGIBLE_EVIDENCE_REPAIR.md`.
- **E2-A3-R3 outcome:** INCONCLUSIVE / CONNECTION_TIMEOUT_AND_PROVIDER_429_INCOMPLETE_PAIRS. Product unchanged from R2. Fixed 14 English Gold/dev questions (10 answered/4 controls), excluding R2 six; F1-F10 and 30 focused tests passed. All 28 attempt records terminal; 12 successful QA outputs per arm and 11 authoritative paired judgments due to three connection timeouts plus one 429. Scoreable quality 1/9/1, support 11/11 each, no critical regression or observed new verifier category. G1/G7/G9/G11 lack complete authority; no activation or rerun. Full fourteen-pair overhead unavailable; 15/11=1.363636 is diagnostic only. Report: `evaluation/E2_A3_R3_RUNTIME_ACTIVATION_REASSESSMENT.md`.
- **E2-A3-R3-R1 outcome:** COMPLETE / FAIL / G11. Six fresh QA arms and three blinded judgments completed the original 11 plus recovery 3 authority. Status/support 14/14 each; quality 1/11/2 (new g001 plus historical g029 worse); critical regressions 0. G11 fails, all other gates PASS with complete authority. G12 (75-61)/14=1.0. Focused evaluator tests 32 passed; product/default unchanged, no activation or further recovery. Report: `evaluation/E2_A3_R3_R1_INFRASTRUCTURE_RECOVERY.md`.
- **E2-A3-R3-R1-FR1 outcome:** COMPLETE / PASS / PRODUCT_REPAIR_AND_GATE_REDESIGN_RECOMMENDED. Static review identifies shared deterministic partial-template sanitization in g029/g059 (A1); g001 separately omits explicit version scope, not just a SHA. No shared g001/g029/g002 cause established. Recommend narrow generic sanitization repair and prospective obligation/materiality gate design; historical G11 FAIL 1/11/2 preserved. Zero scientific calls, no repair, gate change or activation. Report: `evaluation/E2_A3_R3_R1_G11_FAILURE_REVIEW.md`.
- **E2-LR1 interpretation:** Core mechanism implemented and sufficiently targeted-validated for architecture continuation; default acceptance not met. This is not E2 scientific PASS. Historical outcomes above remain immutable, including G11 quality 1/11/2.
- **E2-A3-R4:** NOT_STARTED / SUPERSEDED_BY_LIFECYCLE_SIMPLIFICATION. The historical G11 review recommendation remains recorded; E2-LR1 supersedes its immediate combined activation loop.
- **QA-M1 outcome:** COMPLETE / PASS / GENERIC_CLAIM_SANITIZATION_REPAIR_VALIDATED. Balanced external-wrapper abstraction preserves domain payload and requested names. Focused T0 14 tests/2 subtests passed; frozen scan 290 claim snapshots, 2 intended changes, 0 collateral changes. Shared maintenance only; zero scientific calls and no activation decision. Report: `evaluation/QA_M1_GENERIC_CLAIM_SANITIZATION_REPAIR.md`.
- **Next task (current):** Phase-F scope reconciliation and bounded benchmark-dependency cleanup planning; NOT AUTHORIZED. Default promotion is deferred under the PE-LR1 recorded trigger; the gate-redesign deferral is closed. (Historical chain: E3-A1 → E3-A2 → E3-LR1; Phase E closed by PE-LR1.)
- **Problem:** Atomic claims are not generically accountable to the facets the user asked to have answered.
- **Goal:** Map every generated claim to one or more answer-point IDs and evidence IDs, then measure completeness and support.
- **Why this stage:** E1 quality must be proven before its points become a runtime completeness contract.
- **Intended design:** Maintain explicit `claim -> answer_points -> evidence` mapping; consume semantic point IDs/text without requiring exact facet labels. Run old answer requirements in parallel for regression comparison.
- **Functional requirements:** Validate IDs, point coverage, unsupported/missing-point detection, audit-only versus user-visible claims, and refusal semantics.
- **Explicit out of scope:** Immediate deletion of existing requirements, targeted retrieval, composer, or benchmark-specific mappings.
- **Dependencies:** E1 and current evidence-bound claim/verifier architecture.
- **Planned evaluation scope (not authorized):** T0 plus targeted T2 benchmark/novel QA cases.
- **Primary metrics:** Point coverage, unsupported claims, missing-point detection precision/recall, and benchmark/novel difference.
- **Acceptance criteria:** Visible claims map validly to requested points and evidence; missing facets are detected without adding facts.
- **Continuing boundary:** Preserve legacy compatibility checks and accepted identifier normalization/citation admission repairs. Semantic coverage remains available through explicit experimental selection; core completion does not authorize default promotion or subsequent work.

### E3 — Missing-point targeted retrieval

- **Status:** COMPLETE / BOUNDED_LOW_FREQUENCY_FALLBACK_IMPLEMENTED / SCIENTIFIC_RECOVERY_BENEFIT_UNRESOLVED
- **Execution boundary:** Separate authorization required. Use explicit runtime_e1_v2 experimental path; normal legacy runs retain existing retrieval behavior. No default promotion or scientific evaluation occurs in E3-A1.
- **E3-A0 outcome:** COMPLETE / PASS / MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT_ESTABLISHED. Reconstructed current QA graph from source (`src/panda_agent/qa.py`); distinguished pre-answer sufficiency-based targeted retrieval from post-verify semantic missing-point targeted retrieval; reconciled historical C8 dependency (design reuse without validation claims); established question-derived trigger/objective contract; specified bounded one-attempt recovery; proposed resolution for citation displacement via retained-support evidence ledger and immutable retained-supported-claims snapshot without selection pinning or limit expansion; established minimal A1 seam and T1-T20 test contract (local test IDs, none executed in A0). Zero product edits, zero scientific calls. Report: `evaluation/E3_A0_MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT.md`.
- **E3-A1 outcome:** COMPLETE / PASS / EXPERIMENTAL_MISSING_POINT_TARGETED_RETRIEVAL_IMPLEMENTED. Implemented runtime-only post-verify targeted retrieval seam in `qa.py` and `retrieval.py` under `runtime_e1_v2`. Enforced strict A0 trigger, question-derived collection objective, original plan snapshot preservation, dedicated `missing_point_retrieval_count <= 1`, candidate capture without duplicate calls, cross-pass best-channel-rank RRF (`RRF_K=60`, experimental candidate, not validated optimal), single global rerank on original question only, authoritative final evidence selection, atomic bundle update with single try/except exception boundary, narrow retained-support claims ledger protecting unchanged supported claims, and public schema invariance. Initial baseline `2af8ac95` verified 42 E3 tests and 147 neighboring tests (189 passed, 9 subtests passed). Independent post-implementation review corrections incorporated cross-pass bounded eligible union candidate reservation and deterministic valid retained claim/evidence view in second verify, bringing focused verification to 49 E3 tests and 147 neighboring tests (196 passed, 9 subtests passed). Separate final AGY review PASS; Codex accepted the bounded corrections after inspecting the source/test diffs. Zero scientific/evaluation calls or tokens. Report: `evaluation/E3_A1_EXPERIMENTAL_MISSING_POINT_RETRIEVAL_IMPLEMENTATION.md`.
- **E3-A2 outcome:** COMPLETE / INCONCLUSIVE / INSUFFICIENT_NATURAL_MISSING_POINT_APPLICABILITY. Prospective T2 validation under preregistration `50eada9e4c62980f4437d7b2ce0850667109305c` on a mechanically enriched 11-case novel_dev cohort (n003, n005, n006, n009, n010, n014, n019, n020, n021, n022, n024). An evaluation-only harness forked the identical first-verify checkpoint into a pre-E3 existing-evidence-only revision control and the current E3 treatment; product frozen; default mode unchanged. Only n006 was naturally E3-applicable (2 first-missing points) — below the frozen G2 authority threshold (>=4 cases, >=4 points) — so the recovery hypothesis was never tested with authority. The single blinded pair is descriptive only: no `satisfied_supported` point on either arm (control absent/absent, insufficient_evidence; treatment partial/absent, answered; judge preferred treatment); zero treatment-only preservation/safety regressions; E3 within all bounds (1 targeted retrieval, 1 global rerank, 1 revision, atomic success, 1 newly admitted object, plan preserved). G1/G4/G5/G6/G7 PASS; G3 FAIL; G2 FAIL → overall INCONCLUSIVE. Observed usage 78 model calls / 746,593 returned tokens. Report: `evaluation/E3_A2_TARGETED_MISSING_POINT_RECOVERY_VALIDATION.md`.
- **E3-LR1 outcome:** COMPLETE / PASS / POST_A2_LIFECYCLE_RECONCILED. Static lifecycle decision, zero scientific calls. Separated architecture (justified), implementation safety (validated), and efficacy (unresolved). F1-R12 and F1-R14 reconciled as non-blockers owned by Phase F/retrieval cleanup. Maintenance burden MODERATE and default-isolated. Selected OPTION A: E3 closes as a bounded low-frequency fallback; DEDICATED_E3_REVALIDATION = NOT_PLANNED / LOW_NATURAL_APPLICABILITY_AND_LOW_DECISION_VALUE; FUTURE_E3_EVIDENCE = ACCUMULATE_OPPORTUNISTICALLY_IN_BROADER_AUTHORIZED_EVALUATIONS. First-verify-failure-focused cohorts are outcome-conditioned selection and cannot serve as prospective applicability authority. No default promotion. Report: `evaluation/E3_LR1_POST_A2_LIFECYCLE_DECISION.md`.
- **Next task (current):** Phase-F scope reconciliation and bounded benchmark-dependency cleanup planning; NOT AUTHORIZED. (The Phase-E promotion-boundary reconciliation this section previously pointed to is complete: PE-LR1.)
- **Problem:** Once a genuine answer point is missing, the system needs a generic retrieval objective rather than hidden domain requirements.
- **Goal:** Use missing answer points to trigger one bounded targeted retrieval, followed by global candidate reconsideration (best-rank RRF + rerank + selection) and retained-support evidence preservation.
- **Why this stage:** Requires validated E1 decomposition and E2 claim mapping; global candidate reconsideration is an implemented architectural seam verified in A1 (C8 treatment validation is not a prerequisite per D1).
- **Intended design:** `verify` -> `missing-point targeted retrieval` -> `global candidate reconsideration (best-rank RRF + rerank + selection) + retained-support evidence ledger` -> `bounded revision` -> `second verify` -> `finalize`.
- **Functional requirements:** Bounded loops, explicit objectives, trace provenance, version safety, recovery measurement, and no arbitrary hidden requirements.
- **Explicit out of scope:** New benchmark rules, unbounded retries, answer composer, or removing compatibility behavior before Phase F.
- **Dependencies:** Validated E1 and completed E2 core mechanism; C8 global candidate-pool design principles (C8 treatment validation not a prerequisite). E2 default promotion is not a dependency; QA-M1 is maintenance, not an architectural prerequisite.
- **Planned evaluation scope (not authorized):** T0 fake/static unit tests (T1–T20), then targeted T2 multi-hop/cross-repository/workflow/multi-part novel cases, then small Phase-E T4.
- **Primary metrics:** Missing-point recovery, targeted retrieval success, final point coverage, unsupported claims, and cost.
- **Acceptance criteria:** Missing requested facets are recovered more often without displacing strong evidence or increasing unsupported claims.
- **Failure handling:** Stop after the bounded attempt and return an honest incomplete/refusal outcome; never invent a requirement or fact. Stop after E3.

## Phase F — Benchmark dependency cleanup and final answering

Status:
IN_PROGRESS / F1_COMPLETE

Phase F addresses the audit and retirement of remaining benchmark-specific dependencies, generalization of guard logic, role separation between answer generation and semantic verification, bounded answer composition, and release evaluation.

Original Phase-F planning predates the substantial shortcut migrations completed in D4. F1 has now inventoried bounded non-D4 residual dependencies; remaining Phase-F execution still requires separate scope reconciliation and authorization.

### F1 — Residual benchmark-dependency inventory

- **Status:** COMPLETE / PASS
- **Goal:** Audit residual benchmark dependencies outside already-reconciled D4 query-expansion work.
- **Scope:** Inspect code and configuration guards, negative controls, special prompt requirements, and bespoke sufficiency logic across retrieval and QA.
- **Constraint:** Do not repeat the historical D4 inventory or already-reconciled migrations. Broader residual D4 scope remains undecided.
- **Outcome:** Classified 21 candidates: 12 production residuals (4 F2, 3 F3, 3 E1/E2 compatibility, 2 E3 boundary review), 3 provenance HOLDs, 4 generic/domain mechanisms retained, 1 aggregate D4 exclusion and 1 evaluator-only exclusion. No production cleanup or scientific execution occurred.
- **Planning implication:** Zero substantiated E1 blockers. Recommend E1 — Dynamic Question Decomposition, without authorizing execution; preserve compatibility until a generic replacement is established.
- **Evidence:** `evaluation/f1_residual_benchmark_dependency_inventory.json` and `evaluation/F1_RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY.md`.

### PF-LR1 — Phase-F scope reconciliation

- **Status:** COMPLETE / PASS / PHASE_F_SCOPE_RECONCILED_BOUNDED_CLEANUP_PLAN_ESTABLISHED
- **Goal:** Convert the F1 residual inventory (R01–R21) into a bounded lifecycle/execution map so future Phase-F production tasks can be authorized without re-deriving scope.
- **Outcome:** All 21 F1 anchors revalidated at HEAD `a2920d9` with no reclassification. Formal F2 scope = five bounded groups: A R13 verifier-support semantics; B R10 deterministic completeness semantics; C R08/R09/R11 E1/E2 compatibility retirement as one bounded named step inside F2 (coverage-equivalence condition; no new top-level phase); D R04 premise/refusal generalization; E R01 semantic source obligations. R13 and R10 are independently implementable; R13-first is RECOMMENDED_SEMANTIC_SEQUENCING (SOFT_ARCHITECTURAL_ORDERING) only, not a hard prerequisite. R12 = E3_RECONCILED_NO_STANDALONE_ACTION (E3-LR1 §8; interaction boundary only). R14 = PHASE_F_SHARED_BOUNDARY_REVIEW / NO_CHANGE_CURRENTLY_JUSTIFIED (E3-LR1 §9 governs any future shared-selection change). F3 = bounded R03/R05/R06 fixed-locator/fallback package; D4 owns the YAML query-expansion locator-retirement pattern, the confirmed HOLDs, and R20, while R03/R05/R06 are independent code origins outside the D4 rule inventory. Promotion materiality: R13/R10/R08-R09-R11/R04 promotion-relevant material; R01/R14 potentially material when coupled; R03/R05/R06 localized non-material. Recommended execution order: R13 → R10 → R08/R09/R11 → R14 review (conditional) → R04 → R01 → R03/R05/R06; recommendation only, each step separately authorized.
- **Planning implication:** NEXT_TASK_RECOMMENDATION = R13 bounded verifier-support semantic cleanup; RECOMMENDED, NOT AUTHORIZED. Promotion relevance is not promotion authorization; default promotion stays deferred (D3).
- **Evidence:** `evaluation/PF_LR1_PHASE_F_SCOPE_RECONCILIATION.md` and `evaluation/pf_lr1_phase_f_scope_reconciliation.json`.

### F2 — Generalize benchmark-specific guards

- **Status:** COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE
- **F2-A1 outcome:** COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED. Removed the hard-coded explicit-code-token whitelist and both comparison-wording deterministic-support branches from `_verify`; deterministic support is now granted only by generic shape-based, evidence-grounded coverage invariants (full identifier/path coverage, path coverage over a cited code repository, multi-symbol coverage). Three new focused contract tests plus the authoritative focused E3 deterministic set (49) and neighboring E2-A1 tests (91 total) passed with zero scientific calls. Report: `evaluation/F2_A1_VERIFIER_SUPPORT_SEMANTIC_CLEANUP.md`.
- **F2-A1-R1 outcome:** COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED. Corrective repair: an independent post-commit audit found that the retained lexical coverage branches could still override a whole-claim semantic `unsupported` verdict (citation/locator/identifier grounding is not whole-claim entailment). The `deterministically_supported_claims` set and all coverage-based exemption branches were deleted entirely — the semantic review's unsupported verdict is always honored. Adversarial contracts T1-T6, tests/unit/test_qa.py (58 passed + 2 subtests), the focused E3 deterministic set (49) and neighboring E2-A1 tests (91 total) passed with zero scientific calls; R10/retrieval/selection surfaces have zero diff. Report: `evaluation/F2_A1_R1_VERIFIER_SUPPORT_SEMANTIC_ENTAILMENT_REPAIR.md`.
- **F2-A2 outcome:** COMPLETE / PASS / QUESTION_DERIVED_POINTER_NORMALIZATION_COMPLETENESS_ESTABLISHED. The pointer-normalization requirement now derives its `target_symbol` from the live question's pointer type expression; `_requirement_evidence`, `_compact_requirement_evidence`, and `_deterministic_missing_requirement_ids` evaluate against the question-derived target, and the fixed `pndlmdtrackq`/`lmdtrackq`/`tclonesarray` anchors are deleted from qa.py. Genericity/adversarial contracts T1-T8 (unseen `SensorFrame*` works end to end; the wrong historical symbol cannot satisfy an unseen target; plan-only symbols never become targets) all pass; tests/unit/test_qa.py 66 passed + 4 subtests, focused E3 deterministic set (49) plus neighboring E2-A1 tests (91 total) passed with zero scientific calls. Report: `evaluation/F2_A2_DETERMINISTIC_COMPLETENESS_SEMANTIC_CLEANUP.md`.
- **F2-A3 outcome:** COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED. In coverage modes (shadow_e1_v2, runtime_e1_v2) whole-answer completeness is owned by claim-to-answer-point coverage and bounded revision via missing_answer_point_ids; deterministic missing-requirement enforcement is not executed, the review's known missing_requirement_ids are ignored, plan-driven dataflow augmentation is disabled, and required_boundary_locators payloads are empty. The named-requirement contract remains fully active as the legacy_question_core bridge. The E3 second-verify deterministic-requirement view was retired with its consumer; claim-level retained-ledger protection is preserved; _augment_planned_locators is retained (question-grounded). Seam tests prove the ownership transfer in both coverage modes and legacy preservation; one E2 and three E3 tests updated accordingly; test_qa 70 passed + 6 subtests, E2-A1 42 + focused E3 49 → 91 passed. Report: `evaluation/F2_A3_E1_E2_COMPATIBILITY_RETIREMENT.md`.
- **F2-A3-R1 outcome:** COMPLETE / PASS / COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REMOVED. Corrective repair: an independent post-commit audit found the legacy requirement axis still live in model-facing payloads — coverage-mode generation/review/revision received the full legacy answer_requirements, the coverage prompt contracts treated them as a completeness axis, and a stale supported=false explained only by legacy ids could still create global failure. Coverage-mode model-facing payloads now carry no legacy requirements, the coverage prompt extensions declare them non-authoritative (PROMPT_SET_VERSION 3.8.0 -> 3.9.0), stale known legacy ids are reconciled as obsolete, unknown ids remain structurally guarded, and genuine failures are retained. T1-T12 pass; tests/unit/test_qa.py 76 passed + 11 subtests, E2-A1 42 + focused E3 49 -> 91 passed. Report: `evaluation/F2_A3_R1_COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REPAIR.md`.
- **F2-A4 outcome:** COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED. The exact bare-class negative control (R04) was generalized: `_requested_bare_class_symbols` extracts question-grounded candidates (explicit class/struct/enum wording, pointer expressions, compound-cased identifiers in request/definition contexts; plan-only symbols and plain prose excluded), `_answerability_guard` checks the locked-corpus catalog (not selected evidence) and emits the structured error `unsupported requested symbol: <symbol>`, `_sufficiency`'s exact branch was removed, and `_finalize` emits dynamic generic refusal wording with an optional anchor-ranked evidence-grounded basis claim — no fixed historical locator and no substitute-implementation assertion remain. T1-T15 plus the catalog-authority and premise-mismatch sentinels pass; test_qa 89 passed + 16 subtests, combined focused run 193 passed. Report: `evaluation/F2_A4_PREMISE_REFUSAL_GENERALIZATION.md`.
- **F2-A4-R1 outcome:** COMPLETE / PASS / QUESTION_GROUNDED_PREMISE_REFUSAL_BOUNDARY_ESTABLISHED. Corrective repair: plan-only anchors no longer admit or rank unsupported_symbol refusal bases (question-only anchors), explicit class/struct/enum and pointer captures require a code-like identifier shape ("class of"/"struct layout" inert), and locator contexts ("where is", "which file", "path", ...) restore the bare locator premise; four full-path test fixtures were corrected with realistic catalog rows instead of weakening production semantics. Plan-contamination, natural-language, bare-locator, catalog-authority, premise-mismatch, R05/R06, E3-early-refusal, and F2-A3-R1 sentinels all pass; test_qa 95 passed + 16 subtests, combined focused run 200 passed. Report: `evaluation/F2_A4_R1_QUESTION_GROUNDED_PREMISE_REFUSAL_REPAIR.md`.
- **F2-A5 outcome:** COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED. The fixed R01 config mappings (theory->paper, implementation->paper+code) were retired to []; `_question_grounded_source_obligations` derives paper/code hard obligations from the raw question only (bounded vocabulary, deterministic order, support-span receipt in plan.analysis_diagnostics), the intent only selects the regime for R01 intents, R02/HOLD mappings and all source budgets are byte-identical, and every consumer (paper channel, exact-paper priority, required-first/backfill, sufficiency) keeps gating on the dynamic plan field. Explicit obligations still produce honest insufficiency; no-obligation questions are not refused for source-class absence. T1-T24 pass; test_retrieval 47 passed + 7 subtests, test_qa 91 passed + 16 subtests, combined focused run 249 passed. With all five groups complete, F2 = COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE. Report: `evaluation/F2_A5_SEMANTIC_SOURCE_OBLIGATION_GENERALIZATION.md`.
- **F2-A5-R1 outcome:** COMPLETE / PASS / SOURCE_OBLIGATION_MATCHING_BOUNDARY_ESTABLISHED. Corrective repair: the question-grounded helper's unbounded substring matching (behavior-confirmed false positives: "hypothesis" -> paper via "thesis", "macroscopic" -> code via "macro", "paperless" -> paper, ambiguous bare "which source" -> code) was replaced by bounded whole-token / explicit-phrase matching with actual-phrase support spans; the ambiguous bare "which source" is no longer a sufficient code trigger; the consumer chain is untouched. Precision matrix (paper/thesis/publication/literature/journal -> paper; source code/implementation/implemented/signature/macro/which file/which source file -> code; hypothesis/paperless/journaled/macroscopic/which-source-of-uncertainty -> none) and T1-T26 including the end-to-end sufficiency false-positive sentinel all pass; test_retrieval 52 passed + 7 subtests, test_qa 93 passed + 16 subtests, combined focused run 255 passed. F2-A5 and the aggregate F2 closure are authoritative only after R1. Report: `evaluation/F2_A5_R1_SOURCE_OBLIGATION_BOUNDARY_REPAIR.md`.
- **Bounded scope (PF-LR1):** Groups A–E above (R13; R10; R08/R09/R11 compatibility retirement; R04; R01). R12 is not an F2 task; R14 remains outside mandatory modification unless a present defect is evidenced.
- **Goal:** Replace hard-coded symbol or premise guards with generic handling of false premises, unknown symbols, locked-corpus existence checks, and generic refusal logic.
- **Scope:** Generalize failure-class guards not reducible to D4 locator migration, ensuring robust behavior across unseen symbols.
- **Dependencies:** F1, C5, D2, and existing verifier contracts.

### F3 — Incremental shortcut removal

- **Status:** COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED
- **Bounded scope (PF-LR1):** The R03/R05/R06 fixed-locator/fallback cleanup package. Ownership was reconciled against D4 by implementation origin and lifecycle ownership: D4 already implemented the phrase-to-answer-location retirement pattern for YAML query-expansion locators (five active migrations) and owns R20 plus the confirmed HOLDs; R03/R05/R06 are independent code origins in `retrieval.py`/`qa.py` outside the D4 rule inventory. Shared literals with D4 rules are coordinated, never globally deleted. D4 is not reopened and no D4-A11 is created.
- **Context:** Original F3 planned incremental retirement of phrase-to-answer-location shortcuts once generic replacements were proven. That pattern was implemented by D4 for bounded query-expansion locators; that portion of F3 closes as superseded without new implementation.
- **Outcome:** COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED. R03: the `Retriever.analyze` feedback page override (theory intent + feedback phrases + existing li_2026 hints → forced `[141, 149, 151]`) was deleted; reviewed query-expansion semantics are the only page-hint authority and the D4-owned `reconstructed_profile_to_acceptance` rule keeps its shared page values. R05: the unsupported-API finalizer's fixed `PndPidCorrelator.h` fallback was removed; generic requested-owner matching survives and the optional claim asserts only what the cited evidence supports with no header assumption. R06: the deleted-runtime finalizer's fixed `ana_dpm.C` lookup and unconditional `event_poca` wording were replaced by an artifact-neutral refusal plus a bounded `deleted_runtime` kind in the generic `_refusal_basis_evidence` selector (already-selected bundle, identifier-like question artifact anchors, no fixed path preference, `None` when nothing is relevant). Static sentinels assert the three historical literals are gone from production sources; adversarial contract T1–T24 passes (170 passed + 46 subtests across both focused test files); zero scientific/evaluation calls. Report: `evaluation/F3_FIXED_LOCATOR_FALLBACK_CLEANUP.md`.
- **Dependencies:** F1, F2, and Phase D/E outcomes.

### F4 — Separate answer-generation and semantic-verification roles

- **Status:** COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED
- **Problem:** One client/model role for generation and review creates correlated failures and hides objectively checkable verification.
- **Goal:** Make generation and verification roles/configuration/client paths separable, even if they initially share a model.
- **Why this stage:** Answer completeness is generic and shortcut dependency is reduced, allowing role separation without confounded behavior.
- **Intended design:** Move identifier/path/source/version/locator/evidence-ID/numeric provenance checks to deterministic logic; reserve semantic verification for entailment, causality, comparison, and faithful summary.
- **Functional requirements:** Independent role identities/usage, deterministic fail-closed checks, semantic review contract, and compatibility with bounded revision.
- **Explicit out of scope:** Switching models merely for novelty, composer, unbounded review, or loosening verification.
- **Dependencies:** E2/E3 and existing verifier.
- **Planned evaluation scope (not authorized):** T0 verifier fixtures and targeted T2 supported/unsupported claims.
- **Primary metrics:** False acceptance, false rejection, deterministic coverage, model-call/token cost, and grounding.
- **Acceptance criteria:** Roles are independently configurable/auditable and objective facts are checked deterministically without quality regression.
- **Failure handling:** Retain the safe existing verifier path when separation is inconclusive; never silently bypass verification. Stop after F4.
- **Outcome:** COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED. `VertexSettings` gained the optional `verification_model` (`QA_VERIFICATION_MODEL_ID`, defaulting to the generation model) plus `effective_verification_model`/`for_verification_model()`; `generate_json` gained a `usage_stage` label with additive role-specific call/token counters (`qa_generation_*`, `qa_semantic_verification_*`) that leaves unlabeled aggregate behavior byte-compatible; the production default builds distinct generation/verification client paths even at equal model IDs; `_answer`/`_revise` route to the generation role, `_verify` semantic review (legacy + coverage + E3 second verify) routes to the verification role; usage aggregation sums unique role clients without double-counting a shared injected client; internal `model_roles` diagnostics added. The evaluation judge remains offline-only; deterministic integrity checks stay application authority and the semantic unsupported verdict stays authoritative; failure semantics fail closed with no cross-role fallback; sole legacy `vertex=` injection serves both roles as an explicit compatibility seam. Adversarial contract T1–T30 passes; zero scientific/evaluation calls. Report: `evaluation/F4_GENERATION_VERIFICATION_ROLE_SEPARATION.md` (initial closeout corrected by F4-R1).
- **F4-R1 outcome:** COMPLETE / PASS / PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTED. The internal `model_roles` receipt misidentified the generation role under `QA_GENERATION_MODEL_ID != QA_VERIFICATION_MODEL_ID` (reporting B/B and `same_model_id=true` for an A/B configuration) because it consulted the base `verification_model` configuration field instead of each role client's actual `settings.generation_model`; the repair is confined to `_model_roles_diagnostics` reporting. Reproduced before the fix (B/B/same=true) and verified after (A/B/same=false) through the production construction path; routing, client construction, usage accounting, judge isolation, authority boundaries, and public schema are zero-diff; central regression test added with real A/B/C base settings; test_qa 136 passed + 19 subtests. Final F4 closure is achieved only after F4-R1. Report: `evaluation/F4_R1_PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTION.md`.

### F5 — Bounded Answer Composer

- **Status:** COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED
- **Problem:** Deterministic verified-claim rendering is safe but can be mechanical and claim-by-claim.
- **Goal:** Improve readability without reopening factual generation.
- **Why this stage:** Only after claims, answer points, and verification roles form a stable security boundary can composition be safely added.
- **Intended design:** Composer receives verified claims only, may reorder/merge/group/add discourse connectors/lightly paraphrase, and returns paragraphs plus source claim IDs.
- **Functional requirements:** Validate claim IDs, claim coverage, identifiers, numeric literals, causal/comparison content, and zero new facts; fall back to deterministic renderer on any failure.
- **Explicit out of scope:** Raw retrieval evidence as composer input, new facts/entities/paths/numbers/causal relations/comparisons/requirements, or readability over safety.
- **Dependencies:** E2 and F4.
- **Planned evaluation scope (not authorized):** T0 adversarial validation and targeted T2 readability/faithfulness cases.
- **Primary metrics:** New factual hallucination rate (hard target 0), claim coverage, validation fallback rate, and human readability preference.
- **Acceptance criteria:** No new factual content is introduced and readability improves; every paragraph maps to verified claims.
- **Failure handling:** Fall back to deterministic verified-claim rendering, record validation failure, and do not retry freely. Stop after F5.
- **Outcome:** COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED. The composer receives only verified claim ids/texts (never the question, evidence, evidence_ids, plan, or drafts; citations are application-owned), runs on the F4 generation role with `usage_stage="qa_composer"`, and emits `{paragraphs:[{text, source_claim_ids}]}` gated by deterministic validation before any semantic review: exact-once claim coverage, conservative technical-identifier and exact numeric-literal provenance, and bounded causal/comparison cue gates. Exactly one semantic composition review runs on the F4 verification role (claims+paragraphs only, entailment/preservation, fail-closed review validation). Acceptance is atomic: any exception, validation failure, or rejection falls back to the byte-identical deterministic renderer without failing the QA request or touching verification_errors; no retries (max 1+1 calls; single-claim and all refusal paths bypass with zero calls). Citations derive deterministically per paragraph; `QAResult.claims`/`evidence`/schema/default unchanged; sanitized 8-key internal `diagnostics["composer"]` receipt only; `qa_composer_*` usage aggregates without touching F4 counters; E3 retained claims flow through the same gate. Adversarial contract T1–T43 passes; 49-test E3 suite passes unmodified through the fallback design. READABILITY_BENEFIT = NOT_EMPIRICALLY_EVALUATED_IN_F5; zero scientific/evaluation calls. Report: `evaluation/F5_BOUNDED_ANSWER_COMPOSER.md` (initial closeout corrected by F5-R1).
- **F5-R1 outcome:** COMPLETE / PASS / EXACT_LITERAL_IDENTIFIER_PROVENANCE_BOUNDARY_ESTABLISHED. Both deterministic provenance checks had used substring membership (behavior-confirmed false acceptances: `-3→3`, `13→3`, `10%→10`, `3→+3`, `3.0→3`, `1e3→1e+3`; `PndPidCorrelatorV2→PndPidCorrelator`, `createLmdFitDataLegacy→createLmdFitData`, path shortening, case-altered aliases). Repair: exact extracted-token membership for numeric literals (explicit sign attribution, lookbehind keeps identifier-embedded digits inert, spelling-distinct decimals/percent/scientific forms) and technical tokens (case-/spelling-sensitive), plus a bounded casing-alteration sentinel closing the lowercase-alias bypass. All rejects fail before semantic review and fall back to the exact deterministic renderer; error codes, input boundary, coverage, review, citations, public contracts, F4/F4-R1, E3, F2/F3, and the default are unchanged; the composer prompt gained the authorized bounded identifier clarification (PROMPT_SET_VERSION 3.10.1). 16 new sentinel tests; test_qa 195 passed + 21 subtests, E3 suite 49 passed. Final F5 closure is achieved only after F5-R1. Report: `evaluation/F5_R1_EXACT_LITERAL_IDENTIFIER_PROVENANCE_REPAIR.md`.

### F6 — Release evaluation and generalization gate

- **Status:** IN_PROGRESS / ATTEMPT_3_INFRASTRUCTURE_RECONCILED_READY_FOR_NEW_PREFLIGHT
- **F6-A — Pre-Release Validation & Generalization Gate:** COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (attempt 1, historical: candidate f6a-rc1-20260913; nine preregistered gates failed per the R1-corrected matrix, dominated by erroneous "not defined in the locked corpus" refusals and version-conflict handling errors; fail-fast preserved novel_validation pristine; ablation/composer audit not reached)
- **F6-A attempt 2:** COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Stage A1 fail-fast; ablation/novel/composer stages NOT_REACHED). Fresh identity: preregistration `3f1f16e`, candidate f6a-rc2-20260913 frozen from the clean preregistration HEAD (`1f32eef`, verify valid), zero post-freeze changes. Zero-call A0 preflight (Gold authority, calibration v3 compatibility, selector re-derived 59 IDs e27ef67a, Docker/index identity, roadmap ten→nine correction, 314+68 focused tests, clean FR1 boundary audit). Run f6a-rc2-gold-formal-full-20260913: 59/59 complete, zero errors, zero status mismatches, expected_status_accuracy 1.0 — all eight FR1-reviewed cases now match Gold. Six mandatory gates still fail (final_evidence_recall 0.8810, critical_final_evidence_recall 0.8912, required_source_coverage 0.9592, dual_source 0.0 with g060 answered but paperless, critical misses 4, major unsupported 1); release score 0.9463 (attempt-1 0.8277). No repair during the attempt; no pass chasing. Usage 376 calls / 3,313,651 tokens; novel_validation remains PRISTINE_FOR_CURRENT_LINEAGE. Report: `evaluation/F6_A2_PRERELEASE_VALIDATION_RESULT.md`.
- **F6-A2-FR1 — Post-Attempt-2 Residual Failure Review:** COMPLETE / PASS / RESIDUAL_FAILURES_CLASSIFIED
  (zero-scientific-call review-only attribution; Attempt-2 FAIL preserved and shown robust). Complete
  contributor sets for all six failed gates derived from the immutable records (aggregation cross-checked
  exactly); committed immutable run receipt records evidence hashes. Three-layer attribution of the 10
  gate-contributing evidence groups: 7 selected-but-dropped at the final answer evidence layer, 2
  retrieved-but-not-selected, 1 retrieval miss; zero index-unsatisfiable; zero selected-but-not-credited (no
  evaluator defect). Classification: PRODUCT_DEFECT g013/g016/g021/g022/g060/g113; GOLD_CONTRACT_DEFECT
  g001/g014 (sphinx-form-only group selectors rejecting same-content repository source files); MIXED
  g005/g011/g020/g044; no standalone stochastic variation; nothing inconclusive. Routing: forward-only Gold
  contract review first, then bounded product repair. Report:
  `evaluation/F6_A2_FR1_RESIDUAL_EXPOSED_GOLD_FAILURE_REVIEW.md`.
- **F6-A2-GR1 — Forward-Only Gold Contract Adjudication:** COMPLETE / PASS / FORWARD_ONLY_GOLD_CONTRACT_ADJUDICATED_AND_SUCCESSOR_ESTABLISHED
  (zero-scientific-call benchmark governance; adjudication committed before any benchmark change). Established rule from deterministic
  lineage/content evidence: sphinx/<Section>/<Page>.html ↔ docs/<Section>/<Page>.rst are equivalent representations of the same locked
  documentation. Dispositions: g001 BROADEN + p1 reword (commit-specificity not entailed), g005 p1 reword (develop-vs-run contrast absent
  from the required evidence), g011 BROADEN, g014 BROADEN (incl. Running_Sequence.rst), g044 KEEP_AS_IS (intentional pflueger source lock;
  broadening would be motivated only by Attempt-2's answer), bounded sweep corrections g008/g013/g015/g016/g022/g089/g101/g106/g109
  (additive; sphinx selectors preserved; title-form groups without demonstrated failure recorded KEEP_AS_IS). Successor benchmark
  m6-benchmark-v2.7 created (dataset SHA 4dcc9d06…; 13 changed cases; product validator green) with successor calibration
  phase_b_t3_product_language_scope_v4 (mechanical carry-forward; selector 59 IDs e27ef67a…, membership identical to v3). v2.6 remains the
  authority for Attempts 1 and 2; Attempt-2 FAIL unchanged; no retroactive rescoring; v2.7 applies to future attempts only. Report:
  `evaluation/F6_A2_GR1_FORWARD_ONLY_GOLD_CONTRACT_ADJUDICATION.md`.
- **F6-A2-GR1-R1 — Gold Successor Provenance Reconciliation:** COMPLETE / PASS / UNJUSTIFIED_V2_7_DELTA_RETIRED_FORWARD_ONLY
  (zero-scientific-call governance reconciliation; original GR1/v2.7 commit history untouched). g016.e1 — a title-form group
  that had entered the v2.7 change set without independent adjudication — is now independently adjudicated and its repo-source delta
  REJECTED: docs/EventGenerators/DPMGenerator.rst is a 96-byte doxygen stub whose rendered page content derives from code annotations,
  so the GR1 content-equivalence requirement fails and the addition would not have occurred but for the Attempt-2 outcome. g022.e2 is
  confirmed part of the original bounded path-form sweep (bookkeeping omission only). Exact path-form set reconstructed: 12 pairs
  (primary g014.e2 + 11 additional). Open finding recorded for the next governance task: docs/Tools/PndMasterTasks/PndMasterRunSim.rst
  (105-byte doxygen stub) was sweep-added to five groups — outside GR1-R1 authority. Forward-only successor m6-benchmark-v2.8 created
  from v2.7 (dataset SHA 67c992ce…; only repair = g016.e1 selector removal; product validator green) with calibration
  phase_b_t3_product_language_scope_v5 (mechanical carry-forward; selector 59 IDs e27ef67a…, membership identical to v3/v4). Authority:
  v2.6 historical for Attempts 1/2; v2.7 historical provisional successor (never used scientifically); v2.8 stabilized for future
  attempts. Attempt-2 FAIL unchanged; no retroactive rescoring. Report:
  `evaluation/F6_A2_GR1_R1_GOLD_SUCCESSOR_PROVENANCE_RECONCILIATION.md`.
- **F6-A2-GR1-R2 — Doxygen-Stub Evidence-Selector Cleanup:** COMPLETE / PASS / REMAINING_POINTER_STUB_SELECTORS_RETIRED_FORWARD_ONLY
  (zero-scientific-call governance cleanup; audit committed before benchmark mutation). Mechanically derived universe: 22
  (case,group,path) triples / 11 unique paths (21/10 inherited by v2.8 after the GR1-R1 DPMGenerator retirement). Classification:
  5 CONTENT_BEARING_DOCUMENT, 4 INCLUDE_AGGREGATOR_WITH_CLOSED_CORPUS_TARGETS (Installation.rst/Macros.rst/Running.rst/
  PndMasterTasks.rst — all include/toctree targets verified inside the frozen corpus), 1 DOXYGEN_OR_EMPTY_POINTER_STUB
  (docs/Tools/PndMasterTasks/PndMasterRunSim.rst, 105 bytes) retired forward-only from g013.e1/g013.e2/g015.e1/g016.e2/g089.e1
  with no group emptied and no legitimate coverage weakened. Forward-only successor m6-benchmark-v2.9 created from v2.8 (dataset SHA
  eaacd3ed…; changed cases g013/g015/g016/g089; product validator green) with calibration
  phase_b_t3_product_language_scope_v6 (mechanical carry-forward; selector 59 IDs e27ef67a…, membership identical to v3/v4/v5).
  Authority: v2.6 = Attempts 1/2 historical; v2.7/v2.8 = historical provisional successors (never used scientifically); v2.9 =
  stabilized future Gold authority. Attempt-2 FAIL unchanged; no retroactive rescoring. Report:
  `evaluation/F6_A2_GR1_R2_DOXYGEN_STUB_SELECTOR_AUDIT.md`.
- **F6-A2-FR2 — Bounded Product Repair and New Candidate Development:** COMPLETE / PASS / RESIDUAL_PRODUCT_MECHANISMS_REPAIRED_AND_NEW_CANDIDATE_DEVELOPED
  (zero-scientific-call development against stabilized m6-benchmark-v2.9; Gold/evaluator/thresholds untouched; R0 rebase confirmed all
  eight residual targets applicable). Repaired mechanisms (test-first): (A) source-obligation evidence retention — obligations gated
  retrieval sufficiency only, letting answers drop already-selected obligated-type evidence at the final projection; new
  _augment_source_obligation_evidence adds one bounded evidence-bound anchor claim per uncovered required source type (question-anchor
  gated, mirrors _augment_planned_locators); (D) unsupported-claim revision discipline — _revise drops an identical-normalized-text
  restatement of a claim just found unsupported, preventing second-pass verdict flips from resurrecting it (substantively narrowed
  revisions pass). Deferred: pool→final selection diversity (g011/g020) and genuine retrieval miss (g021) — no safe generic fix without
  scientific measurement. Verification: 6 new tests + controls, 269 passed + 50 subtests, zero new regressions vs the pre-existing
  baseline. PROMPTS untouched; candidate NOT frozen; Attempt 3 NOT preregistered. New candidate-development HEAD `ef9a8db`. Report:
  `evaluation/F6_A2_FR2_BOUNDED_PRODUCT_REPAIR_AND_NEW_CANDIDATE_DEVELOPMENT.md`.
- **F6-A2-FR2-R1 — Source-Obligation Public-Content and Coverage-Mode Boundary Repair:** COMPLETE / PASS /
  SOURCE_OBLIGATION_PUBLIC_CONTENT_AND_COVERAGE_BOUNDARIES_REPAIRED (zero-scientific-call bounded correction; initial
  FR2 record above is historical, corrected by FR2-R1; Cluster D preserved, B/C defer preserved). The rejected
  augment mechanism (public provenance-meta claims synthesized from plan.required_source_types, active in coverage
  modes, divergent classifier) was retired entirely; question-grounded multi-source obligations are now expressed
  through the legacy answer-requirement contract (`source_role_grounding`: ground each part of the explanation in the
  source kind that actually supports it; provenance-only statements forbidden) with a deterministic cited-evidence
  coverage backstop and requirement-evidence mapping into the legacy revision path; source-type classification
  centralized into `_evidence_source_types` shared with `_sufficiency`. Coverage firewall (shadow/runtime
  answer_requirements = []) regression-locked. PROMPTS untouched; product files qa.py + test_qa.py; 274 passed +
  52 subtests, zero new regressions vs pre-existing baseline. New candidate-development HEAD `d323f79`; candidate NOT
  frozen; Attempt 3 NOT preregistered. Report:
  `evaluation/F6_A2_FR2_R1_SOURCE_OBLIGATION_BOUNDARY_REPAIR.md`.
- **F6-A Attempt 3 — Prerelease Validation & Generalization Gate:** HOLD / PRE_RELEASE_PRECONDITION_NOT_MET
  (zero-outcome preflight; scientific execution never started; calls/tokens 0). Verified clean: product lineage
  d323f79 (zero drift), product boundary audit, Gold v2.9 identity, selector re-derivation (59 IDs e27ef67a…),
  Docker/index identity, focused tests 325+70. Two preregistration blockers from the GR1 chain: the candidate
  freezer hard-binds v2_6/m6-benchmark-v2.6 (v2_9 lacks manual_adjudications.yaml; any freeze would bind v2.6), and
  the calibration loader successor chain stops at v3 (v4/v5/v6 unloaded; v3 incompatible with v2.9). A0 is
  validation, not development — no repair performed, no preregistration, no freeze; A1–A5 NOT_REACHED;
  novel_validation = PRISTINE_FOR_CURRENT_LINEAGE. Report:
  `evaluation/F6_A3_PRERELEASE_VALIDATION_RESULT.md`.
- **GOLD-9 — Authority Binding Infrastructure Reconciliation:** COMPLETE / PASS / RELEASE_AUTHORITY_CHAIN_RECONCILED
  (zero-scientific-call bounded reconciliation after the Attempt-3 HOLD; that HOLD is preserved as the historical
  terminal result of that preflight). Repaired: candidate freezer now binds the shared signed-Gold resolver
  (`newest_signed_exposed_gold_dir`: mechanical v2_N discovery, manifest-consistency qualification, highest version)
  instead of hard-coded v2_6; `default_gold_dataset_path` is resolver-first with the historical chain as old-checkout
  fallback; the calibration loader mechanically selects the newest `scope_vN` artifact (v6) eliminating the silent
  v3 authority; manual-adjudications dependency made optional (v2.9 carries none; hash None recorded; no v2.6 copy).
  Cross-layer consistency demonstrated (resolver/default-dataset-path/freezer/product-scope all resolve v2.9
  eaacd3ed… + v6 fe56d4ca… + 59 IDs e27ef67a…). Focused tests 53+18 and 274+52 — zero new regressions; product QA
  behavior untouched. Report: `evaluation/GOLD_9_AUTHORITY_BINDING_INFRASTRUCTURE_RECONCILIATION.md`.
- **F6-A Attempt 3 — Continuous Pre-Release Validation & Generalization Gate:** COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
  (continuous execution after GOLD-9; preregistration commit `2f9a4a3`; frozen candidate `f6a-rc3-20260914`, manifest SHA `be2101a4..`).
  Formal-English Gold v2.9 cohort (59 expected, 58 scored, 1 unhandled exception g013 due to Vertex 429 RESOURCE_EXHAUSTED).
  Release score 0.9741 (58-case diagnostic only; full-cohort release score INCOMPLETE).
  Four mandatory gates failed: critical_final_evidence_recall 0.9410 (<1.00; failing: g011, g022, g044, g060), critical_answer_point_miss_count 3 (>0; failing: g022, g023, g115), paper_code_dual_source_rate 0.0 (<1.00; failing: g060), unhandled_exception_count 1 (>0; g013 Vertex 429).
  Passing gates: gold_recall_at_10 0.9792, final_evidence_recall 0.9306, intent_accuracy 0.9828, per_intent_gold_recall_at_10 (min 0.9500), per_intent_intent_accuracy (min 0.9231), expected_status_accuracy 1.00, citation_integrity 1.00, wrong_version_evidence 0, forbidden_evidence 0, required_source_coverage_answered 0.9792, identifier_hallucination_rate 0.00, answer_point_coverage 0.9741, contradiction_count 0, major_unsupported_claim_count 0.
  Raw canonical matrix evaluated 14 PASS, 4 FAIL, 0 incomplete flags strictly on available observations; raw flags are diagnostic, not complete-cohort PASS; full-cohort measurements remain INCOMPLETE due to unmeasured g013. Missing measurements are treated as INCOMPLETE (not FAIL per policy). Hard measured FAIL on evaluated cohort is terminal for the prerelease gate, while missing g013 status is INCOMPLETE separately.
  Explicit late receipt protocol deviation: late run receipt (`evaluation/f6_a3_a1_receipt.json`) was written after failure case diagnosis was already inspected. Inherited prior execution evidence: A0 focused tests (327 passed + 70 subtests).
  Fail-fast halted scientific execution immediately; stages A2–A5 NOT_REACHED; novel_validation remains PRISTINE_FOR_CURRENT_LINEAGE; holdout access = 0; F6-B LOCKED.
  Observed Attempt-3 scientific usage: 397 model calls, 3,783,197 tokens (final 59 records: 387 calls / 3,745,918 tokens; preserved 3 initial 429 failed attempts: 10 calls / 37,279 tokens).
  Report: `evaluation/F6_A3_PRERELEASE_VALIDATION_RESULT.md`, forward-only closeout audit addendum: `evaluation/f6_a3_closeout_verification.json`.
- **F6-A-FR1 — Exposed Gold Failure Review & New Candidate Development:** COMPLETE / PASS / ROOT_CAUSES_ESTABLISHED_AND_BOUNDED_FIXES_IMPLEMENTED (zero-scientific-call development task; all eight exposed status mismatches explained by two generic root causes — RC1 repository display names refused as bare class symbols by the premise guard while the object catalog legitimately lacks repository identities, RC2 prepositional commit requests missing the version-repository binding so the SHA never reached the locked-version comparison with the status precedence itself confirmed correct; bounded generic fixes: manifest-driven Retriever.is_repository_reference + guard repository-identity exclusion, and a bounded prepositional connector in _has_explicit_version_repository_binding; nine test-first regression tests added, preserved-refusal controls intact, zero new test failures; F6-A FAIL preserved; product-fix HEAD `45f14ba`; candidate NOT frozen, F6-A NOT preregistered). Report: `evaluation/F6_A_FR1_EXPOSED_GOLD_FAILURE_REVIEW_AND_CANDIDATE_DEVELOPMENT.md`.
- **F6-B — Protected Blind Release Gate:** LOCKED / F6_A_DID_NOT_PASS (requires an F6-A PASS with the identical frozen candidate; physical protected holdout availability required; single protected blind release attempt; the only protected blind release decision)
- **Problem:** Final readiness requires simultaneous evidence on exposed benchmark, novel validation, protected holdout, and shortcut-dependency ablations.
- **Goal:** Execute the complete release measurement and decide whether generalization improved without sacrificing grounding/version safety.
- **Why this stage:** This is the final gate only after all requested architecture and cleanup tasks are complete/frozen.
- **Intended design:** Freeze identity; run T5 full benchmark, novel, external holdout, and ablations; report infrastructure, query, retrieval, answer, targeted retrieval, composer, cost, generalization gap, and benchmark dependency.
- **Functional requirements:** Explicit `T5`/`release evaluation` authorization, protected holdout handling, immutable records, full usage accounting, complete splits, and no tuning from holdout outcomes.
- **Explicit out of scope:** Any implementation fix during the same frozen run, targeted holdout tuning, mixed identities, or diagnostic composites represented as release gates.
- **Dependencies:** F1–F5 and explicit user authorization.
- **Planned evaluation scope (not authorized):** T5 only.
- **Primary metrics:** Index/embedding integrity; intent/symbol/concept metrics; Recall@5/@10/@20, MRR, final-evidence recall; point coverage, unsupported claims, citations/identifiers; targeted success; composer new-fact/readability; benchmark score, novel score, Generalization Gap, and Benchmark Dependency.
- **Acceptance criteria:** Planned thresholds are declared before running; grounding/citation/version invariants pass; novel performance and dependency/gap meet the approved release criteria with only bounded benchmark regression.
- **Failure handling:** Report `FAIL` or `INCONCLUSIVE`, archive immutable evidence, and do not tune on protected holdout. A later fix requires a new explicitly requested roadmap task and candidate. Stop after F6.
- **Outcome (first attempt, historical):** HISTORICAL / ZERO_OUTCOME / valid under the then-authorized protocol — HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET. The task was explicitly authorized including T5, but the staged fail-fast order stopped at the zero-outcome preflight: the protected external holdout package (panda-novel-holdout-v1) is not available on the execution machine and no protected execution workspace exists there. No cohort was exposed; scientific/evaluation calls = 0. Completed reusable preflight: the candidate freezer now binds signed m6-benchmark-v2.6 (`manual_adjudications.yaml`), records the F4 runtime/effective verification-model identities and `primary_answer_point_mode`, and fingerprints the complete ten-prompt active set (commit `c871444` + `99fdbab`); a signed v2_6 manifest record lag behind the authorized D4-A2-R1 g021 correction — which had silently diverted the evaluator to m6-benchmark-v2.5 — was aligned with full provenance, restoring v2.6/120 as the evaluator authority. Preregistration and candidate freeze were deferred to the executing attempt. Report: `evaluation/F6_RELEASE_EVALUATION_AND_GENERALIZATION_GATE.md`.
- **F6-LR1 outcome (staging reconciliation):** COMPLETE / PASS / RELEASE_GATE_STAGING_RECONCILED. F6 is formally staged as `F6-A — Pre-Release Validation & Generalization Gate` (Gold v2.6, novel_dev, novel_validation, ablation, composer audit; holdout governance/metadata integrity is its precondition; positive terminal state `HOLDOUT_ELIGIBLE`) and `F6-B — Protected Blind Release Gate` (the only protected blind release decision; requires F6-A PASS with an identical frozen candidate identity; physical holdout availability is a B1/B2 prerequisite). The attempt-1 HOLD is preserved as historical evidence and no longer blocks F6-A. Dataset roles, the holdout-budget principle, candidate-identity continuity, validation exposure semantics, and run orders A0–A7/B0–B5 are fixed; the five preflight engineering findings are carried into F6-A Stage A0 without implementation. Attempt-1 artifacts remain unmodified; zero product/evaluator/manifest changes; zero scientific/evaluation calls. Report: `evaluation/F6_LR1_RELEASE_GATE_STAGING_RECONCILIATION.md`.
- **F6-A outcome (first executed stage):** COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED. Stage A0 resolved all carried engineering debt and reconciled the product-language calibration as successor v3 (mechanical; g021 criticality-only). The exact 59-ID formal-English Gold cohort ran mode=full under frozen candidate f6a-rc1-20260913 (release score 0.8277, 59/59 complete after documented interruption/429 recoveries). Nine preregistered gates failed (per the R1-corrected matrix) — final_evidence_recall 0.8129, critical_final_evidence_recall 0.8231, expected_status_accuracy 0.8644, required_source_coverage_answered 0.9388, paper_code_dual_source_rate 0.0 (single dual-source-required case g060), answer_point_coverage 0.8446, critical_answer_point_miss_count 18, contradiction_count 4, major_unsupported_claim_count 1 — driven by a consistent erroneous-refusal pattern (six Gold-answered cases refused; four claiming "not defined in the locked corpus" against contrary evidence; two version-conflict mishandlings). The FAIL was frozen before exposing further cohorts. F6-B LOCKED. Usage: 383 calls / 3,348,432 tokens. Report: `evaluation/F6_A_PRERELEASE_VALIDATION_AND_GENERALIZATION_GATE.md`.
- **F6-A-R1-R1 outcome (archival/gate-helper consistency repair):** COMPLETE / PASS /
  R1_ARCHIVAL_AND_GATE_HELPER_CONSISTENCY_REPAIRED. Zero-model-call repair: R1 Markdown per-intent counts
  corrected to the authoritative values (2/8/15/12/2/6/14 = 59), the dual-source applicable case ID (g060)
  recorded, gate-helper semantics hardened (missing measurements INCOMPLETE, never PASS; intent-accuracy's own
  denominator; per-intent details with every represented intent visible; failed vs incomplete counts separate),
  and the authoritative matrix is now `evaluation/f6a_gold_gate_matrix_r1_r1.json` (failed_gate_count = 9,
  incomplete = 0, terminal F6-A FAIL unchanged). F6-A-R1 fully accepted after R1-R1. Report:
  `evaluation/F6_A_R1_R1_ARCHIVAL_AND_GATE_HELPER_CONSISTENCY_REPAIR.md`.
- **F6-A-R1-R1-R1 outcome (per-intent denominator emission repair):** COMPLETE / PASS /
  PER_INTENT_INTENT_ACCURACY_DENOMINATOR_EMISSION_REPAIRED. Zero-model-call machine-readable consistency repair;
  R1-R1 remains substantively accepted and only its machine-readable denominator emission is repaired. The
  per-intent intent-accuracy details now emit measurement-derived `applicable_denominator` values (canonical
  measurement rule: metric_applicability override + non-None intent_correct; never hard-coded counts, never
  unconditionally case_count) — current values 2/8/15/12/2/6/14 with metric values and PASS states unchanged;
  zero measurable cases stay INCOMPLETE. Successor matrix `evaluation/f6a_gold_gate_matrix_r1_r1_r1.json`
  (R1-R1 matrix preserved) self-verifies against the prior matrix (any gate divergence except the repaired
  field refuses to write): failed_gate_count = 9 (identical list), incomplete = 0, dual-source applicable IDs
  [g060], terminal verdict effect NO_CHANGE. The reconciliation chain is closed. Report:
  `evaluation/F6_A_R1_R1_R1_PER_INTENT_DENOMINATOR_EMISSION_REPAIR.md`.
- **F6-A-R1 outcome (offline gate/identity/archival reconciliation):** COMPLETE / PASS /
  OFFLINE_GATE_IDENTITY_ARCHIVAL_RECONCILED. Zero-model-call correction of the derived F6-A gate arithmetic:
  dual-source denominator corrected (1 applicable case; rate 0.0; FAIL unchanged), per-intent gates evaluated
  truly per intent (minima 0.9583/0.9286; PASS), identifier hallucination denominator corrected to total
  identifier mentions (121; PASS; upper-bound direction bug fixed), corrected failed-gate count = 9, the
  case-level inspection archival statement corrected, superseded 9/120 usage separately totaled (61 calls /
  339,150 tokens), the broad candidate-verification whitelist removed (strict source identity), and the identity
  chronology audit confirmed a single product behavior identity for all 59 records. The F6-A terminal FAIL is
  preserved; original F6-A artifacts remain byte-unchanged. Report:
  `evaluation/F6_A_R1_OFFLINE_GATE_IDENTITY_ARCHIVAL_RECONCILIATION.md`.

At release, Generalization Gap means benchmark score minus novel score. Benchmark Dependency is the score difference between full compatibility behavior and the approved generic/shortcut-ablation configuration. Neither measurement is authorized here.

## Cross-phase unresolved planning questions

1. **Residual query-expansion impact:** Is residual query-expansion dependency still a material generalization bottleneck in production after the D4-A10 activation?
2. **Remaining D4 candidate disposition:** Does the remaining unassessed D4 inventory contain another naturally testable, high-value migration batch, or should residual entries remain on HOLD?
3. **Phase-F scope boundary:** F1 has established the bounded non-D4 residual inventory and candidate owners. Which candidates warrant a separately authorized treatment remains undecided.
4. **Bottleneck prioritization:** Is answer completeness and decomposition (Phase E) now a larger production bottleneck than residual retrieval shortcut dependency?
5. **Phase execution ordering:** F1 found zero E1 blockers. E1-R2 passed targeted prospective synthetic validation and E1-C1 passed exposed real-style confirmation, including the original atomicity sentinel. E1 is closed under the accepted scope decision. E2-A3 remains FAIL/Q7. E2-A3-FR1 completed with REPAIR_JUSTIFIED. R1 remains FAIL/P2_P6. R2 repaired citation eligibility and passed S1-S13/P1-P11 in six fresh pairs. Historical P6 FAIL remains without waiver or product tuning; historical R3 remains INCONCLUSIVE after four infrastructure failures. R3-R1 completed the missing paired evidence and failed G11 at 2/14 noncritical worse; FR1 subsequently completed a static review recommending shared claim sanitization repair and prospective gate redesign. E2-LR1 subsequently separates completed core mechanisms from deferred promotion and supersedes immediate A3-R4. QA-M1 maintenance subsequently completed with focused T0/static checks. E3-A0 architecture contract is complete; E3-A1 implemented the experimental mechanism under runtime_e1_v2; E3-A2 completed INCONCLUSIVE with insufficient natural applicability; E3-LR1 closed E3 as a bounded low-frequency fallback with standalone recovery benefit unresolved. No further E1 confirmation is required.

```text
CURRENT_TASK = F6-A ATTEMPT 4 / COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
ATTEMPT_4_STATUS = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
FROZEN_PRODUCT_REFERENCE_HEAD = d323f790655c62e18b782d606a02f593a673f3cd
NEW_CANDIDATE_DEVELOPMENT_HEAD = d3a1b274b2784399a7dc51b094a17e466d208b50
INFRASTRUCTURE_ACCEPTANCE_STATUS = PASS
INFRASTRUCTURE_TEST_COUNTS = 112 passed, 18 subtests passed
INFRA_COMMIT = 74af96ae7d2ce18e44c6c9e6e7d1ad93d593fdd0
ATTEMPT_4_SCIENTIFIC_USAGE = 388 calls / 3,647,993 tokens
NEXT_TASK_RECOMMENDATION = POST-ATTEMPT-4 EXPOSED FAILURE REVIEW
NEXT_TASK_EXECUTION_AUTHORIZED = false
FOLLOWING_ARCHITECTURE_TASK = F6-B — Protected Blind Release Gate (LOCKED / F6_A_DID_NOT_PASS)
NEXT_STAGE_AUTHORIZED = false
```


### Post-A3 residual completeness and Gold governance reconciliation

- **Outcome:** COMPLETE / PASS / PRODUCT_REPAIR_DEFERRED_GOLD_GOVERNANCE_RECONCILED.
- **Product:** Stored g022/g023/g013 evidence showed distinct loss mechanisms and no safe shared generic repair. Product behavior remains at d3a1b274b2784399a7dc51b094a17e466d208b50; verifier faithfulness, safe salvage, and F2-A3-R1 coverage ownership remain unchanged.
- **Governance:** g011, g044, and g115 remain unchanged. Forward-only m6-benchmark-v2.10 corrects only g060 by retiring the non-question-grounded paper group/obligation while preserving code groups and all answer points. Calibration v7 mechanically preserves the 59/21 product-language membership.
- **Boundary:** Gold v2.9 remains Attempt-3 historical authority; no rescore, scientific calls, protected cohort access, candidate freeze, or Attempt-4 execution occurred.
- **Successor:** F6-A Attempt 4 completed `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`; see `evaluation/F6_A4_PRERELEASE_VALIDATION_RESULT.md`. The next recommendation is a separately authorized post-Attempt-4 exposed failure review.
- **Report:** evaluation/POST_A3_RESIDUAL_COMPLETENESS_AND_GOLD_GOVERNANCE.md.
