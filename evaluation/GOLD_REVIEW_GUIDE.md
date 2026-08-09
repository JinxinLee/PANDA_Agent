# M6 Gold Benchmark 人工审核指南

`gold_questions.yaml` 是基于锁定语料建立的 **120 题 Gold Benchmark**。120 题现已全部完成人工审核并标记为 `approved`。本文件同时规定 Gold 标注审核和完整 dev 运行失败后的结果审核；两者不要混淆。

## 1. 审核范围

每一道题必须人工确认：

1. `query` 与 `intent` 是否一致；
2. `expected_status` 是否应为 `answered`、`insufficient_evidence` 或 `version_conflict`；
3. `allowed_source_versions` 是否只包含锁定语料；
4. 每个 `required_evidence_groups[*].any_of` 是否至少有一个合法 Gold 证据；
5. `required_source_types` 是否符合问题需要；
6. `required_answer_points` 是否足以判定答案正确，又没有要求语料无法支持的结论；
7. `required_identifiers` 是否必须在最终答案中出现；
8. `forbidden_evidence` 与 `concept_scopes` 是否正确完成概念消歧。

> **关键规则：** “系统能检索到”不等于“标注正确”。审核者需要读取对应源码、PDF 页或 Sphinx 页面后再批准。

## 2. 审核状态

单题审核完成后修改：

```yaml
review_status: approved
reviewer: "reviewer-name"
reviewed_at: 2026-07-30T20:30:00+02:00
```

若题目或 rubric 有问题，使用：

```yaml
review_status: rejected
reviewer: "reviewer-name"
reviewed_at: 2026-07-30T20:30:00+02:00
```

修正 rejected 题后必须重新审核。不要只批量替换 `draft` 字符串；Pydantic 会要求 approved 题同时具有 reviewer 和 reviewed_at，但它无法代替领域审核。

## 3. 校验命令

在 `PANDA_Agent/` 下执行：

```powershell
# 结构、分布和 Gold selector 回读校验；draft 可以通过
panda-qa-eval validate

# 正式批准校验；只要还有 draft/rejected 就以 exit code 2 失败
panda-qa-eval validate --official
```

当前正式数据集的预期结果：

```text
question_count=120
structurally_valid=true
official_ready=true
review_counts={approved: 120}
unmatched_evidence_groups=[]
```

## 4. 审核后的执行顺序

只有 `validate --official` 成功后，才按以下顺序运行：

```powershell
panda-qa-eval run retrieval --split dev --run-id m6-retrieval-dev
panda-qa-eval run qa --split dev --run-id m6-qa-dev
```

开发集用于修复，不是发布门禁。冻结候选实现后运行不再用于调参的验收集：

```powershell
panda-qa-eval run retrieval --split acceptance --run-id m6-retrieval-acceptance
panda-qa-eval run qa --split acceptance --run-id m6-qa-acceptance
panda-qa-eval report --run-id m6-qa-acceptance
```

中断后使用：

```powershell
panda-qa-eval resume --run-id <RUN_ID>
```

每题写入一次 `results.jsonl`，恢复时跳过已完成 ID。manifest 与当前 corpus、index、model、Prompt、retrieval policy 或 Gold hash 不一致时，恢复会拒绝继续。

## 5. Draft 运行边界

CLI 提供显式 `--draft`，只用于审核者希望查看某题真实输出时的非正式诊断：

```powershell
panda-qa-eval run retrieval --split dev --run-id review-sample --draft --limit 1
```

任何 `--draft` 运行都会写入 `official=false`，质量门禁必定失败，不能据此宣布 M6 完成。

## 6. 当前门禁状态

- 结构校验：通过；
- 120 题分布：通过；
- Gold selector 对锁定 KnowledgeObject 回读：通过；
- Gold 人工审核：120/120 approved；
- Retrieval 开发门禁：通过；
- QA 开发门禁：`m6-qa-dev-candidate-v8` 已完成 80/80，但未通过；
- v8 人工结果审核：`failure_review.yaml` 已生成，17 个 case 等待逐项人工分类和处置；
- 正式验收集运行：未开始；
- M6 发布门禁：未通过；
- M7/M8：按计划保持未实施。

## 7. 完整开发集失败后的结果审核

Gold 审核回答“题目和 rubric 是否正确”；failure review 回答“本次模型输出与指标失败究竟是真实问题还是误判”。任何完整 80 题 dev 未通过后，都必须先生成结果审核表：

```powershell
panda-qa-eval review --run-id <RUN_ID>
```

产物：

- `failure_review.yaml`：canonical 人工填写表；
- `failure_review.md`：包含指标、模型 answer/claims 与支持 Evidence 的只读快照。

逐题检查模型输出和引用 Evidence 后，在 YAML 中填写：

```yaml
human_review:
  status: reviewed
  classification: metric_false_positive  # 或 real_failure / acceptable_exception
  action: rescore                         # 或 fix / waiver
  target_layer: evaluation                # retrieval / qa / infrastructure / gold
  rationale: "说明为什么是误判或真实问题，并引用 Evidence ID"
  reviewer: "reviewer-name"
  reviewed_at: 2026-08-02T12:00:00+02:00
  waiver_id: null                         # action=waiver 时必填
```

然后运行离线校验：

```powershell
panda-qa-eval review --run-id <RUN_ID> --check
```

只有校验通过后才能继续：

- `rescore`：只修改评估层并对已有 records 离线重算，不重新调用 Vertex；
- `fix`：只修改表中 `target_layer`，只运行受影响 case；
- `waiver`：必须有可追踪的 waiver ID，不能用来掩盖 citation、wrong-version、真实 unsupported claim、contradiction 或 exception。

> **Acceptance 例外：** acceptance 是冻结候选的最终测量，不能根据其逐题结果继续调参。Acceptance 失败只能归档或拒绝发布；若决定修改实现，必须创建新候选并重新走 dev 流程，旧 acceptance 不能作为调参集。
