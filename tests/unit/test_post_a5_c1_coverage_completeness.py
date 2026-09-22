"""C1 synthetic deterministic contract tests; no scientific calls."""
from copy import deepcopy
import json

import pytest

from panda_agent import qa
from test_e2_a1_answer_point_coverage import agent, claim, review, state, POINTS, QUESTION
from test_post_a5_o1_observability import RecordingVertex, assert_neutral, event


def test_production_schema_exists_and_is_distinct():
    assert qa.COVERAGE_SATISFACTION_SCHEMA_VERSION == "coverage-satisfaction-v1"
    schema = qa.PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA
    assert schema != qa.ANSWER_POINT_COVERAGE_REVIEW_SCHEMA
    assert set(schema["properties"]["answer_point_coverage"]["items"]["required"]) == {
        "answer_point_id", "supporting_claim_ids", "complete", "scope_status", "relationship_checks"}


def test_production_provider_schema_uses_supported_bounded_keywords():
    allowed = {
        "$id", "$defs", "$ref", "$anchor", "type", "format", "title", "description",
        "enum", "items", "prefixItems", "minItems", "maxItems", "minimum", "maximum",
        "anyOf", "oneOf", "properties", "additionalProperties", "required", "propertyOrdering",
    }

    def schema_keywords(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "properties" and isinstance(child, dict):
                    yield key
                    for property_schema in child.values():
                        yield from schema_keywords(property_schema)
                else:
                    yield key
                    yield from schema_keywords(child)
        elif isinstance(value, list):
            for child in value:
                yield from schema_keywords(child)

    observed = set(schema_keywords(qa.PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA))
    assert observed <= allowed
    assert not observed & {"uniqueItems", "minLength", "maxLength"}
    assert not observed & {"minItems", "maxItems"}


def test_production_invalid_scope_cannot_route_to_revision(tmp_path):
    runner = agent(tmp_path)
    s = {"answer_point_coverage_mode": "production_answer_obligations_v1", "errors": ["invalid review"],
         "revision_count": 0, "revisionable_relationships": [], "revisionable_unsupported_claim_ids": []}
    assert runner._after_verify_route(s) == "finalize"


def check(text="The input is a record.", supporters=None, admitted="ADMITTED_BACKING_AVAILABLE", eid="e1"):
    return {"relationship_text": text, "necessity_reason": "Directly answers the requested point.",
            "basis": [{"evidence_id": eid, "quote": text}], "supporting_claim_ids": ["c1"] if supporters is None else supporters,
            "satisfied": bool(["c1"] if supporters is None else supporters), "admission_state": admitted}


def point(pid, checks, status="ESTABLISHED"):
    supporters = list(dict.fromkeys(cid for c in checks for cid in c["supporting_claim_ids"]))
    return {"answer_point_id": pid, "supporting_claim_ids": supporters,
            "complete": status == "ESTABLISHED" and bool(checks) and all(c["satisfied"] for c in checks),
            "scope_status": status, "relationship_checks": checks}


def c1_review(points=None, mappings=None, unsupported=(), irrelevant=()):
    points = points if points is not None else [point("point.1", [check()]),
        point("point.2", [check("The output is a table.", ["c2"])])]
    value = review(mappings if mappings is not None else {"c1": ["point.1"], "c2": ["point.2"]},
                   missing=[p["answer_point_id"] for p in points if not p["complete"]],
                   unsupported=unsupported, irrelevant=irrelevant)
    value["answer_point_coverage"] = points
    return value


def fixture(tmp_path):
    runner = agent(tmp_path)
    claims = [claim(), claim("c2", "point.2", "The output is a table.")]
    evidence = {e["evidence_id"]: e for e in runner.retriever.bundle["evidence"]}
    return claims, evidence


def validate(tmp_path, value):
    claims, evidence = fixture(tmp_path)
    return qa._validate_coverage_satisfaction(value, claims, {"point.1", "point.2"}, set(), evidence, {"e1"})


def test_complete_scope_and_optional_fact_omission(tmp_path):
    claims, evidence = fixture(tmp_path)
    evidence["e1"]["text"] += " An optional detail is uncertain."
    assert qa._validate_coverage_satisfaction(c1_review(), claims, {"point.1", "point.2"}, set(), evidence, {"e1"})


@pytest.mark.parametrize("kind", ["extra_top", "extra_point", "extra_check", "extra_basis", "missing_point",
    "duplicate_point", "unknown_point", "bad_bool", "bad_status", "bad_admission", "empty_scope",
    "empty_text", "long_text", "long_reason", "long_quote", "fuzzy_quote", "case_quote", "space_quote",
    "unknown_basis", "duplicate_basis", "three_basis", "five_checks", "nine_supporters", "33_supporters",
    "unknown_supporter", "unsupported_supporter", "irrelevant_supporter", "wrong_mapping", "uncited_basis",
    "empty_satisfied", "visible_admitted", "uncertain_satisfied", "point_union", "union_order",
    "missing_complement", "duplicate_text", "uncertain_scope", "overflow_complete", "false_complete"])
def test_structural_rejection(tmp_path, kind):
    value = c1_review()
    p = value["answer_point_coverage"][0]
    c = p["relationship_checks"][0]
    claims, evidence = fixture(tmp_path)
    if kind == "extra_top": value["other"] = 1
    elif kind == "extra_point": p["other"] = 1
    elif kind == "extra_check": c["relationship_id"] = "r1"
    elif kind == "extra_basis": c["basis"][0]["other"] = 1
    elif kind == "missing_point": value["answer_point_coverage"].pop()
    elif kind == "duplicate_point": value["answer_point_coverage"].append(deepcopy(p))
    elif kind == "unknown_point": p["answer_point_id"] = "unknown"
    elif kind == "bad_bool": c["satisfied"] = 1
    elif kind == "bad_status": p["scope_status"] = []
    elif kind == "bad_admission": c["admission_state"] = "other"
    elif kind == "empty_scope": p["relationship_checks"] = []
    elif kind == "empty_text": c["relationship_text"] = " "
    elif kind == "long_text": c["relationship_text"] = "x" * 241
    elif kind == "long_reason": c["necessity_reason"] = "x" * 161
    elif kind == "long_quote": c["basis"][0]["quote"] = "x" * 401
    elif kind == "fuzzy_quote": c["basis"][0]["quote"] = "Input consists of records."
    elif kind == "case_quote": c["basis"][0]["quote"] = "the input is a record."
    elif kind == "space_quote": c["basis"][0]["quote"] = "The input  is a record."
    elif kind == "unknown_basis": c["basis"][0]["evidence_id"] = "unknown"
    elif kind == "duplicate_basis": c["basis"] *= 2
    elif kind == "three_basis": c["basis"] *= 3
    elif kind == "five_checks": p["relationship_checks"] *= 5
    elif kind == "nine_supporters": c["supporting_claim_ids"] = [str(i) for i in range(9)]
    elif kind == "33_supporters": p["supporting_claim_ids"] = [str(i) for i in range(33)]
    elif kind == "unknown_supporter": c["supporting_claim_ids"] = ["unknown"]
    elif kind == "unsupported_supporter": value["unsupported_claim_ids"] = ["c1"]
    elif kind == "irrelevant_supporter": value["irrelevant_claim_ids"] = ["c1"]
    elif kind == "wrong_mapping": c["supporting_claim_ids"] = ["c2"]
    elif kind == "uncited_basis": claims[0]["evidence_ids"] = ["different"]
    elif kind == "empty_satisfied": c["supporting_claim_ids"] = []
    elif kind == "visible_admitted": c.update(admission_state="VISIBLE_ONLY_WITHOUT_CITABLE_BACKING", satisfied=False, supporting_claim_ids=[])
    elif kind == "uncertain_satisfied": c["admission_state"] = "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE"
    elif kind == "point_union": p["supporting_claim_ids"] = []
    elif kind == "union_order":
        value["claim_answer_point_mappings"][1]["answer_point_ids"] = ["point.1", "point.2"]
        c["supporting_claim_ids"] = ["c2", "c1"]
        p["supporting_claim_ids"] = ["c2", "c1"]
    elif kind == "missing_complement": value["missing_answer_point_ids"] = ["point.1"]
    elif kind == "duplicate_text": p["relationship_checks"].append({**deepcopy(c), "relationship_text": "The  input is a record."})
    elif kind == "uncertain_scope": p["scope_status"] = "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE"
    elif kind == "overflow_complete": p["scope_status"] = "OVERFLOW"
    elif kind == "false_complete": c.update(satisfied=False, supporting_claim_ids=[])
    with pytest.raises(ValueError):
        qa._validate_coverage_satisfaction(value, claims, {"point.1", "point.2"}, set(), evidence, {"e1"})


@pytest.mark.parametrize("scope", ["INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE", "OVERFLOW"])
def test_declared_blocked_scope_no_revision(tmp_path, scope):
    value = c1_review([point("point.1", [], scope), point("point.2", [], scope)])
    runner = agent(tmp_path, RecordingVertex(reviews=[value]))
    s = state(runner, [claim(), claim("c2", "point.2", "The output is a table.")])
    s["answer_point_coverage_mode"] = qa.DEFAULT_ANSWER_POINT_MODE
    s.update(runner._verify(s))
    assert s["answer_point_audit"]["coverage_evaluable"]
    assert runner._after_verify_route(s) == "finalize"
    result = runner._finalize(s)["result"]
    assert result["status"] == "insufficient_evidence"
    assert len(result["claims"]) == 2
    assert result["answer"].endswith(qa.C1_INCOMPLETE_NOTICE)
    assert len(runner.vertex.calls) == 1


def test_invalid_review_preserves_independent_claims_no_retry(tmp_path):
    value = c1_review()
    value["answer_point_coverage"][0]["relationship_checks"][0]["basis"][0]["quote"] = "invented"
    vertex = RecordingVertex(reviews=[value])
    runner = agent(tmp_path, vertex)
    out = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=True)
    assert out["result"]["status"] == "insufficient_evidence"
    assert len(out["result"]["claims"]) == 2
    assert not out["diagnostics"]["answer_point_audit"]["coverage_evaluable"]
    assert out["diagnostics"]["revision_count"] == 0
    assert len(vertex.exact_calls) == 3
    payload = event(out, "V1_OUTPUT")["payload"]
    assert payload["response"] == value and payload["validation"]["status"] == "REJECTED"


def test_mixed_scope_revision_then_partial_and_trace_neutrality(tmp_path):
    runs = []
    for capture in (False, True):
        r1 = check()
        missing = check("The output is a table.", [])
        blocked = check("The final handoff needs approval.", [], "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING", "page")
        before = c1_review([point("point.1", [r1, missing, blocked]),
                           point("point.2", [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE")], {"c1": ["point.1"]})
        after = c1_review([point("point.1", [r1, {**missing, "satisfied": True, "supporting_claim_ids": ["c2"]}, blocked]),
                          point("point.2", [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE")], {"c1": ["point.1"], "c2": ["point.1"]})
        vertex = RecordingVertex(answers=[claim()], revisions=[claim("c2", "point.1", "The output is a table.")], reviews=[before, after])
        runner = agent(tmp_path, vertex)
        runner.retriever.bundle["evidence"].append({"evidence_id": "page", "object_id": "page",
            "source_id": "synthetic_sphinx", "source_version_id": "synthetic_sphinx@snapshot",
            "text": blocked["relationship_text"], "locator": {"url": "https://example.invalid", "snapshot_date": "2000-01-01", "section_path": []}})
        original = deepcopy(runner.retriever.bundle)
        out = runner._run_detailed(QUESTION, mode=qa.DEFAULT_ANSWER_POINT_MODE, capture_stage_trace=capture)
        assert runner.retriever.bundle == original and runner.retriever.calls == 1
        assert out["result"]["status"] == "insufficient_evidence" and len(out["result"]["claims"]) == 2
        assert out["result"]["answer"].endswith(qa.C1_INCOMPLETE_NOTICE)
        assert out["diagnostics"]["revision_count"] == 1
        calls = [json.loads(c[0]) for c in vertex.exact_calls]
        assert len(calls) == 5 and not any(c["task"] == "compose_verified_claims" for c in calls)
        a1 = next(c for c in calls if c["task"] == "revise_unsupported_claims_once")
        assert a1["missing_answer_point_ids"] == ["point.1"]
        assert len(a1["revisionable_relationships"]) == 1
        assert a1["revisionable_relationships"][0]["relationship_text"] == missing["relationship_text"]
        assert [e["evidence_id"] for e in a1["untrusted_evidence"]] == ["e1"]
        assert blocked["relationship_text"] not in json.dumps(a1)
        assert a1["verification_errors"] == []
        runs.append((out, vertex.exact_calls, runner.retriever.calls))
    assert_neutral(*runs)
    assert event(runs[1][0], "V2_OUTPUT")["payload"]["response"] == after


def test_complete_composer_and_production_payload(tmp_path):
    vertex = RecordingVertex(reviews=[c1_review()], composer_mode="success")
    runner = agent(tmp_path, vertex)
    out = runner.run_detailed(QUESTION)
    assert out["result"]["status"] == "answered"
    assert qa.C1_INCOMPLETE_NOTICE not in out["result"]["answer"]
    assert len(vertex.exact_calls) == 5 and runner.retriever.calls == 1
    payload, schema, kw = next((json.loads(p), s, k) for p,s,k in vertex.exact_calls if json.loads(p)["task"] == "review_claim_support_and_relevance")
    assert payload["untrusted_question"] == QUESTION and payload["admitted_evidence_ids"] == ["e1"]
    assert schema == qa.PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA
    assert out["diagnostics"]["answer_point_audit"]["coverage_satisfaction_schema_version"] == "coverage-satisfaction-v1"


@pytest.mark.parametrize("mode", ["shadow_e1_v2", "runtime_e1_v2"])
def test_historical_mode_payload_schema(tmp_path, mode):
    runner = agent(tmp_path, RecordingVertex())
    out = runner._run_detailed(QUESTION, mode=mode)
    p,s,_ = next((json.loads(p), s, k) for p,s,k in runner.vertex.exact_calls if json.loads(p)["task"] == "review_claim_support_and_relevance")
    assert "untrusted_question" not in p and "admitted_evidence_ids" not in p
    assert s == qa.ANSWER_POINT_COVERAGE_REVIEW_SCHEMA
    assert out["result"]["status"] == "answered"


def test_fingerprint_binds_production_prompts_schema_and_version(monkeypatch):
    from panda_agent import evaluation_runner as er, prompts
    before = "0a5b2909ef586671d533148979fc681c64e37528ad53781a4566cb9044835ba2"
    value = er.prompt_fingerprint()
    assert value != before and value == er.prompt_fingerprint()
    assert prompts.PROMPT_SET_VERSION == "3.11.2"
    for name in ("PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SYSTEM_PROMPT",
                 "PRODUCTION_COVERAGE_SATISFACTION_REVISION_SYSTEM_PROMPT", "COVERAGE_SATISFACTION_SCHEMA_VERSION"):
        with monkeypatch.context() as patch:
            patch.setattr(er, name, getattr(er, name) + " changed")
            assert er.prompt_fingerprint() != value
    with monkeypatch.context() as patch:
        schema = deepcopy(er.PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA)
        schema["properties"]["answer_point_coverage"]["maxItems"] = 4
        patch.setattr(er, "PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA", schema)
        assert er.prompt_fingerprint() != value


@pytest.mark.parametrize("kind", ["admitted", "empty", "unknown", "uncitable", "wrong_version"])
def test_unsupported_claim_recovery_requires_safe_admitted_citations(tmp_path, kind):
    runner = agent(tmp_path)
    c = claim()
    if kind == "empty": c["evidence_ids"] = []
    if kind == "unknown": c["evidence_ids"] = ["unknown"]
    if kind == "uncitable":
        runner.retriever.bundle["evidence"][0].update(source_id="synthetic_sphinx", locator={"section_path": []})
    if kind == "wrong_version": runner.retriever.bundle["evidence"][0]["source_version_id"] = "pandaroot@wrong"
    valid = kind == "admitted"
    points = [point(p["answer_point_id"], [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE") for p in POINTS]
    value = c1_review(points, {"c1": []} if valid else {}, unsupported=["c1"] if valid else [])
    vertex = RecordingVertex(reviews=[value], revisions=[claim(text="The input accepts a record.")])
    runner.generation_vertex = runner.verification_vertex = runner.vertex = vertex
    s = state(runner, [c]); s["answer_point_coverage_mode"] = qa.DEFAULT_ANSWER_POINT_MODE
    s.update(runner._verify(s))
    assert s["revisionable_unsupported_claim_ids"] == (["c1"] if valid else [])
    assert runner._after_verify_route(s) == ("revise" if valid else "finalize")
    if valid:
        s.update(runner._revise(s))
        payload = json.loads(vertex.exact_calls[-1][0])
        assert payload["revisionable_unsupported_claim_ids"] == ["c1"]
        assert [e["evidence_id"] for e in payload["untrusted_evidence"]] == ["e1"]
        assert runner._after_verify_route(s) == "finalize"


def test_empty_invalid_review_no_placeholder(tmp_path):
    vertex = RecordingVertex(answers=[], reviews=[{}])
    out = agent(tmp_path, vertex).run_detailed(QUESTION)
    assert out["result"]["status"] == "insufficient_evidence"
    assert out["result"]["claims"] == [] and out["result"]["evidence"] == []
    assert out["result"]["answer"] == qa.C1_INCOMPLETE_NOTICE
    assert len(vertex.exact_calls) == 3


@pytest.mark.parametrize("error", ["exact future runtime outcome or checksum cannot be established",
    "open-domain universal proof is unsupported", "unsupported requested symbol: UnknownSymbol",
    "unsupported requested API symbol: Unknown::call"])
def test_hard_guard_precedes_c1_partial_policy(tmp_path, error):
    runner = agent(tmp_path)
    s = state(runner, [claim()])
    s.update(answer_point_coverage_mode=qa.DEFAULT_ANSWER_POINT_MODE, sufficient=False,
             coverage_blocked=True, supported_claims=[claim()], errors=[error])
    out = runner._finalize(s)["result"]
    assert out["status"] == "insufficient_evidence" and qa.C1_INCOMPLETE_NOTICE not in out["answer"]
    s["bundle"]["plan"]["version_conflicts"] = ["version conflict"]
    assert runner._finalize(s)["result"]["status"] == "version_conflict"


def test_twenty_checks_and_twenty_one_rejected(tmp_path):
    claims, evidence = fixture(tmp_path)
    c = claims[0]
    ids = {f"point.{i}" for i in range(5)}
    c["answer_point_ids"] = sorted(ids)
    records = []
    for pid in sorted(ids):
        checks = [{**check(), "relationship_text": f"Necessary assertion {i}"} for i in range(4)]
        records.append(point(pid, checks))
    value = c1_review(records, {"c1": sorted(ids)})
    assert qa._validate_coverage_satisfaction(value, [c], ids, set(), evidence, {"e1"})
    records[0]["relationship_checks"].append({**check(), "relationship_text": "Twenty-first assertion"})
    with pytest.raises(ValueError):
        qa._validate_coverage_satisfaction(value, [c], ids, set(), evidence, {"e1"})


def test_supporter_and_string_boundaries(tmp_path):
    _, evidence = fixture(tmp_path)
    evidence["e1"]["text"] = "x" * 400
    claims = [claim(f"c{i}") for i in range(32)]
    checks = []
    for i in range(4):
        c = check("x" * 400, [claim["claim_id"] for claim in claims[i*8:i*8+8]])
        c.update(relationship_text=str(i) + "r" * 239, necessity_reason="n" * 160)
        checks.append(c)
    p = point("point.1", checks)
    value = c1_review([p], {c["claim_id"]: ["point.1"] for c in claims})
    assert qa._validate_coverage_satisfaction(value, claims, {"point.1"}, set(), evidence, {"e1"})


@pytest.mark.parametrize("text", ["A occurs before X and X occurs before B.", "Cedar is implemented in the module.",
                                  "Cedar means a record processor.", "Cedar exists to transform records."])
def test_generic_relationship_shapes_and_topical_gap(tmp_path, text):
    runner = agent(tmp_path)
    runner.retriever.bundle["evidence"][0]["text"] = text
    # Scripted semantic judgment: mentioning the subject is not the relationship.
    c = claim(text="Cedar is discussed.")
    value = c1_review([point("point.1", [check(text, [])]),
                       point("point.2", [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE")], {"c1": ["point.1"]})
    runner.verification_vertex = RecordingVertex(reviews=[value])
    s = state(runner, [c]); s["answer_point_coverage_mode"] = qa.DEFAULT_ANSWER_POINT_MODE
    out = runner._verify(s)
    assert out["coverage_blocked"] and len(out["revisionable_relationships"]) == 1
    assert "point.1" in out["missing_answer_point_ids"]


def test_recovered_complete_path_keeps_seven_call_ceiling(tmp_path):
    first = c1_review([point("point.1", [check()]),
                       point("point.2", [check("The output is a table.", [])])], {"c1": ["point.1"]})
    vertex = RecordingVertex(answers=[claim()], reviews=[first, c1_review()],
        revisions=[claim("c2", "point.2", "The output is a table.")], composer_mode="success")
    runner = agent(tmp_path, vertex)
    out = runner.run_detailed(QUESTION)
    assert out["result"]["status"] == "answered"
    assert out["diagnostics"]["revision_count"] == 1 and len(vertex.exact_calls) == 7
    assert runner.retriever.calls == 1 and out["model_usage"]["embedding_calls"] == 0


def test_visible_only_gap_alone_never_invokes_revision(tmp_path):
    blocked = check("The input is a record.", [], "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING", "page")
    value = c1_review([point("point.1", [blocked]), point("point.2", [check("The output is a table.", ["c2"])])])
    runner = agent(tmp_path, RecordingVertex(reviews=[value]))
    visible = deepcopy(runner.retriever.bundle["evidence"][0])
    visible.update(evidence_id="page", object_id="page", source_id="synthetic_sphinx", locator={"section_path": []})
    runner.retriever.bundle["evidence"].append(visible)
    out = runner.run_detailed(QUESTION)
    assert out["diagnostics"]["revision_count"] == 0
    assert out["result"]["status"] == "insufficient_evidence"
    assert len(runner.vertex.exact_calls) == 3


def test_invalid_global_support_verdict_cannot_salvage_claims(tmp_path):
    value = c1_review()
    value["supported"] = False
    value["answer_point_coverage"][0]["relationship_checks"] = []
    out = agent(tmp_path, RecordingVertex(reviews=[value])).run_detailed(QUESTION)
    assert out["result"]["claims"] == [] and out["diagnostics"]["revision_count"] == 0


@pytest.mark.parametrize("verified,mixed,expected", [([], False, []), (["point.2"], False, ["point.2"]),
    (["point.2"], True, ["point.1", "point.2"]), (["point.1"], True, ["point.1"])])
def test_r1_verified_unsupported_mapping_owns_recovery(tmp_path, verified, mixed, expected):
    records = [point(p["answer_point_id"], [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE") for p in POINTS]
    if mixed:
        records[0] = point("point.1", [check(supporters=[])])
    vertex = RecordingVertex(reviews=[c1_review(records, {"c1": verified}, unsupported=["c1"])], revisions=[])
    runner = agent(tmp_path, vertex)
    s = state(runner, [claim()])
    s["answer_point_coverage_mode"] = qa.DEFAULT_ANSWER_POINT_MODE
    original = deepcopy(s["draft"])
    s.update(runner._verify(s))
    assert s["revisionable_unsupported_claim_ids"] == ["c1"]
    assert runner._after_verify_route(s) == "revise"
    update = runner._revise(s)
    payload = json.loads(vertex.exact_calls[-1][0])
    assert payload["revisionable_answer_point_ids"] == expected
    assert [p["answer_point_id"] for p in payload["runtime_answer_points"]] == expected
    assert payload["untrusted_draft"]["claims"][0]["answer_point_ids"] == verified
    assert s["draft"] == original
    assert payload["revisionable_unsupported_claim_ids"] == ["c1"]
    assert [e["evidence_id"] for e in payload["untrusted_evidence"]] == ["e1"]
    s.update(update)
    assert runner._after_verify_route(s) == "finalize"


def test_r1_partial_rendered_audit_uses_public_claims(tmp_path):
    records = [point(p["answer_point_id"], [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE") for p in POINTS]
    vertex = RecordingVertex(reviews=[c1_review(records, {"c1": ["point.1"], "c2": []}, irrelevant=["c2"])])
    out = agent(tmp_path, vertex).run_detailed(QUESTION)
    assert out["result"]["status"] == "insufficient_evidence"
    assert [c["claim_id"] for c in out["result"]["claims"]] == ["c1"]
    assert "The input is a record." in out["result"]["answer"]
    audit = {m["claim_id"]: m["rendered"] for m in out["diagnostics"]["answer_point_audit"]["claim_mappings"]}
    assert audit == {"c1": True, "c2": False}


@pytest.mark.parametrize("scope", ["ESTABLISHED", "OVERFLOW"])
def test_r1_uncertain_check_requires_uncertain_scope(tmp_path, scope):
    uncertain = check(supporters=[], admitted="INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE")
    value = c1_review([point("point.1", [uncertain], scope),
                       point("point.2", [], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE")])
    with pytest.raises(ValueError, match="uncertain check requires uncertain scope"):
        validate(tmp_path, value)


def test_r1_uncertain_and_visible_only_remain_distinct(tmp_path):
    uncertain = check(supporters=[], admitted="INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE")
    value = c1_review([point("point.1", [uncertain], "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE"),
                       point("point.2", [], "OVERFLOW")])
    assert validate(tmp_path, value)
    # Visible-only acceptance/no revision is separately exercised by the existing full-flow test.
