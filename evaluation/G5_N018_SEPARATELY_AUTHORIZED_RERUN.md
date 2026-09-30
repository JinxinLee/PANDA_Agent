# G5 n018 Separately Authorized Rerun

## Scope and decision

The user separately authorized one `n018` rerun after the [original G5 integrated result](G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION.md). This is a new, one-case exposed-development `qa` run under `g5-n018-separately-authorized-rerun-v1`. The original G5 run and its nonretryable `n018` record are unchanged. The new record is neither a same-run recovery nor a replacement record for the frozen single-provenance 28-case G5 gate.

**Targeted rerun = COMPLETE / FALSE INSUFFICIENCY.** The new invocation scored `n018` without a D1 exception, but the product returned `insufficient_evidence` where the reviewed Gold expects `answered`. Independent locked-source review finds the question answerable. The answer states the two central methods and composite type setup, then appends a refusal and omits the source-supported EvtGen/PDG preparation. The original G5 result remains **INCOMPLETE / PRODUCT ERROR**, and the integrated candidate remains **not ready for G6**. The single later realization does not prove that the D1 failure class has been repaired.

The [machine result](G5_N018_SEPARATELY_AUTHORIZED_RERUN_RESULT.json) preserves both runner verdicts, the old exception, new source and stage pointers, review, and mixed-provenance arithmetic. Raw new records remain Git-ignored at `data/evaluation/runs/g5-n018-separately-authorized-rerun-v1/`.

## Identity and execution

| Item | Observed |
|---|---|
| Original evaluated HEAD | `52c9fc6b2fc2c8e021973aefe8a6d92ceb616e1b` |
| Targeted rerun evaluated HEAD | `0b8e4c6605ebfeb1a1245319289e6b480763a23b`, clean at launch; intervening commit records the G5 result only |
| Product-behavior lineage | `047201166057edd9859292a1760bc2e9bbf173a2`, unchanged |
| Run | `g5-n018-separately-authorized-rerun-v1`; `qa`, `novel_dev`, `case_ids=[n018]`, `limit=none`, `allow_draft=true`, stage traces enabled, no candidate ID |
| Dataset | `evaluation/novel/v1/novel_dev.yaml`, `novel-v1-dev-0.3.0`, SHA256 `25ad18fcf76ab2796aa18ae961bdc4faf076f0c98a8a5226413ec95e58252223` |
| Preflight | PASS: new run ID unused; source, normalized corpus/output, index, prompt, model, retrieval/query-expansion, dataset, audit-resolution, and package-version manifest fields match the original G5 run; no product-source diff from lineage |

The first local preflight script imported `load_gold_dataset` from a nonexistent module and failed before scientific calls. Correcting the import to `panda_agent.evaluation` completed the identity check; the scientific run then used one invocation. No runtime package drift was observed relative to original G5. The guardrails remained 450 model calls and 2,500,000 tokens; neither was reached.

## Raw result and n018 review

| Field | Observation |
|---|---|
| Runner `run_status` | `status=complete`, `cohort_status=COMPLETE`, `official_decision=FAIL`, `1/1` scored, no exception or retryable ID |
| Generic gates | Formal gate `passed=false`; development gate `passed=false`, `complete_full_dev=false`; product-language calibration `compatible=false`, `passed=null` |
| Expected / actual | `answered` / `insufficient_evidence` |
| Product text | Gives `RhoCandidate::GetMcTruth()` with a null check; gives `PndAnalysis::McTruthMatch(candidate)` for arbitrary decay trees; says composite candidates need intended types; then says citable evidence does not establish a complete answer |
| Independently missing | The locked tutorial recommends initializing `TDatabasePDG` with EvtGen properties first, so particle type codes agree and truth matching does not fail from code mismatches |
| Final/cited source | `object.9177635263b46e8bee8b775a` from the permitted Monte Carlo Truth Match tutorial contains `GetMcTruth`, `McTruthMatch`, type setup, and the EvtGen/PDG recommendation; it entered the pool, final evidence, and citation |
| Runtime review | `point.1` valid; `point.2.rel.1` local invalid due to `INVALID_SUPPORTER`, with `MISSING_COMPLEMENT_MISMATCH`; final answer becomes insufficient. Visible receipts do not establish why the supporter was judged invalid or prove a validator implementation defect |
| R2 | Critical tutorial evidence retained; no observed G4 retention-contract contradiction |

The earliest demonstrated critical-content omission is in generation: the final answer leaves out the cited EvtGen/PDG preparation. The V1 local-invalid review is a separate, observed contributor to final refusal. Both are reported without converting the visible `INVALID_SUPPORTER` code into an unproven validator-fault diagnosis. The new result is a false insufficiency on an independently answerable question, even though the response contains useful partial guidance.

The targeted run used **5 model calls / 40,696 tokens**: 4 generation calls, 1 embedding call, 0 external judge calls. It attempted and scored exactly one case, with no resume. Citation integrity is true; wrong-version and forbidden-evidence counts are zero.

## Reissued aggregate interpretation

| Scope | Complete answers | Incomplete answers | Insufficient responses | Errors | False insufficiency | Decision authority |
|---|---:|---:|---:|---:|---:|---|
| Original single-run G5 | 7 | 12 | 8 | 1 | 7 | `INCOMPLETE / PRODUCT ERROR`; authoritative G5 result |
| Old 27 QA results plus new `n018` result | 7 | 12 | 9 | 0 | 8 | Mixed-provenance diagnostic only; **not** a complete G5 run |

Across both run invocations there were 29 case attempts, 28 distinct usable QA results, **169 model calls / 1,166,960 tokens** (140 generation, 29 embedding, 0 external judge). Those sums are spending and diagnostic accounting, not a single-run quality verdict. The original n018 D1 exception and the new false refusal are both real observations. No best-of choice, raw-record rewrite, or 28-case composite gate is made. A complete integrated single-provenance outcome would require a separately authorized new evaluation design and run; this task authorizes neither.

`G5_INTEGRATED_RUN_COMPLETE=false`, `G5_INTEGRATED_CANDIDATE_READY_FOR_G6=false`, and `PHASE_G=IN_PROGRESS / G5_INTEGRATED_CANDIDATE_EXPOSED_REGRESSION_INCOMPLETE` remain current. The smallest next recommendation stays **G5 D1 NONRETRYABLE PRODUCT ERROR FAILURE REVIEW**; the newly observed `n018` false-insufficiency/semantic-completeness evidence should be included in that review or a later separately authorized owning-layer decision. No product repair, new mode, dataset/Gold/calibration edit, G6, protected-data access, or fresh generalization claim follows.

```text
PRODUCT_SOURCE_CHANGE = false
PRODUCT_BEHAVIOR_CHANGE = false
TEST_CHANGE = false
PROMPT_CHANGE = false
CONFIG_CHANGE = false
SCHEMA_CHANGE = false
DATASET_CHANGE = false
GOLD_CHANGE = false
CALIBRATION_CHANGE = false
NEW_RUNTIME_MODE = false

NOVEL_VALIDATION_CONTENT_ACCESS = 0
NOVEL_VALIDATION_OUTCOME_ACCESS = 0
HOLDOUT_CONTENT_ACCESS = 0
HOLDOUT_OUTCOME_ACCESS = 0
PROTECTED_LEAKAGE = 0

EXPOSED_DEVELOPMENT_ONLY = true
FRESH_GENERALIZATION_EVIDENCE = false
RELEASE_EVIDENCE = false
NEXT_TASK_EXECUTION_AUTHORIZED = false
```
