# G4 R2 Post-Correction Exposed Verification Design

## 1. Decision and scope

```text
G4_POST_CORRECTION_EXPOSED_VERIFICATION_DESIGN = PASS / EXECUTION READY
POST_CORRECTION_VERIFICATION_STRATEGY = TWO_LAYER_TARGETED
LAYER_A_CASES = [n002, n006, n017, n024]
LAYER_A_SCIENTIFIC_CALLS = 0
LAYER_B_CASES = [n002, n017, n024]
FULL_28_CASE_RERUN = false
N006_LIVE_GATE = false
FRESH_LANE_B = OPTIONAL / DEFERRED
```

This design freezes the next task's case selection and decision rules. It executes neither layer. The question is whether the corrected R2 rerank-pool constructor removes the established n024 collateral mechanism while retaining the observed n002/n017 opportunity mechanism. It is not a full `novel_dev` quality gate, a V1/G2 repair, a release comparison, or fresh generalization evidence.

The existing deterministic correction already passed CR-1 RED→GREEN, CR-1–CR-10, R2-A–I, the 31-test R2 module, G4 18/18, and focused retrieval neighbors. Their [implementation result](G4_R2_COLLATERAL_RETENTION_IMPLEMENTATION_RESULT.md) and the [failure review](G4_R2_COLLATERAL_RETENTION_COMPLETENESS_FAILURE_REVIEW.md) remain authoritative for those completed scopes. This design does not reopen the selected exchange policy.

## 2. Product lineage and historical authority

```text
DESIGN_START_HEAD = 047201166057edd9859292a1760bc2e9bbf173a2
CURRENT_PRODUCT_BEHAVIOR_LINEAGE_HEAD = 047201166057edd9859292a1760bc2e9bbf173a2
PREVIOUS_PRODUCT_BEHAVIOR_LINEAGE_HEAD = a22c8f70eeebe4a53490e11a4b6852561ca8afa6
```

At design entry, HEAD was the expected correction commit and the worktree was clean. A design-only descendant does not change product behavior. Before any later scientific call, verify that the execution HEAD is this commit or a design-only descendant whose product source still resolves to it. A new product edit requires a new design/identity decision rather than silently reusing this plan.

Historical exposed authority is the initial [post-repair regression](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION.md) and [machine result](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RESULT.json), the authorized [n002/n018 rerun](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RERUN.md) and [machine result](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RERUN_RESULT.json), and the independent [false-insufficiency diagnostic](G4_EXPOSED_DEVELOPMENT_FALSE_INSUFFICIENCY_DIAGNOSTIC.md) and [machine result](G4_EXPOSED_DEVELOPMENT_FALSE_INSUFFICIENCY_RESULT.json). Their old answers, records, verdicts, and lineage remain unchanged. Use the successful n002 record from `g4-r2-post-repair-n002-n018-rerun-v1`; use n006/n017/n024 from `g4-r2-post-repair-novel-dev-regression-v1`. The initial n002 attempt ended before retrieval and cannot supply a pool replay.

## 3. Historical witnesses and smallest cohort

| Case | Fixed role | Historical observation | Next question |
|---|---|---|---|
| n024 | `PRIMARY_COLLATERAL_CORRECTION_TARGET` | Critical analytic-helix header `object.d6ef560b88c3926ecb32d3e1`, dense 8/sparse 19 and RRF 18, was in the legacy base but lost from the 16 ordinary/14 frontier offer under identical channel rankings. | Does the corrected policy retain its rank witness, either through the object or a legal equal-or-better replacement? |
| n002 | `R2_BENEFIT_PRESERVATION_SENTINEL` | Two requirements objects, `object.a45779701b982aff3e7554da` and `object.03af96b1110e782792253a18`, appeared at dense ranks 7/8 and entered the historical frontier on the authorized rerun. | Do qualifying omitted requirements objects still receive a legitimate offer? |
| n017 | `R2_BENEFIT_PRESERVATION_SENTINEL` | Primary `PndTrack.h` object `object.015bff352e03a5f5ee88c307`, dense rank 7, entered frontier and reached final/cited evidence. | Does the omitted single-channel header still receive an offer? |
| n006 | `RESIDUAL_QUOTA_BOUND_DIAGNOSTIC` | Constructor `object.2914485ff398f61e994c46d6` was code queue position 11; four successful code opportunities exhausted its role ceiling while global capacity was not exhausted. | Is it recovered, still legitimately quota-bound, or newly blocked by the exchange guard? |

The five other worsened sentinels are not established R2 collateral targets: n007/n028/n031 have V1/G2 concerns, n014 answerability remains unresolved, and n018 generation/completeness ownership remains unresolved. Adding them would mix causes. The full 28-case rerun would add scientific cost and provider variation across unrelated cases without a direct correction question. The generic CR controls and the targeted exposed witnesses cover the known R2 risk; no distinct cohort-wide risk has been identified. The three-case Layer B is a scoped T1 diagnostic, not a complete-cohort gate.

## 4. Layer A: zero-call saved-state replay

Layer A is a hard prerequisite to Layer B. Read only the two historical G4 run stores named above. Load each successful case's saved channel order, one-based occurrences and provenance, candidate payload validity fields, plan, RRF scores/order, structured supplements, and actual old pool receipt. Reconstruct the exact input to the current `Retriever._r2_rerank_pool()` in memory; invoke that constructor only. Do not call `Retriever.retrieve()`, any search/index channel, Vertex, QAAgent, reranker, generation, or the external judge. Do not write to old stores. A small read-only analyzer may emit a new result outside them.

Replay identity must include all candidate IDs in the historical channel union, per-channel ranks, the original payload selection semantics, source/version/locator/text validity, target/context source membership, specialized `normal` versus fallback origins, the saved plan, RRF score and stable tie order, supplements, and the actual historical pool. A diagnostic exchange explanation may reconstruct the constructor's steps only to record charged role, explicit victim, and before/after vectors; the product constructor's returned pool is the membership authority. Cross-check that the reconstructed **old** inputs reproduce the saved historical RRF order and old pool receipt before interpreting a new-policy result.

Artifact presence is not proof of exact input reproducibility. This design's read-only availability check found successful records and retrieval traces for all four selected cases in the named stores. It also found a material limitation: public `channel_candidates` rows carry IDs/ranks/source/locator metadata but not full candidate `text`, and the trace does not expose aligned workflow/graph origin sidecars; final-evidence text covers only selected outputs. The earlier [collateral analysis](G4_R2_COLLATERAL_RETENTION_ANALYSIS.json) explicitly used conditional lower/upper provenance reconstructions. Such a conditional model is useful context, **not** an exact Layer A acceptance replay. The execution task must first inspect all saved fields for a lossless, provenance-compatible input reconstruction. If a necessary field is absent for a case, record that dimension as `NOT_REPRODUCIBLE`, identify the missing field, and stop before Layer B. Do not fill gaps from fresh retrieval, guessed normal origins, old reranker output, Gold, or exposed expected answers. Do not turn a conditional replay into `PASS`.

## 5. Layer A per-case gates

```text
N024_REPLAY_COLLATERAL_DISPLACEMENT = MUST_BE_FALSE
N024_ILLEGAL_COLLATERAL_DISPLACEMENT_REPRODUCED = false
N002_REPLAY_OPPORTUNITY_PRESERVED = MUST_BE_TRUE
N017_REPLAY_OPPORTUNITY_PRESERVED = MUST_BE_TRUE
N006_ACCEPTABLE_OUTCOMES = RECOVERED_BY_CORRECTION | STILL_LEGITIMATELY_QUOTA_BOUND
```

For **n024**, report legacy top-30 membership, corrected membership and `ordinary_rrf`/`policy_role_frontier` reason, the historical object's qualifying role/channel ranks, the vector before every proposed exchange that could remove it, the candidate/victim/charged role, and componentwise legality. Classify `RETAINED`, `LEGALLY_REPLACED_BY_EQUAL_OR_BETTER_WITNESS`, or `ILLEGAL_WITNESS_LOSS`. A missing ID alone is not failure if a legal replacement preserves every active vector and improves the charged role. The established illegal displacement must not recur.

For **n002** and **n017**, report each target's saved qualifying ranks, legacy top-30 membership, corrected offered membership/reason, and, if exchanged, charged role, victim, and witness comparison. The historical omitted evidence must retain a legitimate rerank opportunity under that exact saved challenger geometry. These are pool-policy gates, not requirements for identical answers or downstream reranker order.

For **n006**, report the target's queue position, role ceiling, successful admissions before its turn, global capacity, candidate eligibility, and any exchange rejection. Classify `RECOVERED_BY_CORRECTION`, `STILL_LEGITIMATELY_QUOTA_BOUND`, `BLOCKED_BY_NEW_EXCHANGE_GUARD`, or `NOT_REPRODUCIBLE`. The first two are acceptable. A new exchange-guard block does not meet this predefined Layer A acceptance condition; inspect whether it obeys or contradicts the approved invariant, without forcing recovery. The separate V1/G2 false-acceptance concern does not become an R2 success gate.

Layer A passes only when n024 has no illegal displacement, both benefit sentinels preserve opportunity, n006 is in an acceptable class, and no saved replay contradicts the deterministic rank-witness contract. Any established illegal loss, benefit regression, or contract contradiction is `FAIL`; a needed exact input marked `NOT_REPRODUCIBLE` or a legal but new n006 guard-bound state is `INCONCLUSIVE`. Neither permits live execution under this plan.

## 6. Layer B: frozen three-case live QA

Only after Layer A `PASS`, use the existing runner and the existing exposed dataset:

```python
run_evaluation(
    PROJECT_ROOT,
    mode="qa",
    split="novel_dev",
    run_id="g4-r2-post-correction-exposed-target-v1",
    allow_draft=True,
    dataset_path=PROJECT_ROOT / "evaluation/novel/v1/novel_dev.yaml",
    case_ids=["n002", "n017", "n024"],
    capture_stage_trace=True,
)
```

```text
LIVE_TARGET_SELECTION_FROZEN = true
POST_OUTCOME_CASE_PRUNING = false
RUN_ID = g4-r2-post-correction-exposed-target-v1
MODE = qa
SPLIT = novel_dev
CASE_IDS = [n002, n017, n024]
CAPTURE_STAGE_TRACE = true
ALLOW_DRAFT = true
EXTERNAL_JUDGE = false
```

The runner source supports `case_ids`, validates them against the selected split, writes the chosen IDs to the manifest, and permits stage tracing for draft `novel_dev` QA. `qa` has generation and runtime verification but no external judge. Use one new run ID and one attempt per selected case. The case IDs, purpose, success/failure criteria, and resume policy in this document are fixed before any new outcome is seen. Do not create a subset Gold file, alter `novel_dev.yaml`, create a second runner, or add/remove cases after viewing outcomes.

Before the run, compare the prospective manifest with the two historical G4 manifests and the expected product lineage: repository/product source, source manifest, normalized corpus and output identities, index fingerprint/payload, dataset and Gold identity, prompt fingerprint/version, generation and embedding model IDs/dimensions, retrieval policy, and query-expansion identity. A design-only HEAD change is expected; a changed corpus/index/dataset/product identity or unexplained prompt/model/policy difference stops before scientific calls. Confirm the proposed run ID is unused. This preflight is an identity comparison, not authorization to create a frozen release candidate.

## 7. Layer B observations and per-case gates

For every selected case save the actual channel rankings, authoritative RRF order/scores, `rerank_pool_entries` including surviving ordinary and frontier IDs, final and cited evidence, answer status, coverage receipt, and missing canonical points/relations. The actual offered pool is the primary R2 observation; a QA answer alone is not causal evidence.

For **n024**, compare the historical critical header's saved channel/rank geometry to the new geometry. Under sufficiently comparable rankings, report current legacy top-30 membership, current corrected offer, exchange reason, and any loss of the qualifying rank witness. Classify the analytic-helix information need as `ANSWERED_COMPLETE`, `ANSWERED_INCOMPLETE`, `INSUFFICIENT_EVIDENCE`, or `ERROR`; record whether critical evidence reaches final, citation, and answer. If upstream rankings materially drift, set `N024_PAIRED_MECHANISTIC_COMPARISON = INCONCLUSIVE_DUE_TO_RANKING_DRIFT`. Layer A remains the exact-state mechanism authority.

For **n002/n017**, compare the historical evidence's new qualifying ranks, current offer/reason, and final/cited membership and runtime completeness. A newly absent offer under comparable upstream ranking is `R2_BENEFIT_PRESERVATION_REGRESSION`. If the relevant evidence disappears or its rank geometry materially changes before R2, the paired R2 comparison is `INCONCLUSIVE_DUE_TO_RANKING_DRIFT`; a changed answer alone is not an R2 regression. Do not require all three live answers to have a predetermined status.

## 8. Nondeterminism, retry, and provenance

Provider variation can change decomposition, dense/sparse rankings, reranker order, generation, and verification even with stable model IDs. A better live n024 answer without comparable candidate geometry does not prove the established collateral mechanism fixed; a worse answer caused downstream or before R2 does not alone refute the pool correction. Preserve both the exact-state Layer A result and the live result without selecting the more favorable attempt.

```text
SUPPORTED_INFRASTRUCTURE_RESUME = SAME_RUN_ONLY
NONRETRYABLE_PRODUCT_ERROR_RERUN = false
POST_OUTCOME_CASE_PRUNING = false
```

The existing run store treats completed QA cases and terminal nonretryable exceptions as completed; supported resume skips them and can retry only pending/retryable cases. Use same-run resume only for clearly retryable infrastructure/provider interruptions such as 429, 502, 503, 504, or transport loss. Inspect recorded exception classification before resuming. Do not rerun completed cases, launch an ad-hoc replacement run for a product exception, or compose a best-of mixture. A nonretryable product error leaves the affected targeted question `INCOMPLETE / PRODUCT ERROR`.

## 9. Result classification and lifecycle

| Scoped decision | Exact condition |
|---|---|
| `PASS / CORRECTION EXPOSED VERIFICATION SUPPORTED` | Layer A passes; all three Layer B cases complete; their live upstream states permit the stated R2 comparisons; no comparable-state n024 collateral loss or n002/n017 opportunity regression occurs. Mixed QA statuses may be reported if their ownership is demonstrably upstream, downstream, or provider-variable. |
| `FAIL / N024 COLLATERAL MECHANISM PERSISTS` | Exact historical saved state, or a sufficiently comparable live state after Layer A PASS, permits the established illegal n024 witness loss. If found in Layer A, do not run Layer B. |
| `FAIL / R2 BENEFIT PRESERVATION REGRESSION` | Exact replay or a comparable live state newly loses qualifying n002/n017 opportunity. |
| `FAIL / RANK-WITNESS CONTRACT CONTRADICTION` | An exact saved replay demonstrates an accepted exchange that violates the approved componentwise/charged-role contract, including any n006 guard-related contradiction. Do not run Layer B. |
| `INCONCLUSIVE / SAVED INPUT NOT_REPRODUCIBLE` | A needed Layer A payload/provenance/ordering field cannot be reconstructed exactly. Stop before Layer B. |
| `INCONCLUSIVE / N006 NEW GUARD BOUNDARY` | n006 is newly guard-blocked without a proven contract violation; the predefined acceptable quota-bound residual condition is not met. Stop before Layer B and review that distinct boundary. |
| `INCONCLUSIVE / LIVE RANKING DRIFT` | Layer A passes but a material upstream difference prevents a needed paired live R2 comparison. Report QA separately. |
| `INCOMPLETE / PRODUCT ERROR` | A selected live case ends with a nonretryable product exception, preventing its acceptance question from being observed. |

Preserve the generic three-case runner's own status and quality-gate verdict, including any `COMPLETE / FAIL`; do not relabel that as a full `novel_dev` gate or development-quality pass. The separate G4 correction verdict assesses only this mechanistic scope. Layer A failure or inconclusive exact replay blocks Layer B under this design. A live product error or needed ranking-drift comparison prevents G4 closeout even when Layer A passes.

If the scoped verification passes, G4 may close at the **exposed development** level as `DETERMINISTIC CORRECTION VERIFIED / EXPOSED CORRECTION MECHANISM VERIFIED / FRESH GENERALIZATION BENEFIT NOT_ESTABLISHED`. That permits entry to `G5 — Integrated Candidate` for Phase-G development integration (`G5_ENTRY_AFTER_SCOPED_G4_PASS = true`), not release validation. A failed, inconclusive, or incomplete correction mechanism keeps G5 blocked. G3 `NO_CHANGE` and fresh Lane B `OPTIONAL / DEFERRED` remain. No result here can establish novel_validation success, release readiness, or fresh generalization.

## 10. Scientific and protected boundaries

```text
DESIGN_QA_RUNS = 0
DESIGN_RETRIEVAL_RUNS = 0
DESIGN_SCIENTIFIC_CALLS = 0
DESIGN_SCIENTIFIC_TOKENS = 0
DESIGN_EXTERNAL_JUDGE_CALLS = 0
FUTURE_LAYER_A_SCIENTIFIC_CALLS = 0
FUTURE_LAYER_B_SELECTED_QA_CASES = 3

NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0

PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
```

The future run may make model calls for three QA cases only after its zero-call prerequisite and identity preflight pass. No token estimate is inferred from prior averages. Any budget guardrail must use the runner's supported limits and be stated as a safety cap, not a performance target.

## 11. Execution handoff

1. Verify product lineage and historical store integrity without changing the old artifacts. Establish exact Layer A input reproducibility for each case; emit explicit missing-field evidence if it fails.
2. If exact, run one read-only replay analyzer against the corrected in-memory pool constructor. Save per-case memberships, exchange witnesses, and a machine-readable result. Stop on `FAIL` or `NOT_REPRODUCIBLE`.
3. Only after Layer A `PASS`, perform the identity preflight and one supported three-case QA run. Use supported same-run infrastructure resume only.
4. Review actual pool receipts and ranking comparability before attributing answer changes. Preserve runner verdicts and raw records. Write the scoped result to `G4_R2_POST_CORRECTION_EXPOSED_VERIFICATION.md` and `G4_R2_POST_CORRECTION_EXPOSED_VERIFICATION_RESULT.json`; an optional `g4_r2_post_correction_exposed_replay.py` may support the read-only replay. Raw live records remain in the ignored run store.
5. Apply the classification table and update status only from observed evidence. Do not initiate G5 or protected evaluation as part of this execution.

```text
NEXT_TASK_RECOMMENDATION = G4 POST-CORRECTION EXPOSED VERIFICATION EXECUTION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
