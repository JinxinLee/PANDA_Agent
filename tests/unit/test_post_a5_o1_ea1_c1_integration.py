"""Synthetic cross-workstream closeout; no product or scientific execution."""
from copy import deepcopy
import json

import pytest

from panda_agent import qa
from panda_agent.retrieval_trace import build_retrieval_trace
from test_e2_a1_answer_point_coverage import agent, claim, review, state, QUESTION
from test_post_a5_c1_coverage_completeness import check, point, c1_review
from test_post_a5_ea1_exact_backing import setup, BACKING_ID, TEXT
from test_post_a5_o1_observability import RecordingVertex, assert_neutral, event


def relation(text="The input is a record.", supporters=None):
    return check(text, supporters, eid=BACKING_ID)


def assert_public(out):
    for c in out["result"]["claims"]:
        assert set(c) == {"claim_id", "claim_text", "evidence_ids"}
    assert not {"relationship_checks", "scope_status", "qa_stage_trace", "answer_point_ids"} & out["result"].keys()


@pytest.mark.parametrize("mixed", [False, True])
def test_resolved_backing_revision_trace_and_finalization(tmp_path, mixed):
    runs = []
    for capture in (False, True):
        first = relation()
        missing = relation("The output is a table.", [])
        blocked = check("Heading", [], "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING", "selected-page")
        def records(repaired):
            second = {**missing, "satisfied": True, "supporting_claim_ids": ["c2"]} if repaired else missing
            return [point("point.1", [first]), point("point.2", [second] + ([blocked] if mixed else []))]
        before = c1_review(records(False), {"c1": ["point.1"], "dropped": []}, irrelevant=["dropped"])
        after = c1_review(records(True), {"c1": ["point.1"], "c2": ["point.2"]})
        vertex = RecordingVertex(answers=[claim(evidence=BACKING_ID), claim("dropped", text="Unrelated detail.", evidence=BACKING_ID)],
            revisions=[claim("c2", "point.2", "The output is a table.", BACKING_ID)],
            reviews=[before, after], composer_mode="success")
        runner, initial, storage = setup(tmp_path, vertex)
        original = deepcopy(initial["bundle"])
        out = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=capture)
        assert initial["bundle"] == original
        assert storage.calls == [["page"]] and runner.retriever.calls == 1
        assert out["model_usage"]["embedding_calls"] == 0
        assert out["diagnostics"]["revision_count"] == 1
        assert out["result"]["status"] == ("insufficient_evidence" if mixed else "answered")
        assert [e["object_id"] for e in out["result"]["evidence"]] == ["section"]
        assert [c["claim_id"] for c in out["result"]["claims"]] == ["c1", "c2"]
        assert_public(out)
        payloads = [json.loads(p) for p, _, _ in vertex.exact_calls]
        a0 = next(p for p in payloads if p["task"] == "create_atomic_evidence_bound_claims")
        a1 = next(p for p in payloads if p["task"] == "revise_unsupported_claims_once")
        assert a0["untrusted_evidence"] == a1["untrusted_evidence"]
        assert [e["evidence_id"] for e in a1["untrusted_evidence"]] == [BACKING_ID]
        assert a1["revisionable_answer_point_ids"] == ["point.2"]
        assert [r["relationship_text"] for r in a1["revisionable_relationships"]] == [missing["relationship_text"]]
        assert "Heading" not in json.dumps(a1)
        for p, schema, _ in vertex.exact_calls:
            p = json.loads(p)
            if p["task"] == "review_claim_support_and_relevance":
                assert p["admitted_evidence_ids"] == [BACKING_ID]
                assert {e["evidence_id"] for e in p["untrusted_evidence"]} == {"selected-page", BACKING_ID}
                assert schema == qa.PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA
        assert len(vertex.exact_calls) == (5 if mixed else 7)
        assert out["result"]["answer"].endswith(qa.C1_INCOMPLETE_NOTICE) == mixed
        mappings = out["diagnostics"]["answer_point_audit"]["claim_mappings"]
        assert all(m["rendered"] for m in mappings if m["claim_id"] in {"c1", "c2"})
        trace_args = dict(question_id="synthetic", run_id="fixture", question=QUESTION,
                          manifest={}, object_lookup={}, result=out["result"])
        trace = build_retrieval_trace(diagnostics=out["diagnostics"], **trace_args)
        assert trace == build_retrieval_trace(diagnostics={**original, "selected_evidence": original["evidence"]}, **trace_args)
        assert [e["object_id"] for e in trace.final_evidence] == ["page"]
        runs.append((out, vertex.exact_calls, runner.retriever.calls))
    assert_neutral(*runs)
    out = runs[1][0]
    d = event(out, "EA_ADMISSION")["payload"]["decisions"][0]
    assert d["reason_code"] == "RESOLVED_EXACT_BACKING"
    assert d["parent_object_id"] == "page" and d["backing_object_id"] == "section"
    assert d["containment_offsets"] == [8, 8 + len(TEXT)]
    for stage in ("A0_OUTPUT", "V1_INPUT", "V1_OUTPUT", "A1_INPUT", "A1_OUTPUT", "A1_POST_MERGE", "V2_INPUT", "V2_OUTPUT"):
        assert event(out, stage)["status"] == "CAPTURED"
    stages = [e["stage"] for e in out["diagnostics"]["qa_stage_trace"]["events"]]
    active = ["A0_OUTPUT", "V1_INPUT", "V1_OUTPUT", "A1_INPUT", "A1_OUTPUT", "A1_POST_MERGE", "V2_INPUT", "V2_OUTPUT"]
    assert [stages.index(stage) for stage in active] == sorted(stages.index(stage) for stage in active)
    assert event(out, "V1_OUTPUT")["payload"]["validation"]["status"] != "REJECTED"
    assert event(out, "V2_OUTPUT")["payload"]["validation"]["status"] != "REJECTED"
    assert event(out, "C_INPUT")["status"] == ("NOT_EXECUTED" if mixed else "CAPTURED")
    assert event(out, "C_OUTPUT")["status"] == ("NOT_EXECUTED" if mixed else "CAPTURED")


@pytest.mark.parametrize("mapped", [[], ["point.2"]])
def test_resolved_backing_does_not_override_verified_mapping(tmp_path, mapped):
    records = [point(pid, [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE") for pid in ("point.1", "point.2")]
    vertex = RecordingVertex(reviews=[c1_review(records, {"c1": mapped}, unsupported=["c1"])], revisions=[])
    runner, initial, storage = setup(tmp_path, vertex)
    s = state(runner, [claim(evidence=BACKING_ID)])
    s["answer_point_coverage_mode"] = qa.DEFAULT_ANSWER_POINT_MODE
    original = deepcopy(s["draft"])
    s.update(runner._verify(s))
    assert runner._after_verify_route(s) == "revise"
    s.update(runner._revise(s))
    a1 = json.loads(vertex.exact_calls[-1][0])
    assert a1["revisionable_answer_point_ids"] == mapped
    assert a1["untrusted_draft"]["claims"][0]["answer_point_ids"] == mapped
    assert a1["revisionable_unsupported_claim_ids"] == ["c1"]
    assert [e["evidence_id"] for e in a1["untrusted_evidence"]] == [BACKING_ID]
    assert original["claims"][0]["answer_point_ids"] == ["point.1"]
    assert storage.calls == [["page"]]
    assert runner._after_verify_route(s) == "finalize"


@pytest.mark.parametrize("kind", ["visible", "ambiguous", "parent"])
def test_resolved_context_preserves_blocked_paths(tmp_path, kind):
    admission = "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING" if kind != "ambiguous" else "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE"
    scope = "ESTABLISHED" if kind != "ambiguous" else "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE"
    records = [point("point.1", [check("Heading", [], admission, "selected-page")], scope),
               point("point.2", [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE")]
    claims = [claim(evidence="selected-page" if kind == "parent" else BACKING_ID)]
    mappings = {} if kind == "parent" else {"c1": ["point.1"]}
    vertex = RecordingVertex(answers=claims, reviews=[c1_review(records, mappings)])
    runner, initial, storage = setup(tmp_path, vertex)
    out = runner.run_detailed(QUESTION)
    assert out["diagnostics"]["revision_count"] == 0
    assert out["result"]["status"] == "insufficient_evidence"
    assert len(vertex.exact_calls) == 3
    assert_public(out)
    if kind == "parent":
        assert out["result"]["claims"] == []
    else:
        assert [c["claim_id"] for c in out["result"]["claims"]] == ["c1"]
    assert not qa._is_public_claim_citation_eligible(initial["bundle"]["evidence"][0])


@pytest.mark.parametrize("error", ["version conflict", "exact future runtime outcome or checksum cannot be established",
    "open-domain universal proof is unsupported", "unsupported requested symbol: UnknownSymbol",
    "unsupported requested API symbol: Unknown::call"])
def test_hard_refusal_public_boundary(tmp_path, error):
    runner, initial, storage = setup(tmp_path)
    s = state(runner, [claim(evidence=BACKING_ID)])
    s.update(answer_point_coverage_mode=qa.DEFAULT_ANSWER_POINT_MODE, sufficient=False,
             coverage_blocked=True, supported_claims=[claim(evidence=BACKING_ID)], errors=[error])
    if error == "version conflict":
        s["bundle"]["plan"]["version_conflicts"] = [error]
    out = runner._finalize(s)
    assert qa.C1_INCOMPLETE_NOTICE not in out["result"]["answer"]
    assert out["result"]["status"] == ("version_conflict" if error == "version conflict" else "insufficient_evidence")
    assert_public(out)
    assert runner.vertex.calls == []


@pytest.mark.parametrize("mode", ["shadow_e1_v2", "runtime_e1_v2", "legacy_question_core"])
def test_historical_contract_is_separate(tmp_path, mode):
    runner = agent(tmp_path, RecordingVertex(reviews=[review({"c1": ["point.1"], "c2": ["point.2"]})] * 2))
    out = runner._run_detailed(QUESTION, mode=mode)
    for prompt, schema, kwargs in runner.vertex.exact_calls:
        assert schema != qa.PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA
        assert kwargs.get("system_instruction") not in (
            qa.PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SYSTEM_PROMPT,
            qa.PRODUCTION_COVERAGE_SATISFACTION_REVISION_SYSTEM_PROMPT)
        assert "revisionable_unsupported_claim_mappings" not in prompt
    assert qa.C1_INCOMPLETE_NOTICE not in out["result"]["answer"]
    assert_public(out)


def test_partial_public_and_dropped_audit_with_resolved_backing(tmp_path):
    records = [point(pid, [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE") for pid in ("point.1", "point.2")]
    vertex = RecordingVertex(answers=[claim(evidence=BACKING_ID), claim("drop", evidence=BACKING_ID)],
        reviews=[c1_review(records, {"c1": ["point.1"], "drop": []}, irrelevant=["drop"])])
    runner, initial, storage = setup(tmp_path, vertex)
    out = runner.run_detailed(QUESTION)
    assert out["result"]["status"] == "insufficient_evidence"
    assert [c["claim_id"] for c in out["result"]["claims"]] == ["c1"]
    assert "The input is a record." in out["result"]["answer"]
    assert out["result"]["answer"].endswith(qa.C1_INCOMPLETE_NOTICE)
    assert {m["claim_id"]: m["rendered"] for m in out["diagnostics"]["answer_point_audit"]["claim_mappings"]} == {"c1": True, "drop": False}
    assert len(vertex.exact_calls) == 3
    assert_public(out)
