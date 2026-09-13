# F6-A-R1-R1-R1 — Per-Intent Intent-Accuracy Denominator Emission Repair

Decision: **F6-A-R1-R1-R1 = COMPLETE / PASS / PER_INTENT_INTENT_ACCURACY_DENOMINATOR_EMISSION_REPAIRED.**

Type: zero-model-call machine-readable consistency repair. The accepted
lifecycle is closed, not reopened: R1-R1 remains substantively accepted and
this task repairs only its machine-readable denominator emission.

```text
PANDA scientific/evaluation calls (R1-R1-R1) = 0
PANDA scientific/evaluation tokens (R1-R1-R1) = 0
```

## 1. Starting state

- Starting HEAD: `5730e9239cb8db458ca0189ea1f502ed3e0f7159`
  ("Align roadmap gate values and complete R1-R1 artifacts") — matched the
  expected baseline; worktree clean; no unrelated user work.

## 2. Defect

Independent audit of the R1-R1 matrix found:

```text
per_intent_intent_accuracy.per_intent_details[*].applicable_denominator = null
```

for all seven represented intents. The gate metric values and PASS states were
already correct; only the detail denominator was incomplete.

Cause: `per_intent_gate(...)` emitted
`entry.get(f"{metric_key}_denominator")`. Canonical `aggregate_metrics`
`per_intent` entries expose per-intent denominators for the recall metrics
(`gold_recall_at_10_denominator`, `final_evidence_recall_denominator`) but no
`intent_accuracy_denominator`, so the lookup returned `None` for every intent
under `metric_key = intent_accuracy`. The recall per-intent details were
unaffected.

## 3. Denominator semantics

`evaluation/scripts/f6a_gate_evaluation.py` now derives the intent-accuracy
applicability denominator deterministically from the same immutable records
(`per_intent_intent_accuracy_denominators`), never from hard-coded counts and
never unconditionally `case_count`:

```text
applicable_denominator(intent) =
    count(records for intent where metrics.intent_correct is not None
          and metric_applicability does not override intent_correct to False)
```

This mirrors the canonical `aggregate_metrics` measurement rule exactly (the
`metric_applicability` override plus a non-None `intent_correct` value — the
same cases the canonical `intent_accuracy` mean includes), so the emitted
denominator matches the metric arithmetic without duplicating or altering it.
A represented intent with zero measurable cases reports denominator 0 and
stays INCOMPLETE, consistent with the established R1-R1 missing-metric rules.
`per_intent_gold_recall_at_10` keeps the canonical denominator behavior
unchanged.

## 4. Current per-intent output (59/59 formal cohort)

Verified from the successor matrix, not assumed:

```text
intent                    case_count  applicable_denominator  metric_value          passed
algorithm_implementation           2                       2  1.0                   True
algorithm_theory                   8                       8  1.0                   True
api                               15                      15  1.0                   True
installation                      12                      12  1.0                   True
module_structure                   2                       2  1.0                   True
troubleshooting                    6                       6  1.0                   True
usage                             14                      14  0.9285714285714286    True
```

All metric values and PASS states are unchanged; the recall per-intent
details are byte-identical to the R1-R1 matrix.

## 5. Successor matrix

`evaluation/f6a_gold_gate_matrix_r1_r1_r1.json` (schema
`f6a-gate-matrix-r1r1r1-v1`) is derived from the exact same immutable
59-case records (`source_run_id = f6a-rc1-gold-formal-full-20260913`,
`source_record_count = 59`) with `source_r1_r1_matrix =
evaluation/f6a_gold_gate_matrix_r1_r1.json`. The R1-R1 matrix is preserved
unchanged as the R1-R1 artifact.

The generator now performs a strict source-matrix comparison: every gate
datum (values, thresholds, passed states, canonical denominators, and
per-intent details) must match the prior matrix exactly except the repaired
`applicable_denominator` field; any divergence refuses to write the successor.
A tampered-value check confirmed the comparison detects mutations. Verified
output:

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
dual_source_applicable_ids = [g060]
terminal_verdict_effect = NO_CHANGE / F6-A remains COMPLETE / FAIL /
  EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
release_score = 0.8276836158192091 (unchanged)
```

## 6. Tests

`tests/unit/test_f6a_gate_evaluator.py` — 15 passed (11 prior + 4 new):

- fully measured intents emit concrete non-null denominators equal to their
  measurable case counts;
- partially measured intent: `case_count = 2` vs
  `applicable_denominator = 1` reported distinctly;
- fully unmeasured represented intent: denominator 0, per-intent and
  aggregate gate INCOMPLETE;
- explicit `metric_applicability["intent_correct"] = False` excludes a case
  from the denominator even with a non-None value (canonical rule).

The script performs zero model/scientific calls by construction (deterministic
offline aggregation only).

## 7. Integrity

- Product behavior changes: **0**; no new candidate created.
- Scientific calls/tokens in R1-R1-R1: **0 / 0** (historical F6-A usage
  unchanged: formal 383 calls / 3,348,432 tokens; superseded 9/120 plan
  61 calls / 339,150 tokens).
- novel_validation: **PRISTINE_FOR_CURRENT_LINEAGE**; holdout access **0**;
  protected-content leakage **0**.
- Immutable artifacts unchanged: formal 59-case run records, superseded 9/120
  records, original F6-A result artifacts, preregistrations, candidate
  manifest, R1 matrix, R1-R1 matrix, Gold dataset, novel datasets.

## 8. Lifecycle result

```text
F6-A-R1-R1-R1 = COMPLETE / PASS / PER_INTENT_INTENT_ACCURACY_DENOMINATOR_EMISSION_REPAIRED
F6-A-R1-R1 = COMPLETE / PASS / R1_ARCHIVAL_AND_GATE_HELPER_CONSISTENCY_REPAIRED (substantively accepted)
F6-A-R1 = COMPLETE / PASS / OFFLINE_GATE_IDENTITY_ARCHIVAL_RECONCILED
F6-A = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
F6-B = LOCKED / F6_A_DID_NOT_PASS
Phase F = IN_PROGRESS / F6_A_RELEASE_GATE_FAILED
```

The reconciliation chain is closed.

## 9. Next action

```text
NEXT_TASK_RECOMMENDATION =
POST-F6-A EXPOSED-GOLD FAILURE REVIEW / NEW CANDIDATE DEVELOPMENT
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
