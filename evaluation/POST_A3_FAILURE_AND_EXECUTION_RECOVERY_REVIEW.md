# Post-Attempt-3 Failure and Execution Recovery Review

Task Identity: **POST-ATTEMPT-3 FAILURE & EXECUTION-RECOVERY REVIEW**
Task Stage: **COMPLETE**
Stage Verdict: **COMPLETE / PASS / FAILURES_CLASSIFIED_RECOVERY_INFRASTRUCTURE_REPAIRED_PRODUCT_RESIDUALS_DEFERRED**

### Accepted Development State
* **UNIFIED_POST_A3_TASK_STATUS**: `COMPLETE`
* **FROZEN_PRODUCT_REFERENCE_HEAD**: `d323f790655c62e18b782d606a02f593a673f3cd`
* **NEW_CANDIDATE_DEVELOPMENT_HEAD**: `d3a1b274b2784399a7dc51b094a17e466d208b50`
* **INFRASTRUCTURE_ACCEPTANCE_STATUS**: `PASS`
* **INFRASTRUCTURE_TEST_COUNTS**: `112 passed, 18 subtests passed`
* **INFRA_COMMIT**: `74af96ae7d2ce18e44c6c9e6e7d1ad93d593fdd0`

> [!NOTE]
> This review consolidates evidence across Stage R0 read-only failure analysis, post-terminal diagnostic execution `post-a3-g013-recovery-20260915`, and focused product configuration repair. Selected repairs passed final focused verification; product residuals remain deferred.

---

## 1. Starting State & Identity Verification

* **Starting Git HEAD**: `b0e0d85e1cd41598e866426ea52a3c13bf804b37` (`Record F6-A attempt 3 result`)
* **Starting Working Tree**: Clean tracked files; only existing untracked `data/_a3_gold_args.txt`.
* **Candidate ID**: `f6a-rc3-20260914`
* **Candidate Manifest SHA-256**: `be2101a4709aa2ab2f324ba00b58d90e561ff1e359fc44b28ab26a5b3be155ca`
* **Implementation Git Commit**: `2f9a4a32a41330326976bce4cf29e726ceac908e`
* **Frozen Product Reference HEAD**: `d323f790655c62e18b782d606a02f593a673f3cd` (frozen reference baseline)
* **NEW_CANDIDATE_DEVELOPMENT_HEAD**: `d3a1b274b2784399a7dc51b094a17e466d208b50` (unfrozen product development commit)
* **INFRA_COMMIT**: `74af96ae7d2ce18e44c6c9e6e7d1ad93d593fdd0`
* **Benchmark Authority**: `m6-benchmark-v2.9` (Dataset SHA-256: `eaacd3ed6595821b24b28823c6344abc4dfb954eb71846e682080b42c2f689be`)
* **Candidate Verification**: Pre-diagnostic verification via `verify_candidate(f6a-rc3-20260914)` passed: `valid = true`, `mismatches = []`.

### Official Bound Artifact Immutability Audit

All official Attempt-3 bound artifacts were hash-verified and remain strictly immutable:

| Artifact | Bound Receipt SHA-256 | Current Computed SHA-256 | Status |
|---|---|---|---|
| `results.jsonl` | `360f6c349f464bee2fb38a3d0da2ef4fa8a6de8200c15fe2975ad811b5ac8263` | `360f6c349f464bee2fb38a3d0da2ef4fa8a6de8200c15fe2975ad811b5ac8263` | **UNCHANGED** |
| `gate_matrix.json` | `d40636195b0a307fe19b3884a5618f1096960e6400bd63a7fb2e2d3f47ca5398` | `d40636195b0a307fe19b3884a5618f1096960e6400bd63a7fb2e2d3f47ca5398` | **UNCHANGED** (raw CRLF; normalized LF: `ddd776042ae5c89f863a25bd34b5d65c488fc21ea790ccb0e730fa8680d7185c`, git blob: `0109ca860bcbe3d7d4b5db903cb4eb256c69b318`) |
| `retrieval_traces.jsonl` | `d8f32ef0da4f91df9598b50f6ac9a78d19dab41dc6f336503d66675ef50836f5` | `d8f32ef0da4f91df9598b50f6ac9a78d19dab41dc6f336503d66675ef50836f5` | **UNCHANGED** |
| `candidate_manifest.json` | `be2101a4709aa2ab2f324ba00b58d90e561ff1e359fc44b28ab26a5b3be155ca` | `be2101a4709aa2ab2f324ba00b58d90e561ff1e359fc44b28ab26a5b3be155ca` | **UNCHANGED** |
| `f6_a3_gate_matrix.json` | `d40636195b0a307fe19b3884a5618f1096960e6400bd63a7fb2e2d3f47ca5398` | `d40636195b0a307fe19b3884a5618f1096960e6400bd63a7fb2e2d3f47ca5398` | **UNCHANGED** (raw CRLF; normalized LF: `ddd776042ae5c89f863a25bd34b5d65c488fc21ea790ccb0e730fa8680d7185c`, git blob: `0109ca860bcbe3d7d4b5db903cb4eb256c69b318`) |
| `traces_combined` (58 files) | `e764d24547eb5588f59d66da4091f584821a82772f5c5c9de933c3ba10365e27` | `e764d24547eb5588f59d66da4091f584821a82772f5c5c9de933c3ba10365e27` | **UNCHANGED** |
| `case_id_set` (59 records) | `914ee1b4b3f937e6839416932b44de06fb0401589fd59825a63ac430c5361d1c` | `914ee1b4b3f937e6839416932b44de06fb0401589fd59825a63ac430c5361d1c` | **UNCHANGED** |

---

## 2. Immutable Attempt-3 Outcome

* **Terminal Verdict**: `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`
* **Cohort Status**: `INCOMPLETE` (58 scored / 59 expected; case `g013` uncompleted due to provider 429 `RESOURCE_EXHAUSTED`)
* **Release Score**: Diagnostic 58-case score = `0.974137931...`; Full cohort score = `INCOMPLETE`
* **Official Accounting**: `397` model calls / `3,783,197` tokens (**UNCHANGED**)
* **Failed Release Gates**:
  1. `critical_final_evidence_recall < 1.00`: Failing cases = `g011`, `g022`, `g044`, `g060`
  2. `critical_answer_point_miss_count > 0`: Failing cases = `g022`, `g023`, `g115`
  3. `paper_code_dual_source_rate < 1.00`: Failing case = `g060`
  4. `unhandled_exception_count > 0`: Failing case = `g013` (Vertex 429)

---

## 3. Protocol Deviations Review (PD1 & PD2)

Both protocol deviations are recorded as immutable historical facts:

* **PD1 (Late Immutable Receipt Generation)**:
  * *Observation*: The Stage A1 immutable receipt (`evaluation/f6_a3_a1_receipt.json`) was generated after case-level failure diagnosis and gate inspection were conducted.
  * *Root Cause*: Receipt generation was implemented as a separate manual post-evaluation script rather than being integrated as a mandatory internal step within the runner's finalization path before inspection APIs could be executed.
  * *Enforceable Boundary Limitation*: Automation establishes the closest enforceable programmatic API boundary (embedding receipt creation into runner finalization before diagnostic inspection surfaces execute). Automation cannot police out-of-band manual file inspection directly from the filesystem.
  * *Forward Remedy*: Embed receipt emission directly into the runner's automated stage-finalization pipeline (`report_evaluation`), sealing receipts before failure diagnostic surfaces are exposed.
* **PD2 (Gate Decision on Incomplete Cohort)**:
  * *Observation*: The formal gate decision was sealed at 58 scored / 59 expected cases before completing the preregistered recovery of case `g013`.
  * *Root Cause*: Two contributing factors:
    1. Early stopping heuristic: Three mandatory gates (`critical_final_evidence_recall`, `critical_answer_point_miss_count`, `paper_code_dual_source_rate`) were already mathematically doomed regardless of g013's outcome.
    2. Infrastructure defect: `EvaluationRunStore.completed_ids` treated exception-carrying records as completed, causing ordinary `resume` to skip `g013` without manual file manipulation.
  * *Enforceable Boundary Limitation*: Automation enforces cohort completeness at the evaluation runner and gate evaluation boundary, failing closed when retryable exceptions exist unless recovery is exhausted or an explicit `INCONCLUSIVE` resolution is recorded.
  * *Forward Remedy*: Enforce strict cohort-completeness gate rules (incomplete cohorts cannot PASS/FAIL without recovery attempt or explicit INCONCLUSIVE resolution) and fix `EvaluationRunStore` to distinguish retryable exceptions from successful records.

---

## 4. Post-Terminal g013 Diagnostic Execution & Analysis

An isolated post-terminal diagnostic execution of case `g013` was conducted under frozen candidate `f6a-rc3-20260914`:

* **Execution ID**: `post-a3-g013-recovery-20260915`
* **Verdict**: `COMPLETE / RECOVERED`
* **Status**: `answered` (clean exit code 0)
* **Duration**: `224,822.721 ms` (~3.7 minutes)
* **Separate Scientific Accounting**:
  * **Total Diagnostic Calls**: `10`
  * **Total Diagnostic Tokens**: `62,370`
  * **Breakdown**:
    * Runtime: `9` calls / `57,153` tokens (1 embedding, 8 generation; including 3 composer calls / 2,054 tokens, 3 QA generation calls / 33,837 tokens)
    * Judge: `1` call / `5,217` tokens
* **Diagnostic Evaluator Findings**:
  * `answer_point_coverage`: `0.6667` (Covered `p1` [terminal setup] and `p2` [ROOT macro invocation]; missed `p3` [master run lifecycle loop orchestration]).
  * `critical_answer_points_missing`: `["p3"]`
  * `critical_final_evidence_recall`: `0.5` (`g013.e1` [macros documentation] matched = `false`; `g013.e2` [pnd_master_run_sim_interface] matched = `true`).
  * `final_evidence_recall`: `0.5`
  * `combined_candidate_recall`: `1.0` (Both `g013.e1` and `g013.e2` entered candidate recall).
* **Diagnostic Implication & Correction of Overclaims**:
  The post-terminal diagnostic rerun observed a new outcome under isolated diagnostic conditions (covering `p1` and `p2`, while missing `p3` and `g013.e1`). **No counterfactual claim can be made that g013 would have produced this exact outcome during the original Attempt 3 run.**
  However, the official Attempt 3 terminal `FAIL` was already mathematically irreversible due to the three other measured failures (`critical_answer_point_miss_count > 0`, `critical_final_evidence_recall < 1.00`, and `paper_code_dual_source_rate < 1.00` across cases `g011`, `g022`, `g023`, `g044`, `g060`, and `g115`). Official Attempt 3 accounting (`397` calls / `3,783,197` tokens across 58/59 cases) remains immutably preserved and separate.

---

## 5. Six-Case Failure Review Matrix

Exact stored field and file locators extracted directly from Gold benchmark `m6-benchmark-v2.9` and official Attempt-3 run records:

| Case ID | Query, Intent & Gold Contract | Selected Evidence & Locators | QA Draft, Verifier, Revisions & Final Claims | Metrics & Failed Gates | Detailed Mechanism & Governance Review | Classification & Disposition |
|---|---|---|---|---|---|---|
| **g011** | **Query**: "What is the difference between the native and container setup paths in the locked documentation?"<br>**Intent**: `installation`<br>**Sources**: `['documentation']`<br>**Points**: `p1` (native build), `p2` (container path), `p3` (boundary without host-specific details) [all critical, weight 1.0]<br>**Groups**: `g011.e1` (general native docs: `Install_PandaRoot.rst`, `Install_Developers.rst`, or Sphinx titles), `g011.e2` (`DevelopingInContainer.html`) | 12 items selected into prompt, including:<br>- `evidence.7559211abc27ed65429f362c` (`pandaroot_sphinx_2023_08_25_dev/.../sphinx/Docker/DevelopingInContainer.html`)<br>- `evidence.f2a5bc65591eb5bfd4078e8b` (`pandaroot/docs/Installation/Install_GSI.rst`, lines 15-15)<br>- `evidence.ac31614074a7a932aa21de1c` (`pandaroot_sphinx_2023_08_25_dev/.../sphinx/Installation/Install_GSI.html`) | 1. `revision_count`: 0<br>2. `verification_errors`: `[]`<br>3. Composer: `single_claim_bypass` (source_claim_count: 1)<br>4. Claim audit: `claim.pandaroot.native_vs_container_setup` rendered<br>5. Final claim: `claim.pandaroot.native_vs_container_setup` citing `Install_GSI.rst` & `Install_GSI.html` | `coverage`: 1.0 (p1, p2, p3 covered)<br>`critical_final_evidence_recall`: 0.0<br>`final_evidence_recall`: 0.0<br>**Failed**: `critical_final_evidence_recall` | Candidate recall retrieved general native docs and container docs. Admission selected `DevelopingInContainer.html` alongside GSI cluster docs (`Install_GSI.rst/html`). The generator synthesized a single claim citing only GSI cluster docs, dropping container docs and general native docs. While the evaluator credited conceptual coverage for p1, p2, and p3, **it cannot be asserted without proof that GSI cluster-specific docs satisfy the broad native PandaRoot requirement**. The Gold selector strictly pins general native docs. | **MIXED**<br>(Admission dilution / citation drop vs Gold selector scope)<br><br>**DEFERRED_NO_SAFE_GENERIC_FIX / GOLD_GOVERNANCE_REQUIRED** |
| **g022** | **Query**: "Which documented RHO pages cover data access and particle identification?"<br>**Intent**: `usage`<br>**Sources**: `['documentation']`<br>**Points**: `p1` (data access page), `p2` (PID page) [all critical, weight 1.0]<br>**Groups**: `g022.e1` (`tut_02_01_analysis_dataaccess.html`), `g022.e2` (`tut_02_02_analysis_pid.html`) | 10 items selected into prompt, including:<br>- `evidence.cee3b87a63ad8e396e65d8fa` (`tut_02_01_analysis_dataaccess.html`)<br>- `evidence.5cde262fdecdbd30e1f8f258` (`tut_02_01_analysis_dataaccess.html`)<br>- `evidence.7bfa915e33fd99c375785933` (`tut_02_02_analysis_pid.html`)<br>- Contaminated symbols from mis-expansion: `ana_dpm.C`, `prod_aod_complete.C`, `PndMasterMultiPidTask.cxx` | 1. `revision_count`: 1<br>2. `verification_errors`: `[]`<br>3. Composer: `single_claim_bypass` (source_claim_count: 1)<br>4. Claim audit: `rho_data_access_doc_page` rendered<br>5. Final claim: `rho_data_access_doc_page` citing `evidence.5cde262fdecdbd30e1f8f258` (`tut_02_01_analysis_dataaccess.html`) | `coverage`: 0.5 (p1 covered, p2 missed)<br>`critical_final_evidence_recall`: 0.5 (missed `g022.e2`)<br>**Failed**: `critical_answer_point_miss_count`, `critical_final_evidence_recall` | Two compounding mechanisms: 1. Upstream query expansion contamination: An overly broad trigger `"particle identification"` in `configs/query_expansions.yaml` under `event_alignment` misidentified this query as Restgas event alignment, injecting macro symbols and biasing intent toward `api/code`. **This trigger was VERIFIED and REPAIRED** in configuration and unit tested. 2. Downstream conjunctive completeness omission: Despite both tutorial pages being admitted into prompt context, the generator synthesized only Section 2.1 (Data Access) and noted PID functionality on that page, prematurely terminating and omitting Section 2.2. The single claim bypassed composer. **Downstream omission remains DEFERRED_NO_SAFE_GENERIC_FIX; no claim of rerun QA improvement is made.** | **PRODUCT_DEFECT**<br>(Upstream expansion contamination + downstream conjunctive omission)<br><br>**UPSTREAM_EXPANSION_REPAIRED; DOWNSTREAM_CONJUNCTION_OMISSION_DEFERRED_NO_SAFE_GENERIC_FIX** |
| **g023** | **Query**: "How do I use PndMasterRecoTask in the generic workflow?"<br>**Intent**: `usage`<br>**Sources**: `['documentation']`<br>**Identifiers**: `PndMasterRecoTask` [code_symbol, critical]<br>**Points**: `p1` (identify reco task), `p2` (place after digi), `p3` (place before PID in generic workflow) [all critical, weight 1.0]<br>**Groups**: `g023.e1` (`PndMasterRecoTask.html`), `g023.e2` (`Running.html` / sequence docs) | 12 items selected into prompt, including:<br>- `evidence.ed289136292e433fad81514e`, `bd052f2ff5775c5795bce219` (`PndMasterRecoTask.html`)<br>- `evidence.ad4ae8121d9d774f7be0fea4` (`PndMasterRecoTask.h`, lines 1-49)<br>- `evidence.88e51e108d5fefa28e93001c` (`PndMasterRecoTask.cxx`, lines 1-266)<br>- `evidence.aa848838ccbb763f405765da` (`Running.html`)<br>- `evidence.d452f25b295c0ce037b92b26`, `80855d41b3c0930be267fe52` (`MasterTasks.html`) | 1. Answer requirements generated `workflow_order`<br>2. Initial draft generated 3 claims, including `generic_workflow_position`<br>3. Verifier rejected draft: `['unsupported claim generic_workflow_position', 'missing answer requirement workflow_order']`<br>4. Revision loop ran (`revision_count: 1`); model failed to establish citation to `Running.html`<br>5. Safe salvage cleanly stripped unsupported claim; rendered 2 supported claims: `macro_usage_and_options_documentation` and `task_composition_code_implementation`<br>6. Composer composed 1 paragraph | `coverage`: 0.6667 (p1, p2 covered; p3 missed)<br>`critical_final_evidence_recall`: 1.0 (both groups cited)<br>**Failed**: `critical_answer_point_miss_count` (missing p3) | Verifier rejection, revision loop, and safe salvage all operated as designed to preserve faithfulness and prevent ungrounded claims. During revision, the model did not formulate a verified citation for pipeline ordering before PID, and salvage stripped the unverified claim; this synthesis/revision behavior is deferred without a safe generic fix. | **MIXED**<br>(Model synthesis / revision limit under conservative verifier salvage)<br><br>**DEFERRED_NO_SAFE_GENERIC_FIX** |
| **g044** | **Query**: "Why is angular acceptance needed in a luminosity fit?"<br>**Intent**: `algorithm_theory`<br>**Sources**: `['paper']`<br>**Points**: `p1` (explain efficiency/acceptance factor using thesis, not code) [critical, weight 1.0]<br>**Groups**: `g044.e1` (`pflueger_2017_page_57_theory`, path: `raw_pdf/Diss_2017_Pflueger_Stefan.pdf`) | 12 items selected into prompt, including:<br>- `evidence.d08dc29fa1e6b71836b02306` (`Diss_2017_Pflueger_Stefan.pdf`, **stored pdf_page: 62**, printed page: 57)<br>- `evidence.2f843652cd4238c5b6a656d9` (`Diss_2017_Pflueger_Stefan.pdf`, pdf_page: 63)<br>- `evidence.cdc1f073b82904230b5a9740` (`Diss_2017_Pflueger_Stefan.pdf`, pdf_page: 165)<br>- `evidence.1cb725748eb4f136387bed10` (`li_2026/raw_pdf/thesis.pdf`, pdf_page: 72)<br>- `evidence.09490ca63494447857aaa093` (`li_2026/raw_pdf/thesis.pdf`, pdf_page: 79)<br>- `evidence.7c1096a68c29f4bdcf08afab` (`concept.luminosityfit.luminosity_fit_model`) | 1. `revision_count`: 0<br>2. `verification_errors`: `[]`<br>3. Composer: composed 1 paragraph (source_claim_count: 2)<br>4. Final claims: `luminosity_fit_acceptance_role` citing Li 2026 (p. 72) & domain concept; `luminosity_fit_acceptance_application` citing Li 2026 (p. 79)<br>5. Final evidence: Li 2026 thesis and concept (omitted Pflueger 2017) | `coverage`: 1.0 (p1 fully covered)<br>`critical_final_evidence_recall`: 0.0<br>**Failed**: `critical_final_evidence_recall` | **Stored Locator Verification**: Initial R0 report referenced thesis printed page 57, whereas stored record locator contains `pdf_page: 62` (and additional chunks at pages 63 and 165). Both Pflueger 2017 and Li 2026 were admitted to prompt context. The generator constructed a thorough theoretical answer using Li 2026, which the judge credited with 100% conceptual coverage for p1. However, Gold v2.9 selector strictly pins `pflueger_2017`, scoring 0.0 evidence recall. **Whether Li 2026 is an authoritative equivalent source remains an unproven governance question; this review does not establish a Gold defect.** | **MIXED**<br>(Citation selection preference vs Gold thesis lock)<br><br>**GOLD_GOVERNANCE_REQUIRED** |
| **g060** | **Query**: "How is beam-divergence smearing implemented in LuminosityFit?"<br>**Intent**: `algorithm_implementation`<br>**Sources**: `['paper', 'code']`<br>**Identifiers**: `PndLmdDivergenceSmearingModel2D` [code_symbol, critical]<br>**Points**: `p1` (model identification), `p2` (divergence parameters/distribution), `p3` (factory composition) [all critical, weight 1.0]<br>**Groups**: `g060.e1` (`pflueger_2017`), `g060.e2` (`PndLmdDivergenceSmearingModel2D.cxx`), `g060.e3` (`PndLmdModelFactory.cxx`) | 10 items selected into prompt, including:<br>- `evidence.5eafe820c8a090563c8abb46` (`PndLmdDivergenceSmearingModel2D.cxx`, lines 1-274)<br>- `evidence.08873b527eb593d445b58bdf` (`PndLmdModelFactory.cxx`, lines 1-910)<br>- `evidence.a8393fe1badc6e8a71322f45` (`PndLmdDivergenceSmearingModel2D.cxx`, lines 145-214)<br>- `evidence.53c74137d1c7d3dcbfc8f768` (`Diss_2017_Pflueger_Stefan.pdf`, pdf_page: 56) | 1. `revision_count`: 1<br>2. `verification_errors`: `[]`<br>3. Composer: composed 2 paragraphs (source_claim_count: 4)<br>4. Final claims: 4 claims (`claim_1` to `claim_4`) citing `PndLmdModelFactory.cxx` and `PndLmdDivergenceSmearingModel2D.cxx`<br>5. Final evidence: strictly code implementation files; omitted `pflueger_2017` | `coverage`: 1.0 (p1, p2, p3 fully covered)<br>`critical_final_evidence_recall`: 0.6667 (missed `g060.e1`)<br>`paper_code_dual_source`: False<br>**Failed**: `critical_final_evidence_recall`, `paper_code_dual_source_rate` | Under the F2-A5 (R01) architectural contract, raw questions dictate hard source obligations (`qa.py` / `retrieval.py`). Because the query explicitly asks "How is ... implemented" without mentioning paper theory, only `code` was established as a hard obligation. The generator produced 4 claims strictly citing code implementation, which achieved 100% answer-point coverage and passed verification. However, Gold v2.9 mandates dual sources `['paper', 'code']`. **This divergence between the runtime question-grounding contract and Gold's dual-source requirement is an evaluator reconciliation and governance question, not an established product defect.** | **MIXED**<br>(Question-grounding contract vs Gold dual-source requirement)<br><br>**GOLD_GOVERNANCE_REQUIRED / EVALUATOR_RECONCILIATION_REQUIRED** |
| **g115** | **Query**: "Why might LMD angular acceptance be confused with pvz efficiency?"<br>**Intent**: `troubleshooting`<br>**Sources**: `['code']`<br>**Points**: `p1` (angular coordinates/products), `p2` (longitudinal pvz coordinate/products), `p3` (explain how checking class/file names and histogram axes prevents mixing the two) [all critical, weight 1.0]<br>**Groups**: `g115.e1` (`PndLmdAcceptance.cxx`), `g115.e2` (`efficiency_correction_2.C`) | 12 items selected into prompt, including:<br>- `evidence.3323773842e278af4dc4d57e` (`data/PndLmdAcceptance.cxx`, lines 1-85)<br>- `evidence.ed959b5c98687ff96b42df06` (`macro/target/correction/efficiency_correction_2.C`, lines 1-873)<br>- `evidence.4c8c16a447da23f89b4b8f0b` (`macro/target/correction/efficiency_correction_steps.C`, lines 1-286)<br>- `evidence.9136c66414b429e98e94e236` (`Diss_2017_Pflueger_Stefan.pdf`, pdf_page: 57)<br>- `evidence.962810aa4795fb86662f03cd` (`Diss_2017_Pflueger_Stefan.pdf`, pdf_page: 66)<br>- Domain concept | 1. `revision_count`: 1<br>2. `verification_errors`: `['missing answer requirement source_role_grounding']`<br>3. Composer: composed 2 paragraphs (source_claim_count: 4)<br>4. Final claims: 4 claims explaining coordinate systems, data products, IP smearing, and longitudinal efficiency<br>5. Final evidence: `PndLmdAcceptance.cxx`, `efficiency_correction_2.C`, `efficiency_correction_steps.C`, `pflueger_2017` (pdf_pages 57, 66), and domain concept | `coverage`: 0.6667 (p1, p2 covered; p3 missed)<br>`critical_final_evidence_recall`: 1.0 (both code groups cited)<br>**Failed**: `critical_answer_point_miss_count` (missing p3) | Both required code evidence groups were cited in final evidence (recall 1.0). The answer thoroughly addressed physical definitions, acceptance calculations, and confusion causes from IP smearing (satisfying points p1 and p2). However, point p3 was missed because Gold v2.9 requires explaining how checking class/file names and histogram axes prevents mixing the two. The user query asked "Why might LMD angular acceptance be confused with pvz efficiency?" ("why" causal/physical demand) without asking for operational disambiguation procedures ("how to prevent"). **Whether p3 (operational preventative disambiguation) is semantically entailed by the causal prompt or represents an unprompted rubric expectation is a question for Gold governance review; developers have no authority to declare Gold truth defective unilaterally.** | **MIXED**<br>(Troubleshooting answer-point completeness vs Gold preventative scope uncertainty)<br><br>**GOLD_GOVERNANCE_REQUIRED** |

---

## 6. Shared Mechanism Clusters & Characterization

### Cluster A: Selected Evidence to Final Evidence Drop
* **Mechanism**: Evidence satisfying Gold contract is present in selected prompt context, but the QA generator attaches only a subset of citations to final claims or drops citations during single-claim bypass.
* **Affected Cases**: `g011`, `g022`, `g044`, `g060`.
* **Characterization**: This is ordinary selective citation behavior in RAG when multiple sources are available. **It must not be addressed by forced citation quotas or universal evidence attachment**, which would not establish substantive source use.

### Cluster B: Question-Grounding Contract vs Dual-Source Expectation
* **Mechanism**: F2-A5 (R01) architectural contract mandates that raw questions alone dictate hard source obligations, whereas Gold benchmark retains legacy dual-source requirements for certain implementation queries.
* **Affected Cases**: `g060`.
* **Characterization**: Contract reconciliation is required between runtime question-grounded source obligations and Gold benchmark evaluation rules; no unilateral product patch is authorized.

### Cluster C: Answer-Point Completeness Miss
* **Mechanism**: Generator misses an answer point despite evidence availability, observed in conjunctive queries ("A and B"), pipeline sequence ordering, or unprompted preventative checks.
* **Affected Cases**: `g022`, `g023`, `g115`.
* **Characterization**: In `g022`, conjunctive omission remains deferred; in `g023`, verifier rejection and safe salvage operated as designed with synthesis and revision behavior deferred; in `g115`, causal query vs operational preventative rubric scope is a governance question.

### Cluster D: Candidate Admission Dilution
* **Mechanism**: Target documents enter candidate recall but are diluted during admission by competing specialized chunks.
* **Affected Cases**: `g011`.
* **Characterization**: Cluster-specific GSI documentation chunks diluted general native documentation in top selected evidence.

### Cluster F: Gold Benchmark Selector and Rubric Scope
* **Mechanism**: Gold benchmark selectors pin a specific single author's thesis or impose preventative verification points not directly prompted by the user query.
* **Affected Cases**: `g011`, `g044`, `g115`.
* **Characterization**: Governance questions requiring formal benchmark review; developers have no authority to declare Gold truth defective unilaterally.

---

## 7. Product Verification & Repaired Configuration

### Verified Configuration Repair (Upstream Query Expansion Contamination)

1. **Repaired File**: [`configs/query_expansions.yaml`](../configs/query_expansions.yaml#L110)
   * Removed overly broad trigger `"particle identification"` from rule `event_alignment`.
   * Preserved genuine alignment triggers: `["event id alignment", "event alignment", "event ID对齐", "事件对齐"]`.
2. **Deterministic Test-First Verification**: [`tests/unit/test_query_expansions.py`](../tests/unit/test_query_expansions.py)
   * **RED Stage**: **6 failed, 3 passed, 10 subtests passed** in 2.88s (reproducing false-positive triggering on generic PID queries).
   * **GREEN Stage**: **4 passed, 15 subtests passed** in 2.34s (all generic PID queries isolated; genuine alignment queries trigger properly; neighboring rules preserved; retriever preparse isolated).
3. **Focused Regression & Integration Test Suite**:
   * Host verified: **84 passed, 42 subtests passed** across query expansions, config, shortcut, and retrieval:
     * `tests/unit/test_query_expansions.py`: **4 passed, 15 subtests passed** in 2.34s
     * `tests/unit/test_config.py`: **8 passed** in 0.33s
     * `tests/unit/test_d3_structured_shortcut.py`: **8 passed** in 2.32s
     * `tests/unit/test_retrieval.py`: **64 passed, 27 subtests passed** in 3.79s
   * Host verified product QA suite:
     * `tests/unit/test_qa.py`: **210 passed, 25 subtests passed**
   * Total host verified product tests: **84 passed, 42 subtests passed** (retrieval/expansion/config) + **210 passed, 25 subtests passed** (QA suite).
4. **Scientific Cost**: **0 model calls / 0 tokens** (pure deterministic tests).
5. **Explicit Limitation**: **No claim of rerun QA improvement is made for g022.** The downstream conjunction completeness omission remains deferred.

---

## 8. Execution-Recovery Infrastructure Review

### Infrastructure Acceptance Status
* **Status**: `PASS` (focused deterministic verification complete)
* **Infrastructure Test Counts**: `112 passed, 18 subtests passed`
* **Infrastructure Commit**: `74af96ae7d2ce18e44c6c9e6e7d1ad93d593fdd0`

### Accepted Infrastructure Mechanisms
1. **`EvaluationRunStore` Exception Classification**:
   * Distinguish records: `successful`, `retryable_exception` (transient transport failures like Vertex 429), and `terminal_exception` (non-retryable permanent errors).
   * `completed_ids` excludes retryable exceptions, allowing resume to re-evaluate only retryable failures while never repeating successful cases.
2. **Cumulative Usage Append Ledger & Crash Replay**:
   * Cumulative usage tracking across failed and retried attempts in append ledger, with crash-resilient replay accounting.
3. **Explicit Candidate Binding & Re-Verification**:
   * Strict candidate identity binding with manifest hash re-verification (`verify_candidate`) before execution to prevent configuration drift.
4. **Cohort Recovery Before Gates (Tri-State Decision Rule)**:
   * Prior to gate evaluation, cohort status determines decision mode:
     * Complete cohort (all cases succeeded) $\rightarrow$ evaluate release gates (`PASS` / `FAIL`).
     * Incomplete cohort with retryable exceptions $\rightarrow$ `RECOVERY_PENDING`.
     * Incomplete cohort with unresolvable missing cases $\rightarrow$ fail closed with `INCONCLUSIVE / PRE_RELEASE_EXECUTION_INCOMPLETE`.
5. **Runner Sealing Before Diagnostics with Content Validation**:
   * Automated runner stage finalization seals the run receipt with payload hash and content validation before diagnostic inspection surfaces or case review APIs are exposed.
6. **Standalone Gate-Adjacent Input Receipt**:
   * Standalone gate CLI binds preregistration manifest, raw results, and derived gate matrix, validating input integrity and recording pending output status only. It never creates or overwrites an execution run receipt.

### Independent Review Findings & Helper Corrections
Independent review of the initial recovery implementation identified four critical issues, resolved through focused failing regressions and verified repairs:
1. *Empty budget stop*: An empty but expected cohort now yields RECOVERY_PENDING, preserving budget-stop status instead of crashing.
2. *Receipt decision tamper*: Receipt validation recomputes all bound sections and detects changed decisions and same-usage ledger mutations.
3. *Malformed QA/result/mode*: QA/full records require a result with a legal QAStatus; metrics-only records cannot count as completed.
4. *Unbound dev truthfulness*: Unbound development runs report candidate_valid=null without claiming frozen verification.

Helper acceptance regressions: 6 failed / 16 passed before repair, 22 passed after repair. Gate CLI: 6 failed / 2 passed before repair, 8 passed after repair.

### Runner Lifecycle Verification
Four runner regressions failed before the local integration corrections and now pass:
1. *Store timestamp drift*: The ledger and current record now use the same attempt payload; legacy seeding does not invent timestamps. Successful record bytes remain unchanged on resume.
2. *Review-before-report file persistence*: Computed metrics, including result_content_hash, and gate files are persisted before sealing; direct review followed by report preserves the receipt.

### Changed File Inventory
Committed implementation and verification files:
* **Core Infrastructure**:
  * [`src/panda_agent/evaluation.py`](../src/panda_agent/evaluation.py)
  * [`src/panda_agent/evaluation_finalization.py`](../src/panda_agent/evaluation_finalization.py)
  * [`src/panda_agent/evaluation_runner.py`](../src/panda_agent/evaluation_runner.py)
  * [`src/panda_agent/cli/evaluate.py`](../src/panda_agent/cli/evaluate.py)
  * [`evaluation/scripts/f6a_gate_evaluation.py`](scripts/f6a_gate_evaluation.py)
* **Infrastructure Test Suite**:
  * [`tests/unit/test_f6a_release_infrastructure.py`](../tests/unit/test_f6a_release_infrastructure.py)
  * [`tests/unit/test_post_a3_execution_recovery.py`](../tests/unit/test_post_a3_execution_recovery.py)
  * [`tests/unit/test_post_a3_finalization_contract.py`](../tests/unit/test_post_a3_finalization_contract.py)
  * [`tests/unit/test_post_a3_gate_cli.py`](../tests/unit/test_post_a3_gate_cli.py)
  * [`tests/unit/test_post_a3_runner_lifecycle.py`](../tests/unit/test_post_a3_runner_lifecycle.py)
* **Product Configuration & Verification**:
  * [`configs/query_expansions.yaml`](../configs/query_expansions.yaml)
  * [`tests/unit/test_query_expansions.py`](../tests/unit/test_query_expansions.py)
* **Review & Roadmap Documentation**:
  * [`evaluation/POST_A3_FAILURE_AND_EXECUTION_RECOVERY_REVIEW.md`](POST_A3_FAILURE_AND_EXECUTION_RECOVERY_REVIEW.md)
  * [`evaluation/post_a3_failure_and_execution_recovery_review.json`](post_a3_failure_and_execution_recovery_review.json)
  * [`docs/EVALUATION_STATUS.md`](../docs/EVALUATION_STATUS.md)
  * [`docs/GENERALIZATION_ROADMAP.md`](../docs/GENERALIZATION_ROADMAP.md)

---

## 9. Scientific Accounting Summary

| Category | Model Calls | Token Usage | Status |
|---|---|---|---|
| **Official Attempt 3** | `397` | `3,783,197` | **IMMUTABLY PRESERVED** |
| **g013 Post-Terminal Diagnostic** | `10` | `62,370` | **RECORDED SEPARATELY** |
| *(Diagnostic Runtime)* | *9* | *57,153* | *(1 emb, 8 gen)* |
| *(Diagnostic Judge)* | *1* | *5,217* | *(1 gen)* |
| **Review & Product Verification** | `0` | `0` | **ZERO COST** |

---

## 10. Protected Cohorts, Historical Stages & Candidate State

* **A1 Old Result**: No rewrite (`397` model calls, `3,783,197` tokens across 58/59 cases immutable)
* **Stages A2–A5**: `NOT_REACHED`
* **novel_validation**: `PRISTINE_FOR_CURRENT_LINEAGE` (access count = 0, protected-content leakage = 0)
* **holdout access**: `0`
* **protected-content leakage**: `0`
* **F6-B execution**: `0` (`LOCKED / F6_A_DID_NOT_PASS`)
* **Candidate Frozen**: `false`
* **Attempt 4 Preregistered**: `false`
* **Attempt 4 Executed**: `false`
* **Frozen Product Reference HEAD**: `d323f790655c62e18b782d606a02f593a673f3cd` (frozen reference baseline)
* **NEW_CANDIDATE_DEVELOPMENT_HEAD**: `d3a1b274b2784399a7dc51b094a17e466d208b50` (unfrozen product development commit)
* **INFRASTRUCTURE_ACCEPTANCE_STATUS**: `PASS`
* **INFRASTRUCTURE_TEST_COUNTS**: `112 passed, 18 subtests passed`
* **INFRA_COMMIT**: `74af96ae7d2ce18e44c6c9e6e7d1ad93d593fdd0`

---

## 11. Recommendations & Safe Next Task

### Safe Next Task Recommendation
```text
NEXT_TASK_RECOMMENDATION =
F6-A RESIDUAL CONJUNCTION & REVISION EVIDENCE REVIEW AND GOLD GOVERNANCE PREPARATION
(Focus: 1. Evaluate downstream conjunction handling in question decomposition; 2. Formulate governance requests for g044 equivalent thesis selector, g060 question-grounded source contract reconciliation, and g115 why-vs-how rubric scope; 3. Residual conjunction/revision evidence and Gold governance preparation only; no Attempt 4 preregistration)
```

### Stop Rule & Authorization
```text
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
No new evaluation is authorized. This review consolidation completes the designated scope. Final infrastructure verification: 112 tests and 18 subtests passed. Combined focused verification: 406 tests and 85 subtests passed; no additional scientific calls.
