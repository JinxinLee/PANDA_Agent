"""Process-local request lifecycle for the bounded QA graph."""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from psycopg.types.json import Jsonb

from panda_agent.models import QAResult
from panda_agent.qa import QAAgent


TRACE_SCHEMA_VERSION = "1.0"
VALID_ORIGINS = frozenset({"cli", "api", "ui"})
_PROCESS_GATE = threading.BoundedSemaphore(1)
_USAGE_KEYS = ("model_calls", "token_usage", "generation_calls", "embedding_calls")
_LOGGER = logging.getLogger(__name__)


class QAServiceError(RuntimeError):
    """A request failure with a stable, safe-to-persist classification."""

    def __init__(
        self, request_id: str, code: str, message: str, *, defer_gate_release: bool = False
    ) -> None:
        super().__init__(message)
        self.request_id = request_id
        self.code = code
        self.error_code = code
        self.defer_gate_release = defer_gate_release

    def error_envelope(self) -> dict[str, str]:
        return {"request_id": self.request_id, "error_code": self.error_code, "message": str(self)}


class QAServiceBusyError(QAServiceError):
    def __init__(self, request_id: str) -> None:
        super().__init__(request_id, "busy", "QA service is busy; retry the request later")


class QAServiceDeadlineError(QAServiceError):
    def __init__(self, request_id: str) -> None:
        super().__init__(
            request_id,
            "deadline_exceeded",
            "QA request exceeded its deadline",
            defer_gate_release=True,
        )


def _lifecycle_log(
    request_id: str,
    origin: str,
    event: str,
    status: str,
    *,
    count: int | None = None,
    timing_ms: int | None = None,
) -> None:
    """Emit a compact lifecycle event without request or model contents."""
    payload: dict[str, str | int] = {
        "request_id": request_id,
        "origin": origin,
        "event": event,
        "status": status,
    }
    if count is not None:
        payload["count"] = count
    if timing_ms is not None:
        payload["timing_ms"] = timing_ms
    _LOGGER.info(json.dumps(payload, sort_keys=True))


def _error_code(error: object) -> str:
    """Convert volatile verifier text into a compact diagnostic code."""
    text = str(error).casefold()
    if "version conflict" in text or "requested" in text and "locked" in text:
        return "version_conflict"
    if "unsupported requested api" in text:
        return "unsupported_api"
    if "unsupported requested symbol" in text:
        return "unsupported_symbol"
    if "runtime artifact" in text:
        return "runtime_artifact_unavailable"
    if "future runtime" in text:
        return "future_runtime_unverifiable"
    if "universal proof" in text:
        return "universal_proof_unavailable"
    if "missing" in text:
        return "missing_evidence"
    return "verification_failed"


@dataclass(frozen=True)
class QAServiceEnvelope:
    """The service-owned response boundary used by CLI, API, and UI adapters."""

    request_id: str
    result: QAResult
    diagnostics: dict[str, Any]
    duration_ms: int
    node_timings: dict[str, float] = field(default_factory=dict)
    model_usage: dict[str, int] = field(default_factory=dict)

    def detailed_output(self) -> dict[str, Any]:
        return {"result": self.result.model_dump(mode="json"), "diagnostics": self.diagnostics}


class QAService:
    """Own request IDs, worker threads, concurrency, and safe qa_runs traces."""

    def __init__(
        self,
        project_root: Any | None = None,
        *,
        agent: QAAgent | None = None,
        origin: str,
        max_concurrency: int = 1,
        deadline_seconds: float = 300.0,
    ) -> None:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be at least one")
        if agent is None and project_root is None:
            raise ValueError("project_root is required when agent is not supplied")
        if origin not in VALID_ORIGINS:
            raise ValueError("origin must be one of: cli, api, ui")
        if deadline_seconds <= 0:
            raise ValueError("deadline_seconds must be greater than zero")
        self.agent = agent or QAAgent(project_root)
        self.origin = origin
        self.deadline_seconds = deadline_seconds
        # Default services share one process-local gate.  A non-default test or
        # embedding may deliberately opt into a separate bounded gate.
        self._gate = _PROCESS_GATE if max_concurrency == 1 else threading.BoundedSemaphore(max_concurrency)

    def run(self, question: str) -> QAResult:
        return self.execute(question).result

    def run_detailed(self, question: str) -> dict[str, Any]:
        return self.execute(question).detailed_output()

    def execute(self, question: str) -> QAServiceEnvelope:
        request_id = str(uuid.uuid4())
        if not self._gate.acquire(blocking=False):
            _lifecycle_log(request_id, self.origin, "rejected", "busy")
            raise QAServiceBusyError(request_id)
        release_gate = True
        try:
            return self._run_once(request_id, question)
        except QAServiceError as exc:
            # The worker owns release after its post-deadline persistence cleanup.
            release_gate = not exc.defer_gate_release
            raise
        finally:
            if release_gate:
                self._gate.release()

    def _run_once(self, request_id: str, question: str) -> QAServiceEnvelope:
        started = time.perf_counter()
        trace = self._trace()
        try:
            self._insert_running(request_id, question, trace)
        except Exception as exc:
            _lifecycle_log(request_id, self.origin, "terminal", "persistence_error")
            raise QAServiceError(
                request_id, "persistence_error", "QA request could not be recorded"
            ) from exc
        _lifecycle_log(request_id, self.origin, "started", "running")

        outcome: dict[str, Any] = {}
        lifecycle = {
            "client_terminal_attempted": threading.Event(),
            "deadline_latched": False,
            "deadline_trace": None,
            "worker_finished": False,
        }
        lifecycle_lock = threading.Lock()

        def worker() -> None:
            try:
                outcome["detailed"] = self.agent.run_detailed(question)
            except BaseException as exc:  # preserve KeyboardInterrupt/SystemExit in caller
                outcome["exception"] = exc
            with lifecycle_lock:
                lifecycle["worker_finished"] = True
                deadline_latched = lifecycle["deadline_latched"]
                deadline_trace = lifecycle["deadline_trace"]
            if deadline_latched:
                lifecycle["client_terminal_attempted"].wait()
                self._cleanup_after_deadline(request_id, started, outcome, deadline_trace)

        thread = threading.Thread(target=worker, name=f"qa-{request_id}")
        thread.start()
        thread.join(self.deadline_seconds)
        duration_ms = int(round((time.perf_counter() - started) * 1000))
        deadline_trace = self._trace(cleanup_status="deadline_exceeded")
        with lifecycle_lock:
            worker_finished = lifecycle["worker_finished"]
            if not worker_finished:
                lifecycle["deadline_latched"] = True
                lifecycle["deadline_trace"] = deadline_trace

        if not worker_finished:
            try:
                self._finish(
                    request_id,
                    "error",
                    duration_ms,
                    None,
                    "deadline_exceeded",
                    {"workflow": duration_ms},
                    self._empty_usage(),
                    deadline_trace,
                )
            except Exception:
                _lifecycle_log(
                    request_id, self.origin, "terminal", "persistence_error", timing_ms=duration_ms
                )
                self._defer_gate_release(thread, request_id)
                raise QAServiceError(
                    request_id,
                    "persistence_error",
                    "QA deadline could not be recorded",
                    defer_gate_release=True,
                )
            finally:
                lifecycle["client_terminal_attempted"].set()
            _lifecycle_log(request_id, self.origin, "terminal", "deadline_exceeded", timing_ms=duration_ms)
            self._defer_gate_release(thread, request_id)
            raise QAServiceDeadlineError(request_id)

        node_timings = self._node_timings(outcome.get("detailed"), duration_ms)
        model_usage = self._model_usage(outcome.get("detailed"))
        if "exception" in outcome:
            error = outcome["exception"]
            trace = self._trace(cleanup_status="execution_error")
            try:
                self._finish(
                    request_id, "failed", duration_ms, None, "execution_error", node_timings, model_usage, trace
                )
            except Exception as cleanup_error:
                _lifecycle_log(
                    request_id, self.origin, "terminal", "persistence_error", timing_ms=duration_ms
                )
                raise QAServiceError(
                    request_id, "persistence_error", "QA failure could not be recorded"
                ) from cleanup_error
            _lifecycle_log(request_id, self.origin, "terminal", "execution_error", timing_ms=duration_ms)
            raise QAServiceError(request_id, "execution_error", "QA request execution failed") from error

        detailed = outcome["detailed"]
        result = QAResult.model_validate(detailed["result"])
        trace = self._trace(detailed, cleanup_status="completed")
        intent = str((detailed.get("diagnostics") or {}).get("plan", {}).get("intent") or "")
        try:
            self._finish(request_id, result.status.value, duration_ms, intent, None, node_timings, model_usage, trace)
        except Exception as exc:
            _lifecycle_log(
                request_id, self.origin, "terminal", "persistence_error", timing_ms=duration_ms
            )
            raise QAServiceError(
                request_id, "persistence_error", "QA completion could not be recorded"
            ) from exc
        _lifecycle_log(request_id, self.origin, "terminal", result.status.value, timing_ms=duration_ms)
        return QAServiceEnvelope(
            request_id=request_id,
            result=result,
            diagnostics=detailed["diagnostics"],
            duration_ms=duration_ms,
            node_timings=node_timings,
            model_usage=model_usage,
        )

    def _insert_running(self, request_id: str, question: str, trace: dict[str, Any]) -> None:
        with self.agent.retriever.storage.connect() as connection:
            connection.execute(
                "INSERT INTO qa_runs(run_id,question,status,trace) VALUES(%s,%s,%s,%s)",
                (request_id, question, "running", Jsonb(trace)),
            )

    def _finish(
        self,
        request_id: str,
        status: str,
        duration_ms: float,
        intent: str | None,
        error_code: str | None,
        node_timings: dict[str, float],
        model_usage: dict[str, int],
        trace: dict[str, Any],
    ) -> None:
        with self.agent.retriever.storage.connect() as connection:
            connection.execute(
                "UPDATE qa_runs SET status=%s,completed_at=now(),duration_ms=%s,intent=%s,error_code=%s,"
                "node_timings=%s,model_usage=%s,trace=%s WHERE run_id=%s",
                (status, duration_ms, intent, error_code, Jsonb(node_timings), Jsonb(model_usage), Jsonb(trace), request_id),
            )

    def _cleanup_after_deadline(
        self,
        request_id: str,
        started: float,
        outcome: dict[str, Any],
        client_trace: dict[str, Any],
    ) -> None:
        """Record worker-only fields after the client-facing deadline is immutable."""
        duration_ms = int(round((time.perf_counter() - started) * 1000))
        detailed = outcome.get("detailed")
        trace = dict(client_trace)
        trace["worker_completed_at"] = datetime.now(UTC).isoformat()
        trace["cleanup_status"] = "completed_after_deadline" if detailed else "execution_error_after_deadline"
        try:
            self._finish_deadline_cleanup(
                request_id,
                self._node_timings(detailed, duration_ms),
                self._model_usage(detailed),
                trace,
            )
        except Exception:
            _lifecycle_log(request_id, self.origin, "cleanup_persistence_failed", "error", timing_ms=duration_ms)
        else:
            _lifecycle_log(request_id, self.origin, "worker_cleanup", "error", timing_ms=duration_ms)

    def _release_after_worker(self, worker: threading.Thread) -> None:
        """Do not reopen the process gate until the timed-out worker has exited."""
        worker.join()
        self._gate.release()

    def _defer_gate_release(self, worker: threading.Thread, request_id: str) -> None:
        threading.Thread(
            target=self._release_after_worker,
            args=(worker,),
            name=f"qa-cleanup-{request_id}",
        ).start()

    def _finish_deadline_cleanup(
        self,
        request_id: str,
        node_timings: dict[str, float],
        model_usage: dict[str, int],
        trace: dict[str, Any],
    ) -> None:
        with self.agent.retriever.storage.connect() as connection:
            connection.execute(
                "UPDATE qa_runs SET node_timings=%s,model_usage=%s,trace=%s WHERE run_id=%s",
                (Jsonb(node_timings), Jsonb(model_usage), Jsonb(trace), request_id),
            )

    @staticmethod
    def _empty_usage() -> dict[str, int]:
        return {key: 0 for key in _USAGE_KEYS}

    def _node_timings(self, detailed: dict[str, Any] | None, duration_ms: int) -> dict[str, float]:
        timings = dict((detailed or {}).get("node_timings_ms") or {})
        timings.setdefault("workflow", duration_ms)
        return timings

    def _model_usage(self, detailed: dict[str, Any] | None) -> dict[str, int]:
        usage = self._empty_usage()
        usage.update((detailed or {}).get("model_usage") or {})
        return usage

    def _trace(self, detailed: dict[str, Any] | None = None, *, cleanup_status: str = "running") -> dict[str, Any]:
        diagnostics = (detailed or {}).get("diagnostics") or {}
        return {
            "trace_schema_version": TRACE_SCHEMA_VERSION,
            "origin": self.origin,
            "selected_evidence_ids": diagnostics.get("selected_evidence_ids", []),
            "targeted_retrieval_count": diagnostics.get("targeted_retrieval_count", 0),
            "revision_count": diagnostics.get("revision_count", 0),
            "verification_error_codes": [_error_code(error) for error in diagnostics.get("verification_errors", [])],
            "worker_completed_at": (
                datetime.now(UTC).isoformat()
                if cleanup_status not in {"running", "deadline_exceeded"}
                else None
            ),
            "cleanup_status": cleanup_status,
        }

    @staticmethod
    def canonical_output(detailed: dict[str, Any]) -> dict[str, Any]:
        """Stable fixture representation: no request, timing, usage, or persistence data."""
        result = QAResult.model_validate(detailed["result"])
        diagnostics = detailed.get("diagnostics", {})
        return {
            "result": {
                "status": result.status.value,
                "answer": result.answer,
                "claims": [claim.model_dump(mode="json") for claim in result.claims],
                "evidence_ids": [item.evidence_id for item in result.evidence],
                "resolved_versions": result.resolved_versions,
                "errors": [_error_code(error) for error in result.verification_errors],
            },
            "diagnostics": {
                "intent": (diagnostics.get("plan") or {}).get("intent"),
                "selected_evidence_ids": diagnostics.get("selected_evidence_ids", []),
                "retrieval_count": diagnostics.get("retrieval_count", 0),
                "targeted_retrieval_count": diagnostics.get("targeted_retrieval_count", 0),
                "revision_count": diagnostics.get("revision_count", 0),
                "verification_error_codes": [_error_code(error) for error in diagnostics.get("verification_errors", [])],
            },
        }
