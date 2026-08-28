# H0 Holdout Worker Handoff

> **SANITIZED GOVERNANCE INPUT ONLY. NO REAL HOLDOUT CONTENT IS INCLUDED.**

## Role and authority

The future H1 Holdout Worker proposes a modest source-first batch of natural
PANDA information needs in a separate protected workspace. The Worker is not
the approving authority and must not instantiate protected content in
`JinxinLee/PANDA_Agent`.

Worker dispositions are advisory:

- `RECOMMEND_ACCEPT`;
- `RECOMMEND_REVISE`;
- `RECOMMEND_REJECT`.

The Holdout Governor may recommend `ACCEPT`, `REVISE`, or `REJECT`. Human
review is authoritative. Never fabricate reviewer identity, review time,
approval, or freeze authorization. Approved is not `split_frozen`.

## Authoritative source boundary

Use only the locked authoritative corpus declared by
`data/manifests/source_manifest.json`: the exact repository snapshots, locked
papers, and frozen Sphinx snapshot. H0-P provides portable canonical
repository resolution under `data/sources/repos/<repo_id>/<commit_sha>/`.

PANDA Knowledge Bundle Prototype v2.0.0 is derived and non-authoritative. Do
not curate from its chunks, KnowledgeObjects, indexes, embeddings, retrieval
objects, or Agent-selected evidence.

## Phase-scoped reference access

### Phase A access

**PHASE A IS REFERENCE-BLIND TO EXPOSED QUESTION/FAMILY CONTENT.**

Phase A may access only:

- the locked authoritative source corpus;
- `data/manifests/source_manifest.json` for locked source identity;
- `docs/NOVEL_DATASET_CURATION_CONTRACT.md`;
- generic holdout-relevant governance;
- generic schema and format rules needed to draft a candidate;
- H0 source-first governance instructions;
- H0-P path and corpus-readiness information when needed.

Before a candidate exists, the Worker must not access:

- Gold question content;
- the Gold representativeness profile;
- raw `novel_dev` question content or semantic curation metadata;
- raw `novel_validation` question content or semantic curation metadata;
- `H0_FROZEN_FAMILY_BOUNDARY_REFERENCE.md`;
- accepted holdout-family content from earlier batches.

### Phase B access

Phase B may begin only after Phase A has produced a candidate information
need, candidate wording, minimum critical authoritative evidence, and an
initial answer obligation. **CANDIDATE FORMULATION MUST PRECEDE GOLD/FAMILY
COMPARISON ACCESS.**

Phase B may then access:

- exposed Gold question definitions;
- the Gold representativeness profile when needed for review;
- `H0_FROZEN_FAMILY_BOUNDARY_REFERENCE.md`;
- accepted holdout-family material needed for collision checking;
- raw frozen Novel definitions only if a boundary ambiguity cannot be resolved
  from the sanitized reference.

The sanitized 43-family reference is the default frozen-family collision
input. Raw frozen `novel_dev` and `novel_validation` question content and
semantic curation metadata are non-default, Phase-B-only, ambiguity-only
inputs. They must be used only to resolve a collision boundary and never to
choose a sampling area.

## Forbidden material and runtime

Do not inspect retrieval, QA, judge, unsupported-claim, evaluation, Novel,
C8, or holdout runtime outcomes, traces, scores, performance summaries,
weakness summaries, or failure analyses. Do not manually inspect
`evaluation/baselines/replay/**`.

Do not run PANDA retrieval, QA, verification, judge, Vertex, embeddings,
Qdrant, SQL retrieval, indexing, reranking, or any evaluation during curation.
Do not derive candidates or evidence from Agent answers or selected evidence.

## Mandatory two-phase order

### First: Phase A — source-first formulation

```text
source anchor
-> natural PANDA information need
-> candidate question/information need
-> independent authoritative evidence
```

During Phase A, do not open the frozen-family reference and do not use frozen
families, Gold content, the Gold profile, raw frozen Novel material, or prior
holdout-family content to choose a subject. Establish the candidate wording,
minimum critical source support, and initial answer obligation independently.

### Then and only then: Phase B — collision audit

```text
existing candidate
-> Gold audit
-> novel_dev family audit
-> novel_validation family audit
-> accepted-holdout family audit
-> recommendation
```

The family reference is an exclusion filter only. It is not a sampling-gap
map and must not be used to identify uncovered topics.

## Novelty and family isolation

Against exposed Gold, reject a semantic duplicate, paraphrase, identical
minimum information need, or superficial task-form change around the same
answer obligation. Shared sources, entities, subsystems, intents, or task
archetypes are allowed.

**Gold requires a new information need.**

Against the 28 frozen `novel_dev` families, 15 frozen `novel_validation`
families, and every accepted holdout family, semantic-family identity is
assessed jointly across minimum information need, requested relation, answer
obligation, critical evidence composition, reasoning topology, and semantic
task structure. A candidate must not belong to the same family when the
signals are considered together. Individual overlap in one or more signals is
allowed: the same reasoning topology, evidence shape, subsystem, class, or
entity alone does not establish a collision.

**Frozen Novel requires a new family.**

A collision with an accepted holdout family requires revision or rejection.
Revision may preserve the same natural information need; it must not disguise
new sampling as a repair.

## Independent annotation and evidence

Gold annotation must be performed directly against the locked authoritative
source corpus before final evaluation. Use the minimum critical evidence
footprint. Multiple evidence groups are allowed only for genuine composition.
Selectors must resolve statically under the locked corpus contract.

Never use PANDA answers, retrieval-selected evidence, QA-selected evidence,
judge feedback, outcome observations, or Knowledge Bundle retrieval objects.

## Candidate quality and review

Review each candidate on:

1. natural information need;
2. authoritative source support;
3. Gold novelty;
4. `novel_dev` family isolation;
5. `novel_validation` family isolation;
6. accepted-holdout family isolation;
7. naturalness;
8. natural difficulty;
9. representativeness;
10. evidence topology;
11. expected status;
12. contamination.

Representativeness uses two signals: benchmark-reference fit and independent
PANDA-domain relevance. Gold is a benchmark proxy, not user-frequency data.
Candidates may be `representative` or `exploratory`; do not impose quotas or
manufacture exploratory cases.

Difficulty follows the natural task and evidence structure. Do not create
artificial multi-hop reasoning, ambiguity, obscure wording, or composition.
Task archetype and answerability are orthogonal. Do not manufacture
`insufficient_evidence`, `version_conflict`, or `clarification_required` cases
for balance. All-answered is acceptable.

Disposition meanings:

- `ACCEPT`: semantic need, evidence, novelty, isolation, and metadata are
  materially sound;
- `REVISE`: the same natural need remains useful, but wording, evidence,
  answer points, selectors, topology, classification, or metadata need repair;
- `REJECT`: Gold duplicate, frozen-family collision, holdout-family collision,
  inadequate support, unnatural task, outcome-derived design, or repair would
  require inventing another information need.

## Size, namespaces, and package identity

The overall planning center is approximately 15 high-quality questions, not a
quota. H1 should normally propose a modest first batch of roughly 6–8 strong
candidates and stop earlier if source-first quality is weak. H2 is optional
and exists only if additional strong independent families are warranted.

Reserved namespaces:

- questions: `n801-n899`;
- families: `hf001-hf099`.

Do not reuse retired or materially replaced identities.

Proposed package identity, not instantiated by H0 or this handoff:

```yaml
dataset_version: 0.1.0
benchmark_version: novel-v1-holdout-0.1.0
dataset_identity: novel-v1-holdout-external
split: novel_holdout
release_eligible: false
```

## Protected storage

All real holdout questions, annotations, answer points, selectors, family
assignments, metadata, review packages, manifests, reports, and freeze records
must remain in a separate access-controlled private repository or equivalent
external workspace, conceptually `PANDA_Agent_Holdout`.

Never commit protected content to `JinxinLee/PANDA_Agent` or its Git history.
The main development Agent must not access protected content before final
authorized evaluation.

## Lifecycle and amendment

Conceptual lifecycle:

```text
draft
-> curation review
-> novelty review
-> evidence review
-> approved
-> split_frozen
```

Use schema-compatible stored states while preserving independent reviews.
Human finalization alone authorizes `split_frozen`. Before freeze, approved
items may be revised under human authority. After freeze, semantic content,
Gold, answer points, selectors, family, and expected status change only through
explicit amendment and versioning. Never reuse retired IDs.

## Contamination accounting

For every candidate and batch, truthfully record at least:

- `agent_outcome_seen_before_freeze: false`;
- `evidence_selected_from_agent_output: false`;
- whether any retrieval, QA, judge, Novel, C8, or holdout outcome was exposed;
- whether all evidence came directly from locked authoritative sources;
- who performed each human review and freeze authorization, when genuinely
  supplied by that human.

## Stop conditions

Stop and escalate to the human authority if:

- the locked source identity or exact snapshot cannot be verified;
- source support is inadequate or selectors cannot resolve statically;
- a candidate duplicates Gold or collides with a frozen/accepted family and
  cannot be repaired without inventing a new need;
- outcome material, Agent-selected evidence, or protected-content leakage may
  have influenced curation;
- storage is not access-controlled and separate from the development repo;
- reviewer approval or freeze authorization is missing;
- a requested change would silently mutate frozen semantic content;
- package or schema requirements conflict and require explicit governance
  review.

Do not proceed to final evaluation from an unresolved stop condition.
