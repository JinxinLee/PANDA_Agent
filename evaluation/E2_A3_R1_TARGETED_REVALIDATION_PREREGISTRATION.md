# E2-A3-R1 — Targeted Prospective Revalidation Preregistration

## Authority and repaired candidate

Starting HEAD: e5941c5f9aac45d98b739a48b245be53a41c6d80. Historical A3 remains
COMPLETE / FAIL / Q7; FR1 remains COMPLETE / PASS / REPAIR_JUSTIFIED.
The user authorizes the full R1 lifecycle, including ten fresh QA executions,
five blinded judgments, and PASS-only default promotion. No additional approval
checkpoint follows candidate freeze. No E3, compatibility retirement, T3/T5,
retrieval bootstrap, reindex, D4, F2, or F3 is authorized.

The only candidate product change is a private token helper in qa.py and its
single call in the unsupported-identifier rejecting loop: strip terminal periods,
then one terminal colon unless ending in ::. Extraction, eligibility, substring
matching, cited text construction, positive support, prompts, E1/E2, retrieval,
DTOs, public signatures, and compatibility remain unchanged. Default stays
legacy_question_core until a scientific PASS is committed. Internal legacy,
shadow_e1_v2 and runtime_e1_v2 modes remain available.

S1-S12 are recorded in e2_a3_r1_identifier_normalization_static_result.json.
Actual repaired-code source-loop reconciliation must reproduce 56 executions,
299 serialized claim objects, 157 distinct per-execution snapshots (81 legacy,
76 runtime), with exactly one changed rejection: initial g112 runtime claim_3.
Negative controls remain rejected, no genuinely unsupported base is accepted,
and no accepted identifier check becomes rejected. Otherwise BLOCKED /
REPAIR_SCOPE_REVIEW_REQUIRED; do not freeze or call live providers.

## Fixed cohort and execution

Manifest: e2_a3_r1_targeted_revalidation_manifest.json. Exactly five approved
English Gold development records, copied unchanged from the committed A3 manifest
at the starting HEAD: g112, g110, g002, g044, g027, in that order.
Roles: original failure; two prior unsupported-token controls; two clean
identifier/citation controls. No new dataset selection or protected data access.

Indices 0,2,4 run legacy then runtime; indices 1,3 run runtime then legacy.
Each arm starts a fresh QAAgent, performs its own normal retrieval, and generates
fresh claims/reviews. No historical arm, retrieval bundle, or claim reuse.
Ten attempts total, each atomically persisted as STARTED then COMPLETE, including
exceptions and all usage events. A completed failed attempt is never repeated.
An ambiguous STARTED record cannot be replayed and requires INCONCLUSIVE closeout.
Established transport-layer attempts remain unchanged and are counted; no new
retry policy is introduced. Partial scientific outcomes must not guide edits.

Generation and judge: gemini-3.8-flash, temperature 0, global; embedding:
gemini-embedding-2, 3072 dimensions. Project, timeout, and all provider settings
are frozen in the manifest and checked at each phase. Existing local services
and corpus are reused. No scientific calls occur before candidate commit.

## Blind judging boundary

Commit all ten raw attempt records before any judging. Exactly one judgment
attempt per scoreable pair, five total on the complete path. An incomplete pair
receives a persisted infrastructure error and no unsupported judge call.
Indices 0,2,4: A=legacy/B=runtime; indices 1,3: A=runtime/B=legacy.
Judge sees only question, approved expected status/reference obligations,
identifiers/versions, and each output's public status, answer, public claims,
and complete cited evidence. No mode names, mappings, decomposition, audit,
coverage, history, repair hypothesis, or failure description.

Use the frozen A3 judge prompt, strict schema and validation: preferred A/B/
equivalent; critical_regression boolean; A_supported/B_supported booleans; reason.
critical_regression refers to the nonpreferred output; equivalent with critical
true is invalid infrastructure. No rejudge for malformed or unfavorable outcomes.
The judge is separate-role/input independent, not model-family independent.
Commit judgments before mapping labels or computing any scientific verdict.

## Frozen live gates

| Gate | Required |
| --- | --- |
| P1 | Five complete legacy, five complete runtime, five complete scoreable judgments |
| P2 | Zero new critical verifier categories per case: runtime set minus legacy set, over ALL reviews |
| P3 | g112 runtime no unsupported_identifier category in any review; valid decomposition; evaluable/complete final coverage; no structural review failure |
| P4 | Runtime expected-status correct >= legacy; zero new false answers and zero new false refusals |
| P5 | Zero critical runtime regressions from blinded judgment |
| P6 | Zero runtime-worse judgments; equivalent never counts as better |
| P7 | Runtime decomposition exactly one/case, legacy zero; runtime revision <=1; postverify retrieval zero |
| P8 | Sum(runtime-generation-adapter minus legacy-generation-adapter)/5 <=2.0; exclude embeddings |
| P9 | Unchanged public QAResult/ClaimCitation, API, compatibility, and default legacy before verdict |

P2 uses A3's frozen category extraction and public-citation checks: wrong_version,
unknown_evidence, incomplete_citation, unsupported_identifier, structural_review,
unknown_answer_point. Improvements in one case cannot cancel a new category in
another; category removal is allowed. P3 does not require reproducing the literal
colon: T0 demonstrates that mechanism; prospective QA tests integration.
Decomposition validity requires 1-5 nonempty sequential point.N records, in
addition to normal runtime contract validation. Track all review audits, not
only final state. Record revisions, retrieval trace, errors, public output,
internal diagnostic decomposition/audit, latency, and per-stage usage.

Zero tolerance: protected/holdout access, case-specific product logic, accepted
unknown point IDs, internal claims credited, postverify retrieval, DTO change,
compatibility removal, frozen code/protocol changes, prompt/cohort/gate tuning,
or selective reruns. Check frozen Git boundaries per phase and all persisted
review/final audits. Product/protocol violations are FAIL even with incomplete
judging. A local ValueError after a successfully returned model response is
recorded as a product-contract violation, not silently counted as provider outage.

PASS requires all S1-S12, P1-P9 and zero-tolerance checks plus authoritative
judging. Complete scoreable product-gate failure means FAIL. Genuine provider,
judge, or ambiguous persisted-execution evidence insufficiency means INCONCLUSIVE.
Do not use a partial-score average to promote an incomplete cohort. All gates
retain their limits after exposure. Do not rerun or repair on failure.

## Provenance and conditional activation

Separate ordinary Git commits: repaired candidate/protocol -> raw -> judged ->
scientific result/report -> PASS-only selector promotion/lifecycle. No squash,
amend, hash inventory, or mutation of historical A3/FR1 artifacts.
Runner imports unchanged A3/A2 helper implementations; these are frozen too.
Persisted results must equal deterministic JSON-canonical recomputation.

After committed PASS only, change DEFAULT_ANSWER_POINT_MODE from
legacy_question_core to runtime_e1_v2. No other production change. Focused fake
tests must demonstrate both public entrypoints route to runtime, one decomposition,
point.N/audit diagnostics, unchanged DTO, explicit legacy and shadow availability,
bounded revision/no E3 retrieval, and compatibility. Directly necessary default
test expectations and lifecycle docs may change in this activation commit.
FAIL/INCONCLUSIVE means no promotion and no further repair.

Historical A3 Q1-Q6, Q8-Q15 and PAIR09 are carried-forward compatible historical
evidence, not fresh repaired-candidate measurements. This bounded decision relies
on FR1 ownership, exactly one repaired-code frozen rejection delta, unchanged
surrounding behavior, and these five fresh pairs. It is not representative
generalization, T3/T4/T5, release evaluation, or legacy-requirement retirement.

## Usage and independent static review

Report logical operations, returned responses, adapter attempts, and observable
tokens separately for legacy/runtime/judge and each stage. Retrieval is a logical
operation; embedding tokens are unavailable, not zero consumption. Adapter counts
are not HTTP/billing counts; monetary cost is unavailable without billing evidence.
Pre-freeze scientific calls are zero. Static and fake checks have no live usage.

AGY staffer-mtubun94-0cf9138a completed abstract pre-freeze critique without repo
access/edits. Configured route gemini-3.8-flash-high; actual model/effort and tokens
unobserved. Retained its warning to count per-snapshot deltas rather than net
totals. Rejected suggestions for category-set equality, extra judges, hashes,
broader grammar handling, and live activation checks: they conflict with this
authorized protocol. Overhead is adapter-call count, not latency. Both arms use
the repaired verifier; normalization does not rewrite public prose. The one-pass
order is fixed by explicit tests. Its mistaken punctuation-order example does
not change the approved implementation.
