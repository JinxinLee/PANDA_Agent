# G1 — Relationship-Aware Answer Obligation Design

**G1 = DESIGN COMPLETE / CORRECTED / IMPLEMENTATION READY**

Design review outcome: **PASS** for D1–D10 below. The accepted architecture selection is unchanged; implementation has not started and requires separate authorization. This is a selected product design, not implementation verification or empirical evidence. Original design inspection HEAD: `9944360accd6de14ebea5a543eeb5026ba523502`. Product behavior remains at `58bd53a86627ff0e0b668915076d974272e86233`, mode `production_answer_obligations_v1`, prompt set `3.11.2`, fingerprint `878caffb022dd66111b3bc6e98c6e372340cb619db13aa856c09aaa09e8b8391`. Phase F and F6 remain closed under [the Phase-F closeout](PHASE_F_CLOSEOUT.md).

## 1. Current architecture confirmed at original inspection HEAD

The following are static source observations, not executed QA results. Line references refer to the original inspection HEAD.

| Source / seam | Confirmed behavior |
|---|---|
| `src/panda_agent/question_decomposition.py:13` | Prompt version `2.0.0`; schema version `e1.question_decomposition.v2`. `_Point` contains semantic `text`, exact-question `support_spans`, and optional diagnostic `facet_type`. |
| `QuestionDecomposer.decompose()` | Receives only the raw question; validates 1–5 points, normalized-text uniqueness and literal supports, then sorts by earliest support position and normalized text before assigning `point.N`. Diagnostic labels do not determine identity or completeness. |
| `src/panda_agent/qa.py:3825`, `_run_detailed()` | Production invokes `decompose_question()` and hence `QuestionDecomposer.decompose()` before the graph. It installs decomposition points and immediately applies `_active_runtime_answer_points()`. The helper's old shadow-only docstring is stale; the call site establishes actual use. |
| `src/panda_agent/qa.py:807`, `_active_runtime_answer_points()` | Projects every coverage-mode point to `answer_point_id` and `text`. Support spans and diagnostic facets remain in decomposition diagnostics, not the downstream point contract. |
| `src/panda_agent/qa.py:158`, C1 schema and validator | `coverage-satisfaction-v1` checks contain `relationship_text`, `necessity_reason`, `basis`, `supporting_claim_ids`, `satisfied`, and `admission_state`. No question-assigned relation IDs or mandatory relation inventory exist. |
| `src/panda_agent/prompts.py:255`, `_verify()` | After retrieval and A0, C1 uses the question, broad point text, claims, and visible/admitted evidence to infer necessary relationship checks. They can also describe factual, definition, or locator content. |
| `_validate_coverage_satisfaction()` / `_after_verify_route()` / `_revise()` | Local code validates structure and evidence provenance, not semantic necessity or entailment. C1 computes completeness from its inferred scope; admitted unsatisfied checks can authorize one revision. |
| `_check_e3_trigger()` / `_build_missing_point_retrieval_objective()` | E3 is gated to `runtime_e1_v2`; production C1 does not enter that route. The existing missing-point objective currently includes only point text. |
| `src/panda_agent/evaluation_runner.py:364`, `prompt_fingerprint()` | The shared fingerprint binds decomposition prompt/version/schema-version and the production C1 prompt, schema and schema-version. |

The current decomposition already models one comparison rather than automatic descriptions of both entities, and one end-to-end workflow without invented intermediate stages. G1 preserves those semantics; diagnostic facets such as `workflow`, `comparison`, `data_flow`, and `cause_reason` are not promoted to authority.

## 2. Identified semantic gap

A broad point may mention the requested topics without preserving the exact requested relation. C1 then infers scope from evidence without a question-derived checklist that must survive and be accounted for. Retaining `facet_type` alone cannot recover direction, polarity, endpoints, or the meaning of “relative to.”

The selected flow is: raw question -> normalized answer points containing required relations -> one immutable runtime contract -> A0 and V1 -> authorized A1 subset, if any -> V2 against the original full contract. Required relations never originate from Gold, retrieval, claims, verifier suggestions, or domain workflow knowledge. This design addresses that structural loss surface without asserting its frequency or empirical repair benefit.

## 3. Alternatives considered

| Option | Assessment | Decision |
|---|---|---|
| A: relation semantics only in point text | Smallest payload and still essential context, but offers no explicit relation inventory, stable match key, or deterministic missing-disposition check. A broad paraphrase can erase the requested relation again. | Not selected. |
| B: `required_relations` nested in each answer point | Gives each relation exactly one owner; local normalization, propagation and coverage accounting remain point-scoped. Adds one bounded list without a second whole-answer completeness axis. | **Selected.** |
| C: top-level `points[]` plus `relations[]` joined by point ID | Can theoretically retain one authority, but adds independent collections, dangling joins and coordination/versioning surfaces without benefit at this scale. | Not selected. |

Structured subject/object/source/target slots are deferred. Pronouns, clause-valued arguments, comparisons of several entities, and end-to-end workflows do not fit a mandatory binary tuple reliably. Semantic request text plus exact question support preserves them without a separate participant-resolution subsystem.

## 4. Selected representation

An answer point contains zero or more question-derived required relations. It remains the only unit of whole-answer completeness and follows exactly one semantic-completeness path. For a relation-bearing point, the canonical required relations carry its requested semantics, including any explanation intrinsic to the relation; there is no additional ordinary-content obligation.

```text
if point.required_relations == []:
    point.complete = existing ordinary C1 completeness rule
else:
    point.complete = exactly one valid disposition per canonical required relation
                     AND every required relation is satisfied
                     AND every satisfied relation has ADMITTED_BACKING_AVAILABLE
missing_answer_point_ids = exactly the incomplete point IDs
```

No `answer_requirements_v2`, global missing-relation gate, graph of entities, or claim-to-relation mapping is introduced. Existing `claim.answer_point_ids` remains sufficient: the verifier can inspect a claim's content and citations against each canonical relation belonging to that point.

Independently omittable ordinary content plus relational content must become separate answer points. For “Where is Cedar implemented and how does Cedar feed Birch?”, one point asks for the implementation location and another carries the feed relation. “How does Cedar produce input for Birch?” is itself one relational request: its explanatory semantics belong in the canonical relation text, without a duplicate ordinary explanation requirement. Context retained in a relation-bearing `point.text` does not create another completeness obligation.

## 5. Authority model

`relation.text` expresses the user's request, supported by exact raw-question spans. It describes what must be answered, not a fact that must be asserted. For “Does Cedar cause Birch?”, a grounded negative answer can satisfy the relation; the system must not require a positive causal assertion. Changing direction, negation, modality, or an explicitly named endpoint changes semantics.

`relation_type` is optional bounded diagnostic metadata. Suggested labels are `ordering`, `workflow_placement`, `dependency`, `input_output`, `cause_effect`, `comparison`, and `composition_containment`; unusable values are omitted locally. Neither this label nor `facet_type` controls obligations, IDs, routing, or completeness. Keep these labels in diagnostics rather than semantic model payloads.

"Why does Cedar stop?" remains one explanation/cause-reason point with `required_relations=[]` and no invented cause participant. "Does Cedar cause Birch?" explicitly requests one causal relation. "How does Cedar work?" does not authorize a hidden workflow. Evidence may provide answer details or intermediate stages, but cannot add new mandatory user obligations.

Definitions, implementation locators and argument-list requests remain ordinary point content even though their grammar can be described relationally. Extract a required relation when the user asks to establish a connection, relative placement, or other relationship itself; do not mechanically convert every verb, property or API parameter into an edge.

Exact-span checks establish literal provenance, not semantic entailment of a model paraphrase. The decomposer's question-only prompt and future adversarial semantic checks must address unsupported paraphrases, missed relations, wrong ownership and bad splitting. G1 does not claim a substring validator can prove these semantic properties, and does not add another model call to pretend otherwise.

## 6. Proposed schema shape

Canonical normalized point, illustrated for “Does Cedar occur before Birch?”:

```json
{
  "answer_point_id": "point.1",
  "text": "Explain whether Cedar occurs before Birch.",
  "support_spans": ["Does Cedar occur before Birch?"],
  "required_relations": [
    {
      "relation_id": "point.1.rel.1",
      "text": "Explain whether Cedar occurs before Birch.",
      "support_spans": ["Does Cedar occur before Birch?"],
      "relation_type": "ordering"
    }
  ]
}
```

The production decomposition proposal uses this nested shape without either ID. It retains the existing `points` and diagnostic `ambiguity` envelope. `required_relations` is a required list in the new production proposal, including an explicit empty list. There is no default that silently converts a malformed new-contract proposal into a relation-free one.

For C1, retain a uniform point response shape and add `required_relation_checks` inside each `answer_point_coverage` record. The canonical relation inventory selects exactly one active completeness list. The following illustrates a relation-bearing point record, not a complete C1 review:

```json
{
  "answer_point_id": "point.1",
  "scope_status": "ESTABLISHED",
  "supporting_claim_ids": ["claim.1"],
  "complete": true,
  "relationship_checks": [],
  "required_relation_checks": [
    {
      "relation_id": "point.1.rel.1",
      "basis": [{"evidence_id": "evidence.1", "quote": "Cedar runs before Birch."}],
      "supporting_claim_ids": ["claim.1"],
      "satisfied": true,
      "admission_state": "ADMITTED_BACKING_AVAILABLE"
    }
  ]
}
```

Each ID identifies a `QUESTION_REQUIRED_RELATION`. The host resolves its semantic text from the immutable point/relation table; C1 copies the ID rather than paraphrasing the target. There is no empty-ID sentinel, model-authored ID, or text-based match. The list is required even when empty.

For relation-free points, `required_relation_checks=[]` and the existing `scope_status`, ordinary `relationship_checks` (including `relationship_text` and `necessity_reason`), supporter and completeness contract remain authoritative. For relation-bearing points, local validation requires `relationship_checks=[]`; only canonical required-relation dispositions determine semantic completeness. Do not manufacture an ordinary check to satisfy the old nonempty-check invariant. The uniform `scope_status` field is derived diagnostic data for these points, as specified in section 9. Existing top-level support, relevance, claim-to-point mappings, `reason`, and missing-point fields remain.

## 7. Deterministic normalization, IDs and bounds

1. Strictly validate types and allowed fields. Reject model-authored point/relation IDs, external owner fields, unknown keys, missing new-contract lists, empty semantic text, and empty/nonliteral support spans. Do not retry or switch contracts on a validation failure.
2. Normalize semantic text by whitespace collapse. For identity/deduplication use its casefolded normalized form, following existing point identity policy. Preserve original question bytes; support matching is case- and whitespace-exact. Semantic verification still distinguishes identifier case and relation polarity.
3. Deduplicate repeated support spans and order relation supports by first literal position, then span text. Every relation has 1–3 nonempty exact spans, each present in the raw question. Both its parent and its own support are checked against that same raw question.
4. Reject duplicate normalized relation text across the question, including duplicates assigned to different parents. Do not merge or reassign semantic ownership automatically. Nesting gives one parent; a mismatched parent in any later projection is an error. Semantically equivalent paraphrase duplicates remain a semantic validation limitation.
5. Preserve current point ordering: earliest exact support position, then normalized casefolded point text. Assign `point.N` after sorting. Sort each point's relations by the same support-position/text rule, then assign `point.N.rel.M`. Never use types, proposal order, evidence or claims in the ID function.
6. Validate all bounds before assigning the finalized runtime contract. No truncation, silent dropping or fallback-to-empty is permitted.

| Bound | Selected value and reason |
|---|---|
| Points | Existing 1–5. Independently omittable requests still split into points. |
| Required relations per point | 0–3: accommodates an explicitly compound placement/relationship while discouraging hiding independent requests in one point. |
| Required relations per question | 10: modest coverage for up to five points, without a general relation graph. |
| Relation text / support count | 1–240 characters after whitespace normalization; 1–3 exact spans. Copy a longer exact question clause when necessary; do not shorten its bytes to fit an invented span-length bound. |
| C1 dispositions | Each point uses either the existing ordinary allowance of up to 4 checks, or exactly one disposition per canonical required relation (1–3); the other list is empty. The existing overall ceiling of 20 checks per question is sufficient, with at most 10 required-relation dispositions. |
| Evidence and supporters | Preserve up to 2 distinct basis IDs per check, one exact nonempty quote of at most 400 characters per ID, 8 supporters per check, and 32 per point. |

Permutation stability is guaranteed for fixed semantic texts and support sets, including changed/omitted diagnostic labels. It is not a promise of identical IDs across arbitrary paraphrases, changed questions, or a changed decomposition partition. Requests exceeding representable scope fail explicitly through the existing decomposition failure path; insufficient evidence or support beyond the check bounds is not truncated into a positive verdict.

## 8. A0 integration

Production `_run_detailed()` must retain the normalized nested relations. `_active_runtime_answer_points()` must validate and project point ID, text, support spans, and the complete required-relation ID/text/support list instead of reducing it to two strings. Preserve a single canonical state object through the graph; generate stage payloads from it without letting model output modify it.

A0 receives the raw question and those relation-aware points, with supplied admissible evidence and no Gold. The prompt asks for evidence-supported answers to the actual relational requests, including grounded negative answers where applicable. `ANSWER_SCHEMA`, public claim DTOs, and `claim.answer_point_ids` do not gain relation fields. A generator mapping or a mention of both participants is never proof that the relation is answered.

## 9. C1 / V1 / V2 integration

The local validator must receive the canonical point/relation mapping, not only the current `point_ids` set. Require exactly one point coverage record as today, then select its completeness path from the immutable canonical inventory, never from the model's preference:

- Relation-free: `required_relations=[]` if and only if `required_relation_checks=[]`. Apply the existing ordinary C1 proof contract, including its scope/nonempty-check rules.
- Relation-bearing: `required_relation_checks` IDs must equal that parent's exact canonical required relation ID set, with each occurring once; `relationship_checks` must be empty. The ordinary nonempty-check invariant does not apply.

Match by ID and parent, never free text or fuzzy similarity. Reject missing or duplicate dispositions, foreign/cross-parent IDs, extra verifier-created relations, missing list fields, and nonempty ordinary checks on a relation-bearing point. An ordinary check cannot substitute for a required disposition, even if its prose describes the same relation.

| Disposition | Completeness and recovery consequence |
|---|---|
| Admitted backing, satisfied | Counts only with supported, relevant claims mapped to the parent, citing the validated required basis and semantically answering the target. |
| Admitted backing, unsatisfied | Parent remains incomplete; the known target and exact approved basis can enter the existing one-revision scope. |
| VISIBLE_ONLY_WITHOUT_CITABLE_BACKING | Must be unsatisfied with no supporters and an indispensable unadmitted basis. Parent incomplete; no citation-policy relaxation and no A1 instruction for this relation. |
| INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE | Must be unsatisfied with no supporters; 0–2 valid basis references allowed. Parent incomplete; no inference, extra retrieval or A1 instruction for this relation. |
| Missing, duplicate, foreign, or unknown key; invalid quote/support | Coverage review structurally invalid; no complete point or revision scope is accepted from it. Preserve only independently valid claim-support/mapping judgments under the existing recovery path. |

For a relation-free point, compute `complete` using the unchanged ordinary rule: established scope, nonempty ordinary checks, and all those checks satisfied with admitted backing. For a relation-bearing point, compute `complete` solely from its exact, validated required-relation dispositions: all must be satisfied with admitted backing. Reject a contradictory model flag or missing-point complement. A required-list omission can never make a point vacuously complete. Honest uncertainty is a valid disposition, not a missing row.

The point supporter union follows the same selected path. For a relation-free point, `point.supporting_claim_ids` is the ordered unique union of ordinary `relationship_checks` supporters, as today. For a relation-bearing point, it is the ordered unique union of `required_relation_checks` supporters only. Preserve supplied claim order and existing per-point limits; reject a contradictory union. No duplicate support through both lists is required.

For relation-free points, `scope_status` retains its existing meaning and coupling to ordinary checks. For relation-bearing points, retain the field only with this deterministic consistency rule:

```text
if any required relation has INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE:
    scope_status = INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE
else:
    scope_status = ESTABLISHED
```

Visible-only backing does not make semantic scope unknown: a visible-only relation therefore permits `scope_status=ESTABLISHED` while keeping `complete=false`. Mixed valid admitted/uncertain dispositions remain valid, with uncertainty reflected in the derived scope. Local validation rejects inconsistent scope values; the model cannot use this field to override dispositions or suppress another relation's authorized revision. `OVERFLOW` remains reserved for explicit bounded-contract overflow under the applicable existing path. Decomposition overflow already fails before C1; it is not an alternative scope value for a valid, within-bounds relation-bearing inventory or a substitute for a missing disposition.

`QUESTION_REQUIRED_RELATION` is authoritative for a relation-bearing point because it was extracted before retrieval. `VERIFIER_DERIVED_RELATIONSHIP_CHECK` remains part of the existing relation-free ordinary contract only. It cannot create a second mandatory list for a relation-bearing point; nonempty ordinary checks there are rejected locally. The verifier may still judge claim entailment through the existing support channel, but cannot invent a workflow stage, independent entity description, or other hidden user requirement. No extra semantic reviewer call is added.

A bad quote, unknown basis, invalid supporter, duplicate relation ID, or other malformed coverage item still invalidates the coverage review globally, preserving only independently valid claim-support/mapping judgments through the existing recovery path. Target-local revision authorization happens **after a valid review**; it is not G2 local malformed-review recovery. G2 remains `PLANNED / NOT_STARTED`. The old experimental coverage contracts are unchanged.

Completeness remains a semantic judgment within a question-defined envelope. Exact IDs and quote provenance prevent silent accounting loss; they cannot independently prove that a supported claim establishes a before/after, comparison, or causal answer. Future semantic adversarial checks must exercise that boundary.

## 10. A1, E3 and composer interaction

**A1:** After a valid C1 review, authorize each repair target independently. A required relation may enter the existing `revisionable_relationships` payload when `satisfied=false`, `admission_state=ADMITTED_BACKING_AVAILABLE`, and its basis is locally valid. Each target contains parent ID, `relation_id`, canonical semantic text resolved by the host, and approved evidence basis. Visible-only or insufficient/ambiguous backing blocks only that relation. One blocked target does not invalidate or suppress another independently grounded, authorized target in the same point; there is no all-targets-must-be-revisionable prerequisite.

For relation-free points, existing ordinary admitted-backed revision targets and authorization remain unchanged. Relation-bearing points have no ordinary check targets. Preserve eligible unsupported-claim repair under its existing rules, verified mapping authority, anti-resurrection merge rules and `revision_count < 1` routing. Multiple independently authorized targets may share the existing single bounded A1 call; do not introduce relation-by-relation calls, a second revision round, or a retry after V2.

Project only authorized named relations into A1's structured point context; broad point text remains context, not blanket repair authority. Do not turn blocked relations into repair targets or admit evidence merely because it was visible. Keep the complete immutable canonical inventory in state for V2. For example, with `point.1.rel.1` admitted-backed/unsatisfied and `point.1.rel.2` visible-only/unsatisfied, A1 receives only `point.1.rel.1`; V2 still checks both. If the second relation remains blocked or unsatisfied, `point.1.complete=false` even when the first repair succeeds. The same target-local authorization holds when the sibling is uncertain and the derived point scope is insufficient. Target-local revision does not grant target-local final acceptance.

This authorization correction does not introduce G4 thresholds, fallbacks or answerability policy changes. G4 remains separate and unimplemented.

**E3:** Preserve the `runtime_e1_v2` trigger and production exclusion. Extend only the existing missing-point objective formatter to include canonical required-relation request text when supplied, under the same parent point and existing bounds. Old point-only inputs format as before. There is no separate relationship retrieval subsystem, candidate pool, budget, or production activation. The preserved experimental path continues to use its versioned point contract; future relation-aware E3 use would need an explicitly authorized integration, not silent promotion here.

**Composer:** Keep verified claims as its sole factual input. Do not send obligations, evidence, or relation completeness decisions to the composer. V2 audits the unchanged full point contract after A1; composition cannot create or clear missing points, and existing factual-preservation/fallback checks remain in force.

## 11. Compatibility, product mode and versioning

**Select product-mode Option 1:** implement the future G1 change inside `production_answer_obligations_v1`. The mode names a pipeline, not an immutable scientific candidate. G1's semantic materiality will be explicit in its implementation commit and prompt/schema identities. Avoid a second complete production branch or reserving `production_answer_obligations_v2` before G5 integrates Phase-G work.

Rollback is the focused implementation commit's full revert, not a silent runtime fallback. Comparison with current v1 uses the preserved `58bd53a...` product lineage and actual execution identities; ordinary development need not create a frozen candidate. No comparison or checkout is executed here. The tradeoff is no concurrent old/new behavior selector in one process; separate authorized Git-based comparisons preserve clarity without dual pipeline maintenance.

Relation-free production questions use `required_relations=[]` and `required_relation_checks=[]`. Preserve their existing ordinary proof checks, evidence capacity, scope rules, supporter rules and revision eligibility; there is no additional named-relation burden. This is a compatibility requirement for future fixtures, not a claim that unrun model outputs will be identical. Legacy mode remains outside decomposition. Preserve the existing decomposition-v2 profile for explicit shadow/runtime E1/E2/E3 entry points; choose the new relation-aware profile explicitly from the production call site. This small contract selection is required compatibility, not a generic feature flag or catch-and-fallback system. New-production payloads may not masquerade as legacy payloads to bypass missing relations.

Planned future versions, **not applied by this design**:

| Identity | Proposed implementation successor |
|---|---|
| QUESTION_DECOMPOSITION_PROMPT_VERSION | 2.0.0 -> 3.0.0 for the relation-aware contract; retain named v2 compatibility data for old entry points. |
| QUESTION_DECOMPOSITION_SCHEMA_VERSION | e1.question_decomposition.v2 -> e1.question_decomposition.v3 for production. |
| COVERAGE_SATISFACTION_SCHEMA_VERSION | coverage-satisfaction-v1 -> coverage-satisfaction-v2: the mandatory nested disposition list changes the output shape and completeness contract. |
| PROMPT_SET_VERSION | 3.11.2 -> 3.12.0. |
| Prompt fingerprint | Recompute through the existing shared authority only during implementation. Bind the new production contracts/provider schemas and the retained decomposition compatibility profile; do not fabricate a value or rewrite historical fingerprints. |

Contract-aware projection, C1 validation, A1 assembly, audit payloads, prompt updates and fingerprint coverage must ship coherently in the future implementation. Preserve model-role configuration, public answer DTOs, evaluator scoring, Gold/calibration, and historical records. The stale decomposition docstring may be corrected with that implementation; it is not changed here.

## 12. Provider-schema practicality

The [Vertex compatibility record](POST_A5_C1_VERTEX_SCHEMA_COMPATIBILITY_REPAIR.md) establishes a real compatibility constraint; it does not establish that every array bound is universally unsupported. Use an explicit simple production proposal schema plus strict local validators, rather than exposing all Pydantic validation constraints to `response_json_schema`.

Use objects, arrays, primitive types, properties, items, required fields, and closed object fields. Do not add `minItems`, `maxItems`, `minLength`, `maxLength`, `uniqueItems`, conditional schemas, participant unions, or dynamic per-question ID enums. Relation nesting adds one small layer to decomposition. C1 keeps a uniform point shape with sibling check lists at the existing depth; only the list selected by the canonical inventory may be nonempty. Named records carry a copied ID instead of relationship/necessity prose. Preserve the relation-free ordinary proof schema and the overall 20-check ceiling. Local validation owns path selection, empty-list requirements and scope consistency without adding provider-facing conditional schemas. Diagnostic type is an optional plain string on the wire and locally bounded.

All count, length, ID, ownership, duplicate and literal-provenance checks run locally. This is a targeted schema definition, not a generic schema sanitizer. Static shape and fake-provider boundary tests are planned; an actual provider compatibility smoke, if requested later, requires explicit authorization and is not evidence from this design task.

## 13. Proposed adversarial future test matrix

All rows below are **PROPOSED / NOT_RUN**, with synthetic neutral entities. Fake responses test deterministic contracts, not natural-language model accuracy. Semantic-response quality needs separately authorized empirical evidence later.

| ID | Input / mutation | Required observation |
|---|---|---|
| R01 | Does Cedar run before Birch? / after Birch? | One direction-preserving request; a grounded negative answer can satisfy it, while reversing the question's predicate or ignoring it cannot. |
| R02 | Where does Cedar occur in the workflow relative to Birch? | One placement relation; do not decide the order in decomposition. |
| R03 | Does Cedar depend on Birch? | One dependency request; grounded yes or no can satisfy it. |
| R04 | How does Cedar produce input for Birch? | One canonical input-output relation includes the requested explanation; no duplicate ordinary explanation obligation. |
| R05 | Does Cedar cause Birch? | Causal question with polarity preserved; correlation alone is insufficient. |
| R06 | How do Cedar and Birch differ? | One comparison relation, exactly one required disposition, and relationship_checks=[]; no duplicate ordinary check or independent entity descriptions. |
| R07 | Is Cedar contained in Birch? | One containment request; no inferred component list. |
| R08 | Describe the workflow from StageOne to StageTwo. | One end-to-end relation; no manufactured intermediate Maple obligation. |
| R09 | How does Cedar feed Birch, and how does Birch differ from Maple? | Two independently omittable points, one relation each. |
| R10 | Is Cedar between Birch and Maple? | Preserve both placement constraints within one composite placement point, using a bounded relation description. |
| R11 | Where is Cedar implemented? / Define Birch. / Which file defines Maple? / What arguments does SensorFrame accept? | required_relations=[] and required_relation_checks=[]; preserve the existing ordinary C1 checks, scope and revision behavior. |
| R12 | How does Cedar work? / What does Cedar do? | No unseen stages, Birch dependency, or invented input/output chain. |
| R13 | Why does Cedar stop? versus Does Cedar cause Birch? | Explanation point without an invented cause participant versus an explicit causal relation. |
| R14 | Does Cedar depend on Birch, and does it produce SensorFrame? | Preserve two requested obligations and exact antecedent context; no required subject/object slots. |
| R15 | Compare Cedar, Birch and Maple. | One comparison request can have more than two participants without tuple expansion. |
| R16 | Where is Cedar implemented and how does Cedar feed Birch? | Two independently omittable points: ordinary locator and canonical feed relation; never two completeness paths in one point. |
| V01 | Relation span absent from question, case-changed, or whitespace-altered | Reject exact-support violation; no fuzzy repair. |
| V02 | Duplicate normalized relation in one point or two owners | Reject; do not merge or move it silently. |
| V03 | Empty/whitespace relation text; wrong field type; missing relation list | Reject malformed new contract; never substitute []. |
| V04 | Decomposer returns point/relation IDs, duplicate IDs or a point_id owner | Reject model-authored authority fields. |
| V05 | Shuffle points/relations/support order; change, omit, or corrupt type labels | Semantic IDs/order unchanged for the same normalized texts and support sets. |
| V06 | Three versus four relations in one point; ten versus eleven total | Accept valid limits; reject overflow without truncation. |
| V07 | Exact span “Cedar” supports a proposed unseen dependency on Maple | Structurally literal does not imply semantic grounding; semantic fixture flags this unsupported inference. |
| P01 | Pass normalized points through initialization and each payload projection | Preserve every canonical semantic field; A0/V1/V2 use the same full inventory. |
| C01 | Omit a required row but claim complete=true; omit the named list when no relations exist | Reject missing/duplicate contract data; relation-free responses require an explicit empty named list and the existing ordinary proof contract. |
| C02 | Duplicate, unknown, cross-parent, or invented relation ID | Reject; no text-based rematching. |
| C03 | Admitted/visible-only/uncertain required disposition variants | Only validated admitted satisfaction counts; other valid dispositions make the parent incomplete. |
| C04 | Participant mentions and mapped supported claims, but an unsatisfied named relation | Relation-bearing parent incomplete; mentions/mappings cannot substitute for required relation satisfaction. |
| C05 | All canonical required relations have valid admitted-backed satisfaction; ordinary checks are empty | Relation-bearing point complete; do not demand an additional ordinary explanation or nonempty ordinary proof. |
| C06 | Nonempty ordinary relationship_checks on a relation-bearing point, even if duplicating the relation | Reject locally; no verifier-created second mandatory completeness path. |
| C07 | Wrong quote, extra basis, unsupported supporter, wrong mapping, uncited basis | Preserve strict rejection and existing independent claim-support salvage only; no G2 local repair. |
| C08 | Model complete/missing IDs or point supporter union contradict dispositions | Reject deterministic inconsistency. |
| C09 | Some required relations lack evidence while another has valid admitted backing | Record every named disposition; derive scope from those dispositions and keep the parent incomplete. |
| C10 | Required relation uncertain versus visible-only, plus inconsistent model scope variants | Any uncertain relation derives uncertain scope; otherwise scope is ESTABLISHED. Visible-only still means complete=false. Reject inconsistent scope or spurious OVERFLOW for a valid bounded inventory. |
| C11 | Point supporter union includes duplicates, wrong order or supporters from the inactive list | Reject inconsistent unions; use ordinary supporters for relation-free points and required-relation supporters for relation-bearing points only. |
| A01 | One admitted-backed unsatisfied relation plus a visible-only or uncertain sibling in the same point | A1 receives the admitted target only, regardless of the blocked sibling or derived scope; V2 checks both and the point stays incomplete if the sibling remains blocked. |
| A02 | Relation-free ordinary admitted-backed target alongside a blocked relation in another point | Preserve existing ordinary revision authorization; no G1 suppression of the valid target. |
| A03 | Already verified claims, ID collisions, and second revision request | Preserve existing merge/provenance rules and one-revision limit. |
| A04 | Two independently admitted-backed unsatisfied required relations in one point | Both may enter one bounded A1 request; revision_count reaches 1 once and V2 rechecks the complete canonical inventory. |
| K01 | Old legacy/shadow/runtime profiles; relation-free production needing 1–4 proof checks or more than two basis IDs overall | Old contracts remain usable; preserve ordinary proof capacity and dispositions with no extra named relations. |
| K02 | Existing E3 objective with/without optional canonical relations | Same missing-point subsystem; formatter preserves relation semantics when provided; no production E3 activation. |
| K03 | Composer payload and trace ON/OFF | Composer remains verified-claims-only; trace capture does not change behavior or completeness. |
| S01 | Provider schema inspection and local invalid-proposal fixtures | No added provider bound keywords or dynamic ID enums; strict local enforcement still rejects violations. |
| I01 | Mutate new decomposition/C1 prompt, schema or declared version | Shared future fingerprint changes; historical artifacts stay unchanged. |

## 14. Future implementation scope

No files listed here are edited by this design. Likely future changes are:

| File | Bounded responsibility |
|---|---|
| `src/panda_agent/question_decomposition.py` | Relation-aware production proposal/normalization, IDs, local bounds, simple provider schema and preserved v2 compatibility profile. |
| `src/panda_agent/qa.py` | Production profile selection; typed runtime point structure/projection; fixed C1 accounting; canonical A1 targeting; existing E3 objective formatting and diagnostics. |
| `src/panda_agent/prompts.py` | A0/C1/A1 question-relation contracts and prompt-set successor; no composer or external judge semantic redesign. |
| `src/panda_agent/evaluation_runner.py` | Shared fingerprint coverage of changed/versioned contracts only; no metric, judge, cohort or evaluation execution change. |
| `tests/unit/test_question_decomposition.py` | Provenance, normalization, ordering, bounds and compatibility profile fixtures. |
| `tests/unit/test_post_a5_c1_coverage_completeness.py` | Mandatory target accounting, admissions, malformed-review and repair-scope contracts. |
| `tests/unit/test_generic_answer_obligation_completeness.py` | Production propagation and relation-free/multi-relation synthetic integration. |
| `tests/unit/test_post_a5_o1_ea1_c1_integration.py`, `tests/unit/test_post_a5_o1_observability.py` | Existing trace and admission seams under the new payload, with no new trace lifecycle. |
| `tests/unit/test_e3_missing_point_retrieval.py`, `tests/unit/test_f6_release_identity.py`, `tests/unit/test_qa.py` | Existing objective formatting, fingerprint authority and directly affected contract/version assertions. |

Use focused fake/static checks in a separately authorized implementation task. No new framework, relation resolver, public API, provider sanitizer, or autonomous evaluation runner is justified.

## 15. Non-goals and materiality

G1 does not include G2 malformed-basis salvage, G3 evidence-admission policy changes, G4 false-insufficiency tuning, new retrieval, fresh novel_dev creation/evaluation, novel_validation, holdout, or release evaluation. Interfaces to those tasks do not authorize them. No historical g013/g023/g047/g050 rule, entity, source, file, PDF page, expected answer or Gold clause defines this schema; the matrix uses neutral synthetic requests.

```text
SOURCE_CHANGE = false
MATERIAL_PRODUCT_CHANGE = false
PROMPT_CHANGE = false
EVALUATOR_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
NOVEL_VALIDATION_ACCESS = 0
HOLDOUT_ACCESS = 0
```

These values describe this design task only. Future implementation is expected to be a material semantic contract change. Protected data remains untouched; all historical Phase-F/T1/T2 outcomes remain unchanged.

## 16. Design acceptance

| Criterion | Selected design satisfies it by |
|---|---|
| D1 — Question-only authority | Raw-question-only decomposition with exact provenance; explicit semantic limitations and anti-inference fixtures. |
| D2 — Single completeness authority | One completeness path per point; final missing/completeness decisions remain point-level. Independently omittable ordinary and relational requests split into separate points. |
| D3 — Downstream preservation | One immutable canonical inventory, explicit production projection, authorized A1 subset and full V2 recheck. |
| D4 — Deterministic identity/provenance | Strict local validation, sorted host-assigned IDs and diagnostic-label independence. |
| D5 — Mandatory C1 accounting | Each point has one completeness path. Relation-free points use the existing ordinary C1 proof contract. Relation-bearing points use exactly one validated disposition per canonical required relation and no duplicate mandatory ordinary checks. |
| D6 — No hidden requirement invention | Relation-bearing points reject nonempty ordinary checks and unknown relation IDs; their canonical relation text carries the full requested semantics. Relation-free ordinary authority is preserved. |
| D7 — Bounded revision | Authorization is target-local after a valid review. Any valid admitted-backed unsatisfied target may enter the existing single bounded revision; blocked targets stay blocked and V2 rechecks the full canonical contract. |
| D8 — Provider practicality | Simple bounded-depth wire shapes, strict local bounds, no new generic sanitizer. |
| D9 — Relation-free compatibility | Explicit empty relation lists and ordinary point checking; preserved older mode contracts. |
| D10 — Genericity | Neutral relational semantics and adversarial matrix; no benchmark/entity/location implementation rules. |

**PASS** applies to the design decision and static consistency only. Proposed tests, real-model decomposition quality, semantic coverage accuracy, runtime provider acceptance and false-refusal effects have not been executed or established in this task.

Static verification confirmed the three requested Markdown paths only, matching forward-authority blocks, unchanged historical documentation sections, 17 design sections, two syntactically valid illustrative JSON snippets, and 44 proposed matrix rows. The corrected contract specifies one completeness path per point, target-local revision after a valid review, full-contract V2 verification, the one-revision bound and unchanged G2/G4 boundaries. `git diff --check` passed. No source/test/Gold/calibration/prompt file changed, and no test suite or evaluation was run.

## 17. Unresolved questions and next step

The accepted architecture choices remain unchanged. The corrected single completeness path and target-local revision contract make G1 implementation-ready; implementation has not started and is not authorized by this correction. Natural-language extraction quality, provider acceptance and the effect of existing evidence bounds remain future verification uncertainties, not reopened design alternatives or permission to execute science now.

```text
G1 = DESIGN COMPLETE / CORRECTED / IMPLEMENTATION READY
NEXT_TASK_RECOMMENDATION = G1 RELATIONSHIP-AWARE ANSWER OBLIGATION IMPLEMENTATION
NEXT_TASK_EXECUTION_AUTHORIZED = false
STOP.
```
