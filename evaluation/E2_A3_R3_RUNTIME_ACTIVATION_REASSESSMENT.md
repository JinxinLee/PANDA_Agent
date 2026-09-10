# E2-A3-R3: Bounded Runtime Activation Reassessment

## Scientific closeout

**E2-A3-R3 = INCONCLUSIVE / CONNECTION_TIMEOUT_AND_PROVIDER_429_INCOMPLETE_PAIRS.**
No activation commit was created. The normal default remains legacy_question_core.
The frozen scorer reports no observed product failures or zero-tolerance violations,
but the complete fourteen-pair activation contract cannot be established.

| Boundary | Commit |
| --- | --- |
| Starting/product candidate | `fd0aed4c7e491a569bf39271825cc0950630863d` |
| Protocol/preregistration | `0a276a40968ed67fb784c37676d172314fb1210d` |
| Raw outputs | `6d760be1eae1e803d8f6c4ff6b374a13dbed4713` |
| Judgments | `77388ec9c2564cce82d0db24ef97a15da62d4779` |
| Scientific closeout | Commit introducing `e2_a3_r3_runtime_activation_result.json`, titled `E2-A3-R3 close bounded runtime activation assessment` |
| Activation | NOT CREATED |

The final delivery records the closeout commit SHA; Git history avoids a
self-referential commit hash. No product, frozen protocol, test, cohort, provider,
Gold or historical evidence change occurred after protocol freeze. No scientific
repair, failed-case replay, rejudge or extra activation experiment occurred.

## Execution completeness and infrastructure failures

All 28 execution records reached terminal COMPLETE (14 per arm); this includes
failed attempts and is not equivalent to 28 successful QA results. Valid final
QA outputs: legacy 12/14, runtime 12/14. Four failures affected three pairs:

| Case/arm | Preserved failure |
| --- | --- |
| g059 legacy | ConnectionTimeout: connection timeout expired |
| g059 runtime | ConnectionTimeout: connection timeout expired |
| g047 runtime | ConnectionTimeout: connection timeout expired |
| g001 legacy | VertexCallError: gemini-3.8-flash 429 RESOURCE_EXHAUSTED during structured generation |

On continuation, the existing process was allowed to finish its in-flight
execution. It ended with 15 terminal records and no ambiguous STARTED record.
The same frozen runner then skipped those 15 records (including failures) and
executed only the 13 never-started arms. No failed arm was rerun. Intermediate
inspection was limited to process/record identity, terminal state and errors.

Raw was committed before judging. The judge phase persisted 14 terminal records:
11 actual model calls returned strict authoritative judgments; three pairs
(g059, g047, g001) were marked unscoreable without a judge call because their raw
pair was incomplete. Fabricating missing outputs or calling a judge on an invalid
pair would violate the frozen protocol. All judgment records were committed
before outcome inspection and deterministic scoring. No judgment provider failed.

## Observed outcomes and denominator boundaries

| Case | Legacy status | Runtime status | Blinded outcome |
| --- | --- | --- | --- |
| g059 | unavailable | unavailable | unscoreable |
| g047 | answered | unavailable | unscoreable |
| g028 | answered | answered | equivalent |
| g001 | unavailable | answered | unscoreable |
| g105 | answered | answered | equivalent |
| g113 | answered | answered | runtime better |
| g014 | answered | answered | equivalent |
| g060 | answered | answered | equivalent |
| g050 | answered | answered | equivalent |
| g029 | answered | answered | runtime worse, noncritical |
| g057 | insufficient_evidence | insufficient_evidence | equivalent |
| g041 | insufficient_evidence | insufficient_evidence | equivalent |
| g007 | insufficient_evidence | insufficient_evidence | equivalent |
| g108 | version_conflict | version_conflict | equivalent |

Each arm has 12 observed correct statuses and two unavailable outcomes; do not
label unavailable results incorrect or correct. On the 11 fully scoreable pairs,
status is 11/11 in each arm, with no new false answer/refusal. Four refusal controls
complete correctly in both arms. Runtime better/equivalent/worse = 1/9/1 over 11,
critical runtime regressions = 0; legacy/runtime supported = 11/11 each among
judgments. Support on three missing pairs remains unknown, not supported.

Runtime decomposition is valid and called exactly once in all 12 successful
runtime executions; the two connection-timeout runtime attempts never decomposed.
All eight successful expected-answered runtime cases have evaluable/complete
coverage (seven are in scoreable pairs). Four correctly refused runtime controls
have false evaluable/complete flags, permitted as diagnostic by the protocol.
Legacy decomposition calls = 0; observed unknown point IDs = 0; runtime revision
>1 cases = 0; post-verify retrieval = 0. No new critical runtime verifier category
was observed in comparable pairs. Noncritical support/legacy-requirement review
errors remain in g113/g050 histories; they are preserved and not described as
uniformly clean reviews. The registered critical-category set is unchanged.

The frozen scorer records zero invalid Sphinx citation edges, incomplete-web
review errors and admission mismatches. These are observable-surface counts:
g001 legacy failed after model work and has no final selected-evidence diagnostic
bundle, so its complete citation surface cannot be reconstructed by the frozen
scorer. No claim of full 28-arm citation completeness is made. This additional
missing diagnostic authority reinforces INCONCLUSIVE; no instrumentation repair
or rerun was performed.

## Gate decisions

Readiness F1-F10 all PASS; focused T0 30 passed before provider calls.
The following table preserves the exact frozen scorer booleans. TRUE with
incomplete evidence is an observed check, not a complete activation PASS.

| Gate | Frozen boolean | Interpretation |
| --- | --- | --- |
| G1 execution completeness | false | 11 authoritative pairs, not 14 |
| G2 status non-inferiority | true | 11/11 paired correct each; full fourteen-pair comparison unavailable |
| G3 no new false answers | true | 0 observed |
| G4 no new false refusals | true | 0 observed |
| G5 verifier integrity | true | No new registered category on scoreable pairs |
| G6 citation eligibility | true | 0 recorded violations; failed-arm diagnostics incomplete |
| G7 decomposition/coverage | false | Twelve valid successful runtime records, not fourteen authoritative pairs |
| G8 runtime boundaries | true | Observed revision/decomposition/retrieval limits respected |
| G9 absolute support | false | Eleven supported judgments, not fourteen |
| G10 critical regression | true | 0 observed among eleven judgments |
| G11 quality non-inferiority | false | better+equivalent=10, fewer than required 13; worse=1, not an excess-worse product failure |
| G12 call overhead | true | Frozen scorer diagnostic 15/11=1.363636; fourteen complete pairs unavailable |
| G13 public/compatibility | true | Product exactly unchanged from R2; default legacy |

G1/G7/G9/G11 are unmet because authoritative evidence is incomplete. No observed
excess-worse, unsupported-runtime or other frozen product failure was detected.
Missing outcomes are not converted to favorable judgments or a reduced cohort.
The result remains INCONCLUSIVE rather than PASS or a fabricated product FAIL.

## Usage and overhead

| Arm | Logical operations | Returned responses | Adapter attempts | Observable tokens |
| --- | ---: | ---: | ---: | ---: |
| Legacy QA | 86 | 69 | 72 | 1,014,387 |
| Runtime QA | 89 | 74 | 80 | 915,451 |
| Judge | 11 | 11 | 11 | 211,845 |
| Total | 186 | 154 | 163 | 2,141,683 |

Scientific/provider calls before protocol freeze = 0. Counts include observed
failed-attempt work and production adapter retries; no case was scientifically
rerun. Embedding tokens and monetary cost are unavailable, not zero. All recorded
generation adapter attempts: legacy 56, runtime 65, difference 9. Dividing this
partial-attempt consumption difference by 14 gives 0.642857, but is NOT the
preregistered full-pair overhead because failed arms are truncated. Among eleven
scoreable pairs: legacy 45, runtime 60, additional 15/11=1.363636. The complete
fourteen-pair generation overhead is unavailable. No denominator is silently
changed to declare activation success.

Latency diagnostic on successful outputs: legacy median 45.5815 s/p95 148.912 s;
runtime median 53.8555 s/p95 171.377 s. Failed-arm elapsed time is not included.
Qdrant client 1.19.0/server 1.15.5 compatibility warnings occurred; settings were
not changed. AGY abstract review job `staffer-mtvfrwpo-713c2747`, dispatched after
protocol freeze, crashed before worker start with state-lock rename EPERM and
produced no review result. Configured route gemini-3.8-flash-high; actual model,
effort and review completion not observed. No review verdict is claimed.

## Lifecycle and stop

```text
E2-A3-R3 = INCONCLUSIVE / CONNECTION_TIMEOUT_AND_PROVIDER_429_INCOMPLETE_PAIRS
E2 = IN_PROGRESS / RUNTIME_ACTIVATION_FAILED / FINAL_ACTIVATION_REASSESSMENT_INCONCLUSIVE
normal default = legacy_question_core
Phase E = IN_PROGRESS / E2
E3 = NOT_STARTED
NEXT_TASK_RECOMMENDATION = E2-A3-R3 INFRASTRUCTURE / ACTIVATION DECISION REASSESSMENT
NEXT_TASK_EXECUTION_AUTHORIZED = false
activation commit = NOT CREATED
```

Historical A3 FAIL/Q7, R1 FAIL/P2_P6, R2 PASS and both accepted repairs remain
unchanged. No P6 waiver, post-freeze repair, selector activation or post-activation
live/test phase. No E3/T3/T5/D4/F2/F3 or legacy retirement. A subsequent recovery
or reassessment needs separate authorization; this task does not repair or rerun.

Changed files are the R3 runner, evaluator test, manifest, readiness record,
preregistration, report, raw, judged and canonical result, plus the two lifecycle
documents. Production files changed: 0. No further scientific work is pending
within this frozen attempt; missing evidence is preserved as its limitation.

## Frozen preparation record (historical)

Product candidate: `fd0aed4c7e491a569bf39271825cc0950630863d`.
Starting worktree clean. No src/config/prompt/schema/corpus/index change.
Normal default before verdict: `legacy_question_core`.
No scientific/provider calls before protocol freeze, including AGY.

The cohort was independently selected from 59 approved effective-English Gold/dev
records, excluding all six R2 IDs. Remaining pool: 53 (43 answered, 10 nonanswered).
Status-partitioned intent round-robin with ascending IDs gives:
g059, g047, g028, g001, g105, g113, g014, g060, g050, g029, g057, g041, g007, g108.
Composition: 10 answered, three insufficient_evidence, one version_conflict.
Seven intents; no quality-outcome selection or protected/holdout access.
Full selection accounting and approved references are in the manifest.

Readiness F1-F10 passed. Focused evaluator/static tests: 30 passed. These cover
selection, shortages, canonical JSON order, A/B labels, all product gate failure
paths, absolute support even for equivalent pairs, one-versus-two worse cases,
refusal coverage exception, both-arm answer/revision citation integrity,
all-review errors, incomplete/malformed judgments, ambiguous STARTED rejection,
public judge-input allowlist and exact unchanged repaired product. A missing
judge cannot erase independently observed citation/status/integrity/support
product failure. No full suite or scientific call was used for readiness.

Generation/judge: configured gemini-3.8-flash; embedding gemini-embedding-2/3072;
global location, 120000 ms timeout; judge temperature zero. Full settings,
strict judge prompt/schema and G1-G13 are fixed before execution. See
`E2_A3_R3_RUNTIME_ACTIVATION_PREREGISTRATION.md` and
`e2_a3_r3_activation_manifest.json`.

Carried-forward compatible historical evidence: E1 semantic decomposition,
E2 mapping/missing-point validation, A3 retrieval bootstrap and unaffected
gates/PAIR09, bounded R1 normalizer repair and g112 integration, R2 admission
reconciliation (144=106+38) and six fresh repair pairs PASS. These are not new
R3 measurements. A3 FAIL/Q7 and R1 FAIL/P2_P6 remain; R2 PASS remains; no P6 waiver.

The scientific lifecycle is protocol commit -> 28 fresh paired QA -> raw commit
-> 14 blinded paired judgments -> judged commit -> deterministic score -> result
commit. Only a committed PASS permits a separate selector-only activation with
focused fake/static checks and no further live calls. No product repair, extra
experiment, E3/T3/T5/D4/F2/F3 or legacy-requirement retirement is authorized.

G11's <=1/14 noncritical-worse threshold preserves original A3's <=2/28 rate,
not a g002 waiver or statistical confidence guarantee. Critical regressions,
unsupported runtime, new status/verifier errors and invalid citations remain
zero-tolerance. The cohort is exposed development evidence with a same-family
blinded judge; it does not establish final generalization performance.

Scientific outcome and final lifecycle will be recorded after the evidence
commits. No activation decision is claimed by this preparation record.
