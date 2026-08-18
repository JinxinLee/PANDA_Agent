from pathlib import Path
from types import SimpleNamespace
import os
import re
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


def _query_span(question, value):
    if not isinstance(value, str) or not value:
        return []
    match = re.search(re.escape(value), question, re.IGNORECASE)
    return [question[match.start():match.end()]] if match else []


def _legacy_delta(result, question, deterministic_context):
    if "repository_additions" in result:
        return result
    delta = {
        "repository_additions": [],
        "concepts": [],
        "symbols": [],
        "version_mentions": [],
        "concept_scopes": [],
    }
    if deterministic_context.get("fixed", {}).get("intent") is None and result.get("intent"):
        delta["intent"] = {
            "value": result["intent"],
            "support_spans": [question[: min(24, len(question))]],
        }
    repository_aliases = {
        "pandaroot": "PandaRoot",
        "luminosityfit": "LuminosityFit",
        "restgas_determination": "RestgasDetermination",
    }
    for repository in result.get("target_repositories", []):
        span = _query_span(question, repository_aliases.get(repository, repository))
        if span:
            delta["repository_additions"].append({"value": repository, "support_spans": span})
    for field_name in ("concepts", "symbols"):
        for value in result.get(field_name, []):
            span = _query_span(question, value)
            if span:
                delta[field_name].append({"value": value, "support_spans": span})
    for repository, token in result.get("requested_versions", {}).items():
        span = _query_span(question, token)
        if span:
            delta["version_mentions"].append({
                "token": token,
                "repository": repository,
                "support_spans": span,
            })
    for key, value in result.get("concept_scopes", {}).items():
        delta["concept_scopes"].append({
            "key": key,
            "value": value,
            "support_spans": [question[: min(24, len(question))]],
        })
    return delta


class FakeVertex:
    def generate_json(self, prompt, schema, **kwargs):
        import json

        payload = json.loads(prompt)
        question = payload["untrusted_question"]
        result = {
            "repository_additions": [],
            "concepts": [],
            "symbols": [],
            "version_mentions": [],
            "concept_scopes": [],
        }
        if payload["deterministic_context"]["fixed"].get("intent") is None:
            result["intent"] = {
                "value": "algorithm_implementation",
                "support_spans": [question[: min(24, len(question))]],
            }
        if "back propagation" in question.casefold():
            result["concepts"].append({
                "value": "back propagation", "support_spans": ["back propagation"],
            })
        if "PndPidCorrelator" in question:
            result["symbols"].append({
                "value": "PndPidCorrelator", "support_spans": ["PndPidCorrelator"],
            })
        return result


class CapturingVertex(FakeVertex):
    def __init__(self, result=None):
        self.calls = []
        self.schemas = []
        self.result = result or {
            "intent": "api", "target_repositories": ["pandaroot"],
            "concepts": [], "symbols": [], "requested_versions": {}, "concept_scopes": {},
        }

    def generate_json(self, prompt, schema, **kwargs):
        import json

        payload = json.loads(prompt)
        self.calls.append(payload)
        self.schemas.append(schema)
        return _legacy_delta(
            self.result,
            payload["untrusted_question"],
            payload["deterministic_context"],
        )


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

    def test_ambiguous_intent_remains_analyzer_owned(self):
        retriever = self.make_retriever()
        retriever.vertex = CapturingVertex()

        plan = retriever.analyze("Describe this pipeline.")

        context = retriever.vertex.calls[0]["deterministic_context"]
        self.assertEqual(context["fixed"], {})
        self.assertIn("intent", context["unresolved_semantics"])
        self.assertIn("intent", retriever.vertex.schemas[0]["required"])
        self.assertNotIn("target_repositories", context["known_partial"])
        self.assertNotIn("concepts", context["known_partial"])
        self.assertEqual(context["unresolved_semantics"]["target_repositories"], "resolve")
        self.assertEqual(context["unresolved_semantics"]["concepts"], "resolve")
        self.assertEqual(plan.intent, "api")
        self.assertEqual(plan.analysis_diagnostics["analyzer_llm_called"], True)

    def test_explicit_repository_and_sha_are_preparsed_before_merge(self):
        retriever = self.make_retriever()
        retriever.vertex = CapturingVertex({
            "intent": "api", "target_repositories": ["luminosityfit"],
            "concepts": [], "symbols": [],
            "requested_versions": {"pandaroot": "18c09e9"}, "concept_scopes": {},
        })

        plan = retriever.analyze("Use PandaRoot commit deadbeef for PndTargetGenerator")

        context = retriever.vertex.calls[0]["deterministic_context"]
        self.assertIn("pandaroot", context["known_partial"]["target_repositories"])
        self.assertEqual(context["fixed"]["requested_versions"]["pandaroot"], "deadbeef")
        self.assertNotIn("requested_versions", context["known_partial"])
        self.assertEqual(context["unresolved_semantics"]["target_repositories"], "augment_known_partial")
        self.assertNotIn("version_mentions", context["semantic_output_fields"])
        self.assertNotIn("requested_versions", context["unresolved_semantics"])
        self.assertEqual(context["provenance"]["target_repositories"][0]["ownership"], "known_partial")
        self.assertEqual(context["provenance"]["requested_versions"][0]["ownership"], "fixed")
        self.assertEqual(plan.analysis_diagnostics["analyzer_final"]["requested_versions"]["pandaroot"], "deadbeef")
        self.assertTrue(plan.version_conflicts)

    def test_c1_plan_compatibility_for_deterministic_and_llm_owned_intents(self):
        policies = SimpleNamespace(intents={
            "api": SimpleNamespace(
                source_budgets={"code": 0.7, "documentation": 0.3},
                required_sources=["code"],
            ),
            "installation": SimpleNamespace(
                source_budgets={"documentation": 1.0}, required_sources=["documentation"],
            ),
            "data_flow": SimpleNamespace(
                source_budgets={"workflow": 0.6, "code": 0.4},
                required_sources=["workflow", "code"],
            ),
        })
        cases = [
            {
                "name": "deterministic_api_route",
                "question": "Where is PndTargetGenerator defined?",
                "analyzer": {
                    "intent": "installation", "target_repositories": ["pandaroot"],
                    "concepts": [], "symbols": [],
                    "requested_versions": {"pandaroot": "dev"}, "concept_scopes": {},
                },
                "intent": "api",
                "repositories": ["pandaroot", "restgas_determination"],
                "requested_versions": {},
                "source_budgets": {"code": 0.7, "documentation": 0.3},
                "required_sources": ["code"],
            },
            {
                "name": "ambiguous_llm_route",
                "question": "Describe this pipeline.",
                "analyzer": {
                    "intent": "data_flow", "target_repositories": ["restgas_determination"],
                    "concepts": ["pipeline"], "symbols": [],
                    "requested_versions": {"restgas_determination": "oct19"}, "concept_scopes": {},
                },
                "intent": "data_flow",
                "repositories": list(TEST_REPOSITORIES),
                "requested_versions": {},
                "source_budgets": {"workflow": 0.6, "code": 0.4},
                "required_sources": ["workflow", "code"],
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                retriever = self.make_retriever()
                retriever.policies = policies
                retriever.vertex = CapturingVertex(case["analyzer"])

                plan = retriever.analyze(case["question"])

                self.assertEqual(plan.intent, case["intent"])
                self.assertEqual(plan.target_repositories, case["repositories"])
                self.assertEqual(
                    plan.analysis_diagnostics["analyzer_final"]["requested_versions"],
                    case["requested_versions"],
                )
                self.assertEqual(
                    plan.resolved_versions,
                    {repo: TEST_REPOSITORIES[repo] for repo in case["repositories"]},
                )
                self.assertEqual(plan.required_source_types, case["required_sources"])
                self.assertEqual(plan.source_budgets, case["source_budgets"])

    def test_alias_and_reviewed_expansion_have_preparse_provenance(self):
        class AliasConnection:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def execute(self, query):
                return SimpleNamespace(fetchall=lambda: [
                    ("POCA", "object.event_poca", {"correction_message": "Use event POCA."}),
                ])

        retriever = self.make_retriever()
        retriever.vertex = CapturingVertex()
        retriever.storage = SimpleNamespace(connect=lambda: AliasConnection())

        plan = retriever.analyze("Explain POCA and the PndMasterRecoTask master reconstruction workflow.")

        parsed = plan.analysis_diagnostics["deterministic_parse"]
        self.assertEqual(plan.resolved_aliases, {"POCA": "object.event_poca"})
        self.assertIn("master_reconstruction_workflow", parsed["fixed"]["matched_expansion_rules"])
        self.assertNotIn("matched_expansion_rules", parsed["known_partial"])
        self.assertIn("tools/MasterTasks/PndMasterRecoTask.cxx", parsed["known_partial"]["symbols"])
        self.assertIn("PandaRoot running sequence", parsed["known_partial"]["concepts"])
        self.assertEqual(parsed["fixed"]["resolved_aliases"], {"POCA": "object.event_poca"})
        self.assertNotIn("resolved_aliases", parsed["known_partial"])
        self.assertEqual(parsed["provenance"]["resolved_aliases"][0]["source"], "accepted_alias")
        self.assertEqual(parsed["provenance"]["query_expansions"][0]["source"], "reviewed_expansion")
        self.assertEqual(parsed["provenance"]["resolved_aliases"][0]["ownership"], "fixed")
        self.assertEqual(parsed["provenance"]["query_expansions"][0]["ownership"], "fixed_reviewed_rule")

    def test_near_match_does_not_route_intent_deterministically(self):
        retriever = self.make_retriever()
        retriever.vertex = CapturingVertex()

        retriever.analyze("Where could PndTargetGenerator perhaps be mentioned?")

        context = retriever.vertex.calls[0]["deterministic_context"]
        self.assertNotIn("intent", context["fixed"])
        self.assertIn("intent", context["unresolved_semantics"])

    def test_scope_fallbacks_yield_to_explicit_llm_scopes(self):
        cases = [
            (
                "Explain back propagation from LMD to IP rather than target track to event POCA.",
                "back_propagation", "lmd_to_ip", "target_track_to_event_poca",
                "back propagation", "target track to event POCA",
            ),
            (
                "Explain efficiency as angular acceptance rather than longitudinal profile.",
                "efficiency", "longitudinal_profile", "angular_acceptance",
                "efficiency", "angular acceptance",
            ),
        ]
        for question, scope_key, fallback_value, llm_value, intent_span, scope_span in cases:
            with self.subTest(question=question):
                retriever = self.make_retriever()
                retriever.vertex = SemanticDeltaVertex({
                    "intent": {"value": "algorithm_implementation", "support_spans": [intent_span]},
                    "repository_additions": [], "concepts": [], "symbols": [],
                    "version_mentions": [],
                    "concept_scopes": [{
                        "key": scope_key, "value": llm_value, "support_spans": [scope_span],
                    }],
                })

                plan = retriever.analyze(question)

                self.assertEqual(plan.concept_scopes[scope_key], llm_value)
                context = retriever.vertex.calls[0]["deterministic_context"]
                self.assertEqual(context["fallback"]["concept_scopes"][scope_key], fallback_value)
                self.assertNotIn("concept_scopes", context["fixed"])
                self.assertEqual(
                    context["unresolved_semantics"]["concept_scopes"],
                    "resolve_remaining_scope_keys_with_fallback",
                )
                self.assertEqual(context["provenance"]["concept_scopes"][0]["ownership"], "fallback")

    def test_fixed_intent_uses_schema_without_intent(self):
        retriever = self.make_retriever()
        retriever.vertex = CapturingVertex({
            "target_repositories": ["pandaroot"], "concepts": [], "symbols": [],
            "requested_versions": {}, "concept_scopes": {},
        })

        plan = retriever.analyze("Where is PndTargetGenerator defined?")

        self.assertEqual(plan.intent, "api")
        self.assertNotIn("intent", retriever.vertex.schemas[0]["properties"])
        self.assertNotIn("intent", retriever.vertex.schemas[0]["required"])
        self.assertEqual(
            retriever.vertex.calls[0]["deterministic_context"]["provenance"]["intent"][0]["ownership"],
            "fixed",
        )

    def test_repository_near_match_respects_boundaries(self):
        retriever = self.make_retriever()
        retriever.vertex = CapturingVertex({
            "intent": "api", "target_repositories": ["luminosityfit"],
            "concepts": [], "symbols": [], "requested_versions": {}, "concept_scopes": {},
        })

        plan = retriever.analyze("Explain PandaRootedConfiguration.")

        self.assertEqual(plan.target_repositories, list(TEST_REPOSITORIES))
        context = retriever.vertex.calls[0]["deterministic_context"]
        self.assertNotIn("pandaroot", context["known_partial"].get("target_repositories", []))

    def test_fixed_scope_comparisons_override_contradictory_llm_scopes(self):
        cases = [
            ("Compare angular acceptance with longitudinal efficiency.", "efficiency", "angular_acceptance_vs_longitudinal_profile"),
            ("Compare point-like acceptance with restgas effective acceptance.", "acceptance", "point_like_vs_restgas_effective"),
            ("Compare lmd-to-ip with event-poca.", "back_propagation", "lmd_to_ip_vs_target_track_to_event_poca"),
        ]
        for question, scope_key, expected in cases:
            with self.subTest(question=question):
                retriever = self.make_retriever()
                retriever.vertex = CapturingVertex({
                    "intent": "algorithm_theory", "target_repositories": ["pandaroot"],
                    "concepts": [], "symbols": [], "requested_versions": {},
                    "concept_scopes": {scope_key: "contradictory_llm_scope"},
                })

                plan = retriever.analyze(question)

                self.assertEqual(plan.concept_scopes[scope_key], expected)
                context = retriever.vertex.calls[0]["deterministic_context"]
                self.assertEqual(context["fixed"]["concept_scopes"][scope_key], expected)
                self.assertEqual(
                    context["unresolved_semantics"]["concept_scopes"],
                    "resolve_remaining_scope_keys_after_fixed_constraints",
                )

    def test_source_types_are_not_conflated(self):
        self.assertEqual(Retriever._source_type({"source_id":"li_2026","object_type":"thesis_section"}),"paper")
        self.assertEqual(Retriever._source_type({"source_id":"pandaroot_sphinx_2023_08_25_dev","object_type":"sphinx_page"}),"documentation")
        self.assertEqual(Retriever._source_type({"source_id":"pandaroot","object_type":"source_file"}),"code")

    def test_sphinx_snapshot_label_is_not_treated_as_repository_ref(self):
        retriever=self.make_retriever()
        retriever.vertex.generate_json=lambda prompt,schema,**kwargs: {
            "intent": {"value": "algorithm_implementation", "support_spans": ["2023-dev"]},
            "repository_additions": [], "concepts": [], "symbols": [],
            "version_mentions": [{"token": "2023-dev", "support_spans": ["2023-dev"]}],
            "concept_scopes": [],
        }
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


class SemanticDeltaVertex:
    def __init__(self, result):
        self.result = result
        self.calls = []
        self.schemas = []

    def generate_json(self, prompt, schema, **kwargs):
        import json

        self.calls.append(json.loads(prompt))
        self.schemas.append(schema)
        return self.result


class SemanticDeltaTests(unittest.TestCase):
    def make_retriever(self, result):
        retriever = RetrievalTests().make_retriever()
        retriever.vertex = SemanticDeltaVertex(result)
        return retriever

    @staticmethod
    def delta(**overrides):
        result = {
            "repository_additions": [],
            "concepts": [],
            "symbols": [],
            "version_mentions": [],
            "concept_scopes": [],
        }
        result.update(overrides)
        return result

    def test_invented_symbol_path_is_rejected_with_item_diagnostic(self):
        retriever = self.make_retriever(self.delta(symbols=[
            {"value": "PndTargetGenerator", "support_spans": ["PndTargetGenerator"]},
            {"value": "PndTargetGenerator.cxx", "support_spans": ["PndTargetGenerator"]},
        ]))

        plan = retriever.analyze("Where is PndTargetGenerator defined?")

        self.assertIn("PndTargetGenerator", plan.symbols)
        self.assertNotIn("PndTargetGenerator.cxx", plan.symbols)
        diagnostics = plan.analysis_diagnostics
        self.assertIn("analyzer_semantic_output_fields", diagnostics)
        self.assertNotIn("analyzer_unresolved_fields", diagnostics)
        self.assertEqual(diagnostics["analyzer_raw_semantic_delta"]["symbols"][1]["value"],
                         "PndTargetGenerator.cxx")
        self.assertEqual(
            diagnostics["analyzer_accepted_semantic_delta"]["symbols"][0]["support_spans"],
            ["PndTargetGenerator"],
        )
        self.assertTrue(diagnostics["analyzer_item_support"]["symbols"])
        self.assertIn("analyzer_final", diagnostics)
        self.assertTrue(any(
            item["field"] == "symbols" and item["reason"] == "unsupported_symbol"
            for item in diagnostics["analyzer_rejected_items"]
        ))

    def test_symbol_substring_requires_complete_technical_token(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "usage", "support_spans": ["use"]},
            symbols=[{
                "value": "PndTarget",
                "support_spans": ["PndTargetGenerator"],
            }],
        ))

        plan = retriever.analyze("How do PandaRoot developers use PndTargetGenerator?")

        self.assertNotIn("PndTarget", plan.symbols)
        self.assertTrue(any(
            item["field"] == "symbols" and item["reason"] == "unsupported_symbol"
            for item in plan.analysis_diagnostics["analyzer_rejected_items"]
        ))

    def test_version_substring_requires_complete_technical_token(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "usage", "support_spans": ["use"]},
            version_mentions=[{
                "token": "dev",
                "support_spans": ["developers"],
            }],
        ))

        plan = retriever.analyze("How do PandaRoot developers use PndTargetGenerator?")

        self.assertEqual(plan.analysis_diagnostics["analyzer_final"]["requested_versions"], {})
        self.assertNotIn("dev", plan.analysis_diagnostics["unbound_version_tokens"])
        self.assertTrue(any(
            item["field"] == "version_mentions" and item["reason"] == "unsupported_version"
            for item in plan.analysis_diagnostics["analyzer_rejected_items"]
        ))

    def test_complete_symbol_and_version_tokens_remain_accepted(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "usage", "support_spans": ["Use"]},
            symbols=[{
                "value": "PndTargetGenerator",
                "support_spans": ["PndTargetGenerator"],
            }],
            version_mentions=[
                {"token": "deadbeef", "support_spans": ["deadbeef"]},
                {"token": "2023-dev", "support_spans": ["2023-dev"]},
            ],
        ))

        plan = retriever.analyze(
            "Use PndTargetGenerator at 2023-dev with commit deadbeef."
        )

        self.assertIn("PndTargetGenerator", plan.symbols)
        accepted_versions = plan.analysis_diagnostics["analyzer_accepted_semantic_delta"]["version_mentions"]
        self.assertEqual([item["token"] for item in accepted_versions], ["deadbeef", "2023-dev"])

    def test_speculative_concept_is_rejected(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "algorithm_theory", "support_spans": ["efficiency"]},
            concepts=[
            {"value": "efficiency", "support_spans": ["efficiency"]},
            {"value": "answer location in source file", "support_spans": ["efficiency"]},
            ],
            concept_scopes=[{
                "key": "answer_location",
                "value": "source_file",
                "support_spans": ["efficiency"],
            }],
        ))

        plan = retriever.analyze("Explain efficiency.")

        self.assertEqual(plan.concepts, ["efficiency"])
        self.assertTrue(any(
            item["field"] == "concepts" and item["reason"] == "unsupported_concept"
            for item in plan.analysis_diagnostics["analyzer_rejected_items"]
        ))
        self.assertTrue(any(
            item["field"] == "concept_scopes" and item["reason"] == "unsupported_scope"
            for item in plan.analysis_diagnostics["analyzer_rejected_items"]
        ))

    def test_speculative_concept_suffix_is_rejected(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "algorithm_theory", "support_spans": ["efficiency"]},
            concepts=[{
                "value": "efficiency source file",
                "support_spans": ["efficiency"],
            }],
        ))

        plan = retriever.analyze("Explain efficiency.")

        self.assertNotIn("efficiency source file", plan.concepts)
        self.assertTrue(any(
            item["field"] == "concepts" and item["reason"] == "unsupported_concept"
            for item in plan.analysis_diagnostics["analyzer_rejected_items"]
        ))

    def test_unsupported_repository_addition_is_rejected(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "usage", "support_spans": ["used"]},
            repository_additions=[
                {"value": "luminosityfit", "support_spans": ["PandaRoot"]},
            ],
        ))

        plan = retriever.analyze("How is PandaRoot used?")

        self.assertEqual(plan.target_repositories, ["pandaroot"])
        self.assertTrue(any(
            item["field"] == "repository_additions" and item["reason"] == "unsupported_repository"
            for item in plan.analysis_diagnostics["analyzer_rejected_items"]
        ))

    def test_bare_sha_stays_unbound_without_false_conflict(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "usage", "support_spans": ["behavior"]},
            repository_additions=[{"value": "pandaroot", "support_spans": ["behavior"]}],
            version_mentions=[{
                "token": "deadbeef", "repository": "pandaroot", "support_spans": ["deadbeef"],
            }],
        ))

        plan = retriever.analyze("Use commit deadbeef for this behavior.")

        self.assertEqual(plan.version_conflicts, [])
        self.assertEqual(plan.analysis_diagnostics["unbound_version_tokens"], ["deadbeef"])
        self.assertEqual(plan.analysis_diagnostics["analyzer_final"]["requested_versions"], {})

    def test_ambiguous_multi_repository_sha_does_not_bind(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "usage", "support_spans": ["commit"]},
            version_mentions=[{
                "token": "deadbeef", "repository": "pandaroot", "support_spans": ["deadbeef", "PandaRoot"],
            }],
        ))

        plan = retriever.analyze("Use commit deadbeef with PandaRoot and LuminosityFit.")

        self.assertEqual(plan.target_repositories, ["pandaroot", "luminosityfit"])
        self.assertEqual(plan.analysis_diagnostics["unbound_version_tokens"], ["deadbeef"])
        self.assertEqual(plan.analysis_diagnostics["analyzer_final"]["requested_versions"], {})
        self.assertEqual(plan.version_conflicts, [])

    def test_single_repo_sha_without_explicit_association_stays_unbound(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "usage", "support_spans": ["behavior"]},
            version_mentions=[{
                "token": "deadbeef",
                "repository": "pandaroot",
                "support_spans": ["PandaRoot", "deadbeef"],
            }],
        ))

        plan = retriever.analyze(
            "Compare PandaRoot behavior with commit deadbeef from another checkout."
        )

        self.assertEqual(plan.analysis_diagnostics["analyzer_final"]["requested_versions"], {})
        self.assertEqual(plan.analysis_diagnostics["unbound_version_tokens"], ["deadbeef"])
        self.assertEqual(plan.version_conflicts, [])

    def test_fixed_intent_is_omitted_and_unresolved_intent_is_grounded(self):
        fixed = self.make_retriever(self.delta(
            intent={"value": "installation", "support_spans": ["defined"]},
            symbols=[
                {"value": "PndTargetGenerator", "support_spans": ["PndTargetGenerator"]},
            ],
        ))
        fixed_plan = fixed.analyze("Where is PndTargetGenerator defined?")
        self.assertNotIn("intent", fixed.vertex.schemas[0]["properties"])
        self.assertNotIn("intent", fixed.vertex.schemas[0]["required"])
        self.assertNotIn("intent", fixed_plan.analysis_diagnostics["analyzer_accepted_semantic_delta"])
        self.assertTrue(any(
            item["field"] == "intent" and item["reason"] == "fixed_intent_output"
            for item in fixed_plan.analysis_diagnostics["analyzer_rejected_items"]
        ))

        unresolved = self.make_retriever(self.delta(
            intent={"value": "data_flow", "support_spans": ["pipeline"]},
        ))
        plan = unresolved.analyze("Describe this pipeline.")
        self.assertEqual(plan.intent, "data_flow")
        self.assertIn("intent", unresolved.vertex.schemas[0]["required"])
        self.assertEqual(
            plan.analysis_diagnostics["analyzer_accepted_semantic_delta"]["intent"]["support_spans"],
            ["pipeline"],
        )

    def test_supported_items_retain_query_support(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "algorithm_implementation", "support_spans": ["back propagation"]},
            repository_additions=[{"value": "pandaroot", "support_spans": ["PandaRoot"]}],
            concepts=[{"value": "back propagation", "support_spans": ["back propagation"]}],
            symbols=[{"value": "PndPidCorrelator", "support_spans": ["PndPidCorrelator"]}],
            version_mentions=[{"token": "2023-dev", "support_spans": ["2023-dev"]}],
            concept_scopes=[{
                "key": "back_propagation", "value": "target_track_to_event_poca",
                "support_spans": ["back propagation", "target track to event POCA"],
            }],
        ))

        plan = retriever.analyze(
            "How does PndPidCorrelator implement back propagation in PandaRoot at 2023-dev "
            "for target track to event POCA?"
        )

        accepted = plan.analysis_diagnostics["analyzer_accepted_semantic_delta"]
        self.assertTrue(accepted["intent"]["support_spans"])
        self.assertTrue(accepted["repository_additions"][0]["support_spans"])
        self.assertTrue(accepted["concepts"][0]["support_spans"])
        self.assertTrue(accepted["symbols"][0]["support_spans"])
        self.assertTrue(accepted["version_mentions"][0]["support_spans"])
        self.assertTrue(accepted["concept_scopes"][0]["support_spans"])
        self.assertTrue(plan.analysis_diagnostics["analyzer_item_support"]["intent"])
        self.assertTrue(plan.analysis_diagnostics["analyzer_item_support"]["repository_additions"])
        self.assertTrue(plan.analysis_diagnostics["analyzer_item_support"]["concepts"])
        self.assertTrue(plan.analysis_diagnostics["analyzer_item_support"]["symbols"])
        self.assertTrue(plan.analysis_diagnostics["analyzer_item_support"]["version_mentions"])
        self.assertTrue(plan.analysis_diagnostics["analyzer_item_support"]["concept_scopes"])
        self.assertEqual(plan.concept_scopes["back_propagation"], "target_track_to_event_poca")
        self.assertEqual(retriever.vertex.calls[0]["untrusted_question"],
                         "How does PndPidCorrelator implement back propagation in PandaRoot at 2023-dev "
                         "for target track to event POCA?")

    def test_explicit_multi_repository_query_and_plan_compatibility(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "data_flow", "support_spans": ["Trace"]},
            concepts=[{"value": "data flow", "support_spans": ["data flow"]}],
        ))

        plan = retriever.analyze(
            "Trace data flow through PandaRoot and RestgasDetermination."
        )

        self.assertEqual(plan.target_repositories, ["pandaroot", "restgas_determination"])
        self.assertEqual(plan.intent, "data_flow")
        self.assertIn("data flow", plan.concepts)
        self.assertIn("resolved_versions", plan.model_dump())

    def test_explicit_repository_sha_remains_fixed_and_conflicts(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "usage", "support_spans": ["commit"]},
            version_mentions=[{
                "token": "deadbeef", "repository": "pandaroot", "support_spans": ["deadbeef", "PandaRoot"],
            }],
        ))

        plan = retriever.analyze("Use PandaRoot commit deadbeef for PndTargetGenerator.")

        self.assertEqual(plan.analysis_diagnostics["analyzer_final"]["requested_versions"],
                         {"pandaroot": "deadbeef"})
        self.assertTrue(plan.version_conflicts)

    def test_unrequested_fixed_field_is_rejected_even_if_fake_bypasses_schema(self):
        retriever = self.make_retriever(self.delta(
            intent={"value": "usage", "support_spans": ["commit"]},
            version_mentions=[{
                "token": "deadbeef", "repository": "pandaroot",
                "support_spans": ["deadbeef", "PandaRoot"],
            }],
        ))

        plan = retriever.analyze("Use PandaRoot commit deadbeef for PndTargetGenerator.")

        self.assertEqual(
            plan.analysis_diagnostics["analyzer_accepted_semantic_delta"]["version_mentions"],
            [],
        )
        self.assertTrue(any(
            item["field"] == "version_mentions" and item["reason"] == "unrequested_delta_field"
            for item in plan.analysis_diagnostics["analyzer_rejected_items"]
        ))


if __name__ == "__main__": unittest.main()
