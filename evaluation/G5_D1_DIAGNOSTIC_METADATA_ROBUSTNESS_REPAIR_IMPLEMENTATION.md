# G5 D1 Diagnostic-Metadata Robustness Repair Implementation

## 1. Decision and repository authority

**PASS / COMPLETE / DETERMINISTIC VERIFICATION PASS.** The approved [D1 diagnostic isolation design](G5_D1_DIAGNOSTIC_METADATA_ROBUSTNESS_REPAIR_DESIGN.md) is implemented without redesign. The [integrated failure-family review](G5_INTEGRATED_FAILURE_FAMILY_REVIEW.md) and all historical G4/G5 results remain unchanged.

Starting `main` HEAD: `8288188d718ef5bfd63cb3a86a4ec1cc01626747`, message `Review G5 failure families and design D1 diagnostic isolation`, parent `7326950d8531e53898910e9db5a2ee3fb39f34e1`. Entry worktree was clean. Previous product lineage: `047201166057edd9859292a1760bc2e9bbf173a2`.

The commit introducing this implementation is the new product-behavior lineage and task delivery commit; resolve its exact SHA from Git history under message `Isolate production ambiguity diagnostics from D1 semantics`. The SHA is reported on delivery, without a self-referential hash in this document. Normal mode remains `production_answer_obligations_v1`.

Authorization covers this implementation, focused deterministic tests, necessary current-state documentation, and commit only. No push, V1 design/repair, live QA/retrieval evaluation, n018 rerun, new G5 run, G6, or protected access is performed.

## 2. Implemented behavior

Source owner: `src/panda_agent/question_decomposition.py`.

- Production envelope still requires a dictionary and `points`, rejects any key outside `points`/`ambiguity`, and enforces the existing list/count checks. Only diagnostic `ambiguity` may be missing.
- All existing point/relation validation, exact question provenance, duplicate rejection, bounds, normalization, sorting, and host ID assignment execute before production ambiguity interpretation. No semantic validation is relaxed, truncated, repaired, or bypassed.
- `_production_diagnostic_ambiguity` catches only Pydantic `ValidationError` raised by `_Ambiguity.model_validate(value)`. Valid objects retain their fields. Missing/null/malformed/unknown/extra-field diagnostics return a fresh `{"status":"unavailable","reason":""}`. Invalid provider text is not copied into the fallback reason.
- The helper runs in production return assembly after semantic canonicalization. Shadow still uses strict `_Proposal` and its original ambiguity validation. Transport/JSON errors, semantic failures, and downstream errors have no new catch or retry.

The `_Ambiguity` and `_Proposal` definitions, all provider prompts/schemas, versions, optional facet/relation-type behavior, legacy QA, `qa.py`, retrieval, admission, coverage, revision, finalization, and runtime mode are unchanged. No new parent-span-containment rule is introduced; exact substring provenance still does not prove semantic entailment.

### Diagnostic containment

Static inspection of `qa.py::_run_detailed` and `_active_runtime_answer_points` confirms that the graph receives the canonical points/relations; ambiguity is emitted only in `diagnostics.question_decomposition`. The fake-provider production integration compares actual graph inputs and all model-facing calls between clear and unavailable diagnostic runs. They are identical, including one decomposition call and no added revision/retry. No downstream control logic for `unavailable` was added. The sentinel is a host diagnostic, not a provider status, QA status, completeness state, or semantic fallback.

## 3. RED -> GREEN evidence

Before any product source edit, added a neutral synthetic fixture asking about Cedar/Birch/Maple order, output, and location. The provider proposal contains valid production points and relations, deliberately reversed provider order, and duplicate literal spans. Its valid-diagnostic baseline succeeds. With only diagnostic status changed to `none`, the focused success assertion fails at the old early `_Ambiguity.model_validate` call:

```text
1 failed
pydantic_core.ValidationError:
status: Input should be 'clear' or 'ambiguous'
[type=literal_error, input_value='none', input_type=str]
```

This is the requested pre-edit RED, not an unrelated test failure. After implementation the same test is GREEN within the 49 passing focused checks. It compares the whole result against the valid baseline with only ambiguity replaced, including point/relation text, spans, order, canonical IDs, and diagnostic-only types. The proposal remains unmodified; one fake decomposition call occurs.

No n018 domain text, Gold content, expected source, live run, or case-specific branch is used. The original failed n018 semantic proposal was never saved, so this result establishes the failure class only when authoritative semantics are valid.

## 4. Exact focused commands and results

Commands ran in the repository root using the existing sibling virtual environment, with no installation or dependency changes.

| Stage | Command | Result |
|---|---|---|
| Pre-edit RED | `& '..\.venv\Scripts\python.exe' -m pytest tests/unit/test_question_decomposition.py::test_production_none_ambiguity_preserves_canonical_semantics -q` | 1 expected failure; ambiguity literal validation |
| Post-edit new controls and production integration | `& '..\.venv\Scripts\python.exe' -m pytest tests/unit/test_question_decomposition.py tests/unit/test_g1_relationship_obligations.py::test_production_unavailable_ambiguity_is_confined_to_diagnostics -k 'production or shadow_none' -q` | 49 passed, 31 deselected |
| Existing decomposition/shadow/legacy neighbors | `& '..\.venv\Scripts\python.exe' -m pytest tests/unit/test_question_decomposition.py -k 'not production and not shadow_none' -q` | 31 passed, 48 deselected |
| Existing G1 regression controls | `& '..\.venv\Scripts\python.exe' -m pytest tests/unit/test_g1_relationship_obligations.py -k 'not production_unavailable_ambiguity and not schema_and_fingerprint' -q` | 44 passed, 1 deselected |

Post-edit total: **124 distinct checks passed**, no post-edit failure. The G1 selection excludes the already-run new integration check; the other exclusion substring does not match an existing test, so all 44 pre-existing G1 checks ran. Existing provider-schema/fingerprint property tests run in memory as part of those regressions; no prompt fingerprint artifact or identity manifest is regenerated. No full repository suite or scientific evaluation runs.

### Coverage of the approved matrix

| Obligation | Evidence |
|---|---|
| D1-DM-1/2/3 | Neutral none RED/GREEN; clear/ambiguous reason preserved; compact invalid diagnostic parametrization; missing diagnostic accepted; semantic equality/input immutability/single call |
| D1-DM-4 | Missing/empty/six/nonlist points, nonobject root, foreign top-level key all reject before helper invocation |
| D1-DM-5 | Wrong/blank point text, empty/malformed/nonliteral support, foreign/model ID fields, duplicate normalized text reject with invalid diagnostic |
| D1-DM-6 | Missing/nonlist relations, malformed relation/type/text/length/spans, four-per-point, foreign/model ID fields, duplicates reject; ten total accepted, eleven rejected |
| D1-DM-7/8 | Global duplicate across parents rejects; reordered multi-point/relation provider output retains canonical identity; existing G1 parent authority and diagnostic-type controls pass; no new containment constraint |
| D1-DM-9 | Real QA graph with scripted providers receives identical semantic inventory and model-facing calls; unavailable appears only in returned diagnostic; no additional invocation |
| D1-DM-10 | Shadow none remains invalid; existing legacy bypass tests pass; injected transport and JSON errors propagate as the same exceptions before graph; malformed semantics prevent graph |
| D1-DM-11 | Existing G1 required-disposition, single completeness path, target-local A1 and full-contract V2 controls pass; static/integration containment proves ambiguity does not enter those inputs |

Representative invalid semantic/envelope cases explicitly mock the diagnostic helper and assert it was not called: diagnostic fallback cannot hide the semantic failure. Provider failure controls assert one attempted generate_json invocation and zero graph invocations; semantic-failure seam likewise asserts graph not called. All provider/retriever activity in tests is scripted/fake.

Static AST comparison against starting HEAD verifies every pre-existing top-level contract assignment, `_Point`, `_Ambiguity`, `_Proposal`, and the entire semantic validation/canonicalization block are unchanged. Static diagnostic-consumer search confirms no new downstream sentinel consumer. `git diff --check` and bounded documentation/history checks provide delivery validation, not an additional evaluation tier.

## 5. Changed files

- `src/panda_agent/question_decomposition.py`: production envelope, one local diagnostic helper, late production interpretation.
- `tests/unit/test_question_decomposition.py`: neutral RED/GREEN and focused diagnostics, semantic, envelope, identity, shadow/provider/graph controls.
- `tests/unit/test_g1_relationship_obligations.py`: one actual production graph integration using existing fixtures.
- `evaluation/G5_D1_DIAGNOSTIC_METADATA_ROBUSTNESS_REPAIR_IMPLEMENTATION.md`: this record.
- `docs/EVALUATION_STATUS.md`: authoritative current state and forward summary only.
- `docs/GENERALIZATION_ROADMAP.md`: authoritative current state and forward summary only.

Historical G5/G4 documents and results, dataset/Gold/calibration/dependencies/configuration, and all other source remain untouched. No redundant machine result, hashes, receipts, logs, feature flags, modes, or retries are added.

## 6. Materiality, cost, lifecycle, and limitations

```text
G5_D1_REPAIR_IMPLEMENTATION = COMPLETE / DETERMINISTIC VERIFICATION PASS
D1_DIAGNOSTIC_ISOLATION = VERIFIED
SEMANTIC_FAIL_CLOSED_CONTROLS = PASS
PRODUCT_SOURCE_CHANGE = true
PRODUCT_BEHAVIOR_CHANGE = true
TEST_CHANGE = true
PROMPT_CHANGE = false
PROMPT_SET_VERSION = 3.12.0
QUESTION_DECOMPOSITION_PROMPT_VERSION = 3.0.0
QUESTION_DECOMPOSITION_SCHEMA_VERSION = e1.question_decomposition.v3
COVERAGE_SCHEMA = coverage-satisfaction-v2
CONFIG_CHANGE = false
PROVIDER_SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
DEPENDENCY_CHANGE = false
NEW_RUNTIME_MODE = false
NORMAL_PRODUCT_MODE = production_answer_obligations_v1
NEW_G5_RUNS = 0
N018_LIVE_RERUNS = 0
QA_SCIENTIFIC_RUNS = 0
RETRIEVAL_EVALUATION_RUNS = 0
SCIENTIFIC_GENERATION_CALLS = 0
SCIENTIFIC_EMBEDDING_CALLS = 0
SCIENTIFIC_CALLS = 0
EXTERNAL_JUDGE_CALLS = 0
SCIENTIFIC_TOKENS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
ORIGINAL_N018_EMPIRICAL_RECOVERY = NOT_ESTABLISHED
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = G5 V1 DISPOSITION-PROVENANCE FALSE-INSUFFICIENCY REPAIR DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

The change deterministically intercepts unusable production ambiguity metadata when semantic validation succeeds. It does not establish original n018 empirical recovery, provider extraction quality, false-insufficiency recovery, V1 provenance reliability, retrieval benefit, or integrated readiness. No before/after scientific metric is available. The only before/after observation is the neutral focused diagnostic test: exception before, unchanged semantics with unavailable diagnostic after.

The original G5 verdict and separate n018 result remain historical authorities. Phase G stays in progress; G6 remains blocked. The V1 recommendation is carried forward from the completed review, not newly designed or executed here. Further implementation/design/live execution needs separate authorization.
