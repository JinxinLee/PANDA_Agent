# PE-LR1 — Phase-E Lifecycle and Promotion-Boundary Reconciliation

Status: `COMPLETE / PASS / PHASE_E_CLOSED_PROMOTION_DEFERRED_UNTIL_MATERIAL_CANDIDATE`
Type: static lifecycle / architecture / promotion-boundary decision. Zero PANDA
scientific/evaluation calls; zero product changes.

## 1. Starting repository state

```text
HEAD = 71e886181cda5a6b20122be4e3ec8e7643ab190a (Correct E3 LR1 lifecycle wording)
working tree = clean
E1 = COMPLETE / PASS / QUESTION_ONLY_SEMANTIC_ANSWER_POINT_DECOMPOSITION_VALIDATED
E2 = COMPLETE / CORE_MECHANISM_VALIDATED / DEFAULT_PROMOTION_DEFERRED
E3 = COMPLETE / BOUNDED_LOW_FREQUENCY_FALLBACK_IMPLEMENTED / SCIENTIFIC_RECOVERY_BENEFIT_UNRESOLVED
Phase E = IN_PROGRESS / E3_FALLBACK_COMPLETE / PROMOTION_BOUNDARY_RECONCILIATION_NEXT
normal default = legacy_question_core
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
E2 DEFAULT PROMOTION = DEFERRED / ACTIVATION_ACCEPTANCE_NOT_MET
E2 DEFAULT-PROMOTION GATE REDESIGN = DEFERRED / REVISIT_AT_PHASE_E_PROMOTION_BOUNDARY
```

## 2. Immutable evidence reviewed

`docs/EVALUATION_STATUS.md`, `docs/GENERALIZATION_ROADMAP.md`,
`docs/EVALUATION_POLICY.md` (T4/T5 boundaries), the E2 activation lineage
(`E2_A3_RUNTIME_ACTIVATION_REGRESSION.md`, `E2_A3_R1...`,
`E2_A3_R2...`, `E2_A3_R3...`, `E2_A3_R3_R1_INFRASTRUCTURE_RECOVERY.md`,
`E2_A3_R3_R1_G11_FAILURE_REVIEW.md`), `E2_POST_A3_LIFECYCLE_RECONCILIATION.md`,
the E3 record (A0/A1/A2/E3-LR1), `F1_RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY.md`,
and current source (`qa.py` mode definitions, `retrieval.py` selection).

## 3. P1 — Phase-E architecture completion: YES

The intended Phase-E capabilities exist with accepted lifecycle dispositions:

- **E1** question-only semantic decomposition: implemented (shadow seam) and
  validated (E1-R2 PASS; E1-C1 real-style confirmation PASS).
- **E2** claim → answer-point → evidence accountability, missing-point
  detection, bounded revision: implemented and core-validated (E2-A1/A2 PASS;
  R2 repair validated); lifecycle reconciled by E2-LR1.
- **E3** bounded post-verify recovery fallback: implemented under explicit
  runtime_e1_v2; lifecycle closed by E3-LR1 as a bounded low-frequency
  fallback with efficacy unresolved.

F1-R08/R09/R11 (compatibility contract, requirement-evidence derivation,
planned-locator/dataflow augmentation) are active mechanisms that E1/E2
validation ran *with*; they are part of the validated architecture's
environment, not missing architecture. They do not block Phase-E completion
(see §9).

Architecture completion is a separate question from default activation.

## 4. P2 — Experimental-path validity: YES

`runtime_e1_v2` remains a legitimate, explicitly selected experimental path
for development and authorized evaluation (`VALIDATED_EXPERIMENTAL_PATH /
EXPLICIT_SELECTION_ONLY`). Its single prospective use under preregistration
(E3-A2) executed with intact boundaries. This is independent of P3.

## 5. P3 — Normal-default promotion now: NO

The historical activation failures are binding evidence and are not waived:

```text
E2-A3      = COMPLETE / FAIL / Q7          (new runtime verifier integrity category, g112)
E2-A3-R1   = COMPLETE / FAIL / P2_P6
E2-A3-R2   = COMPLETE / PASS (repair validated only)
E2-A3-R3   = COMPLETE / INCONCLUSIVE (connection timeout / provider 429)
E2-A3-R3-R1= COMPLETE / FAIL / G11         (quality: 1 better, 11 equivalent, 2 worse)
```

A materially changed runtime candidate does exist after `fd0aed4`: E3-A1
introduced real runtime behavior under `runtime_e1_v2` (post-verify
missing-point retrieval, cross-pass candidate reconsideration, global rerank,
authoritative evidence reselection, a retained-support ledger, and new
routing/state/trace semantics), and QA-M1 made a small generic sanitizer
repair (E2-LR1 explicitly non-activation). However, a material runtime change
is not the same as a promotion-relevant material improvement: E3 does not
repair, invalidate, or directly resolve the historical E2 default-activation
failure surface (Q7/P2_P6/G11 verifier and review semantics); it is a rare
post-verify fallback; its standalone recovery efficacy remains unresolved (a
single descriptive case); and no current product decision depends on immediate
default promotion. Another immediate promotion experiment therefore still
lacks sufficient decision value. Architectural completion is not a waiver.
Promotion now = no.

## 6. P4 — Future-reconsideration trigger

```text
DEFAULT_PROMOTION_RECONSIDERATION_TRIGGER =

  a promotion-relevant materially behavior-changing post-Phase-E candidate,
  meaning a materially behavior-changing candidate that either:

  1. materially affects the unresolved default-promotion failure surface —
     completeness, verification, compatibility, evidence-selection, or other
     behavior implicated in the failed activation lineage — normally via
     Phase-F compatibility / benchmark-dependency cleanup (notably the
     E1_E2_COMPATIBILITY cluster F1-R08/R09/R11, verifier-support semantics
     F1-R13, deterministic-requirement semantics F1-R10, selection policy
     F1-R14, or refusal-path F1-R04) or another independently justified
     architecture change;

  OR

  2. otherwise creates a decision-relevant new integrated runtime candidate
     whose default acceptance needs to be assessed;

  OR

  3. an explicitly authorized release/acceptance candidate evaluation (T4/T5
     boundary) whose scope requires deciding the normal default.
```

Examples that MAY satisfy the trigger: substantial replacement/retirement of
the R08/R09/R11 compatibility behavior; material verifier-support changes
(R13); material deterministic-completeness changes (R10); material
evidence-selection changes (R14); other independently justified integrated
runtime redesign. Not sufficient by themselves: E3 lifecycle closure itself, a
rare bounded fallback that does not address the failed activation surface,
elapsed time, rerunning the same exposed cases, increasing sample size to
chase activation, minor sanitizer maintenance, documentation-only changes.

## 7. E2 activation-history synthesis

The activation lineage tested one integrated runtime candidate (`fd0aed4`)
against the legacy default. Q7 was a new runtime verifier integrity category
(repaired and validated as R2 for citation eligibility); P2/P6 persisted after
the identifier-normalization repair; the R3-R1 recovery established a complete
14-pair quality surface with two noncritical worse cases, failing the frozen
zero-worse gate G11. The G11 review narrowly justified a generic sanitizer
product repair (executed as QA-M1) and a prospective gate redesign, while
leaving R3-R1 permanently FAIL. E2-LR1 separated mechanism completion from
default acceptance. This boundary inherits that separation: the mechanism is
done; the acceptance question is evidence-bound and currently unmet.

## 8. E3 lifecycle implication

E3 is closed as a bounded low-frequency fallback (SCIENTIFIC_RECOVERY_BENEFIT
_UNRESOLVED; DEDICATED_E3_REVALIDATION = NOT_PLANNED). Its unresolved efficacy
is one input to any future promotion decision, not a blocker for Phase-E
closure and not a reason to reopen E3. E3's runtime-only integration means a
future promotion decision inherits E3 behavior as part of the coupled mode
(see §11).

## 9. F1 R08/R09/R11 compatibility analysis

| Item | Blocks Phase-E completion? | Blocks default promotion? | Owner | Removal creates promotion-relevant material candidate? |
|---|---|---|---|---|
| F1-R08 `_answer_requirements` compatibility contract | no | contributes-but-not-sole-blocker | Phase F | yes (part of cluster) |
| F1-R09 requirement-evidence / deterministic missing requirements | no | contributes-but-not-sole-blocker | Phase F | yes (part of cluster) |
| F1-R11 planned-locators / dataflow augmentation | no | contributes-but-not-sole-blocker | Phase F | yes (part of cluster) |

All three are MEDIUM E1_E2_COMPATIBILITY rows: active in both modes, validated
alongside E1/E2, with accepted compatibility rationale. They do not block
Phase-E completion. For promotion they are part of the benchmark-shaped risk
surface of the *same candidate* that failed the activation lineage — historical
failures remain the binding evidence, so they contribute but are not the sole
blocker. Future replacement/retirement of this cluster would change runtime
behavior materially and is precisely the kind of change that reopens promotion
(§6). Ownership remains Phase F; nothing is modified here.

## 10. Relevant Phase-F material-candidate analysis

F1 findings whose future repair/retirement could create a promotion-relevant
materially changed runtime candidate (i.e., reopen promotion under §6):

```text
F1-R08/R09/R11  E1_E2_COMPATIBILITY cluster (generation/review/revision contract)
F1-R13          deterministically_supported_claims verifier-support override (HIGH, F2)
F1-R10          pointer_identifier_normalization deterministic requirements (HIGH, F2)
F1-R14          post-rerank promotion / select_final_evidence policy (E3 boundary; Phase F)
F1-R04          exact negative-control refusal path (HIGH, F2)
```

Not material to promotion by themselves: F1-R05/R06 (localized finalize
fallbacks, F3), F1-R15 (HOLD), F1-R12 (reconciled in E3-LR1; a material
pre-answer-retrieval change must assess E3 interaction in that change's own
broader validation). F1-R01 (benchmark-derived per-intent required_sources,
HIGH) remains the fourth F2 candidate and must stay inside Phase-F scope
reconciliation even if it is not currently classified among the strongest
promotion-material candidates — a prioritization consideration for the future
scope reconciliation, not a reclassification. Phase F is not a blanket
blocker: a small unrelated Phase-F cleanup does not reopen promotion; a
significant replacement of compatibility/completeness/verifier behavior does.

## 11. Component-wise promotion analysis

Current source (`qa.py`): `_ANSWER_POINT_MODES = {"legacy_question_core",
"shadow_e1_v2", "runtime_e1_v2"}` — one mode switch selects decomposition
(E1), answer-point coverage verification semantics (E2), and E3 eligibility
together; legacy mode uses the single `question_core` point and the legacy
review/revision path (which already has the one-bounded-revision behavior).

- E1-only default: not supported without a new mode variant / product change;
  and E1 points alone do not change answer behavior, so it is not
  decision-relevant.
- E2-without-E3 default: not supported without a product change; and the
  historical failures (Q7, P2/P6, G11) attach to exactly this integrated
  runtime verify/revision semantics, so a partial variant would still be an
  activation experiment on a new candidate.
- E3-disabled default: trivially true today (trigger rarely fires and is
  mode-gated), but there is no explicit switch; E3 is part of the coupled mode.
- `runtime_e1_v2` is a coupled runtime mode. Independent component promotion
  is not currently supported by the architecture; inventing partial-promotion
  options would require product changes and has no decision relevance now.

## 12. Phase-E decision matrix

| Criterion | A: complete, promotion deferred | B: remain open for promotion task | C: hold/reopen |
|---|---|---|---|
| E1 architecture completion | complete (R2/C1 PASS) | no open E1 task exists | n/a |
| E2 core-mechanism completion | complete (E2-LR1 separation) | no open E2 task exists | n/a |
| E2 default-activation evidence | unmet, preserved | would require a new gate → gate chasing risk | n/a |
| E3 lifecycle completion | closed (bounded fallback) | closed | closed |
| Remaining benchmark-shaped compatibility | owned by Phase F (R08/R09/R11 cluster) | same | same |
| Current runtime candidate identity | materially changed from `fd0aed4` by E3-A1, but the E3 change is not promotion-relevant to the unresolved historical activation failure surface | same | same |
| Need for additional scientific evidence | none for closure; promotion evidence only via a promotion-relevant material candidate | yes — but no promotion-relevant candidate exists | n/a |
| Risk of activation chasing | low (closes the phase) | high ("stay open and rerun") | low |
| Ownership of remaining work | Phase F (already inventoried) | blurs Phase-E/Phase-F boundary | n/a |

**Selected: OPTION A.** No concrete unresolved Phase-E task exists; the only
open question (default promotion) is evidence-bound, belongs to a future
material-candidate or release boundary, and B would re-create the activation
chasing that E2-LR1 stopped.

## 13. Promotion D1/D2/D3 decision matrix

| Criterion | D1: promote now | D2: new immediate promotion experiment | D3: defer until promotion-relevant material candidate |
|---|---|---|---|
| Waives E2-A3/R3-R1 failures? | would have to — no defensible standard is met | n/a (new experiment ≠ waiver; requires a promotion-relevant new candidate) | no waiver; failures remain binding |
| Materially changed runtime candidate exists? | yes (E3-A1), but not promotion-relevant to the failed surface | yes as a runtime change; not promotion-relevant to the failed activation surface | n/a — trigger requires a promotion-relevant material change |
| Current product decision depends on promotion? | no | no | n/a |
| Proportionate information gain? | negative (chasing) | low: the current candidate is materially changed by E3, but the change does not target the historical activation failure surface, its standalone benefit remains unresolved and low-frequency, and no current product decision requires immediate promotion | high when trigger fires |
| Consistent with anti-activation-chasing rule | no | no | yes |

**Selected: D3.**

## 14. Selected Phase-E lifecycle disposition

```text
Phase E = COMPLETE /
          CORE_ANSWER_GENERALIZATION_ARCHITECTURE_RECONCILED /
          DEFAULT_PROMOTION_DEFERRED

normal default = legacy_question_core
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
E2 DEFAULT PROMOTION = DEFERRED / ACTIVATION_ACCEPTANCE_NOT_MET
```

This asserts Phase-E work is complete; it does not assert runtime_e1_v2
production acceptance, release acceptance, or generalization.

## 15. Selected default-promotion disposition

```text
DEFAULT_PROMOTION DISPOSITION =
D3 — DEFER UNTIL PROMOTION-RELEVANT MATERIAL CANDIDATE CHANGE

E2 DEFAULT-PROMOTION GATE REDESIGN =
CLOSED / NO_IMMEDIATE_REVALIDATION_DEFINED /
REOPEN_ONLY_FOR_PROMOTION_RELEVANT_MATERIAL_CANDIDATE_OR_RELEASE_BOUNDARY
```

Core meaning: promotion remains deferred; no immediate promotion experiment is
justified; reconsideration requires a decision-relevant candidate change
(§6 trigger) or an explicit release/acceptance boundary.

The G11 review's prospective "gate redesign justified" is thereby retired as a
standing obligation: no redesigned gate is defined now, the historical
prospectively-proposed gate ideas remain non-active, and any future activation
experiment must be justified under the §6 trigger with its own preregistered
design. This retires the deferred line without altering any historical E2
outcome.

## 16. Next-task ownership

```text
NEXT_TASK_RECOMMENDATION =
Phase-F scope reconciliation and bounded benchmark-dependency cleanup planning
(F2 candidates F1-R01/R04/R10/R13 — R01 included per the authoritative F1
inventory even if less promotion-relevant — plus the R08/R09/R11
E1_E2_COMPATIBILITY cluster and the F1-R14 shared-selection / E3-boundary
item; F3/D4 residual ownership folded into the same scope reconciliation)

NEXT_TASK_EXECUTION_AUTHORIZED = false
```

The specific unresolved boundary: F1 established the inventory and candidate
owners, but F2 scope (which candidates are treated, in what order — notably
the HIGH verifier-support override F1-R13), F3 scope (partially superseded by
D4), and paused D4 reconciliation are undecided; that reconciliation is the
most coherent next planning task and is the natural producer of the §6
promotion-relevant material candidate.

## 17. Scientific/model call accounting

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
QA executions = 0; retrieval experiments = 0; embeddings = 0; reranker = 0;
review/revision = 0; judges = 0
product files changed = 0
files changed = evaluation/PE_LR1_PHASE_E_PROMOTION_BOUNDARY_RECONCILIATION.md
(new), docs/EVALUATION_STATUS.md, docs/GENERALIZATION_ROADMAP.md
```

Release-boundary note: this decision is not T4/T5 and performs no release
acceptance; conversely, a future explicitly authorized release evaluation may
supply promotion evidence under §6 without resurrecting the E2 activation
lineage.
