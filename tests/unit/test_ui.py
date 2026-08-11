from __future__ import annotations

from pathlib import Path
import threading
import unittest

from fastapi.testclient import TestClient

from panda_agent.models import QAResult
from panda_agent.service import (
    QAServiceBusyError,
    QAServiceDeadlineError,
    QAServiceEnvelope,
    QAServiceError,
)


def ui_envelope(
    status: str = "answered", *, answer: str = "Verified.", evidence: list[dict] | None = None
) -> QAServiceEnvelope:
    return QAServiceEnvelope(
        request_id="00000000-0000-0000-0000-000000000001",
        result=QAResult.model_validate(
            {
                "status": status,
                "answer": answer,
                "claims": [
                    {
                        "claim_id": "claim-1",
                        "claim_text": "<strong>Claim</strong>",
                        "evidence_ids": ["evidence-https"],
                    }
                ]
                if evidence
                else [],
                "evidence": evidence or [],
                "resolved_versions": {"pandaroot": "locked@abc"},
            }
        ),
        diagnostics={
            "plan": {"intent": "api", "routing_method": "structured"},
            "retrieval_count": 4,
            "targeted_retrieval_count": 1,
            "revision_count": 1,
            "prompt": "must-not-leak",
            "rankings": [{"text": "must-not-leak"}],
            "internal_claim_audit": {"secret": "must-not-leak"},
        },
        duration_ms=17,
    )


class FakeService:
    def __init__(self, response: QAServiceEnvelope | Exception | None = None) -> None:
        self.response = response or ui_envelope()
        self.calls: list[tuple[str, str]] = []

    def execute(self, question: str) -> QAServiceEnvelope:
        self.calls.append((question, threading.current_thread().name))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class UIRouteContractTests(unittest.TestCase):
    """M8 UI routes must share the M7 application instance and service boundary."""

    def make_app(self, *, runtime=None, service=None):
        from panda_agent.api import create_app

        runtime = runtime or {"valid": True, "runtime_status": "registered", "checks": {}}
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

    def test_root_redirects_to_ui_and_ui_page_renders(self) -> None:
        app, service, creations = self.make_app()
        with TestClient(app) as client:
            root = client.get("/", follow_redirects=False)
            page = client.get("/ui")
            css = client.get("/static/ui.css")
            htmx = client.get("/static/vendor/htmx.min.js")

        self.assertEqual(root.status_code, 307)
        self.assertEqual(root.headers["location"], "/ui")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Evidence-grounded QA", page.text)
        self.assertEqual(css.status_code, 200)
        self.assertEqual(htmx.status_code, 200)
        self.assertEqual(service.calls, [])
        self.assertEqual(len(creations), 1)

    def test_api_and_ui_share_one_service_and_ui_executes_once(self) -> None:
        app, service, creations = self.make_app()
        with TestClient(app) as client:
            self.assertEqual(client.get("/health/live").status_code, 200)
            self.assertEqual(client.get("/health/ready").status_code, 200)
            self.assertEqual(client.get("/version").status_code, 200)
            api = client.post("/v1/qa", json={"question": "API question"})
            ui = client.post("/ui/qa", data={"question": "  UI question  "})
            self.assertIs(app.state.service, service)
        self.assertEqual(api.status_code, 200)
        self.assertEqual(api.json()["timings_ms"], {"total": 17})
        self.assertEqual(ui.status_code, 200)
        self.assertIn("Response", ui.text)
        self.assertEqual([question for question, _ in service.calls], ["API question", "UI question"])
        self.assertTrue(all(thread != threading.current_thread().name for _, thread in service.calls))
        self.assertEqual(len(creations), 1)

    def test_domain_statuses_render_as_successful_result_partials(self) -> None:
        for status, label in (
            ("answered", "Answered"),
            ("insufficient_evidence", "Insufficient evidence"),
            ("version_conflict", "Version conflict"),
        ):
            app, service, _ = self.make_app(service=FakeService(ui_envelope(status)))
            with TestClient(app) as client:
                response = client.post("/ui/qa", data={"question": "status check"})
            self.assertEqual(response.status_code, 200)
            self.assertIn(label, response.text)
            self.assertEqual(len(service.calls), 1)

    def test_result_escapes_untrusted_text_and_only_https_evidence_is_linked(self) -> None:
        evidence = [
            {
                "evidence_id": "evidence-https",
                "object_id": "object-https",
                "source_id": "<img src=x onerror=alert(1)>",
                "source_version_id": "pandaroot@abc",
                "text": "<script>alert('evidence')</script>",
                "locator": {"url": "https://example.invalid/doc?a=1"},
                "retrieval_channels": ["dense"],
                "score": 1.0,
                "authority_level": "primary",
            },
            {
                "evidence_id": "evidence-http",
                "object_id": "object-http",
                "source_id": "pandaroot",
                "source_version_id": "pandaroot@abc",
                "text": "http evidence",
                "locator": {"url": "http://example.invalid/not-link"},
                "retrieval_channels": ["exact"],
                "score": 0.9,
                "authority_level": "primary",
            },
            {
                "evidence_id": "evidence-file",
                "object_id": "object-file",
                "source_id": "pandaroot",
                "source_version_id": "pandaroot@abc",
                "text": "file evidence",
                "locator": {"url": "file:///private/path"},
                "retrieval_channels": ["exact"],
                "score": 0.8,
                "authority_level": "primary",
            },
        ]
        app, service, _ = self.make_app(
            service=FakeService(ui_envelope(answer="<script>alert('answer')</script>", evidence=evidence))
        )
        with TestClient(app) as client:
            response = client.post("/ui/qa", data={"question": "<img src=x onerror=alert(1)>"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("<script>alert", response.text)
        self.assertNotIn("<img src=x onerror", response.text)
        self.assertIn("&lt;script&gt;alert", response.text)
        self.assertIn(
            'href="https://example.invalid/doc?a=1" target="_blank" rel="noopener noreferrer"',
            response.text,
        )
        self.assertNotIn('href="http://example.invalid/not-link"', response.text)
        self.assertNotIn('href="file:///private/path"', response.text)
        self.assertNotIn("must-not-leak", response.text)
        self.assertIn("Intent", response.text)
        self.assertIn("Targeted retrievals", response.text)
        self.assertEqual(service.calls[0][0], "<img src=x onerror=alert(1)>")

    def test_ui_request_validation_origin_and_transport_errors(self) -> None:
        app, service, _ = self.make_app()
        with TestClient(app) as client:
            bad_type = client.post("/ui/qa", json={"question": "no"})
            forbidden = client.post(
                "/ui/qa", data={"question": "no"}, headers={"Origin": "https://other.invalid"}
            )
            validation = client.post("/ui/qa", data={"question": "   ", "unexpected": "x"})
            oversized = client.post(
                "/ui/qa",
                content=b"question=" + b"a" * 65_530,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        self.assertEqual(bad_type.status_code, 400)
        self.assertIn("The request is invalid", bad_type.text)
        self.assertEqual(forbidden.status_code, 403)
        self.assertIn("This request is not allowed", forbidden.text)
        self.assertEqual(validation.status_code, 422)
        self.assertIn("The question could not be accepted", validation.text)
        self.assertEqual(oversized.status_code, 400)
        self.assertEqual(service.calls, [])

        app, service, _ = self.make_app()
        with TestClient(app) as client:
            same_origin = client.post(
                "/ui/qa", data={"question": "allowed"}, headers={"Origin": "http://testserver"}
            )
        self.assertEqual(same_origin.status_code, 200)
        self.assertEqual([question for question, _ in service.calls], ["allowed"])

        errors = (
            (QAServiceBusyError("00000000-0000-0000-0000-000000000429"), 429, "The agent is busy"),
            (
                QAServiceError("00000000-0000-0000-0000-000000000500", "private", "secret"),
                500,
                "The request could not be completed",
            ),
            (QAServiceDeadlineError("00000000-0000-0000-0000-000000000504"), 504, "The request timed out"),
        )
        for error, expected_status, title in errors:
            app, _, _ = self.make_app(service=FakeService(error))
            with TestClient(app) as client:
                response = client.post("/ui/qa", data={"question": "run"})
            self.assertEqual(response.status_code, expected_status)
            self.assertIn(title, response.text)
            self.assertNotIn("secret", response.text)
            self.assertNotIn("private", response.text)

        app, _, _ = self.make_app(
            runtime={"valid": False, "runtime_status": "not_registered", "checks": {}}
        )
        with TestClient(app) as client:
            unavailable = client.post("/ui/qa", data={"question": "run"})
        self.assertEqual(unavailable.status_code, 503)
        self.assertIn("The local runtime is not ready", unavailable.text)

    def test_security_headers_protect_ui_and_api_responses(self) -> None:
        app, _, _ = self.make_app()
        with TestClient(app) as client:
            for response in (
                client.get("/ui"),
                client.get("/static/ui.css"),
                client.post("/v1/qa", json={"question": "x"}),
            ):
                self.assertEqual(
                    response.headers["content-security-policy"],
                    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                    "connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; "
                    "form-action 'self'",
                )
                self.assertEqual(response.headers["x-content-type-options"], "nosniff")
                self.assertEqual(response.headers["referrer-policy"], "no-referrer")
            self.assertEqual(client.get("/docs").status_code, 200)


if __name__ == "__main__":
    unittest.main()
