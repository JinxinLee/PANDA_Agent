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
CURRENT_TASK = F2-A3-R1 / COMPLETE / PASS / COVERAGE_MODE_LEGACY_PROMPT_AUTHORITY_REMOVED
NEXT_TASK_RECOMMENDATION = F2-A4 — Premise and Refusal Generalization / RECOMMENDED / NOT AUTHORIZED
NEXT_TASK_EXECUTION_AUTHORIZED = false
FOLLOWING_ARCHITECTURE_TASK = bounded Phase-F production cleanup per the PF-LR1 recommended order (F2-A4 next)

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
Phase F = IN_PROGRESS / F2_A3_COMPLETE.
F2 = IN_PROGRESS / A1_A2_A3_COMPLETE.
F3 = NOT_STARTED / UNEXECUTED.
No further recovery, D4, Phase-E, or Phase-F production task is authorized after F2-A3; F2-A4 — Premise and Refusal Generalization is recommended but NOT AUTHORIZED.

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
