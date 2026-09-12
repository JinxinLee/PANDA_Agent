# F2-A4 — Premise and Refusal Generalization

> **CORRECTION / SUPERSESSION NOTICE (F2-A4-R1).** This report's initial
> terminal `COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED`
> closeout was subsequently found premature by an independent post-commit
> audit: the corpus-level existence authority and historical-literal removals
> below are valid and were preserved, but (1) `unsupported_symbol`
> refusal-basis relevance still mixed plan-only symbols/concepts into its
> anchors, (2) explicit `class|struct|enum` extraction did not validate the
> captured token ("class of" / "struct layout" false positives), and (3) the
> bare locator premise ("Where is MissingTrackAdapter?") was under-detected.
> Those boundaries are repaired by
> `evaluation/F2_A4_R1_QUESTION_GROUNDED_PREMISE_REFUSAL_REPAIR.md`
> (F2-A4-R1 = `COMPLETE / PASS / QUESTION_GROUNDED_PREMISE_REFUSAL_BOUNDARY_ESTABLISHED`),
> which is the authoritative final lifecycle record for this surface. The
> narrative below is preserved unchanged for historical transparency.

Status: `COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED`
Type: bounded production cleanup + deterministic verification (PF-LR1 Group D).
Zero PANDA scientific/evaluation calls; zero protected-data access.

Task identity: F2-A4 — Premise and Refusal Generalization.
Traceability: PF-LR1 Group D / F1 residual R04 (provenance only).

## 1. Starting state

```text
HEAD = bb1a63996a563726761e51aa03c11f9dea70b794 (Repair F2-A3 coverage prompt authority)
working tree = clean
F2-A1-R1 / F2-A1 / F2-A2 / F2-A3-R1 / F2-A3 = all COMPLETE / PASS (see status)
F2 = IN_PROGRESS / A1_A2_A3_COMPLETE
F3 = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A3_COMPLETE
normal default = legacy_question_core
default promotion = DEFERRED
```

## 2. Historical R04 specialization (verified at starting HEAD)

- `_sufficiency` contained a dedicated branch with
  `requested_symbol = "PndUniversalRestgasDeconvolver"`: the exact literal in
  the question triggered a definition search **over the currently selected
  evidence** (locator symbol or `class|struct` declaration), and absence
  produced `unsupported requested symbol: PndUniversalRestgasDeconvolver`.
  Selected evidence was therefore the whole-corpus existence authority — the
  inverse of the correct contract.
- `_finalize` matched that exact error prefix, searched one fixed locator
  (`macro/target/correction/efficiency_correction_2.C`), and asserted a
  substitute implementation ("the existing implementation uses a longitudinal
  efficiency-correction macro instead") in the public refusal.
- The generic foundation was already present and untouched (F1-R16):
  `_locked_symbols()` builds the locked-corpus identifier catalog (locator
  symbols/paths plus `class|struct|enum` declarations), and
  `_answerability_guard` already used it for qualified `Class::method` API
  checks.

## 3. Generic premise contract

1. **Question-grounded extraction** (`_requested_bare_class_symbols`, module
   helper — no plan access): explicit `class Foo` / `struct Foo` / `enum Foo`
   wording; pointer type expressions `Foo*`; and class-shaped
   (compound-cased, internal lowercase→uppercase boundary) identifiers named
   inside a request/definition context ("How does X …", "What does X …",
   "… defined", "… implemented"). Plain capitalized prose words (What,
   Where, Implementation — no internal boundary) and plan-only symbols are
   excluded by construction; the extractor never reads the plan.
2. **Locked-catalog existence authority**: the guard checks each candidate
   against `_locked_symbols()` (`symbols` and `paths`). Catalog absence — not
   selected-evidence absence — produces
   `unsupported requested symbol: <symbol>`.
3. **Bounded false positives**: the compound-case shape requirement excludes
   ordinary prose; explicit class/pointer wording is itself the premise; no
   C++ parser, no NER, no uppercase-token heuristic.

## 4. Refusal implementation

- `_sufficiency`: the exact historical branch was **removed**. The guard runs
  at the top of `_sufficiency`, so its structured error drives the refusal.
- `_finalize`: the exact-matcher branch was replaced by a generic branch that
  extracts the requested symbol from the structured error
  (`unsupported requested symbol: <symbol>`), emits dynamic generic wording
  ("The locked corpus does not define <symbol>, so its implementation details
  cannot be verified." / Chinese equivalent), and never hard-codes the
  historical class or locator.
- Optional basis: `_refusal_basis_evidence` gained an `unsupported_symbol`
  kind — candidates are code/workflow evidence with at least one
  question-anchor overlap, ranked purely by anchor overlap (no source-type or
  path preference), and `None` when nothing is query-relevant. A selected
  basis yields one claim: "The cited locked code at <location> documents
  <query-relevant subject>." No substitution/replacement assertion exists.
- No production control-flow literal remains for
  `PndUniversalRestgasDeconvolver` or `macro/target/correction/efficiency_correction_2.C`
  in `qa.py` (grep-verified); the historical locator survives only in a
  pre-existing R05 fallback test fixture.

## 5. Preservation audit

Zero diff touches on: F2-A1/F2-A1-R1 verifier semantics, F2-A2 pointer
completeness, F2-A3/F2-A3-R1 coverage authority, R16 generic guard semantics
(extended, not altered), E1/E2, E3 trigger/retrieval/ledger, retrieval,
reranking, `select_final_evidence`, R01, R05 (`PndPidCorrelator.h` fallback),
R06 (`ana_dpm.C` + `event_poca`), default mode, promotion.

## 6. Adversarial contract (T1–T15)

| Test | Contract | Result |
|---|---|---|
| T1 | historical class refused through the generic guard; dynamic refusal wording; no fixed locator/substitute in answer | PASS |
| T2 | unseen `ImaginaryRestgasCorrector` → identical generic refusal; no production addition for the synthetic symbol | PASS |
| T3/§20 | known class absent from selected evidence but present in the catalog → no refusal (catalog is the authority) | PASS |
| T4 | plan-only unknown symbol → no refusal (extractor never reads the plan) | PASS |
| T5 | `Where is class MissingTrackAdapter defined?` → refused via explicit class wording | PASS |
| T6 | ordinary prose/uppercase tokens → no refusal | PASS |
| T7 | relevant evidence outranks the historical locator under generic ranking; historical path gets no special preference | PASS |
| T8 | no "instead"/"replacement" assertion anywhere | PASS |
| T9 | no relevant basis → bare refusal, zero claims, zero citations | PASS |
| T10 | relevant basis → one claim citing that evidence, naming only the documented subject | PASS |
| T11 | qualified unsupported-API refusal unchanged | PASS |
| T12/T13 | future-runtime / universal-proof / deleted-runtime refusals unchanged (existing tests pass) | PASS |
| T14 | coverage-mode early refusal ends at insufficiency; E3 trigger inputs never produced | PASS |
| T15 | F2-A3-R1 seam tests still pass (run in the combined suite) | PASS |
| §21 | premise-mismatch sentinel: refused without hallucinating from related evidence | PASS |

## 7. E3 interaction

The generalized premise guard is pre-answer `_sufficiency` behavior: an
unsupported requested class returns insufficient before answer/verify, so E3
trigger inputs (`missing_answer_point_ids`) are never produced (T14 asserts
this directly). `_check_e3_trigger`, targeted retrieval, consolidation,
reranking, selection, and retained-support semantics are untouched. As a
bounded regression the full focused E3 deterministic suite (49 tests) was run
together with the neighboring suites and passed; E3 was not reopened.

## 8. Verification

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **89 passed,
  16 subtests passed** (includes `PremiseRefusalGeneralizationTests`).
- Combined focused run with the E2-A1 (42) and E3 (49) suites plus
  `test_service.py`: **193 passed, 16 subtests passed**.
- `git diff --check` PASS; `git diff --stat`:
  `src/panda_agent/qa.py` +144/−42, `tests/unit/test_qa.py` +241.
- PANDA scientific/evaluation calls = 0; PANDA scientific/evaluation tokens = 0.

## 9. Limitations

- The extractor supports the bounded question shapes named in the repair
  contract (explicit class/struct/enum wording, pointer expressions,
  class-shaped identifiers in request/definition context). Broader
  symbol-resolution or C++ declarator support remains out of scope.
- The refusal-basis claim is a single narrow context statement; ranking is
  deterministic anchor overlap without a semantic entailment check.
- R05/R06 fixed fallbacks and R01 source obligations are untouched (F3 /
  Group E ownership).

## 10. Lifecycle closeout

```text
F2-A4  = COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED
F2     = IN_PROGRESS / A1_A2_A3_A4_COMPLETE (F2 still incomplete)
F3     = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A4_COMPLETE
normal default = legacy_question_core (unchanged)
default promotion = DEFERRED (unchanged; promotion relevance != promotion authorization)
```

```text
NEXT_TASK_RECOMMENDATION = F2-A5 — Semantic Source Obligation Generalization
                           (PF-LR1 Group E / F1 residual R01)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
