# F5-R1 — Exact Literal and Identifier Provenance Boundary Repair Closeout

Lifecycle identity: Phase F → F5 → F5-R1 — Exact Literal and Identifier Provenance Boundary Repair.

Decision: **COMPLETE / PASS / EXACT_LITERAL_IDENTIFIER_PROVENANCE_BOUNDARY_ESTABLISHED.**

Corrected parent: `F5 = COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED`
(final closure achieved only after F5-R1);
`READABILITY_BENEFIT = NOT_EMPIRICALLY_EVALUATED_IN_F5` (retained). All PANDA
scientific/evaluation calls and tokens are zero. Deterministic safety
correction only; mocks/fakes only.

## 1. Starting state

- Starting HEAD: `2299cc0ec96c50f96f1d1e8336c957d626c6a4c0`
  ("Add bounded verified-claim answer composer") — matched the expected
  baseline exactly; verified, not assumed.
- Worktree: clean before editing; no unrelated user work; no resets, amends,
  squashes, or force operations.
- Until R1 passed, F5 was treated as PARTIAL / CORRECTION_REQUIRED, Phase F as
  IN_PROGRESS / F5_CORRECTION_REQUIRED, and F6 as NOT_READY / UNEXECUTED.

## 2–3. Pre-fix defect reproduction (both deterministic boundaries)

Reproduced at the starting HEAD by calling `_validate_composed_paragraphs`
directly with production-shaped claims/paragraphs:

```text
NUMERIC    source "The measured efficiency is -3 units."
           paragraph "The measured efficiency is 3 units."
           → ACCEPTED (wrong): "3" is a substring of "-3"
IDENTIFIER source "PndPidCorrelatorV2 provides the analysis."
           paragraph "PndPidCorrelator provides the analysis."
           → ACCEPTED (wrong): "pndpidcorrelator" is a substring of
             "pndpidcorrelatorv2"
MIXED      source "Retry 13 times for 10% of cases in src/foo/TrackBuilder.cxx."
           paragraph "Retry 3 times for 10 of cases in TrackBuilder.cxx."
           → ACCEPTED (wrong): substring hits for 13→3, 10%→10, and the
             shortened path
```

## 4. Root cause

Both deterministic provenance checks used SUBSTRING membership against
arbitrary source prose instead of comparing EXTRACTED tokens:

- numeric: `literal not in source_text` — `"3" in "-3"`, `"3" in "13"`,
  `"10" in "10%"` are all true, so altered spellings passed;
- identifier: `token.casefold() not in source_text.casefold()` — a shorter or
  case-altered technical token is a substring of a longer source token.

`verification_model`-style configuration semantics were not involved; this is
purely a provenance-comparison boundary defect.

## 5–6. Exact provenance repair

- **Numeric extraction** (`_COMPOSER_NUMERIC_PATTERN`): an explicit leading
  `+` or `-` now belongs to the literal (so `3`, `+3`, `-3` are distinct
  spellings), and a lookbehind `(?<![\w.])` keeps digits embedded inside
  technical identifiers (`PndPidCorrelatorV2`, `Model3D`, `sha256`) and inside
  dotted names (`v1.2`) from becoming standalone numeric literals. Decimals,
  percent suffixes, and scientific notation remain part of the exact literal;
  no normalization of any kind.
- **Exact numeric membership**: every paragraph literal must exactly equal one
  of the numeric literals extracted from the referenced source claim texts
  (`literal in {extracted source literals}`), never a substring of prose.
  Collisions rejected: `-3→3`, `13→3`, `10%→10`, `3→+3`, `3.0→3`, `1e3→1e+3`;
  exact `-3→-3` and `10%→10%` accepted.
- **Exact identifier membership**: every paragraph technical token must appear
  verbatim (case- and spelling-sensitive) among the technical tokens extracted
  from the referenced source claim texts. Rejected: prefix collision
  (`PndPidCorrelatorV2→PndPidCorrelator`), suffix drop
  (`createLmdFitDataLegacy→createLmdFitData`), and path shortening
  (`src/foo/TrackBuilder.cxx→TrackBuilder.cxx`); exact identifier and exact
  path accepted.
- **Bounded casing-alteration sentinel** (§13): the extraction heuristic only
  recognizes code-shaped tokens, so a case-altered emission (`pndpidcorrelator`)
  could silently bypass the technical-token check. The validator now also scans
  ordinary word tokens in the paragraph and rejects any word that
  case-insensitively ALIASES an existing source technical token while differing
  in exact spelling. This stays within the bounded technical-token domain — no
  generic proper-noun validation was added; the bounded F5 identifier classes
  (scoped names, paths, code/data filenames, repo@version, underscore
  identifiers, code-like mixed-case identifiers) are unchanged.

Error codes remain exactly `new_numeric_literal` / `new_identifier` (§16); no
new taxonomy.

## 7. Deterministic ownership / 8–10. Fallback and preservation

Every R1 reject case fails in `_validate_composed_paragraphs` BEFORE the
semantic composition review (review calls = 0), and the fallback is exactly
`render_verified_answer(original verified claims)` — no partial salvage, no
composer retry, no claims/evidence mutation, no verification_errors changes.
Preserved with zero diff: composer input boundary (claims-only; T1/T2 payload
security sentinels pass), exact-once claim coverage and its handling, the
semantic composition review as the second layer (still invoked after a
deterministic pass; T19), deterministic citation derivation, single-claim and
refusal/conflict bypasses (§29), F4 generation/verification role routing and
F4-R1 model-role diagnostics, `usage_stage="qa_composer"` accounting
(`qa_composer_calls` / `qa_composer_token_usage`), sanitized diagnostics,
public `QAResult` contracts, E3 retained-claim/finalization behavior, and
F2/F3 mechanisms.

## 11. Prompt clarification

`ANSWER_COMPOSER_SYSTEM_PROMPT` contained a tension between "Preserve
technical identifiers exactly as written in the claims" and "Never include ...
any identifiers other than the given claim IDs". Applied the bounded
clarification verbatim in spirit: "Do not invent metadata identifiers, claim
IDs, citation IDs, or evidence IDs. Technical identifiers already present in
the verified claims may be retained and must be preserved exactly."
`PROMPT_SET_VERSION` 3.10.0 → 3.10.1; the directly dependent prompt-version
test was updated. No other prompt semantics changed.

## 12–15. Preservation audit

Composer input boundary, claim coverage, semantic review, citations, public
claims/evidence/schema, F4/F4-R1 routing and diagnostics, usage accounting,
single-claim/refusal bypasses, E3 compatibility, F2/F3, and the
`legacy_question_core` default all unchanged (no Vertex/service/models/
retrieval/E3/F2/F3 file touched). F4-R1 sentinels pass.

## 16. Adversarial contract results (T1–T30)

New class `TestComposerProvenanceBoundary` (16 methods) in
tests/unit/test_qa.py; T20–T30 are carried by the pre-existing suites, all
passing unmodified.

| Test | Contract | Result |
| ---- | -------- | ------ |
| T1 | `-3 → 3` rejected (`new_numeric_literal`) | PASS (`test_numeric_sign_spelling_collision_rejected`) |
| T2 | `13 → 3` rejected | PASS (`test_numeric_substring_collision_rejected`) |
| T3 | `10% → 10` rejected | PASS (`test_numeric_percent_spelling_collision_rejected`) |
| T4 | `3 → +3` rejected | PASS (`test_numeric_explicit_plus_collision_rejected`) |
| T5 | `3.0 → 3` rejected | PASS (`test_numeric_decimal_spelling_collision_rejected`) |
| T6 | `1e3 → 1e+3` rejected | PASS (`test_numeric_scientific_spelling_collision_rejected`) |
| T7 | exact `-3 → -3` accepted | PASS (`test_exact_signed_literal_accepted`) |
| T8 | exact `10% → 10%` accepted | PASS (`test_exact_percent_literal_accepted`) |
| T9 | identifier-embedded digits inert (PndPidCorrelatorV2/sha256 create no numeric obligations) | PASS (`test_identifier_embedded_digits_inert`) |
| T10 | `PndPidCorrelatorV2 → PndPidCorrelator` rejected | PASS (`test_identifier_prefix_collision_rejected`) |
| T11 | `createLmdFitDataLegacy → createLmdFitData` rejected | PASS (`test_identifier_suffix_collision_rejected`) |
| T12 | case alteration (`PndPidCorrelator → pndpidcorrelator`) rejected | PASS (`test_identifier_case_alteration_rejected`) |
| T13 | full path → shortened filename rejected | PASS (`test_identifier_path_shortening_rejected`) |
| T14 | exact identifier accepted | PASS (`test_exact_identifier_and_path_accepted`) |
| T15 | exact path accepted | PASS (`test_exact_identifier_and_path_accepted`) |
| T16 | all deterministic R1 failures skip semantic review (review calls = 0) | PASS (asserted in T1/T2/T10 tests + dedicated fallback test) |
| T17 | deterministic failures return the exact deterministic renderer output | PASS (`test_provenance_failures_fall_back_exactly_without_retry`) |
| T18 | no composer retry (exactly 1 generation call on failure) | PASS (same test) |
| T19 | semantic review still runs after a deterministic pass | PASS (`test_semantic_review_still_runs_after_deterministic_pass`) |
| T20 | original F5 payload-security sentinels | PASS (pre-existing `TestBoundedAnswerComposer` T1/T2) |
| T21 | original exact-once claim-coverage tests | PASS (pre-existing T6–T9) |
| T22 | causal/comparison gates unchanged | PASS (pre-existing T15–T19) |
| T23 | deterministic citation tests | PASS (pre-existing T26/T27) |
| T24 | public claims/evidence preservation | PASS (pre-existing T28/T29) |
| T25 | single-claim/refusal bypass | PASS (pre-existing T30/T31) |
| T26 | generation/verification role routing | PASS (pre-existing T32/T33) |
| T27 | F4-R1 model-role diagnostics | PASS (pre-existing `test_production_ab_config_diagnostics_report_actual_role_models`) |
| T28 | E3 retained-claim/finalization tests | PASS (49-test E3 suite unmodified) |
| T29 | F2/F3 preservation sentinels | PASS (pre-existing suites) |
| T30 | `legacy_question_core` default unchanged | PASS (pre-existing default-mode tests) |

Before/after reproduction (§34) is recorded in §2–3 (pre-fix ACCEPTED for both
defects) and §5–6 (post-fix REJECT with `new_numeric_literal` /
`new_identifier`, `semantic_review_called=false`, `fallback_used=true`); all
15 unit-level sentinel shapes (N1–N9, I1–I6) were verified directly before
being frozen into the pipeline tests.

## 17. Scientific / evaluation accounting

PANDA scientific/evaluation calls: **0**. PANDA scientific/evaluation tokens:
**0**. No readability evaluation, human preference, T2/T3/T4/T5, protected
holdout, release, promotion evaluation, or live model comparison.

## 18. Historical correction

The original F5 commit `2299cc0` is preserved unamended;
`evaluation/F5_BOUNDED_ANSWER_COMPOSER.md` carries a CORRECTION /
SUPERSESSION NOTICE (F5-R1) at the top; its historical body is unmodified.

## 19–21. Lifecycle result

```text
F5-R1 = COMPLETE / PASS / EXACT_LITERAL_IDENTIFIER_PROVENANCE_BOUNDARY_ESTABLISHED
F5 = COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED (final closure only after F5-R1)
READABILITY_BENEFIT = NOT_EMPIRICALLY_EVALUATED_IN_F5
Phase F = IN_PROGRESS / F5_COMPLETE_F6_NOT_STARTED
```

F6 remains NOT_STARTED and requires separate explicit T5/release/holdout
authorization. Normal default remains `legacy_question_core`; default
promotion remains deferred; promotion evaluation not authorized.

## 22. Verification record

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **195 passed +
  21 subtests** (179 pre-existing + 16 new R1 methods; the only pre-existing
  assertion change is the mandated prompt-version 3.10.0 → 3.10.1 update).
- `PYTHONPATH=src python -m pytest tests/unit/test_e3_missing_point_retrieval.py
  -q` → **49 passed** (affected E3 finalization suite).
- `tests/unit/test_vertex.py` not rerun (vertex.py zero diff).
- Static: `git diff --check` clean; `git status --short` shows exactly the
  three authorized files (`src/panda_agent/qa.py`, `src/panda_agent/prompts.py`,
  `tests/unit/test_qa.py`). No hash bookkeeping.

## 23. Next recommendation / authorization

F6 — Release Evaluation and Generalization Gate. Recommendation only; F6
requires separate explicit T5/release/holdout authorization.

NEXT_TASK_EXECUTION_AUTHORIZED = false
