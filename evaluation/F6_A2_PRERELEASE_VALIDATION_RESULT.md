# F6-A Attempt 2 — Prerelease Validation & Generalization Gate (Result)

Decision: **F6-A Attempt 2 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED** (Stage A1
fail-fast; A2/A3/A4/A5 NOT_REACHED).

Companion machine-readable record: `evaluation/f6_a2_prerelease_validation_result.json`.

## 1. Attempt chronology and identity

- Starting HEAD: `758963f` ("Record F6-A failure-review development closeout").
- Commit A (A0 bookkeeping): `619128b` — "Prepare F6-A attempt 2 release identity"
  (roadmap stale "ten → nine preregistered gates failed" correction only; no product change).
- Commit B (preregistration): `3f1f16e` — "Preregister F6-A attempt 2"
  (`evaluation/f6_a2_prerelease_validation_preregistration.json` + MD; zero scientific calls
  before this point).
- Candidate freeze: `f6a-rc2-20260913`, frozen from the clean committed preregistration HEAD
  (`implementation_git_commit = 3f1f16e`); freeze commit `1f32eef`;
  `verify-candidate` → `valid = true`, zero mismatches. Zero product/config/prompt/model/
  retrieval/dataset/selector changes after freeze.
- Zero-outcome preflight: Gold manifest authority valid (m6-benchmark-v2.6,
  `dataset_sha256 = 6f12d54b…`, 120-question universe); calibration v3 compatible;
  selector derived (59 IDs, `sha256 = e27ef67a…`, 21 non-English dev IDs excluded);
  Docker runtime verified (`postgres:17-alpine`, `qdrant:v1.15.5`, healthy);
  index fingerprint `8172f9a6…` unchanged; A0 focused tests 314 passed + 68 subtests;
  FR1 change-boundary audit clean (exactly the two authorized behavior changes in
  `45f14ba`; no unexpected behavior change).

## 2. Stage A1 — Formal Gold (selector cohort)

- Run ID: `f6a-rc2-gold-formal-full-20260913`; mode `full`; 59/59 complete;
  zero error records; no resume/retry needed; duration 14:44:15 → 16:00:26 UTC.
- Status outcomes: 49 answered, 5 insufficient_evidence, 5 version_conflict.
- **expected_status_accuracy = 1.0 (59/59; attempt-1: 0.8644).** Zero status mismatches
  (attempt-1 had 8).

## 3. Gate decision (R1-R1-R1 corrected gate semantics)

Gate matrix: `data/evaluation/runs/f6a-rc2-gold-formal-full-20260913/gate_matrix.json`.

| gate | value | threshold | result |
| ---- | ----- | --------- | ------ |
| gold_recall_at_10 | 0.9898 | ≥ 0.95 | PASS |
| final_evidence_recall | 0.8810 | ≥ 0.90 | **FAIL** |
| critical_final_evidence_recall | 0.8912 | = 1.00 | **FAIL** |
| intent_accuracy | 0.9831 | ≥ 0.90 | PASS |
| per_intent_gold_recall_at_10 | 0.9583 (min) | ≥ 0.75 | PASS |
| per_intent_intent_accuracy | 0.9286 (min) | ≥ 0.80 | PASS |
| expected_status_accuracy | 1.0 | ≥ 0.975 | PASS |
| citation_integrity | 1.0 | = 1.00 | PASS |
| wrong_version_evidence_count | 0 | = 0 | PASS |
| forbidden_evidence_count | 0 | = 0 | PASS |
| required_source_coverage_answered | 0.9592 | ≥ 0.97 | **FAIL** |
| identifier_hallucination_rate | 0.0 | < 0.03 | PASS |
| paper_code_dual_source_rate | 0.0 | = 1.00 | **FAIL** |
| answer_point_coverage | 0.9463 | ≥ 0.90 | PASS |
| critical_answer_point_miss_count | 4 | = 0 | **FAIL** |
| contradiction_count | 0 | = 0 | PASS |
| major_unsupported_claim_count | 1 | = 0 | **FAIL** |
| unhandled_exception_count | 0 | = 0 | PASS |

```text
failed_gate_count = 6
incomplete_gate_count = 0
release_score = 0.9463276836158192 (attempt-1: 0.8277)
```

Six preregistered mandatory gates fail → Stage A1 fail-fast: **no ablation, no novel_dev,
no novel_validation, no composer audit**. Per the no-pass-chasing contract, no repair was
performed; the verdict is frozen.

## 4. Attempt-1 comparison (diagnostic only; gates unchanged)

| metric | attempt 1 | attempt 2 | delta |
| ------ | --------- | --------- | ----- |
| expected_status_accuracy | 0.8644 | **1.0000** | +0.1356 |
| release_score | 0.8277 | **0.9463** | +0.1186 |
| answer_point_coverage | 0.8446 | 0.9463 | +0.1017 (now PASS) |
| contradiction_count | 4 | **0** | −4 (now PASS) |
| critical_answer_point_miss_count | 18 | 4 | −14 (still FAIL) |
| final_evidence_recall | 0.8129 | 0.8810 | +0.0681 (still FAIL) |
| critical_final_evidence_recall | 0.8231 | 0.8912 | +0.0681 (still FAIL) |
| required_source_coverage_answered | 0.9388 | 0.9592 | +0.0204 (still FAIL) |
| paper_code_dual_source_rate | 0.0 | 0.0 | unchanged FAIL |
| major_unsupported_claim_count | 1 | 1 | unchanged FAIL |
| failed gates | 9 | 6 | −3 |

**Eight FR1-reviewed exposed cases — exact attempt-2 outcomes (all match Gold):**

- g005 answered, g013 answered, g027 answered, g034 answered, g059 answered,
  g060 answered (attempt-1: all six falsely refused);
- g012 version_conflict, g026 version_conflict (attempt-1: insufficient_evidence /
  answered respectively).

The FR1 root causes (RC1 false refusals, RC2 version-conflict detection) are repaired in
production behavior. The remaining FAIL classes are different, deeper quality deficits:

- g001/g005/g013/g022 each miss one critical answer point; g005 answers correctly but
  with a different (evidence-supported) procedural route than the Gold answer points
  (coverage 0.0 on those points);
- g016/g060 miss required-source coverage; g060's evidence set contains no paper source
  (required: paper+code), keeping dual-source at 0.0;
- g113 makes one unsupported causal-diagnosis claim
  (`claim_3_efficiency_empty_bin_diagnosis`);
- final/critical evidence recall remain below threshold (0.88/0.89 vs 0.90/1.00).

## 5. Scientific usage (attempt 2, exact)

```text
Stage A1 Gold formal:        376 calls / 3,313,651 tokens
  runtime (gen+verifier+composer+embedding): 314 calls / 2,903,448 tokens
  evaluation judge:                           62 calls /   410,203 tokens
Stages A2/A3/A4/A5:          not reached → 0 calls / 0 tokens
Attempt-2 total:             376 calls / 3,313,651 tokens
```

Attempt-1 historical usage is reported separately and not merged (formal 383 calls /
3,348,432 tokens; superseded 9/120 plan 61 calls / 339,150 tokens).

## 6. Protected cohorts

```text
novel_validation = PRISTINE_FOR_CURRENT_LINEAGE (A4 not reached; exposure transition = none)
holdout access = 0
protected-content leakage = 0
F6-B execution = 0
```

## 7. Lifecycle result

```text
F6-A attempt 2 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED
F6-A attempt 1 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (historical, unchanged)
F6-B = LOCKED / F6_A_DID_NOT_PASS
Phase F = IN_PROGRESS / F6_A_ATTEMPT_2_FAILED
```

## 8. Next action

```text
NEXT_TASK_RECOMMENDATION =
POST-ATTEMPT-2 EXPOSED-GOLD FAILURE REVIEW / NEW CANDIDATE DEVELOPMENT
(targeting the residual evidence-recall, source-coverage/dual-source,
critical-answer-point, and unsupported-claim deficit classes)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
