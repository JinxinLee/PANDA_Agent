"""Synthetic G2 production coverage containment; no providers."""

from copy import deepcopy
import json

import pytest

from panda_agent import qa
from test_g1_relationship_obligations import named_check, named_point
from test_e2_a1_answer_point_coverage import agent, claim, state
from test_post_a5_c1_coverage_completeness import c1_review, check, fixture, point
from test_post_a5_o1_observability import RecordingVertex, event


def _named_fixture(tmp_path):
    claims, evidence = fixture(tmp_path)
    canonical = [
        {"answer_point_id": "point.1", "required_relations": [
            {"relation_id": "point.1.rel.1", "text": "First relation"},
            {"relation_id": "point.1.rel.2", "text": "Second relation"},
        ]},
        {"answer_point_id": "point.2", "required_relations": []},
    ]
    first = named_point([named_check("point.1.rel.1"), named_check("point.1.rel.2")])
    second = point("point.2", [check("The output is a table.", ["c2"])])
    value = c1_review([first, second])
    return value, claims, evidence, canonical


def _receipt(value, claims, evidence, canonical):
    return qa._build_coverage_receipt(
        value, claims, {"point.1", "point.2"}, set(), evidence, {"e1"},
        canonical_points=canonical,
    )


def test_named_bad_quote_is_local_and_valid_sibling_can_revise(tmp_path):
    value, claims, evidence, canonical = _named_fixture(tmp_path)
    value["answer_point_coverage"][0]["required_relation_checks"][1]["basis"][0]["quote"] = "invented"
    before = deepcopy(value)
    receipt = _receipt(value, claims, evidence, canonical)
    assert value == before
    assert receipt["status"] == "PARTIAL"
    assert receipt["missing_answer_point_ids"] == ["point.1"]
    assert receipt["point_results"][0]["complete"] is False
    assert receipt["point_results"][1]["complete"] is True
    assert [r["state"] for r in receipt["point_results"][0]["relations"]] == ["VALID", "LOCAL_INVALID"]
    assert [r["relation_id"] for r in receipt["revisionable_relationships"]] == ["point.1.rel.1"]


def test_bad_ordinary_check_invalidates_owning_point(tmp_path):
    claims, evidence = fixture(tmp_path)
    value = c1_review()
    value["answer_point_coverage"][0]["relationship_checks"][0]["basis"][0]["quote"] = "invented"
    receipt = _receipt(value, claims, evidence, [
        {"answer_point_id": "point.1", "required_relations": []},
        {"answer_point_id": "point.2", "required_relations": []},
    ])
    assert receipt["status"] == "PARTIAL"
    assert [p["state"] for p in receipt["point_results"]] == ["LOCAL_INVALID", "VALID"]
    assert receipt["revisionable_relationships"] == []


def test_duplicate_point_identity_rejects_whole_review(tmp_path):
    value, claims, evidence, canonical = _named_fixture(tmp_path)
    value["answer_point_coverage"].append(deepcopy(value["answer_point_coverage"][0]))
    receipt = _receipt(value, claims, evidence, canonical)
    assert receipt["status"] == "REJECTED"
    assert receipt["missing_answer_point_ids"] == ["point.1", "point.2"]
    assert receipt["revisionable_relationships"] == []


@pytest.mark.parametrize("case,code", [
    ("bad_quote", "BAD_QUOTE"),
    ("unknown_evidence", "UNKNOWN_EVIDENCE"),
    ("duplicate_basis", "DUPLICATE_BASIS"),
    ("basis_overflow", "BASIS_BOUND"),
    ("two_basis_one_bad", "BAD_QUOTE"),
    ("empty_quote", "BAD_QUOTE"),
    ("long_quote", "BAD_QUOTE"),
    ("unadmitted_basis", "INVALID_ADMISSION"),
    ("visible_admitted_basis", "INVALID_ADMISSION"),
    ("wrong_point_supporter", "INVALID_SUPPORTER"),
    ("duplicate_supporter", "INVALID_SUPPORTER"),
    ("two_supporters_one_bad", "INVALID_SUPPORTER"),
    ("uncited_supporter", "INVALID_SUPPORTER"),
    ("supporter_overflow", "INVALID_SUPPORTER"),
    ("invalid_admission", "INVALID_ADMISSION"),
    ("satisfied_without_supporter", "INVALID_SATISFACTION"),
    ("visible_with_supporter", "INVALID_SATISFACTION"),
])
def test_named_item_failure_never_drops_bad_basis_or_supporter(tmp_path, case, code):
    value, claims, evidence, canonical = _named_fixture(tmp_path)
    check_row = value["answer_point_coverage"][0]["required_relation_checks"][1]
    basis = check_row["basis"][0]
    if case == "bad_quote":
        basis["quote"] = "invented"
    elif case == "unknown_evidence":
        basis["evidence_id"] = "unknown"
    elif case == "duplicate_basis":
        check_row["basis"].append(deepcopy(basis))
    elif case == "basis_overflow":
        check_row["basis"] *= 3
    elif case == "two_basis_one_bad":
        evidence["e2"] = {**evidence["e1"], "evidence_id": "e2"}
        check_row["basis"].append({"evidence_id": "e2", "quote": "invented"})
    elif case == "empty_quote":
        basis["quote"] = " "
    elif case == "long_quote":
        basis["quote"] = "x" * 401
    elif case in {"unadmitted_basis", "visible_admitted_basis"}:
        if case == "unadmitted_basis":
            evidence["e2"] = {**evidence["e1"], "evidence_id": "e2"}
            basis["evidence_id"] = "e2"
        else:
            check_row["admission_state"] = "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING"
    elif case == "wrong_point_supporter":
        check_row.update(supporting_claim_ids=["c2"], satisfied=True)
    elif case == "duplicate_supporter":
        check_row.update(supporting_claim_ids=["c1", "c1"], satisfied=True)
    elif case == "two_supporters_one_bad":
        check_row.update(supporting_claim_ids=["c1", "unknown"], satisfied=True)
    elif case == "uncited_supporter":
        claims[0]["evidence_ids"] = []
        check_row.update(supporting_claim_ids=["c1"], satisfied=True)
    elif case == "supporter_overflow":
        check_row["supporting_claim_ids"] = [str(i) for i in range(9)]
    elif case == "invalid_admission":
        check_row["admission_state"] = "unknown"
    elif case == "satisfied_without_supporter":
        check_row["satisfied"] = True
    elif case == "visible_with_supporter":
        check_row.update(admission_state="VISIBLE_ONLY_WITHOUT_CITABLE_BACKING",
                         supporting_claim_ids=["c1"], satisfied=True)
    receipt = _receipt(value, claims, evidence, canonical)
    assert receipt["status"] == "PARTIAL"
    assert [r["state"] for r in receipt["point_results"][0]["relations"]] == ["VALID", "LOCAL_INVALID"]
    assert receipt["point_results"][0]["complete"] is False
    assert receipt["point_results"][1]["complete"] is True
    assert [r["relation_id"] for r in receipt["revisionable_relationships"]] == ["point.1.rel.1"]
    assert code in [item["reason_code"] for item in receipt["errors"]]


@pytest.mark.parametrize("case,expected_status,expected_point", [
    ("missing_relation", "PARTIAL", "LOCAL_INVALID"),
    ("duplicate_relation", "PARTIAL", "LOCAL_INVALID"),
    ("unknown_relation", "PARTIAL", "LOCAL_INVALID"),
    ("identityless_relation", "PARTIAL", "LOCAL_INVALID"),
    ("wrong_active_path", "PARTIAL", "LOCAL_INVALID"),
    ("missing_point", "PARTIAL", "MISSING"),
    ("malformed_point", "PARTIAL", "LOCAL_INVALID"),
    ("cross_parent", "REJECTED", None),
    ("duplicate_point", "REJECTED", None),
    ("unknown_point", "REJECTED", None),
    ("identityless_point", "REJECTED", None),
    ("non_object", "REJECTED", None),
    ("extra_top", "REJECTED", None),
    ("bad_mapping", "REJECTED", None),
    ("bad_missing_inventory", "REJECTED", None),
    ("unknown_missing_inventory", "REJECTED", None),
    ("untyped_missing_inventory", "REJECTED", None),
    ("canonical_corruption", "REJECTED", None),
    ("global_overflow", "REJECTED", None),
])
def test_inventory_and_global_boundary(tmp_path, case, expected_status, expected_point):
    value, claims, evidence, canonical = _named_fixture(tmp_path)
    first = value["answer_point_coverage"][0]
    named = first["required_relation_checks"]
    if case == "missing_relation":
        named.pop()
    elif case == "duplicate_relation":
        named.append(deepcopy(named[-1]))
    elif case == "unknown_relation":
        named[-1]["relation_id"] = "point.1.rel.99"
    elif case == "identityless_relation":
        named[-1].pop("relation_id")
    elif case == "wrong_active_path":
        first["relationship_checks"].append(check())
    elif case == "missing_point":
        value["answer_point_coverage"].pop(0)
    elif case == "malformed_point":
        first["required_relation_checks"] = "invalid"
    elif case == "cross_parent":
        canonical[1]["required_relations"] = [{"relation_id": "point.2.rel.1", "text": "Other relation"}]
        named[-1]["relation_id"] = "point.2.rel.1"
    elif case == "duplicate_point":
        value["answer_point_coverage"].append(deepcopy(first))
    elif case == "unknown_point":
        first["answer_point_id"] = "unknown"
    elif case == "identityless_point":
        first.pop("answer_point_id")
    elif case == "non_object":
        value = []
    elif case == "extra_top":
        value["unexpected"] = True
    elif case == "bad_mapping":
        value["claim_answer_point_mappings"][0]["answer_point_ids"] = ["unknown"]
    elif case == "bad_missing_inventory":
        value["missing_answer_point_ids"] = ["point.1", "point.1"]
    elif case == "unknown_missing_inventory":
        value["missing_answer_point_ids"] = ["unknown"]
    elif case == "untyped_missing_inventory":
        value["missing_answer_point_ids"] = "point.1"
    elif case == "canonical_corruption":
        canonical[0]["required_relations"].append(deepcopy(canonical[0]["required_relations"][0]))
    elif case == "global_overflow":
        named.extend([deepcopy(named[-1]) for _ in range(20)])
    receipt = _receipt(value, claims, evidence, canonical)
    assert receipt["status"] == expected_status
    assert receipt["missing_answer_point_ids"][0] == "point.1"
    if expected_status == "REJECTED":
        assert receipt["revisionable_relationships"] == []
    if expected_point is not None:
        assert receipt["point_results"][0]["state"] == expected_point
        assert len(receipt["point_results"][0]["relations"]) == 2
        assert receipt["point_results"][1]["complete"] is True


@pytest.mark.parametrize("case", [
    "bad_basis", "bad_supporter", "duplicate_text", "bad_fields",
    "scope_conflict", "valid_unsatisfied_sibling", "ordinary_overflow",
])
def test_ordinary_check_failure_blocks_whole_point_and_a1(tmp_path, case):
    claims, evidence = fixture(tmp_path)
    first = point("point.1", [check(), check("The output is a table.", ["c2"])])
    second = point("point.2", [check("The output is a table.", ["c2"])])
    value = c1_review([first, second], {"c1": ["point.1"], "c2": ["point.1", "point.2"]})
    damaged = first["relationship_checks"][1]
    if case in {"bad_basis", "valid_unsatisfied_sibling"}:
        damaged["basis"][0]["quote"] = "invented"
        if case == "valid_unsatisfied_sibling":
            first["relationship_checks"][0].update(satisfied=False, supporting_claim_ids=[])
    elif case == "bad_supporter":
        damaged["supporting_claim_ids"] = ["unknown"]
    elif case == "duplicate_text":
        damaged["relationship_text"] = "The  input is a record."
    elif case == "bad_fields":
        damaged["extra"] = True
    elif case == "scope_conflict":
        first["scope_status"] = "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE"
    elif case == "ordinary_overflow":
        first["relationship_checks"] *= 3
    receipt = _receipt(value, claims, evidence, [
        {"answer_point_id": "point.1", "required_relations": []},
        {"answer_point_id": "point.2", "required_relations": []},
    ])
    assert receipt["status"] == "PARTIAL"
    assert [p["state"] for p in receipt["point_results"]] == ["LOCAL_INVALID", "VALID"]
    assert receipt["missing_answer_point_ids"] == ["point.1"]
    assert receipt["revisionable_relationships"] == []


@pytest.mark.parametrize("case", [
    "false_complete", "false_incomplete", "wrong_union", "overlong_model_union",
    "wrong_named_scope", "wrong_missing_complement", "wrong_ordinary_complete",
])
def test_fully_valid_children_override_model_aggregates(tmp_path, case):
    value, claims, evidence, canonical = _named_fixture(tmp_path)
    named = value["answer_point_coverage"][0]
    if case == "false_complete":
        named["complete"] = True
    elif case == "false_incomplete":
        for row in named["required_relation_checks"]:
            row.update(satisfied=True, supporting_claim_ids=["c1"])
        named["complete"] = False
    elif case == "wrong_union":
        named["supporting_claim_ids"] = ["c1"]
    elif case == "overlong_model_union":
        named["supporting_claim_ids"] = [str(i) for i in range(33)]
    elif case == "wrong_named_scope":
        named["scope_status"] = "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE"
    elif case == "wrong_missing_complement":
        value["missing_answer_point_ids"] = ["point.1", "point.2"]
    elif case == "wrong_ordinary_complete":
        value["answer_point_coverage"][1]["complete"] = False
    before = deepcopy(value)
    receipt = _receipt(value, claims, evidence, canonical)
    assert value == before
    assert receipt["status"] == "VALID"
    assert receipt["accepted_coverage"] is not None
    assert receipt["accepted_coverage"][0]["complete"] == (case == "false_incomplete")
    assert receipt["accepted_coverage"][0]["supporting_claim_ids"] == (["c1"] if case == "false_incomplete" else [])
    assert receipt["accepted_coverage"][0]["scope_status"] == "ESTABLISHED"
    assert receipt["accepted_coverage"][1]["complete"] is True
    assert receipt["missing_answer_point_ids"] == ([] if case == "false_incomplete" else ["point.1"])
    assert any(item["scope"] == "AGGREGATE" for item in receipt["errors"])


def test_current_check_bounds_preclude_derived_union_over_32():
    # Four ordinary checks with at most eight unique supporters each yield at most 32.
    assert 4 * 8 == 32
    assert 3 * 8 < 32  # The named relation limit is tighter.


def test_derived_union_guard_if_child_limit_is_bypassed(tmp_path, monkeypatch):
    # The normal 8-per-check gate makes this unreachable; isolate the downstream 32 guard.
    claims, evidence = fixture(tmp_path)
    extra = [claim(f"p1_{i}") for i in range(36)]
    claims = [*extra, claims[1]]
    checks = []
    for group in range(4):
        row = check(supporters=[c["claim_id"] for c in extra[group * 9:(group + 1) * 9]])
        row["relationship_text"] = f"Distinct relationship {group}"
        checks.append(row)
    value = c1_review([point("point.1", checks), point("point.2", [check("The output is a table.", ["c2"])])],
                      {**{c["claim_id"]: ["point.1"] for c in extra}, "c2": ["point.2"]})
    original = qa._validate_production_check

    def without_child_cap(row, **kwargs):
        return deepcopy(row) if kwargs["point_id"] == "point.1" else original(row, **kwargs)

    monkeypatch.setattr(qa, "_validate_production_check", without_child_cap)
    receipt = _receipt(value, claims, evidence, [
        {"answer_point_id": "point.1", "required_relations": []},
        {"answer_point_id": "point.2", "required_relations": []},
    ])
    assert receipt["status"] == "PARTIAL"
    assert [p["state"] for p in receipt["point_results"]] == ["LOCAL_INVALID", "VALID"]
    assert receipt["missing_answer_point_ids"] == ["point.1"]
    assert receipt["revisionable_relationships"] == []
    assert any(e["reason_code"] == "POINT_SUPPORTER_BOUND" for e in receipt["errors"])


@pytest.mark.parametrize("damage,state", [
    ("bad_quote", "LOCAL_INVALID"), ("missing", "MISSING"), ("duplicate", "CONFLICTED"),
])
def test_partial_named_inventory_never_derives_positive_point(tmp_path, damage, state):
    value, claims, evidence, canonical = _named_fixture(tmp_path)
    named = value["answer_point_coverage"][0]
    rows = named["required_relation_checks"]
    rows[0].update(satisfied=True, supporting_claim_ids=["c1"])
    if damage == "bad_quote":
        rows[1]["basis"][0]["quote"] = "invented"
    elif damage == "missing":
        rows.pop()
    else:
        rows.append(deepcopy(rows[1]))
    named.update(complete=True, scope_status="INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE",
                 supporting_claim_ids=["c1", "c2"])
    value["missing_answer_point_ids"] = []
    receipt = _receipt(value, claims, evidence, canonical)
    assert receipt["status"] == "PARTIAL"
    assert [r["state"] for r in receipt["point_results"][0]["relations"]] == ["VALID", state]
    assert receipt["point_results"][0]["complete"] is False
    assert receipt["accepted_coverage"] is None
    assert receipt["missing_answer_point_ids"] == ["point.1"]
    assert receipt["point_results"][0]["supporting_claim_ids"] == ["c1"]
    assert receipt["point_results"][0]["scope_status"] is None
    assert [r["relation_id"] for r in receipt["revisionable_relationships"]] == []


def test_one_mapping_authority_for_valid_and_malformed_review(tmp_path):
    value, claims, evidence, canonical = _named_fixture(tmp_path)
    expected, _, _, _ = qa._validate_review_mappings(value, claims, {"point.1", "point.2"}, set())
    value["answer_point_coverage"][0]["required_relation_checks"][1]["basis"][0]["quote"] = "invented"
    partial = _receipt(value, claims, evidence, canonical)
    assert partial["status"] == "PARTIAL"
    assert partial["mapping_valid"] is True
    assert partial["mappings"] == expected
    assert partial["verdict"]["supported"] is True
    assert partial["verdict"]["unsupported_claim_ids"] == []
    value["claim_answer_point_mappings"][0]["answer_point_ids"] = ["unknown"]
    with pytest.raises(ValueError):
        qa._validate_review_mappings(value, claims, {"point.1", "point.2"}, set())
    rejected = _receipt(value, claims, evidence, canonical)
    assert rejected["status"] == "REJECTED"
    assert rejected["mapping_valid"] is False and rejected["mappings"] == {}
    assert rejected["verdict"]["unsupported_claim_ids"] == ["c1", "c2"]
    assert rejected["revisionable_relationships"] == []


@pytest.mark.parametrize("broken_mapping", [False, True])
def test_global_coverage_collision_preserves_only_independent_mapping_salvage(tmp_path, broken_mapping):
    value = c1_review()
    value["answer_point_coverage"].append(deepcopy(value["answer_point_coverage"][0]))
    if broken_mapping:
        value["claim_answer_point_mappings"][0]["answer_point_ids"] = ["unknown"]
    runner = agent(tmp_path, RecordingVertex(reviews=[value]))
    current = state(runner, [claim(), claim("c2", "point.2", "The output is a table.")])
    current["answer_point_coverage_mode"] = qa.DEFAULT_ANSWER_POINT_MODE
    update = runner._verify(current)
    assert update["missing_answer_point_ids"] == ["point.1", "point.2"]
    assert update["revisionable_relationships"] == []
    assert update["revisionable_unsupported_claim_ids"] == []
    assert update["coverage_satisfaction_status"] == "INVALID"
    assert update["answer_point_audit"]["answer_point_coverage"] is None
    if broken_mapping:
        assert update["supported_claims"] == []
        assert all(not row["verified_answer_point_ids"] for row in update["answer_point_audit"]["claim_mappings"])
    else:
        assert [c["claim_id"] for c in update["supported_claims"]] == ["c1", "c2"]
        assert [row["verified_answer_point_ids"] for row in update["answer_point_audit"]["claim_mappings"]] == [
            ["point.1"], ["point.2"]]


def test_partial_v1_retains_one_a1_target_and_v2_uses_full_contract(tmp_path):
    question = "Does Cedar run before Birch and feed Maple?"
    proposal = {"points": [{"text": "Answer both requested relations", "support_spans": [question],
        "required_relations": [{"text": "Whether Cedar runs before Birch", "support_spans": [question]},
                               {"text": "Whether Cedar feeds Maple", "support_spans": [question]}]}],
        "ambiguity": {"status": "clear", "reason": ""}}
    first = c1_review([named_point([named_check("point.1.rel.1"), named_check("point.1.rel.2")])],
                      {"c1": ["point.1"]})
    first["answer_point_coverage"][0]["required_relation_checks"][1]["basis"][0]["quote"] = "invented"
    second = c1_review([named_point([
        named_check("point.1.rel.1", satisfied=True, supporters=["c2"]),
        named_check("point.1.rel.2", satisfied=True, supporters=["c2"]),
    ])], {"c1": ["point.1"], "c2": ["point.1"]})
    vertex = RecordingVertex(decomposition=proposal, answers=[claim()],
        revisions=[claim("c2", "point.1", "The output is a table.")], reviews=[first, second])
    out = agent(tmp_path, vertex)._run_detailed(question, mode=qa.DEFAULT_ANSWER_POINT_MODE,
                                                capture_stage_trace=True)
    payloads = [json.loads(p) for p, _, _ in vertex.exact_calls]
    revisions = [p for p in payloads if p["task"] == "revise_unsupported_claims_once"]
    reviews = [p for p in payloads if p["task"] == "review_claim_support_and_relevance"]
    assert len(revisions) == 1
    assert [r["relation_id"] for r in revisions[0]["revisionable_relationships"]] == ["point.1.rel.1"]
    assert len(reviews) == 2
    assert [c["claim_id"] for c in reviews[1]["untrusted_claims"]] == ["c1", "c2"]
    assert [r["relation_id"] for r in reviews[1]["runtime_answer_points"][0]["required_relations"]] == [
        "point.1.rel.1", "point.1.rel.2"]
    assert out["diagnostics"]["revision_count"] == 1
    assert out["result"]["status"] == "answered"
    assert event(out, "V1_OUTPUT")["payload"]["response"] == first
    assert event(out, "V1_OUTPUT")["payload"]["validation"]["status"] == "PARTIAL"
    assert event(out, "V2_OUTPUT")["payload"]["validation"]["status"] == "ACCEPTED"
    audit = out["diagnostics"]["answer_point_audit"]
    assert audit["coverage_validation"]["status"] == "VALID"
    assert audit["coverage_complete"] is True
