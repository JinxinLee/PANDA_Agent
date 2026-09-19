"""Generic production answer-obligation contracts with fake model doubles only."""

import json

from panda_agent import qa
from test_e2_a1_answer_point_coverage import POINTS, QUESTION, Vertex, agent, claim, review


PRODUCTION_MODE = "production_answer_obligations_v1"


def one_point(text: str, span: str) -> dict:
    return {
        "points": [{"text": text, "support_spans": [span]}],
        "ambiguity": {"status": "clear", "reason": ""},
    }


def one_point_records(text: str) -> list:
    return [{"answer_point_id": "point.1", "text": text}]


def two_point_proposal() -> dict:
    return {
        "points": [
            {"text": POINTS[0]["text"], "support_spans": ["input"]},
            {"text": POINTS[1]["text"], "support_spans": ["output"]},
        ],
        "ambiguity": {"status": "clear", "reason": ""},
    }


def test_t1_default_two_obligations_detects_and_repairs_missing_supported_part(tmp_path):
    vertex = Vertex(
        answers=[claim()],
        reviews=[
            review({"c1": ["point.1"]}, missing=["point.2"]),
            review({"c1": ["point.1"], "c2": ["point.2"]}),
        ],
        revisions=[claim("c2", "point.2", "The output is a table.")],
        decomposition=two_point_proposal(),
    )
    runner = agent(tmp_path, vertex)

    out = runner.run_detailed(QUESTION)

    assert qa.DEFAULT_ANSWER_POINT_MODE == PRODUCTION_MODE
    assert out["diagnostics"]["question_decomposition"]["mode"] == "production_authoritative"
    assert out["diagnostics"]["answer_point_audit"]["mode"] == PRODUCTION_MODE
    assert out["diagnostics"]["answer_point_audit"]["coverage_complete"] is True
    assert out["diagnostics"]["revision_count"] == 1
    assert {item["claim_id"] for item in out["result"]["claims"]} == {"c1", "c2"}
    assert "e3_trace" not in out["diagnostics"]
    assert runner.retriever.calls == 1


def test_t2_unsupported_second_obligation_is_not_invented(tmp_path):
    vertex = Vertex(
        answers=[claim()],
        reviews=[
            review({"c1": ["point.1"]}, missing=["point.2"]),
            review({"c1": ["point.1"]}, missing=["point.2"]),
        ],
        revisions=[],
        decomposition=two_point_proposal(),
    )

    out = agent(tmp_path, vertex).run_detailed(QUESTION)

    assert [item["claim_id"] for item in out["result"]["claims"]] == ["c1"]
    assert out["diagnostics"]["answer_point_audit"]["coverage_complete"] is False
    assert out["diagnostics"]["answer_point_audit"]["missing_answer_point_ids"] == ["point.2"]


def test_t3_single_obligation_stays_single_and_adds_no_revision_burden(tmp_path):
    question = "How does Cedar work?"
    vertex = Vertex(
        answers=[claim(point="point.1", text="Cedar processes a record.")],
        reviews=[review({"c1": ["point.1"]}, points=one_point_records("Explain how Cedar works"))],
        decomposition=one_point("Explain how Cedar works", question),
    )

    out = agent(tmp_path, vertex).run_detailed(question)

    assert len(out["diagnostics"]["question_decomposition"]["points"]) == 1
    assert out["diagnostics"]["revision_count"] == 0
    assert out["diagnostics"]["answer_point_audit"]["coverage_complete"] is True


def test_t4_comparison_remains_one_obligation(tmp_path):
    question = "How do Cedar and Birch differ?"
    vertex = Vertex(
        answers=[claim(point="point.1", text="Cedar and Birch use different record layouts.")],
        reviews=[review({"c1": ["point.1"]}, points=one_point_records("Compare Cedar and Birch"))],
        decomposition=one_point("Compare Cedar and Birch", question),
    )

    out = agent(tmp_path, vertex).run_detailed(question)

    assert [p["text"] for p in out["diagnostics"]["question_decomposition"]["points"]] == [
        "Compare Cedar and Birch"
    ]
    assert out["diagnostics"]["answer_point_audit"]["coverage_complete"] is True


def test_t5_respectively_preserves_two_explicit_targets(tmp_path):
    question = "Where are Cedar and Birch implemented respectively?"
    decomposition = {
        "points": [
            {"text": "Locate Cedar", "support_spans": ["Cedar"]},
            {"text": "Locate Birch", "support_spans": ["Birch"]},
        ],
        "ambiguity": {"status": "clear", "reason": ""},
    }
    vertex = Vertex(
        answers=[claim(), claim("c2", "point.2", "Birch is in the same evidence.")],
        reviews=[review({"c1": ["point.1"], "c2": ["point.2"]})],
        decomposition=decomposition,
    )

    out = agent(tmp_path, vertex).run_detailed(question)

    assert [p["answer_point_id"] for p in out["diagnostics"]["question_decomposition"]["points"]] == [
        "point.1",
        "point.2",
    ]


def test_t6_workflow_does_not_invent_substeps(tmp_path):
    question = "Describe the workflow from Cedar to Birch."
    vertex = Vertex(
        answers=[claim(point="point.1", text="The workflow carries a record from Cedar to Birch.")],
        reviews=[review({"c1": ["point.1"]}, points=one_point_records("Describe the workflow from Cedar to Birch"))],
        decomposition=one_point("Describe the workflow from Cedar to Birch", question),
    )

    out = agent(tmp_path, vertex).run_detailed(question)

    assert len(out["diagnostics"]["question_decomposition"]["points"]) == 1
    assert out["diagnostics"]["revision_count"] == 0


def test_t7_unsupported_claim_is_rejected_then_narrower_supported_claim_recovers(tmp_path):
    vertex = Vertex(
        answers=[claim(), claim("c2", "point.2", "The output always has every field.")],
        reviews=[
            review({"c1": ["point.1"], "c2": []}, missing=["point.2"], unsupported=["c2"]),
            review({"c1": ["point.1"], "c3": ["point.2"]}),
        ],
        revisions=[claim("c3", "point.2", "The evidence describes the output as a table.")],
        decomposition=two_point_proposal(),
    )

    out = agent(tmp_path, vertex).run_detailed(QUESTION)

    assert {item["claim_id"] for item in out["result"]["claims"]} == {"c1", "c3"}
    assert "c2" not in json.dumps(out["result"])
    assert out["diagnostics"]["answer_point_audit"]["coverage_complete"] is True


def test_t8_unsupported_claim_without_recovery_is_removed(tmp_path):
    vertex = Vertex(
        answers=[claim(), claim("c2", "point.2", "The output always has every field.")],
        reviews=[
            review({"c1": ["point.1"], "c2": []}, missing=["point.2"], unsupported=["c2"]),
            review({"c1": ["point.1"]}, missing=["point.2"]),
        ],
        revisions=[],
        decomposition=two_point_proposal(),
    )

    out = agent(tmp_path, vertex).run_detailed(QUESTION)

    assert [item["claim_id"] for item in out["result"]["claims"]] == ["c1"]
    assert out["diagnostics"]["answer_point_audit"]["coverage_complete"] is False


def test_t9_legacy_requirements_have_no_model_authority_in_production_mode(tmp_path):
    vertex = Vertex(
        answers=[claim()],
        reviews=[
            review({"c1": ["point.1"]}, missing=["point.2"]),
            review({"c1": ["point.1"], "c2": ["point.2"]}),
        ],
        revisions=[claim("c2", "point.2", "The output is a table.")],
        decomposition=two_point_proposal(),
    )

    out = agent(tmp_path, vertex).run_detailed(QUESTION)
    payloads = [payload for payload, _, _ in vertex.calls if payload["task"] != "decompose_user_question"]

    authority_payloads = [payload for payload in payloads if "answer_requirements" in payload]
    assert {payload["task"] for payload in authority_payloads} == {
        "create_atomic_evidence_bound_claims",
        "review_claim_support_and_relevance",
        "revise_unsupported_claims_once",
    }
    assert all(payload["answer_requirements"] == [] for payload in authority_payloads)
    assert all(payload.get("requirement_evidence", {}) == {} for payload in payloads)
    assert out["diagnostics"]["answer_point_audit"]["coverage_complete"] is True


def test_t10_internal_coverage_bookkeeping_never_becomes_public_text(tmp_path):
    internal = claim("required_workflow", "point.2", "Coverage point.2 is missing.")
    vertex = Vertex(
        answers=[claim(), internal],
        reviews=[review({"c1": ["point.1"]}, missing=["point.2"]), review({"c1": ["point.1"]}, missing=["point.2"])],
        revisions=[],
        decomposition=two_point_proposal(),
    )

    out = agent(tmp_path, vertex).run_detailed(QUESTION)

    assert [item["claim_id"] for item in out["result"]["claims"]] == ["c1"]
    assert "point.2" not in out["result"]["answer"]
    review_payloads = [p for p, _, _ in vertex.calls if p["task"] == "review_claim_support_and_relevance"]
    assert all(all(c["claim_id"] != "internal" for c in p["untrusted_claims"]) for p in review_payloads)
