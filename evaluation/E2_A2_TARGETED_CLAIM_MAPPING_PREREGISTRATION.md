# E2-A2 — Targeted Claim-Mapping and Missing-Point Validation

Status: PREREGISTERED_EXECUTION_PENDING. Targeted exposed-development T2-style
validation, not protected validation, representative generalization, release,
production activation, or E3. The user authorizes the complete bounded lifecycle
without another approval or budget checkpoint. Stop after E2-A2 closeout.

## Frozen subject and source

Implementation: df52bcddf612515418be298fafde6ebcb32d4a67.
QA prompt version 3.8.0; E1 prompt 2.0.0/schema e1.question_decomposition.v2.
No src/config changes are permitted. Normal QA retains question_core and never
calls decomposition. The explicit E2 diagnostic invokes the existing graph.

Historical source: 77ea6bc27beb1657673e57be763b05419c98bc05,
evaluation/e1_a2_dynamic_question_decomposition_validation_manifest.json.
Select pair07 through pair12 only: n001,n008,n020,n022,n030,n031, both base and
paraphrase, source_group/source_split novel_dev, English. Twelve questions,
six pairs, 28 frozen reference obligations; base counts 3,2,3,2,2,2.
The self-contained manifest is mechanically extracted and equality-checked
against Git source; references, slots, questions, and ordering are not authored
or revised here. No protected dataset is opened.

Two fresh executions per question: rep1 in manifest order, then rep2 in that
same order. These are 24 execution instances of 12 exposed correlated questions,
not 24 independent questions. No reuse of rep1 scientific outputs in rep2.
Only raw question enters the product. Capture subclass delegates every product
node unchanged and records final state/reviews; the adapter meter delegates
unchanged calls and records usage. Existing pre-answer targeted retrieval may
occur naturally; no evaluation-specific retrieval or QA retries are added.

## Provider identity and monitoring

Vertex project gen-lang-client-0694751367; generation and separate evaluation-role
judge gemini-3.8-flash; location global; temperature 0. Embedding gemini-embedding-2,
3072 dimensions; timeout 120000 ms. Exact settings are in the manifest and checked
before every stage. Same model family is used: role/input independence is not
model-family independence. Existing adapter transport behavior is unchanged.
No health probe or scientific/provider call precedes preregistration commit.

Per-stage accounting distinguishes logical operations, adapter attempt counters,
returned responses observed at _record_usage, and returned token totals.
Embedding is reported separately; provider billing/HTTP/retry totals are not
inferred from logical counts. Operational output prints only completed/expected
counts and infrastructure status. Raw outcomes are persisted, not interpreted
or tuned during execution.

## Independent semantic truth and applicability

After all 24 raw attempts are committed, judge each frozen attempt once with only
question, reference slot ID/text, runtime point ID/text, and final supported
rendered user claim ID/text. An allowlist excludes product mapping, coverage,
reasoning, taxonomy, spans, evidence, source grouping and pair IDs. The judge does
not redo evidence verification. Exact prompt/schema are frozen in the runner.
It returns one-to-one runtime/reference alignment and exact unmatched sets,
one mapping record per supplied claim (possibly empty), and collective covered/
missing runtime point sets. Mapping alone does not establish completeness.
Malformed judge structure is infrastructure failure, without rejudging.

E1 conformance requires all references matched, no extra runtime point and
one-to-one alignment. Otherwise UPSTREAM_E1_INPUT_INVALID. N2-N6 applicability
requires E1 conformance, coverage_evaluable=true and at least one final supported
rendered user claim. Record refusal/unevaluable status and actual errors.
Coverage-review structural invalidity at either natural review or controlled
review is a product failure and forces FAIL, never hidden by applicability loss.
Provider/execution or judge errors are separately recorded; incomplete
independent authoritative scoring yields INCONCLUSIVE unless a zero-tolerance
product failure already establishes FAIL.

## Frozen metrics

N1: rep1 >=10/12, rep2 >=10/12, pooled >=20/24 applicable.
For applicable final supported rendered claims compare verified E2 edges with
independent truth, using sets of (claim_id,answer_point_id):
N2 micro edge precision >=.90; N3 micro edge recall >=.90;
N4 exact complete mapping-set accuracy per claim >=.85;
N5 micro covered-point precision >=.95; N6 micro covered-point recall >=.90.
Report numerators/denominators, per-repetition/source/pair metrics, exact coverage
agreement, false covered/missing, upstream failures, refusal and structural counts.
Literal point ID equality across executions is not a semantic stability metric.
Repetition disagreement is reported through per-question metric and applicability
comparisons, not a post-hoc gate.

## Controlled derivation and execution

Freeze independent natural judgments before derivation. Consider rep1 only.
Eligibility: applicable, independently complete baseline, at least two runtime
points. Traverse runtime question-order points backward. Select the last with
nonempty independent-judge mapped support where every supporting claim maps
exactly to that point. Multi-point support disqualifies that candidate. No
fallback, manual choice or target based on E2 mappings is allowed.
Remove ALL singleton-mapped target claims; expected missing set is {target}.
Ineligible reasons: BASELINE_NOT_APPLICABLE, BASELINE_NOT_COMPLETE,
LESS_THAN_TWO_POINTS, NO_ISOLATABLE_DROP_TARGET.

Freeze a complete manifest of all 12 eligibility decisions, independent truth,
points, removed/retained IDs and expected missing sets before controlled calls.
Retain original question, points, non-target claim text/ID/evidence/declared
mapping and frozen evidence. Preserve unresolved deterministic-locator origin.
Call actual QAAgent._verify once, using frozen final bundle/legacy requirements
and captured identifier catalog. Do not invoke the graph or retriever constructor.
ForbiddenRetriever and controlled Meter guards reject all other stages. Do not
send target, removed role, independent truth or expected set to product review.
Evidence remains unchanged by design; coverage is satisfaction by retained claims.

D1 >=8 eligible variants. D2 target detection recall >=.90; D3 micro missing-set
precision >=.90; D4 exact missing-set accuracy >=.80. Report missed targets,
collateral missing points, empty/all-missing behavior and structural failures.
Zero denominators are null/undefined and never a perfect score; a required
undefined quality metric cannot PASS. No eligible controlled variants means D1
insufficient, not a fabricated scientific zero-quality measurement.

## Verdict and invariants

PASS requires N1-N6 and D1-D4, complete scoring, and all invariants. FAIL applies
to sufficiently applicable/scoreable product-quality gate failures or a product
invariant/coverage structural failure. INCONCLUSIVE applies to insufficient N1
or D1, incomplete authoritative judging or execution infrastructure failure.
Do not repair the evaluated subject or frozen evaluator after live execution.

Zero tolerance: protected data access; accepted unknown point IDs; credited
internal claims; any controlled decomposition/analyzer/embedding/reranker/
retrieval/answer/revision; normal production activation; post-outcome cohort,
threshold, prompt, model, judge or target tuning. Runtime checks and Git boundary
checks enforce relevant invariants; no hashes or reindex are performed.

## Provenance and recovery

Commit sequence: preregistration -> natural raw -> natural judgments ->
controlled manifest -> closeout. Downstream stages require committed upstream
artifacts and unchanged src/config/protocol/manifest/runner/tests. Never amend
an upstream scientific freeze after downstream evidence exists.
Each execution ID is persisted STARTED before invoking providers, then COMPLETE
with output or error. Completed records are never repeated. An interrupted
STARTED record is ambiguous and must not replay; preserve it and close
INCONCLUSIVE if authoritative completion cannot be recovered. No task retries,
model switch, selective rejudging or failed-case substitution.

Static tests cover selector equality, blinding, applicability, independent judge
validation, hand-computed N/D metrics, controlled selection/removal, guards,
structural failure precedence and resume. E2-A1 focused tests cover the shared
review seam. No full suite. Closeout reconciles all artifact identities, recomputes
results deterministically, checks Git boundaries, and updates lifecycle only.

AGY staffer-mtt5zej2-67468860 completed an abstract pre-freeze design review.
Routing gemini-3.8-flash-high; actual model/effort and tokens unobserved. No repo
access or edits. Recommendations to hash IDs, add isolation fallbacks or retry
judges were rejected because they conflict with the authorized frozen design.
Blinding, nonempty isolation, explicit undefined denominators and failure
classification are covered by host tests. AGY usage is separate and unknown,
not zero scientific usage.

## Closeout lifecycle

Preserve E1 history and E2-A1 PASS. E2 remains IN_PROGRESS, Phase E IN_PROGRESS/E2,
E3 NOT_STARTED; D4 PAUSED/UNDECIDED and F1/Phase F unchanged.
PASS recommends E2-A3 bounded activation/regression review, unauthorized.
FAIL recommends E2-A2 failure review/repair decision, unauthorized.
INCONCLUSIVE recommends only minimal scientifically valid frozen-protocol
recovery, unauthorized. No product activation or later task is executed.
