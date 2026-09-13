# F6-A-FR1 — Exposed Gold Failure Review & New Candidate Development

Decision: **F6-A-FR1 = COMPLETE / PASS / ROOT_CAUSES_ESTABLISHED_AND_BOUNDED_FIXES_IMPLEMENTED.**

Development task (zero scientific-evaluation-call). This is NOT an F6-A rerun,
a candidate freeze, a preregistration, or a release evaluation. F6-A remains
COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED.

```text
PANDA scientific/evaluation calls (FR1) = 0
PANDA scientific/evaluation tokens (FR1) = 0
```

## 1. Starting state

- Starting HEAD: `557327e3923b0c0f074ec32812928c1b5bdc1797`
  ("Complete F6-A per-intent denominator reporting") — matched the expected
  baseline; worktree clean.

## 2. Exposed cases reviewed

All eight authorized status-mismatch cases were inventoried at case level
before any code change (Stage R0): g005, g012, g013, g026, g027, g034, g059,
g060 — six Gold-ANSWERED → insufficient_evidence false refusals and two Gold
VERSION_CONFLICT mismatches (g012 → insufficient_evidence, g026 → answered).
Full inventory and per-case evidence: `evaluation/F6_A_FR1_EXPOSED_GOLD_FAILURE_REVIEW.md`
(+ JSON companion `evaluation/f6_a_fr1_exposed_gold_failure_review.json`).

## 3. Root causes (2 generic classes explain all 8 cases and all 9 failed gates)

- **RC1 — repository display names treated as requested bare class symbols**
  (g005/g013/g027/g034/g059/g060). Compound-cased repository display names
  ("PandaRoot", "LuminosityFit", "RestgasDetermination") are extracted by
  `_requested_bare_class_symbols` under request/definition context terms, but
  the locked object catalog (symbols/paths/class declarations) has no reason
  to contain repository identities, so `_answerability_guard` refused with
  "unsupported requested symbol". The analyzer had already classified the
  same token as a repository reference (`manifest_repo_id`) — two product
  authorities disagreed. Downstream symptoms: 6 status mismatches, evidence/
  coverage misses, dual-source g060 failure, and all 4 contradictions + the
  1 major unsupported claim (refusal text vs cited in-repository evidence).
- **RC2 — prepositional commit requests never reach version-conflict
  detection** (g012/g026). "PandaRoot from commit deadbeef" /
  "LuminosityFit from requested commit cafebabe" fail the adjacency-based
  `_has_explicit_version_repository_binding` patterns; the SHA lands in
  `unbound_version_tokens` (visible in g012 diagnostics) and is never
  compared to the locked version. The status-precedence audit confirmed the
  existing precedence (VERSION_CONFLICT > INSUFFICIENT_EVIDENCE > ANSWERED)
  is correct and was not the defect.

## 4. Product fixes (bounded, generic, evidence-supported)

1. `src/panda_agent/retrieval.py` — `Retriever.is_repository_reference(token)`:
   manifest-driven repository-identity test reusing the exact
   `_has_explicit_repository_reference` matching semantics the query analyzer
   already uses (no hard-coded repository names).
2. `src/panda_agent/qa.py` — `_answerability_guard` skips repository
   identities before refusing a bare class symbol: the locked object catalog
   decides code symbols; the repository manifest decides repository
   identities.
3. `src/panda_agent/retrieval.py` — `_has_explicit_version_repository_binding`
   accepts a bounded prepositional connector (one preposition from
   from/at/using/with/of/in/for plus an optional the/a/requested/specific/
   given) between the repository and the version qualifier. Adjacent syntax,
   bare-SHA-stays-unbound, and multi-repository-no-bind semantics are
   preserved and regression-locked.

No case-ID branch, no benchmark-specific literal, no fixed locator, no
release-threshold logic, no downstream metric filter, no prompt change, no
Gold dataset change, no threshold change.

## 5. Regression tests (test-first: red before fix, green after)

- `tests/unit/test_retrieval.py`: prepositional commit request binds and
  conflicts (both g012/g026 phrasings); prepositional binding requires a
  named repository (bare SHA stays unbound); locked-commit request does not
  conflict; repository display names are repository references while class
  names are not.
- `tests/unit/test_qa.py`: repository display names are not requested class
  symbols (g005/g034 phrasings); genuine cataloged class alongside repository
  names is not refused (g027 phrasing); uncataloged class-shaped tokens are
  still refused; established conflict with zero evidence stays
  VERSION_CONFLICT and never degrades to INSUFFICIENT_EVIDENCE.
- Preserved-behavior suites passing unchanged: full `test_qa.py` (F2-A4/F2-A5
  refusal and source-obligation contracts, composer/provenance), full
  `test_retrieval.py`, and the QAAgent-dependent suites
  (`test_e2_a1_answer_point_coverage`, `test_e3_missing_point_retrieval`,
  `test_question_decomposition`, `test_e2_a3_runtime_activation`,
  `test_retrieval_trace`, `test_e1_a2_dynamic_question_decomposition_validation`,
  `test_c8_a0_targeted_merge_semantics`, `test_d4_a5_batch2_controlled_retirement_validation`).

## 6. Verification scope and pre-existing failures

Baseline comparison via stash: the 19 failures in
`test_d4_a5_batch2_controlled_retirement_validation.py` and the 5 failures in
`test_e2_a1_answer_point_coverage`/`test_e2_a3_runtime_activation`/
`test_e1_a2_dynamic_question_decomposition_validation` exist identically on
unmodified HEAD `557327e` and are pre-existing; this task introduced **0 new
test failures**. `test_diagnostics.py`/`test_service.py` cannot be collected
in this environment (fastapi not installed) — pre-existing, service layer
untouched.

## 7. Known residual failures (not fixed in FR1)

- The repaired pipeline's actual effect on the 59-case cohort is unmeasured
  by design (zero scientific calls); a future, separately authorized F6-A
  attempt must measure it.
- RC2 covers repository-qualified prepositional requests; an explicit SHA
  with no resolvable repository stays unbound without conflict (unchanged
  conservative semantics).
- RC1 exclusion covers manifest repository identities; non-manifest project
  aliases are not exempted (conservative).
- Pre-existing unrelated test failures and the fastapi collection gap remain
  outside FR1 scope.

## 8. Integrity

- novel_validation access = 0; holdout access = 0; protected-content
  leakage = 0; new F6-A run = 0; new Gold scientific run = 0; threshold
  changes = 0; Gold question changes = 0.
- Historical F6-A usage unchanged (formal 383 calls / 3,348,432 tokens;
  superseded 9/120 plan 61 calls / 339,150 tokens); FR1 adds 0 / 0.

## 9. New candidate development state

```text
NEW_CANDIDATE_DEVELOPMENT_HEAD = 45f14ba (product-fix commit
"Repair generic refusal and version-conflict handling"; final closeout HEAD
is this artifact's commit, documentation only)
candidate frozen = false
new F6-A preregistered = false
```

## 10. Lifecycle result

```text
F6-A-FR1 = COMPLETE / PASS / ROOT_CAUSES_ESTABLISHED_AND_BOUNDED_FIXES_IMPLEMENTED
F6-A = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (unchanged)
F6-B = LOCKED / F6_A_DID_NOT_PASS (unchanged)
Phase F = IN_PROGRESS / POST_F6_A_FAILURE_REVIEW_COMPLETE_NEW_CANDIDATE_DEVELOPED
```

## 11. Next recommendation

```text
NEXT_TASK_RECOMMENDATION =
NEW F6-A ATTEMPT / NEW CANDIDATE PREREGISTRATION AND FREEZE
(new candidate identity; new preregistration; same formal-English selector
contract; same protected-cohort discipline)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
