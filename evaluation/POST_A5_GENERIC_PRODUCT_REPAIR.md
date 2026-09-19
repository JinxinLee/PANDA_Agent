# Post-A5 Generic Product Repair — Completeness Recovery + Negative-Existence Safety

Status: `COMPLETE / PASS / COMPLETENESS_RECOVERY_AND_NEGATIVE_EXISTENCE_CONTRACTS_STRENGTHENED`

Zero scientific calls. Machine-readable companion: `evaluation/post_a5_generic_product_repair.json`. Product-behavior commit: `Repair completeness recovery and negative-existence safety` (this commit is the new product-behavior lineage head; docs-only descendants are not the product head).

> **R1 (forward-only):** `evaluation/POST_A5_GENERIC_PRODUCT_REPAIR_R1_CAUSAL_ATTRIBUTION_AND_LINEAGE_RECONCILIATION.md` supersedes this record's Workstream A ID wording and exact-g013-causality implication, the coverage root-cause overclaim, and the prose-only product-head provenance (exact SHA `e79d3232ed132a224cbceaf3524e19a1406bd648`). All other findings stand.

## 1. Root-cause matrix

| Mechanism | Confirmed | Owning layer | Action |
| --- | --- | --- | --- |
| A. Bounded revision recovery | Yes — the `_revise` merge silently discarded a revised claim reusing an existing local claim ID even for genuinely new content; the generator sees those IDs in its prompt, so reuse is a realistic failure mode (g013 signature: revision ran, evidence was in the pool, no missing-point content in the final answer) | A1 (revision merge) | Implemented |
| B. Coverage false acceptance | Yes — the coverage review schema had no per-point completeness structure, so a relevance-oriented reviewer could never be forced to state, per point, whether the requested substantive relationship is established (g023/g047 signature) | V1 coverage review (schema expressiveness) | Implemented |
| C. Corpus-negative claim safety | Yes — no generation/verification contract prohibited upgrading a local retrieval miss into corpus-wide nonexistence (g011 signature) | A1 + V1 (contract level) | Implemented |
| D. Retrieval/rerank role loss | Yes — `retrieval.py` bounds the reranker input to `fused_order[:30]`; the g011 native-documentation selectors matched four combined-pool objects that never survived into ranked top-30 | R2 | **DEFERRED / NO_SAFE_GENERIC_REPAIR_ESTABLISHED** |

## 2. Workstream A — bounded revision recovery

- Exact failure mechanism: in the `_revise` merge, any revised claim whose `claim_id` already belonged to a supported or unsupported claim was skipped unconditionally — genuinely new content died silently on an ID collision.
- Exact implementation: supported claims merge first (unchanged); each revised claim is then dropped only when (a) it is an identical normalized restatement of a claim just found unsupported under the same ID (F6-A2-FR2 unchanged), or (b) its normalized text already appears in the merged set (exact restatement); otherwise a colliding ID is renamed (`claim_id_r2`, …) and the claim survives.
- Boundedness: still at most one revision; no second retrieval pass, no E3 machinery, no retry loop. A revision that cannot find evidential support leaves the obligation missing — no claim is manufactured.
- Evidence behavior: revision already received all citation-eligible selected evidence; the merged draft is re-verified exactly as before, so a revised claim that fails verification still ends up unsupported.

## 3. Workstream B — coverage relevance vs completeness

- Previous weakness: `ANSWER_POINT_COVERAGE_REVIEW_SCHEMA` exposed only claim-level mappings plus a missing list; the reviewer could satisfy the schema while never explicitly judging per-point completeness.
- New generic contract: the schema now requires one `answer_point_coverage` record per runtime answer point — `{answer_point_id, supporting_claim_ids, complete}` — and `_validate_answer_point_review` enforces deterministically: exactly one record per point; supporting claims must be known, non-excluded, and mapped to the point; `complete=true` requires at least one supported contributing claim; `complete=false` must be exactly the `missing_answer_point_ids` set. Contradictory states (incomplete-but-not-missing, complete-without-support, unknown-ID support) now fail the review into the existing conservative error path.
- The coverage prompt instructs the reviewer to judge the substantive relationship each obligation requests — workflow ordering, purpose, comparison, location, condition, cause/effect — generic relationship kinds, no case domains, no Gold.
- Generator-declared mappings remain non-authoritative; the reviewer's per-point record is the only completeness authority.

## 4. Workstream C — negative-existence safety

- Generic rule (generation, `ANSWER_SYSTEM_PROMPT`): retrieved evidence is a non-exhaustive subset of the locked corpus — never state or imply corpus-wide absence from that subset alone; if one requested side of a comparison lacks support, state only that the supplied evidence does not establish that side; corpus-wide absence belongs exclusively to deterministic exact-lookup refusal paths.
- Generic rule (verification, `EVIDENCE_REVIEW_SYSTEM_PROMPT`): a corpus-wide absence claim inferred from a non-exhaustive subset is not evidence-supported and must be marked unsupported; when cited evidence directly establishes the denied thing, the claim is unsupported.
- Exact deterministic absence paths (exact unsupported-API/refusal machinery, version-conflict handling) are untouched and remain authoritative.

## 5. Workstream D — retrieval/rerank role loss: DEFERRED

Investigation established the mechanism (`rerank_pool = fused_order[:30]`; role-critical candidates ranked below the bound are lost before reranking). A repair meeting the authorized conditions (existing candidates, existing generic signal, no retrieval expansion, no global reselection, usefulness beyond g011) could not be established: the g011 query decomposes to a single obligation, so there is no existing per-obligation signal to preserve candidates with, and the robust remaining options (documentation quota, per-obligation retrieval, global reselection) would effectively promote deferred E3 machinery.

```text
RERANK_ROLE_PRESERVATION_REPAIR = DEFERRED / NO_SAFE_GENERIC_REPAIR_ESTABLISHED
```

`PRODUCTION_E3_PROMOTION = false`.

## 6. Deterministic verification (RED → GREEN)

- New suite `tests/unit/test_post_a5_generic_product_repair.py`: **RED before implementation — 4 failed / 8 passed** (A3 id-collision loss, B1 missing per-point record, C1/C4 absent prompt contracts); **GREEN after — 12/12** (A1 recovery, A2 no-fabrication, A3 collision survival, A4 identical restatement blocked, A5 one-shot bound, B1–B5 relevance/completeness separation, C1/C2/C4 contracts).
- Regression suites: `test_qa.py` 210 passed + 25 subtests; e2_a1 + e3 + generic-completeness + f6-release-identity + evaluation_runner → 336 passed; the only failure is the pre-existing stale v2.6-default-Gold assertion (recorded unrelated debt). The `test_e2_a3_runtime_activation.py` implementation-snapshot tests fail against a stale E2-A3-era anchor (all seven locked functions already differed at the starting HEAD) — pre-existing, unrelated, not modified.
- Combined: `test_f6a_release_infrastructure.py` + `test_identifier_catalog_repair.py` + reconciliation tests → 56/56.
- Test-fixture updates were schema adaptations only (mocks now produce the required per-point coverage record); two review builders gained a `points` parameter so synthetic point sets stay consistent with runtime points.

## 7. Release identity

Prompts changed (`ANSWER_SYSTEM_PROMPT`, `EVIDENCE_REVIEW_SYSTEM_PROMPT`, `ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT`), so the canonical fingerprint changed automatically:

```text
35f1dd3cbcd6cb636e2e92e7af28cb95415787e8d920c99c3b070eae86a8f097
→ 0a5b2909ef586671d533148979fc681c64e37528ad53781a4566cb9044835ba2
```

No hash is hardcoded; `tests/unit/test_f6_release_identity.py` passes and continues to prove that candidate/evaluation prompt authority is fully bound.

## 8. Materiality and accounting

```text
MATERIAL_PRODUCT_CHANGE = true
NEW_PRODUCT_BEHAVIOR_LINEAGE_HEAD = "Repair completeness recovery and negative-existence safety" commit
PANDA scientific/evaluation calls = 0
PANDA scientific/evaluation tokens = 0
novel_validation = PRISTINE_FOR_CURRENT_LINEAGE
holdout access = 0
protected-content leakage = 0
F6-B execution = 0
candidate frozen = false
Attempt 6 preregistered = false
Attempt 6 executed = false
ATTEMPT_6_READINESS = NOT_READY
```

This task proves the generic implementation contract and focused deterministic behavior only; it does **not** prove benchmark improvement. The scientific effect is evaluated only at the next authorized tier.

## 9. Next validation recommendation

```text
NEXT_TASK_RECOMMENDATION =
POST-A5 PRODUCT REPAIR VALIDATION /
FIXED EXPOSED SENTINEL T1
```

The future T1 must be small and fixed before execution: completeness-recovery mechanisms, negative-existence behavior, unaffected controls, no protected data. Its exact scientific result must not be designed after observing new outputs.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`
