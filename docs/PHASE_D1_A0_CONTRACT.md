# PANDA Agent — Phase D1-A0: Concept/Entity Schema Inventory and Identity-Contract Freeze

> Status: `COMPLETE / CONTRACT_FROZEN` (2026-08-29). This document is a static
> design contract, not an implementation. D1-A1 owns implementation; D1-A2 owns
> the small representative knowledge-set expression; D2/D3/D4 own resolver and
> migration work. No production behavior changed in D1-A0.

Source of truth at freeze time: HEAD `d684329` ("C8 A2 close out targeted
applicability"), clean tree except an untracked `data/sources.zip`.

---

## A. Current-state inventory

### A.1 What already exists

**Models (`src/panda_agent/models.py`)**

- `KnowledgeObject`: `object_id`, `object_type`, `source_id`,
  `source_version_id`, `title`, `text`, `authority_level`, `locator`
  (`SourceLocator`), `parent_object_id`, `metadata`, `canonical_locator`,
  `chunk_parent_id`, `token_count`, `embedding_eligible`. Every object is
  version-bound to one `source_version_id`.
- `KnowledgeAlias`: `alias_id`, `alias_text`, `normalized_alias`,
  `target_object_id`, `alias_kind`, `source_version_id`, `review_status`,
  `provenance_object_ids` (min-length 1), `correction_message`, `metadata`.
- `RelationEdge`: `edge_id`, `subject_id`, `predicate`, `object_id`,
  `source_version_ids`, `confidence`, `creation_method`, `review_status`,
  `evidence_object_ids`, `metadata`.
- `RelationCandidate`: candidate with `raw_target`, `resolution_scope`,
  `candidate_object_ids`, `resolution_status`.
- `WorkflowStep`: workflow/step identity, entrypoint, inputs/outputs,
  predecessor/successor links.
- Shared enums: `AuthorityLevel`, `ReviewStatus` (accepted/pending/rejected),
  `CreationMethod` (curated/static_analysis/explicit_reference/llm_proposal),
  `ResolutionStatus`.

**Schema (`configs/knowledge_schema.yaml`)** — 32 base object types across
literature, code, documentation, and `concept` groups
(`physics_concept`, `algorithm`, `detector_component`, `document_reference`),
plus `_chunk` derived suffix. Stable IDs derive from
`source_version_id + object_type + canonical_locator`.

**Ontology (`configs/relation_ontology.yaml`)** — 22 predicates (Section E).

**Storage (`src/panda_agent/storage.py`)** — PostgreSQL tables
`knowledge_objects`, `knowledge_aliases` (FK to objects, indexed on
`normalized_alias`), `relation_edges` (FKs on both endpoints, indexed on
`(subject_id, predicate)` and `(object_id, predicate)`), `relation_candidates`,
`workflow_steps`, plus Qdrant payload indexes on
`source_id/source_version_id/object_type/authority_level`.

**Ingestion (`src/panda_agent/ingestion.py`)** — curated seed objects and
relations loaded from configs with predicate validation against the ontology;
curated aliases resolved to real provenance objects with target-existence
validation; static-analysis `RelationCandidate` → `RelationEdge` materialization
by `RelationResolver` populates `source_version_ids` and
`evidence_object_ids=[subject_id]` for static-analysis edges.

**Curated seeds** — 23 seed objects (concepts, workflows, data products,
subsystems, repository-version entities, a configuration key, a file pattern)
and 16 accepted curated relations, all cross-object semantic relations.

**Resolver (`src/panda_agent/entity_resolution.py`, C5)** — `EntityResolver`
with mentions from explicit identifiers / accepted analyzer symbols / accepted
aliases; match kinds `accepted_alias > exact_symbol > exact_title >
exact_path`; statuses `RESOLVED_UNIQUE`, `RESOLVED_MULTIPLE`, `AMBIGUOUS`,
`UNRESOLVED`, `REJECTED_VERSION`, `REJECTED_SCOPE`, `MISSING_TARGET`;
source-scope and locked-version rejection; full `EntityResolutionReceipt`.
`IDENTITY_RELATION_SUPPORT = "NOT_AVAILABLE"` because no predicate means
identity. Retained as experimental/shadow; production exact remains
`LEGACY_EXACT`.

### A.2 Roadmap D1 categories vs. existing types

| Roadmap category | Existing representation | Verdict |
| --- | --- | --- |
| Concept | `physics_concept`, `algorithm` (concept group) | Reuse |
| Symbol | `locator.symbol` on code objects, not a standalone type | Reuse; do not mint `Symbol` objects |
| Class / Function / File | `class`, `function`, `method`, `source_file`, … | Reuse |
| Workflow / step | `workflow`, `workflow_step`, `WorkflowStep` | Reuse |
| DataProduct | `data_product`, `root_tree`, `file_pattern` | Reuse |
| Configuration | `configuration_key`, `environment_variable` | Reuse |
| PaperSection | `thesis_section`, `sphinx_section`, `document_reference` | Reuse |
| Algorithm | `algorithm` | Reuse |

Genuinely missing capability is **not** object types. The gaps are:

1. **No explicit source-native vs domain-level identity distinction** —
   currently implicit via object-type groups; not governed.
2. **No identity/equivalence relation predicate** — the ontology has none, and
   C5 recorded `IDENTITY_RELATION_SUPPORT = NOT_AVAILABLE`.
3. **Curated accepted relations are not machine-traceably provenanced** — they
   carry only `metadata.evidence_note` prose; `source_version_ids` and
   `evidence_object_ids` are empty (Section F).
4. **The alias corpus is tiny and unstructured** — 2 accepted aliases, no
   governance beyond target-existence and provenance-path resolution.

Everything else in the D1 card ("Concept, Symbol, Class, Function, File,
Workflow, DataProduct, Configuration, PaperSection, Algorithm") is a naming
difference, not a structural gap.

---

## B. Canonical entity model

Two identity classes are frozen:

**Source-native entities** — every `KnowledgeObject` that comes from an
ingestion pipeline (code, documentation, literature objects). Identity is
version-bound: the stable ID is a function of `source_version_id`,
`object_type`, and `canonical_locator`. They must remain version-bound. A
`repository_version` object (e.g. `repository.pandaroot.oct19`) is a curated
source-native container for a version scope, not a domain-level concept.

**Domain-level entities** — curated conceptual objects whose identity is
intended to persist across corpus/source versions: `physics_concept`,
`algorithm`, `workflow`, `subsystem`, `data_product`, `configuration_key`,
`file_pattern`, `document_reference` as currently used in
`configs/seed_objects.yaml`. Their `object_id` stays stable while the corpus
evolves; their connection to evidence stays versioned through relations. They
are additionally distinguished by `source_id` in a dedicated curated namespace
(the current seeds use conceptual IDs such as `concept.*`, `workflow.*`,
`data_product.*`; the resolver already special-cases `curated_panda_domain` as
an always-allowed source scope — this namespace becomes the canonical home for
domain-level entities).

**Identity/versioning contract:**

1. Domain-level entity identity may remain stable across source versions. Its
   `source_version_id` records the curated provenance version, not a claim that
   the concept is version-specific.
2. Realization and evidence remain version-bound. A domain-level concept
   connects to concrete implementations/evidence only through relations
   carrying explicit `source_version_ids`/evidence references.
3. Relations may connect stable concepts to version-bound implementation or
   evidence objects in either direction; the version scope lives on the edge.
4. No duplicate canonical node is created when an existing source-native
   `KnowledgeObject` already provides strong canonical identity (e.g. a class
   that uniquely implements a concept is the canonical anchor for that
   implementation; the concept relates to it, it is not mirrored as a new
   "concept implementation" object).

---

## C. Identity-evidence taxonomy

Freezing the C5 identity-strength finding as a D1 contract:

**Strong identity evidence** (sufficient for canonical resolution, individually
or per future explicit rules):

1. An **accepted reviewed alias** whose target object exists and passes
   source-scope/locked-version validation (already implemented in C5).
2. An **exact source symbol backed by a validated source locator**
   (`locator.symbol` on a source-native object within locked scope).
3. An **explicit canonical entity record** — a curated domain-level entity
   object in the curated namespace (future D1-A1 may formalize this as
   metadata, e.g. an identity-role marker; not required at A0).
4. A future **explicit identity/equivalence relation** (new predicate, Section
   E) with accepted review status and traceable provenance.
5. Another repository-backed source-native identity mechanism introduced with
   explicit justification in a later task.

**Weak retrieval evidence** (useful for retrieval; never sufficient alone to
establish identity):

- exact document/page/README/section titles;
- path or path basename matches;
- repository or product names;
- dense similarity or ordinary full-text match;
- a unique retrieval result without independent identity evidence.

Preserved C5 lesson: *a unique exact retrieval match is not automatically
canonical identity.* `exact_title` and `exact_path` remain match kinds useful
for candidate generation and receipts; D1 must not promote them to identity
semantics. D1-A1 must expose enough structure (identity-role metadata and/or
identity predicate) that D2 can implement this distinction without re-deriving
it from match strings.

---

## D. Alias contract

Core rule: **an accepted alias asserts identity-equivalence of two expression
forms for the same entity.** It is not a semantic-adjacency or
implementation-mapping device.

Frozen rules:

1. **Review states:** `accepted` / `pending` / `rejected` (existing
   `ReviewStatus`). Only `accepted` aliases are resolver-authoritative.
   Uncertain proposals stay `pending`.
2. **Provenance:** every alias requires resolved `provenance_object_ids`
   (existing ingestion already enforces min-length 1 and target existence).
   The alias must state `source_version_id` and `alias_kind`.
3. **Targets:** aliases may target both domain-level and source-native
   entities, but always exactly one `target_object_id`.
4. **Abbreviations and canonical shorthands** (e.g. "LMD" for Longitudinal
   Muon Detector–style acronyms, "PndLmdAcceptance" shorthand forms) are
   legitimate aliases when the short form denotes the same entity.
5. **Descriptive paraphrases** ("the detector resolution convolution") and
   **implementation-oriented descriptions** ("the class that writes the final
   PID file") are NOT aliases by default; they are relations or resolver
   candidate inputs. They become aliases only with independent, reviewable
   evidence that the phrase denotes exactly that entity (e.g. documented
   terminology), recorded as `pending` until reviewed.
6. **Prohibited:** evaluation-case-specific aliases, aliases derived from
   answer locations, multilingual aliases (English-only product scope), and
   aliases whose only evidence is that they co-occur with the target in Gold
   evidence.
7. **Duplicates/conflicts:** one normalized alias text mapping to multiple
   distinct accepted targets is an ambiguity the resolver must surface
   (`AMBIGUOUS`/`RESOLVED_MULTIPLE`), not silently resolve; ingestion must not
   accept two aliases differing only by normalization to different targets
   without an explicit conflict record.
8. **No mass population in D1.** D1-A0 adds no aliases; D1-A2 curates a small
   representative set under this contract.

---

## E. Relation contract

### E.1 Semantic groups of the current ontology

| Group | Predicates |
| --- | --- |
| Documentation/theory | `THEORETICAL_BASIS_FOR`, `FORMALIZES`, `OPERATIONALLY_DOCUMENTS` |
| Implementation | `IMPLEMENTS`, `IMPLEMENTED_AS_PIPELINE`, `EXTENDS` |
| Data-flow | `PRODUCES`, `CONSUMES`, `PRODUCES_INPUT_FOR`, `PRODUCES_PROFILE_FOR`, `GENERATES_CALIBRATION_FOR`, `CORRECTS` |
| Configuration | `PARAMETERIZES`, `CONFIGURES` |
| Dependency/call | `CALLS`, `INCLUDES`, `INHERITS`, `DEPENDS_ON`, `READS`, `WRITES` |
| Workflow | `RUNS_BEFORE` |
| Version/provenance | `FORKED_FROM`, `VERSION_INCOMPATIBLE_WITH` |

### E.2 Assessment

1. **Already sufficient:** the 22 predicates cover the representative D1-A2
   shapes (Section I) without additions. Roadmap-suggested predicates are
   explicitly **not** added: `IMPLEMENTED_BY` (inverse of `IMPLEMENTS`),
   `DESCRIBED_IN` (covered canonically by `THEORETICAL_BASIS_FOR` /
   `OPERATIONALLY_DOCUMENTS` / `FORMALIZES` in documentation→object
   direction), `USES` (decomposes into `CALLS`/`READS`/`CONSUMES`/
   `PARAMETERIZES` with more precision), `PART_OF` (current structural
   containment is expressed by `parent_object_id` and workflow composition;
   introducing `PART_OF` would duplicate that), and `RELATED_TO` (rejected as
   an unbounded escape hatch).
2. **Genuine semantic gap:** no **identity/equivalence** predicate. D1-A1 is
   authorized to add exactly one, `SAME_AS` (symmetric intent, stored once in
   the canonical direction defined by its provenance; the resolver treats any
   accepted `SAME_AS` as strong identity evidence, closing the C5
   `IDENTITY_RELATION_SUPPORT = NOT_AVAILABLE` gap). No other predicate is
   added in D1-A1.
3. **Overlaps to govern, not remove (no behavior change in D1-A0):**
   `PRODUCES_INPUT_FOR` vs `CONSUMES` (subject/object roles inverted);
   `PRODUCES_PROFILE_FOR`/`GENERATES_CALIBRATION_FOR`/`CORRECTS` are special
   cases of data-flow but carry domain precision that generic predicates
   would lose — retained. `PARAMETERIZES` vs `CONFIGURES`: `CONFIGURES` for
   configuration objects controlling components/workflows; `PARAMETERIZES`
   for value/data objects providing parameters. These boundaries are recorded
   as curation guidance.
4. **Inverse-direction policy:** one canonical stored direction per predicate
   as documented in the ontology; inverse traversal is derived at query time,
   never stored as a second edge. If a future need for stored inverses is
   proven, it requires a separate task.
5. **Direction policy:** prefer the semantically primary direction —
   documentation/theory objects → implemented objects
   (`THEORETICAL_BASIS_FOR`, `FORMALIZES`, `OPERATIONALLY_DOCUMENTS`);
   implementers → concepts (`IMPLEMENTS`); producers → products → consumers;
   configuration → configured. `RUNS_BEFORE` stays the single workflow-order
   predicate rather than adding `RUNS_AFTER`.

---

## F. Provenance contract

**Finding (audit):** model-level capability
(`source_version_ids`, `evidence_object_ids`, `review_status`,
`creation_method`, `confidence`, `metadata`) exceeds what curated relations
carry: `ingestion.py` materializes seed relations as
`CreationMethod.CURATED / ReviewStatus.ACCEPTED` with only
`metadata.evidence_note`. Static-analysis edges do populate
`source_version_ids` and `evidence_object_ids=[subject_id]`. Current curated
relations therefore rely on prose-only evidence.

**Frozen D1 contract for accepted curated relations (and accepted curated
objects/aliases):**

1. Resolvable subject and object (already enforced by FKs / target validation).
2. Version scope: non-empty `source_version_ids` naming the source version(s)
   the relation is grounded in, when the relation is version-bound; a curated
   relation between two domain-level entities across the locked corpus may
   carry the locked corpus version scope rather than being unscoped.
3. At least one `evidence_object_ids` entry — a resolvable `KnowledgeObject`
   (source-native object, section, or locator-bearing object) that a reader
   can inspect to audit the claim — where applicable. `evidence_note` prose
   may supplement but not replace machine-traceable evidence.
4. `review_status` and `creation_method` (already present).
5. Explicit provenance sufficient to audit why the relation exists.

Migration of the 16 existing seed relations to this contract belongs to
D1-A1 (Section K); D1-A0 changes nothing.

---

## G. Storage/ingestion implications (expected minimal D1-A1 surface)

- **No new table and no separate graph platform.** Existing
  `knowledge_objects` / `knowledge_aliases` / `relation_edges` /
  `relation_candidates` / `workflow_steps` satisfy D1.
- Most likely change class: **payload/metadata-only additions** (e.g. an
  identity-role marker on curated domain-level objects; provenance fields
  inside relation payloads) plus config/ingestion updates. A small
  schema/column change is permissible only if validation and queryability
  require it; the default is reuse.
- No mass re-embedding or index rebuild: D1 semantics attach to curated
  objects/aliases/relations and metadata; embedding-eligible objects keep
  unchanged embedding text. Qdrant payload-only updates follow the existing
  metadata-sync pattern if payloads must change.
- Existing validation (`validate_ingestion_contract`, seed predicate
  validation, alias target/provenance validation) is extended, not replaced.

---

## H. Resolver inheritance contract (what D1 must expose to D2)

Recorded current state of `EntityResolver` (C5, shadow-only):

- Mention sources: explicit identifiers in the raw question, C2-accepted
  analyzer symbols with complete in-question support, accepted aliases matched
  by boundary-safe deterministic patterns.
- Match kinds: `accepted_alias` > `exact_symbol` > `exact_title` >
  `exact_path`; `identity_relation` is defined but unsupported
  (`IDENTITY_RELATION_SUPPORT = NOT_AVAILABLE`).
- Statuses: `RESOLVED_UNIQUE`, `RESOLVED_MULTIPLE`, `AMBIGUOUS`, `UNRESOLVED`,
  `REJECTED_VERSION`, `REJECTED_SCOPE`, `MISSING_TARGET`.
- Scope behavior: source allow-list (`target_repositories` + context +
  `curated_panda_domain`), locked-version rejection, ambiguity surfacing,
  no hidden selection, full `EntityResolutionReceipt`.

**D1 must provide (and nothing more):**

1. A governed target space: curated domain-level entities identifiable as such
   (Section B), so D2 can rank/abstain over both classes.
2. The alias contract (Section D) so `accepted_alias` remains the strongest
   resolution evidence with governed semantics.
3. An identity predicate (`SAME_AS`, Section E.2) so `identity_relation`
   matching becomes implementable instead of structurally unavailable.
4. Machine-traceable relation provenance (Section F) so D2 candidates can cite
   auditable support.
5. Version/scope metadata unchanged in shape, so the existing
   `_row_scope_status` safety carries over.

D2 then extends the existing resolver (new match kinds / ranking / abstention)
rather than building a duplicate subsystem. D1-A1 must not change resolver
runtime behavior; production exact remains `LEGACY_EXACT`.

---

## I. Representative D1-A2 semantic patterns

Small cross-type patterns D1-A2 should be able to express with existing types
and predicates (expressiveness proof, not coverage; no evaluation-case
mappings):

1. Concept → implementation: `physics_concept` —`IMPLEMENTS`← `class`/
   `function` (concept may instead be subject with `IMPLEMENTED_AS_PIPELINE`
   for multi-step realization).
2. Algorithm → implementation: `algorithm` —`IMPLEMENTS`← code object, or
   `algorithm` —`FORMALIZES`→ relation from a thesis section.
3. Workflow → step: `workflow` object with `WorkflowStep` entries; ordering via
   `RUNS_BEFORE`.
4. Producer → data product → consumer: `workflow`/code —`PRODUCES`→
   `data_product` —`PRODUCES_INPUT_FOR`→ subsystem/workflow.
5. Configuration → workflow/component: `configuration_key` —`PARAMETERIZES`/
   `CONFIGURES`→ object.
6. Documentation/theory → concept: `thesis_section`/`sphinx_section` —
   `THEORETICAL_BASIS_FOR`/`OPERATIONALLY_DOCUMENTS`→ object.
7. Source object → domain-level entity: source-native object —`SAME_AS`→
   curated canonical entity, or `EXTENDS` for subclass realization.
8. Subsystem → component: `subsystem` with `parent_object_id`/composition
   structure (no new predicate).
9. Concept → source evidence: domain-level concept with relation edges whose
   `evidence_object_ids` point at locator-bearing source objects.

---

## J. Explicit non-goals

D1 must not become: a large ontology; a separate graph database or graph
platform; a benchmark mapping layer; a mass query-expansion migration (D3/D4);
a resolver replacement (D2); unvalidated automatic ontology generation; a
multilingual alias system; or a redefinition of production retrieval, fusion,
selector, exact-channel, or answer behavior. D1 adds no aliases beyond the
governed representative set in D1-A2 and never encodes evaluation answer
locations.

---

## K. D1-A1 implementation boundary

D1-A1 is authorized to implement exactly:

1. Add the single identity predicate `SAME_AS` to `relation_ontology.yaml`
   with the Section E semantics; no other predicate changes.
2. Add minimal identity-role provenance to curated domain-level seed objects
   (payload/metadata-level, Section B) — no new object types.
3. Enforce the Section F provenance contract on curated seed relations in
   ingestion (populate `source_version_ids` / `evidence_object_ids` from
   evidence references declared in `seed_relations.yaml`; migrate the 16
   existing seed relations' evidence notes into machine-traceable evidence
   references, keeping prose only as a supplement).
4. Extend schema/ingestion validation for the above (target existence,
   predicate validity, provenance completeness); extend or add focused T0
   schema/ingestion tests.
5. Any minimal storage/payload sync required by 1–3, following the existing
   metadata-sync pattern, with no embedding-text change and no re-embedding.

D1-A1 is NOT authorized to: populate aliases; change `EntityResolver` runtime
behavior or production retrieval/fusion/selector; migrate query expansions;
run anything beyond T0 plus a tiny deterministic smoke; or touch protected
evaluation data.
