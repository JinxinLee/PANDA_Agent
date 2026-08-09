# M6 Phase 1–5 实施记录

> 日期：2026-08-02  
> 历史来源：`m6-qa-dev-candidate-v8` 及其 17 项人工失败审查  
> 当前结论：Phase 1–5 已实施；Phase 4 的 v2 已于 2026-08-02 完成 120/120 人工批准并导入。它是暴露的开发基准，不是 hidden acceptance。

## 1. 人工审查结论

17 个案例中，13 个属于 evaluation/Gold 误判，处理为 `rescore`；4 个是真实失败：`g013`、`g027`、`g098`、`g112`；没有 waiver。

签署决定已导入 `data/evaluation/runs/m6-qa-dev-candidate-v8/failure_review_decisions.yaml`。导入不会覆盖生成时的 `failure_review.yaml`，因此原始失败快照与人工决定可以独立审计。

## 2. Phase 2：Gold Schema v2

实现位置：`src/panda_agent/evaluation.py`、`src/panda_agent/benchmark_v2.py` 和 `evaluation/benchmarks/v2/gold_questions.yaml`。

主要变化：

1. Evidence selector 支持源码行范围、PDF 页范围、title/section 范围。
2. Evidence group 增加 `role` 与 `critical`。
3. Answer point 增加稳定 ID、权重与 critical 标记。
4. identifier 区分 code symbol、path、glob、type expression、ROOT branch、shell pattern 和 regex；glob、指针类型和正则不再被当作主要 API 幻觉。
5. 正确拒答的 final evidence/source coverage 记为 N/A，而不是 0。
6. 4 个真实失败案例的题面、原子 answer points 和证据要求按人工决定修正。

旧 v1 已归档到 `evaluation/benchmarks/v1/`。它曾暴露给开发过程，不能继续充当 blind acceptance。

## 3. Phase 3：Evaluator v2 与离线重评分

新增命令：

```powershell
panda-qa-eval build-v2
panda-qa-eval audit --dataset evaluation/benchmarks/v2/gold_questions.yaml
panda-qa-eval rescore --run-id m6-qa-dev-candidate-v8 `
  --dataset evaluation/benchmarks/v2/gold_questions.yaml `
  --overrides evaluation/benchmarks/v2/manual_rescore_overrides.yaml
```

离线 rescore 只读取原始 `results.jsonl` 和签署纠偏，模型调用数为 0。旧运行的 case 集不等于新 v2 dev 时，必须保持 `complete_v2_dev=false`。

Judge Evidence 不再机械截取文件前 2,500 字符；`_claim_relevant_evidence_excerpt()` 会保留 claim identifier 周边窗口，解决长源码后半段证据被裁掉造成的误判。

## 4. Phase 4：重新分区与 acceptance 隔离

当前 v2 将已暴露的 120 题按知识簇整体分区：

| Split | 数量 | 用途 |
|---|---:|---|
| dev | 80 | 开发与候选冻结前验证 |
| challenge | 24 | 已暴露挑战题，只用于开发诊断 |
| regression | 16 | 已暴露回归题 |

声明分区共使用 76 个知识簇，声明的同簇问题不跨 split。v2 当前 `release_eligible=false`、`acceptance_exposed=true`，120 题全部为 approved，新 blind acceptance 为 `not_created`。

签署数据集 SHA-256 为 `f58ab7f55717aaa5b6205403dfcc78533b941e7fa2d082051848990a21c0af9d`；逐题报告归档于 `evaluation/benchmarks/v2/review/review_report.md`。项目 `validate --official` 已通过。签署报告与当前本地 audit 在 selector 最大匹配数和审核后启发式重聚类方面存在统计口径差异，详见 `evaluation/benchmarks/v2/review/local_import_validation.md`；冻结候选前不能忽略该记录。

## 5. Phase 5：QA 行为修复

实现位置：`src/panda_agent/qa.py` 和 `src/panda_agent/prompts.py`（`PROMPT_SET_VERSION=3.0.1`）。

1. verifier 记录每个 claim 的错误和 supported/unsupported 集合。
2. revision 只接收 unsupported 子集，已验证 claims 不被重写或删除。
3. 第二次验证仍有局部错误时可输出已支持子集；版本冲突或完全无证据仍严格拒答。
4. 最终 Evidence 仅保留最终 claims 实际引用的对象。
5. locator 自动补全仅在用户明确询问位置且写出 locator 时生效，最多补一个。
6. diagnostics 增加 `initial_retrieval_count`、`targeted_retrieval_count` 和 `selected_evidence_count`。
7. Prompt 明确 run-task lifecycle、双仓库版本边界、data product → adapter → model factory 三层职责。

## 6. 定向验证结果

没有运行完整 80 题，也没有运行任何 acceptance。

- `test_qa.py`：7/7 通过；
- `test_m6_evaluation.py`：18/18 通过；
- Python 静态编译通过；
- v2 结构校验：120 题、无 unmatched evidence group、`official_ready=false`（预期）；
- 5 题 retrieval focus 后，只对受影响 case 做逐层 QA 重跑。

最终离线重算结果：

| Case | Recall@10 | Final recall | Source coverage | Answer points | Major unsupported |
|---|---:|---:|---:|---:|---:|
| g013 | 1.0 | 1.0 | 1.0 | 1.0 | 0 |
| g027 | 1.0 | 1.0 | 1.0 | 1.0 | 0 |
| g098 | 1.0 | 1.0 | 1.0 | 1.0 | 0 |
| g112 | 1.0 | 1.0 | 1.0 | 1.0 | 0 |

## 7. 下一步门禁

1. 人工复审并签署 v2 的全部 120 题；
2. 批准后冻结代码、Prompt 3.0.1、模型配置、retrieval policy、index identity 和 dataset hash；
3. 焦点回归无失败后，才允许一次完整 80 题 dev；
4. dev 通过后，独立创建并批准新的 blind acceptance；
5. acceptance 只能在完全冻结后运行一次，结果不得用于针对性调参。
