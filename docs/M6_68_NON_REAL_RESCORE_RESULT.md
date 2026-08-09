# M6 evaluator-2.2：68 题非完整 dev 诊断 rescore 结果

## 结论

本轮完成 Gold v2.2 / evaluator-2.2 对现有 records 的 **68 题离线 diagnostic composite rescore**。它解决并关闭了 `g074`、`g079`、`g086` 三道评分误判，令 48 题统一人工审查表达到 **36 resolved、12 real failure pending**；它不是新的 candidate，也不是完整 M6/dev gate。

本次 rescore 没有调用 Vertex：新增 `0 model calls`、`0 tokens`。报告中的 `405 calls`、`4,126,750 tokens` 是原始 runtime/judge records 的历史用量，不能算成本新增。

## 输入与身份

| 项目 | 值 |
|---|---|
| Gold | `evaluation/benchmarks/v2_2/gold_questions.yaml` |
| Gold SHA-256 | `d65783d4712676af60a1d1b69f7a344d9898ae9c86914c7629c6daaffe4fe156` |
| evaluator | `evaluator-2.2` |
| immutable source run | `m6-v2-36-qa-dev-rc2b` |
| 输出目录 | `data/evaluation/rescores/m6-v2-36-qa-dev-rc2b-evaluator-2_2-d65783d47126-90547a6958bf/` |
| 输出文件 | `records.jsonl`, `report.json`, `rescore_manifest.json` |

所有原始 records 和 replacement records 都保持不可变；输出目录拒绝覆盖既有 rescore。

## 三题 v2.2 窄规则

`evaluation/benchmarks/v2_2/gold_v2_2_patch.yaml` 只作用于这三题：

- `g074`：接受 `data_flow` intent，required source 仅为 `code`；adapter 实现足以回答，论文与上游实现不是阻塞证据。
- `g079`：对 `Lumi_TrksQA` data-product group 使用已签署的直接代码等价 selector（PandaRoot `PndLmdTrackQ.cxx` 或 LuminosityFit `PndLmdCombinedDataReader.cxx`）。这是 g079 该 group 的显式等价，不是一般 graph-to-code heuristic。
- `g086`：`a/e/r/v` 代码语义以实现源码为 blocking source；生成 documentation 仅 optional/diagnostic。

三题的 intent、Gold recall、final evidence、required-source coverage、answer-point、citation 均 pass，且没有 wrong-version 或 major unsupported claim。原人工审查中的 `pending_offline_rescore`、`action: rescore` 和 required-change 文本仍保存在 [`evaluation/reviews/m6_integrated_48_review.yaml`](../evaluation/reviews/m6_integrated_48_review.yaml) 的历史字段中。

## Composite 选择与 replacement

68 题 = dev 80 排除 exact real failures：

`g023 g025 g039 g057 g060 g063 g073 g088 g089 g095 g110 g114`

replacement 只允许以下显式 case：

| replacement run | 采用 cases |
|---|---|
| `m6-v2-36-status-fix-31-retry1` | `g041`, `g119` |
| `m6-v2-36-synthetic-noise-fix-6-v1` | `g011`, `g074`, `g079`, `g085`, `g086` |

`g089` 没有 replacement，仍在待修复集合中。合成噪声 replacement 的 prompt hash 与 RC2b（prompt 3.0.1）不同；manifest 记录 `diagnostic_composite_runtime=true`、`uniform_candidate_identity=false`，所以不能把 68 题宣称为统一 candidate 运行。

## 结果

| 指标 | 结果 |
|---|---:|
| cases / scored cases | 68 / 68 |
| Gold recall@10 | 1.0 |
| final evidence recall | 1.0 |
| critical final evidence recall | 1.0 |
| required-source coverage | 1.0 |
| expected status accuracy | 1.0 |
| intent accuracy | 1.0 |
| citation integrity | 1.0 |
| answer-point coverage | 1.0 |
| paper/code dual-source | 1.0 |
| identifier hallucination | 0 |
| wrong-version / forbidden evidence | 0 / 0 |
| major unsupported / contradiction / unhandled exception | 0 / 0 / 0 |

透明保留的诊断差异：`refusal_evidence_recall=0.5`，分母 4，`g007` 与 `g041` 为 0；`g036` 保留一个 minor unsupported claim `claim_1`。这两项都不是 major gate failure。

`complete_v2_dev=false`，`development_gate.passed=false`，且唯一失败检查是 `complete_full_dev=false`。因此该 subset 不能通过完整 development gate、冻结候选、解锁 regression/challenge/acceptance 或 M7/M8。

## CLI 可重复方式

`rescore` 支持多个 replacement 和显式 subset；每个 replacement 必须列出非空、互不重叠的 case ID，且只能替换 source run 中已选 subset 的 case。`--include-case` 与 `--exclude-case` 可同时传入，但同一 case 不得同时出现于两者；`--exclude-case` 形成的子集也必须标记为 diagnostic only。

示意命令（本轮的选择身份）：

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.evaluate --project-root . rescore `
  --run-id m6-v2-36-qa-dev-rc2b `
  --dataset evaluation/benchmarks/v2_2/gold_questions.yaml `
  --review-decisions data/evaluation/runs/m6-v2-36-qa-dev-rc2b/failure_review_decisions.yaml `
  --replacement m6-v2-36-status-fix-31-retry1:g041,g119 `
  --replacement m6-v2-36-synthetic-noise-fix-6-v1:g011,g074,g079,g085,g086 `
  --exclude-case g023 --exclude-case g025 --exclude-case g039 `
  --exclude-case g057 --exclude-case g060 --exclude-case g063 `
  --exclude-case g073 --exclude-case g088 --exclude-case g089 `
  --exclude-case g095 --exclude-case g110 --exclude-case g114 `
  --adjudications evaluation/benchmarks/v2_1/manual_adjudications.yaml
```

该命令只读取既有 records、签署 review decisions、Gold 和 adjudications，不生成答案、不调用模型。`--replacement RUN_ID:CASE_ID[,CASE_ID]` 可重复；strict manifest identity mismatch、重复或缺失 case 会直接拒绝，不会写入成功 manifest。允许的 prompt mismatch 会写入 manifest，并使 composite 明确标为非 uniform candidate。

## 其他验证

- Gold v2.2 official validation：120/120 approved，unmatched evidence groups 为 0。
- Unit tests：85 passed。
- rescore manifest：`rescore_model_calls=0`、`rescore_token_usage=0`、`cases=68`、`subset_diagnostic_only=true`、`complete_development_gate_eligible=false`。

关键文件 hash：

| 文件 | SHA-256 |
|---|---|
| `rescore_manifest.json` | `38a0165c12977c4cf5c61949d0a9f30ed0a3d2a20f98ade921be048a933cb83b` |
| `report.json` | `451d5f30518abafdc764208f98f570f9778bace573ec78baf989fc62ca1471da` |
| `records.jsonl` | `d16890c050e5e94e23861c35662cfb96f79865a41afd63928b3a88ef674307db` |

后续只能按 48 题审查表修复 12 道 real failure，并为受影响 case 运行 focused test/sentinel；本报告不宣称 M6 完成。
