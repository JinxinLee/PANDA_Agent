# PANDA Agent — Phase D2-A0: Resolver Contract and Evaluation Preregistration

> Status: `COMPLETE / CONTRACT_AND_PREREGISTRATION_FROZEN` (2026-08-29).
> Design/contract/preregistration stage. No runtime behavior changed; the D2
> shadow resolver is NOT implemented here (D2-A1 owns it) and `SAME_AS`
> traversal is NOT activated. Authoritative D1 baseline: `30455d4`
> (`D1 = COMPLETE / PASS`).

Central question frozen for D2:

> Given a user mention or descriptive expression, under what evidence and rules
> may PANDA Agent claim that it refers to a specific canonical or source-native
> entity?

Preserved C5 lesson (identity law): **a unique exact or retrieval match is not
sufficient proof of canonical identity.** Resolver identity must be
independently grounded in governed evidence.

---

## 1. Scope

D2-A0 freezes: the resolver contract (mention → candidates → identity evidence
→ canonicalization → decision), the identity-evidence hierarchy, the alias and
`SAME_AS` consumption contracts, version handling, statuses, ambiguity and
abstention semantics, the descriptive-paraphrase boundary, the
query-expansion boundary, the D2-A1 shadow contract, the D2-A2 evaluation
preregistration, and the D2-A3 role-decision criteria. It implements nothing.

## 2. Terminology

- **Mention**: a phrase or technical expression in the user question taken to
  refer to something.
- **Candidate**: an existing governed entity (D1 canonical or source-native)
  that could plausibly match a mention.
- **Identity evidence**: contract-permitted grounding for claiming a candidate
  is the referred entity.
- **Canonicalization**: mapping a matched noncanonical/source-native
  representation to its canonical entity through governed identity evidence.
- **Alias**: another expression referring to the same entity (identity
  equivalent). **Related term**: semantically associated but not identical.

The five resolver stages are conceptually separable and must remain so:
mention/terminology understanding → candidate generation → identity evidence
evaluation → canonicalization → resolution decision. Resolution is never
"whatever retrieval ranked first".

## 3. Existing resolver inventory (audited at HEAD `30455d4`)

`src/panda_agent/entity_resolution.py` (C5, shadow-only):

- **Input contract**: `resolve(question: str, plan: Mapping|RetrievalPlan)`;
  reads only `knowledge_aliases` and `knowledge_objects` through an injected
  storage connection; never calls models or other channels; never writes.
- **Mention sources** (priority `accepted_alias` 0 > `analyzer_symbol` 1 >
  `explicit_identifier` 2): raw-question technical identifiers; C2-accepted
  analyzer symbols with complete in-question support; accepted aliases matched
  by boundary-safe deterministic patterns.
- **Match kinds / priority**: `accepted_alias` 0 > `exact_symbol` 1 >
  `exact_title` 2 > `exact_path` 3; `identity_relation` defined with priority
  4 but structurally unsupported.
- **Statuses**: `RESOLVED_UNIQUE`, `RESOLVED_MULTIPLE`, `AMBIGUOUS`,
  `UNRESOLVED`, `REJECTED_VERSION`, `REJECTED_SCOPE`, `MISSING_TARGET`.
- **Result schema**: `EntityResolutionReceipt` (per-mention resolutions with
  candidates, selected object, reason; resolved/ambiguous/unresolved lists;
  rejected candidates; `fallback_required`) plus a canonical prefix row list.
- **Scope behavior**: source allow-list (`plan.target_repositories` + context
  sources + `curated_panda_domain`), locked-version rejection
  (`resolved_versions`), ambiguity surfaced, no hidden selection.
- **Identity relation**: `IDENTITY_RELATION_SUPPORT = "NOT_AVAILABLE"` — no
  predicate meant identity when C5 shipped; D1 has since added `SAME_AS`.
- **Exact-match normalization**: boundary-safe, case-insensitive,
  whitespace-flexible alias patterns; `_normalization_key` =
  casefolded whitespace-collapsed text; exact symbol/title/path compares are
  exact string equality (path includes basename fallback).
- **Shadow mode / production consumers**: the only consumer is
  `Retriever.shadow_exact(question, plan)` — an explicit shadow method that
  never triggers an analyzer call and returns PRE (legacy `_exact`) vs POST
  (entity-first `merge_exact_streams`) plus the receipt. Production exact
  remains `LEGACY_EXACT`; no production wiring exists.

models.py also carries a separate `ResolutionStatus` enum
(`resolved`/`ambiguous`/`unresolved_external`/`unresolved_internal`) used by
`RelationCandidate` — a relation-candidate vocabulary, distinct from the
resolver string statuses.

## 4. Identity-evidence hierarchy (frozen for D2-A1)

### Tier G — governed explicit identity (may directly resolve; may canonicalize)

| Evidence | Resolve | Canonicalize | Constraints |
| --- | --- | --- | --- |
| Exact canonical object ID (governed ID stated in the question) | Yes | n/a (already canonical) | ID must exist; scope/version checks still apply |
| Accepted curated alias (`review_status = accepted`) | Yes | Yes, to its single target | boundary-safe occurrence; target exists; scope/version checks; multiple accepted targets → AMBIGUOUS |
| Accepted/reviewed `SAME_AS` edge | Yes | Yes, toward the canonical endpoint per D1 orientation | only accepted; pending/rejected never; conflicts → AMBIGUOUS (Section 6) |
| Exact source-native technical identifier with explicit source/type grounding (`locator.symbol` equality within locked source/version scope) | Yes | Only through governed identity evidence (G alias/SAME_AS); symbol equality alone does not canonicalize | uniqueness within scope; else REJECTED_VERSION/REJECTED_SCOPE/AMBIGUOUS |

### Tier S — strong but context-dependent (candidate generation + conditional resolve; never canonicalize alone)

Exact canonical title; exact unique symbol without explicit type grounding;
exact path/locator; stable repository/document identifier. These may resolve
**only when** uniqueness holds inside the plan's source/version scope AND the
match kind is recorded as context-dependent evidence; any competing same-tier
match → RESOLVED_MULTIPLE/AMBIGUOUS. They must never canonicalize a
noncanonical match to a canonical entity by themselves.

### Tier D — descriptive evidence (candidate generation/scoring only)

Terminology variants, paraphrases, implementation descriptions, domain and
concept descriptions. May generate and rank candidates among governed
entities; may never directly resolve or canonicalize. A descriptive match can
support a final decision only in combination with Tier G/S evidence on the
same candidate, and the combined decision must be recorded as such in
diagnostics. Uniqueness of the descriptive candidate set does not upgrade the
tier.

### Tier N — non-identity evidence (never resolves, never canonicalizes)

Semantic similarity scores, dense retrieval rank, BM25 rank, graph proximity,
co-occurrence, related relation edges (`IMPLEMENTS`, `FORMALIZES`,
`PRODUCES`, `CONSUMES`, `DEPENDS_ON`, `THEORETICAL_BASIS_FOR`, …),
query-expansion rules, and any LLM assertion without independent grounding.
Uses: candidate retrieval support and post-decision context only. Relation
edges may help contextualize or disambiguate candidates that are already
identity-grounded, but never imply their endpoints are the same entity.

No numerical confidence scale is introduced; the deterministic evidence tier +
ambiguity state is the authority signal. If any score exists it is diagnostic:
`score != authority`.

## 5. Alias contract

`alias = another expression referring to the same entity`. Related terms are
not aliases. Prohibited as aliases merely because they are related:
concept ↔ implementation class; workflow ↔ macro; subsystem ↔ source file;
documentation ↔ concept; producer ↔ produced object; parent ↔ child; theory ↔
implementation; broad topic ↔ narrow entity. Alias rules inherited unchanged
from the D1 contract Section D (review states, provenance, single target,
English-only, no evaluation-derived aliases, conflict surfacing).

`configs/query_expansions.yaml` must not automatically become alias data; no
mass migration in D2 (D3/D4 own migration).

**Existing alias audit (2 accepted, both compliant)**: `restgas_profile.txt`
(generic_user_term → `configuration.restgas_profile`) maps the colloquial
user filename to the configuration key it denotes — identity-equivalent
expression of the same referent, with correction_message documenting that no
literal file exists; `*_pid_final.root` (file_pattern →
`data_product.restgas.pid_final_root`) is the filename pattern of that exact
data product. Both satisfy the D2 alias definition; no clarification required.

## 6. `SAME_AS` consumption contract (frozen; not activated in A0)

1. Only accepted/reviewed `SAME_AS` may affect authoritative resolution;
   pending/rejected `SAME_AS` must never resolve or canonicalize.
2. Traversal preserves co-reference semantics: `SAME_AS` endpoints denote one
   entity; the resolver treats the pair as one identity with two records.
3. `SAME_AS` must never be inferred from similarity, title proximity, graph
   proximity, or any heuristic; only stored accepted edges count.
4. Canonicalization direction respects D1 identity roles and the frozen
   orientation (Case A stored `noncanonical → canonical`; Case B
   deterministic; Case C accepted dual-canonical cannot exist — validation
   rejects it). Traversal is bidirectional over the single stored edge.
5. Source-native → canonical canonicalization is allowed only through this
   governed identity evidence (or a governed alias), never through
   similarity.
6. Multiple reachable canonical targets for one mention produce
   AMBIGUOUS/resolution conflict — never arbitrary top-1.
7. `SAME_AS` must not erase version conflicts: locked-version and scope
   rejection still apply to both endpoint records; a version-conflicted
   endpoint yields REJECTED_VERSION, not silent canonicalization.
8. When activated in D2-A1, `SAME_AS` enters Tier G (governed explicit
   identity) alongside accepted aliases; `IDENTITY_RELATION_SUPPORT` flips
   from `NOT_AVAILABLE` only in the shadow resolver.

## 7. Canonical vs source-native result contract

The D2 result must distinguish the mention-matched representation from the
canonical entity when safely available. D2-A1 shall extend the existing
per-mention resolution record (currently mention/candidates/selected/reason)
with the equivalent of:

```text
mention                # interpreted expression + provenance kind
matched_object_id      # the representation the evidence matched
canonical_object_id    # canonical entity when governed canonicalization applies, else null
resolution_status      # Section 9 vocabulary
identity_evidence      # tier + concrete evidence references (alias id, SAME_AS edge id, symbol/locator, relation edge id)
version_scope          # source/version constraints applied (allowed sources, locked versions, rejections)
diagnostics            # candidates considered, rejection reasons, abstention reason
```

Exact field names may follow the existing dataclass style, but the semantic
distinction is frozen: **a matched source-native object is not automatically
the canonical object; canonicalization requires governed evidence.**

## 8. Version-aware resolution

1. Exact source-native symbols may be version-specific; symbol identity is
   asserted only within the locked source/version scope.
2. Canonical domain entities may span corpus versions only as permitted by
   their D1 identity contract (curated namespace, `curated_panda_domain`).
3. User-specified repository/version scope constrains candidates before
   identity evaluation.
4. The same symbol in multiple incompatible versions is
   AMBIGUOUS/version-conflicted, never silently merged.
5. Version scope is never dropped during canonicalization; the result carries
   the applied scope.
6. Accepted-alias provenance/version is respected (existing behavior).
7. No cross-version fuzzy merging.

## 9. Resolution status semantics

Frozen D2 vocabulary (extends the existing C5 strings; `models.ResolutionStatus`
remains a relation-candidate vocabulary and is not reused):

- `RESOLVED_UNIQUE` — one governed entity is supported by permitted evidence
  within scope.
- `RESOLVED_MULTIPLE` (**MULTIPLE**) — multiple valid entities are explicitly
  requested or the phrase legitimately denotes several entities (e.g. a
  plural/collective mention); all are returned; not a failure.
- `AMBIGUOUS` — the resolver cannot safely select among competing identities;
  candidates are surfaced; no selection.
- `UNRESOLVED` — no sufficiently grounded candidate exists.
- Preserved rejections: `REJECTED_VERSION`, `REJECTED_SCOPE`,
  `MISSING_TARGET` (existing C5 semantics unchanged).
- Unsupported mentions (no deterministic mention evidence at all) are simply
  absent from the receipt, not forced to UNRESOLVED — the receipt records what
  was interpreted.

Ambiguity is never collapsed into arbitrary top-1.

## 10. Ambiguity and abstention are first-class

Frozen rule: **when evidence is insufficient to establish identity, return
UNRESOLVED/AMBIGUOUS rather than guessing.** Abstention is a success mode.
Expected abstention/ambiguity triggers: generic nouns; broad physics topics;
related-but-not-identical entities; overloaded class/function names;
conflicting repository/version contexts; descriptive paraphrases with several
plausible candidates; weak semantic similarity without identity evidence.
D2-A2 must measure false-positive resolution explicitly (Section 16).

## 11. Mention and candidate boundaries

D2-A1 supports both mention origins through one thin deterministic interface:

- **Upstream-supplied**: mentions derived from `RetrievalPlan` — exact
  `symbols`, plan `concepts` (as terminology mentions, Tier D candidates at
  most), `resolved_aliases` — with provenance preserved.
- **Self-extracted**: deterministic raw-question mention extraction (the
  existing C5 boundary-safe identifier/alias extraction, extended for
  descriptive mention spans as candidate-generation input).

D2-A0 does not redesign the analyzer. Frozen interface: D2 **receives** the
raw question, the current `RetrievalPlan` (concepts, symbols,
resolved_versions, target_repositories), and a read-only storage connection;
D2 **returns** the resolution receipt plus per-mention results (Section 7).
D2 never calls the analyzer, other retrieval channels, or any model during
resolution.

## 12. Descriptive/paraphrase resolution constraints

A terminology/paraphrase case is a mention that refers to a governed entity
without being a literal alias or exact identifier, e.g. "luminosity fit model"
or "the model used to extract luminosity from the LMD angular distribution"
→ `concept.luminosityfit.luminosity_fit_model`; "first-pass POCA analysis" or
"the step that reads the first PID output and writes the boost ROOT file" →
`workflow.restgas.first_pass_poca`.

Frozen rules: **a descriptive paraphrase may generate or score candidates, but
semantic similarity alone must never become identity truth** (Tier D
constraints, Section 4). D2-A1 must attach interpretable
evidence/diagnostics for every descriptive decision. Candidates come only
from existing governed entities (D1 canonical entities, source-native
entities, accepted alias targets, accepted identity-linked representations);
**the resolver must not invent new canonical objects at query time**; no
unrestricted corpus-wide LLM entity invention. Implementation choices (e.g.
any embedding-based candidate retrieval) belong to D2-A1 design within these
bounds.

## 13. Query-expansion boundary

`configs/query_expansions.yaml` rules are classified (per the D1 contract
Section L inventory) into stable terminology, normalization, phrase→concept,
phrase→implementation/file, workflow shortcut, answer-location shortcut,
negative-control guard, and legacy multilingual compatibility. Frozen rule:

> Query-expansion rules may be analyzed as legacy vocabulary/debt, but they
> are not authoritative identity evidence unless separately represented as
> governed aliases/entities under the D1 alias contract.

No migration in D2-A0/A1; D3/D4 own it.

## 14. D2-A1 shadow-only contract

D2-A1 implements the resolver in **shadow mode**. It must not automatically
alter: production RetrievalPlan; query expansions; exact retrieval; dense
query; sparse query; graph traversal; fusion; reranking; answer behavior. The
shadow resolver produces diagnostics/results alongside current behavior
(analogous to the C5 `shadow_exact` pattern — explicit invocation, explicit
plan, no analyzer trigger, production paths untouched). Expected A1
production statement: `CURRENT_DEPLOYED_RETRIEVAL_BEHAVIOR_CHANGED = false`.
No production wiring in A0 or A1.

## 15. D2-A2 preregistration — categories

Terminology/paraphrase evaluation taxonomy (representative, not
equal-sample; corpus availability recorded honestly at A2 time):

1. exact canonical terminology; 2. exact technical identifier; 3. accepted
alias/abbreviation; 4. source-native symbol; 5. source-native
path/reference where applicable; 6. descriptive domain paraphrase;
7. implementation-description paraphrase; 8. workflow/data-product
description; 9. ambiguous terminology; 10. related-but-not-identical
terminology; 11. version-sensitive identifier; 12. unsupported/unresolvable
expression.

## 16. D2-A2 preregistration — positive/negative cases and metrics

Both positive (defensible canonical/source-native target exists) and
negative/abstention (no single identity may be selected: generic topic,
term spanning multiple implementations, related-not-alias concept,
ambiguous symbol, false premise, unsupported phrase) cases are mandatory —
this prevents recall-only evaluation.

Primary metrics, preregistered before any A1 results:

- **Resolution accuracy** — correct final identity among applicable positive
  cases.
- **Canonicalization accuracy** — correct canonical target when
  canonicalization is expected.
- **Abstention accuracy** — correct unresolved/ambiguous outcome on negative
  cases.
- **False-positive resolution rate** — cases incorrectly resolved when they
  should abstain.
- **Ambiguity accuracy** — correct handling when >1 candidate remains
  plausible.
- **Applicability/coverage** — how often the resolver can make an
  authoritative decision at all.
- **Evidence validity** — resolved cases backed by permitted identity
  evidence rather than prohibited shortcuts.

Decision accounting (reported separately, never collapsed into one score):

```text
correct_resolve / wrong_resolve / correct_abstain / wrong_abstain /
correct_ambiguous / wrong_ambiguous / not_applicable
```

High-severity accounting: **wrong confident resolution is architecturally
more concerning than a safe unresolved result**; the resolver favors identity
precision over forced coverage. D2-A3 must see these counts separately.

## 17. D2-A2 dataset exposure rules

Exposure classes: **development-visible** (may diagnose architecture, never
justifies question-specific fixes); **frozen comparison set** (selected and
frozen before A1 freeze, used for the A2 measured comparison); **protected
holdout** (not required for D2 unless explicitly authorized later). Exposed
cases must not silently become hidden evaluation. Case sources must follow
existing dataset exposure rules: no hidden holdout, no `novel_holdout`, no
protected validation content for implementation tuning. Permitted sources:
source-grounded hand-curated terminology cases; existing approved exposed
development material where permitted; D1 entities/aliases and their source
evidence; source-first manually written paraphrases. **No pseudo-Gold**: do
not generate gold labels by asking the resolver or an LLM.

Source-first curation process (frozen): select governed entity/source
evidence → determine legitimate terminology/paraphrases independently of
resolver output → record expected entity/status → preregister/freeze → only
then run A2. Never inspect resolver failures and then create favorable cases
around them.

## 18. D2-A2 scope and tier

Targeted: small enough to audit manually, large enough to cover the
terminology/paraphrase/ambiguity categories. Likely tier: T0 resolver
invariants plus a targeted T2-style resolution evaluation. No T3/T4/T5; no
retrieval/QA runs unless a later task explicitly needs interaction evidence.

## 19. No benchmark-specific entity rules

Evaluation questions and paraphrases are measurement data, not resolver
implementation specifications. D2-A1 must not add question-ID rules, exact
benchmark phrase routes, hidden answer locations, benchmark-derived aliases,
or phrase-specific candidate overrides. Any genuinely needed new alias must
satisfy the governed alias contract independently of the evaluation case.

## 20. D2-A3 role-decision criteria

Implementation completion does not imply production authority; **D2-A3, not
D2-A1, decides the resolver role**. Candidate outcomes: `KEEP_SHADOW`;
`DEVELOPMENT_SUPPORTED_CANDIDATE`; another explicitly justified limited role;
production-authoritative only if evidence strongly supports it. No automatic
promotion is preregistered; no arbitrary numeric promotion thresholds are
invented in A0. A3 must review: resolution accuracy; false-positive
resolution; abstention behavior; ambiguity handling; applicability; version
handling; evidence-contract violations; observed failure modes; production
interaction risk — never a single aggregate accuracy. Qualitative gates:
no systemic identity false-positive pattern; abstention works on negative
controls; descriptive cases show useful natural applicability; ambiguity is
surfaced rather than hidden; no prohibited identity evidence observed.

## 21. Interaction with retrieval (future boundary, not wired)

Intended future boundary: question → mention/entity resolver → governed
entity identities → retrieval may use entity/relation structure. This wiring
belongs after the D2-A3 role decision / D3 as appropriate. D2-A0/A1 do not
replace current retrieval shortcuts.

## 22. Explicit out-of-scope items

D2-A0/A1 must not: redefine `SAME_AS`; add a parallel ontology; turn related
entities into identity; reclassify D1 objects to ease resolution; use
relation similarity as identity evidence without the identity contract;
redesign the analyzer; migrate query expansions; add aliases beyond the
governed contract; enable `identity_relation` resolution in production;
change production retrieval/fusion/selector; use protected evaluation data.

## 23. Frozen decisions and open questions

Frozen: the evidence hierarchy (Section 4); alias boundary (Section 5);
`SAME_AS` consumption rules (Section 6); matched ≠ canonical result contract
(Section 7); version rules (Section 8); status vocabulary (Section 9);
abstention-first principle (Section 10); thin mention interface (Section 11);
descriptive constraints (Section 12); query-expansion non-authority
(Section 13); shadow-only A1 (Section 14); A2 categories/metrics/accounting
(Sections 15–16); exposure rules (Section 17); A3 role gate (Section 20);
benchmark-independence (Section 19).

Open questions (deferred, to be resolved by evidence in A1/A2): the concrete
descriptive candidate-generation mechanism (deterministic lexical overlap vs
embedding-assisted candidate retrieval — Tier D constraints bind either
way); whether the C5 mention-extraction helpers are extended in place or
wrapped; the exact diagnostic schema field names (semantics frozen in
Section 7); the final A2 case list (built by the source-first process, not
now).
