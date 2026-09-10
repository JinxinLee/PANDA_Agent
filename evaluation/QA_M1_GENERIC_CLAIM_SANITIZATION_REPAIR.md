# QA-M1 — Generic Claim Sanitization Repair

COMPLETE / PASS / GENERIC_CLAIM_SANITIZATION_REPAIR_VALIDATED.
Starting HEAD: `f1c3fd28678292f951e9d827354f558b927079db` (clean).
This is shared QA maintenance, not E2 activation, A3-R4 or E3 work.

## Repair and focused T0

Owner: `src/panda_agent/qa.py::_strip_nonessential_external_identifiers`.
The old external-name regex replaced only the head of a template, leaving its
angle-bracket payload attached to generic prose. The private helper
`_abstract_external_type_text` walks balanced angle brackets, recursively abstracts
unrequested external wrappers in their payload, and preserves payload text using
parenthesized prose. No C++ parser, dependency, configuration or policy change.
Explicitly requested question/plan identifiers retain their complete expression;
non-template abstraction remains equivalent. Incomplete template input is left
intact rather than partially rewritten. Only claim_text changes; input claims
are not mutated. Existing answer/revision call sites share the repaired function.

Command: `python -m pytest tests/unit/test_qa.py -k 'sanitiz or external_identifier' -q`
with PYTHONPATH=src. Result: **14 passed, 37 deselected, 2 subtests passed**.
Coverage: simple STL, PANDA-style payload, unseen synthetic payload, nested STL,
Boost, ordinary external names, requested question/plan identifiers, unrelated
claims, metadata preservation, multiple/spaced templates, incomplete input and
fake answer/revision integration in legacy and runtime modes. No full suite.

## Frozen/static impact

All artifacts were read using `git show` at the starting HEAD. The sanitizer AST
at each artifact's candidate identity equals the starting sanitizer AST. Scope:

| Committed raw artifact | Execution records | Initial/revision claim snapshots |
| --- | ---: | ---: |
| e2_a3_paired_runtime_raw.json | 56 | 155 |
| e2_a3_r1_targeted_paired_raw.json | 10 | 31 |
| e2_a3_r2_targeted_paired_raw.json | 12 | 34 |
| e2_a3_r3_activation_paired_raw.json | 28 | 54 |
| e2_a3_r3_r1_recovery_paired_raw.json | 6 | 16 |
| Total | 112 | 290 |

These are claim snapshots from 128 recorded answer/revision events, not unique
questions or independent scientific samples. Three initial claims in the failed
original g001 legacy arm lack the final plan; none contains a targeted external
identifier, so unchanged behavior is provable without inventing plan metadata.

Old-vs-new changes: **2/290**, both initial runtime claims; **288 unchanged**.
Unexpected collateral changes: **0**. Changed claim metadata is identical.
Known old sanitizer output exactly reproduces each stored final claim text;
new outputs below are static transformations, not new QA answers or judgments.

| Case / claim | Frozen initial fragment | Old output fragment | Repaired fragment |
| --- | --- | --- | --- |
| Original R3 g029 / claim_pndlmdcombineddatareader_boundary | std::vector<Lmd::Data::TrackPairInfo> records | an internal support type<Lmd::Data::TrackPairInfo> records | an internal support type containing (Lmd::Data::TrackPairInfo) records |
| Recovery g059 / claim.2 | std::vector<RecoBinSmearingContributions> | an internal support type<RecoBinSmearingContributions> | an internal support type containing (RecoBinSmearingContributions) |

Historical malformed final claims: **2**, one in each cited raw artifact.
Literal occurrences are duplicated: original R3 raw 2, recovery raw 2, corresponding
judged artifacts 2 each, and G11 review JSON 6. These 14 serialized occurrences
are not 14 distinct defects. Earlier A3/R1/R2 raw artifacts contain zero such
literal occurrences. All differences are balanced external-template abstraction;
no ordinary path, standalone domain identifier, requested identifier, citation,
mapping or unrelated/non-template claim changed in the frozen scan.

## Acceptance and boundaries

M1-M11 PASS for this deterministic maintenance scope: known/nested syntax fixed;
payload retained; requested names and unrelated text preserved; metadata stable;
shared answer/revision behavior; intended-only static impact; forbidden product
surfaces unchanged; default legacy; zero scientific calls. Unit tests establish
synthetic nested/Boost/requested behavior not represented by the two affected
frozen inputs. This bounded scan does not prove every possible C++ expression.
No claim that g029 would be equivalent, G11 would pass, or live quality improved.

Only sanitizer/helper, focused tests, this record and lifecycle docs change.
Prompts, schemas, retrieval, Gold, citation admission, colon normalization,
decomposition, coverage, renderer, revision policy, public DTO/API and default
selector are unchanged. Historical raw/judged/results, E2 failures and G11
preferences remain immutable. Scientific/provider calls = 0; scientific tokens = 0;
new live QA executions = 0; new judge calls = 0. No external AGY worker invoked.

```text
QA-M1 = COMPLETE / PASS / GENERIC_CLAIM_SANITIZATION_REPAIR_VALIDATED
E2 = COMPLETE / CORE_MECHANISM_VALIDATED / DEFAULT_PROMOTION_DEFERRED
runtime_e1_v2 = VALIDATED_EXPERIMENTAL_PATH / EXPLICIT_SELECTION_ONLY
Normal default = legacy_question_core
E3 = NOT_STARTED / ARCHITECTURALLY_UNBLOCKED
NEXT_TASK_RECOMMENDATION = E3 — Missing-Point Targeted Retrieval
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

One normal maintenance commit; no scientific freeze chain. E2 is not reopened,
runtime is not activated, and E3/gate redesign/A3-R4/T3/T5 are not executed.
QA-M1 COMPLETE / PASS
