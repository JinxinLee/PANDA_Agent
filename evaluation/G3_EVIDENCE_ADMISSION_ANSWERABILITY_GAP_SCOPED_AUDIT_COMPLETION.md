# G3 Evidence Admission / Answerability Gap Scoped Audit — Completion

## Decision and scope

**NO_CHANGE** for the frozen-cohort admission-policy decision. All 28 frozen
`novel_dev` IDs now have same-run QA results and complete stage-trace capture.
The exact production G2 validator consistently replayed all three final
`PARTIAL` V1 reviews. Their surviving `VALID` children are included; their
`LOCAL_INVALID` siblings are not treated as semantic authority. No valid
visible-only disposition links a selected rejected item to an
answer-authorization failure. There are no Tier 1 links or Tier 2
admission-policy candidates. The 19 ambiguous-backing rejections remain real
Tier 0 observations, not a policy defect by themselves.

This is a bounded audit decision. It does not prove the absence of latent
corpus gaps, settle the six unrelated or ambiguously owned insufficient
answers, establish a generalization score, or authorize a product change.
The generic QA run store's quality-gate `FAIL` is a separate verdict and is
not the G3 causal-audit decision.

The frozen cohort file is byte-identical to freeze commit
`a5adb94387d11dfa23a3e5ea1423332749f96b0e`. The first budget-stop
report/result and the first execution report/result remain unchanged.
The original execution manifest remains bound to authorization commit
`16dad6f52e266de88f9a218938f236d3ef6cd936` and product-behavior
lineage `a0106bd5eff93646f34f5e50e161e8be8a49d680`.

## Same-run continuation and usage

The run ID remains `g3-evidence-admission-audit-novel-dev-v1`: `qa`,
`novel_dev`, non-formal, no candidate, stage tracing enabled, no task-local
model-call/token caps, and no external judge. The existing run manifest's
repository identity blocked direct resume after the first result commit.
An isolated clean checkout at the manifest's authorization commit connected
to the *same local run store* and used the supported `resume_evaluation`
path. No manifest field, product code, model, index, dataset, provider, or
prompt was changed. The checkout used the original run's ignored runtime
directories and the same source-manifest raw bytes; its tracked normalized
manifest blob remained identical to the authorization commit. Local package
metadata was made visible so the recorded package-version receipt matched.
These steps affected only the temporary checkout, not the run manifest or
product lineage. The completed 24 records were not rerun.

Three additional supported resumes attempted only remaining retryable IDs.
The first completed `n007`, `n010`, and `n028`; `n024` remained a Vertex 429
exception. The second retried only `n024` and recorded a retryable Vertex
504. The third completed `n024`. The final run-store status and cohort
status are both `COMPLETE`, with 28/28 QA cases, zero incomplete IDs, and
54 cumulative case attempts.

| Usage | Previous | This continuation | Cumulative |
|---|---:|---:|---:|
| QA runner invocations | 3 | 3 | 6 |
| QA case attempts | 48 | 6 | 54 |
| Model calls | 344 | 46 | 390 |
| Tokens | 1,371,353 | 192,107 | 1,563,460 |
| Generation calls | 304 | 40 | 344 |
| Embedding calls | 40 | 6 | 46 |
| External judge calls | 0 | 0 | 0 |

Deterministic G2 replay contributed zero scientific calls or tokens.
Monetary cost was not measured. The 24-case A0 baseline remains exactly
250 direct admissions and 17 ambiguous-backing rejections over 267 A0
decisions; only newly completed cases increased final denominators.

## Exact-lineage PARTIAL replay

The completion analyzer invokes the unchanged production
`_build_coverage_receipt(...)`. It reconstructs the production V1 call from
the frozen V1 response, normalized draft, deterministic claim-error map,
V1 model input, canonical runtime points, question, retrieval plan, admitted
IDs, and full review-visible evidence resolved through
`qa_stage_trace.evidence_registry`. The legacy requirement ID set is
recomputed by the production `_answer_requirements(...)` helper from the
same frozen question and plan; the V1 model-facing requirement list is empty
under the active coverage mode. The analyzer confirms the projected
reviewable claims match the frozen V1 model input.

Each replayed receipt matches the persisted status, error codes/order,
first error, point IDs/states, relation IDs/states, and verified mappings.
Any mismatch fails closed. Named relation dispositions enter only when the
relation state is `VALID`; ordinary checks enter only from `VALID` points.

| ID | Input complete | Consistent | Receipt | Valid / local-invalid points | Valid named / ordinary checks | Recovered basis links | Recovered visible-only links |
|---|---|---|---|---:|---:|---:|---:|
| `n004` | true | true | `PARTIAL` | 1 / 1 | 0 / 1 | 1 | 0 |
| `n008` | true | true | `PARTIAL` | 1 / 1 | 0 / 1 | 1 | 0 |
| `n027` | true | true | `PARTIAL` | 1 / 1 | 0 / 1 | 1 | 0 |

For each case, the remaining non-authoritative sibling is explicitly
`LOCAL_INVALID_SIBLING_DISPOSITION`. The recovered valid checks use admitted
backing. No raw invalid sibling is promoted into S7/S8 or causal metrics.
The complete capture count is 28, partial capture 0, and non-observable
capture 0. Twenty-seven questions are A0-admission auditable; one never
entered A0/V1 and is not applicable. The same 27 have some authoritative
semantic evidence, of which 24 have full final semantic authority and three
have only replay-valid local children. Three questions therefore retain a
bounded sibling-level semantic limitation.

## S0–S8 and admission outcomes

S2 final selection has 324 evidence opportunities. S0 candidate availability
is `YES=323`, `NOT_OBSERVABLE=1`; S1 ranked/visible is `YES=289`,
`NOT_OBSERVABLE=35`. Trace absence is never treated as `NO`. S3 direct
eligibility is `YES=305`, `NO=19`; S4 exact-backing applicability is
`YES=19`, `NOT_APPLICABLE=305`. S5 admitted backing is `YES=293`, `NO=19`,
`NOT_APPLICABLE=12`; S6 verifier exposure is `YES=312`,
`NOT_APPLICABLE=12`. S7 valid semantic basis and S8 authorization
contribution each have `YES=43`, `NO=236`, `NOT_OBSERVABLE=33`, and
`NOT_APPLICABLE=12`. The 33 unknown evidence-level semantics remain
associated with non-authoritative PARTIAL siblings.

| A0 metric | Numerator / denominator | Unknown questions | Not applicable questions |
|---|---:|---:|---:|
| Admitted / directly eligible | 293 / 312 (93.91%) | 0 | 1 |
| Rejected | 19 / 312 (6.09%) | 0 | 1 |
| Resolved exact backing | 0 / 312 | 0 | 1 |
| `AMBIGUOUS_BACKING` | 19 / 312 | 0 | 1 |
| Each other current rejection code | 0 / 312 | 0 | 1 |

The other production rejection codes are `INVALID_LOCATOR`,
`CONTENT_RELATION_NOT_ESTABLISHED`, `BOUND_EXCEEDED`, `LOOKUP_FAILED`,
`VERSION_MISMATCH`, and `NO_VALID_BACKING`. `INCOMPLETE_SPHINX_LOCATOR`
is not a production decision. Fourteen of 27 A0-auditable questions have
selected-but-unadmitted evidence (14/27; zero unknown, one not applicable).
The A1 target input exposed 3 of 34 admitted A0 IDs in its applicable
questions (3/34; zero unknown, 25 not applicable). These are separate
evidence- and question-level denominators.

All 19 rejections are selected Sphinx documentation pages with ambiguous
exact section backing. Overlapping source-type tags have 293 direct
admissions overall; subtype and reason cross-counts are in the machine
result and are not disjoint totals. The representative stratum has 273/290
admitted selected items across 25 auditable questions; the exploratory
stratum has 20/22 across two. Neither is a release or generalization score.

## Semantic linkage, review, and cause

The final G2 point-validation inventory contains 56 `VALID` and three
`LOCAL_INVALID` points. Valid named relation admission states are
`ADMITTED_BACKING_AVAILABLE=12/16` and
`INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE=4/16`; valid ordinary checks are
`ADMITTED_BACKING_AVAILABLE=42/46` and
`INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE=4/46`. Both distributions have four
question-level unknowns for full-cohort comparison: the three invalid
siblings and the one case without A0/V1.

There are no valid `VISIBLE_ONLY_WITHOUT_CITABLE_BACKING` dispositions.
Traceable visible-only linkage has denominator zero, so its rate is
undefined, with four question-level unknowns. Tier 1 incomplete-question
incidence is 0/24 fully semantic-auditable questions (four unknown).
Tier 2 candidate incidence is also 0/24 (four unknown). Admission policy
is the primary cause in 0/22 adjudicated questions (six unresolved).

The primary cause distribution over all 28 cases is 19 `NOT_APPLICABLE`
(answered with complete valid coverage and no admission-linked failure),
three `OBSERVABILITY_LIMITATION` (the exact replay leaves a local invalid
sibling without valid semantic authority), and six `UNRESOLVED` (an
insufficient answer without evidence to isolate one owning layer). All
other primary taxonomy codes have observed count zero. In particular,
`n010` has valid semantic insufficiency but no selected admission rejection;
the retrieval/generation/semantic owner remains unresolved rather than being
forced into an admission category.

The prior bounded review of `n004`, `n006`, `n017`, and `n027` was retained.
The host analyst additionally inspected `n024` and `n028`: both are answered
with complete valid point coverage using admitted basis IDs other than their
rejected Sphinx overview page. Neither yields an answerability-gap link.
No Gold answer was used as a repair target. `TIER1_REVIEWED=0`,
`TIER2_CANDIDATES=0`, `TIER2_INDEPENDENT_REVIEW_COMPLETED=false`, and
`TIER2_INDEPENDENT_REVIEW_PENDING=false`; no second reviewer was simulated.

## Boundaries, verification, and lifecycle

The analyzer's exact-replay checks passed for all three real frozen cases.
A focused audit-only check confirmed that valid children survive, invalid
siblings remain excluded, and a mutated persisted error code makes replay
fail closed. `py_compile`, JSON/inventory reconciliation, the unchanged
24-case A0 baseline assertion, and `git diff --check` passed. No full
repository test suite or counterfactual product run was used.

The only implementation edit is the audit-only analyzer under
`evaluation/`. Product source, product behavior, prompts, product/trace/
manifest schemas, retrieval, admission, G1/G2, evaluator scoring, Gold,
calibration, and the frozen cohort are unchanged. Audit analysis artifacts
and current status documents changed. All 28 frozen `novel_dev` case
contents and outcomes were accessed for this authorized audit;
`novel_validation` and holdout content/outcome access are 0/0 each, and
protected leakage is zero.

`PHASE_G = IN_PROGRESS / G3_SCOPED_AUDIT_COMPLETE`.
`G3 = SCOPED AUDIT COMPLETE / NO_CHANGE / PRODUCT CHANGE NOT_AUTHORIZED`.
`NEXT_TASK_RECOMMENDATION = G4 FALSE-INSUFFICIENCY / CONSERVATISM REGRESSION DESIGN`.
`NEXT_TASK_EXECUTION_AUTHORIZED = false`.

The machine-readable completion result is
`evaluation/G3_SCOPED_AUDIT_COMPLETION_RESULT.json`; the bounded completion
review is in `evaluation/G3_SCOPED_AUDIT_COMPLETION_REVIEW_OVERLAY.json`.
Raw run records remain in the ignored standard run store.
