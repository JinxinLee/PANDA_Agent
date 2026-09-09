# E2-A3-R1-FR1 — P2/P6 Failure Review and Repair Reassessment

## Decisions and preserved authority

**BOUNDED_REPAIR_RECOMMENDED. Review scope: PASS.**

- P2: **P2_REPAIR_JUSTIFIED_AT_EVIDENCE_SELECTION**. Primary taxonomy R3;
  owner: citation-eligible evidence admission before answer/revision assignment.
  Specific class: CITATION_INCOMPLETE_PAGE_ADMITTED_TO_CLAIM_EVIDENCE.
- P6: **P6_NO_PRODUCT_REPAIR_JUSTIFIED**. Observation:
  NONCRITICAL_OPTIONAL_COMPLETENESS_DIFFERENCE_WITH_LIMITED_REPEAT_EVIDENCE.
  No generic required-content failure or prompt repair is established.

Starting HEAD: `8c962093c254404c0ccc9bb2908dc912af8646fd`; clean initial tree,
expected ten-commit history verified. Review commit is the normal commit
containing this report, companion JSON, and lifecycle docs. No product, corpus,
locator, prompt, gate, or default changes are made.

Historical A3 remains FAIL/Q7; FR1 remains PASS/REPAIR_JUSTIFIED; R1 remains
FAIL/P2_P6. Colon normalization, S1-S12 and fresh g112 success remain established.
R1 P1/P3/P4/P5/P7/P8/P9 remain PASS. No waiver is granted or result rescored.

Sources inspected: current AGENTS and evaluation policy/status/roadmap; QA,
model, ingestion, retrieval and prompt code; ingestion/QA tests; A3/FR1/R1
reports, protocols, manifests, raw records, judgments and results. Scientific
data scope is only the existing A3/R1 exposed records. The companion JSON
contains reconstruction, exact record pointers, citation rows and counters.

## P2: frozen g027 reconstruction

R1 raw commit: `4092209a11f57ac757502b01e2c55332b88a0519`.
Question and exact approved Gold obligations are recorded in JSON. Obligations:
give PndTargetGenerator's path in locked PandaRoot; give its corresponding path
in the locked RestgasDetermination fork; explain source-version-specific behavior.

Legacy has no integrity errors or revision. Runtime decomposes these into three
points. Initial claim.1 and claim.2 identify the two definition paths; claim.3
explains the fork's GPL header and downstream rest-gas/target-mode differences.
It cites three code records plus this offending item:

```text
evidence_id = evidence.d452f25b295c0ce037b92b26
object_id = object.3e790d97468c8387c1831cf2
source_id = pandaroot_sphinx_2023_08_25_dev
source_version_id = pandaroot_sphinx_2023_08_25_dev@5bff86c0f3a1102c80f3466a8ca0a63db48c0c7d8f142a78a0849219d7844f87
locator.path = pandaroot_sphinx_2023_08_25_dev/raw/~pandacc/documentation/2023-08-25-dev/sphinx/Running/MasterTasks.html
locator.url = https://webdocs.gsi.de/~pandacc/documentation/2023-08-25-dev/sphinx/Running/MasterTasks.html
locator.snapshot_date = 2026-07-30
locator.section_path = []
retrieval_channels = [exact]
```

The item contains the full MasterTasks page, including navigation and multiple
sections. It is not a fragment-addressed section. Full frozen text is retained
in the companion JSON. Local frozen HTML, parsed with the same script/style/nav
removal and text extraction, exactly equals the frozen evidence text; no new
download or hashes were used.

Initial runtime errors:

```text
incomplete web citation evidence.d452f25b295c0ce037b92b26
missing answer point point.3
```

The citation error excludes claim.3 from runtime semantic review. The first
audit is evaluable but misses point.3. Revision input is reconstructed from
that state: claim.3 unsupported, claims 1/2 retained, missing point.3, same
evidence bundle. Raw artifacts store responses, not exact request bytes; the
JSON labels this as reconstructed input. Revision removes the web citation,
narrows the comparison, and retains the three code citations. Final review is
clean, coverage complete/evaluable, status answered. Both public answers,
initial/final claims and all review states are preserved in JSON or exact
frozen-artifact pointers. P2 correctly remains FAIL under all-reviews accounting.

## P2: intended contract and object identity

The intended public web-citation contract is not inferred solely from the
rejecting implementation. `QA_AGENT.md` lines 350–358 explicitly requires web
snapshot date, URL, and heading. `_verify` enforces URL + snapshot_date + nonempty
section_path. The generic SourceLocator model permits empty section_path because
it represents many object types; schema validity does not imply public citation
eligibility. Evaluation policy requires grounded evidence and correct owning-layer
repair and provides no URL-only exception or waiver for this task.

Crucially, `ingestion.parse_web` deliberately creates a `sphinx_page` with URL
and date but no section path, and separately creates `sphinx_section` objects
with heading hierarchy and stable anchors where available. The existing test
`test_sphinx_sections_use_hierarchical_anchor_locators` explicitly expects an
empty page section_path and a nonempty child hierarchy. Thus an empty hierarchy
on this page object is **not evidence of metadata loss**.

The matching local normalized object is explicitly `sphinx_page`, with canonical
locator equal to the fragment-free page URL and preserved metadata.headings.
It occurs in normalized snapshot
`9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94`.
Its source-version and locator agree with the frozen record. The source manifest
identifies the same locked web snapshot. Other local normalized snapshots were
checked for this exact object identity, not treated as current authority.

Authoritative HTML contains `#mastertasks`, `#simulations-macro`,
`#beam-target-settings`, and other headings. Heading recovery is deterministic
and requires no question/answer inference. However, the whole page contains
multiple sections; copying one subsection heading into the existing whole-page
object would silently change its locator semantics. Root title recovery does
not demonstrate a lost section locator. This is interpretation C: legitimate
page/navigation context that is citation-incomplete under the public contract.

The final retrieval selector checks duplicate locators and source/type budgets,
but has no public-citation eligibility check. Exact retrieval can prioritize
page-level objects. The generator receives these evidence IDs, and the existing
answer prompt permits supplied IDs without explicitly specifying the three web
locator fields. Therefore:

- V1 rejected: the public contract requires a heading, and this URL has no fragment.
- Locator/ingestion defect rejected: page hierarchy is intentionally empty;
  headings and separate section representation are preserved.
- A1 rejected as primary owner: no explicit existing generator constraint makes
  it responsible for repairing locator metadata or filtering these fields.
- R3 selected: the evidence offered for claim assignment includes objects the
  existing verifier will deterministically reject as public citations.

## P2: evidence sufficiency and counterfactuals

The remaining code evidence is:

- `evidence.9a6cd964b297593f17a962c1`: PandaRoot target generator, lines 1–103.
- `evidence.4410d28943c43b9065bc7e67`: Restgas target generator, lines 1–115,
  including GPL header at excerpt line 5.
- `evidence.bbdc7b25b56c2217095ed02b`: Restgas PndMasterRunSim, lines 1–993,
  including the 2024 profile default at line 59 and target handling later.

These establish the two paths, source versions, GPL distinction, and downstream
configuration. The Sphinx page additionally describes upstream target modes and
the 2021 profile. **Partly additive** is the appropriate classification for the
exact initial cross-repository configuration claim: code-only evidence does not
fully reconstruct every upstream steering comparison. It is unnecessary for
the approved core obligations after the supported narrowing seen in revision.
We do not infer that any arbitrary unchanged claim remains fully supported after
deleting a citation, or that Sphinx should never be selected for such questions.

Counterfactual A: substituting an authoritative root heading into an in-memory
locator changes the actual source-derived web predicate from rejection to
acceptance. It proves predicate behavior, not authorization to relabel the
whole-page object. Prefer existing correctly scoped sections over fabricated
page hierarchy.

Counterfactual B: removing only the offending Sphinx ID leaves three complete
code citations and removes this deterministic web-citation error. It does not
prove full semantic correctness of the unchanged original wording. The frozen
revision supplies separate evidence of a narrower, supported final answer.

Counterfactual C: retaining URL/date and allowing either a nonempty hierarchy
or a stable URL fragment changes **0** claim-citation decisions across the
complete A3/R1 surface, and **0** selected-evidence checks. All incomplete cited
items lack fragments. It would not fix g027. No verifier relaxation is recommended.

## P2: complete frozen Sphinx scan

Scan both A3 (56 executions) and R1 (10 executions). Public-candidate claim
snapshots include initial answer responses, revision responses, and final public
claims, deduplicated per execution by claim ID/text/ordered evidence IDs.
Each claim-to-Sphinx-evidence edge counts once per distinct snapshot; final
published edges are also counted separately. Internal scope claims are excluded.

| Surface | Complete URL/date/section | Empty section only | Other incomplete | Total |
| --- | --- | --- | --- | --- |
| A3 legacy claim snapshots | 8 | 1 | 0 | 9 |
| A3 runtime claim snapshots | 10 | 1 | 0 | 11 |
| R1 legacy claim snapshots | 3 | 0 | 0 | 3 |
| R1 runtime claim snapshots | 3 | 1 | 0 | 4 |
| All claim snapshots | 24 | 3 | 0 | 27 |
| Final published citations only | 18 | 0 | 0 | 18 |
| Selected Sphinx evidence occurrences | 106 | 38 | 0 | 144 |

The three incomplete claim edges are A3 g013 legacy/runtime, both referencing
`evidence.258612f18040b81459f72d3b` (Tools/PndMasterTasks/PndMasterTasks.html),
and R1 g027 runtime, referencing the MasterTasks page above. All three receive
the expected initial incomplete-web-citation rejection and have clean final
reviews after one revision. There are two distinct page objects, two questions,
both execution modes, and two experiments: this is a broader admission class,
not one isolated malformed object. No final published incomplete web citation
was found. Full per-edge IDs, modes, origins, locators and errors are in JSON.

## P6: frozen g002 reconstruction and Gold comparison

Question: "What are the documented prerequisites before building PandaRoot?"
Expected status: answered. Gold has one critical point, "List only prerequisites
explicitly documented by the locked Sphinx page", and no required identifiers.
It does not enumerate Spack or CVMFS as mandatory content.

R1 legacy and runtime both answer correctly and are marked supported by the
blinded judge. Both name installed external packages, FairRoot, SIMPATH and
FAIRROOTPATH. Legacy additionally explains that Spack may place the two folders
together and cluster installations may already exist on CVMFS. These are
**helpful optional elaborations**, not universal prerequisites or necessary
support for the required core obligation. No other final substantive difference
was identified beyond this extra explanation and minor wording.

Both initial arms also mention CMake with `SIMPATH/bin/cmake`; the frozen
verifier rejects that token in both arms. Legacy revision keeps the Spack/CVMFS
portion but removes the CMake portion. Runtime revision returns an empty claim
list, leaving its already-supported prerequisite claim. The runtime single
point remains covered and final review clean. This is not an R1 runtime-only
citation failure, nor evidence that the colon repair caused the behavior.

The locked installation text explains setting the two variables and then shows
build commands and a conditional newer-CMake fallback. Neither R1 final answer
retains the CMake elaboration. The broad Gold point does not create an explicit
Spack/CVMFS or fallback enumeration requirement. Within the approved contract,
no explicit required answer point or required identifier omission is established;
no final unsupported content, incorrect status, required citation-integrity
failure, or incomplete E2 coverage is found. This is a bounded offline reading
supported by the frozen review/judge, not a new independent semantic evaluation.

R1 judge input is retained at
`e2_a3_r1_targeted_paired_judged.json` records[execution_id=g002].input;
it contains only approved reference and public A/B outputs/cited evidence.
Index 2 assigns A=legacy, B=runtime. Output preferred A, both supported,
critical_regression=false, because A includes Spack/CVMFS details. P6 required
zero worse cases, so its FAIL is valid and immutable. Exact claims, revisions,
decomposition, final output and judgment are retained in companion JSON.

## P6: historical variability and repair decision

Four compatible g002 executions exist in the inspected A3/R1 scope: two prior
A3 executions and two R1 executions. They share question/Gold/reference source;
candidate identity differs by the documented verifier repair. They are not
four independent questions or evidence of model-identical reproducibility.

| Experiment / arm | Spack | CVMFS | CMake in final | Status | Runtime pair judgment |
| --- | --- | --- | --- | --- | --- |
| A3 legacy | yes | yes | yes | answered | equivalent |
| A3 runtime | no | no | yes | answered | equivalent |
| R1 legacy | yes | yes | no | answered | worse, noncritical |
| R1 runtime | no | no | no | answered | worse, noncritical |

All four initially reject SIMPATH/bin/cmake, revise once, and finish with clean
reviews. Both runtime final coverages are evaluable/complete. Spack/CVMFS are
consistently absent in the **two observed runtime outputs**, not variably present.
That repeated optional-detail difference must not be hidden behind a claim of
proven random variation. CMake retention and the pairwise preference do vary
between experiments. Two repeated cases do not establish a generic systematic
required-content omission or isolate generation from revision/renderer causality.

P6_NO_PRODUCT_REPAIR_JUSTIFIED therefore means no evidence-backed generic repair
is justified now, not proof that runtime can never lose useful detail. Do not
add Spack/CVMFS/PandaRoot-installation rules, expand Gold, or change E2 prompts.
Historical A3 quality 6/21/1 and R1 quality 2/2/1, with zero critical regressions
in both, qualitatively show occasional noncritical preferences. Do not pool
them as 33 independent cases: questions overlap and generation is stochastic.

## Next repair contract and prospective design

Next task recommendation: **E2-A3-R2 — Citation-Eligible Evidence Selection Repair**.
Execution is NOT authorized. Repair only the evidence-admission boundary that
offers IDs to answer/revision assignment. Use the existing source-specific
public citation contract as the generic predicate. Keep page objects available
for navigation/context where appropriate, but do not offer citation-incomplete
IDs as public claim evidence. Apply the same admission rule to bounded revision.
Do not silently strip citations from generated claims and assert support.

Preserve eligible code, paper and web evidence, ordering/budgets where possible,
mandatory-source behavior and compatibility. If filtering leaves insufficient
evidence, retain explicit insufficiency rather than fabricate locators or
relax verification. Any need for candidate recall, new backfill architecture,
corpus mutation, schema/prompt change or extra retrieval requires scope review.
No question IDs, page-name allowlists, inferred headings or symbol triggers.

Minimum future repair checks: T0 complete/incomplete web eligibility and negative
controls, unchanged code/paper behavior, answer/revision consistency, and full
frozen A3/R1 admission reconciliation. Record all 38 affected selected evidence
occurrences as well as the three cited failures; do not claim the future selector
has only a three-edge impact. The large difference between selected and cited
counts makes prospective verification necessary.

For targeted repair evidence, recommend six fresh pairs: g013 and g027 (the two
observed citation failures), g112 (normalizer guard), g002 (complete web citation
and optional-quality sentinel), plus two clean controls chosen and frozen before
execution. No full A3 or retrieval bootstrap is required by current evidence.
If implementation changes more than admission or causes broad loss of required
sources, reassess scope before any live run.

Future P6 gate recommendation is a separately approved **larger paired
non-inferiority design**, rather than asserting statistical quality from six
sentinels or automatically repeating the zero-worse five-case rule. A concrete
candidate design is 14 unique questions, <=1 noncritical runtime-worse,
equivalent+better>=13, and zero critical regressions. This preserves the original
A3 descriptive tolerance 2/28 as 1/14. It is not a confidence-bound guarantee.
Required-obligation/status/support and citation gates remain hard constraints.
The 14-question design could incorporate the six repair sentinels to avoid two
automatic batches; choose that single cohort if future authorization includes
activation-quality evidence. Freeze cohort, threshold, judging and stop rules
before outputs. Do not count historical repeats as extra independent samples.

Option A (same zero-worse five-case gate) is legitimate as a strict engineering
screen but highly sensitive to one optional-detail preference. Simply allowing
one worse in five would materially relax the rate and is not recommended.
Original A3-style semantics need an appropriate denominator; neither a new
quality design nor a no-product-repair decision retroactively clears R1.
Waiver granted: no. Activation remains separate and forbidden in this review.

## Verification, usage and lifecycle

Offline checks: JSON parsing and record identity; reconciliation of 27 all-state
and 18 final citation edges; actual source-derived citation predicate for
counterfactual A and all scanned cited locators; B code-citation integrity;
fragment counterfactual over cited and selected surfaces; local HTML/frozen-text
equality; unchanged product and historical artifact paths; git diff --check.
No full test suite is needed for review-only changes.

All scientific decomposition/analyzer/embedding/reranker/retrieval/QA-answer/
QA-review/QA-revision/judge calls are 0; scientific tokens 0. One separate AGY
abstract review, staffer-mtudhc13-8f645dd5, completed without repository access
or edits. Route gemini-3.8-flash-high; actual model/effort and tokens unobserved.
Its caution to separate contract failures from preferences is retained. Its
generic heading-loss inference does not override the explicit page/section
contract; its suggested repeated-seed experiments and gate changes are not
executed or imposed as extra requirements.

```text
E2-A3 = COMPLETE / FAIL / Q7
E2-A3-FR1 = COMPLETE / PASS / Q7_VERIFIER_IDENTIFIER_NORMALIZATION_REPAIR_JUSTIFIED
E2-A3-R1 = COMPLETE / FAIL / P2_P6
E2-A3-R1 FAILURE REVIEW = COMPLETE / PASS / P2_REPAIR_REQUIRED_P6_NO_PRODUCT_REPAIR
E2 = IN_PROGRESS / RUNTIME_ACTIVATION_FAILED / BOUNDED_P2_REPAIR_PENDING
normal default = legacy_question_core
E3 = NOT_STARTED
NEXT_TASK_RECOMMENDATION = E2-A3-R2 — Citation-Eligible Evidence Selection Repair
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
