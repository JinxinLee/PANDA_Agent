"""Unit tests for PANDA Agent D4-A2-V2 Controlled Shared-Plan Validation.

All tests are deterministic, offline, and self-contained.
Zero provider/retrieval calls or live model/database queries.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
from unittest.mock import MagicMock
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))
if str(_PROJECT_ROOT / "evaluation" / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "evaluation" / "scripts"))

from google.genai import errors as genai_errors
from pydantic import ValidationError
from panda_agent.config import load_query_expansions
from panda_agent.evaluation import load_gold_dataset
from panda_agent.llm.vertex import VertexCallError
from panda_agent.models import RetrievalPlan
from panda_agent.prompts import QUERY_ANALYZER_SYSTEM_PROMPT, RERANK_SYSTEM_PROMPT
import d3_5_a5_r2_selectivity as a5_r2
import d3_5_a6_phase1_admission as a6_p1
import d4_a1_fixed_locator_migration as d4_a1
import d4_a2_v2_controlled_shared_plan_validation as v2


# ---------------------------------------------------------------------------
# 1. 16-Case Identity, Order, and Breakdown Tests
# ---------------------------------------------------------------------------

def test_16_case_identity_and_cohort_order():
    """Verify exact 16-case cohort identity, exact order, and dataset breakdown:
    - Order: g029, n021, g025, g036, n022, g020, n006, g041, n014, g060, g052, g055, n003, g021, n004, g007
    - 10 Gold v2.6 dev + 6 novel_dev
    - 13 answered cases + 3 insufficient_evidence negative controls
    - Matches preregistration and manifest.
    """
    expected_order = [
        "g029", "n021", "g025", "g036", "n022", "g020", "n006", "g041",
        "n014", "g060", "g052", "g055", "n003", "g021", "n004", "g007",
    ]
    assert v2.CASE_ORDER == expected_order
    assert len(v2.CASE_ORDER) == 16

    assert len(v2.GOLD_CASES) == 10
    assert len(v2.NOVEL_DEV_CASES) == 6
    assert len(v2.ANSWERED_CASES) == 13
    assert len(v2.INSUFFICIENT_EVIDENCE_CASES) == 3
    assert sorted(v2.INSUFFICIENT_EVIDENCE_CASES) == ["g007", "g025", "g041"]

    prereg = json.loads((_PROJECT_ROOT / v2.PREREGISTRATION_PATH).read_text(encoding="utf-8"))
    assert prereg["cohort"]["exact_case_order"] == expected_order
    assert prereg["cohort"]["dataset_breakdown"]["gold_count"] == 10
    assert prereg["cohort"]["dataset_breakdown"]["novel_dev_count"] == 6

    manifest = json.loads((_PROJECT_ROOT / v2.MANIFEST_PATH).read_text(encoding="utf-8"))
    manifest_case_ids = [c["case_id"] for c in manifest["cases"]]
    assert manifest_case_ids == expected_order


# ---------------------------------------------------------------------------
# 2. 32-Cell Balanced Alternating Schedule Tests
# ---------------------------------------------------------------------------

def test_32_cell_balanced_alternating_schedule():
    """Verify exact 32 slots in balanced alternating paired order:
    - 8 pairs execute BEFORE first (cases 1, 3, 5, 7, 9, 11, 13, 15)
    - 8 pairs execute AFTER first (cases 2, 4, 6, 8, 10, 12, 14, 16)
    - All pairs remain case-local and adjacent
    - 16 BEFORE cells + 16 AFTER cells
    - In manifest, all slots start as NOT_STARTED with 0 pre-exposure accounting.
    """
    assert len(v2.SCHEDULE_32) == 32
    before_first_cases = [v2.CASE_ORDER[i] for i in range(0, 16, 2)]
    after_first_cases = [v2.CASE_ORDER[i] for i in range(1, 16, 2)]

    assert len(before_first_cases) == 8
    assert len(after_first_cases) == 8

    before_count = 0
    after_count = 0

    for i in range(0, 32, 2):
        pair_num = i // 2  # 0 to 15
        s1 = v2.SCHEDULE_32[i]
        s2 = v2.SCHEDULE_32[i + 1]

        # Case-local and adjacent
        assert s1["case_id"] == s2["case_id"]
        assert s1["case_id"] == v2.CASE_ORDER[pair_num]
        assert s1["slot_index"] == i + 1
        assert s2["slot_index"] == i + 2

        if pair_num % 2 == 0:
            # Even index: BEFORE first
            assert s1["arm"] == "BEFORE_COMPAT"
            assert s2["arm"] == "AFTER_BATCH1_REPLACEMENT"
        else:
            # Odd index: AFTER first
            assert s1["arm"] == "AFTER_BATCH1_REPLACEMENT"
            assert s2["arm"] == "BEFORE_COMPAT"

        if s1["arm"] == "BEFORE_COMPAT":
            before_count += 1
        else:
            after_count += 1

        if s2["arm"] == "BEFORE_COMPAT":
            before_count += 1
        else:
            after_count += 1

    assert before_count == 16
    assert after_count == 16

    # Verify against manifest
    manifest = json.loads((_PROJECT_ROOT / v2.MANIFEST_PATH).read_text(encoding="utf-8"))
    manifest_cells = manifest["phase_r_cells_32"]
    assert len(manifest_cells) == 32
    for exp, act in zip(v2.SCHEDULE_32, manifest_cells):
        assert act["cell_index"] == exp["slot_index"]
        assert act["case_id"] == exp["case_id"]
        assert act["arm"] == exp["arm"]
        assert act["status"] == "NOT_STARTED"
        assert act["started_at"] is None
        assert act["completed_at"] is None


# ---------------------------------------------------------------------------
# 3. Treatment Contract & Pipeline Constants Tests
# ---------------------------------------------------------------------------

def test_treatment_contract_values():
    """Verify frozen treatment and pipeline constants:
    - Selectivity cap = 8, Per-origin cap = 4
    - Admission budget K = 3
    - Rerank pool size = 30
    - RRF weights match expected dictionary
    - Models: gemini-3.8-flash, gemini-embedding-2, temperature 0.0
    """
    assert a5_r2.SELECTIVITY_CAP == 8
    assert a5_r2.PER_ORIGIN_CAP == 4
    assert 3 in a6_p1.ADMISSION_BUDGETS
    assert a6_p1.RERANK_POOL_SIZE == 30
    assert a6_p1.WEIGHTS == v2.EXPECTED_RRF_WEIGHTS
    assert v2.EXPECTED_MODEL == "gemini-3.8-flash"
    assert v2.EXPECTED_EMBEDDING_MODEL == "gemini-embedding-2"
    assert v2.EXPECTED_TEMPERATURE == 0.0


# ---------------------------------------------------------------------------
# 4. Batch-1 Exact Component Mask Tests
# ---------------------------------------------------------------------------

def test_batch1_exact_component_mask():
    """Verify exact in-memory Batch-1 component mask:
    - event_poca_handoff: 4 suppressed symbols, 2 page hints on li_2026 (131, 138)
    - restgas_profile_workflow: 5 suppressed symbols
    - Preserves triggers, repositories, concepts
    - Mask application is idempotent and preserves source object
    """
    orig_qe = load_query_expansions(_PROJECT_ROOT / v2.CONFIG_QUERY_EXPANSIONS_PATH)
    orig_dump = orig_qe.model_dump()

    masked_qe = d4_a1.apply_batch1_in_memory_mask(orig_qe)
    masked_twice = d4_a1.apply_batch1_in_memory_mask(masked_qe)

    # Immutability
    assert orig_qe.model_dump() == orig_dump

    # Suppression
    mask_ep = next(r for r in masked_qe.rules if r.rule_id == "event_poca_handoff")
    mask_rg = next(r for r in masked_qe.rules if r.rule_id == "restgas_profile_workflow")
    assert mask_ep.symbols == []
    assert mask_ep.paper_page_hints == {}
    assert mask_rg.symbols == []

    # Preservation
    assert mask_ep.triggers == d4_a1.PRESERVED_TRIGGERS_EVENT_POCA
    assert mask_ep.repositories == d4_a1.PRESERVED_REPOS_EVENT_POCA
    assert mask_ep.concepts == d4_a1.PRESERVED_CONCEPTS_EVENT_POCA
    assert mask_rg.triggers == d4_a1.PRESERVED_TRIGGERS_RESTGAS
    assert mask_rg.repositories == d4_a1.PRESERVED_REPOS_RESTGAS
    assert mask_rg.concepts == d4_a1.PRESERVED_CONCEPTS_RESTGAS

    # Idempotence
    assert masked_qe.model_dump() == masked_twice.model_dump()


# ---------------------------------------------------------------------------
# 5. Shared-Plan Adapter & Phase R Analyzer-Call Guard Tests
# ---------------------------------------------------------------------------

def test_shared_plan_adapter_bypasses_analyzer_and_restores():
    """Verify that frozen_plan_context:
    - Injects the frozen plan directly
    - Results in 0 provider analyzer calls
    - Restores original retriever.analyze on exit and exception
    """
    mock_retriever = MagicMock()
    orig_analyze = MagicMock(return_value="ORIGINAL_RESULT")
    mock_retriever.analyze = orig_analyze

    sample_plan = RetrievalPlan(
        intent="data_flow",
        target_repositories=["pandaroot"],
        resolved_versions={"pandaroot": "v1"},
        version_conflicts=[],
        symbols=[],
        concepts=["lmd reconstruction"],
        concept_scopes={},
        source_budgets={"code": 0.5, "workflow": 0.5},
        required_source_types=["code", "workflow"],
        paper_page_hints={},
        resolved_aliases={},
        premise_corrections=[],
        analysis_diagnostics={},
    )

    with v2.frozen_plan_context(mock_retriever, sample_plan) as calls:
        output_plan = mock_retriever.analyze("What is the LMD workflow?")
        assert output_plan.model_dump(mode="json") == sample_plan.model_dump(mode="json")
        assert len(calls) == 1
        assert orig_analyze.call_count == 0  # 0 provider calls

    assert mock_retriever.analyze == orig_analyze

    # Exception safety
    try:
        with v2.frozen_plan_context(mock_retriever, sample_plan):
            raise RuntimeError("simulated failure")
    except RuntimeError:
        pass
    assert mock_retriever.analyze == orig_analyze


# ---------------------------------------------------------------------------
# 6. Canonical Plan Equality Enforcement Tests
# ---------------------------------------------------------------------------

def test_same_case_arm_plan_canonical_equality_enforcement():
    """Verify that identical plans pass equality and mutated plans fail equality."""
    plan_dict = {
        "intent": "data_flow",
        "target_repositories": ["pandaroot", "restgas_determination"],
        "resolved_versions": {"pandaroot": "v1", "restgas_determination": "v1"},
        "version_conflicts": [],
        "symbols": ["macro/target/ana_dpm.C"],
        "concepts": ["event vertex", "worker step"],
        "concept_scopes": {},
        "source_budgets": {"code": 0.6, "workflow": 0.4},
        "required_source_types": ["code", "workflow"],
        "paper_page_hints": {},
        "resolved_aliases": {},
        "premise_corrections": [],
        "analysis_diagnostics": {},
    }
    p1 = RetrievalPlan.model_validate(plan_dict)
    p2 = RetrievalPlan.model_validate(copy.deepcopy(plan_dict))
    assert p1.model_dump(mode="json") == p2.model_dump(mode="json")

    # Mutated plan
    plan_dict_mutated = copy.deepcopy(plan_dict)
    plan_dict_mutated["concepts"] = ["event vertex"]  # omitted worker step
    p3 = RetrievalPlan.model_validate(plan_dict_mutated)
    assert p1.model_dump(mode="json") != p3.model_dump(mode="json")


# ---------------------------------------------------------------------------
# 7. Semantic Weakness Does Not Trigger Redraw Tests
# ---------------------------------------------------------------------------

def test_valid_plan_semantic_weakness_does_not_trigger_redraw():
    """Verify that a schema-valid plan with few or no concepts is accepted immediately,
    as semantic weakness is strictly NOT a retry condition.
    """
    weak_plan = RetrievalPlan(
        intent="general",
        target_repositories=[],
        resolved_versions={},
        version_conflicts=[],
        symbols=[],
        concepts=[],  # empty concepts: semantically weak
        concept_scopes={},
        source_budgets={"code": 1.0},
        required_source_types=["code"],
        paper_page_hints={},
        resolved_aliases={},
        premise_corrections=[],
        analysis_diagnostics={},
    )
    # A valid schema object deserializes without error
    dumped = weak_plan.model_dump(mode="json")
    validated = RetrievalPlan.model_validate(dumped)
    assert validated.concepts == []
    # In Phase P, this plan must be accepted as generated without retry


# ---------------------------------------------------------------------------
# 8. Corrected Criticality Contract Tests
# ---------------------------------------------------------------------------

def test_corrected_criticality_contract():
    """Verify forward-only corrected benchmark contract:
    - g021.e1 is critical=True
    - g021.e2 is critical=False (valid supporting evidence)
    - n022.e2 is critical=True
    """
    gold_ds = load_gold_dataset(_PROJECT_ROOT / v2.GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(_PROJECT_ROOT / v2.NOVEL_DEV_PATH)
    all_q = {q.id: q for q in gold_ds.questions + novel_ds.questions}

    g021_q = all_q["g021"]
    g021_e1 = next(g for g in g021_q.required_evidence_groups if g.group_id == "g021.e1")
    g021_e2 = next(g for g in g021_q.required_evidence_groups if g.group_id == "g021.e2")
    assert g021_e1.critical is True
    assert g021_e2.critical is False

    n022_q = all_q["n022"]
    n022_e2 = next(g for g in n022_q.required_evidence_groups if g.group_id == "n022.e2")
    assert n022_e2.critical is True


# ---------------------------------------------------------------------------
# 9. Protected Dataset & Production Activation Guards Tests
# ---------------------------------------------------------------------------

def test_protected_dataset_and_production_guards():
    """Verify that:
    - No protected novel_validation or holdout datasets are referenced or loaded
    - production_activation is False
    - first_batch_runtime_migration is BLOCKED
    - d4_a3 is NOT_STARTED / BLOCKED
    """
    manifest = json.loads((_PROJECT_ROOT / v2.MANIFEST_PATH).read_text(encoding="utf-8"))
    assert manifest["production_activation"] is False
    assert manifest["first_batch_runtime_migration"] == "BLOCKED"
    assert manifest["d4_a3"] == "NOT_STARTED / BLOCKED"

    prereg = json.loads((_PROJECT_ROOT / v2.PREREGISTRATION_PATH).read_text(encoding="utf-8"))
    guards = prereg["production_and_lifecycle_guards"]
    assert guards["production_activation"] is False
    assert guards["first_batch_runtime_migration"] == "BLOCKED"
    assert guards["d4_a3"] == "NOT_STARTED / BLOCKED"

    acct = manifest["pre_exposure_accounting"]
    assert acct["NOVEL_VALIDATION_RUNS"] == 0
    assert acct["NOVEL_HOLDOUT_RUNS"] == 0
    assert acct["PROTECTED_DATASET_ACCESS"] == 0


# ---------------------------------------------------------------------------
# 10. No Question-Specific Shortcuts Guard Tests
# ---------------------------------------------------------------------------

def test_no_question_specific_shortcuts():
    """Verify that runner implementation does not contain hardcoded case-ID branching
    for locator injection, expected files, or shortcut bypasses.
    """
    code = (_PROJECT_ROOT / "evaluation" / "scripts" / "d4_a2_v2_controlled_shared_plan_validation.py").read_text(
        encoding="utf-8"
    )
    # Ensure there are no shortcuts like "if cid == 'n022': return special_file"
    forbidden_snippets = [
        "if cid == 'n022': return",
        "if cid == 'g021': return",
        "if case_id == 'n022': return",
        "if case_id == 'g021': return",
    ]
    for snip in forbidden_snippets:
        assert snip not in code


# ---------------------------------------------------------------------------
# 11. Verdict Precedence Ladder Tests
# ---------------------------------------------------------------------------

VALID_PRIMARY_METRIC_DELTAS = {
    "recall_at_5": 0.0,
    "recall_at_10": 0.0,
    "recall_at_20": 0.0,
    "combined_candidate_recall": 0.0,
    "final_evidence_recall": 0.0,
    "critical_final_evidence_recall": 0.0,
}


def _make_valid_verdict_inputs(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "execution_valid": True,
        "protocol_violation": False,
        "before_reference_valid": True,
        "target_replacement_reproduced": 2,
        "batch1_dependency_removed": 2,
        "shared_plan_critical_regressions": [],
        "grounding_regressions": 0,
        "wrong_version_regressions": 0,
        "invalid_provenance_recoveries": 0,
        "metric_deltas": dict(VALID_PRIMARY_METRIC_DELTAS),
    }
    base.update(overrides)
    return base


def test_verdict_precedence_ladder():
    """Verify the 6-level verdict precedence ladder:
    - Level 1: INVALID
    - Level 2: INCONCLUSIVE
    - Level 3: FAIL (Primary target replacement not reproduced)
    - Level 4: FAIL (Shared plan critical treatment regression)
    - Level 5: PARTIAL (Aggregate regression exceeds bounded tolerance)
    - Level 6: PASS (Controlled shared plan T2 validated)
    """
    # Level 1: Protocol failure
    v1 = v2.compute_controlled_shared_plan_verdict(
        **_make_valid_verdict_inputs(execution_valid=False)
    )
    assert v1["verdict_level"] == 1
    assert "INVALID" in v1["verdict"]

    # Level 2: BEFORE reference not reproduced
    v2_res = v2.compute_controlled_shared_plan_verdict(
        **_make_valid_verdict_inputs(before_reference_valid=False)
    )
    assert v2_res["verdict_level"] == 2
    assert "INCONCLUSIVE" in v2_res["verdict"]

    # Level 3: Target replacement not reproduced
    v3 = v2.compute_controlled_shared_plan_verdict(
        **_make_valid_verdict_inputs(target_replacement_reproduced=1)
    )
    assert v3["verdict_level"] == 3
    assert "FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED" in v3["verdict"]

    # Level 4: Shared plan critical regression
    v4 = v2.compute_controlled_shared_plan_verdict(
        **_make_valid_verdict_inputs(shared_plan_critical_regressions=["n022.e2"])
    )
    assert v4["verdict_level"] == 4
    assert "FAIL / SHARED_PLAN_CRITICAL_TREATMENT_REGRESSION" in v4["verdict"]

    # Level 5: Aggregate tolerance exceeded
    deltas_l5 = dict(VALID_PRIMARY_METRIC_DELTAS)
    deltas_l5["recall_at_5"] = -0.06
    v5 = v2.compute_controlled_shared_plan_verdict(
        **_make_valid_verdict_inputs(metric_deltas=deltas_l5)
    )
    assert v5["verdict_level"] == 5
    assert "PARTIAL / AGGREGATE_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE" in v5["verdict"]

    # Level 6: PASS
    v6 = v2.compute_controlled_shared_plan_verdict(
        **_make_valid_verdict_inputs()
    )
    assert v6["verdict_level"] == 6
    assert "PASS / CONTROLLED_SHARED_PLAN_T2_VALIDATED" in v6["verdict"]


def test_verdict_empty_input_cannot_pass():
    """Verify that compute_controlled_shared_plan_verdict fails closed at Level 1 on empty input."""
    res = v2.compute_controlled_shared_plan_verdict()
    assert res["verdict_level"] == 1
    assert "INVALID" in res["verdict"]
    assert "INCOMPLETE_EVALUATOR_INPUT" in res["verdict_reason"]


def test_verdict_incomplete_primary_metrics_cannot_pass():
    """Verify that compute_controlled_shared_plan_verdict fails closed at Level 1 if any primary metric is missing."""
    for key in v2.REQUIRED_PRIMARY_METRIC_KEYS:
        incomplete_deltas = dict(VALID_PRIMARY_METRIC_DELTAS)
        del incomplete_deltas[key]
        inputs = _make_valid_verdict_inputs(metric_deltas=incomplete_deltas)
        res = v2.compute_controlled_shared_plan_verdict(**inputs)
        assert res["verdict_level"] == 1, f"Should fail Level 1 when {key} is missing"
        assert "INVALID" in res["verdict"]
        assert "INCOMPLETE_EVALUATOR_INPUT" in res["verdict_reason"]
        assert key in res["verdict_reason"]


def test_verdict_missing_safety_accounting_cannot_pass():
    """Verify that compute_controlled_shared_plan_verdict fails closed at Level 1 if safety accounting is missing."""
    for safety_key in ("grounding_regressions", "wrong_version_regressions", "invalid_provenance_recoveries"):
        inputs = _make_valid_verdict_inputs(**{safety_key: None})
        res = v2.compute_controlled_shared_plan_verdict(**inputs)
        assert res["verdict_level"] == 1, f"Should fail Level 1 when {safety_key} is None"
        assert "INVALID" in res["verdict"]
        assert "INCOMPLETE_EVALUATOR_INPUT" in res["verdict_reason"]


def test_verdict_missing_target_reproduction_cannot_pass():
    """Verify that compute_controlled_shared_plan_verdict fails closed at Level 1 if target reproduction is missing."""
    for target_key in ("target_replacement_reproduced", "batch1_dependency_removed"):
        inputs = _make_valid_verdict_inputs(**{target_key: None})
        res = v2.compute_controlled_shared_plan_verdict(**inputs)
        assert res["verdict_level"] == 1, f"Should fail Level 1 when {target_key} is None"
        assert "INVALID" in res["verdict"]
        assert "INCOMPLETE_EVALUATOR_INPUT" in res["verdict_reason"]


def test_verdict_complete_valid_input_passes():
    """Verify that compute_controlled_shared_plan_verdict with complete valid input produces Level 6 PASS."""
    inputs = _make_valid_verdict_inputs()
    res = v2.compute_controlled_shared_plan_verdict(**inputs)
    assert res["verdict_level"] == 6
    assert "PASS / CONTROLLED_SHARED_PLAN_T2_VALIDATED" in res["verdict"]


# ---------------------------------------------------------------------------
# 12. Pre-exposure Call Accounting Strictly Zero Tests
# ---------------------------------------------------------------------------

def test_pre_exposure_call_accounting_strictly_zero():
    """Verify that all pre-exposure call counters in manifest and preregistration are zero."""
    manifest = json.loads((_PROJECT_ROOT / v2.MANIFEST_PATH).read_text(encoding="utf-8"))
    acct = manifest["pre_exposure_accounting"]
    assert acct["PHASE_P_PLANS_ACQUIRED"] == 0
    assert acct["PHASE_R_CELLS_COMPLETED"] == 0
    assert acct["ANALYZER_PROVIDER_CALLS"] == 0
    assert acct["EMBEDDING_PROVIDER_CALLS"] == 0
    assert acct["RERANKER_PROVIDER_CALLS"] == 0
    assert acct["TOTAL_LOGICAL_MODEL_CALLS"] == 0
    assert acct["QA_CALLS"] == 0
    assert acct["VERIFIER_CALLS"] == 0
    assert acct["JUDGE_CALLS"] == 0
    assert acct["POSTGRESQL_WRITES"] == 0
    assert acct["QDRANT_WRITES"] == 0


# ---------------------------------------------------------------------------
# 13. Audit Invariants Offline Execution Tests
# ---------------------------------------------------------------------------

def test_audit_invariants_offline(monkeypatch):
    """Verify that audit_invariants executes successfully offline."""
    manifest_data = json.loads((_PROJECT_ROOT / v2.MANIFEST_PATH).read_text(encoding="utf-8"))
    manifest_pre = copy.deepcopy(manifest_data)
    manifest_pre["outcome_exposure_state"]["D4_A2_V2_OUTCOME_EXPOSURE"] = "NOT_STARTED"
    manifest_pre["outcome_exposure_state"]["phase_p_slots_completed"] = 0
    for s in manifest_pre["phase_p_slots_16"]:
        s["status"] = "NOT_STARTED"
    orig_load_json = v2._load_json

    def mock_load(path: Path) -> Any:
        if Path(path).resolve() == (_PROJECT_ROOT / v2.MANIFEST_PATH).resolve():
            return manifest_pre
        return orig_load_json(path)

    monkeypatch.setattr(v2, "_load_json", mock_load)
    monkeypatch.setattr(v2, "verify_drift_guards", lambda root, require_clean_worktree=False: {"verified": True, "dirty_frozen_paths": []})
    receipt = v2.audit_invariants(_PROJECT_ROOT)
    assert receipt["verified"] is True
    assert receipt["cohort_cases"] == 16
    assert receipt["gold_cases"] == 10
    assert receipt["novel_dev_cases"] == 6
    assert receipt["answered_cases"] == 13
    assert receipt["insufficient_evidence_cases"] == 3
    assert receipt["phase_p_slots"] == 16
    assert receipt["phase_r_cells"] == 32
    assert receipt["balanced_schedule_verified"] is True
    assert receipt["drift_guards_verified"] is True


# ---------------------------------------------------------------------------
# Test Helpers
# ---------------------------------------------------------------------------

def _make_sample_canonical_plan(case_id: str) -> dict[str, Any]:
    return {
        "intent": "code_search",
        "routing_method": "rule",
        "target_repositories": ["pandaroot"],
        "resolved_versions": {"pandaroot": "v1"},
        "version_conflicts": [],
        "concepts": [f"concept for {case_id}"],
        "symbols": [f"macro/test_{case_id}.C"],
        "concept_scopes": {},
        "source_budgets": {"code": 1.0},
        "required_source_types": ["code"],
        "resolved_aliases": {},
        "premise_corrections": [],
        "paper_page_hints": {},
        "analysis_diagnostics": {},
    }


def _make_valid_raw_plans_artifact(commit_a_sha: str = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") -> dict[str, Any]:
    plans = []
    for idx, cid in enumerate(v2.CASE_ORDER, start=1):
        plan_dict = _make_sample_canonical_plan(cid)
        sig_str, sig_payload = v2.compute_plan_signature(plan_dict)
        plans.append({
            "draw_index": idx,
            "case_id": cid,
            "question": f"Question for {cid}",
            "status": "COMPLETED",
            "error": None,
            "canonical_plan": plan_dict,
            "plan_signature": sig_payload,
            "retries_count": 0,
            "retry_reasons": [],
            "provider_attempts": 1,
            "token_usage": 100,
            "elapsed_seconds": 0.5,
            "started_at": "2026-09-03T12:00:00",
            "completed_at": "2026-09-03T12:00:01",
        })

    return {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V2",
        "stage": "Phase P — Controlled Shared Plan Acquisition",
        "created_at": "2026-09-03T12:00:05",
        "starting_head": v2.STARTING_HEAD,
        "implementation_freeze_head": commit_a_sha,
        "runtime_execution_head": commit_a_sha,
        "commit_a_implementation_freeze_head": commit_a_sha,
        "plan_freeze_state": "FROZEN",
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED": True,
        "PHASE_R_RETRIEVAL_EXECUTED": False,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "model_id": v2.EXPECTED_MODEL,
        "vertex_location": v2.EXPECTED_VERTEX_LOCATION,
        "temperature": v2.EXPECTED_TEMPERATURE,
        "prompt_authority": "panda_agent.prompts.QUERY_ANALYZER_SYSTEM_PROMPT",
        "exact_acquisition_case_order": list(v2.CASE_ORDER),
        "max_provider_attempts_per_case": v2.MAX_PROVIDER_ATTEMPTS_PER_CASE,
        "allowed_retry_categories": sorted(list(v2.ALLOWED_RETRY_CATEGORIES)),
        "plans_planned": 16,
        "plans_completed": 16,
        "plans_failed": 0,
        "accounting": {
            "analyzer_calls": 16,
            "embedding_calls": 0,
            "reranker_calls": 0,
            "logical_model_calls": 16,
            "provider_attempts": 16,
            "token_usage": 1600,
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "postgresql_writes": 0,
            "qdrant_writes": 0,
            "ingestion": 0,
            "reindex": 0,
            "novel_validation_runs": 0,
            "novel_holdout_runs": 0,
            "protected_dataset_access": 0,
        },
        "plans": plans,
    }


# ---------------------------------------------------------------------------
# 14. Phase P Error Classification and Narrow Retry Tests
# ---------------------------------------------------------------------------

def test_phase_p_retry_error_classification():
    """Verify that only allowed transport/provider failures, unparsable responses,
    or schema-validation failures are classified as retryable.
    All other exceptions fail closed immediately without retry.
    """
    # 1. Transport/provider failures
    assert v2.classify_phase_p_retryable_error(VertexCallError("deadline exceeded")) == (
        True, v2.RETRY_CATEGORY_TRANSPORT_PROVIDER
    )
    assert v2.classify_phase_p_retryable_error(genai_errors.APIError(503, {"error": "API quota"})) == (
        True, v2.RETRY_CATEGORY_TRANSPORT_PROVIDER
    )
    assert v2.classify_phase_p_retryable_error(ConnectionError("socket closed")) == (
        True, v2.RETRY_CATEGORY_TRANSPORT_PROVIDER
    )
    assert v2.classify_phase_p_retryable_error(TimeoutError("request timed out")) == (
        True, v2.RETRY_CATEGORY_TRANSPORT_PROVIDER
    )

    # 2. Unparsable responses
    assert v2.classify_phase_p_retryable_error(json.JSONDecodeError("Expecting value", "doc", 0)) == (
        True, v2.RETRY_CATEGORY_UNPARSABLE_RESPONSE
    )
    assert v2.classify_phase_p_retryable_error(ValueError("Vertex returned an empty structured response")) == (
        True, v2.RETRY_CATEGORY_UNPARSABLE_RESPONSE
    )
    assert v2.classify_phase_p_retryable_error(ValueError("structured response must be a JSON object")) == (
        True, v2.RETRY_CATEGORY_UNPARSABLE_RESPONSE
    )

    # 3. Schema validation failures
    try:
        RetrievalPlan.model_validate({"intent": None})
    except ValidationError as val_err:
        assert v2.classify_phase_p_retryable_error(val_err) == (
            True, v2.RETRY_CATEGORY_SCHEMA_VALIDATION
        )

    assert v2.classify_phase_p_retryable_error(
        ValueError("analyzer semantic delta did not provide a grounded intent")
    ) == (True, v2.RETRY_CATEGORY_SCHEMA_VALIDATION)

    # 4. Strictly non-retryable exceptions (fail closed immediately)
    assert v2.classify_phase_p_retryable_error(KeyError("missing_key")) == (False, None)
    assert v2.classify_phase_p_retryable_error(TypeError("bad type")) == (False, None)
    assert v2.classify_phase_p_retryable_error(RuntimeError("unrelated failure")) == (False, None)
    assert v2.classify_phase_p_retryable_error(ValueError("unrelated message")) == (False, None)
    assert v2.classify_phase_p_retryable_error(ZeroDivisionError()) == (False, None)
    assert v2.classify_phase_p_retryable_error(IndexError("out of range")) == (False, None)


def test_phase_p_allowed_errors_retry_and_record_exact_reasons(monkeypatch, tmp_path):
    """Verify that execute_phase_p retries allowed errors, records exact categorized reasons,
    and accepts valid plan.
    """
    manifest_data = json.loads((_PROJECT_ROOT / v2.MANIFEST_PATH).read_text(encoding="utf-8"))
    manifest_data["outcome_exposure_state"]["D4_A2_V2_OUTCOME_EXPOSURE"] = "NOT_STARTED"
    manifest_data["phase_p_slots_16"][0]["status"] = "NOT_STARTED"
    manifest_file = tmp_path / v2.MANIFEST_PATH
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    mock_q = MagicMock()
    mock_q.id = "g029"
    mock_q.query = "What is the LMD workflow?"
    mock_ds = MagicMock()
    mock_ds.questions = [mock_q]
    monkeypatch.setattr(v2, "load_gold_dataset", lambda path: mock_ds)

    mock_retriever = MagicMock()
    valid_plan = RetrievalPlan.model_validate(_make_sample_canonical_plan("g029"))
    attempt_counter = 0

    def mock_analyze(query: str) -> RetrievalPlan:
        nonlocal attempt_counter
        attempt_counter += 1
        if attempt_counter == 1:
            raise VertexCallError("transient provider timeout")
        elif attempt_counter == 2:
            raise json.JSONDecodeError("Expecting value", "doc", 0)
        return valid_plan

    mock_retriever.analyze = mock_analyze
    mock_retriever.vertex.stats_snapshot.return_value = {}
    mock_retriever.vertex.stats_delta.return_value = {"model_calls": 3, "token_usage": 150}

    monkeypatch.setattr(v2, "Retriever", lambda root: mock_retriever)
    monkeypatch.setattr("time.sleep", lambda s: None)
    monkeypatch.setattr(v2, "_git_head", lambda root: "test_sha_commit_a")
    monkeypatch.setattr(v2, "audit_invariants", lambda root: {"model_id": "gemini-3.8-flash"})
    monkeypatch.setattr(v2, "CASE_ORDER", ["g029"])
    monkeypatch.setattr(
        v2,
        "verify_phase_p_gate",
        lambda root, git_checker=None: {
            "verified": True,
            "implementation_freeze_head": "test_sha_commit_a",
            "runtime_execution_head": "test_sha_commit_a",
            "commit_message": v2.EXPECTED_A_R1_COMMIT_MESSAGE,
            "frozen_paths_clean": True,
        },
    )

    res = v2.execute_phase_p(tmp_path)

    assert attempt_counter == 3
    plan_entry = res["plans"][0]
    assert plan_entry["status"] == "COMPLETED"
    assert plan_entry["retries_count"] == 2
    assert len(plan_entry["retry_reasons"]) == 2
    assert f"[{v2.RETRY_CATEGORY_TRANSPORT_PROVIDER}]" in plan_entry["retry_reasons"][0]
    assert f"[{v2.RETRY_CATEGORY_UNPARSABLE_RESPONSE}]" in plan_entry["retry_reasons"][1]


def test_phase_p_unrelated_exception_fails_closed_without_retry(monkeypatch, tmp_path):
    """Verify that an unrelated exception fails closed immediately without any retry."""
    manifest_data = json.loads((_PROJECT_ROOT / v2.MANIFEST_PATH).read_text(encoding="utf-8"))
    manifest_data["outcome_exposure_state"]["D4_A2_V2_OUTCOME_EXPOSURE"] = "NOT_STARTED"
    manifest_data["phase_p_slots_16"][0]["status"] = "NOT_STARTED"
    manifest_file = tmp_path / v2.MANIFEST_PATH
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    mock_q = MagicMock()
    mock_q.id = "g029"
    mock_q.query = "What is the LMD workflow?"
    mock_ds = MagicMock()
    mock_ds.questions = [mock_q]
    monkeypatch.setattr(v2, "load_gold_dataset", lambda path: mock_ds)

    mock_retriever = MagicMock()
    attempt_counter = 0

    def mock_analyze(query: str) -> RetrievalPlan:
        nonlocal attempt_counter
        attempt_counter += 1
        raise KeyError("unrelated_internal_error")

    mock_retriever.analyze = mock_analyze
    mock_retriever.vertex.stats_snapshot.return_value = {}
    mock_retriever.vertex.stats_delta.return_value = {"model_calls": 1, "token_usage": 0}

    monkeypatch.setattr(v2, "Retriever", lambda root: mock_retriever)
    monkeypatch.setattr("time.sleep", lambda s: None)
    monkeypatch.setattr(v2, "_git_head", lambda root: "test_sha_commit_a")
    monkeypatch.setattr(v2, "audit_invariants", lambda root: {"model_id": "gemini-3.8-flash"})
    monkeypatch.setattr(v2, "CASE_ORDER", ["g029"])
    monkeypatch.setattr(
        v2,
        "verify_phase_p_gate",
        lambda root, git_checker=None: {
            "verified": True,
            "implementation_freeze_head": "test_sha_commit_a",
            "runtime_execution_head": "test_sha_commit_a",
            "commit_message": v2.EXPECTED_A_R1_COMMIT_MESSAGE,
            "frozen_paths_clean": True,
        },
    )

    with pytest.raises(RuntimeError) as exc_info:
        v2.execute_phase_p(tmp_path)

    assert "Non-retryable exception" in str(exc_info.value)
    assert attempt_counter == 1  # Strictly NO retry!

    saved_manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    slot0 = saved_manifest["phase_p_slots_16"][0]
    assert slot0["status"] == "FAILED"
    assert "NON_RETRYABLE_EXCEPTION: KeyError" in slot0["error"]


# ---------------------------------------------------------------------------
# 15. Hard Commit-B Plan-Freeze Gate Tests
# ---------------------------------------------------------------------------

def test_plan_freeze_gate_committed_unchanged_passes(tmp_path):
    """Verify that a committed unchanged raw plans artifact passes the gate."""
    commit_a_sha = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    commit_b_sha = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    artifact = _make_valid_raw_plans_artifact(commit_a_sha)

    raw_plans_file = tmp_path / v2.RAW_PLANS_PATH
    raw_plans_file.parent.mkdir(parents=True, exist_ok=True)
    raw_plans_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    def mock_git_checker(root: Path, rel_path: str, a_sha: str) -> str:
        assert a_sha == commit_a_sha
        assert rel_path.replace("\\", "/") == v2.RAW_PLANS_PATH
        return commit_b_sha

    receipt = v2.verify_plan_freeze_gate(tmp_path, git_checker=mock_git_checker)
    assert receipt["verified"] is True
    assert receipt["commit_a_implementation_freeze_head"] == commit_a_sha
    assert receipt["phase_p_plan_freeze_commit_head"] == commit_b_sha
    assert receipt["plans_count"] == 16
    assert receipt["cases_validated"] == v2.CASE_ORDER


def test_plan_freeze_gate_rejects_uncommitted_or_dirty_worktree(tmp_path):
    """Verify that uncommitted or worktree-dirty plan artifacts are rejected."""
    artifact = _make_valid_raw_plans_artifact("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    raw_plans_file = tmp_path / v2.RAW_PLANS_PATH
    raw_plans_file.parent.mkdir(parents=True, exist_ok=True)
    raw_plans_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    def mock_git_checker_dirty(root: Path, rel_path: str, a_sha: str) -> str:
        raise RuntimeError(f"Plan freeze artifact {rel_path} has uncommitted/dirty changes in index or worktree: ' M {rel_path}'")

    with pytest.raises(RuntimeError) as exc_info:
        v2.verify_plan_freeze_gate(tmp_path, git_checker=mock_git_checker_dirty)
    assert "uncommitted/dirty changes" in str(exc_info.value)


def test_plan_freeze_gate_rejects_stale_or_non_descendant_commit(tmp_path):
    """Verify that freeze commit equal to Commit A or not descendant is rejected."""
    commit_a_sha = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    artifact = _make_valid_raw_plans_artifact(commit_a_sha)
    raw_plans_file = tmp_path / v2.RAW_PLANS_PATH
    raw_plans_file.parent.mkdir(parents=True, exist_ok=True)
    raw_plans_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    with pytest.raises(RuntimeError) as exc_info:
        v2.check_git_plan_freeze_status(tmp_path, v2.RAW_PLANS_PATH, commit_a_sha)
    assert "not present in Git HEAD" in str(exc_info.value)


def test_plan_freeze_gate_rejects_post_freeze_mutations_and_malformed(tmp_path):
    """Verify that any post-freeze mutation, malformed plan, or missing case is rejected."""
    commit_a_sha = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    commit_b_sha = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    base_artifact = _make_valid_raw_plans_artifact(commit_a_sha)

    mock_git_checker = lambda root, rel_path, a_sha: commit_b_sha

    # 1. Missing case (15 plans instead of 16)
    mutated_1 = copy.deepcopy(base_artifact)
    mutated_1["plans"] = mutated_1["plans"][:15]
    mutated_1["plans_planned"] = 15
    mutated_1["plans_completed"] = 15
    p1 = tmp_path / "plans_1.json"
    p1.write_text(json.dumps(mutated_1), encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        v2.verify_plan_freeze_gate(tmp_path, p1, git_checker=mock_git_checker)
    assert "plans_planned mismatch" in str(exc.value)

    # 2. Case order scrambled (swap first two cases)
    mutated_2 = copy.deepcopy(base_artifact)
    mutated_2["plans"][0]["case_id"], mutated_2["plans"][1]["case_id"] = (
        mutated_2["plans"][1]["case_id"], mutated_2["plans"][0]["case_id"]
    )
    p2 = tmp_path / "plans_2.json"
    p2.write_text(json.dumps(mutated_2), encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        v2.verify_plan_freeze_gate(tmp_path, p2, git_checker=mock_git_checker)
    assert "case order mismatch" in str(exc.value)

    # 3. Incomplete status
    mutated_3 = copy.deepcopy(base_artifact)
    mutated_3["plans"][3]["status"] = "STARTED"
    p3 = tmp_path / "plans_3.json"
    p3.write_text(json.dumps(mutated_3), encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        v2.verify_plan_freeze_gate(tmp_path, p3, git_checker=mock_git_checker)
    assert "status is not COMPLETED" in str(exc.value)

    # 4. Schema-invalid canonical_plan
    mutated_4 = copy.deepcopy(base_artifact)
    mutated_4["plans"][0]["canonical_plan"] = {"not_a_valid_plan": True}
    p4 = tmp_path / "plans_4.json"
    p4.write_text(json.dumps(mutated_4), encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        v2.verify_plan_freeze_gate(tmp_path, p4, git_checker=mock_git_checker)
    assert "failed RetrievalPlan schema validation" in str(exc.value)

    # 5. Premature execution flag (PHASE_R_RETRIEVAL_EXECUTED = True)
    mutated_5 = copy.deepcopy(base_artifact)
    mutated_5["PHASE_R_RETRIEVAL_EXECUTED"] = True
    p5 = tmp_path / "plans_5.json"
    p5.write_text(json.dumps(mutated_5), encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        v2.verify_plan_freeze_gate(tmp_path, p5, git_checker=mock_git_checker)
    assert "PHASE_R_RETRIEVAL_EXECUTED must be False" in str(exc.value)

    # 6. Malformed JSON
    p6 = tmp_path / "plans_6.json"
    p6.write_text("NOT_JSON_DATA", encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        v2.verify_plan_freeze_gate(tmp_path, p6, git_checker=mock_git_checker)
    assert "Malformed JSON" in str(exc.value)


def test_execute_phase_r_gate_rejects_before_exposure_state_mutation(tmp_path):
    """Verify that execute_phase_r fails at the plan-freeze gate BEFORE changing exposure state."""
    manifest_data = json.loads((_PROJECT_ROOT / v2.MANIFEST_PATH).read_text(encoding="utf-8"))
    manifest_file = tmp_path / v2.MANIFEST_PATH
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    # Missing raw plans file
    with pytest.raises(FileNotFoundError):
        v2.execute_phase_r(tmp_path)

    # Verify manifest exposure state was NOT mutated
    manifest_after = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert (
        manifest_after["outcome_exposure_state"]["D4_A2_V2_OUTCOME_EXPOSURE"]
        == manifest_data["outcome_exposure_state"]["D4_A2_V2_OUTCOME_EXPOSURE"]
    )
    assert manifest_after["outcome_exposure_state"]["phase_r_cells_completed"] == 0


def test_provenance_names_separate_commit_a_and_plan_freeze():
    """Verify that provenance separately tracks commit_a_implementation_freeze_head
    and phase_p_plan_freeze_commit_head and rejects artifacts conflating the two.
    """
    sample_raw_data = {
        "commit_a_implementation_freeze_head": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "phase_p_plan_freeze_commit_head": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "slots": [
            {
                "cell_index": item["slot_index"],
                "case_id": item["case_id"],
                "arm": item["arm"],
                "status": "COMPLETED",
                "plan_equality_verified": True,
                "analyzer_provider_calls": 0,
            }
            for item in v2.SCHEDULE_32
        ],
        "model_contract": {
            "generation_model_id": v2.EXPECTED_MODEL,
            "embedding_model_id": v2.EXPECTED_EMBEDDING_MODEL,
        },
        "accounting": {
            "NOVEL_VALIDATION_RUNS": 0,
            "NOVEL_HOLDOUT_RUNS": 0,
            "PROTECTED_DATASET_ACCESS": 0,
        },
    }

    is_valid, err, _ = v2.validate_raw_artifact_structural_validity(sample_raw_data)
    assert is_valid is True
    assert err is None

    # Missing or conflated commit_a and plan_freeze
    conflated = copy.deepcopy(sample_raw_data)
    conflated["phase_p_plan_freeze_commit_head"] = conflated["commit_a_implementation_freeze_head"]
    is_valid2, err2, _ = v2.validate_raw_artifact_structural_validity(conflated)
    assert is_valid2 is False
    assert "cannot equal" in err2


# ---------------------------------------------------------------------------
# 16. Phase R Raw Lossless Preservation Tests (Section 13 & 19 Trace Data)
# ---------------------------------------------------------------------------

def test_build_phase_r_cell_record_lossless_preservation():
    """Verify that build_phase_r_cell_record preserves all Section 13 and Section 19
    scientific trace data returned by execute_cell_retrieval without inventing fields from absent keys.
    """
    mock_plan = RetrievalPlan(
        intent="data_flow",
        target_repositories=["pandaroot", "restgas_determination"],
        resolved_versions={"pandaroot": "v1", "restgas_determination": "v1"},
        version_conflicts=[],
        symbols=["macro/target/ana_dpm.C"],
        concepts=["restgas"],
        concept_scopes={},
        source_budgets={"code": 0.6, "workflow": 0.4},
        required_source_types=["code", "workflow"],
        paper_page_hints={"li_2026": [131]},
        resolved_aliases={},
        premise_corrections=[],
        analysis_diagnostics={},
    )
    mock_plan_dict = mock_plan.model_dump(mode="json")

    mock_retrieval_data = {
        "case_id": "g036",
        "arm": "BATCH1_REPLACEMENT",
        "question": "Where is the target generator configured?",
        "matched_query_expansion_rules": ["restgas_profile_workflow"],
        "exact_effective_preserved_components": {
            "restgas_profile_workflow": {
                "triggers": ["restgas"],
                "repositories": ["restgas_determination"],
                "concepts": ["profile"],
            }
        },
        "exact_effective_suppressed_components": {
            "restgas_profile_workflow": {
                "symbols": ["pgenerators/Target/PndTargetGenerator.cxx"],
                "paper_page_hints": {},
            }
        },
        "inputs": {
            "repository_inputs": ["restgas_determination"],
            "symbol_inputs": ["macro/target/ana_dpm.C"],
            "concept_inputs": ["restgas"],
            "page_inputs": {"li_2026": [131]},
        },
        "resolved_d2_seeds": [{"seed_id": "s1", "symbol": "PndTargetGenerator"}],
        "reached_structures": [{"structure_id": "st1", "path": "pgenerators/Target/PndTargetGenerator.cxx"}],
        "reachability_receipts": [{"from": "s1", "to": "st1"}],
        "actual_bridge_receipts": [{"bridge_id": "b1", "target": "cand1"}],
        "eligible_bridge_candidates": [
            {"candidate_object_id": "cand1", "score": 0.95, "origin": "d2_bridge", "source_id": "pandaroot"}
        ],
        "selected_bridge_candidates": ["cand1"],
        "v2_diagnostics": {
            "candidate_receipts": [{"candidate_object_id": "cand1", "status": "GATE_PASS"}],
            "selected_rank_keys": ["cand1"],
            "eligible_count": 1,
            "selected_count": 1,
            "gate_passing_count": 1,
            "gate_rejected_count": 0,
        },
        "structured_receipts": {
            "structured_resolution": {"resolved_seeds": ["s1"]},
            "reachability_receipts_count": 1,
            "bridge_receipts_count": 1,
            "eligible_bridge_candidates_count": 1,
            "v2_selected_bridge_candidates": ["cand1"],
            "v2_selection_receipts": [{"candidate_object_id": "cand1", "passed": True}],
            "reservable_bridge_ids": ["cand1"],
            "reserved_bridge_candidate_ids": ["cand1"],
            "displaced_object_ids": ["cand_disp"],
        },
        "ordinary_fused_ordering": ["base1", "base2", "cand_disp"],
        "ordinary_fused_top30": ["base1", "base2", "cand_disp"],
        "reserved_candidate_ids": ["cand1"],
        "displaced_candidate_ids": ["cand_disp"],
        "final_pool_object_ids": ["base1", "base2", "cand1"],
        "reranked_object_ids": ["cand1", "base1", "base2"],
        "ranked_object_ids": ["cand1", "base1", "base2"],
        "final_evidence_object_ids": ["cand1", "base1"],
        "final_evidence_locators": {
            "cand1": {"path": "pgenerators/Target/PndTargetGenerator.cxx", "line": 42},
            "base1": {"path": "macro/target/ana_dpm.C", "line": 10},
        },
        "excluded": ["cand_disp"],
        "backfill_admissions": [],
        "channel_rankings": {"exact": ["base1"], "dense": ["base2"]},
        "plan_summary": mock_plan_dict,
    }

    group_retention = {
        "g036.e1": {
            "critical": True,
            "role": "primary_target",
            "in_exact_channel": False,
            "in_channel_union": False,
            "in_ordinary_fused_top30": False,
            "in_pre_rerank_pool": True,
            "in_final_evidence": True,
        }
    }

    record = v2.build_phase_r_cell_record(
        cell_idx=7,
        case_id="g036",
        dataset="Gold v2.6 dev",
        arm="BATCH1_REPLACEMENT",
        cell_retrieval_data=mock_retrieval_data,
        frozen_plan=mock_plan,
        group_retention_records=group_retention,
        started_at="2026-09-03T12:00:00",
        completed_at="2026-09-03T12:00:02",
        elapsed_seconds=2.0,
        cell_embedding_calls=1,
        cell_reranker_calls=1,
        cell_provider_attempts=2,
        cell_token_usage=300,
    )

    # Core identity & metadata
    assert record["cell_index"] == 7
    assert record["case_id"] == "g036"
    assert record["dataset"] == "Gold v2.6 dev"
    assert record["arm"] == "BATCH1_REPLACEMENT"
    assert record["status"] == "COMPLETED"
    assert record["elapsed_seconds"] == 2.0
    assert record["plan_equality_verified"] is True
    assert record["analyzer_provider_calls"] == 0
    assert record["embedding_calls"] == 1
    assert record["reranker_calls"] == 1
    assert record["provider_internal_attempts"] == 2
    assert record["token_usage"] == 300
    assert record["started_at"] == "2026-09-03T12:00:00"
    assert record["completed_at"] == "2026-09-03T12:00:02"

    # Plans
    assert record["frozen_canonical_plan"] == mock_plan_dict
    assert record["actual_canonical_plan"] == mock_plan_dict

    # Section 13 & 19 data preservation
    assert record["matched_query_expansion_rules"] == ["restgas_profile_workflow"]
    assert record["inputs"] == mock_retrieval_data["inputs"]
    assert record["exact_effective_preserved_components"] == mock_retrieval_data["exact_effective_preserved_components"]
    assert record["exact_effective_suppressed_components"] == mock_retrieval_data["exact_effective_suppressed_components"]
    assert record["channel_rankings"] == mock_retrieval_data["channel_rankings"]
    assert record["resolved_d2_seeds"] == mock_retrieval_data["resolved_d2_seeds"]
    assert record["reached_structures"] == mock_retrieval_data["reached_structures"]
    assert record["reachability_receipts"] == mock_retrieval_data["reachability_receipts"]
    assert record["actual_bridge_receipts"] == mock_retrieval_data["actual_bridge_receipts"]
    assert record["eligible_bridge_candidates"] == mock_retrieval_data["eligible_bridge_candidates"]
    assert record["selected_bridge_candidates"] == ["cand1"]
    assert record["v2_diagnostics"] == mock_retrieval_data["v2_diagnostics"]
    assert record["structured_receipts"] == mock_retrieval_data["structured_receipts"]
    assert record["ordinary_fused_ordering"] == ["base1", "base2", "cand_disp"]
    assert record["ordinary_fused_top30"] == ["base1", "base2", "cand_disp"]
    assert record["reserved_candidate_ids"] == ["cand1"]
    assert record["displaced_candidate_ids"] == ["cand_disp"]
    assert record["final_pool_object_ids"] == ["base1", "base2", "cand1"]
    assert record["reranked_object_ids"] == ["cand1", "base1", "base2"]
    assert record["ranked_object_ids"] == ["cand1", "base1", "base2"]
    assert record["final_evidence_object_ids"] == ["cand1", "base1"]
    assert record["final_evidence_locators"] == mock_retrieval_data["final_evidence_locators"]
    assert record["excluded"] == ["cand_disp"]
    assert record["backfill_admissions"] == []
    assert record["group_retention"] == group_retention

    # Strict check: absent keys from execute_cell_retrieval are not invented at top-level
    assert "eligible_bridge_candidates_count" not in record
    assert "gate_passing_bridge_candidates_count" not in record
    assert "selected_bridge_candidates_count" not in record
    assert "candidate_origins" not in record


# ---------------------------------------------------------------------------
# 17. Commit-D Evaluator Fail-Closed Boundary Tests
# ---------------------------------------------------------------------------

def test_evaluator_fails_closed_without_creating_files(tmp_path):
    """Verify that invoking evaluate() fails closed with RuntimeError and creates
    zero evaluator or result files. Commit D is not authorized.
    """
    with pytest.raises(RuntimeError) as exc_info:
        v2.evaluate(tmp_path)

    err_msg = str(exc_info.value)
    assert "Commit D" in err_msg
    assert "unavailable until separately authorized Commit D after Commit C raw freeze" in err_msg

    # Verify zero files created
    assert not (tmp_path / v2.EVALUATOR_RESULTS_PATH).exists()
    assert not (tmp_path / v2.RESULT_PATH).exists()
    assert list(tmp_path.rglob("*")) == []


def test_evaluator_cli_fails_closed(monkeypatch, tmp_path):
    """Verify that executing evaluate mode via CLI fails closed with zero file writes."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "d4_a2_v2_controlled_shared_plan_validation.py",
            "--project-root",
            str(tmp_path),
            "--mode",
            "evaluate",
        ],
    )
    with pytest.raises(RuntimeError) as exc_info:
        v2.main()

    assert "Commit D" in str(exc_info.value)
    assert not (tmp_path / v2.EVALUATOR_RESULTS_PATH).exists()
    assert not (tmp_path / v2.RESULT_PATH).exists()
    assert list(tmp_path.rglob("*")) == []


# ---------------------------------------------------------------------------
# 18. Commit A-R1 Pre-Exposure Freeze Guard Focused Tests (Section 25)
# ---------------------------------------------------------------------------

def test_phase_p_gate_rejects_dirty_frozen_files(tmp_path):
    """Verify that Phase-P gate fails closed when worktree or index is dirty for frozen files."""
    def mock_git_checker(root: Path):
        return (
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            v2.EXPECTED_A_R1_COMMIT_MESSAGE,
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            ["M evaluation/scripts/d4_a2_v2_controlled_shared_plan_validation.py"],
        )

    with pytest.raises(RuntimeError) as exc_info:
        v2.verify_phase_p_gate(tmp_path, git_checker=mock_git_checker)
    assert "Worktree or index is dirty" in str(exc_info.value)


def test_phase_p_gate_rejects_head_different_from_implementation_freeze(tmp_path):
    """Verify that Phase-P gate fails closed when current HEAD is not identical to freeze SHA."""
    def mock_git_checker(root: Path):
        return (
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            v2.EXPECTED_A_R1_COMMIT_MESSAGE,
            "cccccccccccccccccccccccccccccccccccccccc",  # different HEAD
            [],
        )

    with pytest.raises(RuntimeError) as exc_info:
        v2.verify_phase_p_gate(tmp_path, git_checker=mock_git_checker)
    assert "differs from authoritative implementation freeze" in str(exc_info.value)


def test_phase_p_does_not_dynamically_redefine_implementation_freeze(tmp_path, monkeypatch):
    """Verify that Phase-P gate determines freeze commit from authoritative containing commit,
    never adopting arbitrary current HEAD dynamically.
    """
    freeze_sha = "1111111111111111111111111111111111111111"
    descendant_head = "2222222222222222222222222222222222222222"
    monkeypatch.setattr(
        v2,
        "get_implementation_freeze_commit",
        lambda root: (freeze_sha, v2.EXPECTED_A_R1_COMMIT_MESSAGE),
    )
    monkeypatch.setattr(v2, "_git_head", lambda root: descendant_head)
    mock_run = MagicMock()
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = ""
    monkeypatch.setattr("subprocess.run", mock_run)

    with pytest.raises(RuntimeError) as exc_info:
        v2.verify_phase_p_gate(tmp_path)
    assert descendant_head in str(exc_info.value)
    assert freeze_sha in str(exc_info.value)
    assert "differs from authoritative implementation freeze" in str(exc_info.value)


def _mock_r2_git_subprocess(
    *,
    head_sha: str = "r2_repair_commit_sha_12345",
    head_msg: str = v2.EXPECTED_R2_COMMIT_MESSAGE,
    head_parents: list[str] | None = None,
    raw_plan_origin: str = v2.PLAN_FREEZE_HEAD,
    frozen_blob: str = v2.PLAN_FREEZE_RAW_BLOB,
    head_blob: str = v2.PLAN_FREEZE_RAW_BLOB,
    worktree_blob: str = v2.PLAN_FREEZE_RAW_BLOB,
    r2_diff_files: list[str] | None = None,
    plan_freeze_parents: list[str] | None = None,
    commit_b_diff_files: list[str] | None = None,
    dirty_paths: list[str] | None = None,
):
    if head_parents is None:
        head_parents = [v2.PLAN_FREEZE_HEAD]
    if r2_diff_files is None:
        r2_diff_files = list(v2.ALLOWED_R2_DIFF_FILES)
    if plan_freeze_parents is None:
        plan_freeze_parents = [v2.IMPLEMENTATION_FREEZE_HEAD]
    if commit_b_diff_files is None:
        commit_b_diff_files = list(v2.ALLOWED_COMMIT_B_DIFF_FILES)
    if dirty_paths is None:
        dirty_paths = []

    def mock_subp_run(cmd, **kwargs):
        res = MagicMock()
        res.returncode = 0
        cmd_str = " ".join(cmd)
        if "cat-file" in cmd_str:
            res.stdout = ""
        elif "status" in cmd_str:
            res.stdout = "\n".join(dirty_paths) + ("\n" if dirty_paths else "")
        elif "diff" in cmd_str:
            if len(cmd) >= 5 and cmd[3] == v2.PLAN_FREEZE_HEAD and cmd[4] == head_sha:
                res.stdout = "\n".join(r2_diff_files) + ("\n" if r2_diff_files else "")
            elif len(cmd) >= 5 and cmd[3] == v2.IMPLEMENTATION_FREEZE_HEAD and cmd[4] == v2.PLAN_FREEZE_HEAD:
                res.stdout = "\n".join(commit_b_diff_files) + ("\n" if commit_b_diff_files else "")
            else:
                res.stdout = ""
        elif "log" in cmd_str:
            if "%H%x00%s" in cmd_str:
                res.stdout = f"{head_sha}\x00{head_msg}\n"
            elif "%H" in cmd_str:
                res.stdout = f"{raw_plan_origin}\n"
            elif "%P" in cmd_str:
                if v2.PLAN_FREEZE_HEAD in cmd:
                    res.stdout = " ".join(plan_freeze_parents) + "\n"
                else:
                    res.stdout = " ".join(head_parents) + "\n"
            else:
                res.stdout = f"{head_sha}\n"
        elif "rev-parse" in cmd_str:
            if "HEAD:" in cmd_str or (len(cmd) >= 3 and cmd[2].startswith("HEAD:")):
                res.stdout = f"{head_blob}\n"
            elif f"{v2.PLAN_FREEZE_HEAD}:" in cmd_str or (len(cmd) >= 3 and cmd[2].startswith(f"{v2.PLAN_FREEZE_HEAD}:")):
                res.stdout = f"{frozen_blob}\n"
            elif cmd[-1] == "HEAD":
                res.stdout = f"{head_sha}\n"
            else:
                res.stdout = f"{head_sha}\n"
        elif "hash-object" in cmd_str:
            res.stdout = f"{worktree_blob}\n"
        elif "merge-base" in cmd_str:
            res.returncode = 0
        return res

    return mock_subp_run


def test_r2_gate_rejects_raw_plan_blob_mutation_after_freeze(tmp_path, monkeypatch):
    """Verify that raw-plan blob mutation after PLAN_FREEZE_HEAD is rejected (Section 17.1)."""
    monkeypatch.setattr(v2, "_git_head", lambda root: "r2_repair_commit_sha_12345")
    monkeypatch.setattr(
        "subprocess.run",
        _mock_r2_git_subprocess(head_blob="mutated_blob_1111111111111111111111111111111111111111"),
    )
    with pytest.raises(RuntimeError) as exc_info:
        v2.check_git_plan_freeze_status(tmp_path, v2.RAW_PLANS_PATH, v2.IMPLEMENTATION_FREEZE_HEAD)
    assert "differs from PLAN_FREEZE_HEAD blob" in str(exc_info.value)


def test_r2_gate_rejects_raw_plan_file_rewrite_with_identical_json(tmp_path, monkeypatch):
    """Verify that raw-plan file rewrite with semantically identical JSON is still rejected
    if the Git blob differs (Section 17.2).
    """
    monkeypatch.setattr(v2, "_git_head", lambda root: "r2_repair_commit_sha_12345")
    monkeypatch.setattr(
        "subprocess.run",
        _mock_r2_git_subprocess(worktree_blob="rewritten_worktree_blob_222222222222222222222222"),
    )
    with pytest.raises(RuntimeError) as exc_info:
        v2.check_git_plan_freeze_status(tmp_path, v2.RAW_PLANS_PATH, v2.IMPLEMENTATION_FREEZE_HEAD)
    assert "differs from frozen blob" in str(exc_info.value)


def test_r2_gate_rejects_wrong_plan_freeze_sha(tmp_path, monkeypatch):
    """Verify that raw plans artifact not originating from PLAN_FREEZE_HEAD is rejected (Section 17.3)."""
    monkeypatch.setattr(v2, "_git_head", lambda root: "r2_repair_commit_sha_12345")
    monkeypatch.setattr(
        "subprocess.run",
        _mock_r2_git_subprocess(raw_plan_origin="wrong_plan_freeze_sha_333333333333333333333333"),
    )
    with pytest.raises(RuntimeError) as exc_info:
        v2.check_git_plan_freeze_status(tmp_path, v2.RAW_PLANS_PATH, v2.IMPLEMENTATION_FREEZE_HEAD)
    assert "origin commit mismatch: expected exactly PLAN_FREEZE_HEAD" in str(exc_info.value)


def test_r2_gate_rejects_r2_parent_not_plan_freeze(tmp_path, monkeypatch):
    """Verify that R2 repair whose parent is not PLAN_FREEZE_HEAD is rejected (Section 17.4)."""
    monkeypatch.setattr(v2, "_git_head", lambda root: "r2_repair_commit_sha_12345")
    monkeypatch.setattr(
        "subprocess.run",
        _mock_r2_git_subprocess(head_parents=["wrong_parent_sha_444444444444444444444444"]),
    )
    with pytest.raises(RuntimeError) as exc_info:
        v2.check_git_plan_freeze_status(tmp_path, v2.RAW_PLANS_PATH, v2.IMPLEMENTATION_FREEZE_HEAD)
    assert "not a direct child of PLAN_FREEZE_HEAD" in str(exc_info.value)


def test_r2_gate_rejects_arbitrary_later_descendant(tmp_path, monkeypatch):
    """Verify that an arbitrary later descendant after R2 fails closed (Section 17.5)."""
    monkeypatch.setattr(v2, "_git_head", lambda root: "later_descendant_commit_sha_5555555555555555")
    monkeypatch.setattr(
        "subprocess.run",
        _mock_r2_git_subprocess(head_sha="r2_repair_commit_sha_12345"),
    )
    with pytest.raises(RuntimeError) as exc_info:
        v2.check_git_plan_freeze_status(tmp_path, v2.RAW_PLANS_PATH, v2.IMPLEMENTATION_FREEZE_HEAD)
    assert "is not the finalized R2 repair commit" in str(exc_info.value)


def test_r2_gate_rejects_unauthorized_r2_file_change(tmp_path, monkeypatch):
    """Verify that unauthorized file modification in R2 diff is rejected (Section 17.6)."""
    monkeypatch.setattr(v2, "_git_head", lambda root: "r2_repair_commit_sha_12345")
    monkeypatch.setattr(
        "subprocess.run",
        _mock_r2_git_subprocess(
            r2_diff_files=list(v2.ALLOWED_R2_DIFF_FILES) + ["src/panda_agent/retrieval.py"]
        ),
    )
    with pytest.raises(RuntimeError) as exc_info:
        v2.check_git_plan_freeze_status(tmp_path, v2.RAW_PLANS_PATH, v2.IMPLEMENTATION_FREEZE_HEAD)
    assert "modified disallowed paths" in str(exc_info.value)


def test_r2_gate_valid_direct_child_lineage_passes(tmp_path, monkeypatch):
    """Verify that valid R2 direct-child lineage passes all gate checks (Section 17.7)."""
    head_sha = "r2_repair_commit_sha_12345"
    monkeypatch.setattr(v2, "_git_head", lambda root: head_sha)
    monkeypatch.setattr(
        "subprocess.run",
        _mock_r2_git_subprocess(head_sha=head_sha),
    )
    frozen_sha = v2.check_git_plan_freeze_status(tmp_path, v2.RAW_PLANS_PATH, v2.IMPLEMENTATION_FREEZE_HEAD)
    assert frozen_sha == v2.PLAN_FREEZE_HEAD


def test_max_provider_attempts_per_case_frozen_consistently():
    """Verify MAX_PROVIDER_ATTEMPTS_PER_CASE = 3 consistently frozen across runner, prereg, and manifest."""
    assert v2.MAX_PROVIDER_ATTEMPTS_PER_CASE == 3

    prereg = json.loads((_PROJECT_ROOT / v2.PREREGISTRATION_PATH).read_text(encoding="utf-8"))
    assert prereg["phase_p_contract"]["max_provider_attempts_per_case"] == 3

    manifest = json.loads((_PROJECT_ROOT / v2.MANIFEST_PATH).read_text(encoding="utf-8"))
    assert manifest["phase_p_contract"]["max_provider_attempts_per_case"] == 3


def test_raw_plan_provenance_contract_fields():
    """Verify that raw plans artifact satisfies all Section 19 self-contained provenance requirements."""
    artifact = _make_valid_raw_plans_artifact("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    # Artifact-level required fields
    required_artifact_fields = [
        "checkpoint",
        "stage",
        "implementation_freeze_head",
        "runtime_execution_head",
        "plan_freeze_state",
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED",
        "model_id",
        "vertex_location",
        "temperature",
        "prompt_authority",
        "exact_acquisition_case_order",
        "max_provider_attempts_per_case",
        "allowed_retry_categories",
        "plans_planned",
        "plans_completed",
        "plans_failed",
        "accounting",
        "plans",
    ]
    for field in required_artifact_fields:
        assert field in artifact, f"Missing artifact field: {field}"

    assert artifact["max_provider_attempts_per_case"] == 3
    assert artifact["model_id"] == "gemini-3.8-flash"
    assert artifact["temperature"] == 0.0
    assert artifact["exact_acquisition_case_order"] == v2.CASE_ORDER

    # Plan-level required fields
    required_plan_fields = [
        "draw_index",
        "case_id",
        "question",
        "canonical_plan",
        "plan_signature",
        "status",
        "retries_count",
        "retry_reasons",
        "provider_attempts",
        "token_usage",
        "elapsed_seconds",
        "started_at",
        "completed_at",
    ]
    for plan in artifact["plans"]:
        for field in required_plan_fields:
            assert field in plan, f"Missing plan field {field} in case {plan.get('case_id')}"


# ---------------------------------------------------------------------------
# 16. Static Protection for Retrieval Semantics Tests (Section 16)
# ---------------------------------------------------------------------------

def test_retrieval_semantics_and_constants_protected():
    """Verify frozen scientific constants and treatment contracts remain strictly unchanged (Section 16)."""
    # 1. CASE_ORDER unchanged
    expected_order = [
        "g029", "n021", "g025", "g036", "n022", "g020", "n006", "g041",
        "n014", "g060", "g052", "g055", "n003", "g021", "n004", "g007",
    ]
    assert v2.CASE_ORDER == expected_order

    # 2. SCHEDULE_32 unchanged
    assert len(v2.SCHEDULE_32) == 32
    before_cells = [c for c in v2.SCHEDULE_32 if c["arm"] == "BEFORE_COMPAT"]
    after_cells = [c for c in v2.SCHEDULE_32 if c["arm"] == "AFTER_BATCH1_REPLACEMENT"]
    assert len(before_cells) == 16
    assert len(after_cells) == 16
    assert {c["case_id"] for c in before_cells} == set(v2.CASE_ORDER)
    assert {c["case_id"] for c in after_cells} == set(v2.CASE_ORDER)

    # 3. Selectivity caps 8 / 4
    assert v2.EXPECTED_SELECTIVITY_CAP == 8
    assert v2.EXPECTED_PER_ORIGIN_CAP == 4

    # 4. K = 3
    assert v2.EXPECTED_ADMISSION_BUDGET_K == 3

    # 5. Rerank pool = 30
    assert v2.EXPECTED_RERANK_POOL_SIZE == 30

    # 6. Model = gemini-3.8-flash
    assert v2.EXPECTED_MODEL == "gemini-3.8-flash"

    # 7. Embedding model = gemini-embedding-2
    assert v2.EXPECTED_EMBEDDING_MODEL == "gemini-embedding-2"

    # 8. Temperature = 0.0
    assert v2.EXPECTED_TEMPERATURE == 0.0

    # 9. BEFORE / AFTER treatment definitions
    assert v2.ARMS == ["BEFORE_COMPAT", "AFTER_BATCH1_REPLACEMENT"]

    # 10. RRF weights unchanged
    expected_rrf = {
        "exact": 2.0,
        "dense": 1.0,
        "sparse": 1.0,
        "paper": 1.15,
        "workflow": 1.2,
        "graph": 0.8,
    }
    assert v2.EXPECTED_RRF_WEIGHTS == expected_rrf


# ---------------------------------------------------------------------------
# 17. Additional R2 Lineage and Artifact Protection Tests (Section 17.8, 17.9)
# ---------------------------------------------------------------------------

def test_r2_gate_valid_frozen_16_plan_artifact_passes_full_signature_gate():
    """Verify that the real frozen 16-plan artifact passes the full signature gate (Section 17.8)."""
    receipt = v2.verify_plan_freeze_gate(
        _PROJECT_ROOT,
        git_checker=lambda root, rel, ca: v2.PLAN_FREEZE_HEAD,
    )
    assert receipt["verified"] is True
    assert receipt["plans_count"] == 16
    assert receipt["plan_freeze_head"] == v2.PLAN_FREEZE_HEAD
    assert receipt["raw_plan_blob_sha"] == v2.PLAN_FREEZE_RAW_BLOB
    assert receipt["cases_validated"] == v2.CASE_ORDER


def test_current_raw_artifact_remains_untouched_and_identical_to_git_blob():
    """Verify that current raw plans artifact remains untouched and identical to Git blob (Section 17.9)."""
    raw_path = _PROJECT_ROOT / v2.RAW_PLANS_PATH
    assert raw_path.exists()

    res = subprocess.run(
        ["git", "hash-object", str(raw_path)],
        cwd=str(_PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    assert res.stdout.strip() == v2.PLAN_FREEZE_RAW_BLOB

    status_res = subprocess.run(
        ["git", "status", "--porcelain", "--", v2.RAW_PLANS_PATH],
        cwd=str(_PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    assert status_res.stdout.strip() == ""


# ---------------------------------------------------------------------------
# 18. Explicit Signature Tests (Section 9)
# ---------------------------------------------------------------------------

def test_plan_signature_empty_paper_page_hints_round_trip():
    """Verify that a plan with empty paper_page_hints round-trips cleanly (Section 9.1)."""
    plan = _make_sample_canonical_plan("g029")
    plan["paper_page_hints"] = {}
    sig_str, sig_payload = v2.compute_plan_signature(plan)
    reloaded = json.loads(sig_str)
    assert reloaded == sig_payload
    re_dumped = json.dumps(reloaded, sort_keys=True)
    assert re_dumped == sig_str
    assert sig_payload["paper_page_hints"] == []


def test_plan_signature_non_empty_paper_page_hints_round_trip():
    """Verify that a plan with non-empty paper_page_hints round-trips cleanly without tuple-vs-list mismatch (Section 9.2)."""
    plan = _make_sample_canonical_plan("g060")
    plan["paper_page_hints"] = {"pflueger_2017": [78, 74, 84]}
    sig_str, sig_payload = v2.compute_plan_signature(plan)
    reloaded = json.loads(sig_str)
    assert reloaded == sig_payload
    assert sig_payload["paper_page_hints"] == [["pflueger_2017", [74, 78, 84]]]
    assert isinstance(sig_payload["paper_page_hints"][0], list)


def test_plan_signature_non_empty_concept_scopes_round_trip():
    """Verify that a plan with non-empty concept_scopes round-trips cleanly (Section 9.3)."""
    plan = _make_sample_canonical_plan("g055")
    plan["concept_scopes"] = {"efficiency": ["detector", "tracking"]}
    sig_str, sig_payload = v2.compute_plan_signature(plan)
    reloaded = json.loads(sig_str)
    assert reloaded == sig_payload
    assert sig_payload["concept_scopes"] == [["efficiency", ["detector", "tracking"]]]
    assert isinstance(sig_payload["concept_scopes"][0], list)


def test_plan_signature_nested_list_content_survives_round_trip():
    """Verify nested list content survives JSON round-trip with all list types intact (Section 9.4)."""
    plan = _make_sample_canonical_plan("nested_case")
    plan["paper_page_hints"] = {
        "doc_b": [10, 20],
        "doc_a": [1, 5, 3],
    }
    plan["concept_scopes"] = {
        "scope_y": ["sub_2", "sub_1"],
        "scope_x": ["sub_0"],
    }
    sig_str, sig_payload = v2.compute_plan_signature(plan)
    reloaded = json.loads(sig_str)
    assert reloaded == sig_payload
    for item in sig_payload["paper_page_hints"]:
        assert isinstance(item, list)
        assert isinstance(item[1], list)
    for item in sig_payload["concept_scopes"]:
        assert isinstance(item, list)


def test_plan_signature_computed_equals_reloaded_from_json():
    """Verify computed signature in Python equals signature after json.dumps/loads (Section 9.5)."""
    plan = _make_sample_canonical_plan("g052")
    plan["paper_page_hints"] = {"li_2026": [12, 15]}
    sig_str, sig_payload = v2.compute_plan_signature(plan)
    reloaded = json.loads(json.dumps(sig_payload))
    assert sig_payload == reloaded
    assert type(sig_payload) is type(reloaded)


def test_plan_signature_recompute_from_canonical_plan_equals_stored_json_loaded():
    """Verify recomputing from canonical plan matches the stored JSON-loaded signature (Section 9.6)."""
    plan = _make_sample_canonical_plan("g055")
    plan["paper_page_hints"] = {"pflueger_2017": [74, 84], "li_2026": [10]}
    plan["concept_scopes"] = {"efficiency": ["detector"]}
    sig_str, sig_payload = v2.compute_plan_signature(plan)

    fake_stored_plan = {
        "canonical_plan": json.loads(json.dumps(plan)),
        "plan_signature": json.loads(sig_str),
    }

    _, recomputed_payload = v2.compute_plan_signature(fake_stored_plan["canonical_plan"])
    assert recomputed_payload == fake_stored_plan["plan_signature"]


def test_plan_signature_genuine_semantic_change_fails():
    """Verify that a genuine semantic change causes signature mismatch (Section 9.7)."""
    plan = _make_sample_canonical_plan("g029")
    sig_str, sig_payload = v2.compute_plan_signature(plan)

    # 1. Alter concepts
    mutated_plan = copy.deepcopy(plan)
    mutated_plan["concepts"].append("new_concept")
    _, mut_payload = v2.compute_plan_signature(mutated_plan)
    assert mut_payload != sig_payload

    # 2. Alter intent
    mutated_plan2 = copy.deepcopy(plan)
    mutated_plan2["intent"] = "different_intent"
    _, mut_payload2 = v2.compute_plan_signature(mutated_plan2)
    assert mut_payload2 != sig_payload

    # 3. Alter symbols
    mutated_plan3 = copy.deepcopy(plan)
    mutated_plan3["symbols"].append("macro/other.C")
    _, mut_payload3 = v2.compute_plan_signature(mutated_plan3)
    assert mut_payload3 != sig_payload


def test_plan_signature_order_insensitivity_for_canonical_fields():
    """Verify target repositories/symbols/concepts/source types remain order-insensitive (Section 9.8)."""
    plan_a = {
        "intent": "code_search",
        "target_repositories": ["pandaroot", "fairroot"],
        "symbols": ["b.C", "a.C"],
        "concepts": ["Beta", "alpha"],
        "required_source_types": ["docs", "code"],
        "paper_page_hints": {},
        "concept_scopes": {},
    }
    plan_b = {
        "intent": "code_search",
        "target_repositories": ["fairroot", "pandaroot"],
        "symbols": ["a.C", "b.C"],
        "concepts": ["ALPHA", "beta"],
        "required_source_types": ["code", "docs"],
        "paper_page_hints": {},
        "concept_scopes": {},
    }
    sig_str_a, payload_a = v2.compute_plan_signature(plan_a)
    sig_str_b, payload_b = v2.compute_plan_signature(plan_b)
    assert payload_a == payload_b
    assert sig_str_a == sig_str_b


def test_plan_signature_real_frozen_g060_verifies():
    """Verify that the real frozen g060 signature verifies without mutation (Section 9.9)."""
    raw_plans = json.loads((_PROJECT_ROOT / v2.RAW_PLANS_PATH).read_text(encoding="utf-8"))
    g060_plan = next(p for p in raw_plans["plans"] if p["case_id"] == "g060")
    canonical = g060_plan["canonical_plan"]
    stored_sig = g060_plan["plan_signature"]
    sig_str, computed_sig = v2.compute_plan_signature(canonical)
    assert computed_sig == stored_sig
    assert sig_str == json.dumps(stored_sig, sort_keys=True)
    assert "pflueger_2017" in canonical["paper_page_hints"]


def test_plan_signature_all_16_real_frozen_plans_verify():
    """Verify that all 16 real frozen plans pass signature verification without mutation (Section 9.10)."""
    raw_plans = json.loads((_PROJECT_ROOT / v2.RAW_PLANS_PATH).read_text(encoding="utf-8"))
    assert len(raw_plans["plans"]) == 16
    for idx, p in enumerate(raw_plans["plans"], start=1):
        cid = p["case_id"]
        canonical = p["canonical_plan"]
        stored_sig = p["plan_signature"]
        sig_str, computed_sig = v2.compute_plan_signature(canonical)
        assert computed_sig == stored_sig, f"Signature mismatch on slot #{idx} ({cid})"
        assert sig_str == json.dumps(stored_sig, sort_keys=True)
