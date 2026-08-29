"""D2 shadow resolution tests (Phase D2-A1).

Follows the C5 FakeConnection/_Rows pattern, extended to answer the new D2
read-only SQL shapes: accepted aliases with the payload correction_message
marker, accepted SAME_AS edges, canonical-entity metadata lookup, and the
canonical relation-feature query.  Deterministic; no live DB, model, or
network.  The production C5 resolve() path is exercised by
tests/unit/test_entity_resolution.py and must stay green.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from panda_agent.entity_resolution import (
    AMBIGUOUS,
    D2_IDENTITY_RELATION_SUPPORT,
    EVIDENCE_CANONICAL_ID,
    EVIDENCE_CORRECTIVE,
    EVIDENCE_DESCRIPN,
    EVIDENCE_SAME_AS,
    EVIDENCE_TRUE_ALIAS,
    IDENTITY_RELATION_SUPPORT,
    MISSING_TARGET,
    REJECTED_SCOPE,
    REJECTED_VERSION,
    RESOLVED_MULTIPLE,
    RESOLVED_UNIQUE,
    D2Resolution,
    TIER_DESCRIPN,
    TIER_GOVERNED,
    TIER_STRUCTURAL,
    UNRESOLVED,
    EntityResolver,
)

try:
    # The Tier D module is delivered concurrently with D2-A1 integration; the
    # Tier D test class is skipped until it exists.
    from panda_agent.descriptive_resolution import (  # noqa: F401
        GovernedEntity,
        build_descriptive_index,
        evaluate_descriptive_mentions,
    )

    _DESCRIPTIVE_AVAILABLE = True
except ImportError:  # pragma: no cover - integration ordering
    _DESCRIPTIVE_AVAILABLE = False

LOCKED = "pandaroot@locked"
CURATED_VERSION = "curated_panda_domain@seed"

_LUMI_FIT_MODEL_ID = "concept.luminosityfit.luminosity_fit_model"
_LUMI_FIT_TEXT = (
    "The model of the LuminosityFit framework that describes the reconstructed "
    "angular distribution of elastic antiproton-proton scattering and from which "
    "the luminosity is extracted. Its physical input is the differential elastic "
    "antiproton-proton cross section with its Coulomb and hadronic "
    "parameterizations; the detector-side effects folded into the model are the "
    "efficiency and acceptance correction, the beam divergence smearing, and the "
    "detector resolution. The model is fitted to the reconstructed track angular "
    "distribution to determine the luminosity. The abstraction is defined by the "
    "LuminosityFit framework chapter of the Pflueger thesis and realized by the "
    "model-and-fit subsystem; it is stable across corpus versions."
)


@dataclass(frozen=True)
class D2Alias:
    """Accepted alias row including the corrective-classification marker."""

    alias_text: str
    normalized_alias: str
    target_object_id: str
    source_version_id: str
    correction_message: str | None = None


def _object_row(
    object_id: str,
    *,
    source_id: str = "pandaroot",
    source_version_id: str = LOCKED,
    object_type: str = "class",
    title: str | None = None,
    symbol: str | None = None,
    path: str | None = None,
    metadata: dict | None = None,
    text: str = "irrelevant",
) -> dict:
    return {
        "object_id": object_id,
        "source_id": source_id,
        "source_version_id": source_version_id,
        "object_type": object_type,
        "title": title or symbol or object_id,
        "text": text,
        "authority_level": "repository",
        "locator": {"path": path, "symbol": symbol, "start_line": 1, "end_line": 2},
        "canonical_locator": f"{path}:{symbol}:1" if path and symbol else None,
        "metadata": metadata or {},
    }


def _canonical_row(
    object_id: str,
    *,
    title: str,
    text: str,
    object_type: str = "physics_concept",
) -> dict:
    return _object_row(
        object_id,
        source_id="curated_panda_domain",
        source_version_id=CURATED_VERSION,
        object_type=object_type,
        title=title,
        text=text,
        metadata={"identity_role": "canonical"},
    )


_COLUMNS = (
    "object_id",
    "source_id",
    "source_version_id",
    "object_type",
    "title",
    "text",
    "authority_level",
    "locator",
    "canonical_locator",
)

# Mirrors _D2_OBJECT_COLUMNS in entity_resolution.py (metadata before
# canonical_locator), so fake tuples zip onto the right column names.
_D2_CANONICAL_COLUMNS = (
    "object_id",
    "source_id",
    "source_version_id",
    "object_type",
    "title",
    "text",
    "authority_level",
    "locator",
    "metadata",
    "canonical_locator",
)


def _exact_hit(row: dict, values: list) -> bool:
    symbol = (row.get("locator") or {}).get("symbol")
    path = (row.get("locator") or {}).get("path")
    basename = path.rsplit("/", 1)[-1] if path else None
    return (
        row.get("title") in values
        or symbol in values
        or path in values
        or basename in values
    )


class FakeConnection:
    """Read-only stand-in answering the C5 and D2 query shapes."""

    def __init__(
        self,
        objects: list[dict],
        aliases: list[D2Alias] = (),
        same_as_edges: list[tuple[str, str, str]] = (),
        feature_edges: list[tuple[str, str, str, str]] = (),
    ) -> None:
        self.objects = objects
        self.aliases = aliases
        # same_as_edges: (subject_id, object_id, review_status)
        self.same_as_edges = same_as_edges
        # feature_edges: (subject_id, predicate, object_id, review_status)
        self.feature_edges = feature_edges
        self.statements: list[tuple[str, tuple]] = []

    def _row(self, object_id: str) -> dict | None:
        return next((row for row in self.objects if row["object_id"] == object_id), None)

    def execute(self, sql: str, params: tuple | None = None):
        self.statements.append((sql, params or ()))
        lowered = sql.casefold()
        if "knowledge_aliases" in lowered:
            return _Rows(
                [
                    (
                        alias.alias_text,
                        alias.normalized_alias,
                        alias.target_object_id,
                        alias.source_version_id,
                        alias.correction_message,
                    )
                    for alias in self.aliases
                ]
            )
        if "same_as" in lowered:
            return _Rows(
                [
                    (subject_id, object_id)
                    for subject_id, object_id, status in self.same_as_edges
                    if status == "accepted"
                ]
            )
        if "identity_role" in lowered:
            canonical = sorted(
                (
                    row
                    for row in self.objects
                    if (row.get("metadata") or {}).get("identity_role") == "canonical"
                ),
                key=lambda row: row["object_id"],
            )
            return _Rows(
                [tuple(row[column] for column in _D2_CANONICAL_COLUMNS) for row in canonical]
            )
        if "relation_edges" in lowered:
            values = set(list(params)[0])
            return _Rows(
                [
                    (
                        subject_id,
                        predicate,
                        object_id,
                        (self._row(subject_id) or {}).get("title"),
                        (self._row(object_id) or {}).get("title"),
                    )
                    for subject_id, predicate, object_id, status in self.feature_edges
                    if status == "accepted" and (subject_id in values or object_id in values)
                ]
            )
        values = list(params)[0] if params else []
        if "object_id=any" in lowered:
            return _Rows(
                [
                    tuple(row[column] for column in _COLUMNS)
                    for row in self.objects
                    if row["object_id"] in values
                ]
            )
        return _Rows(
            [
                tuple(row[column] for column in _COLUMNS)
                for row in self.objects
                if _exact_hit(row, values)
            ]
        )


class _Rows:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows

    def fetchall(self) -> list[tuple]:
        return self._rows


class FakeStorage:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    def connect(self):
        return _Context(self.connection)


class _Context:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, *exc):
        return False


def _plan(**changes) -> dict:
    plan = {
        "intent": "api",
        "target_repositories": ["pandaroot"],
        "resolved_versions": {"pandaroot": "locked"},
        "resolved_aliases": {},
        "symbols": ["SHOULD_NOT_BE_USED"],
        "concepts": [],
        "analysis_diagnostics": {
            "analyzer_accepted_semantic_delta": {"symbols": [], "concepts": []}
        },
    }
    plan.update(changes)
    return plan


def _resolver(
    objects: list[dict],
    aliases: list[D2Alias] | None = None,
    same_as_edges: list[tuple[str, str, str]] | None = None,
    feature_edges: list[tuple[str, str, str, str]] | None = None,
) -> EntityResolver:
    connection = FakeConnection(
        objects, aliases or [], same_as_edges or [], feature_edges or []
    )
    return EntityResolver(FakeStorage(connection), context_sources=("li_2026",))


class D2TierGTests(unittest.TestCase):
    def test_exact_canonical_object_id_resolves_tier_g(self):
        objects = [
            _canonical_row(
                "concept.fixtures.alpha",
                title="Alpha concept",
                text="Curated alpha concept of the fixtures domain.",
            )
        ]
        receipt = _resolver(objects).resolve_shadow(
            "What is concept.fixtures.alpha?", _plan(concepts=["concept.fixtures.alpha"])
        )
        self.assertEqual(len(receipt.resolutions), 1)
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.mention_kind, "governed_id")
        self.assertEqual(resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(resolution.matched_object_id, "concept.fixtures.alpha")
        self.assertEqual(resolution.canonical_object_id, "concept.fixtures.alpha")
        self.assertEqual(len(resolution.evidence), 1)
        self.assertEqual(resolution.evidence[0].tier, TIER_GOVERNED)
        self.assertEqual(resolution.evidence[0].kind, EVIDENCE_CANONICAL_ID)
        self.assertFalse(resolution.diagnostics["canonicalization"])
        self.assertTrue(resolution.diagnostics["identity_authority"])
        self.assertEqual(receipt.resolved_object_ids, ["concept.fixtures.alpha"])
        self.assertFalse(receipt.fallback_required)

    def test_true_identity_alias_resolves_and_canonicalizes(self):
        objects = [
            _canonical_row(
                "data_product.restgas.pid_final_root",
                title="*_pid_final.root",
                text="Boost ROOT output file pattern of the restgas determination.",
                object_type="data_product",
            )
        ]
        aliases = [
            D2Alias(
                "*_pid_final.root",
                "*_pid_final.root",
                "data_product.restgas.pid_final_root",
                CURATED_VERSION,
                None,
            )
        ]
        receipt = _resolver(objects, aliases).resolve_shadow(
            "Which macro writes *_pid_final.root?",
            _plan(concepts=["*_pid_final.root"]),
        )
        resolution = next(
            item for item in receipt.resolutions if item.mention_text == "*_pid_final.root"
        )
        self.assertEqual(resolution.mention_kind, "accepted_alias")
        self.assertEqual(resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(
            resolution.matched_object_id, "data_product.restgas.pid_final_root"
        )
        self.assertEqual(
            resolution.canonical_object_id, "data_product.restgas.pid_final_root"
        )
        self.assertEqual(resolution.evidence[0].tier, TIER_GOVERNED)
        self.assertEqual(resolution.evidence[0].kind, EVIDENCE_TRUE_ALIAS)
        self.assertIn(
            "data_product.restgas.pid_final_root", receipt.resolved_object_ids
        )

    def test_corrective_alias_is_corrective_not_tier_g(self):
        objects = [
            _object_row(
                "configuration.restgas_profile",
                object_type="configuration_key",
                title="restgas_profile",
                symbol=None,
            )
        ]
        message = (
            "No literal file named restgas_profile.txt exists in the corpus; "
            "the configuration key is restgas_profile."
        )
        aliases = [
            D2Alias(
                "restgas_profile.txt",
                "restgas_profile.txt",
                "configuration.restgas_profile",
                LOCKED,
                message,
            )
        ]
        receipt = _resolver(objects, aliases).resolve_shadow(
            "Where does restgas_profile.txt come from?",
            _plan(concepts=["restgas_profile.txt"]),
        )
        self.assertEqual(len(receipt.resolutions), 1)
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, UNRESOLVED)
        self.assertEqual(resolution.mention_kind, "accepted_alias")
        self.assertIsNone(resolution.matched_object_id)
        self.assertIsNone(resolution.canonical_object_id)
        self.assertTrue(resolution.diagnostics["corrective"])
        self.assertEqual(resolution.diagnostics["correction_message"], message)
        self.assertFalse(resolution.diagnostics["identity_authority"])
        self.assertEqual(resolution.evidence[0].tier, "corrective")
        self.assertEqual(resolution.evidence[0].kind, EVIDENCE_CORRECTIVE)
        self.assertEqual(
            receipt.corrective_mentions,
            [
                {
                    "surface_term": "restgas_profile.txt",
                    "target_candidate": "configuration.restgas_profile",
                    "correction_message": message,
                    "identity_authority": False,
                }
            ],
        )
        self.assertNotIn("restgas_profile.txt", receipt.unresolved_mentions)
        self.assertEqual(receipt.resolved_object_ids, [])
        self.assertTrue(receipt.fallback_required)


class D2TierSTests(unittest.TestCase):
    def test_unique_exact_symbol_resolves_tier_s_without_canonicalization(self):
        objects = [_object_row("obj.exact", symbol="PndThing")]
        receipt = _resolver(objects).resolve_shadow(
            "Where is PndThing?", _plan(concepts=["PndThing"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(resolution.matched_object_id, "obj.exact")
        self.assertIsNone(resolution.canonical_object_id)
        self.assertEqual(resolution.evidence[0].tier, TIER_STRUCTURAL)
        self.assertEqual(resolution.evidence[0].kind, "exact_symbol")
        self.assertFalse(receipt.fallback_required)

    def test_exact_title_collision_is_ambiguous_not_resolved_multiple(self):
        objects = [
            _object_row("obj.one", symbol=None, title="event_poca", object_type="data_product"),
            _object_row("obj.two", symbol=None, title="event_poca", object_type="data_product"),
        ]
        receipt = _resolver(objects).resolve_shadow(
            "Which macro produces event_poca?", _plan(concepts=["event_poca"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, AMBIGUOUS)
        self.assertIsNone(resolution.matched_object_id)
        self.assertEqual(
            resolution.diagnostics["ambiguity_reason"],
            "multiple distinct objects share the exact match",
        )
        self.assertEqual(receipt.multi_entity_results, [])
        self.assertIn("event_poca", receipt.ambiguous_mentions)
        self.assertTrue(receipt.fallback_required)

    def test_scope_rejection_recorded(self):
        objects = [
            _object_row(
                "obj.foreign",
                symbol="PndThing",
                source_id="luminosityfit",
                source_version_id="luminosityfit@v",
            )
        ]
        receipt = _resolver(objects).resolve_shadow(
            "Where is PndThing?", _plan(concepts=["PndThing"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, REJECTED_SCOPE)
        # D2-A1R2: the rejected mention triggers the conservative
        # whole-question fallback; with an empty canonical set its evaluated
        # UNRESOLVED abstention is retained alongside the rejection.
        self.assertEqual(
            receipt.unresolved_mentions, ["PndThing", "Where is PndThing?"]
        )
        self.assertTrue(
            any(
                item["object_id"] == "obj.foreign" and item["reason"] == REJECTED_SCOPE
                for item in resolution.diagnostics["rejection_reasons"]
            )
        )
        self.assertTrue(receipt.fallback_required)

    def test_version_rejection_recorded(self):
        objects = [
            _object_row("obj.old", symbol="PndThing", source_version_id="pandaroot@ancient")
        ]
        receipt = _resolver(objects).resolve_shadow(
            "Where is PndThing?", _plan(concepts=["PndThing"])
        )
        self.assertEqual(receipt.resolutions[0].status, REJECTED_VERSION)
        self.assertTrue(receipt.fallback_required)


class D2SameAsTests(unittest.TestCase):
    def _fixtures(self, edge_status: str) -> tuple[list[dict], list[tuple[str, str, str]]]:
        objects = [
            _object_row("object.aaa", symbol="PndLmdThing"),
            _canonical_row(
                "concept.fixtures.lmd_thing",
                title="LMD thing",
                text="The curated LMD thing concept of the fixtures domain.",
            ),
        ]
        edges = [("object.aaa", "concept.fixtures.lmd_thing", edge_status)]
        return objects, edges

    def test_accepted_same_as_canonicalizes_source_native_match(self):
        objects, edges = self._fixtures("accepted")
        receipt = _resolver(objects, same_as_edges=edges).resolve_shadow(
            "Where is PndLmdThing defined?", _plan(concepts=["PndLmdThing"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(resolution.matched_object_id, "object.aaa")
        self.assertEqual(resolution.canonical_object_id, "concept.fixtures.lmd_thing")
        self.assertTrue(resolution.diagnostics["canonicalization"])
        self.assertTrue(resolution.diagnostics["identity_authority"])
        kinds = {item.kind for item in resolution.evidence}
        self.assertEqual(kinds, {"exact_symbol", EVIDENCE_SAME_AS})
        same_as_evidence = next(
            item for item in resolution.evidence if item.kind == EVIDENCE_SAME_AS
        )
        self.assertEqual(same_as_evidence.tier, TIER_GOVERNED)
        self.assertFalse(receipt.fallback_required)

    def test_pending_same_as_never_canonicalizes(self):
        objects, edges = self._fixtures("pending")
        receipt = _resolver(objects, same_as_edges=edges).resolve_shadow(
            "Where is PndLmdThing defined?", _plan(concepts=["PndLmdThing"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(resolution.matched_object_id, "object.aaa")
        self.assertIsNone(resolution.canonical_object_id)
        self.assertFalse(resolution.diagnostics["canonicalization"])
        self.assertFalse(receipt.fallback_required)

    def test_two_canonical_same_as_targets_is_ambiguous(self):
        objects = [
            _object_row("object.aaa", symbol="PndLmdThing"),
            _canonical_row(
                "concept.fixtures.lmd_thing_a",
                title="LMD thing A",
                text="The curated LMD thing concept, variant A.",
            ),
            _canonical_row(
                "concept.fixtures.lmd_thing_b",
                title="LMD thing B",
                text="The curated LMD thing concept, variant B.",
            ),
        ]
        edges = [
            ("object.aaa", "concept.fixtures.lmd_thing_a", "accepted"),
            ("object.aaa", "concept.fixtures.lmd_thing_b", "accepted"),
        ]
        receipt = _resolver(objects, same_as_edges=edges).resolve_shadow(
            "Where is PndLmdThing defined?", _plan(concepts=["PndLmdThing"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, AMBIGUOUS)
        self.assertIsNone(resolution.matched_object_id)
        self.assertIsNone(resolution.canonical_object_id)
        self.assertEqual(
            resolution.diagnostics["ambiguity_reason"],
            "accepted SAME_AS traversal reaches multiple canonical targets",
        )
        self.assertTrue(receipt.fallback_required)

    def test_implements_relation_does_not_canonicalize(self):
        objects = [
            _object_row("object.factory", symbol="PndLmdModelFactory"),
            _canonical_row(
                _LUMI_FIT_MODEL_ID, title="Luminosity fit model", text=_LUMI_FIT_TEXT
            ),
        ]
        feature_edges = [
            ("object.factory", "IMPLEMENTS", _LUMI_FIT_MODEL_ID, "accepted")
        ]
        receipt = _resolver(objects, feature_edges=feature_edges).resolve_shadow(
            "Where is PndLmdModelFactory defined?",
            _plan(concepts=["PndLmdModelFactory"]),
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(resolution.matched_object_id, "object.factory")
        self.assertIsNone(resolution.canonical_object_id)
        self.assertFalse(resolution.diagnostics["canonicalization"])
        self.assertNotIn(EVIDENCE_SAME_AS, [item.kind for item in resolution.evidence])
        self.assertFalse(receipt.fallback_required)


@unittest.skipUnless(
    _DESCRIPTIVE_AVAILABLE, "descriptive_resolution module not yet integrated"
)
class D2TierDTests(unittest.TestCase):
    def test_descriptive_positive_resolves_luminosity_fit_model(self):
        objects = [
            _canonical_row(
                _LUMI_FIT_MODEL_ID, title="Luminosity fit model", text=_LUMI_FIT_TEXT
            )
        ]
        receipt = _resolver(objects).resolve_shadow(
            "the model used to extract luminosity from the LMD angular distribution",
            _plan(),
        )
        span = next(
            item for item in receipt.resolutions if item.mention_kind == "descriptive"
        )
        self.assertEqual(span.mention_text, "the model used to extract luminosity from the LMD angular distribution")
        self.assertEqual(span.status, RESOLVED_UNIQUE)
        self.assertEqual(span.matched_object_id, _LUMI_FIT_MODEL_ID)
        self.assertEqual(span.canonical_object_id, _LUMI_FIT_MODEL_ID)
        self.assertTrue(span.diagnostics["descriptive_inference"])
        self.assertTrue(span.diagnostics["identity_authority"])
        self.assertFalse(span.diagnostics["canonicalization"])
        self.assertEqual(span.evidence[0].tier, TIER_DESCRIPN)
        self.assertEqual(span.evidence[0].kind, EVIDENCE_DESCRIPN)

    def test_descriptive_negative_generic_mention_abstains(self):
        # D2-A1R1: the QE-only concept "the model" is not an authoritative
        # mention; the conservative whole-question fallback runs Tier D and
        # abstains on the single weak feature.
        objects = [
            _canonical_row(
                _LUMI_FIT_MODEL_ID, title="Luminosity fit model", text=_LUMI_FIT_TEXT
            )
        ]
        receipt = _resolver(objects).resolve_shadow(
            "How is the model configured?", _plan(concepts=["the model"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.mention_text, "How is the model configured?")
        self.assertEqual(resolution.mention_kind, "descriptive")
        self.assertEqual(resolution.status, UNRESOLVED)
        self.assertIsNone(resolution.matched_object_id)
        self.assertIsNone(resolution.canonical_object_id)
        self.assertFalse(resolution.diagnostics["descriptive_inference"])
        self.assertFalse(resolution.diagnostics["identity_authority"])
        self.assertTrue(resolution.diagnostics["abstention_reason"])
        self.assertTrue(receipt.fallback_required)

    def test_analyzer_supported_concept_becomes_tier_d_mention(self):
        # D2-A1R1 repair 1: an analyzer-accepted concept with a valid
        # query-grounded support span is an authoritative Tier D mention.
        objects = [
            _canonical_row(
                _LUMI_FIT_MODEL_ID, title="Luminosity fit model", text=_LUMI_FIT_TEXT
            )
        ]
        plan = _plan(
            analysis_diagnostics={
                "analyzer_accepted_semantic_delta": {
                    "concepts": [
                        {
                            "value": "luminosity fit model",
                            "support_spans": ["luminosity fit model"],
                        }
                    ]
                }
            }
        )
        receipt = _resolver(objects).resolve_shadow(
            "How does the luminosity fit model work?", plan
        )
        resolution = next(
            item
            for item in receipt.resolutions
            if item.mention_text == "luminosity fit model"
        )
        self.assertEqual(resolution.mention_kind, "descriptive")
        self.assertEqual(resolution.support_span, "luminosity fit model")
        self.assertEqual(resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(resolution.canonical_object_id, _LUMI_FIT_MODEL_ID)
        self.assertTrue(resolution.diagnostics["descriptive_inference"])

    def test_query_expansion_only_concept_is_not_authoritative(self):
        # D2-A1R1 repair 1 + D2-A1R2 Case A: a concept present only through
        # plan.concepts (query-expansion knowledge) never becomes an
        # authoritative descriptive mention; the whole-question fallback is
        # evaluated and its UNRESOLVED abstention is retained in the receipt.
        objects = [
            _canonical_row(
                "workflow.restgas.profile_correction",
                title="Restgas profile correction workflow",
                text="Workflow correcting the longitudinal restgas profile.",
                object_type="workflow",
            )
        ]
        receipt = _resolver(objects).resolve_shadow(
            "What is the acceptance class?",
            _plan(concepts=["restgas profile correction workflow"]),
        )
        # The QE-only concept never became a mention.
        self.assertNotIn(
            "restgas profile correction workflow",
            {item.mention_text for item in receipt.resolutions},
        )
        # The evaluated whole-question fallback abstention is retained
        # (D2-A1R2: an evaluated abstention is a first-class decision).
        self.assertEqual(len(receipt.resolutions), 1)
        fallback = receipt.resolutions[0]
        self.assertEqual(fallback.mention_text, "What is the acceptance class?")
        self.assertEqual(fallback.mention_kind, "descriptive")
        self.assertEqual(fallback.status, UNRESOLVED)
        self.assertEqual(fallback.candidates, [])
        self.assertIsNone(fallback.matched_object_id)
        self.assertIsNone(fallback.canonical_object_id)
        self.assertEqual(
            receipt.unresolved_mentions, ["What is the acceptance class?"]
        )
        self.assertTrue(receipt.fallback_required)
        self.assertTrue(fallback.diagnostics["abstention_reason"])

    def test_malformed_support_span_fails_closed(self):
        # D2-A1R1 repair 1: support spans that are not substrings of the
        # question fail closed — the concept never becomes a mention and the
        # whole-question fallback takes over.
        objects = [
            _canonical_row(
                _LUMI_FIT_MODEL_ID, title="Luminosity fit model", text=_LUMI_FIT_TEXT
            )
        ]
        plan = _plan(
            analysis_diagnostics={
                "analyzer_accepted_semantic_delta": {
                    "concepts": [
                        {
                            "value": "luminosity fit model",
                            "support_spans": ["span not present in the question"],
                        }
                    ]
                }
            }
        )
        receipt = _resolver(objects).resolve_shadow(
            "How does the luminosity fit model work?", plan
        )
        self.assertNotIn(
            "luminosity fit model",
            {item.mention_text for item in receipt.resolutions},
        )
        fallback = receipt.resolutions[0]
        self.assertEqual(fallback.mention_text, "How does the luminosity fit model work?")
        self.assertEqual(fallback.status, RESOLVED_UNIQUE)
        self.assertEqual(fallback.canonical_object_id, _LUMI_FIT_MODEL_ID)

    def test_malformed_support_with_no_candidate_retains_unresolved(self):
        # D2-A1R2 Case B: the malformed analyzer concept is rejected and the
        # whole-question fallback finds no governed candidate — the evaluated
        # UNRESOLVED abstention must be retained, never silently dropped.
        objects = [
            _canonical_row(
                _LUMI_FIT_MODEL_ID, title="Luminosity fit model", text=_LUMI_FIT_TEXT
            )
        ]
        plan = _plan(
            analysis_diagnostics={
                "analyzer_accepted_semantic_delta": {
                    "concepts": [
                        {
                            "value": "unrelated nonexistent calibration concept",
                            "support_spans": ["span not present in the question"],
                        }
                    ]
                }
            }
        )
        receipt = _resolver(objects).resolve_shadow(
            "What is the unrelated nonexistent calibration concept?", plan
        )
        self.assertNotIn(
            "unrelated nonexistent calibration concept",
            {item.mention_text for item in receipt.resolutions},
        )
        self.assertEqual(len(receipt.resolutions), 1)
        fallback = receipt.resolutions[0]
        self.assertEqual(
            fallback.mention_text,
            "What is the unrelated nonexistent calibration concept?",
        )
        self.assertEqual(fallback.status, UNRESOLVED)
        # One ineligible descriptive decision (the entity ID token "concept"
        # overlaps) is retained as audit evidence with its single_feature
        # rejection; the resolution itself abstains.
        self.assertEqual(len(fallback.candidates), 1)
        self.assertIn("single_feature", fallback.candidates[0]["reason"])
        self.assertIsNone(fallback.matched_object_id)
        self.assertTrue(fallback.diagnostics["abstention_reason"])
        self.assertIn(
            "What is the unrelated nonexistent calibration concept?",
            receipt.unresolved_mentions,
        )
        self.assertTrue(receipt.fallback_required)

    def test_generic_unsupported_query_retains_unresolved_fallback(self):
        # D2-A1R2 Case C: a generic unsupported query yields exactly one
        # descriptive fallback resolution with UNRESOLVED, zero candidates,
        # populated unresolved_mentions, and fallback_required = true — an
        # observable resolver decision, not an empty receipt.
        objects = [
            _canonical_row(
                "workflow.restgas.profile_correction",
                title="Restgas profile correction workflow",
                text="Workflow correcting the longitudinal restgas profile.",
                object_type="workflow",
            )
        ]
        receipt = _resolver(objects).resolve_shadow(
            "What is the unrelated nonexistent calibration concept?", _plan()
        )
        self.assertEqual(len(receipt.resolutions), 1)
        fallback = receipt.resolutions[0]
        self.assertEqual(fallback.mention_kind, "descriptive")
        self.assertEqual(
            fallback.support_span,
            "What is the unrelated nonexistent calibration concept?",
        )
        self.assertEqual(fallback.status, UNRESOLVED)
        self.assertEqual(fallback.candidates, [])
        self.assertTrue(
            fallback.diagnostics["abstention_reason"]
        )
        self.assertIn(
            "What is the unrelated nonexistent calibration concept?",
            receipt.unresolved_mentions,
        )
        self.assertTrue(receipt.fallback_required)

    def test_descriptive_tie_is_ambiguous(self):
        objects = [
            _canonical_row(
                "concept.fixtures.alpha_fit",
                title="Alpha fit model",
                text=(
                    "The model that describes the alpha angular distribution of the "
                    "simulated events and from which the alpha luminosity is "
                    "extracted. The abstraction belongs to the fixtures curated "
                    "domain and is stable across corpus versions."
                ),
            ),
            _canonical_row(
                "concept.fixtures.beta_fit",
                title="Beta fit model",
                text=(
                    "The model that describes the beta angular distribution of the "
                    "simulated events and from which the beta luminosity is "
                    "extracted. The abstraction belongs to the fixtures curated "
                    "domain and is stable across corpus versions."
                ),
            ),
        ]
        plan = _plan(
            analysis_diagnostics={
                "analyzer_accepted_semantic_delta": {
                    "concepts": [
                        {
                            "value": "the fit model used for the angular distribution",
                            "support_spans": [
                                "the fit model used for the angular distribution"
                            ],
                        }
                    ]
                }
            }
        )
        receipt = _resolver(objects).resolve_shadow(
            "Which is the fit model used for the angular distribution?", plan
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(
            resolution.mention_text,
            "the fit model used for the angular distribution",
        )
        self.assertEqual(resolution.status, AMBIGUOUS)
        self.assertIsNone(resolution.matched_object_id)
        self.assertTrue(
            resolution.diagnostics["ambiguity_reason"].startswith(
                "descriptive evidence ties"
            )
        )
        promoted = {
            item["object_id"]
            for item in resolution.candidates
            if item["status"] == "PROMOTED"
        }
        self.assertEqual(
            promoted,
            {"concept.fixtures.alpha_fit", "concept.fixtures.beta_fit"},
        )
        self.assertTrue(receipt.fallback_required)


class D2MultipleTests(unittest.TestCase):
    def test_plural_mention_without_direct_match_abstains(self):
        # D2-A1R1 repair 3: a trailing-s mention is never singularized into
        # multi-entity promotion; without a direct governed match it abstains.
        objects = [
            _object_row("obj.one", symbol="PndThing", object_type="class"),
            _object_row("obj.two", symbol="PndThing", object_type="function"),
        ]
        receipt = _resolver(objects).resolve_shadow(
            "List all PndThings", _plan(concepts=["PndThings"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.mention_text, "PndThings")
        self.assertEqual(resolution.status, UNRESOLVED)
        self.assertIsNone(resolution.matched_object_id)
        self.assertEqual(resolution.selected_object_ids, [])
        self.assertEqual(receipt.multi_entity_results, [])
        self.assertIn("PndThings", receipt.unresolved_mentions)
        self.assertTrue(receipt.fallback_required)

    def test_trailing_s_identifier_is_not_singularized(self):
        # A technical identifier ending in "s" whose singular form would match
        # several records must not be promoted to RESOLVED_MULTIPLE; it simply
        # does not match and the resolver abstains.
        objects = [
            _object_row("obj.one", symbol="PndThing", object_type="class"),
            _object_row("obj.two", symbol="PndThing", object_type="function"),
        ]
        receipt = _resolver(objects).resolve_shadow(
            "How does PndThings behave?", _plan(concepts=["PndThings"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, UNRESOLVED)
        self.assertEqual(resolution.selected_object_ids, [])
        self.assertNotEqual(resolution.status, RESOLVED_MULTIPLE)

    def test_singular_exact_collision_is_ambiguous(self):
        # Multiple exact candidates for a singular mention without genuine
        # multi-entity evidence are AMBIGUOUS (D2 supersession of C5).
        objects = [
            _object_row("obj.one", symbol="PndThing", object_type="class"),
            _object_row("obj.two", symbol="PndThing", object_type="function"),
        ]
        receipt = _resolver(objects).resolve_shadow(
            "Where is PndThing?", _plan(concepts=["PndThing"])
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, AMBIGUOUS)
        self.assertIn("PndThing", receipt.ambiguous_mentions)
        self.assertTrue(receipt.fallback_required)

    def test_resolved_multiple_schema_remains_representable(self):
        # D2-A1R1 repair 3: the RESOLVED_MULTIPLE schema (selected_object_ids,
        # multi-entity receipt accounting) stays representable even though no
        # natural A1 mechanism promotes to it.
        resolution = D2Resolution(
            mention_text="the two detectors",
            mention_kind="descriptive",
            support_span="the two detectors",
            status=RESOLVED_MULTIPLE,
            selected_object_ids=["object.a", "object.b"],
        )
        payload = resolution.as_dict()
        self.assertEqual(payload["status"], RESOLVED_MULTIPLE)
        self.assertEqual(payload["selected_object_ids"], ["object.a", "object.b"])

    def test_tier_d_evidence_is_mention_local(self):
        # D2-A1R1 repair 2: descriptive evidence is computed from each
        # mention's own grounded support text.  Under the previous
        # whole-question token implementation, the decoy entity
        # concept.fixtures.model_workflow_engine would borrow "workflow" and
        # "engine" from the second mention and tie with the first mention,
        # producing a wrong AMBIGUOUS.  With mention-local isolation both
        # mentions resolve to their own entities.
        objects = [
            _canonical_row(
                "concept.fixtures.luminosity_fit_model",
                title="Luminosity fit model",
                text=_LUMI_FIT_TEXT,
            ),
            _canonical_row(
                "concept.fixtures.model_workflow_engine",
                title="Model workflow engine",
                text=(
                    "A model workflow engine fixture abstraction for the "
                    "curated fixtures domain and is stable across corpus versions."
                ),
            ),
        ]
        plan = _plan(
            analysis_diagnostics={
                "analyzer_accepted_semantic_delta": {
                    "concepts": [
                        {
                            "value": "luminosity fit model",
                            "support_spans": ["luminosity fit model"],
                        },
                        {
                            "value": "workflow engine",
                            "support_spans": ["workflow engine"],
                        },
                    ]
                }
            }
        )
        receipt = _resolver(objects).resolve_shadow(
            "How does the luminosity fit model compare to the workflow engine?",
            plan,
        )
        by_mention = {
            item.mention_text: item for item in receipt.resolutions
        }
        first = by_mention["luminosity fit model"]
        second = by_mention["workflow engine"]
        self.assertEqual(first.status, RESOLVED_UNIQUE)
        self.assertEqual(
            first.canonical_object_id, "concept.fixtures.luminosity_fit_model"
        )
        self.assertEqual(second.status, RESOLVED_UNIQUE)
        self.assertEqual(
            second.canonical_object_id, "concept.fixtures.model_workflow_engine"
        )
        first_evidence = next(
            item for item in first.evidence if item.tier == TIER_DESCRIPN
        )
        self.assertIn("luminosity", first_evidence.detail)
        self.assertNotIn("workflow", first_evidence.detail)
        self.assertNotIn("engine", first_evidence.detail)
        self.assertEqual(receipt.ambiguous_mentions, [])


class D2ReceiptTests(unittest.TestCase):
    def test_receipt_shape_and_active_shadow_support(self):
        objects = [_object_row("obj.exact", symbol="PndThing")]
        receipt = _resolver(objects).resolve_shadow(
            "Where is PndThing?", _plan(concepts=["PndThing"])
        )
        payload = receipt.as_dict()
        self.assertEqual(
            set(payload),
            {
                "identity_relation_support",
                "resolutions",
                "ambiguous_mentions",
                "unresolved_mentions",
                "multi_entity_results",
                "corrective_mentions",
                "resolved_object_ids",
                "fallback_required",
            },
        )
        self.assertEqual(payload["identity_relation_support"], "ACTIVE_SHADOW")
        self.assertEqual(D2_IDENTITY_RELATION_SUPPORT, "ACTIVE_SHADOW")
        # The C5 constant and C5 receipt vocabulary stay untouched.
        self.assertEqual(IDENTITY_RELATION_SUPPORT, "NOT_AVAILABLE")
        resolution = payload["resolutions"][0]
        self.assertEqual(
            set(resolution),
            {
                "mention_text",
                "mention_kind",
                "support_span",
                "status",
                "matched_object_id",
                "canonical_object_id",
                "selected_object_ids",
                "evidence",
                "candidates",
                "version_scope",
                "diagnostics",
            },
        )
        self.assertEqual(
            set(resolution["diagnostics"]),
            {
                "canonicalization",
                "descriptive_inference",
                "corrective",
                "correction_message",
                "identity_authority",
                "ambiguity_reason",
                "abstention_reason",
                "rejection_reasons",
            },
        )
        self.assertEqual(
            resolution["version_scope"],
            {
                "allowed_sources": ["pandaroot", "li_2026", "curated_panda_domain"],
                "locked_versions": {"pandaroot": "pandaroot@locked"},
            },
        )

    def test_deterministic_repeated_execution(self):
        objects = [
            _object_row("object.aaa", symbol="PndLmdThing"),
            _canonical_row(
                "concept.fixtures.lmd_thing",
                title="LMD thing",
                text="The curated LMD thing concept of the fixtures domain.",
            ),
        ]
        edges = [("object.aaa", "concept.fixtures.lmd_thing", "accepted")]
        aliases = [
            D2Alias("*_pid_final.root", "*_pid_final.root", "concept.fixtures.lmd_thing", CURATED_VERSION)
        ]
        resolver = _resolver(objects, aliases, same_as_edges=edges)
        question = "Where is PndLmdThing defined for *_pid_final.root?"
        first = resolver.resolve_shadow(question, _plan(concepts=["PndLmdThing"])).as_dict()
        second = resolver.resolve_shadow(question, _plan(concepts=["PndLmdThing"])).as_dict()
        self.assertEqual(first, second)

    def test_resolver_performs_only_read_only_queries(self):
        objects = [
            _object_row("object.aaa", symbol="PndLmdThing"),
            _canonical_row(
                "concept.fixtures.lmd_thing",
                title="LMD thing",
                text="The curated LMD thing concept of the fixtures domain.",
            ),
        ]
        aliases = [
            D2Alias(
                "restgas_profile.txt",
                "restgas_profile.txt",
                "object.aaa",
                LOCKED,
                "corrective",
            )
        ]
        edges = [("object.aaa", "concept.fixtures.lmd_thing", "accepted")]
        feature_edges = [("object.aaa", "CONSUMES", "concept.fixtures.lmd_thing", "accepted")]
        storage = FakeStorage(
            FakeConnection(objects, aliases, edges, feature_edges)
        )
        EntityResolver(storage).resolve_shadow(
            "Where is PndLmdThing defined for restgas_profile.txt?",
            _plan(concepts=["PndLmdThing"]),
        )
        for sql, _params in storage.connection.statements:
            self.assertNotRegex(
                sql.casefold(), r"\b(insert|update|delete|upsert|create|drop|alter)\b"
            )


class ShadowSmokeTests(unittest.TestCase):
    """Tiny read-only structured-knowledge smoke (D2-A1 §41): one combined
    pass over the six representative resolution cases.  Not a benchmark; no
    ranking, QA, model, or Gold/Novel data."""

    def _fixtures(self):
        objects = [
            _canonical_row(
                _LUMI_FIT_MODEL_ID, title="Luminosity fit model", text=_LUMI_FIT_TEXT
            ),
            _canonical_row(
                "workflow.restgas.first_pass_poca",
                title="Restgas first-pass POCA analysis",
                text="First-pass analysis process of the RestgasDetermination "
                "two-pass reconstruction: it consumes the first-pass PID "
                "product, performs the event-by-event POCA vertex "
                "extrapolation of target-spectrometer tracks, and writes the "
                "boost ROOT output containing the event_poca tree.",
                object_type="workflow",
            ),
            _object_row(
                "data_product.restgas.pid_root",
                source_id="restgas_determination",
                source_version_id="restgas_determination@oct19",
                object_type="data_product",
                title="*_pid.root",
            ),
            _object_row(
                "data_product.restgas.boost_root",
                source_id="restgas_determination",
                source_version_id="restgas_determination@oct19",
                object_type="data_product",
                title="*_boost.root",
            ),
            _object_row(
                "data_product.restgas.pid_final_root",
                source_id="restgas_determination",
                source_version_id="restgas_determination@oct19",
                object_type="data_product",
                title="*_pid_final.root",
                metadata={"identity_role": "canonical"},
            ),
            _object_row(
                "object.trackq",
                symbol="PndLmdTrackQ",
                object_type="class",
                path="detectors/lmd/LmdQA/PndLmdTrackQ.cxx",
            ),
        ]
        aliases = [
            D2Alias(
                alias_text="*_pid_final.root",
                normalized_alias="*_pid_final.root",
                target_object_id="data_product.restgas.pid_final_root",
                source_version_id="restgas_determination@oct19",
            ),
            D2Alias(
                alias_text="restgas_profile.txt",
                normalized_alias="restgas_profile.txt",
                target_object_id="configuration.restgas_profile",
                source_version_id="restgas_determination@oct19",
                correction_message=(
                    "The locked corpus contains no literal file named "
                    "restgas_profile.txt; it uses the restgas_profile "
                    "configuration key and concrete restgas_16012024_*.txt "
                    "profile files."
                ),
            ),
        ]
        feature_edges = [
            (
                "workflow.restgas.first_pass_poca",
                "CONSUMES",
                "data_product.restgas.pid_root",
                "accepted",
            ),
            (
                "workflow.restgas.first_pass_poca",
                "PRODUCES",
                "data_product.restgas.boost_root",
                "accepted",
            ),
        ]
        return objects, aliases, feature_edges

    def test_six_case_shadow_smoke(self):
        objects, aliases, feature_edges = self._fixtures()
        resolver = _resolver(objects, aliases, feature_edges=feature_edges)

        def by_status(question, plan_changes=None):
            receipt = resolver.resolve_shadow(question, _plan(**(plan_changes or {})))
            return {r.mention_text: r for r in receipt.resolutions}, receipt

        # 1. exact technical identifier (Tier S, source-native; no canonical).
        resolutions, _ = by_status("How does PndLmdTrackQ work?")
        hit = resolutions["PndLmdTrackQ"]
        self.assertEqual(hit.status, RESOLVED_UNIQUE)
        self.assertEqual(hit.matched_object_id, "object.trackq")
        self.assertIsNone(hit.canonical_object_id)

        # 2. true alias (Tier G, canonicalizes to the target data product).
        resolutions, _ = by_status(
            "Which file is *_pid_final.root?",
            {"target_repositories": ["restgas_determination", "pandaroot"]},
        )
        hit = resolutions["*_pid_final.root"]
        self.assertEqual(hit.status, RESOLVED_UNIQUE)
        self.assertEqual(hit.evidence[0].tier, TIER_GOVERNED)
        self.assertEqual(hit.canonical_object_id, "data_product.restgas.pid_final_root")

        # 3. corrective term (not Tier G; correction surfaced; fallback True).
        resolutions, receipt = by_status(
            "Where is restgas_profile.txt read?",
            {"target_repositories": ["restgas_determination", "pandaroot"]},
        )
        hit = resolutions["restgas_profile.txt"]
        self.assertEqual(hit.status, UNRESOLVED)
        self.assertEqual(hit.evidence[0].kind, EVIDENCE_CORRECTIVE)
        self.assertFalse(hit.diagnostics["identity_authority"])
        self.assertIn(hit.mention_text, receipt.corrective_mentions[0]["surface_term"])
        self.assertTrue(receipt.fallback_required)

        # 4. LuminosityFit descriptive paraphrase (Tier D bundle).
        resolutions, _ = by_status(
            "the model used to extract luminosity from the LMD angular distribution"
        )
        hit = next(
            r
            for r in resolutions.values()
            if r.mention_kind == "descriptive"
        )
        self.assertEqual(hit.status, RESOLVED_UNIQUE)
        self.assertEqual(hit.canonical_object_id, _LUMI_FIT_MODEL_ID)
        self.assertTrue(hit.diagnostics["descriptive_inference"])

        # 5. POCA descriptive paraphrase (Tier D with structured facts).
        resolutions, _ = by_status(
            "the step that reads the first PID output and writes the boost ROOT file"
        )
        hit = next(
            r
            for r in resolutions.values()
            if r.mention_kind == "descriptive"
        )
        self.assertEqual(hit.status, RESOLVED_UNIQUE)
        self.assertEqual(hit.canonical_object_id, "workflow.restgas.first_pass_poca")

        # 6. generic unresolved phrase.
        resolutions, receipt = by_status("Explain the model", _plan(concepts=["the model"]))
        hit = resolutions["Explain the model"]
        self.assertEqual(hit.status, UNRESOLVED)
        self.assertTrue(receipt.fallback_required)

        # Read-only guarantee across the whole smoke.
        for sql, _params in resolver.storage.connection.statements:
            self.assertNotRegex(
                sql.casefold(), r"\b(insert|update|delete|upsert|create|drop|alter)\b"
            )


if __name__ == "__main__":
    unittest.main()
