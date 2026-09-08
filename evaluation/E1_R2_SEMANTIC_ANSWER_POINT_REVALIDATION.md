# E1-R2 — Prospective Semantic Answer-Point Revalidation Closeout

COMPLETE / PASS / TARGETED_PROSPECTIVE_SEMANTIC_ANSWER_POINT_REVALIDATION_PASSED.

The repaired semantic answer-point contract passed the frozen targeted prospective
synthetic exploratory E1-R2 cohort. This is shadow-only T2 evidence, not representative
PANDA generalization, production readiness, E1 closure or authorization to start E2.

## Approval and immutable provenance

- Execution starting HEAD / approved amended cohort: `4cd0305c53541bcba75c00fbf935d87c63ba3069`.
- E1-R1 implementation: `87cc34dd919d8431bb774003a7f76a9fff3a7567`.
- Preregistration commit: `3d0d8ca650d159681fecec324a081d28e8e945eb`.
- Raw decomposition commit: `a5275dfee6c4134f3ad790a5598ca0c0a51f1a58`.
- Closeout commit: the Git commit introducing this report, judgments, result and lifecycle update.
- Human approval: Jinxin Li, recorded `2026-09-08T13:48:52+02:00` per explicit user instruction.

The execution turn began with five approval/documentation edits from the preceding
approval-recording step; these were reviewed and included in preregistration. No
question, reference text, semantic slot, span, pair, shape, stratum or scientific
design changed after approval. All 24 raw records were completed and committed
before the first judge call. No task-level retry, replacement, selective rejudging,
prompt repair, model switch or interim semantic-performance inspection occurred.

Prompt `2.0.0`; schema `e1.question_decomposition.v2`; Python `3.13.14`, pydantic
`2.13.4`, google-genai `2.13.0`. Generation and separate evaluation-role clients
both used `gemini-3.8-flash`, Vertex `global`, temperature 0, timeout 120000 ms.
Source/configuration and frozen runner, judge, scorer, tests and protocol were unchanged.

## Primary results

All 24 cases are structurally valid and all 24 judgments are scoreable.

| Gate | Observed | Frozen threshold | Verdict |
|---|---|---|---|
| G1 Structural validity | 24/24 | >=23/24 | PASS |
| G2 Semantic reference recall | 54/54 (100%) | >=90% | PASS |
| G3 Semantic prediction precision | 54/54 (100%) | >=90% | PASS |
| G4 Under-decomposed cases | 0/24 | <=4/24 | PASS |
| G5 Over-decomposed cases | 0/24 | <=4/24 | PASS |
| G6 Exact point count | 24/24 | >=20/24 | PASS |
| G7 Semantic-complete pairs | 12/12 | >=10/12 | PASS |
| G8 Hidden-prerequisite predictions | 0 | 0 | PASS |

Semantic-complete cases: 24/24. G1–G8 here label the eight named gates in the
frozen result; they are not historical E1-A2 gate identifiers. Taxonomy was excluded
from judge payloads, semantic matching, pair stability and primary acceptance.

## Reference-count strata

Counts include each base and its paraphrase; these are correlated pairs.

| Base reference count | Bases | Cases | Reference recall | Exact-count cases | Semantic-complete cases |
|---|---:|---:|---:|---:|---:|
| 1 | 4 | 8 | 8/8 (100%) | 8/8 | 8/8 |
| 2 | 4 | 8 | 16/16 (100%) | 8/8 | 8/8 |
| 3 | 2 | 4 | 12/12 (100%) | 4/4 | 4/4 |
| 4 | 1 | 2 | 8/8 (100%) | 2/2 | 2/2 |
| 5 | 1 | 2 | 10/10 (100%) | 2/2 | 2/2 |

No stratum-wide accuracy claim follows from the single four-point or five-point base.

## Failure and taxonomy diagnostics

Under the frozen semantic judgment, observed semantic granularity merges, semantic
over-splits, semantic slot omissions, relational over-splits, hidden prerequisites,
structural product failures and provider/evaluation infrastructure failures are all
zero. No failure repair was performed. This is the recorded judge-based result,
not an independent human adjudication of every generated prediction.

52/54 predictions carried a recognized diagnostic label; two omitted it. Among the
52 labeled semantic matches, 43 had exact reference-label agreement and nine differed.
Label distribution: locator 14, mechanism 13, comparison 6, data_flow 2, definition 7,
api_behavior 3, cause_reason 5, implementation 1, constraint 1, omitted 2. These
diagnostics do not affect PASS. Missing labels did not invalidate semantic points.

## Scientific cost

| Role | Logical calls | Returned model calls | Generation calls | Returned tokens |
|---|---:|---:|---:|---:|
| Decomposition | 24 | 24 | 24 | 30056 |
| Semantic judge | 24 | 24 | 24 | 24885 |
| Total | 48 | 48 | 48 | 54941 |

Analyzer = 0; Embedding = 0; Reranker = 0; Retrieval = 0; QA answer = 0;
QA review = 0; QA revision = 0. No adapter-level retry is indicated by the returned
request counters. SDK-level HTTP/billing request counts are not separately observable;
logical counts are not billing counts. Monetary cost was not measured.

No AGY/subagent was added for execution or closeout. The earlier static-design job
`staffer-mtrzkpt8p` is separate from scientific usage; its actual provider calls and
tokens remain unavailable, not zero. It did not review intermediate outcomes.

## Verification and artifacts

Before freeze: existing focused R2 tests 27/27 passed, offline validate PASS,
approved-review validation PASS, exact approved-cohort comparison PASS, frozen
implementation/models/runtime match, and `git diff --check` PASS. After freeze:
offline validate PASS, 24 raw records reconciled in manifest order before their
commit, and all frozen input paths verified unchanged before judging.

After judging: the frozen deterministic report returned PASS. An independent
read-only reconciliation checked exact case order, reference/prediction match ID
sets, support-span validity, complete judgments, strata, usage sums and unchanged
approved case content. No model calls were made by verification. Frozen files and
historical E1-A2 artifacts have no diff. No full suite, T3/T4/T5, retrieval benchmark,
QA evaluation or E1-A2 scientific rerun occurred.

Scientific artifacts:

- `e1_r2_semantic_answer_point_revalidation_raw.json`
- `e1_r2_semantic_answer_point_revalidation_judged.json`
- `e1_r2_semantic_answer_point_revalidation_result.json`

## Historical authority and lifecycle

E1-A2 remains COMPLETE / FAIL /
G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED. E1-R2 does not regrade it.
The cohorts and pair criteria differ, so these are not paired before/after causal
metrics; a numeric gain cannot be attributed solely to repair from this comparison.

E1-R2 = COMPLETE / PASS /
TARGETED_PROSPECTIVE_SEMANTIC_ANSWER_POINT_REVALIDATION_PASSED.
E1 = IN_PROGRESS / REPAIR_PROSPECTIVELY_VALIDATED / CLOSURE_REVIEW_PENDING.
Phase E = IN_PROGRESS / E1. E2 = NOT_STARTED. E3 = NOT_STARTED.
D4 = PAUSED / ROADMAP_RECONCILIATION; overall completion = UNDECIDED.
F1 = COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED.
Phase F = IN_PROGRESS / F1_COMPLETE. Production activation = false.

NEXT_TASK_RECOMMENDATION = E1 CLOSURE / SCOPE REVIEW.
NEXT_TASK_EXECUTION_AUTHORIZED = false. No subsequent task executed.

The fresh prospective synthetic exploratory cohort supports the repaired semantic
contract at this targeted scope. Purposive shape selection, 12 correlated pairs,
small upper-count strata, same-family generation/judging and absence of representative
PANDA sampling limit generalization. A separate closure review should decide whether
this is sufficient for E1 or a small real PANDA-style exposed-development confirmation
is warranted. That review is not authorized or performed here.
