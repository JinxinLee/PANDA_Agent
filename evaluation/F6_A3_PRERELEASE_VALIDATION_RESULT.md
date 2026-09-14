# F6-A Attempt 3 — Prerelease Validation & Generalization Gate (Terminal Result)

## 1. Verdict

**F6-A Attempt 3 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED**

A1 Gold primary execution failed four mandatory preregistered release gates:
1. `critical_final_evidence_recall`: 0.9410 vs threshold 1.00 (misses: `g011`, `g022`, `g044`, `g060`)
2. `critical_answer_point_miss_count`: 3 vs threshold 0 (misses: `g022` [p2], `g023` [p3], `g115` [p3])
3. `paper_code_dual_source_rate`: 0.0 vs threshold 1.00 (`g060` answered without cited paper evidence)
4. `unhandled_exception_count`: 1 vs threshold 0 (`g013` failed with Vertex 429 `RESOURCE_EXHAUSTED`)

Per the preregistered fail-fast contract, scientific execution stopped immediately upon observing mandatory gate failure.
- A1 cohort status: **INCOMPLETE** (58 scored / 59 expected).
- Release score: **0.9741** (58-case diagnostic only; full-cohort release score is **INCOMPLETE**).
- `g013` was not rerun because hard failures were already measured on the evaluated cohort and scientific execution was halted.
- Protocol deviation: late receipt creation occurred after failure case inspection (explicitly declared; no pre-diagnosis compliance claimed).
- Stages A2–A5: **NOT_REACHED**.
- `novel_validation` remains **PRISTINE_FOR_CURRENT_LINEAGE**.
- Protected holdout access = 0; F6-B execution = 0.

---

## 2. Starting State

- **Starting repository HEAD**: `1f03bbdc9da72af0bf90fe0cd15d5c061bffd567` ("Reconcile Gold-9 release authority bindings")
- **Product-behavior lineage HEAD**: `d323f790655c62e18b782d606a02f593a673f3cd` ("Repair FR2 source obligation boundaries")
- **Product-behavior drift**: None. Working tree was clean prior to preregistration and candidate freeze; all diffs since `d323f79` represent evaluation and release authority infrastructure reconciliation.

---

## 3. A0 Preflight

- **Authority resolution**:
  - Gold authority: `m6-benchmark-v2.9` (`evaluation/benchmarks/v2_9/gold_questions.yaml`, SHA-256 `eaacd3ed6595821b24b28823c6344abc4dfb954eb71846e682080b42c2f689be`, manifest status `approved_exposed_development_benchmark_v2_9`, `official_ready = true`, `structurally_valid = true`).
  - Product-language calibration: `phase_b_t3_product_language_scope_v6` (SHA-256 `fe56d4ca1112194643054d0d7627804956b4a35965495e18cbede59a937854a9`, compatible with Gold v2.9).
  - Derived formal-English selector: 59 IDs, SHA-256 `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5`.
  - Production answer mode: `legacy_question_core`.
- **Runtime and corpus environment**:
  - Docker containers: `postgres:17-alpine` (healthy), `qdrant:v1.15.5` (healthy).
  - Corpus index fingerprint: `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`.
  - Models: generation = `gemini-3.8-flash`, verification-effective = `gemini-3.8-flash`, judge = `gemini-3.8-flash`, embedding = `gemini-embedding-2`.
  - Prompts: version 3.10.1, hash `23d73b036646ec62f3095fac4bdfafdfc7ecf6676fd27d18475b86773db4e6d5`.
- **Preflight verdict**: PASS (0 scientific calls, 0 scientific tokens).
  - Focused non-scientific tests: 327 passed + 70 subtests recorded as inherited prior execution evidence from user resume summary / preflight chain, not rerun as current fresh verification.
  - Historical preflight HOLD report: preserved in repository history at `50f0c4b:evaluation/F6_A3_PRERELEASE_VALIDATION_RESULT.md` (unblocked by GOLD-9 commit `1f03bbd`).

---

## 4. Preregistration and Candidate Freeze

- **Preregistration commit**: `2f9a4a32a41330326976bce4cf29e726ceac908e` ("Preregister F6-A attempt 3")
- **Preregistration artifacts**:
  - `evaluation/F6_A3_PRERELEASE_VALIDATION_PREREGISTRATION.md`
  - `evaluation/f6_a3_prerelease_validation_preregistration.json` (SHA-256 `6ef37ca8d248eacb8376950cf8a59cb38bcacb683e04a94758c4a02a9f656e5d`)
- **Candidate freeze commit**: `11de2bd6b0a26176d252400c99a262b42b2a4a0d` ("Freeze F6-A attempt 3 candidate")
- **Candidate ID**: `f6a-rc3-20260914`
- **Candidate manifest SHA-256**: `be2101a4709aa2ab2f324ba00b58d90e561ff1e359fc44b28ab26a5b3be155ca`
- **Freeze receipt**: `evaluation/f6_a3_freeze_receipt.json`
- **Candidate verification**: `valid = true, mismatches = []`

---

## 5. A1 Gold Primary Evaluation

- **Run ID**: `f6a-rc3-gold-formal-full-20260914`
- **Cohort**: 59 formal-English dev cases (Gold v2.9 + calibration v6)
- **Cohort execution status**: **INCOMPLETE**
  - Expected cases: 59
  - Scored cases: 58
  - Incomplete cases: 1 (`g013` failed with Vertex 429 `RESOURCE_EXHAUSTED` exception)
- **Recovery and execution chronology**:
  - Initial pass wrote 59 records: 56 successes, 3 Vertex 429 exceptions (`g006`, `g013`, `g016`), backed up to `results.jsonl.pre-retry-backup`.
  - Pause note recorded in commit `50f0c4b` (`evaluation/F6_A3_EXECUTION_PAUSE_AND_RESUME_NOTE.md`).
  - Path R-A resume executed under temporary detached HEAD `11de2bd` because only `repository_identity.commit` changed from the pause commit, with `main` restored to `50f0c4b`.
  - Retry recovered `g006` and `g016`; `g013` remained an unhandled 429 exception. No further retry was performed as mandatory gates had already failed.
- **Mandatory release gate summary**:
  - Total gates evaluated: 18
  - Passed: 14 (diagnostic on available observations; not complete-cohort PASS)
  - **Failed: 4** (terminal failure for release gate)
  - Incomplete: 0 flags in raw canonical matrix (evaluated strictly on available observations: 58 scored cases, plus exception gate on 59; full-cohort measurements remain INCOMPLETE due to unmeasured `g013`). Note: missing measurements are treated as INCOMPLETE, not FAIL. Hard measured FAIL is terminal and missing `g013` status is INCOMPLETE separately.

| Gate Name | Observed Value | Threshold | Status | Denominator | Failing Cases |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `gold_recall_at_10` | 0.9792 | >= 0.95 | **PASS** | 48 | — |
| `final_evidence_recall` | 0.9306 | >= 0.90 | **PASS** | 48 | — |
| `critical_final_evidence_recall` | 0.9410 | == 1.00 | **FAIL** | 48 | `g011`, `g022`, `g044`, `g060` |
| `intent_accuracy` | 0.9828 | >= 0.90 | **PASS** | 58 | — |
| `per_intent_gold_recall_at_10` | min 0.9500 | >= 0.75 | **PASS** | all intents | — |
| `per_intent_intent_accuracy` | min 0.9231 | >= 0.80 | **PASS** | all intents | — |
| `expected_status_accuracy` | 1.0000 | >= 0.975 | **PASS** | 58 | — |
| `citation_integrity` | 1.0000 | == 1.00 | **PASS** | 58 | — |
| `wrong_version_evidence_count` | 0 | == 0 | **PASS** | 58 | — |
| `forbidden_evidence_count` | 0 | == 0 | **PASS** | 58 | — |
| `required_source_coverage_answered` | 0.9792 | >= 0.97 | **PASS** | 48 | — |
| `identifier_hallucination_rate` | 0.0000 | < 0.03 | **PASS** | 177 | — |
| `paper_code_dual_source_rate` | 0.0000 | == 1.00 | **FAIL** | 1 | `g060` |
| `answer_point_coverage` | 0.9741 | >= 0.90 | **PASS** | 58 | — |
| `critical_answer_point_miss_count` | 3 | == 0 | **FAIL** | 58 | `g022`, `g023`, `g115` |
| `contradiction_count` | 0 | == 0 | **PASS** | 58 | — |
| `major_unsupported_claim_count` | 0 | == 0 | **PASS** | 58 | — |
| `unhandled_exception_count` | 1 | == 0 | **FAIL** | 59 | `g013` |

- **Per-intent breakdown**:
  - `algorithm_implementation` (2 cases): gold_recall@10 = 1.0, intent_acc = 1.0, final_ev_recall = 0.8333
  - `algorithm_theory` (8 cases): gold_recall@10 = 1.0, intent_acc = 1.0, final_ev_recall = 0.8333
  - `api` (15 cases): gold_recall@10 = 1.0, intent_acc = 1.0, final_ev_recall = 1.0
  - `installation` (12 cases): gold_recall@10 = 0.95, intent_acc = 1.0, final_ev_recall = 0.90
  - `module_structure` (2 cases): gold_recall@10 = 1.0, intent_acc = 1.0, final_ev_recall = 1.0
  - `troubleshooting` (6 cases): gold_recall@10 = 1.0, intent_acc = 1.0, final_ev_recall = 1.0
  - `usage` (13 cases): gold_recall@10 = 0.9545, intent_acc = 0.9231, final_ev_recall = 0.9091
- **Release score**:
  - 58 scored cases: **0.9741** (diagnostic only)
  - Full 59-case cohort: **INCOMPLETE**

---

## 6. A2 Ablation

**NOT_REACHED** (fail-fast triggered by Stage A1 mandatory gate failures; zero scientific calls).

---

## 7. A3 novel_dev

**NOT_REACHED** (fail-fast triggered by Stage A1 mandatory gate failures; zero scientific calls).

---

## 8. A4 novel_validation

**NOT_REACHED** (fail-fast triggered by Stage A1 mandatory gate failures; zero scientific calls).

- **Cohort exposure state**:
  `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`
  Zero calls, zero token consumption, zero exposures.

---

## 9. A5 Composer Empirical Audit

**NOT_REACHED** (fail-fast triggered by Stage A1 mandatory gate failures; zero scientific calls).

---

## 10. Attempt-2 Diagnostic Comparison

- **Methodological caution**: Direct aggregate comparison is benchmark-confounded. Attempt 2 evaluated **Gold v2.6** (59 cases, release score 0.9463, 6 failed gates); Attempt 3 evaluated **Gold v2.9** (59 cases, 58 scored, release score diagnostic 0.9741, 4 failed gates).
- **Gate comparison**:
  - `failed_gate_count`: Attempt 2 = 6, Attempt 3 = 4.
  - `expected_status_accuracy`: 1.0000 in both attempts.
  - `unhandled_exception_count`: Attempt 2 = 0, Attempt 3 = 1 (`g013`).
  - `paper_code_dual_source_rate`: Attempt 2 = 0.0 (`g060`), Attempt 3 = 0.0 (`g060`).
  - `critical_answer_point_miss_count`: Attempt 2 = 4 (`g001`, `g005`, `g013`, `g022`), Attempt 3 = 3 (`g022`, `g023`, `g115`).
  - `major_unsupported_claim_count`: Attempt 2 = 1 (`g113`), Attempt 3 = 0.

---

## 11. Scientific Usage

- **Accounting basis**: Exact sum of FINAL 59 records + ONLY ORIGINAL 3 failed attempts from `results.jsonl.pre-retry-backup` (`g006`, `g013`, `g016`). The 56 initial successful runs are not double-counted.
- **Attempt 3 grand total**:
  - Total model calls: **397**
  - Total token usage: **3,783,197**
- **Sub-run components**:
  - Final 59 records: 387 calls / 3,745,918 tokens
  - Initial 3 failed attempts: 10 calls / 37,279 tokens
- **Role breakdown**:
  - **Runtime**: 336 calls / 3,367,021 tokens
    - Generation calls: 271
    - Embedding calls: 65
    - QA generation labeled: 89 calls / 2,007,383 tokens
    - QA composer labeled: 41 calls / 79,801 tokens
    - Runtime verification: `NOT_SEPARATELY_RECOVERABLE_FROM_STORED_RECORDS`
  - **Evaluation judge**: 61 calls / 416,176 tokens (61 generation calls, 0 embedding calls)

---

## 12. Integrity Receipts and Hashes

- **Candidate manifest SHA-256**: `be2101a4709aa2ab2f324ba00b58d90e561ff1e359fc44b28ab26a5b3be155ca`
- **Case ID set (59 IDs) SHA-256**: `914ee1b4b3f937e6839416932b44de06fb0401589fd59825a63ac430c5361d1c`
- **Results file (`results.jsonl`) SHA-256**: `360f6c349f464bee2fb38a3d0da2ef4fa8a6de8200c15fe2975ad811b5ac8263`
- **Gate matrix (`gate_matrix.json`) SHA-256**: `d40636195b0a307fe19b3884a5618f1096960e6400bd63a7fb2e2d3f47ca5398`
- **Combined traces SHA-256 (58 trace files)**: `e764d24547eb5588f59d66da4091f584821a82772f5c5c9de933c3ba10365e27`
- **Retrieval traces (`retrieval_traces.jsonl`) SHA-256**: `d8f32ef0da4f91df9598b50f6ac9a78d19dab41dc6f336503d66675ef50836f5`
- **Committed receipts**:
  - Freeze receipt: `evaluation/f6_a3_freeze_receipt.json`
  - Late A1 run receipt: `evaluation/f6_a3_a1_receipt.json`
  - Committed gate matrix: `evaluation/f6_a3_gate_matrix.json` (local copy matches run bytes; Git normalizes CRLF to LF, preserving JSON content)
- **Git storage identity**: gate matrix Git blob SHA-256 `ddd776042ae5c89f863a25bd34b5d65c488fc21ea790ccb0e730fa8680d7185c`; local/run byte SHA-256 remains `d40636195b0a307fe19b3884a5618f1096960e6400bd63a7fb2e2d3f47ca5398`. The JSON content is identical; the receipt binds original run bytes. See the closeout verification addendum.
- **Protocol timing deviation**: A1 receipt was written after failure case diagnosis was already extracted by a previous worker; receipt is explicitly marked as late without claim of pre-diagnosis sequencing.

---

## 13. Protected Holdout

- **Holdout access**: 0
- **Protected-content leakage**: 0
- **F6-B execution**: 0

---

## 14. Lifecycle

- **F6-A Attempt 1**: `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED` (historical, Gold v2.6)
- **F6-A Attempt 2**: `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED` (historical, Gold v2.6)
- **F6-A Attempt 3 preflight**: `HISTORICAL / HOLD / PRE_RELEASE_PRECONDITION_NOT_MET` (historical, zero scientific calls, unblocked by GOLD-9)
- **GOLD-9 reconciliation**: `COMPLETE / PASS / RELEASE_AUTHORITY_CHAIN_RECONCILED` (commit `1f03bbd`)
- **F6-A Attempt 3**: `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED` (current terminal outcome, Gold v2.9)
- **F6-B**: `LOCKED / F6_A_DID_NOT_PASS`
- **Phase F**: `IN_PROGRESS / F6_A_ATTEMPT_3_FAILED`

---

## 15. Commits and Artifacts

- **Pre-closeout HEAD**: `50f0c4b034d8508b88376cd9419b8ea252ef62cd` (pre-closeout parent; final commit will be created by host)
- **Key artifacts**:
  - `evaluation/f6_a3_a1_receipt.json`
  - `evaluation/f6_a3_gate_matrix.json`
  - `evaluation/f6_a3_prerelease_validation_result.json`
  - `evaluation/F6_A3_PRERELEASE_VALIDATION_RESULT.md`
  - `evaluation/f6_a3_closeout_verification.json`
  - `docs/EVALUATION_STATUS.md`
  - `docs/GENERALIZATION_ROADMAP.md`
- **Git push status**: No push performed.

---

## 16. Next Recommendation

```text
NEXT_TASK_RECOMMENDATION =
POST-ATTEMPT-3 READ-ONLY FAILURE AND RECOVERY-PROTOCOL REVIEW FIRST
(read-only failure and recovery-protocol review first, requiring separate authorization; do not attempt question-specific fixes or product source repairs now)

NEXT_TASK_EXECUTION_AUTHORIZED = false
```
