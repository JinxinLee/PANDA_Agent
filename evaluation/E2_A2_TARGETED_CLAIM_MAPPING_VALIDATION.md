# E2-A2 — Targeted Claim-Mapping and Missing-Point Validation

E2-A2 VERDICT = PASS

COMPLETE / PASS / TARGETED_CLAIM_MAPPING_AND_MISSING_POINT_VALIDATION_PASSED

## Provenance and scope

- Starting implementation: `df52bcddf612515418be298fafde6ebcb32d4a67`.
- Historical E1-A2 source: `77ea6bc27beb1657673e57be763b05419c98bc05`.
- Preregistration: `78969ceee0bd316e7a9632440c175bcdac04f3bc`.
- Natural raw freeze: `ee8049e760c9ef46d2096fd91ff6e5e9716dcde8`.
- Natural judgment freeze: `3f50f15c6359145dd77acacf715a38e660bd3b6f`.
- Controlled manifest freeze: `a9368e5404c164b9b32a72617e9b664ec241e2ef`.
- Closeout identity: the normal Git commit containing this report, controlled raw,
  deterministic result, and current lifecycle updates. No earlier freeze amended.

This is targeted exposed-development T2-style validation. Exactly six historical
pairs07-12, 12 English novel_dev questions (six base/six paraphrase), and 28 frozen
semantic reference obligations were mechanically selected. Two fresh repetitions
produced 24 instances, not 24 independent questions. Base/paraphrase and repeated
executions are correlated. No protected validation or holdout was accessed.

Actual frozen E2-A1 diagnostic graph execution was used, with only raw question
as product input. Product code, prompts, models, configs, protocol and tests were
unchanged after preregistration. No E2 repair, normal QA activation or E3 occurred.

## Natural applicability and gates

| Slice | Attempted | E1-reference-conformant | E2-applicable |
|---|---:|---:|---:|
| rep1 | 12/12 | 12/12 | 12/12 |
| rep2 | 12/12 | 12/12 | 12/12 |
| Pooled | 24/24 | 24/24 | 24/24 |

| Gate | Exact accounting | Observed | Threshold | Verdict |
|---|---|---:|---:|---|
| N1 applicability | 12/12, 12/12, 24/24 | sufficient | >=10 each, >=20 pooled | PASS |
| N2 mapping edge precision | TP 74 / predicted 79 | 93.67% | >=90% | PASS |
| N3 mapping edge recall | TP 74 / truth 75 | 98.67% | >=90% | PASS |
| N4 exact mapping-set accuracy | exact 68 / judgeable claims 74 | 91.89% | >=85% | PASS |
| N5 coverage precision | TP 56 / predicted covered 56 | 100% | >=95% | PASS |
| N6 coverage recall | TP 56 / judge-covered truth 56 | 100% | >=90% | PASS |

Exact coverage-set agreement: 24/24. False-covered points: 0; false-missing
points: 0. UPSTREAM_E1_INPUT_INVALID: 0; coverage_evaluable=false: 0;
answerability/refusal: 0; natural coverage-review structural failures: 0.
All final claims used in these denominators were supported and rendered.
There were seven natural bounded revisions and no pre-answer targeted retrieval.

| Repetition | Edge precision | Edge recall | Exact claim mappings | Coverage precision/recall |
|---|---|---|---|---|
| rep1 | 39/41 = 95.12% | 39/39 = 100% | 35/37 = 94.59% | 28/28 = 100% each |
| rep2 | 35/38 = 92.11% | 35/36 = 97.22% | 33/37 = 89.19% | 28/28 = 100% each |

Applicability and coverage agreement are unchanged across all 12 repetition
pairs. Mapping error-count patterns differ for three questions: b08 has one
extra edge in both repeats and an additional missed edge in rep2; b11 changes
from no mapping errors to two extra edges; p10 changes from one extra edge to
none. Claims themselves are freshly generated and are not paired by literal
claim or point ID. This is a descriptive comparison, not another gate.

## Residual mapping errors

PASS does not mean zero mapping errors. Five extra edges and one missed edge
occur in four execution instances:

| Execution | Extra verified edge(s) | Missing verified edge(s) |
|---|---|---|
| e1a2.b08.rep1 | claim.2 -> point.1 | none |
| e1a2.p10.rep1 | claim_2 -> point.1 | none |
| e1a2.b08.rep2 | claim_2 -> point.1 | claim_1 -> point.2 |
| e1a2.b11.rep2 | claim_ip_alignment_poca_workflow -> point.2; claim_workflow_order_stages -> point.2 | none |

These are disagreements against the frozen independent semantic judge, not an
additional factual-evidence evaluation. In b08 the algorithm-comparison claim
also received the other point, while rep2's algorithm description additionally
addressed a point the product omitted. In p10 and b11 the reviewer mapped
workflow statements beyond the independently judged obligations they address.
The raw claim text, point text, prediction and truth remain in frozen artifacts.
No failure-specific repair was attempted.

Failure taxonomy: CLAIM_POINT_FALSE_POSITIVE=5 edges;
CLAIM_POINT_FALSE_NEGATIVE=1 edge; CLAIM_POINT_OVERMAPPING=5 claims;
COVERAGE_FALSE_COMPLETE=0 points; COVERAGE_FALSE_MISSING=0 points;
DROP_TARGET_NOT_DETECTED=0; DROP_COLLATERAL_FALSE_MISSING=0;
COVERAGE_REVIEW_STRUCTURAL_INVALID=0. Provider/evaluation infrastructure failures=0.
Per-source and per-pair accounting is stored in the machine-readable result.

## Controlled claim-drop slice

Rep1 baselines considered: 12. Eligible variants: 11.
BASELINE_NOT_APPLICABLE=0; BASELINE_NOT_COMPLETE=0; LESS_THAN_TWO_POINTS=0;
NO_ISOLATABLE_DROP_TARGET=1 (`e1a2.p09.rep1`); other=0.
This exclusion follows independent multi-point claim entanglement, not E2
prediction quality. No alternative target or fallback was introduced.

| Gate | Exact accounting | Observed | Threshold | Verdict |
|---|---|---:|---:|---|
| D1 eligible variants | 11 | sufficient | >=8 | PASS |
| D2 target detection recall | 11 detected / 11 targets | 100% | >=90% | PASS |
| D3 missing-set precision | 11 correct / 11 missing reports | 100% | >=90% | PASS |
| D4 exact missing-set accuracy | 11 exact / 11 variants | 100% | >=80% | PASS |

Target not detected=0; collateral false-missing points=0; empty missing sets=0;
all-points-missing cases=0; controlled structural failures=0.
Each eligible variant executed exactly one existing E2 review. Retained claims,
declared mappings, points, evidence and legacy requirements were preserved.
Controlled decomposition, analyzer, embedding, reranker, retrieval, answer and
revision logical calls are each exactly 0. No second repair review occurred.

## Observed usage

| Stage | Logical calls | Returned responses | Adapter request counter | Returned token counter |
|---|---:|---:|---:|---:|
| decomposition | 24 | 24 | 24 | 34,011 |
| analyzer | 24 | 24 | 24 | 57,834 |
| embedding | 24 | 24 | 24 | 0 |
| reranker | 24 | 24 | 24 | 387,351 |
| retrieval | 24 | 0 | 0 | 0 |
| qa_answer | 24 | 24 | 24 | 508,227 |
| qa_review | 31 | 31 | 31 | 660,696 |
| qa_revision | 7 | 7 | 7 | 181,320 |
| judge | 24 | 24 | 24 | 45,414 |
| controlled_review | 11 | 11 | 11 | 216,080 |
| Total | 217 | 193 | 193 | 2,090,933 |

Returned responses include 169 structured-generation responses and 24 embedding
responses. Retrieval is a logical pipeline call, not an additional model response.
Embedding returned-token metadata is not exposed by the current counter: its
recorded zero is not a claim of zero embedding consumption. The total is the
observed returned-token counter (2,090,933), not an estimate of all billed tokens.
The 193 adapter request observations are not independently audited HTTP/billing
requests; no unavailable retry or monetary-cost statistics are invented.

Generation/reviewer and independent judge use gemini-3.8-flash, temperature 0,
global. Embedding uses gemini-embedding-2, 3072 dimensions. Judge inputs were
blinded to E2 mappings, coverage, reasoning and metadata, but the model family
is the same, so correlated semantic bias remains a limitation.

AGY job staffer-mtt5zej2-67468860 completed abstract static design review before
freeze, without repository inspection/edits. Runner routing was
 gemini-3.8-flash-high; worker model/effort and tokens were not independently
observed. AGY usage is separate, unavailable, and not claimed to be zero.

## Verification and invariants

- E2-A2 focused static tests: 32 passed. E2-A1 shared-seam tests: 42 passed.
  Test-fixture import/reference issues found in the first offline run were fixed
  before freeze; no product or scientific-outcome repair occurred.
- Natural raw identities: all 24 complete, unique and reconciled; 24 independent
  judgments complete; all 12 controlled eligibility decisions mechanically
  reproduced; all 11 eligible review records reconciled.
- Deterministic serialized result recomputation matches exactly, including every
  field and all metrics. The frozen CLI's second `score` invocation fails its
  direct Python equality assertion because 154 edge pairs are tuples in memory
  but lists after JSON loading. Read-only diagnosis found only list/tuple type
  differences; serializing the unchanged score function's output reproduces the
  existing result text exactly. No runner, score, gate or artifact was repaired
  or overwritten. This nonfatal offline verification limitation does not remove
  authoritative scoring; scientific execution/judge infrastructure failures stay
  0. The standalone repeat-score CLI check itself did not pass.
- Protocol/subject Git boundary and diff whitespace checks pass. No full suite
  or unrelated T3/T4/T5 was run.
- Zero-tolerance violations: 0. Accepted unknown point IDs=0; internal claims
  credited=0; protected data accessed=0; all forbidden controlled stages=0;
  normal production activation=0; post-result cohort/threshold/prompt/judge
  tuning=0. Frozen source, protocol and implementation were not changed.
- Operational caveat: Qdrant client 1.19.0 warned about server 1.15.5 compatibility.
  All planned runs nevertheless completed without an infrastructure failure;
  no version/config change was made.

## Lifecycle and interpretation

E1 historical lifecycle is preserved, including E1-A2 FAIL, E1-R2 PASS and E1-C1
PASS. E2-A1 remains COMPLETE/PASS/SHADOW_ANSWER_POINT_COVERAGE_CONTRACT_IMPLEMENTED.
D4 remains PAUSED/ROADMAP_RECONCILIATION with completion UNDECIDED; F1 and Phase F
remain unchanged. E2-A1 implementation changed after preregistration: no.
facet_type used for E2 correctness: no. Normal production activation: no.

E2-A2 = COMPLETE / PASS / TARGETED_CLAIM_MAPPING_AND_MISSING_POINT_VALIDATION_PASSED

E2 = IN_PROGRESS / TARGETED_COVERAGE_VALIDATED / RUNTIME_ACTIVATION_PENDING

Phase E = IN_PROGRESS / E2

E3 = NOT_STARTED

NEXT_TASK_RECOMMENDATION = E2-A3 — Bounded Runtime Activation and Regression Check

NEXT_TASK_EXECUTION_AUTHORIZED = false

The shadow mapping and coverage mechanism passed the frozen targeted exposed
natural and controlled missing-point validation. This does not establish
representative PANDA generalization, production readiness, E2 completion, E3
validity, or removability of legacy requirements. It supports proceeding to a
separately authorized bounded runtime activation/regression review; that task
has not been executed.
