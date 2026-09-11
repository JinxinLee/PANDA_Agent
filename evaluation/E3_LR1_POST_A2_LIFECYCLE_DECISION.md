# E3-LR1 — Post-A2 Lifecycle Decision and Scope Review

Status: `COMPLETE / PASS / POST_A2_LIFECYCLE_RECONCILED`
Type: static lifecycle / architecture / scope reconciliation. Zero PANDA
scientific/evaluation calls, zero product changes.

## 1. Starting repository state

```text
HEAD = c57ee18626bbadfb8db22f77743a0fd5f1f01e51 (Close E3 A2 targeted recovery validation)
parent = 50eada9 (Preregister E3 A2 targeted recovery validation)
working tree = clean
E3-A2 = COMPLETE / INCONCLUSIVE / INSUFFICIENT_NATURAL_MISSING_POINT_APPLICABILITY
E3    = IN_PROGRESS / A2_COMPLETE_INCONCLUSIVE / PENDING_FUTURE_LIFECYCLE_DECISION
normal default = legacy_question_core
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
```

## 2. Immutable evidence reviewed

`evaluation/E3_A0_MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT.md`,
`evaluation/E3_A1_EXPERIMENTAL_MISSING_POINT_RETRIEVAL_IMPLEMENTATION.md`,
`evaluation/E3_A2_TARGETED_MISSING_POINT_RECOVERY_PROTOCOL.md`,
`evaluation/E3_A2_TARGETED_MISSING_POINT_RECOVERY_VALIDATION.md`,
`evaluation/e3_a2_targeted_recovery_result.json`, `docs/EVALUATION_STATUS.md`,
`docs/GENERALIZATION_ROADMAP.md`, `docs/EVALUATION_POLICY.md`,
`evaluation/F1_RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY.md` (F1-R12/R14), and
current source anchors in `src/panda_agent/qa.py` and
`src/panda_agent/retrieval.py`. A0 PASS, A1 PASS, A2 INCONCLUSIVE are
immutable; A2 is neither PASS nor FAIL and established neither efficacy nor
inefficacy.

## 3. A0/A1/A2 synthesis

A0 established a question-derived trigger/objective contract: a genuine
post-verify semantic answer-point omission is a generic retrieval target, not a
hidden domain requirement, with bounded one-attempt recovery and a
retained-support displacement resolution. A1 implemented it under explicit
`runtime_e1_v2` only, verified by 49 deterministic E3 tests plus neighboring
suites, with public DTO/prompts unchanged. A2 ran the preregistered T2
recovery validation on a mechanically enriched 11-case cohort and obtained 1
applicable case (2 first-missing points) — below the frozen G2 authority
threshold (>=4, >=4) — so the recovery hypothesis was never tested with
authority.

## 4. Architecture / implementation / efficacy separation

- **Q1 architecture justified — yes.** A0 PASS: the trigger and objective are
  derived from the question and runtime coverage state; after E1 (runtime
  answer points) and E2 (claim→point verification) the "verified semantic
  omission" signal is well-defined and distinct from evidence-sufficiency
  failure.
- **Q2 implemented safely and boundedly — yes.** A1 PASS plus the A2
  observation: one post-verify attempt, one revision, no second-E3 loop,
  question-derived objective, original plan/version preservation, global
  reconsideration, retained-support protection, public/default isolation
  (legacy path executes neither capture nor E3). n006 respected all bounds.
- **Q3 standalone recovery benefit — UNRESOLVED /
  INSUFFICIENT_NATURAL_APPLICABILITY.** The A2 scientific question was never
  answerable on the frozen cohort.

The three questions are not collapsed into one label.

## 5. Low-applicability interpretation

The A2 selector was intentionally enriched for exactly the E3-relevant shape
(multi-part, >=2 critical points and evidence groups, non-single-hop or
cross-source/repository). Even so, 10/11 cases produced a fully covering first
semantic verification. The observed rate is 1/11 = 9.1%; no statistical
certainty is claimed from it. Interpretation: on the current exposed
distribution, naturally occurring post-verify semantic omissions on enriched
multi-part questions are rare; the E3 trigger fires rarely and honestly.

## 6. Future-validation feasibility

Exposed novel_dev totals 28 questions; only 11 fall in the enriched stratum
consumed by A2. At the observed rate, a same-pool rerun of all 28 — whose
remaining 17 are a *simpler* distribution (single-hop/single-source, fewer
critical points) — would expect on the order of 1-3 applicable cases, below
G2's >=4 authority threshold, at non-trivial model cost. A same-distribution
rerun is therefore unlikely to be an efficient next step, and no independent
sampling frame of sufficient size exists in exposed data. A genuinely new,
independently curated dataset could accumulate applicability evidence
opportunistically inside broader authorized evaluations; designing or
authorizing such a dataset is out of scope here.

## 7. Outcome-selection-bias analysis

Selecting future cases using known first-verify missing-point outcomes, known
E3 trigger outcomes, known control/treatment outcomes, or known judge
preferences from the same exposed pool would constitute outcome-conditioned
selection. A proposed "first-verify-failure-focused cohort" is precisely that:
it may be useful diagnostically, but it cannot substitute for natural
prospective applicability authority. This distinction is recorded and binding
for future task designs.

## 8. F1-R12 boundary decision (sufficiency routing / `_targeted_retrieve`)

E3 does not depend on F1-R12: the pre-answer loop activates on evidence
sufficiency errors before answer generation, while E3 triggers on verified
semantic answer-point omission after the first verify; their seams, triggers,
and objectives are separate (`qa.py` sufficiency routing vs
`_missing_point_retrieve`). Coexistence is not duplication. F1-R12 does not
block E3 lifecycle closure; ownership remains Phase F / retrieval policy
cleanup; changing it would not require renewed E3 scientific validation
(though shared-node changes must rerun the focused E3 fake tests).

## 9. F1-R14 boundary decision (post-rerank promotion / `select_final_evidence`)

E3's global reconsideration deliberately *reuses* the authoritative selection
(`consolidate_and_select_candidates` → `_prioritize_and_select_evidence` →
`select_final_evidence`, `retrieval.py:2018/1906/678`) instead of a bespoke
selector, per the A1 contract. E3 therefore depends on that policy's behavior
for its reconsideration step, but the pre-existing selection-policy debt is
generic and owned by Phase F / retrieval policy cleanup. F1-R14 does not block
E3 closure. Any future change to shared selection semantics must at minimum
rerun the 49 focused E3 tests; renewed scientific validation would be needed
only if reconsideration semantics change materially.

## 10. Pre-answer targeting vs E3 coexistence

Keeping both is architecturally justified. They operate on different failure
information: pre-answer targeting addresses evidence-sufficiency failure
(missing source types/symbols before generation); E3 addresses verified
semantic answer-point omission after generation and review. This distinction
remains meaningful after E1/E2, which supply the runtime point set and the
verification that detects omissions. Neither subsumes the other; removal of
either would recreate an uncovered failure class.

## 11. E3 maintenance-burden assessment

Meaningful surface: extra `QAState` fields (additive, mode-gated), the opt-in
`capture_candidates` seam, the global consolidation/reselection seam,
the retained-support ledger inside second verify, one routing branch, a compact
E3 trace, and 49 focused deterministic tests. Burden: **MODERATE** — it is not
purely additive because second-verify and selection are shared paths, but all
invariants are deterministic-tested and default-isolated. Against a rare but
potentially important recovery value (a genuine omission on a hard multi-part
question, the exact case where the product would otherwise refuse or answer
incompletely), moderate and isolated burden is proportionate. Rare is not
worthless.

## 12. A2 G6 protocol wording note

The A2 protocol prose contains both "each treatment-only recovery case should
have new evidence" and "G6 fails only if ALL treatment-only recovery cases lack
new evidence"; the frozen scorer implemented the latter. A2 had zero
treatment-only recovery cases, so the ambiguity had no effect on the A2
verdict. Disposition: future protocol-cleanup note only. A2 is not reopened
and not rescored.

## 13. Decision matrix

| Criterion | A: bounded fallback | B: further dedicated validation | C: hold/reconsider |
|---|---|---|---|
| Architectural evidence (Q1) | supported (A0 PASS) | not in question | no concrete conflict found |
| Implementation evidence (Q2) | supported (A1 PASS + bounds observed) | not in question | no defect requiring hold |
| Scientific efficacy evidence (Q3) | honestly unresolved | chasing 2-3 more cases | does not resolve it either |
| Natural applicability | 9.1% observed on enriched stratum; no larger independent frame | requires nonexistent frame / new dataset | unchanged by hold |
| Observed safety | 0 treatment-only regressions; bounds held | unchanged | unchanged |
| Maintenance burden | MODERATE, isolated, tested | unchanged | unchanged |
| Risk of evaluation chasing | low (closes the dedicated track) | high ("inconclusive, rerun larger" is insufficient) | low but indefinite |
| Decision value of more data | low now — no current decision gates on standalone E3 efficacy | low (1-3 more cases, no decision changes) | zero |
| Phase-E compatibility | enables promotion-boundary reconciliation | leaves E3 open with no defined decision | leaves Phase E blocked |

## 14. Selected lifecycle disposition

**OPTION A — close E3 as a bounded low-frequency fallback with efficacy
unresolved.** The anti-activation-chasing principle is decisive: no current
product or lifecycle decision depends on proving standalone E3 efficacy; the
mechanism is implemented, bounded, safe, default-isolated, and rare by nature
of an honest trigger. Dedicated-revalidation criteria V1-V5 all fail (V1: no
decision depends on it; V2/V3: no independent sampling frame of sufficient
size exists; V4: expected information gain does not justify cost; V5: broader
future evaluations would accumulate such evidence anyway). No sample-size
escalation is recommended.

```text
E3-LR1 = COMPLETE / PASS / POST_A2_LIFECYCLE_RECONCILED

E3 = COMPLETE /
     BOUNDED_LOW_FREQUENCY_FALLBACK_IMPLEMENTED /
     SCIENTIFIC_RECOVERY_BENEFIT_UNRESOLVED

DEDICATED_E3_REVALIDATION = NOT_PLANNED /
     LOW_NATURAL_APPLICABILITY_AND_LOW_DECISION_VALUE

FUTURE_E3_EVIDENCE =
     ACCUMULATE_OPPORTUNISTICALLY_IN_BROADER_AUTHORIZED_EVALUATIONS

runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
normal default = legacy_question_core
```

This is not a standalone scientific PASS: the fallback label explicitly
preserves that recovery benefit was never validated.

## 15. Phase-E consequence

With E3 closed as a bounded fallback, Phase E's core mechanisms are
reconciled: E1 validated (shadow scope), E2 core complete with default
promotion deferred, E3 bounded fallback complete with efficacy unresolved. The
remaining Phase-E question is not another E3 experiment but the broader
promotion-boundary reconciliation: whether, under what gates, and for which
components `runtime_e1_v2` (or any Phase-E candidate) ever becomes the default.
E3's inconclusive efficacy is one input to that boundary, not a blocker for
holding it.

## 16. Next-task recommendation

```text
NEXT_TASK_RECOMMENDATION =
Phase-E lifecycle / promotion-boundary reconciliation

NEXT_TASK_EXECUTION_AUTHORIZED = false
```

This follows directly from the selected disposition (§15) and from the E2
promotion-gate redesign already deferred to the Phase-E boundary
(`E2 DEFAULT-PROMOTION GATE REDESIGN = DEFERRED /
REVISIT_AT_PHASE_E_PROMOTION_BOUNDARY`).

## 17. Scientific/model call accounting

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
new QA executions = 0; new retrieval experiments = 0; new embeddings = 0;
new reranker executions = 0; new revisions/reviews = 0; new judges = 0
product files changed = 0
files changed = evaluation/E3_LR1_POST_A2_LIFECYCLE_DECISION.md (new),
docs/EVALUATION_STATUS.md, docs/GENERALIZATION_ROADMAP.md
```
