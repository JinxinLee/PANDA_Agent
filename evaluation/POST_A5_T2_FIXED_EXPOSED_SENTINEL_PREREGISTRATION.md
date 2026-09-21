# Post-A5 T2-P0 Fixed Exposed Sentinel Preregistration

PREREGISTERED / ZERO SCIENTIFIC CALLS / T2 EXECUTION NOT STARTED

The prior HOLD/hard-budget design is preserved in Git history at `60708e601a0e3fbc01e1872bbb2c2578cf2453ef` and superseded forward by this explicitly authorized simplified protocol. Historical scientific results are unchanged.

T2 is exposed repair-target evidence, not independent generalization evidence. It is a FIXED EXPOSED REPAIR-TARGET REGRESSION STUDY, not release authority, candidate freeze, protected validation or Attempt 6.

## Identity and chronology

Product behavior head `6ed3ba361476b36744c72e76f5905733b1755f5c`; mode `production_answer_obligations_v1`.
Prompt `3.11.0` / `03e1bf270898b28127a42fa2e1ccb24cfc1d87e177eeba5428ba4680d426352c`.
Gold v2.11, `evaluation/benchmarks/v2_11/gold_questions.yaml`, SHA256 `39943c6a3f2152e476109c0340acd066795c8de6ff3b6bb2eac6661ac480a417`.
Calibration v8, 59 formal-English / 21 non-English, selector SHA256 `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5`.

The commit first adding evaluation/post_a5_t2_fixed_exposed_sentinel_preregistration.json is T2-P0. Resolve exact SHA after commit with git log --diff-filter=A -1 --format=%H -- evaluation/post_a5_t2_fixed_exposed_sentinel_preregistration.json. No self-referential SHA fabricated.
The committed P0 must precede every T2 scientific call. Execution requires separate explicit authorization, P0 execution HEAD and empty product-source diff from the behavior head. No product/prompt/storage/evaluator/Gold/calibration/threshold edits during execution, candidate freeze or per-file hash manifest.

## Fixed cohort and execution

Affected: g011, g013, g023, g047. Controls: g010, g014, g022, g050.
Order: **g011 -> g010 -> g013 -> g014 -> g023 -> g022 -> g047 -> g050**.
Run IDs are `post-a5-t2-<case_id>` for those eight IDs in that exact order. One scientific execution each, no additions, substitutions or replicate block. All eight mechanically verified approved, dev, exposed and expected answered; IDs/order equal T1. Repeat identity precheck before execution, never substitute on mismatch.

```python
from pathlib import Path
from panda_agent.evaluation_runner import run_evaluation

# Future execution only after separate explicit authorization, at T2-P0 HEAD.
root = Path(r"C:\Users\Jinxin.DESKTOP-H6SSTQH\Desktop\Agent_learn\PANDA_Agent")
run_evaluation(
    root, mode="full", split="dev", run_id="post-a5-t2-g011",
    allow_draft=True, resume=False, case_ids=["g011"],
    dataset_path=root / "evaluation/benchmarks/v2_11/gold_questions.yaml",
    candidate_id=None, capture_stage_trace=True,
    max_model_calls=None, max_token_usage=None,
)
```

Only replace the fixed case/run IDs according to order. `allow_draft=True` means official=false for development tracing, not permission for draft Gold. Explicit v2.11 path, full external judge and tracing supported by existing runner; no new mechanism judge.

## Resource and rerun policy

RESOURCE_POLICY = USAGE_ACCOUNTING_ONLY. Numerical model/token arguments are None. No quota or hard ceiling; record all actual calls/tokens, including recovery. No adaptive extension: the scientific protocol is fixed. Obvious infrastructure runaway may be stopped and documented as infrastructure failure; resource usage does not determine scientific PASS/FAIL.

Complete the fixed cohort in fixed order subject to genuine infrastructure/identity failures; do not stop for early scientific success/failure or cost preference. No outcome-driven, best-of-N, judge-disagreement, mechanism-activation or trace-quality rerun. Existing same-identity infrastructure/transport recovery may resume interrupted runs with completed records retained. Scientifically completed cases are never rerun. No new retry/budget infrastructure.

## Unchanged scientific criteria

- **g013**: Scientifically valid completed final result must be answered, critical_answer_point_miss_count=0, and satisfy current hard-safety/trustworthiness invariants. An inappropriate insufficient_evidence result is FAIL, not INCONCLUSIVE. Missing evaluator data is not interpreted as zero. All critical points, including active Gold p3 master-run-task/lifecycle obligation, must be satisfied. EA1 or A1 activation is not required. Record EA admission, initial V1 completeness, revisionable gaps, revision_count, A1 merge dispositions and V2 where applicable.
- **g023**: Scientifically valid completed final result must be answered, critical_answer_point_miss_count=0, and satisfy current hard-safety/trustworthiness invariants. An inappropriate insufficient_evidence result is FAIL, not INCONCLUSIVE. Missing evaluator data is not interpreted as zero. Explicitly establish active Gold p3 generic workflow placement, including the relation to PID; a bag of reconstruction/digitization/PID/PndMasterRecoTask mentions does not pass.
- **g047**: Scientifically valid completed final result must be answered, critical_answer_point_miss_count=0, and satisfy current hard-safety/trustworthiness invariants. An inappropriate insufficient_evidence result is FAIL, not INCONCLUSIVE. Missing evaluator data is not interpreted as zero. Explicitly relate elastic differential cross section to luminosity extraction; inappropriate new refusal fails the positive contrast.
- **g011**: Scientifically valid completed final result must be answered, critical_answer_point_miss_count=0, and satisfy current hard-safety/trustworthiness invariants. An inappropriate insufficient_evidence result is FAIL, not INCONCLUSIVE. Missing evaluator data is not interpreted as zero. C_NEGATIVE_EXISTENCE_SAFETY=PASS: no unqualified documentation/corpus-wide claim that no independent native setup path exists without deterministic exact-lookup absence authority. Separately record C_NATIVE_DOCUMENTATION_ROLE_COVERAGE=PASS/FAIL/NOT_APPLICABLE from active Gold critical role matching; role failure does not gate this negative-existence mechanism. Workstream D remains deferred.
- **Controls**: Each of g010,g014,g022,g050 is CONTROL_PASS iff answered, critical_answer_point_miss_count=0, no contradiction, no major unsupported claim, no forbidden/wrong-version evidence, no identifier hallucination under current evaluator, no unhandled exception, no hard-safety/trustworthiness violation and no new inappropriate refusal. Citation-source variation alone is not failure when v2.11 accepted evidence-role contracts are satisfied.

## Primary verdict and diagnostics

- **PASS**: All four sentinels PASS AND all four controls CONTROL_PASS AND all eight scientific executions validly complete AND no hard-safety/trustworthiness violation.
- **FAIL**: Any scientifically valid sentinel FAIL OR any CONTROL_FAIL OR any valid hard-safety/trustworthiness failure. Valid FAIL takes precedence.
- **INCONCLUSIVE**: Unrecoverable infrastructure, identity or transport failure prevents a valid scientific outcome, provided no valid scientific FAIL is already established.

Overall verdict equals T2_SCIENTIFIC_OUTCOME. Scientific FAIL has precedence. Valid poor outcomes never become INCONCLUSIVE. Mechanism observability never changes scientific PASS/FAIL/INCONCLUSIVE. Scientific PASS with COMPLETE, PARTIAL or FAILED trace remains PASS with corresponding diagnostic limitations.

All eight request capture_stage_trace=true; preserve EA_ADMISSION, A0_OUTPUT, V1_INPUT/OUTPUT, A1_INPUT/OUTPUT/POST_MERGE, V2_INPUT/OUTPUT and C_INPUT/OUTPUT as applicable. Legitimately unexecuted stages are NOT_EXECUTED, not missing capture.

T2_MECHANISM_OBSERVABILITY: COMPLETE when g013/g023 permit initial/EA/V1/A1 authorization or non-activation/applicable V2 classification; PARTIAL when some target stage cannot be classified; FAILED when trace absent/corrupt enough to prevent interpretation. Diagnostic only; no rerun for trace or ambiguity.

Preserved ordered, non-exclusive taxonomy:

- **INITIAL_COMPLETE**: A0 reviewed claims already contain all target necessary relations and accepted V1 declares complete; retain claim/relationship evidence, not verdict alone.
- **EA1_BACKING_RESOLVED**: EA_ADMISSION records RESOLVED_EXACT_BACKING with actual parent/child/offset identity. Participation in successful target answer requires traceable relevant child citations; resolution alone does not prove effect.
- **C1_GAP_DETECTED_REVISIONABLE**: Accepted V1 records ESTABLISHED unsatisfied ADMITTED_BACKING_AVAILABLE relation and A1 actual scope includes it.
- **C1_GAP_BLOCKED_VISIBLE_ONLY**: Necessary visible-only relation is unsatisfied and excluded from A1 repair authority.
- **C1_GAP_AMBIGUOUS**: Uncertain check and uncertain point scope, incomplete/non-revisionable; overflow recorded separately as blocked, never forced into uncertainty.
- **A1_RECOVERY_SUCCESS**: Initially missing target relation is observed; C1 authorizes bounded A1; post-merge/V2 and existing final evaluator establish recovered target relation. No global causal attribution.
- **A1_RECOVERY_FAILED**: Observed authorized recovery leaves target relation absent/incomplete or removed; retain actual merge disposition and final verdict.
- **C1_FALSE_ACCEPTANCE_RECURRENCE**: Only when retained reviewed claims establish target relation absent while actual production C1 review declares its point complete. Final judge disagreement alone is insufficient; absent trace means NOT_ESTABLISHED.
- **TARGET_MECHANISM_NOT_NEEDED**: Initial answer succeeds without the target recovery stage; scientific PASS is allowed; do not claim recovery proven.
- **NOT_OBSERVABLE**: Required trace missing/corrupt/insufficient for classification; NOT_ESTABLISHED for uncertain semantic or causal inference.

Use retained structured trace, existing final-answer judge, deterministic outputs and fixed criteria; no second LLM judge. No required EA1/A1 activation for scientific PASS, no causal inference without relevant evidence; uncertainty => NOT_ESTABLISHED/NOT_OBSERVABLE.

## Historical pairing and final stop rule

T1 remains FAIL, 65 calls / 373,265 tokens. Preregistration `421c13a6efc76a845cfd61388e1e2520eea799a7`; result `3d9ca981680ac44940816c294fcc85c9bfc19689`. Report frozen paired g013 FAIL -> T2, g023 FAIL -> T2, g047 PASS -> T2, g011 safety PASS -> T2, controls CONTROL_PASS x4 -> T2. g011 native-documentation role remains separate; Workstream D deferred. No replay, rescore or statistical generalization claim.

T2 is the final planned scientific validation of this F6-A repair loop:

| Terminal T2 | POST_A5_REPAIR_VALIDATION | F6_A_REPAIR_LOOP |
| --- | --- | --- |
| PASS | CLOSED / EXPOSED_SENTINEL_PASS | CLOSED |
| FAIL | CLOSED / EXPOSED_SENTINEL_FAIL / LIMITATION_ACCEPTED | CLOSED |
| INCONCLUSIVE | CLOSED / VALIDATION_INCONCLUSIVE | CLOSED |

This is a lifecycle rule, not a scoring rule. No automatic T3, T2-R1, repair cycle, integration closeout or Attempt 6. A future generic defect requires separate normal product-development authorization and does not automatically reopen F6-A.

ATTEMPT_6 = DEFERRED / NOT_NEXT_STEP; F6_B = NOT_ENTERED / NOT_NEXT_STEP. Candidate frozen=false; Attempt 6 preregistered/executed=false; readiness remains NOT_READY. Formal release is a later explicit milestone. Historical Attempt 1-5 and T1/O1/EA1/C1/C1-R1/integration records unchanged.

## Verification and remaining boundary

Gold/prompt/selector identities verified, calibration compatible; eight approved exposed dev answered cases and T1 order verified. Existing full judge and development trace supported. JSON/invocation syntax and permitted-path checks passed; git diff --check required before commit. No tests or scientific execution needed.

Scientific calls/tokens=0/0; T2 preregistered=true on commit, executed=false; no T2 run directory created. Protected contents untouched: novel_validation=PRISTINE_FOR_CURRENT_LINEAGE, holdout access=0, protected leakage=0, F6-B execution=0.

SOURCE_CHANGE, MATERIAL_PRODUCT_CHANGE, PROMPT_CHANGE, EVALUATOR_CHANGE, GOLD_CHANGE, CALIBRATION_CHANGE = false.

Only next and final planned F6-A task: POST-A5 T2 FIXED EXPOSED SENTINEL EXECUTION + TERMINAL RESULT + F6-A REPAIR LOOP CLOSEOUT. Result and closure remain one task. No execution authorization here.

NEXT_TASK_EXECUTION_AUTHORIZED = false
