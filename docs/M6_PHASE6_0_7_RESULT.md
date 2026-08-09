# M6 Phase 6.0–6.7 实际运行结果

## 2026-08-03：runtime 恢复 3.6 的焦点验证

- runtime generation 已从 Lite 恢复为 `gemini-3.6-flash`；judge 独立保持 `gemini-3.6-flash`，embedding 保持 `gemini-embedding-2`。
- 12 道 dev 焦点题已通过指定焦点门禁。首轮只对 4 个失败题进行修复，之后只重跑失败题及直接哨兵；没有重复运行完整 80 题 dev。
- `g098` regression sentinel 单独通过，Recall@10 与 Final Evidence Recall 均为 `1.0`。
- 相关运行目录：`m6-v2-36-focused-rc2`、`m6-v2-36-focused-fixes-rc2`、`m6-v2-36-focused-g001-rc2b`、`m6-v2-36-focused-regression-rc2`。
- 随后冻结并验证 candidate `m6-v2-36-rc2b`，manifest SHA 为 `a3810966dd1a9347033005f2f83e8142f84b2ab57d50d3252a8e005e83a661d9`。
- 完整 80 题 dev 已运行完成，但 development gate 未通过；因此没有运行 16 题 regression、challenge 或 acceptance。下方 Lite RC1 结果保留为历史记录。

## 最终状态

```text
phase_6_7_complete=false
development_gate_passed=false
regression_gate_passed=false
acceptance_status=not_created
challenge_run=false
m7_unlocked=false
```

本次执行已完成环境门禁、模型迁移焦点回归、候选冻结和唯一一次完整 80 题 dev。由于 development gate 未通过，按运行契约停止；没有运行 16 题 regression、24 题 challenge、hidden acceptance、M7 或 M8。

## 环境门禁

| 检查 | 结果 |
|---|---|
| Docker Engine | 通过，Docker Server 29.3.1 |
| Docker Compose | 通过，PostgreSQL/Qdrant healthy |
| 固定语料 | 通过，corpus locked |
| PostgreSQL/Qdrant index | 通过，80,698 points，missing/stale 0 |
| Gold v2 official | 通过，120/120 approved，SHA `f58ab7f55717aaa5b6205403dfcc78533b941e7fa2d082051848990a21c0af9d` |
| runtime health | 通过，`gemini-3.6-flash` |
| judge health | 通过，`gemini-3.6-flash` |
| query/document embedding | 通过，`gemini-embedding-2`，3072 维 |
| deterministic unit tests | 通过，75/75 |
| `pip check` / compileall | 通过 |

Docker 与 Vertex 采用已批准的非沙箱执行上下文；没有重新认证、复制 ADC 或修改 ACL。

## 焦点回归与候选

- 12 道 3.6 runtime dev 焦点题在定向修复后全部通过；`g098` 单题 regression sentinel 通过。
- 当前 candidate `m6-v2-36-rc2b` 已冻结并验证：manifest SHA `a3810966dd1a9347033005f2f83e8142f84b2ab57d50d3252a8e005e83a661d9`，`mismatches=[]`。
- 冻结后没有修改源码、Prompt、模型、参数、检索策略、语料、Gold 或评估器。

## 当前 3.6 完整 dev 运行

运行目录：`data/evaluation/runs/m6-v2-36-qa-dev-rc2b/`

| 项目 | 实际结果 |
|---|---:|
| 完成题数 | 80/80 |
| Runtime model calls | 403 |
| Judge model calls | 80 |
| Total model calls | 483 |
| Runtime tokens | 4,526,752 |
| Judge tokens | 527,893 |
| Total tokens | 5,054,645 |
| 平均延迟 | 41,224.3 ms |
| P95 延迟 | 65,983.9 ms |

关键指标：

| 指标 | 实际 | 门禁 |
|---|---:|---:|
| Gold Recall@10 | 84.38% | ≥95% |
| Final Evidence Recall | 73.94% | ≥90% |
| Answer-point coverage | 94.27% | ≥90% |
| Expected status accuracy | 93.75% | ≥97.5% |
| Intent accuracy | 95.0% | ≥90% |
| Required-source coverage | 85.92% | ≥97% |
| Citation integrity | 100% | 100% |
| Wrong-version evidence | 0 | 0 |
| Forbidden evidence | 0 | 0 |
| Identifier hallucination rate | 0.823% | <3% |
| Critical answer-point misses | 8 | 0 |
| Major unsupported claims | 0 | 0 |
| Minor unsupported claims | 5 | 0 |
| Contradictions | 0 | 0 |
| Unhandled exceptions | 0 | 0 |

Development gate 文件：`data/evaluation/runs/m6-v2-36-qa-dev-rc2b/development_gate.json`，`passed=false`。

## 失败审查门禁

当前 3.6 运行器已生成/保留：

- `data/evaluation/runs/m6-v2-36-qa-dev-rc2b/failure_review.yaml`
- `data/evaluation/runs/m6-v2-36-qa-dev-rc2b/failure_review.md`

共有 48 道题需要人工审查。审查完成前不得修复、rescore、waive 或运行下一阶段。建议优先按影响层分组：

1. retrieval：Gold/Final evidence recall、required source coverage 和 identifier missing；
2. QA：错误拒答、答案点覆盖、unsupported/contradiction；
3. evaluator：仅在人工证据确认 judge 误判时离线 rescore。

当前结果表明，Lite 运行链的主要瓶颈是检索证据虽被召回，但未稳定进入最终答案，以及部分拒答/答案点判断不一致。它不是 Docker、ADC 或数据库故障。

当前 3.6 运行的主要瓶颈仍是最终证据选择和来源覆盖：Gold Recall@10 为 84.38%，但 Final Evidence Recall 只有 73.94%，required-source coverage 为 85.92%；另有 8 个 critical answer-point misses、2 个 identifier misses 和 4 个 major identifier hallucination。它不是 Docker、ADC、数据库或索引故障。

## 历史 Lite RC1 完整 dev 运行

历史运行目录：`data/evaluation/runs/m6-v2-lite-qa-dev-rc1/`。该段保留 Lite RC1 的原始指标，不作为当前 3.6 candidate 结果。

## 后续允许动作

只能在人工审查表全部完成并通过 `panda-qa-eval review --check` 后，根据 `rescore`、`fix` 或正式 `waiver` 决定下一步：

- evaluator 误判：只离线 rescore，不调用 Vertex；
- retrieval/QA 真实失败：候选失效，修复后只运行受影响题和 sentinel；
- 新候选通过焦点回归后，才允许再次冻结并重新运行一次完整 80 题 dev；
- dev 通过后才允许运行完整 16 题 regression。

禁止运行 challenge、hidden acceptance 或 M7。
