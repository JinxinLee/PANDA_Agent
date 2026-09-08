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
C1 met all eight strict gates and the original pair09 atomicity sentinel. Per the
accepted closure decision, E1 closes directly. E2/E3 remain NOT_STARTED.
Decision: `evaluation/E1_CLOSURE_SCOPE_REVIEW.md`.
Report: `evaluation/E1_C1_REAL_STYLE_CONFIRMATION.md`.
Preregistration: `2517b691245c38175222064e6ca546d06fd21e9a`.
Raw freeze: `7eab1e8fe099fed6ff06384c4fa0eb48dcf52677`.


Repository head (E1-C1 starting baseline):
781007c810b113537025dbe93c28728a59e318bc

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
CURRENT_TASK = E1-C1 / COMPLETE / PASS
NEXT_TASK_RECOMMENDATION = E2 — Answer-Point Coverage and Claim Mapping / NOT AUTHORIZED
NEXT_TASK_EXECUTION_AUTHORIZED = false

No D4-A11 exists.
Phase E = IN_PROGRESS / E1_COMPLETE / E2_NEXT.
E1 = COMPLETE / PASS / QUESTION_ONLY_SEMANTIC_ANSWER_POINT_DECOMPOSITION_VALIDATED.
E2 = NOT_STARTED.
E3 = NOT_STARTED.
Phase F = IN_PROGRESS / F1_COMPLETE.
F2 = NOT_STARTED / SCOPE_PRESERVED.
F3 = SCOPE_RECONCILIATION_REQUIRED / PARTIALLY_SUPERSEDED_BY_D4.
No further D4, Phase-E, or Phase-F task is authorized after E1-C1.

## E1-C1 closeout

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
