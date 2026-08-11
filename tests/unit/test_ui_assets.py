from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = ROOT / "src" / "panda_agent" / "templates"
STATIC_ROOT = ROOT / "src" / "panda_agent" / "static"


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_ROOT)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        undefined=StrictUndefined,
    )


def _result(*, diagnostics: dict, answer: str = "Verified answer.") -> SimpleNamespace:
    evidence = SimpleNamespace(
        evidence_id="evidence-1",
        source_id="pandaroot",
        source_version_id="pandaroot@locked",
        authority_level="primary_source",
        text="<script>alert('evidence')</script>",
        retrieval_channels=["dense"],
        locator=SimpleNamespace(
            path="macro/target/ana.C",
            symbol="PndTask",
            start_line=10,
            end_line=20,
            pdf_page=None,
            printed_page=None,
            section_path=["Chapter 1", "Overview"],
            url="https://example.invalid/doc",
        ),
    )
    claim = SimpleNamespace(
        claim_id="claim-1",
        claim_text="<img src=x onerror=alert(1)>",
        evidence_ids=["evidence-1"],
    )
    return SimpleNamespace(
        status="answered",
        answer=answer,
        claims=[claim],
        evidence=[evidence],
        resolved_versions={"pandaroot": "pandaroot@locked"},
        verification_errors=[],
    )


class UIAssetTests(unittest.TestCase):
    def test_all_html_templates_parse_with_strict_undefined(self) -> None:
        env = _environment()
        for path in TEMPLATE_ROOT.rglob("*.html"):
            env.get_template(path.relative_to(TEMPLATE_ROOT).as_posix())

    def test_health_partial_renders_safe_runtime_identity(self) -> None:
        template = _environment().get_template("partials/health.html")
        rendered = template.render(
            ready=True,
            runtime={
                "status": "registered",
                "knowledge_revision": "knowledge-v1",
                "service_revision": "0005",
                "generation_model": "gemini-3.6-flash",
                "embedding_model": "gemini-embedding-2",
            },
        )
        self.assertIn("Ready", rendered)
        self.assertIn("gemini-embedding-2", rendered)
        self.assertNotIn("ADC", rendered)
        self.assertNotIn("password", rendered.casefold())
        self.assertNotIn("file://", rendered)

    def test_result_escapes_content_and_contains_all_diagnostic_sections(self) -> None:
        template = _environment().get_template("partials/result.html")
        diagnostics = {
            "plan": {
                "intent": "data_flow",
                "routing_method": "structured",
                "target_repositories": ["pandaroot"],
                "resolved_versions": {"pandaroot": "locked"},
                "concept_scopes": {"vertex": "event"},
                "resolved_aliases": {"POCA": "event_poca"},
                "source_budgets": {"code": 0.7},
                "required_source_types": ["code"],
            },
            "channels": {
                "exact": [{"object_id": "object-1", "rank": 1}],
                "dense": [{"object_id": "object-2", "rank": 1}],
                "sparse": [],
                "paper": [],
                "workflow": [],
                "graph": [],
            },
            "fusion": [{"object_id": "object-1", "score": 0.9, "rerank_rank": 1, "final_rank": 1}],
            "exclusions": [{"object_id": "object-x", "reason": "duplicate"}],
            "selected_evidence_ids": ["evidence-1"],
            "workflow_trace": {
                "retrieval_count": 1,
                "targeted_retrieval_count": 0,
                "revision_count": 0,
                "verification_error_codes": [],
                "node_timings": {"retrieve": 4},
                "model_usage": {"model_calls": 1},
            },
        }
        result_json = json.dumps({"answer": "<script>alert(1)</script>"}, ensure_ascii=False)
        rendered = template.render(
            result=_result(diagnostics=diagnostics, answer="<script>alert('answer')</script>"),
            diagnostics=diagnostics,
            result_json=result_json,
            request_id="request-123",
            timings_ms={"total": 42},
        )
        self.assertIn("Query Plan", rendered)
        self.assertIn("Retrieval Channels", rendered)
        self.assertIn("Fusion &amp; Rerank", rendered)
        self.assertIn("Exclusions", rendered)
        self.assertIn("Workflow Trace", rendered)
        self.assertIn("Copy answer", rendered)
        self.assertIn("Download JSON", rendered)
        self.assertNotIn("<script>alert", rendered)
        self.assertNotIn("<img src=x onerror", rendered)
        self.assertIn("&lt;script&gt;alert", rendered)
        self.assertIn("data-result-json=", rendered)
        self.assertNotIn("<script type=\"application/json\"", rendered)
        self.assertNotIn("|safe", rendered)

    def test_empty_diagnostic_sections_are_explicit(self) -> None:
        template = _environment().get_template("partials/result.html")
        diagnostics = {
            "plan": {},
            "channels": {},
            "fusion": [],
            "exclusions": [],
            "selected_evidence_ids": [],
            "workflow_trace": {},
        }
        rendered = template.render(
            result=_result(diagnostics=diagnostics),
            diagnostics=diagnostics,
            result_json="{}",
            request_id="request-empty",
            timings_ms={"total": 0},
        )
        self.assertIn("No query plan was recorded", rendered)
        self.assertIn("No retrieval channel details were recorded", rendered)
        self.assertIn("No fusion or rerank details were recorded", rendered)
        self.assertIn("No evidence was excluded after fusion", rendered)
        self.assertIn("No workflow trace was recorded", rendered)

    def test_static_assets_are_local_and_expose_required_behaviors(self) -> None:
        js = (STATIC_ROOT / "ui.js").read_text(encoding="utf-8")
        css = (STATIC_ROOT / "ui.css").read_text(encoding="utf-8")
        htmx = (STATIC_ROOT / "vendor" / "htmx.min.js").read_text(encoding="utf-8")
        self.assertNotIn("eval(", js)
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("fetch(", js)
        for token in ("data-copy-answer", "data-download-json", "ArrowRight", "ArrowLeft", "Home", "End", "createObjectURL", "clipboard", "path === \"/ui/qa\"", "detail.shouldSwap = true", "detail.isError = false", "status >= 400"):
            self.assertIn(token, js)
        for token in ("diagnostic-tabs", "tab-button", "diagnostic-table", "sr-only", "@media"):
            self.assertIn(token, css)
        self.assertGreater(len(htmx), 1000)
        self.assertIn("htmx", htmx.casefold())


if __name__ == "__main__":
    unittest.main()
