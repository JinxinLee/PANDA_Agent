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
  **Corrective term**: an inaccurate/nonexistent/malformed/premise-confused
  user expression safely redirectable to a governed entity with an explicit
  correction — not identity evidence.

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

### Tier G — governed explicit identity (may directly resolve; may canonicalize across co-referential records)

| Evidence | Resolve | Canonicalize | Constraints |
| --- | --- | --- | --- |
| Exact canonical object ID (governed ID stated in the question) | Yes | n/a (already canonical) | ID must exist; scope/version checks still apply |
| Accepted curated alias (`review_status = accepted`) | Yes | Yes, to its single target | boundary-safe occurrence; target exists; scope/version checks; multiple accepted targets → AMBIGUOUS |
| Accepted/reviewed `SAME_AS` edge | Yes | Yes, toward the canonical endpoint per D1 orientation | only accepted; pending/rejected never; conflicts → AMBIGUOUS (Section 6) |
| Exact source-native technical identifier with explicit source/type grounding (`locator.symbol` equality within locked source/version scope) | Yes | Only through governed identity evidence (G alias/SAME_AS); symbol equality alone does not canonicalize | uniqueness within scope; else REJECTED_VERSION/REJECTED_SCOPE/AMBIGUOUS |

### Tier S — strong structural/exact evidence (candidate generation + conditional resolve; never canonicalizes alone)

Exact canonical title; exact unique symbol without explicit type grounding;
exact path/locator; stable repository/document identifier. These may resolve
the **matched record** when uniqueness holds inside the plan's source/version
scope and the match kind is recorded as context-dependent evidence; any
competing same-tier match → AMBIGUOUS (D2 semantics; see Section 9). They must
never canonicalize a matched record to a **different** record without Tier G
evidence.

### Tier D — governed descriptive inference (bounded inferential resolution)

May generate candidates, score candidates, and — **when the full
descriptive-evidence bundle is satisfied** — directly resolve a mention to an
existing governed canonical entity. May not: create identity equivalence;
canonicalize one matched record into a different record; invent entities;
resolve solely because one similarity score is highest.

**Weak descriptive signal prohibition:** a single embedding similarity,
lexical-overlap score, retrieval top-1, LLM assertion, or one generic
descriptive feature must never directly resolve identity.

**Governed descriptive-evidence bundle** — a descriptive mention supports a
shadow resolution to an existing governed canonical entity only when ALL of:

1. all candidates come from the existing D1-governed entity space;
2. the mention is query-grounded;
3. the selected candidate is supported by multiple compatible, inspectable
   descriptive features or structured facts;
4. relevant source/type/version/context constraints are satisfied;
5. competing candidates are explicitly considered;
6. no plausible competing candidate remains unresolved at the same evidence
   strength;
7. the decision is auditable in diagnostics;
8. no new entity is invented;
9. no source-native → different canonical-record canonicalization is
   performed without Tier G identity evidence.

This is a **bounded inferential resolution**, not a stored identity
equivalence. No numeric thresholds are frozen in A0R1 (no
"similarity > 0.85"-style constants); D2-A1 chooses a deterministic or scored
implementation that satisfies these semantic requirements, and D2-A2 evaluates
whether it actually does.

**Descriptive resolution vs canonicalization (critical distinction):**
descriptive evidence may identify an existing canonical entity **directly**
when the mention is describing that canonical entity itself — e.g. "the model
used to extract luminosity from the LMD angular distribution" may resolve to
`concept.luminosityfit.luminosity_fit_model`, and "the step that reads the
first PID output and writes the boost ROOT file" may resolve to
`workflow.restgas.first_pass_poca`, when the bundle is satisfied. But
descriptive evidence must not canonicalize one matched source-native record
into a different canonical record: `PndLmdModelFactory` must not be
transformed into that concept merely because the class implements it —
`IMPLEMENTS` remains a non-identity relation, and cross-record
canonicalization still requires Tier G evidence (accepted true alias, accepted
`SAME_AS`, or another explicitly governed identity mechanism).

### Tier N — non-authoritative support

Never sufficient for identity resolution by itself. Retained signals:
retrieval rank, BM25/dense rank, graph proximity, raw semantic similarity,
co-occurrence, ordinary non-identity relations, query expansions, unsupported
LLM assertion. Some Tier N signals may contribute to candidate generation,
but they do not become authority merely by aggregation unless the D2-A1
descriptive-evidence mechanism explicitly transforms them into auditable
Tier D evidence under the descriptive-evidence bundle.

No numerical confidence scale is introduced; the deterministic evidence tier +
ambiguity state is the authority signal. If any score exists it is diagnostic:
`score != authority`.

## 5. Alias contract, corrective terms, and existing-alias audit

`alias = another expression referring to the same entity`. Related terms are
not aliases. Prohibited as aliases merely because they are related:
concept ↔ implementation class; workflow ↔ macro; subsystem ↔ source file;
documentation ↔ concept; producer ↔ produced object; parent ↔ child; theory ↔
implementation; broad topic ↔ narrow entity. Alias rules inherited unchanged
from the D1 contract Section D (review states, provenance, single target,
English-only, no evaluation-derived aliases, conflict surfacing).

**Corrective term / premise-correction term (frozen distinction):** a user
expression that is inaccurate, nonexistent, malformed, or premise-confused,
but can be safely redirected to a relevant governed entity with an explicit
correction. It is **not co-reference identity evidence**. It may trigger a
correction message, generate a candidate, support safe user-facing
correction, and contribute to shadow diagnostics. It must not: be treated as
`SAME_AS`; silently canonicalize as if the mistaken term literally denoted the
target; or count as Tier G true-identity evidence.

**Deterministic D2 classification rule (no schema change):** for D2 purposes,
an accepted alias whose stored `correction_message` is non-null is a
**corrective term** (the correction documents that the surface form does not
literally denote the target as named); an accepted alias without a
correction message whose target identity is represented by the expression
itself remains a **true identity alias** (Tier G). D2-A1 must implement this
classification; it must not consume corrective terms as Tier G evidence.

**Existing alias audit (2 accepted, classified separately):**

1. `restgas_profile.txt` (generic_user_term → `configuration.restgas_profile`,
   non-null `correction_message`) — **corrective/premise-repair term, not a
   true identity alias**, for D2 purposes. The corpus states no literal file
   named `restgas_profile.txt` exists; the frozen distinction is
   `restgas_profile` = configuration key, `restgas_16012024_*.txt` = concrete
   input-file pattern, `restgas_profile.txt` = nonexistent/mistaken user
   expression. The three are not collapsed into one identity. The existing
   config row is retained unchanged (C5 compatibility); D2-A1 classifies it
   as corrective via the frozen rule above.
2. `*_pid_final.root` (file_pattern → `data_product.restgas.pid_final_root`,
   no correction message) — **remains a true identity alias**: the D1
   canonical data-product entity's own title/representation is exactly this
   file pattern, so the expression denotes the same entity. Audited
   separately; not demoted because of the corrective case above.

`configs/query_expansions.yaml` must not automatically become alias data; no
mass migration in D2 (D3/D4 own migration).

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
- `RESOLVED_MULTIPLE` — **only** when the mention/query semantics legitimately
  denote multiple entities: an explicit plural/collective request, a user
  asking for several named entities, or one mention intentionally referring
  to a set. This is a **valid resolution, not uncertainty**; all denoted
  entities are returned.
- `AMBIGUOUS` — the mention is intended to identify one entity, but multiple
  plausible candidates remain and the resolver cannot safely choose (same
  singular symbol in multiple scopes; same title on several entities; a
  descriptive phrase with two equally plausible candidates). No selected
  object.
- `UNRESOLVED` — no sufficiently grounded candidate exists.
- Preserved rejections: `REJECTED_VERSION`, `REJECTED_SCOPE`,
  `MISSING_TARGET` (existing C5 semantics unchanged).
- Unsupported mentions (no deterministic mention evidence at all) are simply
  absent from the receipt, not forced to UNRESOLVED — the receipt records what
  was interpreted.

**Deliberate D2 supersession of C5 collision semantics:** C5 returns
`RESOLVED_MULTIPLE` for "multiple distinct objects share the exact match";
that is historical behavior. **In D2, competing candidates for a singular
mention are `AMBIGUOUS`, not `RESOLVED_MULTIPLE`.** D2-A1 implements this in
the shadow resolver; C5 runtime code is not changed in A0R1.

Receipt accounting semantics (frozen for A1): `AMBIGUOUS` →
`ambiguous_mentions`; a valid `RESOLVED_MULTIPLE` result is a resolved
multi-entity result and must not be placed in the ambiguity bucket; A1 may
adjust the receipt structure accordingly. Future `fallback_required`
meaning: ambiguous/unresolved cases may require fallback; a valid
multi-entity resolution is not inherently fallback-worthy; corrective terms
may require correction/fallback depending on whether an authoritative target
is established. Not implemented in A0R1.

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

Frozen rules: **a descriptive paraphrase may generate or score candidates and,
when the governed descriptive-evidence bundle (Section 4, Tier D) is fully
satisfied, may directly resolve to an existing governed canonical entity;
semantic similarity alone must never become identity truth, and descriptive
inference must never canonicalize one matched record into a different
record.** D2-A1 must attach interpretable evidence/diagnostics for every
descriptive decision, recording at minimum: mention text; candidate set;
selected entity; evidence category = descriptive inference;
source/type/version constraints; the descriptive features or structured facts
used; competing candidates and why they were rejected; whether
canonicalization occurred; whether any exact/G/S evidence contributed; and
the abstention reason when unresolved. No opaque `confidence = 0.91` without
explanation. Candidates come only from existing governed entities (D1
canonical entities, source-native entities, accepted alias targets, accepted
identity-linked representations); **the resolver must not invent new
canonical objects at query time**; no unrestricted corpus-wide LLM entity
invention. Implementation choices (e.g. any embedding-based candidate
retrieval) belong to D2-A1 design within these bounds.

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

D2-A0R1 case-type clarifications (binding for A2):

- **Pure descriptive positive cases** (no exact alias/title/symbol/path
  present): expected behavior is correct descriptive resolution when the
  evidence bundle is sufficient, otherwise safe abstention (categories 6–8).
- **Corrective-term cases**: expected behavior is correction surfaced with no
  false Tier G identity claim. `restgas_profile.txt` may appear as a
  governance-type corrective example only if exposure policy permits; its
  exact wording must not drive A1 implementation beyond the frozen generic
  corrective-term mechanism.
- **Singular ambiguity cases**: competing candidates for a singular mention
  must produce `AMBIGUOUS` (category 9).
- **Genuine multiple cases**: if natural corpus examples exist, validate
  `RESOLVED_MULTIPLE`; if none exist, record applicability as unavailable
  rather than inventing artificial production behavior.

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

Evidence-validity accounting additionally distinguishes:

```text
true identity resolution        # Tier G/S evidence
descriptive inferential resolution  # governed Tier D bundle
corrective-term handling        # correction surfaced, no Tier G claim
```

These three authority categories must not be collapsed into one.

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
or phrase-specific candidate overrides (in particular, no
`if "restgas_profile.txt" then ...`-style rules — corrective handling is a
generic mechanism keyed on the frozen alias-classification rule, never on the
surface string). Any genuinely needed new alias must satisfy the governed
alias contract independently of the evaluation case.

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

Frozen: the evidence hierarchy (Section 4, including the governed
descriptive-evidence bundle and the descriptive-vs-canonicalization
distinction); alias/corrective-term boundary and the per-alias classification
(Section 5); `SAME_AS` consumption rules (Section 6); matched ≠ canonical
result contract (Section 7); version rules (Section 8); status vocabulary with
`RESOLVED_MULTIPLE` vs `AMBIGUOUS` semantics and the deliberate supersession
of C5 collision behavior (Section 9); abstention-first principle
(Section 10); thin mention interface (Section 11); descriptive constraints
and required diagnostics (Section 12); query-expansion non-authority
(Section 13); shadow-only A1 (Section 14); A2 categories/case-type
clarifications/metrics/accounting (Sections 15–16); exposure rules
(Section 17); A3 role gate (Section 20); benchmark-independence
(Section 19).

Open questions (deferred, to be resolved by evidence in A1/A2): the concrete
descriptive candidate-generation mechanism and how Tier N signals are
transformed into auditable Tier D bundle evidence (deterministic lexical
overlap vs embedding-assisted candidate retrieval — the bundle constraints
bind either way); whether the C5 mention-extraction helpers are extended in
place or wrapped; the exact diagnostic schema field names (semantics frozen
in Sections 7 and 12); the receipt-structure adjustment for valid
`RESOLVED_MULTIPLE` results and the refined `fallback_required` semantics
(meaning frozen in Section 9, implementation deferred to A1); the final A2
case list (built by the source-first process, not now).
