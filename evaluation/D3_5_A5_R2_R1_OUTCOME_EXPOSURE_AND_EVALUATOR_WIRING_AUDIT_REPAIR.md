# D3.5-A5-R2-R1 — Outcome-Exposure & Evaluator-Wiring Audit Repair

## 1. Executive audit decision

**`R2_R1_DECISION = OUTCOME_EXPOSURE_AND_EVALUATOR_WIRING_AUDIT_REPAIRED`.** The audit defect was in exposure accounting, not in the science: the repaired scorer had already executed on a real frozen case during two failed invocations before the successful six-case replay, so treatment-execution exposure began earlier than the R2 record stated. The post-exposure repair (evaluator parameter wiring) is proven result-neutral — `select_v2` and the applicability semantics are byte-identical across all three relevant commits. `R2_EXECUTION_AUDIT_STATUS = PASS_WITH_AUDIT_REPAIR`; the scientific verdict `REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT` is unchanged; `R2_RERUN_REQUIRED = false`.

## 2. Frozen R2 scientific result

`D3.5-A5-R2 = COMPLETE / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT` (result commit `2bddbbc…`). All scientific outputs preserved byte-for-byte: six-case selected IDs, rank keys, gate counts, fan-out counts, graph displacement, applicability classes, the newly-visible complete-universe discovery, determinism receipts, governance/scope invariants.

## 3. Audit issue

The R2 record stated outcome exposure began at the first **successful** replay. Under the frozen R2 definition (exposure begins when the repaired scorer runs on any real frozen case — even if described as debug/smoke/dry-run), the first **failed** replay invocation had already executed `select_v2` on real case g036, so exposure began earlier. Classification: protocol-accounting defect only; no evidence of multiple policies, outcome-guided mutation, gold leakage, cap/gate mutation, or case-specific rules.

## 4. Original exposure wording

"started at: first successful six-case replay after the freeze commit" — incorrect under the frozen exposure definition.

## 5. Actual first failed invocation sequence

Verified from the frozen harness at `f498714` (identical order at `c4aebd8`) and the recorded tracebacks. The harness per case: `first = select_v2(...)` → `second = select_v2(...)` → determinism comparison → determinism receipt (hashlib) → `evaluate_complete_universe(...)`.

- **Invocation A** (original freeze `c4aebd8`): `select_v2` ×2 on g036 → determinism comparison completed → **crashed at determinism-receipt construction** (`NameError: hashlib`). Evaluator never started. `POST_EXPOSURE_SCORER_MUTATIONS`-relevant: the amendment that followed added exactly one module-level line (`import hashlib`).
- **Invocation B** (amended freeze `f498714`): `select_v2` ×2 on g036 → determinism completed → receipt built → **evaluator started**: selector matching for g036 completed in memory → **crashed at `newly_visible = sorted(matched_universe_ids - a2_matched)`** (`NameError: a2_matched` — missing evaluator parameter wiring). Evaluator not completed.
- **Invocation C** (after the wiring repair): full success — 6/6 cases, results persisted, summary printed.

Both failed invocations are recorded with actual values: two failed invocations (not one), four discarded `select_v2` executions (2 + 2), all on g036.

## 6. Corrected exposure semantics

`R2_REPAIRED_SELECTIVITY_OUTCOME_EXPOSURE.started_at = FIRST_FAILED_REAL_CASE_INVOCATION` (invocation A). Meaning: **scientific treatment execution had begun** — not that human result interpretation had begun.

## 7. Treatment execution vs persisted output

| Exposure layer | Began at |
|---|---|
| `TREATMENT_EXECUTION_EXPOSURE` | Invocation A (first `select_v2` execution on g036) |
| `PERSISTED_RESULT_EXPOSURE` | Invocation C (successful replay wrote results) |
| `HUMAN_RESULT_INSPECTION` | After invocation C |

No persisted or human-inspected case result existed before the evaluator wiring repair.

## 8. Pre-exposure stdlib repair — corrected classification

R1's expectation that the `hashlib` import repair was pre-exposure is **corrected by repository evidence**: invocation A had already executed `select_v2` on g036 before the import fix. The repair is therefore recorded as post-treatment-execution-exposure (after invocation A) but pre-evaluator-execution and pre-invocation-B. Its diff scope is exactly one non-semantic module-level line (`import hashlib`; the `c4aebd8 → f498714` diff is solely that line) — `select_v2` byte-identical across all three versions (sha256 `272546df…`).

## 9. Post-exposure evaluator wiring repair

The `a2_matched_ids` repair (after invocation B, before invocation C): `evaluate_complete_universe` gains the parameter; `newly_visible` uses it; the harness constructs the frozen A2 combined-pool matched-ID reference from `a2_prov` and passes it; the output field `_a2_match_provenance_reference` becomes `a2_combined_pool_matched_reference` (sorted ID list).

## 10. Scorer immutability audit

`POST_EXPOSURE_SCORER_MUTATIONS = 0`. Verified byte-identical across `c4aebd8`/`f498714`/`2bddbbc`: `select_v2` (sha256 `272546df…`), tokenizer, `symbol_exact_match`, candidate lexical view, IDF formula, rank key order, hard gate, `support_rank` semantics, origin attribution, `PER_ORIGIN_CAP`, `SELECTIVITY_CAP`, graph merge semantics.

## 11. Applicability semantics audit

> **R2-R1-R1 provenance clarification (2026-09-01):** the pre-amend implementation-freeze identity `c4aebd84eb91a7a316c9f84e94eaeffb5d1e83a7` referenced above is a **local pre-amend Git object** — no local or remote branch contains it and it is not an ancestor of `origin/main`, so a fresh clone cannot `git show` it. The audit evidence at repair time was nevertheless sufficient: the amended freeze `f498714` and the result implementation `2bddbbc` are reachable, the R2-R1 artifact records the extracted-region identity checks, and the post-freeze evaluator-wiring diff is preserved. This does not invalidate the R2 scientific result or the result-neutrality conclusion.

`POST_EXPOSURE_APPLICABILITY_SEMANTIC_MUTATIONS = 0`. `GoldEvidenceSelector.matches` (in `src/panda_agent/evaluation.py`, sha256 `0017367e…`) and the universe construction, gate-passing calculation, retained calculation, and all four applicability-class rules are unchanged across all three versions.

## 12. Newly-visible diagnostic role

The repaired `a2_matched_ids` parameter is used **only** to determine `newly_visible_complete_universe_applicable_evidence` — a diagnostic comparison against old A2 combined-pool visibility. It does not control which candidates are required evidence, which pass the gate, which are retained, or the applicability class. Verified from the `f498714 → 2bddbbc` diff (the parameter appears only in the `newly_visible` expression and its harness plumbing).

## 13. Formal run accounting

`COMPLETED_FORMAL_R2_CASE_TREATMENTS = 6` (12 low-level deterministic `select_v2` executions — double execution per case); `FAILED_PRE_COMPLETION_REAL_CASE_INVOCATIONS = 2`; `REAL_CASE_SELECT_V2_EXECUTIONS_IN_FAILED_INVOCATIONS = 4` (2 per failed invocation, all g036, all discarded). Formal completed cases are not conflated with low-level scorer calls.

## 14. Why R2 is not rerun

`R2_RERUN_REQUIRED = false`: outcomes are already exposed; the scorer did not mutate; the scientific result can be audited from persisted output; rerunning cannot restore an unbiased pre-exposure boundary. Rerunning for cosmetic cleanliness is prohibited. R2 remains `POST_OUTCOME_MECHANISTIC_DEVELOPMENT`, not fresh unbiased validation.

## 15. g020 origin concentration

g020: 67 eligible, 8 selected, graph displacement 8, `PER_ORIGIN_CAP` respected — but the selected provenance distribution changed: v1 origins after = 6, v2 origins after = 2 (attributed 4 + 4). This is **not an R2 failure**; it is an A6 admission-design diagnostic requirement (origin concentration at the rerank-admission boundary). Selectivity diversity is not changed now: least-used-origin attribution, `PER_ORIGIN_CAP = 4`, `SELECTIVITY_CAP = 8`, and v2 scoring stand; A6 measures downstream concentration first. No numeric concentration-failure threshold is derived from g020's 2-origin/4+4 outcome.

## 16. A6 diagnostic implications

A6 preregistration must record: `selected_bridge_origin_count`, `selected_bridge_per_origin_counts`, `reserved_bridge_origin_count`, `reserved_bridge_per_origin_counts`, `ordinary_rerank_candidates_displaced`, `reserved_bridge_candidate_ids`, `reserved_candidate_origin_ids` — to detect rerank-admission budget monopolization by a small number of provenance origins without a case-specific g020 rule. A6 must also preregister (per A4/R1): the K=2/K=3 arms and their interpretation, the reranker repetition count, symmetric baseline/treatment execution, variance accounting, control material-regression handling, and displacement semantics.

## 17. Lifecycle

```
D3.5-A5       = COMPLETE / SELECTIVITY_FANOUT_REDUCED_WITH_RELEVANCE_LOSS
D3.5-A5-R1    = COMPLETE / SELECTIVITY_RELEVANCE_RETENTION_REPAIR_DESIGN_FROZEN
D3.5-A5-R1-R1 = COMPLETE / RELEVANCE_FORMULA_AND_EXACT_MATCH_CONTRACT_REPAIRED
D3.5-A5-R2    = COMPLETE / REPAIRED_SELECTIVITY_RELEVANCE_RETENTION_VALIDATED_FOR_DEVELOPMENT
D3.5-A5-R2-R1 = COMPLETE / OUTCOME_EXPOSURE_AND_EVALUATOR_WIRING_AUDIT_REPAIRED
D3.5          = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN
D3.5-A6       = NOT_STARTED / READY_FOR_PREREGISTRATION
D4            = NOT_STARTED / BLOCKED
```

## 18. Exact next task

> **D3.5-A6 — Bounded Rerank-Admission Prototype & Paired Replay Validation** — design/preregistration only as the next step (K=2/K=3 arms and decision semantics, R1 repetition count, symmetric execution, control material-regression handling, displacement semantics, origin-concentration diagnostics); no reranker outcome before that preregistration is frozen.
