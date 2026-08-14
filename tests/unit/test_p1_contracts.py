from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


class P1ContractTests(unittest.TestCase):
    def test_alias_preserves_correction_and_provenance(self):
        from panda_agent.models import KnowledgeAlias

        alias = KnowledgeAlias(
            alias_id="alias.restgas_profile_txt",
            alias_text="restgas_profile.txt",
            normalized_alias="restgas_profile.txt",
            target_object_id="configuration.restgas_profile",
            alias_kind="generic_user_term",
            source_version_id="restgas_determination@sha",
            review_status="accepted",
            provenance_object_ids=["object.readme"],
            correction_message="No literal file with this exact name exists.",
        )
        self.assertTrue(alias.correction_message)
        self.assertEqual(alias.provenance_object_ids, ["object.readme"])

    def test_index_identity_changes_with_model_or_dimensions(self):
        from panda_agent.indexing import IndexIdentity

        first = IndexIdentity(
            embedding_model="gemini-embedding-2",
            embedding_dimensions=3072,
            distance="cosine",
            sparse_model="Qdrant/bm25",
            sparse_vector_name="sparse",
            sparse_modifier="idf",
            index_schema_version="3",
        )
        second = first.model_copy(update={"embedding_dimensions": 768})
        self.assertNotEqual(first.fingerprint(), second.fingerprint())
        modifier_changed = first.model_copy(update={"sparse_modifier": "none"})
        self.assertNotEqual(first.fingerprint(), modifier_changed.fingerprint())

    def test_high_confidence_intent_router(self):
        from panda_agent.retrieval import route_high_confidence_intent

        self.assertEqual(route_high_confidence_intent("Where is PndTargetGenerator defined?"), "api")
        self.assertEqual(route_high_confidence_intent("Trace event_poca into pid_final.root"), "data_flow")
        self.assertEqual(route_high_confidence_intent("Which environment variables are required to install PandaRoot?"), "installation")
        self.assertEqual(route_high_confidence_intent("event_poca is missing: what should I inspect first?"), "troubleshooting")
        self.assertEqual(route_high_confidence_intent("How is POCA propagation implemented?"), "algorithm_implementation")
        self.assertEqual(route_high_confidence_intent("Explain the module structure"), "module_structure")

    def test_evaluation_store_checkpoints_each_case_and_resumes(self):
        from panda_agent.evaluation import EvaluationRunStore

        with tempfile.TemporaryDirectory() as temporary:
            store = EvaluationRunStore(Path(temporary), "run-1", {"dataset_hash": "abc"})
            store.record({"id": "q01", "result": {"status": "answered"}})
            reopened = EvaluationRunStore(Path(temporary), "run-1", {"dataset_hash": "abc"}, resume=True)
            self.assertEqual(reopened.completed_ids, {"q01"})


if __name__ == "__main__":
    unittest.main()
