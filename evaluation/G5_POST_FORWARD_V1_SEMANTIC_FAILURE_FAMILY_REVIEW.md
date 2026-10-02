# G5 Bounded Post-Forward V1 Semantic Failure-Family Review

## 1. Status, scope and decision

**COMPLETE / PASS at offline review scope. No product repair or empirical recovery is claimed.**

The central premise of the preceding n018 interpretation is contradicted by its saved first-pass input. A0 contains the useful GetMcTruth assertion, but the deterministic identifier check excludes it **before the V1 provider sees the claim**. The actual V1 input contains only claim.2 and claim.3. Therefore this is not an observed supported-claim mapping undercheck by V1. Historical O/n007 independently exhibits the same qualified-identifier eligibility boundary.

The selected single next step is **G5 DETERMINISTIC IDENTIFIER-EVIDENCE ELIGIBILITY REPAIR DESIGN**, design only and separately authorized. The review establishes the owning layer and recurrent representation-sensitive exclusion, not a safe acceptance relaxation. No V1 prompt repair, semantic contradiction guard, extra review stage or implementation is selected here.

n019 separately exhibits missing construction evidence followed by coarse semantic completeness acceptance. n022/n025/n028 remain consistent with the frozen smaller-complete-proof invariant. The accepted **TARGETED_V1_MECHANISM_SUPPORTED / Rule 5** verdict is unchanged.

## 2. Authorities and bounded evidence

Entry was clean `main` at `ffabe4fe06ce9360a4947331104161a0903f7138`, message `Run post-observability targeted live verification`, parent `fd6c04aab4a7fb25bad5a93b7c335eff49021e32`. Observability implementation is `2e7cdf6378d381b629a5510380ef1e8d05e8022d`; product behavior lineage remains `5b9588ec552deb91a59a8176d6ce0429c2133b1e`. Prompt set remains `3.12.1`; fingerprint remains `08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc`. No product/prompt source changed or new fingerprint was generated.

Reviewed authorities:

- [Forward execution](G5_POST_OBSERVABILITY_REPAIR_TARGETED_LIVE_VERIFICATION.md) and [accepted forward protocol](G5_POST_OBSERVABILITY_REPAIR_TARGETED_LIVE_FORWARD_PROTOCOL_DESIGN.md), especially the primary, relative-control and NON-GATING rules.
- [V1 provenance design](G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_DESIGN.md) and [implementation](G5_V1_DISPOSITION_PROVENANCE_FALSE_INSUFFICIENCY_REPAIR_IMPLEMENTATION.md).
- [Integrated failure-family review](G5_INTEGRATED_FAILURE_FAMILY_REVIEW.md), [integrated regression](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION.md), and [separate n018](G5_N018_SEPARATELY_AUTHORIZED_RERUN.md).
- Current authoritative status/roadmap, AGENTS.md, and relevant actual `prompts.py` / `qa.py` contracts. Source was inspected as text, without importing or executing the QA/validator/runner.

Local raw authorities, all unchanged:

| Alias | Root under `data/evaluation/runs/` | Inspected case scope |
|---|---|---|
| F | `g5-post-observability-repair-targeted-live-v2` | n018, n019, n022, n025, n028 |
| O | `g5-integrated-candidate-novel-dev-v1` | n006, n007, n019, n023 |
| S | `g5-n018-separately-authorized-rerun-v1` | n018 |

For each case, the exact raw pointer is `records/<ID>.json::diagnostics.qa_stage_trace.events`, selected by stage name, with references resolved through `evidence_registry`. Retrieval pointers are `traces/<ID>.json`. `normalized_draft` is not interchangeable with `model_input.untrusted_claims`. Final `answer_point_audit` reflects the final round and must not be substituted for first-pass V1.

The analog set was selected from the existing failure-family report before opening analog outcomes: its explicit-completeness candidates n006/n019/n023, its separately documented qualified-identifier boundary n007, and S/n018 as the earlier same-question provenance case. No all-case sweep, protected listing/search, corpus search, new retrieval, Gold consultation or historical rescore occurred. I's infrastructure run was not needed for semantic analysis. Original O/n018 remains an unobserved pre-retrieval D1 semantic proposal; no reconstruction or new analog measurement is made from it.

## 3. Frozen forward verdict and forward-only correction

```text
G5_POST_OBSERVABILITY_REPAIR_TARGETED_LIVE_VERIFICATION = COMPLETE / PASS / RULE_5
TARGETED_V1_VERDICT = TARGETED_V1_MECHANISM_SUPPORTED
FIXED_PRIMARY_DENOMINATOR = 3
ASSESSABLE_PRIMARY_COUNT = 3
POSITIVE_PRIMARY_COUNT = 3
CONTROL_N008_CLEAN = true
CONTROL_N019_CLEAN = true / PREEXISTING_CONSTRUCTION_LIMITATION_UNCHANGED
TARGETED_EVIDENCE_CLASS = EXPOSED_TARGETED_MECHANISM_EVIDENCE
FALSE_INSUFFICIENCY_RECOVERY = NOT_EMPIRICALLY_ESTABLISHED
SEMANTIC_COMPLETENESS_NOT_UNIVERSALLY_ESTABLISHED
```

There is a concrete **audit interpretation error** in the execution report section 14: the statement that n018 claim.1's deterministic errors were empty is false for V1. The raw first-pass field is:

```json
{"claim.1": ["unsupported identifier RhoCandidate::GetMcTruth"], "claim.2": [], "claim.3": []}
```

The earlier `SEMANTIC_EVASION_OR_UNDERCHECK_OBSERVED / NON-GATING` label is preserved as a historical reported interpretation, and superseded in current state by the corrected identifier-eligibility finding. The execution report and historical checkpoint prose are not edited. This new report is the forward correction authority. The user required verification of this premise and correction if false; preserving history does not require retaining a disproven causal label as current truth.

No raw-store corruption, protocol breach or required primary/control evidence failure was found. n018 has no gating denominator, and the primary proof observations remain valid. Thus the correction neither upgrades nor downgrades Rule 5. Native generic quality-gate FAIL also remains unchanged. Historical scientific usage is not new usage in this review.

## 4. F/n018 exact first-pass reconstruction

Raw question: "In PandaRoot analysis, how can I inspect the Monte Carlo truth counterpart of a reconstructed candidate and check whether an entire reconstructed decay tree matches the generated one?"

| Persisted stage/field | Observation |
|---|---|
| D1 | `ambiguity.status=clear`; point.1 asks how to inspect the counterpart, `required_relations=[]`; point.2 owns the whole reconstructed/generated tree comparison. No diagnostic fallback is exercised. |
| Selected/admitted evidence | Both A0 claim.1 citations are admitted: `evidence.00c987d640013db2875fefe3` and `evidence.66beb6fd9691050770b7879f`. |
| A0 / normalized draft | claim.1: "In PandaRoot analysis, the Monte Carlo truth counterpart of a reconstructed candidate is accessed by calling RhoCandidate::GetMcTruth(), which returns a pointer to the truth RhoCandidate object." Generator mapping is `[point.1]`. |
| Cited content | 00c987 is the preserved MC-truth tutorial section, with the reconstructed-candidate example `muplus[i]->GetMcTruth()` returning `RhoCandidate *truth`, and a null check. 66beb supplies the adjacent counterpart/RhoCandidate explanation. Neither cited projection/locator contains the contiguous qualified token `RhoCandidate::GetMcTruth`. |
| V1_INPUT deterministic errors | claim.1 has the identifier error quoted in section 3; claim.2/claim.3 have none. |
| Actual provider claims | `model_input.untrusted_claims` is exactly `[claim.2, claim.3]`. claim.1 is present only in the diagnostic `normalized_draft`, not in the submitted claim set. The counterpart evidence and both canonical points are still supplied. |
| V1 support/relevance | `supported=true`, `unsupported_claim_ids=[]`, `irrelevant_claim_ids=[]` apply to the two supplied claims. They do not certify the excluded claim.1. |
| V1 mapping | Both supplied claims map to point.2. There is no claim.1 record because claim.1 was not reviewable, not a provider-emitted `claim.1 -> []`. |
| Ordinary point.1 check | Text: "Reconstructed candidates access their Monte Carlo truth counterpart as a RhoCandidate object." Necessity: "Answers how to inspect the Monte Carlo truth counterpart of a reconstructed candidate." Scope ESTABLISHED; basis 00c987; admission ADMITTED_BACKING_AVAILABLE; satisfied=false; supporters=[]. |
| Basis quote | Exact contiguous text: `Therefore we can simply ask any final state reco particle for its Mc Truth counterpart, being\nalso a\nRhoCandidate\nobject, with the code:` (escapes shown here only for readability). Full projection contains the method call. |
| V1 point.2 | Canonical tree check satisfied by claim.2 with admitted `evidence.aef1029b460a3b22035622ff`; claim.3 remains supported/mapped preparation content. |
| Host validation | Persisted V1_OUTPUT.validation: ACCEPTED, error=null, error_codes=[]. The raw coverage marks point.1 incomplete and missing; point.2 complete. |
| Revision authorization | A1_INPUT lists only the point.1 ordinary relationship and its 00c987 basis. `revisionable_unsupported_claim_ids=[]`; `untrusted_draft.claims=[]`; already-verified context contains claim.2/claim.3. |
| A1_OUTPUT | New claim.1 says to call **GetMcTruth() on the reconstructed candidate**, returning its truth counterpart as a RhoCandidate; citation is 00c987 only. It removes the qualified spelling while preserving the useful fact. |
| V2 | Three claims are supplied; all deterministic error lists are empty; claim.1 maps to point.1; both original points complete; host ACCEPTED. |
| Final | answered; three final claims; one revision; accepted composer, no fallback. |

The first-pass private receipt is not independently saved as a separate full object. The saved raw response, ACCEPTED validation and following A1_INPUT establish the observed transition; source inspection explains it. No missing private decision or model reasoning is reconstructed.

## 5. n018 first wrong boundary and minimum-fact audit

```text
FIRST_WRONG_STAGE = PRE_V1_DETERMINISTIC_IDENTIFIER_ELIGIBILITY
FIRST_WRONG_V1_DECISION = NOT_ESTABLISHED_IN_PROVIDER_MAPPING_OR_DISPOSITION
PROXIMATE_CAUSE = QUALIFIED_IDENTIFIER_LITERAL_ABSENCE_EXCLUDES_SEMANTICALLY_SUPPORTED_A0_CLAIM
UPSTREAM_CONTRIBUTORS = A0_QUALIFIED_SPELLING / CITED_TUTORIAL_UNQUALIFIED_OBJECT_CALL
DOWNSTREAM_EFFECTS = REVIEWABLE_CLAIM_REMOVAL / VALID_ADMITTED_UNSATISFIED_TARGET / A1_REEXPRESSION
```

"Wrong" identifies the first demonstrated loss of useful, independently supported semantic content at product level. The implemented conservative lexical rule itself executed as written; this is not an implementation mismatch against that rule. Whether and how its policy should safely admit nonliteral qualification is a separate design question.

| Required hypothesis | Result |
|---|---|
| D1 contains the individual need | Yes |
| A0 explicitly states the method and return meaning | Yes |
| Its central assertion is independently supported | Yes, by the supplied tutorial object-call example and surrounding explanation |
| Citations and supporting content are admitted | Yes |
| No deterministic support error excludes the claim | **False**: exact saved identifier rejection |
| V1 fails to count a supplied supported claim | **False**: claim.1 never reaches the provider claim list |
| An admitted-backed unsatisfied ordinary disposition is emitted | Yes, truthful for the actually reviewable claim set |
| Host accepts that disposition structurally | Yes |
| A1 is authorized from it | Yes, within the existing target-local contract |
| A1 restates the useful A0 fact | Yes, with narrower identifier representation and one existing citation |

Claim.1 status at first pass: independently supported semantic assertion; **runtime deterministic unsupported/excluded from review**; model support/relevance **NOT_ASSESSED**; provider mapping **NOT_SUPPLIED**. An empty unsupported list over claim.2/claim.3 cannot be lifted to all draft claims. Its generator point.1 declaration was not lost by a semantic mapper; the whole claim was filtered earlier.

The ordinary check describes the correct counterpart need at summary level, not an invented broader requirement. Its selected source has an adequate witness, but no eligible supplied claim states it. Therefore `CHECK_INVENTORY_ITSELF_WRONG` and `CHECK_INVENTORY_CORRECT_BUT_DISPOSITION_WRONG` are not established for n018. The excluded A0 fact would make the result seem contradictory only if the two claim populations were conflated.

`A1_SEMANTIC_RESTATEMENT = CONFIRMED`; **unnecessary work by a V1 semantic failure is NOT_ESTABLISHED**. A1 performs a real eligibility repair in this run by dropping `RhoCandidate::` while keeping the evidence-grounded method-on-candidate statement. Its citation set is a subset of the earlier set; no new factual discovery is observed. It does not repeat an already runtime-verified immutable claim, because the original claim failed the deterministic gate. Reuse of claim ID does not imply unchanged claim bytes. This is correctness/representation analysis, not a token-saving claim or an assertion of population-level recovery.

## 6. Actual host and model authority

Relevant source at review HEAD:

- `qa.py:72`, `_normalise_rejected_identifier_token`: terminal prose punctuation only; no owner/member resolution.
- `QAAgent._verify`, `qa.py:3232-3377`: aggregates each claim's cited text and locator path/symbol/url/section metadata. At lines 3344-3350, code-like qualified/path tokens absent from that aggregate receive `unsupported identifier ...`. The whole claim then fails reviewability.
- `qa.py:3377-3404`: `reviewable_claims` excludes claims with deterministic errors, and only that list is sent in `untrusted_claims`; trace also saves the larger normalized draft and errors for diagnosis.
- `_validate_review_mappings`, `qa.py:854-888`: requires exactly one mapping per **reviewable** claim, forbids unknown/duplicate mappings, and requires a declared empty mapping to be unsupported or irrelevant. It would reject omission of a genuinely supplied claim.
- `_validate_production_check`, `qa.py:962-1011`: checks known IDs, literal quotes, admission, parent ownership and every supporter-to-basis citation edge. Admitted evidence with no satisfying eligible claim may remain unsatisfied.
- `_build_coverage_receipt`, `qa.py:1081-1259`: uses the same reviewable inventory, derives aggregates, and creates an ordinary A1 target from a valid admitted-backed unsatisfied check under established scope.
- `qa.py:3604-3629` and `qa.py:3713-3730`: target-local revision keeps coverage targets distinct from eligible unsupported-claim repairs.

The host structurally accepted the exact inventory it supplied; no missing-mapping contradiction escaped it. Admitted evidence availability is distinct from a supported eligible answer claim. The semantic review is also not authorized to silently regenerate an excluded claim merely because its evidence remains visible.

## 7. Deterministic contradiction-guard assessment

**HOST_DETERMINISTIC_REPAIR_NOT_JUSTIFIED for a new V1 semantic contradiction guard.**

| Candidate signal | Assessment |
|---|---|
| V1 says claim.1 is supported/relevant but omits its mapping | Absent: claim.1 is outside V1's supplied universe; supported=true concerns claim.2/claim.3. |
| Same review maps claim.1 to point.1 elsewhere | Absent. |
| Generator maps it to point.1 | Present but untrusted; cannot override the deterministic error or become completeness authority. |
| A basis mentions the required method, so a claim must satisfy it | Invalid implication: evidence may be admitted without an eligible complete claim. |
| Existing mapped claim plus unsatisfied check | Even if present, a mapped claim may be partial; mapping does not entail whole-check completeness. |
| Text overlap or same unqualified suffix | Unsafe: can accept wrong owners, overloads, namespaces or genuinely partial assertions. |
| Exact structured satisfied/aggregate inconsistency | Already checked/derived by the host; not the observed error. |

The existing safe inventory invariant is `mapping_claim_ids == supplied_reviewable_claim_ids`, with supported/relevant restrictions. It holds here and needs no new guard. There is no authoritative owner/member semantic edge in n018's stored structured fields that permits a safe automatic override of the qualified-token rejection. Tutorial prose and flattened code are human-review evidence, not a prevalidated symbol graph.

For n019, constructor-field overlap cannot deterministically establish execution or persistence flow. Neither case justifies lexical sanitization, forced `satisfied=true`, automatic namespace stripping, inferred claim mappings, evidence-only completion or a new model call.

## 8. Prompt-contract sufficiency

Actual production prompt is `PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SYSTEM_PROMPT = EVIDENCE_REVIEW_SYSTEM_PROMPT + ...` (`prompts.py:259`). It does **not** inherit the separate shadow-review prompt at line 218. The production text itself says to correct generator mappings, exclude unsupported/irrelevant supporters, infer necessary evidence-grounded ordinary checks, require all necessary checks, judge actual canonical direction/polarity/explanation, preserve full meaning when choosing smaller proof, and emit truthful admitted-backed unsatisfaction when no valid complete witness exists. Base evidence review requires central-assertion entailment from the claim's own citations and user relevance.

For F/n018, the proper classification is **PROMPT_CONTRACT_NOT_IMPLICATED / PRE_V1_ELIGIBILITY_FAILURE**. Calling it either a new mapping-prompt gap or provider variance is unsupported: the provider did not receive the claim. It followed an already sufficient missing-claim contract for point.1. No unobserved internal model decision is asserted.

For n019/n006/n023, the observed coarse completeness judgments conflict with the already stated question-derived completeness obligation. Classify those semantic observations as **PROMPT_CONTRACT_ALREADY_SUFFICIENT_PROVIDER_RELIABILITY_FAILURE**, with upstream evidence gaps. This means no concrete missing instruction is demonstrated; it does not establish irreducible variance or promise that wording could never improve reliability. A new prompt edit is not selected simply because these outputs were wrong.

The existing structured shape can represent missing claims, truthful unsatisfied/uncertain coverage, and full coverage. This family does not demonstrate an inability to represent the necessary distinction, so coverage schema redesign is not justified.

## 9. Bounded exposed analog ledger

Classification reference is the **corrected** F/n018 family: semantically supported qualified method claim excluded by deterministic literal identifier checking before model review. None of these is a confirmed recurrence of the originally alleged supported-and-supplied V1 mapping loss.

| Analog | Adequate admitted witness / A0 fact before V1 | Runtime support / mapping | Disposition, A1, final effect | Classification |
|---|---|---|---|---|
| O/n007 | Yes: class documentation gives `GetPath(Int_t shortID)` returning path; A0 says `PndGeoHandling::GetPath` on its instance. | `unsupported identifier PndGeoHandling::GetPath`; claim_0 excluded; only initialization claim_1 supplied. No provider mapping loss. | Truthful admitted-unsatisfied point.1. A1 repeats qualification as claim_2 and V2 rejects the same identifier; final insufficient. | **SAME_FAMILY**, deterministic identifier eligibility; not V1 semantic undercheck. |
| O/n006 | Helper/header supports members/getters; adequate literal-extension enumeration is not in A0 or its header witness. | All three claims pass deterministic checks and map to their intended points. No lost mapping. | V1 accepts member/getter descriptions as full extension answer; no A1/V2; final answered but incomplete. No false-unsatisfied check. | **NOT_SAME_FAMILY**; evidence gap plus coarse positive completeness. |
| O/n019 | Partial input/output, fitter, hypothesis and result schema supported; actual per-track construction is absent from selected task snippets/A0. | Four claims pass and map correctly. | V1 accepts coarse construction despite A0's explicit missing-Exec caveat; no revision; final answered-incomplete. | **NOT_SAME_FAMILY**; evidence gap plus coarse positive completeness. |
| O/n023 | Location and FtsTrack/FtsTrackCand are supported; analytic branch is named by variable only, not actual branch string. | Both claims pass and map correctly. | Canonical output relation marked satisfied from header/partial enumeration; no A1/V2; answered-incomplete. | **NOT_SAME_FAMILY**; evidence gap plus coarse positive completeness. |
| S/n018 | Individual GetMcTruth fact is adequate and unqualified in A0. Both tree and preparation claims exist. | All three pass and map correctly. Individual point complete. | Tree check is PARTIAL/INVALID_SUPPORTER because preparation claim lacks one declared basis citation; no A1/V2; final insufficient. | **RELATED_BUT_DIFFERENT_STAGE**: provider proof declaration and expected strict host rejection, not identifier exclusion or mapping loss. |

All five analogs were assessable for their stated boundaries; none was promoted from missing evidence. O/n019 and F/n019 are repeated realizations of the same question, not two independent question examples. No frequency estimate is inferred from this selected set.

O/n007's cited `evidence.b26ce9e5c08c64381b3ac05c` contains the PndGeoHandling class context and flattened GetPath signature/description. The exact qualified literal is absent from the claim's cited aggregate. V2_INPUT again records the same unsupported identifier for A1 claim_2. Thus the different F/n018 final outcome follows a different revised spelling; it is not proof that the underlying policy was fixed.

Retrieval bounds for the coarse-positive analogs are also visible: O/n006 constructor `object.2914485ff398f61e994c46d6` at dense rank 9 and getter objects at graph 11/14 miss the pool; O/n023 implementation `object.4fd2a5cf8c3a67d8f135cd9d` at dense rank 11 misses the pool. These are saved candidate opportunities, not measured counterfactual recoveries. No new source quotas or expected paths are proposed.

## 10. Narrow taxonomy

| Supported family | Observations | Boundary |
|---|---|---|
| IDENTIFIER_REPRESENTATION_ELIGIBILITY_LOSS | F/n018, O/n007 | Literal qualified token absent from cited representation; useful claim excluded before provider coverage. Existing-witness missing is the downstream symptom, not a separate mapping defect. |
| EVIDENCE_GAP_WITH_COARSE_COMPLETENESS_ACCEPTANCE | F/O n019, O/n006, O/n023 | Required implementation/enumeration detail missing downstream; V1 promotes related structure/category content into full question completeness. Separate upstream availability and downstream semantic decisions remain visible. |
| MALFORMED_DISPOSITION_PROVENANCE | S/n018; historical primary faults documented by accepted design | Existing strict quote/citation policy correctly rejects malformed declared proof. |
| SAFE_SMALLER_COMPLETE_PROOF | F/n022/n025/n028 | Valid selected proof preserves full raw need; this is an accepted pattern, not a defect family. |

No confirmed CLAIM_MAPPING_UNDERCHECK family is established by these observations. SEMANTIC_PROOF_SHRINK_EVASION is an unsafe conceptual counterexample, not a newly observed primary fault. Provider unreliability is a causal limitation for semantic judgments, not a substitute category that hides the demonstrated host exclusion.

## 11. F/n019 absolute limitation

Raw question explicitly asks how PndRecoKalmanTask turns input tracks into fitted output, including fitter selection, hypothesis and **construction of each persisted result**. D1 preserves all four needs. Construction is not added from Gold.

Actual V1 projections include task constructor `evidence.92ec891ad49c1be0b86d0dbc` (PndRecoKalmanTask.cxx:39-48), task class declaration `evidence.e64e35c449c930169a1ec1bb` (header:32-99), and PndTrack class `evidence.244a1832474013c70565536f` (header:23-126). They show output TClonesArray allocation, fitter objects/flags, and PndTrack constructor/fields. The selected task implementation snippets do not contain its Exec loop or a per-track construction/persistence call. Generic fitting tutorial and steering material do not fill that exact operational gap.

The F retrieval trace independently repeats the earlier candidate loss:

| Candidate | Channel/rank | Source / role | Pool / rerank / final |
|---|---|---|---|
| `object.83c5f288a2c09997ca9c36d0` | sparse 18 | restgas_determination, Exec:165-262 | absent / absent / absent |
| `object.4103e48146ef09b48783a0c3` | sparse 19 | pandaroot, Init:52-139 | absent / absent / absent |
| `object.6517cc5a47d460f57c6b4844` | sparse 20 | restgas_determination, Init:57-157 | absent / absent / absent |

Source-version distinctions matter: the lost Exec hit is from restgas, so its candidate presence alone does not certify that adding it would completely answer the exact PandaRoot-version question. No unselected body was fetched or treated as a new authoritative runtime witness. The established earliest limit is **selected evidence missing actual per-track construction**, with an R2 implementation-role opportunity loss; a complete causal retrieval repair is unresolved.

A0 claim.4 describes what a PndTrack encapsulates. It does not describe executing the fitter, deriving each result and placing/linking each persisted object. V1 point.4's necessity explicitly says "structure and contents", replacing the requested construction process with a weaker schema description. Its two basis excerpts are output array allocation and the generic PndTrack constructor signature. They have valid IDs, exact quotes, admission and citation edges, but do not establish the task's actual per-track construction. The result is **SEMANTIC_FALSE_POSITIVE / COARSE_WITNESS_OVERACCEPTANCE**, involving ordinary-check scope and point completeness.

No revision is authorized because V1 marks all points complete. Final composition preserves the same coarse A0 claim; it does not drop an already verified detailed construction account. O/n019 explicitly caveated missing Exec, whereas F/n019 omits that caveat already in A0, not first in the composer. This presentation difference and absolute overacceptance do not alter the frozen relative control interpretation.

```text
TARGETED_CONTROL_INTERPRETATION = PREEXISTING_LIMITATION_UNCHANGED
ABSOLUTE_PRODUCT_SEMANTIC_STATE = CONSTRUCTION_INCOMPLETE / COARSE_WITNESS_OVERACCEPTANCE
FIRST_LIMITING_STAGE = SELECTED_EVIDENCE_GAP / R2_IMPLEMENTATION_ROLE_OPPORTUNITY_LOSS
FIRST_WRONG_COMPLETENESS_DECISION = V1_ORDINARY_CHECK_SCOPE_AND_COMPLETE_DISPOSITION
PROXIMATE_CAUSE = RESULT_STRUCTURE_ACCEPTED_AS_ACTUAL_RESULT_CONSTRUCTION
UPSTREAM_CONTRIBUTORS = MISSING_EXEC_BODY / A0_PARTIAL_CONSTRUCTION_ACCOUNT
DOWNSTREAM_EFFECTS = NO_REVISION / ANSWERED_WITH_INCOMPLETE_CONSTRUCTION
```

## 12. n018 versus n019

| Axis | F/n018 | F/n019 |
|---|---|---|
| Adequate essential fact in A0 | Yes | Actual construction absent; schema facts only |
| Adequate source selected | Yes for counterpart inspection | No observed task per-track construction body |
| Claim eligibility | Useful claim excluded deterministically | Four claims eligible |
| Provider mapping | Correct for supplied claims | Correct parent mappings |
| Coverage judgment | Correctly missing relative to supplied claim set | Coarse witness overaccepted as complete |
| Revision/final | One representation-repair A1, V2 complete, answered | No revision; final retains partial account |

The initially proposed semantic mirror image is not established: the n018 missing side originates before model coverage. n019 independently establishes overacceptance at the semantic completeness boundary. Combining them into one V1 mapping repair would target the wrong layer for n018 and would not restore missing implementation evidence for n019.

## 13. Frozen safe-smaller-proof invariant

```text
SAFE_SMALLER_PROOF =
    provenance_valid
    AND every_selected_supporter_directly_contributes
    AND selected_basis_actually_grounds_the_check
    AND selected_claims_collectively_answer_the_entire_necessary_check_or_relation
    AND no_question_derived_component_is_removed_to_obtain_citation_closure
    AND canonical_relation_identity_direction_polarity_and_explanation_are_preserved
```

This is semantic review guidance, not a new deterministic implementation predicate. Full preserved projected evidence supplies context for the exact quote; a short excerpt must genuinely ground the judgment, not serve as an unrelated literal-match token. All-to-all closure remains necessary under the selected contract, not sufficient for semantics.

Safe patterns: omit a redundant supporter when one existing claim genuinely covers the entire check; refine an ordinary composite explanation into independently necessary checks when all required meanings remain and all checks must pass. Unsafe patterns: delete a missing contribution to gain closure; replace a canonical relation with invented ordinary checks; retain only a citation-valid comment that does not establish the requested relation. No host trimming or rewriting of a malformed emitted proof is permitted.

## 14. n022: quote correction without semantic restructuring

Both separate canonical relations remain: first-step artifact handoff and fitted-vertex feedback/reprocessing. F claim.1 cites `evidence.a152b9210e11fce51b717112` and covers both event_poca ROOT output and fitted-means JSON; its exact quote now preserves backticks around `ana_dpm.C`. F claims.2/.3 both cite `evidence.27a3f94ba524e1cf02a503ee`, contribute configuration and propagation, and collectively explain the second pass. The projected workflow supplies JSON parsing, POCA_VERTEX_FILE, fitvertex and event-ID processing; additional cited configuration source supports FIT_VERTEX_* detail.

**PROVENANCE_CORRECTION_WITHOUT_SEMANTIC_RESTRUCTURING**. It is consistent with SAFE_SMALLER_PROOF; no canonical relation was dropped. This is a current compliant provider output under the repaired prompt, not an isolated causal proof that the prompt produced the improvement.

## 15. n025: ordinary inventory refinement

The raw request asks how combinatorics stay manageable while displaced efficiency is preserved. F retains a relation-free point and three necessary checks: radial inner/middle/outer long-baseline selection; topology/azimuth pruning; no-IP seeding with candidate growth/trajectory validation. Claims.1/.2 cite `evidence.290b6e9b34847abb5fcc3836`; claim.3 cites `evidence.a663a0e2c5fc6797b863c488` and explains no-IP, Apollonius candidates, compatible-hit growth and populated continuous trajectory selection. The full README basis at lines 217-231 explicitly joins these operations to displaced efficiency.

**SAFE_INVENTORY_REFINEMENT**. Three checks preserve the combined raw need and all must pass. Neither an exact historical check count nor Gold-only numeric solution-count detail becomes a runtime obligation. The short no-IP quote is interpreted with its actual full projected source and contributing claim, not as permission to drop validation semantics.

## 16. n028: one complete macro-level exposure witness

F retains canonical tag-production and downstream-exposure relations. `claim_downstream_task_exposure` alone supplies the actual selected exposure proof and cites `evidence.5aec65f04ec751097c07fbd4`. The macro's exact quote describes accessing OnlineEventFilterInfo; the next line says it is written by SoftTriggerTask, and the body adds that task before PndAnaWithTrigger, then initializes/runs. The claim states this producer-to-consumer access relationship. The container/query-method claim remains independently supported, mapped and rendered.

**SAFE_SMALLER_COMPLETE_WITNESS at the frozen macro-level raw-question scope**. Removing an unnecessary container-only supporter from the selected proof does not remove its final explanatory content or the required exposure relation. Full producer registration, FairRootManager retrieval, exact branch spelling and tuple internals are not newly mandatory merely because historical Gold explored them. Those deeper implementations are not certified here. No necessary missing handoff is established in the preserved raw scope, so Rule 5 is not reopened.

## 17. Responsibility matrix

| Layer | F/n018 | F/n019 |
|---|---|---|
| D1 | Correct two needs and canonical tree relation | Correct four explicit needs |
| Retrieval | Needed counterpart source selected | Construction body absent downstream; candidate opportunity lost before pool |
| Evidence admission | Needed citations admitted | Coarse selected sources admitted; no observed removal of an otherwise selected complete construction witness |
| A0 | Useful fact present with qualified spelling | Partial structure account, no actual construction process |
| Deterministic claim support | **First demonstrated content loss**, qualified-token literal rejection | No claim errors |
| V1 model support/relevance | Excluded claim not assessed; two supplied claims accepted | Partial claims accepted as factual/relevant |
| V1 mapping | No erroneous mapping omission within supplied inventory | Correct parents; does not prove completeness |
| V1 inventory | Counterpart need compatible with raw question | Construction reduced to structure/contents |
| V1 disposition | Truthful unsatisfied over actual eligible claims | Coarse satisfied/complete decision overstates coverage |
| Host receipt | Correct structural/provenance validation | Correct structural/provenance validation; not a semantic truth oracle |
| A1 | Restates useful fact with eligible unqualified wording | Not executed |
| V2 | Full original inventory accepted after changed claim representation | Not executed |
| Composer/final | Retains recovered content | Preserves already coarse claim; not first omission |

## 18. Genericity and repair threshold

The conservative decision rule was retained: a proposed generic semantic repair requires the claimed error in n018 plus at least one independently comparable same-family observation, or a strong deterministic contract contradiction. The **claimed V1 mapping-undercheck premise fails for n018**, and no new host semantic contradiction exists. Therefore **GENERIC_V1_MAPPING_IMPLEMENTATION_CHANGE_NOT_ESTABLISHED**.

There are two independent exposed question examples of **qualified-identifier representation eligibility loss**: F/n018 and O/n007. That supports an owning-layer design investigation, not an implementation inferred from one wrong provider output. The exact lexical gate is generic and deterministic; its overrestrictive semantic consequence is visible. The safe alternative remains unresolved because suffix matching, guessed ownership and trusting generator mappings can admit wrong assertions.

n006/n019/n023 additionally support a distinct coarse-completeness observation family across three question IDs. They do not establish a new generic prompt-contract gap or a safe host entailment predicate. Retrieval availability, generation detail and model completeness judgments must remain distinct. No claim of all-G5 repair coverage, causal prompt benefit or recovered-case percentage is made.

## 19. Exactly one selected next step

**Primary next-step class: DETERMINISTIC_IDENTIFIER_EVIDENCE_ELIGIBILITY_REPAIR_DESIGN.**
**Next task: G5 DETERMINISTIC IDENTIFIER-EVIDENCE ELIGIBILITY REPAIR DESIGN.**

This is an evidence-driven owning-layer alternative to the suggested A-E outcomes because the minimum premise was disproven. It is not C's proposed V1 contradiction guard: no such guard is justified. A purely V1 NO_CHANGE/MONITOR response would omit the independently repeated upstream identifier boundary; B has no demonstrated V1 prompt gap; D has no representation failure in the coverage schema; E's retrieval/evidence-admission repair would not address the fact that n018's needed source is already admitted. Keeping the demonstrated owner is more precise than forcing it into an inapplicable repair category.

Future design scope, not implementation: specify how deterministic claim-identifier eligibility should treat source-supported object/member notation versus qualified spelling, what evidence can safely establish ownership, and when conservative rejection must remain. Require neutral wrong-owner, namespace/overload and absent-evidence counterexamples before choosing any relaxation. Consider the current strict rule as an explicit option. Do not prescribe case strings, auto-remove qualifiers, consult Gold, change coverage acceptance or add review calls. No particular predicate is claimed implementation-ready here.

n019 construction-evidence and coarse-completeness findings remain documented limitations for later planning, not a second immediate task. No automatic monitoring job, new corpus search, test plan execution or live run is authorized. `NEXT_TASK_EXECUTION_AUTHORIZED=false`.

## 20. Scientific and causal limitations

This is saved-artifact inspection and source reasoning only. No new empirical before/after metric, deterministic test result or repair efficacy is produced. Historical runs differ in realization and some identities; valid current proofs do not isolate prompt causality. The corrected n018 classification does not imply all false insufficiencies share one cause.

The review can establish raw claim filtering, actual provider input, emitted dispositions, host validation and downstream targets. It cannot establish private provider reasoning, population incidence, a universal safe qualified-name resolver, or the answer that unavailable construction evidence would have induced. n019's lost cross-source Exec candidate is an opportunity, not proof of version-compatible complete support.

All three primary proofs are consistent with the frozen invariant at their recorded raw scope; this is not an exhaustive semantic certification. The live failed-QA and late-failure export paths remain NOT_EXERCISED in F. Existing deterministic implementation evidence and historical 429 subtype limitations are unchanged.

## 21. Lifecycle, boundary receipt and delivery

```text
G5_POST_FORWARD_V1_SEMANTIC_FAILURE_FAMILY_REVIEW = COMPLETE / PASS
N018_AUDIT_INTERPRETATION_CORRECTION = CONFIRMED_FROM_FIRST_PASS_INPUT
N018_FIRST_WRONG_STAGE = PRE_V1_DETERMINISTIC_IDENTIFIER_ELIGIBILITY
N018_V1_MAPPING_UNDERCHECK = NOT_ESTABLISHED / CLAIM_NOT_SUPPLIED
N018_A1_FALSE_WORK = SEMANTIC_RESTATEMENT_CONFIRMED / ELIGIBILITY_REPAIR_REQUIRED
N019_ABSOLUTE_SEMANTIC_LIMITATION = CONFIRMED / COARSE_WITNESS_OVERACCEPTANCE_WITH_EVIDENCE_GAP
SMALLER_COMPLETE_PROOF_SELECTION = SAFE_WITH_FROZEN_SEMANTIC_INVARIANT
GENERIC_V1_MAPPING_IMPLEMENTATION_CHANGE = NOT_ESTABLISHED
IDENTIFIER_ELIGIBILITY_FAILURE_FAMILY = CONFIRMED_ON_F_N018_AND_O_N007
HOST_DETERMINISTIC_V1_CONTRADICTION_GUARD = NOT_JUSTIFIED
V1_PROMPT_REPAIR = NOT_JUSTIFIED_BY_THIS_REVIEW
TARGETED_V1_VERDICT = TARGETED_V1_MECHANISM_SUPPORTED
FALSE_INSUFFICIENCY_RECOVERY = NOT_EMPIRICALLY_ESTABLISHED
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = G5 DETERMINISTIC IDENTIFIER-EVIDENCE ELIGIBILITY REPAIR DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false

PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
SCHEMA_CHANGE = false
CONFIG_CHANGE = false
DEPENDENCY_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
RAW_RUN_STORE_CHANGE = false
NEW_PROVIDER_CALLS = 0
NEW_PROVIDER_PREFLIGHT_CALLS = 0
NEW_TARGETED_LIVE_RUNS = 0
NEW_LOGICAL_CASE_ATTEMPTS = 0
NEW_GENERATION_PROVIDER_INVOCATIONS = 0
NEW_EMBEDDING_PROVIDER_INVOCATIONS = 0
NEW_PROVIDER_INVOCATIONS = 0
NEW_SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
TEST_EXECUTIONS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```

Changed files are this report and only the current authoritative sections of `docs/EVALUATION_STATUS.md` and `docs/GENERALIZATION_ROADMAP.md`. Prior reports, checkpoint prose and historical chronology remain intact. Final static delivery review verifies the three-path scope, preserved historical content and frozen Rule-5/lifecycle fields, with `git diff --check`. No pytest, provider client, health check, evaluator/validator execution or raw-store write is part of verification.

Commit message: `Review post-forward V1 semantic failure families`; exact delivery SHA is reported in the final response and resolved from Git history. Parent is the starting HEAD above. No push.
