# PANDA Agent — Phase D2-A2: Terminology/Paraphrase Evaluation Report

> Status: `D2-A2 = COMPLETE / MIXED_RESULTS` (A2R1:
> `COMPLETE / EVALUATION_SEMANTICS_REPAIRED`, 2026-08-30). Frozen evaluation
> executed correctly against a current D1-compatible structured state. The
> mixed outcome is recorded honestly; the resolver was not modified during or
> after the evaluation. D2-A3 owns the role decision.
>
> All headline numbers in this document are mechanically reproduced from the
> structured result artifact `evaluation/d2_a2_results.json`
> (`metric_consistency_problems = []`); they are not manually transcribed.

---

## 1. Objective

Evaluate the frozen D2-A1 shadow resolver (baseline `67eff2b`) against a
preregistered, source-grounded terminology/paraphrase case set: how accurately
and conservatively does it map genuine user terminology, technical
identifiers, aliases, descriptive paraphrases, ambiguous expressions,
corrective expressions, and unsupported expressions to the D1-governed entity
space?

## 2. Baseline and provenance

- Resolver implementation baseline: `67eff2b` — verified unchanged: `git diff
  67eff2b HEAD` over `entity_resolution.py` / `descriptive_resolution.py` /
  `retrieval.py` is empty.
- Case artifact: `evaluation/d2_a2_terminology_cases.yaml` (frozen before
  execution; authorized post-freeze amendments limited to C14/C10 invalid
  markers, the C16 encoding repair, and C21 evaluation metadata — no question
  or expected-identity changes).
- Results artifact: `evaluation/d2_a2_results.json`.
- Runner/state: `evaluation/scripts/d2_a2_runner.py` +
  `evaluation/scripts/d2_a2_state.py`; executed with `--receipt-baseline`
  pointing at the `ae7b281` results for the §19 consistency check.
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

All green before execution (`valid = true`): 32 objects, zero duplicate IDs;
the four required representative canonical IDs
(`concept.luminosityfit.luminosity_fit_model`,
`workflow.restgas.first_pass_poca`, `data_product.restgas.pid_final_root`,
`configuration.restgas_profile`) each present exactly once; identity roles ⊆
{canonical, source_native} on all seeds; 2 accepted aliases (1 corrective, 1
true identity); 16 accepted relations; 1 curated WorkflowStep; POCA structured
facts present; resolver probe executed read-only.

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

## 7. Case counts and validity

```text
case_counts:
  total = 22          valid = 20
  case_invalid = 2    not_applicable = 0
  correct = 16
case_validity: 20/22 = 0.9091
```

Invalid cases (both recorded with reasons in the case artifact, never
replaced): **C10** — expected status was implementation-informed rather than
source-first (the frozen resolver's lexical tie behavior shaped the expected
AMBIGUOUS); **C14** — curation inventory error (the expected target declared
the source_file row while the authoritative symbol-bearing record is the
function row `object.c08459387c6fd0c77a717960`).

## 8. Decision accounting (valid cases)

```text
correct_resolve   = 9
wrong_resolve     = 1   (C16)
correct_abstain   = 5   (C08, C17, C18, C19, C20)
wrong_abstain     = 0
correct_ambiguous = 2   (C03, C13)
wrong_ambiguous   = 2   (C02, C12, C21)
not_applicable    = 2   (C10, C14)
```

The accounting sums to the 20 valid cases; `metric_consistency_problems = []`.

## 9. Preregistered metrics (numerator/denominator/value)

| Metric | Num | Den | Value |
| --- | --- | --- | --- |
| resolution_accuracy (expected RESOLVED_UNIQUE, valid) | 9 | 12 | 0.75 |
| canonical_identity_accuracy (expected-canonical, valid) | 6 | 9 | 0.6667 |
| explicit_canonicalization_accuracy (true-identity alias) | 2 | 2 | 1.0 |
| source_native_noncanonicalization_accuracy | 3 | 3 | 1.0 |
| abstention_accuracy | 5 | 6 | 0.8333 |
| ambiguity_accuracy | 2 | 2 | 1.0 |
| false_positive_resolution_rate (valid negative/control) | 1 | 8 | 0.125 |
| case_validity | 20 | 22 | 0.9091 |
| category_natural_applicability | 14 | 16 | 0.875 |
| execution_coverage | 22 | 22 | 1.0 |
| evidence_validity | 10 | 10 | 1.0 |
| positive_resolution_coverage | 10 | 12 | 0.8333 |

`canonical_identity_accuracy` counts cases expecting a canonical identity
(direct canonical match with `canonical_object_id = null`, or valid Tier G
canonicalization). `explicit_canonicalization_accuracy` counts only the
true-identity alias case, where a noncanonical surface form is expected to
canonicalize. `source_native_noncanonicalization_accuracy` counts cases where
`canonical_object_id` must remain null — all three held.

## 10. Corrective-term analysis

C08 (`restgas_profile.txt`): correction surfaced, `identity_authority = false`,
status UNRESOLVED — `corrective_handling_correct = 1`,
`corrective_handling_incorrect = 0`. The corrective term never carried Tier G
authority and was never sent through Tier D.

## 11. Descriptive Tier D summary

```text
descriptive_positive_cases       = 6  (C02, C09, C11, C12, C21, C22; C10 invalid and excluded)
descriptive_correctly_resolved   = 3  (C09, C11, C22)
descriptive_ambiguous            = 3  (C02, C12, C21)
descriptive_unresolved           = 0
descriptive_wrong_confident      = 0
```

## 12. Strong identity (Tier G/S) analysis

All strong-identity cases correct: governed ID (C01), true alias
canonicalization (C07), exact symbol (C05), exact path (C06), and the
scoped/natural collisions (C03 AMBIGUOUS, C04 version-scoped unique). Zero
false cross-record canonicalizations: `PndLmdModelFactory` resolves to its own
function record with `canonical_object_id = null` despite the `IMPLEMENTS`
relation (C14 qualitative receipt), and `event_poca` resolves to itself
despite containment by `boost_root` (C15).

## 13. False-positive resolution analysis

The only formal false positive is **C16**: after the identifier was correctly
`REJECTED_VERSION`, the whole-question fallback confidently resolved to
`workflow.pandaroot.lmd_reconstruction` (2 features). This is the
fallback-granularity finding of Section 15. C10's related-entity
over-resolution is qualitative only (Section 15).

## 14. Multi-mention isolation

C21 verified the A1R1 evidence-isolation repair independently: each mention's
descriptive evidence excludes the other mention's distinctive tokens
(`mention_isolation_valid = true`, no leakage). The C21 failures are the
lexical sibling ties of Section 11, not evidence leakage.

## 15. Qualitative findings from invalidated cases

- **C10** — CASE_INVALID for quantitative scoring because the Gold
  expectation was implementation-informed. The raw receipt still shows: an
  explicit subsystem description produced a **confident resolution to
  `concept.luminosityfit.luminosity_fit_model`** — qualitative
  RELATED_ENTITY_OVERRESOLUTION evidence: the whole-question fallback span
  aggregates tokens and can dominate where mention-level evidence ties. A3
  should review the fallback-span granularity.
- **C14** — CASE_INVALID (curation inventory error); its re-executed receipt
  demonstrates the corrected state resolving the symbol to the function
  record.

## 16. Version/scope analysis

C04 (locked-version unique resolution), C16 (wrong-version rejection), and
C17 (source-scope rejection) behaved per contract; descriptive inference never
bypassed scope/version checks.

## 17. Query-expansion boundary

C20: the QE-only concept never became a mention; the fallback abstention is
retained and `fallback_required = true`. Query expansion helped planning but
did not establish identity.

## 18. Failure taxonomy

```text
COMPETITION_AMBIGUITY        = 3  (C02, C12, C21)
WRONG_CONFIDENT_RESOLUTION   = 1  (C16)
CASE_INVALID                 = 2  (C10, C14 — excluded from formal failure accounting)
```

## 19. Receipt consistency versus the frozen resolver

`receipt_consistency_vs_ae7b281`: 20 unchanged valid cases compared across
statuses/mention texts/matched/canonical/evidence tier+kind/candidate IDs —
**20/20 identical** (C10/C14 skipped as invalid; C14's difference is the
documented §41 state-row correction, not resolver behavior).
`resolver_behavior_unchanged = true`: **evaluation semantics changed; resolver
behavior did not.**

## 20. Limitations

Small targeted set (22 cases) — proves contract behavior, not statistical
quality; the descriptive mechanism is deliberately lexical-only in A1 (frozen
shadow isolation forbade resolver-time model calls); the evaluation state is
a deterministic fixture of the D1 representative space plus 8 real corpus
rows, not the full 133k corpus (the resolver's exact-match layer is value-
driven, so un-declared corpus identifiers are out of scope rather than
missed); C14 was invalidated by a curation inventory error and C10 by a
source-first Gold violation.

## 21. Implications for D2-A3 (evidence package; no role decision here)

D2-A3 must review: (1) strong identity (Tier G/S) is fully reliable — zero
false canonicalizations; (2) corrective terms and abstention are safely
non-authoritative with correct accounting; (3) descriptive Tier D is useful
(3/6 correct) but lexically conservative — sibling/container ties produce
AMBIGUOUS instead of resolution (C02/C12/C21); (4) the whole-question fallback
can over-resolve (C10 qualitative, C16 formal); (5) natural applicability is
meaningful for identity/descriptive/ambiguous/corrective categories and zero
for MULTIPLE/SAME_AS; (6) failures are systematic (two mechanisms), not
scattered. Candidate A3 considerations: narrowing the fallback-span scope,
sibling-aware descriptive features, or KEEP_SHADOW — the role decision belongs
to D2-A3.
