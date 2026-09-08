# E1 Architecture Review

## Decision

COMPLETE / PASS / REVISED_SEMANTIC_ANSWER_POINT_CONTRACT_ESTABLISHED.

One E1 answer point represents one explicitly requested response obligation that can be independently satisfied and whose omission can be independently detected. Its semantic text and question grounding matter; exact agreement with a facet ontology does not establish whether that obligation exists or is covered. Adopt type-independent identity and optional diagnostic taxonomy for a future separately authorized repair.

**E1-A2 remains FAIL under its frozen preregistered contract.** Its G7/G8 failure was legitimate. This review neither regrades that experiment nor implements or validates a repaired decomposer. E1-AR PASS applies only to the coherence and evidence basis of this architecture decision.

## Starting lifecycle state

Actual starting HEAD: `33173907ecf3d5313868a50c8549721564f5c16f` (`E1-A2 close decomposition validation`); clean worktree. E1-A1 accepted as a diagnostic implementation. E1-A2 COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED. E1 IN_PROGRESS / VALIDATION_FAILED; Phase E IN_PROGRESS / E1. D4 PAUSED / ROADMAP_RECONCILIATION, overall completion UNDECIDED. F1 accepted; Phase F IN_PROGRESS / F1_COMPLETE. The expected lifecycle matched current repository evidence.

## Evidence reviewed

- `AGENTS.md`, `docs/EVALUATION_POLICY.md`, current status and E1/E2/E3 roadmap cards.
- `src/panda_agent/question_decomposition.py`, especially the required taxonomy, exact support validation, type-dependent sorting and facet-local IDs.
- E1-A1 machine-readable contract and implementation report.
- E1-A2 preregistration, all 24 frozen manifest cases and persisted case records, aggregate result, and final scientific report. Preregistration identity: `77ea6bc27beb1657673e57be763b05419c98bc05`.

The static calculation uses Python's standard JSON/collection facilities only; it does not import or execute the evaluation runner or decomposer. It confirms exact question/reference equality between manifest and records, valid support spans, one-to-one matched IDs, and the stored type flags. Diagnostic counts reuse preserved semantic matches rather than creating new judge decisions. Pair-level interpretation below also inspects the original raw questions and predicted need text.

No benchmark/novel source dataset was reopened. No protected validation/holdout content was accessed. No tests, provider calls, hashes or scientific reruns were performed. JSON parsing, direct count reconciliation, Git path scope checks and `git diff --check` provide static verification.

## What E1 is actually responsible for

An answer point is explicit, grounded in the question, independent of retrieved evidence, independently satisfiable, and independently checkable for omission. The unit is a requested response obligation, not a retrieved passage, answer fact, source quota, benchmark requirement, hidden prerequisite, inferred workflow stage, or grammatical clause.

The practical question is: can an answer satisfy one explicitly requested obligation while leaving another unaddressed? If so, those obligations need independently addressable points. This criterion applies at the level of the user's request; it does not recursively split every factual ingredient of an eventual answer.

## E1-A2 failure decomposition

Categories overlap. `SEMANTIC_SLOT_OMISSION` below means an independently addressable frozen slot is unmatched; it does not automatically mean the broad prediction failed even to mention that need.

| Pair / case-record lines | Independent finding | Diagnostic categories |
|---|---|---|
| pair05 / lines 9–10 | Both variants merge the two separately requested model implementation locations into one locator point. Each matches 1/2 references. Knowing one location does not discharge the other obligation. | SEMANTIC_GRANULARITY_MERGE; SEMANTIC_SLOT_OMISSION |
| pair06 / lines 11–12 | Both producer and consumer identity needs are fully recovered in both variants (4/4 matches). Predictions use `data_flow`; references use `locator`. Need text is equivalent despite four label disagreements. | TAXONOMY_BOUNDARY_DISAGREEMENT |
| pair07 / lines 13–14 | All three slots are recovered in both variants (6/6 matches). Encoded pairs/paths use `implementation` versus reference `constraint`; assigned variables use `implementation` versus `api_behavior`. The unmatched-input slot changes from `api_behavior` in base to `mechanism` in paraphrase. Five label disagreements, one cross-variant label transition. | TAXONOMY_BOUNDARY_DISAGREEMENT; PARAPHRASE_TYPE_DRIFT |
| pair08 / lines 15–16 | Approach identification and comparison are complete in both variants (4/4 matches). The paraphrase changes only the identification label from `definition` to `implementation`, creating one disagreement. | TAXONOMY_BOUNDARY_DISAGREEMENT; PARAPHRASE_TYPE_DRIFT |
| pair09 / lines 17–18 | Both variants identify the leftover-hit task but merge the two explicitly requested downstream contributions. Each matches 2/3 references; one separately addressable contribution remains missing. The matched contribution uses `mechanism` versus reference `workflow`, adding two label disagreements. | SEMANTIC_GRANULARITY_MERGE; SEMANTIC_SLOT_OMISSION; TAXONOMY_BOUNDARY_DISAGREEMENT |

The line numbers refer to `e1_a2_dynamic_question_decomposition_validation_cases.jsonl`. Exact case/slot/prediction IDs, reference labels, predicted labels and line references are retained in the new review JSON.

Overall: 12 type disagreements among 40 semantic matches, affecting 7 cases in 4 pairs; 2 label transitions in 2 pairs; 4 granularity-failure cases in 2 pairs, leaving 4 unmatched independent slots. Five otherwise semantic-complete cases fail only the label condition; the two pair09 variants contain both label and granularity problems. None of the label disagreements changes which need the matched text identifies, although pair09 still merges an additional need into that point.

All four unmatched references occur in broad texts that mention both objects/stages. Thus the evidence establishes a real omission of separate addressability, not four independent examples of entirely unexpressed content. No additional standalone unexpressed information need is established by this inspection. Hidden prerequisites = 0; structural failures = 0. Failure is concentrated in taxonomy boundaries and multi-obligation granularity, not observed structural unreliability or widespread invented requirements.

## Answer-point atomicity

Split explicit obligations that may be satisfied or omitted independently. “Where are X and Y implemented respectively?” requests two locations; “What does each of X and Y contribute?” requests two contributions. An answer can correctly provide one and omit the other, so one broad point conceals an independently detectable omission.

Keep “How do X and Y differ?” as one comparison obligation: the relation is the requested unit. Likewise, “How does data move from A to B?” normally requests one end-to-end flow; do not invent unnamed handoffs. An explicit additional ask may warrant another point. Multiple entities, a conjunction, or a clause boundary alone is not sufficient to split.

Future repair should teach this generic semantic distinction, with synthetic contrasting examples. Do not introduce runtime triggers for “respectively”, “each”, or their Chinese equivalents, entity-specific rules, benchmark case templates, or inferred domain stages. Preserve the 1–5 bound; this small cohort does not establish behavior for requests exceeding that capacity, and this review does not design an overflow policy.

## Facet taxonomy decision

`facet_type` is not part of the authoritative semantic correctness contract. It may remain optional diagnostic metadata. It must not determine whether an obligation exists, whether a matched need is covered, the point's identity, or primary E1 acceptance. Downstream exact-label dependence would require a separate experiment establishing concrete utility.

The ten existing categories mix the object of a request with ways of describing it: locating a producer also concerns data flow; describing script behavior can be called implementation, mechanism or API behavior. The preserved semantic matches directly show this ambiguity. Neither reference nor predicted labels are presumed universally correct outside the old experiment. Labels can be useful for analysis without becoming a prerequisite for completeness.

Retain the taxonomy in current code during this review. Its optional representation and handling belong to E1-R1. Diagnostic label changes or absence must not invalidate an otherwise valid semantic point or change ordering/identity in the repaired design. Semantic decomposition quality and taxonomy-label agreement remain separate measurements.

## Point identity decision

Recommend `point.1`, `point.2`, `point.3`, assigned by code after deterministic question-order normalization. The model does not generate IDs. IDs are unique within the current decomposition trace and contain no taxonomy, hashes, UUIDs or randomness. Cross-paraphrase literal ID equality is not required; changed wording can change question order.

Current E1-A1 uses facet type both as a sort tie-break and in the ID prefix/ordinal. Merely changing the prefix would leave diagnostic metadata influencing order. E1-R1 should remove both dependencies: use earliest support position and deterministic type-independent tie-breaking, such as normalized point text with existing duplicate protection. A label-only change must leave ordering and IDs unchanged for an otherwise identical question/proposal. These IDs are local trace references, not permanent semantic identities across regenerated or edited decompositions.

## Support-span and ambiguity decisions

Retain exact non-empty substrings from the raw question: E1-A2 had 24/24 valid decompositions and no support-span failures. This mechanism supplies question-grounding provenance, not a proof of semantic adequacy; the merged obligations in pairs05/09 passed it. Core fields are `answer_point_id`, `text`, and `support_spans`. They identify the obligation and its lexical grounding; optional type metadata does not govern their validity.

Ambiguity remains diagnostic only. Do not turn it into refusal, QA status, retrieval triggering or automatic clarification. The zero ambiguity observations in this small cohort do not establish general ambiguity-handling quality.

## Static counterfactual diagnostics

These are **COUNTERFACTUAL / ARCHITECTURAL DIAGNOSTICS ONLY**, not acceptance results or a new scientific run. They reuse the existing judge's semantic matches without changing any reference, predicted point, missing slot, extra point or threshold.

| Diagnostic | Definition | Verified observation |
|---|---|---:|
| D1 | Valid case, all frozen references matched, no extras; ignore exact type equality only | 20/24 |
| D2 | Both variants satisfy D1 with the frozen semantic slot mapping; no type equality requirement | 10/12 |
| D3 | Existing semantic match with `facet_type_match=false` | 12/40 |
| D4 | Raw question and broad prediction demonstrate merged independently satisfiable obligations, leaving a missing slot | 4 cases / 2 pairs |

D1 excludes b05, p05, b09, p09. D2 excludes pair05 and pair09. D3 includes 4 disagreements in pair06, 5 in pair07, 1 in pair08, and 2 in pair09. D4 is determined from the actual question/prediction text, not by equating every unmatched reference with a taxonomy error.

Historical E1-A2 G8 remains the **strict reference-conformant pair gate**, 7/12. It was not pure semantic paraphrase stability. Architectural D2 is semantic-slot completeness in both variants, 10/12; even it is stricter than mere pairwise similarity, because a pair of consistently incomplete decompositions does not qualify. Two observed label drifts are not evidence of two semantic-slot drifts. None of these diagnostics makes E1 or E1-A2 PASS; removing G7 retroactively is not validation.

## Implications for E2

E2 needs `claim -> requested semantic point -> supporting evidence`. It should consume semantic point IDs/text and evaluate which explicit obligation a claim addresses. It does not inherently need to decide whether the need is a workflow, mechanism, API behavior or implementation. Exact taxonomy must not be a required coverage condition. This is a dependency clarification only: E2 and E3 remain NOT_STARTED, with no implementation or broader redesign here.

## Boundaries retained from E1-A1

Raw-question-only model payload; no retrieval plan/evidence, legacy Gold or benchmark completeness inputs; 1–5 points; exact support spans; code-assigned deterministic unique IDs; no hidden prerequisite inference; shadow diagnostic role; no default QA invocation. Evidence independence remains mandatory even if decomposition later feeds downstream coverage.

Retain current `question_core`, `_answer_requirements`, `_requirement_evidence`, `_deterministic_missing_requirement_ids`, `required_boundary_locators`, and planned locator/data-flow augmentation. They remain compatibility behavior pending validated E1/E2 replacement. The repaired contract would be authoritative only inside the explicitly invoked shadow decomposer, not production completeness.

## What is not being changed

No production source/configuration, tests, E1-A1 implementation, E1-A2 preregistration/manifest/runner/case records/result/report, references, paraphrases or old gates changed. No taxonomy deletion, model/QA/judge execution, new dataset inspection, E2/E3/F1 cleanup or production activation occurred. Review code is a transient standard-library calculation, not a new repository runner.

All review-task counters are zero: Analyzer calls, Embedding calls, Reranker calls, QA calls, Decomposition calls, Judge calls, Total model calls, Token usage. Historical E1-A2 usage is not new review usage.

## Revised E1 contract

Raw question → question-only decomposition into 1–5 independently satisfiable explicit obligations → deterministic question-order normalization without type dependence → type-independent code-assigned IDs with exact question support spans. Each point carries obligation text; optional `facet_type` and ambiguity remain diagnostic.

Future prospective primary quality dimensions: structural validity, semantic reference-point recall, semantic prediction precision, under-decomposition, over-decomposition, exact point count, semantic-slot paraphrase stability, and hidden-prerequisite inference. Exact facet agreement, taxonomy distributions and facet-label stability become secondary diagnostics. No new numeric thresholds are set here; the existing experiment's gates remain immutable.

This is an architectural recommendation supported by a small exposed cohort and its original judge matches. Reference authorship and single-model judging limitations remain; source/language confounding prevents causal generalization conclusions. A future implementation and fresh prospective revalidation are still required.

## Lifecycle decision

E1-AR = COMPLETE / PASS / REVISED_SEMANTIC_ANSWER_POINT_CONTRACT_ESTABLISHED.
E1-A2 = COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED.
E1 = IN_PROGRESS / ARCHITECTURE_REVIEW_COMPLETE / REPAIR_REQUIRED.
Phase E = IN_PROGRESS / E1.

D4 remains PAUSED / ROADMAP_RECONCILIATION, overall completion UNDECIDED. F1 remains COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED. Phase F = IN_PROGRESS / F1_COMPLETE. E2 = NOT_STARTED; E3 = NOT_STARTED; production activation = false.

## Next task recommendation

E1-R1 — Semantic Answer-Point Contract Repair: implement semantic obligation atomicity, type-independent ordering/IDs, non-authoritative optional taxonomy, retained question-only/support-span/shadow boundaries, and focused T0 checks. No live validation in that proposed implementation task. E1-R1 is not executed or authorized by this review.

After a separately authorized successful E1-R1, recommend E1-R2 — Prospective Semantic Answer-Point Revalidation, separately preregistered with a fresh prospective acceptance cohort. E1-A2 cases may serve as exposed regression diagnostics but cannot be the sole acceptance cohort. No full E1-R2 design or thresholds are set here.

NEXT_TASK_EXECUTION_AUTHORIZED = false. Stop after the architecture-review commit.
