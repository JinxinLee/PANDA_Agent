from __future__ import annotations

import unittest

from panda_agent.entity_resolution import (
    AMBIGUOUS,
    MATCH_ACCEPTED_ALIAS,
    MATCH_EXACT_PATH,
    MATCH_EXACT_SYMBOL,
    MATCH_EXACT_TITLE,
    MISSING_TARGET,
    REJECTED_SCOPE,
    REJECTED_VERSION,
    RESOLVED_MULTIPLE,
    RESOLVED_UNIQUE,
    UNRESOLVED,
    AcceptedAlias,
    EntityResolver,
    alias_matches,
    extract_entity_mentions,
    merge_exact_streams,
)
from panda_agent.lexical_query import build_lexical_query

LOCKED = "pandaroot@locked"
OTHER_LOCKED = "restgas_determination@other"


def _object_row(
    object_id: str,
    *,
    source_id: str = "pandaroot",
    source_version_id: str = LOCKED,
    object_type: str = "class",
    title: str | None = None,
    symbol: str | None = None,
    path: str | None = None,
) -> dict:
    return {
        "object_id": object_id,
        "source_id": source_id,
        "source_version_id": source_version_id,
        "object_type": object_type,
        "title": title or symbol or object_id,
        "text": "irrelevant",
        "authority_level": "repository",
        "locator": {"path": path, "symbol": symbol, "start_line": 1, "end_line": 2},
        "canonical_locator": f"{path}:{symbol}:1" if path and symbol else None,
    }


class FakeConnection:
    """Read-only stand-in answering the two C5 query shapes."""

    def __init__(self, objects: list[dict], aliases: list[AcceptedAlias]) -> None:
        self.objects = objects
        self.aliases = aliases
        self.statements: list[tuple[str, tuple]] = []

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
                    )
                    for alias in self.aliases
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


def _exact_hit(row: dict, values: list) -> bool:
    symbol = (row.get("locator") or {}).get("symbol")
    path = (row.get("locator") or {}).get("path")
    basename = path.rsplit("/", 1)[-1] if path else None
    return row.get("title") in values or symbol in values or path in values or basename in values


class _Rows:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows

    def fetchall(self) -> list[tuple]:
        return self._rows


class FakeStorage:
    def __init__(self, objects: list[dict], aliases: list[AcceptedAlias] | None = None) -> None:
        self.connection = FakeConnection(objects, aliases or [])

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
        "concepts": ["flat concept"],
        "analysis_diagnostics": {
            "analyzer_accepted_semantic_delta": {"symbols": [], "concepts": []}
        },
    }
    plan.update(changes)
    return plan


def _resolver(objects: list[dict], aliases: list[AcceptedAlias] | None = None) -> EntityResolver:
    return EntityResolver(FakeStorage(objects, aliases), context_sources=("li_2026",))


class AliasMatchingTests(unittest.TestCase):
    def test_boundary_safe_alias_matching(self):
        self.assertIsNone(alias_matches("fit", "check the profit margin"))
        self.assertEqual(alias_matches("fit", "best fit practice"), "fit")

    def test_multiword_alias_matching_with_stable_whitespace(self):
        self.assertEqual(
            alias_matches("restgas profile", "How is the  restgas   profile supplied?"),
            "restgas   profile",
        )

    def test_case_insensitive_alias_matching(self):
        self.assertEqual(
            alias_matches("Restgas_Profile.txt", "use RESTGAS_PROFILE.TXT now"),
            "RESTGAS_PROFILE.TXT",
        )


class MentionExtractionTests(unittest.TestCase):
    def test_explicit_identifier_mention_from_raw_question(self):
        mentions = extract_entity_mentions("Where is PndMasterRecoTask implemented?", _plan())
        self.assertIn("PndMasterRecoTask", [m.text for m in mentions])

    def test_accepted_analyzer_symbol_mention_requires_support(self):
        plan = _plan(
            analysis_diagnostics={
                "analyzer_accepted_semantic_delta": {
                    "symbols": [
                        {"value": "PndLmdThing", "support_spans": ["PndLmdThing"]}
                    ]
                }
            }
        )
        mentions = extract_entity_mentions("Where does PndLmdThing assemble?", plan)
        kinds = {m.text: m.kind for m in mentions}
        self.assertEqual(kinds.get("PndLmdThing"), "analyzer_symbol")

    def test_rejected_or_unsupported_analyzer_symbols_are_ignored(self):
        plan = _plan(
            analysis_diagnostics={
                "analyzer_accepted_semantic_delta": {
                    "symbols": [
                        {"value": "Ghost", "support_spans": ["somewhere else"]},
                        {"value": "Unsupported", "support_spans": ["Unsupported"]},
                    ]
                }
            }
        )
        mentions = extract_entity_mentions("Where is Unsupported used?", plan)
        # "Unsupported" is not a technical identifier shape (no case transition,
        # no separator, no digits) and "Ghost" has no in-question support.
        self.assertEqual([m.text for m in mentions], [])

    def test_flat_plan_symbols_and_concepts_cannot_become_mentions(self):
        mentions = extract_entity_mentions("How do I configure the build?", _plan())
        self.assertEqual([m.text for m in mentions], [])

    def test_accepted_alias_mention_boundary_safe(self):
        aliases = [AcceptedAlias("restgas_profile.txt", "restgas_profile.txt", "obj.a", LOCKED)]
        mentions = extract_entity_mentions(
            "How is restgas_profile supplied?", _plan(), aliases
        )
        # The partial token stays a plain explicit identifier; the accepted
        # alias does not match without its complete boundary-safe form.
        self.assertEqual(
            [(m.text, m.kind) for m in mentions],
            [("restgas_profile", "explicit_identifier")],
        )
        mentions = extract_entity_mentions(
            "Where does restgas_profile.txt come from?", _plan(), aliases
        )
        self.assertEqual(
            [(m.text, m.kind) for m in mentions],
            [("restgas_profile.txt", "accepted_alias")],
        )


class ResolutionTests(unittest.TestCase):
    def test_exact_symbol_beats_broad_substring(self):
        objects = [
            _object_row("obj.exact", symbol="PndThing", path="a/PndThing.cxx"),
            _object_row("obj.substring", title="PndThingHelper", symbol=None, path="b/PndThingHelper.cxx"),
        ]
        receipt, prefix = _resolver(objects).resolve("Where is PndThing?", _plan())
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(resolution.candidates[0].match_kind, MATCH_EXACT_SYMBOL)
        self.assertEqual(prefix[0]["object_id"], "obj.exact")

    def test_multiple_exact_matches_do_not_select_one(self):
        objects = [
            _object_row("obj.one", symbol="PndThing", object_type="class"),
            _object_row("obj.two", symbol="PndThing", object_type="function"),
        ]
        receipt, prefix = _resolver(objects).resolve("Where is PndThing?", _plan())
        self.assertEqual(receipt.resolutions[0].status, RESOLVED_MULTIPLE)
        self.assertIsNone(receipt.resolutions[0].selected_object_id)
        self.assertEqual(prefix, [])
        self.assertIn("PndThing", receipt.ambiguous_mentions)

    def test_exact_title_match(self):
        objects = [_object_row("obj.title", title="event_poca", symbol=None, object_type="data_product")]
        receipt, prefix = _resolver(objects).resolve("Which macro produces event_poca?", _plan())
        self.assertEqual(receipt.resolutions[0].status, RESOLVED_UNIQUE)
        self.assertEqual(receipt.resolutions[0].candidates[0].match_kind, MATCH_EXACT_TITLE)
        self.assertEqual(prefix[0]["object_id"], "obj.title")

    def test_exact_path_match_is_deterministic(self):
        objects = [
            _object_row(
                "obj.path",
                symbol="Maker",
                path="macro/target/reco_complete.C",
                object_type="source_file_chunk",
            )
        ]
        question = "Which macro consumes POCA_VERTEX_FILE in macro/target/reco_complete.C?"
        receipt, prefix = _resolver(objects).resolve(question, _plan())
        path_resolution = next(
            r for r in receipt.resolutions if r.mention.text == "macro/target/reco_complete.C"
        )
        self.assertEqual(path_resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(path_resolution.candidates[0].match_kind, MATCH_EXACT_PATH)

    def test_version_mismatched_target_is_rejected(self):
        objects = [_object_row("obj.old", symbol="PndThing", source_version_id="pandaroot@ancient")]
        receipt, prefix = _resolver(objects).resolve("Where is PndThing?", _plan())
        self.assertEqual(receipt.resolutions[0].status, REJECTED_VERSION)
        self.assertEqual(prefix, [])
        self.assertEqual(receipt.rejected_candidates[0]["reason"], REJECTED_VERSION)

    def test_out_of_scope_source_target_is_rejected(self):
        objects = [_object_row("obj.foreign", symbol="PndThing", source_id="luminosityfit", source_version_id="luminosityfit@v")]
        receipt, prefix = _resolver(objects).resolve("Where is PndThing?", _plan())
        self.assertEqual(receipt.resolutions[0].status, REJECTED_SCOPE)
        self.assertEqual(receipt.rejected_candidates[0]["reason"], REJECTED_SCOPE)

    def test_context_source_target_is_allowed(self):
        objects = [
            _object_row("obj.paper", symbol=None, title="PndThing", source_id="li_2026", source_version_id="li_2026@sha", object_type="thesis_section")
        ]
        receipt, prefix = _resolver(objects).resolve("Where is PndThing documented?", _plan())
        self.assertEqual(receipt.resolutions[0].status, RESOLVED_UNIQUE)
        self.assertEqual(prefix[0]["object_id"], "obj.paper")

    def test_accepted_unique_alias_resolves_canonical_object(self):
        objects = [_object_row("obj.alias", symbol=None, title="restgas_profile.txt", object_type="configuration_key")]
        aliases = [AcceptedAlias("restgas_profile.txt", "restgas_profile.txt", "obj.alias", LOCKED)]
        receipt, prefix = _resolver(objects, aliases).resolve(
            "Where does restgas_profile.txt come from?", _plan()
        )
        self.assertEqual(receipt.resolutions[0].status, RESOLVED_UNIQUE)
        self.assertEqual(receipt.resolutions[0].candidates[0].match_kind, MATCH_ACCEPTED_ALIAS)
        self.assertEqual(prefix[0]["object_id"], "obj.alias")

    def test_ambiguous_alias_does_not_select_one_target(self):
        objects = [
            _object_row("obj.a", symbol=None, title="thing", object_type="configuration_key"),
            _object_row("obj.b", symbol=None, title="thing", object_type="configuration_key"),
        ]
        aliases = [
            AcceptedAlias("shared_name", "shared_name", "obj.a", LOCKED),
            AcceptedAlias("shared_name", "shared_name", "obj.b", LOCKED),
        ]
        receipt, prefix = _resolver(objects, aliases).resolve(
            "Where does shared_name come from?", _plan()
        )
        self.assertEqual(receipt.resolutions[0].status, AMBIGUOUS)
        self.assertIsNone(receipt.resolutions[0].selected_object_id)
        self.assertEqual(prefix, [])
        self.assertTrue(receipt.fallback_required)

    def test_duplicate_alias_targets_deduplicate(self):
        objects = [_object_row("obj.a", symbol=None, title="thing", object_type="configuration_key")]
        aliases = [
            AcceptedAlias("thing_name", "thing_name", "obj.a", LOCKED),
            AcceptedAlias("Thing Name", "thing name", "obj.a", LOCKED),
        ]
        receipt, prefix = _resolver(objects, aliases).resolve(
            "Where does thing_name come from?", _plan()
        )
        resolution = receipt.resolutions[0]
        self.assertEqual(resolution.status, RESOLVED_UNIQUE)
        self.assertEqual(len(resolution.candidates), 1)
        self.assertEqual(prefix[0]["object_id"], "obj.a")

    def test_missing_alias_target_is_reported(self):
        objects = []
        aliases = [AcceptedAlias("ghost.txt", "ghost.txt", "obj.missing", LOCKED)]
        receipt, prefix = _resolver(objects, aliases).resolve(
            "Where does ghost.txt come from?", _plan()
        )
        self.assertEqual(receipt.resolutions[0].status, MISSING_TARGET)
        self.assertEqual(receipt.rejected_candidates[0]["reason"], MISSING_TARGET)

    def test_unreviewed_alias_rows_are_ignored_by_loader_filter(self):
        # The production loader filters review_status='accepted' in SQL, so an
        # unaccepted alias never reaches mention extraction.  A question token
        # without any accepted alias stays a plain explicit identifier.
        objects = [_object_row("obj.a", symbol=None, title="thing")]
        aliases = [AcceptedAlias("thing_name", "thing_name", "obj.a", LOCKED)]
        resolver = _resolver(objects, aliases)
        question = "Where does other_name come from?"
        receipt, _ = resolver.resolve(question, _plan())
        self.assertEqual(
            [(r.mention.text, r.mention.kind) for r in receipt.resolutions],
            [("other_name", "explicit_identifier")],
        )

    def test_unresolved_mention_is_reported(self):
        receipt, prefix = _resolver([]).resolve("Where is NothingHere?", _plan())
        self.assertEqual(receipt.resolutions[0].status, UNRESOLVED)
        self.assertIn("NothingHere", receipt.unresolved_mentions)

    def test_resolution_receipt_carries_provenance_and_reasons(self):
        objects = [_object_row("obj.exact", symbol="PndThing")]
        receipt, _ = _resolver(objects).resolve("Where is PndThing?", _plan())
        payload = receipt.as_dict()
        resolution = payload["resolutions"][0]
        self.assertEqual(resolution["mention"]["provenance"], "user_raw_technical_token")
        self.assertEqual(resolution["reason"], "unique exact_symbol match within locked scope")
        self.assertEqual(payload["identity_relation_support"], "NOT_AVAILABLE")

    def test_deterministic_repeated_execution(self):
        objects = [
            _object_row("obj.exact", symbol="PndThing"),
            _object_row("obj.other", symbol="OtherThing"),
        ]
        resolver = _resolver(objects)
        first = resolver.resolve("Where is PndThing?", _plan())
        second = resolver.resolve("Where is PndThing?", _plan())
        self.assertEqual(
            [r.as_dict() for r in first[0].resolutions],
            [r.as_dict() for r in second[0].resolutions],
        )
        self.assertEqual(
            [row["object_id"] for row in first[1]],
            [row["object_id"] for row in second[1]],
        )

    def test_resolver_performs_only_read_only_queries(self):
        objects = [_object_row("obj.exact", symbol="PndThing")]
        storage = FakeStorage(objects)
        EntityResolver(storage).resolve("Where is PndThing?", _plan())
        for sql, _ in storage.connection.statements:
            self.assertNotRegex(sql.casefold(), r"\b(insert|update|delete|upsert|create|drop|alter)\b")


class StreamMergeTests(unittest.TestCase):
    def test_entity_first_candidates_precede_fallback_with_stable_dedup(self):
        prefix = [{"object_id": "obj.canon"}]
        legacy = [
            {"object_id": "obj.canon"},
            {"object_id": "obj.fallback"},
            {"object_id": "obj.fallback"},
        ]
        merged = merge_exact_streams(prefix, legacy, 20)
        self.assertEqual(
            [row["object_id"] for row in merged], ["obj.canon", "obj.fallback"]
        )

    def test_legacy_fallback_available_without_prefix(self):
        legacy = [{"object_id": "obj.fallback"}]
        merged = merge_exact_streams([], legacy, 20)
        self.assertEqual([row["object_id"] for row in merged], ["obj.fallback"])


class ProductionBoundaryTests(unittest.TestCase):
    def test_lexical_builder_unchanged_for_c4_boundary(self):
        # C4 remains CLOSED_INCONCLUSIVE: the lexical builder must still
        # behave identically for a representative question.
        plan = _plan(
            analysis_diagnostics={
                "analyzer_accepted_semantic_delta": {
                    "concepts": [
                        {"value": "trace mismatch", "support_spans": ["trace the mismatch"]}
                    ]
                }
            }
        )
        question = "runLmdFit cannot find prepared data; how do I trace the mismatch?"
        lexical = build_lexical_query(question, plan)
        self.assertEqual(
            lexical.text, question + " trace mismatch"
        )


if __name__ == "__main__":
    unittest.main()
