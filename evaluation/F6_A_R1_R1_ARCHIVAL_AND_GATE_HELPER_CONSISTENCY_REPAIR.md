# F6-A-R1-R1 — R1 Archival and Gate-Helper Consistency Repair

Decision: **F6-A-R1-R1 = COMPLETE / PASS / R1_ARCHIVAL_AND_GATE_HELPER_CONSISTENCY_REPAIRED.**

Type: zero-model-call archival/gate-helper consistency repair. The F6-A
scientific verdict is accepted and unchanged. Parent acceptance restored:
`F6-A-R1 = COMPLETE / PASS / OFFLINE_GATE_IDENTITY_ARCHIVAL_RECONCILED`.

```text
PANDA scientific/evaluation calls (R1-R1) = 0
PANDA scientific/evaluation tokens (R1-R1) = 0
```

## 1. Starting state

- Starting HEAD: `8d43fe8262f90b42fb68f7f891c9adcfff62e7c7`
  ("Reconcile F6-A offline gate and archive semantics") — matched the
  expected baseline; worktree clean; no unrelated user work.

## 2. Archival discrepancy and correction (defect A)

The R1 Markdown per-intent table carried incorrect case counts. The
authoritative counts, verified dynamically from the frozen 59-case records
and matching the corrected matrix, are:

| intent | cases |
| ------ | ----- |
| algorithm_implementation | 2 |
| algorithm_theory | 8 |
| api | 15 |
| installation | 12 |
| module_structure | 2 |
| troubleshooting | 6 |
| usage | 14 |
| **total** | **59** |

The R1 Markdown table has been corrected to exactly these counts (metric
values were verified unchanged) and now cites the authoritative corrected
matrix `evaluation/f6a_gold_gate_matrix_r1.json`.

## 3. Dual-source applicable case ID (defect B)

Derived deterministically from the frozen formal run under the canonical
contract (expected_status == answered AND metric applicable AND
required_source_types ⊇ {paper, code}):

```text
applicable_case_ids = [g060]
denominator = 1
passing_case_count = 0
rate = 0.0
gate_result = FAIL (unchanged)
```

`g060` is now recorded in the R1 Markdown, in this artifact, and in the new
R1-R1 matrix.

## 4. Gate-helper repairs (defects C/D/E)

`evaluation/scripts/f6a_gate_evaluation.py` (rewritten to reuse canonical
`aggregate_metrics` directly; no duplicated metric logic):

- **Zero-gate missing-measurement semantics (defect C)**: a missing
  measurement (`None`) yields `passed = null` (INCOMPLETE / not evaluated);
  only an actual numeric zero passes a zero-count gate; a non-zero count
  fails. The matrix distinguishes PASS / FAIL / INCOMPLETE.
- **Global intent-accuracy denominator (defect D)**: the intent-accuracy gate
  uses the intent accuracy's own case count — the sum of represented
  per-intent cases (59 for the complete formal run), never
  `expected_status_accuracy_denominator` merely because the two coincide in
  this run.
- **Per-intent missing-metric semantics (defect E)**: every represented
  intent remains visible. A represented intent whose required metric is
  unavailable is INCOMPLETE; the aggregate per-intent gate FAILs if any
  represented intent fails, is INCOMPLETE if none fail but some lack the
  metric, and PASSes only when every represented intent is measured and
  passes. Explicit per-intent details (intent, case_count,
  applicable_denominator, metric_value, threshold, passed) are emitted for
  both per-intent gates.
- **Failed/incomplete representation (§11)**: `failed_gate_names` /
  `failed_gate_count` and `incomplete_gate_names` / `incomplete_gate_count`
  are reported separately; `release_score` is accounting, not a gate, and is
  excluded from those counts.

## 5. New R1-R1 matrix

`evaluation/f6a_gold_gate_matrix_r1_r1.json` (the R1 matrix
`evaluation/f6a_gold_gate_matrix_r1.json` is preserved unchanged) records:
source run ID `f6a-rc1-gold-formal-full-20260913`, source_record_count 59,
source R1 matrix identity, evaluator revision, scientific_calls = 0,
scientific_tokens = 0, corrected gates, per-intent details, dual-source
applicable IDs `[g060]`, and:

```text
failed_gate_count = 9
failed_gate_names =
  answer_point_coverage / contradiction_count /
  critical_answer_point_miss_count / critical_final_evidence_recall /
  expected_status_accuracy / final_evidence_recall /
  major_unsupported_claim_count / paper_code_dual_source_rate /
  required_source_coverage_answered
incomplete_gate_count = 0
incomplete_gate_names = []
terminal_verdict_effect = NO_CHANGE / F6-A remains COMPLETE / FAIL /
  EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
```

Verified rather than assumed: the nine failed gates are identical to the R1
list, and zero incomplete gates occur on the current complete data.

## 6. Integrity

- Product behavior changes: **0**.
- Scientific calls/tokens in R1-R1: **0 / 0** (historical F6-A usage unchanged).
- novel_validation: **PRISTINE_FOR_CURRENT_LINEAGE**; holdout access **0**;
  protected-content leakage **0**.
- Original F6-A artifacts (run records, initial gate matrix, initial result
  MD/JSON, preregistrations, candidate manifest, R1 JSON) byte-unchanged;
  R1-R1 is additive except for the authorized R1 Markdown corrections above.
- Focused verification: `tests/unit/test_f6a_gate_evaluator.py` 11 passed +
  `test_f6a_release_infrastructure.py`/`test_f6_release_identity.py` 36
  passed + 18 subtests; `git diff --check` clean.

## 7. Lifecycle result

```text
F6-A-R1-R1 = COMPLETE / PASS / R1_ARCHIVAL_AND_GATE_HELPER_CONSISTENCY_REPAIRED
F6-A-R1 = COMPLETE / PASS / OFFLINE_GATE_IDENTITY_ARCHIVAL_RECONCILED (fully accepted after R1-R1)
F6-A = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
F6-B = LOCKED / F6_A_DID_NOT_PASS
Phase F = IN_PROGRESS / F6_A_RELEASE_GATE_FAILED
```

## 8. Next action

```text
NEXT_TASK_RECOMMENDATION =
POST-F6-A EXPOSED-GOLD FAILURE REVIEW / NEW CANDIDATE DEVELOPMENT
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
