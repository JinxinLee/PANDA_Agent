# G5 D1 Diagnostic-Metadata Robustness Repair Design

## 1. Status and scope

**Design: PASS / COMPLETE / IMPLEMENTATION_READY. Implementation and empirical recovery: NOT_ESTABLISHED.** This document specifies a future narrow production repair. No source, prompt, schema, configuration, test, dataset, Gold, calibration, dependency, or runtime mode is changed here. No test or scientific call is executed.

Starting HEAD is `7326950d8531e53898910e9db5a2ee3fb39f34e1`. Product lineage remains `047201166057edd9859292a1760bc2e9bbf173a2`, normal mode `production_answer_obligations_v1`. See [the integrated failure-family review](G5_INTEGRATED_FAILURE_FAMILY_REVIEW.md) for case attribution and the separate post-D1 recommendation.

The original G5 remains **INCOMPLETE / PRODUCT ERROR**. Separate n018 completed once without this exception but was a false insufficiency; it is mixed-provenance diagnostic evidence, not an original-run replacement or proof of repair. D1 isolation alone cannot establish G5 readiness, fresh generalization, or G6 entry.

## 2. Observed failure and architecture

Original n018's recorded nonretryable error rejects `ambiguity.status="none"` against `_Ambiguity.status: Literal["clear", "ambiguous"]`. This occurs in `QuestionDecomposer.decompose`, before retrieval/QA graph execution. The failed record stores the exception but not the raw semantic proposal or a canonical point inventory. The exception identifies a reachable robustness defect; it does not prove all other fields were valid.

Current `src/panda_agent/question_decomposition.py` has:

- Strict `_Point` and `_Ambiguity` models; strict `_Proposal` for shadow compatibility.
- A production provider schema with `points` and `ambiguity` required, and ambiguity status typed only as a string. Provider acceptance therefore does not enforce the local two-value literal.
- Production envelope equality with `{"points", "ambiguity"}`, followed by point-count validation and `_Ambiguity.model_validate(raw["ambiguity"])` before semantic point/relation validation.
- Independent strict point/relation shape, question-substring provenance, duplicate, bound, ordering, and host-ID checks.
- Optional facet metadata already isolated via `_Point.diagnostic_facet_only`; unsupported diagnostic relation types are omitted, without discarding semantic relations.

`qa.py::_run_detailed` passes only `decomposition["points"]` as the canonical semantic inventory into the graph. `decomposition["ambiguity"]` is emitted as diagnostics after execution. Static inspection finds no ambiguity-status consumer governing retrieval, admission, claims, coverage, revision, or finalization. This makes local diagnostic isolation an owning-layer correction. It is not a generic structured-output recovery policy.

## 3. Selected rule

```text
Production authoritative points / required_relations / support provenance:
    validate exactly as today; fail closed.
Optional production ambiguity diagnostic:
    preserve a strictly valid object;
    otherwise return {"status": "unavailable", "reason": ""}.
```

`unavailable` means the host did not obtain a usable diagnostic. It does not mean clear, ambiguous, answered, complete, or evidence sufficient. An empty reason avoids inventing a diagnosis or exposing an invalid provider object as authoritative metadata. Do not normalize `none` into `clear`; do not coerce any field.

This is production-only. Keep `_Ambiguity`, `_Proposal`, shadow validation, provider-facing schemas/prompts, and declared prompt/schema versions unchanged. The host-produced diagnostic return already uses `dict[str, Any]`; the new sentinel is confined to this nonsemantic sink. Provider output is still asked to supply the existing two-field diagnostic. Missing diagnostic acceptance is a host tolerance, not an expanded provider contract.

## 4. Implementation plan, not executed

### 4.1 Production envelope

In `QuestionDecomposer.decompose(..., relation_aware=True)`, replace exact two-key equality with these conditions:

1. Root must be a dictionary.
2. `points` must exist.
3. Root keys must be a subset of `{"points", "ambiguity"}`; all foreign top-level fields still fail.
4. Point inventory remains a list with 1-5 entries.

The only newly tolerated envelope omission is `ambiguity`. Do not treat absent `points` as empty/default; do not filter foreign keys; do not accept a nonobject root.

### 4.2 Semantic validation first

Retain the existing production point/relation loop, normalization, sorting, and host-ID assignment. Remove early production `_Ambiguity.model_validate`. Only after the semantic inventory is fully validated and canonicalized, interpret `raw.get("ambiguity")` with the private diagnostic helper. The shadow branch continues using strict `_Proposal` and its existing ambiguity object.

Do not surround decompose, generate_json, the semantic loop, or graph execution with a fallback exception handler. A malformed inventory must still throw even when its diagnostic is malformed. Semantic-first ordering deliberately ensures diagnostic tolerance cannot conceal a semantic error.

### 4.3 Single local helper

Proposed private helper in the same module, with a narrowly scoped Pydantic `ValidationError` import:

```python
# Design sketch; not implemented by this task.
def _production_diagnostic_ambiguity(value: Any) -> dict[str, str]:
    try:
        validated = _Ambiguity.model_validate(value)
    except ValidationError:
        return {"status": "unavailable", "reason": ""}
    return validated.model_dump()
```

The catch applies only to validating this diagnostic object. It cannot catch `_Point` errors, host semantic `ValueError`, provider transport/JSON errors, or downstream failures. Do not catch arbitrary exceptions or add generic JSON sanitization. Every fallback returns a fresh dictionary; the input proposal and metadata are not mutated.

At return assembly, production emits the helper's dictionary; shadow emits its existing `ambiguity.model_dump()`. A small local variable change suffices; no separate runtime abstraction or mode is needed.

### 4.4 Diagnostic decision table

| Production diagnostic input, with otherwise valid semantics | Host output | Reason |
|---|---|---|
| `{"status":"clear","reason":"..."}` | Same validated fields | Preserve existing valid behavior |
| `{"status":"ambiguous","reason":"..."}` | Same validated fields | Diagnostic ambiguity remains nonsemantic |
| `{"status":"none","reason":"..."}` or unknown status | `unavailable`, empty reason | No invented interpretation |
| Missing `ambiguity`, null, scalar, list | `unavailable`, empty reason | Object unavailable/unusable |
| Missing status/reason, wrong field type, extra diagnostic field | `unavailable`, empty reason | Reject whole diagnostic locally; do not selectively repair it |
| Nonobject root, unknown top-level field, or invalid semantic inventory | Error | Outside diagnostic fallback authority |

Handling other malformed diagnostic shapes follows one existing strict-model validation rule, not a list of provider-specific special cases. No raw error payload, new receipt, counter, log, retry, or additional model call is required; existing diagnostics display the sentinel.

## 5. Semantic invariants retained

The future implementation must preserve these current enforced rules:

- Points: list of 1-5; required text/support/required_relations fields; allowed optional facet; unknown fields and model-authored IDs rejected; strict text/span types and nonempty list; nonblank normalized unique text; each support span an exact nonempty raw-question substring.
- Relations: required list per production point, including valid empty lists; at most 3 per point and 10 per question; required text/support; only allowed optional diagnostic relation type; unknown fields/model-authored IDs rejected; normalized text length 1-240; 1-3 exact nonempty raw-question support spans; normalized relation text globally unique across parents.
- Existing de-duplication/order of spans, canonical point/relation ordering, and host-assigned `point.N`/`point.N.rel.M` IDs remain unchanged. No truncation, default semantic point, inferred relation, or repaired provenance.
- Relation-free points retain ordinary completeness; relation-bearing points retain the single required-relation completeness path. No additional ordinary check can create a second completeness authority.
- Canonical parent/ID validation at the downstream boundary, target-local revision authorization, and full-contract V2 remain unchanged.

Be precise about current limitations: decomposer point and relation spans are each checked against the raw question; relation spans are not currently required to be a subset of their parent's spans. Literal substring checks do not prove semantic entailment. This repair neither invents a new containment rule nor weakens existing cross-parent duplicate/ID enforcement. Test locally enforced authority rules as they exist; do not claim stronger semantic validation from this metadata repair.

Unsupported optional facet/relation-type handling stays as implemented. The repair does not generalize that handling to point text, required relations, supporting evidence, or provider responses elsewhere.

## 6. Proposed deterministic verification

These tests are implementation requirements for a future separately authorized task. **None ran in this review/design.** Use neutral synthetic questions and existing scripted/fake provider helpers. Do not encode n018's domain phrases, expected answer, source paths, or Gold points as runtime rules.

Primary ownership: `tests/unit/test_question_decomposition.py`. Reuse existing relation/boundary fixtures in `tests/unit/test_g1_relationship_obligations.py`; add only missing paired controls. A small fake normal-QA integration test belongs in the existing directly relevant QA/G1 test module. No full suite or live call is implied.

| ID | Input / check | Required observation |
|---|---|---|
| D1-DM-1 RED -> GREEN | Valid points and relation; `status="none"` | Unchanged source initially fails at metadata validation; after implementation succeeds with identical canonical points, IDs, relation IDs, text, spans, order and `unavailable` diagnostic |
| D1-DM-2 | Valid clear and ambiguous objects | Exactly preserve current diagnostic fields and semantic output; no invented default |
| D1-DM-3 | Same valid semantic fixture with missing/null/nonobject/missing-field/wrong-type/unknown/extra-field diagnostics | All use the one `unavailable` rule; input remains unchanged; no coercion |
| D1-DM-4 | Missing points, empty/6-point inventory, nonlist points; root nonobject/foreign field | Still error, paired with invalid diagnostic; no empty-success result |
| D1-DM-5 | Wrong text type/blank text; malformed/empty spans; nonliteral/blank/case-changed question provenance; unknown point key/model ID | Still error with invalid diagnostic; existing canonical duplicate rules unchanged |
| D1-DM-6 | Missing/nonlist required_relations; malformed relation object/type/text; empty/nonliteral/too-many spans; 4 relations per point, 11 total; foreign key/model ID | Still error with invalid diagnostic; exactly 3 per point and 10 total remain accepted when otherwise valid |
| D1-DM-7 | Duplicate normalized point text; duplicate normalized relation text within/across parents; forged downstream parent/relation ID | Existing local errors retained; invalid diagnostic cannot grant authority; no new span-containment assertion |
| D1-DM-8 | Multiple out-of-order points/relations, duplicate literal spans, optional diagnostic facet/type | Compare authoritative output to valid-diagnostic baseline; preserve current normalization and diagnostic-only optional-field behavior |
| D1-DM-9 | Normal production fake QA with valid inventory and invalid diagnostic | Decompose continues into existing graph; semantic input equal to baseline; ambiguity unavailable only in diagnostics; one decomposer generate_json call, no fallback retry/extra call |
| D1-DM-10 | Shadow invalid ambiguity and existing legacy bypass; provider transport/JSON failure; semantic failure before graph | Shadow still rejects invalid ambiguity; legacy unchanged; provider failures propagate; malformed semantics never invoke graph |
| D1-DM-11 | Valid decomposition followed by malformed coverage review | Existing fail-closed coverage/G2 behavior unchanged; unavailable ambiguity cannot mark needs complete or alter claims/revision/finalization |

For RED evidence, run the single neutral D1-DM-1 reproduction before the source edit; then run the focused controls after the edit. Verify no duplicate provider invocation on fallback and no swallowing of unrelated errors. Existing clear/ambiguous and G1 canonical bounds are regression controls. Stop after proportionate deterministic verification; further scientific evaluation is a separately authorized task.

No assertion should equate a successful decomposition with QA success, force a final answered status, or use Gold as canonical obligation authority. No test should assert the original n018 proposal is otherwise valid, since it was not stored.

## 7. Identity and delivery implications

Future source ownership is limited to production diagnostic extraction in `src/panda_agent/question_decomposition.py`, its focused tests, and required current-state documentation. No `qa.py` behavior change is selected. If integration inspection discovers an actual ambiguity control-flow consumer, reassess that concrete dependency before implementing the sentinel; do not add speculative machinery now.

Keep `_Ambiguity` and provider schemas/prompts unchanged. Consequently the current `evaluation_runner.prompt_fingerprint()` payload remains unchanged: it fingerprints active decomposition prompt/schema/version plus other model contracts, not this local helper's source. The future normal Git implementation commit supplies changed product-behavior lineage. Do not claim source behavior is frozen by an unchanged prompt fingerprint, add a new version layer, or regenerate manifests/hashes merely for this design.

Acceptance scope for future implementation is **diagnostic isolation with semantic fail-closed regression controls**. Empirical provider quality, original n018 recovery, refusal reduction, and integrated readiness remain unestablished until separately authorized verification. A passing focused test must not change the original G5 verdict.

## 8. Lifecycle, cost, and next boundary

```text
G5_D1_REPAIR_DESIGN = COMPLETE / IMPLEMENTATION_READY
DESIGN_VERDICT = PASS
PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
DEPENDENCY_CHANGE = false
NEW_RUNTIME_MODE = false
QA_RUNS = 0
RETRIEVAL_RUNS = 0
SCIENTIFIC_GENERATION_CALLS = 0
SCIENTIFIC_EMBEDDING_CALLS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
TEST_EXECUTIONS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = G5 D1 DIAGNOSTIC-METADATA ROBUSTNESS REPAIR IMPLEMENTATION
POST_D1_REPAIR_DESIGN_RECOMMENDATION = G5 V1 DISPOSITION-PROVENANCE FALSE-INSUFFICIENCY REPAIR DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

Limitations: both raw stores were available, but the original failed semantic proposal was never saved. Metadata fallback intercepts one observed class, without guaranteed semantic or final-answer recovery. Other G5 retrieval, generation, verifier-provenance, identifier, and Gold-scope limitations remain as reviewed. Phase G remains in progress; no G6, rerun, implementation, or protected-data execution follows automatically.
