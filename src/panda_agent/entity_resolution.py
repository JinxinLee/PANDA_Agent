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

try:
    # D2 Tier D integration: descriptive_resolution is delivered concurrently
    # with the D2-A1 integration and is consumed defensively until then.  The
    # import is at module top per the D2-A1 brief; absence degrades Tier D to
    # deterministic abstention instead of breaking the C5 module.
    from panda_agent.descriptive_resolution import (
        GovernedEntity,
        build_descriptive_index,
        evaluate_descriptive_mentions,
    )
except ImportError as _descriptive_error:  # pragma: no cover - integration ordering
    GovernedEntity = None  # type: ignore[assignment,misc]
    build_descriptive_index = None  # type: ignore[assignment]
    evaluate_descriptive_mentions = None  # type: ignore[assignment]
    _DESCRIPTIVE_RESOLUTION_IMPORT_ERROR = (
        f"descriptive_resolution import failed: {_descriptive_error}"
    )
else:
    _DESCRIPTIVE_RESOLUTION_IMPORT_ERROR: str | None = None

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

    # -- D2 shadow resolution (Phase D2-A1; contract Section 14) ------------
    #
    # Shadow-only implementation of docs/PHASE_D2_A0_RESOLVER_CONTRACT.md.
    # Read-only SQL, deterministic ordering, no analyzer/model/retrieval-channel
    # calls.  The C5 resolve() path above stays untouched.

    def _load_accepted_aliases_d2(self, connection: Any) -> list[AcceptedAliasD2]:
        """Accepted alias rows with the frozen corrective-classification marker.

        ``correction_message`` is persisted inside the alias payload JSONB; a
        non-null value classifies the alias as a corrective term, which is
        never Tier G identity evidence (contract Section 5).
        """

        rows = connection.execute(
            "SELECT alias_text,normalized_alias,target_object_id,source_version_id,"
            "payload->>'correction_message' AS correction_message "
            "FROM knowledge_aliases WHERE review_status='accepted' "
            "ORDER BY normalized_alias,target_object_id"
        ).fetchall()
        return [AcceptedAliasD2(*row) for row in rows]

    def _load_accepted_same_as(self, connection: Any) -> list[tuple[str, str]]:
        """Accepted SAME_AS edges only; pending/rejected edges are never loaded."""

        rows = connection.execute(
            "SELECT subject_id,object_id FROM relation_edges "
            "WHERE predicate='SAME_AS' AND review_status='accepted' "
            "ORDER BY subject_id,object_id"
        ).fetchall()
        return [(str(row[0]), str(row[1])) for row in rows]

    def _load_canonical_entities(self, connection: Any) -> list[dict[str, Any]]:
        """Full rows of the small governed canonical-entity set."""

        rows = connection.execute(
            f"SELECT {_D2_OBJECT_COLUMNS} FROM knowledge_objects "
            "WHERE metadata->>'identity_role'='canonical' ORDER BY object_id"
        ).fetchall()
        columns = _D2_OBJECT_COLUMNS.split(",")
        return [dict(zip(columns, row)) for row in rows]

    def _load_canonical_relation_features(
        self, connection: Any, canonical_ids: Sequence[str]
    ) -> dict[str, tuple[str, ...]]:
        """Accepted-relation structured facts and related titles per canonical entity.

        Facts look like ``CONSUMES data_product.restgas.pid_root`` when the
        canonical entity is the edge subject and ``~PRODUCES workflow.x`` (the
        ``~`` marker denotes the inverse direction) when it is the edge object;
        related endpoint titles are emitted verbatim.
        """

        if not canonical_ids:
            return {}
        ids = list(dict.fromkeys(canonical_ids))
        rows = connection.execute(
            "SELECT e.subject_id,e.predicate,e.object_id,so.title,oo.title "
            "FROM relation_edges e "
            "LEFT JOIN knowledge_objects so ON so.object_id=e.subject_id "
            "LEFT JOIN knowledge_objects oo ON oo.object_id=e.object_id "
            "WHERE e.review_status='accepted' "
            "AND (e.subject_id=ANY(%s) OR e.object_id=ANY(%s)) "
            "ORDER BY e.subject_id,e.predicate,e.object_id",
            (ids, ids),
        ).fetchall()
        canonical = set(ids)
        features: dict[str, list[str]] = {}
        for subject_id, predicate, object_id, subject_title, object_title in rows:
            for anchor, other_id, other_title, inverse in (
                (str(subject_id), str(object_id), object_title, False),
                (str(object_id), str(subject_id), subject_title, True),
            ):
                if anchor not in canonical:
                    continue
                marker = "~" if inverse else ""
                features.setdefault(anchor, []).append(f"{marker}{predicate} {other_id}")
                if other_title:
                    features[anchor].append(str(other_title))
        return {
            key: tuple(dict.fromkeys(values)) for key, values in sorted(features.items())
        }

    def _d2_mentions(
        self,
        question: str,
        plan: Mapping[str, Any],
        aliases: Sequence[AcceptedAliasD2],
        canonical_rows: Sequence[Mapping[str, Any]],
        connection: Any,
    ) -> tuple[list[EntityMention], dict[str, dict[str, Any]]]:
        """Deterministic D2 mention set (contract Section 11).

        Reuses the C5 extraction, then adds governed-ID mentions (canonical IDs
        plus raw question tokens resolved by exact object-ID lookup, occurring
        verbatim in the question) and descriptive mentions (plan concepts, or
        the whole stripped question when no concepts exist).  A mention text is
        resolved once; the strongest provenance kind wins.
        """

        merged: dict[str, EntityMention] = {}

        def add(text: str, kind: str, provenance: str, support_span: str) -> None:
            key = _normalization_key(text)
            if not key:
                return
            existing = merged.get(key)
            if (
                existing is None
                or _D2_MENTION_KIND_PRIORITY[kind] < _D2_MENTION_KIND_PRIORITY[existing.kind]
            ):
                merged[key] = EntityMention(
                    text=text, kind=kind, provenance=provenance, support_span=support_span
                )

        accepted_for_extraction = [
            AcceptedAlias(
                alias.alias_text,
                alias.normalized_alias,
                alias.target_object_id,
                alias.source_version_id,
            )
            for alias in aliases
        ]
        for mention in extract_entity_mentions(question, plan, accepted_for_extraction):
            add(mention.text, mention.kind, mention.provenance, mention.support_span)

        governed_ids = {str(row["object_id"]) for row in canonical_rows}
        governed_ids.update(_raw_identifiers(question))
        verbatim: list[tuple[str, str]] = []
        for object_id in sorted(governed_ids):
            span = alias_matches(object_id, question)
            if span is not None:
                verbatim.append((object_id, span))
        governed_id_rows = {
            str(row["object_id"]): row
            for row in self._fetch_object_rows(connection, [oid for oid, _ in verbatim])
        }
        for object_id, span in verbatim:
            if object_id in governed_id_rows:
                add(object_id, "governed_id", "verbatim_governed_id", span)

        concepts = [str(item).strip() for item in _as_list(_field(plan, "concepts", []))]
        concepts = [concept for concept in concepts if concept]
        if concepts:
            for concept in sorted(dict.fromkeys(concepts), key=_normalization_key):
                add(concept, "descriptive", "plan_concept", concept)
        else:
            stripped = question.strip()
            if stripped:
                add(stripped, "descriptive", "question_descriptive_span", stripped)

        mentions = sorted(
            merged.values(),
            key=lambda mention: (
                _D2_MENTION_KIND_PRIORITY[mention.kind],
                _normalization_key(mention.text),
            ),
        )
        return mentions, governed_id_rows

    def resolve_shadow(self, question: str, plan: Mapping[str, Any]) -> D2ResolutionReceipt:
        """Deterministic shadow resolution under the frozen D2 contract.

        Read-only; never calls the analyzer, other retrieval channels, or any
        model.  Returns the D2 resolution receipt without touching production
        behavior or the C5 resolve() path.
        """

        if not isinstance(question, str):
            raise TypeError("question must be a string")
        with self.storage.connect() as connection:
            aliases = self._load_accepted_aliases_d2(connection)
            same_as_edges = self._load_accepted_same_as(connection)
            canonical_rows = self._load_canonical_entities(connection)
            canonical_ids = {str(row["object_id"]) for row in canonical_rows}
            canonical_row_by_id = {str(row["object_id"]): row for row in canonical_rows}
            relation_features = self._load_canonical_relation_features(
                connection, sorted(canonical_ids)
            )
            mentions, governed_id_rows = self._d2_mentions(
                question, plan, aliases, canonical_rows, connection
            )
            allowed = self._allowed_source_ids(plan)
            locked = self._locked_versions(plan)
            version_scope = {
                "allowed_sources": list(allowed),
                "locked_versions": dict(locked),
            }
            symbol_values: list[str] = []
            for mention in mentions:
                if mention.kind not in {"explicit_identifier", "analyzer_symbol"}:
                    continue
                symbol_values.append(mention.text)
                # Plural-form mentions fall back to their singular form
                # (contract Section 9 valid multi-entity resolution).
                if len(mention.text) > 1 and mention.text.endswith("s"):
                    symbol_values.append(mention.text[:-1])
            exact_rows = self._fetch_exact_rows(connection, symbol_values)
            same_as_endpoint_ids = sorted({oid for edge in same_as_edges for oid in edge})
            same_as_rows = {
                str(row["object_id"]): row
                for row in self._fetch_object_rows(connection, same_as_endpoint_ids)
            }

            receipt = D2ResolutionReceipt()
            corrective_surfaces: set[str] = set()
            tier_d_pending: list[tuple[EntityMention, D2Resolution]] = []

            for mention in mentions:
                resolution, corrective_entry = self._resolve_mention_d2(
                    mention,
                    connection=connection,
                    aliases=aliases,
                    exact_rows=exact_rows,
                    governed_id_rows=governed_id_rows,
                    canonical_ids=canonical_ids,
                    same_as_edges=same_as_edges,
                    same_as_rows=same_as_rows,
                    allowed=allowed,
                    locked=locked,
                    version_scope=version_scope,
                )
                receipt.resolutions.append(resolution)
                if corrective_entry is not None:
                    receipt.corrective_mentions.append(corrective_entry)
                    corrective_surfaces.add(resolution.mention_text)
                if resolution.status == UNRESOLVED and resolution.diagnostics.get(
                    "corrective"
                ) is not True:
                    tier_d_pending.append((mention, resolution))

            self._apply_tier_d(
                question,
                tier_d_pending,
                canonical_rows=canonical_rows,
                canonical_row_by_id=canonical_row_by_id,
                relation_features=relation_features,
                allowed=allowed,
                locked=locked,
                version_scope=version_scope,
            )

            resolved_ids: set[str] = set()
            for resolution in receipt.resolutions:
                if resolution.status == RESOLVED_UNIQUE and resolution.matched_object_id:
                    resolved_ids.add(resolution.matched_object_id)
                elif resolution.status == RESOLVED_MULTIPLE:
                    resolved_ids.update(resolution.selected_object_ids)
                    receipt.multi_entity_results.append(
                        {
                            "mention": resolution.mention_text,
                            "mention_kind": resolution.mention_kind,
                            "selected_object_ids": list(resolution.selected_object_ids),
                        }
                    )
                elif resolution.status == AMBIGUOUS:
                    receipt.ambiguous_mentions.append(resolution.mention_text)
                elif resolution.status in {
                    UNRESOLVED,
                    REJECTED_VERSION,
                    REJECTED_SCOPE,
                    MISSING_TARGET,
                }:
                    if resolution.mention_text not in corrective_surfaces:
                        receipt.unresolved_mentions.append(resolution.mention_text)
                resolution.candidates.sort(
                    key=lambda item: (
                        str(item.get("status", "")),
                        str(item.get("object_id", "")),
                    )
                )
                resolution.evidence.sort(
                    key=lambda item: (
                        item.tier,
                        item.kind,
                        item.object_id,
                        item.matched_value,
                    )
                )
            receipt.resolved_object_ids = sorted(resolved_ids)
            receipt.fallback_required = any(
                resolution.status in _D2_FAILING_STATUSES
                for resolution in receipt.resolutions
            ) or bool(receipt.corrective_mentions)
            return receipt

    @staticmethod
    def _d2_candidate(
        *,
        object_id: str,
        match_kind: str,
        matched_value: str,
        tier: str,
        status: str,
        reason: str,
        source_id: str = "",
        source_version_id: str = "",
    ) -> dict[str, Any]:
        return {
            "object_id": object_id,
            "source_id": source_id,
            "source_version_id": source_version_id,
            "match_kind": match_kind,
            "matched_value": matched_value,
            "tier": tier,
            "status": status,
            "reason": reason,
        }

    @staticmethod
    def _d2_rejection_status(rejections: Sequence[str]) -> str:
        for status in (MISSING_TARGET, REJECTED_VERSION, REJECTED_SCOPE):
            if status in rejections:
                return status
        return UNRESOLVED

    def _resolve_mention_d2(
        self,
        mention: EntityMention,
        *,
        connection: Any,
        aliases: Sequence[AcceptedAliasD2],
        exact_rows: Sequence[dict[str, Any]],
        governed_id_rows: Mapping[str, dict[str, Any]],
        canonical_ids: set[str],
        same_as_edges: Sequence[tuple[str, str]],
        same_as_rows: Mapping[str, dict[str, Any]],
        allowed: Sequence[str],
        locked: Mapping[str, str],
        version_scope: Mapping[str, Any],
    ) -> tuple[D2Resolution, dict[str, Any] | None]:
        """Resolve one mention through the D2 evidence tiers (contract Section 4)."""

        candidates: list[dict[str, Any]] = []
        evidence: list[D2Evidence] = []
        diagnostics: dict[str, Any] = {
            "canonicalization": False,
            "descriptive_inference": False,
            "corrective": False,
            "correction_message": None,
            "identity_authority": False,
            "ambiguity_reason": None,
            "abstention_reason": None,
            "rejection_reasons": [],
        }
        resolution = D2Resolution(
            mention_text=mention.text,
            mention_kind=mention.kind,
            support_span=mention.support_span,
            status=UNRESOLVED,
            evidence=evidence,
            candidates=candidates,
            version_scope=dict(version_scope),
            diagnostics=diagnostics,
        )
        corrective_entry: dict[str, Any] | None = None

        if mention.kind == "accepted_alias":
            matching = [
                alias
                for alias in aliases
                if _normalization_key(alias.alias_text) == _normalization_key(mention.text)
            ]
            true_aliases = [a for a in matching if a.correction_message is None]
            corrective = [a for a in matching if a.correction_message is not None]
            if not true_aliases and corrective:
                # Corrective term (contract Section 5): correction surfaced,
                # candidate generated, never Tier G identity evidence.
                targets = sorted({alias.target_object_id for alias in corrective})
                message = sorted({str(alias.correction_message) for alias in corrective})[0]
                diagnostics["corrective"] = True
                diagnostics["correction_message"] = message
                diagnostics["abstention_reason"] = (
                    "corrective term requires user-facing correction; not identity evidence"
                )
                for target_id in targets:
                    candidates.append(
                        self._d2_candidate(
                            object_id=target_id,
                            match_kind=EVIDENCE_CORRECTIVE,
                            matched_value=mention.text,
                            tier="corrective",
                            status="CANDIDATE_ONLY",
                            reason=(
                                "corrective term generates a candidate without identity authority"
                            ),
                        )
                    )
                evidence.append(
                    D2Evidence(
                        tier="corrective",
                        kind=EVIDENCE_CORRECTIVE,
                        matched_value=mention.support_span or mention.text,
                        object_id=targets[0] if len(targets) == 1 else "",
                        detail=message,
                    )
                )
                corrective_entry = {
                    "surface_term": mention.text,
                    "target_candidate": targets[0] if len(targets) == 1 else None,
                    "correction_message": message,
                    "identity_authority": False,
                }
                return resolution, corrective_entry

            # Tier G(b): accepted true-identity alias.
            target_ids = sorted({alias.target_object_id for alias in true_aliases})
            rows_by_id = {
                str(row["object_id"]): row
                for row in self._fetch_object_rows(connection, target_ids)
            }
            promotable: list[dict[str, Any]] = []
            rejections: list[str] = []
            for alias in sorted(
                true_aliases, key=lambda item: (item.target_object_id, item.alias_text)
            ):
                row = rows_by_id.get(alias.target_object_id)
                if row is None:
                    candidates.append(
                        self._d2_candidate(
                            object_id=alias.target_object_id,
                            match_kind=MATCH_ACCEPTED_ALIAS,
                            matched_value=alias.alias_text,
                            tier=TIER_GOVERNED,
                            status=MISSING_TARGET,
                            reason="accepted alias target object does not exist",
                        )
                    )
                    diagnostics["rejection_reasons"].append(
                        {"object_id": alias.target_object_id, "reason": MISSING_TARGET}
                    )
                    rejections.append(MISSING_TARGET)
                    continue
                rejection = self._row_scope_status(row, allowed, locked)
                if rejection is not None:
                    candidates.append(
                        self._d2_candidate(
                            object_id=str(row["object_id"]),
                            source_id=str(row.get("source_id", "")),
                            source_version_id=str(row.get("source_version_id", "")),
                            match_kind=MATCH_ACCEPTED_ALIAS,
                            matched_value=alias.alias_text,
                            tier=TIER_GOVERNED,
                            status=rejection,
                            reason=_D2_REJECTION_REASONS[rejection],
                        )
                    )
                    diagnostics["rejection_reasons"].append(
                        {"object_id": str(row["object_id"]), "reason": rejection}
                    )
                    rejections.append(rejection)
                    continue
                candidates.append(
                    self._d2_candidate(
                        object_id=str(row["object_id"]),
                        source_id=str(row.get("source_id", "")),
                        source_version_id=str(row.get("source_version_id", "")),
                        match_kind=MATCH_ACCEPTED_ALIAS,
                        matched_value=alias.alias_text,
                        tier=TIER_GOVERNED,
                        status=_D2_PROMOTED,
                        reason="accepted alias resolves one validated target",
                    )
                )
                promotable.append(row)
            distinct = {str(row["object_id"]) for row in promotable}
            if len(distinct) == 1:
                resolution.status = RESOLVED_UNIQUE
                resolution.matched_object_id = next(iter(distinct))
                resolution.canonical_object_id = resolution.matched_object_id
                evidence.append(
                    D2Evidence(
                        tier=TIER_GOVERNED,
                        kind=EVIDENCE_TRUE_ALIAS,
                        matched_value=mention.support_span or mention.text,
                        object_id=resolution.matched_object_id,
                        detail="accepted true-identity alias maps the mention to its governed target",
                    )
                )
                diagnostics["identity_authority"] = True
            elif len(distinct) > 1:
                resolution.status = AMBIGUOUS
                diagnostics["ambiguity_reason"] = (
                    "accepted alias maps to multiple valid canonical targets"
                )
            else:
                resolution.status = self._d2_rejection_status(rejections)
            return resolution, None

        if mention.kind == "governed_id":
            # Tier G(a): governed object ID stated verbatim in the question.
            row = governed_id_rows.get(mention.text)
            if row is None:
                diagnostics["abstention_reason"] = (
                    "governed object id does not exist in the object set"
                )
                return resolution, None
            rejection = self._row_scope_status(row, allowed, locked)
            if rejection is not None:
                resolution.status = rejection
                candidates.append(
                    self._d2_candidate(
                        object_id=str(row["object_id"]),
                        source_id=str(row.get("source_id", "")),
                        source_version_id=str(row.get("source_version_id", "")),
                        match_kind=EVIDENCE_CANONICAL_ID,
                        matched_value=mention.text,
                        tier=TIER_GOVERNED,
                        status=rejection,
                        reason=_D2_REJECTION_REASONS[rejection],
                    )
                )
                diagnostics["rejection_reasons"].append(
                    {"object_id": str(row["object_id"]), "reason": rejection}
                )
                return resolution, None
            resolution.status = RESOLVED_UNIQUE
            resolution.matched_object_id = str(row["object_id"])
            if resolution.matched_object_id in canonical_ids:
                resolution.canonical_object_id = resolution.matched_object_id
            evidence.append(
                D2Evidence(
                    tier=TIER_GOVERNED,
                    kind=EVIDENCE_CANONICAL_ID,
                    matched_value=mention.text,
                    object_id=resolution.matched_object_id,
                    detail="governed object id stated verbatim in the question",
                )
            )
            diagnostics["identity_authority"] = True
            if resolution.canonical_object_id is None:
                # Source-native record: canonicalization needs governed evidence.
                self._apply_same_as_canonicalization_d2(
                    resolution,
                    resolution.matched_object_id,
                    same_as_edges=same_as_edges,
                    same_as_rows=same_as_rows,
                    canonical_ids=canonical_ids,
                    allowed=allowed,
                    locked=locked,
                )
            return resolution, None

        if mention.kind in {"explicit_identifier", "analyzer_symbol"}:
            # Tier S: exact symbol/title/path with C5 kind priority; plural-form
            # mentions may legitimately denote multiple entities (contract Section 9).
            plural_rows: list[tuple[dict[str, Any], str]] = []
            for row in exact_rows:
                layer = self._match_layer(mention.text, row)
                if layer is not None:
                    plural_rows.append((row, layer))
            singular = (
                mention.text[:-1]
                if len(mention.text) > 1 and mention.text.endswith("s")
                else None
            )
            singular_rows: list[tuple[dict[str, Any], str]] = []
            if not plural_rows and singular:
                for row in exact_rows:
                    layer = self._match_layer(singular, row)
                    if layer is not None:
                        singular_rows.append((row, layer))
            if plural_rows or singular_rows:
                self._resolve_exact_rows_d2(
                    resolution,
                    plural_rows or singular_rows,
                    mention.text if plural_rows else (singular or mention.text),
                    plural_mode=not plural_rows,
                    canonical_ids=canonical_ids,
                    same_as_edges=same_as_edges,
                    same_as_rows=same_as_rows,
                    allowed=allowed,
                    locked=locked,
                )
            return resolution, None

        # Descriptive mentions are Tier D candidates at most (contract Section 11).
        diagnostics["abstention_reason"] = (
            "descriptive mention awaits governed descriptive evaluation"
        )
        return resolution, None

    def _resolve_exact_rows_d2(
        self,
        resolution: D2Resolution,
        rows_with_layer: Sequence[tuple[dict[str, Any], str]],
        matched_value: str,
        *,
        plural_mode: bool,
        canonical_ids: set[str],
        same_as_edges: Sequence[tuple[str, str]],
        same_as_rows: Mapping[str, dict[str, Any]],
        allowed: Sequence[str],
        locked: Mapping[str, str],
    ) -> None:
        """Tier S exact-match resolution with the D2 supersession semantics.

        Competing exact candidates for a singular mention are AMBIGUOUS (never
        RESOLVED_MULTIPLE); a plural-form mention whose plural form matches
        nothing but whose singular form matches several distinct records is a
        valid multi-entity resolution.
        """

        diagnostics = resolution.diagnostics
        best_priority = min(MATCH_KIND_PRIORITY[layer] for _, layer in rows_with_layer)
        best_layer = next(
            layer for _, layer in rows_with_layer if MATCH_KIND_PRIORITY[layer] == best_priority
        )
        competing = sorted(
            (row for row, layer in rows_with_layer if layer == best_layer),
            key=lambda item: str(item["object_id"]),
        )
        promotable: list[dict[str, Any]] = []
        rejections: list[str] = []
        for row in competing:
            object_id = str(row["object_id"])
            rejection = self._row_scope_status(row, allowed, locked)
            if rejection is not None:
                resolution.candidates.append(
                    self._d2_candidate(
                        object_id=object_id,
                        source_id=str(row.get("source_id", "")),
                        source_version_id=str(row.get("source_version_id", "")),
                        match_kind=best_layer,
                        matched_value=matched_value,
                        tier=TIER_STRUCTURAL,
                        status=rejection,
                        reason=_D2_REJECTION_REASONS[rejection],
                    )
                )
                diagnostics["rejection_reasons"].append(
                    {"object_id": object_id, "reason": rejection}
                )
                rejections.append(rejection)
                continue
            resolution.candidates.append(
                self._d2_candidate(
                    object_id=object_id,
                    source_id=str(row.get("source_id", "")),
                    source_version_id=str(row.get("source_version_id", "")),
                    match_kind=best_layer,
                    matched_value=matched_value,
                    tier=TIER_STRUCTURAL,
                    status=_D2_PROMOTED,
                    reason=f"unique exact {best_layer} match within scope",
                )
            )
            promotable.append(row)
        distinct = {str(row["object_id"]) for row in promotable}
        if len(distinct) == 1:
            matched = next(iter(distinct))
            resolution.status = RESOLVED_UNIQUE
            resolution.matched_object_id = matched
            resolution.evidence.append(
                D2Evidence(
                    tier=TIER_STRUCTURAL,
                    kind=EVIDENCE_KIND_BY_MATCH[best_layer],
                    matched_value=matched_value,
                    object_id=matched,
                    detail=f"unique {best_layer} match within locked scope",
                )
            )
            diagnostics["identity_authority"] = True
            if matched not in canonical_ids:
                self._apply_same_as_canonicalization_d2(
                    resolution,
                    matched,
                    same_as_edges=same_as_edges,
                    same_as_rows=same_as_rows,
                    canonical_ids=canonical_ids,
                    allowed=allowed,
                    locked=locked,
                )
        elif len(distinct) > 1 and plural_mode:
            resolution.status = RESOLVED_MULTIPLE
            resolution.selected_object_ids = sorted(distinct)
            for object_id in sorted(distinct):
                row = next(item for item in promotable if str(item["object_id"]) == object_id)
                layer = self._match_layer(matched_value, row) or best_layer
                resolution.evidence.append(
                    D2Evidence(
                        tier=TIER_STRUCTURAL,
                        kind=EVIDENCE_KIND_BY_MATCH[layer],
                        matched_value=matched_value,
                        object_id=object_id,
                        detail="plural mention legitimately denotes multiple governed entities",
                    )
                )
            diagnostics["identity_authority"] = True
        elif len(distinct) > 1:
            # D2 supersession of the C5 collision semantics (contract Section 9).
            resolution.status = AMBIGUOUS
            diagnostics["ambiguity_reason"] = "multiple distinct objects share the exact match"
        elif rejections:
            resolution.status = self._d2_rejection_status(rejections)

    def _apply_same_as_canonicalization_d2(
        self,
        resolution: D2Resolution,
        matched_id: str,
        *,
        same_as_edges: Sequence[tuple[str, str]],
        same_as_rows: Mapping[str, dict[str, Any]],
        canonical_ids: set[str],
        allowed: Sequence[str],
        locked: Mapping[str, str],
    ) -> None:
        """Contract Section 6: canonicalize a resolved source-native record.

        Bidirectional, cycle-safe traversal over accepted SAME_AS edges only.
        Exactly one reachable canonical endpoint canonicalizes; several produce
        AMBIGUOUS; scope/version-conflicted endpoints produce the rejection.
        """

        adjacency: dict[str, set[str]] = {}
        for subject_id, object_id in same_as_edges:
            adjacency.setdefault(subject_id, set()).add(object_id)
            adjacency.setdefault(object_id, set()).add(subject_id)
        visited = {matched_id}
        frontier = [matched_id]
        while frontier:
            current = frontier.pop()
            for neighbor in sorted(adjacency.get(current, ())):
                if neighbor not in visited:
                    visited.add(neighbor)
                    frontier.append(neighbor)
        canonical_reached = sorted((visited & canonical_ids) - {matched_id})
        diagnostics = resolution.diagnostics
        passing: list[str] = []
        statuses: list[str] = []
        for object_id in canonical_reached:
            row = same_as_rows.get(object_id)
            if row is None:
                resolution.candidates.append(
                    self._d2_candidate(
                        object_id=object_id,
                        match_kind=EVIDENCE_SAME_AS,
                        matched_value=matched_id,
                        tier=TIER_GOVERNED,
                        status=MISSING_TARGET,
                        reason="accepted SAME_AS canonical endpoint row unavailable",
                    )
                )
                diagnostics["rejection_reasons"].append(
                    {"object_id": object_id, "reason": MISSING_TARGET}
                )
                statuses.append(MISSING_TARGET)
                continue
            rejection = self._row_scope_status(row, allowed, locked)
            if rejection is not None:
                resolution.candidates.append(
                    self._d2_candidate(
                        object_id=object_id,
                        source_id=str(row.get("source_id", "")),
                        source_version_id=str(row.get("source_version_id", "")),
                        match_kind=EVIDENCE_SAME_AS,
                        matched_value=matched_id,
                        tier=TIER_GOVERNED,
                        status=rejection,
                        reason=(
                            f"SAME_AS canonical endpoint {_D2_REJECTION_REASONS[rejection]}"
                        ),
                    )
                )
                diagnostics["rejection_reasons"].append(
                    {"object_id": object_id, "reason": rejection}
                )
                statuses.append(rejection)
                continue
            resolution.candidates.append(
                self._d2_candidate(
                    object_id=object_id,
                    source_id=str(row.get("source_id", "")),
                    source_version_id=str(row.get("source_version_id", "")),
                    match_kind=EVIDENCE_SAME_AS,
                    matched_value=matched_id,
                    tier=TIER_GOVERNED,
                    status=_D2_PROMOTED,
                    reason="accepted SAME_AS canonical endpoint",
                )
            )
            passing.append(object_id)
        if len(passing) == 1:
            resolution.canonical_object_id = passing[0]
            resolution.evidence.append(
                D2Evidence(
                    tier=TIER_GOVERNED,
                    kind=EVIDENCE_SAME_AS,
                    matched_value=resolution.mention_text,
                    object_id=passing[0],
                    detail=(
                        "accepted SAME_AS traversal from "
                        f"{matched_id} reaches one canonical identity"
                    ),
                )
            )
            diagnostics["canonicalization"] = True
            return
        if len(passing) > 1:
            resolution.status = AMBIGUOUS
            resolution.matched_object_id = None
            resolution.canonical_object_id = None
            diagnostics["identity_authority"] = False
            diagnostics["ambiguity_reason"] = (
                "accepted SAME_AS traversal reaches multiple canonical targets"
            )
            for object_id in passing:
                resolution.evidence.append(
                    D2Evidence(
                        tier=TIER_GOVERNED,
                        kind=EVIDENCE_SAME_AS,
                        matched_value=resolution.mention_text,
                        object_id=object_id,
                        detail="conflicting accepted SAME_AS canonical target",
                    )
                )
            return
        if statuses:
            resolution.status = self._d2_rejection_status(statuses)
            resolution.matched_object_id = None
            resolution.canonical_object_id = None
            diagnostics["identity_authority"] = False
        # No canonical endpoint reachable: the matched record stands as-is.

    def _apply_tier_d(
        self,
        question: str,
        pending: Sequence[tuple[EntityMention, D2Resolution]],
        *,
        canonical_rows: Sequence[Mapping[str, Any]],
        canonical_row_by_id: Mapping[str, Mapping[str, Any]],
        relation_features: Mapping[str, tuple[str, ...]],
        allowed: Sequence[str],
        locked: Mapping[str, str],
        version_scope: Mapping[str, Any],
    ) -> None:
        """Tier D: governed descriptive inference for unresolved/descriptive mentions."""

        if not pending:
            return
        if (
            GovernedEntity is None
            or build_descriptive_index is None
            or evaluate_descriptive_mentions is None
        ):
            for _mention, resolution in pending:
                resolution.diagnostics["abstention_reason"] = (
                    f"descriptive inference unavailable: {_DESCRIPTIVE_RESOLUTION_IMPORT_ERROR}"
                )
            return
        entities = [
            GovernedEntity(
                object_id=str(row["object_id"]),
                object_type=str(row.get("object_type", "")),
                source_id=str(row.get("source_id", "")),
                source_version_id=str(row.get("source_version_id", "")),
                title=str(row.get("title", "")),
                text=str(row.get("text", "") or ""),
                identity_role=str((row.get("metadata") or {}).get("identity_role", "")),
            )
            for row in sorted(canonical_rows, key=lambda item: str(item["object_id"]))
        ]
        index = build_descriptive_index(entities, relation_features)
        mention_texts = [mention.text for mention, _resolution in pending]
        decisions = evaluate_descriptive_mentions(question, mention_texts, index)
        by_mention: dict[str, list[Any]] = {}
        for decision in decisions:
            by_mention.setdefault(decision.mention, []).append(decision)
        for mention, resolution in pending:
            diagnostics = resolution.diagnostics
            group = by_mention.get(mention.text, [])
            if not group:
                diagnostics["abstention_reason"] = (
                    "no governed descriptive candidate matched the mention"
                )
                continue
            passing: list[Any] = []
            for decision in sorted(
                group, key=lambda item: (-item.feature_count, item.candidate_object_id)
            ):
                row = canonical_row_by_id.get(decision.candidate_object_id)
                if row is None:
                    resolution.candidates.append(
                        self._d2_candidate(
                            object_id=decision.candidate_object_id,
                            match_kind=EVIDENCE_DESCRIPN,
                            matched_value=mention.text,
                            tier=TIER_DESCRIPN,
                            status=MISSING_TARGET,
                            reason="descriptive candidate outside the governed canonical set",
                        )
                    )
                    diagnostics["rejection_reasons"].append(
                        {"object_id": decision.candidate_object_id, "reason": MISSING_TARGET}
                    )
                    continue
                rejection = self._row_scope_status(row, allowed, locked)
                if rejection is not None:
                    resolution.candidates.append(
                        self._d2_candidate(
                            object_id=decision.candidate_object_id,
                            source_id=str(row.get("source_id", "")),
                            source_version_id=str(row.get("source_version_id", "")),
                            match_kind=EVIDENCE_DESCRIPN,
                            matched_value=mention.text,
                            tier=TIER_DESCRIPN,
                            status=rejection,
                            reason=_D2_REJECTION_REASONS[rejection],
                        )
                    )
                    diagnostics["rejection_reasons"].append(
                        {"object_id": decision.candidate_object_id, "reason": rejection}
                    )
                    continue
                resolution.candidates.append(
                    self._d2_candidate(
                        object_id=decision.candidate_object_id,
                        source_id=str(row.get("source_id", "")),
                        source_version_id=str(row.get("source_version_id", "")),
                        match_kind=EVIDENCE_DESCRIPN,
                        matched_value=mention.text,
                        tier=TIER_DESCRIPN,
                        status=_D2_PROMOTED,
                        reason=(
                            f"descriptive bundle eligible={decision.eligible}; "
                            f"features={decision.feature_count}"
                            + (f"; {decision.rejection_reason}" if decision.rejection_reason else "")
                        ),
                    )
                )
                if decision.eligible:
                    passing.append(decision)
            if not passing:
                reasons = sorted(
                    {
                        str(decision.rejection_reason)
                        for decision in group
                        if decision.rejection_reason
                    }
                )
                diagnostics["abstention_reason"] = (
                    reasons[0]
                    if reasons
                    else "no descriptive candidate satisfied the governed descriptive-evidence bundle"
                )
                continue
            top = max(decision.feature_count for decision in passing)
            leaders = sorted(
                (decision for decision in passing if decision.feature_count == top),
                key=lambda decision: decision.candidate_object_id,
            )
            if len(leaders) > 1:
                resolution.status = AMBIGUOUS
                diagnostics["ambiguity_reason"] = (
                    f"descriptive evidence ties between {len(leaders)} candidates "
                    f"at {top} features"
                )
                continue
            leader = leaders[0]
            resolution.status = RESOLVED_UNIQUE
            resolution.matched_object_id = leader.candidate_object_id
            resolution.canonical_object_id = leader.candidate_object_id
            resolution.evidence.append(
                D2Evidence(
                    tier=TIER_DESCRIPN,
                    kind=EVIDENCE_DESCRIPN,
                    matched_value=mention.text,
                    object_id=leader.candidate_object_id,
                    detail=(
                        "governed descriptive-evidence bundle satisfied; "
                        f"features={leader.feature_count}; "
                        f"matched={list(leader.matched_features)}"
                    ),
                )
            )
            diagnostics["descriptive_inference"] = True
            diagnostics["identity_authority"] = True


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


# ---------------------------------------------------------------------------
# D2 shadow resolution (Phase D2-A1)
# ---------------------------------------------------------------------------
#
# Shadow-only extension implementing the frozen D2 resolver contract
# (docs/PHASE_D2_A0_RESOLVER_CONTRACT.md).  The C5 resolve() path and the C5
# IDENTITY_RELATION_SUPPORT constant above are unchanged; resolve_shadow() is
# deterministic, read-only, and never calls the analyzer, other retrieval
# channels, or any model.  In the shadow resolver only, accepted SAME_AS edges
# are active governed identity evidence, so identity-relation support flips.

D2_IDENTITY_RELATION_SUPPORT = "ACTIVE_SHADOW"

TIER_GOVERNED = "G"
TIER_STRUCTURAL = "S"
TIER_DESCRIPN = "D"
TIER_NONAUTH = "N"

EVIDENCE_CANONICAL_ID = "canonical_object_id"
EVIDENCE_TRUE_ALIAS = "true_alias"
EVIDENCE_CORRECTIVE = "corrective_term"
EVIDENCE_SAME_AS = "same_as"
EVIDENCE_EXACT_SYMBOL = "exact_symbol"
EVIDENCE_EXACT_TITLE = "exact_title"
EVIDENCE_EXACT_PATH = "exact_path"
EVIDENCE_DESCRIPN = "descriptive_inference"

EVIDENCE_KIND_BY_MATCH = {
    MATCH_EXACT_SYMBOL: EVIDENCE_EXACT_SYMBOL,
    MATCH_EXACT_TITLE: EVIDENCE_EXACT_TITLE,
    MATCH_EXACT_PATH: EVIDENCE_EXACT_PATH,
}

_D2_OBJECT_COLUMNS = (
    "object_id,source_id,source_version_id,object_type,title,text,"
    "authority_level,locator,metadata,canonical_locator"
)

_D2_MENTION_KIND_PRIORITY = {
    "accepted_alias": 0,
    "governed_id": 1,
    "analyzer_symbol": 2,
    "explicit_identifier": 3,
    "descriptive": 4,
}

_D2_PROMOTED = "PROMOTED"

_D2_FAILING_STATUSES = {
    UNRESOLVED,
    AMBIGUOUS,
    REJECTED_VERSION,
    REJECTED_SCOPE,
    MISSING_TARGET,
}

_D2_REJECTION_REASONS = {
    MISSING_TARGET: "target object does not exist",
    REJECTED_VERSION: "rejected by locked-version safety",
    REJECTED_SCOPE: "rejected by source-scope safety",
}


@dataclass(frozen=True)
class AcceptedAliasD2:
    """One accepted alias row with the D2 corrective-classification marker."""

    alias_text: str
    normalized_alias: str
    target_object_id: str
    source_version_id: str
    correction_message: str | None


@dataclass(frozen=True)
class D2Evidence:
    """One piece of identity evidence for a D2 resolution (contract Section 7)."""

    tier: str
    kind: str
    matched_value: str
    object_id: str
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier,
            "kind": self.kind,
            "matched_value": self.matched_value,
            "object_id": self.object_id,
            "detail": self.detail,
        }


@dataclass
class D2Resolution:
    """The D2 outcome for one mention: matched representation vs canonical entity."""

    mention_text: str
    mention_kind: str
    support_span: str
    status: str
    matched_object_id: str | None = None
    canonical_object_id: str | None = None
    selected_object_ids: list[str] = field(default_factory=list)
    evidence: list[D2Evidence] = field(default_factory=list)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    version_scope: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "mention_text": self.mention_text,
            "mention_kind": self.mention_kind,
            "support_span": self.support_span,
            "status": self.status,
            "matched_object_id": self.matched_object_id,
            "canonical_object_id": self.canonical_object_id,
            "selected_object_ids": list(self.selected_object_ids),
            "evidence": [item.as_dict() for item in self.evidence],
            "candidates": [dict(item) for item in self.candidates],
            "version_scope": dict(self.version_scope),
            "diagnostics": dict(self.diagnostics),
        }


@dataclass
class D2ResolutionReceipt:
    """The auditable record of one D2 shadow-resolution pass."""

    resolutions: list[D2Resolution] = field(default_factory=list)
    ambiguous_mentions: list[str] = field(default_factory=list)
    unresolved_mentions: list[str] = field(default_factory=list)
    multi_entity_results: list[dict[str, Any]] = field(default_factory=list)
    corrective_mentions: list[dict[str, Any]] = field(default_factory=list)
    resolved_object_ids: list[str] = field(default_factory=list)
    fallback_required: bool = False
    identity_relation_support: str = D2_IDENTITY_RELATION_SUPPORT

    def as_dict(self) -> dict[str, Any]:
        return {
            "identity_relation_support": self.identity_relation_support,
            "resolutions": [resolution.as_dict() for resolution in self.resolutions],
            "ambiguous_mentions": list(self.ambiguous_mentions),
            "unresolved_mentions": list(self.unresolved_mentions),
            "multi_entity_results": [dict(item) for item in self.multi_entity_results],
            "corrective_mentions": [dict(item) for item in self.corrective_mentions],
            "resolved_object_ids": list(self.resolved_object_ids),
            "fallback_required": self.fallback_required,
        }


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
    "D2_IDENTITY_RELATION_SUPPORT",
    "TIER_GOVERNED",
    "TIER_STRUCTURAL",
    "TIER_DESCRIPN",
    "TIER_NONAUTH",
    "EVIDENCE_CANONICAL_ID",
    "EVIDENCE_TRUE_ALIAS",
    "EVIDENCE_CORRECTIVE",
    "EVIDENCE_SAME_AS",
    "EVIDENCE_EXACT_SYMBOL",
    "EVIDENCE_EXACT_TITLE",
    "EVIDENCE_EXACT_PATH",
    "EVIDENCE_DESCRIPN",
    "AcceptedAliasD2",
    "D2Evidence",
    "D2Resolution",
    "D2ResolutionReceipt",
]
