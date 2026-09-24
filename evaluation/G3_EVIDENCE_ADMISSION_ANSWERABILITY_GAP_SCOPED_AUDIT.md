# G3 Evidence Admission / Answerability Gap Scoped Audit — Budget-Preflight Stop

## 1. Decision

**INCONCLUSIVE.** The outcome-blind cohort was frozen and selected-ID artifact
qualification was completed. All 28 IDs require fresh current-lineage QA stage
capture. Fresh execution was stopped before the first case because the
supported runner cannot guarantee the authorized 300-model-call and
2,500,000-token hard caps for this cohort. No admission gap or answerability
mechanism was empirically measured. This is an execution-budget finding, not
an answer-quality, admission-policy, or trace-schema finding.

## 2. Frozen cohort

The dedicated freeze commit `a5adb94` contains only
`evaluation/G3_SCOPED_AUDIT_COHORT.json`. It was committed before any case
result or QA outcome was opened. The authoritative dataset is
`evaluation/novel/v1/novel_dev.yaml`, benchmark
`novel-v1-dev-0.3.0`, dataset version `0.3.0`, identity
`novel-v1-dev-expansion`; the dataset SHA256 is recorded in the frozen
manifest using the runner's dataset-hash convention. The reviewed eligibility
projection required `split=novel_dev`, `review_status=approved`, sidecar
`lifecycle=split_frozen`, and a stable ID. It found 28 eligible IDs, so the
accepted `<=30` census rule selected all 28. The fixed seed
`g3-evidence-admission-answerability-audit-v1` was recorded but not used to
rank a census. Artifact availability and outcome data did not affect selection.
The IDs have not changed. After freeze, the sidecar classified 26 selected
questions as representative and two as exploratory; neither class has a
measured QA result in this task.

Starting repository HEAD was `910c4fcd4db03c8fcce1a81a7cf15366122b234a`.
The product-behavior lineage remains
`a0106bd5eff93646f34f5e50e161e8be8a49d680`.

## 3. Execution and artifact reuse

The standard run-store manifest inventory has one historical `novel_dev`
retrieval-only run, with no QA stage trace and no current G2 identity. It is
not reusable for G3 S5–S8. There is no compatible current-lineage
`novel_dev` QA stage-traced run. Therefore each of the 28 frozen IDs is
`FRESH_CAPTURE_REQUIRED`; none was replaced. The planned run ID
`g3-evidence-admission-audit-novel-dev-v1` was available and was not started.
No `qa` or `full` execution, external judge, retrieval run, or model call
occurred. The intended path remains non-formal, non-candidate `qa` with
`capture_stage_trace=True` through `run_evaluation()`.

### Budget preflight

`VertexAIClient.generate_json()` allows up to three requests and query
embedding up to five requests on transient failures. An ordinary successful
QA path can execute decomposition, query analysis, one query embedding,
reranking, A0 generation, and V1 verification. Those six stage calls can
consume `3 + 3 + 5 + 3 + 3 + 3 = 20` model requests for one completed case
when each succeeds on its last permitted attempt. For 28 cases, that path
alone permits **560 requests**, exceeding the authorized 300. Targeted
retrieval, revision, V2, and composer calls can raise it further.

The runner checks `max_model_calls` and `max_token_usage` only before and
after a whole case; it has no intra-case hard stop. It also has no proven
hard token upper bound for this cohort. Passing `300` and `2500000` as runner
arguments would therefore not establish the requested hard caps. The task's
explicit rule requires stopping before fresh execution when the actual
possible upper bound exceeds either cap. This report does not estimate actual
usage from that upper-bound argument: actual scientific usage was 0 calls and
0 tokens. A separately authorized, enforceable budget contract or revised
caps proven against the complete frozen cohort is needed before execution.

## 4. Trace completeness and evidence funnel

Complete: 0 questions. Partial: 0. `NOT_OBSERVABLE`: 28. S0–S8 are
`NOT_OBSERVABLE` for every frozen ID because no compatible same-run QA
artifact exists. There are no evidence-opportunity or relation/check-linkage
records. In particular, missing trace is not interpreted as `NO` at any
stage, and no selected-evidence denominator can be constructed. The
historical retrieval-only run is not substituted into the frozen cohort's
current-lineage funnel.

## 5. Admission outcomes, linkage, and metrics

The current runtime selected-item outcomes were checked against
`src/panda_agent/qa.py`:
`DIRECTLY_CITATION_ELIGIBLE`, `RESOLVED_EXACT_BACKING`,
`INVALID_LOCATOR`, `CONTENT_RELATION_NOT_ESTABLISHED`, `BOUND_EXCEEDED`,
`LOOKUP_FAILED`, `VERSION_MISMATCH`, `AMBIGUOUS_BACKING`, and
`NO_VALID_BACKING`. `INCOMPLETE_SPHINX_LOCATOR` remains a trace fallback
label, not a runtime decision. **No outcome count is observable**; a blank
denominator is not a zero-rejection finding. No `rejected_evidence_ids`
shortcut was used.

| Metric group | Numerator | Auditable denominator | Unknown questions |
|---|---:|---:|---:|
| A0 admission/rejection, direct, resolved, each rejection code | N/A | 0 selected items observed | 28 |
| A1 target exposure | N/A | 0 admitted backings observed | 28 |
| Questions with selected-but-unadmitted evidence | N/A | 0 auditable questions | 28 |
| VALID named-relation and ordinary-check admission states | N/A | 0 valid dispositions observed | 28 |
| Traceable visible-only linkage | N/A | 0 valid visible-only dispositions observed | 28 |
| Tier 1 incomplete-question and Tier 2 candidate incidence | N/A | 0 auditable questions | 28 |
| Primary root causes and admission-policy-primary incidence | N/A | 0 classified questions | 28 |

The unknown count is at question level; the number of unknown evidence items
and relation/check dispositions itself cannot be determined without QA
artifacts. No rate or source-type distribution is computed. Machine-readable
nulls, zero auditable denominators, and the 28 unknown questions are recorded
in `evaluation/G3_SCOPED_AUDIT_RESULT.json`.

## 6. Tiers, manual review, and causal classification

No Tier 0 observation, Tier 1 linkage, or Tier 2 candidate was observed.
No bounded semantic manual review or independent Tier 2 review was possible
or performed. `TIER1_REVIEWED=0`, `TIER2_CANDIDATES=0`,
`TIER2_INDEPENDENT_REVIEW_COMPLETED=false`, and
`TIER2_INDEPENDENT_REVIEW_PENDING=false`. These zeroes describe work and
observations, not an absence of underlying gaps. All 28 root causes remain
unclassified. No `ADMISSION_POLICY` primary cause or policy-change gate is
established.

## 7. Limitations and product-change gate

The audit cannot answer how often selected evidence was blocked by admission
or citation authority rather than retrieval, semantics, verifier behavior,
claim mapping, or generation. There is no empirical denominator for any of
those alternatives. Cohort composition alone cannot establish corpus-wide
prevalence or a Representative Generalization Gap. Gold answer text was not
consulted. No counterfactual or repair was attempted. Product, retrieval,
admission, G1/G2, prompts, provider schema, trace/manifest schema, evaluator,
Gold, and calibration were unchanged. Product changes remain unauthorized.

## 8. Lifecycle and accounting

`PHASE_G = IN_PROGRESS / G3_SCOPED_AUDIT_BUDGET_PREFLIGHT_BLOCKED`.
`G3 = COHORT FROZEN / SELECTED-ID ARTIFACT QUALIFICATION COMPLETE /
INCONCLUSIVE / PRODUCT CHANGE NOT_AUTHORIZED`.
`NEXT_TASK_RECOMMENDATION = G3 FRESH-CAPTURE BUDGET RESOLUTION FOR THE FROZEN
28-ID COHORT`.
`NEXT_TASK_EXECUTION_AUTHORIZED = false`.

| Accounting item | Value |
|---|---:|
| Eligible / frozen IDs | 28 / 28 |
| Reused / fresh-captured / unexecuted | 0 / 0 / 28 |
| Completed / incomplete attempted fresh cases | 0 / 0 |
| Retrieval runs / QA runs / external judge calls | 0 / 0 / 0 |
| Scientific calls / tokens | 0 / 0 |
| `novel_dev` case-content / outcome access | 0 / 0 |
| `novel_validation` case-content / outcome access | 0 / 0 |
| Holdout case-content / outcome access | 0 / 0 |
| Protected leakage | 0 |

`AUDIT_EXECUTED=false`; `EMPIRICAL_ADMISSION_GAP_ESTABLISHED=false`.
The frozen cohort and result report are audit artifacts; the status and
roadmap changes describe the stop. No product source or behavior changed.
