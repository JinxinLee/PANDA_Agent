# F6-A2-FR2-R1 — Source-Obligation Public-Content and Coverage-Mode Boundary Repair

Decision: **F6-A2-FR2-R1 = COMPLETE / PASS / SOURCE_OBLIGATION_PUBLIC_CONTENT_AND_COVERAGE_BOUNDARIES_REPAIRED.**

Corrected overall state:

```text
F6-A2-FR2 = COMPLETE / PASS / RESIDUAL_PRODUCT_MECHANISMS_RECONCILED_AND_NEW_CANDIDATE_DEVELOPED
Cluster A = REPAIRED   Cluster D = REPAIRED
Cluster B = DEFERRED_NO_SAFE_GENERIC_FIX   Cluster C = DEFERRED_NO_SAFE_GENERIC_FIX
```

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## 1. Starting state

Starting HEAD `223a1e258dabf1a78b6c870fe8fd0ade902d0b30`
("Record F6-A2-FR2 development closeout"); worktree clean. Gold v2.9
(`eaacd3ed…`), calibration v6, selector 59 IDs / `e27ef67a…` verified
unchanged; Gold/evaluator/thresholds untouched.

## 2. Rejected FR2 Cluster-A behavior (why it was removed)

The FR2 `_augment_source_obligation_evidence()` implementation synthesized
public `source_obligation_<type>` claims whose content was provenance
bookkeeping ("The cited paper at <location> documents <subject>.") rather
than substantive user-facing explanation:

1. a source type survived final-evidence projection through that meta-claim
   instead of supporting a substantive answer claim — violating the
   repository principle that provenance/coverage bookkeeping is audit
   material, not user-requested fact;
2. it ran in coverage modes, letting `plan.required_source_types`
   synthesize public content despite the F2-A3-R1 contract that answer-point
   coverage owns completeness there;
3. its classifier recognized only paper/documentation/code, diverging from
   the sufficiency semantics that also recognize readme/workflow kinds.

Per the review, adding `source_obligation_*` to internal claim prefixes was
not an acceptable fix; the mechanism itself was retired.

## 3. Corrected Cluster-A design (legacy requirement contract)

`_augment_source_obligation_evidence()` and the private
`_primary_evidence_source_type()` classifier are removed. Source obligations
remain retrieval/sufficiency state (F2-A5, untouched). The corrected
mechanism uses the existing legacy answer-requirement contract:

- `_answer_requirements(...)` adds, **only when the plan itself is
  multi-source** (`len(required_source_types) >= 2`), the requirement
  `source_role_grounding` with the instruction: ground each part of the
  explanation in the source kind that actually supports it, so every cited
  source backs a substantive, user-relevant part of the answer; do not add
  provenance-only or coverage-only statements merely to mention a source
  kind. The requirement carries `required_source_types` as data.
- `_deterministic_missing_requirement_ids(...)` backstops it: the
  requirement is missing when the cited evidence does not cover every
  required source kind (shared classifier, below). A missing kind routes
  into the existing legacy revision path, where
  `_requirement_evidence` now maps the selected evidence of each required
  kind to the revision payload — the model writes the substantive grounded
  claim and the semantic verifier remains authoritative. No public claim is
  ever synthesized deterministically.
- **Source-type classifier centralized**: new `_evidence_source_types(item)`
  is the exact per-item extraction of the sufficiency classification
  (paper/documentation/code plus readme/workflow/channel additions), and
  `_sufficiency` now consumes it — one classifier, no divergent copies.

Coverage-mode firewall: `model_answer_requirements` stay `[]` in
`shadow_e1_v2` / `runtime_e1_v2` (existing F2-A3-R1 behavior in `_answer`),
and the deterministic backstop is skipped under `_coverage_shadow` in
`_verify` — both covered by regression.

## 4. Cluster-D preservation (unchanged)

`_revise` still drops an identical-normalized-text restatement of a claim
just found unsupported, and passes substantively narrowed revisions. Both
behaviors are regression-locked in `SourceObligationBoundaryTests`
(`test_cluster_d_*`).

## 5. Deferred residuals (unchanged)

```text
Cluster B (g011/g020, pool->final diversity) = DEFERRED_NO_SAFE_GENERIC_FIX
Cluster C (g021, genuine retrieval miss)     = DEFERRED_NO_SAFE_GENERIC_FIX
```

## 6. Product files changed

- `src/panda_agent/qa.py`: augment retirement; `_answer_requirements` gains
  `source_role_grounding` (multi-source plans only) and returns
  `list[dict[str, Any]]`; `_deterministic_missing_requirement_ids` gains the
  citation-coverage backstop branch; `_requirement_evidence` maps required
  kinds' selected evidence for revision; `_evidence_source_types` shared
  classifier with `_sufficiency` refactored onto it. No prompt change; no
  retrieval change; no evaluator change.
- `tests/unit/test_qa.py`: `ResidualRepairTests` augment tests replaced;
  new `SourceObligationBoundaryTests` (legacy/coverage prompt boundary,
  provenance-only prohibition, deterministic backstop positive + control,
  Cluster-D preservation); pre-existing workflow and requirement-anchor
  assertions adapted to the new requirement.

## 7. Focused verification

Red before green: the four boundary tests failed while the augment
mechanism was still in place (requirement absent); coverage-mode firewall
tests stayed green throughout (the pre-existing filter). Final:
`test_qa.py` + `test_retrieval.py` **274 passed + 52 subtests**;
QAAgent-dependent suites show exactly the pre-existing baseline failures
(19 d4_a5 + 5 e2/e1) — zero new regressions.

## 8. Integrity

```text
Gold changes = 0; evaluator changes = 0; threshold changes = 0
prompts.py changes = 0
Gold scientific runs = 0; novel_dev access = 0; novel_validation access = 0
holdout access = 0; protected-content leakage = 0
novel_validation = PRISTINE_FOR_CURRENT_LINEAGE
```

## 9. New candidate development state

```text
NEW_CANDIDATE_DEVELOPMENT_HEAD = d323f790655c62e18b782d606a02f593a673f3cd
("Repair FR2 source obligation boundaries")
candidate frozen = false
Attempt 3 preregistered = false
Attempt 3 executed = false
```

## 10. Next action

```text
NEXT_TASK_RECOMMENDATION =
F6-A ATTEMPT 3 / NEW CANDIDATE PREREGISTRATION AND FREEZE
(bound to m6-benchmark-v2.9 and calibration v6)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
