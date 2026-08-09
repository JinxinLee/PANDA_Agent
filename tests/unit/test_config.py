from __future__ import annotations

import unittest
from pathlib import Path

from panda_agent.config import (
    load_corpora,
    load_knowledge_schema,
    load_query_expansions,
    load_relation_ontology,
    load_retrieval_policies,
    load_seed_relations,
    validate_seed_predicates,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"


class ConfigTests(unittest.TestCase):
    def test_corpora_references_existing_pdfs_and_known_repositories(self) -> None:
        corpora = load_corpora(CONFIG_DIR / "corpora.yaml")
        self.assertEqual(
            {item.repo_id for item in corpora.repositories},
            {"luminosityfit", "pandaroot", "restgas_determination"},
        )
        for paper in corpora.papers:
            self.assertTrue((PROJECT_ROOT / paper.path).is_file(), paper.path)

    def test_relation_seeds_only_use_declared_predicates(self) -> None:
        ontology = load_relation_ontology(CONFIG_DIR / "relation_ontology.yaml")
        seeds = load_seed_relations(CONFIG_DIR / "seed_relations.yaml")
        validate_seed_predicates(seeds, ontology)
        self.assertGreaterEqual(len(seeds.relations), 8)

    def test_knowledge_object_types_are_unique(self) -> None:
        schema = load_knowledge_schema(CONFIG_DIR / "knowledge_schema.yaml")
        object_types = [
            value for group in schema.object_types.values() for value in group
        ]
        self.assertEqual(len(object_types), len(set(object_types)))
        self.assertIn("source_version_id", schema.required_base_fields)

    def test_retrieval_source_budgets_are_normalized(self) -> None:
        policies = load_retrieval_policies(CONFIG_DIR / "retrieval_policies.yaml")
        self.assertEqual(policies.max_targeted_retrievals, 1)
        for policy in policies.intents.values():
            self.assertAlmostEqual(sum(policy.source_budgets.values()), 1.0)

    def test_query_expansion_rules_are_typed_and_unique(self) -> None:
        expansions = load_query_expansions(CONFIG_DIR / "query_expansions.yaml")
        self.assertGreaterEqual(len(expansions.rules), 6)
        self.assertEqual(
            len({item.rule_id for item in expansions.rules}), len(expansions.rules)
        )


if __name__ == "__main__":
    unittest.main()
