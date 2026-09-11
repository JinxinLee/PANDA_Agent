# E3-A2 — Targeted Missing-Point Recovery Validation Report

Verdict: **COMPLETE / INCONCLUSIVE / INSUFFICIENT_NATURAL_MISSING_POINT_APPLICABILITY**

- Protocol: `evaluation/E3_A2_TARGETED_MISSING_POINT_RECOVERY_PROTOCOL.md`
- Frozen manifest: `evaluation/e3_a2_targeted_recovery_manifest.json`
- Raw records: `evaluation/e3_a2_targeted_recovery_raw.jsonl`
- Judged records: `evaluation/e3_a2_targeted_recovery_judged.jsonl`
- Deterministic result: `evaluation/e3_a2_targeted_recovery_result.json`
- Evaluator: `evaluation/run_e3_a2_targeted_recovery_validation.py`, `evaluation/e3_a2_cohort_selector.py`
- Tests: `tests/unit/test_e3_a2_cohort_selector.py`, `tests/unit/test_e3_a2_fork_harness.py`, `tests/unit/test_e3_a2_judge_scoring.py` (35 tests) plus the 49-test E3-A1 sentinel subset.

## Provenance

```text
candidate HEAD          = 54d548321c65169569b173d97b92731018314ce2 (Complete E3 A1 contract corrections)
preregistration commit  = 50eada9e4c62980f4437d7b2ce0850667109305c
dataset                 = evaluation/novel/v1/novel_dev.yaml @ novel-v1-dev-0.3.0 (28 questions)
selector                = mechanical (protocol §3): approved/en/answered/representative,
                          >=2 critical answer points, >=2 critical evidence groups,
                          OR-topology (evidence_topology != single_hop ∨ source_scope ==
                          cross_source ∨ repository_scope == cross_repository), dataset order
cohort IDs              = n003, n005, n006, n009, n010, n014, n019, n020, n021, n022, n024
cohort count            = 11 (within frozen 8–20 guard)
mode                    = runtime_e1_v2 (explicit selection; normal default legacy_question_core unchanged)
provider                = generation gemini-3.8-flash, judge gemini-3.8-flash,
                          embedding gemini-embedding-2 @ 3072 dims (frozen in manifest)
```

An independent pre-execution review of the preregistration found three material
defects (meter embedding-wrapper signature collision; self-referential
preregistration baseline; scorer crash on unresolved records). They were fixed
before any provider call and the preregistration was rebuilt as the single
commit `50eada9`. Note: AGY was unavailable in this environment (`agy` CLI
absent, `spawn agy ENOENT`); the §38 review gate was executed by an
independent read-only reviewer agent instead, with two review rounds
(DEFECTS FOUND → CLEARED FOR EXECUTION). AGY usage remains zero.

## Execution integrity (G1 — PASS)

- All 11 cohort cases executed and terminal (`COMPLETE`); zero infrastructure
  failures, zero missing records, zero judged failures.
- No `src/` or `configs/` change after preregistration (`git diff` empty on all
  frozen paths, worktree clean).
- `runtime_e1_v2` selected only by the evaluation harness; the product default
  remains `legacy_question_core`.
- No novel_validation or holdout content opened. Gold entered only the judge
  payload after product execution; product prompts were verified free of gold
  content by a deterministic fake test.

## Applicability (G2 — FAIL → INCONCLUSIVE)

```text
selected cases              = 11
E3-applicable cases         = 1   (n006)      [threshold >= 4]
applicability rate          = 9.1%
first-missing runtime points= 2               [threshold >= 4]
non-applicable              = 10 × no_missing_answer_points (all reached first verify)
```

Ten of eleven mechanically selected multi-part questions produced a fully
covering first semantic verification, so the E3 trigger never fired for them.
Per the frozen protocol this is not a product FAIL: natural applicability on
this cohort is insufficient to test the recovery hypothesis, no synthetic
missing points were added, and the cohort was not broadened post hoc.

## Recovery (G3 — FAIL; descriptive, n = 1 applicable case)

```text
control recovered missing points  = 0 of 2 (rate 0.0)
treatment recovered missing points= 0 of 2 (rate 0.0)
net additional recovered points   = 0
verdict counts (control)          = absent 2
verdict counts (treatment)        = partial 1, absent 1
```

Only `satisfied_supported` counts as recovery, so neither arm recovered a
point. Descriptively, on n006 the treatment arm moved point.1 from `absent`
(control) to `partial`, and the blinded judge preferred the treatment arm
(masked preference B; n006 is even → control = Arm A, treatment = Arm B):
"Arm B correctly identifies the relevant helper class PndFileNameCreator and
accurately scopes what can and cannot be confirmed from the provided evidence,
whereas Arm A abstains completely." The control final status was
`insufficient_evidence`; the treatment final status was `answered`.

## Preservation / safety (G4, G5 — PASS)

```text
treatment-only lost requested points   = 0
treatment-only degraded points         = 0
treatment-only unsupported claims      = 0 (union: runtime verifier + judge)
treatment-only contradictions          = 0
treatment-only citation/version failures = 0
```

n006 had zero already-covered runtime points at the shared first verify, so
preservation was vacuous for this cohort. The runtime verifier flagged three
claim-level support failures in the control arm and none in the treatment arm.

## Retrieval contribution (G6 — PASS; descriptive)

```text
applicable E3 attempts        = 1
atomic update                 = success
newly admitted objects        = 1
displaced selected evidence   = 1
retained support evidence     = 2
global selected evidence      = 12
treatment-only recovery cases = 0 (no case required the new-evidence check)
```

## Bounded execution (G7 — PASS)

```text
max missing_point_retrieval_count = 1
max revision_count                = 1
targeted local LLM rerank calls   = 0
global E3 rerank calls            = 1 (n006)
analyzer calls in treatment phase = 0
original plan preserved           = true
second-E3-retrieval violations    = 0
```

## Cost (observed provider usage, PANDA scientific calls only)

```text
shared first pass : 71 model calls (60 generation, 11 embedding), 630,066 returned tokens
control post-fork :  2 model calls (2 generation),               47,329 returned tokens
treatment post-fork:  4 model calls (3 generation, 1 embedding), 58,559 returned tokens
judge             :  1 model call  (1 generation),               10,639 returned tokens
total             : 78 model calls, 746,593 returned tokens
```

Tokens are the observed returned-token counter; embedding billed tokens cannot
be derived from it and are not claimed as zero. AGY workers: 0 (unavailable);
the independent reviewer agent is development delegation, excluded from PANDA
scientific counts.

## Boundaries

```text
product code changed after preregistration = no
novel_validation inspected                 = no
holdout inspected                          = no
runtime default changed                    = no
E2/C8 historical results changed           = no
T4 executed                                = no
T5 executed                                = no
runtime promoted                           = no
scientific result used for same-task repair = no
```

## Limitations

1. The decisive limitation is statistical: one applicable case and two missing
   points cannot establish or refute the recovery hypothesis. All arm-level
   contrasts above are descriptive only.
2. The judge model family equals the generation model family
   (gemini-3.8-flash); correlated semantic bias is possible and unmeasured.
3. Natural E3 applicability on mechanically selected representative multi-part
   novel_dev questions is rare (9.1%) because the first semantic verification
   usually covers all runtime points; any future E3 validation design must
   either widen the cohort substantially or re-derive a cohort selector that
   targets first-verify coverage failure — either requires new authorization
   and cannot reuse this frozen cohort.
4. The paired judge received cited-evidence text but not the runtime
   verifier's internal reasoning; judge and verifier observations were kept
   separate and merged only at the G5 union, per protocol.

## Lifecycle outcome

```text
E3-A2 = COMPLETE / INCONCLUSIVE / INSUFFICIENT_NATURAL_MISSING_POINT_APPLICABILITY
E3    = IN_PROGRESS / A2_COMPLETE_INCONCLUSIVE / PENDING_FUTURE_LIFECYCLE_DECISION
normal default = legacy_question_core (unchanged)
runtime_e1_v2  = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY (unchanged)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
