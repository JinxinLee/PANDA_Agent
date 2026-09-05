"""Unit tests for D4-A4 Second-Batch Low-Risk Locator Retirement Selection & Preregistration.

Covers all 29 verification requirements from Section 29 of the authoritative specification:
1. current HEAD/config has exactly 54 rules
2. exactly 2 Batch1 structured-replacement rules
3. mechanically recover exactly 3 historical LOW_RISK candidates
4. expected candidate IDs
5. current config drift audit
6. exact retirement-mask components
7. effective_acceptance li_2026 [83,86,89] explicitly excluded from retirement
8. root_macro exact two-symbol mask
9. model_factory exact symbol + page-hint mask
10. no other rule included
11. full locator occurrence audit
12. no global-string deletion semantics
13. exact historical case recovery
14. case × rule match matrix
15. overlap-derived schedule complete
16. one prospective plan per unique case
17. paired cells share exact plan
18. downstream Analyzer=0
19. Batch1 behavior invariant across both arms
20. no Batch2 replacement by default
21. F/F not regression
22. T/F correctly classified as retirement regression
23. per-rule disposition complete
24. batch verdict truth-space complete
25. incomplete evaluator inputs cannot PASS
26. metric denominators explicit
27. protected datasets excluded
28. production activation false
29. no provider/runtime execution in D4-A4
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EVAL_SCRIPTS = _REPO_ROOT / "evaluation" / "scripts"
if str(_EVAL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_EVAL_SCRIPTS))

import d4_a4_batch2_retirement_preregistration as b2_lib


CONFIG_PATH = _REPO_ROOT / "configs" / "query_expansions.yaml"
INVENTORY_PATH = _REPO_ROOT / "evaluation" / "d4_a0_expansion_component_inventory.json"
SELECTION_PATH = _REPO_ROOT / "evaluation" / "d4_a4_batch2_low_risk_retirement_selection.json"
PREREG_PATH = _REPO_ROOT / "evaluation" / "d4_a4_batch2_retirement_preregistration.json"
GOLD_PATH = _REPO_ROOT / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml"
NOVEL_DEV_PATH = _REPO_ROOT / "evaluation" / "novel" / "v1" / "novel_dev.yaml"


@pytest.fixture(scope="module")
def config_rules() -> list[dict[str, Any]]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["rules"]


@pytest.fixture(scope="module")
def inventory_data() -> dict[str, Any]:
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def selection_data() -> dict[str, Any]:
    with open(SELECTION_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def prereg_data() -> dict[str, Any]:
    with open(PREREG_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def gold_cases() -> dict[str, Any]:
    with open(GOLD_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = data if isinstance(data, list) else data.get("questions", [])
    return {q["id"]: q for q in items}


@pytest.fixture(scope="module")
def novel_dev_cases() -> dict[str, Any]:
    with open(NOVEL_DEV_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = data if isinstance(data, list) else data.get("questions", [])
    return {q["id"]: q for q in items}


# ---------------------------------------------------------------------------
# Section 29 Requirement Tests (1 - 29)
# ---------------------------------------------------------------------------

def test_req01_current_config_has_exactly_54_rules(config_rules: list[dict[str, Any]]) -> None:
    """1. current HEAD/config has exactly 54 rules."""
    assert len(config_rules) == 54
    audit = b2_lib.audit_starting_boundary(config_rules)
    assert audit["total_rules"] == 54


def test_req02_exactly_2_batch1_structured_replacement_rules(config_rules: list[dict[str, Any]]) -> None:
    """2. exactly 2 Batch1 structured-replacement rules."""
    sr_true = [r["rule_id"] for r in config_rules if r.get("structured_replacement") is True]
    assert sorted(sr_true) == ["event_poca_handoff", "restgas_profile_workflow"]

    # Verify all other 52 rules have structured_replacement == False or None
    other_rules = [r for r in config_rules if r["rule_id"] not in sr_true]
    assert len(other_rules) == 52
    for r in other_rules:
        assert r.get("structured_replacement") in (False, None)


def test_req03_mechanically_recover_exactly_3_historical_low_risk_candidates(
    inventory_data: dict[str, Any]
) -> None:
    """3. mechanically recover exactly 3 historical LOW_RISK candidates."""
    rules = inventory_data.get("rules", [])
    low_risk = [r for r in rules if r.get("migration_readiness") == "LOW_RISK_RETIREMENT_CANDIDATE"]
    assert len(low_risk) == 3


def test_req04_expected_candidate_ids(inventory_data: dict[str, Any]) -> None:
    """4. expected candidate IDs."""
    rules = inventory_data.get("rules", [])
    low_risk_ids = sorted([
        r["rule_id"] for r in rules if r.get("migration_readiness") == "LOW_RISK_RETIREMENT_CANDIDATE"
    ])
    expected = sorted([
        "effective_acceptance_pipeline",
        "root_macro_usage",
        "model_factory_theory",
    ])
    assert low_risk_ids == expected


def test_req05_current_config_drift_audit(
    config_rules: list[dict[str, Any]], inventory_data: dict[str, Any]
) -> None:
    """5. current config drift audit."""
    drift_report = b2_lib.audit_candidate_drift(config_rules, inventory_data["rules"])
    assert drift_report["all_clean"] is True
    for cid in b2_lib.CANDIDATE_RULE_IDS:
        cand = drift_report["candidates"][cid]
        assert cand["exists"] is True
        assert cand["triggers_match"] is True
        assert cand["repositories_match"] is True
        assert cand["concepts_match"] is True
        assert cand["symbols_match"] is True
        assert cand["paper_page_hints_match"] is True
        assert cand["structured_replacement_is_false"] is True
        assert cand["material_drift"] is False
        assert cand["disposition"] == "SELECTED"


def test_req06_exact_retirement_mask_components(selection_data: dict[str, Any]) -> None:
    """6. exact retirement-mask components."""
    masks = selection_data["exact_retirement_masks"]
    assert sorted(masks.keys()) == sorted(b2_lib.CANDIDATE_RULE_IDS)
    for rid, mask in masks.items():
        assert "symbols_retired" in mask
        assert "paper_page_hints_retired" in mask
        assert "symbols_preserved" in mask
        assert "paper_page_hints_preserved" in mask
        assert "triggers_preserved" in mask
        assert "repositories_preserved" in mask
        assert "concepts_preserved" in mask
        assert mask["structured_replacement_after_retirement"] is False


def test_req07_effective_acceptance_li_2026_explicitly_excluded_from_retirement(
    selection_data: dict[str, Any]
) -> None:
    """7. effective_acceptance li_2026 [83,86,89] explicitly excluded from retirement."""
    mask = selection_data["exact_retirement_masks"]["effective_acceptance_pipeline"]
    # NOT in retired hints
    assert "li_2026" not in mask["paper_page_hints_retired"]
    # Explicitly in preserved hints
    assert mask["paper_page_hints_preserved"]["li_2026"] == [83, 86, 89]


def test_req08_root_macro_exact_two_symbol_mask(selection_data: dict[str, Any]) -> None:
    """8. root_macro exact two-symbol mask."""
    mask = selection_data["exact_retirement_masks"]["root_macro_usage"]
    expected_symbols = [
        "Running/Macros.html",
        "tools/MasterTasks/PndMasterRunSim.cxx",
    ]
    assert sorted(mask["symbols_retired"]) == sorted(expected_symbols)
    assert mask["paper_page_hints_retired"] == {}


def test_req09_model_factory_exact_symbol_plus_page_hint_mask(selection_data: dict[str, Any]) -> None:
    """9. model_factory exact symbol + page-hint mask."""
    mask = selection_data["exact_retirement_masks"]["model_factory_theory"]
    expected_symbols = [
        "model/PndLmdDPMAngModel1D.cxx",
        "model/PndLmdDPMAngModel2D.cxx",
        "model/PndLmdModelFactory.cxx",
    ]
    assert sorted(mask["symbols_retired"]) == sorted(expected_symbols)
    assert mask["paper_page_hints_retired"] == {"pflueger_2017": [51, 57, 65]}


def test_req10_no_other_rule_included(selection_data: dict[str, Any], prereg_data: dict[str, Any]) -> None:
    """10. no other rule included."""
    assert sorted(selection_data["selected_batch2_rules"]) == sorted(b2_lib.CANDIDATE_RULE_IDS)
    assert sorted(prereg_data["exact_selected_rules"]) == sorted(b2_lib.CANDIDATE_RULE_IDS)
    assert len(selection_data["held_candidate_rules_and_reasons"]) == 0


def test_req11_full_locator_occurrence_audit(config_rules: list[dict[str, Any]]) -> None:
    """11. full locator occurrence audit."""
    symbols = [
        "macro/target/prod_sim_hvmaps.C",
        "data/PndLmdAcceptance.cxx",
        "model/PndLmdModelFactory.cxx",
        "Running/Macros.html",
        "tools/MasterTasks/PndMasterRunSim.cxx",
        "model/PndLmdDPMAngModel1D.cxx",
        "model/PndLmdDPMAngModel2D.cxx",
    ]
    hints = [
        ("pflueger_2017", (51, 57, 65)),
        ("li_2026", (83, 86, 89)),
    ]
    audit = b2_lib.audit_component_occurrences(config_rules, symbols, hints)
    assert len(audit["symbols"]) == len(symbols)
    assert len(audit["paper_page_hints"]) == len(hints)
    # Check that multi-rule occurrences are documented
    assert audit["symbols"]["macro/target/prod_sim_hvmaps.C"]["total_occurrences"] == 7
    assert audit["symbols"]["model/PndLmdModelFactory.cxx"]["total_occurrences"] == 9
    assert audit["symbols"]["data/PndLmdAcceptance.cxx"]["total_occurrences"] == 5


def test_req12_no_global_string_deletion_semantics() -> None:
    """12. no global-string deletion semantics."""
    # Test provenance subtraction: item with multi-source provenance survives
    item_multi = {
        "locator_path": "macro/target/prod_sim_hvmaps.C",
        "provenance_origin_ids": ["effective_acceptance_pipeline", "reconstructed_profile_to_acceptance"],
    }
    projected = b2_lib.subtract_batch2_provenance([item_multi], ["effective_acceptance_pipeline"])
    assert len(projected) == 1
    assert projected[0]["provenance_origin_ids"] == ["reconstructed_profile_to_acceptance"]

    # Item with sole provenance from retired candidate is subtracted
    item_sole = {
        "locator_path": "Running/Macros.html",
        "provenance_origin_ids": ["root_macro_usage"],
    }
    projected_sole = b2_lib.subtract_batch2_provenance([item_sole], ["root_macro_usage"])
    assert len(projected_sole) == 0


def test_req13_exact_historical_case_recovery(
    gold_cases: dict[str, Any], novel_dev_cases: dict[str, Any]
) -> None:
    """13. exact historical case recovery."""
    all_7 = b2_lib.ALL_7_HISTORICAL_CASES
    assert len(all_7) == 7
    for cid in all_7:
        assert cid in gold_cases or cid in novel_dev_cases

    # Gold dev cases
    assert set(b2_lib.ALL_7_HISTORICAL_CASES).intersection(gold_cases.keys()) == {"g052", "g055", "g007", "g060"}
    # Novel dev cases
    assert set(b2_lib.ALL_7_HISTORICAL_CASES).intersection(novel_dev_cases.keys()) == {"n003", "n004", "n014"}


def test_req14_case_by_rule_match_matrix(
    config_rules: list[dict[str, Any]],
    gold_cases: dict[str, Any],
    novel_dev_cases: dict[str, Any],
) -> None:
    """14. case × rule match matrix."""
    for cid in b2_lib.ALL_7_HISTORICAL_CASES:
        item = gold_cases.get(cid) or novel_dev_cases.get(cid)
        assert item is not None
        matches = b2_lib.compute_deterministic_rule_matches(item["query"], config_rules)
        b2_matches = [r for r in matches if r in b2_lib.CANDIDATE_RULE_IDS]
        # No case matches more than one Batch-2 candidate rule
        assert len(b2_matches) <= 1
        if cid == "g052":
            assert "effective_acceptance_pipeline" in b2_matches
        elif cid == "n004":
            assert "root_macro_usage" in b2_matches
        elif cid == "n014":
            assert "model_factory_theory" in b2_matches
        else:
            assert len(b2_matches) == 0


def test_req15_overlap_derived_schedule_complete(prereg_data: dict[str, Any]) -> None:
    """15. overlap-derived schedule complete."""
    schedule = prereg_data["exact_paired_cell_schedule"]
    assert len(schedule) == 14  # 7 cases × 2 arms
    case_ids_in_sched = {c["case_id"] for c in schedule}
    assert case_ids_in_sched == set(b2_lib.ALL_7_HISTORICAL_CASES)


def test_req16_one_prospective_plan_per_unique_case(prereg_data: dict[str, Any]) -> None:
    """16. one prospective plan per unique case."""
    acq = prereg_data["prospective_one_plan_per_case_acquisition"]
    assert acq["strategy"] == "ONE_PROSPECTIVE_PLAN_PER_UNIQUE_CASE"
    assert acq["phase_p_analyzer_calls"] == 7
    assert acq["downstream_phase_r_analyzer_calls"] == 0
    assert prereg_data["total_prospective_plans"] == 7


def test_req17_paired_cells_share_exact_plan(prereg_data: dict[str, Any]) -> None:
    """17. paired cells share exact plan."""
    assert prereg_data["prospective_one_plan_per_case_acquisition"]["shared_canonical_plan_equality_required"] is True


def test_req18_downstream_analyzer_zero(prereg_data: dict[str, Any]) -> None:
    """18. downstream Analyzer=0."""
    calls = prereg_data["future_call_accounting_expectations"]
    assert calls["analyzer_phase_r"] == 0


def test_req19_batch1_behavior_invariant_across_both_arms(prereg_data: dict[str, Any]) -> None:
    """19. Batch1 behavior invariant across both arms."""
    arms = prereg_data["arm_definitions"]
    assert arms["CURRENT_COMPAT"]["batch1_production_active"] is True
    assert arms["BATCH2_RETIREMENT"]["batch1_production_active"] is True
    assert arms["CURRENT_COMPAT"]["selectivity_v2_active"] is True
    assert arms["BATCH2_RETIREMENT"]["selectivity_v2_active"] is True
    assert arms["CURRENT_COMPAT"]["admission_k"] == arms["BATCH2_RETIREMENT"]["admission_k"] == 3
    assert arms["CURRENT_COMPAT"]["rerank_pool_size"] == arms["BATCH2_RETIREMENT"]["rerank_pool_size"] == 30


def test_req20_no_batch2_replacement_by_default(prereg_data: dict[str, Any]) -> None:
    """20. no Batch2 replacement by default."""
    arms = prereg_data["arm_definitions"]
    assert arms["BATCH2_RETIREMENT"]["batch2_structured_replacement"] is False
    for mask in prereg_data["exact_component_masks"].values():
        assert mask["structured_replacement_after_retirement"] is False


def test_req21_ff_not_regression() -> None:
    """21. F/F not regression."""
    # Verified in phenotype dictionary
    assert b2_lib.PAIR_PHENOTYPES["PAIR_UNRESOLVED_BOTH"] == "F/F"
    # A case where before=False and after=False is unresolved baseline omission, not regression


def test_req22_tf_correctly_classified_as_retirement_regression() -> None:
    """22. T/F correctly classified as retirement regression."""
    assert b2_lib.PAIR_PHENOTYPES["PAIR_RETIREMENT_REGRESSION"] == "T/F"


def test_req23_per_rule_disposition_complete() -> None:
    """23. per-rule disposition complete."""
    expected_dispositions = {
        "RETIREMENT_VALIDATED",
        "DEPENDENCY_OBSERVED_RETAIN",
        "INCONCLUSIVE_BASELINE_NOT_REPRODUCED",
        "INVALID_PROTOCOL",
    }
    assert set(b2_lib.PER_RULE_DISPOSITIONS) == expected_dispositions


def _complete_inputs():
    return dict(execution_valid=True, protocol_violation=False, missing_inputs=False,
                plan_equality_all_verified=True, analyzer_provider_calls_downstream=0,
                reference_baseline_valid=True,
                per_rule_dispositions={r: "RETIREMENT_VALIDATED" for r in b2_lib.CANDIDATE_RULE_IDS},
                critical_retirement_regressions=0, grounding_regressions=0,
                wrong_version_regressions=0, invalid_provenance_recoveries=0,
                metric_deltas={k: 0.0 for k in b2_lib.DEFAULT_METRIC_BOUNDED_TOLERANCES})


def _complete_verdict(**overrides):
    values = _complete_inputs()
    if "metric_deltas" in overrides:
        values["metric_deltas"].update(overrides.pop("metric_deltas"))
    values.update(overrides)
    return b2_lib.evaluate_batch2_verdict(**values)


def test_req24_batch_verdict_truth_space_complete() -> None:
    """24. batch verdict truth-space complete."""
    clean_dispositions = {
        "effective_acceptance_pipeline": "RETIREMENT_VALIDATED",
        "root_macro_usage": "RETIREMENT_VALIDATED",
        "model_factory_theory": "RETIREMENT_VALIDATED",
    }
    # Level 6 PASS
    res = _complete_verdict(per_rule_dispositions=clean_dispositions)
    assert res["verdict_level"] == 6
    assert res["verdict_status"] == "PASS"

    # Level 5 PARTIAL (aggregate metric delta violation)
    res5 = _complete_verdict(
        per_rule_dispositions=clean_dispositions,
        metric_deltas={"recall_at_5": -0.06},
    )
    assert res5["verdict_level"] == 5
    assert res5["verdict_status"] == "PARTIAL"

    # Level 4 FAIL (critical regression)
    res4 = _complete_verdict(
        per_rule_dispositions=clean_dispositions,
        critical_retirement_regressions=1,
    )
    assert res4["verdict_level"] == 4
    assert res4["verdict_status"] == "FAIL"

    # Level 3 PARTIAL (some rules retain dependency, NO safety violation)
    mixed_dispositions = {
        "effective_acceptance_pipeline": "RETIREMENT_VALIDATED",
        "root_macro_usage": "DEPENDENCY_OBSERVED_RETAIN",
        "model_factory_theory": "RETIREMENT_VALIDATED",
    }
    res3 = _complete_verdict(per_rule_dispositions=mixed_dispositions)
    assert res3["verdict_level"] == 3
    assert res3["verdict_status"] == "PARTIAL"

    # Level 4 FAIL when safety failure combined with partial dependency
    res4_comb = _complete_verdict(
        per_rule_dispositions=mixed_dispositions,
        critical_retirement_regressions=1,
    )
    assert res4_comb["verdict_level"] == 4
    assert res4_comb["verdict_status"] == "FAIL"

    # Level 2 INCONCLUSIVE (baseline not reproduced)
    res2 = _complete_verdict(
        reference_baseline_valid=False,
        per_rule_dispositions=clean_dispositions,
    )
    assert res2["verdict_level"] == 2
    assert res2["verdict_status"] == "INCONCLUSIVE"


def test_req25_incomplete_evaluator_inputs_cannot_pass() -> None:
    """25. incomplete evaluator inputs cannot PASS."""
    # missing inputs
    res_missing = b2_lib.evaluate_batch2_verdict(missing_inputs=True)
    assert res_missing["verdict_level"] == 1
    assert res_missing["verdict_status"] == "INVALID"

    # None dispositions
    res_none_disp = b2_lib.evaluate_batch2_verdict(per_rule_dispositions=None)
    assert res_none_disp["verdict_level"] == 1
    assert res_none_disp["verdict_status"] == "INVALID"

    # empty dispositions
    res_empty_disp = b2_lib.evaluate_batch2_verdict(per_rule_dispositions={})
    assert res_empty_disp["verdict_level"] == 1
    assert res_empty_disp["verdict_status"] == "INVALID"

    # execution_valid = False
    res_exec = b2_lib.evaluate_batch2_verdict(execution_valid=False)
    assert res_exec["verdict_level"] == 1
    assert res_exec["verdict_status"] == "INVALID"

    # shared plan inequality
    res_ineq = b2_lib.evaluate_batch2_verdict(plan_equality_all_verified=False)
    assert res_ineq["verdict_level"] == 1
    assert res_ineq["verdict_status"] == "INVALID"

    # downstream Analyzer call > 0
    res_analyzer = b2_lib.evaluate_batch2_verdict(analyzer_provider_calls_downstream=1)
    assert res_analyzer["verdict_level"] == 1
    assert res_analyzer["verdict_status"] == "INVALID"


def test_req26_metric_denominators_explicit(selection_data: dict[str, Any], prereg_data: dict[str, Any]) -> None:
    """26. metric denominators explicit."""
    denoms = prereg_data["evidence_group_applicability_and_denominators"]
    assert denoms["total_cases"] == 7
    assert denoms["answered_case_count"] == 6
    assert denoms["negative_control_case_count"] == 1
    assert denoms["case_macro_denominator"] == 6
    assert denoms["micro_evidence_group_denominator"] == 11
    assert denoms["total_required_evidence_groups"] == 12
    assert denoms["total_critical_evidence_groups"] == 12


def test_req27_protected_datasets_excluded(prereg_data: dict[str, Any]) -> None:
    """27. protected datasets excluded."""
    boundary = prereg_data["protected_data_boundary"]
    assert boundary["novel_validation_access"] is False
    assert boundary["novel_holdout_access"] is False


def test_req28_production_activation_false(selection_data: dict[str, Any], prereg_data: dict[str, Any]) -> None:
    """28. production activation false."""
    assert prereg_data["production_activation"] is False
    for mask in selection_data["exact_retirement_masks"].values():
        assert mask["structured_replacement_after_retirement"] is False


def test_req29_no_provider_runtime_execution_in_d4_a4(
    selection_data: dict[str, Any], prereg_data: dict[str, Any]
) -> None:
    """29. no provider/runtime execution in D4-A4."""
    accounting = selection_data["zero_provider_accounting"]
    assert accounting["analyzer_calls"] == 0
    assert accounting["embedding_calls"] == 0
    assert accounting["reranker_calls"] == 0
    assert accounting["qa_calls"] == 0
    assert accounting["verifier_calls"] == 0
    assert accounting["judge_calls"] == 0
    assert accounting["db_writes"] == 0
    assert accounting["qdrant_writes"] == 0
    assert accounting["retrieval_runs"] == 0
    assert accounting["benchmark_runs"] == 0
    assert accounting["novel_runs"] == 0
    assert accounting["protected_dataset_access"] == 0

    prereg_accounting = prereg_data["d4_a4_zero_provider_accounting"]
    assert prereg_accounting["analyzer_calls"] == 0
    assert prereg_accounting["embedding_calls"] == 0
    assert prereg_accounting["reranker_calls"] == 0
    assert prereg_accounting["retrieval_runs"] == 0


def test_every_required_input_is_required():
    complete = _complete_inputs()
    for key in complete:
        missing = dict(complete)
        del missing[key]
        assert b2_lib.evaluate_batch2_verdict(**missing)["verdict_level"] == 1, key
    for key in b2_lib.DEFAULT_METRIC_BOUNDED_TOLERANCES:
        values = _complete_inputs()
        del values["metric_deltas"][key]
        assert b2_lib.evaluate_batch2_verdict(**values)["verdict_level"] == 1
    for rule in b2_lib.CANDIDATE_RULE_IDS:
        values = _complete_inputs()
        del values["per_rule_dispositions"][rule]
        assert b2_lib.evaluate_batch2_verdict(**values)["verdict_level"] == 1
    for invalid in (float("nan"), float("inf"), None, "0", True):
        values = _complete_inputs()
        values["metric_deltas"]["recall_at_5"] = invalid
        assert b2_lib.evaluate_batch2_verdict(**values)["verdict_level"] == 1
    values = _complete_inputs()
    values["per_rule_dispositions"]["root_macro_usage"] = "UNKNOWN"
    assert b2_lib.evaluate_batch2_verdict(**values)["verdict_level"] == 1


def test_exhaustive_meaningful_batch_truth_space():
    from itertools import product
    for dispositions in product(b2_lib.PER_RULE_DISPOSITIONS, repeat=3):
        for valid, baseline, safety, aggregate in product((False, True), repeat=4):
            values = _complete_inputs()
            values.update(execution_valid=valid, reference_baseline_valid=baseline,
                          per_rule_dispositions=dict(zip(b2_lib.CANDIDATE_RULE_IDS, dispositions)),
                          critical_retirement_regressions=int(safety))
            values["metric_deltas"]["recall_at_5"] = -0.06 if aggregate else 0.0
            if not valid or "INVALID_PROTOCOL" in dispositions:
                expected = 1
            elif not baseline or "INCONCLUSIVE_BASELINE_NOT_REPRODUCED" in dispositions:
                expected = 2
            elif safety:
                expected = 4
            elif "DEPENDENCY_OBSERVED_RETAIN" in dispositions:
                expected = 3
            elif aggregate:
                expected = 5
            else:
                expected = 6
            assert b2_lib.evaluate_batch2_verdict(**values)["verdict_level"] == expected
    for name in ("critical_retirement_regressions", "grounding_regressions",
                 "wrong_version_regressions", "invalid_provenance_recoveries"):
        assert _complete_verdict(**{name: 1})["verdict_level"] == 4


def test_pair_and_rule_truth_spaces():
    from itertools import product
    for before, after in product((False, True), repeat=2):
        phenotype = b2_lib.classify_pair(before, after)
        assert (phenotype == "PAIR_RETIREMENT_REGRESSION") == (before and not after)
    for valid, baseline, loss in product((False, True), repeat=3):
        expected = ("INVALID_PROTOCOL" if not valid else "DEPENDENCY_OBSERVED_RETAIN" if loss
                    else "RETIREMENT_VALIDATED" if baseline else "INCONCLUSIVE_BASELINE_NOT_REPRODUCED")
        assert b2_lib.classify_rule(protocol_valid=valid, baseline_reproduced=baseline,
                                   attributable_loss=loss) == expected


def test_subtraction_respects_each_origins_own_component_mask():
    masks = {"retiring": {"symbols_retired": ["shared/path"]}, "preserving": {"symbols_retired": []}}
    original = [{"path": "shared/path", "provenance_origin_ids": ["retiring", "preserving"]}]
    projected = b2_lib.subtract_batch2_provenance(original, ["retiring", "preserving"], masks)
    assert projected == [{"path": "shared/path", "provenance_origin_ids": ["preserving"]}]
    assert original[0]["provenance_origin_ids"] == ["retiring", "preserving"]
    with pytest.raises(ValueError):
        b2_lib.subtract_batch2_provenance([{"path": "shared/path"}], ["retiring"], masks)


def test_schedule_matches_current_rule_applicability(selection_data, prereg_data):
    from collections import defaultdict
    pairs = defaultdict(list)
    for cell in prereg_data["exact_paired_cell_schedule"]:
        pairs[cell["case_id"]].append(cell)
        matched = selection_data["deterministic_match_matrix"][cell["case_id"]]["batch2_matched_rules"]
        expected = matched if cell["arm"] == "BATCH2_RETIREMENT" else []
        assert cell["retirement_rule_ids"] == expected
        assert cell["batch2_retirement_mask_applied"] == bool(expected)
        assert cell["expected_model_calls"] == {"analyzer": 0, "embedding": 1, "reranker": 1}
    assert set(pairs) == set(prereg_data["exact_case_cohort"])
    for cells in pairs.values():
        assert len(cells) == 2
        assert {c["arm"] for c in cells} == {"CURRENT_COMPAT", "BATCH2_RETIREMENT"}
        assert len({c["canonical_plan_id"] for c in cells}) == 1
    assert sum(c["batch2_retirement_mask_applied"] for cells in pairs.values() for c in cells) == 3
    assert 7 + sum(sum(c["expected_model_calls"].values()) for cells in pairs.values() for c in cells) == 35


def test_every_page_overlap_is_recorded(config_rules, selection_data):
    for hint in selection_data["component_occurrence_overlap_audit"]["paper_page_hints"].values():
        for page in hint["pages"]:
            expected = [r["rule_id"] for r in config_rules
                        if page in r.get("paper_page_hints", {}).get(hint["paper"], [])]
            assert hint["page_occurrences"][str(page)] == expected
    actual = b2_lib.audit_component_occurrences(config_rules, [], [("pflueger_2017", [51, 57, 65])])
    assert "angular_acceptance" in actual["paper_page_hints"]["pflueger_2017: [51, 57, 65]"]["page_occurrences"]["57"]


def test_denominators_and_matching_derive_from_approved_data(gold_cases, novel_dev_cases, prereg_data, selection_data, config_rules):
    from panda_agent.config import QueryExpansionRule
    from panda_agent.d3_structured import select_matching_query_expansions
    questions = {**gold_cases, **novel_dev_cases}
    groups = 0
    answered = []
    for cid in prereg_data["exact_case_cohort"]:
        question = questions[cid]
        assert question["split"] in ("dev", "novel_dev")
        expected_groups = [(g["group_id"], g["critical"]) for g in question["required_evidence_groups"]]
        recorded = prereg_data["evidence_group_applicability_and_denominators"]["evidence_group_details"][cid]
        assert [(g["group_id"], g["critical"]) for g in recorded] == expected_groups
        if question["expected_status"] == "answered":
            answered.append(cid)
            groups += len(expected_groups)
        production_matches = select_matching_query_expansions(
            question["query"], [QueryExpansionRule(**r) for r in config_rules], None)
        assert [r.rule_id for r in production_matches.active_matching_rules] == selection_data["deterministic_match_matrix"][cid]["matched_rules_total"]
    assert answered == prereg_data["evidence_group_applicability_and_denominators"]["answered_cases"]
    assert groups == 11
