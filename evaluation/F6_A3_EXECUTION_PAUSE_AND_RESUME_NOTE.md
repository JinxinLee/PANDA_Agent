# F6-A Attempt 3 — Execution Pause and Resume Note

Purpose: persist the exact mid-execution state of the continuous Attempt-3
run so it can be resumed later without re-deriving anything. This note is the
resume anchor; the authorized execution itself follows the Attempt-3 prompt
("F6-A ATTEMPT 3 — CONTINUOUS PRE-RELEASE VALIDATION & GENERALIZATION GATE")
and the committed preregistration.

Pause point: after A1 primary execution completed its main loop; before the
A1 receipt, gate evaluation, and the 429-recovery rerun.

```text
PANDA scientific/evaluation calls so far = consumed by A1 (see §4); A0/preregistration/freeze = 0
novel_validation = PRISTINE_FOR_CURRENT_LINEAGE (A4 not reached)
holdout access = 0; F6-B execution = 0
```

## 1. Immutable identity chain

| item | value |
| ---- | ----- |
| Attempt-3 starting HEAD | `1f03bbdc9da72af0bf90fe0cd15d5c061bffd567` (GOLD-9) |
| product-behavior lineage HEAD | `d323f790655c62e18b782d606a02f593a673f3cd` |
| preregistration commit | `2f9a4a3` "Preregister F6-A attempt 3" |
| preregistration artifacts | `evaluation/F6_A3_PRERELEASE_VALIDATION_PREREGISTRATION.md` + `.json` (immutable) |
| preregistration JSON SHA-256 | `6ef37ca8d248eacb…` (full hash in `evaluation/f6_a3_freeze_receipt.json`) |
| freeze commit | `11de2bd` "Freeze F6-A attempt 3 candidate" |
| candidate ID | `f6a-rc3-20260914` |
| candidate manifest SHA-256 | `be2101a4709aa2ab2f324ba00b58d90e561ff1e359fc44b28ab26a5b3be155ca` |
| freeze receipt | `evaluation/f6_a3_freeze_receipt.json` |
| implementation_git_commit (frozen) | `2f9a4a32a41330326976bce4cf29e726ceac908e` |
| verify-candidate at freeze | `valid = true, mismatches = []` |
| Gold authority | m6-benchmark-v2.9 / `eaacd3ed…` / v2_9 directory |
| calibration | phase_b_t3_product_language_scope_v6 (`fe56d4ca…`) |
| selector | 59 IDs / `e27ef67a…` (derived, `data/_a3_gold_args.txt` holds the run args) |
| models | generation/verification-effective/judge = gemini-3.8-flash; embedding = gemini-embedding-2; prompts 3.10.1 / `23d73b03…` |
| A1 run ID | `f6a-rc3-gold-formal-full-20260914` |
| A1 run directory | `data/evaluation/runs/f6a-rc3-gold-formal-full-20260914/` |

## 2. A1 state at pause

- Main loop finished normally (exit 0; `run_status.json` = complete):
  **59 records written; 56 successful; 3 incomplete**
  (`g006`, `g013`, `g016` — all `429 RESOURCE_EXHAUSTED` on structured
  generation; exception records preserved with their usage already counted).
- `results.jsonl` last write 02:50:29; no process running.
- A1 receipt: **NOT YET CREATED**.
- Gate matrix: **NOT YET COMPUTED**.

## 3. Known issue for the resumer — resume skips 429 records

`python -m panda_agent.cli.evaluate resume --run-id
f6a-rc3-gold-formal-full-20260914` was already tried once: it exited 0 but
did **not** retry the three 429 cases. Cause located:
`EvaluationRunStore.completed_ids` counts exception-carrying records as
completed, and the run loop skips `case.id in store.completed_ids`
(`evaluation_runner.py` around the `resume` handling). Do not assume resume
will retry them on its own.

Two permitted recovery paths (choose one, document which):

- **Path R-A (Attempt-2 precedent, recommended)**: back up
  `results.jsonl` (e.g. `results.jsonl.pre-retry-backup`), delete exactly the
  three exception records for `g006/g013/g016`, then run
  `PYTHONPATH=src python -m panda_agent.cli.evaluate resume --run-id f6a-rc3-gold-formal-full-20260914`
  — the three cases leave `completed_ids` and are retried under the identical
  frozen identity. Keep the backup; count both attempts' usage.
- **Path R-B**: re-run the full command (all 59 `--case-id`s from
  `data/_a3_gold_args.txt`) only if resume semantics have meanwhile changed —
  not preferred because successful cases must not be rerun.

Recovery contract (from the preregistration): same candidate, same
preregistration, same run ID, no behavior change; failed-attempt usage is
counted; retry only genuinely incomplete cases.

## 4. Resume checklist (execute in order)

1. `git rev-parse HEAD` — expect `11de2bd` or later lifecycle commits;
   `git status --short` — expect only the known untracked `data/` scratch
   files (`_a3_gold_args.txt`, `_a3_gold_run.log`, `_a3_resume.log`).
2. `PYTHONPATH=src python -m panda_agent.cli.evaluate verify-candidate
   --candidate-id f6a-rc3-20260914` — require `valid = true,
   mismatches = []`. If invalid → STOP, HOLD (identity drift).
3. Confirm Docker (`postgres:17-alpine`, `qdrant:v1.15.5` healthy) and index
   fingerprint `8172f9a6…` unchanged.
4. Execute Path R-A from §3; verify 59/59 records all carry non-null
   `result`; confirm `executed_case_ids == formal_product_scope_ids`
   (no missing/extra/duplicates).
5. Compute A1 usage (sum `model_calls`/`token_usage` over all records
   including the preserved 429 attempts; role breakdown: runtime generation /
   verification / composer / embedding — judge per `model_call_breakdown`;
   sub-roles not separable → `NOT_SEPARATELY_RECOVERABLE_FROM_STORED_RECORDS`).
6. **Immediately**, before case-level diagnosis, create the immutable A1
   receipt binding: run ID, candidate ID, candidate manifest SHA
   (`be2101a4…`), record count, case-ID-set hash, `results.jsonl` hash,
   `gate_matrix.json` hash, traces hash, usage summary.
7. Gate matrix:
   `PYTHONPATH=src python evaluation/scripts/f6a_gate_evaluation.py --run-id
   f6a-rc3-gold-formal-full-20260914 --prereg
   evaluation/f6_a3_prerelease_validation_preregistration.json --output
   data/evaluation/runs/f6a-rc3-gold-formal-full-20260914/gate_matrix.json`
   (preregistered thresholds are already inside the preregistration JSON).
8. Gate decision per the preregistered mandatory set. Any FAIL → terminal
   `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED` → stop
   scientific execution (A2–A5 NOT_REACHED), keep
   `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`.
9. If all mandatory gates PASS → continue the authorized chain exactly as the
   Attempt-3 prompt prescribes:
   - A2 ablation `disable_query_expansion_injection`, run ID
     `f6a-rc3-gold-formal-ablation-20260914`, same cohort + frozen candidate;
     before running, confirm the current ablation invocation path in
     `src/panda_agent/f6a_ablation.py` / runner integration (not yet used in
     any attempt — inspect before first use).
     Gate: primary − ablation release score ≤ 0.05; stage receipt
     immediately after.
   - A3 novel_dev `f6a-rc3-novel-dev-full-20260914` (exposed diagnostic;
     only preregistered hard-stop rules apply); stage receipt.
   - A4 novel_validation `f6a-rc3-novel-validation-full-20260914` — verify
     `PRISTINE_FOR_CURRENT_LINEAGE` immediately before; first model outcome
     ⇒ `EXPOSED_FOR_CURRENT_LINEAGE` (record transition); Generalization Gap
     = formal Gold release score − novel_validation representative release
     score ≤ 0.10; stage receipt.
   - A5 composer audit `f6a-rc3-composer-audit-20260914` over frozen ANSWERED
     records; `composer_new_fact_rate == 0`; pairs ≥ 10 and composed
     preferred > deterministic preferred (else INCONCLUSIVE semantics); stage
     receipt.
10. Terminal artifacts: `evaluation/F6_A3_PRERELEASE_VALIDATION_RESULT.md` +
    `.json` (update the existing HOLD result file's role — the HOLD remains
    historical; this execution's terminal verdict is the current one), docs
    (`EVALUATION_STATUS.md`, `GENERALIZATION_ROADMAP.md`), then Commit C
    `Record F6-A attempt 3 result`. Do not push; do not touch holdout/F6-B.

## 5. Hard prohibitions (unchanged)

No product/Gold/calibration/prompt/threshold/evaluator/model changes after
freeze; no pass chasing; no case-specific behavior; FAIL is legitimate;
`novel_validation` exposure rules as preregistered; holdout access = 0 even
on PASS; F6-B requires separate authorization; no push.

## 6. Scratch files (not committed)

`data/_a3_gold_args.txt` (59 `--case-id` arguments),
`data/_a3_gold_run.log`, `data/_a3_resume.log` — regenerable; safe to delete
after successful resume.
