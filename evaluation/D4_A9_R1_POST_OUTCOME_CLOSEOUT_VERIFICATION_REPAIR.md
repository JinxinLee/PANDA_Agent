# D4-A9-R1 — Unaccepted Pre-Freeze Attempt

D4-A9-R1 attempt: FAIL / BLOCKED / NOT_FROZEN / HOST_ACCEPTANCE_FAILED.

The delegated worker reported running its focused test suite. Tests 04-08 and 39 call verify_closeout_r1 against the real repository, which unconditionally calls run_live_audit without a synthetic replacement. The required verifier-checkpoint-before-real-data-recomputation order was therefore not preserved. No R1 scientific verdict is accepted or sealed, and no retroactive freeze is permitted. Six draft paths remain uncommitted; no R1 result JSON exists. Historical A9 authority is preserved, not superseded by an accepted R1 receipt. Production activation remains false. D4-A10 = NOT_STARTED / NOT_AUTHORIZED. User review is required before lifecycle recovery. See evaluation/D4_A9_R1_POST_OUTCOME_CLOSEOUT_VERIFICATION_REPAIR.md. STOP.

## Starting boundary

HEAD and local origin/main: `07b8cc921b4e36dc2acf2ae4ba0b27f4b3edf115`.
Message: `D4-A9 close component-sensitive model-factory validation`.
Direct parent: `2419d4f1818277656c1b3be93e423134e877657f`.
Worktree was clean before delegation. No R1 commit or push was performed.

## Lifecycle incident and test receipt limits

The worker was explicitly instructed to use synthetic/static tests only and not recompute actual frozen outcomes before the host checkpoint. It reported running `python -m pytest tests/unit/test_d4_a9_r1_post_outcome_closeout_verification_repair.py -v` with PYTHONPATH set to src and evaluation/scripts, and reported 40/40 passing in 49.99 seconds. This is a worker-reported result, not a host-verified execution transcript. Static host inspection confirms that the reported test command reaches actual raw-data recomputation through tests 04-08 and 39. Verify continues into the live audit after collecting seal errors.

The worker also returned a Level 6 claim; the host rejects it as an authoritative R1 closeout. The host attempted `run.mjs cancel staffer-mtrbmnp67` after detecting the test path, but the shared runner rejected it because only start/wait are supported. The implementation job subsequently returned. No retroactive verifier freeze was made. No host live scientific recomputation was run. Verifier/test semantics remain as delivered; only status/report wording was corrected after collection.

## Concrete unresolved defects

- Live audit hardcodes successful historical/R2/production seals and superseding receipt booleans rather than deriving them from Git checks.
- Embedding/reranker counts are inferred from slot counts. Zero-provider categories are hardcoded rather than cross-checked from raw accounting and A9 result fields.
- Plan-field, timestamp and shared-plan errors are recorded but not all propagated into failure and Level 1 precedence.
- Verify checks an allowed-path subset, not the exact seven-path set; exact two direct-child commits/messages are not enforced.
- Verify conditionally reads the working result instead of requiring the committed result; several safety/integrity fields are omitted from drift comparison.
- Grounding labels unresolved treatment objects treatment-only without symmetric current accounting. Canonical identity and required-source-type semantics need review.
- Missing source_version_id is skipped, unlike pre-existing allowed-version membership semantics.
- Persistence AST inspection reads the working executor instead of explicitly reading the executor-freeze Git object.
- Several tests assert constants or fixture contents rather than proving mutation rejection. A passing count does not establish acceptance.

Do not freeze these drafts. Further verification-semantic work under a revised lifecycle requires user review; the original chronology cannot be restored by a later commit.

## Scope and accounting

Six uncommitted paths are retained: docs/EVALUATION_STATUS.md, docs/GENERALIZATION_ROADMAP.md, this report, evaluation/d4_a9_r1_post_outcome_closeout_verification_contract.json, evaluation/scripts/d4_a9_r1_post_outcome_closeout_verification_repair.py, tests/unit/test_d4_a9_r1_post_outcome_closeout_verification_repair.py. The JSON contract is an unaccepted draft. evaluation/d4_a9_r1_result.json does not exist.

Formal cohort and treatment remain g031/g032/g033/g047 and model_factory_theory / model/PndLmdModelFactory.cxx. Both DPM symbols remain HOLD_DIRECT_TREATMENT_COVERAGE_GAP. Pflueger_2017 pages 51, 57, 65 remain HOLD_OUTSIDE_TREATMENT_SCOPE. No R1 component disposition is scientifically sealed.

R1 scientific Analyzer/Embedding/Reranker/Retrieval/QA/Verifier/Judge/Scientific-Evaluator calls, retries, tokens and DB writes: zero. The incident is deterministic recomputation before verifier freeze, not a new scientific provider run.

Authorized AGY orchestration is separate:

- staffer-mtrbmnp67: runner reported staffer / gemini-3.8-flash-high; implementation returned but failed host acceptance.
- staffer-mtrbnjlk3: independent read-only review failed with EPERM renaming state.json.tmp-3036 to state.json. No review result was accepted.
- Exact AGY provider attempts, tokens and monetary costs are unavailable; do not report them as zero.

No verifier-freeze SHA, final R1 SHA, accepted committed-result/live-audit comparison or push receipt exists. No full suite, T3, T5, reindex, production activation or D4-A10 was performed by the host.

STOP.

## Final host read-only integrity check

All eight historical A9 paths are working-tree/HEAD/base-commit Git-blob equal. All five R2 paths are working-tree/HEAD/R2-commit Git-blob equal. Raw plans retain 99891321c0d3ba3e0f54158441f2d739eca2db6f; raw results retain 4f44ac31c9fd917c1212f8d64c59974f90e4cfd6. Their original checkpoint blobs were also checked. src/ and configs/ have no cumulative working-tree difference. HEAD and local origin/main remain 07b8cc921b4e36dc2acf2ae4ba0b27f4b3edf115; the remote server was not refreshed and no push occurred. Exactly six draft paths remain. git diff --check reported no whitespace errors.

Additional rejection finding: three R2 blob constants in the unaccepted contract disagree with actual Git objects (R2 report, script, and tests). Actual preserved blobs are e5d73f0bde20076a909d72aa015f9ffdd9cd8b66, 539454dedde6f4bdd1c8a47a42260061ec3a6353, and 3f3a277a87f72422b436438db016303ff9c19a89 respectively. No historical R2 file drift occurred. The draft constants have deliberately not been repaired after the lifecycle incident.

STOP.
