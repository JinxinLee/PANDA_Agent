# PANDA Agent — D2-A3 Resolver Role Decision

> Status: `D2-A3 = COMPLETE / RESOLVER_ROLE_DECISION_FROZEN` (2026-08-30)
>
> Overall D2 role: `MIXED_ROLE / BOUNDED_AUTHORITY_BY_MECHANISM`
>
> Current production D2 role: `SHADOW`

## 1. Objective and boundary

D2-A3 freezes the authority and eligible future system role of each existing
D2 resolver mechanism. It does not modify resolver behavior, retune a
mechanism, wire D2 into production retrieval, or perform a new evaluation.

This decision used committed frozen evidence only. The stage performed zero
new D2 resolver runs, retrieval or QA cases, model/analyzer/embedding/reranker/
verifier/judge calls, production database writes, or Qdrant writes.

`production-consumable` in this report means eligible for consideration by a
separately authorized integration stage. It does not mean production-wired.
D2-A3 authorizes no production wiring.

## 2. Evidence hierarchy

The decision uses this hierarchy:

```text
D2-A2 = direct frozen resolver-efficacy and resolver-safety evidence
ND-0  = production retrieval generalization context only
```

ND-0 measured a production retrieval path that did not consume D2. It cannot
establish that D2 or Tier D improves or fails on `novel_dev`, and it cannot
support a production-authority claim. It establishes contextual overlap and
practical relevance only.

## 3. Frozen D2-A2 evidence

The authoritative A2R2 accounting is:

```text
total cases = 22
valid = 20
invalid = C10, C14
correct = 16

correct_resolve = 9
wrong_resolve = 1
correct_abstain = 5
wrong_abstain = 0
correct_ambiguous = 2
wrong_ambiguous = 3
```

| Metric | Frozen value |
| --- | --- |
| Resolution accuracy | 9/12 = 0.75 |
| Canonical identity accuracy | 6/9 = 0.6667 |
| Explicit canonicalization accuracy | 1/1 = 1.0 |
| Source-native noncanonicalization accuracy | 3/3 = 1.0 |
| Abstention accuracy | 5/6 = 0.8333 |
| Ambiguity accuracy | 2/2 = 1.0 |
| False-positive resolution rate | 1/8 = 0.125 |

The six valid descriptive positives produced three correct resolutions, three
ambiguous results, zero unresolved results, and zero wrong-confident results.
The only valid wrong-confident case was C16.

C10 and C14 are invalid and excluded from direct efficacy and safety
accounting. C10's raw receipt is qualitative observation only; C14 is a
curation inventory error.

## 4. ND-0 contextual evidence

The final case-level D2-relevance accounting is `DIRECT = 7`, `INDIRECT = 7`,
and `NONE = 14`. These are topological/contextual labels, not mechanism tiers
or treatment outcomes.

The eight descriptive-context cases are accounted exactly once:

- five pure candidate-generation losses: n005, n009, n010, n020, n029;
- two ranking losses: n002, n017;
- one mixed channel and final-selector loss: n022.

n014 is DIRECT context for an exact/structural mechanism and is not Tier D
descriptive context. n023 is surface-variation terminology context whose
observed system loss was ranking. ND-0 resolver efficacy remains `UNEVALUATED`.

## 5. Decision principles

The following principles are frozen:

1. `EVIDENCE STRENGTH CONTROLS AUTHORITY`.
2. `AUTHORITY AND USEFULNESS ARE SEPARATE`.
3. Broad candidate generation may be permissive; authoritative resolution
   must remain conservative.
4. `RESOLVED_UNIQUE` does not grant authority independently of its mechanism.
5. Production-consumable eligibility is distinct from actual integration.
6. Query expansions never carry identity authority.
7. A source-native match remains source-native unless governed Tier G
   co-reference supports cross-record canonicalization.

## 6. Per-mechanism role matrix

| Mechanism | A2 direct evidence | ND-0 context | Identity authority | Canonicalization | Production-consumable | Forbidden behavior | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tier G | Applicable observed strong-identity behavior correct; true-alias canonicalization 1/1; source-native safety 3/3; no observed false cross-record canonicalization | No identity-mapping failure or production need established | Yes, bounded | Only accepted true co-reference | Eligible, not wired | Relatedness, similarity, relations, or rank as co-reference | `AUTHORITATIVE_BOUNDED` |
| Tier S | Exact symbol/path correct where applicable; competition and version scope conservative | n014 exact/structural context; its loss was candidate generation | Yes, matched record only | No cross-record canonicalization | Eligible, not wired | Substitute a related/canonical record for the source-native match | `AUTHORITATIVE_BOUNDED` |
| Tier D unique | 3/6 correct, 3/6 ambiguous, 0/6 wrong-confident | Eight contextual cases; no treatment evidence | No | No | Advisory eligibility only, not wired | Treat `RESOLVED_UNIQUE` as identity; narrow scope; force selection | `PRODUCTION_CONSUMABLE_NONAUTHORITATIVE` |
| Tier D ambiguous | Conservative competition signal; descriptive ambiguity 3/6; expected-ambiguity accuracy 2/2 | Not production-consumed | No | No | Advisory eligibility only, not wired | Collapse candidates or treat ambiguity as nonexistence | `PRODUCTION_CONSUMABLE_NONAUTHORITATIVE` |
| UNRESOLVED/abstention | 5 correct abstentions, 0 wrong abstentions in final valid-case accounting | Not production-consumed | No | No | Diagnostic eligibility only, not wired | Interpret as target does not exist or filter retrieval negatively | `PRODUCTION_CONSUMABLE_NONAUTHORITATIVE` |
| Corrective terms | C08 correct, correction surfaced, `identity_authority = false`, UNRESOLVED | No contextual applicability | No | No | Correction/advisory eligibility only, not wired | Promote correction to true alias or silently canonicalize | `PRODUCTION_CONSUMABLE_NONAUTHORITATIVE` |
| SAME_AS | Natural A2 applicability 0 | No topology observed | Contract-conditional, unevaluated | Contract-conditional, unevaluated | No | Activate unreviewed or conflicting edges; claim efficacy | `UNEVALUATED` |
| RESOLVED_MULTIPLE | Schema supported; natural A2 applicability 0 | No topology observed | Unevaluated | No independent authority | No | Treat singular ambiguity or lexical plurality as legitimate multiple | `UNEVALUATED` |
| Whole-question fallback | C16 wrong-confident; formal FPR contribution 1/8 | Not observable because D2 was not wired | No | No | No | Override stronger identifier rejection, mention-local ambiguity, or scope | `PRODUCTION_PROHIBITED` |

## 7. Tier G decision

Tier G is `AUTHORITATIVE_BOUNDED` with `MEDIUM` confidence. The available A2
sample is positive but small, so this is not a global reliability claim.

Tier G may carry identity authority only when the evidence is a governed
canonical object ID, accepted true identity alias, accepted and reviewed
SAME_AS edge, or exact source-native technical identifier with explicit
source/type/version grounding. Competing or scope-incompatible evidence must
remain AMBIGUOUS or UNRESOLVED.

## 8. Tier G canonicalization boundary

Cross-record canonicalization requires governed true co-reference: an accepted
true alias or an accepted and reviewed SAME_AS edge with compatible source,
type, version, and scope. Relatedness, `IMPLEMENTS`, `FORMALIZES`, `PRODUCES`,
`CONSUMES`, `DEPENDS_ON`, similarity, and retrieval rank cannot establish
canonicalization.

The Tier G role is an eligibility decision. SAME_AS remains separately
unevaluated and inactive because no accepted edge had natural A2
applicability.

## 9. Tier S decision

Tier S is `AUTHORITATIVE_BOUNDED` with `MEDIUM` confidence for direct
matched-record identity only. An exact canonical title, unique symbol, path/
locator, or stable repository/document identifier may identify its matched
record when source/type/version scope is explicit and no equal competitor
remains.

Tier S cannot cross-record canonicalize. For a source-native match:

```text
matched_object_id = source-native record
canonical_object_id = null
```

Only independent Tier G co-reference can change that boundary.

## 10. Tier D decision

Tier D `RESOLVED_UNIQUE` has no identity authority and no canonicalization
authority. Its status may be eligible for separately integrated production
consumption only as an auditable candidate hypothesis or additive retrieval
hint. It cannot remove candidates, restrict governed source/version scope, or
force final selection.

Tier D `AMBIGUOUS` is useful as a non-authoritative advisory signal: retain
multiple governed candidates, avoid premature collapse, and expose
uncertainty. AMBIGUOUS is not a failure by default and grants no identity
authority.

The Tier D role decision has `HIGH` confidence because the boundary follows
both the direct 3-correct/3-ambiguous/0-wrong-confident evidence and the frozen
contract. This confidence applies to the authority boundary, not to broad
efficacy.

## 11. Corrective terms and abstention

Corrective terms are `PRODUCTION_CONSUMABLE_NONAUTHORITATIVE` with `HIGH`
confidence, but are not wired. They may support diagnostics, user-facing
correction, and additive candidate/query support. They cannot identify or
canonicalize an entity.

An accepted true alias is not a corrective term. `*_pid_final.root` may be a
true alias where D1 semantics establish true identity. `restgas_profile.txt`
is corrective and cannot silently canonicalize to
`configuration.restgas_profile`.

UNRESOLVED/abstention receipts are also eligible only as non-authoritative
diagnostics. `UNRESOLVED` means that the resolver lacks sufficient governed
identity evidence; it does not mean that the target does not exist and cannot
be used as a negative retrieval filter.

## 12. SAME_AS

SAME_AS is `UNEVALUATED`: contract-supported, natural A2 applicability 0, no
novel topology, and no production activation. The contract can in principle
support Tier G co-reference only for accepted and reviewed true-identity edges
that preserve D1 orientation and source/type/version constraints. Efficacy and
consumer safety require representative natural applicability and a separately
authorized focused stage.

## 13. RESOLVED_MULTIPLE

RESOLVED_MULTIPLE is `UNEVALUATED`: representable in the schema, natural A2
applicability 0, and no novel topology. It remains reserved for legitimate
multi-entity semantics and must not represent uncertainty, singular
competition, or automatic lexical plurality. No production consumption is
eligible at this checkpoint.

## 14. Whole-question fallback

Whole-question fallback is `PRODUCTION_PROHIBITED` with `HIGH` confidence.
C16 supplies direct negative safety evidence: the stronger version-sensitive
identifier interpretation was rejected, after which whole-question fallback
confidently selected an unrelated entity. C16 is the only valid wrong-
confident case and contributes the formal FPR of 1/8.

This is a fallback-precedence and granularity issue, not a wrong-confident Tier
D descriptive-positive result: the descriptive-positive subset had zero
wrong-confident cases. C10 remains qualitative only and C14 is excluded as a
curation inventory error. A separate repair and focused reevaluation are
required before reconsidering the fallback role.

## 15. Overall resolver role

The overall role is:

```text
MIXED_ROLE / BOUNDED_AUTHORITY_BY_MECHANISM
```

- Tier G: bounded governed identity authority and true-co-reference
  canonicalization authority.
- Tier S: bounded direct matched-record authority, no cross-record
  canonicalization.
- Tier D unique, Tier D ambiguous, UNRESOLVED, and corrective terms:
  non-authoritative advisory eligibility only.
- SAME_AS and RESOLVED_MULTIPLE: unevaluated and inactive.
- Whole-question fallback: production-prohibited.

The current production D2 role remains `SHADOW`.

## 16. Explicit questions

### Q1. Can Tier G carry identity authority?

Yes, bounded to valid governed Tier G evidence.

### Q2. Can Tier G cross-record canonicalize, and under what evidence?

Yes, only under accepted true alias or accepted/reviewed SAME_AS co-reference
with compatible source, type, version, and scope. SAME_AS activation itself
remains unevaluated and unauthorized.

### Q3. Can Tier S carry direct matched-record authority?

Yes, bounded to an exact unique match within explicit scope.

### Q4. Can Tier S cross-record canonicalize?

No. Independent Tier G co-reference is required.

### Q5. Can Tier D RESOLVED_UNIQUE be identity-authoritative?

No. The status is an advisory candidate hypothesis only.

### Q6. Can Tier D outputs be production-consumable as advisory signals?

They are eligible for separately authorized, non-authoritative advisory
integration; no consumption is wired by D2-A3.

### Q7. Can Tier D AMBIGUOUS be useful in production?

Yes, as a signal to retain candidates, avoid collapse, and expose uncertainty.
It carries no identity authority.

### Q8. Can UNRESOLVED be consumed as a conservative abstention signal?

Yes, as a diagnostic meaning insufficient governed identity evidence. It
cannot mean target nonexistence or filter retrieval negatively.

### Q9. Can corrective signals be production-consumed?

They are eligible only for diagnostics, user-facing correction, and additive
candidate/query support, with no identity or canonicalization authority.

### Q10. What is the status of SAME_AS?

Contract-supported, efficacy unevaluated, production inactive.

### Q11. What is the status of RESOLVED_MULTIPLE?

Contract-supported/schema-representable, efficacy unevaluated, production
inactive.

### Q12. What is the role of whole-question fallback?

Production-prohibited and shadow-only until a separate repair and focused
reevaluation demonstrate safe precedence and granularity.

### Q13. What production wiring is authorized by D2-A3?

None.

## 17. Production-integration implications and evidence gaps

Any future consumption requires explicit authorization for a bounded
integration stage covering consumer precedence, authority enforcement, source/
type/version scope preservation, rollback/fallback behavior, and focused
evaluation. D2-A3 does not design or execute that integration.

Remaining gaps are the small Tier G/S sample, Tier D discrimination limits,
zero natural SAME_AS and RESOLVED_MULTIPLE applicability, absence of D2
treatment evidence on novel retrieval, and C16 fallback-safety evidence.

## 18. Next stage

The next roadmap task is **D3 — Small shortcut-migration experiment**
(`NOT_STARTED`). D2-A3 does not start D3. Any D2 production consumption would
instead require its own separately authorized bounded integration stage.
