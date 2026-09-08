"""Question-only decomposition, callable explicitly for shadow diagnostics."""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, field_validator

from panda_agent.llm.vertex import VertexAIClient
from panda_agent.prompts import COMMON_SECURITY_SYSTEM_PROMPT

QUESTION_DECOMPOSITION_PROMPT_VERSION = "2.0.0"
QUESTION_DECOMPOSITION_SCHEMA_VERSION = "e1.question_decomposition.v2"

_DiagnosticFacet = Literal[
    "definition", "mechanism", "implementation", "data_flow", "comparison",
    "locator", "workflow", "cause_reason", "api_behavior", "constraint",
]

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


class QuestionDecomposer:
    """Propose explicit obligations for shadow diagnostics, without retrieval context."""

    def __init__(self, vertex: VertexAIClient):
        self.vertex = vertex

    def decompose(self, question: str) -> dict[str, Any]:
        raw = self.vertex.generate_json(
            json.dumps({"task": "decompose_user_question", "untrusted_question": question}),
            QUESTION_DECOMPOSITION_SCHEMA,
            system_instruction=QUESTION_DECOMPOSITION_SYSTEM_PROMPT,
        )
        proposal = _Proposal.model_validate(raw)
        points = []
        seen_texts: set[str] = set()
        for point in proposal.points:
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
            points.append(normalized)
        points.sort(key=lambda point: (
            min(question.index(span) for span in point["support_spans"]),
            point["text"].casefold(),
        ))
        for ordinal, point in enumerate(points, start=1):
            point["answer_point_id"] = f"point.{ordinal}"
        return {
            "schema_version": QUESTION_DECOMPOSITION_SCHEMA_VERSION,
            "mode": "shadow_diagnostic",
            "points": points,
            "ambiguity": proposal.ambiguity.model_dump(),
        }
