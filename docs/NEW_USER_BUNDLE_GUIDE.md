# PANDA QA Agent 新用户 Bundle 使用指南

本指南面向只获得以下两项内容的新用户：

1. `PANDA_Agent` 代码；
2. 维护者预先生成的 PANDA Knowledge Bundle。

按照本指南启动时，不需要重新下载或解析论文、网页和代码仓库，也不需要生成文档向量或重建索引。首次启动只恢复 PostgreSQL、Qdrant、本地 BM25 运行资产和 evaluator lookup catalog。

> **适用边界：** 当前实现是可信本地 Bundle prototype。Bundle 没有数字签名、在线下载、多版本切换、自动回滚或公开分发安全机制。只使用来自可信维护者的 Bundle。

本文同时支持 Windows 10/11（PowerShell）、macOS（Bash/zsh）和 Linux（Bash）。
Windows 命令保留在原有小节中；macOS/Linux 使用紧随其后的 Bash/zsh 小节。
三种平台都需要 Python 3.12 或更高版本、Docker Compose v2，以及可用的 Google
Cloud Application Default Credentials（ADC）。

## 0. 获取与代码版本匹配的 Bundle

当前 `main` 分支使用：

```text
panda-knowledge-bundle/v2
```

v2 Bundle 必须由维护者完整提供，并至少包含：

```text
panda-kb-bundle-v2/
├── bundle_manifest.json
├── postgres.dump
├── qdrant.snapshot
├── evaluator/
│   └── evaluator_lookup_catalog.json
└── runtime_assets/
    └── fastembed/
        └── bm25/
```

`evaluator_lookup_catalog.json` 是 v2 新增的正式运行资产。它保存与 normalized
KnowledgeObject 等价的完整 evaluator lookup，使恢复环境不需要
`data/normalized/*/knowledge_objects.jsonl` 也能执行 Gold selector 验证和迁移后评估。

当前文档不假设固定的 v2 下载地址；拿到 Bundle 后应以目录中的
`bundle_manifest.json` 为唯一 artifact 清单，并先执行 `inspect`。如果只有下面的历史
v1 Release，请使用对应 tag，而不是当前 `main`。

> **版本兼容性：** Bundle schema 必须与代码匹配。当前 `main` 不接受缺少 evaluator
> catalog 的 v1 manifest，也不能把 v1 的 manifest、dump、snapshot 与 v2 catalog
> 混合使用。`panda-qa-kb inspect` 会在连接数据库前拒绝这种组合。

### 0.1 历史 v1.0.0 Release（仅与对应 tag 配套）

以下公开 Release 是历史 v1 Bundle，只能与 Git tag
`panda-kb-prototype-v1.0.0` 对应的代码配套使用，不能直接用于当前 `main`：

[PANDA Knowledge Bundle Prototype v1.0.0](https://github.com/JinxinLee/PANDA_Agent/releases/tag/panda-kb-prototype-v1.0.0)

在 Release 页面下载下面四个资产，并放入同一个本地目录：

| 文件 | 用途 | 大小 |
|---|---|---:|
| `bundle_manifest.json` | Bundle schema、语料身份、数据库/向量库配置和 SHA-256 清单 | 27,235 B |
| `postgres.dump` | 预构建 PostgreSQL 知识库 | 70,915,643 B |
| `qdrant.snapshot` | `panda_knowledge_v1` Qdrant 向量索引快照 | 1,269,908,992 B |
| `fastembed-runtime.zip` | 本地 BM25 runtime 资产 | 13,162 B |

例如，下载后目录暂时应为：

```text
D:\panda-bundles\panda-kb-prototype-v1.0.0\
├── bundle_manifest.json
├── postgres.dump
├── qdrant.snapshot
└── fastembed-runtime.zip
```

macOS/Linux 的目录示例：

```text
$HOME/panda-bundles/panda-kb-prototype-v1.0.0/
├── bundle_manifest.json
├── postgres.dump
├── qdrant.snapshot
└── fastembed-runtime.zip
```

也可以使用 GitHub CLI 下载 Release 资产（浏览器下载同样适用）：

```bash
mkdir -p "$HOME/panda-bundles/panda-kb-prototype-v1.0.0"
gh release download panda-kb-prototype-v1.0.0 \
  --repo JinxinLee/PANDA_Agent \
  --dir "$HOME/panda-bundles/panda-kb-prototype-v1.0.0" \
  --pattern 'bundle_manifest.json' \
  --pattern 'postgres.dump' \
  --pattern 'qdrant.snapshot' \
  --pattern 'fastembed-runtime.zip'
```

Windows PowerShell：

```powershell
$bundlePath = 'D:\panda-bundles\panda-kb-prototype-v1.0.0'
New-Item -ItemType Directory -Force $bundlePath | Out-Null
gh release download panda-kb-prototype-v1.0.0 `
  --repo JinxinLee/PANDA_Agent `
  --dir $bundlePath `
  --pattern 'bundle_manifest.json' `
  --pattern 'postgres.dump' `
  --pattern 'qdrant.snapshot' `
  --pattern 'fastembed-runtime.zip'
```

如果使用浏览器下载，直接把四个资产保存到同一个 Bundle 目录即可。

`fastembed-runtime.zip` 不能直接保留为压缩包而跳过解压。必须在 Bundle 根目录执行：

Windows PowerShell：

```powershell
$bundlePath = (Resolve-Path 'D:\panda-bundles\panda-kb-prototype-v1.0.0').Path
Expand-Archive `
  -LiteralPath (Join-Path $bundlePath 'fastembed-runtime.zip') `
  -DestinationPath $bundlePath `
  -Force
```

解压后应确认目录存在：

```text
D:\panda-bundles\panda-kb-prototype-v1.0.0\
└── runtime_assets\
    └── fastembed\
        └── bm25\
```

macOS/Linux：

Release 中的 zip 资产包含 Windows 风格的反斜杠路径。某些 macOS/Linux `unzip`
版本会把它们当作普通字符，产生不可读的目录；建议使用下面的路径规范化解压脚本：

```bash
export BUNDLE_PATH="$HOME/panda-bundles/panda-kb-prototype-v1.0.0"
# 如果之前尝试过 unzip 并出现 warning 或 Permission denied，先清理不完整目录。
rm -rf "$BUNDLE_PATH/runtime_assets"
python3 - "$BUNDLE_PATH/fastembed-runtime.zip" "$BUNDLE_PATH" <<'PY'
from pathlib import Path
import sys
import zipfile

archive = Path(sys.argv[1])
destination = Path(sys.argv[2]).resolve()
with zipfile.ZipFile(archive) as bundle:
    for item in bundle.infolist():
        relative = item.filename.replace("\\", "/").lstrip("/")
        if not relative or relative.endswith("/"):
            continue
        target = (destination / relative).resolve()
        if not target.is_relative_to(destination):
            raise SystemExit(f"unsafe archive path: {item.filename}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bundle.read(item))
        target.chmod(0o644)
PY
```

解压后确认 `$BUNDLE_PATH/runtime_assets/fastembed/bm25/` 存在。
脚本会重新创建带有执行权限的目录，并将运行时文件设置为可读；不要继续使用之前
由 macOS `unzip` 生成的权限异常目录。

最终 Bundle 目录必须同时包含 `bundle_manifest.json`、`postgres.dump`、
`qdrant.snapshot` 和 `runtime_assets/fastembed/bm25/`。仅下载前三个文件，或只保留
`fastembed-runtime.zip` 而不解压，都会导致 `inspect` 失败。

本次 Release 的关键 SHA-256 如下；`inspect` 会再次根据 manifest 自动检查前两个大文件：

```text
postgres.dump     aadff5c1397317544160c6472d84e91994f7613466558116f589ef57bba21c64
qdrant.snapshot   da592bb445f83d7ce7ee87e9e669831faa27b0f85942753719146bb81d1928c1
```

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
├── evaluator/
│   └── evaluator_lookup_catalog.json
└── runtime_assets/
    └── fastembed/
        └── bm25/
```

缺少任一 Bundle 文件时不要执行恢复。对于当前 `main`，缺少
`evaluator/evaluator_lookup_catalog.json` 也属于不完整 Bundle。

如果目录中还保留 `fastembed-runtime.zip`，这是允许的；恢复程序只使用已经解压的
`runtime_assets/fastembed/bm25/`。不要把 `fastembed-runtime.zip` 解压到额外的嵌套目录，
例如 `runtime_assets/runtime_assets/fastembed/bm25/`，否则运行时路径无法匹配。

## 2. 前置条件

- Windows 10/11、PowerShell 和 Docker Desktop；
- macOS、Bash/zsh 和 Docker Desktop 或 Colima；
- Linux、Bash 和 Docker Engine + Docker Compose v2（当前用户必须能访问 Docker daemon）；
- Python 3.12 或更高版本；
- `docker compose version` 可正常执行；
- QA 阶段需要可以调用 Vertex AI 的 Google Cloud 项目和 Application Default Credentials（ADC）；
- 建议至少预留 5 GB 可用磁盘空间，用于 Bundle、数据库和 Qdrant 恢复数据。

> **注意：** `inspect`、`restore` 和 `verify` 不需要 Vertex。只有最终 QA 查询需要 Vertex，因为 dense query embedding 和回答生成仍由 Vertex 完成。

## 3. 创建 Python 环境

进入 `PANDA_Agent` 项目根目录：

Windows PowerShell：

```powershell
Set-Location C:\path\to\PANDA_Agent
```

创建项目本地虚拟环境并只安装 QA 运行依赖：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[qa]"
```

macOS/Linux（Bash/zsh）：

```bash
cd /path/to/PANDA_Agent
python3 --version  # 必须是 3.12 或更高版本
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[qa]'
```

不需要安装 `ingestion` extra，也不要运行：

```text
panda-qa-source
panda-qa-ingest
panda-qa-index apply
panda-qa-index resume
```

## 4. 配置本地服务和 Vertex

Windows PowerShell：

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

macOS/Linux：

```bash
cp .env.example .env
${EDITOR:-vi} .env
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
COMPOSE_PROJECT_NAME=panda_qa_bundle
```

`PANDA_POSTGRES_PASSWORD` 与 `PANDA_DATABASE_URL` 中的密码必须一致。不要提交 `.env`。

在运行 QA 前配置 ADC（所有平台）：

```console
gcloud auth application-default login
```

`docker compose` 会自动读取项目根目录的 `.env`；Python CLI 也会自动加载它。
只有直接运行 `alembic` 或其他原始脚本时，才需要在 Bash 中先执行
`set -a; source .env; set +a`。

如果组织使用其他 ADC 配置方式，请遵循组织的 Google Cloud 权限策略；不要把凭据文件复制进仓库。

## 5. 在恢复前检查 Bundle

将 Bundle 放在任意本地目录，并解析为绝对路径：

Windows PowerShell：

```powershell
$bundlePath = (Resolve-Path 'D:\panda-bundles\panda-kb-v2').Path
```

执行本地完整性检查：

```powershell
.\.venv\Scripts\panda-qa-kb.exe inspect --bundle $bundlePath
```

macOS/Linux：

```bash
export BUNDLE_PATH="$(cd "$HOME/panda-bundles/panda-kb-v2" && pwd)"
.venv/bin/panda-qa-kb inspect --bundle "$BUNDLE_PATH"
```

`inspect` 会验证 manifest schema、PostgreSQL/Qdrant artifact 的文件大小与
SHA-256、本地 BM25 资产，以及 evaluator catalog 的 schema、完整对象数和 canonical
SHA-256。它不会连接数据库、Qdrant 或 Vertex。

如果出现 hash mismatch、文件缺失或 manifest 校验失败，应停止并重新获取可信 Bundle，不要继续恢复。

## 6. 启动空的 PostgreSQL 和 Qdrant

为本次恢复设置一个固定的 Compose project 名称：

Windows PowerShell：

```powershell
$env:COMPOSE_PROJECT_NAME = 'panda_qa_bundle'
docker compose up -d --wait postgres qdrant
docker compose ps
```

macOS/Linux：

```bash
export COMPOSE_PROJECT_NAME=panda_qa_bundle
docker compose up -d --wait postgres qdrant
docker compose ps
```

只启动 `postgres` 和 `qdrant`。当前项目没有需要在恢复前启动的 Agent 应用容器。

恢复要求：

- PostgreSQL 中不存在 `knowledge_objects` 表；
- Qdrant 中不存在 `panda_knowledge_v1` collection；
- 项目中不存在 `data/runtime/fastembed/bm25`。
- 项目中不存在 `data/runtime/evaluator/evaluator_lookup_catalog.json`。

如果目标不是空的，`restore` 会拒绝继续。不要使用强制覆盖。

## 7. 恢复预构建知识库

在保持相同终端会话和 `COMPOSE_PROJECT_NAME` 的情况下执行：

Windows PowerShell：

```powershell
.\.venv\Scripts\panda-qa-kb.exe restore `
  --bundle $bundlePath `
  --project-root (Get-Location)
```

macOS/Linux：

```bash
.venv/bin/panda-qa-kb restore \
  --bundle "$BUNDLE_PATH" \
  --project-root "$PWD"
```

恢复过程会依次：

1. 再次执行 manifest 和 SHA-256 preflight；
2. 检查 PostgreSQL/Qdrant 目标为空；
3. 使用单事务和 `--exit-on-error` 恢复 PostgreSQL；
4. 上传并恢复 Qdrant snapshot；
5. 安装 `data/runtime/fastembed/bm25`；
6. 安装 `data/runtime/evaluator/evaluator_lookup_catalog.json`；
7. 写入 `data/runtime/installed_bundle.json`。

prototype 没有跨 PostgreSQL/Qdrant 的分布式事务。如果 PostgreSQL 恢复成功而后续步骤失败，不要直接重复恢复；保留错误输出并在隔离环境中重新建立空目标。

## 8. 验证恢复结果

Windows PowerShell：

```powershell
.\.venv\Scripts\panda-qa-kb.exe verify `
  --bundle $bundlePath `
  --project-root (Get-Location)
```

macOS/Linux：

```bash
.venv/bin/panda-qa-kb verify \
  --bundle "$BUNDLE_PATH" \
  --project-root "$PWD"
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
    "verification_samples": true,
    "evaluator_catalog_round_trip": true,
    "gold_selector": true
  }
}
```

只要任一检查为 `false`，就不要开始 QA。

其中：

- `evaluator_catalog_round_trip` 证明恢复后的 catalog 与 Bundle manifest 中的
  schema、lookup contract、对象数和 SHA-256 一致；
- `gold_selector` 证明当前代码中的签署 Gold 与 Bundle 记录的 Gold hash 一致，且所有
  selector 可以用 portable catalog 完成确定性验证。

## 9. 运行第一个问题

Windows PowerShell：

```powershell
.\.venv\Scripts\panda-qa.exe ask "Where is PndPidCorrelator defined?"
```

macOS/Linux：

```bash
.venv/bin/panda-qa ask "Where is PndPidCorrelator defined?"
```

也可以使用 Python 模块入口：

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m panda_agent.cli.qa ask "How is event_poca used?"
```

macOS/Linux：

```bash
.venv/bin/python -m panda_agent.cli.qa ask "How is event_poca used?"
```

正常返回是 JSON，主要字段包括：

- `status`：`answered`、`insufficient_evidence` 或 `version_conflict`；
- `answer`：带 Evidence 引用的回答；
- `claims`：原子结论及对应 Evidence ID；
- `evidence`：源码、论文或网页证据；
- `resolved_versions`：本次使用的锁定版本；
- `verification_errors`：最终验证错误，正常回答通常为空列表。

建议首先运行以下 smoke questions：

Windows PowerShell：

```powershell
.\.venv\Scripts\panda-qa.exe ask "How is event_poca used?"
.\.venv\Scripts\panda-qa.exe ask "Where is PndPidCorrelator defined?"
.\.venv\Scripts\panda-qa.exe ask "What inputs and outputs connect the target generator to the RestgasDetermination analysis?"
```

macOS/Linux：

```bash
.venv/bin/panda-qa ask "How is event_poca used?"
.venv/bin/panda-qa ask "Where is PndPidCorrelator defined?"
.venv/bin/panda-qa ask "What inputs and outputs connect the target generator to the RestgasDetermination analysis?"
```

## 9.1 可选：执行迁移后等价性验收

普通新用户完成 `verify` 和三道 smoke question 即可使用 Agent。若你同时保留迁移前
原始运行态和恢复后的运行态，可以使用冻结的 10 题迁移集进一步区分：

1. PostgreSQL/Qdrant 是否等价；
2. portable evaluator catalog 是否与原 normalized lookup 等价；
3. QA 差异是 Bundle 迁移造成，还是模型 planning/reranking 的正常波动。

先验证冻结测试集与 Gold v2.6 的身份：

Windows PowerShell：

```powershell
.\.venv\Scripts\panda-qa-migration.exe `
  --project-root (Get-Location) validate-suite `
  --suite evaluation\migration\v1\suite.json `
  --canonical-gold evaluation\benchmarks\v2_6\gold_questions.yaml
```

macOS/Linux：

```bash
.venv/bin/panda-qa-migration \
  --project-root "$PWD" validate-suite \
  --suite evaluation/migration/v1/suite.json \
  --canonical-gold evaluation/benchmarks/v2_6/gold_questions.yaml
```

完整流程依次执行 deterministic replay、evaluator lookup A/B 和两组各 10 题的 QA
A/B。前两层新增模型调用为 0；只有 live capture 和 QA A/B 会调用 Vertex。不要把它
扩展成完整 80 题或 16 题 benchmark，也不要因为一次模型证据选择差异而重新 indexing。

命令、门禁、报告字段和本次实测结果见
[KNOWLEDGE_BUNDLE_MIGRATION_EVALUATION.md](KNOWLEDGE_BUNDLE_MIGRATION_EVALUATION.md)。
本次结果为 `runtime_equivalent_but_model_variance_observed`：10/10 replay 和 evaluator
selector parity 通过，两侧 QA 均 10/10 无异常，没有检测到迁移特有的 safety failure
或相对退化。

## 10. 停止和重新启动

停止服务但保留恢复数据：

Windows PowerShell：

```powershell
$env:COMPOSE_PROJECT_NAME = 'panda_qa_bundle'
docker compose stop
```

macOS/Linux：

```bash
export COMPOSE_PROJECT_NAME=panda_qa_bundle
docker compose stop
```

以后重新启动同一知识库：

Windows PowerShell：

```powershell
$env:COMPOSE_PROJECT_NAME = 'panda_qa_bundle'
docker compose up -d --wait postgres qdrant
.\.venv\Scripts\panda-qa-kb.exe verify --bundle $bundlePath --project-root (Get-Location)
```

macOS/Linux：

```bash
export COMPOSE_PROJECT_NAME=panda_qa_bundle
docker compose up -d --wait postgres qdrant
.venv/bin/panda-qa-kb verify --bundle "$BUNDLE_PATH" --project-root "$PWD"
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

### `evaluator catalog destination already exists`

`data/runtime/evaluator/evaluator_lookup_catalog.json` 已存在。确认当前目录是否已经恢复过
Bundle；不要手工覆盖 catalog，也不要把另一个 Bundle 的 catalog 复制到当前运行态。

### `evaluator_catalog_round_trip` 或 `gold_selector` 为 `false`

前者表示安装后的 evaluator catalog 与 manifest identity 不一致；后者通常表示代码中的
Gold 版本/hash 与 Bundle 不匹配，或 selector 无法在 catalog 中解析。确认代码 checkout
与 Bundle schema/version 配套，不要通过修改 manifest 或 Gold 绕过检查。

### Docker Engine permission denied

Windows PowerShell/macOS：确认 Docker Desktop 已启动（macOS 也可使用 Colima），并在当前终端运行：

```console
docker version
docker compose version
```

Linux：确认 Docker Engine 正在运行，且当前用户可以访问 Docker daemon，然后运行同样的两条命令。

如果普通终端可用而受限执行环境不可用，这是执行环境的 Docker named-pipe 权限问题，不代表 Bundle 损坏。

### ADC 或 Vertex 调用失败

所有平台先确认：

```console
gcloud auth application-default print-access-token
```

然后检查 `.env` 中的 `QA_GCP_PROJECT_ID`、`QA_VERTEX_LOCATION` 和模型 ID。不要把 access token 写入日志或文档。

### `verify` 通过，但 QA 找不到内容

确认 QA 使用的 `PANDA_DATABASE_URL`、`PANDA_QDRANT_URL` 和 `PANDA_QDRANT_COLLECTION` 与刚恢复的服务一致。不要运行 indexing 试图“修复”一个连接到错误实例的问题。

## 12. 新用户启动检查表

- [ ] 代码和 Bundle 均来自可信来源；
- [ ] Docker Desktop/Colima（macOS）或 Docker Engine（Linux）可用；
- [ ] Python 3.12 环境安装了 `.[qa]`；
- [ ] `.env` 中 PostgreSQL密码与 URL 一致；
- [ ] `inspect` 成功；
- [ ] 只启动了 PostgreSQL 和 Qdrant；
- [ ] `restore` 成功；
- [ ] `verify` 返回 `valid=true` 和 `sample_count=100`；
- [ ] `evaluator_catalog_round_trip=true`；
- [ ] `gold_selector=true`；
- [ ] ADC 与 Vertex 配置可用；
- [ ] 第一条 QA 返回结构化状态和 Evidence；
- [ ] 没有运行 parsing、ingestion、document embedding 或 indexing。

维护者实现细节、真实 round2 验收哈希和 prototype 非目标见
[KNOWLEDGE_BUNDLE_PROTOTYPE.md](KNOWLEDGE_BUNDLE_PROTOTYPE.md)。迁移等价性测试集、
deterministic replay、evaluator A/B 和 QA 对比报告见
[KNOWLEDGE_BUNDLE_MIGRATION_EVALUATION.md](KNOWLEDGE_BUNDLE_MIGRATION_EVALUATION.md)。
