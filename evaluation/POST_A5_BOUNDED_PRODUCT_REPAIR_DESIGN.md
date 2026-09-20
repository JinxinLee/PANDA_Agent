# Post-A5 bounded product repair design

Status: `COMPLETE / PASS / BOUNDED_PRODUCT_REPAIR_DESIGN_READY`.
PASS means static design gates G1-G10 only. All workstreams are DESIGN_ONLY /
NOT_IMPLEMENTED. Scientific effectiveness is NOT_EVALUATED.

Starting HEAD: `855e6f346bd23003f329b587b55fbc9b654cee84`; clean worktree.
Product-behavior HEAD: `e79d3232ed132a224cbceaf3524e19a1406bd648`.
Canonical prompt fingerprint remains
`0a5b2909ef586671d533148979fc681c64e37528ad53781a4566cb9044835ba2`.
New scientific/evaluation usage: **0 calls / 0 tokens**.
Companion: `evaluation/post_a5_bounded_product_repair_design.json`.

## Current observed architecture and approved design scope

Authority is the forward reconciliation MD/JSON at `855e6f3`, with the earlier
RCA MD/JSON and E2-A3-R2 preregistration as historical evidence. This task approves
a design decision only, not future implementation or scientific validation.

The sequence remains D0 question-only -> R1/R2 retrieval/fusion/rerank/selection
-> EA post-retrieval admission -> A0 -> V1 -> at most one A1 -> V2 -> C composer.
Workstream C1 below means coverage, not composer stage C. E is external evaluation;
O is cross-cutting persistence.

Inspected source anchors at starting HEAD:

- `qa.py:84`, `_answer`, `_revise`: generation/revision filter the selected bundle.
  `_verify` sees broader evidence and rejects incomplete public web citations.
- `_validate_answer_point_review` validates mappings/complete/supporters, not
  entailment. `_after_verify_route` currently sends errors to one revision.
  `_finalize` can salvage supported claims as ANSWERED despite coverage errors.
  C1 must explicitly change routing and this finalization behavior.
- `ingestion.py:parse_web` creates page and section as different objects; section
  has parent_object_id and heading ancestry. Page has empty section_path.
  `models.py:Evidence` omits parent/object_type/metadata, so selected payload alone
  cannot establish structural backing.
- `storage.py:object_persisted_metadata`, `restore_object_parent` preserve parent
  metadata. `load_structured_objects` reads ALL objects; it is not a bounded QA
  backing API. A small exact structural reader is needed for EA1.
- `evaluation.py:EvaluationRunStore.record` persists arbitrary diagnostics into
  attempts.jsonl, records/<id>.json and results.jsonl. Both runner/finalization
  result-content hash functions include diagnostics. `api.py:_ui_diagnostics`
  explicitly projects sanitized fields.
- `evaluation_runner.py:prompt_fingerprint` binds active prompts and D0 versions,
  not every QA JSON schema. C1 changes active review/revision prompts and therefore
  the fingerprint. Implementation commit also binds private schema changes.

Selected units: O1 owns capture only; EA1 owns exact backing and consistent lookup;
C1 owns satisfaction scope, validation, revisionability and limitation output.
RS status separation is deferred. Dependency graph and order:

```text
current runtime -> O1 -> EA1 -> C1 -> deterministic integration closeout
```

Use separate implementation commits and independent T0 gates. O1 observes without
prescribing semantics; EA1 does not depend on relationship records; C1 then reasons
against explicit corrected admission. No implementation is authorized now.

## O1: capture surfaces and persistence

Planned source: `src/panda_agent/qa.py` (QAState, `_run_detailed`, `_answer`,
`_verify`, `_revise`, `_compose_verified_answer`, `_finalize`), and
`src/panda_agent/evaluation_runner.py` only for explicit development capture
opt-in/transport. No new module. Existing evaluation store/finalization need no
schema or verdict change; change transport only if an actual defect is found.
Models, prompts, D0 and public DTO stay unchanged.

Use a private `_run_detailed` keyword `capture_stage_trace=False`; the development
adapter enables it only through an explicitly recorded run-manifest option and
passes the existing mode unchanged. Normal public run/run_detailed and protected
runs remain capture-disabled. Collector is per invocation, referenced privately
in QAState, never shared mutable agent state. Composer receives an optional private
capture callback. No user-visible API option is added.

Envelope: `diagnostics.qa_stage_trace` with `schema_version=qa-stage-trace-v1`,
`capture_status`, ordered `events`, and `evidence_registry`. Event fields are
stage, round, status (CAPTURED/NOT_EXECUTED/NOT_CAPTURED), reason_code, payload.
Enclosing existing record supplies run/case/attempt identity. Registry retains each
exact evidence projection once; references resolve actual text/locator and field
subsets, not only IDs. Copy claims/question/points immutably before mutation.

| Stage | Source and timing | Fields copied / mutation boundary |
| --- | --- | --- |
| EA_ADMISSION | `_answer` / `_revise`, after claim_evidence, before serialization | ordered selected/admitted/rejected IDs, actual evidence projection, predicate reason; identify use/round |
| A0_OUTPUT | `_answer`, immediately after generate_json | parsed ANSWER_SCHEMA fields and claim ordinals before model projection, augmentation, identifier stripping or normalization |
| V1_INPUT | `_verify`, immediately before generate_json | actual task, points, requirements, requirement evidence, claims/evidence; separate normalized draft deltas and deterministic exclusions |
| V1_OUTPUT | `_verify`, immediately on return | raw parsed support/mappings/coverage/supporters/missing IDs/reason before validation/fallback; append validation result separately |
| A1_INPUT | `_revise`, immediately before generate_json | actual missing IDs/text, revision scope, verified claims, unsupported draft, errors, admitted evidence |
| A1_OUTPUT | `_revise`, on return then after normalizers | raw claims plus ordinal-preserving transform map and normalized deltas before merge |
| A1_POST_MERGE | inside actual merge branches, then before return | each input ordinal, old/new ID, comparison target, disposition, final ordered merged claims |
| V2_INPUT | `_verify` at revision_count=1 | same exact input contract as V1, actual post-merge projection and exclusions |
| V2_OUTPUT | same seam as V1_OUTPUT | raw round-2 response before replacement, validation outcome |
| C_INPUT | `_compose_verified_answer`, before bypass/call | actual ordered verified claims; finalizer evidence-edge references outside model input |
| C_OUTPUT | composer response and each return; finalizer after answer chosen | parsed paragraphs/source_claim_ids, existing parsed composer-review verdict, validation/fallback reason, final answer reference |

All snapshots serialize only under the existing diagnostics path, not a parallel
log or RetrievalTrace. Existing composer count-only diagnostics remain unchanged;
new text snapshots are separate internal opt-in data, excluded from public API
projection. No provider envelopes, credentials, hidden reasoning or chain-of-thought.
Copy existing concise structured reasons; do not request extra explanations.

Merge precedence follows the current loop exactly: MISSING_ID;
IDENTICAL_UNSUPPORTED_REJECTED (same ID and normalized unsupported text);
NORMALIZED_DUPLICATE (against already retained/added text); ID_COLLISION_RENAMED
(actual chosen _rN ID, retained=true); otherwise RETAINED. Rejected new_id=null.
Comparison target includes stage/ordinal/ID. Supported-prefix skips are a separate
prefix audit. Any transform removal is OTHER_EXPLICIT_REASON with its actual branch
code, never inferred from final output. No changed normalization/ID policy.

Capture guards surround only copy/serialization, not semantic calls. On capture
failure mark NOT_CAPTURED with fixed reason, preserve answer/exception/retry path.
Preflight serialize the complete optional trace before diagnostics are returned;
if invalid, substitute a minimal serializable incomplete envelope. This prevents
optional data breaking `EvaluationRunStore.record`. Existing disk persistence
failure is NOT swallowed or reported as success. No model retry. Existing parser
errors retain their original behavior; record exception type when available, never
raw provider output. Whole-process failure may leave no durable trace; no second
store or crash-durability promise is added.

Limits: 16 events and 2,097,152 UTF-8 JSON bytes including registry. Normal stages
fit within 12 events (two EA, A0, four V, three A1, two C). Overflow drops the
overflowing snapshot, records incomplete plus missing stages; no truncated text
labeled complete. NOT_EXECUTED includes reason; historical absence is NOT_RETAINED.
Stable keys, causal array order. Limits change diagnostics only.

Neutrality requirements: prompts, full model inputs/schemas, call count/order,
retrieval, routing/retries, revision count, claims/composer semantics, public
status/answer/citations/DTO and fingerprint identical enabled/disabled. Diagnostic
bytes, memory and timing are not equality targets. O1 changes source/artifact
identity without material product behavior.

## EA1: exact backing algorithm and boundedness

Select EA-3 with strict EA-1 fallback; EA-4 adds diagnostic reasons only. EA-2 is
not selected because uncitable context with separate backing risks laundering.

Feasibility A: already-selected eligible section can be reused after provenance
checks, but is already offered and adds no new content. B: persisted direct-parent
metadata enables same-snapshot child lookup, but no bounded QA resolver currently
exists. C: making page itself citeable weakens the existing section contract and
is rejected. D: no valid backing is the expected safe outcome for many pages.
No live index/source corpus inspection or retrieval is performed in this task.

Algorithm:

1. Preserve direct eligible projection. Only attempt selected Sphinx objects
   resolving by exact object_id to original sphinx_page with missing section_path.
   Do not repair missing URL/date, uncertain chunks, other source types or versions.
2. One read-only snapshot transaction batches exact selected-page IDs and direct
   sphinx_section children via persisted metadata.parent_object_id. A localized
   storage.py reader reuses connection handling, `_OBJECT_READ_COLUMNS` and
   `restore_object_parent`; never load all objects or call semantic retrieval.
   Persisted page text/locator/source/version must equal the selected payload.
   Require allowed locked version, snapshot metadata and request-version consistency;
   unavailable lock authority fails closed.
   Authority is the existing `data/manifests/source_manifest.json` web_documents
   entry keyed by doc_id: version must equal doc_id + "@" + snapshot_hash,
   metadata snapshot_hash must match, and date must equal captured_at[:10].
   Match the exact records path/URL for the underlying page. Read this manifest
   once per invocation; no source fetch, new digest or new manifest is needed.
3. At most 4 candidate pages per execution; if more, resolve none, retaining all
   directly eligible evidence. Read at most 17 children/page to detect >16;
   overflow excludes that page, never first-N selection. Read length and at most
   12,000 characters of child text; longer children reject. No pagination/retry.
   At most one resolved backing/page and four additional objects total. Cache
   lookup/admission per invocation for A0/A1/V1/V2. Limits are resource policy,
   not tuned to sentinel outcomes.
   Use a 1,000 ms transaction-local statement timeout and at most two bounded
   statements (page batch, child batch with per-parent limits). Timeout is
   LOOKUP_FAILED and retains strict admission. No new index/migration is planned.
4. Require exact source_id/source_version_id/snapshot_hash/date, direct page parent,
   same document path and URL before fragment, and valid current citation locator.
   Entire nonempty section text must occur exactly once as a contiguous substring
   of the selected page's actual text, case-sensitive without normalization.
   Record [start,end) offsets. This establishes provenance/content containment,
   NOT claim entailment. Topic/title/ancestor similarity cannot substitute.
5. Resolve only when exactly one child qualifies. Multiple qualifying children,
   including nested/overlapping sections, mean AMBIGUOUS_BACKING and exclusion.
   No shortest/most-relevant/first-child preference. Reuse an already-selected
   unique eligible child at its existing position without duplicate content.
6. Otherwise create a normal Evidence-shaped projection of the REAL child:
   exact object/text/locator/version/authority, evidence_id generated by
   `stable_id(child_object_id, "ea_exact_backing", prefix="evidence")`,
   retrieval_channels=["ea_exact_backing"], score=0.0 as non-ranking provenance.
   Parent remains unchanged/ineligible. Insert only in QA admission projection at
   parent's excluded slot; preserve relative order of original eligible evidence.
   Never mutate bundle.evidence/ranks/trace/index or pretend the child was retrieved.
   Internal registry records parent/backing IDs, offsets and reason outside DTO.
7. A0/A1 and applicable legacy requirement mappings use the same projection.
   `_verify` uses selected plus resolved backing lookup with existing guards;
   `_finalize` resolves public citation IDs through this lookup so backing appears
   in QAResult.evidence. This is separate from experimental E3 retained evidence.
   Generation sees only the valid section, not the uncitable whole page. Claim
   cites actual backing and must pass semantic support verification. Never rewrite
   page citation IDs to children after generation.

Reasons: DIRECTLY_CITATION_ELIGIBLE, RESOLVED_EXACT_BACKING, NO_VALID_BACKING,
VERSION_MISMATCH, CONTENT_RELATION_NOT_ESTABLISHED, INVALID_LOCATOR,
AMBIGUOUS_BACKING, BOUND_EXCEEDED, LOOKUP_FAILED. Record bounded candidate reasons
and final page reason. No generic capability framework. Database/resolver failure
keeps strict admission, no looser citation/retry/retrieval.

Planned source: qa.py admission helper/private registry and answer/revise/verify/
finalize; storage.py bounded structural reader. Existing Evidence/SourceLocator
schema reused. No ingestion, index, retrieval.py ranking/search, prompt, D0,
public API or evaluator changes. Structural read adds I/O, not semantic retrieval.
No additional model stage or raised call ceiling; existing optional paths may
activate differently because evidence changes.

## E2-A3-R2 safety mapping

| Gate | Forward requirement |
| --- | --- |
| S1 | Predicate unchanged; real backing independently satisfies it and version guards. |
| S2 | Page remains excluded; only validated real backing enters A0. Explicit expansion beyond strict selected-only projection, not eligibility weakening. |
| S3 | A1/requirement maps use same cached projection as A0. |
| S4 | Direct invalid-page public edge still rejected; no ID substitution. |
| S5/S6 | Historical offending page IDs remain invalid page edges; historical outcomes untouched. |
| S7 | Historical counts remain historical, not quotas for future runtime. Original selected count unchanged, admitted count may change. |
| S8 | Already-valid selected Sphinx identity/payload/relative order preserved. |
| S9 | Non-Sphinx identity/payload/order unchanged. |
| S10 | Retrieval bundle/ranking/trace/implementation/index/corpus unchanged. New bounded provenance read explicitly changes the old no-backfill implementation restriction, projecting only text already selected with real backing. No reindex/ingestion authorization. |
| S11 | Identifier/colon normalization unchanged. |
| S12 | EA1 preserves prompts/schemas/E1-E2 judgment semantics/compatibility/public DTO. Evidence domain changes explicitly. C1 separately changes review/revision semantics and cannot claim S12 unchanged. |
| S13 | Historical legacy default was already superseded; keep current production_answer_obligations_v1, do not restore legacy. |

Historical AST equality constrained that historical repair. Preserve its safety
substance and results, not claim its entire suite certifies this new resolver.
No guessed heading, arbitrary child, cross-version or topically similar citation.

## C1: schema, bounds and necessity

Keep relationship_checks within existing per-point coverage; no second reviewer.
Keep existing top-level review fields. Exact private schema, all keys required,
additional keys forbidden:

```text
point = {answer_point_id, supporting_claim_ids, complete,
         scope_status, relationship_checks}
scope_status = ESTABLISHED | INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE | OVERFLOW
relationship = {relationship_text, necessity_reason, basis,
                supporting_claim_ids, satisfied, admission_state}
basis item = {evidence_id, quote}
admission_state = ADMITTED_BACKING_AVAILABLE |
                  VISIBLE_ONLY_WITHOUT_CITABLE_BACKING |
                  INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE
```

IDs are known strings, booleans strict, lists unique as specified. No separate
relationship_id: point ID plus ordinal identifies a local check. No duplicated
basis ID/span arrays. Point supporters equal ordered unique union of relation
supporters in reviewable-claim order. Factual/definition/location obligations use
a direct requested assertion as a check; not every check needs two entities.
Established/visible-only relationships require 1-2 basis items; uncertain checks
allow 0-2 and cannot assert satisfaction. Evidence IDs are unique within basis.
Supporter lists may be empty only for unsatisfied checks. Point supporter lists
may be empty when incomplete. All strings/arrays have the types and bounds below.

Fixed numerical bounds:

| Item | Maximum |
| --- | --- |
| Checks per point | 4 |
| Checks total | 20 (current 1-5 points) |
| Distinct basis evidence references/check | 2; one quote/reference |
| Supporting claim IDs/check | 8 |
| Supporting claim IDs/point | 32 |
| relationship_text | 240 characters, nonempty |
| necessity_reason | 160 characters, nonempty |
| exact quote | 400 characters, nonempty |

Maximum 40 quotes, 8,000 relation/necessity characters and 16,000 quote characters,
plus IDs/existing fields. These are conservative output complexity ceilings, not
measured token cost or sentinel-fit bounds. Extra tokens are expected; no extra
model call. ESTABLISHED requires 1-4 checks. If more necessary checks/references/
supporters are needed, return scope_status=OVERFLOW, bounded records, complete=false.
OVERFLOW is non-revisionable. Literal over-bound/overlength output is structurally
invalid; never truncate and accept. Total overflow conservatively invalidates
affected scope, or all points if affected points cannot be identified.

INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE permits zero checks or bounded uncertain checks;
uncertain checks have satisfied=false and no supporters. Optional ambiguous facts
are omitted, not used to block an otherwise answerable point.

Necessity requires BOTH material relevance to the user/runtime point AND support
from in-scope evidence. A documented necessary workflow handoff may qualify without
D0 inventing steps. Claims cannot be the sole source of scope. Do not require every
available fact, infer unsupported domain facts, or use Gold/case IDs/expected
answers/judge output. necessity_reason is a brief auditable link to the request,
not hidden reasoning. Quotes cannot mechanically prove necessity or entailment.

V1/V2 explicitly add untrusted_question and admitted evidence IDs to existing
points/claims/evidence inputs. Raw question helps ground necessity beyond compressed
points. This is a semantic input/prompt/schema change, never O1 logging. D0 remains
question-only and unchanged. Visible evidence includes selected pages and backing;
public support uses valid backing only.

## C1: state behavior, validation and recovery

- ADMITTED_BACKING_AVAILABLE: all indispensable basis references are admitted.
  satisfied=true requires relevant supported claims stating the relation and citing
  that basis. Missing relation means incomplete and potentially revisionable.
- VISIBLE_ONLY_WITHOUT_CITABLE_BACKING: necessary relation has visible exact basis
  but at least one indispensable reference is not admitted. satisfied=false,
  no supporters; incomplete EA gap, never a repair obligation instructing invention.
- INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE: necessity/support cannot be established.
  satisfied=false, no supporters; uncertain incomplete scope, non-revisionable.
  Use an empty checks list when no necessary relation can be established rather
  than inventing relationship_text. Never infer corpus-wide absence.

complete=true iff ESTABLISHED, nonempty checks all satisfied with admitted backing,
existing supported relevant mapping checks pass, and no unresolved required scope.
missing_answer_point_ids exactly equals incomplete points.

Derive internal revisionable_relationships only from validated necessary unsatisfied
ADMITTED_BACKING_AVAILABLE checks. A1 receives only those relations, corresponding
points and backing; exclude blocked needs from missing-point instructions AND
verification-error instructions. Mixed point recovers only admitted-backed gaps;
blocked portions remain incomplete. Coverage revision prompt must treat listed
relations as bounded scope, not implicitly demand every part of a broad point.
Existing unsupported-claim repair may run only with admitted cited backing and
existing safety checks. If neither eligible relation nor eligible unsupported-claim
repair exists, finalize. Invalid structural review is non-revisionable. At most one
A1; V2 cannot trigger more recovery. No E3 or extra retrieval. Existing pre-answer
retrieval behavior remains unchanged.

After available recovery, incomplete/uncertain/overflow/invalid coverage returns
existing QAStatus.INSUFFICIENT_EVIDENCE. Retain independently verified relevant
claims/citations, render deterministically, append fixed operational limitation:
"The available citable evidence does not establish a complete answer to this request."
This is a system limitation, not a new factual citation edge. Skip composer on this
path; do not allow current salvageable shortcut to label it ANSWERED. Existing
version-conflict/negative-existence guards retain precedence unchanged. Complete
answers retain existing composer behavior. No new public status or DTO field.
This output policy is a material C1 change.

Validator enforces exact keys/types/enums; known unique points/claims/evidence;
one point record; duplicate relationship text rejection within point (whitespace
normalization only for this duplicate check); exact quote substrings in actual
review evidence; bounds; declared admission state consistent with admitted IDs;
satisfied implies nonempty supporters with valid citations and point mapping;
basis IDs must be cited by those supporters; no unsupported/irrelevant supporter;
uncertain/visible-only cannot be satisfied; point supporter union; complete/missing
equivalence; scope-status consistency. Extend validator input with evidence and
admission lookup. This cannot prove model semantic necessity/entailment.

Planned source: qa.py review schema/validator/_verify/_after_verify_route/_revise/
_finalize; prompts.py coverage-review/revision prompt and prompt-set version;
evaluation_runner.py canonical fingerprint registration if new prompt variants
are introduced. Scope new semantics to production mode; preserve legacy/shadow
schemas/prompts through explicit local selection, not all _coverage_shadow paths.
All active variants must remain fingerprint-bound. No D0/DTO/evaluator changes.
Record private schema version coverage-satisfaction-v1 in diagnostics and source
identity; existing fingerprint does not automatically cover all JSON schemas.

## Future deterministic T0 acceptance units

No tests are added/run now. Use generic synthetic text and scripted clients only.

O1 homes: test_qa.py, test_e2_a1_answer_point_coverage.py, test_evaluation.py,
test_f6_release_identity.py. RED is absent/overwritten stage evidence; GREEN is
exact pre-mutation records. Pair capture off/on with identical responses and assert
public status/answer/claims/evidence/citations, routing, revision count, complete
model input/system/schema payloads and call order/count, prompt fingerprint equal.
Neutrality checks pass even before O1; new capture assertions supply RED. Cover
no/one revision, collision rename, anti-resurrection, duplicate, missing ID,
structural rejection retaining raw review, composer success/fallback/bypass, skipped
stages, serialization/copy/byte/event overflow, parser exception, concurrent isolation,
public projection excludes trace, and attempt/current/aggregate persistence equality.

EA1 homes: test_e2_a3_r2_citation_eligibility.py, test_d1_parent_persistence.py,
test_qa.py. RED: strict old projection cannot offer uniquely backed unselected
section. GREEN: real backing reaches A0/A1/verifier/public evidence without page
edge or bundle mutation. Fixtures: eligible section unchanged; unique same-version
child; selected backing deduplication; none/two children; wrong version/snapshot/
document/parent; topic-similar noncontained text; ambiguous repeated occurrence;
invalid locator; unavailable lock authority; page/child/text limits; DB failure;
non-Sphinx unchanged. Assert selected order/rank/bundle/trace unchanged, zero extra
retrieval/embedding/rerank calls, bounded lookup, cached A1 contract, direct invalid
page citation rejected. Script semantic rejection of a non-entailing claim even
when structural backing passes; containment never substitutes for entailment.

C1 homes: test_e2_a1_answer_point_coverage.py,
test_generic_answer_obligation_completeness.py, test_f6_release_identity.py.
RED: old schema/routing cannot represent new relation/admission decisions; GREEN:
valid records accepted and inconsistent records fail closed. Generic workflow
evidence "A occurs before B": A-only or topical A/B claims cannot be complete when
scripted reviewer marks relation absent; supported ordering may be complete.
Fake model tests enforce decisions, not prove live omission recognition. Cover
purpose/causal positive broad point, simple location/definition, optional fact not
required, ambiguous evidence without invented necessity, visible-only gap with no
recovery instruction, mixed admitted/blocked gap, V2 still missing/no third review,
5 checks/point, 21 total, third basis, overlong quote, unknown/duplicate/missing IDs,
invalid quote, unsupported supporter, state mismatch, empty complete scope,
complete/missing conflict and structural failure. Assert one/zero revision, filtered
recovery inputs, scoped limitation with verified claims, unchanged negative safety,
no E3/retrieval, changed fingerprint and unchanged question-only D0.

Integration: selected page -> unique backing -> omitted generic relation -> one
revision -> V2 -> composer. Trace tells exact story; all public edges resolve real
valid backing; call ceiling unchanged, no semantic retrieval delta. Separate commits
with focused T0 acceptance, then integration. A failed required unit blocks the
next unit. No automatic full pytest, frozen replay or scientific PASS claim.

## Materiality, prompt and release identity; RS

| Unit | Source / material behavior | Prompt fingerprint | Candidate/release identity | Hashes / public schema |
| --- | --- | --- | --- | --- |
| This design | docs only / false | unchanged | no freeze/release; product lineage unchanged | frozen artifacts untouched |
| O1 | true / false if neutrality passes | unchanged | source commit and future manifest/build identity differ; cannot reuse frozen candidate just because behavior is neutral | trace-enabled result/receipt hashes differ; public DTO unchanged |
| EA1 | true / true | unchanged planned | new material implementation identity for any authorized future comparison/release | answers/evidence/hashes may differ; Evidence/QAResult schema unchanged |
| C1 | true / true | changed active review/revision prompts; bind variants | new material source/private schema contract and future candidate/release identity | answers/status/hashes differ; private review schema changes, public DTO unchanged |

Ordinary deterministic development needs normal commits, not forced freezes/hashes.
Formal release remains independently gated. Never regenerate historical receipts.
"Trace/result hash only" means no prompt/public behavior change, not unchanged
source/build identity. O1 implementation scientific calls=0; EA1/C1 T0 calls=0 too.

RS=DEFER from these units. Existing raw runner decision plus explicitly named
preregistered development verdict can report future validation unambiguously.
No candidate-gate weakening or official-flag reinterpretation is needed. Future RS
infrastructure may separate execution validity/scientific verdict/formal validity;
not a prerequisite or authorized work here. Historical raw INCONCLUSIVE and
scientific T1 FAIL remain intact.

## Integration constraints, risks and future scientific validation

Forbidden product mechanisms: case IDs, benchmark lookup, PndMasterRecoTask/master-run
special logic, Gold-derived relationships, sentinel-forcing prompt examples,
extra retrieval/model stages, rerank or revision-bound changes, E3 promotion,
incomplete-page citations, guessed headings, arbitrary/topic/ancestor substitutions,
cross-version backing, or selected absence turned into corpus-wide absence.
No changes to Gold/calibration/evaluator/thresholds/index/corpus/D0.

Risks: unique-child containment may resolve few pages; nested sections deliberately
fail closed. Storage/lock metadata availability and bounded-query performance are
unmeasured. Literal text differences reject potentially safe but unproven backing.
Quotes/structural validation cannot prove semantic necessity or entailment.
Coverage bounds and conservative output may increase scoped limitations and tokens.
O1 cannot guarantee crash durability or reveal provider parse content. These are
effectiveness risks, not permission to weaken safety. If implementation needs
unbounded lookup, extra retrieval, a framework or public schema change, return to
bounded design. Historical g013 A1 defect and g023 reviewer-only cause remain
NOT_ESTABLISHED; no unique cause is claimed.

T0 proves deterministic plumbing/enforcement only. Future exposed scientific work
requires separate explicit authorization, NEW preregistration, fixed cohort and
criteria before outputs, fixed implementation/prompt/evidence identity appropriate
to that protocol, call/token budgets, controls and trace-completeness checks.
Measure admission success/safety, missing-relation recognition, unsupported claims,
completeness and abstention separately; use generic unseen exposed variants where
authorized. No cohort preregistered now; no automatic g013/g023 replay, freeze,
T1/T2/T3/T5 or Attempt 6. Incremental model stages/retrieval calls target zero;
material changes can alter existing conditional call paths and tokens, so future
actual usage must be measured rather than claimed identical.

## Design acceptance and preserved lifecycle

G1 separate units; G2 safety/S-gate mapping; G3 bounded exact fail-closed backing;
G4 question/evidence-only necessity; G5 fixed bounds/overflow; G6 admitted-backed
recovery and one revision; G7 neutral O1; G8 generic RED/GREEN T0 plans; G9 explicit
materiality/identity; G10 separate scientific preregistration/authorization.
All PASS for static design only; nothing implemented or scientifically validated.

OVERALL_T1_VERDICT=FAIL; g013/g023 FAIL, g047 PASS, g011 negative-existence safety
PASS and native-documentation role coverage FAIL; g010/g014/g022/g050 CONTROL_PASS.
Historical usage: 65 calls / 373,265 tokens. Product lineage unchanged.
Current MATERIAL_PRODUCT_CHANGE/EVALUATOR_CONTRACT_CHANGE/GOLD_CHANGE/
CALIBRATION_CHANGE=false. novel_validation=PRISTINE_FOR_CURRENT_LINEAGE;
holdout access=0, protected-content leakage=0, F6-B execution=0.
Candidate frozen=false, Attempt 6 preregistered=false/executed=false;
ATTEMPT_6_READINESS=NOT_READY.

Next recommendation: **POST-A5 O1 BEHAVIOR-NEUTRAL OBSERVABILITY IMPLEMENTATION**.
Separate authorization required; O1 authorization would not automatically cover
EA1/C1 or scientific validation. No push/amend.

## Static verification

JSON parsing, exact four-file authorized scope, unchanged source/tests/benchmarks/
evaluator/Gold/calibration, unchanged prior reconciliation and frozen T1, preserved
lineage/protected/Attempt-6 state, status/roadmap consistency, and git diff --check.
No pytest, scientific execution, hashes or integrity manifests generated.

NEXT_TASK_EXECUTION_AUTHORIZED = false
STOP.
