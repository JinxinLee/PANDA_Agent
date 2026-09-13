# F6-A2-FR1 — Post-Attempt-2 Residual Exposed-Gold Failure Review

Decision: **F6-A2-FR1 = COMPLETE / PASS / RESIDUAL_FAILURES_CLASSIFIED.**

Review-only, zero scientific/model calls. The Attempt-2 terminal verdict is
preserved unchanged. Machine-readable companion:
`evaluation/f6_a2_fr1_residual_exposed_gold_failure_review.json`.
Immutable run receipt: `evaluation/F6_A2_IMMUTABLE_RUN_RECEIPT.md` (+ JSON).

## 1. Method

Contributor sets for all six failed gates were derived deterministically from
the immutable Attempt-2 records (`results.jsonl` + `gate_matrix.json` +
per-case traces + Gold v2.6 + index queries) — not from the closeout
narrative. Aggregation cross-check: the per-case missing-weight sum over the
49 answered cases (5.8333 final / 5.3333 critical) reproduces the gate
aggregates exactly (0.880952 / 0.891156). Each missing evidence group was
then attributed across three layers — index satisfiability, retrieval
candidate pool, trace-final evidence vs final answer evidence — using the
production `GoldEvidenceSelector.matches` semantics.

## 2. Contributor map (complete)

| gate | contributors |
| ---- | ------------ |
| final_evidence_recall (0.8810) | g001, g011, g013, g014, g016, g020, g021, g022, g044, g060 (one missing group each) |
| critical_final_evidence_recall (0.8912) | g001, g011, g013, g014, g016, g020, g022, g044, g060 (g021's missing group is non-critical) |
| required_source_coverage_answered (0.9592) | g016 (documentation missing), g060 (paper missing) |
| paper_code_dual_source_rate (0.0) | g060 |
| critical_answer_point_miss_count (4) | g001 p1, g005 p1, g013 p3, g022 p2 |
| major_unsupported_claim_count (1) | g113 claim_3_efficiency_empty_bin_diagnosis |

Diagnostic note (no gate impact): refusal/version-conflict cases
(g007, g012, g026, g042, g058, g108, g119) also carry unmatched evidence
groups in their provenance, but final-evidence recall does not apply to
non-answered cases, so they contribute to no failed gate.

## 3. Evidence-group attribution (10 gate-contributing groups)

Three-layer attribution result — **zero** groups are unsatisfiable in the
index and **zero** are selected-but-not-credited (no new evaluator defect):

| class | groups | cases |
| ----- | ------ | ----- |
| DROPPED_AT_FINAL_ANSWER_EVIDENCE (retrieval selected a satisfying object; the final answer evidence does not contain it) | g001.installation, g013.e1, g014.e2, g016.e1, g022.e2, g044.e1, g060.e1 | g001, g013, g014, g016, g022, g044, g060 |
| RETRIEVED_BUT_NOT_SELECTED (satisfying objects in the candidate pool, never in trace-final evidence) | g011.e1, g020.e1 | g011, g020 |
| RETRIEVAL_MISS (no satisfying object ever entered the pool) | g021.e2 | g021 |
| GOLD_SET_NOT_SATISFIABLE_IN_INDEX / SELECTED_BUT_NOT_CREDITED | 0 | — |

## 4. Classification per case

**PRODUCT_DEFECT (6):**

- **g013** (evidence recall + critical recall + p3): five satisfying objects
  (sphinx Running/Macros, MasterTasks, PndMasterRunSim documentation) were in
  the trace-final evidence but the answer cites none of them and asserts
  "the supplied evidence does not document lower-level task lifecycle stages"
  — a false insufficiency claim against evidence already retrieved and
  selected. Same family as the attempt-1 false-absence pattern, now inside an
  answered response. High confidence.
- **g016** (evidence recall + required-source coverage): the answer cites
  only `PndMasterRunSim.h` twice; four satisfying sphinx DPMGenerator
  documentation objects were selected but dropped, leaving the required
  `documentation` source type uncovered. High confidence.
- **g021** (evidence recall): the restgas fork's `pgenerators/Target/
  PndTargetGenerator.cxx` (9 satisfying index objects) never entered the
  candidate pool — pure retrieval miss on the implementation file the Gold
  contract names. Medium confidence.
- **g022** (evidence recall + p2): the single satisfying object
  (`tut_02_02_analysis_pid.html`) was trace-final but dropped; the answer
  identifies the Data Access page and merely mentions PID selection, never
  identifying the documented PID page that the query explicitly asks for.
  High confidence.
- **g060** (evidence recall + critical recall + required-source coverage +
  dual-source): both satisfying `pflueger_2017` paper objects were
  trace-final but the final answer evidence contains only `luminosityfit`
  code — the entire paper source is dropped, which alone zeroes the
  dual-source gate and fails the paper coverage obligation. The
  paper+code obligation is question-entailed by the preregistered contract.
  High confidence.
- **g113** (major unsupported claim): the answer generates a causal
  diagnosis ("numerator-empty bins arise when candidate tracks fail
  reconstruction selection", plus specific cut/profile assertions) not
  substantiated by its cited code/macro evidence; the verifier correctly
  flags it major-unsupported, but the unsupported claim still ships in the
  final answer. High confidence.

**GOLD_CONTRACT_DEFECT (2):**

- **g001** (evidence recall + critical recall + p1): the group's selectors
  accept only the rendered sphinx pages ("Installation —" /
  "Installation of PandaRoot for Developers"), while the answer cites the
  same installation documentation in its repository source form
  (`docs/Installation/Install_PandaRoot.rst`, `Install_Developers.rst`) —
  equivalent content for the identical user need. The p1 wording also
  requires stating "repository behavior is commit-specific", which the
  question does not entail. Forward-only recommendation: widen the group's
  `any_of` to the repository source paths or a content-equivalent selector.
  Medium-high confidence.
- **g014** (evidence recall): the group accepts only sphinx
  PndMasterTasks.html / Running.html; the answer cites
  `docs/Running/Running_Sequence.rst` (the Running page's repository source
  form) plus a weak sphinx index citation. Same source-form narrowness as
  g001. Medium confidence.

**MIXED (4):**

- **g005** (critical p1 only; evidence recall is fully satisfied): the
  answer cites the matched sphinx Docker/DevelopingInContainer page and
  answers the user need through a valid evidenced route (VSCode Dev
  Containers workflow), but never performs the "distinguish developing
  inside the container from merely running an image" contrast that p1 makes
  critical. Gold-criticality overreach and answer-content choice both
  contribute. Per the authorized instruction this was explicitly decided,
  not assumed. Medium confidence.
- **g011** (evidence recall): pool contains 4 satisfying installation-page
  objects that are never selected; the answer covers the native-vs-container
  need from the sphinx Docker page. Gold page-title narrowness + selection
  loss. Medium confidence.
- **g020** (evidence recall): the README "POCA Workflow" section objects
  reach the pool but are not selected; the answer describes the runall
  workflow without the POCA-specific second-pass semantics the group
  targets. Medium confidence.
- **g044** (evidence recall): the group locks pflueger_2017 pages 57/58/62;
  the answer answers the same theoretical need from li_2026 (and one
  satisfying pflueger object is dropped at answer time). Single-source
  lock + answer-side substitution. Medium confidence.

**EVALUATOR_DEFECT: none.** No selected-but-not-credited group exists; no
new inconsistency in the corrected R1/R1-R1/R1-R1-R1 evaluator semantics was
found.

**EXPECTED_STOCHASTIC_VARIATION: none stands alone.** The FR1-sensitive
cases changed exactly as intended; residual differences trace to identifiable
deterministic layers (selection/retention/retrieval) or to the Gold contract,
not to unexplained nondeterminism.

**INCONCLUSIVE: none** — every gate contributor reached a supported primary
classification (g020 with the lowest confidence, expressed as MIXED).

## 5. Attempt-2 verdict robustness (§22 check)

Even if every GOLD_CONTRACT_DEFECT and MIXED component were corrected in the
product's favor, the PRODUCT_DEFECT class alone keeps
critical_final_evidence_recall ≤ 0.929 (threshold 1.00),
critical_answer_point_miss_count ≥ 2 (threshold 0),
paper_code_dual_source_rate = 0.0 (g060), and
major_unsupported_claim_count ≥ 1 (g113). **Attempt-2 remains
COMPLETE / FAIL under any favorable correction**; the FAIL is robust.

## 6. Usage reconciliation (§8, most granular recoverable)

```text
qa_generation-labeled     67 calls / 1,566,586 tokens
qa_composer-labeled       46 calls /    75,888 tokens
product_verifier          NOT_SEPARATELY_RECOVERABLE_FROM_STORED_RECORDS
other runtime generation (query analyzer, semantic verification, coverage
review, and other unlabeled calls)  137 calls / 1,260,974 tokens
embedding                 64 calls / tokens NOT_SEPARATELY_RECOVERABLE_FROM_STORED_RECORDS
evaluation judge          62 calls /   410,203 tokens
total                     376 calls / 3,313,651 tokens (unchanged)
```

## 7. Provenance finding (§9)

Attempt-2 chronology: `619128b` → preregistration `3f1f16e` → candidate
frozen from `3f1f16e` → freeze bookkeeping `1f32eef` → scientific execution →
result `e3d7809`. The freeze bookkeeping commit populated
`implementation_head_lineage` fields inside the already-committed
preregistration JSON; no scientific contract changed and the candidate
manifest correctly freezes `3f1f16e`, so Attempt 2 is not invalidated.
Forward recommendation: future attempts keep the preregistration file
immutable after its commit and record freeze provenance in a separate
receipt.

## 8. Integrity

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
novel_validation = PRISTINE_FOR_CURRENT_LINEAGE
holdout access = 0
protected-content leakage = 0
Gold unchanged; thresholds unchanged; product code unchanged; evaluator unchanged
Attempt-2 raw records unchanged (receipt hashes recorded)
```

## 9. Next action

```text
NEXT_TASK_RECOMMENDATION =
smallest ordered sequence:
1) FORWARD-ONLY GOLD CONTRACT REVIEW
   (g001/g014 group source-form narrowness; g005 p1 criticality;
   g011/g044 single-source locks — forward-only, separately authorized)
2) F6-A2-FR2 / BOUNDED PRODUCT REPAIR AND NEW CANDIDATE DEVELOPMENT
   (answer-evidence retention/citation of already-selected evidence
   g013/g016/g022/g060; retrieval miss g021; unsupported-claim discipline
   g113; pool-to-final selection g011/g020)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
