# H0 External Holdout Curation Plan

> **H0 CREATES NO REAL HOLDOUT CONTENT.**

## Purpose and scope

The external `novel_holdout` is the final blind question-distribution
generalization split for PANDA Agent. It measures new information needs over
the same locked authoritative source corpus used by the exposed Gold and
repository-visible Novel splits. It is not a corpus-shift benchmark.

This plan defines governance, curation boundaries, review authority, protected
storage, identity, and lifecycle. It does not instantiate a holdout package,
create a question or family, annotate Gold, or authorize an evaluation.

The planning center is approximately 15 high-quality questions. This is not a
quota. Quality and independent natural information needs take precedence over
count, symmetry, or distribution matching. A future H1 first batch may contain
roughly 6–8 strong candidates and must stop earlier if source-first quality is
weak. H2 exists only if further strong independent families are warranted.

## Authoritative corpus precondition

Holdout curation is confined to the corpus locked by
`data/manifests/source_manifest.json`:

- the three repository identities and exact commits;
- the three locked papers;
- the frozen PandaRoot Sphinx snapshot.

H0-P completed portable locked-repository resolution. Canonical snapshots are
resolved from `data/sources/repos/<repo_id>/<commit_sha>/`; both Novel static
validators pass with zero stale repository-path errors. H0-P changed local path
resolution only and did not change corpus identity.

PANDA Knowledge Bundle Prototype v2.0.0 is a derived representation. Its
chunks, KnowledgeObjects, indexes, embeddings, and retrieval objects are not
authoritative evidence and must not define Holdout Gold.

## Relationship to exposed references

Gold (`m6-benchmark-v2.6`, 120 questions) is an exposed benchmark-reference
proxy, not empirical user-frequency data. A holdout candidate may share a
source, repository, subsystem, detector, class, function, entity, intent, task
archetype, or evidence region with Gold. It must not duplicate Gold's minimum
information need or answer obligation.

**Gold requires a new information need.** Reject semantic duplicates,
paraphrases, and superficial task-form changes around the same obligation.

The frozen Novel references are exclusion boundaries:

- `novel_dev` 0.3.0: 28 active questions and 28 active families;
- `novel_validation` 0.2.0: 15 active questions and 15 active families;
- retired dev lineages `n011/nf011`, `n012/nf012`, and `n013/nf013` are never
  reusable.

A holdout candidate may share subject matter with a frozen family. Semantic
family identity is assessed jointly across minimum information need, requested
relation, answer obligation, critical evidence composition, reasoning
topology, and semantic task structure. A candidate must not belong to the same
family when these signals are considered together. Individual overlap in one
or more signals is allowed: the same reasoning topology, evidence shape,
subsystem, class, or entity alone does not establish a collision.

**Frozen Novel requires a new family.** The same rule applies against every
previously accepted holdout family.

## Outcome-blindness and annotation independence

Curators and reviewers may inspect only authorized static definitions,
curation metadata, schemas, governance, and the locked authoritative corpus.
They must not inspect retrieval, QA, judge, unsupported-claim, evaluation, C8,
Novel, or holdout runtime outcomes. PANDA Agent must not run during curation.

Question formulation, evidence selection, answer points, expected status, and
family assignment must be established independently from the locked source
corpus before final holdout evaluation. Agent-selected evidence, answers,
traces, weakness observations, and Knowledge Bundle retrieval objects are
prohibited.

If outcome-bearing information is exposed and could influence selection, the
affected candidate is ineligible for pristine holdout use and the incident
must be recorded and escalated to human authority.

## Two-phase sampling firewall

### Phase A — source-first formulation

**PHASE A IS REFERENCE-BLIND TO EXPOSED QUESTION/FAMILY CONTENT.**

Phase A may access only source-first material needed to formulate an
independent candidate:

- the locked authoritative source corpus;
- `data/manifests/source_manifest.json` for locked source identity;
- `docs/NOVEL_DATASET_CURATION_CONTRACT.md`;
- generic holdout-relevant governance;
- generic schema and format rules needed to draft a candidate;
- H0 source-first governance instructions;
- H0-P path and corpus-readiness information when needed.

Phase A must not access candidate-content comparison material:

- Gold question content;
- the Gold representativeness profile;
- raw `novel_dev` question content or semantic curation metadata;
- raw `novel_validation` question content or semantic curation metadata;
- `H0_FROZEN_FAMILY_BOUNDARY_REFERENCE.md`;
- accepted holdout-family content from earlier batches.

```text
locked authoritative source
-> natural PANDA information need
-> candidate information need and wording
-> minimum critical authoritative evidence
-> initial answer obligation
```

The candidate, independent source support, and initial answer obligation must
already exist before any comparison material is opened.

### Phase B — post-hoc collision audit

**CANDIDATE FORMULATION MUST PRECEDE GOLD/FAMILY COMPARISON ACCESS.**

Phase B may not begin until Phase A has produced all four prerequisites:

- a candidate information need;
- candidate wording;
- minimum critical authoritative evidence;
- an initial answer obligation.

Only then may Phase B access:

- exposed Gold question definitions;
- the Gold representativeness profile when needed for review;
- `H0_FROZEN_FAMILY_BOUNDARY_REFERENCE.md`;
- previously accepted holdout-family material needed for collision checking;
- raw frozen Novel definitions only when a boundary ambiguity cannot be
  resolved from the sanitized family reference.

The sanitized 43-family reference is the default frozen-family comparison
input. Raw frozen `novel_dev` or `novel_validation` question content and
semantic metadata are non-default, Phase-B-only, ambiguity-only inputs. They
must never be used to choose a sampling area.

```text
existing candidate
-> Gold minimum-information-need audit
-> novel_dev family audit
-> novel_validation family audit
-> accepted-holdout family audit
-> disposition recommendation
```

**The 43-family reference is an exclusion filter, not a sampling-gap map.**

An internal holdout-family collision requires `REVISE` or `REJECT`. Revision
is appropriate only when the same natural information need remains intact;
inventing a different task is new sampling, not revision.

## Candidate quality policy

### Representativeness

Use two independent signals:

1. benchmark-reference fit;
2. independent PANDA-domain relevance.

Classify a candidate as `representative` or `exploratory` through human
judgment. Do not reproduce Gold percentages, infer user traffic from Gold, or
impose quotas. Do not manufacture exploratory cases for diversity.

### Answerability

Task archetype and answerability are orthogonal. Existing schema-compatible
statuses include `answered`, `insufficient_evidence`, `version_conflict`, and
`clarification_required`. Do not manufacture non-answered cases for balance;
an all-answered holdout is acceptable when source-first curation yields it.

### Difficulty

Difficulty is independent of novelty. Assign it from the natural evidence and
reasoning structure. Do not add multi-hop structure, obscure wording,
ambiguity, or unnecessary composition to force diversity. There are no
difficulty quotas.

### Evidence

Use the minimum critical authoritative evidence footprint. Multiple evidence
groups require genuine composition. Every selector must be statically
resolvable under the locked corpus contract. Evidence topology must describe
the actual obligation, not inflate perceived difficulty.

## Candidate review rubric

Review considers:

- natural information need and naturalness;
- direct authoritative source support;
- Gold novelty;
- `novel_dev`, `novel_validation`, and accepted-holdout family isolation;
- natural difficulty and evidence topology;
- representativeness and expected status;
- contamination status.

Worker recommendations are `RECOMMEND_ACCEPT`, `RECOMMEND_REVISE`, or
`RECOMMEND_REJECT`. Governance review uses `ACCEPT`, `REVISE`, or `REJECT`:

- `ACCEPT`: need, evidence, novelty, isolation, and metadata are materially
  sound;
- `REVISE`: the same useful natural need remains, but wording, evidence,
  selectors, answer points, topology, classification, or metadata need repair;
- `REJECT`: the item duplicates Gold, collides with a frozen or holdout family,
  lacks support, is unnatural, is outcome-derived, or can be repaired only by
  inventing a new information need.

LLM and Worker judgments are advisory. The Holdout Governor may recommend a
disposition, but only a human reviewer can approve or authorize freeze. Never
fabricate reviewer identity, review time, approval, or freeze authorization.

## Namespaces and package identity

Reserve, without instantiating records:

- question lineage: `n801-n899`;
- semantic families: `hf001-hf099`.

Retired or materially replaced IDs and family lineages are never reused.

Proposed initial external package identity:

```yaml
dataset_version: 0.1.0
benchmark_version: novel-v1-holdout-0.1.0
dataset_identity: novel-v1-holdout-external
split: novel_holdout
release_eligible: false
```

H0 does not create this package.

## Protected storage firewall

Real holdout content must never enter `JinxinLee/PANDA_Agent` or its normal Git
history. Protected questions, answers, answer points, selectors, family
assignments, metadata, review packages, manifests, coverage reports, and
freeze reports belong in a separate access-controlled private repository or
equivalent external workspace, conceptually `PANDA_Agent_Holdout`.

The main development Agent must not access protected content before an
authorized final evaluation. The development process must not receive real
holdout questions, evidence, families, or outcome summaries.

## Lifecycle, freeze, and amendment

The conceptual lifecycle is:

```text
draft
-> curation review
-> novelty review
-> evidence review
-> approved
-> split_frozen
```

External records must use compatible stored lifecycle values without erasing
the independent conceptual review stages. **Approved is not split_frozen.**
Only explicit human finalization freezes a split.

Before freeze, approved content may be revised under human authority. After
`split_frozen`, question semantics, Gold answers, answer points, evidence
selectors, family assignment, and expected status are immutable except through
an explicit amendment with a new version and auditable human authorization.
Retired identities are not reused.

## Final-evaluation boundary

Real holdout content remains blind to the development process until an
explicitly authorized final evaluation. Curators do not inspect holdout
runtime outcomes during curation. A governance context that begins seeing real
protected content must not return to PANDA Agent tuning or development work.
Case-level results cannot be used to repair and rerun the same frozen release
attempt.

## Roadmap

```text
H0  Governance and curation protocol
 -> H1  Initial external source-first curation batch
 -> Human review
 -> H1-R1 only if revisions are required
 -> H2  Small final expansion/balancing only if quality warrants
 -> Human review
 -> HF  External holdout finalization/freeze
```

H0 creates governance only. H1 must operate in protected external storage and
does not start automatically.
