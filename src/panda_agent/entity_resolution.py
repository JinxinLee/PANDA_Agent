"""Entity-first exact resolution for the exact retrieval channel.

C5 introduces a query-time entity-resolution contract in front of the legacy
exact fallback: boundary-safe mention extraction, deterministic exact
matching, explicit ambiguity, locked-version validation, and a full
resolution receipt.  Resolution reads only ``knowledge_aliases`` and
``knowledge_objects`` through an injected storage connection, never calls
models or other retrieval channels, and never writes.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from panda_agent.lexical_query import (
    _complete_technical_token,
    _looks_like_technical_identifier,
    _raw_identifiers,
)

RESOLVED_UNIQUE = "RESOLVED_UNIQUE"
RESOLVED_MULTIPLE = "RESOLVED_MULTIPLE"
AMBIGUOUS = "AMBIGUOUS"
UNRESOLVED = "UNRESOLVED"
REJECTED_VERSION = "REJECTED_VERSION"
REJECTED_SCOPE = "REJECTED_SCOPE"
MISSING_TARGET = "MISSING_TARGET"

MATCH_ACCEPTED_ALIAS = "accepted_alias"
MATCH_EXACT_SYMBOL = "exact_symbol"
MATCH_EXACT_TITLE = "exact_title"
MATCH_EXACT_PATH = "exact_path"
MATCH_IDENTITY_RELATION = "identity_relation"

MATCH_KIND_PRIORITY = {
    MATCH_ACCEPTED_ALIAS: 0,
    MATCH_EXACT_SYMBOL: 1,
    MATCH_EXACT_TITLE: 2,
    MATCH_EXACT_PATH: 3,
    MATCH_IDENTITY_RELATION: 4,
}

MENTION_KIND_PRIORITY = {
    "accepted_alias": 0,
    "analyzer_symbol": 1,
    "explicit_identifier": 2,
}

# No existing relation predicate unambiguously means entity identity or
# canonical aliasing (CALLS/READS/INCLUDES/... are not equivalence), so
# relation-based identity resolution stays unavailable.  Phase D owns richer
# relation semantics.
IDENTITY_RELATION_SUPPORT = "NOT_AVAILABLE"

_OBJECT_COLUMNS = (
    "object_id,source_id,source_version_id,object_type,title,text,"
    "authority_level,locator,canonical_locator"
)


@dataclass(frozen=True)
class EntityMention:
    """One query-grounded entity mention and its safe provenance."""

    text: str
    kind: str
    provenance: str
    support_span: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "kind": self.kind,
            "provenance": self.provenance,
            "support_span": self.support_span,
        }


@dataclass(frozen=True)
class EntityCandidate:
    """One canonical object considered for a mention and how it matched."""

    object_id: str
    source_id: str
    source_version_id: str
    match_kind: str
    matched_value: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "source_id": self.source_id,
            "source_version_id": self.source_version_id,
            "match_kind": self.match_kind,
            "matched_value": self.matched_value,
        }


@dataclass
class EntityResolution:
    """The outcome of resolving one mention, without hidden selection."""

    mention: EntityMention
    status: str
    candidates: list[EntityCandidate] = field(default_factory=list)
    selected_object_id: str | None = None
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "mention": self.mention.as_dict(),
            "status": self.status,
            "candidates": [candidate.as_dict() for candidate in self.candidates],
            "selected_object_id": self.selected_object_id,
            "reason": self.reason,
        }


@dataclass
class EntityResolutionReceipt:
    """The auditable record of one entity-resolution pass."""

    resolutions: list[EntityResolution] = field(default_factory=list)
    resolved_object_ids: list[str] = field(default_factory=list)
    ambiguous_mentions: list[str] = field(default_factory=list)
    unresolved_mentions: list[str] = field(default_factory=list)
    rejected_candidates: list[dict[str, Any]] = field(default_factory=list)
    fallback_required: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "identity_relation_support": IDENTITY_RELATION_SUPPORT,
            "resolutions": [resolution.as_dict() for resolution in self.resolutions],
            "resolved_object_ids": list(self.resolved_object_ids),
            "ambiguous_mentions": list(self.ambiguous_mentions),
            "unresolved_mentions": list(self.unresolved_mentions),
            "rejected_candidates": [dict(item) for item in self.rejected_candidates],
            "fallback_required": self.fallback_required,
        }


@dataclass(frozen=True)
class AcceptedAlias:
    """One accepted alias row from ``knowledge_aliases``."""

    alias_text: str
    normalized_alias: str
    target_object_id: str
    source_version_id: str


_ALIAS_BOUNDARY_LEFT = r"(?<![A-Za-z0-9_])"
_ALIAS_BOUNDARY_RIGHT = r"(?![A-Za-z0-9_])"


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _normalization_key(value: str) -> str:
    return " ".join(value.casefold().split())


def alias_match_pattern(alias_text: str) -> re.Pattern[str]:
    """Boundary-safe, whitespace-stable, case-insensitive alias matcher."""

    escaped = re.escape(alias_text.strip())
    # Allow flexible internal whitespace while keeping every other character
    # literal; "*" stays literal because broadening glob semantics would
    # exceed the accepted alias data.
    escaped = re.sub(r"(\\\s)+", r"\\s+", escaped)
    return re.compile(
        _ALIAS_BOUNDARY_LEFT + escaped + _ALIAS_BOUNDARY_RIGHT, re.IGNORECASE
    )


def alias_matches(alias_text: str, question: str) -> str | None:
    """Return the matched support span when the alias occurs whole in text."""

    if not isinstance(question, str) or not alias_text.strip():
        return None
    match = alias_match_pattern(alias_text).search(question)
    return match.group(0) if match else None


def load_accepted_aliases(connection: Any) -> list[AcceptedAlias]:
    rows = connection.execute(
        "SELECT alias_text,normalized_alias,target_object_id,source_version_id "
        "FROM knowledge_aliases WHERE review_status='accepted' "
        "ORDER BY normalized_alias,target_object_id"
    ).fetchall()
    return [AcceptedAlias(*row) for row in rows]


def extract_entity_mentions(
    question: str, plan: Any, accepted_aliases: Sequence[AcceptedAlias] = ()
) -> list[EntityMention]:
    """Collect provenance-safe entity mentions from the raw question.

    Sources: explicit technical identifiers in the question, C2 accepted
    analyzer symbols with complete in-question support, and accepted aliases
    matched with boundary-safe deterministic patterns.  Reviewed query
    expansions, rejected analyzer items, flat plan fields, and Gold metadata
    are structurally not consulted.
    """

    merged: dict[str, EntityMention] = {}

    def add(text: str, kind: str, provenance: str, support_span: str) -> None:
        key = _normalization_key(text)
        existing = merged.get(key)
        if existing is None or MENTION_KIND_PRIORITY[kind] < MENTION_KIND_PRIORITY[existing.kind]:
            merged[key] = EntityMention(
                text=text, kind=kind, provenance=provenance, support_span=support_span
            )

    for identifier in _raw_identifiers(question):
        add(identifier, "explicit_identifier", "user_raw_technical_token", identifier)

    diagnostics = _field(plan, "analysis_diagnostics", {}) or {}
    accepted_delta = _field(diagnostics, "analyzer_accepted_semantic_delta", {}) or {}
    for item in _as_list(_field(accepted_delta, "symbols", [])):
        value = _field(item, "value")
        spans = _field(item, "support_spans")
        if not isinstance(value, str) or not value.strip():
            continue
        if isinstance(spans, str):
            spans = (spans,)
        if not isinstance(spans, Sequence) or isinstance(spans, bytes) or not spans:
            continue
        if any(not isinstance(span, str) or span not in question for span in spans):
            continue
        if not _looks_like_technical_identifier(value):
            continue
        if _complete_technical_token(value, question) is None:
            continue
        add(value, "analyzer_symbol", "analyzer_accepted", spans[0])

    for alias in accepted_aliases:
        span = alias_matches(alias.alias_text, question)
        if span is not None:
            add(alias.alias_text, "accepted_alias", "accepted_alias", span)

    return list(merged.values())


def _as_list(value: Any) -> list[Any]:
    if value is None or isinstance(value, (str, bytes)):
        return []
    if isinstance(value, Sequence):
        return list(value)
    return []


class EntityResolver:
    """Resolve query-grounded mentions to canonical objects, or report why not."""

    def __init__(self, storage: Any, *, context_sources: Iterable[str] = ()) -> None:
        self.storage = storage
        self.context_sources = tuple(context_sources)

    # -- plan scope helpers -------------------------------------------------

    def _allowed_source_ids(self, plan: Mapping[str, Any]) -> list[str]:
        targets = [str(repo) for repo in plan.get("target_repositories", [])]
        return [*dict.fromkeys([*targets, *self.context_sources, "curated_panda_domain"])]

    def _locked_versions(self, plan: Mapping[str, Any]) -> dict[str, str]:
        resolved = plan.get("resolved_versions", {}) or {}
        return {
            str(repo): f"{repo}@{version}" for repo, version in resolved.items()
        }

    def _row_scope_status(
        self, row: Mapping[str, Any], allowed: Sequence[str], locked: Mapping[str, str]
    ) -> str | None:
        """Return a rejection status, or None when the row is promotable."""

        source_id = str(row.get("source_id", ""))
        if source_id not in allowed:
            return REJECTED_SCOPE
        expected = locked.get(source_id)
        if expected is not None and str(row.get("source_version_id", "")) != expected:
            return REJECTED_VERSION
        return None

    # -- candidate lookup ---------------------------------------------------

    def _fetch_object_rows(self, connection: Any, object_ids: Sequence[str]) -> list[dict[str, Any]]:
        if not object_ids:
            return []
        rows = connection.execute(
            f"SELECT {_OBJECT_COLUMNS} FROM knowledge_objects WHERE object_id=ANY(%s)",
            (list(dict.fromkeys(object_ids)),),
        ).fetchall()
        columns = _OBJECT_COLUMNS.split(",")
        return [dict(zip(columns, row)) for row in rows]

    def _fetch_exact_rows(self, connection: Any, values: Sequence[str]) -> list[dict[str, Any]]:
        if not values:
            return []
        rows = connection.execute(
            f"SELECT {_OBJECT_COLUMNS} FROM knowledge_objects "
            "WHERE locator->>'symbol' = ANY(%s) OR title = ANY(%s) "
            "OR locator->>'path' = ANY(%s) OR split_part(locator->>'path','/',-1) = ANY(%s)",
            (list(values), list(values), list(values), list(values)),
        ).fetchall()
        columns = _OBJECT_COLUMNS.split(",")
        return [dict(zip(columns, row)) for row in rows]

    def _match_layer(self, value: str, row: Mapping[str, Any]) -> str | None:
        """Deterministic exact-match layer for one row against one value."""

        locator = row.get("locator") or {}
        symbol = locator.get("symbol") if isinstance(locator, Mapping) else None
        path = locator.get("path") if isinstance(locator, Mapping) else None
        if symbol is not None and value == symbol:
            return MATCH_EXACT_SYMBOL
        if value == row.get("title"):
            return MATCH_EXACT_TITLE
        if path is not None:
            if value == path:
                return MATCH_EXACT_PATH
            if "/" in str(path) and value == str(path).rsplit("/", 1)[-1]:
                return MATCH_EXACT_PATH
        return None

    # -- resolution ---------------------------------------------------------

    def resolve(
        self, question: str, plan: Mapping[str, Any]
    ) -> tuple[EntityResolutionReceipt, list[dict[str, Any]]]:
        """Resolve mentions and return the receipt plus the canonical prefix rows."""

        if not isinstance(question, str):
            raise TypeError("question must be a string")
        with self.storage.connect() as connection:
            aliases = load_accepted_aliases(connection)
            mentions = extract_entity_mentions(question, plan, aliases)
            allowed = self._allowed_source_ids(plan)
            locked = self._locked_versions(plan)
            receipt = EntityResolutionReceipt()

            symbol_values = [
                mention.text
                for mention in mentions
                if mention.kind in {"explicit_identifier", "analyzer_symbol"}
            ]
            exact_rows = self._fetch_exact_rows(connection, symbol_values)

            alias_mentions = [m for m in mentions if m.kind == "accepted_alias"]
            alias_target_ids = []
            alias_row_by_target: dict[str, dict[str, Any]] = {}
            if alias_mentions:
                for alias in aliases:
                    if alias_match_pattern(alias.alias_text).search(question):
                        alias_target_ids.append(alias.target_object_id)
                for row in self._fetch_object_rows(connection, alias_target_ids):
                    alias_row_by_target[str(row["object_id"])] = row

        canonical_prefix: list[dict[str, Any]] = []
        prefix_seen: set[str] = set()

        for mention in mentions:
            candidates: list[EntityCandidate] = []
            rejected: list[dict[str, Any]] = []
            promotable_rows: list[tuple[EntityCandidate, dict[str, Any]]] = []

            if mention.kind == "accepted_alias":
                for alias in aliases:
                    if _normalization_key(alias.alias_text) != _normalization_key(mention.text):
                        continue
                    row = alias_row_by_target.get(alias.target_object_id)
                    if row is None:
                        rejected.append(
                            {
                                "mention": mention.text,
                                "target_object_id": alias.target_object_id,
                                "reason": MISSING_TARGET,
                            }
                        )
                        continue
                    rejection = self._row_scope_status(row, allowed, locked)
                    if rejection is not None:
                        rejected.append(
                            {
                                "mention": mention.text,
                                "target_object_id": alias.target_object_id,
                                "source_id": row.get("source_id"),
                                "source_version_id": row.get("source_version_id"),
                                "reason": rejection,
                            }
                        )
                        continue
                    candidate = EntityCandidate(
                        object_id=str(row["object_id"]),
                        source_id=str(row.get("source_id", "")),
                        source_version_id=str(row.get("source_version_id", "")),
                        match_kind=MATCH_ACCEPTED_ALIAS,
                        matched_value=alias.alias_text,
                    )
                    candidates.append(candidate)
                    promotable_rows.append((candidate, row))
                status, reason = self._alias_status(candidates, rejected)
            else:
                best_layer: str | None = None
                for row in exact_rows:
                    layer = self._match_layer(mention.text, row)
                    if layer is None:
                        continue
                    if best_layer is None or MATCH_KIND_PRIORITY[layer] < MATCH_KIND_PRIORITY[best_layer]:
                        best_layer = layer
                for row in exact_rows:
                    layer = self._match_layer(mention.text, row)
                    if layer is None or layer != best_layer:
                        continue
                    rejection = self._row_scope_status(row, allowed, locked)
                    if rejection is not None:
                        rejected.append(
                            {
                                "mention": mention.text,
                                "target_object_id": str(row.get("object_id", "")),
                                "source_id": row.get("source_id"),
                                "source_version_id": row.get("source_version_id"),
                                "reason": rejection,
                            }
                        )
                        continue
                    candidate = EntityCandidate(
                        object_id=str(row["object_id"]),
                        source_id=str(row.get("source_id", "")),
                        source_version_id=str(row.get("source_version_id", "")),
                        match_kind=best_layer,
                        matched_value=mention.text,
                    )
                    candidates.append(candidate)
                    promotable_rows.append((candidate, row))
                status, reason = self._symbol_status(best_layer, candidates, rejected)

            selected: str | None = None
            if status == RESOLVED_UNIQUE:
                unique_rows = {
                    str(row["object_id"]): (candidate, row)
                    for candidate, row in promotable_rows
                }
                if len(unique_rows) == 1:
                    selected = next(iter(unique_rows))
                    if selected not in prefix_seen:
                        prefix_seen.add(selected)
                        canonical_prefix.append(unique_rows[selected][1])
                    receipt.resolved_object_ids.append(selected)
                else:
                    status = RESOLVED_MULTIPLE
                    reason = "distinct canonical objects share the exact match"

            resolution = EntityResolution(
                mention=mention,
                status=status,
                candidates=candidates,
                selected_object_id=selected,
                reason=reason,
            )
            receipt.resolutions.append(resolution)
            if status in {AMBIGUOUS, RESOLVED_MULTIPLE}:
                receipt.ambiguous_mentions.append(mention.text)
            if status in {UNRESOLVED, MISSING_TARGET, REJECTED_VERSION, REJECTED_SCOPE}:
                receipt.unresolved_mentions.append(mention.text)
            receipt.rejected_candidates.extend(rejected)

        receipt.fallback_required = not canonical_prefix or bool(
            receipt.ambiguous_mentions
        )
        return receipt, canonical_prefix

    @staticmethod
    def _alias_status(
        candidates: list[EntityCandidate], rejected: list[dict[str, Any]]
    ) -> tuple[str, str]:
        distinct = {candidate.object_id for candidate in candidates}
        if len(distinct) > 1:
            return AMBIGUOUS, "accepted alias maps to multiple valid canonical targets"
        if len(distinct) == 1:
            return RESOLVED_UNIQUE, "accepted alias resolves one validated canonical target"
        if any(item["reason"] == MISSING_TARGET for item in rejected):
            return MISSING_TARGET, "accepted alias target object does not exist"
        if any(item["reason"] == REJECTED_VERSION for item in rejected):
            return REJECTED_VERSION, "alias target rejected by locked-version safety"
        if any(item["reason"] == REJECTED_SCOPE for item in rejected):
            return REJECTED_SCOPE, "alias target rejected by source-scope safety"
        return UNRESOLVED, "no canonical target matched"

    @staticmethod
    def _symbol_status(
        best_layer: str | None,
        candidates: list[EntityCandidate],
        rejected: list[dict[str, Any]],
    ) -> tuple[str, str]:
        distinct = {candidate.object_id for candidate in candidates}
        if best_layer is not None and len(distinct) == 1:
            return RESOLVED_UNIQUE, f"unique {best_layer} match within locked scope"
        if best_layer is not None and len(distinct) > 1:
            return RESOLVED_MULTIPLE, "multiple distinct objects share the exact match"
        if any(item["reason"] == REJECTED_VERSION for item in rejected):
            return REJECTED_VERSION, "exact match rejected by locked-version safety"
        if any(item["reason"] == REJECTED_SCOPE for item in rejected):
            return REJECTED_SCOPE, "exact match rejected by source-scope safety"
        return UNRESOLVED, "no exact symbol/title/path match"


def merge_exact_streams(
    canonical_prefix: Sequence[Mapping[str, Any]],
    legacy_rows: Sequence[Mapping[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    """Entity-first candidates precede legacy fallback with stable dedup."""

    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in [*canonical_prefix, *legacy_rows]:
        object_id = str(row.get("object_id", ""))
        if object_id in seen:
            continue
        seen.add(object_id)
        merged.append(dict(row))
        if len(merged) >= limit:
            break
    return merged


__all__ = [
    "RESOLVED_UNIQUE",
    "RESOLVED_MULTIPLE",
    "AMBIGUOUS",
    "UNRESOLVED",
    "REJECTED_VERSION",
    "REJECTED_SCOPE",
    "MISSING_TARGET",
    "MATCH_ACCEPTED_ALIAS",
    "MATCH_EXACT_SYMBOL",
    "MATCH_EXACT_TITLE",
    "MATCH_EXACT_PATH",
    "MATCH_IDENTITY_RELATION",
    "IDENTITY_RELATION_SUPPORT",
    "EntityMention",
    "EntityCandidate",
    "EntityResolution",
    "EntityResolutionReceipt",
    "AcceptedAlias",
    "alias_match_pattern",
    "alias_matches",
    "load_accepted_aliases",
    "extract_entity_mentions",
    "EntityResolver",
    "merge_exact_streams",
]
