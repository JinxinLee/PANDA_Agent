# Knowledge Bundle 迁移与迁移后评估指南

本文说明如何验证一个已经构建好的 PANDA Knowledge Bundle 是否可以从原始运行环境迁移到干净环境，并比较迁移前后的运行结果。

这套流程的目的不是重新构建知识库，而是回答一个更窄、更重要的问题：

> PostgreSQL、Qdrant 和本地运行时资源恢复后，是否仍然可以不解析语料、不重新生成 embedding、不重新 indexing，直接完成 QA？

## 1. 范围和原则

本流程只使用一个从 Gold v2.6 中冻结出来的 10 题迁移测试集：

| case | intent | expected status |
|---|---|---|
| g001 | installation | answered |
| g007 | installation | insufficient_evidence |
| g012 | installation | version_conflict |
| g013 | usage | answered |
| g027 | api | answered |
| g051 | algorithm_theory | answered |
| g060 | algorithm_implementation | answered |
| g085 | data_flow | answered |
| g106 | module_structure | answered |
| g116 | troubleshooting | answered |

冻结测试集位于 `evaluation/migration/v1/suite.json`。它记录了 Gold 文件的 SHA-256，因此不能在迁移测试过程中修改 Gold、Prompt、embedding 模型、索引或检索策略。

本流程明确不做：

- Phase 4/5 的检索或回答调参；
- 完整 80 题 dev、16 题 regression、challenge 或 acceptance；
- 语料 parsing、document embedding、Qdrant indexing；
- 重新生成 PostgreSQL/Qdrant 数据；
- 公开分发安全、签名、多 Bundle、rollback 或远程下载机制。

## 2. 迁移前提

迁移测试需要：

1. 一个已经通过 `panda-qa-kb inspect` 的 Bundle；
2. 原始运行态 PostgreSQL/Qdrant；
3. 一个只启动基础设施的干净 PostgreSQL/Qdrant；
4. `evaluation/benchmarks/v2_6/gold_questions.yaml` 和其 `benchmark_manifest.json`；
5. 本地 FastEmbed 运行资源；
6. 只有 QA A/B 阶段才需要 Vertex 配置。

恢复前应只启动 PostgreSQL 和 Qdrant。若使用独立 Compose 项目，固定项目名可以避免恢复环境误连到已有容器：

```powershell
$env:COMPOSE_PROJECT_NAME = 'panda_migration_v2'
docker compose -f tests\integration\docker-compose.bundle-restore.yml up -d --wait
```

恢复顺序必须是：

```text
空 PostgreSQL/Qdrant
  → inspect（manifest + SHA-256）
  → restore
  → verify
  → deterministic replay
  → evaluator A/B
  → 可选的两组 10 题 QA A/B
```

不要先启动会自动执行 migration 或 `Storage.initialize()` 的应用容器，否则 restore 的“目标必须为空”检查会失败。

## 3. 固定身份

本轮实际使用的身份如下：

| 项目 | 固定值 |
|---|---|
| canonical Gold | `evaluation/benchmarks/v2_6/gold_questions.yaml` |
| Gold SHA-256 | `b5406e36c64ee664f9e2ff9c0f42e354feb7164c81d8f1c7551d8f2ed1d0b687` |
| migration suite | `evaluation/migration/v1/suite.json` |
| suite internal SHA-256 | `6025336010e892841db6204f7a2f90622ad1eaee12b3cc1e8cc841e0577ba1b6` |
| Bundle schema | `panda-knowledge-bundle/v2` |
| PostgreSQL objects | 102,875 |
| Qdrant points | 80,698 |
| dense dimension | 3,072 |
| embedding model | `gemini-embedding-2` |

Bundle 的具体 artifact hash 以对应 Bundle 的 `bundle_manifest.json` 为准；本轮导出的 PostgreSQL dump SHA-256 为 `fcb9e2d...f180e`，Qdrant snapshot SHA-256 为 `f568d29...6002`。

## 4. 标准命令流程

以下命令从 `PANDA_Agent` 目录执行。路径和端口应按实际环境调整，但不能替换 Gold 或 suite。

### 4.1 校验 suite 和 Bundle

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.migration `
  --project-root . validate-suite `
  --suite evaluation\migration\v1\suite.json `
  --canonical-gold evaluation\benchmarks\v2_6\gold_questions.yaml

..\.venv\Scripts\panda-qa-kb.exe inspect --bundle D:\panda-bundles\panda-kb-v2
```

`inspect` 只读验证 manifest、Bundle 文件 hash、Qdrant 配置和 FastEmbed 资源；它不连接 Vertex，也不建立索引。

### 4.2 恢复并验证干净环境

```powershell
$env:COMPOSE_PROJECT_NAME = 'panda_migration_v2'
..\.venv\Scripts\panda-qa-kb.exe restore `
  --bundle D:\panda-bundles\panda-kb-v2 `
  --project-root .

..\.venv\Scripts\panda-qa-kb.exe verify `
  --bundle D:\panda-bundles\panda-kb-v2 `
  --project-root .
```

`verify` 必须报告 `valid=true`，并且 PostgreSQL revision、表数量、Qdrant exact count/dimension/payload、FastEmbed、runtime BM25 和 manifest 固定的 100 个跨存储 sample 全部通过。

### 4.3 捕获原始运行态的固定 replay 输入

这一步是本轮唯一允许调用 Vertex 的捕获步骤之一：

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.migration `
  --project-root . capture `
  --suite evaluation\migration\v1\suite.json `
  --live `
  --output data\evaluation\migration\v1\capture.json
```

捕获文件包含固定题目、查询计划和用于 deterministic replay 的通道输入。文件可能较大，不应提交到公开源码仓库。

### 4.4 零模型调用的 replay 对比

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.migration `
  --project-root . replay `
  --suite evaluation\migration\v1\suite.json `
  --capture data\evaluation\migration\v1\capture.json `
  --database-url postgresql://panda:panda@127.0.0.1:55432/panda_qa `
  --qdrant-url http://127.0.0.1:6333 `
  --collection panda_knowledge_v1 `
  --output data\evaluation\migration\v1\replay-original.json

..\.venv\Scripts\python.exe -m panda_agent.cli.migration `
  --project-root . replay `
  --suite evaluation\migration\v1\suite.json `
  --capture data\evaluation\migration\v1\capture.json `
  --database-url postgresql://panda:panda@127.0.0.1:55433/panda_qa `
  --qdrant-url http://127.0.0.1:6335 `
  --collection panda_knowledge_v1 `
  --output data\evaluation\migration\v1\replay-restored.json

..\.venv\Scripts\python.exe -m panda_agent.cli.migration `
  --project-root . compare-replay `
  --left data\evaluation\migration\v1\replay-original.json `
  --right data\evaluation\migration\v1\replay-restored.json `
  --output data\evaluation\migration\v1\replay-compare.json
```

`compare-replay` 比较每道题的通道结果、分数和 fusion tie group。它是确定性存储查询 probe，不等同于完整的 LLM retriever 重放；因此它用于证明跨存储数据一致性，不用于证明模型输出一致。

### 4.5 Evaluator lookup A/B

Evaluator 必须在同一 Gold、同一 selector 规则下比较原始 normalized JSONL 与 Bundle 内 portable catalog：

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.migration `
  --project-root . compare-evaluator `
  --canonical-gold evaluation\benchmarks\v2_6\gold_questions.yaml `
  --normalized-objects data\normalized\<manifest>\knowledge_objects.jsonl `
  --portable-catalog data\tmp\panda-kb-migration-v2\evaluator\evaluator_lookup_catalog.json `
  --output data\evaluation\migration\v1\evaluator-compare.json
```

通过条件是 `passed=true`、`selector_parity=true` 且 `model_calls=0`。这一步可以区分“恢复后 evaluator lookup 变化”和“QA 运行行为变化”。

### 4.6 两组 10 题 QA A/B

QA A/B 只在 replay 和 evaluator A/B 通过后运行。它会调用 runtime generation、query planning/reranking、answer generation 和 evaluation judge，因此要记录成本，不要在每次代码微调后重复执行。

原始环境：

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.migration `
  --project-root . run-qa `
  --role baseline --live `
  --suite evaluation\migration\v1\suite.json `
  --canonical-gold evaluation\benchmarks\v2_6\gold_questions.yaml `
  --portable-catalog data\tmp\panda-kb-migration-v2\evaluator\evaluator_lookup_catalog.json `
  --database-url postgresql://panda:panda@127.0.0.1:55432/panda_qa `
  --qdrant-url http://127.0.0.1:6333 `
  --collection panda_knowledge_v1 `
  --output data\evaluation\migration\v1\qa-baseline.json
```

恢复环境只替换 `--project-root`、数据库/Qdrant endpoint 和输出路径：

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.migration `
  --project-root data\tmp\panda-kb-migration-clean-v2 run-qa `
  --role restored --live `
  --suite evaluation\migration\v1\suite.json `
  --canonical-gold evaluation\benchmarks\v2_6\gold_questions.yaml `
  --portable-catalog data\tmp\panda-kb-migration-v2\evaluator\evaluator_lookup_catalog.json `
  --database-url postgresql://panda:panda@127.0.0.1:55433/panda_qa `
  --qdrant-url http://127.0.0.1:6335 `
  --collection panda_knowledge_v1 `
  --output data\evaluation\migration\v1\qa-restored.json
```

最后进行 model-free 对比和报告生成：

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.migration `
  compare-qa `
  --baseline data\evaluation\migration\v1\qa-baseline.json `
  --restored data\evaluation\migration\v1\qa-restored.json `
  --output data\evaluation\migration\v1\qa-compare.json

..\.venv\Scripts\python.exe -m panda_agent.cli.migration report `
  --suite evaluation\migration\v1\suite.json `
  --output-dir data\evaluation\migration\v1\report `
  --replay data\evaluation\migration\v1\replay-compare.json `
  --evaluator data\evaluation\migration\v1\evaluator-compare.json `
  --qa data\evaluation\migration\v1\qa-compare.json
```

CLI 遵循不覆盖原则。如果目标 artifact 已存在，使用新的带版本后缀的输出目录，而不是覆盖旧报告。

## 5. 门禁和结论解释

迁移报告分成三层：

1. **Bundle/runtime verify**：恢复后数据库、向量库和本地资源是否完整；
2. **replay gate**：同一固定输入在两个后端是否得到相同的确定性 storage-query 结果；
3. **QA A/B**：两次模型驱动运行是否出现绝对安全问题或相对迁移退化。

QA A/B 不要求两次自然语言答案逐字相同，也不要求 evidence ID 集合完全相同。应重点检查：

- restored 是否有异常；
- expected status 和 citation integrity 是否保持；
- wrong-version、forbidden evidence、identifier missing、critical point missing 是否增加；
- answer-point/source coverage 是否下降；
- Gold/final evidence recall 的差异是否只是模型选择波动。

本轮实际结果：

| 层级 | 结果 |
|---|---|
| 10/10 deterministic replay | `passed=true` |
| evaluator selector parity | `passed=true`、`selector_parity=true` |
| baseline QA | 10/10，无异常，34 model calls，797,902 tokens |
| restored QA | 10/10，无异常，34 model calls，724,880 tokens |
| status/citation | 两侧均 10/10 |
| relative transfer gate | `true` |
| absolute safety gate | `true` |
| final conclusion | `runtime_equivalent_but_model_variance_observed` |

报告中的 g001 answer-point coverage 在迁移前后均为 0，属于两侧共同的既有回答/评分问题，不应归因于 Bundle；g060 的 final evidence recall 在恢复后反而提高；g106 的 Gold recall 从 0.25 到 0，是模型证据选择变化，而不是 replay 或 selector parity 失败。

因此本轮结论是：

> Bundle 恢复没有显示出知识对象丢失、Qdrant 数据损坏或 evaluator selector 改变。QA 结果存在模型驱动的 evidence/answer 波动，但没有检测到迁移特有的绝对安全失败或相对退化。

## 6. 结果文件

本轮结果保存在 `data/evaluation/migration/v1/`：

- `suite.json`：10 题冻结 suite；
- `capture.json`：原始运行态固定 replay 输入；
- `replay-original.json`、`replay-restored.json`、`replay-compare.json`：零模型 replay；
- `evaluator-compare.json`：normalized 与 portable evaluator lookup A/B；
- `qa-baseline.json`、`qa-restored.json`：两组 live QA 收据；
- `qa-compare-v3.json`：逐题 status、Gold/final evidence、answer-point 和 source 对比；
- `report_v3/migration_report.json`、`report_v3/migration_report.md`：最终报告。

最终报告 SHA-256：

```text
report_v3/migration_report.json
ce1c089a0c1909c03bfbdbc45164cae344e95f54ad39b12cda9428650e9f7a22
```

## 7. 常见问题

### Vertex healthcheck 通过，但 migration QA 报 ADC 不可用

先确认命令从项目目录启动并能找到上级 `.env`，再运行：

```powershell
..\.venv\Scripts\python.exe -m panda_agent.cli.healthcheck
```

不要把认证失败收据当作质量结果；应保留失败文件、换新的输出路径重跑，并检查 `records` 中 `exception` 数量为 0。

### restore 报目标非空

停止应用容器，只保留空 PostgreSQL/Qdrant；检查 `COMPOSE_PROJECT_NAME`、端口和数据库名是否指向干净实例。不要删除原始运行态数据。

### macOS/Linux 解压后 FastEmbed 目录不可进入

使用项目提供的 Bundle restore 流程，不要直接依赖会把 Windows 反斜杠当普通字符的 unzip 结果。restore 会安装 `data/runtime/fastembed` 并执行 local-only functional probe。

### 是否需要重新 parsing、embedding 或 indexing？

迁移测试的答案是“不需要”。只有 `panda-qa-kb verify` 发现 manifest/count/fingerprint 不一致，或明确要构建新的语料版本时，才进入独立 ingestion/indexing 流程。

## 8. 清理临时恢复环境

确认报告和 artifact 已保存后，可以停止本轮创建的容器；不要使用 `-v` 删除可能仍需复核的卷：

```powershell
docker compose -p panda_migration_v2 down
```
