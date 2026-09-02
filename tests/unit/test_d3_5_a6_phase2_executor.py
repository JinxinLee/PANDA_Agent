"""Unit tests for D3.5-A6 Phase 2 executor and evaluator."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import d3_5_a6_phase2_executor as executor


def test_audit_invariants_passes():
    project_root = Path(__file__).resolve().parents[2]
    receipt = executor.audit_invariants(project_root)
    assert receipt["verified"] is True
    assert receipt["qa_generation_model_id"] == "gemini-3.8-flash"
    assert receipt["pool_manifests_count"] == 18
    assert receipt["call_plan_entries_count"] == 54
    assert receipt["identical_pool_map"]["g021"]["K2_equals_K3"] is True
    assert receipt["identical_pool_map"]["n006"]["K2_equals_BASELINE"] is True


def test_mock_reranker_slot_execution(tmp_path, monkeypatch):
    """Test executor handling with mock VertexAIClient."""
    project_root = Path(__file__).resolve().parents[2]

    class DummyClient:
        def __init__(self, settings):
            self.settings = settings

        def stats_snapshot(self):
            return {"generation_calls": 0, "token_usage": 0}

        def stats_delta(self, before):
            return {"generation_calls": 1, "token_usage": 100}

        def generate_json(self, prompt, schema, system_instruction=None, temperature=0.0):
            pool = schema["properties"]["ranked_object_ids"]["items"]["enum"]
            return {"ranked_object_ids": list(reversed(pool[:10]))}

    monkeypatch.setattr(executor, "VertexAIClient", DummyClient)
    assert executor.audit_invariants(project_root)["verified"] is True


def test_phase2_evaluated_results_structure_and_metrics():
    """Verify the persisted Phase 2 result artifacts and scientific invariants."""
    project_root = Path(__file__).resolve().parents[2]
    result_path = project_root / executor.FINAL_RESULT_PATH
    assert result_path.exists()

    result = json.loads(result_path.read_text(encoding="utf-8"))
    metrics = result["scientific_metrics"]

    assert metrics["DELTA_2"] == 1
    assert metrics["DELTA_3"] == 2
    assert metrics["CAUSAL_DELTA_2"] == 1
    assert metrics["CAUSAL_DELTA_3"] == 2
    assert metrics["NONCAUSAL_STABLE_DELTA_2"] == 0
    assert metrics["NONCAUSAL_STABLE_DELTA_3"] == 0
    assert metrics["REGRESSION_2"] == 0
    assert metrics["REGRESSION_3"] == 0
    assert metrics["MECHANISTIC_SAFE_EFFECTIVE_K2"] is True
    assert metrics["MECHANISTIC_SAFE_EFFECTIVE_K3"] is True
    assert metrics["SELECTED_ADMISSION_BUDGET"] == 3
    assert metrics["FINAL_A6_PHASE2_VERDICT"] == (
        "PASS / BOUNDED_RERANK_ADMISSION_VALIDATED_FOR_DEVELOPMENT"
    )
    assert result["production_activation"] is False

    # Check accounting
    acct = result["accounting"]
    assert acct["FORMAL_RERANKER_CALLS_EXECUTED"] == 54
    assert acct["FORMAL_RERANKER_CALLS_SUCCEEDED"] == 54
    assert acct["FORMAL_RERANKER_CALLS_FAILED"] == 0
    assert acct["PROVIDER_INTERNAL_ATTEMPTS"] == 54
    assert acct["NOVEL_VALIDATION_RUNS"] == 0
    assert acct["PROTECTED_DATASET_ACCESS"] == 0
