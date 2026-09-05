# D4-A4 — Second-Batch Low-Risk Locator Retirement Selection & Preregistration

**Authoritative Lifecycle Stage:** `D4-A4`
**Checkpoint:** `D4-A4`
**Date:** `2026-09-05`
**Status:** `COMPLETE / PASS / SECOND_BATCH_LOW_RISK_RETIREMENT_PREREGISTERED`
**Starting HEAD:** `631a66c125e8d58fee24bd448f868b4a8e423ab6`
**Direct Parent:** `8c0971f20f9a2b2680451e3123fa1d95325816bc`
**Batch-2 Production Activation:** `false`
**Next Stage:** `D4-A5 — Second-Batch Low-Risk Locator Controlled Retirement Validation` (`BLOCKED / REQUIRES_SEPARATE_AUTHORIZATION`)

---

## 1. Executive Summary & Scientific Purpose

Phase D4 systematically migrates query-expansion shortcut rules into generic, evidence-bound architectural representations. Following the completion and production activation of Batch 1 in `D4-A3` (commit `631a66c125e8d58fee24bd448f868b4a8e423ab6`), **Batch 2** focuses on a scientifically distinct category of query-expansion components:

> **Fixed locator components for which historical controlled evidence demonstrated no meaningful legacy dependency (`LEGACY == ABLATION`).**

Unlike Batch 1, which required a generic structured evidence-link replacement because legacy shortcuts carried active evidence dependencies, Batch-2 candidates represent **redundant fixed locators**. In accordance with scientific conservatism and parsimony:
1. Redundant locators must **not** receive an artificial or unevidenced structured replacement.
2. The primary research question is:
   * *Which currently remaining fixed locator components have sufficient pre-existing evidence of redundancy to justify a controlled retirement validation, with stable vocabulary and domain scope preserved?*
3. The prospective scientific validation question preregistered in this stage is:
   * *Under identical prospective shared RetrievalPlans, does retiring only those frozen low-risk redundant locator components preserve retrieval and evidence behavior without grounding, version, provenance, or critical-evidence regressions?*

Stage `D4-A4` is **static selection and preregistration only**. No production files are modified, no locators are deleted, runtime retrieval is not invoked, zero provider model calls are made, and no scientific outcome exposure occurs.

---

## 2. Authoritative Starting Boundary & Reassessment Audit

### 2.1 Repository Baseline Invariants
- **HEAD Commit:** `631a66c125e8d58fee24bd448f868b4a8e423ab6` (`D4-A3 activate first-batch runtime migration`).
- **Direct Parent:** `8c0971f20f9a2b2680451e3123fa1d95325816bc` (`D4-A2-V2-R3 close evaluator contract repair`).
- **Commit History:** Exactly one commit exists since R3 closeout.
- **Working Tree & Index:** Clean, verified prior to task execution.

### 2.2 Production Query-Expansion Rule Configuration
Inspection of `configs/query_expansions.yaml` confirms:
- **Total Rules:** Exactly 54 rules.
- **Batch-1 Active Rules:** Exactly 2 rules have `structured_replacement: true`:
  1. `event_poca_handoff`
  2. `restgas_profile_workflow`
- **All Other 52 Rules:** Have effective `structured_replacement = false` (absent or `false`).
- **Batch 1 Runtime Status:** `ACTIVE`.

---

## 3. Historical Candidate Recovery & Current-State Reassessment

### 3.1 Mechanical Recovery from Frozen Authority
Historical inventory `evaluation/d4_a0_expansion_component_inventory.json` mechanically identified exactly three rules with:
`migration_readiness = LOW_RISK_RETIREMENT_CANDIDATE`

1. `effective_acceptance_pipeline`
2. `root_macro_usage`
3. `model_factory_theory`

Historical D3-A2 evidence established `legacy_dependency = NOT_OBSERVED` and prior decision `NO_MEANINGFUL_LEGACY_DEPENDENCY` for all three rules.

### 3.2 Current-State Drift Audit
Each candidate rule was audited against current HEAD `configs/query_expansions.yaml`:

| Rule ID | Current Existence | Triggers Unchanged | Repositories Unchanged | Concepts Unchanged | Symbols Unchanged | Hints Unchanged | `structured_replacement` | Drift Status | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `effective_acceptance_pipeline` | Yes | Yes (5) | Yes (2) | Yes (1) | Yes (3) | Yes (`li_2026: [83,86,89]`) | `false` | None | **SELECTED** |
| `root_macro_usage` | Yes | Yes (3) | Yes (1) | Yes (1) | Yes (2) | Yes (None) | `false` | None | **SELECTED** |
| `model_factory_theory` | Yes | Yes (3) | Yes (1) | Yes (1) | Yes (3) | Yes (`pflueger_2017: [51,57,65]`) | `false` | None | **SELECTED** |

**Audit Findings:**
- Zero material semantic drift observed across all three candidate rules.
- No subsequent scientific artifact superseded their low-risk classification.
- No D4-A3 code change introduced a case-specific dependency on any candidate rule.
- All three candidate rules are confirmed eligible and **SELECTED**.
- Held rules: **0**.

---

## 4. Frozen Batch-2 Retirement Masks & Preserved Semantics

### 4.1 Mask Specification by Rule

#### Rule 1: `effective_acceptance_pipeline`
- **Symbols Proposed for Retirement (3):**
  - `macro/target/prod_sim_hvmaps.C`
  - `data/PndLmdAcceptance.cxx`
  - `model/PndLmdModelFactory.cxx`
- **Paper Page Hints Proposed for Retirement (0):** None.
- **Symbols Preserved (0):** None.
- **Paper Page Hints Preserved (1):**
  - `li_2026: [83, 86, 89]` (Explicitly excluded from retirement; held pending generic document navigation).
- **Preserved Language & Domain Semantics:**
  - Triggers: `["effective acceptance", "restgas acceptance", "acceptance calculation", "有效接受度", "有效接受度"]`
  - Repositories: `["restgas_determination", "luminosityfit"]`
  - Concepts: `["profile-dependent effective acceptance pipeline"]`
- **Post-Retirement Structured Replacement:** `false`.

#### Rule 2: `root_macro_usage`
- **Symbols Proposed for Retirement (2):**
  - `Running/Macros.html`
  - `tools/MasterTasks/PndMasterRunSim.cxx`
- **Paper Page Hints Proposed for Retirement (0):** None.
- **Symbols Preserved (0):** None.
- **Paper Page Hints Preserved (0):** None.
- **Preserved Language & Domain Semantics:**
  - Triggers: `["ROOT macro", "macro execution", "run a ROOT macro"]`
  - Repositories: `["pandaroot"]`
  - Concepts: `["PandaRoot macro invocation"]`
- **Post-Retirement Structured Replacement:** `false`.

#### Rule 3: `model_factory_theory`
- **Symbols Proposed for Retirement (3):**
  - `model/PndLmdDPMAngModel1D.cxx`
  - `model/PndLmdDPMAngModel2D.cxx`
  - `model/PndLmdModelFactory.cxx`
- **Paper Page Hints Proposed for Retirement (1):**
  - `pflueger_2017: [51, 57, 65]`
- **Symbols Preserved (0):** None.
- **Paper Page Hints Preserved (0):** None.
- **Preserved Language & Domain Semantics:**
  - Triggers: `["PndLmdModelFactory", "DPM、acceptance 和 resolution", "DPM acceptance resolution"]`
  - Repositories: `["luminosityfit"]`
  - Concepts: `["DPM model acceptance resolution composition"]`
- **Post-Retirement Structured Replacement:** `false`.

### 4.2 Non-Global Deletion Principle (Section 7 Audit)
A complete occurrence audit across all 54 query expansion rules demonstrates why retirement is rule-component suppression, **never global string deletion**:

| Locator Component | All Current Rule Occurrences (Count) | Batch-1 Status | Batch-2 Candidate Occurrences | Untouched Non-Batch-2 Occurrences |
| :--- | :---: | :---: | :---: | :--- |
| `macro/target/prod_sim_hvmaps.C` | 7 rules | Cleared in B1 | `effective_acceptance_pipeline` | `profile_generation_and_correction`, `reconstructed_profile_to_acceptance`, `target_macro_workflow_grouping`, `hv_maps_vertex_resolution`, `target_generator_theory`, `reconstructed_profile_factory_alias` |
| `data/PndLmdAcceptance.cxx` | 5 rules | Not in B1 | `effective_acceptance_pipeline` | `angular_acceptance`, `reconstructed_profile_to_acceptance`, `acceptance_model_boundary`, `reconstructed_profile_factory_alias` |
| `model/PndLmdModelFactory.cxx` | 9 rules | Not in B1 | `effective_acceptance_pipeline`, `model_factory_theory` | `luminosityfit_model_layers`, `resolution_models`, `panda_luminosityfit_boundary`, `acceptance_model_boundary`, `beam_divergence_theory`, `reconstructed_profile_factory_alias`, `model_factory_acceptance_methods` |
| `Running/Macros.html` | 2 rules | Not in B1 | `root_macro_usage` | `sphinx_operational_architecture` |
| `tools/MasterTasks/PndMasterRunSim.cxx` | 3 rules | Not in B1 | `root_macro_usage` | `simulation_configuration_usage`, `target_generator_sampling_data_flow` |
| `model/PndLmdDPMAngModel1D.cxx` | 3 rules | Not in B1 | `model_factory_theory` | `luminosityfit_model_layers`, `dpm_angular_models` |
| `model/PndLmdDPMAngModel2D.cxx` | 3 rules | Not in B1 | `model_factory_theory` | `luminosityfit_model_layers`, `dpm_angular_models` |
| `pflueger_2017: [51, 57, 65]` | 1 rule | Not in B1 | `model_factory_theory` | (None for exact tuple; other page tuples untouched) |
| `li_2026: [83, 86, 89]` | 2 rules | Not in B1 | `effective_acceptance_pipeline` (**PRESERVED**) | `pointlike_vs_restgas_acceptance` |

No future implementation may delete any locator globally.

---

## 5. Direct Case Cohort, Overlap Matrix & Evidence Denominators

### 5.1 Historical Direct Case Cohort (7 Cases)
Mechanically recovered from D3/D4 authorities:
- **`effective_acceptance_pipeline`:** `g052` (direct trigger), `g055` (control), `n003` (control)
- **`root_macro_usage`:** `n004` (direct trigger), `g007` (control)
- **`model_factory_theory`:** `n014` (direct trigger), `g060` (nonmatching control)

Cohort composition:
- **Gold v2.6 dev:** 4 cases (`g052`, `g055`, `g007`, `g060`)
- **novel_dev:** 3 cases (`n003`, `n004`, `n014`)
- **Answered Cases:** 6 (`g052`, `g055`, `n003`, `n004`, `n014`, `g060`)
- **Negative Control Cases:** 1 (`g007`, expected status `insufficient_evidence`)

### 5.2 Deterministic Case × Rule Match Matrix
Evaluated via deterministic casefolded trigger substring matching:

| Case ID | Query Snippet | Batch-2 Matched Rules | Batch-1 Matched Rules | Other Matched Rules | Batch-2 Collision |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `g052` | Why does a reconstructed restgas profile feed back into effective acceptance? | `effective_acceptance_pipeline` | `restgas_profile_workflow` | `reconstructed_profile_to_acceptance` | **No** (1 match) |
| `g055` | How should angular acceptance be distinguished from longitudinal efficiency? | None | None | `angular_acceptance`, `longitudinal_efficiency` | **No** (0 matches) |
| `n003` | For an acceptance scan I need single particles whose momentum and polar angle advance in fixed steps... | None | None | None | **No** (0 matches) |
| `n004` | While debugging a running PandaRoot macro I want every log message to carry severity... | `root_macro_usage` | None | None | **No** (1 match) |
| `g007` | What exact minimum GPU memory is required to install PandaRoot? | None | None | `installation_requirements` | **No** (0 matches) |
| `n014` | LuminosityFit has a model_framework directory and a native model/ directory... | `model_factory_theory` | None | `model_factory_acceptance_methods` | **No** (1 match) |
| `g060` | How is beam-divergence smearing implemented in LuminosityFit? | None | None | `beam_divergence_theory` | **No** (0 matches) |

**Attribution Architecture:**
- Exactly **0 multi-Batch-2 rule collisions** occur.
- No interaction cells are required.
- Standard rule-isolated retirement cells support strict per-rule attribution.

### 5.3 Evidence Group Applicability & Denominators

| Case ID | Split | Status | Evidence Group ID | Critical | Role | Candidate Count |
| :--- | :---: | :---: | :--- | :---: | :--- | :---: |
| `g052` | dev | answered | `g052.e1` | True | `li_2026_page_141_theory` | 3 pages (141, 149, 151) |
| `g055` | dev | answered | `g055.e1` | True | `pflueger_2017_page_57_theory` | 2 pages (57, 62) |
| `g055` | dev | answered | `g055.e2` | True | `li_2026_page_142_theory` | 2 pages (142, 147) |
| `n003` | dev | answered | `n003.e1` | True | `fixed_step_generator_definition` | 2 objects (`.h`, sphinx page) |
| `n003` | dev | answered | `n003.e2` | True | `per_event_step_advancement` | 1 object (`.cxx`) |
| `n004` | dev | answered | `n004.e1` | True | `fair_logger_documentation` | 2 objects (sphinx page, title) |
| `g007` | dev | negative | `g007.e1` | True | `installation_documentation` | 1 object (sphinx page) |
| `n014` | dev | answered | `n014.e1` | True | `vendored_framework_status` | 1 object (`README.md`) |
| `n014` | dev | answered | `n014.e2` | True | `native_model_layer` | 1 object (`PndLmdModelFactory.h`) |
| `g060` | dev | answered | `g060.e1` | True | `pflueger_2017_page_74_theory` | 2 pages (74, 78) |
| `g060` | dev | answered | `g060.e2` | True | `pnd_lmd_divergence_smearing_model2_d_implementation` | 1 object (`.cxx`) |
| `g060` | dev | answered | `g060.e3` | True | `generate2_dmodel_implementation` | 1 function (`generate2DModel`) |

**Official Denominators:**
- Total Cases: **7**
- Answered Cases (Macro Recall Denominator): **6**
- Negative Control Cases: **1** (`g007`)
- Total Evidence Groups: **12**
- Answered Evidence Groups (Micro Recall Denominator): **11**
- Critical Evidence Groups: **12** (11 in answered cases + 1 in negative control)

---

## 6. Prospective Experimental Protocol & Cell Schedule

### 6.1 Shared Canonical-Plan Architecture
Future D4-A5 validation must strictly obey the lessons of D4-A2-V2:
```text
Question
   ↓
Phase P: Query Analyzer (executed ONCE per unique case)
   ↓
One Immutable Canonical RetrievalPlan
   ├─ CURRENT_COMPAT (Batch 1 active + Batch 2 legacy locators active)
   └─ BATCH2_RETIREMENT (Batch 1 active - Batch 2 retired mask contributions)
```
- **Shared-Plan Equality:** `plan_equality_verified == true` required across all paired cells.
- **Downstream Phase R Analyzer Calls:** Strictly **0**.

### 6.2 Source-Native Provenance Subtraction Semantics
Subtraction in `BATCH2_RETIREMENT` operates on provenance tags:
- An item is removed if and only if its sole provenance source is the retired mask of an active selected Batch-2 rule.
- If an item was independently supplied by a non-Batch2 rule (e.g. `macro/target/prod_sim_hvmaps.C` supplied by `reconstructed_profile_to_acceptance` on `g052`), explicit user query, or accepted Analyzer output, it remains active in `BATCH2_RETIREMENT`.
- Global string deletion is prohibited.

### 6.3 14-Cell Paired Retrieval Schedule

| Case ID | Arm | Batch 1 Runtime | Batch 2 Treatment | Expected Model Calls |
| :--- | :--- | :---: | :---: | :---: |
| `g052` | `CURRENT_COMPAT` | Active | Legacy active | 1 Embedding + 1 Reranker |
| `g052` | `BATCH2_RETIREMENT` | Active | `effective_acceptance` mask subtracted | 1 Embedding + 1 Reranker |
| `g055` | `CURRENT_COMPAT` | Active | Legacy active | 1 Embedding + 1 Reranker |
| `g055` | `BATCH2_RETIREMENT` | Active | No active mask | 1 Embedding + 1 Reranker |
| `n003` | `CURRENT_COMPAT` | Active | Legacy active | 1 Embedding + 1 Reranker |
| `n003` | `BATCH2_RETIREMENT` | Active | No active mask | 1 Embedding + 1 Reranker |
| `n004` | `CURRENT_COMPAT` | Active | Legacy active | 1 Embedding + 1 Reranker |
| `n004` | `BATCH2_RETIREMENT` | Active | `root_macro_usage` mask subtracted | 1 Embedding + 1 Reranker |
| `g007` | `CURRENT_COMPAT` | Active | Legacy active | 1 Embedding + 1 Reranker |
| `g007` | `BATCH2_RETIREMENT` | Active | No active mask | 1 Embedding + 1 Reranker |
| `n014` | `CURRENT_COMPAT` | Active | Legacy active | 1 Embedding + 1 Reranker |
| `n014` | `BATCH2_RETIREMENT` | Active | `model_factory_theory` mask subtracted | 1 Embedding + 1 Reranker |
| `g060` | `CURRENT_COMPAT` | Active | Legacy active | 1 Embedding + 1 Reranker |
| `g060` | `BATCH2_RETIREMENT` | Active | No active mask | 1 Embedding + 1 Reranker |

### 6.4 Scientific Runtime Contract
- **Generation & Reranker Model:** `gemini-3.8-flash`
- **Embedding Model:** `gemini-embedding-2`
- **Location:** `global`
- **Temperature:** `0.0`
- **Identity Coupling:** Independent of agent/staffer model identity.
- **Retry Policy:** `max_retries = 0` (forward-only bookkeeping).

### 6.5 Prospective Call Accounting (Future D4-A5)
- Prospective Plan Acquisition Calls (Phase P): **7**
- Downstream Retrieval Calls (Phase R):
  - Analyzer Calls: **0**
  - Embedding Calls: **14** (7 cases × 2 arms)
  - Reranker Calls: **14** (7 cases × 2 arms)
- QA Agent / Verifier / Judge Calls: **0**
- Database / Qdrant Writes: **0**

---

## 7. Evidence Phenotypes, Metric Tolerances & Verdict Precedence

### 7.1 Phenotype Classifications
- `PAIR_PRESERVED = T/T` (Evidence retained in both arms).
- `PAIR_RETIREMENT_RECOVERY = F/T` (Evidence recovered in retirement arm).
- `PAIR_RETIREMENT_REGRESSION = T/F` (Evidence lost upon locator retirement).
- `PAIR_UNRESOLVED_BOTH = F/F` (**Hard rule:** F/F is baseline omission, NOT a retirement regression).

### 7.2 Strict Retirement Safety Rules
For redundant components, absence of attributable regression is the primary acceptance criterion:
- Critical retirement regressions == **0**
- Grounding regressions == **0**
- Wrong-version regressions == **0**
- Invalid provenance recoveries == **0**

### 7.3 Primary Retrieval Metric Tolerances
- Recall@5 delta >= **-0.05**
- Recall@10 delta >= **-0.05**
- Recall@20 delta >= **-0.05**
- Combined candidate recall delta >= **-0.05**
- Final evidence recall delta >= **-0.05**
- Critical final evidence recall delta >= **0.0**
- MRR: Diagnostic only

### 7.4 Per-Rule Dispositions
- `RETIREMENT_VALIDATED`: Zero attributable regressions on assigned cases; reference baseline reproduced; tolerances satisfied.
- `DEPENDENCY_OBSERVED_RETAIN`: Attributable regression observed; candidate locator was not redundant and must be retained.
- `INCONCLUSIVE_BASELINE_NOT_REPRODUCED`: CURRENT_COMPAT failed to reproduce reference evidence.
- `INVALID_PROTOCOL`: Execution error or protocol violation.

### 7.5 Batch Verdict Precedence Ladder
The complete, conservative 6-level precedence ladder eliminates undefined verdict-space gaps:

```text
Level 1: INVALID / BATCH2_PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED
         Condition: execution_valid == False or protocol_violation == True or missing_inputs == True or plan_equality_all_verified == False or analyzer_provider_calls_downstream > 0 or any rule INVALID_PROTOCOL

Level 2: INCONCLUSIVE / BATCH2_REFERENCE_BASELINE_NOT_REPRODUCED
         Condition: reference_baseline_valid == False or any rule INCONCLUSIVE_BASELINE_NOT_REPRODUCED

Level 3: PARTIAL / SOME_RETIREMENT_CANDIDATES_RETAIN_DEPENDENCY
         Condition: (some or all rules DEPENDENCY_OBSERVED_RETAIN) and has_safety_violation == False

Level 4: FAIL / BATCH2_CRITICAL_OR_GROUNDING_REGRESSION
         Condition: critical_retirement_regressions > 0 or grounding_regressions > 0 or wrong_version_regressions > 0 or invalid_provenance_recoveries > 0 (including safety failure combined with partial dependency)

Level 5: PARTIAL / BATCH2_AGGREGATE_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE
         Condition: all rules RETIREMENT_VALIDATED, has_safety_violation == False, and any aggregate metric delta < tolerance

Level 6: PASS / SECOND_BATCH_LOW_RISK_RETIREMENT_VALIDATED
         Condition: all rules RETIREMENT_VALIDATED, has_safety_violation == False, has_aggregate_regression == False
```

**Key Precedence Invariants:**
- Incomplete evaluator inputs or missing data **cannot PASS** (returns Level 1 INVALID).
- Critical safety violations (critical regression, grounding regression, version violation) return **Level 4 FAIL**, even when partial dependencies are also present.
- Non-critical dependency retention without safety violations returns **Level 3 PARTIAL**.
- All rules passing with metric tolerance violation returns **Level 5 PARTIAL**.
- Complete validation returns **Level 6 PASS**.

---

## 8. Zero-Outcome-Exposure Accounting (D4-A4 Stage)

| Operation / Resource | Permitted in D4-A4 | Actual Count | Status |
| :--- | :---: | :---: | :---: |
| Query Analyzer LLM Calls | 0 | 0 | **PASS** |
| Embedding Calls | 0 | 0 | **PASS** |
| Reranker Calls | 0 | 0 | **PASS** |
| QA Agent / Verifier / Judge Calls | 0 | 0 | **PASS** |
| Runtime Retrieval Invocations | 0 | 0 | **PASS** |
| Benchmark / Novel Retrieval Runs | 0 | 0 | **PASS** |
| Database / PostgreSQL Writes | 0 | 0 | **PASS** |
| Qdrant Vector DB Writes | 0 | 0 | **PASS** |
| Protected Dataset Access (`novel_validation`) | 0 | 0 | **PASS** |
| Protected Dataset Access (`novel_holdout`) | 0 | 0 | **PASS** |
| Production File Modifications | 0 | 0 | **PASS** |
| Locator Deletions | 0 | 0 | **PASS** |

---

## 9. Verification & Test Execution

Controller command:

```powershell
$env:PYTHONPATH='src;evaluation'
& '..\.venv\Scripts\python.exe' -m pytest tests/unit/test_d4_a4_batch2_retirement_preregistration.py -q -p no:cacheprovider
```

Final result: **36 passed in 0.83s**. This includes 1,024 combinations of per-rule dispositions and protocol/baseline/safety/aggregate gates, complete-input rejection checks, four pair phenotypes, eight per-rule decision combinations, per-origin component subtraction, the mechanical schedule, partial page overlaps, and approved-dataset applicability checks.

The AGY worker reported 29 initial D4-A4 tests and a combined 67-test run including unchanged D4-A3 tests. Controller inspection reproduced two false-PASS gaps despite those passing tests; both were repaired before freezing. The controller then ran 33 strengthened tests (PASS), followed by the final 36-test suite (PASS). No full repository suite or scientific evaluation ran.

JSON/YAML parsing, changed-Python static compilation, exact Git scope inspection, and `git diff --check` passed as recorded in the machine-readable selection artifact.

---

## 10. Lifecycle State Progression

Following successful D4-A4 completion:

```text
D4-A2-V2
COMPLETE / PASS (via D4-A2-V2-R3)

D4-A3
COMPLETE / PASS / FIRST_BATCH_RUNTIME_MIGRATION_ACTIVATED

BATCH1
ACTIVE

D4-A4
COMPLETE / PASS / SECOND_BATCH_LOW_RISK_RETIREMENT_PREREGISTERED

BATCH2
SELECTED / FROZEN / NOT_EXECUTED

BATCH2_PRODUCTION_ACTIVATION
false

D4
IN_PROGRESS / INCREMENTAL_QUERY_EXPANSION_MIGRATION
```

---

## 11. Limitations & Audit Boundary

1. **Static Preregistration Only:** This stage performs static candidate selection, drift analysis, occurrence auditing, and experimental preregistration. No scientific outcomes have been observed or measured.
2. **Batch 1 Baseline Invariance:** Both future retrieval arms inherit the active Batch-1 production runtime (selectivity v2, K=3 admission, 30 rerank pool).
3. **No Automatic Activation:** Even a future Level-6 PASS in D4-A5 does not automatically activate retirement in production; production activation remains a separate operational authorization.
4. **Execution Gate:** D4-A5 execution is **BLOCKED** and requires explicit separate authorization.

## 12. Controller Contract Clarifications

Only g052, n004 and n014 match a selected Batch-2 rule. g055, n003, g007 and g060 are explicit no-op controls with empty retirement masks. All 14 scheduled cells remain, with one shared canonical plan ID per pair. Batch-1 policy remains enabled in both arms; its replacement actually triggers only on g052.

Canonical plans and complete contribution ledgers are frozen unchanged. Retirement is an arm-specific execution projection, with removal keyed to each origin rule's own exact component mask. Missing provenance is INVALID before downstream calls. Independently contributed symbols/pages and all language/domain fields survive.

Per-rule primary baseline applicability covers g052.e1, n004.e1 and n014.e1/e2 (three active cases, four groups). Nonmatching controls do not provide per-rule retirement evidence or baseline gates. The aggregate metrics still use all six answered cases (11 groups); g007's one documentation group is a separate retrieval-anchor control, with no QA-status evaluation. All safety findings are recorded even when verdict precedence yields an earlier non-PASS result.

The controller found and repaired two false-PASS input gaps (missing metrics and missing selected rules). Every required flag/counter, all three dispositions and all six finite deltas must be present. Truth-space tests cover every combination of per-rule dispositions with protocol validity, baseline validity, safety and aggregate regression. Source/page audits now enumerate partial single-page overlaps as well as exact page sets.

Future no-retry accounting is 7 Analyzer + 14 embedding + 14 reranker = 35 logical calls/attempts; none are executed here. AGY coding delegation is separate from scientific provider accounting; its token consumption is not measured.
