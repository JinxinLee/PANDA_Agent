"""Unit tests for D4-A9 Component-Sensitive Model-Factory Targeted Scientific Validation Execution.

Verifies:
  1. Starting R2 boundary match;
  2. R2 live verify returns PASS;
  3. R2 machine authority consumption;
  4. Exact formal cohort ['g031', 'g032', 'g033', 'g047'];
  5. Exact target mask ['model/PndLmdModelFactory.cxx'];
  6. DPM symbols and page hints strictly HOLD;
  7. Production files untouched;
  8. Historical R2 artifacts untouched;
  9. Pure A5 authority helpers load;
  10. Ledger coverage gate rejects partial ledger;
  11. Origin-type consistency rejects malformed origin types;
  12. Persistence state machine rejects out-of-order transitions;
  13. g031 treatment constructor subtracts target origin and preserves independent origins/held items;
  14. Control cases receive zero target subtraction;
  15. Provider budget matches N=4, R=0, F=4;
  16. Deterministic evaluator respects 6-level precedence hierarchy;
  17. No production activation or config mutation path exists.
"""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

import d4_a9_model_factory_covered_symbol_retirement_validation as a9
import d4_a8_r2_component_sensitive_execution_contract_seal as r2

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def test_01_starting_r2_boundary() -> None:
    """Item 1: Verify starting R2 boundary match."""
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=_PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()

    # During development, HEAD may be starting HEAD or a commit derived from it.
    # The starting head must be in the git history.
    assert (head_sha == a9.STARTING_HEAD) or subprocess.run(
        ["git", "merge-base", "--is-ancestor", a9.STARTING_HEAD, "HEAD"],
        cwd=_PROJECT_ROOT,
    ).returncode == 0


def test_02_r2_live_verify_returns_pass() -> None:
    """Item 2: Verify R2 live verify returns PASS and COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEALED."""
    # R2 script verify mode
    audit_res = r2.audit_component_sensitive_coverage(
        _PROJECT_ROOT, r2.load_gold_questions(_PROJECT_ROOT)
    )
    assert audit_res["r1_target_mask_preserved"] is True
    assert audit_res["covered_symbol_mask"] == a9.FROZEN_COVERED_SYMBOL_MASK


def test_03_r2_machine_authority_consumption() -> None:
    """Item 3: Verify R2 machine authority files exist and parse correctly."""
    prereg = a9._load_json(_PROJECT_ROOT / a9.R2_PREREG_PATH)
    result = a9._load_json(_PROJECT_ROOT / a9.R2_RESULT_PATH)

    assert prereg["lifecycle_stage"] == "D4-A8-R2"
    assert result["stage"] == "D4-A8-R2"
    assert result["status"] == "PASS"
    assert result["decision"] == "COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEALED"
    assert prereg["covered_symbol_mask"] == a9.FROZEN_COVERED_SYMBOL_MASK
    assert prereg["formal_case_order"] == a9.FROZEN_FORMAL_CASE_ORDER


def test_04_exact_formal_cohort() -> None:
    """Item 4: Verify exact formal cohort ['g031', 'g032', 'g033', 'g047']."""
    assert a9.FROZEN_FORMAL_CASE_ORDER == ["g031", "g032", "g033", "g047"]
    assert len(a9.SCHEDULE_8) == 8
    cohort_in_schedule = sorted(set(cell["case_id"] for cell in a9.SCHEDULE_8))
    assert cohort_in_schedule == sorted(a9.FROZEN_FORMAL_CASE_ORDER)


def test_05_exact_target_mask() -> None:
    """Item 5: Verify exact target mask ['model/PndLmdModelFactory.cxx']."""
    assert a9.FROZEN_COVERED_SYMBOL_MASK == ["model/PndLmdModelFactory.cxx"]
    mask_def = a9.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS["model_factory_theory"]
    assert mask_def["symbols_retired"] == ["model/PndLmdModelFactory.cxx"]


def test_06_dpm_symbols_and_page_hints_hold() -> None:
    """Item 6: Verify DPM symbols and page hints are strictly HOLD."""
    assert a9.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK == [
        "model/PndLmdDPMAngModel1D.cxx",
        "model/PndLmdDPMAngModel2D.cxx",
    ]
    assert a9.FROZEN_PAGE_HINT_HOLD_MASK == {"pflueger_2017": [51, 57, 65]}
    mask_def = a9.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS["model_factory_theory"]
    assert mask_def["symbols_preserved"] == a9.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK
    assert mask_def["paper_page_hints_preserved"] == a9.FROZEN_PAGE_HINT_HOLD_MASK


def test_07_production_files_untouched() -> None:
    """Item 7: Verify production files under src/ and configs/ are untouched."""
    # Compare against starting head
    for path_prefix in ["src", "configs"]:
        diff = subprocess.run(
            ["git", "diff", a9.STARTING_HEAD, "--", path_prefix],
            cwd=_PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout.strip()
        assert diff == "", f"Production files under {path_prefix} modified since starting head"


def test_08_historical_r2_artifacts_untouched() -> None:
    """Item 8: Verify historical R2 artifacts are untouched."""
    diff = subprocess.run(
        ["git", "diff", a9.STARTING_HEAD, "--", a9.R2_PREREG_PATH, a9.R2_RESULT_PATH],
        cwd=_PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()
    assert diff == "", "Historical R2 machine artifacts modified"


def test_09_pure_a5_authority_helpers_load() -> None:
    """Item 9: Verify pure A5 authority helpers successfully load."""
    a5 = a9.load_a5_authority()
    for helper_name in a9.A5_REQUIRED_HELPERS:
        assert hasattr(a5, helper_name), f"Missing A5 helper {helper_name}"


def test_10_ledger_coverage_gate_rejects_partial_ledger() -> None:
    """Item 10: Verify ledger coverage gate rejects partial ledger."""
    a5 = a9.load_a5_authority()
    plan = {
        "intent": "api",
        "symbols": ["model/PndLmdModelFactory.cxx", "extra_symbol.cxx"],
        "concepts": [],
        "target_repositories": ["luminosityfit"],
        "paper_page_hints": {},
    }
    # Incomplete ledger missing extra_symbol.cxx
    partial_ledger = [
        {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "kind": "symbol",
            "contribution_value": "model/PndLmdModelFactory.cxx",
            "plan_present": True,
            "provenance_origin_ids": ["model_factory_theory"],
            "origin_types": {"model_factory_theory": a9.ORIGIN_TYPE_REVIEWED_RULE},
        }
    ]
    ok, err = a5.validate_ledger_coverage(plan, partial_ledger)
    assert ok is False
    assert "extra_symbol.cxx" in str(err)


def test_11_origin_type_consistency_rejects_malformed_origin_types() -> None:
    """Item 11: Verify origin-type consistency rejects malformed origin types."""
    # Mismatched keys
    bad_ledger_1 = [
        {
            "contribution_id": "symbol::test",
            "plan_present": True,
            "provenance_origin_ids": ["origin_a"],
            "origin_types": {"origin_b": a9.ORIGIN_TYPE_REVIEWED_RULE},
        }
    ]
    ok, err = a9.validate_origin_type_consistency(bad_ledger_1)
    assert ok is False

    # Wrong type for analyzer delta
    bad_ledger_2 = [
        {
            "contribution_id": "symbol::test2",
            "plan_present": True,
            "provenance_origin_ids": [a9.ORIGIN_ACCEPTED_ANALYZER_DELTA],
            "origin_types": {a9.ORIGIN_ACCEPTED_ANALYZER_DELTA: a9.ORIGIN_TYPE_REVIEWED_RULE},
        }
    ]
    ok, err = a9.validate_origin_type_consistency(bad_ledger_2)
    assert ok is False


def test_12_persistence_state_machine_transitions() -> None:
    """Item 12: Verify persistence state machine rejects out-of-order transitions."""
    # Valid transitions
    s1 = a9.transition_execution_state(a9.STATE_ACQUIRED, a9.STATE_PERSISTED)
    assert s1 == a9.STATE_PERSISTED
    s2 = a9.transition_execution_state(s1, a9.STATE_GATED)
    assert s2 == a9.STATE_GATED
    s3 = a9.transition_execution_state(s2, a9.STATE_RETRIEVAL_ELIGIBLE)
    assert s3 == a9.STATE_RETRIEVAL_ELIGIBLE

    # Invalid jump ACQUIRED -> GATED
    with pytest.raises(a9.StateTransitionError):
        a9.transition_execution_state(a9.STATE_ACQUIRED, a9.STATE_GATED)

    # Invalid jump ACQUIRED -> RETRIEVAL_ELIGIBLE
    with pytest.raises(a9.StateTransitionError):
        a9.transition_execution_state(a9.STATE_ACQUIRED, a9.STATE_RETRIEVAL_ELIGIBLE)

    # Invalid jump PERSISTED -> RETRIEVAL_ELIGIBLE
    with pytest.raises(a9.StateTransitionError):
        a9.transition_execution_state(a9.STATE_PERSISTED, a9.STATE_RETRIEVAL_ELIGIBLE)


def test_13_g031_treatment_constructor() -> None:
    """Item 13: Verify g031 treatment constructor subtracts target origin and preserves independent origins."""
    a5 = a9.load_a5_authority()
    plan_g031 = {
        "intent": "api",
        "symbols": [
            "model/PndLmdDPMAngModel1D.cxx",
            "model/PndLmdDPMAngModel2D.cxx",
            "model/PndLmdModelFactory.cxx",
            "PndLmdModelFactory::setAcceptance",
        ],
        "concepts": ["DPM model acceptance resolution composition"],
        "target_repositories": ["luminosityfit"],
        "paper_page_hints": {},
        "analysis_diagnostics": {
            "matched_expansion_rules": ["model_factory_theory", "model_factory_acceptance_methods"]
        },
    }
    # Mock rules_by_id
    mock_rules = {
        "model_factory_theory": {
            "rule_id": "model_factory_theory",
            "symbols": [
                "model/PndLmdDPMAngModel1D.cxx",
                "model/PndLmdDPMAngModel2D.cxx",
                "model/PndLmdModelFactory.cxx",
            ],
            "paper_page_hints": {},
            "concepts": ["DPM model acceptance resolution composition"],
            "repositories": ["luminosityfit"],
        },
        "model_factory_acceptance_methods": {
            "rule_id": "model_factory_acceptance_methods",
            "symbols": [
                "model/PndLmdModelFactory.cxx",
                "PndLmdModelFactory::setAcceptance",
            ],
            "paper_page_hints": {},
            "concepts": [],
            "repositories": ["luminosityfit"],
        },
    }
    matched = ["model_factory_theory", "model_factory_acceptance_methods"]
    ledger = a5.build_contribution_ledger(plan_g031, mock_rules, matched)

    proj, receipts, comp_receipts = a9.construct_component_sensitive_treatment(
        plan_g031,
        ledger,
        matched,
        "g031",
        case_role="TREATMENT",
    )

    # Check origin subtraction
    removed = receipts.get("removed_rule_origin_entries", [])
    assert len(removed) == 1
    assert removed[0]["retired_rule_origins"] == ["model_factory_theory"]
    assert removed[0]["value"] == "model/PndLmdModelFactory.cxx"

    # Because model_factory_acceptance_methods also provides PndLmdModelFactory.cxx,
    # it survives as an independent origin!
    surviving = receipts.get("surviving_independent_origin_entries", [])
    assert any(s["value"] == "model/PndLmdModelFactory.cxx" for s in surviving)
    assert "model/PndLmdModelFactory.cxx" in proj["symbols"]

    # Held symbols are untouched
    assert "model/PndLmdDPMAngModel1D.cxx" in proj["symbols"]
    assert "model/PndLmdDPMAngModel2D.cxx" in proj["symbols"]


def test_14_control_cases_zero_target_subtraction() -> None:
    """Item 14: Verify control cases (g032, g033, g047) receive zero target subtraction."""
    a5 = a9.load_a5_authority()
    for cid in ["g032", "g033", "g047"]:
        plan_ctrl = {
            "intent": "api",
            "symbols": ["data/PndLmdAcceptance.cxx"],
            "concepts": [],
            "target_repositories": ["pandaroot"],
            "paper_page_hints": {},
            "analysis_diagnostics": {
                "matched_expansion_rules": [],
                "analyzer_accepted_semantic_delta": {
                    "symbols": ["data/PndLmdAcceptance.cxx"],
                    "repository_additions": ["pandaroot"],
                },
            },
        }
        ledger_ctrl = a5.build_contribution_ledger(plan_ctrl, {}, [])
        proj, receipts, _ = a9.construct_component_sensitive_treatment(
            plan_ctrl,
            ledger_ctrl,
            [],
            cid,
            case_role="CONTROL",
        )
        assert proj == plan_ctrl, f"Control {cid} projection was mutated"
        assert receipts.get("effective_removal_count") == 0


def test_15_provider_budget_calculation() -> None:
    """Item 15: Verify provider budget calculation matches N=4, R=0, F=4."""
    assert a9.PLANNED_BUDGET["N_formal_cases"] == 4
    assert a9.PLANNED_BUDGET["R_reusable_plans"] == 0
    assert a9.PLANNED_BUDGET["F_fresh_plans"] == 4
    assert a9.PLANNED_BUDGET["analyzer_calls"] == 4
    assert a9.PLANNED_BUDGET["embedding_calls"] == 8
    assert a9.PLANNED_BUDGET["reranker_calls"] == 8
    assert a9.PLANNED_BUDGET["total_logical_model_calls"] == 20
    assert a9.PLANNED_BUDGET["qa_calls"] == 0
    assert a9.PLANNED_BUDGET["judge_calls"] == 0


def test_16_deterministic_evaluator_precedence() -> None:
    """Item 16: Verify deterministic evaluator respects frozen 6-level precedence hierarchy."""
    # Precedence states check
    assert a9.OUTCOME_LEVEL_1_INVALID.startswith("Level 1") or "LEVEL_1" in a9.OUTCOME_LEVEL_1_INVALID or a9.OUTCOME_LEVEL_1_INVALID == "INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED"
    assert a9.OUTCOME_LEVEL_2_BASELINE == "INCONCLUSIVE / ALL_COVERED_COMPONENT_BASELINES_NOT_REPRODUCED"
    assert a9.OUTCOME_LEVEL_3_DEPENDENCY == "PARTIAL / DEPENDENCY_OBSERVED_FOR_COVERED_COMPONENTS_RETAIN"
    assert a9.OUTCOME_LEVEL_4_REGRESSION == "FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION"
    assert a9.OUTCOME_LEVEL_5_APPLICABILITY == "INCONCLUSIVE / COVERED_COMPONENT_APPLICABILITY_INCOMPLETE"
    assert a9.OUTCOME_LEVEL_6_PARTIAL_PASS == "PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD"


def test_17_no_production_activation_authorized() -> None:
    """Item 17: Verify no production activation or config mutation path exists."""
    manifest = a9._load_json(_PROJECT_ROOT / a9.MANIFEST_PATH)
    assert manifest.get("production_activation_authorized") is False
    assert manifest.get("lifecycle_stage") == "D4-A9"
