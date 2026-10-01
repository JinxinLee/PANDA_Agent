# G5 V1 Disposition-Provenance False-Insufficiency Repair Implementation

## 1. Decision and repository authority

**PASS / COMPLETE / DETERMINISTIC VERIFICATION PASS.** Implements the approved [V1 design](G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_DESIGN.md), under `ALL_TO_ALL_CHECK_PROOF_BASIS`. The [integrated failure-family review](G5_INTEGRATED_FAILURE_FAMILY_REVIEW.md), [D1 implementation](G5_D1_DIAGNOSTIC_METADATA_ROBUSTNESS_REPAIR_IMPLEMENTATION.md), G1/G2 design authority and historical results retain their meaning.

Starting `main` HEAD: `c1d6084045efe9b05d9d0073e48a846b6fe58e11`, message `Design G5 V1 disposition provenance repair`, parent `cd0a65df7576a736e83fdfe3da5998b766173ffc`. Entry worktree was clean. Product lineage before this task was `cd0a65df7576a736e83fdfe3da5998b766173ffc`; its previous lineage was `047201166057edd9859292a1760bc2e9bbf173a2`.

The commit introducing this record, `Clarify V1 proof-basis provenance contract`, is the new repository/product-behavior lineage head. Resolve its immutable SHA with `git log -1 --format=%H --grep='^Clarify V1 proof-basis provenance contract$'`; the delivery response reports the exact SHA and post-commit worktree status. Previous product lineage becomes `cd0a65df7576a736e83fdfe3da5998b766173ffc`. Push is not authorized or performed.

## 2. Owning prompt change

Only `PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SYSTEM_PROMPT` and the global prompt-set patch version change in product source:

| Instruction | Implemented clarification |
|---|---|
| Basis meaning | Small adequate proof actually used for this check; every item grounds the judgment; not considered-evidence inventory or optional corroboration. |
| Individual citation closure | Every named supporter **INDIVIDUALLY** cites **EVERY** basis evidence ID. Citation union alone is insufficient. Existing supplied claim citations cannot be added or rewritten. |
| Contribution | Each supported, relevant, correctly parent-mapped supporter directly contributes to the particular check. Parent/entity overlap alone is insufficient. |
| Collective completeness | The selected set answers the entire check. Multiple partial contributors remain permitted with individual citation closure; one supporter is permitted only when it is a complete witness. |
| Pre-emission selection | Smaller complete witness or adequate shared basis may be selected before emission only when semantically sound. No mechanical intersection or omission of necessary contribution/evidence. |
| Unsatisfied outcome | When no closure-valid complete witness exists, retain the truthful existing admitted-backed unsatisfied disposition where applicable and independent support/mappings; do not automatically infer evidence absence or invent a state. |
| Exact quotes | Copy from `untrusted_evidence.text`; preserve backticks, Markdown, case, Unicode, punctuation, internal spaces/newlines. JSON-decoded quote remains an exact contiguous substring. Claims may paraphrase; quotes may not. Short excerpts must remain adequate and bounded. |

Four neutral examples use existing named-check fields: A permits two contributing supporters with shared A; B rejects disjoint A/B citation union; C preserves backticks in an exact sentence and rejects the full altered sentence; D rejects an extra nonciting supporter even alongside a complete witness. Ordinary independent necessary checks must all pass; examples prohibit inventing subrelations or ordinary rows for a canonical relation. No historical case, Gold, real path or historical evidence ID appears in the examples.

## 3. Preserved contract and fixture reconciliation

`src/panda_agent/qa.py` is unchanged. The provider schema and `coverage-satisfaction-v2` are unchanged. G1's single completeness path, canonical ownership, G2 containment, supported/relevant/parent-mapped restrictions, strict `BAD_QUOTE` and `INVALID_SUPPORTER`, target-local A1, at most one revision and full original V2 inventory remain. No union acceptance, supporter/basis trimming, quote normalization/replacement, retry, extra verifier/A1 stage, retrieval/generation change or new runtime mode is introduced. Other prompt assignments are unchanged.

The task attachment section 13 labels bare `Maple::Run()` an invalid quote inside evidence `Cedar invokes \`Maple::Run()\` before Birch.`. That token is itself an exact contiguous substring, so the unchanged validator correctly accepts it. Section 6 Example C and the approved design instead supply a valid negative fixture: the **whole sentence** with backticks removed is not a substring. Verification follows that authoritative exact-substring rule: both the backtick-delimited token and bare inner token remain valid, while the full removed-backtick sentence, case change and added internal space remain `BAD_QUOTE`. This reconciles the concrete fixture contradiction without changing acceptance semantics or claiming delimiters must always be included in a selected excerpt.

## 4. Deterministic verification

All commands run in the repository root using the existing sibling virtual environment; no installation, live provider, benchmark or scientific execution occurs. Prefix for every pytest command below:

```powershell
& '..\.venv\Scripts\python.exe' -m pytest
```

| Step | Exact arguments after the prefix | Observed result |
|---|---|---|
| Pre-edit RED | `tests/unit/test_post_a5_c1_coverage_completeness.py::test_v1_proof_basis_prompt_contract -q` | 0 passed, 1 failed, 0 deselected; old prompt lacks the explicit proof-basis clause. |
| Post-edit GREEN | `tests/unit/test_post_a5_c1_coverage_completeness.py::test_v1_proof_basis_prompt_contract -q` | 1 passed, 0 failed, 0 deselected. |
| Initial host characterization | `tests/unit/test_g2_coverage_local_failure.py -k v1_existing_all_to_all -q` | 16 passed, 6 failed, 70 deselected. All six failures were test assertion shape mistakes after valid receipt acceptance: compared `accepted_coverage` list to the entire review dict. |
| Corrected valid fixtures, quotes, fake integration | `tests/unit/test_g2_coverage_local_failure.py -k 'v1_existing_all_to_all_valid or v1_exact_quote or v1_first_pass' -q` | 14 passed, 0 failed, 78 deselected. Correct comparison is to `review['answer_point_coverage']`; product semantics/expected validity unchanged. |
| G1/G2/C1 focused neighbors and examples | `tests/unit/test_post_a5_c1_coverage_completeness.py -k 'not test_v1_proof_basis_prompt_contract' tests/unit/test_g1_relationship_obligations.py tests/unit/test_g2_coverage_local_failure.py -k 'not test_v1_proof_basis_prompt_contract and not v1_existing_all_to_all and not v1_exact_quote and not v1_first_pass' -q` | 180 passed, 0 failed, 31 deselected. The final `-k` expression governs selection. |
| Active identity and O1 neutrality | `tests/unit/test_post_a5_o1_observability.py::test_o1_default_and_exact_neutrality tests/unit/test_qa.py::QATests::test_prompt_set_marks_completeness_and_judge_strictness -q` | 2 passed, 0 failed, 0 deselected. |

**213 distinct post-edit tests pass**, including 32 added cases (2 prompt/example cases and 30 host/integration cases). The 16 unchanged successful negative host fixtures were not rerun; 6 corrected valid cases plus 8 new quote/integration cases passed afterward. The initial six assertion-construction failures are not product RED evidence. Only the single pre-edit prompt assertion is the planned RED, and proves missing instructions, not real-model failure.

Host characterization covers ordinary and named owners: one supporter/one basis; two supporters/one shared basis; two supporters/two individually cited basis; nonciting, wrong-parent, unsupported, irrelevant, unknown, union-only, full-witness-plus-extra-malformed-supporter and uncited-extra-basis rejections. Input responses remain unchanged. Invalid owners cannot become complete or self-authorize A1; independent valid point siblings remain complete. The existing named-child tests additionally preserve independently valid admitted-unsatisfied sibling targets.

The existing G1/G2 neighbor tests cover exclusive ordinary/named paths, immutable relation identities, local failure ownership, at most one A1, target-only revision payload and full canonical V2 recheck. These are deterministic development checks, not formal acceptance comparisons.

Two separate scripted actual QA-graph runs deliver the active production prompt:

- Malformed first pass: basis `[A,B]`, supporters `[c1,c2]`, c1 cites A, c2 cites A/B. V1 remains PARTIAL with `INVALID_SUPPORTER`; final answer is insufficient, both supported claims are retained, no A1/V2 or retry. Three fake calls.
- Independently scripted compliant first pass: basis `[A]`, supporter `[c2]`, existing c2 states the full neutral witness and already cites A/B. V1 is accepted and answer complete; no A1/V2 or retry. Five fake calls including existing composition/review.

Synthetic call/token counters are fake instrumentation, not scientific consumption. These tests show that the host consumes a compliant first pass and still rejects a malformed one. They do not demonstrate that a real provider now emits a compliant proof. Direct contribution, adequate proof choice and collective semantics remain model judgments; static clauses are not deterministic semantic entailment checks.

Static closeout checks compare unchanged product files with starting Git blobs, compare prompt AST assignments allowing only the selected review/version, preserve both documentation historical suffixes and existing checkpoint paragraphs, enforce the eight-file change scope, verify unchanged decomposition/schema/mode, and run `git diff --check`. No new checksum manifest is introduced.

## 5. Active identity

The existing authority was invoked after the prompt change:

```powershell
& '..\.venv\Scripts\python.exe' -c "from panda_agent.evaluation_runner import prompt_fingerprint; print(prompt_fingerprint())"
```

```text
PROMPT_SET_VERSION_BEFORE = 3.12.0
PROMPT_SET_VERSION_AFTER = 3.12.1
PROMPT_FINGERPRINT_BEFORE = 5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce
PROMPT_FINGERPRINT_AFTER = 08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc
QUESTION_DECOMPOSITION_PROMPT_VERSION = 3.0.0
QUESTION_DECOMPOSITION_SCHEMA_VERSION = e1.question_decomposition.v3
COVERAGE_SATISFACTION_SCHEMA_VERSION = coverage-satisfaction-v2
NORMAL_PRODUCT_MODE = production_answer_obligations_v1

PRODUCT_SOURCE_CHANGE = true
PRODUCT_BEHAVIOR_CHANGE = true
TEST_CHANGE = true
PROMPT_CHANGE = true
HOST_VALIDATOR_CHANGE = false
PROVIDER_SCHEMA_CHANGE = false
CONFIG_CHANGE = false
DEPENDENCY_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
NEW_RUNTIME_MODE = false
```

Only active test/current-document identity expectations change. Historical G4/G5 manifests and fingerprints are untouched.

## 6. Changed files

- `src/panda_agent/prompts.py`
- `tests/unit/test_post_a5_c1_coverage_completeness.py`
- `tests/unit/test_g2_coverage_local_failure.py`
- `tests/unit/test_post_a5_o1_observability.py`
- `tests/unit/test_qa.py`
- `evaluation/G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_IMPLEMENTATION.md`
- `docs/EVALUATION_STATUS.md` (current state only)
- `docs/GENERALIZATION_ROADMAP.md` (current state only)

## 7. Scientific and protected boundary

```text
NEW_G5_RUNS = 0
N018_LIVE_RERUNS = 0
QA_SCIENTIFIC_RUNS = 0
RETRIEVAL_EVALUATION_RUNS = 0
SCIENTIFIC_GENERATION_CALLS = 0
SCIENTIFIC_EMBEDDING_CALLS = 0
EXTERNAL_JUDGE_CALLS = 0
SCIENTIFIC_TOKENS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```

No historical case rerun, live QA, retrieval evaluation, protected evaluation, full suite, G6 or scientific benefit comparison occurred. No empirical before/after metric is available.

## 8. Limitations and forward lifecycle

The retained all-to-all host contract can overconstrain a legitimate disjoint-source multi-claim canonical proof. No prompt wording removes that representational limit, and no mechanical common-citation choice proves adequacy. Provider adherence, exact quote reliability, necessary-evidence/witness selection and empirical false-insufficiency recovery remain unmeasured. No recovery of the four historical cases is claimed. A historical product-error run is not completed by prompt delivery.

```text
G5_V1_PROVENANCE_REPAIR_IMPLEMENTATION = COMPLETE / DETERMINISTIC VERIFICATION PASS
SELECTED_V1_PROVENANCE_CONTRACT = ALL_TO_ALL_CHECK_PROOF_BASIS
V1_PROVENANCE_PROMPT_ALIGNMENT = VERIFIED
HOST_ACCEPTANCE_RULE_CHANGE = false
PROVIDER_COMPLIANCE = NOT_EMPIRICALLY_ESTABLISHED
FALSE_INSUFFICIENCY_RECOVERY = NOT_EMPIRICALLY_ESTABLISHED
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = G5 POST-V1-REPAIR TARGETED LIVE VERIFICATION DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

The recommendation follows successful deterministic delivery and the remaining empirical uncertainty. It is a design task requiring separate authorization, explicit case scope, call budget, lineage identity, stop rules and mixed-provenance interpretation. It does not authorize live execution or select a full G5 rerun.
