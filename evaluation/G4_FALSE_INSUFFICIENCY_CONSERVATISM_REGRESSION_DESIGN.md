# G4 — False-Insufficiency / Conservatism Regression Design

## Decision and boundary

G4 measures whether the current production answer-obligation path refuses a
**safely answerable** request, while independently guarding against unsafe or
incomplete answers. This document specifies future controls and adjudication;
it makes no product, evaluation, admission, verifier, or public-answer change.
G1's one completeness path per canonical answer point, G2's local containment,
and G3's scoped `NO_CHANGE` admission decision remain in force. An observed
`insufficient_evidence` status is a symptom, not an attribution.

The scope is English product questions under the locked corpus and current
`production_answer_obligations_v1` contract. The existing `runtime_e1_v2` E3
experiment is a separate mode; E3 controls below test its bounded recovery
contract, not an assertion that E3 runs in normal production mode. Historical
G3 aggregate evidence motivates the measurement, but its six unresolved
insufficient answers do not establish verifier conservatism. The 19
`AMBIGUOUS_BACKING` decisions are not permission to relax admission.

## Current production insufficiency path

`src/panda_agent/qa.py` runs `retrieve → sufficiency`; insufficient initial
evidence may enter one bounded pre-answer targeted retrieval, except on version
conflict, then returns to sufficiency. `_sufficiency` checks version conflicts,
answerability guards (including unsupported requested-symbol, future-runtime,
and universal-proof requests), evidence presence, an exact-requirement guard,
and required source types. It is a routing check, **not** proof that all answer
obligations are supported. Failure after the allowed route reaches `_finalize`
without generation or verification. Version conflicts produce the distinct
`version_conflict` status, not a G4 false-insufficiency count.

With sufficient initial evidence, A0 generates claims from admitted evidence.
V1 checks claim support, mappings, and the G1/G2 coverage contract. G2 yields a
production coverage receipt with `VALID`, `PARTIAL`, or `REJECTED` whole-review
status and `VALID`, `LOCAL_INVALID`, `MISSING`, or `CONFLICTED` local states.
Valid local children may survive a `PARTIAL` review, but the review is not
globally valid. A bounded A1 route uses eligible required-relation or
unsupported-claim targets and V2 rechecks the full canonical inventory.
Legacy `runtime_e1_v2` can instead trigger bounded E3 missing-point retrieval
when its evaluability/eligibility conditions hold, then revise and reverify.
Neither path makes a missing obligation complete by itself.

Production `_verify` sets host-derived `missing_answer_point_ids`, supported
and unsupported claims, coverage status, and `coverage_blocked` when points are
missing or the coverage review is not wholly evaluable. `_finalize` then has
two materially different insufficient paths:

1. `sufficient` is false, or errors exist without supported-claim salvage and
   without the coverage-incomplete path. It emits `insufficient_evidence`
   (or `version_conflict` for a conflicting plan), potentially with a narrowly
   cited refusal-basis claim but no authorized whole-answer completion.
2. In coverage-satisfaction mode, `sufficient` is true, no version conflict
   exists, and `coverage_blocked` is true. This `c1_incomplete` path emits
   `insufficient_evidence`, can retain independently supported claims, and
   appends an incomplete-answer notice. It never labels partial support as a
   complete `answered` result.

Otherwise `_finalize` renders only verified supported claims, via the bounded
composer or deterministic renderer, and emits `answered`. Thus errors alone
do not prove verifier ownership, and supported-claim salvage does not prove
whole-answer completeness. The audit must identify the *earliest causally
wrong transition*, including sufficiency, decomposition, retrieval, admission,
generation, review, A1, and finalization, before assigning blame. An explicit
refusal guard must be judged against its authoritative premise; a correct
guard is a correct abstention.

## Adjudication: false insufficiency versus correct abstention

For an individual requested obligation, a **false-insufficiency candidate**
requires all of the following independently established facts:

1. The question is within product scope, and its requested points and required
   relations are valid under the question-only G1 contract. An incorrect D1
   representation must first be identified and corrected in the adjudication;
   production's mistaken decomposition cannot serve as answerability authority.
2. Under the locked corpus/version contract, independently inspected evidence
   establishes every mandatory fact and relation with exact, safe provenance
   that could pass current citation/admission rules. Evidence merely existing
   somewhere is insufficient until relevance, version, locator, and support
   are proved. If evidence is only visible but not safely citable, this
   condition is not established.
3. A complete response can be constructed from that evidence without relaxing
   support, citation, G1 completeness, G2 validity, or refusal safeguards.
4. The actual production result is `insufficient_evidence` (including an
   incomplete notice with retained claims), and a reproducible, specific
   pipeline transition explains the divergence. A counterfactual within the
   existing contract must show what the owning transition should have done.

Before item 4 is established, label the case `ANSWERABLE / UNATTRIBUTED`, not
an established G4 mechanism. When evidence or obligation authority is
uncertain, label `UNKNOWN / UNRESOLVED`; do not fill gaps with model output,
Gold status, selected-evidence relevance, or user preference. Case answerability
is an independent property; pipeline success is an outcome.

**Correct insufficiency** includes genuinely absent locked-corpus evidence;
an unsupported required relation or point; only ambiguous/unsafe provenance;
no citation-safe backing; an unsupported future runtime result, open-domain
universal proof, or out-of-scope request; and a valid verifier rejection of
an unsupported claim. A version conflict is a correct distinct refusal/status.
Malformed reviews can correctly block authorization but are structural
containment, not proof of semantic false rejection. An answerable question
with a malformed review may be an operational failure candidate only after
the independent answerability proof and causal attribution; the malformed
child itself is never promoted to a valid disposition.

## Causal ownership and dual-sided safety

Use one primary evaluation-policy ownership code and optional audit-local
annotations. `Q1` covers question understanding; `Q2` entity resolution;
`R1` candidate recall; `R2` fusion/ranking; `R3` final selection; `D1`
question-only decomposition; `A1` initial answer generation or bounded
revision; and `V1` a *valid* verifier disposition that falsely rejects
independently supported, admitted evidence. `C1` means genuine corpus
insufficiency and is not a false-insufficiency defect. For the opposing unsafe
answer family, retain policy `V2` where verification falsely accepts a claim.
Do not call an R1/R2/R3 or admission break `V1` because it surfaced at V1.

Secondary audit-local annotations are `FINALIZATION_CONSERVATISM` (all current
contract conditions are proved satisfied but `_finalize` refuses),
`MALFORMED_REVIEW_CONTAINMENT`, `OBSERVABILITY_LIMITATION`, `UNRESOLVED`, and
`NOT_APPLICABLE`. They do not add stable policy codes or replace the primary
owner. For G3 admission distinctions, record
`ADMITTED_BACKING_AVAILABLE`, `VISIBLE_ONLY_WITHOUT_CITABLE_BACKING`, or
`INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE` separately. A valid visible-only outcome
is a provenance/admission question first and cannot establish V1 conservatism.
G3 `NO_CHANGE` can be reopened only by new, independently verified generic
admission-defect evidence under a separately authorized scope.

Track two opposing error families separately:

- **Over-conservative:** a reviewed answerable case ends in false
  `insufficient_evidence`.
- **Under-conservative:** the system answers an unanswerable case, or answers
  while omitting a required point/relation, accepting unsupported claims,
  unsafe citations, or a version conflict.

G1/G2 seek to prevent missed obligations; G4 must not trade these for refusals.
A lower insufficient count is not success without stable correct abstention,
support, provenance, and completeness. Conversely, a lower incomplete-answer
count is not success if false insufficiency rises.

## Answerability authority

Authority is conditional on compatibility with the exact question, corpus,
version, and current product contract:

| Rank | Source | Permitted conclusion |
|---|---|---|
| A | Deterministic synthetic control with constructed authoritative, citation-safe evidence and canonical obligations | Definitive expected answerability for T0 controls, subject to the real validator contract. |
| B | Independently reviewed `novel_dev` Gold evidence and answer points | Development answerability adjudication after checking current corpus/version and provenance; never a product instruction. |
| C | Independently inspected locked-corpus evidence with verified provenance | Can establish a case's factual/citation-safe sufficiency even when retrieval missed it. |
| D | Production selected/admitted evidence and `VALID` verifier dispositions | Strong pipeline observations; can support a narrower transition diagnosis but cannot alone prove corpus-wide insufficiency or correctness of the model's judgment. |
| E | Generated answer text alone | No answerability authority. |

The review records evidence references, canonical obligations, admission/citation
proof, source version, counterfactual transition, reviewer decision, and any
uncertainty. Gold `answered` status and a prior successful model answer are
insufficient by themselves. Do not use exposed Gold wording as code fixtures.

## Future T0 control matrix

Build generic fake-provider fixtures with constructed source evidence, plan,
canonical point inventory, admitted IDs, A0/A1/V1/V2 outputs, and expected
final status. Each row asserts its owning stage and public claim safety.

| Class | Constructed condition | Expected owner/outcome |
|---|---|---|
| Answerable | One point; admitted support and `VALID` complete ordinary check | V1/coverage/finalize: `answered`. |
| Answerable | Multiple points, each independently supported | G1/G2/finalize: complete `answered`. |
| Answerable | Named relation with exact admitted-backed required-relation disposition | G1 relation path: `answered`. |
| Answerable | Relation-free point with valid ordinary check | G1 ordinary path: `answered`. |
| Answerable | V1 incomplete, eligible A1 supplies precisely the missing relation/claim, V2 validates full inventory | A1/V2: `answered`. |
| Answerable | `PARTIAL` G2 review contains one valid local sibling and one malformed unrelated sibling; an independent valid target authorizes A1, and V2 then validates the full inventory | G2/A1/V2: answer only after full valid recheck; the malformed sibling alone never authorizes A1. |
| Answerable, experimental mode | E3 finds genuinely missing evidence and post-retrieval revision verifies all points | `runtime_e1_v2` E3/V2: `answered`; not normal production E3. |
| Unanswerable | Required locked-corpus evidence absent | C1/sufficiency or coverage: `insufficient_evidence`. |
| Unanswerable | Admitted evidence does not establish requested relation | G1/V1/finalize: `insufficient_evidence`. |
| Unanswerable | Only ambiguous or unsafe provenance | Admission/G1: `insufficient_evidence`. |
| Unanswerable | Conflicting requested version | Plan/finalize: `version_conflict`. |
| Unanswerable | Exact future runtime result unavailable | Answerability guard: `insufficient_evidence`. |
| Unanswerable | Open-domain universal proof unsupported | Answerability guard: `insufficient_evidence`. |
| Unanswerable | Mandatory point remains missing after allowed recovery | Coverage/finalize: `insufficient_evidence`. |
| Unanswerable | Valid V1/V2 correctly rejects an unsupported claim | V1/V2/finalize: no unsupported answer. |
| Unanswerable at current checkpoint | Structurally malformed review cannot authorize complete coverage | G2/finalize: `insufficient_evidence`; no false-`V1` label. |

Pair controls by changing exactly one authoritative fact while holding question
shape, point inventory, generation shape, and unrelated evidence constant:
relation established versus merely similar; safe admitted backing versus
unsafe locator; all relations satisfied versus one absent; `VALID` disposition
versus malformed sibling; A1 repair complete versus one point still missing;
and exact same-version evidence versus a conflicting version. Assert both
public statuses and claim/citation/coverage invariants. These pairs detect an
indiscriminate “answer more often” change.

## Finalization audit and observability

The T0 harness should invoke the real `_verify`/routing/`_finalize` seams with
fake providers and frozen synthetic states. Independently calculate the current
contract from the canonical point inventory and validated G2 receipt, not from
the model's aggregate `supported` flag. Construct one state with `sufficient`,
no version conflict, valid admitted-backed support, every point/relation
complete, no unresolved unsupported claim, and `coverage_blocked=false`.
If `_finalize` still emits `insufficient_evidence`, the test must expose the
exact branch and prove `FINALIZATION_CONSERVATISM`; if no such reachable state
exists, record that result rather than manufacturing a bug. Its paired state
leaves one mandatory relation/point unsatisfied and must not emit a complete
answer. Do not bypass `_finalize`.

Current artifacts support a T0 harness without a prerequisite product change.
For real-case causal attribution, qualify every same-run artifact and trace
before using it; stage capture is best-effort and is not semantic authority.

| Needed field | Classification | Current source / limit |
|---|---|---|
| Final status and public claims | `EXISTING_AUTHORITATIVE_FIELD` | `result.status`, `result.claims`, `verification_errors`; status alone does not name the branch. |
| Canonical points, final missing IDs, G2 validity and local errors | `EXISTING_AUTHORITATIVE_FIELD` | `diagnostics.answer_point_audit`, including `coverage_validation`; `PARTIAL` has no authoritative whole-review semantic coverage. |
| Selected evidence and admission | `EXISTING_AUTHORITATIVE_FIELD` when complete | `selected_evidence` plus reconciled `EA_ADMISSION` decisions/admitted IDs; missing/inconsistent trace is unknown, not rejection. |
| Valid V1/V2 dispositions blocking completion | `DERIVABLE_DETERMINISTICALLY` when complete | Final `VALID` coverage is in the audit; per-round or `PARTIAL` children require exact-lineage replay from complete V input/output and evidence, as in G3. Otherwise `NOT_RELIABLY_OBSERVABLE`. |
| A1 executed, targets, and outcome | `EXISTING_AUTHORITATIVE_FIELD` when complete | `revision_count` and `A1_INPUT`/`A1_OUTPUT`/post-merge, joined to V2; no event is meaningful only with complete capture. |
| E3 executed and recovered | `EXISTING_AUTHORITATIVE_FIELD` in `runtime_e1_v2` | `e3_trace` and counts; `NOT_APPLICABLE` in production mode. |
| Initial sufficiency guard/route and exact finalization branch | `DERIVABLE_DETERMINISTICALLY` for controlled T0 state; `REQUIRES_SMALL_OBSERVABILITY_CHANGE` for reliable saved-run branch attribution | Current normal diagnostics do not persist `sufficient`, `coverage_blocked`, `salvageable`, or a final branch reason; verification errors are not a branch receipt. |
| Corpus-wide answerability and factual support | `NOT_RELIABLY_OBSERVABLE` from telemetry | Independent reviewed evidence/provenance adjudication required. |

No observability prerequisite is required **before the next deterministic
control implementation**. If a later G4 empirical run needs authoritative
per-case branch rates that cannot be reconstructed from complete same-run
artifacts, first add the smallest diagnostic-only finalization decision receipt
(branch/reason and the existing boolean inputs), with no public DTO or product
behavior change. A per-round G2 receipt should be considered only if exact
replay is unavailable and the specific attribution question needs it.

## Metrics, denominators, and gates

Partition independently reviewed cases into `ANSWERABLE`, `UNANSWERABLE`, and
`UNKNOWN / UNRESOLVED` before interpreting production outcomes. For the
answerable denominator `N_A`, report `false_insufficiency_count` (only cases
meeting the full causal definition) and
`false_insufficiency_rate = count / N_A`. Report answerable-but-insufficient
cases with unresolved ownership separately so this numerator cannot conceal
an attribution gap. Also report `answered_complete`,
`answered_incomplete`, missing-point incidence, and missing-relation incidence.
For the unanswerable denominator `N_U`, report `correct_insufficiency_count`
and rate (`count / N_U`), `false_answer_count` and rate, unsupported-claim
incidence, and unsafe citation/provenance incidence. Also report
`correct_abstention_count / N_U`, including valid `version_conflict` refusals;
keep that status-specific count separate from `correct_insufficiency_count`.
Report `UNKNOWN / UNRESOLVED` count and reasons next
to both denominators. Never divide by all insufficient outcomes or infer a
denominator from production output. If `N_A` or `N_U` is zero, its rate is
`N/A`, not zero.

Also report both error families by primary owner, A1 and experimental E3
eligibility/attempt/recovery denominators, valid versus malformed review
counts, and coverage of causal attribution. A1/E3 success uses eligible
attempts as its denominator, not all cases. Any aggregate score must appear
beside the directional rates and safety counts. Do not assign an arbitrary
numeric pass threshold from exposed cases.

For a future proposed behavior change, require generic T0 targeted
RED→GREEN evidence, paired unanswerable controls without regression, no new
missed point/relation, unsupported claim, provenance or version regression,
and focused neighboring tests. Later independent development evidence must
support the same mechanism. A measured false insufficiency does not itself
justify a product change: require a repeatable generic mechanism, a clear
owning layer, a minimal repair, and paired controls that can detect
overcorrection. Q1/Q2, retrieval/recovery, decomposition, A0/A1, valid review,
and finalization are possible owners; no repair owner is selected here.

## Evidence sequence and protected boundary

After separate authorization, build T0 synthetic/fake-provider controls first,
then focused generic regressions. Small exposed development diagnostics can
probe a predeclared mechanism; the existing 28-ID G3 `novel_dev` cohort and its
six unresolved cases are secondary exposed diagnostics only. They cannot set
the fix, acceptance thresholds, or independent generalization claim.
Historical `g047` is at most a **NON_GATING EXPOSED REGRESSION SENTINEL**.
Fresh independently reviewed `novel_dev`, selected or held aside before a
future repair and checked against the locked corpus, is stronger post-change
development confirmation. This design does not access new case content.

No full Gold, T3, T4, `novel_validation`, holdout, T5, or release run follows
automatically. `novel_validation` remains reserved for separately authorized
phase-level comparison; holdout remains under the separate release boundary.
Public partial-answer presentation is **OUT OF SCOPE**: the current
whole-answer status may retain cited safe claims with an incomplete notice,
but changing public answer semantics to “partial answer plus missing portion”
needs its own design and authorization. G4 cannot use that as a shortcut to
label an incomplete response complete.

## Next task and lifecycle

**G4 design complete; implementation not authorized; empirical regression not
established.** Current diagnostic seams are sufficient to start controlled
T0 work, so the smallest recommended next task is **G4 DETERMINISTIC
FALSE-INSUFFICIENCY REGRESSION HARNESS / CONTROL IMPLEMENTATION**: implement
generic synthetic/fake-provider RED→GREEN controls before any behavior repair
or scientific evaluation. Its execution requires separate authorization.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`.
