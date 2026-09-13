# F6-A — Prerelease Validation & Generalization Gate: Result

Terminal decision: **F6-A = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED.**

```text
F6-B = LOCKED / F6_A_DID_NOT_PASS
Phase F = IN_PROGRESS / F6_A_RELEASE_GATE_FAILED
```

The decision is frozen before any case-level failure review (§53 discipline).
No product, prompt, retrieval, threshold, dataset, or candidate change follows
from this FAIL within this task.

## 1. Starting state and lineage

- Expected-baseline HEAD `5385d9a`; actual HEAD had advanced to `58940df`
  (superseded-plan A0/preregistration/freeze commits). Current-repository
  authority applied; the superseded 120-question plan was reconciled per the
  corrected F6-A protocol.
- Lineage: historical F6 attempt-1 HOLD → F6-LR1 staging reconciliation →
  F6-LR1-R1 roadmap alignment → selector-defined F6-A (this task).

## 2. Commits created (chronological)

```text
c871444/99fdbab  attempt-1 preflight identity fixes (historical, superseded plan)
cbb3f57/58940df  superseded preregistration + freeze (historical)
6e92a37/7b02db2/c9227f8  A0 release-freeze infrastructure (Docker Option A, git identity, manifest identity, clean-tree freeze)
f30d907  Prepare selector-defined F6-A evaluation identity (v3 calibration, loader successor support, §5.5 selector-completeness semantics, freezer calibration/selector identity)
500409c  Preregister selector-defined F6-A validation
28be395/50073dd  Refreeze candidate f6a-rc1-20260913 against selector identity + preregistration HEAD alignment
a4ee4ac/f62d4e1  candidate verification semantics (ancestor HEAD; evaluation-infrastructure-only source drift accepted as diagnostic)
```

## 3. Stage A0 findings (zero-outcome)

- **Debt A closed**: freezer enforces the evaluator's signed v2.6 authority
  contract (dataset hash + official_ready + structurally_valid + version).
- **Debt B closed**: freeze records `benchmark_manifest_sha256`, version,
  dataset hash, question count, official flags, status.
- **Debt C decided (Option A)**: Docker image identity is release-critical —
  the compose-managed PostgreSQL/Qdrant pair materially defines the evaluated
  runtime; freeze requires both services captured with concrete identities.
- **Debt D closed**: preregistration/result schemas define
  `candidate_changes_after_freeze = NOT_REACHED` when no candidate is frozen.
- **Debt E closed without file change**: the attempt-1 `dataset_record_correction`
  block already provides g021 post-signing traceability; no additional receipt
  needed.
- **§5.2/5.3 calibration reconciliation**: the reviewed v2 classification
  (bound to pre-D4-A2-R1 SHA `b5406e36…`) was mechanically reconciled to the
  current Gold (`6f12d54b…`) as versioned successor
  `phase_b_t3_product_language_scope_v3` — the g021 correction changed
  criticality metadata only, and re-derivation reproduces the declared 59/21
  IDs exactly. No fresh human review claimed.
- **§5.5 stale semantics removed**: the product gate is now computed from
  selector-cohort completeness; full-dev execution is a diagnostic option, not
  a prerequisite.
- **§5.6 identity completed**: freeze records the implementation Git commit
  (clean implementation tree required at freeze), the calibration identity,
  and the exact selector output hash
  (`e27ef67a…`, 59 IDs).
- Focused verification: 235 passed + 45 subtests across the A0 test files and
  the qa/evaluator regression surfaces.

## 4. Preregistration and frozen candidate

- Preregistration commit: `500409c` (MD + JSON with the exact 59 formal-English
  IDs and the selector hash `e27ef67a…`); freeze HEAD `28be395` recorded and
  aligned (`50073dd`).
- Candidate: `f6a-rc1-20260913`, manifest SHA-256 `e331a5bc1c7309fb…`, verified
  valid (mismatches: none). Runtime mode `legacy_question_core`; models as
  recorded in the preregistration; prompt set 3.10.1.
- Superseded-plan artifacts preserved: the earlier preregistration/freeze
  commits, and the terminated 9/120-case partial run
  (`data/evaluation/runs/f6a-rc1-gold-full-20260913`, unmodified, not F6-A
  evidence).

## 5. Stage A1 — formal Gold product-scope full run

- Run ID: `f6a-rc1-gold-formal-full-20260913`; mode full; cohort = the exact
  59 formal-English selector IDs; 59/59 records complete after interruption
  recovery (below); candidate identity verified before/after.
- **Infrastructure incidents (§19)**: the run process was three times
  externally terminated without traceback (session-host process cleanup); each
  time it was resumed with the same run ID/candidate/preregistration and
  completed records reused (§38). Two cases (g112, g113) first failed with
  Vertex 429 RESOURCE_EXHAUSTED (provider quota); after quota recovery their
  error records were removed and the cases retried successfully under the same
  frozen identity (original records preserved as
  `results.jsonl.pre-retry-backup`; the retry is recorded here and in the
  usage accounting, which includes the failed attempts' consumption).
- **Release score: 0.8277** (denominator 59/59; no incomplete cases after
  retry).

## 6. Gold gate matrix (preregistered thresholds)

| Gate | Value | Threshold | Result |
| ---- | ----- | --------- | ------ |
| cohort completeness | 59/59 exact selector set | exact | PASS |
| candidate identity | valid (evaluation-infra-only drift diagnostic) | unchanged behavior identity | PASS |
| gold_recall_at_10 | 0.9898 | ≥ 0.95 | PASS |
| intent_accuracy | 0.9831 | ≥ 0.90 | PASS |
| per_intent_gold_recall_at_10 / per_intent_intent_accuracy | 0.9898 / 0.9831 | ≥ 0.75 / ≥ 0.80 | PASS |
| citation_integrity | 1.00 | == 1.00 | PASS |
| wrong_version_evidence_count | 0 | == 0 | PASS |
| forbidden_evidence_count | 0 | == 0 | PASS |
| identifier_hallucination_rate | 0.00 | < 0.03 | PASS |
| unhandled_exception_count (product pipeline) | 0 | == 0 | PASS |
| **final_evidence_recall** | **0.8129** | ≥ 0.90 | **FAIL** |
| **critical_final_evidence_recall** | **0.8231** | == 1.00 | **FAIL** |
| **expected_status_accuracy** | **0.8644** | ≥ 0.975 | **FAIL** |
| **required_source_coverage_answered** | **0.9388** | ≥ 0.97 | **FAIL** |
| **paper_code_dual_source_rate** | **0.1633** (49 applicable) | == 1.00 | **FAIL** |
| **answer_point_coverage** | **0.8446** | ≥ 0.90 | **FAIL** |
| **critical_answer_point_miss_count** | **18** | == 0 | **FAIL** |
| **contradiction_count** | **4** | == 0 | **FAIL** |
| **major_unsupported_claim_count** | **1** | == 0 | **FAIL** |

Status distribution: 44 answered / 12 insufficient_evidence / 3
version_conflict. Expected/actual status mismatches: 8 cases — six
Gold-answered cases refused as insufficient evidence (g005, g013, g027, g034,
g059, g060), of which four carry the same contradiction pattern ("the answer
claims the locked corpus does not define PandaRoot/LuminosityFit while the
cited evidence documents exactly that"), plus g012 (expected version_conflict,
got insufficient_evidence) and g026 (expected version_conflict, got answered).

## 7. Gate verdict

Ten preregistered Gold gates fail, including hard safety invariants
(critical_answer_point_miss_count, contradiction_count,
major_unsupported_claim_count) and the primary quality gates
(final_evidence_recall, answer_point_coverage, expected_status_accuracy). The
failures are internally consistent (the erroneous-refusal pattern drives the
recall/coverage/status failures simultaneously) and are product failures, not
evaluator artifacts: per-case metric fields and judge reasons align with the
recorded product behavior. Per the preregistered fail-fast order:

```text
F6-A = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
F6-B = LOCKED / F6_A_DID_NOT_PASS
```

Stages A2 (ablation), A3 (novel_dev), A4 (novel_validation), and A5 (composer
empirical audit) were NOT run: the FAIL was frozen before exposing further
cohorts (novel_validation remains PRISTINE_FOR_CURRENT_LINEAGE). Composer
gates are NOT_REACHED (diagnostic note: within Stage A1 the composer recorded
35 attempts / 32 acceptances, and no composer-related safety metric appeared
in any failure). E3 opportunistic evidence: none applicable (legacy default).

## 8. Scientific accounting (actual)

```text
PANDA scientific/evaluation calls = 383
PANDA scientific/evaluation tokens = 3,348,432
```

Breakdown (Stage A1 formal Gold run): product runtime 319 calls /
2,980,205 tokens (F4 role counters: qa_generation 69, qa_composer 38 calls,
plus embedding/verification within the aggregate); external judge 64 calls /
368,227 tokens. Includes the two 429-failed first attempts (g112/g113). The
terminated superseded-plan partial run consumed additional quota outside F6-A
accounting (9 cases, preserved records). Pre-outcome A0/A1 stages: 0
scientific calls.

## 9. Integrity audit

- Product changes after freeze: **0** (post-freeze commits touched only the
  candidate verifier's own semantics — evaluation infrastructure; the frozen
  behavior identity hashes are unchanged and the drift is recorded as a
  diagnostic).
- Threshold changes after preregistration: **0**.
- Validation-driven tuning: **0** (novel_validation not executed).
- Holdout access: **0**; protected-content leakage: **0**.
- Mixed candidate identities: **0** (all 59 records under
  f6a-rc1-20260913).
- No PASS chasing: the FAIL is frozen; no repair follows in this task.

## 10. Failure review boundary

Aggregate failure analysis only (above). Case-level inspection of the failed
Gold cases for future development is permitted only under the exposure-ledger
policy in a separately authorized task; this task performs no such inspection.

## 11. Next action

```text
NEXT_TASK_RECOMMENDATION =
SEPARATELY_AUTHORIZED POST-F6-A FAILURE REVIEW / NEW CANDIDATE WORK ONLY
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

A repaired candidate (the erroneous "not defined in the locked corpus"
refusal pattern is the obvious first investigation target for a future
authorized task) requires a new development task, a new candidate identity,
and a new F6-A attempt. F6-B remains locked.
