# Post-A5 Generic Product Repair R1 — Causal-Attribution and Lineage Reconciliation

Status: `COMPLETE / PASS / CAUSAL_ATTRIBUTION_AND_PRODUCT_LINEAGE_RECONCILED`

Zero scientific calls. Docs/provenance-only: no product, prompt, retrieval, evaluator, Gold, or calibration file changed. Machine-readable companion: `evaluation/post_a5_generic_product_repair_r1_causal_attribution_and_lineage_reconciliation.json`.

## 1. Scope

Starting HEAD `6d5d54d771fe56065d60fe2c08b0ce5011f4a343`; product-behavior commit `e79d3232ed132a224cbceaf3524e19a1406bd648` (`Repair completeness recovery and negative-existence safety`); pre-repair baseline `257d77aa1d736101110753fbdc5085b713339de0`. All claims below were reconstructed from the pre-repair implementation at `257d77a`, the repair diff, the deterministic tests, the frozen Attempt-5 artifacts, and the current lifecycle records — not from closeout prose.

`MATERIAL_PRODUCT_CHANGE = false`; `EVALUATOR_CONTRACT_CHANGE = false`; `GOLD_CHANGE = false`; `CALIBRATION_CHANGE = false`. The docs-only R1 commit is not a product-behavior lineage head.

## 2. Workstream A — bounded revision recovery: causal strength corrected

- `GENERIC_REVISION_ID_COLLISION_DEFECT = CONFIRMED` — proven from the pre-repair merge code and the T0 tests; the repair remains implemented and deterministically verified.
- Accurate pre-repair semantics (correcting the v1 wording): the merge populated one `seen` set from supported claims followed by revised claims; a revised claim whose ID collided with an **already-admitted** ID (a supported claim, or an earlier revised claim) was unconditionally skipped. A claim whose ID matched an **unsupported** claim was not skipped by ID alone — the separate F6-A2-FR2 anti-resurrection check dropped it only when the normalized text also matched. The v1 phrase "supported or unsupported … unconditionally skipped" is therefore superseded.
- `G013_EXACT_CAUSAL_LINK_TO_ID_COLLISION = NOT_ESTABLISHED_FROM_FROZEN_TRACE`: the immutable Attempt-5 g013 record retains only the two finally rendered claims (`claim_audit` `filter_reason=rendered`), `revision_count=1`, and the missing-point error; it does not retain the pre-merge revised-claim payload, so the exact historical drop path (empty generation, ID collision, re-verification rejection, or rendering omission) cannot be reconstructed. The repair fixes a real generic silent-loss mechanism consistent with the observed g013 failure signature; the trace does not prove it was the exact historical cause. The generic repair's validity is not weakened by this boundary.

## 3. Workstream B — coverage false acceptance: structural strengthening separated from scientific proof

- `STRUCTURAL_COVERAGE_CONTRACT_WEAKNESS = CONFIRMED`, but narrower than any "no per-point completeness semantics" reading: the pre-repair `ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT` already instructed the reviewer to judge each point's explicit obligation against the supported relevant mapped claims collectively, that mapping relevance alone does not imply completeness, and to return every incomplete point. The structural weakness was that the response schema represented completeness only indirectly (`missing_answer_point_ids` plus claim mappings) and required no explicit per-runtime-point record identifying supporting claims and a `complete` flag that could be checked for structural consistency.
- `EXPLICIT_PER_POINT_COMPLETENESS_CONTRACT = IMPLEMENTED` (`answer_point_coverage = {answer_point_id, supporting_claim_ids, complete}`); `DETERMINISTIC_SCHEMA_CONSISTENCY = VERIFIED`.
- `FALSE_ACCEPTANCE_MITIGATION = IMPLEMENTED`; `RUNTIME_SEMANTIC_EFFECT = NOT_YET_SCIENTIFICALLY_VALIDATED`: the deterministic validator cannot prove semantic completeness — a semantically wrong reviewer may still return a structurally self-consistent `complete = true`.
- `G023_G047_EXACT_CAUSAL_LINK_TO_SCHEMA_EXPRESSIVENESS = NOT_ESTABLISHED`. The repair strengthens the reviewer contract against the observed failure class; T1 must determine whether the runtime failure mode is actually improved.

## 4. Workstream C — negative-existence safety: conclusion preserved, scope bounded

- `NEGATIVE_EXISTENCE_CONTRACT_GAP = CONFIRMED`: the pre-repair generation/verification prompts contained no rule forbidding the promotion of absence within a selected non-exhaustive evidence subset into corpus-wide nonexistence (the only adjacent pre-repair rule addressed exact numeric/installation requirements).
- Repair preserved as implemented: generation (non-exhaustive subset → no corpus-wide absence; state only "the supplied evidence does not establish that side") and verification (corpus-wide absence inferred only from a non-exhaustive subset is unsupported; evidence directly establishing the denied thing makes the claim unsupported), with deterministic exact-absence/refusal paths preserved.
- `NEGATIVE_EXISTENCE_CONTRACT_REPAIR = IMPLEMENTED / DETERMINISTICALLY VERIFIED`; `RUNTIME_SCIENTIFIC_EFFECT = NOT_YET_EVALUATED`. T0 prompt-presence tests prove the contract exists, not live model compliance.

## 5. Workstream D — retrieval/rerank role loss: DEFERRED preserved

Re-verified from source and the frozen machine-readable review: `retrieval.py` bounds the reranker input (`rerank_pool = fused_order[:30]`, plus the E3-local `local_rerank_pool = fused_order[:30]`); the frozen review records four g011.e1-matching objects in the combined candidate pool that did not survive into reranked/final top-30, with 143 index-wide matches for the native-documentation role. Counts are quoted only from the frozen machine-readable artifact.

```text
RERANK_ROLE_PRESERVATION_REPAIR = DEFERRED / NO_SAFE_GENERIC_REPAIR_ESTABLISHED
PRODUCTION_E3_PROMOTION = false
```

No quotas, boosts, per-case selectors, retrieval expansion, global reselection, or E3 activation were implemented.

## 6. Product-lineage reconciliation

```text
PREVIOUS_PRODUCT_BEHAVIOR_LINEAGE_HEAD = eda7d932a9b1b7b65436cba01e247859a6f9e056
CURRENT_PRODUCT_BEHAVIOR_LINEAGE_HEAD  = e79d3232ed132a224cbceaf3524e19a1406bd648
```

Verified from Git history. The docs-only closeout commit `6d5d54d771fe56065d60fe2c08b0ce5011f4a343` is not a product-behavior head. The current authoritative planning blocks in `docs/EVALUATION_STATUS.md` and `docs/GENERALIZATION_ROADMAP.md` now carry the corrected lineage; historical lifecycle sections were not rewritten.

## 7. Supersession map for the v1 artifact

`evaluation/POST_A5_GENERIC_PRODUCT_REPAIR.md` / `.json` remain valid for: the implementation diff and generic repair semantics, T0 results, the prompt-fingerprint transition (`35f1dd3c… → 0a5b2909…`), materiality, zero scientific-call accounting, protected-state accounting, Workstream D DEFERRED, and the next validation tier. Superseded by this R1: the Workstream A "supported or unsupported" ID wording and any exact-g013-causality implication; any implication that the pre-repair reviewer had no per-point completeness semantics or that g023/g047 causality is established; the prose-only product-head provenance (now the exact SHA); and the stale lineage bookkeeping in the current planning blocks. A forward pointer has been added to the v1 report without rewriting its historical body.

## 8. Verification performed

1. All changed JSON parses; 2. product commit SHA verified from Git; 3. `e79d323` changed-file inventory verified (2 product files + 7 test files = 9, agreeing with the v1 `files_changed` list); 4. status/roadmap active planning state carries `CURRENT_PRODUCT_BEHAVIOR_LINEAGE_HEAD = e79d323…`; 5. R1 records the g013 / g023-g047 causal boundaries and the not-yet-evaluated scientific effect; 6. Workstream D remains DEFERRED; 7. active Gold `m6-benchmark-v2.11` (`39943c6a…`) and calibration `phase_b_t3_product_language_scope_v8` (selector 59 / 21, `e27ef67a…`) unchanged; 8. no product source file changed; 9. no benchmark/Gold/calibration/evaluator file changed; 10. no scientific execution artifacts produced.

## 9. State and next recommendation

```text
GENERIC_PRODUCT_REPAIR = IMPLEMENTED / DETERMINISTICALLY VERIFIED / SCIENTIFIC EFFECT NOT YET EVALUATED
Attempt 5 = COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED (immutable)
novel_validation = PRISTINE_FOR_CURRENT_LINEAGE; holdout access = 0
protected-content leakage = 0; F6-B execution = 0
candidate frozen = false; Attempt 6 preregistered = false; Attempt 6 executed = false
ATTEMPT_6_READINESS = NOT_READY
NEXT_TASK_RECOMMENDATION = POST-A5 PRODUCT REPAIR VALIDATION / FIXED EXPOSED SENTINEL T1
```

This R1 claims no benchmark improvement and does not authorize T1.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`
