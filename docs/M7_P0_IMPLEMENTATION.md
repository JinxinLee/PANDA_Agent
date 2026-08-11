# M7 P0：本地运行时、QAService 与 Loopback API

> **状态（2026-08-11）：M7 P0 已实现，M7 overall 已通过。** 当前工作树已经有
> P0 的本地运行时注册、持久化审计、并发门控、统一 `QAService` 和 FastAPI
> loopback 边界；M7 P1 也已实现并完成确定性验证。四题真实 API smoke 已通过；M8
> 已解锁但尚未开始。逐题结果见 [`M7_OVERALL_RESULT.md`](M7_OVERALL_RESULT.md)。

本文只描述当前源码中的 M7 P0 行为。M6 的质量结果和历史运行记录仍以
[`QA_AGENT.md`](../QA_AGENT.md)、[`AGENT_GUIDE.md`](../AGENT_GUIDE.md) 和
[`docs/EVALUATION_STATUS.md`](EVALUATION_STATUS.md) 中带日期的记录为准；它们不因
P0 实现而自动变成通过。

当前验收口径按用户当前决定统一为：M6 视为达标；M7 P0+P1 已实现并完成确定性
验证，四道真实 API smoke 已通过，M7 overall PASS；M8 已解锁但尚未开始。本文不虚构
hidden acceptance 或尚未运行的 formal gate。

本文其余章节保留 P0 的历史边界和迁移记录；deadline/504、逐节点 timings、usage、
JSON lifecycle logging 和 readiness TTL 的当前实现见 [`M7_P1_IMPLEMENTATION.md`](M7_P1_IMPLEMENTATION.md)。

## 1. P0 的边界和代码入口

| 边界 | 当前实现 | 真实入口 |
|---|---|---|
| 知识 Bundle | 导出、检查、恢复、知识状态验证；验证不以 runtime receipt 为门槛 | `panda_agent.kb_bundle`、`panda_agent.cli.kb` |
| Runtime registration | 比较 Bundle manifest 与 live PostgreSQL/Qdrant/BM25/embedding 身份，并原子写入 receipt | `runtime.register_runtime()`、`runtime.verify_runtime()`、`panda-qa-runtime` |
| 请求服务 | 请求 ID、单进程门控、worker thread、`qa_runs` 生命周期和脱敏 trace | `service.QAService`、`service.QAServiceEnvelope` |
| HTTP 边界 | FastAPI app、readiness probe、请求校验、稳定错误 envelope | `api.create_app()`、`panda-qa-api` |
| Schema migration | `qa_runs` 的完成时间、耗时、intent、错误码、节点耗时和 model usage 列 | `migrations/versions/0005_qa_service_runtime.py` |

P0 只提供本地单进程服务。CLI 与 API 都通过 `QAService` 执行同一套 QA 语义；
API 不复制检索、证据验证或回答渲染逻辑。

## 2. 架构和身份边界

```text
PostgreSQL + Qdrant + Bundle runtime assets
          │
          ├─ panda-qa-kb verify       (knowledge contract)
          │        └─ runtime_status=not_registered 仍可 valid=true、exit 0
          │
          ├─ alembic upgrade head     (service migration 0005)
          │
          ├─ panda-qa-runtime register-runtime
          │        └─ data/runtime/runtime_identity.json (atomic receipt)
          │
          ├─ panda-qa-runtime verify  (independent readiness contract)
          │
          └─ panda-qa-api → FastAPI/Uvicorn → QAService → QAAgent
```

`panda-qa-kb verify` 只验证知识分发状态。它在没有
`data/runtime/runtime_identity.json` 时返回 `runtime_status=not_registered`，但只要
知识检查通过仍返回 `valid=true`，因此不会把“知识已恢复”和“服务可启动”混为一谈。

`register-runtime` 会重新读取 Bundle manifest 和 live 状态，要求以下身份一致：

- service revision `0005` 与 knowledge revision `0004`；
- PostgreSQL table counts/index fingerprint；
- Qdrant collection、dense/sparse config、payload indexes 和 point count；
- FastEmbed BM25 distribution、runtime BM25 检查；
- `gemini-embedding-2`、3072 dimensions，以及 Qdrant dense size。

检查全部通过后，`RuntimeIdentity` 以临时文件 + `os.replace` 原子写入
`data/runtime/runtime_identity.json`。receipt 只保存 corpus/bundle、存储、BM25 和
embedding 身份，不保存 prompt、evaluation receipt 或凭据。

`panda-qa-runtime verify` 独立读取 receipt，再对 PostgreSQL/Qdrant/BM25/embedding
做 live 对照；缺少 receipt 返回 `runtime_status=not_registered`，损坏 receipt 返回
`invalid_identity`，任一检查失败都以非零退出。

## 3. 新用户恢复、迁移、注册和启动

先在项目根目录复制 `.env.example` 为 `.env`，确认 PostgreSQL URL、Qdrant URL、
Bundle 路径和 Vertex/ADC 配置。安装 QA extra 后，严格按以下顺序执行；恢复目标应是
空的、隔离的 PostgreSQL/Qdrant 环境。

1. **只启动依赖服务：**

   ```powershell
   docker compose up -d --wait postgres qdrant
   ```

   P0 没有需要在恢复前启动的 Agent 应用容器。

2. **恢复 Bundle：**

   ```powershell
   panda-qa-kb restore --bundle <dir> --project-root (Get-Location)
   ```

3. **先做知识验证：**

   ```powershell
   panda-qa-kb verify --bundle <dir> --project-root (Get-Location)
   ```

   这一步在注册前应显示 `runtime_status=not_registered`；只要其知识 checks 全部
   通过，命令仍以 exit 0 结束。不要因为该状态再次 restore 或运行 indexing。

4. **应用服务迁移：**

   ```powershell
   python -m alembic upgrade head
   ```

   `0005` 为服务层迁移，不改变 Bundle 的 knowledge revision `0004`，只为
   `qa_runs` 增加 P0 审计字段。

5. **注册 live runtime：**

   ```powershell
   panda-qa-runtime register-runtime --bundle <dir> --project-root (Get-Location)
   ```

6. **独立验证 runtime：**

   ```powershell
   panda-qa-runtime verify --project-root (Get-Location)
   ```

   只有这一步返回 `valid=true`、`runtime_status=registered` 后，API 才会进入
   ready 状态。

7. **启动 API：**

   ```powershell
   panda-qa-api --project-root (Get-Location)
   ```

   默认监听 `127.0.0.1:8000`，并固定 `workers=1`。`--host` 只接受
   `localhost`、IPv4 loopback 或 IPv6 `::1`；`0.0.0.0` 和局域网地址会被拒绝。

## 4. HTTP 请求和响应契约

### 4.1 路由

| 方法和路径 | 行为 |
|---|---|
| `GET /health/live` | 只表示进程存活，返回 `200 {"status":"live"}`；不调用模型。 |
| `GET /health/ready` | 按 `PANDA_READINESS_TTL_SECONDS`（默认 5 秒）缓存 runtime probe；ready 返回 200，未注册、ADC/存储不满足或服务初始化失败返回 503。无模型调用。 |
| `GET /version` | 返回 package/model IDs、Prompt set、retrieval policy schema 和 runtime receipt 摘要。 |
| `POST /v1/qa` | 统一 QA 请求边界；成功返回 `request_id`、`result` 和 `timings_ms.total`。 |
| `GET /docs`、`GET /openapi.json` | FastAPI 生成的本地交互文档和 schema。 |

`POST /v1/qa` 的 JSON body 只有 `question` 字段；首尾空白会去除，长度必须为
1–10,000（含边界），额外字段会得到 FastAPI/Pydantic 的 422。`result.status` 是
领域结果（例如 `answered`、`insufficient_evidence`、`version_conflict`），领域拒答
仍是 HTTP 200；传输或基础设施失败使用稳定错误 envelope：

| HTTP | `error_code` 示例 | 含义 |
|---:|---|---|
| 422 | validation error | body/schema 或 question 长度不合法。 |
| 429 | `busy` | 进程内 gate 已被另一个请求占用。 |
| 503 | `service_unavailable` | readiness probe 未通过；请求不会进入 QA graph。 |
| 500 | `persistence_error`、`execution_error`、`internal_error` | 记录、worker 或未知内部错误；不返回 stack。 |
| 504 | `deadline_exceeded` | M7 P1 deadline 到期；worker 可能仍在运行，客户端终态已锁存。 |

本节的 route/error 表最初是 P0 边界记录；当前 M7 P1 已增加 `504 deadline_exceeded`、
model usage、逐节点 timings、JSON lifecycle logging 和 readiness TTL，完整契约见
[`M7_P1_IMPLEMENTATION.md`](M7_P1_IMPLEMENTATION.md)。P0 历史记录不应被解释为当前
源码仍缺少这些能力，也不构成 M7 overall smoke 结果。

### 4.2 QAService、并发和审计

`QAService.execute()` 为每个请求生成 UUID request ID；该 API `request_id` 映射到
`qa_runs.run_id`（当前 schema 没有独立的 `request_id` 列）。服务先写入 `qa_runs` 的完整
`question` 和 `running` 状态，再在 worker thread 中调用 `QAAgent.run_detailed()`；
完成或失败后更新 status、completed_at、duration_ms、intent、error_code、
node_timings、model_usage 和 trace；当前 P1 会按四项白名单记录 model usage。CLI
`panda-qa ask` 与 API 都使用这个服务边界。

默认 `PANDA_API_MAX_CONCURRENCY=1`。gate 是进程内 `threading.BoundedSemaphore`，
同一进程的第二个同时请求立即得到 429；它不跨进程、不替代分布式队列或租户隔离。

`qa_runs.trace` 只允许 schema version、origin、selected evidence IDs、计数器、
脱敏 verification error codes、worker 时间和 cleanup status。它不保存 Prompt 正文、
Evidence 正文、凭据或 stack trace；完整 `question` 只保存在 `qa_runs.question`。
当前 P1 还写入逐节点 `node_timings` 和四项 usage 白名单
(`model_calls`、`token_usage`、`generation_calls`、`embedding_calls`)；deadline 时
客户端锁存的 `status/error_code/completed_at/duration_ms` 不会被 worker cleanup 改写。

## 5. 限制、非目标和 M7 状态

- P0 是 loopback-only、本地单进程服务，没有认证、TLS、租户隔离或跨进程并发协调；
  P1 deadline/usage/logging/TTL 已在同一边界内实现。
- P0 API 没有 Web UI；M8 尚未开始（因此 UI 尚未实现）。
- P0 没有多轮对话、长期 Memory、LangGraph checkpoint、Coding/Debug Agent 或工具调用。
- QA 仍需要 Vertex dense query embedding 和回答生成；Bundle verify/registration 不
  代替模型调用，也不提供离线 dense-query fallback。
- 四题真实 API smoke 已通过；P0/P1 deterministic tests、`compileall`、`pip check`
  和 offline Alembic SQL 也已完成。逐题 live 记录见 [`M7_OVERALL_RESULT.md`](M7_OVERALL_RESULT.md)。

因此，**“M7 P0 implemented” 表示 P0 基础代码路径已经落地；本轮四题 live smoke
已使 M7 overall 通过，但不表示 API 已完成生产部署。M8 已解锁但尚未开始。** 后续
M8/P2 结果应追加到带日期的实施或评估记录，不要改写历史 M6 结果。

## 6. 阅读和验证入口

### 6.1 当前本地证据

当前 assembled v2 Bundle 的本地记录（不调用模型、不提交 QA question）为：

- 补装 evaluator asset 后，`panda-qa-kb verify --bundle <dir>` 返回
  `valid=true`、`runtime_status=not_registered`，并以 exit 0 结束；
- `python -m alembic upgrade head` 将数据库从 `0004` 成功迁移到 `0005`；
- `panda-qa-runtime register-runtime --bundle <dir>` 成功写入 receipt，registration
  checks 全部为 `true`；随后 `panda-qa-runtime verify` 返回
  `valid=true`、`runtime_status=registered`，所有 live checks 全部为 `true`；
- 非沙箱 runtime probe 的 ADC check 为 `true`；调用 `load_dotenv()` 后，真实 FastAPI
  `/health/live`、`/health/ready`、`/version` 分别返回 HTTP `200/200/200`；
- 上述 API 健康验证之外，四题真实 `/v1/qa` smoke 已完成并通过；完整请求 ID、状态、
  model usage 和脱敏 trace 检查见 [`M7_OVERALL_RESULT.md`](M7_OVERALL_RESULT.md)。

新用户先读本文件第 3 节和 [`docs/NEW_USER_BUNDLE_GUIDE.md`](NEW_USER_BUNDLE_GUIDE.md)，
然后看 [`README.md`](../README.md) 的 quickstart。架构/实现阅读顺序为：

1. `src/panda_agent/cli/kb.py` → `src/panda_agent/kb_bundle.py`；
2. `src/panda_agent/runtime.py` 和 `src/panda_agent/cli/runtime.py`；
3. `src/panda_agent/service.py`；
4. `src/panda_agent/api.py` 和 `src/panda_agent/cli/api.py`；
5. `migrations/versions/0005_qa_service_runtime.py` 与 `tests/unit/test_runtime.py`、
   `tests/unit/test_service.py`、`tests/unit/test_api.py`。

P0 的最小离线检查命令：

```powershell
python -m unittest discover -s tests/unit -p "test_*.py" -v
python -m compileall -q src tests/unit
python -m pip check
```

这些命令不启动 PostgreSQL/Qdrant、不调用 Vertex；真实 Bundle smoke 和 M7 overall
gate 必须单独记录运行态、模型、题目和时间，不能用本节离线检查替代。P1 的针对性
确定性检查入口与边界见 [`M7_P1_IMPLEMENTATION.md`](M7_P1_IMPLEMENTATION.md)。
