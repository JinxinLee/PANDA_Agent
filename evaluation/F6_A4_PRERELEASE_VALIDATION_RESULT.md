# F6-A Attempt 4 — Continuous Prerelease Validation Terminal Result

## Verdict

`F6-A Attempt 4 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`

The complete 59-case formal-English Gold v2.10 cohort failed two mandatory A1 gates. The fail-fast contract stopped A2–A5, preserved `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`, and kept protected holdout access and F6-B execution at zero.

## Starting state and A0

- Starting HEAD: `cedebea9261db68b532c0e5477c52ddc3a8a7d1c`.
- Accepted product behavior lineage: `d3a1b274b2784399a7dc51b094a17e466d208b50`; no later product drift was present.
- The only initial worktree entry was the known regenerable untracked `data/_a3_gold_args.txt`.
- Gold authority resolved to `m6-benchmark-v2.10`, SHA-256 `bdce5cbdc0a6f1645d7350b87bc2f289265c3d67311dab4b12e488b9dc499513`, with `official_ready = true` and `structurally_valid = true`.
- Calibration resolved to `phase_b_t3_product_language_scope_v7`, SHA-256 `ad68df096fc82d6c52bd984e44e99573e6b47e5047b3d522ae750a93188c49cd`, compatible with Gold v2.10. It mechanically produced 59 formal-English and 21 non-English IDs; formal selector SHA-256 `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5`.
- Candidate/freezer, retry/resume, cohort tri-state, receipt-before-diagnostics, gate, ablation, novel-cohort, composer-audit, and holdout boundaries were verified by host and two parallel read-only AGY audits.
- Focused deterministic verification: 426 passed, 85 subtests passed, and exactly two known legacy `test_m6_evaluation.py` fixture failures reproduced. No new relevant failure occurred.
- A0 scientific usage: 0 calls / 0 tokens.

## Preregistration and freeze

- Preregistration commit: `f9e64cb5d0c60c90cb2a8432d5daf01b63ac05fa` (`Preregister F6-A attempt 4`).
- Candidate ID: `f6a-rc4-20260916`.
- Frozen implementation commit: `f9e64cb5d0c60c90cb2a8432d5daf01b63ac05fa`.
- Freeze commit: `4d2ada392daa2653402d2d1ba645486db935f816` (`Freeze F6-A attempt 4 candidate`).
- Candidate manifest SHA-256: `dc44efe61b1745f0f4fddfdc1f17fbc8ba767c652fae17f5a2a003507ba4f4e7`.
- `verify_candidate`: `valid = true`, `mismatches = []` before A1 and at closeout.
- Frozen runtime: answer mode `legacy_question_core`; prompt 3.10.1 / `23d73b036646ec62f3095fac4bdfafdfc7ecf6676fd27d18475b86773db4e6d5`; generation/effective verification/judge `gemini-3.8-flash`; embedding `gemini-embedding-2` at 3072 dimensions; index `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`; PostgreSQL 17 and Qdrant 1.15.5.

## A1 Gold

- Run: `f6a-rc4-gold-formal-full-20260916`, mode `full`.
- Cohort: 59 expected, 59 scored, no missing/extra/duplicate IDs.
- Recovery: `g112` had two retryable `transport_provider_infrastructure` exceptions and succeeded on the third identical-candidate attempt. Two `resume` operations ran; the other 58 successful cases were untouched. All attempt usage is present in `attempts.jsonl`.
- Release score: `0.9717514124293786` over all 59 cases; it is not an additional gate.

| Mandatory gate | Value | Threshold | Result |
| --- | ---: | ---: | --- |
| `gold_recall_at_10` | 0.989796 | >= 0.95 | PASS |
| `final_evidence_recall` | 0.918367 | >= 0.90 | PASS |
| `critical_final_evidence_recall` | 0.928571 | == 1.00 | **FAIL** |
| `intent_accuracy` | 1.000000 | >= 0.90 | PASS |
| `per_intent_gold_recall_at_10` | min 0.958333 | >= 0.75 | PASS |
| `per_intent_intent_accuracy` | min 1.000000 | >= 0.80 | PASS |
| `expected_status_accuracy` | 0.983051 | >= 0.975 | PASS |
| `citation_integrity` | 1.000000 | == 1.00 | PASS |
| `wrong_version_evidence_count` | 0 | == 0 | PASS |
| `forbidden_evidence_count` | 0 | == 0 | PASS |
| `required_source_coverage_answered` | 0.979592 | >= 0.97 | PASS |
| `identifier_hallucination_rate` | 0.011561 | < 0.03 | PASS |
| `paper_code_dual_source_rate` | 1.000000 | == 1.00 when applicable | PASS (0 applicable) |
| `answer_point_coverage` | 0.971751 | >= 0.90 | PASS |
| `critical_answer_point_miss_count` | 2 | == 0 | **FAIL** |
| `contradiction_count` | 0 | == 0 | PASS |
| `major_unsupported_claim_count` | 0 | == 0 | PASS |
| `unhandled_exception_count` | 0 | == 0 | PASS |

Per-intent Gold recall@10 / intent accuracy: `algorithm_implementation` 1.0/1.0, `algorithm_theory` 1.0/1.0, `api` 1.0/1.0, `installation` 1.0/1.0, `module_structure` 1.0/1.0, `troubleshooting` 1.0/1.0, and `usage` 0.958333/1.0. The two critical answer-point misses were `g013.p3` and `g037.p1`; critical final-evidence recall was below one on `g011`, `g013`, `g037`, `g044`, and `g059`.

The automatic stage receipt was sealed before case diagnostics and validated idempotently: SHA-256 `90fe8ecb1a3b698e0d5e3ea503ad12212f82739b3f6fee1eb04a50386bb57f28`. The authoritative forward-only F6-A gate matrix SHA-256 is `4475f78af04a7d87d6117f5477e803bd314b72f522018dc0b99a69a366733826`; its validated receipt SHA-256 is `0decfa5a0ae69d882940bcf272c9ce3216264adbbbca7f852fa421f9c51e72c5` and binds `candidate_valid = true`, `decision = FAIL`.

## Downstream stages and exposure

- A2 ablation: `NOT_REACHED`, 0 calls / 0 tokens.
- A3 `novel_dev`: `NOT_REACHED`, 0 calls / 0 tokens.
- A4 `novel_validation`: `NOT_REACHED`, 0 calls / 0 tokens; `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`.
- A5 composer audit: `NOT_REACHED`, 0 calls / 0 tokens.

## Scientific usage

- Attempt-4 total: **388 calls / 3,647,993 tokens**, all in A1.
- Runtime: 322 calls / 3,272,550 tokens (256 generation calls, 66 embedding calls).
- Recoverable runtime labels: QA generation 73 calls / 1,895,407 tokens; QA composer 45 calls / 76,443 tokens.
- External judge: 66 calls / 375,443 tokens.
- Runtime verification and embedding token usage: `NOT_SEPARATELY_RECOVERABLE_FROM_STORED_RECORDS`.
- `g112` attempts: failed retryable 7/21,338; failed retryable 6/21,887; successful 8/145,936. These are included once in the total.

## Integrity and protocol record

The first standalone F6-A gate command omitted `.env` loading and sealed an immutable forward-only receipt with `candidate_valid = false`. This incorrect receipt and its matrix remain preserved. The repository-supported `--source-matrix` successor path then rederived byte-equivalent gate data with the environment loaded, verified the frozen candidate, produced the authoritative FAIL matrix and receipt, and passed an idempotent second validation. No model call, record, score, or frozen contract changed. This is recorded as `A4-PD1` in the result JSON.

## Historical and protected state

Attempt 3 used Gold v2.9 while Attempt 4 used v2.10, so aggregate A3→A4 score comparison is benchmark-version confounded. The `g060` contract changed forward-only and is not compared as an unchanged case. Attempt-3 official usage remains 397 calls / 3,783,197 tokens; its post-terminal `g013` diagnostic remains separate at 10 calls / 62,370 tokens.

- `holdout access = 0`
- `protected-content leakage = 0`
- `F6-B execution = 0`

Attempts 1, 2, and 3 remain immutable historical FAIL results. Attempt 4 is terminal FAIL. F6-B remains `LOCKED / F6_A_DID_NOT_PASS`.

## Next task recommendation

Perform a separately authorized post-Attempt-4 exposed failure review for the two critical answer-point misses and five critical final-evidence misses, classifying the smallest general failure mechanisms before any candidate repair or Attempt 5. Do not access `novel_validation` or the protected holdout.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`
