# PANDA 科研代码库问答 Agent：架构决策、实施与验证记录

> **RC3f regression 审查修复（2026-08-09）：** Gold v2.6 与 evaluator 2.6.1 已落地；`g087/g097/g116` 的窄范围 completeness 修复及 `g098/g111` sentinel 全部通过。按评估策略未重跑完整 16 题；13 个已接受原始结果与 3 个 replacement 的 reviewed composite 为 16/16，所有 regression 质量检查通过。因 mixed runtime provenance，该结果不冒充单一冻结 candidate 的 formal gate。详见 `docs/M6_REGRESSION_RC3F_REVIEW_FIX_RESULT.md`。

> **evaluator-2.2 当前结果（2026-08-04）：** Gold v2.2 已对 `g074/g079/g086` 做窄修正并完成 68-case 零模型调用 diagnostic composite rescore；三题均 scorer v2.2/pass。48 题审查现为 36 resolved、12 real failure pending；替换不含 `g089`。rescore 新增 0 calls/0 tokens，历史 405 calls/4,126,750 tokens 不属于新增成本。因 subset 不完整，`complete_v2_dev=false`、development gate=false，不能冻结 candidate 或解锁后续阶段。详见 `docs/M6_68_NON_REAL_RESCORE_RESULT.md`。

> **历史快照：48 题统一人工审查（rescore 前，2026-08-04）：** 原 31 道已修正评分题、最新 6 道 mixed 审查和原 11 道未处理真实失败曾合并到 `evaluation/reviews/m6_integrated_48_review.yaml` 与 `.md`；当时为 33 resolved、3 pending offline rescore 和 12 pending fix-and-rerun。当前状态以本文件上方 evaluator-2.2 记录和 canonical YAML 为准。

> **3.6 RC2b 执行结果（2026-08-03）：** `QA_GENERATION_MODEL_ID` 默认值已恢复为 `gemini-3.6-flash`，evaluation judge 仍为独立的 `gemini-3.6-flash`，embedding 保持 `gemini-embedding-2`。12 道 dev 焦点题及 regression sentinel `g098` 通过；候选 `m6-v2-36-rc2b` 已冻结并验证。随后唯一一次完整 80 道 dev 运行完成 80/80，但 development gate 未通过，因此没有运行完整 16 道 regression、challenge、acceptance 或 M7。详见 `data/evaluation/runs/m6-v2-36-qa-dev-rc2b/` 和 `docs/M6_PHASE6_0_7_RESULT.md`。

> **31 题评分修正（2026-08-04）：** Gold v2.1、evaluator-2.1 和人工 adjudication 已落地。29 题只做离线重算；g041/g119 通过 `m6-v2-36-status-fix-31-retry1` 最小重跑，g031/g112 作为防过度拒答 sentinel。完整 80 题统一结果见 `docs/M6_31_CASE_RESCORE_RESULT.md`；该结果是开发诊断基线，不是新的 candidate，也不代表 M6 gate 通过。

> **六道 mixed claim-noise 修复（2026-08-04）：** `g011`、`g074`、`g079`、`g085`、`g086`、`g089` 在 `data/evaluation/runs/m6-v2-36-synthetic-noise-fix-6-v1/` 做了唯一一次焦点行为运行，6/6 `answered`。`scope_*`、`required_workflow`、`required_code`、`dataflow_locator_*` 和包含 `curated_panda_domain` 的文本现在只保留在内部 `claim_audit`，不进入用户可见 `answer/claims`；每个 rendered claim 的 audit 映射为 `question_core`。本次结果及逐题噪声审计见 `docs/M6_6_MIXED_CLAIM_NOISE_RESULT.md`。

> **历史焦点快照（rescore 前）：** 本次运行 40 次模型调用、410,412 tokens（runtime 34/362,661；judge 6/47,751），耗时 343.7 s。用户可见泄漏为 0，citation integrity、expected status、wrong-version/forbidden evidence、identifier hallucination、major unsupported 和 contradiction 均为通过；answer-point coverage 为 94.44%，但 `g089` 仍有 judge 标记的 p2 missing，且当时 `g074`、`g079`、`g086`、`g089` 尚有 source/final-evidence 或 selector 评分差异待人工处置。focused development gate=false，不代表完整 M6 gate 通过。原 RC2b records 不变；当前源码/Prompt 变更后，RC2b 不再代表当前行为。11 道 real failure 仍未处理。

> **M6 Benchmark v2 更新（2026-08-02）：** v8 的 17 项人工失败审查已导入（13 rescore、4 fix、0 waiver）。v2 的 120 题现已全部人工批准并原样导入，SHA-256 为 `f58ab7f55717aaa5b6205403dfcc78533b941e7fa2d082051848990a21c0af9d`。它仍是已暴露的 80 dev / 24 challenge / 16 regression benchmark，不是 hidden acceptance；新的 blind acceptance 尚未创建。导入审计及统计口径差异见 `evaluation/benchmarks/v2/review/local_import_validation.md`。

> **历史 Lite RC1 更新（2026-08-02）：** 当时 runtime 使用 `gemini-3.5-flash-lite`，evaluation judge 使用 `gemini-3.6-flash`。Lite 候选的完整 dev 已完成 80/80，但 development gate 未通过（Recall@10 79.06%、final evidence recall 53.81%、answer-point coverage 71.15%）。该段只保留历史运行事实，当前配置以上方 2026-08-03 更新为准。

> 本更新覆盖本文后方关于“等待 v8 首次人工失败审查”和旧 Prompt 版本的历史描述；当前 Prompt 版本为 `3.1.0`。

> 当前基线：2026-07-30，P0 与 P1 Phase 0–6 已完成；M6 正在开发集检索修复阶段  
> 项目目录：`PANDA_Agent/`  
> Python 包：`panda_agent`  
> 本文不修改父目录的 `agent.md`

本文记录问答 Agent 的架构决策、真实实现、运行命令、测试标准和最新结果。若本文与历史对话冲突，以当前源码、`data/manifests/source_manifest.json` 和本文最新基线为准。

## Knowledge bundle prototype

`panda-qa-kb export|inspect|restore|verify` is the implemented local
knowledge-bundle prototype for the fixed `panda_qa` database and
`panda_knowledge_v1` collection. Its maintainer export, clean-target restore,
local verification, three smoke questions, and explicit non-goals are recorded
in [docs/KNOWLEDGE_BUNDLE_PROTOTYPE.md](docs/KNOWLEDGE_BUNDLE_PROTOTYPE.md).
The 2026-08-09 round2 record is a real live export → inspect → isolated restore
→ verify → three-smoke PASS, with exact artifact hashes, counts, clean-target
proof, and `errors=[]` summaries. This remains a local prototype acceptance
only: it does not claim public security/release readiness or replace Vertex
dense query embedding (the normal QA query path still calls Vertex).

## P1 实施更新（Phase 0 → Phase 6）

P1 已严格按六个阶段完成，旧章节中把下列项目列为“P1 待办”的内容均由本节取代。

| 阶段 | 已完成实现 | 验证结果 |
|---|---|---|
| Phase 0 | 为 `KnowledgeAlias`、`IndexIdentity`、确定性 intent router、`EvaluationRunStore` 建立先失败的契约测试 | 4 个 P1 契约最初失败，实施后全部通过 |
| Phase 1 | 物化 `event_poca`、`*_pid.root`、`*_boost.root`、`*_pid_final.root`、profile 配置/文件模式与 producer/consumer edges；新增带 provenance 的 alias | q17/q18 均能解析到 canonical 对象 |
| Phase 2 | `RelationCandidateSpool` 使用临时 SQLite 落盘；`RelationResolver` 只构建一次对象索引；JSONL 改为流式写入 | 372,139 candidates 全量重建成功；M2 不再保存候选全集 |
| Phase 3 | `IndexIdentity` 锁定模型、3072 维、距离、sparse 模型和 schema version；迁移 `0004`；alias 表；运行失败/中断/恢复生命周期 | 指纹 `c527bbf...3cf2`；run 12–14 interrupted、15–16 completed |
| Phase 4 | 配置驱动 intent override、alias 前提纠正、canonical exact evidence、policy 驱动 targeted retrieval 次数 | q17/q18 首轮失败后修复为 2/2 answered |
| Phase 5 | 逐题 checkpoint 的可恢复评估；Vertex 429/503 有限重试；直接声明 `requests`；容器仅绑定 IPv4 localhost；QA trace 异常进入日志 | `p1-q17-q18-v2` answered rate 1.0 |
| Phase 6 | 全量 M2 重建、Alembic 迁移、真实 PostgreSQL/Qdrant 索引、故障恢复、独立 verify、live QA | index `valid=true`，missing/stale vectors 均为 0 |

最新规范化产物：

| 产物 | 数量 | SHA-256 |
|---|---:|---|
| `knowledge_objects.jsonl` | 102,875 | `7ee7b3a3be3d3fceac5f01230137942c9a0d0ff60969bf9e58696aa58d2b4876` |
| `relation_edges.jsonl` | 64,561 | `609fd869c8bc7613df4e84fbde95c172c0fce9ad1296ba32f939ab2d9b8136a9` |
| `relation_candidates.jsonl` | 372,139 | `b45264ff7451573c63c7d1e0b9fc169f79a97c5e256f3f70fd996517dfb80048` |
| `knowledge_aliases.jsonl` | 2 | `2e59201f5bcb7f5c515ec6c573af1f15f18e8a8bd97dbd34ceb54aa0fc1fe7da` |
| `workflow_steps.jsonl` | 374 | `27bc6e4fcda3debff056f2217a468b8ce27f4469fd85dc84feee9de8ab5b6c24` |

最终真实存储为 102,875 objects、64,561 accepted relations、372,139 candidates、2 aliases、374 workflows 和 80,698 Qdrant points。`panda-qa-index verify` 返回 `valid=true`。

> **运维发现：** 容器端口改为 `127.0.0.1` 后，客户端默认 URL 也必须使用 `127.0.0.1`，不能继续依赖 Windows 上可能优先解析为 IPv6 `::1` 的 `localhost`。该问题已在 `StorageSettings` 和 `.env.example` 修复。

> **剩余性能债务：** M3 已将 relations/candidates 改成流式 JSONL，索引进程工作集从约 1.98 GB 降到约 179 MB；但 PostgreSQL 全量 upsert/prune 仍较慢，未来应使用 `COPY + merge` 或按 ingestion run 分区切换。

## M6 实施状态：120 题已审核，开发集门禁修复中

120 题已经人工审核并全部批准，`panda-qa-eval validate --official` 已通过。Retrieval 开发门禁已经通过；QA candidate-v8 已完成 80/80，但仍未通过开发门禁，因此没有进入 acceptance、M7 或 M8。完整运行演进、问题分类和优化记录见 `docs/M6_EVALUATION_RETROSPECTIVE.md`。

已实现：

- `evaluation/benchmarks/v2/gold_questions.yaml`：签署后的 120 题暴露 benchmark；80 dev / 24 challenge / 16 regression；英文 60、中文 40、mixed 20；102 answered、10 insufficient、8 version conflict。旧 v1 的 80/40 文件仅作历史归档；
- `evaluation/build_gold_draft.py`：一次性初稿生成器，默认拒绝覆盖已进入审核的 YAML；
- `evaluation/GOLD_REVIEW_GUIDE.md`：逐题人工审核与批准规则；
- `evaluation.py`：严格 Gold schema、Evidence selector、Recall、citation/version/identifier 等确定性指标和冻结门槛；
- `evaluation_runner.py`：固定 manifest、逐题 JSONL checkpoint、resume、Gemini rubric judge、汇总和报告；
- `panda-qa-eval`：`validate`、`run`、`resume`、`report`、`review`；
- `QAAgent.run_detailed()`：同一次 QA 执行返回结果和脱敏检索诊断，不重复运行检索；
- `PROMPT_SET_VERSION=3.1.0` 与 evaluation judge system prompt；
- Vertex 调用计数与可用 token usage 统计，不保存 Prompt 内容。

已验证：120 题的 intent/split/language/status 分布完全符合计划；所有 Gold evidence group 均能在 102,875 个锁定对象中找到真实匹配；当前 54 项单元测试通过。Gold 数据集 hash 为 `2ed63e9af9df3c0dce0c1a71e046b5785e19e40d4292c1da8ba5d46a53b22034`，`official_ready=true`。

第一次正式开发集 retrieval run `m6-retrieval-dev-approved` 完成 80/80，无运行异常，但 Recall@10 为 `0.45`、intent accuracy 为 `0.80`，未达到 `0.85` 与 `0.90` 门槛。经过父页面 Evidence lineage、高置信 intent 路由、逐 symbol exact、可审核 query expansion、独立 paper channel、mandatory anchors 和来源配额修复，`m6-retrieval-dev-approved-v7` 达到 Recall@10 `0.9792`、intent accuracy `0.9875`、required-source coverage `1.0`。

QA 完整开发集从 candidate-v1 的 answer coverage `0.5823`、17 个 unsupported claims、27 个 identifier missing，改进到 candidate-v8 的 answer coverage `0.9375`、Recall@10 `0.9771`、intent `1.0`、citation `1.0`。v8 从 53/80 原子恢复并完成 80/80，但仍有 5 个 unsupported claims、1 个 required identifier missing，answered required-source coverage 为 `0.9873`，因此开发门禁未通过。

评估流程现已增加 mode-aware `development_gate.json` 和失败人工审查表。完整 dev 未通过时会生成 `failure_review.yaml`/`.md`；人工必须先判定 `rescore`、`fix` 或 `waiver`，再只运行受影响层。完整 80 题只用于冻结候选，acceptance 只在全部配置冻结后运行且不能用于针对性调参。

受限 shell 曾因无法读取 Vertex ADC 或 Docker daemon 而在模型调用前失败，恢复 v8 时也遇到 PostgreSQL 未启动导致的 manifest 阶段超时。这些均在模型调用或新 case 写入前结束；启动容器并验证索引后只恢复未完成 case，不作为模型质量依据。v8 的人工审核表位于 `data/evaluation/runs/m6-qa-dev-candidate-v8/failure_review.yaml` 和 `.md`。人工审核规则见 `evaluation/GOLD_REVIEW_GUIDE.md`，分层评估规则见 `docs/EVALUATION_POLICY.md`。

## 1. 当前范围

当前实现是只读、版本感知、结构感知、可验证引用的科研代码库 QA Agent。语料包括：

- LuminosityFit、PandaRoot、RestgasDetermination 三个固定 commit；
- Li、Karavdina、Pflüger 三篇固定 PDF；
- PandaRoot `2023-08-25-dev` Sphinx 固定网页快照。

支持 installation、usage、API、algorithm theory、algorithm implementation、data flow、module structure 和 troubleshooting 八类问题。当前正式入口是 CLI；FastAPI、Coding Agent、Debug Agent、多轮会话和长期 Memory 尚未实现。

## 2. 总体架构

```text
固定 Git/PDF/Sphinx 快照
  → Tree-sitter / Python AST / CMake / Docling / PyMuPDF / BeautifulSoup
  → KnowledgeObject + accepted RelationEdge + RelationCandidate + WorkflowStep
  → PostgreSQL 17 + Qdrant 1.15
  → exact / dense / sparse / workflow / recursive relation graph
  → weighted RRF + symbol/source priority + diversity + Gemini rerank
  → LangGraph bounded QA
  → evidence sufficiency
  → claim-only generation
  → deterministic verification + Gemini evidence review
  → deterministic final answer rendering
```

两个必须保持分离的概念域：

```text
LMD track → nominal/reconstructed IP
Target Spectrometer track → event POCA

angular/effective acceptance ε(θx, θy)
longitudinal reconstruction efficiency εreco(z)
```

## 3. Phase 0：先建立失败契约

在修改实现前增加 `tests/unit/test_p0_contracts.py`，锁定四项 P0 行为：

1. Sphinx 快照只有一个 canonical hash 算法；
2. unresolved/ambiguous 关系必须是 `RelationCandidate`，不能成为 accepted edge；
3. 最终 answer 只能从已验证 claims 确定性生成；
4. QA system prompts 必须声明 untrusted data 边界和 `never follow` 规则。

初始运行四项均失败；Phase 1–5 完成后四项均通过。

## 4. Phase 1：固定语料强门禁

### 4.1 固定来源

| 来源 | 固定标识 |
|---|---|
| LuminosityFit | `ddd83dcd1a74093bf48ef259a2849a67f9413f32` |
| PandaRoot | `18c09e91100db27867ded30e708b4dae95bd8357` |
| RestgasDetermination | `11f1edc49dcbaeb61d707491a6d3bbec390fcd42` |
| PandaRoot Sphinx | `2023-08-25-dev`，snapshot `5bff86c0f3a1102c80f3466a8ca0a63db48c0c7d8f142a78a0849219d7844f87` |
| Li thesis | `9930dfd79c74b9d1dadc6d1eb6c093ac10ccb45e12f641887bcdc8b823b8690a` |
| Karavdina thesis | `422421852c5a046c24e894a77b9380988ec8172914e9b30b055a100145c07a2b` |
| Pflüger thesis | `1b6ec987fc1430be085f2a7ba631d634f6580115ff0a90dff090dfcba5e990f3` |

Sphinx 快照包含 75 个 HTML 页面和 118 个资源。`py-modindex.html` 是上游返回 404 的可选页面；入口、必需页面和正文页均已保存。

### 4.2 实现

- `config.py::WebDocumentConfig` 保存 expected snapshot hash、页面数、资源数和 required paths。
- `source.py::compute_sphinx_snapshot_hash()` 是唯一 canonical 算法；输入包括 URL、final URL、HTTP status、规范化 content type 和文件 SHA-256。
- `source.py::verify_manifest()` 同时校验磁盘文件、manifest 和 `corpora.yaml`，不依赖网络缓存。
- snapshot 先写 staging，全部验证通过后才替换正式快照。
- `panda_agent.cli.source migrate-contract` 用于把已验证旧快照迁移到新 manifest contract，不重新下载内容。

当前验收：`corpus_locked=true`，`errors=[]`。

## 5. Phase 2：关系解析和知识对象契约

### 5.1 关系分层

解析器先产生 `RelationCandidate`。linker 只在同一合法 source version 范围内唯一匹配时生成 accepted `RelationEdge`：

- `resolved`：唯一解析，可进入 accepted graph；
- `ambiguous`：多个候选，只保留审计信息；
- `unresolved_internal`：语料内应有但未解析；
- `unresolved_external`：外部依赖，不伪造本地实体。

每个 candidate 的候选样本最多保留 20 个，但 metadata 保存总匹配数，避免 audit JSONL 无界膨胀。

### 5.2 Schema 与 seed

- `configs/relation_ontology.yaml` 已包含实际解析器产生的 `INCLUDES`、`INHERITS`、`DEPENDS_ON`。
- `configs/knowledge_schema.yaml` 包含 workflow、subsystem、Sphinx section、document reference 和派生 chunk 规则。
- `configs/seed_objects.yaml` 为 curated relation 建立真实端点对象。
- `ingestion.py::validate_ingestion_contract()` 检查对象类型、谓词和 accepted edge 两端完整性。

### 5.3 确定性产物

规范化目录名由 manifest hash 决定：

`data/normalized/9925ec31a6122e05388806990f79aae036f3b0989c4584d24f2092bc4edb3d94/`

| 产物 | 数量 | SHA-256 |
|---|---:|---|
| `knowledge_objects.jsonl` | 102,868 | `96bca54e0f4b077051c6eecb8071f12a6333a00a57a2f910547a2679b46d6f78` |
| `relation_edges.jsonl` | 64,554 | `7429479091428dc0bea069db7c7082eef77ccb157d7e2069bdfbce6b70822a3e` |
| `relation_candidates.jsonl` | 372,139 | `aaa06298b523de4ecdf5ecfef809ff1987cf56647cfab6be1dfa142d605a0481` |
| `workflow_steps.jsonl` | 374 | `b6d3d5827a57b45ed273f544d013c4f514a22b724a5b59cf917dc95c6b620dad` |
| `parse_errors.jsonl` | 1 | `954d96d9a99db774ba8fcb3cf738f2d8757820289fb674b0b99fc0b9d964da13` |

连续两次完整 M2 重建的数量及上述五个 hash 完全一致。Karavdina PDF 的 Docling 单文档 300 秒超时后确定性降级到 PyMuPDF；页码和文本 block 坐标仍保留。

## 6. Phase 3：真实 PostgreSQL/Qdrant 和图检索

### 6.1 数据库

Alembic 当前为 `0003 (head)`：

- `0001`：初始表；
- `0002`：FTS 长文本保护；
- `0003`：`relation_candidates` 表、accepted relation 两端外键和索引。

迁移删除了旧模型中两端不完整的 orphan accepted edges；这些信息仍可由旧规范化 JSONL 恢复。新 accepted edges 有数据库外键约束，不允许再次写入不存在的端点。

### 6.2 Qdrant

Collection：`panda_knowledge_v1`。

- dense：`gemini-embedding-2`，3072 维，cosine；
- sparse：`Qdrant/bm25`；
- document/query task type 严格分离；
- cache key：`model + task_type + text_hash`；
- source/version/object type/authority payload filter；
- SQL/Qdrant 全量 apply 同步清理 stale records。

当前运行态：

| 项目 | 数量 |
|---|---:|
| PostgreSQL objects | 102,868 |
| accepted relations | 64,554 |
| relation candidates | 372,139 |
| workflows | 374 |
| Qdrant expected/actual | 80,691 / 80,691 |
| missing/stale vectors | 0 / 0 |

完整重跑索引得到 `indexed_vectors=0`、`deleted_vectors=0`，幂等门禁通过。reconciliation live test 人工插入 stale SQL 和 Qdrant point 后，两者均被删除。

### 6.3 图检索

`Retriever._graph()` 使用 recursive CTE，沿 accepted relation 返回 seed 的相对端点，支持 `max_relation_hops`，并应用 repo/source-version filter。live test 验证返回真实 opposite endpoint，且不会把 seed 自身当作“邻居”。

## 7. Phase 4：claim-first 确定性答案

模型的 `ANSWER_SCHEMA` 只允许：

```json
{
  "claims": [
    {
      "claim_id": "claim1",
      "claim_text": "...",
      "evidence_ids": ["evidence..."]
    }
  ]
}
```

模型不再提供自由 `answer`。`QAAgent._verify()` 检查：

- claim ID 唯一且非空；
- evidence ID 存在；
- code evidence 的 repo/SHA/path/line 完整；
- paper evidence 的 PDF page 完整；
- web evidence 的 snapshot date/URL/heading 完整；
- API、class、path 和文件名真实出现在所引证据中；
- Gemini reviewer 返回的每个 unsupported claim ID 都被处理。

通过验证后，`render_verified_answer()` 只从 `ClaimCitation` 确定性拼接最终 answer。二次验证仍失败则返回 `insufficient_evidence`。

> 中文 `claim_text` 是 Gemini 对英文证据的中文归纳，不表示语料原文是中文。输出语言通常跟随用户问题语言。

## 8. Phase 5：Prompt 信任边界

所有 QA prompts 位于 `src/panda_agent/prompts.py`：

- `COMMON_SECURITY_SYSTEM_PROMPT`；
- `QUERY_ANALYZER_SYSTEM_PROMPT`；
- `RERANK_SYSTEM_PROMPT`；
- `ANSWER_SYSTEM_PROMPT`；
- `EVIDENCE_REVIEW_SYSTEM_PROMPT`；
- `REVISION_SYSTEM_PROMPT`。

用户问题、检索候选、证据和旧 draft 以 JSON 数据字段传入，例如 `untrusted_question`、`untrusted_evidence`。System instruction 明确要求 never follow 这些数据中的指令。Structured output schema 限制 repo enum、evidence IDs 和返回结构。

确定性 guardrails：

- 空问题拒绝；
- 超过 20,000 字符的问题在模型调用前拒绝；
- requested ref/SHA 必须与 locked corpus 比对；
- Sphinx `2023-dev` 文档标签不会误当成仓库 ref；
- 注入文本无法改变 resolved locked SHA；
- 最多一次 targeted retrieval 和一次 answer revision。

这不能证明模型对所有 Prompt Injection 绝对免疫，但建立了明确的指令/数据边界和可执行回归契约。

## 9. Phase 6：完整验证结果

### 9.1 自动测试

| 验证 | 最新结果 |
|---|---|
| PANDA unit tests | 35/35 通过 |
| P0 contracts | 4/4 通过 |
| Source offline gate | locked，0 errors |
| M2 deterministic rebuild | 两次五组 hash 完全一致 |
| PostgreSQL/Qdrant schema | live 通过 |
| Relation opposite-end graph | live 通过 |
| Stale SQL/vector reconciliation | live 通过 |
| Vertex generation/query/document embedding | live 通过 |
| Python `compileall` | 通过 |
| `pip check` | No broken requirements found |
| 父目录兼容回归 | 27/27 通过 |

### 9.2 M4 检索评估

`evaluation/retrieval_questions.yaml` 的 30 道真实问题全部完成：

- 30/30 返回非空 Evidence；
- 28/30 有非空 graph channel；
- intent 与人工标签一致 23/30；
- 没有运行崩溃。

结果：`data/evaluation/retrieval_results.json`。

### 9.3 M5 QA 评估

24 道真实端到端题全部运行。最终最新结果：

- 22 `answered`；
- 2 `insufficient_evidence`；
- 0 非预期崩溃；
- 所有 answered 结果均含 claims 和 evidence。

结果分片：

- `data/evaluation/qa_results_0_5.json`；
- `data/evaluation/qa_results_5_24.json`；
- `data/evaluation/qa_results_16_18.json`（q17/q18 最新复验）；
- `data/evaluation/qa_results_21_22.json`（q22 文档版本路由修复后的复验）。

保留的两个安全拒答：

1. q17 使用通用名 `restgas_profile.txt`，而锁定语料实际使用 `restgas_profile` 配置键和具体 `restgas_16012024_*.txt` 文件名；系统不把不存在的通用文件名伪造成实体。
2. q18 的 `event_poca` 在源码/README 文本中存在，但尚未物化为一级 DataProduct/ROOTTree 对象，targeted retrieval 不能满足严格 symbol gate。

二者应作为 P1 ontology/alias 建模任务处理，不应通过放宽 verifier 修复。

### 9.4 评估中发现并修复的缺陷

- `locator.path=null` 导致 `.lower()` 崩溃：已归一化为空字符串，并增加单元回归。
- Sphinx `2023-dev` 被误识别为 repo ref：已按固定网页版本 token 消歧。
- targeted retrieval 未携带缺失 symbol：已把 missing symbol 写回固定 `RetrievalPlan`。
- exact symbol 在最终 evidence 中可能被 rerank/预算挤出：已增加 symbol-first 优先级。

## 10. 使用方法

从 `PANDA_Agent/` 目录执行：

```powershell
# 离线语料门禁
..\.venv\Scripts\python.exe -m panda_agent.cli.source verify

# 全量结构化解析
..\.venv\Scripts\python.exe -m panda_agent.cli.ingest

# 服务、迁移与索引
docker compose up -d --wait postgres qdrant
..\.venv\Scripts\alembic.exe upgrade head
..\.venv\Scripts\python.exe -m panda_agent.cli.index plan
..\.venv\Scripts\python.exe -m panda_agent.cli.index apply
..\.venv\Scripts\python.exe -m panda_agent.cli.index verify

# 检索诊断
..\.venv\Scripts\python.exe -m panda_agent.cli.retrieve "PndTargetGenerator 如何配置？"

# QA
..\.venv\Scripts\python.exe -m panda_agent.cli.qa ask "event_poca 如何传给第二遍 PID？"

# M6 Gold 结构和正式审核状态校验（当前 120 题均已 approved）
..\.venv\Scripts\panda-qa-eval.exe validate
..\.venv\Scripts\panda-qa-eval.exe validate --official

# 正式运行（完整 dev 只用于冻结候选；普通修改应使用 --case-id 焦点回归）
..\.venv\Scripts\panda-qa-eval.exe run retrieval --split dev --run-id m6-retrieval-dev
..\.venv\Scripts\panda-qa-eval.exe run qa --split dev --run-id m6-qa-dev
..\.venv\Scripts\panda-qa-eval.exe resume --run-id <RUN_ID>
..\.venv\Scripts\panda-qa-eval.exe report --run-id <RUN_ID>
```

Vertex 配置：

```env
QA_GCP_PROJECT_ID=your-project-id
QA_VERTEX_LOCATION=global
QA_GENERATION_MODEL_ID=gemini-3.6-flash
QA_EVALUATION_JUDGE_MODEL_ID=gemini-3.6-flash
QA_EMBEDDING_MODEL_ID=gemini-embedding-2
QA_EMBEDDING_CONCURRENCY=16
```

不要把真实密钥写入文档或提交到版本库。项目使用 ADC/当前 `.env`；模型不做 fallback。

## 11. 当前 P1/P2 技术债务

### P1

- 将 `event_poca`、具体 restgas profile 文件、输入/输出 ROOT tree 和 data product 物化为一级对象，并建立 producer/consumer 关系。
- 为实际 profile 文件和用户常用泛称建立带 provenance 的 alias，不允许无证据猜测。
- M2 当前全量在内存中排序 37 万 candidates，峰值内存较高；改为分区/流式 linker 和外部排序。
- `ingestion_runs` 在 embedding 异常时可能保留 `running`；增加 try/finally 失败状态。
- 为 30 道检索题补 gold evidence，计算 Recall@10，而不仅是运行成功率。
- 调整 deterministic intent override 或扩充分类评估；当前 intent 命中 23/30。

### P2

- 增加结构化日志、trace ID、模型调用耗时和 token/cost 观测。
- 为 Prompt 增加显式版本号和 snapshot tests。
- 评估 runner 应逐题 checkpoint，并支持按 ID 合并 resume 结果；本次中途崩溃暴露了“只在末尾保存”的问题。
- 补 FastAPI、并发限制、用户隔离和 PostgreSQL checkpoint 后再支持多轮会话。

## 12. 不在当前实现中的能力

- 无标准 LLM Tool Calling；检索通道由 Python 固定执行。
- 无多轮对话 Memory、用户级长期记忆或 LangGraph checkpoint。
- 无 REST API/Web UI。
- 无代码写入、命令执行、自动 debug 或实验运行权限。
- M6 的 120 题 schema、人工批准和评估器已完成；retrieval 开发门禁已通过，QA candidate-v8 正等待失败结果人工审查，正式 acceptance 尚未运行。

这些能力不得在文档或回答中描述成已经实现。
