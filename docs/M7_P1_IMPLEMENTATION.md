# M7 P1：请求 deadline、运行观测与 readiness 缓存

> **状态（2026-08-11）：已实现并完成确定性验证；M7 overall 已通过。**
> M6 按当前验收决定视为达标；M7 P0+P1 的本地代码路径和离线测试已完成，
> 四道真实 API smoke 已通过，因此 M7 PASS。M8 已解锁但尚未开始；逐题 live 记录见
> [`M7_OVERALL_RESULT.md`](M7_OVERALL_RESULT.md)。

本文描述当前源码中的 M7 P1 行为。P0 的运行时注册、Bundle 恢复和 loopback
API 基础契约见 [`M7_P0_IMPLEMENTATION.md`](M7_P0_IMPLEMENTATION.md)；旧 P0 文档中的
缺口说明只代表当时的历史边界，不代表当前源码。

## 1. 架构和入口

P1 不另起服务：`panda-qa-api` 仍由 FastAPI `create_app()` 创建一次
`QAService`，CLI/API 共用 `QAService.execute()`。请求在进程内
`threading.BoundedSemaphore` gate 后启动一个 worker thread；`QAAgent.run_detailed()`
返回结果、逐节点耗时和模型计数，服务层负责 `qa_runs` 持久化及安全日志。

主要入口：

- `src/panda_agent/api.py`：环境变量、readiness TTL、`POST /v1/qa` 504 映射；
- `src/panda_agent/service.py`：deadline 状态机、`qa_runs` 锁存/清理、JSON 生命周期日志；
- `src/panda_agent/qa.py`：`node_timings_ms` 和四项 `model_usage` 计数；
- `src/panda_agent/cli/api.py`：`PANDA_LOG_LEVEL` 配置白名单日志输出；
- `migrations/versions/0005_qa_service_runtime.py`：`qa_runs` 审计列。

## 2. 配置

| 变量 | 默认值 | 约束/作用 |
|---|---:|---|
| `PANDA_QA_DEADLINE_SECONDS` | `300` | 必须为有限正数；API 将同值传给 `QAService`。 |
| `PANDA_READINESS_TTL_SECONDS` | `5` | 必须为有限非负数；TTL 到期才重跑 runtime/ADC probe，`0` 禁用缓存、每次 probe。 |
| `PANDA_LOG_LEVEL` | `INFO` | Python logging level；由 `panda-qa-api` 配置 `panda_agent` logger。 |
| `PANDA_API_MAX_CONCURRENCY` | `1` | 进程内 gate；不提供跨进程协调。 |

Vertex、数据库和 Qdrant 变量仍见 [`.env.example`](../.env.example)。示例文件不含真实凭据。

## 3. Deadline 状态机和 HTTP 504

`QAService.execute()` 非阻塞获取 gate，写入 `qa_runs(status=running)` 后启动 worker，
并以 `thread.join(deadline_seconds)` 等待。worker 完成则正常写入终态；等待超时则：

1. 客户端侧立即写入一次不可变终态：`status=error`、`error_code=deadline_exceeded`、
   `completed_at=now()`、`duration_ms`、`node_timings={"workflow": duration_ms}`、
   `model_usage` 四键全为 0、`trace.cleanup_status=deadline_exceeded`；
2. API 将 `QAServiceDeadlineError` 映射为 HTTP **504**，JSON 为
   `{"request_id", "error_code":"deadline_exceeded", "message":"Request deadline exceeded"}`；
3. Python thread 不能被强制取消。worker 继续运行；退出后只补写
   `node_timings`、`model_usage` 和 `trace`（含 `worker_completed_at` 与
   `completed_after_deadline`/`execution_error_after_deadline`），不改写已锁存的
   `status`、`error_code`、`completed_at` 或 `duration_ms`；
4. worker 退出后 cleanup thread 才释放进程 gate。因此 timeout 后 gate 会保持占用，
   直到该 worker 退出；期间新请求仍可得到 429 `busy`。

持久化 cleanup 失败只记录 `cleanup_persistence_failed` 日志；不得把它伪装成新的
客户端终态或宣称强制取消。deadline 不是生产级任务取消或跨进程队列。

## 4. Timings、usage 和安全日志

- `QAAgent.run_detailed()` 返回 `node_timings_ms`（`retrieve`、`sufficiency`、
  `targeted_retrieve`、`answer`、`verify`、`revise`、`finalize`，以及总的 `workflow`）
  和 `model_usage`。
- usage 白名单固定为 `model_calls`、`token_usage`、`generation_calls`、
  `embedding_calls`；不写 prompt、response 正文或凭据。
- 生命周期日志为单行 JSON；允许 `request_id`、`origin`、`event`、`status`、可选
  `count`/`timing_ms`。问题正文、证据正文、模型内容、stack trace 和凭据不得出现。

生命周期事件包括 `rejected`/`started`/`terminal`，以及 deadline worker 的
`worker_cleanup` 或 `cleanup_persistence_failed`；这些事件只用于本地诊断，不构成
分布式 tracing 或成本计费系统。

## 5. Readiness TTL、运行和调试入口

`GET /health/ready` 和 `/v1/qa` 共用带 TTL 的 runtime probe；缓存有效期内复用
`app.state.ready`，TTL 到期再验证 receipt、存储和 ADC。`/health/live` 始终只表示进程
存活。`PANDA_READINESS_TTL_SECONDS=0` 时不缓存，每次 readiness/QA 请求都 probe。

从项目根目录运行（这些命令不包含网络或 Vertex smoke）：

```powershell
Copy-Item .env.example .env
python -m alembic upgrade head
panda-qa-runtime verify --project-root (Get-Location)
panda-qa-api --project-root (Get-Location)
```

调试时先看 `/health/live`、`/health/ready` 和 `/version`，再提交 `/v1/qa`；用
`PANDA_LOG_LEVEL=DEBUG` 临时提高 `panda_agent` logger 级别。不要把 question、Prompt、
Evidence 或凭据写入日志。Bundle 恢复、runtime 注册和 loopback host 限制仍遵循
[`M7_P0_IMPLEMENTATION.md`](M7_P0_IMPLEMENTATION.md)。

## 6. 限制、测试与未完成边界

P1 仍是 loopback、本地单进程实现：无认证/TLS/租户隔离、无跨进程 gate、无生产级
取消；M8 UI 和多轮 checkpoint 未开始。确定性聚焦入口包括：

```powershell
python -m unittest discover -s tests/unit -p "test_service.py" -v
python -m unittest discover -s tests/unit -p "test_api.py" -v
python -m unittest discover -s tests/unit -p "test_qa.py" -v
python -m unittest discover -s tests/unit -p "test_vertex.py" -v
python -m compileall -q src tests/unit
python -m pip check
```

控制器本轮聚焦结果为：`test_service.py` 13/13、`test_api.py` 13/13、
`test_qa.py` 38/38、`test_vertex.py` 8/8，共 **72/72**；`compileall` 与
`pip check` 也通过。上述聚焦验证不调用 Vertex 或网络；四道真实 API smoke 已另行通过，
故当前状态是 “M7 P0+P1 已实现并完成确定性验证，M7 overall PASS”。这仍不表示
生产级取消能力或远程多用户部署；边界和限制见 [`M7_OVERALL_RESULT.md`](M7_OVERALL_RESULT.md)。
