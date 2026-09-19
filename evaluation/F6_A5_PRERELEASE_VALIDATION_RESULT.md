# F6-A Attempt 5 — Fresh Preregistration, Candidate Freeze, and Continuous Pre-Release Validation Terminal Result

## Verdict

`F6-A Attempt 5 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`

The complete 59-case formal-English Gold v2.10 cohort failed three mandatory A1 gates under the new `production_answer_obligations_v1` candidate. The fail-fast contract stopped A2–A5, preserved `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`, and kept protected holdout access and F6-B execution at zero.

## Starting state and A0

- Starting HEAD: `8f61aee414aa9fa2da0e3a6bbb2f767eadb7da4c` (expected HEAD matched; worktree clean except the known regenerable untracked `data/_a3_gold_args.txt`).
- Material product-behavior lineage HEAD: `eda7d932a9b1b7b65436cba01e247859a6f9e056` (generic answer-obligation completeness). Previous lineage HEAD: `d3a1b274b2784399a7dc51b094a17e466d208b50` (Attempt 4). R1 release-identity repair `8f61aee` is identity/provenance-only and completed the freeze authority.
- Attempt-5 eligibility: material product change after the Attempt-4 lineage; not a stochastic repeat (`SAME_PRODUCT_LINEAGE_FORMAL_REPEAT = PROHIBITED` respected).
- Gold authority: `m6-benchmark-v2.10`, SHA-256 `bdce5cbdc0a6f1645d7350b87bc2f289265c3d67311dab4b12e488b9dc499513`, `official_ready = true`, `structurally_valid = true`.
- Calibration: `phase_b_t3_product_language_scope_v7`, SHA-256 `ad68df096fc82d6c52bd984e44e99573e6b47e5047b3d522ae750a93188c49cd`, compatible; mechanically 59 formal-English and 21 non-English IDs; selector SHA-256 `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5`.
- Production mode: `DEFAULT_ANSWER_POINT_MODE = production_answer_obligations_v1`; E3 requires `answer_point_coverage_mode == runtime_e1_v2` and is not reachable in the production path; E3 missing-point retrieval, candidate capture, cross-pass global reselection, and the retained-support ledger remain unpromoted.
- Decomposition identity: `QUESTION_DECOMPOSITION_PROMPT_VERSION = 2.0.0`, `QUESTION_DECOMPOSITION_SCHEMA_VERSION = e1.question_decomposition.v2`, bound inside the canonical corrected `prompt_fingerprint()` = `35f1dd3cbcd6cb636e2e92e7af28cb95415787e8d920c99c3b070eae86a8f097`; candidate/evaluation prompt authority equivalence verified.
- Models: generation/effective verification/runtime composer/judge `gemini-3.8-flash`; embedding `gemini-embedding-2` at 3072 dimensions. Index `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9` (collection `panda_knowledge_v1`, 104,973 points). Docker `postgres:17-alpine` and `qdrant/qdrant:v1.15.5` running with release identity satisfied. Source manifest, retrieval-policy, and query-expansion hashes identical to the frozen preregistration.
- Focused deterministic verification: 130 + 228 tests and 58 subtests passed across `test_f6_release_identity.py`, `test_generic_answer_obligation_completeness.py`, `test_f6a_gate_evaluator.py`, `test_f6a_release_infrastructure.py`, `test_question_decomposition.py`, `test_post_a3_finalization_contract.py`, `test_query_expansions.py`, `test_qa.py`, and `test_t3_1r2_calibration_rank.py`. The two known legacy `test_m6_evaluation.py` fixture failures reproduced identically; no new current-path regression occurred.
- A0 scientific usage: 0 calls / 0 tokens.

## Preregistration and freeze

- Preregistration commit: `eacbf447eee2527b85e0e47073d8584c64a4a3f4` (`Preregister F6-A attempt 5`).
- Candidate ID: `f6a-rc5-20260919`; frozen implementation commit: `eacbf447eee2527b85e0e47073d8584c64a4a3f4`.
- Freeze commit: `07124a1492fca779c6024525f3a001818f04e975` (`Freeze F6-A attempt 5 candidate`).
- Candidate manifest SHA-256: `db8ba89bd8a7ab490d981c6a49c2ff30f0736bcee2f46e07881efe9979514cc4`.
- `primary_answer_point_mode = production_answer_obligations_v1`; `prompt_hash = 35f1dd3cbcd6cb636e2e92e7af28cb95415787e8d920c99c3b070eae86a8f097`.
- `verify_candidate`: `valid = true`, `mismatches = []` before A1.
- The untracked regenerable scratch `data/_a3_gold_args.txt` was moved unchanged to gitignored `tmp/` before the freeze because the freezer enforces a clean porcelain tree; its content (the 59 `--case-id` arguments) was regenerated mechanically from the frozen preregistration selector.

## A1 Gold

- Run: `f6a-rc5-gold-formal-full-20260919`, mode `full`.
- Cohort: 59 expected, 59 scored; `executed_case_ids == formal_product_scope_ids`; no missing, extra, duplicate, or reused Attempt-4 records.
- Recovery: 10 retryable `transport_provider_infrastructure` exceptions (g001, g017, g018, g026, g029, g031, g040, g105, g108, g115) were recovered by one resume operation under the identical frozen identity; all 10 succeeded on their second attempt. Successful cases were never rerun; the `attempts.jsonl` ledger retains all 69 execution attempts with cumulative usage.
- Release score: `0.9491525423728814` over all 59 cases; not an additional gate.

| Mandatory gate | Value | Threshold | Result |
| --- | ---: | ---: | --- |
| `gold_recall_at_10` | 0.979592 | >= 0.95 | PASS |
| `final_evidence_recall` | 0.908163 | >= 0.90 | PASS |
| `critical_final_evidence_recall` | 0.918367 | == 1.00 | **FAIL** |
| `intent_accuracy` | 1.000000 | >= 0.90 | PASS |
| `per_intent_gold_recall_at_10` | min 0.950000 | >= 0.75 | PASS |
| `per_intent_intent_accuracy` | min 1.000000 | >= 0.80 | PASS |
| `expected_status_accuracy` | 1.000000 | >= 0.975 | PASS |
| `citation_integrity` | 1.000000 | == 1.00 | PASS |
| `wrong_version_evidence_count` | 0 | == 0 | PASS |
| `forbidden_evidence_count` | 0 | == 0 | PASS |
| `required_source_coverage_answered` | 0.979592 | >= 0.97 | PASS |
| `identifier_hallucination_rate` | 0.046154 | < 0.03 | **FAIL** |
| `paper_code_dual_source_rate` | 1.000000 | == 1.00 when applicable | PASS |
| `answer_point_coverage` | 0.949153 | >= 0.90 | PASS |
| `critical_answer_point_miss_count` | 4 | == 0 | **FAIL** |
| `contradiction_count` | 0 | == 0 | PASS |
| `major_unsupported_claim_count` | 0 | == 0 | PASS |
| `unhandled_exception_count` | 0 | == 0 | PASS |

Per-intent Gold recall@10 / intent accuracy: `algorithm_implementation` 1.0/1.0, `algorithm_theory` 1.0/1.0, `api` 1.0/1.0, `installation` 1.0/1.0, `module_structure` 1.0/1.0, `troubleshooting` 1.0/1.0, and `usage` 0.95/1.0.

The four critical answer-point misses were `g013.p3`, `g023.p3`, `g039.p1`, and `g047.p1`. Critical final-evidence recall was below one on `g011`, `g013`, `g016`, `g020`, `g044`, and `g110`. The identifier-hallucination gate failed on six major hallucinated identifiers concentrated in two LumiFit cases: `g060` (`LumiFit::THETA_X`, `LumiFit::THETA_Y`) and `g113` (`LumiFit::MC`, `LumiFit::MC_ACC`, `LumiFit::RECO`, `LumiFit::THETA_X`).

The stage receipt was sealed before case diagnostics and validated: SHA-256 `666007c317e6ef6d1ef9630bb6982cf334863579ed0bfd452fc0845a53486f3e` (archival copy `evaluation/f6_a5_a1_stage_receipt.json`). The authoritative forward-only F6-A gate matrix SHA-256 is `a6e40cf93f3d4b8593268d70ce178e0f5cfdc4ea30aa6a24bd8c506e7047046b`; its validated receipt SHA-256 is `5790a591d9375e374d80469c3e8bf3863203083538096bd4ef4682ae91e099fd` and binds `candidate_valid = true`, `official_decision = FAIL`. An idempotent second invocation confirmed the receipt.

## New obligation-mode behavior (diagnostic only, after receipt sealing)

- Decomposition: no failures and no refusal regressions. Points-per-question distribution 1:52, 2:4, 3:2, 4:1 — no over-splitting signal; the 1–5 obligation bound was respected.
- The bounded revision fired in 6 of 59 cases (at most one revision, as frozen). Product-layer `missing_answer_point_ids` were empty for all 59 final answers, while the evaluator found 4 critical Gold points uncovered — an under-splitting-relative-to-critical-Gold-points signal left for post-terminal review, not a formal measurement.
- Cost: 563 calls / 3,201,331 tokens vs Attempt 4's 388 calls / 3,647,993 tokens — more calls, fewer tokens, consistent with added decomposition/coverage/revision calls; attribution is not established.

## Downstream stages and exposure

- A2 ablation: `NOT_REACHED`, 0 calls / 0 tokens.
- A3 `novel_dev`: `NOT_REACHED`, 0 calls / 0 tokens.
- A4 `novel_validation`: `NOT_REACHED`, 0 calls / 0 tokens; `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`.
- A5 composer audit: `NOT_REACHED`, 0 calls / 0 tokens.

## Scientific usage

- Attempt-5 total: **563 calls / 3,201,331 tokens**, all in A1.
- Successful attempts: 511 calls / 3,051,535 tokens; failed retryable attempts: 52 calls / 149,796 tokens (included once).
- Recoverable roles: external judge 85 calls / 376,598 tokens; runtime QA-generation-labeled 78 calls / 1,339,203 tokens; runtime QA-composer-labeled 53 calls / 59,012 tokens; 69 runtime embedding calls.
- Question decomposition and runtime verification token usage: `NOT_SEPARATELY_RECOVERABLE_FROM_STORED_RECORDS` (both share the unlabeled generation bucket; no estimation used). Embedding token usage likewise not separately recoverable.

## Integrity and protocol record

One resume operation recovered ten retryable transport exceptions under the identical frozen identity. No successful case was rerun; no product, prompt, retrieval, Gold, calibration, threshold, model, evaluator, or composer change occurred after freeze. Receipt chronology was respected: stage completion → recovery → cohort completeness → gate persistence → stage receipt sealed and validated → gate matrix sealed and validated → case-level diagnostics.

## Comparison with Attempt 4 (informative, no causal attribution)

- Attempt 4: Gold v2.10, `legacy_question_core`, release score 0.971751, 388 calls / 3,647,993 tokens, 2 failed gates.
- Attempt 5: Gold v2.10, `production_answer_obligations_v1`, release score 0.949153, 563 calls / 3,201,331 tokens, 3 failed gates.
- `expected_status_accuracy` improved to 1.000000 (Attempt 4: 0.983051) — no erroneous refusal or status mismatch remained.
- Critical answer-point misses changed from 2 (`g013.p3`, `g037.p1`) to 4 (`g013.p3`, `g023.p3`, `g039.p1`, `g047.p1`): `g037.p1` is no longer missed; three new critical misses appeared.
- `identifier_hallucination_rate` worsened from 0.011561 to 0.046154 (LumiFit identifiers on `g060` and `g113`).
- These are lineage-level observations; no difference is attributed solely to the completeness mechanism.

## Historical and protected state

Attempts 1–4 remain immutable historical FAIL results. Attempt 5 is terminal FAIL.

- `holdout access = 0`
- `protected-content leakage = 0`
- `F6-B execution = 0`

F6-B remains `LOCKED / F6_A_DID_NOT_PASS`.

## Next task recommendation

Perform a separately authorized post-Attempt-5 exposed failure review of the three failed mandatory gates: (1) QuestionDecomposer under-splitting relative to critical Gold answer points behind the four critical misses, (2) the LumiFit identifier hallucinations on `g060`/`g113` at the generation/verification layer, and (3) the six critical final-evidence misses. Classify the smallest general failure mechanisms before any candidate repair or Attempt 6. Do not access `novel_validation` or the protected holdout.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`
