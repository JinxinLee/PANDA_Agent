# F6-A Attempt 2 — Immutable Run Receipt

Archival receipt (Stage R0 of F6-A2-FR1). The raw local run directory
(`data/evaluation/runs/f6a-rc2-gold-formal-full-20260913/`, gitignored) is the
**scientific evidence**; this committed receipt is the **integrity / audit
index**; the submitted result MD/JSON is the **lifecycle interpretation**.
Machine-readable companion: `evaluation/f6_a2_immutable_run_receipt.json`.

## Identity

```text
run_id                    = f6a-rc2-gold-formal-full-20260913
candidate_id              = f6a-rc2-20260913
candidate_manifest_sha256 = 5c70357757967ee33464b61db86f6af5dd618fbfb0e1a056d5879214b8916098
record_count              = 59
case_id_set_sha256        = 914ee1b4b3f937e6839416932b44de06fb0401589fd59825a63ac430c5361d1c
results_file_sha256       = e82bf74a7bdb62b425de203ab3660aed068fc9927f4e5dd348da46edc728ce9c
gate_matrix_sha256        = adf3703e8cc54079dcaadfdae8ad0b97c5d106eee3802f1f1551f80a0273fc03
traces_combined_sha256    = 8e4829b2347448cbf0121a8c722d62f38bfc9661013eb15c620ed3593391e708 (59 files)
```

Hash methods: `case_id_set_sha256` = SHA-256 over the compact JSON array of
sorted record IDs; `traces_combined_sha256` = SHA-256 over the concatenation
of per-case trace files in sorted filename order.

## Outcome summary

```text
status distribution   = 49 answered / 5 insufficient_evidence / 5 version_conflict
status mismatches     = 0
failed_gate_count     = 6
incomplete_gate_count = 0
release_score         = 0.9463276836158192
```

Failed-gate contributor case IDs (complete, derived from the immutable
records — includes contributors not named in the closeout narrative):

| gate | failing case IDs |
| ---- | ---------------- |
| final_evidence_recall | g001, g011, g013, g014, g016, g020, g021, g022, g044, g060 |
| critical_final_evidence_recall | g001, g011, g013, g014, g016, g020, g022, g044, g060 |
| required_source_coverage_answered | g016, g060 |
| paper_code_dual_source_rate | g060 |
| critical_answer_point_miss_count | g001, g005, g013, g022 |
| major_unsupported_claim_count | g113 |

## Usage (immutable record totals)

```text
total              = 376 calls / 3,313,651 tokens
runtime            = 314 calls / 2,903,448 tokens
  labeled qa_generation = 67 calls / 1,566,586 tokens
  labeled qa_composer   = 46 calls /    75,888 tokens
  other generation calls (query analyzer, semantic verification, coverage
  review, and other unlabeled generation): 137 calls / 1,260,974 tokens
  embedding calls       = 64 (embedding tokens not separately recorded)
evaluation judge   =  62 calls /   410,203 tokens
```

Zero scientific/evaluation calls were consumed producing this receipt.
