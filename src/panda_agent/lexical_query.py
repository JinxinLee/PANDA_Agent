"""Pure, bounded lexical-query construction for sparse retrieval.

The lexical query keeps the user's question authoritative.  It can retain
technical anchors already present in that question and append only
provenance-bearing terms from the accepted analyzer delta or resolved alias
keys.  Retrieval, storage, model, and benchmark code intentionally do not
belong in this module.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


LEXICAL_MAX_APPENDED_COMPONENTS = 6
LEXICAL_MAX_APPENDED_TOKENS = 32

_EXCLUDED_COMPONENT_CLASSES = (
    "reviewed_expansions",
    "rejected_analyzer_items",
    "fallback_scopes",
    "paper_page_hints",
    "file_hints",
    "gold_evidence",
    "critical_evidence",
    "hidden_repository_metadata",
    "hidden_version_metadata",
    "target_object_ids",
    "answer_requirements",
    "phrase_to_file_shortcuts",
    "flat_plan_symbols",
    "flat_plan_concepts",
    "c5_canonical_lookup",
)

_KIND_PRIORITY = {
    "raw_identifier": 0,
    "analyzer_symbol": 10,
    "analyzer_concept": 20,
    "accepted_alias": 30,
}

# A technical token may contain the separators commonly used by source
# identifiers and paths.  The pattern deliberately starts and ends on an
# alphanumeric/underscore token rather than consuming surrounding prose.
_TECHNICAL_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(?:[A-Za-z]:[\\/])?[A-Za-z_][A-Za-z0-9_]*"
    r"(?:(?:::|[:./\\-])[A-Za-z0-9_]+)*"
    r"(?![A-Za-z0-9_])"
)
_VERSION_OR_SHA_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(?:v?\d+(?:[._-]\d+)+(?:[-._][A-Za-z0-9]+)*|[0-9A-Fa-f]{7,40})"
    r"(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
_QUERY_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


@dataclass(frozen=True)
class LexicalQueryComponent:
    """One retained or appended lexical anchor and its safe provenance."""

    kind: str
    value: str
    provenance: str
    support_spans: tuple[str, ...] = ()
    appended: bool = False


@dataclass
class LexicalQuery:
    """The raw-authoritative sparse query and its auditable components."""

    text: str
    raw_question: str
    components: list[LexicalQueryComponent]
    excluded_component_classes: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "raw_question": self.raw_question,
            "components": [
                {
                    "kind": component.kind,
                    "value": component.value,
                    "provenance": component.provenance,
                    "support_spans": list(component.support_spans),
                    "appended": component.appended,
                }
                for component in self.components
            ],
            "excluded_component_classes": list(self.excluded_component_classes),
        }


@dataclass(frozen=True)
class _Candidate:
    component: LexicalQueryComponent
    append: bool
    order: int


def _field(value: Any, name: str, default: Any = None) -> Any:
    """Read a field from either a mapping or a RetrievalPlan-shaped object."""

    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _query_tokens(value: str) -> set[str]:
    return {token.casefold() for token in _QUERY_TOKEN_RE.findall(value)}


def _continues_technical_token(text: str, index: int, direction: int) -> bool:
    char = text[index]
    if char.isalnum() or char in "_:/@":
        return True
    if char in ".-":
        neighbor = index + direction
        return 0 <= neighbor < len(text) and (
            text[neighbor].isalnum() or text[neighbor] == "_"
        )
    return False


def _complete_technical_token(token: str, text: str) -> str | None:
    """Return a complete technical token only when it occurs in ``text``."""

    if not token or not isinstance(text, str):
        return None
    for match in re.finditer(re.escape(token), text):
        start, end = match.span()
        if start and _continues_technical_token(text, start - 1, -1):
            continue
        if end < len(text) and _continues_technical_token(text, end, 1):
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


def _support_spans(item: Any, question: str) -> tuple[str, ...] | None:
    raw_spans = _field(item, "support_spans")
    if isinstance(raw_spans, str):
        spans = (raw_spans,)
    elif isinstance(raw_spans, bytes) or not isinstance(raw_spans, Sequence) or not raw_spans:
        return None
    else:
        spans = tuple(raw_spans)
    if any(not isinstance(span, str) or not span or span not in question for span in spans):
        return None
    return spans


def _value(item: Any) -> str | None:
    value = _field(item, "value")
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _symbol_is_grounded(value: str, support_spans: tuple[str, ...], question: str) -> bool:
    if _complete_technical_token(value, question) is None:
        return False
    return any(_complete_technical_token(value, span) is not None for span in support_spans)


def _normalization_key(value: str) -> str:
    return " ".join(value.casefold().split())


def _is_literally_represented(value: str, question: str) -> bool:
    normalized_value = _normalization_key(value)
    if not normalized_value:
        return False
    return normalized_value in _normalization_key(question)


def _looks_like_technical_identifier(value: str) -> bool:
    if any(separator in value for separator in ("_", ":", ".", "/", "\\", "-")):
        return True
    if any(char.isdigit() for char in value):
        return True
    if len(value) >= 2 and value.isupper():
        return True
    # CamelCase and lowerCamelCase are common source identifiers; requiring an
    # internal case transition avoids treating ordinary capitalized prose as a
    # technical anchor.
    return re.search(r"[a-z][A-Z]|[A-Z][A-Z][a-z]", value) is not None


def _raw_identifiers(question: str) -> list[str]:
    matches: list[tuple[int, int, str]] = []
    for pattern in (_TECHNICAL_TOKEN_RE, _VERSION_OR_SHA_RE):
        for match in pattern.finditer(question):
            value = match.group(0)
            if pattern is _TECHNICAL_TOKEN_RE and not _looks_like_technical_identifier(value):
                continue
            matches.append((match.start(), match.end(), value))
    matches.sort(key=lambda item: (item[0], item[1], item[2]))

    identifiers: list[str] = []
    seen: set[str] = set()
    for _, _, value in matches:
        key = _normalization_key(value)
        if key and key not in seen:
            seen.add(key)
            identifiers.append(value)
    return identifiers


def _alias_keys(plan: Any) -> list[str]:
    aliases = _field(plan, "resolved_aliases", {})
    if not isinstance(aliases, Mapping):
        return []
    keys = [key for key in aliases.keys() if isinstance(key, str) and key.strip()]
    return sorted(keys, key=lambda key: (_normalization_key(key), key))


def _accepted_items(plan: Any, field_name: str) -> list[Any]:
    diagnostics = _field(plan, "analysis_diagnostics", {})
    accepted = _field(diagnostics, "analyzer_accepted_semantic_delta", {})
    items = _field(accepted, field_name, [])
    if isinstance(items, (str, bytes)) or not isinstance(items, Sequence):
        return []
    return list(items)


def _candidate_list(question: str, plan: Any) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    order = 0

    for identifier in _raw_identifiers(question):
        candidates.append(
            _Candidate(
                LexicalQueryComponent(
                    kind="raw_identifier",
                    value=identifier,
                    provenance="user_raw",
                    support_spans=(identifier,),
                ),
                append=False,
                order=order,
            )
        )
        order += 1

    for item in _accepted_items(plan, "symbols"):
        value = _value(item)
        support_spans = _support_spans(item, question) if value is not None else None
        if value is None or support_spans is None or not _symbol_is_grounded(value, support_spans, question):
            continue
        candidates.append(
            _Candidate(
                LexicalQueryComponent(
                    kind="analyzer_symbol",
                    value=value,
                    provenance="analyzer_accepted",
                    support_spans=support_spans,
                ),
                append=not _is_literally_represented(value, question),
                order=order,
            )
        )
        order += 1

    for item in _accepted_items(plan, "concepts"):
        value = _value(item)
        support_spans = _support_spans(item, question) if value is not None else None
        if value is None or support_spans is None or not _concept_is_query_grounded(value, support_spans, question):
            continue
        candidates.append(
            _Candidate(
                LexicalQueryComponent(
                    kind="analyzer_concept",
                    value=value,
                    provenance="analyzer_accepted",
                    support_spans=support_spans,
                ),
                append=not _is_literally_represented(value, question),
                order=order,
            )
        )
        order += 1

    for alias in _alias_keys(plan):
        if not _is_literally_represented(alias, question):
            continue
        candidates.append(
            _Candidate(
                LexicalQueryComponent(
                    kind="accepted_alias",
                    value=alias,
                    provenance="accepted_alias",
                    support_spans=(alias,),
                ),
                append=False,
                order=order,
            )
        )
        order += 1

    return candidates


def build_lexical_query(question: str, plan: Any) -> LexicalQuery:
    """Build a deterministic, raw-first lexical query from supplied plan data."""

    if not isinstance(question, str):
        raise TypeError("question must be a string")

    candidates = sorted(
        _candidate_list(question, plan),
        key=lambda candidate: (
            _KIND_PRIORITY.get(candidate.component.kind, 99),
            candidate.order,
        ),
    )

    components: list[LexicalQueryComponent] = []
    seen_component_keys: set[tuple[str, str, str]] = set()
    rendered_values: set[str] = set()
    appended_values: list[str] = []
    appended_tokens = 0
    appended_components = 0

    for candidate in candidates:
        component = candidate.component
        value_key = _normalization_key(component.value)
        component_key = (component.kind, component.provenance, value_key)
        if not value_key or component_key in seen_component_keys:
            continue
        seen_component_keys.add(component_key)

        should_append = candidate.append and value_key not in rendered_values
        if should_append:
            value_tokens = component.value.split()
            token_count = len(value_tokens)
            if (
                appended_components >= LEXICAL_MAX_APPENDED_COMPONENTS
                or not token_count
                or token_count > LEXICAL_MAX_APPENDED_TOKENS - appended_tokens
            ):
                continue
            appended_values.append(component.value)
            appended_components += 1
            appended_tokens += token_count

        rendered_values.add(value_key)
        if should_append:
            component = LexicalQueryComponent(
                kind=component.kind,
                value=component.value,
                provenance=component.provenance,
                support_spans=component.support_spans,
                appended=True,
            )
        components.append(component)

    text = question
    if appended_values:
        text += " " + " ".join(appended_values)

    return LexicalQuery(
        text=text,
        raw_question=question,
        components=components,
        excluded_component_classes=list(_EXCLUDED_COMPONENT_CLASSES),
    )


__all__ = [
    "LEXICAL_MAX_APPENDED_COMPONENTS",
    "LEXICAL_MAX_APPENDED_TOKENS",
    "LexicalQueryComponent",
    "LexicalQuery",
    "build_lexical_query",
]
