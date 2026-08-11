"""Real-browser M8 P1 acceptance against a loopback fake QA service.

The test deliberately starts Uvicorn and drives the packaged local assets with
the installed Microsoft Edge executable.  It never initializes the real
runtime, database, vector store, or Vertex client.
"""

from __future__ import annotations

import json
from pathlib import Path
import socket
import tempfile
import threading
import time
import unittest
from urllib.request import urlopen

from playwright.sync_api import Browser, Page, expect, sync_playwright
import uvicorn

from panda_agent.models import QAResult
from panda_agent.service import (
    QAServiceBusyError,
    QAServiceDeadlineError,
    QAServiceEnvelope,
    QAServiceError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EDGE_EXECUTABLE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
SCREENSHOT_PATH = PROJECT_ROOT / "docs" / "images" / "m8_ui.png"


def _envelope(status: str = "answered") -> QAServiceEnvelope:
    answer = {
        "answered": "Fake answer: event_poca is passed through the second PID stage.",
        "insufficient_evidence": "The locked fake corpus does not establish that API.",
        "version_conflict": "The requested revision is outside the locked fake source version.",
    }[status]
    evidence = [
        {
            "evidence_id": "evidence-fake-1",
            "object_id": "object.fake.1",
            "source_id": "fake-pandaroot",
            "source_version_id": "fake-pandaroot@locked",
            "text": "Fake evidence excerpt for browser-only acceptance.",
            "locator": {
                "path": "macro/fake_pipeline.C",
                "symbol": "FakePipeline::run",
                "start_line": 11,
                "end_line": 13,
                "url": "https://example.invalid/fake-pandaroot",
            },
            "retrieval_channels": ["exact", "dense"],
            "score": 0.97,
            "authority_level": "primary",
        }
    ]
    claims = [
        {
            "claim_id": "claim-fake-1",
            "claim_text": "The fake pipeline preserves the event alignment.",
            "evidence_ids": ["evidence-fake-1"],
        }
    ]
    return QAServiceEnvelope(
        request_id=f"00000000-0000-0000-0000-00000000{status[-2:].encode().hex()[-4:]}",
        result=QAResult.model_validate(
            {
                "status": status,
                "answer": answer,
                "claims": claims,
                "evidence": evidence,
                "resolved_versions": {"fake-pandaroot": "fake-pandaroot@locked"},
                "verification_errors": [],
            }
        ),
        diagnostics={
            "plan": {
                "intent": "data_flow",
                "routing_method": "fake_structured_plan",
                "target_repositories": ["fake-pandaroot"],
                "resolved_versions": {"fake-pandaroot": "fake-pandaroot@locked"},
                "concept_scopes": {"vertex": "event_poca"},
                "resolved_aliases": {"fake-poca": "event_poca"},
                "source_budgets": {"code": 0.7, "documentation": 0.3},
                "required_source_types": ["code"],
            },
            "rankings": {
                "exact": ["object.fake.1"],
                "dense": ["object.fake.1"],
                "sparse": ["object.fake.2"],
                "workflow": ["workflow.fake.1"],
                "graph": ["graph.fake.1"],
            },
            "fusion_scores": {"object.fake.1": 0.97},
            "reranked_object_ids": ["object.fake.1"],
            "ranked_object_ids": ["object.fake.1"],
            "selected_evidence_ids": ["evidence-fake-1"],
            "excluded": [{"object_id": "object.fake.2", "reason": "duplicate_locator"}],
            "retrieval_count": 2,
            "targeted_retrieval_count": 1,
            "revision_count": 1,
            "verification_errors": [],
        },
        duration_ms=19,
        node_timings={"normalize": 1.0, "retrieve": 8.0, "answer": 10.0},
        model_usage={"model_calls": 2, "token_usage": 42, "generation_calls": 1, "embedding_calls": 1},
    )


class FakeBrowserService:
    """A deterministic QAService boundary keyed only by harmless fake input."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self._lock = threading.Lock()

    def execute(self, question: str) -> QAServiceEnvelope:
        with self._lock:
            self.calls.append(question)
        if question == "busy":
            raise QAServiceBusyError("00000000-0000-0000-0000-000000000429")
        if question == "deadline":
            raise QAServiceDeadlineError("00000000-0000-0000-0000-000000000504")
        if question == "internal":
            raise QAServiceError("00000000-0000-0000-0000-000000000500", "fake_internal", "fake only")
        if question == "unavailable":
            from panda_agent.api import _ServiceUnavailableError

            raise _ServiceUnavailableError()
        if question == "insufficient":
            return _envelope("insufficient_evidence")
        if question == "conflict":
            return _envelope("version_conflict")
        return _envelope("answered")


@unittest.skipUnless(EDGE_EXECUTABLE.is_file(), "Microsoft Edge is not installed at the required path")
class M8PlaywrightAcceptanceTests(unittest.TestCase):
    """Exercise HTMX swaps, result actions, safety UI, and keyboard navigation."""

    @classmethod
    def setUpClass(cls) -> None:
        from panda_agent.api import create_app

        cls.service = FakeBrowserService()
        cls.app = create_app(
            project_root=PROJECT_ROOT,
            runtime_probe=lambda *, project_root: {
                "valid": True,
                "runtime_status": "fake_registered",
                "checks": {"fake": True},
            },
            service_factory=lambda project_root, **_kwargs: cls.service,
        )
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            cls.port = probe.getsockname()[1]
        cls.server = uvicorn.Server(
            uvicorn.Config(cls.app, host="127.0.0.1", port=cls.port, log_level="warning", access_log=False)
        )
        cls.server_thread = threading.Thread(target=cls.server.run, name="m8-playwright-uvicorn", daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                with urlopen(f"{cls.base_url}/health/live", timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(0.05)
        else:
            raise RuntimeError("Loopback Uvicorn test server did not start")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.should_exit = True
        cls.server_thread.join(timeout=10)
        if cls.server_thread.is_alive():
            raise RuntimeError("Loopback Uvicorn test server did not stop")

    def _new_page(self, browser: Browser) -> tuple[Page, list[str], list[str]]:
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        context.grant_permissions(["clipboard-read", "clipboard-write"], origin=self.base_url)
        page = context.new_page()
        page.route("**/favicon.ico", lambda route: route.fulfill(status=204))
        console_errors: list[str] = []
        page_errors: list[str] = []
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        return page, console_errors, page_errors

    def _submit(self, page: Page, question: str, expected_selector: str) -> None:
        before = len(self.service.calls)
        page.locator("#question").fill(question)
        page.locator("button[type=submit]").click()
        expect(page.locator(expected_selector)).to_be_visible()
        self.assertEqual(len(self.service.calls), before + 1, f"{question} must execute QAService exactly once")

    def test_m8_ui_in_real_edge(self) -> None:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=str(EDGE_EXECUTABLE), headless=True)
            try:
                page, console_errors, page_errors = self._new_page(browser)

                page.goto(f"{self.base_url}/ui", wait_until="domcontentloaded")
                expect(page.locator("#runtime-status .health-label")).to_have_text("Ready")
                expect(page.locator("h1")).to_have_text("Evidence-grounded QA")

                self._submit(page, "answered", ".result-card")
                expect(page.locator(".status-badge")).to_have_text("Answered")
                expect(page.locator(".answer")).to_have_text(
                    "Fake answer: event_poca is passed through the second PID stage."
                )
                expect(page.locator(".claim")).to_contain_text("fake pipeline preserves")
                expect(page.locator("#evidence-evidence-fake-1")).to_be_visible()

                tabs = page.locator("[role=tab]")
                self.assertEqual(tabs.count(), 5)
                page.locator("#tab-query-plan").focus()
                page.keyboard.press("ArrowRight")
                expect(page.locator("#tab-retrieval-channels")).to_have_attribute("aria-selected", "true")
                for tab_id in ("query-plan", "retrieval-channels", "fusion-rerank", "exclusions", "workflow-trace"):
                    page.locator(f"#tab-{tab_id}").click()
                    expect(page.locator(f"#panel-{tab_id}")).to_be_visible()

                page.locator(".citation-link").click()
                expect(page.locator("#evidence-evidence-fake-1")).to_be_focused()

                page.locator("[data-copy-answer]").click()
                expect(page.locator("[data-action-status]")).to_have_text("Answer copied.")
                self.assertEqual(
                    page.evaluate("navigator.clipboard.readText()"),
                    "Fake answer: event_poca is passed through the second PID stage.",
                )

                with tempfile.TemporaryDirectory() as temp_dir:
                    with page.expect_download() as downloaded:
                        page.locator("[data-download-json]").click()
                    download_path = Path(temp_dir) / "result.json"
                    downloaded.value.save_as(download_path)
                    payload = json.loads(download_path.read_text(encoding="utf-8"))
                self.assertIn("request_id", payload)
                self.assertEqual(payload["result"]["status"], "answered")
                self.assertIn("diagnostics", payload)
                self.assertNotIn("prompt", json.dumps(payload).casefold())

                SCREENSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(SCREENSHOT_PATH), full_page=True)

                for question, title in (
                    ("insufficient", "Insufficient evidence"),
                    ("conflict", "Version conflict"),
                ):
                    self._submit(page, question, ".result-card")
                    expect(page.locator(".status-badge")).to_have_text(title)

                for question, status, title in (
                    ("busy", 429, "The agent is busy"),
                    ("unavailable", 503, "The local runtime is not ready"),
                    ("deadline", 504, "The request timed out"),
                    ("internal", 500, "The request could not be completed"),
                ):
                    with page.expect_response(
                        lambda response, expected=status: response.url.endswith("/ui/qa")
                        and response.status == expected
                    ):
                        self._submit(page, question, ".error-card")
                    expect(page.locator(".error-card h2")).to_have_text(title)

                page.set_viewport_size({"width": 390, "height": 844})
                expect(page.locator(".app-shell")).to_be_visible()
                shell_box = page.locator(".app-shell").bounding_box()
                self.assertIsNotNone(shell_box)
                self.assertLessEqual(shell_box["width"], 390)
                expected_network_errors = (
                    "server responded with a status of 429",
                    "server responded with a status of 503",
                    "server responded with a status of 504",
                    "server responded with a status of 500",
                    "frame-ancestors' is ignored when delivered via a <meta> element",
                )
                unexpected_console_errors = [
                    message
                    for message in console_errors
                    if not any(expected in message for expected in expected_network_errors)
                ]
                self.assertEqual(unexpected_console_errors, [])
                self.assertFalse(any("violates the following content security policy" in message.casefold() for message in console_errors))
                self.assertEqual(page_errors, [])
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main()
