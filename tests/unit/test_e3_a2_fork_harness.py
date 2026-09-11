"""Deterministic fake/unit tests for the E3-A2 evaluation-only fork harness.

Zero real provider calls. Proves the harness:
- uses the same product nodes as the production runtime path,
- respects the existing pre-answer targeted retrieval loop,
- produces the same first-verify state as the production path under fakes,
- does not execute E3 before the fork,
- does not access Gold while running product nodes,
- forks deep-copied independent control/treatment continuations,
- keeps bounded execution (<=1 missing-point retrieval, <=1 revision).
"""

from copy import deepcopy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

import panda_agent.qa as qa
from panda_agent.models import stable_id
from test_e3_missing_point_retrieval import (
    POINTS,
    QUESTION,
    FakeE3Retriever,
    FakeVertex,
    bundle_for,
    make_agent,
    make_claim,
    make_evidence,
    make_review,
)

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "e3_a2_run", ROOT / "evaluation" / "run_e3_a2_targeted_recovery_validation.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)


class StubMeter:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.phase = "shared"


def recording_vertex(vertex: FakeVertex, meter: StubMeter) -> FakeVertex:
    """Make a fake vertex append meter events like the real Meter wrapper."""
    base = vertex.generate_json

    def generate_json(prompt: str, schema: dict[str, Any], **kwargs: Any) -> Any:
        task = json.loads(prompt).get("task", "")
        meter.events.append(
            {
                "phase": meter.phase,
                "stage": mod.TASKS.get(task, "qa_answer"),
                "logical_calls": 1,
            }
        )
        return base(prompt, schema, **kwargs)

    vertex.generate_json = generate_json
    return vertex


def eligible_vertex(verify_reviews: int = 2) -> FakeVertex:
    """First review reports point.2 missing; each continuation arm consumes one
    complete second-verify review from the same fake queue."""
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    eid2 = stable_id("obj2", "exact", prefix="evidence")
    second = make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[])
    return FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.", [eid1])],
        reviews=[make_review(mappings={"c1": ["point.1"]}, missing=["point.2"])]
        + [deepcopy(second) for _ in range(verify_reviews)],
        revisions=[
            make_claim(
                "c2",
                "point.2",
                "Track filtering in fillData via successfullyPassedFilters.",
                [eid2],
            )
        ],
    )


def complete_vertex() -> FakeVertex:
    """Complete first-verify coverage plus one spare review for a re-run."""
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    eid2 = stable_id("obj2", "exact", prefix="evidence")
    review = make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[])
    return FakeVertex(
        answers=[
            make_claim("c1", "point.1", "PndPidCorrelator configuration.", [eid1]),
            make_claim("c2", "point.2", "Track filtering in fillData.", [eid2]),
        ],
        reviews=[review, deepcopy(review)],
    )


def complete_setup(tmp_path):
    """Fully covered first verify: both claims cite evidence present in the bundle."""
    e1 = make_evidence("obj1", path="src/PndPidCorrelator1.cxx", text="void PndPidCorrelator::Init() {}")
    e2 = make_evidence(
        "obj2",
        path="src/PndPidCorrelator2.cxx",
        text="void PndPidCorrelator::fillData() { successfullyPassedFilters(); }",
    )
    bundle = bundle_for([e1, e2])
    bundle["plan"]["source_budgets"] = {"code": 1.0}
    bundle["candidate_snapshot"] = {
        "pass_origin": "initial",
        "rankings": {"exact": [deepcopy(e1), deepcopy(e2)]},
    }
    vertex = complete_vertex()
    retriever = FakeE3Retriever(initial_bundle=bundle, vertex=vertex)
    return make_agent(tmp_path, vertex=vertex, retriever=retriever)


def run_first_pass(agent: qa.QAAgent, question: str) -> dict[str, Any]:
    graph = mod.build_first_pass_graph(agent)
    decomposition = agent.decompose_question(question)
    initial: qa.QAState = {
        "question": question,
        "answer_point_coverage_mode": "runtime_e1_v2",
        "runtime_answer_points": decomposition["points"],
    }
    initial["runtime_answer_points"] = qa._active_runtime_answer_points(initial)
    return graph.invoke(initial)


def strip_timings(state: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in state.items() if k != "node_timings_ms"}


def test_first_verify_state_matches_production_path(tmp_path, monkeypatch):
    captured: list[dict[str, Any]] = []
    real = qa.QAAgent._missing_point_retrieve

    def tracking(self: Any, state: dict[str, Any]) -> Any:
        captured.append(deepcopy(state))
        return real(self, state)

    monkeypatch.setattr(qa.QAAgent, "_missing_point_retrieve", tracking)
    production_agent = make_agent(tmp_path, vertex=eligible_vertex())
    production_agent._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert len(captured) == 1

    harness_agent = make_agent(tmp_path, vertex=eligible_vertex())
    harness_state = run_first_pass(harness_agent, QUESTION)
    assert strip_timings(harness_state) == strip_timings(captured[0])
    # E3 must not execute inside the shared first pass.
    assert harness_agent.retriever.collect_calls == []
    assert harness_agent.retriever.consolidate_calls == []


def test_first_pass_respects_pre_answer_targeted_retrieval_loop(tmp_path):
    agent = make_agent(tmp_path, vertex=eligible_vertex())
    agent.retriever.bundle["plan"]["required_source_types"] = ["code", "workflow"]
    state = run_first_pass(agent, QUESTION)
    # Initial retrieval plus one pre-answer targeted retrieval, then the
    # configured bound stops the loop (max_targeted_retrievals = 1).
    assert len(agent.retriever.retrieve_calls) == 2
    assert state.get("retrieval_count") == 1
    snapshots = state.get("candidate_snapshots", [])
    assert [s.get("pass_origin") for s in snapshots] == [
        "initial",
        "pre_answer_targeted_1",
    ]
    assert agent.retriever.collect_calls == []


def test_non_applicable_complete_coverage_records_no_arms(tmp_path):
    agent = complete_setup(tmp_path)
    state = run_first_pass(agent, QUESTION)
    eligible, reason = agent._check_e3_trigger(state)
    assert (eligible, reason) == (False, "no_missing_answer_points")
    record = mod.execute_case(agent, StubMeter(), "n900", QUESTION, 0)
    assert record["applicable"] is False
    assert record["trigger_reason"] == "no_missing_answer_points"
    assert record["control"] is None and record["treatment"] is None
    assert "arm_mask" not in record


def test_control_arm_skips_e3_and_stays_bounded(tmp_path):
    agent = make_agent(tmp_path, vertex=eligible_vertex())
    state = run_first_pass(agent, QUESTION)
    assert agent._check_e3_trigger(state) == (True, "genuine_missing_point")
    checkpoint = deepcopy(state)
    final = mod.build_continuation_graph(agent, "revise").invoke(deepcopy(checkpoint))
    assert agent.retriever.collect_calls == []
    assert agent.retriever.consolidate_calls == []
    assert final["missing_point_retrieval_count"] == 0
    assert final["revision_count"] == 1
    assert "result" in final
    assert final.get("e3_trace") is None
    # Only one second-verify review remains (the unused treatment-arm one).
    assert len(agent.vertex.reviews) == 1
    # Fork checkpoint remains untouched by the control continuation.
    assert checkpoint.get("missing_point_retrieval_count") == 0


def test_treatment_arm_matches_production_end_to_end(tmp_path):
    production_agent = make_agent(tmp_path, vertex=eligible_vertex())
    production = production_agent._run_detailed(QUESTION, mode="runtime_e1_v2")

    harness_agent = make_agent(tmp_path, vertex=eligible_vertex())
    state = run_first_pass(harness_agent, QUESTION)
    treatment = mod.build_continuation_graph(
        harness_agent, "missing_point_retrieve"
    ).invoke(deepcopy(state))
    assert treatment["result"] == production["result"]
    assert treatment["e3_trace"] == production["diagnostics"]["e3_trace"]
    assert treatment["revision_count"] == production["diagnostics"]["revision_count"]
    assert treatment["missing_point_retrieval_count"] == 1
    assert len(harness_agent.retriever.collect_calls) == 1
    rerank_calls = [
        c
        for c in harness_agent.vertex.calls
        if c[0].get("task") == "rerank_evidence"
    ]
    assert len(rerank_calls) == 1


def test_fork_arms_execute_independently_from_shared_checkpoint(tmp_path):
    agent = make_agent(tmp_path, vertex=eligible_vertex())
    state = run_first_pass(agent, QUESTION)
    checkpoint = deepcopy(state)
    control = mod.build_continuation_graph(agent, "revise").invoke(deepcopy(checkpoint))
    treatment = mod.build_continuation_graph(
        agent, "missing_point_retrieve"
    ).invoke(deepcopy(checkpoint))
    assert control["missing_point_retrieval_count"] == 0
    assert treatment["missing_point_retrieval_count"] == 1
    assert checkpoint["missing_point_retrieval_count"] == 0
    assert control is not treatment and checkpoint is not control
    # Deep-copy isolation: the shared checkpoint must be unmodified by both arms.
    assert checkpoint.get("e3_trace") is None


def test_execute_case_record_shape_and_mask(tmp_path):
    meter = StubMeter()
    agent = make_agent(tmp_path, vertex=recording_vertex(eligible_vertex(), meter))
    record = mod.execute_case(agent, meter, "n003", QUESTION, 0)
    assert record["applicable"] is True
    assert record["trigger_reason"] == "genuine_missing_point"
    assert record["arm_mask"] == {"A": "treatment", "B": "control"}
    # Control keeps the pre-E3 semantics: the existing-evidence-only revision
    # cannot cite the missing evidence object, so it cannot recover the point.
    assert record["control"]["status"] == "insufficient_evidence"
    assert record["control"]["missing_point_retrieval_count"] == 0
    assert record["treatment"]["status"] == "answered"
    assert record["treatment"]["missing_point_retrieval_count"] == 1
    assert record["treatment"]["e3_trace"]["triggered"] is True
    phases = [event["phase"] for event in record["usage"]]
    assert set(phases) == {"shared", "control", "treatment"}
    assert phases.index("control") < phases.index("treatment")


def test_execute_case_even_id_mask(tmp_path):
    agent = make_agent(tmp_path, vertex=eligible_vertex())
    record = mod.execute_case(agent, StubMeter(), "n006", QUESTION, 0)
    assert record["arm_mask"] == {"A": "control", "B": "treatment"}


def test_product_prompts_never_receive_gold_content(tmp_path):
    gold_sentinel = "GOLD_ONLY_SENTINEL_REQUIRED_POINT_TEXT"
    agent = make_agent(tmp_path, vertex=eligible_vertex())
    record = mod.execute_case(agent, StubMeter(), "n003", QUESTION, 0)
    prompts = [json.dumps(call[0], ensure_ascii=False) for call in agent.vertex.calls]
    queries = [q for q, _ in agent.retriever.collect_calls]
    assert prompts and queries
    for text in [*prompts, *queries]:
        assert gold_sentinel not in text
        assert "required_answer_points" not in text
    assert record["shared_first_verify"]["runtime_answer_points"] == POINTS


def test_mask_rule_is_deterministic_by_numeric_id():
    assert mod.arm_assignment("n003") == {"A": "treatment", "B": "control"}
    assert mod.arm_assignment("n006") == {"A": "control", "B": "treatment"}
    assert mod.arm_assignment("n021") == {"A": "treatment", "B": "control"}
    assert mod.arm_assignment("n010") == {"A": "control", "B": "treatment"}
