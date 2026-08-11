"""Authorized M8 overall smoke through the real loopback Web UI.

The test is skipped unless ``PANDA_RUN_LIVE_M8_UI=1``.  When enabled it
submits exactly the frozen eight-case M8 smoke set to the real QA service,
which calls the configured Vertex AI runtime and persists one ``qa_runs`` row
per question.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import threading
import time
import unittest
from urllib.request import urlopen

from dotenv import load_dotenv
from playwright.sync_api import expect, sync_playwright
import uvicorn
import yaml

from panda_agent.storage import Storage


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOLD_PATH = PROJECT_ROOT / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
EDGE_EXECUTABLE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
CASE_IDS = ("g001", "g013", "g027", "g051", "g070", "g090", "g105", "g112")
CODE_SOURCES = {"pandaroot", "luminosityfit", "restgas_determination"}
PAPER_SOURCES = {"li_2026", "karavdina_2015", "pflueger_2017"}


def _selected_case_ids() -> tuple[str, ...]:
    requested = os.getenv("PANDA_M8_LIVE_CASE_IDS", "").strip()
    if not requested:
        return CASE_IDS
    selected = tuple(value.strip() for value in requested.split(",") if value.strip())
    if not selected or len(selected) != len(set(selected)) or not set(selected) <= set(CASE_IDS):
        raise RuntimeError("PANDA_M8_LIVE_CASE_IDS must be a unique subset of the frozen M8 cases")
    return selected


def _load_cases(case_ids: tuple[str, ...]) -> list[dict]:
    payload = yaml.safe_load(GOLD_PATH.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload["questions"]}
    if set(CASE_IDS) - set(by_id):
        raise RuntimeError("The frozen M8 smoke cases are missing from Gold v2.6")
    return [by_id[case_id] for case_id in case_ids]


def _source_types(result: dict, diagnostics: dict, storage: Storage) -> set[str]:
    source_types: set[str] = set()
    for item in result["evidence"]:
        source_id = item["source_id"]
        if source_id in PAPER_SOURCES:
            source_types.add("paper")
        if "sphinx" in source_id:
            source_types.add("documentation")
        if "workflow" in item.get("retrieval_channels", []) or item["object_id"].startswith("workflow."):
            source_types.add("workflow")
    workflow_items = diagnostics.get("channels", {}).get("workflow", [])
    if workflow_items:
        source_types.add("workflow")
    object_ids = {
        item.get("object_id")
        for items in diagnostics.get("channels", {}).values()
        for item in items
        if isinstance(item, dict) and isinstance(item.get("object_id"), str)
    }
    object_ids.update(
        item["object_id"] for item in result["evidence"] if isinstance(item.get("object_id"), str)
    )
    if object_ids:
        with storage.connect() as connection:
            records = connection.execute(
                "SELECT object_type,source_id FROM knowledge_objects WHERE object_id = ANY(%s)",
                (list(object_ids),),
            ).fetchall()
        for object_type, source_id in records:
            if source_id in CODE_SOURCES and object_type not in {
                "readme_section", "readme_section_chunk", "sphinx_page", "sphinx_section"
            }:
                source_types.add("code")
            if "sphinx" in source_id or object_type in {
                "readme_section", "readme_section_chunk", "sphinx_page", "sphinx_section"
            }:
                source_types.add("documentation")
            if source_id in PAPER_SOURCES:
                source_types.add("paper")
            if object_type == "workflow":
                source_types.add("workflow")
    return source_types


@unittest.skipUnless(os.getenv("PANDA_RUN_LIVE_M8_UI") == "1", "live M8 UI smoke is opt-in")
@unittest.skipUnless(EDGE_EXECUTABLE.is_file(), "Microsoft Edge is unavailable")
class M8LiveUISmokeTests(unittest.TestCase):
    def test_eight_intents_through_real_ui(self) -> None:
        # Mirror the packaged CLI: find the configured workspace .env rather
        # than assuming it lives inside the repository root.
        load_dotenv()
        from panda_agent.api import create_app
        from panda_agent.service import QAService

        cases = _load_cases(_selected_case_ids())
        storage = Storage()
        initialization_errors: list[str] = []

        def service_factory(project_root, **kwargs):
            try:
                return QAService(project_root, **kwargs)
            except Exception as exc:
                initialization_errors.append(type(exc).__name__)
                raise

        app = create_app(PROJECT_ROOT, service_factory=service_factory)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        server = uvicorn.Server(
            uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)
        )
        server_thread = threading.Thread(target=server.run, name="m8-live-ui", daemon=True)
        server_thread.start()
        base_url = f"http://127.0.0.1:{port}"
        try:
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                if not server_thread.is_alive():
                    self.fail("The real M8 loopback service exited during startup")
                try:
                    with urlopen(f"{base_url}/health/ready", timeout=2) as response:
                        if response.status == 200:
                            break
                except OSError:
                    time.sleep(0.1)
            else:
                runtime_status = getattr(getattr(app, "state", None), "runtime", {}).get(
                    "runtime_status", "unknown"
                )
                detail = initialization_errors[-1] if initialization_errors else "service initialization did not run"
                self.fail(
                    f"The real M8 loopback service did not become ready ({runtime_status}; {detail})"
                )

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path=str(EDGE_EXECUTABLE), headless=True)
                try:
                    page = browser.new_page(viewport={"width": 1280, "height": 900})
                    page.goto(f"{base_url}/ui", wait_until="domcontentloaded")
                    expect(page.locator("#runtime-status .health-label")).to_have_text("Ready")
                    seen_request_ids: set[str] = set()
                    for case in cases:
                        page.locator("#question").fill(case["query"])
                        with page.expect_response(
                            lambda response: response.url.endswith("/ui/qa"), timeout=330_000
                        ) as response_info:
                            page.locator("button[type=submit]").click()
                        self.assertEqual(response_info.value.status, 200, case["id"])
                        expect(page.locator(".result-card")).to_be_visible()
                        payload = json.loads(page.locator(".result-card").get_attribute("data-result-json"))
                        request_id = payload["request_id"]
                        result = payload["result"]
                        diagnostics = payload["diagnostics"]

                        self.assertNotIn(request_id, seen_request_ids)
                        seen_request_ids.add(request_id)
                        self.assertEqual(result["status"], "answered", case["id"])
                        self.assertTrue(result["claims"], case["id"])
                        self.assertTrue(result["evidence"], case["id"])
                        self.assertEqual(result["verification_errors"], [], case["id"])
                        evidence_ids = {item["evidence_id"] for item in result["evidence"]}
                        for claim in result["claims"]:
                            self.assertTrue(set(claim["evidence_ids"]) <= evidence_ids, case["id"])
                        visible_claims = result["answer"] + " " + " ".join(
                            claim["claim_text"] for claim in result["claims"]
                        )
                        for identifier in case.get("required_identifiers", []):
                            self.assertIn(identifier["text"], visible_claims, case["id"])
                        allowed_versions = set(case["allowed_source_versions"])
                        self.assertTrue(
                            all(item["source_version_id"] in allowed_versions for item in result["evidence"]),
                            case["id"],
                        )
                        self.assertTrue(
                            set(case["required_source_types"]) <= _source_types(result, diagnostics, storage),
                            case["id"],
                        )
                        self.assertTrue(diagnostics.get("plan"), case["id"])
                        self.assertTrue(diagnostics.get("channels"), case["id"])
                        self.assertTrue(diagnostics.get("workflow_trace"), case["id"])
                        self.assertEqual(page.locator("[role=tab]").count(), 5, case["id"])

                        with storage.connect() as connection:
                            rows = connection.execute(
                                "SELECT status,completed_at,duration_ms,intent,error_code,node_timings,model_usage "
                                "FROM qa_runs WHERE run_id=%s",
                                (request_id,),
                            ).fetchall()
                        self.assertEqual(len(rows), 1, case["id"])
                        status, completed_at, duration_ms, intent, error_code, node_timings, model_usage = rows[0]
                        self.assertEqual(status, "answered", case["id"])
                        self.assertIsNotNone(completed_at, case["id"])
                        self.assertGreaterEqual(duration_ms, 0, case["id"])
                        self.assertEqual(intent, case["intent"], case["id"])
                        self.assertIsNone(error_code, case["id"])
                        self.assertTrue(node_timings, case["id"])
                        self.assertTrue(model_usage, case["id"])
                        print(
                            json.dumps(
                                {
                                    "case_id": case["id"],
                                    "request_id": request_id,
                                    "status": status,
                                    "claims": len(result["claims"]),
                                    "evidence": len(result["evidence"]),
                                    "duration_ms": duration_ms,
                                },
                                sort_keys=True,
                            )
                        )
                finally:
                    browser.close()
        finally:
            server.should_exit = True
            server_thread.join(timeout=30)
            if server_thread.is_alive():
                raise RuntimeError("The M8 live loopback service did not stop")


if __name__ == "__main__":
    unittest.main()
