"""G4 synthetic answerability and abstention controls; fake providers only.

Each fixture states its evidence authority and canonical obligation. The
production validator, router, and finalizer determine the observed outcome.
Pairs change the named authoritative fact, not the expected product rule.
"""

from copy import deepcopy

import pytest

from panda_agent import qa
from test_e2_a1_answer_point_coverage import agent, claim, state
from test_e3_missing_point_retrieval import (
    FakeE3Retriever, FakeVertex as E3Vertex, make_agent as e3_agent,
    make_claim as e3_claim, make_evidence as e3_evidence,
    make_review as e3_review,
)
from test_g1_relationship_obligations import named_check, named_point
from test_post_a5_c1_coverage_completeness import c1_review, check, point
from test_post_a5_o1_observability import RecordingVertex, event
from test_qa import bundle_for, code_evidence


MODE = qa.DEFAULT_ANSWER_POINT_MODE
QUESTION = "Describe the input record."
TEXT = "The input is a record."


def _evidence(eid="e1", text=TEXT, *, safe=True):
    item = code_evidence(evidence_id=eid, text=text, path=f"src/{eid}.h")
    if not safe:
        item.update(source_id="synthetic_sphinx", source_version_id="synthetic_sphinx@snapshot")
        item["locator"] = {"url": "https://example.invalid/page", "snapshot_date": "2000-01-01",
                           "section_path": []}
    return item


def _point(pid="point.1", relations=()):
    return {"answer_point_id": pid, "text": "Answer the requested fact.",
            "support_spans": [QUESTION], "required_relations": list(relations)}


def _verify_final(tmp_path, *, evidence, claims, points, review, question=QUESTION):
    """Use production V1/G2/finalization; the review is scripted authority input."""
    runner = agent(tmp_path, RecordingVertex(reviews=[review]), bundle=bundle_for(evidence))
    s = state(runner, claims, points)
    s.update(question=question, answer_point_coverage_mode=MODE)
    s.update(runner._verify(s))
    return runner, s, runner._finalize(s)["result"]


def test_g4_a1_single_complete_ordinary_point(tmp_path):
    """A1: one admitted exact quote satisfies the sole ordinary obligation."""
    review = c1_review([point("point.1", [check(TEXT)])], {"c1": ["point.1"]})
    _, s, result = _verify_final(tmp_path, evidence=[_evidence()], claims=[claim()],
                                  points=[_point()], review=review)
    assert s["coverage_satisfaction_status"] == "VALID"
    assert s["answer_point_audit"]["coverage_complete"] is True
    assert result["status"] == "answered"
    assert [c["claim_id"] for c in result["claims"]] == ["c1"]
    assert [e["evidence_id"] for e in result["evidence"]] == ["e1"]


@pytest.mark.parametrize("malformed,expected", [(False, "answered"), (True, "insufficient_evidence")])
def test_g4_pair_valid_vs_malformed_second_ordinary_item(tmp_path, malformed, expected):
    """A2/B9: two independent facts; only the second exact quote is corrupted."""
    evidence = [_evidence(), _evidence("e2", "The output is a table.")]
    claims = [claim(), claim("c2", "point.2", "The output is a table.", "e2")]
    review = c1_review([point("point.1", [check(TEXT)]),
                        point("point.2", [check("The output is a table.", ["c2"], eid="e2")])],
                       {"c1": ["point.1"], "c2": ["point.2"]})
    if malformed:
        review["answer_point_coverage"][1]["relationship_checks"][0]["basis"][0]["quote"] = "invented"
    _, s, result = _verify_final(tmp_path, evidence=evidence, claims=claims,
                                  points=[_point(), _point("point.2")], review=review)
    assert result["status"] == expected
    assert s["answer_point_audit"]["coverage_validation"]["status"] == ("PARTIAL" if malformed else "VALID")
    assert s["answer_point_audit"]["coverage_validation"]["point_results"][0]["state"] == "VALID"
    assert s["answer_point_audit"]["coverage_complete"] is not malformed
    assert {e["evidence_id"] for e in result["evidence"]} <= {"e1", "e2"}
    if malformed:
        assert s["missing_answer_point_ids"] == ["point.2"]
        assert s["revisionable_relationships"] == []


@pytest.mark.parametrize("established,expected", [(True, "answered"), (False, "insufficient_evidence")])
def test_g4_pair_established_vs_unsupported_named_relation(tmp_path, established, expected):
    """A3/B2: same requested order; only corpus support for that order changes."""
    question = "Does the input record precede the output table?"
    positive = "The input record precedes the output table."
    text = positive if established else "The input record and output table are present."
    evidence = [_evidence(text=text)]
    claims = [claim(text=positive)]
    relation = {"relation_id": "point.1.rel.1", "text": "Whether input precedes output",
                "support_spans": [question]}
    disposition = named_check("point.1.rel.1", satisfied=established,
                              supporters=["c1"] if established else [], quote=text)
    review = c1_review([named_point([disposition])], {"c1": ["point.1"]},
                       unsupported=() if established else ("c1",))
    _, s, result = _verify_final(tmp_path, evidence=evidence, claims=claims,
                                  points=[_point(relations=[relation])], review=review, question=question)
    assert s["answer_point_audit"]["coverage_validation"]["status"] == "VALID"
    assert result["status"] == expected
    assert s["answer_point_audit"]["coverage_complete"] is established
    if not established:
        assert not result["claims"]


@pytest.mark.parametrize("safe,expected", [(True, "answered"), (False, "insufficient_evidence")])
def test_g4_pair_citable_vs_unsafe_provenance(tmp_path, safe, expected):
    """A1/B3: same factual text; Sphinx locator lacks the exact section only in B3."""
    evidence = [_evidence(safe=safe)]
    disposition = check(TEXT, ["c1"] if safe else [],
                        admitted="ADMITTED_BACKING_AVAILABLE" if safe else "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING")
    review = c1_review([point("point.1", [disposition])], {"c1": ["point.1"]},
                       unsupported=() if safe else ("c1",))
    runner, s, result = _verify_final(tmp_path, evidence=evidence, claims=[claim()],
                                      points=[_point()], review=review)
    assert [e["evidence_id"] for e in runner._admitted_evidence(s)] == (["e1"] if safe else [])
    assert result["status"] == expected
    assert all(e["evidence_id"] in {x["evidence_id"] for x in runner._admitted_evidence(s)}
               for e in result["evidence"])


@pytest.mark.parametrize("repaired,expected", [(True, "answered"), (False, "insufficient_evidence")])
def test_g4_pair_a1_repairs_vs_leaves_relation_missing(tmp_path, repaired, expected):
    """A4/B7: V1 identifies an admitted-backed target; V2 checks full inventory."""
    question = "Is the input a record, and does it precede the output table?"
    proposal = {"points": [{"text": "Answer both requested relations", "support_spans": [question],
                            "required_relations": [{"text": "Whether input is a record",
                                                    "support_spans": [question]},
                                                   {"text": "Whether input precedes output",
                                                    "support_spans": [question]}]}],
                "ambiguity": {"status": "clear", "reason": ""}}
    relation_text = "The input record precedes the output table."
    established = named_check("point.1.rel.1", satisfied=True, supporters=["c1"], quote=TEXT)
    missing = named_check("point.1.rel.2", quote=relation_text)
    initial = named_point([established, missing])
    final = named_point([established, named_check("point.1.rel.2", satisfied=repaired,
                                                 supporters=["c2"] if repaired else [], quote=relation_text)])
    vertex = RecordingVertex(decomposition=proposal, answers=[claim()],
                             revisions=[claim("c2", "point.1", relation_text)],
                             reviews=[c1_review([initial], {"c1": ["point.1"]}),
                                      c1_review([final], {"c1": ["point.1"], "c2": ["point.1"]})])
    runner = agent(tmp_path, vertex, bundle=bundle_for([_evidence(text=f"{TEXT} {relation_text}")]))
    out = runner._run_detailed(question, mode=MODE, capture_stage_trace=True)
    assert out["result"]["status"] == expected
    assert out["diagnostics"]["revision_count"] == 1
    v2 = event(out, "V2_INPUT")["payload"]["model_input"]
    assert [r["relation_id"] for r in v2["runtime_answer_points"][0]["required_relations"]] == [
        "point.1.rel.1", "point.1.rel.2"]
    assert out["diagnostics"]["answer_point_audit"]["coverage_complete"] is repaired
    assert all(c["evidence_ids"] == ["e1"] for c in out["result"]["claims"])


def test_g4_a6_experimental_e3_recovers_genuinely_missing_point(tmp_path):
    """A6 EXPERIMENTAL_MODE_CONTROL: E3 is scoped to runtime_e1_v2."""
    e1 = e3_evidence("input", text=TEXT)
    e2 = e3_evidence("output", text="The output is a table.")
    proposal = {"points": [{"text": "Describe the input", "support_spans": ["input"]},
                           {"text": "Describe the output", "support_spans": ["output"]}],
                "ambiguity": {"status": "clear", "reason": ""}}
    vertex = E3Vertex(decomposition=proposal,
                      answers=[e3_claim("c1", "point.1", TEXT, [e1["evidence_id"]])],
                      revisions=[e3_claim("c2", "point.2", "The output is a table.", [e2["evidence_id"]])],
                      reviews=[e3_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
                               e3_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[])])
    retriever = FakeE3Retriever(initial_bundle=bundle_for([e1]),
                                targeted_candidates={"exact": [e2]}, vertex=vertex)
    retriever.bundle["plan"]["source_budgets"] = {"code": 1.0}
    runner = e3_agent(tmp_path, vertex=vertex, retriever=retriever, ev1=e1, ev2=e2)
    out = runner._run_detailed("Describe the input and output.", mode="runtime_e1_v2")
    trace = out["diagnostics"]["e3_trace"]
    assert trace["triggered"] is True
    assert trace["recovered_answer_point_ids"] == ["point.2"]
    assert trace["post_retrieval_missing_point_result"] == "complete"
    assert out["result"]["status"] == "answered"
    assert out["diagnostics"]["revision_count"] == 1


def test_g4_b1_absent_evidence_refuses_without_claim(tmp_path):
    """B1: the synthetic world has no source for its requested fact."""
    runner = agent(tmp_path, bundle=bundle_for([]))
    s = {"question": QUESTION, "bundle": bundle_for([]), "retrieval_count": 1}
    s.update(runner._sufficiency(s))
    assert s["sufficient"] is False and "no evidence" in s["errors"]
    result = runner._finalize(s)["result"]
    assert result["status"] == "insufficient_evidence"
    assert result["claims"] == []


def test_g4_b4_version_conflict_remains_distinct(tmp_path):
    """B4: a conflicting locked revision cannot authorize any mixed answer."""
    bundle = bundle_for([_evidence()])
    bundle["plan"]["version_conflicts"] = ["requested revision differs from locked corpus"]
    runner = agent(tmp_path, bundle=bundle)
    s = {"question": QUESTION, "bundle": bundle, "retrieval_count": 0}
    s.update(runner._sufficiency(s))
    result = runner._finalize(s)["result"]
    assert result["status"] == "version_conflict"
    assert result["claims"] == []


@pytest.mark.parametrize("question,error_prefix", [
    ("What will the exact checksum of the future runtime output file be?",
     "exact future runtime outcome"),
    ("Prove a theorem for all possible input records.", "open-domain universal proof"),
])
def test_g4_b5_b6_explicit_answerability_guards(tmp_path, question, error_prefix):
    """B5/B6: current locked source cannot establish the requested universal/future fact."""
    bundle = bundle_for([_evidence()])
    runner = agent(tmp_path, bundle=bundle)
    s = {"question": question, "bundle": bundle, "retrieval_count": 1}
    s.update(runner._sufficiency(s))
    assert s["sufficient"] is False and s["errors"][0].startswith(error_prefix)
    result = runner._finalize(s)["result"]
    assert result["status"] == "insufficient_evidence"
    assert not any(c["claim_text"] == TEXT for c in result["claims"])


def test_g4_b8_valid_verifier_rejects_unsupported_claim(tmp_path):
    """B8: a claim absent from the only admitted text cannot become public."""
    unsupported = claim(text="The input is encrypted.")
    review = c1_review([point("point.1", [check(TEXT, supporters=[])])],
                       {"c1": ["point.1"]}, unsupported=("c1",))
    _, s, result = _verify_final(tmp_path, evidence=[_evidence()], claims=[unsupported],
                                  points=[_point()], review=review)
    assert "c1" in s["unsupported_claim_ids"]
    assert result["status"] == "insufficient_evidence"
    assert result["claims"] == []


@pytest.mark.parametrize("complete,expected", [(True, "answered"), (False, "insufficient_evidence")])
def test_g4_f1_f2_complete_vs_incomplete_finalization(tmp_path, complete, expected):
    """F1/F2: only canonical coverage completion changes; safe support is retained."""
    ordinary = check(TEXT, supporters=["c1"] if complete else [])
    review = c1_review([point("point.1", [ordinary])], {"c1": ["point.1"]})
    _, s, result = _verify_final(tmp_path, evidence=[_evidence()], claims=[claim()],
                                 points=[_point()], review=review)
    assert s["coverage_satisfaction_status"] == "VALID"
    assert s["coverage_blocked"] is not complete
    assert result["status"] == expected
    assert [c["claim_id"] for c in result["claims"]] == ["c1"]
    assert [e["evidence_id"] for e in result["evidence"]] == ["e1"]
    assert result["answer"].endswith(qa.C1_INCOMPLETE_NOTICE) is not complete
    assert s["answer_point_audit"]["coverage_complete"] is complete


def test_g4_sufficiency_required_source_pair(tmp_path):
    """Source-type routing distinguishes available evidence from missing required type."""
    runner = agent(tmp_path)
    present = {"question": QUESTION, "bundle": bundle_for([_evidence()]), "retrieval_count": 1}
    missing = deepcopy(present)
    missing["bundle"]["plan"]["required_source_types"] = ["paper"]
    assert runner._sufficiency(present) == {"sufficient": True, "errors": []}
    result = runner._sufficiency(missing)
    assert result["sufficient"] is False
    assert result["errors"] == ["missing required source: paper"]
