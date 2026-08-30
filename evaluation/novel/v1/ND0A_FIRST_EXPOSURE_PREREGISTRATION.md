# ND-0A — First Novel-Dev Exposure Preregistration

- Checkpoint: **ND-0A** (pre-outcome preregistration subphase of **ND-0 — First Frozen Novel-Dev Generalization Baseline**)
- Status: **PRE_OUTCOME_PREREGISTRATION_FROZEN**
- Preregistered: 2026-08-30
- Machine-readable counterpart: `evaluation/novel/v1/nd0a_first_exposure_preregistration.json` (schema `nd0a-preregistration-v1`)
- Preregistration source HEAD: `e40ac8099607e83f720b103d7da80a85aab697ab` ("D2 A2R2 repair target-scoped evaluation accounting")

This document freezes, **before any novel outcome exists**, what the first novel_dev measurement will be, how it will be reported, and what it will be compared against. It is a preregistration, not a result report: it contains **no novel outcome metrics**, because none exist.

## 1. Why ND-0 exists

The repository now owns three protected novel evaluation cohorts that have never been touched by the system: `novel_dev` (28 frozen questions), `novel_validation` (15 frozen questions), and an externally sealed `novel_holdout` (expected 13 questions). All development so far has been measured on exposed Gold cohorts (Phase B/C replay cohorts, bootstrap baselines). The known weakness of that history is selection effects: development and evaluation have repeatedly seen the same question population, and the C6 novel corroboration gate (`NEW_PRODUCTION_POLICY_ACTIVATION = NOT_AUTHORIZED_BY_C6_A2_ALONE`) exists precisely because no independent cohort has ever corroborated a candidate.

ND-0 is the first controlled exposure of the frozen novel_dev split to the current production retrieval path. Its purpose is to produce one clean, preregistered generalization baseline plus a failure-class diagnosis, and to hand that diagnosis to D2-A3. It is deliberately a measurement-and-diagnosis checkpoint, not a repair task.

## 2. Why ND-0 happens before D2-A3 and D3

- D2-A3 is the resolver production-role decision (`KEEP_SHADOW` / `DEVELOPMENT_SUPPORTED_CANDIDATE` / limited role / production-authoritative). It must not be decided on Gold-derived evidence alone for the same selection-effect reason that blocked C6 candidates. ND-0C feeds ND-0B's generic failure diagnosis into that decision; D2-A3 therefore remains **NOT_STARTED** until ND-0 completes.
- D3 (downstream architecture work) would otherwise lack any independent evidence about which failure classes actually dominate on unseen questions.
- Exposing novel_dev before freezing this contract would make every later comparison post hoc. Freezing first preserves the interpretive value of this one first measurement. Novel_dev exposure is one-way: after ND-0B it is development-exposed forever, which is exactly why the single first measurement is preregistered.

Lifecycle flow: **D2-A2R2 → ND-0A → ND-0B → ND-0C → D2-A3 → D3**. ND-0 is a cross-phase evaluation checkpoint, not a D2 implementation stage.

## 3. Provenance

- This preregistration was authored and frozen at repository HEAD `e40ac8099607e83f720b103d7da80a85aab697ab` (the D2-A2R2 closeout commit, "D2 A2R2 repair target-scoped evaluation accounting").
- The ND-0A commit that introduces this artifact into history is created **after** this file is written; its SHA is intentionally not recorded here and must not be backfilled later.

## 4. Current production roles (provenance only; no promotion or demotion)

Recorded from `docs/EVALUATION_STATUS.md`, section **Current authoritative state — 2026-08-30** (D2-A2R2):

| Component | Role |
| --- | --- |
| Production exact | `LEGACY_EXACT` |
| Production sparse | the exact raw question |
| RawDense | `PRODUCTION_AUTHORITATIVE` |
| SemanticDense | `KEEP_DISABLED` (auxiliary-shadow only) |
| Fusion | `P0 CURRENT` / `PRODUCTION_AUTHORITATIVE` |
| P3 SPARSE_HEAVY | `DEVELOPMENT_SUPPORTED_CANDIDATE` |
| C6_INTENT_AWARE_V1 | `DEVELOPMENT_SUPPORTED_CANDIDATE` |
| Selector | `CURRENT_SELECTOR` / `PRODUCTION_AUTHORITATIVE` |
| `c7.explicit_selection.v1` | `REJECTED_AS_GLOBAL_PRODUCTION_REPLACEMENT` |
| D2 resolver | `SHADOW` (diagnostic-only; not applied in the production retrieval path) |
| D2-A3 | `NOT_STARTED` |

ND-0 changes none of these. The P3 and C6_INTENT_AWARE_V1 candidates remain blocked from production activation by the absent novel corroboration gate — which ND-0B is the first step toward addressing, without prejudging its outcome.

## 5. novel_dev frozen identity

From `evaluation/novel/v1/manifest.json` (schema `novel-manifest-v1`):

- split `novel_dev`; dataset_identity `novel-v1-dev-expansion`; benchmark_version `novel-v1-dev-0.3.0`; dataset_version `0.3.0`; status `COMPLETE`.
- question_count **28**; independent_family_count **28**; frozen_count **28**.
- Review state: `approved` by Li, `human_approval: complete` (28 accepted / 0 revise / 0 rejected / 0 pending); curation origin `human_directed_llm_draft`; locked corpus manifest `data/manifests/source_manifest.json`.
- Representativeness: 26 `KEEP_REPRESENTATIVE` / 2 `KEEP_EXPLORATORY` (classification outcomes, not quotas).
- `agent_outcome_seen_before_freeze: false`; `evidence_selected_from_agent_output: false`.

**Explicit outcome-exposure statement:** `NOVEL_DEV_OUTCOME_OBSERVED_BEFORE_ND0 = false` and `FIRST_NOVEL_DEV_MEASUREMENT_RUN = NOT_RUN`. This is bound to the manifest governance fields above (`agent_outcome_seen_before_freeze`, `evidence_selected_from_agent_output`) and to the human curation review records (N2 plan, N2-B review package, N2 finalization report; README statement that no PANDA Agent retrieval, QA, judge, runtime evaluation, or novel evaluation has run for this curation) — not merely to the absence of run files. Correspondingly: `FIRST_NOVEL_DEV_OUTCOME_EXPOSURE = NOT_STARTED` and `NOVEL_DEV_DEVELOPMENT_EXPOSED = false`.

## 6. ND-0B measurement contract (frozen; not executed here)

- **Dataset / cohort:** `novel_dev`, **28/28 cases** — the full frozen set. No sampling; no cohort splitting for the primary measurement.
- **Mode:** `retrieval` (retrieval-only). The current production retrieval path runs unchanged: `LEGACY_EXACT` exact, raw-question sparse, RawDense authoritative (SemanticDense disabled), P0 CURRENT fusion, `CURRENT_SELECTOR`, D2 shadow resolver not applied. Production retrieval is not modified for this measurement.
- **Prohibited in ND-0B:** QA generation, runtime answer generation, answer verifier, answer revision, external rubric judge, T5.
- **Prohibited-stage counters (preregistered at zero):** `QA_GENERATION_CALLS = 0`, `ANSWER_VERIFIER_CALLS = 0`, `EXTERNAL_JUDGE_CALLS = 0`.
- **Model-call policy:** total model calls are **not** preregistered as zero. The current production retrieval path may legitimately use model/API-backed components (query analyzer, dense embedding, reranking where applicable); these are authorized production components, not evaluation add-ons.
- **Failure handling:** if infrastructure failure interrupts ND-0B, partial runs are preserved and handled explicitly; partial runs are never silently redefined into a completed measurement.

## 7. Primary metric contract (frozen before outcomes)

All metrics reuse the existing authoritative evaluator semantics (frozen evidence-group matcher in `panda_agent.evaluation`) unchanged. **No new relevance semantics are invented for novel_dev**, and no question-specific relevance handling is introduced.

| Metric (preregistered name) | Evaluator key | Definition | Applicability |
| --- | --- | --- | --- |
| Recall@5 | `gold_recall_at_5` | Fraction of required evidence groups matched in the top-5 ranked candidates | `PARTIALLY_APPLICABLE` |
| Recall@10 | `gold_recall_at_10` | Fraction of required evidence groups matched in the top-10 ranked candidates | `PARTIALLY_APPLICABLE` |
| Recall@20 | `gold_recall_at_20` | Fraction of required evidence groups matched in the top-20 ranked candidates | `PARTIALLY_APPLICABLE` |
| MRR | `mrr` | Mean reciprocal rank of the first required-evidence-group match within the top-20 ranked candidates | `PARTIALLY_APPLICABLE` |
| Combined candidate recall | `combined_candidate_recall` | Fraction of required evidence groups matched within the combined channel candidate pool (pre-selection union) | `PARTIALLY_APPLICABLE` |
| Critical evidence recall | `critical_final_evidence_recall` | Fraction of required evidence groups marked `critical: true` matched in the final selected evidence set | `PARTIALLY_APPLICABLE` |
| Final evidence recall | `final_evidence_recall` | Fraction of required evidence groups matched in the final selected evidence set | `PARTIALLY_APPLICABLE` |

**Applicability rationale:** every metric above is ordinary-applicable only for `expected_status = answered` cases under the existing evaluator (`ordinary_applicable = case.expected_status == QAStatus.ANSWERED`). novel_dev contains 27 answered and 1 `insufficient_evidence` record, so each metric's denominator is 27 of 28 via the evaluator's native `metric_applicability` mechanism; the refusal-type case is covered by expected-status/refusal semantics instead. The novel_dev schema does support the metrics (per-record `required_evidence_groups` with `critical` flags exist), so nothing is `NOT_APPLICABLE`; the honest label for all seven is `PARTIALLY_APPLICABLE` (applicable denominator 27/28).

## 8. Stratified reporting contract (frozen before outcomes)

Reporting is the full 28-case aggregate plus the existing frozen curation-metadata groupings only. **No post-outcome grouping scheme may be created.** Groupings frozen now, with their supporting frozen metadata (`evaluation/novel/v1/coverage_report.json`, `evaluation/novel/v1/curation_metadata.yaml`):

- **Intent** — frozen distribution: installation 2, usage 9, api 3, algorithm_theory 3, algorithm_implementation 5, data_flow 2, module_structure 2, troubleshooting 2.
- **Evidence topology** — single_hop 14, multi_hop 6, comparison 5, producer_consumer 3.
- **Source topology** — per-record `source_types` (required source types in the dataset).
- **Single-repository vs cross-repository** — single_repository 25, cross_repository 1, paper_only 2.
- **Single-evidence vs multi-evidence** — multi_evidence_count 17.
- **Curation family / family class** — 28 independent families (`curation_family_id`) with family class as recorded in the frozen sidecar.
- **Representative vs exploratory disposition** — 26 `KEEP_REPRESENTATIVE` / 2 `KEEP_EXPLORATORY`.

Small-dimension policy: dimensions with very small cell counts (for example cross_repository = 1, paper_only = 2) are reported as counts only, without strong comparative claims. No protected novel_validation or external-holdout metadata is exposed by this contract.

## 9. Comparison-reference contract (frozen before outcomes)

**Selected reference:** `english-gold-stratified-bootstrap-v1-20260813` — the English Gold Stratified Bootstrap Baseline.

- Selection manifest: `evaluation/baselines/manifests/english_gold_stratified_bootstrap_v1.json` (baseline_id `english-gold-stratified-bootstrap-v1`, frozen case IDs with a reuse rule).
- Artifact directory: `evaluation/baselines/english-gold-stratified-bootstrap-v1-20260813` (`baseline_manifest.json`, `implementation_identity.json`, `benchmark_retrieval_baseline.jsonl`, `benchmark_retrieval_traces.jsonl`).
- Measurement: retrieval mode over 24 English Gold v2.6 questions; benchmark retrieval run id `generalization-a3-stratified-retrieval-20260813`; created 2026-08-12.
- Frozen reference metrics (retrieval): Recall@5 0.8417, Recall@10 0.9000, Recall@20 0.9000, MRR 0.6867, combined candidate recall 0.95, critical final evidence recall 0.9000, final evidence recall 0.9000.
- Why this one: it is the only existing artifact that is (a) a retrieval-mode measurement, (b) over a frozen, documented cohort with a selection manifest, and (c) recorded with exactly the metric set preregistered above. The alternative inventory candidate, `generalization-a3-bootstrap-20260813-limited`, is a preserved 1-question smoke ("not the A3 baseline", superseded by the stratified baseline) and is rejected. **No new Gold benchmark is run for ND-0.**

**Comparability classification:** `comparability_status = APPROXIMATE / NON_IDENTICAL_COHORT`; `configuration_comparability = NON_IDENTICAL_CONFIGURATION`. The two measurements are not interchangeable, and this preregistration does not pretend they are. High-level production roles are broadly continuous, but **role-level continuity does not imply identical retrieval configuration, query-analysis generation, index contents, chunking state, sparse identity, or implementation provenance** (`role_level_continuity = true`; `retrieval_state_identity = false`).

Supporting comparability:

- Both measurements are retrieval-only and use the same authoritative evaluator metric semantics.
- Retrieval channel roles are unchanged across the interval per the lifecycle role statements at C6/C7/D1/D2 closeouts (exact `LEGACY_EXACT`, raw-question sparse, RawDense authoritative with SemanticDense disabled, P0 fusion, `CURRENT_SELECTOR`, D2 shadow resolver not applied).
- Embedding model configuration is continuous at the model level (`gemini-embedding-2`, 3072 dimensions on both sides); model-configuration continuity is NOT index identity, index-schema, index-contents, or chunking-state continuity.

**Index/configuration mismatch (ND-0A-R1 provenance correction).** The historical Gold retrieval did **not** run on the current index:

| Aspect | Gold reference | Current ND-0 | Comparable? |
| --- | --- | --- | --- |
| Measurement mode | retrieval | retrieval | yes |
| Embedding model | `gemini-embedding-2` | same | largely |
| Embedding dimension | 3072 | 3072 | yes |
| Sparse model | `Qdrant/bm25` (no modifier/parameters recorded) | `Qdrant/bm25`, modifier `idf`, schema-4 portable receipt | governance evolved; scoring equivalence not claimable |
| Index schema | 2 | 4 | no |
| Index identity | `c527bbf1d10c88969da02745d678c640a4544757258584110a5ddd7744be3cf2` | `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9` | no (`INDEX_IDENTITY_CHANGED = true`) |
| Corpus/index state | pre-B5 | post-B5: 133075 SQL objects / 104973 Qdrant points | no (`CORPUS_INDEX_STATE_CHANGED = true`) |
| Prompt set | 3.6.0 | 3.7.0 | no |
| Base commit | `e132acce` (dirty tree) | `e40ac80` | no (coarse provenance) |
| Production role labels | broadly similar | current roles | partial (continuity only) |
| Question cohort | 24 Gold v2.6 | 28 novel_dev | no |

`REEMBEDDING_REQUIRED = false` / `INDEX_REBUILD_REQUIRED = false` / `QDRANT_SCHEMA_CHANGE_REQUIRED = false` describe the **current pending-change state** at the preregistration source head, not historical continuity from 2026-08-13 to ND-0A; using them as index-identity continuity evidence is invalid and superseded. Sparse-contract note: the governed sparse identity/factory contract (explicit `idf` modifier, schema-4 portable receipt) was introduced after the baseline (B1/B3); the historical artifact records no sparse modifier or parameters. The governance/identity contract demonstrably evolved (`SPARSE_CONTRACT_EVOLVED = true`); whether retrieval scoring behavior itself differed at baseline time is not claimable from the recorded artifacts and is not asserted — the two are kept distinct.

Mismatch dimensions (recorded explicitly):

1. **Non-identical cohort.** 24 Gold v2.6 questions vs 28 novel_dev questions: different question sets, different intent mixes; the Gold baseline has no evaluated data_flow, module_structure, or troubleshooting questions, while novel_dev includes them.
2. **Analyzer generation.** The baseline was measured at prompt_set_version **3.6.0**; current production is **3.7.0** (`PROMPT_SET_VERSION` in `src/panda_agent/prompts.py`). C6-A1R1 recorded 0/46 current-plan channel-input compatibility with the frozen 3.6.0-era streams, so the query-analysis layer demonstrably changed after the baseline.
3. **Provenance coarseness.** The baseline was executed from base commit `e132acce` (2026-08-12) with a dirty working tree; that provenance predates the Phase C evaluation-infrastructure work and Phase D (D1/D2).
4. **Index identity.** Schema 2 (`c527bbf1…`) vs schema 4 (`8172f9a6…`, 104973 points): the Gold run did not use the current index.
5. **Corpus/index state.** The Gold baseline predates the B5 selective index/chunking migration; the current corpus is the post-B5 state (133075 SQL objects / 104973 Qdrant points / schema 4).
6. **Sparse contract.** Governed sparse identity/factory (explicit `idf` modifier, schema-4 portable receipt) introduced after the baseline (B1/B3); scoring-behavior equivalence is not claimable from artifacts.

**Reporting plan:** for Recall@5, Recall@10, Recall@20, MRR, critical evidence recall, and final evidence recall (combined candidate recall as a secondary diagnostic), report three columns — Gold/reference, novel_dev (ND-0B, not yet run), and the gap. If either side lacks comparable support for a metric, the cell is marked **UNAVAILABLE** rather than synthesized. **Gap interpretation (frozen):** the gap is a historical cross-cohort AND cross-configuration reference difference. It is not an apples-to-apples treatment effect, must not be attributed solely to novel-question generalization, and must not be interpreted as "same system + different dataset only". The gap reflects a combination of: question-population difference; analyzer-generation difference; historical provenance difference; index/corpus-state difference; and potentially other recorded configuration evolution. It is never used alone to justify production changes. The Gold reference remains useful as a historical scale reference, a directional comparison, and rough generalization context; it is simply not a controlled current-system baseline.

**Provenance correction record (`PRE_OUTCOME_PROVENANCE_CORRECTION`, ND-0A-R1, 2026-08-30):** the original ND-0A preregistration (commit `06b68c8`) historically contained an incorrect same-index comparability statement ("Index identity unchanged … index schema v2", supported by the no-pending-rebuild flags). That statement and the flag-based continuity inference were false. ND-0A-R1 corrected the comparison provenance **before ND-0B / first novel outcome exposure**; Git history preserves the original ND-0A wording. The selected Gold reference, the ND-0B measurement contract, the primary metric set, and the diagnosis taxonomy are unchanged by this correction.

## 10. ND-0C diagnosis taxonomy (frozen)

ND-0C classifies ND-0B misses into generic failure classes. The categories are frozen now; they name classes of failure for any unseen question, never specific questions. `INFRASTRUCTURE_FAILURE` and `UNCLASSIFIED` are explicit outcomes; an infrastructure failure is never counted as a retrieval failure. `EXPECTED_EVIDENCE_MAPPING_ISSUE` and `EVALUATION_CASE_ISSUE` record suspected dataset-side causes; they are diagnoses, not justifications for editing frozen Gold.

`CHANNEL_RECALL_FAILURE`, `FUSION_OR_RANKING_FAILURE`, `RERANK_FAILURE`, `FINAL_SELECTOR_FAILURE`, `SOURCE_SCOPE_FAILURE`, `VERSION_SCOPE_FAILURE`, `ENTITY_OR_TERMINOLOGY_RELATED`, `EXACT_IDENTIFIER_FAILURE`, `DESCRIPTIVE_TERMINOLOGY_FAILURE`, `CROSS_REPOSITORY_FAILURE`, `MULTI_EVIDENCE_FAILURE`, `CORPUS_OR_INDEX_COVERAGE_FAILURE`, `EXPECTED_EVIDENCE_MAPPING_ISSUE`, `EVALUATION_CASE_ISSUE`, `INFRASTRUCTURE_FAILURE`, `UNCLASSIFIED`.

## 11. ND-0C development rule (frozen)

After ND-0B finishes, novel_dev becomes `DEVELOPMENT_EXPOSED`: later development may use it for generic debugging and iteration. But ND-0 artifacts — including this preregistration — must never be overwritten by later novel_dev iterations, and future novel_dev reruns use new run/checkpoint identities rather than overwriting ND-0 records.

## 12. novel_validation protection

From `evaluation/novel/v1/novel_validation_manifest.json`: split `novel_validation`, dataset_identity `novel-v1-validation-expansion`, benchmark_version `novel-v1-validation-0.2.0`, question_count **15**, frozen_count **15**, human approval `complete`, measurement **NOT_RUN**. Role: **FROZEN / UNSEEN / ONE_SHOT_LATER**. ND-0 does not run it, does not inspect outcomes on it, and does not use it to select or tune anything.

## 13. External holdout — sealed registration reference

A separate ND-0A workstream maintains the registration record `evaluation/novel/v1/external_holdout_manifest.json`. This artifact records only the user-authorized non-sensitive metadata:

- schema `external-holdout-v1`; dataset_identity `panda-novel-holdout-v1`; split `novel_holdout`; status `FROZEN_SEALED`; externally_managed `true`; expected_count **13**; content_repository_visible `false`; outcome_observed `false`; loader contract `--dataset <external-path>`; authorized use: **release/T5 only**.

This preregistration does not locate, inspect, or describe the external holdout beyond these fields, and records no real filesystem path for it.

## 14. Protected-evaluation ladder

| Cohort | Size | State | Next use |
| --- | --- | --- | --- |
| `novel_dev` | 28 frozen | outcome unseen before ND-0 | first development exposure under ND-0 (ND-0B) |
| `novel_validation` | 15 frozen | unseen | one-shot measurement later |
| `novel_holdout` | 13 expected | frozen/sealed externally; content not repository-visible; outcome unseen | release/T5 only |

## 15. Lifecycle placement and expected closeout state

ND-0 is a cross-phase evaluation checkpoint (**not** a D2 implementation stage) with subphases ND-0A (pre-outcome preregistration — this artifact) → ND-0B (first 28-question retrieval measurement) → ND-0C (generalization diagnosis and D2-A3 handoff). Flow: D2-A2R2 → ND-0A → ND-0B → ND-0C → D2-A3 → D3. **D2-A3 remains `NOT_STARTED`.**

Expected state after ND-0A closes: `ND-0 = IN_PROGRESS`; `ND-0A = COMPLETE / PRE_OUTCOME_PREREGISTRATION_FROZEN`; `ND-0B = NOT_STARTED`; `ND-0C = NOT_STARTED`; `FIRST_NOVEL_DEV_OUTCOME_EXPOSURE = NOT_STARTED`; `NOVEL_DEV_DEVELOPMENT_EXPOSED = false`.

## 16. Explicit no-outcome statement and next step

**No novel outcome has been observed.** No retrieval, QA, judge, or evaluation runner has been executed on novel_dev, novel_validation, or any novel split in the preparation of this preregistration; this artifact and its JSON counterpart contain no novel outcome metrics, because none exist.

**Next step: ND-0B** — execute the frozen measurement contract in Section 6 against novel_dev under the frozen metric contract (Section 7), and report per the frozen stratified reporting (Section 8) and comparison-reference contract (Section 9). No other stage may run first.
