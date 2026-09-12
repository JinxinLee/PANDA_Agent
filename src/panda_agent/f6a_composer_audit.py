"""F6-A evaluation-only composer release audit.

This module never changes product composer behavior: it consumes immutable run
records (final answer, verified claims, composer diagnostics) and produces the
preregistered factuality/readability measurements through the offline
evaluation judge. It adds no retrieval and no product model calls beyond the
audit judge calls themselves.
"""

from __future__ import annotations

import json
from typing import Any

COMPOSER_AUDIT_FACTUALITY_PROMPT = """
You are the release factuality auditor for a bounded answer composer.
You receive the verified claims that were rendered into a composed answer.
Decide whether the composed answer introduces ANY factual content that is not
supported by those claims: new entities, identifiers, paths, versions, numbers,
causal relationships, comparisons, chronology, or strengthened certainty.
Light paraphrase, reordering, merging, and neutral connectors are allowed.
Answer with the structured verdict only. Do not rewrite the answer.
"""

COMPOSER_AUDIT_FACTUALITY_SCHEMA = {
    "type": "object",
    "properties": {
        "introduces_new_facts": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["introduces_new_facts", "reason"],
    "additionalProperties": False,
}

COMPOSER_AUDIT_READABILITY_PROMPT = """
You are a blinded readability judge. You receive two renderings of the same
verified claims, labeled A and B. Judge ONLY readability and organization:
flow, grouping, and ease of reading. Ignore which one is longer or shorter,
ignore factual assessment (both render the same claims), and do not rewrite
either text. Prefer the rendering that reads better as an answer. If neither
clearly reads better, answer "tie".
"""

COMPOSER_AUDIT_READABILITY_SCHEMA = {
    "type": "object",
    "properties": {
        "preferred": {"type": "string", "enum": ["A", "B", "tie"]},
        "reason": {"type": "string"},
    },
    "required": ["preferred", "reason"],
    "additionalProperties": False,
}


def build_composer_audit_pairs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build eligible (composed, deterministic) pairs from frozen run records.

    Eligibility: ANSWERED, composer attempted AND accepted, at least two
    verified public claims. Fallback cases are excluded by construction and
    reported separately as diagnostics.
    """
    pairs: list[dict[str, Any]] = []
    fallback_cases = 0
    for record in records:
        result = record.get("result") or {}
        if result.get("status") != "answered":
            continue
        diagnostics = (record.get("diagnostics") or {}).get("composer") or {}
        claims = result.get("claims") or []
        if len(claims) < 2:
            continue
        if diagnostics.get("attempted") and not diagnostics.get("accepted"):
            fallback_cases += 1
            continue
        if not diagnostics.get("accepted"):
            continue
        composed = str(result.get("answer") or "")
        deterministic = "\n".join(
            f"{claim['claim_text'].strip()} [{', '.join(claim['evidence_ids'])}]"
            for claim in claims
        )
        if not composed.strip() or not deterministic.strip():
            continue
        pairs.append(
            {
                "case_id": str(record.get("id")),
                "composed_answer": composed,
                "deterministic_answer": deterministic,
                "verified_claims": claims,
            }
        )
    return pairs


def judge_composer_factuality(pair: dict[str, Any], vertex: Any) -> dict[str, Any]:
    payload = {
        "task": "audit_composer_factuality",
        "verified_claims": [
            {"claim_id": claim["claim_id"], "claim_text": claim["claim_text"]}
            for claim in pair["verified_claims"]
        ],
        "composed_answer": pair["composed_answer"],
    }
    return vertex.generate_json(
        json.dumps(payload, ensure_ascii=False),
        COMPOSER_AUDIT_FACTUALITY_SCHEMA,
        system_instruction=COMPOSER_AUDIT_FACTUALITY_PROMPT,
    )


def judge_composer_readability(pair: dict[str, Any], vertex: Any) -> dict[str, Any]:
    # Deterministic counterbalancing by preregistered case-ID rule: the first
    # embedded number in the case ID decides presentation order (even ->
    # composed labeled A).
    import re

    match = re.search(r"\d+", str(pair["case_id"]))
    composed_first = (int(match.group(0)) % 2 == 0) if match else True
    first, second = (
        (pair["composed_answer"], pair["deterministic_answer"])
        if composed_first
        else (pair["deterministic_answer"], pair["composed_answer"])
    )
    payload = {
        "task": "judge_composer_readability",
        "A": first,
        "B": second,
    }
    verdict = vertex.generate_json(
        json.dumps(payload, ensure_ascii=False),
        COMPOSER_AUDIT_READABILITY_SCHEMA,
        system_instruction=COMPOSER_AUDIT_READABILITY_PROMPT,
    )
    preferred = verdict.get("preferred")
    if composed_first:
        mapped = {"A": "composed", "B": "deterministic"}.get(preferred, "tie")
    else:
        mapped = {"A": "deterministic", "B": "composed"}.get(preferred, "tie")
    return {"preferred": mapped, "judge_label": preferred, "reason": verdict.get("reason")}


def aggregate_composer_audit(
    pairs: list[dict[str, Any]],
    factuality_verdicts: list[dict[str, Any]],
    readability_verdicts: list[dict[str, Any]],
) -> dict[str, Any]:
    new_fact_count = sum(
        1 for verdict in factuality_verdicts if verdict.get("introduces_new_facts") is True
    )
    composed_preferred = sum(1 for verdict in readability_verdicts if verdict.get("preferred") == "composed")
    deterministic_preferred = sum(
        1 for verdict in readability_verdicts if verdict.get("preferred") == "deterministic"
    )
    ties = sum(1 for verdict in readability_verdicts if verdict.get("preferred") == "tie")
    return {
        "eligible_cases": len(pairs),
        "composer_new_fact_count": new_fact_count,
        "composer_new_fact_rate": (new_fact_count / len(pairs)) if pairs else None,
        "composed_preferred": composed_preferred,
        "deterministic_preferred": deterministic_preferred,
        "tie": ties,
    }
