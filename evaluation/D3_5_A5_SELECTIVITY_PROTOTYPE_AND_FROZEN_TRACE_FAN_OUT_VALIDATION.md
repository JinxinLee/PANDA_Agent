# D3.5-A5 — Selectivity Prototype & Frozen-Trace Fan-Out Validation

## 1. Executive verdict

**`PARTIAL / SELECTIVITY_FANOUT_REDUCED_WITH_RELEVANCE_LOSS`.** The one preregistered deterministic selectivity policy, replayed over the six frozen A2 development cases through the exact repository-persistent fixture, achieved its fan-out goal and violated its relevance-retention goal:

| Case | Eligible governed | Old A2 admitted | A5 selected | Reduction | Origins before→after | Graph displacement before→after | Applicable required evidence retained |
|---|---|---|---|---|---|---|---|
| g036 | 3 | 3 | 3 | 0% | 2→2 | 0→0 | **YES** (ana_dpm.C) |
| g021 | 62 | 20 | **4** | **93.5%** | 1→1 | 4→**0** | **NO** (prod_sim_hvmaps.C lost at the origin cap) |
| n006 | 0 | 0 | 0 | — | 0→0 | 0→0 | — (fail-closed) |
| g041 | 0 | 0 | 0 | — | 0→0 | 0→0 | — (fail-closed) |
| g020 | 67 | 20 | **8** | **88.1%** | 7→6 | 20→**8** | — (control) |
| n004 | 0 | 0 | 0 | — | 0→0 | 0→0 | — (fail-closed) |

Per the preregistered decision rule, PASS required all applicable required-evidence bridge candidates for the designated positive mechanistic cases (g036, g021) to be retained. g036 retained; **g021 lost `prod_sim_hvmaps.C`** — it scored 2 (path 1 + title 1) but three same-score README-chunk candidates won the frozen object_id tie-break inside the single-origin `PER_ORIGIN_CAP = 4` boundary. The loss is deterministic and inherent to the frozen design (one origin, 62 candidates, 4 slots), not a governance or nondeterminism failure. A6 is therefore **not ready**; the next stage is a separately authorized selectivity design/decision repair stage.

A5 changed no production state: runtime/D1/D2/query-expansion changes 0, PostgreSQL/Qdrant writes 0, all model calls 0, `A5_ADMISSION_TREATMENT_RUNS = 0`, protected datasets untouched.

## 2. A4 frozen contract

`A4_DESIGN_DECISION = STAGED_SELECTIVITY_THEN_ADMISSION` with `SELECTIVITY_CAP = 8`, `PER_ORIGIN_CAP = 4`, `SELECTIVITY_MODEL_CALLS = 0`, admission budgets `{2, 3}` reserved for A6 (not exercised here). A3's `CONTINUE_ONLY_AFTER_SELECTIVITY_DESIGN` and A2's `PARTIAL / TARGETED_RECOVERY_MIXED` remain immutable. `TRACE_REPLAY_ROLE = POST_OUTCOME_MECHANISTIC_DEVELOPMENT` — the six A2 case outcomes are already exposed.

## 3. Replay fixture construction

`evaluation/d3_5_downstream_replay_fixture.json` (tracked, 1,225,100 bytes, schema 1.0.0, `created_from_frozen_A2 = true`) built mechanically from the frozen A2 records plus the frozen normalized corpus — no gold datasets, no models. Identity records: source A2 result commit `e8e2d5a…`, run `d3_5_a2_focused_20260901`, A1 anchor `470b62f…`, pre-outcome commit `9467061…`, frozen runtime `9b5a849…`, final D1 `9b5a849…`, source manifest `9925ec31…`, index identity (`panda_knowledge_v1`, `8172f9a6…`, 104,973 points, 133,077 SQL objects), case and cell trace identities.

Builder: `evaluation/scripts/d3_5_a5_build_replay_fixture.py`. Per case it persists both structured arms' frozen traces (treatment receipts, plan fields, D2 resolution receipt, per-channel ordered candidate IDs, graph orderings, reachability receipts), the BRIDGED-cell bridge receipts, the complete **pre-cap eligible governed bridge-candidate universe**, the frozen fusion contract (weights, full recomputed baseline fused ordering, top-30 members and cutoff), and a global deduplicated rerank-payload registry (217 entries: `object_id/title/source_id/text[:2000]`).

**Pre-cap universe discovery**: the A2 runtime emits an `INJECTED`-status receipt both for first materializations and for duplicate references to already-injected candidates from other origins (marked in `reason_included`). The eligible universe is therefore the set of **unique** candidates across `INJECTED`/`RANKED_OUT` receipts, each carrying its full origin set: g036 = 3, g021 = 62, g020 = 67 (47 INJECTED receipts = 20 first + 27 duplicates), controls = 0.

## 4. Fixture equivalence proof

All gates passed before Commit 1: BRIDGED-cell fusion recomputed from frozen channel rankings + frozen weights equals the stored `fusion_top30` for all six cases; all persisted orderings equal the frozen records verbatim; bridge identities/origins/versions/locators equal the frozen receipts; per-case baseline displacement reproduction verified; all 217 payloads verified to match the frozen PostgreSQL state read-only; outcome-label cleanliness scan passed (label-like tokens are corpus text such as "MC-truth control", not metadata).

## 5. Outcome-label cleanliness

The runtime fixture contains no `required_evidence`, gold, positive/control, expected-rank, expected pass/fail, case-to-target, or mechanism-success fields. Evaluator metadata (A2 combined-pool match provenance) stays in the A2 records and is consulted only post-output for the retention check.

## 6. Selectivity preregistration

`evaluation/d3_5_a5_selectivity_preregistration.json` (policy `d3_5_a5_selectivity_v1`) was committed with the implementation **before any case-level selectivity outcome existed** (`case_level_outcomes_seen_before_freeze = false`, one variant, `A5_SELECTIVITY_OUTCOME_EXPOSURE = NOT_STARTED` until Phase 3). It froze the tokenizer, formulas, caps, origin semantics, tie-break order, failure behavior, graph-reconstruction contract, invariants, and the full A5 decision rule including the mechanical definition of "material reduction" and the applicability accounting.

## 7. Exact scoring contract

- **Tokenizer** (one generic rule): NFKD → camelCase boundary split (before casefolding) → casefold → non-`[a-z0-9]` runs become separators → dedupe; no stopwords, no stemming. Example: `PndTargetGenerator.cxx` → {pnd, target, generator, cxx}.
- **Query tokens**: tokens(question) ∪ tokens(plan concepts) ∪ tokens(plan symbols) from the frozen BRIDGED cell.
- **Primary score** = path_overlap + title_overlap (set intersection counts against frozen `locator_path` and registry `title`).
- **Minimum relevance criterion**: `primary_score ≥ 1`; below that the candidate is rejected (`zero_score_rejected`) even when slots remain — fail closed.
- **Support (secondary only)**: best 1-based rank across the frozen non-graph channels; pure ordering key, never eligibility, never a vote.
- **Plan scope filter**: if the frozen plan names repositories/versions, out-of-scope sources are rejected; in-scope never earns a score bonus.
- **Ordering**: primary score ↓ → support rank ↑ → structural distance ↑ → stable object_id ↑.
- **Diversity guard**: candidate attributed to its least-used origin (tie: lexicographic); `PER_ORIGIN_CAP = 4` per attributed origin; a candidate whose every origin is at capacity is skipped (`origin_capped_out`).
- **Global cap**: `SELECTIVITY_CAP = 8`, ceiling not quota.

## 8. Anti-tuning boundary

Before Phase-2 commit the policy was never run on any A2 case — only 13 synthetic checks (score ordering, zero-score fail-closed, scope rejection, scope-no-bonus, per-origin cap, global cap, multi-origin survival, support tie-break, structural tie-break, object-id tie-break, determinism, subset invariant, tokenizer contract). The synthetic tokenizer-contract check caught a real bug (casefold applied before camel splitting) which was repaired pre-freeze — the allowed repair window. After outcome exposure: `PARAMETERS_CHANGED_AFTER_OUTCOME_EXPOSURE = 0`. One **result-neutral** diagnostic repair was made post-exposure: `per_origin_retained_counts` switched from membership-based to attribution-based counting (matching the cap semantics), with the informational `per_origin_membership_counts` added — the selection algorithm was untouched and g036/g021 selection identity was verified against the captured pre-repair output (the 9-line diff touches only the diagnostic).

## 9. Six-case development replay

Deterministic double-execution replay of the frozen fixture through the frozen policy (`evaluation/scripts/d3_5_a5_selectivity.py --run-replay`); byte-identical outputs enforced per case. No analyzer, embeddings, retrieval, reranker, or any model call.

## 10. Aggregate fan-out results

See the table in §1. Both high-fan-out cases satisfied the preregistered `material_reduction` check: g021 (4 < 62 and 0 < 4) and g020 (8 < 67 and 8 < 20). Every case satisfied `no_new_control_expansion` (displacement and selection counts never increased versus the old-cap baseline).

## 11. g036 relevance retention

All 3 eligible candidates selected (scores 2 — `prod_aod_complete.C`, `pid_complete.C`, `ana_dpm.C`), all 3 graph-admitted, zero displacement, zero channel overlap — the bridge-only candidates won on primary score alone with no non-graph support, confirming the A4 circularity guard. **`ana_dpm.C` (object.5cae2ceab6e67bb4c9065331) retained.**

## 12. g021 applicability / relevance retention

62 eligible candidates from a single origin (the Mechanism-C `PARAMETERIZES` edge). 27 rejected as zero-score (mostly bare `README.md` paths), 31 `origin_capped_out`, 4 selected (reduction 93.5%, displacement 4→0). **`prod_sim_hvmaps.C` (object.3ab0a90ae68e8ece071a9f22, score 2: path "target" + title token) lost** the object_id tie-break at the 4-slot single-origin boundary against `object.35cf84…`, `object.e8af51…` (both score 2, `macro/target/README.md` chunks) — deterministic and generic, but a real relevance loss. **e2 (`pgenerators/Target/PndTargetGenerator.cxx`) is `NOT_APPLICABLE_TO_SELECTIVITY`**: it was never in the eligible universe (its provenance-bearing edge originates from a non-seed object), so selectivity neither retains nor loses it.

## 13. g020 fan-out reduction

The primary high-fan-out control diagnostic: 67 eligible → 8 selected (88.1% reduction), graph displacement 20 → 8, and the diversity guard spread the 8 selections across 6 origins with a maximum of 3 attributed per origin. No special branch for g020 exists — the guard is the generic per-origin cap.

## 14. Other controls

n006/g041/n004: empty eligible universes → zero selection, zero displacement, zero expansion — fail-closed behavior verified exactly.

## 15. Graph displacement

Displacement after ≤ displacement before in every case (0≤0, 0≤4, 0≤0, 0≤0, 8≤20, 0≤0). The selectivity-only graph stream is reconstructed with the frozen additive-prefix merge semantics on the frozen unbridged graph baseline; fusion weights, graph limit (20), and the unbridged baseline are untouched.

## 16. Origin diversity

Origins before→after: g036 2→2, g021 1→1, g020 7→6, controls 0→0. The g020 attributed counts (1/0/3/1/1/2) demonstrate genuine multi-origin spreading; membership counts (which can exceed 4 because a candidate may belong to several origins) are reported separately as informational.

## 17. Determinism

Every case's selectivity output was computed twice and compared byte-for-byte inside the runner — identical. The policy is a pure function of the fixture.

## 18. What A5 validates

The replay fixture is exact and repository-persistent; one preregistered deterministic policy can bound governed bridge fan-out (62→4, 67→8) and graph displacement (4→0, 20→8) without increasing expansion anywhere; governance/scope/cap invariants and fail-closed behavior hold; bridge-only candidates can win selectivity; the g020 fan-out class is bounded by the generic per-origin guard.

## 19. What A5 does not validate

End-to-end final-evidence recovery (no reranker/selector ran; `CONTROL_MATERIAL_REGRESSION` is not measurable in A5); the admission budgets {2, 3}; and — critically — the current frozen policy does **not** preserve all applicable relevant bridge evidence (g021 loss), so the selectivity design is not yet suitable to freeze for A6.

## 20. A6 readiness

**Gate failed.** A6 is eligible only if A5 establishes no applicable relevant-evidence loss; g021's loss blocks it. `D3.5-A6 = NOT_STARTED / NOT_READY`. The reserved A6 parameters (`ADMISSION_BUDGET_CANDIDATES = {2, 3}`, R1 symmetric repeated reranker evaluation) remain frozen but untested, and A5 did not choose between them.

## 21. Lifecycle

```
D3_5_INITIAL_VALIDATION_CYCLE = COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED
D3.5    = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN
D3.5-A2 = COMPLETE / PARTIAL / TARGETED_RECOVERY_MIXED                       (unchanged)
D3.5-A3 = COMPLETE / POST_A2_BRIDGE_VIABILITY_DECISION_FROZEN                (unchanged)
D3.5-A4 = COMPLETE / BRIDGE_SELECTIVITY_AND_ADMISSION_BUDGET_DESIGN_FROZEN   (unchanged)
D3.5-A5 = COMPLETE / SELECTIVITY_FANOUT_REDUCED_WITH_RELEVANCE_LOSS
D3.5-A6 = NOT_STARTED / NOT_READY
D4      = NOT_STARTED / BLOCKED
```

## 22. Exact next task

A separate design/decision repair stage (candidate name: **D3.5-A5-R1 — Selectivity Relevance-Retention Design Repair**), separately authorized. Per the frozen post-exposure rules, A5 itself must not mutate the selectivity policy and rerun; the repair stage would have to redesign the relevance-retention boundary generically (e.g., how a tight single-origin budget and a lexical title/path score interact) without case-specific rules, then re-freeze and re-validate before any A6 admission work. D4 remains blocked.
