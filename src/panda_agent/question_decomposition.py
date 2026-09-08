"""Question-only decomposition, callable explicitly for shadow diagnostics."""

from __future__ import annotations

import json
from collections import Counter
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from panda_agent.llm.vertex import VertexAIClient
from panda_agent.prompts import COMMON_SECURITY_SYSTEM_PROMPT

QUESTION_DECOMPOSITION_PROMPT_VERSION = "1.0.0"
QUESTION_DECOMPOSITION_SCHEMA_VERSION = "e1.question_decomposition.v1"

QUESTION_DECOMPOSITION_SYSTEM_PROMPT = COMMON_SECURITY_SYSTEM_PROMPT + """

Decompose only the user's explicit information request. Do not answer it.
Return 1–5 minimal, independently requested facets, not expected answer facts.
Use only wording and semantics explicitly supported by the raw question.
Do not use domain knowledge to infer hidden prerequisites or requirements.
Do not guess files, paths, APIs, stages, repositories, evidence, or facts.
Copy exact non-empty support spans from the original question for every point.
Point text describes what the user asks to know. Do not generate point IDs.
Keep a single request as one point; split only independently explicit asks.
"How does X work?" normally has one mechanism point, not guessed substeps.
"How do X and Y differ?" normally has one comparison point, not separate
background descriptions of X and Y unless independently requested.
"Describe the workflow from A to C" normally has one workflow/data-flow point.
Do not invent intermediate stages or handoffs unless separately requested.
"Where is X defined and why is it needed?" has locator and cause_reason points.
Do not reproduce benchmark templates or reverse-engineer compatibility
requirements. A factory question does not imply input/setter/construction/output
points; troubleshooting does not imply upstream/producer/consumer/schema/binning
or range points unless explicitly requested.
Use only the generic facet taxonomy in the schema.
Ambiguity is diagnostic only: report the narrowest explicit requested facets
even when ambiguous. Do not invent alternative interpretations or ask a
clarification question. For clear questions use an empty ambiguity reason.
Return only the required structured JSON, without rationale or hidden reasoning.
"""


class _Point(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    facet_type: Literal[
        "definition", "mechanism", "implementation", "data_flow", "comparison",
        "locator", "workflow", "cause_reason", "api_behavior", "constraint",
    ]
    text: str = Field(min_length=1)
    support_spans: list[Annotated[str, Field(min_length=1)]] = Field(min_length=1)


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
    """Propose and validate diagnostic facets without retrieval context."""

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
            points.append({
                "facet_type": point.facet_type,
                "text": text,
                "support_spans": list(dict.fromkeys(point.support_spans)),
            })
        points.sort(key=lambda point: (
            min(question.index(span) for span in point["support_spans"]),
            point["facet_type"], point["text"].casefold(),
        ))
        ordinals: Counter[str] = Counter()
        for point in points:
            facet = point["facet_type"]
            ordinals[facet] += 1
            point["answer_point_id"] = f"{facet}.{ordinals[facet]}"
        return {
            "schema_version": QUESTION_DECOMPOSITION_SCHEMA_VERSION,
            "mode": "shadow_diagnostic",
            "points": points,
            "ambiguity": proposal.ambiguity.model_dump(),
        }
