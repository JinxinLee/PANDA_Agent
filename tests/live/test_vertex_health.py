from __future__ import annotations

import os
import unittest

from dotenv import load_dotenv

from panda_agent.llm.vertex import VertexAIClient, VertexSettings


@unittest.skipUnless(
    os.getenv("RUN_VERTEX_LIVE_TESTS") == "1",
    "set RUN_VERTEX_LIVE_TESTS=1 to call real Vertex models",
)
class LiveVertexHealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv()

    def test_generation_and_both_embedding_roles(self) -> None:
        result = VertexAIClient(VertexSettings.from_env()).health_check()
        self.assertEqual(result.status, "ok")
        self.assertGreater(result.query_embedding_dimensions, 0)
        self.assertEqual(
            result.query_embedding_dimensions, result.document_embedding_dimensions
        )


if __name__ == "__main__":
    unittest.main()

