# F6-A Evaluation-Contract Reconciliation — Critical-Evidence Equivalence + g039 Gold Correction + Hard-Safety Reclassification

Status: `COMPLETE / PASS / EVIDENCE_ROLE_GOLD_AND_GATE_CLASSIFICATION_RECONCILED`

Zero scientific calls. Machine-readable companion: `evaluation/f6_a_evaluation_contract_reconciliation.json`. Focused zero-call tests: `tests/unit/test_f6_a_evaluation_contract_reconciliation.py` (T1–T10, 10/10).

## 1. Scope and authorities

Starting HEAD `f9aa4dfa7da02c47df86dc954ee4dc64b1433b8c`. Starting Gold `m6-benchmark-v2.10` (SHA `bdce5cbd…`), calibration `phase_b_t3_product_language_scope_v7`, formal-English selector 59 IDs (SHA `e27ef67a…`). Attempts 1–5 remain immutable and bound to their historical Gold/evaluator contracts; Attempt 5 remains `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`.

## 2. Critical-evidence construct

- INTENDED_CONSTRUCT: every critical evidence ROLE required by the question receives valid authoritative final support of the required source type and version.
- FINAL_CONTRACT: `role + explicitly reviewed any_of[] selectors`; a critical group is satisfied by any reviewed acceptable selector. Source-specific user requests keep their pinned selectors; `same source type` alone never satisfies a role; no free-form runtime semantic equivalence.
- IMPLEMENTATION_MECHANISM: **Option A — forward-only Gold successor with audited any_of selectors; evaluator matching semantics unchanged; NO EVALUATOR CODE CHANGE** (one exception below). The existing `GoldEvidenceGroup.role + any_of[]` fully expresses the reconciled construct.
- THRESHOLD: `critical_final_evidence_recall == 1.00` unchanged. Interpretation: 100% of required critical evidence roles must be represented by an explicitly approved acceptable evidence selector — materially different from "100% of benchmark-author-pinned original objects must be cited". This distinction is recorded in `docs/EVALUATION_POLICY.md` (§9, "Critical evidence roles and gate categories").

Evaluator code exception: the identifier-catalog cache in `build_identifier_catalog()` received a strictly correctness-only identity check (`cached[0] is object_lookup`, mirroring the existing `_PATH_INDEX_CACHE` pattern). The combined-run test matrix deterministically exposed cache entries colliding on reused `id(lookup)` addresses across test fixtures; the fix changes no metric value (`NEW_EVALUATOR_SEMANTIC_CHANGE = false`).

## 3. Per-case evidence-role reconciliation

Every decision was re-verified from frozen Attempt-5 evidence and locked-corpus content (not copied from prior prose). Equivalence criteria: same substantive obligation; required source type/role preserved; allowed source versions; no weakening of a source-specific user request; independent frozen-corpus justification; acceptable for a normal user answer independent of benchmark outcome.

| Case | Group / role | Decision | Accepted equivalent evidence | Reason |
| --- | --- | --- | --- | --- |
| g011 | g011.e1 (native-install docs) + g011.e2 | **KEEP_AS_IS / PRODUCT_DEFECT / NEGATIVE CONTROL** | none | The answer denied the existence of native-installation documentation the locked corpus contains (143 e1-matching objects; e1 selectors fell out of rerank/top30), and the pinned Docker group was selected then dropped. The e1 role is genuinely necessary for the literal native-vs-container question. g011 stays failing (crit-ev 0.0) — the reconciled metric still catches real failures. |
| g013 | g013.e1 (macros_documentation) | EQUIVALENCE_ACCEPTED | `pandaroot macro/master/mastermacros.rst` (authoritative Master Macros docs, finally cited) | Same macro-invocation obligation and documentation role; the literal question does not require the sphinx page specifically. |
| g016 | g016.e1 (dpmgenerator_documentation) | EQUIVALENCE_ACCEPTED | `pandaroot tools/MasterTasks/PndMasterRunSim.h` (API docs: UseDpmGenerator/SetInput/SetGenerator/SetDpmFlag) | AP p1 names the PndMasterRunSim API; the header documentation satisfies the same selection and mode-choice obligations; required source types documentation+code unchanged; both critical answer points were covered. |
| g020 | g020.e1 (poca_workflow_documentation) | EQUIVALENCE_ACCEPTED | `restgas_determination README.md` readme_section `POCA` (finally cited) | Same two-pass POCA workflow role; all four critical answer points covered (crit_pts_missing = []); selector constrained with `section_contains: POCA` so an arbitrary root-README section does not satisfy the role. |
| g044 | g044.e1 — role renamed `pflueger_2017_page_57_theory` → `angular_acceptance_thesis_theory` | EQUIVALENCE_ACCEPTED | `li_2026` thesis pages 72/79 (thesis_section, finally cited) | AP requires thesis-level acceptance-factor theory (not source-code inference); the literal question does not require Pflueger specifically; li_2026 is an allowed authoritative thesis (paper source type preserved); identical failure shape recurred in Attempts 3/4/5 purely from literal pinning. |
| g110 | g110.e2 (poca_workflow_documentation) | EQUIVALENCE_ACCEPTED | `restgas_determination README.md` readme_section `POCA` plus code (finally cited) | Three-step triage answer covered all three critical answer points (crit_pts_missing = []); same troubleshooting/workflow role; `section_contains: POCA` constraint. |

## 4. g039 Gold correction (forward-only)

- p1 before: `Locate the profile-correction macro and distinguish it from PndLmdAcceptance.`
- p1 after: `Locate the longitudinal-profile efficiency-correction implementation macro.`
- Preserved: required identifier `efficiency_correction_2.C` (critical); forbidden evidence `data/PndLmdAcceptance.cxx`; all other fields.
- Governance principle (generic, recorded in policy): **forbidden evidence ≠ mandatory answer content** — a forbidden-evidence selector guards a known confusion without forcing the public answer to describe the forbidden alternative. The distinction clause was not independently requested by the literal "Where is … implemented?" question.

## 5. Successor Gold m6-benchmark-v2.11

- Path `evaluation/benchmarks/v2_11/gold_questions.yaml`; SHA-256 `39943c6a3f2152e476109c0340acd066795c8de6ff3b6bb2eac6661ac480a417`; parent `m6-benchmark-v2.10` (`bdce5cbd…`, byte-identical, verified unchanged).
- Changed question objects: **6** (`g013`, `g016`, `g020`, `g039`, `g044`, `g110`); the other **114** objects are semantically identical (model-dump comparison). No unrelated metadata rewrites.
- 120 questions; split counts dev 80 / challenge 24 / regression 16; status counts answered 102 / insufficient_evidence 10 / version_conflict 8; 120/120 approved; `official_ready = true`, `structurally_valid = true`, zero unmatched evidence groups, zero unknown allowed source versions.
- Artifact family: `benchmark_manifest.json`, `gold_v2_11_change_report.json`, `gold_v2_11_patch.yaml` (repository-standard successor convention).
- `g011` is deliberately not reconciled (negative control) and is recorded in the change report accordingly.

## 6. Successor calibration phase_b_t3_product_language_scope_v8

- Path `evaluation/baselines/manifests/phase_b_t3_product_language_scope_v8.json`; source Gold `m6-benchmark-v2.11` / `39943c6a…`; parent v7.
- Required because `calibration_compatibility` binds the calibration to the exact active Gold SHA.
- Mechanically verified: formal-English IDs, non-English IDs, and counts unchanged (59/21); selector SHA-256 unchanged (`e27ef67a…`); `compatible = true`.

## 7. Gate-category reclassification (future contracts only)

- `HARD_SAFETY / TRUSTWORTHINESS`: citation integrity, wrong-version evidence, forbidden evidence, contradictions, major unsupported claims, unhandled exceptions.
- `STRICT_RELEASE_QUALITY / COMPLETENESS`: critical answer-point completeness (`critical_answer_point_miss_count == 0`) and critical evidence-role coverage (`critical_final_evidence_recall == 1.00`).
- The historical Attempt-5 preregistration is not modified. **Classification changes; thresholds do not**; both categories remain mandatory wherever a preregistered contract requires them.

## 8. Thresholds

`NUMERICAL_THRESHOLD_CHANGES = NONE`. The post-A5 finding stands: the F6 thresholds are inherited frozen M6 acceptance constants with no repository numerical derivation; no retroactive justification was invented.

## 9. Attempt-5 offline counterfactual (COUNTERFACTUAL / NON-AUTHORITATIVE)

Deterministic recomputation of frozen Attempt-5 outputs under the v2.11 evidence groups (zero model calls):

- `critical_final_evidence_recall`: historical 45/49 = 0.918367 (reproduced exactly) → counterfactual **48/49 = 0.979592**. Changed: g013/g016/g020/g044/g110 → 1.0. Unchanged: **g011 = 0.0 (negative control holds)**. Gate status counterfactual: still FAIL (0.9796 ≠ 1.00) — no pass chasing.
- `critical_answer_point_miss_count`: historical 4 → counterfactual **3** (`COUNTERFACTUAL / NON-AUTHORITATIVE / GOVERNANCE_ADJUDICATION`): the frozen g039 answer opens by locating `macro/target/correction/efficiency_correction_2.C`, the critical required identifier is present (`missing_identifiers = []`), and the g039.e1 group is matched — the corrected literal-location p1 is deterministically satisfied. Remaining counterfactual misses: g013.p3, g023.p3, g047.p1. Gate status counterfactual: still FAIL (3 ≠ 0).
- `identifier_hallucination_rate`: counterfactual 0/130 = 0.0 (established by the identifier repair line). Gate status counterfactual: PASS.
- Overall: Attempt 5 remains FAIL under every counterfactual; no retroactive PASS.

## 10. Historical preservation and protected state

Attempts 1–5 remain immutable and bound to their historical contracts (A1/A2 v2.6, A3 v2.9, A4/A5 v2.10). `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`; `holdout access = 0`; `protected-content leakage = 0`; `F6-B execution = 0`. `MATERIAL_PRODUCT_CHANGE = false`; `EVALUATION_CONTRACT_CHANGE = true`; `GOLD_SUCCESSOR_CREATED = true`; product-behavior lineage HEAD unchanged (`eda7d932…`).

## 11. Attempt-6 readiness

```text
ATTEMPT_6_READINESS = NOT_READY
```

Remaining product-development blockers: g013 bounded-revision recovery insufficiency; g023/g047 answer-content omission with possible semantic-coverage verifier false acceptance; g011 document-role retrieval/reranking loss plus negative corpus-existence claim false acceptance; focused T0/T1/T2 development evidence; no materially new product candidate. Future product work follows: generic product repair → T0 deterministic → affected-case diagnostics → fixed development sentinel / T1 → targeted T2 → only then consider Attempt 6.

## 12. Verification

- Focused zero-call tests T1–T10: 10/10 (`test_f6_a_evaluation_contract_reconciliation.py`).
- Coupled suites: `test_f6a_release_infrastructure.py` + `test_identifier_catalog_repair.py` + reconciliation tests → 56/56 (after the cache identity fix and the authority-migration assertion updates: the manifest-sensitivity test now targets the active authoritative benchmark directory, and the calibration assertions expect v8 / v2.11 — the mechanical successor established by this task, exactly as the v6→v7 and v2.6→v2.9 migrations updated their assertions before).
- `git diff --check` clean. No full test suite (governance task).

## 13. Next task recommendation

```text
NEXT_TASK_RECOMMENDATION =
POST-A5 GENERIC PRODUCT REPAIR /
COMPLETENESS RECOVERY + NEGATIVE-EXISTENCE SAFETY
```

`NEXT_TASK_EXECUTION_AUTHORIZED = false`
