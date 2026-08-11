# M7 Overall 验收结果

**验收日期：** 2026-08-11  
**状态：** `M7 overall PASS`  
**后续状态：** `M8 unlocked but not started`

本文记录 M7 P0、P1 完成后的本机服务整体验收。M7 是一个单用户、单进程、
loopback-only 的 FastAPI 服务验收，不是公开部署或生产安全认证。

## 1. 验收范围与冻结门禁

本轮只验证以下内容：

1. 已恢复并注册的固定 Knowledge Bundle 能被 runtime readiness 正确识别；
2. `QAService`、FastAPI 路由、Vertex runtime 和 `qa_runs` 持久化能够组成完整请求链；
3. 四类代表性请求均能通过真实 `/v1/qa` 路径完成：正常回答、代码/API、
   证据不足拒答和版本冲突拒答；
4. 拒答和版本冲突属于正常领域结果，仍返回 HTTP 200；基础设施错误才使用 5xx/503，
   deadline 才使用 504。

本轮没有运行 M6 的 80 题开发集、16 题 regression、challenge 或 acceptance，
也没有开始 M8 Web UI。

## 2. P0/P1 确定性验收证据

在真实模型 smoke 之前，P0/P1 的本地确定性验证已经通过：

| 检查 | 结果 |
|---|---:|
| `tests/unit/test_service.py` | 13/13 |
| `tests/unit/test_api.py` | 13/13 |
| `tests/unit/test_qa.py` | 38/38 |
| `tests/unit/test_vertex.py` | 8/8 |
| P0/P1 聚焦测试合计 | **72/72** |
| `compileall` | 通过 |
| `pip check` | 通过 |
| `git diff --check` | 通过 |

这些测试覆盖了 runtime registration、QAService 状态机、并发 gate、HTTP schema、
deadline/504、逐节点 timings、model usage、JSON 日志和 readiness TTL。它们不替代
真实 Vertex 请求，因此还需要下面的 live smoke。

## 3. 真实四题 API smoke

四题均通过真实本机 FastAPI `/v1/qa` 路径执行，并使用当前锁定 runtime：

| Case | 预期领域结果 | HTTP | 实际结果 | 关键检查 |
|---|---|---:|---|---|
| `g090` | answered / data-flow | 200 | answered | 3 claims、3 evidence；`event_poca` 数据流、workflow 与代码/文档来源均可追溯 |
| `g027` | answered / code-API | 200 | answered | 3 claims、3 evidence；`PndTargetGenerator` 与锁定 PandaRoot/Restgas 代码证据一致 |
| `g041` | insufficient_evidence | 200 | insufficient_evidence | 对不存在的 API 符号拒答，没有编造 signature |
| `g042` | version_conflict | 200 | version_conflict | 正确拒绝未锁定的 `0123456789abcdef` commit，没有混入错误版本证据 |

请求记录 ID（用于 `qa_runs` 审计）：API 返回的 `request_id` 在当前数据库 schema 中
映射为 `qa_runs.run_id`；没有另设一个 `request_id` 数据库列。

- `g090`: `9067b1d1-100f-40f1-ba97-d3597278c0ce`
- `g027`: `d5627b51-f8cf-4bbc-8ff5-c6d4b99fde5a`
- `g041`: `5aeadc6e-0f42-4751-8480-7029e4165486`
- `g042`: `f2abf082-176a-46c8-8acd-e4c3ece1f20f`

所有请求均无 timeout、未处理异常或 wrong-version evidence。运行时使用
`gemini-3.6-flash` 生成模型和 `gemini-embedding-2` embedding，Prompt 版本为
`3.6.0`。本轮只验证 API wrapping 和运行链，不把四题结果扩展为完整 benchmark 指标。

## 4. Runtime、健康检查与持久化

- `panda-qa-runtime verify` 返回有效、已注册，Bundle、PostgreSQL、Qdrant、BM25 和
  embedding identity checks 全部通过。
- `/health/live`、`/health/ready`、`/version` 均返回 HTTP 200。
- `qa_runs` 回读确认每条记录的 `run_id` 与 API `request_id` 一致，并有
  `completed_at`、请求来源、正确 intent、节点 timings 和 model usage；当前 schema 没有
  独立的 `request_id` 列，正常请求的 `error_code` 为 `null`。
- 模型调用统计按请求持久化，四题分别为 `5/75244`、`5/107919`、`5/35213`、
  `3/18420`（调用次数/Token usage）。
- trace 只保留允许的诊断字段，不包含问题正文、完整 Prompt、完整回答、Evidence 正文、
  ADC 路径、凭据或异常堆栈。
- API 服务停止后，loopback 端口已释放，没有留下运行中的后台服务。

## 5. 安全与边界确认

当前 M7 仍严格限制为：

- 仅监听 `127.0.0.1`；
- 单用户、单进程、进程内并发上限；
- 无账户、API key、TLS、跨进程锁或远程访问；
- 无 session、多轮 Memory、LangGraph checkpoint 或服务端会话恢复；
- Python worker 超时后不能被强制取消，504 终态由服务锁存，worker 退出后再补写清理字段；
- 不提供代码写入、shell 执行、数据库管理或索引重建接口。

因此本结果只表示本机 prototype 的 M7 服务链通过验收，不能作为生产部署、公开分发
或多用户安全能力的证明。

## 6. 结论

M7 P0/P1 的确定性门禁和四题真实 API smoke 均已通过，故当前里程碑状态为：

```text
M7 overall PASS
M8 unlocked but not started
```

M8 可以在后续单独实施；其 UI 必须继续复用同一个 `QAService`，不能绕过本轮已经验收的
runtime、并发、诊断和安全边界。
