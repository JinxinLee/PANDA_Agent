# D3.5-A5-R1 — Selectivity Relevance-Retention Design Repair

## 1. Executive decision

**`R1_DESIGN_DECISION = REPAIR_WITH_HIGHER_RESOLUTION_DETERMINISTIC_RELEVANCE`.** The A5 fan-out architecture is kept intact (caps unchanged: `PER_ORIGIN_CAP_NEXT = 4`, `SELECTIVITY_CAP_NEXT = 8`); the repair is a higher-resolution deterministic relevance ranking between the unchanged fail-closed gate and the unchanged caps. The failure was a **ranking-resolution defect, not a budget defect**: the frozen v1 contract ignored three generic, already-persisted information sources — plan-symbol compound identifiers, bounded text payloads, and universe-local token rarity — and double-counted directory tokens through path+title addition.

- Exact next stage: **D3.5-A5-R2 — Repaired Selectivity Prototype Freeze & Revalidation** (implement exactly this design; evaluator upgraded to complete-universe matching; synthetic tests first; exactly one repaired policy evaluated; no admission, no reranker).
- `D3.5-A6 = NOT_STARTED / NOT_READY` — R1 is a design, not evidence of repair.
- R1 changed nothing: production runtime/A5 implementation/fixture unchanged; `REAL_CASE_SELECTIVITY_TREATMENT_RUNS = 0`; all model calls 0; DB/Qdrant writes 0; protected datasets untouched.

## 2. Frozen A5 result

`D3.5-A5 = COMPLETE / SELECTIVITY_FANOUT_REDUCED_WITH_RELEVANCE_LOSS` (experiment valid; commits `e20fc6a` / `70a808d` / `f409562`). Immutable and preserved as historical evidence. Observed failure: g021 — 62 eligible governed bridge candidates from a single provenance origin, `PER_ORIGIN_CAP = 4`, and `prod_sim_hvmaps.C` (primary_score 2) lost under the frozen ordering/tie-break.

## 3. What A5 successfully validated

Repository-persistent replay fixture with exact baseline equivalence; complete pre-cap eligible universe replayable (unique-candidate reconstruction with full origin sets); single validly preregistered deterministic policy; governance/scope invariants; caps respected; high-fan-out reduction (g021 62→4, g020 67→8); graph-displacement reduction (4→0, 20→8); zero-eligible controls fail closed; bridge-only evidence can win without dense/sparse support (g036); deterministic double-execution replay.

## 4. What A5 failed

Exactly one applicable required-evidence candidate was lost: `prod_sim_hvmaps.C` — present in the eligible universe, A2-admitted, primary_score 2 — defeated inside the single-origin 4-slot boundary by three same-score README-chunk candidates via the object_id tie-break. The loss is deterministic; no governance, fixture, nondeterminism, or tuning failure was involved.

## 5. Ranking-vs-budget diagnosis

Does the system possess enough generic information to rank meaningfully before the origin cap? **Yes** — four unused/underused generic sources were verified in the frozen fixture and plan fields: (1) plan-symbol compound identifiers (`plan.symbols = ["restgas_profile"]` exists for g021 but v1 had no identifier tier); (2) bounded text payloads (`text[:2000]` persisted for every candidate, unused by v1; `prod_sim_hvmaps.C`'s text literally contains `restgas_profile`); (3) universe-local token rarity (df: `target` 49/62, `readme` 61/62 vs `supplied` 2/62 — computable deterministically from the eligible universe alone); (4) locator basename/parent-directory decomposition. Budget relaxation is therefore unnecessary and rejected.

## 6. Current lexical-score limitations

v1 = `path_overlap + title_overlap`, raw counts, no rarity, no text, no identifier tier. Four structural defects (all SUPPORTED): raw counts cannot distinguish df-49 tokens from df-2 tokens; title==path for source-file objects double-counts one generic directory token; README section titles are long descriptive sentences whose raw overlap outranks precise file identifiers; the identifier compound form is destroyed by tokenization with no exact-match tier.

## 7. Query-side token analysis

The union (question ∪ plan.concepts ∪ plan.symbols) is retained. Its generic tokens are not removed by hand lists (prohibited); instead rarity weighting downweights universe-ubiquitous tokens automatically, and the symbol tier gives compound identifiers their own channel. Root cause B: PARTIAL.

## 8. Locator/title/text relevance analysis

- **Locator structure**: generic basename vs parent-directory decomposition adopted (a basename match is more specific than a directory match); no directory names encoded. Root cause E: SUPPORTED — `prod_sim_hvmaps.C`'s persisted title equals its path, so v1 counted the generic directory token `target` twice (both score points came from one df-49 token).
- **Title semantics**: title tokens stay in the lexical view but the additive path+title double-count is removed; no README penalty — the issue is discrimination, not extension preference. Root cause G: SUPPORTED.
- **Text payload**: bounded `text[:2000]` adopted as query relevance evidence only (symbol-exact tier + distinct-token presence level); never governance, identity authority, or answer truth; raw occurrence counts rejected for length bias. Root cause C: SUPPORTED.

## 9. Existing-channel support analysis

Support rank remains the secondary rank after all primary levels — promoting it was evaluated and rejected because g036 proved bridge-only candidates must be able to win on primary signals alone (circularity risk). Root cause H: SUPPORTED as observed (3 of 4 g021 winners had support; prod_sim had none) but the repair is higher-resolution primary signals.

## 10. Structural-distance analysis

All 62 g021 candidates share one origin at distance 1 — zero discrimination inside single-origin sets. Retained as tie-breaker only. Root cause I: SUPPORTED (as a limitation of v1 discrimination, not a reason to promote distance).

## 11. Origin-cap analysis

Root causes J/K/L: **REJECTED**. The per-origin cap correctly bounded the fan-out (62→4, displacement 4→0); the selectivity cap was never binding in g021 (4 < 8); the attribution semantics were inert with a single origin. A known candidate appearing just outside a cap is not sufficient evidence that the cap is the defect — the evidence shows abundant unused ranking information inside the cap boundary.

## 12. Candidate repair families

- **R1-A — richer deterministic lexicographic hierarchy: SELECTED.**
- R1-B — compact weighted deterministic score: rejected (weights add tuning surface; lexicographic levels are weight-free and more auditable).
- R1-C — two-stage gate + ranking: partially adopted (the gate is unchanged; the repair is the ranking resolution).
- R1-D — budget-only relaxation: rejected (prohibited as primary repair; would admit more low-resolution candidates without improving ordering).

## 13. Selected relevance design (`d3_5_selectivity_v2`, to be implemented in A5-R2)

Hard filters unchanged (governance universe, plan scope, `MIN_PRIMARY_SCORE ≥ 1` on path/title overlap — admission breadth is not widened). Primary rank, lexicographic:

1. **symbol_exact_tier** — distinct compound plan-symbol strings (unsplit identifier form) occurring in basename ∪ path ∪ text[:2000]; inert when `plan.symbols` is empty.
2. **rarity_weighted_overlap** — Σ over distinct query tokens present in (basename ∪ parent-dir ∪ title ∪ text) of `idf(t) = log2(|U| / (1 + df(t)))`, df computed solely over the current query's eligible universe (path ∪ title ∪ text token views).
3. **basename_coverage** — distinct query tokens in the locator basename.
4. **text_presence** — distinct query tokens in `text[:2000]` (bounded distinct count; length-bias mitigation).

Then: support_rank (secondary, never mandatory) → structural distance → stable object_id. Caps and origin attribution unchanged. All signals deterministic functions of the frozen fixture: `SELECTIVITY_MODEL_CALLS = 0`, `EXTRA_EMBEDDING_CALLS = 0`.

## 14. Rejected alternatives

Raw text overlap counts (length bias); token precision (inverse length bias); standalone coverage; README/file-type penalties; budget relaxation; corpus-wide IDF (universe-local only); learned scorers, embeddings, LLM relevance judges; text proximity/co-occurrence (overengineered for this stage; revisit only on R2 evidence).

## 15. Cap decision

`PER_ORIGIN_CAP_NEXT = 4`; `SELECTIVITY_CAP_NEXT = 8`. Independent justification: root causes J/K/L are rejected with evidence — the caps behaved correctly and the loss occurred inside the origin boundary from ranking-resolution poverty while abundant unused generic discrimination exists.

## 16. Evaluator coverage repair

**Old limitation**: A5's retention check derived applicable candidates from frozen A2 combined-pool match provenance — biased toward A2-admitted evidence; a required-evidence candidate ranked out by the old 20-cap never entered the A2 pool and could not be classified applicable. **Repaired contract**: revalidation evaluates the **complete pre-cap eligible governed universe × frozen evaluator-only expected-evidence selectors**, reusing the existing deterministic evaluator matching semantics (no second gold-matching definition). Applicability classes frozen: `APPLICABLE_AND_RETAINED` / `APPLICABLE_AND_LOST` / `NOT_APPLICABLE_TO_SELECTIVITY` (genuinely absent from the complete universe; old-cap ranked-out evidence is never "not applicable"). R2 implementation note: if selector matching needs per-candidate fields beyond the fixture's persisted set (e.g., object_type), the fixture may be extended additively and mechanically from the frozen normalized corpus, documented in the R2 preregistration before outcomes.

## 17. Outcome-label isolation

Flow preserved: fixture → selectivity runtime → selected candidates frozen → evaluator-only selector matching → retention metrics. Expected evidence never reaches the selectivity score; the runtime policy remains outcome-label clean.

## 18. Future anti-tuning boundary

`SELECTIVITY_REPAIR_VARIANTS_EVALUATED_ON_REAL_CASES = 0` in R1; `NUMBER_OF_R2_REPAIRED_POLICIES_TO_EVALUATE = 1`; sequence: design freeze (R1, this artifact) → R2 implementation → evaluator upgrade → synthetic tests → freeze/commit → one real six-case revalidation → verdict. No outcome-guided iteration; no winner-picking.

## 19. Lifecycle

```
D3_5_INITIAL_VALIDATION_CYCLE = COMPLETE / STRUCTURED_EVIDENCE_LINK_BRIDGING_NOT_VALIDATED
D3.5    = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN
D3.5-A2   = COMPLETE / PARTIAL / TARGETED_RECOVERY_MIXED                        (unchanged)
D3.5-A3   = COMPLETE / POST_A2_BRIDGE_VIABILITY_DECISION_FROZEN                 (unchanged)
D3.5-A4   = COMPLETE / BRIDGE_SELECTIVITY_AND_ADMISSION_BUDGET_DESIGN_FROZEN    (unchanged)
D3.5-A5   = COMPLETE / SELECTIVITY_FANOUT_REDUCED_WITH_RELEVANCE_LOSS           (unchanged; exposure metadata repaired to COMPLETE)
D3.5-A5-R1= COMPLETE / SELECTIVITY_RELEVANCE_RETENTION_REPAIR_DESIGN_FROZEN
D3.5-A6   = NOT_STARTED / NOT_READY
D4        = NOT_STARTED / BLOCKED
```

A5 audit metadata repaired narrowly (`D3.5-A5-R1_METADATA_REPAIR`): exposure state STARTED → COMPLETE with the historical boundary preserved; the evaluator coverage limitation recorded; the A5 post-exposure diagnostic repair (membership→attribution counting) remains valid and is not reinterpreted as a policy mutation.

## 20. Exact next task

> **D3.5-A5-R2 — Repaired Selectivity Prototype Freeze & Revalidation** — implement exactly the frozen v2 relevance design, upgrade the evaluator to complete-universe matching, run synthetic tests before real outcomes, freeze the implementation, evaluate exactly one repaired policy on the six frozen cases, preserve the caps, run no admission and no reranker.
