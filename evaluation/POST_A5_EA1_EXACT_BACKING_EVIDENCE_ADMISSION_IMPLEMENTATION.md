# POST-A5 EA1 Exact-Backing Evidence-Admission Implementation

Verdict: **PASS** for deterministic implementation gates only.

EA1 = IMPLEMENTED / DETERMINISTICALLY VERIFIED / MATERIAL PRODUCT CHANGE / SCIENTIFIC EFFECT NOT YET EVALUATED.
O1 remains IMPLEMENTED / DETERMINISTICALLY VERIFIED / BEHAVIOR_NEUTRAL.
C1 remains DESIGN_COMPLETE / NOT_IMPLEMENTED / NOT_AUTHORIZED. RS remains DEFER.

## Identity and delivery

- Starting HEAD: `81b1308d6c0fa03c7f83894af851fd71b4503f41` (clean at start).
- Final implementation HEAD: `60dff40a671e62bffcbe0eb82d38ea6e9aeb05c4`.
- Previous product behavior lineage: `e79d3232ed132a224cbceaf3524e19a1406bd648`.
- New/current product behavior lineage: `60dff40a671e62bffcbe0eb82d38ea6e9aeb05c4`.
- One focused source/test implementation commit, followed by documentation-only closeout binding its actual SHA. No amend, push, candidate freeze, or new digest contract.

Changed files:
- `src/panda_agent/qa.py`
- `src/panda_agent/storage.py`
- `tests/unit/test_post_a5_ea1_exact_backing.py`
- `evaluation/POST_A5_EA1_EXACT_BACKING_EVIDENCE_ADMISSION_IMPLEMENTATION.md`
- `evaluation/post_a5_ea1_exact_backing_evidence_admission_implementation.json`
- `docs/EVALUATION_STATUS.md`
- `docs/GENERALIZATION_ROADMAP.md`

## Implemented contract

1. Retain directly citation-eligible selected evidence; rejected Sphinx pages remain ineligible.
2. Read locked web manifest at most once and perform one bounded storage lookup per QA invocation.
3. Validate persisted page identity and manifest source/version/snapshot/date/path/URL against the selected evidence.
4. Accept only real direct sphinx_section children with matching provenance and valid existing citation locator.
5. Require entire nonempty child text exactly once as a case-sensitive contiguous substring, including rejection of overlapping repeated occurrences.
6. Exactly one qualifying child resolves; zero or multiple candidates retain strict exclusion.
7. Reuse matching eligible already-selected child at its original position; otherwise insert actual child admission at excluded parent slot.
8. Invocation-local cache shared by A0/A1, verifier/finalizer, and O1; no page-to-child citation substitution.

Normal Evidence projection uses the real child's ID/source/version/text/locator/authority, `stable_id(child_id, "ea_exact_backing", prefix="evidence")`, `retrieval_channels=["ea_exact_backing"]`, and score 0.0. These are structural provenance, not ranking. Selected Evidence does not carry object_type/snapshot metadata in its public DTO; those fields are established from the exact persisted object and locked manifest. If supplied in a selected payload, conflicting metadata/type is rejected.

## Storage and bounds

Read-only repeatable-read transaction; SET LOCAL timeout. Exact page ID batch ordered with LIMIT 4; lateral child batch constrained by source/version/type/direct-parent metadata, ordered LIMIT 17 per page. Returned text capped at 12000 with full char_length for rejection. Transaction control statements are separate from the two SELECTs. Existing columns and restore_object_parent reused; no migration or whole-table loader.

| Bound | Implemented value |
| --- | --- |
| Candidate pages per execution | 4; >4 resolves none |
| Children inspected per page | 16 |
| Rows returned per page | At most 17, to detect overflow and reject the page |
| Added backing objects | At most 4 |
| Accepted child text | At most 12,000 characters |
| Transaction-local statement timeout | 1,000 ms |
| Structural SELECTs | At most 2 |
| Retries / pagination | 0 / 0 |
| EA manifest parse / backing lookup | At most once per invocation |

There is no Qdrant, embedding, ranking, ingestion, migration, full object loader, or semantic search in this reader. Failure is local and cached; existing independent infrastructure failures retain their existing behavior.

Reason codes: `DIRECTLY_CITATION_ELIGIBLE`, `RESOLVED_EXACT_BACKING`, `NO_VALID_BACKING`, `VERSION_MISMATCH`, `CONTENT_RELATION_NOT_ESTABLISHED`, `INVALID_LOCATOR`, `AMBIGUOUS_BACKING`, `BOUND_EXCEEDED`, `LOOKUP_FAILED`.

Zero valid children has page reason NO_VALID_BACKING; candidate_rejections retains specific VERSION_MISMATCH/INVALID_LOCATOR/content/bound reasons. Resolved decisions record both identities and half-open containment offsets.

## Integration and invariants

- A0/A1 use the same private admission projection. The full-graph fixture forces one revision; only one EA manifest read and one backing lookup occur per invocation.
- V1/V2 preserve visibility of original selected evidence and recognize real backing IDs. Parent, unknown-ID, existing code-version, and unsupported-claim rejection remain effective. Child version checks occur before admission; semantic entailment remains the existing verifier's responsibility.
- Final public evidence contains the actual backing child cited by supported claims; no parent-to-child citation rewriting.
- Selected bundle/rankings/fusion scores/IDs stay deeply equal. The actual RetrievalTrace remains equal and names the original page. One fake semantic retrieval, zero fake embeddings, and the existing six-stage revision/composition flow remain unchanged.
- O1 merges admission reasons and provenance into its existing bounded trace while preserving prior fields. Trace OFF/ON produces equal results, non-trace diagnostics, model payload/schema/system instructions, usage and retrieval counts under EA1.
- E3 `runtime_e1_v2` keeps its existing strict admission and retained-support contract. It is deliberately outside this bounded EA1 resolver.
- Prompt, coverage schema/semantics, public DTO, evaluator, Gold, calibration, identifier normalization and retrieval source remain unchanged.

## RED / GREEN and focused regression evidence

Commands use `PYTHONPATH=src`; no network/model/database service was invoked.

- Legitimate initial RED: `test_unique_exact_backing_and_cache` failed once because `QAAgent._admitted_evidence` did not exist.
- GREEN: `python -m pytest tests/unit/test_post_a5_ea1_exact_backing.py -q`: **52 passed**. Covers T0-A through T0-Q with synthetic objects, manifests, fake SQL and fake model responses.
- O1: **33 passed** (initial combined EA1/O1 green was 77 tests; eight additional EA1 boundary cases subsequently passed).
- Focused historical regression batch: **332 passed, 49 subtests passed, 4 pre-existing failures**. Files: `test_e2_a3_r2_citation_eligibility.py`, `test_e2_a3_r1_identifier_normalization.py`, `test_qa.py`, `test_e2_a1_answer_point_coverage.py`, `test_generic_answer_obligation_completeness.py`, `test_post_a5_generic_product_repair.py`, `test_evaluation_runner.py`, `test_f6_release_identity.py`, `test_evaluation_cli.py`.
- Parent persistence + E3: **62 passed**.
- Extended full-graph RetrievalTrace equality assertion: **1 passed**, already included among the 52 EA1 cases; not an additional distinct case.
- Static checks: strict predicate and coverage-helper ASTs unchanged; prompt fingerprint unchanged; reviewed complete source diff; `git diff --check` passed.

Unrelated failures, reproduced at starting HEAD without modifying the checkout:
- test_e2_a3_r2_citation_eligibility.py::test_answer_revision_auxiliary_mapping_and_original_bundle: obsolete fixture lacks generation_vertex
- test_e2_a3_r2_citation_eligibility.py::test_complete_frozen_reconciliation_and_exact_scope: same obsolete fixture
- test_e2_a3_r1_identifier_normalization.py::test_complete_frozen_repaired_code_scan: extracted verifier loop lacks _CODE_DATA_EXTENSIONS in its execution environment
- test_evaluation_runner.py::EvaluationRunnerTests::test_v26_is_default_and_signed_dry_rescore_preserves_real_failures: v2_6 expectation versus existing v2_11 default

Baseline isolation loaded starting-HEAD QA code in-process for runtime failures and separately substituted starting-HEAD source for the R1 AST scanner. Existing evaluator default code is unchanged. Frozen historical tests/artifacts were not repaired.

## Historical safety mapping and success gates

| Safety gate | Evidence |
| --- | --- |
| S1 | unchanged strict predicate and historical predicate tests |
| S2 | A0 receives real backing only; parent remains excluded |
| S3 | same cached A0/A1 projection, full graph revision test |
| S4 | normal verifier rejects parent and unknown IDs, no substitution |
| S8 | direct selected child identity and ordering unchanged |
| S9 | non-Sphinx code evidence unchanged |
| S10 | bundle/rankings deep equality; original-page RetrievalTrace; one semantic retrieve and zero embeddings |
| S11 | identifier normalization source unchanged; applicable old identifier tests pass |
| S12 | prompt fingerprint/public schemas/evaluator sources unchanged |

EA1-G1 through EA1-G15: PASS within the deterministic scope above. Four isolated obsolete tests are not presented as passing. No scientific acceptance is inferred.

## Materiality, usage and preserved lifecycle

SOURCE_CHANGE = true
MATERIAL_PRODUCT_BEHAVIOR_CHANGE = true
MATERIAL_PRODUCT_CHANGE = true
PROMPT_FINGERPRINT_CHANGE = false
PUBLIC_DTO_CHANGE = false
EVALUATOR_CONTRACT_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false

Prompt fingerprint before and after: `0a5b2909ef586671d533148979fc681c64e37528ad53781a4566cb9044835ba2`.

New scientific calls/tokens: **0 / 0**. Fake client usage counters are synthetic test data, not scientific cost. No before/after scientific metrics were collected.

Historical T1 stays **COMPLETE / FAIL**, **65 calls / 373,265 tokens**. No replay, rescoring, or backfill. No claim that g013/g023 are fixed.

novel_validation = PRISTINE_FOR_CURRENT_LINEAGE; holdout access = 0; protected-content leakage = 0; F6-B execution = 0. No protected content was accessed.

Candidate frozen = false; Attempt 6 preregistered = false; Attempt 6 executed = false; ATTEMPT_6_READINESS = NOT_READY.

## Limitations and next recommendation

- Scientific effectiveness not evaluated; no claim that g013/g023 are fixed.
- Fake SQL contract tests only; no live PostgreSQL execution, timeout timing, or query-plan measurement. Query constrains source/version/type/parent, uses existing source index eligibility and statement timeout; physical planner choice not certified.
- Statement timeout does not impose a connection establishment deadline; Storage.connect is unchanged.
- Conservative ambiguity and text bounds can exclude useful pages; no normalization or semantic choice.
- Experimental runtime_e1_v2/E3 retains strict admission and existing retained-support policy; EA1 does not resolve retained evidence or change E3.
- Four unrelated stale historical tests remain failing; applicable deterministic checks pass.

NEXT_TASK_RECOMMENDATION = POST-A5 C1 BOUNDED COVERAGE-COMPLETENESS IMPLEMENTATION
NEXT_TASK_EXECUTION_AUTHORIZED = false
