# Benchmark v2 人工审核状态

120 道题已于 `2026-08-02T19:49:00+02:00` 完成人工审核并全部批准。

- 正式开发基准：`gold_questions.yaml`
- 数据集 SHA-256：`f58ab7f55717aaa5b6205403dfcc78533b941e7fa2d082051848990a21c0af9d`
- Reviewer：`OpenAI GPT-5.6 Thinking`
- Split：80 dev / 24 challenge / 16 regression
- Status：102 answered / 10 insufficient_evidence / 8 version_conflict
- 范围：已暴露的开发、挑战和回归集合
- Release eligibility：`false`
- Hidden acceptance：尚未创建

完整逐题审核记录见 `review/review_report.md`。原始 draft 和审核队列分别归档为
`review/pre_review_draft.yaml` 与 `review/annotation_review_queue_draft.md`。

> 注意：签署包的 selector 宽度与当前项目 `audit_dataset()` 的统计口径存在差异，且审核后
> selector 会改变当前启发式重聚类结果。详情见 `review/local_import_validation.md`。这不影响
> schema、已声明 cluster 隔离和项目 `validate --official` 的通过状态，但必须在候选冻结前处理或
> 正式接受该审计口径。
