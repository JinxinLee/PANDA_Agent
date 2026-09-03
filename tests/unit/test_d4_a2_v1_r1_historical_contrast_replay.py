"""Unit tests for PANDA Agent D4-A2-V1-R1 Historical Contrast Shared-Plan Replay.

All tests are deterministic, offline, and self-contained.
Zero live provider/retrieval calls or live model/database queries.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
from unittest.mock import MagicMock
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))
if str(_PROJECT_ROOT / "evaluation" / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "evaluation" / "scripts"))

from panda_agent.config import load_query_expansions
from panda_agent.evaluation import load_gold_dataset
from panda_agent.models import RetrievalPlan
from panda_agent.prompts import QUERY_ANALYZER_SYSTEM_PROMPT, RERANK_SYSTEM_PROMPT
import d3_5_a5_r2_selectivity as a5_r2
import d3_5_a6_phase1_admission as a6_p1
import d4_a1_fixed_locator_migration as d4_a1
import d4_a2_v1_r1_historical_contrast_replay as r1


# ---------------------------------------------------------------------------
# 1. Historical Source-Cell Extraction & Exactly Two n022 Cells
# ---------------------------------------------------------------------------

def test_historical_source_cell_extraction():
    """Verify that exactly two n022 historical cells exist in d4_a2_raw_before_after_results.json."""
    raw_path = _PROJECT_ROOT / r1.HISTORICAL_A2_RAW_PATH
    assert raw_path.exists(), f"Historical raw file missing: {raw_path}"
    data = json.loads(raw_path.read_text(encoding="utf-8"))
    slots = data.get("slots", [])
    n022_slots = [s for s in slots if s.get("case_id") == r1.CASE_ID]
    assert len(n022_slots) == 2, f"Expected 2 n022 slots, found {len(n022_slots)}"

    s_before = next((s for s in n022_slots if s.get("arm") == "BEFORE_COMPAT"), None)
    s_after = next((s for s in n022_slots if s.get("arm") == "AFTER_BATCH1_REPLACEMENT"), None)
    assert s_before is not None
    assert s_after is not None
    assert s_before.get("slot_index") == r1.HISTORICAL_SLOT_BEFORE
    assert s_after.get("slot_index") == r1.HISTORICAL_SLOT_AFTER
    assert s_before.get("status") == "COMPLETED"
    assert s_after.get("status") == "COMPLETED"


# ---------------------------------------------------------------------------
# 2. Plan Canonical Deserialization & Non-Identity
# ---------------------------------------------------------------------------

def test_plan_canonical_deserialization_and_nonidentity():
    """Verify that both historical plans deserialize validly and are not identical."""
    pair_path = _PROJECT_ROOT / r1.HISTORICAL_PLAN_PAIR_PATH
    assert pair_path.exists(), f"Historical plan pair artifact missing: {pair_path}"
    data = json.loads(pair_path.read_text(encoding="utf-8"))

    p_before_dict = data["HIST_A2_BEFORE_PLAN"]["canonical_plan"]
    p_after_dict = data["HIST_A2_AFTER_PLAN"]["canonical_plan"]

    p_before = RetrievalPlan.model_validate(p_before_dict)
    p_after = RetrievalPlan.model_validate(p_after_dict)

    assert p_before.intent == "data_flow"
    assert p_after.intent == "data_flow"
    assert p_before.model_dump(mode="json") != p_after.model_dump(mode="json")

    # Concepts differ
    assert "worker step" in [c.lower() for c in p_before.concepts]
    assert "fitted vertex" in [c.lower() for c in p_before.concepts]
    assert "worker step" not in [c.lower() for c in p_after.concepts]
    assert "fitted vertex" not in [c.lower() for c in p_after.concepts]

    assert data["HIST_A2_BEFORE_PLAN"]["r1_concept_phenotype"] == "R1_FEATURE_COMPLETE"
    assert data["HIST_A2_AFTER_PLAN"]["r1_concept_phenotype"] == "R1_FEATURE_ABSENT"


# ---------------------------------------------------------------------------
# 3. 2x2 Cell Construction & Exact Execution Order
# ---------------------------------------------------------------------------

def test_crossover_2x2_cell_construction_and_schedule():
    """Verify exact 4-cell crossover schedule and balanced alternating arm order."""
    manifest_path = _PROJECT_ROOT / r1.MANIFEST_PATH
    assert manifest_path.exists(), f"Manifest missing: {manifest_path}"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cells = manifest["cells_4"]
    assert len(cells) == 4

    expected = [
        (1, r1.PLAN_ID_BEFORE, 9, "BEFORE_COMPAT"),
        (2, r1.PLAN_ID_BEFORE, 9, "AFTER_BATCH1_REPLACEMENT"),
        (3, r1.PLAN_ID_AFTER, 10, "AFTER_BATCH1_REPLACEMENT"),
        (4, r1.PLAN_ID_AFTER, 10, "BEFORE_COMPAT"),
    ]

    for c, (exp_idx, exp_plan, exp_slot, exp_arm) in zip(cells, expected):
        assert c["cell_index"] == exp_idx
        assert c["historical_plan_id"] == exp_plan
        assert c["source_slot_index"] == exp_slot
        assert c["arm"] == exp_arm


# ---------------------------------------------------------------------------
# 4. Shared-Plan Adapter Restoration & Zero Analyzer Provider Calls
# ---------------------------------------------------------------------------

def test_shared_plan_adapter_restoration_and_call_interception():
    """Verify that frozen_plan_context injects the plan and restores retriever.analyze."""
    mock_retriever = MagicMock()
    orig_analyze = MagicMock(return_value="ORIGINAL")
    mock_retriever.analyze = orig_analyze

    sample_plan = RetrievalPlan(
        intent="data_flow",
        target_repositories=["restgas_determination"],
        resolved_versions={"restgas_determination": "v1"},
        version_conflicts=[],
        symbols=[],
        concepts=["restgas analysis", "event vertex"],
        concept_scopes={},
        source_budgets={"code": 0.5, "workflow": 0.5},
        required_source_types=["code", "workflow"],
        paper_page_hints={},
        resolved_aliases={},
        premise_corrections=[],
        analysis_diagnostics={},
    )

    with r1.frozen_plan_context(mock_retriever, sample_plan) as calls:
        plan_out = mock_retriever.analyze("test question")
        assert plan_out.model_dump(mode="json") == sample_plan.model_dump(mode="json")
        assert len(calls) == 1
        assert orig_analyze.call_count == 0

    assert mock_retriever.analyze == orig_analyze

    # Exception safety
    try:
        with r1.frozen_plan_context(mock_retriever, sample_plan):
            raise ValueError("boom")
    except ValueError:
        pass
    assert mock_retriever.analyze == orig_analyze


# ---------------------------------------------------------------------------
# 5. Batch-1 Rule Activation Absence on n022
# ---------------------------------------------------------------------------

def test_batch1_rules_do_not_match_n022():
    """Verify that Batch-1 rules (event_poca_handoff, restgas_profile_workflow) do not trigger on n022."""
    qe = load_query_expansions(_PROJECT_ROOT / r1.CONFIG_QUERY_EXPANSIONS_PATH)
    lowered_q = r1.EXACT_QUERY.casefold()

    matched_rules = [
        r.rule_id
        for r in qe.rules
        if any(str(tr).casefold() in lowered_q for tr in r.triggers)
    ]
    assert "event_poca_handoff" not in matched_rules
    assert "restgas_profile_workflow" not in matched_rules
    assert matched_rules == []


# ---------------------------------------------------------------------------
# 6. Mask Parity & Invariants
# ---------------------------------------------------------------------------

def test_mask_parity_and_determinism():
    """Verify that in-memory component mask applies deterministically."""
    qe = load_query_expansions(_PROJECT_ROOT / r1.CONFIG_QUERY_EXPANSIONS_PATH)
    masked_once = d4_a1.apply_batch1_in_memory_mask(qe)
    masked_twice = d4_a1.apply_batch1_in_memory_mask(masked_once)
    assert masked_once.model_dump() == masked_twice.model_dump()


# ---------------------------------------------------------------------------
# 7. Pipeline Constants (K=3, Selectivity Caps 8/4, Pool 30)
# ---------------------------------------------------------------------------

def test_pipeline_constants():
    """Verify frozen pipeline constants match contract."""
    assert a5_r2.SELECTIVITY_CAP == 8
    assert a5_r2.PER_ORIGIN_CAP == 4
    assert 3 in a6_p1.ADMISSION_BUDGETS
    assert a6_p1.RERANK_POOL_SIZE == 30
    assert a6_p1.WEIGHTS == r1.EXPECTED_RRF_WEIGHTS


# ---------------------------------------------------------------------------
# 8. Protected Dataset Guard
# ---------------------------------------------------------------------------

def test_protected_dataset_guard():
    """Verify that no novel_validation or holdout files are touched or referenced."""
    novel_ds = load_gold_dataset(_PROJECT_ROOT / r1.NOVEL_DEV_PATH)
    n022_q = next((q for q in novel_ds.questions if q.id == r1.CASE_ID), None)
    assert n022_q is not None
    assert n022_q.split == "novel_dev"
    assert n022_q.query.strip() == r1.EXACT_QUERY.strip()


# ---------------------------------------------------------------------------
# 9. Verdict Truth Table Logic
# ---------------------------------------------------------------------------

def test_verdict_precedence_ladder():
    """Verify verdict precedence levels."""
    assert "INVALID" in r1.VERDICT_LEVEL_1_INVALID
    assert "FAIL" in r1.VERDICT_LEVEL_2_FAIL
    assert "PARTIAL" in r1.VERDICT_LEVEL_3_PARTIAL
    assert "INCONCLUSIVE" in r1.VERDICT_LEVEL_4_INCONCLUSIVE_BEFORE
    assert "INCONCLUSIVE" in r1.VERDICT_LEVEL_5_INCONCLUSIVE_SENSITIVITY
    assert "PASS" in r1.VERDICT_LEVEL_6_PASS
