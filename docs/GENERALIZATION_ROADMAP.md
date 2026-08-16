# PANDA Agent — Generalization Roadmap

> This document is a roadmap, not a single implementation task.
> Codex must implement only the roadmap task explicitly requested in the
> current user instruction and must stop after that task.

The Generalization Phase moves PANDA Agent from benchmark-dependent fixes toward reusable question understanding, entity resolution, retrieval, answer decomposition, evidence-bound claims, and verification. Existing compatibility behavior remains until generic replacements have been measured. Evaluation questions are measurement data, never implementation specifications.

Statuses describe implementation state; acceptance targets remain planned until measured. Each task ends with a report and stop. Future tasks are `NOT_STARTED`.

## Phase A — Evaluation infrastructure and versioned baseline

### A1 — Explicit evaluation modes

- **Status:** PASS
- **Problem:** Retrieval, production QA/runtime verification, and the external rubric judge were coupled under the former `qa` run, wasting model calls for layer-specific tests.
- **Goal:** Provide auditable `retrieval`, `qa`, and `full` boundaries without duplicating or changing production QA logic.
- **Why this stage:** Every later task needs a cost-appropriate way to isolate the layer it changes before architecture work begins.
- **Intended design:** `retrieval` stops after evidence selection and trace creation; `qa` adds production answer generation and runtime verification/revision; `full` adds the external evaluation judge. Run metadata declares the permitted stages.
- **Functional requirements:** Reuse the existing retriever and QA graph; persist mode/boundaries; prevent retrieval from entering answer/judge paths; prevent QA from automatically entering the external judge; preserve former judged behavior under `full`; support resume/report.
- **Explicit out of scope:** Retrieval ranking, prompts, query expansions, answer behavior, model choice, and index changes.
- **Dependencies:** Existing evaluation runner, Retriever, QAAgent, run store, and usage accounting.
- **Authorized evaluation tier:** T0 plus the smallest useful T1 boundary smoke.
- **Primary metrics:** Boundary correctness, exception-free execution, model-call breakdown, and compatibility of `full` with the former judged path.
- **Acceptance criteria:** All modes execute only declared stages; mode appears in manifest; tests detect boundary crossing; no intended production behavior change.
- **Failure handling:** Add thin orchestration around existing components. Do not redesign QA for cleaner evaluation plumbing; classify environment failures separately from behavior failures; stop after A1.

### A2 — Structured retrieval traces and reusable intermediates

- **Status:** PASS
- **Problem:** Final scores cannot localize analyzer, channel recall, fusion, reranking, or evidence-selection failures, and repeated QA runs waste Vertex calls.
- **Goal:** Persist deterministic-enough, reloadable retrieval traces that faithfully represent current behavior.
- **Why this stage:** B–F require before/after comparison and layer-specific reuse; instrumentation must predate changes to those layers.
- **Intended design:** Store question/run/implementation identity, RetrievalPlan, raw/original/dense/sparse query text, resolved concepts/symbols, exact/dense/sparse/paper/workflow/graph candidates with ranks and available scores, fused/reranked candidates, exclusions, and selected evidence as atomic JSON plus JSONL.
- **Functional requirements:** Current dense and sparse query text must remain the raw question; preserve source/version/object/locator identity; serialize/load without QA or Vertex; expose full selected evidence from QA diagnostics; support frozen candidate reuse.
- **Explicit out of scope:** SemanticQueryBuilder, LexicalQueryBuilder, entity resolution, workflow engines, new ranking scores, query rewrites, or retrieval changes.
- **Dependencies:** A1, current retrieval diagnostics, canonical object lookup, and run manifests.
- **Authorized evaluation tier:** T0 schema/round-trip tests plus a small T1 trace smoke.
- **Primary metrics:** Serialization round-trip, trace count versus completed cases, candidate order/identity stability, and zero instrumentation exceptions.
- **Acceptance criteria:** Traces load independently; represent every available channel and final evidence; raw query use is explicit; production behavior is unchanged.
- **Failure handling:** Record unavailable values as absent rather than inventing them. If persistence fails, fix the trace contract/writer without changing retrieval; stop after A2.

### A3 — Low-cost stratified bootstrap baseline

- **Status:** PASS
- **Problem:** The phase needs a reproducible current reference, but a complete benchmark retrieval run is unnecessary for bootstrap and may waste Vertex tokens.
- **Goal:** Create the smallest representative baseline that verifies the infrastructure, provides a current before/after reference for early Generalization tasks, estimates retrieval/QA behavior, and reuses historical full-run evidence.
- **Why this stage:** All later work needs a stable comparison point before B1 changes index semantics.
- **Intended design:** Reuse the newest trustworthy complete prior E2E split; select approximately 20–30 benchmark questions deterministically across API/symbol, implementation, data flow, workflow, theory, troubleshooting, usage, and cross-repository classes for `retrieval`; select approximately 10–20 for `qa`; include only trustworthy human-authored novel questions that already exist; package identities, selected IDs, records, traces, metrics, and a report.
- **Functional requirements:** Record the deterministic selection method and IDs; record Git/dirty state, prompts, models/dimensions, sparse/index identity, generation/verifier/judge roles, retrieval policy, dataset, timestamp, mode, usage, and exact run provenance; package artifacts without rerunning source runs; state whether historical evidence matches the A3 measured execution provenance.
- **Baseline naming and reuse:** Report this package as the **English Gold Stratified Bootstrap Baseline**, never as a complete generalization, complete benchmark, or all-intent baseline. Persist versioned fixed retrieval/QA ID manifests and reuse them unchanged for future before/after comparisons; a changed selection requires a new manifest identity.
- **Explicit out of scope:** T3, any full 120-question retrieval or E2E run, T5, full novel E2E, generated pseudo-Gold, repeated judges, dense re-embedding, candidate release, or B1.
- **Dependencies:** A1, A2, current infrastructure, existing run artifacts, and reviewed benchmark Gold.
- **Authorized evaluation tier:** T0 plus a stratified low-cost baseline: normally 20–30 retrieval cases and 10–20 `qa` cases; no T3 and no external judge.
- **Primary metrics:** Recall@5/@10/@20, MRR, combined candidate recall, final-evidence recall where Gold supports them; runtime QA status/grounding metrics without pretending external rubric coverage was measured.
- **Acceptance criteria:** Historical reference exists; 20–30 stratified retrieval cases and 10–20 small E2E cases exist where practical; selected IDs are recorded; novel absence is explicit; no full 120-question retrieval or E2E run is performed.
- **Coverage limitation:** If approved English Gold lacks an intent, record it as unevaluated. The v2.6 bootstrap selection has no eligible `data_flow`, `module_structure`, or `troubleshooting` questions.
- **Failure handling:** Reuse fewer trustworthy novel questions or create only schema/harness if none exist. If infrastructure would require an unauthorized expensive operation, stop and report `INCONCLUSIVE`; stop after A3.

## Phase B — Indexing and embedding correctness

### B1 — Correct sparse BM25 / Qdrant IDF contract

- **Status:** PASS
- **Problem:** The deployed FastEmbed/Qdrant BM25 path may omit the server-side IDF modifier expected by its sparse scoring contract, weakening rare-identifier discrimination.
- **Goal:** Confirm installed-version behavior and make indexing/query scoring use the correct BM25/IDF contract.
- **Why this stage:** Sparse correctness is foundational; tuning queries or fusion before fixing scoring would confound later measurements.
- **Intended design:** Inspect installed APIs and live collection configuration; apply the correct modifier; update immutable index identity/schema when necessary; rebuild only required sparse/index structures while reusing valid dense embeddings. The verified contract uses FastEmbed `0.7.4`, Qdrant client `1.15.1`, live Qdrant server `1.15.5`, and an explicit server-side `idf` modifier.
- **Functional requirements:** Index/query contracts agree; identity records scoring modifier/model; migration/rebuild is explicit and auditable; dense vectors remain unchanged.
- **Explicit out of scope:** Dense model/dimensions, analyzer, query expansion, fusion weights, answer logic, aliases, or benchmark-specific compensation.
- **Dependencies:** A3 baseline, installed FastEmbed/Qdrant versions, index identity, compatible caches.
- **Authorized evaluation tier:** T0 contract/config tests, T1 live correctness smoke, and targeted T2 lexical/rare-identifier retrieval; no T5.
- **Primary metrics:** Sparse Recall@5/@10, sparse MRR, rare-identifier retrieval, scoring-contract correctness, rebuild/model-call cost.
- **Acceptance criteria:** Deployed sparse configuration follows the installed-version IDF contract; indexer/retriever remain compatible; dense embeddings are reused; benchmark/novel effects are reported, not forced. PASS: `SparseVectorParams()` previously exposed a null modifier, while the deployed contract now records `modifier=idf`; the immutable identity is schema 3 with fingerprint `5f0f9ffe6149091e6c42d650f3a7576466d82b8eb86af0567d9c57a81bb8a937`. An in-place migration preserved all `80698` points before and after without collection recreation, sparse-vector regeneration, dense reinsertion, dense embedding recomputation, or Vertex calls.
- **Measured comparison:** On the fixed 24-question sparse-only set (applicable denominator 20), Recall@5 changed from `0.375` to `0.475` (`+0.1`), Recall@10 from `0.5166666667` to `0.6` (`+0.0833333333`), and MRR from `0.4212698413` to `0.4201388889` (`-0.0011309524`). The explicit identifier-heavy subset (9 fixed IDs, applicable denominator 8) changed from Recall@5 `0.125` to `0.25` (`+0.125`), Recall@10 `0.2916666667` to `0.375` (`+0.0833333333`), and MRR `0.1513888889` to `0.1302083333` (`-0.0211805556`). Per-question first-relevant-rank outcomes were improved `3`, unchanged `14`, and regressed `3`; no broad systematic regression was observed.
- **Failure handling:** Do not add aliases, query phrases, weights, or guards to hide weak sparse results. If API/collection migration is ambiguous, stop before destructive rebuild and report the exact blocker; stop after B1.

### B2 — Explicit dense embedding dimensionality contract

- **Status:** PASS
- **Problem:** Configuration, embedding API output, and Qdrant collection dimensions can drift when the API default is implicit.
- **Goal:** Make dimensions explicit from request through vector validation and collection identity.
- **Why this stage:** Once sparse correctness is established, dense reproducibility must be secured before changing chunking or semantic queries.
- **Intended design:** Pass configured dimensions where supported; validate every returned vector; bind dimensions to collection/index identity; fail clearly on mismatch. The verified implementation uses `google-genai 2.13.0` `EmbedContentConfig.output_dimensionality`; shared query/document `_embed` requests explicitly use 3072 and fail closed on count, non-empty, or exact-length violations.
- **Functional requirements:** Single, small-batch, and indexing-batch paths request/validate the same dimension; mismatch stops before storage; health/identity output exposes dimensions.
- **Explicit out of scope:** Changing embedding model, semantic query text, chunking, fusion, or answer behavior.
- **Dependencies:** B1 identity conventions, active embedding API, Qdrant collection schema.
- **Authorized evaluation tier:** T0 and minimal integration tests; a tiny live embedding smoke only when needed.
- **Primary metrics:** Percentage of vectors matching configured dimension (target 100%), mismatch detection, and zero partial writes.
- **Acceptance criteria:** All representative paths validate exact size; mismatches fail fast with stage/model context; identity is reproducible. PASS: the cache key is unchanged, SQL cache reuse requires `dimensions=3072`, and all `70102` existing rows already have 3072 dimensions; stale receipts are updated only after an actual re-embed. `IndexIdentity` already carries dimensions, so no field/schema/fingerprint change was needed; schema 3 and fingerprint `5f0f9ffe6149091e6c42d650f3a7576466d82b8eb86af0567d9c57a81bb8a937` remain unchanged. The live Qdrant collection remains size 3072 with `80698` points and three sampled vectors of length 3072, requiring no collection/index/dense-vector migration or re-embedding. T0 final verification passed 50 tests plus `compileall` and `git diff --check`; the live embedding smoke passed: 1 query + 1 document embedding, both explicitly requested and returned 3072 dimensions.
- **Live smoke cost:** The supplemental smoke used one query and one document embedding request; generation calls and judge calls were `0`, and the embedding API returned no token-usage metadata.
- **Failure handling:** Do not silently fall back to another model/dimension. Preserve the existing model and report access/API incompatibility; stop after B2.

### B3 — Unified sparse encoder identity/factory

- **Status:** PASS
- **Problem:** Indexer and retriever independently constructing sparse encoders can silently diverge in model, language, tokenizer, or scoring configuration.
- **Goal:** Establish one authoritative construction/identity path and fail closed on mismatch.
- **Why this stage:** B1 defines scoring and B2 completes dense identity; B3 consolidates sparse reproducibility before ingestion/chunk changes.
- **Intended design:** Reuse `src/panda_agent/sparse.py` as the sole factory and receipt path; include model, language, scoring modifier, and meaningful tokenizer/model settings in index identity.
- **Functional requirements:** Index/query encoder receipts match; startup/index compatibility checks reject mismatch; offline local-model behavior remains fail-closed. The former independent `SparseTextEmbedding` construction in `indexing.py`, `retrieval.py`, `sparse_evaluation.py`, and `kb_bundle.py` now delegates to `create_sparse_encoder`.
- **Explicit out of scope:** Multilingual sparse models, Chinese tokenization, new aliases, retrieval tuning, or dense changes.
- **Dependencies:** B1 sparse contract, current configuration and index identity.
- **Authorized evaluation tier:** T0 identity/factory tests and minimal integration compatibility smoke.
- **Primary metrics:** Identity equality across indexing/retrieval and deterministic mismatch rejection.
- **Acceptance criteria:** PASS: `SparseEncoderReceipt` and `create_sparse_encoder` are the authoritative contract. The receipt binds `Qdrant/bm25`, English, `sparse`, `idf`, `k=1.2`, `b=0.75`, `avg_len=256.0`, `token_max_length=40`, `disable_stemmer=false`, `SimpleTokenizer`, `SnowballStemmer`, `mmh3.hash`, FastEmbed `0.7.4`, `mmh3` `5.2.1`, `py-rust-stemmers` `0.1.8`, and the English stopword asset SHA-256 `019f104ba2ed07436d05f9cdd3383034ad66014edc27fc651f837e1a038b6451`. Machine-specific `model_path`, `local_files_only`, `threads`, and `device` are excluded from portable semantic identity: the path and execution settings are environment/runtime concerns, while `local_files_only` is enforced as a fail-closed loading policy. Persisted/Qdrant receipt mismatch and sparse modifier/schema mismatch fail closed.
- **Measured verification:** The schema-3 identity migrated to schema 4, changing fingerprint `5f0f9ffe6149091e6c42d650f3a7576466d82b8eb86af0567d9c57a81bb8a937` to `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`. Both dry-run and `--run` validated the first eight points in native Qdrant scroll order by re-encoding `title + "\n" + text`; point sets and sparse index sets matched, and sparse values were float32 bit-exact for 8/8 points with zero mismatches. The run performed one metadata-only PostgreSQL single-row CAS update; Qdrant remained at 80,698 points with dense size 3072 and sparse `idf`, with no collection rebuild, vector regeneration/reinsertion, dense re-embedding, or Vertex call.
- **Evaluation cost and limitation:** T0 final verification passed 63 tests, `compileall`, `git diff --check`, and one constructor smoke. T1 used local FastEmbed only: eight document encodes in dry-run plus eight in `--run` (16 total), two Qdrant scroll/read passes, and one SQL identity update. Generation, analyzer, dense embedding, reranker, answer, verifier, judge, Retriever/QA, token usage, benchmark, T3, and higher evaluations were not run.
- **Failure handling:** Do not add warnings-and-continue or model fallbacks. Report missing local assets/version incompatibility; stop after B3.

### B4 — Precise derived-chunk locators

- **Status:** PASS
- **Problem:** Derived chunks inherited a parent-wide line/page locator, weakening citation precision and auditability; truncated file objects also claimed source ranges beyond their represented prefixes, while Markdown and Sphinx section provenance was flattened.
- **Goal:** Record the narrowest available path/line/page/section locator for each derived chunk.
- **Why this stage:** Identity contracts are stable, so locator metadata can be corrected before more substantial chunking changes.
- **Intended design:** Carry deterministic source offsets through derivation; map source chunks to path/start/end lines and documents to page/section provenance without altering semantic text or chunk boundaries. Offset tracking is performed during splitting and does not recover spans with ambiguous `str.find()`.
- **Functional requirements:** Cover multiple functions per source, long objects, derived text chunks, and PDF/document chunks; preserve parent-child lineage; avoid broader-than-content claims.
- **Explicit out of scope:** Broad semantic rechunking, query changes, fusion, answer prompts, or dense recomputation when embedding text is unchanged.
- **Dependencies:** B2/B3 identity, ingestion provenance, current locator models.
- **Authorized evaluation tier:** T0 fixtures and metadata integrity checks.
- **Primary metrics:** Locator precision/validity, lineage preservation, and count of materially overbroad test locators.
- **Acceptance criteria:** PASS. The normalized corpus remained semantically invariant at `102875` objects before and after: IDs added/removed, text, title, object type, source/version identity, canonical locator, token count, embedding eligibility, and parent/chunk lineage changes were all `0`. `28010` locators changed, concentrated in derived function/class/script/README chunks and truncated source-file records. The audit found `16352` derived chunks with `0` containment violations and `0` invalid line ranges; `652` truncated file objects were corrected with `0` remaining overbroad ranges; `281` README sections received hierarchical paths; `314` Sphinx sections were audited, with `241` stable anchor fragments and `0` synthetic fragment URLs; PDF provenance remained page/section-only with `0` fabricated line locators. Existing parser-native C/C++, Python, CMake, and shell coordinates remained authoritative. Citation consumers remain compatible.
- **Measured metadata deployment:** Normalized artifacts were updated. The initial metadata-only dry-run planned and the explicit apply updated `28010` PostgreSQL locator rows and `22856` Qdrant payload locators; the post-apply dry-run planned `0` changes. The sync verified object/source/version/point identity and unchanged semantic content before every write. Qdrant vectors changed `0`; dense vectors reinserted `0`; sparse vectors regenerated `0`; dense embeddings and model calls `0`. Index schema remained `4` and fingerprint remained `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`.
- **Measured verification:** T0 passed `10` ingestion locator tests, `7` metadata-sync tests, and `11` B3 sparse-factory regression tests. T1 ingestion completed in `239.387s`; live metadata dry-run, apply, and post-apply checks passed. No retrieval, QA, judge, or benchmark evaluation was run.
- **Failure handling:** If parser offsets are unavailable, preserve honest parent provenance and record the limitation rather than guessing; stop after B4.

### B5 — Structure-aware, token-aware chunking and source-file coverage

- **Status:** PASS
- **Problem:** Approximate character/token limits and function/class extraction can leave large source-file context or coarse PDF pages semantically uncovered.
- **Goal:** Use structure first and token-aware limits second while covering important free code, configuration, orchestration, comments, and document sections.
- **Why this stage:** Correct locators and identities must exist before changing embedding units and selectively rebuilding affected objects.
- **Intended design:** Preserve classes/functions plus meaningful global/configuration/file regions; prefer section/paragraph/equation/table context for documents; keep page as provenance, not mandatory chunk boundary.
- **Functional requirements:** Prevent oversized inputs; retain lineage/precise locators; cover non-function source information; avoid arbitrary overlap; re-embed/rebuild only affected objects where practical.
- **Explicit out of scope:** Generic query builders, fusion tuning, answer changes, or wholesale corpus redesign.
- **Dependencies:** B2–B4, parser structure, embedding cache identity, A3 retrieval traces.
- **Authorized evaluation tier:** T0 chunk/integrity fixtures, targeted T2 retrieval, then Phase-B T3 retrieval-only comparison.
- **Primary metrics:** Index integrity, uncovered-source fixture retrieval, benchmark/novel Recall@k and MRR, changed-object/re-embedding counts.
- **Acceptance criteria:** Integrity does not regress; newly represented file-level information is retrievable; benchmark regression stays within policy tolerance; novel retrieval does not materially regress.
- **Failure handling:** Revert or narrow the generic chunking mechanism, not add case-specific chunks or page anchors. Stop after B5 and report the Phase-B comparison; do not start C1.
- **B5.1R2 closeout (pre-migration, PASS):** `ChunkingPolicy` now separates intermediate upper-bounds validity (`within_upper_bounds`, no minimum) from final eligibility (`embedding_input_is_valid`), so sub-minimum paragraphs/lines survive into source-ordered atom merging and are combined into valid chunks instead of being silently dropped; unmergeable sub-minimum residuals stay on the non-eligible parent and are audit-visible. A coverage-based structural-container rule stops broad parents with structured searchable children (`source_file`, `python_script`, README roots, `sphinx_page`) from producing broad duplicate embedding chunks; README roots additionally receive a preamble gap region, and generic `.txt`/`.rst`/`.md`/`.yml` files keep deterministic paragraph/block → lines → hard-fallback coverage, including content beyond the legacy 20000/30000-character boundaries (fixture-proven). Curated alias provenance and `RelationResolver` both exclude `b5_source_gap` objects, preserving B4 semantics. `apply_b5_selective_index` was fixed (`vertex_settings` now constructed exactly once and passed to `VertexAIClient`) and its read-only preflight now validates settings, sparse factory receipt, identity, artifacts, plan closures, reuse locators, selected inputs, and live counts before any SQL/Qdrant mutation; a fully mocked `run=True` orchestration test covers reuse/change/stale handling and verifies stale deletion happens only after replacement writes. Offline churn attribution assigns exactly one primary cause to every planned re-embed object with `unknown = 0`.
- **Measured final candidate before deployment:** `133075` objects, `104973` embedding-eligible, output hash `ff7f6102542bd68775caefba19d19d9ba0bb2452fe05a234344db40284538e73` (reproduced across two full ingestion runs); relations invariant (`64561` edges / `372139` candidates). Integrity: duplicate IDs 0, missing parents 0, orphan relation endpoints 0, locator containment violations 0, invalid line ranges 0, fabricated PDF lines 0, policy-invalid eligible 0. Source coverage (B4 → final): C/C++ uncovered containers 1281 → 0 (gap regions 26092), build/config 44 → 0 (gap regions 638), Python 0 → 0 (gap regions 96), generic long-file paragraphs 1756, shell 0 → 0, README/Sphinx 0 → 0, PDF 0 → 0; hard-fallback chunks 2 (whole corpus); sub-minimum residuals 0. Revised selective impact plan: reuse `64426` unchanged points (including `11235` receipt-missing points that are never re-embedded), changed `13541`, new `25003`, eligibility gained `2003`, stale `2731`; `40547` dense and sparse documents in `634` batches; index identity remains schema 4 / `8172f9a640e62977be6e911bfb4848ce3aecd0994f1f3ba51a0985bffec62cb9`; collection is never recreated. Live index was untouched throughout (PostgreSQL `102875`, Qdrant `80698`); zero model calls, zero live writes.
- **Measured verification:** T0 passed `40` B5 chunking/migration tests plus `20` B5.2 migration/safety tests (resume-safe selected-point skipping, pre-write Vertex/sparse constructor failures, mocked `run=True` apply), `11` B3 sparse-factory regression tests, and `7` B4 locator tests; `compileall` and `git diff --check` clean. Pre-B5 T2 remains the authoritative before-state (`b5-pre-retrieval-20260815`, 16 fixed A3 IDs, retrieval-only).
- **B5.2 closeout (live migration, PASS):** selected-point resume skipping now requires a compatible dense receipt bound to the same `object_id` plus an exact current-B5 Qdrant payload (`object_id`, `source_id`, `source_version_id`, `object_type`, `title`, `text`, `locator`); any uncertainty forces a safe re-embed. `VertexAIClient` and the authoritative sparse encoder are constructed and the sparse receipt is verified before any live SQL/Qdrant mutation. Live migration started from pure B4 (`102875` SQL / `80698` Qdrant), embedded `40547` selected dense and sparse documents, reused `64426` unchanged points (including `11235` missing-receipt points), deleted `2731` stale points, and ended at `133075` SQL / `104973` Qdrant with no collection recreation. T1 passed: exact point-ID set match (`missing 0`, `stale 0`), all `40547` selected payloads verified, deterministic reuse/missing-receipt samples verified, SQL/relation/candidate/alias/workflow counts matched, dense `3072`, sparse `sparse`/`idf`, schema `4`, fingerprint unchanged. Post-B5 T2 (run `b5-post-retrieval-20260816`, same fixed 16 IDs, retrieval-only) completed: Recall@5 `0.6944444444` → `0.7361111111` (`+0.0416666667`), Recall@10 `0.8333333333` → `0.8333333333` (`0`), Recall@20 `0.8333333333` → `0.8333333333` (`0`), MRR `0.6` → `0.5375` (`-0.0625`), combined candidate recall `0.9166666667` → `1.0` (`+0.0833333333`), final evidence recall `0.8333333333` → `0.8333333333` (`0`), intent accuracy `0.9375` → `0.9375` (`0`), exceptions `0`; cost `48` model calls, `283871` tokens. First-relevant rank: improved `0`, unchanged `8`, regressed `2` (`g001` 1→2, `g013` 2→4); `g038`/`g043` had no first-relevant hit in either run. No migration/integrity defect was indicated.
- **Phase-B T3 full retrieval-only result (FAIL):** complete 80-question approved development run `phase-b-t3-retrieval-20260816`, mode `retrieval`, manifest `evaluation/baselines/manifests/phase_b_t3_retrieval_v1.json`. Applicable `73`, excluded `7` version-conflict. Metrics: Recall@5 `0.8801369863`, Recall@10 `0.9748858447`, Recall@20 `0.9863013699`, MRR `0.7285388128`, combined candidate recall `1.0`, final evidence recall `0.9828767123`, critical final evidence recall `0.9828767123`, intent accuracy `0.9875`, expected-status accuracy `0.9125`, exceptions `0`. Development gate `passed=false` because `critical_evidence_coverage < 1.0` and `expected_status_accuracy < 0.975`. Failure taxonomy: Q1 `1`, R2 `3`, R3 `2`, R1 `0`; no evidence of broad systematic ranking regression (rank-1 fraction `0.534`, Recall@10 `0.975`, R1 `0`). Cost `240` model calls, `1403061` tokens, `0` document embeddings. Novel retrieval remains `UNMEASURED`.
- **T3.1 evaluator semantics and English product-scope rescore:** original T3 records remain immutable. Retrieval-mode `expected_status_accuracy` is now N/A because retrieval does not run the sufficiency/refusal decision; ordinary Recall/MRR/final-evidence metrics apply only to Gold `answered` cases; version-conflict rejection remains a hard retrieval check. Gold dev language distribution: `en=51`, `zh=20`, `mixed=9`; deterministic English product selector selects exactly `51` approved dev English cases. Corrected all-language diagnostic (80 records): ordinary answered denominator `66`, Recall@5 `0.8674`, Recall@10 `0.9722`, MRR `0.7427`, final evidence recall `0.9811`, critical final evidence recall `0.9811`, expected-status accuracy N/A, gate `FAIL` (critical evidence coverage < 1.0). English product-scope (51): answered-applicable `43`, Recall@5 `0.9147`, Recall@10 `0.9651`, MRR `0.7953`, final evidence recall `0.9767`, critical final evidence recall `0.9767`, intent accuracy `0.9804`, formal product gate `FAIL` (critical evidence coverage < 1.0). Exact English critical blockers: `g011.e1` (R3) and `g016.e2` (R2). `g072`/`g085` are zh diagnostics outside the English gate.
- **T3.1R1 product-language recalibration and 59-case rescore:** raw Gold dev language metadata was audited for the exact 80 T3 dev questions. Calibration artifact `phase_b_t3_product_language_scope_v2.json` records reviewed overrides for the 9 raw `mixed` dev IDs: `g102` remains non-English, while `g105,g108,g110,g112,g113,g114,g115,g119` are effective English. Formal English product scope is `59` cases (`51` raw English + `8` calibrated mixed-to-English); non-English scope is `21` (`20` raw zh + `g102`). Recalibrated status counts: answered `49`, insufficient-evidence `5`, version-conflict `5`. Metrics: Recall@5 `0.9048`, Recall@10 `0.9694`, Recall@20 `0.9796`, MRR `0.7626`, combined candidate recall `1.0`, final evidence recall `0.9796`, critical final evidence recall `0.9796`, intent accuracy `0.9831`, expected-status accuracy N/A. Formal product gate `FAIL` because critical evidence coverage remains below `1.0`. Actual failure taxonomy: Q1 `1`, R2 `2`, R3 `1`; genuine critical misses are `g011.e1` (R3) and `g016.e2` (R2). `report_evaluation()` now exposes `product_development_gate` alongside the all-language diagnostic.
- **Remaining B5 work:** none. Phase-B T3.1R1 recalibration is complete; formal English product-scope Phase-B T3 gate is `FAIL` because critical evidence coverage remains below 1.0. Next task is `T3.2 — Critical-evidence mechanism investigation` for final calibrated formal blockers `g011` (R3) and `g016` (R2); do not implement fixes and do not start C1.

## Phase C — Retrieval generalization

### C1 — Deterministic parsing before expensive LLM analysis

- **Status:** NOT_STARTED
- **Problem:** The LLM analyzer may infer syntax that is already deterministically recognizable and then be overridden by routing rules, adding cost and variance.
- **Goal:** Extract unambiguous identifiers, `Class::method`, paths, repositories, refs/versions, and genuinely generic high-confidence intents before LLM analysis.
- **Why this stage:** With index/chunk correctness established, query understanding is the first retrieval-side generalization layer and can reduce cost without changing downstream architecture.
- **Intended design:** Produce a deterministic partial plan; call the LLM only for unresolved semantic aspects; merge while preserving explicit user syntax and provenance of each field.
- **Functional requirements:** Exact syntax recall, conflict handling, call-skipping criteria, routing provenance in traces, and compatibility with current plan consumers.
- **Explicit out of scope:** Benchmark phrases, semantic/lexical query builders, entity ontology, fusion changes, or removal of compatibility rules.
- **Dependencies:** Phase B and A2 traces.
- **Authorized evaluation tier:** T0 parser fixtures, T1/T2 explicit-symbol and intent subsets.
- **Primary metrics:** Explicit-symbol recall, intent accuracy, analyzer-call reduction, latency, and query-understanding failures.
- **Acceptance criteria:** Deterministic extraction preserves/improves correctness, avoids unnecessary calls, and adds no benchmark-specific route.
- **Failure handling:** Narrow ambiguous parsing and defer to the analyzer; never force a low-confidence deterministic guess. Stop after C1.

### C2 — Narrow and auditable query-analyzer contract

- **Status:** NOT_STARTED
- **Problem:** A broad analyzer can become an opaque answer-location oracle, emit exact files/pages, and cause query drift.
- **Goal:** Restrict LLM analysis to intent/confidence, concepts, entities, semantic/lexical terms, and unresolved ambiguity.
- **Why this stage:** C1 removes deterministic work; C2 makes the remaining semantic contract safe before query builders consume it.
- **Intended design:** Merge deterministic fields with bounded LLM output; preserve explicit symbols; reject ordinary answer paths/pages/benchmark shortcuts; persist field provenance and confidence.
- **Functional requirements:** Validate known intents, limited concepts, non-speculative terms, explicit-symbol preservation, and complete trace output.
- **Explicit out of scope:** Building semantic/lexical queries, resolving the full entity graph, tuning individual outputs to Gold evidence, or ranking changes.
- **Dependencies:** C1 and reviewed analyzer fixtures.
- **Authorized evaluation tier:** T0 contract tests and T2 analyzer/paraphrase set.
- **Primary metrics:** Intent accuracy, explicit-symbol recall, core-concept recall, spurious-concept rate, and analyzer cost.
- **Acceptance criteria:** High-confidence question understanding is retained without answer-location shortcuts; audit traces explain output sources.
- **Failure handling:** Reduce speculative output or preserve raw question ambiguity; do not add expected files/pages. Stop after C2.

### C3 — SemanticQueryBuilder for dense retrieval

- **Status:** NOT_STARTED
- **Problem:** Dense retrieval uses mainly the raw question even when the analyzer identifies useful concepts, while free-form rewriting risks answer-oriented drift.
- **Goal:** Build a semantic query in which the original question remains primary and a small number of high-confidence concepts are supplementary.
- **Why this stage:** C1/C2 create trustworthy inputs; dense construction must be isolated before sparse construction or fusion tuning.
- **Intended design:** Combine the untouched question with capped, high-confidence resolved concepts; exclude file/page hints; retain raw-question representation for audit and ablation.
- **Functional requirements:** Confidence/cap rules, deterministic composition, trace persistence, raw-versus-semantic ablation, and no replacement of explicit user meaning.
- **Explicit out of scope:** Sparse query design, exact/entity-first retrieval, fusion weights, answer prompts, or benchmark concept injection.
- **Dependencies:** C2, A2 traces, B2 embedding contract.
- **Authorized evaluation tier:** T0, targeted T2 dense/paraphrase subset; no full E2E.
- **Primary metrics:** Dense Recall@5/@10, MRR, identifier-free novel retrieval, English paraphrase robustness, and query-drift rate.
- **Acceptance criteria:** Novel dense retrieval improves meaningfully or robustly across expression types while targeted benchmark recall stays within tolerance.
- **Failure handling:** Reduce/remove the generic supplementary concept mechanism when drift occurs; never add more benchmark-specific terms. Stop after C3.

### C4 — LexicalQueryBuilder for sparse retrieval

- **Status:** NOT_STARTED
- **Problem:** Sparse BM25 should emphasize lexical anchors and need not consume the same text as dense retrieval.
- **Goal:** Build a bounded lexical query from explicit symbols, canonical entities, accepted aliases, and reliable technical terminology.
- **Why this stage:** Dense behavior has been isolated and B1/B3 secured sparse correctness/identity, enabling independent lexical measurement.
- **Intended design:** Preserve exact identifiers, use only validated aliases/canonical names, include useful lexical concepts, and avoid turning speculation into mandatory terms.
- **Functional requirements:** Deterministic query receipt, trace persistence, rare-identifier retention, English-only contract, and raw-query ablation.
- **Explicit out of scope:** Dense construction, multilingual models/tokenization/aliases, fusion tuning, or benchmark phrase expansions.
- **Dependencies:** B1/B3, C2, entity information currently available without Phase D.
- **Authorized evaluation tier:** T0 plus targeted T2 lexical/rare-identifier/paraphrase subset.
- **Primary metrics:** Sparse Recall@5/@10, MRR, rare-identifier and technical-term retrieval, lexical paraphrase performance.
- **Acceptance criteria:** Sparse retrieval benefits across a class of lexical questions without query drift or benchmark-only terms.
- **Failure handling:** Remove weak speculative terms and preserve raw/explicit anchors; do not compensate with per-question aliases. Stop after C4.

### C5 — Entity-first exact retrieval

- **Status:** NOT_STARTED
- **Problem:** Broad ILIKE lookup handles literal identifiers but poorly resolves descriptive references to canonical technical entities.
- **Goal:** Resolve exact symbols and accepted aliases to canonical objects before robust lexical fallbacks.
- **Why this stage:** C1–C4 supply explicit and semantic/lexical terms; C5 creates the interface later expanded by Phase D.
- **Intended design:** Prefer exact symbol, accepted alias, resolved entity relation, trigram/FTS where appropriate, then broad ILIKE fallback; preserve current fallbacks during transition.
- **Functional requirements:** Canonical lookup receipt, ambiguity handling, locked-version filtering, fallback observability, and trace candidates.
- **Explicit out of scope:** Full concept ontology/resolver, mass alias creation, removing fallbacks, fusion tuning, or question-specific mapping.
- **Dependencies:** C1/C2/C4, accepted aliases, current object/relation storage.
- **Authorized evaluation tier:** T0 and T2 exact-symbol plus identifier-free descriptive subset.
- **Primary metrics:** Exact Recall@5/@10, Top-k resolution, false-resolution rate, explicit/identifier-free gap.
- **Acceptance criteria:** Canonical exact lookup improves descriptive retrieval while preserving literal-symbol performance and version safety.
- **Failure handling:** Return ambiguity or use lexical fallback instead of guessing; do not manufacture aliases for failures. Stop after C5.

### C6 — Fusion evaluation and intent-aware tuning

- **Status:** NOT_STARTED
- **Problem:** Static weights may fit exposed questions and not generalize across exact, dense, sparse, paper, workflow, and graph channels.
- **Goal:** Select fusion behavior from aggregate benchmark-plus-novel evidence rather than single-case nudging.
- **Why this stage:** Each channel/query path is now independently correct and measurable, so fusion effects are interpretable.
- **Intended design:** Replay frozen channel candidates and compare current, exact-heavy, semantic-heavy, sparse-heavy, and carefully justified intent-aware strategies; retain application-side multi-channel fusion where appropriate.
- **Functional requirements:** Fixed development data, frozen-candidate replay, per-intent and aggregate reports, stable configuration identity, and no leakage from validation/holdout.
- **Explicit out of scope:** Migrating all fusion into Qdrant for neatness, per-question weights, answer changes, or query-rule additions.
- **Dependencies:** C3–C5, A2 reusable candidates, curated novel_dev.
- **Authorized evaluation tier:** T0 replay and targeted T2; broader retrieval only after strategy selection.
- **Primary metrics:** Combined Candidate Recall@20, fused Recall@10, MRR, final-evidence recall, novel/benchmark gap.
- **Acceptance criteria:** One strategy is selected by aggregate evidence and remains auditable; no manual one-failure weight nudges.
- **Failure handling:** Retain current weights if alternatives lack robust evidence; report inconclusive rather than overfit. Stop after C6.

### C7 — Clear source constraints and evidence diversity

- **Status:** NOT_STARTED
- **Problem:** Current source budgets may act as opaque maximum caps and can force/suppress evidence without clear minimum/preferred/maximum/required semantics.
- **Goal:** Make evidence-selection constraints explicit while preserving necessary exact evidence and useful diversity.
- **Why this stage:** Fusion is fixed first, so selection policy can be evaluated without confounding rank changes.
- **Intended design:** Represent minimum/preferred/maximum/required only where meaningful; never force irrelevant evidence merely to fill a quota; trace every selection/exclusion reason.
- **Functional requirements:** Preserve mandatory exact-symbol evidence, prevent one source/type domination, honor genuinely required source types, and expose policy decisions.
- **Explicit out of scope:** Benchmark-specific quotas, new retrieval channels, query builders, or answer requirements.
- **Dependencies:** C6 ranked pools and A2 traces.
- **Authorized evaluation tier:** T0 frozen selection tests and targeted T2 source-diversity/evidence cases.
- **Primary metrics:** Final Evidence Recall, precision/relevance where Gold supports it, required-source satisfaction, and displacement rate.
- **Acceptance criteria:** Semantics are explicit; useful diversity remains; irrelevant quota evidence is not forced; critical exact evidence is retained.
- **Failure handling:** Simplify constraints or preserve the existing selector if gains are not robust; never add case-specific caps. Stop after C7.

### C8 — Global rerank after targeted retrieval

- **Status:** NOT_STARTED
- **Problem:** Targeted retrieval can append new evidence and truncate without globally reconsidering initial and targeted candidates.
- **Goal:** Treat targeted results as candidates in a deduplicated global fusion/rerank/selection pass.
- **Why this stage:** Query/channel/fusion/selection contracts must be stable before changing the second retrieval pass.
- **Intended design:** Merge initial and targeted pools, deduplicate, globally fuse/rerank, then apply C7 selection; preserve strong initial evidence unless genuinely outranked.
- **Functional requirements:** Trace both pools and global decisions; measure missing-evidence recovery and initial-evidence displacement; retain version/source constraints.
- **Explicit out of scope:** Question decomposition-driven objectives (E3), new query builders, benchmark-specific targeted terms, or T5.
- **Dependencies:** C6/C7 and existing targeted-retrieval loop.
- **Authorized evaluation tier:** T0/T2 incomplete-evidence cases, then Phase-C T3 benchmark and available novel retrieval plus small T4 `qa`.
- **Primary metrics:** Targeted retrieval success rate, retained strong-evidence rate, final-evidence recall, and generalization gap.
- **Acceptance criteria:** Missing evidence found by the targeted pass survives final selection, while good initial evidence is not unnecessarily displaced.
- **Failure handling:** Narrow global merge/rerank logic and retain safe initial evidence; do not privilege a case-specific candidate. Stop after C8 and do not run T5.

## Phase D — Concept and entity knowledge abstraction

### D1 — Concept/entity schema

- **Status:** NOT_STARTED
- **Problem:** Query expansions and routing carry PANDA knowledge that belongs in auditable corpus/entity/relation structures.
- **Goal:** Introduce a restrained domain entity model by extending existing KnowledgeObject/relation architecture.
- **Why this stage:** Retrieval interfaces are proven before adding a knowledge abstraction that they can consume.
- **Intended design:** Add only justified categories such as Concept, Symbol, Class, Function, File, Workflow, DataProduct, Configuration, PaperSection, or Algorithm and relations such as DEFINED_IN, IMPLEMENTED_BY, CALLS, READS, WRITES, PRODUCES, CONSUMES, CONFIGURES, USES, PART_OF, DESCRIBED_IN, and RELATED_TO.
- **Functional requirements:** Versioned provenance, review status, stable identifiers, validation, storage/index compatibility, and traceable relation evidence.
- **Explicit out of scope:** Mass query-rule migration, a separate graph platform, unvalidated automatic ontology generation, or aliases for evaluation cases.
- **Dependencies:** Phase C entity-first interface and current object/relation schema.
- **Authorized evaluation tier:** T0 schema/migration/integrity fixtures and tiny retrieval smoke.
- **Primary metrics:** Schema validity, provenance completeness, accepted relation resolution, and zero index-integrity regression.
- **Acceptance criteria:** A small representative knowledge set is expressible through existing architecture without encoding answer locations.
- **Failure handling:** Reduce categories/relations to evidenced use cases; keep uncertain proposals pending rather than accepted. Stop after D1.

### D2 — Concept/entity resolver

- **Status:** NOT_STARTED
- **Problem:** Users often describe PANDA concepts/components without naming their exact classes or symbols.
- **Goal:** Resolve genuine English terminology, abbreviations, descriptive paraphrases, and implementation-oriented descriptions to canonical entities.
- **Why this stage:** D1 provides the reviewed target space; resolving before migration lets quality be measured independently.
- **Intended design:** Separate true aliases from related concepts connected by graph relations; rank candidates with ambiguity/confidence; fail safely instead of forcing a match.
- **Functional requirements:** Top-k candidates, provenance, version scope, false-resolution controls, accepted-alias governance, and trace integration.
- **Explicit out of scope:** Giant artificial alias lists, benchmark answer locations, multilingual aliases, or mass shortcut deletion.
- **Dependencies:** D1 and C5 resolver interface.
- **Authorized evaluation tier:** T0 plus targeted T2 terminology/paraphrase resolution.
- **Primary metrics:** Entity Top-1/Top-3 accuracy, false-resolution/abstention rate, and downstream exact recall.
- **Acceptance criteria:** Stable terminology resolves accurately across unseen expression forms with bounded false positives.
- **Failure handling:** Abstain or expose ambiguity; do not turn related concepts into aliases to force Top-1. Stop after D2.

### D3 — Small shortcut-migration experiment

- **Status:** NOT_STARTED
- **Problem:** Wholesale removal of proven compatibility rules before the structured path is validated would cause avoidable regression.
- **Goal:** Replace roughly 5–10 representative phrase-to-file/page shortcuts with phrase-to-concept/entity-to-relation/retrieval paths.
- **Why this stage:** D1/D2 must demonstrate that structured knowledge can reproduce useful behavior before broader migration.
- **Intended design:** Select nontrivial rules across types, record their old dependency, migrate one bounded batch, and compare benchmark plus novel retrieval.
- **Functional requirements:** Auditable selection, before/after traces, no direct answer-location encoding in replacements, rollback boundary, and aggregate report.
- **Explicit out of scope:** Deleting the entire expansion file, choosing only trivial rules, answer changes, or hidden-case tuning.
- **Dependencies:** D1/D2 and A3/Phase-C baselines.
- **Authorized evaluation tier:** T0, targeted T2, and a small comparison set.
- **Primary metrics:** Reproduction of useful retrieval, novel retrieval, shortcut dependency, final-evidence recall, and regressions.
- **Acceptance criteria:** Structured paths reproduce useful behavior without encoding exact evaluation answer locations and show credible generality.
- **Failure handling:** Stop migration if performance collapses; keep old rules and fix the general resolver/schema rather than add replacement hard-coded rules. Stop after D3.

### D4 — Incremental migration of appropriate query expansions

- **Status:** NOT_STARTED
- **Problem:** Remaining shortcut knowledge should move gradually, while genuine terminology and normalization must remain.
- **Goal:** Migrate appropriate shortcuts in small measured batches only after D3 passes.
- **Why this stage:** Small batches preserve accountability and localize regressions while the structured layer matures.
- **Intended design:** Retain stable aliases/domain vocabulary/normalization; replace phrase-to-file/page, negative-control, and answer-location shortcuts where a generic mechanism is proven.
- **Functional requirements:** Batch inventory, replacement mechanism, before/after retrieval and novel checks, dependency metric, and reversible changes.
- **Explicit out of scope:** One-operation deletion of `query_expansions.yaml`, removing stable vocabulary, or re-adding hidden shortcuts after one failure.
- **Dependencies:** D3 PASS.
- **Authorized evaluation tier:** T0 and T2 per batch; a Phase-D T3 only at an agreed boundary.
- **Primary metrics:** Benchmark/novel retrieval, generalization gap, benchmark dependency, and rules migrated/retained by classification.
- **Acceptance criteria:** Each batch has an evidenced generic replacement, bounded benchmark regression, and no grounding regression.
- **Failure handling:** Pause the batch and retain prior compatibility behavior; repair the generic mechanism at its owning layer. Stop after each requested D4 batch.

## Phase E — Answer generalization

### E1 — Dynamic question decomposition

- **Status:** NOT_STARTED
- **Problem:** A single `question_core` plus domain-specific requirements can be complete on known questions but miss unseen multi-part structure.
- **Goal:** Derive approximately 1–5 evidence-independent answer points from the question itself.
- **Why this stage:** Retrieval generalization and structured knowledge must be established before asking decomposition to drive completeness.
- **Intended design:** Represent mechanism, implementation, data flow, comparison, locator, workflow step, cause/reason, or API behavior; initially run diagnostically alongside existing requirements.
- **Functional requirements:** Question-only input, stable IDs, limited count, paraphrase stability, over-decomposition checks, and trace/audit output.
- **Explicit out of scope:** Deriving points from retrieved evidence, removing existing requirements, targeted retrieval, or benchmark templates.
- **Dependencies:** Phases C/D and curated answer-point annotations.
- **Authorized evaluation tier:** T0 and targeted T2 multi-part/paraphrase set.
- **Primary metrics:** Gold answer-point recall, over-decomposition rate, paraphrase stability, and benchmark-versus-novel gap.
- **Acceptance criteria:** Decomposition captures required question facets generically without mirroring whatever evidence was found.
- **Failure handling:** Reduce/merge unstable points or mark ambiguity; retain old requirements during diagnosis. Stop after E1.

### E2 — Answer-point coverage and claim mapping

- **Status:** NOT_STARTED
- **Problem:** Atomic claims are not generically accountable to the facets the user asked to have answered.
- **Goal:** Map every generated claim to one or more answer-point IDs and evidence IDs, then measure completeness and support.
- **Why this stage:** E1 quality must be proven before its points become a runtime completeness contract.
- **Intended design:** Maintain explicit `claim -> answer_points -> evidence` mapping; run old answer requirements in parallel for regression comparison.
- **Functional requirements:** Validate IDs, point coverage, unsupported/missing-point detection, audit-only versus user-visible claims, and refusal semantics.
- **Explicit out of scope:** Immediate deletion of existing requirements, targeted retrieval, composer, or benchmark-specific mappings.
- **Dependencies:** E1 and current evidence-bound claim/verifier architecture.
- **Authorized evaluation tier:** T0 plus targeted T2 benchmark/novel QA cases.
- **Primary metrics:** Point coverage, unsupported claims, missing-point detection precision/recall, and benchmark/novel difference.
- **Acceptance criteria:** Visible claims map validly to requested points and evidence; missing facets are detected without adding facts.
- **Failure handling:** Keep old completeness checks active and treat mappings diagnostically until reliable. Stop after E2.

### E3 — Missing-point targeted retrieval

- **Status:** NOT_STARTED
- **Problem:** Once a genuine answer point is missing, the system needs a generic retrieval objective rather than hidden domain requirements.
- **Goal:** Use missing answer points to trigger one bounded targeted retrieval, followed by the global C8 merge/rerank/selection path.
- **Why this stage:** Requires proven decomposition, claim mapping, and global targeted-rerank behavior.
- **Intended design:** Initial evidence → point coverage → missing point → targeted retrieval → global rerank → updated evidence → answer/verification.
- **Functional requirements:** Bounded loops, explicit objectives, trace provenance, version safety, recovery measurement, and no arbitrary hidden requirements.
- **Explicit out of scope:** New benchmark rules, unbounded retries, answer composer, or removing compatibility behavior before Phase F.
- **Dependencies:** E1/E2 PASS and C8.
- **Authorized evaluation tier:** T0, targeted T2 multi-hop/cross-repository/workflow/multi-part novel cases, then small Phase-E T4.
- **Primary metrics:** Missing-point recovery, targeted retrieval success, final point coverage, unsupported claims, and cost.
- **Acceptance criteria:** Missing requested facets are recovered more often without displacing strong evidence or increasing unsupported claims.
- **Failure handling:** Stop after the bounded attempt and return an honest incomplete/refusal outcome; never invent a requirement or fact. Stop after E3.

## Phase F — Benchmark dependency cleanup and final answering

### F1 — Benchmark rule inventory

- **Status:** NOT_STARTED
- **Problem:** Benchmark phrases, expected symbols/paths/pages, negative controls, special requirements, and bespoke sufficiency checks are distributed across code/configuration.
- **Goal:** Produce an auditable inventory without changing runtime behavior.
- **Why this stage:** Generic C/D/E mechanisms must exist before classifying what they can safely replace.
- **Intended design:** Inspect QA, retrieval, prompts, expansions, and policies; classify each rule as stable domain knowledge, generic policy, benchmark shortcut, benchmark-specific guard, or uncertain.
- **Functional requirements:** Location, trigger, effect, supported cases, proposed generic owner, classification rationale, and no removals.
- **Explicit out of scope:** Runtime edits, rule deletion, scoring changes, or migration.
- **Dependencies:** Completed generic architecture and current repository inventory.
- **Authorized evaluation tier:** T0/static audit only; no model calls required.
- **Primary metrics:** Inventory completeness, classification coverage, and unresolved/uncertain count.
- **Acceptance criteria:** Every identified dependency is located and classified with evidence and a potential replacement layer.
- **Failure handling:** Mark uncertain rather than infer intent; do not remove anything. Stop after F1.

### F2 — Generalize benchmark-specific guards

- **Status:** NOT_STARTED
- **Problem:** Guards for one named symbol or premise fail on unseen instances of the same error class.
- **Goal:** Replace selected guards with canonical resolution, locked-corpus existence checks, and generic false-premise/insufficient-evidence behavior.
- **Why this stage:** F1 identifies guards and D/C supply resolver/existence mechanisms.
- **Intended design:** Test the counterfactual: replacing the concrete PANDA name with another unseen member of the class must still work.
- **Functional requirements:** Bounded batches, generic contract tests, before/after behavior, version safety, and explicit replacement provenance.
- **Explicit out of scope:** Shortcut removal, answer composer, one-off expected-symbol lists, or relaxing refusal safety.
- **Dependencies:** F1, C5, D2, existing verifier/refusal contracts.
- **Authorized evaluation tier:** T0 and targeted T2 false-premise/unseen-symbol cases.
- **Primary metrics:** Unseen-symbol correctness, false-positive resolution, refusal correctness, and benchmark regression.
- **Acceptance criteria:** Replacements work for the failure class without concrete-name branching and preserve grounding.
- **Failure handling:** Retain the old guard until the generic mechanism passes; do not disguise a case list as a resolver. Stop after F2.

### F3 — Incremental shortcut removal

- **Status:** NOT_STARTED
- **Problem:** Phrase-to-answer-location shortcuts obscure true generalization but removing them wholesale risks strong benchmark behavior.
- **Goal:** Remove only shortcuts that proven generic mechanisms replace, in batches of roughly 5–10.
- **Why this stage:** F1/F2 classify dependencies and C/D/E provide measured replacements.
- **Intended design:** For each batch, identify replacement, run targeted benchmark and novel retrieval/QA, and measure dependency/generalization rather than demanding zero score movement.
- **Functional requirements:** Batch manifest, before/after traces/metrics, bounded regression tolerance, rollback, and no leakage from validation/holdout.
- **Explicit out of scope:** Immediate deletion of all expansions, re-adding a shortcut after one exposed failure, or removing stable domain terminology.
- **Dependencies:** F1/F2 and passing relevant C/D/E mechanisms.
- **Authorized evaluation tier:** T0/T2 per batch; phase-level T3/T4 when justified; no automatic T5.
- **Primary metrics:** Novel performance, benchmark performance, grounding/citation integrity, generalization gap, and benchmark dependency.
- **Acceptance criteria:** Novel performance improves materially or dependency falls while grounding stays strong and benchmark regression remains within agreed tolerance.
- **Failure handling:** Diagnose owning generic layer and pause the batch; do not tune a replacement to the failed question. Stop after each requested batch.

### F4 — Separate answer-generation and semantic-verification roles

- **Status:** NOT_STARTED
- **Problem:** One client/model role for generation and review creates correlated failures and hides objectively checkable verification.
- **Goal:** Make generation and verification roles/configuration/client paths separable, even if they initially share a model.
- **Why this stage:** Answer completeness is generic and shortcut dependency is reduced, allowing role separation without confounded behavior.
- **Intended design:** Move identifier/path/source/version/locator/evidence-ID/numeric provenance checks to deterministic logic; reserve semantic verification for entailment, causality, comparison, and faithful summary.
- **Functional requirements:** Independent role identities/usage, deterministic fail-closed checks, semantic review contract, and compatibility with bounded revision.
- **Explicit out of scope:** Switching models merely for novelty, composer, unbounded review, or loosening verification.
- **Dependencies:** E2/E3 and existing verifier.
- **Authorized evaluation tier:** T0 verifier fixtures and targeted T2 supported/unsupported claims.
- **Primary metrics:** False acceptance, false rejection, deterministic coverage, model-call/token cost, and grounding.
- **Acceptance criteria:** Roles are independently configurable/auditable and objective facts are checked deterministically without quality regression.
- **Failure handling:** Retain the safe existing verifier path when separation is inconclusive; never silently bypass verification. Stop after F4.

### F5 — Bounded Answer Composer

- **Status:** NOT_STARTED
- **Problem:** Deterministic verified-claim rendering is safe but can be mechanical and claim-by-claim.
- **Goal:** Improve readability without reopening factual generation.
- **Why this stage:** Only after claims, answer points, and verification roles form a stable security boundary can composition be safely added.
- **Intended design:** Composer receives verified claims only, may reorder/merge/group/add discourse connectors/lightly paraphrase, and returns paragraphs plus source claim IDs.
- **Functional requirements:** Validate claim IDs, claim coverage, identifiers, numeric literals, causal/comparison content, and zero new facts; fall back to deterministic renderer on any failure.
- **Explicit out of scope:** Raw retrieval evidence as composer input, new facts/entities/paths/numbers/causal relations/comparisons/requirements, or readability over safety.
- **Dependencies:** E2 and F4.
- **Authorized evaluation tier:** T0 adversarial validation and targeted T2 readability/faithfulness cases.
- **Primary metrics:** New factual hallucination rate (hard target 0), claim coverage, validation fallback rate, and human readability preference.
- **Acceptance criteria:** No new factual content is introduced and readability improves; every paragraph maps to verified claims.
- **Failure handling:** Fall back to deterministic verified-claim rendering, record validation failure, and do not retry freely. Stop after F5.

### F6 — Release evaluation and generalization gate

- **Status:** NOT_STARTED
- **Problem:** Final readiness requires simultaneous evidence on exposed benchmark, novel validation, protected holdout, and shortcut-dependency ablations.
- **Goal:** Execute the complete release measurement and decide whether generalization improved without sacrificing grounding/version safety.
- **Why this stage:** This is the final gate only after all requested architecture and cleanup tasks are complete/frozen.
- **Intended design:** Freeze identity; run T5 full benchmark, novel, external holdout, and ablations; report infrastructure, query, retrieval, answer, targeted retrieval, composer, cost, generalization gap, and benchmark dependency.
- **Functional requirements:** Explicit `T5`/`release evaluation` authorization, protected holdout handling, immutable records, full usage accounting, complete splits, and no tuning from holdout outcomes.
- **Explicit out of scope:** Any implementation fix during the same frozen run, targeted holdout tuning, mixed identities, or diagnostic composites represented as release gates.
- **Dependencies:** F1–F5 and explicit user authorization.
- **Authorized evaluation tier:** T5 only.
- **Primary metrics:** Index/embedding integrity; intent/symbol/concept metrics; Recall@5/@10/@20, MRR, final-evidence recall; point coverage, unsupported claims, citations/identifiers; targeted success; composer new-fact/readability; benchmark score, novel score, Generalization Gap, and Benchmark Dependency.
- **Acceptance criteria:** Planned thresholds are declared before running; grounding/citation/version invariants pass; novel performance and dependency/gap meet the approved release criteria with only bounded benchmark regression.
- **Failure handling:** Report `FAIL` or `INCONCLUSIVE`, archive immutable evidence, and do not tune on protected holdout. A later fix requires a new explicitly requested roadmap task and candidate. Stop after F6.

## Novel dataset targets and release metrics

The eventual curation target is approximately 30 `novel_dev`, 15 `novel_validation`, and 15 externally loaded `novel_holdout` questions across API/symbol, implementation, data flow, workflow, theory, troubleshooting, usage, and cross-repository reasoning. Questions must vary knowledge recognition/combination, not merely paraphrase benchmark wording. Generated drafts require human review and never constitute a holdout.

At release, define:

`Generalization Gap = benchmark score - novel score`

and measure Benchmark Dependency as the score difference between full compatibility behavior and the approved generic/shortcut-ablation configuration. The desired direction is higher novel performance, approximately preserved benchmark performance, a smaller gap, lower dependency, and unchanged grounding/version safety.
