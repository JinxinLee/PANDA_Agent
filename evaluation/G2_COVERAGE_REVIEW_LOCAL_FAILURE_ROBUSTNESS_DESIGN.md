# G2 — Coverage Review Local-Failure Robustness Design

**G2 = DESIGN COMPLETE / IMPLEMENTATION READY.** This is a design record, not an implementation or an empirical result. Inspected repository HEAD: `38d43cd988763912127b70cd12d1b253e3b2f79e`; product-behavior lineage: `9979b631191f4cf11adca1b63242ed08c45c9ea1`.

## 1. Decision and alternatives

Select **canonical relation-local validation with point-local fallback**. Validate the review envelope and claim/mapping inventory once. Then visit canonical points in canonical order. A relation-bearing point uses its question-derived relation IDs to isolate malformed dispositions; a relation-free point uses its existing ordinary C1 contract and becomes locally invalid if any ordinary check is malformed. A bad item never becomes a valid semantic verdict. Surviving judgments require independently validated ownership, claim mapping, support, and exact provenance.

| Option | Decision | Reason |
|---|---|---|
| Point-local validation only | Reject as insufficient | Simple between-point isolation, but discards a valid named sibling and its independently grounded A1 target. |
| Canonical relation-local validation, ordinary point-local fallback | Select | Uses G1 host-owned IDs where they exist and stops at the point boundary where ordinary-check identity/inventory is verifier-derived. |
| Generic nested-row sanitizer | Reject | Dropping or repairing arbitrary rows can silently turn incomplete inventories, quotes, or supporter sets into positive verdicts; it creates a second trust path. |

## 2. Existing flow and boundaries

`_validate_coverage_satisfaction` in `src/panda_agent/qa.py` currently validates a complete production review via `_validate_answer_point_review`, then checks all points and checks. One `ValueError` makes production coverage globally invalid. `_verify` can rebuild a negative coverage projection to preserve independently valid claim support and claim-to-point mappings; it cannot preserve valid coverage siblings. `_after_verify_route` uses the production target lists and the existing `revision_count < 1` limit. `_finalize` can render verified claims with `insufficient_evidence` when production coverage remains incomplete.

G2 changes only deterministic validation and its production-mode consumption. It does not change question decomposition, evidence admission, retrieval, semantic thresholds, provider calls, public claim DTOs, Gold, calibration, evaluator scoring, or the experimental `runtime_e1_v2` path. Historical exposed cases motivate a generic class of failures, never a rule.

## 3. Preserved G1 authority

- Canonical answer points and `required_relations` are fixed from the raw question before retrieval. The review cannot add, remove, reparent, or reconstruct a required relation by prose. IDs are exact `point.N.rel.M` host IDs.
- A relation-free point uses only `relationship_checks`; a relation-bearing point uses only `required_relation_checks`. No dual completeness authority, and no `claim.relation_ids`.
- Evidence IDs must be known; every basis quote must be nonempty, within bound, and an exact contiguous substring of that evidence text. Admission, citation eligibility, mapped supported/relevant supporters, and citation of every required basis remain unchanged.
- A locally invalid required relation stays in the canonical inventory and blocks point completeness. Its state is a validator failure, not a model-authored `INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE` disposition. A malformed item is never `satisfied=true`, `complete=true`, or A1-authorized by salvage.
- One bounded A1 revision remains. V2 rechecks **all original canonical points and relations**, including those invalid or omitted at V1. Composer input remains verified claims only. E3 stays experimental.

## 4. Isolation proof and internal receipt

Raw model output stays immutable and untrusted. A small production-only validation result, the **coverage receipt**, is built from it; it is not a provider response or a rewritten review. An item is localizable only if (1) its canonical parent is known, (2) a named relation's exact canonical ID is known when relation-level isolation is claimed, (3) the row boundary is parseable, (4) no identity collision can change a surviving sibling's interpretation, and (5) surviving claim mappings, support and provenance validate independently. Shared evidence or a shared claim does not itself couple two checks: each check must independently validate all of its own edges and basis.

The receipt contains: `status` (`VALID`, `PARTIAL`, `REJECTED`); the single validated claim-to-point map and claim-support verdicts; one canonical-order point entry with `state`, derived `complete`, derived supporter union and derived scope when knowable; one canonical-order relation entry for each required relation with `state`, and validated model disposition/basis/supporters **only if valid**; host-derived missing point IDs; eligible A1 targets; and bounded structured errors. Item states are `VALID`, `LOCAL_INVALID`, `MISSING`, or `CONFLICTED`. `VALID` means structurally/provenance-valid, not necessarily satisfied. An honest, valid unsatisfied or uncertain disposition remains `VALID` and incomplete. `MISSING` is host detection of an omitted canonical row; it does not invent an `admission_state` or model judgment.

| Candidate level | Safe containment rule |
|---|---|
| Review | Envelope, canonical-state or cross-owner integrity failure: reject all coverage. |
| Point | Known unique parent but uncertain child inventory, including malformed ordinary checks: invalidate that point. |
| Check / required relation | Exact canonical relation owner and intact sibling boundaries: invalidate that relation; ordinary checks fall back to point. |
| Basis item | Identify the bad item for diagnostics, but invalidate its whole owning check; never drop only the item. |
| Supporter | Identify the bad edge for diagnostics, but invalidate its whole owning check; never drop only the supporter. |
| Claim support / mapping | Validate once through the existing independent inventory; a malformed global mapping inventory defeats model-judgment salvage. |

The receipt is transient `_verify` state. Persist only a bounded diagnostic summary (status, affected IDs, stable reason codes and derived point completion) through the existing answer-point audit/O1 trace; do not persist full malformed review text as an accepted review. The raw provider output remains in the existing V1/V2 trace where tracing is already enabled. A small G2-specific error record has `scope` (`REVIEW`, `POINT`, `RELATION`, `CHECK`, or `AGGREGATE`), optional canonical owner IDs, and a stable `reason_code`; no exception-message parsing or generic error framework is needed.

## 5. Global envelope and claim/mapping authority

First validate the raw review's closed top-level shape, required fields and types, the nonempty top-level coverage array within its existing bound, `supported`/`reason`, unsupported/irrelevant claim inventories, and the complete claim-to-point mapping inventory. Validate child-list types at the owning point after its identity is established. Validate canonical runtime points before consuming model output: exact unique point/relation IDs, parent ownership, schema and bounds. Canonical corruption is an **internal integrity failure**, not a model review defect; fail closed and record it separately. An unparseable review, unusable top-level inventory, mapping collision, or non-isolatable row boundary rejects coverage for every point.

Extract the existing `_validate_answer_point_review` claim/mapping checks into one shared narrow helper used by the production validator and its current salvage path. Do not create a second mapping interpretation. Reviewable claims still exclude deterministic claim errors; a mapped supporter must be in the validated reviewable set and neither unsupported nor irrelevant. If a coverage-local or coverage-global defect occurs **after** this helper succeeds, the existing independent claim-support/mapping salvage remains available. If the helper fails, no model claim/mapping judgment is salvaged; deterministic claim-error guards still apply. `supported=false` with no independently valid explanation remains the existing global support failure and cannot be rescued by coverage locality.

`missing_answer_point_ids` is a required, well-typed, unique inventory of canonical point IDs. Unknown/duplicate IDs or an unusable type are review-fatal. If it is structurally valid but disagrees with independently derived point completeness, record `MISSING_COMPLEMENT_MISMATCH` and use the **host-derived** complement. This field never creates or clears an obligation.

## 6. Point and required-relation handling

Index raw point rows by exact `answer_point_id` before validating their contents. A missing canonical row produces a `MISSING` point; other uniquely owned points may survive. A uniquely identified but malformed point with broken child-list shape, wrong active path, unparseable check boundary, or extra/unknown named relation is `LOCAL_INVALID`; other points may survive. An unknown or duplicate point ID, absent/unusable identity, cross-point ownership collision, or ambiguous attribution rejects the whole coverage review. Count raw rows against limits before discarding invalid rows, so malformed rows never bypass bounds.

For a relation-bearing point, `relationship_checks` must be an empty list. A nonempty ordinary list makes that point locally invalid; ordinary prose cannot replace canonical relations. Index parseable named rows by exact canonical ID. A missing ID becomes `MISSING`; duplicates of one canonical ID make that relation `CONFLICTED` without selecting a winner. A uniquely identified row with bad fields, basis, supporter or disposition becomes `LOCAL_INVALID`. Valid siblings survive even though the parent remains incomplete. A row with an unknown ID under a uniquely known parent invalidates that point; do not guess which canonical relation it meant. A row claiming another canonical parent's ID, or a foreign-prefixed ID with unclear ownership, is a whole-review ownership collision. A named row lacking a usable ID invalidates its known parent point, because its target cannot be determined. These wider boundaries prevent a malformed sibling from being silently ignored as an optional extra.

For a relation-bearing point, `complete=true` only if **every** canonical required relation has one `VALID`, admitted-backed, satisfied disposition under the unchanged G1 contract. No omitted or conflicted relation is removed from the denominator. If all child dispositions are valid, derive `scope_status` exactly as G1 does: uncertainty in any child implies `INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE`, otherwise `ESTABLISHED`; visible-only alone does not make scope unknown. If any child is invalid/missing/conflicted, derived scope is unknown for the point, but independently valid admitted-backed unsatisfied siblings can still be A1 candidates.

## 7. Relation-free ordinary checks

Ordinary checks have no question-derived canonical check IDs. The host cannot prove that valid-looking siblings are the complete necessary inventory after one check is malformed. Therefore bad basis, invalid supporter, duplicate normalized `relationship_text`, bad check fields, count overflow or incompatible `scope_status` makes the **whole owning point** `LOCAL_INVALID`. Other uniquely owned points survive. Valid ordinary siblings can be retained in bounded diagnostics to explain the failure, but cannot make their parent complete or become A1 targets while its ordinary inventory is invalid. Do not use their partial set to infer that all necessary checks were seen.

When the entire ordinary inventory validates, keep G1's established/nonempty/1–4-check rules, uncertainty coupling, supporter requirements, and admitted-backed all-check completeness. `OVERFLOW` remains incomplete under the existing contract; it is not a way to approve a truncated check list. This is malformed-output containment, not G4 tuning of valid insufficiency judgments.

## 8. Basis, supporter and disposition checks

The smallest **safe semantic** failure unit for a bad basis item or supporter edge is its owning check, because dropping the item/edge could falsely preserve `satisfied=true`. For named checks, that invalidates the canonical relation; for ordinary checks, the point. Never trim, normalize, substitute, or accept a bad quote. Apply the existing 0–2 distinct basis, exact quote, admitted/visible rules, 0–8 unique supporters, point 32-supporter, and question 20-active-check bounds to the raw bounded structure and to surviving checks. An attributable per-check or per-point overflow invalidates that owner; unbounded/global overflow or an unassignable row rejects the review.

An unknown evidence ID, duplicate basis ID, empty/non-exact/overlong quote, unadmitted basis claimed admitted, or visible-only claim with no indispensable unadmitted basis invalidates its check. Likewise an unknown, duplicate, unsupported, irrelevant, wrong-point, or non-citing supporter invalidates its check; no bad edge is silently removed. Invalid `admission_state`, `satisfied=true` without a valid supporter, or `VISIBLE_ONLY`/`INSUFFICIENT_OR_AMBIGUOUS` with satisfaction or supporters invalidates that check. Valid admitted-backed unsatisfied checks retain their existing meaning and may qualify for A1; valid visible-only and uncertain checks remain blocked.

## 9. Derived aggregate fields

Only fully validated child judgments can yield a positive aggregate. Derive each point's ordered unique supporter union from its active valid children in supplied claim order; derive relation-bearing scope from all valid named children; derive `complete`; then derive the missing-point complement from all canonical points. If the derived point supporter union exceeds the existing 32-claim bound, invalidate that point and block its targets; a merely overlong model union is an aggregate defect when the independently derived union remains within bound. Model `supporting_claim_ids`, `scope_status`, `complete`, and `missing_answer_point_ids` are consistency assertions, not independent authorities. If all applicable children validate and a model aggregate disagrees, record a stable aggregate mismatch and use the derived value, including a positive value supported by **all** valid children. The raw contradiction remains auditable. A malformed aggregate type cannot create a positive result; it may be ignored as an aggregate-only defect only when child inventory, ownership, support and provenance are complete and independently valid.

If a child is invalid, missing or conflicted, the parent is incomplete regardless of model flags. Its validated sibling supporters remain only where their own edges validate; the model's point-level supporter union is not used to rescue the parent. For ordinary points, a contradictory `scope_status` is not merely redundant: it changes the interpretation of verifier-derived checks and invalidates the point. For named points, a scope mismatch is an aggregate-only defect **only when all named children are valid**; otherwise scope is unknown and the point is incomplete. A structurally invalid top-level missing-point inventory remains review-fatal as specified above.

## 10. `_verify`, A1, V2 and finalization

Production `_verify` consumes the receipt, never raw point rows, to build `verified_mappings`, supported claims, derived `missing_answer_point_ids`, `revisionable_relationships`, and audit fields. A `PARTIAL` receipt sets `coverage_complete=false`, `coverage_evaluable=false` at whole-review scope, `coverage_blocked=true`, and exposes per-point/per-relation evaluability. Set the existing `coverage_satisfaction_status` to `VALID`, `PARTIAL`, or `INVALID` (for `REJECTED`), and V1/V2 trace validation status to `ACCEPTED`, `PARTIAL`, or `REJECTED`. On partial/rejected reviews, keep the existing audit's `answer_point_coverage` as `None`; attach only the bounded validated summary, not raw malformed rows. `VALID` can still contain honest incomplete points. `REJECTED` keeps every canonical point missing and the existing independent claim/mapping salvage only when its shared validation succeeded. The production target router remains target-list driven; do not make a false whole-review `coverage_evaluable` flag suppress a validated target.

A1 receives a named relation only when its own exact canonical identity, admitted basis, unsatisfied model disposition, claim/mapping context and independence all validate. A malformed relation never authorizes itself. A valid admitted-backed unsatisfied sibling may authorize the one existing A1 call even when another relation in its parent is locally invalid. Ordinary targets require their **whole ordinary point** to validate. Unsupported-claim repair remains possible only for an independently validated claim verdict and mapping with eligible admitted citations; no mapping inferred from invalid coverage may authorize repair. If ownership/mapping integrity fails, there are no A1 targets. No retry, model repair pass, relation-by-relation call or extra retrieval is added.

After A1, V2 builds a fresh receipt against the unchanged full canonical contract; it does not carry forward V1's truncated target projection or treat a V1 validation error as a model disposition. V2 may clear an earlier failure only by returning a fully valid review. Final `answered` still requires all canonical points complete and existing non-coverage gates satisfied. If a point remains missing, final status is `insufficient_evidence`; independently verified claims may render under the existing partial-answer rule, but malformed-review diagnostics and obligations never become composer facts. Existing hard guards and claim anti-resurrection rules remain in force.

Example: `point.1.rel.1` valid satisfied, `point.1.rel.2` bad quote, `point.2` fully valid and complete. The first relation and `point.2` survive; `point.1.rel.2` is `LOCAL_INVALID`, `point.1` is incomplete, host missing IDs contain only `point.1`, and whole-review `coverage_evaluable=false` with per-item validity recorded. No A1 target comes from the bad quote. The final result is `insufficient_evidence` with only independently verified/renderable claims, subject to existing hard guards. If row ownership instead collides across points, coverage is `REJECTED`, all canonical points are missing, no coverage-derived A1 target survives, and only separately validated claim/mapping support may render.

## 11. Whole-review rejection boundary and observability

Reject the entire coverage review for a non-object/unparseable envelope; missing or wrong-type required top-level fields; duplicate/unknown/unusable top-level claim or missing-point inventories; inconsistent claim/mapping authority; unknown/duplicate/identity-less point rows; cross-parent relation ownership; ambiguous item boundaries; non-attributable or global bound overflow; or contradictory ownership that could change a sibling's meaning. Reject before any positive coverage or A1 target is emitted. Canonical runtime inventory corruption is reported as a distinct internal integrity failure and also yields no coverage/A1 acceptance. Do not catch arbitrary exceptions as local review errors.

Diagnostics are bounded by canonical point/relation/check limits. Suggested stable codes include `REVIEW_SHAPE`, `MAPPING_INVENTORY`, `POINT_ID_COLLISION`, `POINT_MISSING`, `POINT_SHAPE`, `RELATION_MISSING`, `RELATION_DUPLICATE`, `RELATION_FOREIGN`, `BAD_QUOTE`, `UNKNOWN_EVIDENCE`, `DUPLICATE_BASIS`, `INVALID_SUPPORTER`, `INVALID_ADMISSION`, `AGGREGATE_MISMATCH`, and `GLOBAL_BOUND`. Keep `coverage_validation_status` and `whole_review_rejected` distinct; expose affected canonical IDs and derived completion, not full untrusted quotes. Existing O1 V1/V2 trace events should carry the summary without changing public QA semantics.

## 12. Provider contract and future identity

The provider response shape, simple JSON schema, model prompts, model roles and number of calls remain unchanged. G2 is a deterministic validator/runtime change under `production_answer_obligations_v1`; explicit shadow/runtime v2 paths remain unchanged. No dynamic per-question enums, conditional schemas, new provider role or fallback protocol are needed.

At implementation, keep `COVERAGE_SATISFACTION_SCHEMA_VERSION=coverage-satisfaction-v2`: the provider wire shape and valid-disposition semantics do not change; only host treatment of malformed output changes. Keep `PROMPT_SET_VERSION=3.12.0` and the existing prompt fingerprint value **if and only if** prompt/schema inputs remain byte-identical. `prompt_fingerprint()` binds prompt/schema payloads, not validator code; the material behavior change is identified by the implementation commit and source-tree identity in a future candidate/evaluation manifest. If implementation discovers a necessary provider prompt or schema change, revisit this decision explicitly and version/fingerprint that change through the shared authority. No identity is changed by this design document.

## 13. Planned deterministic adversarial matrix

All cases use neutral synthetic points, claims and evidence. `P` means the owning point, `R` one canonical required relation, `C` one ordinary check, and `ALL` the whole coverage review. “Other” means independently validated siblings/points and independently validated claim/mapping judgments. A1 consequence assumes the existing one-revision limit and admitted-backing rules. These are **planned expectations**, not executed results.

| Failure | Unit | Survives | Invalidated | A1 consequence | Completeness consequence | Whole reject? |
|---|---|---|---|---|---|---|
| Two points; one bad basis quote | R or P by point type | Other point | Owning R / ordinary P | Other valid targets only | Bad point missing | No |
| One point: `rel.1` satisfied, `rel.2` bad quote | R | `rel.1` | `rel.2` | Bad relation blocked | Parent missing | No |
| `rel.1` valid admitted-unsatisfied, `rel.2` bad basis | R | `rel.1` | `rel.2` | `rel.1` eligible | Parent missing | No |
| Valid point plus wrong-point supporter in another | R or P | Valid point | Owning R / ordinary P | Invalid owner blocked | Bad point missing | No |
| Valid named children; wrong model `complete` | Aggregate | Both children | Model flag | Valid targets unchanged | Derive from children | No |
| Valid children; wrong point supporter union | Aggregate | Both children | Model union | Valid targets unchanged | Derive union/completion | No |
| Malformed ordinary check among valid siblings | P | Other points; siblings diagnostic only | Ordinary P | No ordinary target from P | P missing | No |
| Duplicate ordinary `relationship_text` | P | Other points | Ordinary P | P blocked | P missing | No |
| Bad ordinary basis or supporter | P | Other points | Ordinary P | P blocked | P missing | No |
| Contradictory ordinary `scope_status` | P | Other points | Ordinary P | P blocked | P missing | No |
| Missing canonical point row, other rows unique | P | Other points | Missing P | P blocked | P missing | No |
| Unique known point ID, malformed child-list structure | P | Other points | Owning P | P blocked | P missing | No |
| Missing canonical relation row | R | Valid named siblings | Missing R | Missing R blocked; eligible siblings remain | Parent missing | No |
| Duplicate rows for one canonical relation ID | R | Other named siblings | Conflicted R | Conflicted R blocked | Parent missing | No |
| Unknown relation ID under known parent | P | Other points | Owning P | P blocked | P missing | No |
| Canonical relation ID nested under other parent | ALL | Validated claim/mapping only | All coverage | No coverage target | All points missing | Yes |
| Named row without usable relation ID | P | Other points | Owning P | P blocked | P missing | No |
| Unknown evidence ID | R or P | Other independent owners | Owning R / ordinary P | Invalid owner blocked | Bad point missing | No |
| Duplicate basis ID or basis bound overflow | R or P | Other independent owners | Owning R / ordinary P | Invalid owner blocked | Bad point missing | No |
| Empty, non-exact or overlong quote | R or P | Other independent owners | Owning R / ordinary P | Invalid owner blocked | Bad point missing | No |
| Admitted claim on unadmitted basis; visible-only claimed admitted | R or P | Other independent owners | Owning R / ordinary P | Invalid owner blocked | Bad point missing | No |
| Unknown, duplicate, irrelevant, unmapped or non-citing supporter | R or P | Other independent owners | Owning R / ordinary P | Invalid owner blocked | Bad point missing | No |
| Supporter bound overflow within a named/ordinary check | R or P | Other independent owners | Owning R / ordinary P | Invalid owner blocked | Bad point missing | No |
| Derived point supporter union exceeds 32 | P | Other points | Owning P | P targets blocked | P missing | No |
| Invalid admission; satisfied without supporter; uncertain/visible with supporters | R or P | Other independent owners | Owning R / ordinary P | Invalid owner blocked | Bad point missing | No |
| Valid named children; wrong model `scope_status` | Aggregate | Both children | Model scope field | Valid targets unchanged | Derive scope/completion | No |
| Valid children; well-typed but wrong known-ID missing complement | Aggregate | All valid children | Model complement | Valid targets unchanged | Derive missing IDs | No |
| Unparseable/non-object top-level review | ALL | No model judgments | All review judgments | None | All points missing | Yes |
| Duplicate/unknown point ID or ambiguous ownership | ALL | Validated claim/mapping only | All coverage | No coverage target | All points missing | Yes |
| Malformed top-level claim/mapping inventory | ALL | Deterministic claim guards only | All model review judgments | None | All points missing | Yes |
| Duplicate/unknown/untyped top-level missing inventory | ALL | Validated claim/mapping if independent | All coverage | No coverage target | All points missing | Yes |
| Canonical runtime inventory mismatch/corruption | ALL | No coverage/mapping authority | All review judgments | None | All points missing; internal error | Yes |
| Unassignable row boundary or global 20-check overflow | ALL | Validated claim/mapping only | All coverage | No coverage target | All points missing | Yes |

## 14. Implementation sequence, acceptance and next step

1. Extract one shared claim/mapping validation seam from the current production review path. Preserve its strict checks and the existing global-rejection support salvage semantics.
2. Add a production-only receipt builder with envelope/canonical preflight, exact point/relation indexing, current basis/supporter checks, derived aggregates and small reason-coded errors. Keep legacy, shadow and experimental paths unchanged.
3. Make production `_verify` and A1 consume only receipt-validated support, mappings, completion and targets; V2 rebuilds the receipt from the original canonical inventory. Preserve final partial-answer and composer boundaries.
4. Update existing G1/C1 tests that deliberately expect global rejection for now-localizable defects, while retaining their exact quote/provenance guards and whole-review collision cases. Add focused fake-provider/static tests for every matrix row, including positive sibling survival, whole-review rejection, raw-output immutability, one-revision bound, full V2 contract, claim-support salvage, O1 diagnostics and unchanged provider schema/fingerprint. No model call or scientific evaluation is needed for deterministic acceptance.

Acceptance requires: no bad quote acceptance; no lost canonical relation; unrelated valid point and valid named sibling survival only under the isolation proof; invalid owner blocked from completeness/A1; conservative ordinary-point handling; whole-review rejection on ambiguous ownership; one completeness path per point; full-contract V2; one validated mapping authority; unchanged G3/G4 semantics and provider-call count. These are test requirements for the separately authorized implementation, not results of this design task. No unresolved design question blocks implementation; provider compatibility and empirical benefit remain unverified until separately authorized work.

```text
G2 = DESIGN COMPLETE / IMPLEMENTATION READY
NEXT_TASK_RECOMMENDATION = G2 COVERAGE REVIEW LOCAL-FAILURE ROBUSTNESS IMPLEMENTATION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
