# M6 benchmark v2 — P0/P1 reviewed package

This package contains the completed review of all 120 benchmark questions against the locked corpus.

## Primary artifact

- `gold_questions_v2_p0_p1_reviewed.yaml`: reviewed replacement YAML.

## Review outputs

- `benchmark_v2_p0_p1_review_report.md`: per-question approval and change summary.
- `benchmark_v2_validation.txt`: selector/split/status validation.
- `benchmark_v2_strict_validation.txt`: strict structural and corpus-match validation.

## Reproducibility

- `review_and_patch_benchmark.py`: transformation script from the supplied draft.
- `validate_reviewed_benchmark.py`: base validator.
- `validate_reviewed_benchmark_strict.py`: strict validator.

## Validation result

- Questions approved: 120/120
- Split counts preserved: dev 80, challenge 24, regression 16
- Status counts preserved: answered 102, insufficient_evidence 10, version_conflict 8
- Selectors with no corpus match: 0
- Selectors matching more than 20 knowledge objects: 0
- Generic evidence roles remaining: 0
- Required-source-type mismatches: 0
- Multi-point questions after rubric atomization: 74

`release_eligible` remains `false` because this is an exposed dev/challenge/regression suite, not a hidden final acceptance set. It no longer indicates unfinished P0/P1 annotation work.
