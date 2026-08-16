# PANDA QA Agent — Evaluation Status

This file records transient evaluation state: current Gold/evaluator versions, candidate status, unresolved cases, run provenance, metrics, hashes, and historical checkpoints.

Stable evaluation rules belong in `docs/EVALUATION_POLICY.md`.
Day-to-day Codex behavior belongs in `AGENTS.md`.

When records conflict, use the single section explicitly marked **Current authoritative state**.

---

# Current authoritative state — 2026-08-14

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

## Generalization Phase status

- Bootstrap tasks A1–A3: `PASS`; A3.1 hardening: `PASS`; B1: `PASS`; B2: `PASS`; B3: `PASS`; B4: `PASS`; B5: `PASS` (B5.1R2 static closeout and B5.2 live migration/T1/post-B5 T2 completed); Phase-B T3 full 80-question dev retrieval-only original mechanical gate: `FAIL`; T3.1 evaluator semantics correction: `PASS`; T3.1R1 product-language calibration: `PASS`; T3.1R2 calibration-binding/rank-stage closeout: `PASS`; T3.1R3 frozen fused-rank provenance & dynamic dev-completeness closeout: `PASS`; T3.2 critical-evidence mechanism investigation: `PASS`; T3.3A first implementation attempt: `SUPERSEDED`; T3.3A-R1 bounded soft-budget closeout: `INCONCLUSIVE` (boundedness and diagnostics corrected, but local frozen replay does not recover g011/g016 and baseline fidelity is false; authoritative formal Phase-B product T3 remains `FAIL`).
- Evaluation modes: `retrieval`, `qa`, and `full` have explicit recorded boundaries.
- Structured retrieval traces are persisted as atomic JSON and JSONL and can be loaded without rerunning QA.
- A3 was corrected from a possible full-retrieval interpretation to a stratified low-cost bootstrap baseline. Phase-B T3 (complete 80-question dev retrieval-only) was performed on `2026-08-16`; no full 120-question retrieval/E2E run was performed.
- C1 remains `NOT_STARTED`; it is not the active task because the recalibrated English product-scope T3 gate still has a genuine critical-evidence blocker.

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

### Current small E2E baseline

- Run: `generalization-a3-stratified-qa-20260813`.
- Mode/cases: `qa`, 16 approved English Gold questions; runtime generation and verification enabled, external judge disabled.
- Cost: 76 runtime model calls, 819,872 tokens, 0 external-judge calls.
- Measured: Recall@5 `0.6041666667`; Recall@10 `0.75`; Recall@20 `0.75`; MRR `0.65`; combined candidate recall `0.875`; final-evidence recall `0.7083333333`; expected-status accuracy `1.0`; citation integrity `1.0`; identifier hallucination rate `0.0`; no exceptions.
- Answer-point coverage is N/A because the external rubric judge was deliberately disabled.
- External-rubric contradiction and unsupported-claim metrics were likewise not measured; corrected package artifacts represent all three metric families as N/A rather than synthetic zero/clean values.

The retrieval and QA measurements are unchanged. A3.1 corrects only metric representation, portable artifact paths, consistency metadata, and measured-execution provenance wording; historical model outputs remain untouched.

## Novel dataset state

- `novel_dev`: 0.
- `novel_validation`: 0.
- `novel_holdout`: not created; the runner supports loading it from an external path.
- Human-curated: no trustworthy human-authored novel dataset is currently available.
- Empty novel JSONL artifacts are schema/placeholders, not measured results.

## Known limitations

- The A3 stratified bootstrap baseline does not cover every intent in depth; Phase-B T3 now measures all approved development intents, including `data_flow`, `module_structure`, and `troubleshooting`.
- The current baseline measures exposed English Gold behavior, not genuinely novel-question generalization.
- Historical E2E and current baseline identities differ, so their metric differences are not a controlled before/after comparison.

## Next authorized roadmap task

`T3.3A-R1 remains active: bounded soft-budget corrected but local replay does not recover g011/g016; next step requires either a broader bounded selector invariant or an explicitly authorized formal re-evaluation — do not implement C1`

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
