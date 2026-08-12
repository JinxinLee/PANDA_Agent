# Novel generalization datasets

This directory defines the curation boundary for genuinely novel, English-only PANDA questions. No novel question is currently committed, so no novel measurement is claimed.

The existing evaluation runner accepts external datasets through `panda-qa-eval run <mode> --dataset <path>` and supports these splits:

- `novel_dev`: inspectable during development;
- `novel_validation`: phase-level validation; do not tune individual cases;
- `novel_holdout`: load from an external path and keep Gold evidence outside normal Codex-visible development inputs.

Novel IDs use `n###`. Each curated question uses the existing strict question schema, including English language, intent, locked source versions, evidence groups, answer points, review status, reviewer, and review timestamp. This lets retrieval metrics be computed only when human-reviewed evidence Gold exists.

Target sizes are approximately 30 development, 15 validation, and 15 protected holdout questions. Categories should cover API/symbol, implementation, data flow, workflow, theory, troubleshooting, usage, and cross-repository reasoning. Expression diversity should include canonical, descriptive, causal, implementation-oriented, identifier-free, and identifier-heavy wording.

A trivial paraphrase of an exposed benchmark question is not novel. Generated questions may be used as untrusted drafts for human curation, but must not be represented as a protected holdout or frozen Gold.
