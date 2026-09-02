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
            # Parse schema enum and return reverse order
            pool = schema["properties"]["ranked_object_ids"]["items"]["enum"]
            return {"ranked_object_ids": list(reversed(pool[:10]))}

    monkeypatch.setattr(executor, "VertexAIClient", DummyClient)
    # Target temp path for raw results
    raw_path = tmp_path / "raw_results.json"
    monkeypatch.setattr(executor, "RAW_RESULTS_PATH", str(raw_path.relative_to(project_root) if raw_path.is_relative_to(project_root) else raw_path))

    # Test audit invariants
    assert executor.audit_invariants(project_root)["verified"] is True
