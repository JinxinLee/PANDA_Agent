# Post-A5 T2 Fixed Exposed Sentinel Scientific Validation Design

**COMPLETE / HOLD / T2_EXECUTION_CONTRACT_NOT_CURRENTLY_AVAILABLE**

Blocking reason: **HARD_BUDGET_NOT_ENFORCEABLE_WITH_CURRENT_RUNNER**. The scientific protocol below is fixed as a design proposal, not preregistration and not executable authority. All independent design work is complete; strict budget enforcement remains unavailable. No runner repair is made here.

T2 is exposed repair-target evidence, not independent generalization evidence. Classification: **FIXED EXPOSED REPAIR-TARGET REGRESSION STUDY**, development scientific evidence. The cohort was exposed in T1 and informed product engineering. Success supports only the fixed repaired cohort plus controls, not general effectiveness, release readiness or Attempt 6.

## Identity and precheck

Starting HEAD `6a64891165d34346a37c5a599d837d81bdd7df9f`; behavior head `6ed3ba361476b36744c72e76f5905733b1755f5c` unchanged. Prompt `3.11.0` / `03e1bf270898b28127a42fa2e1ccb24cfc1d87e177eeba5428ba4680d426352c` mechanically verified.
Gold v2.11 SHA `39943c6a3f2152e476109c0340acd066795c8de6ff3b6bb2eac6661ac480a417` verified from bytes. Calibration v8 compatible, 59 formal-English / 21 non-English; derived selector SHA `e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5` verified using repository canonical sorted-ID JSON. No per-file hash manifest.

Normal product mode `production_answer_obligations_v1`. All eight current objects are approved dev, expected answered; dataset acceptance_exposed=true, release_eligible=false. T1 preregistration and result confirm exposure and exact cohort/order. Future P0 repeats exact Gold identity/object/approval/exposure checks. Any mismatch: HOLD / T2_COHORT_CONTRACT_NO_LONGER_MATCHES, never substitution.

## Fixed cohort and sequence

Affected: g011, g013, g023, g047. Controls: g010, g014, g022, g050.
Order: **g011 -> g010 -> g013 -> g014 -> g023 -> g022 -> g047 -> g050**.
One logical execution each; run IDs `post-a5-t2-<case_id>` for precisely these IDs. No reorder, replacements, additions or replicate block.

## Existing invocation and tracing

Verified current Python entry point supports the following argument combination. **Do not execute this example**: the budget blocker must be resolved, P0 committed/reviewed and execution separately authorized first.

```python
from pathlib import Path
from panda_agent.evaluation_runner import run_evaluation

# DESIGN ONLY: DO NOT EXECUTE before budget blocker closure, reviewed T2-P0
# commit, and separate explicit authorization for scientific execution.
root = Path(r"C:\Users\Jinxin.DESKTOP-H6SSTQH\Desktop\Agent_learn\PANDA_Agent")
run_evaluation(
    root, mode="full", split="dev", run_id="post-a5-t2-g011",
    allow_draft=True, resume=False, case_ids=["g011"],
    dataset_path=root / "evaluation/benchmarks/v2_11/gold_questions.yaml",
    candidate_id=None, capture_stage_trace=True,
    max_model_calls=10, max_token_usage=100000,
)
```

Change only the fixed case ID/run ID according to the locked order. No invented CLI flags; `official` is derived as `not allow_draft`, not a runner argument. `allow_draft=True` only permits non-formal tracing, never draft Gold: independent approved-cohort checks are mandatory. No candidate required.

`evaluation_mode_boundaries('full')` enables external judge independently of official. `_configure_stage_trace` accepts full/dev/official=false/candidate=null, and manifest retains capture choice. `_execute_evaluation_case` uses the existing final-answer external judge. No second mechanism judge. This combination is available; it is not the HOLD cause. If it becomes unavailable use HOLD / T2_TRACE_AND_FULL_JUDGE_CONTRACT_UNAVAILABLE.

All eight request trace. Preserve EA_ADMISSION, A0_OUTPUT, V1_INPUT/OUTPUT, A1_INPUT/OUTPUT/POST_MERGE, V2_INPUT/OUTPUT, C_INPUT/OUTPUT when executed. Legitimate absent stages are NOT_EXECUTED, not missing capture. Persist existing manifest, records, diagnostics, usage, exceptions and retrieval trace; no parallel model-based trace interpretation.

## Hard budget: required numbers, unavailable enforcement

Required fixed ceiling: **10 provider/model calls and 100,000 tokens per case; 80 calls and 800,000 tokens cohort-wide, including retries/resume**. No adaptive extension. These numbers are retained as requirements, not falsely certified as enforceable by current runner flags.

T1 used 65 / 373,265; maxima 14 calls (g013), 67,573 tokens (g050). Aggregate headroom is 15 calls / 426,735 tokens. Seven runtime stages do not bound provider attempts: judge, embedding and internal retries also count. A 10-call cap may legitimately interrupt a case; it is a safety ceiling, not an expectation of completion.

Static findings:

- `evaluation_runner.py:465` compares already-observed totals. Around lines 1777-1887 it checks only before/after a complete case and resets attempt totals at resume. A one-case run can exceed both limits before detection.
- `llm/vertex.py:114` counts each request attempt; generation has up to three attempts, embedding up to five. Usage is recorded after a response; missing provider metadata is not evidence of zero billed tokens.
- No remaining-budget gate or output-token reservation is applied by this runner invocation. An external check between cases cannot prevent an in-flight case overshoot. Raising fixed numbers cannot repair this semantic mismatch.

Therefore **no mechanically justified fixed numerical adjustment can establish the requested hard ceiling** through the existing entry point. P0 must HOLD until separately authorized budget-contract resolution is reviewed. Do not substitute a soft post-case threshold, reset the allowance on resume, or implement an ad-hoc wrapper here.

Resource exhaustion: stop without extension; incomplete case INCONCLUSIVE / RESOURCE_LIMIT unless valid scientific FAIL already exists. A completed valid failure takes precedence. Preserve outputs and consumption even when the budget contract is breached; never rerun to improve them.

## Fixed scientific criteria

### g013

Scientifically valid completed final result must be answered, critical_answer_point_miss_count=0, and satisfy current hard-safety/trustworthiness invariants. An inappropriate insufficient_evidence result is FAIL, not INCONCLUSIVE. Missing evaluator data is not interpreted as zero. All critical points, including active Gold p3 master-run-task/lifecycle obligation, must be satisfied. EA1 or A1 activation is not required. Record EA admission, initial V1 completeness, revisionable gaps, revision_count, A1 merge dispositions and V2 where applicable.

### g023

Scientifically valid completed final result must be answered, critical_answer_point_miss_count=0, and satisfy current hard-safety/trustworthiness invariants. An inappropriate insufficient_evidence result is FAIL, not INCONCLUSIVE. Missing evaluator data is not interpreted as zero. Explicitly establish active Gold p3 generic workflow placement, including the relation to PID; a bag of reconstruction/digitization/PID/PndMasterRecoTask mentions does not pass.

### g047

Scientifically valid completed final result must be answered, critical_answer_point_miss_count=0, and satisfy current hard-safety/trustworthiness invariants. An inappropriate insufficient_evidence result is FAIL, not INCONCLUSIVE. Missing evaluator data is not interpreted as zero. Explicitly relate elastic differential cross section to luminosity extraction; inappropriate new refusal fails the positive contrast.

### g011

Scientifically valid completed final result must be answered, critical_answer_point_miss_count=0, and satisfy current hard-safety/trustworthiness invariants. An inappropriate insufficient_evidence result is FAIL, not INCONCLUSIVE. Missing evaluator data is not interpreted as zero. C_NEGATIVE_EXISTENCE_SAFETY=PASS: no unqualified documentation/corpus-wide claim that no independent native setup path exists without deterministic exact-lookup absence authority. Separately record C_NATIVE_DOCUMENTATION_ROLE_COVERAGE=PASS/FAIL/NOT_APPLICABLE from active Gold critical role matching; role failure does not gate this negative-existence mechanism. Workstream D remains deferred.

### controls

Each of g010,g014,g022,g050 is CONTROL_PASS iff answered, critical_answer_point_miss_count=0, no contradiction, no major unsupported claim, no forbidden/wrong-version evidence, no identifier hallucination under current evaluator, no unhandled exception, no hard-safety/trustworthiness violation and no new inappropriate refusal. Citation-source variation alone is not failure when v2.11 accepted evidence-role contracts are satisfied.

The existing external final-answer judge and deterministic metrics remain authoritative under current Gold/evaluator contracts. For required explicit relationships, record supported pass evidence; unresolved semantic interpretation is not silently accepted. Do not add a new LLM judge or change Gold after seeing output. A Gold-answered refusal is FAIL; any claim that the question should instead be unanswerable needs separate governance after terminal result, not a T2 exception.

## Ordered descriptive mechanism taxonomy

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

Multiple labels may occur in causal stage order. Activation is not an independent scientific pass condition. A complete initial answer can PASS with TARGET_MECHANISM_NOT_NEEDED. Relevant EA participation requires actual child/admission/citation linkage; revision recovery requires observed gap, authorization, A1 merge and V2 recovery. Neither observation proves unseen-data effectiveness or isolates causal contribution of a whole repaired stack.

## Verdicts: disjoint, in priority order

1. **FAIL**: any scientifically valid fixed case fails its criterion, or a valid hard-safety/trustworthiness failure occurs. This overrides incomplete traces, resource stops and uncompleted later cases.
2. **PASS**: all eight scientifically complete; all sentinels PASS and four CONTROL_PASS; no safety failure; g013/g023 mechanism observability COMPLETE.
3. **INCONCLUSIVE**: no established scientific FAIL, but scientific completion/identity/infrastructure/transport/resources or required target trace prevents interpretation.

Report T2_SCIENTIFIC_OUTCOME separately: PASS iff all eight meet scientific gates; FAIL if any valid scientific gate fails; otherwise INCONCLUSIVE. Missing trace alone can coexist with scientific PASS.

Report T2_MECHANISM_OBSERVABILITY separately: COMPLETE when both targets permit initial state, EA, V1, A1 authorization/non-activation and V2 where applicable; PARTIAL when some interpretation survives but a required target stage is unclassifiable; FAILED when missing/corrupt target trace prevents mechanism interpretation. Natural non-activation counts as observable. Scientific PASS plus PARTIAL/FAILED yields overall INCONCLUSIVE, never a scientific rerun.

## Paired baseline and recovery

Frozen T1: preregistration 421c13a6efc76a845cfd61388e1e2520eea799a7; result 3d9ca981680ac44940816c294fcc85c9bfc19689; FAIL, 65 calls / 373,265 tokens. Chronology authority remains the later retained provenance reconciliation; no historical record is rewritten.

Report g013 FAIL -> T2, g023 FAIL -> T2, g047 PASS -> T2, g011 safety PASS -> T2, controls CONTROL_PASS x4 -> T2. g011 native-documentation role failure is a separate non-gating axis for the safety mechanism; not evidence that no usable native-path evidence exists. No p-value or statistical generalization from these eight selected exposed cases.

Scientific reruns forbidden: no second chance, best-of-N, stochastic replicate, judge-disagreement retry, poor-result retry, non-activation retry, or trace-repair retry. A valid completed case is never rerun.

Only existing repository-classified retryable transport/infrastructure recovery can be considered, with identical run/case/P0 HEAD/behavior/prompt/Gold/calibration/evaluator/trace setting. Preserve completed records. Existing provider retries are unchanged; all consumption must count cumulatively. Current fresh attempt budgets do not provide this guarantee, so recovery remains blocked with the execution budget contract; no new retry policy or numeric allowance is invented.

## Chronology and immutable execution boundary

DESIGN -> review and separately authorized blocker resolution -> re-reviewed design -> zero-call T2-P0 preregistration commit -> review plus explicit scientific execution authorization -> first QA/retrieval/embedding/judge call -> fixed eight-case sequence -> frozen terminal result.

P0 must exist before any scientific call and be execution HEAD. Bind behavior, prompt, Gold, calibration and current model/corpus/index identities. Require empty `git diff <PRODUCT_BEHAVIOR_HEAD>..<T2_PREREGISTRATION_HEAD> -- src/panda_agent`. No candidate freeze or per-file hash manifest. If separate budget infrastructure work affects source identity, reconcile the design before P0; do not silently waive the drift gate.

No QA/prompt/storage/evaluator/Gold/calibration/threshold edits or test-driven repair between P0 and terminal result. Freeze FAIL before separately authorized RCA/repair. No T2 run directory created by this design.

## Verification, materiality and limits

JSON parses; fixed cohort/order equal T1; all eight approved exposed dev objects verified; Gold and selector hashes and prompt fingerprint mechanically verified; source diff from behavior head empty. Full judge plus development trace verified statically. No tests or scientific execution were needed. Hard budget gate is HOLD; the remaining independent design checks are satisfied. This is not READY_FOR_PREREGISTRATION.

SOURCE_CHANGE, MATERIAL_PRODUCT_CHANGE, PROMPT_CHANGE, EVALUATOR_CHANGE, GOLD_CHANGE, CALIBRATION_CHANGE = false. Scientific calls/tokens = 0/0. T2_preregistered=false; T2_executed=false.

Protected content not accessed. novel_validation=PRISTINE_FOR_CURRENT_LINEAGE; holdout access=0; protected-content leakage=0; F6-B execution=0. Candidate frozen=false; Attempt 6 preregistered/executed=false; ATTEMPT_6_READINESS=NOT_READY, including after any future T2 PASS until separate readiness decision.

Next recommendation: **POST-A5 T2 HARD-BUDGET EXECUTION CONTRACT REVIEW / BOUNDED DESIGN RESOLUTION**, separately authorized and zero-call; no implementation permission implied. Only after resolution and design PASS recommend **POST-A5 T2-P0 / FIXED EXPOSED SENTINEL PREREGISTRATION**, itself zero-call, then separate execution authorization.

NEXT_TASK_EXECUTION_AUTHORIZED = false
