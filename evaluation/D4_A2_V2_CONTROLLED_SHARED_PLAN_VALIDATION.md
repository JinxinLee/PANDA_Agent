# PANDA Agent — D4-A2-V2: Controlled Shared-Plan Validation Report

## 1. Executive Decision & Scientific Verdict

```text
D4_A2_V2_DECISION = FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
D4-A2-V2 = COMPLETE / FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
STAGE = D4-A2-V2 — Controlled Shared-Plan T2 Before/After Validation
LIFECYCLE_STATUS = COMPLETE / FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
VERDICT_LEVEL = 3
VERDICT = FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
VERDICT_REASON = Primary target replacement or fixed locator dependency removal not reproduced: 2/2 targets reproduced under AFTER with valid governed witness, 0/2 dependencies removed.

EXECUTION_VALID = true
BEFORE_REFERENCE_VALID = true
TARGET_REPLACEMENT_REPRODUCED = 2 / 2
BATCH1_DEPENDENCY_REMOVED = 0 / 2

CRITICAL_TREATMENT_REGRESSIONS = 0
NONCRITICAL_REGRESSIONS = 0
GROUNDING_REGRESSIONS = 0
WRONG_VERSION_REGRESSIONS = 0
INVALID_PROVENANCE_RECOVERIES = 0

FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED
PRODUCTION_ACTIVATION = false
D4-A3_STATUS = NOT_STARTED / BLOCKED
```

The deterministic offline evaluation of **D4-A2-V2 — Controlled Shared-Plan T2 Before/After Validation** has completed over the frozen, immutable raw results.

Key findings:
1. **Target Replacement Reproduced (2 / 2):** Under the `AFTER_BATCH1_REPLACEMENT` arm, both primary migration targets were retained with valid governed structured admission witnesses:
   - `g036.e1` (`macro/target/ana_dpm.C`): `BEFORE = True`, `AFTER = True`; witness `object.5cae2ceab6e67bb4c9065331` (origin `edge.2e09628416a01ce2461d752a`, relation_edge from `restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42`, selected by selectivity v2, pool position 3, retained in final evidence).
   - `g021.e1` (`macro/target/prod_sim_hvmaps.C`): `BEFORE = True`, `AFTER = True`; witness `object.3ab0a90ae68e8ece071a9f22` (origin `edge.ea3a79d222f0ca6cc0e6df72`, relation_edge from `restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42`, selected by selectivity v2, pool position 5, retained in final evidence).
2. **Fixed Locator Dependency Removal Not Witnessed (0 / 2):** Under the prospectively acquired shared plans for `g036` and `g021`, the query expansion mechanisms in `BEFORE_COMPAT` did not actively activate the exact masked fixed locators (`fixed_locator_inputs_active_before = false`). Consequently, the dependency removal receipt evaluated to `0 / 2`.
3. **Reference Baseline Valid:** Both primary targets were retained under the fresh shared-plan `BEFORE_COMPAT` baseline (`before_reference_valid = true`).
4. **Zero Shared-Plan Critical Treatment Regressions (0):** Holding the canonical RetrievalPlans fixed across paired arms completely eliminated the critical regressions previously observed in unconstrained D4-A2 (`n022.e2` and `g021.e2`). Zero treatment regressions occurred (`PAIR_TREATMENT_REGRESSION = 0`, `FINAL_TREATMENT_REGRESSION = 0`).
5. **Zero Tolerance Regressions:** All six primary retrieval metric deltas equal `0.000000`, satisfying bounded tolerance thresholds. MRR delta was `-0.025641` (diagnostic only).
6. **Safety Gates Satisfied:** Zero grounding regressions, zero wrong-version regressions, and zero invalid provenance recoveries.
7. **Scientific Precedence & Verdict:** Under frozen Section 17 verdict precedence, Level 1 (INVALID) and Level 2 (INCONCLUSIVE) pass, but Level 3 (**`FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED`**) triggers because `batch1_dependency_removed` equals 0 / 2.
8. **Lifecycle Impact:** First-batch runtime migration is **BLOCKED**. `PRODUCTION_ACTIVATION` remains **`false`**. D4-A3 remains **`NOT_STARTED / BLOCKED`**.

---

## 2. Background, Motivation & Shared-Plan Scientific Design

### 2.1 Why D4-A2-V2 was Necessary
In the original unconstrained **D4-A2** experiment (2026-09-02), two critical evidence-group regressions were observed: `n022.e2` and `g021.e2`. Subsequent investigations established that:
- For `g021.e2`, the evidence group represented noncritical supporting code rather than required critical evidence; this benchmark contract was corrected forward in **D4-A2-R1**.
- For `n022.e2`, deterministic layer-by-layer divergence analysis (D4-A2-R1) and focused paired replays (**D4-A2-V1** and **D4-A2-V1-R1**) demonstrated that the loss was driven by run-to-run Query Analyzer sampling variability (omitting the concepts "worker step" and "fitted vertex" in the AFTER draw, dropping the target from exact-channel recall) rather than a causal regression caused by Batch-1 replacement. In D4-A2-V1-R1, holding the historical BEFORE plan fixed across arms yielded `T/T` (preserved), while holding the AFTER plan fixed yielded `F/F` (unresolved both), confirming `T/T vs F/F` clean factorial separation.

To formally evaluate the true causal treatment effect of Batch-1 fixed-locator replacement without confounding analyzer variability, **D4-A2-V2** was designed as a controlled, shared-plan T2 validation.

### 2.2 Shared-Plan Two-Phase Protocol
1. **Phase P (Prospective Plan Acquisition):** A single Query Analyzer run is performed prospectively for each case in the frozen 16-case cohort to produce a canonical `RetrievalPlan`. The 16 canonical plans are frozen and committed into Git before any Phase R retrieval execution.
2. **Phase R (Paired Downstream Retrieval):** Each frozen canonical plan is executed across both arms:
   - `BEFORE_COMPAT`: Production query expansions active with all Batch-1 fixed locators present; generic structured replacement OFF; admission budget K = 0.
   - `AFTER_BATCH1_REPLACEMENT`: Batch-1 fixed locators suppressed via in-memory component mask; generic governed D3.5 structured replacement ON with deterministic selectivity v2 (caps 8/4); K = 3 bounded rerank admission; rerank pool size = 30.
   Both arms execute downstream retrieval against the identical, immutable plan (`plan_equality_verified = true`).

### 2.3 Upstream Commit Lineage & Frozen Artifact Authority
The scientific audit boundary was strictly preserved across the following commits:
- **Implementation Freeze Commit:** `afc93327ff7f6de6c0b49dd905347696cfaad27a` (*D4-A2-V2 repair pre-exposure freeze guards*)
- **Prospective Plan Freeze Commit:** `537836244d44d9e5c10472df019f5fac1c9070a1` (*D4-A2-V2 freeze prospective shared plans*)
  - Raw plans Git blob: `ee7c1c011463973557ef423178d7c241bf3821d4` (`evaluation/d4_a2_v2_raw_plans.json`, 16 canonical plans).
- **R2 Plan-Verification Repair Commit:** `8ef69a99d6389c47d7c2f09f7b9ff7d04aee548d` (*D4-A2-V2-R2 repair frozen plan verification*)
  - Repaired verification logic without mutating any frozen plans.
- **Raw Retrieval Freeze Commit:** `b1a9f12366e328263e000f7b4c89184f2854c77a` (*D4-A2-V2 freeze paired raw retrieval results*)
  - Raw results Git blob: `2d894ff2d0ac8a49239663df155478614a99bae0` (`evaluation/d4_a2_v2_raw_results.json`, 32 retrieval cells).
- **Evaluator Implementation Freeze Commit:** `6c12af68ee17615a66a732108cb5b895f86853b7` (*D4-A2-V2 freeze deterministic evaluator*)
  - Froze deterministic offline evaluator and 94 focused unit tests before formal evaluation.
- **Final Scientific Closeout Commit:** *D4-A2-V2 close controlled shared-plan validation* (direct child of `6c12af68ee17615a66a732108cb5b895f86853b7`).

---

## 3. Protocol Validity & Execution Accounting

### 3.1 Protocol Validity
- `execution_valid`: **`true`**
- `protocol_violation`: **`false`**
- `slots_total`: **32** (16 cases × 2 arms)
- `plan_equality_all_verified`: **`true`** (all 32 cells used exact frozen canonical plan)
- `before_reference_valid`: **`true`** (`g036.e1` and `g021.e1` both reproduced under `BEFORE_COMPAT`)

### 3.2 Applicability Accounting
Applicability is determined strictly by case ID and preregistered cohort membership, not by raw display strings:
- **Total Cohort Cases:** 16
- **Formally Applicable Answered Cases:** 13
  - Gold answered (7): `g029`, `g036`, `g020`, `g060`, `g052`, `g055`, `g021`
  - Novel Dev answered (6): `n021`, `n022`, `n006`, `n014`, `n003`, `n004`
- **Negative Controls (3):** `g025`, `g041`, `g007` (insufficient evidence; participating in negative control evidence accounting and safety checks, excluded from answered retrieval metric denominators)
  - `g025`: BEFORE final evidence count = 12, AFTER final evidence count = 12
  - `g041`: BEFORE final evidence count = 11, AFTER final evidence count = 11
  - `g007`: BEFORE final evidence count = 12, AFTER final evidence count = 12

### 3.3 Zero-Provider Evaluation Accounting
The evaluator ran purely offline and deterministically over frozen artifacts with zero provider invocations:
- `ANALYZER_CALLS`: 0
- `EMBEDDING_CALLS`: 0
- `RERANKER_CALLS`: 0
- `QA_CALLS`: 0
- `VERIFIER_CALLS`: 0
- `JUDGE_CALLS`: 0
- `POSTGRESQL_WRITES`: 0
- `QDRANT_WRITES`: 0
- `INGESTION_RUNS`: 0
- `REINDEX_RUNS`: 0
- `NOVEL_VALIDATION_RUNS`: 0
- `NOVEL_HOLDOUT_RUNS`: 0
- `PROTECTED_DATASET_ACCESS`: 0

---

## 4. Paired Evidence Outcomes & Phenotype Accounting

Across all 16 cases and 27 required evidence groups:

### 4.1 Phenotype Counts
- **Pre-rerank Pool Classification:**
  - `PAIR_PRESERVED` (BEFORE=True, AFTER=True): **22**
  - `PAIR_TREATMENT_RECOVERY` (BEFORE=False, AFTER=True): **0**
  - `PAIR_TREATMENT_REGRESSION` (BEFORE=True, AFTER=False): **0**
  - `PAIR_UNRESOLVED_BOTH` (BEFORE=False, AFTER=False): **5**
- **Final Evidence Classification:**
  - `FINAL_PRESERVED` (BEFORE=True, AFTER=True): **22**
  - `FINAL_TREATMENT_RECOVERY` (BEFORE=False, AFTER=True): **0**
  - `FINAL_TREATMENT_REGRESSION` (BEFORE=True, AFTER=False): **0**
  - `FINAL_UNRESOLVED_BOTH` (BEFORE=False, AFTER=False): **5**

### 4.2 Unresolved-Both Analysis
All 5 unresolved-both evidence groups reside entirely in `novel_dev`:
1. `n021.e2` (role `pandaroot_lmd_implementation_ownership`)
2. `n022.e1` (role `pass1_artifact_production`)
3. `n006.e2` (role `filename_suffix_literals`)
4. `n014.e1` (role `vendored_framework_status`)
5. `n003.e2` (role `per_event_step_advancement`)

Under the frozen contract: **F/F is not a treatment regression**. These 5 groups represent shared baseline omissions under the canonical plan rather than treatment-induced losses. In contrast, 100% of Gold evidence groups (13/13 across answered and negative control cases) were `FINAL_PRESERVED`.

---

## 5. Primary Target Witnesses & Replacement Reproduction

### 5.1 Witness Audit for Primary Migration Targets

#### Target 1: `g036.e1` (`macro/target/ana_dpm.C`)
- **BEFORE Retention:** `True` (pool: True, final: True)
- **AFTER Retention:** `True` (pool: True, final: True)
- **Fixed-Locator Input Suppressed under AFTER:** `True`
- **Governed Structured Replacement Witness:**
  - Candidate Object ID: `object.5cae2ceab6e67bb4c9065331`
  - Provenance Origin: `edge.2e09628416a01ce2461d752a` (relation_edge)
  - Source ID: `restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42`
  - Locator Path: `macro/target/ana_dpm.C` (lines 1–938)
  - Selected by Selectivity v2: `True`
  - Rerank Pool Membership: `True` (position 3, ordinary top30 before reservation)
  - Competed in Reranker: `True`
  - Retained in Final Evidence: `True`
  - Valid Governed Witness: `True`
- **Reproduction Verdict:** `reproduced = true`
- **Dependency Removal:** `dependency_removed = false` (`fixed_locator_inputs_active_before = false`)

#### Target 2: `g021.e1` (`macro/target/prod_sim_hvmaps.C`)
- **BEFORE Retention:** `True` (pool: True, final: True)
- **AFTER Retention:** `True` (pool: True, final: True)
- **Fixed-Locator Input Suppressed under AFTER:** `True`
- **Governed Structured Replacement Witness:**
  - Candidate Object ID: `object.3ab0a90ae68e8ece071a9f22`
  - Provenance Origin: `edge.ea3a79d222f0ca6cc0e6df72` (relation_edge)
  - Source ID: `restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42`
  - Locator Path: `macro/target/prod_sim_hvmaps.C` (lines 1–203)
  - Selected by Selectivity v2: `True`
  - Rerank Pool Membership: `True` (position 5, ordinary top30 before reservation)
  - Competed in Reranker: `True`
  - Retained in Final Evidence: `True`
  - Valid Governed Witness: `True`
- **Reproduction Verdict:** `reproduced = true`
- **Dependency Removal:** `dependency_removed = false` (`fixed_locator_inputs_active_before = false`)

### 5.2 Summary of Target Metrics
- `target_replacement_reproduced`: **`2 / 2`**
- `batch1_dependency_removed`: **`0 / 2`**

---

## 6. First-Divergence Attribution

For all 27 evidence groups across the 16 cases:
- `NO_DIVERGENCE`: **24**
- `FIXED_LOCATOR_SUPPRESSION`: **0**
- `ORDINARY_CHANNEL_RECALL`: **0**
- `STRUCTURED_GENERATION`: **1** (`n022.e1` — bridge candidates generated under AFTER; group is F/F unresolved in both arms)
- `SELECTIVITY`: **1** (`g055.e1` — selective candidate pruning occurred; group is T/T preserved)
- `K3_ADMISSION`: **1** (`g020.e1` — candidate reservation exercised; group is T/T preserved)
- `FUSION_CUTOFF`: **0**
- `RERANKER`: **0**
- `FINAL_SELECTION`: **0**

Crucially, zero evidence groups experienced treatment-induced divergence leading to regression. The single candidate-admission differences in `g020.e1` and `g055.e1` resulted in final evidence retention in both arms.

---

## 7. Quantitative Retrieval Metrics

### 7.1 Primary Metrics Table (13 Answered Cases)

| Metric | BEFORE_COMPAT | AFTER_BATCH1_REPLACEMENT | Delta | Threshold | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Recall@5** | 0.769231 (10.0/13) | 0.769231 (10.0/13) | +0.000000 | delta >= -0.05 | **PASS** |
| **Recall@10** | 0.820513 (10.67/13) | 0.820513 (10.67/13) | +0.000000 | delta >= -0.05 | **PASS** |
| **Recall@20** | 0.820513 (10.67/13) | 0.820513 (10.67/13) | +0.000000 | delta >= -0.05 | **PASS** |
| **combined_candidate_recall** | 0.897436 (11.67/13) | 0.897436 (11.67/13) | +0.000000 | delta >= -0.05 | **PASS** |
| **final_evidence_recall** | 0.820513 (10.67/13) | 0.820513 (10.67/13) | +0.000000 | delta >= -0.05 | **PASS** |
| **critical_final_evidence_recall**| 0.820513 (10.67/13) | 0.820513 (10.67/13) | +0.000000 | delta >= 0.00 | **PASS** |
| *MRR (diagnostic)* | 0.707692 | 0.682051 | -0.025641 | diagnostic only | N/A |

### 7.2 Subset Diagnostics

#### Gold Answered Cohort (7 Cases)
- **Recall@5:** BEFORE 0.904762, AFTER 0.904762, Delta +0.000000
- **Recall@10:** BEFORE 1.000000, AFTER 1.000000, Delta +0.000000
- **Recall@20:** BEFORE 1.000000, AFTER 1.000000, Delta +0.000000
- **combined_candidate_recall:** BEFORE 1.000000, AFTER 1.000000, Delta +0.000000
- **final_evidence_recall:** BEFORE 1.000000, AFTER 1.000000, Delta +0.000000
- **critical_final_evidence_recall:** BEFORE 1.000000, AFTER 1.000000, Delta +0.000000
- *MRR (diagnostic):* BEFORE 0.714286, AFTER 0.690476, Delta -0.023810

#### Novel Dev Answered Cohort (6 Cases)
- **Recall@5:** BEFORE 0.611111, AFTER 0.611111, Delta +0.000000
- **Recall@10:** BEFORE 0.611111, AFTER 0.611111, Delta +0.000000
- **Recall@20:** BEFORE 0.611111, AFTER 0.611111, Delta +0.000000
- **combined_candidate_recall:** BEFORE 0.777778, AFTER 0.777778, Delta +0.000000
- **final_evidence_recall:** BEFORE 0.611111, AFTER 0.611111, Delta +0.000000
- **critical_final_evidence_recall:** BEFORE 0.611111, AFTER 0.611111, Delta +0.000000
- *MRR (diagnostic):* BEFORE 0.700000, AFTER 0.672222, Delta -0.027778

---

## 8. Scientific Verdict & Precedence Analysis

The deterministic evaluator evaluated the six-level frozen precedence ladder:

```text
Level 1: INVALID / PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED
         Condition: execution_valid == False or protocol_violation == True
         Result: PASS (execution_valid=True, protocol_violation=False)

Level 2: INCONCLUSIVE / BEFORE_REFERENCE_NOT_REPRODUCED
         Condition: before_reference_valid == False
         Result: PASS (before_reference_valid=True)

Level 3: FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
         Condition: target_replacement_reproduced < 2 or batch1_dependency_removed < 2
         Observation: target_replacement_reproduced = 2, batch1_dependency_removed = 0
         Result: TRIGGERED -> FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED

Level 4: FAIL / SHARED_PLAN_CRITICAL_TREATMENT_REGRESSION
         (Not evaluated due to Level 3 precedence; shared_plan_critical_regressions = 0)

Level 5: PARTIAL / AGGREGATE_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE
         (Not evaluated due to Level 3 precedence; all metric deltas = 0.0)

Level 6: PASS / CONTROLLED_SHARED_PLAN_T2_VALIDATED
         (Not reached)
```

### Exact Final Verdict
- **Verdict Level:** **3**
- **Verdict:** **`FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED`**
- **Verdict Reason:** *"Primary target replacement or fixed locator dependency removal not reproduced: 2/2 targets reproduced under AFTER with valid governed witness, 0/2 dependencies removed."*

---

## 9. Limitations & Discussion

1. **Elimination of Confirmed Confounders:** By using prospectively frozen canonical shared plans, D4-A2-V2 conclusively eliminated the apparent regressions that confounded original D4-A2. Under shared plans, zero critical regressions occurred, and recall deltas across all six primary metrics were identically 0.000000.
2. **The Mechanism of Dependency Removal Failure:** The failure at Level 3 was driven strictly by the dependency removal receipt (`batch1_dependency_removed = 0 / 2`). The formal dependency removal rule requires proving that in the `BEFORE_COMPAT` arm, the exact masked fixed locators were actively injected and relied upon by the plan (`fixed_locator_inputs_active_before = true`), and then cleanly absent in `AFTER_BATCH1_REPLACEMENT` with evidence preserved via the generic mechanism. Under the prospectively acquired shared plans for `g036` and `g021`, the plan generator did not output queries that actively utilized those specific fixed locators in BEFORE. Thus, while AFTER proved that generic structured replacement successfully recovers the target with valid governed witnesses (2/2), the test could not verify removal of an active baseline dependency (0/2).
3. **Absence of General Safety Claim:** While zero treatment regressions were observed across the 16 cases, this finding applies strictly to the frozen cohort under canonical shared plans and does not constitute a global safety proof.

---

## 10. Lifecycle Consequence & Next Steps

```text
D4-A2-V2 = COMPLETE / FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
PRODUCTION_ACTIVATION = false
FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED
D4-A3 = NOT_STARTED / BLOCKED
```

- **Production Activation:** Remains `false`.
- **Runtime Migration:** First-batch fixed locator suppression is **NOT** automatically activated in runtime configuration.
- **D4-A3:** Remains `NOT_STARTED / BLOCKED`. Proceeding to the next batch (D4-A3) is blocked until a formal architectural/repair decision addresses the Level 3 outcome.
- **No Unilateral Reruns:** Raw retrieval results, plans, and evaluator code remain strictly frozen and immutable.
