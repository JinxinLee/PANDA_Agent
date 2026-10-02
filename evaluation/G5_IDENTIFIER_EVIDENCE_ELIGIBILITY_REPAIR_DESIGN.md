# G5 Deterministic Identifier-Evidence Eligibility Repair Design

## 1. Status and authorized scope

**COMPLETE / PASS / NO_IMPLEMENTATION_READY at offline design scope.**

Exactly one primary outcome is selected: **A — STRICT_RULE_RETAINED / NO_SAFE_RELAXATION**. The deterministic contract remains **STRICT_EXACT_MATCH_RETAINED**. `IMPLEMENTATION_READY=false`; the two known false exclusions remain limitations. This is a completed negative design decision, not an incomplete implementation.

The current cited representation does not establish a small, safe owner/member equivalence predicate covering both motivating examples. In particular, a method returning an Owner object does not establish that the receiver is Owner. Strong human-readable class documentation in n007 does not supply that missing receiver ownership in n018. Suffix matching, citation-union composition and qualifier deletion are rejected.

This task authorizes design, static source/artifact review, documentation and its delivery commit only. No product, test, prompt, schema, configuration, dependency, dataset, Gold, calibration or raw-store edits; no test execution, provider call, health check, QA/evaluation, rerun/resume or lifecycle advancement occurred.

## 2. Authorities and entry identity

Entry is clean `main` at `696cd23354a0d6de606a7e974b174c7a96a198bd`, message `Review post-forward V1 semantic failure families`, parent `ffabe4fe06ce9360a4947331104161a0903f7138`. Product lineage remains `5b9588ec552deb91a59a8176d6ce0429c2133b1e`; prompt set is `3.12.1`, fingerprint `08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc`. No fingerprint was regenerated.

The [preceding review](G5_POST_FORWARD_V1_SEMANTIC_FAILURE_FAMILY_REVIEW.md) was read completely and remains the current causal authority. Existing [integrated review](G5_INTEGRATED_FAILURE_FAMILY_REVIEW.md) and [integrated execution report](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION.md) supply historical context; their prose and outcomes are not rewritten. Current status/roadmap and AGENTS.md govern boundaries.

Source inspection covers `qa.py` normalization, deterministic claim checks and V1 payload construction; `models.py` locator/knowledge/evidence fields; `ingestion.py` C++ symbol extraction, web sections and derived chunks; `retrieval.py` Evidence projection. The existing deterministic-integrity fixture in `tests/unit/test_qa.py` was read as text, not run. No product module or provider client was imported or instantiated.

The bounded raw set is exactly:

| Alias | Root under `data/evaluation/runs/` | Opened case |
|---|---|---|
| F | `g5-post-observability-repair-targeted-live-v2` | n018 |
| O | `g5-integrated-candidate-novel-dev-v1` | n007 |

The same records also provide existing exact-pass controls, avoiding an additional case search. Raw pointers are `records/<ID>.json::diagnostics.qa_stage_trace.events`, stage V1_INPUT, resolving `evidence_projection_ref` through `evidence_registry`; EA_ADMISSION and V2_INPUT confirm admission and subsequent errors. `diagnostics.selected_evidence` and `traces/<ID>.json::channel_candidates` establish available Evidence fields and upstream object types. Only these exposed records/traces were inspected. No corpus/source-document search, protected listing/search/open, Gold consultation or new retrieval occurred. Reading source URLs in saved metadata did not fetch them.

## 3. Confirmed failure mechanism

F/n018 A0 claim.1 states `RhoCandidate::GetMcTruth()` returning the MC-truth RhoCandidate. Its cited tutorial provides an instance call and the useful semantic fact; deterministic errors contain `unsupported identifier RhoCandidate::GetMcTruth`. V1 receives only claim.2 and claim.3. A1 later generates unqualified `GetMcTruth()` using an existing citation, and V2 has no deterministic errors for it.

O/n007 A0 claim_0 states `PndGeoHandling::GetPath(Int_t shortID)` on an instance. Its cited class documentation lists GetPath and its return meaning. The exact qualified literal is absent, so claim_0 is excluded; V1 receives only initialization claim_1. A1 claim_2 repeats the qualified representation and is again rejected in V2.

These are independent question-level examples of **PRE_V1_DETERMINISTIC_IDENTIFIER_ELIGIBILITY** loss. Neither establishes V1 mapping omission of a supplied claim. Existing semantic support of a useful fact and deterministic proof of its qualification are different questions. This design preserves the prior correction rather than reverting to semantic-undercheck attribution.

## 4. Current source contract, quoted accurately

`QAAgent._verify` begins at `src/panda_agent/qa.py:3228`. For each claim, `_claim_ev` resolves its own cited IDs from current QA evidence, with retained support evidence available only for an unchanged retained claim. The joined aggregate at lines 3306-3320 contains, in order for each resolved item:

```python
[
    item.get("text", ""),
    locator.get("path") or "",
    locator.get("symbol") or "",
    locator.get("url") or "",
    " / ".join(locator.get("section_path") or []),
]
cited = " ".join(cited_parts)
```

The extraction and rejection at lines 3344-3350 are:

```python
for token in set(re.findall(r"[A-Za-z_][A-Za-z0-9_:./-]+", claim.get("claim_text", ""))):
    token = _normalise_rejected_identifier_token(token)
    is_path = token.count("/") >= 2 or token.startswith(("macro/", "src/", "data/", "pgenerators/", "model/", "fit/")) or token.endswith(_CODE_DATA_EXTENSIONS)
    if ("::" in token or is_path) and token not in cited:
        message = f"unsupported identifier {token}"
        errors.append(message)
        claim_errors[claim_id].append(message)
```

`_CODE_DATA_EXTENSIONS` is `(.C, .py, .root, .h, .hpp, .cpp, .cxx, .json, .txt, .yaml, .yml)`. Path behavior is quoted for separation, not selected for repair.

The operative coverage-mode boundary at line 3377 is:

```python
reviewable_claims = [c for c in claims if not claim_errors.get(str(c.get("claim_id") or ""))] if shadow else claims
```

Production answer-obligation mode is included in the coverage-mode flag named `shadow`; the variable name does not mean this is a shadow-only finding. `untrusted_claims` uses `_model_claims(reviewable_claims)` in those modes. Other deterministic errors remain independently fatal. Legacy payload behavior is not redefined here.

**Current exact means case-sensitive contiguous substring presence (`token in cited`), not lexical-boundary equality, whole-symbol equality, a declaration check or signature resolution.** An exact value in `locator.symbol` already enters this same aggregate. Version/source IDs do not enter the string; they participate in separate authority checks. Source/object types, titles, parent IDs, parser metadata and graph edges do not enter it.

## 5. Token grammar and punctuation

`_normalise_rejected_identifier_token` at `qa.py:72` is unchanged:

```python
token = token.rstrip(".")
if token.endswith(":") and not token.endswith("::"):
    token = token[:-1]
return token
```

It strips trailing periods and at most one final colon when the token does not end in `::`. It does not remove qualification, normalize case or collapse whitespace. Regex matches are maximal runs in the stated alphabet, begin with a letter/underscore and require at least one further character; `::` at the beginning of prose is not captured. Parentheses and signature arguments are not part of a qualified-name token. Thus `Owner::Set(int)` checks the extracted name `Owner::Set`, not that overload.

For design reasoning only, ordinary qualification can be described as `[A-Za-z_][A-Za-z0-9_]*(::[A-Za-z_][A-Za-z0-9_]*)+`; the last component is a member/symbol name and the preceding components are a scope path. This does not identify class versus namespace versus enum. The selected policy adds no parser and does not restrict or replace the existing extractor.

Known extraction limits: templates split at `<`/`>`; `Owner::~Owner` splits at `~`; conversion/operator forms split at spaces or punctuation; a leading global `::` is omitted; slash/dot/hyphen can remain in a captured token. Whitespace-separated `A :: B` is not reconstructed as one qualified token. A trailing `::` remains significant. Constructors `Owner::Owner`, destructors, operators, templates, macros and signatures receive no new fallback. Their existing extracted fragments retain current behavior; this does not certify the full complex spelling. No tokenizer defect was established that is inseparable from the present design.

## 6. Evidence metadata capability matrix

Saved code version for the relevant PandaRoot citations is `pandaroot@18c09e91100db27867ded30e708b4dae95bd8357`; saved web version is `pandaroot_sphinx_2023_08_25_dev@5bff86c0f3a1102c80f3466a8ca0a63db48c0c7d8f142a78a0849219d7844f87`, captured date `2026-07-30`. These are existing authority values, not new integrity calculations.

| Item / actual upstream type | Exact target literal | Member literal | Owner signal actually present | `locator.symbol` | Section, URL and path | Selected S0 outcome |
|---|---|---|---|---|---|---|
| F `evidence.00c987d640013db2875fefe3` / sphinx_section | No `RhoCandidate::GetMcTruth` | GetMcTruth, on separate flattened lines | RhoCandidate is the counterpart/return object; muplus has RhoCandList type. No receiver-type or declaring-scope link | null | Accessing the MC truth under MC-truth headings; tutorial URL/anchor; saved HTML path | REJECTED |
| F `evidence.66beb6fd9691050770b7879f` / source_file_chunk containing RST | No | No GetMcTruth in this two-line item | Counterpart RhoCandidate prose only | null | `docs/Tutorials/tut_02_04_analysis_mctruth.rst`:23-24; no URL/section | REJECTED; cannot supply missing ownership |
| O `evidence.b26ce9e5c08c64381b3ac05c` / sphinx_section_chunk | No `PndGeoHandling::GetPath` | GetPath and Int_t shortID | Human-readable `class PndGeoHandling : public FairTask`, Public Functions list and method description; no typed member-to-owner metadata | null | `section_path=[PndGeoHandling ¶]`; Tools/PndGeoHandling.html URL and saved path | REJECTED |
| O `evidence.a5ee8ebd36a4a2edd82f9bf9` / function | No target GetPath qualification; other exact symbols present | fGeoH->GetPath(id) | fGeoH assigned from PndGeoHandling::Instance(); no receiver type or factory return signature | PndSdsRecoHit2, the caller's symbol | `tracking/GenfitTools/recohits2/PndSdsRecoHit2.cxx`:58-99; no section/URL | REJECTED for target; exact literals retain existing pass |
| F `evidence.aef1029b460a3b22035622ff` / Sphinx full-tree section, exact-pass control | Yes: PndAnalysis::McTruthMatch, RhoCandidate::SetType, RhoCandList::SetType | Yes | Explicit qualified method wording supplies name-level representation | null | Full MC truth tree match headings; same tutorial URL with its own anchor | ELIGIBLE for those exact tokens |
| O same b26ce9 item / second exact-pass control | Yes: PndGeoHandling::Instance | Instance | Explicit qualified text in constructor guidance | null | PndGeoHandling page/section above | ELIGIBLE for that exact token |

The representative source-code item is O/a5ee8; the representative Sphinx items are F/00c987 and O/b26ce9. Their object types were observed in saved retrieval-channel entries. A `source_id` identifies a source and its version, not a declaring scope; `source_version_id` binds provenance, not a member relation. File paths, page names and titles are locators, not ownership proofs.

`Evidence` (`models.py:184`) has object_id, source/source_version IDs, text, locator, channels, score and authority level, but no object_type, source_type, KnowledgeObject.metadata or owner-member edge. QA's model projection further retains just evidence_id, source IDs, locator and text. The full selected Evidence is available to the host; this absence is not inferred only from the narrower model projection. The object's upstream type can be read offline from the saved trace, but obtaining more KnowledgeObject fields at runtime would be a new projection/data dependency, not an existing fallback input.

## 7. Ownership-proof requirements and metadata provenance

An absent qualified token could be relaxed only with a deterministic, evidence-local binding of the complete scope path to that specific member. A nearby scope name and member occurrence are not that binding. For a call, receiver type and the relevant declaring scope must not be confused with return type, containing caller or factory name. Inheritance, aliases, overloads and nested scopes cannot be silently inferred.

Existing source generation does not supply a uniform binding:

- `SourceLocator` (`models.py:69`) validates basic fields and line ordering; `symbol` is an optional string without a full-scope guarantee.
- `parse_cpp` (`ingestion.py:274`) creates class/function objects with `_node_name`, line spans and parser metadata. `_node_name` at line 155 selects identifier nodes, not a certified fully qualified declaring-scope/member path. The inspected code citation's symbol denotes PndSdsRecoHit2, not the owner of every invoked method in its body. No caller-scope inference is valid.
- `parse_web` (`ingestion.py:602`) extracts `get_text("\n", strip=True)` and heading ancestry. It does not emit Sphinx domain object IDs or class/member DOM associations. A section may contain multiple classes, examples, inherited-member lists or quoted code.
- Derived chunk locators preserve parent fields while narrowing line spans where available. Web chunks can retain section headings without preserving the original DOM's member enclosure. O/b26ce9 is a section chunk and ends mid-list. A page title plus a member word is not an independently certified ownership edge.
- Upstream parser language/error metadata and parent/chunk identities are not projected into Evidence. Introducing them would require a separately designed representation and migration; merely adding an eligibility helper cannot manufacture them.

The absence of a generic safe binding does not dispute a human reviewer's n007 class-document interpretation. It prevents treating the same loose display cues as an authoritative runtime predicate for every document and for n018's different representation.

## 8. Preserved exact-match path and positive controls

For any extracted/normalized qualified token, presence in the existing cited aggregate remains the strongest available path and remains accepted at identifier level. This includes exact locator.symbol values; no new symbol-only path is needed. It does not guarantee truth of the claim or a correct overload.

F/n018 claim.2 and claim.3 have empty saved deterministic error lists and are in V1 input. Their aef1029 citation literally contains PndAnalysis::McTruthMatch and both SetType qualifications. O/n007 initialization claim_1 similarly has no deterministic errors, reaches V1 and cites the literal PndGeoHandling::Instance(). The selected policy retains each observed token decision. No new run, replay or test establishes a semantic before/after result.

Source-code exact literals such as PndGeoHandling::Instance in O/a5ee8 also enter the aggregate even though locator.symbol denotes the caller. File-path literals in that locator retain the path rule independently. The existing integrity test at `tests/unit/test_qa.py:1970` demonstrates the intended independent wrong-code-version and absent-qualified-identifier checks by its assertions; those assertions were inspected, not re-executed or reported as passing this turn.

## 9. Candidate policies S0-S4 and signals A-E

| Policy | Deterministic proposition considered | F/n018 | O/n007 | Decision |
|---|---|---|---|---|
| S0 strict | Existing normalized token is a substring of the current cited aggregate | REJECTED | REJECTED | **Selected**; preserves known limitations without unsupported ownership inference |
| S1 structured symbol | Exact path above OR `locator.symbol == token` | REJECTED: null symbols | REJECTED: null/caller symbol | Redundant: symbol is already in the aggregate. No gain, no new implementation |
| S2 same-item ownership | Exact path OR authoritative same-item binding(full scope, exact member) | UNRESOLVED ownership; would fail closed | Display association strong for human review; no certified binding field; unselected fallback unresolved | No implementation-ready common predicate. Title/member co-occurrence is insufficient |
| S3 citation-set composition | Exact path OR owner evidence A plus member evidence B | UNRESOLVED receiver type | UNRESOLVED generic binding despite coherent human interpretation | Reject union without an explicit identity edge; same source/version alone is insufficient |
| S4 normalization/deletion | Remove qualifier and check/submit member | Would appear ELIGIBLE for member | Would appear ELIGIBLE for member | Rejected: drops the owner assertion, admits wrong owner, mutates content if applied to claims |

UNRESOLVED in candidate analysis means the proof obligation has not been established. It is not a new runtime status and cannot become a warning/pass. Under selected S0 the runtime outcome is REJECTED with the existing error.

Signals evaluated: A (exact structured symbol) is already covered; B (authoritative owner scope plus exact member) lacks a binding field; C (instance use plus object type) fails for n018 and remains unresolved for n007's factory assignment; D (class-body declaration) could support a narrow intact simple declaration with proven enclosure, but the motivating n018 citation is not such a declaration and arbitrary nested/truncated C++ would need scope parsing; E (documentation class context) is a display hint here, not retained Sphinx member identity. No universal predicate across C++, Sphinx, README/workflow and Python is selected. No new language framework is justified by two exposed examples.

## 10. n018 application under each candidate

The decisive tutorial lines, flattened by ingestion, express `RhoCandidate *truth = muplus[i]->GetMcTruth();` after a RhoCandList declaration. The left-hand type describes the returned truth pointer. The source does not declare the type returned by RhoCandList's indexed access, bind muplus[i] to RhoCandidate as receiver, or declare GetMcTruth inside that type. Generic prose describes the counterpart object, not a verified receiver/declaring-scope edge. The RST citation adds that same prose without the method.

S0 and S1 reject. For S2/Signal C, `Owner *result = receiver->Member()` permits a different receiver type in ordinary code; a return-object rule would wrongly infer Owner::Member. S2/Signal D or E has no receiver class body/member domain context in this tutorial. S3 cannot reconstruct an operator[] type from these two items; combining return-type prose with a member call still lacks that relation. S4 would pass a different assertion and is unsafe.

**Selected outcome: REJECTED**, exact qualified token absent. **Owner equivalence: UNRESOLVED from current cited runtime representation.** A1's later unqualified statement and V2 success do not prove qualification and are prohibited as runtime fallback authority. No claim is made that this design reduces revisions or recovers a final answer.

## 11. n007 application under each candidate

The class-document item displays PndGeoHandling, its public functions and `GetPath(Int_t shortID)` with the path-return explanation. This is useful human semantic support and stronger ownership presentation than n018. However, its generic section/chunk representation has no class-member binding, full enclosing-scope identity, signature field or DOM member ID. Using the page basename or section title as class ownership would also accept an unrelated method in an example or another class inside that page.

The code item assigns fGeoH from PndGeoHandling::Instance and calls fGeoH->GetPath(id). Without the factory return declaration or receiver type, that assignment is not a deterministic type certificate. Its locator.symbol identifies PndSdsRecoHit2. It cannot supply PndGeoHandling::GetPath as an exact structured symbol.

S0/S1 reject; S2 has unselected document association but no common safe rule covering n018; S3 supplies no additional explicit identity edge; S4 erases qualification. **Selected outcome: REJECTED.** A narrow document-specific design could be investigated later, but no such separate repair is selected or implementation-ready under the required common-predicate threshold.

## 12. Neutral wrong-owner and ambiguity counterexamples

The following are frozen **design expectations**, not implemented or executed fixtures. Except where explicitly stated, the proposed qualified token is absent from all accepted aggregate fields; no misleading exact token is planted in a comment/URL/locator.

| Cited evidence / claim | Selected S0 decision | Ownership reason / rejected inference |
|---|---|---|
| `class Birch { void Run(); }` / `Maple::Run()` | REJECTED | Run belongs to no proven Maple scope; member-only matching is unsafe |
| `class Cedar { void Reset(); } class Birch { void Reset(); }` / `Cedar::Reset()` | REJECTED | S0 cannot compose even a legitimate unqualified declaration; same member in two scopes is not a binding predicate |
| Same two classes plus exact `Cedar::Reset` in a valid cited field | Identifier ELIGIBLE | Existing exact path; this does not infer support for all assertions about Reset |
| Only `alpha::load` / `beta::load` | REJECTED | Different scope spelling; no namespace substitution |
| `obj.Run()` with no declaring type / `Maple::Run()` | REJECTED | Static/member and receiver ownership unresolved |
| `Cedar *result = proxy->Run();` / `Cedar::Run()` | REJECTED | Return type is not receiver type; neutral n018 safety counterexample |
| `proxy = Maple::Instance(); proxy->Run();` / `Maple::Run()` | REJECTED | Factory class spelling does not establish return/receiver type |
| Derived inherits Base and `obj->Method()` / either `Derived::Method` or `Base::Method` | REJECTED | No inheritance or declaring-scope inference |
| Cited A mentions Maple; cited B mentions Run on an unrelated object / `Maple::Run` | REJECTED | Citation union cannot manufacture an ownership edge |
| Uncited B declares Maple::Run, cited A mentions Run only / Maple::Run | REJECTED | Uncited evidence cannot enter eligibility |
| Matching title/filename Maple, body declares Birch's Run / Maple::Run | REJECTED | Filename and generic heading are not class ownership |

This is fail-closed reasoning for **absent-qualified-literal fallback**. Existing substring acceptance can admit a spelling appearing in a comment, quotation or longer name; normal semantic support remains necessary. The design does not claim universal wrong-owner exclusion across inherited exact-pass behavior.

## 13. Namespace, nested scopes and overload boundaries

Complete scope identity would be required for any future fallback: `A::B`, `Outer::Inner::Run` and `Inner::Run` are not semantically interchangeable; neither is Base with Derived. No alias expansion, namespace stripping or inheritance resolution is selected.

The unchanged substring predicate has a specific limitation that must be reported rather than hidden:

| Evidence literal / extracted claim token | Actual selected identifier decision |
|---|---|
| `Inner::Run` / `Outer::Inner::Run` | REJECTED: longer token absent |
| `Outer::Inner::Run` / `Inner::Run` | ELIGIBLE by existing substring presence; abbreviated full-scope semantics remain for normal review |
| Only unqualified Run in nested context / either qualified token | REJECTED |
| `Owner::Set(int)` / `Owner::Set` | ELIGIBLE at name level; no signature/overload certification |
| `Owner::Set(int)` / a claim asserting Owner::Set accepts a string | Name token eligible; whole claim requires ordinary semantic support and may fail |

Thus the requested nested-scope fail-closed expectation applies where the qualified token is absent. Universal rejection of shortened nested qualification would require tightening existing exact acceptance. That would conflict with the instructed preservation of exact behavior and enlarge this task; no such tokenizer/boundary repair is selected. This limitation is explicit, not a new waiver.

Constructors `Owner::Owner` can still pass when their extracted token is present. No constructor/destructor/operator equivalence is introduced. No claim of overload safety follows from name eligibility. A future ownership design would have to distinguish name-level admission from signature-level semantic support without overriding the latter.

## 14. Same-evidence versus citation-union authority

A same-item scope-to-member proof is preferable to independent name co-occurrence because it limits accidental composition. However, same item alone is insufficient: a page can contain several classes and a method call can be inside an unrelated caller. A proof needs the relation, not just physical proximity. Current source_version equality also does not imply one owner.

The existing exact aggregate remains the union of a claim's own resolved cited items. Retaining that aggregate does not authorize composing owner text in A with member text in B into a newly accepted qualified spelling. Since items are separated with spaces, the contiguous scope token cannot be manufactured by joining Owner in one and Member in another. If one item actually contains the token, existing exact behavior applies.

A future same-item fallback might leave split documentation rejected; that is an acceptable conservative limitation. A broader claim-citation-set fallback would need an explicit, version-bound identity edge between the pieces. No such edge is available here, and no cross-document fallback is selected. Existing retained-citation handling remains limited to unchanged retained claims; it is not an uncited-evidence discovery path.

## 15. Selected deterministic predicate

The following is a **specification of the retained contract**, not a new executable helper or test. Inputs are the extracted token and only the current claim's resolved cited Evidence items, using exactly the existing resolution rules. Missing/invalid IDs retain their independent errors.

```text
normalise(t):
    strip terminal periods
    if t ends in one colon but not double colon: remove that final colon

aggregate(E):
    for each resolved cited item in existing order:
        append text, locator.path, locator.symbol, locator.url,
               section_path joined with " / "
    join those strings with " "

qualified_identifier_eligible(t, E):
    n = normalise(t)
    precondition: "::" occurs in n
    return n in aggregate(E)    # case-sensitive contiguous substring

fallback_owner_member_equivalence(t, E):
    return false               # no new fallback selected
```

For the whole existing token branch, an unsupported-identifier error is emitted exactly when `("::" in n OR existing_is_path(n)) AND n not in aggregate(E)`. Ordinary unqualified names that are not paths do not enter this branch. Path and qualified status can overlap; neither bypasses the other. Token/claim text, citations and metadata are not mutated.

Owner/member proof is not attempted by the selected runtime predicate. Its accepted fields, normalization, union behavior, unsupported-syntax behavior and false outcome are fully defined above. No model output, future A1 result, generator answer_point_ids, parametric knowledge, Gold, case ID or repository-wide runtime search is an input.

## 16. Fail-closed errors and independent authority

When the qualified token is absent, retain `unsupported identifier <normalized-token>` in both the ordinary errors and claim_errors. No warning downgrade, distinct status, schema addition or eligibility override is selected. The coverage-mode claim stays out of reviewable_claims.

The source separately checks citation IDs, expected code source_version for luminosityfit/pandaroot/restgas_determination, code path/line locator completeness, paper page completeness and Sphinx URL/snapshot/section completeness. An identifier pass never clears those errors. The existing source-specific version checks are preserved; this design does not assert that every source type already has a universal version validator.

Monotonic preservation is literal here: existing exact-pass and exact-reject outcomes remain the same; unrelated errors remain fatal; admission, quote validation and proof provenance remain the same. There is no unsupported-to-eligible conversion selected, so no semantic benefit metric is claimed.

## 17. Claim and citation immutability

The host never deletes qualifiers, rewrites A0 scientific text, adds/replaces evidence IDs, injects source text, changes locators or searches for another citation to make this predicate pass. No string-normalization result is substituted into claim_text. Normalizing an extracted token for the existing presence check remains separate from claim rewriting.

A1 may generate a genuinely different wording under the already existing target-local contract, as observed in F/n018. That historical behavior does not authorize the deterministic host to perform the same rewrite. Claim text and citation lists remain inputs, not repair outputs.

## 18. Interaction with V1, A1 and V2

S0 leaves current claim exclusion and review inputs unchanged. Deterministic eligibility establishes only whether an extracted representation can reach ordinary semantic review; it never declares whole-claim truth, relevance, point mapping or coverage completeness. A future equivalence success, if separately designed, could avoid only its own identifier error; any other error would still exclude the claim.

V1 retains its complete mapping inventory over supplied reviewable claims, all-to-all supporter/basis citation contract, ordinary check semantics and canonical relations. A1 target-local authorization and V2 full-contract recheck remain unchanged. There is no added review stage, retry, semantic forced acceptance or automatic target suppression. A newly eligible claim in any future implementation would still be allowed to fail model support/relevance or completeness.

F/n018's A1 representation repair and O/n007's repeated qualification rejection remain historical observations. Neither a final recovery nor fewer A1 calls can be guaranteed from an unexecuted design.

## 19. Future implementation seam and readiness threshold

If a separately authorized design later establishes a safe minimal equivalence predicate, the smallest candidate seam is a helper adjacent to `_normalise_rejected_identifier_token`, invoked from `_verify`'s deterministic qualified-token branch with the claim-local cited items. The path branch, retained-citation resolution, text/citation bytes and independent errors must remain unchanged. Do not scatter symbol-name exceptions in `_verify`.

**No helper implementation, refactor or test edit is recommended under this result.** S1 would duplicate existing logic; S2/S3 would introduce an unproved relation. `IMPLEMENTATION_READY=false` because both cases cannot be admitted by one established safe predicate using current metadata. The threshold also requires wrong-owner rejection, ambiguous-owner fail closure, exact-pass preservation, no uncited authority, no truth inference and a small seam; merely passing the two positive examples would not satisfy it.

If future metadata were considered, it would need a version-bound full scope/member identity with documented derivation and completeness, not a guessed title field. C++ receiver/declaration links and Sphinx member-domain associations have different derivations; n018 may require information absent from its current citations, not just retention of DOM styling. New fields would affect ingestion, Evidence projection, artifact compatibility and possibly schema/version identities. This is an unselected architecture option, not permission for a metadata migration, reindex or ownership infrastructure project. An eventual runtime relaxation would require reassessing product lineage even if prompts/fingerprint stayed unchanged; this documentation task advances neither.

## 20. Future RED/GREEN acceptance matrix

These neutral fixtures are frozen design requirements **before any future relaxation implementation**, not executed tests and not implementation authorization. Under selected S0 there are no recovery GREEN targets. Any new owner-proof input or predicate requires a separately reviewed contract before assigning a GREEN expectation.

| Fixture | Retained S0 expectation | Requirement for any later proposed relaxation |
|---|---|---|
| A: `Cedar *result = candidates[i]->Lookup();` / `Cedar::Lookup` with only return-object context | REJECTED; neutral n018-style RED remains | Must remain rejected without receiver/declaring-scope proof; adding a return-type shortcut is forbidden |
| B: class Maple doc section lists Run; qualified Maple::Run absent | REJECTED; neutral n007-style RED remains | GREEN only with a generic authoritative member-to-full-scope binding, not heading co-occurrence |
| A+ and B+: absent qualification plus independently proven full owner/member binding | REJECTED under S0 | Candidate GREEN only after the missing binding representation/predicate is separately designed; no input invented this turn |
| C: Birch declares Run / Maple::Run | REJECTED | Must stay RED |
| D: two owners declare Reset | REJECTED without exact token | Must reject ambiguous owner; any pass needs the selected owner specifically proven |
| E: alpha::load / beta::load | REJECTED | Must stay RED |
| F: exact Maple::Run in valid cited text or exact locator.symbol | Identifier ELIGIBLE | Must stay GREEN at identifier level, independent of semantic verdict |
| G: exact token plus wrong code version, missing evidence or incomplete locator | Claim excluded by other errors | Identifier success must never clear unrelated errors |
| H: absent/present path literals, including a token also containing `::` | Existing path rule/error unchanged | No path bypass; extension and prefix rules preserved |
| I: qualified claim bytes and citation IDs | Unchanged | Must remain byte-for-byte unmodified by eligibility |
| J: fake downstream reviewer | Rejected claim absent; exact eligible claim reaches V1 if no other errors | If future proof makes a claim eligible, verify V1 delivery and permit reviewer rejection; do not require semantic acceptance |
| K: owner evidence uncited, or owner/member only in different unbound cited items | REJECTED | Must stay RED |
| L: namespace/nested/inheritance/static ambiguity | Absent token rejected; inherited substring caveat in section 13 | No new qualification equivalence; preserve exact behavior explicitly |
| M: name-only Set with explicit int overload | Identifier eligible if extracted name present | No assertion of string-overload support; normal semantic check remains |
| N: terminal punctuation, trailing `::`, templates/operators/destructors | Existing extraction/normalization behavior | No tokenizer expansion or fuzzy normalization hidden in the repair |
| O: class title says Maple, embedded example belongs to Birch; truncated/nested class body | REJECTED without exact token | Reject owner-by-title, owner-by-caller and uncertain scope closure |

A later implementation should use fake providers for geometry checks and direct deterministic controls; it must not use live QA or an external judge just to test the helper. No need to embed PANDA symbol names in generic fixtures. This matrix records expected properties only; RED/GREEN has not been measured.

## 21. Rejected alternatives and outcome selection

Rejected: qualifier removal, member-only/suffix checks, factory-name type inference, return-type receiver inference, title/filename ownership, unbound cross-citation unions, forced V1 mappings/completeness, new LLM calls, fuzzy/embedding matches, runtime Internet lookup, corpus-wide symbol search and a new parser/database framework. No case-specific rule, source quota or Gold-derived expected symbol is proposed.

Outcome B is not justified: n018's receiver/declaration identity is not established and the required common predicate is absent. Outcome C is not selected as a mandatory new metadata task: the necessary ownership information for n018 is not shown to be derivable from the current cited source content, and no minimal representation/migration is established. It remains an explicitly described option rather than an infrastructure mandate. Outcome D is unnecessary because A already expresses the evidence-supported result.

**Primary outcome remains A.** Recommend **no identifier-eligibility implementation; retain the strict rule and documented false-exclusion limitation**. No additional immediate roadmap task is selected. Reconsideration would need separately authorized evidence or a reviewed ownership representation; it is not automatically authorized by the confirmed failure family.

## 22. Scientific and retained semantic limitations

This is static source and saved-exposed-artifact reasoning only. No empirical before/after metric, recovery proportion, call reduction, final-answer improvement or population incidence was measured. Design counterexamples are reasoned expectations, not newly passing tests. Historical version/source authorities were read, not recomputed or expanded.

Both semantically useful qualified claims remain excluded under the selected contract; the retained policy also has the inherited substring/complex-token limitations documented above. No universal C++ type/overload authority or Sphinx ownership certification is claimed. The human semantic adequacy findings remain valid while deterministic qualification stays conservative.

n019/n006/n023's **EVIDENCE_GAP_WITH_COARSE_COMPLETENESS_ACCEPTANCE** remains a separate retained limitation. No retrieval or V1 completeness repair is proposed in this task. n022/n025/n028's **SAFE_WITH_FROZEN_SEMANTIC_INVARIANT** result is preserved without rereading their cases. Rule 5, original G5 incomplete precedence and the absence of fresh generalization/release evidence are unchanged.

## 23. Static validation and delivery

Only this design and the current authoritative sections of `docs/EVALUATION_STATUS.md` and `docs/GENERALIZATION_ROADMAP.md` change. Historical prose/reports, source/tests/configuration/data and raw stores remain unchanged. Static delivery checks compare the allowed path set, preserve earlier checkpoint prose and historical chronology, retain frozen lifecycle fields, resolve document links and run `git diff --check`. These are document/Git checks, not product tests or validator execution.

Commit message: `Design deterministic identifier evidence eligibility`; parent is the entry HEAD in section 2. Delivery SHA is reported in the final response and resolved from Git history. No push. Worktree cleanliness after the requested commit is a delivery check, not a new frozen scientific candidate or acceptance manifest.

## 24. Lifecycle and boundary receipt

```text
G5_IDENTIFIER_EVIDENCE_ELIGIBILITY_REPAIR_DESIGN = COMPLETE / PASS / NO_IMPLEMENTATION_READY
IDENTIFIER_ELIGIBILITY_DESIGN_OUTCOME = STRICT_RULE_RETAINED / NO_SAFE_RELAXATION
SELECTED_IDENTIFIER_ELIGIBILITY_CONTRACT = STRICT_EXACT_MATCH_RETAINED
KNOWN_FALSE_EXCLUSION_FAMILY = F_N018 / O_N007
IDENTIFIER_ELIGIBILITY_FAILURE_FAMILY = CONFIRMED_ON_F_N018_AND_O_N007
SAFE_RELAXATION = NOT_ESTABLISHED
IMPLEMENTATION_READY = false
EXACT_QUALIFIED_MATCH = PRESERVED / EXISTING_SUBSTRING_SEMANTICS
WRONG_OWNER_FAIL_CLOSED = DESIGN_VERIFIED_FOR_ABSENT_QUALIFIED_LITERAL
AMBIGUOUS_OWNER_FAIL_CLOSED = DESIGN_VERIFIED_FOR_ABSENT_QUALIFIED_LITERAL
CLAIM_TEXT_REWRITE = false
CITATION_REWRITE = false
V1_CONTRACT_CHANGE = false
PRODUCT_BEHAVIOR_LINEAGE_CHANGE = false
TARGETED_V1_VERDICT = TARGETED_V1_MECHANISM_SUPPORTED
G5_POST_OBSERVABILITY_REPAIR_TARGETED_LIVE_VERIFICATION = COMPLETE / PASS / RULE_5
N018_FIRST_WRONG_STAGE = PRE_V1_DETERMINISTIC_IDENTIFIER_ELIGIBILITY
N018_V1_MAPPING_UNDERCHECK = NOT_ESTABLISHED / CLAIM_NOT_SUPPLIED
N019_ABSOLUTE_SEMANTIC_LIMITATION = CONFIRMED / COARSE_WITNESS_OVERACCEPTANCE_WITH_EVIDENCE_GAP
SMALLER_COMPLETE_PROOF_SELECTION = SAFE_WITH_FROZEN_SEMANTIC_INVARIANT
G5_ORIGINAL_VERDICT = INCOMPLETE / PRODUCT ERROR
G5_INTEGRATED_RUN_COMPLETE = false
G5_INTEGRATED_CANDIDATE_READY_FOR_G6 = false
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_RECOMMENDATION = NO_IDENTIFIER_ELIGIBILITY_IMPLEMENTATION / RETAIN_STRICT_RULE_AND_DOCUMENTED_LIMITATION
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
NEW_PROVIDER_CALLS = 0
NEW_PROVIDER_PREFLIGHT_CALLS = 0
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
