"""Focused deterministic unit tests for D4-A8 Model-Factory-Theory Symbol-Retirement Targeted Revalidation Preregistration.

Covers all 20 requirements specified in Section 29 of the D4-A8 contract:
  1. current HEAD/A7 authority exact;
  2. A7 verifier result required before preregistration;
  3. current model_factory_theory exact 3-symbol + 3-hint mask;
  4. g031 metadata/evidence group matches frozen expectations;
  5. g032 metadata/source evidence matches expectations;
  6. g033 metadata/source evidence matches expectations;
  7. g047 is English algorithm_theory and Pflueger-page adjacent;
  8. g064 excluded from formal gate because language != en;
  9. deterministic role audit classifies g031 direct and controls nonmatching;
  10. treatment mask contains exactly 3 symbols;
  11. page hints excluded from treatment;
  12. treatment projection removes selected-rule origins only;
  13. equal symbol value from independent origin preserved;
  14. no-op controls cannot receive treatment mutation;
  15. Level-2 baseline failure precedence;
  16. Level-3 dependency precedence;
  17. Level-5 incomplete applicability;
  18. Level-6 successful PARTIAL outcome;
  19. Level-6 can never produce full RETIREMENT_VALIDATED;
  20. production/config/scientific paths cannot be written by A8.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from evaluation.scripts.d4_a8_model_factory_theory_symbol_retirement_preregistration import (
    A8_COMMIT_MESSAGE,
    EXPECTED_A8_PATHS,
    FORMAL_COHORT,
    HELD_PAGE_HINT_MASK,
    MODEL_FACTORY_THEORY_SYMBOL_MASK,
    QUERY_EXPANSIONS_PATH,
    STARTING_COMMIT_MESSAGE,
    STARTING_HEAD,
    STARTING_PARENT_HEAD,
    TARGET_RULE_ID,
    audit_case_metadata,
    audit_deterministic_rule_matching,
    audit_page_hint_coverage_gap,
    audit_plan_reusability,
    evaluate_hypothetical_outcome,
    load_gold_questions,
    project_treatment_plan,
    verify_production_state,
    verify_starting_boundary,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def gold_questions() -> list[dict[str, Any]]:
    return load_gold_questions(PROJECT_ROOT)


@pytest.fixture
def current_query_expansions() -> dict[str, Any]:
    with open(PROJECT_ROOT / QUERY_EXPANSIONS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 1. current HEAD/A7 authority exact
def test_01_current_head_a7_authority_exact() -> None:
    # Check that STARTING_HEAD is the authorized D4-A7 commit
    cmd_log = ["git", "log", "-1", "--pretty=format:%s", STARTING_HEAD]
    msg = subprocess.run(cmd_log, cwd=PROJECT_ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    assert msg == STARTING_COMMIT_MESSAGE

    cmd_parent = ["git", "rev-parse", f"{STARTING_HEAD}~1"]
    parent = subprocess.run(cmd_parent, cwd=PROJECT_ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    assert parent == STARTING_PARENT_HEAD

    # Verify current HEAD is either STARTING_HEAD (pre-commit) or has STARTING_HEAD as parent (post-commit)
    current_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    if current_head == STARTING_HEAD:
        boundary = verify_starting_boundary(PROJECT_ROOT)
        assert boundary["head_exact"] is True
        assert boundary["msg_exact"] is True
        assert boundary["parent_exact"] is True
    else:
        current_parent = subprocess.run(["git", "rev-parse", "HEAD~1"], cwd=PROJECT_ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
        assert current_parent == STARTING_HEAD


# 2. A7 verifier result required before preregistration
def test_02_a7_verifier_result_required_before_preregistration() -> None:
    # 1. Verify frozen D4-A7 decision artifact
    a7_decision_path = PROJECT_ROOT / "evaluation/d4_a7_validated_subset_locator_retirement_activation.json"
    assert a7_decision_path.exists()
    with open(a7_decision_path, "r", encoding="utf-8") as f:
        a7_data = json.load(f)
    assert a7_data["status"] == "PASS"
    assert a7_data["decision"] == "VALIDATED_SUBSET_LOCATOR_RETIREMENT_ACTIVATED"
    assert a7_data["batch2_validated_subset_production_active"] is True
    assert a7_data["full_batch2_production_activation"] is False

    # 2. Verify production state matches post-A7 activation contract
    prod_state = verify_production_state(PROJECT_ROOT)
    assert prod_state["production_state_valid"] is True
    assert prod_state["effective_acceptance_pipeline_retired"] is True
    assert prod_state["root_macro_usage_retired"] is True
    assert prod_state["model_factory_theory_held"] is True
    assert prod_state["batch1_active"] is True


# 3. current model_factory_theory exact 3-symbol + 3-hint mask
def test_03_current_model_factory_theory_exact_mask(current_query_expansions: dict[str, Any]) -> None:
    rules = {r["rule_id"]: r for r in current_query_expansions.get("rules", [])}
    assert TARGET_RULE_ID in rules
    mft = rules[TARGET_RULE_ID]
    assert mft.get("symbols") == MODEL_FACTORY_THEORY_SYMBOL_MASK
    assert mft.get("symbols") == [
        "model/PndLmdDPMAngModel1D.cxx",
        "model/PndLmdDPMAngModel2D.cxx",
        "model/PndLmdModelFactory.cxx",
    ]
    assert mft.get("paper_page_hints") == HELD_PAGE_HINT_MASK
    assert mft.get("paper_page_hints") == {"pflueger_2017": [51, 57, 65]}
    assert mft.get("structured_replacement", False) is False
    assert "structured_replacement" not in mft


# 4. g031 metadata/evidence group matches frozen expectations
def test_04_g031_metadata_and_evidence_matches_frozen_expectations(gold_questions: list[dict[str, Any]]) -> None:
    audit = audit_case_metadata(gold_questions)
    assert audit["all_valid"] is True
    assert "g031" in audit["case_audits"]
    assert audit["case_audits"]["g031"]["valid"] is True
    assert audit["case_audits"]["g031"]["formal_role"] == "DIRECT_MODEL_FACTORY_TREATMENT_CASE"

    case_map = {q["id"]: q for q in gold_questions}
    g031 = case_map["g031"]
    assert g031["split"] == "dev"
    assert g031["language"] == "en"
    assert g031["intent"] == "api"
    assert g031["expected_status"] == "answered"
    assert g031["review_status"] == "approved"

    e1_group = next(eg for eg in g031["required_evidence_groups"] if eg["group_id"] == "g031.e1")
    assert any(
        ev.get("path") == "model/PndLmdModelFactory.cxx" and ev.get("symbol") == "generateModel"
        for ev in e1_group["any_of"]
    )


# 5. g032 metadata/source evidence matches expectations
def test_05_g032_metadata_and_evidence_matches_expectations(gold_questions: list[dict[str, Any]]) -> None:
    audit = audit_case_metadata(gold_questions)
    assert audit["case_audits"]["g032"]["valid"] is True
    assert audit["case_audits"]["g032"]["formal_role"] == "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL"

    case_map = {q["id"]: q for q in gold_questions}
    g032 = case_map["g032"]
    assert g032["split"] == "dev"
    assert g032["language"] == "en"
    assert g032["intent"] == "api"
    assert g032["expected_status"] == "answered"
    assert g032["review_status"] == "approved"

    e1_group = next(eg for eg in g032["required_evidence_groups"] if eg["group_id"] == "g032.e1")
    assert any(ev.get("path") == "model/PndLmdDPMAngModel1D.cxx" for ev in e1_group["any_of"])


# 6. g033 metadata/source evidence matches expectations
def test_06_g033_metadata_and_evidence_matches_expectations(gold_questions: list[dict[str, Any]]) -> None:
    audit = audit_case_metadata(gold_questions)
    assert audit["case_audits"]["g033"]["valid"] is True
    assert audit["case_audits"]["g033"]["formal_role"] == "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL"

    case_map = {q["id"]: q for q in gold_questions}
    g033 = case_map["g033"]
    assert g033["split"] == "dev"
    assert g033["language"] == "en"
    assert g033["intent"] == "api"
    assert g033["expected_status"] == "answered"
    assert g033["review_status"] == "approved"

    e1_group = next(eg for eg in g033["required_evidence_groups"] if eg["group_id"] == "g033.e1")
    assert any(ev.get("path") == "model/PndLmdDPMAngModel2D.cxx" for ev in e1_group["any_of"])


# 7. g047 is English algorithm_theory and Pflueger-page adjacent
def test_07_g047_metadata_and_evidence_matches_expectations(gold_questions: list[dict[str, Any]]) -> None:
    audit = audit_case_metadata(gold_questions)
    assert audit["case_audits"]["g047"]["valid"] is True
    assert audit["case_audits"]["g047"]["formal_role"] == "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL"

    case_map = {q["id"]: q for q in gold_questions}
    g047 = case_map["g047"]
    assert g047["split"] == "dev"
    assert g047["language"] == "en"
    assert g047["intent"] == "algorithm_theory"
    assert g047["expected_status"] == "answered"
    assert g047["review_status"] == "approved"

    e1_group = next(eg for eg in g047["required_evidence_groups"] if eg["group_id"] == "g047.e1")
    assert any(
        ev.get("source_id") == "pflueger_2017" and ev.get("pdf_page") == 51
        for ev in e1_group["any_of"]
    )


# 8. g064 excluded from formal gate because language != en
def test_08_g064_excluded_from_formal_gate_because_language_not_en(gold_questions: list[dict[str, Any]]) -> None:
    audit = audit_case_metadata(gold_questions)
    assert "g064" in audit["case_audits"]
    g064_audit = audit["case_audits"]["g064"]
    assert g064_audit["language"] == "zh"
    assert g064_audit["excluded"] is True
    assert g064_audit["reason"] == "NON_ENGLISH_OUTSIDE_FORMAL_PRODUCT_GATE"


# 9. deterministic role audit classifies g031 direct and controls nonmatching
def test_09_deterministic_role_audit_classifies_g031_direct_and_controls_nonmatching(gold_questions: list[dict[str, Any]]) -> None:
    matching = audit_deterministic_rule_matching(PROJECT_ROOT, gold_questions)
    assert matching["all_roles_correct"] is True

    res = matching["matching_results"]
    assert res["g031"]["role"] == "DIRECT_TREATMENT"
    assert res["g031"]["target_matched"] is True

    assert res["g032"]["role"] == "NO_OP_CONTROL"
    assert res["g032"]["target_matched"] is False

    assert res["g033"]["role"] == "NO_OP_CONTROL"
    assert res["g033"]["target_matched"] is False

    assert res["g047"]["role"] == "NO_OP_CONTROL"
    assert res["g047"]["target_matched"] is False


# 10. treatment mask contains exactly 3 symbols
def test_10_treatment_mask_contains_exactly_three_symbols() -> None:
    assert len(MODEL_FACTORY_THEORY_SYMBOL_MASK) == 3
    assert MODEL_FACTORY_THEORY_SYMBOL_MASK == [
        "model/PndLmdDPMAngModel1D.cxx",
        "model/PndLmdDPMAngModel2D.cxx",
        "model/PndLmdModelFactory.cxx",
    ]


# 11. page hints excluded from treatment
def test_11_page_hints_excluded_from_treatment() -> None:
    assert HELD_PAGE_HINT_MASK == {"pflueger_2017": [51, 57, 65]}
    gap_audit = audit_page_hint_coverage_gap(PROJECT_ROOT)
    assert gap_audit["status"] == "OPEN"
    assert gap_audit["result"] == "NO_EXISTING_APPROVED_ENGLISH_CASE_FOUND"

    # Verify project_treatment_plan never strips or mutates paper page hints in the plan
    canonical_plan = {
        "symbols": ["model/PndLmdModelFactory.cxx"],
        "paper_page_hints": {"pflueger_2017": [51, 57, 65]},
        "contributions": [
            {
                "rule_id": TARGET_RULE_ID,
                "kind": "symbol",
                "value": "model/PndLmdModelFactory.cxx",
                "applicability": "ACTIVE_IDENTIFIABLE",
            }
        ],
    }
    projected = project_treatment_plan(canonical_plan)
    assert projected.get("paper_page_hints") == {"pflueger_2017": [51, 57, 65]}


# 12. treatment projection removes selected-rule origins only
def test_12_treatment_projection_removes_selected_rule_origins_only() -> None:
    canonical_plan = {
        "symbols": ["model/PndLmdDPMAngModel1D.cxx", "other/file.cxx"],
        "contributions": [
            {
                "rule_id": TARGET_RULE_ID,
                "kind": "symbol",
                "value": "model/PndLmdDPMAngModel1D.cxx",
                "applicability": "ACTIVE_IDENTIFIABLE",
            },
            {
                "rule_id": "other_rule",
                "kind": "symbol",
                "value": "other/file.cxx",
                "applicability": "ACTIVE_IDENTIFIABLE",
            },
        ],
    }
    projected = project_treatment_plan(canonical_plan)
    assert projected["selected_origins_removed"] == 1
    assert "model/PndLmdDPMAngModel1D.cxx" not in projected["symbols"]
    assert "other/file.cxx" in projected["symbols"]
    assert len(projected["contributions"]) == 1
    assert projected["contributions"][0]["rule_id"] == "other_rule"


# 13. equal symbol value from independent origin preserved
def test_13_equal_symbol_value_from_independent_origin_preserved() -> None:
    canonical_plan = {
        "symbols": ["model/PndLmdModelFactory.cxx"],
        "contributions": [
            {
                "rule_id": TARGET_RULE_ID,
                "kind": "symbol",
                "value": "model/PndLmdModelFactory.cxx",
                "applicability": "ACTIVE_IDENTIFIABLE",
            },
            {
                "rule_id": "model_factory_acceptance_methods",
                "kind": "symbol",
                "value": "model/PndLmdModelFactory.cxx",
                "applicability": "ACTIVE_IDENTIFIABLE",
            },
        ],
    }
    projected = project_treatment_plan(canonical_plan)
    assert projected["selected_origins_removed"] == 1
    # model_factory_theory origin was removed, but symbol remains due to independent origin
    assert "model/PndLmdModelFactory.cxx" in projected["symbols"]
    assert len(projected["contributions"]) == 1
    assert projected["contributions"][0]["rule_id"] == "model_factory_acceptance_methods"


# 14. no-op controls cannot receive treatment mutation
def test_14_no_op_controls_cannot_receive_treatment_mutation() -> None:
    control_plan = {
        "symbols": ["model/PndLmdDPMAngModel1D.cxx"],
        "contributions": [
            {
                "rule_id": "dpm_angular_model_1d",
                "kind": "symbol",
                "value": "model/PndLmdDPMAngModel1D.cxx",
                "applicability": "ACTIVE_IDENTIFIABLE",
            }
        ],
    }
    projected = project_treatment_plan(control_plan)
    assert projected["selected_origins_removed"] == 0
    assert projected["symbols"] == control_plan["symbols"]
    assert projected["contributions"] == control_plan["contributions"]


# 15. Level-2 baseline failure precedence
def test_15_level_2_baseline_failure_precedence() -> None:
    outcome = evaluate_hypothetical_outcome(
        baseline_reproduced=False,
        all_symbols_active=True,
        dependency_observed=True,
        control_divergence=True,
        safety_regression=True,
    )
    assert outcome == "INCONCLUSIVE / TARGET_REFERENCE_BASELINE_NOT_REPRODUCED"


# 16. Level-3 dependency precedence
def test_16_level_3_dependency_precedence() -> None:
    outcome = evaluate_hypothetical_outcome(
        baseline_reproduced=True,
        all_symbols_active=True,
        dependency_observed=True,
        control_divergence=False,
        safety_regression=False,
    )
    assert outcome == "DEPENDENCY_OBSERVED_RETAIN"


# 17. Level-5 incomplete applicability
def test_17_level_5_incomplete_applicability() -> None:
    outcome = evaluate_hypothetical_outcome(
        baseline_reproduced=True,
        all_symbols_active=False,
        dependency_observed=False,
        control_divergence=False,
        safety_regression=False,
    )
    assert outcome == "INCONCLUSIVE / SYMBOL_COMPONENT_APPLICABILITY_INCOMPLETE"


# 18. Level-6 successful PARTIAL outcome
def test_18_level_6_successful_partial_outcome() -> None:
    outcome = evaluate_hypothetical_outcome(
        baseline_reproduced=True,
        all_symbols_active=True,
        dependency_observed=False,
        control_divergence=False,
        safety_regression=False,
    )
    assert outcome == "PARTIAL / MODEL_FACTORY_SYMBOL_RETIREMENT_VALIDATED_PAGE_HINTS_HOLD"


# 19. Level-6 can never produce full RETIREMENT_VALIDATED
def test_19_level_6_can_never_produce_full_retirement_validated() -> None:
    for b in (True, False):
        for a in (True, False):
            for d in (True, False):
                for c in (True, False):
                    for s in (True, False):
                        res = evaluate_hypothetical_outcome(b, a, d, c, s)
                        assert res != "RETIREMENT_VALIDATED"
                        assert res != "VALIDATED / FULL_RETIREMENT"


# 20. production/config/scientific paths cannot be written by A8
def test_20_production_config_scientific_paths_cannot_be_written_by_a8() -> None:
    assert len(EXPECTED_A8_PATHS) == 7
    for path in EXPECTED_A8_PATHS:
        assert not path.startswith("src/"), f"Unauthorized src path in A8: {path}"
        assert not path.startswith("configs/"), f"Unauthorized configs path in A8: {path}"
        assert not "d4_a4" in path, f"Unauthorized historical path in A8: {path}"
        assert not "d4_a5" in path, f"Unauthorized historical path in A8: {path}"
        assert not "d4_a6" in path, f"Unauthorized historical path in A8: {path}"
        assert not "d4_a7" in path, f"Unauthorized historical path in A8: {path}"
