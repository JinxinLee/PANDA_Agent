# M6 六道 mixed claim-noise 修复结果

## 1. 范围与结论

本报告覆盖 `g011`、`g074`、`g079`、`g085`、`g086`、`g089` 的用户可见答案噪声修复。唯一焦点运行目录为：

```text
data/evaluation/runs/m6-v2-36-synthetic-noise-fix-6-v1/
```

6/6 为 `answered`。六题的 `answer` 和公开 `claims` 中，以下内部标记均为 0：

```text
scope_*
required_workflow
required_code
dataflow_locator_*
curated_panda_domain
```

这证明的是用户可见边界修复，不是完整 80 题开发门禁、candidate 冻结或 M6 正式通过。

## 2. 问题与根因

六题核心答案正确，但末尾出现了无关的来源作用域声明、workflow/code 定位器或 `curated_panda_domain` metadata。根因已由运行记录和源码确认：

1. `src/panda_agent/qa.py::_answer` 曾按 `resolved_versions` 追加 `scope_*`，把可用版本白名单接近成了逐库外显说明。
2. `_augment_required_dataflow_evidence` 曾追加 `required_workflow`、`required_code` 和 `dataflow_locator_*`。
3. 旧 verifier 只检查 evidence support，不检查 claim 是否回答问题；因此“有证据但无关”的句子被渲染。

故障链为：

```text
额外来源被选中 → synthetic claim 被追加 → 只检查 factual support
→ supported claim 被 finalizer 渲染 → 内部 metadata 泄漏
```

## 3. 修复内容

涉及实现：`src/panda_agent/qa.py`、`src/panda_agent/prompts.py`。

- `scope_*`、`required_workflow`、`required_code`、`dataflow_locator_*` 和包含 `curated_panda_domain` 的文本只进入内部 `claim_audit`，不进入 `QAResult.answer/claims`。
- `ANSWER_SCHEMA` 强制每个用户 claim 携带运行时 `answer_point_ids: ["question_core"]`；缺失、为空或非法映射的 claim 不渲染。
- Evidence review 增加 `irrelevant_claim_ids`；支持不等于相关，标记为 irrelevant 的 claim 被过滤。
- `_finalize` 在公开 `ClaimCitation` 边界去除内部 `answer_point_ids`，保持公开 schema 不变。
- `insufficient_evidence` 和 `version_conflict` 直接走拒答路径，不为了补齐 source/workflow/identifier 生成 filler。
- Prompt 版本更新为 `3.1.0`。

## 4. 运行与确定性验证

| 项目 | 结果 |
|---|---:|
| 完成 | 6/6 `answered` |
| 模型调用 | 40 |
| runtime | 34 次 / 362,661 tokens |
| judge | 6 次 / 47,751 tokens |
| 总 tokens | 410,412 |
| 耗时 | 343.7 s |
| answer-point coverage | 94.44% |
| citation integrity | 100% |
| expected status | 100% |
| wrong-version / forbidden evidence | 0 |
| identifier hallucination | 0 |
| major unsupported / contradiction | 0 |

确定性验证：77 项 unit tests、`compileall`、`pip check` 均通过。

## 5. 六题逐题结果

| Case | 正确核心 | 修复后的可见噪声 | 遗留评测差异 |
|---|---|---|---|
| `g011` | PandaRoot native/container setup 对比 | 0；三套无关 scope 声明不再外显 | focused gate 不替代 80 题 gate |
| `g074` | `LMDTrackQ → track_array → TrackPairInfo` | 0；无 `curated_panda_domain` | intent/evidence selector 待人工处置 |
| `g079` | `Lumi_TrksQA → PndLmdCombinedDataReader → createLmdFitData → runLmdFit → PndLmdLumiFitResult → lumi-values.json` | 0 | source/final-evidence 差异待处置 |
| `g085` | `rho(z) → restgas simulation → effective acceptance → PndLmdAcceptance` | 0；metadata 和 locator filler 不再外显 | source/final-evidence 差异待处置 |
| `g086` | a/e/r/v 数据流 | 0 | source/final-evidence 差异待处置 |
| `g089` | `PndMasterRunSim → PndTargetGenerator` 参数传递 | 0；无内部 metadata | judge 标记 p2 missing，待人工确认 |

每个 rendered claim 的内部 audit 映射均为 `question_core`。`g089` 的 p2 missing、`g074` 的 intent/evidence selector，以及 `g074/g079/g086/g089` 的 source/final-evidence 差异仍需统一人工审查；不能把它们写成“六题所有指标通过”。

## 6. 边界与下一步

- 原 RC2b records 未修改；源码/Prompt 已变，`m6-v2-36-rc2b` 不再代表当前行为。
- 六题 focused development gate=false；不宣称 M6 gate、完整 development gate 或 candidate verification 通过。
- 11 道 real failure 仍未处理。
- 本阶段不运行完整 80 dev、16 regression、24 challenge、acceptance、M7 或 M8。
- 对剩余差异先人工分类：评分器误判使用同一 Gold/selector/evaluator 离线 rescore；真实行为问题只修复受影响层并重跑受影响 case 与 sentinel。
- 只有代码、Prompt、模型配置、policy、index 和 Gold 完全冻结后，才允许运行一次完整 80 题 dev；acceptance 结果不得用于针对性调参。

## 7. 可追溯身份

- 焦点运行：`data/evaluation/runs/m6-v2-36-synthetic-noise-fix-6-v1/`
- 人工失败审查（YAML，可编辑）：`data/evaluation/runs/m6-v2-36-synthetic-noise-fix-6-v1/failure_review.yaml`
- 人工失败审查（Markdown 快照）：`data/evaluation/runs/m6-v2-36-synthetic-noise-fix-6-v1/failure_review.md`
- 六题范围中 `g074/g079/g086/g089` 需要人工决定；`g011/g085` 作为无失败项的 clean controls 登记，不要求选择 rescore/fix/waiver。
- 后续人工决定已并入 48 题统一表：`evaluation/reviews/m6_integrated_48_review.yaml` 与 `evaluation/reviews/m6_integrated_48_review.md`。最终分类为 g011/g085 clean PASS、g074/g079/g086 评分误判待 rescore、g089 真实失败待修复重跑。
- 本报告：`docs/M6_6_MIXED_CLAIM_NOISE_RESULT.md`
- 结果是当前行为修复的诊断记录，不覆盖原始 records，也不替代完整 M6 报告。
