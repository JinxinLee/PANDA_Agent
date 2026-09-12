# F6-A — Pre-Release Validation & Generalization Gate: Preregistration

Frozen before the first scientific model call. No measured outcome values
appear in this document. Machine-readable counterpart:
`evaluation/f6_a_pre_release_validation_preregistration.json`.

## 1. Implementation and candidate identity

- Implementation HEAD at preregistration: `6e92a37` ("Prepare F6-A release
  validation infrastructure", child of `5385d9a` "Align F6 roadmap staged
  status").
- Candidate ID: `f6a-rc1-20260913` (frozen after this preregistration commit;
  the freeze binds this implementation HEAD).
- Runtime mode (primary): `legacy_question_core` (production default;
  `runtime_e1_v2` is explicit-selection-only and is NOT a competing arm).

## 2. Model / prompt / corpus identities

- Generation model: `gemini-3.8-flash`
- Product semantic-verification model: `QA_VERIFICATION_MODEL_ID` absent →
  effective verification model = `gemini-3.8-flash` (same-model architecture;
  distinct F4 client paths)
- Offline evaluation judge: `gemini-3.8-flash` (never used as product
  verifier/composer)
- Embedding: `gemini-embedding-2` / 3072 dimensions / location per env
- Prompt set: version `3.10.1`, `prompt_hash = 23d73b036646ec62f3095fac4bdfafdfc7ecf6676fd27d18475b86773db4e6d5`
- Index fingerprint: `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`
  (collection `panda_knowledge_v1`)
- Packages: python 3.13.14, panda-research-qa-agent 0.1.0, google-genai 2.13.0,
  langgraph 1.2.11, psycopg 3.3.4, qdrant-client 1.19.0
- Docker contract: Option A — release-critical; required compose services
  (postgres, qdrant) must be captured with concrete image identities.

## 3. Dataset identities and roles

| Dataset | Identity | Role |
| ------- | -------- | ---- |
| Gold | m6-benchmark-v2.6, 120 questions, dataset_sha256 `6f12d54b…` (manifest record aligned to the authorized D4-A2-R1 g021 correction) | EXPOSED_BENCHMARK_REFERENCE |
| novel_dev | novel-v1-dev-0.3.0, 28 questions | EXPOSED_DEVELOPMENT_GENERALIZATION_DIAGNOSTIC (aggregate diagnostics only) |
| novel_validation | novel-v1-validation-0.2.0, 15 questions / 15 families, all representative (verified from manifest) | CANDIDATE_LEVEL_PRE_RELEASE_GENERALIZATION_GATE — PRISTINE_FOR_CURRENT_LINEAGE (no case-level question/Gold/outcome material has been used to guide behavior in this lineage; historical run records state `novel_validation = UNSEEN`) |
| novel_holdout | panda-novel-holdout-v1, FROZEN_SEALED, 13, externally managed, outcome_observed=false | metadata only in F6-A; no package discovery/mounting/access |

## 4. Run IDs (fresh, immutable)

```text
f6a-rc1-gold-full-20260913
f6a-rc1-gold-ablation-full-20260913
f6a-rc1-novel-dev-full-20260913
f6a-rc1-novel-validation-full-20260913
f6a-rc1-composer-audit-20260913
```

## 5. Release score formula

For each complete case:

```text
if expected_status == answered: case_release_score = answer_point_coverage
else: case_release_score = 1.0 if expected_status_correct else 0.0
release_score = mean(case_release_score over complete cohort)
```

None is never zero: a missing required metric makes the case incomplete and it
is excluded from the numerator AND denominator while being reported by ID;
exceptions are counted as hard completion failures; denominators are always
reported. Implemented by `evaluation_runner.f6a_release_score`.

## 6. Gold absolute quality thresholds (preregistered)

```text
gold_recall_at_10 >= 0.95
final_evidence_recall >= 0.90
critical_final_evidence_recall == 1.00
intent_accuracy >= 0.90
per_intent_gold_recall_at_10 >= 0.75
per_intent_intent_accuracy >= 0.80
expected_status_accuracy >= 0.975
citation_integrity == 1.00
wrong_version_evidence_count == 0
forbidden_evidence_count == 0
required_source_coverage_answered >= 0.97
identifier_hallucination_rate < 0.03
paper_code_dual_source_rate == 1.00 when applicable
answer_point_coverage >= 0.90
critical_answer_point_miss_count == 0
contradiction_count == 0
major_unsupported_claim_count == 0
unhandled_exception_count == 0
```

Evaluator semantics and denominators are the current runner's; no metric is
redefined post hoc. The historical hidden-acceptance M6 gate itself is not
claimed as a release gate; its metric thresholds are reused as this exposed
Gold contract.

## 7. Cross-cohort hard safety invariants

For Gold, novel_dev, and novel_validation where applicable:

```text
citation_integrity == 1.0
wrong_version_evidence_count == 0
forbidden_evidence_count == 0
contradiction_count == 0
major_unsupported_claim_count == 0
critical_answer_point_miss_count == 0
unhandled_exception_count == 0
```

Plus: no release-record corruption, no mixed candidate identities, no missing
scheduled case. A novel_dev hard-safety failure stops before novel_validation.

## 8. Generalization Gap

```text
GENERALIZATION_GAP = Gold_v2.6_release_score - novel_validation_release_score
GENERALIZATION_GAP <= 0.10
```

All 15 validation cases are representative (verified from the manifest);
secondary diagnostics reported without substituting the primary score:
Recall@5/@10/@20 gaps, MRR gap, final-evidence-recall gap,
answer-point-coverage gap, expected-status-accuracy gap.

## 9. Benchmark Dependency

```text
BENCHMARK_DEPENDENCY = Gold_primary_release_score - Gold_ablation_release_score
BENCHMARK_DEPENDENCY <= 0.05
```

Negative values pass. No novel_validation ablation (validation exposure budget
is never spent on model/config selection).

## 10. Ablation definition (preregistered, evaluation-only)

```text
ablation_id = disable_query_expansion_injection
mechanism = runtime overlay in the isolated ablation process
  (panda_agent.f6a_ablation.install): Retriever.load_query_expansions returns
  an empty rule set, disabling the D4-owned reviewed YAML trigger-rule layer
  (matched symbols/concepts/repositories/page hints)
unchanged: qa, prompts, models, retrieval policies, index, runtime mode
recorded in: evaluation/f6a_ablation_manifest.json
```

Static justification: F1/PF-LR1 retired the F2/F3 benchmark-shaped semantics
and fixed locators; the remaining approved compatibility/shortcut surface in
the production retrieval path is the reviewed query-expansion trigger-rule
layer, whose triggers are benchmark-domain phrases. Generic/domain mechanisms
are not classified as shortcuts. The overlay is evaluation-only and isolated;
the primary candidate is not mutated.

## 11. Composer release audit contract

- Eligible pairs: ANSWERED + composer attempted AND accepted + >= 2 verified
  claims, drawn from the frozen Gold + novel_validation records (no product
  rerun; no holdout).
- Factuality: offline judge decides whether the composed answer introduces any
  content unsupported by the verified claims.
  `composer_new_fact_rate == 0` — else
  `COMPLETE / FAIL / COMPOSER_FACTUALITY_GATE_FAILED`.
- Readability: blinded pairwise A/B (deterministic counterbalance by the first
  embedded case-ID number; even → composed labeled A), judge readability/
  organization only. Gate: `eligible_pairs >= 10 AND composed_preferred >
  deterministic_preferred`; fewer than 10 pairs →
  `COMPLETE / INCONCLUSIVE / COMPOSER_READABILITY_EVIDENCE_INSUFFICIENT`;
  deterministic preferred at least as often →
  `COMPLETE / FAIL / COMPOSER_READABILITY_GATE_FAILED`.
- Diagnostics reported: attempt/accept/fallback counts and rates.

## 12. Fail-fast ordering

A2 (Gold primary) → if any Gold completion/hard-safety/absolute-quality gate
fails: `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`, stop.
A3 (ablation) → `BENCHMARK_DEPENDENCY > 0.05` →
`COMPLETE / FAIL / BENCHMARK_DEPENDENCY_GATE_FAILED`, stop. A4 (novel_dev) →
hard-safety failure → FAIL, novel_validation preserved unrun; ordinary weak
diagnostics are reported honestly and the run continues. A5 (novel_validation)
→ completion/hard-safety/gap failure →
`COMPLETE / FAIL / NOVEL_VALIDATION_PRE_RELEASE_GATE_FAILED`. A6 (composer
audit) → terminal states per §11. A7 (gate decision) aggregates.

## 13. Infrastructure interruption / resume

Same run ID + same candidate identity + same preregistration + no behavior
change + completed records reused. If complete evidence cannot be obtained:
`COMPLETE / INCONCLUSIVE / INFRASTRUCTURE_INCOMPLETE`. Evaluator defects after
outcomes: immutable offline rescore only (documented provenance, no threshold
change), else INCONCLUSIVE.

## 14. Usage accounting

Exact actual totals recorded per run and per stage (Gold primary, Gold
ablation, novel_dev, novel_validation, composer audit, external judge, product
generation/verification/composer roles where available, latency). Primary and
ablation totals are never mixed.

## 15. Valid terminal outcomes

```text
COMPLETE / PASS / HOLDOUT_ELIGIBLE
COMPLETE / FAIL / <specific failed gate>
COMPLETE / INCONCLUSIVE / <specific evidence gap>
HOLD / PRE_RELEASE_PRECONDITION_NOT_MET (pre-outcome only)
```

## 16. No-holdout boundary

F6-A never discovers, mounts, or accesses the protected holdout package or its
cases; holdout metadata (identity/count/status/flags) is repository-visible
only. Gate semantics: with no candidate frozen, `candidate_changes_after_freeze`
is NOT_REACHED, never PASS. Post-freeze immutability: zero behavior-changing
edits until the F6-A verdict; candidate identity is verified before each
primary stage; run artifacts may leave the working tree dirty without
invalidating the frozen identity (verification checks immutable behavior
identity and the frozen implementation HEAD).

## 17. E3 opportunistic evidence

Naturally occurring only (legacy_question_core does not trigger E3; expected
applicability 0). No dedicated cohort; E3 recovery benefit remains UNRESOLVED
unless a pre-existing authoritative threshold is naturally satisfied.
