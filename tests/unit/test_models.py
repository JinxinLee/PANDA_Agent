from __future__ import annotations

import unittest

from pydantic import ValidationError

from panda_agent.models import RetrievalPlan, SourceLocator, stable_id


class ModelTests(unittest.TestCase):
    def test_stable_id_is_deterministic_and_namespaced(self) -> None:
        first = stable_id("repo@sha", "function", "src/a.cc:f", prefix="object")
        second = stable_id("repo@sha", "function", "src/a.cc:f", prefix="object")
        changed = stable_id("repo@sha2", "function", "src/a.cc:f", prefix="object")
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("object."))
        self.assertNotEqual(first, changed)

    def test_locator_rejects_inverted_line_range(self) -> None:
        with self.assertRaises(ValidationError):
            SourceLocator(path="src/a.cc", start_line=20, end_line=10)

    def test_retrieval_plan_requires_normalized_budgets(self) -> None:
        with self.assertRaises(ValidationError):
            RetrievalPlan(
                intent="api",
                source_budgets={"code": 0.7, "documentation": 0.2},
            )


if __name__ == "__main__":
    unittest.main()

