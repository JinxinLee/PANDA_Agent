# F2-A2 — Deterministic Completeness Semantic Cleanup

Status: `COMPLETE / PASS / QUESTION_DERIVED_POINTER_NORMALIZATION_COMPLETENESS_ESTABLISHED`
Type: bounded production cleanup + deterministic verification. Zero PANDA
scientific/evaluation calls; zero protected-data access.

Task identity: F2-A2 — Deterministic Completeness Semantic Cleanup.
Traceability: PF-LR1 Group B / F1 residual R10. R10 is provenance only, not the
task name. The repair is bounded to the `pointer_identifier_normalization`
completeness specialization; no other requirement handled by
`_deterministic_missing_requirement_ids` was redesigned.

## 1. Starting state

```text
HEAD = 071ad166d977372a56087de3ab3b1cead9a09e30 (Repair F2-A1 verifier support entailment)
working tree = clean
F2-A1-R1 = COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED
F2-A1 = COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED
F2 = IN_PROGRESS / A1_COMPLETE
F3 = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A1_COMPLETE
normal default = legacy_question_core
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
default promotion = DEFERRED
```

## 2. Mechanism found (old R10 specialization)

The requirement activation in `_answer_requirements` was already generic and
question-grounded (a pointer type expression plus pointer/normalization
vocabulary in the live question/plan). The specialization was downstream:

1. `_requirement_evidence` selected requirement evidence through the fixed
   anchor set `("pndlmdtrackq", "pointer", "tclonesarray")`;
2. `_compact_requirement_evidence` compacted the model-facing subset through
   the fixed anchor set `("pndlmdtrackq", "pointer", "tclonesarray", "lmdtrackq")`;
3. `_deterministic_missing_requirement_ids` evaluated completeness against the
   hard-coded symbol: the claim had to contain `PndLmdTrackQ*` (or
   `PndLmdTrackQ` + `pointer`), had to say `underlying ... PndLmdTrackQ`, and
   had to explain the qualifier rule.

So a generic live-question requirement flowed into a hard-coded known-symbol
completion rule; a question about `SensorFrame*` activated a requirement that
only a `PndLmdTrackQ` answer could satisfy.

## 3. Implementation (`src/panda_agent/qa.py`, +43/−15)

Question-derived target representation: `_answer_requirements` now extracts the
pointer type expression from the live question
(`re.search(r"[A-Za-z_][A-Za-z0-9_:]*\*", question)`, first occurrence, no
C++-grammar parsing) and emits the requirement with bounded metadata
`{"id": "pointer_identifier_normalization", "instruction": ..., "target_symbol":
<symbol>}`. Activation additionally requires a named pointer type expression
(the previous bare `"*" in question` condition is subsumed), so a requirement is
never created without a derivable target, and plan-only symbol presence never
creates the requirement.

- `_requirement_evidence`: fixed anchors removed; matches require the dynamic
  `target_symbol` or generic normalization vocabulary (`pointer`,
  `type expression`).
- `_compact_requirement_evidence`: signature gained an optional
  `target_symbol` parameter (other requirements unchanged); the pointer
  requirement's anchors are now `(target_symbol, "pointer", "type expression")`.
  The fixed `pndlmdtrackq`/`lmdtrackq`/`tclonesarray` anchors are deleted.
- `_deterministic_missing_requirement_ids`: completeness is evaluated against
  the question-derived target — (1) the pointer type expression
  `<target>*` (or `<target>` + `pointer`) is stated; (2) `underlying` plus the
  target symbol is named; (3) the qualifier is explained as syntax, not a new
  identifier (generic rule unchanged). A requirement without a derivable target
  stays missing — the check is never weakened into target-independent keyword
  presence.

No hard-coded `pndlmdtrackq`, `lmdtrackq`, or `tclonesarray` remains anywhere in
`src/panda_agent/qa.py`.

## 4. Genericity / adversarial contract (T1–T8)

`tests/unit/test_qa.py`: updated
`test_regression_protected_requirements_reject_incomplete_claims` to the
target-bearing requirement representation, and added
`PointerNormalizationCompletenessTests`:

| Test | Contract | Result |
|---|---|---|
| T1 | `PndLmdTrackQ*` question → target `PndLmdTrackQ`; semantically complete answer passes (regression, not special case) | PASS |
| T2 | unseen `SensorFrame*` question → target `SensorFrame`; complete normalization explanation passes with no PndLmdTrackQ-specific logic | PASS |
| T3 | `SensorFrame*` question answered only with `PndLmdTrackQ* → PndLmdTrackQ` → requirement stays missing (anti-benchmark) | PASS |
| T4 | right symbol, incomplete semantics (`"SensorFrame is used by the adapter."`; bare `"SensorFrame*"` repetition) → missing | PASS |
| T5 | underlying symbol named but qualifier-syntax explanation absent → missing | PASS |
| T6 | non-pointer question (`"Where is SensorFrame defined?"`) → no requirement | PASS |
| T7 | plan-only `PndLmdTrackQ` symbol does not manufacture the requirement; plan symbol does not become the target of a `SensorFrame*` question | PASS |
| T8 | evidence selection and compaction follow the dynamic target: `SensorFrame` evidence is eligible, unrelated `PndLmdTrackQ` evidence receives no historical preference | PASS |

## 5. Preservation audit

Unchanged (diff-audited): F2-A1/F2-A1-R1 verifier-support repair (no
`deterministically_supported_claims` restoration; no whitelist/comparison
restoration), semantic unsupported-claim behavior, citation/version/locator
integrity, all other answer requirements and deterministic completeness
predicates (factory composition, divergence, acceptance application, elastic
cross-section, reader accounting, model-layer inventory, implementation
disambiguation, efficiency diagnosis, workflow completeness), generic
requirement review, E1 decomposition, E2 claim/point coverage, E3 trigger
semantics, retained-support behavior, retrieval, reranking, evidence selection,
public DTOs, prompts, runtime modes, normal default, promotion. No R04, R01,
R14, F3, D4, or E3 lifecycle surface touched; Group C compatibility retirement
not begun (the in-helper changes are the minimum local ones needed to
genericize R10).

## 6. Verification

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **66 passed,
  4 subtests passed** (includes T1–T8).
- Shared-verify coupling applied (`_deterministic_missing_requirement_ids`
  executes inside `_verify`, including E3 second verify): the authoritative
  focused E3 deterministic set (E3-LR1 §9: 49 focused E3 tests) plus 42
  neighboring E2-A1 shadow tests → `PYTHONPATH=src python -m pytest
  tests/unit/test_e3_missing_point_retrieval.py
  tests/unit/test_e2_a1_answer_point_coverage.py -q` → **91 passed**.
  Regression check only; E3 lifecycle not reopened.
- `git diff --check` PASS; `git diff --stat`: `src/panda_agent/qa.py` +43/−15,
  `tests/unit/test_qa.py` +142.
- PANDA scientific/evaluation calls = 0; PANDA scientific/evaluation tokens = 0.

## 7. Limitations

- Only the first pointer type expression in the question becomes the target;
  multi-expression disambiguation is out of the bounded contract (§7).
- The instruction text of the pointer requirement is unchanged prose; no
  prompt-level changes were needed.
- Other requirements in the shared helpers keep their existing (historical)
  vocabulary; generalizing them belongs to their own lifecycle ownership
  (Group C retirement or later authorization), not to F2-A2.

## 8. Lifecycle closeout

```text
F2-A2  = COMPLETE / PASS /
         QUESTION_DERIVED_POINTER_NORMALIZATION_COMPLETENESS_ESTABLISHED
F2     = IN_PROGRESS / A1_A2_COMPLETE (F2 still incomplete)
F3     = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A2_COMPLETE
normal default = legacy_question_core (unchanged)
default promotion = DEFERRED (unchanged; promotion relevance != promotion authorization)
```

```text
NEXT_TASK_RECOMMENDATION = F2-A3 — E1/E2 Compatibility Retirement
                           (PF-LR1 Group C / F1 residuals R08, R09, R11)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
