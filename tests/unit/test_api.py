from __future__ import annotations

from contextlib import redirect_stderr
import io
import logging
import os
import threading
import tomllib
from tempfile import TemporaryDirectory
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from panda_agent.models import QAResult
from panda_agent.service import QAServiceBusyError, QAServiceDeadlineError, QAServiceEnvelope, QAServiceError


def answered_envelope() -> QAServiceEnvelope:
    return QAServiceEnvelope(
        request_id="00000000-0000-0000-0000-000000000001",
        result=QAResult.model_validate({"status": "answered", "answer": "Verified.", "claims": []}),
        diagnostics={"plan": {"intent": "usage"}},
        duration_ms=17,
    )


class FakeService:
    def __init__(self, response: QAServiceEnvelope | Exception | None = None) -> None:
        self.response = response or answered_envelope()
        self.calls: list[tuple[str, str]] = []

    def execute(self, question: str) -> QAServiceEnvelope:
        self.calls.append((question, threading.current_thread().name))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class APITestClientContractTests(unittest.TestCase):
    def make_app(self, *, runtime=None, service=None):
        from panda_agent.api import create_app

        runtime = runtime or {"valid": True, "runtime_status": "registered", "checks": {"registered": True}}
        service = service or FakeService()
        creations: list[tuple[Path, str, int, float]] = []

        def runtime_probe(*, project_root: Path):
            self.assertEqual(project_root, Path(".").resolve())
            return runtime

        def service_factory(project_root: Path, *, origin: str, max_concurrency: int, deadline_seconds: float):
            creations.append((project_root, origin, max_concurrency, deadline_seconds))
            return service

        return create_app(
            project_root=Path("."), runtime_probe=runtime_probe, service_factory=service_factory
        ), service, creations

    def test_lifecycle_health_ready_version_and_qa_contract(self) -> None:
        app, service, creations = self.make_app()
        with TestClient(app) as client:
            self.assertEqual(client.get("/health/live").json(), {"status": "live"})
            self.assertEqual(client.get("/health/ready").status_code, 200)
            version = client.get("/version")
            self.assertEqual(version.status_code, 200)
            self.assertIn("package", version.json())
            self.assertIn("models", version.json())
            self.assertIn("prompt_set", version.json())
            self.assertEqual(version.json()["retrieval_policy_schema_version"], "1.0")
            self.assertEqual(
                set(version.json()["runtime"]),
                {
                    "knowledge_revision", "service_revision", "source_manifest_sha256",
                    "index_fingerprint", "status",
                },
            )
            self.assertEqual(client.get("/docs").status_code, 200)
            openapi = client.get("/openapi.json")
            self.assertEqual(openapi.status_code, 200)
            qa_schema = openapi.json()["components"]["schemas"]["QAResponse"]["properties"]
            self.assertEqual(set(qa_schema), {"request_id", "result", "timings_ms"})
            response = client.post("/v1/qa", json={"question": "  What is PANDA?  "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["request_id"], "00000000-0000-0000-0000-000000000001")
        self.assertEqual(response.json()["result"]["status"], "answered")
        self.assertEqual(response.json()["timings_ms"], {"total": 17})
        self.assertNotIn("diagnostics", response.json())
        self.assertEqual(service.calls, [("What is PANDA?", service.calls[0][1])])
        self.assertNotEqual(service.calls[0][1], threading.current_thread().name)
        self.assertEqual(len(creations), 1)
        self.assertEqual(creations[0][1:], ("api", 1, 300.0))
        paths = {route.path for route in app.routes}
        self.assertEqual(
            paths,
            {
                "/",
                "/ui",
                "/ui/qa",
                "/ui/health",
                "/static",
                "/health/live",
                "/health/ready",
                "/version",
                "/v1/qa",
                "/v1/qa/diagnose",
                "/docs",
                "/openapi.json",
            },
        )

    def test_unready_runtime_keeps_live_but_blocks_qa(self) -> None:
        app, service, creations = self.make_app(runtime={"valid": False, "runtime_status": "not_registered"})
        with TestClient(app) as client:
            self.assertEqual(client.get("/health/live").status_code, 200)
            self.assertEqual(client.get("/health/ready").status_code, 503)
            response = client.post("/v1/qa", json={"question": "hello"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(set(response.json()), {"request_id", "error_code", "message"})
        self.assertEqual(response.json()["error_code"], "service_unavailable")
        self.assertEqual(service.calls, [])
        self.assertEqual(creations, [])

    def test_startup_exception_keeps_live_but_not_ready(self) -> None:
        app, service, creations = self.make_app()
        def failing_probe(*, project_root: Path):
            raise RuntimeError("do not disclose this")
        from panda_agent.api import create_app
        app = create_app(project_root=Path("."), runtime_probe=failing_probe, service_factory=lambda *_args, **_kwargs: service)
        with TestClient(app) as client:
            self.assertEqual(client.get("/health/live").status_code, 200)
            self.assertEqual(client.get("/health/ready").status_code, 503)
            response = client.post("/v1/qa", json={"question": "hello"})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("disclose", response.text)
        self.assertEqual(creations, [])

    def test_validation_busy_and_sanitized_errors(self) -> None:
        app, _, _ = self.make_app()
        with TestClient(app) as client:
            self.assertEqual(client.post("/v1/qa", json={"question": "   "}).status_code, 422)
        busy = QAServiceBusyError("00000000-0000-0000-0000-000000000429")
        service_error = QAServiceError(
            "00000000-0000-0000-0000-000000000500", "execution_error", "private detail"
        )
        for error, expected, payload in (
            (busy, 429, {"request_id": busy.request_id, "error_code": "busy", "message": "Service busy"}),
            (
                service_error,
                500,
                {"request_id": service_error.request_id, "error_code": "execution_error", "message": "Internal server error"},
            ),
            (RuntimeError("secret-token"), 500, None),
        ):
            app, _, _ = self.make_app(service=FakeService(error))
            with TestClient(app) as client:
                response = client.post("/v1/qa", json={"question": "hello"})
            self.assertEqual(response.status_code, expected)
            if payload is not None:
                self.assertEqual(response.json(), payload)
            else:
                self.assertEqual(set(response.json()), {"request_id", "error_code", "message"})
                self.assertEqual(response.json()["error_code"], "internal_error")
            self.assertNotIn("private", response.text)
            self.assertNotIn("secret", response.text)

    def test_deadline_error_has_safe_504_contract_and_openapi_schema(self) -> None:
        deadline = QAServiceDeadlineError("00000000-0000-0000-0000-000000000504")
        app, _, _ = self.make_app(service=FakeService(deadline))
        with TestClient(app) as client:
            response = client.post("/v1/qa", json={"question": "hello"})
            openapi = client.get("/openapi.json").json()
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json(), {
            "request_id": deadline.request_id,
            "error_code": "deadline_exceeded",
            "message": "Request deadline exceeded",
        })
        self.assertEqual(
            openapi["paths"]["/v1/qa"]["post"]["responses"]["504"],
            {"description": "Gateway Timeout", "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}
            }},
        )

    def test_deadline_configuration_is_passed_to_service_and_invalid_values_fail_closed(self) -> None:
        with patch.dict(os.environ, {"PANDA_QA_DEADLINE_SECONDS": "12.5"}):
            app, _, creations = self.make_app()
            with TestClient(app):
                pass
        self.assertEqual(creations[0][3], 12.5)

        from panda_agent.api import create_app

        for name, raw in (
            ("PANDA_QA_DEADLINE_SECONDS", "private-invalid-value"),
            ("PANDA_QA_DEADLINE_SECONDS", "0"),
            ("PANDA_READINESS_TTL_SECONDS", "private-invalid-value"),
            ("PANDA_READINESS_TTL_SECONDS", "-1"),
        ):
            with patch.dict(os.environ, {name: raw}):
                with self.assertRaises(ValueError) as raised:
                    create_app(project_root=Path("."), runtime_probe=lambda **_kwargs: {"valid": False})
            self.assertNotIn(raw, str(raised.exception))

    def test_readiness_ttl_reuses_startup_probe_and_zero_disables_cache(self) -> None:
        state = {"valid": True, "runtime_status": "registered", "checks": {"registered": True}}
        calls: list[Path] = []
        service = FakeService()

        def probe(*, project_root: Path):
            calls.append(project_root)
            return dict(state)

        from panda_agent.api import create_app

        with patch.dict(os.environ, {"PANDA_READINESS_TTL_SECONDS": "5"}):
            app = create_app(project_root=Path("."), runtime_probe=probe, service_factory=lambda *_args, **_kwargs: service)
            with TestClient(app) as client:
                self.assertEqual(client.get("/health/ready").status_code, 200)
                self.assertEqual(client.post("/v1/qa", json={"question": "cached"}).status_code, 200)
        self.assertEqual(len(calls), 1)

        calls.clear()
        with patch.dict(os.environ, {"PANDA_READINESS_TTL_SECONDS": "0"}):
            app = create_app(project_root=Path("."), runtime_probe=probe, service_factory=lambda *_args, **_kwargs: service)
            with TestClient(app) as client:
                self.assertEqual(client.get("/health/ready").status_code, 200)
                self.assertEqual(client.post("/v1/qa", json={"question": "uncached"}).status_code, 200)
        self.assertEqual(len(calls), 3)

    def test_readiness_ttl_reprobes_at_expiry_without_rebuilding_service(self) -> None:
        calls: list[Path] = []
        creations: list[object] = []
        clock = [100.0]
        service = FakeService()

        def probe(*, project_root: Path):
            calls.append(project_root)
            return {"valid": True, "runtime_status": "registered", "checks": {"registered": True}}

        def factory(*_args, **_kwargs):
            creations.append(object())
            return service

        from panda_agent.api import create_app

        with (
            patch.dict(os.environ, {"PANDA_READINESS_TTL_SECONDS": "5"}),
            patch("panda_agent.api.time", SimpleNamespace(monotonic=lambda: clock[0])),
        ):
            app = create_app(project_root=Path("."), runtime_probe=probe, service_factory=factory)
            with TestClient(app) as client:
                self.assertEqual(client.get("/health/ready").status_code, 200)
                self.assertEqual(len(calls), 1)
                clock[0] = 105.0
                self.assertEqual(client.get("/health/ready").status_code, 200)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(creations), 1)

    def test_readiness_refresh_blocks_qa_after_dependency_flip_without_rebuilding_service(self) -> None:
        state = {"valid": True, "runtime_status": "registered", "checks": {"registered": True}}
        calls: list[Path] = []
        service = FakeService()
        creations: list[object] = []
        from panda_agent.api import create_app

        def probe(*, project_root: Path):
            calls.append(project_root)
            return dict(state)

        def factory(*_args, **_kwargs):
            creations.append(object())
            return service

        with patch.dict(os.environ, {"PANDA_READINESS_TTL_SECONDS": "0"}):
            app = create_app(project_root=Path("."), runtime_probe=probe, service_factory=factory)
            with TestClient(app) as client:
                self.assertEqual(client.get("/health/ready").status_code, 200)
                state["valid"] = False
                state["runtime_status"] = "qdrant_unavailable"
                self.assertEqual(client.get("/health/ready").status_code, 503)
                self.assertEqual(client.post("/v1/qa", json={"question": "blocked"}).status_code, 503)
                state["valid"] = True
                state["runtime_status"] = "registered"
                self.assertEqual(client.post("/v1/qa", json={"question": "restored"}).status_code, 200)
        self.assertGreaterEqual(len(calls), 5)
        self.assertEqual(len(creations), 1)
        self.assertEqual([question for question, _ in service.calls], ["restored"])

    def test_version_uses_runtime_receipt_identity_without_readiness_side_effects(self) -> None:
        from panda_agent import kb_bundle, runtime
        from panda_agent.api import create_app

        with TemporaryDirectory() as directory:
            root = Path(directory)
            receipt = runtime.RuntimeIdentity(
                bundle_manifest_sha256="b" * 64,
                corpus_source_manifest_sha256="c" * 64,
                registered_at="2026-08-10T00:00:00Z",
                postgres=kb_bundle.PostgresState(
                    database=kb_bundle.DATABASE_NAME,
                    revision=runtime.SERVICE_REVISION,
                    table_counts={name: 0 for name in kb_bundle.SELECTED_TABLES},
                    index_fingerprint="f" * 64,
                ),
                qdrant=kb_bundle.QdrantState(
                    collection=kb_bundle.COLLECTION_NAME,
                    point_count=0,
                    dense_config={},
                    sparse_config={},
                    payload_indexes={},
                ),
                fastembed=kb_bundle.FastEmbedState(
                    model="Qdrant/bm25", vector_name="sparse", language="english", fastembed_version="0.0.0"
                ),
                embedding=runtime.EmbeddingIdentity(model=runtime.EMBEDDING_MODEL, dimensions=3072),
            )
            runtime._write_identity(runtime.runtime_identity_path(root), receipt)
            app = create_app(project_root=root, runtime_probe=lambda **_kwargs: {"valid": False})
            with TestClient(app) as client:
                response = client.get("/version")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["runtime"], {
            "knowledge_revision": receipt.knowledge_revision,
            "service_revision": receipt.service_revision,
            "source_manifest_sha256": "c" * 64,
            "index_fingerprint": "f" * 64,
            "status": "not_initialized",
        })

    def test_all_domain_result_statuses_remain_successful(self) -> None:
        for status in ("answered", "insufficient_evidence", "version_conflict"):
            envelope = answered_envelope()
            envelope = QAServiceEnvelope(
                request_id=envelope.request_id,
                result=QAResult.model_validate({**envelope.result.model_dump(), "status": status}),
                diagnostics=envelope.diagnostics,
                duration_ms=envelope.duration_ms,
            )
            app, _, _ = self.make_app(service=FakeService(envelope))
            with TestClient(app) as client:
                response = client.post("/v1/qa", json={"question": "hello"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["result"]["status"], status)

    def test_twenty_sequential_requests_reuse_one_service_without_leaking_state(self) -> None:
        app, service, creations = self.make_app()
        with TestClient(app) as client:
            for number in range(20):
                response = client.post("/v1/qa", json={"question": f"q{number}"})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["result"]["answer"], "Verified.")
        self.assertEqual([question for question, _ in service.calls], [f"q{number}" for number in range(20)])
        self.assertEqual(len(creations), 1)

    def test_cli_loopback_guard_and_declared_entry_points(self) -> None:
        from panda_agent.cli.api import _configure_panda_agent_logging, _loopback_host

        self.assertTrue(_loopback_host("127.0.0.1"))
        self.assertTrue(_loopback_host("::1"))
        self.assertTrue(_loopback_host("localhost"))
        self.assertFalse(_loopback_host("0.0.0.0"))
        self.assertFalse(_loopback_host("192.168.1.2"))
        with (Path(__file__).parents[2] / "pyproject.toml").open("rb") as stream:
            scripts = tomllib.load(stream)["project"]["scripts"]
        self.assertEqual(scripts["panda-qa-api"], "panda_agent.cli.api:main")
        self.assertEqual(scripts["panda-qa-runtime"], "panda_agent.cli.runtime:main")

        logger = logging.getLogger("panda_agent")
        previous = (logger.level, logger.propagate, list(logger.handlers))
        output = io.StringIO()
        try:
            with patch.dict(os.environ, {"PANDA_LOG_LEVEL": "DEBUG"}), redirect_stderr(output):
                _configure_panda_agent_logging()
                logger.debug('{"event":"started"}')
            self.assertEqual(logger.level, logging.DEBUG)
            self.assertEqual(output.getvalue(), '{"event":"started"}\n')
        finally:
            logger.handlers[:] = previous[2]
            logger.setLevel(previous[0])
            logger.propagate = previous[1]

    def test_model_reporting_reflects_configuration_and_unconfigured_state(self) -> None:
        with patch.dict(os.environ, {"QA_GENERATION_MODEL_ID": "test-env-model"}, clear=True):
            app, _, _ = self.make_app()
            with TestClient(app) as client:
                version = client.get("/version").json()
                self.assertEqual(version["models"]["generation"], "test-env-model")
                ui_health = client.get("/ui/health")
                self.assertEqual(ui_health.status_code, 200)
                self.assertIn("test-env-model", ui_health.text)

        with patch.dict(os.environ, {}, clear=True):
            app, _, _ = self.make_app()
            with TestClient(app) as client:
                version = client.get("/version").json()
                self.assertEqual(version["models"]["generation"], "unconfigured")
                ui_health = client.get("/ui/health")
                self.assertEqual(ui_health.status_code, 200)
                self.assertIn("unconfigured", ui_health.text)

        mock_settings = SimpleNamespace(generation_model="service-configured-model")
        mock_agent = SimpleNamespace(vertex=SimpleNamespace(settings=mock_settings))
        service_with_settings = FakeService()
        service_with_settings.agent = mock_agent
        with patch.dict(os.environ, {}, clear=True):
            app, _, _ = self.make_app(service=service_with_settings)
            with TestClient(app) as client:
                version = client.get("/version").json()
                self.assertEqual(version["models"]["generation"], "service-configured-model")
                ui_health = client.get("/ui/health")
                self.assertEqual(ui_health.status_code, 200)
                self.assertIn("service-configured-model", ui_health.text)


if __name__ == "__main__":
    unittest.main()
