# F2-A1-R1 — Verifier-Support Semantic Entailment Repair

Status: `COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED`
Type: corrective bounded production repair of F2-A1 + deterministic verification.
Zero PANDA scientific/evaluation calls; zero protected-data access.

Task identity: F2-A1-R1 — Verifier-Support Semantic Entailment Repair.
Traceability: PF-LR1 Group A / F1 residual R13. R13 is provenance only, not the
task name.

## 1. Historical correction record

- Initial F2-A1 (commit `32abb1c`, "Generalize verifier support semantics")
  validly removed (1) the benchmark-shaped explicit-code-token whitelist and
  (2) the comparison-wording deterministic-support exceptions.
- A subsequent independent post-commit audit did **NOT** accept the original
  `COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED` closeout:
  the remaining generic lexical identifier/path/symbol coverage branches could
  still mark a whole claim as deterministically supported, causing an explicit
  semantic-review `unsupported_claim_ids` verdict to be ignored.
- F2-A1-R1 exists specifically to repair that defect. No historical commit or
  result was rewritten; `32abb1c` remains in history and this report is the
  authoritative correction. The original F2-A1 report carries a
  correction/supersession notice and its implementation narrative is unchanged.

## 2. Starting state

```text
HEAD = 32abb1ca81a44cbd7bed9e13ebd99fc4b2e20790 (Generalize verifier support semantics)
working tree = clean
F2-A1 = COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED (premature; corrected by this repair)
F2 = IN_PROGRESS / A1_COMPLETE
F3 = NOT_STARTED / UNEXECUTED
Phase F = IN_PROGRESS / F2_A1_COMPLETE
normal default = legacy_question_core
default promotion = DEFERRED
```

## 3. Defect verification (independent, at HEAD `32abb1c`)

`QAAgent._verify` still contained live whole-claim lexical bypasses feeding
`deterministically_supported_claims`, consumed by
`for claim_id in unsupported: if not shadow and claim_id in
deterministically_supported_claims: continue`:

1. full structured-identifier coverage (repository paths, `::`-qualified,
   `Pnd`-prefixed tokens all appearing in the cited evidence text);
2. path-token coverage over a cited code repository plus any explicit code
   symbol in the cited text;
3. two-or-more explicit code symbols all present in the cited text;
4. path-token coverage over a cited code repository;
5. an unreachable `scope_`-claim branch (internal-claim filtering removes
   `scope_` claims before the loop).

All five are lexical token/path/symbol overlap. Lexical grounding establishes
citation/locator/identifier integrity — it does not establish the truth of the
claim's factual predicates. Any claim whose identifiers all appeared in its
cited evidence could therefore bypass an explicit semantic unsupported verdict,
violating the F2-A1 semantic contract
(`citation / locator / identifier grounding != whole-claim semantic entailment`).

## 4. Repair

`src/panda_agent/qa.py` (−89 lines, removals only):

- Deleted the `deterministically_supported_claims` set, all five add-branches,
  and their now-unused helpers (identifier-token collection, path tokens,
  explicit code tokens, cited source-set set-logic).
- Deleted the unsupported-claim exemption: the semantic review's
  `unsupported_claim_ids` verdict is now always honored; every unsupported
  known claim produces an error and enters the bounded revision path.

`deterministically_supported_claims` no longer exists; **no deterministic
whole-claim semantic-support bypass remains**. No live claim class has a fully
structured, whole-claim entailment contract (the only candidate, `scope_`
provenance claims, is unreachable and carries template wording beyond what
structured metadata derives), so per the repair decision the override was
removed entirely rather than narrowed. The `cited` evidence-text assembly was
retained solely because the deterministic unsupported-identifier integrity
check depends on it.

Preserved deterministic verification (unchanged): unsupported-identifier
check, wrong-code-version check, incomplete code/paper/web citation checks,
internal-claim filtering, generic claim sanitization, refusal semantics,
`_deterministic_missing_requirement_ids` (R10) and all requirement-completeness
logic, public DTOs, prompts, retrieval, evidence selection, mode selection.

## 5. Adversarial contract (tests/unit/test_qa.py)

`test_generic_path_anchor_support_survives_conservative_review` was audited,
found to encode the unsafe assumption (path grounding overriding semantic
rejection), and replaced. New/updated contracts:

| Test | Contract | Result |
|---|---|---|
| T1 `test_correct_path_with_unsupported_semantics_remains_unsupported` | correct cited path + unsupported factual assertion → stays unsupported | PASS |
| T2 `test_correct_symbols_with_unsupported_relationship_remains_unsupported` | correct qualified symbol + false relationship → stays unsupported | PASS |
| T3 `test_multiple_identifiers_with_false_predicate_remains_unsupported` | two correct symbols + unsupported joining predicate → stays unsupported | PASS |
| T4 `test_legitimate_supported_claim_still_accepted` | grounded claim accepted by the semantic review remains accepted; `_verify` is not blanket rejection | PASS |
| T5 `test_removed_token_whitelist_no_longer_grants_support` / `test_comparison_wording_no_longer_grants_support` | former whitelist tokens and comparison wording never grant deterministic support | PASS |
| T6 `test_deterministic_integrity_checks_remain_active` | wrong-code-version and unsupported-identifier checks fire independently of the semantic verdict | PASS |

## 6. Verification

- `PYTHONPATH=src python -m pytest tests/unit/test_qa.py -q` → **58 passed,
  2 subtests passed** (includes T1–T6).
- Shared-verify bounded regression (E3 second verify uses `_verify`; this is a
  deterministic regression check, not a new scientific E3 validation and not an
  E3 reopening): the authoritative focused E3 deterministic set (E3-LR1 §9:
  49 focused E3 tests) plus 42 neighboring E2-A1 shadow tests →
  `PYTHONPATH=src python -m pytest tests/unit/test_e3_missing_point_retrieval.py
  tests/unit/test_e2_a1_answer_point_coverage.py -q` → **91 passed**.
- `git diff --check` PASS; diff audit confirms zero changes to R10 semantics
  (`_deterministic_missing_requirement_ids`, `pointer_identifier_normalization`),
  requirement logic, retrieval, reranking, or evidence selection.
- PANDA scientific/evaluation calls = 0; PANDA scientific/evaluation tokens = 0.

## 7. Limitations

- Whole-claim support now rests entirely on the semantic review; the historical
  motivation for the removed bypasses (conservative false rejections) is a
  verifier-quality concern that belongs to future separately authorized
  verifier work, not to a lexical bypass.
- No scientific evaluation was run or authorized; behavior impact beyond the
  focused deterministic surface is unmeasured by design.

## 8. Lifecycle closeout

```text
F2-A1-R1 = COMPLETE / PASS / WHOLE_CLAIM_SEMANTIC_BYPASS_REMOVED
F2-A1    = COMPLETE / PASS / GENERIC_VERIFIER_SUPPORT_SEMANTICS_ESTABLISHED
           (final state achieved only after this corrective repair)
F2       = IN_PROGRESS / A1_COMPLETE (F2 still incomplete)
F3       = NOT_STARTED / UNEXECUTED
Phase F  = IN_PROGRESS / F2_A1_COMPLETE
normal default = legacy_question_core (unchanged)
default promotion = DEFERRED (unchanged; promotion relevance != promotion authorization)
```

```text
NEXT_TASK_RECOMMENDATION = F2-A2 — Deterministic Completeness Semantic Cleanup
                           (PF-LR1 Group B / F1 residual R10)
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
