from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from panda_agent.config import load_query_expansions
from panda_agent.d3_structured import select_matching_query_expansions
from panda_agent.retrieval import Retriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "configs" / "query_expansions.yaml"

TEST_REPOSITORIES = {
    "pandaroot": "18c09e91100db27867ded30e708b4dae95bd8357",
    "luminosityfit": "ddd83dcd1a74093bf48ef259a2849a67f9413f32",
    "restgas_determination": "11f1edc49dcbaeb61d707491a6d3bbec390fcd42",
}


def _make_test_retriever(expansions):
    retriever = Retriever.__new__(Retriever)
    retriever.fixed_versions = TEST_REPOSITORIES
    retriever.fixed_refs = {repo: "dev" for repo in TEST_REPOSITORIES}
    retriever.web_version_tokens = {"2023-08-25-dev"}
    policy = SimpleNamespace(
        source_budgets={
            "paper": 0.3,
            "code": 0.4,
            "graph": 0.15,
            "documentation": 0.1,
            "workflow": 0.05,
        },
        required_sources=["paper", "code"],
    )
    retriever.policies = SimpleNamespace(
        intents={
            intent: policy
            for intent in (
                "installation",
                "usage",
                "algorithm_theory",
                "algorithm_implementation",
                "api",
                "data_flow",
                "module_structure",
                "troubleshooting",
            )
        }
    )
    retriever.query_expansions = expansions
    return retriever


class EventAlignmentQueryExpansionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.expansions = load_query_expansions(CONFIG_PATH)

    def test_generic_particle_identification_queries_do_not_trigger_event_alignment(self) -> None:
        """Bare particle identification queries must not trigger event_alignment or inject restgas symbols."""
        unseen_pid_queries = [
            "Where can I find the tutorial on particle identification in PandaRoot?",
            "How does particle identification work in the offline analysis framework?",
            "Which documentation chapter describes the particle identification algorithms?",
            "Explain the particle identification selection criteria in PandaRoot",
            "What particle identification selectors are available for charged particles?",
        ]
        for query in unseen_pid_queries:
            with self.subTest(query=query):
                decision = select_matching_query_expansions(query, self.expansions.rules, None)
                self.assertNotIn(
                    "event_alignment",
                    decision.matched_rule_ids,
                    f"Query falsely triggered event_alignment: {query}",
                )

    def test_genuine_event_alignment_queries_trigger_event_alignment(self) -> None:
        """Queries explicitly targeting event alignment must reliably trigger event_alignment."""
        genuine_alignment_queries = [
            "How does event alignment synchronize tracks with the POCA tree?",
            "Explain event ID alignment for the restgas POCA handoff",
            "What is the procedure for event alignment in the two-pass reconstruction?",
            "How is event id alignment validated across passes?",
        ]
        for query in genuine_alignment_queries:
            with self.subTest(query=query):
                decision = select_matching_query_expansions(query, self.expansions.rules, None)
                self.assertIn(
                    "event_alignment",
                    decision.matched_rule_ids,
                    f"Query failed to trigger event_alignment: {query}",
                )
                matched_rules = {r.rule_id: r for r in decision.active_matching_rules}
                rule = matched_rules["event_alignment"]
                self.assertIn("macro/target/ana_dpm.C", rule.symbols)
                self.assertIn("macro/target/prod_aod_complete.C", rule.symbols)
                self.assertIn("POCA_VERTEX_FILE", rule.symbols)
                self.assertIn("event_poca", rule.symbols)
                self.assertIn("event ID aligned POCA handoff", rule.concepts)

    def test_neighboring_rules_preservation(self) -> None:
        """Neighboring rules around PID workflows and event POCA remain functional and trigger on qualified cues."""
        checks = [
            (
                "How is the target pid pipeline configured in restgas determination?",
                "target_pid_pipeline",
            ),
            (
                "Where is pid processing defined in the macros?",
                "target_pid_pipeline",
            ),
            (
                "What outputs are written to pid_final.root during reconstruction?",
                "pid_two_pass_files",
            ),
            (
                "How is second-pass pid executed using the poca_vertex_file?",
                "event_poca_handoff",
            ),
            (
                "What should be checked if event_poca is missing?",
                "event_poca_troubleshooting",
            ),
            (
                "Where is lumi_trksqa generated in the data chain?",
                "lmd_fit_data_chain",
            ),
        ]
        for query, expected_rule in checks:
            with self.subTest(query=query, expected_rule=expected_rule):
                decision = select_matching_query_expansions(query, self.expansions.rules, None)
                self.assertIn(
                    expected_rule,
                    decision.matched_rule_ids,
                    f"Neighboring rule {expected_rule} was not triggered for query: {query}",
                )

    def test_retriever_preparse_isolation(self) -> None:
        """Retriever preparse does not pollute generic PID documentation queries with event POCA artifacts."""
        retriever = _make_test_retriever(self.expansions)
        generic_pid_query = "What particle identification selectors are available for charged particles?"
        parsed = retriever._preparse(generic_pid_query)
        self.assertNotIn("event_alignment", parsed.matched_expansion_rules)
        self.assertNotIn("macro/target/ana_dpm.C", parsed.symbols)
        self.assertNotIn("macro/target/prod_aod_complete.C", parsed.symbols)
        self.assertNotIn("POCA_VERTEX_FILE", parsed.symbols)
        self.assertNotIn("event_poca", parsed.symbols)
        self.assertNotIn("restgas_determination", parsed.target_repositories)
        self.assertNotIn("event ID aligned POCA handoff", parsed.concepts)

        # Genuine alignment query must still inject event alignment symbols
        alignment_query = "How is event id alignment handled in the POCA handoff?"
        parsed_alignment = retriever._preparse(alignment_query)
        self.assertIn("event_alignment", parsed_alignment.matched_expansion_rules)
        self.assertIn("macro/target/ana_dpm.C", parsed_alignment.symbols)
        self.assertIn("restgas_determination", parsed_alignment.target_repositories)
        self.assertIn("event ID aligned POCA handoff", parsed_alignment.concepts)


if __name__ == "__main__":
    unittest.main()
