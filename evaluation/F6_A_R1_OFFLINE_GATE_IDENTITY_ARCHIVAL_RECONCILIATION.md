# F6-A-R1 — Offline Gate / Identity / Archival Reconciliation

Decision: **F6-A-R1 = COMPLETE / PASS / OFFLINE_GATE_IDENTITY_ARCHIVAL_RECONCILED.**

Type: zero-model-call evaluator / release-identity / archival correction.

```text
PANDA scientific/evaluation calls (F6-A-R1 itself) = 0
PANDA scientific/evaluation tokens (F6-A-R1 itself) = 0
```

The accepted F6-A terminal FAIL is preserved (see §5); this reconciliation
corrects the derived gate arithmetic, applicability/denominator semantics,
freeze-verifier interpretation, archival wording, and usage accounting. It
supersedes the initial F6-A closeout only for those derived layers — the
underlying scientific records are unchanged.

## 1. Starting state

- Starting HEAD: `e34ecdc9bfc265a35e679a361c98ee64348e19c1`
  ("Record F6-A prerelease validation result") — matched the expected
  baseline; worktree clean; no unrelated user work.

## 2. Immutable source evidence

- Formal run: `data/evaluation/runs/f6a-rc1-gold-formal-full-20260913`
  (candidate `f6a-rc1-20260913`, freeze HEAD `28be395`, preregistration
  `evaluation/f6_a_prerelease_validation_preregistration.json`).
- 59/59 records complete; g112/g113 first-attempt 429 error records were
  removed-and-retried after quota recovery with the pre-retry snapshot
  preserved (`results.jsonl.pre-retry-backup`) — accepted infrastructure
  recovery (§2.5), not rerun again in R1.
- Original artifacts preserved byte-unchanged: initial gate matrix
  (`f6a_gold_gate_matrix.json`), initial result MD/JSON, both
  preregistrations, candidate manifest, superseded 9/120 partial run.
- Superseded-plan run: `data/evaluation/runs/f6a-rc1-gold-full-20260913`
  (9/120 records, terminated) — preserved, excluded from F6-A evidence.

## 3. Original metric defects and corrections

The initial gate script computed several gates with non-canonical semantics.
The corrected evaluator (`evaluation/scripts/f6a_gate_evaluation.py`, R1
revision) reuses `evaluation.aggregate_metrics` directly (canonical
repository semantics; no duplicated metric logic) and derives the gate matrix
from its output. Measured model outputs are the immutable records; everything
in the corrected matrix is OFFLINE DERIVED METRICS.

### Correction A — paper/code dual-source denominator

Canonical applicability (answered + `metric_applicability.paper_code_dual_source`
+ `required_source_types ⊇ {paper, code}`) yields **1 applicable case**
(denominator was incorrectly 49 all-answered cases).

```text
applicable_case_ids: the single dual-source-required answered case
denominator: 1
passing_case_count: 0
corrected_rate: 0.0
threshold: == 1.00
gate_result: FAIL (unchanged)
```

### Corrections B/C — true per-intent gates

Per-intent values from canonical per-intent aggregation (7 represented
intents; case counts derived from records):

| intent | cases | gold_recall_at_10 (≥0.75) | intent_accuracy (≥0.80) |
| ------ | ----- | ------------------------- | ----------------------- |
| algorithm_implementation | 33 | 1.0 PASS | 1.0 PASS |
| algorithm_theory | 4 | 1.0 PASS | 1.0 PASS |
| api | 4 | 1.0 PASS | 1.0 PASS |
| installation | 4 | 1.0 PASS | 1.0 PASS |
| module_structure | 3 | 1.0 PASS | 1.0 PASS |
| troubleshooting | 4 | 1.0 PASS | 1.0 PASS |
| usage | 11 | 0.9583 PASS | 0.9286 PASS |

(The per-intent case counts are reported by the corrected matrix; the initial
script collapsed all intents into single whole-cohort means, masking the
weakest intent. The aggregate per-intent gate PASSES under corrected
semantics — `min(recall)=0.9583`, `min(accuracy)=0.9286`.)

### Correction D — identifier hallucination denominator

```text
identifier_hallucination_count = 0
identifier_mentions (total) = 121
corrected rate = 0.0
threshold < 0.03
gate_result: PASS (unchanged value; denominator corrected from
"records with a mentions field" to total identifier mentions)
```

The corrected evaluator also fixed an upper-bound direction bug: this gate is
`rate < 0.03`; the initial script's lower-bound comparison would have
misread any positive rate.

### Correction E — failed-gate count

Derived from the corrected matrix (no assumed count):

```text
failed_gate_count = 9
failed_gate_names =
  answer_point_coverage (0.8446 < 0.90)
  contradiction_count (4 != 0)
  critical_answer_point_miss_count (18 != 0)
  critical_final_evidence_recall (0.8231 != 1.00)
  expected_status_accuracy (0.8644 < 0.975)
  final_evidence_recall (0.8129 < 0.90)
  major_unsupported_claim_count (1 != 0)
  paper_code_dual_source_rate (0.0 != 1.00)
  required_source_coverage_answered (0.9388 < 0.97)
newly_changed_gate_results =
  paper_code_dual_source_rate FAIL retained (value 0.1633 → 0.0, denominator corrected)
  identifier_hallucination_rate PASS retained (denominator corrected)
  per_intent gates now evaluated truly per intent (both PASS)
```

## 4. Terminal F6-A verdict (§12)

The corrected offline matrix still contains nine mandatory Gold gate failures.
The terminal verdict is preserved:

```text
F6-A = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
```

No HOLD reconsideration was triggered (several failures are unrelated to
Corrections A–D).

## 5. Case-level inspection statement correction (§13)

The initial closeout stated "aggregate failure analysis only" / "no case-level
inspection". That was inaccurate. Corrected archival statement:

> Case-level inspection of already-exposed Gold failures occurred for failure
> classification after the frozen Stage A1 outcome (the erroneous-refusal
> pattern and version-conflict cases were identified by case ID). No product
> repair, prompt change, retrieval change, threshold change, candidate change,
> or rerun followed from that inspection within F6-A. novel_validation was not
> executed and remains pristine for the current lineage.

No additional qualitative case-level investigation was performed in R1.

## 6–7. Usage reconciliation (§14) and candidate identity chronology (§15)

### Usage

```text
FORMAL_F6_A_EVIDENCE_USAGE:
  product runtime 319 calls / 2,980,205 tokens
  external judge    64 calls /   368,227 tokens
  total            383 calls / 3,348,432 tokens
  (includes the two 429-failed first attempts for g112/g113)

SUPERSEDED_PLAN_USAGE (9/120 partial run, excluded from F6-A evidence):
  superseded_plan_product_calls = 52
  superseded_plan_product_tokens = 302,469
  superseded_plan_judge_calls = 9
  superseded_plan_judge_tokens = 36,681
  superseded_plan_total_calls = 61
  superseded_plan_total_tokens = 339,150

TOTAL_SCIENTIFIC_USAGE_DURING_F6_A_WORK:
  444 calls / 3,687,582 tokens
```

All values are deterministic aggregations of preserved per-case
`model_call_breakdown` records; no field was missing.

### Freeze/source chronology

- Freeze HEAD: `28be395` (candidate f6a-rc1-20260913 frozen on a clean
  implementation tree).
- All 59 formal records completed by 2026-09-13T00:31:43Z.
- Post-freeze `src/` changes: exactly one file, `src/panda_agent/candidate.py`
  (commits `a4ee4ac` 02:37:24+02:00 and `f62d4e1` 02:39:22+02:00 — both AFTER
  the last scientific record). `candidate.py` is the verifier itself and is
  not imported by the QA runtime; no product/evaluator execution semantics
  changed.
- All 59 formal records therefore share one actual product behavior identity.
  **No mixed execution identity detected.**
- Prior `valid=True` was not trusted: this audit independently confirmed the
  chronology above via commit timestamps and record completion times.

## 7. Candidate verifier repair (§16/§17)

The broad `EVALUATION_INFRASTRUCTURE_PATHS` whitelist (which could drop
`source_tree_hash` from mismatches when only candidate/runner/evaluator/CLI
files changed — including files that materially affect execution and scoring)
was **removed**. New strict semantics:

- Ancestry: the frozen implementation commit must be an ancestor of (or equal
  to) the current HEAD.
- Source identity: any `src/` change after freeze makes current-checkout
  verification fail (`source_tree_hash` mismatch) — no silent whitelisting.
- Offline evaluator corrections are recorded as separate offline rescore
  identities (this R1 matrix carries `offline rescore evaluator revision`),
  never by pretending the old freeze matches the current tree.
- RUN-TIME FROZEN CANDIDATE IDENTITY (28be395, under which all 59 records were
  produced) is distinguished from CURRENT CHECKOUT CANDIDATE VERIFICATION: the
  current checkout intentionally no longer verifies byte-for-byte against the
  old freeze after the R1 verifier/evaluator corrections, and the historical
  run's records remain scientifically usable.

Focused tests added: `tests/unit/test_f6a_gate_evaluator.py` (7 tests: dual
denominator, identifier denominator, upper-bound zero rate, per-intent minima,
failed-list derivation, zero-model-call check) plus the tightened verifier
covered by `test_f6a_release_infrastructure.py`/`test_f6_release_identity.py`
(42 passed + 18 subtests total across the R1/A0 test files).

## 8. Integrity

- Product behavior changes in R1: **0** (only the verifier/evaluator
  derivation corrections).
- Validation/holdout exposure: **0** (novel_validation pristine; holdout
  untouched).
- Original evidence immutability: run records, initial gate matrix, initial
  result MD/JSON, preregistrations, candidate manifest — all byte-unchanged.
