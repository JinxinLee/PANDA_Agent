# G5 Integrated Failure-Family Review

## 1. Decision and authority

**Review scope: PASS / COMPLETE. Product repair and empirical recovery: NOT_ESTABLISHED.** This is an offline review and design recommendation, not an evaluation, replacement result, or authorization to implement.

Starting repository HEAD: `7326950d8531e53898910e9db5a2ee3fb39f34e1` (`Record the separate n018 rerun as a false insufficiency`). Product-behavior lineage remains `047201166057edd9859292a1760bc2e9bbf173a2`; normal mode remains `production_answer_obligations_v1`. The working tree was clean at entry.

The original G5 run remains **INCOMPLETE / PRODUCT ERROR**: 28 attempted, 27 usable results, one terminal nonretryable D1 exception. Its offline categories remain seven answered-complete, twelve answered-incomplete, seven false insufficiencies, one justified abstention, and one error. The later n018 result is a separately authorized false insufficiency, not a replacement in the original gate. Neither this review nor arithmetic across runs establishes G5 completion or G6 readiness.

The immediate recommendation is the separately authorized implementation of [the D1 diagnostic isolation design](G5_D1_DIAGNOSTIC_METADATA_ROBUSTNESS_REPAIR_DESIGN.md). After D1, recommend exactly one further design task: **G5 V1 DISPOSITION-PROVENANCE FALSE-INSUFFICIENCY REPAIR DESIGN**. Neither task is authorized by this review.

## 2. Evidence and method

Reviewed authority:

- [G5 integrated design](G5_INTEGRATED_CANDIDATE_DESIGN.md), [original report](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION.md), and [machine result](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION_RESULT.json).
- [Separate n018 report](G5_N018_SEPARATELY_AUTHORIZED_RERUN.md) and [machine result](G5_N018_SEPARATELY_AUTHORIZED_RERUN_RESULT.json).
- [G4 scoped live report](G4_POST_CORRECTION_TARGETED_LIVE_VERIFICATION.md) and [machine result](G4_POST_CORRECTION_TARGETED_LIVE_VERIFICATION_RESULT.json).
- [G1 design](G1_RELATIONSHIP_AWARE_ANSWER_OBLIGATION_DESIGN.md), [G2 design](G2_COVERAGE_REVIEW_LOCAL_FAILURE_ROBUSTNESS_DESIGN.md), and current status/roadmap.
- Current `question_decomposition.py`, relevant `qa.py`, production review prompt in `prompts.py`, runner identity/record behavior, and focused decomposition/G1/G2/QA tests, by static inspection only.

Both ignored stores are present: `data/evaluation/runs/g5-integrated-candidate-novel-dev-v1/` and `data/evaluation/runs/g5-n018-separately-authorized-rerun-v1/`. Saved records, retrieval traces, and stage traces were inspected for all 20 problematic original cases and supplemental n018. They remain unchanged. No trace was regenerated. For case `nNNN`, raw pointers are the applicable store's `records/nNNN.json` and its saved trace sidecars; the committed machine result supplies the durable case inventory, locators, and historical classifications.

The ledger below summarizes raw questions and canonical obligations rather than treating Gold points as runtime instructions. A0 denotes initial generated claims; A1 denotes the existing bounded revision, when reached. V1/V2 denote initial/revision verification. Retrieval observations distinguish channel presence, pool membership, final evidence, and citation. Absence is absence in the saved trace, not proof the corpus lacks the source. Static comparison of recorded supporter edges and quotes is not a new verifier execution.

Runtime differences between historical/targeted G4 and G5 remain an existing comparison confound. Original G5 and separate n018 share runtime package identity. No dependency investigation or alteration was needed to explain the observed provenance failures.

## 3. Case matrix

All rows below have historical expected status `answered` and independently answerable questions against locked evidence, subject to the stated scope caveats. `A` = actual `answered` but historically incomplete; `I` = actual `insufficient_evidence`; `E` = terminal error. FI means independently answerable false insufficiency, not permission to accept malformed coverage. `VALID k/k` records runtime acceptance, not offline completeness. Owners are forward diagnostic refinements; historical results are not rewritten.

| Case / expected -> actual | Independent answerability | Critical missing content | Critical evidence availability | Earliest supported owner | Secondary owner | Family | Runtime coverage | FI | Candidate generic repair | Confidence / authority limitation |
|---|---|---|---|---|---|---|---|---|---|---|
| n001 answered -> I | Yes; branch wording caveat | FairSoft/FairRoot pairings, environment/branch account | Exact script final; not cited | Q1 requested-symbol veto | C1/final response; Gold/source conflict | C, authority | V1 not reached | Yes | Requested-symbol sufficiency review | High veto; Bash execution conflicts with Gold branch wording |
| n003 answered -> A | Yes | Per-event stepping/increment/rollover detail | Implementation dense 16; not pool | R2 role loss | GENERATION/depth | D | VALID 2/2 | No | Retrieval role opportunity review | High loss; internal API depth exceeds explicit configuration request |
| n005 answered -> A | Yes | Exact implementation/Setup chain | Specific tools macro absent from channels; similarly named distractors present | R1 source-role gap | GENERATION/depth | D | VALID 2/2 | No | Recall/role review | Medium causal scope; explicit opening procedure largely supplied |
| n006 answered -> A | Yes | Literal stage extensions | Implementation dense 9, graph 11/14; not pool | R2 | V1 completeness | D, semantic | VALID 2/2 | No | Role opportunity and explicit-enumeration completeness review | High; D1 already captures extensions |
| n007 answered -> I | Yes | Verified full detector-path resolution | GetPath method documentation final/cited | V1 deterministic identifier rejection | A1/V2 | C | V1 then V2; resolution missing, state complete | Yes | Qualified-identifier evidence review | High; distinct from LOCAL_INVALID supporter family |
| n008 answered -> A | Yes | Low-hit operating limitation/comparison depth | Cited thesis includes low-hit qualification | GENERATION depth | V1 narrow acceptance | B | VALID 2/2 | No | Question-bounded completeness review | Medium; quantitative Gold depth is not separately requested |
| n009 answered -> I | Yes | Added beam-momentum uncertainty | Selected thesis lacks added uncertainty; implementation absent channels | R1/source-role availability; Q2 root unresolved | A1/V2 insufficient basis | D, unresolved | V1/V2 VALID receipts; point 4 incomplete | Yes | Source-role diagnosis | Medium; missing implementation does not itself explain thesis uncertainty loss |
| n010 answered -> A | Yes | Detector/response object chain | Critical implementation symbols absent channels | R1 | GENERATION/V1 depth | D | VALID 2/2 | No | Recall/role review | Medium; no proven D1 lost explicit clause |
| n014 answered -> I | Yes, resolved | Explicit model_framework repository identity | Locked README absent from trace | R1 | A1/V2 | D | V1/V2 VALID receipts; point 1 incomplete | Yes | Recall review | High source gap; no remaining answerability uncertainty |
| n018 original answered -> E | Yes, from independent locked evidence | Entire runtime answer | Retrieval not reached | D1 diagnostic validation / PROVIDER_PRODUCT_ERROR | None observed | A | None | No: error | Diagnostic isolation | High exception; original semantic proposal never saved |
| n019 answered -> A | Yes | Actual persisted-result construction | Early implementation chunks final; relevant body sparse 18-20 excluded | R2 relevant-body loss | V1 completeness | D, semantic | VALID 4/4 | No | Role opportunity and explicit-construction completeness review | High; D1 already separates four requested components |
| n020 answered -> A | Yes | Final-fit configuration under historical Gold | README and macro final/cited include final fit | GENERATION depth under Gold | V1 depth; authority limit | B | VALID 3/3 | No | Question-bounded completeness review | High availability; final fit is temporal context in raw question |
| n021 answered -> A | Yes | Specific sim/digi/reco implementation locations | LMD CMakeLists absent trace | R1 | D1 granularity candidate/V1 | D, semantic candidate | VALID 2/2 | No | Recall and independent-location obligation review | Medium; no demonstrated causal D1 defect |
| n022 answered -> I | Yes | Accepted worker-output relation; fallback detail under Gold | Main workflow already final/cited; ana_dpm.C absent | V1 nonexact quote declaration | Gold depth/source-role limit | C | PARTIAL: point 1 LOCAL_INVALID BAD_QUOTE; point 2 valid | Yes | V1 disposition provenance | High refusal cause; historical R1 label is not overwritten |
| n023 answered -> A | Yes | Literal FtsTrackAnalytic branch; payload detail | Finder implementation dense 11; not pool | R2 | V1 completeness | D, semantic | VALID 2/2 | No | Role opportunity and branch-enumeration completeness review | High name gap; payload types are additional Gold depth |
| n024 answered -> A | Yes | Matrix transport/backwards mode detail | Both propagators final/cited; helix retained through ordinary RRF pool | GENERATION depth | V1 completeness/authority limit | B | VALID 3/3 | No | Question-bounded state-explanation completeness review | High availability; no R2 contradiction; exact matrix/mode obligations not explicit |
| n025 answered -> I | Yes | Accepted efficiency/tradeoff explanation; solution-count detail under Gold | Core radial/CA/displaced content and solution count cited | V1 supporter/basis declaration | GENERATION depth; D1 granularity candidate | C, B | PARTIAL: point 1 LOCAL_INVALID INVALID_SUPPORTER | Yes | V1 disposition provenance | High refusal cause; one tradeoff explanation need not split mechanically |
| n028 answered -> I | Yes | Accepted downstream decision exposure; producer/tuple depth | Header/macro final; producer sparse 18 and consumer graph 5 excluded | R2 for implementation omission | V1 supporter/basis declaration causes refusal | D, C | PARTIAL: point 1 valid; point 2 LOCAL_INVALID INVALID_SUPPORTER | Yes | V1 disposition provenance; separate retrieval diagnosis | High dual contribution; no causal recovery count |
| n029 answered -> A | Yes | RingSorter/ring-cell/time ordering mechanics | Locked implementation absent trace | R1 observation; Q1/Q2 root unresolved | GENERATION/V1 depth | D, unresolved | VALID 1/1 | No | Recall/root-cause review | Medium; not proof of one specific query-planning defect |
| n031 answered -> A | Yes | Prior DPM and scan subcategory distinctions under Gold | Relevant category/scan/history sources final/cited | GENERATION depth | V1 narrow basis/authority limit | B | VALID 2/2 | No | Question-bounded comparison completeness review | High availability; history and both scan subtypes not separately asked |
| n018 separate answered -> I | Yes | Accepted whole-tree comparison; EvtGen/PDG preparation under Gold | Locked tutorial final/cited | V1 supporter/basis declaration causes refusal | GENERATION preparation depth | C, B | PARTIAL: point 1 valid; point 2 LOCAL_INVALID INVALID_SUPPORTER | Yes | V1 disposition provenance | High; supplemental provenance only, original D1 semantics unknown |

## 4. Stage-chain ledger

Each entry carries the raw request through the saved canonical inventory, evidence, generation, verification/revision, and final status. Content not reached is stated explicitly.

### n001, n003, n005, n006

- **n001:** Request: GSI RestgasDetermination FairSoft/FairRoot pairs and paths, configSettings.sh variables, and unmatched behavior as written. D1 has those three needs, including the pairing relation. Script `object.50d52a0c234701fb6654a245` appears dense 1/exact 1/sparse 7, enters pool/rerank/final, but is not cited. Requested-symbol sufficiency rejects `FairSoft` before A0/model V1; no revision/V2. The insufficient final response contains installation context instead. This is an early Q1 veto, not unavailable downstream evidence or proven decomposition loss. The script's Bash syntax error qualifies Gold's execution narrative, without removing other answerable requests.
- **n003:** Request: identify the generator and configure fixed-step momentum/theta on each event. D1 separates identity and configuration. The critical `.cxx` (`object.7329dd15f58b29f584d01169`) is dense 16, absent from pool/rerank/final. A0 supplies `PndFixStepParticleGun`, `SetPRange`, `SetThetaRange`/`SetCosThetaRange`, but not `ReadEvent`/`CalcActValues` increment/rollover. V1 accepts 2/2; no A1/V2; final answered-incomplete under existing review. Source loss is observed; requiring internal method names as independent runtime needs would exceed the raw configuration question.
- **n005:** Request: display events/geometry and open an event file. D1 has tool and opening procedure. The specific `macro/tools/eventDisplay.C` is absent from the trace. Other eventDisplay.C files (DISC dense 15, EMC dense 19) are distractors, not the missing tool source, and do not enter pool. A0 gives EventDisplay, the tools macro, prefix/default, and sim/digi/reco loading from documentation. V1 accepts 2/2; no revision; final answered. Missing `PndMasterRunAna::Setup` chain is historical Gold depth, not an explicit extra raw-question obligation.
- **n006:** Request: helper deriving sim/digi/reco/pid filenames and its stage extensions. D1 explicitly captures extensions. `.cxx` `object.2914485ff398f61e994c46d6` appears dense 9 and graph 11/14, then disappears before pool. A0 gives getters/members and acknowledges literal defaults are unestablished. V1 nevertheless accepts 2/2; no revision; final answered without trackF, idealTrackF, riemann, combRiemann, kalman, vertex. R2 is the earliest observed loss; V1's coarse acceptance is a distinct explicit-semantic gap.

### n007, n008, n009, n010, n014

- **n007:** Request: resolve a shortID to full detector path and specify initialized state first. D1 separates resolution from prerequisite/order. Documentation has `GetPath(Int_t shortID)` in final/cited evidence; the generated qualified token `PndGeoHandling::GetPath` is not literally present in its cited joined text. Deterministic identifier validation rejects that claim before model V1. V1 sees the remaining state claim and validly authorizes an admitted unsatisfied resolution target; one A1 repeats the qualification failure. V2 leaves resolution incomplete, state complete; final insufficiency retains the state claim. This is an identifier representation boundary, not the PARTIAL/INVALID_SUPPORTER path.
- **n008:** Request: name LMD track-search algorithms and compare them. D1 contains identity plus one comparison relation. A0 explains track following/cellular automaton and multiplicity tradeoffs. Cited thesis `object.03162881f60d1c981e85d4b7` also contains low-hit constraints. V1 accepts 2/2; no revision; final omits that qualification and quantitative depth. Available-source generation omission is supported; a new required numerical performance obligation is not derived from the raw question.
- **n009:** Request: alternative to DPM, implemented code, intrinsic parameter uncertainty, and added beam-momentum uncertainty. D1 has all four. Selected thesis supports E760 and intrinsic uncertainty; final `object.4aa...` does not supply the added beam uncertainty. E760 implementation does not appear in channels. A0/V1 and one A1/V2 occur; final review receipts are VALID but point 4 remains insufficient/ambiguous, with missing-point/irrelevant-claim diagnostics. Final retains the supported alternative/implementation/uncertainty content and refuses overall. Missing implementation alone cannot explain missing thesis uncertainty: source-role availability is observed, exact Q2/recall cause unresolved.
- **n010:** Request: fastsim response mechanism and building blocks. D1 separates mechanism and composition relation. `PndFsmAbsDet`, `PndFsmDetFactory`, `PndFsmResponse` are absent from channels; A0 gives acceptance/smearing, PndFastSim/FairRunSim and detector blocks. V1 accepts 2/2; no revision; final misses the object/response chain. R1 availability gap precedes generation depth; no explicit clause is demonstrably absent from D1.
- **n014:** Request: explicit repository description of model_framework and modelFactory role. D1 has both. Locked `object.6250849152b18c0c068abe5e`, `model_framework/README.md:1-4`, describes the archived ModelFramework working copy, but is absent from retrieval. A0/V1 and one A1/V2 cannot establish point 1; point 2 is complete in VALID receipts. Factory content remains in final insufficiency. Independent answerability is resolved by the README, not an evaluator uncertainty.

### n018 original, n019, n020, n021

- **n018 original:** Request: individual MC-truth counterpart and whole reconstructed/generated tree comparison. The recorded error rejects diagnostic `ambiguity.status="none"` against the two-value literal. It precedes retrieval, graph execution, A0/V1/A1/V2/finalization. No raw proposal or canonical semantic inventory was persisted for this failed call. This proves a diagnostic fatality, not that the original points/relations would pass or that fallback guarantees an answer.
- **n019:** Request: input PndTrack to fitted output, including fitter selection, hypothesis, and construction of each persisted result. D1 has four components. Early `.cxx` exact 3 (`object.796...`, start 38) reaches pool/rerank but not final; exact 5 (`object.b54...`, start 39) reaches final/citation. Relevant body chunks sparse 18 (`object.83c...`, start 165), 19 (start 52), 20 (start 57) do not enter pool. A0 gives array/type, fitter flags/default 211, output fields, and acknowledges missing Exec body. V1 accepts 4/4; no revision; final lacks actual construction. R2 body loss and V1 explicit completeness both matter; more D1 splitting is not justified here.
- **n020:** Request: leftover collector and each displaced finder/z-recovery contribution before final fit. D1 correctly separates three contributions. Final/cited README `object.48be486a9ecab8f524ef9f35` and macro `object.08993f3edcaf98c42a3bdf34` include `PndRecoKalmanTask2` and `SetPropagateToIP(kFALSE)`. A0 covers the three asked contributions; V1 accepts 3/3; no revision. Historical answered-incomplete omits final-fit detail, but raw wording makes final fit temporal context rather than an independently requested configuration. Do not manufacture a fourth point from Gold.
- **n021:** Request: PandaRoot locations implementing LMD sim/digi/reco and LumFit scripts in sequential workflow. D1 has one stage-location point and one script-order relation. LMD CMakeLists is absent; A0 gives sim macro/general SDS context and ordered script names. V1 accepts 2/2; no revision; final incomplete. Three requested stage locations merit neutral granularity scrutiny, but absent sources prevent attribution of recovery to D1 alone.

### n022, n023, n024, n025

- **n022:** Request: second-step worker outputs and feeding fitted vertex into reprocessing. D1 has both relations. A0 gives actual JSON/ROOT tree outputs and FIT_VERTEX_* / POCA_VERTEX_FILE / event-ID propagation from final evidence. `ana_dpm.C` is absent, but the central workflow is already downstream. V1 point 1 relation fails BAD_QUOTE: the saved 295-character quote is not a contiguous exact substring of its declared evidence. Point 2 is valid; both claims deterministically supported and rendered. No valid revision target, hence no A1/V2. Final insufficiency is a provenance-declaration failure; historical R1/fallback-depth notes remain diagnostic, not the proximate refusal cause.
- **n023:** Request: source locator and branches written by the FTS finder. D1 has two points. `.cxx` `object.4fd2a5cf8c3a67d8f135cd9d` is dense 11, absent pool. A0 gives FtsTrack/FtsTrackCand and variable fOutAnalyticBranchName, without literal FtsTrackAnalytic or payload detail. V1 accepts 2/2; no revision; final incomplete. Literal branch enumeration is explicit; payload-type expansion is Gold depth and must not create hidden D1 authority.
- **n024:** Request: identify two propagators and explain how each determines transported state. D1 has identity and separate GEANE/helix explanations: it does not merge both into one explanation. GEANE `object.b92e31dcb2ee34a46234ac0f` is final/cited and contains `fInErrorMatrix`/`fTransportMatrix`; helix `object.d6ef560b88c3926ecb32d3e1` contains `fBackPropagate`. Helix dense 8/sparse 19, fused rank 18, survives as ordinary RRF, reranks at 2, reaches final/citation. A0 gives shared interface, numerical ERTRAK/RungeKutta and analytical circle mechanics, without matrices/backward mode. V1 accepts 3/3; no revision. This is a downstream depth/completeness control, not a G4 R2 breach. Exact matrix/mode obligations are not separately explicit in raw wording.
- **n025:** Request: tangency triplets manage combinatorics while remaining efficient for displaced vertices. D1 gives one tradeoff explanation; automatic splitting is not required by G1's mechanism rule. A0 covers radial partition, CA neighbor-phi, no nominal-IP assumption, growth/quality. Cited source also contains up-to-eight solutions; that number is background depth rather than a separately asked count. V1 ordinary point's second check lists two basis IDs, but `claim.1` does not cite `evidence.1b1c6c7f25d05af9ea662bd5`. INVALID_SUPPORTER is correct under the existing edge rule. All three claims remain supported/rendered; no A1/V2; final insufficiency. No missing retrieval is needed to explain this local refusal.

### n028, n029, n031, supplemental n018

- **n028:** Request: produce triggers and expose OnlineFilterInfo decisions downstream. D1 has ordinary production and separate exposure relation. Producer `.cxx` sparse 18 and consumer `.cxx` graph 5 are absent pool; header/macro are final. A0 gives tasks/config, counts container, downstream task/query methods but lacks producer registration/tuple detail. V1 point 1 valid; point 2 relation names `claim.2` as supporter of `evidence.5aec65f04ec751097c07fbd4`, which that claim does not cite. PARTIAL/INVALID_SUPPORTER blocks complete coverage; all three supported claims render, no A1/V2. Retrieval loss precedes detailed omission; a separate malformed declaration causes refusal.
- **n029:** Request: time-based interleaved detector data sorting into processing order. D1 has one mechanism need. Locked RingSorter header/implementation are absent trace; A0 gives generic buffers/GetData/task sorting without ring cells/AddElement/WriteOutElements/timestamp multimap. V1 accepts 1/1; no revision; final incomplete. R1 absence is observable; exact Q1/Q2 ownership is not established.
- **n031:** Request: compare realistic background/signal/simple scans and name current standard background. D1 has category comparison and standard identity. Relevant sources `object.24a...`, `object.ddc...`, `object.ab4...`, `object.8aa...` reach final/citation, including prior DPM and random-box/fixed-step detail. A0 gives three categories and FTF; V1 accepts 2/2 from a narrower background/event basis, despite broader claim citations; no revision. Historical finer distinctions/history are omitted. This supports scrutiny of generation/comparison depth, not Gold-derived mandatory history or scan-subtype points.
- **n018 separate:** Same raw two-part request, now two canonical points including whole-tree relation. Tutorial `object.917...` reaches final/citation, including preparation. A0 supplies GetMcTruth null checking, McTruthMatch and composite types, but not EvtGen/PDG preparation. V1 point 1 valid; point 2 relation selects the preparation claim as supporter of RST basis `evidence.0e87ee452eca4d3f8a836620`, which it does not cite. The full-tree claim cites that basis, but each named supporter must do so individually. PARTIAL/INVALID_SUPPORTER; three claims supported/rendered; no A1/V2; final insufficiency. This is a C/B diagnostic, not proof the original D1 defect is repaired.

Controls: original n016 remains a justified abstention; it is excluded from the problematic matrix. n004's historical identifier/independent-validity caveat remains a control limitation, not a new failure. Complete cases and n002/n017 G4 benefit opportunities are not recategorized. No G4 scoped verdict is altered.

## 5. Generic families and bounded counts

Counts below overlap. They describe observations/opportunities, not predicted recovered answers.

| Generic family | Evidence-bounded count | Interpretation and candidate mechanism |
|---|---|---|
| A: diagnostic-only D1 fatality | 1 original exception | Production-local diagnostic fallback can intercept this validation class if semantics are otherwise valid. Original semantic validity and recovered QA outcome are unknown. |
| Question-derived inventory loss | 0 conclusively demonstrated; n021/n025 are granularity candidates | D1 already captures explicit subrequests in n006/n019/n023/n024 and separate n018. Do not rebrand all 12 historical incomplete answers as decomposition failures. |
| B: final/cited evidence with omitted depth | 5 original examples: n008/n020/n024/n025/n031; plus supplemental n018 | Generation/completeness review is warranted, but omitted Gold details are not uniformly explicit runtime needs. No numerical recovery claim. |
| Explicit need represented, yet accepted too coarsely | 3 original strong candidates: n006/n019/n023 | V1 accepts incomplete extension/construction/branch enumeration; retrieval loss also exists. These are semantic acceptance candidates, not proof of a host-validator bug. |
| C: PARTIAL provenance causing refusal | 3 originals: n022/n025/n028; plus supplemental n018 | Nonexact quote or supporter-to-basis cite mismatch. Small V1 output-contract reliability design is justified. Exact proof checks must remain. |
| C: separate deterministic identifier boundary | 1 original: n007 | Qualified identifier rejected against documented unqualified method. Keep separate from supporter repairs. |
| G2 finalization erasure | 0 observed among the 4 PARTIAL records | All independently supported claims remain rendered; LOCAL_INVALID still blocks completeness. No demonstrated erasure correction to implement. |
| D: residual retrieval availability/opportunity | 11 originals: R1 observations n005/n009/n010/n014/n021/n029; R2 losses n003/n006/n019/n023/n028 | Some source-role depth exceeds raw-question scope; precise upstream query cause unresolved for n009/n029. Not 11 guaranteed retrieval recoveries. No unique R3 defect established. |
| Authority/unresolved | 1 actual Gold/source conflict (n001); 9 scope caveats including supplemental n018; 2 unresolved upstream roots; 1 missing original semantic proposal | Scope caveats n003/n005/n008/n020/n022/n024/n025/n031/separate n018 are not nine new Gold conflicts, waivers, or dataset changes. Categories overlap. |

### Family A: diagnostic metadata is not semantic inventory

`QuestionDecomposer.decompose` validates `_Ambiguity` before canonical point/relation validation. The production provider schema permits any status string; local `_Ambiguity` permits only `clear`/`ambiguous`. `_run_detailed` projects only `decomposition["points"]` into graph state and uses ambiguity only in diagnostic output. Thus `none` can terminate QA without exercising retrieval or authoritative semantics. The selected D1 repair isolates metadata after semantic validation; it does not soften semantic failures.

### Families B and semantic granularity: retain raw-question authority

G1 requires one completeness path per point and independent explicitly requested contributions. Its prompt also keeps a general "how X works" request as one explanation, without inventing hidden prerequisites. n020's final fit, n024's exact matrices/backward mode, and n031's prior generator history are source-supported Gold depth, but not independently stated requests. Historical incomplete verdicts remain; this review cannot convert their Gold detail into runtime requirements.

The saved raw questions provide the boundary directly:

- **n020:** "In the restgas determination analysis, the standard track finder leaves part of the hits unassigned. Which task picks up those leftover hits, and what do the downstream displaced-track finder and z-recovery stages each contribute before the final fit?" Its three canonical points correspond to collector, displaced finder, and z-recovery; all are relation-free. The final-fit phrase scopes their contributions.
- **n024:** "PandaRoot can transport tracks through the magnetic field either with GEANE or with an analytic helix. What are the two propagators behind these options, and how does each determine the transported track state?" Its three canonical points are separate GEANE explanation, separate analytic-helix explanation, and propagator identity; all are relation-free. The inventory already separates "each". State-explanation depth merits scrutiny, but matrix/backwards implementation specifics are not separately named.
- **n031:** "For different studies I need realistic background, one specific signal channel, and simple particle scans. How do PandaRoot's event-generator categories differ, and which generator is the current standard for background?" Canonical point 1 owns one category-comparison relation, point 2 owns the current standard identity. The raw request does not independently ask former-generator history.
- **n025:** "The displaced-track finder in the restgas branch builds candidates from triplets of STT drift circles by solving the classical Apollonius tangency problem. How does it keep the triplet combinatorics manageable while staying efficient for displaced vertices?" The single relation-free canonical explanation covers the combined tradeoff. Two explicitly contrasted concerns can motivate a neutral completeness fixture; the saved failure does not prove splitting them would repair its invalid supporter.
- **n021:** "I want to trace the LMD workflow across PandaRoot and LuminosityFit. Where does PandaRoot implement the LMD simulation, digitization, and reconstruction side, and which LuminosityFit scripts orchestrate simulation/reconstruction and then the luminosity fit?" Stage locations share point 1; ordered script orchestration owns point 2's relation. Independent stage-location omission is a plausible granularity question, with missing evidence as a confound.

Useful next semantic work would use neutral questions with explicit enumeration/ordering/state-transfer clauses and verify that each explicitly requested component has a question-derived completeness check. Current evidence does not establish that broad D1 regranulation is the smallest common fix. n006/n019/n023 show that adding more points need not solve V1 acceptance or unavailable source detail.

### Family C: support containment succeeds; coverage reliability does not

`_validate_production_check` requires each supporter to exist, remain unexcluded, map to the canonical parent, and cite every declared basis ID; quotes must be exact contiguous substrings within the existing length bound. The recorded n025/n028/separate-n018 edges violate that rule, and n022 violates quote exactness. INVALID_SUPPORTER alone did not establish a code bug; these concrete edge comparisons identify malformed provider declarations.

G2's PARTIAL path preserves independently valid mapping/support results. `_finalize` renders supported claims with the incomplete notice when coverage is blocked; it bypasses the composer in this path. Observed retained counts are n022 2, n025 3, n028 3, separate n018 3. Thus the invariant "one LOCAL_INVALID must not erase unrelated deterministically verified claims" holds in these records. Overall insufficiency remains conservative because invalid review cannot certify its own need or authorize an invalid revision target. Existing valid-sibling target-local A1 and full-contract V2 safeguards remain.

### Family D: residual opportunity is not a G4 contradiction

n024's dense/sparse rank witness survives pool, rerank and final citation. Other R2 candidates lack an established identical qualifying exchange geometry proving violation of G4's retention contract. Existing role ceilings, strict RRF majority, pool bound, rank-witness protection, admission, and R3 selection are not reopened. Retrieval review would need a separate generic opportunity/root-cause hypothesis, not source quotas or expected paths copied from these cases.

## 6. One post-D1 recommendation

**G5 V1 DISPOSITION-PROVENANCE FALSE-INSUFFICIENCY REPAIR DESIGN**, design only, under separate authorization.

Why V1 next: three original PARTIAL refusals and supplemental n018 share directly observed malformed disposition provenance, with useful answerable content already downstream. This is more concrete than a common D1 granularity defect or finalization erasure. The design should investigate the smallest production-review contract clarification that makes each check's supporters, basis IDs, and exact quote align with already emitted claims and canonical parents. Establish with synthetic examples whether prompt/contract guidance alone suffices; select a bounded remedy only after that analysis. Do not pre-authorize a new provider retry or host recovery mechanism.

Motivating cases: n022 (quote exactness), n025 and n028 (supporter/basis mismatch), separate n018 (same edge mismatch with adequate final tutorial). n028 also retains independent retrieval limitations; this recommendation does not promise its full detail recovery. It does not claim to solve original n018 D1, n001 early veto/source conflict, n007 identifier qualification, missing-source R1/R2 cases, or all generation/Gold depth omissions.

Safety invariants remain: every supporter must cite every selected basis; exact quotes remain exact; parent/ID authority remains canonical; unsupported claims never render; LOCAL_INVALID is never complete or self-authorizing; ambiguous/uncitable needs are never silently filled. No union-citation shortcut, dropping inconvenient supporters/bases, or automatic answered status based on surviving claims. Preserve G1's single completeness path, G2 valid-sibling A1, one existing revision, and full-contract V2.

Before any separately authorized live run, proposed deterministic/synthetic verification should use Cedar/Birch-style fixtures: valid multi-supporter basis alignment; incorrect individual edge despite union coverage; nonexact quote; forged/cross-parent IDs; absent supporter; partial local invalidity with valid claims still rendered; valid sibling's admitted-unsatisfied revision; no target from invalid disposition; unsupported-claim exclusion; unchanged full V2 recheck. Compare model-facing contract examples statically and host validation behavior with fake providers. This review executes none of those tests or models. Any future live verification requires explicit scope and cannot be inferred from design completion.

## 7. Boundaries, cost, and limitations

```text
G5_FAILURE_FAMILY_REVIEW = COMPLETE / PASS
G5_D1_REPAIR_DESIGN = COMPLETE / IMPLEMENTATION_READY
PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
DEPENDENCY_CHANGE = false
NEW_RUNTIME_MODE = false
QA_RUNS = 0
RETRIEVAL_RUNS = 0
SCIENTIFIC_GENERATION_CALLS = 0
SCIENTIFIC_EMBEDDING_CALLS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
TEST_EXECUTIONS = 0
NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = G5 D1 DIAGNOSTIC-METADATA ROBUSTNESS REPAIR IMPLEMENTATION
POST_D1_REPAIR_DESIGN_RECOMMENDATION = G5 V1 DISPOSITION-PROVENANCE FALSE-INSUFFICIENCY REPAIR DESIGN
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

No result remains unresolved because either raw store was unavailable: both were available. Original n018's raw semantic proposal was never persisted; no reconstruction is claimed. Exact upstream roots for n009/n029, prospective repair efficacy, and the raw-question significance of some Gold depth remain unresolved. Historical environment confounding remains. No before/after empirical metric exists for this review; original and separate-run metrics remain their own authorities. Phase G is not complete; G6 is blocked. Only the two review/design documents and current-state sections of status/roadmap are delivered.
