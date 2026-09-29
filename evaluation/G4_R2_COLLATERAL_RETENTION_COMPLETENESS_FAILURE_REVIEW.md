# G4 R2 Collateral Retention / Completeness Failure Review

## 1. Decision and scope

```text
G4_R2_COLLATERAL_RETENTION_REVIEW = PASS / GENERIC CORRECTION DESIGN READY
N024_R2_COLLATERAL_DISPLACEMENT = CONFIRMED
N006_RESIDUAL_R2_LOSS = CONFIRMED
R2_REPAIR_BENEFIT_OBSERVED = true
R2_COLLATERAL_REGRESSION_OBSERVED = true
FRONTIER_UNIVERSALITY = 28/28 selected exposed cases; 295 entries; 4/10/14 min/median/max
CURRENT_FORMAL_DESIGN_VIOLATED = false
CURRENT_DESIGN_INCOMPLETE = true
FAILED_INVARIANT = Frontier quantity is bounded, but replacing an ordinary RRF incumbent requires no preservation of its legitimate policy-role channel support and no improvement over that incumbent's retained opportunity.
SELECTED_CORRECTION_ARCHITECTURE = BOUNDED_POLICY_ROLE_CHALLENGER_EXCHANGE_WITH_RANK_WITNESS_RETENTION
FRONTIER_CAPACITY_SEMANTICS = Upper bound on successful admissions; never guaranteed allocation; rejected offers consume no admission quota.
RRF_RETENTION_INVARIANT = Every exchange preserves or improves every component of the current pool's bounded rank-witness vector for every active role and legitimate channel.
CHALLENGER_ADMISSION_INVARIANT = A valid omitted challenger must improve at least one rank-witness component for its charged role without worsening any role/channel component, by replacing one specifically identified ordinary incumbent.
STRUCTURED_SUPPLEMENT_PRECEDENCE = unchanged
POOL_LIMIT = 30
R3_CHANGE_REQUIRED = false
PROMPT_CHANGE_REQUIRED = false
SCHEMA_CHANGE_REQUIRED = false
PRODUCT_VERIFICATION = FAIL / ESTABLISHED EXPOSED SAFETY REGRESSION; CORRECTION NOT_IMPLEMENTED
FRESH_GENERALIZATION_BENEFIT = NOT_ESTABLISHED
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

This separately authorized task reviews saved exposed evidence and specifies a future deterministic correction. It changes no product source, tests, prompts, config, dataset, Gold, calibration, or public schemas. It implements and executes no proposed pool policy. The review PASS applies to the causal analysis and implementation-ready contract, not to the current product or unrun future gates.

At entry, `git rev-parse HEAD`, `git status --short`, and `git log -8 --oneline` confirmed starting HEAD `9caf7314e0fd908a71cb93520d482002756e1d4c` (`Update G4 regression after authorized target rerun`) and a clean worktree. Current product-behavior lineage remains `a22c8f70eeebe4a53490e11a4b6852561ca8afa6`. The review commit advances repository history only; resolve its exact SHA from Git history/delivery, rather than making the document self-referential.

Authorities inspected:

- [Accepted R2 repair design](G4_R2_FUSION_EVIDENCE_RETENTION_REPAIR_DESIGN.md), [implementation result](G4_R2_EVIDENCE_RETENTION_IMPLEMENTATION_RESULT.md), and [normal-product integration correction](G4_R2_NORMAL_PRODUCT_POOL_INTEGRATION_CORRECTION.md).
- [Initial regression](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION.md) and [result](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RESULT.json); [authorized target rerun](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RERUN.md) and [composite result](G4_EXPOSED_NOVEL_DEV_POST_REPAIR_REGRESSION_RERUN_RESULT.json).
- [Exposed false-insufficiency diagnostic](G4_EXPOSED_DEVELOPMENT_FALSE_INSUFFICIENCY_DIAGNOSTIC.md) and [result](G4_EXPOSED_DEVELOPMENT_FALSE_INSUFFICIENCY_RESULT.json).
- Relevant methods of [retrieval.py](../src/panda_agent/retrieval.py), the [existing R2 controls](../tests/unit/test_g4_r2_evidence_retention.py), [current status](../docs/EVALUATION_STATUS.md), and [roadmap](../docs/GENERALIZATION_ROADMAP.md).

The optional [analysis JSON](G4_R2_COLLATERAL_RETENTION_ANALYSIS.json) and [stdlib-only analyzer](g4_r2_collateral_retention_analysis.py) retain per-case structural metadata and all 295 displaced candidate-case occurrences. They characterize the existing policy, not a new policy's outcomes. No threshold search or semantic rescoring occurred.

## 2. Current product behavior

`Retriever.retrieve()` collects channel streams and stable weighted RRF ordering, discovers structured eligibility against the legacy top-30, then calls the shared `_r2_rerank_pool()`. `consolidate_and_select_candidates()` merges consistent payloads, retains occurrences and best channel ranks across passes, and calls the same constructor. Repeated passes do not create independent channels or extra RRF terms. Normal single-pass score ties retain insertion order; global ties use canonical object ID. The correction must preserve each caller's existing ordinary order.

Relevant source anchors at the starting lineage are `_source_type_of` (line 665), `_workflow` (1614), `_graph` (1646), normal pool call (1937), `_channel_pass_occurrences` (2134), `_r2_rerank_pool` (2152), and the global pool call (2421).

Current constructor:

1. Reserve first 30 unique eligible supplements; exclude them from ordinary membership. Let `B = 30 - supplement_count` and let the first `B` ordinary RRF IDs be the legacy base.
2. Activate roles with positive plan source budgets or required source types. Derive raw role ceiling `q_r = max(1, ceil(final_evidence_limit * budget_r))` for positive budgets, otherwise one for a required-only role. Clip to eligible omitted-candidate count for the current role limit.
3. Accept omitted candidates only with usable payload, source/version/locator, permitted target/context source, and a qualifying normal occurrence. Payload source role supplies membership; normal workflow/graph occurrence can additionally supply that specialized role. Paper may qualify through ordinary channels without a dedicated paper retrieval.
4. Sort each role queue by `(best qualifying channel rank, -RRF score, object_id)`. Visit required roles first, then decreasing budget and role name. Round-robin selects until clipped capacity, exhaustion, or duplicate exhaustion.
5. `F_cap = min(sum(role_limits), max(0, floor((B - 1)/2)))`. Take the first `B - F_selected` ordinary IDs, then frontier, then supplements.

All observed selected pools have 30 unique IDs and zero supplements. Each has a strict RRF majority. The implementation faithfully follows the accepted design's selection/truncation formulas.

| Signal | Current use | Protects the displaced incumbent? |
|---|---|---|
| RRF rank / score | Orders the backbone; score breaks frontier channel-rank ties | Only through surviving the shortened prefix |
| Number of agreeing channels | Contributes indirectly to RRF score | No independent guard |
| Cross-channel ranks / consensus | Occurrences determine challenger eligibility and minimum rank | No incumbent-versus-challenger comparison |
| Distance from old pool boundary | Determines which suffix is dropped after selection | No relative competitiveness test |
| Payload source role / specialized role | Chooses challenger queues and limits | No preservation of displaced role coverage |
| Strict majority | Bounds replacement quantity | No bound on lost witness quality |

Final ordering can subsequently include full fused IDs as fallback. The established failure is loss of semantic rerank opportunity, with observed final/cited absence; it is not a claim that every excluded ID is mathematically barred from all final-selection paths. R3, admission, verifier, and finalization retain their existing authorities.

## 3. Established benefit observations

| Case | Established saved observation | Interpretation |
|---|---|---|
| n002 | Authorized replacement changes old insufficient_evidence to answered-complete; previously omitted requirements evidence enters frontier and reaches final/cited evidence | Repair-consistent exposed recovery |
| n017 | Previously omitted `PndTrack` header, dense rank 7, enters frontier and final/cited evidence; production coverage is complete; old insufficient_evidence becomes answered-complete | Strong repair-consistent exposed recovery |

These establish observable useful behavior. Changed model outputs remain provider-nondeterministic comparisons; neither case estimates the isolated deterministic QA effect of R2. The correction must preserve the generic opportunity for strong legitimate single-channel evidence omitted by consensus-heavy fusion. Old answers and reranker ranks are diagnostic evidence only, never runtime inputs.

## 4. Established collateral failure: n024

`object.d6ef560b88c3926ecb32d3e1`, `tracking/PndHelixPropagator/PndHelixPropagator.h`, is the critical analytic-helix witness. All old/new channel rankings are identical. Its ranks are dense 8 and sparse 19; both are regular legitimate channels. Old and new weighted RRF rank are 18 and score is `0.027364110201042444`.

Old: legacy pool inclusion -> semantic reranker rank 2 -> final evidence -> citation. Current: 16 ordinary + 14 frontier -> object excluded before reranker -> absent final evidence -> analytic-helix answer incomplete. The earliest established divergence is R2 pool construction. Provider variability downstream cannot explain an already missing model input.

Current active ceilings/limits, in visit order, are code 5, paper 4, graph 2, documentation 2, workflow 1. All are available; capacity 14 is fully selected. Payload roles of the 14 frontier objects are seven code, four paper, two documentation, one workflow. The seven code payloads include six graph-only occurrences and one sparse occurrence; no dense-code frontier challenger is selected. Graph-derived code can charge either code or graph, but canonical IDs still occupy one slot each. This is legitimate eligibility under the accepted contract, not evidence of fallback privilege or duplicate slots.

The source-level failure distinctions are:

- **Capacity:** 14 meets the formal majority bound. A smaller arbitrary cap would merely move the truncation boundary.
- **Eligibility:** The admitted challengers are permitted by the observed role/provenance contract. This witness does not establish an eligibility bug.
- **Ordering:** RRF rank 18 is unchanged. Rank/score still order the backbone correctly; its length changes.
- **Replacement and retention:** Every selected challenger implicitly sacrifices one suffix incumbent, without comparing retained channel support. This is the confirmed missing contract.

For an architecture-level check only, the saved legacy base contains two code/dense witnesses at ranks `[5, 8]` and two code/sparse witnesses at `[19, 20]`. The target's code/channel ordinals are 2 and 1, within the already-derived code ceiling 5. Removing it without an equal-or-better replacement in these same role/channel positions degrades retained opportunities. No new cap or rank threshold was searched, and no proposed policy was replayed. These observed ordinals illustrate the selected invariant; the exchange formulas below contain no case, object, path, or exposed rank literals.

## 5. n006 residual R2 loss

The saved omitted constructor `object.2914485ff398f61e994c46d6` is code, legitimately recalled at dense rank 9. It remains absent from the actual offered pool and final evidence. This is the original residual evidence-retention loss; critical `p2` suffix literals are absent even though production V1/G2 accepts completeness. The latter is a separate secondary false-acceptance concern.

Metadata reconstruction places the constructor at code queue position 11, not position 9. The queue merges normal graph-derived code and dense code by their minimum qualifying channel rank. Its prefix is:

| Queue position | Channel/rank | Selected? | Charged role |
|---|---|---|---|
| 1 | graph 1 | yes | code |
| 2 | dense 2 | yes | code |
| 3 | graph 2 | yes | graph |
| 4 | graph 3 | yes | graph |
| 5 | graph 4 | yes | code |
| 6 | dense 5 | yes | code |
| 7 | graph 5 | yes | graph |
| 8 | graph 6 | no | — |
| 9 | graph 7 | no | — |
| 10 | graph 8 | no | — |
| 11 | dense 9 constructor | no | — |

Code budget 0.30 gives ceiling 4; four successful code selections exhaust it before this target. Graph's ceiling 3 is also used. The selected frontier is 13, below the global majority maximum 14. Workflow/readme contribute four/two; paper has no eligible omitted rows in the conditional model.

| Suspected cause | Finding |
|---|---|
| Role eligibility / payload classification | Eligible code candidate; not excluded by classification |
| Role queue capacity | Code's four-admission ceiling is exhausted |
| Duplicate competition | Distinct code/graph objects compete in overlapping role queues; repeated identity is deduplicated correctly |
| Global frontier saturation | No: 13 < 14 |
| Ordering | Heterogeneous graph/dense ranks move the dense candidate behind earlier role competitors |

Graph origin is normal because graph is not required and that branch does not emit generic fallback. Workflow origin remains unobserved in the saved sidecar-free trace. The conservative conditional reconstruction matches the actual frontier sequence, including the code/graph attribution above; this match is not proof that every saved workflow row's full payload/origin is observable.

The selected correction removes guaranteed displacement, not the heterogeneous queue or its ceiling. Rejected earlier offers may allow a later dense candidate to be examined; earlier successful admissions may still exhaust its role. Thus it **does not guarantee natural recovery of this exact residual**. Role-queue competition is a separate residual R2 surface. No extra code slots, dense-specific priority, or target quota is justified by this case. CR-3 must test both later feasible opportunity after rejections and a truthful remaining capacity-bound omission.

## 6. Non-R2 regression separation

| Taxonomy | Case/observation | Bounded ownership |
|---|---|---|
| `R2_COLLATERAL_DISPLACEMENT` | n024 | High-confidence pool displacement; paired identical rankings |
| `R2_RESIDUAL_TARGET_LOSS` | n006 | Original constructor opportunity remains lost |
| `V1_G2_COMPLETENESS_FALSE_ACCEPTANCE` | n006 secondary | Production completeness accepts an answer missing independently required suffix literals; separate from pool loss |
| `V1_G2_COMPLETENESS_FALSE_ACCEPTANCE` | n018 concern | Runtime coverage 1.0 despite absent critical null checking / complete tree preparation; generic owner remains unresolved |
| `V1_G2_COMPLETENESS_REJECTION` | n007 | Qualified identifier validation blocks completeness although relevant source is present; no established R2 loss |
| `V1_G2_COMPLETENESS_REJECTION` | n028 | `LOCAL_INVALID / INVALID_SUPPORTER`; macro/header available; possible false rejection remains unresolved |
| `V1_G2_COMPLETENESS_REJECTION` | n031 | `LOCAL_INVALID / BAD_QUOTE`; source is present; this does not establish a verifier defect |
| `ANSWERABILITY_UNRESOLVED` | n014 | Explicit repository scope versus historical thesis answer; independent answerability unresolved |
| `PROVIDER_NONDETERMINISM` | Old/new QA and n002/n018 replacement observations | Model-generated plans/answers/reviews vary; output transitions are not isolated deterministic effects |
| `D1_SCHEMA_VARIABILITY` | Original n002/n018 failed attempts | Nonretryable D1 ambiguity-validation exceptions; later successful replacement does not erase failures or establish a schema repair |
| `NOT_R2` | n001 | Q1 observation plus Gold/source shell discrepancy; no R2 repair mandate |
| Unresolved, not credited to R2 | n010, n019 | Prior Q1/R1 and R2/Q2 ownership uncertainty respectively; improvement alone is not causal assignment |

The six worsened saved production-complete sentinels are n007, n014, n018, n024, n028, n031. They are not six proven R2 regressions. n018's relevant documentation is already final evidence; a pool patch is not established as its generic repair. G3 admission `NO_CHANGE` remains binding.

## 7. Frontier activation breadth

### Reproducibility and observation limits

Selection authority is the committed rerun composite: 26 original records plus n002/n018 replacements. Only these three exposed run stores are read:

```text
g3-evidence-admission-audit-novel-dev-v1
g4-r2-post-repair-novel-dev-regression-v1
g4-r2-post-repair-n002-n018-rerun-v1
```

The analyzer reads their records/traces and source-manifest IDs for context-source membership. It recomputes current normal single-pass RRF ordering from saved channel metadata and verifies each legacy top-30 and score against saved fused receipts. It verifies the actual backbone is exactly the shortened legacy prefix. It performs no retrieval, model generation, source-content rescoring, protected dataset read, or new-policy simulation.

Public saved candidate traces omit full text/title and aligned specialized-origin sidecars. Therefore exact original `valid_challenger` payload checks cannot be independently repeated in full. Eligible counts below are explicitly **conditional on usable channel payloads**. Source/version/locator metadata are available. Specialized normal origin is inferred only when the current branch cannot fall back, when row source/type cannot match its fallback query, or when a specialized-only accepted frontier receipt plus uniform branch provenance necessarily implies normal origin. Other rows remain `UNKNOWN`, rather than being guessed normal. Conservative lower and permissive upper metadata models are both retained in JSON.

Unknown-specialized-origin cases are n006, n019, n020, n022, n028, n031. Conditional lower reconstruction matches actual ordered frontier in 28/28; upper matches in 25/28. This concordance is useful characterization, not recovered sidecar evidence. Actual selected counts, backbone sizes, role budgets, and suffix displacement are directly observable regardless of those bounds.

### Per-case structural accounting

Role abbreviations: C=code, D=documentation, R=readme, P=paper, W=workflow, G=graph. Vectors use the listed role visitation order. `q` is the raw policy ceiling; `N` is conditional-lower eligible omitted count; `L=min(q,N)` is clipped role limit. Full lower/upper vectors and origins are in the machine artifact. Roles can overlap, so summing `N` does not count distinct candidates.

| Case | Active roles | q | N | L | sum L | F cap | Selected F | Backbone | F/30 |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| n001 | D,R,C,G,P | 6/3/2/1/1 | 13/1/20/20/0 | 6/1/2/1/0 | 10 | 10 | 10 | 20 | 33.3% |
| n002 | C,D,G,R,P | 7/3/2/2/1 | 6/21/1/0/0 | 6/3/1/0/0 | 10 | 10 | 9 | 21 | 30.0% |
| n003 | D,C,R,W,P | 4/3/3/2/1 | 11/12/1/0/7 | 4/3/1/0/1 | 9 | 9 | 9 | 21 | 30.0% |
| n004 | D,C,R,W,P | 4/3/3/2/1 | 18/2/1/3/0 | 4/2/1/2/0 | 9 | 9 | 9 | 21 | 30.0% |
| n005 | D,C,R,W,P | 4/3/3/2/1 | 25/8/2/13/1 | 4/3/2/2/1 | 12 | 12 | 12 | 18 | 40.0% |
| n006 | W,C,G,R,P | 5/4/3/2/1 | 4/20/17/3/0 | 4/4/3/2/0 | 13 | 13 | 13 | 17 | 43.3% |
| n007 | D,C,R,W,P | 4/3/3/2/1 | 4/51/0/13/0 | 4/3/0/2/0 | 9 | 9 | 9 | 21 | 30.0% |
| n008 | P,C,D,G,W | 7/2/2/2/2 | 13/15/0/5/18 | 7/2/0/2/2 | 13 | 13 | 13 | 17 | 43.3% |
| n009 | P,C,D,G,W | 7/2/2/2/2 | 40/0/0/0/20 | 7/0/0/0/2 | 9 | 9 | 9 | 21 | 30.0% |
| n010 | C,G,W,D,R | 5/4/2/2/2 | 19/6/5/13/0 | 5/4/2/2/0 | 13 | 13 | 13 | 17 | 43.3% |
| n014 | C,G,W,D,R | 5/4/2/2/2 | 38/19/14/3/2 | 5/4/2/2/2 | 15 | 14 | 14 | 16 | 46.7% |
| n015 | C,D,R,W,G | 4/4/3/2/1 | 8/22/0/12/5 | 4/4/0/2/1 | 11 | 11 | 11 | 19 | 36.7% |
| n016 | D,R,C,G,P | 6/3/2/1/1 | 26/0/0/0/0 | 6/0/0/0/0 | 6 | 6 | 6 | 24 | 20.0% |
| n017 | C,D,G,R,P | 7/3/2/2/1 | 32/11/20/0/4 | 7/3/2/0/1 | 13 | 13 | 13 | 17 | 43.3% |
| n018 | D,C,R,W,P | 4/3/3/2/1 | 19/6/0/7/3 | 4/3/0/2/1 | 10 | 10 | 10 | 20 | 33.3% |
| n019 | W,C,G,R,P | 5/4/3/2/1 | 0/20/0/0/1 | 0/4/0/0/1 | 5 | 5 | 5 | 25 | 16.7% |
| n020 | W,C,G,R,P | 5/4/3/2/1 | 0/24/20/3/8 | 0/4/3/2/1 | 10 | 10 | 10 | 20 | 33.3% |
| n021 | C,D,G,R,P | 7/3/2/2/1 | 10/4/4/3/16 | 7/3/2/2/1 | 15 | 14 | 14 | 16 | 46.7% |
| n022 | W,C,G,R,P | 5/4/3/2/1 | 0/13/6/1/7 | 0/4/3/1/1 | 9 | 9 | 9 | 21 | 30.0% |
| n023 | C,G,W,D,R | 5/4/2/2/2 | 43/20/11/11/1 | 5/4/2/2/1 | 14 | 14 | 14 | 16 | 46.7% |
| n024 | C,P,G,D,W | 5/4/2/2/1 | 23/14/15/4/12 | 5/4/2/2/1 | 14 | 14 | 14 | 16 | 46.7% |
| n025 | C,P,G,D,W | 5/4/2/2/1 | 37/6/20/0/15 | 5/4/2/0/1 | 12 | 12 | 12 | 18 | 40.0% |
| n026 | D,C,R,W,P | 4/3/3/2/1 | 15/8/0/10/0 | 4/3/0/2/0 | 9 | 9 | 9 | 21 | 30.0% |
| n027 | D,R,C,G,P | 6/3/2/1/1 | 15/0/6/6/0 | 6/0/2/1/0 | 9 | 9 | 9 | 21 | 30.0% |
| n028 | W,C,G,R,P | 5/4/3/2/1 | 0/16/4/0/2 | 0/4/3/0/1 | 8 | 8 | 7 | 23 | 23.3% |
| n029 | C,P,G,D,W | 5/4/2/2/1 | 17/4/12/6/12 | 5/4/2/2/1 | 14 | 14 | 14 | 16 | 46.7% |
| n030 | P,C,D,G,W | 7/2/2/2/2 | 16/3/4/2/11 | 7/2/2/2/2 | 15 | 14 | 14 | 16 | 46.7% |
| n031 | C,G,W,D,R | 5/4/2/2/2 | 0/0/0/6/2 | 0/0/0/2/2 | 4 | 4 | 4 | 26 | 13.3% |

### Distribution and architectural interpretation

| Quantity | Min | Median | Max |
|---|---:|---:|---:|
| Active role count | 5 | 5 | 5 |
| Sum clipped limits, conditional lower | 4 | 10 | 15 |
| Frontier capacity, conditional lower | 4 | 10 | 14 |
| Actual selected frontier | 4 | 10 | 14 |
| Ordinary backbone | 16 | 20 | 26 |
| Frontier fraction | 13.33% | 33.33% | 46.67% |

Selected frontier frequency: `4:1, 5:1, 6:1, 7:1, 9:8, 10:3, 11:1, 12:2, 13:4, 14:6`. Backbone frequencies follow exactly from `30 - F`. Full ceiling/limit/capacity frequencies are retained in JSON.

Six of 28 cases (21.43%) saturate the majority bound at **14 frontier / 16 RRF**: n014, n021, n023, n024, n029, n030. The cap equals 14 in these same cases. 26/28 fill their conditional computed frontier capacity; n002 (9/10) and n028 (7/8) stop after overlapping role queues exhaust distinct IDs. These are duplicate-exhaustion exceptions, not a competitiveness check.

Universal activation is mechanical for the observed plans: every plan has five positive/required roles; every case has at least one nonempty eligible omitted queue, and large channel unions outside top-30; small positive/required roles get a minimum-one ceiling; round-robin selection has no benefit/retention predicate. Normal specialized results can belong to both payload and specialized roles. Positive budgets alone do not logically guarantee activation on every possible query, but here their nonempty outside-base queues trigger it in every case. The code does not inspect whether the old base already adequately represents that role/channel before replacing a suffix.

This satisfies the accepted formulas. The design calls ceilings "never reserved slots", yet its explicit selection formula fills capacity whenever enough distinct omitted candidates exist. It implements bounded opportunity as actual allocated pool membership conditional only on eligibility/queue competition. Thus **formal compliance is true, while the qualitative retention intent is underspecified**. Common activation alone is not a failure; common unconditional displacement plus the confirmed collateral witness establishes the missing exchange criterion.

## 8. Legacy RRF displacement analysis

There are **295 displaced candidate-case occurrences**, exactly one legacy-base omission per selected frontier entry. These are not 295 distinct corpus objects. No supplement caused these omissions. JSON lists every displaced ID, old-base rank, score, channels/ranks, source role, locator, and historical final/cited flags.

| Property | Observed distribution |
|---|---|
| Displaced RRF rank | min 17, median 25, max 30 |
| Rank frequencies | 17:6, 18:10, 19:12, 20:13, 21:16, 22:24, 23:24, 24:25, 25:26, 26:27, 27:28, 28:28, 29:28, 30:28 |
| Displaced RRF score | min 0.013888888888888888, median 0.019047619047619046, max 0.03125 |
| Raw distinct channels | one:269; two:26 |
| Known qualifying distinct channels | zero:5; one:264; two:26; zero-known rows have unobserved specialized origins, not proven zero legitimate support |
| Channel occurrence counts | exact 84, workflow 137, sparse 49, dense 46, paper 4, graph 1; multi-channel rows contribute to multiple counts |
| Payload source roles | code 84, documentation 33, workflow 139, paper 34, readme 5 |
| Actual frontier payload roles | code 136, documentation 69, paper 42, workflow 31, readme 17 |
| Historical G3 final / cited overlap | 8 / 8 candidate-case occurrences |
| Full channel rankings identical to G3 | 20/28 cases |
| Historical cited overlap among identical-ranking cases | 5 occurrences |

The eight historical overlaps are listed for audit, not labelled eight causal harms:

| Case | Object | Legacy rank | Channels/ranks | Same rankings? |
|---|---|---:|---|---|
| n001 | object.e363543e4fd82b6ccc0b1b4a | 30 | sparse 1 | no |
| n003 | object.af3da13dbbe391b8999697ec | 26 | dense 4 | no |
| n009 | object.4aa016da5e65b7a8dcfbce38 | 29 | paper 27, sparse 6 | yes |
| n014 | object.432011cd3810787037f8b091 | 23 | graph 9, sparse 13 | yes |
| n021 | object.015d183a412eb1fab6948b24 | 17 | exact 12 | yes |
| n022 | object.6a72bf9df87e9a5810015881 | 25 | dense 14, sparse 13 | no |
| n024 | object.d6ef560b88c3926ecb32d3e1 | 18 | dense 8, sparse 19 | yes |
| n030 | object.25772a34446d53e2e1720b10 | 17 | dense 18, sparse 8 | yes |

Changed rankings make n001/n003/n022 unpaired comparisons. Even identical rankings plus historical citation do not independently prove critical relevance or answer degradation in the other four same-ranking overlaps. Only the established n024 causal chain supplies that authority here. No manual full-text semantic review of all displaced objects was performed.

## 9. Failed invariant

**The current policy bounds frontier quantity but allows replacing an ordinary RRF incumbent without preserving its legitimate role/channel support or establishing a better retained opportunity.**

Quantity and eligibility checks are functioning. The missing invariant is about a **specific exchange**, rather than a smaller frontier count. Increasing the pool, changing final capacity, lowering an exposed cap, or adjusting downstream verification would not repair that contract at its origin.

The strict-majority rule remains a binding coarse safety bound, necessary under the existing contract and insufficient for witness retention. Rank-witness preservation below adds the missing constraint. It does not infer semantic relevance from RRF alone.

## 10. Candidate repair architectures

| Family | Assessment | Decision |
|---|---|---|
| A. Blanket multi-channel protection | Distinct legitimate channels provide useful support, but `>=2` alone counts weak duplication as strong. Existing R2-A deliberately has 30 exact+sparse incumbents and an omitted dense candidate; blanket protection blocks the original recovery. Repeated passes and generic specialized fallbacks must not manufacture agreement. | Reject blanket rule; retain support **rank and role** information instead |
| B. Competitive RRF / tail guard | Weakest-first displacement is deterministic and avoids arbitrary protected prefixes. However challenger score >= incumbent score reduces to the old fusion cutoff: challengers are outside the ordered base and generally have lower score. Rank-gap/score-gap cutoffs would require new justification or tuning. | Use ordinary RRF only to choose the weakest **legal** victim; no scalar admission threshold |
| C. Explicit challenger-incumbent exchange | Makes each loss accountable. A rank-witness comparison can use existing plan/provenance without another model. A vague "role necessity" or minimum rank across heterogeneous channels alone is insufficient. | Select with the precise componentwise retention condition below |
| D. Capacity as upper bound | Preserves bounded opportunity while allowing rejection when every victim loses competitive support. This fits the existing ceiling language more closely; total eligible rows need not imply allocated slots. | Select; quotas bound successful admissions, not guaranteed slots |
| E. Simpler alternatives | Removing frontier/pure RRF reintroduces the established loss. Larger pools change model cost and leave another cutoff. Static per-channel reservations ignore roles/fallbacks. A static union of protected witnesses is possible, but cannot permit an equal-or-better substitute for a protected ID. | Prefer a small dynamic rank-vector exchange over frozen ID reservations; no learned policy or framework |

Architecture-level justification is symmetric: if the plan permits up to `q_r` challenger opportunities for a role, introducing those opportunities must not erase equally bounded existing opportunities in any legitimate channel for that role. Use the **same existing ceiling**, rather than inventing a new protected rank/count. Comparing each channel separately prevents a new graph opportunity from compensating numerically for losing dense/sparse support. Componentwise comparison prevents a better top rank from hiding a degraded lower witness. The rule is specified independently of exposed outcomes and is not chosen by optimizing a 28-case replay.

## 11. Selected correction contract

### Definitions and retained inputs

Name: `BOUNDED_POLICY_ROLE_CHALLENGER_EXCHANGE_WITH_RANK_WITNESS_RETENTION`.

Retain existing supplements, target/context/version checks, payload consistency, active roles, raw ceilings `q_r`, clipped admission limits, role order, queue order, RRF scores/weights, channel limits, and pool limit. The existing final-evidence limit is read for the already-established role-ceiling derivation; it is not changed. Do not invoke answer points, Gold, old reranker results, expected paths, or case identities.

For an object, role, and channel, let `rank(o,r,h)` be its best **qualifying** one-based occurrence rank in that channel, using the same role membership and usable-payload checks as frontier eligibility. Regular exact/dense/sparse/paper occurrences qualify under their existing contract; specialized workflow/graph occurrences qualify only with explicit normal origin. Missing/unknown runtime provenance and generic fallback do not qualify. Repeated passes of the same object/channel count once using the minimum qualifying rank; a fallback occurrence must not lower a normal occurrence's qualifying rank. Payload-role and specialized-role memberships may overlap without duplicate object slots.

For the current **non-supplement** pool `P`, define:

```text
W[r,h](P) = the q_r smallest finite rank(o,r,h) values,
            one per distinct object ID, sorted ascending,
            padded with infinity to length q_r.
```

Use the raw policy ceiling, not its clipping to omitted challengers: a role must retain witnesses even when it has no outside-base challengers. Only the existing legitimate channel types participate; no new whitelist of source roles or intent branches is introduced. No rank comparison crosses channel identity. Equal ranks from distinct objects supply distinct slots; object IDs determine deterministic ordering, not quality. Specialized generic fallback cannot add a vector component or create agreement. This "consensus" is preservation of supported opportunities across distinct retrieval mechanisms, not statistical independence and not raw occurrence counting.

### Exchange algorithm for a future implementation

1. Reserve supplements exactly as today. Start with the first `B` ordinary IDs as incumbent pool `P0`. No frontier slots are pre-reserved.
2. Build current eligible omitted-role queues and their admission ceilings as today. Preserve `F_cap` as the strict-majority upper bound. Count successful admissions per role; deduplicate successful IDs globally.
3. Visit roles in the existing deterministic round-robin order. For a role with unused successful-admission quota, examine its next unselected omitted candidate `c`. Advance its queue cursor whether admission succeeds or fails.
4. Consider each **remaining original ordinary incumbent** `v` in weakest-first order, by reverse position in the unchanged base RRF order. Previously admitted frontier candidates and supplements cannot be victims. Form `P' = P - {v} + {c}`.
5. An exchange is legal iff **every** component of **every** `W[r,h](P')` is <= its corresponding component of `W[r,h](P)`, and at least one component for the **charged role** is strictly smaller. Infinity behaves as missing opportunity. The challenger must retain its valid role/provenance eligibility. Pick the first legal victim, if any.
6. On success, replace that specific victim, append the challenger to ordered frontier admissions, and consume one successful-admission slot for the charged role/global cap. On rejection, consume no admission slot; leave the incumbent pool unchanged. Continue beyond rejected candidates. Do not terminate merely because an entire round had no admission while unvisited queue rows remain. Stop only at the successful global cap or exhaustion of all queues whose roles have unused quotas. Each role cursor advances monotonically, so traversal is finite without a retry framework.
7. Return surviving ordinary IDs in their unchanged RRF order, successful frontier IDs in admission order, and supplements in unchanged order, with truthful existing reason categories. The structured receipt's structured-only displacement fields remain structured-only; actual final pool IDs remain authoritative. No answer-facing schema or prompt change is needed.

No candidate gets an allocation solely because a role ceiling is nonzero. If no legal victim exists, fewer than maximum frontier slots are used and the ordinary incumbent remains offered. No successful candidate is charged twice for overlapping roles. A rejected object may occur in another finite role queue; it receives no duplicate membership or manufactured quota.

### What the invariant guarantees

- By induction over accepted exchanges, every rank-witness component is no worse than the original non-supplement base. An incumbent that supplies a competitive bounded witness cannot disappear without an equal-or-better same-role/channel replacement that preserves all other witnessed opportunities.
- Meaningful dense+sparse evidence cannot be removed just because novel graph capacity exists: losing either protected dense or sparse component vetoes that particular exchange. Multi-channel support adds multiple constraints without a new channel-count threshold.
- Strong omitted evidence can enter by improving an underrepresented legitimate role/channel while replacing a redundant or weaker incumbent outside the protected rank-witness envelope. Challenger RRF score need not exceed its victim, preserving the original single-channel recovery mechanism.
- In the existing consensus-heavy R2-A fixture, only the bounded best exact/sparse witnesses constrain exchanges; lower duplicate-rank tail objects remain possible victims. An initially missing dense opportunity can improve without sacrificing those best witnesses. The same construction supports the existing multiple-chunk and non-code synthetic controls; their actual future PASS remains unmeasured.
- Static benefit compatibility also follows from the saved bases: n002/n017 have four/six code-dense witnesses, below their existing code ceiling seven, and 21/19 workflow payload incumbents respectively (unique IDs, including ordinary-channel workflow payloads). Workflow is inactive in both plans, and those workflow payloads have no graph occurrence supplying an active specialized role. A strong omitted code-dense witness can improve a missing bounded position while exchanging one of these unconstrained incumbents. This establishes a feasible generic opportunity relative to the original base, not a simulated admission sequence or guaranteed final QA recovery after other exchanges.
- The pool stays unique and <=30. With nonzero frontier opportunity the ordinary base is full, and `F <= floor((B-1)/2)` ensures surviving ordinary count > frontier count. Supplement saturation still forces frontier zero. Supplements are protected by reservation precedence and are excluded from witness vectors to avoid inventing channel provenance or double charging.

### Limits and design acceptance

This is a deterministic **retrieval opportunity** invariant, not a semantic relevance proof or a guarantee to preserve every useful ID. A competitive witness may be exchanged for another object with equal-or-better channel ranks if some charged-role component also improves. Evidence below all `q_r` witness envelopes can still be displaced; the product lacks authoritative semantic knowledge before reranking. Multiple legitimate channels may be correlated. A pool fully covered by competitive rank witnesses can legitimately admit no challenger. Role/channel vectors may strongly constrain replacement; CR-2/CR-5 and existing recovery controls must guard against overprotection.

Using the established role ceiling as retained witness breadth is a new explicit retention contract, not a claim that it was already implemented, nor a new tuned constant. The bound is derived symmetrically from the same plan allocation that grants challenger privilege. No per-channel reserved allocation is created. No simulated exposed outcomes, threshold sweep, or case-specific acceptance counts justify this choice.

The observed n024 witness lies inside the existing code/dense and code/sparse envelopes, so unsupported removal fails this invariant structurally. This is a static contract check, not a prediction of all 28 new pools or QA outcomes. n006 can remain capacity-bound for the separately explained queue reason. These limitations do not block writing the generic RED and implementing this narrowly specified correction; they do block claiming the product repaired before the gates run.

## 12. Future deterministic RED/GREEN plan — NOT RUN

All fixtures must use fictional objects, repositories, source versions, and questions. No exposed identifiers, paths, rank literals, or expected answers belong in product logic. Construct RRF inputs to make the structural condition hold; do not tune against saved QA scores.

| Gate | Required fixture and acceptance |
|---|---|
| **CR-1: collateral retention RED first** | A legitimate dense+sparse ordinary witness lies inside its plan-derived role/channel witness envelope but outside the current shortened prefix under many valid frontier challengers. Use a plan and derived pressure that put it at a different rank from the exposed witness. Current constructor must exclude it; corrected constructor must keep it unless an explicit equal-or-better same-channel substitute preserves every component. In the no-substitute RED fixture, require that exact fictional incumbent remains offered. Add a substitution GREEN fixture to ensure protection is not a frozen ID rule. |
| **CR-2: challenger recovery** | Consensus-heavy ordinary base has redundant lower-tail witnesses and an omitted valid, strong legitimate single-channel role candidate. Require a specific feasible exchange, unchanged <=30 bound, and actual offered inclusion. Cover both normal retrieval and global consolidation. Preserve existing R2-A and complementary multi-chunk recovery controls. |
| **CR-3: residual opportunity** | Mixed specialized/ordinary role queues place an omitted single-channel candidate behind earlier competitors. In one fixture earlier offers fail exchange, then a later feasible candidate must still be examined/admitted without rejection consuming quota. In a paired fixture earlier successful competitors exhaust the unchanged role quota: record the later omission as the permitted residual, not a new recovery promise. Do not add dense-specific preference or enlarge a case's ceiling. |
| **CR-4: no entitlement** | Many eligible challengers have no exchange that preserves all incumbent rank witnesses, despite positive capacity. Require fewer than capacity admissions, potentially zero, and unchanged incumbent membership. Add a zero-improvement pair: equal vectors alone must not admit. |
| **CR-5: weak tail exchange** | A weak/redundant ordinary tail can be replaced by a stronger legitimate role/channel witness even when challenger RRF score is lower. Require actual exchange, proving neither blanket legacy-ID retention nor pure RRF. |
| **CR-6: bound/dedup/order** | Check <=30, unique IDs, successful quotas, strict majority, unchanged surviving RRF order, stable role/admission order, and deterministic ties across repeated passes/overlapping roles. Check every accepted exchange's componentwise inequality, including a top-rank improvement that would mask a lower-rank regression under lexicographic comparison. |
| **CR-7: role generality** | Paper through ordinary dense/sparse without dedicated paper; normal workflow and normal graph role privileges; code and other positive/required payload roles. Required-only role uses its existing minimum ceiling. No hardcoded intent or code-only shortcut. |
| **CR-8: fallback safety** | Pair identical specialized object/rank with normal, generic_fallback, and absent origin. Only normal gets specialized challenger/witness contribution. Normal plus better-ranked fallback occurrence across passes must use the normal qualifying rank. Repeated same-channel passes must not manufacture consensus. |
| **CR-9: supplements** | Preserve first unique supplements, overlap precedence, full saturation, reduced residual majority bound, discovery against legacy pool, and truthful actual pool receipt. Do not change C8 structured-only displacement accounting to include frontier victims. |
| **CR-10: shared callers** | Equivalent single-pass snapshots through `retrieve()` and `consolidate_and_select_candidates()` use one shared policy and produce equivalent pool membership/reasons, respecting existing caller ordering semantics. Fake reranker must see the actual offered IDs; detailed diagnostics must report that same pool. |

Required next-task sequence: write and demonstrate CR-1 RED on current product **before** correction; implement the selected shared contract; run CR-1–CR-10, all existing 17 R2 controls, and G4 18/18. Investigate a genuine contradictory recovery gate rather than adjusting constants to pass exposed cases. Only after these deterministic gates should a separately authorized task decide whether any exposed regression rerun is necessary. None runs in this review.

## 13. Empirical boundaries, accounting, and static verification

The selected regression composite remains 20 reviewed complete, 2 incomplete, 6 insufficient, no selected errors. It is 26 original results plus two authorized replacements, not a passed complete single-run cohort. The original 26/28 `INCOMPLETE / INCONCLUSIVE` run and focused rerun `COMPLETE / FAIL` remain unchanged. Existing exposed product verification remains `FAIL / SAFETY REGRESSION`. Fresh generalization benefit is not established. Fresh Lane B remains `OPTIONAL / DEFERRED`.

```text
QA_RUNS = 0
RETRIEVAL_RUNS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
FULL_28_CASE_RERUN = false
N002_N018_RERUN = false
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
DESIGN_CHANGE = true
ANALYSIS_CHANGE = true
STATUS_DOC_CHANGE = true
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

Historical regression reports/results and all raw run stores are preserved. Analysis outputs are forward-only new evaluation artifacts; the analyzer's output guard excludes raw stores. No hashes, manifest regeneration, candidate freeze, product unit suite, or optional full suite is needed.

Static verification for this delivery: analyzer syntax; read-only reproduction with saved-artifact assertions; JSON/per-case/count consistency; local Markdown references; allowed changed-file inventory; full tracked diff review; `git diff --check`. The review's artifact-verification PASS records these checks after completion, not any future synthetic gate. An initial ad hoc read used the Windows default GBK decoder and failed; specifying UTF-8 completed it without modifying input or requiring user action.

## 14. Lifecycle and next task

```text
PHASE_G = IN_PROGRESS / G4_R2_COLLATERAL_RETENTION_DESIGN_COMPLETE
G4 = DETERMINISTIC HARNESS COMPLETE / EXPOSED R2 BENEFIT OBSERVED / R2 COLLATERAL COMPLETENESS REGRESSION ESTABLISHED / COLLATERAL RETENTION FAILURE REVIEW COMPLETE / GENERIC CORRECTION DESIGN READY / VERIFICATION FAIL / FRESH GENERALIZATION BENEFIT NOT_ESTABLISHED
G3_ADMISSION = NO_CHANGE
FRESH_LANE_B = OPTIONAL / DEFERRED
G5_EXECUTION = NOT_AUTHORIZED
NEXT_TASK_RECOMMENDATION = G4 R2 COLLATERAL RETENTION DETERMINISTIC RED / IMPLEMENTATION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

The next recommendation is exact and implementation-ready. It grants no execution authorization, no scientific calls, no new cohort, and no protected-data access. This review stops before that task.

STOP.
