# E1-C1 — Real PANDA-Style Exposed-Development Confirmation

COMPLETE / PASS / REAL_PANDA_STYLE_EXPOSED_DEVELOPMENT_CONFIRMATION_PASSED.
All eight strict gates and the required pair09 sentinel passed. Per the authorized
closure decision, E1 closes directly; E2 remains NOT_STARTED.

## Provenance

- Starting HEAD: `781007c810b113537025dbe93c28728a59e318bc`; initially clean.
- Source manifest commit: `77ea6bc27beb1657673e57be763b05419c98bc05`.
- Source path: `evaluation/e1_a2_dynamic_question_decomposition_validation_manifest.json`.
- Implementation: `87cc34dd919d8431bb774003a7f76a9fff3a7567`.
- Preregistration: `2517b691245c38175222064e6ca546d06fd21e9a`.
- Raw freeze: `7eab1e8fe099fed6ff06384c4fa0eb48dcf52677`.
- Closeout identity: Git commit introducing this report, judgments, result and lifecycle update.

All 12 selected objects were resolved from the historical Git source in its original
order; no independent Gold copy or annotation rewrite was created. Selected pairs
07–12 have source IDs n001/n008/n020/n022/n030/n031, source_group novel_dev and language
en. There are six bases, six paraphrases and 28 references; base strata 2x4 and3x2.
No current novel source, protected validation or holdout was accessed. This is exposed
regression/closure evidence, not fresh prospective or representative sampling.

Prompt `2.0.0`, schema `e1.question_decomposition.v2`, generation/judge
`gemini-3.8-flash` in separate clients, global, temperature0, timeout120000ms.
Python3.13.14, pydantic2.13.4, google-genai2.13.0. Production source/configuration and
all frozen C1 inputs remained unchanged throughout execution. Historical E1-A2 and
E1-R2 artifacts were not edited or scientifically rerun.

## Primary gates

| Gate | Observed | Required | Verdict |
|---|---|---|---|
| C1-G1 Structural validity | 12/12 | 12/12 | PASS |
| C1-G2 Semantic reference recall | 28/28 (100%) | 100% | PASS |
| C1-G3 Semantic prediction precision | 28/28 (100%) | 100% | PASS |
| C1-G4 Under-decomposed cases | 0/12 | 0 | PASS |
| C1-G5 Over-decomposed cases | 0/12 | 0 | PASS |
| C1-G6 Exact point count | 12/12 | 12/12 | PASS |
| C1-G7 Semantic-complete pairs | 6/6 | 6/6 | PASS |
| C1-G8 Hidden prerequisites | 0 | 0 | PASS |

All judgments were scoreable. No structural, provider or evaluation infrastructure
failure occurred in scientific execution. Under the frozen judge contract, there
were no semantic omissions, merges, over-splits or relational over-splits.

## Required sentinel and per-pair results

C1-S1 pair09/n020: base matches3/3, predictions3, extras0, PASS; paraphrase matches3/3,
predictions3, extras0, PASS. Overall PASS. Both outputs independently request the
leftover-hit task identity, displaced-track contribution and z-recovery contribution.
Static inspection of the completed raw texts confirms these are separately addressable
needs. No PANDA answers were produced or inferred by the evaluation.

| Pair / source | Shape | References base/paraphrase | Predictions base/paraphrase | Missing slots base/paraphrase | Extras base/paraphrase | Completeness base/paraphrase |
|---|---|---|---|---|---|---|
| pair07 / n001 | Configuration behavior | 3/3 | 3/3 | 0/0 | 0/0 | PASS/PASS |
| pair08 / n008 | Track-search identification and comparison | 2/2 | 2/2 | 0/0 | 0/0 | PASS/PASS |
| pair09 / n020 | Leftover task and independent contributions | 3/3 | 3/3 | 0/0 | 0/0 | PASS/PASS |
| pair10 / n022 | POCA handoff and reprocessing | 2/2 | 2/2 | 0/0 | 0/0 | PASS/PASS |
| pair11 / n030 | Preprocessing reason and effect | 2/2 | 2/2 | 0/0 | 0/0 | PASS/PASS |
| pair12 / n031 | Generator comparison and standard | 2/2 | 2/2 | 0/0 | 0/0 | PASS/PASS |

The machine result preserves each case ID, reference/prediction counts, missing IDs,
extra IDs and completeness, plus the explicit sentinel decision. Taxonomy was never
sent to the judge. 27/28 predictions had labels,17/27 labeled matches agreed exactly;
ten label disagreements and one omission are secondary diagnostics only.

## Cost and execution

| Role | Logical calls | Returned model calls | Generation calls | Returned tokens |
|---|---:|---:|---:|---:|
| Decomposition | 12 | 12 | 12 | 16417 |
| Judge | 12 | 12 | 12 | 13682 |
| Total | 24 | 24 | 24 | 30099 |

Analyzer0; Embedding0; Reranker0; Retrieval0; QA answer0; QA review0; QA revision0.
No task retry, fallback, selective rejudging or adapter-counter-indicated retry.
Underlying SDK HTTP/billing request counts and monetary cost are not measured;
logical calls are not billing counts.

All12 raw records were committed before any semantic judgment; progress inspection
was operational only until execution completed. No prompt/schema/selector/reference/
gate repair occurred after freeze. No failed case was replaced or dropped.

AGY static review job `staffer-mtssvfc4-50a3cfa5` crashed with EPERM on local state-lock
rename before a stored result. No independent subagent review completed. Routing
advertised gemini-3.8-flash-high, but actual worker model/effort and provider usage
were unavailable. Do not count this as zero usage or as a review PASS. This failure
was separate from the fully successful scientific execution; host verification
covered the protocol. No worker edits or intermediate-outcome review occurred.

## Verification

Initial focused tests27 passed/3 failed due to the test Git mock conflating source
and raw reads. After correcting the mock,30/30 passed before freeze. Offline source/
selector validation, count/strata checks, strict gates and sentinel checks passed.
C1 judge prompt/schema were verified identical to R2; generation/runtime identities
matched. No production or historical test edit was needed.

Post-execution frozen report reproduction and independent ID-set, exact-span,
record-order, pair/sentinel/count and usage reconciliation all passed. Raw Git content
matched its committed artifact, with the preregistration commit as its parent;
frozen source/protocol and historical evidence had no diff. `git diff --check` passed.
No full suite, T3/T4/T5, retrieval/QA benchmark, v1 rerun or R2 rerun occurred.

## Lifecycle and interpretation

E1-CLOSURE-REVIEW = COMPLETE / PASS /
REAL_PANDA_STYLE_CONFIRMATION_REQUIRED_BEFORE_CLOSURE.
E1-C1 = COMPLETE / PASS / REAL_PANDA_STYLE_EXPOSED_DEVELOPMENT_CONFIRMATION_PASSED.
E1 = COMPLETE / PASS / QUESTION_ONLY_SEMANTIC_ANSWER_POINT_DECOMPOSITION_VALIDATED.
Phase E = IN_PROGRESS / E1_COMPLETE / E2_NEXT.
E2 = NOT_STARTED. E3 = NOT_STARTED.

E1-A2 remains COMPLETE / FAIL / G7_FACET_TYPE_ACCURACY_AND_G8_PAIR_STABILITY_FAILED.
E1-R2 remains COMPLETE / PASS /
TARGETED_PROSPECTIVE_SEMANTIC_ANSWER_POINT_REVALIDATION_PASSED.
D4 = PAUSED / ROADMAP_RECONCILIATION; overall completion UNDECIDED.
F1 = COMPLETE / PASS / RESIDUAL_BENCHMARK_DEPENDENCY_INVENTORY_ESTABLISHED.
Phase F = IN_PROGRESS / F1_COMPLETE.
NEXT_TASK_RECOMMENDATION = E2 — Answer-Point Coverage and Claim Mapping.
NEXT_TASK_EXECUTION_AUTHORIZED = false. No subsequent task or production activation.

C1 confirms that v2 handles the exposed real-style atomicity failure motivating
repair, supplementing R2's targeted prospective evidence. The predeclared closure
condition is met, so E1 closes without another confirmation. Same-family judging,
small purposive exposed cases and correlated paraphrases limit inference: this is
not representative generalization or real-world accuracy estimation. Production
readiness, runtime completeness integration, claim-to-point coverage, targeted
retrieval and compatibility replacement remain outside E1. question_core and all
existing compatibility requirements remain authoritative and unchanged.
