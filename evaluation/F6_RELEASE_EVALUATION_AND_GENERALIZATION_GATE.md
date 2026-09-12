# F6 — Release Evaluation and Generalization Gate: Pre-Outcome HOLD Record

Decision: **F6 = HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET.**

```text
Phase F = IN_PROGRESS / F5_COMPLETE_F6_HOLD
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

Per the fail-fast release order, the protected-holdout availability preflight
failed before ANY T5 model/evaluation call. No cohort (Gold, novel_dev,
novel_validation, holdout, or any ablation) was exposed. The HOLD preserves
every unexposed cohort for a future authorized F6 attempt.

## 1. Starting state

- Starting HEAD: `47789f83cccb05affce7b72cb2ac1f6c78b93f50`
  ("Repair F5 composer provenance validation") — matched the expected baseline.
- Worktree clean; no unrelated user work; no history rewrites.

## 2. Stage A preflight audit results (zero-outcome)

### 2.1 Candidate-freeze infrastructure audit (authorized correction executed)

Findings at the starting HEAD, all confirmed by direct inspection:

1. **Stale benchmark binding**: `candidate.py` hashed
   `evaluation/benchmarks/v2/gold_questions.yaml` while the evaluator authority
   resolves the newest signed exposed benchmark (v2_6). Corrected.
2. **Stale adjudication record**: `candidate.py` hashed the v2
   `audit_resolution.yaml`; the v2_6 identity carries
   `manual_adjudications.yaml`. Corrected.
3. **Missing verification-role identity (F4)**: the frozen manifest recorded
   generation/judge/embedding models but neither `runtime_verification_model_id`
   nor `effective_verification_model_id`. Corrected.
4. **Missing runtime-mode identity**: no `primary_answer_point_mode` field.
   Corrected (records the product default `legacy_question_core` explicitly).
5. **Incomplete prompt fingerprint**: `prompt_fingerprint()` covered only six
   prompts and omitted the answer-point coverage review/revision prompts and
   the F5 `ANSWER_COMPOSER_SYSTEM_PROMPT` / `ANSWER_COMPOSER_REVIEW_SYSTEM_PROMPT`
   (active on every successful multi-claim answer). Extended to the full
   ten-prompt set with change-sensitivity tests. Corrected.
6. **Benchmark manifest record lag (extra finding)**: the signed v2_6
   `benchmark_manifest.json` recorded `dataset_sha256 = b5406e36…`, but the
   authorized D4-A2-R1 g021 criticality correction (commit `9b007b5`, three
   `critical: true → false` lines, no other change) had updated
   `gold_questions.yaml` (actual `6f12d54b…`) without aligning the manifest.
   The evaluator's signed-hash check therefore silently fell back to v2.5 —
   the effective runner authority at the starting HEAD was
   **m6-benchmark-v2.5**, not the authorized v2.6. Corrected by aligning the
   manifest record to the authorized corrected dataset with full provenance
   (previous hash, authorizing commit, correcting task). Question content is
   unchanged by this record fix; after the fix the runner resolves
   `m6-benchmark-v2.6 / 120 questions` again.

Preflight correction commits (evaluation-infrastructure only; no product
behavior change; part of the eventual release candidate identity per §7):

```text
c871444  Prepare F6 release evaluation identity
99fdbab  Fix release identity test assertion
```

Focused verification: `tests/unit/test_f6_release_identity.py` 6 passed +
18 subtests; `tests/unit/test_qa.py` 195 passed + 21 subtests;
`tests/unit/test_e3_missing_point_retrieval.py` 49 passed; `git diff --check`
clean.

### 2.2 Dataset identity and exposure audit

| Dataset | Identity | Status at HOLD |
| ------- | -------- | -------------- |
| Gold | m6-benchmark-v2.6, 120 questions, approved_exposed_development_benchmark_v2_6, manifest record aligned to the authorized corrected dataset | EXPOSED_BENCHMARK_REFERENCE — validated, unrun |
| novel_dev | novel-v1-dev-0.3.0, 28 questions, `acceptance_exposed: true` | EXPOSED_DEVELOPMENT_GENERALIZATION_DIAGNOSTIC — validated, unrun; never pristine release evidence |
| novel_validation | novel-v1-validation-0.2.0, 15 questions / 15 families, `agent_outcome_seen_before_freeze: false`; historical run records repeatedly state `novel_validation = UNSEEN` | PRISTINE — validated, unrun |
| holdout | panda-novel-holdout-v1, FROZEN_SEALED, expected_count 13, externally_managed, loader `--dataset <external-path>` | metadata only — **package not available on this machine** |

### 2.3 Infrastructure/service availability

- `.env` present with all required Vertex/storage keys (no
  `QA_VERIFICATION_MODEL_ID` → same-model verification architecture, which F4
  supports and the freeze now records explicitly).
- PostgreSQL reachable; `index_identities` populated for `panda_knowledge_v1`.
- Qdrant reachable; collection `panda_knowledge_v1` present.
- Docker compose CLI reported no running project rows at preflight time
  (compose services were not confirmed running); freezing a candidate also
  requires live Docker image digests.

## 3. Blocking precondition (the HOLD cause)

The protected external holdout package is **not available on this machine**.
Bounded discovery performed without opening any protected content or printing
any protected path: the repository parent directory, the user profile's
Desktop/Documents/Downloads, a bounded user-tree search for holdout-named
artifacts, the D: drive root, and the project governance documents
(`H0_HOLDOUT_WORKER_HANDOFF.md` — a sanitized curation handoff defining the
conceptual protected workspace `PANDA_Agent_Holdout`, which does not exist on
this machine; `H0_HOLDOUT_CORPUS_PREFLIGHT.md` — locked-corpus path
resolution, not a holdout package locator) were checked. No external holdout
package or protected execution workspace was found.

Because §9 makes holdout availability a precondition for ANY F6 scientific
run, and the staged fail-fast order (§36 Stage A) stops before Stage B when
any precondition fails, the release evaluation was not started.

## 4. What remains to run after the precondition is met

A future authorized F6 attempt (fresh release-attempt identity) must, in
order: complete the holdout availability/protected-workspace preflight,
preregister (`evaluation/F6_RELEASE_EVALUATION_PREREGISTRATION.md` + JSON,
commit before the first T5 call), freeze the candidate identity, then execute
the staged pipeline — Gold 120 full run with the §21/§22 absolute/safety
gates, preregistered Gold ablation (Benchmark Dependency ≤ 0.05), novel_dev
28-case exposed diagnostic, pristine novel_validation 15-case run with
Generalization Gap ≤ 0.10 and the composer release audit (new-fact rate == 0;
readability gate ≥ 10 eligible pairs with composed strictly preferred), and
finally the single blind protected-holdout attempt (13 cases, Blind Holdout
Gap ≤ 0.15, sanitized aggregate receipt only).

Evaluation-infrastructure work completed by this HOLD is reusable: the
candidate freezer now binds the signed v2.6 identity, records the three model
roles and the runtime mode, and fingerprints the complete active prompt set.

## 5. Integrity audit at HOLD

- Product changes in this F6 task: **0** (only evaluation-infrastructure
  corrections under §6).
- Threshold changes: **0** (no thresholds were frozen; none altered).
- Holdout-driven tuning: **0** (no holdout outcome exists).
- Protected-content leakage: **0** (no protected path, question, answer, or
  selector entered this repository or context).
- Cohort exposure: **0** (Gold, novel_dev, novel_validation, holdout, and
  ablation cohorts remain unexposed).
- Candidate identity frozen: **NO** (freeze is deferred to the executing
  attempt, after preregistration, per §16).

## 6. Lifecycle result

```text
F6 = HOLD / PROTECTED_HOLDOUT_PRECONDITION_NOT_MET
Phase F = IN_PROGRESS / F5_COMPLETE_F6_HOLD
F1–F5 outcomes unchanged; READABILITY_BENEFIT = NOT_EMPIRICALLY_EVALUATED_IN_F5
Normal default = legacy_question_core; runtime_e1_v2 = explicit-selection-only;
default promotion = DEFERRED
```

Next action: provide/provision the protected external holdout package in its
governed execution environment, then re-authorize an F6 attempt (fresh
preregistration + candidate identity). No F6 scientific/evaluation call has
occurred in this task.

NEXT_TASK_EXECUTION_AUTHORIZED = false
