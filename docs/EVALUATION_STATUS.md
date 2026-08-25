# PANDA QA Agent — Evaluation Status

This file records transient evaluation state: current Gold/evaluator versions, candidate status, unresolved cases, run provenance, metrics, hashes, and historical checkpoints.

Stable evaluation rules belong in `docs/EVALUATION_POLICY.md`.
Day-to-day Codex behavior belongs in `AGENTS.md`.

When records conflict, use the single section explicitly marked **Current authoritative state**.

---

# Current authoritative state — 2026-08-24

## A3 measured execution provenance

- Base Git commit when the A3 measurements started: `e132accefc8181abba76e8d818a621dd03cd1c9c`.
- Working tree: dirty because A1–A3 and governance changes were then uncommitted.
- The measurements therefore represent that base commit plus the then-current working-tree changes. This is valid prototype diagnostic provenance, not a frozen candidate identity.
- A later user-created commit or newer repository HEAD does not rewrite this measured execution identity and does not require an evaluation rerun.
- Prompt set: `3.6.0`.
- Generation and runtime verifier role: `gemini-3.6-flash`.
- Evaluation judge configuration: `gemini-3.6-flash`; it was not invoked by the current retrieval or small QA baseline.
- Dense embeddings: `gemini-embedding-2`, configured 3072 dimensions.
- Sparse encoder: `Qdrant/bm25`, English, local-files-only.
- Index identity: `c527bbf1d10c88969da02745d678c640a4544757258584110a5ddd7744be3cf2` (`index_schema_version=2`).
- Gold: v2.6, identity `b5406e36c64ee664f9e2ff9c0f42e354feb7164c81d8f1c7551d8f2ed1d0b687`.

## Current runtime defaults after B1

- Base Git commit for the current prototype state: `422246c` (`Finish A3.1`); the working tree is dirty and remains valid prototype provenance.
- Current generation and evaluation-judge defaults: `gemini-3.7-flash`.
- Dense embedding remains `gemini-embedding-2`, configured at 3072 dimensions.
- These current defaults do not rewrite the A3 measured provenance above, which remains `gemini-3.6-flash` with index schema 2 and identity `c527bbf1d10c88969da02745d678c640a4544757258584110a5ddd7744be3cf2`.

## N1 novel-dev pilot curation — 2026-08-24 (human-reviewed and frozen)

- N1 status: `PASS / COMPLETE`. The 16-question `novel_dev` pilot has been human-reviewed and frozen. Human reviewer `Li` accepted 14 items at `2026-08-24T00:28:55+02:00`, requested revisions to n002 and n008, and accepted both corrected items on re-review at `2026-08-24T00:49:13+02:00`. Final decisions: 16 ACCEPT / 0 REVISE / 0 REJECT / 0 PENDING. All 16 active records are `approved` with reviewer `Li`, and all 16 sidecar lifecycles are `split_frozen`.
- Active count: `16` `novel_dev` questions (`n001`-`n010`, `n014`-`n019`) in `16` independent active families. Drafts n011/nf011, n012/nf012, and n013/nf013 are `WITHDRAWN_DRAFT`; n011's repaired analysis-usage information need moved to n018, n012's unsupported original information need was replaced by independently sampled n019, and n013 remains replaced by n017. Retired IDs remain historical and must not be reused.
- Intent coverage: 7 of 8 canonical intents (installation 2, usage 4, api 3, algorithm_theory 2, algorithm_implementation 2, data_flow 0, module_structure 1, troubleshooting 2). Expected status: `15` answered / `1` insufficient_evidence. Difficulty: 5 simple / 9 moderate / 2 hard. The missing data-flow intent is an explicit pilot gap, not a forced quota fill.
- N1-R2R1 corrected n001's evaluator-compatible source type to `workflow` and removed the false claim that PndFsmResponse carries detector efficiency. Human review then revised n002 to treat `requirements.txt` as a repository-declared Python requirements/tooling list rather than proof of per-script runtime requirements, and added n008's directly supported Cellular-Automaton versus Track-Following performance result with the minimum locked-PDF extension from pages 72–77 to 72–78. The repaired n011 content was reclassified as `usage` / `component_usage` under new ID n018 with tutorial-only evidence; n012 was retired without migration; n019 covers the independently sampled PndRecoKalmanTask implementation pipeline.
- Representativeness: 16 representative / 0 exploratory, following `benchmark_reference_fit` plus `domain_relevance`, with no active representative/exploratory quota. Primary task archetypes include two `implementation_explanation` cases, one `source_location`, and no fabricated data-flow replacement.
- N1-R1 methodology remains authoritative (`benchmark_reference_proxy`, `empirical_user_frequency: false`, task archetype orthogonal to answerability). The static validator freshly derives minimum required source scope, topology, and difficulty for all Gold v2.6 cases.
- Package: `evaluation/novel/v1/`; review artifacts `N1_FINAL_HUMAN_REVIEW.md` and `N1_FINALIZATION_REPORT.md`; sidecar v3; dataset identity `novel-v1-n1-pilot`; dataset version `0.2.0` (`novel-v1-dev-0.2.0`); `release_eligible: false`. This is a frozen pilot, not the final ~30-question `novel_dev`.
- No evaluation or runtime inspection occurred: PANDA retrieval, QA, judge, Vertex, embeddings, index rebuilds, and benchmark/novel outcome inspection were all `0`. Only locked source/PDF inspection and static T0 validation were used.
- No validation or holdout content was created; full-dataset quotas remain unfrozen.

## N2 expansion planning and plan review — 2026-08-24 (historical; superseded by the N2-A section below)

- N2 status: `PLAN_DRAFT / HUMAN_REVIEW_PENDING`. `evaluation/novel/v1/N2_FULL_NOVEL_DEV_EXPANSION_PLAN.md` proposes the expansion from the frozen 16-question pilot toward the ~30-question full `novel_dev`: coverage diagnosis, a static locked-corpus support audit, 16 labelled `PROPOSED_SOFT_TARGET` coverage bands with an explicit non-quota statement, the anchor-first sampling protocol, semantic-family isolation, representative/exploratory and status-selection policies, Batch 1 / Batch 2 design, the no-outcome contamination boundary, a `0.3.0` expansion-lineage versioning proposal, the human-review workflow, freeze criteria, and out-of-scope list.
- Strongest audited supports: data_flow / producer-consumer (restgas `macro/target` POCA pipeline, `macro/run` stage chain), genuine cross-repository workflow needs (pandaroot `detectors/lmd` plus the luminosityfit README workflow, under a strict two-repository-identity rule), source_location and implementation_explanation anchors (`tracking/`, LMD sources), documentation_navigation via the locked sphinx snapshot, and moderate exploratory regions (`softrig`, `timebased`, rare locked-thesis chapters).
- The plan creates no question, Gold record, or dataset-version change at planning time; the frozen N1 artifacts are untouched and N1 remains `PASS / COMPLETE`. No PANDA Agent component, evaluation tier, or outcome inspection occurred.
- Human review (2026-08-24): `REVISE` with five required revisions — (1) align `expected_split_counts`/`expected_status_counts` semantics with the runtime evaluator (all loaded question records, not approved-only; curation contract §11 updated accordingly); (2) relax exploratory admission to domain relevance plus one or more substantive exploratory properties; (3) remove Gold-proxy-derived numeric caps on `component_usage`, `setup_environment`, and `documentation_navigation` (prioritization guidance, not ceilings); (4) reframe exploratory targeting as an investigation pool and identify the 25/50/25 difficulty band as a pilot-derived heuristic, not a contract rule; (5) keep the strict cross-repository definition with final classification contingent on the annotated minimum critical evidence footprint requiring two repository identities. All five revisions are applied in plan Rev 1; all other planning decisions were accepted. The subsequent re-review returned `ACCEPT` — see the N2-A section below.

## N2 full novel-dev expansion — 2026-08-25 (finalized and split_frozen)

- N2: `PASS / COMPLETE`. Plan Rev 1 was approved by `Li` at 2026-08-24T01:25+02:00 (commit `08626661e3bb776c8f74c4f5b28c85ff2147c0fb`; 5/5 prior revisions resolved).
- N2-A: `COMPLETE / SPLIT_FROZEN` — 6/6 ACCEPT (reviewer `Li`; n020/n024/n025 accepted 2026-08-24T01:50+02:00, corrected n021/n022/n023 accepted on re-review 2026-08-24T02:05+02:00 of commit `516ba51abc628c63c90c41bc722a3b3825eb0269`). All six are approved and were split_frozen during N2 finalization; the historical R1 corrections remain preserved.
- N2-B: `COMPLETE / SPLIT_FROZEN` (authorized 2026-08-24T02:17+02:00; first review by `Li` at 2026-08-24T02:42+02:00 of candidate `d70eb1b85bc704e329207edd3874403bf4672d3b`). The first decision was 1 ACCEPT (`n027`) / 5 REVISE (`n026`, `n028`, `n029`, `n030`, `n031`) / 0 REJECT / 0 PENDING; Li accepted all five corrected records on final re-review at 2026-08-25T22:11:57+02:00. Final Batch 2 totals: 6 ACCEPT / 0 REVISE / 0 REJECT / 0 PENDING. All n026-n031 are approved and split_frozen.
- Dataset lineage: `0.3.0` (`novel-v1-dev-0.3.0`, identity `novel-v1-dev-expansion`, status `COMPLETE`); 28 loaded records, 28 independent families, 28 human-approved, 28 split_frozen, 0 rejected. The 16 frozen N1 questions and the 12 approved N2 expansion records are preserved; retired n011/nf011, n012/nf012, and n013/nf013 remain inactive historical drafts.
- Parallel-stream isolation: no PANDA Agent component was run and no benchmark, novel, or C8 outcome was inspected or used for Batch 2 candidate selection. C8 development proceeds separately under its own authorization and its state is preserved as-is below.
- N2 finalization is complete. novel_validation remains not started, novel_holdout remains externally managed and not created, and novel evaluation was not run or authorized by this freeze.

## C8-A0 targeted-retrieval boundary inventory — 2026-08-24

- C8 status: `ACTIVE`; `C8-A0 = PASS` (artifact `evaluation/baselines/manifests/phase_c_c8_a0_targeted_retrieval_boundary_inventory_v1.json`; expected source HEAD `3e40dcace0d5ce30c6b9598f58c70f71b992b918` with zero src/configs delta to the audit branch HEAD; focused static tests `tests/unit/test_c8_a0_targeted_merge_semantics.py` `6/6`).
- Verified current targeted flow: sufficiency insufficient + `retrieval_count < max_targeted_retrievals (1)` + no version conflicts → `_targeted_retrieve` (qa.py:938-953) copies the initial plan (`RetrievalPlan.model_validate`), PREPENDS symbols parsed from `"symbol:"`-bearing sufficiency errors, and calls the FULL `Retriever.retrieve` pipeline on the augmented question (`"\nTarget missing evidence sources: ... Missing evidence details: ..."`); the analyzer is bypassed because a plan is supplied. Sufficiency is rerun after the targeted pass; at most one targeted pass is possible; verifier/revision can never trigger one.
- Merge is EVIDENCE-LEVEL, not candidate-level: the merge input is the two already-selected evidence lists (≤12 each), ordered targeted-first, deduplicated by `evidence_id`, truncated to `[:12]`, inside the initial bundle shell (`{**state["bundle"], "evidence": ...}`). Duplicate collision keeps the targeted (first) position but stores the initial-pass payload (dict first-insertion/last-write semantics). No global rerank exists: fusion, reranker, and `CURRENT_SELECTOR` each run once per pass and never again after the merge; global-competition properties A–K are all `ABSENT`.
- Identity finding: merge dedup key `evidence_id = stable_id(object_id + channel set)` is not one-to-one with `object_id`, so one object retrieved under different channel sets in the two passes survives as two final-evidence entries (fusion identity is `object_id`; merge identity is not aligned with it).
- State retention: initial bundle metadata survives the merge (plan/rankings/fusion/reranker/excluded receipts; exact/paper/workflow/graph payloads are discarded at retrieve return), while ALL targeted-pass metadata (targeted plan, channels, fusion, reranker, selector receipts, query text) is discarded except its selected evidence items.
- Replay capability for a future frozen C8 A/B: `INSUFFICIENT` — existing QA traces mix initial-pass channel state with post-merge evidence and record no targeted-pass state, pre-merge initial evidence, or pre/post-targeted sufficiency reasons; the minimum future capture state is listed in the artifact.
- Production isolation: `PRODUCTION_BEHAVIOR_CHANGED = false`, `SRC_CHANGED = false`, `CONFIG_CHANGED = false`, `GOLD_OUTCOMES_INSPECTED = false`, `NOVEL_DATASET_WORK_PERFORMED = false`; all zero-live-work ledger counters are 0. Development-only C6 candidates (P3, `C6_INTENT_AWARE_V1`) were not activated.
- Documentation-only cleanups applied with A0: C8 "apply C7 selection" clarified to feed the production-authoritative `CURRENT_SELECTOR` (C7 closeout), and the C7 intended vocabulary clarified to `PROTECTED/REQUIRED/PREFERRED/MAXIMUM` with no `MINIMUM`; historical C7 artifacts untouched.
- `C8-A1 = NEXT_ELIGIBLE / NOT_STARTED` (explicit global candidate-pool and provenance contract; evaluation-first/shadow, no production activation).

## C8-A1 global candidate-pool contract — 2026-08-24

- C8-A1: `PASS_AFTER_CONTRACT_FIDELITY_REPAIR` (architecture accepted as executed; the original contract pass required the pre-outcome A1R1 repair recorded in the next section — historical progression preserved). Contract identity `c8.global_candidate_pool.v1` (data/provenance contract only; NOT a production retrieval policy and NOT a ranking treatment), implemented as the pure, deterministic, unwired shadow module `src/panda_agent/global_candidate_pool.py` (artifact `evaluation/baselines/manifests/phase_c_c8_a1_global_candidate_pool_contract_v1.json`; C8-A0 anchor `4028d366a3a8ccf170bbdf8200fddb408cc490b9`; focused synthetic tests at A1 time `15/15`; C8-A0 merge tests rechecked `6/6`).
- Cross-pass candidate identity is `object_id` (C6 fusion identity; `evidence_id` derives from object_id + pass-local channel set, so it is preserved only as occurrence/output provenance and never used as global identity). Origin classification is descriptive only: `INITIAL_ONLY` / `TARGETED_ONLY` / `BOTH` with independent per-pass occurrences (channels, channel ranks, Stage-F rank/score, Stage-R/M/P ranks, Stage-S selected + evidence_id, exclusion receipts, backfill status); ranks are never collapsed, averaged, or made authoritative across passes.
- Pass snapshots preserve pass origin, query text, complete RetrievalPlan, executed channel streams, and complete F/R/M/P/S state; `COMPLETE` vs `PARTIAL` is explicit — a snapshot whose Stage-F/M/P orders do not cover the full channel universe must declare `PARTIAL` (the current top-30 production diagnostics are PARTIAL, not the complete candidate universe). The targeted trigger context (original question, initial sufficiency result/errors, targeted query text, targeted plan, plan delta) is provenance only.
- The global pool builder performs object-level consolidation only: one candidate per `object_id`, canonical payload provenance, observability counts, deterministic `object_id` serialization order explicitly labeled as not a relevance ranking. NO global score, global rank, pass weighting, bonus, new RRF weights, normalization, new reranker prompt, new selector, or new final limit is defined; global fusion/reranker/selector are NOT implemented.
- Minimal version-safety invariants fail fast: Stage-R ⊆ Stage-F membership, M = dedup(R+F), P = permutation of M, Stage-S ⊆ universe, payload provenance for every candidate, same `object_id` cannot map to conflicting source/version identity across passes, `semantic_dense`/`lexical` rejected as executed channels (representation-only).
- A0 terminology clarification (A0 artifact unchanged, verdict stays `PASS`): SemanticQuery and LexicalQuery representations are COMPUTED/shadow-capable, while SemanticDense retrieval and lexical sparse retrieval are `NOT_EXECUTED` in production `Retriever.retrieve`; dedicated shadow methods may execute them separately. Recorded debt (not fixed, by scope): `error.split("symbol:", 1)[1]` in `_targeted_retrieve` can preserve leading whitespace in targeted symbols (`EXISTING_TARGETED_QUERY_DEBT`).
- Production isolation: `PRODUCTION_BEHAVIOR_CHANGED = false` (qa.py, retrieval.py production paths, and the targeted merge are untouched and must not import the module during A1), `CONFIG_CHANGED = false`, `GOLD_OUTCOMES_INSPECTED = false`, `NOVEL_OUTCOMES_INSPECTED = false`; zero-live-work ledger all 0. Replay of real targeted cases remains NOT captured — that belongs to A2.
- Baseline compatibility: the only commit between the A0 anchor and this task (`4769a63`, novel curation closeout) touched shared docs and `evaluation/novel/` only; C8-relevant runtime paths and C6/C7/C8-A0 artifacts are unchanged.
- `C8-A2 = NEXT_ELIGIBLE / NOT_STARTED` — frozen two-pass capture and global-treatment preregistration (populate the A1 contract from real targeted cases; establish faithful CURRENT append parity; preregister global treatments before relevance outcomes). Live capture is NOT authorized in A1.

## C8-A1R1 contract fidelity repair — 2026-08-24

- C8-A1R1: `PASS` (artifact `evaluation/baselines/manifests/phase_c_c8_a1r1_contract_fidelity_repair_v1.json`; A1 anchor `e17f8b2`; focused contract tests `23/23` — 15 original plus 8 repair tests; C8-A0 merge tests rechecked `6/6`; zero live work). Pre-outcome correctness repair of the SAME contract identity `c8.global_candidate_pool.v1` — no v2, no architecture change, no new policy semantics.
- Five repaired invariants, all fail-closed: (1) `build_global_candidate_pool` requires `initial.pass_origin is INITIAL` (the second snapshot remains fail-closed to `TARGETED`); (2) `stage_m_order` must exactly equal `dedup_preserving_order(R + F)` — correct membership with wrong order is rejected because Stage-M rank is provenance; (3) per executed channel, ranks must form exactly the contiguous stream `1..N` (duplicates, gaps, zero, negative rejected); (4) every `payloads[key]` must satisfy `payload.object_id == key` (object_id is the authoritative identity); (5) `stage_s_evidence_ids` keys must always be a subset of Stage-S selected IDs, `COMPLETE` requires exact equality, and a `PARTIAL` subset is allowed only when the missing evidence-id coverage is documented in `completeness_notes`.
- All A1 invariants are preserved without weakening; `object_id` cross-pass identity, `evidence_id` occurrence role, `INITIAL_ONLY`/`TARGETED_ONLY`/`BOTH`, `COMPLETE`/`PARTIAL`, deterministic non-relevance serialization, and the UNWIRED production isolation are unchanged. No global score/rank, pass weighting, bonus, normalization, new RRF logic, global fusion/reranker/selector, new reranker prompt, or new final limit was added.
- `EXISTING_TARGETED_QUERY_DEBT` remains `RECORDED_ONLY / NOT_FIXED` (leading-whitespace symbol parsing in `_targeted_retrieve`).
- Production isolation: `PRODUCTION_BEHAVIOR_CHANGED = false`, `QA_RUNTIME_CHANGED = false`, `RETRIEVER_RUNTIME_CHANGED = false`, `CONFIG_CHANGED = false`, `GOLD_OUTCOMES_INSPECTED = false`, `NOVEL_OUTCOMES_INSPECTED = false`; qa.py/retrieval.py untouched; the C8-A0/A1 artifacts are unchanged.
- `C8-A1 = PASS_AFTER_CONTRACT_FIDELITY_REPAIR`; `C8-A2 = NEXT_ELIGIBLE / NOT_STARTED` (frozen two-pass capture and global-treatment preregistration; eligible only after this A1R1 PASS; live capture NOT authorized here).

## Generalization Phase status

# Current Evaluation Status

**Phase C, legacy C3-R1/R2/R3 — historical single-vector semantic replacement evaluations**: `INCONCLUSIVE` (all three historical conclusions and artifacts remain preserved; the legacy single-vector replacement is superseded and not accepted for production)
**Phase C, C3-A1 — Raw-preserving dense-query contract**: `PASS` (`20/20` final focused contract checks; RawDense is explicit and production-authoritative)
**Phase C, C3-A2 — Shadow dual-dense verification**: `PASS` (the authoritative Qdrant preflight, separate one-call credential preflight, and five-case raw/semantic shadow execution passed within the exact 10-embedding/10-dense-read budget; semantic unique-relevant is N/A without an authoritative relevant-object set)
**Phase C, C3-A overall / current C3**: `PASS` (revised raw-preserving architecture; RawDense remains production-authoritative; SemanticDense is auxiliary/experimental and explicit shadow-only; production fusion efficacy remains unvalidated and deferred to C6)
**Phase C, C2 — QueryAnalyzer implementation**: `PASS`
**Phase C, C1 — Retriever entrypoint and channels**: `PASS` (C1-R1 closeout; initial implementation was `INCONCLUSIVE` after review)
**Phase C, C4 — LexicalQueryBuilder for sparse retrieval**: evaluation verdict `INCONCLUSIVE`, lifecycle `CLOSED_INCONCLUSIVE` (`C4-A1` `PASS`; `C4-A2` `INCONCLUSIVE`; `C4-A2R1` `INCONCLUSIVE`; `C4-A3` architectural closeout `PASS`; the completed 46-case screening found `3` treatment-qualified cases (`g008,g110,g113`), below the six-case minimum, so no live sparse outcome was ever collected; production sparse remains the exact raw question and `LexicalQuery` is a retained experimental/shadow abstraction)
**Phase C, C5 — Entity-first exact retrieval**: evaluation verdict `INCONCLUSIVE`, lifecycle `CLOSED_INCONCLUSIVE` (`C5-A0` generic inventory `DONE`; `C5-A1` `PASS` — entity-resolution contract, boundary-safe alias matching, explicit ambiguity, locked-version safety, preserved legacy fallback, `63/63` focused T0; `C5-A2` `INCONCLUSIVE` — mention-layer screening qualified `39/46` cases but `0` DESCRIPTIVE_OR_ALIAS cases exist because the accepted-alias corpus has only `2` rows that never occur whole in the locked English pool, so the preregistered minimum of `2` descriptive cases fails and the 12-case exact A/B ran as diagnostics only: Recall@10/20 unchanged at `0.3333`, MRR `0.2222 -> 0.1369` with `3` regressed and `0` improved, safety gates all clean; `C5-A3` architectural closeout `PASS` with the identity-strength finding — unique exact retrieval match is not sufficient canonical identity evidence for unconditional prefix promotion; production exact remains `LEGACY_EXACT` and `EntityResolver`/`shadow_exact` are retained experimental/shadow)
**Phase C, C6 — Multi-channel fusion evaluation**: `COMPLETE` (`C6-A0` `PASS` — frozen-channel inventory complete with explicit PRESENT/EMPTY/SKIPPED/MISSING/INVALID states: 80 core-replay cases from the phase-b t3 traces with all six production channels authoritatively recorded, 5 faithful semantic_dense streams from the C3-A resume (raw streams verified object-identical to t3 dense), novel data `ABSENT`; `C6-A1` `PASS` — pure evaluation-only `src/panda_agent/fusion_replay.py` reproduces current production weighted-RRF fusion (`K=60`, exact 2.0/raw_dense 1.0/sparse 1.0/paper 1.15/workflow 1.2/graph 0.8, object_id identity, production insertion-order ties) with `80/80` exact order+score parity against historical fused traces and `23/23` focused T0; P0-P5 policies, cohort rules, A2 metrics, 10 hard safety gates, the SemanticDense decision tree, intent-aware eligibility, and the novel corroboration gate all frozen before any A2 relevance outcome; production fusion `UNCHANGED`; `C6-A1R1` `PASS` as a scope/provenance correction — inherited the authoritative 59-case formal-English product scope (`phase_b_t3_product_language_scope_v2.json`; raw en/cn/mix labels were NOT the filter, 8 raw-`mixed` pure-English cases included, 59/59 map into the 80-case historical replay set) and audited current-plan fidelity: `0/46` formal-English cases with current 3.7.0 plans are channel-input compatible with the frozen 3.6.0-era streams (exact-channel concepts differ on `46/46`, plan repository scopes on `22/46`, e.g. g021 3→2 repos; 13 cases have no faithful current plan) → `C6-A2 = NOT_ELIGIBLE` at that point; `C6-A1R2` `PASS` then refreshed current-plan candidate coverage: with the 46 faithful 3.7.0 plans a 30-case `CORE_CAPTURE_COHORT` plus one semantic supplement case were frozen before retrieval and captured through the current production channels (`31/31 CAPTURE_COMPLETE`; embeddings `35`, sparse encodes `31`, Qdrant reads `87`, SQL reads `282` all read-only-asserted; `0` analyzer/reranker/QA generation), producing `evaluation/baselines/replay/phase_c_c6_current_plan_candidate_replay_v1.jsonl` with `P0` replay integrity `30/30`; a subsequent provenance preflight audit found 3 core cases captured under empty-default plan fields, and the authorized provenance repair then rebuilt all six affected cases from the faithful C3-R3 full plans (identity gate `MATCH`, `6/6` recaptured, replay v2 = 34 rows with 28 unchanged v1 rows, core-30 identical, P0 integrity `30/30`, unaffected parity `27/27`), so `C6-A1R2 = PASS_AFTER_PROVENANCE_REPAIR` and `C6-A2 = ELIGIBLE / NOT_STARTED` (`semantic_a2_evidence_eligible=true` after the A1R2 semantic-cohort correction: 8 semantic-active faithful cases over 4 intents — the repair verification had undercounted the cohort at 6 by adding live-cohort/supplemental restrictions the original semantic preregistration does not contain; `phase_c_c6_a1r2_semantic_cohort_correction_v1.json`); `C6-A2` `PASS` — the frozen P0-P5 comparison over replay v2 ran with the authoritative evidence-group matcher (`panda_agent.evaluation`, C3-R3-frozen) under a persisted pre-outcome lock: P3 sparse-heavy passes all 10 hard gates (Fused R@20 `1.0`, critical `1.0`, MRR `+0.0334`) while P1 fails 5/6/7 and P2 fails 3/5/7; P4 fails hard gates 3/5/7; P5 keeps the scored prefix identical to P0 on 8/8 with `NOT_MEANINGFUL` expansion yield (marginal candidate-recall contribution `0.0` on every case); SemanticDense unique-relevant-case count `1 < 2` → `SEMANTIC_CONTRIBUTION = INSUFFICIENT` (production-role evidence `KEEP_DISABLED`); intent-aware eligibility `true` with the evaluation-only `C6_INTENT_AWARE_V1` mapping (installation→P3, troubleshooting→P2, others CURRENT); novel gate `ABSENT`, `NEW_PRODUCTION_POLICY_ACTIVATION = NOT_AUTHORIZED_BY_C6_A2_ALONE`, no production activation; the post-A2 critical-miss semantics audit then corrected Gate 5 to critical-group identity (no OLD_FALSE_NEGATIVE existed; P3 remains `PASS_ALL_GATES`, intent mapping unchanged, SemanticDense `KEEP_DISABLED`), so A2 stands at `PASS` after audit; `C6-A3` `PASS` — the frozen production-role decision keeps P0 CURRENT production-authoritative, retains P3 SPARSE_HEAVY as the development-supported global candidate and C6_INTENT_AWARE_V1 as the development-supported intent-aware candidate (both blocked from production activation by absent novel corroboration), rejects P1/P2/P4 as standalone global alternatives, gives P5 no production role, keeps SemanticDense `KEEP_DISABLED`, leaves production fusion and production code `UNCHANGED`, and closes the C6 lifecycle `COMPLETE` with `C7 NEXT_ELIGIBLE / NOT_STARTED`)
**Phase C, C7 — Explicit post-reranker selection evaluation**: `COMPLETE` (`C7-A0` `PASS`; `C7-A1` `PASS_AFTER_SEMANTICS_REPAIR`; `C7-A1R1` `PASS`; `C7-A2` `PASS_AFTER_EVALUATOR_REPAIR`; `C7-A2R1` `PASS`; the original `C7-A3` attempt remains historical `INCONCLUSIVE / PRE_OUTCOME_INFRASTRUCTURE_FAILURE`; `C7-A3R1` `PASS` made `C7-A3` `PASS_AFTER_PRE_OUTCOME_INVOCATION_RECOVERY`; `S1_POLICY_RESULT=CURRENT_PREFERRED_GATE_FAILURE`; `C7-A4` `PASS` retained CURRENT_SELECTOR as `PRODUCTION_AUTHORITATIVE`, rejected `c7.explicit_selection.v1` as a global production replacement, and closed C7 with `C8 NEXT_ELIGIBLE / NOT_STARTED`)
- Evaluation modes: `retrieval`, `qa`, and `full` have explicit recorded boundaries.
- Structured retrieval traces are persisted as atomic JSON and JSONL and can be loaded without rerunning QA.
- A3 was corrected from a possible full-retrieval interpretation to a stratified low-cost bootstrap baseline. Phase-B T3 (complete 80-question dev retrieval-only) was performed on `2026-08-16`; no full 120-question retrieval/E2E run was performed.
- Phase C is started by C1; the legacy C3 production implementation remains accepted as an implementation, while its single-vector semantic replacement behavior is superseded and not accepted for production. C1-R1 is `PASS`, C1 overall is `PASS`, and C2 is `PASS`. C3-R1, C3-R2, and C3-R3 remain historical `INCONCLUSIVE`; their artifacts and outcomes are preserved unchanged. The revised C3-A1 contract, C3-A2 shadow verification, C3-A overall, and current C3 are `PASS` for the raw-preserving architecture. The authoritative resume used one separate credential-preflight embedding plus exactly 10 case query embeddings and 10 dense reads for `g113,g055,g114,g115,g039`, with independent RawDense/SemanticDense streams and no fusion. SemanticDense production efficacy remains unvalidated and deferred to C6. C4-A1 is `PASS`; the C4 evaluation verdict is `INCONCLUSIVE`: the first offline preregistration screened only `6` evaluable faithful plans (`1` treatment-qualified among `6` screened, with `40` pool cases missing plan proof and not yet screenable — not a `1/47` activation rate), and the C4-A2R1 coverage-completion round later completed `46` valid plans over the same locked pool and found `3/46` treatment-qualified, still below the required six, so no live sparse preflight, encoding, reads, rankings, or outcome metrics ran. Production sparse remains the exact raw question and `LexicalQuery` remains an experimental/shadow abstraction. No C3-R4 or Gold sampling round was started, no novel retrieval generalization claim is made, and no formal T3, T4, or T5 was run. C4 lifecycle is `CLOSED_INCONCLUSIVE` after the C4-A3 closeout. C5 was then executed: C5-A0 inventoried storage generically (`2` accepted aliases, no multi-target or dangling aliases, no identity-safe relation predicate, existing FTS/title indexes reused with no new extension), C5-A1 introduced the entity-resolution contract in `src/panda_agent/entity_resolution.py` plus the shadow-only `Retriever.shadow_exact(question, plan)` with production `_exact()` unchanged (`63/63` focused T0 including C4 boundary regressions, `0` external/model calls), and C5-A2 preregistered then screened the `46` faithful frozen plans (`39` treatment-qualified, `0` descriptive/alias). With `0 < 2` descriptive cases the exact A/B ran as diagnostics only (`55` read-only exact SQL reads, `0` writes): Recall@10/20 `0.3333 -> 0.3333`, MRR `0.2222 -> 0.1369` (`3` regressed from the correctly-resolved PandaRoot Readme prefix, `0` improved), `0` lost hits / critical misses / version violations / out-of-scope promotions / false resolutions, `0` analyzer/Vertex/embedding/dense/sparse/Qdrant calls. Final C5 is `INCONCLUSIVE`; the C5-A3 architectural closeout is `PASS` and the C5 lifecycle is `CLOSED_INCONCLUSIVE` (identity-strength finding recorded; further C5 sampling under the current contract is closed; reactivation depends primarily on Phase-D generic entity infrastructure). Production exact remains legacy; C6 is `COMPLETE`: C6-A0 inventoried every frozen candidate source and produced the coverage matrix with explicit availability states (`80` CORE_PRODUCTION_REPLAY cases from `phase-b-t3-retrieval-20260816`, six production channels each, `PRESENT_NONEMPTY/PRESENT_EMPTY` authoritative; `5` SEMANTIC_REPLAY cases; `80` INTENT_DIAGNOSTIC cases across all 8 intents at `>=4` each; novel `ABSENT`), and C6-A1 delivered the pure `fusion_replay.py` module plus the mechanically normalized replay dataset, with `80/80` exact order+score parity against the historical pre-reranker fused order (`23/23` focused T0; `0` model/retrieval/Qdrant/SQL calls). P0-P5, cohorts, metrics, gates, the SemanticDense decision tree, intent-aware eligibility, and the novel corroboration gate are frozen in `phase_c_c6_a0_a1_fusion_replay_preregistration_v1.json` before any A2 relevance outcome. C6-A1R1 then corrected the A2 source population before any outcome: the authoritative 59-case formal-English scope was inherited from `phase_b_t3_product_language_scope_v2.json` (not derived from raw en/cn/mix labels; 8 raw-`mixed` pure-English cases included; all 59 map into the 80-case replay set), and the current-plan fidelity audit found `0/46` comparable cases channel-input compatible (exact concepts `46/46` changed; repository scopes `22/46` narrower under 3.7.0; 13 cases without faithful current plans), so `PLAN_FIDELITY_BLOCKED` and `C6-A2 = NOT_ELIGIBLE` (`C6_A2_POLICY_COHORT` empty; blocker recorded in `phase_c_c6_a1r1_product_scope_plan_fidelity_v1.json`; a possible `C6 candidate-coverage refresh` is recorded, not executed). The 80-case historical replay scope and the 80/80 parity remain preserved as valid historical results; production fusion is `UNCHANGED`. `C6-A3` is `PASS` (frozen production-role decision; P0 CURRENT remains production-authoritative); C7 is `NEXT_ELIGIBLE` / `NOT_STARTED`; C8 remains `NOT_STARTED`. The Phase-B T3.3A-R2/g011 blocker remains deferred to generic Phase-E coverage-aware architecture; optional T3.3B ranking debt is deferred. Phase D and Phase E remain `NOT_STARTED`.

## Current C3-A closeout — 2026-08-21

- **Artifact and provenance:** `evaluation/baselines/manifests/phase_c_c3a_raw_preserving_auxiliary_semantic_dense_v1.json`, source HEAD `687dee5d6c6f648aa7ad739f9049441628ccd811`, execution mode `luna_only`. The artifact records the revised architecture, the current resume evidence, and the historical legacy C3 status and artifacts.
- **Architecture:** `RawDense` always carries the exact original question with `user_raw` provenance and is production-authoritative. `SemanticDense` is an independent auxiliary/experimental view present only when the existing frozen `SemanticQuery.text` differs from the raw question; its provenance-aware components remain intact. Default production dense embedding/query uses RawDense and performs zero SemanticDense embedding/query calls. SemanticDense execution is explicit shadow-only and its stream is never merged into production fusion.
- **C3-A1 result:** `PASS`. Final bundled-Python in-memory direct checks passed `20/20` (`16/16` semantic contract, including the request-interleaving concurrency regression, and `4/4` trace contract, including the faithful-trace regression); AST/import checks passed `6/6` each. No external/model/Qdrant/SQL calls were made, and the existing semantic query policy was not tuned.
- **C3-A2 preflight:** The current read-only `panda_knowledge_v1` preflight was `green` with `104973` points, dense `3072`/`Cosine`, schema `4`, fingerprint `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`, and `gemini-embedding-2` in `global`; Qdrant/SQL preflight writes and index mutation were `0`. One separate minimal credential-visible `RETRIEVAL_QUERY` embedding preflight also passed with a valid 3072-dimensional result and exactly one embedding call.
- **C3-A2 result:** `PASS`. The five frozen cases (`g113,g055,g114,g115,g039`) completed in order with exact raw questions, frozen semantic texts/components, and the same per-case RetrievalPlan/filter. Each case produced separate RawDense and SemanticDense top-20 object-ID streams; overlap/raw-unique/semantic-unique were recorded as `17/3/3`, `16/4/4`, `11/9/9`, `10/10/10`, and `13/7/7` respectively. `semantic_unique_relevant_at_20` is `N/A` for all cases because no authoritative relevant-object set was available; no streams were merged and no production fusion decision was made.
- **Cost and isolation:** Credential preflight embeddings `1` in a separate call; case query embeddings `10`; case dense reads `10`; analyzer, sparse, exact, paper, workflow, graph, fusion, reranker, selector, QA/verifier/judge, SQL writes, Qdrant writes, index mutation, reindex, and document reembedding were all `0`/`no`. C3-A does not introduce AnswerPoint, coverage, Gold-derived runtime, or Phase-D/E implementation logic.
- **Resume boundary:** Static/import identity checks passed, the working tree was clean at HEAD `687dee5d6c6f648aa7ad739f9049441628ccd811`, and the authoritative case result is bound to that candidate. The prior interim safety-rejection attempt remains historical evidence only; the current result is `PASS`.
- **Current boundary:** C3-A overall and current C3 are `PASS` for the revised raw-preserving architecture. RawDense remains production-authoritative; SemanticDense is auxiliary/experimental and explicit shadow-only. SemanticDense production fusion/usefulness is `UNVALIDATED` and deferred to C6, which owns channel union, weights, intent-aware use, candidate-expansion policy, and the decision to enable or disable SemanticDense. C4 lifecycle is `CLOSED_INCONCLUSIVE` (evaluation verdict `INCONCLUSIVE` after C4-A3); its lexical view is experimental/shadow and no sparse benefit is claimed. C5 is `NEXT` eligible and `NOT_STARTED`; C6-C8 remain `NOT_STARTED`; no C5 work was authorized or begun.

## Current C4 closeout — 2026-08-22

- **Artifact and provenance:** `evaluation/baselines/manifests/phase_c_c4_lexical_query_builder_sparse_v1.json`; baseline HEAD `c258a670f91c5ca11344eb0022287f43fb2e17fe` plus the reviewed seven-file C4-A1 diff; artifact state `PREREGISTERED_NO_SPARSE_OUTCOMES`.
- **Builder contract:** The raw-first, English-only builder preserves the exact raw question and may append only accepted analyzer-supported symbols/concepts and accepted alias keys, bounded to `<=6` components and `<=32` tokens. Rejected, reviewed, fallback, hidden-metadata, Gold, and flat-plan fields are excluded; C5 lookup is not used and alias targets are not read.
- **C4-A1 result:** `PASS`. The aggregate was `54/54` (`23` lexical, `14` trace, `13` C4 evaluator, and `4` existing sparse checks); AST checks were `7/7`, import checks were `4/4`, and external/model/Qdrant/SQL calls were `0`.
- **C4-A2 preregistration:** The qualifying Gold pool was `49` before explicit exclusions and `47` after excluding `g011` and `g016`. Complete frozen plan records were `g018,g039,g040,g055,g113,g114,g115`; six were faithful C2-compatible prompt `3.7.0` records, with `g018` excluded for its semantic reconstruction mismatch. The current builder changed only `g113`: treatment-qualified was `1` among the `6` screened cases, while `40` of the `47` target-pool cases lacked plan proof and were not screenable, so the first attempt never established a `1/47` activation rate.
- **Final result and isolation:** C4-A2 and final C4 are `INCONCLUSIVE`. Because the frozen cohort was below six, no live sparse preflight, encoding, reads, rankings, or outcome metrics ran. Production sparse remains the exact raw question with a single encode/read; raw-versus-lexical shadow execution is isolated with the same non-text parameters and no fusion or downstream calls. Artifact-local writes were `1`; analyzer/Vertex, dense, live sparse, downstream, SQL/Qdrant, index mutation, reindex, and reembedding operations were `0`/not run. No sparse benefit is claimed.
- **Scope boundary:** Canonical alias/entity target resolution remains C5; `g011` remains deferred to Phase E. No novel dataset, novel generalization result, T3, T4, or T5 was run. C5-C8 remain `NOT_STARTED`; no C5 work was authorized or begun. C5 became `NEXT` eligible only later, via the C4-A3 closeout below.

## Current C4-A2R1 coverage completion — 2026-08-22

- **Artifact and provenance:** `evaluation/baselines/manifests/phase_c_c4_a2r1_frozen_plan_coverage_completion_v1.json` (companion of the original C4 artifact, which preserves the full first-attempt record); source HEAD `c0904d7ee81bb02aedf30f673da9e6bccb41b62d`.
- **Phase 1 recovery:** Exhaustive search of all manifests, bootstrap baselines, run traces, and data directories reused `0` new plans. Ten partial-plan records were rejected: nine C3-R3 stage-A cases (`g010,g021,g022,g023,g024,g034,g035,g036,g037`) whose `retrieval_plan` is null (snapshots lost after a runner error) and the historically unfaithful `g018`. Bootstrap/run-trace plans were rejected as pre-3.7.0 prompt output.
- **Phase 2 analyzer-only capture:** all `40` still-missing cases were captured through the unchanged C1 deterministic preparse -> C2 narrow analyzer (prompt `3.7.0`) -> RetrievalPlan path: `40` analyzer calls, `70,977` analyzer tokens, `0` failures, `0` repeated calls, and `0` embedding/dense/sparse/exact/paper/workflow/graph/fusion/reranker/selector/QA/verifier/judge calls. Capture stopped at RetrievalPlan creation.
- **Completed screening:** target pool `47`; valid plans `46`; missing valid plan `1` (`g018`, historical unfaithful exclusion); screened `46`; treatment-qualified `3` (`g008,g110,g113`); activation among screened `3/46` (not `3/47`, because `valid_plan_count != 47`). An independent `normalize_plan_record` + `eligibility_report` pass reproduced the same three activated cases. All appended components are `analyzer_accepted` concepts with in-question support spans; explicit identifier retention is `100%` and contamination cases are `0`.
- **Cohort decision and result:** threshold `6`; `3 < 6`, so the live sparse stage, preflight, encodes, and reads were `NOT RUN`. C4-A2R1 `INCONCLUSIVE`, C4-A2 `INCONCLUSIVE`, final C4 `INCONCLUSIVE`. Production sparse remains the exact raw question; `LexicalQuery` remains explicit shadow-only. Architectural signal: completed C2-plan screening shows low lexical augmentation activation under the current conservative C2 -> C4 contract; this is not permission to tune per-question lexical rules.
- **Cost and isolation:** SQL writes `0`; Qdrant writes `0`; index mutation `0`; reindex/sparse rebuild/dense reembedding `no`. C4 remained active at this point; it was closed by C4-A3 below.

## Current C4-A3 architectural closeout — 2026-08-22

- **Artifact and provenance:** `evaluation/baselines/manifests/phase_c_c4_a3_architectural_closeout_v1.json`; source HEAD `469904e9bbf1f0af7a452d35107caec3d12f4e88`. The artifact references and preserves both historical C4 artifacts (`phase_c_c4_lexical_query_builder_sparse_v1.json`, `phase_c_c4_a2r1_frozen_plan_coverage_completion_v1.json`); no historical verdict was rewritten.
- **Result distinction:** `C4-A3` `PASS` records only that the closeout/governance update was completed correctly. The C4 evaluation verdict remains `INCONCLUSIVE` (the proposed production LexicalQuery improvement was never validated), and the C4 lifecycle state is `CLOSED_INCONCLUSIVE` (C4 no longer remains an active roadmap blocker). `CLOSED_INCONCLUSIVE` is intentionally neither `C4 = PASS` nor `C4 = FAIL`.
- **Why closed:** C4 exhausted its reasonable blind evaluation path. After the complete 46-case screening produced only `3` treatment-qualified cases (`3/46` activation, below the preregistered six), any threshold reduction or builder modification would be post-hoc and outcome-aware. The evidence indicates low augmentation applicability under the conservative C2 -> C4 contract — not proven sparse harm and not proven benefit; no sparse ranking was ever observed and no Recall/MRR claim may be made.
- **Production decision:** production sparse remains the exact raw question (`lexical_query_production_activation = false`). `LexicalQuery` is retained (`experimental/shadow`, auditable, provenance-preserving) for future architectural experiments and C5/C6 diagnostics.
- **Sampling and tuning boundary:** further C4 sampling under the current strategy is closed (no C4-A2R2/R3, treatment search, Gold sample, or frozen-plan completion round); minimum treatment cases remain `6`; builder tuning from the exposed Gold pool and benchmark-specific lexical rules are prohibited.
- **Reopen rule:** reopening requires a genuinely new explicitly authorized upstream capability or architecture change (for example a future C5 entity resolver exposing generic canonical lexical forms); it must not be triggered by more Gold questions, the inconvenient `3/46` result, or a desire for `PASS`.
- **C5 dependency correction:** the previous rule "C5 is not eligible while C4 remains INCONCLUSIVE" no longer applies. `C4 CLOSED_INCONCLUSIVE -> C5 is the next eligible roadmap task`, because C5 owns a distinct capability (entity-first exact retrieval, canonical entity/symbol resolution) that C4 did not own and does not depend on C4 proving LexicalQuery production benefit. C5 is `NEXT_ELIGIBLE` and `NOT_STARTED`; C5/C6 ownership boundaries are unchanged; Phase D/E remain `NOT_STARTED` and `g011` stays deferred to Phase E.
- **Cost and isolation:** analyzer/Vertex/dense/sparse/exact/paper/workflow/graph/fusion/reranker/selector/QA/verifier/judge calls all `0`; SQL/Qdrant writes `0`; index mutation `0`; reindex/reembedding `no`; production code changes `0`; writes limited to the closeout artifact and the two governance documents.

## Current C5 closeout — 2026-08-22

- **Artifact and provenance:** `evaluation/baselines/manifests/phase_c_c5_entity_first_exact_retrieval_v1.json`; source HEAD `db4edfb7835802e6af3f69e11bf32fc9a9cb3cc5` plus the reviewed C5 diff (`src/panda_agent/entity_resolution.py`, `src/panda_agent/retrieval.py` shadow method, `tests/unit/test_entity_resolution.py`). Historical C4 artifacts were not modified.
- **C5-A0 inventory:** `2` accepted aliases (`*_pid_final.root`, `restgas_profile.txt`, both single-target, locked-version, no dangling or multi-target groups); `133,075` objects with every target repository at exactly one locked version; exact fields `object_id/title/canonical_locator/locator.path/locator.symbol` fully populated; existing English GIN FTS + `lower(title)` indexes reused (pg_trgm deliberately not installed); relation predicates contain no identity/equivalence semantics, so `relation_identity_resolution = NOT_AVAILABLE` (Phase D owns richer relations).
- **C5-A1 result:** `PASS`. Entity-resolution contract: `EntityMention/EntityCandidate/EntityResolution/EntityResolutionReceipt` with explicit statuses (`RESOLVED_UNIQUE/RESOLVED_MULTIPLE/AMBIGUOUS/UNRESOLVED/REJECTED_VERSION/REJECTED_SCOPE/MISSING_TARGET`), boundary-safe deterministic alias matching (no substring false positives, stable whitespace, case-insensitive, no glob broadening), deterministic exact priority (`accepted_alias > exact_symbol > exact_title > exact_path`), locked-version and source-scope validation, forbidden provenance structurally excluded (reviewed expansions, rejected analyzer items, flat plan fields, Gold metadata), ambiguity never silently resolved, legacy fallback preserved, and `Retriever.shadow_exact(question, plan)` shadow-only with production `_exact()` untouched. `63/63` focused T0 (27 new C5 tests + C4 boundary regressions); external/model/Qdrant calls `0`. One pre-preregistration implementation smoke (`g023`) is disclosed in the artifact.
- **C5-A2 preregistration and screening:** frozen before any A/B outcome over the `46` faithful C4-A2R1 plans (analyzer rerun `0`). Mention-layer screening qualified `39` cases, all `EXPLICIT_IDENTIFIER`; `0` `DESCRIPTIVE_OR_ALIAS` because neither accepted alias occurs whole in any locked English question. Cohort frozen at `12` explicit cases (`g001-g006,g008-g010,g013-g015`).
- **Exact-only A/B (diagnostics under the below-minimum-descriptive rule):** `55` read-only exact SQL reads with a no-write assertion. Recall@5 `0.25 -> 0.25`, Recall@10 `0.3333 -> 0.3333`, Recall@20 `0.3333 -> 0.3333`, MRR `0.2222 -> 0.1369`, critical coverage `0.3333 -> 0.3333`; classification: improved `0`, recovered `0`, unchanged `1`, no_hit_both `8`, regressed `3`, lost_hit `0`; new critical misses `0`. Entity-resolution safety: unique `10`, ambiguous/multiple `1`, unresolved `5`, alias resolutions `0`, version violations `0`, out-of-scope promotions `0`, false resolutions `0`, false unique-from-ambiguous `0`, fallback used `2`, canonical targets present@5/@10 `10/10`.
- **MRR decrease explanation:** the unique title match for the product name `PandaRoot` resolves the repository Readme object and the entity-first prefix places it at rank `1` in `10/12` cases, displacing previously rank-1 Gold evidence to rank `2` (g003/g004 MRR `1.0 -> 0.5`; g005 rank `6 -> 7`). The resolution is correct; the signal is that unique canonical resolution of generic product-name mentions is not a retrieval-valuable rank-1 promotion. No ranking rule was changed in response.
- **Gate ledger and result:** gates `3` (descriptive/alias `>= 2`) and `14` (descriptive improvement) FAIL; all other 14 gates PASS. C5-A2 `INCONCLUSIVE`, Final C5 `INCONCLUSIVE`. Production exact remains `LEGACY_EXACT`; the entity-first path remains available through the explicit shadow method. Architectural signals: descriptive-resolution evidence requires the Phase-D systematic alias migration (C5 may not create aliases), and future production activation needs an explicit ordering policy for generic-entity prefixes.
- **Cost and isolation:** analyzer/Vertex/embedding calls `0`; dense/sparse/paper/workflow/graph/fusion/reranker/selector/QA/verifier/judge `0`; Qdrant reads/writes `0`; SQL writes `0` (asserted); index mutation `0`; reindex/reembedding `no`. At this point C5 remained active; it was closed by C5-A3 below.

## Current C5-A3 architectural closeout — 2026-08-22

- **Artifact and provenance:** `evaluation/baselines/manifests/phase_c_c5_a3_architectural_closeout_identity_strength_v1.json`; source HEAD `08a43f944b247da4447d83a4b32e0ff34bf6ebca`. The historical C5 evaluation artifact is referenced and preserved unchanged; no historical C5-A0/A1/A2 result was rewritten.
- **Result distinction:** `C5-A3` `PASS` records only that this architectural/governance closeout was completed correctly. The C5 evaluation verdict remains `INCONCLUSIVE`; the C5 lifecycle state becomes `CLOSED_INCONCLUSIVE` — intentionally neither `C5 = PASS` nor `C5 = FAIL`. `C5-A1` remains `PASS` under its original preregistered contract and is not retroactively failed; the post-evaluation architecture finding is that the original canonicality contract was too permissive for weak identity evidence.
- **Closeout blockers recorded:** (A) descriptive-resolution evidence is `UNAVAILABLE` (2 accepted aliases in the corpus, 0 descriptive evaluation cases; creating aliases from the exposed Gold pool is benchmark fitting and prohibited). (B) identity strength is underspecified: a unique exact database match is not sufficient evidence for unconditional canonical-prefix promotion.
- **Identity-strength finding (authoritative):** exact-match uniqueness alone is insufficient evidence of canonical entity identity for all object types — exact title, path basename, and generic repository/product/document names may identify a relevant object without proving the object is the canonical entity representation intended by the mention. Conceptual boundary recorded for future work: `STRONG_IDENTITY_EVIDENCE` (validated accepted-alias target, symbol-carrying exact locator.symbol match, future canonical entity records, unambiguous identity relations, Phase-D entity infrastructure) versus `WEAK_RETRIEVAL_MATCH` (exact title, path basename, generic repository/product name, README/document/page titles, same-named documentation objects). Weak matches may be useful candidates but must not automatically imply canonical identity or unconditional rank-1 promotion. This distinction is governance documentation only — **no code change implemented it**.
- **PandaRoot diagnostic interpretation:** the resolution of the mention `PandaRoot` to the repository README via unique exact-title match was syntactically/database-correct and stays `RESOLVED_UNIQUE`; the README title match was nevertheless not sufficient evidence for unconditional canonical prefix promotion, and the MRR regression (`0.2222 -> 0.1369`, 3 regressions) is preserved as architecture evidence. No PandaRoot-specific rule, README suppression, title demotion, repository-name special case, or any other outcome-driven patch was introduced.
- **Canonical-locator finding (secondary):** `canonical_locator` semantics are `DEFERRED_FOR_GENERIC_REVIEW`; the resolver was not modified, and the existence of the field must not be read as every value being an entity identity key.
- **Boundary:** further C5 evaluation under the current resolver/data contract is `CLOSED` (no C5-A2R1/R2, no new exact cohort, Gold sample, alias-treatment search, or same-cohort rerun after ranking adjustment); descriptive/alias minimum stays `2`; no new aliases; no post-hoc gate changes; resolver/merge/shadow/production-exact code frozen unchanged. Reactivation depends primarily on Phase-D generic entity infrastructure (systematic aliases, canonical entity records, explicit identity semantics, an independently designed identity-strength policy, or new independently-authored descriptive evaluation data); reopening merely because Gold cases exist, the result is INCONCLUSIVE, MRR decreased, a PASS is desired, or the PandaRoot case looks tunable is prohibited.
- **Production decision:** production exact remains `LEGACY_EXACT` (entity-first activation rejected: descriptive evidence absent; no improvement and three regressions; identity-strength contract needs future refinement; production benefit not established). `EntityResolver`/`shadow_exact` retained as experimental/shadow reusable foundations.
- **C6 dependency correction:** `C5 CLOSED_INCONCLUSIVE -> C6 NEXT_ELIGIBLE`. C6 evaluates the currently valid production channels (`exact = LEGACY_EXACT`, RawDense production-authoritative, SemanticDense auxiliary/shadow, sparse raw-question, paper, workflow, graph) and does not require EntityFirstExact to be production-authoritative. C6 ownership (fusion, channel inclusion/weights, SemanticDense production decision, intent-aware activation, candidate union) is unchanged; C5-A3 made no fusion decision. C4 remains `CLOSED_INCONCLUSIVE`; Phase D/E remain `NOT_STARTED`; `g011` remains Phase E.
- **Cost and isolation:** analyzer/Vertex/embeddings/exact SQL/dense/sparse/paper/workflow/graph/fusion/reranker/selector/QA/verifier/judge all `0`; SQL/Qdrant reads and writes `0`; index mutation `0`; schema migration/reindex/reembedding `no`; production code changes `0`. C6-C8 remain `NOT_STARTED`; Phase D/E remain `NOT_STARTED`; `g011` remains Phase E.

## Current C6-A0/A1 — 2026-08-22

- **Artifacts:** preregistration `evaluation/baselines/manifests/phase_c_c6_a0_a1_fusion_replay_preregistration_v1.json`; normalized replay data `evaluation/baselines/replay/phase_c_c6_frozen_channel_replay_v1.jsonl`; replay module `src/panda_agent/fusion_replay.py` + `tests/unit/test_fusion_replay.py`. Source HEAD `dfc4ff8541cab3c88f544216658fa6da0a69f24b`.
- **A0 result: `PASS` (coverage state `COVERAGE_READY`).** All frozen candidate sources inventoried read-only. Core source: `phase-b-t3-retrieval-20260816` (80 dev cases; per-case `channel_candidates` with object_id/rank/score/channels/source/version/locator plus the recorded pre-reranker fused order). Missing vs empty vs skipped vs invalid explicitly distinguished: paper absent-key records `PRESENT_EMPTY` (production always executes `_paper` and omits only empty results); semantic_dense is `MISSING_NOT_CAPTURED` for the 75 cases never captured and `PRESENT_NONEMPTY` for the 5 C3-A resume cases whose raw streams were verified object-identical to the t3 dense streams (cross-run combination justified without guessing). Coverage: exact 77/3, raw_dense 80/0, sparse 79/1, paper 20/60, workflow 68/12, graph 74/6 (nonempty/empty). Cohorts: CORE 80, SEMANTIC 5 (`g039,g055,g113,g114,g115`), INTENT_DIAGNOSTIC 80 (all 8 intents at >=4: api 15, usage 14, algorithm_implementation 12, installation 11, data_flow 10, algorithm_theory 8, troubleshooting 6, module_structure 4), NOVEL `ABSENT` (no committed novel dataset exists).
- **A1 result: `PASS`.** Production fusion identity recorded from source: application-side weighted RRF `weight/(60+1-based rank)`, weights exact 2.0/dense 1.0/sparse 1.0/paper 1.15/workflow 1.2/graph 0.8, object_id dedup, stable insertion-order ties, semantic_dense absent from production. The pure evaluation-only replay module reproduces CURRENT exactly: `80/80` parity-eligible cases match the historical fused order and recorded fusion scores (cross-checks: b5-pre 16/16, b5-post 16/16, a3-stratified 24/24). Focused T0 `23/23` with `0` model/retrieval calls.
- **Preregistration frozen before any A2 outcome:** P0 `c6.current.v1`, P1 `c6.raw_dense_centered.v1` (raw_dense x1.5), P2 `c6.exact_heavy.v1` (exact x1.5), P3 `c6.sparse_heavy.v1` (sparse x1.5), P4 `c6.semantic_aux25.v1` (dense-family total preserved: raw_dense 0.75/semantic 0.25), P5 `c6.semantic_expansion_only.v1` (CURRENT scoring unchanged; semantic unique candidates into an explicit expansion pool). Cohort rules (core max 30 by intent round-robin + case ID, minimum 12; semantic up to 20, minimum 8 and >=2 intents), the A2 metric set, the 10 global safety gates, the SemanticDense decision tree (`N_sem >= 8` and `semantic_unique_relevant_case_count >= max(2, ceil(0.10*N_sem))`), intent-aware eligibility (>=3 sufficiently represented intents, >=4 cases each, deterministic mapping only to preregistered policies), and the novel corroboration gate (`NEW_PRODUCTION_POLICY_ACTIVATION = NOT_AUTHORIZED_BY_C6_A2_ALONE` while novel data is `ABSENT`) are all frozen.
- **A2 eligibility: `ELIGIBLE`** (A0 PASS, A1 PASS, 80 >= 12 core cases, replay fidelity proven). `semantic_a2_evidence_eligible = false` (5 < 8): A2 may evaluate core policies but must not make a substantive SemanticDense production claim, which defaults to `EVIDENCE_INSUFFICIENT`.
- **Production behavior: `UNCHANGED`.** `fusion_replay.py` is evaluation-only and not imported by production retrieval; no weights, channels, limits, or builders changed.
- **Cost and isolation:** analyzer/Vertex/embeddings/live exact/dense/sparse/paper/workflow/graph/reranker/selector/QA/verifier/judge all `0`; Qdrant reads/writes `0`; SQL writes `0`; index mutation `0`; schema migration/reindex/reembedding `no`; repository file reads only.

## Current C6-A1R1 — 2026-08-22

- **Artifacts:** correction artifact `evaluation/baselines/manifests/phase_c_c6_a1r1_product_scope_plan_fidelity_v1.json`; normalized scope file `evaluation/baselines/replay/phase_c_c6_a2_product_scope_v1.json`. Source HEAD `51de55f6192e7f835cab633c88ee6346e83bff8d`; the original C6-A0/A1 preregistration artifact is preserved unchanged (this correction additively supersedes only the C6-A2 source-population/provenance-eligibility clauses).
- **Timing:** before any C6-A2 relevance outcome (A2 was never executed; no Recall/MRR/critical/policy-winner value was computed or inspected in this task).
- **Part A — formal-English scope inheritance:** the authoritative 59-case scope is `phase_b_t3_product_language_scope_v2.json` (calibration of the exact 80 Phase-B T3 development questions against Gold v2.6, natural-language-grammar rule, 9 reviewed overrides, reviewed 2026-08-16 — predating C6-A2 and bound to the same source run as the frozen replay set). Verification: count `59`; all 59 IDs exist in the 80-case historical replay set (`missing = 0`); formal-English (59) and non-English (21) partition the 80 exactly. Raw language metadata is diagnostic only — 80-case distribution `en 51 / zh 20 / mixed 9`; 59-case distribution `en 51 / mixed 8` — and was NOT used as the product filter: 8 raw-`mixed` pure-English questions are inside the inherited scope, `mix` was not globally excluded, and no new language adjudication was performed.
- **Historical replay preservation:** `HISTORICAL_REPLAY_SCOPE = 80` unchanged; `phase_c_c6_frozen_channel_replay_v1.jsonl` untouched; the `80/80` CURRENT replay parity and `23/23` T0 remain valid historical A1 results (they prove faithful replay of the historical fusion). Distinct scopes are now explicit: HISTORICAL_REPLAY_SCOPE `80` / FORMAL_ENGLISH_PRODUCT_SCOPE `59` / CURRENT_PLAN_COMPATIBLE_PRODUCT_SCOPE `0` / C6_A2_POLICY_COHORT `0` / SEMANTIC_A2_POLICY_COHORT `0`.
- **Part B — current-plan fidelity audit:** current 3.7.0 plans were taken only from faithful frozen sources (C4-A2R1's 40 analyzer-only captures plus the 6 faithful C4 records; g018 excluded; analyzer rerun `0`). A static channel-input dependency map was derived from `retrieval.py` source (exact consumes question/symbols/concepts/resolved_aliases/target_repositories/resolved_versions/required_source_types; raw_dense and sparse consume the exact raw question plus the repository/version filter; paper consumes the question vector, the `paper` source-type gate, and page hints; workflow consumes question regex terms plus the scope filter and `workflow` fallback gate; graph consumes the exact/dense/sparse seeds plus scope filter and `graph` fallback gate; diagnostic-only fields are not dependencies). Comparing only those consumed fields plus exact question text: `46` formal-English cases have current plans, `0` are channel-input compatible — exact-channel concepts differ on `46/46` (the C2 3.7.0 additive-delta contract reconstructs concepts differently), `plan.target_repositories` differs on `22/46` (3.7.0 accepts analyzer repository additions only with explicit query grounding, so current plans target fewer repositories, e.g. g021 `3->2`, g022 `2->1`), `required_source_types` on `6`, paper hints on `1`; `13` cases (including g011/g016) have no faithful current plan; question text is identical on every compared case. Per-channel: exact compatible `0/46`; raw_dense/sparse/workflow/graph identical `24`, material `22`; paper identical `40`, material `6`.
- **Interpretation:** `PLAN_FIDELITY_BLOCKED` — `0 < 12` minimum. The frozen 3.6.0-era candidate streams faithfully replay the historical fusion but are not structurally representative of current 3.7.0 RetrievalPlan inputs, so they cannot support a formal CURRENT-product C6-A2 policy comparison.
- **Corrected A2 population and cohort:** compatible formal-English scope `0`; the unchanged frozen round-robin selection over that population yields an empty `C6_A2_POLICY_COHORT` (no relevance information was used). Intent distributions recorded for all four scopes (59-case: api 15, usage 14, installation 11, algorithm_theory 8, troubleshooting 6, algorithm_implementation 2, module_structure 2, data_flow 1; compatible and cohort distributions are empty). Semantic cohort: historical `5` (`g039,g055,g113,g114,g115`) -> formal-English `5` -> current-plan-compatible `0`; `semantic_a2_evidence_eligible = false` (>=8/>=2-intent gate unchanged, derived mechanically).
- **Preregistration preservation:** P0-P5, weights, RRF K, metrics, the 10 safety gates, the SemanticDense decision tree, intent-aware eligibility/construction, and the novel gate (`novel_replay_status = ABSENT`; `NEW_PRODUCTION_POLICY_ACTIVATION` not authorized by A2 alone) are all unchanged.
- **Result:** `C6-A1R1` `PASS` as a methodologically valid audit; `C6-A2` execution eligibility `NOT_ELIGIBLE` with blocker `insufficient current-plan-compatible formal-English frozen candidates` (0 compatible < 12; 46 comparable but all materially changed, 13 without current plans). A possible future `C6 candidate-coverage refresh` (separately authorized, minimum current formal-English cohort only) is recorded, not executed. Production behavior `UNCHANGED` (fusion/exact/sparse/RawDense/SemanticDense untouched).
- **Cost and isolation:** analyzer/Vertex/embeddings/live retrieval of any channel/reranker/selector/QA/verifier/judge all `0`; PostgreSQL candidate reads `0`; Qdrant reads/writes `0`; SQL writes `0`; index mutation `0`; reindex/reembedding `no`; repository file reads only.
- **Provenance preflight audit — 2026-08-22 (FAIL):** a static/offline audit (amended into the A1R2 manifest as `provenance_preflight_audit`, source HEAD `f6e1b5d`) found that the minimal-plan compatibility issue did NOT concern `source_budgets` only. The six C4 minimal records (`g039,g040,g055,g113,g114,g115`) lack `target_repositories`, `resolved_versions`, `symbols`, `concepts`, and `required_source_types`, and the A1R2 preparation validated them to empty defaults (`required_source_types=[]` hardcoded) instead of using the faithful full values that exist for the same cases in the C3-R3 artifact. Three captured core cases are affected (`g113,g114,g115`): their exact/raw_dense/sparse/workflow/graph/semantic streams are invalid (exact terms degraded to the regex fallback; dense/sparse lost the version/source filter; workflow/graph lost the repository scope), while paper is behavior-equivalent by coincidence and the semantic activation screen is unaffected (`analysis_diagnostics` was faithful). `source_budgets` itself is benign: it is intent-policy-owned (`configs/retrieval_policies.yaml`), numerically equivalent when borrowed from a same-intent plan, consumed only by final-evidence selection (`select_final_evidence`), and absent from all six capture channels and the P0 fusion replay. Consequence: `C6-A2 = NOT_ELIGIBLE` pending a separately authorized provenance repair (re-prepare the three cases' plans from the C3-R3 faithful full plans and recapture only those frozen cases); the audit performed no repair, no recapture, and no live call; the A1R2 capture results and P0 integrity remain valid historical records of what was executed.
- **Provenance repair — 2026-08-22 (`phase_c_c6_a1r2_provenance_repair_v1.json`, source HEAD `790d918`):** `PASS`. All six affected cases were repaired from the faithful C3-R3 full plans (guard-validated explicit field presence; question text verified identical to Gold v2.6; `source_budgets` derived from the current versioned intent policy, which equals the recorded values — no same-intent copying). Capture identity gate: `MATCH`. Live recapture of all six cases completed all six production channels plus semantic where structurally active (embeddings `11` = 6 raw + 5 semantic, sparse encodes `6`, Qdrant reads `20`, read-only-asserted SQL reads `80`; analyzer/reranker/QA generation `0`). A semantic-activation discrepancy was recorded and explained: the faithful full plans additionally activate `g039/g055/g114/g115` (5/6) because the minimal records had lacked `deterministic_parse.fixed.concept_scopes`; no threshold or core-cohort change resulted. Authoritative replay v2 (`phase_c_c6_current_plan_candidate_replay_v2.jsonl`, 34 rows = 28 unchanged v1 rows + repaired `g113/g114/g115` in place + supplemental `g039/g040/g055` appended) verified: 28/28 reused rows unchanged, original 30-case core identical, supplemental excluded from the A2 core, P0 core integrity `30/30`, unaffected-core P0 parity `27/27`, no Gold/relevance fields. Semantic A2 cohort within the original live cohort is now `6` (`g008,g050,g110,g113,g114,g115`, 3 intents) — still `< 8`, so `semantic_a2_evidence_eligible=false` unchanged. A fail-fast executable-plan guard (`evaluation/scripts/plan_provenance.py`) now protects the evaluation capture path. `C6-A1R2` current authoritative verdict: `PASS_AFTER_PROVENANCE_REPAIR` (the historical FAIL audit record is preserved); `C6-A2 = ELIGIBLE / NOT_STARTED`; production behavior `UNCHANGED`.

## Current C6-A1R2 — 2026-08-22

- **Artifacts:** `evaluation/baselines/manifests/phase_c_c6_a1r2_current_plan_candidate_coverage_v1.json` (pre-capture preregistration persisted before any retrieval); new frozen dataset `evaluation/baselines/replay/phase_c_c6_current_plan_candidate_replay_v1.jsonl`; evaluation-only capture script `evaluation/scripts/capture_c6_current_plan_candidates.py`. Source HEAD `3b450cc43d88581040116b9411acc337f0dda1d8`. Historical artifacts (`phase_c_c6_a0_a1_…`, `phase_c_c6_a1r1_…`, `phase_c_c6_frozen_channel_replay_v1.jsonl`, `phase_b_t3_product_language_scope_v2.json`) preserved unchanged.
- **Frozen cohorts (before any live retrieval):** `CURRENT_PLAN_CAPTURE_POOL` `46` (the A1R1 cases with faithful 3.7.0 plans); `CORE_CAPTURE_COHORT` `30` via the unchanged A1 round-robin algorithm (installation 6, usage 6, algorithm_theory 5, algorithm_implementation 2, api 5, module_structure 1, troubleshooting 5); structural SemanticDense screen via pure `build_semantic_query` found only `4/46` semantic-active cases (the conservative C2 additive-delta contract rarely changes the query text); `SEMANTIC_SUPPLEMENT_COHORT` `[g008]` (the only remaining active case; the >=8 threshold is unreachable from the pool); `LIVE_CAPTURE_COHORT` `31` (max 38 respected).
- **Capture identity:** locked repositories luminosityfit `ddd83dc…` / pandaroot `18c09e9…` / restgas_determination `11f1edc…` matching the frozen plans; `panda_knowledge_v1` with `104973` points, dense `3072/Cosine`, sparse `sparse/idf`, index fingerprint `8172f9…`, `gemini-embedding-2`, sparse receipt `Qdrant/bm25 english idf fastembed 0.7.4`, `candidate_pool_per_channel = 20`.
- **Capture execution:** `31/31 CAPTURE_COMPLETE`, `0` failures, no case replaced. Per-channel availability: exact `27/4`, raw_dense `31/0`, sparse `31/0`, paper `7/24`, workflow `25/6`, graph `24/7` (nonempty/empty; every executed empty is authoritative), semantic_dense `4 PRESENT_NONEMPTY` + `27 SKIPPED_BY_PLAN (semantic_view_inactive)`. Live ledger: RawDense embeddings `31`, SemanticDense embeddings `4`, sparse encodes `31`, Qdrant reads `87`, read-only-asserted SQL reads `282`, SQL/Qdrant writes `0`, analyzer/reranker/QA generation `0`. `analyze()`/`retrieve()`/reranker/selector were never invoked (explicit frozen plans only).
- **Dataset integrity:** static banned-field scan clean (no relevance/evidence/answer-requirement/Gold fields); candidate identity = `object_id` (production semantics); ranks 1-based deterministic.
- **P0 replay integrity:** `30/30` core cases pass deterministic repeated replay, contribution-sum validation, no-unavailable-channel contribution, `semantic_dense` weight/contribution `0` under `c6.current.v1`, and object_id dedup preservation.
- **Semantic derivation:** `SEMANTIC_A2_POLICY_COHORT = [g008, g050, g110, g113]` over `3` intents — `semantic_a2_evidence_eligible = false` (`4 < 8`; threshold unchanged); no SemanticDense production decision made (A2 evaluates relevance first, A3 decides).
- **Result:** `C6-A1R2` `PASS`; `C6-A2` execution eligibility `ELIGIBLE` (core frozen before outcomes; all core cases complete on six channels; faithful 3.7 plans; coherent identity; no Gold; P0 integrity `100%`; core `30 >= 12`). `PLAN_FIDELITY_BLOCKED` remains true for reuse of the old 3.6 streams and is resolved for the newly captured cohort because current 3.7 streams were newly captured. Production behavior `UNCHANGED`; `C6-A3` `NOT_STARTED`.
- **Semantic-cohort eligibility correction — 2026-08-22 (`phase_c_c6_a1r2_semantic_cohort_correction_v1.json`, source HEAD `4d1f71d`):** static cohort correction only; the provenance repair itself remains `PASS` and replay v2 remains authoritative, and the global 30-case A2 core is unchanged (g039/g040/g055 were NOT added to the P0-P3 core). The previous six-case Semantic cohort (`g008,g050,g110,g113,g114,g115`, `semantic_a2_evidence_eligible=false`) was undercounted because the repair verification (`repair_c6_a1r2_build_v2.py` verification 5) accidentally constrained semantic eligibility to the original A1R2 live-capture cohort and excluded `row_role=supplemental_coverage` — both conditions of global-core bookkeeping that the original C6-A1 preregistered Semantic Policy Cohort rule does not contain ("all SEMANTIC_REPLAY cases up to 20, deterministic by intent + case ID", min `8` cases / `2` intents, with an explicit allowance for a separately authorized candidate-coverage task to expand the frozen semantic cohort; A1R2 refresh + provenance repair was such a task). Re-derivation from replay v2 under the structural rule (formal-English scope, faithful 3.7.0 plan provenance, `semantic_view_active=true`, execution `OK`, semantic availability `PRESENT_*`, all six production channels `PRESENT_*`, identity gate `MATCH`, pre-A2 timing, no relevance data) yields `SEMANTIC_A2_POLICY_COHORT = [g050, g055, g039, g008, g110, g113, g114, g115]` (deterministic intent-ascending + case-ID order; distribution troubleshooting 4 / algorithm_theory 2 / api 1 / installation 1; `4` represented intents) — count `8 >= 8` and intents `4 >= 2`, so `semantic_a2_evidence_eligible = true`. `g040` remains excluded because its semantic view is structurally inactive (`semantic_view_active=false`, `SKIPPED_BY_PLAN`, `skip_reason=semantic_view_inactive`), independent of its supplemental status. This authorizes only substantive P4/P5 evaluation coverage in A2 — no SemanticDense benefit is claimed, `novel_replay_status=ABSENT` stands, and `global_policy_evidence_eligible=true` / `semantic_policy_evidence_eligible=true`. Cost: static/deterministic only (analyzer/embeddings/sparse/Qdrant/SQL/reranker/selector/QA/judge all `0`; recaptures `0`; relevance outcomes inspected `0`); historical artifacts preserved; no `C6-A1R3` created — this remains a C6-A1R2 preregistration/eligibility correction.

## Current C6-A2 — 2026-08-22

- **Artifacts:** `evaluation/baselines/manifests/phase_c_c6_a2_frozen_fusion_policy_comparison_v1.json` (pre-outcome lock persisted before any relevance computation, then results); per-case receipts `evaluation/baselines/replay/phase_c_c6_a2_policy_receipts_v1.jsonl` (`144` rows = 30x4 global + 8x3 semantic, each with first-relevant-rank, hit@5/10/20, per-group first ranks, critical status, direction vs P0, fused top-20 IDs; P5 rows add the annotated expansion pool); evaluation-only script `evaluation/scripts/evaluate_c6_a2_fusion_policies.py`. Source HEAD `f3229b30fb87d1f674e347c5e7d02faef7a53392`. First and only C6-A2 relevance evaluation.
- **Pre-outcome input lock:** replay v2 authoritative (34 rows, unchanged); frozen global cohort = the original 30 core IDs from the committed A1R2 coverage manifest; semantic cohort = the corrected 8-case cohort `[g050, g055, g039, g008, g110, g113, g114, g115]`; code `preregistered_policies()` verified equal to the A1 artifact (P0-P5 weights/channels/modes, RRF `K=60`, `object_id` identity); Gold v2.6 (`gold_questions.yaml`, sha256 recorded; all 33 evaluated cases verified `answered` dev questions with identical question text; g010's frozen `usage` label is a Gold `accepted_intent`); relevance matcher = `panda_agent.evaluation._matched_evidence_groups` with `GoldEvidenceSelector` direct/ancestor/path-containment tiers — the C3-R3-frozen authoritative required-evidence-group semantics that produced the trusted Gold v2.6 Recall/MRR/critical metrics; object lookup = the evaluator-canonical normalized `knowledge_objects.jsonl` (`133,075` objects, selection rule identical to `load_object_lookup`; `0` replay candidates missing; `0` SQL calls).
- **Global P0-P3 (30 cases, frozen intent labels):** P0 CURRENT: R@5 `0.7222`, R@10 `0.8444`, R@20 `0.9667`, MRR `0.5679`, critical `0.9667`, combined candidate recall@20 `1.0`. P1 raw_dense x1.5: R@10 `0.8611` but `FAIL_HARD_GATES` on gates 5/6/7 (`1` lost_hit, one new critical miss, 6 negative vs 5 positive). P2 exact x1.5: `FAIL_HARD_GATES` on gates 3/5/7 (R@20 `0.9556 < 0.9667`). **P3 sparse x1.5 passes all 10 hard gates** — R@10 `0.8611`, R@20 `1.0` (the one P0 critical miss recovered), MRR `0.6013` (`+0.0334`), critical `1.0`, lost_hit `0`, 5 positive = 5 negative (gate 7 is `<=`), R@5 `0.7167` (`-0.0056`, diagnostic only — MRR/Recall@5 diagnostics reported as raw deltas, no post-outcome threshold invented). Global passing set = `{P3_SPARSE_HEAVY}`; CURRENT is therefore not undominated under hard-gate evidence; no composite winner was invented and P3 remains an A3 decision candidate only.
- **Semantic P0/P4/P5 (same 8 cases, apples-to-apples):** P0-on-8 baseline: R@10 `0.875`, R@20 `1.0`, MRR `0.5387`. P4 SEMANTIC_AUXILIARY_25: `FAIL_HARD_GATES` (gates 3/5/7 — R@20 `0.9375 < 1.0`, one new critical miss, 1 regressed vs 0 improved). P5: `SCORED_PREFIX_IDENTITY = PASS` 8/8 (fused order and scores identical to P0) and `EXPANSION_CONTRIBUTION = NOT_MEANINGFUL` — 41 expansion candidates across the 8 cases, only 1 relevant (g114), and the semantic marginal candidate-recall contribution is `0.0` on every case (that group is already covered by production channels).
- **SemanticDense contribution:** semantic/raw overlap@20 10-17 per case; unique semantic candidates 3-8 per case; `semantic_unique_relevant_case_count = 1 < max(2, ceil(0.10*8)) = 2` → `meaningful_semantic_marginal_recall = false`; `SEMANTIC_CONTRIBUTION = INSUFFICIENT`; weighted participation `NOT_SUPPORTED`; expansion-only `NOT_SUPPORTED`; semantic production-role evidence = `KEEP_DISABLED`.
- **Intent-aware:** sufficiently represented intents (>=4 of 30): installation `6`, usage `6`, algorithm_theory `5`, api `5`, troubleshooting `5`. All six preregistered conditions satisfied → `INTENT_AWARE_ELIGIBLE = true`; evaluation-only mapping `C6_INTENT_AWARE_V1`: installation→`P3_SPARSE_HEAVY` (intent R@10 `0.667->0.833`, MRR `0.536->0.702`, 3 positive/0 negative), troubleshooting→`P2_EXACT_HEAVY` (intent R@10 `0.8->1.0`, 2 positive/0 negative), algorithm_theory/api/usage→CURRENT (api's P3 and algorithm_theory's P1 fail the positive>negative condition 5); low-count intents map to CURRENT. P2 remains a globally failing policy — the troubleshooting preference is intent-level evidence for A3, not a global activation.
- **Authorization boundary:** novel gate `ABSENT`; `NEW_PRODUCTION_POLICY_ACTIVATION = NOT_AUTHORIZED_BY_C6_A2_ALONE`; no production policy activated; production fusion/exact/sparse/dense `UNCHANGED` (exact `LEGACY_EXACT`, sparse raw question, RawDense production-authoritative, SemanticDense auxiliary/shadow). Selection-layer debt not assessed (no reranker/selector execution; C7/C8 own downstream layers).
- **Verification:** aggregates rebuilt from receipts match the manifest; outcome gates 3-7 recomputed independently from receipts and consistent; P5 prefix 8/8; every policy replay double-applied with identical receipts; replay v2 byte-unchanged; no live-call imports in the evaluation path; `git diff --check` clean.
- **Cost and isolation:** analyzer/embeddings/sparse encodes/live retrieval of any channel/Qdrant reads/SQL candidate reads/reranker/selector/QA/verifier/judge all `0`; SQL/Qdrant writes `0`; index mutation `0`; the authorized Gold-file read is the only evaluation-external data access; repository file reads only.
- **Result:** `C6-A2` `PASS` — methodological integrity held (frozen inputs valid, authoritative matcher reused, both cohorts evaluated exactly as preregistered, deterministic outputs, no methodology violation); policy performance is decision evidence for A3, not the A2 verdict. `C6-A3` `NEXT_ELIGIBLE / NOT_STARTED`.
- **Critical-miss semantics audit — 2026-08-22 (`phase_c_c6_a2_critical_miss_semantics_audit_v1.json`, source HEAD `83db6bb`, evaluation-only script `evaluation/scripts/audit_c6_a2_critical_miss_semantics.py`):** `PASS`. The original A2 execution remains the first and only relevance evaluation; post-A2 review found hard Gate 5 had been implemented as aggregate critical-coverage decline (`policy critical_evidence_coverage < P0`), which can miss a critical-group swap (coverage equal while a specific P0-hit critical group is lost). The static group-level audit recomputed Gate 5 from the frozen receipts' `group_first_ranks` plus Gold v2.6 `required_evidence_groups[*].critical` (exact group IDs, TOP_K=20, no fusion/retrieval rerun): a new critical miss is now defined as a P0-hit critical group the policy loses, with recovered groups recorded separately and never cancelling losses. Result: **no `OLD_FALSE_NEGATIVE` and no `OLD_FALSE_POSITIVE` case existed for any audited policy** (per-case coverage decline is equivalent to at least one P0-hit critical-group loss on this data, and every coverage-equal case preserved its hit set). Corrected Gate 5: P1 `FAIL` (g059 loses `g059.e2`+`g059.e3`; recovers `g002.e1` on g002), P2 `FAIL` (g105 loses `g105.e2`), **P3 `PASS` (zero newly lost critical groups; recovers `g002.e1`)**, P4 `FAIL` (g055 loses `g055.e2`). All other gates unchanged → **P3 remains `PASS_ALL_GATES`**, P1/P2/P4 remain `FAIL_HARD_GATES`, passing set unchanged `{P3_SPARSE_HEAVY}`. Intent-level audit: zero new critical-group misses for every sufficiently represented intent × P1/P2/P3 (the lost groups sit in low-count intents or the semantic cohort) → preferences, conditions 1-6, `INTENT_AWARE_ELIGIBLE = true`, and the `C6_INTENT_AWARE_V1` mapping are all unchanged (P2 remains eligible for troubleshooting under the preregistered intent-level rules despite its global failure). SemanticDense `INSUFFICIENT` / `KEEP_DISABLED` is independent of Gate 5 and unchanged; a yield-denominator note was added (A1 freezes the metric name only; `1/160` counts relevant/all semantic candidates while relevant/semantic-unique is `1/41`). The A2 manifest now carries a `critical_miss_semantics_correction` section (superseded interpretation preserved; `authoritative_after_audit = true`), and `evaluate_c6_a2_fusion_policies.py` now defines `new_critical_miss` via the `critical_group_delta` group-identity helper for future deterministic reruns. `C6-A2` authoritative verdict after audit: `PASS`; `critical_miss_semantics_audit = PASS`; `C6-A3` `NEXT_ELIGIBLE / NOT_STARTED`. Cost: analyzer/embeddings/sparse/retrieval/Qdrant/SQL/reranker/selector/QA/verifier/judge/writes/index mutation all `0` (frozen receipt + Gold + repository file reads only).

## Current C6-A3 — 2026-08-22

- **Artifact:** `evaluation/baselines/manifests/phase_c_c6_a3_frozen_production_role_decision_v1.json`; source HEAD `200d8d51c2dce164de5d027751be97b371551fc3`. A pure frozen-evidence interpretation and production-role decision task: zero new outcome measurements, zero policy replays, zero retrieval/analyzer/embedding/reranker/selector/QA calls, zero production code changes. First and only C6-A3 execution.
- **Role vocabulary:** `PRODUCTION_AUTHORITATIVE` / `DEVELOPMENT_SUPPORTED_CANDIDATE` / `EVALUATION_ONLY_CANDIDATE` / `KEEP_DISABLED` / `REJECTED_BY_A2` (defined in the artifact; no new state machine).
- **Decisions:** P0 CURRENT = `PRODUCTION_AUTHORITATIVE` (production fusion remains unchanged). P1 = `REJECTED_BY_A2` (gates 5/6/7; critical-group losses g059.e2/g059.e3). P2 = `REJECTED_BY_A2` as a standalone global alternative (gates 3/5/7; loses g105.e2) while remaining a component of the evaluation-only `C6_INTENT_AWARE_V1` troubleshooting mapping. **P3 SPARSE_HEAVY = `DEVELOPMENT_SUPPORTED_CANDIDATE`** — the strongest global development-policy candidate identified by C6 (`PASS_ALL_GATES` 10/10 after the corrected group-identity Gate 5; R@20 `1.0`, critical `1.0`, MRR `+0.0334`, lost_hit `0`), blocked from production activation solely by `novel_replay_status = ABSENT`. P4 = `REJECTED_BY_A2`. P5 = `EVALUATION_ONLY_CANDIDATE` (prefix-safe 8/8, non-harmful expansion mechanism retained as an evaluation/diagnostic construct; `EXPANSION_CONTRIBUTION = NOT_MEANINGFUL`; production role none). SemanticDense = `KEEP_DISABLED` (unique relevant case count `1 < 2`; auxiliary/shadow implementation retained for research; no further C6 tuning, no reopened P4/P5, threshold unchanged). `C6_INTENT_AWARE_V1` = `DEVELOPMENT_SUPPORTED_CANDIDATE` (mapping frozen as the current evaluation candidate: installation→P3, troubleshooting→P2, others CURRENT; not production activated, not tuned).
- **Hypotheses kept distinct:** global P3 (H1) and `C6_INTENT_AWARE_V1` (H2) remain two separate development hypotheses for future independent corroboration; no composite score, tie-break, or winner selection was invented.
- **Novel corroboration gate:** `novel_replay_status = ABSENT`; `NEW_PRODUCTION_POLICY_ACTIVATION = NOT_AUTHORIZED_BY_C6_A2_ALONE`; `production_activation_authorized = false`. Development evidence is not independent corroboration, and the gate was not weakened even though P3 passes all 10 hard gates.
- **Production behavior:** fusion unchanged (P0 CURRENT `c6.current.v1`); exact `LEGACY_EXACT`; sparse `RAW_QUESTION`; RawDense production-authoritative; SemanticDense disabled from scored production fusion (auxiliary/shadow only); intent-aware routing not production activated; production code changes `0`. A2 selection-layer debt remains downstream debt owned by C7/C8.
- **Future corroboration boundary (non-executable note):** production activation of any new fusion role requires independent or novel question evidence, evaluated without reusing the exposed development outcomes for tuning, under the same frozen candidate/policy semantics or a separately preregistered future policy revision, with no regression of critical evidence safety. No novel dataset was designed or generated and no T3/T4/T5 was scheduled.
- **Result:** `C6-A3` `PASS` (authoritative A2 evidence internally consistent — contradictions found `0`; roles assigned without new outcome selection; novel gate respected; no unauthorized activation; production behavior unchanged). **C6 lifecycle `COMPLETE`.** Next roadmap item: `C7` — Clear source constraints and evidence diversity, `NEXT_ELIGIBLE / NOT_STARTED` (its dependencies on C6 ranked pools and A2 traces are satisfied; Phase D follows Phase C and does not precede C7). C7 was not executed in A3.

## Current C7-A0 — 2026-08-23

- **Artifact and verification:** `evaluation/baselines/manifests/phase_c_c7_a0_selection_boundary_replay_inventory_v1.json`; static-only audit `evaluation/scripts/audit_c7_a0_selection_boundary_replay.py`; accepted source HEAD `c4510bd4f09f6dfaab47ef87260b4c1ce9843f8a`. `C6` remains `COMPLETE`; this is the first C7 task.
- **Boundary:** C7 begins after raw LLM `reranked_object_ids`; the LLM reranker is `HELD_CONSTANT`, `RERANKER_QUALITY_EVALUATED=false`, and `RERANKER_MODIFIED=false`. C7 owns deterministic Stage-M construction (raw R followed by remaining F fallback candidates), hinted/required/exact priority reorder, and `select_final_evidence` through final Evidence. Fusion, retrieval, reranker behavior, targeted/global second pass, and QA are out of scope.
- **Static findings:** Stage F is the complete fusion order; R is raw reranker output; M is raw R followed by the remaining F fallback candidates, deduplicated in that order; P is the deterministic priority reorder; S is final evidence/receipts. `ranked_object_ids` is only the Stage-P top-30 prefix, while the selector can inspect the complete P order. `source_budgets` are source-type maximum caps; `max_per_source` is a separate source-id cap. `graph` is a retrieval channel rather than a derived source type, while `workflow` has mixed channel/source-type semantics; required-first is channel-aware for graph/workflow but backfill is source-type-only. Mandatory exact-symbol IDs bypass only source/type caps, not duplicate suppression or the final limit. Required source types are intent-policy defaults, not individually proven question requirements.
- **Replay finding:** `POST_RERANKER_REPLAY_CAPABILITY=INSUFFICIENT`; current faithful full-replay case count `0`; `C7_A2_FROZEN_CAPTURE_REQUIRED=true`. `phase_c_c6_current_plan_candidate_replay_v2.jsonl` is a pre-reranker fusion/candidate artifact, never a C7 selector replay dataset. No existing frozen trace provides complete F/R/M/P/S state, all candidate payload facets, and the complete selector fallback order without external lookup. The artifact defines a non-executable minimum C7-A2 capture schema without Gold outcome fields.
- **Isolation and result:** Static repository reads only; relevance outcomes, retrieval/fusion/policy replay, reranker, selector treatment, QA/verifier/judge, analyzer, embeddings, sparse, Qdrant, SQL, and DB/index writes all `0`. Production fusion, reranker, selector, and `retrieval_policies.yaml` are unchanged; production code changes `0`. `C7-A0` `PASS`; `C7` is `ACTIVE`; `C7-A1` is `NEXT_ELIGIBLE / NOT_STARTED`; `C7-A2/A3/A4` are `NOT_STARTED`.

## Historical C7-A1 implementation before semantic repair — 2026-08-23

- **Artifact and verification:** `evaluation/baselines/manifests/phase_c_c7_a1_explicit_selection_contract_v1.json`; shadow-only module `src/panda_agent/evidence_selection.py`; focused T0 `21/21` PASS. The accepted source HEAD for this task was `1c93a33944d119e10c0aad0dcc830ceb4284cd0c`.
- **Contract:** `PROTECTED`, `REQUIRED`, `PREFERRED`, and `MAXIMUM` are the sole constraint vocabulary; `MINIMUM` is unsupported. Dimensions are explicit and separate: `SOURCE_ID`, `SOURCE_TYPE`, `RETRIEVAL_CHANNEL`, and `OBJECT_ID`. `graph` is only a retrieval channel; `workflow` may independently occur in source-type and channel constraints. `source_budgets` become explicit MAXIMUM constraints; reviewed static intent source defaults become PREFERRED with `not_question_required=true`; exact mandatory symbols become PROTECTED.
- **REQUIRED boundary:** A REQUIRED `SOURCE_ID` is generated only for an exact `target_repositories` match whose existing `analysis_diagnostics.deterministic_parse.provenance.target_repositories` record is `source=explicit_query_reference`. Static intent defaults never generate REQUIRED, and no new query analysis or inference was introduced.
- **Superseded selector semantics:** `c7.explicit_selection.v1` introduced plain frozen-data, shadow-only M/P/S logic and complete candidate/constraint receipts, but its first implementation gave every PREFERRED match and every match of an existential REQUIRED facet Stage-P priority. This could change admission membership solely because of a soft preference and could promote an entire REQUIRED matching group. Those two conformance defects required C7-A1R1 before authoritative closeout; they were contract defects, not outcome-performance findings.
- **Historical isolation:** Production `Retriever.retrieve` still called `select_final_evidence`; `retrieval.py`, `retrieval_policies.yaml`, reranker prompt/call, and fusion weights were unchanged. Gold outcomes, retrieval/fusion replay, reranker, analyzer, embeddings, sparse, Qdrant, SQL, QA/verifier/judge, and DB/index operations were all `0`.

## Current C7-A1R1 — 2026-08-23

- **Artifact and verification:** The original provenance is retained in `evaluation/baselines/manifests/phase_c_c7_a1_explicit_selection_contract_v1.json`, whose `a1r1_semantics_correction` section is authoritative after this repair. Source HEAD was `dc266f3565b0d7cd1cb5c0eaa4a95abc4a5073d5`; focused deterministic T0 is `30/30` PASS, including all retained C7-A1 coverage and nine correction fixtures.
- **PREFERRED correction:** PREFERRED is advisory and receipt-only for admission. With frozen input, hard constraints, and `final_evidence_limit` fixed, adding or removing only PREFERRED constraints cannot change the selected object-ID set. A low-ranked PREFERRED candidate outside the normal top-12 boundary remains excluded; no preference backfill, minimum obligation, MAXIMUM bypass, duplicate bypass, or final-limit bypass exists.
- **REQUIRED correction:** REQUIRED remains generated only from existing exact `explicit_query_reference` target-repository provenance and has existential default cardinality `1`. Each constraint chooses the earliest hard-eligible matching Stage-M candidate as its deterministic satisfying representative; one candidate may represent several constraints, while remaining matches retain ordinary rank semantics. A representative may record `required_override` when an applicable diversity MAXIMUM would otherwise block it, but validity, source-version/usability, duplicate suppression, and final limit remain hard. Missing or hard-blocked representatives remain `unsatisfied` without invented evidence.
- **Graph normalization:** The shadow translation from graph source budget to `RETRIEVAL_CHANNEL graph MAXIMUM` remains an intentional `EXPLICIT_V1` treatment semantic delta. It is explicitly **not** behavior-preserving relative to current production, where graph-as-source-type budgeting was effectively inert.
- **Receipts and isolation:** Candidate receipts distinguish ordinary admission, `protected_override`, `required_override`, `required_representative`, preference match without admission effect, and hard exclusion reasons. REQUIRED receipts expose matched, eligible, and satisfying IDs plus cardinality; PREFERRED receipts declare `admission_effect=false`. MAXIMUM summaries exclude valid hard overrides from ordinary-count conformance. Production retrieval, selector wiring, `retrieval_policies.yaml`, reranker, and fusion remain unchanged; Gold/outcome evaluation, retrieval, reranker calls, A2 capture, analyzer, embeddings, sparse, Qdrant, SQL reads, QA/verifier/judge, DB/index writes, and production activation are all `0`.
- **Result:** `C7-A1R1` `PASS`; `C7-A1` is `PASS_AFTER_SEMANTICS_REPAIR`; `C7` remains `ACTIVE`; `C7-A2` is `NEXT_ELIGIBLE / NOT_STARTED`. At this A1R1 historical point, A3/A4 had not started; `C7_A2_FROZEN_CAPTURE_REQUIRED=true`.

## Current C7-A2 — 2026-08-23

- **Baseline and parent population:** Accepted source HEAD `a6bec2776e55b824831e22b7fbebd68489158be5`. The authoritative C6 global-policy parent contains 30 cases with intent counts installation `6`, usage `6`, algorithm-theory `5`, API `5`, troubleshooting `5`, algorithm-implementation `2`, and module-structure `1`.
- **Frozen cohort:** Before any live capture or outcome observation, the deterministic rule retained all intents with at most three cases and otherwise the lexicographically first three, followed by a final lexical sort. The resulting 18 cases are `g001,g002,g003,g010,g013,g014,g027,g028,g029,g044,g047,g050,g059,g060,g105,g110,g112,g113`, with intent counts `3/3/3/3/3/2/1`. Gold, relevance, criticality, S1 results, wins/losses, and outcome fields were not used to select or replace cases.
- **Capture execution and replay:** The one authorized capture executed exactly one production retrieval and one held-constant reranker call per case: retrieval `18`, reranker `18`, analyzer `0`, Gold evaluation `0`, S1 real-cohort calls `0`, QA `0`, verifier `0`, and judge `0`. All 18 rows captured frozen question/plan identity, channel rankings and Stage F, raw Stage R with Stage-F ranks, Stage M, complete Stage P selector inputs, candidate payloads/scores/channels, exact stream, mandatory IDs, final limit, and production CURRENT S0 evidence/exclusion/backfill receipts. Failed cases `0`; no retries or replacements. Offline CURRENT replay reproduced selected order, exclusions, and backfill receipts on `18/18` cases without external reads.
- **A3 preregistration:** Policies are S0 `CURRENT_SELECTOR` and S1 `c7.explicit_selection.v1`; reranker is `HELD_CONSTANT`. Five primary metrics are frozen: Final Evidence Recall, Critical Evidence Retention, explicit REQUIRED satisfaction, per-policy selector-caused relevant-group displacement from the full frozen candidate universe, and protected exact retention. Supported precision and the full diagnostic family are secondary. The 12 hard gates, the meaningful-gain rule (all supported gates pass, at least one primary improvement, and no primary regression), A1R1 PREFERRED/REQUIRED/PROTECTED semantics, and graph-channel MAXIMUM treatment are frozen in the manifest. Gate 9 is `NOT_SUPPORTED` unless explicit negative completeness exists; Gate 11 is bound to static policy/contract/source evidence rather than case receipts; Gate 12 is bound to the frozen manifest rather than a caller assertion.
- **Isolation and original result:** No S1 execution on the real cohort and no outcome/Gold evaluation occurred in A2. Production retrieval, fusion, reranker, selector wiring, `src/`, and `configs/` were unchanged; DB/index writes, reindex, and document reembedding were `0`. The original capture and replay result was `PASS`; subsequent pre-outcome evaluator review required C7-A2R1 before A3 eligibility could remain authoritative.

## Current C7-A2R1 — 2026-08-23

- **Reason and frozen-data preservation:** Review found four evaluator-conformance defects: primary-metric direction was inferred positionally and therefore inverted protected exact retention; aggregate primary metrics used a macro mean rather than frozen micro units; Gates 4/5/6 compared ratios rather than case-scoped loss identities; and source-type concentration used raw `object_type`. The accepted 18-case cohort, capture JSONL, complete F/R/M/P/S state, CURRENT S0 replay, S1 policy semantics, hard-gate intent, and meaningful-gain intent remain unchanged. No recapture or case replacement occurred.
- **Metric and gate correction:** All five metric directions are explicit; relevant and critical groups, explicit REQUIRED constraints, and mandatory IDs aggregate by micro case-scoped identity with auditable numerator/denominator/value; selector displacement reports displaced count, exposed-group denominator, and rate with identical S0/S1 denominator identity. Gate 3 consumes micro recall; Gate 4 rejects any S0-retained critical identity lost by S1; Gate 5 rejects any S0-retained mandatory object identity lost by S1; Gate 6 requires both non-regressing micro satisfaction and no newly unsatisfied S0 constraint identity; Gate 7 compares both displacement count and rate. Gate 9 remains `NOT_SUPPORTED` without explicit negative completeness.
- **Secondary diagnostics:** Source types now reuse the deterministic C7 classifier (`paper`, `documentation`, `workflow`, `readme`, `code`) rather than raw object types. Diversity separately reports unique source-ID and source-type counts.
- **Verification and isolation:** Synthetic focused tests `17/17 PASS`, covering explicit directions, micro-vs-macro behavior, unequal REQUIRED/protected denominators, case-scoped group collision, compensating-swap identity losses, displacement count/rate, and source-type/diversity diagnostics. Static capture validation confirms exactly 18 unchanged case IDs, all captured S0 parity flags true, and the original A2 call ledger remains retrieval `18`, reranker `18`, analyzer/Gold/S1 `0`. During A2R1: retrieval, reranker, analyzer, embeddings, sparse encoding, Qdrant/SQL reads, QA/verifier/judge, Gold outcomes, real-cohort S1, and DB/index writes all `0`; production `src/`, `configs/`, selector, fusion, and reranker are unchanged.
- **Artifact and result:** `evaluation/baselines/manifests/phase_c_c7_a2_frozen_selector_preregistration_v1.json#a2r1_evaluator_semantics_correction` is authoritative after this repair; original `source_head=a6bec2776e55b824831e22b7fbebd68489158be5` remains the capture identity and repair source HEAD is recorded separately as `4a31540151b7b7cedb11da361ffce22907c9d34f`. `C7-A2R1` `PASS`; `C7-A2` `PASS_AFTER_EVALUATOR_REPAIR`. At the end of A2R1, A3 was eligible; the historical failed A3 invocation and current A3R1 recovery record follow.

## Historical C7-A3 — 2026-08-23

- **Baseline and preflight:** Source HEAD was `190a8bef30d80d6470c926ccae0336d0647ffc4d`; `C7-A2` was `PASS_AFTER_EVALUATOR_REPAIR` and `C7-A2R1` was `PASS`. The frozen 18-case capture remained unchanged and CURRENT S0 replay parity remained `18/18`. Pre-outcome `preregistration_integrity()` passed `27/27` checks, `static_s1_contract_proof()` passed `7/7`, and capture validation passed.
- **Gold annotation projection:** `evaluation/baselines/manifests/phase_c_c7_a3_gold_annotation_projection_v1.json` projected all 18 frozen cases with the authoritative `panda_agent.evaluation._matched_evidence_groups` matcher. `unsupported_conditions` was empty. Candidate-universe misses were recorded without compensation as `g013.e2`, `g105.e2`, and `g113.e3`. Negative completeness was unsupported and not fabricated; no known-irrelevant IDs were asserted.
- **Authoritative invocation:** Exactly one authorized offline evaluator invocation was attempted. It failed during `module_import` with `ModuleNotFoundError: No module named 'evaluation'` before any case evaluation. Case evaluations, S0 executions, and S1 executions were all `0`. No environment or evaluator fix was applied and no rerun was permitted.
- **Metrics and gates:** All five primary metrics are `NOT_EVALUATED`: Final Evidence Recall, Critical Evidence Retention, Explicit REQUIRED Satisfaction, Selector-caused Relevant Displacement, and Protected Exact Retention. Identity losses, case directions, selector displacement, graph/workflow/source diagnostics, and the authoritative 12-gate matrix are `NOT_EVALUATED`. Gate 11 and Gate 12 retain only their pre-outcome static proofs (`PASS`); they are not completed A3 gate-matrix results. Gate 9 is `NOT_EVALUATED`, with negative completeness absent.
- **Isolation:** `LIVE_RETRIEVAL_CALLS=0`; `RERANKER_CALLS=0`; `ANALYZER_CALLS=0`; embedding, sparse encoding, Qdrant, SQL candidate reads, DB/index writes, QA, verifier, and judge calls were `0`. The reranker remained `HELD_CONSTANT`; production behavior and the production selector remained unchanged.
- **Artifacts and terminal state:** The projection above and `evaluation/baselines/manifests/phase_c_c7_a3_frozen_selector_evaluation_v1.json` preserve the evidence. `S1_POLICY_RESULT=null` / unavailable; production activation remains unauthorized. `C7` remains `ACTIVE`; `C7-A3` is `INCONCLUSIVE`; `C7-A4` is `NOT_ELIGIBLE / NOT_STARTED`. No next C7 stage is eligible from this task, and A4 was not executed.

## Authoritative C7-A3R1 — 2026-08-23

- **Recovery basis and preflight:** Source HEAD `68c2d5686ff486134eeb13de3306c11408ca01d3` preserved the historical A3 failure as a pre-outcome infrastructure failure: case, S0, S1, and Gold outcome executions were all `0`, so `PRIOR_A3_OUTCOME_OBSERVED=false`. Repository-root package import succeeded with `CURRENT_SELECTOR` and `c7.explicit_selection.v1`; preregistration integrity, static S1 contract proof, unchanged capture validation, `18/18` S0 replay parity, and the existing 18-case Gold projection all passed. The evaluator, selector contract, projection, Gold, cohort, capture, and scientific preregistration were reused unchanged.
- **Authoritative recovery execution:** Exactly one `python -m evaluation.scripts.evaluate_c7_a3_frozen_selectors` invocation evaluated all 18 frozen cases. No second comparison ran. Retrieval, reranker, analyzer, embedding, sparse encoding, Qdrant/SQL reads, DB/index writes, QA, verifier, and judge calls were all `0`; reranker role remained `HELD_CONSTANT`, and production code/configuration remained unchanged.
- **Primary metrics:** Final Evidence Recall and Critical Evidence Retention both regressed from `28/32 = 0.875` to `27/32 = 0.84375`. Explicit REQUIRED Satisfaction stayed `11/11 = 1.0`; Protected Exact Retention stayed `52/52 = 1.0`. Selector-caused Relevant Displacement regressed from `1/29 = 0.034482758620689655` to `2/29 = 0.06896551724137931`. The sole new identity loss was critical group `g003.e1`; protected and REQUIRED identity losses were `0`.
- **Gates and direction:** Gates 1, 2, 5, 6, 8, 10, 11, and 12 passed; Gates 3, 4, and 7 failed; Gate 9 was `NOT_SUPPORTED` because negative completeness is absent. Case direction was `0` improved, `17` unchanged, and `1` regressed. The frozen meaningful-gain rule therefore produced `S1_POLICY_RESULT=CURRENT_PREFERRED_GATE_FAILURE`.
- **Diagnostics:** The graph RETRIEVAL_CHANNEL MAXIMUM treatment exposed `132` matched candidates and caused membership differences in `g003,g028,g044,g047,g059,g060,g105,g110`. Workflow-channel candidates were present in 16 cases, with selected counts `20 -> 23`. Summed per-case source-ID diversity changed `60 -> 57`, and source-type diversity changed `59 -> 58`. Candidate-universe-absent Gold groups `g013.e2`, `g105.e2`, and `g113.e3` were not counted as selector displacement.
- **Artifact, limitation, and lifecycle at A3R1 completion:** `evaluation/baselines/manifests/phase_c_c7_a3r1_frozen_selector_evaluation_v1.json` superseded the historical failed-attempt artifact as authoritative C7-A3 outcome evidence while retaining the historical reference. Because development Gold was exposed, `PRODUCTION_ACTIVATION_AUTHORIZED=false` and `PRODUCTION_SELECTOR_CHANGED=false`. `C7-A3R1` was `PASS`; `C7-A3` became `PASS_AFTER_PRE_OUTCOME_INVOCATION_RECOVERY`; C7 remained `ACTIVE`, and A4 became eligible. The current A4 closeout record follows.

## Current C7-A4 — 2026-08-23

- **Frozen-evidence closeout:** `PASS` at source HEAD `8ba16ba6e400c7a97317a14eb5eda0e63c7e9050`, using only the committed A1/A1R1 contract, A2/A2R1 preregistration, historical failed A3 provenance, and authoritative A3R1 result. The contradiction audit found `0` material contradictions. A4 generated no new outcome: Gold evaluations, S0/S1 executions, retrieval, reranker, analyzer, embedding, sparse encoding, Qdrant/SQL reads, QA/verifier/judge, and DB/index writes were all `0`.
- **Production roles:** `CURRENT_SELECTOR = PRODUCTION_AUTHORITATIVE`. `c7.explicit_selection.v1 = REJECTED_AS_GLOBAL_PRODUCTION_REPLACEMENT` because it failed Gates 3, 4, and 7, produced `0` improved cases, introduced the new critical miss `g003.e1`, regressed Final Evidence Recall and Critical Evidence Retention from `28/32` to `27/32`, and increased selector displacement from `1/29` to `2/29`. Production activation is rejected; production selector and wiring remain unchanged.
- **Causal boundary:** Candidate-level receipts prove `g003.e1` was excluded by S1 MAXIMUM-based selection behavior. They do not prove direct graph RETRIEVAL_CHANNEL MAXIMUM ownership: the displaced relevant candidate IDs do not overlap the graph-MAXIMUM matched set. Graph MAXIMUM remains a material diagnostic exposure (`132` matched candidates; membership differences in `g003,g028,g044,g047,g059,g060,g105,g110`) and is recorded as `FUTURE_REDESIGN_DEBT`, not repaired or tuned in A4.
- **Retained architecture and safe semantics:** The `PROTECTED`, `REQUIRED`, `PREFERRED`, and explicit-constraint vocabulary; SOURCE_ID/SOURCE_TYPE/RETRIEVAL_CHANNEL/OBJECT_ID separation; representative/protected semantics; candidate/constraint receipts; and frozen replay/evaluation infrastructure remain available as architecture and research reference. REQUIRED stayed `11/11`, protected exact stayed `52/52`, related identity losses were `0`, source/version/usability passed, S1 was deterministic, and the PREFERRED admission invariant held. These facts do not authorize a partial production rollout.
- **Lifecycle and handoff:** No A3R2, post-outcome tuning, selector v2, C6+C7 composite, or production change occurred. `evaluation/baselines/manifests/phase_c_c7_a4_production_role_closeout_v1.json` is the closeout artifact. `C7-A4` is `PASS`; C7 is `COMPLETE`. `C8` is `NEXT_ELIGIBLE / NOT_STARTED`, while `NOVEL_DATASET_CURATION_BEFORE_SUBSTANTIAL_DOWNSTREAM_DEVELOPMENT` is the recommended immediate workflow; no novel dataset or C8 work was executed.

## Current N0 — Novel Dataset Curation Contract — 2026-08-23

- **Result:** `PASS`. `docs/NOVEL_DATASET_CURATION_CONTRACT.md` is the authoritative Novel Dataset Curation Contract v1. It defines question-distribution generalization over the locked corpus; `novel_dev`, `novel_validation`, and externally protected `novel_holdout`; the 12–16 candidate-`novel_dev` N1 pilot; substantive novelty and overlap review; independent structural difficulty and coverage metadata; Gold-compatible evaluator records plus a question-ID-keyed curation sidecar; human review; exposure-ledger semantics; external holdout loading; lightweight dataset identity; and annotation-versus-information-need amendment rules.
- **Compatibility boundary:** The current strict `GoldQuestion` model already accepts `n###` IDs and all three novel splits, and canonical `QAStatus` includes `answered`, `insufficient_evidence`, `version_conflict`, and `clarification_required`. Novel-only metadata remains in a sidecar because unknown Gold fields are forbidden. Gold v2 does not formally cover `clarification_required`, so N1 must perform a small generic T0 loader/evaluator compatibility check before accepting such a case; N0 made no evaluator change.
- **Isolation:** No novel question, validation item, or holdout item was created. PANDA retrieval, QA, judge, Vertex generation, dense embedding, sparse encoding, Qdrant/SQL, index mutation, and benchmark/novel outcome inspection were all `0`. No T1/T2/T3/T4/T5, C8, D1, dataset generation, candidate activation, or production behavior change occurred.
- **Handoff at N0 closeout:** N0 is `COMPLETE`; N1 was then `NEXT / NOT_STARTED`. The current N1 state is the N1-R2R1 draft ready for final human approval, as recorded at the top of this file. C8 remains scientifically unchanged and `NEXT_ELIGIBLE / NOT_STARTED`.
- **Pre-N1 governance correction — 2026-08-23:** N0 remains `PASS / COMPLETE`. The contract now freezes authoritative source truth and source versions rather than derived KnowledgeObject/chunk/index representations; defines validation exposure for question content, Gold, and outcome material actually used for development; requires cross-file semantic-family isolation for repository-visible novel splits plus an external holdout non-derivation declaration; and separates canonical intents from orthogonal coverage dimensions in `evaluation/novel/README.md`. This was documentation-only: no novel question, validator, evaluation, C8 change, or production change was created.

## Historical full E2E reference

The newest trustworthy complete E2E artifact selected for historical reference is:

`data/evaluation/runs/m6-v2-36-qa-dev-rc3e`

It is a complete 80-question dev run with 514 model calls and 6,389,043 tokens. Measured metrics include `gold_recall_at_10=1.0`, `final_evidence_recall=0.9482323232`, `critical_final_evidence_recall=0.9482323232`, `answer_point_coverage=0.9458333333`, `citation_integrity=1.0`, `intent_accuracy=0.9875`, and `expected_status_accuracy=1.0`.

It does **not** match the A3 measured execution provenance exactly: the historical manifest predates explicit Git commit recording and used Gold v2.4 plus prompt set 3.5.0. It is historical evidence, not a current release claim.

## English Gold Stratified Bootstrap Baseline

Versioned package:

`evaluation/baselines/english-gold-stratified-bootstrap-v1-20260813`

Fixed selection manifest:

`evaluation/baselines/manifests/english_gold_stratified_bootstrap_v1.json`

This is a low-cost English Gold reference, not a complete generalization, complete benchmark, or all-intent baseline. Future before/after comparisons must reuse the fixed 24 retrieval and 16 QA IDs unchanged; a different selection requires a new manifest identity.

### Current stratified retrieval baseline

- Run: `generalization-a3-stratified-retrieval-20260813`.
- Mode/cases: `retrieval`, 24 approved English Gold questions.
- Cost: 72 runtime model calls, 482,907 tokens, 0 external-judge calls.
- Measured: Recall@5 `0.8416666667`; Recall@10 `0.9`; Recall@20 `0.9`; MRR `0.6866666667`; combined candidate recall `0.95`; final-evidence recall `0.9`; intent accuracy `1.0`; no exceptions.

### Current B1 sparse BM25/Qdrant IDF result

- Installed contract: FastEmbed `0.7.4`, Qdrant client `1.15.1`, live Qdrant server `1.15.5`; `SparseVectorParams()` exposed a null modifier, while FastEmbed BM25 requires server-side IDF.
- Deployed identity: explicit sparse modifier `idf`, index schema `3`, fingerprint `5f0f9ffe6149091e6c42d650f3a7576466d82b8eb86af0567d9c57a81bb8a937`.
- Migration: in-place update of `80698` points before/after; no collection recreation, sparse-vector regeneration, dense reinsertion, dense embedding recomputation, or Vertex calls.
- Cost: 24 sparse encodings and 24 Qdrant sparse queries; analyzer, dense embedding, reranker, answer, verifier, judge, and token usage were all `0`.
- Fixed 24-query sparse-only comparison (applicable denominator 20; the four `version_conflict` cases remain excluded): Recall@5 `0.375` → `0.475` (`+0.1`), Recall@10 `0.5166666667` → `0.6` (`+0.0833333333`), MRR `0.4212698413` → `0.4201388889` (`-0.0011309524`).
- Explicit identifier-heavy IDs: `g015,g027,g028,g029,g038,g041,g042,g059,g060`; applicable denominator 8. Recall@5 `0.125` → `0.25` (`+0.125`), Recall@10 `0.2916666667` → `0.375` (`+0.0833333333`), MRR `0.1513888889` → `0.1302083333` (`-0.0211805556`).
- First-relevant-rank comparison: improved `3`, unchanged `14`, regressed `3`. Improvements were `g025` (14 → 4), `g028` (9 → 8), and `g029` (no hit → 2); regressions were `g002` (7 → 9), `g015` (1 → 3), and `g060` (10 → 12). Recall improved without a broad systematic regression; MRR was effectively flat and slightly lower.
- Limitation: this is an exposed English Gold bootstrap comparison with a small identifier-heavy subset, not a complete benchmark or novel-question generalization result.

### Current B2 dense embedding dimensionality contract result

- Verification revision: `ec692735e0623b256a40fe384a9f865e8cdb58c0` (B1 committed).
- Installed API: `google-genai 2.13.0`; `EmbedContentConfig.output_dimensionality` is explicitly set to 3072 for the shared query/document `_embed` path, and every returned vector is checked for count, non-empty values, and exact length before use.
- Cache/index impact: cache key remains unchanged; SQL reuse requires `dimensions=3072`, and all `70102` existing rows already match. Stale receipts update only after a real re-embed. `IndexIdentity` already includes dimensions, so schema 3 and fingerprint `5f0f9ffe6149091e6c42d650f3a7576466d82b8eb86af0567d9c57a81bb8a937` are unchanged.
- Live collection: Qdrant size is 3072 with `80698` points; three sampled vectors are length 3072. No collection/index migration, dense-vector migration, or re-embedding was needed.
- Verification cost: T0 final suite `50` tests passed, along with `compileall` and `git diff --check`. The supplemental live endpoint smoke then used the production `VertexAIClient` for exactly one `RETRIEVAL_QUERY` and one `RETRIEVAL_DOCUMENT` request; both explicitly requested and returned 3072 dimensions with `gemini-embedding-2` in `global`. Cost was two embedding calls, zero generation/judge calls, and no token usage metadata returned by the embedding API.

### Current B3 unified sparse encoder identity/factory result

- Implementation: the former independent sparse construction paths in `src/panda_agent/indexing.py`, `retrieval.py`, `sparse_evaluation.py`, and `kb_bundle.py` now use the sole `create_sparse_encoder` factory and `SparseEncoderReceipt` contract in `src/panda_agent/sparse.py`.
- Portable receipt: `Qdrant/bm25`, English, vector `sparse`, modifier `idf`, `k=1.2`, `b=0.75`, `avg_len=256.0`, `token_max_length=40`, `disable_stemmer=false`, `SimpleTokenizer`, `SnowballStemmer`, `mmh3.hash`, FastEmbed `0.7.4`, `mmh3` `5.2.1`, `py-rust-stemmers` `0.1.8`, and English stopwords `english.txt` SHA-256 `019f104ba2ed07436d05f9cdd3383034ad66014edc27fc651f837e1a038b6451`.
- Identity boundary: machine-specific `model_path`, `local_files_only`, `threads`, and `device` are excluded from portable semantic identity because they describe installation or runtime policy; `local_files_only` is nevertheless mandatory and fail-closed. Semantic receipt or Qdrant/persisted-contract mismatches reject startup/migration rather than degrade silently.
- Schema/migration: schema 3 fingerprint `5f0f9ffe6149091e6c42d650f3a7576466d82b8eb86af0567d9c57a81bb8a937` migrated to schema 4 fingerprint `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`. Dry-run and `--run` sampled the first eight points in native Qdrant scroll order, re-encoded `title + "\n" + text`, matched point sets and sparse index sets, and found float32 bit-exact sparse values for 8/8 points with `mismatch=0`.
- Migration effect and cost: the only write was one metadata-only PostgreSQL single-row CAS update. Qdrant remains at `80698` points with dense size `3072` and sparse `idf`; no collection rebuild, sparse/dense vector regeneration or reinsertion, dense embedding recomputation, or Vertex call occurred. T0 final verification passed `63` tests plus `compileall`, `git diff --check`, and one constructor smoke. T1 local FastEmbed used eight dry-run and eight `--run` document encodes (16 total), two Qdrant scroll/read rounds, and one SQL identity update; generation, analyzer, embedding, reranker, QA, verifier, judge, token, benchmark, Retriever/QA, T3+ work were all zero/not run.

### Current B4 precise derived-chunk locator result

- Root cause confirmed: derived embedding chunks reused parent-wide locators; truncated file objects claimed lines beyond their stored prefixes; README sections lacked heading hierarchy; Sphinx pages used a flattened first-heading slice and sections kept only a title; PDF chunks inherited page-wide provenance. Existing parser-native C/C++, Python, CMake, and shell coordinates were already precise and remain authoritative.
- Implementation: chunk derivation now carries deterministic source spans while splitting and derives inclusive child line ranges from those offsets. It does not recover spans with ambiguous `str.find()`, and it preserves the exact pre-B4 chunk text, boundaries, IDs, titles, canonical locators, token counts, embedding eligibility, source/version identity, and parent/chunk lineage. Truncated file locators are bounded to the represented prefix. README paths are hierarchical; Sphinx sections use deterministic heading ancestry and stable anchors where available; PDF provenance remains conservative page/section metadata without fabricated line numbers.
- Semantic invariance: normalized artifacts remain at `102875` objects before and after. IDs added `0`, IDs removed `0`, and changes to text, title, object type, source/version identity, canonical locator, token count, embedding eligibility, and parent/chunk lineage were all `0`. Locator changes totaled `28010`, concentrated in derived function/class/script/README chunks and truncated source-file records.
- Locator audit: `16352` derived chunks checked with `0` parent-containment violations and `0` invalid line ranges; `652` truncated file objects corrected with `0` remaining overbroad ranges; `281` README hierarchy cases checked; `314` Sphinx sections checked, including `241` stable anchor fragments and `0` synthetic fragment URLs; PDF page/section cases had `0` fabricated line locators. Duplicate-text, blank-line, CRLF, first/final-line, and mid-line span fixtures passed.
- Live metadata impact: normalized artifacts were updated. The initial dry-run planned and the explicit metadata-only apply updated `28010` PostgreSQL locator rows and `22856` Qdrant payload locators; the post-apply dry-run planned `0` changes. Every update was gated by object ID, source/version, Qdrant point mapping, unchanged text/content hash, and current B3 identity.
- Vector/index impact: Qdrant vector content changed `0`; dense vectors reinserted `0`; sparse vectors regenerated `0`; dense embeddings recomputed `0`; Vertex/model calls `0`. Index schema remained `4`; fingerprint remained `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`.
- Verification cost: T0 passed `10` ingestion locator tests, `7` metadata-sync tests, and `11` B3 sparse-factory regression tests. T1 ingestion took `239.387s`; live metadata dry-run, apply, and post-apply checks passed. No retrieval baseline, QA baseline, generation, analyzer, reranker, verifier, judge, T3, T4, or T5 run was performed.

### Current B5 structure-aware chunking and source-file coverage result

- Status: `PASS` overall. **B5.1R2 (pre-migration static closeout): `PASS`**; **B5.2 (live selective migration, T1 integrity verification, and post-B5 T2): `PASS`**.
- B5.1R2 fixes (commits `23a42fd` and earlier): intermediate upper-bounds validity (`ChunkingPolicy.within_upper_bounds`, no minimum) is now distinct from final eligibility (`embedding_input_is_valid`), so sub-minimum paragraphs/lines merge in source order into valid chunks instead of being dropped; unmergeable sub-minimum residuals remain on the non-eligible parent and are audit-visible. A coverage-based structural-container rule stops broad parents with structured searchable children (`source_file`, `python_script`, README roots, `sphinx_page`) from producing broad duplicate embedding chunks; README roots gain a preamble gap region; generic `.txt`/`.rst`/`.md`/`.yml` files keep paragraph/block → lines → hard-fallback coverage, including content beyond the legacy 20000/30000-character boundaries (fixture-proven). Curated alias provenance and `RelationResolver` exclude `b5_source_gap` objects. `apply_b5_selective_index` runtime bug fixed (`vertex_settings` constructed once and passed to `VertexAIClient`); read-only preflight validates settings, sparse factory receipt, schema-4 identity, artifacts, plan closures, reuse locators, selected inputs, and live counts before any mutation; a fully mocked `run=True` orchestration test covers reuse/changed/stale handling with stale deletion only after replacement writes.
- Final normalized candidate: `133075` objects, `104973` embedding-eligible, output hash `ff7f6102542bd68775caefba19d19d9ba0bb2452fe05a234344db40284538e73` (reproduced across two full ingestion runs); relations invariant (`64561` edges, `372139` candidates). Integrity: duplicate IDs 0, missing parents 0, orphan relation endpoints 0, locator containment violations 0, invalid line ranges 0, fabricated PDF lines 0, policy-invalid eligible 0. Source coverage (B4 trusted → final): C/C++ uncovered 1281 → 0 (gap regions 26092); build/config 44 → 0 (gap regions 638); Python 0 → 0 (gap regions 96); shell 0 → 0; README/Sphinx 0 → 0; PDF 0 → 0; generic long-file paragraph regions 1756; whole-corpus hard-fallback chunks 2; sub-minimum residuals 0.
- Churn attribution: every planned re-embed object has exactly one primary cause; `unknown/unclassified = 0`; cause total == dense total == `40547` (`new_source_gap_coverage` 19296, `intentional_structural_rechunk` 17492, `new_generic_file_coverage` 1756, `eligibility_gain` 2003). Supplementary: title-only 0; text changes 13572 (whitespace-only 1535, a B4-boundary-stripping artifact); same-ID input changes 13572; new coverage 25003; removed old derived chunks 2764; eligibility gained 2003 / lost 0; unchanged reused 64426; missing-receipt unchanged reused 11235.
- Revised selective impact plan: reuse `64426`; changed `13541`; new `25003`; eligibility gained `2003`; eligibility lost `0`; stale points `2731`; dense documents `40547`; sparse documents `40547`; batches `634`; rebuild ratio ≈ `0.502` of the B4 live points (all churn explained, no threshold tuning); identity unchanged schema 4 / `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`; collection never recreated. `b5-apply` dry-run preflight passed against the live B4 index.
- **B5.2 safety hardening:** selected-point resume skipping now requires a compatible dense receipt bound to the same `object_id` plus an exact current-B5 Qdrant payload for `object_id`, `source_id`, `source_version_id`, `object_type`, `title`, `text`, and `locator`; any uncertainty (old payload, missing receipt, or receipt owned by another object with identical input) forces a safe re-embed. `VertexAIClient` and the authoritative sparse encoder are constructed and the sparse receipt is verified before any live SQL/Qdrant mutation. Added T0 tests cover old-point-with-cache must re-embed, current-point-with-same-object-receipt may skip, other-object-receipt must not skip, missing receipt re-embeds, unchanged reuse never requires receipts, and Vertex/sparse constructor or receipt-mismatch failures happen before live mutation.
- **B5.2 live migration (run_id `17`):** started from pure B4 (`102875` SQL objects, `80698` Qdrant points). Planned selected documents `40547`; resume-verified already-current selected points `0`; actually dense-embedded `40547`; actually sparse-encoded `40547`; Qdrant points upserted `40547`; unchanged points reused `64426` (including `11235` missing-receipt points); stale points deleted `2731`; SQL records deleted `2764`; collection recreated `false`. Vertex stats: `40547` embedding requests/model calls, `0` token usage metadata returned by the embedding API; local FastEmbed document count `40547`.
- **B5.2 T1 live index integrity:** SQL `133075` objects, relations `64561`, candidates `372139`, aliases `2`, workflows `374`; duplicate object IDs `0`; missing relation endpoints `0`; eligible normalized objects `104973`; Qdrant points `104973`; missing expected point IDs `0`; unexpected/stale point IDs `0`; stale-deletion verified `0` remaining. All `40547` selected point payloads verified against normalized candidate fields; deterministic `1000`-point reuse sample and `1000`-point missing-receipt reuse sample verified; selected SQL rows verified. Dense dimension `3072`, sparse vector `sparse`/`idf`, schema `4`, fingerprint `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9` unchanged.
- Pre-B5 T2 authoritative before-state: run `b5-pre-retrieval-20260815`, mode `retrieval`, fixed 16 A3 IDs; Recall@5 `0.6944444444`; Recall@10 `0.8333333333`; Recall@20 `0.8333333333`; MRR `0.6`; combined candidate recall `0.9166666667`; final evidence recall `0.8333333333`; intent accuracy `0.9375`; exceptions 0 (applicable denominator 12). Selection manifest: `evaluation/baselines/manifests/b5_t2_retrieval_v1.json`. It was not rerun.
- Post-B5 T2: run `b5-post-retrieval-20260816`, mode `retrieval`, same fixed 16 IDs; applicable denominator 12 (4 `version_conflict` excluded). Recall@5 `0.7361111111`; Recall@10 `0.8333333333`; Recall@20 `0.8333333333`; MRR `0.5375`; combined candidate recall `1.0`; final evidence recall `0.8333333333`; intent accuracy `0.9375`; exceptions 0; model calls `48`; token usage `283871`. First-relevant-rank movement among supported applicable cases: improved `0`, unchanged `8`, regressed `2` (`g001` 1→2, `g013` 2→4); two applicable cases (`g038`, `g043`) had no first-relevant hit in either run and are not rank-supported. No index-integrity/migration defect was indicated; regression is a generic retrieval/ranking effect, not a deployment defect.
- T0 verification: `20` B5 migration/safety tests pass in `test_b5_index_migration.py`, plus `11` B3 sparse-factory tests and `7` B4 locator tests; `compileall` and `git diff --check` clean.
- Novel retrieval: `UNMEASURED` — no trustworthy human-authored novel dataset exists.
- Phase-B T3 retrieval-only comparison: `FAIL` — complete valid 80-question dev run; existing retrieval-mode development gate not satisfied (see T3 section below).

### Phase-B T3 full retrieval-only result

- Manifest: `evaluation/baselines/manifests/phase_b_t3_retrieval_v1.json`.
- Run: `phase-b-t3-retrieval-20260816`, mode `retrieval`, split `dev`, 80 approved development questions; applicable `73`, excluded `7` (`g012,g026,g042,g058,g077,g096,g108`, all `version_conflict`). No acceptance/holdout questions were used.
- Candidate identity: Git `2341a2e2dc5960212c4b335fd97513633e375012` (dirty: docs-only wording), corpus `133075` objects / `104973` eligible, object hash `ff7f6102542bd68775caefba19d19d9ba0bb2452fe05a234344db40284538e73`, index schema `4` / fingerprint `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`, dense `gemini-embedding-2` / `3072`, sparse `Qdrant/bm25` / `sparse` / `idf`, analyzer/reranker `gemini-3.7-flash`, Gold v2.6 hash `b5406e36c64ee664f9e2ff9c0f42e354feb7164c81d8f1c7551d8f2ed1d0b687`.
- Overall metrics: Recall@5 `0.8801369863`; Recall@10 `0.9748858447`; Recall@20 `0.9863013699`; MRR `0.7285388128`; combined candidate recall `1.0`; final evidence recall `0.9828767123`; critical final evidence recall `0.9828767123`; intent accuracy `0.9875`; expected-status accuracy `0.9125`; exceptions `0`.
- Rank distribution (question-level first relevant rank, applicable 73): rank1 `39`, rank2 `22`, rank3 `7`, rank4–5 `4`, rank6–10 `0`, rank11–20 `0`, no top-20 hit `1`; rank-1 fraction `0.5342`, median `1`, mean `1.708`.
- Failure taxonomy: Q1 `1`, Q2 `0`, R1 `0`, R2 `3`, R3 `2`, unclassified `0`. Material Recall@10/final-evidence misses: `g006` (R2), `g011` (R3), `g016` (R2), `g025` (Q1), `g072` (R2), `g085` (R3).
- Identifier-heavy predeclared subset (dev intersection of B1 set): `g015,g027,g028,g029,g041,g042,g059,g060`; applicable `7`; Recall@5 `0.8333`, Recall@10 `1.0`, Recall@20 `1.0`, MRR `0.7190`, combined candidate recall `1.0`, no R1/R2/R3 failures.
- B5 coverage diagnostic: B5-added coverage objects appear in candidate pools in `71/73` applicable questions, top-5 in `19/73`, final evidence in `32/73`, and are relevant Gold hits in `3/73` (causal attribution limited).
- T2 overlap stability: `g001` T3 rank `2` (same as post-B5 T2), `g013` T3 rank `2` (post-B5 T2 was `4`; variance observed, not a tuning target).
- Development gate: `passed=false`; failing checks are `critical_evidence_coverage` (`0.9829 < 1.0`) and `expected_status_accuracy` (`0.9125 < 0.975`). Other retrieval-mode development checks pass.
- Cost: `240` runtime model calls (`0` judge), `1403061` tokens, `0` document embeddings, `0` QA/verifier/judge calls.
- Systematic ranking assessment: `NO EVIDENCE OF SYSTEMATIC REGRESSION` — high Recall@10/20, combined candidate recall `1.0`, R1 `0`, rank-1 fraction `0.534`, and per-intent MRR do not indicate a broad Phase-B ranking regression. The T3 `FAIL` is a development-gate failure, not a systematic-ranking regression signal.

### Phase-B T3.1 evaluator semantics and English product-scope rescore

- Artifact: `evaluation/baselines/manifests/phase_b_t3_1_retrieval_semantics_v1.json`.
- Source run: `phase-b-t3-retrieval-20260816`; source records immutable; zero additional model calls/tokens.
- Evaluator defect confirmed: retrieval mode synthesizes `answered` whenever evidence exists, so 7 Gold `insufficient_evidence` dev cases were scored as ordinary answered cases and caused original `expected_status_accuracy = 0.9125`.
- Retrieval-mode semantic fix: `expected_status_accuracy` is now N/A in retrieval mode; version-conflict rejection remains hard; ordinary Recall/MRR/final-evidence metrics apply only to Gold `answered` cases; `insufficient_evidence` cases are no longer ordinary retrieval cases. QA/full expected-status measurement/gating is unchanged.
- Product language scope: Gold dev distribution `en=51`, `zh=20`, `mixed=9`; deterministic English product selector is `split=dev AND language=en AND review_status=approved`; exact English count `51`; zh/mixed (`29`) remain diagnostic outside the formal English gate. Gold was not modified.
- Corrected all-language diagnostic: `80` source records; ordinary answered-applicable `66`; insufficient-evidence `7`; version-conflict `7`; Recall@5 `0.8674242424`; Recall@10 `0.9722222222`; Recall@20 `0.9848484848`; MRR `0.7426767677`; combined candidate recall `1.0`; final evidence recall `0.9810606061`; critical final evidence recall `0.9810606061`; intent accuracy `0.9875`; expected-status accuracy `N/A`; version-conflict rejection `true`; corrected diagnostic gate `FAIL` (critical evidence coverage < 1.0).
- English product-scope T3: `51` cases; answered-applicable `43`; insufficient-evidence `4`; version-conflict `4`; Recall@5 `0.9147286822`; Recall@10 `0.9651162791`; Recall@20 `0.9767441860`; MRR `0.7953488372`; combined candidate recall `1.0`; final evidence recall `0.9767441860`; critical final evidence recall `0.9767441860`; intent accuracy `0.9803921569`; expected-status accuracy `N/A`; formal product gate `FAIL` (critical evidence coverage < 1.0).
- English failure ownership: Q1 `1` diagnostic (`g025`, an `insufficient_evidence` case outside ordinary retrieval metrics), Q2 `0`, R1 `0`, R2 `2` (`g006`, `g016`), R3 `1` (`g011`). Exact formal critical blockers: `g011.e1` (R3, final evidence drops a top-10 critical object) and `g016.e2` (R2, critical object ranked 11/10 and not selected).
- Multilingual separation: `g072` (zh, R2) and `g085` (zh, R3) remain recorded as all-language diagnostics and no longer participate in the English product gate.
- Next roadmap task: targeted critical-evidence investigation for the two English formal blockers (`g011` R3 and `g016` R2); do not start C1.

### Phase-B T3.1R1 product-language recalibration and 59-case rescore

- Calibration artifact: `evaluation/baselines/manifests/phase_b_t3_product_language_scope_v2.json`.
- Rescore artifact: `evaluation/baselines/manifests/phase_b_t3_1r1_product_rescore_v1.json`.
- Source run: `phase-b-t3-retrieval-20260816`; source records immutable; zero additional model calls/tokens.
- Language audit: raw Gold dev distribution `en=51`, `zh=20`, `mixed=9`. The 9 raw mixed IDs are `g102,g105,g108,g110,g112,g113,g114,g115,g119`. Reviewed effective language: `g102 = non_en` (Chinese grammar with English identifiers); `g105,g108,g110,g112,g113,g114,g115,g119 = en` (pure English natural language). All 20 raw `zh` cases are non-English; no unexpected raw-zh English mislabel was found.
- Effective formal English product scope: `59` cases (`51` raw English + `8` recalibrated mixed-to-English). Non-English dev scope: `21` (`20` raw zh + `g102`).
- Recalibrated status counts: answered `49`, insufficient-evidence `5`, version-conflict `5`.
- Recalibrated product metrics: Recall@5 `0.9047619048`; Recall@10 `0.9693877551`; Recall@20 `0.9795918367`; MRR `0.7625850340`; combined candidate recall `1.0`; final evidence recall `0.9795918367`; critical final evidence recall `0.9795918367`; intent accuracy `0.9830508475`; expected-status accuracy `N/A`.
- Formal product gate: `FAIL` — only `critical_evidence_coverage` remains below `1.0`.
- Failure taxonomy (actual failures only): Q1 `1` (`g025` diagnostic), Q2 `0`, R1 `0`, R2 `2` (`g006`, `g016`), R3 `1` (`g011`), unclassified `0`.
- Genuine critical evidence misses: `g011.e1` (R3; final selection drops a top-10 critical object) and `g016.e2` (R2; critical object is reranked at 1-based rank 10, just outside top-10 and not selected). Rank presentation now distinguishes 0-based index from 1-based human rank.
- Reporting-path integration: `report_evaluation()` now emits `product_development_gate` for compatible official full-dev runs when a reviewed calibration artifact is present; the all-language `development_gate` remains as diagnostic.
- Multilingual separation: all `21` non-English dev cases remain diagnostic; `g072`/`g085` (zh) and `g102` (mixed→non_en) do not participate in the formal English gate.
- Next roadmap task: `T3.2 — Critical-evidence mechanism investigation` for the final calibrated formal blockers `g011` and `g016`; do not start C1.

### Phase-B T3.1R2 calibration binding and rank-stage closeout

- Closeout artifact: `evaluation/baselines/manifests/phase_b_t3_1r2_calibration_rank_closeout_v1.json`.
- Calibration binding: calibration `phase_b_t3_product_language_scope_v2` is compatible with active Gold v2.6 (`b5406e36c64ee664f9e2ff9c0f42e354feb7164c81d8f1c7551d8f2ed1d0b687`) and `split=dev`; override IDs/raw languages validated; declared `formal_english_ids`/`non_english_ids` exactly equal independently derived ID sets (`59` / `21`).
- Reporting completeness: official full-dev runs now support both no-`case_ids` and explicit complete all-dev `case_ids`; incomplete subsets and arbitrary English-only subsets cannot produce a complete formal product gate.
- Rank-stage semantics: channel candidates (`rankings`), fused order (`fusion_scores`), LLM reranker (`reranked_object_ids`), final deterministic ranked stage (`ranked_object_ids`), and final evidence selection are now explicit and distinct. Recall@K uses `ranked_object_ids` (final ranked stage).
- Stage traces for final formal blockers:
  - `g011.e1` / `object.2de0c11066dd97bc1177de1c`: combined present; fused rank `7`; reranker rank `9`; final ranked rank `9`; final top-10 `true`; final selected `false` → R3.
  - `g016.e2` / `object.f516ef98aeecd335607ac0f6`: combined present; fused rank `30`; reranker rank `10`; final ranked rank `11`; final top-10 `false`; final selected `false` → R2 (post-rerank deterministic ordering drops it just outside top-10).
- Formal metrics unchanged: Recall@5 `0.9047619048`; Recall@10 `0.9693877551`; Recall@20 `0.9795918367`; MRR `0.7625850340`; combined candidate recall `1.0`; final evidence recall `0.9795918367`; critical final evidence recall `0.9795918367`; intent accuracy `0.9830508475`.
- Formal product gate remains `FAIL` because critical evidence coverage `< 1.0`.

### Phase-B T3.1R3 frozen fused-rank provenance and dynamic dev-completeness closeout

- Closeout artifact: `evaluation/baselines/manifests/phase_b_t3_1r3_fused_rank_dev_completeness_closeout_v1.json`.
- Frozen fusion-rank audit: persisted `fusion_scores` dict key order is not authoritative after key-sorted serialization. `stage_trace_for_object()` now uses only frozen `RetrievalTrace.fused_candidates` for fused rank; when unavailable, `fused_rank_1based = null` and `fused_rank_source = unavailable`.
- Corrected stage traces for final formal blockers:
  - `g011.e1` / `object.2de0c11066dd97bc1177de1c`: combined present; fused rank `27` (authoritative trace); reranker rank `9`; final ranked rank `9`; final top-10 `true`; final selected `false` → R3.
  - `g016.e2` / `object.f516ef98aeecd335607ac0f6`: combined present; fused rank `22` (authoritative trace); reranker rank `10`; final ranked rank `11`; final top-10 `false`; final selected `false` → R2 with diagnostic substage `R2_post_rerank_deterministic_ordering`.
- Dynamic dev completeness: full official dev execution is now derived from exact approved dataset ID sets; the hard-coded `80` check is removed and replaced by data-derived completeness. A synthetic non-80 (5-case) dev test proves no hidden count dependency.
- Formal metrics remain unchanged: Recall@5 `0.9047619048`; Recall@10 `0.9693877551`; Recall@20 `0.9795918367`; MRR `0.7625850340`; combined candidate recall `1.0`; final evidence recall `0.9795918367`; critical final evidence recall `0.9795918367`; intent accuracy `0.9830508475`.
- Formal product gate remains `FAIL` because critical evidence coverage `< 1.0`; failure taxonomy remains Q1 `1`, Q2 `0`, R1 `0`, R2 `2`, R3 `1`, unclassified `0`.

### Phase-B T3.2 critical-evidence mechanism investigation

- Investigation artifact: `evaluation/baselines/manifests/phase_b_t3_2_critical_evidence_mechanism_investigation_v1.json`.
- Production stage map: channel candidates → fusion → LLM reranker → deterministic post-rerank ordering (`hinted_first` + `required_first` + `symbol_first` + reranked/fused) → `ranked_object_ids` → final evidence selection (duplicate locator, per-source cap, per-type budget, limit 12) → evidence.
- g011 mechanism: final-selection `source_diversity_cap` (`max_per_source=4`). `object.2de0c11066dd97bc1177de1c` is final ranked rank 9 but four same-source objects were already selected, so it is excluded with `source_diversity_cap`; critical-group coverage is not visible to the selector. Primary class `R3_source_diversity_cap`.
- g016 mechanism: post-rerank `symbol_first` promotion. `object.24323bf526f94cd30b58ab41` (PndDpmGenerator.cxx source-gap chunk) is reranker rank 14 but promoted to final rank 3 by exact-symbol priority, displacing `object.f516ef98aeecd335607ac0f6` from reranker rank 10 to final rank 11. Primary class `R2_post_rerank_deterministic_ordering`; the displacer is not the Gold-critical object.
- Cross-case scan (49 applicable formal English cases): 40 cases have reranker/final top-10 composition changes; 8 Gold-relevant promotions into top-10, 2 Gold-relevant demotions out of top-10; 5 critical promotions, 1 critical demotion; 1 R3-like case (`g011`); selector preserves all critical evidence in 47 cases and drops critical evidence in 2 (`g011`, `g016`).
- Shared-root-cause assessment: partially shared — both are deterministic priority/budget mechanisms without coverage awareness, but they operate in different production stages (final evidence selection vs post-rerank ordering).
- Mechanism classification: both are intended generic tradeoffs, not implementation bugs or evaluator artifacts.
- Recommended next tasks: `T3.3A` (generic final-evidence selection coverage awareness, recommended first) and `T3.3B` (generic post-rerank deterministic-ordering coverage awareness). No production fix was implemented.
- Formal metrics/gate remain unchanged: 59-case metrics identical; formal product gate remains `FAIL`.

### Phase-B T3.3A / T3.3A-R1 final-evidence soft-budget correction

- T3.3A artifact (historical first attempt): `evaluation/baselines/manifests/phase_b_t3_3a_final_evidence_soft_budget_v1.json`.
- T3.3A-R1 closeout artifact: `evaluation/baselines/manifests/phase_b_t3_3a_r1_bounded_soft_budget_closeout_v1.json`.
- Production change: `src/panda_agent/retrieval.py` — final evidence selection extracted to `select_final_evidence()`; T3.3A-R1 adds explicit bounded overflow accounting: at most one soft overflow per source and one per source type, both-cap violations consume both allowances, and soft admissions are returned separately from rejected exclusions. `retrieval_trace.py` persists `soft_budget_admissions`.
- T3.3A defect confirmed: the original implementation was effectively unbounded and recorded soft-admitted candidates as excluded.
- Bounded frozen selector-local replay: PRE and POST final/critical evidence recall both `0.9591836735` on the canonical top-30 snapshot; `g011` and `g016` are **not recovered** by the strictly bounded one-overflow rule; local critical misses remain `g006,g011,g016`.
- Replay baseline fidelity: authoritative PRE is `0.9795918367`, replay PRE is `0.9591836735`; `baseline_faithful=false`; therefore no global post-fix projection is claimed.
- Diversity for bounded replay: mean unique sources `2.90 -> 2.88`; median `3`; 2 cases lose a source, 1 gains; soft admission events: source `26`, type `17`, both `10`, unique cases `44`.
- Ranking metrics unchanged (Recall@5/10/20, MRR, combined candidate recall, intent accuracy).
- Authoritative formal Phase-B product T3 remains `FAIL`; deterministic post-fix formal-gate projection is `INCONCLUSIVE`; T3.3B gate-blocker status is `INCONCLUSIVE`.

### Phase-B T3.3A-R2 two-pass backfill closeout

- T3.3A-R2 artifact: `evaluation/baselines/manifests/phase_b_t3_3a_r2_two_pass_backfill_closeout_v1.json`.
- Production change: `src/panda_agent/retrieval.py` now uses a two-pass selector: Pass 1 applies hard budgets only; Pass 2 backfills Pass-1 budget-rejected required-source candidates in canonical rank order using only unused total evidence capacity. `retrieval_trace.py` persists `backfill_admissions`.
- Frozen selector-local replay: PRE final/critical evidence recall `0.9591836735`; POST `0.9693877551020`; g016 locally recovered; g011 **not recovered** because Pass 1 already filled the full evidence limit with lower-ranked candidates, leaving no unused capacity for backfill.
- Replay baseline fidelity remains false (`0.9591836735` vs authoritative `0.9795918367`); therefore deterministic post-fix formal-gate projection is `INCONCLUSIVE`.
- Diversity: hard-pass evidence fully preserved; final mean unique sources `2.94`, median `3`; 0 cases lose source diversity, 2 gain; backfill events `133`, unique affected cases `36`, mean per affected case `3.69`, max `8`.
- Authoritative formal Phase-B product T3 remains `FAIL`; T3.3B gate-blocker status remains `INCONCLUSIVE`.

### Phase-C C1 deterministic pre-parse implementation

- Artifact: `evaluation/baselines/manifests/phase_c_c1_deterministic_preparse_v1.json`.
- Source commit: `22cde4a761c28b0e6b5ae7cba185395e233aeba3`; the worktree also contains the four verified C1 code/test changes owned by Terra.
- Initial implementation direction: `INCONCLUSIVE` after review. `DeterministicQueryParse` and per-field provenance run before `generate_json`; `deterministic_context` carries fixed intent, known deterministic fields, unresolved fields, and provenance. A fixed high-confidence intent is authoritative. Existing repository/SHA/version, scope, accepted-alias, and reviewed-expansion signals are pre-parsed; unresolved free-form semantic fields remain LLM-owned. Diagnostics are exposed in `RetrievalPlan.analysis_diagnostics`.
- Measured boundary: C1 reuses these existing deterministic signals; it does not claim a new free-form path/`Class::method` parser or a new benchmark-specific route.
- Analyzer-call policy: no valid current query skips the analyzer because unresolved free-form semantic fields remain; each valid current query makes one analyzer call. This is the observed C1 behavior, not a claim of analyzer-call reduction.
- Verification: `18` targeted unittest tests passed (`15` retrieval and `3` prompt-security); `compileall` and `git diff --check` passed. Live analyzer smoke was not run. Calls and tokens were `0`; ranking, reranking, index, storage, embedding, QA, and selector behavior were not changed.
- Scope boundary: this is a T0 implementation check only; no benchmark metrics were collected and no live service was called.
- Novel retrieval generalization: `UNMEASURED`; no trustworthy human-authored novel dataset exists.

### Phase-C C1-R1 fixed/fallback ownership closeout

- Artifact: `evaluation/baselines/manifests/phase_c_c1_r1_fixed_fallback_ownership_closeout_v1.json`.
- Source C1 commit before R1: `ae567aeeccd9cbc835e0f2803c3641358c1dce3b`; the dirty R1 candidate changes only `src/panda_agent/retrieval.py` and `tests/unit/test_retrieval.py`.
- Reviewed defects: weak `setdefault` scope fallbacks became fixed overrides; fixed intent remained required in the analyzer schema; diagnostics conflated partial/fixed/unresolved ownership; normalized repository substring matching over-triggered larger tokens.
- Final contract: fixed > LLM > fallback; fixed intent is removed from actual response-schema properties/required, while ambiguous intent remains required and LLM-owned. Fixed, fallback, known-partial, unresolved, and mixed states align with per-entry provenance ownership. The repository boundary matcher accepts explicit `PandaRoot` and rejects `PandaRootedConfiguration`.
- Preserved behavior: explicit repository+SHA, aliases/expansions, prompt security, version conflicts, and plan semantics remain intact. C1-R1 is `PASS`; C1 overall is `PASS`.
- Verification and cost: `22` targeted tests passed (`19` retrieval and `3` prompt-security); exact discover commands, three-file `compileall`, and `git diff --check` passed. External/model/token, Retriever, reranker, embedding, QA, SQL, Qdrant, index, benchmark, and live-smoke counts are all `0` or not run.

### Phase-C C2 narrow and auditable query-analyzer contract

- **Status:** `PASS`; artifact: `evaluation/baselines/manifests/phase_c_c2_narrow_auditable_analyzer_v1.json`.
- **Source and prompt identity:** source/base commit SHA `c2f933b287e52d76947a3865e2527d2349e5ec27`; prompt version `3.7.0`.
- **Implementation contract:** The analyzer returns an additive `AnalyzerSemanticDelta`, not a `RetrievalPlan`. Fixed deterministic intent is omitted from the response schema; unresolved intent remains analyzer-owned; merge precedence is fixed > LLM > fallback. Query-grounded concepts, symbols, repository additions, version mentions, and scopes retain support spans. Exact symbols are preserved, unsupported items are rejected, and bare version tokens remain unbound unless the query explicitly associates them with a repository.
- **Ownership and diagnostics:** `deterministic_parse`, `analyzer_llm_called`, `analyzer_semantic_output_fields`, `analyzer_raw_semantic_delta`, `analyzer_accepted_semantic_delta`, `analyzer_rejected_items`, `analyzer_item_support`, `unbound_version_tokens`, and `analyzer_final` are persisted in `RetrievalPlan.analysis_diagnostics`. The old `analyzer_unresolved_fields` key is removed.
- **T0 evidence:** `39/39 PASS` (retrieval `34/34`, prompt-security `4/4`, exact QA prompt `1/1`), with zero external/model calls.
- **Analyzer-only T2 evidence:** `10/10 PASS` using `gemini-3.7-flash` in `global`; analyzer model calls `10`, successful structured responses `10`, tokens `17173`, mean `1717.3` tokens/call, failures `0`, retries `0`. ADC and harness pre-request failures are environment history only: `0` remote calls and `0` tokens.
- **Cost and impact:** Retriever/reranker/query embeddings/document embeddings/QA/verifier/judge/SQL/Qdrant/index mutation `0`; reindex/reembedding `no`. The query-understanding analyzer contract changed `yes`; dense/sparse query construction changed `no`; retrieval ranking intentionally changed `no`; selector/index/corpus changed `no`.
- **Review and limitations:** Sol's final live review was `PASS`; deterministic local replay compared `90` stored sections with `0` mismatches. This is an analyzer-only T2 result, not a global cost-saving claim or pseudo-Gold result; no `g011`/`g016` targeting was introduced, no T3/T4/T5, retrieval benchmark, or index work was run. C3-R1 remains historical `INCONCLUSIVE`; C3-R2 is now `INCONCLUSIVE`; C4 remains `NOT_STARTED`.

### Phase-C C3-R1 dense-only TTY closeout

- Artifact: `evaluation/baselines/manifests/phase_c_c3_r1_dense_ab_evaluation_integrity_closeout_v1.json`.
- Execution evidence: the completed TTY capture was extracted read-only from the rollout JSONL, had `exit_code=0`, and was not rerun during closeout. The artifact preserves the complete JSON record for all 16 cases, including raw query, semantic components, change flag, canonical PRE/POST filter, same-plan/isolation checks, top-20 object IDs, per-case metrics, rank effects, and contamination audit.
- Locked IDs: primary `g001,g013,g044,g059,g027,g105,g110,g002,g014,g047,g060,g028`; reserves `g003,g015,g050,g029`; all 16 were executed in the locked order. Exclusions `g011` and `g016` were preserved.
- Treatment coverage: 12 primary cases and 4 reserves; `SemanticQuery.text` changed for `g110` and `g050` only (`2/16`), while `14/16` remained unchanged. The preregistered minimum is 3 changed cases, so the treatment gate is not met.
- Retrieval metrics (PRE → POST): Recall@5 `0.5208333333 → 0.5208333333`; Recall@10 `0.6979166667 → 0.6979166667`; Recall@20 `0.6979166667 → 0.6979166667`; MRR `0.3059771825 → 0.2872271825`; critical coverage `0.6979166667 → 0.6979166667`; new critical misses `0`.
- Isolation and cost: all 16 cases reused the same analyzer plan and canonical-equivalent PRE/POST filters; analyzer calls `16` (`29101` tokens), query embeddings `32`, dense Qdrant reads `32`, and sparse/reranker/judge/write/index-mutation operations `0`.
- Final result: `INCONCLUSIVE`, not `PASS`, solely because treatment coverage is `2/16 < 3`. At that historical boundary C4 remained `NOT_STARTED`; the subsequent authorized follow-up was C3-R2.

### Phase-C C3-R2 treatment-qualified screening closeout

- Artifact: `evaluation/baselines/manifests/phase_c_c3_r2_treatment_qualified_dense_ab_closeout_v1.json`; C3-R1 artifact and historical result remain preserved unchanged.
- Screening evidence: the completed TTY run used the preregistered fixed order, executed exactly 20 analyzer-only cases, and stopped at the absolute screening limit. Five cases qualified (`g018,g113,g055,g114,g115`), below the target of six; no dense embedding or Qdrant ranking was inspected during screening.
- Qualified activations: `g018` accepted concept `run luminosity fit`; `g113` accepted concept `trace mismatch`; `g055` fixed scope `efficiency=angular_acceptance_vs_longitudinal_profile`; `g114` and `g115` accepted scope `efficiency=longitudinal_profile`. No contamination was observed.
- Cost and isolation: analyzer calls `20`, analyzer tokens `36098`, query embeddings `0`, dense Qdrant reads `0`, and all sparse/exact/paper/workflow/graph/fusion/reranker/selector/QA/judge/write/index-mutation operations `0`. The live index preflight passed with 104973 points, schema `4`, dense 3072, `gemini-embedding-2`, and the expected fingerprint.
- Final result: `INCONCLUSIVE`, not `PASS`, because the preregistered six-case treatment target was not reached within 20 screenings. Stage B metrics are intentionally N/A; C4 remains `NOT_STARTED`.

### Phase-C C3-R3 exhaustive treatment-qualified dense closeout — 2026-08-21

- Artifact: `evaluation/baselines/manifests/phase_c_c3_r3_exhaustive_treatment_qualified_dense_evaluation_v1.json`; preregistration source commit `9f856044b062fb666cd0b357982399c7f59a6161`, resumed source HEAD `59b2decab9ed661c77b482f46b18b4d86836a270`; artifact status `CLOSED_INCONCLUSIVE`, result `INCONCLUSIVE`. C3-R1 and C3-R2 artifacts and outcomes remain preserved and are excluded from the C3-R3 aggregate denominator.
- Preregistration was locked before the first remote call. It preserved the C3 history, carried forward the five blinded qualified cases (`g018,g113,g055,g114,g115`), locked the remaining 11 IDs (`g021,g034,g010,g022,g035,g023,g036,g024,g037,g039,g040`), set no treatment-count threshold, and froze the dense-only PRE/POST gates. The C3 semantic strategy, prompt, and production implementation were not changed.
- T0 regression verification used the bundled-Python in-memory direct-check because standard pytest was unavailable: `12/12 PASS`, with no dependency installation and no external/model calls. Raw-question preservation, analyzer concept/scope ownership, contamination/provenance guards, fixed/LLM/fallback scope handling, metadata non-injection, dense/sparse isolation, deterministic output, deduplication, and symbol-duplication checks passed.
- The earlier attempt was **environment-blocked before Stage A** when `http://127.0.0.1:6333` was unavailable. On resume, the authoritative `panda_knowledge_v1` collection was reachable and populated (`green`, `104973` points, `3072`-dimensional dense `Cosine`, schema `4`, fingerprint `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`), with payload `object_id` available and identity compatible with the preregistration. No empty substitute collection was used.
- Stage A screened the same locked order (`g021,g034,g010,g022,g035,g023,g036,g024,g037,g039,g040`) exactly once using the production analyzer and `build_semantic_query()` only. All `11` cases completed; `g039` was the only new treatment-qualified case, giving five carried-forward cases plus `g039`. Analyzer calls were `11` (`19878` tokens); three sandbox ADC attempts produced no valid remote result and were not counted. The first nine valid results lost their plan snapshots after a runner serialization error; no duplicate calls were made.
- The five pre-registered carried-forward cases used the allowed maximum `5` reconstruction analyzer calls (`9839` tokens). `g113,g055,g114,g115` matched their frozen R2 SemanticQuery snapshots; `g018` did not, so its historical frozen text was retained and the mismatch is recorded as an evidence-integrity limitation. All six required cases (`g018,g113,g055,g114,g115,g039`) were frozen before embeddings. Dense-only PRE/POST used raw question versus frozen `SemanticQuery.text`, the same plan/filter/collection/model/dimensions, `12` query embeddings, and `12` dense Qdrant reads; sparse/exact/paper/workflow/graph/fusion/reranker/selector/QA/judge and all writes were `0`.
- PRE → POST Recall@5 `0.0833333333 → 0.0833333333`, Recall@10 `0.1666666667 → 0.0833333333`, Recall@20 `0.3333333333 → 0.25`, MRR `0.0873737374 → 0.0754385965`, and critical coverage `0.3333333333 → 0.25`. Rank counts were improved `0`, recovered `0`, unchanged `1`, no-hit-both `3`, regressed `2`, lost-hit `0`; positive direction `0`, negative direction `2`; informative `3/6`; contamination `0`. Raw gates were Recall@20 `FAIL`, critical evidence `FAIL`, lost-hit `PASS`, directional rank `FAIL`, informativeness `PASS`, contamination `PASS`.
- Historical C3-R1 diagnostics remain separate and are not in the R3 denominator: `g110` no-hit → no-hit and `g050` rank `2` → `5`. C3-R3 closes `INCONCLUSIVE`, not a complete `PASS`/`FAIL` decision, because the first nine Stage-A plan snapshots were lost after valid analyzer calls and `g018` could not be semantically reconstructed to its blinded snapshot; the observed Stage-B gates were also not met. C3 overall remains `INCONCLUSIVE`. No C3-R4 or new Gold sampling round was started automatically; evidence-integrity review or repair requires separate authorization, and C4 remains `NOT_STARTED`.
- Limitations remain: C2 concepts are conservative; the raw question is mandatory and first-class; C3 activation is sparse; this is a conditional dense-only shadow evaluation rather than formal T3 and does not measure novel retrieval generalization; reviewed expansions remain elsewhere in retrieval; `g011` remains deferred to Phase E; no C4 work was started.

### Current small E2E baseline

- Run: `generalization-a3-stratified-qa-20260813`.
- Mode/cases: `qa`, 16 approved English Gold questions; runtime generation and verification enabled, external judge disabled.
- Cost: 76 runtime model calls, 819,872 tokens, 0 external-judge calls.
- Measured: Recall@5 `0.6041666667`; Recall@10 `0.75`; Recall@20 `0.75`; MRR `0.65`; combined candidate recall `0.875`; final-evidence recall `0.7083333333`; expected-status accuracy `1.0`; citation integrity `1.0`; identifier hallucination rate `0.0`; no exceptions.
- Answer-point coverage is N/A because the external rubric judge was deliberately disabled.
- External-rubric contradiction and unsupported-claim metrics were likewise not measured; corrected package artifacts represent all three metric families as N/A rather than synthetic zero/clean values.

The retrieval and QA measurements are unchanged. A3.1 corrects only metric representation, portable artifact paths, consistency metadata, and measured-execution provenance wording; historical model outputs remain untouched.

## Novel dataset state

- `novel_dev`: 28 loaded records (dataset lineage `0.3.0` / `novel-v1-dev-0.3.0`, identity `novel-v1-dev-expansion`, status `COMPLETE`): 28 human-approved and 28 `split_frozen` records in 28 independent families. The N1 pilot history and N2-A/N2-B review histories remain preserved; the active split is frozen.
- Human-approved: 28. Frozen: 28 (N1 historical approvals, N2-A approvals at 2026-08-24T01:50/02:05+02:00, n027 accepted 2026-08-24T02:42+02:00, and n026/n028/n029/n030/n031 accepted on final re-review at 2026-08-25T22:11:57+02:00). Rejected: 0. Pending: 0.
- `novel_validation`: 0 / not started.
- `novel_holdout`: not created / externally managed; the runner supports loading it from an external path.
- Empty novel JSONL artifacts are schema/placeholders, not measured results.
- Curation governance: N0 `COMPLETE`; `docs/NOVEL_DATASET_CURATION_CONTRACT.md` is authoritative; N1 `PASS / COMPLETE` (frozen pilot; no generalization claim); N2 `PASS / COMPLETE`; N2-A `COMPLETE`; N2-B `COMPLETE`; `novel_dev` `COMPLETE / SPLIT_FROZEN`.
- Next curation step: none selected by this task. Any novel evaluation or novel_validation curation requires a new explicit authorization; C8 remains separately authorized and its current lifecycle is preserved below.

## Known limitations

- The A3 stratified bootstrap baseline does not cover every intent in depth; Phase-B T3 now measures all approved development intents, including `data_flow`, `module_structure`, and `troubleshooting`.
- The current baseline measures exposed English Gold behavior, not genuinely novel-question generalization.
- Historical E2E and current baseline identities differ, so their metric differences are not a controlled before/after comparison.

## Next authorized roadmap task

**N2 finalization is complete.** The package `N2B_BATCH2_REVIEW_PACKAGE.md` records Li's first 1 ACCEPT / 5 REVISE decision, the R1 corrections, and the final 5 ACCEPT re-review; all 28 active novel_dev records are now split_frozen. N1 remains `PASS / COMPLETE`; N2 is `PASS / COMPLETE`; C8 is `ACTIVE` with `C8-A1 = PASS_AFTER_CONTRACT_FIDELITY_REPAIR` and `C8-A2 = NEXT_ELIGIBLE / NOT_STARTED` (per the current C8 sections above). No novel evaluation was run or authorized by this freeze.

### Historical pre-N0 roadmap summary

The following paragraph preserves the pre-N0 closeout context and is superseded by the current N1 handoff above.

`C3-A1`, `C3-A2`, C3-A overall, and current C3 are `PASS` for the revised raw-preserving architecture. No C3-R4, new Gold sampling round, T3, T4, or T5 was started. The historical C3-R1/R2/R3 artifacts and conclusions remain preserved; the legacy single-vector semantic replacement is superseded and not accepted for production. `RawDense` is production-authoritative, `SemanticDense` is auxiliary/experimental and explicit shadow-only, and its production fusion decision is deferred to C6. C4-A1 is `PASS`; the C4 evaluation verdict is `INCONCLUSIVE` and the C4 lifecycle state is `CLOSED_INCONCLUSIVE` after the `PASS` C4-A3 architectural closeout (no live sparse stage or outcome metric ever ran). Production sparse remains the exact raw question and `LexicalQuery` is an experimental/shadow abstraction; no sparse benefit is claimed. C5 — Entity-first exact retrieval has evaluation verdict `INCONCLUSIVE` and lifecycle `CLOSED_INCONCLUSIVE` after the `PASS` C5-A3 architectural closeout (C5-A0 `DONE`, C5-A1 `PASS`, C5-A2 `INCONCLUSIVE`; descriptive evidence `UNAVAILABLE`; identity-strength finding recorded; production exact remains `LEGACY_EXACT` with `EntityResolver` retained experimental/shadow). C6 — Multi-channel fusion evaluation is `COMPLETE`: C6-A0 `PASS`, C6-A1 `PASS`, and C6-A1R1 `PASS` as the pre-outcome product-scope/plan-fidelity correction (the 59-case formal-English scope inherited from `phase_b_t3_product_language_scope_v2.json`; `PLAN_FIDELITY_BLOCKED` with `0/46` current-plan-compatible cases). `C6-A1R2` refreshed current-plan candidate coverage (30-case core + 1 semantic supplement, `31/31` captured) and, after the provenance preflight audit found 3 core cases captured under unfaithful empty-default plan fields, the authorized provenance repair rebuilt all six affected cases from the faithful C3-R3 full plans into authoritative replay v2 (34 rows; core-30 identical; P0 integrity `30/30`; unaffected parity `27/27`), so `C6-A1R2 = PASS_AFTER_PROVENANCE_REPAIR` (`semantic_a2_evidence_eligible=true` after the semantic-cohort correction: 8 semantic-active faithful cases over 4 intents). `C6-A2` `PASS` frozen policy comparison (P3 sparse-heavy passes all 10 hard gates with R@20 `1.0`/critical `1.0`/MRR `+0.0334`; P1/P2/P4 fail; P5 prefix-identical 8/8 with no meaningful expansion; `SEMANTIC_CONTRIBUTION = INSUFFICIENT` with SemanticDense `KEEP_DISABLED`; `INTENT_AWARE_ELIGIBLE = true` with the evaluation-only `C6_INTENT_AWARE_V1` mapping), confirmed unchanged by the `PASS` critical-miss semantics audit (corrected Gate-5 group identity; P3 remains `PASS_ALL_GATES`). `C6-A3` `PASS` — the frozen production-role decision keeps P0 CURRENT production-authoritative, retains P3 SPARSE_HEAVY and `C6_INTENT_AWARE_V1` as development-supported candidates blocked from activation by absent novel corroboration, rejects P1/P2/P4 as standalone global alternatives, gives P5 no production role, keeps SemanticDense `KEEP_DISABLED`, and leaves production fusion and production code `UNCHANGED`; the C6 lifecycle is `COMPLETE`. C7 is `COMPLETE`: the original A3 attempt remains historical `INCONCLUSIVE / PRE_OUTCOME_INFRASTRUCTURE_FAILURE`, C7-A3R1 is `PASS`, C7-A3 is `PASS_AFTER_PRE_OUTCOME_INVOCATION_RECOVERY`, and C7-A4 is `PASS`. `CURRENT_SELECTOR` remains `PRODUCTION_AUTHORITATIVE`; `c7.explicit_selection.v1` is `REJECTED_AS_GLOBAL_PRODUCTION_REPLACEMENT`. The next roadmap state is `C8 NEXT_ELIGIBLE / NOT_STARTED`, with `NOVEL_DATASET_CURATION_BEFORE_SUBSTANTIAL_DOWNSTREAM_DEVELOPMENT` recommended; C8 and dataset curation were not executed. T3.3A-R2 remains `INCONCLUSIVE`/partial, g016 is locally recovered but g011 is not, heuristic iteration is stopped, and the unresolved g011 mechanism is deferred to generic Phase-E coverage-aware architecture; optional T3.3B ranking debt is deferred. No formal T3, T4, or T5 was run.

---

# Historical records

## Historical authoritative snapshot — 2026-08-09

Gold v2.6 (`b5406e36…b687`) 与 evaluator 2.6.1 已按签署的 RC3f regression 人工审查落地。`g087/g097/g116` 及 `g098/g111` 两个 sentinel 的 focused run 全部通过；没有重跑完整 16 题。将 13 个已接受原始结果与 3 个 replacement 合成后，16/16 的 Gold recall、final evidence、source coverage、answer-point coverage、citation integrity 和 intent/status accuracy 均为 1.0，错误计数均为 0。

该结果是 reviewed diagnostic composite：`diagnostic_quality_checks.passed=true`，但因 mixed runtime provenance 不宣称 formal frozen-candidate regression gate。完整证据、hash、运行目录与边界见 `docs/M6_REGRESSION_RC3F_REVIEW_FIX_RESULT.md`。

---

## Historical authoritative snapshot — 2026-08-04

**Status date:** 2026-08-04

## 1. Current Gold and evaluator

Current official Gold:

```text
evaluation/benchmarks/v2_2/gold_questions.yaml
```

SHA-256:

```text
d65783d4712676af60a1d1b69f7a344d9898ae9c86914c7629c6daaffe4fe156
```

Current evaluator:

```text
evaluator-2.2
```

Official Gold validation:

```text
120/120
unmatched = 0
```

Current deterministic unit-test baseline:

```text
85 passed
```

## 2. Current benchmark exposure

The exposed benchmark contains 120 approved cases:

- `dev`: 80
- `challenge`: 24
- `regression`: 16

These 120 cases are exposed development/evaluation assets and are not hidden acceptance.

Current hidden acceptance state:

```text
not_created
```

The exposed benchmark is therefore:

```text
release_eligible = false
```

Do not treat dev/challenge/regression as hidden acceptance.

## 3. Current runtime identity

Current runtime model:

```text
gemini-3.6-flash
```

Current evaluation judge:

```text
gemini-3.6-flash
```

Embedding model:

```text
gemini-embedding-2
```

Current answer Prompt version after the mixed claim-noise behavior fixes:

```text
3.1.0
```

The previously frozen candidate `m6-v2-36-rc2b` is historical and no longer represents the current implementation identity because later source/Prompt behavior changed.

## 4. Current failure-review state

Current integrated review state:

```text
36 resolved
12 real failures pending
```

The 12 currently excluded real-failure cases in the 68-case diagnostic composite are:

```text
g023
g025
g039
g057
g060
g063
g073
g088
g089
g095
g110
g114
```

These failures must be handled through targeted fixes/focused reruns before a new formal candidate is frozen.

## 5. Evaluator-2.2 narrow corrections

The evaluator-2.2 corrections for `g074`, `g079`, and `g086` are intentionally narrow.

### g074

Accepted contract:

- intent: `data_flow`;
- blocking source: `code`;
- adapter implementation is sufficient to answer;
- paper/upstream implementation is context rather than a blocking source.

### g079

Only inside the signed Gold selector's `Lumi_TrksQA` data-product group, two explicitly approved direct-code locators may count as equivalent evidence.

This is **not** a repository-wide graph-to-code heuristic.

### g086

Implementation source is the blocking source.

Documentation is optional/diagnostic rather than required.

After evaluator-2.2 offline rescore, these three cases pass the relevant intent/evidence/required-source/answer-point/citation checks, with no wrong-version or major-unsupported failure under the approved narrow contract.

## 6. Current 68-case diagnostic composite

Current composite output:

```text
data/evaluation/rescores/
m6-v2-36-qa-dev-rc2b-evaluator-2_2-d65783d47126-90547a6958bf/
```

It represents the 80-case dev run excluding:

```text
g023 g025 g039 g057 g060 g063
g073 g088 g089 g095 g110 g114
```

Permitted replacements in this composite are:

```text
status run:
  g041 g119

synthetic-noise run:
  g011 g074 g079 g085 g086
```

`g089` is explicitly **not** replaced.

The composite added:

```text
model_calls = 0
token_usage = 0
```

Historical source-record usage must not be reported as new composite cost.

Because the synthetic replacements do not share the original RC2b prompt identity, the composite must preserve:

```text
diagnostic_composite_runtime = true
uniform_candidate_identity = false
complete_v2_dev = false
subset_diagnostic_only = true
```

Consequences:

- the composite is diagnostic only;
- it cannot pass the complete development gate;
- it cannot freeze a candidate;
- it cannot unlock regression;
- it cannot unlock challenge;
- it cannot unlock acceptance;
- it cannot unlock M7/M8.

## 7. Mixed claim-noise behavior fixes

The focused behavior-fix run covered:

```text
g011
g074
g079
g085
g086
g089
```

Run directory:

```text
data/evaluation/runs/m6-v2-36-synthetic-noise-fix-6-v1/
```

Result:

```text
6/6 answered
```

User-visible leakage of internal coverage/provenance claims was reduced to zero for this focused run.

Relevant runtime rule:

- `scope_*`
- `required_workflow`
- `required_code`
- `dataflow_locator_*`
- text containing `curated_panda_domain`

may remain in internal `claim_audit`, but must not be rendered as user-facing answer claims.

Focused run usage:

```text
model calls: 40
tokens: 410,412
runtime calls/tokens: 34 / 362,661
judge calls/tokens: 6 / 47,751
elapsed: 343.7 s
```

Focused answer-point coverage:

```text
94.44%
```

Known remaining issue in this group:

```text
g089: judge still marks p2 missing
```

The focused run is not a complete dev result and does not mean M6 passed.

## 8. Current authorization / next allowed work

At the current state:

**Allowed:**

- targeted fixes for the 12 real failures;
- rerun directly affected cases;
- add a very small number of directly relevant sentinels when useful;
- deterministic unit tests;
- offline rescore for evaluator/Gold/scoring-only changes;
- targeted work on `g089` and other confirmed real failures.

**Not yet authorized as the default next step:**

- another complete 80-case dev run;
- complete 16-case regression;
- challenge;
- hidden acceptance;
- M7;
- M8.

A new complete dev run becomes appropriate only after the current fix batch has been validated and a new candidate is intentionally frozen.

---

# Historical evaluation record

The following entries are retained for provenance. They are not the current candidate identity.

## A. evaluator-2.1 / Gold v2.1 offline correction

Historical Gold:

```text
evaluation/benchmarks/v2_1/gold_questions.yaml
```

Dataset SHA:

```text
1fea656c1ea05ac2cf4bbb78e8e712fec3c09e40c31f5d77a914fa7cadbd9d22
```

Historical unified rescore output:

```text
data/evaluation/rescores/
m6-v2-36-qa-dev-rc2b-evaluator-2_1-1fea656c1ea0/
```

The 31-case correction process preserved original records, used offline rescoring for scoring/Gold/selector changes, and reran only behavior-affected cases.

This state is superseded by Gold v2.2 / evaluator-2.2.

## B. RC2b formal dev checkpoint

Historical frozen candidate:

```text
m6-v2-36-rc2b
```

Historical candidate manifest SHA:

```text
a3810966dd1a9347033005f2f83e8142f84b2ab57d50d3252a8e005e83a661d9
```

The frozen 80-case dev run:

```text
m6-v2-36-qa-dev-rc2b
```

completed:

```text
80/80
```

but failed the development gate.

Because later source/Prompt behavior changed, RC2b is no longer the current implementation identity.

No full regression/challenge/acceptance was authorized from that failed candidate.

## C. Candidate v8 checkpoint

Historical run:

```text
m6-qa-dev-candidate-v8
```

It resumed from `53/80` using the same run ID and completed `80/80` without rerunning completed cases.

Historical gate failures included:

```text
unsupported claims: 5
required identifier missing: 1
answered required-source coverage: 0.9873
```

The v8 state was later superseded by the Benchmark v2 / evaluator correction work.

## D. Candidate v5 checkpoint

Historical result:

```text
m6-qa-dev-candidate-v5
80/80 completed
development gate failed
```

Recorded metrics:

```text
Gold Recall@10: 0.9833
answer-point coverage: 0.9125
intent accuracy: 0.9875
expected-status accuracy: 1.0
citation integrity: 1.0
wrong-version evidence: 0
unhandled exceptions: 0
unsupported claims: 5
identifier hallucination: 1/400 (0.0025)
model calls: 498
token usage: 6,067,814
```

This record is historical only.

## E. v2-lite RC1 baseline

Historical candidate:

```text
m6-v2-lite-rc1
```

Historical complete dev result:

```text
80/80 completed
development gate failed
```

Recorded metrics:

```text
Recall@10: 79.06%
final evidence recall: 53.81%
answer-point coverage: 71.15%
citation integrity: 100%
wrong-version evidence: 0
unhandled exceptions: 0
expected-status accuracy: 91.25%
intent accuracy: 92.5%
major unsupported claims: 4
contradictions: 1
critical answer-point misses: 39
runtime/judge calls: 406/80
total token usage: 4,494,556
```

This older baseline is superseded by later candidate/evaluator states.

---

# Maintenance rules for this file

Update this file when any of the following changes:

- approved Gold version/hash;
- evaluator version;
- runtime/judge/embedding model identity;
- prompt identity relevant to evaluation;
- benchmark split/acceptance state;
- current frozen candidate;
- complete formal run result;
- integrated failure-review count;
- authoritative unresolved-case list;
- authorization to proceed to regression/challenge/acceptance/M7/M8.

Do not update this file for every ordinary code edit.

When adding a new current state:

1. add a new dated **Current authoritative state** section or update the existing one;
2. move superseded candidate/run details into **Historical evaluation record**;
3. clearly mark superseded identities as historical;
4. never rewrite historical model-call/token usage as if it belonged to a newer offline rescore.
