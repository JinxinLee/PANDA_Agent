# D3.5-A3 — Post-A2 Bridge Viability & Downstream Competition Decision

## 1. Executive decision

**`FOLLOW_UP_DECISION = CONTINUE_ONLY_AFTER_SELECTIVITY_DESIGN`.** The structured-evidence bridge line is worth continuing: A2 proved the A+B mechanism works end-to-end up to candidate injection with full receipts, and the loss point is a single, exactly quantified downstream boundary. But A2's control case g020 demonstrated that one ordinary query can fan out 112 governed provenance objects (20 admitted to graph, 92 capped out, 20/20 graph-slot displacement) through a single ambiguous seed. An admission experiment without a designed selectivity gate would let such fan-outs monopolize the rerank pool, so selectivity must be designed first.

- Exact next stage: **D3.5-A4 — Bridge Selectivity & Admission-Budget Design** (design/preregistration only; no implementation, prototype, or evaluation inside A4).
- Preferred intervention boundary: **fused candidate set → rerank-pool admission** — the earliest downstream boundary at which A2 receipts show the required candidates are lost.
- D3.5 lifecycle unchanged: `COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED`. D4 remains `NOT_STARTED / BLOCKED`.
- A3 changed nothing: `runtime files changed = 0`, D1/query-expansion configs `0`, PostgreSQL/Qdrant writes `0`, retrieval/model calls `0`, protected datasets untouched.

## 2. Frozen A2 facts

| Identity | Value |
|---|---|
| Frozen A1 scientific-state anchor | `470b62f823c3e65637604da2f614461c1a81d5b6` |
| A2 pre-outcome execution commit (manifest + runner) | `9467061c81a288f2c3b01548b7eb39202f38e91c` |
| A2 final result commit | `e8e2d5aa532a6b54ebdcc728804b211e44fb2132` |
| Final repository D1 | `9b5a84996c30eaf1a297924b36452a90fe6d84d2` |

Frozen verdict `PARTIAL / TARGETED_RECOVERY_MIXED` (experiment valid; 24/24 cells). Frozen causal result: `LEGACY−ABLATION = +0.4` final evidence; `UNBRIDGED−ABLATION = 0.0` final and combined; `BRIDGED−UNBRIDGED = 0.0` final / `+0.3` combined; `BRIDGED−LEGACY = −0.4` final. Frozen mechanism status: Mechanism A `VALIDATED_OBSERVED`; Mechanism B `VALIDATED_OBSERVED`; Mechanism C use `PARTIALLY_OBSERVED`; pool-level injection `DEMONSTRATED`; end-to-end final-evidence recovery `NOT_VALIDATED`. These are immutable and were not relabeled.

## 3. Audit-record corrections

Two audit-record issues were repaired in the A2 machine artifact and report (`D3.5-A3_A2_AUDIT_RECORD_REPAIR`), with metrics, verdict, and cell identities verified byte-unchanged:

1. **Commit-role naming**: `470b62f…` is the **frozen A1 scientific-state anchor** (the A1-R3 state before A2 evaluation-only files were added), not the manifest commit; `9467061…` is the **A2 pre-outcome execution commit** that actually contains the execution manifest and the A2 runner before the first formal cell. The full identity set now also records `git_head_during_run = 9467061…` and `final_result_commit = e8e2d5a…`.
2. **Cell reruns vs model attempts**: `FORMAL_CELL_RERUNS = 0` — no formal cell was discretionarily rerun. `EXTRA_GENERATION_ATTEMPTS = 2`: the frozen vertex `generate_json` client runs an internal transient-retry loop (up to 3 attempts; each attempt records one generation request before the API call). It fired once in g021/ABLATION (sequence 6: `generation_calls=3`, `model_calls=4`) and once in n004/LEGACY (sequence 21), each contributing +1 generation and +1 model call. The retry mechanism is determinable from the frozen client and per-cell deltas; the retried stage (analyzer vs reranker) is `NOT_DETERMINABLE_FROM_PERSISTED_RECEIPT`.

## 4. Root-cause decomposition

The post-A2 question: is the next problem genuinely a downstream competition/admission problem rather than another reachability, D1, or provenance problem? Each candidate explanation was tested against the frozen receipts:

| Explanation | Status | Evidence |
|---|---|---|
| A. Reachability failure | **REJECTED** | all attempted paths `REACHED` with receipts; 0 `STRUCTURAL_PATH_NOT_FOUND`, 0 budget exhaustion |
| B. Provenance materialization failure | **REJECTED** | required candidates injected (g036 `ana_dpm.C` via `edge.2e09628416a01ce2461d752a`; g021 e1 `prod_sim_hvmaps.C` via `edge.ea3a79d222f0ca6cc0e6df72`) with exact frozen versions |
| C. Source/version qualification failure | **REJECTED** | `VERSION_SCOPE_CONFLICT` never triggered; exact frozen `source_version_ids` on all bridged candidates |
| D. Candidate-cap failure | **REJECTED** | no cap bound the required candidates (g036: 3/3 injected; g021: e1 injected within the 20-cap) |
| E. Graph-stream displacement/competition | **PARTIAL** | required candidates entered the stream and pool; displacement hit ordinary candidates (g021: 4; g020: 20/20) — a selectivity risk, not the primary loss point |
| F. Cross-channel fusion admission failure | **SUPPORTED (primary)** | both required candidates scored below the fused top-30 cutoff (see §5/§6) |
| G. Reranker failure | **REJECTED AS CAUSE / NOT TESTED** | bridge candidates never reached the reranker |
| H. Final selector failure | **REJECTED AS CAUSE / NOT TESTED** | selector never saw the bridge candidates |
| I. Stochastic analyzer/reranker variance | **REJECTED AS PRIMARY CAUSE** | the loss is deterministic and exactly recomputable from frozen channel rankings + frozen weights; the variance class only produced metric-neutral control R@5/MRR spreads |

**Conclusion**: the first failed downstream boundary is **cross-channel fusion admission (fused candidate set → rerank-pool admission)**; reachability, D1, and provenance are not binding.

## 5. g036 downstream loss

`macro/target/ana_dpm.C` was governed, reached, materialized, entered the graph stream (prefix position 3/16), and entered the candidate pool (combined recall 1.0) — but its fused score was `0.8/(60+3) = 0.012698` (fused rank 61), below the top-30 admission cutoff `0.015789` (shortfall 0.003091). It never entered the fused rerank pool, was never reranked, and never reached the final selector. The exact first failed boundary: **fused candidate set → rerank-pool admission**. No inference beyond persisted diagnostics: the recomputation from the persisted channel rankings reproduces the stored `fusion_top30` exactly.

## 6. g021 two-failure decomposition

The two required evidence groups failed for **different reasons** and are not collapsed:

- **e1 (`prod_sim_hvmaps.C`) — downstream competition.** The bridge reached the Mechanism-C `PARAMETERIZES` edge, materialized 62 governed evidence objects (20 admitted, 42 capped out) including e1, and e1 entered the pool (combined recall 0.5). Its fused score `0.8/(60+9) = 0.011594` (fused rank 53) fell below the cutoff `0.014286` (shortfall 0.002692) — the same boundary as g036.
- **e2 (`pgenerators/Target/PndTargetGenerator.cxx`) — upstream seed/reachability coverage boundary.** Its provenance-bearing edge (`edge.81276373f106c8758d5aec92`) originates from `file_pattern.restgas_profile_input`, which the frozen D2 resolution did not seed for this question (statuses: RESOLVED_UNIQUE 1, UNRESOLVED 2); the frozen one-transition budget never reaches that edge. This is **not** a downstream competition failure and **not** a Mechanism-C governance failure — the provenance exists in final D1. It is recorded as a remaining coverage boundary; Mechanism-C governance stays frozen and is not repaired here.

## 7. g020 expansion/selectivity signal

| Quantity | Value |
|---|---|
| Bridged candidates generated (fan-out) | 112 governed objects from 2 provenance-bearing edges |
| Bridged candidates admitted to graph | 20 (bridge cap) |
| Candidates capped out | 92 |
| Graph candidates displaced | 20 / 20 (entire graph channel) |
| Final result regression | none (1.0 in all four arms) |

Accounting: `CONTROL_OUTCOME_REGRESSION = false`; `CONTROL_SCOPE_LEAKAGE = false`; **`CONTROL_EXPANSION_SIGNAL = true`**. g020 must not be described as "safe because the metric is unchanged": a single Tier-D ambiguous seed (atomically admitted, set size 2) fanned out 112 provenance objects on an ordinary control query and displaced the entire graph channel. This is a first-class selectivity design constraint for any future admission experiment.

## 8. What A2 validated

Bounded governed structural reachability (Mechanism A) with atomic Tier-D ambiguity handling; exact provenance materialization into source-native candidates with frozen source versions (Mechanism B); additive pool-level bridge injection with zero dedup overlap, zero version conflicts, full displacement receipts, and zero prohibited-use counter violations across all 12 structured-arm executions.

## 9. What A2 did not validate

End-to-end final-evidence recovery: no bridged candidate ever reached the reranker, the selector, or final evidence on any case. `BRIDGED−ABLATION` remains a combined contribution, never a pure bridge effect. Pool-level value is not relabeled as end-to-end success.

## 10. Candidate downstream interventions

| Option | Verdict | Core reason |
|---|---|---|
| A. Increase global graph fusion weight (0.8 → larger) | REJECTED AS FIRST CHOICE | poor causal clarity; global blast radius on all graph candidates; does not specifically solve bridge admission; broad retuning lacks justification |
| B. Increase global rerank-pool size (top-30 → top-N) | REJECTED AS FIRST CHOICE | linear token/cost increase for every query; admits more irrelevant candidates globally; g036's rank 61 would need a ~60-slot pool (cost doubling) — conflates "more" with "fair" |
| C. Separate structured vote / extra RRF weight | REJECTED WITHOUT NEW PREREGISTRATION | double-counting risk (bridge candidates already carry the graph contribution); A0 explicitly prohibited it; not normalized as the default |
| **D. Bounded rerank-pool admission reservation** | **PREFERRED CANDIDATE** | acts exactly at the failed boundary; admission ≠ force selection; preserves candidate authority and normal reranker/selector competition; must be paired with a selectivity gate |
| E. Increase graph candidate limit | REJECTED | acts before the same fusion bottleneck; against g020 it amplifies displacement instead of solving admission |
| F. Relevance-gated bridge preselection | **REQUIRED COMPONENT** | governance decides existence; generic deterministic relevance may only order/select among governed candidates under a cap; directly answers the g020 fan-out |
| G. Force-select bridge evidence | REJECTED | bypasses the ranking question; violates `GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE` (identity authority NONE) |

## 11. Double-vote / ranking-authority risks

Any future design must preserve the additive candidate authority with identity authority NONE, must not add an independent RRF vote or weight on top of the existing graph contribution (double-counting), and must not let admission automatically improve final-selection chances — only the chance to be considered by the reranker. Selection improvements must come only through normal reranker/selector evaluation.

## 12. Selectivity requirements

`SELECTIVITY_REQUIRED = true`. The dual requirement any future design must answer: (1) genuinely relevant provenance-backed bridge candidates get a fair chance to reach reranking; (2) a broad governed provenance fan-out cannot monopolize the graph/rerank budget. Any admission budget must be justified generically (e.g., a small fixed provenance-backed admission budget relative to the existing rerank-pool size) — never derived from case-specific positions ("g036 needs rank 3", "g021 needs rank 9" are explicitly prohibited derivations). The exact value remains to be preregistered in A4.

## 13. Frozen-trace replay feasibility

**`TRACE_REPLAY_FEASIBILITY = SUFFICIENT_FOR_DOWNSTREAM_EXPERIMENT`.** Verified during A3 from the frozen A2 records:

- Channel candidate order is fully persisted per cell (complete per-channel object_id lists; e.g., g036 BRIDGED: exact 7 / dense 20 / sparse 20 / workflow 20 / graph 16).
- Fusion is a deterministic function of channel rankings + frozen weights (`exact 2.0, dense 1.0, sparse 1.0, paper 1.15, workflow 1.2, graph 0.8`, score `weight/(60+rank+1)`). Recomputation from the frozen records **exactly reproduces** the stored `fusion_top30` for both positive cells.
- Candidate identities and payloads (title/source_id/source_version_id/locator/text) are recoverable from the frozen normalized corpus (`9925ec31…`) by object_id; the rerank payload (`object_id/title/source_id/text[:2000]`) is therefore reconstructible.
- The unbridged graph baseline is the UNBRIDGED cells' `graph` ranking; bridge candidate IDs, origins, versions, and locators are persisted per candidate.

**Reranker-only replay is possible**: a changed admission pool can be reranked and selector-evaluated without rerunning the analyzer, D2, channel retrieval, or bridge reachability/materialization. The causal benefit is exact — same frozen upstream state, only the downstream admission treatment differs. Caveat: the reranker is a model call, so a paired replay must rerun the frozen reranker on both the baseline pool and the treatment pool so execution variance applies symmetrically.

## 14. Recommended next experiment shape

Prefer paired downstream experiments over four independent end-to-end executions: frozen A2 upstream trace → unchanged baseline downstream policy **vs** the same frozen trace → candidate admission/selectivity treatment. Evaluated (not frozen) arm shapes: `CURRENT_BRIDGED` (frozen A2 bridge behavior as replay baseline), `ADMISSION_TREATMENT` (same bridge candidates + bounded rerank-pool admission), optional `SELECTIVITY_TREATMENT` (admission + separately specified selectivity gate). No unbridged reference is needed unless comparability demands it; the A2 four-arm experiment is not reproduced.

## 15. Causal identifiability requirements

Only the downstream admission policy may vary between arms; bridge reachability, materialization, D1, D2, query expansions, and source/index state stay frozen and identical. If selectivity and admission both change, use separate staged experiments or explicit factorial arms — never label a combined outcome an "admission effect". A2 facts reusable as historical frozen evidence: legacy dependency, unbridged baseline, pool-level injection value, reachability/materialization receipts, control stability. Requiring contemporaneous controls: any outcome under the new policy (reranker is re-run, so paired baseline treatment is mandatory) and control-case regression/displacement under the new policy.

## 16. Safety/control requirements

Preregistered control-failure concept (defined before outcomes, no numeric threshold from future results, and not all displacement is inherently bad): **material loss of previously useful evidence caused by structured admission/displacement**. Expansion diagnostics to freeze in any future experiment: bridged candidates generated / admitted to graph / admitted to rerank pool; ordinary candidates displaced from graph / from rerank pool; bridge admission ratio; final selected bridge evidence; control regressions. Production boundary unchanged: `CURRENT_PRODUCTION_D2_ROLE = SHADOW`; no bridge production activation; no query-expansion deletion; no D4.

## 17. Rejected alternatives

Global graph-weight retuning, global rerank-pool enlargement, a separate structured fusion vote (absent new preregistration), graph-limit increase, and force-selection are all rejected as first-choice interventions for the reasons in §10; Option F (relevance-gated preselection) is retained as a required component of the A4 selectivity design rather than a standalone fix.

## 18. Follow-up decision

**`CONTINUE_ONLY_AFTER_SELECTIVITY_DESIGN`.** Rationale: every `CONTINUE_WITH_BOUNDED_DOWNSTREAM_COMPETITION_EXPERIMENT` precondition is individually supported (pool-level value demonstrated; failure localized at one exact boundary; a small generic intervention is isolable; g020 risk is receipted and measurable), but g020's demonstrated fan-out means candidate selectivity must be designed before any admission experiment is scientifically safe. The decision is based only on measured value, architectural cleanliness, causal identifiability, generalization potential, control risk, and implementation scope — implementation effort already spent was ignored.

## 19. Lifecycle

```
D3.5   = COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED  (unchanged)
D3.5-A2 = COMPLETE / PARTIAL / TARGETED_RECOVERY_MIXED               (unchanged, audit-repaired records only)
D3.5-A3 = COMPLETE / POST_A2_BRIDGE_VIABILITY_DECISION_FROZEN
FOLLOW_UP_DECISION = CONTINUE_ONLY_AFTER_SELECTIVITY_DESIGN
D4     = NOT_STARTED / BLOCKED                                        (unchanged)
```

The follow-up is a new experimental repair/validation track, not retroactive A2 success.

## 20. Exact next task

> **D3.5-A4 — Bridge Selectivity & Admission-Budget Design** — design/preregistration first; no implementation, prototype, or evaluation inside A4.

Frozen next scientific question (generic, no case filenames):

> Can a small, bounded, generic admission policy — gated by generic deterministic selectivity — allow governed provenance-backed bridge candidates to reach normal reranking while preserving ordinary candidate competition and avoiding control overexpansion?
