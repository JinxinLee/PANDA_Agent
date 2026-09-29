# G5 Integrated Candidate Design

## Decision and boundary

**G5_INTEGRATED_CANDIDATE_DESIGN = PASS / EXECUTION READY.** This is a design decision, not an empirical G5 result or authorization to run the evaluation. The accepted G1 and G2 behavior, G3 `NO_CHANGE`, and the corrected G4 R2 behavior already coexist on the normal product path. G5 will assess that path as one integrated development candidate. No product, prompt, configuration, schema, test, dataset, Gold, calibration, or runtime-mode change is selected.

```text
G5_PRODUCT_BEHAVIOR_LINEAGE = 047201166057edd9859292a1760bc2e9bbf173a2
NORMAL_PRODUCT_MODE = production_answer_obligations_v1
NEW_RUNTIME_MODE_REQUIRED = false
PRODUCTION_ANSWER_OBLIGATIONS_V2_ACTIVATED = false
FORMAL_CANDIDATE_FREEZE_REQUIRED = false
FULL_EXPOSED_NOVEL_DEV_INTEGRATED_REGRESSION = true
FUTURE_MODE = qa
FUTURE_SPLIT = novel_dev
FUTURE_COMPLETE_SPLIT_REQUIRED = true
EXTERNAL_JUDGE_REQUIRED = false
FULL_28_CASE_RESULT_COUNTS_AS_FRESH_GENERALIZATION = false
NOVEL_VALIDATION_AUTHORIZED = false
HOLDOUT_AUTHORIZED = false
```

The product-behavior lineage is the G4 collateral-retention correction commit; later documentation/evaluation-only descendants may supply the execution HEAD if they do not change behavior or material inputs. G1 uses question-derived relation obligations, G2 contains independently attributable local review failures, G3 made no admission-policy change, and G4 corrected the shared normal-path R2 pool. This is the integrated composition; a bookkeeping version bump would add no semantic identity. `production_answer_obligations_v2` remains an unreserved, inactive possibility for a future material change.

This is an exposed-development candidate identity, not an F6/release candidate freeze. `src/panda_agent/candidate.py` binds the signed official benchmark, compatible product-language calibration, Docker service image identities, protected file hashes, and a formal clean-tree freeze. Those release-oriented obligations do not describe this draft `novel_dev` regression. The normal evaluation manifest and run records, together with the product lineage and preflight below, are sufficient; no separate G5 candidate manifest or freezer is required. No candidate ID is passed to the runner.

## Why one complete exposed run

G4 asked whether the R2 correction retained qualifying evidence under a narrow three-case causal protocol. Its scoped R2 PASS, with the targeted runner's separate `COMPLETE / FAIL`, does not answer how G1–G4 interact across retrieval, final evidence, generation, verification, revision, and refusal. The corrected lineage has no coherent complete exposed `novel_dev` QA snapshot. A single complete 28-case `qa` run is therefore the smallest available integrated cohort that can inventory all currently reviewed Phase-G interactions and make a candidate-readiness decision. It is within the policy's approximately 10–30-case targeted-regression scale; `retrieval` would omit answer/refusal behavior, while `full` would add an unnecessary external judge. This run is selected for the integrated question, not reassurance or repeated R2 confirmation.

The cohort is already exposed. Its result may establish integrated exposed regression behavior, failure ownership, and readiness for further development. It cannot establish fresh generalization, independent confirmation, `novel_validation` success, phase-level validation, or release readiness. The G4 target cases `n002`, `n017`, and `n024` necessarily recur in the complete split. Their G5 observations are **not independent empirical replication** of the G4 result. Preserve `g4-r2-post-correction-exposed-target-v1` as the G4 scoped authority; never select the better realization, rewrite G4 history, or combine records into a best-of composite.

## Future execution identity and preflight

The following is a future, separately authorized execution contract. The run ID is a proposal; its nonexistence must be checked immediately before launch. No run is created by this design.

```text
RUN_ID = g5-integrated-candidate-novel-dev-v1
MODE = qa
SPLIT = novel_dev
DATASET_PATH = evaluation/novel/v1/novel_dev.yaml
ALLOW_DRAFT = true
CAPTURE_STAGE_TRACE = true
CASE_IDS = none
LIMIT = none
EXTERNAL_JUDGE = false
CANDIDATE_ID = none
EXPECTED_CURRENT_SPLIT_SIZE = 28
DATASET_BENCHMARK_VERSION = novel-v1-dev-0.3.0
DATASET_SHA256 = 25ad18fcf76ab2796aa18ae961bdc4faf076f0c98a8a5226413ec95e58252223
```

The checked current approved `novel_dev` ID set is `n001,n002,n003,n004,n005,n006,n007,n008,n009,n010,n014,n015,n016,n017,n018,n019,n020,n021,n022,n023,n024,n025,n026,n027,n028,n029,n030,n031`. Its Gold expects `answered` for 27 cases and `insufficient_evidence` for `n016`; all 28 are approved, exposed development cases. These are checked current facts, not a fixed-count definition of completeness. At execution, derive the full approved ID set from the unchanged dataset, require exactly one completed record per ID under one run ID/product/dataset identity, and require no extra or missing IDs. `CASE_IDS=none` and `LIMIT=none` select the whole split.

Before any scientific call, compare the current checkout and planned run manifest with the G4 current-lineage capture and this design: product-behavior lineage and behavior-affecting source; source manifest; normalized corpus/output identity; index collection/schema/payload identity; exact dataset/version/ID set; prompt set, decomposition prompt/schema and fingerprint; generation model; embedding model and dimension; retrieval/fusion/rerank policy; query-expansion identity. The expected current normal-path versions are decomposition prompt `3.0.0`, schema `e1.question_decomposition.v3`, coverage schema `coverage-satisfaction-v2`, prompt set `3.12.0`, and prompt fingerprint `5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce`. Record evaluated HEAD and relevant runtime/package versions. Document package differences and their comparability implications; do not treat a behavior-affecting package change as documentation drift. Any material product/input mismatch or reused run ID stops before calls as `INCONCLUSIVE / MATERIAL IDENTITY DRIFT`, pending a forward design decision. This preflight uses existing manifests/receipts; it does not require a new integrity machinery or routine per-file hashes.

Use the runner's atomic case store and manifest. A clearly retryable `429`, `502`, `503`, `504`, or transport interruption may be resumed under **the same run ID and same identity only**; never rerun completed cases. Do not replace a nonretryable product exception, open a second run after a poor outcome, or use first-PASS/best-of selection. A budget stop or unclassified error needs a documented decision before further scientific calls; it is not an automatic retry permission.

The proposed operational guardrails are `max_model_calls=450` and `max_token_usage=2500000`. The G3 full 28-case QA audit consumed 390 calls/1,563,460 tokens across 54 attempts with provider recovery; 450 gives about 15% call headroom. The latest G4 three-case QA capture consumed 18 calls/199,797 tokens; linear 28-case token scale is about 1.865 million, so 2.5 million gives about 34% headroom. The older G4 28-case attempt used 153 calls/1,107,119 tokens before two nonretryable errors. These are spending guardrails, not quality thresholds or promises of completion. The runner checks them only **between cases** and resets attempt counters on resume, so they are soft per-invocation stops, not hard cumulative caps. If a strict cumulative maximum becomes required, this execution contract must be revised before launch; no silent override or automatic resume is allowed.

## Frozen integrated case review

For every selected ID, preserve raw runner status, response, citations, final evidence, stage trace, runtime coverage receipt, and exceptions. Compare dataset `expected_status` with actual product status. Apply these offline exposed-development classifications to the unchanged output:

| Class | Rule |
|---|---|
| `ANSWERED_COMPLETE` | Actual answer is present, supported by permitted evidence, and expresses every independently required critical semantic point and relation. |
| `ANSWERED_INCOMPLETE` | An answer is present but omits or fails to support independently required critical content; identify whether the needed evidence reached the relevant stages. |
| `INSUFFICIENT_EVIDENCE` | Product abstains; independently adjudicate whether the question is answerable from allowed locked sources before deciding correct abstention versus false insufficiency. |
| `ERROR` | A terminal exception or missing usable QA result; distinguish retryable provider infrastructure from nonretryable product failure. |

For expected `answered`, use the existing reviewed Gold and locked allowed sources to identify critical answer points, explicitly requested relations, evidence roles, and version/source restrictions. Require their **meaning**, not benchmark-author phrasing or irrelevant Gold prose; cite support must match reviewed critical role selectors or independently justified source authority. For expected `insufficient_evidence`, require a justified abstention; an unsupported answer is a defect. Gold status is a comparison input, not conclusive proof of independent answerability. An independently answerable case ending in `insufficient_evidence` is a false-insufficiency defect even with healthy R2. Conversely, genuine corpus insufficiency should not be forced into an answer.

Runtime G1/G2 coverage is diagnostic, never the sole semantic completeness authority. The G4 n024 capture had final/cited critical evidence and `VALID` runtime coverage, yet bounded Gold-detail review found omitted answer details. Accordingly, inspect answer text and support separately from canonical runtime obligations. Record missing critical point, relation, evidence role, or generated detail; identify a V1/G2 false acceptance only when the trace supports that narrower diagnosis. Do not infer it merely from a semantic omission.

Hard safety/trustworthiness blockers follow `docs/EVALUATION_POLICY.md`: wrong-version or forbidden evidence, citation-integrity failure, major unsupported factual claim, observable contradiction, and unhandled product exception. An incorrect asserted answer for a genuinely insufficient case is also a blocker. Do not waive or weaken these because an aggregate metric improves. Critical answer and evidence-role omissions are completeness blockers, including upstream loss from an independently answerable source or downstream omission despite available final/cited evidence.

### Pre-existing authority limits, frozen before outcome inspection

- `n001`: the existing G4 independent source review found the question answerable from `configSettings.sh`, but current Gold p1/p2 branch-execution language conflicts with the script's as-written Bash syntax error. Treat branch-execution assertions as a documented Gold/source conflict, not an automatic product failure or an excuse for abstention. Assess the supported nominal branch literals, paths, exports, and actual as-written shell behavior against source authority. Do not silently change Gold or grant a blanket case waiver.
- `n004`: the historical raw `fairlogger/Logger.h` identifier flag coexists with that string in cited evidence; the header itself is absent from the locked inventory. Retain the raw flag and check the exact claim/citation support before attributing an unsupported assertion. No automatic pass or waiver follows.
- `n014`: independent answerability for the requested repository description remains unresolved. It has **no pre-granted exception**. Review locked source and answerability under the same general rule; if authority remains unresolved and determines readiness, classify the decision `INCONCLUSIVE / EVALUATOR OR GOLD AUTHORITY LIMIT`.
- `n016`: the current Gold expectation is `insufficient_evidence`. Preserve it and evaluate any actual answer for genuine support; historical incorrect answering does not modify the expectation.

Any further Gold/evaluator conflict discovered during review must be documented with the exact affected dimension and source evidence. It cannot become a post-outcome waiver or a silent Gold edit. If a necessary authority question cannot be resolved without a forward reviewed Gold/evaluator decision, keep the affected conclusion inconclusive. Unaffected dimensions remain assessable.

## Failure ownership and historical comparison

For each non-complete/problematic case, record: ID, expected and actual status, semantic completeness, relevant allowed-source availability, channel/pool/rerank/final/cited evidence, runtime coverage, earliest supported owner, secondary owner, confidence, and generic failure family. Apply the existing policy taxonomy: `Q1` question analysis; `Q2` query construction; `R1` channel recall; `R2` fusion/pool retention; `R3` final selection; `D1` decomposition; `A1 / GENERATION` answer composition; `V1` claim review; `V2` post-revision review; `C1` genuine corpus insufficiency. `FINALIZATION` and `PROVIDER_PRODUCT_ERROR` are operational stage labels to map to the responsible pipeline layer; `GOLD_OR_EVALUATOR_CONFLICT` is an authority limitation, and `UNRESOLVED` explicitly records insufficient causal evidence. These are review labels, not new runtime categories.

Attribute the earliest supported loss. If source evidence reaches rerank pool, final evidence, and citation, an omitted answer detail is downstream unless contrary trace evidence exists. A valid R2 observation in G4 does not shield a newly observed R2 contract contradiction in G5. The current known residuals guide review, not product logic: n024's repaired R2 retention coexists with generation omission and a possible secondary V1/G2 narrow-obligation issue; n006 has an historical R2 quota residual and separate completeness concern; n007/n028/n031 have historical V1/G2 concerns; n018 has generation/completeness concerns; n014 has unresolved answerability; n001 has the Gold/source conflict above. None supplies a case-specific runtime trigger or automatic causal verdict.

The earlier G4 28-case initial run (`INCOMPLETE / INCONCLUSIVE`) and its n002/n018 replacement composite belong to the older `a22c8f70eeebe4a53490e11a4b6852561ca8afa6` product lineage; the composite is mixed provenance. They may supply labelled directional status transitions and sentinels, never the G5 gate denominator, a numerical PASS threshold, or replacement records. Differing G4/G5 realizations require stage analysis, not an opportunistic rerun.

## Run completion, runner verdict, and G5 decision

`G5_INTEGRATED_RUN_COMPLETE` means exactly one scored QA record for every approved split ID, under one compatible run/product/dataset identity, with no unresolved case error. `G5_INTEGRATED_CANDIDATE_READY_FOR_G6` is a separate quality decision. A complete run can fail readiness.

Preserve the runner's own cohort status, quality verdict, development-gate report, and product-language-gate compatibility **verbatim**. Its generic complete-development gate requires `official=true` and `split=dev`, while this run is `allow_draft=true`/`novel_dev`; the benchmark product-language calibration is incompatible with this dataset. Thus these generic gates are diagnostic or inapplicable as G5 readiness authority, and any runner `FAIL`/incompatibility is reported, never silently rewritten as `PASS`. The auditable G5 contract here is the separate development decision; it does not alter runner code, Gold, or calibration.

Decision precedence for the future review:

1. Material preflight mismatch or reused ID: `INCONCLUSIVE / MATERIAL IDENTITY DRIFT`; stop before scientific calls.
2. Retryable infrastructure interruption: `INCOMPLETE / RECOVERY PENDING` while same-run recovery is allowed. Exhausted budget or unavailable recovery is `INCONCLUSIVE` with actual partial records and spending reported. A nonretryable product error leaves `INCOMPLETE / PRODUCT ERROR`, blocks readiness, and is flagged as a hard-safety/product-quality defect; never replace it to manufacture completion.
3. For a complete single-provenance run, any hard safety breach gives `FAIL / HARD SAFETY BLOCKER`. Otherwise any independently answerable false insufficiency gives `FAIL / FALSE INSUFFICIENCY REGRESSION`; any observable contradiction of the accepted G4 R2 retention contract gives `FAIL / R2 CONTRACT REGRESSION`; any unresolved critical answer/evidence-role omission or incorrect expected-insufficient answer gives `FAIL / ANSWER COMPLETENESS BLOCKER` or the applicable hard-safety classification. Multiple defects are retained in the inventory even when one label takes precedence; the umbrella is `FAIL / INTEGRATED PRODUCT QUALITY BLOCKER`.
4. If no established blocker exists but a material Gold/evaluator/answerability authority limit prevents a reliable readiness conclusion, use `INCONCLUSIVE / EVALUATOR OR GOLD AUTHORITY LIMIT` with the affected dimensions named. A conflict on an irrelevant dimension does not erase a separately established defect.
5. Only one complete run with no remaining product error, hard safety breach, false insufficiency, incorrect expected abstention, R2 contradiction, or independently supported critical completeness omission, and with all decision-relevant authority limits resolved under the predeclared review rule, may be `PASS / INTEGRATED CANDIDATE READY FOR G6`.

There is no average-score override for these blockers. A repeated G5 observation cannot replace G4's scoped result. If a family of available-evidence → incomplete generation → verifier acceptance appears, inventory it as a generic candidate-level completeness signal for later owning-layer work; do not repair the product during G5 execution.

## G6 and stop boundary

G5 PASS only supports recommending the separately authorized **G6 FRESH DEVELOPMENT EVALUATION DESIGN**. It does not itself authorize that design, a new fresh cohort, `novel_validation`, a release candidate, holdout access, or release readiness. The current decision that fresh Lane B is **OPTIONAL / DEFERRED** remains in force: G6 may decide whether, when, and how fresh reviewed development evidence is needed, without making curation a G5 prerequisite. A G5 FAIL instead calls for a separately authorized generic owning-layer repair decision; an INCONCLUSIVE result calls for resolution of its named authority/infrastructure issue.

This design performs no QA or retrieval run, model/judge call, product repair, dataset or Gold edit, or protected-data inspection. The next recommended task is **G5 INTEGRATED CANDIDATE EXPOSED REGRESSION EXECUTION**, under separate authorization. `NEXT_TASK_EXECUTION_AUTHORIZED = false`.

```text
G6_ENTRY_REQUIRES_G5_PASS = true
PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
QA_RUNS = 0
RETRIEVAL_RUNS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```
