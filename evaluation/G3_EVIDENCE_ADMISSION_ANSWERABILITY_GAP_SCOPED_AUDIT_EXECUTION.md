# G3 Evidence Admission / Answerability Gap Scoped Audit — Execution Continuation

## 1. Decision

**INCONCLUSIVE.** The fixed 28-ID novel_dev cohort was executed through the
supported non-formal `qa` runner with stage tracing. Twenty-four cases have
QA results and complete trace capture; four remain incomplete after the
initial attempt and two supported resumes because of retryable Vertex 429
infrastructure failures. Three of the completed cases also have a `PARTIAL`
G2 review without an authoritative per-round valid-disposition projection.
The resulting 20 admission-and-semantic-auditable questions show no Tier 1
selected-unadmitted visible-only linkage, but the missing cohort evidence
prevents a whole-cohort causal conclusion. No admission-policy change is
justified or authorized.

This is a new execution result. The earlier
`G3_EVIDENCE_ADMISSION_ANSWERABILITY_GAP_SCOPED_AUDIT.md` and
`G3_SCOPED_AUDIT_RESULT.json` remain unchanged as the historical
budget-preflight stop.

## 2. Frozen cohort and authorization

The original outcome-blind cohort in
`evaluation/G3_SCOPED_AUDIT_COHORT.json` is unchanged from freeze commit
`a5adb94387d11dfa23a3e5ea1423332749f96b0e`. It contains all 28
human-approved, split-frozen `novel_dev` IDs from dataset identity
`novel-v1-dev-expansion`, benchmark `novel-v1-dev-0.3.0`, version `0.3.0`.
The 28-ID census, not artifact availability or outcome, fixed membership.
Metadata classifies 26 as representative and two as exploratory.

Authorization commit `16dad6f52e266de88f9a218938f236d3ef6cd936`
superseded only the prior task-local limits of 300 model calls and
2,500,000 tokens. The execution manifest records both limits as null.
It binds the exact 28 IDs, `qa`, `novel_dev`, non-formal/no candidate,
`capture_stage_trace=true`, dataset SHA256
`25ad18fcf76ab2796aa18ae961bdc4faf076f0c98a8a5226413ec95e58252223`,
prompt fingerprint
`5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce`,
and the clean authorization commit as repository identity. The
product-behavior lineage remains
`a0106bd5eff93646f34f5e50e161e8be8a49d680`.

## 3. Execution and infrastructure

The run ID is `g3-evidence-admission-audit-novel-dev-v1`. No compatible
current-lineage QA artifact was reusable, so all 28 IDs required fresh
capture. The initial run attempted all 28; 14 succeeded. The first supported
resume attempted the 14 retryable IDs and increased completed cases to 22.
The second resume attempted the six remaining IDs and increased completion
to 24. In total, 48 case attempts were recorded, with 24 completed QA cases
and four current retryable exceptions: `n007`, `n010`, `n024`, and `n028`.
Each current exception is a provider/transport `429 RESOURCE_EXHAUSTED`, not
an answer-quality or admission-policy result. Completed immutable records
were not rerun. The run-store status is `recovery_pending` and its cohort
status is `INCOMPLETE`.

Authoritative attempts-ledger and run-status accounting agrees on **344
model calls and 1,371,353 tokens**: 304 generation requests and 40 embedding
requests. Configured generation and verification use `gemini-3.8-flash`;
query embeddings use `gemini-embedding-2`. The configured evaluator judge
was never called. There were three `qa` runner invocations (initial plus
two resumes), zero retrieval-only runs, zero `full` runs, and zero external
judge calls. The repository `.env` was explicitly loaded after a first
pre-manifest configuration error; that error produced no model or QA call.

## 4. Trace qualification and S0–S8

All 24 completed QA records have `qa_stage_trace.capture_status=COMPLETE`
and a same-run retrieval trace. The four exception cases are
`NOT_OBSERVABLE`; none is called `NO`. A complete capture can correctly mark
an unentered stage `NOT_EXECUTED`. In one completed case A0/V1 was not
entered, so its 12 selected items are excluded from the A0 admission
denominator as `NOT_APPLICABLE`.

| Stage | Selected-evidence observations among completed cases |
|---|---|
| S0 channel candidate | YES 278, NOT_OBSERVABLE 1 |
| S1 stored ranked/visible | YES 249, NOT_OBSERVABLE 30; bounded-trace absence is not NO |
| S2 final selected | YES 279 |
| S3 direct citation eligibility | YES 262, NO 17, replayed with the current predicate |
| S4 exact-backing applicability | YES 17, NOT_APPLICABLE 262; precise attempted substage remains conditional |
| S5 admitted backing | YES 250, NO 17, NOT_APPLICABLE 12 |
| S6 verifier exposure | YES 267, NOT_APPLICABLE 12; visibility is distinct from citation admission |
| S7 valid semantic basis | YES 32, NO 199, NOT_OBSERVABLE 36, NOT_APPLICABLE 12 |
| S8 authorization contribution | YES 32, NO 199, NOT_OBSERVABLE 36, NOT_APPLICABLE 12 |

The four failed questions have no evidence-level stage denominator. S0/S1
membership comes only from authoritative same-run retrieval records. No
fused rank was reconstructed from unordered serialized maps. S2 selected
items remain the primary admission denominator. The deterministic records
use final EA decisions and parent/backing IDs; they never treat
`rejected_evidence_ids` as a rejection count.

Three completed questions (`n004`, `n008`, `n027`) have `PARTIAL` G2 review
validation but no complete final per-round accepted-coverage projection.
Their S7/S8 semantics are `NOT_OBSERVABLE`; `LOCAL_INVALID` is not an
admission verdict. Across available G2 point validation, 47 point results
are `VALID` and three are `LOCAL_INVALID`. The audit records V1 and V2
event status separately and uses the final authoritative G2 receipt only
where available; it does not infer valid PARTIAL rows from raw verifier text.

## 5. Admission results and source strata

Twenty-three questions have complete A0 decision alignment. They contribute
267 selected-item decisions: 250 `DIRECTLY_CITATION_ELIGIBLE`, zero
`RESOLVED_EXACT_BACKING`, and 17 `AMBIGUOUS_BACKING`. All other current
runtime rejection codes have zero observed decisions. The latter are
`INVALID_LOCATOR`, `CONTENT_RELATION_NOT_ESTABLISHED`, `BOUND_EXCEEDED`,
`LOOKUP_FAILED`, `VERSION_MISMATCH`, and `NO_VALID_BACKING`.
`INCOMPLETE_SPHINX_LOCATOR` is only a trace fallback label and was not counted
as a production decision.

| Selected-item metric | Numerator / denominator | Unknown questions | Rate |
|---|---:|---:|---:|
| A0 admitted | 250 / 267 | 4 | 93.63% |
| A0 rejected | 17 / 267 | 4 | 6.37% |
| Directly eligible | 250 / 267 | 4 | 93.63% |
| Resolved exact backing | 0 / 267 | 4 | 0% |
| Ambiguous backing | 17 / 267 | 4 | 6.37% |
| Each other rejection code listed above | 0 / 267 | 4 | 0% |

The A0-not-executed question is separately `NOT_APPLICABLE`. Twelve of 23
A0-auditable questions have at least one selected-but-unadmitted item
(12/23; four unknown and one not applicable). This is Tier 0 frequency
evidence only, not a semantic or policy-defect rate.

All 17 observed rejections are for selected Sphinx documentation pages
with ambiguous exact section backing. Coarse source tags may overlap; the
existing classifier yields direct-admission counts of code 128, paper 50,
documentation 72, workflow 24, readme 14, and graph 4. These tag counts
must not be added as disjoint categories. The audit also records source
object subtype when present in the bound retrieval trace and keeps
unavailable subtypes as `UNKNOWN`.

The representative subset has 241 admitted of 257 A0-auditable selected
items (22 auditable questions; three unknown, one A0 not applicable). The
exploratory subset has nine of ten (one auditable question; one unknown).
Neither is a release score or Representative Generalization Gap.

## 6. A1, relation/check linkage, and authorization

A1 ran in three auditable questions. Its target evidence input exposed three
of the 34 admitted A0 IDs for those questions (3/34; four questions unknown,
21 not applicable). This narrow target exposure is not an independent
second admission decision.

Among authoritative final valid dispositions, named relations have
`ADMITTED_BACKING_AVAILABLE` 10/13 and
`INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE` 3/13. Accepted ordinary checks have
the respective counts 32/36 and 4/36. Eight questions lack comparable
final semantic authority (four infrastructure failures, three PARTIAL
without per-round receipt, one without A0/V1). There are no valid
`VISIBLE_ONLY_WITHOUT_CITABLE_BACKING` dispositions in the auditable set:
traceable visible-only linkage has denominator zero and no meaningful rate.

Tier 1 incomplete-question incidence is 0/20 questions with both admission
and authoritative final semantic records (eight unknown). Tier 2 candidate
incidence is likewise 0/20 (eight unknown). Admission-policy-primary
incidence is 0/19 adjudicated question-level causes (nine unknown or
unresolved). These observations do not prove that the four unexecuted
questions lack a gap.

## 7. Root causes and bounded manual review

The 24 completed QA questions have these cautious primary classifications:
16 `NOT_APPLICABLE` (answered, no final admission gap established), three
`OBSERVABILITY_LIMITATION` (PARTIAL per-round valid-disposition authority
missing), and five `UNRESOLVED` (no evidence sufficient to distinguish the
owning downstream layer). Four exception questions are outside this
answerability-cause denominator and are explicitly recorded as
infrastructure-incomplete. Every other primary taxonomy code, including
`ADMISSION_POLICY` and `ADMISSION_DATA_INTEGRITY`, has observed count zero
over 24 completed questions with four unknown; zero does not establish a
corpus-wide absence.

One host analyst reviewed bounded selected-page excerpts and final
validated coverage for `n004`, `n006`, `n017`, and `n027`, targeting
ambiguous causal classification. Each had a selected Sphinx page rejected
as `AMBIGUOUS_BACKING`, but none had a `VALID` visible-only disposition
citing that rejected item as basis. `n004` and `n027` additionally lack
authoritative PARTIAL per-round semantics. Page relevance alone was not
promoted to Tier 1, Tier 2, or a safe-citation finding. No Gold answer was
used to decide factual sufficiency. `TIER1_REVIEWED=0`,
`TIER2_CANDIDATES=0`, `TIER2_INDEPENDENT_REVIEW_COMPLETED=false`, and
`TIER2_INDEPENDENT_REVIEW_PENDING=false`; no second reviewer was simulated.

## 8. Limitations, product gate, and lifecycle

The causal question cannot be closed for the fixed cohort while four cases
have only 429 exceptions and three others lack authoritative PARTIAL
per-round dispositions. The 17 observed selected-item admission rejections
are real, but no valid semantic link establishes that they caused an
answer-authorization failure. There was no counterfactual admission run,
no repair, no historical exposed benchmark guidance, and no protected-data
access. The audit cannot establish corpus-wide prevalence or a
generalization score. Product source, retrieval, admission, G1/G2, prompts,
schemas, evaluator, Gold, and calibration are unchanged.

`PHASE_G = IN_PROGRESS / G3_SCOPED_AUDIT_EXECUTION_INCONCLUSIVE`.
`G3 = SCOPED AUDIT EXECUTED / INCONCLUSIVE (PERSISTENT_VERTEX_429_AND_PARTIAL_SEMANTIC_AUTHORITY) / PRODUCT CHANGE NOT_AUTHORIZED`.
`NEXT_TASK_RECOMMENDATION = RESUME THE SAME G3 FROZEN-COHORT QA RUN AFTER VERTEX 429 RECOVERY`.
`NEXT_TASK_EXECUTION_AUTHORIZED = false`.

The next task must preserve the same 28 IDs, run identity, `qa` mode,
stage-trace requirement, and product lineage. It must not use protected
splits or implement an audit-driven repair. The three PARTIAL cases retain
their stage-specific `NOT_OBSERVABLE` semantics unless an exact-lineage
deterministic replay is separately justified and possible.

## 9. Scientific and data-access accounting

| Item | Actual |
|---|---:|
| Frozen / fresh-required / fresh-attempted IDs | 28 / 28 / 28 |
| Reused / completed / incomplete cases | 0 / 24 / 4 |
| QA case attempts / QA runner invocations | 48 / 3 |
| Scientific model calls / tokens | 344 / 1,371,353 |
| Generation / embedding / external judge calls | 304 / 40 / 0 |
| `novel_dev` case-content / outcome access | 28 / 28 |
| `novel_validation` case-content / outcome access | 0 / 0 |
| Holdout case-content / outcome access | 0 / 0 |
| Protected leakage | 0 |

`EMPIRICAL_AUDIT_EXECUTED=true`; `EMPIRICAL_ADMISSION_GAP_ESTABLISHED=false`.
The machine-readable execution result is
`evaluation/G3_SCOPED_AUDIT_EXECUTION_RESULT.json`, generated by the
audit-only `evaluation/g3_scoped_audit_analyze.py` with a separate bounded
review overlay. Raw run records remain in the ignored standard run store
and are not copied into this commit.
