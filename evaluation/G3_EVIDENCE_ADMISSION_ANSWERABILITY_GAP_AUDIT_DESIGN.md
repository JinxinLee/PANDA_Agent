# G3 — Evidence Admission / Answerability Gap Audit Design

## 1. Decision and scope

Select a trace-first, selected-evidence-centered observational audit of the current
production_answer_obligations_v1 path. Join the retrieval funnel when an authoritative
retrieval trace exists, but use final selected evidence as the admission denominator.
Preselect a reviewed novel_dev development cohort without looking at QA outcomes.
Reuse compatible immutable artifacts first. A separately authorized scoped run
may fill missing current-lineage artifacts through the supported QA stage-trace
path for novel_dev. This document authorizes neither route.

The audit asks how often evidence reached selection yet failed to become citable,
verifier-used, and answer-authorized backing, and which layer owns each break.
Selected-but-unadmitted is an observation, not a finding that the answer should have
been produced or that admission policy is defective. A valid visible-only disposition
is stronger semantic linkage, but still does not establish a policy defect.

No admission, retrieval, G1/G2, verifier, or composer behavior changes here. No
questions, outcomes, protected datasets, or historical expected answers were inspected
for this design. The trace-capability preflight and its narrow observability
prerequisite are complete; the next recommended task is a separately authorized
scoped audit.

## 2. Current production architecture

Source authority: src/panda_agent/retrieval.py (Retriever.retrieve and final
selection), src/panda_agent/qa.py (_is_public_claim_citation_eligible,
_admitted_evidence, _trace_admission, _answer, _verify, _revise), and
src/panda_agent/evaluation_runner.py (optional development stage trace and
retrieval-trace persistence). The relevant deterministic contracts are also covered
by tests/unit/test_post_a5_ea1_exact_backing.py,
test_post_a5_o1_ea1_c1_integration.py,
test_e2_a3_r2_citation_eligibility.py,
test_post_a5_o1_observability.py,
test_post_a5_c1_coverage_completeness.py,
test_g1_relationship_obligations.py, and
test_g2_coverage_local_failure.py.

EvaluationSplit includes novel_dev. The standard run_evaluation path calls
_configure_stage_trace before execution; its explicit development allowlist now
includes novel_dev for non-formal, non-candidate qa/full runs with
capture_stage_trace=true. Protected/formal and retrieval-only requests remain
rejected. The runner writes a retrieval trace separately from optional QA stage
tracing; retrieval candidate/selection records do not contain EA_ADMISSION,
A1_INPUT, or V1/V2 stage events. Stage capture remains bounded and best-effort,
so each future artifact still requires a completeness check.

Retriever.retrieve produces bounded per-channel rankings, top fusion scores,
reranked and ranked object IDs, and a final bundle.evidence. The selected Evidence
projection has evidence_id, object_id, source/version identity, text, locator,
retrieval channels, score, and authority level; it does not retain object_type.
Normal production QA calls retrieval without capture_candidates, although
diagnostics retain ranking IDs. Do not infer an absent object from an absent
candidate snapshot. A stored retrieval trace is needed for authoritative candidate
stage claims; its fused_candidates currently represents only stored top fusion
scores, not necessarily every fused object.

The direct public citation rule is exact current behavior: an evidence item whose
source_id contains lowercase "sphinx" requires nonempty locator.url,
locator.snapshot_date, and locator.section_path. Other source IDs pass this
particular direct-eligibility check. Direct eligibility does not prove relevance,
support, version correctness for a requested claim, or answer authorization.

For selected non-direct Sphinx pages, _admitted_evidence may resolve one exact
section. Its bounded path requires a page object ID, usable URL/date and empty
section_path, a source manifest and backing-store lookup, matching source/version
and snapshot, exact page content/locator relationships, one qualified child, exact
single containment, and the child's own citation eligibility. At most four pages
enter the resolution candidate set; child count and length have separate bounds.
The admitted projection contains directly eligible selected items and any resolved
backing substituted for a selected parent. bundle.evidence itself is unchanged.
The _ea_cache holds that projection, added backings, and per-selected decisions.

A0 receives the admitted projection. A1, if reached, receives a bounded subset of
that projection for its repair targets. V1/V2 receive the full QA-visible evidence
set, which is selected parents plus newly resolved backings, and separately receive
admitted_evidence_ids. Thus review visibility, citable admission, generation
exposure, and A1 target exposure are distinct. G1 named relations use canonical
relation IDs; ordinary checks have only verifier-authored local order. G2 validates
coverage into VALID, PARTIAL, or REJECTED, with local item states VALID,
LOCAL_INVALID, MISSING, or CONFLICTED. Only valid dispositions can support a G3
semantic-linkage claim.

The explicit runtime_e1_v2 path returns only directly eligible selected items
from _admitted_evidence and can change the bundle through E3. It is not a
comparable production admission cohort and is excluded from G3 rates.

## 3. Causal ownership rules

Corpus existence, channel retrieval, ranked visibility, final selection, direct
eligibility, exact-backing resolution, admission, verifier visibility, valid
semantic use, and answer authorization are separate states. Never infer an earlier
stage from a later stage without its artifact, or infer a downstream semantic
entitlement from upstream visibility.

Classify an absent selected item as retrieval/selection-owned only after a relevant
candidate trace or independent reviewed evidence establishes what was missing.
R1 covers unavailable candidate recall, R2 ranking, and R3 final selection. A
selected item rejected at admission is an admission observation, not yet a defect.
Admitted evidence judged insufficient remains a semantic or verifier question.
G2 LOCAL_INVALID, MISSING, and CONFLICTED dispositions are structural validation
states, never admission verdicts. A supported claim can still fail claim mapping,
relation satisfaction, point completeness, or final answer gates.

## 4. Evidence funnel and stage provenance

Use three-valued stage values YES, NO, and NOT_OBSERVABLE, plus NOT_APPLICABLE
where a stage does not apply. Absence from an incomplete trace is NOT_OBSERVABLE.
Join selected evidence by evidence_id, candidates by object_id plus
source_version_id when available, and resolved sections by the explicit parent
and backing IDs. Never join unrelated evidence solely by similar text.

| Stage | Question | Existing proof and limits |
|---|---|---|
| S0 candidate availability | Was the object in an executed channel candidate pool? | A complete same-run retrieval trace channel_candidates, or bundle rankings with its run identity, proves membership. No trace means NOT_OBSERVABLE; corpus presence is not S0. |
| S1 ranked/visible | Was it fused, offered to rerank, reranked, or present in the post-prioritization ranked pool? | Use fusion_scores, reranked_object_ids, ranked_object_ids, and channel ranks separately. Stored fusion_scores is top-30 only; absence cannot prove no fusion. The full rerank input pool is not persisted in ordinary production diagnostics. |
| S2 selected | Was the object in final retrieval evidence? | diagnostics.selected_evidence / selected_evidence_ids or retrieval_trace.final_evidence, reconciled by IDs with the run result. This is the primary admission denominator. |
| S3 direct eligibility | Did the selected item satisfy the current public citation predicate? | Deterministically replay _is_public_claim_citation_eligible on the frozen selected item's source_id and locator under the bound product lineage. Do not infer it from admitted membership alone. |
| S4 resolution | Was exact-backing resolution applicable and attempted? | Applicability follows the selected non-direct page fields and candidate bound. _ea_cache decisions and EA_ADMISSION give outcomes, but no explicit attempted flag. RESOLVED_EXACT_BACKING, VERSION_MISMATCH, AMBIGUOUS_BACKING, and post-lookup NO_VALID_BACKING establish path entry; BOUND_EXCEEDED and LOOKUP_FAILED do not always identify the precise substage. Mark uncertain attempt/substage NOT_OBSERVABLE. |
| S5 admitted backing | Was the selected item admitted directly or through an exact backing? | Reconcile EA_ADMISSION.decisions with admitted_evidence_ids and parent_evidence_id/backing_evidence_id. DIRECTLY_CITATION_ELIGIBLE admits the selected ID; RESOLVED_EXACT_BACKING admits the backing ID. Require matching selected IDs and a complete decision list. |
| S6 verifier exposure | Was selected parent or backing visible at V1/V2? | V1_INPUT/V2_INPUT.model_input.untrusted_evidence and admitted_evidence_ids distinguish full review visibility from admission. A0_INPUT is not a named trace event; EA_ADMISSION.untrusted_evidence and A1_INPUT.model_input.untrusted_evidence separately show generation exposure. |
| S7 semantic use | Did a valid disposition cite the evidence as basis? | Join the round's V1/V2 raw coverage output to its validated G2 disposition and basis evidence IDs. A final VALID answer_point_audit.answer_point_coverage is usable for the final round. For PARTIAL, per-round valid items require deterministic replay under exact G2 lineage with complete frozen inputs, or a small future per-round receipt trace; otherwise NOT_OBSERVABLE. |
| S8 authorization | Did the item support a claim, satisfied named relation, complete ordinary check, and/or complete point? | Use the same-round validated coverage, answer_point_audit.claim_mappings, supported/rendered flags, covered_answer_point_ids, and final result claims/evidence. Record each level separately; one positive level never implies the next. |

For S6, the full review-visible set can contain an unadmitted selected parent;
visibility alone cannot turn its basis into ADMITTED_BACKING_AVAILABLE. For S7,
VISIBLE_ONLY_WITHOUT_CITABLE_BACKING with an exact selected basis is Tier 1 only
when its G2 disposition is VALID. INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE is not
inferred from the absence of basis. V1 and V2 are separate observations; the final question
summary uses V2 if executed, otherwise V1. Never count one relation twice in a
final question-level incidence rate.

## 5. Strength tiers and analysis units

Tier 0, visibility only: a selected item was not admitted after decision/backing
reconciliation. This supports frequency accounting, not a relevance claim.

Tier 1, semantic linkage: a VALID verifier disposition for a requested point or
canonical relation cites the selected parent or resolved backing as basis, with
the item's admission state and provenance traceable. A valid visible-only
disposition referencing a selected-but-unadmitted item is the principal
admission-gap candidate. Reviewer semantic linkage can be recorded separately
where no valid disposition exists; it must not be silently promoted to
model-observed Tier 1.

Tier 2, policy-defect candidate: Tier 1 plus independent factual support and
unambiguous source/version/citation provenance under a plausible generic rule,
evidence that the blocker is an admission mechanic rather than retrieval,
semantic insufficiency, mapping, or malformed review, and a repeated or
structurally generalizable mechanism. Tier 2 remains a candidate, not a
confirmed defect or authority to change policy.

The evidence unit is (run_id, question_id, phase A0/A1, selected_evidence_id).
Keep parent and resolved backing IDs linked without counting the backing as a
second selected item. The semantic unit is (run_id, question_id, V1/V2,
answer_point_id, canonical relation_id) for named relations. An ordinary
check uses answer_point_id and validated local ordinal only within one round;
it is not a durable cross-run semantic ID. The question unit deduplicates
evidence and relation observations for final incidence and primary ownership.

## 6. Bounded audit record and artifact status

The future audit writes one evidence-opportunity record per selected evidence
unit, with zero or more separate relation/check linkage records. Fields are
audit-only, never production DTOs:

| Field group | Fields |
|---|---|
| Identity | run_id, question_id, dataset identity, product-behavior lineage, mode, phase, verify_round, artifact references |
| Selected evidence | selected_evidence_id, object_id, source_id, source_version_id, coarse_source_types, admission_subtype, final_selected |
| Retrieval | S0/S1 stage values, channel ranks, fused/reranked/ranked positions where actually retained |
| Admission | S3 direct eligibility, S4 applicability/attempt state, selected-parent decision/reason, S5 admission route, parent/backing evidence and object IDs, trace consistency |
| Exposure | A0/A1 model evidence IDs, V1/V2 review-visible IDs and admitted IDs |
| Semantic link | answer_point_id, canonical relation_id or local ordinary ordinal, G2 validation state, valid admission_state, basis evidence IDs, satisfied, supporter claim IDs |
| Authorization | supported claim IDs and verified point mappings, ordinary check/required relation/point completion, rendered claim flag, final status |
| Audit judgment | strength tier, primary root cause, secondary causes, reviewer decisions, uncertainty reason, evidence/provenance references |

Write evidence_opportunities.jsonl with one object per evidence unit,
semantic_links.jsonl with one object per valid or separately reported
invalid relation/check coordinate and basis edge, and
question_summaries.jsonl with one object per question. All records carry
schema_version, run_id, question_id, and artifact_identity. The evidence
record uses phase, selected_evidence_id, selected_object_id,
source_version_id, stage_status keyed by S0–S8, admission_reason_code,
admission_route, backing_evidence_id, source_type tags, and
observability_codes. The semantic-link record uses verify_round,
answer_point_id, relation_id or ordinary_check_ordinal, validation_state,
admission_state only when VALID, basis_evidence_id, supporter_claim_ids,
and authorization flags. The question record contains final status,
denominator eligibility, tier counts, and primary/secondary ownership.
Use null only for an applicable but unknown value; use NOT_APPLICABLE
for an inapplicable stage and NOT_OBSERVABLE for missing authority.
Keep reviewer judgments in a separate keyed overlay so they cannot
rewrite deterministic stage facts.

Field classifications for current artifacts:

| Field or join | Classification | Qualification |
|---|---|---|
| S2 selected IDs and selected item metadata | EXISTING_AUTHORITATIVE_FIELD | Same-run diagnostics.selected_evidence or retrieval_trace.final_evidence. |
| S0 channel membership and S1 stored ranks | EXISTING_AUTHORITATIVE_FIELD | Only when a complete same-run retrieval trace/diagnostics exists; omitted stages remain NOT_OBSERVABLE. |
| S3 direct eligibility and coarse source types | DERIVABLE_DETERMINISTICALLY | Replay current predicates on frozen metadata and bound code lineage. |
| Sphinx page/section subtype | DERIVABLE_DETERMINISTICALLY | Requires same-version object lookup or exact-backing record; selected Evidence alone lacks object_type. Otherwise NOT_RELIABLY_OBSERVABLE. |
| Admission decision and successful parent-to-backing link | EXISTING_AUTHORITATIVE_FIELD | EA_ADMISSION.decisions after ID/count reconciliation, plus admitted IDs and backing IDs. |
| Exact S4 attempted substage for all rejection codes | REQUIRES_SMALL_OBSERVABILITY_CHANGE if essential | Existing reason alone conflates pre-lookup bounds and later bounds or lookup failure stages; do not require this extra field unless artifact qualification shows the audit cannot otherwise answer its question. |
| A0/A1 exposure and V1/V2 review exposure | EXISTING_AUTHORITATIVE_FIELD | Complete EA_ADMISSION/A1_INPUT/V1_INPUT/V2_INPUT stage events, when present in compatible immutable artifacts or captured through the supported non-formal novel_dev QA/full path. A1 absence means NOT_APPLICABLE only when it was not executed. |
| G2 final valid coverage and final claim mapping | EXISTING_AUTHORITATIVE_FIELD | Final answer_point_audit and result, with status/lineage checked. |
| V1 PARTIAL per-relation validated dispositions | DERIVABLE_DETERMINISTICALLY only with complete frozen V1 input/output, evidence, canonical points, and exact G2 code; otherwise REQUIRES_SMALL_OBSERVABILITY_CHANGE | The saved V1_OUTPUT validation summary has status/error codes, not the full per-round receipt. |
| Corpus-wide relevant evidence absent from retrieval | NOT_RELIABLY_OBSERVABLE | Needs an independent reviewed corpus search; never infer it from selected evidence. |
| Citation-quality factual sufficiency | NOT_RELIABLY_OBSERVABLE from telemetry alone | Requires bounded independent human review. |

The existing _trace_admission fallback labels an admitted selected ID
DIRECTLY_CITATION_ELIGIBLE and an unadmitted selected ID
INCOMPLETE_SPHINX_LOCATOR, then overlays _ea_cache.decisions by positional
zip. The fallback code is a trace-only label, not an _admitted_evidence
decision code. On exact-backing success, the selected parent ID is absent from
admitted_evidence_ids and can still appear in rejected_evidence_ids while its
decision is RESOLVED_EXACT_BACKING. Therefore rejected_evidence_ids is a
literal ID-nonmembership list, not an authoritative admission-rejection count.
Positional merge also needs a length/order/ID consistency check before using
reason codes. Mark inconsistent or incomplete traces NOT_OBSERVABLE and report
their count; do not silently coerce them into NO_VALID_BACKING.

The bounded QA stage-trace path for explicit non-formal novel_dev runs is now
available through run_evaluation; its enablement was not an admission-policy
change. Explicit per-selected resolution_applicable,
resolution_attempted, decision source/substage, consistent parent/backing
disposition fields, and bounded per-round G2 validated states are conditional
improvements only. Reuse authoritative fields or exact-lineage deterministic
replay when sufficient; request an additional field only if artifact qualification
shows its absence prevents a reliable audit answer. Any such future task must
preserve admission decisions, provider contracts, and product behavior. This
design itself changes no instrumentation.

## 7. Current admission reason-code accounting

The complete _admitted_evidence selected-item outcome set observed in source
is below. Nested candidate_rejections uses VERSION_MISMATCH,
CONTENT_RELATION_NOT_ESTABLISHED, INVALID_LOCATOR, and BOUND_EXCEEDED;
these are child diagnostics, not additional selected-item outcomes.

| Code | Current meaning and owner | Audit interpretation |
|---|---|---|
| DIRECTLY_CITATION_ELIGIBLE | Selected item passes the current direct citation predicate; admission S3/S5. | Success, not proof of factual support. |
| RESOLVED_EXACT_BACKING | One exact section meets source/version/content/locator checks; parent maps to admitted backing at S4/S5. | Success via backing; count parent once. |
| INVALID_LOCATOR | Selected non-direct item lacks usable page URL/date or has a section path that cannot enter page resolution; child diagnostics may also report locator mismatch. | Expected provenance safety until reviewed metadata proves a generic mechanical limitation; possible data-integrity issue. |
| CONTENT_RELATION_NOT_ESTABLISHED | Missing parent object ID, page/content/locator mismatch, child identity/containment mismatch, or conflicting existing evidence prevents exact relationship. | Expected safety; investigate corpus metadata/content integrity before considering policy. |
| BOUND_EXCEEDED | More than four candidate pages, more than sixteen children, or excessive child text length. | Expected cost/safety bound; exact substage may be unobservable without extra trace. Repeated generic limitation is only a candidate. |
| LOOKUP_FAILED | Manifest/backing read or a per-candidate processing exception prevents resolution. | Infrastructure or data-integrity uncertainty; not a product-quality failure by default. Exact failing substage may be unobservable. |
| VERSION_MISMATCH | Manifest, page, selected item, or child lacks the required unique source/snapshot/version agreement. | Expected provenance safety; data/corpus issue may be primary. |
| AMBIGUOUS_BACKING | More than one child qualifies; no winner is chosen. | Expected ambiguity safety, not an automatic policy defect. |
| NO_VALID_BACKING | No selected page/qualified child can provide unique exact backing after the applicable path; also the initial default before more specific resolution. | Requires stage and candidate detail; never equate with semantic insufficiency or policy defect alone. |

INCOMPLETE_SPHINX_LOCATOR is only the generic trace fallback before decision
overlay. Treat it as OBSERVABILITY_LIMITATION unless the authoritative
selected-item decision can be reconstructed. Do not aggregate it with the nine
runtime outcomes.

## 8. Source-type stratification

Use qa._evidence_source_types on source metadata for the established coarse
paper/documentation/code/workflow/readme tags. Retain multiple tags where that
function returns them. Add an audit-only subtype from authoritative object_type
and locator metadata: Sphinx page, Sphinx section, README/prose, workflow,
paper, code, or other. For Sphinx subtype, require a same-version object
record or explicit backing record; source_id alone proves the Sphinx family,
not page versus section. Record UNKNOWN_SUBTYPE if object_type is unavailable.
Do not change the existing classifier or force every documentation item into
a Sphinx category. Stratify both selected-parent and resolved-backing types,
but keep parent as the evidence-rate unit.

## 9. Relation, check, and round linkage

For named points, use runtime_answer_points.required_relations and exact
relation_id. A VALID named disposition can be admitted-backed satisfied,
admitted-backed unsatisfied, visible-only, or insufficient/ambiguous.
LOCAL_INVALID, MISSING, and CONFLICTED remain G2 structural categories,
reported separately and excluded from admission-state denominators.

For relation-free points, use valid relationship_checks in supplied order
within V1 or V2. If any ordinary check invalidates its owning point under
G2, none of its siblings is promoted to an accepted semantic disposition.
Do not compare ordinary ordinals across rounds or runs as stable obligations.

Report A0 and A1 admission/exposure separately, including A1's narrower
target evidence. In production, A1 normally reuses the cached admitted
projection; its EA event is a separate use, not a second independent
admission decision. Report V1 and V2 dispositions separately; a V2 valid
review can replace V1's local failure only by its own full canonical
validation. The final question-level outcome uses the last executed valid
round and retains prior-round diagnostics without double counting.

## 10. Root-cause taxonomy

Assign one primary cause per auditable gap and optional secondary causes.
Use UNRESOLVED when evidence cannot separate owners:

| Primary cause | Minimum evidence; established taxonomy link |
|---|---|
| RETRIEVAL_SELECTION | Relevant item absent from candidate/selection path with trustworthy stage proof; R1 recall, R2 ranking, or R3 selection as evidenced. Not G3 policy evidence. |
| ADMISSION_DATA_INTEGRITY | Selected relevant item has demonstrably wrong/incomplete source, version, locator, or backing data under the intended rule; admission-path data owner. |
| ADMISSION_POLICY | Tier 2 plus an independently verified, generic admission-mechanics blocker despite sufficient citation-quality provenance. Do not assign from a rejection code alone. |
| SEMANTIC_INSUFFICIENCY | Available/admitted evidence does not actually support the requested relation; C1/V1 as appropriate. |
| VERIFIER_FALSE_REJECTION | Independent support exists but a valid verifier judgment rejects it; V1, with G4 conservatism as a later owner. |
| CLAIM_MAPPING_OR_SUPPORT | Claim or supporter lacks validated mapping, citation, or support despite admission; V1/V2. |
| GENERATION_OR_REVISION | Admitted, exposed backing was not converted into a supported claim by A0 or the one bounded A1 revision; A1 when that stage ran. |
| QUESTION_DECOMPOSITION | Requested relation/point missing or wrong before admission analysis; D1. |
| INFRASTRUCTURE | Backing store/manifest unavailable or execution failed; do not score as admission policy quality. |
| OBSERVABILITY_LIMITATION | Trace, identity, decision alignment, or per-round validity cannot be established. |
| NOT_APPLICABLE | No selected admission opportunity or no valid relevant disposition for this mechanism. |
| UNRESOLVED | Competing causes remain after the available evidence and bounded review. |

ADMISSION_POLICY can be primary only after selected identity, valid semantic
linkage, factual support, version/provenance sufficiency, and mechanical
rejection ownership are independently established. A single exposed failure
cannot set the policy rule or threshold. A repeated generic pattern or a
structurally generalizable mechanism is needed for a policy-change
recommendation. Existing R1/R2/R3/D1/A1/V1/V2/C1 labels are links where
justified, not forced classifications.

## 11. Cohort and artifact plan for a separately authorized audit

Pre-register the eligible reviewed novel_dev dataset snapshot, product
lineage, mode, artifact requirements, sample cap, and deterministic selection
seed before opening any case result. Use a census when at most 30 eligible
reviewed question IDs exist. Otherwise rank all eligible IDs by a fixed
seeded digest of dataset identity and question ID, and select the first 30.
Eligibility uses only reviewed status, dataset identity, and stable ID,
never artifact availability or result status,
admission code, source type observed after QA, or historical exposed failure.
If too few auditable IDs exist, report coverage and INCONCLUSIVE; do not
backfill with hand-picked failures.

For each preselected ID, reuse an immutable existing production QA run only
if its manifest/record binds the exact G2-or-successor product-behavior
lineage, admission implementation, retrieval/index/source identity, dataset
and question identity, production mode, same-run selected evidence, EA_ADMISSION,
executed A0/A1 and V1/V2 events, final G2 coverage/mapping state, and trace
completeness. A pre-G2 artifact cannot establish current G3 relation-local
behavior merely because its question text is unchanged. Qualify artifacts only
after the outcome-blind cohort is frozen. Missing artifacts do not change
cohort membership. Existing exposed benchmark/development artifacts
may be described in a separately labeled secondary diagnostic appendix,
never pooled into primary rates or used to choose a rule. novel_validation
and holdout remain inaccessible.

The trace-capability preflight found no current-lineage novel_dev QA stage-trace
artifact class, and the supported capture prerequisite is complete. After
separate scoped-audit authorization, freeze the cohort
outcome-blind and inspect compatibility for those selected IDs. Path A: if
every selected ID has sufficient compatible immutable artifacts, reuse them.
Path B: otherwise use the supported bounded non-formal novel_dev path to
capture only missing preselected development artifacts within the separately
authorized audit execution scope. Do not rerun model stages for convenience or use an
undocumented QAAgent._run_detailed(..., capture_stage_trace=True) invocation
to bypass _configure_stage_trace. An internal call is not the supported audit
artifact path. Potentially reusable artifacts, if discovered by metadata
alone, are not declared sufficient before selected-ID qualification. If stage
capture remains incomplete, stop semantic classification and report
NOT_OBSERVABLE or INCONCLUSIVE rather than assuming another policy change.

Required future artifact bundle per question: immutable dataset/run/lineage
identity, same-run retrieval trace and selected evidence, source/object
metadata for subtype joins, EA_ADMISSION stage events, A0/A1 and V1/V2
inputs/outputs if executed, final G2 answer-point audit, claim mapping
audit, result, and trace capture status. Resolve projected evidence through
qa_stage_trace.evidence_registry. Do not treat an absent optional stage as
missing data when it was legitimately NOT_EXECUTED. Retain trace-incomplete
questions in the frozen cohort denominator; mark missing stage authority
NOT_OBSERVABLE, exclude them only from the corresponding stage-specific
auditable denominator, and report their count and reason. Never replace them
with easier-to-trace questions or infer NO_VALID_BACKING from a missing trace.

## 12. Metrics and denominators

Publish counts with each denominator and an explicit unknown count. Do not
mix phase or round scopes:

| Metric | Numerator / denominator |
|---|---|
| A0 selected evidence admission rate | Selected IDs directly admitted or resolved to backing / all S2 selected IDs with complete A0 admission decisions. |
| A0 selected evidence rejection rate | Selected IDs with neither direct admission nor resolved backing / the same complete-decision selected-ID denominator. |
| A1 target exposure | Admitted backing IDs included in executed A1 model input / admitted backing IDs from the complete A0 decision set for those A1 questions. Report target restriction separately; do not count cached decisions as a second admission run. |
| Direct, resolved, and each rejection code | Selected IDs with that reconciled final decision / selected IDs with one validated final decision; also publish raw counts by source type. |
| Question selected-but-unadmitted incidence | Questions with at least one such selected ID / questions with complete S2/S5 evidence; report excluded/unknown questions. |
| Disposition admission states | VALID named relations or accepted ordinary checks with each admission_state / all VALID named relations or accepted ordinary checks in that round, reported separately for named and ordinary. |
| Traceable visible-only linkage | VALID visible-only dispositions whose basis joins a selected unadmitted parent / all VALID visible-only dispositions with complete basis and admission trace; report untraceable separately. |
| Tier 1 incomplete-question incidence | Questions with final incomplete point and at least one Tier 1 admission-gap link / questions with complete final valid-disposition and admission trace. |
| Tier 2 candidate incidence | Questions with at least one adjudicated Tier 2 candidate / questions with complete admission/semantic trace and completed candidate adjudication where applicable; report unresolved reviews separately. |
| Admission-policy-primary incidence | Questions whose final incompleteness is primarily ADMISSION_POLICY after adjudication / questions with an adjudicated primary cause. |

Report evidence-level, relation/check-level, and question-level tables
separately. A0/A1 and V1/V2 tables are separate; the final question summary
deduplicates round and parent/backing lineage. Stratify selected-parent
outcomes by coarse source type, admission subtype, reason code, and
trace-completeness tier. Always report the fixed cohort size beside each
stage-specific auditable denominator and unknown count. Never present a
cohort rate as corpus-wide prevalence without a representative sampling
argument.

## 13. Manual review and decision gate

Only Tier 1 links and targeted ambiguous classifications receive bounded
manual review. The worksheet records the selected/basis IDs and exact
source-version/locator excerpts, then asks independently: (1) Is the
item relevant to this requested relation? (2) Does the text actually
establish it? (3) Is provenance/version identity sufficient and
unambiguous? (4) Could it be cited safely under the intended provenance
model? (5) Is the block due to admission mechanics rather than semantic
content, retrieval, mapping, or malformed verification? Reviewers do not
see benchmark expected answers as implementation guidance. Two reviewers
independently assess each Tier 2 candidate; record both judgments and a
short adjudication of disagreements. Smaller Tier 0 frequency-only items
need no manual review.

The audit emits machine-readable evidence and linkage records, an aggregate
summary with cohort/lineage and trace completeness, a mechanism table
with frequency/source types/tier/primary owner/genericity, and one primary
decision:

- NO_CHANGE: no Tier 2 candidate survives independent review, or observed
  gaps are valid provenance rejection, heterogeneous, or primarily
  retrieval/semantic/downstream owned.
- OBSERVABILITY_ONLY: missing or contradictory stage evidence prevents a
  reliable ownership estimate; propose a separate trace-only task.
- DATA_OR_CORPUS_REPAIR: repeated metadata/content/version defects explain
  rejection under an otherwise sound policy.
- ADMISSION_POLICY_CHANGE_JUSTIFIED: independently reviewed Tier 2 evidence
  establishes the same generic mechanical blocker in at least two
  independent primary-cohort questions, or proves a source-type-wide
  structural limitation without relying on one case's expected answer;
  a precisely scoped rule could preserve provenance safeguards. Two cases
  are a minimum replication condition, not an automatic trigger: require
  clear admission ownership, citation/provenance safety, denominator context,
  and no better retrieval, data-integrity, or semantic explanation.
- INCONCLUSIVE: sample, trace, relevance, or adjudication evidence cannot
  support a stronger decision.

These are audit conclusions, not automatic authorization to implement a
policy change. Any future counterfactual requires separate approval after
observational evidence: vary exactly one admission condition while holding
selected evidence, source/version/provenance, decomposition, and G1/G2
semantics fixed. Do not use protected data for repair and never run an
"admit everything" comparison.

## 14. Alternatives, sequence, and acceptance

Selected-evidence-only inspection is cheap and has a clean admission
denominator but cannot locate upstream R1/R2/R3 losses. A full
retrieval-funnel audit has stronger attribution but depends on complete
same-run traces and object metadata. Outcome-first inspection of only
insufficient answers is efficient for diagnosis but selection-biased and
cannot estimate frequency. The selected architecture uses S2 as the
primary denominator, joins S0/S1 when authoritative, and permits an
outcome-focused secondary drilldown only after the outcome-blind cohort
is fixed.

Future execution sequence: (1) separately authorize the scoped audit and
freeze the reviewed novel_dev cohort outcome-blind; (2) qualify compatible
immutable artifacts only for the frozen IDs; (3) reuse them where sufficient
and capture only missing preselected development artifacts through the
supported path within the authorized scope; (4) build deterministic stage
and reason records; (5) review Tier 1/Tier 2 candidates; (6) publish
denominators, unknowns, taxonomy, and one decision.
Stop or return INCONCLUSIVE when the required trace or provenance
cannot be established. Do not silently expand the cohort.

The methodology is ready for a separately authorized scoped audit because
it separates availability from authority, identifies proof and
NOT_OBSERVABLE boundaries for S0–S8, exhausts current admission
outcome codes, excludes retrieval/G2/G4 failures from policy evidence,
defines outcome-blind sampling and denominators, and allows NO_CHANGE
or INCONCLUSIVE. The supported novel_dev QA stage-trace path is available;
selected-ID artifact completeness remains for the separately authorized
audit to establish. This document neither executes nor authorizes that audit.

Future identity handling is conditional: a trace-only change should
record its artifact/trace schema identity without bumping provider
prompt/schema identity unless those bytes change; metadata/corpus
repair requires its own source/index and compatibility provenance;
an admission-policy runtime change creates a new product-behavior
lineage and proportionate evaluation authority; a provider prompt or
schema change must use the existing version/fingerprint mechanism.
None of those identities change in this design task.
