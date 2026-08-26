# N3-E2 Final Validation Expansion Plan

Status: `EXPANSION2_CURATED / HUMAN_REVIEW_PENDING`

Dataset: `novel-v1-validation-0.2.0`

## Starting state

The N3 pilot remains complete and immutable. After recording Li's
authoritative review of N3-E commit
`fa902109123c17b92297c6839fd4664c659ff3c5`, the starting state for this final
small expansion audit was:

- 12 loaded questions;
- 12 independent families;
- 12 human-approved questions;
- 6 `split_frozen` pilot questions;
- 6 approved N3-E questions that are not yet frozen;
- 0 pending questions.

No validation, novel-dev, C8, or holdout outcome was inspected.

## Goal

Curate one small final outcome-blind validation expansion batch. The preferred
center is approximately three candidates; two to four may be admitted only if
they arise naturally from strong locked-source support.

The authoritative N0 target is approximately 15 total `novel_validation`
questions. This is a quality target, not a quota. Weak, redundant, or
artificially balanced records are not admissible merely to reach a number.

## Isolation methodology

### Exposed Gold

Each candidate must express a new minimum user information need. Overlap with
Gold in intent, task form, entity, subsystem, repository, source file,
documentation page, or supporting evidence is allowed. Semantic duplicates,
paraphrases, mechanical entity substitutions, and narrower or broader versions
of the same minimum answer are rejected.

### Novel families

Strict semantic-family isolation applies against all 28 frozen `novel_dev`
families and all validation families vf001-vf012. Every admitted record was
compared with the complete validation-family boundary list, not only the
frozen pilot. A different class, detector, method, or path does not establish
independence by itself.

## Static support audit

The audit was deliberately small and source-first. It inspected:

- the RhoTuple n-tuple tutorial and its candidate-row persistence contract;
- the PandaRoot runtime-database tutorial's parameter object, container
  factory, and task-access roles;
- the DalitzGUI tutorial's coherent/incoherent and projection behavior;
- the QuickAna tutorial as a possible high-level analysis interface;
- PndPrintFairLinks documentation and implementation as a possible provenance
  diagnostic.

Three strong regions survived. QuickAna was rejected because its broad
one-line combination of decay combinatorics, PID, and fitting risked being a
wrapper-level restatement of vf002 and vf011. PndPrintFairLinks was rejected
because its documentation anchor is thin and the natural question surface
degenerated into a niche internal-tool inventory. No IDs were assigned to
discarded ideas.

## Admitted batch

- n913 / vf013: RhoTuple row creation, default handling, and TTree persistence;
- n914 / vf014: runtime-parameter serialization, factory registration, and
  task access;
- n915 / vf015: Dalitz interference and projection diagnostics.

All three are `draft`, have no reviewer or review timestamp, and have sidecar
lifecycle `draft`. Codex recommendations are advisory only.

## Outcome blindness

Sampling and annotation used only repository-visible questions, family
metadata, exposed Gold, the locked source manifest, and locked source content.
Agent-selected evidence, retrieval traces, QA answers, verifier/judge output,
C8 results, novel outcomes, and holdout material were not used.

## Stop condition

Sampling stopped immediately after three strong and mutually isolated
candidates were established. No further source region was sampled for cosmetic
intent, status, topology, repository, or representativeness balance.
