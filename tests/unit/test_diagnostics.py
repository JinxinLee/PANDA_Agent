from __future__ import annotations

import threading
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from panda_agent.models import QAResult
from panda_agent.service import QAServiceBusyError, QAServiceDeadlineError, QAServiceEnvelope, QAServiceError


def _envelope() -> QAServiceEnvelope:
    return QAServiceEnvelope(
        request_id="00000000-0000-0000-0000-000000000008",
        result=QAResult.model_validate(
            {
                "status": "answered",
                "answer": "Verified answer.",
                "claims": [],
                "evidence": [],
                "resolved_versions": {"pandaroot": "locked@abc"},
            }
        ),
        diagnostics={
            "plan": {
                "intent": "data_flow",
                "routing_method": "structured",
                "target_repositories": ["pandaroot"],
                "resolved_versions": {"pandaroot": "locked@abc"},
                "concept_scopes": {"vertex": "event_poca"},
                "resolved_aliases": {"poca": "event_poca"},
                "source_budgets": {"code": 1.0},
                "required_source_types": ["code"],
                "prompt": "must-not-leak",
            },
            "rankings": {
                "dense": ["object-b", "object-a"],
                "exact": ["object-a"],
                "graph": ["object-c"],
                "unknown": ["object-z"],
            },
            "fusion_scores": {"object-a": 0.8, "object-b": 0.9},
            "reranked_object_ids": ["object-b", "object-a"],
            "ranked_object_ids": ["object-a", "object-b"],
            "excluded": [
                {"object_id": "object-x", "reason": "duplicate", "candidate_text": "must-not-leak"}
            ],
            "selected_evidence_ids": ["evidence-1"],
            "retrieval_count": 2,
            "targeted_retrieval_count": 1,
            "revision_count": 1,
            "verification_errors": ["unsupported requested symbol: must-not-leak"],
            "claim_audit": [{"claim_text": "must-not-leak"}],
        },
        duration_ms=17,
        node_timings={"retrieve": 7.0, "workflow": 17.0},
        model_usage={"model_calls": 2, "token_usage": 11, "generation_calls": 2, "embedding_calls": 0},
    )


class FakeService:
    def __init__(self, response: QAServiceEnvelope | Exception | None = None) -> None:
        self.calls: list[tuple[str, str]] = []
        self.response = response or _envelope()

    def execute(self, question: str) -> QAServiceEnvelope:
        self.calls.append((question, threading.current_thread().name))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class PublicDiagnosticsContractTests(unittest.TestCase):
    def make_app(self, *, runtime=None, service=None):
        from panda_agent.api import create_app

        service = service or FakeService()
        runtime = runtime or {"valid": True, "runtime_status": "registered", "checks": {}}
        app = create_app(
            project_root=Path("."),
            runtime_probe=lambda **_kwargs: runtime,
            service_factory=lambda *_args, **_kwargs: service,
        )
        return app, service

    def test_public_projection_is_deterministic_and_excludes_internal_content(self) -> None:
        from panda_agent.api import _ui_diagnostics

        public = _ui_diagnostics(
            _envelope().diagnostics,
            node_timings=_envelope().node_timings,
            model_usage=_envelope().model_usage,
        )
        self.assertEqual(
            list(public),
            ["plan", "channels", "fusion", "exclusions", "selected_evidence_ids", "workflow_trace"],
        )
        self.assertEqual(
            list(public["plan"]),
            [
                "intent", "routing_method", "target_repositories", "resolved_versions",
                "concept_scopes", "resolved_aliases", "source_budgets", "required_source_types",
            ],
        )
        self.assertEqual(list(public["channels"]), ["exact", "dense", "graph"])
        self.assertEqual(public["channels"]["exact"], [{"object_id": "object-a", "rank": 1}])
        self.assertEqual(
            public["fusion"],
            [
                {"object_id": "object-b", "score": 0.9, "rerank_rank": 1, "final_rank": 2},
                {"object_id": "object-a", "score": 0.8, "rerank_rank": 2, "final_rank": 1},
            ],
        )
        self.assertEqual(public["exclusions"], [{"object_id": "object-x", "reason": "duplicate"}])
        self.assertEqual(public["workflow_trace"]["verification_error_codes"], ["unsupported_symbol"])
        self.assertEqual(public["workflow_trace"]["node_timings"], {"retrieve": 7.0, "workflow": 17.0})
        self.assertEqual(public["workflow_trace"]["model_usage"], _envelope().model_usage)
        self.assertNotIn("must-not-leak", str(public))
        self.assertNotIn("claim_audit", str(public))

    def test_diagnose_and_health_use_one_service_without_exposing_qa_internals(self) -> None:
        app, service = self.make_app()
        with TestClient(app) as client:
            diagnose = client.post("/v1/qa/diagnose", json={"question": "diagnose"})
            health = client.get("/ui/health")
            openapi = client.get("/openapi.json").json()

        self.assertEqual(diagnose.status_code, 200)
        self.assertEqual(diagnose.json()["node_timings_ms"], _envelope().node_timings)
        self.assertEqual(diagnose.json()["model_usage"], _envelope().model_usage)
        self.assertEqual(diagnose.json()["diagnostics"]["plan"]["intent"], "data_flow")
        self.assertNotIn("must-not-leak", diagnose.text)
        self.assertEqual(health.status_code, 200)
        self.assertEqual(len(service.calls), 1)
        self.assertIn("/v1/qa/diagnose", openapi["paths"])

    def test_diagnose_reuses_the_sanitized_api_error_contract(self) -> None:
        errors = (
            (QAServiceBusyError("00000000-0000-0000-0000-000000000429"), 429, "busy"),
            (QAServiceDeadlineError("00000000-0000-0000-0000-000000000504"), 504, "deadline_exceeded"),
            (QAServiceError("00000000-0000-0000-0000-000000000500", "private", "secret"), 500, "private"),
        )
        for error, status, code in errors:
            app, service = self.make_app(service=FakeService(error))
            with TestClient(app) as client:
                response = client.post("/v1/qa/diagnose", json={"question": "diagnose"})
            self.assertEqual(response.status_code, status)
            self.assertEqual(response.json()["error_code"], code)
            self.assertNotIn("secret", response.text)
            self.assertEqual(len(service.calls), 1)

        app, service = self.make_app(runtime={"valid": False, "runtime_status": "not_registered", "checks": {}})
        with TestClient(app) as client:
            unavailable = client.post("/v1/qa/diagnose", json={"question": "diagnose"})
            invalid = client.post("/v1/qa/diagnose", json={"question": "   "})
        self.assertEqual(unavailable.status_code, 503)
        self.assertEqual(unavailable.json()["error_code"], "service_unavailable")
        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(service.calls, [])


if __name__ == "__main__":
    unittest.main()
