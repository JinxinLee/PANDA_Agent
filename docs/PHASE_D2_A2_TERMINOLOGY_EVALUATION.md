# PANDA Agent — Phase D2-A2: Terminology/Paraphrase Evaluation Report

> Status: `D2-A2 = COMPLETE / MIXED_RESULTS` (2026-08-30). Frozen evaluation
> executed correctly against a current D1-compatible structured state. The
> mixed outcome is recorded honestly; no resolver changes were made during or
> after the evaluation. D2-A3 owns the role decision.

---

## 1. Objective

Evaluate the frozen D2-A1 shadow resolver (baseline `67eff2b`) against a
preregistered, source-grounded terminology/paraphrase case set, measuring how
accurately and conservatively it maps genuine user terminology, technical
identifiers, aliases, descriptive paraphrases, ambiguous expressions,
corrective expressions, and unsupported expressions to the D1-governed entity
space.

## 2. Baseline and provenance

- Starting HEAD / resolver implementation commit: `67eff2b` (`D2 A1R2 repair
  empty fallback abstention accounting`).
- Case artifact: `evaluation/d2_a2_terminology_cases.yaml` (frozen before
  execution; the only post-freeze amendments are documented in §14 below and
  are not case rewording).
- Result artifact: `evaluation/d2_a2_results.json` (per-case
  results with full receipts, metrics, category summaries, state-validation
  report, run provenance).
- Runner: `evaluation/scripts/d2_a2_runner.py`; state:
  `evaluation/scripts/d2_a2_state.py`; executed with
  `PYTHONPATH=src python evaluation/scripts/d2_a2_runner.py --project-root .
  --cases evaluation/d2_a2_terminology_cases.yaml --results
  evaluation/d2_a2_results.json`.
- No model/Vertex/LLM calls; no Qdrant; no production DB writes.

## 3. Evaluation-state construction

Deterministic in-memory D1-compatible fixture state (the A0-acceptable
alternative to a reingested isolated database), materialized via the
PRODUCTION loaders — `seed_knowledge_objects`, `materialize_seed_relations`,
`seed_workflow_steps`, `seed_knowledge_aliases` — plus 8 declared real-corpus
source-native rows (ids/versions/locators verified against
`data/normalized/9925ec31…/knowledge_objects.jsonl`, including the
symbol-bearing `PndLmdTrackQ` class records in both pandaroot and
restgas_determination and the `PndLmdModelFactory` function record added by
the documented state correction in §14). The stale live PostgreSQL state
(133,075 objects predating D1-A2) was deliberately NOT used: missing D1-A2
representative entities there must not be counted as resolver failures.

## 4. Evaluation-state validation gate

All green before execution (`valid = true`): 32 objects (24 seeds + 8 declared
rows), zero duplicate IDs; the four required representative canonical IDs
(`concept.luminosityfit.luminosity_fit_model`,
`workflow.restgas.first_pass_poca`, `data_product.restgas.pid_final_root`,
`configuration.restgas_profile`) each present exactly once; identity roles ⊆
{canonical, source_native} on all seeds; 2 accepted aliases (1 corrective, 1
true identity); 16 accepted relations; 1 curated WorkflowStep; POCA structured
facts (CONSUMES/PRODUCES) present; resolver probe executed read-only.

## 5. Case curation method and distribution

Source-first per the A0 preregistration: governed entities/conditions selected
from current D1 configs and verified corpus rows → terminology/paraphrases
determined from source semantics → expected status/targets assigned from the
frozen contract → frozen → only then executed. No Gold wording mining; no
pseudo-Gold; no protected data. 22 concrete cases + 2 recorded
NOT_APPLICABLE categories (`RESOLVED_MULTIPLE` natural applicability = 0 —
the trailing-`s` mechanism was removed in D2-A1R1; `SAME_AS` — no accepted
`SAME_AS` edges exist in the current D1 state, and manufacturing one would
violate the D1 co-reference contract). Both are separately covered by focused
T0 tests.

Category coverage: exact canonical terminology (2), exact technical
identifier (1), source-native symbol (1), path reference (1), accepted alias
(1), corrective term (1), descriptive domain paraphrase (1), implementation
description (1), workflow description (1), data-product description (1),
ambiguous terminology (1), related-but-not-identical (2), version-sensitive
(2), unsupported/generic (2), query-expansion negative control (1),
multi-mention isolation (1), documentation-vs-concept (1).

## 6. Exposure policy

Development-visible and source-grounded only. No `novel_holdout`, no
protected holdout, no hidden benchmark content, no T5/release data.

## 7. Headline metrics

| Metric | Value |
| --- | --- |
| Applicable cases | 21 of 22 (C14 recorded INVALID_CASE) |
| Resolution accuracy | 0.75 (12/16 expected-resolve cases) |
| Canonicalization accuracy (expected-canonical cases) | 0.6667 (2/3) |
| Canonicalization accuracy (source-native, canonical=null expected) | 1.0 (4/4) |
| Abstention accuracy | 0.8333 (5/6) |
| Ambiguity accuracy | 0.6667 (2/3) |
| False-positive resolution rate | 0.2222 (2/9) |
| Applicability / coverage | 0.9545 / 1.0 |
| Evidence validity | 1.0 (zero prohibited-evidence violations) |

Decision accounting: `correct_resolve = 10`, `wrong_resolve = 2`,
`correct_abstain = 5`, `wrong_abstain = 2`, `correct_ambiguous = 2`,
`wrong_ambiguous = 0`, `not_applicable = 1` (C14 INVALID_CASE);
`corrective_handling_correct = 1`, `corrective_handling_incorrect = 0`.

## 8. Category-level results (applicable → correct/wrong)

- Exact canonical terminology: 2 → 1 correct (C01 Tier G governed ID), 1 wrong
  (C02 COMPETITION_AMBIGUITY, below).
- Exact technical identifier: 1 → 1 correct (C03 natural two-repository
  collision correctly AMBIGUOUS).
- Source-native symbol / path reference: 2 → 2 correct (C05, C06).
- Accepted alias: 1 → 1 correct (C07 Tier G true alias with canonicalization).
- Corrective term: 1 → 1 correct (C08; correction surfaced, identity authority
  false, not Tier G).
- Descriptive domain paraphrase: 1 → 1 correct (C09 Tier D).
- Implementation description: 1 → 0 correct (C10, below).
- Workflow description: 1 → 1 correct (C11 Tier D with structured facts).
- Data-product description: 1 → 0 correct (C12 COMPETITION_AMBIGUITY).
- Ambiguous terminology / singular collision: 1 → 1 correct (C13 AMBIGUOUS,
  no top-1).
- Related-but-not-identical: 2 → 1 correct (C15; C14 INVALID_CASE).
- Version-sensitive: 2 → 1 correct (C17 REJECTED_SCOPE), 1 wrong (C16, below).
- Unsupported/generic: 2 → 2 correct (C18, C19; evaluated abstentions
  retained per A1R2).
- Query-expansion negative control: 1 → 1 correct (C20; QE concept never
  became a mention; fallback abstention retained).
- Multi-mention isolation: 1 → 0 correct (C21 COMPETITION_AMBIGUITY; evidence
  isolation itself verified — no cross-mention tokens in evidence).
- Documentation-vs-concept: 1 → 1 correct (C22).
- `RESOLVED_MULTIPLE`: NOT_APPLICABLE (natural applicability 0).
- `SAME_AS`: NOT_APPLICABLE (no accepted edges in current D1 state).

## 9. False-positive analysis

2 of 9 abstain/ambiguous-expected (or corrective) cases were confidently
resolved — both by the whole-question fallback mechanism:

- **C10** (WRONG_CONFIDENT_RESOLUTION): the question's two explicit
  identifiers ("LuminosityFit", "model-and-fit") correctly went AMBIGUOUS,
  but the synthesized whole-question fallback resolved UNIQUE to
  `concept.luminosityfit.luminosity_fit_model` (5 features) — the fallback
  span aggregates tokens from the entire question and can dominate where
  mention-level evidence ties.
- **C16** (WRONG_CONFIDENT_RESOLUTION contribution): after the identifier
  was correctly REJECTED_VERSION, the whole-question fallback resolved UNIQUE
  to `workflow.pandaroot.lmd_reconstruction` (2 features) — a confident
  resolution attached to a question whose primary mention was version-
  rejected.

Both are the same architectural finding: **the whole-question fallback span
is coarser than mention-level spans and can convert ambiguity/rejection into
confident resolution.** Recorded for D2-A3; no tuning performed.

## 10. Ambiguity analysis

2 of 3 ambiguity-expected cases correct (C03 natural two-repository symbol
collision; C13 PID data-product sibling ambiguity). C02 was expected to
resolve and instead hit a three-way lexical tie — recorded as
wrong_abstain/COMPETITION_AMBIGUITY (Section 11). No case collapsed to
arbitrary top-1.

## 11. Abstention analysis

5 of 6 abstain-expected cases correct, with the A1R2 accounting exercised:
every evaluated fallback abstention appears in `receipt.resolutions`,
`unresolved_mentions`, and drives `fallback_required = true` — including the
zero-candidate case (C18) and the QE-only control (C20). One wrong abstention
is C02 (should have resolved; tied instead — Section 11).

## 12. Canonicalization analysis

Zero false cross-record canonicalizations. Source-native cases correctly keep
`canonical_object_id = null` (4/4), including the `PndLmdModelFactory`
negative control. The 1/3 expected-canonical misses are Tier D ties where the
matched record would itself have been canonical (comparator clarification
documented: a direct canonical match with `canonical_object_id = null`
satisfies the expectation; only a different canonical target fails).

## 13. Evidence-validity analysis

Zero violations: no query-expansion identity authority, no retrieval-rank or
similarity-based identity, no relation-edge co-reference, no unsupported
analyzer concepts, no cross-record canonicalization without Tier G. All 12
resolved outcomes carried contract-permitted evidence (G/S/D per category).

## 14. Evaluation-state corrections and invalid case (transparent record)

- **C14 INVALID_CASE**: the frozen expectation declared the source_file row
  `object.ceb44bd02a5e3a790cf2dfad` for "PndLmdModelFactory", but the
  authoritative symbol-bearing record is the function row
  `object.c08459387c6fd0c77a717960` — a curation inventory error. Recorded
  INVALID_CASE per the freeze discipline (not replaced); excluded from
  metrics as not_applicable.
- **State correction (§41)**: the symbol-bearing function row was added to
  the declared evaluation-state rows (state 31 → 32 objects; documented in
  the state builder). This is evaluation-infrastructure correction, not
  resolver tuning.
- **C16 encoding repair**: the deliberate wrong-version stimulus was
  YAML-coerced to an integer (`0000…` unquoted), making the case
  CASE_INVALID on encoding grounds. Fixed by quoting (semantically identical
  stimulus); the re-run measured the intended REJECTED_VERSION outcome plus
  the fallback finding in Section 9. First-run and re-run both documented in
  the results provenance.

## 15. Version/scope analysis

3 of 4 version/scope cases correct: locked-version resolution (C04),
source-scope rejection (C17), and wrong-version rejection measured after the
encoding repair (C16 — the rejection itself is correct; the extra fallback
resolution is the Section 9 finding). Descriptive inference never bypassed
scope/version checks.

## 16. Multi-mention isolation

Evidence isolation verified: each mention's descriptive evidence excludes the
other mention's distinctive tokens (C21). The C21 failures are lexical
sibling ties (Section 11), not evidence leakage.

## 17. Failure taxonomy

`COMPETITION_AMBIGUITY = 3` (C02, C12, C21 — lexical sibling/container ties);
`WRONG_CONFIDENT_RESOLUTION = 2` (C10, C16 — whole-question fallback
over-resolution); `CASE_INVALID = 1` (C14 — curation inventory error). No
MENTION_EXTRACTION_FAILURE, no QUERY_GROUNDING_FAILURE, no
FALSE_CANONICALIZATION, no EVIDENCE_AUTHORITY_VIOLATION, no
VERSION_SCOPE_FAILURE, no CORRECTIVE_TERM_FAILURE, no
MISSING_STRUCTURED_STATE.

## 18. Representative failures

- C02/C21: "luminosity fit model" ties with
  `subsystem.luminosityfit.model_and_fit` and other LuminosityFit siblings —
  the lexical feature space cannot separate the framework's own
  concept/subsystem siblings at mention granularity.
- C12: "the boost ROOT output that contains the event_poca tree" ties with
  `event_poca` — container-vs-contained wording is lexically symmetric.
- C10/C16: whole-question fallback converts ambiguity/rejection into
  confident resolution.

## 19. Limitations

Small targeted set (22 cases) — proves contract behavior, not statistical
quality; descriptive mechanism is deliberately lexical-only in A1 (frozen
shadow isolation forbade resolver-time model calls); the evaluation state is
a deterministic fixture of the D1 representative space plus 8 real corpus
rows, not the full 133k corpus (the resolver's exact-match layer is value-
driven, so un-declared corpus identifiers are out of scope rather than
missed); C14 was invalidated by a curation inventory error.

## 20. Implications for D2-A3 (evidence package; no role decision here)

D2-A3 must review: (1) strong identity (Tier G/S) is reliable — 0 false
canonicalizations, all exact/symbol/path/alias cases correct; (2) corrective
terms are safely non-authoritative; (3) abstention accounting is reliable
post-A1R2; (4) descriptive Tier D is useful but conservative — and its
lexical granularity cannot separate entity siblings sharing a framework token
cluster (C02/C10/C12/C21), and the whole-question fallback can
over-resolve (C10/C16); (5) natural applicability is meaningful for
identity/descriptive/ambiguous/corrective categories and zero for
MULTIPLE/SAME_AS; (6) failures are systematic (two mechanisms above), not
scattered. Whether these support KEEP_SHADOW, a DEVELOPMENT_SUPPORTED_CANDIDATE
role with narrowed fallback scope, or an A1R3-style fallback repair is the
D2-A3 decision.
