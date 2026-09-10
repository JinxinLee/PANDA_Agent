# E2-A3-R3-R1-FR1 — G11 Failure Review and Activation Decision Reassessment

## Decision and immutable authority

Review scope: **PASS**. Overall decision:
**PRODUCT_REPAIR_AND_GATE_REDESIGN_RECOMMENDED**.

Product decision: **G11_PRODUCT_REPAIR_JUSTIFIED**, narrowly for generic,
shared deterministic claim sanitization (A1), not a common g001/g029 defect.
Gate decision: **G11_GATE_REDESIGN_JUSTIFIED**, prospective only.

Starting HEAD `7caded39baa9208be4a349a9e6cccc71fc52112a` was clean.
Current product remains `fd0aed4c7e491a569bf39271825cc0950630863d`.
Historical R3-R1 is permanently COMPLETE / FAIL / G11: 1 better, 11 equivalent,
2 worse; 14 authoritative pairs/judgments; critical runtime regressions 0;
runtime support 14/14; G1-G10/G12-G13 PASS. No rescore, waiver, gate change,
product change or activation occurs. A3 FAIL, R1 FAIL, R2 PASS and R3 INCONCLUSIVE
remain intact. This report does not turn diagnostic interpretation into a new
scientific judgment.

Sources are committed artifacts. g029 uses original protocol `0a276a40968ed67fb784c37676d172314fb1210d`,
raw `6d760be1eae1e803d8f6c4ff6b374a13dbed4713`, judged `77388ec9c2564cce82d0db24ef97a15da62d4779`.
g001 uses recovery protocol `3a93f081a77e8bb507b14729a981dc1fa9c1f449`,
raw `0bc039d39211540843863d73ef9dd2be430087cd`, judged `5f260a3fa92ade82528825669e0f5360fe1bc34e`.
The companion JSON preserves exact Gold, both complete raw records (selected
text/locators, initial responses, reviews, revisions, decomposition, mapping,
final claims/answer/citations) and complete blinded judge input/output for both
cases. Raw request bytes are not captured: generator-input availability is
reconstructed from frozen code, plan, evidence and admission records, not
misrepresented as an exact recorded request.

## g029: exact reconstruction before interpretation

Question: Where is PndLmdCombinedDataReader defined and what data boundary does it implement?
Gold: locate it in LuminosityFit and explain the boundary from PandaRoot LMD QA
products to LuminosityFit data objects. Required identifier: PndLmdCombinedDataReader.
Required code evidence includes data/PndLmdCombinedDataReader.cxx.
Original index 9: A=runtime, B=legacy. Both supported, preferred B,
critical_regression=false.

Frozen judge reason:

> Both models answer the question accurately and are fully supported by their citations, but Model B provides a cleaner, more complete explanation of the data boundary without the awkward phrasing found in Model A.

### legacy_question_core — exact final public answer

```text
PndLmdCombinedDataReader is defined in the luminosityfit repository in data/PndLmdCombinedDataReader.h and implemented in data/PndLmdCombinedDataReader.cxx as a subclass of PndLmdDataReader. [evidence.77284586a783f77f2d51cd36, evidence.772bd06fada5d9bc168d9077, evidence.0e7f3d179f9feb50000a6ca2]
PndLmdCombinedDataReader interfaces with ROOT tree input by initializing a TChain named pndsim and reading PndLmdTrackQ objects from the LMDTrackQ branch into a TClonesArray. [evidence.0e7f3d179f9feb50000a6ca2, evidence.182c767781622298d12916b2]
Through getEntry(), PndLmdCombinedDataReader converts the PndLmdTrackQ data into a collection of Lmd::Data::TrackPairInfo objects that map reconstructed and Monte Carlo position and momentum at both the interaction point (IP) and the luminosity monitor (LMD). [evidence.77284586a783f77f2d51cd36, evidence.0e7f3d179f9feb50000a6ca2]
```

### runtime_e1_v2 — exact final public answer

```text
PndLmdCombinedDataReader is defined in the luminosityfit repository within data/PndLmdCombinedDataReader.h and data/PndLmdCombinedDataReader.cxx. [evidence.77284586a783f77f2d51cd36, evidence.0e7f3d179f9feb50000a6ca2, evidence.772bd06fada5d9bc168d9077]
PndLmdCombinedDataReader inherits from PndLmdDataReader and implements a data boundary that reads PndLmdTrackQ objects from the LMDTrackQ branch of a pndsim TChain and unpacks them into an internal support type<Lmd::Data::TrackPairInfo> records. [evidence.77284586a783f77f2d51cd36, evidence.0e7f3d179f9feb50000a6ca2, evidence.772bd06fada5d9bc168d9077]
```

### Interpretation and stage trace

Classification **C — material optional elaboration improving user utility**.
Legacy explicitly describes reconstructed/Monte Carlo position and momentum at
IP/LMD. Runtime already identifies the input branch, PndLmdTrackQ and output
TrackPairInfo; no explicit Gold point or required identifier is missing. The
additional payload explanation is useful to understanding the boundary, but is
not an extra enumerated Gold obligation. The judge also mentions awkward prose;
that portion has a directly reconstructible deterministic origin.

Runtime initial text says `std::vector<Lmd::Data::TrackPairInfo> records`.
The final phrase is `an internal support type<Lmd::Data::TrackPairInfo> records`.
The same malformed template-head abstraction appears in recovery g059:
`std::vector<RecoBinSmearingContributions>` becomes
`an internal support type<RecoBinSmearingContributions>`; that pair was equivalent.
This second case supports a generic textual mechanism, not a second quality FAIL.

| Stage | Frozen evidence and attribution |
| --- | --- |
| selected evidence | Both arms have the same ordered 12 selected evidence IDs and identical shared implementation text. getEntry maps RecoIP, RecoLMD, MCIP and MCLMD position/momentum; availability failure not established. |
| decomposition | Two explicit question obligations retained: definition and data boundary. No forced omission of payload explanation established. |
| initial generation | Runtime generates std::vector<Lmd::Data::TrackPairInfo> records, but not the optional reconstructed/MC payload elaboration. Legacy generates it. |
| answer postprocessing | Shared _strip_nonessential_external_identifiers replaces only std::vector, leaving <Lmd::Data::TrackPairInfo> attached to an internal support type. Pure frozen-function execution reproduces all final claim texts exactly. |
| verification | No rejection or claim removal; review clean. Replacement occurs before verification, not in verifier. |
| revision | Neither arm revises. |
| renderer | Joins already verified claim text and citations. Does not cause the transformation or drop optional text. |

Bypassing just the sanitizer preserves the initial grammatical container type expression in memory. This local string comparison does not predict judge preference and does not authorize exposing all third-party identifiers.

## g001: exact reconstruction and the omitted concept

Question: How do I install the locked PandaRoot development snapshot?
Gold: "Use the locked 2023-dev installation documentation and state that repository
behavior is commit-specific." There are no required identifiers and no literal
SHA requirement. Required documentation group permits the locked installation
page or developer installation title. Original index 3: A=runtime, B=legacy;
both supported, preferred B, critical_regression=false.

Frozen judge reason:

> Model B explicitly specifies the commit hash for the snapshot behavior, directly addressing the reference requirement that repository behavior is commit-specific.

### legacy_question_core — exact final public answer

```text
In PandaRoot at commit 18c09e91100db27867ded30e708b4dae95bd8357, Readme.md instructs developers to follow docs/Installation/Install_Developers.md (referenced in the documentation as Installation of PandaRoot for Developers), but the supplied evidence does not contain the complete developer-specific installation instructions from that file. [evidence.3c80d1da5887ef3ee98fd191, evidence.3b4af011e964b0498dab48ec, evidence.a5c121832f17c058e2344921]
The repository's documented installation base in docs/Installation/Install_PandaRoot.rst specifies setting SIMPATH and FAIRROOTPATH environment variables, creating a build folder, configuring with cmake -DCMAKE_INSTALL_PREFIX=../install ../source, and running make install -j4. [evidence.77425787ad04c01992cc8842, evidence.afe1338f948eb37357a506ad]
```

### runtime_e1_v2 — exact final public answer

```text
In PandaRoot, developers are directed to docs/Installation/Install_Developers.md (titled Installation of PandaRoot for Developers in docs/Installation/Install_Developers.rst), although the specific developer workflow steps beyond the document title are not detailed in the supplied evidence. [evidence.3c80d1da5887ef3ee98fd191, evidence.a5c121832f17c058e2344921, evidence.3b4af011e964b0498dab48ec]
According to docs/Installation/Install_PandaRoot.rst, the installation setup requires configuring the environment variables SIMPATH and FAIRROOTPATH to point to the external packages and FairRoot installation directories. [evidence.77425787ad04c01992cc8842, evidence.afe1338f948eb37357a506ad]
The documented build and installation commands in docs/Installation/Install_PandaRoot.rst involve creating and entering a build directory, configuring the project with cmake -DCMAKE_INSTALL_PREFIX=../install ../source, and compiling with make install -j4. [evidence.afe1338f948eb37357a506ad]
```

### Interpretation and stage trace

Classification **A — explicit Gold-required obligation**.
The runtime answer does **not** state commit-specific behavior in other words:
it says "In PandaRoot" and gives paths and build commands, with no version/commit
qualifier in public claim text. Legacy says "In PandaRoot at commit ...".
The SHA itself is optional; its scope-setting function answers the explicit Gold
clause. Calling the entire distinction minor hash specificity would conceal this
omission. Structured resolved_versions and evidence source_version_id retain the
identity, but metadata presence is not equivalent to stating it to the user.

Both arms acknowledge that the complete developer-specific instructions are not
in supplied evidence. Both use the locked installation Sphinx context and local
installation source. Do not convert that shared limitation into a runtime-only
failure or demand instructions absent from evidence.

The historical flags remain support=true, coverage_complete=true and
critical_regression=false. Those flags do not assert that every Gold clause is
expressed: support assesses facts asserted; E2 coverage assesses question-derived
points. The offline review finds one omitted explicit scope clause, without
replacing the frozen judge or modifying G2-G7/G10/G11. No automatic prompt repair,
new hash requirement or broad source-version rule follows from one observation.

| Stage | Frozen evidence and attribution |
| --- | --- |
| selected evidence | Both arms admit locked Sphinx installation context and PandaRoot installation code with source_version_id=pandaroot@18c09e91100db27867ded30e708b4dae95bd8357. Selected ordering differs but relevant version identity exists in both. |
| metadata and prompt path | Runtime selected Sphinx source identity and locators retain 2023-08-25-dev, snapshot_date and source_version_id. _answer passes source metadata and retrieval_plan.resolved_versions. Exact request bytes are not stored; input path is reconstructed from frozen code plus admissions/diagnostics. |
| evidence text | Selected text points to locked documentation but does not explicitly say repository behavior is commit-specific. That scope is available as version metadata; no need for a new retrieval to know which commit is in use. |
| decomposition | Single workflow point retains locked development snapshot wording. No direct evidence that decomposition deleted the qualifier. |
| initial generation | Runtime does not state commit/version scope; legacy initial claim says In PandaRoot at commit followed by the SHA. Runtime lacks the whole user-visible qualifier, not merely the literal SHA. |
| verification and revision | Initial runtime claims remain unchanged, review says covered, no revision. Semantic answer-point coverage is not proof of all approved Gold obligations. |
| renderer | All runtime public claims rendered unchanged. resolved_versions is retained in structured metadata but does not itself state the Gold-requested concept in the public answer. |

A generic in-scope version qualifier need not print a SHA to express commit-specific behavior, but adding such text now would be unauthorized output repair. No new Gold requirement to print hashes is proposed.

## Required per-case failure distinctions

| Runtime question | g029 | g001 |
| --- | --- | --- |
| Missed explicit Gold point/clause (offline reading) | no | yes: version scope |
| Missed required identifier | no | no: none required |
| Incorrect status | no | no |
| Unsupported | no | no |
| Citation-integrity failure | no | no |
| Coverage incomplete in frozen audit | no | no |
| Critical regression in frozen judgment | no | no |
| Preferred information available in runtime evidence path | yes | yes, metadata |
| Preferred detail generated then removed by verifier/revision | no | no |
| Lost by final renderer | no | no |

For g029, optional payload elaboration was never generated; a separate type phrase
was changed by answer-stage sanitization. For g001, version scope was never
generated. Neither case revised. Decomposition retains the requested obligations
in question terms; a systematic decomposition-induced narrowing is not isolated.

## Generic product assessment and g002 comparison

No single generic mechanism spans g001/g029/g002. The accepted P6 review found
Spack/CVMFS optional details in two legacy outputs and absent in two runtime
outputs. That repeated observation is not dismissed as proven random noise.
However g002 involved revision and optional installation context; g001 did not
revise and omits an explicit scope clause; g029 combines optional payload detail
with deterministic text rewriting. These are not independent activation samples
and are not pooled into an expanded denominator.

A narrower generic product defect **is** established across g029/g059:
partial third-party template-head replacement produces malformed public phrases.
This satisfies the five causal requirements: readable boundary/type explanations
have user utility; original type information was available and generated; the
named deterministic function performs the loss; two compatible frozen outputs
plus exact local reproduction identify the mechanism; and a syntax-aware generic
repair can avoid any exposed name or question trigger. The impact is bounded
presentation quality, not an unsupported or critical-answer claim. It does not
prove that correcting the phrase would change either frozen preference.

Owner: `src/panda_agent/qa.py::_strip_nonessential_external_identifiers`
(lines 636-659), called by `_answer` (around 1492) and `_revise`.
Taxonomy: **A1**, deterministic answer postprocessing, not retrieval, D1, V1 or
final rendering. `render_verified_answer` (around 980) merely joins claim text
and citations. The sanitizer is shared by legacy/runtime and is AST-identical
to the pre-A3 implementation at `ffedb2117f578515ea9d74eca92105956b8a3dcb`.
Thus this is a pre-existing shared defect manifested by runtime-generated syntax,
not proof that E1/E2 introduced it. The g001 A1 scope omission remains isolated;
no second product repair or mandatory-SHA rule is justified now.

## Full fourteen-pair frozen quality surface

Lengths are characters including citation text; citations are claim-to-evidence
edges (unique counts also stored in JSON). Counts are descriptive, not quality
scores. L/R means legacy/runtime. No new judgments were made.

| Case | Intent | Gold points | Runtime points | Claims L/R | Characters L/R | Citation edges L/R | Revisions L/R | Frozen quality | Reason category |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| g059 | algorithm_implementation | 3 | 1 | 3/3 | 1502/1077 | 5/4 | 1/0 | equivalent | equivalent_substantive_content |
| g047 | algorithm_theory | 1 | 1 | 3/2 | 1331/1033 | 7/7 | 0/0 | equivalent | equivalent_substantive_content |
| g028 | api | 1 | 1 | 2/2 | 564/601 | 6/8 | 0/0 | equivalent | equivalent_substantive_content |
| g001 | installation | 1 | 1 | 2/3 | 796/982 | 5/6 | 0/0 | worse | legacy_required_obligation_advantage |
| g105 | module_structure | 3 | 1 | 3/3 | 1195/1204 | 6/9 | 0/0 | equivalent | equivalent_substantive_content |
| g113 | troubleshooting | 3 | 1 | 6/3 | 3400/1547 | 11/5 | 1/1 | better | runtime_relevance_and_completeness_advantage |
| g014 | usage | 5 | 1 | 2/3 | 870/1030 | 4/5 | 0/0 | equivalent | equivalent_substantive_content |
| g060 | algorithm_implementation | 3 | 1 | 4/3 | 1623/1215 | 7/4 | 1/0 | equivalent | equivalent_substantive_content |
| g050 | algorithm_theory | 2 | 1 | 3/3 | 1471/1498 | 6/5 | 1/1 | equivalent | equivalent_substantive_content |
| g029 | api | 2 | 2 | 3/2 | 873/603 | 7/6 | 0/0 | worse | legacy_material_optional_elaboration_and_presentation |
| g057 | algorithm_theory | 1 | 1 | 1/1 | 353/353 | 1/1 | 0/0 | equivalent | equivalent_substantive_content |
| g041 | api | 1 | 1 | 1/1 | 349/349 | 1/1 | 0/0 | equivalent | equivalent_substantive_content |
| g007 | installation | 1 | 1 | 0/0 | 65/65 | 0/0 | 0/0 | equivalent | equivalent_substantive_content |
| g108 | module_structure | 1 | 1 | 0/0 | 196/196 | 0/0 | 0/0 | equivalent | equivalent_substantive_content |

Runtime answers are shorter in 5, longer in 5, identical-length in 4 cases.
g001 is longer despite omitting scope; g113 is shorter and preferred. These
observations reject length-as-quality and do not establish systematic optional
specificity loss. Eleven reasons describe substantive equivalence (including
four refusal controls), one prefers runtime relevance/completeness, one prefers
legacy required scope, and one prefers legacy boundary elaboration/presentation.
Full reasons and exact judgments are retained in JSON. g113 reason criticizes
legacy irrelevant concepts while its support flag is true; retain both rather
than silently reconcile them. Support and relevance/completeness differ.

Offline required-obligation omission identified in the reviewed public wording:
one (g001). No additional omission is established by this review; this is not a
new full semantic benchmark grade. Historical unsupported runtime outputs and
critical regressions are zero, with two noncritical legacy preferences.

## G11 design history, purpose and fragility

Original A3 Q6 allowed <=2 worse among 28. R1 P6 required zero worse in a bounded
five-case repair sentinel, not final activation. The accepted prior P6 review
proposed 14 cases and <=1 worse; R3 preregistered <=1/14 and >=13 non-worse with
zero critical regressions. Source lines and identities are in JSON.
`2/28 = 1/14` is arithmetic-rate equivalence only; statistical equivalence was
not established, nor was a population risk tolerance justified by that arithmetic.

Observed worse is 2/14 (14.29%); boundary 1/14 (7.14%). Holding everything else
fixed, one worse-to-equivalent label crosses the original PASS boundary; one
additional worse from 1/14 crosses to FAIL. This is a hypothetical sensitivity
calculation only, not a rescore. All discrete count thresholds have boundary
sensitivity; increasing N reduces percentage leverage but does not eliminate it.
There was one frozen model judgment per pair, so plausible sensitivity to rubric
and model variation is unmeasured: no empirical judge instability or power claim
is made and no confidence interval is used to imply a post-hoc PASS.

G11 should capture meaningful noncritical user-visible loss beyond status,
support, integrity, citation and coverage. The original prompt already says
"meaningful user-facing quality advantage" and forbids rewarding mere length or
citation count. The design problem is not an absent instruction: its single
preference field does not expose obligation coverage, severity rationale or the
material/minor distinction. g001 is a real scope omission; g029 contains useful
elaboration and malformed phrasing. Neither should automatically be dismissed as
cosmetic. Conversely an optional extra detail must not automatically become an
implementation requirement. A future rubric must record this distinction with
exact spans and consequences. Current binary support/coverage flags alone are
insufficient substitutes for an explicit Gold-obligation audit.

## Prospective options — not implemented

- **Option A:** Transparent strict engineering gate, valid historical rejection; not preferred for future activation because scalar preference does not expose obligation completeness versus material and minor differences.
- **Option B:** Larger cohort reduces one-case percentage weight but every count threshold still has a one-label boundary. Does not fix rubric validity. No evidence supports inheriting 7.14% as a risk margin.
- **Option C:** Preferred with explicit obligation audit. Require exact evidence/output spans, concrete consequence and materiality justification. Mere formatting/specificity advantages remain diagnostic; substantive scope omissions cannot be relabelled cosmetic.
- **Option D:** Useful only with explicit Gold obligations plus material user-utility safeguards; present support/coverage flags alone miss g001 scope omission and cannot be the only hard gates.
- **Option E:** Valid default unless a prospective design or generic repair is separately approved. Candidate remains rejected today; no repeated batches until PASS.

## Smallest proposed repair contract

- **owner:** src/panda_agent/qa.py::_strip_nonessential_external_identifiers, shared answer/revision postprocessing (A1)
- **generic_contract:** When abstracting an unrequested third-party type, transform the complete type expression into grammatical prose without leaving template delimiters or exposing an incomplete type fragment; preserve surrounding supported meaning, claim IDs and citations. Preserve explicitly requested identifiers. No source, question or concrete type allowlist.
- **unchanged:** decomposition, retrieval, source selection, citation admission, normalizer, Gold, prompts, schemas, coverage, verification policy, public DTO, default selector
- **T0:** Synthetic unseen third-party scalar/nested template expressions, punctuation and requested-name controls; preserve domain payload names/meaning and unaffected claims; exercise both answer and revision call sites.
- **frozen_impact_scan:** Scan compatible frozen initial/revision claims in both modes for transformations; report exact changes and collateral differences, without rewriting artifacts or claiming new quality labels.
- **smallest_prospective_revalidation:** After T0 and impact review, a separately approved 4-6 fresh paired development cases covering type-bearing API/boundary explanations, another intent, requested-name preservation and no-type controls; no activation claim from this repair check. Avoid an automatic second batch by incorporating these strata into one approved redesigned 28-case assessment if that combined scope is authorized.

## Future preregistration design proposal

- **status:** PROPOSAL_ONLY_NOT_IMPLEMENTED
- **product_candidate:** fd0aed4c7e491a569bf39271825cc0950630863d remains current; any authorized sanitizer repair creates a new candidate, which must be frozen before evaluation
- **new_product_code_required:** Yes only for the separately justified sanitizer repair; gate redesign itself requires no product code
- **dataset:** Fresh human-approved English development cohort; all R3/R3-R1/g002 evidence is exposed diagnostic material only. No protected/novel_validation access. Approve Gold independently of candidate outputs.
- **proposed_cohort_size:** 28
- **size_rationale:** Four unique questions in each of the seven observed intent strata is a bounded coverage target, not a powered statistical non-inferiority claim or reuse of 2/28. Preapprove answered/refusal/version controls; if suitable approved cases are unavailable, stop design rather than fill with trivial paraphrases.
- **judge_structure:** Two independently obtained blinded judgments for every pair with preregistered opposite A/B orders; no model identity claims of independence, no post-outcome rejudge. Each checks explicit Gold obligations, support, severity and exact cited spans. Judge disagreement on a gating fact is unresolved authority, not majority-by-retries.
- **hard_gates:** Zero established runtime explicit-obligation omissions, wrong status/version, unsupported claims, invalid citations, new critical verifier categories, invalid decomposition/coverage, critical regressions, or boundary violations; retain one-decomposition/one-revision/no post-verify retrieval and preregistered cost controls. Gold obligations and semantic point coverage are separate.
- **noncritical_quality_rule:** Zero confirmed material noncritical runtime regressions. Material means a supported difference that changes ability to perform the requested task, understand its boundary, or avoid a plausible error, with exact spans and concrete consequence. Two consistent judgments establish the comparative finding; disputed materiality prevents PASS. Minor style/optional specificity preferences and raw better/equivalent/worse remain diagnostic, with no offset of a defect by wins.
- **PASS:** All planned authority complete, every hard gate passes, no confirmed material regression and no unresolved gating disagreement. Engineering acceptance for declared cohort only.
- **FAIL:** Any independently established hard failure or confirmed material noncritical regression; missing other evidence cannot erase it.
- **INCONCLUSIVE:** Missing authority or unresolved gating disagreement without established FAIL. No automatic additional calls, case replacement or cohort expansion.
- **loop_stop:** One separately authorized preregistered assessment after design approval and any repair. No expanding N, changing rubric, rejudging, or new cohort merely because it fails. If design is not approved, retain legacy.

This is a bounded engineering acceptance design, not a claimed statistically
powered non-inferiority test. If population-rate certification is wanted, define
a defensible risk margin and sample-size calculation separately before any run.
A future experiment is decision-relevant only after the generic repair/design
is separately approved; another arbitrary fourteen questions is not recommended.
The 28-case proposal itself is not authorization or a frozen new gate.

## Independent AGY review and integration

Abstract-only job `staffer-mtvj1a3w-737e2027` completed SUCCESS, staffer route
`gemini-3.8-flash-high`, exit 0, one turn, 19.3848526 seconds. Effort was not
separately exposed. Reported input/output/thinking/cache tokens:
11571/4431/2105/8159, separate from scientific usage, not additive billing fields.
No repository content, cases or protected material was sent; only abstract counts
and design constraints. No worker edit was observed.

Accepted: distinguish mechanism evidence from historical rejection, operationalize
materiality, and state denominator/uncertainty limits. Rejected as unsupported:
the review's numerical power assertions, claim that larger N eliminates label
cliffs, and ad-hoc sequential 20+40 thresholds. No statistical inference is drawn
from its unverified confidence intervals. Its abstract opinion is not scientific
authority and does not override the exact g001 scope omission or g029 transform.

## Offline verification, costs and lifecycle

Checks: 14 identities exactly once; original eleven and recovery three selected
by committed provenance; 1/11/2 reproduced; g001 index3/g029 index9 both A=runtime,
B=legacy; complete exact selected records preserved; frozen sanitizer reproduces
g029/g059 final texts; unchanged pre-A3 shared function; only four allowed paths
changed; historical raw/judged/result, product/config/prompt/schema/corpus/index
unchanged; default legacy; JSON/count consistency and git diff --check.
No full test suite, retrieval, QA, judge, benchmark or model replay occurred.
Analyzer/embedding/reranker/retrieval/decomposition/answer/review/revision/judge
scientific calls = 0; scientific/provider calls = 0; scientific tokens = 0.
Static local computation and the separately reported abstract AGY review are not
scientific evaluation usage. Review computation has no new scientific cost.

Limitations: no new causal experiment or repeat judge; no proof that sanitization
repair flips a preference; no common systemic cause for g001/g029/g002; no claim
of general quality from lengths or 14 exposed cases; future materiality rubric
needs independent approval and calibration. Historical support/coverage flags
and this offline Gold-clause reading are separately labelled.

```text
E2-A3-R3-R1 = COMPLETE / FAIL / G11
E2-A3-R3-R1 G11 FAILURE REVIEW = COMPLETE / PASS / PRODUCT_REPAIR_AND_GATE_REDESIGN_RECOMMENDED
E2 = IN_PROGRESS / RUNTIME_ACTIVATION_FAILED / GENERIC_SANITIZATION_REPAIR_AND_GATE_REDESIGN_PENDING
normal default = legacy_question_core
E3 = NOT_STARTED
NEXT_TASK_RECOMMENDATION = E2-A3-R4 — Generic Claim Sanitization Repair and Prospective Activation Gate Redesign
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

The one normal review commit contains only this report, companion JSON and the
two lifecycle documents. No scientific freeze chain, repair, gate modification,
rescore, waiver, activation, E3, T3/T5 or automatic next task is performed.

E2-A3-R3-R1 G11 FAILURE REVIEW COMPLETE
