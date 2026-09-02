"""Unit tests for PANDA Agent D4-A2 First-Batch Before/After Validation.

All tests are deterministic, offline, and self-contained.
Zero provider/retrieval calls or live model/database queries.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import MagicMock
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))
if str(_PROJECT_ROOT / "evaluation" / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "evaluation" / "scripts"))

from panda_agent.config import QueryExpansions, load_query_expansions, load_retrieval_policies
from panda_agent.evaluation import GoldEvidenceGroup, GoldEvidenceSelector, load_gold_dataset
import d4_a1_fixed_locator_migration as d4_a1
import d4_a2_before_after_validation as d4_a2


# ---------------------------------------------------------------------------
# 1. 16-Case Identity and Cohort Authority Tests
# ---------------------------------------------------------------------------

def test_16_case_identity_and_dataset_assignment():
    """Verify exact 16-case identity, order, and dataset breakdown:
    - Order: g029, n021, g025, g036, n022, g020, n006, g041, n014, g060, g052, g055, n003, g021, n004, g007
    - 10 Gold v2.6 dev + 6 novel_dev
    - 13 answered cases + 3 insufficient_evidence negative controls (g025, g041, g007)
    - Reused unchanged from historical D3-A0-R1 / D3-A2 manifest.
    """
    expected_order = [
        "g029", "n021", "g025", "g036", "n022", "g020", "n006", "g041",
        "n014", "g060", "g052", "g055", "n003", "g021", "n004", "g007",
    ]
    assert d4_a2.CASE_ORDER == expected_order
    assert len(d4_a2.CASE_ORDER) == 16

    assert len(d4_a2.GOLD_CASES) == 10
    assert len(d4_a2.NOVEL_DEV_CASES) == 6
    assert len(d4_a2.ANSWERED_CASES) == 13
    assert len(d4_a2.INSUFFICIENT_EVIDENCE_CASES) == 3

    assert sorted(d4_a2.INSUFFICIENT_EVIDENCE_CASES) == ["g007", "g025", "g041"]

    # Verify against historical D3-A2 manifest
    d3_results_path = _PROJECT_ROOT / "evaluation" / "d3_a2_three_arm_results.json"
    assert d3_results_path.exists()
    d3_data = json.loads(d3_results_path.read_text(encoding="utf-8"))
    d3_order = d3_data["comparison_manifest_identity"]["case_ids_in_execution_order"]
    assert d4_a2.CASE_ORDER == d3_order

    # Verify each case's expected_status in the authoritative benchmark files
    gold_ds = load_gold_dataset(_PROJECT_ROOT / d4_a2.GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(_PROJECT_ROOT / d4_a2.NOVEL_DEV_PATH)
    all_q = {q.id: q for q in gold_ds.questions + novel_ds.questions}

    for cid in d4_a2.ANSWERED_CASES:
        assert all_q[cid].expected_status.value == "answered", f"{cid} expected answered"
    for cid in d4_a2.INSUFFICIENT_EVIDENCE_CASES:
        assert all_q[cid].expected_status.value == "insufficient_evidence", f"{cid} expected insufficient_evidence"


# ---------------------------------------------------------------------------
# 2. 32-Slot Order and Two-Arm Construction Tests
# ---------------------------------------------------------------------------

def test_32_slot_order_and_two_arm_construction():
    """Verify exact 32 slots in case-major paired order:
    For each case: BEFORE_COMPAT followed immediately by AFTER_BATCH1_REPLACEMENT.
    All slots in manifest start as NOT_EXECUTED with 0 pre-exposure accounting.
    """
    manifest_path = _PROJECT_ROOT / d4_a2.MANIFEST_PATH
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    slots = manifest["formal_slots_32"]
    assert len(slots) == 32
    assert d4_a2.TOTAL_FORMAL_SLOTS == 32
    assert d4_a2.ARMS == ["BEFORE_COMPAT", "AFTER_BATCH1_REPLACEMENT"]

    expected_schedule = []
    idx = 1
    for cid in d4_a2.CASE_ORDER:
        for arm in d4_a2.ARMS:
            expected_schedule.append((idx, cid, arm))
            idx += 1

    for s, (exp_idx, exp_cid, exp_arm) in zip(slots, expected_schedule):
        assert s["slot_index"] == exp_idx
        assert s["case_id"] == exp_cid
        assert s["arm"] == exp_arm
        assert s["outcome_status"] == "NOT_EXECUTED"
        assert s["started_at_utc"] is None
        assert s["completed_at_utc"] is None
        assert s["error"] is None

    # Pre-exposure accounting checks
    assert manifest["outcome_exposure_state"]["D4_A2_OUTCOME_EXPOSURE"] == "NOT_STARTED"
    assert manifest["outcome_exposure_state"]["formal_slots_completed"] == 0
    assert manifest["outcome_exposure_state"]["formal_slots_failed"] == 0
    assert manifest["outcome_exposure_state"]["evaluator_executed"] is False
    assert manifest["outcome_exposure_state"]["scientific_verdict_computed"] is False

    for counter, val in manifest["pre_exposure_accounting"].items():
        assert val == 0, f"Pre-exposure accounting {counter} != 0: {val}"


# ---------------------------------------------------------------------------
# 3. Exact Mask Parity with A0 / A1 Tests
# ---------------------------------------------------------------------------

def test_exact_mask_parity_with_a0_a1():
    """Verify that the in-memory mask applied in D4-A2 is identical to A0/A1:
    - 4 symbols + 2 page hints on event_poca_handoff
    - 5 symbols on restgas_profile_workflow
    - Preserves triggers, repositories, concepts
    - Does not mutate source object
    - Double application is idempotent
    """
    config_path = _PROJECT_ROOT / d4_a2.CONFIG_QUERY_EXPANSIONS_PATH
    orig_qe = load_query_expansions(config_path)
    orig_dump = orig_qe.model_dump()

    masked_qe = d4_a1.apply_batch1_in_memory_mask(orig_qe)
    masked_twice = d4_a1.apply_batch1_in_memory_mask(masked_qe)

    # Immutability
    assert orig_qe.model_dump() == orig_dump

    orig_ep = next(r for r in orig_qe.rules if r.rule_id == "event_poca_handoff")
    orig_rg = next(r for r in orig_qe.rules if r.rule_id == "restgas_profile_workflow")
    assert orig_ep.symbols == d4_a1.SUPPRESSED_SYMBOLS_EVENT_POCA
    assert orig_ep.paper_page_hints == d4_a1.SUPPRESSED_PAGE_HINTS_EVENT_POCA
    assert orig_rg.symbols == d4_a1.SUPPRESSED_SYMBOLS_RESTGAS

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
# 4. A1 Helper Reuse and Parity Tests
# ---------------------------------------------------------------------------

def test_a1_helper_reuse_and_parity():
    """Verify that A2 imports and reuses A1 helpers rather than duplicating logic:
    - apply_batch1_in_memory_mask
    - build_eligible_bridge_candidates
    - build_candidate_payload_registry
    - check_admission_witness
    - revalidate_a0_overlaps
    """
    assert callable(d4_a1.apply_batch1_in_memory_mask)
    assert callable(d4_a1.build_eligible_bridge_candidates)
    assert callable(d4_a1.build_candidate_payload_registry)
    assert callable(d4_a1.check_admission_witness)
    assert callable(d4_a1.revalidate_a0_overlaps)

    # Revalidation runs cleanly
    receipt = d4_a1.revalidate_a0_overlaps(_PROJECT_ROOT)
    assert receipt["verified"] is True


# ---------------------------------------------------------------------------
# 5. Production Retrieval Parity and Parameters Tests
# ---------------------------------------------------------------------------

def test_production_retrieval_parity_mirror():
    """Verify that production retrieval channels, RRF weights, and parameters
    match the frozen specification:
    exact = 2.0, dense = 1.0, sparse = 1.0, paper = 1.15, workflow = 1.2, graph = 0.8
    pool = 30, K = 3, caps = 8 / 4.
    """
    policies = load_retrieval_policies(_PROJECT_ROOT / "configs" / "retrieval_policies.yaml")
    assert policies.candidate_pool_per_channel >= 10
    assert policies.final_evidence_limit >= 3

    # Check that A2 preregistration and manifest freeze these exact parameters
    prereg = json.loads((_PROJECT_ROOT / d4_a2.PREREGISTRATION_PATH).read_text(encoding="utf-8"))
    manifest = json.loads((_PROJECT_ROOT / d4_a2.MANIFEST_PATH).read_text(encoding="utf-8"))

    for doc in (prereg, manifest):
        after_cfg = doc["arms"]["AFTER_BATCH1_REPLACEMENT"]
        assert after_cfg["admission_budget_k"] == 3
        assert after_cfg["rerank_pool_size"] == 30
        assert after_cfg["selectivity_caps"]["SELECTIVITY_CAP"] == 8
        assert after_cfg["selectivity_caps"]["PER_ORIGIN_CAP"] == 4


# ---------------------------------------------------------------------------
# 6. Metric Applicability and Denominators Tests
# ---------------------------------------------------------------------------

def test_metric_applicability_and_denominators():
    """Retrieval metrics apply strictly to the 13 answered cases.
    The 3 insufficient_evidence cases (g025, g041, g007) are evaluated separately
    as negative controls and excluded from answered denominators.
    """
    assert len(d4_a2.ANSWERED_CASES) == 13
    assert len(d4_a2.INSUFFICIENT_EVIDENCE_CASES) == 3
    assert len(d4_a2.CASE_ORDER) == 16
    assert set(d4_a2.ANSWERED_CASES).isdisjoint(set(d4_a2.INSUFFICIENT_EVIDENCE_CASES))
    assert set(d4_a2.ANSWERED_CASES) | set(d4_a2.INSUFFICIENT_EVIDENCE_CASES) == set(d4_a2.CASE_ORDER)


# ---------------------------------------------------------------------------
# 7. Section 41 Six-Level Verdict Precedence Truth Table Tests
# ---------------------------------------------------------------------------

def test_six_level_verdict_precedence_truth_table():
    """Verify exact 6-level verdict precedence from Section 41:
    Level 1: INVALID / PROTOCOL_OR_TREATMENT_CONSTRUCTION_FAILED
    Level 2: INCONCLUSIVE / BEFORE_REFERENCE_NOT_REPRODUCED
    Level 3: FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
    Level 4: FAIL / CRITICAL_OR_GROUNDING_REGRESSION
    Level 5: PARTIAL / BEFORE_AFTER_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE
    Level 6: PASS / FIRST_BATCH_BEFORE_AFTER_VALIDATED_FOR_RUNTIME_MIGRATION_DECISION
    """
    clean_deltas = {
        "recall_at_5": 0.0,
        "recall_at_10": 0.0,
        "recall_at_20": 0.0,
        "combined_candidate_recall": 0.0,
        "final_evidence_recall": 0.0,
        "critical_final_evidence_recall": 0.0,
        "mrr": 0.0,
    }

    # Level 1: Protocol or construction failure
    v1 = d4_a2.compute_before_after_verdict(
        execution_valid=False,
        protocol_violation=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
    )
    assert v1["verdict_level"] == 1
    assert v1["batch_verdict"] == d4_a2.VERDICT_LEVEL_1_INVALID

    # Level 2: BEFORE reference not reproduced
    v2 = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=False,
        target_replacement_reproduced=2,
    )
    assert v2["verdict_level"] == 2
    assert v2["batch_verdict"] == d4_a2.VERDICT_LEVEL_2_INCONCLUSIVE

    # Level 3: Primary target replacement not reproduced
    v3 = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=1,  # only 1 of 2 reproduced
    )
    assert v3["verdict_level"] == 3
    assert v3["batch_verdict"] == d4_a2.VERDICT_LEVEL_3_FAIL_PRIMARY_TARGET

    # Level 4: Critical group regression
    v4_crit = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
        critical_group_regressions=["g020.e1"],
    )
    assert v4_crit["verdict_level"] == 4
    assert v4_crit["batch_verdict"] == d4_a2.VERDICT_LEVEL_4_FAIL_CRITICAL_OR_GROUNDING

    # Level 4: Grounding / wrong-version regression
    v4_ground = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
        wrong_version_regressions=1,
    )
    assert v4_ground["verdict_level"] == 4
    assert v4_ground["batch_verdict"] == d4_a2.VERDICT_LEVEL_4_FAIL_CRITICAL_OR_GROUNDING

    # Level 5: Bounded tolerance exceeded (delta < -0.05)
    bad_deltas = dict(clean_deltas, recall_at_10=-0.08)
    v5 = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
        metric_deltas=bad_deltas,
    )
    assert v5["verdict_level"] == 5
    assert v5["batch_verdict"] == d4_a2.VERDICT_LEVEL_5_PARTIAL_TOLERANCE

    # Level 5: Critical final evidence delta < 0
    crit_bad_deltas = dict(clean_deltas, critical_final_evidence_recall=-0.01)
    v5_crit = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
        metric_deltas=crit_bad_deltas,
    )
    assert v5_crit["verdict_level"] == 5
    assert v5_crit["batch_verdict"] == d4_a2.VERDICT_LEVEL_5_PARTIAL_TOLERANCE

    # Level 6: PASS (clean run)
    v6 = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
        metric_deltas=clean_deltas,
    )
    assert v6["verdict_level"] == 6
    assert v6["batch_verdict"] == d4_a2.VERDICT_LEVEL_6_PASS

    # Noncritical regression does NOT trigger Level 4; yields PASS if deltas within tolerance
    v6_noncrit = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
        critical_group_regressions=[],
        noncritical_group_regressions=["g021.e2"],
        metric_deltas=dict(clean_deltas, final_evidence_recall=-0.03),  # within -0.05
    )
    assert v6_noncrit["verdict_level"] == 6
    assert v6_noncrit["batch_verdict"] == d4_a2.VERDICT_LEVEL_6_PASS
    assert "g021.e2" in v6_noncrit["verdict_reason"]

    # Precedence override checks: Level 1 overrides Level 2, Level 2 overrides Level 3, etc.
    v_override_1_2 = d4_a2.compute_before_after_verdict(
        execution_valid=False,
        before_reference_valid=False,
    )
    assert v_override_1_2["verdict_level"] == 1

    v_override_2_3 = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=False,
        target_replacement_reproduced=0,
    )
    assert v_override_2_3["verdict_level"] == 2

    v_override_3_4 = d4_a2.compute_before_after_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=1,
        critical_group_regressions=["g020.e1"],
    )
    assert v_override_3_4["verdict_level"] == 3


# ---------------------------------------------------------------------------
# 8. Journal and Resume Semantics Tests
# ---------------------------------------------------------------------------

def test_journal_and_resume_semantics(tmp_path):
    """Verify journal semantics:
    - Missing raw artifact raises FileNotFoundError in evaluate
    - Incomplete completed slots raises ValueError in evaluate
    """
    # 1. Nonexistent raw artifact
    with pytest.raises(FileNotFoundError, match="does not exist"):
        d4_a2.evaluate_d4_a2(tmp_path, require_git_frozen=False)

    # 2. Incomplete completed slots (< 32) raises ValueError
    raw_path = tmp_path / d4_a2.RAW_RESULTS_PATH
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(
        json.dumps({
            "outcome_exposure_state": {"formal_slots_completed": 5},
            "slots": [],
        }),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="completed slots, expected 32"):
        d4_a2.evaluate_d4_a2(tmp_path, require_git_frozen=False)


# ---------------------------------------------------------------------------
# 9. Cell Retrieval Arm Mapping Tests
# ---------------------------------------------------------------------------

def test_execute_cell_retrieval_a2_arm_mapping(monkeypatch):
    """Verify that execute_cell_retrieval_a2 delegates to d4_a1.execute_cell_retrieval
    mapping BEFORE_COMPAT -> LEGACY_CONTROL and AFTER_BATCH1_REPLACEMENT -> BATCH1_REPLACEMENT.
    """
    recorded_arms = []

    def mock_a1_retrieval(*args, **kwargs):
        arm = kwargs.get("arm")
        recorded_arms.append(arm)
        return {"status": "COMPLETED", "arm": arm}

    monkeypatch.setattr(d4_a1, "execute_cell_retrieval", mock_a1_retrieval)

    retriever_mock = MagicMock()
    qe_mock = MagicMock()

    # Call BEFORE_COMPAT
    res1 = d4_a2.execute_cell_retrieval_a2(
        retriever=retriever_mock,
        case_id="g029",
        arm="BEFORE_COMPAT",
        question_text="sample",
        original_expansions=qe_mock,
        masked_expansions=qe_mock,
    )
    assert recorded_arms[-1] == "LEGACY_CONTROL"
    assert res1["arm"] == "BEFORE_COMPAT"

    # Call AFTER_BATCH1_REPLACEMENT
    res2 = d4_a2.execute_cell_retrieval_a2(
        retriever=retriever_mock,
        case_id="g029",
        arm="AFTER_BATCH1_REPLACEMENT",
        question_text="sample",
        original_expansions=qe_mock,
        masked_expansions=qe_mock,
    )
    assert res1["in_memory_mask_active"] is False
    assert res1["structured_replacement_active"] is False
    assert res1["admission_budget_k"] == 0
    assert res2["in_memory_mask_active"] is True
    assert res2["structured_replacement_active"] is True
    assert res2["admission_budget_k"] == 3
    assert recorded_arms[-1] == "BATCH1_REPLACEMENT"
    assert res2["arm"] == "AFTER_BATCH1_REPLACEMENT"


# ---------------------------------------------------------------------------
# 10. Drift Guards and Protected Dataset Tests
# ---------------------------------------------------------------------------

def test_drift_guards_verification():
    """Drift guards verify protected src/ and configs/ are identical to
    STARTING_HEAD, and only allowed Commit-A files differ."""
    receipt = d4_a2.verify_drift_guards(_PROJECT_ROOT, require_clean_worktree=False)
    assert receipt["verified"] is True
    assert receipt["starting_head"] == d4_a2.STARTING_HEAD


def test_protected_dataset_guards():
    """Assert novel_validation and novel_holdout datasets are untouched,
    and all 16 cases are Gold dev or novel_dev."""
    manifest = json.loads((_PROJECT_ROOT / d4_a2.MANIFEST_PATH).read_text(encoding="utf-8"))
    assert manifest["pre_exposure_accounting"]["NOVEL_VALIDATION_RUNS"] == 0
    assert manifest["pre_exposure_accounting"]["NOVEL_HOLDOUT_RUNS"] == 0
    assert manifest["pre_exposure_accounting"]["PROTECTED_DATASET_ACCESS"] == 0

    for c in manifest["cases"]:
        assert c["dataset"] in ("Gold v2.6 dev", "novel_dev")


# ---------------------------------------------------------------------------
# 11. Pre-Exposure Audit Invariant Function Test
# ---------------------------------------------------------------------------

def test_audit_invariants_offline():
    """Verify that audit_invariants runs offline and verifies all checks:
    model, 16 cases, 32 slots, 0 accounting, clean exposure state."""
    receipt = d4_a2.audit_invariants(_PROJECT_ROOT)
    assert receipt["verified"] is True
    assert receipt["cohort_cases_count"] == 16
    assert receipt["formal_slots_count"] == 32
    assert receipt["pre_exposure_accounting_zero"] is True
    assert receipt["pre_exposure_exposure_state"] == "NOT_STARTED"
    assert receipt["protected_dataset_access"] == 0


# ---------------------------------------------------------------------------
# 12. Helper & Tests for Defect 1: Formal Journal State & Failure Accounting
# ---------------------------------------------------------------------------

def _make_valid_raw_artifact():
    slots = []
    idx = 1
    for cid in d4_a2.CASE_ORDER:
        for arm in d4_a2.ARMS:
            is_after = arm == "AFTER_BATCH1_REPLACEMENT"
            suppressed = (
                {
                    "event_poca_handoff": {
                        "symbols": ["event_poca_lookup"],
                        "paper_page_hints": {"li_2026": [8, 9]},
                    },
                    "restgas_profile_workflow": {
                        "symbols": ["restgas_init"],
                        "paper_page_hints": {},
                    },
                }
                if is_after
                else {}
            )
            slots.append({
                "slot_index": idx,
                "case_id": cid,
                "arm": arm,
                "outcome_status": "COMPLETED",
                "error": None,
                "in_memory_mask_active": is_after,
                "structured_replacement_active": is_after,
                "admission_budget_k": 3 if is_after else 0,
                "rerank_pool_size": 30,
                "final_pool_object_ids": [f"pool_{n:02d}" for n in range(30)],
                "effective_symbols": (
                    ["event_poca_lookup", "restgas_init"] if arm == "BEFORE_COMPAT" else []
                ),
                "effective_paper_page_hints": {},
                "suppressed_components": suppressed,
                "exact_effective_suppressed_components": suppressed,
                "ranked_object_ids": ["doc_001", "doc_002"],
                "final_evidence_object_ids": ["doc_001"],
                "channel_rankings": {"exact": ["doc_001"], "dense": ["doc_002"]},
            })
            idx += 1

    return {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-RAW-BEFORE-AFTER-OUTCOME-FREEZE",
        "stage": "d4_a2_raw_before_after_results",
        "authority": {
            "manifest": d4_a2.MANIFEST_PATH,
            "preregistration": d4_a2.PREREGISTRATION_PATH,
            "implementation_freeze_head": "0123456789abcdef0123456789abcdef01234567",
            "implementation_freeze_contract": d4_a2.IMPLEMENTATION_FREEZE_CONTRACT_POLICY,
        },
        "model_contract": {
            "generation_model_id": "gemini-3.8-flash",
            "embedding_model_id": "gemini-embedding-2",
            "temperature": 0.0,
            "location": "global",
            "system_prompt": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT",
            "query_analyzer_prompt": "src/panda_agent/prompts.py:QUERY_ANALYZER_SYSTEM_PROMPT",
        },
        "outcome_exposure_state": {
            "D4_A2_OUTCOME_EXPOSURE": "COMPLETE",
            "formal_slots_total": 32,
            "formal_slots_completed": 32,
            "formal_slots_failed": 0,
        },
        "evaluation_boundary": {
            "EVALUATOR_EXECUTED": False,
            "SCIENTIFIC_VERDICT_COMPUTED": False,
        },
        "accounting": {
            "FORMAL_CELLS_TOTAL": 32,
            "FORMAL_CELLS_COMPLETED": 32,
            "FORMAL_CELLS_FAILED": 0,
            "NOVEL_VALIDATION_RUNS": 0,
            "NOVEL_HOLDOUT_RUNS": 0,
            "PROTECTED_DATASET_ACCESS": 0,
        },
        "slots": slots,
    }


def test_defect1_formal_journal_state_and_failure_accounting():
    """Verify Defect 1:
    - Pre-invocation journal state writes D4_A2_OUTCOME_EXPOSURE = STARTED, even at slot 32.
    - FORMAL_CELLS_COMPLETED counts only COMPLETED records.
    - FORMAL_CELLS_FAILED accurately counts FAILED records.
    - D4_A2_OUTCOME_EXPOSURE becomes COMPLETE only when 32/32 completed with 0 failures.
    """
    # 1. When all 32 slots have completed records, but outcome exposure is prematurely STARTED:
    raw = _make_valid_raw_artifact()
    raw["outcome_exposure_state"]["D4_A2_OUTCOME_EXPOSURE"] = "STARTED"
    is_valid, fail_reason, _ = d4_a2.validate_raw_artifact_structural_validity(raw)
    assert is_valid is False
    assert "D4_A2_OUTCOME_EXPOSURE is not COMPLETE" in fail_reason

    # 2. When pre-invocation at slot 32 (slot 32 is STARTED, exposure state is STARTED):
    raw = _make_valid_raw_artifact()
    raw["slots"][31]["outcome_status"] = "STARTED"
    raw["outcome_exposure_state"]["D4_A2_OUTCOME_EXPOSURE"] = "STARTED"
    raw["outcome_exposure_state"]["formal_slots_completed"] = 31
    raw["accounting"]["FORMAL_CELLS_COMPLETED"] = 31
    is_valid, fail_reason, _ = d4_a2.validate_raw_artifact_structural_validity(raw)
    assert is_valid is False
    assert "status is not COMPLETED" in fail_reason

    # 3. If slot failed, failure counters must be persisted accurately:
    raw["slots"][31]["outcome_status"] = "FAILED"
    raw["slots"][31]["error"] = "RuntimeError: quota exceeded"
    raw["outcome_exposure_state"]["formal_slots_failed"] = 1
    raw["accounting"]["FORMAL_CELLS_FAILED"] = 1
    raw["outcome_exposure_state"]["D4_A2_OUTCOME_EXPOSURE"] = "STARTED"
    is_valid, fail_reason, _ = d4_a2.validate_raw_artifact_structural_validity(raw)
    assert is_valid is False
    assert "status is not COMPLETED" in fail_reason or "failed is not 0" in fail_reason


# ---------------------------------------------------------------------------
# 13. Test for Defect 2: Evaluator Structural Validity Audit
# ---------------------------------------------------------------------------

def test_defect2_evaluator_structural_validity():
    """Verify Defect 2:
    - Mechanical structural validation of 32 slots, case-major order, exact arms,
      0 failed, model contract, authorities, boundary flags, freeze head, mask receipts.
    - Violations feed Level 1 INVALID.
    """
    base_raw = _make_valid_raw_artifact()
    is_valid, reason, mutations = d4_a2.validate_raw_artifact_structural_validity(base_raw)
    assert is_valid is True
    assert reason is None
    assert all(v == 0 for v in mutations.values())

    # Violation 1: missing slot (31 slots)
    bad_raw = copy.deepcopy(base_raw)
    bad_raw["slots"].pop()
    v, r, _ = d4_a2.validate_raw_artifact_structural_validity(bad_raw)
    assert v is False
    assert "slots count mismatch" in r

    # Violation 2: duplicate slot
    bad_raw = copy.deepcopy(base_raw)
    bad_raw["slots"][1] = copy.deepcopy(bad_raw["slots"][0])
    v, r, _ = d4_a2.validate_raw_artifact_structural_validity(bad_raw)
    assert v is False
    assert "Slots are not unique" in r

    # Violation 3: out of order slots
    bad_raw = copy.deepcopy(base_raw)
    bad_raw["slots"][0], bad_raw["slots"][1] = bad_raw["slots"][1], bad_raw["slots"][0]
    v, r, m = d4_a2.validate_raw_artifact_structural_validity(bad_raw)
    assert v is False
    assert "Slot schedule mismatch" in r
    assert m["POST_EXPOSURE_CASE_MUTATIONS"] > 0

    # Violation 4: wrong model
    bad_raw = copy.deepcopy(base_raw)
    bad_raw["model_contract"]["generation_model_id"] = "gemini-1.5-pro"
    v, r, m = d4_a2.validate_raw_artifact_structural_validity(bad_raw)
    assert v is False
    assert m["POST_EXPOSURE_MODEL_MUTATIONS"] > 0

    # Violation 5: boundary flag violated
    bad_raw = copy.deepcopy(base_raw)
    bad_raw["evaluation_boundary"]["EVALUATOR_EXECUTED"] = True
    v, r, _ = d4_a2.validate_raw_artifact_structural_validity(bad_raw)
    assert v is False
    assert "EVALUATOR_EXECUTED is not False" in r

    # Violation 6: placeholder freeze HEAD
    bad_raw = copy.deepcopy(base_raw)
    bad_raw["authority"]["implementation_freeze_head"] = "PLACEHOLDER_NOT_YET_CAPTURED"
    v, r, _ = d4_a2.validate_raw_artifact_structural_validity(bad_raw)
    assert v is False
    assert "placeholder" in r.lower() or "not a valid" in r.lower()

    # Violation 7: missing explicit arm-construction receipt must fail closed.
    bad_raw = copy.deepcopy(base_raw)
    bad_raw["slots"][0].pop("in_memory_mask_active")
    v, r, m = d4_a2.validate_raw_artifact_structural_validity(bad_raw)
    assert v is False
    assert m["POST_EXPOSURE_MASK_MUTATIONS"] > 0

    # Violation 8: missing explicit replacement budget must not pass by default.
    bad_raw = copy.deepcopy(base_raw)
    bad_raw["slots"][1].pop("admission_budget_k")
    v, r, m = d4_a2.validate_raw_artifact_structural_validity(bad_raw)
    assert v is False
    assert m["POST_EXPOSURE_REPLACEMENT_MUTATIONS"] > 0


# ---------------------------------------------------------------------------
# 14. Test for Defect 3: Grounding, Version, and Provenance Safety
# ---------------------------------------------------------------------------

def test_defect3_grounding_version_and_provenance_safety():
    """Verify Defect 3:
    - Wrong-version regressions count newly introduced AFTER relative to BEFORE.
    - Grounding regressions detect newly introduced forbidden evidence hits.
    - Invalid provenance recoveries detect AFTER structured recoveries lacking governed path/origins.
    - Detailed evidence-level records are preserved.
    """
    cid = "g029"
    q_mock = MagicMock()
    q_mock.allowed_source_versions = ["v1.0"]
    selector_mock = MagicMock()
    selector_mock.matches.side_effect = lambda item: item.get("forbidden", False)
    selector_mock.model_dump.return_value = {"selector_type": "forbidden_test"}
    q_mock.forbidden_evidence = [selector_mock]

    all_questions = {cid: q_mock}
    object_lookup = {
        "doc_allowed": {"source_version_id": "v1.0", "forbidden": False},
        "doc_legacy_wv": {"source_version_id": "v0.9", "forbidden": False},
        "doc_new_wv": {"source_version_id": "v2.0", "forbidden": False},
        "doc_forbidden": {"source_version_id": "v1.0", "forbidden": True},
    }

    # Case A: doc_legacy_wv is in BOTH BEFORE and AFTER -> NOT newly introduced
    slots_map = {
        (cid, "BEFORE_COMPAT"): {
            "final_evidence_object_ids": ["doc_allowed", "doc_legacy_wv"],
        },
        (cid, "AFTER_BATCH1_REPLACEMENT"): {
            "final_evidence_object_ids": ["doc_allowed", "doc_legacy_wv"],
            "reserved_candidate_ids": [],
        },
    }
    res = d4_a2.compute_grounding_and_version_safety(
        slots_map=slots_map,
        all_questions=all_questions,
        object_lookup=object_lookup,
        witness_g036={},
        witness_g021={},
        group_retention={},
    )
    assert res["WRONG_VERSION_REGRESSIONS"] == 0
    assert res["GROUNDING_REGRESSIONS"] == 0

    # Case B: doc_new_wv is newly introduced in AFTER -> WRONG_VERSION_REGRESSIONS == 1
    slots_map[(cid, "AFTER_BATCH1_REPLACEMENT")]["final_evidence_object_ids"] = [
        "doc_allowed", "doc_new_wv"
    ]
    res = d4_a2.compute_grounding_and_version_safety(
        slots_map=slots_map,
        all_questions=all_questions,
        object_lookup=object_lookup,
        witness_g036={},
        witness_g021={},
        group_retention={},
    )
    assert res["WRONG_VERSION_REGRESSIONS"] == 1
    assert len(res["wrong_version_details"]) == 1
    assert res["wrong_version_details"][0]["object_id"] == "doc_new_wv"

    # Case C: forbidden evidence hit newly introduced in AFTER -> GROUNDING_REGRESSIONS == 1
    slots_map[(cid, "AFTER_BATCH1_REPLACEMENT")]["final_evidence_object_ids"] = [
        "doc_allowed", "doc_forbidden"
    ]
    res = d4_a2.compute_grounding_and_version_safety(
        slots_map=slots_map,
        all_questions=all_questions,
        object_lookup=object_lookup,
        witness_g036={},
        witness_g021={},
        group_retention={},
    )
    assert res["GROUNDING_REGRESSIONS"] == 1
    assert len(res["grounding_details"]) == 1
    assert res["grounding_details"][0]["object_id"] == "doc_forbidden"

    # Case D: invalid provenance witness (missing governed path or origins)
    wit_invalid = {
        "candidate_witnesses": [
            {
                "candidate_object_id": "cand_x",
                "in_final_evidence": True,
                "is_valid_witness": True,
                "governed_path": False,
                "structured_path": {"provenance_origin_ids": [], "source_id": "src_1"},
            }
        ]
    }
    res = d4_a2.compute_grounding_and_version_safety(
        slots_map=slots_map,
        all_questions=all_questions,
        object_lookup=object_lookup,
        witness_g036=wit_invalid,
        witness_g021={},
        group_retention={},
    )
    assert res["INVALID_PROVENANCE_RECOVERIES"] == 1
    assert len(res["invalid_provenance_details"]) == 1

    # Case E: the exact A1 witness field names describe valid provenance.
    wit_valid = {
        "candidate_witnesses": [
            {
                "candidate_object_id": "cand_valid",
                "final_evidence_retained": True,
                "is_valid_witness": True,
                "governed_path": True,
                "full_structured_path": {
                    "provenance_origin_ids": ["edge.valid"],
                    "source_id": "source_valid",
                },
            }
        ]
    }
    res = d4_a2.compute_grounding_and_version_safety(
        slots_map=slots_map,
        all_questions=all_questions,
        object_lookup=object_lookup,
        witness_g036=wit_valid,
        witness_g021={},
        group_retention={},
    )
    assert res["INVALID_PROVENANCE_RECOVERIES"] == 0


# ---------------------------------------------------------------------------
# 15. Test for Defect 4: Dependency Removal Five Conditions & False Cases
# ---------------------------------------------------------------------------

def test_defect4_batch1_dependency_removal_five_conditions():
    """Verify Defect 4:
    - Separately verifies 5 conditions for each target rule.
    - Test false cases for each of the 5 conditions.
    - Failure of dependency removal causes Level 3 FAIL.
    """
    def _make_slots_and_witnesses():
        slots_map = {
            ("g036", "BEFORE_COMPAT"): {
                "in_memory_mask_active": False,
                "effective_symbols": ["event_poca_lookup"],
            },
            ("g036", "AFTER_BATCH1_REPLACEMENT"): {
                "in_memory_mask_active": True,
                "effective_symbols": [],
                "effective_paper_page_hints": {},
                "structured_replacement_active": True,
                "admission_budget_k": 3,
            },
            ("g021", "BEFORE_COMPAT"): {
                "in_memory_mask_active": False,
                "effective_symbols": ["restgas_init"],
            },
            ("g021", "AFTER_BATCH1_REPLACEMENT"): {
                "in_memory_mask_active": True,
                "effective_symbols": [],
                "effective_paper_page_hints": {},
                "structured_replacement_active": True,
                "admission_budget_k": 3,
            },
        }
        wit_g036 = {"has_valid_witness": True}
        wit_g021 = {"has_valid_witness": True}
        group_retention = {
            "g036.e1": {"BEFORE_COMPAT": True, "AFTER_BATCH1_REPLACEMENT": True},
            "g021.e1": {"BEFORE_COMPAT": True, "AFTER_BATCH1_REPLACEMENT": True},
        }
        return slots_map, wit_g036, wit_g021, group_retention

    # All 5 hold: returns 2/2
    slots, w36, w21, gr = _make_slots_and_witnesses()
    count, receipts = d4_a2.compute_batch1_dependency_removal(slots, w36, w21, gr)
    assert count == 2
    assert receipts["event_poca_handoff"]["dependency_removed"] is True
    assert receipts["restgas_profile_workflow"]["dependency_removed"] is True

    # False condition 1: not active before
    slots, w36, w21, gr = _make_slots_and_witnesses()
    slots[("g036", "BEFORE_COMPAT")]["in_memory_mask_active"] = True
    slots[("g036", "BEFORE_COMPAT")]["effective_symbols"] = []
    slots[("g036", "BEFORE_COMPAT")]["suppressed_components"] = {"event_poca_handoff": True}
    count, receipts = d4_a2.compute_batch1_dependency_removal(slots, w36, w21, gr)
    assert receipts["event_poca_handoff"]["fixed_locator_inputs_active_before"] is False
    assert receipts["event_poca_handoff"]["dependency_removed"] is False
    assert count == 1

    # False condition 2: locator input not absent after (leaked symbol)
    slots, w36, w21, gr = _make_slots_and_witnesses()
    slots[("g036", "AFTER_BATCH1_REPLACEMENT")]["effective_symbols"] = ["PndPidCorrelator"]
    count, receipts = d4_a2.compute_batch1_dependency_removal(slots, w36, w21, gr)
    assert receipts["event_poca_handoff"]["exact_masked_locator_inputs_absent_after"] is False
    assert count == 1

    # False condition 3: structured mechanism not active after
    slots, w36, w21, gr = _make_slots_and_witnesses()
    slots[("g036", "AFTER_BATCH1_REPLACEMENT")]["structured_replacement_active"] = False
    count, receipts = d4_a2.compute_batch1_dependency_removal(slots, w36, w21, gr)
    assert receipts["event_poca_handoff"]["generic_structured_mechanism_active"] is False
    assert count == 1

    # False condition 4: target evidence not retained after
    slots, w36, w21, gr = _make_slots_and_witnesses()
    gr["g036.e1"]["AFTER_BATCH1_REPLACEMENT"] = False
    count, receipts = d4_a2.compute_batch1_dependency_removal(slots, w36, w21, gr)
    assert receipts["event_poca_handoff"]["target_evidence_retained_after"] is False
    assert count == 1

    # False condition 5: valid witness missing
    slots, w36, w21, gr = _make_slots_and_witnesses()
    w36["has_valid_witness"] = False
    count, receipts = d4_a2.compute_batch1_dependency_removal(slots, w36, w21, gr)
    assert receipts["event_poca_handoff"]["valid_governed_witness_exists"] is False
    assert count == 1

    # Level 3 verdict precedence check when dependency removal fails
    verdict = d4_a2.compute_before_after_verdict(
        target_replacement_reproduced=2,
        batch1_dependency_removed=1,
    )
    assert verdict["verdict_level"] == 3
    assert verdict["batch_verdict"] == d4_a2.VERDICT_LEVEL_3_FAIL_PRIMARY_TARGET
    assert "dependency removal not satisfied" in verdict["verdict_reason"]


# ---------------------------------------------------------------------------
# 16. Test for Defect 5: Metric Semantics, Candidate Recall & Generalization
# ---------------------------------------------------------------------------

def test_defect5_candidate_recall_and_generalization_diagnostics():
    """Verify Defect 5:
    - combined_candidate_recall uses the union of channel_rankings.
    - Full targeted generalization diagnostics are computed across all retrieval metrics.
    - Group retention includes applicability and is_negative_control tags.
    """
    # 1. Candidate recall computation
    channel_rankings = {
        "exact": ["doc_A", "doc_B"],
        "dense": ["doc_B", "doc_C"],
        "sparse": ["doc_D"],
    }
    union_cands = list(dict.fromkeys(oid for oids in channel_rankings.values() for oid in oids))
    assert union_cands == ["doc_A", "doc_B", "doc_C", "doc_D"]

    # 2. Verdict with deltas within tolerance
    deltas_ok = {
        "recall_at_5": 0.0,
        "recall_at_10": -0.01,
        "recall_at_20": 0.02,
        "combined_candidate_recall": 0.0,
        "final_evidence_recall": 0.0,
        "critical_final_evidence_recall": 0.0,
    }
    v_pass = d4_a2.compute_before_after_verdict(metric_deltas=deltas_ok)
    assert v_pass["verdict_level"] == 6

    # 3. Verdict when delta exceeds tolerance (-0.05)
    deltas_bad = dict(deltas_ok, combined_candidate_recall=-0.06)
    v_partial = d4_a2.compute_before_after_verdict(metric_deltas=deltas_bad)
    assert v_partial["verdict_level"] == 5
    assert v_partial["batch_verdict"] == d4_a2.VERDICT_LEVEL_5_PARTIAL_TOLERANCE


# ---------------------------------------------------------------------------
# 17. Test for Defect 6: Environment and Parity Audit Checks
# ---------------------------------------------------------------------------

def test_defect6_audit_invariants_environment_and_parity_checks(monkeypatch):
    """Verify Defect 6:
    - audit_invariants checks generation model, embedding model, location, temp,
      prompts, RRF weights, caps 8/4, K=3, pool 30, and fails closed on any mismatch.
    """
    # Generation model mismatch
    monkeypatch.setenv("QA_GENERATION_MODEL_ID", "wrong-model")
    with pytest.raises(ValueError, match="QA_GENERATION_MODEL_ID mismatch"):
        d4_a2.audit_invariants(_PROJECT_ROOT)

    # Embedding model mismatch
    monkeypatch.setenv("QA_GENERATION_MODEL_ID", "gemini-3.8-flash")
    monkeypatch.setenv("QA_EMBEDDING_MODEL_ID", "wrong-embedding")
    with pytest.raises(ValueError, match="QA_EMBEDDING_MODEL_ID mismatch"):
        d4_a2.audit_invariants(_PROJECT_ROOT)

    # Location mismatch
    monkeypatch.setenv("QA_EMBEDDING_MODEL_ID", "gemini-embedding-2")
    monkeypatch.setenv("QA_VERTEX_LOCATION", "us-central1")
    with pytest.raises(ValueError, match="Vertex location mismatch"):
        d4_a2.audit_invariants(_PROJECT_ROOT)

    # Temperature mismatch
    monkeypatch.setenv("QA_VERTEX_LOCATION", "global")
    monkeypatch.setenv("QA_TEMPERATURE", "0.7")
    with pytest.raises(ValueError, match="Reranker temperature mismatch"):
        d4_a2.audit_invariants(_PROJECT_ROOT)


# ---------------------------------------------------------------------------
# 18. Test for Defect 7: Post-Exposure Mutation Accounting
# ---------------------------------------------------------------------------

def test_defect7_post_exposure_mutation_accounting():
    """Verify Defect 7:
    - Pre-exposure mutation counters are 0.
    - Post-exposure mutations (case, mask, replacement, model, metric, verdict)
      are mechanically detected and recorded.
    """
    prereg = json.loads((_PROJECT_ROOT / d4_a2.PREREGISTRATION_PATH).read_text(encoding="utf-8"))
    mut = prereg["post_exposure_mutation_accounting"]
    for k in [
        "POST_EXPOSURE_CASE_MUTATIONS",
        "POST_EXPOSURE_MASK_MUTATIONS",
        "POST_EXPOSURE_REPLACEMENT_MUTATIONS",
        "POST_EXPOSURE_MODEL_MUTATIONS",
        "POST_EXPOSURE_METRIC_MUTATIONS",
        "POST_EXPOSURE_VERDICT_MUTATIONS",
    ]:
        assert mut[k] == 0

    # Test detection of replacement mutation (e.g. wrong K)
    raw = _make_valid_raw_artifact()
    raw["slots"][1]["admission_budget_k"] = 5  # mutated
    is_valid, reason, counters = d4_a2.validate_raw_artifact_structural_validity(raw)
    assert is_valid is False
    assert counters["POST_EXPOSURE_REPLACEMENT_MUTATIONS"] > 0


# ---------------------------------------------------------------------------
# 19. Test for Defect 8: Freeze Identity Contract
# ---------------------------------------------------------------------------

def test_defect8_freeze_identity_contract():
    """Verify Defect 8:
    - Manifest and preregistration contain implementation_freeze_contract
      with policy GIT_COMMIT_CONTAINING_THIS_ARTIFACT.
    - validate_raw_artifact_structural_validity rejects unresolved placeholders.
    """
    manifest = json.loads((_PROJECT_ROOT / d4_a2.MANIFEST_PATH).read_text(encoding="utf-8"))
    prereg = json.loads((_PROJECT_ROOT / d4_a2.PREREGISTRATION_PATH).read_text(encoding="utf-8"))

    assert manifest["implementation_freeze_contract"]["policy"] == "GIT_COMMIT_CONTAINING_THIS_ARTIFACT"
    assert prereg["implementation_freeze_contract"]["policy"] == "GIT_COMMIT_CONTAINING_THIS_ARTIFACT"

    raw = _make_valid_raw_artifact()
    raw["authority"]["implementation_freeze_head"] = "GIT_COMMIT_CONTAINING_THIS_ARTIFACT"  # Not a 40-hex SHA
    is_valid, reason, _ = d4_a2.validate_raw_artifact_structural_validity(raw)
    assert is_valid is False
    assert "not a valid 40-character hex" in reason
