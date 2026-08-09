# M6 31 题评分修正结果

## 结论

本轮完成的是 **31 题诊断修正**，不是新的完整开发集验收，也不是 M6 release gate。处理方式严格分为：

- 29 题只做离线 evaluator/Gold/adjudication rescore；
- g041、g119 修改 Agent 的结构化状态后最小重跑；
- g031、g112 只作为防止过度拒答的 sentinel，不替换 RC2b 记录；
- 最终对完整 80 条统一离线重算，未重新调用 80 题生成、judge、embedding 或 retrieval。

6 道 `mixed_evaluation_and_answer_quality` 和 11 道 `real_failure` 本阶段保持未处理，不运行完整 dev、regression、challenge、acceptance、M7 或 M8。

## 输入身份

| 输入 | 身份 |
|---|---|
| 原始运行 | `m6-v2-36-qa-dev-rc2b` |
| 原始 source results SHA-256 | `bd1e601d2c01c76011b115ee3caab5bbf839e027867311f3d2db0ad00838af9d` |
| 人工审查 overlay SHA-256 | `2e7ee94257afa32620745b6e5f8f4ba1ae49f27b4827c3f2980ba4b21f699a97` |
| Gold | `m6-benchmark-v2.1` / `1fea656c1ea05ac2cf4bbb78e8e712fec3c09e40c31f5d77a914fa7cadbd9d22` |
| 最小替换运行 | `m6-v2-36-status-fix-31-retry1` |
| runtime source | `m6-v2-36-rc2b` |
| evaluation revision | `evaluator-2.1` |

用户提供的原始审查文件未被修改；RC2b 运行目录也未被覆盖。

## 代码修正

### Gold 与 selector

- 新增 `evaluation/benchmarks/v2_1/`、确定性构建器和变更报告。
- evidence matcher 按 `direct → ancestor → 同 source/version/path 的文件级 descendant containment` 匹配；跨来源等价只能来自 v2.1 显式 `any_of`。
- 一个 `any_of` group 最多计一次，并记录 match provenance。

### 指标适用性

- 正确 `version_conflict` 和 `insufficient_evidence` 的 ordinary recall、required identifier、dual-source 指标为 N/A，并在 aggregate 中报告真实分母。
- `insufficient_evidence` 使用 `refusal_evidence_recall`；错误拒答状态不获得豁免。
- locked identifier catalog 只收录题目允许的 source versions，且区分“identifier 存在”与“identifier 被 claim evidence 支持”。
- README/documentation 不再冒充 code。

### Agent 状态

- 精确请求不存在的 `Class::Method` 时返回 `insufficient_evidence`。
- 要求从源码恢复已删除 runtime artifact 时返回 `insufficient_evidence`，可保留已验证 schema 的部分帮助。
- g031、g112 保持 `answered`，用于防止 guard 过度拒答。

## 最小运行结果

首次尝试 `m6-v2-36-status-fix-31` 在指标落盘时发现 catalog 正则读取不存在的捕获组；该运行的 4 条记录均为确定性 `IndexError`，没有作为替换数据使用。修复后执行不可变重试 `m6-v2-36-status-fix-31-retry1`：

| case | 期望/实际 status | intent | citation | version/forbidden | identifier | critical points | major unsupported |
|---|---|---:|---:|---:|---:|---:|---:|
| g031 | answered / answered | 1.0 | 通过 | 0 | 0 | 通过 | 0 |
| g041 | insufficient / insufficient | 1.0 | 通过 | 0 | N/A | 通过 | 0 |
| g112 | answered / answered | 1.0 | 通过 | 0 | 0 | 通过 | 0 |
| g119 | insufficient / insufficient | 1.0 | 通过 | 0 | N/A | 通过 | 0 |

该运行共使用 26 次模型调用（runtime 22、judge 4），只覆盖 4 个 case；没有执行完整集合。

## 统一 80 题离线 rescore

输出目录：

`data/evaluation/rescores/m6-v2-36-qa-dev-rc2b-evaluator-2_1-1fea656c1ea0/`

| 检查 | 结果 |
|---|---:|
| cases rescored | 80 |
| 原始 78 条 result/diagnostics 保持不变 | 78/78 |
| replacement records | 仅 g041、g119 |
| rescore model calls | 0 |
| rescore token usage | 0 |
| citation integrity | 1.0 |
| wrong-version evidence | 0 |
| forbidden evidence | 0 |
| unhandled exceptions | 0 |

本次重算得到的诊断指标为：Gold Recall@10 `0.9831`（分母 69）、Final Evidence Recall `0.9167`（分母 69）、intent accuracy `0.975`、expected status accuracy `0.9625`、answer-point coverage `0.9552`。这些指标仍包含尚未处理的 mixed/real failures，因此 development gate 为 `passed=false`；本报告不把离线 rescore 结果宣布为 M6 通过。

逐条记录的字段来源写在 `rescore_provenance`：确定性字段为 `computed`，judge 保留字段为 `preserved_judge`，g005 的 answer-point 字段为 `human_adjudicated`。

## 可重复命令

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.evaluate --project-root . validate --official --dataset evaluation/benchmarks/v2_1/gold_questions.yaml
..\.venv\Scripts\python.exe -m panda_agent.cli.evaluate --project-root . rescore `
  --run-id m6-v2-36-qa-dev-rc2b `
  --dataset evaluation/benchmarks/v2_1/gold_questions.yaml `
  --review-decisions data/evaluation/runs/m6-v2-36-qa-dev-rc2b/failure_review_decisions.yaml `
  --replacement-run m6-v2-36-status-fix-31-retry1 `
  --adjudications evaluation/benchmarks/v2_1/manual_adjudications.yaml
```

rescore 输出目录不可覆盖；重复执行会创建冲突并停止，而不是修改既有结果。

## 下一步边界

下一阶段若处理 mixed/real failures，必须先人工审查对应 case，再按受影响层做 focused run。除非代码、Prompt、模型、Gold、policy 和 index 全部冻结，否则不得重新运行完整 dev；不得用 acceptance 结果做针对性调参。

