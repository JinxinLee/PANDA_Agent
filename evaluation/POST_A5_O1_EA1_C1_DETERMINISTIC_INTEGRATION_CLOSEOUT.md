# Post-A5 O1+EA1+C1 Deterministic Integration Closeout

**COMPLETE / PASS / DETERMINISTIC_INTEGRATION_VERIFIED**

The assembled production contracts compose consistently under deterministic fixtures. **DETERMINISTIC INTEGRATION PASS does not equal SCIENTIFIC EFFECTIVENESS PASS.** No product implementation was changed.

## Identity

Starting repository HEAD: `1510904b57c238445e5f45859f8d258b1fc26c42` (clean). Ending repository HEAD is the single closeout commit containing this record, reported exactly in the final delivery. The JSON uses null until that self-referential identity exists and supplies a Git resolution instruction; it does not mislabel the starting or behavior SHA as the ending commit.

Material behavior head remains `6ed3ba361476b36744c72e76f5905733b1755f5c`. O1 `81b1308d6c0fa03c7f83894af851fd71b4503f41`, EA1 `60dff40a671e62bffcbe0eb82d38ea6e9aeb05c4`, C1 `5e0a3a3ae4828ea3b5831646e3d5d2c8f08cc9ed`, C1-R1 `6ed3ba361476b36744c72e76f5905733b1755f5c` are verified ancestors. The previous `1510904` commit is docs-only.

Production mode: `production_answer_obligations_v1`. Prompt version `3.11.0`; mechanically verified fingerprint `03e1bf270898b28127a42fa2e1ccb24cfc1d87e177eeba5428ba4680d426352c`. Production review/revision/schema/version are bound by the canonical fingerprint. No identity drift.

Inspected current qa.py admission, review, R1 projection, routing, trace and finalization; storage.py bounded reader; prompts.py production contracts; evaluation_runner.py fingerprint. Inspected both Markdown and JSON authority records for O1, EA1, C1, C1-R1 and the bounded repair design. Historical reports remain unchanged.

## Integration evidence

A dedicated synthetic module was necessary to exercise the resolved EA1 child across explicit C1 relationship review, revision and finalization, with strict O1 OFF/ON comparisons. It reuses fake clients/storage and existing fixture helpers. No real model, database, retrieval or embedding service is contacted.

| Axis | Finding | Evidence |
| --- | --- | --- |
| I1: Product identity | PASS: Production default remains production_answer_obligations_v1; O1 opt-in defaults false, EA1 admission and production C1 review are active; R1 mappings feed A1; historical modes distinct and E3 not promoted. | O1 test_o1_default_and_exact_neutrality; integration test_historical_contract_is_separate; qa.py _run_detailed/_after_verify_route |
| I2: Prompt identity | PASS: 3.11.0 and canonical 03e1bf27... unchanged. Fingerprint includes production review/revision prompts, private schema and version. | Mechanical fingerprint; C1 test_fingerprint_binds_production_prompts_schema_and_version; evaluation_runner.py prompt_fingerprint |
| I3: Lineage | PASS: All five implementation identities are ancestors of starting HEAD. 1510904 changes four docs/records only; behavior head remains 6ed3ba3. | git merge-base --is-ancestor; git show --stat 1510904 |
| I4: O1 plus EA1 | PASS: Exact selected page resolves real section; trace records RESOLVED_EXACT_BACKING, parent page, child section, and offsets [8,53]. ON/OFF output and exact calls equal. | integration test_resolved_backing_revision_trace_and_finalization (complete and mixed) |
| I5: EA1 plus C1 visibility | PASS: A0/A1 contain real child only; V1/V2 see selected parent plus child, admitted IDs contain only child; both reviews accepted. | integration test_resolved_backing_revision_trace_and_finalization |
| I6: Parent safety | PASS: Incomplete original page remains citation-ineligible and its claim is rejected even with a resolved child. No ID substitution. | integration test_resolved_context_preserves_blocked_paths[parent]; EA1 test_normal_verification_still_rejects |
| I7: C1 resolved-child revision | PASS: Missing admitted relationship alone reaches A1 with child evidence, without parent text or extra retrieval. | integration test_resolved_backing_revision_trace_and_finalization |
| I8: EA cache | PASS: A0 and A1 projections equal; structural storage calls exactly [[page]] per invocation; no alternate child selection. | integration test_resolved_backing_revision_trace_and_finalization; EA1 cache tests |
| I9: R1 mapping authority | PASS: Draft point.1 with verified [] gives no A1 point; verified point.2 gives only point.2. Eligible claim remains repairable and uses resolved child. | integration test_resolved_backing_does_not_override_verified_mapping (2 cases) |
| I10: Visible-only | PASS: Parent-only visible necessary relationship remains incomplete; no A1 solely for it and no parent evidence enters A1. | integration test_resolved_context_preserves_blocked_paths[visible]; mixed integration |
| I11: Ambiguous | PASS: Uncertain relationship with uncertain scope remains incomplete and non-revisionable. Contradictory scope rejected by R1-C tests. | integration test_resolved_context_preserves_blocked_paths[ambiguous]; C1 test_r1_uncertain_check_requires_uncertain_scope |
| I12: Mixed point | PASS: One point contains admitted missing output relation and visible-only Heading relation. Only output reaches A1; V2 repair leaves point incomplete. | integration test_resolved_backing_revision_trace_and_finalization[True] |
| I13: Partial finalization | PASS: Verified claims and real child evidence retained; fixed limitation notice; composer skipped. Public claims rendered=true, dropped claim false. | integration mixed case; test_partial_public_and_dropped_audit_with_resolved_backing |
| I14: Complete finalization | PASS: Recovered fully satisfied case is answered, composer and composer review run, no limitation notice. | integration test_resolved_backing_revision_trace_and_finalization[False] |
| I15: Hard guards | PASS: Version conflict, future runtime, universal proof and unsupported requested symbol/API override C1 partial. Existing locked-catalog absence vs selected-subset absence safety preserved. | integration test_hard_refusal_public_boundary (5 cases); C1 hard-guard tests; QA test_known_class_absent_from_selected_evidence_is_not_refused/test_nonexistent_api_guard_keeps_verified_alternative; generic product negative-existence contract tests |
| I16: O1 stages | PASS: EA, A0, V1, A1 input/output/merge, V2 captured in causal order. Composer captured for complete path and NOT_EXECUTED for partial. | integration test_resolved_backing_revision_trace_and_finalization; O1 suite |
| I17: Trace neutrality | PASS: OFF/ON exact public results, diagnostics excluding trace, usage, retrieval count, model count/order, serialized payloads, schemas and kwargs all equal. | integration assert_neutral in complete and mixed runs |
| I18: Call ceiling | PASS: Recovered complete path exactly 7 fake model calls, partial revision 5; revision_count=1 and route bound preserved. | integration complete/mixed cases; R1 mapping tests route finalize after one revision |
| I19: Retrieval/embedding | PASS: One semantic retrieval and zero embeddings per integrated full run; one structural lookup does not count as semantic retrieval; production does not activate E3. | integration complete/mixed cases; E3 focused suite; qa.py production routing |
| I20: Retrieval truth | PASS: Deep equality of original bundle including rankings/scores/IDs; rebuilt RetrievalTrace matches original selected evidence and still records page, while public evidence is section. | integration complete/mixed cases; EA1 test_four_pages_and_insertion_order |
| I21: Public DTO | PASS: Public claim fields remain exactly claim_id, claim_text, evidence_ids; private coverage/trace keys absent from result across complete, partial and refusal fixtures. Model DTO source unchanged. | integration assert_public; historical/public projection tests |
| I22: Historical compatibility | PASS: shadow_e1_v2, runtime_e1_v2 and legacy_question_core use no production C1 schema/prompt or partial policy; existing routing/merge regressions pass. | integration test_historical_contract_is_separate (3 cases); E2, QA and E3 suites |
| I23: EA1 safety | PASS: 52 focused tests pass: strict predicate, unique exact same-source/version/snapshot/document backing, ambiguity/overflow rejection, lookup fallback/cache and immutable retrieval. | tests/unit/test_post_a5_ea1_exact_backing.py |
| I24: C1 safety | PASS: All 77 current C1/C1-R1 tests pass; no coverage removed. | tests/unit/test_post_a5_c1_coverage_completeness.py |
| I25: O1 safety | PASS: All 33 focused tests pass, including capture failure/size-bound neutrality. | tests/unit/test_post_a5_o1_observability.py |
| I26: Change audit | PASS: Only one integration test module and four closeout/lifecycle documents changed. No product source, prompt, evaluator, benchmark, Gold or calibration diff. | git diff --check; complete changed-path inventory and source diff |

## Verification

- Dedicated integration: **16 passed**.
- O1: **33 passed**; EA1: **52 passed**; C1/C1-R1: **77 passed**.
- Combined existing required batch: **498 passed, 49 subtests passed, 1 isolated baseline failure**. The broader portion excluding the three core suites is 336 passed plus 49 subtests, with that one failure.
- Across distinct tests including the new module: **514 passed, 49 subtests passed, 1 isolated baseline failure**.
- Stale `test_v26_is_default_and_signed_dry_rescore_preserves_real_failures`: expects v2_6 while default is v2_11. Independently rerun at unchanged starting HEAD; source and original test equal baseline. It fails at the default path assertion before rescore. Not repaired.
- Initial seven integration cases passed. An extended legacy fixture initially exhausted a one-response fake queue; corrected the fixture to supply both possible reviews. No assertion weakened or product change made; final 16 passed. This was a test fixture error, not an integration defect or product RED/GREEN cycle.
- Complete diff/path audit and `git diff --check`; product source diff empty. No full repository suite.

Commands (PowerShell sessions set `PYTHONPATH=src`):

```text
PYTHONPATH=src python -m pytest tests/unit/test_post_a5_o1_ea1_c1_integration.py -q --tb=short
```

```text
PYTHONPATH=src python -m pytest tests/unit/test_post_a5_o1_observability.py tests/unit/test_post_a5_ea1_exact_backing.py tests/unit/test_post_a5_c1_coverage_completeness.py tests/unit/test_qa.py tests/unit/test_e2_a1_answer_point_coverage.py tests/unit/test_generic_answer_obligation_completeness.py tests/unit/test_post_a5_generic_product_repair.py tests/unit/test_evaluation_runner.py tests/unit/test_f6_release_identity.py tests/unit/test_e3_missing_point_retrieval.py -q --tb=short
```

```text
PYTHONPATH=src python -m pytest tests/unit/test_evaluation_runner.py::EvaluationRunnerTests::test_v26_is_default_and_signed_dry_rescore_preserves_real_failures -q --tb=short
```

## Materiality, cost and lifecycle

`SOURCE_CHANGE = false`; `MATERIAL_PRODUCT_CHANGE = false`; prompt, evaluator, Gold and calibration changes = false. Test change = true. One integration test module, this report/JSON, and two lifecycle docs are the entire change scope. No candidate freeze or hash manifests created.

New scientific/evaluation calls/tokens = **0 / 0**. Fake client usage counters are synthetic assertions, not scientific consumption.

T1 remains **COMPLETE / FAIL**, historical **65 calls / 373,265 tokens**. No replay, rescore, retroactive repair application or g013/g023-fixed claim.

Protected contents were not accessed. `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`; holdout access, protected-content leakage, F6-B execution = **0**.
Candidate frozen = false; Attempt 6 preregistered/executed = false; `ATTEMPT_6_READINESS = NOT_READY`.

## Limitations and next boundary

No new product-contract gap identified within these fixtures. The known stale test remains failing. Deterministic mechanics do not certify model entailment, necessity judgments, scientific answer quality, live PostgreSQL execution/query planning, network timing or provider behavior. Full suite and scientific cohorts were not run.

Next recommendation: **POST-A5 REPAIRED PRODUCT SCIENTIFIC VALIDATION DESIGN / FIXED EXPOSED SENTINEL T2**. That separately authorized planning task would decide whether T2 is justified, fixed exposed cohort, gates, identity, budget, replay permissions and O1 trace retention. This closeout neither preregisters nor executes T2.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`.
