# F1 — Residual Benchmark-Dependency Inventory

## Executive decision

F1 = COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED.

The bounded audit classified 21 candidates: 12 production residual findings, 3 local provenance HOLDs, 2 generic mechanisms, 2 domain mechanisms, 1 aggregate D4 exclusion, and 1 evaluator-only exclusion. The 12 residuals have 4 F2 candidates, 3 F3 candidates, 3 E1/E2 compatibility items, and 2 E3 boundary-review items. There are 0 substantiated E1 blockers.

Recommend E1 — Dynamic Question Decomposition, as a recommendation only. NEXT TASK EXECUTION AUTHORIZED = false.

PASS means this static inventory is complete and internally consistent. It does not mean dependencies were removed, D4 or Phase F is complete, or E1/F2/F3 is authorized.

## Starting repository state

- Starting HEAD: `53356ab81c1b81abe0c5ae04834f6112f6d2c1a8`.
- Branch: `main`; worktree and index were clean.
- Latest observed commit: `docs: reconcile generalization roadmap and evaluation status`.
- D4 was PAUSED / ROADMAP_RECONCILIATION, overall completion UNDECIDED; D4-A10 remained the latest accepted production action.
- Phase E was NOT_STARTED; Phase F was NOT_STARTED / SCOPE_RECONCILIATION_REQUIRED; F1 was NOT_STARTED / POTENTIALLY_VALID; F3 was partially superseded by D4.
- Current AGENTS.md, evaluation policy, current status and roadmap were read. Current code and ownership artifacts, not historical chat, determine the findings.

## Scope and explicit exclusions

Production source/configuration is read-only. Only this report, the paired JSON inventory, and the two lifecycle documents may change. No cleanup, prompt/config change, model call, retrieval, QA, scientific evaluation, database operation, or protected-split access was performed. Novel-dev content was not needed or read.

D4 query-expansion inventory was not repeated. D4-A0 metadata and directly related ownership entries establish exclusion boundaries; D4-A9-R2 mask metadata confirms partial ownership. Existing D4 dispositions are not reassessed. Tests were read selectively as provenance, never executed.

## Audit method

Followed `QAService.execute` (`service.py:136,188`) into `QAAgent.run_detailed` (`qa.py:1983-1987`), the graph (`qa.py:899-953`), and `Retriever.retrieve` (`retrieval.py:1627-1649`). Reviewed active analysis, channels, selection, sufficiency, completeness, review/revision, refusal and rendering. Production reachability is established statically, not by executing these paths.

Source comments establish explicit origins where available. Targeted `git log -S` and `git blame` show several suspicious literals were already present in initial source import `3d90848`; that provides a history limit, not proof of a particular benchmark cause. Named regression-protected tests support STRONG provenance for completeness specialization without treating their expected answers as new specifications.

Counting unit: a bounded behavior family, not each branch, literal, historical rule, or caller. `is_production_residual=true` defines the 12 residuals. HOLD and all exclusions do not inflate that total. The coupled negative-control finalizer is counted once in R04; pointer-specific enforcement R10 is excluded from R08/R09's grouped mechanisms. Risk describes static potential impact, not measured failure frequency.

| Summary key | Count |
|---|---:|
| inspected_candidates | 21 |
| production_residual_findings | 12 |
| f2_candidates | 4 |
| f3_candidates | 3 |
| e1_e2_compatibility_items | 3 |
| e3_boundary_review_items | 2 |
| keep_generic_items | 2 |
| keep_domain_items | 2 |
| d4_excluded_items | 1 |
| hold_items | 3 |
| evaluation_only_items | 1 |
| e1_blockers | 0 |

## Production dependency classification

Each candidate has exactly one primary classification. Production-conditional means a branch in the default production graph, not a shadow-only experiment. Full reachability and provenance details are in the JSON.

| ID | Classification | Location / anchor | Risk | Future owner | E1 blocker |
|---|---|---|---|---|---|
| F1-R01 | BENCHMARK_DERIVED_RUNTIME_POLICY | `configs/retrieval_policies.yaml:25` — `intents.algorithm_theory / algorithm_implementation.required_sources` | HIGH | F2_CANDIDATE | false |
| F1-R02 | HOLD_UNCERTAIN_PROVENANCE | `configs/retrieval_policies.yaml:18` — `non-paper intent required_sources` | MEDIUM | HOLD | false |
| F1-R03 | FIXED_LOCATOR_SHORTCUT_OUTSIDE_D4 | `src/panda_agent/retrieval.py:1146` — `Retriever.analyze feedback paper-page override` | HIGH | F3_CANDIDATE | false |
| F1-R04 | CASE_SPECIFIC_NEGATIVE_CONTROL | `src/panda_agent/qa.py:1071` — `QAAgent._sufficiency / _finalize exact negative control` | HIGH | F2_CANDIDATE | false |
| F1-R05 | FIXED_LOCATOR_SHORTCUT_OUTSIDE_D4 | `src/panda_agent/qa.py:1850` — `QAAgent._finalize unsupported-API header fallback` | MEDIUM | F3_CANDIDATE | false |
| F1-R06 | FIXED_LOCATOR_SHORTCUT_OUTSIDE_D4 | `src/panda_agent/qa.py:1892` — `QAAgent._finalize deleted-runtime fallback` | MEDIUM | F3_CANDIDATE | false |
| F1-R07 | HOLD_UNCERTAIN_PROVENANCE | `src/panda_agent/qa.py:1053` — `QAAgent._sufficiency exact_memory_question` | MEDIUM | HOLD | false |
| F1-R08 | BENCHMARK_SHAPED_COMPATIBILITY_LAYER | `src/panda_agent/qa.py:290` — `_answer_requirements / generation-review-revision prompt contract` | MEDIUM | E1_E2_COMPATIBILITY | false |
| F1-R09 | BENCHMARK_SHAPED_COMPATIBILITY_LAYER | `src/panda_agent/qa.py:563` — `_requirement_evidence / _compact_requirement_evidence / _deterministic_missing_requirement_ids` | MEDIUM | E1_E2_COMPATIBILITY | false |
| F1-R10 | BESPOKE_SUFFICIENCY_OR_COMPLETENESS | `src/panda_agent/qa.py:785` — `_deterministic_missing_requirement_ids pointer_identifier_normalization` | HIGH | F2_CANDIDATE | false |
| F1-R11 | BENCHMARK_SHAPED_COMPATIBILITY_LAYER | `src/panda_agent/qa.py:1114` — `planned locators / dataflow augmentation / required_boundary_locators` | MEDIUM | E1_E2_COMPATIBILITY | false |
| F1-R12 | BESPOKE_SUFFICIENCY_OR_COMPLETENESS | `src/panda_agent/qa.py:917` — `sufficiency routing / QAAgent._targeted_retrieve` | MEDIUM | E3_BOUNDARY_REVIEW | false |
| F1-R13 | BESPOKE_SUFFICIENCY_OR_COMPLETENESS | `src/panda_agent/qa.py:1482` — `QAAgent._verify deterministically_supported_claims` | HIGH | F2_CANDIDATE | false |
| F1-R14 | BENCHMARK_SHAPED_COMPATIBILITY_LAYER | `src/panda_agent/retrieval.py:1803` — `post-rerank promotion / select_final_evidence` | MEDIUM | E3_BOUNDARY_REVIEW | false |
| F1-R15 | HOLD_UNCERTAIN_PROVENANCE | `src/panda_agent/retrieval.py:1537` — `Retriever._workflow / _graph curated fallback` | MEDIUM | HOLD | false |
| F1-R16 | GENERIC_LEGITIMATE_MECHANISM | `src/panda_agent/qa.py:985` — `_answerability_guard / query-grounded refusal bases` | LOW | KEEP_GENERIC | false |
| F1-R17 | GENERIC_LEGITIMATE_MECHANISM | `src/panda_agent/qa.py:505` — `runtime question objective / citation integrity / internal claim filtering` | LOW | KEEP_GENERIC | false |
| F1-R18 | DOMAIN_KNOWLEDGE_OR_ROUTING | `src/panda_agent/retrieval.py:970` — `deterministic routing / domain scopes / accepted aliases` | LOW | KEEP_DOMAIN | false |
| F1-R19 | DOMAIN_KNOWLEDGE_OR_ROUTING | `src/panda_agent/retrieval.py:1470` — `locked source taxonomy / per-paper diversification` | LOW | KEEP_DOMAIN | false |
| F1-R20 | D4_OWNED_EXCLUDED | `src/panda_agent/retrieval.py:1022` — `D4 expansion consumption and active structured replacement` | LOW | D4_EXCLUDED | false |
| F1-R21 | EVALUATION_ONLY_NON_PRODUCTION | `src/panda_agent/evaluation_runner.py:875` — `_execute_evaluation_case / external Gold judge` | LOW | KEEP_GENERIC | false |

## Residual findings

The entries below include the three explicitly non-counted HOLD candidates so uncertain provenance stays visible.

### F1-R01 — intents.algorithm_theory / algorithm_implementation.required_sources

Intent policy mandates paper for theory and paper plus code for implementation. analyze transfers requirements into the plan; paper retrieval, selection, and QA sufficiency consume them.

Explicit provenance applies to the paper-intent policy, not automatically to every other source requirement or budget. **Disposition:** F2_CANDIDATE. Do not change in F1; Consider question-grounded source obligations in a separately authorized F2 change; preserve safety and assess E3 interaction.

**Evidence:** `src/panda_agent/retrieval.py:1150-1155 explicitly says gold policy requires literature for these two intents`; `src/panda_agent/retrieval.py:1222-1231`; `src/panda_agent/retrieval.py:1470-1488`; `src/panda_agent/qa.py:1090-1110`.

**E1 blocker: false.** E1 can derive question-only facets without adopting intent-to-source mandates.

### F1-R02 — non-paper intent required_sources

Installation requires documentation; usage documentation/code; API code; data_flow workflow/code; module_structure code/graph; troubleshooting documentation/code. These affect production sufficiency.

The mappings are observable; available comments do not establish a Gold origin for each non-paper mapping. Determinism and domain specificity alone are insufficient. **Disposition:** HOLD. Do not change in F1; Retain pending product-contract/provenance review; do not count as substantiated benchmark debt.

**Evidence:** `configs/retrieval_policies.yaml:18-42`; `src/panda_agent/retrieval.py:1228-1229`; `src/panda_agent/qa.py:1107-1110`.

**E1 blocker: false.** Question-only decomposition is separable from these downstream source requirements.

### F1-R03 — Retriever.analyze feedback paper-page override

For algorithm_theory with feed back/feedback/reconstructed restgas profile and an existing li_2026 hint, replace that source's page set with [141,149,151].

Direct code-level answer-location shortcut. Matching page values in D4 do not transfer ownership of this independent code origin; exact originating benchmark case is not established. **Disposition:** F3_CANDIDATE. Do not change in F1; Retain until separately authorized F3 replacement; coordinate overlapping origins with D4 instead of deleting shared page values globally.

**Evidence:** `src/panda_agent/retrieval.py:1146-1149`; `src/panda_agent/retrieval.py:1488-1514,1853-1867`; `evaluation/d4_a0_expansion_component_inventory.json rules[rule_id=reconstructed_profile_to_acceptance]`; `git blame: trigger/page assignment present in initial source commit 3d90848`.

**E1 blocker: false.** Retrieval locator selection is not the E1 question-only decomposition contract.

### F1-R04 — QAAgent._sufficiency / _finalize exact negative control

Exact PndUniversalRestgasDeconvolver branch checks retrieved definitions, refuses, and optionally cites efficiency_correction_2.C; final refusal also asserts the alternative implementation without requiring that replacement evidence.

One coupled negative-control finding covers both refusal and its fixed response locator, avoiding double counting. Generic locked-symbol infrastructure exists, but current generic guard checks qualified APIs, not every bare class. **Disposition:** F2_CANDIDATE. Do not change in F1; Generalize class/premise handling and evidence-grounded refusal together under F2; do not assume the current generic API guard already replaces this branch.

**Evidence:** `src/panda_agent/qa.py:1071-1089 negative-control comment and literal`; `src/panda_agent/qa.py:1819-1849`; `src/panda_agent/qa.py:955-983,1013-1026`.

**E1 blocker: false.** E1 can be implemented independently without copying the dedicated refusal branch.

### F1-R05 — QAAgent._finalize unsupported-API header fallback

Unsupported-API finalization selects an already retrieved class-matching item OR any path ending PndPidCorrelator.h, even without a query/class relationship to that header.

Evidence presence is required and no retrieval is added, but the unconditional exact-header alternative can control the public citation independently of the requested class. Historical case origin is unknown. **Disposition:** F3_CANDIDATE. Do not change in F1; Replace only the fixed fallback when a generic query-grounded refusal-basis selector is established; preserve the generic API guard.

**Evidence:** `src/panda_agent/qa.py:1850-1891`.

**E1 blocker: false.** A final-response citation fallback does not constrain independent E1 design.

### F1-R06 — QAAgent._finalize deleted-runtime fallback

Generic deleted-runtime refusal selects retrieved macro/target/ana_dpm.C and hard-codes event_poca in response wording, although the guard also matches other runtime artifacts.

Separate generic impossibility guard from the fixed presentation/citation shortcut; public event_poca wording is not conditional on a query-specific match or replacement evidence. **Disposition:** F3_CANDIDATE. Do not change in F1; Retain the generic refusal; separately review the code-level locator and wording under F3 with F2 coordination.

**Evidence:** `src/panda_agent/qa.py:1027-1033`; `src/panda_agent/qa.py:1892-1922`.

**E1 blocker: false.** E1 need not inherit the refusal template.

### F1-R07 — QAAgent._sufficiency exact_memory_question

Exact/minimum plus gpu/memory/ram triggers a resource-specific refusal unless an evidence-text proximity regex matches; it does not validate an actual numeric value or unit.

Generic exact-numeric evidence caution is legitimate. This implementation is narrower, but available static history does not prove benchmark derivation; no runtime defect is repaired or empirically asserted. **Disposition:** HOLD. Do not change in F1; Retain on HOLD for numeric-sufficiency provenance/contract review; do not label it a proven benchmark-specific rule.

**Evidence:** `src/panda_agent/qa.py:1053-1070`; `src/panda_agent/prompts.py:80-84`; `git blame -L 1053,1075: present in initial source commit 3d90848; no earlier local provenance`.

**E1 blocker: false.** E1 can express requested exact numeric facets without using this guard.

### F1-R08 — _answer_requirements / generation-review-revision prompt contract

Live question and plan activate workflow, handoff, factory, acceptance, reader, theory-fit, module and troubleshooting obligations used during generation/review/revision.

Regression-shaped obligations use actual question/plan and require evidence-backed answers; there is no runtime Gold answer-point input. Treat as compatibility, not immediate F2 deletion. Pointer-specific enforcement is separately R10. **Disposition:** E1_E2_COMPATIBILITY. Do not change in F1; Retain during diagnostic E1 work; map migration to dynamic decomposition and claim/point coverage in E1/E2.

**Evidence:** `src/panda_agent/qa.py:290-482,1271-1297,1584-1609,1677-1705`; `src/panda_agent/prompts.py:46-200`; `tests/unit/test_qa.py:452-505,847-891,1228-1238`.

**E1 blocker: false.** E1 question-only output can run alongside these legacy obligations with separate provenance.

### F1-R09 — _requirement_evidence / _compact_requirement_evidence / _deterministic_missing_requirement_ids

Selects existing evidence by named requirement, truncates around domain anchors, and checks required claim vocabulary and, for selected requirements, cited-evidence links. Missing requirements drive one revision and may coexist with salvaged supported claims.

Named domain checks are bespoke but currently support completeness over live evidence. Not every check itself verifies entailment; ordinary citation/review checks remain separate. Excludes R10 pointer literal. **Disposition:** E1_E2_COMPATIBILITY. Do not change in F1; Retain and assess coverage equivalence in E1/E2; do not translate keyword checks into new Gold-shaped decomposition points.

**Evidence:** `src/panda_agent/qa.py:563-784,796-860,1605-1664,1736-1743,1933-1962`; `tests/unit/test_qa.py:612-670,948-1060`.

**E1 blocker: false.** E1 can remain question-only and diagnostic; eventual replacement of enforcement belongs to E2.

### F1-R10 — _deterministic_missing_requirement_ids pointer_identifier_normalization

A generic pointer-normalization request activates a check that specifically requires pndlmdtrackq and underlying/pointer-syntax wording; evidence compaction also uses PndLmdTrackQ anchors.

Regression-protected exact-symbol enforcement is stronger than the generic live-query trigger. Distinct narrow specialization within R08/R09, not evidence that all completeness obligations should be removed. **Disposition:** F2_CANDIDATE. Do not change in F1; Review genericization of the hard-coded symbol under F2 in coordination with E1/E2; preserve existing behavior in F1.

**Evidence:** `src/panda_agent/qa.py:409-417,614-618,675-677,785-795`; `tests/unit/test_qa.py:847-910 test_regression_protected_requirements_reject_incomplete_claims`.

**E1 blocker: false.** E1 is not blocked if it derives facets from the question and does not reuse this hard-coded completion predicate.

### F1-R11 — planned locators / dataflow augmentation / required_boundary_locators

Planned-locator augmentation requires a query-named planned identifier and selected evidence; dataflow augmentation uses planned symbols/required types and actual evidence. Module-boundary prompts treat plan symbols as required components.

No new fixed answer path is encoded by the helpers. Plan may contain D4-derived symbols; internal required_* and dataflow_locator_* claims are filtered from public answers. required_boundary_locators can still shape generated content. **Disposition:** E1_E2_COMPATIBILITY. Do not change in F1; Retain compatibility; E1/E2 should distinguish question requirements from upstream plan suggestions before replacing it.

**Evidence:** `src/panda_agent/qa.py:1114-1269,1287-1295,1304-1305`; `src/panda_agent/prompts.py:112-115`; `src/panda_agent/qa.py:485-526,1385-1393`; `tests/unit/test_qa.py:1508-1518`.

**E1 blocker: false.** E1 can derive requirements without plan symbols or retrieved evidence and be observed separately.

### F1-R12 — sufficiency routing / QAAgent._targeted_retrieve

Insufficiency triggers one retry except version conflicts; query suffix includes required source types and error text, missing-symbol errors extend the reused plan, and evidence merges with a fixed 12-item truncation.

Mechanism follows sufficiency errors, not missing decomposed answer points, and generic refusals can also enter it. Static architectural mismatch is clear; exact benchmark origin is not. **Disposition:** E3_BOUNDARY_REVIEW. Do not change in F1; Review before E3 becomes authoritative, preserving C8/global-merge boundary; do not execute targeted retrieval in F1.

**Evidence:** `src/panda_agent/qa.py:917-953`; `configs/retrieval_policies.yaml:5`; `src/panda_agent/retrieval.py:1634-1640`.

**E1 blocker: false.** E1 decomposition can be implemented independently of targeted retrieval activation.

### F1-R13 — QAAgent._verify deterministically_supported_claims

Identifier/path matches, code-source membership and comparison wording can mark whole claims deterministically supported; such claims skip semantic unsupported-claim errors. Explicit token whitelist includes createLmdFitData, fillData and other names.

Observed bespoke support override, not ordinary citation-integrity checking: matching identifiers is not semantic entailment. Exact historical benchmark derivation is unproven; static policy risk is sufficient for a bounded guard candidate, not a measured regression claim. **Disposition:** F2_CANDIDATE. Do not change in F1; Review support-override generalization under F2 and the later verifier-role boundary; preserve citation/version checks.

**Evidence:** `src/panda_agent/qa.py:1482-1543,1611-1618`; `src/panda_agent/qa.py:1500-1505`.

**E1 blocker: false.** Downstream claim verification can be kept unchanged during an independently observable E1 implementation.

### F1-R14 — post-rerank promotion / select_final_evidence

Plan hints, required types and exact symbols are promoted before reranker order; mandatory symbols can bypass caps; two-pass backfill admits required types only into unused capacity.

Current accepted selector is production-authoritative and works on runtime candidates. This row covers the generic selection policy, not D4 locator values or a new review of C7 scientific results. **Disposition:** E3_BOUNDARY_REVIEW. Do not change in F1; Retain current selector; reconcile coverage and merge semantics before E3, without reopening C7 or tuning weights in F1.

**Evidence:** `src/panda_agent/retrieval.py:678-784,1803-1877`; `docs/GENERALIZATION_ROADMAP.md Phase B/B5 and C7 deferred coverage/ranking outcome`.

**E1 blocker: false.** Selection debt does not prevent question-only E1 design.

### F1-R15 — Retriever._workflow / _graph curated fallback

When required workflow lacks a workflow object, or required graph has no edges, fallback selects bounded curated objects by object_id without question-term/seed relevance conditions.

Potential source-coverage accommodation is observable, but sparse-corpus fallback may be legitimate. Historical origin and usefulness are not established by static evidence; not classified as a fixed exact-object shortcut. **Disposition:** HOLD. Do not change in F1; Retain on HOLD for relevance/ownership review at retrieval/E3 boundary; do not count as proven benchmark debt.

**Evidence:** `src/panda_agent/retrieval.py:1537-1550,1587-1598`.

**E1 blocker: false.** E1 can operate solely on user text; fallback relevance is downstream.

## D4 exclusions

R20 is one aggregate D4_OWNED_EXCLUDED entry, not a new 54-rule inventory. D4 retains ownership of expansion contributions and active structured migrations; its confirmed ModelFactory HOLDs do not represent the entire residual D4 scope.

The code-level feedback override R03 is RELATED_BUT_OUTSIDE_D4. D4-A0's `reconstructed_profile_to_acceptance` also contains `li_2026 [141,149,151]`, but the independent `Retriever.analyze` assignment is outside that rule inventory. R03 additionally requires an existing li_2026 hint. Shared values are not interchangeable provenance origins. No page or rule removal is proposed for execution.

D4-A10's rule-local ModelFactory retirement and independent-origin preservation remain unchanged. No D4-A11 is created or authorized.

## Generic/domain mechanisms retained

R16 retains generic qualified-API validation, future-runtime and formal-proof boundaries, and query-grounded refusal bases. A catalog lookup for `Class::method` is a useful F2 foundation but is not already a generic replacement for the exact bare-class branch R04.

R17 retains runtime question objectives, citation/version/locator integrity, internal-claim filtering and supported-claim rendering. These are distinct from the semantic-support overrides in R13. Scope claims containing a fixed Sphinx snapshot date are internal audit material, filtered before public output; no public fixed-date dependency is inferred from construction alone.

R18/R19 retain accepted aliases, terminology, corpus/source identity and domain routing. Alias provenance is recorded in configuration; this task did not revalidate corpus contents or live alias-table materialization. Deterministic/domain-specific does not mean benchmark-specific.

R21 excludes Gold/judge metrics: `_execute_evaluation_case` passes only `case.query` to production QA, then applies deterministic metrics and optional external judging to the returned result. Shared storage of judge prompts in prompts.py does not make that prompt production-reachable.

## Answer-completeness compatibility assessment

R08/R09/R11 are retained for E1/E2. Requirements are generated from the live question and plan; evidence subsets come from the actual bundle. The runtime objective currently contains one `question_core` point. There is no runtime read of Gold required-answer-points in the inspected call graph.

This does not make every predicate generic or correct: R10's hard-coded pointer symbol and R13's support overrides are separately inventoried. Several completeness checks use vocabulary rather than proving entailment, and finalization can salvage supported claims despite missing requirements. No claim of complete answer coverage is made.

E1 should remain question-only and independently observable under its existing diagnostic plan. Plan-derived symbols, source requirements, and compatibility obligations must not become decomposition ground truth. Retain existing production behavior until a separately authorized E1/E2 migration establishes its replacement.

## Phase-E blocking assessment

Every candidate records `e1_blocking=false` with an individual rationale. No observed dependency forces question-only dynamic decomposition to read Gold, infer requirements from retrieved evidence, or reuse a hard-coded completeness predicate.

E1 integration work will eventually touch the single-runtime-point interface, but that is not a benchmark-derived blocker. E2 enforcement and E3 targeted recovery have separate unresolved boundaries. Zero E1 blockers is a bounded static finding, not an implementation result or permission to run E1.

## Phase-F ownership implications

- F2 candidates: R01, R04, R10, R13. Refine source mandates, exact negative-control behavior, symbol-specific completion enforcement, and bespoke support overrides only under separate authorization.
- F3 candidates: R03, R05, R06. These are code-level answer-location/presentation shortcuts outside D4; conditional evidence presence does not remove the fixed-locator dependency.
- E1/E2 compatibility: R08, R09, R11. Preserve until generic decomposition and claim/point coverage replace their role.
- E3 boundary review: R12, R14. Existing sufficiency-driven targeting and current selector remain unchanged.
- HOLD: R02, R07, R15. Provenance uncertainty does not authorize removal or establish benchmark ancestry.

F1 establishes non-D4 residual scope; it does not reconcile every original D4 item or finish F3 design. Phase F becomes IN_PROGRESS / F1_COMPLETE; F2 is NOT_STARTED and F3 remains SCOPE_RECONCILIATION_REQUIRED / PARTIALLY_SUPERSEDED_BY_D4.

## Verification performed

T0/static only:

- `git status --short`, `git rev-parse HEAD`, `git log -5 --oneline`: independent starting identity and cleanliness.
- Targeted `rg -n`, `Get-Content` slices, `ConvertFrom-Json`, `git log -1 --format=... -S ... -- <source>`, and `git blame -L ... -- <source>`: call graph, taxonomy, ownership and provenance inspection.
- A targeted `git show 2511d69:docs/EVALUATION_STATUS.md` keyword search supplied historical documentation context only; no dataset or raw case outcome read.
- Python standard-library JSON parsing and in-memory assertions: unique IDs, exact taxonomies, reachability/provenance values, source locations, residual/exclusion separation, counts, report-table agreement, E1 blocker count, verdict and next-task agreement.
- `git diff --check`, `git status --short`, `git diff --stat`, and the four-path diff: formatting and authorized change scope.
- Protected source/config/test paths compared to the starting HEAD; unique current-authority/planning headings and lifecycle states checked.
- One normal commit; post-commit path/parent/cleanliness checks. No project test suite, evaluator, reusable verifier, hash inventory or freeze manifest.

The JSON verification block records the actual check outcome. These static checks do not establish runtime quality or safe removal.

## Cost accounting

| Counter | Value |
|---|---:|
| Analyzer calls | 0 |
| Embedding calls | 0 |
| Reranker calls | 0 |
| QA calls | 0 |
| Runtime evidence-review calls | 0 |
| Revision calls | 0 |
| Judge calls | 0 |
| Total model calls | 0 |
| Token usage | 0 |

These are F1 execution costs. No AGY or other external worker was invoked for this task. Before/after scientific metrics are not applicable because behavior was unchanged and no science ran.

## Limitations

- Bounded inspection of the default production call graph, not exhaustive repository/corpus or database inspection.
- No empirical trigger frequency, quality impact, replacement efficacy or retirement safety measured.
- Three local HOLDs remain. Some fixed-locator/bespoke findings establish structural dependence without proving exact benchmark ancestry.
- Initial-import history limits older provenance. Current accepted selector policy is preserved, not independently re-evaluated.
- Protected splits and novel-dev content remain untouched; D4 completion and broader residual inventory remain undecided.

## Closeout decision

PASS

F1 = COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED.
D4 = PAUSED / ROADMAP_RECONCILIATION; overall completion UNDECIDED.
D4-A10 remains the latest accepted production action.
Phase F = IN_PROGRESS / F1_COMPLETE.
Phase E = NOT_STARTED.
F2 = NOT_STARTED / SCOPE_PRESERVED.
F3 = SCOPE_RECONCILIATION_REQUIRED / PARTIALLY_SUPERSEDED_BY_D4.

No production cleanup occurred. F1 PASS is inventory acceptance only.

## Next task recommendation

NEXT TASK RECOMMENDATION = E1 — Dynamic Question Decomposition.
NEXT TASK EXECUTION AUTHORIZED = false.

Stop after F1. Do not execute E1, F2, F3, a further D4 task, or any evaluation.
