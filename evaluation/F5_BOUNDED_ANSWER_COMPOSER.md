# F5 — Bounded Answer Composer Closeout

Lifecycle identity: Phase F → F5 — Bounded Answer Composer.

Decision: **COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED.**

READABILITY_BENEFIT = NOT_EMPIRICALLY_EVALUATED_IN_F5 (no live readability
experiment, human preference study, or model comparison was run or authorized).
All PANDA scientific/evaluation calls and tokens are zero.

## 1. Starting state

- Starting HEAD: `6d24c5bd15ec0ec697b92879f1ff60377aa63fe4`
  ("Repair F4 model role diagnostics") — matched the expected baseline exactly;
  verified, not assumed.
- Worktree: clean before editing; no unrelated user work; no resets, amends,
  squashes, or force operations.

## 2. Previous rendering boundary

`render_verified_answer(claims)` (qa.py) renders claim-by-claim:
`"{claim_text} [{evidence_ids}]"` joined by newlines — deterministic, safe, and
now BYTE-IDENTICAL (verified via AST source-segment extraction). It is the
mandatory deterministic fallback renderer for every F5 failure mode and for
every bypassed path.

## 3. Composer architecture

- **Input boundary (hard)**: the composer call receives exactly
  `{"task": "compose_verified_claims", "verified_claims": [{"claim_id",
  "claim_text"}]}` for already-verified public claims. No question, evidence,
  evidence text, locators, evidence_ids, retrieval plan, answer points,
  answer requirements, analyzer output, expansions, budgets, unsupported
  claims, or drafts ever enter the composer; the composer never sees
  `evidence_ids` (citations are application-owned). The raw question is NOT
  composer input; language/style is inferred from claim texts only.
- **Output schema**: `COMPOSER_SCHEMA` = `{"paragraphs": [{"text": str,
  "source_claim_ids": [str]}]}` (`COMPOSER_REVIEW_SCHEMA` = `{valid, 
  unsupported_paragraph_indexes, missing_or_distorted_claim_ids, reason}`).
- **Generation role**: composer generation runs on `self.generation_vertex`
  (F4 generation role); **verification role**: the single bounded composition
  review runs on `self.verification_vertex`. Both calls carry
  `usage_stage="qa_composer"`. The evaluation judge is untouched and unused.
- **Review boundary**: the reviewer receives only verified claim IDs/texts plus
  composed paragraph texts/source claim IDs — no raw evidence (F4 `_verify`
  already established evidence→claims; F5 validates claims→prose only).

## 4. Deterministic safety validation (`_validate_composed_paragraphs`)

Before any semantic review (failure → fallback, review NOT called), with exact
error codes:

1. **Claim-ID contract**: paragraphs non-empty list of dicts with non-empty
   text and non-empty unique source ids (`invalid_structure`,
   `empty_paragraph`); every source id known (`unknown_claim_id`); no duplicate
   within or across paragraphs (`duplicate_claim_id`); flattened multiset
   exactly equals the verified claim IDs each exactly once
   (`missing_claim_id`) — exact-once coverage, claims may be reordered/merged/
   grouped but never split or dropped.
2. **Technical identifiers**: conservative code-like tokens (`::`-qualified,
   path-like `/`, code/data extensions via the shared `_CODE_DATA_EXTENSIONS`
   set, `repo@version`, underscore identifiers ≥4 chars, inner case-transition
   identifiers such as `PndPidCorrelator`/`createLmdFitData`) must already occur
   in the combined text of the paragraph's referenced claims
   (`new_identifier`).
3. **Numeric literals**: exact-string matching (no `2.0`→`2` normalization) for
   integers/decimals/signed/scientific/percent (`new_numeric_literal`).
4. **Causal relations**: a bounded cue set (because/therefore/thus/causes/
   caused by/leads to/results in/hence/因此/因为/导致/从而) appearing in a
   paragraph but absent from its referenced claim texts fails
   (`new_causal_relation`).
5. **Comparison relations**: bounded cue set (unlike/whereas/compared with/
   compared to/higher/lower/more than/less than/different from/相比/不同/更高/
   更低) treated identically (`new_comparison_relation`).

Neutral discourse connectors (Additionally/Also/Specifically/In this
context/...) are permitted; no large whitelist is maintained — the semantic
reviewer is the second safety layer.

## 5. Semantic composition review

After deterministic validation, exactly ONE review call
(`ANSWER_COMPOSER_REVIEW_SYSTEM_PROMPT`) asks whether every paragraph is fully
entailed by its referenced verified claims with no new factual relationships
(entailment/preservation only; no world knowledge, no answering, no
rewriting). `_validate_composer_review` fails closed: `valid=true` with
non-empty lists, out-of-range paragraph indexes, unknown claim ids, or missing
reason → invalid → fallback. Rejection or exception → fallback. No composer
repair, no second attempt, no alternative model, no generator-as-reviewer or
reviewer-as-composer fallback.

## 6. Deterministic citation ownership and public contracts

`render_composed_answer` derives citations deterministically: per paragraph,
evidence IDs are gathered from its `source_claim_ids` in that order,
deduplicated preserving first occurrence, and appended as
`"{paragraph text} [ids]"` — the model never selects evidence IDs and any
composer-emitted citation-like strings are ignored by construction.
`QAResult.claims` remains the original verified `ClaimCitation` list (ids,
texts, evidence ids untouched); `QAResult.evidence` remains derived from the
verified claims exactly as before (no evidence added/removed by composition);
`QAResult` schema, answer-point modes, and the normal default
`legacy_question_core` are unchanged; no `ComposedClaim` public type exists
(paragraphs are internal dicts); role labels never appear in public content.
Composer failure is recorded ONLY in internal diagnostics — it never appends
to `QAResult.verification_errors` and never fails the QA request. Distinction
preserved: core verification fails closed; the OPTIONAL composer falls back to
the deterministic renderer of already-verified claims.

## 7. Fallback / applicability

- Single verified claim → deterministic bypass (`reason="single_claim_bypass"`,
  attempted=false, fallback_used=false, zero composer/review calls).
- Refusals (future-runtime, universal-proof, unsupported-symbol,
  unsupported-API, deleted-runtime), version conflicts, and generic
  insufficient evidence → no composer call; `composer_diagnostics` stays None.
- Composer generation exception → fallback (`composer_generation_failed`).
- Deterministic validation failure → fallback
  (`deterministic_validation_failed` + codes), semantic review skipped.
- Review exception → fallback (`composer_review_failed`); review rejection →
  fallback (`semantic_review_rejected`).
- Fallback is atomic: always `render_verified_answer(original verified
  claims)`; no partial/salvaged paragraphs. Bound: at most 1 composer + 1
  review = 2 F5 calls per QA execution (0 for bypassed paths).

## 8. Composer diagnostics

`diagnostics["composer"]` (internal only, via the new internal
`QAState.composer_diagnostics` key) carries the fixed sanitized 8-key shape:
attempted / accepted / fallback_used / reason / source_claim_count /
paragraph_count / deterministic_error_codes / semantic_review_called. No
prompt, paragraph text, claim text, raw response, evidence, or credentials.
Allowed reasons: `single_claim_bypass`, `composer_generation_failed`,
`deterministic_validation_failed`, `composer_review_failed`,
`semantic_review_rejected`, `composed`.

## 9. Usage accounting

Composer generation and review both use `usage_stage="qa_composer"` (existing
F4 additive mechanism, vertex.py unchanged) → `qa_composer_calls` /
`qa_composer_token_usage` aggregate across both role clients. Existing
`qa_generation_*` / `qa_semantic_verification_*` counters for their existing
call sites are untouched; tokens come only from response usage metadata.

## 10. E3 / coverage compatibility

For runtime E1/E3 answers the composer receives the final verified public
claim list, including retained supported claims; deterministic citation
rendering covers retained evidence IDs as well. No E3 retained-support, atomic
update, second-verify, decomposition, or revision semantics were modified.
The 49-test E3 suite passes unchanged (multi-claim E3 finalizations route
through the composer's fail-closed validation with their existing task-
dispatching fakes and fall back to the identical renderer).

## 11. Adversarial contract results (T1–T43)

New class `TestBoundedAnswerComposer` (43 methods) plus `ComposerFakeVertex`
in tests/unit/test_qa.py.

| Test | Contract | Result |
| ---- | -------- | ------ |
| T1 | composer payload contains verified claim id/text only — no question/evidence/evidence_ids/locator/plan/answer_point_ids/answer_requirements/source_version_id (central security sentinel) | PASS |
| T2 | reviewer payload contains only verified claims + paragraphs | PASS |
| T3 | exact claim coverage accepted | PASS |
| T4 | claim reordering accepted | PASS |
| T5 | claim merge accepted (stable evidence union citation) | PASS |
| T6 | unknown source claim id → fallback, review skipped | PASS |
| T7 | missing verified claim → fallback | PASS |
| T8 | duplicate source claim assignment → fallback | PASS |
| T9 | empty paragraph → fallback | PASS |
| T10 | new technical identifier (ImaginaryTracker vs PndPidCorrelator) → `new_identifier` fallback before review | PASS |
| T11 | new path → fallback | PASS |
| T12 | preserved existing identifier accepted | PASS |
| T13 | new numeric literal (3 vs 4) → `new_numeric_literal` fallback | PASS |
| T14 | preserved numeric literal accepted | PASS |
| T15 | new causal relation (neutral claims → "therefore") → fallback | PASS |
| T16 | source-supported causal relation allowed | PASS |
| T17 | new comparison rejected | PASS |
| T18 | source-supported comparison allowed | PASS |
| T19 | neutral discourse connector allowed | PASS |
| T20 | semantic reviewer rejects subtle new fact (deterministic checks pass) → fallback | PASS |
| T21 | reviewer reports distorted/missing claim → fallback | PASS |
| T22 | reviewer exception → fallback; generator not used as reviewer | PASS |
| T23 | composer generation exception → fallback; QA request still ANSWERED, verification_errors untouched | PASS |
| T24 | no free retry: exactly 1+0 (failed) / 1+1 (accepted) calls | PASS |
| T25 | deterministic validation failure skips semantic review (zero review calls) | PASS |
| T26 | accepted composition derives citations deterministically | PASS |
| T27 | merged paragraph gets stable evidence-ID union ([e2,e3,e1] order) | PASS |
| T28 | `QAResult.claims` unchanged | PASS |
| T29 | `QAResult.evidence` unchanged | PASS |
| T30 | single verified claim bypasses composer (zero calls) | PASS |
| T31 | refusal bypasses composer (zero calls) | PASS |
| T32 | composer generation routes through generation client (object identity) | PASS |
| T33 | composer review routes through verification client | PASS |
| T34 | evaluation judge remains unused | PASS |
| T35 | `qa_composer_calls` reflects composer + review calls (2 on accepted path; F4 counters untouched) | PASS |
| T36 | composer token usage from response metadata only | PASS |
| T37 | composer diagnostics contain no prompt/claim/evidence text | PASS |
| T38 | `legacy_question_core` remains normal default | PASS |
| T39 | coverage modes remain intact (shadow review audit unchanged; composition gate identical) | PASS |
| T40 | E3 retained-claim/evidence behavior intact (retained citations derive correctly) | PASS |
| T41 | F4 role-routing/failure contracts remain intact (existing suites) | PASS |
| T42 | F2 contracts remain intact (existing suites) | PASS |
| T43 | F3 fixed-locator retirement remains intact (existing sentinel) | PASS |

Two pre-existing assertions required minimal mandated updates: the prompt-set
version test (3.9.0 → 3.10.0 per §36) and the static `usage_stage=` count in
the F4 labeling test (3 → 5 call sites per §32); the runtime stage-set
assertion there is unchanged. No other existing test was modified; all 49 E3
tests pass unmodified through the fallback design.

## 12. Scientific / evaluation accounting

PANDA scientific/evaluation calls: **0**. PANDA scientific/evaluation tokens:
**0**. No T2/T3/T4/T5 scientific evaluation, readability/faithfulness
evaluation, human preference experiment, protected holdout, release
evaluation, promotion evaluation, or LLM judge was run. Mocks/fakes only.

## 13. Readability-benefit boundary

bounded composer safety mechanism established; readability benefit not
empirically evaluated in F5. No claim of scientifically improved readability
is made.

## 14. Lifecycle result

```text
F5 = COMPLETE / PASS / BOUNDED_ANSWER_COMPOSER_SAFETY_CONTRACT_ESTABLISHED
READABILITY_BENEFIT = NOT_EMPIRICALLY_EVALUATED_IN_F5
Phase F = IN_PROGRESS / F5_COMPLETE_F6_NOT_STARTED
```

F6 remains NOT_STARTED; Phase F is not marked complete. Normal default remains
`legacy_question_core`; `runtime_e1_v2` remains explicit-selection-only;
default promotion remains DEFERRED (composition applying to successful
multi-claim answers regardless of mode promotes nothing).

## 15. Next recommendation / authorization

F6 — Release Evaluation and Generalization Gate. Recommendation only; F6
requires separate explicit authorization (T5/release evaluation and protected
holdout work).

NEXT_TASK_EXECUTION_AUTHORIZED = false

## Verification record

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **179 passed +
  19 subtests** (136 pre-existing incl. F4/F4-R1 + 43 new).
- `PYTHONPATH=src python -m pytest tests/unit/test_e3_missing_point_retrieval.py
  -q` → **49 passed** (affected E3 finalization suite; composer fallback
  preserves E3 paths).
- `tests/unit/test_vertex.py` not rerun (vertex.py zero diff);
  `tests/unit/test_service.py` not run (service zero diff).
- Static: `git diff --check` clean; `git status --short` shows exactly the
  three authorized files (`src/panda_agent/qa.py`,
  `src/panda_agent/prompts.py`, `tests/unit/test_qa.py`). No hash bookkeeping.
