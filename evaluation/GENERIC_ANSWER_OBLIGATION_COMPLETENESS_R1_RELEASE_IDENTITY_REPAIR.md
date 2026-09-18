# Generic Answer-Obligation Completeness R1 — Decomposition Prompt Release Identity Repair

Status: `COMPLETE / PASS / DECOMPOSITION_PROMPT_RELEASE_IDENTITY_REPAIRED`

## Starting state

- Starting HEAD: `476f838078f34c7178069a6ad45abaef864e4845`.
- Accepted product-development HEAD:
  `eda7d932a9b1b7b65436cba01e247859a6f9e056`.
- Normal product mode: `production_answer_obligations_v1`.
- Pre-R1 Attempt-5 state:
  `BLOCKED_PENDING_RELEASE_IDENTITY_REPAIR`.
- The known regenerable `data/_a3_gold_args.txt` scratch file remained
  untracked and untouched.

## Identity defect and repair

Normal QA now calls `QuestionDecomposer`, but the canonical
`prompt_fingerprint()` previously omitted its behavior-affecting model
contract. Candidate `source_tree_hash` was a broad integrity backstop, but the
explicit `prompt_hash` authority was incomplete.

`prompt_fingerprint()` now imports the authoritative
`panda_agent.question_decomposition` module and includes one canonical payload:

```text
question_decomposition = {
    prompt: QUESTION_DECOMPOSITION_SYSTEM_PROMPT,
    prompt_version: QUESTION_DECOMPOSITION_PROMPT_VERSION,
    schema_version: QUESTION_DECOMPOSITION_SCHEMA_VERSION
}
```

The full generated JSON schema is not duplicated. Prompt text, prompt version,
and schema version literals remain owned by `question_decomposition.py`.
Neither the prompt nor either declared version changed. `PROMPT_SET_VERSION`
was not bumped because no model behavior contract changed.

The corrected canonical prompt fingerprint for this checkout is:

```text
35f1dd3cbcd6cb636e2e92e7af28cb95415787e8d920c99c3b070eae86a8f097
```

## Canonical authority

Candidate manifest assembly and evaluation manifest assembly both continue to
set `prompt_hash` by calling the same imported
`panda_agent.evaluation_runner.prompt_fingerprint()` function. The focused
contract verifies function identity at the candidate authority seam, source
assembly at both manifest sites, and behavior-level evaluation manifest output.

For one checkout/configuration:

```text
candidate_manifest.prompt_hash
== evaluation_manifest.prompt_hash
== prompt_fingerprint()
```

Candidate manifests also continue to record
`primary_answer_point_mode = production_answer_obligations_v1`.

## Test-first verification

RED before implementation:

```text
3 failed, 8 passed, 18 subtests passed
```

The three failures independently showed that changing only the decomposition
system prompt, prompt version, or schema version did not change the canonical
fingerprint.

GREEN after the minimal implementation:

```text
PYTHONPATH=src python -m pytest tests/unit/test_f6_release_identity.py -q
11 passed, 18 subtests passed
```

The focused suite also verifies candidate/evaluation canonical-authority
equivalence, evaluation manifest output, production mode recording, and the
existing signed benchmark identity contract. `git diff --check` passed.

## Product, history, and lifecycle boundary

No QA, decomposition, generation, verification, revision, composer, retrieval,
or E3 behavior changed. `src/panda_agent/qa.py`, decomposition prompt content,
prompt versions, and schema versions were untouched.

Attempt 1-4 candidates, prompt hashes, evaluation manifests, stage receipts,
and prior closeouts were not rewritten. The repair is forward-only.

```text
MATERIAL_PRODUCT_CHANGE = false

NEW_CANDIDATE_DEVELOPMENT_HEAD =
eda7d932a9b1b7b65436cba01e247859a6f9e056

ATTEMPT_5_ELIGIBILITY =
ELIGIBLE_PENDING_FRESH_PREREGISTRATION_AND_CANDIDATE_FREEZE

candidate frozen = false
Attempt 5 preregistered = false
Attempt 5 executed = false

novel_validation = PRISTINE_FOR_CURRENT_LINEAGE
holdout access = 0
protected-content leakage = 0
F6-B execution = 0

PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
```

```text
NEXT_TASK_RECOMMENDATION =
F6-A ATTEMPT 5 /
FRESH PREREGISTRATION, CANDIDATE FREEZE, AND CONTINUOUS PRE-RELEASE VALIDATION

NEXT_TASK_EXECUTION_AUTHORIZED = false
```
