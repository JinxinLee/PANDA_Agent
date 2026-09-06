"""Unit test suite for D4-A8-R1 Component-Sensitive Revalidation Contract Repair.

Verifies all 31 requirements defined in Section 33 of the D4-A8-R1 specification:
1. exact starting A8 SHA/message/parent;
2. exact seven-file R1 allowlist;
3. historical A8 artifacts immutable;
4. src/ and configs/ immutable;
5. production state still post-A7;
6. g031 counts as direct coverage for ModelFactory.cxx;
7. g032 does NOT count as direct coverage for DPM1D while nonmatching;
8. g033 does NOT count as direct coverage for DPM2D while nonmatching;
9. no-op control evidence cannot authorize retirement coverage;
10. unapproved English Gold case cannot count;
11. Chinese case cannot count;
12. Novel case without explicit formal eligibility cannot silently count;
13. page-hint audit enforces approval eligibility;
14. covered mask derived mechanically from coverage table;
15. uncovered symbols automatically become HOLD;
16. page hints remain outside treatment;
17. reusability audit actually scans plan-bearing artifacts;
18. fake compatible complete historical plan can classify reusable;
19. incomplete plan record cannot classify reusable;
20. behavior-incompatible plan cannot classify reusable;
21. future provider budget derives from N/R/F;
22. real A5 ledger schema is accepted;
23. selected target origin subtraction uses provenance_origin_ids;
24. independent origin survives selected-origin retirement;
25. no independent origin -> value is effectively removed;
26. page hints untouched by symbol projection;
27. uncovered symbols untouched by projection;
28. control plan gets zero selected-origin removal;
29. successful component result cannot validate uncovered sibling component;
30. full RETIREMENT_VALIDATED cannot be produced by this repaired contract;
31. no production/scientific/provider execution path exists in R1.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

import evaluation.scripts.d4_a8_r1_component_sensitive_revalidation_contract_repair as r1

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Tests 1-5: Boundaries, Allowlist, Immutability, Production State
# ---------------------------------------------------------------------------

def test_01_starting_boundary() -> None:
    """Requirement 1: Exact starting A8 SHA, message, and parent."""
    assert r1.STARTING_HEAD == "ae2e744f6a05e711d407a02d0ae276e6e1422809"
    assert r1.STARTING_COMMIT_MESSAGE == "D4-A8 preregister model-factory symbol retirement revalidation"
    assert r1.STARTING_PARENT_HEAD == "2da89b8223399ff184f4b2b3674f7c995ce8d390"

    res = r1.verify_starting_boundary(PROJECT_ROOT)
    assert res["head_exact"] is True
    assert res["msg_exact"] is True
    assert res["parent_exact"] is True


def test_02_r1_cumulative_diff_allowlist() -> None:
    """Requirement 2: Exact seven-file R1 allowlist."""
    assert len(r1.EXPECTED_R1_PATHS) == 7
    # Test validator with exact match
    res = r1.verify_git_cumulative_diff(PROJECT_ROOT, _override_diff_paths=r1.EXPECTED_R1_PATHS)
    assert res["exact_match"] is True

    # Test validator rejects extra file
    extra = r1.EXPECTED_R1_PATHS + ["some/extra/file.txt"]
    res_extra = r1.verify_git_cumulative_diff(PROJECT_ROOT, _override_diff_paths=extra)
    assert res_extra["exact_match"] is False
    assert res_extra["extra_paths"] == ["some/extra/file.txt"]

    # Test validator rejects missing file
    missing = r1.EXPECTED_R1_PATHS[:-1]
    res_missing = r1.verify_git_cumulative_diff(PROJECT_ROOT, _override_diff_paths=missing)
    assert res_missing["exact_match"] is False
    assert len(res_missing["missing_paths"]) == 1


def test_03_historical_a8_artifacts_immutable() -> None:
    """Requirement 3: Historical A8 artifacts are sealed and immutable."""
    res = r1.verify_historical_a8_immutability(PROJECT_ROOT, head_ref="HEAD")
    assert res["all_match"] is True, f"Mismatches: {res['mismatches']}"


def test_04_src_and_configs_immutable() -> None:
    """Requirement 4: src/ and configs/ remain byte-identical to STARTING_HEAD."""
    src_res = r1.verify_production_tree_immutability(PROJECT_ROOT)
    assert src_res["src_tree_immutable"] is True

    configs_res = r1.verify_configs_immutability(PROJECT_ROOT)
    assert configs_res["configs_immutable"] is True


def test_05_production_state_post_a7() -> None:
    """Requirement 5: Production state matches post-D4-A7 contract."""
    res = r1.verify_production_state(PROJECT_ROOT)
    assert res["production_state_valid"] is True
    assert res["effective_acceptance_pipeline_retired"] is True
    assert res["root_macro_usage_retired"] is True
    assert res["model_factory_theory_held"] is True
    assert res["batch1_active"] is True


# ---------------------------------------------------------------------------
# Tests 6-12: Coverage & Formal Eligibility
# ---------------------------------------------------------------------------

def test_06_g031_direct_coverage_for_model_factory() -> None:
    """Requirement 6: g031 counts as direct coverage for ModelFactory.cxx."""
    gold_questions = r1.load_gold_questions(PROJECT_ROOT)
    coverage = r1.audit_component_sensitive_coverage(PROJECT_ROOT, gold_questions)

    mf_cov = coverage["component_coverage"]["model/PndLmdModelFactory.cxx"]
    assert mf_cov["coverage_status"] == "DIRECT_TREATMENT_COVERAGE_FOUND"
    assert mf_cov["targetable"] is True
    assert any(c["case_id"] == "g031" for c in mf_cov["direct_cases"])


@pytest.mark.parametrize("sym_path,control_id", [
    ("model/PndLmdDPMAngModel1D.cxx", "g032"),
    ("model/PndLmdDPMAngModel2D.cxx", "g033"),
])
def test_07_08_controls_do_not_count_as_direct_coverage(sym_path: str, control_id: str) -> None:
    """Requirements 7 & 8: g032 and g033 do NOT count as direct coverage for DPM1D/2D while nonmatching."""
    gold_questions = r1.load_gold_questions(PROJECT_ROOT)
    coverage = r1.audit_component_sensitive_coverage(PROJECT_ROOT, gold_questions)

    sym_cov = coverage["component_coverage"][sym_path]
    assert sym_cov["coverage_status"] == "DIRECT_TREATMENT_COVERAGE_GAP"
    assert sym_cov["targetable"] is False
    assert sym_cov["direct_cases"] == []
    assert coverage["matching_info"][control_id]["matches_target_rule"] is False


def test_09_no_op_control_evidence_cannot_authorize_retirement() -> None:
    """Requirement 9: Evidence presence in no-op controls cannot authorize retirement."""
    # When evaluated under hypothetical outcome, even if g032/g033 reproduce baseline,
    # their mentioned components remain on HOLD because they have no direct treatment coverage.
    case_results = {
        "model/PndLmdModelFactory.cxx": {
            "baseline_reproduced": True,
            "applicability": "ACTIVE_IDENTIFIABLE",
            "treatment_presence": True,
            "origin_subtracted": True,
        }
    }
    outcome = r1.evaluate_component_sensitive_hypothetical_outcome(
        covered_symbols=["model/PndLmdModelFactory.cxx"],
        uncovered_symbols=["model/PndLmdDPMAngModel1D.cxx", "model/PndLmdDPMAngModel2D.cxx"],
        page_hints={"pflueger_2017": [51, 57, 65]},
        case_results=case_results,
    )
    disps = outcome["component_dispositions"]
    assert disps["model/PndLmdDPMAngModel1D.cxx"] == r1.DISPOSITION_COVERAGE_GAP
    assert disps["model/PndLmdDPMAngModel2D.cxx"] == r1.DISPOSITION_COVERAGE_GAP


def test_10_unapproved_english_gold_cannot_count() -> None:
    """Requirement 10: Unapproved English Gold cases cannot count as direct treatment coverage."""
    mock_questions = [
        {
            "id": "g999",
            "split": "dev",
            "language": "en",
            "review_status": "draft",  # NOT approved
            "intent": "api",
            "query": "How does PndLmdDPMAngModel1D work?",
            "required_evidence_groups": [
                {"group_id": "g999.e1", "any_of": [{"path": "model/PndLmdDPMAngModel1D.cxx"}]}
            ],
        }
    ]
    # Synthetic coverage check should reject unapproved question
    coverage = r1.audit_component_sensitive_coverage(PROJECT_ROOT, mock_questions)
    assert coverage["component_coverage"]["model/PndLmdDPMAngModel1D.cxx"]["coverage_status"] == "DIRECT_TREATMENT_COVERAGE_GAP"


def test_11_chinese_case_cannot_count() -> None:
    """Requirement 11: Non-English (e.g. Chinese g064) cannot count for formal gate."""
    gold_questions = r1.load_gold_questions(PROJECT_ROOT)
    audit_res = r1.audit_case_eligibility(gold_questions)
    g064 = audit_res["case_audits"].get("g064")
    assert g064 is not None
    assert g064["excluded"] is True
    assert g064["reason"] == "NON_ENGLISH_OUTSIDE_FORMAL_PRODUCT_GATE"


def test_12_novel_case_without_formal_eligibility_cannot_count() -> None:
    """Requirement 12: Novel case without formal eligibility cannot silently count."""
    gap_res = r1.audit_page_hint_coverage_gap_approval_aware(PROJECT_ROOT)
    assert gap_res["status"] == "OPEN"
    assert gap_res["result"] == "NO_EXISTING_APPROVED_ENGLISH_CASE_FOUND"
    assert gap_res["candidate_surviving_cases"] == []


# ---------------------------------------------------------------------------
# Tests 13-16: Target Masks & Page Hint Audits
# ---------------------------------------------------------------------------

def test_13_page_hint_audit_enforces_approval() -> None:
    """Requirement 13: Page-hint gap audit strictly requires approved English cases."""
    gap_res = r1.audit_page_hint_coverage_gap_approval_aware(PROJECT_ROOT)
    assert gap_res["status"] == "OPEN"
    assert "pflueger_2017 [51, 57, 65] remain strictly on HOLD" in gap_res["explanation"]


def test_14_15_16_derived_masks() -> None:
    """Requirements 14, 15, 16: Covered mask derived mechanically, uncovered symbols HOLD, page hints HOLD."""
    gold_questions = r1.load_gold_questions(PROJECT_ROOT)
    coverage = r1.audit_component_sensitive_coverage(PROJECT_ROOT, gold_questions)

    assert coverage["covered_symbol_mask"] == ["model/PndLmdModelFactory.cxx"]
    assert sorted(coverage["uncovered_symbol_hold_mask"]) == sorted([
        "model/PndLmdDPMAngModel1D.cxx",
        "model/PndLmdDPMAngModel2D.cxx",
    ])
    assert coverage["page_hint_hold_mask"] == {"pflueger_2017": [51, 57, 65]}


# ---------------------------------------------------------------------------
# Tests 17-21: Plan Reusability & Budget Derivation
# ---------------------------------------------------------------------------

def test_17_plan_reusability_audit_scans_real_artifacts() -> None:
    """Requirement 17: Plan reusability audit actually scans exposed plan-bearing artifacts."""
    res = r1.audit_plan_reusability(PROJECT_ROOT)
    assert len(res["scanned_artifacts"]) > 0
    assert "evaluation/d4_a5_continuation_raw_prospective_plans.json" in res["scanned_artifacts"]
    assert res["all_require_fresh_acquisition"] is True
    assert res["fresh_plan_count"] == 4
    assert res["reusable_plan_count"] == 0


def test_18_compatible_plan_classifies_reusable() -> None:
    """Requirement 18: Fake compatible complete historical plan can classify as reusable."""
    valid_rec = {
        "case_id": "test_case",
        "canonical_plan": {
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": ["model factory"],
        },
        "contribution_ledger": [
            {
                "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
                "kind": "symbol",
                "value": "model/PndLmdModelFactory.cxx",
                "provenance_origin_ids": ["model_factory_theory"],
            }
        ],
    }
    is_compat, reason = r1.check_plan_record_compatibility(valid_rec)
    assert is_compat is True
    assert reason == "COMPATIBLE"


def test_19_incomplete_plan_rejected() -> None:
    """Requirement 19: Incomplete plan record cannot classify reusable."""
    incomplete_rec = {
        "case_id": "test_case",
        "canonical_plan": {
            # missing symbols
            "concepts": ["model factory"],
        },
    }
    is_compat, reason = r1.check_plan_record_compatibility(incomplete_rec)
    assert is_compat is False
    assert reason == "CANONICAL_PLAN_FIELDS_INCOMPLETE"


def test_20_incompatible_provenance_plan_rejected() -> None:
    """Requirement 20: Plan with corrupted/missing provenance origins cannot classify reusable."""
    corrupted_rec = {
        "case_id": "test_case",
        "canonical_plan": {
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": ["model factory"],
        },
        "contribution_ledger": [
            {
                "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
                "kind": "symbol",
                "value": "model/PndLmdModelFactory.cxx",
                # missing provenance_origin_ids!
            }
        ],
    }
    is_compat, reason = r1.check_plan_record_compatibility(corrupted_rec)
    assert is_compat is False
    assert reason == "ORIGINS_MISSING_IN_LEDGER_ENTRY"


def test_21_provider_budget_derived_from_N_R_F() -> None:
    """Requirement 21: Future provider budget derives strictly from N, R, F."""
    fake_audit = {
        "reusable_plan_case_ids": ["g031"],  # R = 1, N = 4, F = 3
    }
    cohort_budget = r1.derive_future_cohort_and_budget(["model/PndLmdModelFactory.cxx"], fake_audit)
    budget = cohort_budget["derived_provider_budget"]
    assert budget["N_formal_cases"] == 4
    assert budget["R_reusable_plans"] == 1
    assert budget["F_fresh_plans"] == 3
    assert budget["analyzer_calls"] == 3
    assert budget["embedding_calls"] == 8
    assert budget["reranker_calls"] == 8
    assert budget["total_logical_model_calls"] == 3 + 4 * 4  # 19


# ---------------------------------------------------------------------------
# Tests 22-28: Real Contribution Ledger & Projection Machinery
# ---------------------------------------------------------------------------

def test_22_real_a5_ledger_schema_accepted() -> None:
    """Requirement 22: Authoritative D4-A5 ledger schema is produced."""
    canonical_plan = {
        "symbols": ["model/PndLmdModelFactory.cxx"],
        "concepts": ["luminosity model"],
        "target_repositories": ["luminosityfit"],
        "paper_page_hints": {"pflueger_2017": [51]},
    }
    rules = {
        "model_factory_theory": {
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": ["luminosity model"],
            "repositories": ["luminosityfit"],
            "paper_page_hints": {"pflueger_2017": [51]},
        }
    }
    ledger = r1.build_real_contribution_ledger(canonical_plan, rules, ["model_factory_theory"])
    assert len(ledger) == 4
    for entry in ledger:
        assert "contribution_id" in entry
        assert "kind" in entry
        assert "value" in entry
        assert "provenance_origin_ids" in entry
        assert "origin_types" in entry
        assert "plan_present" in entry


def test_23_selected_target_origin_subtraction() -> None:
    """Requirement 23: Subtraction uses provenance_origin_ids."""
    canonical_plan = {
        "symbols": ["model/PndLmdModelFactory.cxx"],
        "concepts": ["luminosity model"],
    }
    ledger = [
        {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "kind": "symbol",
            "value": "model/PndLmdModelFactory.cxx",
            "provenance_origin_ids": ["model_factory_theory"],
            "plan_present": True,
        }
    ]
    proj, diff = r1.project_component_sensitive_treatment(
        canonical_plan, ledger, ["model/PndLmdModelFactory.cxx"], ["model_factory_theory"]
    )
    assert diff["selected_rule_origins_removed"] == 1
    assert "model/PndLmdModelFactory.cxx" in diff["effective_values_removed"]
    assert "model/PndLmdModelFactory.cxx" not in proj["symbols"]


def test_24_independent_origin_survives_selected_retirement() -> None:
    """Requirement 24: Independent origin survives selected-origin retirement."""
    canonical_plan = {
        "symbols": ["model/PndLmdModelFactory.cxx"],
    }
    ledger = [
        {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "kind": "symbol",
            "value": "model/PndLmdModelFactory.cxx",
            # Multi-origin: both model_factory_theory AND independent rule
            "provenance_origin_ids": ["model_factory_theory", "model_factory_acceptance_methods"],
            "plan_present": True,
        }
    ]
    proj, diff = r1.project_component_sensitive_treatment(
        canonical_plan, ledger, ["model/PndLmdModelFactory.cxx"], ["model_factory_theory"]
    )
    assert diff["selected_rule_origins_removed"] == 1
    assert len(diff["effective_values_removed"]) == 0
    assert len(diff["values_surviving_via_independent_origins"]) == 1
    assert diff["values_surviving_via_independent_origins"][0]["symbol"] == "model/PndLmdModelFactory.cxx"
    assert diff["values_surviving_via_independent_origins"][0]["surviving_origins"] == ["model_factory_acceptance_methods"]
    # Symbol remains in projected plan!
    assert "model/PndLmdModelFactory.cxx" in proj["symbols"]


def test_25_no_independent_origin_effectively_removes_value() -> None:
    """Requirement 25: Value is effectively removed when no independent origin survives."""
    canonical_plan = {
        "symbols": ["model/PndLmdModelFactory.cxx"],
    }
    ledger = [
        {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "kind": "symbol",
            "value": "model/PndLmdModelFactory.cxx",
            "provenance_origin_ids": ["model_factory_theory"],
            "plan_present": True,
        }
    ]
    proj, diff = r1.project_component_sensitive_treatment(
        canonical_plan, ledger, ["model/PndLmdModelFactory.cxx"], ["model_factory_theory"]
    )
    assert proj["symbols"] == []
    assert diff["effective_values_removed"] == ["model/PndLmdModelFactory.cxx"]


def test_26_page_hints_untouched_by_symbol_projection() -> None:
    """Requirement 26: Page hints are untouched by symbol projection."""
    canonical_plan = {
        "symbols": ["model/PndLmdModelFactory.cxx"],
        "paper_page_hints": {"pflueger_2017": [51, 57, 65]},
    }
    ledger = [
        {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "kind": "symbol",
            "value": "model/PndLmdModelFactory.cxx",
            "provenance_origin_ids": ["model_factory_theory"],
            "plan_present": True,
        },
        {
            "contribution_id": "paper_page_hint::pflueger_2017#51",
            "kind": "paper_page_hint",
            "value": "pflueger_2017#51",
            "provenance_origin_ids": ["model_factory_theory"],
            "plan_present": True,
        },
    ]
    proj, diff = r1.project_component_sensitive_treatment(
        canonical_plan, ledger, ["model/PndLmdModelFactory.cxx"], ["model_factory_theory"]
    )
    # Page hints remain completely untouched!
    assert proj["paper_page_hints"] == {"pflueger_2017": [51, 57, 65]}
    assert "pflueger_2017#51" in diff["held_components_untouched"]


def test_27_uncovered_symbols_untouched_by_projection() -> None:
    """Requirement 27: Uncovered symbols are untouched by projection."""
    canonical_plan = {
        "symbols": ["model/PndLmdDPMAngModel1D.cxx"],
    }
    ledger = [
        {
            "contribution_id": "symbol::model/PndLmdDPMAngModel1D.cxx",
            "kind": "symbol",
            "value": "model/PndLmdDPMAngModel1D.cxx",
            "provenance_origin_ids": ["model_factory_theory"],
            "plan_present": True,
        }
    ]
    # Projection with COVERED_SYMBOL_MASK only containing ModelFactory.cxx
    proj, diff = r1.project_component_sensitive_treatment(
        canonical_plan, ledger, ["model/PndLmdModelFactory.cxx"], ["model_factory_theory"]
    )
    # DPM1D is NOT in covered mask, so it remains untouched
    assert proj["symbols"] == ["model/PndLmdDPMAngModel1D.cxx"]
    assert "model/PndLmdDPMAngModel1D.cxx" in diff["held_components_untouched"]
    assert diff["selected_rule_origins_removed"] == 0


def test_28_control_plan_zero_origin_removal() -> None:
    """Requirement 28: Nonmatching control plan gets zero selected-origin removal."""
    canonical_plan = {
        "symbols": ["model/PndLmdDPMAngModel1D.cxx"],
    }
    ledger = [
        {
            "contribution_id": "symbol::model/PndLmdDPMAngModel1D.cxx",
            "kind": "symbol",
            "value": "model/PndLmdDPMAngModel1D.cxx",
            "provenance_origin_ids": ["dpm_theory_control_rule"],
            "plan_present": True,
        }
    ]
    # For a control, model_factory_theory was not matched
    proj, diff = r1.project_component_sensitive_treatment(
        canonical_plan, ledger, ["model/PndLmdModelFactory.cxx"], ["dpm_theory_control_rule"]
    )
    assert diff["target_rule_matched"] is False
    assert diff["selected_rule_origins_removed"] == 0
    assert proj["symbols"] == canonical_plan["symbols"]


# ---------------------------------------------------------------------------
# Tests 29-31: Outcome Precedence & Execution Safety
# ---------------------------------------------------------------------------

def test_29_successful_component_cannot_validate_sibling() -> None:
    """Requirement 29: Successful component outcome cannot validate uncovered sibling component."""
    case_results = {
        "model/PndLmdModelFactory.cxx": {
            "baseline_reproduced": True,
            "applicability": "ACTIVE_IDENTIFIABLE",
            "treatment_presence": True,
            "origin_subtracted": True,
        }
    }
    outcome = r1.evaluate_component_sensitive_hypothetical_outcome(
        covered_symbols=["model/PndLmdModelFactory.cxx"],
        uncovered_symbols=["model/PndLmdDPMAngModel1D.cxx", "model/PndLmdDPMAngModel2D.cxx"],
        page_hints={"pflueger_2017": [51, 57, 65]},
        case_results=case_results,
    )
    disps = outcome["component_dispositions"]
    assert disps["model/PndLmdModelFactory.cxx"] == r1.DISPOSITION_RETIREMENT_VALIDATED
    # Sibling components remain HOLD
    assert disps["model/PndLmdDPMAngModel1D.cxx"] == r1.DISPOSITION_COVERAGE_GAP
    assert disps["model/PndLmdDPMAngModel2D.cxx"] == r1.DISPOSITION_COVERAGE_GAP


def test_30_full_retirement_validated_cannot_be_produced() -> None:
    """Requirement 30: Full RETIREMENT_VALIDATED cannot be produced under this repaired contract."""
    case_results = {
        "model/PndLmdModelFactory.cxx": {
            "baseline_reproduced": True,
            "applicability": "ACTIVE_IDENTIFIABLE",
            "treatment_presence": True,
            "origin_subtracted": True,
        }
    }
    outcome = r1.evaluate_component_sensitive_hypothetical_outcome(
        covered_symbols=["model/PndLmdModelFactory.cxx"],
        uncovered_symbols=["model/PndLmdDPMAngModel1D.cxx", "model/PndLmdDPMAngModel2D.cxx"],
        page_hints={"pflueger_2017": [51, 57, 65]},
        case_results=case_results,
    )
    # Level 6 verdict is PARTIAL, never full RETIREMENT_VALIDATED
    assert outcome["level"] == 6
    assert outcome["overall_outcome"] == r1.OUTCOME_LEVEL_6_PARTIAL_PASS
    assert "RETIREMENT_VALIDATED" != outcome["overall_outcome"]
    assert "FULL_BATCH2_VALIDATED" != outcome["overall_outcome"]


def test_31_no_provider_execution_path_in_r1() -> None:
    """Requirement 31: Zero provider/scientific/retrieval execution path in R1."""
    audit_res = r1.audit_preregistration(PROJECT_ROOT)
    assert audit_res["status"] == "PASS"

    with open(PROJECT_ROOT / "evaluation/d4_a8_r1_result.json", "r", encoding="utf-8") as f:
        res_data = json.load(f)
    assert res_data["production_activation_authorized"] is False
    assert res_data["d4_a9_authorized"] is False
    assert res_data["zero_provider_accounting"]["analyzer_calls"] == 0
    assert res_data["zero_provider_accounting"]["tokens"] == 0
