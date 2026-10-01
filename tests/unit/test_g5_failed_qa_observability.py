"""G5 failure-boundary capture: neutral fakes and temporary stores only."""

from collections import Counter
from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from panda_agent import evaluation_runner as er, evaluation_finalization as ef, qa
from panda_agent.evaluation import EvaluationRunStore, aggregate_metrics, load_run_records
from panda_agent.llm.vertex import VertexCallError
from test_e2_a1_answer_point_coverage import QUESTION, agent, claim, review
from test_post_a5_o1_observability import RecordingVertex


class ScriptedVertex(RecordingVertex):
    """Counts attempted fake requests, including the one that throws."""

    def __init__(self, *, fault=None, error=None, **kwargs):
        super().__init__(**kwargs)
        self.fault = fault
        self.error = error or VertexCallError("fake structured generation: 429 RESOURCE_EXHAUSTED")
        self.attempts = []
        self.task_counts = Counter()

    def generate_json(self, prompt, schema, **kwargs):
        task = json.loads(prompt)["task"]
        self.task_counts[task] += 1
        self.attempts.append((task, kwargs.get("usage_stage")))
        if self.fault == (task, self.task_counts[task]):
            self.exact_calls.append((prompt, deepcopy(schema), deepcopy(kwargs)))
            raise self.error
        return super().generate_json(prompt, schema, **kwargs)

    def stats_snapshot(self):
        stats = {"model_calls": len(self.attempts), "generation_calls": len(self.attempts),
                 "embedding_calls": 0, "token_usage": len(self.attempts) * 5}
        for _, stage in self.attempts:
            if stage:
                key = f"{stage}_calls"
                stats[key] = stats.get(key, 0) + 1
        return stats


def scripted_agent(tmp_path, fault=None, error=None, *, revision=False, composer_mode="success"):
    first = review({"c1": ["point.1"]}, missing=["point.2"]) if revision else review(
        {"c1": ["point.1"], "c2": ["point.2"]})
    kwargs = {"answers": [claim()] if revision else None,
              "revisions": [claim("c2", "point.2", "The output is a table.")],
              "reviews": [first, review({"c1": ["point.1"], "c2": ["point.2"]})],
              "composer_mode": composer_mode}
    gen = ScriptedVertex(fault=fault, error=error, **kwargs)
    ver = ScriptedVertex(fault=fault, error=gen.error, **kwargs)
    runner = agent(tmp_path, gen)
    runner.verification_vertex = ver
    return runner, gen, ver


def save_fake_case(tmp_path, monkeypatch, runner, *, capture=True, successful=False):
    """Exercise the actual runner catch and store with no real runtime dependencies."""
    case = SimpleNamespace(id="synthetic-failure", query=QUESTION, intent="usage", split="dev",
                           language="en", expected_status=SimpleNamespace(value="answered"),
                           required_source_types=["code"])
    monkeypatch.setattr(er, "load_gold_dataset", lambda *a: SimpleNamespace())
    monkeypatch.setattr(er, "_selected_questions", lambda *a: [case])
    monkeypatch.setattr(er, "build_evaluation_manifest", lambda *a, **k: {
        "mode": k["mode"], "split": k["split"], "official": k["official"]})
    monkeypatch.setattr(er, "QAAgent", lambda *a: runner)
    monkeypatch.setattr(er, "load_object_lookup", lambda *a, **k: {})
    # Explicit test-only all-role reader, not a default accounting change.
    monkeypatch.setattr(er, "_stats_snapshot", lambda engine: engine._stats_snapshot())
    monkeypatch.setattr(ef, "resolve_expected_case_ids", lambda *a: {case.id})
    monkeypatch.setattr(ef, "resolve_candidate_binding", lambda *a: (None, None, True))
    monkeypatch.setattr(er, "report_evaluation", lambda *a: {})
    monkeypatch.setattr(er, "VertexAIClient", lambda *a, **k: pytest.fail("no real SDK client"))
    for name in ("deterministic_case_metrics", "judge_answer", "build_retrieval_trace", "write_retrieval_trace"):
        monkeypatch.setattr(er, name, lambda *a, _name=name, **k: pytest.fail(f"failed QA reached {_name}"))
    if successful:
        monkeypatch.setattr(er, "deterministic_case_metrics", lambda *a: {})
        monkeypatch.setattr(er, "build_retrieval_trace", lambda **k: {})
        monkeypatch.setattr(er, "write_retrieval_trace", lambda *a: None)
    path = er.run_evaluation(tmp_path, mode="qa", split="dev", run_id="fake-store",
                             allow_draft=True, capture_stage_trace=capture)
    return load_run_records(path)[0], path


def failure_trace(record):
    assert not {"result", "diagnostics", "metrics"} & record.keys()
    assert record["exception"]["type"] == "VertexCallError"
    assert record["exception"]["retryable"] is True
    assert record["exception"]["category"] == "transport_provider_infrastructure"
    assert ef.evaluation_record_state(record) == "retryable_exception"
    assert aggregate_metrics([record])["scored_cases"] == 0
    envelope = record["failure_diagnostics"]
    assert set(envelope) == {"schema_version", "capture_status", "failure_codes",
                             "question_decomposition", "qa_stage_trace"}
    assert envelope["capture_status"] == "INCOMPLETE"
    assert "QA_EXECUTION_FAILED" in envelope["failure_codes"]
    trace = envelope["qa_stage_trace"]
    assert trace["capture_status"] == "INCOMPLETE"
    assert all(e["status"] != "NOT_EXECUTED" for e in trace["events"])
    return trace


def event(trace, stage):
    return next(e for e in trace["events"] if e["stage"] == stage)


def resolve_projections(value, registry):
    if isinstance(value, dict):
        if "evidence_projection_ref" in value:
            return registry[value["evidence_projection_ref"]]
        return {k: resolve_projections(v, registry) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_projections(v, registry) for v in value]
    return value


def test_b_d1_failure(tmp_path, monkeypatch):
    runner, gen, ver = scripted_agent(tmp_path, ("decompose_user_question", 1))
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    assert gen.task_counts["decompose_user_question"] == 1 and not ver.attempts
    assert record["exception"]["message"] == str(gen.error)
    trace = failure_trace(record)
    assert record["failure_diagnostics"]["question_decomposition"] is None
    assert "DECOMPOSITION_UNAVAILABLE" in record["failure_diagnostics"]["failure_codes"]
    assert trace["events"] == []


def test_e_v1_provider_failure(tmp_path, monkeypatch):
    runner, gen, ver = scripted_agent(tmp_path, ("review_claim_support_and_relevance", 1))
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    assert ver.task_counts["review_claim_support_and_relevance"] == 1
    trace = failure_trace(record)
    assert event(trace, "A0_OUTPUT")["status"] == "CAPTURED"
    assert event(trace, "V1_INPUT")["status"] == "CAPTURED"
    assert not any(e["stage"] == "V1_OUTPUT" for e in trace["events"])


def test_f_late_a1_failure_preserves_v1(tmp_path, monkeypatch):
    runner, gen, ver = scripted_agent(tmp_path, ("revise_unsupported_claims_once", 1), revision=True)
    record, path = save_fake_case(tmp_path, monkeypatch, runner)
    assert gen.task_counts["revise_unsupported_claims_once"] == 1
    assert ver.task_counts["review_claim_support_and_relevance"] == 1
    trace = failure_trace(record)
    output = event(trace, "V1_OUTPUT")["payload"]
    assert output["validation"]["status"] == "ACCEPTED"
    assert output["response"]["missing_answer_point_ids"] == ["point.2"]
    model_input = resolve_projections(event(trace, "V1_INPUT")["payload"], trace["evidence_registry"])["model_input"]
    evidence = {e["evidence_id"]: e for e in model_input["untrusted_evidence"]}
    for point in output["response"]["answer_point_coverage"]:
        for check in point["relationship_checks"]:
            for basis in check["basis"]:
                assert basis["quote"] in evidence[basis["evidence_id"]]["text"]
    assert event(trace, "A1_INPUT")["status"] == "CAPTURED"
    assert not any(e["stage"] == "A1_OUTPUT" for e in trace["events"])
    for file in (path / "attempts.jsonl", path / "results.jsonl", path / "records/synthetic-failure.json"):
        assert json.loads(file.read_text(encoding="utf-8"))["failure_diagnostics"] == record["failure_diagnostics"]


@pytest.mark.parametrize("revision", [False, True])
def test_a_success_capture_neutrality(tmp_path, revision):
    outputs = []
    for capture in (False, True):
        runner, gen, ver = scripted_agent(tmp_path, revision=revision)
        out = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=capture)
        assert "failure_diagnostics" not in out
        assert out["diagnostics"]["revision_count"] == int(revision)
        assert ("qa_stage_trace" in out["diagnostics"]) is capture
        diagnostics = deepcopy(out["diagnostics"])
        diagnostics.pop("qa_stage_trace", None)
        outputs.append((out["result"], diagnostics, out["model_usage"],
                        gen.exact_calls, ver.exact_calls, runner.retriever.calls))
    assert outputs[0] == outputs[1]
    assert er.prompt_fingerprint() == "08083fffd968f5903293e927759cf0d2de72871bbadc66741af87f1d0de49abc"


def test_b_semantic_error_remains_terminal(tmp_path, monkeypatch):
    error = ValueError("invalid semantic proposal")
    runner, _, _ = scripted_agent(tmp_path, ("decompose_user_question", 1), error)
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    assert record["exception"] == {"type": "ValueError", "message": str(error),
                                    "retryable": False, "category": None}
    assert ef.evaluation_record_state(record) == "terminal_exception"
    assert record["failure_diagnostics"]["question_decomposition"] is None
    assert not {"result", "diagnostics", "metrics"} & record.keys()


@pytest.mark.parametrize("operation", ["analyzer", "rerank"])
def test_c_post_d1_retrieval_failure(tmp_path, monkeypatch, operation):
    runner, gen, _ = scripted_agent(tmp_path)
    canonical = []
    original = runner.decompose_question
    def decompose(*a, **k):
        value = original(*a, **k)
        canonical.append(deepcopy(value))
        return value
    monkeypatch.setattr(runner, "decompose_question", decompose)
    def retrieve(*a, **k):
        raise VertexCallError(f"fake {operation}: 429 RESOURCE_EXHAUSTED")
    monkeypatch.setattr(runner.retriever, "retrieve", retrieve)
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    assert gen.task_counts["decompose_user_question"] == 1
    assert record["failure_diagnostics"]["question_decomposition"] == canonical[0]
    assert failure_trace(record)["events"] == []


def test_d_a0_provider_failure(tmp_path, monkeypatch):
    runner, gen, ver = scripted_agent(tmp_path, ("create_atomic_evidence_bound_claims", 1))
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    trace = failure_trace(record)
    assert event(trace, "EA_ADMISSION")["status"] == "CAPTURED"
    assert trace["evidence_registry"]
    assert not any(e["stage"] == "A0_OUTPUT" for e in trace["events"])
    assert gen.stats_snapshot()["qa_generation_calls"] == 1
    assert not ver.attempts
    assert record["model_call_breakdown"]["runtime"]["qa_generation_calls"] == 1


def test_i_v2_failure_preserves_v1_a1_merge(tmp_path, monkeypatch):
    runner, gen, ver = scripted_agent(tmp_path, ("review_claim_support_and_relevance", 2), revision=True)
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    trace = failure_trace(record)
    assert gen.task_counts["revise_unsupported_claims_once"] == 1
    assert ver.task_counts["review_claim_support_and_relevance"] == 2
    for stage in ("V1_INPUT", "V1_OUTPUT", "A1_INPUT", "A1_OUTPUT", "A1_POST_MERGE", "V2_INPUT"):
        assert event(trace, stage)["status"] == "CAPTURED"
    resolve_projections(trace["events"], trace["evidence_registry"])
    assert not any(e["stage"] == "V2_OUTPUT" for e in trace["events"])


@pytest.mark.parametrize("fault", ["initialization", "snapshot", "decomposition", "envelope", "wrapper", "runner_copy"])
def test_g_capture_failures_never_mask_original(tmp_path, monkeypatch, fault):
    runner, gen, _ = scripted_agent(tmp_path, ("review_claim_support_and_relevance", 1))
    def fail(*a, **k):
        raise RuntimeError("optional capture fault")
    if fault == "initialization":
        monkeypatch.setattr(qa._QAStageTrace, "__init__", fail)
    elif fault == "snapshot":
        monkeypatch.setattr(qa._QAStageTrace, "snapshot_on_failure", fail)
    elif fault == "decomposition":
        original = runner.decompose_question
        def invalid_copy(*a, **k):
            value = original(*a, **k)
            value["ambiguity"]["reason"] = object()
            return value
        monkeypatch.setattr(runner, "decompose_question", invalid_copy)
    elif fault == "envelope":
        monkeypatch.setattr(qa, "_build_failure_diagnostics", fail)
    elif fault == "wrapper":
        monkeypatch.setattr(qa.QADetailedExecutionError, "__init__", fail)
    else:
        monkeypatch.setattr(er, "_copy_failure_diagnostics", fail)
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    assert record["exception"]["type"] == "VertexCallError"
    assert record["exception"]["message"] == str(gen.error)
    assert record["exception"]["retryable"] is True
    if fault in {"envelope", "wrapper", "runner_copy"}:
        assert "failure_diagnostics" not in record
    else:
        trace = failure_trace(record)
        codes = record["failure_diagnostics"]["failure_codes"]
        if fault == "initialization":
            assert "TRACE_COLLECTOR_UNAVAILABLE" in codes
            assert trace["reason_code"] == "CAPTURE_INITIALIZATION_FAILED"
        elif fault == "snapshot":
            assert "TRACE_SNAPSHOT_FAILED" in codes
            assert trace["reason_code"] == "CAPTURE_ASSEMBLY_FAILED"
            assert record["failure_diagnostics"]["question_decomposition"] is not None
        else:
            assert "DECOMPOSITION_COPY_FAILED" in codes
            assert record["failure_diagnostics"]["question_decomposition"] is None
            assert event(trace, "V1_INPUT")["status"] == "CAPTURED"


@pytest.mark.parametrize("entry", ["internal", "run", "run_detailed"])
def test_h_capture_disabled_exact_original(tmp_path, monkeypatch, entry):
    error = VertexCallError("original failure")
    cause = RuntimeError("original cause")
    error.__cause__ = cause
    runner, _, _ = scripted_agent(tmp_path, ("decompose_user_question", 1), error)
    monkeypatch.setattr(qa, "_build_failure_diagnostics", lambda *a, **k: pytest.fail("capture disabled"))
    with pytest.raises(VertexCallError) as caught:
        if entry == "internal":
            runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=False)
        else:
            getattr(runner, entry)(QUESTION)
    assert caught.value is error and caught.value.__cause__ is cause


@pytest.mark.parametrize("error", [KeyboardInterrupt(), SystemExit(), ValueError("unsupported")])
def test_execution_guard_boundaries(tmp_path, error):
    runner, _, _ = scripted_agent(tmp_path)
    if isinstance(error, ValueError):
        with pytest.raises(ValueError, match="unsupported answer-point mode"):
            runner._run_detailed(QUESTION, mode="unsupported", capture_stage_trace=True)
    else:
        def fail(*a, **k):
            raise error
        runner.decompose_question = fail
        with pytest.raises(type(error)) as caught:
            runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=True)
        assert caught.value is error


def envelope(decomposition=None):
    return qa._build_failure_diagnostics(decomposition, qa._QAStageTrace(),
        decomposition_applicable=True, trace_initialization_failed=False)


def encoded_size(value):
    return len(qa._trace_json(value).encode("utf-8"))


def test_j_trace_events_and_copy_isolation():
    collector = qa._QAStageTrace()
    evidence = {"evidence_id": "neutral", "text": "Exact scientific quote."}
    collector.record("V1_INPUT", 1, {"evidence": evidence, "fallback": "NOT_EXECUTED"})
    collector.failure("V1_OUTPUT", 1, "CAPTURE_FAILED")
    for index in range(20):
        collector.record(f"neutral.{index}", 0, {})
    original_events = deepcopy(collector.events)
    snapshot = collector.snapshot_on_failure()
    assert len(snapshot["events"]) == 16
    assert encoded_size(snapshot) <= 2_097_152
    assert "TRACE_EVENT_BOUND_EXCEEDED" in snapshot["failure_codes"]
    assert "CAPTURE_FAILED" in snapshot["failure_codes"]
    assert "QA_EXECUTION_FAILED" in snapshot["failure_codes"]
    assert collector.events == original_events
    assert snapshot["events"][0]["payload"]["fallback"] == "NOT_EXECUTED"
    collector.registry["projection.1"]["text"] = "mutated"
    collector.events[0]["payload"]["fallback"] = "mutated"
    evidence["text"] = "also mutated"
    assert snapshot["evidence_registry"]["projection.1"]["text"] == "Exact scientific quote."
    assert snapshot["events"][0]["payload"]["fallback"] == "NOT_EXECUTED"
    resolve_projections(snapshot["events"], snapshot["evidence_registry"])


def test_j_trace_failure_metadata_overflow():
    collector = qa._QAStageTrace()
    collector.record("A0_OUTPUT", 0, {"text": ""})
    overhead = encoded_size(collector._envelope())
    collector.record("A0_OUTPUT", 0, {"text": "x" * (2_097_152 - overhead)})
    assert encoded_size(collector._envelope()) == 2_097_152
    snapshot = collector.snapshot_on_failure()
    assert snapshot["reason_code"] == "TRACE_SIZE_BOUND_EXCEEDED"
    assert snapshot["events"] == [] and snapshot["evidence_registry"] == {}
    assert collector.events[0]["status"] == "CAPTURED"


@pytest.mark.parametrize("offset", [0, 1])
def test_j_decomposition_exact_byte_boundary(offset):
    value = {"text": "x" * (65_536 - encoded_size({"text": ""}) + offset)}
    out = envelope(value)
    if offset:
        assert out["question_decomposition"] is None
        assert "DECOMPOSITION_SIZE_BOUND_EXCEEDED" in out["failure_codes"]
    else:
        assert out["question_decomposition"] == value
        value["text"] = "changed"
        assert encoded_size(out["question_decomposition"]) == 65_536


def test_j_multibyte_decomposition_omission():
    value = {"text": "é" * 40_000}
    assert len(qa._trace_json(value)) < 65_536 < encoded_size(value)
    out = envelope(value)
    assert out["question_decomposition"] is None
    assert "DECOMPOSITION_SIZE_BOUND_EXCEEDED" in out["failure_codes"]


@pytest.mark.parametrize("offset", [0, 1])
def test_j_whole_envelope_byte_cap(offset):
    value = {"padding": "x" * (2_166_784 - encoded_size({"padding": ""}) + offset)}
    if offset:
        with pytest.raises(qa._QADiagnosticsSizeError):
            qa._copy_failure_diagnostics(value)
    else:
        assert encoded_size(qa._bounded_json_copy(value, 2_166_784)) == 2_166_784


@pytest.mark.parametrize("invalid", [object(), float("nan")])
def test_j_non_json_decomposition_is_explicit(invalid):
    out = envelope({"text": invalid})
    assert out["question_decomposition"] is None
    assert "DECOMPOSITION_COPY_FAILED" in out["failure_codes"]


def test_no_decomposition_mode_and_setup_failure(tmp_path, monkeypatch):
    runner, _, _ = scripted_agent(tmp_path)
    def fail(*a, **k):
        raise VertexCallError("fake 429")
    monkeypatch.setattr(runner.graph, "invoke", fail)
    with pytest.raises(qa.QADetailedExecutionError) as caught:
        runner._run_detailed(QUESTION, mode="legacy_question_core", capture_stage_trace=True)
    assert "DECOMPOSITION_NOT_APPLICABLE" in caught.value.failure_diagnostics["failure_codes"]
    monkeypatch.setattr(runner, "_stats_snapshot", fail)
    with pytest.raises(qa.QADetailedExecutionError) as caught:
        runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=True)
    assert caught.value.failure_diagnostics["qa_stage_trace"]["reason_code"] == "CAPTURE_NOT_INITIALIZED"


@pytest.mark.parametrize("malformed", ["extra", "codes", "trace", "projection", "non_json", "oversized"])
def test_k_runner_omits_malformed_optional_payload(tmp_path, monkeypatch, malformed):
    runner, _, _ = scripted_agent(tmp_path)
    payload = envelope()
    if malformed == "extra":
        payload["extra"] = "not in contract"
    elif malformed == "codes":
        payload["failure_codes"].append("dynamic error")
    elif malformed == "trace":
        payload["qa_stage_trace"]["events"] = [{"status": "NOT_EXECUTED"}]
    elif malformed == "projection":
        payload["qa_stage_trace"]["events"] = [{"stage": "V1_INPUT", "round": 1, "status": "CAPTURED",
            "reason_code": None, "payload": {"evidence_projection_ref": "missing"}}]
    elif malformed == "non_json":
        payload["question_decomposition"] = {"text": float("nan")}
    else:
        payload["question_decomposition"] = {"text": "x" * 2_166_784}
    original = VertexCallError("fake 429 RESOURCE_EXHAUSTED")
    def fail(*a, **k):
        raise qa.QADetailedExecutionError(original, payload) from original
    monkeypatch.setattr(runner, "_run_detailed", fail)
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    assert "failure_diagnostics" not in record
    assert record["exception"]["type"] == "VertexCallError"
    assert record["exception"]["message"] == str(original)
    assert record["exception"]["retryable"] is True


def test_k_root_cause_classification_and_legacy_record(tmp_path, monkeypatch):
    original = VertexCallError("provider status in cause only")
    cause = RuntimeError("safe provider cause")
    cause.code = 429
    original.__cause__ = cause
    runner, _, _ = scripted_agent(tmp_path, ("decompose_user_question", 1), original)
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    assert original.__cause__ is cause
    assert record["exception"]["type"] == "VertexCallError"
    assert record["exception"]["retryable"] is True
    legacy = {k: v for k, v in record.items() if k != "failure_diagnostics"}
    args = {"expected_case_ids": {record["id"]}, "mode": "qa"}
    assert ef.evaluate_cohort_decision(records=[record], **args) == ef.evaluate_cohort_decision(records=[legacy], **args)
    assert aggregate_metrics([record]) == aggregate_metrics([legacy])
    assert ef.evaluation_record_state(legacy) == "retryable_exception"
    store = EvaluationRunStore(tmp_path / "legacy-store", "legacy", {"mode": "qa"})
    store.record(legacy)
    assert load_run_records(store.run_dir) == [legacy]


def test_k_ordinary_exception_not_generically_unwrapped(tmp_path, monkeypatch):
    original = RuntimeError("ordinary terminal error")
    original.original_exception = VertexCallError("fake 429")
    runner, _, _ = scripted_agent(tmp_path)
    def fail(*a, **k):
        raise original
    monkeypatch.setattr(runner, "_run_detailed", fail)
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    assert record["exception"] == {"type": "RuntimeError", "message": str(original),
                                    "retryable": False, "category": None}
    assert "failure_diagnostics" not in record


def test_k_real_store_fault_propagates(tmp_path, monkeypatch):
    runner, _, _ = scripted_agent(tmp_path, ("decompose_user_question", 1))
    def fail(*a, **k):
        raise OSError("store durability fault")
    monkeypatch.setattr(er.EvaluationRunStore, "record", fail)
    with pytest.raises(OSError, match="store durability fault"):
        save_fake_case(tmp_path, monkeypatch, runner)


def test_l_late_assembly_filters_finish_placeholders(tmp_path, monkeypatch):
    runner, _, _ = scripted_agent(tmp_path)
    original = VertexCallError("fake return assembly: 429")
    def fail(*a, **k):
        raise original
    monkeypatch.setattr(runner, "_model_usage_delta", fail)
    record, _ = save_fake_case(tmp_path, monkeypatch, runner)
    trace = failure_trace(record)
    assert event(trace, "V1_OUTPUT")["status"] == "CAPTURED"
    assert not any(e["stage"] in {"A1_INPUT", "V2_OUTPUT"} for e in trace["events"])
    assert event(trace, "C_OUTPUT")["status"] == "CAPTURED"


@pytest.mark.parametrize("mode", ["generation_failure", "review_failure"])
def test_l_composer_fallback_still_success(tmp_path, mode):
    runner, _, _ = scripted_agent(tmp_path, composer_mode=mode)
    out = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=True)
    assert out["result"]["status"] == "answered"
    assert "failure_diagnostics" not in out
    assert out["diagnostics"]["composer"]["accepted"] is False


@pytest.mark.parametrize("revision", [False, True])
def test_a_success_record_no_failure_fields(tmp_path, monkeypatch, revision):
    runner, _, _ = scripted_agent(tmp_path, revision=revision)
    record, path = save_fake_case(tmp_path, monkeypatch, runner, successful=True)
    assert "exception" not in record and "failure_diagnostics" not in record
    assert record["result"]["status"] == "answered"
    assert record["diagnostics"]["revision_count"] == int(revision)
    assert ef.evaluation_record_state(record) == "completed"
    for file in (path / "attempts.jsonl", path / "results.jsonl", path / "records/synthetic-failure.json"):
        assert "failure_diagnostics" not in json.loads(file.read_text(encoding="utf-8"))


@pytest.mark.parametrize("fault", ["envelope", "wrapper"])
def test_g_capture_construction_preserves_exact_original(tmp_path, monkeypatch, fault):
    original = VertexCallError("fake original 429")
    cause = RuntimeError("original provider cause")
    original.__cause__ = cause
    runner, _, _ = scripted_agent(tmp_path, ("decompose_user_question", 1), original)
    def fail(*a, **k):
        raise RuntimeError("capture construction fault")
    if fault == "envelope":
        monkeypatch.setattr(qa, "_build_failure_diagnostics", fail)
    else:
        monkeypatch.setattr(qa.QADetailedExecutionError, "__init__", fail)
    with pytest.raises(VertexCallError) as caught:
        runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=True)
    assert caught.value is original and original.__cause__ is cause
