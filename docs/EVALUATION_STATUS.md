# PANDA QA Agent — Evaluation Status

This file records transient evaluation state: current Gold/evaluator versions, candidate status, unresolved cases, run provenance, metrics, hashes, and historical checkpoints.

Stable evaluation rules belong in `docs/EVALUATION_POLICY.md`.
Day-to-day Codex behavior belongs in `AGENTS.md`.

When records conflict, use the single section explicitly marked **Current authoritative state**.

---

# Current authoritative state — 2026-08-13

## A3 measured execution provenance

- Base Git commit when the A3 measurements started: `e132accefc8181abba76e8d818a621dd03cd1c9c`.
- Working tree: dirty because A1–A3 and governance changes were then uncommitted.
- The measurements therefore represent that base commit plus the then-current working-tree changes. This is valid prototype diagnostic provenance, not a frozen candidate identity.
- A later user-created commit or newer repository HEAD does not rewrite this measured execution identity and does not require an evaluation rerun.
- Prompt set: `3.6.0`.
- Generation and runtime verifier role: `gemini-3.6-flash`.
- Evaluation judge configuration: `gemini-3.6-flash`; it was not invoked by the current retrieval or small QA baseline.
- Dense embeddings: `gemini-embedding-2`, configured 3072 dimensions.
- Sparse encoder: `Qdrant/bm25`, English, local-files-only.
- Index identity: `c527bbf1d10c88969da02745d678c640a4544757258584110a5ddd7744be3cf2` (`index_schema_version=2`).
- Gold: v2.6, identity `b5406e36c64ee664f9e2ff9c0f42e354feb7164c81d8f1c7551d8f2ed1d0b687`.

## Generalization Phase status

- Bootstrap tasks A1, A2, and A3: `PASS`.
- Evaluation modes: `retrieval`, `qa`, and `full` have explicit recorded boundaries.
- Structured retrieval traces are persisted as atomic JSON and JSONL and can be loaded without rerunning QA.
- A3 was corrected from a possible full-retrieval interpretation to a stratified low-cost bootstrap baseline. No T3 or full 120-question retrieval/E2E run was performed.
- Later architecture tasks B1–F6 remain `NOT_STARTED`.

## Historical full E2E reference

The newest trustworthy complete E2E artifact selected for historical reference is:

`data/evaluation/runs/m6-v2-36-qa-dev-rc3e`

It is a complete 80-question dev run with 514 model calls and 6,389,043 tokens. Measured metrics include `gold_recall_at_10=1.0`, `final_evidence_recall=0.9482323232`, `critical_final_evidence_recall=0.9482323232`, `answer_point_coverage=0.9458333333`, `citation_integrity=1.0`, `intent_accuracy=0.9875`, and `expected_status_accuracy=1.0`.

It does **not** match the A3 measured execution provenance exactly: the historical manifest predates explicit Git commit recording and used Gold v2.4 plus prompt set 3.5.0. It is historical evidence, not a current release claim.

## English Gold Stratified Bootstrap Baseline

Versioned package:

`evaluation/baselines/english-gold-stratified-bootstrap-v1-20260813`

Fixed selection manifest:

`evaluation/baselines/manifests/english_gold_stratified_bootstrap_v1.json`

This is a low-cost English Gold reference, not a complete generalization, complete benchmark, or all-intent baseline. Future before/after comparisons must reuse the fixed 24 retrieval and 16 QA IDs unchanged; a different selection requires a new manifest identity.

### Current stratified retrieval baseline

- Run: `generalization-a3-stratified-retrieval-20260813`.
- Mode/cases: `retrieval`, 24 approved English Gold questions.
- Cost: 72 runtime model calls, 482,907 tokens, 0 external-judge calls.
- Measured: Recall@5 `0.8416666667`; Recall@10 `0.9`; Recall@20 `0.9`; MRR `0.6866666667`; combined candidate recall `0.95`; final-evidence recall `0.9`; intent accuracy `1.0`; no exceptions.

### Current small E2E baseline

- Run: `generalization-a3-stratified-qa-20260813`.
- Mode/cases: `qa`, 16 approved English Gold questions; runtime generation and verification enabled, external judge disabled.
- Cost: 76 runtime model calls, 819,872 tokens, 0 external-judge calls.
- Measured: Recall@5 `0.6041666667`; Recall@10 `0.75`; Recall@20 `0.75`; MRR `0.65`; combined candidate recall `0.875`; final-evidence recall `0.7083333333`; expected-status accuracy `1.0`; citation integrity `1.0`; identifier hallucination rate `0.0`; no exceptions.
- Answer-point coverage is N/A because the external rubric judge was deliberately disabled.
- External-rubric contradiction and unsupported-claim metrics were likewise not measured; corrected package artifacts represent all three metric families as N/A rather than synthetic zero/clean values.

The retrieval and QA measurements are unchanged. A3.1 corrects only metric representation, portable artifact paths, consistency metadata, and measured-execution provenance wording; historical model outputs remain untouched.

## Novel dataset state

- `novel_dev`: 0.
- `novel_validation`: 0.
- `novel_holdout`: not created; the runner supports loading it from an external path.
- Human-curated: no trustworthy human-authored novel dataset is currently available.
- Empty novel JSONL artifacts are schema/placeholders, not measured results.

## Known limitations

- Gold v2.6 has no eligible approved English questions for `data_flow`, `module_structure`, or `troubleshooting`; these intents are unevaluated in this bootstrap baseline.
- `algorithm_implementation` has only two eligible approved English questions, so that stratum is exhausted rather than evenly sized.
- The current baseline measures exposed English Gold behavior, not genuinely novel-question generalization.
- Historical E2E and current baseline identities differ, so their metric differences are not a controlled before/after comparison.

## Next authorized roadmap task

`B1 — Correct sparse BM25 / Qdrant IDF contract`

---

# Historical records

## Historical authoritative snapshot — 2026-08-09

Gold v2.6 (`b5406e36…b687`) 与 evaluator 2.6.1 已按签署的 RC3f regression 人工审查落地。`g087/g097/g116` 及 `g098/g111` 两个 sentinel 的 focused run 全部通过；没有重跑完整 16 题。将 13 个已接受原始结果与 3 个 replacement 合成后，16/16 的 Gold recall、final evidence、source coverage、answer-point coverage、citation integrity 和 intent/status accuracy 均为 1.0，错误计数均为 0。

该结果是 reviewed diagnostic composite：`diagnostic_quality_checks.passed=true`，但因 mixed runtime provenance 不宣称 formal frozen-candidate regression gate。完整证据、hash、运行目录与边界见 `docs/M6_REGRESSION_RC3F_REVIEW_FIX_RESULT.md`。

---

## Historical authoritative snapshot — 2026-08-04

**Status date:** 2026-08-04

## 1. Current Gold and evaluator

Current official Gold:

```text
evaluation/benchmarks/v2_2/gold_questions.yaml
```

SHA-256:

```text
d65783d4712676af60a1d1b69f7a344d9898ae9c86914c7629c6daaffe4fe156
```

Current evaluator:

```text
evaluator-2.2
```

Official Gold validation:

```text
120/120
unmatched = 0
```

Current deterministic unit-test baseline:

```text
85 passed
```

## 2. Current benchmark exposure

The exposed benchmark contains 120 approved cases:

- `dev`: 80
- `challenge`: 24
- `regression`: 16

These 120 cases are exposed development/evaluation assets and are not hidden acceptance.

Current hidden acceptance state:

```text
not_created
```

The exposed benchmark is therefore:

```text
release_eligible = false
```

Do not treat dev/challenge/regression as hidden acceptance.

## 3. Current runtime identity

Current runtime model:

```text
gemini-3.6-flash
```

Current evaluation judge:

```text
gemini-3.6-flash
```

Embedding model:

```text
gemini-embedding-2
```

Current answer Prompt version after the mixed claim-noise behavior fixes:

```text
3.1.0
```

The previously frozen candidate `m6-v2-36-rc2b` is historical and no longer represents the current implementation identity because later source/Prompt behavior changed.

## 4. Current failure-review state

Current integrated review state:

```text
36 resolved
12 real failures pending
```

The 12 currently excluded real-failure cases in the 68-case diagnostic composite are:

```text
g023
g025
g039
g057
g060
g063
g073
g088
g089
g095
g110
g114
```

These failures must be handled through targeted fixes/focused reruns before a new formal candidate is frozen.

## 5. Evaluator-2.2 narrow corrections

The evaluator-2.2 corrections for `g074`, `g079`, and `g086` are intentionally narrow.

### g074

Accepted contract:

- intent: `data_flow`;
- blocking source: `code`;
- adapter implementation is sufficient to answer;
- paper/upstream implementation is context rather than a blocking source.

### g079

Only inside the signed Gold selector's `Lumi_TrksQA` data-product group, two explicitly approved direct-code locators may count as equivalent evidence.

This is **not** a repository-wide graph-to-code heuristic.

### g086

Implementation source is the blocking source.

Documentation is optional/diagnostic rather than required.

After evaluator-2.2 offline rescore, these three cases pass the relevant intent/evidence/required-source/answer-point/citation checks, with no wrong-version or major-unsupported failure under the approved narrow contract.

## 6. Current 68-case diagnostic composite

Current composite output:

```text
data/evaluation/rescores/
m6-v2-36-qa-dev-rc2b-evaluator-2_2-d65783d47126-90547a6958bf/
```

It represents the 80-case dev run excluding:

```text
g023 g025 g039 g057 g060 g063
g073 g088 g089 g095 g110 g114
```

Permitted replacements in this composite are:

```text
status run:
  g041 g119

synthetic-noise run:
  g011 g074 g079 g085 g086
```

`g089` is explicitly **not** replaced.

The composite added:

```text
model_calls = 0
token_usage = 0
```

Historical source-record usage must not be reported as new composite cost.

Because the synthetic replacements do not share the original RC2b prompt identity, the composite must preserve:

```text
diagnostic_composite_runtime = true
uniform_candidate_identity = false
complete_v2_dev = false
subset_diagnostic_only = true
```

Consequences:

- the composite is diagnostic only;
- it cannot pass the complete development gate;
- it cannot freeze a candidate;
- it cannot unlock regression;
- it cannot unlock challenge;
- it cannot unlock acceptance;
- it cannot unlock M7/M8.

## 7. Mixed claim-noise behavior fixes

The focused behavior-fix run covered:

```text
g011
g074
g079
g085
g086
g089
```

Run directory:

```text
data/evaluation/runs/m6-v2-36-synthetic-noise-fix-6-v1/
```

Result:

```text
6/6 answered
```

User-visible leakage of internal coverage/provenance claims was reduced to zero for this focused run.

Relevant runtime rule:

- `scope_*`
- `required_workflow`
- `required_code`
- `dataflow_locator_*`
- text containing `curated_panda_domain`

may remain in internal `claim_audit`, but must not be rendered as user-facing answer claims.

Focused run usage:

```text
model calls: 40
tokens: 410,412
runtime calls/tokens: 34 / 362,661
judge calls/tokens: 6 / 47,751
elapsed: 343.7 s
```

Focused answer-point coverage:

```text
94.44%
```

Known remaining issue in this group:

```text
g089: judge still marks p2 missing
```

The focused run is not a complete dev result and does not mean M6 passed.

## 8. Current authorization / next allowed work

At the current state:

**Allowed:**

- targeted fixes for the 12 real failures;
- rerun directly affected cases;
- add a very small number of directly relevant sentinels when useful;
- deterministic unit tests;
- offline rescore for evaluator/Gold/scoring-only changes;
- targeted work on `g089` and other confirmed real failures.

**Not yet authorized as the default next step:**

- another complete 80-case dev run;
- complete 16-case regression;
- challenge;
- hidden acceptance;
- M7;
- M8.

A new complete dev run becomes appropriate only after the current fix batch has been validated and a new candidate is intentionally frozen.

---

# Historical evaluation record

The following entries are retained for provenance. They are not the current candidate identity.

## A. evaluator-2.1 / Gold v2.1 offline correction

Historical Gold:

```text
evaluation/benchmarks/v2_1/gold_questions.yaml
```

Dataset SHA:

```text
1fea656c1ea05ac2cf4bbb78e8e712fec3c09e40c31f5d77a914fa7cadbd9d22
```

Historical unified rescore output:

```text
data/evaluation/rescores/
m6-v2-36-qa-dev-rc2b-evaluator-2_1-1fea656c1ea0/
```

The 31-case correction process preserved original records, used offline rescoring for scoring/Gold/selector changes, and reran only behavior-affected cases.

This state is superseded by Gold v2.2 / evaluator-2.2.

## B. RC2b formal dev checkpoint

Historical frozen candidate:

```text
m6-v2-36-rc2b
```

Historical candidate manifest SHA:

```text
a3810966dd1a9347033005f2f83e8142f84b2ab57d50d3252a8e005e83a661d9
```

The frozen 80-case dev run:

```text
m6-v2-36-qa-dev-rc2b
```

completed:

```text
80/80
```

but failed the development gate.

Because later source/Prompt behavior changed, RC2b is no longer the current implementation identity.

No full regression/challenge/acceptance was authorized from that failed candidate.

## C. Candidate v8 checkpoint

Historical run:

```text
m6-qa-dev-candidate-v8
```

It resumed from `53/80` using the same run ID and completed `80/80` without rerunning completed cases.

Historical gate failures included:

```text
unsupported claims: 5
required identifier missing: 1
answered required-source coverage: 0.9873
```

The v8 state was later superseded by the Benchmark v2 / evaluator correction work.

## D. Candidate v5 checkpoint

Historical result:

```text
m6-qa-dev-candidate-v5
80/80 completed
development gate failed
```

Recorded metrics:

```text
Gold Recall@10: 0.9833
answer-point coverage: 0.9125
intent accuracy: 0.9875
expected-status accuracy: 1.0
citation integrity: 1.0
wrong-version evidence: 0
unhandled exceptions: 0
unsupported claims: 5
identifier hallucination: 1/400 (0.0025)
model calls: 498
token usage: 6,067,814
```

This record is historical only.

## E. v2-lite RC1 baseline

Historical candidate:

```text
m6-v2-lite-rc1
```

Historical complete dev result:

```text
80/80 completed
development gate failed
```

Recorded metrics:

```text
Recall@10: 79.06%
final evidence recall: 53.81%
answer-point coverage: 71.15%
citation integrity: 100%
wrong-version evidence: 0
unhandled exceptions: 0
expected-status accuracy: 91.25%
intent accuracy: 92.5%
major unsupported claims: 4
contradictions: 1
critical answer-point misses: 39
runtime/judge calls: 406/80
total token usage: 4,494,556
```

This older baseline is superseded by later candidate/evaluator states.

---

# Maintenance rules for this file

Update this file when any of the following changes:

- approved Gold version/hash;
- evaluator version;
- runtime/judge/embedding model identity;
- prompt identity relevant to evaluation;
- benchmark split/acceptance state;
- current frozen candidate;
- complete formal run result;
- integrated failure-review count;
- authoritative unresolved-case list;
- authorization to proceed to regression/challenge/acceptance/M7/M8.

Do not update this file for every ordinary code edit.

When adding a new current state:

1. add a new dated **Current authoritative state** section or update the existing one;
2. move superseded candidate/run details into **Historical evaluation record**;
3. clearly mark superseded identities as historical;
4. never rewrite historical model-call/token usage as if it belonged to a newer offline rescore.
