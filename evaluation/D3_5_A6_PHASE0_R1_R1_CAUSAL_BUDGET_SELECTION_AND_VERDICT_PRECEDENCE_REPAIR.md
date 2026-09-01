# D3.5-A6 Phase 0-R1-R1 — Causal Budget Selection & Verdict Precedence Repair

## 1. Executive decision

**`A6_PHASE0_R1_R1_DECISION = CAUSAL_BUDGET_SELECTION_AND_VERDICT_PRECEDENCE_REPAIRED`.** The three remaining decision-contract defects are completely repaired and the A6 preregistration is now finalized: budget selection embeds the causal witness (`CAUSAL_DELTA_K` / `MECHANISTIC_SAFE_EFFECTIVE`), stable pool-perturbation recovery has its own PARTIAL verdict, and `MATERIAL_CONTROL_REGRESSION` is explicitly a scientific budget-safety outcome rather than a FAIL trigger. This was an extremely narrow decision-contract repair: no Phase-1 implementation, no real treatment pools, no `select_v2`, no reranker, no new scientific outcome; `evaluation/scripts/`, `src/`, `configs/`, and the replay fixture unchanged.

## 2. Parent Phase0-R1 state

Phase 0-R1 (commit `84f218b`) repaired the replay surfaces (Repair A), the broad benefit/safety populations and incremental metrics (Repair B), and the authoritative BASELINE graph channel (Repair C). `RERANK_POOL_SIZE = 30`, `ADMISSION_BUDGET_CANDIDATES = [2, 3]`, the three arms, 3 repetitions, the cyclic schedule, `STABLE_RETAINED >= 2/3`, the material-regression rule, `ADMISSION_APPLICABLE_BRIDGE_GROUP`, `DELTA_2`/`DELTA_3`, `REGRESSION_2`/`REGRESSION_3`, the reserved-required-candidate witness, origin-concentration diagnostic-only status, `A6_RERANK_OUTCOME_EXPOSURE = NOT_STARTED`, and `D4 = BLOCKED` are all accepted and unchanged.

## 3. Remaining causal-selection defect

The Phase0-R1 selector used `SAFE_EFFECTIVE(K) = DELTA_K > 0 AND REGRESSION_K == 0`, while mechanistic PASS separately required a stable reserved-required-candidate witness. A budget could therefore be **selected first and then fail the causal PASS gate** even when the other budget would have satisfied the mechanistic causal criterion (e.g., K2 with a causally witnessed recovery versus K3 with a larger but noncausal `DELTA_K`). A second residual issue: stable pool-perturbation recovery without a reserved-required-candidate witness had no precise final verdict. A third: `MATERIAL_CONTROL_REGRESSION` was not explicitly separated from FAIL-level structural invariant failures, and the Phase-0 FAIL trigger "systematic control degradation" was ambiguous.

## 4. DELTA_K vs CAUSAL_DELTA_K

- `DELTA_K` (unchanged): number of `ADMISSION_APPLICABLE_BRIDGE_GROUP`s `STABLE_RETAINED` under treatment K and **not** under BASELINE — stable downstream recovery after admission-induced pool perturbation.
- `CAUSAL_DELTA_K` (new, primary mechanistic benefit metric): the number of admission-applicable groups satisfying **both** (1) the `DELTA_K` condition and (2) `STABLE_RESERVED_REQUIRED_WITNESS` under treatment K — stable incremental admission recovery with a stable actually-reserved required-candidate witness.
- Invariant: `0 <= CAUSAL_DELTA_K <= DELTA_K`. The two are never conflated.
- `CAUSAL_DELTA_2` / `CAUSAL_DELTA_3` are frozen as the primary benefit counts; `DELTA_2` / `DELTA_3` remain important pool-level diagnostics and are not deleted.
- `NONCAUSAL_STABLE_DELTA_K = DELTA_K − CAUSAL_DELTA_K` — diagnostic only; never used to claim direct bridge-admission recovery; no runtime effect.

## 5. Stable reserved-required witness

`RESERVED_REQUIRED_CANDIDATE_RETAINED` (per admission-applicable group / treatment repetition: final evidence contains a required-evidence matching candidate that actually consumed a reserved slot in that treatment arm) and `STABLE_RESERVED_REQUIRED_WITNESS` (retained in ≥ 2/3 repetitions) keep their Phase0-R1 definitions — the change is that the witness now feeds `CAUSAL_DELTA_K` and therefore **budget eligibility itself**, instead of being checked only after budget selection.

## 6. MECHANISTIC_SAFE_EFFECTIVE

`MECHANISTIC_SAFE_EFFECTIVE(K) = CAUSAL_DELTA_K > 0 AND REGRESSION_K == 0` replaces `SAFE_EFFECTIVE(K) = DELTA_K > 0 AND REGRESSION_K == 0` as the PASS budget criterion; the older rule is marked superseded for PASS selection and retained as a broader diagnostic. If `CAUSAL_DELTA_K > 0` but `REGRESSION_K > 0`, the budget is **not** eligible — safety still precedes budget minimality.

## 7. Corrected K2/K3 hierarchy

```
if K2 is MECHANISTIC_SAFE_EFFECTIVE and K3 is MECHANISTIC_SAFE_EFFECTIVE:
    SELECTED_ADMISSION_BUDGET = 3 if CAUSAL_DELTA_3 > CAUSAL_DELTA_2 else 2
elif K2 is MECHANISTIC_SAFE_EFFECTIVE:
    SELECTED_ADMISSION_BUDGET = 2
elif K3 is MECHANISTIC_SAFE_EFFECTIVE:
    SELECTED_ADMISSION_BUDGET = 3
else:
    no budget is selected as PASS
```

`DEFAULT_BUDGET_PRINCIPLE = smallest sufficient causally witnessed safe budget` — not the smallest budget and not the largest-`DELTA_K` budget. K3 beats K2 only on causal benefit; a pure increase in `DELTA_K`, median rank, MRR-like diagnostics, or `NONCAUSAL_STABLE_DELTA_K` can never by itself justify K3. The budget is never chosen from positive-case identity.

## 8. Stable pool-perturbation recovery

New verdict class **`PARTIAL / POOL_PERTURBATION_ASSOCIATED_RECOVERY_WITHOUT_RESERVED_WITNESS`**, used when there exists at least one budget K with `DELTA_K > 0` and `REGRESSION_K == 0` but, for every safe budget, `CAUSAL_DELTA_K == 0`. Interpretation: the admission-modified rerank pools produced stable downstream recovery, but the experiment did not validate that an actually reserved required bridge candidate carried it — scientifically stronger than "no downstream recovery" but weaker than mechanistic PASS. The `POOL_PERTURBATION_ASSOCIATED_RECOVERY` diagnostic is preserved with the added relationship: `DELTA_K > CAUSAL_DELTA_K` means the difference is stable pool-level recovery not backed by a stable witness (no runtime effect).

## 9. Material regression classification

**`MATERIAL_CONTROL_REGRESSION` IS A SCIENTIFIC BUDGET-SAFETY OUTCOME.** It is not, by itself, a FAIL-level structural invariant failure: a treatment may produce material control regression while the experiment remains valid and interpretable. Such results are handled through `REGRESSION_K`, `MECHANISTIC_SAFE_EFFECTIVE`, and `PARTIAL / ADMISSION_RECOVERY_WITH_CONTROL_REGRESSION`. The regression rule (`BASELINE retention_count >= 2 AND treatment retention_count <= 1`) and `REGRESSION_2`/`REGRESSION_3` are unchanged; no new numeric threshold.

## 10. Narrow FAIL semantics

FAIL is relabeled **`FAIL / BOUNDED_ADMISSION_CONSTRUCTION_OR_AUTHORITY_FAILED`** (previous label `BOUNDED_ADMISSION_SAFETY_OR_CONSTRUCTION_FAILED`, narrowed) and applies to structural/protocol implementation failures only: pool-size invariant failure; duplicate-admission accounting failure; out-of-scope candidate admission; candidate-authority violation; reserved-slot accounting violation; post-rerank replay parity failure discovered after implementation freeze; implementation not matching preregistration; other deterministic construction/authority invariant failures. Ordinary `MATERIAL_CONTROL_REGRESSION` groups are never automatic FAIL triggers; the Phase-0 "systematic control degradation" trigger is removed with the explicit clarification above and no new numeric "systematic" threshold.

## 11. Total verdict precedence

```
1. INVALID
2. FAIL / BOUNDED_ADMISSION_CONSTRUCTION_OR_AUTHORITY_FAILED
   (structural construction / authority / implementation invariant failure)
3. PASS / BOUNDED_RERANK_ADMISSION_VALIDATED_FOR_DEVELOPMENT
   if at least one MECHANISTIC_SAFE_EFFECTIVE budget exists
4. PARTIAL / ADMISSION_RECOVERY_WITH_CONTROL_REGRESSION
   if stable DELTA_K > 0 exists but every stable-recovery budget is unsafe
5. PARTIAL / POOL_PERTURBATION_ASSOCIATED_RECOVERY_WITHOUT_RESERVED_WITNESS
   if at least one safe budget has DELTA_K > 0 but no safe budget has CAUSAL_DELTA_K > 0
6. PARTIAL / ADMISSION_RECOVERY_NOT_STABLE_ACROSS_RERANKER_REPETITIONS
   if DELTA_2 = DELTA_3 = 0 but UNSTABLE_ADMISSION_RECOVERY exists
7. PARTIAL / ADMISSION_DID_NOT_VALIDATE_DOWNSTREAM_RECOVERY otherwise
```

Total and non-overlapping with no outcome-dependent label selection ("safe" in levels 4–5 means `REGRESSION_K == 0`). PARTIAL scopes are now exact: recovery-with-regression = exists K with `DELTA_K > 0` and every `DELTA_K > 0` budget has `REGRESSION_K > 0` (causal or noncausal); not-stable = only when `DELTA_2 = DELTA_3 = 0` with `UNSTABLE_ADMISSION_RECOVERY`; no-recovery = the true residual class. PASS requires: protocol valid; construction invariants pass; at least one MECHANISTIC_SAFE_EFFECTIVE budget; budget chosen by the frozen causal-safe hierarchy; selected budget with `REGRESSION_K = 0` and `CAUSAL_DELTA_K > 0`; no runtime gold/case-role leakage; no post-exposure treatment mutation. The witness is **not** separately re-required after selection — it is embedded in `CAUSAL_DELTA_K`.

## 12. Synthetic edge-case examples

Static truth-table checks (design-only, no real case data, no treatment pools, no model calls) verified every listed case maps to exactly one final verdict and, where PASS is possible, exactly one selected budget:

| Synthetic case | Result |
|---|---|
| K2 causal-safe, K3 higher `DELTA_3` but noncausal | PASS, budget **2** |
| K2 unsafe, K3 causal-safe | PASS, budget **3** |
| both causal-safe, `CAUSAL_DELTA_2 == CAUSAL_DELTA_3` | PASS, budget **2** |
| both causal-safe, `CAUSAL_DELTA_3 > CAUSAL_DELTA_2` | PASS, budget **3** |
| stable safe `DELTA_K` but `CAUSAL_DELTA_K = 0` | PARTIAL / POOL_PERTURBATION_ASSOCIATED_RECOVERY_WITHOUT_RESERVED_WITNESS |
| stable recovery only under unsafe arms | PARTIAL / ADMISSION_RECOVERY_WITH_CONTROL_REGRESSION |
| no stable delta but isolated treatment recovery | PARTIAL / ADMISSION_RECOVERY_NOT_STABLE_ACROSS_RERANKER_REPETITIONS |
| no stable or unstable recovery | PARTIAL / ADMISSION_DID_NOT_VALIDATE_DOWNSTREAM_RECOVERY |
| structural invariant failure | FAIL / BOUNDED_ADMISSION_CONSTRUCTION_OR_AUTHORITY_FAILED (precedence over all outcome classes) |

The Phase 0-R1-R1 task card's critical example (K2: `DELTA_2=1, CAUSAL_DELTA_2=1, REGRESSION_2=0`; K3: `DELTA_3=2, CAUSAL_DELTA_3=0, REGRESSION_3=0` → budget **2**) is frozen in the preregistration and covered by the first row.

## 13. Preserved contracts

Repair A (replay surfaces, full selector-visible text, complete universe, materialization gate, parity target) and Repair C (`A6_BASELINE_GRAPH_CHANNEL_AUTHORITY`, `PHASE1_SELECT_V2_RUNS = 0`, double-merge prohibition, parity-check-only reconstruction) are unchanged and closed. `ADMISSION_APPLICABLE_BRIDGE_GROUP`, the safety population, `DELTA_K`, `REGRESSION_K`, the witness definitions, and the full Phase-0 broad architecture are unchanged. Protected datasets remain `novel_validation = FROZEN / UNSEEN`, `novel_holdout = SEALED / UNSEEN`.

## 14. Lifecycle

```
D3.5-A6              = IN_PROGRESS / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FINALIZED
D3.5-A6-PHASE0       = COMPLETE / BOUNDED_RERANK_ADMISSION_PREREGISTRATION_FINALIZED
D3.5-A6-PHASE0-R1    = COMPLETE / REPLAY_SURFACE_AND_BUDGET_DECISION_CONTRACT_REPAIRED
D3.5-A6-PHASE0-R1-R1 = COMPLETE / CAUSAL_BUDGET_SELECTION_AND_VERDICT_PRECEDENCE_REPAIRED
D3.5-A6-PHASE1       = NOT_STARTED / READY_TO_IMPLEMENT
D3.5-A6-PHASE2       = NOT_STARTED / BLOCKED_UNTIL_PHASE1_FREEZE
D3.5                 = IN_PROGRESS / POST_A2_SELECTIVITY_AND_ADMISSION_REDESIGN (unchanged)
D4                   = NOT_STARTED / BLOCKED
```

## 15. Exact next stage

> **D3.5-A6 Phase 1 — Bounded Admission Prototype & Synthetic Construction Freeze** — may materialize the complete replay surface mechanically, extend replay metadata generically, implement deterministic pool construction, post-rerank replay logic, diagnostics, synthetic/parity tests, and the formal runner skeleton, with `REAL_CASE_RERANKER_CALLS = 0` and `PHASE1_SELECT_V2_RUNS = 0` throughout and the complete-replay-surface gate passed before implementation freeze.
