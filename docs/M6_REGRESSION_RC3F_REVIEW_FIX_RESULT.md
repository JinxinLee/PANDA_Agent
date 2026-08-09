# M6 RC3f Regression 人工审查修复结果

**日期：** 2026-08-09  
**运行模型：** runtime `gemini-3.6-flash`；judge `gemini-3.6-flash`；embedding `gemini-embedding-2`  
**范围：** 已暴露的 16 题 regression；不包含 challenge、hidden acceptance、M7 或 M8。

## 1. 人工审查输入

- 审核 YAML：`D:/Download/failure_review_regression_rc3f_14_reviewed_v2.yaml`
- SHA-256：`5a42e46cce0e7ab3e0e84daf11b5f664df3266206a7797fbdf158e93b7d59b43`
- 审核报告：`D:/Download/failure_review_regression_rc3f_14_final_report_v2.md`
- SHA-256：`bd5b2862ffd619a4555921717c0081996258a06d24913a4e8a443cb3fe86aa22`
- canonical overlay：`data/evaluation/runs/m6-v2-36-qa-regression-rc3f/failure_review_decisions.yaml`

14 个受审查案例被规范化为：10 个离线 `rescore`、1 个正式 `waiver`、3 个真实 `fix`。原始 run 与用户附件均保持不可变。

## 2. 实施内容

### 2.1 Case-local Gold 与 scorer 修正

当前默认 Gold 为 `evaluation/benchmarks/v2_6/gold_questions.yaml`：

- 120/120 approved；
- dev/challenge/regression 分布仍为 80/24/16；
- SHA-256：`b5406e36c64ee664f9e2ff9c0f42e354feb7164c81d8f1c7551d8f2ed1d0b687`；
- official validation：无 unmatched evidence group，无 unknown source version。

审查授权的窄修正包括：

- `g093`：code 为 blocking source；
- `g101`：删除与问题无关的可见版本治理样板；
- `g106`：以功能/架构责任边界替代泛化版本声明；
- `g087`：保留严格 pointer-normalization 行为，但不再要求重复的 synthetic graph 对象；
- `g116`：允许锁定 PandaRoot 中同路径 Apollonius 实现作为显式等价 selector；
- 其余评分误判仅使用签署、逐题、fail-closed adjudication；
- `g109` 使用正式 waiver `rc3f-g109-relative-path-shorthand`。

evaluator `2.6.1` 还将 16 题 regression composite 与 80 题 development gate 分开报告，避免把完整 regression 错写成“不完整 dev”。

### 2.2 三个真实行为修复

`src/panda_agent/qa.py` 增加三个窄范围 completeness requirement：

- `pointer_identifier_normalization`：明确 `PndLmdTrackQ* -> PndLmdTrackQ`，`*` 是类型语法而不是新 identifier；
- `model_layer_component_inventory`：model layer 必须覆盖 DPM/physics、acceptance、resolution/divergence smearing 与 factory；
- `implementation_disambiguation_procedure`：必须核验 source/repository/full path、锁定 revision（相关时）、implementation、callers/configuration sites 与 consumed/produced data products。

这些规则由问题语义触发，没有修改 dense/sparse/exact/workflow/graph retrieval、fusion、rerank、模型参数或 embedding 配置。

## 3. Focused run

运行目录：

```text
data/evaluation/runs/m6-v2-36-qa-regression-fix-rc3g/
```

只运行 `g087/g097/g116` 与同 split sentinel `g098/g111`。没有重跑完整 16 题。

| Case | 作用 | Status | Gold@10 | Final evidence | Source coverage | Answer points | Critical miss | Citation | Major unsupported |
|---|---|---|---:|---:|---|---:|---:|---|---:|
| g087 | pointer normalization fix | answered | 1.0 | 1.0 | pass | 1.0 | 0 | pass | 0 |
| g097 | model-layer acceptance fix | answered | 1.0 | 1.0 | pass | 1.0 | 0 | pass | 0 |
| g098 | module/data-flow sentinel | answered | 1.0 | 1.0 | pass | 1.0 | 0 | pass | 0 |
| g111 | troubleshooting sentinel | answered | 1.0 | 1.0 | pass | 1.0 | 0 | pass | 0 |
| g116 | implementation disambiguation fix | answered | 1.0 | 1.0 | pass | 1.0 | 0 | pass | 0 |

Focused run 实际消耗 38 次模型调用、630,251 tokens。两项 selector 修正后的指标通过离线 rescore 得到，新增模型调用和 token 均为 0。

## 4. 16 题 reviewed composite

原始 16 题 run 的 13 个已接受结果与 focused run 的 `g087/g097/g116` 合成后，统一使用 Gold v2.6、evaluator 2.6.1 和签署审查重新计算：

```text
data/evaluation/rescores/
  m6-v2-36-qa-regression-rc3f-evaluator-2_6_1-
  b5406e36c64e-32a7c69dc725-298e311a6dd7/
```

结果：

| 指标 | 结果 |
|---|---:|
| Cases | 16/16 |
| Gold Recall@10 | 1.0 |
| Final Evidence Recall | 1.0 |
| Critical Final Evidence Recall | 1.0 |
| Required-source coverage | 1.0 |
| Intent accuracy | 1.0 |
| Expected-status accuracy | 1.0 |
| Answer-point coverage | 1.0 |
| Citation integrity | 1.0 |
| Identifier hallucination rate | 0.0 |
| Critical answer-point misses | 0 |
| Wrong-version / forbidden evidence | 0 / 0 |
| Major unsupported / contradiction | 0 / 0 |
| Unhandled exceptions | 0 |
| Rescore model calls / tokens | 0 / 0 |

`diagnostic_quality_checks.passed=true`，且使用真实的 regression contract。

> **边界：** 该 16 题结果混合了原始 run 与 3 个 focused replacement，因此是 reviewed diagnostic composite，不是单一冻结 candidate 的统一运行身份。`regression_gate.passed=false` 仅由 `complete_full_regression=false`（混合 provenance）造成，不是质量指标失败。若未来发布流程要求 formal frozen-candidate regression gate，仍需在源码、Prompt、模型和 evaluator 冻结后统一重跑 16 题。

## 5. 验证

- deterministic unit tests：118/118 通过（新增 split-aware test 后相关模块 38/38 通过）；
- `compileall -q src tests`：通过；
- `pip check`：通过；
- Gold v2.6 official validation：120/120，0 unmatched selector group；
- 14 题原始离线检查：10 rescore + 1 waiver 通过，3 real failure 未被 adjudication 隐藏；
- focused 5 题：全部通过；
- composite 16 题：全部质量门禁通过；
- 未运行完整 16 题、challenge、acceptance、M7 或 M8。

