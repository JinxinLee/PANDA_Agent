# E1-R2 — Prospective Semantic Answer-Point Revalidation

## Current state

DRAFT_PENDING_HUMAN_REVIEW / NOT_EXECUTED. The user authorized E1-R2; scientific
execution remains pending the reviewed-cohort prerequisite. This is a prospective
T2 shadow decomposition experiment, not T3/T5, retrieval, QA, production activation,
or E2/E3. No acceptance verdict exists yet.

Starting and implementation HEAD: `87cc34dd919d8431bb774003a7f76a9fff3a7567`.
The working tree was clean. E1-R1 prompt `2.0.0` and schema
`e1.question_decomposition.v2` are already committed. Do not repair or tune them
using this cohort. E1-A2's original FAIL and all historical artifacts remain intact.

## Hypothesis and cohort

Does the repaired decomposer recover independently satisfiable explicit obligations
without relying on diagnostic taxonomy, while preserving single relational needs
and semantic slots across reordered paraphrases?

The smallest planned targeted cohort is 12 fresh base/paraphrase pairs (24 English
questions). Four single-point bases cover comparison/flow, four two-point bases cover
independent locations/contributions, two three-point bases cover heterogeneous needs,
and one base each exercises four/five obligations. There are 54 reference points.
Questions and references were authored by Codex after the implementation commit and
before any live predictions. They are synthetic exploratory reconstruction/software
needs, not assertions that the named functionality exists in PANDA. No old E1-A2 case,
benchmark source, novel source or protected dataset was loaded for cohort authorship.
Freshness means new prospective measurement, not proven representative novelty.

Exact questions, references, semantic slot IDs, diagnostic types and support spans:
`e1_r2_semantic_answer_point_revalidation_manifest.json`. Readable review package:
`E1_R2_COHORT_REVIEW.md`. Both variants preserve reference text and semantic slot IDs,
while order and exact support spans can change. Literal predicted ID equality across
variants is not required. Human review must confirm explicitness, independent
satisfiability, paraphrase equivalence and exploratory domain relevance. Generated
questions remain untrusted drafts until reviewed under `docs/EVALUATION_POLICY.md`
section 6. Approval must be recorded with reviewer identity and date before freeze;
an agent's static review is not human review.

## Frozen execution and exposure sequence

1. Finish human review and any prospective corrections; record approved status.
2. Commit the manifest, readable review, this preregistration, runner and tests.
   That Git SHA is the preregistration identity. Freeze source/configuration against
   the E1-R1 commit; freeze Python 3.13.14, pydantic 2.13.4 and google-genai 2.13.0.
3. Run `validate`, then `decompose --prereg-commit <SHA>` in manifest order.
   The only model input is the unmodified raw question under the existing decomposer
   contract. References, labels, pair identity and source never enter this call.
4. Persist every attempted decomposition and usage before proceeding. Preserve the
   adapter-returned JSON proposal even if local normalization rejects it, plus the
   normalized result or safe exception types. This is not a complete wire-response
   capture; malformed JSON/transport failures may have no recoverable proposal.
5. Complete all 24 raw records and commit the raw JSON file before any judge call.
   Inspect progress counts only; do not use interim semantic results to select,
   omit, replace or repair cases. The judge phase verifies exact raw Git content.
6. Run `judge --prereg-commit <SHA> --raw-commit <RAW_SHA>` against structurally valid
   records only. Persist judgments separately; never modify frozen decomposition data.
7. Run `report` with those two SHAs after judging. Preserve negative results. Commit
   the completed evidence and status as the authorized formal validation record;
   no push or production activation is part of this task.

All runner commands use `PYTHONPATH=src` and
`python evaluation/run_e1_r2_semantic_answer_point_revalidation.py <phase> ...`.
Validation is offline and permits a pending review. Live phases fail closed on
unreviewed data, missing Git provenance, changed implementation/preregistration,
changed runtime or different configured models. There is no task-level retry or
schema-repair call. Resume skips completed records; a persisted request-started
record is ambiguous and blocks automatic replay. Preserve it for explicit recovery.
Incomplete completed-prefix data can be frozen and reported INCONCLUSIVE without
judging. Interrupted ambiguous requests require an explicit recovery record before
the normal report path; they can never be silently counted as zero-cost success.

## Semantic judge and scoring

The separate evaluation-role client receives only question, reference IDs/text,
and prediction IDs/text. It does not see facet labels, support spans, pairing,
source, legacy rubrics, answers or retrieval evidence. Match needs one-to-one;
a broad point merging independent needs may cover at most one slot. Missing and
extra sets must be the exact unmatched IDs; hidden prerequisites must be extras.
Unknown IDs, repeated matches or duplicate list entries invalidate the judgment.

An inferred setup stage or unstated implementation requirement is a hidden
prerequisite; a redundant version of an explicit need is an extra but not hidden.
Wording elaboration of the same need alone is not another obligation. The judge
considers all candidates before choosing matches. No similarity-score calibration
or Hungarian matcher is introduced without evidence that it improves this contract.
Single-model judgment and reference ambiguity remain limitations, not grounds for
post-outcome threshold changes or selective rejudging.

Primary metrics, computed only when the complete cohort is scoreable:

- Structural validity: valid normalized outputs / 24.
- Micro semantic reference recall: matched pairs / all 54 reference points.
- Micro prediction precision: matched pairs / all valid predicted points; zero
  denominator yields zero. Invalid proposals have no synthetic predictions.
- Under-decomposition: number of cases with missing reference slots, including
  invalid product outputs; over-decomposition: valid cases with unmatched predictions.
  These are semantic omission/extra counts, not merely point-count comparisons.
- Exact count: valid cases whose prediction and reference counts are equal / 24.
- Semantic-complete pairs: both variants valid, fully scored, all slots matched
  one-to-one and no extras. Taxonomy and literal predicted IDs are ignored.
- Hidden-prerequisite prediction count; zero is a hard gate.

Structural product failures count every reference as missing, zero matches, no
invented extras, false exact-count and false pair stability. Provider/configuration
failures and invalid judge responses instead make the run INCONCLUSIVE. Environment
failure is never poor product quality. Partial quality metrics are not authoritative.

| Gate | Threshold |
|---|---|
| Valid cases | >= 23/24 |
| Micro semantic reference recall | >= 0.90 |
| Micro semantic prediction precision | >= 0.90 |
| Under-decomposed cases | <= 4/24 |
| Over-decomposed cases | <= 4/24 |
| Exact-count cases | >= 20/24 |
| Semantic-complete pairs | >= 10/12 |
| Hidden prerequisites | 0 |

These preserve successful historical structural/semantic tolerance levels while
prospectively adopting the architecture's semantic-only pair contract. There is no
type-accuracy gate. An invalid five-slot output consumes five of the allowed missed
slots: gates are conjunctive and micro averaging deliberately weights obligations.
No thresholds depend on E1-R2 results. Historical E1-A2 gates are not rewritten.
Predicted label distribution, omitted labels, exact label agreement among labeled
semantic matches and failure categories are secondary diagnostics only.

## Models and cost

Current configured generation and evaluation-judge models are both
`gemini-3.8-flash`, location `global`, temperature 0, timeout 120000 ms. They use
separate role clients, not independent model families. Existing transport retry
policy permits up to three adapter requests per logical call; no fallback/model
switching or live smoke is added. Budget: 24 decomposition calls, <=24 judge calls,
<=48 logical calls, <=144 adapter attempts. Underlying SDK transport behavior is
not separately instrumented. Record returned model/generation/embedding counters
and token usage per role, including errors; returned tokens may omit failed-request
usage. Do not present logical call counts as billing or HTTP-level request counts.
Token and monetary cost cannot be known before execution; no dollar estimate is
claimed. Analyzer, embeddings, reranker, QA and retrieval calls remain zero.

One AGY static design-review job completed (`staffer-mtrzkpt8p`), separately from
the scientific call budget. Runner routing reported `gemini-3.8-flash-high`; the
worker self-reported Gemini 3.8 Flash / High, not independently attested. Its actual
provider call/token totals are unavailable, not zero. Only the authored abstract
protocol was supplied, without historical data or repository files. No worker edits.
Review feedback clarified metric denominators, pair semantics and limitations.
Its suggestion that exact count constrains semantic under/over counts was rejected:
equal counts can contain both missing and extra needs. A score-matrix matcher was
not adopted because it adds an unvalidated scoring contract. The single-model risk
is retained explicitly. Agent review is not approval of the questions/references.

## Verdict and lifecycle

Preparation checks completed before human review: targeted runner tests passed
24/24 initially, 24/24 after scoring/runtime-identity changes, and finally 27/27
after adding raw-freeze boundary tests. The offline `validate` command returned
static_contract PASS, human_review pending, live_calls 0. `git diff --check` passed.
Production source/configuration and historical E1-A2 runner, tests and scientific
artifacts have no diff. No full suite or historical scientific rerun was performed.
Scientific decomposition/judge calls and returned tokens are zero so far; the AGY
review usage is separately unavailable as recorded above. Preparation is not an
experimental PASS. Changes remain uncommitted while the cohort awaits review.

PASS requires complete scoring and every primary gate. It supports the bounded
synthetic exploratory shadow validation only, not a representative PANDA
generalization estimate or production readiness. FAIL requires complete scoring
with a failed product gate. INCONCLUSIVE covers incomplete execution/scoring.
With only one base each for four/five-point strata, no stratum-wide accuracy claim
is justified. Paired questions are correlated, not 24 independent samples.

Current E1-R2 = IN_PROGRESS / PREREGISTRATION_DRAFT / HUMAN_REVIEW_PENDING.
E1 = IN_PROGRESS / REPAIR_IMPLEMENTED / REVALIDATION_PENDING.
After a bounded PASS, recommend an E1 closure/scope decision before starting E2;
do not automatically close general E1 acceptance from an exploratory cohort.
FAIL requires separately authorized repair; INCONCLUSIVE requires a recovery
decision. No subsequent task is authorized. D4 remains PAUSED with overall
completion UNDECIDED; F1 and Phase F remain unchanged; E2/E3 are NOT_STARTED.
