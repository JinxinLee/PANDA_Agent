# Gold v2.1 变更报告

## 目的

`m6-benchmark-v2.1` 是针对 RC2b 失败审查的、可审计的 Gold 修订。它只修正人工确认的 selector、来源类型和 intent rubric，不改变题目文本、split、cluster、允许的语料版本或题目数量。

构建脚本是 `evaluation/build_gold_v21.py`。脚本只执行 `gold_v2_1_patch.yaml` 中列出的确定性操作，不执行 embedding、模糊扩展或重新聚类。

## 身份与哈希

| 项目 | 值 |
|---|---|
| benchmark version | `m6-benchmark-v2.1` |
| base dataset SHA-256 | `2c412a501c2ae45ff4d605562f4b56f9afa0a6a14067f402fc0a45bd09020ec1` |
| v2.1 dataset SHA-256 | `1fea656c1ea05ac2cf4bbb78e8e712fec3c09e40c31f5d77a914fa7cadbd9d22` |
| patch SHA-256 | `d089d58c7bbc712ba3fd77849a99971c87fd76c2ff7be71022568f25e6ef4304` |
| signed review SHA-256 | `2e7ee94257afa32620745b6e5f8f4ba1ae49f27b4827c3f2980ba4b21f699a97` |
| selector audit SHA-256 | `3a36c6a26d4a40c928fac973f204901363a6aeac707b83b4e46b6dff2e08056d` |
| questions | 120 |
| split | dev 80 / challenge 24 / regression 16 |
| status | answered 102 / insufficient_evidence 10 / version_conflict 8 |

官方校验：`120/120 approved`，所有 evidence group 均能匹配锁定对象；`release_eligible=false`、`acceptance_exposed=true` 保持不变。

## 审核授权的变化

- `g010` 增加 `accepted_intents: [usage]`，因此 installation/usage 两种人工认可的 intent 都可判定正确。
- 对人工确认的等价证据补充精确 `source_id + source_version_id + path/symbol` 或精确 PDF 页码；`any_of` 仍按 evidence group 计分且每组最多计一次。
- 对安装、MasterTasks、LuminosityFit factory、DataReader、Restgas `ana_dpm.C` 等题补充真实的仓库或 Sphinx selector。
- 对 `g017`、`g059`、`g066`、`g069`、`g070` 删除人工确认不必要的 paper group，并同步调整 `required_source_types`。
- 不把 README 默认分类成 code；canonical object type 为 `readme + documentation`。
- 没有修改 query、split、cluster、allowed source versions、题目数量或签署的 v2 文件。

完整操作记录位于 `gold_v2_1_patch.yaml`，签署审计决策位于 `audit_resolution.yaml`。

## 可重复构建

```powershell
..\.venv\Scripts\python.exe evaluation\build_gold_v21.py
..\.venv\Scripts\python.exe -m panda_agent.cli.evaluate --project-root . validate --official --dataset evaluation/benchmarks/v2_1/gold_questions.yaml
```

构建器会重新计算 dataset、patch 和 selector audit hash；相同输入必须产生相同规范化 YAML 和 JSON 报告。
