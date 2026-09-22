"""Synthetic T0 contracts; fake proposals do not measure semantic quality."""

import copy
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from panda_agent.qa import QAAgent, _runtime_answer_points
from panda_agent.question_decomposition import (
    QUESTION_DECOMPOSITION_V2_PROMPT_VERSION as QUESTION_DECOMPOSITION_PROMPT_VERSION,
    QUESTION_DECOMPOSITION_V2_SCHEMA as QUESTION_DECOMPOSITION_SCHEMA,
    QUESTION_DECOMPOSITION_V2_SYSTEM_PROMPT as QUESTION_DECOMPOSITION_SYSTEM_PROMPT,
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
        "schema_version": "e1.question_decomposition.v2",
        "mode": "shadow_diagnostic",
        "points": [{**point(), "answer_point_id": "point.1"}],
        "ambiguity": {"status": "clear", "reason": ""},
    }
    assert len(vertex.calls) == 1
    payload, schema, kwargs = vertex.calls[0]
    assert payload == {"task": "decompose_user_question", "untrusted_question": question}
    assert schema is QUESTION_DECOMPOSITION_SCHEMA
    assert schema["properties"]["points"]["minItems"] == 1
    assert schema["properties"]["points"]["maxItems"] == 5
    assert "answer_point_id" not in schema["$defs"]["_Point"]["properties"]
    assert "facet_type" not in schema["$defs"]["_Point"]["required"]
    assert kwargs["system_instruction"] == QUESTION_DECOMPOSITION_SYSTEM_PROMPT
    assert QUESTION_DECOMPOSITION_PROMPT_VERSION == "2.0.0"


def test_multi_part_order_and_ids():
    question = "Where is X defined and why is it needed?"
    locator = point("locator", "Where X is defined", ["Where is X defined"])
    reason = point("cause_reason", "Why X is needed", ["why is it needed"])
    first = decompose(question, proposal(locator, reason))
    assert first == decompose(question, proposal(reason, locator))
    assert [p["answer_point_id"] for p in first["points"]] == ["point.1", "point.2"]


def test_question_order_ids_and_tie_break_are_model_order_independent():
    question = "Where are X and Y defined?"
    x = point("locator", "Locate X", [question, "X", "X"])
    y = point("locator", "Locate Y", [question])
    result = decompose(question, proposal(y, x))
    assert result == decompose(question, proposal(x, y))
    assert [p["answer_point_id"] for p in result["points"]] == ["point.1", "point.2"]
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


@pytest.mark.parametrize("field,value", [("text", " "), ("text", 42), ("answer_point_id", "model.1")])
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


def test_explicit_legacy_mode_never_invokes_decomposer():
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
        result = agent._run_detailed("Where is X defined?", mode="legacy_question_core")
    assert result["result"]["status"] == "answered"
    assert vertex.calls == 2  # Existing answer and review calls only, both fake.


def test_legacy_question_core_unchanged():
    question = "Where is X defined and why is it needed?"
    assert _runtime_answer_points(question) == [{"answer_point_id": "question_core", "text": question}]


@pytest.mark.parametrize("metadata", [None, "workflow_order", "", 42, {}, [], True])
def test_unusable_diagnostic_type_is_omitted_without_invalidating_point(metadata):
    raw = point(facet=metadata)
    expected = point()
    del expected["facet_type"]
    expected["answer_point_id"] = "point.1"
    assert decompose("How does X work?", proposal(raw))["points"] == [expected]


def test_type_changes_or_absence_cannot_reorder_or_reidentify_points():
    question = "Describe X and explain Y."
    # Shared earliest support position makes the text tie-break decisive.
    x = point("workflow", "Describe X", [question, "X"])
    y = point("definition", "Explain Y", [question, "Y"])

    def semantic_fields(result):
        return [{k: v for k, v in p.items() if k != "facet_type"} for p in result["points"]]

    expected = [
        {"answer_point_id": "point.1", "text": "Describe X", "support_spans": [question, "X"]},
        {"answer_point_id": "point.2", "text": "Explain Y", "support_spans": [question, "Y"]},
    ]
    assert semantic_fields(decompose(question, proposal(y, x))) == expected
    x["facet_type"], y["facet_type"] = "api_behavior", "locator"
    assert semantic_fields(decompose(question, proposal(x, y))) == expected
    del x["facet_type"]
    del y["facet_type"]
    assert semantic_fields(decompose(question, proposal(y, x))) == expected


def test_type_does_not_excuse_duplicate_semantic_text_or_invalid_support():
    with pytest.raises(ValueError, match="unique"):
        decompose("How does X work?", proposal(point(), point(facet="workflow")))
    with pytest.raises(ValueError, match="support span"):
        decompose("How does X work?", proposal(point(facet=None, spans=["not requested"])))


@pytest.mark.parametrize("question,texts", [
    ("Where are Cedar and Birch implemented respectively?", ["Locate Cedar", "Locate Birch"]),
    ("What does each of Cedar and Birch contribute?", ["Describe Cedar's contribution", "Describe Birch's contribution"]),
    ("How do Cedar and Birch differ?", ["Compare Cedar and Birch"]),
    ("How does data move from Cedar to Birch?", ["Explain the flow from Cedar to Birch"]),
])
def test_synthetic_obligation_proposals_preserved_without_taxonomy(question, texts):
    # Fake proposals test representation only, not real-model atomicity quality.
    raw = [{"text": text, "support_spans": [question]} for text in texts]
    result = decompose(question, proposal(*reversed(raw)))
    assert [p["text"] for p in result["points"]] == sorted(texts, key=str.casefold)
    assert [p["answer_point_id"] for p in result["points"]] == [f"point.{i}" for i in range(1, len(texts) + 1)]
    assert all("facet_type" not in p for p in result["points"])


def test_normalizer_does_not_invent_semantic_splits_from_cue_words():
    question = "What does each of Cedar and Birch contribute?"
    raw = {"text": "Contributions of Cedar and Birch", "support_spans": [question]}
    result = decompose(question, proposal(raw))
    # Structural validity cannot prove semantic atomicity; E1-R2 must measure it.
    assert len(result["points"]) == 1
