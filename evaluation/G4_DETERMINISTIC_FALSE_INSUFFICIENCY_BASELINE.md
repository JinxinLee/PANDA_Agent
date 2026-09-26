# G4 Deterministic False-Insufficiency Baseline

## Decision and authority

**HARNESS IMPLEMENTATION: PASS. CURRENT T0 BASELINE: PASS.** Eighteen
synthetic/fake-provider controls passed against the unchanged product source.
Seven should-answer controls answered; ten must-abstain controls preserved the
expected refusal or incomplete-answer boundary; one sufficiency seam control
checked both available and missing required source types. No deterministic
false-insufficiency or under-conservative defect was established by this
matrix. This is a T0 contract baseline, not real-model or empirical
generalization evidence.

Every fixture supplies a constructed corpus fact, safe or unsafe provenance,
canonical obligations, and scripted model judgments. `qa.py` supplies the
actual G2 receipt, verification, routing, E3 (only in experimental mode), and
finalization behavior. A scripted review is test input, not independent
evidence that production's judgment is semantically correct. The expected
answerability class comes from the constructed fact and citation contract;
the product result is measured separately. No Gold or development question
content was used.

## Controls

`PASS` means the expected status, coverage, and safety assertion in
`tests/unit/test_g4_false_insufficiency_regression.py` passed. `N/A` means
coverage is not entered on that guard path. The owner column names the
transition under test, not a defect classification.

| ID | Class | Pair | Authoritative fact / obligation | Expected → observed status | Coverage and safety invariant observed | Owner | Result |
|---|---|---|---|---|---|---|---|
| A1 | Answerable | — | One ordinary point; exact admitted text and supported claim | `answered` → `answered` | `VALID`, complete, only cited `c1`/`e1` public | V1/G2/finalize | PASS |
| A2 | Answerable | P1 | Two independent points with exact admitted support | `answered` → `answered` | Both points complete; citations remain in constructed evidence | V1/G2/finalize | PASS |
| B9 | Must abstain at review checkpoint | P1 | Same two-point world, but second quote is structurally invented | `insufficient_evidence` → `insufficient_evidence` | `PARTIAL`; first `VALID` child survives, second remains missing, no A1 authority from malformed child | G2/finalize | PASS |
| A3 | Answerable | P2 | Corpus explicitly establishes the named order | `answered` → `answered` | Required relation `VALID` and complete | G1/G2/finalize | PASS |
| B2 | Unanswerable | P2 | Same order request; corpus says only that both objects are present | `insufficient_evidence` → `insufficient_evidence` | Valid unsatisfied relation; unsupported claim absent from public result | V1/G1/finalize | PASS |
| A-provenance | Answerable | P3 | Exact fact with direct citation-safe locator | `answered` → `answered` | Admitted `e1`; public evidence admitted | Admission/G1/finalize | PASS |
| B3 | Unanswerable under current citation contract | P3 | Same text, but Sphinx section locator is missing | `insufficient_evidence` → `insufficient_evidence` | No admitted backing or unsafe public citation | Admission/G1/finalize | PASS |
| A4 | Answerable | P4 | First relation already supported; one admitted-backed relation is repairable and A1 supplies it | `answered` → `answered` | One revision; V2 receives both canonical relations; complete final coverage | A1/V2/finalize | PASS |
| B7 | Must abstain at final checkpoint | P4 | Same first relation and A1 opportunity; second relation remains unsatisfied in V2 | `insufficient_evidence` → `insufficient_evidence` | One revision; V2 receives both relations; final coverage incomplete | A1/V2/finalize | PASS |
| A6 | Answerable, experimental mode | — | `runtime_e1_v2` E3 obtains genuinely missing second fact | `answered` → `answered` | E3 triggered once, point recovered on revision, final complete | E3/V2 | PASS |
| B1 | Unanswerable | — | No locked-corpus evidence for requested fact | `insufficient_evidence` → `insufficient_evidence` | Sufficiency false; no fabricated claim | Sufficiency/finalize | PASS |
| B4 | Unanswerable | — | Requested version conflicts with locked corpus | `version_conflict` → `version_conflict` | Distinct status; no mixed-version claim | Sufficiency/finalize | PASS |
| B5 | Unanswerable | — | Exact future runtime checksum cannot yet exist as evidence | `insufficient_evidence` → `insufficient_evidence` | Guard fires; no factual answer claim | Sufficiency/finalize | PASS |
| B6 | Unanswerable | — | No same-domain theorem for universal proof request | `insufficient_evidence` → `insufficient_evidence` | Guard fires; no factual answer claim | Sufficiency/finalize | PASS |
| B8 | Unanswerable | — | Only admitted text describes a record; encryption claim is unsupported | `insufficient_evidence` → `insufficient_evidence` | Valid review rejects `c1`; no public claim | V1/finalize | PASS |
| F1 | Answerable | P5 | Valid G2 receipt proves the only mandatory point complete | `answered` → `answered` | `coverage_blocked=false`; supported cited claim rendered | G2/finalize | PASS |
| F2/F3 | Must abstain at final checkpoint | P5 | Same admitted support, but the mandatory ordinary check is marked unsatisfied | `insufficient_evidence` → `insufficient_evidence` | `coverage_blocked=true`; safe `c1` retained with incomplete notice, never complete status | G2/finalize | PASS |
| S1 | Sufficiency seam, mixed | — | Same selected code evidence; source obligation is `code` then `paper` | sufficient true → true; false → false | Missing required source is explicit; no semantic answerability inferred | Sufficiency | PASS |

P1 changes only the second check's quote validity. P2 changes the fact that
establishes the requested relation (and the scripted judgment of that fact).
P3 changes citation provenance while keeping text fixed. P4 changes whether
V2 establishes the still-missing relation. P5 changes the one mandatory
ordinary check's scripted satisfaction, with G2 deriving the corresponding
coverage state. The pairs check both refusal and unsafe acceptance directions.
The B7, B9, and F2/F3 rows assert **safe behavior at an incomplete pipeline
checkpoint**. Their constructed corpus may still contain answerable facts;
an intentionally failed fake revision or malformed/unsatisfied fake review is
not evidence of a deterministic product defect. This distinction prevents a
correct final refusal from being misreported as corpus insufficiency or a
semantic verifier finding.

## Verification and interpretation

Commands run from the repository root using the existing local virtual
environment:

```text
..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_g4_false_insufficiency_regression.py
  18 passed

..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_g1_relationship_obligations.py tests/unit/test_g2_coverage_local_failure.py tests/unit/test_post_a5_c1_coverage_completeness.py tests/unit/test_e3_missing_point_retrieval.py::test_t4_runtime_genuine_missing_point_triggers_exactly_one_e3
  179 passed
```

The bare `pytest -q tests/unit/test_g4_false_insufficiency_regression.py`
command was unavailable on `PATH` (`pytest` command not found); the documented
virtual-environment invocation is the executed verification authority.

The first virtual-environment G4 execution returned **16 passed, 2 failed**
from **fixture construction** errors, not product RED: the scripted A1 revision
repeated the A0 claim and was correctly dropped
as `NORMALIZED_DUPLICATE`; the experimental E3 fake retrieval plan omitted
its required `source_budgets`. The authoritative fixtures were corrected to
provide distinct relation support and a valid plan. Normative expectations
were unchanged. The final G4 command passed all 18 controls. No product repair
or source modification occurred. The full suite and scientific evaluations
were not run.

The synthetic suite can establish only behavior for its constructed worlds.
It does not classify the six unresolved G3 insufficient answers, change G3's
`NO_CHANGE` admission result, or prove that real-model false insufficiency is
absent. No public partial-answer semantics were introduced. E3 is explicitly
an `EXPERIMENTAL_MODE_CONTROL`, not normal production behavior.

## Accounting, materiality, and next boundary

Scientific calls/tokens, real retrieval runs, QA evaluation runs, external
judge calls, new `novel_dev` content access, `novel_validation` content/outcome
access, holdout content/outcome access, and protected leakage: **all zero**.
The only material changes are tests, this audit artifact, and current-status
documentation. Product source/behavior, prompts, schemas, trace/manifest
schemas, retrieval, admission, verifier, finalization, Gold, and calibration
are unchanged. Product-behavior lineage remains
`a0106bd5eff93646f34f5e50e161e8be8a49d680`.

`PHASE_G = IN_PROGRESS / G4_DETERMINISTIC_HARNESS_COMPLETE`.

`G4 = DETERMINISTIC HARNESS COMPLETE / CURRENT T0 CONTROLS PASS /
EMPIRICAL REGRESSION NOT_ESTABLISHED / PRODUCT CHANGE NOT_AUTHORIZED`.

The smallest next recommendation is **G4 FOCUSED DEVELOPMENT
FALSE-INSUFFICIENCY DIAGNOSTIC DESIGN**. It should define independent
answerability review, uncertainty/denominators, and the minimum exposed or
fresh development evidence before any separately authorized model run. This
report does not authorize that task or any empirical evaluation.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`.
