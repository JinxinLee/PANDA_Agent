# E1-A2 — Targeted Dynamic Question Decomposition Validation

## Decision

**FAIL / PRODUCT_QUALITY_GATES_FAILED: G7 and G8.** All 24 frozen cases completed and were scoreable; no provider or judge-infrastructure failure occurred. Matched facet-type accuracy was 28/40 = 70%, below 90%. Strict reference-conformant paraphrase stability was 7/12, below 10/12. These failures are not waived by the passing recall, precision, validity or hidden-prerequisite gates.

| Gate | Observed | Frozen threshold | Outcome |
|---|---:|---:|---|
| G1 valid decomposition | 24/24 | >=23/24 | PASS |
| G2 reference-facet recall | 40/44 = 90.91% | >=90% | PASS |
| G3 prediction precision | 40/40 = 100% | >=90% | PASS |
| G4 under-decomposed cases | 4/24 | <=4/24 | PASS |
| G5 over-decomposed cases | 0/24 | <=4/24 | PASS |
| G6 exact point count | 20/24 | >=20/24 | PASS |
| G7 matched facet type | 28/40 = 70% | >=90% | **FAIL** |
| G8 stable paraphrase pairs | 7/12 | >=10/12 | **FAIL** |
| G9 hidden prerequisites | 0 points | =0 | PASS |

## Repository / preregistration identity

- Starting HEAD / E1-A1 implementation: `709321657016762ee11ee38d21d53c30ffa7b951`.
- Preregistration commit: `77ea6bc27beb1657673e57be763b05419c98bc05` (`E1-A2 preregister decomposition validation`). It preceded the first live provider request.
- Frozen decomposition prompt `1.0.0`, schema `e1.question_decomposition.v1`. Production prompt set remains `3.7.0`.
- Preregistration report, manifest, runner and tests were unchanged after live execution began. No production source/configuration changed from the starting HEAD.
- Closeout uses one subsequent normal Git commit; no push, tag, hash inventory or production activation.

## Frozen cohort

12 bases + 12 same-language controlled paraphrases = 24 cases / 12 pairs / 44 references. Six bases from benchmark dev (`m6-benchmark-v2.6`), six from novel_dev (`novel-v1-dev-0.3.0`). Base language counts: Chinese 6, English 6. Base facet-count strata: single 4, double 6, triple 2. Each count doubles at the case level; no other development source was used.

Base IDs in order: g063, g067, g072, g073, g066, g081, n001, n008, n020, n022, n030, n031. Exact source paths, raw wording, reference needs, support spans and controlled paraphrases remain in the frozen manifest. No question or reference was replaced after outcomes.

## Execution boundary

Command, once: `python evaluation/run_e1_a2_dynamic_question_decomposition_validation.py --run`, with `PYTHONPATH=src` and UTF-8 output. Sequential direct `QuestionDecomposer.decompose(question)` calls; normalized valid points alone proceed to the question/reference/prediction judge. The normal QA graph and retrieval were never instantiated by the scientific runner.

Pre-run fake verification: the initial runner-test collection failed because its dynamic import was not registered; this was repaired before freeze. Then `python -m pytest tests/unit/test_e1_a2_dynamic_question_decomposition_validation.py -q` passed 24 tests, and passed 24 again after final pre-freeze exception/persistence handling changes. `python -m pytest tests/unit/test_question_decomposition.py -q` passed 19. The runner without `--run` validated the manifest without creating provider clients. Base questions/source versions were mechanically checked against development-only projections. All pre-run provider calls were zero.

Post-run `python evaluation/run_e1_a2_dynamic_question_decomposition_validation.py --verify` reproduced frozen records, call counts, metrics and gates. A separate read-only Python calculation independently checked all 24 unique ordered case IDs, exact questions/references, support spans, one-to-one matches, G1–G9 and physical usage sums. No cases were missing or extra. No provider rerun occurred. `git diff --check` passed; production and preregistration path diffs were empty.

## Structural validity

24/24 = 100%; all predictions passed the unchanged exact-span, count, enum, duplicate-text and ID contract. Judge output validation also passed for all 24.

| Failure category | Count |
|---|---:|
| SCHEMA_VALIDATION | 0 |
| INVALID_SUPPORT_SPAN | 0 |
| DUPLICATE_POINT | 0 |
| POINT_COUNT | 0 |
| OTHER_VALIDATION | 0 |
| PROVIDER_INFRASTRUCTURE | 0 |
| EVALUATION_INFRASTRUCTURE (separate judge category) | 0 |

## Reference-facet recall and precision

Question-only reference recall: 40/44 = 90.91%. Prediction precision: 40/40 = 100%. These are the preregistered E1-specific reference metrics, not legacy Gold answer-rubric recall. No legacy Gold metrics were substituted. Successful cases satisfying semantic coverage, no extras and exact reference types: 15/24.

## Over- and under-decomposition

Under-decomposed: 4/24 = 16.67%; over-decomposed: 0/24. Exact count: 20/24 = 83.33%.

Both variants of pair05 (g066) merged the separately requested locations of the two angular models into one point. Both variants of pair09 (n020) merged the contributions of two explicitly named downstream stages into one point. Under the frozen one-to-one rule, each merged point matches at most one independent reference, leaving one missing slot per case. The broad predicted texts mention both requested objects/stages; the scored deficit is independently addressable point granularity, not proof that the model failed to mention the second object at all. No post-outcome reannotation was performed.

## Facet-type accuracy

28/40 = 70%. Twelve semantic matches used a different facet label from the frozen reference:

- Pair06 (g081): producer/consumer identity needs were tagged `data_flow`, reference `locator` (4 mismatches).
- Pair07 (n001): encoded environment constraints/variable assignment were tagged `implementation` instead of `constraint`/`api_behavior`; the paraphrase's unmatched-input behavior used `mechanism` instead of `api_behavior` (5 mismatches).
- Pair08 (n008), paraphrase: approach identification used `implementation` instead of `definition` (1 mismatch).
- Pair09 (n020), both variants: a matched stage-contribution point used `mechanism` instead of `workflow` (2 mismatches).

These type mismatches count exactly as preregistered. Semantically matched text with another label is not automatically a missing information need. The evidence motivates reviewing operational facet definitions and granularity before prescribing a bounded implementation repair; it does not justify rewriting references or lowering G7 after the run.

## Paraphrase stability

7/12 = 58.33% satisfy the full frozen rule. Stable pairs: 01, 02, 03, 04, 10, 11, 12. Non-conforming pairs: 05, 06, 07, 08, 09.

This metric requires correctness against reference slots/types for both variants, not merely similarity between variants. Pairs05 and 09 consistently merge needs; pair06 consistently uses a different taxonomy label. Pair07 changes the unmatched-input label between variants, and pair08 changes the approach-identification label. Therefore five failed pairs must not be described as five observed semantic paraphrase drifts. The G8 result remains 7/12 without a post-hoc alternative gate.

## Hidden-prerequisite audit

0 hidden-prerequisite predictions, 0 affected cases, 0 extras. All 24 judges returned empty hidden-prerequisite lists. This passes the hard G9 gate on this small cohort only, not a universal guarantee against hidden inference.

## Secondary diagnostics

Ambiguity: 0/24. Precision and validity are 100% in every reported source/language/variant/count stratum.

| Group | Cases | Recall | Type accuracy | Exact count | Stable pairs |
|---|---:|---:|---:|---:|---:|
| Base | 12 | 20/22 = 90.91% | 15/20 = 75% | 10/12 | N/A |
| Paraphrase | 12 | 20/22 = 90.91% | 13/20 = 65% | 10/12 | N/A |
| Benchmark dev / Chinese | 12 | 14/16 = 87.50% | 10/14 = 71.43% | 10/12 | 4/6 |
| Novel dev / English | 12 | 26/28 = 92.86% | 18/26 = 69.23% | 10/12 | 3/6 |
| Single reference | 8 | 8/8 = 100% | 8/8 = 100% | 8/8 | 4/4 |
| Two references | 12 | 22/24 = 91.67% | 17/22 = 77.27% | 10/12 | 3/6 |
| Three references | 4 | 10/12 = 83.33% | 3/10 = 30% | 2/4 | 0/2 |

Pair stability is not applicable within a base-only or paraphrase-only slice. The frozen helper mechanically emits zero complete pairs in those slices; those zeros are not evidence of instability. The authoritative paired result uses all 24 records.

Benchmark-minus-novel diagnostic gaps: recall -5.36 percentage points; precision 0; validity 0. Sources are fully confounded with language and have different count strata. These are not release-level or causal generalization estimates.

| Reference facet | Recall | Matched type accuracy |
|---|---:|---:|
| definition | 4/4 | 3/4 |
| mechanism | 2/2 | 2/2 |
| implementation | 4/4 | 4/4 |
| data_flow | 4/4 | 4/4 |
| comparison | 6/6 | 6/6 |
| locator | 8/10 | 4/8 |
| workflow | 2/4 | 0/2 |
| cause_reason | 4/4 | 4/4 |
| api_behavior | 4/4 | 1/4 |
| constraint | 2/2 | 0/2 |

Facet prediction precision is 100% wherever at least one point was predicted. No points used `workflow` or `constraint`; their frozen zero-denominator precision value is 0, not a measured false-positive rate. Full counts remain in the result JSON.

## Model/token accounting

Both configured roles used `gemini-3.8-flash` in Vertex `global`, temperature 0, separate generation/evaluation clients. No alternate model or fallback.

| Logical call role | Calls |
|---|---:|
| Analyzer | 0 |
| Embedding | 0 |
| Reranker | 0 |
| QA answer | 0 |
| QA review | 0 |
| QA revision | 0 |
| Retrieval | 0 |
| Decomposition | 24 |
| Semantic judge | 24 |
| Total model calls | 48 |

| Actual client counter | Decomposition | Judge | Total |
|---|---:|---:|---:|
| model_calls | 24 | 24 | 48 |
| generation_calls | 24 | 24 | 48 |
| embedding_calls | 0 | 0 | 0 |
| token_usage | 31,820 | 31,798 | 63,618 |

The physical request counters equal logical calls; no adapter transport retries were observed. Both decomposition and semantic evaluation are structured-generation requests in Vertex counter terminology; none is QA answer generation. Monetary billing was not measured.

## Protected-data accounting

novel_validation question content accessed = no. novel_holdout accessed = no. Protected split content accessed = no. Legacy Gold required_answer_points used as E1 ground truth = no. Development discovery displayed only allowed projected question fields, never protected questions or legacy rubric annotations. Source datasets were not modified.

## Limitations

Small purposive development-exposed cohort; source/language and source/count-mix confounding; host-authored reference labels and paraphrases without independent human semantic review; a single model family serves both separate roles. Exact type agreement depends on the frozen annotation choices and should be distinguished from semantic coverage. No prompt repair, alternative scoring, statistical population claim, multilingual activation, retrieval/QA evaluation, E2 coverage or E3 recovery was performed. The result is a valid failure under this preregistered contract.

## Lifecycle decision

E1-A2 = COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED.
E1 = IN_PROGRESS / VALIDATION_FAILED. Phase E = IN_PROGRESS / E1.
E1-A1 remains accepted as a diagnostic implementation; `question_core` and all compatibility requirements remain authoritative and unchanged. Production activation = false.

D4 = PAUSED / ROADMAP_RECONCILIATION; D4 overall completion = UNDECIDED. F1 remains COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED. Phase F = IN_PROGRESS / F1_COMPLETE.

## Next task recommendation

E1 ARCHITECTURE REVIEW: review generic facet-label boundaries and independently addressable point granularity using the preserved evidence, before authorizing any repair or new validation. NEXT_TASK_EXECUTION_AUTHORIZED = false. No E2, E3, F2, F3 or rerun was executed. Stop after the closeout commit.
