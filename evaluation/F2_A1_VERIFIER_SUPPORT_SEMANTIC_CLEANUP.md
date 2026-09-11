# F2-A1 — Verifier-Support Semantic Cleanup

> **CORRECTION / SUPERSESSION NOTICE (F2-A1-R1).** This report's initial
> terminal `COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED`
> closeout was subsequently found incomplete by an independent post-commit
> audit: the generic lexical identifier/path/symbol coverage branches it
> retained could still override a whole-claim semantic `unsupported` verdict.
> That defect is repaired by `evaluation/F2_A1_R1_VERIFIER_SUPPORT_SEMANTIC_ENTAILMENT_REPAIR.md`
> (F2-A1-R1 = `COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED`), which is
> the authoritative final lifecycle record for this surface. The whitelist and
> comparison-wording removals described below remain valid. The narrative below
> is preserved unchanged for historical transparency.

Status: `COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED`
Type: bounded production implementation + deterministic verification. Zero PANDA
scientific/evaluation calls; zero protected-data access.

Task identity: F2-A1 — Verifier-Support Semantic Cleanup.
Traceability: PF-LR1 Group A / F1 residual R13. The residual identifier R13 is
provenance only, not the task name.

## 1. Starting state

```text
HEAD = c7a1c5ac7cf1c172b261759a422e6c1e224ae21c
       (Reconcile Phase-F scope and establish bounded cleanup plan)
working tree = clean
Phase F = IN_PROGRESS / F1_COMPLETE / PF_LR1_SCOPE_RECONCILED
F1 = COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED
PF-LR1 = COMPLETE / PASS / PHASE_F_SCOPE_RECONCILED_BOUNDED_CLEANUP_PLAN_ESTABLISHED
F2 = NOT_STARTED / UNEXECUTED
F3 = NOT_STARTED / UNEXECUTED
normal default = legacy_question_core
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
default promotion = DEFERRED
```

## 2. Mechanism investigation (before editing)

`deterministically_supported_claims` is produced inside `QAAgent._verify`
(`src/panda_agent/qa.py`) as a per-verify `set[str]` of claim IDs and consumed in
the unsupported-claim loop (`for claim_id in unsupported: if not shadow and
claim_id in deterministically_supported_claims: continue`), which exempts a claim
from the model semantic review's `unsupported_claim_ids` verdict in non-shadow
verification (legacy and `runtime_e1_v2` share this code path; shadow/E1-E2
diagnostic verification never exempts). It is token/string-scoped, not
claim/evidence-scoped, for the branches below. Six add-branches existed:

1. **scope-claim branch** (`scope_<repo>` provenance against locked plan
   versions): generic provenance logic, but **unreachable** — the internal-claim
   filter at the top of `_verify` removes `scope_`-prefixed claims before the
   loop. Left unchanged (dead code, not a benchmark dependency).
2. **identifier/path coverage**: every structured identifier token in the claim
   (repository paths, `::`-qualified, `Pnd`-prefixed) must appear in the cited
   evidence text. Generic claim/evidence coverage invariant — retained.
3. **code-symbol anchor with token whitelist**: cited code repository plus full
   path-token coverage plus any "explicit code token" in the cited text, where
   explicit tokens were `Pnd*`, `contains ::`, capitalized, **or members of the
   hard-coded whitelist `{createLmdFitData, fillData, successfullyPassedFilters,
   GetTubeID, CheckZInfo, Init, Exec}`**. The whitelist is a benchmark-shaped
   token enumeration (the capitalized rule already covers four of its seven
   entries; the three lowercase camelCase entries exist only as known-case
   exceptions). Subsumed by branch 5 for all its other inputs — effectively dead
   beyond the whitelist. **Whitelist removed.**
4. **two-explicit-symbol coverage**: cited code repository plus at least two
   explicit code tokens, all present in the cited text. Live branch whose
   explicit-token set included the same whitelist. **Whitelist removal
   generalizes this branch.**
5. **path coverage over a code repository**: cited code repository plus all
   path tokens present in the cited text. Generic — retained.
6. **comparison-wording branches (two)**: cross-repository citations plus a
   hard-coded contrast-word list (`whereas`, `unlike`, `相比`, `而在`,
   `different implementation`, `multiple repositor`). Case-shaped wording
   triggers (including non-English tokens in the English-only product) whose
   only justification is current benchmark behavior. **Both branches removed.**
   Branch 6a was additionally subsumed by branch 5 (dead for all inputs);
   branch 6b had independent exempting power and is the behaviorally observed
   removal.

## 3. Implementation

Smallest owning-layer repair inside `_verify` (`src/panda_agent/qa.py`):

1. Deleted the hard-coded token whitelist from `explicit_code_tokens`;
   the predicate is now purely shape-based (`Pnd*` prefix, `::` qualifier,
   capitalized identifier) with no enumerated benchmark tokens.
2. Deleted both comparison-wording deterministic-support branches and their
   now-unused local helpers (`cited_paths`, `claim_text_lower`).

Net effect: a claim bypasses ordinary unsupported-claim semantic review only
through generic, evidence-grounded invariants — full structured-identifier
coverage, full path-token coverage over a cited code repository, or multi-symbol
coverage under the shape predicate. Benchmark token enumeration and case-shaped
contrast wording no longer grant support. No replacement whitelist was
introduced; verification is strictly tightened, never weakened.

Files changed:

- `src/panda_agent/qa.py` (−19 lines, two removals, no additions)
- `tests/unit/test_qa.py` (+81 lines: `UnsupportedReviewVertex` double and
  `VerifierSupportSemanticTests` with three contract tests)

## 4. Preservation audit

Unchanged (verified by diff scope and focused tests): citation eligibility,
evidence-version and locator integrity, ordinary unsupported-claim detection,
generic claim sanitization, refusal semantics, answer-point decomposition,
requirement completeness logic (R10 surface untouched —
`_deterministic_missing_requirement_ids` and the pointer predicate have zero
diff), retrieval behavior, evidence selection, public DTOs, prompts, default
routing, runtime mode selection, E3 trigger semantics, retained-support
protections. No R08/R09/R11, R04, R01, R14, F3, D4, or E3 lifecycle surface was
modified. Default runtime and promotion state untouched.

## 5. Verification

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **54 passed,
  2 subtests passed** (includes the three new F2-A1 contract tests:
  generic path-anchor support survives a conservative review; the former
  whitelist tokens no longer grant support; comparison wording no longer grants
  support).
- Shared-verify E3 coupling applied: `_verify` is the shared verification
  surface used by `runtime_e1_v2` second verification, so the authoritative
  focused E3 deterministic set (E3-LR1 §9: 49 focused E3 tests) was run —
  `PYTHONPATH=src python -m pytest tests/unit/test_e3_missing_point_retrieval.py
  tests/unit/test_e2_a1_answer_point_coverage.py -q` → **91 passed** (49 E3 +
  42 neighboring E2-A1 shadow tests). E3 lifecycle was not reopened.
- `git diff --check` PASS; production diff confined to `src/panda_agent/qa.py`.
- PANDA scientific/evaluation calls = 0; PANDA scientific/evaluation tokens = 0.

## 6. Limitations

- The semantic honesty of the retained generic branches (identifier/path
  substring coverage is not entailment) is unchanged by design; further
  tightening of those branches belongs to future separately authorized work.
- The scope-claim support branch remains unreachable dead code (internal-claim
  filtering precedes it); removing it would be unrelated cleanup and was not
  done.
- No scientific evaluation was run or authorized; behavior impact beyond the
  focused deterministic surface is unmeasured by design.

## 7. Lifecycle closeout

```text
F2-A1 = COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED
F2    = IN_PROGRESS / A1_COMPLETE
F3    = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS
normal default = legacy_question_core (unchanged)
default promotion = DEFERRED (unchanged; promotion relevance != promotion authorization)
```

```text
NEXT_TASK_RECOMMENDATION = F2-A2 — Deterministic Completeness Semantic Cleanup
                           (PF-LR1 Group B / F1 residual R10)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
