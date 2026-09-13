# GOLD-9 — Authority Binding Infrastructure Reconciliation

Decision: **GOLD-9 = COMPLETE / PASS / RELEASE_AUTHORITY_CHAIN_RECONCILED.**

Bounded evaluation-infrastructure reconciliation after the F6-A Attempt-3
preflight hold. Zero scientific/evaluation calls.

```text
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

## 1. Starting state

Starting HEAD `840336962a98518a31875f0a5e446abc53fbe3d5`
("Record F6-A attempt 3 preflight hold"); worktree clean. The Attempt-3 HOLD
(zero-outcome preflight; no preregistration, no freeze, A1–A5 NOT_REACHED)
is preserved as a historical terminal result.

## 2. Root causes confirmed

- **Freezer authority**: `candidate.py` hard-bound
  `BENCHMARK_DIR = evaluation/benchmarks/v2_6` and
  `BENCHMARK_VERSION = m6-benchmark-v2.6`; `_current_manifest` read
  `manual_adjudications.yaml` from that directory (absent in v2_9), so any
  freeze would bind v2.6 or fail.
- **Default Gold resolver**: `default_gold_dataset_path` walked a hand-written
  v2_6 → v2_2 chain and never considered v2_7/v2_8/v2_9.
- **Calibration resolver**: `load_product_language_calibration` resolved only
  v2 → v3; v4/v5/v6 existed on disk but could never be selected, and v3 is
  incompatible with the v2.9 dataset.
- **Manual-adjudication disposition**: v2.9's manifest records
  `manual_adjudications_sha256 = None` and its authority is the signed
  manifest + dataset itself; the legacy adjudication file is not part of the
  v2.9 release-critical identity. The freezer dependency was made optional
  rather than copying a v2.6 artifact forward.

## 3. Reconciliation implemented

- **Shared signed-Gold resolver** (`evaluation.py`):
  `newest_signed_exposed_gold_dir(project_root)` discovers
  `evaluation/benchmarks/v2_N` directories mechanically, qualifies them by
  manifest-internal consistency (dataset SHA match) plus
  official-ready/structurally-valid flags, and selects the highest version.
  Adding a successor benchmark requires no resolver change; there is one
  authority definition instead of independent hard-coded ones.
- **Default Gold dataset**: `default_gold_dataset_path` resolves through the
  shared resolver first and keeps the historical v2_6 → v2_2 chain only as an
  old-checkout fallback (verified by regression).
- **Candidate freezer**: `_benchmark_identity` and `_current_manifest` bind
  the resolver-selected directory (currently m6-benchmark-v2.9 /
  `eaacd3ed…`); the version-constant check is superseded by resolver
  discovery + manifest-internal consistency; `manual_adjudications.yaml` is
  optional — recorded as hash `None` with the key absent from
  `protected_file_hashes` when the active benchmark carries none (v2.9), and
  hashed as before when present (v2.6-era checkouts). `verify_candidate`
  recomputes through the same resolver, so authority drift of a historical
  candidate is detected, not hidden.
- **Calibration authority**: `newest_product_language_calibration_path`
  mechanically selects the highest `phase_b_t3_product_language_scope_vN`
  artifact (currently v6) and the loader consumes it; no silent v3 fallback.
  `_product_scope_identity` hashes the same resolved artifact, eliminating
  the v6-content/v3-hash mismatch the pre-repair dry run exposed.

## 4. Cross-layer consistency demonstration (§5.6)

```text
resolver directory            = v2_9
default_gold_dataset_path     = evaluation/benchmarks/v2_9/gold_questions.yaml
freezer benchmark identity    = m6-benchmark-v2.9 / eaacd3ed… / official
calibration                   = phase_b_t3_product_language_scope_v6
product-scope calibration     = v6 / fe56d4ca… (hash now consistent)
formal selector               = 59 IDs / e27ef67a…
ALL CONSISTENT: True
```

## 5. Focused verification

- `tests/unit/test_f6a_release_infrastructure.py`: resolver picks the newest
  qualified directory (stale v2.6 not selected while valid v2.9 exists);
  freezer identity binds m6-benchmark-v2.9; calibration identity is v6 with
  the exact artifact hash and deterministic selector hash; missing
  `manual_adjudications.yaml` recorded as `None`, not fatal; old-checkout
  fallback to the historical chain preserved; unqualified/mismatched
  directories are not resolved.
- `tests/unit/test_f6_release_identity.py`: benchmark-identity binding
  updated to the resolver-selected authority.
- Results: freezer/identity/gate suites **53 passed + 18 subtests**;
  `test_qa.py` + `test_retrieval.py` **274 passed + 52 subtests** — no
  product QA behavior touched, no new regressions.

## 6. Preserved outcomes

```text
F6-A Attempt 1 = COMPLETE / FAIL (v2.6, historical)
F6-A Attempt 2 = COMPLETE / FAIL (v2.6, historical)
F6-A Attempt 3 = HOLD / PRE_RELEASE_PRECONDITION_NOT_MET (historical terminal result of that preflight)
F6-B = LOCKED / F6_A_DID_NOT_PASS
novel_validation = PRISTINE_FOR_CURRENT_LINEAGE
```

No Attempt-3 scientific result exists yet; the next task may re-run the
Attempt-3 A0 preflight because no preregistration, freeze, or scientific
outcome was created before the HOLD.

## 7. Next action

```text
NEXT_TASK_RECOMMENDATION =
F6-A ATTEMPT 3 / RE-RUN ZERO-OUTCOME A0 PREFLIGHT, THEN PREREGISTER AND
FREEZE ONLY IF ALL PRECONDITIONS PASS
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
