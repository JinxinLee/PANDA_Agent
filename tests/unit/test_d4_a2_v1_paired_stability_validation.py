"""Unit tests for PANDA Agent D4-A2-V1 Paired Retrieval Stability and Variance Attribution Validation.

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
import d4_a2_v1_paired_stability_validation as d4_a2_v1


# ---------------------------------------------------------------------------
# 1. n022 Query Identity and Batch-1 Non-Trigger Verification
# ---------------------------------------------------------------------------

def test_n022_query_identity_exact():
    """Verify n022 query text, split, intent, and critical evidence group from novel_dev.yaml."""
    novel_ds = load_gold_dataset(_PROJECT_ROOT / d4_a2_v1.NOVEL_DEV_PATH)
    n022_q = next((q for q in novel_ds.questions if q.id == d4_a2_v1.CASE_ID), None)
    assert n022_q is not None, f"Case {d4_a2_v1.CASE_ID} not found in {d4_a2_v1.NOVEL_DEV_PATH}"

    assert n022_q.split == "novel_dev"
    assert n022_q.intent == "data_flow"
    assert n022_q.expected_status.value == "answered"
    assert n022_q.query.strip() == d4_a2_v1.EXACT_QUERY.strip()

    e2_group = next((g for g in n022_q.required_evidence_groups if g.group_id == d4_a2_v1.TARGET_EVIDENCE_GROUP_ID), None)
    assert e2_group is not None, f"Group {d4_a2_v1.TARGET_EVIDENCE_GROUP_ID} missing"
    assert e2_group.role == d4_a2_v1.TARGET_ROLE
    assert e2_group.critical is True

    # Selector points to poca_step2_analysis.py
    sel = e2_group.any_of[0]
    assert sel.source_id == "restgas_determination"
    assert sel.path == d4_a2_v1.TARGET_EVIDENCE_PATH


def test_batch1_rules_do_not_match_n022():
    """Verify that neither event_poca_handoff nor restgas_profile_workflow triggers on n022."""
    qe = load_query_expansions(_PROJECT_ROOT / d4_a2_v1.CONFIG_QUERY_EXPANSIONS_PATH)
    lowered_q = d4_a2_v1.EXACT_QUERY.casefold()

    matched_rules = [
        r.rule_id
        for r in qe.rules
        if any(str(tr).casefold() in lowered_q for tr in r.triggers)
    ]
    assert "event_poca_handoff" not in matched_rules
    assert "restgas_profile_workflow" not in matched_rules
    assert matched_rules == []


# ---------------------------------------------------------------------------
# 2. Manifest and Preregistration Invariants
# ---------------------------------------------------------------------------

def test_manifest_phase_p_and_phase_r_slots():
    """Verify exactly 8 Phase P slots and 16 Phase R cells in manifest."""
    manifest = json.loads((_PROJECT_ROOT / d4_a2_v1.MANIFEST_PATH).read_text(encoding="utf-8"))

    slots_p = manifest["phase_p_slots_8"]
    assert len(slots_p) == 8
    for i, s in enumerate(slots_p, start=1):
        assert s["draw_index"] == i
        assert s["case_id"] == "n022"
        assert s["status"] == "NOT_EXECUTED"

    cells_r = manifest["phase_r_cells_16"]
    assert len(cells_r) == 16
    for i, c in enumerate(cells_r, start=1):
        assert c["cell_index"] == i
        assert c["case_id"] == "n022"
        assert c["status"] == "NOT_EXECUTED"


def test_balanced_arm_schedule_alternation():
    """Verify exact alternating schedule across the 16 downstream cells."""
    manifest = json.loads((_PROJECT_ROOT / d4_a2_v1.MANIFEST_PATH).read_text(encoding="utf-8"))
    cells = manifest["phase_r_cells_16"]

    expected_schedule = [
        (1, 1, "BEFORE_COMPAT"),
        (2, 1, "AFTER_BATCH1_REPLACEMENT"),
        (3, 2, "AFTER_BATCH1_REPLACEMENT"),
        (4, 2, "BEFORE_COMPAT"),
        (5, 3, "BEFORE_COMPAT"),
        (6, 3, "AFTER_BATCH1_REPLACEMENT"),
        (7, 4, "AFTER_BATCH1_REPLACEMENT"),
        (8, 4, "BEFORE_COMPAT"),
        (9, 5, "BEFORE_COMPAT"),
        (10, 5, "AFTER_BATCH1_REPLACEMENT"),
        (11, 6, "AFTER_BATCH1_REPLACEMENT"),
        (12, 6, "BEFORE_COMPAT"),
        (13, 7, "BEFORE_COMPAT"),
        (14, 7, "AFTER_BATCH1_REPLACEMENT"),
        (15, 8, "AFTER_BATCH1_REPLACEMENT"),
        (16, 8, "BEFORE_COMPAT"),
    ]

    assert len(d4_a2_v1.SCHEDULE) == 16
    for sched, exp, cell in zip(d4_a2_v1.SCHEDULE, expected_schedule, cells):
        exp_c_idx, exp_p_idx, exp_arm = exp
        assert sched["cell_index"] == exp_c_idx
        assert sched["plan_index"] == exp_p_idx
        assert sched["arm"] == exp_arm
        assert cell["cell_index"] == exp_c_idx
        assert cell["plan_index"] == exp_p_idx
        assert cell["arm"] == exp_arm


def test_preregistration_integrity():
    """Verify preregistration fields and verdict precedence ladder."""
    prereg = json.loads((_PROJECT_ROOT / d4_a2_v1.PREREGISTRATION_PATH).read_text(encoding="utf-8"))
    assert prereg["checkpoint"] == "D4-A2-V1"
    assert prereg["starting_head"] == d4_a2_v1.STARTING_HEAD
    assert prereg["scientific_scope"]["case_id"] == "n022"
    assert prereg["scientific_scope"]["query"] == d4_a2_v1.EXACT_QUERY
    assert prereg["outcome_exposure_state"]["D4_A2_V1_OUTCOME_EXPOSURE"] == "NOT_STARTED"

    ladder = prereg["verdict_precedence"]
    assert len(ladder) == 7
    assert ladder[0]["level"] == 1
    assert "INVALID" in ladder[0]["verdict"]
    assert ladder[1]["level"] == 2
    assert "FAIL" in ladder[1]["verdict"]
    assert ladder[6]["level"] == 7
    assert "PASS" in ladder[6]["verdict"]


# ---------------------------------------------------------------------------
# 3. Shared-Plan Adapter Tests
# ---------------------------------------------------------------------------

def _create_sample_plan() -> RetrievalPlan:
    return RetrievalPlan(
        intent="data_flow",
        target_repositories=["restgas_determination", "pandaroot"],
        resolved_versions={"restgas_determination": "v1", "pandaroot": "v1"},
        version_conflicts=[],
        symbols=[],
        concepts=["restgas analysis", "event vertex", "worker step", "fitted vertex"],
        concept_scopes={},
        source_budgets={"code": 0.5, "workflow": 0.5},
        required_source_types=["code", "workflow"],
        paper_page_hints={},
        resolved_aliases={},
        premise_corrections=[],
        analysis_diagnostics={},
    )


def test_frozen_plan_adapter_injects_exact_plan_and_records_call():
    """Verify that frozen_plan_context supplies the frozen plan and intercepts analyze."""
    mock_retriever = MagicMock()
    original_analyze = MagicMock(return_value="ORIGINAL_RETURN")
    mock_retriever.analyze = original_analyze

    sample_plan = _create_sample_plan()

    with d4_a2_v1.frozen_plan_context(mock_retriever, sample_plan) as calls:
        res = mock_retriever.analyze(d4_a2_v1.EXACT_QUERY)
        assert res.model_dump() == sample_plan.model_dump()
        assert len(calls) == 1
        assert calls[0] == d4_a2_v1.EXACT_QUERY
        assert original_analyze.call_count == 0

    assert mock_retriever.analyze == original_analyze
    res_orig = mock_retriever.analyze("test")
    assert res_orig == "ORIGINAL_RETURN"


def test_frozen_plan_adapter_restoration_on_exception():
    """Verify that frozen_plan_context restores original analyze even when an exception is raised."""
    mock_retriever = MagicMock()
    original_analyze = MagicMock(return_value="ORIGINAL_RETURN")
    mock_retriever.analyze = original_analyze

    sample_plan = _create_sample_plan()

    with pytest.raises(ValueError, match="simulated cell error"):
        with d4_a2_v1.frozen_plan_context(mock_retriever, sample_plan):
            mock_retriever.analyze("q")
            raise ValueError("simulated cell error")

    assert mock_retriever.analyze == original_analyze


def test_frozen_plan_adapter_zero_provider_calls():
    """Verify that calling mocked analyze makes zero provider calls on vertex client."""
    mock_retriever = MagicMock()
    mock_vertex = MagicMock()
    mock_retriever.vertex = mock_vertex

    sample_plan = _create_sample_plan()

    with d4_a2_v1.frozen_plan_context(mock_retriever, sample_plan):
        plan = mock_retriever.analyze(d4_a2_v1.EXACT_QUERY)
        assert "worker step" in plan.concepts

    assert mock_vertex.generate_json.call_count == 0


def test_canonical_plan_equality_check():
    """Verify that canonical model_dump equality holds when plan is serialized/deserialized."""
    sample_plan = _create_sample_plan()

    dump1 = sample_plan.model_dump(mode="json")
    reconstructed = RetrievalPlan.model_validate(dump1)
    dump2 = reconstructed.model_dump(mode="json")
    assert dump1 == dump2


# ---------------------------------------------------------------------------
# 4. In-Memory Component Mask Parity Tests
# ---------------------------------------------------------------------------

def test_batch1_in_memory_mask_parity():
    """Verify in-memory mask suppresses Batch-1 locators while preserving triggers/repos/concepts."""
    original_qe = load_query_expansions(_PROJECT_ROOT / d4_a2_v1.CONFIG_QUERY_EXPANSIONS_PATH)
    masked_qe = d4_a1.apply_batch1_in_memory_mask(original_qe)

    ep_orig = next(r for r in original_qe.rules if r.rule_id == "event_poca_handoff")
    ep_mask = next(r for r in masked_qe.rules if r.rule_id == "event_poca_handoff")
    assert len(ep_orig.symbols) == 4
    assert len(ep_mask.symbols) == 0
    assert ep_mask.paper_page_hints == {}
    assert ep_mask.triggers == ep_orig.triggers
    assert ep_mask.repositories == ep_orig.repositories
    assert ep_mask.concepts == ep_orig.concepts

    rg_orig = next(r for r in original_qe.rules if r.rule_id == "restgas_profile_workflow")
    rg_mask = next(r for r in masked_qe.rules if r.rule_id == "restgas_profile_workflow")
    assert len(rg_orig.symbols) == 5
    assert len(rg_mask.symbols) == 0
    assert rg_mask.triggers == rg_orig.triggers
    assert rg_mask.repositories == rg_orig.repositories
    assert rg_mask.concepts == rg_orig.concepts


# ---------------------------------------------------------------------------
# 5. Pipeline Constants and Authorities
# ---------------------------------------------------------------------------

def test_pipeline_constants_and_authorities():
    """Verify frozen constants: K=3, pool=30, selectivity 8/4, RRF weights, model and prompts."""
    assert d4_a2_v1.EXPECTED_ADMISSION_BUDGET_K == 3
    assert d4_a2_v1.EXPECTED_SELECTIVITY_CAP == 8
    assert d4_a2_v1.EXPECTED_PER_ORIGIN_CAP == 4
    assert d4_a2_v1.EXPECTED_RERANK_POOL_SIZE == 30
    assert a6_p1.WEIGHTS == d4_a2_v1.EXPECTED_RRF_WEIGHTS
    assert a5_r2.SELECTIVITY_CAP == 8
    assert a5_r2.PER_ORIGIN_CAP == 4
    assert a6_p1.RERANK_POOL_SIZE == 30

    assert d4_a2_v1.EXPECTED_MODEL == "gemini-3.8-flash"
    assert d4_a2_v1.EXPECTED_EMBEDDING_MODEL == "gemini-embedding-2"
    assert d4_a2_v1.EXPECTED_TEMPERATURE == 0.0
    assert d4_a2_v1.EXPECTED_VERTEX_LOCATION == "global"

    assert len(QUERY_ANALYZER_SYSTEM_PROMPT) > 50
    assert len(RERANK_SYSTEM_PROMPT) > 50


# ---------------------------------------------------------------------------
# 6. Phenotype Classification and Signatures
# ---------------------------------------------------------------------------

def test_r1_concept_phenotype_classification():
    """Verify classification of R1 concepts: COMPLETE, PARTIAL, ABSENT."""
    assert d4_a2_v1.classify_r1_concept_phenotype(["worker step", "fitted vertex", "reprocessing"]) == "R1_FEATURE_COMPLETE"
    assert d4_a2_v1.classify_r1_concept_phenotype(["WORKER STEP", "FITTED VERTEX"]) == "R1_FEATURE_COMPLETE"
    assert d4_a2_v1.classify_r1_concept_phenotype(["worker step", "reprocessing"]) == "R1_FEATURE_PARTIAL"
    assert d4_a2_v1.classify_r1_concept_phenotype(["fitted vertex"]) == "R1_FEATURE_PARTIAL"
    assert d4_a2_v1.classify_r1_concept_phenotype(["two-step POCA workflow", "reprocessing"]) == "R1_FEATURE_ABSENT"


def test_plan_signature_determinism():
    """Verify plan signature is deterministic and ignores transient metadata."""
    plan1 = {
        "intent": "data_flow",
        "target_repositories": ["pandaroot", "restgas_determination"],
        "symbols": ["symA"],
        "concepts": ["fitted vertex", "worker step"],
        "required_source_types": ["code"],
        "paper_page_hints": {"li_2026": [131]},
        "concept_scopes": {},
    }
    plan2 = copy.deepcopy(plan1)
    plan2["timestamp"] = "2026-09-03T12:00:00"
    plan2["token_usage"] = 1234

    sig1, _ = d4_a2_v1.compute_plan_signature(plan1)
    sig2, _ = d4_a2_v1.compute_plan_signature(plan2)
    assert sig1 == sig2


# ---------------------------------------------------------------------------
# 7. Protected Dataset Guard
# ---------------------------------------------------------------------------

def test_protected_dataset_guard():
    """Verify zero novel_validation and novel_holdout runs in manifest and preregistration."""
    manifest = json.loads((_PROJECT_ROOT / d4_a2_v1.MANIFEST_PATH).read_text(encoding="utf-8"))
    prereg = json.loads((_PROJECT_ROOT / d4_a2_v1.PREREGISTRATION_PATH).read_text(encoding="utf-8"))

    m_acc = manifest["pre_exposure_accounting"]
    assert m_acc["novel_validation_runs"] == 0
    assert m_acc["novel_holdout_runs"] == 0
    assert m_acc["protected_dataset_access"] == 0

    p_acc = prereg["planned_formal_call_accounting"]
    assert p_acc["novel_validation_runs"] == 0
    assert p_acc["novel_holdout_runs"] == 0
    assert p_acc["protected_dataset_access"] == 0
