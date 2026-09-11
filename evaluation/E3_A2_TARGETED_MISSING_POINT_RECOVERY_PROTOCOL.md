# E3-A2 — Targeted Missing-Point Recovery Validation Protocol

Status: PREREGISTERED (frozen before any scientific provider call).
Tier: T2 targeted mechanism validation. No T3/T4/T5, no full benchmark, no
novel_validation, no protected holdout.

This protocol freezes the complete scientific contract for E3-A2 before the
first provider call. The frozen manifest is
`evaluation/e3_a2_targeted_recovery_manifest.json`; the evaluator is
`evaluation/run_e3_a2_targeted_recovery_validation.py` plus
`evaluation/e3_a2_cohort_selector.py`; deterministic tests are
`tests/unit/test_e3_a2_cohort_selector.py`, `tests/unit/test_e3_a2_fork_harness.py`,
and `tests/unit/test_e3_a2_judge_scoring.py`.

## 1. Candidate identity

```text
candidate HEAD   = 54d548321c65169569b173d97b92731018314ce2
candidate subject = Complete E3 A1 contract corrections
normal default   = legacy_question_core (unchanged; runtime_e1_v2 is
                   explicitly selected for this experiment only)
```

The product is frozen for the duration of A2. `src/` and `configs/` must not
change after this protocol is committed. If scientific execution exposes a
genuine product defect, it is recorded and classified, not repaired inside A2.

## 2. Dataset identity

```text
dataset       = evaluation/novel/v1/novel_dev.yaml
curation      = evaluation/novel/v1/curation_metadata.yaml
benchmark_version = novel-v1-dev-0.3.0
question count    = 28 (expected_status: answered 27, insufficient_evidence 1)
```

`novel_dev` is exposed development evaluation data, authorized for this T2
task. Case-level `novel_validation` and holdout content is never opened.

## 3. Mechanical cohort selector

A `novel_dev` case is selected iff all of the following hold, using the actual
schema fields (selection order = dataset question order):

```text
review_status == approved
language == en
expected_status == answered
curation_metadata.representativeness.class == representative
len([p in required_answer_points if p.critical]) >= 2
len([g in required_evidence_groups if g.critical]) >= 2
AND at least one of:
    coverage.evidence_topology != single_hop
    coverage.source_scope == cross_source
    coverage.repository_scope == cross_repository
```

Scope guard: `8 <= selected <= 20`; otherwise A2 is
`BLOCKED / COHORT_SELECTOR_SCOPE_REVIEW_REQUIRED` before any provider call.
The selector is frozen and must not be tuned after outputs are observed. No
PANDA outcome was inspected before freezing the cohort.

Frozen cohort (11 cases):

```text
n003, n005, n006, n009, n010, n014, n019, n020, n021, n022, n024
```

## 4. Checkpoint / fork semantics (evaluation-only harness)

For each selected question, the harness reproduces the production
`runtime_e1_v2` path up to and including the first production `_verify` node:

```text
decomposition (product QuestionDecomposer)
→ retrieve (capture_candidates, runtime path)
→ sufficiency
→ configured pre-answer targeted retrieval loop (unchanged product routing)
→ answer
→ FIRST VERIFY
→ freeze/deepcopy the exact post-first-verify state (fork checkpoint)
```

Implementation: `build_first_pass_graph` wires the unmodified `QAAgent` node
functions with the production sufficiency routing expression (copied verbatim
from `qa.py`) and a terminal edge after `verify`. E3 cannot execute inside the
shared first pass. The harness never re-implements substantive retrieval or
verification logic; parity with the production path is locked by
`test_first_verify_state_matches_production_path`,
`test_treatment_arm_matches_production_end_to_end`, and
`test_first_pass_respects_pre_answer_targeted_retrieval_loop` under
deterministic fakes.

Both arms are invoked on independent `deepcopy` checkpoints of the same state.
After the fork there is no cross-arm state reuse; execution is sequential and
independent.

## 5. Natural E3 applicability

A case is E3-applicable iff the shared first-verify state satisfies the
current product trigger contract (`QAAgent._check_e3_trigger`, used
read-only):

```text
answer_point_coverage_mode == runtime_e1_v2
revision_count == 0 and missing_point_retrieval_count == 0
no version conflicts
coverage review structurally valid and coverage_evaluable == true
missing_answer_point_ids non-empty and all valid runtime point IDs
```

Missing points are never created artificially; claims or evidence are never
dropped; Gold never triggers E3. Non-applicable cases are recorded with
`applicable = false`, the product trigger reason, and the first coverage
state; they remain in the applicability denominator and receive no treatment
and no judge.

## 6. Arms

CONTROL (pre-E3 behavior):

```text
same first-verify checkpoint
→ NO missing-point retrieval
→ one bounded revision using existing selected evidence (product `_revise`)
→ second verify (product `_verify`)
→ finalize (product `_finalize`)
```

TREATMENT (current E3):

```text
same first-verify checkpoint (independent deepcopy)
→ current E3 missing-point targeted retrieval (`_missing_point_retrieve`)
→ current global candidate reconsideration + retained-support behavior
→ one bounded revision
→ second verify
→ finalize
```

Bounds (unchanged product semantics): `missing_point_retrieval_count <= 1`,
`revision_count <= 1`. Continuation routing after verify is the unmodified
product `_after_verify_route`; the state counters make a second E3 retrieval
unreachable.

Product-input leakage boundary: during both arms the product receives only the
question and current runtime state. Gold required answer points, evidence
groups, expected answers, source paths/symbols, curation rationale, judge
outputs, and arm-comparison metrics never enter product execution. The E3
retrieval objective remains original question + runtime missing answer-point
texts.

## 7. Blinded paired judge

One independent blinded judge per E3-applicable pair; non-applicable cases are
never judged. Judge model: `evaluation_judge_model` from the frozen provider
identity, called via the evaluation judge client with `temperature=0`.

Judge input (per pair): original question; Gold expected status; Gold required
answer-point texts (evaluation reference only); shared first-verify missing and
already-covered runtime answer point IDs/texts; masked Arm A final
(status, claims, cited evidence); masked Arm B final (status, claims, cited
evidence). The judge never receives the E3 trace, treatment/control labels,
retrieval counts, or implementation details.

Masking rule (deterministic, transparent, recorded outside the judge prompt):

```text
odd  numeric question id → treatment = Arm A, control = Arm B
even numeric question id → control   = Arm A, treatment = Arm B
```

Judge output schema (frozen; `Judgment` in the evaluator; schema also frozen
in the manifest):

```text
per arm:
  missing_point_outcomes:  [{point_id, verdict ∈ satisfied_supported|partial|
                             absent|unsupported, reason}]  (exactly the missing set)
  preserved_point_outcomes:[{point_id, verdict ∈ preserved_supported|degraded|
                             lost_or_unsupported, reason}]  (exactly the covered set)
  unsupported_claim_ids:   [claim ids from that arm only]
  contradiction_present:   bool
  wrong_version_or_citation_concern: bool
overall_preference ∈ {A, B, equivalent}
reason: str
```

Only `satisfied_supported` counts as scientific recovery; `partial` does not.
The runtime coverage-review output is never treated as scientific ground
truth. The judge model family equals the generation model family in the frozen
provider identity; this correlated semantic bias is recorded as a limitation.

## 8. Metrics

Applicability: selected cohort count; E3-applicable count and rate; total
first-missing runtime points; missing points per applicable case.

Recovery (per missing point, judge-rated): control/treatment recovered counts
and rates; net additional recovered points; full `partial/absent/unsupported`
verdict counts.

Preservation (points covered at first verify): per-arm `preserved_supported`
counts; treatment-only degradation count; treatment-only
`lost_or_unsupported` count.

Retrieval (per applicable treatment case): targeted candidate count; newly
admitted object IDs/count; displaced selected evidence IDs/count; retained
support evidence IDs/count; atomic update status (`success|no_gain|failure`);
global selected evidence count; whether treatment-only recovery co-occurs with
at least one newly admitted E3 evidence object.

Safety: treatment-only unsupported claims, contradictions, and
wrong-version/citation-integrity failures, using the union of runtime verifier
observations and blinded judge findings without double-counting claim-level
events. Runtime and judge observations are reported separately in the raw
records.

Cost: actual observed usage per phase (shared first pass, control post-fork,
treatment post-fork, judge): model calls, generation calls, embedding calls,
returned-token counter, retrieval logical calls, reranker calls, revision
calls, review calls, judge calls. Tokens are the observed returned-token
counter; embedding billed tokens are not claimed as zero. No monetary
estimate.

## 9. Pre-registered verdict gates

G1 — protocol/execution integrity: PASS requires the exact frozen cohort IDs
used; no product/protocol edit after preregistration (`git diff` on frozen
paths is empty); every planned case terminal or validly resumable (an
unresolved provider/infrastructure failure that prevents complete required
authority makes A2 INCONCLUSIVE, not FAIL); no novel_validation/holdout
access; no Gold leakage into product execution.

G2 — natural applicability: requires `E3-applicable cases >= 4` AND
`total first-missing runtime points >= 4`. If either is below threshold:
`E3-A2 = COMPLETE / INCONCLUSIVE / INSUFFICIENT_NATURAL_MISSING_POINT_APPLICABILITY`.
Not a product FAIL; no synthetic cases and no post-hoc cohort broadening.

G3 — missing-point recovery benefit (among judged applicable cases): PASS
requires `treatment recovery rate >= 50%` AND
`treatment recovered >= control recovered + 2` (point-level, judge-rated
`satisfied_supported` only).

G4 — no requested-content regression: for runtime points already covered at
the shared first verify and `preserved_supported` in control, treatment-only
`lost_or_unsupported` must be 0. Material `degraded` cases are reported
separately.

G5 — no new unsupported-answer regression: treatment-only unsupported claims,
contradictions, and wrong-version/citation-integrity failures must all be 0
(union of runtime verifier + blinded judge findings, claim-level dedup).

G6 — retrieval contribution consistency: for every case where treatment
recovers a missing point that control does not, the treatment case must have
`>= 1` newly admitted E3 evidence object. G6 fails only if ALL treatment-only
recovery cases lack newly admitted evidence; partial attribution is flagged,
not assumed.

G7 — bounded E3 execution integrity: across every applicable treatment case:
`missing_point_retrieval_count <= 1`; `revision_count <= 1`; targeted local
LLM rerank = 0; successful E3 global rerank <= 1; no second E3 retrieval after
the second verify; no question re-analysis solely for E3 (no analyzer-stage
calls in the treatment phase); original plan/version constraints preserved.

Overall verdict:

```text
infrastructure-only G1 gap            → INCONCLUSIVE
G2 insufficient natural applicability → INCONCLUSIVE
otherwise                             → PASS iff G3+G4+G5+G6+G7 all PASS
                                        otherwise FAIL
```

No additional gates may be invented after outcomes are observed.

## 10. Execution, resume, and stop rules

Artifacts (append-only until final):

```text
evaluation/e3_a2_targeted_recovery_raw.jsonl      one atomic record per attempt
evaluation/e3_a2_targeted_recovery_judged.jsonl   one record per judged pair
evaluation/e3_a2_targeted_recovery_result.json    deterministic scoring output
evaluation/E3_A2_TARGETED_MISSING_POINT_RECOVERY_VALIDATION.md  report
```

Resume: completed compatible records are reused; only missing/failed cases are
re-executed; completed records are never overwritten; infrastructure failures
are not scientific failures and are retried by re-running `execute`/`judge`.
Scoring requires zero new model calls and zero new embedding calls and is
recomputable offline from the frozen manifest, raw records, judged records, and
this protocol.

Stop rules: after any A2 scientific outcome is observed, product code,
prompts, schemas, retrieval policy, judge schema, cohort, thresholds, and
scoring semantics must not be modified to improve A2. FAIL → record and stop.
INCONCLUSIVE → record why and stop. Any later product repair requires a
separately authorized task.

## 11. Interpretation boundary

A2 PASS establishes only: on the frozen targeted exposed novel_dev T2 cohort,
naturally occurring semantic missing points were recovered more often with E3
than with the same-checkpoint existing-evidence-only revision control, within
the frozen safety and bounded-execution criteria. It does not establish
production readiness, representative full generalization, T4/T5 success,
default runtime promotion, release acceptance, or C8 historical treatment
success.
