# PANDA Agent — ND-0B: First Frozen Novel-Dev Retrieval Measurement Report

> Status: `ND-0B = COMPLETE / FIRST_EXPOSURE_MEASUREMENT_FROZEN` (2026-08-30).
This is the first controlled system-outcome exposure of the frozen `novel_dev`
dataset (28/28, retrieval-only), executed under the ND-0A/ND-0A-R1 frozen
contract. It is a measurement stage: no failure diagnosis, no causal
interpretation, no system changes, and no post-hoc thresholds appear here.
ND-0C owns interpretation.

## 1. Run identity and provenance

- Run ID: `nd0b-first-novel-dev-retrieval-20260830` (fresh; nothing overwritten).
- Measurement HEAD: `348dd0d3c4b1ac464498f2a16b65ccb4b39eb6d7`
  (`348dd0d ND-0A-R1 correct historical comparison provenance`); working tree
  dirty only by the untracked `data/sources.zip` (not part of the measured
  system).
- Dataset: `novel-v1-dev-expansion` / `novel-v1-dev-0.3.0`, split `novel_dev`,
  28/28 frozen, 28 independent families, dataset hash `25ad18fc…`. Frozen
  manifest fields unchanged (`agent_outcome_seen_before_freeze = false`).
- First-exposure transition: `FIRST_NOVEL_DEV_OUTCOME_EXPOSURE` NOT_STARTED →
  STARTED (first retrieval request) → **COMPLETE** (valid 28/28 completion);
  `NOVEL_DEV_DEVELOPMENT_EXPOSED = true`. This transition is irreversible and
  the artifacts below are the immutable first-exposure record
  (`FIRST_EXPOSURE_ARTIFACT_IMMUTABLE = true`; future reruns need new run IDs).

## 2. Production state at measurement (provenance snapshot)

| Aspect | Value |
| --- | --- |
| Production roles | exact `LEGACY_EXACT`; sparse = raw question; RawDense `PRODUCTION_AUTHORITATIVE`; SemanticDense `KEEP_DISABLED`; fusion `P0 CURRENT`; selector `CURRENT_SELECTOR`; D2 resolver `SHADOW` (not applied) |
| Prompt set | 3.7.0 (`8bc024ee…`) |
| Index | schema 4, fingerprint `8172f9a6…`, 104973 Qdrant points, 133075 SQL objects |
| Embedding | `gemini-embedding-2` / 3072 / cosine |
| Sparse | `Qdrant/bm25`, modifier `idf` (schema-4 portable receipt) |
| Retrieval policy hash | `ebe4cb10…` (identical to the value recorded in the historical Gold baseline artifact) |
| Query-expansion hash | `dad22d19…` (identical to the value recorded in the historical Gold baseline artifact) |
| D2 activation | `D2_RESOLVER_PRODUCTION_ACTIVATION = false` |

Policy/QE config-file identities matching the historical artifact is a
config-identity fact only; it does not make the cohorts or configurations
apples-to-apples (analyzer generation, index/corpus state, and provenance
still differ, per the frozen ND-0A-R1 comparison semantics).

## 3. Run validity vs dataset structural validity

These are distinct, and both are recorded:

- **Measurement execution valid = true** — 28 scheduled, 28 completed, 0
  unhandled exceptions, retrieval-only, frozen semantics. The first-exposure
  run is valid and immutable.
- **Dataset structural valid = false** — the frozen `novel_dev` evaluation
  dataset contains one evidence-mapping defect, detected during preflight
  **before the first retrieval request** (`known_before_first_outcome = true`;
  `known_pre_exposure_dataset_defect_count = 1`):

  - **n023.e1** (`EXPECTED_EVIDENCE_MAPPING_ISSUE`): selector `pandaroot` /
    `tracking/PndFtsTrackFinder/README.MD` matches no object in the
    evaluator-canonical normalized corpus, so the group is structurally
    impossible under the frozen mapping. The frozen dataset was not modified
    and the group is not replaced.

The distinction is mandatory: measurement execution succeeded does not imply
all frozen evaluation mappings were structurally valid.

**n023 factual impact (raw outcome, no reinterpretation; diagnosis belongs to
ND-0C):** n023.e1 unmatched / structurally impossible; n023.e2 (valid selector
for `tracking/PndFtsTrackFinder/PndFtsTrackFinderTask.cxx`) matched in the
combined candidate pool (provenance `ancestor`) but not in top-5/10/20 or
final evidence. Observed raw per-case values: combined candidate recall 0.5;
Recall@5 = Recall@10 = Recall@20 = MRR = final evidence recall = critical
evidence recall = 0. n023 remains in the primary 28/28 measurement.

**NON_PRIMARY PRE_EXPOSURE_DATASET_DEFECT_SENSITIVITY** (fully deterministic
offline arithmetic on the immutable raw records; zero model/retrieval calls;
Gold and raw records untouched): with the known-impossible n023.e1 ignored for
sensitivity purposes, n023's only valid group n023.e2 (matched in the combined
pool) would change n023's combined candidate recall from 0.5 to 1.0, moving
the combined-candidate-recall aggregate from 0.8117 to 0.8302 (+0.0185); all
other aggregate values are unchanged (n023 contributed 0 to them). This view
never replaces the primary metrics, which retain n023.e1.

## 4. Execution summary

- Cases scheduled 28; cases completed **28**; unhandled exceptions **0**;
  result statuses: 28 `answered` (retrieval-level status; see §6).
- Prohibited stages: `QA_GENERATION_CALLS = 0`, `ANSWER_VERIFIER_CALLS = 0`,
  `EXTERNAL_JUDGE_CALLS = 0`; no novel_validation or holdout case ran;
  `PRODUCTION_DB_WRITES = 0`, `QDRANT_WRITES = 0`.
- Cost: 85 retrieval-side model calls (28 dense query embedding calls, 57
  runtime generation calls — query analyzer and reranker; the
  analyzer/reranker split is not separately instrumented), 537,922 tokens,
  plus 1 preflight embedding call before the first case.

## 5. Aggregate metrics (frozen semantics; applicability-aware)

Ordinary retrieval metrics apply to the 27 answered-expected cases under the
evaluator-native applicability mechanism. Aggregate retrieval metrics are
**case-level arithmetic means** over those 27 cases (the
`panda_agent.evaluation` aggregation semantics: applicable per-case metric
values → arithmetic mean). The displayed numerator is the **sum of the
applicable per-case metric values**; the denominator is the applicable case
count. A numerator of 16.666667 with denominator 27 therefore means the 27
applicable per-case values sum to 16.666667 — it does not mean 16.666667
evidence groups matched, and it is not a per-case-fraction × group-count
weighting.

| Metric | Numerator | Denominator | Value |
| --- | --- | --- | --- |
| Recall@5 | 14.833333 | 27 | 0.5494 |
| Recall@10 | 16.666667 | 27 | 0.6173 |
| Recall@20 | 16.666667 | 27 | 0.6173 |
| MRR | 13.583333 | 27 | 0.5031 |
| combined candidate recall | 21.916667 | 27 | 0.8117 |
| critical evidence recall | 16.333333 | 27 | 0.6049 |
| final evidence recall | 16.333333 | 27 | 0.6049 |

Ranks 11–20 contributed no additional required-evidence-group recall under
the frozen evaluator semantics, which is why Recall@10 and Recall@20 are
identical.

## 6. The frozen insufficient_evidence case (n016)

n016 is retained in the 28/28 run. Expected `insufficient_evidence`; the
retrieval path returned non-empty evidence (12 final evidence items,
retrieval-level status `answered`), so the refusal expectation was not met —
a measurement outcome, not an execution failure. Its ordinary metrics are
excluded from the 27-case denominators by the frozen applicability rule, and
no post-hoc metric was invented.

## 7. Frozen stratified summaries

Preregistered strata only, from frozen curation metadata. Strata with fewer
than 3 applicable cases report counts only (small-cell rule).

### Intent

| Stratum | Cases | R@20 | Final evidence recall | Combined candidate recall |
| --- | --- | --- | --- | --- |
| algorithm_implementation | 5 | 0.5000 | 0.5000 | 0.6500 |
| algorithm_theory | 3 | 0.7778 | 0.7778 | 0.8889 |
| api | 3 | 0.5000 | 0.5000 | 1.0000 |
| data_flow | 2 | (small cell: counts only) | — | — |
| installation | 2 | (small cell: counts only) | — | — |
| module_structure | 2 | (small cell: counts only) | — | — |
| troubleshooting | 2 | (small cell: counts only) | — | — |
| usage | 9 | 0.7593 | 0.7593 | 0.8889 |

### Evidence topology

| Stratum | Cases | R@20 | Final evidence recall | Combined candidate recall |
| --- | --- | --- | --- | --- |
| comparison | 5 | 0.7667 | 0.7667 | 0.8333 |
| multi_hop | 6 | 0.5000 | 0.5000 | 0.7083 |
| producer_consumer | 3 | 0.4444 | 0.3333 | 0.6667 |
| single_hop | 14 | 0.6538 | 0.6538 | 0.8846 |

### Source scope

| Stratum | Cases | R@20 | Final evidence recall | Combined candidate recall |
| --- | --- | --- | --- | --- |
| cross_source | 3 | 0.4444 | 0.4444 | 0.5556 |
| single_source | 25 | 0.6389 | 0.6250 | 0.8438 |

### Repository scope

| Stratum | Cases | R@20 | Final evidence recall | Combined candidate recall |
| --- | --- | --- | --- | --- |
| cross_repository | 1 | (small cell: counts only) | — | — |
| paper_only | 2 | (small cell: counts only) | — | — |
| single_repository | 25 | 0.5903 | 0.5764 | 0.8090 |

### Required-evidence count

| Stratum | Cases | R@20 | Final evidence recall | Combined candidate recall |
| --- | --- | --- | --- | --- |
| multi | 17 | 0.5098 | 0.4902 | 0.7010 |
| single | 11 | 0.8000 | 0.8000 | 1.0000 |

### Representativeness

| Stratum | Cases | R@20 | Final evidence recall | Combined candidate recall |
| --- | --- | --- | --- | --- |
| exploratory | 2 | (small cell: counts only) | — | — |
| representative | 26 | 0.6533 | 0.6400 | 0.8367 |

Curation families are 28 independent one-question families (`nf001`–`nf031`
range); every family cell is a small cell, so family-level rows report counts
only in `nd0b_metrics.json`. The two `exploratory` cases and the
`cross_repository` case are small cells as well.

## 8. Historical reference comparison

**APPROXIMATE HISTORICAL REFERENCE COMPARISON — NOT AN APPLES-TO-APPLES
EFFECT ESTIMATE.** Reference: `english-gold-stratified-bootstrap-v1-20260813`
(`comparability_status = APPROXIMATE / NON_IDENTICAL_COHORT`;
`configuration_comparability = NON_IDENTICAL_CONFIGURATION`). Difference
direction: `novel_minus_historical_reference` (negative = novel lower).

| Metric | Historical Gold reference | ND-0B novel_dev | Difference |
| --- | --- | --- | --- |
| Recall@5 | 0.8417 | 0.5494 | -0.2923 |
| Recall@10 | 0.9000 | 0.6173 | -0.2827 |
| Recall@20 | 0.9000 | 0.6173 | -0.2827 |
| MRR | 0.6867 | 0.5031 | -0.1836 |
| combined candidate recall | 0.9500 | 0.8117 | -0.1383 |
| critical evidence recall | 0.9000 | 0.6049 | -0.2951 |
| final evidence recall | 0.9000 | 0.6049 | -0.2951 |

Per the frozen ND-0A-R1 interpretation: the gap is a historical cross-cohort
AND cross-configuration reference difference. It is not an apples-to-apples
treatment effect, must not be attributed solely to novel-question
generalization, and must not be interpreted as "same system + different
dataset only". No causal interpretation is performed in ND-0B; substantive
diagnosis belongs to ND-0C.

## 9. Artifacts and immutability

- Provenance note: the mirrored `nd0b_run_manifest.json` preserves the raw
  runner manifest verbatim, including its machine-local absolute
  `gold_dataset_path` (non-sensitive provenance debt, kept for raw fidelity;
  the repository-relative dataset identity is recorded in
  `nd0b_first_exposure_manifest.json`). No holdout path appears anywhere.
- Raw run (gitignored working location):
  `data/evaluation/runs/nd0b-first-novel-dev-retrieval-20260830`.
- Tracked immutable first-exposure package: `evaluation/novel/v1/nd0/` —
  `nd0b_first_exposure_manifest.json`, `nd0b_run_manifest.json`,
  `nd0b_retrieval_results.jsonl` (per-case results, diagnostics, metrics),
  `nd0b_retrieval_traces.jsonl` (28 retrieval traces), `nd0b_metrics.json`,
  this report.
- Per-case records preserve question IDs, expected statuses, applicability,
  channel/combined candidate IDs and ranks, final selected evidence,
  required-evidence match provenance, Recall@k/MRR contributions, and
  per-case cost — sufficient for ND-0C, with no repair recommendations
  included (by contract).

## 10. Next stage

`ND-0C — Generalization Diagnosis and D2-A3 Handoff` remains NOT_STARTED.
