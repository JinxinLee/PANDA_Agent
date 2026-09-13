# F6-A2-FR2 — Bounded Product Repair and New Candidate Development

Decision: **F6-A2-FR2 = COMPLETE / PASS / RESIDUAL_PRODUCT_MECHANISMS_REPAIRED_AND_NEW_CANDIDATE_DEVELOPED.**

Development task (zero scientific/evaluation calls). Gold v2.9
(`eaacd3ed…`) and calibration v6 are the stabilized authority for this
development; they are not modified. Attempt 2 remains COMPLETE / FAIL under
v2.6; no retroactive rescoring.

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## 1. Starting state and authority verification

- Starting HEAD `7411caa9e2ae203dfaaa7442dfa560c95eb4836e`
  ("Create Gold v2.9 forward-only successor"); worktree clean.
- v2.9 dataset SHA re-verified: `eaacd3ed…` (match); calibration
  `phase_b_t3_product_language_scope_v6` compatible; formal-English selector
  re-derived: 59 IDs, `e27ef67a…`.

## 2. R0 — defect map rebased against v2.9

All eight prior residual targets remain applicable under the stabilized
v2.9 contract (the forward-only changes added equivalent repo-source
selectors and retired stub selectors; none removed the evidence-group or
answer-point requirements these mechanisms failed):

| case | v2.9 contract component | attempt-2 observed behavior | mechanism | still applicable |
| ---- | ----------------------- | ---------------------------- | --------- | ---------------- |
| g013 | g013.e1/e2 documentation groups | 5 satisfying objects selected but uncited; answer asserted evidence does not document task lifecycle | A (+D-style claim) | yes |
| g016 | g016.e1 sphinx documentation page; documentation obligation | 4 satisfying objects selected; answer cited only code | A | yes |
| g022 | g022.e2 PID tutorial page | single satisfying object selected but dropped | A | yes |
| g060 | g060.e1 pflueger pages; paper+code obligation | both paper objects selected; final evidence code-only | A | yes |
| g011 | g011.e1 installation pages | 4 satisfying objects in pool, never selected | B | yes |
| g020 | g020.e1 POCA workflow readme section | satisfying objects in pool, never selected | B | yes |
| g021 | g021.e2 PndTargetGenerator.cxx | 9 satisfying index objects, zero in pool | C | yes |
| g113 | claim discipline | major-unsupported claim shipped in the final answer | D | yes |

## 3. Root-cause clusters and dispositions

### Cluster A — source-obligation evidence retention (REPAIRED)

- **Root cause**: question-grounded source obligations (F2-A5) gate
  *retrieval sufficiency* only. `_sufficiency` checks source types over the
  *selected* bundle evidence; once satisfied there, nothing aligns the final
  answer's claims with the obligation. The final-evidence projection is
  strictly `supported_claims → cited evidence`, so an answer whose claims
  never cite the obligated source type silently drops already-selected
  evidence for it (g013/g016/g022 documentation; g060 paper → dual-source
  0.0).
- **Repair** (`qa.py`): `_augment_source_obligation_evidence` — mirroring the
  existing `_augment_planned_locators` precedent: for each required source
  type not represented among the draft claims' citations, add at most one
  bounded, evidence-bound anchor claim (`source_obligation_<type>`) citing
  the best selected citation-eligible evidence of that type, and only when
  that evidence shares a question domain anchor with the query; the claim
  asserts only what the evidence itself shows ("The cited <type> at
  <location> documents <subject>"). No new sources, no unanchored
  attachment, no case IDs, no Gold literals; the claim then passes the
  normal semantic verification like any other.
- Supporting helper: `_primary_evidence_source_type` (single classifier
  mirroring the existing sufficiency obligation logic).
- Evidence projection afterwards: `supported_claims → cited evidence`
  naturally includes the obligated type **because the answer now actually
  makes a supported claim for which that evidence is relevant** — the
  contract required by §8, not arbitrary attachment.

### Cluster D — unsupported-claim revision discipline (REPAIRED)

- **Root cause**: `_verify` correctly excludes unsupported claims and routes
  to the one bounded revision; `_revise` merges supported + revised claims
  and re-enters them for a second verification. The semantic verifier is a
  model: the same, materially unchanged text can flip to `supported` on the
  second pass, so a claim already found unsupported survived into the final
  answer as an asserted fact (g113).
- **Repair** (`qa.py`): `_revise` now records the normalized text of each
  claim just found unsupported and drops any revision that restates it with
  an identical normalized text — the same text cannot both lack and carry
  evidential support, so the conservative verdict stands. Substantively
  narrowed/reworded revisions pass and are re-verified normally. No severity
  threshold is invented; ordinary verifier criticism of other claims is
  untouched; the verifier result remains visible in `verification_errors`.

### Cluster B — pool→final selection (DEFERRED_NO_SAFE_GENERIC_FIX)

- g011/g020: satisfying objects reach the candidate pool but not the final
  selection. A generic diversity/completeness rule inside
  `select_final_evidence` would reshape ranking behavior for the whole
  product and risks retrieval precision regressions that cannot be measured
  without scientific calls. Deferred rather than benchmark-hacked; FR1
  classified both cases MIXED (partial Gold-contract component).

### Cluster C — genuine retrieval miss (DEFERRED_NO_SAFE_GENERIC_FIX)

- g021: the restgas fork's `PndTargetGenerator.cxx` (9 satisfying index
  objects) never entered the pool for a configuration-phrased query. Safe
  generic recall repair (query reformulation/expansion mechanisms) would
  recreate retired shortcut territory or require a new retrieval subsystem;
  deferred per §14.

## 4. Focused verification (test-first)

New `ResidualRepairTests` (red before repair, green after):

- identical restatement of an unsupported claim is dropped from the revision
  merge; a substantively rewritten revision survives (positive + control);
- source-obligation anchor claim added for an uncovered required type;
- no augmentation when the type is already cited;
- no augmentation without a question-anchor overlap;
- single-source answers unaffected.

Updated: `test_external_identifier_answer_revision_integration` now uses a
substantively rewritten revision sentence (the identical-restatement case is
exactly what the new discipline drops), preserving the QA-M1 sanitization
contract on the revise path.

Results: `test_qa.py` + `test_retrieval.py` 269 passed + 50 subtests; the
QAAgent-dependent suites show exactly the pre-existing baseline failures
(19 d4_a5 + 5 e2/e1, previously verified against unmodified HEAD via stash)
— zero new regressions.

## 5. Integrity

```text
Gold scientific runs = 0
novel_dev access = 0
novel_validation access = 0 (PRISTINE_FOR_CURRENT_LINEAGE)
holdout access = 0
protected-content leakage = 0
Gold changes = 0; evaluator changes = 0; threshold changes = 0
```

## 6. New candidate development state

```text
NEW_CANDIDATE_DEVELOPMENT_HEAD = <product-fix commit "Repair residual answer evidence and claim handling">
candidate frozen = false
Attempt 3 preregistered = false
Attempt 3 executed = false
```

## 7. Next action

```text
NEXT_TASK_RECOMMENDATION =
F6-A ATTEMPT 3 / NEW CANDIDATE PREREGISTRATION AND FREEZE
(new candidate identity; new preregistration bound to m6-benchmark-v2.9 and
calibration v6; same formal-English selector contract; same protected-cohort
discipline)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
