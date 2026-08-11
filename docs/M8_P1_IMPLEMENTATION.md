# M8 P1：诊断、浏览器验收与真实 UI smoke

> **状态（2026-08-11）：** `M8 P1 implemented and deterministically verified`。
> P0 的服务端渲染页面、共享服务和 loopback 边界在
> [`M8_P0_IMPLEMENTATION.md`](M8_P0_IMPLEMENTATION.md)；P0/P1 合并后的验收结论见
> [`M8_OVERALL_RESULT.md`](M8_OVERALL_RESULT.md)。当前里程碑为 **M8 overall PASS，M8 complete**。

本文只描述当前源码中已经存在的 M8 P1 行为。它不把本机 UI 说成公开部署，也不引入
多轮会话、账户、远程访问、上传、代码修改、命令执行或 Coding/Debug Agent。

## 1. 实施范围

M8 P1 在同一个 FastAPI `create_app()` 上完成了 P0 留下的诊断和浏览器验收边界：

- `GET /ui/health` 返回安全的运行状态 partial，页面启动时加载并每 30 秒刷新；
- `POST /v1/qa/diagnose` 与普通 QA 请求使用同一个 `QAService.execute(question)`，
  返回脱敏的 plan、通道、融合、排除项、workflow trace、节点耗时和 model usage；
- `result.html` 将诊断投影为五个可键盘操作的 tabs：Query Plan、Retrieval Channels、
  Fusion & Rerank、Exclusions、Workflow Trace；
- 结果 partial 提供 Copy answer 和 Download JSON，下载内容只含公开结果、最终所选 evidence
  与诊断投影，不含 Prompt、凭据或未选中的内部候选 evidence；
- `tests/e2e/test_ui_playwright.py` 通过真实 Microsoft Edge 驱动 loopback Uvicorn，
  覆盖 HTMX swap、五个 tabs、键盘导航、citation focus、复制、JSON 下载、安全 headers、
  错误 partial 和窄屏布局，并写入截图 `docs/images/m8_ui.png`；
- `tests/live/test_m8_ui_live.py` 提供真实 Vertex/数据库/`qa_runs` 八意图 smoke，
  但默认跳过，只有显式授权和环境变量才运行。

## 2. 路由与一次执行契约

| 方法 | 路径 | 当前行为 |
|---|---|---|
| `GET` | `/` | 307 重定向到 `/ui` |
| `GET` | `/ui` | Jinja2 主页面；health partial 通过 HTMX 加载 |
| `POST` | `/ui/qa` | 校验同源 urlencoded 表单并执行一次共享 `QAService`，返回 result/error partial |
| `GET` | `/ui/health` | 返回健康 partial；ready 为 200，未 ready 为 503 |
| `POST` | `/v1/qa` | 既有 JSON QA 契约，仍调用同一个 `QAService` |
| `POST` | `/v1/qa/diagnose` | 同一次 QA 执行返回 `QADiagnoseResponse` 及脱敏诊断 |

`/ui/qa`、`/v1/qa` 和 `/v1/qa/diagnose` 都经过同一 readiness probe 和进程内并发
gate。UI 不为显示诊断再次检索；一次请求只调用一次 `QAService.execute()`。`qa_runs`
仍由服务层写入，页面不读取历史会话，诊断 endpoint 也不形成 checkpoint 或 Memory。

## 3. 公开诊断投影

`src/panda_agent/api.py::_ui_diagnostics()` 只保留可展示的结构化字段：

- Query Plan：`intent`、`routing_method`、目标仓库、锁定版本、concept scopes、alias、
  source budgets 和 required source types；
- Retrieval Channels：exact、dense、sparse、paper、workflow、graph 的对象 ID/排名；
- Fusion & Rerank：融合分数、rerank/final rank 和最终 evidence ID；
- Exclusions：对象 ID 与确定性排除原因；
- Workflow Trace：检索/定向检索/修订计数、验证错误码、逐节点 timings 和四项 usage
  （`model_calls`、`token_usage`、`generation_calls`、`embedding_calls`）。

原始问题、完整 Prompt、模型原文、完整 evidence 正文、ADC 路径、凭据和异常堆栈不进入
HTML 或 diagnose response。`result_json` 仅用于当前结果下载；它沿用同一脱敏投影。

## 4. 页面交互与资源

- 模板由 Jinja2 渲染并默认 autoescape；本地 `static/vendor/htmx.min.js` 固定为
  HTMX **2.0.7**，不访问 CDN，也不需要 Node/npm。
- HTMX 只替换 `#qa-result` 或 `#runtime-status` 的 partial；`ui.js` 绑定 tabs、示例问题、
  citation focus、剪贴板复制和 JSON Blob 下载。
- 五个 tabs 使用 `role=tablist/tab/tabpanel`、`aria-selected`、roving `tabindex` 和
  Arrow/Home/End 键盘导航；citation 点击后将焦点移到对应 evidence card。
- 下载文件名按 request ID 清理为 `panda-qa-<request-id>.json`；复制只复制当前回答。

截图（真实 Edge P1 E2E 产生）:

![M8 UI screenshot](images/m8_ui.png)

## 5. 安全和部署边界

M8 继续是 loopback-only、本机单进程原型：`panda-qa-api` 拒绝非 loopback host，默认
`127.0.0.1:8000`、Uvicorn `workers=1`，没有账户、鉴权、TLS、CORS、跨进程 gate、远程
访问白名单或公开部署能力。

UI 请求只接受 `application/x-www-form-urlencoded`，body 上限 65,536 bytes，问题长度
为 1–10,000 字符；可选 `Origin` 必须与当前 scheme/netloc 同源。Jinja2 autoescape、
页面和响应 CSP、`X-Content-Type-Options: nosniff`、`Referrer-Policy: no-referrer` 和
HTMX `selfRequestsOnly` 共同限制脚本和请求边界。Evidence locator 仅对 `https://` 生成
`target="_blank"` 链接并带 `rel="noopener noreferrer"`；`http://`/`file://` 只显示文本。

## 6. 验证

确定性验证证据（详见 overall 结果）如下：

| 检查 | 结果 |
|---|---:|
| 全部 `tests/unit` | **198/198** |
| UI 单元（`test_ui.py` + `test_ui_assets.py`） | **11/11** |
| 公开 diagnostics 单元（`test_diagnostics.py`） | **3/3** |
| 真实 Microsoft Edge Playwright E2E（`tests/e2e/test_ui_playwright.py`） | **1/1** |
| `python -m compileall -q src tests\unit tests\e2e tests\live` | 通过 |
| `python -m pip check` | 通过 |
| `git diff --check` | 通过 |

真实 Edge 测试使用 fake `QAService`，因此不调用 Vertex、不写数据库；它验证的是打包后
本地 UI、浏览器行为和安全边界。真实服务 smoke 由下一节的显式 opt-in 测试负责。

## 7. 真实 UI smoke（显式授权）

可复现入口为 `tests/live/test_m8_ui_live.py`。默认运行会跳过：

```powershell
python -m unittest tests\live\test_m8_ui_live.py -v
```

只有设置 `PANDA_RUN_LIVE_M8_UI=1` 才启用真实 loopback 服务、Microsoft Edge、Vertex AI
和 PostgreSQL `qa_runs` 写入；可用 `PANDA_M8_LIVE_CASE_IDS` 选择冻结八题的唯一子集，
例如：

```powershell
$env:PANDA_RUN_LIVE_M8_UI = '1'
$env:PANDA_M8_LIVE_CASE_IDS = 'g090,g112'
python -m unittest tests\live\test_m8_ui_live.py -v
```

该测试每题通过 `/ui/qa` 发送问题，会真实调用 Vertex，并为每题写入一条 `qa_runs`。
因此它是可复现但有外部副作用的 opt-in smoke，必须有明确授权；未设置变量时不得把
跳过当作 live 通过。

## 8. M8 P1 结论

P1 的诊断、健康 partial、复制/下载、真实 Edge E2E、截图和可授权 live harness 均已
落地并验证。与 P0 合并后，当前里程碑为 **M8 overall PASS，M8 complete**；后续仍可
单独规划生产鉴权、跨进程协调、metrics/cost 聚合或多轮 checkpoint，但这些不属于 M8
本次完成范围。
