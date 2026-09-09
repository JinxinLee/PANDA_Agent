# E2-A3 — Bounded Runtime Activation and Regression Check

## Verdict and disposition

**FAIL / Q7.** The complete bounded experiment found one new runtime verifier
integrity category failure, on Gold case `g112`. The preregistered gate counts
all reviews, including errors repaired by the existing single revision.
Normal QA remains `legacy_question_core`; no activation commit is created.
The candidate is retained for explicit diagnostic use. No repair or rerun was
performed after exposure.

## Provenance and execution

| Boundary | Git commit |
| --- | --- |
| Starting baseline | `ffedb2117f578515ea9d74eca92105956b8a3dcb` |
| Candidate and preregistration | `997c8a84c57b92e28372f6532acdc074724985f9` |
| All retrieval and paired QA raw outputs | `8ba275addf44a5c7e96bf83a292c6737fbe07b38` |
| Blinded judgments | `a804e41d5a13ddb39e8547331353d9d047cb818f` |
| Scientific result and FAIL closeout | Commit containing this report, directly following the judgment commit |
| Default activation | NOT CREATED |

Protocol: `E2_A3_RUNTIME_ACTIVATION_PREREGISTRATION.md` and
`e2_a3_runtime_activation_manifest.json`. Evidence:
`e2_a3_retrieval_bootstrap_raw.json`, `e2_a3_paired_runtime_raw.json`,
`e2_a3_runtime_regression_judged.json`, and
`e2_a3_runtime_activation_result.json`.

One frozen candidate contains legacy, existing shadow, and runtime modes.
Runtime shares shadow semantics with a truthful runtime audit label. The public
entrypoints retain their signatures and default to legacy before and after the
verdict. Public QAResult/ClaimCitation and legacy compatibility requirements are
unchanged. Each arm ran fresh; no claim or evidence-bundle reuse occurred.
Case order alternated legacy/runtime and runtime/legacy. All raw outputs were
committed before judging. Balanced blinded A/B judgments were committed before
label interpretation. No product changes occurred during frozen science.

## Cohorts and retrieval diagnostic

The deterministic bootstrap used 24 approved English answered Gold/dev cases.
Paired QA used 16 Gold cases (12 answered and four refusal controls) plus the
exact 12 exposed E2-A2 English novel sentinels: 28 pairs, 56 executions.
No novel_validation, holdout, or other protected evaluation data was used.

Gold source is the reviewed `evaluation/benchmarks/v2_6/gold_questions.yaml`.
The generic dataset locator returned v2.5 because its stored v2.6 identity was
stale following the reviewed g021 correction. The frozen runner explicitly uses
v2.6 and checks approval, calibration membership, and all language-selection
fields against the calibration Git state. Only g021 obligation fields changed;
g021 is outside these cohorts. Historical calibration artifacts were preserved.

| Retrieval observation | Value |
| --- | --- |
| Completed / exceptions | 24 / 0 |
| Recall@5 | 0.8402777777777778 |
| Recall@10 / Recall@20 | 1.0 / 1.0 |
| MRR | 0.7125 |
| Compatible historical baseline | No |

Older bootstrap cohorts and retrieval configuration differ. These are current
diagnostic metrics; no retrieval regression delta is established.

## Primary gates

| Gate | Result | Evidence |
| --- | --- | --- |
| A1 dual-mode candidate | PASS | Focused offline contract tests |
| A2 pre-verdict legacy default | PASS | Frozen default selector |
| Q1 complete scoreable pairs | PASS | 28/28, 56/56 QA executions |
| Q2 Gold status non-regression | PASS | Legacy 14/16; runtime 14/16 |
| Q3 new false answers | PASS | 0 |
| Q4 new false refusals | PASS | 0; limit 1 |
| Q5 critical user-visible regressions | PASS | 0 |
| Q6 pairwise non-inferiority | PASS | Better 6, equivalent 21, worse 1; worse limit 2 |
| Q7 verifier integrity | FAIL | New unsupported_identifier category on g112 |
| Q8 novel valid decomposition | PASS | 12/12 |
| Q9 novel coverage evaluable | PASS | 12/12 |
| Q10 novel final coverage complete | PASS | 12/12 |
| Q11 generation overhead | PASS | Mean +0.75 adapter calls/case; limit 2 |
| Q12 bounded revision | PASS | No runtime case exceeds one revision |
| Q13 no post-verify retrieval | PASS | 0 calls |
| Q14 public DTO unchanged | PASS | Offline contract and frozen Git checks |
| Q15 legacy requirements preserved | PASS | Offline contract and frozen Git checks |
| PAIR09 atomicity sentinel | PASS | Base and paraphrase each exactly 3 points, evaluable and complete, no structural errors |

New category counts: unsupported identifier 1; wrong version, unknown evidence,
incomplete citation, structural review, and unknown answer point each 0.
Infrastructure failures and separate zero-tolerance violations each 0.

## Failure evidence and interpretation

`g112` runtime's initial review reported
`unsupported identifier PndLmdDataReader::fillData:` (including the trailing
colon), `missing answer point point.3`, and
`missing answer requirement reader_selection_histogram_accounting`.
The initial claim used `PndLmdDataReader::fillData:` in prose. That claim was not
credited for coverage. The existing single revision used `PndLmdDataReader`
instead; final coverage was evaluable and complete and the unsupported-identifier
error disappeared. Final review still reported the legacy requirements
`troubleshoot_upstream_to_downstream` and `explicit_compatibility_check` missing.
Legacy g112 had no review errors and no revision. Both final statuses were
answered; the blinded judge preferred runtime without a critical regression.

Failure classification: `ACTIVATION_CITATION_REGRESSION`, specifically the Q7
unsupported-identifier verifier category. This is an observed validator failure,
not proof that the underlying API does not exist. The trailing punctuation is
recorded as evidence, not a validated root-cause diagnosis. Final recovery and
judge preference cannot waive the frozen all-reviews Q7 rule.

The only user-visible worse judgment was g026, noncritical and within Q6's
allowance: legacy explained the available resolved version and unsupported
requested version; runtime returned a generic insufficient-evidence refusal.
Both missed the expected version_conflict status. g012 also missed that expected
status in both arms. Gold comparisons were 6 better, 9 equivalent, 1 worse;
all 12 novel comparisons were equivalent. These results do not establish perfect
absolute status accuracy or universally improved answer quality.

## Calls, latency, and cost accounting

Legacy decomposition calls: 0. Runtime decomposition calls: 28, exactly one per
runtime case. Generation adapter requests were legacy 131 and runtime 152,
giving (152-131)/28 = 0.75 additional calls per case, excluding embeddings.
Legacy/runtime revisions were 10/7. Each arm made 30 retrieval operations,
including two pre-answer targeted retrievals; post-verification retrieval was 0.

| Latency | Median ms | p95 ms |
| --- | --- | --- |
| Legacy workflow | 58973 | 120355 |
| Runtime workflow | 62134 | 149340 |
| Runtime decomposition | 5294 | 8498 |

Usage tables below are computed from frozen event counters. Logical operations
include retrieval; returned model responses include embeddings. Adapter attempts
are not provider HTTP or billing counts. One extra legacy-review adapter attempt
and three extra judge attempts are observed; no task-level scientific rerun was
performed. Embedding token counters are unavailable, not zero consumption.
Monetary cost cannot be determined from these artifacts.

| Slice | Logical operations | Returned model responses | Adapter attempts | Observable tokens |
| --- | --- | --- | --- | --- |
| bootstrap | 96 | 72 | 72 | 493619 |
| legacy | 190 | 160 | 161 | 2265365 |
| runtime | 212 | 182 | 182 | 2140844 |
| judge | 28 | 28 | 31 | 487556 |
| Total | 526 | 442 | 446 | 5387384 |

| Slice / stage | Logical | Returned | Adapter | Tokens (embedding unavailable) |
| --- | --- | --- | --- | --- |
| bootstrap / analyzer | 24 | 24 | 24 | 52831 |
| bootstrap / embedding | 24 | 24 | 24 | unavailable |
| bootstrap / reranker | 24 | 24 | 24 | 440788 |
| bootstrap / retrieval | 24 | 0 | 0 | 0 |
| legacy / analyzer | 28 | 28 | 28 | 64267 |
| legacy / embedding | 30 | 30 | 30 | unavailable |
| legacy / qa_answer | 26 | 26 | 26 | 615303 |
| legacy / qa_review | 36 | 36 | 37 | 823197 |
| legacy / qa_revision | 10 | 10 | 10 | 246769 |
| legacy / reranker | 30 | 30 | 30 | 515829 |
| legacy / retrieval | 30 | 0 | 0 | 0 |
| runtime / analyzer | 28 | 28 | 28 | 79511 |
| runtime / decomposition | 28 | 28 | 28 | 37765 |
| runtime / embedding | 30 | 30 | 30 | unavailable |
| runtime / qa_answer | 26 | 26 | 26 | 613297 |
| runtime / qa_review | 33 | 33 | 33 | 739600 |
| runtime / qa_revision | 7 | 7 | 7 | 146013 |
| runtime / reranker | 30 | 30 | 30 | 524658 |
| runtime / retrieval | 30 | 0 | 0 | 0 |
| judge / judge | 28 | 28 | 31 | 487556 |

Generation and judge used gemini-3.8-flash, global, temperature 0; embeddings
used gemini-embedding-2 with 3072 dimensions. The judge is independent by input
and role, not by model family. A Qdrant client/server version warning did not
prevent completion. No configuration change was made in response.

## Verification, scope, and lifecycle

Pre-freeze focused tests: 107 passed across the two new A3 modules and existing
E2-A1/QA tests. The static check passed. Offline canonical score recomputation
reproduced FAIL/Q7 without live calls. The first closeout invocation omitted
PYTHONPATH and stopped at import; repeating with PYTHONPATH=src succeeded.
This local invocation error is outside the scientific infrastructure count.
Frozen candidate boundaries and whitespace checks were checked at closeout.
No full suite, T3, T5, reindex, or new evaluation was run during closeout.

AGY staffer-mtu2fno1-14b1e839 completed abstract pre-freeze design review only,
with no repository access or edits. Configured route: gemini-3.8-flash-high;
actual runtime model, effort, and token counts were unavailable. Its usage is
separate from the scientific counters. Historical E2-A2 artifacts and its
tuple/list recomputation defect remain untouched.

This bounded exposed cohort supports non-inferiority on the stated aggregate
quality and status gates, but fails activation integrity. It does not establish
representative unseen generalization, removal of legacy requirements, or E3
missing-point retrieval. Prior E1 and E2-A1/A2 results remain unchanged.

```text
E2-A3 = COMPLETE / FAIL / Q7
E2 = IN_PROGRESS / RUNTIME_ACTIVATION_FAILED / REPAIR_DECISION_PENDING
normal default = legacy_question_core
Phase E = IN_PROGRESS / E2
E3 = NOT_STARTED
NEXT_TASK_RECOMMENDATION = E2-A3 FAILURE REVIEW / REPAIR DECISION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

No default activation, repair, E3, D4, F2, or F3 execution follows this closeout.
