# G5 V1 Disposition-Provenance False-Insufficiency Repair Design

## 1. Status, scope, and authority

**PASS / COMPLETE / IMPLEMENTATION_READY for a prompt clarification with neutral examples under the existing host contract.** This is review/design only. No product, prompt, schema, configuration, dependency, dataset, Gold, calibration, or test change is made; no product test or scientific call is executed.

Starting clean `main` HEAD and current product lineage: `cd0a65df7576a736e83fdfe3da5998b766173ffc`, `Isolate production ambiguity diagnostics from D1 semantics`. Previous product lineage is `047201166057edd9859292a1760bc2e9bbf173a2`. Normal mode remains `production_answer_obligations_v1`. The D1 implementation and its 124 deterministic checks remain authoritative within their recorded scope.

Read authority: [failure-family review](G5_INTEGRATED_FAILURE_FAMILY_REVIEW.md), [D1 design](G5_D1_DIAGNOSTIC_METADATA_ROBUSTNESS_REPAIR_DESIGN.md), [D1 implementation](G5_D1_DIAGNOSTIC_METADATA_ROBUSTNESS_REPAIR_IMPLEMENTATION.md), [G1 design](G1_RELATIONSHIP_AWARE_ANSWER_OBLIGATION_DESIGN.md), [G2 design](G2_COVERAGE_REVIEW_LOCAL_FAILURE_ROBUSTNESS_DESIGN.md), [original G5 report](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION.md) and [machine result](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION_RESULT.json), [separate n018 report](G5_N018_SEPARATELY_AUTHORIZED_RERUN.md) and [machine result](G5_N018_SEPARATELY_AUTHORIZED_RERUN_RESULT.json), current status/roadmap, relevant source and focused tests. Both original ignored raw stores remain available and were inspected offline for the four cases. No replacement record is created.

The original G5 remains **INCOMPLETE / PRODUCT ERROR**, not ready for G6. Later n018 is mixed-provenance diagnostic evidence, not a synthetic complete gate. This design does not implement the next task or establish provider compliance/recovered answers.

## 2. Observed family

n022 has a nonexact quote; n025, n028, and separate n018 have supporter/basis citation mismatch. All four have `PARTIAL` V1 receipts, incomplete coverage, no A1/V2, final `insufficient_evidence`, and independently supported claims retained in the response. Thus G2 finalization erasure is **NOT OBSERVED**. These errors are proximate causes of refusal; they are not proof that the validator is buggy or that generation/retrieval limitations disappear.

All three citation-mismatch checks have full **union** coverage and at least one existing claim citing every declared basis. However, citation eligibility alone does not prove that one claim answers the entire check. The case review below assesses that distinction explicitly.

## 3. Current prompt contract

`prompts.py:259-308` defines the production review. Its exact relevant wording is:

```text
A basis is {evidence_id, quote}: known visible evidence and a nonempty exact
contiguous quote, not a paraphrase.
...
ADMITTED_BACKING_AVAILABLE requires 1-2 admitted basis items. satisfied=true
requires supported relevant mapped claims citing every basis item and actually
answering the check.
```

The plural sentence does not distinguish each-supporter citation closure from collective citation coverage. It also does not clearly distinguish a check's required proof material from all relevant evidence the reviewer considered. The inherited claim-review prompt evaluates each claim against its own cited evidence and accepts a central assertion supported across those citations; point relevance does not, by itself, prove contribution to each check within that point.

Quote exactness is already explicit. The n022 source projection seen by V1 retains the backticks that its output removed, so a host/provider input-text mismatch is not established. The model's internal reason for removing formatting is unknown.

## 4. Current host validator contract

`qa.py::_validate_production_check` (`962-1011` at starting HEAD) validates whole checks without discarding malformed items. For each basis it requires known evidence, unique ID, nonblank quote <=400 characters, and exact contiguous membership in that evidence text. For every named supporter it requires a known, nonexcluded claim, validated parent mapping, and:

```python
basis_ids <= set(claim_lookup[cid].get("evidence_ids", []))
```

Thus the declared citation edge set is the Cartesian product of supporters and basis IDs, not the citation union. Admitted checks require 1-2 admitted basis IDs and nonempty supporters when satisfied. Uncertain/visible-only dispositions remain unsatisfied with no supporters and retain their existing admission requirements. Bounds, canonical ownership, whole-point ordinary failure, and relation-local G2 failure remain.

The host does not deterministically prove a quote's semantic necessity, a supporter's contribution to this particular check, or collective answer completeness. Those remain review judgments. All-to-all citation closure is stronger than the logically minimal proof graph, but is not sufficient by itself to prove semantic truth.

## 5. Historical G1/G2 authority

- C1 implementation `5e0a3a3` already requires every supporter to cite all required basis; `git show` confirms the same subset test and the error `supporter does not cite required basis`.
- G1 implementation `9979b63` retains that rule while introducing canonical required relations. G1 design sections 9/14 preserve required-basis citation and reject wrong quotes, extra/uncited basis, bad supporters and mappings. They do not explicitly compare Cartesian and union semantics for independent multi-source claims.
- G2 design sections 3/4/8 preserves the existing citation contract, independently validates each check's edges/basis, and forbids trimming malformed supporters or basis. G2 implementation `a0106bd` extracts the existing subset rule into `_validate_production_check`; current blame identifies that extraction. It is not evidence that G2 invented a new acceptance restriction.
- Existing C1/G1/G2 tests preserve exact quote, non-citing/unsupported/irrelevant/wrong-parent supporter rejection, valid sibling containment, target-local A1, and full-contract V2. Existing tests do not establish that every legitimate independent-source multi-claim proof is representable.

**Finding:** historical prose is ambiguous about the abstract minimum necessary edge model, but unambiguous about retaining existing strict checks and not trimming invalid declarations. All-to-all is a selected compatibility policy inherited from C1, not a theorem forced by the words "every edge". This design deliberately retains it for the narrow output-reliability repair. A future union/edge contract would be a real semantic acceptance change, even with identical schema shape. Historical documents are not rewritten to imply otherwise.

## 6. Four-case trace analysis

Raw authority: `data/evaluation/runs/g5-integrated-candidate-novel-dev-v1/records/{n022,n025,n028}.json` and corresponding `traces/*.json`; separate `data/evaluation/runs/g5-n018-separately-authorized-rerun-v1/records/n018.json` and `traces/n018.json`. Stage evidence is each record's `diagnostics.qa_stage_trace`, especially `V1_INPUT.normalized_draft`, `V1_OUTPUT.response`, validation and evidence registry. All IDs and quotes below are from those records. Evidence aliases are local editorial notation, not proposed runtime identifiers.

In the quote blocks, `A:`/`B:`/`C:` are editorial labels and are not quote bytes. Passing sibling quote bodies remain available in the unchanged raw records; the failed checks' complete quote bodies are reproduced below.

### n022: BAD_QUOTE, not a citation-union problem

Canonical `point.1.rel.1` asks what the first POCA worker leaves for the second step; `point.2.rel.1` asks how the fitted vertex feeds reprocessing. Both claims directly contribute to their own check.

| Evidence alias | Recorded evidence ID |
|---|---|
| A | `evidence.a152b9210e11fce51b717112` |
| B | `evidence.39f00bef06a208f69d334ceb` |
| C | `evidence.5212466c1e2a4793ad9b8f80` |
| D | `evidence.004cd90afeaa4d77e39a6883` |
| E | `evidence.e43bc446969283f4c9396481` |

`claim_1` describes JSON fitted vertex parameters and ROOT event_poca output with event coordinates; citations `[B,A,C]`, mapped to point 1. `claim_2` describes FIT_VERTEX_* / POCA_VERTEX_FILE, matching event ID and reprocessing; citations `[D,B,E]`, mapped to point 2.

The invalid named check declares basis `[A]`, supporter `[claim_1]`, satisfied/admitted. Individual and union citation closure both hold. Its exact recorded **invalid** quote is:

```text
For the two-pass workflow, ana_dpm.C writes two complementary products:

- `<prefix>_boost.root`, containing an `event_poca` tree with exactly one entry per input event;
- `<prefix>_vtx_fit.json`, containing fitted sample-level means and widths for diagnostics and legacy fixed-IP compatibility.
```

Length is 295. The input/source instead begins `For the two-pass workflow, ` followed by **backtick-delimited** `ana_dpm.C`; the two removed backticks suffice to make membership false. V1's actual projection contains the backticks. The second relation's `[D,B]` basis quotes are exact and `claim_2` cites both; its disposition survives. `claim_1` is a plausible complete witness to the output check, but the submitted quote remains invalid. Both verified claims render; revision count 0. Historical fallback/code-role omissions remain independent, not new runtime obligations from Gold.

Classification: **EXPECTED_STRICT_REJECTION + PROMPT_MODEL_RELIABILITY**, with a useful formatting-preservation example opportunity. No validator bug established; actual provider thought process unresolved.

### n025: one extra non-citing supporter on an ordinary check

Canonical point 1 is relation-free and asks how triplet combinatorics stay manageable while efficient for displaced vertices. The ordinary inventory has two necessary checks: combinatorial reduction, then displaced efficiency.

| Alias | Recorded evidence ID |
|---|---|
| A | `evidence.a663a0e2c5fc6797b863c488` |
| B | `evidence.290b6e9b34847abb5fcc3836` |
| C | `evidence.1b1c6c7f25d05af9ea662bd5` |
| D | `evidence.6222de90a430ece2922b0abd` |

`claim.1`: radial inner/mid/outer triplets, lever arm, no hard nominal-IP constraint, citations `[A,B]`. `claim.2`: CA neighbor connectivity and phi compatibility, citations `[A,B,D]`. `claim.3`: no beam-axis filtering plus hit growth, continuity/multiplicity and residual quality, citations `[A,B,C]`. All map to point 1 and remain verified/rendered.

The failed second ordinary check declares basis `[A,C]`, supporters `[claim.1,claim.3]`, satisfied/admitted. Its exact quotes are:

```text
A: This avoids a hard nominal-IP constraint and preserves efficiency for displaced vertices.
C: For candidates with comparable hit counts, the geometric fit quality is evaluated by computing the quadratic distance of the assigned hits to the candidate circle
```

The `A:`/`C:` labels above are editorial prefixes, not quote bytes. Both quote bodies are exact (89/162 characters). `claim.1` lacks C; `claim.3` cites both. Union closure holds. Both claims contribute to the efficiency explanation, but `claim.1` is a partial/redundant contribution; `claim.3` already states the full failed check's mechanism and is a plausible single witness. The first check uses exact B and supporters `[claim.1,claim.2]`, both citing B. Because the second check is malformed, the entire ordinary point is LOCAL_INVALID; no A1/V2. Historical eight-solution omission remains a generation/Gold-depth caveat, not a new required runtime point.

Classification: **PROMPT_UNDERSPECIFICATION + EXPECTED_STRICT_REJECTION**, and ambiguous proof-set selection; not a demonstrated validator bug. A provider could choose a valid smaller witness set before emission; the host must not rewrite this saved malformed check.

### n028: container claim plus full downstream witness

Point 1 is ordinary trigger production; `point.2.rel.1` is canonical OnlineFilterInfo exposure to downstream analysis.

| Alias | Recorded evidence ID |
|---|---|
| A | `evidence.5aec65f04ec751097c07fbd4` |
| B | `evidence.e50ba941687f3ad1f64ff9d6` |
| C | `evidence.5b2f98e5b1088ebe297830b6` |
| D | `evidence.4bf94185a76021c56caf12ef` |

`claim.1`: trigger task/config/tag mode, citations `[A,D]`, point 1. `claim.2`: counts/container/SetNTag, citations `[B,C]`, points 1/2. `claim.3`: written decisions, downstream PndAnaWithTrigger sequence, query methods, citations `[A,B,C]`, point 2.

The failed named check declares basis `[A,B]`, supporters `[claim.2,claim.3]`, satisfied/admitted. Exact quote bodies:

```text
A: // Example analysis in a task with accessing the OnlineEventFilterInfo
B: bool Tagged() const { return fNTagTotal > 0; }
```

Both exact (70/46 characters). `claim.2` lacks A; `claim.3` cites both. Union closure holds. The container claim contributes partial context; `claim.3` plausibly answers the full exposure check alone. That does not prove the short comment/header quotes establish every omitted implementation detail. Point 1's task/SetNTag ordinary checks remain valid. Three verified claims render, no A1/V2. Independent producer/consumer implementation loss and registration/tuple depth remain; a provenance prompt repair cannot guarantee recovery of those details.

Classification: **PROMPT_UNDERSPECIFICATION + EXPECTED_STRICT_REJECTION**, with a separate retrieval/generation limitation. Same-parent mapping is not itself sufficient per-check semantic contribution.

### Separate n018: shared adequate source exists; one full witness is not established

Point 1 is ordinary individual MC-truth inspection; `point.2.rel.1` asks whole reconstructed/generated tree matching. This is the later separate run, not the original D1 error record.

| Alias | Recorded evidence ID |
|---|---|
| A | `evidence.0e87ee452eca4d3f8a836620` |
| B | `evidence.aef1029b460a3b22035622ff` |
| C | `evidence.d52108d61ba7fd98e185dd49` |
| D | `evidence.00c987d640013db2875fefe3` |
| E | `evidence.66beb6fd9691050770b7879f` |

`claim_inspect_mc_truth_counterpart`: GetMcTruth returns counterpart or null, citations `[D,E,C]`, point 1. `claim_full_tree_mctruthmatch`: PndAnalysis::McTruthMatch on composite candidate for topology/particle hypotheses, citations `[B,A,C]`, point 2. `claim_tree_match_preparation`: configure intermediate particle types with SetType/combination, citations `[B,C]`, point 2.

The failed named check declares basis `[A,B]`, supporters `[claim_full_tree_mctruthmatch,claim_tree_match_preparation]`, satisfied/admitted. Exact quote bodies:

```text
A: If you don't know immediately how to perform such kind of match, don't worry! Fortunately there is a method available within **PndAnalysis** which does this job for you, called ``PndAnalysis::McTruthMatch``. This method needs a particle as input and does the tree match for arbitrary decay trees.
B: Since the matching routine also checks whether intermediate resonances
have the correct type (at least in default setting), we have to tell our composite candidates, of which type they are supposed to be, either by using the methods
RhoCandidate::SetType
or for a full list
RhoCandList::SetType
, or even more comfortable, just together with the combinatorics.
```

Both exact (296/360 characters). The preparation claim lacks A; the full-tree claim cites both; union closure holds. Both semantically contribute. The full-tree claim is citation-eligible as a single witness but does not state the separate preparation assertion; a semantically complete single witness is therefore **not established**, rather than inferred from IDs.

Crucially, B's saved text already contains both the McTruthMatch method and the SetType preparation; C also contains both. Both point-2 claims already cite B/C. A fresh provider disposition can potentially choose adequate exact quote(s) from a common source under the current shape, provided the bounded excerpts truly support the full check. It must not mechanically choose the citation intersection or remove necessary preparation to pass validation. The current `[A,B]` raw declaration remains invalid. Three supported claims render, no A1/V2. Missing EvtGen/PDG preparation under historical review remains independent; no new Gold-derived runtime obligation is introduced.

Classification: **PROMPT_UNDERSPECIFICATION + EXPECTED_STRICT_REJECTION / DISPOSITION_DATA_MODEL_AMBIGUITY**. Current source offers a common-basis opportunity; success is not guaranteed. No fundamentally required new edge schema is demonstrated by this trace.

## 7. Selected semantic model

**Precise invariant:** A V1 check is provenance-valid only when every declared basis item has known evidence, an exact bounded quote and valid admission, and every named supporter is known, supported, relevant, correctly parent-mapped, directly contributes to that check and individually cites every declared basis ID; an admitted satisfied check additionally requires nonempty supporters that collectively answer its full canonical relation or necessary ordinary check.

Decision label: `ALL_TO_ALL_CHECK_PROOF_BASIS`. This label records the design decision; it is not a new runtime mode or schema.

Let B be declared basis IDs, S named supporters, and C(s) a supplied claim's citations: retain `for every s in S: B subset C(s)`. Semantic coverage is collective; **not every supporter must individually answer the whole check**, and not every quote must individually entail every claim. Per-claim entailment remains against that claim's cited evidence set. The complete check still needs evidence-grounded semantics, not just set arithmetic.

`basis` means the small sufficient proof material actually used to judge this check, **not all evidence seen, all claim citations, or optional corroboration**. Each selected item must substantively ground the support judgment; all declared items become required citation edges once emitted. Selecting a minimal adequate proof before emission is permitted; silently shrinking an already malformed declaration is forbidden. Logical minimality/necessity is a semantic reviewer responsibility, not a new deterministic host predicate.

All-to-all is intentionally stronger than the minimum logical proof graph. It can overconstrain a legitimate distributed proof with disjoint citations. Retaining that limitation is the conservative scope decision for this repair, not a claim that union semantics are inherently always unsafe or that this design solves all false insufficiency. The three observed mismatches have feasible existing-contract candidate expressions, so broader acceptance changes are not required to address this measured output family first.

## 8. Neutral counterexamples and representational limits

| Pattern | Selected contract / outcome | Safety and expressiveness reasoning |
|---|---|---|
| S1: full claim c1 cites A; basis A | Valid if exact/admitted/semantically sound | Straightforward single witness |
| S2: c1 answers X citing only A; c2 answers Y citing only B; full check needs X+Y | Union-only `[A,B]` / `[c1,c2]` remains invalid | For ordinary points, two genuinely necessary checks X and Y can separately use A/c1 and B/c2 while both must pass; never omit Y. A canonical composite relation cannot acquire new subcheck IDs or two rows. With no complete existing witness/common adequate cited basis, its positive disposition is not representable under retained all-to-all. This is a real HOST_CONTRACT_OVERCONSTRAINT limit. |
| S3: c1 answers using A; c2 carries B but contributes nothing to this check | Must not count complete | Parent relevance is insufficient; direct per-check contribution and full-check semantics are required. Citation union cannot prove that. Even all-to-all could be gamed by gratuitous citations, so semantic review remains necessary. |
| S4: named supporter cites no basis | Invalid | Known/parent-mapped status cannot replace a declared citation edge |
| S5: quote paraphrases A | BAD_QUOTE / invalid | No fuzzy, whitespace, Markdown, Unicode or case repair |
| S6: valid full c1 plus extra unsupported/non-citing c2 | Whole owning check invalid; G2 local owner affected | Host may not trim c2. Provider may choose only c1 before emission if it really answers the full check. |
| S7: c1 answers with A; optional B declared as basis but uncited by c1 | Invalid as submitted | B becomes required proof material by declaration. Prefer `[A]` at original emission only if A genuinely suffices; do not drop indispensable B. |

Positive multi-claim expression remains legal: canonical "How does Cedar order work and feed Maple?", c1 states order, c2 states output, **both already cite A**, and A genuinely supports both contributions. `[A]` / `[c1,c2]` is valid; a single-witness cardinality rule would unnecessarily reject it. Two-basis/multi-supporter checks remain legal when each supplied supporter already cites both and the entire target is semantically established.

For the unrepresentable canonical S2 variant, do not manufacture citation edges, collapse atomic claims, weaken the relation, invent hidden requirements, or call evidence absent. A provider may emit the existing honest admitted-backed unsatisfied disposition with adequate basis and no malformed supporters, explaining that no complete provenance-valid witness is available under this contract. This is not evidence insufficiency and not automatic positive recovery. It may expose the existing bounded A1 opportunity; neither a new call nor successful repair is guaranteed. A broader distributed-edge acceptance policy remains a separately scoped future question. The selected prompt repair is implementation-ready within its expressly limited contract.

## 9. Candidate decision matrix

| Candidate | Safety / false-positive risk | Expressiveness / false-insufficiency risk | Provider reliability / schema complexity | G1 / G2 compatibility | Implementation / versions | BAD_QUOTE / INVALID_SUPPORTER | Decision |
|---|---|---|---|---|---|---|---|
| A: prose clarification only | No host acceptance expansion; semantics still model-judged | Retains disjoint-source ceiling; reduces ambiguity only | Small prompt; no new shape; empirical benefit unknown | Preserves canonical path and no trimming | Review prompt + prompt-set patch + tests; no validator/schema bump | Restates copy and individual citation rules; may be ignored | Less concrete than B |
| B: clarification + neutral positive/negative examples | Same strict host closure; semantic carriers explicitly excluded | Supports existing common-basis/multi-claim proofs and smaller complete witnesses; known S2 residual | Modest prompt addition; current simple schema; no compliance guarantee | Preserves G1/G2 authority, locality and revision | Review prompt, patch version/fingerprint, focused tests; no host/schema change | Distinguishes exact formatting, pre-emission proof choice, bad declarations | **Select** |
| C: union citation relaxation | New accepted graphs; semantic alignment not proved by union; higher acceptance risk | Expresses S2 without duplication; may reduce refusals | No shape change, but changes local acceptance; output ambiguity still needs prose | Requires explicit G1/G2 citation semantics revision; no-trimming can remain | Validator + prompt + semantic-contract tests/version decision; material behavior change | Does not fix quotes; accepts some current citation failures | Not needed for this bounded family; do not adopt blindly |
| D: explicit supporter/basis edges | Strict declared-edge validation possible; semantic per-edge truth still model-judged | Expresses S2 and necessary proof ownership | Larger lists/joins, limits, mapping conflicts and failure surface | Requires a new selected edge authority and locality proof | New provider/local schema version, prompt and validator/tests | Still needs exact quotes; makes citation associations explicit | Disproportionate here; not a deterministic semantic guarantee |
| E: mandatory single full witness | Strong citation closure; full-target semantics still necessary | Rejects legitimate multi-claim common-basis answers; cannot express general S2 | Simpler emission, but artificial witness pressure conflicts with atomic claims | Cardinality restriction changes current G1/G2 capacity | Prompt and possibly host restriction/tests; material restriction if enforced | May avoid extra supporter error, not quote copying | Reject mandatory rule; use one witness only when genuinely complete |
| F: host-derived provenance/reduction/quote extraction | Risks inventing proof or promoting malformed satisfaction; no exact semantic extraction authority exists | Can appear to recover cases by hiding bad edges/basis | New host selection policy; not merely simpler provider schema | Violates G2 no-trim/no-substitute unless separately proven/redesigned | New host authority and tests/version analysis, beyond scope | Would conceal rather than prevent malformed proof | Reject |
| G: second verifier/retry/correction call | A second untrusted output still needs strict validation | Might improve output quality; efficacy/cost unknown | More provider calls/failure surface | Requires explicit call-budget and retry authority; cannot self-authorize | New orchestration/cost contract | Can attempt both repairs, cannot guarantee them | Reject; no demonstrated necessity |

## 10. Selected prompt change, implementation-ready prose

Future implementation changes only the production coverage review's proof instructions/examples plus ordinary version/test delivery. It prevents malformed output at original emission; it does not repair output after reception. Proposed prose for that prompt, with no domain/case-specific examples:

```text
For each check, basis is the small adequate proof used for that check, not a
catalogue of evidence you considered or optional corroboration. Each selected
basis item must ground the judgment. Use only existing supplied claims and their
existing evidence_ids; never add or rewrite a claim's citations.

Every named supporting_claim_id must INDIVIDUALLY cite EVERY basis evidence_id.
Collective citation union is insufficient. Every supporter must directly
contribute to this check, be supported/relevant, and map to its canonical parent.
The selected supporters collectively must answer the full check to set
satisfied=true. A shared point mapping or a mention of the same entities is
not enough. A single supporter is allowed only if it answers the full check;
multiple supporters are allowed when all satisfy the individual citation rule.

Choose a smaller complete witness set or an adequate shared basis BEFORE
emitting the disposition, only when its semantics really establish the whole
check. Never omit a necessary contribution or evidence merely to satisfy the
citation test. If there is no provenance-valid complete witness, do not emit
a malformed satisfied disposition: retain the existing truthful unsatisfied
admission disposition and preserve independently valid claim support/mappings.
Do not confuse missing proof closure with absent or ambiguous evidence.

Copy each quote directly from the selected untrusted_evidence text. Preserve
backticks, markup, case, punctuation, Unicode and internal whitespace/newlines.
JSON escaping must decode to the exact original substring. Claims may
paraphrase; basis quotes may not. Use a short semantically adequate contiguous
excerpt within the existing bound, not silently shortened or cleaned text.
```

Add three short neutral structured examples: (1) two contributing claims already citing A, one exact A basis and valid multi-supporter check; (2) split A/B citations with `[A,B]` invalid despite union coverage, plus an ordinary two-check expression requiring both subparts; (3) evidence `Cedar uses ` followed by backtick-delimited `Maple`, where deleting backticks from the quote is invalid. Include that an extra malformed supporter invalidates the submitted check. Use existing check fields/IDs, no extra response field. Fully formed example rows must satisfy the current closed schema and bounds.

No unconditional instruction to use only one supporter, no citation-intersection shortcut, no automatic output rewriting, and no instruction to mark the four observed cases answered.

## 11. Rejected alternatives and contract impact

Union coverage is a potentially legitimate distributed-proof contract, but is neither established by current historical prose nor a sufficient semantic alignment guarantee. It would materially relax host acceptance and deserves its own adversarial contract design if required by an authorized broader scope. Explicit edges could express S2 more cleanly but add schema/ownership surfaces without being needed for these common-basis/witness opportunities. A mandatory single witness is too restrictive.

No host supporter/basis trimming, inferred citations, deterministic basis replacement, quote repair or new verifier call is selected. These would promote provider-authored `satisfied=true` using host-invented proof or broaden execution. The selected change clarifies an inherited host policy; it does not claim that policy is the universal minimum safe provenance model. Future prompt behavior is material even though formal host acceptance is unchanged.

## 12. BAD_QUOTE treatment

Retain exact known-evidence substring, nonempty, <=400 and admission checks. n022 demonstrates formatting loss despite an explicit exact-copy instruction, so classify it as output reliability rather than unspecified host semantics. Short literal examples can highlight the distinction between faithful claim paraphrase and literal provenance copy; they cannot prove a real model will obey.

Do not normalize spaces, strip Markdown, change Unicode/case/quotes, fuzzy-match, select a replacement substring, omit quotes for host extraction, or retry automatically. A new quote representation (offsets/host-selected excerpts) would require its own input identity, semantic span-selection and version authority; the current evidence does not justify it. Raw BAD_QUOTE still invalidates its whole owning check under G2. No claim is made that an edited prompt repairs the historical raw quote.

## 13. INVALID_SUPPORTER treatment

Make all-to-all explicit for every named supporter, not just "some claims collectively cite enough". Explain proof-basis choice and per-check contribution. Pre-emission selection can use one genuinely complete existing witness or multiple existing claims with an adequate common cited basis. It must not mutate claim evidence_ids, hide necessary evidence or classify a citation carrier as semantic support. Every extra declared bad edge still invalidates the owning check; no union shortcut or host repair is introduced.

The mismatch classifications are therefore different: n025/n028/separate n018 primarily exhibit prompt underspecification under a strict inherited data model; n022 primarily exhibits failure to obey an already stated literal rule. Generic disjoint-citation S2 exposes real host overconstraint, intentionally retained and disclosed. Provider-schema shape is not the demonstrated blocker for the four traces; no validator bug is established. Residual extraction quality and some proof-witness sufficiency remain unresolved empirically.

## 14. G2, A1 and V2 interaction

All receipt/locality rules remain. Named malformed check -> LOCAL_INVALID canonical relation; malformed ordinary check -> LOCAL_INVALID whole ordinary point. Independently valid sibling support/mapping survives, but LOCAL_INVALID is never complete or self-authorizing. The four historical malformed rows remain blocked exactly as recorded.

Only a newly emitted, wholly valid admitted-backed unsatisfied check can enter the existing target-local A1 scope. Invalid metadata cannot create a target; prompt instructions cannot authorize repair of a raw malformed disposition. Other valid unsatisfied siblings may still share the one existing A1 call. No second V1, coverage retry, second A1, extra retrieval, new model stage or runtime mode is added. Better first-pass output can change whether the existing bounded A1 is legitimately reached; identical future call counts or recovery are not promised.

V2 rechecks the full immutable canonical point/relation inventory, including earlier invalid/missing siblings. Supported claims alone cannot make the answer complete. G1 single completeness path, canonical relation/parent identity, G2 valid-sibling containment, anti-resurrection and composer/unsupported-claim exclusion remain.

## 15. Future deterministic verification plan

No tests below ran in this design. Use existing C1/G1/G2 fake fixtures, without evaluation questions, Gold-derived expected facts or live providers.

1. **Prompt RED -> GREEN:** before changing the prompt, add one narrow static/fake-provider contract assertion requiring the explicit individual citation rule, proof-basis meaning, per-check semantic contribution and literal-formatting distinction. Its RED proves missing contract wording, not real-model noncompliance. After the prompt edit, GREEN proves the intended instruction/example was delivered through the existing production review seam.
2. **Host characterization:** the following positive and negative outcomes must remain identical before/after; compare the same raw fixtures/receipt codes, not a repaired response. This distinguishes output-guidance change from host-rule relaxation.
3. **Fake integration:** script a malformed first-pass output and confirm unchanged PARTIAL/owner blocking, then separately script a valid pre-emission witness/common-basis output and confirm ordinary G1/G2 handling. Do not model the latter as an automatic retry or proof that the real provider improves.

| Neutral fixture | Expected unchanged host / integration outcome |
|---|---|
| Exact quote, known supported mapped c1/A | Valid admitted satisfied check |
| Paraphrase/backticks removed/case or internal-space change | BAD_QUOTE; no substitution |
| Non-citing, wrong-parent, unsupported, irrelevant, unknown supporter | Owning check invalid; no acceptance from parent mapping |
| Two supporters, one genuinely shared basis | Valid if both cite it and collectively answer the check |
| Two supporters, two basis, each already citing both | Valid with exact quotes and semantic support; not a one-supporter restriction |
| Union-only disjoint citations; irrelevant citation carrier | No positive closure; carrier cannot establish semantics; static/synthetic oracle must separately flag per-check irrelevance |
| Complete witness plus extra malformed supporter | Owning check invalid; host never trims |
| Unnecessary declared uncited extra basis | Invalid as submitted; separate fresh `[A]` example valid only if A is adequate |
| Legitimate S2 ordinary X/Y versus composite named relation | Both ordinary checks required; no duplicated/invented canonical relation rows; named distributed-only proof not accepted |
| Required-relation disposition versus ordinary relationship check | Single active completeness path; canonical ID/owner and ordinary full-inventory requirements preserved |
| LOCAL_INVALID sibling plus valid admitted-unsatisfied sibling | Invalid owner incomplete and not a target; valid sibling independently eligible |
| A1 authorization and V2 | At most one existing revision; full original canonical inventory in V2; no truncated acceptance |

Semantic counterexamples require explicit fixture judgments: a deterministic validator cannot discover check-level irrelevance from prose merely because an ID graph is valid. A fake `satisfied=true` must not be described as proof of real semantic correctness. No new inference mechanism is introduced to make that test claim true.

Future focused ownership: prompt contract/delivery tests in existing `test_post_a5_c1_coverage_completeness.py`; representative hostile receipt tests in existing `test_g2_coverage_local_failure.py`; reuse existing G1 canonical/A1/V2 and QA/E2 support/mapping controls. Run only touched tests and directly affected neighbors, not a full suite. Stop at deterministic scope; no live verification is authorized by this plan.

## 16. Future file and version impact

| Item | Future implementation requirement |
|---|---|
| `src/panda_agent/prompts.py` | Production review prose/examples only; **PROMPT_CHANGE=true** |
| `PROMPT_SET_VERSION` | Proposed patch `3.12.0 -> 3.12.1`, because model-facing prose changes behavior; do not apply now |
| Separate coverage prompt version | None exists; add no new version layer |
| Shared prompt fingerprint | Must change through existing `evaluation_runner.prompt_fingerprint()` authority when prompt/version changes; do not calculate/freeze a new fingerprint in this design |
| Host validator / `qa.py` | **No change**; identical acceptance rules and G2 locality |
| Provider coverage schema / `coverage-satisfaction-v2` | **No change**; no edge fields or schema-version bump |
| Decomposition prompt/schema/version, runtime mode, A1 prompt | **No change** |
| Focused tests | Static delivery/neutral characterization/integration tests; update only directly affected version/fingerprint assertions |
| Known identity assertions | `test_post_a5_c1_coverage_completeness.py`, `test_post_a5_o1_observability.py`, `test_qa.py` contain current identity expectations; inspect/update affected assertions under future authorization, not historical artifacts |
| Documentation / lineage | Future implementation record/current state and normal Git delivery; future prompt behavior establishes a new product lineage |

No new manifest, hash layer, schema, feature flag, retry, call, dataset edit, historical result rewrite or dependency change is needed. An unexpected requirement to alter host acceptance is a scope contradiction to report, not permission to silently implement union semantics.

## 17. Empirical boundary and limits

This task establishes an exact implementable prompting contract and an explicit conservative expressiveness ceiling, not measured provider reliability. The four historical outputs remain invalid under current acceptance. Common-basis/full-witness opportunities are static observations, not repaired QA results or numerical causal recovery coverage. Retrieval/generation/Gold-depth limitations remain separate, and original n018 empirical recovery remains unestablished after D1.

A future live check would need separate authorization defining cases, lineage, mode, call budget and stop rules. No run is selected or authorized here. No full G5/n018 rerun, new scientific evidence, G6, novel_validation or holdout follows from design PASS.

## 18. Current task lifecycle and next recommendation

```text
G5_V1_PROVENANCE_REPAIR_DESIGN = COMPLETE / IMPLEMENTATION_READY
DESIGN_VERDICT = PASS
SELECTED_V1_PROVENANCE_CONTRACT = ALL_TO_ALL_CHECK_PROOF_BASIS
SELECTED_REPAIR = PROMPT_CLARIFICATION_WITH_NEUTRAL_EXAMPLES
HOST_ACCEPTANCE_RULE_CHANGE_PLANNED = false
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
NEW_RUNTIME_MODE = false
TEST_EXECUTIONS = 0
NEW_G5_RUNS = 0
N018_LIVE_RERUNS = 0
QA_SCIENTIFIC_RUNS = 0
RETRIEVAL_EVALUATION_RUNS = 0
SCIENTIFIC_GENERATION_CALLS = 0
SCIENTIFIC_EMBEDDING_CALLS = 0
SCIENTIFIC_CALLS = 0
SCIENTIFIC_TOKENS = 0
EXTERNAL_JUDGE_CALLS = 0
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
NEXT_TASK_RECOMMENDATION = G5 V1 DISPOSITION-PROVENANCE FALSE-INSUFFICIENCY REPAIR IMPLEMENTATION
NEXT_TASK_EXECUTION_AUTHORIZED = false
```

Both local raw stores were available; no new raw-unavailability blocker exists. Unresolved limits are actual provider compliance, exact semantic adequacy of prospective proof choices, and the intentionally retained distributed-only named-proof restriction. No implementation or empirical recovery is claimed. Only this design document and authoritative current-state sections are changed; historical G1/G2/G5 records remain intact.
