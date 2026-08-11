import json
import sys
import threading
import time
import unittest
from uuid import UUID
from pathlib import Path
from unittest.mock import Mock, patch

from panda_agent.service import (
    QAService,
    QAServiceBusyError,
    QAServiceDeadlineError,
    QAServiceError,
)


class RecordingConnection:
    def __init__(self, fail_at=None):
        self.calls = []
        self.fail_at = fail_at

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query, params=None):
        self.calls.append((query, params))
        if self.fail_at == len(self.calls):
            raise RuntimeError("persistence unavailable")
        return self


class RecordingStorage:
    def __init__(self, fail_at=None):
        self.connection = RecordingConnection(fail_at)

    def connect(self):
        return self.connection


class DeadlineOrderingConnection(RecordingConnection):
    def __init__(self):
        super().__init__()
        self.deadline_update_started = threading.Event()
        self.release_deadline_update = threading.Event()
        self.cleanup_started = threading.Event()

    def execute(self, query, params=None):
        self.calls.append((query, params))
        if query.startswith("UPDATE qa_runs SET status="):
            self.deadline_update_started.set()
            if not self.release_deadline_update.wait(timeout=2):
                raise RuntimeError("deadline update was not released")
        elif query.startswith("UPDATE qa_runs SET node_timings="):
            self.cleanup_started.set()
        return self


class DeadlineOrderingStorage:
    def __init__(self):
        self.connection = DeadlineOrderingConnection()

    def connect(self):
        return self.connection


class StaticGraph:
    def __init__(self, state):
        self.state = state
        self.worker_name = None

    def invoke(self, _input):
        self.worker_name = threading.current_thread().name
        return self.state


class FailingGraph:
    def invoke(self, _input):
        raise RuntimeError("fake worker failure")


class BlockingGraph:
    def __init__(self, state):
        self.state = state
        self.started = threading.Event()
        self.release = threading.Event()
        self.finished = threading.Event()

    def invoke(self, _input):
        self.started.set()
        self.release.wait(timeout=5)
        self.finished.set()
        return self.state


class FakeAgent:
    def __init__(self, graph, storage):
        self.graph = graph
        self.retriever = type("Retriever", (), {"storage": storage})()

    def run_detailed(self, question):
        return self.graph.invoke({"question": question})


def answered_state():
    return {
        "result": {
            "status": "answered",
            "answer": "A verified answer. [e1]",
            "claims": [{"claim_id": "c1", "claim_text": "A verified answer.", "evidence_ids": ["e1"]}],
            "evidence": [{
                "evidence_id": "e1", "object_id": "o1", "source_id": "pandaroot",
                "source_version_id": "pandaroot@locked", "text": "private source body",
                "locator": {"path": "x.h", "symbol": None, "start_line": 1, "end_line": 1,
                            "pdf_page": None, "printed_page": None, "section_path": [], "url": None,
                            "snapshot_date": None},
                "retrieval_channels": ["exact"], "score": 1.0, "authority_level": "primary",
            }],
            "resolved_versions": {"pandaroot": "locked"},
            "verification_errors": [],
        },
        "diagnostics": {
            "plan": {"intent": "usage"},
            "selected_evidence_ids": ["e1"],
            "targeted_retrieval_count": 0,
            "revision_count": 0,
            "verification_errors": [],
        },
    }


class QAServiceContractTests(unittest.TestCase):
    def test_deadline_cleanup_waits_for_client_terminal_persistence(self):
        storage = DeadlineOrderingStorage()
        state = answered_state()
        state["node_timings_ms"] = {"retrieve": 7, "finalize": 3, "workflow": 12}
        state["model_usage"] = {"model_calls": 2, "generation_calls": 2, "token_usage": 11}
        graph = BlockingGraph(state)
        service = QAService(
            agent=FakeAgent(graph, storage), origin="api", deadline_seconds=0.01
        )
        outcome = {}
        caller = threading.Thread(
            target=lambda: outcome.setdefault("error", self._capture_error(service, "deadline race"))
        )
        caller.start()
        self.assertTrue(graph.started.wait(timeout=2))
        self.assertTrue(storage.connection.deadline_update_started.wait(timeout=2))

        try:
            graph.release.set()
            self.assertTrue(graph.finished.wait(timeout=2))
            self.assertFalse(storage.connection.cleanup_started.wait(timeout=0.2))
        finally:
            storage.connection.release_deadline_update.set()
            caller.join(timeout=2)
            self.assertFalse(caller.is_alive())
            self.assertTrue(storage.connection.cleanup_started.wait(timeout=2))
            self.assertTrue(service._gate.acquire(timeout=2))
            service._gate.release()

        self.assertIsInstance(outcome["error"], QAServiceDeadlineError)
        self.assertEqual(len(storage.connection.calls), 3)
        self.assertTrue(storage.connection.calls[1][0].startswith("UPDATE qa_runs SET status="))
        self.assertTrue(storage.connection.calls[2][0].startswith("UPDATE qa_runs SET node_timings="))
        self.assertEqual(storage.connection.calls[2][1][0].obj["retrieve"], 7)
        self.assertEqual(storage.connection.calls[2][1][1].obj["model_calls"], 2)
        self.assertIsNotNone(storage.connection.calls[2][1][2].obj["worker_completed_at"])

    @staticmethod
    def _capture_error(service, question):
        try:
            service.execute(question)
        except QAServiceError as error:
            return error
        raise AssertionError("deadline request unexpectedly succeeded")

    def test_deadline_persistence_failure_returns_persistence_error_and_keeps_gate_held(self):
        storage = RecordingStorage(fail_at=2)
        graph = BlockingGraph(answered_state())
        service = QAService(
            agent=FakeAgent(graph, storage), origin="api", deadline_seconds=0.01
        )

        with self.assertRaises(QAServiceError) as raised:
            service.execute("deadline persistence failure")

        try:
            self.assertNotIsInstance(raised.exception, QAServiceDeadlineError)
            self.assertEqual(raised.exception.code, "persistence_error")
            with self.assertRaises(QAServiceBusyError):
                service.execute("still busy")
        finally:
            graph.release.set()
            self.assertTrue(graph.finished.wait(timeout=2))
            end = time.monotonic() + 2
            while not service._gate.acquire(blocking=False):
                if time.monotonic() >= end:
                    self.fail("deadline worker did not restore the process gate")
                time.sleep(0.01)
            service._gate.release()

        end = time.monotonic() + 2
        while True:
            try:
                response = service.execute("after cleanup")
                break
            except QAServiceBusyError:
                if time.monotonic() >= end:
                    raise
                time.sleep(0.01)
        self.assertEqual(response.result.status.value, "answered")

    def test_execution_and_persistence_failures_emit_allowlisted_terminal_events(self):
        cases = (
            (FakeAgent(FailingGraph(), RecordingStorage()), "execution_error"),
            (FakeAgent(StaticGraph(answered_state()), RecordingStorage(fail_at=1)), "persistence_error"),
            (FakeAgent(StaticGraph(answered_state()), RecordingStorage(fail_at=2)), "persistence_error"),
        )
        allowed = {"request_id", "origin", "event", "status", "count", "timing_ms"}
        for agent, expected_status in cases:
            with self.subTest(status=expected_status), self.assertLogs("panda_agent.service", level="INFO") as captured:
                with self.assertRaises(QAServiceError):
                    QAService(agent=agent, origin="api").execute("never log this question")
            terminal = [
                json.loads(record.getMessage())
                for record in captured.records
                if json.loads(record.getMessage())["event"] == "terminal"
            ]
            self.assertEqual(len(terminal), 1)
            self.assertEqual(terminal[0]["status"], expected_status)
            self.assertTrue(set(terminal[0]) <= allowed)

    def test_deadline_latches_client_error_and_holds_gate_until_worker_cleanup(self):
        storage = RecordingStorage()
        graph = BlockingGraph(answered_state())
        service = QAService(
            agent=FakeAgent(graph, storage), origin="api", deadline_seconds=0.01
        )

        with self.assertRaises(QAServiceDeadlineError) as raised:
            service.execute("deadline")

        self.assertEqual(raised.exception.code, "deadline_exceeded")
        self.assertEqual(raised.exception.request_id, storage.connection.calls[0][1][0])
        client_finish = storage.connection.calls[1]
        self.assertEqual(client_finish[1][0], "error")
        self.assertEqual(client_finish[1][3], "deadline_exceeded")
        self.assertIn("completed_at=now(),duration_ms=%s", client_finish[0])
        with self.assertRaises(QAServiceBusyError):
            service.execute("still busy")

        graph.release.set()
        self.assertTrue(graph.finished.wait(timeout=2))
        end = time.monotonic() + 2
        while True:
            try:
                response = service.execute("after cleanup")
                break
            except QAServiceBusyError:
                if time.monotonic() >= end:
                    raise
                time.sleep(0.01)
        self.assertEqual(response.result.status.value, "answered")
        deadline_updates = [
            call for call in storage.connection.calls
            if call[1] and call[1][-1] == raised.exception.request_id
        ]
        self.assertEqual(len(deadline_updates), 2)
        self.assertIn("UPDATE qa_runs SET node_timings=%s,model_usage=%s,trace=%s", deadline_updates[-1][0])
        self.assertNotIn("status=", deadline_updates[-1][0])
        self.assertNotIn("completed_at=", deadline_updates[-1][0])
        self.assertIsNone(client_finish[1][6].obj["worker_completed_at"])
        self.assertEqual(deadline_updates[-1][1][2].obj["cleanup_status"], "completed_after_deadline")
        self.assertIsNotNone(deadline_updates[-1][1][2].obj["worker_completed_at"])
        self.assertEqual(deadline_updates[-1][1][2].obj["selected_evidence_ids"], [])

    def test_lifecycle_logs_are_json_allowlisted_and_exclude_request_contents(self):
        with self.assertLogs("panda_agent.service", level="INFO") as captured:
            QAService(
                agent=FakeAgent(StaticGraph(answered_state()), RecordingStorage()), origin="api"
            ).execute("do not log this question or private source body")

        payloads = [json.loads(record.getMessage()) for record in captured.records]
        allowed = {"request_id", "origin", "event", "status", "count", "timing_ms"}
        self.assertTrue(payloads)
        self.assertTrue(all(set(payload) <= allowed for payload in payloads))
        rendered = json.dumps(payloads)
        self.assertNotIn("do not log this question", rendered)
        self.assertNotIn("private source body", rendered)

    def test_service_owns_request_lifecycle_in_a_worker_and_persists_allowlisted_trace(self):
        storage = RecordingStorage()
        graph = StaticGraph(answered_state())
        response = QAService(agent=FakeAgent(graph, storage), origin="api").execute("What is the answer?")

        self.assertEqual(response.result.status.value, "answered")
        self.assertRegex(response.request_id, r"^[0-9a-f-]{36}$")
        self.assertGreaterEqual(response.duration_ms, 0)
        self.assertTrue(graph.worker_name.startswith("qa-"))
        insert, update = storage.connection.calls
        self.assertIn("INSERT INTO qa_runs", insert[0])
        self.assertEqual(insert[1][0], response.request_id)
        self.assertEqual(insert[1][2], "running")
        self.assertIn("UPDATE qa_runs SET status=%s,completed_at=now(),duration_ms=%s,intent=%s,error_code=%s", update[0])
        self.assertEqual(update[1][0], "answered")
        self.assertEqual(update[1][2], "usage")
        self.assertIsNone(update[1][3])
        self.assertEqual(response.node_timings, update[1][4].obj)
        self.assertIn("workflow", response.node_timings)
        self.assertEqual(response.model_usage, update[1][5].obj)
        self.assertEqual(
            update[1][5].obj,
            {"model_calls": 0, "token_usage": 0, "generation_calls": 0, "embedding_calls": 0},
        )
        trace = update[1][6].obj
        self.assertEqual(
            set(trace),
            {"trace_schema_version", "origin", "selected_evidence_ids", "targeted_retrieval_count",
             "revision_count", "verification_error_codes", "worker_completed_at", "cleanup_status"},
        )
        self.assertEqual(trace["selected_evidence_ids"], ["e1"])
        self.assertEqual(trace["origin"], "api")
        self.assertNotIn("private source body", json.dumps(trace))

    def test_busy_request_is_rejected_by_the_process_local_gate(self):
        storage = RecordingStorage()
        graph = BlockingGraph(answered_state())
        first = QAService(agent=FakeAgent(graph, storage), origin="api")
        second = QAService(agent=FakeAgent(StaticGraph(answered_state()), storage), origin="api")
        completed = {}
        worker = threading.Thread(target=lambda: completed.setdefault("response", first.execute("first")))
        worker.start()
        self.assertTrue(graph.started.wait(timeout=2))
        with self.assertRaises(QAServiceBusyError) as raised:
            second.execute("second")
        self.assertEqual(raised.exception.code, "busy")
        self.assertRegex(raised.exception.request_id, r"^[0-9a-f-]{36}$")
        self.assertEqual(
            raised.exception.error_envelope(),
            {
                "request_id": raised.exception.request_id,
                "error_code": "busy",
                "message": "QA service is busy; retry the request later",
            },
        )
        graph.release.set()
        worker.join(timeout=5)
        self.assertFalse(worker.is_alive())
        self.assertNotEqual(raised.exception.request_id, completed["response"].request_id)

    def test_worker_exception_is_classified_and_completed_as_failed(self):
        storage = RecordingStorage()
        service = QAService(agent=FakeAgent(FailingGraph(), storage), origin="api")

        with self.assertRaises(QAServiceError) as raised:
            service.run_detailed("boom")

        self.assertEqual(raised.exception.code, "execution_error")
        self.assertRegex(raised.exception.request_id, r"^[0-9a-f-]{36}$")
        self.assertEqual(storage.connection.calls[0][1][0], raised.exception.request_id)
        self.assertEqual(
            raised.exception.error_envelope(),
            {
                "request_id": raised.exception.request_id,
                "error_code": "execution_error",
                "message": "QA request execution failed",
            },
        )
        self.assertEqual(storage.connection.calls[-1][1][0], "failed")
        self.assertEqual(storage.connection.calls[-1][1][3], "execution_error")
        self.assertEqual(storage.connection.calls[-1][1][6].obj["cleanup_status"], "execution_error")

    def test_persistence_failure_is_classified_without_a_stack_trace(self):
        storage = RecordingStorage(fail_at=2)
        service = QAService(agent=FakeAgent(StaticGraph(answered_state()), storage), origin="api")

        with self.assertRaises(QAServiceError) as raised:
            service.run_detailed("record this")

        self.assertEqual(raised.exception.code, "persistence_error")
        self.assertRegex(raised.exception.request_id, r"^[0-9a-f-]{36}$")
        self.assertEqual(storage.connection.calls[0][1][0], raised.exception.request_id)
        self.assertEqual(
            raised.exception.error_envelope(),
            {
                "request_id": raised.exception.request_id,
                "error_code": "persistence_error",
                "message": "QA completion could not be recorded",
            },
        )

    def test_service_owned_ids_are_unique_across_success_and_error_outcomes(self):
        ids = [
            UUID("00000000-0000-4000-8000-000000000001"),
            UUID("00000000-0000-4000-8000-000000000002"),
            UUID("00000000-0000-4000-8000-000000000003"),
            UUID("00000000-0000-4000-8000-000000000004"),
        ]
        with patch("panda_agent.service.uuid.uuid4", side_effect=ids):
            success = QAService(
                agent=FakeAgent(StaticGraph(answered_state()), RecordingStorage()), origin="api"
            ).execute("success")
            with self.assertRaises(QAServiceError) as execution:
                QAService(agent=FakeAgent(FailingGraph(), RecordingStorage()), origin="api").execute("failure")
            with self.assertRaises(QAServiceError) as persistence:
                QAService(
                    agent=FakeAgent(StaticGraph(answered_state()), RecordingStorage(fail_at=1)), origin="api"
                ).execute("persistence")
            busy_service = QAService(
                agent=FakeAgent(StaticGraph(answered_state()), RecordingStorage()), origin="api", max_concurrency=2
            )
            busy_service._gate.acquire()
            busy_service._gate.acquire()
            try:
                with self.assertRaises(QAServiceBusyError) as busy:
                    busy_service.execute("busy")
            finally:
                busy_service._gate.release()
                busy_service._gate.release()

        observed = [
            success.request_id,
            execution.exception.request_id,
            persistence.exception.request_id,
            busy.exception.request_id,
        ]
        self.assertEqual(observed, [str(item) for item in ids])
        self.assertEqual(len(set(observed)), len(observed))

    def test_canonical_output_matches_frozen_fixtures_with_existing_fakes(self):
        from test_qa import FakeRetriever, FakeVertex, bundle_for, code_evidence
        from panda_agent.qa import QAAgent

        fixtures = Path(__file__).parents[1] / "fixtures" / "qa_service_invariance"
        cases = {
            "answered.json": (bundle_for(code_evidence()), "Where is PndPidCorrelator?"),
            "insufficient_evidence.json": (
                bundle_for(code_evidence(), required_source_types=["paper"]),
                "What does the cited paper establish?",
            ),
            "version_conflict.json": (
                bundle_for(code_evidence(), conflicts=[
                    "pandaroot: requested deadbeef, locked 18c09e91100db27867ded30e708b4dae95bd8357"
                ]),
                "Use PandaRoot deadbeef",
            ),
        }
        for fixture_name, (bundle, question) in cases.items():
            bundle["plan"]["source_budgets"] = {"code": 1.0}
            agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
            actual = QAService.canonical_output(QAService(agent=agent, origin="api").run_detailed(question))
            expected = json.loads((fixtures / fixture_name).read_text(encoding="utf-8"))
            self.assertEqual(actual, expected, fixture_name)

    def test_valid_api_origin_is_traced_and_invalid_origin_is_rejected(self):
        storage = RecordingStorage()
        QAService(agent=FakeAgent(StaticGraph(answered_state()), storage), origin="api").execute("answer")
        self.assertEqual(storage.connection.calls[-1][1][6].obj["origin"], "api")
        with self.assertRaisesRegex(ValueError, "origin must be one of"):
            QAService(agent=FakeAgent(StaticGraph(answered_state()), storage), origin="worker")

    def test_cli_constructs_service_with_cli_origin(self):
        from panda_agent.cli import qa as qa_cli

        rendered = Mock()
        rendered.model_dump_json.return_value = "{}"
        with patch.object(sys, "argv", ["panda-qa", "ask", "hello", "--project-root", "."]):
            with patch("panda_agent.cli.qa.QAService") as service_class:
                service_class.return_value.run.return_value = rendered
                qa_cli.main()
        self.assertEqual(service_class.call_args.kwargs["origin"], "cli")


if __name__ == "__main__":
    unittest.main()
