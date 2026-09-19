# PANDA QA Agent — Evaluation Status

This file records current authoritative evaluation and production state.

Stable evaluation policy:
docs/EVALUATION_POLICY.md

Long-term architecture and future planning:
docs/GENERALIZATION_ROADMAP.md

Detailed scientific experiments, preregistrations, repairs, raw artifacts, and incident history:
evaluation/

The single `Current authoritative state` section is authoritative over historical checkpoint prose.

---

## Current authoritative state

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
DEDICATED_E3_REVALIDATION = NOT_PLANNED / LOW_NATURAL_APPLICABILITY_AND_LOW_DECISION_VALUE.
FUTURE_E3_EVIDENCE = ACCUMULATE_OPPORTUNISTICALLY_IN_BROADER_AUTHORIZED_EVALUATIONS.
E2-A3-R4 = NOT_STARTED / SUPERSEDED_BY_LIFECYCLE_SIMPLIFICATION.
E2 DEFAULT PROMOTION = DEFERRED / ACTIVATION_ACCEPTANCE_NOT_MET.
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY.
E2 DEFAULT-PROMOTION GATE REDESIGN = CLOSED / NO_IMMEDIATE_REVALIDATION_DEFINED / REOPEN_ONLY_FOR_PROMOTION_RELEVANT_MATERIAL_CANDIDATE_OR_RELEASE_BOUNDARY.
DEFAULT_PROMOTION_RECONSIDERATION_TRIGGER = a promotion-relevant materially behavior-changing post-Phase-E candidate that either (1) materially affects the unresolved default-promotion failure surface (completeness, verification, compatibility, evidence-selection, or other behavior implicated in the failed activation lineage — normally Phase-F cleanup of F1-R08/R09/R11, R13, R10, R14, R04) or (2) otherwise creates a decision-relevant new integrated runtime candidate whose default acceptance needs assessment; OR (3) an explicitly authorized release/acceptance candidate evaluation requiring the normal-default decision.
Reconciliation: `evaluation/E2_POST_A3_LIFECYCLE_RECONCILIATION.md`.
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
F3 = COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED.
F3 report: `evaluation/F3_FIXED_LOCATOR_FALLBACK_CLEANUP.md`.
F4 = COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED (final closure achieved only after F4-R1).
F4 report: `evaluation/F4_GENERATION_VERIFICATION_ROLE_SEPARATION.md` (initial closeout corrected by F4-R1).
F4-R1 = COMPLETE / PASS / PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTED.
F4-R1 report: `evaluation/F4_R1_PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTION.md`.
F5 = COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED (final closure achieved only after F5-R1).
F5 report: `evaluation/F5_BOUNDED_ANSWER_COMPOSER.md` (initial closeout corrected by F5-R1; READABILITY_BENEFIT = NOT_EMPIRICALLY_EVALUATED_IN_F5).
F5-R1 = COMPLETE / PASS / EXACT_LITERAL_IDENTIFIER_PROVENANCE_BOUNDARY_ESTABLISHED.
F5-R1 report: `evaluation/F5_R1_EXACT_LITERAL_IDENTIFIER_PROVENANCE_REPAIR.md`.
F6 = staged release gate reconciled by F6-LR1 (attempt 1 = HISTORICAL / HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET / ZERO_OUTCOME).
F6-LR1 = COMPLETE / PASS / RELEASE_GATE_STAGING_RECONCILED.
F6-LR1 record: `evaluation/F6_LR1_RELEASE_GATE_STAGING_RECONCILIATION.md` (companion `evaluation/f6_lr1_release_gate_staging_reconciliation.json`).
F6-A Attempt 1 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.6, historical; record: `evaluation/F6_A_PRERELEASE_VALIDATION_AND_GENERALIZATION_GATE.md`).
F6-A Attempt 2 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.6, historical; record: `evaluation/F6_A2_PRERELEASE_VALIDATION_RESULT.md`).
F6-A Attempt 3 Preflight = HISTORICAL / HOLD / PRE_RELEASE_PRECONDITION_NOT_MET (zero-outcome preflight hold; unblocked by GOLD-9).
GOLD-9 = COMPLETE / PASS / RELEASE_AUTHORITY_CHAIN_RECONCILED (commit `1f03bbd`).
F6-A Attempt 3 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED.
F6-A Attempt 3 record: `evaluation/F6_A3_PRERELEASE_VALIDATION_RESULT.md` (result JSON `evaluation/f6_a3_prerelease_validation_result.json`, receipt `evaluation/f6_a3_a1_receipt.json`, gate matrix `evaluation/f6_a3_gate_matrix.json`, closeout addendum `evaluation/f6_a3_closeout_verification.json`).
F6-A Attempt 4 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.10; 59/59 complete after two retryable `g112` recoveries; failed `critical_final_evidence_recall` and `critical_answer_point_miss_count`; release score 0.971751; 388 calls / 3,647,993 tokens; A2-A5 NOT_REACHED; `novel_validation` pristine).
F6-A Attempt 4 record: `evaluation/F6_A4_PRERELEASE_VALIDATION_RESULT.md` (result JSON `evaluation/f6_a4_prerelease_validation_result.json`, stage receipt `evaluation/f6_a4_a1_stage_receipt.json`, authoritative gate matrix `evaluation/f6_a4_gate_matrix.json`, gate receipt `evaluation/f6_a4_gate_matrix_receipt.json`).
GENERIC ANSWER-OBLIGATION COMPLETENESS = PRODUCT CHANGE ACCEPTED / MATERIAL (development HEAD `eda7d932a9b1b7b65436cba01e247859a6f9e056`; record `evaluation/GENERIC_ANSWER_OBLIGATION_COMPLETENESS_DEVELOPMENT.md`).
NORMAL PRODUCT MODE = `production_answer_obligations_v1` (raw question → QuestionDecomposer → 1–5 question-only semantic obligations → generation with authoritative answer points → support + coverage verification → at most one bounded evidence-backed revision → final verification/coverage audit; E3 missing-point retrieval, candidate capture, cross-pass global reselection, and the retained-support ledger are not promoted).
R1 DECOMPOSITION PROMPT RELEASE IDENTITY REPAIR = COMPLETE / PASS / DECOMPOSITION_PROMPT_RELEASE_IDENTITY_REPAIRED (HEAD `8f61aee414aa9fa2da0e3a6bbb2f767eadb7da4c`; identity/provenance-only; canonical `prompt_fingerprint()` = `35f1dd3cbcd6cb636e2e92e7af28cb95415787e8d920c99c3b070eae86a8f097`; record `evaluation/GENERIC_ANSWER_OBLIGATION_COMPLETENESS_R1_RELEASE_IDENTITY_REPAIR.md`).
F6 FORMAL REPEAT POLICY = ESTABLISHED (`SAME_PRODUCT_LINEAGE_FORMAL_REPEAT = PROHIBITED`; `evaluation/F6_FORMAL_REPEAT_POLICY.md`).
F6-A Attempt 5 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.10 under the materially new `production_answer_obligations_v1` candidate f6a-rc5-20260919; 59/59 complete after one resume recovering ten retryable transport exceptions; failed `critical_final_evidence_recall` 0.918367, `identifier_hallucination_rate` 0.046154, and `critical_answer_point_miss_count` 4 (`g013.p3`, `g023.p3`, `g039.p1`, `g047.p1`); release score 0.949153; 563 calls / 3,201,331 tokens; A2-A5 NOT_REACHED; `novel_validation` pristine).
F6-A Attempt 5 record: `evaluation/F6_A5_PRERELEASE_VALIDATION_RESULT.md` (result JSON `evaluation/f6_a5_prerelease_validation_result.json`, stage receipt `evaluation/f6_a5_a1_stage_receipt.json`, authoritative gate matrix `evaluation/f6_a5_gate_matrix.json`, gate receipt `evaluation/f6_a5_gate_matrix_receipt.json`).
POST-ATTEMPT-5 FAILURE OWNERSHIP & GATE VALIDITY REVIEW = COMPLETE / PASS / FAILURE_OWNERSHIP_AND_GATE_VALIDITY_ESTABLISHED (zero scientific calls).
Review findings: the QuestionDecomposer under-splitting hypothesis is REJECTED for all four critical answer-point misses (g013/g023/g047 = A1 obligation-content gaps; g039.p1 = Gold rubric clause beyond the literal question); five of six critical final-evidence misses are content-equivalent alternate-source citations against literal pinned groups (the same literalness handled by 17 signed final_evidence_equivalence adjudications in v2.5/v2.6, absent in v2.9/v2.10) while g011 is a genuine R2 rerank loss plus a V2 corpus-negative false acceptance; all six identifier "hallucinations" (g060 ×2, g113 ×4) are evaluator false positives — the symbols are verbatim corpus enum members invisible to build_identifier_catalog (locator.symbol + class/struct/enum type names only). Gate dispositions: critical_final_evidence_recall REDEFINE_METRIC_REQUIRED, critical_answer_point_miss_count GOLD_RECONCILIATION_REQUIRED, identifier_hallucination_rate EVALUATOR_REPAIR_REQUIRED. All 18 thresholds are INHERITED_HISTORICAL_CONSTANT (frozen M6 hidden-acceptance constants from the root commit; no derivation recorded). critical_answer_point_miss_count is a completeness/quality criterion misclassified inside hard_safety_invariants. ATTEMPT_6_READINESS = NOT_READY. Review: `evaluation/POST_A5_FAILURE_OWNERSHIP_AND_GATE_VALIDITY_REVIEW.md` (companion JSON `evaluation/post_a5_failure_ownership_and_gate_validity_review.json`). A forward-only causal-attribution erratum is appended in review §16: generator self-declared answer-point mappings are NOT ESTABLISHED AS THE CAUSAL COMPLETENESS AUTHORITY; g013.p3 = A1 bounded-revision recovery insufficiency; g023.p3/g047.p1 = A1 answer-content omission with possible V2 semantic-coverage false acceptance.
IDENTIFIER CATALOG EVALUATOR REPAIR + ATTEMPTS 1–5 OFFLINE IDENTIFIER RESCORE = COMPLETE / PASS / IDENTIFIER_EVALUATOR_REPAIRED_AND_HISTORY_RESCORED (zero scientific calls; generic T1–T8 RED→GREEN suite plus production-corpus Attempt-5 regression; `build_identifier_catalog` now harvests qualified scoped identifiers verbatim from allowed locked-corpus text with namespace-head-guarded tail fallback; namespace spoof protected; exists/support separation preserved; allowed-version boundary preserved). Offline rescore (raw repaired-evaluator deterministic values, denominators reproduce the historical matrices exactly, zero events introduced): Attempt 1 v2.6 0/121→0/121; Attempt 2 v2.6 0/155→0/155; Attempt 3 v2.9 0/177→0/177 (58/59 stored, g013 historically missing); Attempt 4 v2.10 2/173→0/173 (g060 ×2 cleared); Attempt 5 v2.10 6/130→0/130 (g060 ×2, g113 ×4 cleared; review's 6/130→0/130 prediction verified mechanically). Counterfactual identifier gate PASS for Attempt 5 is COUNTERFACTUAL / NON-AUTHORITATIVE; all five terminal verdicts unchanged; `MATERIAL_PRODUCT_CHANGE = false`, `EVALUATOR_CONTRACT_CHANGE = true`; `ATTEMPT_6_READINESS = NOT_READY`. Record: `evaluation/IDENTIFIER_CATALOG_EVALUATOR_REPAIR_AND_OFFLINE_RESCORE.md` (rescore artifacts `evaluation/identifier_catalog_evaluator_repair/`, summary JSON `evaluation/identifier_catalog_evaluator_repair_and_offline_rescore.json`). Identifier metrics and count terminology superseded by R1 below.
IDENTIFIER EVALUATOR R1 — QUALIFIED-SYMBOL EXACT-OWNERSHIP BOUNDARY + RESCORE PROVENANCE RECONCILIATION = COMPLETE / PASS / QUALIFIED_SYMBOL_OWNERSHIP_AND_RESCORE_PROVENANCE_RECONCILED (zero scientific calls). R1 tightened `_qualified_symbol_exists` to exact-ownership semantics: a qualified identifier exists only when that exact qualified form is established by allowed locked-corpus evidence; the known-head + unrelated-known-tail combinatorial fallback was removed (RED: R1-T1 demonstrated `ExampleNS::VALUE_A` legitimized from known head `ExampleNS` + bare tail `VALUE_A`; GREEN: 14/14 including nested literals, wrong member/owner rejection, namespace spoof, version boundary, exists/support separation, and the production Attempt-5 regression). R1 rescore re-derived identical denominators (121/155/177/173/130) with zero introduced events, proving the fallback was never load-bearing for a real identifier; all six Attempt-5 false positives remain cleared (0/130). Provenance reconciled from the immutable stores: Attempt 1 = 60 raw rows / 59 unique cases (one complete duplicate `g119` execution, append-only recovery residue; g119's expected_status is insufficient_evidence so neither duplicated row is applicable to the identifier metric and neither contributes mentions — the denominator 121 is the identifier-mention total over the 49 applicable answered records, reproduced exactly); Attempt 3 = 59 raw rows / 59 unique cases with preserved `g013` Vertex-429 exception row (completed/scored 58; g013 is not a valid applicable identifier measurement record and contributes no identifier measurement; the denominator 177 is the mention total over the 49 applicable answered cases, of which 48 carry an actual measurement); Attempts 2/4/5 clean 59/59 with 49 applicable answered cases each. Forward-only rescore artifacts reissued as `identifier-rescore-r1-v1` superseding `identifier-rescore-v1` count terminology. `MATERIAL_PRODUCT_CHANGE = false`, `EVALUATOR_CONTRACT_CHANGE = true`; all five terminal verdicts unchanged; `ATTEMPT_6_READINESS = NOT_READY`. Record: `evaluation/IDENTIFIER_CATALOG_EVALUATOR_R1_EXACT_OWNERSHIP_AND_PROVENANCE.md` (companion JSON `evaluation/identifier_catalog_evaluator_r1_exact_ownership_and_provenance.json`). Identifier provenance schema finalized: `identifier_gold_applicable_case_count` (Gold answered semantics, 49 per attempt) and `identifier_measured_record_count` (49 per attempt; 48 for Attempt 3, whose g013 is Gold-applicable but unmeasured) are separated, the legacy `identifier_applicable_case_count` field is removed from active artifacts, and `IDENTIFIER PROVENANCE SCHEMA = COMPLETE / PASS / GOLD_APPLICABILITY_AND_MEASUREMENT_SEPARATED`.
F6-B = LOCKED / F6_A_DID_NOT_PASS.
POST-ATTEMPT-3 FAILURE & EXECUTION-RECOVERY REVIEW = COMPLETE / PASS / FAILURES_CLASSIFIED_RECOVERY_INFRASTRUCTURE_REPAIRED_PRODUCT_RESIDUALS_DEFERRED.
POST-ATTEMPT-3 review: `evaluation/POST_A3_FAILURE_AND_EXECUTION_RECOVERY_REVIEW.md` (companion JSON `evaluation/post_a3_failure_and_execution_recovery_review.json`).
Phase E = COMPLETE / CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED / DEFAULT_PROMOTION_DEFERRED.
E2-A1 report: `evaluation/E2_A1_SHADOW_ANSWER_POINT_COVERAGE_CONTRACT.md`.
C1 met all eight strict gates and the original pair09 atomicity sentinel. Per the
accepted closure decision, E1 is complete. E2-A2 passed targeted shadow validation. E2-A3 failed Q7; normal QA remains legacy. E3-A0 established the missing-point targeted retrieval architecture contract; E3-A1 implemented the experimental mechanism under runtime_e1_v2. E3-A2 completed INCONCLUSIVE: on the frozen 11-case cohort only 1 case (n006, 2 missing points) was naturally E3-applicable, below the G2 threshold (>=4 cases, >=4 points); the single applicable pair was descriptive only (no recovered point on either arm; treatment moved one point absent→partial and was preferred by the blinded judge within all safety/bounds gates). E3-LR1 subsequently reconciled the E3 lifecycle (static, zero scientific calls): E3 closes as a bounded low-frequency experimental fallback with standalone recovery benefit unresolved; dedicated revalidation is not planned; future E3 evidence accumulates opportunistically in broader authorized evaluations. PE-LR1 subsequently closed Phase E at the promotion boundary: architecture complete, normal default remains legacy_question_core, promotion deferred until a material candidate change or an explicitly authorized release-boundary decision; the E2 gate-redesign deferral is retired (closed, reopen only under the recorded trigger).
Decision: `evaluation/E1_CLOSURE_SCOPE_REVIEW.md`.
Report: `evaluation/E1_C1_REAL_STYLE_CONFIRMATION.md`.
Preregistration: `2517b691245c38175222064e6ca546d06fd21e9a`.
Raw freeze: `7eab1e8fe099fed6ff06384c4fa0eb48dcf52677`.


Repository head (E2-A3 starting baseline):
ffedb2117f578515ea9d74eca92105956b8a3dcb

Latest completed prospective validation:
E1-R2 — Prospective Semantic Answer-Point Revalidation
COMPLETE / PASS / TARGETED_PROSPECTIVE_SEMANTIC_ANSWER_POINT_REVALIDATION_PASSED
Preregistration: 3d0d8ca650d159681fecec324a081d28e8e945eb
Raw freeze: a5275dfee6c4134f3ad790a5598ca0c0a51f1a58

Latest completed shadow repair:
E1-R1
COMPLETE / PASS / SHADOW_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIRED

Latest completed architecture review:
E1-AR
COMPLETE / PASS / REVISED_SEMANTIC_ANSWER_POINT_CONTRACT_ESTABLISHED

Historical decomposition validation:
E1-A2
COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED
Preregistration commit: 77ea6bc27beb1657673e57be763b05419c98bc05

Latest completed diagnostic implementation:
E1-A1
COMPLETE / PASS / QUESTION_ONLY_DIAGNOSTIC_DECOMPOSITION_IMPLEMENTED

Latest completed static inventory:
F1
COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED

Latest completed Phase-F scope reconciliation:
PF-LR1
COMPLETE / PASS / PHASE_F_SCOPE_RECONCILED_BOUNDED_CLEANUP_PLAN_ESTABLISHED

Latest completed Phase-F production cleanup:
F2-A1
COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED
F2-A1-R1
COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED
F2-A2
COMPLETE / PASS / QUESTION_DERIVED_POINTER_NORMALIZATION_COMPLETENESS_ESTABLISHED
F2-A3
COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED
F2-A3-R1
COMPLETE / PASS / COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REMOVED
F2-A4
COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED
F2-A4-R1
COMPLETE / PASS / QUESTION_GROUNDED_PREMISE_REFUSAL_BOUNDARY_ESTABLISHED
F2-A5
COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED
F2-A5-R1
COMPLETE / PASS / SOURCE_OBLIGATION_MATCHING_BOUNDARY_ESTABLISHED
F3
COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED
F4
COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED
F4-R1
COMPLETE / PASS / PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTED
F5
COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED
F5-R1
COMPLETE / PASS / EXACT_LITERAL_IDENTIFIER_PROVENANCE_BOUNDARY_ESTABLISHED
F6
HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET (attempt 1, HISTORICAL)
F6-LR1
COMPLETE / PASS / RELEASE_GATE_STAGING_RECONCILED

Latest accepted production action:
D4-A10
COMPLETE / PASS /
VALIDATED_MODEL_FACTORY_LOCATOR_RETIREMENT_ACTIVATED

Latest accepted scientific authority relevant to that activation:
D4-A9-R2
COMPLETE / PASS /
LEVEL 6 / PARTIAL /
MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD

Current planning state:
D4 = PAUSED / ROADMAP_RECONCILIATION
D4 overall completion = UNDECIDED
CURRENT_TASK = POST-A5 GENERIC PRODUCT REPAIR / COMPLETE / PASS / COMPLETENESS_RECOVERY_AND_NEGATIVE_EXISTENCE_CONTRACTS_STRENGTHENED
GENERIC_PRODUCT_REPAIR = IMPLEMENTED / DETERMINISTICALLY VERIFIED / SCIENTIFIC EFFECT NOT YET EVALUATED (zero scientific calls; bounded-revision recovery: revised claims with genuinely new content survive local-ID collisions under fresh IDs while identical-unsupported restatement stays blocked and the one-revision bound is intact; coverage review schema now requires a per-runtime-point completeness record {answer_point_id, supporting_claim_ids, complete} with deterministic validation, keeping generator mappings non-authoritative; generation and verification contracts forbid corpus-wide absence inferred from a non-exhaustive evidence subset while deterministic exact-absence refusal paths stay authoritative; rerank role preservation DEFERRED — rerank_pool=fused_order[:30] investigated, no safe generic repair established, E3 not promoted; prompt fingerprint changed automatically to 0a5b2909ef586671d533148979fc681c64e37528ad53781a4566cb9044835ba2 with release-identity tests passing; MATERIAL_PRODUCT_CHANGE = true; focused deterministic tests: T0 suite 12/12 (RED 4/8 before), qa 210, focused regressions 336 with only the recorded pre-existing stale assertions failing). Product-behavior HEAD = `e79d3232ed132a224cbceaf3524e19a1406bd648` (exact SHA; docs-only descendants are not the product head). Causal attribution reconciled by R1: the generic ID-collision defect is CONFIRMED from code/T0, but the exact g013 historical causality is NOT_ESTABLISHED_FROM_FROZEN_TRACE; the coverage repair is a structural strengthening (FALSE_ACCEPTANCE_MITIGATION = IMPLEMENTED, RUNTIME_SEMANTIC_EFFECT = NOT_YET_SCIENTIFICALLY_VALIDATED, g023/g047 exact causality NOT_ESTABLISHED); negative-existence contract gap CONFIRMED and repaired with RUNTIME_SCIENTIFIC_EFFECT = NOT_YET_EVALUATED; rerank role preservation remains DEFERRED. Record: `evaluation/POST_A5_GENERIC_PRODUCT_REPAIR.md` (companion JSON `evaluation/post_a5_generic_product_repair.json`) with R1 `evaluation/POST_A5_GENERIC_PRODUCT_REPAIR_R1_CAUSAL_ATTRIBUTION_AND_LINEAGE_RECONCILIATION.md` (companion JSON `evaluation/post_a5_generic_product_repair_r1_causal_attribution_and_lineage_reconciliation.json`).
ACTIVE_GOLD = m6-benchmark-v2.11 (evaluation/benchmarks/v2_11/gold_questions.yaml, SHA 39943c6a3f2152e476109c0340acd066795c8de6ff3b6bb2eac6661ac480a417; parent v2.10 byte-identical)
ACTIVE_CALIBRATION = phase_b_t3_product_language_scope_v8 (compatible; formal-English 59 / non-English 21 unchanged; selector SHA e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5 unchanged)
F6_A_EVALUATION_CONTRACT_RECONCILIATION = COMPLETE / PASS / EVIDENCE_ROLE_GOLD_AND_GATE_CLASSIFICATION_RECONCILED (zero scientific calls; critical-evidence construct = required evidence roles with explicitly reviewed any_of equivalence, evaluator matching unchanged, threshold 1.00 unchanged; successor Gold v2.11 changes exactly 6 objects — g039 p1 literal-scope correction plus audited role/any_of equivalence for g013/g016/g020/g044/g110, g044.e1 role renamed angular_acceptance_thesis_theory, g011 deliberately unchanged as negative control; Attempt-5 counterfactual crit-ev 0.918367 -> 48/49 = 0.979592 still FAIL and g011 stays 0.0; g039 governance adjudication counterfactual drops critical point misses to 3, still FAIL; identifier counterfactual 0/130 PASS; all formal verdicts unchanged; hard-safety vs strict-release-quality gate categories separated for future contracts with thresholds unchanged; NUMERICAL_THRESHOLD_CHANGES = NONE; `MATERIAL_PRODUCT_CHANGE = false`, `EVALUATION_CONTRACT_CHANGE = true`, `GOLD_SUCCESSOR_CREATED = true`). One evaluator correctness-only exception: the identifier-catalog cache received an object-identity check (no metric change). Record: `evaluation/F6_A_EVALUATION_CONTRACT_RECONCILIATION.md` (companion JSON `evaluation/f6_a_evaluation_contract_reconciliation.json`).
PREVIOUS_PRODUCT_BEHAVIOR_LINEAGE_HEAD = eda7d932a9b1b7b65436cba01e247859a6f9e056
CURRENT_PRODUCT_BEHAVIOR_LINEAGE_HEAD = e79d3232ed132a224cbceaf3524e19a1406bd648
R1_RELEASE_IDENTITY_HEAD = 8f61aee414aa9fa2da0e3a6bbb2f767eadb7da4c
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
NEXT_TASK_RECOMMENDATION = POST-A5 PRODUCT REPAIR VALIDATION / FIXED EXPOSED SENTINEL T1 (NO ATTEMPT 6)
NEXT_TASK_EXECUTION_AUTHORIZED = false
FOLLOWING_ARCHITECTURE_TASK = F6-B — Protected Blind Release Gate (LOCKED / F6_A_DID_NOT_PASS)

No D4-A11 exists.
Phase E = COMPLETE / CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED / DEFAULT_PROMOTION_DEFERRED.
E1 = COMPLETE / PASS / QUESTION_ONLY_SEMANTIC_ANSWER_POINT_DECOMPOSITION_VALIDATED.
E2 = COMPLETE / CORE_MECHANISM_VALIDATED / DEFAULT_PROMOTION_DEFERRED.
E3-A0 = COMPLETE / PASS / MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT_ESTABLISHED.
E3-A1 = COMPLETE / PASS / EXPERIMENTAL_MISSING_POINT_TARGETED_RETRIEVAL_IMPLEMENTED.
E3-A2 = COMPLETE / INCONCLUSIVE / INSUFFICIENT_NATURAL_MISSING_POINT_APPLICABILITY.
E3-LR1 = COMPLETE / PASS / POST_A2_LIFECYCLE_RECONCILED.
E3 = COMPLETE / BOUNDED_LOW_FREQUENCY_FALLBACK_IMPLEMENTED / SCIENTIFIC_RECOVERY_BENEFIT_UNRESOLVED.
PE-LR1 = COMPLETE / PASS / PHASE_E_CLOSED_PROMOTION_DEFERRED_UNTIL_MATERIAL_CANDIDATE.
Phase E = COMPLETE / CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED / DEFAULT_PROMOTION_DEFERRED.
Phase F = IN_PROGRESS / F6_A_ATTEMPT_4_FAILED.
F2 = COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE.
F3 = COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED.
F4 = COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED.
F4-R1 = COMPLETE / PASS / PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTED.
F5 = COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED.
F5-R1 = COMPLETE / PASS / EXACT_LITERAL_IDENTIFIER_PROVENANCE_BOUNDARY_ESTABLISHED.
F6 attempt 1 = HISTORICAL / HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET / ZERO_OUTCOME (valid under the then-authorized protocol).
F6-LR1 = COMPLETE / PASS / RELEASE_GATE_STAGING_RECONCILED (static reconciliation: holdout governance/metadata integrity is the F6-A precondition; physical package availability is the F6-B precondition only).
F6-A Attempt 1 (historical) = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED. Selector-defined formal-English Gold cohort (59 IDs, calibration v3 reconciliation) executed mode=full under frozen candidate f6a-rc1-20260913 after zero-outcome Stage A0. Release score 0.8277 (59/59 complete). Ten preregistered gates failed: final_evidence_recall 0.8129 (<0.90), critical_final_evidence_recall 0.8231 (==1.00), expected_status_accuracy 0.8644 (<0.975), required_source_coverage_answered 0.9388 (<0.97), paper_code_dual_source_rate 0.1633 (==1.00), answer_point_coverage 0.8446 (<0.90), critical_answer_point_miss_count 18 (==0), contradiction_count 4 (==0), major_unsupported_claim_count 1 (==0). Passing: gold_recall_at_10 0.9898, intent_accuracy 0.9831, citation_integrity 1.00, wrong/forbidden evidence 0, identifier_hallucination_rate 0.00, unhandled exceptions 0. Failure pattern: six erroneous insufficient-evidence refusals on Gold-answered questions (four asserting "not defined in the locked corpus" against cited contrary evidence — g005/g013/g034/g059) plus two version-conflict handling errors (g012/g026). Fail-fast froze the FAIL before ablation/novel_dev/novel_validation/composer-audit exposure; novel_validation remains PRISTINE_FOR_CURRENT_LINEAGE. Infrastructure incidents (three external process terminations, two Vertex 429 quota failures retried after recovery) recovered under the same frozen identity; usage: 383 scientific/evaluation calls, 3,348,432 tokens. Report: `evaluation/F6_A_PRERELEASE_VALIDATION_AND_GENERALIZATION_GATE.md`.
F6-A Attempt 2 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Gold v2.6, historical; candidate f6a-rc2-20260913; release score 0.9463; 6 failed gates; report: `evaluation/F6_A2_PRERELEASE_VALIDATION_RESULT.md`).
F6-A Attempt 3 Preflight = HISTORICAL / HOLD / PRE_RELEASE_PRECONDITION_NOT_MET (zero-outcome preflight hold: candidate freezer bound v2.6 and calibration loader stopped at v3; unblocked by GOLD-9; preserved at `50f0c4b:evaluation/F6_A3_PRERELEASE_VALIDATION_RESULT.md`).
GOLD-9 = COMPLETE / PASS / RELEASE_AUTHORITY_CHAIN_RECONCILED (commit `1f03bbd`; candidate freezer bound to Gold v2.9; calibration loader successor chain extended to v6).
F6-A Attempt 3 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED. Formal-English Gold v2.9 cohort (59 expected, 58 scored, 1 unhandled exception g013 due to Vertex 429 RESOURCE_EXHAUSTED) executed under frozen candidate f6a-rc3-20260914 (manifest SHA be2101a4..). Release score 0.9741 (58-case diagnostic only; full-cohort release score INCOMPLETE). Four mandatory gates failed: critical_final_evidence_recall 0.9410 (<1.00; failing: g011, g022, g044, g060), critical_answer_point_miss_count 3 (>0; failing: g022, g023, g115), paper_code_dual_source_rate 0.0 (<1.00; failing: g060), unhandled_exception_count 1 (>0; g013 Vertex 429). Passing gates: gold_recall_at_10 0.9792, final_evidence_recall 0.9306, intent_accuracy 0.9828, per_intent_gold_recall_at_10 (min 0.9500), per_intent_intent_accuracy (min 0.9231), expected_status_accuracy 1.00, citation_integrity 1.00, wrong_version_evidence 0, forbidden_evidence 0, required_source_coverage_answered 0.9792, identifier_hallucination_rate 0.00, answer_point_coverage 0.9741, contradiction_count 0, major_unsupported_claim_count 0. Raw canonical matrix evaluated 14 PASS, 4 FAIL, 0 incomplete flags strictly on available observations; raw flags are diagnostic, not complete-cohort PASS; full cohort measurements are INCOMPLETE due to unmeasured g013. Missing measurements are treated as INCOMPLETE (not FAIL per policy). Hard measured FAIL on evaluated cohort is terminal for the prerelease gate, while missing g013 status is INCOMPLETE separately. Explicit late receipt protocol deviation: late run receipt (`evaluation/f6_a3_a1_receipt.json`) was written after failure case diagnosis was already inspected. Inherited prior execution evidence: A0 focused tests (327 passed + 70 subtests). Fail-fast halted scientific execution immediately; stages A2-A5 NOT_REACHED; novel_validation remains PRISTINE_FOR_CURRENT_LINEAGE; holdout access = 0; F6-B LOCKED. Observed Attempt-3 scientific usage: 397 model calls, 3,783,197 tokens (final 59 records: 387 calls / 3,745,918 tokens; preserved 3 initial 429 failed attempts: 10 calls / 37,279 tokens). Forward-only closeout audit addendum: `evaluation/f6_a3_closeout_verification.json`.
F6-A Attempt 4 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED. Formal-English Gold v2.10 cohort completed 59/59 under candidate f6a-rc4-20260916 after two retryable `g112` recoveries. Release score 0.971751. Mandatory failures: critical_final_evidence_recall 0.928571 and critical_answer_point_miss_count 2 (`g013.p3`, `g037.p1`). All other mandatory gates passed; A2-A5 were not reached; novel_validation remains pristine. Usage: 388 calls / 3,647,993 tokens. Report: `evaluation/F6_A4_PRERELEASE_VALIDATION_RESULT.md`.
F6-A Attempt 5 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED. Formal-English Gold v2.10 cohort completed 59/59 under the materially new `production_answer_obligations_v1` candidate f6a-rc5-20260919 (fresh preregistration commit `eacbf44`, frozen implementation commit `eacbf44`, freeze commit `07124a1`) after one resume operation recovering ten retryable transport exceptions (g001, g017, g018, g026, g029, g031, g040, g105, g108, g115) under the identical frozen identity; successful cases were never rerun and all 69 attempt entries remain in the cumulative ledger. Release score 0.949153. Mandatory failures: critical_final_evidence_recall 0.918367, identifier_hallucination_rate 0.046154 (six major LumiFit identifier hallucinations on g060 and g113), and critical_answer_point_miss_count 4 (`g013.p3`, `g023.p3`, `g039.p1`, `g047.p1`). All other mandatory gates passed, including expected_status_accuracy 1.000000 and unhandled_exception_count 0. A2-A5 were not reached; novel_validation remains pristine. Usage: 563 calls / 3,201,331 tokens (successful attempts 511 / 3,051,535; failed retryable attempts 52 / 149,796; question-decomposition and runtime-verification usage NOT_SEPARATELY_RECOVERABLE_FROM_STORED_RECORDS). Stage receipt sealed and validated before case diagnostics; authoritative gate matrix `a6e40cf9...` with validated receipt. Report: `evaluation/F6_A5_PRERELEASE_VALIDATION_RESULT.md`.
F6-B = LOCKED / F6_A_DID_NOT_PASS.
POST-ATTEMPT-3 FAILURE AND EXECUTION-RECOVERY REVIEW = COMPLETE / PASS / FAILURES_CLASSIFIED_RECOVERY_INFRASTRUCTURE_REPAIRED_PRODUCT_RESIDUALS_DEFERRED.
Post-Attempt-3 review consolidated Stage R0 failure classification, post-terminal diagnostic execution of g013 (`post-a3-g013-recovery-20260915`, 10 calls / 62,370 tokens; Attempt 3 accounting 397 / 3,783,197 immutable), and focused product configuration repair (bare 'particle identification' removed from event_alignment; 84 passed, 42 subtests across query expansions/config/shortcut/retrieval plus QA 210 passed, 25 subtests verified by host; 0 calls / 0 tokens). Protocol deviations PD1 and PD2 remain historical facts. Infrastructure recovery and receipt mechanisms were accepted and then used by Attempt 4. Detailed review and exact trace locators: `evaluation/POST_A3_FAILURE_AND_EXECUTION_RECOVERY_REVIEW.md` (companion JSON `evaluation/post_a3_failure_and_execution_recovery_review.json`).
No further production task is authorized; the next recommendation is a post-Attempt-5 exposed failure review only.

## E3-A1 experimental implementation closeout

COMPLETE / PASS / EXPERIMENTAL_MISSING_POINT_TARGETED_RETRIEVAL_IMPLEMENTED.
Implemented bounded post-verify missing-point targeted retrieval and candidate reconsideration under explicit
`runtime_e1_v2` mode only. Normal default remains `legacy_question_core`; `shadow_e1_v2` unchanged. Trigger
strictly requires all A0 trigger conditions. Targeted collection query uses original question + exact missing point
text(s) in original order; global reranker receives original question only. Original retrieval plan snapshot
preserved without mutation or expanded budgets. Candidate capture uses private opt-in `capture_candidates=True`
with zero duplicate retrieval calls. Cross-pass candidates deduplicated by `object_id` with best channel rank
RRF (`RRF_K=60`, experimental candidate, not validated optimal) and strict payload content validation. Exactly
one global rerank on successful path; zero local targeted reranks; reuses authoritative `_prioritize_and_select_evidence`
(`select_final_evidence`). Atomic bundle update with single try/except exception boundary and honest no-gain fallback.
Retained-support claims ledger protects unchanged supported claims whose cited evidence was displaced; new/modified
claims rejected from citing ledger evidence; normal deterministic integrity checks enforced without waiver.
Final cited evidence appends cited retained support items in deterministic sorted order. Public DTOs and prompts unchanged.
Initial implementation baseline `2af8ac95` verified 42 E3 tests covering T1–T20, Sentinels 1–3 and defect regressions, plus 147 affected neighboring tests (189 passed, 9 subtests passed).
Historical initial implementation review reported PASS; host inspection then identified 8 defect areas resolved by the fix worker, with removal of the `TypeError` retry and test-only agent state confirmed at initial closeout.
Independent post-implementation contract review identified two bounded implementation gaps: (1) structured/supplemental candidate capture and global reconsideration omitted structured-replacement candidates and suffered chronological starvation in saturated candidate pools (>=30), corrected via cross-pass bounded eligible union reservation without fake channel ranks; (2) deterministic requirement evaluation during E3 second verify falsely failed unchanged retained claims whose cited evidence was displaced, corrected via a claim-scoped deterministic valid claim/evidence view strictly preventing new/modified claims from using ledger-only evidence. Corrected final focused verification: 49 E3 tests and 147 neighboring tests; 196 passed, 9 subtests passed. Separate final AGY review PASS; Codex accepted the bounded corrections after inspecting the source/test diffs. All PANDA scientific/evaluation calls and tokens are zero. E3 is IN_PROGRESS / A1_COMPLETE / VALIDATION_NEXT; next task is E3-A2 — Targeted Missing-Point Recovery Validation (NOT AUTHORIZED, execution false); no cohort or threshold is frozen.
Report: `evaluation/E3_A1_EXPERIMENTAL_MISSING_POINT_RETRIEVAL_IMPLEMENTATION.md`.

## E3-A2 targeted recovery validation closeout

COMPLETE / INCONCLUSIVE / INSUFFICIENT_NATURAL_MISSING_POINT_APPLICABILITY.
Prospective T2 validation of E3-A1 under the preregistration commit `50eada9e4c62980f4437d7b2ce0850667109305c`
(candidate HEAD `54d5483`). Mechanically selected exposed novel_dev cohort of 11 cases
(n003, n005, n006, n009, n010, n014, n019, n020, n021, n022, n024) from the frozen selector
(representative, >=2 critical answer points and evidence groups, non-single-hop or cross-source/repo topology).
Evaluation-only harness forked the identical first-verify checkpoint into a pre-E3 existing-evidence-only
revision control and the current E3 treatment; product frozen; default mode unchanged. All 11 cases terminal.
Natural applicability failed G2: only n006 was E3-applicable (2 first-missing runtime points; both thresholds
require >=4). The single blinded pair is descriptive only: no `satisfied_supported` point on either arm
(control absent/absent, insufficient_evidence; treatment partial/absent, answered; judge preferred treatment,
even-id mask control=Arm A), zero treatment-only preservation/safety regressions, E3 executed within all bounds
(1 targeted retrieval, 1 global rerank, 1 revision, atomic success, 1 newly admitted object, plan preserved).
G1/G4/G5/G6/G7 PASS; G3 FAIL; G2 FAIL → overall INCONCLUSIVE per the frozen precedence. No synthetic missing
points, no post-hoc cohort change, no product repair inside A2. Observed scientific usage: 78 model calls,
746,593 returned tokens (shared 71/630,066; control 2/47,329; treatment 4/58,559; judge 1/10,639); AGY workers 0
(AGY CLI unavailable in this environment; the §38 review gate ran as two rounds of an independent read-only
reviewer agent: defects found → cleared for execution). Limitations: single-case descriptive evidence;
judge model family equals generation model family; future E3 validation design must address the observed
9.1% natural applicability. E3 = IN_PROGRESS / A2_COMPLETE_INCONCLUSIVE / PENDING_FUTURE_LIFECYCLE_DECISION.
Report: `evaluation/E3_A2_TARGETED_MISSING_POINT_RECOVERY_VALIDATION.md`.

## E3-LR1 post-A2 lifecycle reconciliation closeout

COMPLETE / PASS / POST_A2_LIFECYCLE_RECONCILED. Static lifecycle/architecture/scope review at HEAD `c57ee18`;
zero PANDA scientific/evaluation calls or tokens; zero product changes; only the decision report, this status
file, and the roadmap changed. Separated architecture (Q1 justified, A0 PASS), implementation safety/bounds
(Q2 validated, A1 PASS plus observed bounds), and standalone recovery benefit (Q3 UNRESOLVED /
INSUFFICIENT_NATURAL_APPLICABILITY). Reconciled F1-R12 (pre-answer sufficiency routing: coexists with E3 on
different failure information; not a blocker; ownership remains Phase F/retrieval cleanup) and F1-R14
(E3 global reconsideration reuses authoritative `select_final_evidence`; not a blocker; shared-selection
changes must rerun focused E3 tests). Maintenance burden classified MODERATE (shared-path seams, mode-gated,
deterministically tested); proportionate to rare-but-important recovery value. Recorded the non-outcome-impacting
A2 G6 protocol-wording ambiguity as a future cleanup note only (A2 not reopened/rescored). Determined that
first-verify-failure-focused cohorts are outcome-conditioned selection: diagnostically useful, never prospective
applicability authority. Decision matrix selected OPTION A: E3 = COMPLETE /
BOUNDED_LOW_FREQUENCY_FALLBACK_IMPLEMENTED / SCIENTIFIC_RECOVERY_BENEFIT_UNRESOLVED; DEDICATED_E3_REVALIDATION =
NOT_PLANNED / LOW_NATURAL_APPLICABILITY_AND_LOW_DECISION_VALUE; FUTURE_E3_EVIDENCE = ACCUMULATE_OPPORTUNISTICALLY
_IN_BROADER_AUTHORIZED_EVALUATIONS. No default promotion; E2 promotion remains DEFERRED.
NEXT_TASK_RECOMMENDATION = Phase-E lifecycle / promotion-boundary reconciliation (NOT AUTHORIZED).
Report: `evaluation/E3_LR1_POST_A2_LIFECYCLE_DECISION.md`.

## PE-LR1 Phase-E promotion-boundary reconciliation closeout

COMPLETE / PASS / PHASE_E_CLOSED_PROMOTION_DEFERRED_UNTIL_MATERIAL_CANDIDATE. Static promotion-boundary decision at
HEAD `71e8861`; zero PANDA scientific/evaluation calls or tokens; zero product changes; only the decision report,
this status file, and the roadmap changed. Four questions separated: P1 Phase-E architecture complete = yes
(E1/E2/E3 all present with accepted dispositions); P2 runtime_e1_v2 valid experimental path = yes; P3 normal-default
promotion now = no (historical activation failures E2-A3 Q7, R1 P2_P6, R3-R1 G11 remain binding; a materially
changed runtime candidate does exist after the failed lineage because E3-A1 introduced real runtime_e1_v2 behavior,
but E3 is a rare post-verify fallback that does not repair or directly resolve that failure surface, its standalone
efficacy remains unresolved, and no current product decision depends on immediate promotion — so it is not a
promotion-relevant material improvement; QA-M1 was generic maintenance and E3-LR1/PE-LR1 are documentation); P4 reopening trigger recorded. F1-R08/R09/R11
compatibility cluster does not block Phase-E completion; contributes-but-not-sole-blocker for promotion; ownership
remains Phase F. Material-candidate set for a future promotion decision: R08/R09/R11 cluster, R13 verifier-support
override, R10 deterministic requirements, R14 selection policy, R04 refusal path; F1-R01 remains the fourth
F2 candidate inside Phase-F scope reconciliation even if less promotion-relevant (prioritization
consideration, not a reclassification). Component-wise analysis:
runtime_e1_v2 is a coupled mode (single answer_point_coverage_mode switch selects E1 decomposition + E2 coverage
semantics + E3 eligibility); independent component promotion is unsupported and not decision-relevant. Decision
matrices selected Phase-E OPTION A (COMPLETE / CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED /
DEFAULT_PROMOTION_DEFERRED) and promotion D3 (defer until a promotion-relevant material candidate change or explicit release boundary).
Retired the E2 DEFAULT-PROMOTION GATE REDESIGN deferral as CLOSED / NO_IMMEDIATE_REVALIDATION_DEFINED /
REOPEN_ONLY_FOR_PROMOTION_RELEVANT_MATERIAL_CANDIDATE_OR_RELEASE_BOUNDARY — no historical E2 outcome altered. Recorded
DEFAULT_PROMOTION_RECONSIDERATION_TRIGGER. Legacy default is an accepted stable outcome, not an incomplete state.
NEXT_TASK_RECOMMENDATION = Phase-F scope reconciliation and bounded benchmark-dependency cleanup planning
(NOT AUTHORIZED).
Report: `evaluation/PE_LR1_PHASE_E_PROMOTION_BOUNDARY_RECONCILIATION.md`.

## PF-LR1 Phase-F scope reconciliation closeout

COMPLETE / PASS / PHASE_F_SCOPE_RECONCILED_BOUNDED_CLEANUP_PLAN_ESTABLISHED. Static lifecycle/scope reconciliation
at HEAD `a2920d9`; zero PANDA scientific/evaluation calls or tokens; zero product changes; zero protected-data
access; only the decision report, its machine-readable companion, this status file, and the roadmap changed.
Revalidated the F1 inventory (R01-R21) against current HEAD: all anchors present, no reclassification. Formal F2
scope = five bounded groups: A R13 verifier-support semantics, B R10 deterministic completeness semantics,
C R08/R09/R11 E1/E2 compatibility retirement as one bounded named step inside F2 (coverage-equivalence condition,
no new top-level phase), D R04 premise/refusal generalization (building on R16 as a design foundation, never
blanket deletion), E R01 semantic source obligations. R13 and R10 are independently implementable; R13-first is
RECOMMENDED_SEMANTIC_SEQUENCING (SOFT_ARCHITECTURAL_ORDERING) only — no hard prerequisite, code, or dataflow
dependency — so a non-PASS R13 outcome alone does not block R10. R12 = E3_RECONCILED_NO_STANDALONE_ACTION
(E3-LR1 §8; phase_f_action_required=false, standalone_task_allowed=false, promotion_materiality=NOT_APPLICABLE;
revisitable only as an interaction boundary if a broader Phase-F change materially modifies the pre-answer
retrieval/sufficiency path). R14 = PHASE_F_SHARED_BOUNDARY_REVIEW with NO_CHANGE_CURRENTLY_JUSTIFIED (C7
CURRENT_SELECTOR remains production-authoritative; E3-LR1 §9 validation coupling — the focused E3 validation
prescribed by the authoritative E3 lifecycle artifact, cited there as the 49 focused E3 tests — applies to any
future shared-selection change; no implementation task is manufactured for R14). F3 = bounded R03/R05/R06
fixed-locator/fallback cleanup package; ownership decided by implementation origin and lifecycle ownership:
D4 owns the YAML query-expansion locator-retirement pattern (five active migrations), the confirmed HOLDs, and
R20, while R03/R05/R06 are independent code origins outside the D4 rule inventory (the reconstructed_profile_to_acceptance
rule shares page values but is unmigrated; event_poca_handoff's structured replacement covers the YAML rule, not
the finalizer). Original-F3 scope already implemented by D4 closes as superseded. Promotion materiality per
PE-LR1 §6/§10: R13/R10/R08-R09-R11/R04 = PROMOTION_RELEVANT_MATERIAL; R01/R14 = POTENTIALLY_MATERIAL_WHEN_COUPLED;
R03/R05/R06 = LOCAL_NON_MATERIAL; R12/HOLD/KEEP/excluded = NOT_APPLICABLE. Promotion relevance is not promotion
authorization. Default promotion stays deferred (D3); normal default remains legacy_question_core; runtime_e1_v2
remains explicit-selection-only. No historical outcome rewritten; E3 and D4 not reopened; no D4-A11.
NEXT_TASK_RECOMMENDATION = R13 bounded verifier-support semantic cleanup (RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/PF_LR1_PHASE_F_SCOPE_RECONCILIATION.md`.

## F2-A1 verifier-support semantic cleanup closeout

COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED. Bounded production cleanup of the PF-LR1 Group A
verifier-support surface (F1 residual R13) at HEAD `c7a1c5a`; zero PANDA scientific/evaluation calls or tokens;
zero protected-data access. Mechanism: `deterministically_supported_claims` is produced in `QAAgent._verify` and
consumed to exempt claims from the semantic review's unsupported-claim verdict in non-shadow verification
(legacy and runtime_e1_v2 share the path; shadow never exempts). Removed: (1) the hard-coded token whitelist
`{createLmdFitData, fillData, successfullyPassedFilters, GetTubeID, CheckZInfo, Init, Exec}` from the
explicit-code-token predicate — the predicate is now purely shape-based (Pnd prefix, :: qualifier, capitalized
identifier) with no enumerated benchmark tokens; (2) both comparison-wording deterministic-support branches and
their hard-coded contrast-word lists (including non-English tokens) whose only justification was current
benchmark behavior — those claims now pass through ordinary semantic verification. Retained: the generic
identifier/path full-coverage, path-coverage-over-code-repository, and multi-symbol-coverage invariants, all
evidence-grounded and shape-based with no enumerated tokens. No replacement whitelist was introduced; verification
is strictly tightened. R10 surface (`_deterministic_missing_requirement_ids`, pointer predicate) has zero diff;
compatibility, refusal, retrieval, selection, DTO, prompt, default-routing, mode-selection, E3-trigger, and
retained-support surfaces unchanged. Verification: tests/unit/test_qa.py 54 passed + 2 subtests (including three
new F2-A1 contract tests: generic path-anchor support survives a conservative review; former whitelist tokens no
longer grant support; comparison wording no longer grants support). Shared-verify E3 coupling applied (_verify is
the runtime_e1_v2 second-verify surface): the authoritative focused E3 deterministic set (E3-LR1 §9: 49 focused
E3 tests) plus 42 neighboring E2-A1 shadow tests → 91 passed. E3 lifecycle not reopened. Scope-claim support
branch noted as unreachable dead code (internal-claim filtering precedes it) and left unchanged. Normal default
remains legacy_question_core; runtime_e1_v2 remains explicit-selection-only; default promotion remains deferred
(D3); promotion relevance is not promotion authorization.
NEXT_TASK_RECOMMENDATION = F2-A2 — Deterministic Completeness Semantic Cleanup (PF-LR1 Group B / F1 residual R10)
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F2_A1_VERIFIER_SUPPORT_SEMANTIC_CLEANUP.md`.

## F2-A1-R1 verifier-support semantic entailment repair closeout

COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED. Corrective repair of F2-A1 at HEAD `32abb1c`; zero PANDA
scientific/evaluation calls or tokens; zero protected-data access. Post-commit audit did not accept F2-A1's
initial terminal PASS: generic lexical identifier/path/symbol coverage branches still marked whole claims as
deterministically supported, causing an explicit semantic-review unsupported verdict to be ignored (citation/
locator/identifier grounding is not whole-claim semantic entailment). Repair: deleted the
`deterministically_supported_claims` set entirely — the scope-claim branch (unreachable: internal-claim filtering
precedes it), the identifier-coverage branch, the path-coverage-over-code-repository branches, the multi-symbol
coverage branch, and the unsupported-claim exemption in the verify loop. No live claim class has a fully
structured whole-claim entailment contract, so the override was removed entirely rather than narrowed; no
replacement whitelist was introduced. The semantic review's unsupported_claim_ids verdict is now always honored.
Preserved unchanged: unsupported-identifier, wrong-code-version, and incomplete code/paper/web citation checks,
internal-claim filtering, R10 (`_deterministic_missing_requirement_ids`, pointer predicate, zero diff),
requirement logic, retrieval, reranking, evidence selection, public DTOs, prompts, mode selection, default
routing, E3 trigger semantics, retained-support protections. Valid F2-A1 removals (token whitelist, comparison
wording) remain removed; commit `32abb1c` preserved in history, original F2-A1 report carries a correction/
supersession notice. Adversarial contracts T1-T6 (correct path + false semantics; correct symbols + false
relationship; multiple identifiers + false predicate; legitimate supported claim still accepted; former
whitelist/comparison regressions stay removed; integrity checks remain active) all pass.
Verification: tests/unit/test_qa.py 58 passed + 2 subtests; authoritative focused E3 deterministic set (E3-LR1
§9: 49 focused E3 tests) plus 42 neighboring E2-A1 shadow tests → 91 passed (deterministic regression check
only; E3 lifecycle not reopened). F2-A1's final lifecycle state (GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED)
is achieved only after this repair. Normal default remains legacy_question_core; runtime_e1_v2 remains
explicit-selection-only; default promotion remains deferred (D3); promotion relevance is not promotion
authorization.
NEXT_TASK_RECOMMENDATION = F2-A2 — Deterministic Completeness Semantic Cleanup (PF-LR1 Group B / F1 residual R10)
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F2_A1_R1_VERIFIER_SUPPORT_SEMANTIC_ENTAILMENT_REPAIR.md`.

## F2-A2 deterministic completeness semantic cleanup closeout

COMPLETE / PASS / QUESTION_DERIVED_POINTER_NORMALIZATION_COMPLETENESS_ESTABLISHED. Bounded production cleanup of the
PF-LR1 Group B pointer-normalization completeness specialization (F1 residual R10) at HEAD `071ad16`; zero PANDA
scientific/evaluation calls or tokens; zero protected-data access. Old specialization: generic question-grounded
activation (pointer type expression + normalization vocabulary) flowed into a hard-coded completion rule —
`_requirement_evidence` selected through fixed anchors (pndlmdtrackq, pointer, tclonesarray),
`_compact_requirement_evidence` compacted through (pndlmdtrackq, pointer, tclonesarray, lmdtrackq), and
`_deterministic_missing_requirement_ids` required the claim to mention PndLmdTrackQ*/underlying PndLmdTrackQ.
Repair: `_answer_requirements` extracts the pointer type expression from the live question and emits the
requirement with bounded metadata target_symbol (activation additionally requires a named pointer type expression;
plan-only symbol presence never creates the requirement); `_requirement_evidence` selects on the dynamic target or
generic normalization vocabulary (pointer, type expression); `_compact_requirement_evidence` gained an optional
target_symbol parameter with dynamic anchors; `_deterministic_missing_requirement_ids` evaluates the three-part
semantic contract (pointer type expression stated, underlying target symbol named, qualifier explained as syntax)
against the question-derived target, and a targetless requirement stays missing (never weakened to keyword
presence). No hard-coded pndlmdtrackq/lmdtrackq/tclonesarray remains in qa.py. Other requirements, F2-A1/F2-A1-R1
semantics, integrity checks, retrieval, selection, DTOs, prompts, modes, and E3 surfaces unchanged; Group C
retirement not begun. Genericity/adversarial contracts T1-T8 (historical symbol generic regression; unseen
SensorFrame* end to end; wrong historical symbol cannot satisfy an unseen target; incomplete semantics fails;
qualifier explanation required; non-pointer question inactive; plan-only symbol not a target; dynamic evidence
selection/compaction) all pass. Verification: tests/unit/test_qa.py 66 passed + 4 subtests; authoritative focused
E3 deterministic set (E3-LR1 §9: 49 focused E3 tests) plus 42 neighboring E2-A1 shadow tests → 91 passed
(deterministic regression check only; E3 lifecycle not reopened). F2 remains incomplete (Groups C/D/E outstanding).
Normal default remains legacy_question_core; runtime_e1_v2 remains explicit-selection-only; default promotion
remains deferred (D3); promotion relevance is not promotion authorization.
NEXT_TASK_RECOMMENDATION = F2-A3 — E1/E2 Compatibility Retirement (PF-LR1 Group C / F1 residuals R08, R09, R11)
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F2_A2_DETERMINISTIC_COMPLETENESS_SEMANTIC_CLEANUP.md`.

## F2-A3 E1/E2 compatibility retirement closeout

COMPLETE / PASS / E1_E2_COMPATIBILITY_AUTHORITY_RECONCILED. Bounded Group-C cluster cleanup (F1 residuals R08/R09/
R11) at HEAD `d480fc2`; zero PANDA scientific/evaluation calls or tokens; zero protected-data access. Authority
reconciliation: in E1/E2 coverage modes (shadow_e1_v2, runtime_e1_v2) whole-answer completeness is owned by the
claim-to-answer-point coverage review and bounded revision via missing_answer_point_ids; the legacy named-requirement
contract is retained in full as a legacy_question_core bridge and is non-authoritative in coverage modes — the
deterministic missing-requirement check is not executed there, the review's known missing_requirement_ids are
ignored (unknown-id hallucination guard kept), revision scope asks only for missing_answer_point_ids, plan-driven
dataflow augmentation (required_*/dataflow_locator_*, internal-filtered) is disabled, and required_boundary_locators
payloads are empty. The E3 second-verify deterministic-requirement view was retired with its consumer; claim-level
retained-ledger protection (invalid evidence) is preserved. _augment_planned_locators is preserved in all modes
(question-grounded: locator vocabulary + question-named planned symbol). Seam tests prove the ownership transfer:
a coverage-complete answer with a model-returned legacy missing requirement passes in both coverage modes
(test_coverage_mode_legacy_requirement_is_non_authoritative, shadow+runtime) while legacy_question_core still
enforces it (test_legacy_default_still_enforces_requirements); plan-only suggestions synthesize no claims and inject
no boundary locators in coverage modes (test_dataflow_augmentation_is_mode_scoped,
test_boundary_locators_are_mode_scoped). One E2 and three E3 tests were updated from asserting coverage-mode
named-requirement authority to asserting the retired mode-scoped semantics. Verification: tests/unit/test_qa.py
70 passed + 6 subtests; E2-A1 42 + focused E3 deterministic set 49 → 91 passed; combined 161 passed + 6 subtests.
Prompts.py and question_decomposition.py unchanged; retrieval/selection/R04/R01/R14/F3/D4/default/promotion
untouched; F2 remains incomplete (Groups D/E outstanding). Normal default remains legacy_question_core;
runtime_e1_v2 remains explicit-selection-only; default promotion remains deferred (D3); promotion relevance is not
promotion authorization.
NEXT_TASK_RECOMMENDATION = F2-A4 — Premise and Refusal Generalization (PF-LR1 Group D / F1 residual R04)
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F2_A3_E1_E2_COMPATIBILITY_RETIREMENT.md`.

## F2-A3-R1 coverage-mode legacy prompt authority repair closeout

COMPLETE / PASS / COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REMOVED. Corrective repair of F2-A3 at HEAD `7bf0df4`; zero
PANDA scientific/evaluation calls or tokens; zero protected-data access. Post-commit audit did not accept F2-A3's
initial terminal PASS: legacy answer_requirements were retired as downstream code-side authority but remained live
in model-facing payloads — generation, coverage review, and revision all received the full legacy set (with
requirement evidence), the inherited/coverage prompt contracts still treated them as a completeness axis, and a
stale supported=false verdict explained only by known legacy requirement ids could still create global_review_failure.
Repair: coverage-mode model-facing generation/review/revision payloads now carry answer_requirements=[],
requirement_evidence={}, and missing_requirement_ids=[]; the full legacy set remains in state only for the
unknown-requirement guard, diagnostics, and legacy execution; a supported=false explained solely by known legacy
ids with every authoritative axis clean is treated as obsolete (no global failure) while unknown ids keep the
coverage-review structural guard and unexplained/other supported=false keeps conservative failure; coverage-specific
review/revision prompt extensions now state that named legacy requirements are non-authoritative and must be
returned empty (legacy review/revision prompt contracts unchanged; PROMPT_SET_VERSION 3.8.0 -> 3.9.0). Adversarial
contracts T1-T12 (mode-scoped generation payload; empty coverage review/revision axes; stale-legacy sentinel with
coverage complete/evaluable in shadow+runtime; unknown-id guard; genuine failures retained; legacy bridge and
F2-A3 R11 scoping, F2-A2, F2-A1/F2-A1-R1 preservation) all pass. Verification: tests/unit/test_qa.py 76 passed +
11 subtests; E2-A1 42 + focused E3 deterministic set 49 -> 91 passed (shared _verify/_revise model-facing
regression only; E3 lifecycle not reopened); combined 167 passed + 11 subtests. Commit `7bf0df4` preserved; the
original F2-A3 report carries a correction/supersession notice. F2-A3's final lifecycle state is achieved only
after this repair. Normal default remains legacy_question_core; runtime_e1_v2 remains explicit-selection-only;
default promotion remains deferred (D3); promotion relevance is not promotion authorization.
NEXT_TASK_RECOMMENDATION = F2-A4 — Premise and Refusal Generalization (PF-LR1 Group D / F1 residual R04)
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F2_A3_R1_COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REPAIR.md`.

## F2-A4 premise and refusal generalization closeout

COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED. Bounded Group-D cleanup (F1 residual R04) at HEAD
`bb1a639`; zero PANDA scientific/evaluation calls or tokens; zero protected-data access. Historical specialization:
`_sufficiency` triggered on the exact literal PndUniversalRestgasDeconvolver and used the currently selected
evidence as the whole-corpus existence authority; `_finalize` matched that exact error, searched the fixed locator
macro/target/correction/efficiency_correction_2.C, and asserted a substitute implementation in the public refusal.
Repair: a question-grounded extractor (`_requested_bare_class_symbols`; explicit class/struct/enum wording, pointer
type expressions, and compound-cased identifiers inside request/definition contexts — plain capitalized prose and
plan-only symbols excluded by construction, the plan is never read) feeds a generic bare-class premise check in
`_answerability_guard` against `_locked_symbols()`; catalog absence — not selected-evidence absence — produces the
structured error `unsupported requested symbol: <symbol>`. `_sufficiency`'s exact branch was removed; `_finalize`
now parses the requested symbol from the structured error and emits dynamic generic refusal wording with an
optional evidence-grounded basis: `_refusal_basis_evidence` gained an unsupported_symbol kind (code/workflow
evidence with question-anchor overlap, ranked purely by overlap, None when nothing is relevant) producing at most
one claim ("The cited locked code at <location> documents <subject>.") with no substitution assertion. No
production control-flow literal remains for the historical class or locator. Preservation audit: zero diff touches
on F2-A1/A1-R1, F2-A2, F2-A3/A3-R1, R16, R05/R06, R14, E1/E2, E3, retrieval, selection, default, promotion.
Adversarial contracts T1-T15 plus the selected-evidence-vs-catalog sentinel and the premise-mismatch sentinel all
pass. Verification: tests/unit/test_qa.py 89 passed + 16 subtests; combined focused run with E2-A1 42, focused E3
49, and test_service 13 -> 193 passed + 16 subtests (E3 run as a bounded regression; E3 lifecycle not reopened).
F2 remains incomplete (Group E outstanding). Normal default remains legacy_question_core; runtime_e1_v2 remains
explicit-selection-only; default promotion remains deferred (D3); promotion relevance is not promotion
authorization.
NEXT_TASK_RECOMMENDATION = F2-A5 — Semantic Source Obligation Generalization (PF-LR1 Group E / F1 residual R01)
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F2_A4_PREMISE_REFUSAL_GENERALIZATION.md`.

## F2-A4-R1 question-grounded premise refusal repair closeout

COMPLETE / PASS / QUESTION_GROUNDED_PREMISE_REFUSAL_BOUNDARY_ESTABLISHED. Corrective repair of F2-A4 at HEAD
`4f9c87e`; zero PANDA scientific/evaluation calls or tokens; zero protected-data access. Post-commit audit did not
accept F2-A4's initial terminal PASS; three behavior-confirmed defects: (1) unsupported_symbol refusal-basis
relevance mixed plan-only symbols/concepts into the anchors (plan-suggested unrelated evidence could become the
optional basis); (2) explicit class/struct/enum capture did not validate the token ("What class of problem is
this?" extracted "of"; "Explain the struct layout used here." extracted "layout"); (3) the bare locator premise
("Where is MissingTrackAdapter?") was under-detected after "where is" had been dropped. Repair: question-only
anchors (`question_anchors`) are the admission and ranking authority for the unsupported_symbol kind while
future_runtime/universal_proof rankings are unchanged; explicit and pointer captures require the code-like shape
predicate (`_is_code_like_identifier`: length > 2, initially capitalized or underscore-bearing); locator contexts
restored ("where is", "where's", "which file", "which code", "path") with class-shape still required; per the R1
rule the fixtures of four full-path tests asking "Where is PndPidCorrelator?" were corrected with a realistic
catalog row instead of weakening production semantics. Adversarial sentinels: plan-only basis contamination ->
basis None and zero optional claims; question-relevant basis still selected; "class of"/"struct layout" -> no
trigger; bare "Where is MissingTrackAdapter?" -> refused; "Where is PndPidCorrelator?" with catalog -> no refusal;
plan-only unknown symbol still inert; historical/unseen negative controls still generic; selected-evidence-vs-
catalog and premise-mismatch sentinels intact; R05/R06 untouched; coverage-mode early refusal still never reaches
E3 inputs; F2-A3-R1 authority contract intact. Verification: tests/unit/test_qa.py 95 passed + 16 subtests;
combined focused run with E2-A1 42, focused E3 49, test_service 13 -> 200 passed + 16 subtests (E3 run as an
optional bounded regression; E3 lifecycle not reopened). Commit `4f9c87e` preserved; the original F2-A4 report
carries a correction/supersession notice. F2-A4's final lifecycle state is achieved only after this repair. Normal
default remains legacy_question_core; runtime_e1_v2 remains explicit-selection-only; default promotion remains
deferred (D3); promotion relevance is not promotion authorization.
NEXT_TASK_RECOMMENDATION = F2-A5 — Semantic Source Obligation Generalization (PF-LR1 Group E / F1 residual R01)
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F2_A4_R1_QUESTION_GROUNDED_PREMISE_REFUSAL_REPAIR.md`.

## F2-A5 semantic source obligation generalization closeout

COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED. Bounded Group-E cleanup (F1 residual
R01) at HEAD `79df30e`; zero PANDA scientific/evaluation calls or tokens; zero protected-data access. Historical
chain: fixed config mappings (algorithm_theory -> paper; algorithm_implementation -> paper+code, F1 EXPLICIT gold
provenance) flowed through Retriever.analyze into RetrievalPlan.required_source_types and gated exact-paper
priority, the dedicated _paper channel, required-first/backfill selection, and _sufficiency hard refusals. Repair:
`_question_grounded_source_obligations` derives bounded paper/code obligations from the raw user question only
(paper: paper/thesis/publication/literature/journal; code: source code/implementation/implemented/signature/which
file/which source/macro); `Retriever.analyze` applies it for the R01 intents (the intent only selects the
question-grounded regime; analyzer concepts/symbols, plan symbols, page hints, and query expansions are never
consulted) and retains policy.required_sources unchanged for the R02/HOLD intents; a source_obligations receipt
(mode/authority/required_source_types/matches) is recorded in plan.analysis_diagnostics. The two R01 config
required_sources entries are retired to [] with all source_budgets byte-identical; all six R02 mappings are
exactly preserved (asserted) and an R02 probe proves the paper vocabulary in a question cannot replace an R02
policy mapping. Consumers keep gating purely on the dynamic plan field (inspect-audited: _paper, exact-paper
priority, _prioritize_and_select_evidence, select_final_evidence, _sufficiency — no intent-keyed requirement
logic; selector algorithm unchanged). Sufficiency honors explicit paper/code obligations (missing required source:
paper|code) while no-obligation questions are not refused for source-class absence and zero evidence is still
refused. R03, R14, R19, D4 boundaries preserved (diff-audited); F2-A1..A4-R1 preservation sentinels pass; E3
indirect boundary intact (explicit source insufficiency still terminates pre-answer; E3 not reopened).
Verification: tests/unit/test_retrieval.py 47 passed + 7 subtests (13 new SourceObligationTests); tests/unit/
test_qa.py 91 passed + 16 subtests; combined focused run with E2-A1 42, focused E3 49, test_service 13 -> 249
passed + 25 subtests. F2 closure: PF-LR1 defines exactly five F2 groups; A (R13, closed by F2-A1-R1), B (R10),
C (R08/R09/R11, closed by F2-A3-R1), D (R04, closed by F2-A4-R1), and E (R01) are all COMPLETE/PASS, so
F2 = COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE; R12/R14/R02/R03-R05-R06 are not unfinished F2 work. Phase F =
IN_PROGRESS / F2_COMPLETE_F3_NOT_STARTED. Future-applicability note only: the accumulated F2 package may
constitute a future promotion-relevant material candidate under the PE-LR1 trigger; this authorizes nothing.
Normal default remains legacy_question_core; runtime_e1_v2 remains explicit-selection-only; default promotion
remains deferred (D3); promotion relevance is not promotion authorization.
NEXT_TASK_RECOMMENDATION = F3 — Fixed Locator/Fallback Cleanup (PF-LR1 bounded package: R03, R05, R06)
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F2_A5_SEMANTIC_SOURCE_OBLIGATION_GENERALIZATION.md`.

## F2-A5-R1 source obligation boundary repair closeout

COMPLETE / PASS / SOURCE_OBLIGATION_MATCHING_BOUNDARY_ESTABLISHED. Corrective repair of F2-A5 at HEAD `3eca78d`;
zero PANDA scientific/evaluation calls or tokens; zero protected-data access. Post-commit audit did not accept
F2-A5's initial terminal PASS (nor the aggregate F2 closure): the question-grounded helper used unbounded substring
matching, behavior-confirmed false positives — "Why is this hypothesis physically reasonable?" -> ["paper"]
("thesis" inside "hypothesis"), "Why is the macroscopic behavior different?" -> ["code"] ("macro" inside
"macroscopic"), "How does a paperless workflow behave?" -> ["paper"], and "Which source of systematic uncertainty
dominates ...?" -> ["code"] from the ambiguous bare "which source" — each feeding a hard sufficiency gate. Repair
(helper-local, no negative-word patching): `_PAPER_OBLIGATION_PATTERNS` / `_CODE_OBLIGATION_PATTERNS` +
`_first_source_obligation_match` — multi-word phrases match as phrases, single tokens require regex word
boundaries; the ambiguous bare "which source" was removed as a sufficient code trigger (bounded replacements:
"which source file", "which code file", "source file"); support spans record the actual matched phrase; obligation
order remains deterministically paper, code; the helper still accepts only the raw question; the consumer chain
(_exact paper priority, _paper, _prioritize_and_select_evidence, select_final_evidence, _sufficiency) is untouched
(diff-audited zero consumer/selector/R03 changes). Post-fix precision matrix: paper/thesis/publication/
literature/journal -> paper; hypothesis/paperless/journaled -> none; source code/implementation/implemented/
signature/macro/which file/which source file -> code; macroscopic/which-source-of-uncertainty/source-of-background
-> none; receipt spans record actual phrases. Adversarial contracts T1-T26 pass, including the end-to-end sentinel
(lexical false positives cannot fail sufficiency) and R02/budget/consumer preservation. Verification:
tests/unit/test_retrieval.py 52 passed + 7 subtests; tests/unit/test_qa.py 93 passed + 16 subtests; combined
focused run with E2-A1 42, focused E3 49, test_service 13 -> 255 passed + 47 subtests (E3 run as an optional
bounded regression; E3 lifecycle not reopened). Commit `3eca78d` preserved; the original F2-A5 report carries a
correction/supersession notice. F2-A5's final lifecycle state is achieved only after this repair, and the
aggregate F2 = COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE is re-validated after R1. Normal default remains
legacy_question_core; runtime_e1_v2 remains explicit-selection-only; default promotion remains deferred (D3);
promotion relevance is not promotion authorization.
NEXT_TASK_RECOMMENDATION = F3 — Fixed Locator/Fallback Cleanup (PF-LR1 bounded package: R03, R05, R06)
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F2_A5_R1_SOURCE_OBLIGATION_BOUNDARY_REPAIR.md`.

## F3 fixed locator / fallback cleanup closeout

COMPLETE / PASS / FIXED_LOCATOR_FALLBACK_SHORTCUTS_RETIRED. Bounded PF-LR1 F3 package (F1 residuals R03/R05/R06,
all LOCAL_NON_MATERIAL) at HEAD `a7109e3`; zero PANDA scientific/evaluation calls or tokens; zero protected-data
access. R03: deleted the `Retriever.analyze` feedback page override (algorithm_theory + feedback phrases +
existing li_2026 hints -> forced `[141, 149, 151]`); reviewed query-expansion semantics are the only remaining
page-hint authority and the D4-owned `reconstructed_profile_to_acceptance` YAML rule is unchanged. R05: removed
the unsupported-API finalizer's fixed `PndPidCorrelator.h` endswith fallback; the generic requested-owner
matching (owner-in-path / owner==symbol) is preserved and the optional claim now states exactly what the cited
evidence supports ("The cited locked code at <location> documents <owner>, but does not establish the exact
requested API signature <requested>.") with no header assumption; no relevant evidence keeps `claims = []` /
`evidence = []`. R06: removed the deleted-runtime finalizer's fixed `macro/target/ana_dpm.C` lookup and
unconditional event_poca wording; the base refusal is artifact-neutral ("Deleted runtime records cannot be
reconstructed from source code alone.") and optional context comes from a bounded `deleted_runtime` kind in the
generic `_refusal_basis_evidence` selector (already-selected bundle only, identifier-like question artifact
anchors, question-anchor-overlap ranking, no fixed path preference, None when nothing is relevant; existing
future_runtime/universal_proof/unsupported_symbol kinds byte-identical). No replacement fixed locator, new
configuration, model call, or retrieval was introduced (static sentinels assert the three historical literals
are absent from production sources). Adversarial contract T1-T24 all PASS, including both central sentinels
(unseen API owner gets no historical header citation; unseen deleted-runtime artifact gets a generic refusal
with no event_poca leakage). D4 YAML and `select_final_evidence` zero-diff; R14/R15/R07/R20 and E3 boundaries
untouched; both pre-existing fallback-dependent tests pass unmodified through the generic mechanisms.
Verification: tests/unit/test_retrieval.py 59 passed + 27 subtests; tests/unit/test_qa.py 111 passed + 19
subtests; integrated focused run 170 passed + 46 subtests. R03/R05/R06 = RETIRED; per-residual matrix and
T1-T24 record in the report. Normal default remains legacy_question_core; runtime_e1_v2 remains
explicit-selection-only; default promotion remains deferred (D3); promotion relevance is not promotion
authorization.
NEXT_TASK_RECOMMENDATION = F4 — Separate Answer-Generation and Semantic-Verification Roles
(RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F3_FIXED_LOCATOR_FALLBACK_CLEANUP.md`.

## F4 generation / verification role separation closeout

COMPLETE / PASS / ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED. Architecture-only role separation at
HEAD `ba521bb`; zero PANDA scientific/evaluation calls or tokens; zero protected-data access; no model comparison
and no promotion evaluation. Pre-F4 coupling: one client (`self.vertex = vertex or VertexAIClient(from_env())`)
served `_answer`, the `_verify` semantic review (single call site shared by legacy and coverage review), and
`_revise`; prompt separation existed, role/client separation did not. Changes: `VertexSettings` gained an optional
`verification_model` field (from_env reads optional `QA_VERIFICATION_MODEL_ID`; not required),
`effective_verification_model` (= verification_model or generation_model), and `for_verification_model()`;
`generate_json` gained a keyword-only `usage_stage` label recording additive role counters
(`qa_generation_calls`/`qa_generation_token_usage`/`qa_semantic_verification_calls`/
`qa_semantic_verification_token_usage`) with aggregate counters and unlabeled call behavior byte-compatible;
`QAAgent.__init__` gained `verification_vertex=` and the production default builds two DISTINCT clients
(generation + `settings.for_verification_model()`) even when both effective model IDs are equal; a sole legacy
`vertex=` injection serves both roles as an explicit compatibility seam; routing: `_answer`/`_revise` →
generation role, `_verify` semantic review (legacy + coverage + E3 second verify via re-entry) → verification
role; retrieval/analyzer/embedding/decomposition paths unchanged; role-agnostic usage aggregation sums unique
role clients by object identity (a shared injected client is counted once) preserving the four aggregate keys;
internal `model_roles` diagnostics receipt added to `run_detailed` diagnostics. Failure semantics stay fail-closed
with no cross-role fallback and no new retries. The evaluation judge remains a third, offline role — never wired
into product QA. Deterministic integrity checks remain application authority (a `supported=true` verdict cannot
waive invalid-evidence/wrong-version/incomplete-locator errors) and F2-A1 semantic unsupported authority is
preserved. Adversarial contract T1-T30 all PASS, including both central sentinels (same-model-ID operation with
distinct client paths; three-model isolation generation/verification/judge). Public `QAResult`/schema/default
unchanged; role labels never appear in public content; E1/E2/E3 and all F2/F3 outcomes preserved. Verification:
tests/unit/test_vertex.py 20 passed (13 pre-existing unmodified + 7 new); tests/unit/test_qa.py 135 passed + 19
subtests (111 pre-existing unmodified + 24 new); integrated focused run 155 passed + 19 subtests;
test_retrieval.py regression 59 passed + 27 subtests. Normal default remains legacy_question_core;
runtime_e1_v2 remains explicit-selection-only; default promotion remains deferred; promotion evaluation not
authorized. F4 validates architecture and deterministic routing only; no verifier-quality claim is made.
NEXT_TASK_RECOMMENDATION = F5 — Bounded Answer Composer (RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F4_GENERATION_VERIFICATION_ROLE_SEPARATION.md`.

## F4-R1 production model-role diagnostics correction closeout

COMPLETE / PASS / PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTED. Corrective repair of F4 at HEAD `a9f3897`;
zero PANDA scientific/evaluation calls or tokens; zero protected-data access; reporting-only fix. Post-commit
audit did not accept F4's initial terminal PASS: with the production-shaped A/B/C configuration the internal
`model_roles` receipt misidentified the generation role — `role_model()` computed
`verification_model or generation_model` for BOTH role clients, but `verification_model` is the base-settings
field naming the model used to DERIVE the verification client, while the model any role client actually sends
`generate_json` calls to is `client.settings.generation_model`. Reproduction at the starting HEAD (real
production construction path, only from_env/VertexAIClient/Retriever mocked): generation client actual model
model-A, verification client actual model model-B, yet the receipt reported
`{answer_generation_model: model-B, semantic_verification_model: model-B, same_model_id: true}`. Repair
(`QAAgent._model_roles_diagnostics` only): `role_model()` now returns each role client's actual
`settings.generation_model` (settings-less fakes still report None markers). Post-fix the same production-shaped
reproduction reports `{answer_generation_model: model-A, semantic_verification_model: model-B, same_model_id:
false, distinct_client_paths: true}`. Routing, client construction, usage accounting (role counters, aggregate
summing, shared-client dedup, `usage_stage` labels), failure semantics, judge isolation, deterministic/semantic
authority, Vertex settings semantics, public schema, and the normal default have zero diff. New central
regression test uses real A/B/C base settings through the production-default construction path. T1-T18 all pass
(T2-T18 via pre-existing tests, unmodified). Verification: tests/unit/test_qa.py 136 passed + 19 subtests
(test_vertex.py not rerun — vertex.py zero diff). Initial F4 commit `a9f3897` preserved; the original F4 report
carries a correction/supersession notice. F4's final lifecycle state
(ANSWER_GENERATION_SEMANTIC_VERIFICATION_ROLES_SEPARATED) is achieved only after this repair. Normal default
remains legacy_question_core; runtime_e1_v2 remains explicit-selection-only; default promotion remains deferred;
promotion evaluation not authorized.
NEXT_TASK_RECOMMENDATION = F5 — Bounded Answer Composer (RECOMMENDED / NOT AUTHORIZED).
Report: `evaluation/F4_R1_PRODUCTION_MODEL_ROLE_DIAGNOSTICS_CORRECTION.md`.

## F5 bounded answer composer closeout

COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED.
READABILITY_BENEFIT = NOT_EMPIRICALLY_EVALUATED_IN_F5. Architecture implementation with deterministic/adversarial
T0-style validation at HEAD `6d24c5b`; zero PANDA scientific/evaluation calls or tokens; zero protected-data
access; no live Vertex calls. The deterministic `render_verified_answer` is byte-identical and is the mandatory
fallback. The composer receives ONLY verified claim ids/texts (`{task, verified_claims}` — no question, evidence,
evidence_ids, locators, plan, answer points, requirements, or drafts; citations are application-owned) through
the F4 generation role (`self.generation_vertex`, `usage_stage="qa_composer"`), returns structured paragraphs
with source claim ids, and is deterministically validated before any semantic review: exact-once claim coverage
(unknown/duplicate/missing/empty/invalid_structure), conservative technical-identifier provenance
(`new_identifier` via the shared `_CODE_DATA_EXTENSIONS` set), exact numeric-literal provenance
(`new_numeric_literal`), and bounded causal/comparison cue gates (`new_causal_relation`/
`new_comparison_relation`). Exactly one bounded semantic composition review runs on the F4 verification role
(reviewer sees only claims + paragraphs, no raw evidence; entailment/preservation only, fail-closed review
validation including valid=true-with-nonempty-lists and out-of-range/unknown references). Atomic acceptance:
any composer/reviewer exception, validation failure, or rejection falls back to
`render_verified_answer(original verified claims)` — the QA request never fails, verification_errors are never
touched, no partial salvage, no retries (max 1 composer + 1 review = 2 F5 calls; 0 for bypassed paths).
Single-claim (`single_claim_bypass`) and all refusal/conflict paths bypass the composer. Citations are
deterministically derived per paragraph (source-claim-order dedup union); `QAResult.claims`/`evidence`/schema/
default unchanged; no ComposedClaim public type; composer diagnostics are the sanitized 8-key internal
`diagnostics["composer"]` receipt only. Composer/review usage aggregates as `qa_composer_calls`/
`qa_composer_token_usage` without touching F4 counters. E3 retained claims/evidence flow through the same gate
and deterministic citation rendering. Adversarial contract T1-T43 all PASS, including both central security
sentinels (composer/reviewer payload boundaries). Verification: tests/unit/test_qa.py 179 passed + 19 subtests
(136 pre-existing incl. F4/F4-R1 + 43 new; two pre-existing assertions updated only as mandated by the prompt
version bump and the two new labeled call sites); tests/unit/test_e3_missing_point_retrieval.py 49 passed
(fallback preserves E3 finalizations). Normal default remains legacy_question_core; runtime_e1_v2 remains
explicit-selection-only; default promotion remains deferred; promotion evaluation not authorized.
NEXT_TASK_RECOMMENDATION = F6 — Release Evaluation and Generalization Gate (RECOMMENDED / NOT AUTHORIZED;
requires separate explicit T5/release authorization).
Report: `evaluation/F5_BOUNDED_ANSWER_COMPOSER.md`.

## F5-R1 exact literal and identifier provenance repair closeout

COMPLETE / PASS / EXACT_LITERAL_IDENTIFIER_PROVENANCE_BOUNDARY_ESTABLISHED. Corrective repair of F5 at HEAD
`2299cc0`; zero PANDA scientific/evaluation calls or tokens; zero protected-data access; reporting-boundary fix
only. Post-commit audit did not accept F5's initial terminal PASS: both deterministic provenance checks used
substring membership against arbitrary source prose instead of exact extracted-token membership. Reproduced at
the starting HEAD: numeric `-3 → 3` accepted ("3" in "-3"), `13 → 3`, `10% → 10` accepted; identifier
`PndPidCorrelatorV2 → PndPidCorrelator` accepted ("pndpidcorrelator" in "pndpidcorrelatorv2"), path shortening
`src/foo/TrackBuilder.cxx → TrackBuilder.cxx` accepted. Repair (`_validate_composed_paragraphs` + numeric
pattern only): numeric extraction gained explicit `+`/`-` sign attribution and a `(?<![\w.])` lookbehind so
digits embedded in technical identifiers (PndPidCorrelatorV2, sha256, v1.2) never become standalone literals;
paragraph numeric literals must exactly equal a literal extracted from the referenced source claims (sign,
decimal, percent, and scientific spellings are distinct; no normalization); paragraph technical tokens must
appear verbatim (case- and spelling-sensitive) among technical tokens extracted from the referenced claims; a
bounded casing-alteration sentinel rejects ordinary word tokens that case-insensitively alias a source technical
token while differing in exact spelling (closing the pndpidcorrelator bypass without generic proper-noun
validation). All R1 rejects fail before semantic review (review calls = 0) and fall back to the exact
deterministic renderer; no retry; claims/evidence/verification_errors untouched. Error codes remain
`new_numeric_literal`/`new_identifier`. Composer input boundary, exact-once coverage, semantic review as second
layer, deterministic citations, F4/F4-R1 routing and diagnostics, `qa_composer_*` accounting, single-claim/
refusal bypasses, public schema, E3 behavior, F2/F3, and the default are zero-diff. Applied the authorized
bounded prompt clarification ("Do not invent metadata identifiers, claim IDs, citation IDs, or evidence IDs.
Technical identifiers already present in the verified claims may be retained and must be preserved exactly.");
PROMPT_SET_VERSION 3.10.0 -> 3.10.1 with the dependent assertion updated. Adversarial contract T1-T30 all PASS
(16 new methods in TestComposerProvenanceBoundary; T20-T30 via pre-existing suites). Verification:
tests/unit/test_qa.py 195 passed + 21 subtests; tests/unit/test_e3_missing_point_retrieval.py 49 passed
(test_vertex.py not rerun — vertex.py zero diff). Original F5 commit `2299cc0` preserved; the original F5
report carries a correction/supersession notice. F5's final lifecycle state
(BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED) is achieved only after this repair. Normal default
remains legacy_question_core; default promotion remains deferred; promotion evaluation not authorized.
NEXT_TASK_RECOMMENDATION = F6 — Release Evaluation and Generalization Gate (RECOMMENDED / NOT AUTHORIZED;
requires separate explicit T5/release authorization).
Report: `evaluation/F5_R1_EXACT_LITERAL_IDENTIFIER_PROVENANCE_REPAIR.md`.

## F6 release evaluation pre-outcome HOLD record

HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET. F6 was explicitly authorized including T5, but the staged
fail-fast release order stopped at the zero-outcome preflight: the protected external holdout package
(panda-novel-holdout-v1, FROZEN_SEALED, expected 13, externally managed) is not available on the execution
machine — bounded discovery across the repository parent directory, user profile locations, the D: drive root,
and the sanitized governance documents found no package and no protected execution workspace
(`PANDA_Agent_Holdout` is a conceptual external workspace). No cohort was exposed; scientific/evaluation calls
and tokens are exactly 0. Completed preflight value: (1) candidate-freeze audit found and fixed the stale v2
benchmark binding (now signed m6-benchmark-v2.6 with manual_adjudications.yaml), added the F4
runtime/effective verification-model identities and primary_answer_point_mode, and extended prompt_fingerprint
to the full ten-prompt set including the F5 composer prompts (commit `c871444`, assertion fix `99fdbab`);
(2) an extra identity defect was found and fixed: the signed v2_6 benchmark manifest dataset_sha256 lagged the
authorized D4-A2-R1 g021 correction (commit `9b007b5`), which had silently diverted the evaluator to
m6-benchmark-v2.5 — the manifest record was aligned to the authorized corrected dataset with full provenance,
restoring m6-benchmark-v2.6 / 120 questions as the evaluator authority; (3) dataset roles were revalidated
(Gold exposed reference; novel_dev exposed development; novel_validation pristine/UNSEEN per historical run
records; holdout metadata-only), PostgreSQL/Qdrant/index identity confirmed reachable, and the integrity audit
recorded zero product changes, zero threshold changes, zero holdout-driven tuning, zero protected-content
leakage, and zero cohort exposure. Preregistration and candidate freeze were deferred to the executing attempt.
Phase F remains IN_PROGRESS / F5_COMPLETE_F6_HOLD; F1–F5 outcomes unchanged. Normal default remains
legacy_question_core; runtime_e1_v2 remains explicit-selection-only; default promotion remains deferred.
NEXT_TASK_RECOMMENDATION = F6 retry (fresh preregistration + candidate identity) after the protected external
holdout package is provisioned in its governed execution environment.
Report: `evaluation/F6_RELEASE_EVALUATION_AND_GENERALIZATION_GATE.md`.

## F6-LR1 release-gate staging reconciliation record

COMPLETE / PASS / RELEASE_GATE_STAGING_RECONCILED. Static lifecycle/protocol reconciliation at HEAD `03fc400`;
zero product/evaluator/freezer/manifest changes; zero model calls; zero scientific/evaluation calls or tokens.
Correction: the first F6 attempt treated physical protected-holdout availability as a prerequisite for ANY F6
scientific execution — over-strict, because the exposed/validation cohorts have different exposure economics
than the sealed holdout. Reconciled structure: F6-A — Pre-Release Validation & Generalization Gate (Gold v2.6,
novel_dev, novel_validation, approved evaluation-only ablation, composer release audit; holdout governance/
metadata integrity is its precondition; its positive terminal state is HOLDOUT_ELIGIBLE, not release PASS) and
F6-B — Protected Blind Release Gate (the only protected blind release decision; requires
F6-A = COMPLETE / PASS / HOLDOUT_ELIGIBLE with an identical frozen candidate identity; physical package
availability and the protected workspace are F6-B prerequisites B1/B2). Dataset roles formalized (Gold =
EXPOSED_BENCHMARK_REFERENCE; novel_dev = EXPOSED_DEVELOPMENT_GENERALIZATION_DIAGNOSTIC; novel_validation =
CANDIDATE_LEVEL_PRE_RELEASE_GENERALIZATION_GATE with PRISTINE_FOR_CURRENT_LINEAGE semantics and exposure-ledger
rules; novel_holdout = FINAL_PROTECTED_BLIND_RELEASE_EVIDENCE, not required during F6-A). Holdout-budget
principle recorded (do not consume holdout before F6-A PASS; a failed F6-A never triggers holdout). Run orders
A0–A7 / B0–B5 fixed; the five attempt-1 preflight engineering findings are carried into F6-A Stage A0 without
implementation (freezer/evaluator authority equivalence, benchmark-manifest identity in the freeze, Docker
image identity semantics decision, candidate_changes_after_freeze = NOT_REACHED when unfrozen, g021
post-signing provenance traceability). Attempt-1 artifacts preserved unmodified as historical records; no
product/evaluator/manifest/Gold content changed. Normal default remains legacy_question_core; default
promotion remains deferred.
NEXT_TASK_RECOMMENDATION = F6-A — Pre-Release Validation & Generalization Gate (RECOMMENDED / NOT AUTHORIZED;
Stage A0 engineering debt first).
Report: `evaluation/F6_LR1_RELEASE_GATE_STAGING_RECONCILIATION.md`.

## F6-A prerelease validation result record

COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED. First executed F6-A under the corrected staged
protocol at preregistration HEAD lineage `f30d907`/`28be395` (candidate f6a-rc1-20260913, refrozen against the
selector-defined identity; the superseded 120-question plan's preregistration/freeze and its terminated 9/120
partial run are preserved as historical records). Stage A0 closed all carried engineering debt: freezer/evaluator
signed-authority equivalence, benchmark-manifest identity, Docker Option A (release-critical postgres/qdrant
identities), clean-implementation-tree freeze + ancestor-HEAD verification with evaluation-infrastructure-only
drift accepted as diagnostic, unfrozen-gate NOT_REACHED semantics, and g021 provenance confirmed sufficient. The
reviewed product-language calibration was mechanically reconciled as versioned successor v3 (g021 criticality-only
change; re-derivation reproduces the declared 59/21 IDs exactly; no fresh human review claimed) and the stale
"full-dev before product gate" coupling was removed — the product gate is now computed from selector-cohort
completeness. Stage A1 executed the exact 59-ID formal-English Gold cohort mode=full (59/59 complete after three
external process terminations resumed under the same identity and two Vertex 429 quota failures retried after
recovery; retry transparently recorded). Release score 0.8277 (59/59). Ten preregistered gates FAILED:
final_evidence_recall 0.8129, critical_final_evidence_recall 0.8231, expected_status_accuracy 0.8644,
required_source_coverage_answered 0.9388, paper_code_dual_source_rate 0.1633, answer_point_coverage 0.8446,
critical_answer_point_miss_count 18, contradiction_count 4, major_unsupported_claim_count 1, plus the same
failure pattern surfacing in expected_status_accuracy. Six Gold-answered cases were erroneously refused
(g005/g013/g027/g034/g059/g060), four with the contradiction pattern of claiming "not defined in the locked
corpus" against cited contrary evidence; two version-conflict cases were mishandled (g012/g026). Passing gates:
gold_recall_at_10 0.9898, intent_accuracy 0.9831, citation_integrity 1.00, wrong/forbidden evidence 0,
identifier_hallucination_rate 0.00, unhandled product exceptions 0. The FAIL was frozen before exposing
ablation/novel_dev/novel_validation/composer-audit cohorts; novel_validation remains
PRISTINE_FOR_CURRENT_LINEAGE; composer diagnostics within A1 were healthy (35 attempted / 32 accepted) but the
empirical audit is NOT_REACHED. Usage: 383 scientific/evaluation calls, 3,348,432 tokens (runtime 319/2,980,205
incl. qa_generation 69 + qa_composer 38; judge 64/368,227; includes the two 429-failed first attempts).
Integrity: zero post-freeze product changes, zero threshold changes, zero validation-driven tuning, zero holdout
access, zero protected-content leakage, zero mixed identities. No case-level failure inspection was performed;
aggregate analysis only. Normal default remains legacy_question_core; default promotion remains deferred.
NEXT_TASK_RECOMMENDATION = SEPARATELY AUTHORIZED POST-F6-A FAILURE REVIEW / NEW CANDIDATE WORK ONLY.
Report: `evaluation/F6_A_PRERELEASE_VALIDATION_AND_GENERALIZATION_GATE.md`.

## F6-A-R1 offline gate / identity / archival reconciliation record

COMPLETE / PASS / OFFLINE_GATE_IDENTITY_ARCHIVAL_RECONCILED. Zero-model-call evaluator/release-identity/archival
correction at HEAD `e34ecdc`; the F6-A terminal FAIL is preserved. Corrections derived from the canonical
`aggregate_metrics` on the immutable 59-case records: (A) paper_code_dual_source_rate denominator corrected to
the single dual-source-required answered case (rate 0.1633 -> 0.0; FAIL unchanged); (B/C) per-intent gates now
evaluated truly per intent (minimum across 7 intents: recall 0.9583, accuracy 0.9286 — both PASS, replacing the
whole-cohort means); (D) identifier_hallucination_rate denominator corrected to total identifier mentions (121;
rate 0.0; PASS unchanged) with an upper-bound direction bug fixed; (E) failed-gate count derived from the
corrected matrix = 9 (prose/JSON count inconsistency resolved). The archival statement was corrected: case-level
inspection of already-exposed Gold failures occurred for classification after the frozen Stage A1 outcome, with
no repair/rerun following. Usage reconciled: formal F6-A 383 calls/3,348,432 tokens; superseded 9/120 plan
61 calls/339,150 tokens; total during F6-A work 444 calls/3,687,582 tokens. Identity chronology audit: all 59
records completed before the only post-freeze src change (candidate.py verifier corrections); single product
behavior identity; no mixed execution identity. The broad evaluation-infrastructure verification whitelist was
removed (strict source_tree_hash + ancestor-HEAD semantics; offline rescore identity recorded separately).
Original F6-A artifacts remain byte-unchanged; R1 is additive. novel_validation pristine; holdout access 0.
NEXT_TASK_RECOMMENDATION = POST-F6-A EXPOSED-GOLD FAILURE REVIEW / NEW CANDIDATE DEVELOPMENT (NOT AUTHORIZED).
Report: `evaluation/F6_A_R1_OFFLINE_GATE_IDENTITY_ARCHIVAL_RECONCILIATION.md`.

## F6-A-R1-R1 archival and gate-helper consistency repair record

COMPLETE / PASS / R1_ARCHIVAL_AND_GATE_HELPER_CONSISTENCY_REPAIRED. Zero-model-call archival/gate-helper
consistency repair at HEAD `8d43fe8`; the F6-A terminal FAIL is preserved. Corrections: the R1 Markdown
per-intent case counts were corrected to the authoritative values (algorithm_implementation 2, algorithm_theory
8, api 15, installation 12, module_structure 2, troubleshooting 6, usage 14; total 59) matching the corrected
matrix exactly; the dual-source applicable case ID (g060) is now recorded; gate-helper semantics hardened —
zero-count gates with missing measurements are INCOMPLETE (passed=null) and can never silently PASS, the global
intent-accuracy denominator is its own case count (sum of represented per-intent cases), per-intent gates keep
every represented intent visible with FAIL/INCOMPLETE/PASS aggregation semantics, and failed vs incomplete gate
counts are reported separately with release_score excluded as accounting. New authoritative matrix
`evaluation/f6a_gold_gate_matrix_r1_r1.json` (R1 matrix preserved): failed_gate_count = 9 (identical gate list),
incomplete_gate_count = 0, terminal verdict effect NO_CHANGE. F6-A-R1 is fully accepted after R1-R1.
novel_validation pristine; holdout access 0; product changes 0; scientific calls/tokens 0.
NEXT_TASK_RECOMMENDATION = POST-F6-A EXPOSED-GOLD FAILURE REVIEW / NEW CANDIDATE DEVELOPMENT (NOT AUTHORIZED).
Report: `evaluation/F6_A_R1_R1_ARCHIVAL_AND_GATE_HELPER_CONSISTENCY_REPAIR.md`.

## F6-A-R1-R1-R1 per-intent denominator emission repair record

COMPLETE / PASS / PER_INTENT_INTENT_ACCURACY_DENOMINATOR_EMISSION_REPAIRED. Zero-model-call machine-readable
consistency repair at HEAD `5730e92`; R1-R1 remains substantively accepted and only its machine-readable
denominator emission is repaired: `per_intent_intent_accuracy.per_intent_details[*].applicable_denominator` was
`null` for every represented intent because canonical `aggregate_metrics` per_intent entries expose recall
denominators only (no `intent_accuracy_denominator`). The gate helper now derives the intent-accuracy
applicability denominator deterministically from the same immutable records under the canonical measurement rule
(`metric_applicability` override plus non-None `intent_correct` — never hard-coded counts, never unconditionally
case_count); zero measurable cases report denominator 0 and stay INCOMPLETE; recall per-intent denominators keep
canonical behavior. Successor matrix `evaluation/f6a_gold_gate_matrix_r1_r1_r1.json` (schema
f6a-gate-matrix-r1r1r1-v1; R1-R1 matrix preserved) verifies against the prior matrix — every gate datum must
match exactly except the repaired field, any divergence refuses to write. Current denominators 2/8/15/12/2/6/14
(metric values and PASS states unchanged; failed_gate_count = 9, identical gate list; incomplete_gate_count = 0;
dual-source applicable IDs [g060]; release_score 0.8276836158192091; terminal verdict effect NO_CHANGE).
Focused tests: 15 passed (11 prior + 4 new: full/partial/zero measurement and applicability override). The
reconciliation chain F6-A-R1-R1 / F6-A-R1 / F6-A / F6-B / Phase F is closed and unchanged. novel_validation
pristine; holdout access 0; product changes 0; scientific calls/tokens 0.
NEXT_TASK_RECOMMENDATION = POST-F6-A EXPOSED-GOLD FAILURE REVIEW / NEW CANDIDATE DEVELOPMENT (NOT AUTHORIZED).
Report: `evaluation/F6_A_R1_R1_R1_PER_INTENT_DENOMINATOR_EMISSION_REPAIR.md`.

## F6-A-FR1 exposed Gold failure review and candidate development record

COMPLETE / PASS / ROOT_CAUSES_ESTABLISHED_AND_BOUNDED_FIXES_IMPLEMENTED. Zero-scientific-call development task at
HEAD `557327e`: all eight exposed status-mismatch cases (g005/g012/g013/g026/g027/g034/g059/g060) inventoried
before any code change and explained by two generic root causes — RC1: repository display names (PandaRoot/
LuminosityFit/RestgasDetermination) were extracted as requested bare class symbols by the question-grounded
guard while the locked object catalog legitimately lacks repository identities, producing six false
"unsupported requested symbol" refusals whose refusal text contradicted the cited in-repository evidence (all 4
contradictions + the 1 major unsupported claim); RC2: prepositional commit requests ("repo from (requested)
commit SHA") failed the adjacency-based version-repository binding, so the SHA stayed unbound and never reached
the locked-version comparison (g012 degraded to insufficient evidence, g026 silently answered the locked
snapshot). The status-precedence audit confirmed the existing VERSION_CONFLICT > INSUFFICIENT_EVIDENCE >
ANSWERED ordering was correct. Bounded generic fixes: Retriever.is_repository_reference (manifest-driven,
reusing analyzer matching semantics) with the QA guard excluding repository identities, and a bounded
prepositional connector in _has_explicit_version_repository_binding. Nine new regression tests written first
(red before fix, green after) including preserved-refusal controls (uncataloged class tokens, bare-SHA-unbound,
multi-repository-no-bind, conflict-never-degrades). F2-A4/F2-A5 and QAAgent-dependent suites pass unchanged;
the 24 baseline test failures (19 d4_a5 + 5 e2/e1) plus the fastapi collection gap were verified pre-existing
via stash baseline — zero new failures introduced. Product-fix HEAD: `45f14ba`. F6-A remains FAIL; F6-B LOCKED;
Phase F = IN_PROGRESS / POST_F6_A_FAILURE_REVIEW_COMPLETE_NEW_CANDIDATE_DEVELOPED. novel_validation pristine;
holdout access 0; threshold/Gold changes 0; scientific calls/tokens 0.
NEXT_TASK_RECOMMENDATION = NEW F6-A ATTEMPT / NEW CANDIDATE PREREGISTRATION AND FREEZE (NOT AUTHORIZED).
Report: `evaluation/F6_A_FR1_EXPOSED_GOLD_FAILURE_REVIEW_AND_CANDIDATE_DEVELOPMENT.md`.

## F6-A attempt 2 prerelease validation record

COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (Stage A1 fail-fast; A2 ablation, A3 novel_dev,
A4 novel_validation, A5 composer audit NOT_REACHED). Fresh identity: preregistration commit `3f1f16e`,
candidate f6a-rc2-20260913 frozen from the clean preregistration HEAD (`1f32eef`; verify-candidate valid),
zero post-freeze changes. A0 preflight zero-call: Gold m6-benchmark-v2.6 authority valid (6f12d54b), calibration
v3 compatible, selector re-derived (59 IDs, e27ef67a, 21 non-English excluded; count derived, not hard-coded),
Docker/index identities verified, stale roadmap "ten→nine" corrected (619128b), focused tests 314 passed + 68
subtests, FR1 boundary audit clean. Stage A1 run f6a-rc2-gold-formal-full-20260913 (mode=full): 59/59 complete,
zero errors, zero status mismatches — expected_status_accuracy 1.0 (attempt-1 0.8644); all eight FR1-reviewed
cases now match Gold (six former false refusals answered, both version-conflict cases version_conflict).
Six preregistered gates still fail: final_evidence_recall 0.8810 (≥0.90), critical_final_evidence_recall 0.8912
(=1.00), required_source_coverage_answered 0.9592 (≥0.97), paper_code_dual_source_rate 0.0 (g060 answered but no
paper source), critical_answer_point_miss_count 4 (g001/g005/g013/g022), major_unsupported_claim_count 1 (g113).
Release score 0.9463276836158192 (attempt-1 0.8277); failed gates 9→6. Diagnostic comparison only; no gate
changes; no repair during the attempt. Usage (attempt 2): 376 calls / 3,313,651 tokens (runtime 314 / 2,903,448;
judge 62 / 410,203); attempt-1 historical usage not merged. novel_validation = PRISTINE_FOR_CURRENT_LINEAGE (A4
not reached); holdout access 0; F6-B not executed.
NEXT_TASK_RECOMMENDATION = POST-ATTEMPT-2 EXPOSED-GOLD FAILURE REVIEW / NEW CANDIDATE DEVELOPMENT (NOT AUTHORIZED).
Report: `evaluation/F6_A2_PRERELEASE_VALIDATION_RESULT.md`.

## F6-A2-FR1 residual exposed-Gold failure review record

COMPLETE / PASS / RESIDUAL_FAILURES_CLASSIFIED. Zero-scientific-call review-only attribution at HEAD `e3d7809`;
the Attempt-2 terminal FAIL is preserved and shown robust (the PRODUCT_DEFECT class alone keeps
critical_final_evidence_recall ≤ 0.929, critical misses ≥ 2, dual-source 0.0, and major unsupported ≥ 1 even
under fully favorable GOLD/MIXED corrections). Complete contributor sets for all six failed gates were derived
from the immutable records with exact aggregation cross-checks (weighted missing 5.8333/5.3333 over the 49
answered cases reproduces 0.880952/0.891156); committed immutable run receipt records hashes of results.jsonl /
gate_matrix / traces / candidate manifest. Three-layer group attribution (index / candidate pool /
trace-final-vs-answer evidence): of the 10 gate-contributing groups, 7 are selected-but-dropped at the final
answer evidence layer, 2 retrieved-but-not-selected, 1 retrieval miss; zero index-unsatisfiable, zero
selected-but-not-credited (no evaluator defect). Classification: PRODUCT_DEFECT g013/g016/g021/g022/g060/g113
(answer drops already-selected evidence, retrieval miss, unsupported causal claim shipped in the answer);
GOLD_CONTRACT_DEFECT g001/g014 (group selectors lock rendered sphinx forms, rejecting same-content repository
source files); MIXED g005/g011/g020/g044; EXPECTED_STOCHASTIC_VARIATION none stands alone; INCONCLUSIVE none.
Usage reconciliation: qa_generation 67/1,566,586, qa_composer 46/75,888, judge 62/410,203, other runtime
137/1,260,974, embedding 64 calls; product_verifier/embedding tokens NOT_SEPARATELY_RECOVERABLE; total unchanged
376/3,313,651. Provenance nuance documented (freeze bookkeeping populated lineage fields in the committed
preregistration JSON; no contract change; not invalidating; future attempts keep preregistration immutable).
novel_validation pristine; holdout access 0; Gold/evaluator/product code unchanged.
NEXT_TASK_RECOMMENDATION = FORWARD-ONLY GOLD CONTRACT REVIEW, then F6-A2-FR2 / BOUNDED PRODUCT REPAIR AND NEW
CANDIDATE DEVELOPMENT (NOT AUTHORIZED).
Report: `evaluation/F6_A2_FR1_RESIDUAL_EXPOSED_GOLD_FAILURE_REVIEW.md`.

## F6-A2-GR1 forward-only Gold contract adjudication record

COMPLETE / PASS / FORWARD_ONLY_GOLD_CONTRACT_ADJUDICATED_AND_SUCCESSOR_ESTABLISHED. Zero-scientific-call
benchmark-governance task at HEAD `7ad90a9`; adjudication committed before any benchmark change (`88ecbb4`).
Established rule (deterministic lineage/content evidence, independent of Attempt-2 outcomes): the locked sphinx
web snapshot and the frozen PandaRoot repository carry the same documentation with a mechanical whole-tree
mapping sphinx/<Section>/<Page>.html ↔ docs/<Section>/<Page>.rst (path isomorphism; Install_PandaRoot content
check 308/357 word types + 19/40 sampled sentences verbatim + key install commands in both; sphinx Running.html
renders the docs/Running/ toctree with Running_Sequence.rst as its Running-Sequence section source; same
2023-08-25-dev generation). Dispositions: g001 BROADEN (repo installation-doc source selectors added; p1
reworded — the commit-specificity statement is not entailed by the install query) / g005 p1 REVISE_ANSWER_POINT_SCOPE
(reworded to the documented container development workflow; the develop-vs-run contrast does not exist anywhere
in the required 6,153-char evidence document) / g011 BROADEN / g014 BROADEN (incl. Running_Sequence.rst) /
g044 KEEP_AS_IS (the pflueger pages 57/58/62 lock is an intentional source-specific theory contract; li_2026
equivalence not established; broadening would be motivated only by Attempt-2's answer choice). Bounded
consistency sweep: same-pattern path-form groups corrected additively (g008.e2, g013.e1/e2, g015.e1, g016.e1/e2,
g022.e2, g089.e1, g101.e1/e3, g106.e1, g109.e1; original sphinx selectors preserved everywhere); title-form
groups without demonstrated failure recorded KEEP_AS_IS (no redesign). Successor benchmark m6-benchmark-v2.7
created (`evaluation/benchmarks/v2_7/`; dataset SHA 4dcc9d06…; 120 questions; split/status counts unchanged;
13 changed cases: g001/g005/g008/g011/g013/g014/g015/g016/g022/g089/g101/g106/g109; patch + change report +
manifest with product-validator green: structurally_valid, official_ready, zero unmatched evidence groups, all
24 new repo-docs selectors index-satisfied). Successor calibration phase_b_t3_product_language_scope_v4
mechanically carries v3 assignments, binds v2.7 SHA, compatibility verified; formal-English selector re-derived:
59 IDs, sha e27ef67a…, membership identical to v3. Attempts 1 and 2 remain evaluated against v2.6; Attempt-2
FAIL unchanged; no retroactive rescoring. novel_validation pristine; holdout access 0; product/evaluator code
unchanged; scientific calls/tokens 0.
NEXT_TASK_RECOMMENDATION = F6-A2-FR2 / BOUNDED PRODUCT REPAIR AND NEW CANDIDATE DEVELOPMENT (USING v2.7 AS THE
STABILIZED GOLD AUTHORITY) (NOT AUTHORIZED).
Report: `evaluation/F6_A2_GR1_FORWARD_ONLY_GOLD_CONTRACT_ADJUDICATION.md`.

## F6-A2-GR1-R1 Gold successor provenance reconciliation record

COMPLETE / PASS / UNJUSTIFIED_V2_7_DELTA_RETIRED_FORWARD_ONLY. Zero-scientific-call governance reconciliation at
HEAD `9c9593e`; original GR1 adjudication and v2.7 creation commit history preserved untouched. Issue A
(g016.e1): the v2.7 change set included a title-form group that had never received the independent adjudication
the GR1 rule requires — independent deterministic adjudication now REJECTS the delta: docs/EventGenerators/
DPMGenerator.rst is a 96-byte doxygen stub (single .. doxygenclass:: PndDpmDirect directive; 3 indexed objects /
165 chars / 7 word types) whose rendered sphinx page (3596 chars) is generated from code annotations, not from
the rst; content equivalence required by the GR1 rule is absent, and the file would not have been added had
Attempt 2 never failed g016. Issue B (g022.e2): confirmed a valid path-form pair and part of the original
bounded sweep; the omission was bookkeeping-only (its 9,838-byte substantive rst extension is retained). The
exact path-form set was reconstructed deterministically from v2.6: 12 pairs (primary g014.e2 + g008.e2,
g013.e1/e2, g015.e1, g016.e2, g022.e2, g089.e1, g101.e1/e3, g106.e1, g109.e1); g016.e1 is recorded separately
as an independently adjudicated title-form case with a rejected delta. Open finding recorded outside task
authority: docs/Tools/PndMasterTasks/PndMasterRunSim.rst (105 bytes) is likewise a doxygen stub added by the
v2.7 sweep to five groups — routed to the next benchmark-governance task (whereas docs/Running/Macros.rst is an
include-aggregation stub whose targets live inside the corpus and is retained). Forward-only successor
m6-benchmark-v2.8 created from v2.7 (dataset SHA 67c992ce…; only governance repair = removal of the unjustified
g016.e1 repo selector; changed case g016 only; product validator green). Calibration
phase_b_t3_product_language_scope_v5 mechanically carried from v4, bound to v2.8, compatible; selector
re-derived 59 IDs / e27ef67a…, membership identical to v3/v4. Authority: v2.6 = historical for Attempts 1/2;
v2.7 = historical provisional successor, not used for any scientific release attempt; v2.8 = stabilized
forward-only authority for future attempts. Attempt-2 FAIL unchanged; no retroactive rescoring.
NEXT_TASK_RECOMMENDATION = F6-A2-FR2 / BOUNDED PRODUCT REPAIR AND NEW CANDIDATE DEVELOPMENT (USING v2.8 AS THE
STABILIZED GOLD AUTHORITY) (NOT AUTHORIZED).
Report: `evaluation/F6_A2_GR1_R1_GOLD_SUCCESSOR_PROVENANCE_RECONCILIATION.md`.

## F6-A2-GR1-R2 doxygen-stub evidence-selector cleanup record

COMPLETE / PASS / REMAINING_POINTER_STUB_SELECTORS_RETIRED_FORWARD_ONLY. Zero-scientific-call benchmark-governance
cleanup at HEAD `deab588`; audit committed before benchmark mutation (`0468852`). Mechanically derived universe
(v2.6->v2.7 repo-docs selector set-difference): 22 (case,group,path) triples over 11 unique paths, of which
docs/EventGenerators/DPMGenerator.rst (g016.e1) was already retired by GR1-R1 — inherited v2.8 universe 21 triples /
10 paths. Every underlying file read in full and classified: CONTENT_BEARING_DOCUMENT — Install_Developers.rst
(6029B), Install_PandaRoot.rst (5886B), MasterTasks.rst (10878B), Running_Sequence.rst (1746B),
tut_02_02_analysis_pid.rst (9838B); INCLUDE_AGGREGATOR_WITH_CLOSED_CORPUS_TARGETS — Installation.rst (523B toctree,
targets inside docs/Installation/), Macros.rst (331B include chain, all four targets verified IN CORPUS), Running.rst
(4069B toctree + own overview text), PndMasterTasks.rst (709B introduction + 9-target toctree verified IN CORPUS);
DOXYGEN_OR_EMPTY_POINTER_STUB — docs/Tools/PndMasterTasks/PndMasterRunSim.rst (105B, doxygenclass pointer) removed
forward-only from g013.e1/g013.e2/g015.e1/g016.e2/g089.e1 (groups retain sphinx/code/README/valid repo-doc
selectors; none empty; g013 special care honored — Macros.rst and MasterTasks.rst kept). Forward-only successor
m6-benchmark-v2.9 created from v2.8 (dataset SHA eaacd3ed…; changed cases g013/g015/g016/g089; product validator
green). Calibration phase_b_t3_product_language_scope_v6 mechanically carried from v5, bound to v2.9, compatible;
selector re-derived 59 IDs / e27ef67a…, membership identical to v3/v4/v5. Authority: v2.6 = Attempts 1/2 historical;
v2.7 and v2.8 = historical provisional successors (never used scientifically); v2.9 = stabilized future Gold
authority. Attempt-2 FAIL unchanged; no retroactive rescoring. novel_validation pristine; holdout access 0;
product/evaluator code unchanged; scientific calls/tokens 0.
NEXT_TASK_RECOMMENDATION = F6-A2-FR2 / BOUNDED PRODUCT REPAIR AND NEW CANDIDATE DEVELOPMENT (USING v2.9 AS THE
STABILIZED GOLD AUTHORITY) (NOT AUTHORIZED).
Report: `evaluation/F6_A2_GR1_R2_DOXYGEN_STUB_SELECTOR_AUDIT.md`.

## F6-A2-FR2 bounded product repair and new candidate development record

COMPLETE / PASS / RESIDUAL_PRODUCT_MECHANISMS_REPAIRED_AND_NEW_CANDIDATE_DEVELOPED. Zero-scientific-call
development task at HEAD `7411caa` against the stabilized m6-benchmark-v2.9 authority (dataset eaacd3ed…,
calibration v6 compatible, selector 59 IDs e27ef67a… re-verified; Gold/evaluator/thresholds untouched). R0 rebase
confirmed all eight prior residual targets still applicable. Two generic mechanisms repaired (test-first, red
before green): (A) source-obligation evidence retention — obligations gated retrieval sufficiency only, so an
answer whose claims never cited the obligated source type silently dropped already-selected evidence at the
final projection (g013/g016/g022 documentation; g060 paper → dual-source 0.0); new
_augment_source_obligation_evidence adds at most one evidence-bound anchor claim per uncovered required source
type, only for selected citation-eligible evidence sharing a question domain anchor, asserting only what the
evidence shows (mirrors _augment_planned_locators). (D) unsupported-claim revision discipline — _revise re-entered
revised claims for a second model verification where the same materially unchanged text could flip to supported,
resurrecting a known-unsupported claim (g113); _revise now drops an identical-normalized-text restatement of a
claim just found unsupported, while substantively narrowed revisions pass. Two clusters legitimately deferred:
pool→final selection diversity (g011/g020; whole-product ranking reshaping unmeasurable without scientific calls)
and genuine retrieval miss (g021; safe generic recall repair would recreate retired shortcut territory).
Verification: 6 new ResidualRepairTests (positive + controls), test_qa + test_retrieval 269 passed + 50 subtests;
QAAgent-dependent suites show exactly the pre-existing baseline failures (19 d4_a5 + 5 e2/e1) — zero new
regressions. PROMPTS untouched. novel_validation pristine; holdout access 0; Gold/novel/holdout scientific
activity 0.
NEXT_TASK_RECOMMENDATION = F6-A ATTEMPT 3 / NEW CANDIDATE PREREGISTRATION AND FREEZE (bound to m6-benchmark-v2.9
and calibration v6) (NOT AUTHORIZED).
Report: `evaluation/F6_A2_FR2_BOUNDED_PRODUCT_REPAIR_AND_NEW_CANDIDATE_DEVELOPMENT.md`.

## F6-A2-FR2-R1 source-obligation boundary repair record

COMPLETE / PASS / SOURCE_OBLIGATION_PUBLIC_CONTENT_AND_COVERAGE_BOUNDARIES_REPAIRED. Zero-scientific-call bounded
correction at HEAD `223a1e2`; the initial FR2 closeout above is historical and corrected by this record (Cluster D
preserved; B/C defer preserved). Rejected Cluster-A behavior retired: `_augment_source_obligation_evidence`
synthesized public provenance-meta claims ("The cited paper at X documents Y.") — bookkeeping, not user-facing
content — letting source types survive final-evidence projection through meta-claims, ran in coverage modes against
the F2-A3-R1 contract, and used a divergent paper/documentation/code-only classifier. Corrected design: the augment
mechanism is removed entirely; question-grounded multi-source obligations are expressed through the legacy
answer-requirement contract — `source_role_grounding` (multi-source plans only) instructs grounding each part of the
explanation in the source kind that actually supports it (provenance-only statements explicitly forbidden);
`_deterministic_missing_requirement_ids` backstops it via cited-evidence coverage of every required kind;
`_requirement_evidence` maps required kinds' selected evidence into the legacy revision payload so the model writes
the substantive grounded claim and the semantic verifier stays authoritative. Source-type classification centralized
into `_evidence_source_types` (exact per-item extraction of sufficiency semantics incl. readme/workflow/channel
kinds) with `_sufficiency` refactored onto it. Coverage firewall regression-locked: shadow_e1_v2/runtime_e1_v2
generation payloads carry `answer_requirements = []` (F2-A3-R1 preserved). Focused verification: new
SourceObligationBoundaryTests (legacy prompt carries the requirement; coverage prompts do not; no synthesized
provenance claims; backstop positive + control; Cluster-D preservation) — red before green; test_qa + test_retrieval
274 passed + 52 subtests; QAAgent-dependent suites show exactly the pre-existing baseline failures (19 d4_a5 +
5 e2/e1) — zero new regressions. Product files: qa.py, test_qa.py; prompts.py untouched. New candidate-development
HEAD `d323f79`; candidate frozen = false; Attempt 3 preregistered/executed = false. novel_validation pristine;
holdout access 0; Gold/evaluator/thresholds unchanged; scientific calls/tokens 0.
NEXT_TASK_RECOMMENDATION = F6-A ATTEMPT 3 / NEW CANDIDATE PREREGISTRATION AND FREEZE (bound to m6-benchmark-v2.9
and calibration v6) (NOT AUTHORIZED).
Report: `evaluation/F6_A2_FR2_R1_SOURCE_OBLIGATION_BOUNDARY_REPAIR.md`.

## F6-A Attempt 3 preflight hold record

HOLD / PRE_RELEASE_PRECONDITION_NOT_MET. Zero-outcome preflight at HEAD `52713da`; scientific/evaluation execution
never started (calls/tokens 0). Verified clean: product-behavior lineage d323f79 (d323f79..HEAD touches docs/
artifacts only — zero product drift), product boundary audit clean (no synthetic source_obligation claims, no Gold
case IDs, production mode legacy_question_core), Gold v2.9 identity (dataset eaacd3ed…, official_ready,
structurally_valid), selector re-derived 59 IDs / e27ef67a… against v2.9+v6, Docker/index identities match, focused
tests 325 passed + 70 subtests (zero regressions). Two preregistration blockers discovered, both evaluation-
infrastructure authority-binding gaps from the GR1 chain: (1) candidate freezer hard-binds BENCHMARK_DIR/
BENCHMARK_VERSION to v2_6/m6-benchmark-v2.6 — _current_manifest reads v2_6's gold_questions.yaml and
manual_adjudications.yaml (absent in v2_9) — so any frozen candidate would bind v2.6, conflicting with the required
v2.9 binding; (2) load_product_language_calibration's successor chain stops at v3 — v4/v5/v6 exist on disk but the
default-loaded calibration (v3) is incompatible with v2.9, so freezer product-scope identity would raise and the
pipeline cannot select v6. Per the Attempt-3 protocol A0 is validation, not development (product files and
Gold/calibration may not change during Attempt 3); no repair performed, no preregistration, no freeze. Stages
A1–A5 NOT_REACHED; novel_validation = PRISTINE_FOR_CURRENT_LINEAGE. Attempt-1/2 historical FAILs preserved.
NEXT_TASK_RECOMMENDATION = GOLD-9 AUTHORITY BINDING INFRASTRUCTURE RECONCILIATION (freezer binding to v2.9 incl.
manual-adjudications disposition; calibration loader successor chain to v6), then re-run Attempt-3 preflight
(NOT AUTHORIZED).
Report: `evaluation/F6_A3_PRERELEASE_VALIDATION_RESULT.md`.

## GOLD-9 authority binding infrastructure reconciliation record

COMPLETE / PASS / RELEASE_AUTHORITY_CHAIN_RECONCILED. Zero-scientific-call bounded reconciliation at HEAD `8403369`
(after the Attempt-3 preflight HOLD above; that HOLD is preserved as the historical terminal result of that
preflight). Root causes confirmed and repaired: (1) candidate freezer hard-bound v2_6/m6-benchmark-v2.6 — replaced
by the shared resolver `evaluation.newest_signed_exposed_gold_dir` (mechanical discovery of
evaluation/benchmarks/v2_N, qualified by manifest-internal consistency + official-ready/structurally-valid, highest
version wins; freezer and evaluator now bind the same authority); (2) `default_gold_dataset_path` walked a
hand-written v2_6->v2_2 chain — now resolver-first with the historical chain preserved as old-checkout fallback;
(3) `load_product_language_calibration` successor chain stopped at v3 — replaced by mechanical discovery of the
newest `phase_b_t3_product_language_scope_vN` artifact (v6), with `newest_product_language_calibration_path` shared
so `_product_scope_identity` hashes the same resolved artifact (v6 content/v3 hash mismatch eliminated);
(4) manual-adjudication disposition: v2.9 carries no manual_adjudications.yaml and its signed manifest+dataset is
the authority — the freezer dependency is optional (hash None recorded when absent; v2.6 artifacts untouched; no
convenience copy). Cross-layer consistency demonstrated: resolver/default-dataset-path/freezer identity/product-
scope identity all resolve Gold v2.9 (eaacd3ed…) + calibration v6 (fe56d4ca…) + formal selector 59 IDs
(e27ef67a…) without fallback ambiguity. Focused tests: freezer/identity/gate suites 53 passed + 18 subtests;
test_qa + test_retrieval 274 passed + 52 subtests — zero new regressions; product QA behavior untouched.
Historical outcomes preserved (Attempt-1/2 FAIL under v2.6; Attempt-3 HOLD as the terminal result of that
preflight; F6-B LOCKED; novel_validation pristine).
NEXT_TASK_RECOMMENDATION = F6-A ATTEMPT 3 / RE-RUN ZERO-OUTCOME A0 PREFLIGHT, THEN PREREGISTER AND FREEZE ONLY IF
ALL PRECONDITIONS PASS (NOT AUTHORIZED).
Report: `evaluation/GOLD_9_AUTHORITY_BINDING_INFRASTRUCTURE_RECONCILIATION.md`.

## Historical E3-A0 architecture contract closeout

COMPLETE / PASS / MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT_ESTABLISHED.
Static architecture and dependency contract only; zero product code modified, zero scientific
validation or evaluation calls. Reconstructed current QA graph from source (`src/panda_agent/qa.py`);
formally distinguished pre-answer sufficiency-based targeted retrieval from post-verify semantic
missing-point targeted retrieval. Reconciled historical C8 dependency: preserved C8 DEFERRED /
INSUFFICIENT_NATURAL_TARGETED_APPLICABILITY without false validation claims; reused C8 candidate-pool
design principles (object_id identity, per-pass/channel provenance, best-rank RRF, no BOTH bonus,
lexicographic tie-breaking, unchanged selector/budgets). Established strict question-derived trigger
and retrieval objective (question + missing point texts in question order; forbidden evaluator/gold/reason
signals). Contract specifies dedicated E3 budget (missing_point_retrieval_count <= 1) and bounded
recovery (`verify -> optional E3 -> revise -> verify -> finalize`; never answer again) while preserving
configured pre-answer budget (`policies.max_targeted_retrievals`). Contract proposes resolution for
supported-claim citation displacement via internal immutable retained-supported-claims snapshot
(exact original claim text, citation IDs, point mappings) and retained-support evidence ledger
(claim-scoped to unchanged supported claims, preserving original evidence IDs and payloads, normal
verifier recheck without waivers, public QAResult shape unchanged) without pinning selection or inflating
the configured final evidence limit (currently 12; policy-selected). Defined minimal A1 implementation
seam in `qa.py` / `retrieval.py` and focused T1-T20 test contract (local test IDs, none executed in A0).
All PANDA scientific/evaluation calls and tokens are zero; zero product or test code modified.
Report: `evaluation/E3_A0_MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT.md`.

## Historical QA-M1 maintenance closeout

COMPLETE / PASS / GENERIC_CLAIM_SANITIZATION_REPAIR_VALIDATED. Shared external
template sanitization now consumes balanced wrappers and retains payload meaning;
requested identifiers remain intact. Focused T0: 14 tests and 2 subtests passed.
Offline scan: 290 initial/revision claim snapshots, 2 intended changes (g029/g059),
288 unchanged and zero unexpected collateral changes. All scientific/provider
calls and tokens are zero. Historical G11 FAIL/preferences unchanged; no activation.
E2 core remains complete with promotion deferred. Historical baseline prior to E3-A0
contract establishment. Report:
`evaluation/QA_M1_GENERIC_CLAIM_SANITIZATION_REPAIR.md`.

## Historical E2-LR1 lifecycle reconciliation

E2 core implementation and targeted validation are sufficient for further
architecture development; default-promotion acceptance is not met. This is
lifecycle completion, not E2 scientific PASS or a historical rescore. The G11
review recommendation is preserved below but its immediate combined A3-R4 task
is superseded, never executed. Shared sanitizer maintenance is QA-M1, not an E2
reopening requirement and not an architectural E3 blocker.

E3 is architecturally unblocked on explicitly selected runtime_e1_v2 or the
appropriate experimental/shadow path. It remains NOT_STARTED and unauthorized.
Normal legacy QA retains existing retrieval behavior; future missing-point
retrieval must not silently enter ordinary QA. No behavior is implemented here.
Promotion and rubric redesign are deferred until a materially broader Phase-E
candidate exists, naturally after E3 or another explicit Phase-E completion
decision. The prior 28-case/two-judge/materiality proposals are design ideas,
not active gates. No future experiment is defined or frozen here.

Recommended order: QA-M1 maintenance, then E3 architecture. Neither is authorized.
See `evaluation/E2_POST_A3_LIFECYCLE_RECONCILIATION.md` for evidence and boundaries.

## Historical E2-A3-R3-R1-FR1 static review closeout

COMPLETE / PASS / PRODUCT_REPAIR_AND_GATE_REDESIGN_RECOMMENDED.
Historical G11 FAIL and 1/11/2 remain immutable. Exact g001 public wording omits
commit-specific scope (not merely a SHA); support/coverage flags do not establish
all Gold clauses. g029 optional boundary elaboration differs, and its malformed
type phrase is exactly reproduced by the shared pre-existing identifier sanitizer;
g059 supplies a second compatible transform. Narrow A1 shared sanitization repair
is justified, without claiming a common g001/g029/g002 runtime defect. Future gate
redesign should separately audit explicit obligations and material noncritical loss.
No current gate change, repair, rejudge, waiver or activation. Offline review only:
all scientific calls/tokens zero; abstract AGY review separately reported.
Report: `evaluation/E2_A3_R3_R1_G11_FAILURE_REVIEW.md`.
Artifact: `evaluation/e2_a3_r3_r1_g11_failure_review.json`.
The prior closeout's metrics below remain frozen; the new Gold-clause observation
is not a rescore of those gates. Next R4 requires separate authorization.

## Historical E2-A3-R3-R1 scientific closeout

COMPLETE / FAIL / G11. Recovery g059/g047/g001 completed all six fresh arms and
three blinded judgments with zero terminal infrastructure failures or case replays.
Exactly eleven original complete pairs plus three fresh recovery pairs establish
14/14 QA outputs per arm and 14 judgments. Correct status and supported answers
are 14/14 per arm; new false answers/refusals and critical regressions are zero.
Quality is 1 better / 11 equivalent / 2 worse: new g001 plus historical g029 fail
G11's unchanged <=1 worse and >=13 non-worse requirements. All other G1-G13 gates
PASS with complete authority. Coverage is complete for 10/10 applicable answered
runtime outputs, decomposition valid 14/14, and no new registered verifier category
or invalid Sphinx citation is observed. G12 = (75 - 61)/14 = 1.0.

Protocol: `3a93f081a77e8bb507b14729a981dc1fa9c1f449`.
Raw: `0bc039d39211540843863d73ef9dd2be430087cd`.
Judged: `5f260a3fa92ade82528825669e0f5360fe1bc34e`.
Result: `evaluation/e2_a3_r3_r1_activation_completion_result.json`.
Report: `evaluation/E2_A3_R3_R1_INFRASTRUCTURE_RECOVERY.md`.
Focused evaluator tests: 32 passed before freeze. Recovery usage: 44 logical
operations, 38 returned responses, 40 adapter requests, 475016 observable tokens.
Embedding tokens and monetary cost unavailable. Original historical usage and
failed-attempt expenditure remain separately preserved. No product change,
activation, rejudge, P6 waiver, or automatic next task. Default remains legacy.

## Historical E2-A3-R3 scientific closeout

INCONCLUSIVE: three connection timeouts (g059 both arms, g047 runtime) and
one provider 429 (g001 legacy) prevent three authoritative pairs. All 28 attempt
records are terminal; successful QA outputs 12/14 per arm. Fourteen judgment
records include eleven actual authoritative judgments and three unscoreable
pairs skipped without a judge call. No failed-case replay or rejudge.

F1-F10 passed; focused evaluator/static tests 30 passed. The fixed 14-question
cohort excludes the six R2 cases, with ten answered and four refusal controls.
On eleven scoreable pairs: correct statuses 11/11 each, quality 1 better / 9
equivalent / 1 noncritical worse, support 11/11 each, critical regression 0.
No new registered runtime verifier category or recorded invalid Sphinx citation.
Failed-arm diagnostics are incomplete: these observations are not a complete
activation PASS. G1/G7/G9/G11 remain false due to missing authority; no observed
product failure overrides the infrastructure INCONCLUSIVE classification.

Protocol: `0a276a40968ed67fb784c37676d172314fb1210d`.
Raw: `6d760be1eae1e803d8f6c4ff6b374a13dbed4713`.
Judged: `77388ec9c2564cce82d0db24ef97a15da62d4779`.
Result: `evaluation/e2_a3_r3_runtime_activation_result.json`.
Usage: 186 logical operations, 154 returned responses, 163 adapter attempts,
2,141,683 observable tokens; embedding tokens and monetary cost unavailable.
Overhead diagnostic 15/11=1.363636 on scoreable pairs; full 14-pair mean unavailable.
All-record generation consumption is 56 legacy/65 runtime and is not a complete
paired overhead estimate. Product/default unchanged, no activation commit.
Historical A3/R1 FAIL, R2 PASS and no-P6-waiver remain. E3 NOT_STARTED.
Further infrastructure/reassessment work is not authorized automatically.

## Historical E2-A3-R2 scientific closeout

S1-S13 and P1-P11 all PASS. Historical selected Sphinx reconciliation:
144 occurrences = 106 complete retained + 38 ineligible excluded; three historical
invalid citation edges excluded from admission; all 18 historical final edges
remain complete. Production repair is answer/revision admission only, including
the revision requirement-evidence input; retrieval bundle and verifier unchanged.
126 focused T0 tests passed with zero scientific calls before candidate freeze.

Six fresh legacy/runtime pairs and six blinded judgments completed. Expected
status and supported judgments 6/6 per arm. Invalid Sphinx public citations 0;
incomplete-web review errors 0; new runtime verifier categories 0. Runtime
better/equivalent/worse 1/5/0; critical regressions 0. g002 has the same initial
SIMPATH/bin/cmake rejection in both arms, clean final reviews, complete runtime
coverage and equivalent supported answers. Historical P6 FAIL is preserved,
with no waiver or product tuning. Overhead 8/6 = 1.333333 generation calls;
runtime decomposition 6, revisions <=1, post-verify retrieval 0.

Candidate: `85ec7e353a65c31f0f1b491d5e00bad59b044c58`.
Raw freeze: `12ae8138bd8268e9246d4d477a1d9f07cafc854f`.
Judged freeze: `5992cd1e7b354583cd395fd7e7552f509ce03b75`.
Result: `evaluation/e2_a3_r2_targeted_revalidation_result.json`.
Usage: 90 logical operations, 78 returned responses, 78 adapter attempts,
1,270,945 observable tokens; embedding tokens and monetary cost unavailable.
No activation: default legacy_question_core, E2 IN_PROGRESS, E3 NOT_STARTED.
Recommend R3 independent activation reassessment, execution NOT AUTHORIZED;
no future activation cohort or threshold is established here.

## Historical E2-A3-R1-FR1 failure review closeout

P2 ownership: R3 citation-eligible evidence admission. The offending whole-page
Sphinx object intentionally has no section_path; its headings remain in source
metadata. It should not be offered as public claim citation under the established
URL/date/heading contract. Across A3/R1, 27 distinct public-candidate Sphinx
citation edges include 24 complete and 3 empty-section edges; final published
edges are 18/18 complete. Fragment relaxation changes zero decisions.
P6: no generic product repair justified. Spack/CVMFS are optional details, absent
in both observed runtime outputs and present in both legacy outputs; this limited
repeat evidence does not prove a broad required-content defect. Historical P6
FAIL remains valid; no waiver. Recommend bounded P2 repair and separately
preregistered prospective evidence. Scientific calls/tokens 0/0.
Report: `evaluation/E2_A3_R1_P2_P6_FAILURE_REVIEW.md`.

## Historical E2-A3-R1 closeout

S1-S12 passed, with exactly one historical rejecting-token delta. Five fresh
legacy/runtime pairs and five blinded judgments completed. Prospective FAIL:
P2 g027 added an initial incomplete web citation; P6 g002 runtime was judged
worse (noncritical). g112 repair sentinel passed; expected-status accuracy was
5/5 in both arms; better/equivalent/worse = 2/2/1. Mean additional generation
adapter calls = 1.0; runtime decomposition one/case; revisions <=1; no postverify
retrieval. Normal default remains legacy_question_core. No activation or rerun.
Usage: 78 logical operations, 68 returned model responses, 68 adapter attempts,
1,369,992 observable tokens; embedding tokens and monetary cost unavailable.
Report: `evaluation/E2_A3_R1_IDENTIFIER_NORMALIZATION_REPAIR.md`.

## Historical E2-A3-FR1 failure review closeout

Static/offline review confirmed V1 verification false rejection: the g112 cited
source contains PndLmdDataReader::fillData, while the rejecting tokenizer retains
the trailing prose colon. Across 56 frozen executions / 157 distinct claim
snapshots, the narrow counterfactual changes one identifier rejection (g112
runtime); existing g110/g002 unsupported-token controls remain rejected.
Decision: REPAIR_JUSTIFIED. Future scope is only deterministic rejecting-token
normalization; recommend T0, full frozen impact scan, and five fresh paired
prospective cases under a new candidate. No repair or activation was implemented.
Scientific calls/tokens: 0/0; one separate abstract AGY review completed.
Report: `evaluation/E2_A3_Q7_FAILURE_REVIEW.md`.

## Historical E2-A3 closeout

Complete bounded execution: retrieval 24/24, paired QA 56/56, blinded judgments
28/28. Gold expected-status accuracy remained 14/16 in both arms. Runtime was
better/equivalent/worse in 6/21/1 pairs, with zero critical user-visible regressions.
All gates passed except Q7: g112 added an unsupported-identifier review error.
The existing revision removed that error, but the preregistered gate includes
initial reviews. No default activation or repair occurred. Novel validity,
evaluability, and final completeness were each 12/12; pair09 retained three points.
Scientific usage: 526 logical operations, 442 returned model responses, 446
adapter attempts, 5,387,384 observable tokens; embedding tokens and monetary cost
are unavailable. Focused pre-freeze tests: 107 passed; offline rescore reproduced
FAIL/Q7. Report: `evaluation/E2_A3_RUNTIME_ACTIVATION_REGRESSION.md`.

## Historical E2-A2 closeout

Frozen targeted exposed validation passed all N1-N6 and D1-D4 gates.
Natural applicability: rep1 12/12, rep2 12/12. Mapping precision 74/79,
recall 74/75, exact claim mapping 68/74; coverage precision/recall 56/56.
Controlled: 11/12 eligible, one non-isolatable baseline; detection, missing-set
precision and exact-set accuracy each 11/11. Structural/infrastructure failures 0.
Residual mapping errors: five extra edges and one missed edge; no repairs made.
Exact serialized recomputation matches. The frozen repeat-score CLI has a
nonfatal tuple/list equality limitation; it remains unchanged and is documented
in the report. Scientific execution and independent judging completed normally.
Scientific usage: 217 logical operations, 193 returned responses (169 generation,
24 embedding), 2,090,933 returned token-counter total. Embedding tokens unavailable.
Same-model-family independent-role blinded judge; no representative or production
readiness claim. Preregistration `78969ceee0bd316e7a9632440c175bcdac04f3bc`;
natural raw `ee8049e760c9ef46d2096fd91ff6e5e9716dcde8`; judgments
`3f50f15c6359145dd77acacf715a38e660bd3b6f`; controlled manifest
`a9368e5404c164b9b32a72617e9b664ec241e2ef`.
Report: `evaluation/E2_A2_TARGETED_CLAIM_MAPPING_VALIDATION.md`.
No E2-A3, production activation, E3, compatibility removal, D4 or Phase-F continuation.

## Historical E1-C1 closeout

Exact historical English novel_dev pairs07-12:12 cases,6 pairs,28 references.
All12 valid, recall28/28, precision28/28, under/over0, exact count12/12,
semantic-complete pairs6/6, hidden prerequisites0. Pair09/n020 base and paraphrase
both matched3/3 with3 predictions and zero extras. All strict gates and sentinel PASS.
Scientific usage:12 decomposition calls/16417 tokens plus12 judge calls/13682 tokens;
24 returned model calls and30099 tokens total. Other pipeline stages zero.
Focused tests30/30 and independent post-run reconciliation passed. AGY static review
crashed on local lock EPERM without a result; its usage is unavailable, not zero.
The exposed confirmation supplements fresh synthetic R2 evidence. E1 closure is
bounded to shadow question decomposition; representative generalization, production
integration and compatibility replacement are not established. No extra confirmation,
E2/E3 execution or production activation occurred. Historical A2 FAIL and R2 PASS remain.

## Historical checkpoint — E1-R2 scientific closeout

The approved amended cohort passed all eight frozen primary gates: 24/24 valid,
54/54 semantic reference recall, 54/54 prediction precision, 0 under/over-decomposed
cases, 24/24 exact count, 12/12 semantic-complete pairs, zero hidden prerequisites.
All 24 judgments were scoreable. Facet taxonomy is diagnostic only; two predictions
omitted labels and nine labeled semantic matches differed from reference labels.

All 24 raw decomposition records were committed before judging. Frozen inputs and
approved case content remained unchanged. Scientific usage: decomposition 24 logical /
24 returned model calls / 30056 tokens; judge 24 / 24 / 24885 tokens; total 48 calls /
54941 returned tokens. Analyzer, embeddings, reranker, retrieval and QA calls were zero.
Focused pre-freeze tests passed 27/27; offline validation and independent post-report
count/usage/provenance reconciliation passed. No scientific retry or next task occurred.

Report: `evaluation/E1_R2_SEMANTIC_ANSWER_POINT_REVALIDATION.md`.
Result: `evaluation/e1_r2_semantic_answer_point_revalidation_result.json`.
This is targeted prospective synthetic exploratory shadow evidence, not representative
PANDA generalization or production readiness. E1-A2 remains FAIL. E1 awaits separately
authorized E1 CLOSURE / SCOPE REVIEW; E2/E3 remain NOT_STARTED.

## Historical checkpoint — E1-R2 preparation

The user authorized E1-R2. The repaired v2 implementation is committed at the
starting HEAD. A fresh 24-question / 12-pair English synthetic exploratory cohort
with 54 explicit reference obligations, a separate v2 semantic judge/scorer,
raw-before-judge Git freeze boundaries and targeted fake tests are prepared.

Human review of generated questions, reference obligations, paraphrase equivalence
and exploratory domain relevance was explicitly approved by Jinxin Li, recorded at
2026-09-08T13:48:52+02:00, for amended cohort commit
`4cd0305c53541bcba75c00fbf935d87c63ba3069`. The manifest is
APPROVED_FOR_PREREGISTRATION; preregistration freeze remains pending. No scientific
decomposition/judge calls occurred; no scientific metrics or PASS/FAIL verdict exist.
Scientific verification status = INCONCLUSIVE / NOT_EXECUTED_PENDING_PREREGISTRATION_FREEZE.
One completed AGY static protocol review is separate: its provider call/token totals
are unavailable. Its review is not human approval.

Review package: `evaluation/E1_R2_COHORT_REVIEW.md`.
Protocol: `evaluation/E1_R2_REVALIDATION_PREREGISTRATION.md`.
E1-A2 remains FAIL; E1 remains REVALIDATION_PENDING. E2/E3 and production activation
remain out of scope. A synthetic exploratory PASS would require an explicit E1
closure/scope decision, not automatically establish representative generalization.

## Historical checkpoint — E1-R1 shadow repair closeout

Decomposition prompt 2.0.0 / schema e1.question_decomposition.v2 implements the semantic-obligation contract in the explicit shadow seam. Points use type-independent question-order IDs (`point.N`). Optional facet metadata cannot affect validity of otherwise valid semantic points, ordering or identity; unusable metadata is omitted. The prompt teaches independently satisfiable explicit obligations, with no lexical splitting heuristics. Question-only input, 1–5 bound, exact spans and diagnostic ambiguity remain.

V2 focused fake tests: 32 passed. A directly relevant frozen E1-A2 test run against v2 returned 23 passed / 1 failed because its fake judge still requires v1 IDs; the same unmodified tests passed 24/24 with the original preregistered v1 module loaded in-memory. This version mismatch remains explicit; historical scientific evidence was not rerun or changed. `git diff --check` passed. All live calls and token usage were zero.

E1-R1 PASS covers implementation/T0 only; real-model granularity and semantic quality remain unmeasured for v2. Normal QA, `question_core`, legacy completeness requirements, production prompts, E2/E3 and retrieval remain unchanged. E1-A2 retains its original FAIL. E1-R2 requires separately authorized prospective validation with a fresh acceptance cohort.

Report: `evaluation/E1_R1_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIR.md`.

## Historical checkpoint — E1-AR architecture review closeout

E1's primary abstraction is an independently satisfiable explicit question obligation whose omission can be independently detected. The revised architecture makes `facet_type` optional diagnostic metadata, not semantic correctness, a primary acceptance gate, or a dependency of point ordering/identity. Future E1-R1 should assign type-independent question-order IDs, retain exact question support spans and diagnostic ambiguity, and teach generic obligation atomicity without lexical or benchmark triggers. These are architecture decisions; current code remains unchanged.

Static counterfactual diagnostics from preserved E1-A2 matches: semantic-complete cases ignoring type 20/24; semantic-slot stable pairs ignoring type 10/12; type disagreements 12/40 matches; granularity failures 4 cases in pairs05/09. Those four cases leave four independent reference slots unmatched through merges; no additional standalone unexpressed need was established. Taxonomy disagreement and semantic omission are distinct. Historical G8's 7/12 is strict reference conformance, not pure paraphrase stability.

E1-A2 remains FAIL under its frozen preregistered contract. No regrading, provider/judge/scorer execution, pytest, source dataset reopening, protected-data access, production change or E1-A2 artifact mutation occurred. JSON/count/lifecycle/path checks and `git diff --check` passed. All model calls and token usage for E1-AR were zero.

E1-AR PASS establishes a revised contract only; repair and fresh prospective validation remain required. E1-R1 is recommended but not authorized. A later separately authorized E1-R2 must use a fresh prospective acceptance cohort; E1-A2 may be exposed regression diagnostics, not its sole acceptance cohort. `question_core` and compatibility requirements remain authoritative, E2/E3 remain NOT_STARTED, and production activation remains false.

Artifacts: `evaluation/e1_architecture_review.json`, `evaluation/E1_ARCHITECTURE_REVIEW.md`.

## Historical checkpoint — E1-A2 targeted validation closeout

All 24 preregistered cases (12 bases and 12 controlled paraphrases) completed and were scoreable. Valid decomposition 24/24; question-only reference recall 40/44 (90.91%); prediction precision 40/40 (100%); under-decomposed 4/24; over-decomposed 0/24; exact count 20/24; hidden prerequisites 0. G7 failed at 28/40 (70%) matched facet-type accuracy against >=90%; G8 failed at 7/12 strict reference-conformant pairs against >=10/12. All other gates passed. No structural/provider/judge-infrastructure failures occurred.

The frozen verdict is FAIL. Type disagreement and merged independently requested needs warrant architecture review; five non-conforming pairs must not all be described as semantic paraphrase drift. Sources and languages are fully confounded in this small exposed-development cohort. References were question-only, not legacy Gold answer rubrics. No protected question content was accessed.

Execution used 24 decomposition and 24 semantic-judge logical calls, 48 actual generation requests, 63,618 tokens. Analyzer, embedding, reranker, retrieval and QA answer/review/revision calls were zero. Frozen-run verification and an independent offline count/gate/usage audit reproduced the results; no provider rerun or mid-run repair occurred.

The E1-A1 implementation remains shadow diagnostic, with normal QA, `question_core`, compatibility requirements and production source/configuration unchanged. No E2/E3 or production activation occurred. E1 ARCHITECTURE REVIEW is recommended, not authorized.

Artifacts: `evaluation/e1_a2_dynamic_question_decomposition_validation_manifest.json`, `evaluation/E1_A2_DYNAMIC_QUESTION_DECOMPOSITION_VALIDATION_PREREGISTRATION.md`, `evaluation/e1_a2_dynamic_question_decomposition_validation_cases.jsonl`, `evaluation/e1_a2_dynamic_question_decomposition_validation_result.json`, `evaluation/E1_A2_DYNAMIC_QUESTION_DECOMPOSITION_VALIDATION.md`.

## Historical checkpoint — E1-A1 diagnostic implementation closeout

The explicit `QAAgent.decompose_question` seam accepts only the raw question and returns 1–5 validated shadow diagnostic facets. Exact question support spans, normalized-text duplicate rejection, question-order normalization, and code-assigned facet ordinals are implemented. Ambiguity remains diagnostic only.

The normal QA path does not invoke decomposition. `question_core`, existing answer requirements, production prompts, retrieval, and claim coverage remain unchanged; E2/E3 and production activation were not implemented.

Focused T0 verification: 19 decomposition contract tests and 2 existing QA tests passed; `git diff --check` passed. An initial collection attempt lacked `PYTHONPATH=src`; setting the command-local source path resolved it. All provider calls and token usage were zero. No benchmark/novel dataset or Gold annotation was accessed.

E1-A1 PASS does not mean E1 PASS. Real-model quality, Gold recall, semantic over/under-decomposition, paraphrase stability, and generalization remain unmeasured. E1-A2 is recommended but not authorized.

Artifacts: `evaluation/e1_a1_dynamic_question_decomposition_contract.json`, `evaluation/E1_A1_DYNAMIC_QUESTION_DECOMPOSITION_CONTRACT.md`.

## F1 static inventory closeout

F1 classified 21 candidates: 12 production residuals, 3 provenance HOLDs, 2 generic mechanisms, 2 domain mechanisms, 1 aggregate D4 exclusion, and 1 evaluator-only exclusion. Residual ownership: 4 F2 candidates, 3 F3 candidates, 3 E1/E2 compatibility items, and 2 E3 boundary reviews. E1 blockers = 0.

Keep the current answer-completeness compatibility layer until a generic E1/E2 replacement is established. The three local HOLDs concern non-paper intent source-policy provenance, the exact GPU-memory guard, and curated workflow/graph fallback provenance. They are not counted as substantiated production residuals.

PASS applies only to the bounded static inventory. No production source/configuration changed, no D4 reinventory occurred, no protected split was accessed, and scientific/provider/model calls and token usage were zero. F1 does not complete Phase F or D4, remove dependencies, or authorize E1/F2/F3.

Artifacts: `evaluation/f1_residual_benchmark_dependency_inventory.json`, `evaluation/F1_RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY.md`.

---

## Current D4 production state

Structured replacement active:

- event_poca_handoff
- restgas_profile_workflow

Validated locator retirement active:

- effective_acceptance_pipeline
- root_macro_usage

Validated component-level locator retirement active:

- model_factory_theory /
  model/PndLmdModelFactory.cxx

Current ModelFactory rule state:
model_factory_theory symbols:

- model/PndLmdDPMAngModel1D.cxx
- model/PndLmdDPMAngModel2D.cxx

paper hints:

- pflueger_2017 [51,57,65]

structured_replacement:
absent/default false

FULL_BATCH2_PRODUCTION_ACTIVATION=false

Only `model/PndLmdModelFactory.cxx` was removed from `model_factory_theory.symbols`. Independent ModelFactory references remain elsewhere; the entire rule is not retired.

---

## Current unresolved / HOLD items

model/PndLmdDPMAngModel1D.cxx
→ HOLD_DIRECT_TREATMENT_COVERAGE_GAP

model/PndLmdDPMAngModel2D.cxx
→ HOLD_DIRECT_TREATMENT_COVERAGE_GAP

pflueger_2017 [51,57,65]
→ HOLD_OUTSIDE_TREATMENT_SCOPE

These confirmed HOLD items are not assumed to represent the complete residual original D4 inventory.

Broader D4 inventory reconciliation remains pending.

---

## Latest scientific decision summary (D4-A9-R2)

Result:
PASS / Level 6 / PARTIAL

Validated:
model_factory_theory origin for
model/PndLmdModelFactory.cxx

Held:
DPM1D
DPM2D
Pflueger [51,57,65]

Critical losses:
0

Grounding regressions:
0

Version violations:
0

Production activation:
subsequently performed in D4-A10

Detailed evidence remains in the existing machine-readable and report artifacts (`evaluation/d4_a9_result.json`, `evaluation/d4_a9_evaluator_results.json`, `evaluation/D4_A9_MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATION.md`, `evaluation/d4_a9_r2_result.json`, `evaluation/D4_A9_R2_POST_OUTCOME_CLOSEOUT_VERIFICATION_RECOVERY.md`).

---

## Key historical D4 checkpoints

D4-A3
First-batch structured migration activated.
Artifacts: `evaluation/d4_a3_batch1_runtime_migration.json`, `evaluation/D4_A3_BATCH1_RUNTIME_MIGRATION.md`.

D4-A7
Validated Batch2 subset locator retirement activated:
effective_acceptance_pipeline and root_macro_usage.
Artifacts: `evaluation/d4_a7_validated_subset_locator_retirement_activation.json`, `evaluation/D4_A7_VALIDATED_SUBSET_LOCATOR_RETIREMENT_ACTIVATION.md`.

D4-A9
Prospective component-sensitive ModelFactory scientific execution.
Artifacts: `evaluation/d4_a9_result.json`, `evaluation/d4_a9_evaluator_results.json`, `evaluation/D4_A9_MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATION.md`.

D4-A9-R1
Failed post-outcome closeout-verifier attempt.
No scientific authority.
Artifact: `evaluation/D4_A9_R1_POST_OUTCOME_CLOSEOUT_VERIFICATION_REPAIR.md`.

D4-A9-R2
Forward-only closeout recovery and accepted Level-6 component result.
Artifacts: `evaluation/d4_a9_r2_result.json`, `evaluation/D4_A9_R2_POST_OUTCOME_CLOSEOUT_VERIFICATION_RECOVERY.md`.

D4-A10
Validated ModelFactory rule-local locator retirement activated.
Evidence: accepted D4-A10 activation in Git history and current `configs/query_expansions.yaml`.

---

## Key historical D1–D3.5 checkpoints

- **D3.5-A6 (Phase 2)**: COMPLETE / PASS. Validated bounded structured candidate admission and reranking for development (`SELECTED_ADMISSION_BUDGET = 3`). Confirmed safety on baseline-stable evidence groups; production activation was not performed. Artifacts: `evaluation/d3_5_a6_phase2_result.json`.
- **D3-A2**: COMPLETE / PASS. Three-arm controlled comparison validated generic structured replacement foundation; established the experimental replacement foundation for investigated shortcuts without phrase/rule/case-to-object answer-location mapping. Artifacts: `evaluation/d3_a2_three_arm_results.json`, `evaluation/D3_A2_FROZEN_THREE_ARM_COMPARISON.md`.
- **D2-A3 / D2-A3-R1**: ROLE_DECISION_COMPLETE. Mechanism-dependent bounded authority frozen (Tier G / Tier S authoritative-bounded; Tier D advisory/non-authoritative; whole-question fallback prohibited). Current production resolver role remains SHADOW. Artifacts: `evaluation/d2_a3_role_decision.json`, `evaluation/D2_A3_RESOLVER_ROLE_DECISION.md`.
- **D1-A3**: COMPLETE / PASS. Canonical knowledge representation established for concepts, entities, relations, and workflows with machine-traceable provenance and version identity. Compatible with real corpus; did not claim query-time resolver or shortcut migration. Detailed D1 contracts and compatibility records remain in `docs/`, `evaluation/`, and Git history.

---

## Key historical Phase C checkpoints

- **C8-A2-C0**: DEFERRED / CLOSED_INCONCLUSIVE. Natural targeted applicability closeout; observed targeted branch applicability was 1/80 (1.25%), falling short of the preregistered minimum cohort of 6. Unresolved generic downstream coverage-aware behavior deferred to Phase E. Artifact: `evaluation/baselines/manifests/phase_c_c8_a2_applicability_closeout_v1.json`.
- **C7-A4**: COMPLETE / PASS. Evaluated explicit post-reranker selection. Retained CURRENT_SELECTOR as production-authoritative; rejected `c7.explicit_selection.v1` as global replacement. Artifact: `evaluation/baselines/manifests/phase_c_c7_a4_production_role_closeout_v1.json`.
- **C6-A3**: COMPLETE / PASS. Evaluated candidate fusion replay. Confirmed P0 CURRENT fusion remains production-authoritative. Artifact: `evaluation/baselines/manifests/phase_c_c6_a3_frozen_production_role_decision_v1.json`.
- **C5-A3**: CLOSED_INCONCLUSIVE. Evaluated entity resolution on frozen plans. Established identity-strength finding; production exact matching remains legacy. Reactivation depends on Phase D generic entity infrastructure. Artifact: `evaluation/baselines/manifests/phase_c_c5_a3_architectural_closeout_identity_strength_v1.json`.
- **C4-A3**: CLOSED_INCONCLUSIVE. Evaluated lexical query expansion / BM25. Treatment-qualified plans under locked pool were insufficient (3/46 vs minimum 6). Production sparse remains exact raw question; LexicalQuery remains experimental/shadow abstraction. Artifact: `evaluation/baselines/manifests/phase_c_c4_a3_architectural_closeout_v1.json`.
- **C3-A**: COMPLETE / PASS. Evaluated raw-preserving dual-dense architecture. RawDense always carries raw question and is production-authoritative. SemanticDense is auxiliary/experimental and explicit shadow-only. Artifact: `evaluation/baselines/manifests/phase_c_c3a_raw_preserving_auxiliary_semantic_dense_v1.json`.
- **C2**: COMPLETE / PASS. Delivered narrow and auditable query-analyzer contract.
- **C1 / C1-R1**: COMPLETE / PASS. Delivered deterministic pre-parse implementation with fixed/fallback ownership.

---

## Key historical Phase B checkpoints

- **B5**: PASS. Structure-aware chunking and source-file coverage.
- **B4**: PASS. Precise derived-chunk locators.
- **B3**: PASS. Unified sparse encoder identity and factory.
- **B2**: PASS. Dense embedding dimensionality contract (3072 dimensions, Cosine metric, `gemini-embedding-2`).
- **B1**: PASS. Correct sparse BM25 / Qdrant server-side IDF modifier contract.
- **Phase-B T3 / T3.1 / T3.2 / T3.3A**: Full 80-question dev retrieval-only benchmark, product-language recalibration (59 formal-English cases), frozen fused-rank provenance, soft-budget correction, and two-pass backfill closeout. The formal English retrieval gate remained FAIL; subsequent replay was INCONCLUSIVE/partial. Generic coverage-aware selection and optional ranking debt remain deferred.

---

## Key historical Phase A and baseline checkpoints

- **A1**: PASS. Explicit evaluation modes (`retrieval`, `qa`, `full`) with recorded execution boundaries.
- **A2**: PASS. Structured retrieval traces persisted as atomic JSON and JSONL without requiring QA reruns.
- **A3**: PASS. English Gold Stratified Bootstrap Baseline established (deterministic manifest-driven selection across question classes) providing a reproducible before/after comparison reference.
- **Novel Dataset Curation (N0–N3, ND-0)**: Established curated novel dataset splits (Novel Dev N1/N2, Validation N3-F/N3-E/N3-VF). ND-0 closed the first novel-dev retrieval generalization baseline; historical diagnostic attribution remains in its artifacts and does not establish resolver treatment efficacy.
- **Historical Pre-Generalization Baselines**: Gold v2.6 / Evaluator 2.6.1, RC2b, Candidate v8, Candidate v5, and v2-lite RC1 baselines preserved in Git history and `evaluation/baselines/`.


## Post-A3 residual completeness and Gold governance reconciliation

COMPLETE / PASS / PRODUCT_REPAIR_DEFERRED_GOLD_GOVERNANCE_RECONCILED. Stored g022, g023, and post-terminal g013 evidence did not establish one safe generic product defect: g022 lost an unrepresented conjunctive obligation, g023 preserved faithfulness after an unsupported workflow-order claim could not be repaired, and g013 remained a diagnostic answer-granularity gap. Product code stayed unchanged and NEW_CANDIDATE_DEVELOPMENT_HEAD = d3a1b274b2784399a7dc51b094a17e466d208b50.

Source-level and benchmark-wide governance kept g011, g044, and g115 unchanged and established one forward-only correction for g060. Gold m6-benchmark-v2.10 (SHA bdce5cbd...) changes only g060 and is paired with calibration v7 (59 formal-English IDs; selector SHA e27ef67a...). Gold v2.9 and Attempt-3 scoring remain immutable. Change-relevant deterministic tests passed; two unrelated gate-test failures were already present in the pre-edit AGY baseline. Scientific calls/tokens 0; novel_validation pristine; holdout access 0; F6-B execution 0. Attempt 4 is READY for fresh preregistration/freeze/execution but is not authorized by this task. Report: evaluation/POST_A3_RESIDUAL_COMPLETENESS_AND_GOLD_GOVERNANCE.md.

NEXT_TASK_RECOMMENDATION = F6-A ATTEMPT 4 / FRESH PREREGISTRATION, CANDIDATE FREEZE, AND CONTINUOUS PRE-RELEASE VALIDATION (NOT AUTHORIZED).

## F6-A formal repeat eligibility and stochastic attempt policy

COMPLETE / PASS / SAME_LINEAGE_REPEAT_PROHIBITED_WITHOUT_MATERIAL_CHANGE.

A complete terminal formal F6-A result now closes its product-behavior lineage
for ordinary single-attempt validation. Provider-hosted stochastic variation
under the same frozen model/product identity is not a new candidate. Repeating
the same exposed-Gold cohort until PASS, selecting the best realization,
discarding FAIL results, or tuning between runs is prohibited optional stopping.
Infrastructure recovery remains limited to completing an interrupted run under
the exact frozen run identity.

A fixed replicate block remains possible only as one formal design whose count,
run identities, complete schedule, aggregate rule, hard-gate rule, failure
treatment, usage accounting, and no-peeking boundary are preregistered before
replicate 1. No such protocol is established by this task and it cannot be
introduced retroactively after Attempt-4 outcomes and case diagnostics were
inspected.

Current product-behavior lineage HEAD remains
`d3a1b274b2784399a7dc51b094a17e466d208b50`. The post-A4 gate-bootstrap and
stage-receipt metadata repairs are infrastructure-only. Therefore
`EXECUTION_INFRASTRUCTURE_READY = true`,
`FORMAL_REPEAT_SCIENTIFICALLY_ELIGIBLE = false`, and
`ATTEMPT_5_ELIGIBILITY = NOT_ELIGIBLE`. Attempt 5 was not preregistered, frozen,
or executed. Scientific calls/tokens were 0/0; novel_validation remains
pristine; holdout access, protected-content leakage, and F6-B execution remain
zero.

Policy: `evaluation/F6_FORMAL_REPEAT_POLICY.md`.

NEXT_TASK_RECOMMENDATION = WAIT FOR A MATERIAL NEW PRODUCT CANDIDATE BEFORE ANOTHER FORMAL F6-A ATTEMPT (NOT AUTHORIZED).
