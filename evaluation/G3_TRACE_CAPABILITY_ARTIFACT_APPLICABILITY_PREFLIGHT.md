# G3 Trace-Capability / Artifact-Applicability Preflight

## Decision and boundary

**OBSERVABILITY_PREREQUISITE_REQUIRED.** The accepted G3 audit methodology is
unchanged. A fresh, explicit non-formal `novel_dev` QA/full run cannot currently
capture its required QA stage events through a supported evaluation path. The
standard runner rejects that split when stage tracing is requested, and the CLI
does not expose the runner's trace opt-in. Existing run metadata does not supply
a current-lineage `novel_dev` QA stage-trace class. The future cohort is not
frozen, so no selected-ID artifact sufficiency is asserted.

This was a source, test-contract, directory, and manifest-metadata inspection.
No question, expected answer, case outcome, record body, retrieval trace body,
evidence content, or protected dataset content was opened. No cohort was
selected, and no retrieval, QA, model, audit, or counterfactual run occurred.

## Supported execution paths and trace authority

`EvaluationSplit` includes `novel_dev`
(`src/panda_agent/evaluation_runner.py:70-79`). `run_evaluation()` calls
`_configure_stage_trace()` before loading the dataset or starting a run
(`:1646-1649`). That guard permits `capture_stage_trace=true` only for explicit
non-formal, non-candidate `dev`, `challenge`, or `regression` QA/full runs
(`:1606-1625`). It rejects `novel_dev`, `novel_validation`, `novel_holdout`,
`acceptance`, formal/candidate-bound runs, and retrieval-only mode. The
relevant test contract covers opt-in persistence, resume, and protected/formal
rejection (`tests/unit/test_post_a5_o1_observability.py:290-360`); the source
restriction itself also excludes `novel_dev`.

The `panda-qa-eval run` CLI accepts `novel_dev` as a split but has no stage-trace
option and does not pass `capture_stage_trace` to `run_evaluation()`
(`src/panda_agent/cli/evaluate.py:59-84,300-316`). `resume_evaluation()` reuses
the manifest's trace choice and delegates to the same guarded runner
(`src/panda_agent/evaluation_runner.py:2190-2213`); it cannot turn tracing on
for a legacy run or bypass the split guard. A repository search found no other
supported evaluation wrapper that produces these stage events with standard
run identity. Direct `QAAgent._run_detailed(..., capture_stage_trace=True)`,
test helpers, and bespoke diagnostic scripts are not G3 execution paths.
The O1 implementation record identifies the programmatic
`run_evaluation(..., capture_stage_trace=True)` opt-in as the supported
development path, with no separate CLI tracing route
(`evaluation/POST_A5_O1_BEHAVIOR_NEUTRAL_OBSERVABILITY_IMPLEMENTATION.md:97-102`).

`QAAgent` defines bounded `EA_ADMISSION`, `A1_INPUT`, `V1_INPUT`, `V1_OUTPUT`,
`V2_INPUT`, and `V2_OUTPUT` events when reached. Its `qa-stage-trace-v1`
envelope records `capture_status`, events, and an evidence registry under
`diagnostics.qa_stage_trace` only when capture is enabled
(`src/panda_agent/qa.py:1866-1892,4120-4220`). It is best-effort and can be
`INCOMPLETE`; a manifest opt-in is not proof that every event was captured.
Final G2 coverage/mapping state is separate run-result authority.

Retrieval traces are independent of this QA opt-in. After a case executes
successfully, the runner builds and writes a per-question trace under the run
directory (`src/panda_agent/evaluation_runner.py:1819-1837`); a non-traced
`novel_dev` run can therefore write one. `RetrievalTrace` binds `run_id`,
`question_id`, and a manifest-derived implementation identity, with channel
candidates, stored fusion and rerank candidates, and final selected evidence
(`src/panda_agent/retrieval_trace.py:119-167,253-309`). It is written as an
atomic `traces/*.json` file and an append-only `retrieval_traces.jsonl` stream
(`:313-328`). Subject to trace completeness, it can support G3 S0-S2; it does
not carry `EA_ADMISSION`, A1/V1/V2 events, validated relation
`admission_state`, or G2 per-round semantic validity. It cannot establish
S5-S8 by itself.

## Metadata-only artifact inventory

Inventory location: `data/evaluation/runs/*/manifest.json` and existence/count
of sibling `traces/`, `retrieval_traces.jsonl`, and `records/` files. Directory
and file names were used only for counting, never to select case IDs. The
inventory covered 118 run directories and 116 readable manifests; two run
directories lacked a manifest. Across the run store, 31 run directories had
retrieval trace JSON files (502 files total), and 114 had record directories
(2,153 JSON files total). These are file-presence counts, not valid-case or
trace-completeness counts; no trace or record body was read.

| Metadata class | Count | G3 applicability |
|---|---:|---|
| `novel_dev` / retrieval / official, no stage-trace flag | 1 | `PRE_G2_INCOMPATIBLE`, `RETRIEVAL_TRACE_ONLY`, and wrong mode for S5-S8; a retrieval trace directory exists. |
| Explicit `capture_stage_trace=true` / `dev` / full / non-formal / no candidate | 16 | `WRONG_SPLIT` and `PRE_G2_INCOMPATIBLE`; eight have retrieval trace directories. The flag does not prove captured QA events without record inspection. |
| Manifests with a repository commit before G2 | 40 | `PRE_G2_INCOMPATIBLE` for current relation-local behavior. |
| Legacy manifests without a repository commit | 76 | `TRACE_IDENTITY_INCOMPLETE` / unknown product lineage. None is a `novel_dev` QA stage-traced class. |
| Exact G2 or later documentation-only lineage | 0 | No `CURRENT_LINEAGE_POTENTIAL` class in this standard run store. |

Among the 116 manifests, 114 contain dataset hash, source manifest hash, index
identity, and prompt hash fields; 40 contain a repository commit. Sixteen
explicitly record stage tracing enabled; the remaining 100 have no such field.
Ninety-three are marked official and two are candidate-bound. None of those
formal/candidate classes can supply an authorized fresh G3 stage trace.
Run-level metadata and file presence alone cannot prove which stage events
or selected IDs an existing record contains.

`POTENTIALLY_REUSABLE_ARTIFACT_CLASS = NO` for current-lineage primary
`novel_dev` QA stage tracing in this standard run store. This is a class-level
finding only; `SELECTED_ID_ARTIFACT_SUFFICIENCY = NOT_EVALUATED`.

`a0106bd5eff93646f34f5e50e161e8be8a49d680` is the current G2 product
behavior lineage. Git shows only the G3 design and documentation-correction
files changed between it and this preflight's starting HEAD; a later
documentation-only run identity could be behavior-compatible if its manifest
also binds the required admission, retrieval/index/source, dataset, mode, and
trace identities. Pre-G2 or missing repository identity cannot be promoted
from question text or a trace file's existence. The future audit must first
freeze its reviewed `novel_dev` cohort outcome-blind, then qualify artifacts
for those selected IDs. Artifact availability cannot choose or replace IDs.

## Identity and protected-split safeguards

| Identity layer | Preflight classification | Limit |
|---|---|---|
| Standard manifest schema | `SUFFICIENT_FOR_PREFLIGHT` | Supports run mode/split, official/candidate status, dataset, source/index, prompt/model, repository identity when populated, and capture choice when present. Legacy omissions prevent case-level compatibility claims. |
| Retrieval trace schema alone | `PARTIAL` | Has run ID and a subset of implementation identity; split, source manifest, and capture choice require the matching manifest. It includes raw question and evidence fields, which this preflight did not open. |
| QA stage trace schema alone | `PARTIAL` | Has stage events and capture status but no standalone run/dataset identity; it must be joined through the case record and immutable run manifest. No record body was opened here. |
| Existing selected-ID coverage and event completeness | `MISSING` | The cohort is not frozen and record/trace contents were not inspected. Sufficiency is `NOT_EVALUATED`, not a negative admission finding. |

The current guard's official, candidate, split, and mode checks must remain
fail-closed. Any future change must keep tracing unavailable for
`novel_validation`, `novel_holdout`, acceptance/release evaluation, and
candidate-bound formal runs absent their own authorization. It must not
broaden tracing to all development-like splits.

## Minimum next task and lifecycle

The smallest separately authorized prerequisite is evaluation/trace plumbing:
permit bounded, explicit QA stage-trace capture for non-formal, non-candidate
`novel_dev` QA/full development runs through the existing programmatic
`run_evaluation()` opt-in, preserve manifest/run identity and resume rules,
and add focused tests for the allowed path and every protected/formal
exclusion. A CLI switch is optional if a separately authorized execution
workflow requires it; it is not needed to remove the known runner guard.
Confirm whether an artifact-schema identity update is needed if
the manifest or trace contract changes. Do not change admission, citation,
retrieval, G1/G2, prompt/schema, composer, Gold, or calibration behavior.
Additional S4 attempt fields or per-round G2 receipt telemetry remain
conditional future improvements, not part of this minimum prerequisite.

`PHASE_G = IN_PROGRESS / G3_PREFLIGHT_COMPLETE`.
`G3 = AUDIT DESIGN COMPLETE / TRACE-CAPABILITY PREFLIGHT COMPLETE /
OBSERVABILITY PREREQUISITE REQUIRED / PRODUCT CHANGE NOT_AUTHORIZED`.
`NEXT_TASK_RECOMMENDATION = G3 NOVEL_DEV QA STAGE-TRACE OBSERVABILITY PREREQUISITE`.
`NEXT_TASK_EXECUTION_AUTHORIZED = false`.

## Access and execution accounting

```text
RUN_DIRECTORY_METADATA_INSPECTED = 118
RUN_MANIFESTS_INSPECTED = 116
TRACE_FILE_CONTENTS_INSPECTED = 0
CASE_RECORD_CONTENTS_INSPECTED = 0
AUDIT_EXECUTED = false
AUDIT_CASES_COLLECTED = 0
RETRIEVAL_RUNS = 0
QA_RUNS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
NOVEL_DEV_CASE_CONTENT_ACCESS = 0
NOVEL_DEV_OUTCOME_ACCESS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```
