# D3.5-A5-R1-R1 — Relevance Formula & Exact-Match Contract Repair

## 1. Executive repair decision

**`R1_R1_DECISION = RELEVANCE_FORMULA_AND_EXACT_MATCH_CONTRACT_REPAIRED`.** Both preregistration-level defects identified by independent audit are now fully frozen, leaving R2 with zero contract discretion:

1. **IDF formula repaired**: `idf(t) = log2((|U| + 1) / (df(t) + 1))` — non-negative, `idf(df = N) = 0`, strictly decreasing in df, deterministic (verified 17/17 synthetic property checks).
2. **Symbol-exact semantics repaired**: NFKC → casefold → path-separator normalization; boundary-aware matching with the identifier class `[a-z0-9_]`; underscore preserved; no hyphen/camelCase equivalence; surfaces = basename/path/text[:2000] with title excluded; distinct-symbol counting; empty `plan.symbols` → 0.
3. **`GATE_RECALL_LIMITATION`** evaluator-only diagnostic frozen with the four future applicability classes.

R1's top-level decision (`REPAIR_WITH_HIGHER_RESOLUTION_DETERMINISTIC_RELEVANCE`), the caps (`PER_ORIGIN_CAP_NEXT = 4`, `SELECTIVITY_CAP_NEXT = 8`), and every other R1 conclusion are preserved unchanged. R1-R1 changed no code, no fixture, no A5 result, and ran no real-case treatment (`REPAIRED_SCORER_RUNS = 0`, all model calls 0).

## 2. Parent R1 state

`D3.5-A5-R1 = COMPLETE / SELECTIVITY_RELEVANCE_RETENTION_REPAIR_DESIGN_FROZEN` (commit `240cfe0…`), parent decision `REPAIR_WITH_HIGHER_RESOLUTION_DETERMINISTIC_RELEVANCE`, on top of the immutable A5 result (`PARTIAL / SELECTIVITY_FANOUT_REDUCED_WITH_RELEVANCE_LOSS`, commits `e20fc6a` / `70a808d` / `f409562`).

## 3. IDF defect

The R1-frozen formula `idf(t) = log2(|U| / (1 + df(t)))` is defective: when a token is ubiquitous in the eligible universe (`df(t) = |U|`), `idf = log2(|U| / (|U| + 1)) < 0` — a **matched** query token would create *negative* relevance evidence. Worked example: N = 10, df = 10 → log2(10/11) = −0.1375.

## 4. Repaired IDF formula

**`idf(t) = log2((|U| + 1) / (df(t) + 1))`** (base 2). Adopted unchanged from the task-preferred contract: it satisfies every required invariant with the smallest deviation from the R1 design; no alternative formula is needed.

## 5. Mathematical invariants

For N = |U| ≥ 1 and 1 ≤ df ≤ N: `idf(df) ≥ 0`; `idf(df = N) = 0`; `idf(df = 1) > idf(df = 2) > … ≥ idf(df = N)`; identical (N, df) → identical value. No corpus-global statistics, no expected evidence, no case-specific constants. Floating-point values are ranking-only: ranking compares unrounded deterministic values; serialization may round for diagnostics only. All invariants verified synthetically (17/17 checks, including reproduction of the old-formula negative defect for documentation).

## 6. df / candidate-view semantics

- `df(t)` = number of **unique eligible candidate object IDs** whose `candidate_lexical_view` contains t — not receipts, not origins, not occurrences, not selected counts; a candidate belonging to multiple origins counts once.
- `candidate_lexical_view` = deduplicated union of tokens from locator basename, parent-directory components, title, and bounded `text[:2000]`, under the frozen v1 lexical tokenizer. Set semantics: repeated occurrences inside one candidate never increase df.
- Effect: a token present in path + title + text contributes its IDF weight **once** at ranking level 2 — removing the R1-diagnosed path/title double-count.
- Empty universe: if `|U| = 0`, select none and perform no IDF computation; no division fallback hacks.

## 7. Symbol-exact ambiguity

R1 defined the tier only as "count of compound plan-symbol strings whose occurrence is found in basename/path/text", leaving case sensitivity, Unicode normalization, substring behavior, identifier boundaries, underscore, hyphen, and path-separator handling implementation-defined. R1-R1 freezes all of them.

## 8. Normalization contract

Both the plan symbol and the candidate search surface: **Unicode NFKC → casefold → path separators to "/"**. The compound identifier is never split for this tier (`restgas_profile` remains one identifier); the ordinary split-token lexical scorer is separate and unchanged. Case-insensitivity is deterministic via casefold.

## 9. Identifier-boundary contract

A normalized symbol matches only if its occurrence is bounded on both sides by start/end of string or a character **not** in `[a-z0-9_]`. Underscore is part of an identifier. Positive: `… restgas_profile …`, `/restgas_profile/`, `restgas_profile(`, `macro/target/restgas_profile.txt`. Negative: `my_restgas_profile_backup`, `restgas_profile2`, `xrestgas_profile`. Arbitrary substring matching is prohibited.

## 10. Search surfaces and count semantics

- **Hyphen**: `restgas-profile` does **not** exact-match `restgas_profile` (no invented equivalence; ordinary lexical overlap still applies).
- **CamelCase**: `RestgasProfile` does **not** equal `restgas_profile` for this tier (no camel-splitting; no existing canonical normalization establishes equivalence).
- **Surfaces**: locator basename, full normalized locator path, bounded `text[:2000]`. **Title is excluded** by the strong default — it is synthetic/descriptive and duplicates path semantics for source-file objects; recorded explicitly.
- **Count**: number of **distinct** plan symbols with ≥ 1 valid boundary-aware match in any allowed surface; 10 occurrences → 1; path + text hits → 1.
- **Empty `plan.symbols`** → `symbol_exact_tier = 0` for every candidate; no fallback to inferred symbols.
- The tier remains **PRIMARY_RANK level 1, ranking-only** — not governance authority, hard inclusion, answer truth, or required-evidence mapping.

## 11. Final v2 rank hierarchy

```
1. symbol_exact_tier DESC
2. rarity_weighted_overlap DESC   (repaired non-negative universe-local IDF)
3. basename_coverage DESC
4. text_presence DESC             (distinct normal query tokens in text[:2000])
5. support_rank ASC               (missing = worse than any present; never disqualifying)
6. structural_distance ASC
7. stable candidate_object_id ASC
```

No weights between levels; no outcome-based reordering. Lexical-view dedup semantics: basename/parent-dir/title/text tokens are one deduplicated set before the IDF-weighted overlap; `basename_coverage` and `text_presence` deliberately remain separate later levels (cross-level structural specificity, not double-counting); `text_presence` counts distinct normal query tokens, not raw occurrences.

## 12. Gate-recall diagnostic

Frozen evaluator-only category **`GATE_RECALL_LIMITATION`**: a required-evidence candidate present in the complete pre-cap eligible universe, identified as required by the repaired evaluator, but rejected by the **unchanged** `MIN_PRIMARY_SCORE ≥ 1` path/title gate before v2 ranking. Distinct from `APPLICABLE_AND_LOST_AFTER_RANKING`. If R2 observes it: do **not** modify the gate inside R2 — record and stop/route to a later design stage. R1-R1 does not change the gate and does not widen eligibility.

## 13. Evaluator implications

Future evaluator classes frozen: `NOT_APPLICABLE_TO_SELECTIVITY` (absent from the complete eligible universe) / `GATE_RECALL_LIMITATION` / `APPLICABLE_AND_RETAINED` / `APPLICABLE_AND_LOST`. The R1 complete-universe contract is preserved (no reversion to A2 combined-pool provenance); expected evidence remains completely absent from runtime scoring; all four classes are evaluator-only.

## 14. Anti-tuning boundary

`NUMBER_OF_R2_REPAIRED_POLICIES_TO_EVALUATE = 1`. Sequence: R1-R1 contract frozen → R2 implementation → evaluator implementation → synthetic tests → freeze commit → one real six-case revalidation. R2 has **no discretion** over the IDF formula, df definition, candidate lexical view, symbol normalization, boundary behavior, surfaces, count semantics, or rank order; on any discovered ambiguity R2 must `STOP BEFORE REAL-CASE OUTCOME`. No winner-picking. Property checks in R1-R1 used synthetic strings only; no real-case outcomes were generated or inspected.

## 15. Lifecycle

```
D3.5-A5     = COMPLETE / SELECTIVITY_FANOUT_REDUCED_WITH_RELEVANCE_LOSS      (unchanged)
D3.5-A5-R1  = COMPLETE / SELECTIVITY_RELEVANCE_RETENTION_REPAIR_DESIGN_FROZEN (unchanged; contract narrowed by this repair)
D3.5-A5-R1-R1 = COMPLETE / RELEVANCE_FORMULA_AND_EXACT_MATCH_CONTRACT_REPAIRED
D3.5-A5-R2  = NOT_STARTED / READY_TO_IMPLEMENT
D3.5-A6     = NOT_STARTED / NOT_READY
D4          = NOT_STARTED / BLOCKED
```

R1 remains the parent design decision; R1-R1 is a narrow contract repair. The A5 historical result (records, selected IDs, metrics, verdict) is untouched.

## 16. Exact next task

> **D3.5-A5-R2 — Repaired Selectivity Prototype Freeze & Revalidation** — implement exactly the frozen v2 contract, upgrade the evaluator to complete-universe matching with the four applicability classes, run synthetic tests before real outcomes, freeze the implementation, evaluate exactly one repaired policy on the six frozen cases, preserve the caps, run no admission and no reranker.
