# D3.5-A5-R2 — Repaired Selectivity Prototype Freeze & Revalidation

## 1. Executive verdict

**`PASS / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT`.** The single preregistered repaired deterministic relevance policy (`d3_5_selectivity_v2`) was implemented exactly per the frozen R1/R1-R1 contract and revalidated over the six frozen A2 development cases. **Every preregistered PASS condition holds**: the A5 v1 relevance loss is repaired — `prod_sim_hvmaps.C` (g021.e1), lost under v1's coarse path/title score, is now retained — with zero `GATE_RECALL_LIMITATION`, zero `APPLICABLE_AND_LOST`, fan-out still bounded (62→4, 67→8), graph displacement unchanged from v1, controls fail-closed, and deterministic double-execution on every case.

| Case | Eligible | Gate-passing | V1 selected | V2 selected | Origins after | V1 disp. | V2 disp. | Required-evidence applicability | Retained |
|---|---|---|---|---|---|---|---|---|---|
| g036 | 3 | 3 | 3 | 3 | 2 | 0 | 0 | e1 APPLICABLE_AND_RETAINED | YES (ana_dpm.C) |
| g021 | 62 | 35 | 4 | **4** | 1 | 0 | 0 | e1 **APPLICABLE_AND_RETAINED**; e2 NOT_APPLICABLE | **YES (prod_sim_hvmaps.C)** |
| n006 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | NOT_APPLICABLE ×2 | — |
| g041 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | NOT_APPLICABLE | — |
| g020 | 67 | 67 | 8 | 8 | 7→**2** | 8 | 8 | e1 APPLICABLE_AND_RETAINED (newly visible); e2 NOT_APPLICABLE | YES |
| n004 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | NOT_APPLICABLE | — |

`D3.5-A5-R2 = COMPLETE / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT`; `D3.5-A6 = NOT_STARTED / READY_FOR_PREREGISTRATION` (preregistration first; not started here); `D4 = NOT_STARTED / BLOCKED`. No model calls, no admission, no DB/Qdrant writes, production runtime unchanged.

## 2. Frozen R1/R1-R1 contract

`R1_DESIGN_DECISION = REPAIR_WITH_HIGHER_RESOLUTION_DETERMINISTIC_RELEVANCE` (R1, commit `240cfe0…`) + `R1_R1_DECISION = RELEVANCE_FORMULA_AND_EXACT_MATCH_CONTRACT_REPAIRED` (R1-R1, commit `e445f14…`). R2 implemented the contract with **zero scientific discretion**: hard filters unchanged (governance universe, plan scope, `MIN_PRIMARY_SCORE ≥ 1` v1 path/title gate); PRIMARY_RANK lexicographic (symbol_exact_tier → rarity_weighted_overlap with the repaired non-negative universe-local IDF → basename_coverage → text_presence); support secondary; distance/object-id tie-breakers; caps 4/8; least-used-origin attribution; fail-closed.

## 3. Optional fixture extension

Required and performed (Commit `3db1aaa`, `D3_5_A5_R2_FIXTURE_EXTENSION_COMMIT`): the six cases' selectors use `object_type`/`symbol`/`title_contains`-via-`section_path`, so the fixture (schema 1.0.0 → 1.1.0) additively gained `object_type` and the full frozen `locator` on eligible candidate entries and payload-registry entries, read mechanically from the frozen normalized corpus. Preservation verified: candidate universe/IDs/orderings/payload text/source-version identity/provenance origins and all pre-existing fields identical; no gold labels or annotations added.

## 4. v2 implementation

`evaluation/scripts/d3_5_a5_r2_selectivity.py` (new versioned surface; the A5 v1 implementation is untouched). Rank keys per candidate: `symbol_exact_tier` (compound plan-symbol boundary-aware match in basename/path/text, title excluded), `rarity_weighted_overlap` (`idf(t)=log2((|U|+1)/(df+1))`, df over the scope-filtered eligible universe's deduplicated lexical views), `basename_coverage`, `text_presence`; then `support_rank` (missing worse, never disqualifying), `structural_distance`, `object_id`. Caps and attribution exactly as frozen.

## 5. Evaluator implementation

`evaluate_complete_universe` reuses the frozen `GoldEvidenceSelector.matches` semantics over the **complete pre-cap eligible universe** and classifies each required-evidence group: `NOT_APPLICABLE_TO_SELECTIVITY` (no universe match), `GATE_RECALL_LIMITATION` (matched but all gate-rejected), `APPLICABLE_AND_RETAINED`, `APPLICABLE_AND_LOST`. It also reports `NEWLY_VISIBLE_COMPLETE_UNIVERSE_APPLICABLE_EVIDENCE` — required candidates the old A2 combined-pool evaluator could not see. Expected evidence is read only after selection outputs are frozen and never enters the scorer.

## 6. Pre-outcome freeze

Phase sequence held: fixture extension commit `3db1aaa` → implementation + evaluator + preregistration + synthetic tests committed at `f498714` (`D3_5_A5_R2_IMPLEMENTATION_FREEZE_COMMIT`) with `real_case_outcomes_seen_before_freeze = false`.

> **R2-R1 correction (2026-09-01):** outcome exposure began at the **first failed replay invocation**, not at the first successful replay — the frozen harness at `f498714` runs `select_v2` twice per case before the evaluator, so the first failed invocation had already executed the repaired scorer on real frozen case g036 (twice, deterministic comparison completed) before its evaluator failed. Exact chronology: **invocation A** (at the original freeze commit `c4aebd8`) — `select_v2` ×2 on g036, determinism comparison completed, crashed at determinism-receipt construction (`NameError: hashlib`); evaluator never started. **Invocation B** (at the amended freeze `f498714`) — `select_v2` ×2 on g036, determinism completed, evaluator started (selector matching for g036 completed in memory), crashed at `newly_visible` (`NameError: a2_matched` — missing evaluator parameter wiring). **Invocation C** — full success (6/6 cases persisted). Accounting: `COMPLETED_FORMAL_R2_CASE_TREATMENTS = 6`; `FAILED_PRE_COMPLETION_REAL_CASE_INVOCATIONS = 2` (4 discarded `select_v2` executions, all g036); `TREATMENT_EXECUTION_EXPOSURE` began at invocation A, while `PERSISTED_RESULT_EXPOSURE` and `HUMAN_RESULT_INSPECTION` began only after invocation C — no persisted or human-inspected case result existed before the evaluator wiring repair. The wiring repair is therefore a **post-exposure infrastructure/evaluator-plumbing repair** (not pre-exposure) with `POST_EXPOSURE_SCORER_MUTATIONS = 0` and `POST_EXPOSURE_APPLICABILITY_SEMANTIC_MUTATIONS = 0`: `select_v2` is byte-identical (sha256 `272546df…`) and `src/panda_agent/evaluation.py` (`GoldEvidenceSelector.matches`) byte-identical (sha256 `0017367e…`) across `c4aebd8`/`f498714`/`2bddbbc`; the `c4aebd8 → f498714` amendment is exactly one non-semantic module-level line (`import hashlib`); the `f498714 → 2bddbbc` diff touches only the evaluator parameter wiring and the newly-visible diagnostic enablement. `R2_RERUN_REQUIRED = false`. Full audit: `evaluation/d3_5_a5_r2_r1_outcome_exposure_evaluator_wiring_audit_repair.json`.

## 7. Anti-tuning audit

`NUMBER_OF_R2_REPAIRED_POLICIES_IMPLEMENTED = 1`; `EVALUATED = 1`; `REAL_CASE_OUTCOMES_SEEN_BEFORE_IMPLEMENTATION_FREEZE = 0`; `POLICY_MUTATIONS_AFTER_OUTCOME_EXPOSURE = 0`; `EXPECTED_EVIDENCE_USED_BY_SCORER = 0`; `CASE_ID_USED_BY_SCORER = 0`; `CASE_ROLE_USED_BY_SCORER = 0`; `FILE_TYPE_SPECIAL_CASES = 0`; `CAP_CHANGES = 0`; `GATE_CHANGES = 0`. Static isolation check: the v2 selection implementation accesses no required-evidence/gold/role fields; case_id is a record key only. The post-freeze evaluator parameter-wiring repair (NameError before any output) affects only the newly-visible discovery record — `select_v2` is untouched between the freeze commit and the results.

## 8. Six-case replay

Deterministic double-execution replay of the six frozen cases; byte-identical outputs per case (`determinism_receipts` with SHA-256 in the machine artifact). No analyzer/embedding/reranker/QA/verifier/judge calls; `A5_R2_ADMISSION_TREATMENT_RUNS = 0`.

## 9. v1 vs v2

g036: same 3 selected IDs (ana_dpm.C, prod_aod_complete.C, pid_complete.C). g021: same count (4), different composition — `prod_sim_hvmaps.C` enters, three low-discrimination README chunks leave. g020: same count (8), different composition; displacement identical (8). Controls identical (0). v2 graph displacement equals v1 in every case (0/0/0/0/8/0) and never exceeds the pre-selectivity bridge footprint.

## 10. g036

`ana_dpm.C` (object.5cae2ceab6e67bb4c9065331): in the eligible universe ✓, passes the unchanged gate ✓, retained by v2 ✓ (`APPLICABLE_AND_RETAINED`). All 3 eligible candidates selected; bridge-only candidates (no non-graph support) win on primary levels alone.

## 11. g021

- **e1 / `prod_sim_hvmaps.C`**: eligible ✓, passes the gate ✓ (path_overlap 1 via "target", title_overlap 1), **retained ✓** — `symbol_exact_tier = 1` (the frozen plan symbol `restgas_profile` occurs literally in its bounded text: the configuration key the macro passes to `PndMasterRunSim`) and `rarity_weighted_overlap = 8.532` rank it second inside the single-origin cap. The A5 v1 loss is repaired by exactly the mechanism R1 identified: higher-resolution deterministic signals, not budget relaxation.
- **e2 / `pgenerators/Target/PndTargetGenerator.cxx`**: `NOT_APPLICABLE_TO_SELECTIVITY` — genuinely absent from the complete eligible universe (its provenance-bearing edge originates from a non-seed object). Not collapsed with e1.

## 12. Complete-universe applicability discoveries

**`NEWLY_VISIBLE_COMPLETE_UNIVERSE_APPLICABLE_EVIDENCE`: 1** — g020.e1's required `readme_section` (object.e29c4fcd17107cabea45f18e, `macro/target/README.md`, "POCA Workflow") exists in the complete eligible universe but was invisible to A5's combined-pool-based evaluator; under v2 it is ranked first and **retained**. This is an evaluator-coverage discovery, not a new runtime candidate.

## 13. g020

67 eligible → 67 gate-passing → 8 selected (caps respected); origins 7→2 under v2 attribution (4+4 to the two top origins — within the frozen per-origin ceiling, more concentrated than v1's six-origin spread; reported honestly as an attribution-distribution difference); graph displacement 8 (v1: 8). No case-specific logic anywhere.

## 14. Other controls

n006/g041/n004: complete eligible universes remain empty → selected 0, displacement 0 — any selected candidate would have been an invariant failure.

## 15. Fan-out

High-fan-out behavior remains bounded by the frozen caps (g021 62→4; g020 67→8); zero-eligible controls remain zero. The bounded architecture validated by A5 is preserved.

## 16. Graph displacement

v2 displacement equals v1 displacement in every case (0, 0, 0, 0, 8, 0) and never exceeds the pre-selectivity bridge footprint. Reported per case with v1/v2/pre-selectivity values; no relevance-vs-displacement tradeoff was hidden (g020's origin concentration shift is documented in §13).

## 17. Relevance retention

All required bridge evidence that is present in the complete eligible universe **and** passes the unchanged hard gate is retained: g036.e1, g021.e1, g020.e1 — `APPLICABLE_AND_RETAINED` 3/3 applicable groups; `APPLICABLE_AND_LOST` 0; `GATE_RECALL_LIMITATION` 0.

## 18. Gate-recall diagnostics

`GATE_RECALL_LIMITATION` count: **0**. The unchanged `MIN_PRIMARY_SCORE ≥ 1` path/title gate rejected no required-evidence candidate present in the complete universe, so the gate-design concern raised in R1-R1 did not materialize on these cases.

## 19. Determinism

Byte-identical double execution on all six cases, with SHA-256 output receipts recorded per case.

## 20. What R2 validates

The repaired v2 policy preserves A5's bounded fan-out architecture (caps, attribution, fail-closed controls, determinism) while restoring complete-universe relevance retention for all applicable governed bridge evidence that reaches the unchanged gate — including the g021 loss that motivated the repair and a newly visible g020 requirement.

## 21. What R2 does not validate

Final-answer retrieval recovery (no reranker/selector ran); the admission budgets {2, 3}; reranker-variance handling; anything beyond the six exposed development cases (this is `POST_OUTCOME_MECHANISTIC_DEVELOPMENT`, not a fresh holdout).

## 22. A6 readiness

**`NOT_STARTED / READY_FOR_PREREGISTRATION`.** A6 must first preregister: K=2/K=3 arms, decision semantics between them, the R1 symmetric reranker repetition count, symmetric baseline/treatment execution, control material-regression handling, and reranker stochastic-variance accounting. R2 made none of these decisions.

## 23. Lifecycle

```
D3.5-A5       = COMPLETE / SELECTIVITY_FANOUT_REDUCED_WITH_RELEVANCE_LOSS
D3.5-A5-R1    = COMPLETE / SELECTIVITY_RELEVANCE_RETENTION_REPAIR_DESIGN_FROZEN
D3.5-A5-R1-R1 = COMPLETE / RELEVANCE_FORMULA_AND_EXACT_MATCH_CONTRACT_REPAIRED
D3.5-A5-R2    = COMPLETE / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT
D3.5          = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN
D3.5-A6       = NOT_STARTED / READY_FOR_PREREGISTRATION
D4            = NOT_STARTED / BLOCKED
```

## 24. Exact next task

> **D3.5-A6 — Bounded Rerank-Admission Prototype & Paired Replay Validation** — preregistration first (K=2/K=3 arms and decision semantics, R1 repetition count, symmetric execution, control-regression handling, variance accounting); no reranker outcome before that preregistration is frozen.
