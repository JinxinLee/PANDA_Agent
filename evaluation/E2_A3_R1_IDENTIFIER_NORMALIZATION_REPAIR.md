# E2-A3-R1 — Identifier Normalization Repair and Targeted Revalidation

## Candidate state before live execution

Historical E2-A3 = COMPLETE / FAIL / Q7. FR1 = COMPLETE / PASS /
Q7_VERIFIER_IDENTIFIER_NORMALIZATION_REPAIR_JUSTIFIED. Starting HEAD:
e5941c5f9aac45d98b739a48b245be53a41c6d80.

The production repair adds `_normalise_rejected_identifier_token` in qa.py and
uses it only in the unsupported-identifier rejecting loop. It retains terminal
period removal and removes one single terminal colon unless ending in ::.
Positive-support logic, regex, eligibility, matching, prompts, E1/E2, retrieval,
public API/DTO and legacy compatibility remain unchanged. Pre-verdict default
is legacy_question_core. No case-specific logic or allowlist was added.

Focused tests passed: 130 across the new R1 module and existing A3 runtime,
A3 evaluator, E2-A1 coverage, and QA modules. The complete repaired-code frozen
scan independently recomputed 56 executions, 299 serialized claim copies, and
157 snapshots (legacy 81/runtime 76). Exactly one rejection outcome changed:
g112 runtime initial claim_3, supported PndLmdDataReader::fillData with a trailing
prose colon. No genuinely unsupported base became accepted; no accepted check
became rejected. g110 prefix_pid.root/prefix_boost.root and g002 SIMPATH/bin/cmake
controls remained rejected. S1-S12 all PASS. Whole-module AST reversal verifies
that only the approved helper and one call differ from the starting QA code.

Static evidence: `e2_a3_r1_identifier_normalization_static_result.json`.
Protocol: `E2_A3_R1_TARGETED_REVALIDATION_PREREGISTRATION.md`.
Manifest: `e2_a3_r1_targeted_revalidation_manifest.json`.
Fixed cohort: g112, g110, g002, g044, g027, ten fresh executions and five blind
judgments after separate candidate/raw freezes. No retrieval bootstrap.

Scientific calls before candidate freeze: 0. Prospective verdict: NOT_RUN.
No runtime activation has occurred at this candidate boundary. Results will be
appended only after raw and judgments are independently committed.

## Frozen scientific closeout

**VERDICT = FAIL / P2, P6.** No activation commit. Normal default remains
`legacy_question_core`. The repaired normalizer is retained; no further repair
or selective rerun was performed. Historical A3 FAIL and FR1 PASS are unchanged.

| Boundary | Commit |
| --- | --- |
| Starting HEAD | `e5941c5f9aac45d98b739a48b245be53a41c6d80` |
| Repaired candidate/preregistration | `0dd7adf2c5aa456396b39890dbf968df1bcb4161` |
| Ten paired raw outputs | `4092209a11f57ac757502b01e2c55332b88a0519` |
| Five blinded judgments | `8e73df44d0d39dde93cb9349d8896c15dafefe7f` |
| Scientific result / closeout | Commit containing this final report, directly following the judgment commit |
| Activation | NOT CREATED |

Exact cases: g112, g110, g002, g044, g027. Five fresh legacy and five fresh
runtime executions completed without infrastructure errors, in frozen alternating
order. Five independent-role judgments were frozen before label interpretation.
All five pairs are scoreable. No retrieval bootstrap or protected data was used.

| Gate | Result | Evidence |
| --- | --- | --- |
| S1-S12 | PASS | Repaired-code static scan and focused tests |
| P1 | PASS | 5/5 legacy, 5/5 runtime, 5/5 scoreable judgments |
| P2 | FAIL | g027 runtime adds incomplete_citation in its initial review |
| P3 | PASS | g112 runtime no unsupported_identifier; valid, evaluable, complete; no structural error |
| P4 | PASS | Expected-status correct 5/5 in both arms; new false answers/refusals 0/0 |
| P5 | PASS | Critical runtime regressions 0 |
| P6 | FAIL | Runtime worse 1, frozen limit 0 |
| P7 | PASS | Legacy decomposition 0, runtime 5 (one each); revision >1 zero; postverify retrieval zero |
| P8 | PASS | Additional adapter requests (-1 + 1 + 1 + 1 + 3)/5 = 1.0 <= 2.0 |
| P9 | PASS | Public/API/compatibility preserved; default remains legacy |

| Case | Legacy integrity | Runtime integrity | New category | Pairwise quality |
| --- | --- | --- | --- | --- |
| g112 | unsupported_identifier | none | none | better |
| g110 | none | none | none | better |
| g002 | unsupported_identifier | unsupported_identifier | none | worse |
| g044 | none | none | none | equivalent |
| g027 | none | incomplete_citation | incomplete_citation | equivalent |

Aggregate quality: better 2, equivalent 2, worse 1; critical regressions 0.
All five runtime decompositions are valid and all final coverage audits are
evaluable and complete. Runtime revisions: g002 and g027 each one, the other
three zero. Legacy revisions: g112 and g002 each one. Each arm made five
retrieval operations, with no extra targeted retrieval or postverify retrieval.

### Failure evidence

P2: g027 runtime first review reports
`incomplete web citation evidence.d452f25b295c0ce037b92b26` and
`missing answer point point.3`. Initial claim.3 cites the Sphinx MasterTasks
page, whose frozen locator has URL and snapshot_date but an empty section_path.
The existing web-citation check requires all three. Legacy g027 has no review
errors. The bounded runtime revision removes that web evidence ID and retains
three code citations; its final review is error-free and coverage complete.
The initial incomplete citation still counts under the frozen all-reviews rule.
This is an observed citation regression, not evidence that the colon repair
caused the source-selection difference; no new root-cause repair is authorized.

P6: g002 (index 2, A=legacy/B=runtime) is judged worse for runtime because
legacy includes the documented Spack and CVMFS pre-installation details and
is slightly more complete. Both outputs are marked supported; critical_regression
is false. One noncritical worse outcome exceeds this five-case protocol's zero
tolerance. No rejudge or threshold change is permitted.

g112 runtime passes the repaired integration sentinel without revision or any
verification errors. Its fresh legacy arm reports PndLmdTrackQ::GetSecondary
and PndLmdTrackQ::GetTrkRecStatus unsupported initially, repaired by its one
revision. This fresh generation differs from historical A3; it does not alter
the frozen static negative-control result or historical verdict. g002 retains
the SIMPATH/bin/cmake initial unsupported category in both fresh arms.

### Scientific usage

Scientific/provider calls before candidate freeze: **0**. Static tests and
frozen reconciliation make no live calls. Prospective usage:

| Slice | Logical operations | Returned model responses | Adapter attempts | Observable tokens |
| --- | --- | --- | --- | --- |
| legacy | 34 | 29 | 29 | 579527 |
| runtime | 39 | 34 | 34 | 619495 |
| judge | 5 | 5 | 5 | 170970 |
| Total | 78 | 68 | 68 | 1369992 |

| Slice / stage | Logical | Returned | Adapter | Tokens |
| --- | --- | --- | --- | --- |
| legacy / analyzer | 5 | 5 | 5 | 9993 |
| legacy / embedding | 5 | 5 | 5 | unavailable |
| legacy / qa_answer | 5 | 5 | 5 | 187817 |
| legacy / qa_review | 7 | 7 | 7 | 235005 |
| legacy / qa_revision | 2 | 2 | 2 | 57583 |
| legacy / reranker | 5 | 5 | 5 | 89129 |
| legacy / retrieval | 5 | 0 | 0 | 0 |
| runtime / analyzer | 5 | 5 | 5 | 11446 |
| runtime / decomposition | 5 | 5 | 5 | 6117 |
| runtime / embedding | 5 | 5 | 5 | unavailable |
| runtime / qa_answer | 5 | 5 | 5 | 186850 |
| runtime / qa_review | 7 | 7 | 7 | 251857 |
| runtime / qa_revision | 2 | 2 | 2 | 73172 |
| runtime / reranker | 5 | 5 | 5 | 90053 |
| runtime / retrieval | 5 | 0 | 0 | 0 |
| judge / judge | 5 | 5 | 5 | 170970 |

Embedding tokens are unavailable, not zero consumption. Logical operations
include retrieval; returned model responses include embeddings. No extra adapter
attempts above returned responses occurred. These are not provider HTTP/billing
counts, and monetary cost is unavailable. Qdrant client 1.19.0/server 1.15.5
compatibility warnings occurred; all executions completed without configuration
changes. The separate abstract AGY pre-freeze review completed; configured route
gemini-3.8-flash-high, actual model/effort and usage unobserved.

### Closeout verification and interpretation

Pre-freeze focused tests: 130 passed; after the evaluator product-error handling
addition, its 23 directly affected tests passed again. Static S1-S12 passed.
Offline canonical recomputation reproduced exactly FAIL/P2/P6. Frozen candidate
source/config/tests/protocol boundaries remained unchanged throughout science.
Whitespace and final changed-path checks passed. No post-activation tests were
run because activation was forbidden by the failed scientific verdict.

The deterministic repair establishes removal of the demonstrated punctuation
false rejection without weakening the frozen negative controls. Five prospective
pairs establish successful g112 integration but fail the broader bounded
activation gates on g027 citation integrity and g002 quality. Historical A3
Q1-Q6, Q8-Q15 and PAIR09 are carried-forward compatible historical evidence
under the old candidate, not remeasured repaired-candidate PASS results. This
small exposed cohort and same-model-family judge do not establish representative
generalization or authorize E3, legacy requirement retirement, T3/T5, D4, F2/F3.

```text
E2-A3 = COMPLETE / FAIL / Q7
E2-A3-FR1 = COMPLETE / PASS / Q7_VERIFIER_IDENTIFIER_NORMALIZATION_REPAIR_JUSTIFIED
E2-A3-R1 = COMPLETE / FAIL / P2_P6
E2 = IN_PROGRESS / RUNTIME_ACTIVATION_FAILED / REPAIR_REASSESSMENT_PENDING
normal default = legacy_question_core
Phase E = IN_PROGRESS / E2
E3 = NOT_STARTED
NEXT_TASK_RECOMMENDATION = E2-A3-R1 FAILURE REVIEW / REPAIR REASSESSMENT
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
