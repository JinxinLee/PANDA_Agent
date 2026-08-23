# Novel generalization datasets

The authoritative governance rules are in `docs/NOVEL_DATASET_CURATION_CONTRACT.md`. This directory is the future repository boundary for genuinely novel, English-only PANDA questions. N0 defines the contract only: no novel question is currently committed, so no novel measurement is claimed.

The existing evaluation runner accepts external datasets through `panda-qa-eval run <mode> --dataset <path>` and supports these splits:

- `novel_dev`: inspectable during development;
- `novel_validation`: phase-level validation; do not tune individual cases;
- `novel_holdout`: load from an external path and keep Gold evidence outside normal Codex-visible development inputs.

Novel IDs use `n###`. Evaluator question records use the existing strict Gold schema, including English language, intent, locked source versions, evidence groups, answer points, review status, reviewer, and review timestamp. Novelty, coverage, origin, lifecycle, and exposure metadata belong in a separate sidecar keyed by question ID because the evaluator model forbids unknown fields. This lets existing evaluation semantics remain authoritative while retrieval metrics are computed only when human-reviewed evidence Gold exists.

Target sizes are approximately 30 development, 15 validation, and 15 protected holdout questions. Categories should cover API/symbol, implementation, data flow, workflow, theory, troubleshooting, usage, and cross-repository reasoning. Expression diversity should include canonical, descriptive, causal, implementation-oriented, identifier-free, and identifier-heavy wording.

A trivial paraphrase or mechanical entity substitution is not novel by itself. Generated questions may be used as untrusted drafts for human curation, but must not be represented as protected holdout or frozen Gold. N1 will create only the files needed for its 12–16 candidate `novel_dev` pilot; N0 does not create empty dataset placeholders.
