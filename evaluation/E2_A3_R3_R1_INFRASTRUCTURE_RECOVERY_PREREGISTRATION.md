# E2-A3-R3-R1: Infrastructure Recovery Preregistration

## Authorization and identities

Starting HEAD: `29bc2864a95b797ecfc07d3824711c5dc855ff95`.
Product candidate: `fd0aed4c7e491a569bf39271825cc0950630863d`.
Original R3 protocol: `0a276a40968ed67fb784c37676d172314fb1210d`.
Original raw: `6d760be1eae1e803d8f6c4ff6b374a13dbed4713`.
Original judged: `77388ec9c2564cce82d0db24ef97a15da62d4779`.
Original result: the starting HEAD above; historically INCONCLUSIVE.

The user authorizes this supplemental six-QA/three-judge recovery, original-gate
fourteen-pair composition, scientific result commit and PASS-only selector
activation. No additional approval checkpoint. No product repair, changed
provider settings, scientific replay or historical artifact rewrite is allowed.

The recovery protocol commit contains only this protocol, manifest, runner,
readiness artifact, focused tests and report draft. Its full SHA is passed as
`--protocol` and persisted in all new evidence. No scientific/provider call
precedes this commit, including abstract AGY review. Optional AGY review after
freeze receives only an abstract authority/composition question, no repository
evidence, case content, outcomes or file access. It cannot edit frozen decisions.

## Infrastructure-only selection and full-pair replacement

Reconstruct original R3 exclusively from the committed manifest/raw/judged/result.
Exactly four preserved failures explain the incomplete set: g059 legacy/runtime
and g047 runtime ConnectionTimeout; g001 legacy provider 429 RESOURCE_EXHAUSTED.
No valid prior paired judgment exists for any of these three cases. Do not select
by quality, coverage, status, difficulty or previous preference.

Recover exactly g059, g047, g001 using a fresh pair for each. Old successful
g047 legacy and g001 runtime remain historical but cannot enter the new pair.
Preserve original global indices, not recovery-list indices:

| Case | Original index | Fresh execution order | A | B |
| --- | --- | --- | --- | --- |
| g059 | 0 | legacy, runtime | legacy | runtime |
| g047 | 1 | runtime, legacy | runtime | legacy |
| g001 | 3 | runtime, legacy | runtime | legacy |

Reuse exactly the original eleven full pairs and judgments: g028, g105, g113,
g014, g060, g050, g029, g057, g041, g007, g108. Do not run or rejudge any of them.
Final order is the original fourteen-case manifest order. For each recovered
case use ONLY its fresh pair/judgment, even if recovery fails. Never fall back
to an old successful partial arm. Each result pair records authority_source,
raw_commit, judged_commit and execution IDs. Composition is deterministic and
does not copy or rewrite historical artifacts.

## Same product and provider

Before verdict, src/configs/prompts/schemas/corpus/index/data match the R2 product
exactly and normal default remains legacy_question_core. The normalizer,
Sphinx admission, E1/E2 semantics, compatibility and public DTO/API are unchanged.
Exact provider settings equal the original manifest: generation and judge
gemini-3.8-flash, embedding gemini-embedding-2/3072, global, timeout 120000 ms;
judge temperature zero. Production sampling and existing adapter retry policy
remain unchanged. One scientific execution per arm; configured adapter attempts
are measured separately and do not authorize case replay.

## Readiness and freeze

R-F1 product identity; R-F2 old protocol/raw/judged/result unchanged; R-F3 exact
recovery set; R-F4 genuine infrastructure incompleteness; R-F5 eleven complete
original pairs; R-F6 identical provider; R-F7 original gates and judge unchanged;
R-F8 default legacy; R-F9 focused tests pass; R-F10 protected/holdout access zero;
R-F11 all scientific/provider calls before recovery protocol freeze zero.
All eleven are required before live calls. Product drift blocks execution.

Freeze product/config/prompt/schema/corpus/index, tests, recovery runner and
imported helpers, manifest/readiness/protocol, original evidence, original gates,
case IDs, A/B mapping and combination policy after protocol commit. No changing
threshold, model, timeout, cohort or semantics in response to outcomes.

## Persistence and judging

Persist STARTED before each of the six fresh executions. Use a fresh normal
agent/retrieval for each arm; capture original index/order/question/expected
status, public result, evidence/citations, retrieval diagnostics, all reviews,
revision count, runtime decomposition/coverage, model usage, timings and errors.
Evaluator-only answer/revision hooks copy selected evidence before generation,
preserving citation context even on provider failure without changing public DTO
or product behavior. A terminal failure is preserved and never replayed. An
ambiguous STARTED record must not be replayed. Existing terminal records are
skipped; never-started records may continue within the frozen order.

Commit all six terminal raw attempts before any recovery judge. For each complete
fresh pair, call the unchanged original R3 judge once (maximum three calls).
Incomplete pairs get explicit unscoreable judgment records without a model call.
Input uses original-index A/B mapping and only question, approved expected status/
Gold obligations, public answer/claims and their cited evidence. Never expose
modes, old outcomes, infrastructure/recovery history, decomposition/audit or the
remaining worse allowance. Strict original schema: preferred A/B/equivalent,
critical_regression, A_supported, B_supported, nonempty reason; no extra fields,
no critical equivalent. No unfavorable-result rejudge.

Commit all three judgment records before unblinding/scoring. Do not inspect live
scientific outcomes while the batch runs. Preserve failures without repairing
or rerunning. The original eleven and new three are combined only after this
judgment freeze.

## Explicit original gate authority

Each gate emits state PASS/FAIL/NOT_EVALUABLE plus authority_complete and
observed_violation. A known violation is FAIL even when another pair is missing;
absence of a known violation without required evidence is NOT_EVALUABLE.
Original thresholds/definitions are copied unchanged from the R3 manifest.

| Gate | PASS authority and requirement |
| --- | --- |
| G1 | 14 complete legacy, 14 runtime, 14 authoritative pair judgments |
| G2 | All 14 paired statuses available; runtime_correct >= legacy_correct |
| G3 | All expected nonanswered pair statuses available; no new runtime false answer |
| G4 | All expected answered pair statuses available; no new runtime false refusal |
| G5 | All paired outputs/reviews available; per-pair runtime-minus-legacy critical category empty |
| G6 | Complete selected-evidence/admission/raw answer/revision/review context for every execution; zero invalid Sphinx public edges, incomplete-web errors or admission mismatches |
| G7 | 14 runtime outputs with exactly one valid 1..5 sequential nonempty point.N decomposition; expected-and-final answered coverage evaluable/complete with no unknown-point/structural errors |
| G8 | Complete QA traces/usage; legacy decomposition zero, runtime revision <=1, post-verify retrieval zero |
| G9 | 14 authoritative judgments; every runtime output supported |
| G10 | 14 authoritative judgments; critical runtime regressions zero |
| G11 | 14 authoritative judgments; worse <=1 and better+equivalent >=13 |
| G12 | All 14 complete paired QA call counts; sum(runtime-legacy generation adapter calls)/14 <=2.0, excluding embedding/retrieval |
| G13 | All readiness invariants including exact unchanged product/default/compatibility |

G5 retains original registered categories: wrong_version, unknown_evidence,
incomplete_citation, unsupported_identifier, structural_review, unknown_answer_point.
Every review counts, not only the final one. Correct refusals retain the original
coverage exception. G9 rejects unsupported equivalent outputs. G11 already has
one original noncritical worse among 1 better/9 equivalent/1 worse; therefore
any recovery worse fails the unchanged final threshold. Historical R1 P6 FAIL
has no waiver. No human override of unfavorable frozen gates.

Independent failures include an observed invalid citation (also in partial
failure context), new paired status/integrity failure, completed-runtime coverage
failure, runtime boundary violation, unsupported judged runtime, critical runtime
regression, second noncritical worse, and complete-authority overhead >2.0.
Unknown accepted point IDs, internal claims receiving public coverage credit,
public DTO violations and product-contract violations are zero-tolerance.

Verdict precedence: independently established product/zero-tolerance failure ->
FAIL; otherwise missing fourteen-pair/gate authority -> INCONCLUSIVE; otherwise
all G1-G13 PASS -> PASS. No missing judge can turn a known product failure into
INCONCLUSIVE. No complete-case denominator substitutes for fourteen in G12;
return unavailable if complete paired call counts do not exist.

## Usage, commits, activation and stop

Report original R3 historical usage (including failed work), original failed
attempt expenditure, superseded partial-pair expenditure, and new recovery
legacy/runtime/judge usage separately. The scientific G12 quantity uses only
eleven original complete pairs plus three fresh recovery pairs. Never include
old failed attempts or superseded partial arms in its denominator. Embedding
tokens and monetary cost are unavailable, not zero. Scientific/provider calls
before recovery protocol freeze are zero.

Commit chain: recovery protocol -> recovery raw -> recovery judgments -> combined
scientific result/report/lifecycle -> PASS only selector activation. No squash
or amend across boundaries. Historical R3 stays INCONCLUSIVE, A3/R1 stay FAIL,
R2 stays PASS. No original artifact is edited or original pair rejudged.

Only committed combined PASS permits DEFAULT_ANSWER_POINT_MODE changing from
legacy_question_core to runtime_e1_v2. That is the sole product-semantic change;
focused test expectations and lifecycle documents may accompany it. Static/fake
checks must establish run/run_detailed default runtime, exactly one decomposition,
point.N contract, internal diagnostics, explicit legacy and shadow availability,
<=1 revision, no missing-point retrieval, active citation/colon repairs,
compatibility and public DTO preservation. No live calls after activation.
If any other semantic change is needed, stop instead of adding a repair.

PASS activation closes E2 and recommends E3 without authorizing it. FAIL keeps
legacy with ACTIVATION_COMPLETION_FAILED; missing evidence keeps legacy with
ACTIVATION_COMPLETION_INCONCLUSIVE. No automatic recovery, E3/T3/T5/D4/F2/F3 or
legacy-requirement retirement. STOP after this task's closeout.
