"""Focused T0 contracts for the C4-A1 lexical-query boundary."""

from __future__ import annotations

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import call, patch

import panda_agent.c4_sparse_evaluation as c4_sparse_evaluation
import panda_agent.retrieval as retrieval_module
from panda_agent.lexical_query import build_lexical_query
from panda_agent.models import RetrievalPlan
from panda_agent.retrieval import (
    Retriever,
    build_dense_query_bundle,
    build_semantic_query,
)
from panda_agent.retrieval_trace import build_retrieval_trace


def _lexical_plan(
    *,
    accepted_symbols=(),
    accepted_concepts=(),
    resolved_aliases=None,
    **diagnostic_fields,
) -> dict:
    diagnostics = {
        "analyzer_accepted_semantic_delta": {
            "symbols": list(accepted_symbols),
            "concepts": list(accepted_concepts),
        }
    }
    diagnostics.update(diagnostic_fields)
    return {
        "symbols": [],
        "concepts": [],
        "concept_scopes": {},
        "target_repositories": [],
        "resolved_versions": {},
        "resolved_aliases": dict(resolved_aliases or {}),
        "paper_page_hints": {},
        "analysis_diagnostics": diagnostics,
    }


def _retrieval_plan(
    *,
    accepted_symbols=(),
    accepted_concepts=(),
    resolved_aliases=None,
    analysis_extra=None,
    **fields,
) -> RetrievalPlan:
    diagnostics = _lexical_plan(
        accepted_symbols=accepted_symbols,
        accepted_concepts=accepted_concepts,
        resolved_aliases=resolved_aliases,
    )["analysis_diagnostics"]
    diagnostics.update(analysis_extra or {})
    return RetrievalPlan(
        intent="usage",
        source_budgets={"code": 1.0},
        target_repositories=list(fields.get("target_repositories", [])),
        resolved_versions=dict(fields.get("resolved_versions", {})),
        concepts=list(fields.get("concepts", [])),
        symbols=list(fields.get("symbols", [])),
        concept_scopes=dict(fields.get("concept_scopes", {})),
        resolved_aliases=dict(resolved_aliases or {}),
        paper_page_hints=dict(fields.get("paper_page_hints", {})),
        analysis_diagnostics=diagnostics,
    )


def _components(query, kind=None):
    return [
        component
        for component in query.components
        if kind is None or component.kind == kind
    ]


class C4A1LexicalQueryContractTests(TestCase):
    # C4-A1-01: the raw question remains the complete authoritative query.
    def test_c4_a1_01_preserves_full_raw_question_byte_exactly(self) -> None:
        question = "  Where is PndLmdTrackQ implemented?\r\n"

        query = build_lexical_query(question, _lexical_plan())

        self.assertIs(query.raw_question, question)
        self.assertEqual(query.text.encode("utf-8"), question.encode("utf-8"))
        self.assertEqual(query.as_dict()["raw_question"], question)

    # C4-A1-02: every technical identifier in the raw question is byte-exact.
    def test_c4_a1_02_retains_raw_identifiers_byte_exactly(self) -> None:
        question = (
            "Where is PndLmdTrackQ in src/panda_agent/lexical_query.py "
            "at v1.2.3 deadbeefcafebabe?"
        )
        expected = [
            "PndLmdTrackQ",
            "src/panda_agent/lexical_query.py",
            "v1.2.3",
            "deadbeefcafebabe",
        ]

        query = build_lexical_query(question, _lexical_plan())
        identifiers = [component.value for component in _components(query, "raw_identifier")]

        self.assertEqual(identifiers, expected)
        self.assertEqual(
            [value.encode("utf-8") for value in identifiers],
            [value.encode("utf-8") for value in expected],
        )

    # C4-A1-03: accepted symbols retain provenance and support-span auditing.
    def test_c4_a1_03_retains_accepted_symbol_with_audit_fields(self) -> None:
        question = "Where does PndLmdTrackQ route records?"
        plan = _lexical_plan(
            accepted_symbols=[
                {"value": "PndLmdTrackQ", "support_spans": ["PndLmdTrackQ"]}
            ]
        )

        query = build_lexical_query(question, plan)
        component = _components(query, "analyzer_symbol")[0]

        self.assertEqual(component.value, "PndLmdTrackQ")
        self.assertEqual(component.provenance, "analyzer_accepted")
        self.assertEqual(component.support_spans, ("PndLmdTrackQ",))
        self.assertFalse(component.appended)
        self.assertEqual(query.as_dict()["components"][-1]["support_spans"], ["PndLmdTrackQ"])

    # C4-A1-04: a query-grounded concept may add useful lexical material.
    def test_c4_a1_04_query_grounded_accepted_concept_may_append_new_material(self) -> None:
        question = "Explain topicalpha output."
        plan = _lexical_plan(
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": "topicalpha"}
            ]
        )

        query = build_lexical_query(question, plan)
        component = _components(query, "analyzer_concept")[0]

        self.assertEqual(query.text, f"{question} topicalphas")
        self.assertEqual(component.support_spans, ("topicalpha",))
        self.assertTrue(component.appended)
        self.assertEqual(query.as_dict()["components"][-1]["appended"], True)

    # C4-A1-05: rejected analyzer output never enters the lexical query.
    def test_c4_a1_05_rejected_symbols_and_concepts_are_excluded(self) -> None:
        question = "Explain acceptedThing."
        plan = _lexical_plan(
            analyzer_rejected_semantic_delta={
                "symbols": [
                    {"value": "rejectedSymbol", "support_spans": ["acceptedThing"]}
                ],
                "concepts": [
                    {"value": "rejected concept", "support_spans": ["acceptedThing"]}
                ],
            },
            rejected_analyzer_items=[
                {"value": "anotherRejectedTerm", "support_spans": ["acceptedThing"]}
            ],
        )

        query = build_lexical_query(question, plan)
        values = [component.value for component in query.components]

        self.assertNotIn("rejectedSymbol", values)
        self.assertNotIn("rejected concept", values)
        self.assertNotIn("anotherRejectedTerm", values)
        self.assertIn("rejected_analyzer_items", query.excluded_component_classes)

    # C4-A1-06: fallback scopes are explicit exclusions, not lexical inputs.
    def test_c4_a1_06_fallback_scopes_are_excluded(self) -> None:
        question = "Explain acceptedThing."
        plan = _lexical_plan(
            deterministic_parse={
                "fixed": {"concept_scopes": {"repository": "fixedRepo"}},
                "fallback": {"concept_scopes": {"repository": "fallbackRepo"}},
            }
        )
        plan["concept_scopes"] = {"repository": "fallbackRepo"}
        plan["analysis_diagnostics"]["analyzer_accepted_semantic_delta"]["concept_scopes"] = [
            {"key": "repository", "value": "acceptedScope", "support_spans": ["acceptedThing"]}
        ]

        query = build_lexical_query(question, plan)
        values = [component.value for component in query.components]

        self.assertNotIn("fallbackRepo", values)
        self.assertNotIn("fixedRepo", values)
        self.assertNotIn("acceptedScope", values)
        self.assertIn("fallback_scopes", query.excluded_component_classes)

    # C4-A1-07: reviewed expansion rules remain excluded from C4.
    def test_c4_a1_07_reviewed_expansions_are_excluded(self) -> None:
        plan = _lexical_plan(
            reviewed_expansions=[{"value": "reviewedExpansion"}],
            matched_expansion_rules=["reviewed-rule"],
        )

        query = build_lexical_query("Explain acceptedThing.", plan)
        values = [component.value for component in query.components]

        self.assertNotIn("reviewedExpansion", values)
        self.assertNotIn("reviewed-rule", values)
        self.assertIn("reviewed_expansions", query.excluded_component_classes)

    # C4-A1-08: paper/page hints are retrieval controls, never query terms.
    def test_c4_a1_08_paper_and_page_hints_are_excluded(self) -> None:
        plan = _lexical_plan()
        plan["paper_page_hints"] = {"li_2026": [17, 21]}
        plan["analysis_diagnostics"]["paper_page_hints"] = {
            "li_2026": [17, 21],
            "page_titles": ["paperPageTitle"],
        }

        query = build_lexical_query("Explain acceptedThing.", plan)
        values = [component.value for component in query.components]

        self.assertNotIn("li_2026", values)
        self.assertNotIn("17", values)
        self.assertNotIn("paperPageTitle", values)
        self.assertIn("paper_page_hints", query.excluded_component_classes)

    # C4-A1-09: hidden repository/version metadata cannot pollute lexical text.
    def test_c4_a1_09_hidden_repository_and_version_metadata_are_excluded(self) -> None:
        plan = _lexical_plan(
            repository_additions=[
                {"value": "hidden_repository", "support_spans": ["acceptedThing"]}
            ],
            version_mentions=[
                {"token": "v9.9.9", "repository": "hidden_repository", "support_spans": ["acceptedThing"]}
            ],
        )
        plan["target_repositories"] = ["hidden_repository"]
        plan["resolved_versions"] = {"hidden_repository": "deadbeef1234567"}

        query = build_lexical_query("Explain acceptedThing.", plan)
        values = [component.value for component in query.components]

        self.assertNotIn("hidden_repository", values)
        self.assertNotIn("v9.9.9", values)
        self.assertNotIn("deadbeef1234567", values)
        self.assertIn("hidden_repository_metadata", query.excluded_component_classes)
        self.assertIn("hidden_version_metadata", query.excluded_component_classes)

    # C4-A1-10: flat RetrievalPlan symbols/concepts cannot bypass provenance.
    def test_c4_a1_10_flat_plan_fields_cannot_bypass_provenance(self) -> None:
        plan = _lexical_plan()
        plan["symbols"] = ["FlatSymbol"]
        plan["concepts"] = ["flat concept"]
        plan["analysis_diagnostics"]["flat_plan_symbols"] = ["FlatSymbol"]
        plan["analysis_diagnostics"]["flat_plan_concepts"] = ["flat concept"]

        query = build_lexical_query("Explain acceptedThing.", plan)
        values = [component.value for component in query.components]

        self.assertNotIn("FlatSymbol", values)
        self.assertNotIn("flat concept", values)
        self.assertIn("flat_plan_symbols", query.excluded_component_classes)
        self.assertIn("flat_plan_concepts", query.excluded_component_classes)

    # C4-A1-11: retain only the accepted alias key, never its C5 target title.
    def test_c4_a1_11_alias_key_is_retained_without_c5_target_injection(self) -> None:
        question = "Where is PndAlias used?"
        query = build_lexical_query(
            question,
            _lexical_plan(resolved_aliases={"PndAlias": "CanonicalTargetTitle"}),
        )
        aliases = _components(query, "accepted_alias")

        self.assertEqual(len(aliases), 1)
        self.assertEqual(aliases[0].value, "PndAlias")
        self.assertEqual(aliases[0].provenance, "accepted_alias")
        self.assertFalse(aliases[0].appended)
        self.assertNotIn("CanonicalTargetTitle", query.text)
        self.assertIn("c5_canonical_lookup", query.excluded_component_classes)

    # C4-A1-12: component ordering is deterministic and provenance-prioritized.
    def test_c4_a1_12_component_order_is_deterministic(self) -> None:
        question = (
            "Inspect PndRaw and SvcEndpoint under PndAlias with topicalpha topicbeta."
        )
        plan = _lexical_plan(
            accepted_symbols=[
                {"value": "SvcEndpoint", "support_spans": ["SvcEndpoint"]},
                {"value": "PndRaw", "support_spans": "PndRaw"},
            ],
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": ["topicalpha"]},
                {"value": "topicbetas", "support_spans": ["topicbeta"]},
            ],
            resolved_aliases={"PndAlias": "CanonicalTargetTitle"},
        )

        first = build_lexical_query(question, plan)
        second = build_lexical_query(question, plan)
        ordered = [(component.kind, component.value) for component in first.components]

        self.assertEqual(first.as_dict(), second.as_dict())
        self.assertEqual(
            ordered,
            [
                ("raw_identifier", "PndRaw"),
                ("raw_identifier", "SvcEndpoint"),
                ("raw_identifier", "PndAlias"),
                ("analyzer_symbol", "SvcEndpoint"),
                ("analyzer_symbol", "PndRaw"),
                ("analyzer_concept", "topicalphas"),
                ("analyzer_concept", "topicbetas"),
                ("accepted_alias", "PndAlias"),
            ],
        )

    # C4-A1-13: duplicate components collapse while mixed provenance stays auditable.
    def test_c4_a1_13_component_and_render_dedup_are_stable(self) -> None:
        question = "Explain PndThing and topicalpha."
        plan = _lexical_plan(
            accepted_symbols=[
                {"value": "PndThing", "support_spans": ["PndThing"]},
                {"value": "PndThing", "support_spans": "PndThing"},
            ],
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": ["topicalpha"]},
                {"value": "TOPICALPHAS", "support_spans": ["topicalpha"]},
            ],
            resolved_aliases={"PndThing": "CanonicalTargetTitle"},
        )

        query = build_lexical_query(question, plan)
        symbols = _components(query, "analyzer_symbol")
        concepts = _components(query, "analyzer_concept")

        self.assertEqual(len(symbols), 1)
        self.assertEqual(len(concepts), 1)
        self.assertEqual(
            query.text,
            "Explain PndThing and topicalpha. topicalphas",
        )
        self.assertEqual(query.text.casefold().count("topicalphas"), 1)
        self.assertEqual(len(_components(query, "accepted_alias")), 1)

    # C4-A1-14: no more than six appended components, with auditable flags.
    def test_c4_a1_14_appended_component_budget_is_at_most_six(self) -> None:
        stems = [
            "topicalpha",
            "topicbravo",
            "topiccharlie",
            "topicdelta",
            "topichotel",
            "topicindia",
            "topicjuliet",
            "topickilo",
        ]
        question = "Discuss " + " ".join(stems)
        concepts = [
            {"value": f"{stem}s", "support_spans": stem} for stem in stems
        ]

        query = build_lexical_query(
            question,
            _lexical_plan(accepted_concepts=concepts),
        )
        appended = [component for component in query.components if component.appended]

        self.assertLessEqual(len(appended), 6)
        self.assertEqual(len(appended), 6)
        self.assertTrue(all(component.appended for component in appended))
        self.assertEqual(
            [component.value for component in appended],
            [f"{stem}s" for stem in stems[:6]],
        )

    # C4-A1-15: no more than thirty-two appended tokens are rendered.
    def test_c4_a1_15_appended_token_budget_is_at_most_thirty_two(self) -> None:
        stems = ["alpha", "bravo", "charlie", "delta", "hotel", "india"]
        question = "Discuss " + " ".join(stems)
        concepts = [
            {
                "value": " ".join(f"{stem}{suffix}" for stem in stems),
                "support_spans": [question],
            }
            for suffix in ("s", "t", "x", "y", "z", "q")
        ]

        query = build_lexical_query(
            question,
            _lexical_plan(accepted_concepts=concepts),
        )
        appended = [component for component in query.components if component.appended]
        appended_tokens = sum(len(component.value.split()) for component in appended)

        self.assertLessEqual(appended_tokens, 32)
        self.assertEqual(len(appended), 5)
        self.assertEqual(appended_tokens, 30)
        self.assertNotIn("alphaq", query.text)

    # C4-A1-16: repeated accepted values do not receive arbitrary term weight.
    def test_c4_a1_16_duplicate_values_do_not_receive_arbitrary_weight(self) -> None:
        question = "Discuss topicalpha."
        plan = _lexical_plan(
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": "topicalpha"},
                {"value": "TOPICALPHAS", "support_spans": ["topicalpha"]},
                {"value": "topicalphas", "support_spans": ["topicalpha"]},
            ]
        )

        query = build_lexical_query(question, plan)
        concepts = _components(query, "analyzer_concept")

        self.assertEqual(len(concepts), 1)
        self.assertEqual(query.text.casefold().count("topicalphas"), 1)
        self.assertEqual(sum(component.appended for component in concepts), 1)

    # C4-A1-17: RawDense remains the exact raw question and user_raw stream.
    def test_c4_a1_17_raw_dense_remains_unchanged(self) -> None:
        question = "Explain topicalpha output."
        plan = _retrieval_plan(
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": "topicalpha"}
            ]
        )
        lexical = build_lexical_query(question, plan)
        bundle = build_dense_query_bundle(question, plan)

        self.assertNotEqual(lexical.text, question)
        self.assertEqual(bundle.raw.text, question)
        self.assertEqual(bundle.raw.provenance, "user_raw")
        self.assertEqual(bundle.as_dict()["raw"], {
            "text": question,
            "provenance": "user_raw",
            "active": True,
        })

    # C4-A1-18: the pre-existing SemanticDense policy is unchanged by C4.
    def test_c4_a1_18_semantic_dense_remains_unchanged(self) -> None:
        question = "Explain topicalpha output."
        plan = _retrieval_plan(
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": "topicalpha"}
            ],
            analysis_extra={
                "deterministic_parse": {
                    "fixed": {"concept_scopes": {"mode": "fixedvalue"}}
                }
            },
        )
        before = build_semantic_query(question, plan).as_dict()
        build_lexical_query(question, plan)
        after = build_semantic_query(question, plan).as_dict()
        bundle = build_dense_query_bundle(question, plan)

        self.assertEqual(before, after)
        self.assertIsNotNone(bundle.semantic)
        self.assertEqual(bundle.semantic.text, before["text"])
        self.assertEqual(
            [component.__dict__ for component in bundle.semantic.components],
            before["components"],
        )

    # C4-A1-19: production retrieval remains raw sparse before C4 acceptance.
    def test_c4_a1_19_production_sparse_starts_with_raw_query(self) -> None:
        question = "Explain topicalpha output."
        plan = _retrieval_plan(
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": "topicalpha"}
            ]
        )
        retriever = Retriever.__new__(Retriever)
        query_filter = object()

        with (
            patch.object(retriever, "_query_filter", return_value=query_filter),
            patch.object(
                retriever,
                "_dense_query",
                return_value=(["dense-hit"], [0.1, 0.2]),
            ) as dense_query,
            patch.object(
                retriever,
                "_sparse_query",
                return_value=["raw-sparse-hit"],
            ) as sparse_query,
        ):
            dense_hits, sparse_hits, _, semantic_query = retriever._vector(
                question, plan, 7
            )

        dense_query.assert_called_once_with(question, query_filter, 7)
        sparse_query.assert_called_once_with(question, query_filter, 7)
        self.assertEqual(dense_hits, ["dense-hit"])
        self.assertEqual(sparse_hits, ["raw-sparse-hit"])
        self.assertNotEqual(semantic_query.text, question)

    # C4-A1-20: shadow sparse executes exactly one raw and one lexical query.
    def test_c4_a1_20_shadow_sparse_runs_exactly_raw_and_lexical_two_calls(self) -> None:
        question = "Explain topicalpha output."
        plan = _retrieval_plan(
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": "topicalpha"}
            ]
        )
        lexical = build_lexical_query(question, plan)
        retriever = Retriever.__new__(Retriever)
        query_filter = object()
        raw_hit = SimpleNamespace(payload={"object_id": "raw-hit"})
        lexical_hit = SimpleNamespace(payload={"object_id": "lexical-hit"})

        with (
            patch.object(retriever, "_query_filter", return_value=query_filter),
            patch.object(
                retriever,
                "_sparse_query",
                side_effect=[[raw_hit], [lexical_hit]],
            ) as sparse_query,
        ):
            result = retriever.shadow_sparse(question, plan, limit=9)

        self.assertEqual(sparse_query.call_count, 2)
        self.assertEqual(
            sparse_query.call_args_list,
            [
                call(question, query_filter, 9),
                call(lexical.text, query_filter, 9),
            ],
        )
        self.assertEqual(result["sparse_candidates"]["raw"], [{"object_id": "raw-hit"}])
        self.assertEqual(result["sparse_candidates"]["lexical"], [{"object_id": "lexical-hit"}])

    # C4-A1-21: shadow sparse keeps channels separate and performs no fusion.
    def test_c4_a1_21_shadow_sparse_does_not_fuse_channels(self) -> None:
        question = "Explain topicalpha output."
        plan = _retrieval_plan(
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": "topicalpha"}
            ]
        )
        retriever = Retriever.__new__(Retriever)
        query_filter = object()
        raw_hit = SimpleNamespace(payload={"object_id": "raw-only"})
        lexical_hit = SimpleNamespace(payload={"object_id": "lexical-only"})

        with (
            patch.object(retriever, "_query_filter", return_value=query_filter),
            patch.object(
                retriever,
                "_sparse_query",
                side_effect=[[raw_hit], [lexical_hit]],
            ),
        ):
            result = retriever.shadow_sparse(question, plan, limit=4)

        self.assertEqual(
            set(result), {"lexical_query", "sparse_queries", "sparse_candidates"}
        )
        self.assertNotIn("fusion_scores", result)
        self.assertNotIn("rankings", result)
        self.assertEqual(
            result["sparse_candidates"],
            {
                "raw": [{"object_id": "raw-only"}],
                "lexical": [{"object_id": "lexical-only"}],
            },
        )

    # C4-A1-22: trace keeps raw production/original query distinct from lexical.
    def test_c4_a1_22_trace_separates_raw_lexical_and_original_query(self) -> None:
        question = "Explain topicalpha output."
        lexical_payload = build_lexical_query(
            question,
            _lexical_plan(
                accepted_concepts=[
                    {"value": "topicalphas", "support_spans": "topicalpha"}
                ]
            ),
        ).as_dict()
        trace = build_retrieval_trace(
            question_id="c4-a1",
            run_id="focused",
            question=question,
            diagnostics={
                "plan": {},
                "lexical_query": lexical_payload,
                "sparse_queries": {
                    "raw": {"text": question, "provenance": "user_raw", "active": True},
                    "lexical": lexical_payload,
                    "lexical_active": True,
                    "lexical_executed": True,
                },
                "sparse_candidates": {
                    "raw": [{"object_id": "raw-hit"}],
                    "lexical": [{"object_id": "lexical-hit"}],
                },
                "rankings": {"sparse": ["raw-hit"]},
            },
            manifest={},
            object_lookup={},
        )

        self.assertEqual(trace.original_retrieval_query, question)
        self.assertEqual(trace.sparse_query_text, question)
        self.assertEqual(trace.sparse_queries["raw"]["text"], question)
        self.assertEqual(trace.sparse_queries["raw"]["provenance"], "user_raw")
        self.assertNotEqual(trace.sparse_queries["lexical"]["text"], question)
        self.assertEqual(trace.sparse_candidates["raw"], [{"object_id": "raw-hit"}])
        self.assertEqual(trace.sparse_candidates["lexical"], [{"object_id": "lexical-hit"}])

    # C4-A1-23: lexical construction performs no model, storage, analyzer, or Gold calls.
    def test_c4_a1_23_builder_has_zero_external_calls(self) -> None:
        plan = _lexical_plan(
            accepted_concepts=[
                {"value": "topicalphas", "support_spans": "topicalpha"}
            ]
        )

        with (
            patch.object(retrieval_module, "VertexAIClient") as model_client,
            patch.object(retrieval_module, "Storage") as storage,
            patch.object(retrieval_module, "create_sparse_encoder") as sparse_factory,
            patch.object(retrieval_module.Retriever, "analyze") as analyzer,
            patch.object(c4_sparse_evaluation, "run_c4_sparse_evaluation") as gold,
        ):
            query = build_lexical_query("Explain topicalpha output.", plan)

        self.assertTrue(query.text.endswith("topicalphas"))
        model_client.assert_not_called()
        storage.assert_not_called()
        sparse_factory.assert_not_called()
        analyzer.assert_not_called()
        gold.assert_not_called()


if __name__ == "__main__":
    import unittest

    unittest.main()
