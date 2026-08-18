import pytest
from panda_agent.retrieval import build_semantic_query, Retriever
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
        def embed_query(self, text):
            self.last_query = text
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
    
    assert retriever.vertex.last_query != question
    assert "mock_concept" in retriever.vertex.last_query
    
    assert retriever.sparse.last_query == question
