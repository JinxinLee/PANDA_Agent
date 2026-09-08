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

Repository planning baseline:
87cc34dd919d8431bb774003a7f76a9fff3a7567 (E1-R2 starting HEAD)

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
IN_PROGRESS / E1

E1:
IN_PROGRESS / REPAIR_IMPLEMENTED / REVALIDATION_PENDING

E1-A1:
COMPLETE / PASS / QUESTION_ONLY_DIAGNOSTIC_DECOMPOSITION_IMPLEMENTED

E1-A2:
COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED

E1-AR:
COMPLETE / PASS / REVISED_SEMANTIC_ANSWER_POINT_CONTRACT_ESTABLISHED

E1-R1:
COMPLETE / PASS / SHADOW_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIRED

E1-R2:
IN_PROGRESS / PREREGISTRATION_DRAFT / HUMAN_REVIEW_APPROVED

Phase F:
IN_PROGRESS / F1_COMPLETE

F1:
COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED

D4 overall completion:
UNDECIDED

Next task recommendation:
E1-R2 outcome-dependent closure or repair decision / NOT AUTHORIZED

Current task authorization:
E1-R2 authorized; human review approved by Jinxin Li; live execution awaits preregistration freeze.

No D4-A11 exists.
No further D4 task is currently authorized.
No further Phase-E task is currently authorized after E1-R2.
No further Phase-F task is currently authorized.

## Phase overview

- **Phase A — Evaluation infrastructure and versioned baseline:** `COMPLETE`
  Evaluation boundaries (`retrieval`, `qa`, `full`), structured trace persistence, and reproducible bootstrap baseline established.

- **Phase B — Indexing and embedding correctness:** `COMPLETE`
  Sparse BM25 IDF contract, explicit 3072-dimensional dense contract, unified sparse encoder factory, precise chunk locators, and structure-aware chunking established. Residual downstream ranking/coverage mechanisms explicitly deferred.

- **Phase C — Retrieval generalization:** `COMPLETE / WITH_DEFERRED_COMPONENTS`
  Query-understanding decomposition and multi-channel retrieval mechanisms evaluated. RawDense remains production-authoritative; experimental semantic, lexical, and entity-first candidates remain shadow, deferred, or rejected. Production selector remains authoritative. Targeted retrieval candidate unification (C8) deferred.

- **Phase D — Concept and entity knowledge abstraction:** `PAUSED / ROADMAP_RECONCILIATION`
  Structured domain concept/entity representation, bounded resolver authority, and generic evidence-link bridging established. Bounded query-expansion migrations are active in production, while broader residual scope remains unreconciled.

- **Phase E — Answer generalization:** `IN_PROGRESS / E1`
  Dynamic question decomposition, answer-point coverage, claim-to-evidence mapping, and targeted completeness recovery.

- **Phase F — Benchmark dependency cleanup and final answering:** `IN_PROGRESS / F1_COMPLETE`
  F1 established the bounded non-D4 residual inventory without production cleanup. F2/F3 and later work remain unstarted; original F3 overlaps D4 and still requires scope reconciliation.

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
IN_PROGRESS / E1

Phase E addresses answer synthesis, facet coverage, claim-to-evidence grounding, and targeted recovery of missing answer points.

### Architecture-level downstream requirements

* **Source and version constraints:** Grounded claims must respect locked repository and document version boundaries.
* **Stable evidence and locators:** Claims must map to stable object IDs and precise line/page/section locators.
* **Relational provenance:** Generated statements reflecting workflows or relations must reflect verified graph structure.
* **Analyzer boundary:** Deterministic vs LLM-derived question semantics must maintain clear provenance boundaries.
* **Query observability:** Distinguish lexical from semantic retrieval contributions during answer verification.
* **Independent answer requirements:** Answer requirements must be derived strictly from question understanding, never inferred post-hoc from retrieved evidence.

### E1 — Dynamic question decomposition

- **Status:** IN_PROGRESS / REPAIR_IMPLEMENTED / REVALIDATION_PENDING
- **E1-A1 outcome:** COMPLETE / PASS / QUESTION_ONLY_DIAGNOSTIC_DECOMPOSITION_IMPLEMENTED. Question-only 1–5 facet contract and explicit shadow diagnostic seam implemented; normal QA does not invoke it. Existing `question_core` remains authoritative and compatibility requirements remain active. Focused fake-based T0 checks passed. E1-A1 PASS is not E1 PASS.
- **E1-A2 outcome:** COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED. Frozen 24-case T2 cohort fully scored: valid 24/24, question-only reference recall 40/44, precision 40/40, under 4/24, over 0/24, exact count 20/24, hidden prerequisites 0. G7 type accuracy 28/40 (70%) and G8 strict reference-conformant pairs 7/12 failed; all other gates passed. Production and preregistration contracts remained unchanged. Small exposed-development results are not release generalization estimates; source and language are confounded.
- **E1-A2 evidence:** `evaluation/e1_a2_dynamic_question_decomposition_validation_result.json`, `evaluation/E1_A2_DYNAMIC_QUESTION_DECOMPOSITION_VALIDATION.md`; preregistration commit `77ea6bc27beb1657673e57be763b05419c98bc05`.
- **E1-AR outcome:** COMPLETE / PASS / REVISED_SEMANTIC_ANSWER_POINT_CONTRACT_ESTABLISHED. Static architectural diagnostics ignoring type: semantic-complete 20/24, semantic-slot stable pairs 10/12; taxonomy disagreements 12/40 matched points; granularity merges in 4 cases. E1-A2 remains FAIL under its original G7/G8; these are not new acceptance results. No implementation or scientific rerun occurred.
- **E1-AR evidence:** `evaluation/e1_architecture_review.json`, `evaluation/E1_ARCHITECTURE_REVIEW.md`.
- **E1-R1 outcome:** COMPLETE / PASS / SHADOW_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIRED. Prompt 2.0.0 / schema e1.question_decomposition.v2 implements obligation atomicity guidance, optional diagnostic taxonomy, and type-independent question-order IDs. Focused v2 T0: 32 passed; real-model repair quality remains unmeasured. Normal QA and compatibility requirements remain unchanged. Historical v1 test fixtures require their original implementation, as documented in the repair report.
- **E1-R1 evidence:** `evaluation/E1_R1_SEMANTIC_ANSWER_POINT_CONTRACT_REPAIR.md`.
- **Evidence:** `evaluation/e1_a1_dynamic_question_decomposition_contract.json`, `evaluation/E1_A1_DYNAMIC_QUESTION_DECOMPOSITION_CONTRACT.md`.
- **E1-R2 status:** IN_PROGRESS / PREREGISTRATION_DRAFT / HUMAN_REVIEW_APPROVED. Authorized prospective T2 uses a draft fresh synthetic exploratory English cohort (24 cases, 12 pairs, 54 reference obligations). Human question/reference/paraphrase review and Git preregistration freeze precede live calls. Scientific execution has not started. Protocol: `evaluation/E1_R2_REVALIDATION_PREREGISTRATION.md`; human review package: `evaluation/E1_R2_COHORT_REVIEW.md`.
- **Next task recommendation:** E1-R2 outcome-dependent closure or repair decision; not authorized. An exploratory synthetic PASS alone does not establish representative PANDA generalization or automatically authorize E2.
- **Problem:** A single `question_core` plus domain-specific requirements can be complete on known questions but miss unseen multi-part structure.
- **Goal:** Derive 1–5 evidence-independent, independently satisfiable explicit response obligations from the question itself, each independently checkable for omission.
- **Why this stage:** Retrieval generalization and structured knowledge must be established before asking decomposition to drive completeness.
- **Intended design:** Question-only semantic obligations with exact support spans and deterministic, type-independent question-order IDs; optional facet taxonomy and ambiguity are diagnostic metadata, not semantic correctness authority. Split independently satisfiable explicit obligations, not merely multiple entities or clauses; preserve a requested comparison or end-to-end flow as one unit absent separate asks. Remain shadow-only alongside existing compatibility requirements.
- **Functional requirements:** Question-only input, 1–5 points, unique code-assigned IDs independent of taxonomy in both sorting and identity, exact question support spans, semantic-slot paraphrase stability, over/under-decomposition checks, and trace/audit output. Literal ID equality across paraphrases is not required.
- **Explicit out of scope:** Deriving points from retrieved evidence, removing existing requirements, targeted retrieval, or benchmark templates.
- **Dependencies:** Phases C/D and curated answer-point annotations.
- **Evaluation scope:** E1-A1 T0, E1-A2 targeted T2, E1-AR static review and E1-R1 implementation/T0 completed. E1-R2 prospective T2 is authorized, with generated-cohort human review approved by Jinxin Li and preregistration freeze pending. No live E1-R2 call or old E1-A2 gate/verdict change occurred.
- **Future primary metrics:** Structural validity, question-only semantic reference-point recall, semantic prediction precision, under/over-decomposition, exact point count, semantic-slot paraphrase stability, and hidden-prerequisite inference. Legacy answer facts are not E1 ground truth.
- **Secondary diagnostics:** Exact facet-type agreement, taxonomy distribution and facet-label paraphrase stability; source-group gaps remain diagnostic. Historical E1-A2's strict reference-conformant pair gate remains unchanged and must not be presented as pure semantic paraphrase stability.
- **Acceptance criteria:** Decomposition captures required question facets generically without mirroring whatever evidence was found.
- **Failure handling:** Repair generic explicit-obligation granularity without benchmark or lexical triggers; keep taxonomy and ambiguity diagnostic and retain old requirements. Freeze any future repair before separately authorized prospective validation. Stop after the current authorized E1 task.

### E2 — Answer-point coverage and claim mapping

- **Status:** NOT_STARTED
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
- **Failure handling:** Keep old completeness checks active and treat mappings diagnostically until reliable. Stop after E2.

### E3 — Missing-point targeted retrieval

- **Status:** NOT_STARTED
- **Problem:** Once a genuine answer point is missing, the system needs a generic retrieval objective rather than hidden domain requirements.
- **Goal:** Use missing answer points to trigger one bounded targeted retrieval, followed by the global C8 merge/rerank/selection path.
- **Why this stage:** Requires proven decomposition, claim mapping, and global targeted-rerank behavior.
- **Intended design:** Initial evidence → point coverage → missing point → targeted retrieval → global rerank → updated evidence → answer/verification.
- **Functional requirements:** Bounded loops, explicit objectives, trace provenance, version safety, recovery measurement, and no arbitrary hidden requirements.
- **Explicit out of scope:** New benchmark rules, unbounded retries, answer composer, or removing compatibility behavior before Phase F.
- **Dependencies:** E1/E2 PASS and C8.
- **Planned evaluation scope (not authorized):** T0, targeted T2 multi-hop/cross-repository/workflow/multi-part novel cases, then small Phase-E T4.
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

### F2 — Generalize benchmark-specific guards

- **Status:** NOT_STARTED / SCOPE_PRESERVED
- **Goal:** Replace hard-coded symbol or premise guards with generic handling of false premises, unknown symbols, locked-corpus existence checks, and generic refusal logic.
- **Scope:** Generalize failure-class guards not reducible to D4 locator migration, ensuring robust behavior across unseen symbols.
- **Dependencies:** F1, C5, D2, and existing verifier contracts.

### F3 — Incremental shortcut removal

- **Status:** SCOPE_RECONCILIATION_REQUIRED / PARTIALLY_SUPERSEDED_BY_D4
- **Goal:** Reconcile residual shortcut removal against completed D4 migrations.
- **Context:** Original F3 planned incremental retirement of phrase-to-answer-location shortcuts once generic replacements were proven. D4 has already implemented this pattern for bounded query-expansion locators. F3 must not duplicate D4; remaining F3 scope is undecided pending residual dependency inventory reconciliation.
- **Dependencies:** F1, F2, and Phase D/E outcomes.

### F4 — Separate answer-generation and semantic-verification roles

- **Status:** NOT_STARTED
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

### F5 — Bounded Answer Composer

- **Status:** NOT_STARTED
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

### F6 — Release evaluation and generalization gate

- **Status:** NOT_STARTED
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

At release, Generalization Gap means benchmark score minus novel score. Benchmark Dependency is the score difference between full compatibility behavior and the approved generic/shortcut-ablation configuration. Neither measurement is authorized here.

## Cross-phase unresolved planning questions

1. **Residual query-expansion impact:** Is residual query-expansion dependency still a material generalization bottleneck in production after the D4-A10 activation?
2. **Remaining D4 candidate disposition:** Does the remaining unassessed D4 inventory contain another naturally testable, high-value migration batch, or should residual entries remain on HOLD?
3. **Phase-F scope boundary:** F1 has established the bounded non-D4 residual inventory and candidate owners. Which candidates warrant a separately authorized treatment remains undecided.
4. **Bottleneck prioritization:** Is answer completeness and decomposition (Phase E) now a larger production bottleneck than residual retrieval shortcut dependency?
5. **Phase execution ordering:** The authorized F1 inventory preceded Phase E and found zero substantiated E1 blockers. E1-A2 remains failed; E1-R1 implements the E1-AR semantic-obligation contract in shadow mode. E1-R2 is authorized and human-approved by Jinxin Li, pending preregistration freeze before prospective execution. No subsequent phase task is authorized.

```text
CURRENT_TASK = E1-R2 / AUTHORIZED / HUMAN_REVIEW_APPROVED
NEXT_TASK_RECOMMENDATION = E1-R2 outcome-dependent closure or repair decision
NEXT_TASK_EXECUTION_AUTHORIZED = false
NEXT_STAGE_AUTHORIZED = false
```
