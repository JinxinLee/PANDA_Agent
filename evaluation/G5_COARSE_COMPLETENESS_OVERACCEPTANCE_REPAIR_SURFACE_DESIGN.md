# G5 Bounded Evidence-Gap / Coarse-Completeness Overacceptance Repair-Surface Design

> **CORRECTION_STATUS = COMPLETE / CORRECTED / PASS**
>
> This document supersedes its earlier n023 D1 classification. The bounded
> correction finds that n023's output-list request was over-extracted into a
> required relation. The original n006/n019 findings and frozen lifecycle
> conclusions remain unchanged.

## 1. Status and scope

```text
G5_COARSE_COMPLETENESS_OVERACCEPTANCE_REPAIR_SURFACE_DESIGN = COMPLETE / CORRECTED / PASS
PRIMARY_OUTCOME = C / D1_RELATION_EXTRACTION_BOUNDARY_REPAIR_DESIGN
SELECTED_REPAIR_SURFACE = D1_RELATION_EXTRACTION_BOUNDARY_REPAIR_DESIGN
IMPLEMENTATION_READY = false
NEXT_TASK_RECOMMENDATION = G5 D1 RELATION-EXTRACTION BOUNDARY REPAIR DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

PASS applies to the corrected bounded review and repair-surface decision. The observed semantic defects remain. This task performs offline review, static source inspection, saved exposed-artifact inspection and documentation only; it does not implement the next design.

Correction entry: clean `main`, HEAD `30f726cbe67a2f6461b993e34dfb7f32010518d7`, message `Design coarse completeness repair surface`, parent `4bdf73e75509aa868ccb4fb78ec34350fd994e64`. The correction commit has this entry HEAD as parent; its SHA is resolved from Git history and reported on delivery. No push.

Product behavior lineage remains `5b9588ec552deb91a59a8176d6ce0429c2133b1e`; prompt set remains `3.12.1`, fingerprint `08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc`. These existing identities are retained, not regenerated. No frozen candidate or new integrity manifest is created.

## 2. Authorities and artifact scope

Current interpretation follows the [post-forward semantic review](G5_POST_FORWARD_V1_SEMANTIC_FAILURE_FAMILY_REVIEW.md) and [identifier-eligibility design](G5_IDENTIFIER_EVIDENCE_ELIGIBILITY_REPAIR_DESIGN.md). Historical context comes from the [integrated failure-family review](G5_INTEGRATED_FAILURE_FAMILY_REVIEW.md), [integrated execution report](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION.md), [G4 exposed diagnostic](G4_EXPOSED_DEVELOPMENT_FALSE_INSUFFICIENCY_DIAGNOSTIC.md), [R2 design](G4_R2_FUSION_EVIDENCE_RETENTION_REPAIR_DESIGN.md), [collateral-retention implementation](G4_R2_COLLATERAL_RETENTION_IMPLEMENTATION_RESULT.md), [normal-product integration correction](G4_R2_NORMAL_PRODUCT_POOL_INTEGRATION_CORRECTION.md), [post-correction exposed verification](G4_R2_POST_CORRECTION_EXPOSED_VERIFICATION.md), [collateral completeness review](G4_R2_COLLATERAL_RETENTION_COMPLETENESS_FAILURE_REVIEW.md), [G4 targeted live verification](G4_POST_CORRECTION_TARGETED_LIVE_VERIFICATION.md) and [G5 forward execution report](G5_POST_OBSERVABILITY_REPAIR_TARGETED_LIVE_VERIFICATION.md).

Static implementation authority: [question_decomposition.py](../src/panda_agent/question_decomposition.py), [prompts.py](../src/panda_agent/prompts.py), [qa.py](../src/panda_agent/qa.py), [retrieval.py](../src/panda_agent/retrieval.py). Current lifecycle authority: [evaluation status](../docs/EVALUATION_STATUS.md) and [roadmap](../docs/GENERALIZATION_ROADMAP.md). Source inspection establishes behavior, not execution authorization.

Aliases below:

- **O**: `g5-integrated-candidate-novel-dev-v1`.
- **F**: `g5-post-observability-repair-targeted-live-v2`.

Exactly four saved realizations, three independent question IDs:

| Realization | Record | Trace |
| --- | --- | --- |
| O/n006 | [record](../data/evaluation/runs/g5-integrated-candidate-novel-dev-v1/records/n006.json) | [trace](../data/evaluation/runs/g5-integrated-candidate-novel-dev-v1/traces/n006.json) |
| O/n019 | [record](../data/evaluation/runs/g5-integrated-candidate-novel-dev-v1/records/n019.json) | [trace](../data/evaluation/runs/g5-integrated-candidate-novel-dev-v1/traces/n019.json) |
| F/n019 | [record](../data/evaluation/runs/g5-post-observability-repair-targeted-live-v2/records/n019.json) | [trace](../data/evaluation/runs/g5-post-observability-repair-targeted-live-v2/traces/n019.json) |
| O/n023 | [record](../data/evaluation/runs/g5-integrated-candidate-novel-dev-v1/records/n023.json) | [trace](../data/evaluation/runs/g5-integrated-candidate-novel-dev-v1/traces/n023.json) |

Record paths used: `diagnostics.question_decomposition`, `plan`, `selected_evidence`, `rerank_pool_entries`, `fusion_scores`, and `qa_stage_trace.events/evidence_registry`. Trace paths used: `channel_candidates`, `fused_candidates`, `reranked_candidates`, `final_evidence`. First-pass events `V1_INPUT` and `V1_OUTPUT` expose runtime points, eligible claims, evidence projections, review response and host validation. Placeholder events with `status=NOT_EXECUTED` do not establish A1/V2 execution.

No other raw case was opened. No all-28 sweep, fresh retrieval, source-body fetch, Gold/calibration content inspection or protected-material listing/search/open occurred. Existing historical reports were read within the authorized relevant scope. Case IDs below are offline locators, never proposed runtime triggers.

## 3. Family hypothesis and finding

The broad family **EVIDENCE_GAP_WITH_COARSE_COMPLETENESS_ACCEPTANCE** remains confirmed across n006/n019/n023, but its D1 mechanisms are not uniform. n006 and n019 retain their explicit obligations and exhibit ordinary-check scope weakening. n023 has an earlier decomposition boundary defect: its output-set request was represented as a required relation whose text loses the identity-set question.

The narrower **ORDINARY_CHECK_SCOPE_WEAKENING** mechanism is confirmed on n006 and n019 only. The corrected n023 path is **RELATION_OVEREXTRACTION / ORDINARY_ENUMERATION_MISCLASSIFIED_AS_RELATION**. V1 then evaluates the weakened canonical relation and accepts it; that downstream result is retained as a consequence, not treated as the first owner. This correction removes the earlier claim that n023 was a D1-sufficient canonical counterexample.

F/O n019 are two realizations of one question, not two independent examples. The four records do not measure population incidence, causal effects of a prompt change, recovery probability or fresh generalization. Historical evaluator incompleteness alone is not the defect criterion; sections 4-7 establish the runtime discrepancy independently.

## 4. Raw-question authority

**O/n006:**

> My analysis chain produces sim, digi, reco and pid files and I keep concatenating the stage names by hand. Does PandaRoot ship a helper that derives all these file names from the simulation file name, and which stage extensions does it define?

D1 point 1 contains canonical `point.1.rel.1`, "The helper derives file names from the simulation file name." Point 2 is ordinary, "Which stage extensions the helper defines," with the explicit question span "which stage extensions does it define?" Filename context requires the defined extension values, not merely the names of extension members/getters. No Gold-specific list, count or extra stage is imposed.

**O/F n019, identical raw question:**

> How does PndRecoKalmanTask turn input PndTrack objects into fitted output tracks, including fitter selection, particle-hypothesis choice, and the construction of each persisted result?

D1 separately represents transformation (canonical `point.1.rel.1`), fitter selection (ordinary point 2), particle hypothesis (ordinary point 3), and "How each persisted result is constructed in PndRecoKalmanTask" (ordinary point 4). The explicit construction span is present. Describing the result type and fields does not answer the requested construction process. The question does not explicitly name a repository version; nevertheless, an unselected fork body cannot automatically prove the behavior of the selected PandaRoot implementation.

**O/n023:**

> I need to modify forward tracking for the forward spectrometer. Where in the PandaRoot source tree is the FTS track finder implemented, and which track branches does it write out?

D1 point 1 asks the source locator. Point 2 says "Identify which track branches the FTS track finder writes out," with canonical `point.2.rel.1`, "The FTS track finder writes out track branches." The parent text and raw question establish enumeration, but the relation-bearing completeness path makes the relation text operative and that text is broad. A field holding an unknown branch name is not that branch's actual name. Gold-only payload-type or internal producer details are not added as runtime obligations.

The exact persisted D1 bytes are: point 2 text `Identify which track branches the FTS track finder writes out.`; point 2 support span `which track branches does it write out?`; relation ID `point.2.rel.1`; relation text `The FTS track finder writes out track branches.`; relation support span `which track branches does it write out?`; no `relation_type` field. The relation is therefore not merely a report paraphrase: the raw point and relation both omit the requested `which` identity-set semantics from the canonical relation text.

Under G1, this is not a sufficient relation-bearing representation. “Which track branches does task X write out?” is analogous to which outputs, fields or extensions a component defines: it asks for an ordinary property/list enumeration. It does not ask to establish a connection, ordering, dependency or other relation between distinct participants. The correct D1 shape is the existing point text with `required_relations=[]`, leaving enumeration scope to ordinary C1 rather than assigning it to a generic input/output edge.

## 5. n006 trace reconstruction

Selected/claim-cited `evidence.a1ad47fbb4d555cf69c341bd` is PandaRoot `tools/PndFileNameCreator.h:1-74`, version beginning `18c09`. Its projected text supplies the helper, simulation-name base, the `<SimulationFileName>_<extension>.root` pattern, getters and extension-member declarations. It does not supply literal extension initializers. The other selected macro/workflow/domain evidence does not supply a complete claim-cited extension-default witness.

All three eligible A0 claims cite this header. `claim_1` answers helper derivation. `claim_2` lists primary extension members/getters for par/sim/digi/reco/pid. `claim_3` lists additional tracking/Riemann/Kalman/vertex members/getters and explicitly says "though the literal string defaults are not established by the header passage." This is useful partial evidence, not complete enumeration of the requested extension values.

First-pass V1 preserves the valid helper relation and makes two ordinary point-2 checks:

| Relationship text | Necessity reason | Basis quote / supporter |
| --- | --- | --- |
| PndFileNameCreator defines dedicated stage extension members and methods for par, sim, digi, reco, and pid. | Specifies the primary simulation and reconstruction stage extensions defined by the class. | `std::string fExtPar;` in the header / `claim_2` |
| PndFileNameCreator also defines stage extension members and methods for tracking, Riemann, Kalman, and vertexing. | Specifies additional tracking and vertexing stage extensions defined by the class. | `std::string fExtTrackF;` in the same header / `claim_3` |

Both checks are `satisfied=true`, `ADMITTED_BACKING_AVAILABLE`; point 2 is `scope_status=ESTABLISHED`, `complete=true`. Claims are supported/relevant with correct parent mappings; exact quotes, own citations and all-to-all closure are valid. The names are legitimately supported. The semantic mistake is treating that member inventory as the full requested extension enumeration, despite the explicit caveat.

The response is host-accepted, `missing_answer_point_ids=[]`. No A1 target/execution or V2 execution follows, `revision_count=0`. The accepted composer preserves the three claims and caveat; the final answered result still lacks the extension values. Final rendering did not originate this discrepancy.

Upstream opportunities are three distinct objects, not one object repeated across channels: dense-rank-9 constructor, graph-rank-11 `GetParFileName`, graph-rank-14 `GetDigiFileName` (section 14). All miss saved legacy top 30, offered pool, reranked set and final evidence. Historical G4 material identifies initialization/default opportunities; current candidate trace lacks their full text, so counterfactual complete recovery is not established here.

```text
N006_FIRST_LIMITING_STAGE = SELECTED_EVIDENCE_GAP / R2_EXTENSION_VALUE_OPPORTUNITY_LOSS
N006_FIRST_WRONG_SEMANTIC_DECISION = V1_ORDINARY_CHECK_SCOPE_AND_COMPLETE_DISPOSITION
N006_PROXIMATE_CAUSE = MEMBER_GETTER_INVENTORY_ACCEPTED_AS_EXTENSION_VALUE_ENUMERATION
N006_UPSTREAM_CONTRIBUTORS = UNSELECTED_INITIALIZATION_OPPORTUNITY / PARTIAL_A0
N006_DOWNSTREAM_EFFECTS = NO_A1_TARGET / FINAL_ENUMERATION_GAP_PRESERVED
```

## 6. n019 trace reconstruction and mirror check

Both realizations share the relevant selected PandaRoot evidence:

| Evidence ID | Projected locator | What it establishes |
| --- | --- | --- |
| `evidence.92ec891ad49c1be0b86d0dbc` | `tracking/GenfitTools/recotasks/PndRecoKalmanTask.cxx:39-48` | Task constructor, `fFitTrackArray=new TClonesArray("PndTrack")`, fitter members and defaults |
| `evidence.e64e35c449c930169a1ec1bb` | same task `.h:32-99` | Init/Exec signatures, setters/flags and input/output members; no Exec body |
| `evidence.244a1832474013c70565536f` | `pnddata/TrackData/PndTrack.h:23-126` | Result constructor signature and track parameters/candidate/PID/quality/statistic fields; no task per-track construction calls |

F also selects restgas constructor `evidence.8d73f5c6eee075fd7ed6ebc3`, `.cxx:38-50`; it does not supply Exec. Other selected tutorial/steering/domain material is not the task's actual construction process.

O's `claim_1` through `claim_4` cover array transformation, fitter flags, PDG/default/ideal hypothesis settings and result structure. `claim_4` explicitly caveats the unavailable Exec/per-track loop. F's corresponding `claim.1` through `claim.4` also supply coarse result structure, but the construction caveat is already absent in A0. All four eligible claims reach V1 in each realization with empty deterministic claim errors and correct mappings.

First-pass point-4 ordinary check:

| Realization | Relationship text | Necessity reason |
| --- | --- | --- |
| O | Persisted output tracks are PndTrack instances stored in fFitTrackArray containing track parameters, track candidate, PID hypothesis, quality flag, and chi2. | Directly explains how each persisted result is constructed in PndRecoKalmanTask. |
| F | Persisted results are constructed as PndTrack objects encapsulating track parameters, candidate, fit statistics, quality flag, and PID hypothesis. | Explains the structure and contents of the persisted PndTrack result. |

Both use constructor/array evidence `92ec...` and result-type evidence `244a...`, supported by the respective fourth claim. Their exact basis quotes come from these supplied projections; own-citation/all-to-all/admission constraints pass. Array allocation and a result constructor signature establish a coarse structural witness, not the actual task's per-input fitting and persisted-result construction procedure. O's necessity prose calls it construction without supplying that semantics; F expressly substitutes structure/contents.

V1 marks all four points complete, point 4 established and satisfied with admitted backing; no unsupported/irrelevant exclusions or missing points. Host validation is ACCEPTED. There is no A1 target/execution or V2 execution, `revision_count=0`. The accepted composer preserves all four claims. O retains the caveat; F's absent caveat was not first removed by the composer. The same construction gap reaches each final answered result.

This confirms a semantic false positive at V1, not a stylistic issue. The frozen n018 mirror distinction remains: an adequate claim was excluded before V1 in that other family, whereas n019's supplied, structurally grounded but inadequate construction witness is accepted by V1. Identifier eligibility is not reopened.

Retrieved rows in both O/F include restgas Exec at sparse 18, PandaRoot Init at sparse 19 and restgas Init at sparse 20 (section 14), all absent from pool/final. Init does not prove Exec construction. The Exec row's restgas version is plan-allowed, but cross-repository semantic equivalence with the selected PandaRoot task is unproved. It is **merely suggestive as a complete construction witness**, neither certified recoverable nor established incompatible. No saved full body is fetched or synthesized here.

```text
N019_FIRST_LIMITING_STAGE = SELECTED_EVIDENCE_GAP / R2_IMPLEMENTATION_ROLE_OPPORTUNITY_LOSS
N019_FIRST_WRONG_COMPLETENESS_DECISION = V1_ORDINARY_CHECK_SCOPE_AND_COMPLETE_DISPOSITION
N019_FIRST_WRONG_SEMANTIC_DECISION = V1_ORDINARY_CHECK_SCOPE_AND_COMPLETE_DISPOSITION
N019_PROXIMATE_CAUSE = RESULT_STRUCTURE_ACCEPTED_AS_ACTUAL_CONSTRUCTION_PROCESS
N019_UPSTREAM_CONTRIBUTORS = MISSING_SELECTED_EXEC_BODY / UNRESOLVED_FORK_WITNESS / PARTIAL_A0
N019_DOWNSTREAM_EFFECTS = NO_A1_TARGET / FINAL_CONSTRUCTION_GAP_PRESERVED
```

## 7. n023 trace reconstruction

Selected `evidence.8629217598da4dc02a896b88` is PandaRoot `tracking/PndFtsTrackFinder/PndFtsTrackFinderTask.h:25-105`. It supplies `SetOutputBranchName`, default `FtsTrack`, the name-plus-`Cand` convention, and `fOutAnalyticBranchName`/analytic array declarations. It does not supply the analytic branch's initialized string. `evidence.eb90b56ee985e10b621ade1a`, the directory's `CMakeLists.txt:1-76`, supports the source locator/build identity.

A0's source-location claim correctly locates `tracking/PndFtsTrackFinder`. Its `claim_fts_track_finder_output_branches` names default FtsTrack/FtsTrackCand and describes "analytic tracks (fOutAnalyticBranchName)," citing the header. A variable describing an additional branch does not enumerate its actual branch name.

V1's locator ordinary check is grounded. The output point is **canonical**, with copied `point.2.rel.1`, `relationship_checks=[]`, not a V1-generated ordinary relationship. Its basis is the header quote "Sets the name of the output branch containing generated PndTracks." Its supporter is the output-branches claim. This exact comment and admitted own-citation closure are valid, but the comment is not a complete enumeration witness. V1 sets the canonical check satisfied, point complete/established, missing points empty; host validation accepts.

No A1 target/execution or V2 execution follows, `revision_count=0`; the accepted composer preserves the two claims, including the unknown analytic branch variable, in the final answered result. V1's `complete=true` is a downstream consequence of evaluating the weakened canonical relation. The supplied claim and header do support the broad relation that output branches exist, so an independent V1 failure against that weakened relation is not established. V1 cannot recover the `which` semantics removed before it.

The saved dense-rank-11 source-file chunk for `PndFtsTrackFinderTask.cxx:1-18` misses legacy top 30, offered pool, reranked set and final evidence. Historical review associates implementation initialization with the missing analytic name. The current trace stores locator/rank but no candidate body; it cannot prove that this short chunk alone supplies the complete answer. No new body fetch or guaranteed recovery claim is made.

```text
N023_FIRST_LIMITING_STAGE = D1_RELATION_EXTRACTION_BOUNDARY / REQUIRED_RELATION_SEMANTIC_NORMALIZATION
N023_FIRST_WRONG_SEMANTIC_DECISION = D1_RELATION_OVEREXTRACTION / ORDINARY_ENUMERATION_MISCLASSIFIED_AS_RELATION
N023_PROXIMATE_CAUSE = IDENTITY_SET_REQUEST_LOST_FROM_CANONICAL_RELATION_TEXT
N023_UPSTREAM_CONTRIBUTORS = PARTIAL_SELECTED_EVIDENCE / UNSELECTED_INITIALIZATION_OPPORTUNITY
N023_DOWNSTREAM_WRONG_DECISIONS = V1_ACCEPTED_WEAKENED_CANONICAL_RELATION / POINT_COMPLETE
N023_DOWNSTREAM_EFFECTS = NO_A1_TARGET / FINAL_BRANCH_ENUMERATION_GAP_PRESERVED
```

## 8. Responsibility matrix

The matrix describes the observed deficient point; it does not declare every other point in these answers defective.

| Layer | O/n006 | O/F n019 | O/n023 |
| --- | --- | --- | --- |
| D1 obligation correctness | Sufficient explicit extensions point | Sufficient separate construction point | **Defective:** ordinary branch enumeration over-extracted into a generic required relation |
| Retrieval availability | Constructor/getter metadata upstream | Init and fork Exec metadata upstream; complete compatible witness unresolved | Initial source-file metadata upstream; full initializer text unresolved |
| Selected evidence | Header/member inventory, not extension defaults | Array constructor/result schema, no task Exec construction | Header/locator, no actual analytic branch name |
| Admission | Cited basis admitted; no admission loss | Cited basis admitted; no admission loss | Cited basis admitted; no admission loss |
| A0 semantic depth | Partial member inventory with caveat | Partial result structure; O caveat, F no caveat | Partial branch names plus variable description |
| V1 claim support/relevance | Supported coarse assertions remain useful | Supported coarse assertions remain useful | Locator/default names supported; full enumeration not established |
| V1 mapping | Correct helper/extensions parents | Correct four parents | Correct locator/branches parents |
| V1 ordinary/canonical inventory | Helper canonical; extensions ordinary | Transformation canonical; construction ordinary | Locator ordinary; branches canonical |
| V1 scope wording | Members/getters substitute extension values | Structure/contents substitute construction | Evaluates already-weakened relation; no further V1 wording substitution |
| V1 basis adequacy | Declaration proves member, not extension value | Allocation/signature prove structure, not per-track procedure | Setter comment proves output role, not all branch names |
| V1 satisfied decision | Incorrect for full requested enumeration | Incorrect for construction obligation | Satisfies the weakened generic relation; independent V1 error not established |
| Point complete decision | Incorrect point 2 complete | Incorrect point 4 complete | Complete only under the weakened D1 contract; wrong for raw question downstream |
| A1 authorization | No targets | No targets in either realization | No targets |
| Final rendering | Preserves gap/caveat | Preserves gap; caveat difference precedes composer | Preserves gap/variable |

Across all four: first-pass claims have no deterministic rejection; cited basis is admitted; host review validation ACCEPTED; final composer attempted, accepted and semantically reviewed, with no fallback. These facts support provenance/mapping validity, not semantic completeness.

## 9. Evidence gap versus overacceptance

The earliest observed limitation is case-specific. For n006/n019 it is the selected-evidence gap, followed by V1's weaker ordinary check. For n023 it is D1 relation normalization: the identity-set request is absent from the canonical relation before V1 sees it. The selected-evidence gap remains an upstream contributor, but it is no longer the first limiting stage. A0 is already semantically partial; in O/n006 and O/n019 it says so. Useful grounded partial claims need not be discarded merely because the whole point is incomplete.

Retrieval repair alone is **not established sufficient**: candidate semantic/version sufficiency is unresolved in saved payloads, and an improved pool would not guarantee selection, generation or reliable review. Conversely, with the current coarse evidence V1 should already preserve the explicit need and mark the deficient point incomplete rather than complete. This does not require speculative new evidence or Gold.

Use the existing truthful disposition: admitted-backed unsatisfied only when the evidence supports that disposition; otherwise `INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE` or visible-only as applicable. Evidence absence must not be relabelled a complete admitted witness merely to obtain an A1 target. Blocked/uncertain checks do not authorize A1. Conservative incompleteness is not a promise that the current A1 geometry can repair missing implementation evidence.

## 10. Ordinary-check scope weakening and explicit semantic components

The recurring ordinary mechanism has two independent examples: n006 replaces extension values by member/getter categories; n019 replaces actual construction by result structure. Valid `relationship_text`/`necessity_reason`, mappings and citation closure cannot prove equivalence with the raw obligation. A plausible necessity sentence can accompany a weaker relationship.

`EXPLICIT_SEMANTIC_COMPONENT` is useful as a review concept: preserve requested enumeration, requested process and explicit included subparts. D1 supplies the distinction for n006/n019, but fails to retain it in n023's relation text. It is not a proposed runtime parser, keyword classifier, expected answer list or new intermediate schema. A broad question can be fully answered at its actual requested abstraction level; the existence of the word "how" does not require an implementation body.

n023 demonstrates a decomposition boundary failure, not a third ordinary-check scope failure. Its downstream canonical acceptance cannot be repaired by V1 alone because V1 receives the weakened relation. The same evidence gap still matters after a corrected ordinary point, but it does not establish that retrieval alone would recover every branch name.

## 11. D1 adequacy and structured-contract assessment

```text
N006_D1_CLASSIFICATION = D1_SUFFICIENT
N019_D1_CLASSIFICATION = D1_SUFFICIENT
N023_D1_CLASSIFICATION = D1_REQUIRED_RELATION_SEMANTIC_DEFECT / RELATION_OVEREXTRACTION
COMMON_D1_GRANULARITY_DEFECT = false
COMMON_D1_DEFECT = false
N023_RELATION_EXTRACTION_BOUNDARY = ORDINARY_ENUMERATION_MISCLASSIFIED_AS_RELATION
STRUCTURED_ORDINARY_CONTRACT_REDESIGN = NOT_JUSTIFIED
```

N006 and n019 retain their explicit needs in the actual runtime inventory. n023's parent retains the wording, but G1 assigns completeness authority for a relation-bearing point only to its canonical required relation. Because the canonical relation says only that tracks are written out, it cannot carry the raw `which` identity-set obligation. The correct classification is a D1 relation-extraction boundary defect, not a common D1 granularity defect.

The G1 decomposition implementation and focused contract inventory provide ordinary examples for a locator, definition, API argument list and unstructured explanation (`Where is Cedar implemented?`, `Define Birch.`, `Which file defines Maple?`, `What arguments does SensorFrame accept?`, `How does Cedar work?`). They do not provide a neutral output/field/branch/extension-list example. This is bounded evidence of a missing boundary example, not a test result and not a reason to add a PANDA-specific rule.

G1 is binding here: for `required_relations == []`, ordinary C1 owns completeness; when the list is nonempty, the canonical required-relation dispositions are the sole completeness path. Current `_active_runtime_answer_points` preserves `point.text` but projects the canonical relation list, and `_validate_coverage_satisfaction` validates relation IDs and derives the relation-bearing `complete` value from those named checks. Parent `point.text` is context and provenance; it is not an independent second completeness axis.

The existing representation can express full extension enumeration, a construction-process check, and incomplete/uncertain dispositions. No structured-contract redesign is needed. The narrower correction is to keep output/property/list questions ordinary unless the user explicitly asks to establish a relation between distinct participants. Do not split canonical relations to evade all-to-all closure.

## 12. Current production prompt sufficiency

The production V1 prompt concatenates `EVIDENCE_REVIEW_SYSTEM_PROMPT` with `PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SYSTEM_PROMPT` prose. Static inspection confirms:

- Ordinary checks must be necessary, evidence-grounded and materially answer the point; all necessary checks need admitted satisfaction for completeness.
- Canonical checks must actually answer the canonical relation, including requested explanation; participant mentions and mappings alone cannot satisfy it.
- Basis must substantively ground the support judgment; selected supporters must collectively answer the full check.
- A single supporter must answer the entire check; necessary contributions/evidence must not be omitted to pass citation closure.
- Existing truthful unsatisfied/blocked/uncertain dispositions remain available.

The literal sentence "mapping relevance alone does not imply completeness" occurs in the separate shadow coverage prompt, **not in the production prompt's inheritance chain**. The attachment's shorthand is therefore not an exact production quotation. The production rules above nevertheless impose the relevant logical distinction. This precision does not weaken the sufficiency finding.

The V1 prompt remains sufficient for n006/n019 and is not the owner of the corrected n023 finding: it cannot recover semantics removed from D1. The D1 decomposition prompt does say that ordinary definitions, locators, API arguments and unstructured explanations use an empty relation list, and says not to invent an edge from a verb or property. It also permits input/output relations without explicitly distinguishing an output-set/property question from a relation between participants. The n023 realization demonstrates this generic category-boundary ambiguity. A clarification should state that enumeration/property/list requests such as which outputs, fields, branches or extensions remain ordinary unless the user asks to establish a relation itself; this is a generic boundary rule, not a PANDA-specific trigger.

```text
D1_RELATION_EXTRACTION_BOUNDARY_GAP = ESTABLISHED
D1_RELATION_SEMANTICS_PROMPT_GAP = NOT_ESTABLISHED
V1_PROMPT_CONTRACT_GAP_FOR_N006_N019 = NOT_ESTABLISHED
V1_PROMPT_ASSESSMENT = PROMPT_CONTRACT_ALREADY_SUFFICIENT / PROVIDER_COMPLETENESS_RELIABILITY_FAILURE
PROMPT_REPAIR_SELECTED = D1_BOUNDARY_DESIGN_ONLY / NOT_IMPLEMENTED
```

## 13. Deterministic host-guard assessment

`_validate_production_check` validates shape, bounds, exact basis quotations, visible IDs, admitted basis, supported/relevant parent mappings and individual all-to-all supporter citations. `_build_coverage_receipt` validates inventory/IDs, ordinary scope and duplicate text, derives supporter unions/completeness and checks submitted aggregates/missing-point complement. Its complete result follows validated checks' satisfied/admitted flags, with established scope for ordinary points.

Those rules work as specified on these receipts. They do not deterministically infer that a result schema is equivalent to a construction process, that a member declaration supplies an extension value, or that a setter comment proves full branch enumeration. No foreign ID, impossible aggregate, missing citation edge or admission contradiction supplies a generic host rejection here.

Raw point text, check wording, necessity prose, mapped claim text and evidence content are semantic inputs; they do not provide a machine-certified component inventory or exhaustive source interpretation. Correct paraphrases and abstraction levels vary. Keyword overlap, string containment, embedding thresholds, caveat-word vetoes, Gold nouns and PANDA-specific terms would create unsafe false exclusions. F/n019 also omits the caveat already in A0, so a caveat veto would not cover the confirmed family.

The host also cannot safely infer from the words `which`, `writes` or `branches` that D1 should have emitted an ordinary point. That is a decomposition/model-semantic decision, not a deterministic coverage-receipt invariant. A host check for this case would be a question-specific keyword guard and is rejected.

```text
HOST_DETERMINISTIC_COMPLETENESS_GUARD = NOT_JUSTIFIED
HOST_DETERMINISTIC_SCOPE_GUARD_NOT_JUSTIFIED = true
HOST_VALIDATOR_CONTRACT_REGRESSION = NOT_ESTABLISHED
```

No second reviewer, LLM judge, vote, best-of or post-V1 semantic stage is selected. No hidden retrieval retry is proposed; there is no separately justified deterministic trigger.

## 14. Retrieval geometry and G4 compatibility

### Saved opportunity ledger

Every row below is present in the saved channel trace and absent from saved legacy fused top 30, actual offered rerank pool, reranked candidates and final evidence. n019 rows have the same observed ranks/absence in O and F. Source versions are abbreviated only for readability: `18c09...` is `pandaroot@18c09e91100db27867ded30e708b4dae95bd8357`, and `11f1ed...` is `restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42`. The raw trace remains exact authority.

| Case | Object ID | Channel/rank; type | Source/version; locator/symbol | G4 classification |
| --- | --- | --- | --- | --- |
| O/n006 | `object.2914485ff398f61e994c46d6` | dense 9; function | PandaRoot `18c09...`; `tools/PndFileNameCreator.cxx:12-17`, `PndFileNameCreator` | NOT_ASSESSABLE |
| O/n006 | `object.9281add925687f506301e359` | graph 11; function | PandaRoot `18c09...`; same file `19-22`, `GetParFileName` | NOT_ASSESSABLE |
| O/n006 | `object.e0fb403c3760cf27980b7846` | graph 14; function | PandaRoot `18c09...`; same file `29-32`, `GetDigiFileName` | NOT_ASSESSABLE |
| O/F n019 | `object.83c5f288a2c09997ca9c36d0` | sparse 18; function_chunk | restgas_determination `11f1ed...`; `tracking/GenfitTools/recotasks/PndRecoKalmanTask.cxx:165-262`, `Exec` | NOT_ASSESSABLE |
| O/F n019 | `object.4103e48146ef09b48783a0c3` | sparse 19; function | PandaRoot `18c09...`; same task `.cxx:52-139`, `Init` | NOT_ASSESSABLE |
| O/F n019 | `object.6517cc5a47d460f57c6b4844` | sparse 20; function | restgas_determination `11f1ed...`; same task `.cxx:57-157`, `Init` | NOT_ASSESSABLE |
| O/n023 | `object.4fd2a5cf8c3a67d8f135cd9d` | dense 11; source_file_chunk | PandaRoot `18c09...`; `tracking/PndFtsTrackFinder/PndFtsTrackFinderTask.cxx:1-18`, symbol null | NOT_ASSESSABLE |

The n006 graph getter objects are distinct from its dense constructor. Historical shorthand grouping their appearances must not be read as identical object membership. No historical report is rewritten.

### Actual plans and offered pools

| Realization | Intent; required types | Source budgets | Offered pool composition |
| --- | --- | --- | --- |
| O/n006 | data_flow; workflow/code | workflow .35, code .30, graph .20, readme .10, paper .05 | 30 = 18 ordinary + 12 frontier |
| O/n019 | data_flow; workflow/code | workflow .35, code .30, graph .20, readme .10, paper .05 | 30 = 30 ordinary + 0 frontier |
| F/n019 | algorithm_implementation; none | code .40, paper .30, graph .15, documentation .10, workflow .05 | 30 = 22 ordinary + 8 frontier |
| O/n023 | module_structure; code/graph | code .35, graph .30, workflow .15, documentation .10, readme .10 | 30 = 19 ordinary + 11 frontier |

No reserved supplement occurs in these pools. n006/n023 target PandaRoot; n019 allows lumisoft/PandaRoot/restgas. Allowed source-version metadata does not prove semantic interchangeability. Same-question O/F n019 plans and frontier counts differ; neither is a controlled causal comparison of reviewer behavior.

### Current retention contract

Normal product retrieval uses the shared `_r2_rerank_pool`. It preserves eligible reserved supplements, an ordinary-base strict majority and bounded role frontiers. Challenger eligibility requires valid source/version/text/locator and appropriate origins: dense/sparse/exact/paper qualify under their regular route; workflow/graph require normal origin. Specialized origin/role can affect frontier eligibility. `_source_type_of` identifies source roles such as code, not semantic implementation depth.

Omitted queues use qualifying ranks, RRF score and object-ID tie order. Role quotas are bounded from budget/required roles and clipped to queue availability. The global frontier cap is an upper bound, not guaranteed occupancy. Accepted exchanges require nonworsening per-role/channel rank-witness vectors and strict improvement for the charged role; protected witnesses and finite round-robin/exhaustion further constrain replacements.

```text
FRONTIER_CAPACITY_IS_NOT_FRONTIER_ENTITLEMENT = true
COMMON_RETRIEVAL_POLICY_DEFECT = NOT_ESTABLISHED
G4_CONTRACT_VIOLATION_ESTABLISHED = false
EXACT_CANDIDATE_EXCHANGE_ASSESSMENT = NOT_ASSESSABLE
```

The saved standard trace exposes candidate rank/locator/version metadata but not the complete omitted candidate text, specialized origin, exact constructor queue inputs or per-exchange incumbent/victim witness vectors. `fusion_scores`/`fused_candidates` are saved legacy top 30, not the full constructor input. Thus this review cannot positively certify `G4_CONTRACT_COMPLIANT_OPPORTUNITY_LOSS` for a particular exact exchange, nor establish a violation. **NOT_ASSESSABLE** is the exact-contract classification for each listed candidate. The observed exclusion is compatible with a bounded retention contract; compatibility is not a reconstructed compliance proof.

The dense 9 / graph 11-14 constructor/getter family, sparse 18-20 mixed-repository function family, and dense 11 source-file chunk do not establish one generic current-policy error. Required/budgeted code role is active, but rank relevance does not entail promotion. These candidates were not protected ordinary top-30 witnesses, unlike the historical illegal collateral displacement corrected in G4. Historical n006 queue-position/quota explanations cannot be transplanted into O's different actual frontier output. G4's scoped current-lineage correction remains supported; historical exact replay remains unavailable.

Final evidence selection can use full fused order in fallback paths as well as the offered pool. Therefore outside-pool status alone is not proof of impossible final selection; actual saved final absence is checked separately here. No constructor replay, retrieval execution, quota expansion, source-specific reservation or new implementation-role heuristic is performed or selected.

## 15. Genericity and change threshold

The generic semantic observation is supported by three independent raw questions; ordinary scope weakening by two; the n023 D1 extraction boundary is a third mechanism. All are question-derived and require no protected data or Gold. They identify a repairable design surface, not an implemented fix.

The threshold for a narrow D1 boundary-design task is met by the G1 category rule, the exact n023 D1 loss, and the neutral analogies in the authorized review. The threshold for a V1, host, structured-schema or retrieval change remains unmet. A fixture that demands the observed PANDA literals, source paths, page locations, extra quotas or expected symbols would overfit measurement data.

Grounded partial assertions may remain relevant while the point is incomplete. Do not force unsupported-claim exclusion merely to imitate missing-point detection. Correct abstention must remain safe; a universal demand for deeper implementation evidence would harm valid high-level questions and schema questions.

## 16. Neutral future safety controls (design only)

These are expected properties for separately authorized future work. No fixture is implemented or run, and none is reported passing.

| Neutral scenario | Expected decision / control |
| --- | --- |
| Explicit enumeration; supplied definition states all requested values and claim enumerates them | Complete with adequate admitted proof; do not demand unrelated implementation internals |
| Explicit enumeration; supplied definition/claim gives only some values or unknown member names | Relevant partial claims retained; relevant point incomplete |
| Process requested; evidence gives only the output schema | Incomplete; type/field inventory must not substitute the process |
| Schema requested; same schema evidence | Complete when all requested schema components are supplied |
| Implementation location requested; only broad package mention available | Incomplete unless that mention actually resolves the requested locator |
| One explicit included subpart absent | Whole relevant point incomplete; unrelated complete points retained |
| Extra detail appears only in Gold, absent from raw question/D1 | No hidden runtime obligation or false insufficiency |
| Genuinely ambiguous, uncitable or incompatible evidence | Conservative disposition; no fabricated admitted witness or A1 entitlement |
| Broad explanation requested at an abstract level; coherent abstract evidence supplied | Complete when it answers that level; no blanket Exec/body requirement |
| Legitimate relational point with a stable canonical relation ID but only partial enumeration | Incomplete despite correct ID/mapping/closure; this remains a neutral control for relation semantics, not the corrected n023 category |
| Full canonical enumeration supported by one adequate shared basis | Complete; preserve the smaller-complete-proof invariant and exact quote closure |
| Several partial claims collectively supply all explicit parts with valid proof | Complete when the actual contract is met; do not require one artificial monolithic sentence |

Full/partial enumeration and process/schema pairs test opposite directions. A later implementation must justify a generic mechanism before treating these properties as its acceptance plan. No semantic judge, new provider stage or automatic retrieval retry is implicit in this matrix.

## 17. Candidate repair surfaces

| Candidate | Assessment |
| --- | --- |
| A: NO_CHANGE / PROVIDER_RELIABILITY_LIMITATION | Rejected after correction: n023 identifies a bounded D1 extraction-boundary design issue under G1 authority |
| B: V1 ordinary-check prompt repair | Not selected: no concrete missing generic rule; n023 is canonical, not ordinary |
| C: D1 relation-extraction boundary repair design | **Selected:** output/property/list questions should remain ordinary unless the user explicitly asks to establish a relation; implementation is not authorized here |
| D: question-derived ordinary obligation/schema redesign | Not selected: existing representation can express the needed obligations/dispositions once the point is classified correctly |
| E: residual retrieval role-opportunity repair | Not selected: heterogeneous geometries, incomplete exact exchange inputs, no common current-lineage contradiction or certified complete replacement witness |
| F: split responsibility / no single repair | Retained as the family-level causal description, but it is no longer the single next task: the corrected n023 boundary has higher causal leverage |

D1 boundary design is selected without changing source, prompt or schema in this task. A0 still lacks selected detailed evidence; forcing it to invent details is unsafe. Composer claims are preserved rather than first lost, and composer review is not a new full original-obligation auditor. Admission/host provenance do not originate the n023 boundary loss. No compensating downstream source/schema rewrite is selected.

## 18. Selected outcome and exactly one recommendation

**C — G5 D1 RELATION-EXTRACTION BOUNDARY REPAIR DESIGN.** The family-level split remains true, but the corrected n023 first owner selects one bounded next design task. It must cover generic output/property/list enumeration versus actual relational requests, without case-specific terms or runtime implementation in this task.

```text
SELECTED_REPAIR_SURFACE = D1_RELATION_EXTRACTION_BOUNDARY_REPAIR_DESIGN
NEXT_TASK_RECOMMENDATION = G5 D1 RELATION-EXTRACTION BOUNDARY REPAIR DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

This is a completed correction and design selection, not implementation. The selected next design requires separate authorization. The identifier design remains strict/no safe relaxation with its known false exclusions; this task supplies no authorization or mechanism to revisit it.

## 19. Retained limitations and static delivery validation

Semantic incompleteness remains on the exposed cases. Exact upstream text/constructor exchange evidence is unavailable in the bounded saved traces, fork equivalence is unresolved, and no guaranteed retrieval recovery is shown. n023's first owner is corrected to D1 relation extraction; the saved V1 acceptance is a downstream consequence of the weakened relation. No before/after answer metric, new empirical benefit or reliability rate is measured. Reasoned future controls are not tests. No new retrieval/body capture is requested merely to improve this report's evidence.

The original integrated run remains incomplete. The n019 absolute construction limitation coexists with its unchanged regression-relative control status; it does not revoke Rule 5 or targeted provenance mechanism support. The safe smaller-complete-proof result is preserved without reopening n022/n025/n028. No integrity contradiction requiring historical correction is established; historical prose, reports and raw stores remain immutable.

Delivery changes exactly this report and the two current-state documents. Static checks cover the allowed path set, retained prior checkpoint prose and historical chronology, corrected n023 fields, resolvable document links and `git diff --check`. No product imports, tests, validator calls or frozen acceptance comparison are performed. Commit message: `Correct n023 D1 completeness attribution`; delivery SHA is reported externally to avoid self-referential identity.

## 20. Lifecycle and boundary receipt

```text
G5_COARSE_COMPLETENESS_OVERACCEPTANCE_REPAIR_SURFACE_DESIGN = COMPLETE / CORRECTED / PASS
CORRECTION_STATUS = COMPLETE / CORRECTED / PASS
COARSE_COMPLETENESS_FAMILY = CONFIRMED_ON_N006_N019_N023
BOUNDED_QUESTION_COUNT = 3
BOUNDED_SAVED_REALIZATION_COUNT = 4
ORDINARY_CHECK_SCOPE_WEAKENING = CONFIRMED_ON_N006_N019 / N023_D1_RELATION_OVEREXTRACTION
N006_D1_CLASSIFICATION = D1_SUFFICIENT
N019_D1_CLASSIFICATION = D1_SUFFICIENT
N023_D1_CLASSIFICATION = D1_REQUIRED_RELATION_SEMANTIC_DEFECT / RELATION_OVEREXTRACTION
N023_FIRST_LIMITING_STAGE = D1_RELATION_EXTRACTION_BOUNDARY / REQUIRED_RELATION_SEMANTIC_NORMALIZATION
N023_FIRST_WRONG_STAGE = D1_RELATION_EXTRACTION_BOUNDARY / REQUIRED_RELATION_SEMANTIC_NORMALIZATION
N023_FIRST_WRONG_SEMANTIC_DECISION = D1_RELATION_OVEREXTRACTION / ORDINARY_ENUMERATION_MISCLASSIFIED_AS_RELATION
N023_V1_CANONICAL_OVERACCEPTANCE = DOWNSTREAM_CONTRIBUTOR / INDEPENDENT_V1_ERROR_NOT_ESTABLISHED
N023_DOWNSTREAM_WRONG_DECISIONS = V1_ACCEPTED_WEAKENED_CANONICAL_RELATION / POINT_COMPLETE
COMMON_D1_GRANULARITY_DEFECT = false
COMMON_D1_DEFECT = false
D1_RELATION_EXTRACTION_BOUNDARY_GAP = ESTABLISHED
D1_RELATION_SEMANTICS_PROMPT_GAP = NOT_ESTABLISHED
COMMON_RETRIEVAL_POLICY_DEFECT = NOT_ESTABLISHED
HOST_DETERMINISTIC_COMPLETENESS_GUARD = NOT_JUSTIFIED
V1_PROMPT_CONTRACT_GAP_FOR_N006_N019 = NOT_ESTABLISHED
STRUCTURED_ORDINARY_CONTRACT_REDESIGN = NOT_JUSTIFIED
SELECTED_REPAIR_SURFACE = D1_RELATION_EXTRACTION_BOUNDARY_REPAIR_DESIGN
IMPLEMENTATION_READY = false
TARGETED_V1_VERDICT = TARGETED_V1_MECHANISM_SUPPORTED
G5_POST_OBSERVABILITY_REPAIR_TARGETED_LIVE_VERIFICATION = COMPLETE / PASS / RULE_5
G5_IDENTIFIER_EVIDENCE_ELIGIBILITY_REPAIR_DESIGN = COMPLETE / PASS / NO_IMPLEMENTATION_READY
IDENTIFIER_ELIGIBILITY_DESIGN_OUTCOME = STRICT_RULE_RETAINED / NO_SAFE_RELAXATION
KNOWN_FALSE_EXCLUSION_FAMILY = F_N018 / O_N007
SAFE_RELAXATION = NOT_ESTABLISHED
N019_ABSOLUTE_SEMANTIC_LIMITATION = CONFIRMED / COARSE_WITNESS_OVERACCEPTANCE_WITH_EVIDENCE_GAP
SMALLER_COMPLETE_PROOF_SELECTION = SAFE_WITH_FROZEN_SEMANTIC_INVARIANT
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = G5 D1 RELATION-EXTRACTION BOUNDARY REPAIR DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false

PRODUCT_SOURCE_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
SCHEMA_CHANGE = false
CONFIG_CHANGE = false
DEPENDENCY_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
RAW_RUN_STORE_CHANGE = false
PRODUCT_BEHAVIOR_LINEAGE_CHANGE = false
V1_CONTRACT_CHANGE = false
NEW_PROVIDER_CALLS = 0
NEW_PROVIDER_PREFLIGHT_CALLS = 0
NEW_RETRIEVAL_RUNS = 0
NEW_TARGETED_LIVE_RUNS = 0
NEW_LOGICAL_CASE_ATTEMPTS = 0
NEW_GENERATION_PROVIDER_INVOCATIONS = 0
NEW_EMBEDDING_PROVIDER_INVOCATIONS = 0
NEW_SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
TEST_EXECUTIONS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
```
