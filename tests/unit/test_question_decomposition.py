"""Synthetic T0 contracts; fake proposals do not measure semantic quality."""

import copy
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from panda_agent.qa import QAAgent, _runtime_answer_points
from panda_agent.question_decomposition import (
    QUESTION_DECOMPOSITION_SCHEMA,
    QuestionDecomposer,
)
from test_qa import FakeRetriever, FakeVertex, bundle_for, code_evidence


def point(facet="mechanism", text="How X works", spans=None):
    return {"facet_type": facet, "text": text, "support_spans": spans or ["How does X work?"]}


def proposal(*points):
    return {"points": list(points), "ambiguity": {"status": "clear", "reason": ""}}


class ProposalVertex:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def generate_json(self, prompt, schema, **kwargs):
        self.calls.append((json.loads(prompt), schema, kwargs))
        return copy.deepcopy(self.response)


def decompose(question, response):
    return QuestionDecomposer(ProposalVertex(response)).decompose(question)


def test_one_facet_and_question_only_qa_seam():
    question = "How does X work?"
    vertex = ProposalVertex(proposal(point()))
    agent = QAAgent(Path.cwd(), vertex=vertex, retriever=FakeRetriever({}))
    result = agent.decompose_question(question)
    assert result == {
        "schema_version": "e1.question_decomposition.v1",
        "mode": "shadow_diagnostic",
        "points": [{**point(), "answer_point_id": "mechanism.1"}],
        "ambiguity": {"status": "clear", "reason": ""},
    }
    assert len(vertex.calls) == 1
    payload, schema, _ = vertex.calls[0]
    assert payload == {"task": "decompose_user_question", "untrusted_question": question}
    assert schema is QUESTION_DECOMPOSITION_SCHEMA
    assert schema["properties"]["points"]["minItems"] == 1
    assert schema["properties"]["points"]["maxItems"] == 5
    assert "answer_point_id" not in schema["$defs"]["_Point"]["properties"]


def test_multi_part_order_and_ids():
    question = "Where is X defined and why is it needed?"
    locator = point("locator", "Where X is defined", ["Where is X defined"])
    reason = point("cause_reason", "Why X is needed", ["why is it needed"])
    first = decompose(question, proposal(locator, reason))
    assert first == decompose(question, proposal(reason, locator))
    assert [p["answer_point_id"] for p in first["points"]] == ["locator.1", "cause_reason.1"]


def test_same_facet_ordinals_and_tie_break_are_model_order_independent():
    question = "Where are X and Y defined?"
    x = point("locator", "Locate X", [question, "X", "X"])
    y = point("locator", "Locate Y", [question])
    result = decompose(question, proposal(y, x))
    assert result == decompose(question, proposal(x, y))
    assert [p["answer_point_id"] for p in result["points"]] == ["locator.1", "locator.2"]
    assert result["points"][0]["support_spans"] == [question, "X"]


def test_duplicate_normalized_text_rejected():
    with pytest.raises(ValueError, match="unique"):
        decompose("How does X work?", proposal(point(), point(text=" HOW   X works ")))


@pytest.mark.parametrize("spans", [["missing"], ["How", "missing"], [""], [" "], []])
def test_invalid_support_rejected(spans):
    raw = point()
    raw["support_spans"] = spans
    with pytest.raises(ValueError):
        decompose("How does X work?", proposal(raw))


@pytest.mark.parametrize("count", [0, 6])
def test_point_count_bounds_even_without_provider_schema_enforcement(count):
    with pytest.raises(ValueError):
        decompose("How does X work?", proposal(*(point(text=f"Facet {i}") for i in range(count))))


@pytest.mark.parametrize("field,value", [("facet_type", "workflow_order"), ("text", " "), ("text", 42), ("answer_point_id", "model.1")])
def test_invalid_point_contract_rejected(field, value):
    raw = point()
    raw[field] = value
    with pytest.raises(ValueError):
        decompose("How does X work?", proposal(raw))


def test_five_points_and_diagnostic_ambiguity():
    question = "Define A, B, C, D and E."
    raw = proposal(*(point("definition", f"Define {name}", [name]) for name in "ABCDE"))
    raw["ambiguity"] = {"status": "ambiguous", "reason": "The referents are unspecified."}
    result = decompose(question, raw)
    assert len(result["points"]) == 5
    assert len({p["answer_point_id"] for p in result["points"]}) == 5
    assert result["ambiguity"] == raw["ambiguity"]
    raw["ambiguity"]["status"] = "clarification_required"
    with pytest.raises(ValueError):
        decompose(question, raw)


@pytest.mark.parametrize("entry", ["run", "run_detailed"])
def test_normal_qa_never_invokes_decomposer(entry):
    class CapturingVertex(FakeVertex):
        def __init__(self):
            self.calls = 0

        def generate_json(self, prompt, schema, **kwargs):
            assert schema is not QUESTION_DECOMPOSITION_SCHEMA
            self.calls += 1
            response = super().generate_json(prompt, schema, **kwargs)
            if "claims" in response:
                response["claims"][0]["claim_text"] = "X is defined in src/X.h."
            return response

    # Reuse the existing bounded QA seam with synthetic evidence and question.
    evidence = code_evidence(text="class X {};", path="src/X.h")
    vertex = CapturingVertex()
    agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle_for(evidence)), vertex=vertex)
    with patch.object(QuestionDecomposer, "decompose", side_effect=AssertionError("unexpected decomposition")):
        result = getattr(agent, entry)("Where is X defined?")
    assert (result.status if entry == "run" else result["result"]["status"]) == "answered"
    assert vertex.calls == 2  # Existing answer and review calls only, both fake.


def test_legacy_question_core_unchanged():
    question = "Where is X defined and why is it needed?"
    assert _runtime_answer_points(question) == [{"answer_point_id": "question_core", "text": question}]
