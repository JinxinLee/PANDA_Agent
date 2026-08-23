# PANDA Agent — Evaluation Policy

This document defines stable evaluation rules for the Generalization Phase. Current candidates, runs, metrics, and limitations belong in `docs/EVALUATION_STATUS.md`.

## 1. Evaluation integrity

1. Evaluation questions are measurement data, not implementation specifications.
2. A change must address a general failure class and must be repaired at the layer where it originates.
3. Benchmark, novel development, novel validation, and protected holdout data have different exposure rules and must not be silently combined.
4. Measured results must be distinguished from planned acceptance targets.
5. Diagnostic subsets and mixed-provenance composites are not complete gates.
6. Immutable records and compatible intermediate artifacts should be reused instead of regenerating model output.
7. English is the product language. Do not add multilingual models, aliases, tokenization, or query rules without an explicit scope change.

Do not add question-specific trigger phrases, expected symbols, answer paths, thesis/PDF pages, expected answers, source quotas, weights, or guards merely to make an exposed question pass. Stable domain terminology may be represented as curated corpus knowledge, accepted aliases, entities, or relations when independently justified.

## 2. Failure taxonomy and ownership

Assign one primary classification and optional secondary notes:

| Code | Failure | Owning layer |
|---|---|---|
| `Q1` | Query-understanding failure | deterministic parser or analyzer |
| `Q2` | Entity-resolution failure | concept/entity resolver |
| `R1` | Candidate-recall failure | retrieval channel or index |
| `R2` | Fusion/ranking failure | fusion or reranker |
| `R3` | Evidence-selection failure | final evidence selector |
| `D1` | Question-decomposition failure | answer-point decomposition |
| `A1` | Answer-generation failure | bounded answer generation |
| `V1` | Verification false rejection | verifier |
| `V2` | Verification false acceptance | verifier |
| `C1` | Corpus/evidence genuinely insufficient | corpus or explicit refusal |

An `R1` failure must not be repaired with an answer-prompt instruction. A `Q2` failure must not be repaired with a fixed page hint. A `D1` failure must not be repaired with one benchmark-specific answer requirement. If evidence shows the initial classification was wrong, reclassify it explicitly before changing another layer.

## 3. Evaluation modes

Every run records its mode and pipeline boundaries.

### `retrieval`

Runs current query analysis, all production retrieval channels, fusion/reranking, and evidence selection. It writes a structured retrieval trace. It must not call answer generation, runtime claim verification/revision, or the external rubric judge.

### `qa`

Runs retrieval plus production answer generation and runtime verification/revision. It must not automatically call the external evaluation judge. Use it for targeted behavior checks and small stratified E2E baselines.

### `full`

Runs the complete E2E path and the configured external judge. This preserves the former judged-QA behavior and is reserved for tiers that explicitly need external scoring.

Changing evaluation mode must not change production retrieval or QA behavior; it changes only which evaluation stages are entered.

## 4. Evaluation pyramid

### T0 — Deterministic, unit, and integrity

Use frequently. Vertex use is zero or negligible. Examples include schema validation, serialization, frozen-candidate fusion, index identity, parser and locator fixtures, deterministic verifier logic, and offline rescore.

### T1 — Small targeted smoke

Use roughly 5–12 relevant cases, or fewer when one case is sufficient. Select only cases that test the current subsystem and stop when the hypothesis is answered.

### T2 — Targeted regression

Use roughly 10–30 relevant cases. Examples include a lexical/rare-identifier subset for BM25, a semantic/paraphrase subset for dense query construction, or a multi-part subset for decomposition.

### T3 — Full retrieval-only

Run a complete relevant dataset in `retrieval` mode at phase boundaries. T3 requires explicit authorization in the current task. The existence of a complete dataset, “establish a baseline”, “create a frozen baseline”, or completion of A3 does not authorize T3. Do not call answer generation, runtime verification/revision, or the external judge.

Retrieval mode does not execute the production sufficiency/refusal decision, so `expected_status_accuracy` is N/A in retrieval-mode formal gates. Version-conflict rejection remains a hard retrieval responsibility. Ordinary Recall/MRR/final-evidence metrics apply only to Gold `answered` questions; Gold `insufficient_evidence` cases are not converted into ordinary answered retrieval cases merely because a synthetic retrieval status says answered.

Formal product-scope gates use a deterministic declared selector from the approved dataset plus a versioned reviewed product-language calibration when present (for example `split == dev`, reviewed `effective_product_language == en`, `review_status == approved`) and require the exact complete selector ID set. Raw benchmark language metadata may be overridden by the reviewed calibration without mutating historical Gold; code identifiers, symbols, paths, and hashes do not make an otherwise English query mixed. Multilingual questions remain valid diagnostic assets but are outside the formal English product gate. Arbitrary hand-picked subsets cannot be declared complete, and completeness is ID-set based, not fixed-count based.

A reviewed product-language calibration is applied only when it is compatible with the exact active Gold identity/scope: benchmark version, file SHA-256, split, override IDs, and raw-language claims must match Gold, and the calibration's declared formal/non-English ID sets must equal the IDs independently derived from Gold + reviewed overrides. Incompatible calibrations are never silently applied.

Formal top-K retrieval metrics (Recall@5/@10/@20) use the canonical final-ranked stage (`diagnostics.ranked_object_ids` when present), not the LLM reranker output. Reranker rank and final-ranked rank are distinct diagnostic concepts and must be reported separately with explicit 0-based/1-based fields.

Persisted `fusion_scores` dictionary key order is not valid historical fused-rank provenance after key-sorted serialization. Formal fused rank may only come from an authoritative frozen ordered fusion trace (for example `RetrievalTrace.fused_candidates`); when no such ordered artifact exists, fused rank must be reported `N/A`, not reconstructed from dict key order or score sorting.

Complete formal development execution is derived from exact dataset-approved ID sets, not from a hard-coded question count. No fixed `80`/`59` or other number defines completeness.

### T4 — Small stratified E2E

Normally use approximately 20 benchmark plus 20 trustworthy novel questions where available. Run `qa`: retrieval, answer generation, and runtime verification/revision. Invoke the external judge only when separately and explicitly justified.

### T5 — Full release evaluation

Run full benchmark E2E, full novel E2E, protected holdout, external judging, release metrics, and required ablations. T5 is rare and requires an explicit user instruction containing `T5` or `release evaluation`.

The phrases “run tests”, “verify the change”, “make sure it works”, and “check regressions” do not authorize T5.

### A3 bootstrap default

A3 is not a phase-boundary T3. It should normally use 20–30 deterministically stratified benchmark questions in `retrieval`, 10–20 representative benchmark questions in `qa`, and any trustworthy human-authored novel questions already available. Full retrieval-only evaluation requires separate explicit authorization or an explicitly authorized phase-boundary T3.

Persist A3 retrieval and QA case IDs in a versioned fixed manifest and reuse them unchanged for before/after comparisons. Call the current package an **English Gold Stratified Bootstrap Baseline** and state every English Gold intent with no eligible approved case as unevaluated; do not describe it as a complete generalization or all-intent baseline.

## 5. Cost decision

Before every evaluation, answer:

1. What hypothesis is being tested?
2. What is the smallest dataset that can test it?
3. Which model calls are required?

Prefer static inspection, then T0, one affected case, a few sentinels, T2, T3, T4, and finally T5. Do not escalate merely for reassurance. Do not call answer generation to test BM25, call the judge to test retrieval, rerun an analyzer when a compatible frozen plan answers the hypothesis, recompute embeddings when a compatible cache exists, or run unrelated tests because they are available.

Record per run: purpose, mode, dataset/subset, question count, Vertex invocation, model-call count, token usage, exceptions, and measured metrics. Environment or quota failures are not quality pass/fail evidence.

## 6. Novel dataset exposure

- `novel_dev` is exposed and may be inspected for detailed failure-class development, but it does not permit question-specific fixes.
- `novel_validation` is primarily for phase-level and frozen-candidate comparison. Aggregate metrics alone do not contaminate every case; when a case-level outcome is inspected and used to guide development, append an exposure-ledger event and stop treating that case as pristine validation evidence for that development lineage.
- `novel_holdout` loads only from an external protected path for an explicitly authorized release/T5 evaluation. Its questions, Gold evidence, answer points, and hidden expected answers do not enter the repository or normal Codex development context, and its outcomes cannot be used to repair and rerun the same frozen release attempt.

A trivial paraphrase or mechanical entity substitution is not novel by itself. Evidence overlap is allowed when the information need, relation, evidence combination, or reasoning topology is substantively different. Generated questions are untrusted drafts until human review and are never a protected holdout. Gold evidence must be established independently from PANDA Agent outputs; do not report retrieval metrics when reviewed Gold evidence does not exist.

The authoritative split, novelty, annotation, review, exposure, external-holdout, versioning, and amendment rules are in `docs/NOVEL_DATASET_CURATION_CONTRACT.md`.

## 7. Change-impact and reindex policy

| Change | Dense document re-embed | Sparse/index rebuild |
|---|---:|---:|
| Prompt | No | No |
| Query analyzer | No | No |
| Fusion/reranking | No | No |
| Answer/verifier/composer | No | No |
| Locator metadata only | Generally no | Only if the deployed payload/index requires it |
| BM25 IDF/index modifier | No | Yes, where required |
| Sparse model/configuration | No | Yes |
| Chunk text | Affected objects where practical | Affected objects where practical |
| Embedding model | Yes | No, unless independently changed |
| Embedding dimensions | Yes | No, unless independently changed |
| Embedding text construction | Affected or all dense objects as required | Only if sparse input also changes |

Changing `index_schema_version` alone does not require dense regeneration when the cached dense embedding identity remains valid.

## 8. Frozen records, traces, and resume

During prototype roadmap development, normal Git commits are sufficient history. Working-tree tests and dirty-working-tree diagnostic evaluations are allowed; their provenance is the recorded base commit plus the then-current changes. They do not require a clean-tree rerun, frozen candidate, per-file integrity manifest, or hash regeneration. Strict immutable implementation identity is reserved for an explicitly authorized formal phase-boundary, T5/release, acceptance/release-candidate comparison, or explicit frozen-candidate request.

- Persist run manifests, atomic case records, structured retrieval traces, metrics, model usage, and exceptions.
- Resume interrupted runs without repeating completed cases.
- Reuse analyzer plans, channel candidates, selected evidence, claims, and verified claims only when their upstream behavior identity is compatible with the hypothesis.
- Original run records are immutable. Offline rescore produces new provenance and reports zero new model calls/tokens.
- Frozen traces may be loaded for fusion/evidence analysis without rerunning QA.
- Do not calculate gratuitous per-file hashes. Use Git, dataset, prompt/policy, corpus/index, and model identities where sufficient.

## 9. Formal candidate and gate rules

Freeze behavior-affecting identities before a formal complete run: repository/corpus/index, models and dimensions, prompts, retrieval/query policies, approved dataset, and relevant runtime packages. A behavior-changing edit creates a new candidate identity.

A complete split is complete only when its declared approved questions are present under one compatible identity. A subset, focused run, interrupted run, or mixed-provenance composite is diagnostic and cannot pass a full development, regression, acceptance, or release gate.

Hidden acceptance results may be used only for reporting, archival, and release decisions. They must not be used for targeted prompt, routing, retrieval, Gold, model, or scoring tuning.

## 10. Failure review and rescore

After a failed complete gate, create an auditable review containing failed metrics, expected/actual status, answer and claims, verification errors, evidence and locators, suspected owning layer, classification, action, rationale, and reviewer metadata.

Allowed review actions:

- `rescore`: deterministic evaluator error; preserve model output and recompute offline;
- `fix`: genuine system failure; return to targeted development at the owning layer;
- `waiver`: explicitly approved exception with identifier and rationale.

Do not silently relax global thresholds. Citation-integrity failures, wrong-version evidence, contradictions, unsupported claims, and unhandled exceptions are not waived by default.

## 11. Completion and stop rule

Report implementation, changed files, every evaluation and its cost, measured before/after metrics, exactly `PASS`/`FAIL`/`INCONCLUSIVE`, concrete limitations, and only the next roadmap task. Stop at the authorized tier and task boundary.

Do not automatically escalate:

`affected case → sentinels → T2 → T3 → T4 → T5`

Each escalation requires a decision-relevant reason, and T5 requires explicit authorization.
