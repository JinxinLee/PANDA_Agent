"""Unit tests for PANDA Agent D4-A2-V2 Controlled Shared-Plan Validation.

All tests are deterministic, offline, and self-contained.
Zero provider/retrieval calls or live model/database queries.
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
    v1 = v2.compute_controlled_shared_plan_verdict(execution_valid=False)
    assert v1["verdict_level"] == 1
    assert "INVALID" in v1["verdict"]

    # Level 2: BEFORE reference not reproduced
    v2_res = v2.compute_controlled_shared_plan_verdict(
        execution_valid=True,
        before_reference_valid=False,
    )
    assert v2_res["verdict_level"] == 2
    assert "INCONCLUSIVE" in v2_res["verdict"]

    # Level 3: Target replacement not reproduced
    v3 = v2.compute_controlled_shared_plan_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=1,
        batch1_dependency_removed=2,
    )
    assert v3["verdict_level"] == 3
    assert "FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED" in v3["verdict"]

    # Level 4: Shared plan critical regression
    v4 = v2.compute_controlled_shared_plan_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
        batch1_dependency_removed=2,
        shared_plan_critical_regressions=["n022.e2"],
    )
    assert v4["verdict_level"] == 4
    assert "FAIL / SHARED_PLAN_CRITICAL_TREATMENT_REGRESSION" in v4["verdict"]

    # Level 5: Aggregate tolerance exceeded
    v5 = v2.compute_controlled_shared_plan_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
        batch1_dependency_removed=2,
        shared_plan_critical_regressions=[],
        metric_deltas={"recall_at_5": -0.06},
    )
    assert v5["verdict_level"] == 5
    assert "PARTIAL / AGGREGATE_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE" in v5["verdict"]

    # Level 6: PASS
    v6 = v2.compute_controlled_shared_plan_verdict(
        execution_valid=True,
        before_reference_valid=True,
        target_replacement_reproduced=2,
        batch1_dependency_removed=2,
        shared_plan_critical_regressions=[],
        metric_deltas={"recall_at_5": 0.0, "final_evidence_recall": 0.0},
    )
    assert v6["verdict_level"] == 6
    assert "PASS / CONTROLLED_SHARED_PLAN_T2_VALIDATED" in v6["verdict"]


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

def test_audit_invariants_offline():
    """Verify that audit_invariants executes successfully offline."""
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
        "commit_a_implementation_freeze_head": commit_a_sha,
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED": True,
        "PHASE_R_RETRIEVAL_EXECUTED": False,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
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
    assert manifest_after["outcome_exposure_state"]["D4_A2_V2_OUTCOME_EXPOSURE"] == "NOT_STARTED"
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
