"""E2-A1 fake-only contract and normal-mode regression checks."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from panda_agent.models import QAResult, ClaimCitation
from panda_agent.prompts import (
    ANSWER_SYSTEM_PROMPT, EVIDENCE_REVIEW_SYSTEM_PROMPT, REVISION_SYSTEM_PROMPT,
    ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT, ANSWER_POINT_COVERAGE_REVISION_SYSTEM_PROMPT,
)
from panda_agent.qa import (
    QAAgent, ANSWER_SCHEMA, REVIEW_SCHEMA, ANSWER_POINT_COVERAGE_REVIEW_SCHEMA,
    _active_runtime_answer_points, _validate_answer_point_review,
)
from test_qa import FakeRetriever, bundle_for, code_evidence, production_review_fixture

QUESTION = "Describe the input and the output."
POINTS = [{"answer_point_id": "point.1", "text": "Describe the input."},
          {"answer_point_id": "point.2", "text": "Describe the output."}]


def claim(cid="c1", point="point.1", text="The input is a record.", evidence="e1"):
    return dict(claim_id=cid, claim_text=text, evidence_ids=[evidence], answer_point_ids=[point])


def coverage_records(mappings=None, missing=(), unsupported=(), irrelevant=(), points=None):
    excluded = set(unsupported) | set(irrelevant)
    by_point = {}
    for cid, pts in (mappings or {}).items():
        if cid in excluded:
            continue
        for pid in pts:
            by_point.setdefault(pid, []).append(cid)
    return [dict(answer_point_id=p["answer_point_id"],
                 supporting_claim_ids=by_point.get(p["answer_point_id"], []),
                 complete=p["answer_point_id"] not in set(missing))
            for p in (points or POINTS)]


def review(mappings=None, missing=(), unsupported=(), irrelevant=(), requirements=(), points=None):
    return dict(supported=True, unsupported_claim_ids=list(unsupported), irrelevant_claim_ids=list(irrelevant),
                missing_requirement_ids=list(requirements), reason="",
                claim_answer_point_mappings=[dict(claim_id=k, answer_point_ids=v) for k,v in (mappings or {}).items()],
                missing_answer_point_ids=list(missing),
                answer_point_coverage=coverage_records(mappings, missing, unsupported, irrelevant, points))


def proposal():
    return dict(points=[dict(text=p["text"], support_spans=["input" if i==0 else "output"], facet_type="definition")
                        for i,p in enumerate(POINTS)], ambiguity=dict(status="clear", reason=""))


class Vertex:
    def __init__(self, answers=None, reviews=None, revisions=None, decomposition=None):
        self.answers = answers if answers is not None else [claim(), claim("c2", "point.2", "The output is a table.")]
        self.reviews = list(reviews or [review({"c1":["point.1"], "c2":["point.2"]})])
        self.revisions = revisions or []
        self.decomposition = decomposition if decomposition is not None else proposal()
        self.calls = []

    def stats_snapshot(self):
        return dict(model_calls=len(self.calls), generation_calls=len(self.calls), token_usage=len(self.calls)*5, embedding_calls=0)

    def stats_delta(self, before):
        return {k:v-before.get(k,0) for k,v in self.stats_snapshot().items()}

    def generate_json(self, prompt, schema, **kwargs):
        p=json.loads(prompt)
        self.calls.append((p, deepcopy(schema), kwargs))
        if p["task"] == "decompose_user_question":
            if isinstance(self.decomposition, Exception):
                raise self.decomposition
            result = deepcopy(self.decomposition)
            if "required_relations" in schema["properties"]["points"]["items"].get("required", []):
                for point in result["points"]:
                    point.setdefault("required_relations", [])
            return result
        if p["task"] == "review_claim_support_and_relevance":
            return production_review_fixture(deepcopy(self.reviews.pop(0)), p)
        if p["task"] == "revise_unsupported_claims_once":
            return {"claims":deepcopy(self.revisions)}
        return {"claims":deepcopy(self.answers)}


def agent(tmp_path, vertex=None, bundle=None):
    vertex=vertex or Vertex()
    retriever=FakeRetriever(bundle or bundle_for(code_evidence(text="The input is a record. The output is a table.",path="input.h")))
    return QAAgent(tmp_path,retriever=retriever,vertex=vertex)


def state(a, claims, points=None):
    runtime_points = deepcopy(points or POINTS)
    for p in runtime_points:
        p.setdefault("support_spans", [QUESTION])
        p.setdefault("required_relations", [])
    return dict(question=QUESTION, bundle=a.retriever.bundle, sufficient=True,
                answer_point_coverage_mode="shadow_e1_v2", runtime_answer_points=runtime_points,
                draft={"claims":claims}, answer_requirements=[])


def test_projection_explicit_entrypoint_usage_and_dto(tmp_path):
    a=agent(tmp_path); out=a.run_answer_point_coverage_diagnostic(QUESTION)
    assert [c[0]["task"] for c in a.vertex.calls] == ["decompose_user_question","create_atomic_evidence_bound_claims","review_claim_support_and_relevance","compose_verified_claims"]
    assert a.vertex.calls[0][0] == {"task":"decompose_user_question","untrusted_question":QUESTION}
    for payload,_,_ in a.vertex.calls[1:3]:
        assert payload["runtime_answer_points"] == POINTS
        assert all(x not in json.dumps(payload) for x in ["facet_type","support_spans","ambiguity","expected_count","Gold"])
    assert a.vertex.calls[2][1] == ANSWER_POINT_COVERAGE_REVIEW_SCHEMA
    assert a.vertex.calls[2][2]["system_instruction"] == ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT
    audit=out["diagnostics"]["answer_point_audit"]
    assert audit["coverage_complete"] and audit["coverage_evaluable"]
    assert all(m["rendered"] for m in audit["claim_mappings"])
    assert out["model_usage"]["model_calls"] == 4
    assert out["model_usage"]["token_usage"] == 20
    assert "question_decomposition" in out["node_timings_ms"]
    assert out["diagnostics"]["question_decomposition"]["points"][0]["facet_type"] == "definition"
    assert set(ClaimCitation.model_fields) == {"claim_id","claim_text","evidence_ids"}
    assert set(QAResult.model_fields) == {"status","answer","claims","evidence","resolved_versions","verification_errors"}
    assert all(set(c)==set(ClaimCitation.model_fields) for c in out["result"]["claims"])


def test_explicit_legacy_mode_unchanged(tmp_path):
    r={k:v for k,v in review().items() if k in REVIEW_SCHEMA["required"]}
    v=Vertex(answers=[claim(point="question_core")],reviews=[r])
    a=agent(tmp_path,v)
    a.decompose_question=lambda question: pytest.fail("explicit legacy mode must not decompose")
    out=a._run_detailed(QUESTION, mode="legacy_question_core")
    assert len(v.calls)==2 and a.retriever.calls==1
    assert v.calls[0][1]==ANSWER_SCHEMA and v.calls[0][2]["system_instruction"]==ANSWER_SYSTEM_PROMPT
    assert v.calls[1][1]==REVIEW_SCHEMA and v.calls[1][2]["system_instruction"]==EVIDENCE_REVIEW_SYSTEM_PROMPT
    assert v.calls[0][0]["runtime_answer_points"]==[{"answer_point_id":"question_core","text":QUESTION}]
    result=out["result"]
    assert "answer_point_ids" not in json.dumps(result)
    assert "answer_point_audit" not in out["diagnostics"]


def test_semantic_mapping_corrects_proposal_and_retains_declaration(tmp_path):
    v=Vertex(reviews=[review({"c1":["point.2"]},missing=["point.1"])])
    a=agent(tmp_path,v); s=state(a,[claim(text="The output is a table.")])
    o=a._verify(s)
    assert o["supported_claims"][0]["answer_point_ids"]==["point.2"]
    m=o["answer_point_audit"]["claim_mappings"][0]
    assert m["declared_answer_point_ids"]==["point.1"] and m["verified_answer_point_ids"]==["point.2"] and m["supported"]
    assert o["missing_answer_point_ids"]==["point.1"]


@pytest.mark.parametrize("bad", ["unknown_point","missing_mapping","unknown_evidence","wrong_version","unsupported_identifier","duplicate_claim"])
def test_deterministically_invalid_claim_cannot_cover(tmp_path,bad):
    v=Vertex(reviews=[review({},missing=["point.1","point.2"])])
    a=agent(tmp_path,v); c=claim()
    if bad=="unknown_point":c["answer_point_ids"]=["invented"]
    if bad=="missing_mapping":c["answer_point_ids"]=[]
    if bad=="unknown_evidence":c["evidence_ids"]=["invented"]
    if bad=="wrong_version":a.retriever.bundle["evidence"][0]["source_version_id"]="pandaroot@wrong"
    if bad=="unsupported_identifier":c["claim_text"]="Located at src/invented.cpp."
    o=a._verify(state(a,[c,c] if bad=="duplicate_claim" else [c]))
    assert v.calls[0][0]["untrusted_claims"]==[]
    assert not o["supported_claims"] and not o["answer_point_audit"]["covered_answer_point_ids"]


def test_mapping_relevance_not_collective_completeness(tmp_path):
    p=[{"answer_point_id":"point.1","text":"Compare the two approaches."}]
    a=agent(tmp_path,Vertex(reviews=[review({"c1":["point.1"]},missing=["point.1"],points=p)]))
    o=a._verify(state(a,[claim(text="The first approach uses a record.")],p))
    assert o["supported_claims"] and not o["answer_point_audit"]["coverage_complete"]
    assert o["answer_point_audit"]["covered_answer_point_ids"]==[]
    assert o["missing_answer_point_ids"]==["point.1"]


@pytest.mark.parametrize("fixed", [True,False])
def test_missing_point_reuses_one_revision_without_retrieval(tmp_path,fixed):
    first=review({"c1":["point.1"]},missing=["point.2"])
    second=review({"c1":["point.1"],"c2":["point.2"]}) if fixed else first
    v=Vertex(answers=[claim()],reviews=[first,second],revisions=[claim("c2","point.2","The output is a table.")] if fixed else [])
    a=agent(tmp_path,v);out=a.run_answer_point_coverage_diagnostic(QUESTION)
    assert a.retriever.calls==1 and out["diagnostics"]["revision_count"]==1
    assert len(v.calls)==(6 if fixed else 5)
    payload,_,kw=v.calls[3]
    assert payload["missing_answer_point_ids"]==["point.2"] and payload["missing_answer_points"]==[POINTS[1]]
    assert payload["untrusted_evidence"]==a.retriever.bundle["evidence"]
    assert kw["system_instruction"]==ANSWER_POINT_COVERAGE_REVISION_SYSTEM_PROMPT
    audit=out["diagnostics"]["answer_point_audit"]
    assert audit["coverage_complete"]==fixed
    assert audit["missing_answer_point_ids"]==([] if fixed else ["point.2"])
    assert all(m["rendered"] for m in audit["claim_mappings"])


def test_corrected_declaration_survives_final_verify(tmp_path):
    a=agent(tmp_path,Vertex(answers=[claim(text="The output is a table.")],
        reviews=[review({"c1":["point.2"]},missing=["point.1"]),review({"c1":["point.2"],"c2":["point.1"]})],
        revisions=[claim("c2","point.1")]))
    o=a.run_answer_point_coverage_diagnostic(QUESTION)
    m=next(m for m in o["diagnostics"]["answer_point_audit"]["claim_mappings"] if m["claim_id"]=="c1")
    assert m["declared_answer_point_ids"]==["point.1"] and m["verified_answer_point_ids"]==["point.2"]


@pytest.mark.parametrize("kind",["unsupported","irrelevant"])
def test_semantic_rejection_cannot_cover_even_code_anchored_claim(tmp_path,kind):
    kw={kind:["c1"]}
    a=agent(tmp_path,Vertex(reviews=[review({"c1":["point.1"]},missing=["point.1","point.2"],**kw)]))
    c=claim(text="The implementation is at input.h.")
    o=a._verify(state(a,[c]))
    assert not o["supported_claims"]
    assert not o["answer_point_audit"]["covered_answer_point_ids"]
    assert not o["answer_point_audit"]["claim_mappings"][0]["supported"]


@pytest.mark.parametrize("cid",["required_workflow","required_code","scope_x","dataflow_locator_x","internal"])
def test_internal_claims_never_enter_coverage(tmp_path,cid):
    a=agent(tmp_path,Vertex(reviews=[review({},missing=["point.1","point.2"])]))
    c=claim(cid=cid,text="curated_panda_domain" if cid=="internal" else "Internal evidence anchor.")
    o=a._verify(state(a,[c]))
    assert o["claim_audit"] and o["answer_point_audit"]["claim_mappings"]==[]
    assert a.vertex.calls[0][0]["untrusted_claims"]==[]
    assert not o["answer_point_audit"]["covered_answer_point_ids"]


def test_deterministic_locator_requires_semantic_mapping(tmp_path):
    b=bundle_for(code_evidence(text="class Widget {};",path="src/Widget.h"),symbols=["src/Widget.h"])
    a=agent(tmp_path,Vertex(),b)
    s=state(a,[]);s["question"]="Where is Widget implemented?"
    d=a._augment_planned_locators({"claims":[]},s)
    c=d["claims"][0];assert c["answer_point_ids"]==[]
    a.vertex.reviews=[review({c["claim_id"]:["point.2"]},missing=["point.1"])]
    s["draft"]=d;o=a._verify(s)
    assert o["supported_claims"][0]["answer_point_ids"]==["point.2"]
    assert o["answer_point_audit"]["claim_mappings"][0]["declared_answer_point_ids"]==[]
    s.pop("answer_point_coverage_mode")
    assert a._augment_planned_locators({"claims":[]},s)["claims"][0]["answer_point_ids"]==["question_core"]


@pytest.mark.parametrize("missing_point",[True,False])
def test_legacy_requirements_are_non_authoritative_in_coverage_modes(tmp_path,missing_point):
    rs=review({"c1":["point.1"],"c2":["point.2"]},missing=["point.2"] if missing_point else [],requirements=[] if missing_point else ["custom_obligation"])
    a=agent(tmp_path,Vertex(reviews=[rs]));s=state(a,[claim(),claim("c2","point.2","The output is a table.")])
    s["answer_requirements"]=[{"id":"custom_obligation","instruction":"An independent compatibility obligation."}]
    o=a._verify(s)
    assert o["missing_requirement_ids"]==[]
    assert not any("missing answer requirement" in err for err in o["errors"])
    assert o["missing_answer_point_ids"]==(["point.2"] if missing_point else [])


@pytest.mark.parametrize("points",[[],[{"answer_point_id":"","text":"x"}],[{"answer_point_id":"a","text":""}],POINTS+POINTS])
def test_invalid_projection_no_fallback(points):
    with pytest.raises(ValueError):
        _active_runtime_answer_points({"question":QUESTION,"answer_point_coverage_mode":"shadow_e1_v2","runtime_answer_points":points})


def test_decomposition_failure_visible_before_retrieval(tmp_path):
    a=agent(tmp_path,Vertex(decomposition=ValueError("invalid decomposition")))
    with pytest.raises(ValueError,match="invalid decomposition"):
        a.run_answer_point_coverage_diagnostic(QUESTION)
    assert a.retriever.calls==0 and len(a.vertex.calls)==1


def test_early_refusal_coverage_not_evaluable(tmp_path):
    b=bundle_for([],conflicts=["version mismatch"])
    a=agent(tmp_path,Vertex(),b);o=a.run_answer_point_coverage_diagnostic(QUESTION)
    assert len(a.vertex.calls)==1
    audit=o["diagnostics"]["answer_point_audit"]
    assert not audit["coverage_evaluable"] and not audit["coverage_complete"]
    assert audit["claim_mappings"]==[] and audit["covered_answer_point_ids"]==[]


@pytest.mark.parametrize("bad",["unknown_claim","duplicate_record","missing_record","unknown_point","duplicate_point","unknown_unsupported","unknown_irrelevant","duplicate_missing","unknown_missing","unsupported_covered","irrelevant_covered","unmapped_relevant"])
def test_invalid_reviewer_contract_fails_closed(tmp_path,bad):
    rs=review({"c1":["point.1"]},missing=["point.2"])
    if bad=="unknown_claim":rs["claim_answer_point_mappings"][0]["claim_id"]="invented"
    if bad=="duplicate_record":rs["claim_answer_point_mappings"]*=2
    if bad=="missing_record":rs["claim_answer_point_mappings"]=[]
    if bad=="unknown_point":rs["claim_answer_point_mappings"][0]["answer_point_ids"]=["invented"]
    if bad=="duplicate_point":rs["claim_answer_point_mappings"][0]["answer_point_ids"]*=2
    if bad=="unknown_unsupported":rs["unsupported_claim_ids"]=["invented"]
    if bad=="unknown_irrelevant":rs["irrelevant_claim_ids"]=["invented"]
    if bad=="duplicate_missing":rs["missing_answer_point_ids"]*=2
    if bad=="unknown_missing":rs["missing_answer_point_ids"]=["invented"]
    if bad=="unsupported_covered":rs["unsupported_claim_ids"]=["c1"]
    if bad=="irrelevant_covered":rs["irrelevant_claim_ids"]=["c1"]
    if bad=="unmapped_relevant":rs["claim_answer_point_mappings"][0]["answer_point_ids"]=[]
    a=agent(tmp_path,Vertex(reviews=[rs]));o=a._verify(state(a,[claim()]))
    assert not o["supported_claims"] and o["answer_point_audit"]["covered_answer_point_ids"]==[]
    assert not o["answer_point_audit"]["coverage_evaluable"]
    assert any("invalid answer-point coverage review" in e for e in o["errors"])
