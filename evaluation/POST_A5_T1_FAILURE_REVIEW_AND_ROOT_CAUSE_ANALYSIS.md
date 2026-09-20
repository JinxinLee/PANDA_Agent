# Post-A5 T1 failure review and bounded root-cause analysis

Review outcome: `COMPLETE / PARTIAL / TRACE_OBSERVABILITY_AND_SEMANTIC_SCOPE_LIMITS_REMAIN`.
Offline verification: `PASS`. This is a verification of the review and its provenance,
not a new scientific evaluation or a validated product repair.

`OVERALL_T1_VERDICT = FAIL` is preserved. New PANDA scientific/evaluation usage:
**0 calls / 0 tokens**. No QA, retrieval, embedding, judge, diagnostic model prompt,
stochastic replica, T2, or Attempt 6 was run. No product repair or future repair test
was implemented.

Machine-readable authority: `evaluation/post_a5_t1_failure_review_and_root_cause_analysis.json`.
Compact raw-file receipts: `evaluation/post_a5_t1_execution_provenance_receipts.json`.

## R0. Provenance and lifecycle reconciliation

### Identity and chronology

The starting HEAD was `3d9ca981680ac44940816c294fcc85c9bfc19689`, with a clean
worktree. No newer lineage needed reconciliation. The review commit is a docs/artifact
descendant, not a new product-behavior head.

| Identity | Reconciled value | Evidence |
| --- | --- | --- |
| Repository base before preregistration | `60a62fc9d954bfaaf48e3d5dae48d914c4b0ff21` | Committed preregistration and Git parent history |
| T1 preregistration commit | `421c13a6efc76a845cfd61388e1e2520eea799a7` | Git commit |
| Execution repository HEAD | `421c13a6efc76a845cfd61388e1e2520eea799a7` | All eight manifests, retrieval traces, and stage receipts agree; manifest/trace dirty=false |
| Product-behavior HEAD | `e79d3232ed132a224cbceaf3524e19a1406bd648` | Preregistration plus unchanged source/tests/configs/benchmarks through execution HEAD |
| T1 result commit | `3d9ca981680ac44940816c294fcc85c9bfc19689` | Git |
| Prompt fingerprint | `0a5b2909ef586671d533148979fc681c64e37528ad53781a4566cb9044835ba2` | Each manifest and stage receipt |
| Gold | `m6-benchmark-v2.11`, `39943c6a3f2152e476109c0340acd066795c8de6ff3b6bb2eac6661ac480a417` | Each manifest and stage receipt |
| Calibration | `phase_b_t3_product_language_scope_v8`, selector `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5` | Committed preregistration; no independently retained per-run calibration fingerprint |

`EXECUTION_HEAD_PROVENANCE = CONFIRMED`.
The frozen result's `repository_execution_head = 60a62fc...` labels the base as
the execution head incorrectly. This is corrected forward only. The difference
from `60a62fc` to `421c13a` consists of exactly the two preregistration artifacts;
it does not represent a product-behavior change. The source implementation of
`repository_identity` runs `git rev-parse HEAD` and `git status --porcelain`
(`src/panda_agent/evaluation_runner.py:108`); this is persisted identity, not
an inference from intended procedure.

`T1_PREREGISTRATION_CHRONOLOGY = VERIFIED` within the retained local Git/runtime
evidence. The preregistration commit time is **2026-09-20 00:00:59 UTC**
(`02:00:59+02:00`). Every manifest start, run start, and receipt follows it, with
non-overlapping run intervals in the predeclared order. These are local persisted
timestamps, not an external trusted timestamp service.

All times below are on 2026-09-20, UTC, truncated here to seconds; receipts preserve
the original precision.

| Run | Manifest run_started_at | Run-status start | Run-status completion | Receipt generated_at | Calls | Tokens |
| --- | --- | --- | --- | --- | ---: | ---: |
| post-a5-t1-g011 | 00:01:33 | 00:01:37 | 00:03:13 | 00:03:13 | 8 | 34,056 |
| post-a5-t1-g010 | 00:03:19 | 00:03:23 | 00:05:21 | 00:05:22 | 7 | 28,130 |
| post-a5-t1-g013 | 00:05:27 | 00:05:32 | 00:10:06 | 00:10:06 | 14 | 60,764 |
| post-a5-t1-g014 | 00:10:12 | 00:10:16 | 00:11:49 | 00:11:50 | 7 | 37,563 |
| post-a5-t1-g023 | 00:11:55 | 00:12:00 | 00:13:30 | 00:13:31 | 7 | 42,239 |
| post-a5-t1-g022 | 00:13:36 | 00:13:41 | 00:16:49 | 00:16:49 | 8 | 57,804 |
| post-a5-t1-g047 | 00:16:55 | 00:17:00 | 00:18:32 | 00:18:32 | 7 | 45,136 |
| post-a5-t1-g050 | 00:18:38 | 00:18:42 | 00:20:25 | 00:20:26 | 7 | 67,573 |

Two discrepancies are retained, not repaired:

1. `records/<case>.json.completed_at` is assigned **before** scientific execution
   (`evaluation_runner.py:1765`); `attempted_at` is assigned when the completed
   record is appended (`evaluation.py:2278`). Their names misleadingly suggest
   the reverse sequence. Receipts preserve both literal values and separately use
   `run_status.json.attempt_started_at/attempt_completed_at` for run intervals.
   Manifest creation time as a separate field and shell exit codes are absent;
   those receipt fields are null, not invented.
2. The formal runner reports `INCONCLUSIVE / INVALID_CANDIDATE_IDENTITY` for each
   run, because no formal candidate is bound. Each case is nevertheless scored
   and the cohort status is COMPLETE. Preregistration explicitly defines this
   as development T1, not a candidate freeze or formal release gate. The frozen
   T1 sentinel decision is FAIL and is not replaced by the generic runner label.

`T1_RESULT_INTEGRITY = NO_INVALIDATING_DEFECT_FOUND`. Provenance completeness and
scientific outcome are separate axes. Calibration is attributed to preregistration,
not misrepresented as a raw-run fingerprint.

### Compact receipts and retention boundary

All eight exact local run directories exist under
`data/evaluation/runs/post-a5-t1-<case_id>/` and remain gitignored.
`raw_run_artifacts_committed_to_git = false`.

The new receipts store SHA-256, size, and repository-relative path for six existing
files per run: `manifest.json`, `records/<case>.json`, `traces/<case>.json`,
`run_status.json`, `stage_receipt.json`, and `metrics.json` (**48 digests**).
There is no standalone usage file: usage is retained in status/receipt/record
fields. Existing stage-receipt hashes for manifest, results, aggregate retrieval
trace, gate, metrics, and attempts were also checked: **48/48 match**. Aggregate
records/traces equal their canonical per-case equivalents. Each attempts ledger
has one successful row, no exception or recovery: **65 calls / 373,265 tokens,
transport recovery 0**, unchanged.

The exact directories, T1 temporary summary, and the runner/store/Vertex/QA
persistence paths were inspected. They retain decomposition, selected evidence,
final normalized mappings, final claims, and external metrics, but no raw initial
draft, first-round g013 coverage response, revision prompt/response, raw post-merge
draft, or full `answer_point_coverage` response. The negative retention conclusion
is bounded to this inspected evidence; no protected storage was searched.
`qa.py:3260` onward explains this diagnostic projection; `llm/vertex.py` returns
parsed responses without writing model payloads to the inspected run stores.

## R1. Bounded reconstruction

Layer names below use this task's taxonomy: D0 decomposition; R1/R2 retrieval and
evidence availability; A0 initial generation; V1 first support/coverage review;
A1 revision/merge; V2 re-verification; C composition; E external evaluation;
O observability. Historical policy shorthand is not silently reused.

### A. g013

Primary record: `data/evaluation/runs/post-a5-t1-g013/records/g013.json`.
Relevant pointers are `diagnostics.question_decomposition`,
`diagnostics.selected_evidence`, `diagnostics.answer_point_audit`,
`diagnostics.claim_audit`, `result.claims`, and `metrics`.

| Stage | Observation and classification | Confidence / limit |
| --- | --- | --- |
| D0 | `G013_RUNTIME_POINT_COVERAGE = PRESENT`: point.3 is `How the master run task participates in the lifecycle`, with the corresponding raw-question support span. | CONFIRMED; D0 omission of the explicit obligation is excluded. |
| R1/R2 | `critical_final_evidence_recall=1.0`; both required roles match accepted macro-document alternatives. `G013_P3_SUPPORTING_EVIDENCE_AVAILABLE = AMBIGUOUS`: partial role support exists, full configuration/event-loop support is not directly established. | SUPPORTED semantic limitation; role recall does not prove complete entailment. |
| A0 | `G013_INITIAL_P3_CLAIM = NOT_OBSERVABLE`. | Initial draft is not retained. Final claims cannot establish the initial draft. |
| V1 | A revision occurred (`revision_count=1`), consistent with the error-trigger route. | SUPPORTED that some recovery trigger fired; NOT_OBSERVABLE whether the first review specifically listed point.3. |
| A1 request | `G013_REVISION_REQUEST_WELL_FORMED = NOT_OBSERVABLE`. Source includes runtime point IDs/text, missing points, eligible evidence, and already verified claims. | Code contract is present; actual first-review state and request bytes are absent. |
| A1 response/merge | `REVISION_EMITTED_P3_CLAIM = NOT_OBSERVABLE`. The final verification inventory contains only terminal setup and macro invocation. | No user-visible p3 claim at the post-merge verification boundary is supported by the final mapping inventory; raw response/merge draft unavailable. |
| V2 | Final review correctly reports `missing_answer_point_ids=[point.3]`, `coverage_complete=false`, `coverage_evaluable=true`, `review_error=null`. Both remaining claims are supported. | CONFIRMED; no final false acceptance of p3. No retained third rejected p3 claim or internal-filter entry. |
| C | Composer accepted two source claims; both appear in the answer. Neither source claim establishes p3. | CONFIRMED downstream omission; composer is not the earliest loss. |
| E | p3 missing; g013 FAIL. | Frozen result preserved. |

Evidence content is narrower than the matched role labels:

- `evidence.ab72413dbb9a54b5e68ce96d` (`macro/master/Readme.md`) says master run
  and Master Tasks provide default settings and operation modes. It then gives
  macro invocations. This supports a partial lifecycle description, not the
  full master-run configuration/event-loop account in Gold p3.
- `evidence.5781619e91d4c152182d9b8e` (`macro/master/mastermacros.rst`) gives
  macro ordering, event-generator settings, and shell parameters. The other
  selected macro-page variants repeat these themes; none directly supplies
  the full master-run orchestration explanation.
- `evidence.258612f18040b81459f72d3b` says `PndMasterRunSim` is the simulation
  master runner and calls `PndMasterSimTask`. It is selected but has Sphinx
  `section_path=[]`. `_is_public_claim_citation_eligible` (`qa.py:84`) excludes
  it from `_answer` and `_revise` inputs (`qa.py:2244`, `qa.py:2737`). This is
  a confirmed input-admission fact, not evidence that retrieval was rerun.

**Earliest supported upstream limitation:** `R1/R2 /
PARTIAL_LIFECYCLE_EVIDENCE_AT_GENERATION_ADMISSION_BOUNDARY` — SUPPORTED.
Full p3 evidence sufficiency is not established. Do not compensate for this by
assuming the generator should invent the event-loop mechanism.

**Bounded answer-path residual:** `A1 / BOUNDED_REVISION_RECOVERY_RESIDUAL` —
SUPPORTED, with `SUBMECHANISM = UNRESOLVED_DUE_TO_TRACE_OBSERVABILITY_AND_EVIDENCE_SUFFICIENCY`.
The post-revision miss itself is CONFIRMED; a revision-generation defect, merge
defect, initial point-specific recovery trigger, and unique causal mechanism are
not. Partial/empty revised generation versus normalization/merge exclusion cannot
be separated. Final V2 rejection of a surviving p3 claim is not supported by its
complete two-claim inventory. Both historical and T1 exact ID-collision causality
remain `NOT_ESTABLISHED`.

### B. g023

Primary record: `data/evaluation/runs/post-a5-t1-g023/records/g023.json`.

**D0 semantics:** raw question is `How do I use PndMasterRecoTask in the generic
workflow?`; the sole runtime point is `How to use PndMasterRecoTask in the generic
workflow`. Neither explicitly names PID or a before/after relation.
`G023_RUNTIME_POINT_CONTAINS_BEFORE_PID_OBLIGATION = AMBIGUOUS`
(`explicit_before_pid_obligation = NO`). Workflow placement is a reasonable
reading, but the exact requested relation is not encoded. The question-only
decomposer explicitly forbids guessed stages and domain facts
(`question_decomposition.py:22`). It is therefore not valid to label D0 a
confirmed deletion merely because the Gold answer contains a domain-specific
before-PID fact. Conversely, this broad point does not satisfy the strict
prerequisite for **CONFIRMED** specific-relation V1 false acceptance.

**Evidence admission:** the selected full Sphinx pages
`evidence.aa848838ccbb763f405765da` (`Running/Running.html`) and
`evidence.d452f25b295c0ce037b92b26` (`Running/MasterTasks.html`) explicitly describe
reconstruction followed by PID. The latter contains `AddDigiTasks`,
`AddRecoTasks`, `AddPidTasks`, followed by `Init`, `Run`, and `Finish`, plus text
linking the tasks to `PndMasterRecoTask`. Both have empty `section_path` and are
excluded from generation claim evidence. The verifier's `review_evidence` includes
the full selected bundle (`qa.py:2480` onward), so generation and review see
different evidence sets.

This selected-to-generation loss is **CONFIRMED**, within R1/R2 evidence
availability. Some eligible material remains: a brief curated workflow list,
an option section mentioning preselection before PID, and a different Restgas
tracking/PID sequence. These are not the same explicit task-position account.
Thus neither zero available workflow information nor unique causal sufficiency
of the excluded pages is claimed.

**A0 supported claims:** `revision_count=0`; the final mapping inventory and
result retain exactly these three user-visible claims before composition:

| Claim | Content | Verified mapping | Establishes before PID? |
| --- | --- | --- | --- |
| claim.reco_task_role | Wrapper for default reconstruction, barrel/forward tracking and Kalman fitting | point.1 | NO |
| claim.reco_task_instantiation_options | Constructor and option flags | point.1 | NO |
| claim.reco_task_internal_assembly | Creates subtasks and registers them via Add | point.1 | NO |

`G023_SUPPORTED_CLAIMS_ESTABLISH_P3 = NO`. Mentioning reconstruction or internal
task registration is not the workflow ordering relation. The unprocessed initial
response is not retained; the no-revision run and complete verification inventory
support an A0 content omission, not a composer deletion.

**V1 payload boundary:** persisted audit has all three verified mappings above,
`coverage_complete=true`, `missing_answer_point_ids=[]`, `review_error=null`.
Raw `claim_answer_point_mappings`, `answer_point_coverage`, the exact
`supporting_claim_ids`, and model `reason` are **NOT_OBSERVABLE**. The normalized
mapping projection is retained, not the full response. Under the unchanged source,
the accepted audit implies a `point.1` coverage record with `complete=true` and
a nonempty eligible supporter subset of those three claims. Which subset the
model named cannot be recovered and is not fabricated.

The deterministic validator (`qa.py:795`) checks exact records, ID membership and
uniqueness, per-claim mappings, supporter eligibility, complete/missing consistency,
and coverage record presence. It does not evaluate claim-text entailment; it does
not even receive point text as an argument. The accepted audit is evidence of a
structurally valid path, not a fresh raw-payload validation. **No validator bug is
established.** Semantic completeness remains a model judgment.

**Downstream:** V1 produced no errors, so no A1 revision or V2 re-verification
occurred. Composition retained the three claims without adding the missing
ordering relation. The external measurement reports p3 missing and g023 FAIL.
It also reports p2 covered; this review neither rescored p2 nor endorsed that
separate judgment merely from the claim wording.

**Causal classification:**

- Earliest directly established information loss: `R1/R2 /
  EXPLICIT_ORDERING_TEXT_LOST_AT_SELECTED_TO_GENERATION_ADMISSION` — CONFIRMED.
  This is a proven mechanism at an interface, not a proven unique root cause.
- Earliest supported answer-content failure: `A0 /
  BEFORE_PID_RELATION_ABSENT_FROM_INITIAL_USER_VISIBLE_CLAIMS` — SUPPORTED.
- `V1_RUNTIME_VS_EXTERNAL_COMPLETENESS_DISAGREEMENT = CONFIRMED`.
  This is the frozen false-acceptance recurrence in the outcome sense.
- `V1_SEMANTIC_FALSE_ACCEPTANCE = NOT_ESTABLISHED` under the requested strict
  causal criterion; `D0_VS_V1 = UNRESOLVED_SEMANTIC_SCOPE`. A specific before-PID
  obligation in the runtime point and the exact reviewer rationale are not
  independently demonstrated.

The earlier T1 prose called this coverage false acceptance. That observation
remains; interpreting it as a confirmed reviewer-only mechanism would exceed
the retained evidence. Revision/merge and composer-first-loss hypotheses are
excluded. D0 underspecification, broad-point semantic judgment, evidence admission,
and generation omission remain competing or interacting explanations.

### C. g047 positive contrast

The runtime point is also broad: `The theoretical purpose of the DPM
elastic-scattering model`. It does not explicitly name luminosity extraction.
However, `claim_3` explicitly says the DPM hadronic amplitude combines with the
Coulomb amplitude into the full elastic differential cross section, enabling
stable luminosity extraction. All three claims map to point.1; coverage is complete,
missing IDs are empty, no revision occurred, and external p1 coverage passes.
Exact raw coverage supporter IDs are not retained here either.

This single PASS is consistent with selective content/completeness behavior,
rather than universal schema malfunction. It does not test whether the reviewer
would reject an incomplete answer, establish a general semantic repair benefit,
or resolve g023's D0/V1 boundary.

### D. g011 safety versus evidence role

`C_NEGATIVE_EXISTENCE_SAFETY = PASS`.
Forward alias: `C_NATIVE_DOCUMENTATION_ROLE_COVERAGE = FAIL`.
Legacy frozen field: `C_RETRIEVAL_COMPLETENESS = FAIL` (preserved).

The positive native-path claim cites `evidence.120adb43d2fa804bd1d521df`,
`object.80b0b8544d4418c2bc9ebfe6`, the Docker documentation section
`what-is-or-should-be-included`. Its text explicitly contrasts the traditional
host package/FairSoft/FairRoot/PandaRoot build sequence with container/CVMFS
options. `evidence.4d74e560e77092857621de1d` supplies the workstation container
implementation. Both claims are supported; the deterministic final fallback
contains no unqualified documentation-wide absence assertion.

g011.e1 requires native installation documentation identified by the Sphinx titles
`Installing & running PandaRoot` / `Installation of PandaRoot for Developers`,
or the code-documentation paths `docs/Installation/Install_PandaRoot.rst` /
`docs/Installation/Install_Developers.rst`. Docker content does not match those
selectors. The persisted metric records e1 unmatched and e2 matched via ancestor,
for critical role recall 0.5. This is **required native-documentation role coverage
failure**, not absence of all information needed to describe a native path.
Workstream D stays DEFERRED; no new retrieval or Gold modification.

### Controls and historical limits

g010, g014, g022, and g050 remain `CONTROL_PASS` (4/4). Their retained records
have no critical point miss or hard-safety failure. This supports only no obvious
broad regression in this fixed sample, not global regression absence.
Attempt-5 historical causal uncertainty remains unchanged; no exact historical
ID-collision assertion is revived and no historical result is rescored.

## Current scientific-effect state and next decision

```text
GENERIC_PRODUCT_REPAIR = IMPLEMENTED / DETERMINISTICALLY VERIFIED /
T1 SCIENTIFIC EVIDENCE = MIXED / OVERALL T1 = FAIL /
GENERAL EFFECT NOT ESTABLISHED
```

A: g013 target FAIL, revision recovery mechanism not directly observed.
B: g023 FAIL with outcome-level false-acceptance recurrence; g047 PASS; mixed
single observations, reviewer-only causality not established.
C: g011 safety PASS, positive single observation, general effect not established.
D: retrieval role preservation DEFERRED.

Next recommendation:
`POST-A5 T1 OBSERVABILITY CONTRACT RECONCILIATION / EVIDENCE-ADMISSION AND COVERAGE-SCOPE REVIEW`.
Both cases still have limits that prevent confidently choosing a unique behavior
repair: g013 lacks round history and full evidence sufficiency; g023 combines
an admission loss with unresolved specific-obligation semantics. This is a
bounded prerequisite recommendation, not an architecture redesign or replay.

Future hypotheses only: minimal per-round draft/request/review/revision retention;
generic usable-evidence preservation across citation admission; and generic
workflow-position completeness without inserting Gold facts into decomposition.
None is implemented or validated. Any repair, replay, or additional scientific
sample requires separate authorization.

## Verification and closeout boundary

- Eight persisted execution identities/chronologies agree; 48 new content digests
  reference real local files and 48 existing receipt digests match. JSON parses.
- Source/history inspection and deterministic artifact comparisons only;
  no full pytest suite or scientific evaluation was run. Monetary model cost: 0.
- Frozen T1 scientific body and verdict are preserved; optional result pointers
  only direct provenance/interpretation readers to this forward review.
- Authorized changes are exactly three new review/receipt artifacts, two active
  lifecycle documents, and two minimal result pointers. No source, tests, prompts,
  evaluator, benchmark/Gold, calibration, or thresholds change.
- `git diff --check`, JSON parsing, frozen-result preservation checks, and the
  complete changed-file/diff review pass before the single focused commit. No amend, squash, or push.
- `MATERIAL_PRODUCT_CHANGE = false`; `EVALUATOR_CONTRACT_CHANGE = false`;
  `GOLD_CHANGE = false`; `CALIBRATION_CHANGE = false`.
- `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`; holdout access 0;
  protected-content leakage 0; F6-B execution 0. Protected content was not opened.
- Candidate frozen=false; Attempt 6 preregistered=false; Attempt 6 executed=false;
  `ATTEMPT_6_READINESS = NOT_READY`.

Changed files:

1. `evaluation/POST_A5_T1_FAILURE_REVIEW_AND_ROOT_CAUSE_ANALYSIS.md`
2. `evaluation/post_a5_t1_failure_review_and_root_cause_analysis.json`
3. `evaluation/post_a5_t1_execution_provenance_receipts.json`
4. `docs/EVALUATION_STATUS.md`
5. `docs/GENERALIZATION_ROADMAP.md`
6. `evaluation/POST_A5_T1_FIXED_EXPOSED_SENTINEL_RESULT.md` (forward pointer only)
7. `evaluation/post_a5_t1_fixed_exposed_sentinel_result.json` (forward pointer only)

`NEXT_TASK_EXECUTION_AUTHORIZED = false`.

## Forward contract reconciliation pointer

`evaluation/POST_A5_T1_OBSERVABILITY_EVIDENCE_ADMISSION_AND_COVERAGE_SCOPE_RECONCILIATION.md` and its JSON companion supersede only causal-layer/contract interpretation and chronology wording: selected-to-generation exclusion belongs to EA, g013 unsuccessful recovery does not establish an A1 defect, and chronology is VERIFIED_WITHIN_RETAINED_LOCAL_EVIDENCE. The historical analytical body, raw receipts, scientific observations and T1 FAIL above remain unchanged. All new contracts are design-only.
