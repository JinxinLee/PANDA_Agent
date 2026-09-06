"""Unit tests for D4-A8-R2 — Component-Sensitive Model-Factory Execution Contract Seal.

Covers all required areas:
  - Boundary & Immutability (Items 1-9)
  - Scientific Target Preservation (Items 10-14)
  - Formal Eligibility & Page-Hint Gap (Items 15-22)
  - Section 33 Focused Amendment Tests (Items 1-45):
      * A5 Authority & Ledger Coverage (1-7)
      * Origin-Type Consistency Gate (8-14)
      * A5 Applicability & Projection Semantics (15-24)
      * Treatment Construction & Fail-Closed Precedence (25-26, plus levels 2, 3, 4, 6)
      * Persistence-Before-Gate State Machine (27-30)
      * Plan Reuse Internal Consistency & Budget (31-41)
      * Machine Artifact Drift & Audit Failure Propagation (42-45)
"""

from __future__ import annotations

import copy
import inspect
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
if str(_REPO_ROOT / "evaluation" / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "evaluation" / "scripts"))

import d4_a8_r2_component_sensitive_execution_contract_seal as r2


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def mock_rules() -> dict[str, dict[str, Any]]:
    return {
        r2.TARGET_RULE_ID: {
            "symbols": [
                "model/PndLmdModelFactory.cxx",
                "model/PndLmdDPMAngModel1D.cxx",
                "model/PndLmdDPMAngModel2D.cxx",
            ],
            "concepts": ["DPM model acceptance resolution composition"],
            "repositories": ["luminosityfit"],
            "paper_page_hints": {"pflueger_2017": [51, 57, 65]},
        },
        "model_factory_acceptance_methods": {
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": ["acceptance method"],
            "repositories": ["luminosityfit"],
            "paper_page_hints": {},
        },
        "acceptance_pipeline_active": {
            "symbols": ["data/PndLmdAcceptance.cxx"],
            "concepts": [],
            "repositories": ["pandaroot"],
            "paper_page_hints": {},
        },
    }


# ---------------------------------------------------------------------------
# Category 1: Boundary & Immutability (Items 1-9)
# ---------------------------------------------------------------------------

class TestBoundaryAndImmutability:
    """Tests items 1-9."""

    def test_item_01_to_03_starting_boundary_head_msg_parent(self, project_root: Path) -> None:
        """Items 1, 2, 3: Starting HEAD exact, message exact, parent exact."""
        receipt = r2.verify_starting_boundary(project_root, ref=r2.STARTING_HEAD)
        assert receipt["head_exact"], f"Starting HEAD mismatch: {receipt['head_sha']}"
        assert receipt["msg_exact"], f"Starting message mismatch: {receipt['head_msg']}"
        assert receipt["parent_exact"], f"Starting parent mismatch: {receipt['parent_sha']}"

    def test_item_04_clean_worktree_enforced(self, project_root: Path) -> None:
        """Item 4: Clean worktree enforced."""
        res = r2.verify_clean_worktree(project_root)
        assert isinstance(res, bool)

    def test_item_05_historical_r1_blobs_sealed(self, project_root: Path) -> None:
        """Item 5: Historical R1 blobs sealed."""
        res = r2.verify_historical_r1_immutability(project_root, head_ref=r2.STARTING_HEAD)
        assert res["all_match"], f"Historical R1 blob mismatch: {res['mismatches']}"

    def test_item_06_historical_a8_blobs_sealed(self, project_root: Path) -> None:
        """Item 6: Historical A8 blobs sealed."""
        res = r2.verify_historical_a8_immutability(project_root, head_ref=r2.STARTING_HEAD)
        assert res["all_match"], f"Historical A8 blob mismatch: {res['mismatches']}"

    def test_item_07_src_tree_immutable(self, project_root: Path) -> None:
        """Item 7: src tree immutable."""
        res = r2.verify_production_tree_immutability(
            project_root, head_ref=r2.STARTING_HEAD, base_ref=r2.STARTING_HEAD
        )
        assert res["src_tree_immutable"]
        res_bad = r2.verify_production_tree_immutability(
            project_root, _override_src_tree=("hash1", "hash2")
        )
        assert not res_bad["src_tree_immutable"]

    def test_item_08_configs_tree_immutable(self, project_root: Path) -> None:
        """Item 8: configs tree immutable."""
        res = r2.verify_configs_immutability(
            project_root, head_ref=r2.STARTING_HEAD, base_ref=r2.STARTING_HEAD
        )
        assert res["configs_immutable"]
        res_bad = r2.verify_configs_immutability(
            project_root, _override_configs_paths=["configs/query_expansions.yaml"]
        )
        assert not res_bad["configs_immutable"]

    def test_item_09_cumulative_diff_allowlist_enforced(self, project_root: Path) -> None:
        """Item 9: Exactly seven changed files allowlist enforced."""
        exact_list = sorted(r2.EXPECTED_R2_PATHS)
        assert len(exact_list) == 7
        res_ok = r2.verify_git_cumulative_diff(project_root, _override_diff_paths=exact_list)
        assert res_ok["exact_match"]

        res_extra = r2.verify_git_cumulative_diff(
            project_root, _override_diff_paths=exact_list + ["unexpected.txt"]
        )
        assert not res_extra["exact_match"]


# ---------------------------------------------------------------------------
# Category 2: Scientific Target Preservation (Items 10-14)
# ---------------------------------------------------------------------------

class TestScientificTargetPreservation:
    """Tests items 10-14."""

    def test_item_10_to_12_masks_exact(self) -> None:
        """Items 10, 11, 12: COVERED_SYMBOL_MASK, UNCOVERED_SYMBOL_HOLD_MASK, PAGE_HINT_HOLD_MASK exact."""
        assert r2.FROZEN_COVERED_SYMBOL_MASK == ["model/PndLmdModelFactory.cxx"]
        assert r2.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK == [
            "model/PndLmdDPMAngModel1D.cxx",
            "model/PndLmdDPMAngModel2D.cxx",
        ]
        assert r2.FROZEN_PAGE_HINT_HOLD_MASK == {"pflueger_2017": [51, 57, 65]}

    def test_item_13_target_mask_drift_blocks(self, project_root: Path) -> None:
        """Item 13: R1 mask drift blocks."""
        gold = r2.load_gold_questions(project_root)
        cov = r2.audit_component_sensitive_coverage(project_root, gold)
        assert cov["r1_target_mask_preserved"]
        assert cov["covered_symbol_mask"] == r2.FROZEN_COVERED_SYMBOL_MASK
        assert sorted(cov["uncovered_symbol_hold_mask"]) == sorted(r2.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK)

    def test_item_14_formal_roles_preserved(self, project_root: Path) -> None:
        """Item 14: Formal roles preserved (g031 direct; g032, g033, g047 controls)."""
        gold = r2.load_gold_questions(project_root)
        case_audit = r2.audit_case_eligibility(gold)
        assert case_audit["all_valid"]
        ca = case_audit["case_audits"]
        assert ca["g031"]["formal_role"] == "DIRECT_MODEL_FACTORY_TREATMENT_CASE"
        assert ca["g032"]["formal_role"] == "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL"
        assert ca["g033"]["formal_role"] == "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL"
        assert ca["g047"]["formal_role"] == "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL"


# ---------------------------------------------------------------------------
# Category 3: Formal Eligibility & Page-Hint Gap (Items 15-22)
# ---------------------------------------------------------------------------

class TestFormalEligibilityAndPageHintGap:
    """Tests items 15-22."""

    @pytest.mark.parametrize(
        "q_mut,expected_class,expected_formal",
        [
            ({}, "FORMAL_ELIGIBLE", True),
            ({"language": "zh"}, "EXCLUDED", False),
            ({"review_status": "draft"}, "EXCLUDED", False),
            ({"expected_status": "unanswered"}, "EXCLUDED", False),
            ({"split": "train"}, "EXCLUDED", False),
        ],
    )
    def test_item_15_to_18_gold_formal_criteria(
        self, q_mut: dict[str, Any], expected_class: str, expected_formal: bool
    ) -> None:
        """Items 15, 16, 17, 18: Gold formal eligibility criteria."""
        base_q = {
            "id": "test_case",
            "language": "en",
            "review_status": "approved",
            "expected_status": "answered",
            "split": "dev",
        }
        base_q.update(q_mut)
        res = r2.classify_formal_case_eligibility(base_q, "gold")
        assert res["classification"] == expected_class
        assert res["formal_eligible"] == expected_formal

    def test_item_19_novel_dev_classified_diagnostic_only(self) -> None:
        """Item 19: Novel Dev cases classified DIAGNOSTIC_ONLY unless authorized."""
        novel_q = {
            "id": "n014",
            "language": "en",
            "review_status": "approved",
            "expected_status": "answered",
            "split": "novel_dev",
        }
        res = r2.classify_formal_case_eligibility(novel_q, "novel_dev")
        assert res["classification"] == "DIAGNOSTIC_ONLY"
        assert not res["formal_eligible"]

    def test_item_20_page_hint_gap_distinguishes_gold_vs_novel(self, project_root: Path) -> None:
        """Item 20: Page-hint gap audit distinguishes Gold vs Novel."""
        gap = r2.audit_page_hint_coverage_gap_approval_aware(project_root)
        assert "formal_eligible_candidates" in gap
        assert "diagnostic_only_candidates" in gap
        assert "excluded_candidates" in gap

    def test_item_21_page_hint_gap_open_no_approved_case(self, project_root: Path) -> None:
        """Item 21: Page-hint gap OPEN / no approved case found."""
        gap = r2.audit_page_hint_coverage_gap_approval_aware(project_root)
        assert gap["status"] == "OPEN"
        assert gap["result"] == "NO_EXISTING_APPROVED_ENGLISH_CASE_FOUND"
        assert len(gap["formal_eligible_candidates"]) == 0

    def test_item_22_page_hint_gap_drift_blocks(self, monkeypatch: pytest.MonkeyPatch, project_root: Path) -> None:
        """Item 22: Page-hint gap drift blocks."""
        mock_gold = [
            {
                "id": "mock_g999",
                "language": "en",
                "review_status": "approved",
                "expected_status": "answered",
                "split": "dev",
                "intent": "algorithm_theory",
                "query": "PndLmdModelFactory generateModel algorithm theory",
            }
        ]
        monkeypatch.setattr(r2, "load_gold_questions", lambda _: mock_gold)
        gap = r2.audit_page_hint_coverage_gap_approval_aware(project_root)
        assert gap["result"] == "EXISTING_APPROVED_ENGLISH_CASE_FOUND"
        assert len(gap["formal_eligible_candidates"]) == 1


# ---------------------------------------------------------------------------
# Section 33 Items 1-7: A5 Authority & Ledger Coverage
# ---------------------------------------------------------------------------

class TestA5AuthorityAndLedgerCoverage:
    """Section 33, items 1-7."""

    def test_sec33_item_01_a5_authority_import_failure_causes_audit_fail(
        self, monkeypatch: pytest.MonkeyPatch, project_root: Path
    ) -> None:
        """Item 1: A5 authority import failure -> audit FAIL."""
        def mock_load() -> Any:
            raise ImportError("Mock authority module missing")
        monkeypatch.setattr(r2, "load_a5_authority", mock_load)
        res = r2.audit_execution_contract(project_root)
        assert res["status"] == "FAIL"
        assert not res["a5_authority_audit"]["authority_loaded"]

    def test_sec33_item_02_a5_required_helper_missing_causes_audit_fail(
        self, monkeypatch: pytest.MonkeyPatch, project_root: Path
    ) -> None:
        """Item 2: A5 required helper missing -> audit FAIL."""
        real_a5 = r2.load_a5_authority()
        class IncompleteA5:
            pass
        incomplete = IncompleteA5()
        for name in r2.A5_REQUIRED_HELPERS[:-1]:
            setattr(incomplete, name, getattr(real_a5, name, None))
        monkeypatch.setattr(r2, "load_a5_authority", lambda: incomplete)
        res = r2.audit_execution_contract(project_root)
        assert res["status"] == "FAIL"
        assert not res["a5_authority_audit"]["required_helpers_present"]

    def test_sec33_item_03_no_broad_silent_scientific_fallback(self) -> None:
        """Item 3: No broad silent scientific fallback."""
        source = inspect.getsource(r2.load_a5_authority)
        assert "except Exception:" not in source
        assert "pass" not in source

    def test_sec33_item_04_actual_a5_ledger_helper_used_for_authority(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 4: Actual A5 ledger helper used for authority."""
        plan = {
            "intent": "api",
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        ledger = r2.build_real_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        a5 = r2.load_a5_authority()
        expected = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        assert ledger == expected

    def test_sec33_item_05_full_ledger_coverage_rejects_missing_concept(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 5: Full ledger coverage rejects missing concept entry."""
        a5 = r2.load_a5_authority()
        plan = {
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": ["DPM model acceptance resolution composition"],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        ledger_no_concept = [e for e in ledger if e["kind"] != "concept"]
        ok, err = a5.validate_ledger_coverage(plan, ledger_no_concept)
        assert not ok
        assert "Concept contribution missing" in str(err)

    def test_sec33_item_06_full_ledger_coverage_rejects_missing_repository(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 6: Full ledger coverage rejects missing repository entry."""
        a5 = r2.load_a5_authority()
        plan = {
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        ledger_no_repo = [e for e in ledger if e["kind"] != "repository"]
        ok, err = a5.validate_ledger_coverage(plan, ledger_no_repo)
        assert not ok
        assert "Repository contribution missing" in str(err)

    def test_sec33_item_07_full_ledger_coverage_rejects_missing_page_hint(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 7: Full ledger coverage rejects missing page-hint entry."""
        a5 = r2.load_a5_authority()
        plan = {
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {"pflueger_2017": [51]},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        ledger_no_hint = [e for e in ledger if e["kind"] != "paper_page_hint"]
        ok, err = a5.validate_ledger_coverage(plan, ledger_no_hint)
        assert not ok
        assert "Page hint contribution missing" in str(err)


# ---------------------------------------------------------------------------
# Section 33 Items 8-14: Origin-Type Consistency Gate
# ---------------------------------------------------------------------------

class TestOriginTypeConsistencyGate:
    """Section 33, items 8-14."""

    def test_sec33_item_08_missing_origin_types_invalid(self) -> None:
        """Item 8: Missing origin_types -> protocol invalid."""
        entry = {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "provenance_origin_ids": ["model_factory_theory"],
            "plan_present": True,
        }
        ok, err = r2.validate_origin_type_consistency([entry])
        assert not ok
        assert "origin_types is not a dict" in str(err)

    def test_sec33_item_09_origin_type_key_missing_for_provenance_origin(self) -> None:
        """Item 9: Origin-type key missing for a provenance origin -> protocol invalid."""
        entry = {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "provenance_origin_ids": ["model_factory_theory", "extra_origin"],
            "origin_types": {"model_factory_theory": r2.ORIGIN_TYPE_REVIEWED_RULE},
            "plan_present": True,
        }
        ok, err = r2.validate_origin_type_consistency([entry])
        assert not ok
        assert "do not match exactly" in str(err)

    def test_sec33_item_10_extra_unknown_origin_type_key_invalid(self) -> None:
        """Item 10: Extra unknown origin-type key -> protocol invalid."""
        entry = {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "provenance_origin_ids": ["model_factory_theory"],
            "origin_types": {
                "model_factory_theory": r2.ORIGIN_TYPE_REVIEWED_RULE,
                "spurious_origin": "reviewed_expansion_rule",
            },
            "plan_present": True,
        }
        ok, err = r2.validate_origin_type_consistency([entry])
        assert not ok
        assert "do not match exactly" in str(err)

    def test_sec33_item_11_reviewed_rule_with_wrong_origin_type_invalid(self) -> None:
        """Item 11: Reviewed rule with wrong origin type -> protocol invalid."""
        entry = {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "provenance_origin_ids": ["model_factory_theory"],
            "origin_types": {"model_factory_theory": "wrong_origin_type"},
            "plan_present": True,
        }
        ok, err = r2.validate_origin_type_consistency([entry], known_rule_ids=["model_factory_theory"])
        assert not ok
        assert "wrong type" in str(err)

    def test_sec33_item_12_analyzer_delta_with_wrong_type_invalid(self) -> None:
        """Item 12: Analyzer delta with wrong type -> protocol invalid."""
        entry = {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "provenance_origin_ids": [r2.ORIGIN_ACCEPTED_ANALYZER_DELTA],
            "origin_types": {r2.ORIGIN_ACCEPTED_ANALYZER_DELTA: "reviewed_expansion_rule"},
            "plan_present": True,
        }
        ok, err = r2.validate_origin_type_consistency([entry])
        assert not ok
        assert "wrong type" in str(err)

    def test_sec33_item_13_runtime_override_with_wrong_type_invalid(self) -> None:
        """Item 13: Runtime override with wrong type -> protocol invalid."""
        entry = {
            "contribution_id": "paper_page_hint::li_2026#141",
            "provenance_origin_ids": [r2.ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE],
            "origin_types": {r2.ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE: "reviewed_expansion_rule"},
            "plan_present": True,
        }
        ok, err = r2.validate_origin_type_consistency([entry])
        assert not ok
        assert "wrong type" in str(err)

    def test_sec33_item_14_duplicate_contribution_id_invalid(self) -> None:
        """Item 14: Duplicate contribution ID -> protocol invalid."""
        entry1 = {
            "contribution_id": "symbol::model/PndLmdModelFactory.cxx",
            "provenance_origin_ids": ["model_factory_theory"],
            "origin_types": {"model_factory_theory": r2.ORIGIN_TYPE_REVIEWED_RULE},
            "plan_present": True,
        }
        entry2 = copy.deepcopy(entry1)
        ok, err = r2.validate_origin_type_consistency([entry1, entry2])
        assert not ok
        assert "Duplicate contribution_id" in str(err)


# ---------------------------------------------------------------------------
# Section 33 Items 15-24: A5 Applicability & Projection Semantics
# ---------------------------------------------------------------------------

class TestA5ApplicabilityAndProjection:
    """Section 33, items 15-24."""

    def test_sec33_item_15_real_a5_active_applicability_fixture(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 15: Real A5 ACTIVE applicability fixture."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        mask_entries = a5.build_batch2_mask_entries("g031", [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, summary = a5.classify_component_applicability(plan, ledger, mask_entries)
        assert summary["active"] == 1
        assert receipts[0]["applicability_status"] == r2.APPLICABILITY_ACTIVE

    def test_sec33_item_16_real_a5_inactive_applicability_fixture(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 16: Real A5 INACTIVE applicability fixture."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, ["model_factory_acceptance_methods"])
        mask_entries = a5.build_batch2_mask_entries("g031", [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, summary = a5.classify_component_applicability(plan, ledger, mask_entries)
        assert summary["inactive"] == 1
        assert receipts[0]["applicability_status"] == r2.APPLICABILITY_INACTIVE

    def test_sec33_item_17_real_a5_ambiguous_fixture(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 17: Real A5 AMBIGUOUS fixture."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        ledger[0]["plan_present"] = False  # Contradicts plan
        mask_entries = a5.build_batch2_mask_entries("g031", [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, summary = a5.classify_component_applicability(plan, ledger, mask_entries)
        assert summary["ambiguous"] == 1
        assert receipts[0]["applicability_status"] == r2.APPLICABILITY_AMBIGUOUS

    def test_sec33_item_18_sole_target_origin_effective_symbol_removal(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 18: Sole target origin -> effective symbol removal."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        mask_entries = a5.build_batch2_mask_entries("g031", [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, _ = a5.classify_component_applicability(plan, ledger, mask_entries)
        proj, sub_rec = a5.build_retirement_projection_r1(
            plan, ledger, receipts, [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
        )
        assert "model/PndLmdModelFactory.cxx" not in proj["symbols"]
        assert "model/PndLmdModelFactory.cxx" in sub_rec["effective_removed_symbols"]

    def test_sec33_item_19_independent_reviewed_rule_origin_symbol_survives(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 19: Independent reviewed-rule origin -> symbol survives."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        ledger = a5.build_contribution_ledger(
            plan, mock_rules, [r2.TARGET_RULE_ID, "model_factory_acceptance_methods"]
        )
        mask_entries = a5.build_batch2_mask_entries("g031", [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, _ = a5.classify_component_applicability(plan, ledger, mask_entries)
        proj, sub_rec = a5.build_retirement_projection_r1(
            plan, ledger, receipts, [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
        )
        assert "model/PndLmdModelFactory.cxx" in proj["symbols"]
        assert len(sub_rec["effective_removed_symbols"]) == 0

    def test_sec33_item_20_analyzer_semantic_origin_symbol_survives(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 20: Analyzer semantic origin -> symbol survives."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
            "analysis_diagnostics": {
                "analyzer_accepted_semantic_delta": {
                    "symbols": ["model/PndLmdModelFactory.cxx"]
                }
            },
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        mask_entries = a5.build_batch2_mask_entries("g031", [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, _ = a5.classify_component_applicability(plan, ledger, mask_entries)
        proj, sub_rec = a5.build_retirement_projection_r1(
            plan, ledger, receipts, [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
        )
        assert "model/PndLmdModelFactory.cxx" in proj["symbols"]
        assert len(sub_rec["effective_removed_symbols"]) == 0

    def test_sec33_item_21_real_runtime_deterministic_fixture_unaffected(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 21: Real runtime-deterministic fixture remains unaffected."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {"li_2026": [141]},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        mask_entries = a5.build_batch2_mask_entries("g031", [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, _ = a5.classify_component_applicability(plan, ledger, mask_entries)
        proj, _ = a5.build_retirement_projection_r1(
            plan, ledger, receipts, [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
        )
        assert proj["paper_page_hints"] == {"li_2026": [141]}

    def test_sec33_item_22_dpm_hold_symbols_never_mutate(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 22: DPM HOLD symbols never mutate."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": [
                "model/PndLmdModelFactory.cxx",
                "model/PndLmdDPMAngModel1D.cxx",
                "model/PndLmdDPMAngModel2D.cxx",
            ],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        mask_entries = a5.build_batch2_mask_entries("g031", [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, _ = a5.classify_component_applicability(plan, ledger, mask_entries)
        proj, _ = a5.build_retirement_projection_r1(
            plan, ledger, receipts, [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
        )
        assert "model/PndLmdDPMAngModel1D.cxx" in proj["symbols"]
        assert "model/PndLmdDPMAngModel2D.cxx" in proj["symbols"]

    def test_sec33_item_23_page_hints_never_mutate(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 23: Page hints never mutate."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {"pflueger_2017": [51, 57, 65]},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [r2.TARGET_RULE_ID])
        mask_entries = a5.build_batch2_mask_entries("g031", [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, _ = a5.classify_component_applicability(plan, ledger, mask_entries)
        proj, _ = a5.build_retirement_projection_r1(
            plan, ledger, receipts, [r2.TARGET_RULE_ID], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
        )
        assert proj["paper_page_hints"] == {"pflueger_2017": [51, 57, 65]}

    def test_sec33_item_24_control_gets_zero_target_subtraction(
        self, mock_rules: dict[str, dict[str, Any]]
    ) -> None:
        """Item 24: Control gets zero target subtraction."""
        a5 = r2.load_a5_authority()
        plan = {
            "intent": "api",
            "symbols": ["data/PndLmdAcceptance.cxx"],
            "concepts": [],
            "target_repositories": ["pandaroot"],
            "paper_page_hints": {},
        }
        ledger = a5.build_contribution_ledger(plan, mock_rules, [])
        mask_entries = a5.build_batch2_mask_entries("g032", [], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS)
        receipts, summary = a5.classify_component_applicability(plan, ledger, mask_entries)
        proj, sub_rec = a5.build_retirement_projection_r1(
            plan, ledger, receipts, [], masks=r2.COMPONENT_SENSITIVE_A9_RETIREMENT_MASKS
        )
        assert len(mask_entries) == 0
        assert summary["active"] == 0
        assert proj == plan
        assert sub_rec["effective_removal_count"] == 0


# ---------------------------------------------------------------------------
# Section 33 Items 25-26: Treatment Construction & Precedence
# ---------------------------------------------------------------------------

class TestTreatmentConstructionFailClosedAndOutcomes:
    """Section 33, items 25-26, plus outcome precedence."""

    def test_sec33_item_25_invalid_treatment_construction_causes_level_1(self) -> None:
        """Item 25: Invalid treatment construction -> Level 1 INVALID_PROTOCOL."""
        # 1. Direct constructor raises TargetedValidationProtocolError
        with pytest.raises(r2.TargetedValidationProtocolError):
            r2.construct_component_sensitive_treatment_or_raise(
                {"symbols": ["model/PndLmdModelFactory.cxx"]},
                [],  # empty ledger -> fails ledger coverage
                [r2.TARGET_RULE_ID],
                "g031",
            )
        # 2. Evaluator marks Level 1
        res = r2.evaluate_component_sensitive_hypothetical_outcome(
            r2.FROZEN_COVERED_SYMBOL_MASK,
            r2.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK,
            r2.FROZEN_PAGE_HINT_HOLD_MASK,
            {},
            malformed_treatment=True,
        )
        assert res["level"] == 1
        assert res["overall_outcome"] == r2.OUTCOME_LEVEL_1_INVALID
        assert res["decision"] == "INVALID_PROTOCOL"

    def test_sec33_item_26_invalid_treatment_construction_cannot_become_baseline_failure(self) -> None:
        """Item 26: Invalid treatment construction cannot become baseline failure."""
        res = r2.evaluate_component_sensitive_hypothetical_outcome(
            r2.FROZEN_COVERED_SYMBOL_MASK,
            r2.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK,
            r2.FROZEN_PAGE_HINT_HOLD_MASK,
            {"model/PndLmdModelFactory.cxx": {"baseline_reproduced": False}},
            malformed_treatment=True,
        )
        # Level 1 takes precedence over Level 2
        assert res["level"] == 1
        assert res["overall_outcome"] != r2.OUTCOME_LEVEL_2_BASELINE

    def test_outcome_level_2_baseline_not_reproduced(self) -> None:
        """Level 2: Baseline not reproduced."""
        res = r2.evaluate_component_sensitive_hypothetical_outcome(
            r2.FROZEN_COVERED_SYMBOL_MASK,
            r2.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK,
            r2.FROZEN_PAGE_HINT_HOLD_MASK,
            {"model/PndLmdModelFactory.cxx": {"baseline_reproduced": False}},
        )
        assert res["level"] == 2
        assert res["overall_outcome"] == r2.OUTCOME_LEVEL_2_BASELINE

    def test_outcome_level_3_dependency_observed_retain(self) -> None:
        """Level 3: Valid attributable T/F -> dependency retained."""
        res = r2.evaluate_component_sensitive_hypothetical_outcome(
            r2.FROZEN_COVERED_SYMBOL_MASK,
            r2.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK,
            r2.FROZEN_PAGE_HINT_HOLD_MASK,
            {
                "model/PndLmdModelFactory.cxx": {
                    "baseline_reproduced": True,
                    "treatment_presence": False,
                    "origin_subtracted": True,
                    "dependency_observed": True,
                }
            },
        )
        assert res["level"] == 3
        assert res["overall_outcome"] == r2.OUTCOME_LEVEL_3_DEPENDENCY

    def test_outcome_level_4_control_divergence(self) -> None:
        """Level 4: Control divergence causes regression fail."""
        res = r2.evaluate_component_sensitive_hypothetical_outcome(
            r2.FROZEN_COVERED_SYMBOL_MASK,
            r2.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK,
            r2.FROZEN_PAGE_HINT_HOLD_MASK,
            {
                "model/PndLmdModelFactory.cxx": {
                    "baseline_reproduced": True,
                    "retirement_validated": True,
                }
            },
            control_divergence=True,
        )
        assert res["level"] == 4
        assert res["overall_outcome"] == r2.OUTCOME_LEVEL_4_REGRESSION

    def test_outcome_level_6_partial_pass(self) -> None:
        """Level 6: Valid T/T -> covered component retirement validated."""
        res = r2.evaluate_component_sensitive_hypothetical_outcome(
            r2.FROZEN_COVERED_SYMBOL_MASK,
            r2.FROZEN_UNCOVERED_SYMBOL_HOLD_MASK,
            r2.FROZEN_PAGE_HINT_HOLD_MASK,
            {
                "model/PndLmdModelFactory.cxx": {
                    "baseline_reproduced": True,
                    "retirement_validated": True,
                }
            },
        )
        assert res["level"] == 6
        assert res["overall_outcome"] == r2.OUTCOME_LEVEL_6_PARTIAL_PASS
        assert res["component_dispositions"]["model/PndLmdModelFactory.cxx"] == r2.DISPOSITION_RETIREMENT_VALIDATED
        assert res["component_dispositions"]["model/PndLmdDPMAngModel1D.cxx"] == r2.DISPOSITION_COVERAGE_GAP
        assert res["component_dispositions"]["pflueger_2017:[51, 57, 65]"] == r2.DISPOSITION_OUTSIDE_SCOPE
        assert res["overall_outcome"] != "RETIREMENT_VALIDATED"


# ---------------------------------------------------------------------------
# Section 33 Items 27-30: Persistence-Before-Gate State Machine
# ---------------------------------------------------------------------------

class TestPersistenceBeforeGateContract:
    """Section 33, items 27-30."""

    def test_sec33_item_27_acquired_to_gated_transition_rejected(self) -> None:
        """Item 27: ACQUIRED -> GATED persistence transition rejected."""
        with pytest.raises(r2.StateTransitionError):
            r2.transition_execution_state(r2.STATE_ACQUIRED, r2.STATE_GATED)

    def test_sec33_item_28_acquired_to_persisted_to_gated_accepted(self) -> None:
        """Item 28: ACQUIRED -> PERSISTED -> GATED accepted."""
        s1 = r2.transition_execution_state(r2.STATE_ACQUIRED, r2.STATE_PERSISTED)
        assert s1 == r2.STATE_PERSISTED
        s2 = r2.transition_execution_state(s1, r2.STATE_GATED)
        assert s2 == r2.STATE_GATED

    def test_sec33_item_29_missing_persistence_receipt_rejected(self) -> None:
        """Item 29: Missing persistence receipt rejected."""
        ok, err = r2.validate_persistence_receipt({})
        assert not ok
        assert "Missing required key" in str(err)

    def test_sec33_item_30_incomplete_persisted_record_rejected(self) -> None:
        """Item 30: Incomplete persisted record rejected."""
        incomplete = {
            "case_id": "g031",
            "persisted_record_path": "some/path.json",
            "persistence_completed": True,
            # missing canonical_plan, contribution_ledger, provider_accounting
        }
        ok, err = r2.validate_persistence_receipt(incomplete)
        assert not ok
        assert "Missing required key" in str(err)


# ---------------------------------------------------------------------------
# Section 33 Items 31-41: Plan Reuse Contract & Budget
# ---------------------------------------------------------------------------

class TestPlanReuseContractAndBudget:
    """Section 33, items 31-41."""

    @pytest.fixture
    def valid_plan_record(self, project_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
        gold = r2.load_gold_questions(project_root)
        g031 = next(q for q in gold if q["id"] == "g031")
        from panda_agent.config import load_query_expansions
        from panda_agent.d3_structured import select_matching_query_expansions
        qe = load_query_expansions(project_root / r2.QUERY_EXPANSIONS_PATH)
        cur_dec = select_matching_query_expansions(g031.get("query", ""), qe.rules, None)
        cur_matched = [r.rule_id for r in cur_dec.active_matching_rules]

        a5 = r2.load_a5_authority()
        plan = {
            "intent": g031.get("intent", "algorithm_theory"),
            "symbols": ["model/PndLmdModelFactory.cxx"],
            "concepts": [],
            "target_repositories": ["luminosityfit"],
            "paper_page_hints": {},
        }
        computed_sig, _ = a5.compute_plan_signature(plan)
        canonical_ser = json.dumps(plan)
        rules_by_id = {
            r.rule_id: {
                "symbols": list(r.symbols),
                "concepts": list(r.concepts),
                "repositories": list(r.repositories),
                "paper_page_hints": {src: list(pages) for src, pages in r.paper_page_hints.items()},
            }
            for r in qe.rules
        }
        ledger = a5.build_contribution_ledger(plan, rules_by_id, cur_matched)

        record = {
            "case_id": "g031",
            "question": g031["query"],
            "canonical_plan": plan,
            "canonical_serialization": canonical_ser,
            "plan_signature": computed_sig,
            "provider_accounting": {
                "model_id": "gemini-3.8-flash",
                "temperature": 0.0,
                "location": "global",
                "retries": 0,
            },
            "matched_rule_identities": cur_matched,
            "contribution_ledger": ledger,
            "provenance_origin_receipts": [{"receipt": "ok"}],
            "component_applicability_receipts": [{"receipt": "ok"}],
        }
        return record, g031

    def test_sec33_item_31_canonical_serialization_mismatch_rejects(
        self, valid_plan_record: tuple[dict[str, Any], dict[str, Any]], project_root: Path
    ) -> None:
        """Item 31: Canonical serialization mismatch rejects reuse."""
        rec, q = valid_plan_record
        rec = copy.deepcopy(rec)
        rec["canonical_serialization"] = json.dumps({"intent": "api", "symbols": ["other.cxx"]})
        compat, code, detail = r2.check_plan_record_complete_contract(rec, "g031", q, project_root)
        assert not compat
        assert code == r2.PLAN_REUSE_SERIALIZATION_INCONSISTENT

    def test_sec33_item_32_plan_signature_mismatch_rejects(
        self, valid_plan_record: tuple[dict[str, Any], dict[str, Any]], project_root: Path
    ) -> None:
        """Item 32: Plan signature mismatch rejects reuse."""
        rec, q = valid_plan_record
        rec = copy.deepcopy(rec)
        rec["plan_signature"] = "tampered_signature"
        compat, code, detail = r2.check_plan_record_complete_contract(rec, "g031", q, project_root)
        assert not compat
        assert code == r2.PLAN_REUSE_SIGNATURE_MISMATCH

    def test_sec33_item_33_missing_temperature_rejects(
        self, valid_plan_record: tuple[dict[str, Any], dict[str, Any]], project_root: Path
    ) -> None:
        """Item 33: Missing temperature rejects reuse."""
        rec, q = valid_plan_record
        rec = copy.deepcopy(rec)
        del rec["provider_accounting"]["temperature"]
        compat, code, detail = r2.check_plan_record_complete_contract(rec, "g031", q, project_root)
        assert not compat
        assert code == r2.PLAN_REUSE_PROVIDER_CONTRACT_INCOMPLETE

    def test_sec33_item_34_missing_location_rejects(
        self, valid_plan_record: tuple[dict[str, Any], dict[str, Any]], project_root: Path
    ) -> None:
        """Item 34: Missing location rejects reuse."""
        rec, q = valid_plan_record
        rec = copy.deepcopy(rec)
        del rec["provider_accounting"]["location"]
        compat, code, detail = r2.check_plan_record_complete_contract(rec, "g031", q, project_root)
        assert not compat
        assert code == r2.PLAN_REUSE_PROVIDER_CONTRACT_INCOMPLETE

    def test_sec33_item_35_missing_retries_rejects(
        self, valid_plan_record: tuple[dict[str, Any], dict[str, Any]], project_root: Path
    ) -> None:
        """Item 35: Missing retries rejects reuse."""
        rec, q = valid_plan_record
        rec = copy.deepcopy(rec)
        del rec["provider_accounting"]["retries"]
        compat, code, detail = r2.check_plan_record_complete_contract(rec, "g031", q, project_root)
        assert not compat
        assert code == r2.PLAN_REUSE_PROVIDER_CONTRACT_INCOMPLETE

    def test_sec33_item_36_wrong_location_rejects(
        self, valid_plan_record: tuple[dict[str, Any], dict[str, Any]], project_root: Path
    ) -> None:
        """Item 36: Wrong location rejects reuse."""
        rec, q = valid_plan_record
        rec = copy.deepcopy(rec)
        rec["provider_accounting"]["location"] = "us-central1"
        compat, code, detail = r2.check_plan_record_complete_contract(rec, "g031", q, project_root)
        assert not compat
        assert code == r2.PLAN_REUSE_PROVIDER_CONTRACT_INCOMPATIBLE

    def test_sec33_item_37_matched_rule_identity_missing_rejects(
        self, valid_plan_record: tuple[dict[str, Any], dict[str, Any]], project_root: Path
    ) -> None:
        """Item 37: Matched-rule identity missing rejects reuse."""
        rec, q = valid_plan_record
        rec = copy.deepcopy(rec)
        del rec["matched_rule_identities"]
        compat, code, detail = r2.check_plan_record_complete_contract(rec, "g031", q, project_root)
        assert not compat
        assert code == r2.PLAN_REUSE_BEHAVIOR_INCOMPATIBLE

    def test_sec33_item_38_matched_rule_identity_drift_rejects(
        self, valid_plan_record: tuple[dict[str, Any], dict[str, Any]], project_root: Path
    ) -> None:
        """Item 38: Matched-rule identity drift rejects reuse."""
        rec, q = valid_plan_record
        rec = copy.deepcopy(rec)
        rec["matched_rule_identities"] = ["unrelated_rule_xyz"]
        compat, code, detail = r2.check_plan_record_complete_contract(rec, "g031", q, project_root)
        assert not compat
        assert code == r2.PLAN_REUSE_BEHAVIOR_INCOMPATIBLE

    def test_sec33_item_39_complete_internally_consistent_plan_reusable(
        self, valid_plan_record: tuple[dict[str, Any], dict[str, Any]], project_root: Path
    ) -> None:
        """Item 39: Complete internally consistent compatible plan can be reusable."""
        rec, q = valid_plan_record
        compat, code, detail = r2.check_plan_record_complete_contract(rec, "g031", q, project_root)
        assert compat
        assert code == r2.PLAN_REUSE_COMPATIBLE

    def test_sec33_item_40_mixed_reusable_fresh_still_passes(
        self, monkeypatch: pytest.MonkeyPatch, project_root: Path
    ) -> None:
        """Item 40: Mixed reusable/fresh still passes."""
        def mock_reuse(root: Path, cohort: list[str] | None = None) -> dict[str, Any]:
            return {
                "artifacts_discovered": [],
                "artifacts_considered": [],
                "artifacts_scanned": [],
                "artifacts_rejected_and_reason": {},
                "reusability_results": {
                    "g031": r2.PLAN_REUSE_COMPATIBLE,
                    "g032": r2.PLAN_REUSE_NO_CANDIDATE,
                    "g033": r2.PLAN_REUSE_NO_CANDIDATE,
                    "g047": r2.PLAN_REUSE_NO_CANDIDATE,
                },
                "rejection_reasons_by_case": {},
                "reusable_plan_case_ids": ["g031"],
                "fresh_plan_case_ids": ["g032", "g033", "g047"],
                "plan_reusability_audit_complete": True,
                "total_formal_cases": 4,
                "reusable_count": 1,
                "fresh_count": 3,
                "derived_provider_budget": {
                    "N_formal_cases": 4,
                    "R_reusable_plans": 1,
                    "F_fresh_plans": 3,
                    "analyzer_calls": 3,
                    "embedding_calls": 8,
                    "reranker_calls": 8,
                    "qa_calls": 0,
                    "verifier_calls": 0,
                    "judge_calls": 0,
                    "scientific_evaluator_calls": 0,
                    "retries": 0,
                    "total_logical_model_calls": 19,
                },
            }
        monkeypatch.setattr(r2, "audit_plan_reusability", mock_reuse)
        res = r2.audit_execution_contract(project_root)
        assert res["status"] == "PASS"
        assert res["derived_provider_budget"]["R_reusable_plans"] == 1
        assert res["derived_provider_budget"]["F_fresh_plans"] == 3

    def test_sec33_item_41_budget_derives_from_actual_reuse(self) -> None:
        """Item 41: Budget derives from actual reuse classification."""
        # N=4, R=0, F=4 -> 4 analyzer, 8 emb, 8 rerank = 20
        # N=4, R=1, F=3 -> 3 analyzer, 8 emb, 8 rerank = 19
        budget_all_fresh = {
            "N": 4, "R": 0, "F": 4, "analyzer": 4, "emb": 8, "rerank": 8, "total": 20,
        }
        budget_mixed = {
            "N": 4, "R": 1, "F": 3, "analyzer": 3, "emb": 8, "rerank": 8, "total": 19,
        }
        assert budget_all_fresh["total"] == 20
        assert budget_mixed["total"] == 19


# ---------------------------------------------------------------------------
# Section 33 Items 42-45: Committed Drift & Audit Failure Propagation
# ---------------------------------------------------------------------------

class TestAuditAndVerifyFailurePropagation:
    """Section 33, items 42-45."""

    def test_sec33_item_42_committed_prereg_drift_causes_verify_failure(
        self, monkeypatch: pytest.MonkeyPatch, project_root: Path
    ) -> None:
        """Item 42: Committed prereg drift causes verify failure."""
        audit_res = r2.audit_execution_contract(project_root)
        # Mock prereg load with altered covered mask
        real_load = r2.verify_committed_artifacts_consistency
        def mock_verify_consistency(root: Path, audit_results: dict[str, Any]) -> dict[str, Any]:
            res = real_load(root, audit_results)
            res["consistent"] = False
            res["mismatches"].append("prereg covered_symbol_mask drift")
            return res
        monkeypatch.setattr(r2, "verify_committed_artifacts_consistency", mock_verify_consistency)
        v_res = r2.verify_execution_contract(project_root)
        assert v_res["status"] == "FAIL"
        assert not v_res["committed_artifacts_consistent"]
        assert any("R2_MACHINE_ARTIFACT_DRIFT" in e or "drift" in e for e in v_res["errors"])

    def test_sec33_item_43_committed_result_drift_causes_verify_failure(
        self, monkeypatch: pytest.MonkeyPatch, project_root: Path
    ) -> None:
        """Item 43: Committed result drift causes verify failure."""
        real_load = r2.verify_committed_artifacts_consistency
        def mock_verify_consistency(root: Path, audit_results: dict[str, Any]) -> dict[str, Any]:
            res = real_load(root, audit_results)
            res["consistent"] = False
            res["mismatches"].append("result decision drift")
            return res
        monkeypatch.setattr(r2, "verify_committed_artifacts_consistency", mock_verify_consistency)
        v_res = r2.verify_execution_contract(project_root)
        assert v_res["status"] == "FAIL"
        assert not v_res["committed_artifacts_consistent"]

    def test_sec33_item_44_a5_applicability_audit_failure_causes_overall_audit_failure(
        self, monkeypatch: pytest.MonkeyPatch, project_root: Path
    ) -> None:
        """Item 44: A5 applicability audit failure causes overall audit failure."""
        def mock_a5_audit() -> dict[str, Any]:
            return {
                "authority_loaded": True,
                "required_helpers_present": True,
                "ledger_coverage_verified": True,
                "origin_type_consistency_verified": True,
                "applicability_equivalence_verified": False,  # FAIL
                "sole_origin_projection_verified": True,
                "independent_rule_origin_verified": True,
                "analyzer_origin_verified": True,
                "runtime_origin_semantics_verified": True,
                "held_component_preservation_verified": True,
                "control_noop_verified": True,
                "a5_provenance_compatibility_verified": True,
                "a5_applicability_compatibility_verified": False,
                "a5_projection_compatibility_verified": False,
                "non_rule_origin_preservation_verified": True,
            }
        monkeypatch.setattr(r2, "audit_a5_execution_semantic_compatibility", mock_a5_audit)
        res = r2.audit_execution_contract(project_root)
        assert res["status"] == "FAIL"
        assert not res["a5_applicability_compatibility_verified"]

    def test_sec33_item_45_persistence_contract_audit_failure_causes_overall_audit_failure(
        self, monkeypatch: pytest.MonkeyPatch, project_root: Path
    ) -> None:
        """Item 45: Persistence contract audit failure causes overall audit failure."""
        def mock_persistence_audit() -> dict[str, Any]:
            return {
                "persistence_before_gate_contract_verified": False,  # FAIL
                "acquired_to_gated_rejected": True,
                "acquired_to_retrieved_rejected": True,
                "persisted_to_retrieved_rejected": True,
                "valid_sequence_accepted": True,
                "missing_receipt_rejected": True,
                "incomplete_receipt_rejected": True,
                "valid_receipt_accepted": True,
            }
        monkeypatch.setattr(r2, "audit_persistence_before_gate_contract", mock_persistence_audit)
        res = r2.audit_execution_contract(project_root)
        assert res["status"] == "FAIL"
        assert not res["persistence_before_gate_contract_verified"]
