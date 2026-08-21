from types import SimpleNamespace

import pytest
from panda_agent.retrieval import DenseQueryBundle, Retriever, build_semantic_query
from panda_agent.models import RetrievalPlan

def test_t0_raw_question_preservation():
    question = "How does this work?"
    plan = RetrievalPlan(
        intent="algorithm_theory",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {}
        }
    )
    sq = build_semantic_query(question, plan)
    assert sq.text == question
    assert sq.raw_question == question

    bundle = DenseQueryBundle.from_semantic_query(question, sq)
    assert bundle.raw.text == question
    assert bundle.raw.provenance == "user_raw"
    assert bundle.semantic is None

def test_t0_accepted_analyzer_concept_augmentation():
    question = "Where is the function defined?"
    plan = RetrievalPlan(
        intent="api",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {
                "concepts": [{"value": "PndTargetGenerator", "support_spans": ["the function"]}]
            }
        }
    )
    sq = build_semantic_query(question, plan)
    assert question in sq.text
    assert "Semantic focus:\nPndTargetGenerator" in sq.text
    assert len(sq.components) == 1
    assert sq.components[0].kind == "analyzer_concept"
    assert sq.components[0].value == "PndTargetGenerator"

    bundle = DenseQueryBundle.from_semantic_query(question, sq)
    assert bundle.raw.text == question
    assert bundle.semantic is not None
    assert bundle.semantic.text == sq.text
    assert bundle.semantic.provenance == "semantic_query"
    assert bundle.semantic.components == sq.components

def test_t0_reviewed_expansion_contamination_guard():
    question = "How to generate targets?"
    plan = RetrievalPlan(
        intent="usage",
        source_budgets={"code": 1.0},
        symbols=["pgenerators/Target/PndTargetGenerator.cxx"],
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {
                "concepts": [{"value": "target generation", "support_spans": ["generate targets"]}]
            }
        }
    )
    sq = build_semantic_query(question, plan)
    assert question in sq.text
    assert "pgenerators" not in sq.text
    assert "target generation" in sq.text
    assert len(sq.components) == 1

def test_t0_plan_flattened_fields_not_trusted():
    question = "test question"
    plan = RetrievalPlan(
        intent="usage",
        source_budgets={"code": 1.0},
        symbols=["bad_symbol"],
        concepts=["bad_concept"],
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {}
        }
    )
    sq = build_semantic_query(question, plan)
    assert sq.text == question
    assert "bad_symbol" not in sq.text
    assert "bad_concept" not in sq.text

def test_t0_scopes():
    question = "point-like acceptance"
    plan = RetrievalPlan(
        intent="algorithm_theory",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "deterministic_parse": {
                "fixed": {"concept_scopes": {"acceptance": "point_like_vs_restgas_effective"}}
            },
            "analyzer_accepted_semantic_delta": {
                "concept_scopes": [{"key": "acceptance", "value": "some_llm_value"}]
            }
        }
    )
    sq = build_semantic_query(question, plan)
    assert "acceptance=point_like_vs_restgas_effective" in sq.text
    assert "some_llm_value" not in sq.text

def test_t0_accepted_llm_only_scope_is_semantic_augmentation():
    question = "Explain efficiency for longitudinal acceptance."
    plan = RetrievalPlan(
        intent="algorithm_theory",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "deterministic_parse": {"fallback": {"concept_scopes": {"efficiency": "angular_acceptance"}}},
            "analyzer_accepted_semantic_delta": {
                "concept_scopes": [{
                    "key": "efficiency",
                    "value": "longitudinal_profile",
                    "support_spans": ["longitudinal acceptance"],
                }]
            },
        },
    )

    sq = build_semantic_query(question, plan)

    assert "efficiency=longitudinal_profile" in sq.text
    assert [(item.kind, item.provenance) for item in sq.components] == [
        ("analyzer_scope", "analyzer_accepted")
    ]

def test_t0_fallback_only_scope_is_excluded_from_semantic_augmentation():
    question = "Explain efficiency."
    plan = RetrievalPlan(
        intent="algorithm_theory",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "deterministic_parse": {
                "fallback": {"concept_scopes": {"efficiency": "angular_acceptance"}}
            },
            "analyzer_accepted_semantic_delta": {},
        },
    )

    sq = build_semantic_query(question, plan)

    assert sq.text == question
    assert sq.components == []
    assert DenseQueryBundle.from_semantic_query(question, sq).semantic is None

def test_t0_components_match_deduplicated_semantic_query():
    question = "Explain the acceptance."
    plan = RetrievalPlan(
        intent="algorithm_theory",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {
                "concepts": [
                    {"value": "angular acceptance", "support_spans": ["acceptance"]},
                    {"value": "angular acceptance", "support_spans": ["acceptance"]},
                ]
            }
        },
    )

    sq = build_semantic_query(question, plan)

    assert sq.text.count("angular acceptance") == 1
    assert len(sq.components) == 1
    assert sq.components[0].value == "angular acceptance"

def test_t0_symbol_duplication():
    question = "Where is PndTargetGenerator?"
    plan = RetrievalPlan(
        intent="api",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {
                "concepts": [{"value": "PndTargetGenerator", "support_spans": ["PndTargetGenerator"]}]
            }
        }
    )
    sq = build_semantic_query(question, plan)
    assert sq.text == question

def test_t0_repository_version_metadata_not_injected():
    question = "How to install?"
    plan = RetrievalPlan(
        intent="installation",
        target_repositories=["pandaroot"],
        resolved_versions={"pandaroot": "1234567"},
        source_budgets={"code": 1.0},
        analysis_diagnostics={}
    )
    sq = build_semantic_query(question, plan)
    assert sq.text == question
    assert "pandaroot" not in sq.text
    assert "1234567" not in sq.text

def test_t0_determinism():
    question = "test question"
    plan = RetrievalPlan(
        intent="api",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {
                "concepts": [{"value": "C", "support_spans": []}, {"value": "B", "support_spans": []}],
                "concept_scopes": [{"key": "K", "value": "V"}]
            },
            "deterministic_parse": {
                "fixed": {"concept_scopes": {"A": "X"}}
            }
        }
    )
    sq1 = build_semantic_query(question, plan)
    sq2 = build_semantic_query(question, plan)
    assert sq1.text == sq2.text
    assert sq1.text.endswith("A=X")


def test_t0_dense_bundle_keeps_policy_exclusions_out_of_semantic_dense():
    question = "How to generate targets?"
    plan = RetrievalPlan(
        intent="usage",
        source_budgets={"code": 1.0},
        symbols=["reviewed/path.py"],
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {
                "concepts": [{"value": "target generation", "support_spans": ["generate targets"]}],
            },
            "deterministic_parse": {
                "fallback": {"concept_scopes": {"efficiency": "fallback_only"}},
            },
        },
    )

    semantic_query = build_semantic_query(question, plan)
    bundle = DenseQueryBundle.from_semantic_query(question, semantic_query)

    assert bundle.raw.text == question
    assert "target generation" not in bundle.raw.text
    assert bundle.semantic is not None
    assert "target generation" in bundle.semantic.text
    assert "reviewed/path.py" not in bundle.semantic.text
    assert "fallback_only" not in bundle.semantic.text
    assert bundle.semantic.excluded_component_classes == semantic_query.excluded_component_classes

def test_t0_channel_isolation(monkeypatch):
    question = "test question"
    plan = RetrievalPlan(
        intent="algorithm_theory",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {
                "concepts": [{"value": "mock_concept", "support_spans": []}]
            }
        }
    )
    
    import os
    from pathlib import Path
    
    class MockVertex:
        def __init__(self):
            self.queries = []

        def embed_query(self, text):
            self.queries.append(text)
            return [0.1]
    
    class MockSparse:
        def query_embed(self, text):
            self.last_query = text
            class DummySparse:
                indices = __import__("numpy").array([1])
                values = __import__("numpy").array([0.1])
            yield DummySparse()
            
    class MockStorage:
        class Settings:
            collection_name = "test"
        settings = Settings()
        qdrant = type("MockQdrant", (), {"query_points": lambda *args, **kwargs: type("Hits", (), {"points": []})()})()
        def require_sparse_receipt(self, receipt):
            pass
        
    class MockPolicies:
        candidate_pool_per_channel = 10
        
    # Instead of creating a real Retriever, let's create a partial one
    # But since __init__ reads manifests, we monkeypatch `json.loads` or `Path.read_text`.
    monkeypatch.setattr(Path, "read_text", lambda self, **kwargs: '{"repositories":[],"papers":[],"web_documents":[]}')
    monkeypatch.setenv("QA_GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("GCP_LOCATION", "us-central1")
    monkeypatch.setenv("QA_QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QA_DB_URL", "sqlite:///:memory:")
    
    import panda_agent.retrieval
    monkeypatch.setattr(panda_agent.retrieval, "create_sparse_encoder", lambda root: (None, type("DummyReceipt", (), {"vector_name": "sparse"})()))
    
    retriever = Retriever(Path("."), storage=MockStorage())
    retriever.vertex = MockVertex()
    retriever.sparse = MockSparse()
    retriever.storage = MockStorage()
    retriever.policies = MockPolicies()
    retriever.sparse_vector_name = "sparse"
    
    # mock _exact, _workflow, _paper, _graph
    monkeypatch.setattr(retriever, '_exact', lambda *args, **kwargs: [])
    monkeypatch.setattr(retriever, '_workflow', lambda *args, **kwargs: [])
    monkeypatch.setattr(retriever, '_paper', lambda *args, **kwargs: [])
    monkeypatch.setattr(retriever, '_graph', lambda *args, **kwargs: [])
    
    retriever._vector(question, plan, 10)

    assert retriever.vertex.queries == [question]
    assert not hasattr(retriever, "_last_dense_query_bundle")

    assert retriever.sparse.last_query == question


def test_t0_shadow_dense_is_independent_and_separately_labelled(monkeypatch):
    question = "Where is the function defined?"
    plan = RetrievalPlan(
        intent="api",
        source_budgets={"code": 1.0},
        analysis_diagnostics={
            "analyzer_accepted_semantic_delta": {
                "concepts": [{"value": "PndTargetGenerator", "support_spans": ["function"]}],
            },
        },
    )

    class MockVertex:
        def __init__(self):
            self.queries = []

        def embed_query(self, text):
            self.queries.append(text)
            return [float(len(self.queries))]

    class MockQdrant:
        def __init__(self):
            self.calls = []

        def query_points(self, **kwargs):
            self.calls.append(kwargs)
            label = "raw" if kwargs["query"] == [1.0] else "semantic"
            return SimpleNamespace(points=[SimpleNamespace(payload={"object_id": label})])

    vertex = MockVertex()
    qdrant = MockQdrant()
    retriever = Retriever.__new__(Retriever)
    retriever.vertex = vertex
    retriever.context_sources = []
    retriever.storage = SimpleNamespace(
        settings=SimpleNamespace(collection_name="collection"), qdrant=qdrant
    )
    retriever.policies = SimpleNamespace(candidate_pool_per_channel=10)

    result = retriever.shadow_dense(question, plan=plan, limit=10)

    semantic_text = build_semantic_query(question, plan).text
    assert vertex.queries == [question, semantic_text]
    assert [call["using"] for call in qdrant.calls] == ["dense", "dense"]
    assert result["dense_queries"]["raw"]["text"] == question
    assert result["dense_queries"]["semantic"]["text"] == semantic_text
    assert result["dense_queries"]["semantic_executed"] is True
    assert result["dense_candidates"]["raw"] == [{"object_id": "raw"}]
    assert result["dense_candidates"]["semantic"] == [{"object_id": "semantic"}]


def test_t0_shadow_dense_skips_absent_semantic_stream():
    question = "How does this work?"
    plan = RetrievalPlan(
        intent="algorithm_theory",
        source_budgets={"code": 1.0},
        analysis_diagnostics={"analyzer_accepted_semantic_delta": {}},
    )

    queries = []
    qdrant_calls = []

    class MockQdrant:
        def query_points(self, **kwargs):
            qdrant_calls.append(kwargs)
            return SimpleNamespace(points=[])

    retriever = Retriever.__new__(Retriever)
    retriever.vertex = SimpleNamespace(embed_query=lambda text: queries.append(text) or [0.1])
    retriever.context_sources = []
    retriever.storage = SimpleNamespace(
        settings=SimpleNamespace(collection_name="collection"), qdrant=MockQdrant()
    )
    retriever.policies = SimpleNamespace(candidate_pool_per_channel=10)

    result = retriever.shadow_dense(question, plan=plan, limit=10)

    assert queries == [question]
    assert len(qdrant_calls) == 1
    assert result["dense_queries"]["semantic"] is None
    assert result["dense_candidates"]["semantic"] is None


def test_t0_dense_diagnostics_are_request_local_under_interleaving(monkeypatch):
    first_question = "What does the first request retrieve?"
    second_question = "What does the second request retrieve?"
    plan = RetrievalPlan(
        intent="algorithm_theory",
        source_budgets={"code": 1.0},
        analysis_diagnostics={"analyzer_accepted_semantic_delta": {}},
    )

    retriever = Retriever.__new__(Retriever)
    retriever.policies = SimpleNamespace(candidate_pool_per_channel=10, final_evidence_limit=1)
    monkeypatch.setattr(retriever, "_exact", lambda *args, **kwargs: [])
    monkeypatch.setattr(retriever, "_paper", lambda *args, **kwargs: [])
    monkeypatch.setattr(retriever, "_workflow", lambda *args, **kwargs: [])
    monkeypatch.setattr(retriever, "_graph", lambda *args, **kwargs: [])

    shared_name = "_last_" + "dense_query_bundle"
    nested_results = []
    nested = False

    def interleaving_vector(question, current_plan, limit):
        nonlocal nested
        semantic_query = build_semantic_query(question, current_plan)
        setattr(retriever, shared_name, DenseQueryBundle.from_semantic_query(question, semantic_query))
        if question == first_question and not nested:
            nested = True
            nested_results.append(retriever.retrieve(second_question, plan=plan))
        return [], [], [], semantic_query

    monkeypatch.setattr(retriever, "_vector", interleaving_vector)

    first_result = retriever.retrieve(first_question, plan=plan)

    assert nested_results[0]["dense_queries"]["raw"]["text"] == second_question
    assert first_result["dense_queries"]["raw"]["text"] == first_question
