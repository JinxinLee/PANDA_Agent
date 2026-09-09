# E2-A3-FR1 — Q7 Failure Review and Repair Decision

## Decision

**REPAIR_JUSTIFIED. Review verification: PASS.** Primary ownership is
**V1 — verification false rejection**. Specific failure class:
`ACTIVATION_VERIFIER_IDENTIFIER_NORMALIZATION_REGRESSION`.
The historical E2-A3 result remains **COMPLETE / FAIL / Q7** and its historical
`ACTIVATION_CITATION_REGRESSION` classification is not rewritten.

Starting HEAD was `e503dba67b7ed6b7dab6edd89b4158471b93fb54`, with a clean tree
and the expected ten-commit history. Current policy, roadmap, status, QA code,
A3 preregistration, manifest, report, raw outputs, judgments, result, and runner
were inspected. This is an offline review, not implementation or revalidation.
Review commit is the normal Git commit containing this report and its companion
`e2_a3_q7_failure_review.json`; no new candidate or activation commit exists.

## Frozen failure reconstruction

Evidence source: committed raw artifact at
`8ba275addf44a5c7e96bf83a292c6737fbe07b38`, record
`g112.runtime_e1_v2`. The companion JSON records the complete question, legacy
initial/final claims, runtime initial claims, revised claim, review states,
final public answer, cited-evidence provenance, and token comparison.

Question: "createLmdFitData returns no acceptance: which data mode, Lumi_TrksQA
input/tree assumptions, selection filters, and accepted/generated histogram
filling should I inspect?"

Legacy initial claim_3 begins "Selection filters and secondary rejection: in
PndLmdDataReader::fillData, verify that tracks satisfy ...". Its comma is outside
the tokenizer character class. Legacy had no review errors or revision; its
four initial claims cover mode/input, tree/branch schema, selection, and
accepted/generated filling. Initial and final claim text is retained in JSON.

Runtime initial claim_3 is:

> Inspect track selection filters in PndLmdDataReader::fillData: tracks are immediately skipped from registered acceptances if track_info.IsSecondary is true (evaluated from track->GetSecondary() >= 0), and tracks are rejected if getTrackParameterValue fails dimension_range.isDataWithinRange for any selection dimension in data->getSelectorSet().

It cites `evidence.2912806314dc84af87470e1b` and
`evidence.9b11380bf90f5bf9e8f0e312`. The latter is the frozen luminosityfit
`data/PndLmdDataReader.cxx` excerpt, locator lines 1–444, and contains:

```cpp
void PndLmdDataReader::fillData(const Lmd::Data::TrackPairInfo &track_info) {
```

Thus the base identifier is explicitly supported in the very evidence cited
by the failing claim. No global catalog, new source retrieval, or assumption
about API existence is necessary. The other cited excerpt is
`data/PndLmdCombinedDataReader.cxx`, locator lines 1–85.

First review errors, exactly:

```text
unsupported identifier PndLmdDataReader::fillData:
missing answer point point.3
missing answer requirement reader_selection_histogram_accounting
```

The deterministic error excludes claim_3 from `reviewable_claims` in runtime
mode. Its declared point.3 receives no verified mapping; the frozen semantic
review therefore receives no eligible selection-filter claim. This establishes
the upstream verifier exclusion, not an independent decomposition defect.
The first audit is evaluable, incomplete, and missing point.3.

The revision input is reconstructed from the first review and `_revise` prompt
builder: unsupported draft = claim_3; already supported = claims 1, 2, 4;
missing point = point.3; missing requirement =
reader_selection_histogram_accounting; verification errors = the three above;
question, four runtime points, requirements, and selected evidence remain the
same. Raw records contain responses, not request-prompt bytes, so this is a
source-grounded reconstruction, not a claimed byte-exact captured request.

Revised claim_3 begins "Inspect the selection filters in PndLmdDataReader:",
then describes secondary rejection and successfullyPassedFilters with the same
two evidence IDs. Final review has no unsupported-identifier error, covers all
four points, and is evaluable/complete. Remaining errors are
`missing answer requirement troubleshoot_upstream_to_downstream` and
`missing answer requirement explicit_compatibility_check`. The final public
answer is answered and contains claims 1, 2, 4, 3. The full text is in JSON.
Frozen judging preferred runtime, without a critical regression. Neither final
recovery nor judge preference waives the preregistered all-reviews Q7 rule.

## Exact deterministic ownership and counterfactual

`src/panda_agent/qa.py` `_verify`, lines 1675–1682 at starting HEAD, extracts
`re.findall(r"[A-Za-z_][A-Za-z0-9_:./-]+", claim_text)`, deduplicates with `set`,
and applies only `token.rstrip(".")`. It checks scoped/path tokens using
substring membership in `cited`, built from each cited evidence's text, path,
symbol, URL, and section path. This is not an exact identifier-set lookup.
The companion JSON includes the scoped-token projection of that cited universe.

| Comparison | Current | Counterfactual |
| --- | --- | --- |
| Raw token | `PndLmdDataReader::fillData:` | Same |
| Normalized token | `PndLmdDataReader::fillData:` | `PndLmdDataReader::fillData` |
| In claim-specific cited text | No | Yes, explicit function definition |
| Unsupported-identifier loop errors | One | Zero |

The offline check extracts the actual unsupported-identifier `for` loop from
the current source AST and executes it against frozen claim/cited text. An
in-memory copy inserts single-colon removal immediately after the existing
period normalization. No QA graph, model-backed review, answer generation, or
product code mutation is executed. Assertions confirm the exact original error
and its removal in the counterfactual. This changes token comparison only;
it does not predict a new semantic review, revision decision, or final answer.

Other `_verify` logic at lines 1578–1589 uses a similar normalization for
deterministic positive support anchors, with a different eligibility predicate
(including bare Pnd names). Later explicit-code support heuristics use raw
tokens. **Do not extend this repair to those acceptance heuristics.** A shared
helper, if introduced, should initially replace only the rejecting loop's local
normalization; broad caller migration would require a new impact assessment.

## Complete frozen impact scan

All 56 execution records were scanned recursively: 299 serialized claim-text
objects, representing 157 distinct per-execution claim snapshots (legacy 81,
runtime 76). Identity is claim ID + exact text + ordered evidence IDs within
one execution. Answer/revision responses and final-public copies are deduplicated;
different revised text remains a separate snapshot. Recursive inspection found
no additional claim objects outside those projections. Counts below count token
occurrences before the verifier's per-claim set deduplication.

| Surface | Token occurrences | Claim snapshots | Legacy / runtime tokens |
| --- | --- | --- | --- |
| Single terminal colon, all prose tokens | 41 | 36 | 25 / 16 |
| Terminal double colon | 0 | 0 | 0 / 0 |
| Terminal period | 140 | 140 | 74 / 66 |
| Changed scoped/path tokens | 1 | 1 | 0 / 1 |
| Changed rejection outcome | 1 | 1 | 0 / 1 |

All-prose colon cases: g013, g059, g105, g110, g112, e1a2.b07,
e1a2.b08, e1a2.b10, e1a2.p07, e1a2.p08, e1a2.p10, e1a2.p12.
The sole rejection delta is g112 runtime initial claim_3. The other 40 colon
tokens are not scoped/path rejection candidates before or after normalization;
they include ordinary prose labels and unscoped names. Existing period handling
is unchanged. No other observed token form changes under this rule.

Valid identifier semantics changed: **0 observed**. Currently rejected tokens
newly passing the identifier check: **1**, the demonstrated supported base
identifier. Genuinely unsupported base identifiers newly accepted: **0**.
Previously accepted token checks newly rejected: **0**. These are identifier
checks, not assertions that complete claims become semantically accepted.

Existing unsupported tokens remain rejected: g110 legacy `prefix_pid.root`
and `prefix_boost.root`; g002 both arms `SIMPATH/bin/cmake`. These are retained
as negative controls, not repaired or granted new support. The scan reveals no
broad final-claim or multiple-case revision-trigger delta. The actual future
g112 revision outcome is unknown until prospective execution.

## Minimum future repair contract

Owner: deterministic rejecting identifier-token normalization in `qa.py` only.
One small helper or equivalent local logic; no production default change.
First retain existing removal of trailing periods, then remove exactly one
terminal colon only when the resulting token does not end in `::`. Continue
the existing scoped/path predicate and cited-evidence membership checks.
Do not normalize evidence text or change source selection or matching policy.
The rule interprets a terminal single colon as prose punctuation in claim text;
it is not a filesystem renaming or universal C++ parser rule.

Required future unit matrix:

| Input | Expected token |
| --- | --- |
| `PndLmdDataReader::fillData` | unchanged |
| `PndLmdDataReader::fillData.` | `PndLmdDataReader::fillData` |
| `PndLmdDataReader::fillData:` | `PndLmdDataReader::fillData` |
| `Namespace::Class` | unchanged |
| `Namespace::` | unchanged |
| `std::vector` | unchanged |
| `src/foo.C` | unchanged |
| `C:/path/to/file` | unchanged |
| `Namespace::.` | `Namespace::` |
| `Class::method:.` | `Class::method` |

Include a generic supported `Class::method:` check and an unsupported
`Other::method:` check that still rejects, plus the frozen g112 static sentinel
and the three existing negative tokens above. Keep terminal `:::` unchanged;
do not introduce odd-colon repair or broad punctuation stripping. Do not promise
iterative handling of `Class::method.:`; the defined one-pass rule leaves a
period. Those unobserved compound forms do not justify extending this repair.
Internal scope separators, slash paths, and file extensions remain intact.

Prohibited: g112/case-ID behavioral branches; PndLmdDataReader/fillData allowlists;
prompt, E1, E2 mapping, retrieval, Gold, schema, mode, positive-support heuristic,
or compatibility-rule changes. Fixture strings may document the regression;
they must never become product triggers. This review implements none of it.

## Minimum scientifically valid future revalidation

**Full A3 repetition is not required for the reviewed scope.** Recommended
future sequence, subject to separate authorization:

1. Implement the narrow repair; run T0 token tests, frozen g112 check, complete
   frozen A3 counterfactual scan, and directly affected QA/verifier tests.
   Require the same single explained rejection delta, unchanged negative
   controls, preserved public/default/compatibility boundaries. Use existing
   pair09 offline integration tests; no new live pair09 cases are necessary
   when its semantic paths are unchanged.
2. Freeze a **new** candidate and a five-case targeted paired protocol:
   g112 original false-rejection sentinel; g110 and g002 prior unsupported-token
   controls; g044 and g027 clean Gold identifier/citation sentinels (both arms
   had empty review errors). These IDs are verified from frozen A3 evidence.
3. Run fresh legacy/runtime QA on those five questions, 10 executions, under
   the same repaired candidate, with balanced order. Do not compare a repaired
   runtime run against a reused historical legacy output. Freeze all outputs
   before five separate-role blinded paired judgments; freeze judgments before
   interpreting labels. No new retrieval-only bootstrap is needed because
   retrieval is unchanged; each QA execution still includes its own retrieval.
4. Predefine zero new critical integrity categories over all reviews, no new
   false status transitions or critical user-visible regressions, and no worse
   paired outputs for this small sentinel cohort. Require one decomposition
   per runtime case, zero per legacy case, at most one revision, zero postverify
   retrieval, and the original mean additional-call limit. A missing or malformed
   execution/judgment is INCONCLUSIVE, never an implicit pass. Do not require a
   stochastic g112 output to reproduce the punctuation: T0 proves the mechanism.
5. Record a new targeted repair verdict. Any activation requires an explicitly
   authorized conditional decision that accepts this bounded evidence scope.
   Historical A3 stays FAIL; neither offline analysis nor five cases establishes
   that the old candidate passed or that all A3 gates were freshly rerun.

Five pairs test integration and negative controls, not statistical generalization.
Historical A3's other gates are context and retained evidence, not newly measured
scores for the repaired candidate. Fresh repair scope beyond this local loop,
unexpected multiple-case acceptance/revision effects, altered valid syntax,
prompt/schema/runtime changes, or an unbounded impact scan require reassessing
the design and potentially full A3 revalidation. Do not expand retrospectively
after observing prospective outcomes.

## Independent review, usage, and limitations

AGY job `staffer-mtua77he-6e69ccc0` completed an abstract review without repository
access or edits. Configured route: gemini-3.8-flash-high; its response self-reports
Gemini 3.8 Flash / High, not independently observed runtime metadata. Tokens are
unavailable. Its cautions about preserving terminal scope, duplicate counting,
and weak statistical power of small cohorts are incorporated. Its proposed
odd-colon repair, exhaustive grammar proof, and production shadow monitoring
are not adopted: they exceed the observed defect or this task's scope. Its
index-symmetry concern does not describe the actual substring-in-cited-text check.

Scientific decomposition, analyzer, embedding, reranker, retrieval, QA answer,
QA review, QA revision, judge calls: **all 0**. Scientific tokens: **0**.
The one optional AGY orchestration call is separate; total external calls are
not claimed to be zero. No live science, QA rerun, historical rescore, protected
dataset access, repair implementation, or activation occurred.

The analysis establishes token-level causality and a bounded frozen impact,
not a counterfactual semantic judgment or guaranteed future revision/final answer.
Malformed token grammar and substring-match policy are pre-existing boundaries
outside this repair. Review artifacts and lifecycle documentation are the only
changes. Frozen scientific artifacts and product code remain unchanged.

Focused offline checks passed: 12 explicit normalization sentinels, two generic
supported/unsupported scoped-token checks using the source-derived loop, exact
g112 before/after assertions, and complete frozen impact assertions. Git checks
confirmed unchanged src/config/tests, default selector, and historical A3
protocol/manifest/runner/raw/judged/result/report files. `git diff --check`
passed. No broader test suite was necessary for documentation-only delivery.

```text
E2-A3 = COMPLETE / FAIL / Q7
E2-A3 FAILURE REVIEW = COMPLETE / PASS / Q7_VERIFIER_IDENTIFIER_NORMALIZATION_REPAIR_JUSTIFIED
E2 = IN_PROGRESS / RUNTIME_ACTIVATION_FAILED / BOUNDED_VERIFIER_REPAIR_PENDING
normal default = legacy_question_core
Phase E = IN_PROGRESS / E2
E3 = NOT_STARTED
NEXT_TASK_RECOMMENDATION = E2-A3-R1 — Deterministic Identifier Normalization Repair
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
