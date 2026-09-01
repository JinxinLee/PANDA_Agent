# D3.5-A4 — Bridge Selectivity & Admission-Budget Design

## 1. Executive design decision

**`A4_DESIGN_DECISION = STAGED_SELECTIVITY_THEN_ADMISSION`.** The post-A2 redesign track continues as two separate, causally clean stages:

- **D3.5-A5 — Selectivity Prototype & Frozen-Trace Fan-Out Validation** (exact next task): build and freeze the compact tracked replay fixture, implement selectivity only, run no admission treatment, measure fan-out/displacement/relevance retention. No reranker required.
- **D3.5-A6 — Bounded Rerank-Admission Prototype & Paired Replay Validation** (later): with selectivity frozen, a fixed small absolute rerank-pool admission reservation evaluated under symmetric reranker-variance accounting.

Key frozen parameters (generic, never case-derived): `SELECTIVITY_CAP = 8`, `PER_ORIGIN_CAP = 4`, `ADMISSION_BUDGET_CANDIDATES = {2, 3}` against the unchanged 30-slot rerank pool. Reranker-variance strategy: **R1 — symmetric repeated reranker evaluation**. A4 changed nothing: runtime/D1/query-expansion changes 0, DB/Qdrant writes 0, retrieval/model calls 0.

## 2. Frozen A2/A3 facts

| Item | Value |
|---|---|
| A2 verdict | `PARTIAL / TARGETED_RECOVERY_MIXED` (immutable; pool-level injection DEMONSTRATED, end-to-end final-evidence recovery NOT_VALIDATED) |
| A3 decision | `CONTINUE_ONLY_AFTER_SELECTIVITY_DESIGN` (immutable) |
| Primary observed downstream boundary | fused candidate set → rerank-pool admission (g036 fused rank 61; g021 e1 fused rank 53; both below the frozen top-30 cutoff) |
| Control/selectivity signal | g020: 112 provenance objects reachable, 20 admitted, 92 capped out, 20/20 graph displacement, `CONTROL_EXPANSION_SIGNAL = true` |
| Identities | A1 anchor `470b62f…`; A2 pre-outcome commit `9467061…`; A2 result `e8e2d5a…`; A3 result `1e8b2b4…`; final D1 `9b5a849…` |

## 3. Parent lifecycle repair

`D3.5 = COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED` correctly described the completed initial A0→A2 cycle but conflicted with the A3-authorized redesign track. Repaired semantics:

- `D3_5_INITIAL_VALIDATION_CYCLE = COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED`
- `D3.5 = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN`

Meaning: the initial bridge design/implementation/evaluation completed → did not validate the end-to-end bridge → A3 authorized a separate bounded redesign track → overall D3.5 work is active again. The A2 verdict is unchanged and A2 is not retroactively invalidated. `D4 = NOT_STARTED / BLOCKED`.

## 4. Local vs persistent trace replay

- `LOCAL_TRACE_REPLAY_FEASIBILITY = SUFFICIENT` — local A2 raw records and the local normalized corpus exist; A3 verified exact fusion reproduction from frozen rankings + frozen weights.
- `REPOSITORY_PERSISTED_REPLAY_FIXTURE_READY = false` — `.gitignore` excludes `/data/evaluation/` and `/data/normalized/` (only `/data/manifests/*.json` is tracked). The raw local A2 run is **not** a durable scientific fixture and may be absent on another machine; a future downstream experiment must not depend solely on it.
- A narrow A3 wording clarification (`D3.5-A4_TRACE_REPLAY_SCOPE_CLARIFICATION`) was applied to the A3 machine artifact, retaining the original verdict verbatim; no A3 decision field changed.

## 5. Replay fixture contract

Suggested tracked artifact: `evaluation/d3_5_downstream_replay_fixture.json` (created in A5 by mechanical, outcome-independent extraction from the frozen A2 records — not in A4).

- **Identity fields**: fixture schema version; source A2 result commit; source run id `d3_5_a2_focused_20260901`; frozen runtime SHA; final repository D1 SHA; source-manifest identity `9925ec31…`; index identity (`panda_knowledge_v1`, fingerprint `8172f9a6…`, 104,973 points, 133,077 SQL objects); case identities; per-cell arm/sequence/treatment-flag trace identity; `created_from_frozen_A2 = true`.
- **Per-case trace**: question text/identity; frozen plan fields (intent, target/version repositories, resolved versions, concepts, symbols, concept scopes, required source types, source budgets); D2 resolution receipt/seed identities; per-channel ordered candidate object IDs with rank and channel name; bridge candidate IDs with provenance origins, source_id, source_version_id, locator; unbridged graph ordering; bridged graph ordering; frozen fusion weights (`exact 2.0, dense 1.0, sparse 1.0, paper 1.15, workflow 1.2, graph 0.8`, score `weight/(60+rank+1)`); full baseline fused ordering; baseline rerank-pool boundary (top-30 members and cutoff score).
- **Size envelope**: compact — IDs, bridge records, a global deduplicated payload registry; no corpus dump, no full documents. A5 must verify the committed size before freezing.

## 6. Reranker payload persistence strategy

**Option 1 chosen — persist the exact bounded reranker payload** (`object_id`, `title`, `source_id`, `text[:2000]` exactly as used by the reranker) in a global deduplicated registry covering the union of baseline fused top-30 members and all bridge candidates per cell. Option 2 (identities + tracked content source) is **invalid**: the normalized corpus is gitignored, so no repository-persistent immutable reconstruction source exists. Option 1 makes the fixture fully repository-replayable. Payload provenance is therefore unambiguous.

## 7. Reranker variance boundary

`UPSTREAM_VARIANCE_CONTROL = FROZEN_TRACE_REPLAY` eliminates analyzer, D2, channel-retrieval, bridge-reachability, bridge-materialization, and fusion-input variance. `RERANKER_VARIANCE = PRESENT / MUST_BE_SYMMETRICALLY_ACCOUNTED` — a paired replay still invokes the reranker model separately on baseline and treatment pools, so an observed difference may contain treatment effect + reranker variance unless handled by preregistered symmetric execution. Chosen strategy: **R1 — symmetric repeated reranker evaluation** (same frozen trace, both pools run the same preregistered number of times, compare distributions/stability). R2 rejected: no deterministic reranker surface exists in the system (the only rerank path is the LLM `generate_json` call). R3 rejected: single paired calls leave variance unresolved exactly where the primary admission question is decided. The repetition count is a small fixed value frozen in the A6 preregistration from a generic stability rationale — never chosen from A2 outcomes, no Monte Carlo sweeps, no heavy significance frameworks.

## 8. Selectivity problem

The bridge currently answers "which candidates are governable and therefore eligible to exist?" It does not answer "which governed candidates are most relevant to this query under a tight downstream budget?" **`GOVERNANCE ELIGIBILITY != QUERY RELEVANCE`** — governance remains a hard prerequisite; selectivity operates only among already governed bridge candidates.

## 9. Current cap is not selectivity

`GLOBAL_BRIDGED_CANDIDATE_CAP = 20` bounds breadth, but candidate materialization is provenance-order bounded, not a dedicated candidate-level query-relevance ranking — **candidate cap ≠ selectivity policy**. The consequence was visible in A2: g021 admitted 19 README-evidence objects alongside `prod_sim_hvmaps.C`, and g020 filled all 20 slots from a single fan-out.

## 10. Candidate relevance signals

| Signal | Status | Role |
|---|---|---|
| A. Exact lexical overlap with query/concepts/symbols | **ELIGIBLE_SIGNAL** | PRIMARY (deterministic, already computed; 0 model calls) |
| B. Sparse score/rank | SUPPORTING_TIEBREAKER_ONLY | circularity risk forbids hard use |
| C. Dense score/rank | SUPPORTING_TIEBREAKER_ONLY | same |
| D. Existing fused non-graph evidence | SUPPORTING_TIEBREAKER_ONLY | no duplicate authority |
| E. Plan source/scope match | **ELIGIBLE_SIGNAL** | bounded eligibility filter |
| F. Locator/title token overlap | **ELIGIBLE_SIGNAL** | PRIMARY (same deterministic family) |
| G. Provenance distance / path cost | SUPPORTING_TIEBREAKER_ONLY | final tie-break; never the sole rule |
| H. Origin confidence/governance status | NOT_AVAILABLE | all frozen D1 relations carry uniform confidence 1.0 / accepted — no discriminating signal |

## 11. Circularity / duplicated-channel risk

A selectivity rule keeping only bridge candidates already ranked highly by dense/sparse/exact would destroy the bridge's incremental value: in A2 the required files were absent from **every** non-graph channel when the focused shortcuts were suppressed — that absence is exactly what the bridge repairs. Therefore non-graph presence is never a hard requirement or a removal trigger; channel support may only add bounded tie-break points within the bridge ordering, and must never become extra structured vote + extra channel vote + forced admission without explicit accounting.

## 12. Fan-out and diversity constraints

One provenance origin must not consume the selectivity budget: `PER_ORIGIN_CAP = 4` (generic guard for the high-fan-out governed-provenance class g020 exposed — one origin contributed all 112 fanned-out objects). Source diversity is preserved across distinct origins/files/relations where multiple exist; no artificial diversity is forced when only one valid origin exists. The rule addresses the class "high-fan-out governed provenance", never "query looks like g020"; values are generic bounds, not derived from g020's exact 112→20 outcome.

## 13. Proposed selectivity policy

```
governed eligible bridge candidates
→ generic deterministic relevance scoring (primary: query/concepts/symbols lexical + locator/title token overlap; bounded plan-scope eligibility filter)
→ per-origin diversity guard (PER_ORIGIN_CAP = 4)
→ small bridge-selectivity cap (SELECTIVITY_CAP = 8, ceiling not quota)
→ graph/additive candidate representation
→ bounded rerank admission (A6 only)
```

Tie-breaking: selectivity score → structural/provenance secondary key → stable object_id lexicographic; never database row order. Fail closed: if no bridge candidate meets the criteria, admit none. `SELECTIVITY_MODEL_CALLS = 0`; no extra embeddings (channel ranks/scores and lexical/query-grounded information are reused). No hand-written file-pattern boosts (`.C`/`README`/`macro/`/`pgenerators/`) — one generic tokenizer for all candidates. Score transparency: a small number of interpretable signals, reconstructible from recorded inputs.

## 14. Admission-policy alternatives

| Family | Verdict |
|---|---|
| A. Fixed small absolute reservation | **SELECTED** (easy to audit/replay, causally clean, bounded) |
| B. Small fraction of rerank pool | REJECTED AS PRIMARY (ratio parameter with no architectural benefit over a fixed ceiling) |
| C. Dynamic reservation by selected count | REJECTED (dynamic complexity without justification) |

## 15. Selected admission policy

A fixed small absolute reservation in a **total-rerank-pool-size-unchanged** pool (30 slots): retain the baseline fused top-N ordering, then replace the lowest-ranked eligible baseline entries with selected bridge candidates not already present, up to the admission budget; displaced IDs recorded. A bridge candidate already in the baseline pool does not consume a reserved slot (dedup by stable object identity; overlap recorded separately). Slots are a **ceiling, not a quota** ("up to K", never "always K"; empty reservation valid, fail closed).

## 16. Admission budget

`ADMISSION_BUDGET_CANDIDATES = {2, 3}` — generic class "small absolute reservation relative to pool size" (≈7% / 10% of 30), both preserving ≥ 90% ordinary-candidate competition. Never derived from g036/g021 fused ranks (61/53) or any case-derived slot count. Comparison without outcome tuning: A6 preregisters both budget arms ex ante against the same frozen baseline pool with preregistered decision criteria (bridge admission ratio, displacement accounting, control safety) — never "whichever makes a positive case pass".

## 17. Admission-vs-selection authority boundary

Every specially admitted candidate remains `GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE` with `IDENTITY_AUTHORITY = NONE`. Admission grants only **permission to compete in the reranker** — never answer authority, never final-selection priority; selection chances improve only through normal reranker/selector evaluation. `SELECTIVITY_CAP` (how many governed candidates survive preselection) and `RERANK_ADMISSION_BUDGET` (how many non-baseline candidates get reserved slots) are distinct and never collapsed.

## 18. Staged vs factorial design

**S1 — STAGED_SELECTIVITY_THEN_ADMISSION** chosen. Rationale: A3 froze `CONTINUE_ONLY_AFTER_SELECTIVITY_DESIGN`; the factorial design (S2) requires proving the admission-only arm is safe to run, but under the unproven-selectivity g020 fan-out it is not — S2 is invalid. S1 preserves clean attribution and minimizes treatment complexity.

## 19. Future causal contrasts

- A5 (selectivity only, no reranker): fan-out reduction, per-origin retention, ordinary graph displacement, bridge-candidate reduction ratio, candidate relevance retention — with the preregistered anti-tuning boundary: the policy is chosen from generic criteria **before** evaluating frozen case outcomes (no "retain ana_dpm.C / prod_sim_hvmaps.C / remove g020 candidates" tuning).
- A6 (frozen selectivity + admission, paired replay): baseline pool vs treatment pool on the same frozen trace, under R1 symmetric repeated reranker evaluation; contrasts reported against the preregistered decision criteria.
- Reusing the A2 six-case set is **post-outcome design validation** (`TRACE_REPLAY_ROLE = POST_OUTCOME_MECHANISTIC_DEVELOPMENT`) — outcomes are already exposed; it is never represented as a fresh holdout. Any later claim of general validated improvement requires a separate untouched evaluation surface (boundary preserved now, not scheduled).
- Runtime selectivity cannot inspect case IDs, roles, or mechanism labels (evaluator-only).

## 20. Replay fixture freeze gates

Before any replay-based experimental outcome: baseline fusion order reproduced exactly; baseline top-30 rerank pool reproduced exactly; bridge candidate identities reproduced exactly; candidate payload reconstruction exact (semantic field equality: `object_id/title/source_id/text payload/order`; byte equality preferred); source/version identities preserved. On any failure: **STOP** — no treatment evaluation on a non-equivalent fixture. Implementation sequence: A4 design freeze → build fixture → verify exact fusion reproduction → freeze fixture → implement selectivity → evaluate (A5) → A6 admission. Selectivity is never implemented before the fixture identity is stable.

## 21. Future diagnostics

Five distinct stage quantities: `eligible_governed_bridge_candidates`, `selected_bridge_candidates`, `graph_admitted_bridge_candidates`, `rerank_reserved_bridge_candidates`, `final_selected_bridge_evidence`. Displacement diagnostics: ordinary graph/rerank candidates displaced, displaced object IDs, bridge overlap with baseline rerank pool, reserved slots used/unused.

## 22. Control safety requirements

- `CONTROL_MATERIAL_REGRESSION` = loss of previously useful final evidence attributable to structured selectivity/admission displacement (no numeric threshold now; never derived from observed outcomes; not all displacement is failure).
- `CONTROL_EXPANSION_SIGNAL` = disproportionate candidate-budget consumption (graph slots, selectivity cap, reserved slots) even without metric regression — non-outcome diagnostic.
- Production boundary unchanged: `CURRENT_PRODUCTION_D2_ROLE = SHADOW`; no bridge production activation; no query-expansion deletion; no D4.

## 23. Protected-data boundary

`NOVEL_VALIDATION_RUNS = 0`; `NOVEL_HOLDOUT_RUNS = 0` — A4 and its immediate prototype stages remain development-only; sealed sets are never used to choose selectivity parameters. Expected evidence/gold selectors remain evaluator-only and never enter the runtime fixture (no gold-candidate markers, required-evidence labels, treatment targets, expected ranks, or case→candidate admission labels inside it; evaluator metadata lives in a separate evaluator-side file).

## 24. Lifecycle

```
D3_5_INITIAL_VALIDATION_CYCLE = COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED
D3.5  = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN
D3.5-A2 = COMPLETE / PARTIAL / TARGETED_RECOVERY_MIXED            (unchanged)
D3.5-A3 = COMPLETE / POST_A2_BRIDGE_VIABILITY_DECISION_FROZEN     (unchanged)
D3.5-A4 = COMPLETE / BRIDGE_SELECTIVITY_AND_ADMISSION_BUDGET_DESIGN_FROZEN
D4    = NOT_STARTED / BLOCKED
```

## 25. Exact next task

> **D3.5-A5 — Selectivity Prototype & Frozen-Trace Fan-Out Validation** — create/freeze the compact tracked replay fixture, implement selectivity only, run no admission treatment, measure fan-out/displacement/relevance retention.
