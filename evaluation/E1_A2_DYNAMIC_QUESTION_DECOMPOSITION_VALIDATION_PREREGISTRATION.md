# E1-A2 — Targeted Dynamic Question Decomposition Validation Preregistration

## Scientific question

Can the frozen E1-A1 real-model decomposer recover explicit information needs from a raw question as 1–5 diagnostic points, without omissions, unnecessary splits, hidden prerequisites, or controlled-paraphrase instability? This is a prospective 24-case T2 decomposition evaluation, not QA/retrieval evaluation or production activation.

## Frozen implementation identity

Starting HEAD and E1-A1 implementation: `709321657016762ee11ee38d21d53c30ffa7b951` (`E1-A1 add diagnostic question decomposition`). Starting worktree was clean. Decomposition prompt `1.0.0`, output schema `e1.question_decomposition.v1`, production prompt set unchanged at `3.7.0`. Production source/configuration will remain unchanged. Commit 1 freezes this report, manifest, runner and focused tests; its actual Git SHA will be recorded in results. No hash inventory.

## Data-protection boundary

`docs/EVALUATION_POLICY.md` identifies development benchmark measurement separately from protected acceptance/release gates, and preserves non-English diagnostic use. `docs/NOVEL_DATASET_CURATION_CONTRACT.md` section 4.1 explicitly identifies `novel_dev` as exposed development data. `evaluation/novel/v1/README.md` confirms the approved frozen dev dataset identity. The status history identifies Gold v2.6 as an exposed historical benchmark baseline.

Sources: `evaluation/benchmarks/v2_6/gold_questions.yaml`, `m6-benchmark-v2.6`, filtered to `split=dev`; `evaluation/novel/v1/novel_dev.yaml`, `novel-v1-dev-0.3.0`, filtered to `split=novel_dev`. Discovery projected only `id`, `query`, `split`, and `language`, plus top-level version. YAML parsing mechanically reads the source file; no legacy answer rubric fields or non-dev benchmark question content were displayed or used for reference authorship. No protected novel question file, external holdout, or protected question content was inspected. Curation README protection metadata is not question content.

Chinese source questions are explicitly authorized diagnostic measurements here. No Chinese product support, runtime change, or release claim is authorized.

## Cohort construction

Purposive exposed-development sample, frozen before outcomes. Base sources in pair order: `g063`, `g067`, `g072`, `g073`, `g066`, `g081`, `n001`, `n008`, `n020`, `n022`, `n030`, `n031`. Each base immediately precedes its paraphrase in execution order. No replacement or omission is permitted after execution begins.

Shape coverage (base cases, overlap allowed): comparison 3 (`g072`, `n008`, `n031`); workflow/data-flow 2 (`n020`, `n022`); locator/cause-reason 5 (`g073`, `g066`, `g081`, `n020`, `n030`); implementation/API-behavior 3 (`g063`, `g067`, `n001`); definition/mechanism/constraint 4 (`n001`, `n008`, `n030`, `n031`). No shape or source-balance deviation is needed. Source and language are fully confounded: all six benchmark bases are Chinese, all six novel bases English. Source gaps cannot isolate generalization from language or shape mix.

## Question-only annotation protocol

References were authored by the host agent using raw question semantics only, without legacy Gold answer points, required symbols/repositories, answer facts, retrieved evidence, or model predictions. Each reference has a unique question-specific ID, semantic pair slot, frozen generic facet type, English need description, and exact source-question support spans.

Independent explicitly requested needs are separate slots: `g066` asks separately where each named model is implemented; `g081` asks for producer and consumer. `n001` separately requests encoded environment pairs/paths, assigned variables, and unmatched-input behavior. `n020` separately requests the leftover-hit task and the contribution of each of two explicitly named downstream stages. These slots do not enumerate unstated workflow stages. A pure comparison stays one comparison; `n008` and `n031` explicitly ask an additional identification need. No answer is encoded in references.

Frozen E1-specific question-only reference-facet recall replaces legacy Gold answer-point recall for this acceptance decision. Legacy rubrics can require answer facts or hidden completeness; those are not the information needs E1 is meant to decompose. No legacy Gold metrics will be added and no Gold data modified. This scientific interpretation is fixed before execution.

## Controlled paraphrase protocol

Exactly one host-authored, same-language paraphrase per base, created without decomposition outputs. Preserve technical identifiers literally and preserve the original constraints, explicit needs, and reference slot/facet mapping. Only the question wording and its exact support spans change; reference descriptions stay the same. No translation, extra detail, or hidden need is introduced. Mechanical slot/span checks supplement manual prospective text review; there is no independent human semantic reference review.

## Frozen cohort summary

12 bases + 12 paraphrases = 24 cases, 12 pairs, 44 reference points. Base distribution: benchmark_dev 6, novel_dev 6; Chinese 6, English 6; single-facet 4, two-facet 6, three-facet 2. Total case distribution doubles each base group.

Base facet counts: implementation 2, comparison 3, cause_reason 2, locator 5, constraint 1, api_behavior 2, definition 2, workflow 2, data_flow 2, mechanism 1. Exact questions, references, spans and source versions are in `e1_a2_dynamic_question_decomposition_validation_manifest.json`.

The focused tests validate 24 unique cases, 12 pairs, one base/paraphrase each, exact spans, unique references/slots, matching pair slot types and languages, count strata, and explicit source allowlists. Protected or unknown groups/paths/splits are rejected.

## Semantic judge contract

The runner owns the frozen strict `Judgment` JSON schema and `JUDGE_PROMPT`. A separate configured evaluation-role client receives only raw question, frozen reference points and normalized prediction points. It does not receive source group, language labels, retrieval plans/evidence, QA answers or legacy rubrics. No answer or chain-of-thought is requested.

References are authoritative. Match semantic information needs one-to-one regardless of wording or facet label; merged independent needs cover at most one slot. Missing and extra IDs must equal the exact unmatched sets. Hidden prerequisite IDs must be a subset of extras introducing an unstated prerequisite, answer fact, domain stage, implementation component or benchmark-shaped obligation. Redundant explicit needs are extras but are not automatically hidden prerequisites.

The `facet_type_match` flag means exact equality of supplied facet strings; local validation checks it against both points. Unknown IDs, duplicate pairings/list entries, wrong unmatched sets, wrong equality flags and hidden IDs outside extras invalidate the judge output. No repair or second judge call. Invalid judge output is evaluation-infrastructure incomplete, never a product score fabricated by the host.

## Structural failure semantics

Each case calls the unchanged `QuestionDecomposer.decompose(question)` directly, never the QA graph. A returned proposal rejected by its contract is a product failure. Fixed taxonomy: SCHEMA_VALIDATION, INVALID_SUPPORT_SPAN, DUPLICATE_POINT, POINT_COUNT, OTHER_VALIDATION, PROVIDER_INFRASTRUCTURE. Pydantic root point-count violations use POINT_COUNT; other Pydantic shape errors use SCHEMA_VALIDATION. The adapter's wrapped malformed JSON/empty structured response is also SCHEMA_VALIDATION. Transport/configuration failures are infrastructure, not poor decomposition.

Invalid decompositions receive no judge call; all reference slots count missing, matched count is zero, exact count is false and pair stability is false. No synthetic predictions/extras are manufactured. Provider messages are not copied with credentials: records retain exception/cause types and safe validation diagnostics. Judge failures are recorded separately as EVALUATION_INFRASTRUCTURE.

Records are persisted after decomposition starts, after its result, before judging and after judging, using atomic replacement of the small JSONL snapshot with one row per case. This preserves completed evidence without adaptive selection. Existing output files prohibit automatic reruns. Unexpected non-generation model counters stop execution. Incomplete execution yields INCONCLUSIVE and no authoritative partial-quality gate decision.

## Metrics

M1 valid cases / 24. M2 matched references / all 44 frozen references. M3 matched predictions / all predicted points in valid decompositions. If no predictions or no matched pairs exist, the corresponding ratio is 0, not a vacuous pass.

M4 cases with missing references / 24 (includes product-invalid decompositions). M5 valid cases with extra predictions / 24; invalid output has no synthetic extras. M6 valid cases with predicted count equal to reference count / 24. M7 exact facet-type matches / semantic matched pairs. M8 hidden-prerequisite point count and affected-case count.

M9 stable pairs / 12: both variants valid and fully scored, no missing slots or extras, all frozen slots matched one-to-one, every matched facet type equal. Literal predicted IDs need not agree across paraphrases. M10 all six structural failure categories, including zeros, plus separate judge-infrastructure count.

Secondary diagnostics: ambiguity among all 24 cases; metrics by base/paraphrase, language, source group and reference-count stratum; facet-specific reference recall, prediction precision and matched-type accuracy. Benchmark-minus-novel recall, precision and valid-rate gaps are small-sample diagnostics only. Quality metrics are authoritative only for a fully scoreable cohort; raw incomplete case evidence is retained without partial PASS/FAIL.

## Acceptance gates

| Gate | Frozen threshold |
|---|---|
| G1 | Valid decompositions >= 23/24 |
| G2 | Micro reference-facet recall >= 0.90 |
| G3 | Micro prediction precision >= 0.90 |
| G4 | Under-decomposed cases <= 4/24 |
| G5 | Over-decomposed valid cases <= 4/24 |
| G6 | Exact point-count cases >= 20/24 |
| G7 | Matched facet-type accuracy >= 0.90 |
| G8 | Stable paraphrase pairs >= 10/12 |
| G9 | Hidden-prerequisite predictions = 0 (hard gate) |

## Provider-call budget

Currently configured generation role: `gemini-3.8-flash`; evaluation-judge role: `gemini-3.8-flash`; Vertex location `global`. Separate clients use existing `VertexSettings.from_env()` and `for_generation_model()`. Exact model/location values are checked against the manifest before live execution. Temperature remains 0. No model selection, fallback, task retry, or extra live smoke.

Logical budget: exactly 24 decomposition calls; one judge call per structurally valid output, at most 24; total at most 48. Analyzer, embeddings, reranker, QA answer/review/revision and retrieval calls are zero. Existing transport retries remain unchanged; record per-role and total actual `model_calls`, `generation_calls`, `embedding_calls`, `token_usage` independently of logical calls. Token usage is the adapter's returned usage counter, not an estimate for failed requests.

## PASS / FAIL / INCONCLUSIVE semantics

PASS / QUESTION_ONLY_DYNAMIC_DECOMPOSITION_VALIDATED requires all 24 cases scoreable, no unresolved infrastructure failure, and all G1–G9 passing. Complete scoring with any failed product gate yields FAIL / PRODUCT_QUALITY_GATES_FAILED. Incomplete provider/judge execution yields CLOSED_INCONCLUSIVE / EVALUATION_INFRASTRUCTURE_INCOMPLETE. Invalid model proposals remain scoreable product failures. No failed case may be dropped or replaced.

PASS completes E1 at this bounded development scope but keeps it shadow-only; recommend E2 without authorizing it. FAIL leaves E1 IN_PROGRESS / VALIDATION_FAILED and recommends E1 ARCHITECTURE REVIEW pending a separately authorized repair decision. INCONCLUSIVE leaves validation pending and any rerun requires separate authorization. D4 remains paused with completion undecided; F1 and Phase F remain unchanged.

## No-mid-run-repair rule

Commit this preregistration before the first live request. Thereafter do not change cohort, questions, paraphrases, references, production source/configuration, prompts, models, schema, judge/scorer, metrics or thresholds. Run all cases sequentially in frozen order, reporting progress counts only until complete. Preserve any negative result and stop at E1-A2 closeout.

Pre-run verification uses fake clients only. The first test collection exposed a dynamic-import registration issue; registering the test-loaded module fixed it before freeze. Focused runner tests: 24 passed. Existing E1-A1 focused tests: 19 passed. Changes after those tests are checked again before Commit 1. `git diff --check` and staged scope review are required. No live provider call has occurred while authoring this preregistration.
