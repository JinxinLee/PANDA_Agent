# G5 D1 Relation-Extraction Boundary Repair Design

## 1. Status and scope

**COMPLETE / PASS / D1_RELATION_EXTRACTION_AND_QUALIFIER_PRESERVATION_CLARIFICATION**. Select B2, outcome C. `IMPLEMENTATION_READY = true` means a bounded future implementation is specified; no implementation or empirical recovery is claimed.

This task is static design, source/fixture inspection and documentation only. Entry HEAD is `c7d9871ef1e6fa52bda171e176bdcb1f87c73e1d`, parent `30f726cbe67a2f6461b993e34dfb7f32010518d7`, message `Correct n023 D1 completeness attribution`; the entry working tree was clean. The delivery commit adds this design and updates only the current sections of the two state documents. Its exact SHA is reported on delivery, avoiding a self-referential commit identity.

Current product identity remains:

```text
CURRENT_PRODUCT_BEHAVIOR_LINEAGE_HEAD = 5b9588ec552deb91a59a8176d6ce0429c2133b1e
PROMPT_SET_VERSION = 3.12.1
PROMPT_FINGERPRINT = 08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc
QUESTION_DECOMPOSITION_PROMPT_VERSION = 3.0.0
QUESTION_DECOMPOSITION_SCHEMA_VERSION = e1.question_decomposition.v3
COVERAGE_SATISFACTION_SCHEMA_VERSION = coverage-satisfaction-v2
NORMAL_PRODUCT_MODE = production_answer_obligations_v1
```

## 2. Authorities

- [Corrected coarse-completeness design](G5_COARSE_COMPLETENESS_OVERACCEPTANCE_REPAIR_SURFACE_DESIGN.md): frozen n023 attribution, quoted exposed decomposition and downstream interpretation; it is not rewritten.
- [G1 architectural design](G1_RELATIONSHIP_AWARE_ANSWER_OBLIGATION_DESIGN.md), sections 4–9: one completeness path, question-derived relation semantics, bounds and propagation.
- [Current D1 source](../src/panda_agent/question_decomposition.py): actual production/v2 prompt separation, schema and normalizer.
- [Current prompt-set identity](../src/panda_agent/prompts.py) and [`prompt_fingerprint()`](../src/panda_agent/evaluation_runner.py): actual version and canonical identity coverage.
- [D1 fixtures](../tests/unit/test_question_decomposition.py), [generic obligation fixtures](../tests/unit/test_generic_answer_obligation_completeness.py), [G1 fixtures](../tests/unit/test_g1_relationship_obligations.py) and [identity fixtures](../tests/unit/test_f6_release_identity.py): inspected as source, never executed.
- [V1 implementation identity precedent](G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_IMPLEMENTATION.md): prompt-only clarification advanced the global patch version and canonical fingerprint.
- [Evaluation status](../docs/EVALUATION_STATUS.md), [roadmap](../docs/GENERALIZATION_ROADMAP.md), repository instructions and the explicit task attachment define the authorization boundary.

This is a forward design using the corrected exposed finding, not a new case audit. No new raw-run replay, outcome collection, protected search or evaluation is needed to decide the representation boundary.

## 3. Corrected n023 failure mechanism

The exposed request asks where the FTS track finder is implemented and **which track branches it writes out**. The second D1 point retained `Identify which track branches the FTS track finder writes out.` but incorrectly carried a canonical required relation, `The FTS track finder writes out track branches.` The exact support was `which track branches does it write out?`.

There are two linked errors in this one boundary failure: ordinary output enumeration entered the relation path, and its authoritative relation text weakened an identity-set request into an existence/category statement. The original point's `which` wording cannot restore an independent ordinary completeness obligation after that routing decision. V1 subsequently accepted the weakened canonical relation. This supports the frozen downstream-contributor finding; it does not establish an independent V1 error against a correctly extracted relation.

```text
N023_D1_CLASSIFICATION = D1_REQUIRED_RELATION_SEMANTIC_DEFECT / RELATION_OVEREXTRACTION
N023_FIRST_WRONG_STAGE = D1_RELATION_EXTRACTION_BOUNDARY / REQUIRED_RELATION_SEMANTIC_NORMALIZATION
N023_FIRST_WRONG_SEMANTIC_DECISION = D1_RELATION_OVEREXTRACTION / ORDINARY_ENUMERATION_MISCLASSIFIED_AS_RELATION
N023_V1_CANONICAL_OVERACCEPTANCE = DOWNSTREAM_CONTRIBUTOR / INDEPENDENT_V1_ERROR_NOT_ESTABLISHED
D1_RELATION_EXTRACTION_BOUNDARY_GAP = ESTABLISHED
D1_RELATION_SEMANTICS_PROMPT_GAP = NOT_ESTABLISHED
COMMON_D1_DEFECT = false
COMMON_D1_GRANULARITY_DEFECT = false
```

## 4. Current G1 and D1 contract

G1 section 4 states exactly:

> For a relation-bearing point, the canonical required relations carry its requested semantics, including any explanation intrinsic to the relation; there is no additional ordinary-content obligation.

It also states:

> Context retained in a relation-bearing `point.text` does not create another completeness obligation.

G1 section 5 states:

> Definitions, implementation locators and argument-list requests remain ordinary point content even though their grammar can be described relationally. Extract a required relation when the user asks to establish a connection, relative placement, or other relationship itself; do not mechanically convert every verb, property or API parameter into an edge.

The current production extension in `question_decomposition.py` says exactly:

```text
Production relationship-aware contract: every point must include required_relations,
an explicit empty list for ordinary definitions, locators, API arguments, and
unstructured explanations. Extract a relation only when the user asks to
establish a connection, relative placement, ordering, dependency, input/output,
cause/effect, comparison, or containment. Do not invent an edge from a verb,
property, evidence, or domain workflow knowledge. Preserve direction, negation,
modality, endpoints, and the requested explanation in each relation's text.
A question asking whether a relation holds requests an answer, not a positive
assertion: a grounded negative answer can satisfy it. Copy 1–3 literal nonempty
support spans from the raw question for each relation. Do not generate point or
relation IDs. relation_type is optional diagnostic metadata only. Split ordinary
and relational requests into separate points when either could be omitted while
answering the other. One relational explanation is not a second ordinary point.
Return no unsupported inferred relationship or hidden intermediate stage.
```

The generic prohibition against inventing edges is sound. The actionable ambiguity is how to distinguish a requested output/property **inventory** from the listed positive relation categories `input/output` and `containment`. The extension does not explicitly state that ordinary list membership remains ordinary, or name identity/count preservation inside genuine relations. The clarification below makes the classification operation explicit rather than merely repeating the prohibition. It is a justified instruction improvement, not proof that any prompt makes provider variance impossible.

## 5. Ordinary property and list semantics

**Ordinary invariant:** A request for an anchor's properties, values or item identities remains ordinary when the requested answer does not itself establish a relationship among independently relevant participants; preserve the requested list, identities or count in `point.text` and use `required_relations=[]`.

Outputs, fields, branches, extensions, methods, files and arguments can all be ordinary inventory requests. `write`, `produce`, `define`, `expose`, `contain` or `accept` does not turn an inventory into a canonical relation. Likewise, several named items can be independent ordinary targets rather than a relationship. The rule concerns the information requested, not the number of verbs, nouns, proper names or clauses.

Ordinary does not mean a weaker completeness obligation. A question asking which values exist still requires the requested identities under the existing ordinary C1 contract; a generic statement that values exist does not satisfy it. No `answer_requirements_v2`, new list schema or downstream semantic guard is introduced.

## 6. Genuine relation semantics

**Relation invariant:** Extract a canonical relation only when the requested answer is a connection, relative placement, ordering, dependency, flow, causal relation, comparison or containment among independently relevant participants, preserving the complete question-derived request in `relation.text`.

Participants may be named, described, pronominal, clause-valued or themselves unknown and requested by the question. This is not a requirement for exactly two proper nouns or even two explicitly named endpoints. For example, `Which stage feeds Birch?` requests the identity of a participant in a specified flow relation. `Compare Cedar, Birch and Maple` remains a comparison. `Where is Cedar implemented?` remains an ordinary locator despite mentioning an object and an unknown location.

Ordering, dependence, workflow placement, input/output handoff, cause/effect, comparison and composition/containment remain supported. `Why does Cedar stop?` is ordinary explanation without an invented cause participant; `Does Cedar cause Birch?` asks about a causal relation. `Which fields does Birch contain?` asks for an inventory; `Is Cedar contained in Birch?` asks whether a specified containment holds. `How is Maple composed from Cedar and Birch?` asks for composition. These distinctions require semantic judgment from the decomposer, not host token matching.

## 7. Input/output ambiguity

| Request | Intended path and complete target |
|---|---|
| Which outputs does Cedar write? | Ordinary: identify Cedar's requested outputs. |
| Which fields does Birch contain? | Ordinary: identify Birch's requested fields. |
| Which extensions does Maple define? | Ordinary: identify Maple's requested extensions. |
| How does Cedar feed Birch? | Relation: explain the requested handoff from Cedar to Birch. |
| How does Cedar output become Birch input? | Relation: explain the requested source-to-consumer transition. |
| Which outputs from Cedar are consumed by Birch? | Relation: identify the outputs participating in that specified consumption relation. |
| Which outputs does Cedar write, and how does Birch consume them? | Two points: ordinary output inventory and relational consumption explanation. |

The third participant need not be named: `How does Cedar feed the next stage?` can express a relation with a descriptive endpoint. Conversely, a list's unnamed elements do not automatically become independent relation endpoints. The requested predicate and answer scope decide which of the two invariants applies.

## 8. Mixed requests and point granularity

For `Which outputs does Cedar write, and how does Birch consume them?`, use:

1. Ordinary point: `Identify which outputs Cedar writes.`; no required relations.
2. Relational point: `Explain how Birch consumes the outputs written by Cedar.`; a canonical relation with that entire explanation request.

Copy literal question spans for each proposal. The relational point may use multiple exact spans to support the source of `them`; do not manufacture a paraphrase as a support span. Either the complete inventory or the consumption explanation can be omitted while answering the other, so the existing independently-omittable rule justifies two points. No duplicate ordinary explanation is added to the relation-bearing point.

`How does Cedar produce input for Birch?` stays one relational explanation. `Which outputs from Cedar are consumed by Birch?` stays one relation asking for the participating subset. Neither requires an extra ordinary point that asks the same question again. Retain existing 1–5 point bounds and fail explicitly on unrepresentable requests rather than silently dropping obligations.

## 9. Genuine relations with identity-set or quantifier qualifiers

For `Which outputs from Cedar are consumed by Birch?`, the canonical relation should say `Identify which outputs from Cedar are consumed by Birch.` It must not become `Cedar outputs are consumed by Birch.` A correct `point.text` alone is insufficient because canonical relations own completeness.

Preserve identities, requested subset, count, stage/item selection and applicable scope, not necessarily the original interrogative token. Thus `which`, `which ones`, `how many` and `which stage` remain semantically specific after paraphrase. `How many Cedar outputs does Birch consume?` requires a count; `Which stage feeds Birch?` requires identifying the source stage; `Which of Cedar and Birch runs first?` requires the requested ordering selection. Do not insert a numerical answer or invent a stage during D1.

This is a safety invariant for retaining legitimate relations while narrowing extraction. It follows existing G1 full-request ownership and does not upgrade `D1_RELATION_SEMANTICS_PROMPT_GAP = NOT_ESTABLISHED` into a second empirically established defect. n023 is not evidence of failure on a legitimately relational identity-set request.

## 10. Intended n023 shape

The intended correction uses the existing two independently omittable points. Their semantic shape is:

```json
[
  {
    "text": "Identify where in the PandaRoot source tree the FTS track finder is implemented.",
    "required_relations": []
  },
  {
    "text": "Identify which track branches the FTS track finder writes out.",
    "required_relations": []
  }
]
```

This is an illustrative projection, not a complete provider payload or a replacement historical artifact. The full proposal still needs exact raw-question support and the existing envelope; the host assigns IDs. The implementation locator and requested output identities remain ordinary. The design prevents the specified contract error of converting output enumeration into a weaker existence relation; real-provider prevention is not yet demonstrated.

No branch identities, paths, expected answers or case-specific tokens belong in production prompt examples or new fixtures. Correct routing does not supply missing selected evidence, prove that ordinary V1 checks will be complete, or guarantee final-answer recovery. The corrected historical report and all raw bytes stay unchanged.

## 11. n006 consistency control

The n006 extension-value enumeration is ordinary under the same rule: asking which extensions an anchor defines does not request a connection between independent participants. Preserve `N006_D1_CLASSIFICATION = D1_SUFFICIENT` and `N019_D1_CLASSIFICATION = D1_SUFFICIENT`; their frozen selected-evidence and ordinary V1 limitations are not reclassified as D1 errors.

The n006 control establishes consistency of the design interpretation, not a rerun or a new finding. Neutral `Which extensions does Maple define?` is the future contract fixture. Do not copy n006 identifiers, answers, source quotas or selected evidence into implementation. Neither n006 nor n019 is reopened for analysis or repair here.

## 12. Existing neutral fixture coverage and exact hole

| Inspected fixture seam | What it currently establishes | Remaining hole |
|---|---|---|
| `test_question_decomposition.py::test_synthetic_obligation_proposals_preserved_without_taxonomy` | Scripted locator/contribution/comparison/flow point text survives; this helper uses the v2 profile. | Does not exercise production ordinary-versus-relation classification or the requested list cases. |
| `test_normalizer_does_not_invent_semantic_splits_from_cue_words` | Host retains a structurally valid supplied partition. | Deliberately cannot judge model atomicity or semantic boundary correctness. |
| `production_proposal()` and production diagnostic/semantic validation tests | Scripted ordering and feed relations plus a locator; normalization, IDs, strict structural rejection and diagnostic isolation. | No contrasting ordinary output/field/branch/extension inventories; no identity-qualified flow or mixed inventory/handoff example. |
| `test_generic_answer_obligation_completeness.py` T1–T6 | Fake missing-point repair/abstention, single explanation, comparison, respective targets and workflow cardinality through QA. | Expectations and decomposition are supplied by the fake; do not measure real D1 extraction or resolve list-versus-flow semantics. |
| `test_g1_relationship_obligations.py::test_neutral_question_shapes_are_supported_as_scripted_contracts` | Production representation supports relation positives for order, placement, dependence, flow, cause, comparison, containment and ordinary negatives for locator/definition/arguments/how/why. | `relation_bearing` is supplied by the test; lacks the neutral output/field/branch/extension contrast and qualifier-retention/mixed inventory controls. |
| `test_f6_release_identity.py::PromptFingerprintTests` | Existing assertions cover active D1 prompt and declared contract identity in the canonical fingerprint. | Inspect/reuse for future identity validation; no identity repair is needed in this design. |

The missing neutral fixtures are not failed tests. No test was executed, and existing fake acceptance cannot be converted into provider-semantic evidence. New production fixtures must call `decompose(..., relation_aware=True)` and explicitly import the active production prompt: the D1 test module currently aliases v2 constants to unqualified names for compatibility tests.

## 13. Candidate policies B0–B4

| Policy | Assessment | Decision |
|---|---|---|
| B0: no prompt change | Existing G1 principles already prohibit the observed outcome; provider variance remains possible. However, the actual prompt lists input/output and containment without an operational inventory contrast. Retaining that ambiguity does not address the corrected generic failure. | Reject as the next design outcome; do not claim ambiguity alone proves repeatability. |
| B1: boundary clarification | Resolves inventory versus requested relationship and keeps mixed splitting. Current text can represent all positive/negative cases. | Necessary core, but insufficient as the full repair safety specification: it must also preserve identity/count requests that remain relational. |
| B2: boundary plus qualifier preservation | Combines B1 with explicit full-request retention within genuine relations; avoids both over-extraction and over-broad removal of identity-qualified relations. | **Select. Outcome C; implementation-ready for separately authorized work.** |
| B3: structured schema | Empty/nonempty `required_relations` already expresses both paths. Kind markers or participant tuples would not determine semantic correctness and would complicate pronouns, comparisons and unknown endpoints. | No schema dependency established. |
| B4: deterministic host correction | Shape, literal spans, bounds and duplicate detection cannot establish whether an inventory or relationship was requested. | Reject semantic reclassification, keyword filters and sanitizers. |

Selection threshold is met: the corrected generic boundary defect is established; the existing representation covers all contrasts; the rule is question-derived and domain-neutral; genuine relations, mixed points and qualifiers survive; no host heuristic, Gold or protected authority is needed; section 18 gives paired future controls.

## 14. Selected boundary invariant and exact proposed prompt delta

**Single boundary rule:** Classify by the fact requested: an anchor's property/value/item inventory is ordinary unless the requested answer itself establishes a relationship among independently relevant participants; only that relationship request belongs in `required_relations`.

The ordinary and genuine-relation invariants in sections 5–6 are its two branches. Do not classify by token lists, grammatical transitivity or name count.

Proposed future edit: within the **production-only extension**, replace the block beginning `Extract a relation only when the user asks to` and ending `in each relation's text.` with the following text; retain the extension's opening empty-list rule and all subsequent negative-answer, support, ID, diagnostic, mixed-splitting and hidden-stage clauses:

```text
Classify by the information requested. A request for an anchor's properties,
values, or item identities is ordinary unless the requested answer is itself
a relationship among independently relevant participants. Extract a relation
only for that requested connection, relative placement, ordering, dependency,
input/output flow, cause/effect, comparison, or containment. Participants may
be named, described, pronominal, or themselves requested; their name count is
not a classification rule. Do not invent an edge from a verb, property,
evidence, or domain workflow knowledge.
For a genuine relation, preserve the full request in relation.text: direction,
negation, modality, endpoints, explanation, and any requested identity set,
subset, count, or participant selection. Do not weaken an identity or quantity
request into a statement that a relation exists.
For example, "Which outputs does Cedar write?" is ordinary. "How does Cedar
feed Birch?" is relational. "Which outputs from Cedar are consumed by Birch?"
is relational and must ask to identify those outputs in relation.text.
```

This adds an operational inventory-versus-connection decision and the qualifier constraint, with one small neutral contrast. It does not require a long verb/category catalogue in the runtime prompt. Keeping the shared v2 base untouched is part of the seam, not an invitation to redefine every explanation or list as a relation.

## 15. Relation qualifier invariant

```text
RELATION_IDENTITY_SET_QUALIFIER_PRESERVATION = REQUIRED
```

Every extracted genuine relation must retain the user's requested identity set, subset, count or participant selection in canonical `relation.text`, alongside existing direction, negation, modality, endpoints and explanation. A grounded negative answer can satisfy a whether-relation request; the relation text must not presuppose a positive fact. A `which`/`how many` request cannot be discharged by an existence-only statement. Exact spans document provenance; they do not repair a weakened canonical target.

Do not force exact interrogative tokens, expand the scope beyond the question, add hidden participants, or create a second ordinary check under a relation-bearing point. Optional `relation_type` and `facet_type` remain diagnostic, with no new control authority.

## 16. Schema and host decision

```text
PROMPT_CHANGE_PROPOSED = true
SCHEMA_CHANGE_REQUIRED = false
HOST_SEMANTIC_RECLASSIFICATION = NOT_JUSTIFIED
```

Keep the provider-facing points/relations/envelope shape and simple types. Preserve required explicit empty lists, 1–5 points, 0–3 relations per point, 10 total relations, normalized relation text of 1–240 characters, and 1–3 nonempty literal question support spans. Keep strict allowed fields, model-ID rejection, duplicate normalized-text rejection across parents, support-position/text ordering, host IDs and diagnostic ambiguity isolation. Overflow must fail rather than truncate, merge or silently strip relations.

A structurally valid but semantically wrong relation proposal may still pass the host. No generic structural invariant can safely convert it back to ordinary. Neither diagnostic labels nor support substring presence supplies that missing semantic authority. Do not add a regex parser, `which`/`output` filter, noun-count rule, fallback, additional model call or sanitizer.

## 17. Smallest future implementation seam and downstream invariants

Future source changes are limited to:

1. `src/panda_agent/question_decomposition.py`: the production prompt delta in section 14 and the active D1 prompt identity described in section 19. Preserve the shared v2 base, schema and normalizer.
2. `src/panda_agent/prompts.py`: the established prompt-set version update only.
3. `tests/unit/test_question_decomposition.py`: focused prompt-delivery assertions and neutral production contract fixtures from section 18. Reuse adjacent G1/identity tests; update only directly affected current identity assertions if necessary.
4. An implementation report and current-state identity documentation, only when separately authorized.

No dependency requires edits to `qa.py`, retrieval, coverage schemas, V1/A1/V2 prompts, composer or evidence eligibility. D1 remains question-only, before retrieval, with unchanged one-call decomposition geometry. A0 receives the same immutable canonical point/relation shape and existing context; new code must not infer relations from retrieved evidence or turn support spans into answer evidence.

V1 retains exactly one completeness path per point: ordinary C1 checks when the list is empty; canonical relation dispositions otherwise. Target-local A1 remains one bounded revision for authorized missing targets; V2 rechecks the full contract. No `point.text` secondary completeness axis, V1 compensation for D1 loss, or target-locality relaxation is proposed. Correct ordinary routing exposes the intended inventory to existing ordinary verification without claiming that verification is infallible.

## 18. Future RED/GREEN matrix — planned, not executed

Each row is a **neutral model-contract expectation**, not a runtime keyword rule. Supply valid raw-question support, explicit relation lists, the existing envelope and no model IDs. The fake returns the chosen proposal; assert normalized semantics, one active completeness path and stable host ownership/IDs. The full question can serve as an exact span for these short fixtures.

| ID | Neutral request | Correct production proposal | Forbidden semantic weakening / guard |
|---|---|---|---|
| R1 | Which outputs does Cedar write? | One ordinary point identifying the outputs; `[]`. | Do not substitute a `Cedar writes outputs` relation. |
| R2 | Which fields does Birch contain? | One ordinary point identifying fields; `[]`. | Do not treat field inventory as requested containment. |
| R3 | Which extensions does Maple define? | One ordinary point identifying extension values; `[]`. | Do not replace values with existence or member/getter inventory. |
| R4 | What arguments does SensorFrame accept? | One ordinary argument-list point; `[]`. | Preserve existing argument-list control. |
| R5 | How does Cedar pass data to Birch? | One point/relation explaining Cedar-to-Birch handoff. | Preserve direction and explanation, not merely two object names. |
| R6 | Does Cedar run before Birch? | One point/relation asking whether the ordering holds. | Do not require a positive ordering assertion. |
| R7 | How do Cedar and Birch differ? | One comparison point/relation. | Do not replace comparison with two unrelated descriptions. |
| R8 | Which outputs from Cedar are consumed by Birch? | One point/relation identifying the participating output subset. | Existence-only `Cedar outputs are consumed by Birch` is not the expected target. |
| R9 | Which outputs does Cedar write, and how does Birch consume them? | Two points: ordinary inventory and canonical consumption explanation. | No mixed obligations hidden in one relation; no duplicate ordinary explanation. |
| R10 | Which files does Cedar create? | One ordinary file-identity point; `[]`. | A transitive verb alone is not a relation request. |
| R11 | Why does Cedar stop? | One ordinary explanation point; `[]`. | Do not invent a causal participant or hidden relation. |
| R12 | Is Cedar contained in Birch? | One point/relation asking whether containment holds. | Field-list clarification must not erase genuine containment. |

Focused additional controls cover the precise fixture hole and boundary reversals:

- Ordinary `Which branches does Cedar write?` and `Which methods does Birch expose?`; ordinary independent multi-name locators. Avoid any PANDA symbol or expected answer.
- Genuine `How does Cedar output become Birch input?`, dependency, relative placement, cause and multi-entity comparison; a workflow explanation stays one end-to-end target with no inferred intermediate stages.
- `How many Cedar outputs does Birch consume?`, `Which stage feeds Birch?`, `Which ones does Birch consume from Cedar?`, and `Which of Cedar and Birch runs first?`: retain requested count/identity/selection in the supplied relation text.
- A descriptive/pronominal endpoint with literal contextual supports; preserve direction, negation and modality, including a whether-question permitting a grounded negative answer.
- Reuse current strict span/shape/duplicate/bounds/ID and diagnostic-isolation tests. Preserve v2 identity and semantics. No need to broaden to a full suite or run QA/retrieval to test prompt routing.

**Honest RED/GREEN procedure for the future implementation:**

1. Add a focused active-production prompt-contract/delivery assertion for the selected operational boundary and qualifier clauses. Capture its pre-edit RED because those explicit instructions are absent; do not simulate a failing provider classification or insert a fake that conditionally changes its answer when prose changes.
2. Add the matrix as fake proposal preservation/geometry tests. Many are expected to pass even before the prompt edit because the schema/normalizer already supports the correct outcome. Record that baseline honestly; these are safety controls, not demonstrated model-repair REDs.
3. Apply only the selected prompt/identity edits. The prompt assertion becomes GREEN; fake fixtures and directly neighboring structural/profile/identity controls must pass.
4. Verify active production prompt delivery, v2 stability and canonical fingerprint sensitivity. Stop after focused gates; actual provider classification and n023 recovery require separately authorized future empirical verification.

Incorrect but structurally valid semantic counterexamples are review expectations, **not** host-rejection assertions. An assertion that the current normalizer rejects R1 over-extraction or R8 qualifier loss would test an unauthorized host semantic parser. No RED/GREEN result is claimed in this design.

## 19. Version and fingerprint implications

Current source separates v2 prompt `2.0.0` / schema `e1.question_decomposition.v2` from production prompt `3.0.0` / schema `e1.question_decomposition.v3`. The shared base is captured into `QUESTION_DECOMPOSITION_V2_SYSTEM_PROMPT` before the production extension is appended. Edit only that extension.

The actual `evaluation_runner.prompt_fingerprint()` includes the global prompt-set version, active production D1 prompt, D1 prompt version, production schema version and schema, plus v2 compatibility prompt/version/schema. Its documented rule is: `Any prompt or declared decomposition-contract identity change must change this hash.` Existing identity fixtures test that coverage. No additional fingerprint implementation, per-file hash manifest or candidate freeze is needed.

Following the existing versioned D1 identity and prompt-set patch precedent, a future prompt clarification must advance active `QUESTION_DECOMPOSITION_PROMPT_VERSION` and `PROMPT_SET_VERSION`, then obtain the actual fingerprint using this existing function. With no intervening identity changes, patch successors are `3.0.1` and `3.12.2`; these are a bounded implementation proposal under the existing dotted versions, not values activated here or a new versioning framework. Resolve then-current values before implementation to avoid reverting intervening changes.

Keep production schema v3, coverage schema v2, compatibility prompt `2.0.0` and compatibility schema v2 unchanged. The future source commit becomes a new product-behavior lineage because production prompt semantics change; update only current identity assertions/documentation. Do not rewrite historical run manifests, corrected reports or old fingerprints. This design computes no new fingerprint and changes no current product identity.

## 20. Rejected alternatives

No D1 schema redesign, structured subject/object requirement, obligation-kind taxonomy, host keyword correction, span-as-entailment proof, evidence-derived obligation, benchmark trigger, source quota, retrieval repair or new runtime call is justified. No downstream V1 repair or extra `point.text` completeness check compensates for an upstream canonicalization error. No blanket ordinary treatment of `which` requests is safe, and no blanket relation treatment of outputs, fields or containment verbs is safe.

Keep strict identifier eligibility/no-safe-relaxation and all unrelated selected-evidence/G4 findings frozen. Do not reopen n018, n006/n019 review, the closed forward run or integrated G5. A useful future empirical verification is not an additional immediate next task and is not authorized by implementation readiness.

## 21. Scientific limitations and static acceptance

PASS applies to a coherent, minimally scoped design: the corrected failure maps to the proposed boundary; current representation supports the desired shape; the prompt delta adds an operational distinction; real relations and identity-qualified/mixed requests have explicit controls; code/test execution and empirical authority are separated.

Static closeout checks are the allowlisted three-file diff, whitespace validation, unchanged earlier correction/source/tests/raw stores as established by the Git change set, and preservation of both historical document suffixes. No tests, decomposition, retrieval, provider health checks or product imports are part of acceptance. Before/after empirical metrics are not applicable. There is no new benchmark score or measured provider improvement.

The rule still relies on provider semantic judgment. Exact supports do not guarantee entailment, fakes do not measure that judgment, and a prompt improvement may not eliminate over-extraction or qualifier loss. Correct n023 routing does not repair its selected-evidence gap or guarantee ordinary completeness. n006/n019 remain counterexamples to any claim that using the ordinary path alone guarantees recovery. Current relation-text bounds and proof expressiveness limits remain unchanged.

## 22. Lifecycle, preserved findings and next task

```text
G5_D1_RELATION_EXTRACTION_BOUNDARY_REPAIR_DESIGN = COMPLETE / PASS / D1_RELATION_EXTRACTION_AND_QUALIFIER_PRESERVATION_CLARIFICATION
SELECTED_D1_BOUNDARY_POLICY = B2_BOUNDARY_AND_RELATIONAL_QUALIFIER_CLARIFICATION
ORDINARY_PROPERTY_LIST_REQUEST_CONTRACT = An anchor's property/value/item inventory is ordinary unless the requested answer itself establishes a relationship among independently relevant participants; preserve requested identities/count in point.text and use required_relations=[].
GENUINE_RELATION_REQUEST_CONTRACT = Extract only a requested relationship among independently relevant participants; preserve its full question-derived semantics in relation.text, including identities/subsets/counts/participant selection.
RELATION_IDENTITY_SET_QUALIFIER_PRESERVATION = REQUIRED
PROMPT_CHANGE_PROPOSED = true
SCHEMA_CHANGE_REQUIRED = false
HOST_SEMANTIC_RECLASSIFICATION = NOT_JUSTIFIED
IMPLEMENTATION_READY = true
G5_COARSE_COMPLETENESS_OVERACCEPTANCE_REPAIR_SURFACE_DESIGN = COMPLETE / CORRECTED / PASS
N006_D1_CLASSIFICATION = D1_SUFFICIENT
N019_D1_CLASSIFICATION = D1_SUFFICIENT
TARGETED_V1_VERDICT = TARGETED_V1_MECHANISM_SUPPORTED
G5_IDENTIFIER_EVIDENCE_ELIGIBILITY_REPAIR_DESIGN = COMPLETE / PASS / NO_IMPLEMENTATION_READY
IDENTIFIER_ELIGIBILITY_DESIGN_OUTCOME = STRICT_RULE_RETAINED / NO_SAFE_RELAXATION
IDENTIFIER_ELIGIBILITY_IMPLEMENTATION_READY = false
N019_ABSOLUTE_SEMANTIC_LIMITATION = CONFIRMED / COARSE_WITNESS_OVERACCEPTANCE_WITH_EVIDENCE_GAP
COMMON_RETRIEVAL_POLICY_DEFECT = NOT_ESTABLISHED
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false

PRODUCT_SOURCE_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
SCHEMA_CHANGE = false
PROMPT_FINGERPRINT_CHANGE = false
PRODUCT_BEHAVIOR_LINEAGE_CHANGE = false
NEW_PROVIDER_CALLS = 0
NEW_PROVIDER_PREFLIGHT_CALLS = 0
NEW_DECOMPOSITION_MODEL_CALLS = 0
NEW_RETRIEVAL_RUNS = 0
NEW_TARGETED_LIVE_RUNS = 0
NEW_LOGICAL_CASE_ATTEMPTS = 0
NEW_GENERATION_PROVIDER_INVOCATIONS = 0
NEW_EMBEDDING_PROVIDER_INVOCATIONS = 0
NEW_SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
TEST_EXECUTIONS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0

NEXT_TASK_RECOMMENDATION = G5 D1 RELATION-EXTRACTION BOUNDARY REPAIR IMPLEMENTATION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

The single selected outcome is **C — D1_RELATION_EXTRACTION_AND_QUALIFIER_PRESERVATION_CLARIFICATION**. The sole next recommendation is the separately authorized implementation above. No implementation, next-stage execution, G6 advancement or push is part of this delivery.
