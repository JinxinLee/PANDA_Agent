from pathlib import Path
from types import SimpleNamespace
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from panda_agent.config import FASTEMBED_MODEL_PATH_ENV, SPARSE_VECTOR_NAME, load_query_expansions
from panda_agent.retrieval import Retriever
from panda_agent.sparse import SparseEncoderReceipt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_REPOSITORIES = {
    "pandaroot": "18c09e91100db27867ded30e708b4dae95bd8357",
    "luminosityfit": "ddd83dcd1a74093bf48ef259a2849a67f9413f32",
    "restgas_determination": "11f1edc49dcbaeb61d707491a6d3bbec390fcd42",
}


class FakeVertex:
    def generate_json(self, prompt, schema, **kwargs):
        return {"intent":"algorithm_implementation","target_repositories":["pandaroot"],"concepts":["back propagation"],"symbols":["PndPidCorrelator"],"requested_versions":{},"concept_scopes":{}}


class RetrievalTests(unittest.TestCase):
    def test_init_uses_absolute_local_only_fastembed_runtime_path(self):
        with tempfile.TemporaryDirectory() as model_dir:
            with patch.dict(os.environ, {FASTEMBED_MODEL_PATH_ENV: model_dir}, clear=False):
                receipt = SparseEncoderReceipt(
                    model_name="Qdrant/bm25", language="english", vector_name="sparse", modifier="idf",
                    k=1.2, b=0.75, avg_len=256, token_max_length=40, disable_stemmer=False,
                    tokenizer="SimpleTokenizer", stemmer="SnowballStemmer", hash_function="mmh3.hash",
                    fastembed_version="0.7.4", mmh3_version="5.2.1", py_rust_stemmers_version="0.1.8",
                    stopwords_sha256="a" * 64,
                )
                sparse = Mock()
                storage = SimpleNamespace(require_sparse_receipt=Mock())
                with (
                    patch("panda_agent.retrieval.create_sparse_encoder", return_value=(sparse, receipt)) as factory,
                ):
                    retriever = Retriever(
                        PROJECT_ROOT,
                        storage=storage,
                        vertex=FakeVertex(),
                    )
            factory.assert_called_once_with(PROJECT_ROOT.resolve())
            storage.require_sparse_receipt.assert_called_once_with(receipt)
            self.assertEqual(retriever.sparse_vector_name, SPARSE_VECTOR_NAME)

    def test_sparse_query_uses_configured_sparse_vector_name(self):
        class Values:
            def __init__(self, values):
                self.values = values

            def tolist(self):
                return self.values

        calls = []

        class Qdrant:
            def query_points(self, **kwargs):
                calls.append(kwargs)
                return SimpleNamespace(points=[])

        retriever = Retriever.__new__(Retriever)
        retriever.vertex = SimpleNamespace(embed_query=lambda question: [0.1])
        retriever.sparse = SimpleNamespace(
            query_embed=lambda question: iter(
                [SimpleNamespace(indices=Values([1]), values=Values([0.5]))]
            )
        )
        retriever.sparse_vector_name = SPARSE_VECTOR_NAME
        retriever.context_sources = []
        retriever.storage = SimpleNamespace(
            settings=SimpleNamespace(collection_name="collection"), qdrant=Qdrant()
        )

        retriever._vector("identifier", SimpleNamespace(target_repositories=[]), 5)

        self.assertEqual(calls[1]["using"], SPARSE_VECTOR_NAME)

    def make_retriever(self):
        value=Retriever.__new__(Retriever)
        value.vertex=FakeVertex()
        value.fixed_versions=TEST_REPOSITORIES
        value.fixed_refs={repo:"dev" for repo in TEST_REPOSITORIES}
        value.web_version_tokens={"2023-08-25-dev"}
        policy=SimpleNamespace(source_budgets={"paper":0.3,"code":0.4,"graph":0.15,"documentation":0.1,"workflow":0.05},required_sources=["paper","code"])
        value.policies=SimpleNamespace(intents={
            intent: policy for intent in (
                "installation", "usage", "algorithm_theory", "algorithm_implementation",
                "api", "data_flow", "module_structure", "troubleshooting",
            )
        })
        value.query_expansions=load_query_expansions(PROJECT_ROOT / "configs" / "query_expansions.yaml")
        return value

    def test_analyzer_resolves_locked_version_and_scope(self):
        plan=self.make_retriever().analyze("PndPidCorrelator 的 back propagation 如何实现？")
        self.assertEqual(plan.resolved_versions["pandaroot"],"18c09e91100db27867ded30e708b4dae95bd8357")
        self.assertEqual(plan.concept_scopes["back_propagation"],"target_track_to_event_poca")

    def test_explicit_wrong_sha_creates_conflict(self):
        plan=self.make_retriever().analyze("Use PandaRoot commit deadbeef for PndTargetGenerator")
        self.assertTrue(plan.version_conflicts)

    def test_source_types_are_not_conflated(self):
        self.assertEqual(Retriever._source_type({"source_id":"li_2026","object_type":"thesis_section"}),"paper")
        self.assertEqual(Retriever._source_type({"source_id":"pandaroot_sphinx_2023_08_25_dev","object_type":"sphinx_page"}),"documentation")
        self.assertEqual(Retriever._source_type({"source_id":"pandaroot","object_type":"source_file"}),"code")

    def test_sphinx_snapshot_label_is_not_treated_as_repository_ref(self):
        retriever=self.make_retriever()
        retriever.vertex.generate_json=lambda prompt,schema,**kwargs: {"intent":"algorithm_implementation","target_repositories":["pandaroot"],"concepts":[],"symbols":[],"requested_versions":{"pandaroot":"2023-dev"},"concept_scopes":{}}
        plan=retriever.analyze("Why can 2023-dev Sphinx documentation differ from code?")
        self.assertEqual(plan.version_conflicts,[])

    def test_real_expansion_config_adds_reviewed_workflow_and_factory_anchors(self):
        retriever=self.make_retriever()

        master_plan=retriever.analyze("Explain the PndMasterRecoTask master reconstruction workflow.")
        self.assertTrue({"Running/Running.html", "Running/MasterTasks.html", "tools/MasterTasks/PndMasterRecoTask.cxx"}.issubset(master_plan.symbols))
        self.assertIn("PandaRoot running sequence", master_plan.concepts)

        generator_plan=retriever.analyze("Trace PndMasterRunSim and PndTargetGenerator data flow through SampleInteractionVertex.")
        self.assertTrue({"pandaroot", "restgas_determination"}.issubset(generator_plan.target_repositories))
        self.assertTrue({"tools/MasterTasks/PndMasterRunSim.cxx", "pgenerators/Target/PndTargetGenerator.cxx", "PndTargetGenerator::SampleInteractionVertex", "Tools/PndMasterTasks/PndMasterRunSim.html", "Running/Running.html", "Running/MasterTasks.html"}.issubset(generator_plan.symbols))
        self.assertIn("PandaRoot operational documentation", generator_plan.concepts)
        self.assertIn("generic PandaRoot workflow", generator_plan.concepts)

        factory_plan=retriever.analyze("How does beam divergence reach PndLmdModelFactory through effective acceptance?")
        self.assertTrue({"PndLmdModelFactory::setAcceptance", "PndLmdModelFactory::generate2DModel"}.issubset(factory_plan.symbols))
        self.assertIn("luminosityfit", factory_plan.target_repositories)

        acceptance_plan=retriever.analyze("How does PndLmdAcceptance enter PndLmdModelFactory for the effective acceptance fit?")
        self.assertTrue({"PndLmdModelFactory::setAcceptance", "PndLmdModelFactory::generate2DModel"}.issubset(acceptance_plan.symbols))
        self.assertIn("data/PndLmdAcceptance.cxx", acceptance_plan.symbols)

    def test_real_expansion_config_preserves_restgas_troubleshooting_context(self):
        retriever=self.make_retriever()

        efficiency_plan=retriever.analyze("Where is longitudinal restgas efficiency correction implemented?")
        self.assertIn("restgas_determination", efficiency_plan.target_repositories)
        self.assertNotIn("luminosityfit", efficiency_plan.target_repositories)
        self.assertIn("macro/target/correction/efficiency_correction_2.C", efficiency_plan.symbols)
        self.assertIn("macro/target/correction/efficiency_correction_steps.C", efficiency_plan.symbols)
        self.assertNotIn("data/PndLmdAcceptance.cxx", efficiency_plan.symbols)
        self.assertIn("angular acceptance versus longitudinal efficiency distinction", efficiency_plan.concepts)

        poca_plan=retriever.analyze("Troubleshoot event_poca missing after second-pass PID.")
        self.assertTrue({"macro/target/pid_complete.C", "macro/target/ana_dpm.C"}.issubset(poca_plan.symbols))
        self.assertIn("first-pass PID input and prefix context", poca_plan.concepts)

        empty_bin_plan=retriever.analyze("Troubleshoot empty bins in restgas profile efficiency correction.")
        self.assertTrue({"macro/target/correction/efficiency_correction_2.C", "macro/target/correction/efficiency_correction_steps.C"}.issubset(empty_bin_plan.symbols))
        self.assertIn("empty-bin binning and profile compatibility", empty_bin_plan.concepts)

    def test_unrelated_question_does_not_receive_new_domain_anchors(self):
        plan=self.make_retriever().analyze("How do I install PandaRoot?")
        self.assertNotIn("tools/MasterTasks/PndMasterRecoTask.cxx", plan.symbols)
        self.assertNotIn("PndTargetGenerator::SampleInteractionVertex", plan.symbols)
        self.assertNotIn("PndLmdModelFactory::setAcceptance", plan.symbols)
        self.assertNotIn("PndLmdAcceptance angular-acceptance contrast", plan.concepts)

    def test_bare_master_run_sim_does_not_receive_target_generator_anchors(self):
        """A RunSim configuration query stays in PandaRoot's own domain."""
        plan=self.make_retriever().analyze("How is PndMasterRunSim used to configure a simulation?")
        self.assertNotIn("restgas_determination", plan.target_repositories)
        self.assertNotIn("pgenerators/Target/PndTargetGenerator.cxx", plan.symbols)
        self.assertNotIn("PndTargetGenerator::SampleInteractionVertex", plan.symbols)
        self.assertNotIn("simulation master task to target-generator data flow", plan.concepts)


if __name__ == "__main__": unittest.main()
