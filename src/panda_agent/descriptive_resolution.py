"""Deterministic lexical/structured descriptive (Tier D) resolution.

Implements the bounded descriptive-inference mechanism of the resolver
contract (docs/PHASE_D2_A0_RESOLVER_CONTRACT.md Section 4 Tier D, Section 12)
over a bounded governed canonical entity set:

- pure deterministic token matching; no SQL, IO, network, model, or
  query-expansion content; no scores beyond feature counts;
- eligibility requires multiple compatible descriptive features
  (``feature_count >= 2``) and canonical identity role (weak-signal
  prohibition: a single feature never resolves identity);
- competition is resolved by explicit dominance: a candidate is dominant only
  when eligible and strictly more question tokens match it than every other
  matching candidate; ties are never dominant (AMBIGUOUS support).

Tokenization: strings are lowercased, camelCase identifiers are split into
parts (``PndLmdModelFactory`` -> pnd lmd model factory), and ``[a-z0-9]+``
word tokens are extracted (so ``_``/``-``/``.``/``/`` act as separators,
``*_pid_final.root`` -> pid final root). Tokens shorter than 3 characters and
the following minimal generic English stopword set are dropped from BOTH the
question and all feature sources: the, a, an, of, to, for, in, on, and, or,
is, are, was, were, be, been, that, which, this, these, those, by, as, at,
into, from, with, used, using, its, their.

Feature sources per entity: title tokens, object_id segment tokens,
object_type tokens, curated text tokens, and the caller-supplied
``relation_features[object_id]`` strings (predicate names plus related
ID/title strings).

``rejection_reason`` values: ``"non_canonical"`` (identity_role is not
canonical, checked first), ``"single_feature"`` (fewer than 2 matched
features), ``"tied_with_competitor"`` (eligible but not dominant, i.e. some
other matching candidate has at least as many matched features). ``None``
means the candidate is eligible and dominant.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

__all__ = [
    "GovernedEntity",
    "DescriptiveDecision",
    "DescriptiveIndex",
    "build_descriptive_index",
    "evaluate_descriptive_mentions",
]

_MIN_TOKEN_LENGTH = 3
_MIN_DESCRIPTIVE_FEATURES = 2
_CAMEL_BOUNDARY_LOWER_UPPER = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_CAMEL_BOUNDARY_ACRONYM = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])")
_WORD_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset({
    "the", "a", "an", "of", "to", "for", "in", "on", "and", "or", "is", "are",
    "was", "were", "be", "been", "that", "which", "this", "these", "those",
    "by", "as", "at", "into", "from", "with", "used", "using", "its", "their",
})


def _tokenize(value: str) -> tuple[str, ...]:
    """Split camelCase/snake identifiers and keep content tokens."""
    split = _CAMEL_BOUNDARY_LOWER_UPPER.sub(" ", value)
    split = _CAMEL_BOUNDARY_ACRONYM.sub(" ", split)
    tokens = _WORD_RE.findall(split.lower())
    return tuple(
        token for token in tokens
        if len(token) >= _MIN_TOKEN_LENGTH and token not in _STOPWORDS
    )


@dataclass(frozen=True)
class GovernedEntity:
    object_id: str
    object_type: str
    source_id: str
    source_version_id: str
    title: str
    text: str
    identity_role: str  # e.g. "canonical"


@dataclass(frozen=True)
class DescriptiveDecision:
    mention: str
    candidate_object_id: str
    eligible: bool
    matched_features: tuple[str, ...]
    feature_count: int
    competing: tuple[dict, ...]
    dominance: bool
    rejection_reason: str | None


class DescriptiveIndex:
    """Immutable feature index over governed entities (built once per call)."""

    def __init__(
        self,
        entities: Mapping[str, GovernedEntity],
        features: Mapping[str, frozenset[str]],
    ) -> None:
        self._entities: Mapping[str, GovernedEntity] = MappingProxyType(dict(entities))
        self._features: Mapping[str, frozenset[str]] = MappingProxyType(dict(features))

    @property
    def entities(self) -> Mapping[str, GovernedEntity]:
        return self._entities

    @property
    def features(self) -> Mapping[str, frozenset[str]]:
        return self._features


def build_descriptive_index(
    entities: Iterable[GovernedEntity],
    relation_features: Mapping[str, tuple[str, ...]] = MappingProxyType({}),
) -> DescriptiveIndex:
    """Build the deterministic feature index for the governed entity set."""
    entity_map: dict[str, GovernedEntity] = {}
    feature_map: dict[str, frozenset[str]] = {}
    for entity in entities:
        sources = (entity.title, entity.object_id, entity.object_type, entity.text)
        tokens = {token for source in sources for token in _tokenize(source)}
        for relation in relation_features.get(entity.object_id, ()):
            tokens.update(_tokenize(relation))
        feature_map[entity.object_id] = frozenset(tokens)
        entity_map[entity.object_id] = entity
    return DescriptiveIndex(entity_map, feature_map)


def _rejection_reason(
    entity: GovernedEntity,
    feature_count: int,
    dominance: bool,
) -> str | None:
    if dominance:
        return None
    if entity.identity_role != "canonical":
        return "non_canonical"
    if feature_count < _MIN_DESCRIPTIVE_FEATURES:
        return "single_feature"
    return "tied_with_competitor"


def evaluate_descriptive_mentions(
    question: str,
    mentions: Sequence[str],
    index: DescriptiveIndex,
) -> list[DescriptiveDecision]:
    """Evaluate descriptive mentions against the bounded governed entity set.

    Returns one decision per (mention, candidate) pair with >= 1 matched
    feature, sorted by (feature_count desc, candidate_object_id asc).
    """
    question_tokens = frozenset(_tokenize(question))
    decisions: list[DescriptiveDecision] = []
    for mention in mentions:
        matches: list[tuple[str, tuple[str, ...], bool]] = []
        for object_id in sorted(index.entities):
            matched = tuple(sorted(index.features[object_id] & question_tokens))
            if not matched:
                continue
            entity = index.entities[object_id]
            eligible = len(matched) >= _MIN_DESCRIPTIVE_FEATURES and entity.identity_role == "canonical"
            matches.append((object_id, matched, eligible))
        for object_id, matched, eligible in matches:
            feature_count = len(matched)
            others = [(oid, m) for oid, m, _ in matches if oid != object_id]
            competing = tuple(
                {
                    "object_id": other_id,
                    "feature_count": len(other_matched),
                    "matched_features": other_matched,
                }
                for other_id, other_matched in sorted(
                    others, key=lambda item: (-len(item[1]), item[0])
                )
            )
            dominance = eligible and all(
                feature_count > len(other_matched) for _, other_matched in others
            )
            decisions.append(
                DescriptiveDecision(
                    mention=mention,
                    candidate_object_id=object_id,
                    eligible=eligible,
                    matched_features=matched,
                    feature_count=feature_count,
                    competing=competing,
                    dominance=dominance,
                    rejection_reason=_rejection_reason(
                        entity, feature_count, dominance
                    ),
                )
            )
    decisions.sort(key=lambda decision: (-decision.feature_count, decision.candidate_object_id))
    return decisions
