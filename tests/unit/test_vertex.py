from __future__ import annotations

import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from panda_agent.llm.vertex import (
    VertexAIClient,
    VertexCallError,
    VertexConfigurationError,
    VertexSettings,
)


class FakeModels:
    def __init__(
        self,
        embedding_dimensions: int,
        response_dimensions: list[int] | None = None,
        response_counts: list[int] | None = None,
    ) -> None:
        self.generation_calls = []
        self.embedding_calls = []
        self.embedding_dimensions = embedding_dimensions
        self.response_dimensions = response_dimensions or [embedding_dimensions]
        self.response_counts = response_counts or []

    def generate_content(self, **kwargs):
        self.generation_calls.append(kwargs)
        return SimpleNamespace(text=json.dumps({"status": "ok"}))

    def embed_content(self, **kwargs):
        self.embedding_calls.append(kwargs)
        contents = kwargs["contents"]
        response_dimension = self.response_dimensions[
            min(len(self.embedding_calls) - 1, len(self.response_dimensions) - 1)
        ]
        response_count = (
            self.response_counts[
                min(len(self.embedding_calls) - 1, len(self.response_counts) - 1)
            ]
            if self.response_counts
            else len(contents)
        )
        return SimpleNamespace(
            embeddings=[
                SimpleNamespace(values=[0.1] * response_dimension)
                for _ in range(response_count)
            ]
        )


class FakeClient:
    def __init__(
        self,
        embedding_dimensions: int = 3072,
        response_dimensions: list[int] | None = None,
        response_counts: list[int] | None = None,
    ) -> None:
        self.models = FakeModels(embedding_dimensions, response_dimensions, response_counts)


class VertexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = VertexSettings(project="test-project")
        self.fake = FakeClient(self.settings.embedding_dimensions)
        self.client = VertexAIClient(self.settings, client=self.fake)

    def test_settings_require_project(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(VertexConfigurationError):
                VertexSettings.from_env()

    def test_model_roles_are_separate_and_configurable(self) -> None:
        with patch.dict(
            os.environ,
            {
                "QA_GCP_PROJECT_ID": "test-project",
                "QA_GENERATION_MODEL_ID": "gemini-3.7-flash",
                "QA_EVALUATION_JUDGE_MODEL_ID": "gemini-3.7-flash",
                "QA_EMBEDDING_MODEL_ID": "gemini-embedding-2",
            },
            clear=True,
        ):
            settings = VertexSettings.from_env()
        self.assertEqual(settings.generation_model, "gemini-3.7-flash")
        self.assertEqual(settings.evaluation_judge_model, "gemini-3.7-flash")
        self.assertEqual(
            settings.for_generation_model(settings.evaluation_judge_model).generation_model,
            "gemini-3.7-flash",
        )

    def test_generation_health_check_reports_model_role(self) -> None:
        result = self.client.generation_health_check()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["generation_model"], "gemini-3.7-flash")

    def test_generate_json_uses_constrained_json_output(self) -> None:
        result = self.client.generate_json(
            "health", {"type": "object", "properties": {"status": {"type": "string"}}}
        )
        self.assertEqual(result, {"status": "ok"})
        config = self.fake.models.generation_calls[0]["config"]
        self.assertEqual(config.response_mime_type, "application/json")
        self.assertIsNotNone(config.response_json_schema)

    def test_embedding_roles_remain_separate(self) -> None:
        query = self.client.embed_query("query")
        documents = self.client.embed_documents(["doc one", "doc two"])
        self.assertEqual(len(query), 3072)
        self.assertEqual(len(documents), 2)
        self.assertEqual([len(vector) for vector in documents], [3072, 3072])
        query_config = self.fake.models.embedding_calls[0]["config"]
        document_config = self.fake.models.embedding_calls[1]["config"]
        self.assertEqual(query_config.task_type, "RETRIEVAL_QUERY")
        self.assertEqual(document_config.task_type, "RETRIEVAL_DOCUMENT")
        self.assertEqual(query_config.output_dimensionality, 3072)
        self.assertEqual(document_config.output_dimensionality, 3072)
        self.assertFalse(query_config.auto_truncate)

    def test_embedding_dimension_mismatch_reports_expected_and_actual(self) -> None:
        settings = VertexSettings(project="test-project")
        fake = FakeClient(settings.embedding_dimensions, response_dimensions=[3071])
        client = VertexAIClient(settings, client=fake)

        with self.assertRaisesRegex(
            VertexCallError,
            r"RETRIEVAL_QUERY.*gemini-embedding-2.*expected 3072.*actual 3071",
        ) as context:
            client.embed_query("secret query")

        self.assertNotIn("secret query", str(context.exception))

    def test_mixed_document_dimensions_fail_strictly(self) -> None:
        settings = VertexSettings(project="test-project")
        fake = FakeClient(settings.embedding_dimensions, response_dimensions=[3072, 0])
        client = VertexAIClient(settings, client=fake)

        with self.assertRaisesRegex(
            VertexCallError, r"RETRIEVAL_DOCUMENT.*expected 3072.*actual 0"
        ) as context:
            client.embed_documents(["first document", "wrong document"])

        self.assertNotIn("wrong document", str(context.exception))

    def test_embedding_response_count_mismatch_reports_expected_and_actual(self) -> None:
        settings = VertexSettings(project="test-project")
        fake = FakeClient(settings.embedding_dimensions, response_counts=[2])
        client = VertexAIClient(settings, client=fake)

        with self.assertRaisesRegex(
            VertexCallError,
            r"RETRIEVAL_QUERY.*gemini-embedding-2.*expected 1, actual 2",
        ) as context:
            client.embed_query("secret query")

        self.assertNotIn("secret query", str(context.exception))

    def test_health_check_reports_models_without_vectors(self) -> None:
        result = self.client.health_check()
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.query_embedding_dimensions, 3072)
        self.assertEqual(result.document_embedding_dimensions, 3072)
        self.assertNotIn("project", result.to_dict())

    def test_model_call_statistics_do_not_store_prompt_content(self) -> None:
        self.client.generate_json(
            "secret prompt", {"type": "object", "properties": {"status": {"type": "string"}}}
        )
        self.client.embed_query("secret query")
        stats = self.client.stats_snapshot()
        self.assertEqual(stats["model_calls"], 2)
        self.assertEqual(stats["generation_calls"], 1)
        self.assertEqual(stats["embedding_calls"], 1)
        self.assertNotIn("secret prompt", json.dumps(stats))

    def test_model_call_statistics_delta_has_all_observability_fields(self) -> None:
        before = self.client.stats_snapshot()
        self.client.generate_json(
            "health", {"type": "object", "properties": {"status": {"type": "string"}}}
        )
        self.client.embed_query("query")

        self.assertEqual(
            self.client.stats_delta(before),
            {"model_calls": 2, "token_usage": 0, "generation_calls": 1, "embedding_calls": 1},
        )


if __name__ == "__main__":
    unittest.main()
