"""Question-only answer-obligation decomposition."""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, field_validator

from panda_agent.llm.vertex import VertexAIClient
from panda_agent.prompts import COMMON_SECURITY_SYSTEM_PROMPT

QUESTION_DECOMPOSITION_V2_PROMPT_VERSION = "2.0.0"
QUESTION_DECOMPOSITION_V2_SCHEMA_VERSION = "e1.question_decomposition.v2"
QUESTION_DECOMPOSITION_PROMPT_VERSION = "3.0.0"
QUESTION_DECOMPOSITION_SCHEMA_VERSION = "e1.question_decomposition.v3"

_DiagnosticFacet = Literal[
    "definition", "mechanism", "implementation", "data_flow", "comparison",
    "locator", "workflow", "cause_reason", "api_behavior", "constraint",
]
_DiagnosticRelation = frozenset({"ordering", "workflow_placement", "dependency", "input_output",
    "cause_effect", "comparison", "composition_containment"})

QUESTION_DECOMPOSITION_SYSTEM_PROMPT = COMMON_SECURITY_SYSTEM_PROMPT + """

Decompose only the user's explicit information request. Do not answer it.
Return 1–5 explicit response obligations, each independently satisfiable and
independently checkable for omission. These are requested needs, not answer facts.
Use only wording and semantics explicitly supported by the raw question.
Do not use domain knowledge to infer hidden prerequisites or requirements.
Do not guess files, paths, APIs, stages, repositories, evidence, or facts.
Copy exact non-empty support spans from the original question for every point.
Point text describes what the user asks to know. Do not generate point IDs.
Split when an answer could satisfy one explicitly requested obligation while
leaving another independently unaddressed. Do not split merely because several
entities, grammatical clauses, conjunctions, or particular cue words occur.
"Where are X and Y implemented respectively?" requests two independently
checkable locations. "What does each of X and Y contribute?" likewise requests
two independently checkable contributions. Represent each obligation separately;
do not hide multiple obligations in a single broad point that mentions them all.
Apply this semantic principle regardless of the particular wording used.
"How does X work?" normally requests one explanation, not guessed substeps.
"How do X and Y differ?" normally requests one comparison, not separate
background descriptions of X and Y unless independently requested.
"Describe the workflow from A to C" normally requests one end-to-end flow.
Do not invent intermediate stages or handoffs unless separately requested.
"Where is X defined and why is it needed?" requests a location and a reason.
Do not reproduce benchmark templates or reverse-engineer compatibility
requirements. A factory question does not imply input/setter/construction/output
points; troubleshooting does not imply upstream/producer/consumer/schema/binning
or range points unless explicitly requested.
The optional facet_type is diagnostic metadata only. Omit it when
uncertain; otherwise use a generic label from the schema. A label does not
determine whether an obligation exists, how to split it, its identity or coverage.
Ambiguity is diagnostic only: report the narrowest explicit requested obligations
even when ambiguous. Do not invent alternative interpretations or ask a
clarification question. For clear questions use an empty ambiguity reason.
Return only the required structured JSON, without rationale or hidden reasoning.
"""
QUESTION_DECOMPOSITION_V2_SYSTEM_PROMPT = QUESTION_DECOMPOSITION_SYSTEM_PROMPT
QUESTION_DECOMPOSITION_SYSTEM_PROMPT = QUESTION_DECOMPOSITION_V2_SYSTEM_PROMPT + """

Production relationship-aware contract: every point must include required_relations,
an explicit empty list for ordinary definitions, locators, API arguments, and
unstructured explanations. Extract a relation only when the user asks to
establish a connection, relative placement, ordering, dependency, input/output,
cause/effect, comparison, or containment. Do not invent an edge from a verb,
property, evidence, or domain workflow knowledge. Preserve direction, negation,
modality, endpoints, and the requested explanation in each relation's text.
A question asking whether a relation holds requests an answer, not a positive
assertion: a grounded negative answer can satisfy it. Copy 1–3 literal nonempty
support spans from the raw question for each relation. Do not generate point or
relation IDs. relation_type is optional diagnostic metadata only. Split ordinary
and relational requests into separate points when either could be omitted while
answering the other. One relational explanation is not a second ordinary point.
Return no unsupported inferred relationship or hidden intermediate stage.
"""


class _Point(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    facet_type: _DiagnosticFacet | None = None
    text: str = Field(min_length=1)
    support_spans: list[Annotated[str, Field(min_length=1)]] = Field(min_length=1)

    @field_validator("facet_type", mode="plain", json_schema_input_type=_DiagnosticFacet)
    @classmethod
    def diagnostic_facet_only(cls, value: Any) -> Any:
        """Unusable optional metadata must not invalidate the semantic point."""
        return value if isinstance(value, str) and value in get_args(_DiagnosticFacet) else None


class _Ambiguity(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    status: Literal["clear", "ambiguous"]
    reason: str


class _Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    points: list[_Point] = Field(min_length=1, max_length=5)
    ambiguity: _Ambiguity


QUESTION_DECOMPOSITION_SCHEMA = _Proposal.model_json_schema()
QUESTION_DECOMPOSITION_V2_SCHEMA = QUESTION_DECOMPOSITION_SCHEMA

# Keep provider-facing schema simple; all bounds and exact provenance are local.
_RELATION_PROPERTIES = {"text": {"type": "string"},
                        "support_spans": {"type": "array", "items": {"type": "string"}},
                        "relation_type": {"type": "string"}}
_POINT_PROPERTIES = {"text": {"type": "string"},
                     "support_spans": {"type": "array", "items": {"type": "string"}},
                     "facet_type": {"type": "string"},
                     "required_relations": {"type": "array", "items": {"type": "object",
                         "properties": _RELATION_PROPERTIES,
                         "required": ["text", "support_spans"], "additionalProperties": False}}}
PRODUCTION_QUESTION_DECOMPOSITION_SCHEMA = {"type": "object", "properties": {
    "points": {"type": "array", "items": {"type": "object", "properties": _POINT_PROPERTIES,
        "required": ["text", "support_spans", "required_relations"], "additionalProperties": False}},
    "ambiguity": {"type": "object", "properties": {
        "status": {"type": "string"}, "reason": {"type": "string"}},
        "required": ["status", "reason"], "additionalProperties": False}},
    "required": ["points", "ambiguity"], "additionalProperties": False}


class QuestionDecomposer:
    """Propose obligations from the raw question without retrieval context."""

    def __init__(self, vertex: VertexAIClient):
        self.vertex = vertex

    def decompose(self, question: str, *, relation_aware: bool = False) -> dict[str, Any]:
        raw = self.vertex.generate_json(
            json.dumps({"task": "decompose_user_question", "untrusted_question": question}),
            PRODUCTION_QUESTION_DECOMPOSITION_SCHEMA if relation_aware else QUESTION_DECOMPOSITION_V2_SCHEMA,
            system_instruction=(QUESTION_DECOMPOSITION_SYSTEM_PROMPT if relation_aware
                                else QUESTION_DECOMPOSITION_V2_SYSTEM_PROMPT),
        )
        if relation_aware:
            if not isinstance(raw, dict) or set(raw) != {"points", "ambiguity"}:
                raise ValueError("invalid decomposition fields")
            if not isinstance(raw["points"], list) or not 1 <= len(raw["points"]) <= 5:
                raise ValueError("invalid point count")
            ambiguity = _Ambiguity.model_validate(raw["ambiguity"])
            proposals = raw["points"]
        else:
            proposal = _Proposal.model_validate(raw)
            ambiguity = proposal.ambiguity
            proposals = proposal.points
        points = []
        seen_texts: set[str] = set()
        seen_relations: set[str] = set()
        total_relations = 0
        for proposed in proposals:
            if relation_aware:
                if not isinstance(proposed, dict) or set(proposed) - {"text", "support_spans", "facet_type", "required_relations"} or not {"text", "support_spans", "required_relations"} <= set(proposed):
                    raise ValueError("invalid production point fields")
                if not isinstance(proposed["required_relations"], list) or len(proposed["required_relations"]) > 3:
                    raise ValueError("invalid relation count")
                point = _Point.model_validate({k: v for k, v in proposed.items() if k != "required_relations"})
            else:
                point = proposed
            text = " ".join(point.text.split())
            if not text or text.casefold() in seen_texts:
                raise ValueError("point text must be non-empty and unique after normalization")
            seen_texts.add(text.casefold())
            if any(not span.strip() or span not in question for span in point.support_spans):
                raise ValueError("every support span must be an exact non-empty question substring")
            normalized = {
                "text": text,
                "support_spans": list(dict.fromkeys(point.support_spans)),
            }
            if point.facet_type is not None:
                normalized["facet_type"] = point.facet_type
            if relation_aware:
                relations = []
                for raw_relation in proposed["required_relations"]:
                    if not isinstance(raw_relation, dict) or set(raw_relation) - {"text", "support_spans", "relation_type"} or not {"text", "support_spans"} <= set(raw_relation):
                        raise ValueError("invalid relation fields")
                    raw_text, spans = raw_relation["text"], raw_relation["support_spans"]
                    if not isinstance(raw_text, str) or not isinstance(spans, list) or not 1 <= len(spans) <= 3 or not all(isinstance(s, str) and s.strip() and s in question for s in spans):
                        raise ValueError("invalid relation text or exact support")
                    relation_text = " ".join(raw_text.split())
                    if not 1 <= len(relation_text) <= 240 or relation_text.casefold() in seen_relations:
                        raise ValueError("invalid or duplicate relation text")
                    seen_relations.add(relation_text.casefold())
                    ordered_spans = sorted(set(spans), key=lambda s: (question.index(s), s))
                    relation = {"text": relation_text, "support_spans": ordered_spans}
                    kind = raw_relation.get("relation_type")
                    if isinstance(kind, str) and kind in _DiagnosticRelation:
                        relation["relation_type"] = kind
                    relations.append(relation)
                    total_relations += 1
                    if total_relations > 10:
                        raise ValueError("relation count exceeds question bound")
                relations.sort(key=lambda r: (min(question.index(s) for s in r["support_spans"]), r["text"].casefold()))
                normalized["required_relations"] = relations
            points.append(normalized)
        points.sort(key=lambda point: (
            min(question.index(span) for span in point["support_spans"]),
            point["text"].casefold(),
        ))
        for ordinal, point in enumerate(points, start=1):
            point["answer_point_id"] = f"point.{ordinal}"
            if relation_aware:
                for relation_ordinal, relation in enumerate(point["required_relations"], start=1):
                    relation["relation_id"] = f"point.{ordinal}.rel.{relation_ordinal}"
        return {
            "schema_version": QUESTION_DECOMPOSITION_SCHEMA_VERSION if relation_aware else QUESTION_DECOMPOSITION_V2_SCHEMA_VERSION,
            "mode": "production_authoritative" if relation_aware else "shadow_diagnostic",
            "points": points,
            "ambiguity": ambiguity.model_dump(),
        }
