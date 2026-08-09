# M6 48 题统一人工审查表：evaluator-2.2 当前状态

## 1. 范围与结论

本表保留原 RC2b 的 48 个失败 case 人工审查历史，并记录 Gold v2.2 / evaluator-2.2 对其中 3 道评分误判的完成处理。当前状态：

| 当前状态 | 数量 | Case |
|---|---:|---|
| 已解决的评分误判 | 34 | 原 31 道 evaluator-2.1 修正 + `g074/g079/g086` evaluator-2.2/pass |
| Clean PASS | 2 | `g011`, `g085` |
| 待修复并焦点重跑 | 12 | `g023`, `g025`, `g039`, `g057`, `g060`, `g063`, `g073`, `g088`, `g089`, `g095`, `g110`, `g114` |
| **合计** | **48** | — |

因此共有 **36 道 resolved、12 道真实失败 pending**。完整 development gate 仍未通过；本诊断不授权 regression、challenge、acceptance、M7 或 M8，也不把 composite 结果当作冻结 candidate。

Gold v2.2 为 [`evaluation/benchmarks/v2_2/gold_questions.yaml`](../../evaluation/benchmarks/v2_2/gold_questions.yaml)，SHA-256 为 `d65783d4712676af60a1d1b69f7a344d9898ae9c86914c7629c6daaffe4fe156`。权威结构化审查表为 [`m6_integrated_48_review.yaml`](./m6_integrated_48_review.yaml)。

## 2. 原审查历史（保留）

- 原 31 道评分误判仍按 Gold v2.1 / evaluator-2.1 记录在 YAML 的 `previously_corrected_scoring_cases`；其 rescore 目录未被覆盖。
- 六道 mixed 的行为焦点运行仍由 `data/evaluation/runs/m6-v2-36-synthetic-noise-fix-6-v1/` 记录；`g011/g085` 从该轮起即为 clean PASS。
- 原 11 道 real failure 加 `g089` 仍是待修复集合；`g089` 没有被任何 replacement run 替换。
- `g074/g079/g086` 的原始人工结论、`pending_offline_rescore` 状态和原 `required_change` 保留在 YAML 对应条目中；本表只追加 `prior_status/prior_action` 与 evaluator-2.2 结果。

## 3. evaluator-2.2 三题窄修正

Gold patch [`evaluation/benchmarks/v2_2/gold_v2_2_patch.yaml`](../../evaluation/benchmarks/v2_2/gold_v2_2_patch.yaml) 只改以下三题，不改变 query、source-version allowlist、split 或 cluster ID：

| Case | v2.2 规则（仅限该题） | Rescore 结果 |
|---|---|---|
| `g074` | 允许 `data_flow` intent；`required_source_types` 仅为 `code`。adapter 实现源码足以回答；论文和上游 `PndLmdTrackQ` 仅作上下文，不是阻塞证据。 | intent / Gold recall / final evidence / source / answer points / citation 全部 pass；wrong-version=0、major unsupported=0 |
| `g079` | `Lumi_TrksQA` data-product group 允许**已签署的直接代码等价证据**：`pandaroot@18c09e.../detectors/lmd/LmdQA/PndLmdTrackQ.cxx` 或 `luminosityfit@ddd83d.../data/PndLmdCombinedDataReader.cxx`。这是该 group 的显式例外，不是一般 graph-to-code heuristic。 | intent / Gold recall / final evidence / source / answer points / citation 全部 pass；wrong-version=0、major unsupported=0 |
| `g086` | `a/e/r/v` 语义题的实现源码为 blocking source；生成 documentation group 改为 optional/diagnostic，不要求文档作为阻塞证据。 | intent / Gold recall / final evidence / source / answer points / citation 全部 pass；wrong-version=0、major unsupported=0 |

三题均已从 `pending_offline_rescore` 更新为 `resolved`、`action: offline_rescore`、`resolution: scorer_v2.2_pass`。YAML 保留每题原始人工结论和原 required change，便于追溯。

## 4. 68 题零模型调用 diagnostic composite rescore

输出目录为 `data/evaluation/rescores/m6-v2-36-qa-dev-rc2b-evaluator-2_2-d65783d47126-90547a6958bf/`，包含不可覆盖的 `records.jsonl`、`report.json` 和 `rescore_manifest.json`。它从 dev 80 中排除以下 12 道 exact real failures：

`g023 g025 g039 g057 g060 g063 g073 g088 g089 g095 g110 g114`

替换 records 仅来自：

- `m6-v2-36-status-fix-31-retry1`：`g041`, `g119`；
- `m6-v2-36-synthetic-noise-fix-6-v1`：`g011`, `g074`, `g079`, `g085`, `g086`；
- **不得**使用 `g089` replacement。

合成噪声运行的 prompt hash 与 RC2b（prompt 3.0.1）不同；manifest 明确记录 `diagnostic_composite_runtime=true`、`uniform_candidate_identity=false`。因此这是跨记录的诊断 composite，不是统一 candidate 的新运行。

### Aggregate 指标

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
| identifier hallucination | 0（199 mentions） |
| wrong-version / forbidden evidence | 0 / 0 |
| major unsupported / contradiction / unhandled exception | 0 / 0 / 0 |

保留两项诊断细节：`refusal_evidence_recall=0.5`（分母 4，`g007` 与 `g041` 为 0）；`g036` 保留一个 minor unsupported claim `claim_1`。二者都不是 major gate failure，不能从表中隐去。

本次 rescore 新增 **0 calls / 0 tokens**。报告中的历史记录用量 `model_calls=405`、`token_usage=4,126,750` 属于原始 runtime/judge records，不能表述为本次 rescore 新增成本。

`complete_v2_dev=false` 且 `development_gate.passed=false`，唯一阻断检查是 `complete_full_dev=false`；68 题 subset 只能作诊断，不能通过完整 dev gate、冻结 candidate 或解锁后续阶段。

## 5. 仍待修复的 12 道真实失败

| Case | 缺失内容 | 处理边界 |
|---|---|---|
| `g023` | 明确 reconstruction 位于 digitization 之后、PID 之前 | fix + focused rerun |
| `g025` | 对未来 `runLmdFit` 输出 SHA-256 明确拒答 | fix + focused rerun |
| `g039` | 区分 longitudinal restgas efficiency 与 angular `PndLmdAcceptance` | fix + focused rerun |
| `g057` | 收敛结论限制到已测试 profile，禁止推广到所有 profile | fix + focused rerun |
| `g060` | 说明 `PndLmdModelFactory` 如何组合 divergence smearing | fix + focused rerun |
| `g063` | 说明 acceptance 如何进入 `PndLmdModelFactory` 和最终模型 | fix + focused rerun |
| `g073` | 明确 `PndLmdModelFactory` 消费 `PndLmdAcceptance` | fix + focused rerun |
| `g088` | 解释 acceptance 实际用途并移除无关 filler | fix + focused rerun |
| `g089` | 补充 `ReadDensityFile()` → 内部 profile、`SampleInteractionVertex()` → 交互顶点采样及 primary event handoff | fix + focused rerun；无 replacement |
| `g095` | 对未来 `event_poca` checksum 明确拒答 | fix + focused rerun |
| `g110` | 检查 `ana_dpm.C` 上游 first-pass PID 输入、prefix 和 path | fix + focused rerun |
| `g114` | 修正前检查 histogram binning 与 profile 范围兼容性 | fix + focused rerun |

## 6. 验证与后续边界

- v2.2 Gold 官方验证：120/120 approved，unmatched evidence groups 为 0。
- 当前 unit test 计数：85 passed。
- 只允许继续修复上述 12 道 real failure 的受影响层，并运行对应 case 与直接 deterministic sentinel。
- 只有新 candidate 的代码、Prompt、模型、policy、Gold、index 身份全部冻结后，才可考虑一次完整 80 题 dev；本 composite 不满足冻结条件。

## 7. 关键溯源

| 产物 | SHA-256 |
|---|---|
| `evaluation/benchmarks/v2_2/gold_questions.yaml` | `d65783d4712676af60a1d1b69f7a344d9898ae9c86914c7629c6daaffe4fe156` |
| `evaluation/benchmarks/v2_2/gold_v2_2_patch.yaml` | `43cce7dc579df7308f9842b1ddb2bc9d53f98aa8d87cb6a4fe21cf0c51386ed0` |
| `...evaluator-2_2.../rescore_manifest.json` | `38a0165c12977c4cf5c61949d0a9f30ed0a3d2a20f98ade921be048a933cb83b` |
| `...evaluator-2_2.../report.json` | `451d5f30518abafdc764208f98f570f9778bace573ec78baf989fc62ca1471da` |
| `...evaluator-2_2.../records.jsonl` | `d16890c050e5e94e23861c35662cfb96f79865a41afd63928b3a88ef674307db` |
| 原 RC2b `results.jsonl` | `bd1e601d2c01c76011b115ee3caab5bbf839e027867311f3d2db0ad00838af9d` |

本表和 YAML 只更新审查状态与诊断说明，不修改原始 run records、replacement records 或既有 rescore 输出。
