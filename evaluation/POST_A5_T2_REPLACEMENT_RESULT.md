# Post-A5 Fixed Eight-Case T2 Replacement Result

**COMPLETE / FAIL / REPLACEMENT_VALIDATION_FAIL**

This record closes the authorized replacement T2 after the final C1 Vertex structured-schema smoke passed. It uses the repaired product identity and the fixed order `g011,g010,g013,g014,g023,g022,g047,g050`. The run is valid for the stated exposed repair-target scope; it is not a release evaluation and does not reopen F6-A.

## Execution identity and contract

- Replacement T2 product identity: `58bd53a86627ff0e0b668915076d974272e86233`.
- Prompt set: `3.11.2`.
- Prompt fingerprint: `878caffb022dd66111b3bc6e98c6e372340cb619db13aa856c09aaa09e8b8391`.
- Gold: `m6-benchmark-v2.11`.
- Calibration: `phase_b_t3_product_language_scope_v8`.
- Contract: `run_evaluation`, `mode=full`, `split=dev`, `allow_draft=True`, `candidate_id=None`, `capture_stage_trace=True`, explicit Gold v2.11 path, one case per invocation, no model-call or token quota.
- Same-identity recovery was used only for the interrupted/retryable `g011` and `g047` executions. No tracked files changed between the implementation commit and T2 completion.

The earlier pre-repair T2 record remains unchanged as historical infrastructure-invalid evidence: 8/8 attempted, 0/8 scientifically valid, 56 calls / 288,539 tokens, 9 embedding calls, 0 judge calls, and one transport recovery. It is not combined with the replacement result.

## Case results

| Case | Result | Critical miss | Trace / mechanism | Verdict |
|---|---|---|---|---|
| `g011` | answered; zero critical misses | none | complete; negative-existence safety passed; native documentation role separately uncovered | **PASS** for the requested sentinel |
| `g010` | answered; zero critical misses | none | complete | **CONTROL_PASS** |
| `g013` | insufficient_evidence | `p3` / `point.3` | complete; `C1_GAP_BLOCKED_VISIBLE_ONLY`; A1 and V2 not executed | **FAIL** |
| `g014` | answered; zero critical misses | none | complete | **CONTROL_PASS** |
| `g023` | answered | `p3` | complete for the observed runtime point set; Gold p3 absent from runtime trace; causal recovery not established | **FAIL** |
| `g022` | answered; zero critical misses | none | complete | **CONTROL_PASS** |
| `g047` | insufficient_evidence | `p1` / `point.1` | complete after one retryable 500 recovery; explicit elastic differential cross section to luminosity extraction relation not fully established | **FAIL** |
| `g050` | insufficient_evidence | `p1` / `point.1` | complete; coverage not evaluable because the basis quote was not exact or exceeded the bound | **CONTROL_FAIL** |

The g011 negative-existence safety result is PASS because the answer did not make an unqualified corpus-wide absence claim. Its native-documentation role is separately **FAIL / NOT_COVERED** (`critical_final_evidence_recall=0.5`) and does not gate that negative-existence mechanism criterion.

The g013 result is an exposed C1 gap: point 3 was visible only without citable backing, so the trace correctly blocked completeness and did not authorize A1. The g023 result is a runtime-observability boundary: the trace was complete for its exposed point set, but the Gold-required p3 was not present in that trace. Neither case supports a claim of C1 recovery.

## Usage and validity

Replacement T2 aggregate usage was **63 model/provider calls / 345,411 tokens / 8 embedding calls / 10 judge calls**, with **one transport recovery event**. Per-case calls/tokens were:

- `g011`: 8 / 34,719
- `g010`: 10 / 31,180
- `g013`: 7 / 43,807
- `g014`: 7 / 37,645
- `g023`: 7 / 42,103
- `g022`: 8 / 47,478
- `g047`: 9 / 40,965
- `g050`: 7 / 67,514

All eight stage traces have `capture_status=COMPLETE`. The failures are therefore valid sentinel/control outcomes for this scope. The earlier T1 baseline remains historical **FAIL** (65 calls / 373,265 tokens).

## Lifecycle and protected state

- F6-A remains **CLOSED**. This result is post-F6-A compatibility-repair validation, not a new F6-A attempt.
- Attempt 6 remains `DEFERRED / NOT_NEXT_STEP`.
- F6-B was not entered; holdout access and protected leakage are both zero.
- No T2-R1, T3, candidate freeze, release evaluation, or F6-B execution is authorized by this result.

**Replacement T2 remains exposed repair-target evidence, not independent generalization evidence.**

Final status: **COMPLETE / FAIL** for the fixed replacement T2 scope.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`

`STOP.`
