"""Loopback-only local FastAPI boundary for the QA service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version
import json
import math
import os
from pathlib import Path
import re
import threading
import time
from typing import Any, Callable
from urllib.parse import parse_qs, urlsplit
import uuid

from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from panda_agent import __version__
from panda_agent.models import QAResult
from panda_agent.prompts import PROMPT_SET_VERSION
from panda_agent.runtime import EMBEDDING_MODEL, RuntimeIdentity, runtime_identity_path, verify_runtime
from panda_agent.service import (
    QAService,
    QAServiceBusyError,
    QAServiceDeadlineError,
    QAServiceEnvelope,
    QAServiceError,
    _error_code,
)


PACKAGE_NAME = "panda-research-qa-agent"
DEFAULT_GENERATION_MODEL = "gemini-3.7-flash"
PACKAGE_ROOT = Path(__file__).resolve().parent
MAX_UI_FORM_BODY_BYTES = 65_536
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
    "connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; "
    "form-action 'self'"
)


class QARequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=10_000)

    @field_validator("question", mode="before")
    @classmethod
    def strip_question(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class TimingsResponse(BaseModel):
    total: int = Field(ge=0)


class QAResponse(BaseModel):
    request_id: str
    result: QAResult
    timings_ms: TimingsResponse


class QADiagnoseResponse(QAResponse):
    node_timings_ms: dict[str, float] = Field(default_factory=dict)
    model_usage: dict[str, int] = Field(default_factory=dict)
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    request_id: str
    error_code: str
    message: str


RuntimeProbe = Callable[..., dict[str, Any]]
ServiceFactory = Callable[..., QAService]


class _ServiceUnavailableError(RuntimeError):
    """The process is live but its registered local QA runtime is unavailable."""


def _max_concurrency_from_env() -> int:
    raw = os.getenv("PANDA_API_MAX_CONCURRENCY", "1")
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError("PANDA_API_MAX_CONCURRENCY must be a positive integer") from exc
    if value < 1 or str(value) != raw.strip():
        raise ValueError("PANDA_API_MAX_CONCURRENCY must be a positive integer")
    return value


def _positive_seconds_from_env(name: str, default: float) -> float:
    raw = os.getenv(name, str(default))
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive number") from exc
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive number")
    return value


def _readiness_ttl_seconds_from_env() -> float:
    name = "PANDA_READINESS_TTL_SECONDS"
    raw = os.getenv(name, "5")
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a non-negative number") from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a non-negative number")
    return value


def _default_runtime_probe(*, project_root: Path) -> dict[str, Any]:
    """Check the registered runtime and locally resolvable ADC without model calls."""
    state = verify_runtime(project_root=project_root)
    if not state.get("valid"):
        return state
    try:
        import google.auth

        google.auth.default()
    except Exception:
        checks = dict(state.get("checks") or {})
        checks["adc"] = False
        return {**state, "valid": False, "runtime_status": "adc_unavailable", "checks": checks}
    checks = dict(state.get("checks") or {})
    checks["adc"] = True
    return {**state, "checks": checks}


def _package_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return __version__


def _runtime_identity(root: Path) -> RuntimeIdentity | None:
    try:
        return RuntimeIdentity.model_validate_json(runtime_identity_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _retrieval_policy_schema_version(root: Path) -> str | None:
    try:
        text = (root / "configs" / "retrieval_policies.yaml").read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^schema_version:\s*[\"']?([^\s\"'#]+)", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def _error_response(status_code: int, request_id: str, error_code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            request_id=request_id, error_code=error_code, message=message
        ).model_dump(mode="json"),
    )


async def _bounded_form_body(request: Request) -> bytes:
    """Read one urlencoded body without admitting an unbounded in-memory upload."""
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_UI_FORM_BODY_BYTES:
                raise ValueError("body is too large")
        except ValueError as exc:
            raise ValueError("body is too large") from exc
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_UI_FORM_BODY_BYTES:
            raise ValueError("body is too large")
        chunks.append(chunk)
    return b"".join(chunks)


def _same_origin(request: Request) -> bool:
    origin = request.headers.get("origin")
    if not origin:
        return True
    parsed = urlsplit(origin)
    return bool(parsed.scheme and parsed.netloc) and (
        parsed.scheme.casefold(), parsed.netloc.casefold()
    ) == (request.url.scheme.casefold(), request.url.netloc.casefold())


def _parse_ui_request(body: bytes) -> QARequest:
    try:
        parsed = parse_qs(
            body.decode("utf-8"), keep_blank_values=True, strict_parsing=True, max_num_fields=2
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("invalid form body") from exc
    fields: dict[str, object] = {
        name: values[0] if len(values) == 1 else values for name, values in parsed.items()
    }
    return QARequest.model_validate(fields)


_PUBLIC_CHANNEL_ORDER = ("exact", "dense", "sparse", "paper", "workflow", "graph")
_PUBLIC_USAGE_KEYS = ("model_calls", "token_usage", "generation_calls", "embedding_calls")


def _string_list(value: object) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _string_mapping(value: object) -> dict[str, str]:
    return {
        key: item for key, item in value.items() if isinstance(key, str) and isinstance(item, str)
    } if isinstance(value, dict) else {}


def _numeric_mapping(value: object, *, integer: bool) -> dict[str, int | float]:
    values: dict[str, int | float] = {}
    if not isinstance(value, dict):
        return values
    for key, item in value.items():
        if not isinstance(key, str) or isinstance(item, bool) or not isinstance(item, (int, float)):
            continue
        if not math.isfinite(float(item)):
            continue
        values[key] = int(item) if integer else float(item)
    return values


def _rank_by_id(value: object) -> dict[str, int]:
    return {object_id: rank for rank, object_id in enumerate(_string_list(value), start=1)}


def _safe_count(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


def _ui_diagnostics(
    diagnostics: dict[str, Any],
    *,
    node_timings: dict[str, float] | None = None,
    model_usage: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Deterministically project diagnostics without exposing QA internals or text."""
    plan = diagnostics.get("plan") if isinstance(diagnostics.get("plan"), dict) else {}
    rankings = diagnostics.get("rankings") if isinstance(diagnostics.get("rankings"), dict) else {}
    channels = {
        channel: [
            {"object_id": object_id, "rank": rank}
            for rank, object_id in enumerate(_string_list(rankings.get(channel)), start=1)
        ]
        for channel in _PUBLIC_CHANNEL_ORDER
        if channel in rankings
    }
    rerank_ranks = _rank_by_id(diagnostics.get("reranked_object_ids"))
    final_ranks = _rank_by_id(diagnostics.get("ranked_object_ids"))
    fusion_scores = _numeric_mapping(diagnostics.get("fusion_scores"), integer=False)
    fusion = [
        {
            "object_id": object_id,
            "score": float(score),
            "rerank_rank": rerank_ranks.get(object_id),
            "final_rank": final_ranks.get(object_id),
        }
        for object_id, score in sorted(fusion_scores.items(), key=lambda item: (-float(item[1]), item[0]))
    ]
    exclusions = [
        {"object_id": item["object_id"], "reason": item["reason"]}
        for item in diagnostics.get("excluded", [])
        if isinstance(item, dict)
        and isinstance(item.get("object_id"), str)
        and isinstance(item.get("reason"), str)
    ] if isinstance(diagnostics.get("excluded"), list) else []
    raw_usage = _numeric_mapping(model_usage, integer=True)
    usage = {key: int(raw_usage.get(key, 0)) for key in _PUBLIC_USAGE_KEYS}
    return {
        "plan": {
            "intent": plan.get("intent") if isinstance(plan.get("intent"), str) else None,
            "routing_method": plan.get("routing_method") if isinstance(plan.get("routing_method"), str) else None,
            "target_repositories": _string_list(plan.get("target_repositories")),
            "resolved_versions": _string_mapping(plan.get("resolved_versions")),
            "concept_scopes": _string_mapping(plan.get("concept_scopes")),
            "resolved_aliases": _string_mapping(plan.get("resolved_aliases")),
            "source_budgets": _numeric_mapping(plan.get("source_budgets"), integer=False),
            "required_source_types": _string_list(plan.get("required_source_types")),
        },
        "channels": channels,
        "fusion": fusion,
        "exclusions": exclusions,
        "selected_evidence_ids": _string_list(diagnostics.get("selected_evidence_ids")),
        "workflow_trace": {
            "retrieval_count": _safe_count(diagnostics.get("retrieval_count", 0)),
            "targeted_retrieval_count": _safe_count(diagnostics.get("targeted_retrieval_count", 0)),
            "revision_count": _safe_count(diagnostics.get("revision_count", 0)),
            "verification_error_codes": [
                _error_code(error) for error in diagnostics.get("verification_errors", [])
            ] if isinstance(diagnostics.get("verification_errors"), list) else [],
            "node_timings": _numeric_mapping(node_timings, integer=False),
            "model_usage": usage,
        },
    }


def _public_runtime_context(root: Path, runtime_state: dict[str, Any]) -> dict[str, Any]:
    identity = _runtime_identity(root)
    return {
        "status": runtime_state.get("runtime_status", "not_initialized"),
        "knowledge_revision": identity.knowledge_revision if identity else None,
        "service_revision": identity.service_revision if identity else None,
        "generation_model": os.getenv("QA_GENERATION_MODEL_ID", DEFAULT_GENERATION_MODEL),
        "embedding_model": os.getenv("QA_EMBEDDING_MODEL_ID", EMBEDDING_MODEL),
    }


def _public_health_context(root: Path, runtime_state: dict[str, Any], *, ready: bool) -> dict[str, Any]:
    runtime = _public_runtime_context(root, runtime_state)
    return {
        "status": "ready" if ready else "not_ready",
        "ready": ready,
        "package_version": _package_version(),
        "runtime_status": runtime["status"],
        "generation_model": runtime["generation_model"],
        "embedding_model": runtime["embedding_model"],
        "prompt_version": PROMPT_SET_VERSION,
    }


def _diagnose_payload(envelope: QAServiceEnvelope) -> dict[str, Any]:
    return {
        "request_id": envelope.request_id,
        "result": envelope.result.model_dump(mode="json"),
        "timings_ms": {"total": envelope.duration_ms},
        "node_timings_ms": envelope.node_timings,
        "model_usage": envelope.model_usage,
        "diagnostics": _ui_diagnostics(
            envelope.diagnostics,
            node_timings=envelope.node_timings,
            model_usage=envelope.model_usage,
        ),
    }


def create_app(
    project_root: Path | None = None,
    *,
    runtime_probe: RuntimeProbe = _default_runtime_probe,
    service_factory: ServiceFactory = QAService,
) -> FastAPI:
    """Create a process-local API app; QAService is initialized once per lifespan."""
    root = (project_root or Path(__file__).resolve().parents[2]).resolve()
    max_concurrency = _max_concurrency_from_env()
    deadline_seconds = _positive_seconds_from_env("PANDA_QA_DEADLINE_SECONDS", 300.0)
    readiness_ttl_seconds = _readiness_ttl_seconds_from_env()
    readiness_lock = threading.Lock()
    readiness_expires_at = 0.0

    def probe_runtime() -> dict[str, Any]:
        try:
            return runtime_probe(project_root=root)
        except Exception:
            return {"valid": False, "runtime_status": "initialization_failed", "checks": {}}

    def refresh_readiness(app: FastAPI, *, force: bool = False) -> bool:
        nonlocal readiness_expires_at
        with readiness_lock:
            now = time.monotonic()
            if not force and readiness_ttl_seconds and now < readiness_expires_at:
                return bool(app.state.ready)
            runtime_state = probe_runtime()
            app.state.runtime = runtime_state
            app.state.ready = bool(runtime_state.get("valid") and app.state.service is not None)
            readiness_expires_at = now + readiness_ttl_seconds if readiness_ttl_seconds else 0.0
            return app.state.ready

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        nonlocal readiness_expires_at
        app.state.ready = False
        app.state.runtime = {"valid": False, "runtime_status": "not_initialized", "checks": {}}
        app.state.service = None
        runtime_state = probe_runtime()
        app.state.runtime = runtime_state
        if runtime_state.get("valid"):
            try:
                app.state.service = service_factory(
                    root,
                    origin="api",
                    max_concurrency=max_concurrency,
                    deadline_seconds=deadline_seconds,
                )
            except Exception:
                # Startup failure must not make liveness unavailable or disclose local details.
                app.state.runtime = {"valid": False, "runtime_status": "initialization_failed", "checks": {}}
        with readiness_lock:
            app.state.ready = bool(app.state.runtime.get("valid") and app.state.service is not None)
            readiness_expires_at = time.monotonic() + readiness_ttl_seconds if readiness_ttl_seconds else 0.0
        yield
        app.state.service = None

    app = FastAPI(
        title="PANDA Research QA API",
        version=_package_version(),
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
        redoc_url=None,
        swagger_ui_oauth2_redirect_url=None,
    )
    templates = Jinja2Templates(directory=str(PACKAGE_ROOT / "templates"))
    app.mount("/static", StaticFiles(directory=str(PACKAGE_ROOT / "static")), name="static")

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        # FastAPI's built-in Swagger document requires inline/external assets; leave it usable.
        if request.url.path != "/docs":
            response.headers["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    async def execute_question(question: str) -> QAServiceEnvelope:
        if not await run_in_threadpool(refresh_readiness, app):
            raise _ServiceUnavailableError
        return await run_in_threadpool(app.state.service.execute, question)

    @app.get("/", include_in_schema=False)
    async def root_redirect():
        return RedirectResponse(url="/ui", status_code=307)

    @app.get("/ui", include_in_schema=False)
    async def ui(request: Request):
        return templates.TemplateResponse(request=request, name="ui.html", context={})

    @app.post("/ui/qa", include_in_schema=False)
    async def ui_ask(request: Request):
        request_id = str(uuid.uuid4())
        if not _same_origin(request):
            return templates.TemplateResponse(
                request=request,
                name="partials/error.html",
                context={
                    "error": {"status_code": 403, "error_code": "origin_forbidden"},
                    "request_id": request_id,
                },
                status_code=403,
            )
        content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().casefold()
        if content_type != "application/x-www-form-urlencoded":
            return templates.TemplateResponse(
                request=request,
                name="partials/error.html",
                context={"error": {"status_code": 400, "error_code": "bad_request"}, "request_id": request_id},
                status_code=400,
            )
        try:
            parsed_request = _parse_ui_request(await _bounded_form_body(request))
        except ValidationError:
            return templates.TemplateResponse(
                request=request,
                name="partials/error.html",
                context={
                    "error": {"status_code": 422, "error_code": "validation_error"},
                    "request_id": request_id,
                },
                status_code=422,
            )
        except ValueError:
            return templates.TemplateResponse(
                request=request,
                name="partials/error.html",
                context={"error": {"status_code": 400, "error_code": "bad_request"}, "request_id": request_id},
                status_code=400,
            )
        try:
            envelope = await execute_question(parsed_request.question)
        except _ServiceUnavailableError:
            return templates.TemplateResponse(
                request=request,
                name="partials/error.html",
                context={
                    "error": {"status_code": 503, "error_code": "service_unavailable"},
                    "request_id": request_id,
                },
                status_code=503,
            )
        except QAServiceBusyError as exc:
            return templates.TemplateResponse(
                request=request,
                name="partials/error.html",
                context={"error": {"status_code": 429, "error_code": "busy"}, "request_id": exc.request_id},
                status_code=429,
            )
        except QAServiceDeadlineError as exc:
            return templates.TemplateResponse(
                request=request,
                name="partials/error.html",
                context={
                    "error": {"status_code": 504, "error_code": "deadline_exceeded"},
                    "request_id": exc.request_id,
                },
                status_code=504,
            )
        except QAServiceError as exc:
            return templates.TemplateResponse(
                request=request,
                name="partials/error.html",
                context={
                    "error": {"status_code": 500, "error_code": "internal_error"},
                    "request_id": exc.request_id,
                },
                status_code=500,
            )
        except Exception:
            return templates.TemplateResponse(
                request=request,
                name="partials/error.html",
                context={"error": {"status_code": 500, "error_code": "internal_error"}, "request_id": request_id},
                status_code=500,
            )
        return templates.TemplateResponse(
            request=request,
            name="partials/result.html",
            context={
                "result": envelope.result,
                "request_id": envelope.request_id,
                "timings_ms": {"total": envelope.duration_ms},
                "diagnostics": _ui_diagnostics(
                    envelope.diagnostics,
                    node_timings=envelope.node_timings,
                    model_usage=envelope.model_usage,
                ),
                "result_json": json.dumps(_diagnose_payload(envelope), ensure_ascii=False),
            },
            status_code=200,
        )

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "live"}

    @app.get("/health/ready", response_model=None)
    async def ready():
        if not await run_in_threadpool(refresh_readiness, app):
            return JSONResponse(status_code=503, content={"status": "not_ready"})
        return {"status": "ready"}

    @app.get("/ui/health", include_in_schema=False)
    async def ui_health(request: Request):
        is_ready = await run_in_threadpool(refresh_readiness, app)
        return templates.TemplateResponse(
            request=request,
            name="partials/health.html",
            context={
                "ready": is_ready,
                "runtime": _public_runtime_context(root, app.state.runtime),
                "health": _public_health_context(root, app.state.runtime, ready=is_ready),
            },
            status_code=200 if is_ready else 503,
        )

    @app.get("/version")
    async def api_version() -> dict[str, Any]:
        runtime_state = getattr(app.state, "runtime", {})
        identity = _runtime_identity(root)
        return {
            "package": {"name": PACKAGE_NAME, "version": _package_version()},
            "models": {
                "generation": os.getenv("QA_GENERATION_MODEL_ID", DEFAULT_GENERATION_MODEL),
                "embedding": os.getenv("QA_EMBEDDING_MODEL_ID", EMBEDDING_MODEL),
            },
            "prompt_set": {"version": PROMPT_SET_VERSION},
            "retrieval_policy_schema_version": _retrieval_policy_schema_version(root),
            "runtime": {
                "knowledge_revision": identity.knowledge_revision if identity else None,
                "service_revision": identity.service_revision if identity else None,
                "source_manifest_sha256": identity.corpus_source_manifest_sha256 if identity else None,
                "index_fingerprint": identity.postgres.index_fingerprint if identity else None,
                "status": runtime_state.get("runtime_status", "not_initialized"),
            },
        }

    @app.post(
        "/v1/qa",
        response_model=QAResponse,
        responses={
            429: {"model": ErrorResponse},
            500: {"model": ErrorResponse},
            503: {"model": ErrorResponse},
            504: {"model": ErrorResponse},
        },
    )
    async def ask(request: QARequest) -> dict[str, Any]:
        try:
            envelope = await execute_question(request.question)
        except _ServiceUnavailableError:
            return _error_response(503, str(uuid.uuid4()), "service_unavailable", "Service unavailable")
        except QAServiceBusyError as exc:
            error = exc.error_envelope()
            return _error_response(429, error["request_id"], error["error_code"], "Service busy")
        except QAServiceDeadlineError as exc:
            return _error_response(504, exc.request_id, "deadline_exceeded", "Request deadline exceeded")
        except QAServiceError as exc:
            error = exc.error_envelope()
            return _error_response(500, error["request_id"], error["error_code"], "Internal server error")
        except Exception:
            return _error_response(500, str(uuid.uuid4()), "internal_error", "Internal server error")
        return {
            "request_id": envelope.request_id,
            "result": envelope.result.model_dump(mode="json"),
            "timings_ms": {"total": envelope.duration_ms},
        }

    @app.post(
        "/v1/qa/diagnose",
        response_model=QADiagnoseResponse,
        responses={
            429: {"model": ErrorResponse},
            500: {"model": ErrorResponse},
            503: {"model": ErrorResponse},
            504: {"model": ErrorResponse},
        },
    )
    async def diagnose(request: QARequest) -> dict[str, Any]:
        try:
            envelope = await execute_question(request.question)
        except _ServiceUnavailableError:
            return _error_response(503, str(uuid.uuid4()), "service_unavailable", "Service unavailable")
        except QAServiceBusyError as exc:
            error = exc.error_envelope()
            return _error_response(429, error["request_id"], error["error_code"], "Service busy")
        except QAServiceDeadlineError as exc:
            return _error_response(504, exc.request_id, "deadline_exceeded", "Request deadline exceeded")
        except QAServiceError as exc:
            error = exc.error_envelope()
            return _error_response(500, error["request_id"], error["error_code"], "Internal server error")
        except Exception:
            return _error_response(500, str(uuid.uuid4()), "internal_error", "Internal server error")
        return _diagnose_payload(envelope)

    return app
