# F6-A Attempt 3 — Prerelease Validation & Generalization Gate (Result)

Decision: **F6-A Attempt 3 = HOLD / PRE_RELEASE_PRECONDITION_NOT_MET.**

Zero-outcome preflight hold: scientific/evaluation execution was never
started.

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## 1. Starting state and lineage verification

- Starting HEAD `52713da2092579c3697a56d6bee9d5b1e7baf2fa`
  ("Record FR2-R1 development closeout"); worktree clean.
- Product-behavior lineage HEAD `d323f790655c62e18b782d606a02f593a673f3cd`
  ("Repair FR2 source obligation boundaries") verified:
  `git diff d323f79..HEAD` touches only lifecycle docs and FR2-R1 artifacts —
  **zero product-behavior drift** after the accepted development HEAD.
- Product boundary audit clean: no `source_obligation_*` synthetic claims in
  product code (the FR2-R1 corrected requirement mechanism carries no
  synthesized public claims), no Gold case IDs, no benchmark paths as product
  logic, no metric-specific postprocessing, no fixed locators for deferred
  clusters. Production answer-point mode confirmed `legacy_question_core`
  (default `DEFAULT_ANSWER_POINT_MODE`).

## 2. Authority verification (passed items)

- Gold v2.9: `evaluation/benchmarks/v2_9/gold_questions.yaml`,
  `dataset_sha256 = eaacd3ed6595821b24b28823c6344abc4dfb954eb71846e682080b42c2f689be`
  (match), manifest status `approved_exposed_development_benchmark_v2_9`,
  `official_ready = true`, `structurally_valid = true`.
- Selector derivation against v2.9 + v6: **59 IDs**,
  `sha256 = e27ef67a866274b4a8441b789ca78fc3ccb7e022eed537c7442e15230777a0e5`
  (re-derived, not assumed).
- Docker runtime: `postgres:17-alpine` + `qdrant:v1.15.5` (running, healthy);
  index fingerprint `8172f9a6…` (match).
- Focused non-scientific tests: 325 passed + 70 subtests (FR2-R1 boundary,
  Cluster-D restatement discipline, F2-A3-R1/F2-A5, FR1 regressions, freezer
  identity, gate helper, full test_qa/test_retrieval).

## 3. Preregistration blockers (why HOLD)

### Blocker 1 — candidate freezer still binds Gold v2.6

`src/panda_agent/candidate.py` hard-codes:

```python
BENCHMARK_DIR = Path("evaluation") / "benchmarks" / "v2_6"
BENCHMARK_VERSION = "m6-benchmark-v2.6"
```

`_current_manifest` reads `gold_questions.yaml` and
`manual_adjudications.yaml` from that directory, so any frozen candidate
would bind **Gold v2.6** identities and would additionally fail on the
missing `manual_adjudications.yaml` in `evaluation/benchmarks/v2_9/`. This
directly conflicts with the Attempt-3 requirement that the frozen candidate
bind Gold v2.9 (`eaacd3ed…`) as the scientific authority. No override
parameter or environment binding exists.

### Blocker 2 — calibration loader does not reach v6

`load_product_language_calibration(...)` resolves its successor chain only
through `phase_b_t3_product_language_scope_v3.json`; v4/v5/v6 exist on disk
but the default-loaded calibration is **v3**, which is incompatible with the
v2.9 dataset (`calibration_compatibility → False`). The candidate freezer's
product-scope identity would raise
"product-language calibration incompatible with active Gold", and the
evaluation pipeline cannot select the authoritative v6 calibration.

Both blockers are evaluation-infrastructure authority-binding gaps left by
the GR1 governance chain (the Gold authority was advanced to v2.9 without
updating the freezer binding and the calibration loader successor chain).

## 4. Disposition

Per the Attempt-3 protocol, A0 is validation, not development: product files
(including the candidate freezer in `src/panda_agent/**`) may not change
during Attempt 3, and no Gold/calibration files may be modified. Correcting
the blockers requires a separate, explicitly authorized
benchmark-governance/infrastructure task. No repair was performed; no
preregistration was created; no candidate was frozen.

## 5. Stage status

```text
A0 preflight            = HOLD (preregistration blockers, zero scientific calls)
preregistration         = NOT_CREATED
candidate freeze        = NOT_CREATED
A1 formal Gold          = NOT_REACHED
A2 Gold ablation        = NOT_REACHED
A3 novel_dev            = NOT_REACHED
A4 novel_validation     = NOT_REACHED (PRISTINE_FOR_CURRENT_LINEAGE)
A5 composer audit       = NOT_REACHED
```

## 6. Integrity

```text
novel_validation = PRISTINE_FOR_CURRENT_LINEAGE
holdout access = 0
protected-content leakage = 0
F6-B execution = 0
Gold changes = 0; calibration changes = 0; product changes = 0
```

## 7. Lifecycle

```text
F6-A Attempt 3 = HOLD / PRE_RELEASE_PRECONDITION_NOT_MET
F6-A Attempt 1 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (v2.6, historical)
F6-A Attempt 2 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (v2.6, historical)
F6-B = LOCKED / F6_A_DID_NOT_PASS
Phase F = IN_PROGRESS / F6_A_ATTEMPT_3_HOLD
```

## 8. Next action

```text
NEXT_TASK_RECOMMENDATION =
GOLD-9 AUTHORITY BINDING INFRASTRUCTURE RECONCILIATION /
(update candidate-freezer benchmark binding to m6-benchmark-v2.9 including
the manual-adjudications disposition, and extend the calibration loader
successor chain to phase_b_t3_product_language_scope_v6 — then re-run
F6-A Attempt 3 preflight)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
