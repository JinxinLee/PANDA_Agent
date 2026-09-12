import json
import inspect
import tempfile
import unittest
from pathlib import Path

from panda_agent.models import QAStatus
from panda_agent.prompts import PROMPT_SET_VERSION
from panda_agent.qa import (
    ANSWER_SCHEMA,
    QAAgent,
    _answer_requirements,
    _compact_requirement_evidence,
    _deterministic_missing_requirement_ids,
    _refusal_basis_evidence,
    _requested_bare_class_symbols,
    _requirement_evidence,
)


class NoStorage:
    def connect(self):
        raise RuntimeError("not used")


class FakeRetriever:
    def __init__(self, bundle, storage=None):
        self.bundle = bundle
        self.storage = storage or CatalogStorage([])
        self.calls = 0

    def retrieve(self, question, plan=None, capture_candidates: bool = False):
        self.calls += 1
        return self.bundle


class CatalogConnection:
    def __init__(self, rows):
        self.rows = rows
        self.queries = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query, params=None):
        self.queries.append((query, params))
        return self

    def fetchall(self):
        return self.rows


class CatalogStorage:
    def __init__(self, rows):
        self.connection = CatalogConnection(rows)
        self.connect_calls = 0

    def connect(self):
        self.connect_calls += 1
        return self.connection


def code_evidence(
    *,
    evidence_id="e1",
    source_id="pandaroot",
    text="class PndPidCorrelator {};",
    path="pid/PndPidCorrelator.h",
    object_type="class",
    channel="exact",
):
    return {
        "evidence_id": evidence_id,
        "object_id": f"o-{evidence_id}",
        "source_id": source_id,
        "source_version_id": (
            f"{source_id}@18c09e91100db27867ded30e708b4dae95bd8357"
            if source_id == "pandaroot"
            else f"{source_id}@11f1edc49dcbaeb61d707491a6d3bbec390fcd42"
        ),
        "text": text,
        "locator": {
            "path": path,
            "symbol": "PndPidCorrelator" if "PndPid" in text else None,
            "start_line": 1,
            "end_line": 4,
            "section_path": [],
        },
        "retrieval_channels": [channel],
        "score": 1.0,
        "authority_level": "primary",
    }


def web_evidence(evidence_id="e2"):
    return {
        "evidence_id": evidence_id,
        "object_id": f"o-{evidence_id}",
        "source_id": "pandaroot_sphinx_2023_08_25_dev",
        "source_version_id": "pandaroot_sphinx_2023_08_25_dev@2023-08-25-dev",
        "text": "Installation and container setup for PandaRoot.",
        "locator": {
            "url": "https://example.invalid/install.html",
            "snapshot_date": "2023-08-25",
            "section_path": ["Installation"],
            "path": None,
            "start_line": None,
            "end_line": None,
        },
        "retrieval_channels": ["dense"],
        "score": 1.0,
        "authority_level": "operational",
    }


def bundle_for(
    evidence,
    *,
    intent="usage",
    required_source_types=None,
    symbols=None,
    concepts=None,
    concept_scopes=None,
    conflicts=None,
):
    if isinstance(evidence, dict):
        evidence = [evidence]
    return {
        "plan": {
            "intent": intent,
            "required_source_types": required_source_types or ["code"],
            "symbols": symbols or [],
            "concepts": concepts or [],
            "concept_scopes": concept_scopes or {},
            "resolved_versions": {
                "pandaroot": "18c09e91100db27867ded30e708b4dae95bd8357"
            },
            "target_repositories": ["pandaroot"],
            "version_conflicts": conflicts or [],
        },
        "evidence": evidence,
    }


class FakeVertex:
    """A deterministic model double that follows the production claim schema."""

    def generate_json(self, prompt, schema, **kwargs):
        if "supported" in schema.get("properties", {}):
            return {
                "supported": True,
                "unsupported_claim_ids": [],
                "irrelevant_claim_ids": [],
                "missing_requirement_ids": [],
                "reason": "",
            }
        return {
            "claims": [
                {
                    "claim_id": "c1",
                    "claim_text": "PndPidCorrelator is present.",
                    "evidence_ids": ["e1"],
                    "answer_point_ids": ["question_core"],
                }
            ]
        }


class ObservedVertex(FakeVertex):
    def __init__(self):
        self.stats = {
            "model_calls": 0,
            "token_usage": 0,
            "generation_calls": 0,
            "embedding_calls": 0,
        }

    def generate_json(self, prompt, schema, **kwargs):
        self.stats["model_calls"] += 1
        self.stats["generation_calls"] += 1
        self.stats["token_usage"] += 7
        return super().generate_json(prompt, schema, **kwargs)

    def stats_snapshot(self):
        return dict(self.stats)


class InstallationVertex(FakeVertex):
    def generate_json(self, prompt, schema, **kwargs):
        if "supported" in schema.get("properties", {}):
            return super().generate_json(prompt, schema, **kwargs)
        return {
            "claims": [
                {
                    "claim_id": "install",
                    "claim_text": "Install PandaRoot with CMake.",
                    "evidence_ids": ["e2"],
                    "answer_point_ids": ["question_core"],
                }
            ]
        }


class IrrelevantClaimVertex(FakeVertex):
    def generate_json(self, prompt, schema, **kwargs):
        if "supported" in schema.get("properties", {}):
            return {
                "supported": True,
                "unsupported_claim_ids": [],
                "irrelevant_claim_ids": ["noise"],
                "reason": "noise is factual but does not answer the question",
            }
        return {
            "claims": [
                {
                    "claim_id": "answer",
                    "claim_text": "PndPidCorrelator is present.",
                    "evidence_ids": ["e1"],
                    "answer_point_ids": ["question_core"],
                },
                {
                    "claim_id": "noise",
                    "claim_text": "An unrelated helper is also present.",
                    "evidence_ids": ["e1"],
                    "answer_point_ids": ["question_core"],
                },
            ]
        }


class PartialRevisionVertex:
    def generate_json(self, prompt, schema, **kwargs):
        if "supported" in schema.get("properties", {}):
            claims = json.loads(prompt)["untrusted_claims"]
            if any(item["claim_id"] == "c2" for item in claims):
                return {
                    "supported": False,
                    "unsupported_claim_ids": ["c2"],
                    "irrelevant_claim_ids": [],
                    "reason": "c2 is unsupported",
                }
            return {
                "supported": True,
                "unsupported_claim_ids": [],
                "irrelevant_claim_ids": [],
                "reason": "",
            }
        task = json.loads(prompt)["task"]
        if task == "revise_unsupported_claims_once":
            return {"claims": []}
        return {
            "claims": [
                {
                    "claim_id": "c1",
                    "claim_text": "The class is present.",
                    "evidence_ids": ["e1"],
                    "answer_point_ids": ["question_core"],
                },
                {
                    "claim_id": "c2",
                    "claim_text": "It performs an unrelated action.",
                    "evidence_ids": ["e1"],
                    "answer_point_ids": ["question_core"],
                },
            ]
        }


class CapturingVertex(FakeVertex):
    def __init__(self):
        self.prompts = []

    def generate_json(self, prompt, schema, **kwargs):
        self.prompts.append(json.loads(prompt))
        return super().generate_json(prompt, schema, **kwargs)


class MissingRequirementVertex(FakeVertex):
    """Model double for the one bounded completeness-revision path."""

    def __init__(self):
        self.review_calls = 0
        self.prompts = []

    def generate_json(self, prompt, schema, **kwargs):
        payload = json.loads(prompt)
        self.prompts.append(payload)
        if "supported" in schema.get("properties", {}):
            self.review_calls += 1
            if self.review_calls == 1:
                return {
                    "supported": False,
                    "unsupported_claim_ids": [],
                    "irrelevant_claim_ids": [],
                    "missing_requirement_ids": ["factory_composition"],
                    "reason": "factory chain is incomplete",
                }
            return {
                "supported": True,
                "unsupported_claim_ids": [],
                "irrelevant_claim_ids": [],
                "missing_requirement_ids": [],
                "reason": "",
            }
        if payload["task"] == "revise_unsupported_claims_once":
            return {
                "claims": [{
                "claim_id": "factory_chain",
                    "claim_text": "PndLmdModelFactory::setAcceptance stores PndLmdAcceptance before generate2DModel constructs the model and applies it as a multiplicative acceptance factor.",
                    "evidence_ids": ["e1"],
                    "answer_point_ids": ["question_core"],
                }]
            }
        return {
            "claims": [{
                "claim_id": "base",
                "claim_text": "PndLmdModelFactory has an acceptance configuration.",
                "evidence_ids": ["e1"],
                "answer_point_ids": ["question_core"],
            }]
        }


class ExternalIdentifierVertex(FakeVertex):
    def generate_json(self, prompt, schema, **kwargs):
        if "supported" in schema.get("properties", {}):
            return super().generate_json(prompt, schema, **kwargs)
        return {
            "claims": [{
                "claim_id": "composition",
                "claim_text": "PndLmdModelFactory uses boost::property_tree::ptree while constructing the fit model.",
                "evidence_ids": ["e1"],
                "answer_point_ids": ["question_core"],
            }]
        }


class QATests(unittest.TestCase):
    # Realistic locked-catalog fixture: the production premise guard consults
    # the locked-corpus catalog for bare locator questions, so full-path tests
    # must run against a catalog that actually contains the requested class.
    PID_CATALOG_ROWS = [
        ({"symbol": "PndPidCorrelator", "path": "pid/PndPidCorrelator.h"}, "class PndPidCorrelator {};")
    ]

    def test_run_detailed_reports_per_request_workflow_and_model_usage(self):
        bundle = bundle_for(code_evidence())
        detailed = QAAgent(
            Path.cwd(),
            retriever=FakeRetriever(bundle, storage=CatalogStorage(self.PID_CATALOG_ROWS)),
            vertex=ObservedVertex(),
        ).run_detailed(
            "Where is PndPidCorrelator?"
        )

        self.assertGreaterEqual(detailed["node_timings_ms"]["workflow"], 0)
        self.assertTrue(
            {"retrieve", "sufficiency", "answer", "verify", "finalize"}.issubset(
                detailed["node_timings_ms"]
            )
        )
        self.assertGreater(detailed["model_usage"]["model_calls"], 0)
        self.assertEqual(
            detailed["model_usage"]["model_calls"],
            detailed["model_usage"]["generation_calls"],
        )
        self.assertEqual(detailed["model_usage"]["embedding_calls"], 0)
        self.assertGreater(detailed["model_usage"]["token_usage"], 0)

    def _guard_agent(self, bundle):
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        # Guard tests concern only request answerability, not the separately
        # tested on-disk locked-symbol catalog.
        agent._locked_identifier_symbols = {"symbols": set(), "paths": set()}
        return agent

    def test_locked_symbol_catalog_uses_cached_read_only_database_when_normalized_file_is_absent(self):
        storage = CatalogStorage([
            ({"symbol": "PndDbCatalog", "path": "pid\\PndDbCatalog.h"}, "class PndTextCatalog {};"),
            ({"path": "macro/catalog.C"}, "struct CatalogRecord {}; enum CatalogMode { kDefault };"),
        ])
        retriever = FakeRetriever(bundle_for(code_evidence()))
        retriever.storage = storage
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            self.assertFalse((project_root / "data" / "normalized" / "knowledge_objects.jsonl").exists())
            agent = QAAgent(project_root, retriever=retriever, vertex=FakeVertex())
            catalog = agent._locked_symbols()
            self.assertEqual(catalog["symbols"], {"PndDbCatalog", "PndTextCatalog", "CatalogRecord", "CatalogMode"})
            self.assertEqual(catalog["paths"], {"pid/PndDbCatalog.h", "macro/catalog.C"})
            self.assertIs(catalog, agent._locked_symbols())

        self.assertEqual(storage.connect_calls, 1)
        self.assertEqual(len(storage.connection.queries), 1)
        query, params = storage.connection.queries[0]
        self.assertIsNone(params)
        self.assertTrue(query.lstrip().upper().startswith("SELECT"))
        self.assertNotRegex(query.upper(), r"\b(?:INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b")

    def test_locked_symbol_catalog_fails_closed_when_database_is_unavailable(self):
        retriever = FakeRetriever(bundle_for(code_evidence()), storage=NoStorage())
        with tempfile.TemporaryDirectory() as directory:
            agent = QAAgent(Path(directory), retriever=retriever, vertex=FakeVertex())
            with self.assertRaisesRegex(RuntimeError, "locked identifier catalog database is unavailable"):
                agent._locked_symbols()

    def test_exact_future_runtime_guard_refuses_english_and_chinese(self):
        bundle = bundle_for(code_evidence())
        agent = self._guard_agent(bundle)
        for question in (
            "What exact checksum will the output file have after the next runtime execution?",
            "下次运行后输出文件的精确校验和是多少？",
        ):
            errors = agent._answerability_guard({"question": question, "bundle": bundle})
            self.assertEqual(
                errors,
                ["exact future runtime outcome or checksum cannot be established before execution"],
            )

    def test_future_planning_and_locked_file_checksum_are_not_over_refused(self):
        bundle = bundle_for(code_evidence())
        agent = self._guard_agent(bundle)
        self.assertEqual(
            agent._answerability_guard({
                "question": "How should I plan the next runtime test?",
                "bundle": bundle,
            }),
            [],
        )
        self.assertEqual(
            agent._answerability_guard({
                "question": "What is the SHA-256 checksum of the already locked source file?",
                "bundle": bundle,
            }),
            [],
        )

    def test_open_domain_universal_proof_guard_and_formal_proof_control(self):
        bundle = bundle_for(code_evidence())
        agent = self._guard_agent(bundle)
        for question in (
            "Prove that this algorithm works for every possible input.",
            "证明该算法对所有可能输入都成立。",
        ):
            errors = agent._answerability_guard({"question": question, "bundle": bundle})
            self.assertEqual(
                errors,
                ["open-domain universal proof is unsupported without explicit same-domain theorem/proof evidence"],
            )
        formal_bundle = bundle_for(
            code_evidence(
                text="Theorem (PndProofDomain): for all PndProofDomain inputs the invariant holds. Proof: induction.",
                path="docs/PndProofDomain.md",
            )
        )
        self.assertEqual(
            self._guard_agent(formal_bundle)._answerability_guard({
                "question": "Prove the invariant for every PndProofDomain input.",
                "bundle": formal_bundle,
            }),
            [],
        )

    def test_answer_requirements_are_specific_to_question_and_plan(self):
        ids = lambda question, plan: [item["id"] for item in _answer_requirements(question, plan)]
        self.assertEqual(
            ids("Explain the workflow sequence.", {"intent": "usage"}),
            ["workflow_order"],
        )
        self.assertEqual(
            ids("Explain the data flow handoff through the pipeline.", {"intent": "data_flow"}),
            ["workflow_order", "complete_dataflow_handoff"],
        )
        self.assertEqual(
            ids("Why must event IDs align before second-pass PID?", {"intent": "data_flow"}),
            ["complete_dataflow_handoff"],
        )
        self.assertEqual(
            ids("How does the factory use input setter values to construct the output?", {"intent": "usage"}),
            ["factory_composition"],
        )
        self.assertEqual(
            ids("Contrast the longitudinal Restgas profile with angular PndLmdAcceptance.", {"intent": "theory"}),
            ["longitudinal_vs_angular_acceptance"],
        )
        self.assertEqual(
            ids("Debug this failure and diagnose the schema mismatch.", {"intent": "usage"}),
            ["troubleshoot_upstream_to_downstream"],
        )
        self.assertEqual(ids("Where is PndPidCorrelator defined?", {"intent": "usage"}), [])

    def test_answer_requirements_use_live_plan_anchors_without_overreach(self):
        ids = lambda question, plan: [item["id"] for item in _answer_requirements(question, plan)]
        self.assertEqual(
            ids(
                "Explain this implementation.",
                {"intent": "algorithm_implementation", "symbols": ["PndLmdModelFactory::setAcceptance", "PndLmdModelFactory::generate2DModel"]},
            ),
            ["factory_composition", "acceptance_factory_application"],
        )
        self.assertEqual(
            ids(
                "How does point-like angular acceptance differ from restgas effective acceptance?",
                {
                    "intent": "algorithm_theory",
                    "symbols": ["PndLmdModelFactory::setAcceptance"],
                    "concepts": ["longitudinal_profile", "PndLmdAcceptance"],
                },
            ),
            ["longitudinal_vs_angular_acceptance"],
        )
        self.assertEqual(
            ids(
                "Map model/ vs data/ vs apps/ in LuminosityFit with PndLmdModelFactory and createLmdFitData.",
                {
                    "intent": "module_structure",
                    "symbols": ["PndLmdModelFactory::setAcceptance", "createLmdFitData"],
                    "concepts": ["acceptance"],
                },
            ),
            [],
        )
        self.assertEqual(
            ids(
                "Explain the correction.",
                {
                    "intent": "algorithm_implementation",
                    "concepts": ["PndLmdAcceptance"],
                    "concept_scopes": {"response_axis": "longitudinal_profile"},
                },
            ),
            ["longitudinal_vs_angular_acceptance"],
        )
        self.assertEqual(
            ids(
                "Why does this correction fail?",
                {
                    "intent": "troubleshooting",
                    "concepts": ["empty bins", "efficiency profile range"],
                },
            ),
            [
                "troubleshoot_upstream_to_downstream",
                "explicit_compatibility_check",
                "efficiency_empty_bin_diagnosis",
            ],
        )
        self.assertEqual(
            ids(
                "Trace the data flow.",
                {"intent": "data_flow", "required_source_types": ["workflow", "documentation"]},
            ),
            ["workflow_order", "complete_dataflow_handoff", "workflow_or_operational_grounding"],
        )
        self.assertEqual(
            ids(
                "Where is PndLmdDataReader defined?",
                {"intent": "api", "symbols": ["PndLmdDataReader"]},
            ),
            [],
        )

    def test_answer_and_revision_payloads_include_runtime_requirements(self):
        bundle = bundle_for(code_evidence(), intent="data_flow")
        vertex = CapturingVertex()
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=vertex)
        answered = agent._answer({"question": "Explain the data flow handoff.", "bundle": bundle})
        self.assertIn("answer_requirements", vertex.prompts[0])
        self.assertEqual(
            [item["id"] for item in vertex.prompts[0]["answer_requirements"]],
            ["workflow_order", "complete_dataflow_handoff"],
        )
        agent._revise({
            "question": "Explain the data flow handoff.",
            "bundle": bundle,
            "draft": answered["draft"],
            "supported_claims": [],
            "unsupported_claim_ids": ["c1"],
            "errors": ["unsupported claim c1"],
        })
        self.assertIn("answer_requirements", vertex.prompts[1])

    def test_evidence_review_reports_missing_requirement_and_single_revision_adds_only_it(self):
        evidence = code_evidence(
            text="PndLmdModelFactory::setAcceptance stores PndLmdAcceptance before PndLmdModelFactory::generate2DModel constructs the model and applies it as a multiplicative acceptance factor.",
            path="model/PndLmdModelFactory.cxx",
            object_type="method",
        )
        bundle = bundle_for(
            evidence,
            intent="algorithm_implementation",
            symbols=["PndLmdModelFactory::setAcceptance", "PndLmdModelFactory::generate2DModel"],
        )
        vertex = MissingRequirementVertex()
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=vertex)
        initial = agent._answer({"question": "Explain this implementation.", "bundle": bundle})
        first_review = agent._verify({"question": "Explain this implementation.", "bundle": bundle, **initial})
        self.assertEqual(
            first_review["missing_requirement_ids"],
            ["factory_composition", "acceptance_factory_application"],
        )
        review_payload = next(item for item in vertex.prompts if item["task"] == "review_claim_support_and_relevance")
        self.assertEqual(review_payload["answer_requirements"], initial["answer_requirements"])
        revised = agent._revise({
            "question": "Explain this implementation.",
            "bundle": bundle,
            **initial,
            **first_review,
        })
        revision_payload = next(item for item in vertex.prompts if item["task"] == "revise_unsupported_claims_once")
        self.assertEqual(
            revision_payload["missing_requirement_ids"],
            ["factory_composition", "acceptance_factory_application"],
        )
        self.assertIn("only evidence-backed, user-relevant", revision_payload["revision_scope"])
        second_review = agent._verify({
            "question": "Explain this implementation.",
            "bundle": bundle,
            **revised,
        })
        self.assertEqual(second_review["missing_requirement_ids"], [])
        self.assertEqual([claim["claim_id"] for claim in second_review["supported_claims"]], ["base", "factory_chain"])

    def test_deterministic_requirement_backstop_requests_factory_and_workflow_evidence(self):
        factory_evidence = code_evidence(
            text="PndLmdModelFactory::setAcceptance configures acceptance before PndLmdModelFactory::generate2DModel constructs the result.",
            path="model/PndLmdModelFactory.cxx",
            object_type="method",
        )
        factory_bundle = bundle_for(
            factory_evidence,
            intent="algorithm_implementation",
            symbols=["PndLmdModelFactory::setAcceptance", "PndLmdModelFactory::generate2DModel"],
        )
        factory_verified = QAAgent(Path.cwd(), retriever=FakeRetriever(factory_bundle), vertex=FakeVertex())._verify({
            "question": "Explain this implementation.",
            "bundle": factory_bundle,
            "draft": {"claims": [{
                "claim_id": "smearing_only",
                "claim_text": "The divergence map evaluates the smearing integral.",
                "evidence_ids": ["e1"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertEqual(
            factory_verified["missing_requirement_ids"],
            ["factory_composition", "acceptance_factory_application"],
        )

        workflow_evidence = code_evidence(
            evidence_id="workflow",
            text="The simulation workflow passes the generated event into the next transport stage.",
            path="macro/run_sim.C",
            object_type="workflow",
            channel="workflow",
        )
        code = code_evidence(
            evidence_id="code",
            text="PndTargetGenerator samples an interaction vertex.",
            path="pgenerators/Target/PndTargetGenerator.cxx",
            object_type="function",
        )
        workflow_bundle = bundle_for(
            [workflow_evidence, code],
            intent="data_flow",
            required_source_types=["workflow", "code"],
        )
        workflow_verified = QAAgent(Path.cwd(), retriever=FakeRetriever(workflow_bundle), vertex=FakeVertex())._verify({
            "question": "Trace the data flow.",
            "bundle": workflow_bundle,
            "draft": {"claims": [{
                "claim_id": "code_only",
                "claim_text": "PndTargetGenerator samples an interaction vertex.",
                "evidence_ids": ["code"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertEqual(workflow_verified["missing_requirement_ids"], ["workflow_or_operational_grounding"])
        self.assertEqual(
            workflow_verified["errors"],
            ["missing answer requirement workflow_or_operational_grounding"],
        )

    def test_factory_requirements_distinguish_divergence_composition_and_acceptance_application(self):
        ids = lambda question, plan: [item["id"] for item in _answer_requirements(question, plan)]
        divergence_plan = {
            "intent": "algorithm_implementation",
            "symbols": ["model/PndLmdDivergenceSmearingModel2D.cxx", "model/PndLmdModelFactory.cxx"],
            "concepts": ["beam divergence smearing"],
        }
        self.assertEqual(
            ids("Explain this implementation.", divergence_plan),
            ["factory_composition", "divergence_factory_composition"],
        )
        acceptance_plan = {
            "intent": "algorithm_implementation",
            "symbols": ["PndLmdAcceptance", "model/PndLmdModelFactory.cxx"],
            "concepts": ["acceptance data object to model factory boundary"],
        }
        self.assertEqual(
            ids("Explain this implementation.", acceptance_plan),
            ["factory_composition", "acceptance_factory_application"],
        )

        divergence = code_evidence(
            evidence_id="divergence",
            text="PndLmdDivergenceSmearingModel2D computes the smearing contribution.",
            path="model/PndLmdDivergenceSmearingModel2D.cxx",
        )
        factory = code_evidence(
            evidence_id="factory",
            text="PndLmdModelFactory::generate2DModel composes PndLmdDivergenceSmearingModel2D into the resulting fit model.",
            path="model/PndLmdModelFactory.cxx",
            object_type="method",
        )
        divergence_bundle = bundle_for(
            [divergence, factory],
            intent="algorithm_implementation",
            symbols=divergence_plan["symbols"],
            concepts=divergence_plan["concepts"],
        )
        divergence_verified = QAAgent(Path.cwd(), retriever=FakeRetriever(divergence_bundle), vertex=FakeVertex())._verify({
            "question": "Explain this implementation.",
            "bundle": divergence_bundle,
            "draft": {"claims": [{
                "claim_id": "internal_map_only",
                "claim_text": "PndLmdDivergenceSmearingModel2D computes a smearing map.",
                "evidence_ids": ["divergence"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertEqual(
            divergence_verified["missing_requirement_ids"],
            ["factory_composition", "divergence_factory_composition"],
        )
        self.assertIn(
            "factory",
            divergence_verified["errors"][1],
        )

        acceptance = code_evidence(
            evidence_id="acceptance",
            text="PndLmdModelFactory::setAcceptance stores PndLmdAcceptance for later model construction.",
            path="model/PndLmdModelFactory.h",
        )
        acceptance_factory = code_evidence(
            evidence_id="acceptance-factory",
            text="PndLmdModelFactory::generate2DModel applies the stored PndLmdAcceptance as a multiplicative factor in the constructed model.",
            path="model/PndLmdModelFactory.cxx",
            object_type="method",
        )
        acceptance_bundle = bundle_for(
            [acceptance, acceptance_factory],
            intent="algorithm_implementation",
            symbols=acceptance_plan["symbols"],
            concepts=acceptance_plan["concepts"],
        )
        acceptance_verified = QAAgent(Path.cwd(), retriever=FakeRetriever(acceptance_bundle), vertex=FakeVertex())._verify({
            "question": "Explain this implementation.",
            "bundle": acceptance_bundle,
            "draft": {"claims": [{
                "claim_id": "setter_only",
                "claim_text": "PndLmdModelFactory::setAcceptance stores PndLmdAcceptance.",
                "evidence_ids": ["acceptance"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertEqual(
            acceptance_verified["missing_requirement_ids"],
            ["factory_composition", "acceptance_factory_application"],
        )

    def test_factory_specific_requirements_do_not_leak_to_unrelated_plans(self):
        ids = lambda question, plan: [item["id"] for item in _answer_requirements(question, plan)]
        self.assertEqual(
            ids(
                "Explain the internal smearing map.",
                {"intent": "algorithm_implementation", "symbols": ["model/PndLmdDivergenceSmearingModel2D.cxx"], "concepts": ["smearing"]},
            ),
            [],
        )
        self.assertEqual(
            ids(
                "Explain the model factory.",
                {"intent": "algorithm_implementation", "symbols": ["model/PndLmdModelFactory.cxx"], "concepts": ["fit model"]},
            ),
            ["factory_composition"],
        )

    def test_topic_completeness_requirements_are_narrow_and_do_not_leak(self):
        ids = lambda question, plan: [item["id"] for item in _answer_requirements(question, plan)]
        self.assertEqual(
            ids(
                "How does the elastic differential cross section fit the measured distribution to extract luminosity?",
                {"intent": "theory", "concepts": ["elastic differential cross section", "luminosity fit"]},
            ),
            ["elastic_cross_section_luminosity_fit"],
        )
        self.assertEqual(
            ids(
                "What does the DPM elastic model represent?",
                {"intent": "theory", "concepts": ["DPM elastic model"]},
            ),
            ["elastic_cross_section_luminosity_fit"],
        )
        self.assertEqual(
            ids(
                "What does this elastic model represent?",
                {"intent": "theory", "concepts": ["DPM elastic model"]},
            ),
            ["elastic_cross_section_luminosity_fit"],
        )
        self.assertEqual(
            ids(
                "Explain the PndLmdDataReader selection and accepted/generated histograms.",
                {"intent": "algorithm_implementation", "symbols": ["PndLmdDataReader"]},
            ),
            ["reader_selection_histogram_accounting"],
        )
        self.assertEqual(
            ids(
                "Why do empty bins appear in this efficiency profile?",
                {"intent": "troubleshooting", "concepts": ["empty bins", "efficiency profile"]},
            ),
            [
                "troubleshoot_upstream_to_downstream",
                "explicit_compatibility_check",
                "efficiency_empty_bin_diagnosis",
            ],
        )
        self.assertNotIn(
            "efficiency_empty_bin_diagnosis",
            ids(
                "createLmdFitData returns no acceptance: which data mode, input/tree assumptions, selection filters, and accepted/generated histogram filling should I inspect?",
                {
                    "intent": "troubleshooting",
                    "symbols": ["PndLmdDataReader", "createLmdFitData"],
                    "concepts": ["empty bins", "efficiency profile"],
                },
            ),
        )
        self.assertEqual(
            ids("Where is PndLmdDataReader defined?", {"intent": "api", "symbols": ["PndLmdDataReader"]}),
            [],
        )
        self.assertEqual(
            ids("Explain an elastic scattering measurement.", {"intent": "theory", "concepts": ["elastic scattering"]}),
            [],
        )
        self.assertEqual(
            ids("What does this elastic model represent?", {"intent": "theory", "concepts": ["elastic model"]}),
            [],
        )
        self.assertEqual(
            ids("What does this DPM model represent?", {"intent": "theory", "concepts": ["DPM model"]}),
            [],
        )

    def test_regression_protected_requirements_are_narrow_and_explicit(self):
        ids = lambda question, plan: [item["id"] for item in _answer_requirements(question, plan)]
        pointer_plan = {
            "intent": "api",
            "symbols": ["PndLmdTrackQ", "PndLmdCombinedDataReader"],
            "concepts": ["pointer type normalization"],
        }
        self.assertEqual(
            ids(
                "PndLmdTrackQ* appears in adapter code. How should this pointer type be normalized?",
                pointer_plan,
            ),
            ["pointer_identifier_normalization"],
        )
        inventory_plan = {
            "intent": "module_structure",
            "symbols": ["PndLmdModelFactory"],
            "concepts": [
                "model layer", "DPM physics model", "divergence smearing",
                "detector resolution", "model factory",
            ],
        }
        inventory_ids = ids("Which components form the model layer?", inventory_plan)
        self.assertIn("model_layer_component_inventory", inventory_ids)
        self.assertNotIn("pointer_identifier_normalization", inventory_ids)
        self.assertNotIn("implementation_disambiguation_procedure", inventory_ids)
        disambiguation_plan = {
            "intent": "troubleshooting",
            "concepts": [
                "class name matching", "code retrieval", "implementation ambiguity",
                "detector-scoped disambiguation",
            ],
        }
        self.assertEqual(
            ids(
                "Why can a class name match the query but still be the wrong implementation?",
                disambiguation_plan,
            ),
            ["implementation_disambiguation_procedure"],
        )
        self.assertEqual(
            ids("Where is PndLmdTrackQ defined?", {"intent": "api", "symbols": ["PndLmdTrackQ"]}),
            [],
        )

    def test_regression_protected_requirements_reject_incomplete_claims(self):
        pointer_requirement = [{
            "id": "pointer_identifier_normalization",
            "instruction": "",
            "target_symbol": "PndLmdTrackQ",
        }]
        old_pointer_claim = [{
            "claim_id": "c1",
            "claim_text": "PndLmdCombinedDataReader casts an entry to PndLmdTrackQ* and consumes it.",
            "evidence_ids": [],
        }]
        self.assertEqual(
            _deterministic_missing_requirement_ids(pointer_requirement, old_pointer_claim, {}),
            ["pointer_identifier_normalization"],
        )
        fixed_pointer_claim = [{
            "claim_id": "c1",
            "claim_text": "The pointer type expression PndLmdTrackQ* normalizes to the underlying PndLmdTrackQ symbol; the asterisk is pointer syntax and is not part of a new identifier.",
            "evidence_ids": [],
        }]
        self.assertEqual(
            _deterministic_missing_requirement_ids(pointer_requirement, fixed_pointer_claim, {}),
            [],
        )

        inventory_requirement = [{"id": "model_layer_component_inventory", "instruction": ""}]
        old_inventory_claim = [{
            "claim_id": "c1",
            "claim_text": "The DPM physics model and resolution smearing are assembled by PndLmdModelFactory.",
            "evidence_ids": [],
        }]
        self.assertEqual(
            _deterministic_missing_requirement_ids(inventory_requirement, old_inventory_claim, {}),
            ["model_layer_component_inventory"],
        )

        disambiguation_requirement = [{"id": "implementation_disambiguation_procedure", "instruction": ""}]
        old_disambiguation_claim = [{
            "claim_id": "c1",
            "claim_text": "The same class name can have a different implementation in another repository path.",
            "evidence_ids": [],
        }]
        self.assertEqual(
            _deterministic_missing_requirement_ids(
                disambiguation_requirement, old_disambiguation_claim, {}
            ),
            ["implementation_disambiguation_procedure"],
        )
        fixed_disambiguation_claim = [{
            "claim_id": "c1",
            "claim_text": "A name match is insufficient: check the repository source and full path, then inspect the implementation, callers or configuration sites, and consumed or produced data products before accepting it.",
            "evidence_ids": [],
        }]
        self.assertEqual(
            _deterministic_missing_requirement_ids(
                disambiguation_requirement, fixed_disambiguation_claim, {}
            ),
            [],
        )

    def test_topic_completeness_requires_all_answer_elements_and_final_citations(self):
        dpm_theory = code_evidence(
            evidence_id="theory",
            text="The elastic differential cross section is the theory input for the luminosity fit.",
            path="macro/target/ana_dpm.C",
        )
        dpm_fit = code_evidence(
            evidence_id="fit",
            text="The fit compares the measured distribution with that differential cross section to extract luminosity.",
            path="macro/target/ana_dpm.C",
        )
        dpm_bundle = bundle_for(
            [dpm_theory, dpm_fit],
            intent="theory",
            concepts=["elastic differential cross section", "luminosity fit"],
        )
        dpm_agent = QAAgent(Path.cwd(), retriever=FakeRetriever(dpm_bundle), vertex=FakeVertex())
        incomplete_dpm = dpm_agent._verify({
            "question": "How does the elastic differential cross section fit the measured distribution to extract luminosity?",
            "bundle": dpm_bundle,
            "draft": {"claims": [{
                "claim_id": "theory_only",
                "claim_text": "The elastic differential cross section is the theory input for luminosity.",
                "evidence_ids": ["theory"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertEqual(incomplete_dpm["missing_requirement_ids"], ["elastic_cross_section_luminosity_fit"])
        complete_dpm = dpm_agent._verify({
            "question": "How does the elastic differential cross section fit the measured distribution to extract luminosity?",
            "bundle": dpm_bundle,
            "draft": {"claims": [{
                "claim_id": "theory_to_fit",
                "claim_text": "The elastic differential cross section is the theory input; fitting the measured distribution with that model extracts luminosity.",
                "evidence_ids": ["theory", "fit"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertEqual(complete_dpm["missing_requirement_ids"], [])

        reader = code_evidence(
            evidence_id="reader",
            text="PndLmdDataReader applies the event selection filter and fills accepted and generated histograms.",
            path="data/PndLmdDataReader.cxx",
        )
        reader_bundle = bundle_for(reader, intent="algorithm_implementation", symbols=["PndLmdDataReader"])
        reader_verified = QAAgent(Path.cwd(), retriever=FakeRetriever(reader_bundle), vertex=FakeVertex())._verify({
            "question": "Explain the PndLmdDataReader selection and accepted/generated histograms.",
            "bundle": reader_bundle,
            "draft": {"claims": [{
                "claim_id": "reader_accounting",
                "claim_text": "PndLmdDataReader applies the selection filter and fills accepted and generated histograms.",
                "evidence_ids": ["reader"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertEqual(reader_verified["missing_requirement_ids"], [])

        acceptance = code_evidence(
            evidence_id="acceptance",
            text="PndLmdModelFactory::setAcceptance stores the internal PndLmdAcceptance member; generate2DModel constructs the model and applies it as a multiplicative factor.",
            path="model/PndLmdModelFactory.cxx",
        )
        acceptance_bundle = bundle_for(
            acceptance,
            intent="algorithm_implementation",
            symbols=["PndLmdAcceptance", "PndLmdModelFactory::setAcceptance", "PndLmdModelFactory::generate2DModel"],
        )
        acceptance_verified = QAAgent(Path.cwd(), retriever=FakeRetriever(acceptance_bundle), vertex=FakeVertex())._verify({
            "question": "Explain this implementation.",
            "bundle": acceptance_bundle,
            "draft": {"claims": [{
                "claim_id": "acceptance_handoff",
                "claim_text": "PndLmdModelFactory::setAcceptance stores the internal PndLmdAcceptance member; the factory's generate2DModel constructs the model and applies that acceptance as a multiplicative factor.",
                "evidence_ids": ["acceptance"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertNotIn("acceptance_factory_application", acceptance_verified["missing_requirement_ids"])

        efficiency = code_evidence(
            evidence_id="efficiency",
            text="A numerator-empty bin can result from reconstructed selection or migration; denominator-zero efficiency is handled separately, and binning must be compatible with the profile range.",
            path="macro/target/correction/efficiency_correction_2.C",
        )
        efficiency_bundle = bundle_for(
            efficiency,
            intent="troubleshooting",
            concepts=["empty bins", "efficiency profile"],
        )
        efficiency_agent = QAAgent(Path.cwd(), retriever=FakeRetriever(efficiency_bundle), vertex=FakeVertex())
        incomplete_efficiency = efficiency_agent._verify({
            "question": "Why do empty bins appear in this efficiency profile?",
            "bundle": efficiency_bundle,
            "draft": {"claims": [{
                "claim_id": "denominator_only",
                "claim_text": "A denominator-zero efficiency bin needs explicit handling.",
                "evidence_ids": ["efficiency"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertIn("efficiency_empty_bin_diagnosis", incomplete_efficiency["missing_requirement_ids"])
        complete_efficiency = efficiency_agent._verify({
            "question": "Why do empty bins appear in this efficiency profile?",
            "bundle": efficiency_bundle,
            "draft": {"claims": [{
                "claim_id": "complete_efficiency_diagnosis",
                "claim_text": "A numerator-empty bin can arise from reconstructed selection or migration; handle denominator-zero efficiency and verify binning/profile compatibility.",
                "evidence_ids": ["efficiency"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertNotIn("efficiency_empty_bin_diagnosis", complete_efficiency["missing_requirement_ids"])
        finalized = efficiency_agent._finalize({
            "bundle": efficiency_bundle,
            "sufficient": True,
            "supported_claims": complete_efficiency["supported_claims"],
            "errors": [],
        })["result"]
        self.assertEqual([item["evidence_id"] for item in finalized["evidence"]], ["efficiency"])
        self.assertNotIn("answer_point_ids", finalized["claims"][0])

    def test_unrequested_external_identifier_is_sanitized_before_verification(self):
        evidence = code_evidence(
            text="PndLmdModelFactory uses boost::property_tree::ptree while constructing the fit model.",
            path="model/PndLmdModelFactory.cxx",
            object_type="method",
        )
        bundle = bundle_for(evidence, intent="algorithm_implementation", symbols=["PndLmdModelFactory"])
        draft = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=ExternalIdentifierVertex())._answer({
            "question": "How does PndLmdModelFactory construct the fit model?",
            "bundle": bundle,
        })["draft"]
        self.assertNotIn("boost::property_tree::ptree", draft["claims"][0]["claim_text"])
        self.assertIn("internal support type", draft["claims"][0]["claim_text"])

    def test_refusal_basis_prefers_exact_producer_and_query_specific_validation(self):
        generic_doc = code_evidence(
            evidence_id="doc",
            text="README describes an output artifact.",
            path="README.md",
            object_type="documentation",
            channel="dense",
        )
        producer = code_evidence(
            evidence_id="producer",
            text="runLmdFit.sh produces the requested output artifact after the workflow runs.",
            path="python/runLmdFit.sh",
            object_type="shell_script",
            channel="exact",
        )
        runtime_bundle = bundle_for(
            [generic_doc, producer],
            symbols=["python/runLmdFit.sh"],
        )
        runtime_result = self._guard_agent(runtime_bundle)._finalize({
            "question": "What exact checksum will the output have after the next runtime execution?",
            "bundle": runtime_bundle,
            "sufficient": False,
            "errors": ["exact future runtime outcome or checksum cannot be established before execution"],
        })["result"]
        self.assertEqual(runtime_result["claims"][0]["evidence_ids"], ["producer"])

        generic_paper = code_evidence(
            evidence_id="paper-generic",
            source_id="li_2026",
            text="The study reports finite simulated cases.",
            path="papers/thesis.pdf",
            object_type="paper",
        )
        specific_paper = code_evidence(
            evidence_id="paper-specific",
            source_id="li_2026",
            text="The RestgasProfile iteration convergence validation reports a contracting reconstruction workflow rather than a universal proof.",
            path="papers/thesis.pdf",
            object_type="paper",
        )
        theory_bundle = bundle_for(
            [generic_paper, specific_paper],
            intent="algorithm_theory",
            concepts=["RestgasProfile iteration"],
            required_source_types=["paper"],
        )
        theory_result = self._guard_agent(theory_bundle)._finalize({
            "question": "Prove that every RestgasProfile iteration converges.",
            "bundle": theory_bundle,
            "sufficient": False,
            "errors": ["open-domain universal proof is unsupported without explicit same-domain theorem/proof evidence"],
        })["result"]
        self.assertEqual(theory_result["claims"][0]["evidence_ids"], ["paper-specific"])

    def test_new_guard_refusals_remain_insufficient_and_bilingual_safe(self):
        bundle = bundle_for(code_evidence())
        agent = self._guard_agent(bundle)
        for error, phrase in (
            ("exact future runtime outcome or checksum cannot be established before execution", "无法在执行前验证"),
            ("open-domain universal proof is unsupported without explicit same-domain theorem/proof evidence", "明确形式定理或证明"),
        ):
            result = agent._finalize({
                "question": "请解释这个请求",
                "bundle": bundle,
                "sufficient": False,
                "supported_claims": [
                    {"claim_id": "partial", "claim_text": "Ignored because status must not promote.", "evidence_ids": ["e1"]}
                ],
                "errors": [error],
            })["result"]
            self.assertEqual(result["status"], QAStatus.INSUFFICIENT_EVIDENCE.value)
            self.assertIn(phrase, result["answer"])

    def test_future_runtime_refusal_keeps_relevant_cited_code_basis(self):
        evidence = code_evidence(
            text="ana_dpm.C writes the event_poca output tree during the analysis workflow.",
            path="macro/target/ana_dpm.C",
            object_type="workflow",
            channel="workflow",
        )
        bundle = bundle_for(evidence, intent="data_flow", symbols=["macro/target/ana_dpm.C"])
        agent = self._guard_agent(bundle)
        question = "What exact checksum will the event_poca output have after the next runtime execution?"
        result = agent._finalize({
            "question": question,
            "bundle": bundle,
            "sufficient": False,
            "errors": ["exact future runtime outcome or checksum cannot be established before execution"],
        })["result"]
        self.assertEqual(result["status"], QAStatus.INSUFFICIENT_EVIDENCE.value)
        self.assertEqual([claim["claim_id"] for claim in result["claims"]], ["future_runtime_refusal_basis"])
        self.assertEqual(result["claims"][0]["evidence_ids"], ["e1"])
        self.assertEqual([item["evidence_id"] for item in result["evidence"]], ["e1"])
        self.assertIn("event_poca", result["claims"][0]["claim_text"])
        self.assertIn("producer/workflow", result["claims"][0]["claim_text"])
        for marker in ("scope_", "required_", "curated_panda_domain", "dataflow_locator_"):
            self.assertNotIn(marker, result["answer"])
        verified = agent._verify({
            "question": question,
            "bundle": bundle,
            "draft": {"claims": [{
                **result["claims"][0],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertEqual([claim["claim_id"] for claim in verified["supported_claims"]], ["future_runtime_refusal_basis"])

    def test_universal_proof_refusal_keeps_relevant_cited_theory_basis(self):
        evidence = code_evidence(
            evidence_id="paper1",
            source_id="li_2026",
            text="The PndProofDomain study evaluates finite simulated cases and validates their observed behavior.",
            path="papers/PndProofDomain.pdf",
            object_type="paper",
        )
        evidence["locator"]["pdf_page"] = 4
        bundle = bundle_for(evidence, intent="theory", required_source_types=["paper"])
        agent = self._guard_agent(bundle)
        question = "Prove the behavior for every PndProofDomain case."
        result = agent._finalize({
            "question": question,
            "bundle": bundle,
            "sufficient": False,
            "errors": ["open-domain universal proof is unsupported without explicit same-domain theorem/proof evidence"],
        })["result"]
        self.assertEqual(result["status"], QAStatus.INSUFFICIENT_EVIDENCE.value)
        self.assertEqual([claim["claim_id"] for claim in result["claims"]], ["universal_proof_refusal_basis"])
        self.assertEqual(result["claims"][0]["evidence_ids"], ["paper1"])
        self.assertEqual([item["evidence_id"] for item in result["evidence"]], ["paper1"])
        self.assertIn("finite or evaluated", result["claims"][0]["claim_text"])
        self.assertIn("PndProofDomain", result["claims"][0]["claim_text"])
        for marker in ("scope_", "required_", "curated_panda_domain", "dataflow_locator_"):
            self.assertNotIn(marker, result["answer"])
        verified = agent._verify({
            "question": question,
            "bundle": bundle,
            "draft": {"claims": [{
                **result["claims"][0],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertEqual([claim["claim_id"] for claim in verified["supported_claims"]], ["universal_proof_refusal_basis"])

    def test_prompt_set_marks_completeness_and_judge_strictness(self):
        from panda_agent.prompts import (
            ANSWER_SYSTEM_PROMPT,
            EVALUATION_JUDGE_SYSTEM_PROMPT,
            REVISION_SYSTEM_PROMPT,
        )

        self.assertEqual(PROMPT_SET_VERSION, "3.9.0")
        for prompt in (ANSWER_SYSTEM_PROMPT, REVISION_SYSTEM_PROMPT):
            self.assertIn("answer_requirements", prompt)
        self.assertIn("factory/composition", EVALUATION_JUDGE_SYSTEM_PROMPT)
        self.assertIn("upstream-first", EVALUATION_JUDGE_SYSTEM_PROMPT)

    def test_sufficiency_accepts_null_optional_path(self):
        evidence = code_evidence()
        evidence["locator"]["path"] = None
        bundle = bundle_for(evidence)
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        self.assertTrue(agent._sufficiency({"bundle": bundle})["sufficient"])

    def test_answered_path_is_bounded_and_cited(self):
        bundle = bundle_for(code_evidence())
        retriever = FakeRetriever(bundle, storage=CatalogStorage(self.PID_CATALOG_ROWS))
        result = QAAgent(Path.cwd(), retriever=retriever, vertex=FakeVertex()).run(
            "Where is PndPidCorrelator?"
        )
        self.assertEqual(result.status, QAStatus.ANSWERED)
        self.assertEqual(retriever.calls, 1)
        self.assertEqual(result.answer, "PndPidCorrelator is present. [e1]")
        self.assertEqual(result.claims[0].model_dump().keys(), {"claim_id", "claim_text", "evidence_ids"})

    def test_agent_core_run_has_no_service_import_or_database_persistence(self):
        storage = CatalogStorage(self.PID_CATALOG_ROWS)
        agent = QAAgent(
            Path.cwd(), retriever=FakeRetriever(bundle_for(code_evidence()), storage=storage), vertex=FakeVertex()
        )
        result = agent.run("Where is PndPidCorrelator?")

        self.assertEqual(result.status, QAStatus.ANSWERED)
        self.assertNotIn("panda_agent.service", inspect.getsource(QAAgent))
        self.assertTrue(storage.connection.queries)
        self.assertTrue(all(query.lstrip().upper().startswith("SELECT") for query, _ in storage.connection.queries))

    def test_version_conflict_refuses_without_generation(self):
        bundle = bundle_for(
            code_evidence(),
            conflicts=[
                "pandaroot: requested deadbeef, locked 18c09e91100db27867ded30e708b4dae95bd8357"
            ],
        )
        retriever = FakeRetriever(bundle)
        result = QAAgent(Path.cwd(), retriever=retriever, vertex=FakeVertex()).run(
            "Use PandaRoot deadbeef"
        )
        self.assertEqual(result.status, QAStatus.VERSION_CONFLICT)
        self.assertEqual(retriever.calls, 1)
        self.assertIn("deadbeef", result.answer)
        self.assertIn("locked corpus", result.answer)
        self.assertFalse(result.claims)
        self.assertNotIn("scope_", result.answer)

    def test_internal_claims_are_audited_but_not_rendered(self):
        web = web_evidence()
        code = code_evidence()
        bundle = bundle_for(
            [web, code],
            intent="installation",
            required_source_types=["documentation"],
        )
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=InstallationVertex())
        state = {
            "question": "Install the locked PandaRoot version",
            "bundle": bundle,
        }
        # Scope provenance is intentionally represented as an internal draft
        # claim.  Whether retrieval decides to add it is not part of this
        # filtering contract; once present it must never cross the DTO
        # boundary.
        draft = {
            "claims": [
                {
                    "claim_id": "install",
                    "claim_text": "Install PandaRoot with CMake.",
                    "evidence_ids": ["e2"],
                    "answer_point_ids": ["question_core"],
                },
                {
                    "claim_id": "scope_pandaroot",
                    "claim_text": "The answer is scoped to the locked PandaRoot version.",
                    "evidence_ids": ["e2", "e1"],
                    "answer_point_ids": [],
                },
            ]
        }
        self.assertIn("scope_pandaroot", {claim["claim_id"] for claim in draft["claims"]})
        verified = agent._verify({**state, "draft": draft})
        finalized = agent._finalize({**state, **verified, "draft": draft, "sufficient": True, "errors": []})
        result = finalized["result"]
        public_ids = {claim["claim_id"] for claim in result["claims"]}
        self.assertEqual(public_ids, {"install"})
        self.assertNotIn("scope_pandaroot", result["answer"])
        audit = {item["claim_id"]: item for item in finalized["claim_audit"]}
        self.assertIn("scope_pandaroot", audit)
        self.assertIn("internal_claim", audit["scope_pandaroot"]["filter_reason"])

    def test_all_internal_dataflow_claims_are_diagnostic_only(self):
        evidence = [
            code_evidence(
                evidence_id="e1",
                text="PndLmdAcceptance implementation",
                path="data/PndLmdAcceptance.cxx",
            ),
            code_evidence(
                evidence_id="e2",
                source_id="restgas_determination",
                object_type="workflow",
                text="Restgas profile flows into effective acceptance.",
                path="workflow/restgas_aware_luminosity_acceptance",
                channel="workflow",
            ),
        ]
        bundle = bundle_for(
            evidence,
            intent="data_flow",
            required_source_types=["code", "workflow"],
            symbols=["data/PndLmdAcceptance.cxx"],
        )
        state = {"question": "Explain the data flow", "bundle": bundle}
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        draft = {
            "claims": [
                {
                    "claim_id": "visible",
                    "claim_text": "PndLmdAcceptance is used in the flow.",
                    "evidence_ids": ["e1"],
                    "answer_point_ids": ["question_core"],
                }
            ]
        }
        augmented = agent._augment_required_dataflow_evidence(draft, state)
        augmented["claims"].append(
            {
                "claim_id": "dataflow_locator_manual",
                "claim_text": "The data-flow implementation includes a locator.",
                "evidence_ids": ["e1"],
            }
        )
        augmented["claims"].append(
            {
                "claim_id": "metadata_echo",
                "claim_text": "The workflow evidence identifies curated_panda_domain.",
                "evidence_ids": ["e2"],
                "answer_point_ids": ["question_core"],
            }
        )
        verified = agent._verify({**state, "draft": augmented})
        finalized = agent._finalize({
            **state,
            **verified,
            "draft": augmented,
            "sufficient": True,
            "errors": [],
        })
        result_ids = {claim["claim_id"] for claim in finalized["result"]["claims"]}
        self.assertEqual(result_ids, {"visible"})
        answer = finalized["result"]["answer"]
        for marker in ("required_workflow", "required_code", "dataflow_locator_", "curated_panda_domain"):
            self.assertNotIn(marker, answer)
        audit_ids = {item["claim_id"] for item in finalized["claim_audit"]}
        self.assertTrue({"required_workflow", "dataflow_locator_manual", "metadata_echo"}.issubset(audit_ids))
        self.assertTrue(all(item.get("filter_reason") for item in finalized["claim_audit"]))

    def test_answer_schema_requires_runtime_answer_point_mapping(self):
        claim_schema = ANSWER_SCHEMA["properties"]["claims"]["items"]
        self.assertIn("answer_point_ids", claim_schema["required"])
        self.assertEqual(claim_schema["properties"]["answer_point_ids"]["minItems"], 1)

    def test_missing_or_invalid_answer_point_mapping_is_not_rendered(self):
        bundle = bundle_for(code_evidence())
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        for mapping in (None, [], ["wrong_point"]):
            claim = {
                "claim_id": "bad",
                "claim_text": "PndPidCorrelator is present.",
                "evidence_ids": ["e1"],
            }
            if mapping is not None:
                claim["answer_point_ids"] = mapping
            state = {"question": "Where is PndPidCorrelator?", "bundle": bundle, "draft": {"claims": [claim]}}
            verified = agent._verify(state)
            self.assertEqual(verified["supported_claims"], [])
            finalized = agent._finalize({
                **state,
                **verified,
                "sufficient": True,
                "errors": verified["errors"],
            })
            self.assertEqual(finalized["result"]["claims"], [])
            self.assertNotIn("PndPidCorrelator is present", finalized["result"]["answer"])

    def test_irrelevant_review_claim_is_filtered(self):
        bundle = bundle_for(code_evidence())
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=IrrelevantClaimVertex())
        state = {
            "question": "Where is PndPidCorrelator?",
            "bundle": bundle,
            "draft": IrrelevantClaimVertex().generate_json("", {"properties": {}}),
        }
        verified = agent._verify(state)
        self.assertEqual([claim["claim_id"] for claim in verified["supported_claims"]], ["answer"])
        self.assertIn("irrelevant claim noise", verified["errors"])
        finalized = agent._finalize({
            **state,
            **verified,
            "sufficient": True,
            "errors": verified["errors"],
        })
        self.assertEqual([claim["claim_id"] for claim in finalized["result"]["claims"]], ["answer"])
        self.assertNotIn("unrelated helper", finalized["result"]["answer"])

    def test_refusal_paths_do_not_render_synthetic_fillers(self):
        bundle = bundle_for(code_evidence(), conflicts=["pandaroot: requested deadbeef"])
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        state = {
            "question": "Use deadbeef and include the required_workflow details",
            "bundle": bundle,
            "sufficient": False,
            "errors": ["version conflict"],
            "supported_claims": [],
            "claim_audit": [
                {"claim_id": "required_workflow", "filter_reason": "internal_claim_id:required_workflow"}
            ],
        }
        finalized = agent._finalize(state)
        result = finalized["result"]
        self.assertEqual(result["status"], QAStatus.VERSION_CONFLICT.value)
        self.assertFalse(result["claims"])
        self.assertNotIn("required_workflow", result["answer"])
        self.assertNotIn("curated_panda_domain", result["answer"])

    def test_nonexistent_api_guard_keeps_verified_alternative(self):
        bundle = bundle_for(code_evidence())
        state = {
            "question": "What is SetMagicRestgasSeed?",
            "bundle": bundle,
            "sufficient": False,
            "errors": ["unsupported requested API symbol: PndPidCorrelator::SetMagicRestgasSeed"],
            "supported_claims": [],
        }
        result = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())._finalize(state)["result"]
        self.assertEqual(result["status"], QAStatus.INSUFFICIENT_EVIDENCE.value)
        self.assertTrue(result["claims"])
        self.assertNotIn("required_code", result["answer"])

    def test_runtime_artifact_guard_keeps_schema_without_filler(self):
        evidence = code_evidence(text="event_poca tree is written by ana_dpm.C", path="macro/target/ana_dpm.C")
        bundle = bundle_for(evidence)
        state = {
            "question": "Recover the deleted event_poca records",
            "bundle": bundle,
            "sufficient": False,
            "errors": ["runtime artifact records cannot be reconstructed"],
            "supported_claims": [],
        }
        result = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())._finalize(state)["result"]
        self.assertEqual(result["status"], QAStatus.INSUFFICIENT_EVIDENCE.value)
        self.assertTrue(result["claims"])
        self.assertNotIn("curated_panda_domain", result["answer"])

    def test_revision_preserves_supported_claim_instead_of_total_refusal(self):
        bundle = bundle_for(code_evidence())
        result = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=PartialRevisionVertex()).run(
            "What is this class?"
        )
        self.assertEqual(result.status, QAStatus.ANSWERED)
        self.assertEqual([claim.claim_id for claim in result.claims], ["c1"])
        self.assertEqual([item.evidence_id for item in result.evidence], ["e1"])

    def test_locator_augmentation_requires_user_named_locator(self):
        bundle = bundle_for(
            code_evidence(text="ana_dpm.C", path="macro/target/ana_dpm.C"),
            symbols=["macro/target/ana_dpm.C"],
        )
        unchanged = QAAgent._augment_planned_locators(
            {"claims": []}, {"question": "Explain the POCA workflow", "bundle": bundle}
        )
        self.assertEqual(unchanged["claims"], [])
        changed = QAAgent._augment_planned_locators(
            {"claims": []}, {"question": "Where is ana_dpm.C implemented?", "bundle": bundle}
        )
        self.assertEqual(len(changed["claims"]), 1)
        self.assertEqual(changed["claims"][0]["answer_point_ids"], ["question_core"])

    def test_finalizer_never_adds_a_claim_after_verification(self):
        bundle = bundle_for(code_evidence())
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        draft = {
            "claims": [
                {
                    "claim_id": "c1",
                    "claim_text": "The class is present.",
                    "evidence_ids": ["e1"],
                    "answer_point_ids": ["question_core"],
                }
            ]
        }
        verified = agent._verify({"question": "Which locked version?", "bundle": bundle, "draft": draft})
        finalized = agent._finalize({
            "question": "Which locked version?",
            "bundle": bundle,
            "sufficient": True,
            "draft": draft,
            **verified,
        })
        self.assertEqual([item["claim_id"] for item in finalized["result"]["claims"]], ["c1"])




class ExternalTypeSanitizationTests(unittest.TestCase):
    def sanitize(self, text, question="Explain the data boundary.", symbols=None):
        from panda_agent.qa import _strip_nonessential_external_identifiers
        return _strip_nonessential_external_identifiers(
            [{"claim_text": text}], question, {"symbols": symbols or []}
        )[0]["claim_text"]

    def test_external_identifier_simple_template(self):
        self.assertEqual(self.sanitize("Uses std::vector<Foo>."),
                         "Uses an internal support type containing (Foo).")

    def test_external_identifier_domain_payload(self):
        self.assertEqual(self.sanitize("Uses std::vector<Lmd::Data::TrackPairInfo>."),
                         "Uses an internal support type containing (Lmd::Data::TrackPairInfo).")

    def test_external_identifier_unseen_payload(self):
        self.assertEqual(self.sanitize("Uses std::deque<WaveformPacket>."),
                         "Uses an internal support type containing (WaveformPacket).")

    def test_external_identifier_nested_template(self):
        self.assertEqual(self.sanitize("Uses std::vector<std::pair<Foo, Bar>>."),
                         "Uses an internal support type containing (an internal support type containing (Foo, Bar)).")

    def test_external_identifier_boost_template(self):
        self.assertEqual(self.sanitize("Uses boost::shared_ptr<SensorFrame>."),
                         "Uses an internal support type containing (SensorFrame).")

    def test_external_identifier_non_template(self):
        self.assertEqual(self.sanitize("Uses boost::property_tree::ptree and std::string."),
                         "Uses an internal support type and an internal support type.")

    def test_external_identifier_requested_question(self):
        text = "Uses std::vector<std::pair<Foo, Bar>>."
        self.assertEqual(self.sanitize(text, question="Explain std::vector."), text)

    def test_external_identifier_requested_plan(self):
        text = "Uses boost::shared_ptr<SensorFrame>."
        self.assertEqual(self.sanitize(text, symbols=["boost::shared_ptr"]), text)

    def test_external_identifier_unrelated_claim(self):
        text = "Domain::Buffer<Foo> is defined in src/buffer.h."
        self.assertEqual(self.sanitize(text), text)

    def test_external_identifier_metadata_preserved(self):
        from copy import deepcopy
        from panda_agent.qa import _strip_nonessential_external_identifiers
        claim = dict(claim_id="c1", claim_text="Uses std::vector<Foo>.",
                     evidence_ids=["e1"], answer_point_ids=["point.1"], extra={"value": 7})
        before = deepcopy(claim)
        result = _strip_nonessential_external_identifiers([claim], "Explain storage.", {})[0]
        self.assertEqual(claim, before)
        self.assertEqual({k: v for k, v in result.items() if k != "claim_text"},
                         {k: v for k, v in before.items() if k != "claim_text"})

    def test_external_identifier_multiple_and_spaced_templates(self):
        self.assertEqual(self.sanitize("std::vector <Foo> and std::vector<Bar>"),
                         "an internal support type containing (Foo) and an internal support type containing (Bar)")

    def test_external_identifier_incomplete_template_preserved(self):
        text = "Uses std::vector<Foo"
        self.assertEqual(self.sanitize(text), text)

    def test_external_identifier_answer_revision_integration(self):
        from copy import deepcopy
        claim = dict(claim_id="c1", claim_text="Uses std::vector<SensorPacket>.",
                     evidence_ids=["e1"], answer_point_ids=["point.1"])
        class Vertex:
            def generate_json(self, prompt, schema, **kwargs):
                return {"claims": [deepcopy(claim)]}
        bundle = bundle_for(code_evidence(text="Uses std::vector<SensorPacket>."))
        for mode in ("legacy_question_core", "runtime_e1_v2"):
            with self.subTest(mode=mode):
                agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=Vertex())
                state = dict(question="Explain storage.", bundle=bundle,
                             answer_point_coverage_mode=mode,
                             runtime_answer_points=[{"answer_point_id": "point.1", "text": "Explain storage."}])
                answer = agent._answer(state)
                revised = agent._revise({**state, **answer, "unsupported_claim_ids": ["c1"],
                                         "supported_claims": [], "errors": ["unsupported claim c1"]})
                expected = "Uses an internal support type containing (SensorPacket)."
                self.assertEqual(answer["draft"]["claims"][0]["claim_text"], expected)
                self.assertEqual(revised["draft"]["claims"][0]["claim_text"], expected)
                self.assertEqual(revised["draft"]["claims"][0]["evidence_ids"], ["e1"])
                self.assertEqual(revised["revision_count"], 1)
                self.assertEqual(agent.retriever.calls, 0)


class UnsupportedReviewVertex(FakeVertex):
    """Review double whose semantic review conservatively rejects every claim."""

    def generate_json(self, prompt, schema, **kwargs):
        if "supported" in schema.get("properties", {}):
            payload = json.loads(prompt)
            return {
                "supported": False,
                "unsupported_claim_ids": [item["claim_id"] for item in payload["untrusted_claims"]],
                "irrelevant_claim_ids": [],
                "missing_requirement_ids": [],
                "reason": "conservative review",
            }
        return super().generate_json(prompt, schema, **kwargs)


class VerifierSupportSemanticTests(unittest.TestCase):
    """F2-A1/F2-A1-R1 contract: citation, locator, and identifier grounding are
    deterministic integrity checks, not whole-claim semantic entailment.  Only
    the semantic review decides whole-claim support; lexical coverage can never
    override an unsupported verdict, and integrity checks stay independent of
    that verdict."""

    def _verify_under_conservative_review(self, claims, bundle):
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=UnsupportedReviewVertex())
        return agent._verify({
            "question": "Explain this implementation.",
            "bundle": bundle,
            "draft": {"claims": claims},
        })

    # T1 — correct path, unsupported semantics
    def test_correct_path_with_unsupported_semantics_remains_unsupported(self):
        evidence = code_evidence(
            text="The reconstruction macro prepares the restgas profile steps.",
            path="macro/target/ana_dpm.C",
        )
        bundle = bundle_for(evidence)
        rejected = self._verify_under_conservative_review([{
            "claim_id": "c1",
            "claim_text": "macro/target/ana_dpm.C proves that detector noise is exactly zero.",
            "evidence_ids": ["e1"],
            "answer_point_ids": ["question_core"],
        }], bundle)
        self.assertIn("unsupported claim c1", rejected["errors"])

    # T2 — correct symbols, unsupported semantics
    def test_correct_symbols_with_unsupported_relationship_remains_unsupported(self):
        evidence = code_evidence(
            text="class PndPidCorrelator {}; void PndPidCorrelator::Exec(Option_t* option);",
            path="pid/PndPidCorrelator.h",
        )
        bundle = bundle_for(evidence)
        rejected = self._verify_under_conservative_review([{
            "claim_id": "c1",
            "claim_text": "PndPidCorrelator::Exec destroys the accepted histogram data.",
            "evidence_ids": ["e1"],
            "answer_point_ids": ["question_core"],
        }], bundle)
        self.assertIn("unsupported claim c1", rejected["errors"])

    # T3 — multiple correct identifiers joined by an unsupported predicate are
    # still not entailment
    def test_multiple_identifiers_with_false_predicate_remains_unsupported(self):
        evidence = code_evidence(
            text="PndLmdDataReader reads calibration entries; PndLmdTrackQ normalizes pointer syntax.",
            path="data/PndLmdDataReader.cxx",
        )
        bundle = bundle_for(evidence)
        rejected = self._verify_under_conservative_review([{
            "claim_id": "c1",
            "claim_text": "PndLmdDataReader forwards every entry to PndLmdTrackQ and deletes the raw output.",
            "evidence_ids": ["e1"],
            "answer_point_ids": ["question_core"],
        }], bundle)
        self.assertIn("unsupported claim c1", rejected["errors"])

    # T4 — legitimate semantic support still succeeds
    def test_legitimate_supported_claim_still_accepted(self):
        evidence = code_evidence(
            text="The reconstruction macro prepares the restgas profile steps.",
            path="macro/target/ana_dpm.C",
        )
        bundle = bundle_for(evidence)
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        accepted = agent._verify({
            "question": "Explain this implementation.",
            "bundle": bundle,
            "draft": {"claims": [{
                "claim_id": "c1",
                "claim_text": "macro/target/ana_dpm.C prepares the restgas profile steps.",
                "evidence_ids": ["e1"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertNotIn("unsupported claim c1", accepted["errors"])
        self.assertIn("c1", [claim["claim_id"] for claim in accepted["supported_claims"]])

    # T5 — former F2-A1 removals stay removed
    def test_removed_token_whitelist_no_longer_grants_support(self):
        evidence = code_evidence(
            text="fillData and successfullyPassedFilters fill accepted histograms.",
            path="data/PndLmdDataReader.cxx",
        )
        bundle = bundle_for(evidence)
        rejected = self._verify_under_conservative_review([{
            "claim_id": "c1",
            "claim_text": "fillData and successfullyPassedFilters fill accepted histograms.",
            "evidence_ids": ["e1"],
            "answer_point_ids": ["question_core"],
        }], bundle)
        self.assertIn("unsupported claim c1", rejected["errors"])

    def test_comparison_wording_no_longer_grants_support(self):
        root = code_evidence(
            evidence_id="root",
            text="The target macro coordinates reconstruction steps.",
            path="macro/target/ana_dpm.C",
        )
        fit = code_evidence(
            evidence_id="fit",
            source_id="luminosityfit",
            text="The model factory composes the fit model.",
            path="model/PndLmdModelFactory.cxx",
        )
        bundle = bundle_for([root, fit])
        bundle["plan"]["resolved_versions"]["luminosityfit"] = (
            "luminosityfit@11f1edc49dcbaeb61d707491a6d3bbec390fcd42"
        )
        rejected = self._verify_under_conservative_review([{
            "claim_id": "c1",
            "claim_text": "macro/target/ana_dpm.C and model/PndLmdMystery.cxx show a different implementation.",
            "evidence_ids": ["root", "fit"],
            "answer_point_ids": ["question_core"],
        }], bundle)
        self.assertIn("unsupported claim c1", rejected["errors"])

    # T6 — deterministic integrity checks remain active and independent of the
    # semantic verdict
    def test_deterministic_integrity_checks_remain_active(self):
        evidence = code_evidence(
            source_id="luminosityfit",
            text="The fit model composes acceptance components.",
            path="model/PndLmdModelFactory.cxx",
        )
        bundle = bundle_for(evidence)
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        checked = agent._verify({
            "question": "Explain this implementation.",
            "bundle": bundle,
            "draft": {"claims": [{
                "claim_id": "c1",
                "claim_text": "PndLmdMissing::Symbol lives in model/PndLmdModelFactory.cxx.",
                "evidence_ids": ["e1"],
                "answer_point_ids": ["question_core"],
            }]},
        })
        self.assertIn("wrong code version e1", checked["errors"])
        self.assertIn("unsupported identifier PndLmdMissing::Symbol", checked["errors"])


class PointerNormalizationCompletenessTests(unittest.TestCase):
    """F2-A2 contract: the pointer-normalization completeness requirement
    derives its target symbol from the live question's pointer type
    expression; no fixed PndLmdTrackQ/lmdtrackq dependency remains anywhere in
    the R10 completeness, evidence-selection, or compaction contract."""

    POINTER_PLAN = {
        "intent": "api",
        "symbols": ["PndLmdTrackQ"],
        "concepts": ["pointer type normalization"],
    }

    def _requirement(self, question, plan=None):
        requirements = _answer_requirements(question, plan or dict(self.POINTER_PLAN))
        matches = [r for r in requirements if r["id"] == "pointer_identifier_normalization"]
        return matches[0] if matches else None

    # T1 — historical symbol still works generically
    def test_historical_symbol_derived_from_question_and_complete_answer_passes(self):
        requirement = self._requirement(
            "PndLmdTrackQ* appears in adapter code. How should this pointer type be normalized?"
        )
        self.assertEqual(requirement["target_symbol"], "PndLmdTrackQ")
        complete_claim = [{
            "claim_id": "c1",
            "claim_text": "The pointer type expression PndLmdTrackQ* normalizes to the underlying PndLmdTrackQ symbol; the asterisk is pointer syntax and is not part of a new identifier.",
            "evidence_ids": [],
        }]
        self.assertEqual(
            _deterministic_missing_requirement_ids([requirement], complete_claim, {}),
            [],
        )

    # T2 — unseen symbol works end to end
    def test_unseen_symbol_derived_and_complete_answer_passes(self):
        requirement = self._requirement(
            "SensorFrame* appears in the adapter. How should this pointer type be normalized?"
        )
        self.assertEqual(requirement["target_symbol"], "SensorFrame")
        complete_claim = [{
            "claim_id": "c1",
            "claim_text": "SensorFrame* is a pointer type expression; SensorFrame is the underlying code symbol, and the asterisk is pointer syntax and is not part of a new identifier.",
            "evidence_ids": [],
        }]
        self.assertEqual(
            _deterministic_missing_requirement_ids([requirement], complete_claim, {}),
            [],
        )

    # T3 — wrong known symbol cannot satisfy an unseen query
    def test_wrong_known_symbol_cannot_satisfy_unseen_target(self):
        requirement = self._requirement(
            "SensorFrame* appears in the adapter. How should this pointer type be normalized?"
        )
        historical_claim = [{
            "claim_id": "c1",
            "claim_text": "The pointer type expression PndLmdTrackQ* normalizes to the underlying PndLmdTrackQ symbol; the asterisk is pointer syntax and is not part of a new identifier.",
            "evidence_ids": [],
        }]
        self.assertEqual(
            _deterministic_missing_requirement_ids([requirement], historical_claim, {}),
            ["pointer_identifier_normalization"],
        )

    # T4 — right symbol but incomplete semantics fails
    def test_right_symbol_with_incomplete_semantics_remains_missing(self):
        requirement = self._requirement(
            "SensorFrame* appears in the adapter. How should this pointer type be normalized?"
        )
        for claim_text in (
            "SensorFrame is used by the adapter.",
            "SensorFrame* is passed between the adapter layers.",
        ):
            with self.subTest(claim_text=claim_text):
                claims = [{"claim_id": "c1", "claim_text": claim_text, "evidence_ids": []}]
                self.assertEqual(
                    _deterministic_missing_requirement_ids([requirement], claims, {}),
                    ["pointer_identifier_normalization"],
                )

    # T5 — pointer qualifier semantics required
    def test_missing_qualifier_explanation_remains_missing(self):
        requirement = self._requirement(
            "SensorFrame* appears in the adapter. How should this pointer type be normalized?"
        )
        no_qualifier = [{
            "claim_id": "c1",
            "claim_text": "SensorFrame is the underlying code symbol used by the adapter.",
            "evidence_ids": [],
        }]
        self.assertEqual(
            _deterministic_missing_requirement_ids([requirement], no_qualifier, {}),
            ["pointer_identifier_normalization"],
        )

    # T6 — non-pointer question does not activate
    def test_non_pointer_question_does_not_activate(self):
        self.assertIsNone(self._requirement("Where is SensorFrame defined?"))

    # T7 — plan-only symbol does not become target
    def test_plan_only_symbol_does_not_manufacture_requirement(self):
        self.assertIsNone(self._requirement("Where is PndLmdTrackQ defined?"))
        self.assertIsNone(self._requirement("How is the pointer parameter passed?"))
        requirement = self._requirement(
            "SensorFrame* appears in the adapter. How should this pointer type be normalized?"
        )
        self.assertEqual(requirement["target_symbol"], "SensorFrame")

    # T8 — evidence selection and compaction are dynamic
    def test_evidence_selection_and_compaction_follow_dynamic_target(self):
        requirement = {
            "id": "pointer_identifier_normalization",
            "instruction": "",
            "target_symbol": "SensorFrame",
        }
        target_evidence = {
            "e1": {"evidence_id": "e1", "source_id": "pandaroot", "text": "SensorFrame carries the adapter frame payload.", "locator": {}},
        }
        historical_evidence = {
            "e2": {"evidence_id": "e2", "source_id": "pandaroot", "text": "PndLmdTrackQ tracks particles.", "locator": {}},
        }
        selected = _requirement_evidence([requirement], {**target_evidence, **historical_evidence})
        selected_ids = [item["evidence_id"] for item in selected["pointer_identifier_normalization"]]
        self.assertIn("e1", selected_ids)
        self.assertNotIn("e2", selected_ids)
        compacted = _compact_requirement_evidence(
            selected["pointer_identifier_normalization"],
            "pointer_identifier_normalization",
            "SensorFrame",
        )
        self.assertTrue(compacted)
        self.assertIn("sensorframe", compacted[0]["text"].casefold())


class CoverageReviewVertex(FakeVertex):
    """Coverage-mode review double: full answer-point coverage, while the model
    still returns the given legacy missing-requirement ids. Records every
    payload, including revision calls."""

    def __init__(self, missing_requirement_ids=()):
        self.missing_requirement_ids = list(missing_requirement_ids)
        self.prompts = []

    def generate_json(self, prompt, schema, **kwargs):
        self.prompts.append(json.loads(prompt))
        if "supported" in schema.get("properties", {}):
            payload = self.prompts[-1]
            review = {
                "supported": True,
                "unsupported_claim_ids": [],
                "irrelevant_claim_ids": [],
                "missing_requirement_ids": self.missing_requirement_ids,
                "reason": "",
            }
            if "claim_answer_point_mappings" in schema.get("properties", {}):
                review["claim_answer_point_mappings"] = [
                    {
                        "claim_id": item["claim_id"],
                        "answer_point_ids": list(item.get("answer_point_ids") or []),
                    }
                    for item in payload["untrusted_claims"]
                ]
                review["missing_answer_point_ids"] = []
            return review
        return super().generate_json(prompt, schema, **kwargs)


class StaleLegacyReviewVertex(CoverageReviewVertex):
    """Coverage review double that reports stale legacy incompleteness: the
    aggregate supported flag is false only because of retired legacy
    requirements, while every authoritative answer-point axis is clean."""

    def generate_json(self, prompt, schema, **kwargs):
        if "supported" in schema.get("properties", {}):
            payload = json.loads(prompt)
            self.prompts.append(payload)
            review = {
                "supported": False,
                "unsupported_claim_ids": [],
                "irrelevant_claim_ids": [],
                "missing_requirement_ids": self.missing_requirement_ids,
                "reason": "legacy completeness obligation not satisfied",
            }
            if "claim_answer_point_mappings" in schema.get("properties", {}):
                review["claim_answer_point_mappings"] = [
                    {
                        "claim_id": item["claim_id"],
                        "answer_point_ids": list(item.get("answer_point_ids") or []),
                    }
                    for item in payload["untrusted_claims"]
                ]
                review["missing_answer_point_ids"] = []
            return review
        return super().generate_json(prompt, schema, **kwargs)


class E1E2CompatibilityAuthorityTests(unittest.TestCase):
    """F2-A3 seam contract: in E1/E2 coverage modes the claim-to-answer-point
    coverage review owns whole-answer completeness and plan-only suggestions
    never become mandatory public-answer content; the legacy named-requirement
    contract remains a legacy_question_core bridge."""

    def _state(self, bundle, mode=None):
        state = {
            "question": "Explain the factory composition.",
            "bundle": bundle,
            "draft": {"claims": [{
                "claim_id": "c1",
                "claim_text": "The factory composes the model from its inputs.",
                "evidence_ids": ["e1"],
            }]},
            "answer_requirements": [
                {"id": "factory_composition", "instruction": "legacy completeness obligation"}
            ],
        }
        if mode:
            state["answer_point_coverage_mode"] = mode
            state["draft"]["claims"][0]["answer_point_ids"] = ["point.1"]
            state["runtime_answer_points"] = [
                {"answer_point_id": "point.1", "text": "Explain the factory composition."}
            ]
        return state

    # T2/T6 — full answer-point coverage plus a legacy missing requirement
    # produces no independent legacy failure in coverage modes.
    def test_coverage_mode_legacy_requirement_is_non_authoritative(self):
        bundle = bundle_for(code_evidence())
        for mode in ("shadow_e1_v2", "runtime_e1_v2"):
            with self.subTest(mode=mode):
                vertex = CoverageReviewVertex(["factory_composition"])
                agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=vertex)
                out = agent._verify(self._state(bundle, mode))
                self.assertEqual(out["missing_requirement_ids"], [])
                self.assertFalse(any("missing answer requirement" in err for err in out["errors"]))
                self.assertEqual([c["claim_id"] for c in out["supported_claims"]], ["c1"])

    # T7 — legacy_question_core keeps named-requirement enforcement (bridge).
    def test_legacy_default_still_enforces_requirements(self):
        bundle = bundle_for(code_evidence())
        vertex = CoverageReviewVertex(["factory_composition"])
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=vertex)
        out = agent._verify(self._state(bundle))
        self.assertEqual(out["missing_requirement_ids"], ["factory_composition"])
        self.assertTrue(any("missing answer requirement factory_composition" in err for err in out["errors"]))

    # T3 — plan-only data-flow suggestions synthesize claims only in legacy mode.
    def test_dataflow_augmentation_is_mode_scoped(self):
        bundle = bundle_for(
            code_evidence(text="The workflow stage runs after ingest.", object_type="workflow"),
            intent="data_flow",
        )
        bundle["plan"]["required_source_types"] = ["workflow", "code"]
        bundle["plan"]["symbols"] = ["src/Factory.cxx"]
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        shadow_state = {
            "question": "Explain the data flow.",
            "bundle": bundle,
            "draft": {"claims": []},
            "answer_point_coverage_mode": "shadow_e1_v2",
        }
        self.assertEqual(agent._augment_required_dataflow_evidence({"claims": []}, shadow_state)["claims"], [])
        legacy_state = {key: value for key, value in shadow_state.items() if key != "answer_point_coverage_mode"}
        legacy = agent._augment_required_dataflow_evidence({"claims": []}, legacy_state)
        self.assertTrue(any(claim["claim_id"].startswith("required_") for claim in legacy["claims"]))

    # T3 — plan symbols do not become mandatory boundary components in
    # coverage modes.
    def test_boundary_locators_are_mode_scoped(self):
        bundle = bundle_for(code_evidence(), intent="module_structure", concepts=["model boundary"])
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=CapturingVertex())
        shadow_state = {
            "question": "Map the module boundary.",
            "bundle": bundle,
            "answer_point_coverage_mode": "shadow_e1_v2",
            "runtime_answer_points": [
                {"answer_point_id": "point.1", "text": "Map the module boundary."}
            ],
        }
        agent._answer(shadow_state)
        self.assertEqual(agent.vertex.prompts[0]["retrieval_plan"]["required_boundary_locators"], [])
        agent._answer({"question": "Map the module boundary.", "bundle": bundle})
        self.assertEqual(
            agent.vertex.prompts[1]["retrieval_plan"]["required_boundary_locators"],
            bundle["plan"]["symbols"],
        )

    # T1/T8 — coverage-mode generation carries no legacy requirement authority;
    # a plan-shaped requirement that legacy mode would activate is absent.
    def test_generation_payload_authority_is_mode_scoped(self):
        bundle = bundle_for(code_evidence(), intent="algorithm_implementation")
        bundle["plan"]["symbols"] = ["model/PndLmdModelFactory.cxx"]
        cases = (
            ("shadow_e1_v2", []),
            ("runtime_e1_v2", []),
            (None, ["factory_composition"]),
        )
        for mode, expected_ids in cases:
            with self.subTest(mode=mode or "legacy_question_core"):
                agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=CapturingVertex())
                state = {"question": "Explain the factory composition.", "bundle": bundle}
                if mode:
                    state["answer_point_coverage_mode"] = mode
                    state["runtime_answer_points"] = [
                        {"answer_point_id": "point.1", "text": "Explain the factory composition."}
                    ]
                agent._answer(state)
                payload_ids = [
                    item["id"] for item in agent.vertex.prompts[0]["answer_requirements"]
                ]
                if expected_ids:
                    self.assertIn("factory_composition", payload_ids)
                else:
                    self.assertEqual(payload_ids, expected_ids)

    # T3 — coverage-mode review payload has no legacy completeness axis.
    def test_coverage_review_payload_has_no_legacy_axis(self):
        bundle = bundle_for(code_evidence())
        vertex = CoverageReviewVertex(["factory_composition"])
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=vertex)
        agent._verify(self._state(bundle, "shadow_e1_v2"))
        payload = vertex.prompts[0]
        self.assertEqual(payload["answer_requirements"], [])
        self.assertEqual(payload["requirement_evidence"], {})

    # T4 — coverage-mode revision payload is driven only by missing answer
    # points; stale state-level legacy requirement ids cannot leak back in.
    def test_coverage_revision_payload_has_no_legacy_axis(self):
        bundle = bundle_for(code_evidence())
        vertex = CoverageReviewVertex()
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=vertex)
        state = {
            "question": "Explain this implementation.",
            "bundle": bundle,
            "draft": {"claims": [{
                "claim_id": "c1",
                "claim_text": "The model is composed.",
                "evidence_ids": ["e1"],
                "answer_point_ids": [],
            }]},
            "supported_claims": [],
            "unsupported_claim_ids": [],
            "missing_requirement_ids": ["factory_composition"],
            "missing_answer_point_ids": ["point.1"],
            "answer_requirements": [{"id": "factory_composition", "instruction": "legacy"}],
            "answer_point_coverage_mode": "shadow_e1_v2",
            "runtime_answer_points": [
                {"answer_point_id": "point.1", "text": "Explain this implementation."}
            ],
            "errors": ["missing answer point point.1"],
        }
        agent._revise(state)
        payload = vertex.prompts[0]
        self.assertEqual(payload["missing_answer_point_ids"], ["point.1"])
        self.assertEqual(payload["answer_requirements"], [])
        self.assertEqual(payload["missing_requirement_ids"], [])
        self.assertEqual(payload["requirement_evidence"], {})
        self.assertIn("missing_answer_point_ids", payload["revision_scope"])
        self.assertNotIn("missing_requirement_ids", payload["revision_scope"])

    # T5 — the central repair sentinel: a stale known legacy missing
    # requirement with supported=false must not fail a coverage-complete
    # answer.
    def test_stale_legacy_missing_requirement_does_not_fail_coverage_answer(self):
        bundle = bundle_for(code_evidence())
        for mode in ("shadow_e1_v2", "runtime_e1_v2"):
            with self.subTest(mode=mode):
                vertex = StaleLegacyReviewVertex(["factory_composition"])
                agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=vertex)
                out = agent._verify(self._state(bundle, mode))
                self.assertNotIn("missing answer requirement factory_composition", out["errors"])
                self.assertFalse(any("evidence review failed" in err for err in out["errors"]))
                self.assertEqual([c["claim_id"] for c in out["supported_claims"]], ["c1"])
                audit = out["answer_point_audit"]
                self.assertTrue(audit["coverage_complete"])
                self.assertTrue(audit["coverage_evaluable"])

    # T6 — unknown requirement ids remain a structural/hallucination guard
    # (caught by coverage-review validation) with conservative failure; R1 is
    # not blanket missing-id suppression.
    def test_unknown_missing_requirement_remains_guarded(self):
        bundle = bundle_for(code_evidence())
        vertex = StaleLegacyReviewVertex(["nonexistent_requirement"])
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=vertex)
        out = agent._verify(self._state(bundle, "shadow_e1_v2"))
        self.assertTrue(
            any("invalid answer-point coverage review" in err for err in out["errors"])
        )
        self.assertEqual(out["supported_claims"], [])
        self.assertTrue(out["answer_point_audit"]["review_error"])

    # T7 — genuine unsupported-claim verdicts still fail in coverage modes.
    def test_genuine_unsupported_claim_still_fails_in_coverage_mode(self):
        bundle = bundle_for(code_evidence())
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=UnsupportedReviewVertex())
        out = agent._verify(self._state(bundle, "shadow_e1_v2"))
        self.assertTrue(any("unsupported claim c1" in err for err in out["errors"]))


class PremiseRefusalGeneralizationTests(unittest.TestCase):
    PID_CATALOG_ROWS = [
        ({"symbol": "PndPidCorrelator", "path": "pid/PndPidCorrelator.h"}, "class PndPidCorrelator {};")
    ]
    """F2-A4 contract: bare-class premise refusals are generic, question-
    grounded, and decided by the locked-corpus catalog; selected evidence can
    only supply a narrow cited context statement, never a substitute
    implementation or a fixed historical locator."""

    def _agent(self, bundle, catalog_rows=()):
        storage = CatalogStorage(list(catalog_rows))
        retriever = FakeRetriever(bundle)
        retriever.storage = storage
        return QAAgent(Path.cwd(), retriever=retriever, vertex=FakeVertex())

    def _finalize_result(self, agent, question, bundle):
        state = {
            "question": question,
            "bundle": bundle,
            "sufficient": False,
            "errors": [
                "unsupported requested symbol: "
                + ("PndUniversalRestgasDeconvolver" if "PndUniversalRestgasDeconvolver" in question else "ImaginaryRestgasCorrector")
            ],
            "supported_claims": [],
        }
        return agent._finalize(state)["result"]

    # T1 — historical negative control now uses the generic path.
    def test_historical_negative_control_uses_generic_path(self):
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle)
        question = "How does PndUniversalRestgasDeconvolver normalize the restgas profile?"
        self.assertEqual(
            agent._answerability_guard({"question": question, "bundle": bundle}),
            ["unsupported requested symbol: PndUniversalRestgasDeconvolver"],
        )
        state = {
            "question": question,
            "bundle": bundle,
            "sufficient": False,
            "errors": ["unsupported requested symbol: PndUniversalRestgasDeconvolver"],
            "supported_claims": [],
        }
        result = agent._finalize(state)["result"]
        self.assertEqual(result["status"], QAStatus.INSUFFICIENT_EVIDENCE.value)
        self.assertIn("does not define PndUniversalRestgasDeconvolver", result["answer"])
        self.assertNotIn("efficiency_correction", result["answer"])
        self.assertNotIn("instead", result["answer"])

    # T2 — unseen nonexistent class behaves the same.
    def test_unseen_nonexistent_class_uses_generic_path(self):
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle)
        question = "How does ImaginaryRestgasCorrector implement the correction?"
        self.assertEqual(
            agent._answerability_guard({"question": question, "bundle": bundle}),
            ["unsupported requested symbol: ImaginaryRestgasCorrector"],
        )
        result = self._finalize_result(agent, question, bundle)
        self.assertIn("does not define ImaginaryRestgasCorrector", result["answer"])
        self.assertNotIn("instead", result["answer"])

    # T3 / §20 sentinel — a known class absent from selected evidence is not
    # refused: the locked catalog, not selected evidence, is the authority.
    def test_known_class_absent_from_selected_evidence_is_not_refused(self):
        bundle = bundle_for(code_evidence())  # evidence mentions PndPidCorrelator only
        catalog_rows = [({"symbol": "SensorFrame", "path": "src/SensorFrame.h"}, "class SensorFrame {};")]
        agent = self._agent(bundle, catalog_rows)
        self.assertEqual(
            agent._answerability_guard({
                "question": "How does SensorFrame implement the correction?",
                "bundle": bundle,
            }),
            [],
        )

    # T4 — plan-only unknown symbol does not create a refusal.
    def test_plan_only_unknown_symbol_does_not_create_refusal(self):
        bundle = bundle_for(code_evidence(), symbols=["ImaginaryRestgasCorrector"])
        agent = self._agent(bundle)
        self.assertEqual(
            agent._answerability_guard({
                "question": "Explain the restgas workflow in this corpus.",
                "bundle": bundle,
            }),
            [],
        )

    # T5 — explicit simple class syntax is handled without plan support.
    def test_explicit_class_wording_is_handled(self):
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle)
        self.assertEqual(
            agent._answerability_guard({
                "question": "Where is class MissingTrackAdapter defined?",
                "bundle": bundle,
            }),
            ["unsupported requested symbol: MissingTrackAdapter"],
        )

    # T6 — ordinary capitalized prose tokens never become requested classes.
    def test_ordinary_prose_tokens_are_not_refused(self):
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle)
        for question in (
            "What does Implementation mean here?",
            "What is the SHA-256 checksum of the locked source file?",
        ):
            with self.subTest(question=question):
                self.assertEqual(
                    agent._answerability_guard({"question": question, "bundle": bundle}),
                    [],
                )

    # T7 — the historical locator receives no special preference: the
    # query-relevant evidence outranks it under the generic ranking.
    def test_no_fixed_alternative_locator_preference(self):
        relevant = code_evidence(
            evidence_id="rel",
            text="The restgas correction workflow prepares the profile.",
            path="src/Workflow.cxx",
        )
        historical = code_evidence(
            evidence_id="hist",
            text="Longitudinal efficiency correction macro.",
            path="macro/target/correction/efficiency_correction_2.C",
        )
        bundle = bundle_for([relevant, historical])
        agent = self._agent(bundle)
        question = "How does ImaginaryRestgasCorrector apply the restgas correction?"
        state = {
            "question": question,
            "bundle": bundle,
            "sufficient": False,
            "errors": ["unsupported requested symbol: ImaginaryRestgasCorrector"],
            "supported_claims": [],
        }
        result = agent._finalize(state)["result"]
        cited_ids = [claim["evidence_ids"][0] for claim in result["claims"]]
        self.assertTrue(cited_ids)
        self.assertNotIn("hist", cited_ids)
        self.assertNotIn("efficiency_correction_2.C", result["answer"])

    # T8 — no speculative replacement-implementation claim.
    def test_no_speculative_replacement_claim(self):
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle)
        result = self._finalize_result(agent, "How does ImaginaryRestgasCorrector implement the correction?", bundle)
        for claim in result["claims"]:
            self.assertNotIn("instead", claim["claim_text"].casefold())
            self.assertNotIn("replacement", claim["claim_text"].casefold())
        self.assertNotIn("uses a longitudinal", result["answer"])

    # T9 — no relevant selected evidence produces a bare refusal with zero
    # optional claims and zero fabricated citations.
    def test_no_relevant_basis_produces_zero_optional_claims(self):
        unrelated = code_evidence(
            text="The luminosity fit extracts the luminosity value.",
            path="fit/LuminosityFit.cxx",
        )
        bundle = bundle_for(unrelated)
        agent = self._agent(bundle)
        result = self._finalize_result(agent, "How does ImaginaryRestgasCorrector implement the correction?", bundle)
        self.assertEqual(result["claims"], [])
        self.assertEqual(result["evidence"], [])
        self.assertIn("does not define ImaginaryRestgasCorrector", result["answer"])

    # T10 — a query-relevant basis is evidence-grounded and names only what
    # the evidence supports.
    def test_relevant_basis_is_evidence_grounded(self):
        relevant = code_evidence(
            evidence_id="rel",
            text="The restgas correction workflow prepares the profile.",
            path="src/Workflow.cxx",
        )
        bundle = bundle_for(relevant)
        agent = self._agent(bundle)
        result = self._finalize_result(agent, "How does ImaginaryRestgasCorrector apply the restgas correction?", bundle)
        self.assertEqual(len(result["claims"]), 1)
        self.assertEqual(result["claims"][0]["evidence_ids"], ["rel"])
        self.assertIn("documents", result["claims"][0]["claim_text"])
        self.assertNotIn("instead", result["answer"])

    # T11 — qualified unsupported-API refusal unchanged (R05 fallback untouched).
    def test_unsupported_api_refusal_unchanged(self):
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle)
        self.assertEqual(
            agent._answerability_guard({
                "question": "How does PndPidCorrelator::MissingSeed build the fit?",
                "bundle": bundle,
            }),
            ["unsupported requested API symbol: PndPidCorrelator::MissingSeed"],
        )

    # T14 — a coverage-mode early refusal ends at insufficiency and never
    # reaches the E3 missing-point trigger inputs.
    def test_coverage_mode_early_refusal_does_not_reach_e3(self):
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle)
        state = {
            "question": "How does ImaginaryRestgasCorrector implement the correction?",
            "bundle": bundle,
            "answer_point_coverage_mode": "runtime_e1_v2",
            "runtime_answer_points": [
                {"answer_point_id": "point.1", "text": "Explain the correction."}
            ],
        }
        out = agent._sufficiency(state)
        self.assertFalse(out["sufficient"])
        self.assertEqual(
            out["errors"],
            ["unsupported requested symbol: ImaginaryRestgasCorrector"],
        )
        self.assertNotIn("missing_answer_point_ids", out)
        self.assertNotIn("missing_point_retrieval_count", out)

    # §21 premise-mismatch sentinel — a question assuming an unavailable class
    # implementation is refused without hallucinating from related evidence.
    def test_premise_mismatch_refuses_without_hallucination(self):
        related = code_evidence(
            text="The restgas profile is reconstructed from the corrected density.",
            path="src/RestgasProfile.cxx",
        )
        bundle = bundle_for(related)
        agent = self._agent(bundle)
        question = "How does MissingTrackAdapter apply the restgas correction?"
        self.assertEqual(
            agent._answerability_guard({"question": question, "bundle": bundle}),
            ["unsupported requested symbol: MissingTrackAdapter"],
        )
        state = {
            "question": question,
            "bundle": bundle,
            "sufficient": False,
            "errors": ["unsupported requested symbol: MissingTrackAdapter"],
            "supported_claims": [],
        }
        result = agent._finalize(state)["result"]
        self.assertNotIn("MissingTrackAdapter", related["text"])
        self.assertTrue(result["answer"].startswith("The locked corpus does not define MissingTrackAdapter"))

    # T15/T16 (F2-A5) - sufficiency honors explicit question-derived source
    # obligations against the actual source-type classification.
    def test_sufficiency_honors_explicit_source_obligations(self):
        cases = (
            (["paper"], "missing required source: paper", code_evidence()),
            (["code"], "missing required source: code", code_evidence(source_id="li_2026")),
        )
        for required, expected_error, evidence in cases:
            with self.subTest(required=required):
                bundle = bundle_for(evidence)
                bundle["plan"]["required_source_types"] = list(required)
                agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
                out = agent._sufficiency({
                    "question": "According to the paper, how is this implemented?",
                    "bundle": bundle,
                })
                self.assertFalse(out["sufficient"])
                self.assertIn(expected_error, out["errors"])

    # T17/T18 (F2-A5) - no hard R01 obligation means no source-class refusal,
    # while zero evidence remains insufficient.
    def test_no_obligation_and_no_evidence_refusals_unchanged(self):
        bundle = bundle_for(code_evidence())
        bundle["plan"]["required_source_types"] = []
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever(bundle), vertex=FakeVertex())
        out = agent._sufficiency({
            "question": "How does this correction work?",
            "bundle": bundle,
        })
        self.assertTrue(out["sufficient"])
        self.assertEqual(out["errors"], [])
        empty = bundle_for(code_evidence())
        empty["evidence"] = []
        empty["plan"]["required_source_types"] = []
        out = agent._sufficiency({"question": "How does this correction work?", "bundle": empty})
        self.assertFalse(out["sufficient"])
        self.assertEqual(out["errors"], ["no evidence"])

    # T1 (R1) — central plan-contamination sentinel: plan-only suggestions can
    # never make unrelated evidence the optional refusal basis.
    def test_plan_only_suggestion_cannot_become_refusal_basis(self):
        plan_only = code_evidence(
            text="PndLmdDataReader applies event selection.",
            path="data/PndLmdDataReader.cxx",
        )
        bundle = bundle_for(plan_only, symbols=["PndLmdDataReader"])
        agent = self._agent(bundle, catalog_rows=[])
        question = "How does ImaginaryRestgasCorrector implement the correction?"
        basis = _refusal_basis_evidence(
            {"question": question, "bundle": bundle}, kind="unsupported_symbol"
        )
        self.assertIsNone(basis)
        state = {
            "question": question,
            "bundle": bundle,
            "sufficient": False,
            "errors": ["unsupported requested symbol: ImaginaryRestgasCorrector"],
            "supported_claims": [],
        }
        result = agent._finalize(state)["result"]
        self.assertEqual(result["claims"], [])
        self.assertEqual(result["evidence"], [])

    # T2 (R1) — question-relevant basis still works under question-only
    # anchors.
    def test_question_relevant_basis_still_selected(self):
        relevant = code_evidence(
            evidence_id="rel",
            text="The restgas correction workflow prepares the profile.",
            path="src/Workflow.cxx",
        )
        bundle = bundle_for(relevant, symbols=["PndLmdDataReader"])
        agent = self._agent(bundle, catalog_rows=[])
        basis = _refusal_basis_evidence(
            {
                "question": "How does ImaginaryRestgasCorrector apply the restgas correction?",
                "bundle": bundle,
            },
            kind="unsupported_symbol",
        )
        self.assertIsNotNone(basis)
        self.assertEqual(basis["evidence_id"], "rel")

    # T3 (R1) — natural-language "class of" is not a code symbol.
    def test_natural_language_class_of_does_not_trigger(self):
        self.assertEqual(_requested_bare_class_symbols("What class of problem is this?"), [])
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle, catalog_rows=[])
        self.assertEqual(
            agent._answerability_guard({
                "question": "What class of problem is this?",
                "bundle": bundle,
            }),
            [],
        )

    # T4 (R1) — natural-language "struct layout" is not a code symbol.
    def test_natural_language_struct_layout_does_not_trigger(self):
        self.assertEqual(_requested_bare_class_symbols("Explain the struct layout used here."), [])
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle, catalog_rows=[])
        self.assertEqual(
            agent._answerability_guard({
                "question": "Explain the struct layout used here.",
                "bundle": bundle,
            }),
            [],
        )

    # T6 (R1) — bare locator premise without "defined" is recognized.
    def test_bare_locator_premise_is_recognized(self):
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle, catalog_rows=[])
        self.assertEqual(
            agent._answerability_guard({
                "question": "Where is MissingTrackAdapter?",
                "bundle": bundle,
            }),
            ["unsupported requested symbol: MissingTrackAdapter"],
        )

    # T7 (R1) — known bare locator survives with a realistic catalog fixture.
    def test_known_bare_locator_with_catalog_support_is_not_refused(self):
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle, catalog_rows=self.PID_CATALOG_ROWS)
        self.assertEqual(
            agent._answerability_guard({
                "question": "Where is PndPidCorrelator?",
                "bundle": bundle,
            }),
            [],
        )

    # T13 (R1) — pointer premise extraction still recognizes the underlying
    # code symbol.
    def test_pointer_premise_extraction_remains_supported(self):
        self.assertEqual(_requested_bare_class_symbols("SensorGhostBuilder*"), ["SensorGhostBuilder"])
        bundle = bundle_for(code_evidence())
        agent = self._agent(bundle, catalog_rows=[])
        self.assertEqual(
            agent._answerability_guard({
                "question": "How should SensorGhostBuilder* be normalized?",
                "bundle": bundle,
            }),
            ["unsupported requested symbol: SensorGhostBuilder"],
        )


if __name__ == "__main__":
    unittest.main()
