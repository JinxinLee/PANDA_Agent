# PANDA QA Agent 新用户 Bundle 使用指南

本指南面向只获得以下两项内容的新用户：

1. `PANDA_Agent` 代码；
2. 维护者预先生成的 PANDA Knowledge Bundle。

按照本指南启动时，不需要重新下载或解析论文、网页和代码仓库，也不需要生成文档向量或重建索引。首次启动只恢复 PostgreSQL、Qdrant 和本地 BM25 运行资产。

> **适用边界：** 当前实现是可信本地 Bundle prototype。Bundle 没有数字签名、在线下载、多版本切换、自动回滚或公开分发安全机制。只使用来自可信维护者的 Bundle。

## 1. 你应当拿到什么

代码目录中应存在：

```text
PANDA_Agent/
├── docker-compose.yml
├── pyproject.toml
├── configs/
├── data/manifests/
└── src/panda_agent/
```

Bundle 目录中应存在：

```text
panda-kb-bundle/
├── bundle_manifest.json
├── postgres.dump
├── qdrant.snapshot
└── runtime_assets/
    └── fastembed/
        └── bm25/
```

缺少任一 Bundle 文件时不要执行恢复。

## 2. 前置条件

- Windows 10/11 与 PowerShell；
- Python 3.12 或更高版本；
- Docker Desktop，且 `docker compose version` 可正常执行；
- QA 阶段需要可以调用 Vertex AI 的 Google Cloud 项目和 Application Default Credentials（ADC）；
- 建议至少预留 5 GB 可用磁盘空间，用于 Bundle、数据库和 Qdrant 恢复数据。

> **注意：** `inspect`、`restore` 和 `verify` 不需要 Vertex。只有最终 QA 查询需要 Vertex，因为 dense query embedding 和回答生成仍由 Vertex 完成。

## 3. 创建 Python 环境

进入 `PANDA_Agent` 项目根目录：

```powershell
Set-Location C:\path\to\PANDA_Agent
```

创建项目本地虚拟环境并只安装 QA 运行依赖：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[qa]"
```

不需要安装 `ingestion` extra，也不要运行：

```text
panda-qa-source
panda-qa-ingest
panda-qa-index apply
panda-qa-index resume
```

## 4. 配置本地服务和 Vertex

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`，至少确认以下配置：

```env
QA_GCP_PROJECT_ID=your-gcp-project-id
QA_VERTEX_LOCATION=global
QA_GENERATION_MODEL_ID=gemini-3.6-flash
QA_EMBEDDING_MODEL_ID=gemini-embedding-2
QA_EMBEDDING_DIMENSIONS=3072

PANDA_POSTGRES_PASSWORD=choose-one-local-password
PANDA_DATABASE_URL=postgresql://panda:choose-one-local-password@127.0.0.1:55432/panda_qa
PANDA_QDRANT_URL=http://127.0.0.1:6333
PANDA_QDRANT_COLLECTION=panda_knowledge_v1
PANDA_FASTEMBED_MODEL_PATH=data/runtime/fastembed/bm25
```

`PANDA_POSTGRES_PASSWORD` 与 `PANDA_DATABASE_URL` 中的密码必须一致。不要提交 `.env`。

在运行 QA 前配置 ADC：

```powershell
gcloud auth application-default login
```

如果组织使用其他 ADC 配置方式，请遵循组织的 Google Cloud 权限策略；不要把凭据文件复制进仓库。

## 5. 在恢复前检查 Bundle

将 Bundle 放在任意本地目录，并解析为绝对路径：

```powershell
$bundlePath = (Resolve-Path 'D:\panda-bundles\panda-kb-v1').Path
```

执行本地完整性检查：

```powershell
.\.venv\Scripts\panda-qa-kb.exe inspect --bundle $bundlePath
```

`inspect` 会验证 manifest schema、文件大小、SHA-256 和本地 BM25 资产是否存在。它不会连接数据库、Qdrant 或 Vertex。

如果出现 hash mismatch、文件缺失或 manifest 校验失败，应停止并重新获取可信 Bundle，不要继续恢复。

## 6. 启动空的 PostgreSQL 和 Qdrant

为本次恢复设置一个固定的 Compose project 名称：

```powershell
$env:COMPOSE_PROJECT_NAME = 'panda_qa_bundle'
docker compose up -d --wait postgres qdrant
docker compose ps
```

只启动 `postgres` 和 `qdrant`。当前项目没有需要在恢复前启动的 Agent 应用容器。

恢复要求：

- PostgreSQL 中不存在 `knowledge_objects` 表；
- Qdrant 中不存在 `panda_knowledge_v1` collection；
- 项目中不存在 `data/runtime/fastembed/bm25`。

如果目标不是空的，`restore` 会拒绝继续。不要使用强制覆盖。

## 7. 恢复预构建知识库

在保持相同 PowerShell 会话和 `COMPOSE_PROJECT_NAME` 的情况下执行：

```powershell
.\.venv\Scripts\panda-qa-kb.exe restore `
  --bundle $bundlePath `
  --project-root (Get-Location)
```

恢复过程会依次：

1. 再次执行 manifest 和 SHA-256 preflight；
2. 检查 PostgreSQL/Qdrant 目标为空；
3. 使用单事务和 `--exit-on-error` 恢复 PostgreSQL；
4. 上传并恢复 Qdrant snapshot；
5. 安装 `data/runtime/fastembed/bm25`；
6. 写入 `data/runtime/installed_bundle.json`。

prototype 没有跨 PostgreSQL/Qdrant 的分布式事务。如果 PostgreSQL 恢复成功而后续步骤失败，不要直接重复恢复；保留错误输出并在隔离环境中重新建立空目标。

## 8. 验证恢复结果

```powershell
.\.venv\Scripts\panda-qa-kb.exe verify `
  --bundle $bundlePath `
  --project-root (Get-Location)
```

成功结果应满足：

```json
{
  "valid": true,
  "sample_count": 100,
  "checks": {
    "postgres_revision": true,
    "postgres_table_counts": true,
    "postgres_fingerprint": true,
    "qdrant_green": true,
    "qdrant_exact_count": true,
    "qdrant_dense_config": true,
    "qdrant_sparse_config": true,
    "qdrant_payload_indexes": true,
    "qdrant_version": true,
    "fastembed": true,
    "runtime_bm25": true,
    "verification_samples": true
  }
}
```

只要任一检查为 `false`，就不要开始 QA。

## 9. 运行第一个问题

```powershell
.\.venv\Scripts\panda-qa.exe ask "Where is PndPidCorrelator defined?"
```

也可以使用 Python 模块入口：

```powershell
.\.venv\Scripts\python.exe -m panda_agent.cli.qa ask "How is event_poca used?"
```

正常返回是 JSON，主要字段包括：

- `status`：`answered`、`insufficient_evidence` 或 `version_conflict`；
- `answer`：带 Evidence 引用的回答；
- `claims`：原子结论及对应 Evidence ID；
- `evidence`：源码、论文或网页证据；
- `resolved_versions`：本次使用的锁定版本；
- `verification_errors`：最终验证错误，正常回答通常为空列表。

建议首先运行以下 smoke questions：

```powershell
.\.venv\Scripts\panda-qa.exe ask "How is event_poca used?"
.\.venv\Scripts\panda-qa.exe ask "Where is PndPidCorrelator defined?"
.\.venv\Scripts\panda-qa.exe ask "What inputs and outputs connect the target generator to the RestgasDetermination analysis?"
```

## 10. 停止和重新启动

停止服务但保留恢复数据：

```powershell
$env:COMPOSE_PROJECT_NAME = 'panda_qa_bundle'
docker compose stop
```

以后重新启动同一知识库：

```powershell
$env:COMPOSE_PROJECT_NAME = 'panda_qa_bundle'
docker compose up -d --wait postgres qdrant
.\.venv\Scripts\panda-qa-kb.exe verify --bundle $bundlePath --project-root (Get-Location)
```

> **破坏性操作：** `docker compose down -v` 会删除恢复后的 PostgreSQL/Qdrant volumes。只有明确准备丢弃这个具名、隔离环境时才可以执行。

## 11. 常见问题

### `postgres_target_not_empty` 或 `knowledge_objects table` 已存在

当前 Compose project 已经初始化或恢复过。确认 `COMPOSE_PROJECT_NAME`，然后使用一个新的具名、空环境。不要覆盖已有数据库。

### Qdrant collection 已存在

当前 Qdrant volume 不是空目标。换用新的 Compose project，或仅在明确允许丢弃旧测试数据时删除对应隔离 volumes。

### Bundle hash mismatch

Bundle 文件损坏或不属于该 manifest。停止恢复并重新取得完整 Bundle；不要修改 manifest 来绕过检查。

### `runtime asset destination already exists`

`data/runtime/fastembed/bm25` 已存在。确认是否已经恢复过 Bundle。prototype 不支持覆盖或自动回滚。

### Docker Engine permission denied

确认 Docker Desktop 已启动，并在当前终端运行：

```powershell
docker version
docker compose version
```

如果普通终端可用而受限执行环境不可用，这是执行环境的 Docker named-pipe 权限问题，不代表 Bundle 损坏。

### ADC 或 Vertex 调用失败

先确认：

```powershell
gcloud auth application-default print-access-token
```

然后检查 `.env` 中的 `QA_GCP_PROJECT_ID`、`QA_VERTEX_LOCATION` 和模型 ID。不要把 access token 写入日志或文档。

### `verify` 通过，但 QA 找不到内容

确认 QA 使用的 `PANDA_DATABASE_URL`、`PANDA_QDRANT_URL` 和 `PANDA_QDRANT_COLLECTION` 与刚恢复的服务一致。不要运行 indexing 试图“修复”一个连接到错误实例的问题。

## 12. 新用户启动检查表

- [ ] 代码和 Bundle 均来自可信来源；
- [ ] Python 3.12 环境安装了 `.[qa]`；
- [ ] `.env` 中 PostgreSQL密码与 URL 一致；
- [ ] `inspect` 成功；
- [ ] 只启动了 PostgreSQL 和 Qdrant；
- [ ] `restore` 成功；
- [ ] `verify` 返回 `valid=true` 和 `sample_count=100`；
- [ ] ADC 与 Vertex 配置可用；
- [ ] 第一条 QA 返回结构化状态和 Evidence；
- [ ] 没有运行 parsing、ingestion、document embedding 或 indexing。

维护者实现细节、真实 round2 验收哈希和 prototype 非目标见 [KNOWLEDGE_BUNDLE_PROTOTYPE.md](KNOWLEDGE_BUNDLE_PROTOTYPE.md)。
