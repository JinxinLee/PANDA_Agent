"""Loopback-only local FastAPI boundary for the QA service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version
import os
from pathlib import Path
import re
from typing import Any, Callable
import uuid

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from panda_agent import __version__
from panda_agent.models import QAResult
from panda_agent.prompts import PROMPT_SET_VERSION
from panda_agent.runtime import EMBEDDING_MODEL, RuntimeIdentity, runtime_identity_path, verify_runtime
from panda_agent.service import QAService, QAServiceBusyError, QAServiceEnvelope, QAServiceError


PACKAGE_NAME = "panda-research-qa-agent"
DEFAULT_GENERATION_MODEL = "gemini-3.6-flash"


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


class ErrorResponse(BaseModel):
    request_id: str
    error_code: str
    message: str


RuntimeProbe = Callable[..., dict[str, Any]]
ServiceFactory = Callable[..., QAService]


def _max_concurrency_from_env() -> int:
    raw = os.getenv("PANDA_API_MAX_CONCURRENCY", "1")
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError("PANDA_API_MAX_CONCURRENCY must be a positive integer") from exc
    if value < 1 or str(value) != raw.strip():
        raise ValueError("PANDA_API_MAX_CONCURRENCY must be a positive integer")
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


def create_app(
    project_root: Path | None = None,
    *,
    runtime_probe: RuntimeProbe = _default_runtime_probe,
    service_factory: ServiceFactory = QAService,
) -> FastAPI:
    """Create a process-local API app; QAService is initialized once per lifespan."""
    root = (project_root or Path(__file__).resolve().parents[2]).resolve()
    max_concurrency = _max_concurrency_from_env()

    def probe_runtime() -> dict[str, Any]:
        try:
            return runtime_probe(project_root=root)
        except Exception:
            return {"valid": False, "runtime_status": "initialization_failed", "checks": {}}

    def refresh_readiness() -> bool:
        runtime_state = probe_runtime()
        app.state.runtime = runtime_state
        app.state.ready = bool(runtime_state.get("valid") and app.state.service is not None)
        return app.state.ready

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.ready = False
        app.state.runtime = {"valid": False, "runtime_status": "not_initialized", "checks": {}}
        app.state.service = None
        runtime_state = probe_runtime()
        app.state.runtime = runtime_state
        if runtime_state.get("valid"):
            try:
                app.state.service = service_factory(
                    root, origin="api", max_concurrency=max_concurrency
                )
            except Exception:
                # Startup failure must not make liveness unavailable or disclose local details.
                app.state.runtime = {"valid": False, "runtime_status": "initialization_failed", "checks": {}}
        app.state.ready = bool(app.state.runtime.get("valid") and app.state.service is not None)
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

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "live"}

    @app.get("/health/ready", response_model=None)
    async def ready():
        if not await run_in_threadpool(refresh_readiness):
            return JSONResponse(status_code=503, content={"status": "not_ready"})
        return {"status": "ready"}

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
        responses={429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    )
    async def ask(request: QARequest) -> dict[str, Any]:
        if not await run_in_threadpool(refresh_readiness):
            return _error_response(503, str(uuid.uuid4()), "service_unavailable", "Service unavailable")
        try:
            envelope: QAServiceEnvelope = await run_in_threadpool(app.state.service.execute, request.question)
        except QAServiceBusyError as exc:
            error = exc.error_envelope()
            return _error_response(429, error["request_id"], error["error_code"], "Service busy")
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

    return app
