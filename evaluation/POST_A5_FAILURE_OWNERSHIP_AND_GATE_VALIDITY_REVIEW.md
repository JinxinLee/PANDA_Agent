# Post-Attempt-5 Failure Ownership & F6-A Gate Validity Review

Status: `COMPLETE / PASS / FAILURE_OWNERSHIP_AND_GATE_VALIDITY_ESTABLISHED`

Zero scientific calls. Machine-readable companion: `evaluation/post_a5_failure_ownership_and_gate_validity_review.json`.

## 1. Scope and method

This review reconstructs, from immutable Attempt-5 stored records, traces, diagnostics, Gold v2.10, the locked-corpus object index, and the evaluator source, the earliest causal loss point for every mandatory Attempt-5 failure, and assesses whether the three failed gates measure the constructs they intend. No product, evaluator, Gold, or threshold was changed. Attempt 5 remains `COMPLETE / FAIL / EXPOSED_BENCHMARK_PRE_RELEASE_GATE_FAILED`.

## 2. The previous undersplitting hypothesis is rejected

The working hypothesis entering this review — that the four critical answer-point misses are caused by QuestionDecomposer under-splitting — is **rejected for all four cases**:

- `g013`: the decomposer produced exactly three obligations mapping onto all three Gold points (p1 terminal setup, p2 macro invocation, p3 master-run-task lifecycle). No under-splitting.
- `g023`: one obligation ("How to use PndMasterRecoTask in the generic workflow") is faithful to the literal question. The Gold position detail (after digitization, before PID) is rubric detail inside that obligation; the production contract intentionally keeps an end-to-end workflow as one obligation.
- `g039` / `g047`: each has exactly one Gold critical answer point; a single-obligation decomposition cannot under-split a single-point rubric.

Attempt-5 decomposition behavior was healthy overall: points-per-question distribution 1:52, 2:4, 3:2, 4:1; zero decomposition failures; no refusal regressions.

## 3. Critical answer-point misses (ownership)

| Case | Earliest causal loss | PRIMARY | Layer |
| --- | --- | --- | --- |
| `g013.p3` | Runtime coverage correctly detected `point.3` missing (`verification_errors: ["missing answer point point.3"]`) and one bounded revision ran, but produced no p3 claim although the directly supporting evidence (`macro/master/Readme.md`: "Master run and Master Tasks … provide default settings and operation modes") was already in the final citation set. Attempt 4 failed identically, there with the explicit statement that the evidence does not document internal lifecycle stages. | PRODUCT_DEFECT | A1 (revision/compensation insufficiency; secondary: thin corpus detail for "orchestrates the event loop") |
| `g023.p3` | Both critical Gold evidence groups were selected (crit-ev 1.0) and three supported claims were composed (definition, instantiation, options) — but none states the task's workflow position. Attempt 4, same Gold, answered the position explicitly ("reconstruction takes place after simulation and digitization and is followed by PID") and passed. | PRODUCT_DEFECT | A1 (content gap inside the obligation; secondary: coverage-review granularity — the claim self-declared `point.1`, so revision never triggered) |
| `g039.p1` | The answer correctly locates `efficiency_correction_2.C` (crit-ev 1.0; judge: both claims supported). The miss comes from the Gold rubric clause "distinguish it from PndLmdAcceptance" inside the critical point — anti-confusion detail not independently requested by the literal "Where is X implemented?" question, and separately guarded by `forbidden_evidence` (data/PndLmdAcceptance.cxx). Attempt 4 passed with an "unlike angular acceptance…" contrast that also never named PndLmdAcceptance — judge latitude exists. | GOLD_CONTRACT_DEFECT | GOLD |
| `g047.p1` | The pinned Pflueger pages were finally cited (crit-ev 1.0; all claims judged supported), but the answer never relates the elastic differential cross section to luminosity extraction. Attempt 4, same Gold, stated that relation explicitly and passed. | PRODUCT_DEFECT | A1 |

Three-mechanism separation (per protocol §9): `g023`/`g047`/`g013` are "one obligation exists, but the answer content inside it is incomplete" (A1); `g039` is "Gold rubric contains implicit detail not independently requested by the literal question" (GOLD). No case is "semantic obligation missing" (D1).

## 4. Critical final-evidence misses (ownership)

The metric measures whether each **benchmark-author-pinned critical evidence group** literally appears in the **final answer's citation set** (with same-path/descendant extension). Stage-by-stage reconstruction:

| Case | Missing group | Selected-stage state | Earliest loss | Equivalent alternate source? | PRIMARY |
| --- | --- | --- | --- | --- | --- |
| `g011` | e1 + e2 | e1: 4 matching objects in the combined pool (incl. `docs/Installation/Install_PandaRoot.rst` chunks) fell out of rerank and top30 entirely; e2: selected, then dropped from citations | **R2** | **No** — e1 (native install path) is a genuinely necessary information role, and the answer asserts "the supplied locked documentation does not detail an independent native setup procedure", which the indexed corpus (67+ matching objects) directly contradicts — a V2 false acceptance on top | PRODUCT_DEFECT (R2; secondary V2, composer convergence) |
| `g013` | e1 (sphinx Macros page) | 5 matching objects selected, none cited | composer/A1 source choice | Yes — same content answered from `mastermacros.rst` / `Readme.md` | GOLD_CONTRACT_DEFECT |
| `g016` | e1 (DPMGenerator doc page) | 4 matching objects selected, none cited | composer/A1 source choice | Yes — answer gives complete API + mode semantics from code | GOLD_CONTRACT_DEFECT |
| `g020` | e1 (`macro/target/README.md` readme_section) | pinned-file object selected; final claims cite the **repo-root README** ("3.4 POCA-first back-propagation") plus code | composer/A1 source choice | Yes — all four critical APs covered (`crit_pts_missing = []`) | GOLD_CONTRACT_DEFECT |
| `g044` | e1 (Pflueger p57/58/62) | one Pflueger object selected, final citations are li_2026 thesis p72/79 + curated | composer/A1 source choice | Yes — AP says "using the thesis, not source-code inference"; li_2026 is a thesis; same failure in Attempts 3/4/5 | GOLD_CONTRACT_DEFECT |
| `g110` | e2 (`macro/target/README.md` readme_section) | pinned-file object in pool; citations use repo-root README + code | composer/A1 source choice | Yes — three-step triage covers all three APs | GOLD_CONTRACT_DEFECT |

Five of six misses are the same construct gap: content-equivalent authoritative sources satisfy the user need while the gate demands a pinned literal group. The repository itself previously acknowledged this: the signed v2.5/v2.6 adjudication contracts contain seventeen `final_evidence_equivalence` human adjudications (including g011 and g060) precisely for this literalness; v2.9/v2.10 carry no adjudication file, so the same literalness re-exposed. `g011` is the one genuine product failure this gate caught — which is why the gate must be redefined, not deleted.

## 5. Identifier hallucinations: all six events are evaluator false positives

Corpus verification of every alleged hallucinated identifier:

| Event | Verdict | Evidence |
| --- | --- | --- |
| `LumiFit::THETA_X` (g060) | EVALUATOR_DEFECT (false positive) | literal string in 48 corpus objects, **including the very evidence object the claim cites** (`model/PndLmdModelFactory.cxx`) |
| `LumiFit::THETA_Y` (g060) | EVALUATOR_DEFECT (false positive) | literal string in 13 corpus objects (`LumiFitStructs.h`, factory code) |
| `LumiFit::MC` (g113) | EVALUATOR_DEFECT (false positive) | literal string in 53 objects; **both cited `runLmdFit.cxx` evidence objects contain it verbatim** |
| `LumiFit::MC_ACC` (g113) | EVALUATOR_DEFECT (false positive) | 37 objects; cited evidence contains it |
| `LumiFit::RECO` (g113) | EVALUATOR_DEFECT (false positive) | 39 objects; cited evidence contains it |
| `LumiFit::THETA_X` (g113) | EVALUATOR_DEFECT (false positive) | cited evidence contains it |

Root cause (deterministic, in `build_identifier_catalog`): the symbol catalog collects `locator.symbol` plus `class/struct/enum <Type>` declaration names only. Namespace **enum members** such as `LumiFit::THETA_X`/`MC`/`MC_ACC`/`RECO` are never catalogued, and the `::` base-name fallback also only checks catalog symbols. There is no qualification-only error and no invented symbol: `LumiFit::` is a real namespace in the corpus, and the alleged hallucinations are real enum members. Attempt 4 recorded the same two g060 events (rate 0.0116, passed); Attempt 5's g113 answer enumerated runLmdFit filters/track types more specifically, adding four false-positive events and crossing the threshold.

## 6. Gate construct validity

### 6.1 `critical_final_evidence_recall == 1.00`

- INTENDED_CONSTRUCT: every critical user-required source role represented in final support (interpretation A).
- MEASURED_CONSTRUCT: interpretation B — each pinned critical group must literally appear in final evidence; no semantic source equivalence.
- SAFETY_OR_QUALITY: quality (completeness/provenance).
- STOCHASTIC_SENSITIVITY: high — A4 failed {g011, g013, g037, g044, g059} vs A5 {g011, g013, g016, g020, g044, g110} on the same Gold; citation-source choice varies between runs.
- DEPENDENCE_ON_GOLD_LITERALITY: high (five of six A5 misses are equivalent alternates).
- HISTORICAL_VARIATION: STABLE_FAIL — 0.8231 / 0.8912 / 0.9410 / 0.9286 / 0.9184 across five attempts, three Gold versions, two product modes; never 1.00.
- THRESHOLD_ORIGIN: INHERITED_HISTORICAL_CONSTANT (frozen M6 hidden-acceptance constant from the root commit; no derivation recorded; UNKNOWN beyond that).
- CURRENT_DISPOSITION: **REDEFINE_METRIC_REQUIRED** — distinguish "uniquely necessary source roles" (keep literal) from "one acceptable source among several equivalent authoritative sources" (accept verified equivalence), consistent with the historical adjudication precedent. Not silently redefined here.

### 6.2 `critical_answer_point_miss_count == 0`

- INTENDED_CONSTRUCT: no critical user obligation left uncovered.
- MEASURED_CONSTRUCT: external-judge semantic coverage against Gold point texts, which can embed anti-confusion rubric detail not requested by the literal question (g039).
- SAFETY_OR_QUALITY: quality/completeness — **currently misclassified inside `hard_safety_invariants`** (see §7).
- STOCHASTIC_SENSITIVITY: medium (judge latitude exists; A4→A5 deltas track real content differences).
- DEPENDENCE_ON_GOLD_LITERALITY: medium-high (g039 clause; the other three cases are genuine gaps).
- HISTORICAL_VARIATION: STABLE_FAIL — 18 / 4 / 3 / 2 / 4; never 0.
- THRESHOLD_ORIGIN: INHERITED_HISTORICAL_CONSTANT (root-commit M6 acceptance constant; the safety framing was added by F6-A preregistrations, the value was not).
- CURRENT_DISPOSITION: **GOLD_RECONCILIATION_REQUIRED** — the g039-type rubric contamination needs a forward-only Gold correction; the gate itself remains meaningful for genuine content gaps (g023/g047/g013).

### 6.3 `identifier_hallucination_rate < 0.03`

- INTENDED_CONSTRUCT: the model must not invent identifiers absent from the locked corpus.
- MEASURED_CONSTRUCT: deterministic membership in an incomplete catalog; enum members are invisible.
- SAFETY_OR_QUALITY: quality leaning safety (fabricated symbols undermine trust); the construct itself is sound.
- STOCHASTIC_SENSITIVITY: high in count terms (2 events → 6 events across attempts with the same defect, purely through more specific generation content).
- DEPENDENCE_ON_GOLD_LITERALITY: none (deterministic, Gold-independent).
- HISTORICAL_VARIATION: RECENT_REGRESSION (0.0 / 0.0 / 0.0 / 0.0116 / 0.0462) — but the A5 regression is 100% evaluator false positives.
- THRESHOLD_ORIGIN: INHERITED_HISTORICAL_CONSTANT (root-commit M6 constant; the M6 retrospective shows it in use with no derivation; numeric basis UNKNOWN).
- CURRENT_DISPOSITION: **EVALUATOR_REPAIR_REQUIRED** — the only confirmed objective measurement defect; repairable offline with zero model calls.

## 7. Hard-safety classification coherence

The current `hard_safety_invariants` mix two conceptually different categories:

- Trustworthiness/harm invariants (coherent as safety): `citation_integrity`, `wrong_version_evidence_count == 0`, `forbidden_evidence_count == 0`, `contradiction_count == 0`, `major_unsupported_claim_count == 0`, `unhandled_exception_count == 0`.
- `critical_answer_point_miss_count == 0` is a **completeness/release-quality** criterion: a missing answer point makes an answer incomplete, not untrustworthy or harmful. It does not belong in the same conceptual category.

No policy or threshold was changed here; re-categorization is recommended for a later authorized task.

## 8. Historical gate stability (Attempts 1–5)

Comparability: A1/A2 share Gold v2.6; A4/A5 share Gold v2.10; A3 (v2.9, 58/59 scored, g013 Vertex-429 INCOMPLETE) is a separate Gold. Cross-version value comparisons are benchmark-confounded.

| Class | Gates |
| --- | --- |
| STABLE_PASS | gold_recall_at_10, intent_accuracy, per_intent_gold_recall_at_10, per_intent_intent_accuracy, citation_integrity, wrong_version_evidence_count, forbidden_evidence_count |
| STABLE_FAIL | critical_final_evidence_recall (5/5), critical_answer_point_miss_count (5/5) |
| VOLATILE | final_evidence_recall, expected_status_accuracy, required_source_coverage_answered, answer_point_coverage, contradiction_count, major_unsupported_claim_count, unhandled_exception_count |
| RECENT_REGRESSION | identifier_hallucination_rate (only same-Gold A4→A5 pass→fail; 100% evaluator false positives) |
| NOT_COMPARABLE | paper_code_dual_source_rate (applicable set flipped by the forward-only g060 v2.10 contract change: denominator 1 → 0, vacuous PASS) |

## 9. Threshold origin audit

All 18 mandatory thresholds are INHERITED_HISTORICAL_CONSTANT: present verbatim in the root commit `3d90848` as the "frozen M6 acceptance thresholds", explicitly re-declared as reused by the F6-A preregistrations, and never recalibrated across attempts. No repository artifact derives any numeric value; the pre-repository M6 origin is UNKNOWN. `docs/EVALUATION_POLICY.md` contains no numeric thresholds and no derivations. The three failing thresholds share this origin: `critical_final_evidence_recall == 1.00` (M6 `critical_evidence_coverage == 1.0`), `identifier_hallucination_rate < 0.03` (M6 retrospective table value, no derivation), `critical_answer_point_miss_count == 0` (M6 `critical_answer_points == 0`, later given safety framing by preregistration).

## 10. Confirmed defects

### Product defects (generic; no Gold IDs/answers/paths in the repair hypotheses)

1. **Obligation-content coverage gap (A1).** Runtime coverage review accepts a claim's self-declared obligation mapping as coverage, so content gaps inside an obligation are invisible to revision; when a gap is detected (g013-type), one bounded revision may still fail to emit a claim despite supporting evidence already cited. Affected: `g013.p3`, `g023.p3`, `g047.p1`. Minimum test: deterministic coverage unit test + revision-with-evidence test.
2. **Document-role rerank loss with negative-existence false acceptance (R2/V2).** Role-matching documentation objects exist in the combined pool but fall out of rerank/top30 while adjacent operational pages dominate; the generator then asserts a corpus-negative existence claim contradicted by the uncited corpus, and the verifier accepts it. Affected: `g011`. Minimum test: corpus-negative-claim rejection test + stored-trace role-preserving rerank replay.

### Evaluator defects

1. **Identifier catalog omits namespace enum members** (and any non-`locator.symbol`, non-type-name symbol), classifying verbatim corpus identifiers as hallucinations. Affected: all six Attempt-5 events. Forward-only repair: deterministic catalog extension / text-presence fallback; offline rescore of stored Attempts 1–5 metrics with zero model calls; no new scientific execution needed for this metric.

### Gold defects

1. **g039.p1 rubric clause** ("distinguish it from PndLmdAcceptance") exceeds the literal question. Forward-only governance fix; re-decision over stored answers would be a bounded judge re-evaluation (contract reconciliation), not a product attempt.

### Stochastic cases

None qualify under the strict criteria (cross-candidate differences are not within-candidate stochastic variation). The five equivalent-source misses are recorded as generation citation-source preference amplified by the gate's literal construct, not as stochastic variance.

## 11. Counterfactuals (COUNTERFACTUAL / NON-AUTHORITATIVE)

1. With the identifier catalog repaired, Attempt-5 `identifier_hallucination_rate` recomputes to 0/130 = 0.0 — the gate would pass; the other two failed gates remain failed; the Attempt-5 terminal verdict is unchanged.
2. If verified content-equivalent alternates were accepted for g013.e1/g016.e1/g020.e1/g044.e1/g110.e2, `critical_final_evidence_recall` recomputes to 48/49 = 0.9796 — still failing, because g011 is a genuine failure. The gate caught something real.
3. With g039.p1 corrected, `critical_answer_point_miss_count` would be 3 — still failing on genuine content gaps.

Conclusion: every failed gate measured at least one genuine problem; the identifier gate is the only one whose entire A5 failure is measurement defect.

## 12. Attempt-6 readiness

```text
ATTEMPT_6_READINESS = NOT_READY
```

Blockers: unresolved evaluator defect (catalog) and Gold construct issue (g039); a separately authorized redefinition decision for the critical-evidence construct; two confirmed product defects requiring bounded development; no materially new candidate.

## 13. Cost-aware protocol assessment

- `DEVELOPMENT_SENTINEL_SCREEN = RECOMMENDED` — three of five attempts failed on the same two stable gates; a small preregistered development-only sentinel screen would catch stable-gate failures before a full formal run. It must never gate formal outcomes.
- `FORMAL_IRREVERSIBLE_FAILURE_EARLY_STOP = INCONCLUSIVE` — the current fail-fast already stops downstream stages after A1; intra-A1 reachability-based early stop saves tokens only in narrow conditions and has not been designed or validated.

## 14. Protected state and accounting

- `PANDA scientific/evaluation calls = 0`; `PANDA scientific/evaluation tokens = 0`.
- `novel_validation = PRISTINE_FOR_CURRENT_LINEAGE`; `holdout access = 0`; `protected-content leakage = 0`; `F6-B execution = 0`.

## 15. Next task recommendation

Repair the deterministic identifier-catalog evaluator defect (extend the catalog to namespace enum members and/or add a locked-corpus text-presence fallback for qualified `::` symbols), then offline-rescore the stored Attempt-1..5 identifier metrics with zero model calls to validate the repair. This is the only confirmed objective measurement defect; it requires no new scientific execution.

`NEXT_TASK_EXECUTION_AUTHORIZED = false`

## 16. Erratum (forward-only, recorded by the identifier-catalog evaluator repair task)

The review's causal wording for the confirmed obligation-content gap — "runtime coverage review treats a claim self-declared obligation mapping as coverage" — overstated the authority of generator-declared answer-point mappings. Product code and prompts establish otherwise: generator-declared `answer_point_ids` are untrusted proposals; the semantic coverage reviewer independently remaps claims (`verified_mappings` in `qa.py` is produced by `_validate_answer_point_review` from the verifier-returned review), and mapping relevance alone does not imply completeness.

Refined ownership wording:

- `g013.p3` = A1 bounded-revision recovery insufficiency (the missing obligation was correctly detected; one bounded revision failed to recover it).
- `g023.p3` / `g047.p1` = A1 answer-content omission with possible V2 semantic-coverage false acceptance.
- Generator self-declared answer-point mappings = NOT ESTABLISHED AS THE CAUSAL COMPLETENESS AUTHORITY.

High-level classifications, gate dispositions, and the Attempt-5 verdict are unchanged. The historical review commit is not rewritten.
