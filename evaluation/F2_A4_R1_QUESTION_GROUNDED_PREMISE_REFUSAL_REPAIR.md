# F2-A4-R1 — Question-Grounded Premise Extraction and Refusal-Basis Repair

Status: `COMPLETE / PASS / QUESTION_GROUNDED_PREMISE_REFUSAL_BOUNDARY_ESTABLISHED`
Type: corrective bounded production repair of F2-A4 + deterministic
verification (PF-LR1 Group D). Zero PANDA scientific/evaluation calls; zero
protected-data access.

Task identity: F2-A4-R1 — Question-Grounded Premise Extraction and
Refusal-Basis Repair. Traceability: PF-LR1 Group D / F1 residual R04
(provenance only).

## 1. Historical correction record

- Initial F2-A4 (commit `4f9c87e`, "Generalize premise refusal semantics")
  correctly generalized corpus-level existence handling
  (`_locked_symbols()` as the whole-corpus authority) and correctly removed
  the historical class control-flow literal and the fixed replacement locator.
- An independent post-commit audit did **NOT** accept the original
  `COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED` closeout.
  Three remaining question-grounding defects were found and
  behavior-confirmed at `4f9c87e`:
  1. `unsupported_symbol` refusal-basis relevance mixed plan-only
     symbols/concepts into the anchor set, so plan-suggested unrelated
     evidence could become the optional refusal basis;
  2. explicit `class|struct|enum <token>` extraction did not validate the
     captured token, so natural language ("What class of problem is this?" →
     `of`; "Explain the struct layout used here." → `layout`) became
     requested code symbols;
  3. the bare locator premise ("Where is MissingTrackAdapter?", "Which file
     contains X?") was under-detected because "where is" had been dropped
     from the context terms.
- F2-A4-R1 repairs exactly these boundaries. No historical commit or result
  was rewritten; `4f9c87e` remains in history and this report is the
  authoritative final correction. The original F2-A4 report carries a
  correction/supersession notice.

## 2. Starting state

```text
HEAD = 4f9c87e1f61da7cd5f6bd4f679261bb9f6c6a953 (Generalize premise refusal semantics)
working tree = clean
F2-A4 = COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED (premature; corrected by this repair)
F2 = IN_PROGRESS / A1_A2_A3_A4_COMPLETE
F3 = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A4_COMPLETE
normal default = legacy_question_core
default promotion = DEFERRED
```

## 3. Repair

### 3.1 Question-only refusal basis (Defect A)

`_refusal_basis_evidence` now computes `question_anchors =
_question_domain_tokens(question)` separately from the plan-assisted
`anchors`; the `unsupported_symbol` kind uses `question_anchors` for both
candidate admission and ranking. `future_runtime` and `universal_proof`
rankings are byte-for-byte unchanged (they legitimately keep plan-assisted
context). Plan-only symbols/concepts can therefore no longer admit or promote
unrelated evidence as the optional refusal basis; the basis stays optional
and `None` when no question-relevant selected evidence exists.

### 3.2 Explicit-token validation (Defect B)

Explicit `class|struct|enum <token>` capture now requires a plausible
code-identifier shape (`_is_code_like_identifier`: length > 2 and initially
capitalized or underscore-bearing). "class of", "struct layout", and "type"
as ordinary prose are rejected; `MissingTrackAdapter`, `SensorFrame`,
`Foo` still extract. Pointer-expression extraction (`Foo*`) uses the same
validation.

### 3.3 Locator premise restoration (Defect C)

Context terms restored/extended: `where is`, `where's`, `which file`,
`which code`, `path` (plus the existing how/what/defined/implemented
terms). Class-shaped identifier + context is still required, so "Where is
Implementation?" stays inert while "Where is MissingTrackAdapter?" extracts
the symbol.

### 3.4 Realistic catalog fixtures (§11 rule)

Restoring "where is" correctly surfaced that several full-path tests asked
"Where is PndPidCorrelator?" against an unrealistically empty locked
catalog. Per the R1 rule, the **fixtures** were corrected (a catalog row for
`PndPidCorrelator`), not the production semantics:
`test_answered_path_is_bounded_and_cited`,
`test_agent_core_run_has_no_service_import_or_database_persistence`,
`test_run_detailed_reports_per_request_workflow_and_model_usage` (all in
`test_qa.py` via a shared `PID_CATALOG_ROWS` constant), and the
`test_service.py` canonical frozen-fixture test. Production behavior is now
exactly: question asks where `PndPidCorrelator` is + catalog contains it →
no refusal.

## 4. Verification

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **95 passed,
  16 subtests passed** (includes the R1 sentinels T1/T3/T4/T6/T7/T13 within
  `PremiseRefusalGeneralizationTests`).
- Combined focused run: `test_qa.py` + E2-A1 (42) + focused E3 deterministic
  (49) + `test_service.py` (13) → **200 passed, 16 subtests passed**. The E3
  suite is an optional bounded regression (this repair does not touch
  `_verify`/`_revise`/E3 trigger/selector); E3 was not reopened.
- Behavior verification at HEAD: `class of` → `[]`; `struct layout` → `[]`;
  `Where is MissingTrackAdapter?` → extracted; `Where is
  PndPidCorrelator?` → extracted (refused only against an empty catalog);
  plan-only evidence → basis `None`.
- Static sentinels: no `PndUniversalRestgasDeconvolver` /
  `efficiency_correction_2` literals in production; no
  `unsupported_symbol` selection on plan-only anchors; no natural-language
  `class of`/`struct layout` path to refusal.
- `git diff --check` PASS.
- PANDA scientific/evaluation calls = 0; PANDA scientific/evaluation tokens
  = 0.

## 5. Preservation

F2-A4 valid architecture preserved (corpus-catalog existence authority,
generic guard/finalizer/structured error/dynamic wording, no replacement
assertion, historical literals gone). F2-A1/F2-A1-R1, F2-A2, F2-A3/F2-A3-R1,
R05 (`PndPidCorrelator.h` fallback), R06 (`ana_dpm.C`/`event_poca`), E1/E2,
E3, retrieval, selector, R01, default, promotion: untouched (diff-audited).

## 6. Limitations

- The extractor remains a bounded shape/context contract, not symbol
  resolution; compound-case prose words inside request contexts remain a
  theoretical false-positive surface (mitigated by the catalog check).
- Question-only relevance uses the existing conservative domain-token
  anchors; it does not perform semantic relatedness.

## 7. Lifecycle closeout

```text
F2-A4-R1 = COMPLETE / PASS / QUESTION_GROUNDED_PREMISE_REFUSAL_BOUNDARY_ESTABLISHED
F2-A4    = COMPLETE / PASS / GENERIC_PREMISE_REFUSAL_SEMANTICS_ESTABLISHED
           (final closure achieved only after this corrective repair)
F2       = IN_PROGRESS / A1_A2_A3_A4_COMPLETE (F2 still incomplete)
F3       = NOT_STARTED / UNEXECUTED
Phase F  = IN_PROGRESS / F2_A4_COMPLETE
normal default = legacy_question_core (unchanged)
default promotion = DEFERRED (unchanged; promotion relevance != promotion authorization)
```

```text
NEXT_TASK_RECOMMENDATION = F2-A5 — Semantic Source Obligation Generalization
                           (PF-LR1 Group E / F1 residual R01)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
