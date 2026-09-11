# PF-LR1 — Phase-F Scope Reconciliation and Bounded Cleanup-Plan Establishment

Status: `COMPLETE / PASS / PHASE_F_SCOPE_RECONCILED_BOUNDED_CLEANUP_PLAN_ESTABLISHED`
Type: static lifecycle / scope reconciliation and documentation formalization. Zero
PANDA scientific/evaluation calls; zero product changes; zero protected-data access.

## 1. Purpose

Persist the Phase-F scope reconciliation as the authoritative conversion of the F1
residual inventory (R01–R21) into a bounded lifecycle/execution map. After this
report, a future Phase-F production task can be authorized without re-deriving
Phase-F scope: the formal F2 scope, the E1/E2 compatibility-retirement scope, the
F3/D4 boundary, the recommended execution order, promotion materiality under
PE-LR1, and the recommended next bounded implementation task are all established
here.

## 2. Authorization boundary

This task is a repository-level lifecycle/documentation task. It is NOT
authorization to implement F2, R13, R10, compatibility retirement, R14, R04, R01,
F3, or any production-code change. It does not promote `runtime_e1_v2`, reopen E3
or D4, create D4-A11, or reconsider default promotion. Only the artifacts listed
in §17 changed.

## 3. Starting repository state

```text
HEAD = a2920d91781c3f99633a57e8c9d3d6e2e9c3ef26 (Clean up PE-LR1 decision matrices)
working tree = clean
Phase F = IN_PROGRESS / F1_COMPLETE
F2 = NOT_STARTED / SCOPE_PRESERVED
F3 = SCOPE_RECONCILIATION_REQUIRED / PARTIALLY_SUPERSEDED_BY_D4
D4 = PAUSED / ROADMAP_RECONCILIATION (overall completion UNDECIDED)
Phase E = COMPLETE / CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED / DEFAULT_PROMOTION_DEFERRED
normal default = legacy_question_core
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
```

Actual HEAD matched the expected authorization HEAD; no unrelated user work was
present or disturbed.

## 4. Authoritative inputs and exclusions

Read and reconciled: `docs/GENERALIZATION_ROADMAP.md`, `docs/EVALUATION_STATUS.md`,
`docs/EVALUATION_POLICY.md`, `evaluation/F1_RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY.md`
plus the paired machine-readable `evaluation/f1_residual_benchmark_dependency_inventory.json`,
`evaluation/PE_LR1_PHASE_E_PROMOTION_BOUNDARY_RECONCILIATION.md`,
`evaluation/E3_LR1_POST_A2_LIFECYCLE_DECISION.md`,
`evaluation/E2_POST_A3_LIFECYCLE_RECONCILIATION.md`, D4 lifecycle/activation records
(A0 inventory, A9-R2, A10 state via `docs/EVALUATION_STATUS.md` and current
`configs/query_expansions.yaml`), and current production code anchors for R01–R21
verified at HEAD `a2920d9`. The prior conversational PF-LR1 analysis was used only
as a starting hypothesis; every disposition below is re-grounded in current
repository evidence.

Exclusions: no protected novel-validation/holdout content, no hidden benchmark
answers, no scientific/model/judge/DB calls, no production code/config/prompt
edits, no runtime-default change, no promotion acceptance, no D4 reinventory.

## 5. F1 inventory revalidation at current HEAD

All 21 F1 anchors were re-verified present at `a2920d9` (line numbers shifted from
the F1 snapshot because Phase-E seams were added; every semantic anchor resolved):

| ID | Current verified anchor (HEAD a2920d9) |
|---|---|
| R01 | `configs/retrieval_policies.yaml:25-31` (intents required_sources) |
| R02 | `configs/retrieval_policies.yaml:18-42` (non-paper required_sources) |
| R03 | `src/panda_agent/retrieval.py:1147-1149` (feedback page override, li_2026 [141,149,151]) |
| R04 | `src/panda_agent/qa.py:1585,2511-2538` (exact negative control + fixed refusal locator) |
| R05 | `src/panda_agent/qa.py:2560` (PndPidCorrelator.h fallback) |
| R06 | `src/panda_agent/qa.py:2592-2610` (deleted-runtime fallback locator/wording) |
| R07 | `src/panda_agent/qa.py:1566-1576` (exact_memory_question guard) |
| R08 | `src/panda_agent/qa.py:333,1784,2138,2362` (`_answer_requirements`) |
| R09 | `src/panda_agent/qa.py:703,801,841,2141-2205,2366` (requirement evidence/enforcement) |
| R10 | `src/panda_agent/qa.py:757,816,926-929` (pndlmdtrackq pointer predicate) |
| R11 | `src/panda_agent/qa.py:106,1772,1799` (dataflow_locator_ / required_boundary_locators) |
| R12 | `src/panda_agent/qa.py:1091-1106,1145` (sufficiency routing; E3 seam coexists at 1094) |
| R13 | `src/panda_agent/qa.py:1911,2001-2067,2053` (deterministically_supported_claims + whitelist) |
| R14 | `src/panda_agent/retrieval.py:678-700,1977` (`select_final_evidence`) |
| R15 | `src/panda_agent/retrieval.py:1524,1552` (`_workflow`/`_graph` curated fallback) |
| R16 | `src/panda_agent/qa.py:1495` (`_answerability_guard`) |
| R17 | `src/panda_agent/qa.py:65,76,79` (question_core objective, citation eligibility) |
| R18 | `src/panda_agent/retrieval.py:1010-1015`, `configs/aliases.yaml` (accepted aliases) |
| R19 | `src/panda_agent/retrieval.py:1478-1484` (locked paper taxonomy) |
| R20 | `src/panda_agent/retrieval.py:1022`, `configs/query_expansions.yaml` (D4 expansion consumption) |
| R21 | `src/panda_agent/evaluation_runner.py:875,1576` (`_execute_evaluation_case`) |

No reclassification was needed: current evidence supports the F1 classifications,
with the PF-LR1 review corrections applied to R12, R13/R10 dependency semantics,
and R14 (§8–§10).

## 6. Complete R01–R21 reconciliation matrix

Dependency types: `HARD_PREREQUISITE`, `SOFT_ARCHITECTURAL_ORDERING`,
`VALIDATION_COUPLING`, `NO_DEPENDENCY` — never collapsed.

| ID | Current class | Final PF-LR1 disposition | Owner | Phase-F action? | Standalone task? | Coupling group | Dependency / prerequisite | Order | Promotion materiality | D4 boundary | E3 boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | BENCHMARK_DERIVED_RUNTIME_POLICY | F2_GENERIC_POLICY_CLEANUP | F2 (group E) | yes | yes | F2_GROUP_E_SEMANTIC_SOURCE_OBLIGATIONS | NO_DEPENDENCY | 6 | POTENTIALLY_MATERIAL_WHEN_COUPLED | NONE | indirect via sufficiency only |
| R02 | HOLD_UNCERTAIN_PROVENANCE | HOLD_UNCERTAIN_PROVENANCE | HOLD | no | no | NONE | NO_DEPENDENCY | — | NOT_APPLICABLE | NONE | NONE |
| R03 | FIXED_LOCATOR_SHORTCUT_OUTSIDE_D4 | F3_FIXED_LOCATOR_CLEANUP | F3 | yes | yes | F3_FIXED_LOCATOR_PACKAGE | NO_DEPENDENCY | 7 | LOCAL_NON_MATERIAL | RELATED_BUT_OUTSIDE_D4 (shared page values, independent code origin) | NONE |
| R04 | CASE_SPECIFIC_NEGATIVE_CONTROL | F2_GENERIC_POLICY_CLEANUP | F2 (group D) | yes | yes | F2_GROUP_D_PREMISE_REFUSAL_GENERALIZATION | NO_DEPENDENCY (R16 is a design foundation, not a prerequisite) | 5 | PROMOTION_RELEVANT_MATERIAL | RELATED_BUT_OUTSIDE_D4 (rule unmigrated) | refusal may enter sufficiency routing |
| R05 | FIXED_LOCATOR_SHORTCUT_OUTSIDE_D4 | F3_FIXED_LOCATOR_CLEANUP | F3 | yes | yes | F3_FIXED_LOCATOR_PACKAGE | SOFT_ARCHITECTURAL_ORDERING (after R04) | 7 | LOCAL_NON_MATERIAL | NONE | NONE |
| R06 | FIXED_LOCATOR_SHORTCUT_OUTSIDE_D4 | F3_FIXED_LOCATOR_CLEANUP | F3 | yes | yes | F3_FIXED_LOCATOR_PACKAGE | SOFT_ARCHITECTURAL_ORDERING (after R04) | 7 | LOCAL_NON_MATERIAL | RELATED_BUT_OUTSIDE_D4 (structured replacement covers YAML rule, not finalizer) | NONE |
| R07 | HOLD_UNCERTAIN_PROVENANCE | HOLD_UNCERTAIN_PROVENANCE | HOLD | no | no | NONE | NO_DEPENDENCY | — | NOT_APPLICABLE | NONE | NONE |
| R08 | BENCHMARK_SHAPED_COMPATIBILITY_LAYER | E1_E2_COMPATIBILITY_RETIREMENT | F2 (bounded named step, group C) | yes | yes (as one cluster step) | F2_GROUP_C_E1E2_COMPATIBILITY_RETIREMENT | SOFT_ARCHITECTURAL_ORDERING after R13/R10 + VALIDATION_COUPLING (E1/E2 coverage equivalence) | 3 | PROMOTION_RELEVANT_MATERIAL | NONE (R11: RELATED_BUT_OUTSIDE_D4) | active in both modes; runtime_e1_v2 mode-coupled |
| R09 | BENCHMARK_SHAPED_COMPATIBILITY_LAYER | E1_E2_COMPATIBILITY_RETIREMENT | F2 (bounded named step, group C) | yes | yes (as one cluster step) | F2_GROUP_C_E1E2_COMPATIBILITY_RETIREMENT | SOFT_ARCHITECTURAL_ORDERING after R13/R10 + VALIDATION_COUPLING | 3 | PROMOTION_RELEVANT_MATERIAL | NONE | active in both modes |
| R10 | BESPOKE_SUFFICIENCY_OR_COMPLETENESS | F2_CORE_BEHAVIORAL_CLEANUP | F2 (group B) | yes | yes | F2_GROUP_B_DETERMINISTIC_COMPLETENESS | NO_DEPENDENCY — R13→R10 is SOFT_ARCHITECTURAL_ORDERING (recommended semantic sequencing) only, not a hard prerequisite/code/dataflow dependency | 2 | PROMOTION_RELEVANT_MATERIAL | NONE | NONE |
| R11 | BENCHMARK_SHAPED_COMPATIBILITY_LAYER | E1_E2_COMPATIBILITY_RETIREMENT | F2 (bounded named step, group C) | yes | yes (as one cluster step) | F2_GROUP_C_E1E2_COMPATIBILITY_RETIREMENT | SOFT_ARCHITECTURAL_ORDERING after R13/R10 + VALIDATION_COUPLING | 3 | PROMOTION_RELEVANT_MATERIAL | RELATED_BUT_OUTSIDE_D4 | active in both modes |
| R12 | BESPOKE_SUFFICIENCY_OR_COMPLETENESS | E3_RECONCILED_NO_STANDALONE_ACTION | E3-reconciled (interaction boundary only) | **no** | **no** | E3_INTERACTION_BOUNDARY | NO_DEPENDENCY | — | NOT_APPLICABLE | NONE | GOVERNED_BY_E3_LR1_§8 |
| R13 | BESPOKE_SUFFICIENCY_OR_COMPLETENESS | F2_CORE_BEHAVIORAL_CLEANUP | F2 (group A) | yes | yes | F2_GROUP_A_VERIFIER_SUPPORT_SEMANTICS | NO_DEPENDENCY | 1 | PROMOTION_RELEVANT_MATERIAL | NONE | no direct seam; feeds activation failure surface |
| R14 | BENCHMARK_SHAPED_COMPATIBILITY_LAYER | PHASE_F_SHARED_BOUNDARY_REVIEW | Phase-F boundary review | no (NO_CHANGE_CURRENTLY_JUSTIFIED) | no | E3_SHARED_SELECTION_BOUNDARY | NO_DEPENDENCY; VALIDATION_COUPLING applies to any future shared-selection change | 4 (review only) | POTENTIALLY_MATERIAL_WHEN_COUPLED | RELATED_BUT_OUTSIDE_D4 (policy layer) | GOVERNED_BY_E3_LR1_§9 |
| R15 | HOLD_UNCERTAIN_PROVENANCE | HOLD_UNCERTAIN_PROVENANCE | HOLD | no | no | NONE | NO_DEPENDENCY | — | NOT_APPLICABLE | NONE | retrieval/E3 boundary review stays HOLD |
| R16 | GENERIC_LEGITIMATE_MECHANISM | KEEP_GENERIC | retained mechanism | no | no | R04_DESIGN_FOUNDATION | NO_DEPENDENCY | — | NOT_APPLICABLE | NONE | NONE |
| R17 | GENERIC_LEGITIMATE_MECHANISM | KEEP_GENERIC | retained mechanism | no | no | F2_PRESERVATION_BOUNDARY | NO_DEPENDENCY | — | NOT_APPLICABLE | NONE | NONE |
| R18 | DOMAIN_KNOWLEDGE_OR_ROUTING | KEEP_DOMAIN | retained mechanism | no | no | NONE | NO_DEPENDENCY | — | NOT_APPLICABLE | NONE (D4 injection is R20) | NONE |
| R19 | DOMAIN_KNOWLEDGE_OR_ROUTING | KEEP_DOMAIN | retained mechanism | no | no | NONE | NO_DEPENDENCY | — | NOT_APPLICABLE | NONE | NONE |
| R20 | D4_OWNED_EXCLUDED | D4_OWNED_EXCLUDED | D4 (paused) | no | no | NONE | NO_DEPENDENCY | — | NOT_APPLICABLE | D4_OWNED | NONE |
| R21 | EVALUATION_ONLY_NON_PRODUCTION | EVALUATION_ONLY_EXCLUDED | evaluation infrastructure | no | no | NONE | NO_DEPENDENCY | — | NOT_APPLICABLE | NONE | NONE |

All 21 items appear exactly once. Current code surface, HEAD status, retirement /
replacement conditions, and per-item evidence are encoded in the machine-readable
companion (`evaluation/pf_lr1_phase_f_scope_reconciliation.json`).

## 7. F1 revalidation corrections carried into this formalization

The read-only PF-LR1 analysis was accepted with mandatory corrections, all applied
consistently here:

1. **R13 → R10 is not a hard/dataflow dependency.** R13 (verifier-support
   semantics) and R10 (deterministic completeness semantics) are conceptually
   related but distinct, independently implementable F2 surfaces. R13 is
   recommended first only as `RECOMMENDED_SEMANTIC_SEQUENCING`
   (`SOFT_ARCHITECTURAL_ORDERING`) for architectural clarity, causal isolation,
   and easier validation. No hard prerequisite, code dependency, dataflow
   dependency, or implementation blocker is asserted. If a future R13 task ends
   in HOLD/DEFERRED/INCONCLUSIVE, that fact alone must not block R10.
2. **R12 is not an ordinary Phase-F cleanup item.** Final disposition is
   `E3_RECONCILED_NO_STANDALONE_ACTION` with `phase_f_action_required = false`,
   `standalone_task_allowed = false`, `promotion_materiality = NOT_APPLICABLE`.
   R12 is not ORDINARY_CLEANUP, not an outstanding F2/F3 cleanup, and not a
   reason to reopen E3. It may only be revisited as an interaction boundary if a
   broader future Phase-F production change materially modifies the pre-answer
   retrieval/sufficiency path; that change must assess E3 interaction within its
   own broader authorized validation.
3. **The focused-E3-validation size.** The authoritative E3 lifecycle artifact
   (E3-LR1 §9) cites the 49 focused E3 tests for shared-selection-semantics
   changes; that count is cited here as recorded historical evidence, not
   re-derived and not converted into a new standing invariant by PF-LR1. Where
   possible this report uses the wording "the focused E3 validation prescribed by
   the authoritative E3 lifecycle artifact."
4. **R14 is not pre-authorized for implementation.** Disposition is
   `PHASE_F_SHARED_BOUNDARY_REVIEW` with
   `current_implementation_action = NO_CHANGE_CURRENTLY_JUSTIFIED`: C7 retained
   `CURRENT_SELECTOR` production-authoritative, E3-LR1 §9 reconciled the boundary
   as a non-blocker, and no present defect justifies modification. No production
   task is manufactured for R14 solely because it exists in F1.

## 8. Formal F2 boundary (bounded scope)

F2 = NOT_STARTED / UNEXECUTED, owner Phase F. Five bounded groups:

**A. Verifier-support semantics (R13).**
Changes: which claims may bypass semantic unsupported-claim review as
deterministically supported. Preserved: citation/version/locator integrity,
ordinary unsupported-claim detection, refusal semantics, public DTO/prompts.
Replacement condition: support determination consistent with the evidence-claim
relationship; the token whitelist justified generically or removed. Likely
future validation: T0 verifier fixtures and focused deterministic verifier tests.
Promotion materiality: PROMOTION_RELEVANT_MATERIAL (changes the semantics of
verified/supported — the failed activation surface). Interactions: E2 claim
accountability; E3 second-verify retained-support view (the focused E3 validation
prescribed by the authoritative E3 lifecycle artifact applies if shared verify
paths change).

**B. Deterministic completeness semantics (R10).**
Changes: the deterministic missing-requirement predicate requiring a hard-coded
pointer symbol and pointer-syntax wording. Preserved: generic completeness
obligations over live evidence, one bounded revision, salvage of supported
claims, honest incomplete/refusal outcomes. Replacement condition:
question-grounded completeness semantics without Gold-shaped decomposition
points. Likely future validation: T0 plus regression-protected requirement tests.
Promotion materiality: PROMOTION_RELEVANT_MATERIAL. Interactions: hosted inside
the R09 machinery; E1/E2 remain the source of any future question-derived
coverage semantics.

**C. E1/E2 compatibility retirement (R08/R09/R11) — one bounded named step
inside F2.**
Changes: the legacy generation/review/revision requirement contract (obligation
derivation, named-requirement evidence enforcement, planned-locator/dataflow
augmentation). Preserved: evidence-backed answering, citation integrity, internal
claim filtering, bounded revision, E1/E2 runtime semantics. Retirement condition:
established coverage equivalence with the E1/E2 claim→answer-point→evidence
architecture; question requirements distinguished from upstream plan
suggestions; never blanket deletion. Likely future validation: cluster-level
focused deterministic tests plus E1/E2 seam tests; prospective scientific
validation only under separate authorization. Promotion materiality:
PROMOTION_RELEVANT_MATERIAL (cluster). Interactions: `runtime_e1_v2` is a coupled
mode (E1 + E2 + E3); E1/E2 validation ran with this layer active. No new
top-level lifecycle phase is created for the cluster.

**D. Premise/refusal generalization (R04).**
Changes: the exact case-specific negative-control refusal path and its fixed
response locator. Preserved: generic refusal correctness, evidence-grounded
refusal bases, safety boundaries (future-runtime, formal-proof, deleted-runtime).
Replacement condition: generic class/premise handling plus evidence-grounded
refusal, building on R16's foundation; behavior never merely deleted. Likely
future validation: T0 refusal fixtures including bare-class and premise-mismatch
sentinels. Promotion materiality: PROMOTION_RELEVANT_MATERIAL (refusal
correctness is named by PE-LR1 §6). Interactions: refusal may enter pre-answer
sufficiency routing; R05/R06 presentation cleanup coordinates with this group;
no E3 reopening.

**E. Semantic source obligations (R01).**
Changes: fixed intent→required-source mappings driving plan requirements,
retrieval, selection, and sufficiency. Preserved: safety behavior (version-conflict
rejection, honest sufficiency/refusal). Replacement condition: question-grounded
semantic source-obligation logic. Likely future validation: T0 policy/config
tests plus sufficiency-focused checks. Promotion materiality:
POTENTIALLY_MATERIAL_WHEN_COUPLED. Interactions: sufficiency/refusal outcomes; no
direct E3 seam.

Excluded from F2: R12 (not an F2 task — E3-reconciled); R14 (outside mandatory
modification; `NO_CHANGE_CURRENTLY_JUSTIFIED` unless a present defect is
evidenced).

## 9. Formal F3 boundary against D4

F3 = NOT_STARTED / UNEXECUTED, owner Phase F. Remaining scope is a small bounded
fixed-locator/fallback cleanup package: R03, R05, R06.

Ownership is decided by implementation origin, owning runtime layer, existing
structured replacement, and lifecycle ownership — not by matching filenames,
pages, macros, symbols, or literals:

- **R20 = D4-owned** because it *is* the D4 expansion-consumption mechanism and
  the active structured migrations (event_poca_handoff, restgas_profile_workflow,
  effective_acceptance_pipeline, root_macro_usage, model_factory_theory
  rule-local) plus the confirmed HOLDs (DPM1D, DPM2D, pflueger_2017 [51,57,65]).
  Broader D4 inventory reconciliation remains pending; D4 overall completion is
  UNDECIDED. D4 is not reopened and no D4-A11 is created.
- **R03/R05/R06 remain Phase-F-owned** because their code origins live in
  `retrieval.py`/`qa.py` production branches outside the D4 rule inventory:
  R03's page-set replacement is an independent `Retriever.analyze` code origin
  (the D4 rule `reconstructed_profile_to_acceptance` shares the page values
  `li_2026 [141,149,151]` but is itself unmigrated / NEEDS_EVIDENCE); R05's
  exact-header fallback has no D4-supplied replacement; R06's finalizer
  locator/wording is not covered by the active `event_poca_handoff` structured
  replacement, which addresses the YAML rule contribution only.
- **Superseded by D4:** the original F3 goal of incremental
  phrase-to-answer-location retirement as a pattern was implemented by D4 for
  YAML query-expansion locators; that portion of F3 closes as superseded without
  new implementation.
- **Coordination rule:** shared literals between R03 and D4 rules are
  coordinated, never globally deleted; no D4 rule or page removal is proposed.

## 10. E3 reconciliation (R12 / R14)

- **R12 = E3_RECONCILED_NO_STANDALONE_ACTION.** E3-LR1 §8 reconciled the
  pre-answer sufficiency targeting (`_targeted_retrieve`) and the post-verify
  E3 missing-point retrieval as operating on different failure information with
  justified coexistence; R12 is a non-blocker owned by neither an outstanding F2
  nor F3 cleanup. Interaction-boundary condition recorded in §7(2).
- **R14 = PHASE_F_SHARED_BOUNDARY_REVIEW / NO_CHANGE_CURRENTLY_JUSTIFIED.**
  E3's global reconsideration deliberately reuses `select_final_evidence`
  (E3-LR1 §9). C7 retained `CURRENT_SELECTOR` production-authoritative. Any
  future change to shared selection semantics requires E3-boundary-aware focused
  validation — at minimum the focused E3 validation prescribed by the
  authoritative E3 lifecycle artifact (E3-LR1 §9 cites the 49 focused E3 tests)
  — and renewed scientific validation only if reconsideration semantics change
  materially. E3 is not reopened by this reconciliation.

## 11. Dependency / coupling graph

- **Independent residuals:** R01, R03, R04, R13 (each `NO_DEPENDENCY`; R04's R16
  relationship is a design foundation, not a prerequisite).
- **Coupled residuals:** R13↔R10 = SOFT_ARCHITECTURAL_ORDERING only
  (recommended semantic sequencing; independently implementable);
  R08/R09/R11 = one coherent cluster retired as a unit;
  R04↔R05↔R06 = finalize refusal/presentation surface (R05/R06 follow R04);
  R10 vs the cluster = R10 is an independent narrow repair and must not be
  collapsed into the cluster retirement.
- **Same-owning-layer groups:** QA verifier/completeness (R13, R10,
  R08/R09/R11); QA refusal/finalize (R04, R05, R06); retrieval policy (R01, R03,
  R12, R14).
- **Must remain separate:** R10 vs R08/R09/R11; R04 vs R05/R06 (F2 generalization
  vs F3 presentation cleanup); R03 vs the D4 rule (same page values, different
  code origins); R13 vs R16/R17 (semantic support overrides vs generic citation
  integrity).
- **D4-overlapping items:** R03, R04, R06, R11 (RELATED_BUT_OUTSIDE_D4), R20
  (D4-owned excluded).

## 12. Recommended execution order

Recommendation only — each step requires separate authorization and its own
validation design. No step is a hard prerequisite of another except where the
replacement condition itself demands it.

```text
1. R13            verifier-support semantics          (NO_DEPENDENCY)
2. R10            deterministic completeness semantics (SOFT_ARCHITECTURAL_ORDERING after R13)
3. R08/R09/R11    E1/E2 compatibility retirement       (SOFT_ARCHITECTURAL_ORDERING after R13/R10;
                                                       VALIDATION_COUPLING: E1/E2 coverage equivalence)
4. R14            shared-boundary review               (conditional; NO_CHANGE_CURRENTLY_JUSTIFIED —
                                                       no implementation task unless a present defect
                                                       or promotion-boundary need is evidenced)
5. R04            premise/refusal generalization        (NO_DEPENDENCY; establishes the generic
                                                       refusal-basis selector referenced by R05/R06)
6. R01            semantic source obligations           (NO_DEPENDENCY; late for causal clarity)
7. R03/R05/R06    F3 fixed-locator/fallback package     (R05/R06 SOFT_ARCHITECTURAL_ORDERING after R04;
                                                       R03 NO_DEPENDENCY; isolated from behavioral F2 work)
```

Ordering resolutions: R13 before R10 is recommended semantic sequencing only;
R10 remains distinct from the cluster retirement (the narrow repair must not
force the wholesale replacement to carry it, and retiring the cluster is a
separately validated material change); R14's review sits after the core
behavioral groups because a selection-semantics change is most meaningfully
assessed against the settled candidate shape — but since no current change is
justified, step 4 is a checkpoint, not a task; R04 precedes R05/R06 because the
F1 replacement conditions for those fallbacks reference a generic
query-grounded refusal-basis selector; R01 is independent and placed late for
causal clarity; F3 stays isolated unless actual code coupling requires otherwise.

## 13. Promotion-materiality reconciliation

Governing authority: PE-LR1 §6/§10 (`DEFAULT_PROMOTION_RECONSIDERATION_TRIGGER`).

```text
PROMOTION_RELEVANT_MATERIAL            R13, R10, R08/R09/R11 (cluster), R04
POTENTIALLY_MATERIAL_WHEN_COUPLED      R01, R14
LOCAL_NON_MATERIAL                     R03, R05, R06
NOT_APPLICABLE                         R02, R07, R12, R15, R16–R21
```

A material Phase-F candidate may satisfy the PE-LR1 condition for reopening a
**separate** promotion decision. It does not itself promote the experimental
runtime, authorize a promotion evaluation, authorize protected evaluation, or
make Phase F a blanket prerequisite for promotion. Promotion relevance is not
promotion authorization. Localized F3 cleanup by itself is non-material on
current evidence.

## 14. HOLD / KEEP / excluded findings

- HOLD (provenance unresolved; no speculative cleanup): R02, R07, R15.
- KEEP_GENERIC (legitimate generic mechanisms, retained): R16, R17. R16 may serve
  as the design foundation for future R04 work; that is a design relationship,
  not a hard prerequisite.
- KEEP_DOMAIN (legitimate domain knowledge/routing; not benchmark contamination):
  R18, R19.
- D4_OWNED_EXCLUDED (not reopened in Phase F): R20.
- EVALUATION_ONLY_EXCLUDED (not production runtime cleanup): R21.
- E3_RECONCILED_NO_STANDALONE_ACTION: R12.

## 15. Recommended next task

```text
NEXT_TASK_RECOMMENDATION =
R13 bounded verifier-support semantic cleanup (F2 group A)

NEXT_TASK_EXECUTION_AUTHORIZED = false
```

R13 is the strongest candidate for the first future bounded Phase-F production
task assuming current HEAD (verified here): the support-override surface is
present, independently implementable, and directly relevant to the unresolved
default-promotion failure surface. PF-LR1 recommends R13; PF-LR1 does not
authorize it. A future R13 task may validly end in PASS, FAIL, INCONCLUSIVE,
HOLD, or DEFERRED; a non-PASS R13 outcome does not by itself block R10.

## 16. Lifecycle conclusion

```text
PF-LR1 = COMPLETE / PASS /
         PHASE_F_SCOPE_RECONCILED_BOUNDED_CLEANUP_PLAN_ESTABLISHED

Phase F = IN_PROGRESS
F1      = COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED
PF-LR1  = COMPLETE / PASS / PHASE_F_SCOPE_RECONCILED_BOUNDED_CLEANUP_PLAN_ESTABLISHED
F2      = NOT_STARTED / UNEXECUTED
F3      = NOT_STARTED / UNEXECUTED

Phase D = PAUSED / ROADMAP_RECONCILIATION (D4 overall completion UNDECIDED; no D4-A11)
Phase E = COMPLETE / CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED / DEFAULT_PROMOTION_DEFERRED
normal default = legacy_question_core
runtime_e1_v2   = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
DEFAULT-PROMOTION DISPOSITION = D3 — DEFER UNTIL PROMOTION-RELEVANT MATERIAL CANDIDATE CHANGE
```

Legacy default remains an accepted stable outcome, not an incomplete state. No
historical evaluation result was rewritten; no frozen Phase-E lifecycle, E3
lifecycle, PE-LR1 decision, or D4 historical outcome was altered.

## 17. Verification performed and cost accounting

Static, proportional checks only:

- `git rev-parse HEAD`, `git status --short`, `git log`: starting identity
  `a2920d9` and clean tree confirmed before and after the task.
- Anchor verification for R01–R21 at current HEAD (targeted grep/sed on
  production files; read-only).
- JSON parse of the machine-readable companion; R01–R21 each exactly once;
  Markdown/JSON disposition agreement; lifecycle-state agreement with
  status/roadmap; R13→R10 encoded as SOFT_ARCHITECTURAL_ORDERING (no hard
  prerequisite); R12 = E3_RECONCILED_NO_STANDALONE_ACTION with no standalone
  authorization; R14 NO_CHANGE_CURRENTLY_JUSTIFIED; production files unchanged
  (verified via `git diff` path scope and final `git status`).
- Not run: full/broad suites, scientific or protected evaluation, activation
  chasing, hash/SHA256 bookkeeping. No tests were added for this documentation
  change.

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
product files changed = 0
files changed = evaluation/PF_LR1_PHASE_F_SCOPE_RECONCILIATION.md (new),
                evaluation/pf_lr1_phase_f_scope_reconciliation.json (new),
                docs/EVALUATION_STATUS.md, docs/GENERALIZATION_ROADMAP.md
commits created = 0 (none authorized)
```

Limitations: static reconciliation only; no runtime behavior executed or
measured; F1's provenance limits (initial-import history) are inherited unchanged
for HOLD items; D4 overall completion remains UNDECIDED and is not resolved here;
the execution order is a recommendation, and the 49-focused-E3-test count is
cited from E3-LR1 §9 as recorded evidence, not re-derived or made a new standing
invariant.
