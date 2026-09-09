# E2-A3-R2: Citation-Eligible Evidence Repair Preregistration

## Authority and immutable candidate

Starting HEAD: `ee719bde5331f4102c9d79dd929e31a8063fc9ae`.
The user explicitly authorizes this bounded repair, T0, complete historical
reconciliation, 12 fresh QA executions and six blinded judgments after freeze.
No further activation authorization is implied. Historical A3 FAIL/Q7 and R1
FAIL/P2_P6 remain authoritative. Historical P6 is neither waived nor repaired.

The candidate is the Git commit containing this protocol, the fixed manifest,
runner, tests, static result and draft report. Its full SHA is supplied as
`--candidate` and persisted in both raw and judged artifacts. Product code,
configs, prompts, tests, manifest, runner, gates and imported historical helper
implementations cannot change after this commit. No self-referential hash is
stored in the manifest. Four separate commits freeze candidate, raw, judgments,
and scientific closeout; no amend, squash or activation commit follows.

## Hypothesis and minimal intervention

The evidence-selection failure is admission of citation-incomplete Sphinx pages
to public claim generation. For `"sphinx" in source_id`, require truthy URL,
snapshot_date and section_path exactly as the existing verifier does. Other
source classes retain their existing admission behavior. Apply this projection
to initial answer and bounded revision `untrusted_evidence`; derive revision
`requirement_evidence` from the same projection using the unchanged helper.
Rejected references can remain in draft/error diagnostic material; they are not
offered as usable evidence. The original selected bundle remains intact.

No prompt/schema changes, verifier changes, section synthesis, source quotas,
backfill, extra retrieval, ranking changes, index/corpus/locator changes, public
DTO/API changes, compatibility removal or normalizer changes are permitted.
The normal default remains `legacy_question_core` before, during and after R2.
The full-module AST must equal the starting module after reversing only the
predicate and the three evidence-input substitutions (two lists and one map).

## Static gate definitions

All S gates must pass before scientific calls. Actual answer/revision/verifier
methods are exercised with fake model responses and a three-item mixed bundle.

| Gate | Required evidence |
| --- | --- |
| S1 | Predicate exactly matches frozen Sphinx citation contract |
| S2 | Initial answer offers section/code, excludes incomplete page |
| S3 | Revision and requirement mapping use the same eligible projection |
| S4 | Direct invalid-page claim still triggers incomplete web citation |
| S5 | Both historical A3 g013 offending IDs excluded |
| S6 | Historical R1 g027 runtime offending ID excluded |
| S7 | Recomputed 144 selected = 106 complete + 38 empty-section; all 38 excluded; 27 candidate edges = 24 complete + 3 invalid; 18 final edges complete |
| S8 | All 106 complete Sphinx occurrences retained |
| S9 | All non-Sphinx identities, order and payloads unchanged |
| S10 | Original retrieval bundle, ranking, trace, retrieval implementation, index and corpus unchanged |
| S11 | Colon normalization unchanged |
| S12 | E1/E2 semantics, prompts, schemas, public API/DTO and compatibility helpers unchanged |
| S13 | Default remains legacy_question_core |

Historical scans read committed A3 and R1 raw artifacts, not new model outputs.
Candidate snapshots are initial answer, revision and final public claims,
deduplicated within each execution by claim ID/text/ordered evidence IDs.
Internal claims are excluded. Each Sphinx citation edge is counted separately.
Filtering prevents those three invalid IDs from being offered; it does not
rewrite historical outputs or guarantee a model cannot invent a rejected ID.
The unchanged verifier remains necessary defense in depth.

## Fixed prospective cohort and order

Use the six exact exposed Gold records copied from the frozen A3 manifest.
No protected/holdout access, case substitution, Gold editing or historical arm
reuse. Each arm constructs a fresh agent and performs normal retrieval and QA.

| Index | Case | Role | Execution order | A | B |
| --- | --- | --- | --- | --- | --- |
| 0 | g013 | Historical incomplete-Sphinx sentinel | legacy, runtime | legacy | runtime |
| 1 | g027 | R1 incomplete-Sphinx sentinel | runtime, legacy | runtime | legacy |
| 2 | g112 | Colon-normalizer regression guard | legacy, runtime | legacy | runtime |
| 3 | g002 | Complete-Sphinx and optional-quality sentinel | runtime, legacy | runtime | legacy |
| 4 | g044 | Clean non-web control | legacy, runtime | legacy | runtime |
| 5 | g110 | Code/path negative control | runtime, legacy | runtime | legacy |

Modes are `legacy_question_core` and `runtime_e1_v2`. Provider/model/settings are
the exact `provider` object in the manifest, validated against current settings
before each phase. Generation and judge use the configured gemini-3.8-flash;
embedding uses gemini-embedding-2. Normal production sampling/adapter behavior
is unchanged. Judge temperature is zero. No tuning for g002, Spack or CVMFS.
This is an explicitly authorized six-pair exposed development validation, not
T3, T5, a generalization benchmark or final runtime activation assessment.

## Persistence and exposure boundary

The runner persists STARTED before every execution and COMPLETE afterward,
including exceptions, model events/responses, review history, retrieval trace,
runtime decomposition/coverage, final result and generation admission IDs.
The original selected evidence is preserved in diagnostics. Admission capture
is evaluator-only and does not extend public DTOs. Existing COMPLETE records
are never rerun; a STARTED record is ambiguous and must not be replayed.
No intermediate scientific outcome inspection or adaptive execution decisions.

Freeze all 12 raw records before any judge call. Then run exactly one blinded
paired judgment per case using the established A3 strict schema and prompt.
Judge input is an allowlist: question, approved expected status/Gold obligations,
public A/B status/answer/claims and their cited evidence. No modes, decomposition,
coverage, repair hypothesis or historical failure information is supplied.
Freeze all six judgments before label unblinding or deterministic scoring.
No rejudge or failed-case rerun. Underlying adapter attempts are measured, not
assumed identical to logical operations or returned model responses.

## Prospective gate definitions

| Gate | Frozen requirement |
| --- | --- |
| P1 | Six complete legacy + six complete runtime records and six authoritative strict judgments |
| P2 | Zero public claims citing ineligible Sphinx evidence across every raw answer/revision response in both arms; recorded input and auxiliary IDs match the eligible projection |
| P3 | Zero incomplete-web-citation errors across all reviews of all 12 arms |
| P4 | g013/g027: both expected statuses correct; runtime valid decomposition/evaluable/complete coverage; neither arm has incomplete_citation or structural_review; runtime audit has no structural error |
| P5 | g112 runtime: no historical `PndLmdDataReader::fillData:` colon-class unsupported-identifier error; valid decomposition and evaluable/complete coverage; generic normalization and negative controls remain protected by T0/S11 |
| P6 | Runtime expected-status correct >= legacy; zero new runtime false answers/refusals |
| P7 | Per-case runtime-minus-legacy critical verifier category set is empty, using all reviews |
| P8 | Legacy decomposition zero; runtime exactly one per case; runtime revision <=1; post-verify retrieval zero in both arms |
| P9 | Sum(runtime generation adapter calls - legacy generation adapter calls)/6 <=2.0; embeddings excluded |
| P10 | Zero critical runtime regressions AND runtime supported in all six authoritative judgments, including equivalent pairs |
| P11 | Public DTO/API, compatibility, default and retrieval boundaries unchanged |

P7 uses established categories: wrong_version, unknown_evidence,
incomplete_citation, unsupported_identifier, structural_review and
unknown_answer_point. Decomposition validity follows the established bounded
runtime audit: 1..5 nonempty points with sequential `point.N` IDs.
Critical regression follows the established judge: the nonpreferred output has
severe user-visible damage. Unsupported runtime is independently failing even
when the pair is equivalent. Better/equivalent/noncritical worse are diagnostic
only in R2. Historical R1 P6 FAIL remains; no P6 waiver is granted.

The scorer reuses frozen R1 accounting for status, integrity categories,
decomposition, call counts, DTO and mapping violations; it discards R1's gate
decisions and applies only the R2 gates above. All real static gates are required.

## Verdict, cost and stop boundary

PASS requires S1-S13, P1-P11, all six authoritative judgments, and zero forbidden
changes/actions. Complete evidence with a product gate failure is FAIL, with
no fix-and-rerun. Genuine provider/judge failure or ambiguous/incomplete records
is INCONCLUSIVE; an observed product contract violation remains FAIL.
Runtime point acceptance/internal-claim credit and public DTO violations are
explicit zero-tolerance scorer checks. Repository diffs establish the remaining
product/protocol invariants. No protected data, case/page-specific product logic,
fabricated locator, verifier relaxation, prompt tuning, Gold changes, E3,
post-freeze product edits, selective reruns or runtime activation are allowed.

Report legacy QA, runtime QA and judge separately: logical operations, returned
responses, adapter attempts and observable tokens. Embedding token usage is
unavailable, not zero. Monetary cost is unavailable unless supplied by provider.
Scientific calls before candidate freeze are zero; fake T0 and abstract staffer
review are not scientific model executions.

On PASS: E2 remains IN_PROGRESS / RUNTIME_ACTIVATION_FAILED /
FINAL_ACTIVATION_REASSESSMENT_PENDING; recommend independently preregistered R3,
with execution authorization false. On FAIL: P2_REPAIR_REASSESSMENT_PENDING.
E3 remains NOT_STARTED. Do not establish the previously suggested 14-case
activation design or its thresholds. STOP after the R2 scientific closeout.
