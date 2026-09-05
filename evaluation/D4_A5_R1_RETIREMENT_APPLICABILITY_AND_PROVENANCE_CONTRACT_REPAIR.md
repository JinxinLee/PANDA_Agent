# D4-A5-R1 — Retirement Applicability and Provenance-Contract Repair

Status: `COMPLETE / PASS / RETIREMENT_APPLICABILITY_CONTRACT_REPAIRED`
Date: 2026-09-05
Parent commit: `dc679f880cda8d2ccdfb709d725e24673c562eab` (`D4-A5 record pre-outcome provenance gate stop`)
R1 commit: `D4-A5-R1 repair retirement applicability contract`

R1 is a **pre-retrieval contract + persistence repair only**. It performs zero
provider calls, zero retrieval, zero reacquisition, and zero production changes.
A future D4-A5 continuation still requires separate authorization.

---

## 1. Why the original STOP was correct

The first D4-A5 execution attempt stopped during Phase P, after 6 Analyzer calls
were consumed and before any embedding/reranker call, any paired retrieval, any
scientific metric, any per-rule disposition, and any Batch2 production
activation. Under the frozen D4-A4 contract
(`component_provenance_subtraction_contract.pre_outcome_gate`:
"absent expected contribution ... is INVALID before downstream calls") the
fail-closed stop was the correct outcome. R1 does **not** rewrite that verdict:
`INVALID / BATCH2_PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED` remains the
historical, immutable result of the first attempt
(`evaluation/d4_a5_result.json`, untouched).

## 2. The defect: configured component ≠ active runtime contribution

D4-A4 statically selected `model_factory_theory` with retirement components
`model/PndLmdDPMAngModel1D.cxx`, `model/PndLmdDPMAngModel2D.cxx`,
`model/PndLmdModelFactory.cxx`, and the paper-page hint
`pflueger_2017: [51, 57, 65]`. Production `analyze()` applies the generic
policy:

```python
if intent not in {"algorithm_theory", "algorithm_implementation"}:
    paper_page_hints = {}
```

so a locator configured on a **matched** query-expansion rule is not necessarily
an **active contribution** in the final canonical RetrievalPlan. The first
prospective n014 plan did not contain the selected-rule `pflueger_2017`
page-hint contributions. The original contract incorrectly treated the absence
of any frozen configured component as protocol-invalid, which made the
experiment non-constructible for deterministic runtime-policy drops.

## 3. Why production Analyzer behavior is not modified

The current production system is the object being evaluated. R1 does not touch
`src/panda_agent/retrieval.py`, `src/panda_agent/config.py`,
`src/panda_agent/d3_structured.py`, or `configs/query_expansions.yaml`; it does
not broaden page-hint retention, force `algorithm_theory`, special-case n014,
or force `model_factory_theory` page hints into the plan. The experiment adapts
its applicability semantics to real production behavior — never the reverse.

## 4. Component-level applicability (the repair)

Every configured retirement-mask component of a matched selected Batch-2 rule
is classified — by **selected-rule origin in the contribution ledger, never by
raw token presence** — into exactly one of:

- **`ACTIVE_IDENTIFIABLE`** — the selected rule contributed the exact component
  to the final canonical plan with unambiguous provenance; it is removable while
  preserving independent origins; scientifically testable in this plan.
- **`INACTIVE_NOT_IDENTIFIABLE`** — the selected rule did not contribute the
  component to the final plan after normal production plan construction (the
  plan is the unmodified production output, so the absence is a deterministic
  consequence of normal plan formation). This is not protocol-invalid, not
  dependency observed, and not retirement validated: **RETIREMENT EFFECT NOT
  IDENTIFIABLE FOR THIS COMPONENT IN THIS PLAN**. A token present only through
  independent origins leaves the selected-rule component INACTIVE while the
  token itself stays active and untouched.
- **`AMBIGUOUS_INVALID`** — the component appears but selected-rule ownership
  cannot be determined, provenance is contradictory/incomplete, or treatment
  construction would require guessing or global deletion. Fail-closed.

Per-component receipts record: rule ID, kind, exact value, configured-in-frozen-
mask flag, selected-rule origin presence, independent origins, canonical-plan
presence, applicability status, retirement projection action, hold reason
(inactive), ambiguity reason (invalid). The logic is fully generic — no case-id
or component-value shortcuts (enforced by source-scan test `test_r1_26`).

## 5. Per-rule implications

Repaired disposition precedence:

1. `INVALID_PROTOCOL` — ambiguous provenance, malformed input, plan inequality,
   projection drift, impossible attribution.
2. `DEPENDENCY_OBSERVED_RETAIN` — any attributable T/F loss from removal of the
   rule's ACTIVE_IDENTIFIABLE contribution set; takes precedence over baseline
   incompleteness for another group.
3. `INCONCLUSIVE_BASELINE_NOT_REPRODUCED` — no attributable loss, baseline
   missing.
4. `INCONCLUSIVE_NO_ACTIVE_RETIREMENT_COMPONENT` — protocol valid, baseline
   reproduced, zero frozen components ACTIVE (nothing was tested).
5. `PARTIAL_RETIREMENT_VALIDATED_COMPONENT_HOLD` — protocol valid, baseline
   reproduced, no loss, ≥1 ACTIVE and ≥1 INACTIVE; the full frozen mask is NOT
   validated; `validated_active_components` and `held_inactive_components` are
   recorded separately and never collapsed into one boolean.
6. `RETIREMENT_VALIDATED` — only when ALL frozen components are
   ACTIVE_IDENTIFIABLE, baseline reproduced, no attributable loss, protocol
   valid.

An inactive component is never automatically safe to retire: it never counts
toward `RETIREMENT_VALIDATED`, the successful-retirement numerator, the
dependency-removal numerator, or production retirement eligibility. It remains
HOLD unless a later prospective case naturally activates it or a separately
governed lifecycle resolves it.

## 6. Repaired batch verdict truth space (7 levels)

| Level | Verdict | Trigger |
|---|---|---|
| 1 | `INVALID / BATCH2_PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED` | any protocol/provenance/shared-plan/input defect |
| 2 | `INCONCLUSIVE / BATCH2_REFERENCE_BASELINE_NOT_REPRODUCED` | active direct-rule baseline not reproduced |
| 3 | `PARTIAL / SOME_RETIREMENT_CANDIDATES_RETAIN_DEPENDENCY` | ≥1 rule DEPENDENCY, no Level-4 violation |
| 4 | `FAIL / BATCH2_CRITICAL_OR_GROUNDING_REGRESSION` | any safety regression; wins over Level 3 |
| 5 | `PARTIAL / RETIREMENT_COMPONENT_APPLICABILITY_INCOMPLETE` | ≥1 rule NO_ACTIVE_COMPONENT or PARTIAL_..._HOLD |
| 6 | `PARTIAL / BATCH2_AGGREGATE_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE` | all rules fully validated, a metric tolerance fails |
| 7 | `PASS / SECOND_BATCH_LOW_RISK_RETIREMENT_VALIDATED` | 3/3 RETIREMENT_VALIDATED + zero safety + six thresholds pass |

Evaluation order L1 → L2 → L4 → L3 → L5 → L6 → L7; exhaustively tested with no
undefined state (`test_r1_21`: 216 disposition combinations × safety × metrics,
plus the full `classify_rule_r1` input space). Future full PASS requires every
frozen mask component ACTIVE — any held inactive component forbids full PASS.

## 7. What did NOT change

The 3 selected rules; the original A4 configured masks (including
`pflueger_2017: [51, 57, 65]` — removing it because n014's first plan lacked it
would be outcome-tailored mask editing and is prohibited); the 7-case cohort;
active direct cases; control cases; evidence groups and denominators; the six
primary metrics and thresholds (-0.05/-0.05/-0.05/-0.05/-0.05/0.0); MRR as
diagnostic-only; Batch1 invariant; the no-Batch2-replacement design; pair
phenotype definitions; safety gates.

## 8. Persistence repair

The first attempt consumed an n014 Analyzer call but lost its token accounting
and full plan because the applicability gate terminated before durable
persistence. The repaired Phase P now, for every acquisition: (1) captures
provider accounting immediately after the single Analyzer call; (2) builds the
canonical plan, serialization, signature, matched rules, full ordered
contribution ledger, provenance origin receipts, component applicability
receipts, and (when constructible) both execution projections; (3) **durably
writes the complete record before any gate evaluation**; (4) only then
evaluates the gate — a `GATE_STOPPED_AMBIGUOUS_INVALID` stop retains the full
record and consumed-cost evidence
(`evaluation/d4_a5_continuation_raw_prospective_plans.json` + continuation
manifest). Implementation reuses the existing manifest/raw-artifact pattern; no
scheduler, workflow engine, resume framework, or transaction framework.
Behaviorally verified by `test_r1_27_28` and `test_r1_27b`.

## 9. First-attempt plan reusability audit

Mechanical audit of the immutable stopped manifest
(`evaluation/d4_a5_execution_manifest.json` at `dc679f8`), checking for each
case whether all eight required artifacts (canonical plan, serialization,
ledger, origin provenance, both projections, signature, provider accounting)
are durably recoverable without any provider call:

| Case | Previous state | Persisted | Classification |
|---|---|---|---|
| g052 | COMPLETED | status/token/attempts/plan_signature/timestamps | `HISTORICAL_ATTEMPT_NOT_REUSABLE` |
| g055 | COMPLETED | same slot-level bookkeeping | `HISTORICAL_ATTEMPT_NOT_REUSABLE` |
| n003 | COMPLETED | same slot-level bookkeeping | `HISTORICAL_ATTEMPT_NOT_REUSABLE` |
| n004 | COMPLETED | same slot-level bookkeeping | `HISTORICAL_ATTEMPT_NOT_REUSABLE` |
| g007 | COMPLETED | same slot-level bookkeeping | `HISTORICAL_ATTEMPT_NOT_REUSABLE` |
| n014 | FAILED | stop receipt only; tokens unknown | `HISTORICAL_ATTEMPT_NOT_REUSABLE` |
| g060 | NOT_EXECUTED | nothing | `NEVER_EXECUTED` |

No raw plans artifact was ever committed. A `plan_signature` alone never
satisfies the reuse contract (`test_r1_29_30`).

## 10. Future minimum-affected continuation policy

R1 performs zero reacquisition. A future separately authorized D4-A5
continuation must reuse every plan classified
`REUSABLE_FROZEN_SCIENTIFIC_PLAN` (currently none exist), reacquire only
`HISTORICAL_ATTEMPT_NOT_REUSABLE` or never-executed cases, and never redraw a
reusable frozen plan or select plans by semantic quality or expected outcome.
Because no valid frozen 7-plan scientific artifact exists, the continuation may
explicitly authorize a fresh complete 7-plan acquisition under the repaired
contract; that is not an outcome-improvement rerun.

## 11. Historical cost accounting

The first failed attempt consumed 6 Analyzer logical calls, 6 provider attempts,
0 retries, and at least 10,303 recorded tokens, plus one n014 call whose token
usage remains explicitly unknown. These counts are preserved
(`HISTORICAL_ATTEMPT_ACCOUNTING`) and never overwritten: future reporting keeps
historical-attempt cost, continuation-attempt cost, and cumulative cost
separate, with unknown components remaining explicitly unknown.

## 12. R1 boundary and verification

Zero exposure: Analyzer 0, embedding 0, reranker 0, QA/verifier/judge 0,
retrieval 0, benchmark/novel runs 0, DB/Qdrant writes 0, protected access 0; no
provider smoke tests. Focused verification: 86 tests passing (31 added for R1),
compile/static checks, JSON parse, source-scan for outcome-specific shortcuts,
Git blob identity for production and historical artifacts, `git diff --check`,
clean worktree.

## 13. Lifecycle state

```text
D4-A5 FIRST ATTEMPT      HISTORICAL / INVALID / PRE-OUTCOME STOP (preserved)
D4-A5-R1                 COMPLETE / PASS / RETIREMENT_APPLICABILITY_CONTRACT_REPAIRED
D4-A5                    BLOCKED / READY_FOR_SEPARATELY_AUTHORIZED_CONTINUATION
BATCH1                   ACTIVE
BATCH2                   SELECTED / FROZEN / NOT YET SCIENTIFICALLY VALIDATED
BATCH2 PRODUCTION        false
D4-A6                    NOT_STARTED
```

R1 does not claim any scientific validation of Batch 2 has completed. A5
continuation requires separate authorization.
