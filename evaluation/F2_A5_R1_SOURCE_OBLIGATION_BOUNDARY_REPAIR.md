# F2-A5-R1 — Source Obligation Lexical and Semantic Boundary Repair

Status: `COMPLETE / PASS / SOURCE_OBLIGATION_MATCHING_BOUNDARY_ESTABLISHED`
Type: corrective bounded production repair of F2-A5 + deterministic
verification (PF-LR1 Group E). Zero PANDA scientific/evaluation calls; zero
protected-data access.

Task identity: F2-A5-R1 — Source Obligation Lexical and Semantic Boundary
Repair. Traceability: PF-LR1 Group E / F1 residual R01 (provenance only).

## 1. Historical correction record

- Initial F2-A5 (commit `3eca78d`, "Generalize semantic source obligations")
  correctly retired the fixed R01 intent authority, established raw-question
  ownership, preserved R02 mappings/source budgets/the consumer chain, and
  added the diagnostics receipt.
- An independent post-commit audit did **NOT** accept the original
  `COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED`
  closeout (nor the aggregate `F2 = COMPLETE / PASS /
  A1_A2_A3_A4_A5_COMPLETE`): the question-grounded helper used unbounded
  substring matching, behavior-confirmed at `3eca78d`:
  - `"Why is this hypothesis physically reasonable?"` → `["paper"]`
    ("thesis" inside "hypothesis");
  - `"Why is the macroscopic behavior different?"` → `["code"]` ("macro"
    inside "macroscopic");
  - `"How does a paperless workflow behave?"` → `["paper"]`;
  - `"Which source of systematic uncertainty dominates ...?"` → `["code"]`
    (ambiguous bare "which source").
  Each false positive feeds a hard sufficiency gate and can produce an
  incorrect refusal.
- F2-A5-R1 repairs only the lexical/semantic matching boundary. No historical
  commit or result was rewritten; `3eca78d` remains in history and this report
  is the authoritative final correction. The original F2-A5 report carries a
  correction/supersession notice.

## 2. Starting state

```text
HEAD = 3eca78d3c0254ed61b8f759f79856abd9f03982e (Generalize semantic source obligations)
working tree = clean
F2-A5 = COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED (premature; corrected by this repair)
F2 = COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE (pending correction)
F3 = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_COMPLETE_F3_NOT_STARTED
normal default = legacy_question_core
default promotion = DEFERRED
```

## 3. Matcher repair (`src/panda_agent/retrieval.py`, +43/−12, helper-local)

- `_PAPER_OBLIGATION_PATTERNS` (`paper`, `thesis`, `publication`,
  `literature`, `journal`) and `_CODE_OBLIGATION_PATTERNS`
  (`which source file`, `which code file`, `source code`, `which file`,
  `source file`, `implementation`, `implemented`, `signature`, `macro`),
  multi-word phrases ordered before single tokens.
- `_first_source_obligation_match`: multi-word phrases match as phrases;
  single tokens require regex word boundaries. Substrings inside unrelated
  words can therefore never match ("thesis" in "hypothesis", "paper" in
  "paperless"/"journaled", "macro" in "macroscopic").
- The semantically ambiguous bare `which source` was **removed** as a
  sufficient code trigger (an uncertainty/background "source" is not source
  code); `which source file` / `which code file` / `source file` are the
  bounded replacements. No negative-word patching and no denylist were used —
  the matching primitive itself is the fix.
- Receipt: `support_span` records the actual bounded matched phrase (e.g.
  `which source file`), never an ambiguous shorter substring.
- Obligation order remains deterministically `paper`, `code`; the helper
  still accepts only the raw question (signature inspect-asserted); the
  consumer chain (`_exact` paper priority, `_paper`,
  `_prioritize_and_select_evidence`, `select_final_evidence`,
  `_sufficiency`) is untouched (diff-audited zero consumer/selector/R03
  changes).

## 4. Post-fix precision matrix (§21, helper-level)

| Input | Obligation |
|---|---|
| paper / thesis / publication / literature / journal | paper |
| hypothesis / paperless / journaled | none |
| source code / implementation / implemented / signature / macro / which file / which source file | code |
| macroscopic / which source of systematic uncertainty / source of background | none |

No intentional deviations.

## 5. Adversarial contract (T1–T26)

| Test | Contract | Result |
|---|---|---|
| T1 `test_matching_precision_matrix[hypothesis-...]` | "hypothesis" → no paper | PASS |
| T2 | "macroscopic" → no code | PASS |
| T3 | "paperless" → no paper | PASS |
| T4/T5 | "Which source of systematic uncertainty/background..." → no code | PASS |
| T6/T7/T8 | explicit paper/thesis/publication/literature still match | PASS |
| T9/T10/T11/T12/T13 | source code / implemented / signature / macro / which source file still match | PASS |
| T14 | bare ambiguous "which source" no longer a code trigger | PASS |
| T15/T16 | mixed request canonical `["paper","code"]`; receipt span = actual phrase | PASS |
| T17 | same-intent positive/negative lexical pair (`[]` vs `["paper"]`) | PASS |
| T18 | R02 mappings exactly preserved | PASS |
| T19 | source budgets unchanged | PASS |
| T20 | analyzer/plan/expansion isolation unchanged (signature + receipt authority) | PASS |
| T21 | explicit missing paper/code sufficiency failure preserved | PASS |
| T22 `test_lexical_false_positives_cannot_fail_sufficiency` | end-to-end sentinel: hypothesis/macroscopic questions with valid evidence → sufficient, no `missing required source` | PASS |
| T23 | zero-evidence refusal unchanged | PASS |
| T24/T25 | F2-A4 premise/refusal and F2-A3-R1 coverage authority sentinels pass (existing suites) | PASS |
| T26 | R03/R14/F3/R05/R06 untouched (diff-audited) | PASS |

## 6. Verification

- `PYTHONPATH=src python -m pytest tests/unit/test_retrieval.py -q` → **52
  passed, 7 subtests** (adds `SourceObligationBoundaryTests`).
- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **93 passed,
  16 subtests** (adds the T22 end-to-end sentinel).
- Combined focused run with E2-A1 (42), focused E3 (49), `test_service` (13):
  **255 passed, 47 subtests passed**. The E3 suite is an optional bounded
  regression (the repair is helper-local; no consumer/selector/E3 code
  changed); E3 was not reopened.
- `git diff --check` PASS; `git diff --stat`: 3 files changed, +109/−12.
- PANDA scientific/evaluation calls = 0; PANDA scientific/evaluation tokens
  = 0.

## 7. Preservation

F2-A5 valid architecture preserved: empty R01 config mappings, raw-question
authority, R02 mappings, source budgets, consumer chain, diagnostics receipt.
F2-A1/F2-A1-R1, F2-A2, F2-A3/F2-A3-R1, F2-A4/F2-A4-R1, R05/R06, R03, R14, D4,
E1/E2, E3, default, promotion: untouched (diff-audited).

## 8. Limitations

- The accepted scope is bounded deterministic source-request matching for R01
  hard obligations, not semantic source understanding; compound-case words
  containing a whole trigger token (e.g. a hypothetical "papersource") would
  still match by design of word-boundary matching.
- The vocabulary remains intentionally narrow; ordinary technical questions
  rely on soft budgets.

## 9. Lifecycle closeout

```text
F2-A5-R1 = COMPLETE / PASS / SOURCE_OBLIGATION_MATCHING_BOUNDARY_ESTABLISHED
F2-A5    = COMPLETE / PASS / QUESTION_GROUNDED_SOURCE_OBLIGATION_SEMANTICS_ESTABLISHED
           (final closure achieved only after this corrective repair)
F2       = COMPLETE / PASS / A1_A2_A3_A4_A5_COMPLETE (re-validated after R1)
F3       = NOT_STARTED / UNEXECUTED
Phase F  = IN_PROGRESS / F2_COMPLETE_F3_NOT_STARTED
normal default = legacy_question_core (unchanged)
default promotion = DEFERRED (unchanged; promotion relevance != promotion authorization)
```

```text
NEXT_TASK_RECOMMENDATION = F3 — Fixed Locator/Fallback Cleanup
                           (PF-LR1 bounded package: R03, R05, R06)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
