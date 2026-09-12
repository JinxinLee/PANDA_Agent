"""M4 multi-channel retrieval with version filtering, RRF, and quotas."""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from qdrant_client import models

from panda_agent.config import load_query_expansions, load_retrieval_policies
from panda_agent.d3_structured import (
    D3_5Arm,
    D3_5ExperimentConfig,
    D3Arm,
    D3ExperimentConfig,
    SELECTIVITY_POLICY_VERSION,
    build_candidate_payload_registry,
    build_eligible_bridge_candidates,
    build_structured_contribution_from_storage,
    build_treatment_pool,
    reservable_bridge,
    select_matching_query_expansions,
    select_structured_candidates_v2,
)
from panda_agent.entity_resolution import EntityResolver, merge_exact_streams
from panda_agent.lexical_query import build_lexical_query
from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.models import AuthorityLevel, Evidence, RetrievalPlan, SourceLocator, stable_id
from panda_agent.prompts import QUERY_ANALYZER_SYSTEM_PROMPT, RERANK_SYSTEM_PROMPT
from panda_agent.sparse import create_sparse_encoder
from panda_agent.storage import Storage


_ANALYZER_INTENTS = [
    "installation",
    "usage",
    "algorithm_theory",
    "algorithm_implementation",
    "api",
    "data_flow",
    "module_structure",
    "troubleshooting",
]
_REPOSITORY_IDS = ["luminosityfit", "pandaroot", "restgas_determination"]
_SUPPORT_SPANS_SCHEMA = {"type": "array", "items": {"type": "string"}}
_SEMANTIC_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "string"},
        "support_spans": _SUPPORT_SPANS_SCHEMA,
    },
    "required": ["value", "support_spans"],
    "additionalProperties": False,
}
_INTENT_ITEM_SCHEMA = {
    **_SEMANTIC_ITEM_SCHEMA,
    "properties": {
        "value": {"type": "string", "enum": _ANALYZER_INTENTS},
        "support_spans": _SUPPORT_SPANS_SCHEMA,
    },
}
_VERSION_MENTION_SCHEMA = {
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "repository": {"type": "string", "enum": _REPOSITORY_IDS},
        "support_spans": _SUPPORT_SPANS_SCHEMA,
    },
    "required": ["token", "support_spans"],
    "additionalProperties": False,
}
_CONCEPT_SCOPE_SCHEMA = {
    "type": "object",
    "properties": {
        "key": {"type": "string"},
        "value": {"type": "string"},
        "support_spans": _SUPPORT_SPANS_SCHEMA,
    },
    "required": ["key", "value", "support_spans"],
    "additionalProperties": False,
}


ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": _INTENT_ITEM_SCHEMA,
        "repository_additions": {
            "type": "array",
            "items": {
                **_SEMANTIC_ITEM_SCHEMA,
                "properties": {
                    "value": {"type": "string", "enum": _REPOSITORY_IDS},
                    "support_spans": _SUPPORT_SPANS_SCHEMA,
                },
            },
        },
        "concepts": {"type": "array", "items": _SEMANTIC_ITEM_SCHEMA},
        "symbols": {"type": "array", "items": _SEMANTIC_ITEM_SCHEMA},
        "version_mentions": {"type": "array", "items": _VERSION_MENTION_SCHEMA},
        "concept_scopes": {"type": "array", "items": _CONCEPT_SCOPE_SCHEMA},
    },
    "required": [
        "intent",
        "repository_additions",
        "concepts",
        "symbols",
        "version_mentions",
        "concept_scopes",
    ],
    "additionalProperties": False,
}


def _analysis_schema(
    *, intent_is_fixed: bool, semantic_output_fields: list[str] | None = None
) -> dict[str, Any]:
    """Return the explicit response contract for the remaining semantic delta."""
    properties = dict(ANALYSIS_SCHEMA["properties"])
    required = list(ANALYSIS_SCHEMA["required"])
    if intent_is_fixed:
        properties.pop("intent", None)
        if "intent" in required:
            required.remove("intent")
    if semantic_output_fields is not None:
        allowed = set(semantic_output_fields)
        properties = {key: value for key, value in properties.items() if key in allowed}
        required = [key for key in required if key in allowed]
    return {**ANALYSIS_SCHEMA, "properties": properties, "required": required}


@dataclass(frozen=True)
class AnalyzerSemanticItem:
    value: str
    support_spans: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"value": self.value, "support_spans": list(self.support_spans)}


@dataclass(frozen=True)
class AnalyzerVersionMention:
    token: str
    support_spans: tuple[str, ...]
    repository: str | None = None

    def as_dict(self) -> dict[str, Any]:
        result = {"token": self.token, "support_spans": list(self.support_spans)}
        if self.repository is not None:
            result["repository"] = self.repository
        return result


@dataclass(frozen=True)
class AnalyzerScopeItem:
    key: str
    value: str
    support_spans: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "support_spans": list(self.support_spans),
        }


@dataclass
class AnalyzerSemanticDelta:
    intent: AnalyzerSemanticItem | None = None
    repository_additions: list[AnalyzerSemanticItem] = field(default_factory=list)
    concepts: list[AnalyzerSemanticItem] = field(default_factory=list)
    symbols: list[AnalyzerSemanticItem] = field(default_factory=list)
    version_mentions: list[AnalyzerVersionMention] = field(default_factory=list)
    concept_scopes: list[AnalyzerScopeItem] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "repository_additions": [item.as_dict() for item in self.repository_additions],
            "concepts": [item.as_dict() for item in self.concepts],
            "symbols": [item.as_dict() for item in self.symbols],
            "version_mentions": [item.as_dict() for item in self.version_mentions],
            "concept_scopes": [item.as_dict() for item in self.concept_scopes],
        }
        if self.intent is not None:
            result["intent"] = self.intent.as_dict()
        return result


@dataclass
class AnalyzerDeltaValidation:
    delta: AnalyzerSemanticDelta
    rejected_items: list[dict[str, Any]] = field(default_factory=list)
    unbound_version_tokens: list[str] = field(default_factory=list)


def _query_tokens(value: str) -> set[str]:
    return {token.casefold() for token in re.findall(r"[A-Za-z0-9]+", value)}


def _complete_technical_token(
    token: str, text: str, *, case_sensitive: bool = True
) -> str | None:
    """Return a query substring only when token boundaries are technically complete."""
    if not token or not isinstance(text, str):
        return None
    flags = 0 if case_sensitive else re.IGNORECASE

    def continues(index: int, direction: int) -> bool:
        char = text[index]
        if char.isalnum() or char in "_:/@":
            return True
        if char in ".-":
            neighbor = index + direction
            return (
                0 <= neighbor < len(text)
                and (text[neighbor].isalnum() or text[neighbor] == "_")
            )
        return False

    for match in re.finditer(re.escape(token), text, flags):
        start, end = match.span()
        if start and continues(start - 1, -1):
            continue
        if end < len(text) and continues(end, 1):
            continue
        return text[start:end]
    return None


def _concept_is_query_grounded(value: str, support_spans: tuple[str, ...], question: str) -> bool:
    value_tokens = _query_tokens(value)
    grounded_tokens = _query_tokens(question) | _query_tokens(" ".join(support_spans))
    if not value_tokens or not grounded_tokens:
        return False
    return all(
        any(
            value_token == grounded_token
            or (
                len(value_token) >= 5
                and len(grounded_token) >= 5
                and (
                    value_token.startswith(grounded_token)
                    or grounded_token.startswith(value_token)
                )
            )
            for grounded_token in grounded_tokens
        )
        for value_token in value_tokens
    )


def _scope_is_query_grounded(
    key: str,
    value: str,
    support_spans: tuple[str, ...],
    question: str,
    parsed: DeterministicQueryParse,
) -> bool:
    """Require both the scope concept and normalized value to be grounded."""
    normalized_key = re.sub(r"[_-]+", " ", key)
    key_grounded = _concept_is_query_grounded(normalized_key, support_spans, question)
    normalized_key = re.sub(r"\s+", " ", normalized_key).strip().casefold()
    normalized_value = re.sub(r"[_-]+", " ", value)
    normalized_value = re.sub(r"\s+", " ", normalized_value).strip().casefold()
    known_value = False
    for known_scopes in (parsed.fixed_concept_scopes, parsed.fallback_concept_scopes):
        for known_key, known_scope_value in known_scopes.items():
            known_key_normalized = re.sub(r"[_-]+", " ", known_key)
            known_key_normalized = re.sub(r"\s+", " ", known_key_normalized).strip().casefold()
            if known_key_normalized == normalized_key:
                key_grounded = True
                known_value = known_value or (
                    re.sub(r"[_-]+", " ", known_scope_value)
                    .strip()
                    .casefold()
                    == normalized_value
                )
    value_grounded = _concept_is_query_grounded(value, support_spans, question)
    return key_grounded and (value_grounded or known_value)


def _has_explicit_repository_reference(question: str, repository: str) -> bool:
    """Match a manifest repository ID without accepting a larger containing token."""
    parts = [re.escape(part) for part in repository.split("_")]
    pattern = rf"(?<![a-z0-9]){'[\\s_-]?'.join(parts)}(?![a-z0-9])"
    return re.search(pattern, question, re.IGNORECASE) is not None


def _has_explicit_version_repository_binding(
    question: str, repository: str, token: str
) -> bool:
    """Require explicit repository/version syntax before fixing a SHA association."""
    repository_parts = [re.escape(part) for part in repository.split("_")]
    repository_pattern = rf"(?<![a-z0-9]){'[\\s_-]?'.join(repository_parts)}(?![a-z0-9])"
    token_pattern = rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])"
    qualifier = r"(?:commit|sha|version|ref)"
    separator = r"[\s:=-]+"
    patterns = (
        rf"{repository_pattern}{separator}{qualifier}{separator}{token_pattern}",
        rf"{repository_pattern}\s*@\s*{token_pattern}",
        rf"{qualifier}{separator}{token_pattern}{separator}(?:for|of|in){separator}{repository_pattern}",
    )
    return any(re.search(pattern, question, re.IGNORECASE) for pattern in patterns)


@dataclass
class DeterministicQueryParse:
    """Known query facts extracted without semantic inference."""

    intent: str | None = None
    target_repositories: list[str] = field(default_factory=list)
    requested_versions: dict[str, str] = field(default_factory=dict)
    explicit_shas: list[str] = field(default_factory=list)
    version_repositories: list[str] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    fixed_concept_scopes: dict[str, str] = field(default_factory=dict)
    fallback_concept_scopes: dict[str, str] = field(default_factory=dict)
    resolved_aliases: dict[str, str] = field(default_factory=dict)
    premise_corrections: list[str] = field(default_factory=list)
    paper_page_hints: dict[str, list[int]] = field(default_factory=dict)
    matched_expansion_rules: list[str] = field(default_factory=list)
    structured_replacement_rules: list[str] = field(default_factory=list)
    provenance: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    d3_experiment: dict[str, Any] | None = None

    def record(
        self, field_name: str, *, source: str, rule: str, value: str | None = None,
        ownership: str | None = None,
    ) -> None:
        entry = {"source": source, "rule": rule}
        if value is not None:
            entry["value"] = value
        if ownership is not None:
            entry["ownership"] = ownership
        self.provenance.setdefault(field_name, []).append(entry)

    def analyzer_context(self, semantic_output_fields: list[str]) -> dict[str, Any]:
        fixed: dict[str, Any] = {}
        if self.intent is not None:
            fixed["intent"] = self.intent
        if self.fixed_concept_scopes:
            fixed["concept_scopes"] = self.fixed_concept_scopes
        for field_name, value in {
            "requested_versions": self.requested_versions,
            "explicit_sha_tokens": self.explicit_shas,
            "resolved_aliases": self.resolved_aliases,
            "premise_corrections": self.premise_corrections,
            "matched_expansion_rules": self.matched_expansion_rules,
            "paper_page_hints": self.paper_page_hints,
        }.items():
            if value:
                fixed[field_name] = value
        known_partial = {
            "target_repositories": self.target_repositories,
            "symbols": self.symbols,
            "concepts": self.concepts,
        }
        known_partial = {key: value for key, value in known_partial.items() if value}
        unresolved_semantics: dict[str, str] = {}
        for field_name in semantic_output_fields:
            if field_name == "repository_additions" and self.target_repositories:
                unresolved_semantics[field_name] = "augment_known_partial"
                unresolved_semantics["target_repositories"] = "augment_known_partial"
            elif field_name == "repository_additions":
                unresolved_semantics[field_name] = "resolve"
                unresolved_semantics["target_repositories"] = "resolve"
            elif field_name in known_partial:
                unresolved_semantics[field_name] = "augment_known_partial"
            elif field_name == "version_mentions" and self.requested_versions:
                unresolved_semantics[field_name] = "preserve_fixed_version_keys"
                unresolved_semantics["requested_versions"] = "augment_fixed_keys"
            elif field_name == "concept_scopes" and self.fixed_concept_scopes:
                unresolved_semantics[field_name] = "resolve_remaining_scope_keys_after_fixed_constraints"
            elif field_name == "concept_scopes" and self.fallback_concept_scopes:
                unresolved_semantics[field_name] = "resolve_remaining_scope_keys_with_fallback"
            else:
                unresolved_semantics[field_name] = "resolve"
        return {
            "fixed": fixed,
            "fallback": {"concept_scopes": self.fallback_concept_scopes},
            "known_partial": known_partial,
            "semantic_output_fields": semantic_output_fields,
            "unresolved_semantics": unresolved_semantics,
            "provenance": self.provenance,
        }


def _validate_analyzer_delta(
    question: str,
    parsed: DeterministicQueryParse,
    result: Any,
    semantic_output_fields: list[str],
) -> AnalyzerDeltaValidation:
    """Validate and normalize the query-grounded semantic delta."""
    validation = AnalyzerDeltaValidation(delta=AnalyzerSemanticDelta())
    if not isinstance(result, dict):
        validation.rejected_items.append(
            {"field": "root", "value": result, "reason": "malformed_delta"}
        )
        return validation

    def reject(field_name: str, item: Any, reason: str, **extra: Any) -> None:
        entry = {"field": field_name, "item": item, "reason": reason}
        entry.update(extra)
        validation.rejected_items.append(entry)

    def grounded_item(
        field_name: str,
        item: Any,
        *,
        value_key: str = "value",
        allowed_keys: set[str] | None = None,
    ) -> tuple[str, tuple[str, ...]] | None:
        allowed = allowed_keys or {value_key, "support_spans"}
        if not isinstance(item, dict):
            reject(field_name, item, "malformed_item")
            return None
        if set(item) - allowed:
            reject(field_name, item, "unexpected_item_properties")
            return None
        value = item.get(value_key)
        support_spans = item.get("support_spans")
        if not isinstance(value, str) or not value.strip():
            reject(field_name, item, "missing_value")
            return None
        if (
            not isinstance(support_spans, list)
            or not support_spans
            or any(not isinstance(span, str) or not span or span not in question for span in support_spans)
        ):
            reject(field_name, item, "unsupported_query_support")
            return None
        return value, tuple(support_spans)

    def item_list(field_name: str) -> list[Any]:
        raw_items = result.get(field_name, [])
        if raw_items is None:
            return []
        if not isinstance(raw_items, list):
            reject(field_name, raw_items, "malformed_field")
            return []
        return raw_items

    if parsed.intent is None:
        raw_intent = result.get("intent")
        if raw_intent is None:
            reject("intent", raw_intent, "missing_intent")
        else:
            grounded = grounded_item("intent", raw_intent)
            if grounded is not None:
                value, support_spans = grounded
                if value not in _ANALYZER_INTENTS:
                    reject("intent", raw_intent, "unsupported_intent")
                else:
                    validation.delta.intent = AnalyzerSemanticItem(value, support_spans)
    elif "intent" in result:
        reject("intent", result["intent"], "fixed_intent_output")

    repository_items = item_list("repository_additions")
    if "repository_additions" not in semantic_output_fields and repository_items:
        for raw_item in repository_items:
            reject("repository_additions", raw_item, "unrequested_delta_field")
        repository_items = []
    for raw_item in repository_items:
        grounded = grounded_item("repository_additions", raw_item)
        if grounded is None:
            continue
        value, support_spans = grounded
        repository = value.casefold()
        if (
            repository not in _REPOSITORY_IDS
            or not _has_explicit_repository_reference(question, repository)
            or not any(
                _has_explicit_repository_reference(span, repository)
                for span in support_spans
            )
        ):
            reject("repository_additions", raw_item, "unsupported_repository")
            continue
        validation.delta.repository_additions.append(
            AnalyzerSemanticItem(repository, support_spans)
        )

    concept_items = item_list("concepts")
    if "concepts" not in semantic_output_fields and concept_items:
        for raw_item in concept_items:
            reject("concepts", raw_item, "unrequested_delta_field")
        concept_items = []
    for raw_item in concept_items:
        grounded = grounded_item("concepts", raw_item)
        if grounded is None:
            continue
        value, support_spans = grounded
        if not _concept_is_query_grounded(value, support_spans, question):
            reject("concepts", raw_item, "unsupported_concept")
            continue
        validation.delta.concepts.append(AnalyzerSemanticItem(value, support_spans))

    symbol_items = item_list("symbols")
    if "symbols" not in semantic_output_fields and symbol_items:
        for raw_item in symbol_items:
            reject("symbols", raw_item, "unrequested_delta_field")
        symbol_items = []
    for raw_item in symbol_items:
        grounded = grounded_item("symbols", raw_item)
        if grounded is None:
            continue
        value, support_spans = grounded
        if (
            _complete_technical_token(value, question) is None
            or not any(
                _complete_technical_token(value, span) is not None
                for span in support_spans
            )
        ):
            reject("symbols", raw_item, "unsupported_symbol")
            continue
        validation.delta.symbols.append(AnalyzerSemanticItem(value, support_spans))

    fixed_version_tokens = {
        value.casefold() for value in parsed.requested_versions.values()
    }
    version_items = item_list("version_mentions")
    if "version_mentions" not in semantic_output_fields and version_items:
        for raw_item in version_items:
            reject("version_mentions", raw_item, "unrequested_delta_field")
        version_items = []
    for raw_item in version_items:
        grounded = grounded_item(
            "version_mentions",
            raw_item,
            value_key="token",
            allowed_keys={"token", "repository", "support_spans"},
        )
        if grounded is None:
            continue
        token, support_spans = grounded
        repository: str | None = None
        requested_repository = raw_item.get("repository")
        if "repository" in raw_item:
            if (
                not isinstance(requested_repository, str)
                or requested_repository.casefold() not in _REPOSITORY_IDS
            ):
                reject("version_mentions", raw_item, "unsupported_repository")
            elif (
                len(parsed.version_repositories) == 1
                and requested_repository.casefold() == parsed.version_repositories[0]
                and any(
                    _has_explicit_repository_reference(span, requested_repository)
                    for span in support_spans
                )
            ):
                repository = requested_repository.casefold()
            else:
                reject("version_mentions", raw_item, "ambiguous_version_repository")
        query_token = _complete_technical_token(token, question, case_sensitive=False)
        if query_token is None or not any(
            _complete_technical_token(token, span, case_sensitive=False) is not None
            for span in support_spans
        ):
            reject("version_mentions", raw_item, "unsupported_version")
            continue
        validation.delta.version_mentions.append(
            AnalyzerVersionMention(query_token, support_spans, repository)
        )
        if repository is None and query_token.casefold() not in fixed_version_tokens:
            validation.unbound_version_tokens.append(query_token)

    scope_items = item_list("concept_scopes")
    if "concept_scopes" not in semantic_output_fields and scope_items:
        for raw_item in scope_items:
            reject("concept_scopes", raw_item, "unrequested_delta_field")
        scope_items = []
    for raw_item in scope_items:
        if not isinstance(raw_item, dict):
            reject("concept_scopes", raw_item, "malformed_item")
            continue
        grounded = grounded_item(
            "concept_scopes",
            raw_item,
            allowed_keys={"key", "value", "support_spans"},
        )
        if grounded is None:
            continue
        _, support_spans = grounded
        key = raw_item.get("key")
        value = raw_item.get("value")
        if not isinstance(key, str) or not key.strip() or not isinstance(value, str) or not value.strip():
            reject("concept_scopes", raw_item, "missing_scope_value")
            continue
        if not _scope_is_query_grounded(key, value, support_spans, question, parsed):
            reject("concept_scopes", raw_item, "unsupported_scope")
            continue
        validation.delta.concept_scopes.append(
            AnalyzerScopeItem(key, value, support_spans)
        )

    allowed_output_fields = set(ANALYSIS_SCHEMA["properties"])
    for field_name, raw_value in result.items():
        if field_name not in allowed_output_fields:
            reject(field_name, raw_value, "unexpected_delta_field")
    validation.unbound_version_tokens = list(dict.fromkeys(validation.unbound_version_tokens))
    return validation


def route_high_confidence_intent(
    question: str, routes: dict[str, list[str]] | None = None
) -> str | None:
    """Route explicit operational wording before asking the LLM classifier."""
    lowered = question.casefold()
    if re.search(
        r"(?:recover|reconstruct|restore).*\b(?:deleted|removed)\b|"
        r"\b(?:deleted|removed)\b.*(?:recover|reconstruct|restore)",
        lowered,
    ):
        return "troubleshooting"
    routes = routes or {
        "troubleshooting": [r"\btroubleshoot", r"\bdebug\b", r"\berror\b", r"\bfail(?:s|ed|ure)?\b", r"\bmissing\b", r"\bcannot\b", r"\bwrong\b", r"\bwhy might\b", "what should i inspect", "排查", "报错", "失败", "缺失"],
        "installation": [r"\binstall", "environment variable", "pandaroot environment", "cernvm-fs", "cvmfs", "cmake error", "docker", "安装", "环境变量"],
        "data_flow": [r"\btrace\b", "data flow", r"\bproduces\b", r"\bconsumes\b", "into pid_final", "passed to", "read into", "写出", "读入", "数据流", "谁产生", "谁消费", "如何进入", "如何连接"],
        "api": [r"\bwhere (?:is|does|can)\b", r"\bdefined\b", r"\bsignature\b", r"\bapi\b", r"\bwhich (?:macro|source|file|class|method|function)\b", r"\blocate\b", "哪个宏", "哪个类", "哪个函数"],
        "algorithm_implementation": [r"\bhow is .+ implemented\b", r"\bhow does .+ (?:form|create|work|use)\b", r"\bimplementation\b", r"event_poca.*(?:event|事件).*(?:read|读)", r"extrapolat.*event.?poca", "如何实现", "由哪些类实现", "如何回传", "如何形成", "如何用于", "实现层面", "代码实现"],
        "algorithm_theory": [r"\btheoretical\b", r"\bconceptual\b", r"\bwhy does\b", r"\bwhy is\b", "理论", "原理", "为什么需要", "物理意义"],
        "module_structure": [r"\bmodule structure\b", r"\bmodule boundary\b", r"\bmodule.*connect", r"\bcomponents?\b", r"\blayers?\b", "模块结构", "模块边界", "模块如何连接", "由哪些模块"],
        "usage": [r"\bhow (?:do|can) i (?:run|use|invoke|start|select)\b", r"\bhow is .+ (?:supplied|provided|documented)\b", r"\bwhat is the documented .+ sequence\b", r"\busage\b", "如何运行", "如何使用", "怎么运行", "如何提供", "如何供给"],
    }
    priority = (
        "troubleshooting", "installation", "algorithm_implementation", "api",
        "usage", "module_structure", "data_flow", "algorithm_theory",
    )
    for intent in priority:
        patterns = [
            *routes.get(intent, []),
            *routes.get(f"{intent}_extra", []),
        ]
        if any(re.search(pattern, lowered) for pattern in patterns):
            return intent
    return None


def _evidence(payload: dict[str, Any], score: float, channels: list[str]) -> Evidence:
    return Evidence(
        evidence_id=stable_id(payload["object_id"], *sorted(channels), prefix="evidence"),
        object_id=payload["object_id"], source_id=payload["source_id"],
        source_version_id=payload["source_version_id"], text=payload.get("text", ""),
        locator=SourceLocator.model_validate(payload.get("locator") or {}),
        retrieval_channels=channels, score=score,
        authority_level=AuthorityLevel(payload.get("authority_level", "primary")),
    )


def _source_type_of(item: dict[str, Any]) -> str:
    if item["source_id"] in {"li_2026", "karavdina_2015", "pflueger_2017"}:
        return "paper"
    if "sphinx" in item["source_id"]:
        return "documentation"
    locator = item.get("locator") or {}
    path = (locator.get("path") or "").replace("\\", "/").lower()
    if path.startswith(("docs/", "doc/")):
        return "documentation"
    if item.get("object_type") in {"workflow", "python_script", "shell_script"}:
        return "workflow"
    if item.get("object_type") == "readme_section":
        return "readme"
    if item.get("object_type") == "python_script":
        return "workflow"
    return "code"


def select_final_evidence(
    ordered: list[str],
    payloads: dict[str, dict[str, Any]],
    scores: dict[str, float],
    channels: dict[str, list[str]],
    plan: RetrievalPlan,
    final_evidence_limit: int,
    mandatory_symbol_ids: set[str],
) -> tuple[list[Evidence], list[dict[str, Any]], list[dict[str, Any]]]:
    """Select final evidence with a two-pass hard-budget plus required backfill.

    Pass 1 applies the original hard budgets (duplicate locator, per-source cap,
    per-type cap, mandatory exact-symbol exemption) without any soft admission.
    Pass 2 runs only when the hard pass left unused evidence capacity; it backfills
    Pass-1 budget-rejected candidates in original canonical order if they are
    high-ranked, distinct, and from a required source type.  Backfill count is
    naturally bounded by ``final_evidence_limit - hard_pass_selected_count``.
    """
    selected: list[Evidence] = []
    per_source: dict[str, int] = defaultdict(int)
    per_type: dict[str, int] = defaultdict(int)
    max_per_source = max(2, math.ceil(final_evidence_limit / 3))
    type_caps = {
        key: max(1, math.ceil(value * final_evidence_limit))
        for key, value in plan.source_budgets.items()
    }
    required_types = set(plan.required_source_types)
    seen_locator: set[str] = set()
    hard_rejected: list[dict[str, Any]] = []
    duplicate_rejected: list[dict[str, Any]] = []

    # Pass 1: hard-budget allocation only.
    for rank, object_id in enumerate(ordered, 1):
        item = payloads[object_id]
        raw_locator = item.get("locator") or {}
        locator = json.dumps(raw_locator, sort_keys=True)
        if not any(value not in (None, "", [], {}) for value in raw_locator.values()):
            locator = f"object:{object_id}"
        source_type = _source_type_of(item)
        if locator in seen_locator:
            duplicate_rejected.append({"object_id": object_id, "reason": "duplicate_locator"})
            continue
        source_violated = (
            object_id not in mandatory_symbol_ids
            and per_source[item["source_id"]] >= max_per_source
        )
        type_violated = (
            object_id not in mandatory_symbol_ids
            and per_type[source_type] >= type_caps.get(source_type, final_evidence_limit)
        )
        if source_violated or type_violated:
            reason = (
                "source_diversity_cap_and_source_budget_cap"
                if source_violated and type_violated
                else "source_diversity_cap"
                if source_violated
                else "source_budget_cap"
            )
            hard_rejected.append(
                {
                    "object_id": object_id,
                    "canonical_rank": rank,
                    "original_block_reason": reason,
                    "source_id": item["source_id"],
                    "source_type": source_type,
                }
            )
            continue
        seen_locator.add(locator)
        per_source[item["source_id"]] += 1
        per_type[source_type] += 1
        selected.append(_evidence(item, scores[object_id], channels[object_id]))
        if len(selected) >= final_evidence_limit:
            break

    # Pass 2: required-source backfill using only unused total evidence capacity.
    backfill_admissions: list[dict[str, Any]] = []
    if len(selected) < final_evidence_limit:
        backfill_admitted_ids: set[str] = set()
        for rejected in hard_rejected:
            if len(selected) >= final_evidence_limit:
                break
            object_id = rejected["object_id"]
            if rejected["canonical_rank"] > final_evidence_limit:
                continue
            if rejected["source_type"] not in required_types:
                continue
            item = payloads[object_id]
            raw_locator = item.get("locator") or {}
            locator = json.dumps(raw_locator, sort_keys=True)
            if not any(value not in (None, "", [], {}) for value in raw_locator.values()):
                locator = f"object:{object_id}"
            if locator in seen_locator:
                continue
            seen_locator.add(locator)
            per_source[item["source_id"]] += 1
            per_type[rejected["source_type"]] += 1
            selected.append(_evidence(item, scores[object_id], channels[object_id]))
            backfill_admitted_ids.add(object_id)
            backfill_admissions.append(
                {
                    "object_id": object_id,
                    "canonical_rank": rejected["canonical_rank"],
                    "original_block_reason": rejected["original_block_reason"],
                    "source_id": item["source_id"],
                    "source_type": rejected["source_type"],
                    "admission_phase": "required_source_backfill",
                }
            )

    final_excluded = duplicate_rejected + [
        rejected
        for rejected in hard_rejected
        if rejected["object_id"] not in {admission["object_id"] for admission in backfill_admissions}
    ]
    return selected, final_excluded, backfill_admissions


@dataclass(frozen=True)
class SemanticQueryComponent:
    kind: str
    value: str
    provenance: str

@dataclass
class SemanticQuery:
    text: str
    raw_question: str
    components: list[SemanticQueryComponent]
    excluded_component_classes: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "raw_question": self.raw_question,
            "components": [{"kind": c.kind, "value": c.value, "provenance": c.provenance} for c in self.components],
            "excluded_component_classes": self.excluded_component_classes,
        }


@dataclass(frozen=True)
class RawDenseQuery:
    """The production-authoritative dense view of the user's raw question."""

    text: str
    provenance: str = "user_raw"

    def as_dict(self) -> dict[str, Any]:
        return {"text": self.text, "provenance": self.provenance, "active": True}


@dataclass(frozen=True)
class SemanticDenseQuery:
    """An optional, independently observable dense view from SemanticQuery."""

    text: str
    components: list[SemanticQueryComponent]
    provenance: str = "semantic_query"
    excluded_component_classes: list[str] = field(default_factory=list)

    def as_dict(self, *, executed: bool = False) -> dict[str, Any]:
        return {
            "text": self.text,
            "components": [
                {"kind": c.kind, "value": c.value, "provenance": c.provenance}
                for c in self.components
            ],
            "provenance": self.provenance,
            "excluded_component_classes": list(self.excluded_component_classes),
            "active": True,
            "executed": executed,
        }


@dataclass(frozen=True)
class DenseQueryBundle:
    """RawDense plus an optional auxiliary SemanticDense view."""

    raw: RawDenseQuery
    semantic: SemanticDenseQuery | None

    @classmethod
    def from_semantic_query(cls, question: str, semantic_query: SemanticQuery) -> "DenseQueryBundle":
        semantic = None
        if semantic_query.text != question:
            semantic = SemanticDenseQuery(
                text=semantic_query.text,
                components=list(semantic_query.components),
                excluded_component_classes=list(semantic_query.excluded_component_classes),
            )
        return cls(raw=RawDenseQuery(text=question), semantic=semantic)

    def as_dict(self, *, semantic_executed: bool = False) -> dict[str, Any]:
        return {
            "raw": self.raw.as_dict(),
            "semantic": self.semantic.as_dict(executed=semantic_executed) if self.semantic is not None else None,
            "semantic_active": self.semantic is not None,
            "semantic_executed": semantic_executed and self.semantic is not None,
        }


def build_semantic_query(question: str, plan: RetrievalPlan) -> SemanticQuery:
    components: list[SemanticQueryComponent] = []
    excluded = ["rejected_analyzer_items", "reviewed_expansions", "repository_metadata", "version_metadata"]
    
    diag = getattr(plan, "analysis_diagnostics", {}) or {}
    accepted = diag.get("analyzer_accepted_semantic_delta", {})
    lowered_question = question.casefold()

    concepts = accepted.get("concepts", [])
    for concept in concepts:
        val = concept.get("value")
        if val and val.casefold() not in lowered_question:
            components.append(SemanticQueryComponent(kind="analyzer_concept", value=val, provenance="analyzer_accepted"))

    deterministic_parse = diag.get("deterministic_parse", {})
    fixed_scopes = deterministic_parse.get("fixed", {}).get("concept_scopes", {})
    
    for k, v in fixed_scopes.items():
        if v.casefold() not in lowered_question:
            components.append(SemanticQueryComponent(kind="deterministic_fixed_scope", value=f"{k}={v}", provenance="fixed"))

    accepted_scopes = accepted.get("concept_scopes", [])
    for scope in accepted_scopes:
        k = scope.get("key")
        v = scope.get("value")
        if k not in fixed_scopes and v and v.casefold() not in lowered_question:
            components.append(SemanticQueryComponent(kind="analyzer_scope", value=f"{k}={v}", provenance="analyzer_accepted"))

    text = question
    included_components: list[SemanticQueryComponent] = []
    if components:
        text += "\n\nSemantic focus:\n"
        seen = set()
        unique_components = []
        for c in components:
            if c.value not in seen:
                seen.add(c.value)
                unique_components.append(c)
        def sort_key(c: SemanticQueryComponent) -> tuple[int, str]:
            order = {"analyzer_concept": 0, "analyzer_scope": 1, "deterministic_fixed_scope": 2}
            return (order.get(c.kind, 99), c.value)
        unique_components.sort(key=sort_key)
        for comp in unique_components:
            text += f"{comp.value}\n"
        text = text.strip()
        included_components = unique_components
    
    return SemanticQuery(
        text=text,
        raw_question=question,
        components=included_components,
        excluded_component_classes=excluded
    )


def build_dense_query_bundle(question: str, plan: RetrievalPlan) -> DenseQueryBundle:
    """Build the raw-authoritative dense views from the existing semantic policy."""
    return DenseQueryBundle.from_semantic_query(question, build_semantic_query(question, plan))


_R01_SOURCE_OBLIGATION_INTENTS = frozenset({"algorithm_theory", "algorithm_implementation"})
_PAPER_OBLIGATION_PATTERNS = ("paper", "thesis", "publication", "literature", "journal")
# Multi-word phrases first, then single tokens; the ambiguous bare "which
# source" is deliberately not a sufficient code trigger (an uncertainty or
# background "source" is not source code).
_CODE_OBLIGATION_PATTERNS = (
    "which source file", "which code file", "source code", "which file",
    "source file", "implementation", "implemented", "signature", "macro",
)


def _first_source_obligation_match(question: str, patterns: tuple[str, ...]) -> str | None:
    """Return the first bounded source-request match, or None.

    Multi-word phrases match as phrases; single tokens require word
    boundaries, so substrings inside unrelated words ("thesis" inside
    "hypothesis", "paper" inside "paperless", "macro" inside "macroscopic")
    never create a hard source obligation.
    """
    lowered = question.casefold()
    for pattern in patterns:
        if " " in pattern:
            if pattern in lowered:
                return pattern
        elif re.search(rf"\b{re.escape(pattern)}\b", lowered):
            return pattern
    return None


def _question_grounded_source_obligations(question: str) -> dict[str, Any]:
    """Derive hard paper/code source obligations from the raw user question.

    R01 replacement (F2-A5): for the algorithm-theory/implementation intents
    the intent only selects this question-grounded regime; the raw question
    alone decides which source classes are hard obligations.  Analyzer
    concepts/symbols, plan symbols, page hints, and query expansions are never
    consulted.  Matching is bounded whole-token / explicit-phrase source-
    request matching (F2-A5-R1), so unrelated substrings cannot manufacture a
    hard obligation.
    """
    obligations: list[str] = []
    matches: list[dict[str, str]] = []
    for source_type, patterns in (
        ("paper", _PAPER_OBLIGATION_PATTERNS),
        ("code", _CODE_OBLIGATION_PATTERNS),
    ):
        hit = _first_source_obligation_match(question, patterns)
        if hit:
            obligations.append(source_type)
            matches.append({"source_type": source_type, "support_span": hit})
    return {"required_source_types": obligations, "matches": matches}


class Retriever:
    def __init__(self, project_root: Path, *, storage: Storage | None = None, vertex: VertexAIClient | None = None) -> None:
        self.project_root = Path(project_root).resolve()
        self.storage = storage or Storage()
        self.vertex = vertex or VertexAIClient(VertexSettings.from_env())
        self.policies = load_retrieval_policies(self.project_root / "configs" / "retrieval_policies.yaml")
        self.query_expansions = load_query_expansions(self.project_root / "configs" / "query_expansions.yaml")
        self.sparse, self.sparse_receipt = create_sparse_encoder(self.project_root)
        self.storage.require_sparse_receipt(self.sparse_receipt)
        self.sparse_vector_name = self.sparse_receipt.vector_name
        manifest = json.loads((self.project_root / "data" / "manifests" / "source_manifest.json").read_text(encoding="utf-8"))
        self.fixed_versions = {item["repo_id"]: item["commit_sha"] for item in manifest["repositories"]}
        self.fixed_refs = {item["repo_id"]: item["ref"] for item in manifest["repositories"]}
        self._paper_versions = {item["doc_id"]: item["sha256"] for item in manifest["papers"]}
        self.context_sources = [item["doc_id"] for item in [*manifest["papers"], *manifest["web_documents"]]]
        self.web_version_tokens = {
            match.group(0).lower()
            for item in manifest["web_documents"]
            for match in re.finditer(r"\b\d{4}(?:-\d{2}-\d{2})?-dev\b", item["entry_url"], re.IGNORECASE)
        }

    def _preparse(
        self,
        question: str,
        *,
        d3_config: D3ExperimentConfig | D3_5ExperimentConfig | None = None,
    ) -> DeterministicQueryParse:
        """Collect only existing raw-query and reviewed knowledge before analysis."""
        parsed = DeterministicQueryParse()
        lowered = question.casefold()

        routed_intent = route_high_confidence_intent(
            question, getattr(self.policies, "intent_routes", None)
        )
        if routed_intent is not None:
            parsed.intent = routed_intent
            parsed.record("intent", source="deterministic_route", rule=routed_intent, value=routed_intent, ownership="fixed")

        named_repositories = [
            repo for repo in self.fixed_versions
            if _has_explicit_repository_reference(question, repo)
        ]
        for repo in named_repositories:
            parsed.target_repositories.append(repo)
            parsed.record("target_repositories", source="explicit_query_reference", rule="manifest_repo_id", value=repo, ownership="known_partial")

        if any(term in lowered for term in ("event_poca", "poca_vertex_file", "restgas_profile")):
            parsed.target_repositories.append("restgas_determination")
            parsed.record("target_repositories", source="legacy_query_rule", rule="restgas_event_poca_terms", value="restgas_determination", ownership="known_partial")

        if "back propagation" in lowered or "回传" in question or "反向传播" in question:
            value = "lmd_to_ip" if "lmd" in lowered else "target_track_to_event_poca"
            parsed.fallback_concept_scopes["back_propagation"] = value
            parsed.record("concept_scopes", source="deterministic_scope", rule="back_propagation", value=value, ownership="fallback")
        if "efficiency" in lowered or "效率" in question:
            value = "longitudinal_profile" if any(term in lowered for term in ("restgas", "profile", "pvz")) else "angular_acceptance"
            parsed.fallback_concept_scopes["efficiency"] = value
            parsed.record("concept_scopes", source="deterministic_scope", rule="efficiency", value=value, ownership="fallback")
        if "angular acceptance" in lowered and "longitudinal efficiency" in lowered:
            parsed.fixed_concept_scopes["efficiency"] = "angular_acceptance_vs_longitudinal_profile"
            parsed.record("concept_scopes", source="deterministic_scope", rule="acceptance_efficiency_comparison", value="angular_acceptance_vs_longitudinal_profile", ownership="fixed")
        if "point-like acceptance" in lowered and "restgas effective acceptance" in lowered:
            parsed.fixed_concept_scopes["acceptance"] = "point_like_vs_restgas_effective"
            parsed.record("concept_scopes", source="deterministic_scope", rule="point_like_restgas_comparison", value="point_like_vs_restgas_effective", ownership="fixed")
        if "lmd-to-ip" in lowered and "event-poca" in lowered:
            parsed.fixed_concept_scopes["back_propagation"] = "lmd_to_ip_vs_target_track_to_event_poca"
            parsed.record("concept_scopes", source="deterministic_scope", rule="back_propagation_comparison", value="lmd_to_ip_vs_target_track_to_event_poca", ownership="fixed")

        try:
            with self.storage.connect() as connection:
                alias_rows = connection.execute(
                    "SELECT alias_text,target_object_id,payload FROM knowledge_aliases WHERE review_status='accepted'"
                ).fetchall()
            for alias_text, target_object_id, payload in alias_rows:
                if alias_text.casefold() in lowered:
                    parsed.resolved_aliases[alias_text] = target_object_id
                    parsed.record("resolved_aliases", source="accepted_alias", rule="review_status=accepted", value=alias_text, ownership="fixed")
                    if payload.get("correction_message"):
                        parsed.premise_corrections.append(payload["correction_message"])
                        parsed.record("premise_corrections", source="accepted_alias", rule="correction_message", value=alias_text, ownership="fixed")
        except Exception:
            pass

        expansion_decision = select_matching_query_expansions(
            question,
            getattr(getattr(self, "query_expansions", None), "rules", []),
            d3_config,
        )
        for rule in expansion_decision.active_matching_rules:
            parsed.matched_expansion_rules.append(rule.rule_id)
            if getattr(rule, "structured_replacement", False):
                parsed.structured_replacement_rules.append(rule.rule_id)
            parsed.symbols.extend(rule.symbols)
            parsed.concepts.extend(rule.concepts)
            parsed.target_repositories.extend(repo for repo in rule.repositories if repo in self.fixed_versions)
            for source_id, pages in rule.paper_page_hints.items():
                parsed.paper_page_hints.setdefault(source_id, []).extend(pages)
            parsed.record("query_expansions", source="reviewed_expansion", rule=rule.rule_id, ownership="fixed_reviewed_rule")
        if d3_config is not None:
            parsed.d3_experiment = expansion_decision.diagnostics(d3_config)

        parsed.explicit_shas = re.findall(r"(?i)\b[0-9a-f]{7,40}\b", question)
        if parsed.explicit_shas and len(named_repositories) == 1:
            repo = named_repositories[0]
            parsed.version_repositories = []
            if _has_explicit_version_repository_binding(question, repo, parsed.explicit_shas[0]):
                parsed.version_repositories = [repo]
                parsed.requested_versions[repo] = parsed.explicit_shas[0]
                parsed.record("requested_versions", source="explicit_version_token", rule="commit_sha", value=repo, ownership="fixed")
        else:
            parsed.version_repositories = named_repositories if len(named_repositories) == 1 else []

        parsed.target_repositories = list(dict.fromkeys(parsed.target_repositories))
        parsed.symbols = list(dict.fromkeys(parsed.symbols))
        parsed.concepts = list(dict.fromkeys(parsed.concepts))
        parsed.premise_corrections = list(dict.fromkeys(parsed.premise_corrections))
        parsed.paper_page_hints = {
            source_id: list(dict.fromkeys(pages))
            for source_id, pages in parsed.paper_page_hints.items()
        }
        return parsed

    def _semantic_output_fields(self, parsed: DeterministicQueryParse) -> list[str]:
        """Return only the semantic-delta fields that can still add query meaning."""
        fields: list[str] = []
        if parsed.intent is None:
            fields.append("intent")
        if len(parsed.target_repositories) < len(self.fixed_versions):
            fields.append("repository_additions")
        fields.extend(("concepts", "symbols"))
        if not (parsed.explicit_shas and parsed.version_repositories):
            fields.append("version_mentions")
        fields.append("concept_scopes")
        return fields

    def analyze(
        self,
        question: str,
        *,
        d3_config: D3ExperimentConfig | D3_5ExperimentConfig | None = None,
    ) -> RetrievalPlan:
        if not question.strip():
            raise ValueError("question cannot be empty")
        if len(question) > 20_000:
            raise ValueError("question exceeds the 20,000 character safety limit")
        parsed = self._preparse(question, d3_config=d3_config)
        semantic_output_fields = self._semantic_output_fields(parsed)
        response_schema = _analysis_schema(
            intent_is_fixed=parsed.intent is not None,
            semantic_output_fields=semantic_output_fields,
        )
        raw_result = self.vertex.generate_json(
            json.dumps(
                {
                    "task": "analyze_retrieval_question",
                    "untrusted_question": question,
                    "deterministic_context": parsed.analyzer_context(semantic_output_fields),
                },
                ensure_ascii=False,
            ),
            response_schema,
            system_instruction=QUERY_ANALYZER_SYSTEM_PROMPT,
        )
        validation = _validate_analyzer_delta(
            question, parsed, raw_result, semantic_output_fields
        )
        delta = validation.delta
        if parsed.intent is not None:
            intent = parsed.intent
        elif delta.intent is not None:
            intent = delta.intent.value
        else:
            raise ValueError("analyzer semantic delta did not provide a grounded intent")
        policy = self.policies.intents[intent]
        scopes = {
            **parsed.fallback_concept_scopes,
            **{item.key: item.value for item in delta.concept_scopes},
            **parsed.fixed_concept_scopes,
        }
        lowered = question.casefold()
        targets = [
            *parsed.target_repositories,
            *(item.value for item in delta.repository_additions),
        ]
        if not targets:
            targets = list(self.fixed_versions)
        targets = list(dict.fromkeys(targets))
        expanded_symbols = [item.value for item in delta.symbols] + parsed.symbols
        expanded_concepts = [item.value for item in delta.concepts] + parsed.concepts
        paper_page_hints = {
            source_id: list(pages)
            for source_id, pages in parsed.paper_page_hints.items()
        }
        # Mixed implementation questions need room for both paper and source
        # evidence.  Keep the first reviewed anchor set contributed by each
        # source; theory-only questions may retain multiple complementary sets.
        if intent == "algorithm_implementation":
            remaining = 3
            limited_hints: dict[str, list[int]] = {}
            for source_id, pages in paper_page_hints.items():
                if remaining <= 0:
                    break
                selected = pages[:remaining]
                if selected:
                    limited_hints[source_id] = selected
                    remaining -= len(selected)
            paper_page_hints = limited_hints
        # Operational, API, and troubleshooting questions should not spend
        # their small evidence budget on thesis anchors.  Papers remain part of
        # the plan for the two intents whose gold policy explicitly requires
        # theoretical/implementation literature.
        if intent not in {"algorithm_theory", "algorithm_implementation"}:
            paper_page_hints = {}
        conflicts = []
        requested_versions = dict(parsed.requested_versions)
        unbound_version_tokens = [
            *validation.unbound_version_tokens,
            *(
                token
                for token in parsed.explicit_shas
                if token.casefold()
                not in {value.casefold() for value in parsed.requested_versions.values()}
            ),
        ]
        for mention in delta.version_mentions:
            if mention.repository is not None:
                requested_versions.setdefault(mention.repository, mention.token)
            else:
                unbound_version_tokens.append(mention.token)
        unbound_version_tokens = list(dict.fromkeys(unbound_version_tokens))
        for repo, requested in requested_versions.items():
            requested_lower = requested.lower()
            is_document_version = any(
                requested_lower == token
                or (
                    requested_lower.endswith("-dev")
                    and token.endswith("-dev")
                    and requested_lower.split("-", 1)[0] == token.split("-", 1)[0]
                )
                for token in getattr(self, "web_version_tokens", set())
            )
            if is_document_version and any(term in lowered for term in ("sphinx", "documentation", "documented", "docs")):
                continue
            locked = self.fixed_versions.get(repo)
            if locked and requested not in {locked, locked[:7], self.fixed_refs[repo]}:
                conflicts.append(f"{repo}: requested {requested}, locked {locked}")
        analysis_diagnostics = {
            "deterministic_parse": parsed.analyzer_context(semantic_output_fields),
            "analyzer_llm_called": True,
            "analyzer_semantic_output_fields": semantic_output_fields,
            "analyzer_raw_semantic_delta": raw_result,
            "analyzer_accepted_semantic_delta": delta.as_dict(),
            "analyzer_rejected_items": validation.rejected_items,
            "analyzer_item_support": {
                field_name: (
                    [values]
                    if isinstance(values, dict) and values.get("support_spans")
                    else [item for item in values if item.get("support_spans")]
                )
                for field_name, values in delta.as_dict().items()
                if (
                    isinstance(values, dict) and values.get("support_spans")
                ) or isinstance(values, list)
            },
            "unbound_version_tokens": unbound_version_tokens,
            "analyzer_final": {
                "intent": intent,
                "target_repositories": targets,
                "concepts": list(dict.fromkeys(expanded_concepts)),
                "symbols": list(dict.fromkeys(expanded_symbols)),
                "requested_versions": requested_versions,
                "concept_scopes": scopes,
            },
        }
        analysis_diagnostics["matched_expansion_rules"] = list(parsed.matched_expansion_rules)
        if parsed.structured_replacement_rules:
            analysis_diagnostics["structured_replacement_rules"] = list(parsed.structured_replacement_rules)
        if parsed.d3_experiment is not None:
            analysis_diagnostics["d3_experiment"] = parsed.d3_experiment
        if intent in _R01_SOURCE_OBLIGATION_INTENTS:
            # F2-A5 (R01): the intent only selects the question-grounded
            # source-obligation regime; the raw question alone decides which
            # source classes are hard obligations.  The retired fixed
            # config mapping (theory -> paper, implementation -> paper+code)
            # no longer carries runtime authority.
            obligation = _question_grounded_source_obligations(question)
            required_source_types = obligation["required_source_types"]
            analysis_diagnostics["source_obligations"] = {
                "mode": "question_grounded_r01",
                "authority": "raw_question",
                **obligation,
            }
        else:
            # R02/HOLD intents retain their existing intent-level policy
            # mapping unchanged (F1 HOLD_UNCERTAIN_PROVENANCE disposition).
            required_source_types = list(policy.required_sources)
            analysis_diagnostics["source_obligations"] = {
                "mode": "retained_intent_policy_r02",
                "authority": "intent_policy",
                "required_source_types": required_source_types,
                "matches": [],
            }
        return RetrievalPlan(
            intent=intent, routing_method="rule" if parsed.intent else "llm", target_repositories=targets,
            resolved_versions={repo: self.fixed_versions[repo] for repo in targets},
            version_conflicts=conflicts,
            concepts=list(dict.fromkeys(expanded_concepts)),
            symbols=list(dict.fromkeys(expanded_symbols)),
            concept_scopes=scopes, source_budgets=policy.source_budgets,
            required_source_types=required_source_types,
            resolved_aliases=parsed.resolved_aliases, premise_corrections=parsed.premise_corrections,
            paper_page_hints={key: list(dict.fromkeys(value)) for key, value in paper_page_hints.items()},
            analysis_diagnostics=analysis_diagnostics,
        )

    @staticmethod
    def _row(row: Any) -> dict[str, Any]:
        keys = ("object_id", "source_id", "source_version_id", "object_type", "title", "text", "authority_level", "locator")
        return dict(zip(keys, row))

    def _exact(self, plan: RetrievalPlan, question: str, limit: int) -> list[dict[str, Any]]:
        terms = [*plan.symbols, *plan.concepts] or re.findall(r"[A-Za-z_][A-Za-z0-9_:./-]{3,}", question)
        rows_by_term: list[list[dict[str, Any]]] = []
        alias_rows: list[dict[str, Any]] = []
        with self.storage.connect() as connection:
            alias_targets = list(plan.resolved_aliases.values())
            if alias_targets:
                alias_rows.extend(
                    self._row(row)
                    for row in connection.execute(
                        "SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator FROM knowledge_objects WHERE object_id=ANY(%s)",
                        (alias_targets,),
                    ).fetchall()
                )
            for term in terms[:24]:
                text_clause = " OR text ILIKE %s" if (
                    any(char.isspace() for char in term)
                    or any(char.isupper() for char in term)
                ) else ""
                query = f"""SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator
                    FROM knowledge_objects
                    WHERE (title ILIKE %s OR canonical_locator ILIKE %s
                           OR locator->>'path' ILIKE %s OR locator->>'symbol' ILIKE %s{text_clause})"""
                wildcard = f"%{term}%"
                params: list[Any] = [wildcard, wildcard, wildcard, wildcard]
                if text_clause:
                    params.append(wildcard)
                if plan.target_repositories:
                    query += " AND source_id = ANY(%s)"
                    params.append([*plan.target_repositories, *self.context_sources, "curated_panda_domain"])
                    query += " AND (NOT (source_id = ANY(%s)) OR source_version_id = ANY(%s))"
                    params.extend([plan.target_repositories, [f"{repo}@{plan.resolved_versions[repo]}" for repo in plan.target_repositories]])
                paper_priority = ""
                if "paper" in plan.required_source_types:
                    paper_priority = "CASE WHEN source_id = ANY(%s) THEN 0 ELSE 1 END, "
                    params.append(["li_2026", "karavdina_2015", "pflueger_2017"])
                query += f""" ORDER BY {paper_priority}CASE
                    WHEN locator->>'path' ILIKE %s AND object_type IN ('sphinx_page','sphinx_page_chunk','source_file','readme_section') THEN 0
                    WHEN title=%s OR locator->>'symbol'=%s THEN 0
                    WHEN locator->>'path' ILIKE %s THEN 1
                    WHEN title ILIKE %s THEN 2
                    WHEN canonical_locator ILIKE %s THEN 3
                    ELSE 4 END, object_id LIMIT 6"""
                params.extend([f"%/{term}", term, term, f"%/{term}", wildcard, wildcard])
                rows_by_term.append([
                    self._row(row) for row in connection.execute(query, params).fetchall()
                ])
        # Round-robin prevents one broad concept from exhausting the channel.
        ordered = list(alias_rows)
        seen = {item["object_id"] for item in ordered}
        for offset in range(6):
            for term_rows in rows_by_term:
                if offset < len(term_rows) and term_rows[offset]["object_id"] not in seen:
                    ordered.append(term_rows[offset])
                    seen.add(term_rows[offset]["object_id"])
                    if len(ordered) >= limit:
                        return ordered
        return ordered[:limit]

    def shadow_resolve(
        self, question: str, plan: RetrievalPlan
    ) -> dict[str, Any]:
        """D2 shadow: conservative concept/entity resolution diagnostics.

        Requires an explicit RetrievalPlan so the shadow never triggers an
        analyzer call.  Read-only: it never calls models, embeddings, or any
        retrieval channel, and production retrieval paths are untouched.
        """
        resolver = EntityResolver(self.storage, context_sources=self.context_sources)
        receipt = resolver.resolve_shadow(
            question,
            plan.model_dump(mode="json") if isinstance(plan, RetrievalPlan) else plan,
        )
        return {"resolution_receipt": receipt.as_dict()}

    def shadow_exact(
        self, question: str, plan: RetrievalPlan
    ) -> dict[str, Any]:
        """C5 shadow: legacy versus entity-first exact, without other channels.

        Requires an explicit RetrievalPlan so the shadow never triggers an
        analyzer call.  Returns the legacy PRE stream, the entity-first POST
        stream, and the entity-resolution receipt; production ``_exact`` is
        untouched.
        """

        limit = 20
        resolver = EntityResolver(self.storage, context_sources=self.context_sources)
        receipt, canonical_prefix = resolver.resolve(
            question,
            plan.model_dump(mode="json") if isinstance(plan, RetrievalPlan) else plan,
        )
        legacy_rows = self._exact(plan, question, limit)
        post_rows = merge_exact_streams(canonical_prefix, legacy_rows, limit)
        return {
            "pre": legacy_rows,
            "legacy_exact_candidates": legacy_rows,
            "post": post_rows,
            "entity_first_exact_candidates": post_rows,
            "entity_resolution_receipt": receipt.as_dict(),
        }

    def _query_filter(self, plan: RetrievalPlan) -> models.Filter | None:
        query_filter = None
        if plan.target_repositories:
            version_scopes = [
                models.Filter(must=[
                    models.FieldCondition(key="source_id", match=models.MatchValue(value=repo)),
                    models.FieldCondition(key="source_version_id", match=models.MatchValue(value=f"{repo}@{plan.resolved_versions[repo]}")),
                ])
                for repo in plan.target_repositories
            ]
            version_scopes.append(models.FieldCondition(key="source_id", match=models.MatchAny(any=[*self.context_sources, "curated_panda_domain"])))
            query_filter = models.Filter(should=version_scopes)

        return query_filter

    def _dense_query(
        self,
        text: str,
        query_filter: models.Filter | None,
        limit: int,
    ) -> tuple[list[Any], list[float]]:
        vector = self.vertex.embed_query(text)
        common = dict(
            collection_name=self.storage.settings.collection_name,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )
        hits = self.storage.qdrant.query_points(query=vector, using="dense", **common).points
        return hits, vector

    def _sparse_query(
        self,
        text: str,
        query_filter: models.Filter | None,
        limit: int,
    ) -> list[Any]:
        """Encode and query one sparse text with the authoritative index contract."""
        encoded = next(iter(self.sparse.query_embed(text)))
        indices = (
            encoded.indices.tolist()
            if hasattr(encoded.indices, "tolist")
            else list(encoded.indices)
        )
        values = (
            encoded.values.tolist()
            if hasattr(encoded.values, "tolist")
            else list(encoded.values)
        )
        common = dict(
            collection_name=self.storage.settings.collection_name,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )
        return self.storage.qdrant.query_points(
            query=models.SparseVector(indices=indices, values=values),
            using=self.sparse_vector_name,
            **common,
        ).points

    def _vector(self, question: str, plan: RetrievalPlan, limit: int) -> tuple[list[Any], list[Any], list[float], SemanticQuery]:
        query_filter = self._query_filter(plan)
        semantic_query = build_semantic_query(question, plan)
        dense_bundle = DenseQueryBundle.from_semantic_query(question, semantic_query)
        dense_hits, dense = self._dense_query(dense_bundle.raw.text, query_filter, limit)
        # RawSparse remains production-authoritative until C4 acceptance.
        sparse_hits = self._sparse_query(question, query_filter, limit)
        return dense_hits, sparse_hits, dense, semantic_query

    def shadow_dense(
        self,
        question: str,
        plan: RetrievalPlan | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Execute RawDense and optional SemanticDense without other channels."""
        if plan is None:
            raise ValueError("shadow_dense requires an existing RetrievalPlan")
        limit = limit if limit is not None else self.policies.candidate_pool_per_channel
        query_filter = self._query_filter(plan)
        semantic_query = build_semantic_query(question, plan)
        dense_bundle = DenseQueryBundle.from_semantic_query(question, semantic_query)

        raw_hits, _ = self._dense_query(dense_bundle.raw.text, query_filter, limit)
        semantic_hits: list[Any] = []
        if dense_bundle.semantic is not None:
            semantic_hits, _ = self._dense_query(dense_bundle.semantic.text, query_filter, limit)

        return {
            "dense_queries": dense_bundle.as_dict(semantic_executed=dense_bundle.semantic is not None),
            "dense_candidates": {
                "raw": [hit.payload for hit in raw_hits],
                "semantic": [hit.payload for hit in semantic_hits] if dense_bundle.semantic is not None else None,
            },
        }

    def shadow_sparse(
        self,
        question: str,
        plan: RetrievalPlan | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Execute RawSparse and LexicalSparse independently without other channels."""
        if plan is None:
            raise ValueError("shadow_sparse requires an existing RetrievalPlan")
        limit = limit if limit is not None else self.policies.candidate_pool_per_channel
        query_filter = self._query_filter(plan)
        lexical_query = build_lexical_query(question, plan)
        lexical_payload = lexical_query.as_dict()

        raw_hits = self._sparse_query(question, query_filter, limit)
        lexical_hits = self._sparse_query(lexical_query.text, query_filter, limit)

        return {
            "lexical_query": lexical_payload,
            "sparse_queries": {
                "raw": {"text": question, "provenance": "user_raw", "active": True},
                "lexical": lexical_payload,
                "lexical_active": True,
                "lexical_executed": True,
            },
            "sparse_candidates": {
                "raw": [hit.payload for hit in raw_hits],
                "lexical": [hit.payload for hit in lexical_hits],
            },
        }

    def _paper(self, query_vector: list[float], plan: RetrievalPlan, limit: int) -> list[dict[str, Any]]:
        """Retrieve paper evidence independently for paper-required plans.

        A normal mixed-source vector query can let a highly similar page from one
        thesis crowd out the other papers.  The paper channel gives each locked
        thesis its own retrieval budget, while retaining the same version gate.
        This is a retrieval diversification measure, not a benchmark-specific
        page lookup.
        """
        if "paper" not in plan.required_source_types:
            return []
        paper_ids = ["li_2026", "karavdina_2015", "pflueger_2017"]
        rows_by_source: list[list[dict[str, Any]]] = []
        for source_id in paper_ids:
            version = self._paper_versions.get(source_id)
            if not version:
                continue
            hinted: list[dict[str, Any]] = []
            pages = plan.paper_page_hints.get(source_id, [])
            if pages:
                with self.storage.connect() as connection:
                    for page in pages:
                        rows = connection.execute(
                            """SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator
                               FROM knowledge_objects
                               WHERE source_id=%s AND source_version_id=%s AND locator->>'pdf_page'=%s
                               ORDER BY length(text) DESC, object_id
                               LIMIT 1""",
                            (source_id, f"{source_id}@{version}", str(page)),
                        ).fetchall()
                        hinted.extend(self._row(row) for row in rows)
            query_filter = models.Filter(must=[
                models.FieldCondition(key="source_id", match=models.MatchValue(value=source_id)),
                models.FieldCondition(key="source_version_id", match=models.MatchValue(value=f"{source_id}@{version}")),
            ])
            hits = self.storage.qdrant.query_points(
                collection_name=self.storage.settings.collection_name,
                query=query_vector,
                using="dense",
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            ).points
            seen = {item["object_id"] for item in hinted}
            rows_by_source.append([*hinted, *[hit.payload for hit in hits if hit.payload["object_id"] not in seen]])
        merged: list[dict[str, Any]] = []
        seen: set[str] = set()
        for offset in range(limit):
            for rows in rows_by_source:
                if offset < len(rows) and rows[offset]["object_id"] not in seen:
                    merged.append(rows[offset])
                    seen.add(rows[offset]["object_id"])
        return merged

    def _workflow(self, question: str, plan: RetrievalPlan, limit: int) -> list[dict[str, Any]]:
        terms = re.findall(r"[A-Za-z_][A-Za-z0-9_.-]{3,}", question)
        if not terms:
            return []
        pattern = "|".join(re.escape(term) for term in terms[:10])
        with self.storage.connect() as connection:
            rows = connection.execute("""SELECT k.object_id,k.source_id,k.source_version_id,k.object_type,k.title,k.text,k.authority_level,k.locator
                FROM workflow_steps w JOIN knowledge_objects k ON k.object_id=w.payload->>'entrypoint_object_id'
                WHERE w.payload::text ~* %s
                  AND k.source_id=ANY(%s)
                  AND (NOT (k.source_id=ANY(%s)) OR k.source_version_id=ANY(%s))
                LIMIT %s""", (pattern, [*plan.target_repositories,*self.context_sources,"curated_panda_domain"], plan.target_repositories, [f"{repo}@{plan.resolved_versions[repo]}" for repo in plan.target_repositories], limit)).fetchall()
        results = [self._row(row) for row in rows]
        if "workflow" not in plan.required_source_types:
            return results
        if any(item.get("object_type") == "workflow" for item in results):
            return results
        # Some Chinese or identifier-heavy questions do not share literal
        # words with the normalized workflow payload.  A bounded fallback keeps
        # the workflow channel usable without broadening code retrieval.
        with self.storage.connect() as connection:
            fallback = connection.execute("""SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator
                FROM knowledge_objects
                WHERE source_id='curated_panda_domain' AND object_type='workflow'
                ORDER BY object_id
                LIMIT %s""", (limit,)).fetchall()
        return [self._row(row) for row in fallback]

    def _graph(self, seeds: list[dict[str, Any]], plan: RetrievalPlan, limit: int) -> list[dict[str, Any]]:
        ids = [item["object_id"] for item in seeds[:limit]]
        if not ids:
            return []
        allowed_sources=[*plan.target_repositories,*self.context_sources,"curated_panda_domain"]
        resolved_versions=[f"{repo}@{plan.resolved_versions[repo]}" for repo in plan.target_repositories]
        with self.storage.connect() as connection:
            rows = connection.execute("""WITH RECURSIVE walk(node_id,depth,path) AS (
                  SELECT DISTINCT
                    CASE WHEN r.subject_id=ANY(%s) THEN r.object_id ELSE r.subject_id END,
                    1,
                    ARRAY[
                      CASE WHEN r.subject_id=ANY(%s) THEN r.subject_id ELSE r.object_id END,
                      CASE WHEN r.subject_id=ANY(%s) THEN r.object_id ELSE r.subject_id END
                    ]
                  FROM relation_edges r
                  WHERE r.review_status='accepted'
                    AND (r.subject_id=ANY(%s) OR r.object_id=ANY(%s))
                  UNION ALL
                  SELECT
                    CASE WHEN r.subject_id=w.node_id THEN r.object_id ELSE r.subject_id END,
                    w.depth+1,
                    w.path || CASE WHEN r.subject_id=w.node_id THEN r.object_id ELSE r.subject_id END
                  FROM walk w JOIN relation_edges r
                    ON r.subject_id=w.node_id OR r.object_id=w.node_id
                  WHERE r.review_status='accepted' AND w.depth < %s
                    AND NOT (CASE WHEN r.subject_id=w.node_id THEN r.object_id ELSE r.subject_id END = ANY(w.path))
                )
                SELECT DISTINCT k.object_id,k.source_id,k.source_version_id,k.object_type,k.title,k.text,k.authority_level,k.locator
                FROM walk w JOIN knowledge_objects k ON k.object_id=w.node_id
                WHERE NOT (k.object_id=ANY(%s))
                  AND k.source_id=ANY(%s)
                  AND (NOT (k.source_id=ANY(%s)) OR k.source_version_id=ANY(%s))
                LIMIT %s""", (ids,ids,ids,ids,ids,self.policies.max_relation_hops,ids,allowed_sources,plan.target_repositories,resolved_versions,limit)).fetchall()
        results = [self._row(row) for row in rows]
        if results or "graph" not in plan.required_source_types:
            return results
        # Curated architecture objects are a bounded fallback when accepted
        # relation edges are sparse for a structural query.
        with self.storage.connect() as connection:
            fallback = connection.execute("""SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator
                FROM knowledge_objects
                WHERE source_id='curated_panda_domain'
                  AND object_type IN ('document','repository','subsystem','concept')
                ORDER BY object_id
                LIMIT %s""", (limit,)).fetchall()
        return [self._row(row) for row in fallback]

    @staticmethod
    def _source_type(item: dict[str, Any]) -> str:
        return _source_type_of(item)

    @staticmethod
    def _validate_d3_plan(
        plan: RetrievalPlan,
        config: D3ExperimentConfig | D3_5ExperimentConfig,
    ) -> dict[str, Any]:
        diagnostics = plan.analysis_diagnostics.get("d3_experiment")
        if not isinstance(diagnostics, dict):
            raise ValueError(
                "an externally supplied D3 plan must be produced with the same D3 config"
            )
        expected = {
            "d3_arm": config.arm.value,
            "selected_rule_ids": list(config.selected_rule_ids),
            "structured_treatment_enabled": config.structured_treatment_enabled,
            "bridge_enabled": config.bridge_enabled,
            "selected_legacy_rules_suppressed": config.selected_legacy_rules_suppressed,
        }
        for key, value in expected.items():
            actual = diagnostics.get(key, False) if key == "bridge_enabled" else diagnostics.get(key)
            if actual != value:
                raise ValueError("D3 plan/config mismatch")
        return diagnostics

    def _collect_channel_rankings(
        self,
        question: str,
        plan: RetrievalPlan,
        limit: int,
    ) -> tuple[dict[str, list[dict[str, Any]]], SemanticQuery, list[float]]:
        rankings: dict[str, list[dict[str, Any]]] = {"exact": self._exact(plan, question, limit)}
        dense, sparse, query_vector, semantic_query = self._vector(question, plan, limit)
        rankings["dense"] = [hit.payload for hit in dense]
        rankings["sparse"] = [hit.payload for hit in sparse]
        paper = self._paper(query_vector, plan, limit)
        if paper:
            rankings["paper"] = paper
        rankings["workflow"] = self._workflow(question, plan, limit)
        rankings["graph"] = self._graph([*rankings["exact"],*rankings["dense"],*rankings["sparse"]], plan, limit)
        return rankings, semantic_query, query_vector

    def _apply_structured_replacement(
        self,
        question: str,
        plan: RetrievalPlan,
        rankings: dict[str, list[dict[str, Any]]],
        rerank_pool: list[str],
        payloads: dict[str, dict[str, Any]],
    ) -> tuple[list[str], list[str], dict[str, Any] | None]:
        diagnostics = plan.analysis_diagnostics or {}
        rules = getattr(getattr(self, "query_expansions", None), "rules", [])
        if "matched_expansion_rules" in diagnostics:
            matched_set = set(diagnostics["matched_expansion_rules"])
        else:
            # Normal caller-supplied plans may predate policy diagnostics.
            matched_set = {
                rule.rule_id for rule in
                select_matching_query_expansions(question, rules, None).active_matching_rules
            }
        active_migrated_rules = [
            rule.rule_id for rule in rules
            if rule.rule_id in matched_set and getattr(rule, "structured_replacement", False)
        ]

        if not active_migrated_rules:
            return rerank_pool, [], None

        structured_contribution = build_structured_contribution_from_storage(
            question,
            plan,
            storage=getattr(self, "storage", None),
            context_sources=getattr(self, "context_sources", None),
            max_relation_hops=min(2, getattr(getattr(self, "policies", None), "max_relation_hops", 2)),
            bridge_enabled=True,
        )
        for oid, cand_payload in structured_contribution.bridged_payloads.items():
            if oid not in payloads:
                payloads[oid] = cand_payload

        eligible_candidates = build_eligible_bridge_candidates(
            structured_contribution.bridge_receipts,
            structured_contribution.reachability_receipts,
            object_lookup=structured_contribution.bridged_payloads,
        )
        # Selectivity uses source-native text even when an ordinary
        # channel already supplied a different projection of this object.
        payload_registry = build_candidate_payload_registry(
            eligible_candidates,
            structured_contribution.bridged_payloads,
        )
        unbridged_graph = rankings.get("graph", [])
        unbridged_graph_ids = [
            item["object_id"] if isinstance(item, dict) else str(item)
            for item in unbridged_graph
        ]
        channel_orderings = {
            ch: [item["object_id"] if isinstance(item, dict) else str(item) for item in items]
            for ch, items in rankings.items()
        }
        v2_result = select_structured_candidates_v2(
            question,
            plan,
            eligible_candidates,
            payload_registry,
            channels=channel_orderings,
            unbridged_graph=unbridged_graph_ids,
        )
        v2_selected_order = v2_result.get("selected_object_ids", [])
        reservable = reservable_bridge(v2_selected_order, rerank_pool)
        treatment_pool = build_treatment_pool(rerank_pool, reservable, k=3)
        displaced_ids = treatment_pool.get("displaced_object_ids", [])
        reserved_ids = treatment_pool.get("reserved_bridge_candidate_ids", [])
        new_rerank_pool = treatment_pool.get("treatment_pool_object_ids", rerank_pool)

        reserved_set = set(reserved_ids)
        rerank_pool_set = set(rerank_pool)
        eligible_supplemental_ids = [
            oid for oid in v2_selected_order
            if oid in reserved_set or oid in rerank_pool_set
        ]

        resolution_receipt = structured_contribution.resolution_receipt
        if hasattr(resolution_receipt, "as_dict"):
            resolution_receipt = resolution_receipt.as_dict()

        structured_replacement_receipt = {
            "active_migrated_rule_ids": list(active_migrated_rules),
            "governed_resolution_receipt": resolution_receipt,
            "reachability_receipts_count": len(structured_contribution.reachability_receipts),
            "reachability_receipts": [
                r.as_dict() if hasattr(r, "as_dict") else r
                for r in structured_contribution.reachability_receipts
            ],
            "bridge_receipts_count": len(structured_contribution.bridge_receipts),
            "bridge_receipts": [
                b.as_dict() if hasattr(b, "as_dict") else b
                for b in structured_contribution.bridge_receipts
            ],
            "eligible_candidate_count": len(eligible_candidates),
            "eligible_candidates": eligible_candidates,
            "selectivity_policy_version": v2_result.get("policy_version", SELECTIVITY_POLICY_VERSION),
            "selected_candidate_ids": v2_selected_order,
            "candidate_selectivity_receipts": v2_result.get("candidate_receipts", []),
            "selected_rank_keys": v2_result.get("selected_rank_keys", []),
            "reservable_ids": reservable,
            "reserved_ids": reserved_ids,
            "eligible_supplemental_ids": eligible_supplemental_ids,
            "displaced_ordinary_ids": displaced_ids,
            "k": 3,
            "final_rerank_pool_ids": list(new_rerank_pool),
        }
        return new_rerank_pool, eligible_supplemental_ids, structured_replacement_receipt

    def retrieve(
        self,
        question: str,
        plan: RetrievalPlan | None = None,
        *,
        d3_config: D3ExperimentConfig | D3_5ExperimentConfig | None = None,
        capture_candidates: bool = False,
    ) -> dict[str, Any]:
        plan_was_supplied = plan is not None
        plan = plan or self.analyze(question, d3_config=d3_config)
        d3_diagnostics: dict[str, Any] | None = None
        if d3_config is not None:
            d3_diagnostics = self._validate_d3_plan(plan, d3_config)
        elif plan_was_supplied and "d3_experiment" in plan.analysis_diagnostics:
            raise ValueError("a D3 plan requires its explicit D3 config at retrieval time")
        limit = self.policies.candidate_pool_per_channel
        rankings, semantic_query, query_vector = self._collect_channel_rankings(question, plan, limit)
        structured_contribution = None
        if d3_config is not None and d3_config.structured_treatment_enabled:
            structured_contribution = build_structured_contribution_from_storage(
                question,
                plan,
                storage=self.storage,
                context_sources=self.context_sources,
                max_relation_hops=min(2, self.policies.max_relation_hops),
                bridge_enabled=d3_config.bridge_enabled,
            )
            before_graph = list(rankings["graph"])
            unbridged_graph = merge_exact_streams(
                structured_contribution.candidates,
                before_graph,
                limit,
            )
            if d3_config.bridge_enabled:
                rankings["graph"] = merge_exact_streams(
                    structured_contribution.bridged_candidates,
                    unbridged_graph,
                    limit,
                )
                structured_contribution.compute_displacement_diagnostics(
                    before_graph=unbridged_graph,
                    after_graph=rankings["graph"],
                    bridged_candidates=structured_contribution.bridged_candidates,
                )
            else:
                rankings["graph"] = unbridged_graph
                structured_contribution.displacement_diagnostics = {
                    "bridged_candidate_count": 0,
                    "graph_candidates_before_bridge": len(before_graph),
                    "graph_candidates_after_bridge": len(rankings["graph"]),
                    "graph_candidates_displaced_by_prefix": 0,
                    "displaced_object_ids": [],
                    "bridged_candidate_ids": [],
                    "deduplicated_overlap_count": 0,
                }
        scores: dict[str, float] = defaultdict(float)
        payloads: dict[str, dict[str, Any]] = {}
        channels: dict[str, list[str]] = defaultdict(list)
        weights = {"exact": 2.0, "dense": 1.0, "sparse": 1.0, "paper": 1.15, "workflow": 1.2, "graph": 0.8}
        for channel, items in rankings.items():
            for rank, item in enumerate(items):
                oid = item["object_id"]
                scores[oid] += weights[channel] / (60 + rank + 1)
                payloads[oid] = item
                channels[oid].append(channel)
        fused_order = sorted(scores, key=scores.get, reverse=True)
        rerank_pool = fused_order[:30]
        structured_replacement_receipt: dict[str, Any] | None = None
        supplemental_candidates: list[dict[str, Any]] = []
        if d3_config is None:
            rerank_pool, eligible_supplemental_ids, structured_replacement_receipt = self._apply_structured_replacement(
                question, plan, rankings, rerank_pool, payloads
            )
            for oid in eligible_supplemental_ids:
                if oid in payloads:
                    supplemental_candidates.append(dict(payloads[oid]))

        rerank_payload = [{"object_id":oid,"title":payloads[oid].get("title"),"source_id":payloads[oid].get("source_id"),"text":payloads[oid].get("text","")[:2000]} for oid in rerank_pool]
        rerank_schema = {"type":"object","properties":{"ranked_object_ids":{"type":"array","items":{"type":"string","enum":rerank_pool}}},"required":["ranked_object_ids"],"additionalProperties":False}
        reranked = self.vertex.generate_json(
            json.dumps({"task": "rerank_evidence", "untrusted_question": question, "untrusted_candidates": rerank_payload}, ensure_ascii=False),
            rerank_schema,
            system_instruction=RERANK_SYSTEM_PROMPT,
        )["ranked_object_ids"] if rerank_pool else []
        ordered, ranked_object_ids, selected, excluded, backfill_admissions, symbol_first = self._prioritize_and_select_evidence(
            question=question,
            plan=plan,
            ordered=list(dict.fromkeys([*reranked, *rerank_pool, *fused_order])),
            payloads=payloads,
            scores=scores,
            channels=channels,
            exact_candidates=rankings.get("exact", []),
            final_evidence_limit=self.policies.final_evidence_limit,
        )
        lexical_query = build_lexical_query(question, plan)
        lexical_payload = lexical_query.as_dict()
        result = {
            "plan": plan.model_dump(mode="json"),
            "semantic_query": semantic_query.as_dict(),
            "lexical_query": lexical_payload,
            "dense_queries": DenseQueryBundle.from_semantic_query(question, semantic_query).as_dict(),
            "dense_candidates": {
                "raw": rankings["dense"],
                "semantic": None,
            },
            "sparse_queries": {
                "raw": {"text": question, "provenance": "user_raw", "active": True},
                "lexical": lexical_payload,
                "lexical_active": True,
                "lexical_executed": False,
            },
            "sparse_candidates": {
                "raw": rankings["sparse"],
                "lexical": None,
            },
            "rankings": {key: [item["object_id"] for item in value] for key, value in rankings.items()},
            "fusion_scores": {oid: scores[oid] for oid in sorted(scores, key=scores.get, reverse=True)[:30]},
            "reranked_object_ids": reranked,
            "ranked_object_ids": ranked_object_ids,
            "excluded": excluded,
            "backfill_admissions": backfill_admissions,
            "evidence": [item.model_dump(mode="json") for item in selected],
        }
        if capture_candidates:
            result["candidate_snapshot"] = {
                "pass_origin": "initial",
                "rankings": {key: [dict(item) for item in value] for key, value in rankings.items()},
                "supplemental_candidates": supplemental_candidates,
            }
        if structured_replacement_receipt is not None:
            result["structured_replacement"] = structured_replacement_receipt
        if d3_config is not None and d3_diagnostics is not None:
            counters = dict(d3_diagnostics.get("diagnostic_counters") or {})
            d3_receipt: dict[str, Any] = {
                "d3_arm": d3_config.arm.value,
                "selected_rule_ids": list(d3_config.selected_rule_ids),
                "structured_treatment_enabled": d3_config.structured_treatment_enabled,
                "bridge_enabled": d3_config.bridge_enabled,
                "selected_legacy_rules_suppressed": d3_config.selected_legacy_rules_suppressed,
                "suppressed_selected_rule_ids": list(
                    d3_diagnostics.get("suppressed_selected_rule_ids") or []
                ),
            }
            if structured_contribution is not None:
                counters.update(structured_contribution.diagnostic_counters)
                d3_receipt.update(structured_contribution.as_dict())
            d3_receipt["diagnostic_counters"] = counters
            result["d3_experiment"] = d3_receipt
        return result

    def _prioritize_and_select_evidence(
        self,
        question: str,
        plan: RetrievalPlan,
        ordered: list[str],
        payloads: dict[str, dict[str, Any]],
        scores: dict[str, float],
        channels: dict[str, list[str]],
        exact_candidates: list[dict[str, Any]],
        final_evidence_limit: int,
    ) -> tuple[list[str], list[str], list[Evidence], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
        preferred_sources = list(plan.target_repositories)
        lowered_question = question.casefold()
        if any(term in lowered_question for term in ("restgas", "off-ip", "event_poca", "poca", "displaced")):
            preferred_sources = ["restgas_determination", "pandaroot", "luminosityfit", *preferred_sources]
        elif "pandaroot" in lowered_question:
            preferred_sources = ["pandaroot", "restgas_determination", "luminosityfit", *preferred_sources]
        preferred_sources = list(dict.fromkeys(preferred_sources))
        source_rank = {source_id: rank for rank, source_id in enumerate(preferred_sources)}
        symbol_first = []

        def symbol_order(value: str) -> tuple[int, int]:
            normalized = value.replace("\\", "/").lower()
            if plan.intent == "troubleshooting" and ("readme" in normalized or "running/" in normalized):
                return (0, 0)
            return (1, 0 if "/" in value or "." in value else 1)

        symbols = sorted(plan.symbols, key=symbol_order)
        for symbol in symbols:
            literal = symbol.replace("*", "").replace("?", "")
            matches = []
            for item in exact_candidates:
                locator = item.get("locator") or {}
                if literal and (
                    literal in (item.get("title") or "")
                    or literal in (locator.get("symbol") or "")
                    or literal in (locator.get("path") or "")
                    or literal in (item.get("text") or "")
                ):
                    matches.append(item)
            if matches:
                def match_priority(item: dict[str, Any]) -> tuple[int, int, int, str]:
                    locator = item.get("locator") or {}
                    path = (locator.get("path") or "").replace("\\", "/")
                    exact_path = int(bool(literal and (
                        path == literal
                        or ("/" in literal and path.endswith("/" + literal))
                    )))
                    page_level = int(item.get("object_type") in {"sphinx_page", "source_file", "readme_section"})
                    return (source_rank.get(item.get("source_id"), 999), -exact_path, -page_level, item["object_id"])
                matches.sort(key=match_priority)
                symbol_first.append(matches[0]["object_id"])

        required_first = []
        for required in plan.required_source_types:
            for oid in ordered:
                source_type = self._source_type(payloads[oid])
                if source_type == required or (required in {"workflow", "graph"} and required in channels.get(oid, [])):
                    required_first.append(oid)
                    break

        hinted_first = []
        for oid in ordered:
            item = payloads[oid]
            source_id = item.get("source_id")
            page = (item.get("locator") or {}).get("pdf_page")
            if source_id in plan.paper_page_hints and page is not None and int(page) in plan.paper_page_hints[source_id]:
                hinted_first.append(oid)

        ordered = list(dict.fromkeys([*hinted_first, *required_first, *symbol_first, *ordered]))
        ranked_object_ids = ordered[:30]
        selected, excluded, backfill_admissions = select_final_evidence(
            ordered,
            payloads,
            scores,
            channels,
            plan,
            final_evidence_limit,
            set(symbol_first),
        )
        return ordered, ranked_object_ids, selected, excluded, backfill_admissions, symbol_first

    def collect_channel_candidates(
        self,
        question: str,
        plan: RetrievalPlan,
    ) -> dict[str, Any]:
        """Collect bounded channel candidates without LLM reranking or final selection."""
        limit = self.policies.candidate_pool_per_channel
        rankings, _, _ = self._collect_channel_rankings(question, plan, limit)
        rankings_copy = {key: [dict(item) for item in value] for key, value in rankings.items()}

        payloads: dict[str, dict[str, Any]] = {}
        scores: dict[str, float] = defaultdict(float)
        weights = {"exact": 2.0, "dense": 1.0, "sparse": 1.0, "paper": 1.15, "workflow": 1.2, "graph": 0.8}
        for channel, items in rankings.items():
            for rank, item in enumerate(items):
                oid = item["object_id"]
                scores[oid] += weights[channel] / (60 + rank + 1)
                payloads[oid] = dict(item)
        fused_order = sorted(scores, key=scores.get, reverse=True)
        local_rerank_pool = fused_order[:30]

        _, eligible_supplemental_ids, _ = self._apply_structured_replacement(
            question, plan, rankings, local_rerank_pool, payloads
        )
        supplemental = [dict(payloads[oid]) for oid in eligible_supplemental_ids if oid in payloads]
        return {
            "rankings": rankings_copy,
            "supplemental_candidates": supplemental,
        }

    def consolidate_and_select_candidates(
        self,
        original_question: str,
        plan: RetrievalPlan,
        pass_snapshots: list[dict[str, Any]],
        current_selected_evidence: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Global candidate consolidation and selection across all executed passes.

        Consolidates candidate occurrences across initial, pre-answer targeted,
        and E3 targeted passes by object_id using minimum rank per channel,
        frozen weighted RRF, single global LLM rerank (original question only),
        and authoritative policy selection (select_final_evidence).
        """
        if isinstance(plan, dict):
            plan = RetrievalPlan.model_validate(plan)

        if not pass_snapshots:
            return {
                "status": "empty_candidates",
                "failure_reason": "no pass snapshots provided",
                "selected_evidence": [dict(x) for x in (current_selected_evidence or [])],
                "newly_admitted_object_ids": [],
                "displaced_evidence_ids": [],
                "fused_candidate_ids": [],
                "reranked_object_ids": [],
                "ranked_object_ids": [],
                "best_channel_ranks": {},
                "scores": {},
                "payloads": {},
                "pass_occurrences": {},
            }

        payloads: dict[str, dict[str, Any]] = {}
        best_ranks: dict[str, dict[str, int]] = defaultdict(dict)
        pass_occurrences: dict[str, list[dict[str, Any]]] = defaultdict(list)
        consistency_failures: list[str] = []
        eligible_supplemental_ids: list[str] = []

        for p_idx, snapshot in enumerate(pass_snapshots):
            pass_origin = snapshot.get("pass_origin", f"pass_{p_idx}")
            pass_rankings = snapshot.get("rankings", {})
            for channel, items in pass_rankings.items():
                for rank, item in enumerate(items, 1):
                    oid = item.get("object_id")
                    if not oid:
                        continue
                    if oid in payloads:
                        prev = payloads[oid]
                        mismatches = []
                        if prev.get("source_id") != item.get("source_id"):
                            mismatches.append(f"source_id: {prev.get('source_id')} vs {item.get('source_id')}")
                        if prev.get("source_version_id") != item.get("source_version_id"):
                            mismatches.append(f"source_version_id: {prev.get('source_version_id')} vs {item.get('source_version_id')}")
                        prev_loc = json.dumps(prev.get("locator") or {}, sort_keys=True)
                        item_loc = json.dumps(item.get("locator") or {}, sort_keys=True)
                        if prev_loc != item_loc:
                            mismatches.append("locator mismatch")
                        if (prev.get("text") or "") != (item.get("text") or ""):
                            mismatches.append("text mismatch")
                        if prev.get("object_type") != item.get("object_type"):
                            mismatches.append(f"object_type: {prev.get('object_type')} vs {item.get('object_type')}")
                        if (prev.get("title") or "") != (item.get("title") or ""):
                            mismatches.append(f"title: {prev.get('title')} vs {item.get('title')}")
                        if mismatches:
                            consistency_failures.append(f"{oid}: {'; '.join(mismatches)}")
                    else:
                        payloads[oid] = dict(item)

                    if channel not in best_ranks[oid] or rank < best_ranks[oid][channel]:
                        best_ranks[oid][channel] = rank
                    pass_occurrences[oid].append({
                        "pass_origin": pass_origin,
                        "channel": channel,
                        "rank": rank,
                    })

            supplemental_items = snapshot.get("supplemental_candidates", [])
            for item in supplemental_items:
                oid = item.get("object_id")
                if not oid:
                    continue
                if oid in payloads:
                    prev = payloads[oid]
                    mismatches = []
                    if prev.get("source_id") != item.get("source_id"):
                        mismatches.append(f"source_id: {prev.get('source_id')} vs {item.get('source_id')}")
                    if prev.get("source_version_id") != item.get("source_version_id"):
                        mismatches.append(f"source_version_id: {prev.get('source_version_id')} vs {item.get('source_version_id')}")
                    prev_loc = json.dumps(prev.get("locator") or {}, sort_keys=True)
                    item_loc = json.dumps(item.get("locator") or {}, sort_keys=True)
                    if prev_loc != item_loc:
                        mismatches.append("locator mismatch")
                    if (prev.get("text") or "") != (item.get("text") or ""):
                        mismatches.append("text mismatch")
                    if prev.get("object_type") != item.get("object_type"):
                        mismatches.append(f"object_type: {prev.get('object_type')} vs {item.get('object_type')}")
                    if (prev.get("title") or "") != (item.get("title") or ""):
                        mismatches.append(f"title: {prev.get('title')} vs {item.get('title')}")
                    if mismatches:
                        consistency_failures.append(f"{oid}: {'; '.join(mismatches)}")
                else:
                    payloads[oid] = dict(item)

                if oid not in eligible_supplemental_ids:
                    eligible_supplemental_ids.append(oid)

                pass_occurrences[oid].append({
                    "pass_origin": pass_origin,
                    "channel": "structured_replacement",
                    "rank": None,
                })

        if consistency_failures:
            return {
                "status": "consistency_failure",
                "failure_reason": "; ".join(consistency_failures),
                "consistency_failures": consistency_failures,
                "selected_evidence": [dict(x) for x in (current_selected_evidence or [])],
                "newly_admitted_object_ids": [],
                "displaced_evidence_ids": [],
                "fused_candidate_ids": [],
                "reranked_object_ids": [],
                "ranked_object_ids": [],
                "best_channel_ranks": dict(best_ranks),
                "scores": {},
                "payloads": payloads,
                "pass_occurrences": dict(pass_occurrences),
            }

        if not payloads:
            return {
                "status": "empty_candidates",
                "failure_reason": "no candidates in pass snapshots",
                "selected_evidence": [dict(x) for x in (current_selected_evidence or [])],
                "newly_admitted_object_ids": [],
                "displaced_evidence_ids": [],
                "fused_candidate_ids": [],
                "reranked_object_ids": [],
                "ranked_object_ids": [],
                "best_channel_ranks": {},
                "scores": {},
                "payloads": {},
                "pass_occurrences": {},
            }

        weights = {"exact": 2.0, "dense": 1.0, "sparse": 1.0, "paper": 1.15, "workflow": 1.2, "graph": 0.8}
        rrf_k = 60
        scores: dict[str, float] = {}
        channels: dict[str, list[str]] = {}
        for oid, ch_ranks in best_ranks.items():
            s = 0.0
            for ch, r in ch_ranks.items():
                if ch in weights:
                    s += weights[ch] / (rrf_k + r)
            scores[oid] = s
            channels[oid] = list(ch_ranks.keys())

        for oid in eligible_supplemental_ids:
            if oid not in scores:
                scores[oid] = 0.0
            if oid not in channels:
                channels[oid] = []

        # Deterministic tie-break: object_id lexicographic order
        base_fused_order = sorted(
            [oid for oid in scores if best_ranks.get(oid)],
            key=lambda oid: (-scores[oid], oid),
        )

        # Combine per-pass bounded eligible union, reserve space for that union within 30 then fill base RRF, dedup by object.
        supp_pool = list(dict.fromkeys(eligible_supplemental_ids))[:30]
        supp_set = set(supp_pool)
        base_slots = max(0, 30 - len(supp_pool))
        base_candidates = [oid for oid in base_fused_order if oid not in supp_set][:base_slots]
        rerank_pool = base_candidates + supp_pool

        fused_order = list(dict.fromkeys([*base_fused_order, *eligible_supplemental_ids]))

        # Single Global LLM Rerank: question MUST be original question only
        rerank_payload = [
            {
                "object_id": oid,
                "title": payloads[oid].get("title"),
                "source_id": payloads[oid].get("source_id"),
                "text": (payloads[oid].get("text") or "")[:2000],
            }
            for oid in rerank_pool
        ]
        rerank_schema = {
            "type": "object",
            "properties": {
                "ranked_object_ids": {
                    "type": "array",
                    "items": {"type": "string", "enum": rerank_pool},
                }
            },
            "required": ["ranked_object_ids"],
            "additionalProperties": False,
        }
        reranked = (
            self.vertex.generate_json(
                json.dumps(
                    {
                        "task": "rerank_evidence",
                        "untrusted_question": original_question,
                        "untrusted_candidates": rerank_payload,
                    },
                    ensure_ascii=False,
                ),
                rerank_schema,
                system_instruction=RERANK_SYSTEM_PROMPT,
            ).get("ranked_object_ids", [])
            if (rerank_pool and self.vertex is not None)
            else []
        )

        final_evidence_limit = getattr(getattr(self, "policies", None), "final_evidence_limit", 12)

        # E3 exact candidate ordering derived deterministically from best channel ranks
        exact_candidates = [
            payloads[oid]
            for oid in sorted(
                [oid for oid in payloads if "exact" in best_ranks.get(oid, {})],
                key=lambda oid: (best_ranks[oid]["exact"], oid),
            )
        ]
        ordered, ranked_object_ids, selected, excluded, backfill_admissions, symbol_first = self._prioritize_and_select_evidence(
            question=original_question,
            plan=plan,
            ordered=list(dict.fromkeys([*reranked, *rerank_pool, *fused_order])),
            payloads=payloads,
            scores=scores,
            channels=channels,
            exact_candidates=exact_candidates,
            final_evidence_limit=final_evidence_limit,
        )

        prior_selected_object_ids = set()
        prior_evidence_lookup = {}
        if current_selected_evidence:
            for item in current_selected_evidence:
                oid = item.get("object_id")
                if oid:
                    prior_selected_object_ids.add(oid)
                eid = item.get("evidence_id")
                if eid:
                    prior_evidence_lookup[eid] = item

        selected_evidence_dicts = [item.model_dump(mode="json") for item in selected]
        new_selected_object_ids = [item.object_id for item in selected]
        new_admissions = [oid for oid in new_selected_object_ids if oid not in prior_selected_object_ids]
        displaced_evidence_ids = [
            eid for eid, item in prior_evidence_lookup.items()
            if item.get("object_id") not in set(new_selected_object_ids)
        ]

        if current_selected_evidence is not None and not new_admissions:
            status = "no_gain"
            failure_reason = "no_newly_admitted_objects"
        else:
            status = "success"
            failure_reason = None

        return {
            "status": status,
            "selected_evidence": selected_evidence_dicts,
            "newly_admitted_object_ids": new_admissions,
            "displaced_evidence_ids": displaced_evidence_ids,
            "fused_candidate_ids": fused_order,
            "reranked_object_ids": reranked,
            "ranked_object_ids": ordered[:30],
            "best_channel_ranks": dict(best_ranks),
            "scores": scores,
            "payloads": payloads,
            "pass_occurrences": dict(pass_occurrences),
            "failure_reason": failure_reason,
        }
