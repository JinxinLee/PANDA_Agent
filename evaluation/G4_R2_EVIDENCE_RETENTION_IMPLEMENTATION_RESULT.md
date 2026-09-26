# G4 R2 Evidence-Retention Deterministic Implementation Result

## Decision

`G4_R2_DETERMINISTIC_IMPLEMENTATION = PASS`. This is a bounded R2 retrieval-behavior repair, not a live QA or generalization result. The previous product-behavior lineage was `a0106bd5eff93646f34f5e50e161e8be8a49d680`; the `Implement G4 R2 evidence retention` commit is the new behavior lineage. Existing retrieval-policy YAML and its hash are unchanged; future runs distinguish this rule through that policy identity plus the new Git/product lineage.

## RED and implementation

At starting HEAD `9e5fd9ebdbbf258b0d09d3a4e0105a69ddf3dd7d`, the newly written R2-A test was run before changing product source:

```text
..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_g4_r2_evidence_retention.py::test_r2_a_valid_single_channel_policy_candidate_gets_rerank_opportunity
1 failed
```

The valid fictional-repository candidate had dense rank 1 and appeared in `fused_candidate_ids`, but 30 higher-scoring consensus objects occupied the offered rerank pool. The failure was the final assertion that the fake reranker received the candidate, not a plan, source/version, payload-consistency, or final-selector failure. The R2-A expectation was retained unchanged and became green.

`Retriever.consolidate_and_select_candidates` now uses one private bounded pool constructor after existing weighted RRF scoring and structured-supplement collection. Positive/required plan roles determine challenger ceilings; normal source-role occurrences and marked normal workflow/graph occurrences may compete outside the counterfactual RRF pool. Role queues use `(best qualifying rank, -RRF score, object_id)`, required-role/descending-budget visits, and successive rounds. Structured supplements are reserved first; the ordinary RRF backbone remains a strict majority of remaining slots. The global limit is still 30. Source/version/payload consistency and the R3 final selector remain in their existing places. `rerank_pool_entries` is an additive diagnostic-only return field.

`_workflow` and `_graph` mark normal versus generic fallback results at their known branch returns. An aligned internal `channel_origins` snapshot sidecar flows into `pass_occurrences`; historical missing markers grant no specialized frontier preference. Canonical payloads and the formal retrieval trace schema are unchanged. The local `retrieve` rerank remains its existing intermediate single-pass behavior; the diagnosed authoritative multi-pass rerank is in global consolidation. `collect_channel_candidates`, captured initial snapshots, and the E3 targeted-snapshot handoff in `qa.py` carry the sidecar into that seam. D3 graph stream modification clears the marker when alignment is no longer reliable.

## Verification

| Control | Outcome |
|---|---|
| R2-A valid single-channel omission | GREEN after demonstrated RED |
| R2-B weak noise | PASS; role ceiling excludes lower-ranked candidates |
| R2-C consensus majority | PASS; 17 RRF backbone / 13 frontier under multiple roles |
| R2-D global bound | PASS; 30 supplements occupy exactly 30 slots |
| R2-E dedup/provenance | PASS; one slot across channels, passes, roles, and supplement overlap |
| R2-F validity | PASS; wrong source/version, unusable payload, and inconsistent payload do not gain frontier access |
| R2-G supplement precedence | PASS; 28 supplements leave two RRF slots and zero frontier slots |
| R2-H deterministic ties | PASS; identical input repeats membership, order, and reasons |
| R2-I non-code roles/fallback | PASS; paper via dense, normal workflow/graph, paired fallback, and unknown historical origins |
| Origin branch check | PASS; normal/fallback workflow and graph branch returns mark their own items |
| E3 targeted handoff | PASS; `qa.py` forwards the origin sidecar into global consolidation |

Observed synthetic frontier counts range from 0 to 13. RRF backbone checks include 17 > 13 with multiple roles, 18 > 12 under a single-role ceiling, and two RRF slots with 28 supplements.

Commands and outcomes:

```text
..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_g4_r2_evidence_retention.py
12 passed

..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_g4_r2_evidence_retention.py tests/unit/test_retrieval.py tests/unit/test_retrieval_trace.py tests/unit/test_fusion_replay.py tests/unit/test_c8_global_candidate_pool.py tests/unit/test_e3_missing_point_retrieval.py tests/unit/test_g4_false_insufficiency_regression.py
203 passed, 27 subtests passed

..\.venv\Scripts\python.exe -m pytest -q tests/unit/test_g4_false_insufficiency_regression.py
18 passed
```

An E3 fixture sets `context_sources=None`; its first focused run exposed a `TypeError` in the new role check. Treating that optional fixture value as an empty context set fixed the issue. The final combined run passed. No existing G4 control was weakened.

The [exposed pool replay](G4_R2_EXPOSED_POOL_RETENTION_REPLAY.md) was run only after the generic rule and focused safety tests were green. All five previously lost reviewed objects across `n002`, `n006`, and `n017` enter the new offered pool through `policy_role_frontier`; this is non-gating and did not change the rule. Replay compatibility is partial because historical trace metadata omits full payload text/title, explicit supplement eligibility, and specialized-channel origin.

## Materiality and boundaries

`PRODUCT_SOURCE_CHANGE=true`, `PRODUCT_BEHAVIOR_CHANGE=true`, `RETRIEVAL_BEHAVIOR_CHANGE=true`, `R2_BEHAVIOR_CHANGE=true`. Prompt, question-decomposition and coverage schemas, public trace schema, manifest schema, admission, verifier, finalization, config, Gold, dataset, and calibration are unchanged. Dense re-embedding, sparse-index rebuild, and corpus re-ingestion are not required.

`SCIENTIFIC_CALLS=0`; `SCIENTIFIC_TOKENS=0`; `QA_RUNS=0`; `LIVE_RETRIEVAL_RUNS=0`; `EXTERNAL_JUDGE_CALLS=0`. `EXPOSED_REPLAY_CASES=n002,n006,n017`; `NEW_NOVEL_DEV_CASE_CONTENT_ACCESS=0`; novel-validation and holdout content/outcome access and protected leakage are 0. No fresh Lane B cohort exists, no empirical repaired-QA benefit is established, and no later phase is authorized by this result.
