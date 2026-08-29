# PANDA Agent — Phase D1-A0: Concept/Entity Schema Inventory and Identity-Contract Freeze

> Status: `D1-A0 = COMPLETE / CONTRACT_FROZEN` (2026-08-29);
> `D1-A0R1 = COMPLETE / CONTRACT_REPAIRED_AND_REFROZEN` (2026-08-29);
> `D1-A0R2 = COMPLETE / FINAL_SEMANTIC_BOUNDARY_AMENDMENT` (2026-08-29);
> `D1-A1 = COMPLETE / PASS` (2026-08-29) — implemented per Sections D/E/F/K
> with no architectural change; `D1-A1R1 = COMPLETE /
> PROVENANCE_AND_PERSISTENCE_REPAIR_PASS` (2026-08-29) — provenance is
> grounded in resolved evidence versions with inspectable-locator evidence
> and per-path resolution accounting, and `parent_object_id` persists
> canonically as `metadata.parent_object_id` with a frozen reload contract;
> `D1-A2 = COMPLETE / REPRESENTATIVE_KNOWLEDGE_MATERIALIZED` (2026-08-29) —
> small representative batch materialized (model concept + first-pass POCA
> process, FORMALIZES/IMPLEMENTS/CONSUMES/PRODUCES patterns, one WorkflowStep;
> `SAME_AS` legitimately not exercised, see `docs/EVALUATION_STATUS.md`);
> `D1-A2R1 = COMPLETE / CANONICAL_MODEL_CONCEPT_SEMANTIC_REPAIR_PASS`
> (2026-08-29) — the model concept corrected and renamed to
> `concept.luminosityfit.luminosity_fit_model` over the elastic
> antiproton-proton scattering angular distribution;
> `D1-A3 = COMPLETE / INTEGRITY_AND_COMPATIBILITY_PASS` (2026-08-29) —
> deterministic parent/workflow integrity validators, the
> `load_structured_objects` structured read boundary, normalized/SQL
> round-trip and index-compatibility verification, and the tiny read-only
> structured smokes; **D1 overall `COMPLETE / PASS`**; implementation records
> in `docs/EVALUATION_STATUS.md`. D2 owns concept/entity resolution; D3/D4 own
> shortcut migration. No production behavior changed in any D1 task.

Repository provenance (recorded precisely; Git history is not rewritten):

- Audit base: `d684329` ("C8 A2 close out targeted applicability"); the audited
  knowledge schema, relation ontology, seed configs, storage, and resolver code
  are unchanged through the current HEAD.
- `f6d1b15` (local) committed the first D1-A0 closeout. At re-derivation time,
  HEAD already contained that commit, while the working tree carried
  **uncommitted inverse edits** restoring the three D1 documents to their
  pre-D1-A0 content. Those uncommitted inverse edits are recorded here but are
  **not part of Git history** — they are not a historical commit.
- `bedd24d` committed the re-derived D1-A0 contract (second freeze).
- Local main merged `origin/main` at `f45a55f`: origin commits `a3aebba` /
  `a11bd87` (holdout source-path portability in `src/panda_agent/source.py`
  and novel preflight tooling) and `73f3134` / `df77c88` (novel holdout
  curation documents and validation tooling) do not touch the knowledge
  schema, relation ontology, storage contracts, alias corpus, or
  `EntityResolver` audited here.
- `9587c3c` recorded that merge in this document's provenance wording.
- The D1-A0R1 repair was audited at HEAD `9587c3c` with a clean tree except
  the untracked `data/sources.zip`.

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

**Schema (`configs/knowledge_schema.yaml`)** — 37 base object types across
literature, code, documentation, and `concept` groups
(`physics_concept`, `algorithm`, `detector_component`, `document_reference`),
plus the derived `_chunk` suffix. Stable IDs derive from
`source_version_id + object_type + canonical_locator`.

**Ontology (`configs/relation_ontology.yaml`)** — 23 predicates (Section E).

**Storage (`src/panda_agent/storage.py`)** — PostgreSQL tables
`knowledge_objects`, `knowledge_aliases` (FK to objects, indexed on
`normalized_alias`), `relation_edges` (FKs on both endpoints, indexed on
`(subject_id, predicate)` and `(object_id, predicate)`), `relation_candidates`,
`workflow_steps`, plus Qdrant payload indexes on
`source_id/source_version_id/object_type/authority_level`.

**Ingestion (`src/panda_agent/ingestion.py`)** — curated seed objects and
relations loaded from configs with predicate validation against the ontology;
curated aliases resolved to real provenance objects with target-existence
validation; static-analysis `RelationCandidate` → `RelationEdge`
materialization by `RelationResolver` populates `source_version_ids` and
`evidence_object_ids=[subject_id]` for static-analysis edges.

**Curated seeds** — 22 seed objects (concepts, workflows, data products,
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
   `source_version_id` records the curated provenance version, not a claim
   that the concept is version-specific.
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
identity predicate) that D2 can implement this distinction without
re-deriving it from match strings.

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
4. **Abbreviations and canonical shorthands** (e.g. acronym forms such as
   "LMD" for the Luminosity Detector, shorthand forms for class names
   like `PndLmdAcceptance`) are legitimate aliases when the short form denotes
   the same entity.
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
   (`AMBIGUOUS`/`RESOLVED_MULTIPLE`), not silently resolve; ingestion must
   not accept two aliases differing only by normalization to different
   targets without an explicit conflict record.
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

1. **Already sufficient:** the 23 predicates cover the representative D1-A2
   shapes (Section I) without additions. Roadmap-suggested predicates are
   explicitly **not** added: `IMPLEMENTED_BY` (inverse of `IMPLEMENTS`),
   `DESCRIBED_IN` (covered canonically by `THEORETICAL_BASIS_FOR` /
   `OPERATIONALLY_DOCUMENTS` / `FORMALIZES` in documentation→object
   direction), `USES` (decomposes into `CALLS`/`READS`/`CONSUMES`/
   `PARAMETERIZES` with more precision), `PART_OF` (current structural
   containment is expressed by `parent_object_id` and workflow composition;
   introducing `PART_OF` would duplicate that), and `RELATED_TO` (rejected as
   an unbounded escape hatch). If D1-A1 adds `SAME_AS`, the resulting
   ontology accounting is 23 existing predicates + `SAME_AS` = 24.
2. **Identity predicate `SAME_AS` (frozen semantics):** the genuine semantic
   gap stands — no predicate means identity, and C5 recorded
   `IDENTITY_RELATION_SUPPORT = NOT_AVAILABLE`. D1-A1 may add exactly one
   predicate, `SAME_AS`, with the following frozen semantics:
   - `SAME_AS` may connect only two records that are **genuinely
     co-referential representations of the same entity** (e.g. two stored
     records denoting the very same source symbol or the very same domain
     entity, one of which must be merged or canonically aliased).
   - `SAME_AS` must **not** mean: concept → implementation; workflow → macro;
     algorithm → implementing class; producer → data product; documentation →
     concept; related concept → concept; or similar object → object. Those
     relationships use semantic relations such as `IMPLEMENTS`, `FORMALIZES`,
     `PRODUCES`, `EXTENDS`, `THEORETICAL_BASIS_FOR`, etc.
   - **Storage behavior (deterministic, amended in D1-A0R2):** `SAME_AS` is
     semantically symmetric but stores exactly one physical edge; query
     traversal treats it as bidirectional; no inverse edge is stored. Stored
     orientation by case:
     - **Case A — exactly one endpoint canonical:** store
       `noncanonical -> canonical`.
     - **Case B — neither endpoint canonical:** store once using
       deterministic stable ordering — the lexicographically smaller
       `object_id` as `subject_id`. This represents two equivalent
       noncanonical records whose canonical status is not yet assigned.
     - **Case C — both endpoints canonical:** invalid/pending conflict. Two
       canonical records asserting `SAME_AS` means the canonical identity
       model itself is in conflict; this must **not** silently fall back to
       lexical ordering. Accepting such an edge requires explicit
       reconciliation or demotion of one endpoint first; D1-A1 validation
       fails for an accepted canonical-canonical `SAME_AS`, and D1-A1 must
       not automatically merge canonical entities.
     - `edge_id` continues to derive from the stored triple via the existing
       `stable_id`.
   - **Validation scope (frozen in D1-A0R2):** deterministic code validation
     covers the structural `SAME_AS` contract only — endpoint existence,
     predicate validity, accepted review status, provenance completeness,
     version/scope validity, canonical-role conflict (Case C), deterministic
     stored orientation, and duplicate-edge rules. The semantic truth of
     co-reference is **not** inferred by code: `A SAME_AS B` must be supported
     by curated/reviewed evidence and governance. No fuzzy title similarity,
     dense similarity, broad path matching, LLM-generated equivalence, or
     retrieval co-occurrence may establish identity. Frozen terminology:
     **structural `SAME_AS` contract validation plus reviewed co-reference
     evidence.**
3. **Frozen boundaries for overlapping predicates** (make D1-A1 deterministic;
   descriptions are repaired only in D1-A1, not in A0R1):
   - `PRODUCES` (amended in D1-A0R2): a **production/data-generation
     relation** — an executable process, workflow, code component, or other
     genuine producer generates a data product/result as an output of
     execution or transformation. `PRODUCES` must **not** be used merely
     because one stored artifact physically contains another object;
     structural containment and production are distinct semantics (Section
     E.2 item 4, `boost_root` → `event_poca` case).
   - `CONSUMES`: a workflow/code/component consumes a data product or input
     it reads during execution.
   - `PRODUCES_INPUT_FOR`: an object, data product, file pattern, or workflow
     result **serves as an input to** a downstream workflow, component, or
     subsystem. The accepted subject domain is broader than the current
     description ("a workflow"): data products and file patterns are valid
     subjects.
   - `PARAMETERIZES`: a value, data, or configuration-like object provides
     parameter values or a parameterized input (e.g. a configuration key whose
     value selects an input file). It supplies *what* runs with.
   - `CONFIGURES`: a configuration entity controls or selects behavior,
     settings, or mode of another object (component/workflow). It selects
     *how* something runs. `restgas_profile` selecting a concrete input
     profile file is `PARAMETERIZES`, not `CONFIGURES`.
4. **Audit of all 16 accepted seed relations against predicate semantics**
   (compared in D1-A0R1, amended in D1-A0R2; no relation migrated in A0R1 or
   A0R2). **C-class resolution ownership (frozen in D1-A0R2):** D1-A1 may
   resolve a C-class relation ambiguity only when the correct normalization
   can be expressed using already-existing entities and already-authorized
   predicates/structure. If the correct representation requires a new domain
   concept, a new workflow/entity, representative knowledge materialization,
   or source-backed semantic curation beyond existing records, D1-A1 must
   **not** invent the missing entity merely to close the ambiguity — it must
   preserve the relation as pending, record the exact deferred requirement,
   and hand it to D1-A2, which owns representative knowledge-set
   materialization. Final accounting: **8 conform / 5 A / 3 C**.
   - **Conforming (8):** karavdina `THEORETICAL_BASIS_FOR` →
     lmd_reconstruction, lmd_reconstruction `PRODUCES` lumi_trks_qa,
     effective-acceptance `IMPLEMENTED_AS_PIPELINE`,
     `PRODUCES_PROFILE_FOR`, `FORKED_FROM`, sphinx
     `OPERATIONALLY_DOCUMENTS`, restgas_profile_reconstruction `PRODUCES`
     boost_root (workflow producer), and second-pass PID `PRODUCES`
     pid_final_root.
   - **A — ontology description too narrow, usage semantically valid (3
     description families, 5 edges):** `PRODUCES_INPUT_FOR` says "a workflow
     produces an input used by another subsystem" but accepted usage has
     `data_product`→subsystem, `file_pattern`→workflow, and
     `data_product`→workflow subjects/objects (3 edges) — frozen boundary in
     item 3 governs; `CORRECTS` says "a correction object" but the accepted
     subject is a physics concept acting as the correcting factor (1 edge);
     `PARAMETERIZES` says "a value or data object" but the accepted subject is
     a `configuration_key` (1 edge).
   - **C — genuine ambiguity requiring future explicit treatment (3 edges):**
     1. pflueger `FORMALIZES` → `subsystem.luminosityfit.model_and_fit`: the
        description targets a *concept*, the actual target is the implementing
        subsystem. Decision policy frozen in D1-A0R2 (not the final relation):
        if repository evidence makes an existing-entity normalization
        unambiguous (e.g. re-pointing to `THEORETICAL_BASIS_FOR`), D1-A1 may
        normalize it; if the semantically correct structure is
        `paper FORMALIZES model_concept` + `subsystem IMPLEMENTS
        model_concept`, the missing model-domain entity belongs to D1-A2 —
        D1-A1 must not choose the weaker representation merely to eliminate
        all pending cases.
     2. `pid_root` —`PRODUCES_INPUT_FOR`→ `event_poca` (product → product).
        Candidate existing normalization: the consuming first-pass POCA
        analysis (`macro/target/ana_dpm.C`, referenced in the seed evidence
        note) as subject with `CONSUMES`. D1-A1 may normalize **only if** the
        consuming process is already represented as an existing object and
        the mapping is unambiguous; D1-A1 must not invent a new workflow
        entity, and must not widen `PRODUCES_INPUT_FOR`/`CONSUMES` solely to
        preserve the historical edge. Otherwise the ambiguity stays pending
        for D1-A2.
     3. `boost_root` —`PRODUCES`→ `event_poca` (reclassified A → C in
        D1-A0R2): the seed description states the boost ROOT output
        **contains** the `event_poca` tree — this is structural containment,
        not production/data-generation, so it must not be justified by
        broadening `PRODUCES` (item 3). Future representations to consider,
        in order: existing `parent_object_id`/composition structure; another
        already-existing structural mechanism; a later explicitly justified
        structural relation if existing architecture proves insufficient.
        No `CONTAINS`/`PART_OF` predicate is added in D1-A0R2; the seed
        relation is not modified in A0R2. D1-A1 may resolve it only if an
        existing representation is sufficient and unambiguous; otherwise the
        final normalization is deferred to D1-A2.
   - **B — seed predicate misclassified: none found.** No seed relation is
     reclassified in A0R1/A0R2.
5. **Inverse-direction policy:** one canonical stored direction per predicate
   as documented in the ontology; inverse traversal is derived at query time,
   never stored as a second edge. If a future need for stored inverses is
   proven, it requires a separate task. (`SAME_AS` is the one sanctioned
   single-edge symmetric exception with deterministic orientation, item 2.)
6. **Direction policy:** prefer the semantically primary direction —
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

1. Resolvable subject and object (already enforced by FKs / target
   validation).
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
  analyzer symbols with complete in-question support, accepted aliases
  matched by boundary-safe deterministic patterns.
- Match kinds: `accepted_alias` > `exact_symbol` > `exact_title` >
  `exact_path`; `identity_relation` is defined but unsupported
  (`IDENTITY_RELATION_SUPPORT = NOT_AVAILABLE`).
- Statuses: `RESOLVED_UNIQUE`, `RESOLVED_MULTIPLE`, `AMBIGUOUS`, `UNRESOLVED`,
  `REJECTED_VERSION`, `REJECTED_SCOPE`, `MISSING_TARGET`.
- Scope behavior: source allow-list (`target_repositories` + context +
  `curated_panda_domain`), locked-version rejection, ambiguity surfacing,
  no hidden selection, full `EntityResolutionReceipt`.

**D1 must provide (and nothing more):**

1. A governed target space: curated domain-level entities identifiable as
   such (Section B), so D2 can rank/abstain over both classes.
2. The alias contract (Section D) so `accepted_alias` remains the strongest
   resolution evidence with governed semantics.
3. An identity predicate (`SAME_AS`, Section E.2) with co-reference-only
   semantics and deterministic storage orientation, so `identity_relation`
   matching becomes implementable instead of structurally unavailable.
4. Machine-traceable relation provenance (Section F) so D2 candidates can
   cite auditable support.
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
3. Workflow → step: `workflow` object with `WorkflowStep` entries; ordering
   via `RUNS_BEFORE`.
4. Producer → data product → consumer: `workflow`/code —`PRODUCES`→
   `data_product` —`PRODUCES_INPUT_FOR`→ subsystem/workflow.
5. Configuration → workflow/component: `configuration_key` —`PARAMETERIZES`/
   `CONFIGURES`→ object.
6. Documentation/theory → concept: `thesis_section`/`sphinx_section` —
   `THEORETICAL_BASIS_FOR`/`OPERATIONALLY_DOCUMENTS`→ object.
7. Source object → domain-level entity: `class`/`function` —`IMPLEMENTS`→
   `physics_concept`/`algorithm`, or `EXTENDS` for subclass realization.
   `SAME_AS` is reserved for genuinely co-referential records of the very
   same entity (e.g. two stored records denoting the same source symbol that
   must be merged); a source-native implementation object and the domain
   concept it implements are normally **not** `SAME_AS`.
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

## K. D1-A1 implementation boundary (after D1-A0R2 amendment)

D1-A1 is authorized to implement exactly:

1. Add the single identity predicate `SAME_AS` to `relation_ontology.yaml`
   with the Section E.2 co-reference-only semantics, the Case A/B/C storage
   contract, and structural validation including canonical-canonical conflict
   detection. No other predicate is created. Resulting ontology accounting:
   23 existing predicates + `SAME_AS` = 24.
2. Add minimal identity-role provenance to curated domain-level seed objects
   (payload/metadata-level, Section B) — no new object types. This marker is
   also what makes the `SAME_AS` orientation rule deterministic.
3. Enforce the Section F provenance contract on curated seed relations in
   ingestion (populate `source_version_ids` / `evidence_object_ids` from
   evidence references declared in `seed_relations.yaml`; migrate the 16
   existing seed relations' evidence notes into machine-traceable evidence
   references, keeping prose only as a supplement).
4. Correct existing-predicate descriptions **only where the semantic boundary
   is already frozen and unambiguous** (Section E.2 item 3: `PRODUCES`,
   `PRODUCES_INPUT_FOR`, `CORRECTS`, `PARAMETERIZES`, `CONFIGURES`). This
   authorizes description repair only — no ontology expansion, no new generic
   predicates, no broad relation redesign, no benchmark-driven relation
   changes.
5. Normalize an ambiguous seed relation **only when existing entities and
   already-authorized predicates/structures are sufficient** (Section E.2
   item 4 C-class ownership rule). When resolution would require creating new
   representative domain entities or knowledge objects, D1-A1 must defer to
   D1-A2: preserve the relation pending and record the exact deferred
   requirement.
6. Extend schema/ingestion validation: endpoint existence, predicate
   validity, review status, provenance completeness, version/scope validity,
   structural `SAME_AS` contract validation (including Case C
   canonical-canonical conflict detection and deterministic orientation) plus
   reviewed co-reference evidence as the only path to semantic identity — no
   heuristic or automatic co-reference inference; extend or add focused T0
   schema/ingestion tests.
7. Any minimal storage/payload sync required by 1–6, following the existing
   metadata-sync pattern, with no embedding-text change and no re-embedding.

D1-A1 is NOT authorized to: create new concept/entity records merely to close
ambiguity; populate aliases; expand `EntityResolver` behavior; migrate query
expansions; add structural/data-flow predicates beyond the already-approved
`SAME_AS`; perform semantic co-reference inference; redesign the graph;
change production exact, fusion, or selector; tune against benchmarks; or
touch protected evaluation data.

---

## L. Query-expansion knowledge-debt inventory (D1-A0R1)

Static classification of representative patterns in
`configs/query_expansions.yaml` (39 rules inspected as committed at
D1-A0R1). No rule is modified, migrated, or disabled here; no evaluation
outcome was consulted. Stage boundary: **D1** defines entities, relations,
provenance, and the small representative knowledge set; **D2** resolves
terminology/paraphrases to canonical entities; **D3** runs the small
(~5–10-rule) structured shortcut-migration experiment; **D4** performs
incremental measured migration.

| Category | Representative patterns | Future owner |
| --- | --- | --- |
| Stable domain vocabulary | concept noun phrases in `concepts:` fields (e.g. `detector resolution`, `beam divergence`, `distributed target generation`) | Retain as ordinary vocabulary; D2 consumes as resolver input, no migration |
| Normalization / ASCII-alias routing | underscore/space variants routing (`event poca` ↔ `event_poca`, `event_poca_workflow_alias`) | Retain; D2 may own terminology normalization later |
| Genuine alias candidates | within-rule synonym trigger groups denoting one entity (`pvz efficiency`/`longitudinal efficiency`; `restgas acceptance`/`effective acceptance`) | D1-A2 curates under the Section D contract; D2 resolves |
| Phrase → concept/entity mapping | `concepts:` keyed by natural-language phrases per rule | D2 |
| Phrase → implementation/file shortcut | `symbols:` mapping phrases to files (`angular acceptance` → `data/PndLmdAcceptance.cxx`, `PndMasterRunSim` → `tools/MasterTasks/...`) | D3 experiment, then D4 |
| Workflow shortcut | `restgas_workflow_usage`, `target_macro_workflow_grouping`, `master_reconstruction_workflow` | D3/D4 |
| Data-product shortcut | `pid_two_pass_files` (`*_pid.root`/`*_pid_final.root` → macros) | D3/D4 |
| Negative-control / false-premise guard | `nonexistent_restgas_deconvolver`, `similarly_named_track_finders`, `version_mismatch_troubleshooting`, `acceptance_efficiency_disambiguation` | Conditional (frozen in D1-A0R2): **D4** when an already-proven generic replacement exists; **later generic false-premise / benchmark-dependency cleanup phase** otherwise. D2 may own disambiguation semantics |
| Answer-location shortcut | `paper_page_hints` fields (~15 rules pinning `li_2026`/`pflueger_2017`/`karavdina_2015` pages) | D3/D4 only where a generic structured replacement has been demonstrated; never re-encoded as D1 relations/aliases |
| Legacy multilingual compatibility debt | Chinese-language triggers across rules (reclassified in D1-A0R2) | Existing behavior preserved unchanged; not migrated into D1 aliases/entities; D2 is not expanded to multilingual resolution; these triggers are not part of the English product contract; future removal requires an explicit compatibility-cleanup task or later Phase-F-style cleanup. Aliases remain English-only |

This inventory defines future task boundaries only; it authorizes no
migration and must not be read as an implementation plan.
