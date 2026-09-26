# G4 — Focused Development False-Insufficiency Diagnostic Design

## 1. Decision and scope

Select an **exposed, outcome-conditioned development diagnostic** as the next
smallest task. Freeze the answerability rubric in that task before opening any
of the six already exposed G3 insufficient cases. Independently adjudicate
their answerability, then join compatible same-run G3 artifacts to identify
the earliest causally wrong transition where possible. Reuse is preferred;
missing artifacts do not automatically authorize a new QA run. This document
does not execute the diagnostic, inspect case-level Gold/question/trace
content, curate data, implement observability, or change product behavior.

The G4 T0 [baseline](G4_DETERMINISTIC_FALSE_INSUFFICIENCY_BASELINE.md) passed
18/18 synthetic controls (seven should-answer, ten must-abstain safety, one
sufficiency seam). It establishes no real-model result. G3's
[scoped completion](G3_EVIDENCE_ADMISSION_ANSWERABILITY_GAP_SCOPED_AUDIT_COMPLETION.md)
finished 28/28 exposed `novel_dev` QA cases with complete stage capture, but
left six insufficient answers without a primary owner. Its 19
`AMBIGUOUS_BACKING` decisions, zero Tier 1/Tier 2 admission links, and scoped
`NO_CHANGE` policy verdict remain intact. None of these counts is a G4
false-insufficiency finding.

Use two independent judgments: **answerability** from reviewed obligations and
locked-corpus proof, and **pipeline outcome/causal ownership** from compatible
production artifacts. Neither judgment may determine the other. The
diagnostic preserves G1 point/relation completeness, G2 local-invalid
containment, G3 citation/admission safety, claim support, version safety, and
correct abstention. It does not propose public partial-answer semantics.

## 2. Answerability adjudication contract

Freeze this rubric before inspecting the six selected case contents. Record
exactly one high-level state per case: `ANSWERABLE`, `UNANSWERABLE`, or
`UNKNOWN`, with a reason and review references. A reviewer must reconstruct
the intended obligations from the question and independently reviewed Gold,
not adopt production's possibly faulty decomposition as truth.

| State | Required authority |
|---|---|
| `ANSWERABLE` | Product-language/scope fit; valid mandatory point and required-relation inventory; current locked-corpus evidence for **every** mandatory obligation; requested-version compatibility; exact citation-safe/admission-compatible provenance; and a complete supported response possible under current G1/G2/G3 rules. Preserve evidence/locator references and the support chain for each obligation. |
| `UNANSWERABLE` | Authoritative proof that at least one mandatory condition cannot be satisfied under the same contract: e.g. an established locked-corpus absence, unsupported relation, unsafe-only provenance, incompatible version, unavailable future outcome, unsupported universal proof, or out-of-scope request. Mere failure to find evidence in production retrieval is insufficient proof of absence. |
| `UNKNOWN` | Neither conclusion can be established with sufficient authority, including incomplete Gold/provenance, uncertain corpus search completeness, ambiguous obligation meaning, or unresolved version/scope identity. State the missing proof and do not force a verdict. |

For exposed `novel_dev`, the authority order is: (A) human-reviewed Gold
obligations/evidence **rechecked** against the current locked source/version;
(B) direct locked-corpus inspection with exact provenance; (C) deterministic
source/code/document search as a discovery aid verified against B; then (D)
production selected evidence and trace as *diagnostic observations only*.
Gold `expected_status=answered` is not sufficient by itself. Production
answer text, status, verifier dispositions, and model-generated text carry no
independent answerability authority. Gold wording is measurement annotation,
never a product implementation specification.

The minimum review record is keyed by case ID and product/corpus identity and
contains the one state, reason, reviewer/date, scope/version decision,
question-derived obligation inventory, Gold reference, per-obligation locked
source/locator and citation/admission proof or a documented impossibility,
and uncertainty fields. Store this review separately from a later pipeline
overlay; do not let outcome fields leak into answerability decisions. If a
reviewer already knows a case's outcome because G3 exposed it, document that
exposure, apply the frozen rubric, and require evidence references rather
than treating an asserted blind review as possible. A second reviewer should
resolve consequential disagreements when feasible; unresolved disagreements
remain `UNKNOWN`.

## 3. Lane A — exposed causal diagnostic

The existing six G3 `UNRESOLVED` insufficient cases are the bounded starting
set. Selection is **EXPOSED / OUTCOME-CONDITIONED DEVELOPMENT DIAGNOSTIC**:
after rubric freeze, review their question/Gold/locked evidence under the
authorized next task, then read only compatible case artifacts needed for
causal attribution. The six can reveal *which generic mechanisms exist*;
their false-insufficiency share is not a `novel_dev` prevalence estimate, a
generalization result, an independent confirmation, or a post-repair gate.
The other 22 G3 outcomes are not silently added to a population denominator.

If a same-run answered comparison is needed to understand a specific
transition, use at most a small matched set from the already exposed answered
G3 cases. Predeclare the need and select using existing metadata such as
intent, difficulty, representativeness, source topology, and relation
structure, with stable ID tie-breaking. Do not select based on appealing
trace contents or a desired conclusion. Matched controls are explanatory,
not prevalence controls. Do not use historical `g047` as a primary case; it
remains a non-gating exposed regression sentinel.

The [G3 aggregate result](G3_SCOPED_AUDIT_COMPLETION_RESULT.json) reports
28 complete stage traces, 28 completed QA results, and the same product
lineage; its referenced run manifest and review overlay are present at design
time. This qualifies the *starting artifact family*, not each causal field.
The later execution must check manifest/run/corpus/model/prompt identity and
per-case trace completeness before joining results, QA diagnostics, retrieval
trace, EA admission events, V1/V2 input/output, and G2 replay. A missing or
inconsistent field is `NOT_OBSERVABLE`, never inferred as a negative event.
Reuse the exact-lineage G2 replay discipline established in G3 for `PARTIAL`
reviews; surviving `VALID` children are diagnostic evidence, while
`LOCAL_INVALID`, `MISSING`, and `CONFLICTED` children cannot authorize an
answer or prove V1 semantic false rejection.

## 4. Causal attribution and decision gates

After answerability is fixed independently, compare the public result. Only
`ANSWERABLE + insufficient_evidence` is a
`FALSE_INSUFFICIENCY_CANDIDATE`. It is a mismatch requiring investigation,
not a product-repair authorization. For `UNANSWERABLE`, check correct
abstention and the opposing unsafe-answer family. A valid `version_conflict`
is a correct distinct refusal, not an insufficient-evidence event. For
`UNKNOWN`, report output descriptively without inserting the case into an
answerable or unanswerable denominator.

Terminology clarification: the earlier G4 design used “false-insufficiency
candidate” for a case with causal proof already in hand. This focused
diagnostic uses the term only for the **screening mismatch** defined above;
`attributed_false_insufficiency` and an **established generic mechanism**
retain the earlier design's stronger causal requirements. Historical G4 T0
and G3 results are unaffected.

Attribute a candidate to the **earliest necessary wrong transition**, using
the stable [evaluation-policy taxonomy](../docs/EVALUATION_POLICY.md):

1. Compare the independent question/obligation interpretation with Q1 query
   analysis, Q2 entity resolution, and D1 question-derived point/relation
   decomposition. A D1 omission may precede downstream evidence use even
   when the retrieval graph runs later; use causal precedence, not only event
   timestamp.
2. Trace independently verified required evidence through R1 candidate
   recall, R2 fusion/ranking, and R3 selection. Corpus evidence outside the
   selected set is not proof of V1 conservatism. Require same-run retrieval
   authority before asserting a stage was missed.
3. Reconcile selected evidence with G3 admission decisions and exact backing.
   Distinguish `ADMITTED_BACKING_AVAILABLE`, valid
   `VISIBLE_ONLY_WITHOUT_CITABLE_BACKING`, and
   `INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE`. Selected-but-unadmitted alone is not
   a defect. Under the current contract, unsafe-only evidence normally makes
   the case `UNANSWERABLE`; genuinely new generic admission-policy concerns
   are separate reopening candidates, not V1 or finalization findings.
4. Inspect admitted evidence presented to A0, generated claims, supported
   mappings, eligible A1 targets, revision result, and full V2 recheck.
   Classify generation/revision failures as A1 only after earlier evidence and
   obligations are shown sound.
5. Inspect valid semantic dispositions, G2 structural state, and final
   coverage. Assign V1 only for a *valid* disposition falsely rejecting
   independently supported admitted evidence. Malformed review containment
   is structural, never a valid semantic verdict.
6. Inspect the finalization path. Use `FINALIZATION_CONSERVATISM` only if all
   current-contract completion inputs are proved satisfied and finalization
   still refuses. Correct `coverage_blocked`, missing points, or an explicit
   safety guard must remain correct abstention. If the branch or an earlier
   competing cause cannot be established, retain `UNRESOLVED` or
   `OBSERVABILITY_LIMITATION` instead of guessing.

An **established generic mechanism** additionally requires compatible
same-run artifacts, a reproducible earliest divergence, explicit elimination
of competing earlier explanations, and a mechanism stated without case IDs,
symbols, locations, or wording as product logic. One candidate or one
ambiguous review does not justify repair. Independent semantic-family
replication strengthens a development mechanism claim; two nominal IDs from
one information need do not. A later change requires the owning layer, a
minimal generic seam, and G4 paired T0 safety controls that detect
overcorrection. No repair is authorized by this design.

## 5. Observability sufficiency and narrow fallback

The G3 run's full capture makes an initial Lane A diagnostic feasible, but
stage capture is best-effort telemetry and is not semantic authority. Qualify
each needed field for the selected case before using it:

| Causal field | Classification for compatible complete G3 artifacts | Qualification |
|---|---|---|
| Public status, claims, cited evidence, version/error output | `EXISTING_AUTHORITATIVE_FIELD` | Saved QA result; status never establishes answerability. |
| Production canonical points and final missing IDs | `EXISTING_AUTHORITATIVE_FIELD` | `question_decomposition` and `answer_point_audit`; independent review still owns intended obligations. |
| Final G2 validation, point/relation local states | `EXISTING_AUTHORITATIVE_FIELD` for final summary; `DERIVABLE_DETERMINISTICALLY` for per-round `PARTIAL` detail | Exact-lineage replay needs complete V input/output, canonical points, claims, and evidence. Otherwise `NOT_RELIABLY_OBSERVABLE`. |
| Selected evidence and ranked/candidate membership | `EXISTING_AUTHORITATIVE_FIELD` when complete | Same-run diagnostics/retrieval trace; absence from a bounded stage is not corpus absence. |
| Admission state and parent/backing linkage | `EXISTING_AUTHORITATIVE_FIELD` after reconciliation | EA_ADMISSION decisions/admitted IDs plus validated selected-item identity/order; inconsistent trace is unknown. |
| V1/V2 raw input/output | `EXISTING_AUTHORITATIVE_FIELD` when captured | Stage events and evidence registry, not their unvalidated semantic claims. |
| A1 execution, targets, revision and V2 result | `EXISTING_AUTHORITATIVE_FIELD` when captured | `revision_count`, A1_INPUT/OUTPUT/post-merge and V2; missing event is absence only with complete stage capture. |
| E3 execution/recovery | `NOT_APPLICABLE` in production mode | `e3_trace` is an existing field in separate `runtime_e1_v2`, not a production G4 cause. |
| Initial sufficiency route and guard | `DERIVABLE_DETERMINISTICALLY` when complete inputs exist | Reconstruct from plan, selected evidence, errors, stage reachability, and bound source code; otherwise `NOT_RELIABLY_OBSERVABLE`. No dedicated saved branch reason. |
| Exact finalization branch | `DERIVABLE_DETERMINISTICALLY` only in unambiguous states; otherwise `REQUIRES_SMALL_OBSERVABILITY_CHANGE` for exact saved-run proof | Current diagnostics omit `sufficient`, `coverage_blocked`, `salvageable`, and explicit branch reason. Do not treat errors as a branch receipt. |
| Corpus answerability / citation-safe factual sufficiency | `NOT_RELIABLY_OBSERVABLE` from telemetry | Independent locked-corpus/provenance review is mandatory. |

**No observability prerequisite is required before Lane A begins.** The next
task can adjudicate answerability and attribute cases with sufficient existing
authority, reporting unresolved fields honestly. If the only material blocker
for a candidate is exact finalization branch identity, first propose a narrow
diagnostic-only receipt carrying branch/reason and existing inputs
(`sufficient`, `coverage_blocked`, `salvageable`, version conflict, relevant
current booleans). It must not change the public DTO, product decisions, or
trace framework. Do not rerun the exposed cases or add the receipt merely to
make the audit look complete. Per-round G2 receipt expansion is conditional
on exact replay being impossible for a specific needed case.

## 6. Lane B — fresh development confirmation

The repository-visible `novel_dev` currently consists of the 28 already
exposed G3 cases. **No untouched fresh confirmation cohort exists.** Lane B
therefore requires additional reviewed `novel_dev` curation under the
[novel dataset contract](../docs/NOVEL_DATASET_CURATION_CONTRACT.md) before
any independent mechanism confirmation or post-repair comparison. It is a
separate, later authorization; do not borrow `novel_validation` or holdout.

Curate independent user information needs within the same locked
corpus/source universe, not near-paraphrases or entity swaps of the six G3
cases. Human review must establish question quality, independent Gold
evidence/answer points, exact locked version and provenance, novelty,
`curation_family_id` isolation (including across visible novel splits),
`representative` versus `exploratory` metadata, `review_status=approved`,
and `lifecycle=split_frozen`. Require truthful
`agent_outcome_seen_before_freeze=false` and
`evidence_selected_from_agent_output=false`. Exploratory cases can probe a
mechanism but do not substitute for representative evidence.

Freeze question, Gold, sidecar, and selected IDs **before** viewing production
outcomes, retrieval traces, or case-level model behavior and, where practical,
before implementing or evaluating the hypothesized repair. Selection must be
outcome-blind: no predicted failures, known hard-case targeting, historical
case analogues, or case-specific weakness screen. Use a normal Git commit
with dataset version/identity, locked source identity, selected IDs, and
review metadata; do not add per-file hash inventories unless an authorized
formal gate requires them. Amendments follow the dataset contract and cannot
retroactively turn outcome-informed cases into fresh confirmation.

No fixed case count is imposed. The smallest future cohort should be
predeclared around independent semantic families needed to replicate the
identified mechanism and around answerable/unanswerable paired safety
observations. A replication claim needs genuinely independent information
needs, normally spanning more than one `curation_family_id`; nominally
different IDs or trivial variants do not suffice. Report representative and
exploratory strata separately. If Lane A finds no reproducible generic
mechanism, do not spend fresh cases merely to search blindly. If Lane A finds
a plausible mechanism, curate/freeze Lane B before a mechanism-specific
repair where practical. If separate deterministic evidence already justifies
a repair, freeze Lane B before its post-repair empirical comparison.

## 7. Reporting and execution decision

For each lane, report answerability counts first:
`N_A=ANSWERABLE`, `N_U=UNANSWERABLE`, and `N_?=UNKNOWN` with reasons. Join
production status only afterward. For `N_A`, separately report
`answered_complete`, `answered_incomplete`, `insufficient_evidence`,
`false_insufficiency_candidate_count`,
`attributed_false_insufficiency_count`, and
`unattributed_answerable_insufficient_count`. A candidate is simply
`ANSWERABLE + insufficient_evidence`; attribution requires the full causal
gate above. If rates are warranted by outcome-blind Lane B selection, use
`N_A` as the denominator for candidate and attributed rates, never all
insufficient results. Among candidates also report
`causally_attributed_count` and `causally_unresolved_count`, including
observability reasons. A low attributed count with many unresolved cases is
not reassuring.

For `N_U`, report correct abstention (including correct version-conflict
status), false answers, unsupported claims, unsafe citations/provenance, and
missed version conflicts, with `N_U` as the denominator when rates are
meaningful. Report incomplete answered obligations and missing required
relations separately even when an answer is otherwise supported. Keep
`UNKNOWN` out of both denominators and show its count. Do not combine
over-conservative and under-conservative outcomes into one score.

Lane A's six are selected *because* their outcome is insufficient: report
case counts, answerability judgments, candidate/attributed/unresolved counts,
and mechanisms only. Do not calculate or present their candidate share as a
population rate. Matched answered controls are descriptive and cannot repair
that selection bias. Lane B, once separately authorized and outcome-blindly
frozen, can support directional development rates with explicit denominators,
unknowns, semantic-family independence, and limited scope; it still does not
automatically authorize T3/T4/T5 or a generalization/release claim.

The next task should: (1) freeze the rubric and selected exposed IDs; (2)
adjudicate answerability from Gold plus current locked corpus before joining
case outcomes; (3) qualify and reuse G3 artifacts; (4) classify outcome and
earliest cause; (5) check the opposing safety family; and (6) report
uncertainty and decide whether a generic mechanism warrants a later repair
**design** or Lane B curation. No new model run is presumed. If required
artifacts prove incompatible or absent, stop that subanalysis and recommend
the smallest recovery/observability step under separate authorization.

**Single next recommendation:** `G4 EXPOSED DEVELOPMENT ANSWERABILITY
ADJUDICATION / CAUSAL DIAGNOSTIC`. The current design authorizes neither
that execution nor fresh data curation, scientific calls, or a product fix.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`.
