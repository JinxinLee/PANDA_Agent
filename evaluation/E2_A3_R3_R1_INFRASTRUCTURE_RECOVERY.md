# E2-A3-R3-R1: Infrastructure Recovery and Activation Completion

## Frozen preparation record

Starting HEAD `29bc2864a95b797ecfc07d3824711c5dc855ff95` was clean. Product candidate
`fd0aed4c7e491a569bf39271825cc0950630863d` remains unchanged; default legacy.
Historical R3 protocol/raw/judged/result identities are reconstructed from Git.
Exactly g059/g047/g001 lack authoritative pairs due to three ConnectionTimeout
events and one provider 429. The remaining eleven original pairs are complete.

The recovery replaces both arms for each affected case, never mixing old/new
arms. Original indices 0/1/3 preserve order and A/B labels. Only three fresh
pairs and at most three fresh judgments are authorized. The old eleven remain
untouched and are reused only in final fourteen-pair scoring. Historical R3
INCONCLUSIVE, A3/R1 FAIL, R2 PASS and no-P6-waiver remain authoritative.

Product/provider settings, original G1-G13 and judge schema/prompt are unchanged.
Explicit gate states distinguish PASS/FAIL/NOT_EVALUABLE. Independent product
failures override missing authority; incomplete citation context or missing
fourteen-pair overhead cannot be reported as PASS. G11's existing one-worse
allowance is unchanged and already consumed by original g029.

Focused recovery/composition tests: 32 passed. Tests cover original authority,
infrastructure-only selection, original-index mapping, exact eleven-plus-three
composition with no partial-arm fallback, each product gate, missing-authority
states, independent failure precedence, prior-worse allowance, complete fourteen-
pair denominator, strict judge boundary, ambiguous STARTED protection, and
evaluator snapshot retention on answer/revision provider exceptions. No product
tests or prior scientific cases were rerun; no provider call before freeze.

The only added runtime instrumentation is an evaluation subclass copying the
selected evidence before answer/revision generation, so partial provider failures
retain citable-context diagnostics where available. This does not alter product
code, prompts, schemas, outputs or retrieval. No recovery-specific retry policy.

## Scientific closeout

E2-A3-R3-R1 = COMPLETE / FAIL / G11.

Infrastructure recovery completed: six fresh successful QA executions and three
successful blinded judgments. The combined authority is exactly eleven original
complete pairs plus three fresh recovery pairs, with fourteen judgments. No
scientific replay, rejudge, old/new arm mixing, case replacement, or product
repair occurred. Historical R3 remains INCONCLUSIVE.

G11 fails: runtime quality is 1 better / 11 equivalent / 2 worse. The original
g029 noncritical worse result is preserved, and recovery g001 adds a second
noncritical worse result. Thus worse 2/14 exceeds 1/14, and better plus equivalent
12/14 is below 13/14. All other gates PASS with complete required authority.
No threshold adjustment, historical P6 waiver, or reinterpretation is applied.

The g001 original index is 3: A = runtime and B = legacy. The frozen judge prefers
B because it explicitly states the snapshot commit hash, addressing the approved
reference's commit-specific repository behavior requirement. Both outputs are
supported and critical_regression is false. This observation does not establish
a repair design or authorize tuning to the exposed case.

## Immutable provenance

| Identity | Commit |
| --- | --- |
| Starting HEAD / historical R3 result | `29bc2864a95b797ecfc07d3824711c5dc855ff95` |
| Product candidate | `fd0aed4c7e491a569bf39271825cc0950630863d` |
| Original R3 protocol | `0a276a40968ed67fb784c37676d172314fb1210d` |
| Original R3 raw | `6d760be1eae1e803d8f6c4ff6b374a13dbed4713` |
| Original R3 judged | `77388ec9c2564cce82d0db24ef97a15da62d4779` |
| Recovery protocol | `3a93f081a77e8bb507b14729a981dc1fa9c1f449` |
| Recovery raw | `0bc039d39211540843863d73ef9dd2be430087cd` |
| Recovery judged | `5f260a3fa92ade82528825669e0f5360fe1bc34e` |
| Recovery result | The commit introducing `e2_a3_r3_r1_activation_completion_result.json` |
| Activation | NOT CREATED |

The result JSON contains each pair's authority_source, raw_commit,
judged_commit and execution_ids. Result identity is resolved from Git history,
not a self-referential commit field. No evidence boundary is amended or squashed.

## Recovery outcomes

| Case | Original index | Fresh order | Legacy / runtime status | Blinded preference | Runtime quality |
| --- | ---: | --- | --- | --- | --- |
| g059 | 0 | legacy then runtime | answered / answered | equivalent | equivalent |
| g047 | 1 | runtime then legacy | answered / answered | equivalent | equivalent |
| g001 | 3 | runtime then legacy | answered / answered | B (legacy) | worse, noncritical |

Terminal connection timeouts = 0; terminal provider 429 = 0; other terminal
provider failures = 0; unscoreable recovery pairs = 0; scientific case replays = 0.
Two legacy operations used two adapter requests each (g059 analyzer and g001
reranker); both returned successfully. Intermediate attempt error types are not
exposed by these usage records, so zero terminal failures does not imply zero
transient adapter events. The original retry policy was unchanged.

Qdrant emitted a client 1.19.0 / server 1.15.5 compatibility warning. It did not
prevent these six executions; no dependency, server or provider setting changed.

## Combined authority and gates

| Gate | State | Evidence |
| --- | --- | --- |
| G1 | PASS | 14 legacy outputs, 14 runtime outputs, 14 judgments |
| G2 | PASS | Correct expected status: legacy 14/14, runtime 14/14 |
| G3 | PASS | New runtime false answers: 0 |
| G4 | PASS | New runtime false refusals: 0 |
| G5 | PASS | No new registered critical verifier category across all reviews |
| G6 | PASS | Invalid Sphinx edges, incomplete web errors, admission mismatches: 0 |
| G7 | PASS | Valid runtime decomposition 14/14; applicable answered coverage 10/10 |
| G8 | PASS | Legacy decomposition 0; runtime revision <=1; post-verify retrieval 0 |
| G9 | PASS | Runtime supported 14/14; legacy supported 14/14 |
| G10 | PASS | Critical runtime regressions 0 |
| G11 | FAIL | Better/equivalent/worse 1/11/2; worse exceeds 1 and non-worse below 13 |
| G12 | PASS | (75 - 61) / 14 = 1.0 additional generation calls, threshold <=2.0 |
| G13 | PASS | Frozen boundaries and R-F1 through R-F11 preserved |

All gate authority_complete fields are true. Zero-tolerance violations = 0.
Unknown accepted point IDs = 0; structural review errors = 0; runtime valid
one-decomposition executions = 14. All ten expected-and-final answered outputs
have coverage_evaluable and coverage_complete true. Four correct refusals retain
the registered exception; their false coverage flags are not coverage failures.
Two runtime executions revise once (historical g113/g050); none revises more
than once. Public DTO remains unchanged and coverage metadata stays internal.

G5 does not mean every intermediate review was error-free. For example, recovery
g059 legacy initially reports missing factory_composition and resolves it in its
single revision. Historical compatibility-review observations remain preserved;
no registered new runtime critical category is introduced.

| Case | Source | Runtime quality | Legacy generation | Runtime generation | Delta |
| --- | --- | --- | ---: | ---: | ---: |
| g059 | r3_r1_recovery | equivalent | 7 | 5 | -2 |
| g047 | r3_r1_recovery | equivalent | 4 | 5 | 1 |
| g028 | original_r3 | equivalent | 4 | 6 | 2 |
| g001 | r3_r1_recovery | worse | 5 | 5 | 0 |
| g105 | original_r3 | equivalent | 4 | 5 | 1 |
| g113 | original_r3 | better | 6 | 7 | 1 |
| g014 | original_r3 | equivalent | 4 | 6 | 2 |
| g060 | original_r3 | equivalent | 6 | 6 | 0 |
| g050 | original_r3 | equivalent | 6 | 7 | 1 |
| g029 | original_r3 | worse | 4 | 7 | 3 |
| g057 | original_r3 | equivalent | 3 | 5 | 2 |
| g041 | original_r3 | equivalent | 3 | 4 | 1 |
| g007 | original_r3 | equivalent | 3 | 4 | 1 |
| g108 | original_r3 | equivalent | 2 | 3 | 1 |

Original R3's eleven-pair diagnostic was 1/9/1 quality and 15/11 overhead;
recovery adds 0/2/1 quality and -1 generation-call delta. The authoritative
fourteen-pair totals are 1/11/2 and 14/14 = 1.0. This completes missing evidence;
it is not a before/after product repair comparison. Old g047 legacy and g001
runtime successes and all old failed arms are excluded from the combined view.

## Usage and cost

Logical operations include recorded local retrieval operations. Returned
responses and adapter requests count separately; observable tokens exclude
unavailable embedding tokens. Monetary cost is unavailable.

| Scope | Logical operations | Returned responses | Adapter requests | Observable tokens |
| --- | ---: | ---: | ---: | ---: |
| Original R3 judge | 11 | 11 | 11 | 211845 |
| Original R3 legacy | 86 | 69 | 72 | 1014387 |
| Original R3 runtime | 89 | 74 | 80 | 915451 |
| Recovery legacy | 20 | 17 | 19 | 244743 |
| Recovery runtime | 21 | 18 | 18 | 174386 |
| Recovery judge | 3 | 3 | 3 | 55887 |
| Original R3 total | 186 | 154 | 163 | 2141683 |
| Recovery total | 44 | 38 | 40 | 475016 |
| Actual original plus recovery total | 230 | 192 | 203 | 2616699 |
| Original failed arms only (subset, not additive) | 7 | 5 | 8 | 30905 |
| Original superseded six partial-pair arms (subset, not additive) | 20 | 16 | 19 | 116981 |

Historical failed-attempt consumption remains actual expenditure. G12 instead
uses only authoritative paired generation calls (61 legacy, 75 runtime), not
judge/embedding calls, retry-attempt counts, or discarded partial-arm costs.
Recovery scientific/provider calls before protocol freeze = 0.
Embedding tokens = unavailable, not zero. No live calls after judgments.

## Independent abstract review

The explicitly requested AGY worker completed successfully after protocol freeze:
job `staffer-mtvi36vz-89828906`, model route `gemini-3.8-flash-high`, staffer mode,
exit 0, one turn, 16.8300319 seconds. Actual effort was not separately exposed.
Reported tokens: input 11525, output 3615, thinking 1878, cache 8159; these are
AGY reporting fields, separate from scientific usage and not summed as disjoint
billing components. No repository evidence or case outcomes were transmitted.

The abstract review identified pair mixing, original-index alignment, missing
trace authority, independent failure precedence, run-local grounding, and
fourteen-pair denominator risks. Frozen composition and focused tests address
these risks. The suggested historical overwrite/tombstone is not adopted:
original artifacts remain immutable and explicit provenance selects full pairs.
Backend temporal drift remains a limitation despite identical configuration.

The wrapper's working-tree warning names only the recovery raw artifact written
by the concurrently running host batch. It is not evidence of a staffer edit;
the worker was instructed not to use tools or edit files. The authorized raw
artifact was retained, not rolled back. No other workspace delta was observed.

## Lifecycle and stop

E2-A3-R3-R1 = COMPLETE / FAIL / G11.
E2 = IN_PROGRESS / RUNTIME_ACTIVATION_FAILED / ACTIVATION_COMPLETION_FAILED.
Normal default remains legacy_question_core; no activation commit or
post-activation tests. The 32 focused recovery/composition tests passed before
protocol freeze; no full suite or prior scientific evaluation was repeated.

Historical A3 FAIL/Q7, R1 FAIL/P2_P6, R2 PASS, and R3 INCONCLUSIVE are preserved.
P6 waiver = no; product repair = no. Phase E remains IN_PROGRESS / E2; E3 remains
NOT_STARTED. Next recommendation is a separate G11 failure review, not an
implementation or new recovery; NEXT_TASK_EXECUTION_AUTHORIZED = false.
No E3, T3, T5, D4, F2, F3, legacy retirement or automatic recovery is performed.

Limitations: fourteen exposed English development cases are not a broad
benchmark; a single frozen judgment per pair is retained without rejudging;
temporal backend drift cannot be ruled out; embedding and monetary costs are
unavailable; G11 failure does not by itself identify the upstream repair layer.

E2-A3-R3-R1 COMPLETE / FAIL
