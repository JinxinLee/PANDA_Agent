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

Final scientific outcome will be recorded after protocol, raw and judgment
commits. PASS-only activation requires a separately committed scientific PASS,
then selector-only change plus focused static tests; no later provider call.
