from __future__ import annotations

import os
import unittest
from types import SimpleNamespace

from panda_agent.retrieval import Retriever
from panda_agent.storage import Storage


@unittest.skipUnless(os.getenv("RUN_GRAPH_LIVE_TESTS") == "1", "set RUN_GRAPH_LIVE_TESTS=1")
class GraphRetrievalLiveTests(unittest.TestCase):
    def test_graph_returns_the_opposite_resolved_endpoint(self):
        storage = Storage()
        with storage.connect() as connection:
            row = connection.execute(
                """SELECT r.subject_id, r.object_id
                   FROM relation_edges r
                   JOIN knowledge_objects s ON s.object_id=r.subject_id
                   JOIN knowledge_objects o ON o.object_id=r.object_id
                   WHERE r.review_status='accepted'
                     AND s.source_id='pandaroot'
                     AND o.source_id IN ('pandaroot','curated_panda_domain')
                     AND r.subject_id<>r.object_id
                   LIMIT 1"""
            ).fetchone()
        self.assertIsNotNone(row)
        subject_id, object_id = row
        retriever = Retriever.__new__(Retriever)
        retriever.storage = storage
        retriever.context_sources = ["li_2026", "karavdina_2015", "pflueger_2017", "pandaroot_sphinx_2023_08_25_dev"]
        retriever.policies = SimpleNamespace(max_relation_hops=1)
        plan = SimpleNamespace(
            target_repositories=["pandaroot"],
            resolved_versions={"pandaroot": "18c09e91100db27867ded30e708b4dae95bd8357"},
        )
        result = retriever._graph([{"object_id": subject_id}], plan, 20)
        self.assertIn(object_id, {item["object_id"] for item in result})
        self.assertNotIn(subject_id, {item["object_id"] for item in result})


if __name__ == "__main__":
    unittest.main()
