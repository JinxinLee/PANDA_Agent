"""O1 fake-only stage capture and strict semantic neutrality contracts."""
from copy import deepcopy
import json

import pytest

from panda_agent import qa
from panda_agent.evaluation_runner import prompt_fingerprint
from test_e2_a1_answer_point_coverage import Vertex, agent, claim, review, QUESTION


FINGERPRINT = "5147f85c09a933609d91f4fa4e7bf3d8fbfa530684a3ecea4d3aaed72c3e04ce"


class RecordingVertex(Vertex):
    def __init__(self, **kwargs):
        self.composer_mode = kwargs.pop("composer_mode", "fallback")
        super().__init__(**kwargs)
        self.exact_calls = []

    def generate_json(self, prompt, schema, **kwargs):
        self.exact_calls.append((prompt, deepcopy(schema), deepcopy(kwargs)))
        payload = json.loads(prompt)
        if payload["task"] == "compose_verified_claims" and self.composer_mode != "fallback":
            self.calls.append((payload, deepcopy(schema), kwargs))
            if self.composer_mode == "generation_failure":
                raise RuntimeError("fake composer failure")
            return {"paragraphs": [{"text": c["claim_text"], "source_claim_ids": [c["claim_id"]]}
                                   for c in payload["verified_claims"]]}
        if payload["task"] == "review_composed_answer":
            self.calls.append((payload, deepcopy(schema), kwargs))
            if self.composer_mode == "review_failure":
                raise RuntimeError("fake review failure")
            return {"valid": self.composer_mode != "rejected", "unsupported_paragraph_indexes": [],
                    "missing_or_distorted_claim_ids": [], "reason": "existing concise reason"}
        return super().generate_json(prompt, schema, **kwargs)


def execute(tmp_path, capture=False, **kwargs):
    vertex = RecordingVertex(**kwargs)
    runner = agent(tmp_path, vertex)
    out = runner._run_detailed(
        QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=capture
    )
    return out, vertex.exact_calls, runner.retriever.calls


def event(out, stage):
    return next(e for e in out["diagnostics"]["qa_stage_trace"]["events"] if e["stage"] == stage)


def assert_neutral(off, on):
    a, calls_a, retrieves_a = off
    b, calls_b, retrieves_b = on
    assert a["result"] == b["result"]
    da, db = deepcopy(a["diagnostics"]), deepcopy(b["diagnostics"])
    db.pop("qa_stage_trace")
    assert da == db
    assert a["model_usage"] == b["model_usage"]
    assert calls_a == calls_b
    assert retrieves_a == retrieves_b


def test_o1_default_and_exact_neutrality(tmp_path):
    assert "qa_stage_trace" not in agent(tmp_path).run_detailed(QUESTION)["diagnostics"]
    assert agent(tmp_path).run(QUESTION).status
    off, on = execute(tmp_path), execute(tmp_path, True)
    assert_neutral(off, on)
    trace = on[0]["diagnostics"]["qa_stage_trace"]
    assert trace["schema_version"] == "qa-stage-trace-v1"
    assert trace["capture_status"] == "COMPLETE"
    assert event(on[0], "A0_OUTPUT")["status"] == "CAPTURED"
    assert event(on[0], "A1_INPUT")["status"] == "NOT_EXECUTED"
    assert event(on[0], "V2_OUTPUT")["status"] == "NOT_EXECUTED"
    assert len(trace["events"]) <= 16
    assert len(json.dumps(trace, ensure_ascii=False, sort_keys=True).encode("utf-8")) <= 2097152
    assert prompt_fingerprint() == FINGERPRINT


def test_o1_collision_branch_and_v2(tmp_path):
    args = dict(answers=[claim()], revisions=[claim("c1", "point.2", "The output is a table.")],
                reviews=[review({"c1": ["point.1"]}, missing=["point.2"]),
                         review({"c1": ["point.1"], "c1_r2": ["point.2"]})])
    off, on = execute(tmp_path, **args), execute(tmp_path, True, **args)
    assert_neutral(off, on)
    dispositions = event(on[0], "A1_POST_MERGE")["payload"]["dispositions"]
    assert dispositions[0]["disposition"] == "ID_COLLISION_RENAMED"
    assert dispositions[0]["old_claim_id"] == "c1"
    assert dispositions[0]["new_claim_id"] == "c1_r2"
    assert dispositions[0]["retained"] is True
    assert event(on[0], "V2_INPUT")["round"] == 2
    assert on[0]["diagnostics"]["revision_count"] == 1


@pytest.mark.parametrize("kind", ["anti_resurrection", "duplicate", "missing_id"])
def test_merge_rejections_are_actual_and_neutral(tmp_path, kind):
    first = review({"c1": ["point.1"]}, missing=["point.2"])
    second = review({"c1": ["point.1"]}, missing=["point.2"])
    revised = claim("c2", "point.2", "  The input is a record.  ")
    expected = "NORMALIZED_DUPLICATE"
    if kind == "anti_resurrection":
        first = review({"c1": []}, missing=["point.1", "point.2"], unsupported=["c1"])
        second = review({}, missing=["point.1", "point.2"])
        revised, expected = claim(), "IDENTICAL_UNSUPPORTED_REJECTED"
    elif kind == "missing_id":
        revised, expected = claim(""), "MISSING_ID"
    args = dict(answers=[claim()], reviews=[first, second], revisions=[revised])
    off, on = execute(tmp_path, **args), execute(tmp_path, True, **args)
    assert_neutral(off, on)
    disposition = event(on[0], "A1_POST_MERGE")["payload"]["dispositions"][0]
    assert disposition["disposition"] == expected
    assert disposition["retained"] is False
    assert disposition["new_claim_id"] is None
    assert event(on[0], "A1_OUTPUT")["payload"]["response"]["claims"] == [revised]


def test_raw_structural_rejection_survives_fallback(tmp_path):
    bad = review({"c1": ["point.1"], "c2": ["point.2"]})
    bad["claim_answer_point_mappings"][0]["answer_point_ids"] = ["unknown"]
    args = dict(reviews=[bad, review({}, missing=["point.1", "point.2"])])
    off, on = execute(tmp_path, **args), execute(tmp_path, True, **args)
    assert_neutral(off, on)
    payload = event(on[0], "V1_OUTPUT")["payload"]
    from test_qa import production_review_fixture
    actual_input = next(json.loads(p) for p, _, _ in on[1] if json.loads(p)["task"] == "review_claim_support_and_relevance")
    assert payload["response"] == production_review_fixture(bad, actual_input)
    assert payload["validation"]["status"] == "REJECTED"
    assert payload["validation"]["error"]


@pytest.mark.parametrize("mode,reason", [("success", "composed"),
    ("fallback", "deterministic_validation_failed"), ("generation_failure", "composer_generation_failed"),
    ("review_failure", "composer_review_failed"), ("rejected", "semantic_review_rejected")])
def test_composer_paths_neutral(tmp_path, mode, reason):
    off, on = execute(tmp_path, composer_mode=mode), execute(tmp_path, True, composer_mode=mode)
    assert_neutral(off, on)
    out = event(on[0], "C_OUTPUT")["payload"]
    assert out["outcome"]["reason"] == reason
    assert out["final_answer_ref"] == "result.answer"
    if mode == "success":
        assert len(out["response"]["paragraphs"]) == 2
        assert out["review_response"]["valid"] is True


def test_single_claim_bypass_and_evidence_projection_registry(tmp_path):
    args = dict(answers=[claim()], reviews=[review({"c1": ["point.1", "point.2"]})])
    off, on = execute(tmp_path, **args), execute(tmp_path, True, **args)
    assert_neutral(off, on)
    assert event(on[0], "C_OUTPUT")["payload"]["generation_status"] == "NOT_EXECUTED"
    trace = on[0]["diagnostics"]["qa_stage_trace"]
    model_input = event(on[0], "V1_INPUT")["payload"]["model_input"]
    ref = model_input["untrusted_evidence"][0]["evidence_projection_ref"]
    actual = next(json.loads(c[0]) for c in on[1] if json.loads(c[0])["task"] == "review_claim_support_and_relevance")
    assert trace["evidence_registry"][ref] == actual["untrusted_evidence"][0]
    assert model_input["untrusted_question"] == QUESTION
    assert model_input["coverage_satisfaction_schema_version"] == "coverage-satisfaction-v2"


@pytest.mark.parametrize("failure", ["serialization", "record", "assembly", "initialization"])
def test_optional_capture_failure_never_changes_semantics(tmp_path, monkeypatch, failure):
    off = execute(tmp_path)
    def fail(*args, **kwargs):
        raise TypeError("diagnostic failure only")
    if failure == "serialization":
        monkeypatch.setattr(qa, "_trace_json", fail)
    elif failure == "initialization":
        monkeypatch.setattr(qa._QAStageTrace, "__init__", fail)
    else:
        monkeypatch.setattr(qa._QAStageTrace, "record" if failure == "record" else "finish", fail)
    on = execute(tmp_path, True)
    assert_neutral(off, on)
    trace = on[0]["diagnostics"]["qa_stage_trace"]
    assert trace["capture_status"] == "INCOMPLETE"
    json.dumps(trace, allow_nan=False)


def test_size_limit_is_diagnostic_not_semantic(tmp_path, monkeypatch):
    off = execute(tmp_path)
    original = qa._QAStageTrace.record
    def oversized(self, stage, round_, payload, **kwargs):
        if stage == "A0_OUTPUT":
            payload = {**payload, "oversized_fixture": "x" * 2_097_152}
        return original(self, stage, round_, payload, **kwargs)
    monkeypatch.setattr(qa._QAStageTrace, "record", oversized)
    on = execute(tmp_path, True)
    assert_neutral(off, on)
    trace = on[0]["diagnostics"]["qa_stage_trace"]
    assert event(on[0], "A0_OUTPUT")["reason_code"] == "TRACE_SIZE_BOUND_EXCEEDED"
    assert trace["capture_status"] == "INCOMPLETE"
    assert len(json.dumps(trace, ensure_ascii=False, sort_keys=True).encode()) <= 2_097_152


def test_event_bound_and_snapshot_copy():
    trace = qa._QAStageTrace()
    raw = {"claims": [claim()]}
    trace.record("A0_OUTPUT", 0, raw)
    raw["claims"][0]["claim_text"] = "mutated later"
    assert trace.events[0]["payload"]["claims"][0]["claim_text"] == "The input is a record."
    for i in range(20):
        trace.record(f"synthetic.{i}", 0, {})
    finished = trace.finish()
    assert len(finished["events"]) == 16
    assert finished["capture_status"] == "INCOMPLETE"
    assert "TRACE_EVENT_BOUND_EXCEEDED" in finished["failure_codes"]


def test_admission_and_deterministic_exclusion_observe_without_repair(tmp_path):
    from test_e2_a1_answer_point_coverage import state
    from test_qa import code_evidence
    runner = agent(tmp_path, RecordingVertex(answers=[claim(evidence="page")],
                   reviews=[review({}, missing=["point.1", "point.2"])]))
    page = code_evidence(text="Visible but uncitable page.", path="page.html")
    page.update(evidence_id="page", source_id="synthetic_sphinx", source_version_id="synthetic_sphinx@1",
                locator={"url": "https://example.invalid/page", "snapshot_date": "2000-01-01", "section_path": []})
    runner.retriever.bundle["evidence"].append(page)
    original = deepcopy(runner.retriever.bundle)
    st = state(runner, [])
    st["_stage_trace"] = trace = qa._QAStageTrace()
    st.update(runner._answer(st))
    runner._verify(st)
    admission = next(e for e in trace.events if e["stage"] == "EA_ADMISSION")["payload"]
    assert admission["admitted_evidence_ids"] == ["e1"]
    assert admission["rejected_evidence_ids"] == ["page"]
    assert admission["decisions"][-1]["missing_locator_fields"] == ["section_path"]
    vin = next(e for e in trace.events if e["stage"] == "V1_INPUT")["payload"]
    assert vin["model_input"]["untrusted_claims"] == []
    assert "incomplete web citation page" in vin["deterministic_claim_errors"]["c1"]
    assert runner.retriever.bundle == original


def test_early_exit_skips_all_semantic_stages(tmp_path):
    runner = agent(tmp_path)
    runner.retriever.bundle["plan"]["version_conflicts"] = ["synthetic conflict"]
    off = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE)
    runner = agent(tmp_path)
    runner.retriever.bundle["plan"]["version_conflicts"] = ["synthetic conflict"]
    on = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=True)
    assert off["result"] == on["result"]
    assert all(e["status"] == "NOT_EXECUTED" for e in on["diagnostics"]["qa_stage_trace"]["events"])


def test_duplicate_input_ids_keep_ordinals_and_transform_snapshots(tmp_path):
    from test_e2_a1_answer_point_coverage import state
    revised = [claim("dup", text="The output is a table."), claim("dup", text="The input is a record.")]
    runner = agent(tmp_path, RecordingVertex(revisions=revised))
    st = state(runner, [])
    st.update(errors=["missing answer point point.1"], missing_answer_point_ids=["point.1"],
              supported_claims=[], unsupported_claim_ids=[], _stage_trace=qa._QAStageTrace())
    runner._revise(st)
    events = st["_stage_trace"].events
    raw = next(e for e in events if e["stage"] == "A1_OUTPUT")["payload"]
    assert raw["response"]["claims"] == revised
    assert raw["claim_ordinals"] == [0, 1]
    merged = next(e for e in events if e["stage"] == "A1_POST_MERGE")["payload"]
    assert [d["input_ordinal"] for d in merged["dispositions"]] == [0, 1]
    assert merged["dispositions"][1]["new_claim_id"] == "dup_r2"


def test_public_diagnostic_projection_is_an_explicit_allowlist():
    # The optional FastAPI runtime is not needed for this static boundary check.
    import ast
    from pathlib import Path
    tree = ast.parse(Path(qa.__file__).with_name("api.py").read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_ui_diagnostics")
    result = next(n.value for n in fn.body if isinstance(n, ast.Return))
    assert isinstance(result, ast.Dict) and all(k is not None for k in result.keys)
    assert "qa_stage_trace" not in [k.value for k in result.keys]
    reads = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
             and n.func.value.id == "diagnostics"]
    assert reads and all(n.func.attr == "get" and isinstance(n.args[0], ast.Constant) for n in reads)
    assert "qa_stage_trace" not in [n.args[0].value for n in reads]


def test_invocations_do_not_share_registry_or_collector(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    runner = agent(tmp_path)
    # Stateless model double permits concurrent requests on the SAME agent.
    runner.generation_vertex.generate_json = lambda *a, **k: RecordingVertex().generate_json(*a, **k)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outputs = list(pool.map(lambda _: runner._run_detailed(
            QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=True), range(2)))
    left, right = (x["diagnostics"]["qa_stage_trace"] for x in outputs)
    assert left == right
    assert left is not right and left["events"] is not right["events"]
    left["evidence_registry"].clear()
    assert right["evidence_registry"]


def test_runner_opt_in_persistence_resume_and_routing(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import Mock
    from panda_agent import evaluation_runner as er
    from panda_agent.evaluation import EvaluationRunStore
    manifest = {"official": False, "mode": "qa", "split": "dev"}
    er._configure_stage_trace(manifest, False)
    assert manifest["capture_stage_trace"] is False
    er._configure_stage_trace(manifest, True)
    store = EvaluationRunStore(tmp_path, "synthetic", manifest)
    saved = json.loads(store.manifest_path.read_text(encoding="utf-8"))
    assert saved["capture_stage_trace"] is True
    resumed = {"official": False, "mode": "qa", "split": "dev"}
    er._configure_stage_trace(resumed, False, saved)
    assert resumed == saved
    EvaluationRunStore(tmp_path, "synthetic", resumed, resume=True)
    legacy = {"official": False, "mode": "qa", "split": "dev"}
    er._configure_stage_trace(deepcopy(legacy), False, legacy)
    with pytest.raises(ValueError):
        er._configure_stage_trace(deepcopy(legacy), True, legacy)
    monkeypatch.setattr(er, "deterministic_case_metrics", lambda *a: {})
    monkeypatch.setattr(er, "apply_mode_metric_semantics", lambda m, **kw: m)
    engine = Mock()
    engine.run_detailed.return_value = engine._run_detailed.return_value = {"result": {}, "diagnostics": {}}
    for capture in [False, True]:
        er._execute_evaluation_case(engine, None, mode="qa", case=SimpleNamespace(query=QUESTION),
                                    object_lookup={}, capture_stage_trace=capture)
    engine.run_detailed.assert_called_once_with(QUESTION)
    engine._run_detailed.assert_called_once_with(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE,
                                                capture_stage_trace=True)
    run_dir = tmp_path / "data/evaluation/runs/resume"
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(json.dumps(saved), encoding="utf-8")
    dispatch = Mock()
    monkeypatch.setattr(er, "run_evaluation", dispatch)
    er.resume_evaluation(tmp_path, "resume")
    assert dispatch.call_args.kwargs["capture_stage_trace"] is True


@pytest.mark.parametrize("change", [{"official": True}, {"candidate_id": "formal"},
    {"split": "novel_validation"}, {"split": "acceptance"}, {"mode": "retrieval"}])
def test_runner_rejects_capture_outside_development_without_execution(change):
    from panda_agent.evaluation_runner import _configure_stage_trace
    with pytest.raises(ValueError):
        _configure_stage_trace({"official": False, "mode": "qa", "split": "dev", **change}, True)


@pytest.mark.parametrize("capture", [False, True])
def test_run_manifest_records_choice_before_any_runtime_client(tmp_path, monkeypatch, capture):
    from types import SimpleNamespace
    from panda_agent import evaluation_runner as er
    from panda_agent.evaluation import EvaluationRunStore
    class StopBeforeRuntime(Exception):
        pass
    monkeypatch.setattr(er, "load_gold_dataset", lambda *a: SimpleNamespace())
    monkeypatch.setattr(er, "_selected_questions", lambda *a: [SimpleNamespace(id="synthetic")])
    monkeypatch.setattr(er, "build_evaluation_manifest", lambda *a, **k: {
        "mode": k["mode"], "split": k["split"], "official": k["official"]})
    def save_and_stop(root, run_id, manifest, **kwargs):
        EvaluationRunStore(root, run_id, manifest, **kwargs)
        raise StopBeforeRuntime
    monkeypatch.setattr(er, "EvaluationRunStore", save_and_stop)
    with pytest.raises(StopBeforeRuntime):
        er.run_evaluation(tmp_path, mode="qa", split="dev", run_id="synthetic",
                          allow_draft=True, capture_stage_trace=capture)
    saved = json.loads((tmp_path / "data/evaluation/runs/synthetic/manifest.json").read_text(encoding="utf-8"))
    assert saved["capture_stage_trace"] is capture
    with pytest.raises(StopBeforeRuntime):
        er.run_evaluation(tmp_path, mode="qa", split="dev", run_id="synthetic",
                          allow_draft=True, resume=True)
    assert json.loads((tmp_path / "data/evaluation/runs/synthetic/manifest.json").read_text(encoding="utf-8")) == saved


def test_distinct_generation_verification_roles_unchanged(tmp_path):
    outputs = []
    for capture in [False, True]:
        gen, ver = RecordingVertex(composer_mode="success"), RecordingVertex(composer_mode="success")
        order = []
        for role, client in [("generation", gen), ("verification", ver)]:
            original = client.generate_json
            def wrapped(prompt, schema, _role=role, _original=original, **kwargs):
                order.append((_role, prompt, deepcopy(schema), deepcopy(kwargs)))
                return _original(prompt, schema, **kwargs)
            client.generate_json = wrapped
        runner = agent(tmp_path, gen)
        runner.verification_vertex = ver
        out = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=capture)
        outputs.append((out, order, runner.retriever.calls))
    assert_neutral(*outputs)
    assert [x[0] for x in outputs[0][1]] == ["generation", "generation", "verification", "generation", "verification"]


def test_trace_roundtrip_uses_existing_store_and_does_not_swallow_disk_errors(tmp_path, monkeypatch):
    from panda_agent.evaluation import EvaluationRunStore
    out, _, _ = execute(tmp_path, True)
    store = EvaluationRunStore(tmp_path, "capture", {"capture_stage_trace": True})
    record = {"id": "synthetic", "result": out["result"], "diagnostics": out["diagnostics"]}
    store.record(record)
    for path in [store.records_dir / "synthetic.json", store.results_path, store.attempts_path]:
        saved = json.loads(path.read_text(encoding="utf-8"))
        assert saved["diagnostics"]["qa_stage_trace"] == out["diagnostics"]["qa_stage_trace"]
    def fail(*args, **kwargs):
        raise OSError("existing storage failure")
    monkeypatch.setattr(type(store.attempts_path), "open", fail)
    with pytest.raises(OSError, match="existing storage failure"):
        store.record({**record, "id": "another"})
