"""G1 question-only relation contracts with scripted model responses."""

from copy import deepcopy
import json

import pytest

from panda_agent import qa
from panda_agent import evaluation_runner, question_decomposition
from panda_agent.question_decomposition import QuestionDecomposer
from test_question_decomposition import ProposalVertex
from test_e2_a1_answer_point_coverage import agent, claim, state
from test_post_a5_c1_coverage_completeness import c1_review, check, fixture, point
from test_post_a5_o1_observability import RecordingVertex


QUESTION = "Does Cedar run before Birch?"


def relation(text="Explain whether Cedar runs before Birch.", spans=None, kind="ordering"):
    return {"text": text, "support_spans": spans or [QUESTION], "relation_type": kind}


def production_point(relations=None):
    return {"text": "Answer the requested order.", "support_spans": [QUESTION],
            "required_relations": [relation()] if relations is None else relations}


def decompose(point_value):
    return QuestionDecomposer(ProposalVertex({"points": [point_value],
        "ambiguity": {"status": "clear", "reason": ""}})).decompose(QUESTION, relation_aware=True)


def test_production_relations_get_host_ids_and_literal_question_support():
    value = decompose(production_point())
    assert value["schema_version"] == "e1.question_decomposition.v3"
    assert value["points"][0]["required_relations"][0]["relation_id"] == "point.1.rel.1"
    assert value["points"][0]["required_relations"][0]["support_spans"] == [QUESTION]


@pytest.mark.parametrize("change", [
    lambda p: p.pop("required_relations"),
    lambda p: p["required_relations"][0].update(relation_id="model.1"),
    lambda p: p["required_relations"][0].update(support_spans=["cedar"]),
    lambda p: p["required_relations"].append(deepcopy(p["required_relations"][0])),
    lambda p: p.update(required_relations=[relation(text=f"Relation {i}") for i in range(4)]),
])
def test_malformed_production_relation_fails_explicitly(change):
    value = production_point()
    change(value)
    with pytest.raises(ValueError):
        decompose(value)


def test_required_relation_disposition_is_mandatory_and_exclusive(tmp_path):
    claims, evidence = fixture(tmp_path)
    canonical = [{"answer_point_id": "point.1", "text": "Answer order", "support_spans": [QUESTION],
                  "required_relations": [{"relation_id": "point.1.rel.1", "text": "Whether Cedar runs before Birch",
                                          "support_spans": [QUESTION]}]},
                 {"answer_point_id": "point.2", "text": "Answer another request", "support_spans": [QUESTION],
                  "required_relations": []}]
    named = {"relation_id": "point.1.rel.1", "basis": [{"evidence_id": "e1", "quote": "The input is a record."}],
             "supporting_claim_ids": ["c1"], "satisfied": True,
             "admission_state": "ADMITTED_BACKING_AVAILABLE"}
    first = point("point.1", [])
    first.update(complete=True, supporting_claim_ids=["c1"], required_relation_checks=[named])
    second = point("point.2", [check("The output is a table.", ["c2"])])
    second["required_relation_checks"] = []
    value = c1_review([first, second])
    assert qa._validate_coverage_satisfaction(value, claims, {"point.1", "point.2"}, set(), evidence,
                                               {"e1"}, canonical_points=canonical)
    for mutation in (lambda v: v["answer_point_coverage"][0]["required_relation_checks"].clear(),
                     lambda v: v["answer_point_coverage"][0]["relationship_checks"].append(check()),
                     lambda v: v["answer_point_coverage"][1].pop("required_relation_checks")):
        bad = deepcopy(value)
        mutation(bad)
        with pytest.raises(ValueError):
            qa._validate_coverage_satisfaction(bad, claims, {"point.1", "point.2"}, set(), evidence,
                                               {"e1"}, canonical_points=canonical)


@pytest.mark.parametrize("question,relation_bearing", [
    ("Does Cedar run before Birch?", True),
    ("Where does Cedar occur in the workflow relative to Birch?", True),
    ("Does Cedar depend on Birch?", True),
    ("How does Cedar produce input for Birch?", True),
    ("Does Cedar cause Birch?", True),
    ("How do Cedar and Birch differ?", True),
    ("Is Cedar contained in Birch?", True),
    ("Describe the workflow from StageOne to StageTwo.", True),
    ("Is Cedar between Birch and Maple?", True),
    ("Compare Cedar, Birch and Maple.", True),
    ("Where is Cedar implemented?", False),
    ("Define Birch.", False),
    ("Which file defines Maple?", False),
    ("What arguments does SensorFrame accept?", False),
    ("How does Cedar work?", False),
    ("Why does Cedar stop?", False),
])
def test_neutral_question_shapes_are_supported_as_scripted_contracts(question, relation_bearing):
    raw = {"points": [{"text": "Answer the explicit request", "support_spans": [question],
                       "required_relations": ([{"text": "Answer the requested relation", "support_spans": [question]}]
                                              if relation_bearing else [])}],
           "ambiguity": {"status": "clear", "reason": ""}}
    value = QuestionDecomposer(ProposalVertex(raw)).decompose(question, relation_aware=True)
    assert bool(value["points"][0]["required_relations"]) is relation_bearing


def test_relation_order_and_ids_ignore_proposal_order_and_diagnostic_type():
    question = "Does Cedar depend on Birch and produce input for Maple?"
    one = {"text": "Whether Cedar depends on Birch", "support_spans": ["Cedar depend on Birch"],
           "relation_type": "dependency"}
    two = {"text": "Whether Cedar produces input for Maple", "support_spans": ["produce input for Maple"],
           "relation_type": "input_output"}
    def run(relations):
        raw = {"points": [{"text": "Answer the two requested relations", "support_spans": [question],
                           "required_relations": relations}], "ambiguity": {"status": "clear", "reason": ""}}
        return QuestionDecomposer(ProposalVertex(raw)).decompose(question, relation_aware=True)["points"][0]
    a = run([two, one])
    b = run([{**one, "relation_type": "invalid"}, {k: v for k, v in two.items() if k != "relation_type"}])
    assert [(r["relation_id"], r["text"]) for r in a["required_relations"]] == [
        (r["relation_id"], r["text"]) for r in b["required_relations"]]
    assert [r["relation_id"] for r in a["required_relations"]] == ["point.1.rel.1", "point.1.rel.2"]
    assert "relation_type" not in b["required_relations"][0]


def test_relation_question_limit_is_local_not_truncated():
    question = "Compare Cedar, Birch and Maple."
    def raw(counts):
        return {"points": [{"text": f"Request {i}", "support_spans": [question],
                            "required_relations": [{"text": f"Relation {i}-{j}", "support_spans": [question]}
                                                   for j in range(n)]} for i, n in enumerate(counts)],
                "ambiguity": {"status": "clear", "reason": ""}}
    assert sum(len(p["required_relations"]) for p in QuestionDecomposer(ProposalVertex(raw([3, 3, 3, 1]))).decompose(
        question, relation_aware=True)["points"]) == 10
    with pytest.raises(ValueError, match="question bound"):
        QuestionDecomposer(ProposalVertex(raw([3, 3, 3, 2]))).decompose(question, relation_aware=True)


def test_independently_omittable_ordinary_and_relational_requests_split():
    question = "Where is Cedar implemented and how does Cedar feed Birch?"
    raw = {"points": [
        {"text": "Explain how Cedar feeds Birch", "support_spans": ["how does Cedar feed Birch"],
         "required_relations": [{"text": "How Cedar feeds Birch", "support_spans": ["how does Cedar feed Birch"]}]},
        {"text": "Locate Cedar implementation", "support_spans": ["Where is Cedar implemented"],
         "required_relations": []}], "ambiguity": {"status": "clear", "reason": ""}}
    points = QuestionDecomposer(ProposalVertex(raw)).decompose(question, relation_aware=True)["points"]
    assert [p["answer_point_id"] for p in points] == ["point.1", "point.2"]
    assert points[0]["required_relations"] == []
    assert [r["relation_id"] for r in points[1]["required_relations"]] == ["point.2.rel.1"]


def test_duplicate_relation_across_parents_rejected():
    question = "How does Cedar feed Birch, and how does Birch differ from Maple?"
    raw = {"points": [
        {"text": "First request", "support_spans": [question],
         "required_relations": [{"text": "Requested relation", "support_spans": [question]}]},
        {"text": "Second request", "support_spans": [question],
         "required_relations": [{"text": " requested   RELATION ", "support_spans": [question]}]}],
         "ambiguity": {"status": "clear", "reason": ""}}
    with pytest.raises(ValueError, match="duplicate relation"):
        QuestionDecomposer(ProposalVertex(raw)).decompose(question, relation_aware=True)


@pytest.mark.parametrize("bad_span", ["does Cedar run before Birch?", "Does Cedar  run before Birch?", ""])
def test_relation_support_is_byte_exact(bad_span):
    value = production_point()
    value["required_relations"][0]["support_spans"] = [bad_span]
    with pytest.raises(ValueError):
        decompose(value)


@pytest.mark.parametrize("field,value", [("text", " "), ("text", 42), ("support_spans", "Cedar")])
def test_relation_bad_field_types_and_empty_text_rejected(field, value):
    raw = production_point()
    raw["required_relations"][0][field] = value
    with pytest.raises(ValueError):
        decompose(raw)


def named_check(rid, *, admission="ADMITTED_BACKING_AVAILABLE", satisfied=False,
                supporters=None, eid="e1", quote="The input is a record."):
    return {"relation_id": rid, "basis": [{"evidence_id": eid, "quote": quote}],
            "supporting_claim_ids": supporters or [], "satisfied": satisfied,
            "admission_state": admission}


def named_point(checks):
    supporters = list(dict.fromkeys(cid for c in checks for cid in c["supporting_claim_ids"]))
    return {"answer_point_id": "point.1", "supporting_claim_ids": supporters,
            "complete": all(c["satisfied"] for c in checks),
            "scope_status": ("INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE" if any(
                c["admission_state"] == "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE" for c in checks) else "ESTABLISHED"),
            "relationship_checks": [], "required_relation_checks": checks}


@pytest.mark.parametrize("mutation", [
    lambda v: v["answer_point_coverage"][0]["required_relation_checks"].append(
        deepcopy(v["answer_point_coverage"][0]["required_relation_checks"][0])),
    lambda v: v["answer_point_coverage"][0]["required_relation_checks"][0].update(relation_id="point.9.rel.1"),
    lambda v: v["answer_point_coverage"][0]["required_relation_checks"][0].update(relation_id="point.2.rel.1"),
    lambda v: v["answer_point_coverage"][0].update(supporting_claim_ids=[]),
    lambda v: v["answer_point_coverage"][0].update(complete=False),
    lambda v: v.update(missing_answer_point_ids=["point.1"]),
    lambda v: v["answer_point_coverage"][0].update(scope_status="OVERFLOW"),
])
def test_named_disposition_rejects_inventory_and_consistency_errors(tmp_path, mutation):
    claims, evidence = fixture(tmp_path)
    canonical = [{"answer_point_id": "point.1", "required_relations": [{"relation_id": "point.1.rel.1"}]},
                 {"answer_point_id": "point.2", "required_relations": [{"relation_id": "point.2.rel.1"}]}]
    first = named_point([named_check("point.1.rel.1", satisfied=True, supporters=["c1"])])
    second = {**named_point([named_check("point.2.rel.1", satisfied=True, supporters=["c2"])]),
              "answer_point_id": "point.2"}
    value = c1_review([first, second])
    mutation(value)
    with pytest.raises(ValueError):
        qa._validate_coverage_satisfaction(value, claims, {"point.1", "point.2"}, set(), evidence,
                                           {"e1"}, canonical_points=canonical)


@pytest.mark.parametrize("admission,satisfied,supporters,scope,complete", [
    ("ADMITTED_BACKING_AVAILABLE", True, ["c1"], "ESTABLISHED", True),
    ("ADMITTED_BACKING_AVAILABLE", False, [], "ESTABLISHED", False),
    ("VISIBLE_ONLY_WITHOUT_CITABLE_BACKING", False, [], "ESTABLISHED", False),
    ("INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE", False, [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE", False),
])
def test_named_admission_dispositions(tmp_path, admission, satisfied, supporters, scope, complete):
    claims, evidence = fixture(tmp_path)
    claims = claims[:1]
    evidence["page"] = {"evidence_id": "page", "text": "Visible page"}
    named = named_check("point.1.rel.1", admission=admission, satisfied=satisfied, supporters=supporters,
                        eid="page" if admission == "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING" else "e1",
                        quote="Visible page" if admission == "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING" else "The input is a record.")
    record = named_point([named])
    value = c1_review([record], {"c1": ["point.1"]})
    assert record["scope_status"] == scope and record["complete"] == complete
    assert qa._validate_coverage_satisfaction(value, claims, {"point.1"}, set(), evidence, {"e1"},
        canonical_points=[{"answer_point_id": "point.1", "required_relations": [{"relation_id": "point.1.rel.1"}]}])


def test_target_local_revision_and_full_v2_contract(tmp_path):
    question = "Does Cedar run before Birch and feed Maple?"
    proposal = {"points": [{"text": "Answer both requested relations", "support_spans": [question],
        "required_relations": [{"text": "Whether Cedar runs before Birch", "support_spans": [question]},
                               {"text": "Whether Cedar feeds Maple", "support_spans": [question]}]}],
        "ambiguity": {"status": "clear", "reason": ""}}
    admitted = named_check("point.1.rel.1")
    blocked = named_check("point.1.rel.2", admission="VISIBLE_ONLY_WITHOUT_CITABLE_BACKING",
                          eid="page", quote="Visible page")
    first = c1_review([named_point([admitted, blocked])], {"c1": ["point.1"]})
    repaired = named_check("point.1.rel.1", satisfied=True, supporters=["c2"])
    second = c1_review([named_point([repaired, blocked])], {"c1": ["point.1"], "c2": ["point.1"]})
    vertex = RecordingVertex(decomposition=proposal, answers=[claim()],
        revisions=[claim("c2", "point.1", "The input is a record.")], reviews=[first, second])
    runner = agent(tmp_path, vertex)
    runner.retriever.bundle["evidence"].append({"evidence_id": "page", "object_id": "page",
        "source_id": "synthetic_sphinx", "source_version_id": "synthetic_sphinx@snapshot",
        "text": "Visible page", "locator": {"section_path": []}})
    out = runner._run_detailed(question, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=True)
    assert out["diagnostics"]["revision_count"] == 1
    assert out["result"]["status"] == "insufficient_evidence"
    assert out["diagnostics"]["answer_point_audit"]["missing_answer_point_ids"] == ["point.1"]
    payloads = [json.loads(p) for p, _, _ in vertex.exact_calls]
    a1 = next(p for p in payloads if p["task"] == "revise_unsupported_claims_once")
    assert [r["relation_id"] for r in a1["revisionable_relationships"]] == ["point.1.rel.1"]
    assert [r["relation_id"] for r in a1["runtime_answer_points"][0]["required_relations"]] == ["point.1.rel.1"]
    reviews = [p for p in payloads if p["task"] == "review_claim_support_and_relevance"]
    assert len(reviews) == 2
    assert [r["relation_id"] for r in reviews[1]["runtime_answer_points"][0]["required_relations"]] == [
        "point.1.rel.1", "point.1.rel.2"]


def test_two_admitted_targets_share_one_revision(tmp_path):
    question = "Does Cedar depend on Birch and produce input for Maple?"
    proposal = {"points": [{"text": "Answer both relations", "support_spans": [question],
        "required_relations": [{"text": "Whether Cedar depends on Birch", "support_spans": [question]},
                               {"text": "Whether Cedar produces input for Maple", "support_spans": [question]}]}],
        "ambiguity": {"status": "clear", "reason": ""}}
    first = c1_review([named_point([named_check("point.1.rel.1"), named_check("point.1.rel.2")])],
                      {"c1": ["point.1"]})
    repaired = c1_review([named_point([named_check("point.1.rel.1", satisfied=True, supporters=["c2"]),
                                       named_check("point.1.rel.2", satisfied=True, supporters=["c2"])])],
                         {"c1": ["point.1"], "c2": ["point.1"]})
    vertex = RecordingVertex(decomposition=proposal, answers=[claim()],
        revisions=[claim("c2", "point.1", "The input is a record.")], reviews=[first, repaired])
    out = agent(tmp_path, vertex)._run_detailed(question, mode=qa.DEFAULT_ANSWER_POINT_MODE)
    payloads = [json.loads(p) for p, _, _ in vertex.exact_calls]
    revisions = [p for p in payloads if p["task"] == "revise_unsupported_claims_once"]
    assert out["diagnostics"]["revision_count"] == 1 and len(revisions) == 1
    assert {r["relation_id"] for r in revisions[0]["revisionable_relationships"]} == {
        "point.1.rel.1", "point.1.rel.2"}


def test_uncertain_sibling_does_not_suppress_admitted_target(tmp_path):
    review = c1_review([named_point([named_check("point.1.rel.1"),
        named_check("point.1.rel.2", admission="INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE")])],
        {"c1": ["point.1"]})
    runner = agent(tmp_path, RecordingVertex(reviews=[review]))
    canonical = [{"answer_point_id": "point.1", "text": "Answer both relations",
                  "support_spans": [QUESTION], "required_relations": [
                      {"relation_id": "point.1.rel.1", "text": "Whether Cedar runs before Birch",
                       "support_spans": [QUESTION]},
                      {"relation_id": "point.1.rel.2", "text": "Whether Cedar depends on Birch",
                       "support_spans": [QUESTION]}]}]
    s = state(runner, [claim()], canonical)
    s["answer_point_coverage_mode"] = qa.DEFAULT_ANSWER_POINT_MODE
    s.update(runner._verify(s))
    assert s["answer_point_audit"]["coverage_evaluable"]
    assert s["answer_point_audit"]["answer_point_coverage"][0]["scope_status"] == "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE"
    assert [r["relation_id"] for r in s["revisionable_relationships"]] == ["point.1.rel.1"]
    assert runner._after_verify_route(s) == "revise"


def test_provider_schemas_stay_simple_and_fingerprint_binds_both_profiles(monkeypatch):
    def keys(value):
        if isinstance(value, dict):
            for key, child in value.items():
                yield key
                yield from keys(child)
        elif isinstance(value, list):
            for child in value:
                yield from keys(child)
    forbidden = {"minItems", "maxItems", "minLength", "maxLength", "uniqueItems", "if", "then", "else"}
    assert not forbidden & set(keys(question_decomposition.PRODUCTION_QUESTION_DECOMPOSITION_SCHEMA))
    assert not forbidden & set(keys(qa.PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA))
    initial = evaluation_runner.prompt_fingerprint()
    with monkeypatch.context() as patch:
        patch.setattr(question_decomposition, "QUESTION_DECOMPOSITION_V2_PROMPT_VERSION", "changed")
        assert evaluation_runner.prompt_fingerprint() != initial
    with monkeypatch.context() as patch:
        patch.setattr(question_decomposition, "PRODUCTION_QUESTION_DECOMPOSITION_SCHEMA", {"changed": True})
        assert evaluation_runner.prompt_fingerprint() != initial
    with monkeypatch.context() as patch:
        patch.setattr(evaluation_runner, "PROMPT_SET_VERSION", "changed")
        assert evaluation_runner.prompt_fingerprint() != initial
