# Local import validation

Validation performed against the current locked corpus and current project code on 2026-08-02.

## Passed checks

- `panda-qa-eval validate --official`: passed.
- Dataset SHA-256: `f58ab7f55717aaa5b6205403dfcc78533b941e7fa2d082051848990a21c0af9d`.
- Questions: 120; all `review_status=approved` with reviewer and timestamp.
- Declared split counts: 80 dev / 24 challenge / 16 regression.
- Expected statuses: 102 answered / 10 insufficient evidence / 8 version conflict.
- IDs, split, declared cluster ID, language, intent, expected status and allowed source versions are unchanged from the pre-review draft.
- Only `g087` changed query text; evidence selectors, roles and answer rubrics contain the larger reviewed edits.
- No unknown allowed source version and no unmatched evidence group.
- Declared cluster IDs do not cross splits.

## Differences from the submitted validation reports

1. The submitted strict report states that all selectors match at most 20 knowledge objects. The current
   `panda_agent.benchmark_v2.audit_dataset()` implementation counts 25 matches for `g023.e1` and 23 for
   `g010.e1`. Its matching semantics count every matching normalized KnowledgeObject, including page and
   subsection chunks whose searchable content contains the requested title.
2. The declared cluster IDs remain split-disjoint and therefore pass the dataset schema. However, calling
   the current heuristic `cluster_questions()` again after the reviewed selector changes merges two groups
   across splits: `g031/g065/g078/g088/g102/g105` and
   `g036/g070/g077/g081/g082/g090/g095/g110/g119`.
3. The submitted README lists `review_and_patch_benchmark.py`, `validate_reviewed_benchmark.py`, and
   `validate_reviewed_benchmark_strict.py`; those scripts were not part of the five supplied files, so their
   exact counting semantics cannot currently be reproduced from the handoff.

These are recorded as audit warnings rather than silent corrections. The signed YAML is imported byte for
byte and has not been changed. It is valid for exposed development/challenge/regression work, but it remains
ineligible for hidden acceptance. Before freezing a release candidate, either align the local and submitted
selector-counting/cluster-recomputation semantics or explicitly approve the declared-cluster interpretation.
