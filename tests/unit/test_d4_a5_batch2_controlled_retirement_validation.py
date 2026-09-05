"""Unit tests for D4-A5 Second-Batch Low-Risk Locator Controlled Retirement Validation.

Focused pre-exposure tests (frozen before any scientific provider call).
Tests use synthetic fixtures and the frozen D4-A4 contract module; they never
encode the expected observed scientific outcome of g052/n004/n014 and never
invoke providers, databases, or protected datasets.

Covered verification requirements (task Section 14, items 1-40):
 1-5   frozen cohort, rules, masks, page-hint preservation, control masks
 6-7   multi-origin survival / sole-origin removal projections
 8-12  canonical immutability, plan-inequality, missing/ambiguous provenance,
       non-mask projection drift -> INVALID
 13-15 Batch-1 runtime invariance, g052 Batch-1 activation retention,
       no Batch-2 structured replacement
 16-19 pair phenotypes (F/F, F/T, T/F, T/T)
 20-24 per-rule disposition precedence
 25-30 batch verdict levels 1-6
 31-35 metric completeness, MRR diagnostic-only, negative-control exclusion,
       macro denominator 6, answered group count 11
 36    active per-rule groups
 37    evaluator performs no provider calls (synthetic end-to-end with
       provider construction forbidden)
 38    production files never mutated by treatment construction
 39    no benchmark/case -> expected locator shortcut in projections
 40    no protected dataset access
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EVAL_SCRIPTS = _REPO_ROOT / "evaluation" / "scripts"
for _p in (str(_EVAL_SCRIPTS), str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import d4_a4_batch2_retirement_preregistration as b2
import d4_a5_batch2_controlled_retirement_validation as a5
from panda_agent.evaluation import GoldDataset, GoldQuestion, load_gold_dataset


PREREG = json.loads(
    (_REPO_ROOT / "evaluation" / "d4_a4_batch2_retirement_preregistration.json").read_text(
        encoding="utf-8"
    )
)
SELECTION = json.loads(
    (_REPO_ROOT / "evaluation" / "d4_a4_batch2_low_risk_retirement_selection.json").read_text(
        encoding="utf-8"
    )
)


def _rules_by_id() -> dict[str, dict[str, Any]]:
    from panda_agent.config import load_query_expansions

    qe = load_query_expansions(_REPO_ROOT / "configs" / "query_expansions.yaml")
    return {r["rule_id"]: r for r in qe.model_dump(mode="python")["rules"]}


def _synthetic_canonical_plan(matched_rules: list[str], symbols: list[str],
                              hints: dict[str, list[int]] | None = None) -> dict[str, Any]:
    return {
        "intent": "algorithm_theory",
        "secondary_intents": [],
        "routing_method": "rule",
        "target_repositories": ["luminosityfit"],
        "resolved_versions": {"luminosityfit": "deadbeef" * 5},
        "version_conflicts": [],
        "concepts": ["synthetic concept"],
        "symbols": list(symbols),
        "concept_scopes": {},
        "source_budgets": {"code": 0.6, "paper": 0.4},
        "required_source_types": ["paper"],
        "resolved_aliases": {},
        "premise_corrections": [],
        "paper_page_hints": hints or {},
        "analysis_diagnostics": {
            "matched_expansion_rules": list(matched_rules),
            "structured_replacement_rules": (
                ["restgas_profile_workflow"] if "restgas_profile_workflow" in matched_rules else []
            ),
            "analyzer_accepted_semantic_delta": {
                "symbols": [],
                "concepts": [{"value": "synthetic concept", "support_spans": [0]}],
            },
        },
    }


def _full_mask_symbols(rule_id: str) -> list[str]:
    return list(b2.FROZEN_RETIREMENT_MASKS[rule_id]["symbols_retired"])


# ---------------------------------------------------------------------------
# 1-5: frozen cohort, rules, masks, page-hint preservation, control masks
# ---------------------------------------------------------------------------


def test_01_exact_seven_case_order():
    assert a5.CASE_ORDER == ["g052", "g055", "n003", "n004", "g007", "n014", "g060"]
    assert a5.CASE_ORDER == PREREG["exact_case_cohort"]
    assert [p["case_id"] for p in a5.SCHEDULE_14 and []] == []


def test_01b_schedule_is_exact_frozen_14_cell_order():
    expected = [
        ("g052", "CURRENT_COMPAT"), ("g052", "BATCH2_RETIREMENT"),
        ("g055", "CURRENT_COMPAT"), ("g055", "BATCH2_RETIREMENT"),
        ("n003", "CURRENT_COMPAT"), ("n003", "BATCH2_RETIREMENT"),
        ("n004", "CURRENT_COMPAT"), ("n004", "BATCH2_RETIREMENT"),
        ("g007", "CURRENT_COMPAT"), ("g007", "BATCH2_RETIREMENT"),
        ("n014", "CURRENT_COMPAT"), ("n014", "BATCH2_RETIREMENT"),
        ("g060", "CURRENT_COMPAT"), ("g060", "BATCH2_RETIREMENT"),
    ]
    observed = [(c["case_id"], c["arm"]) for c in a5.SCHEDULE_14]
    assert observed == expected
    assert [c["cell_index"] for c in a5.SCHEDULE_14] == list(range(1, 15))
    prereg_cells = [
        (c["case_id"], c["arm"]) for c in PREREG["exact_paired_cell_schedule"]
    ]
    assert observed == prereg_cells


def test_02_exact_three_selected_rules():
    assert a5.SCHEDULE_14 is not None
    assert list(b2.CANDIDATE_RULE_IDS) == [
        "effective_acceptance_pipeline", "root_macro_usage", "model_factory_theory",
    ]
    assert PREREG["exact_selected_rules"] == list(b2.CANDIDATE_RULE_IDS)
    assert a5.build_initial_manifest(_REPO_ROOT)["exact_selected_rules"] == list(b2.CANDIDATE_RULE_IDS)


def test_03_exact_masks_match_frozen_d4_a4_contract():
    assert a5.b2.FROZEN_RETIREMENT_MASKS == b2.FROZEN_RETIREMENT_MASKS
    for rid, mask in b2.FROZEN_RETIREMENT_MASKS.items():
        prereg_mask = PREREG["exact_component_masks"][rid]
        shared = {k: v for k, v in prereg_mask.items() if k in mask}
        assert mask == shared
        assert prereg_mask["retirement_rationale"]
    # Exact mask content
    assert b2.FROZEN_RETIREMENT_MASKS["effective_acceptance_pipeline"]["symbols_retired"] == [
        "macro/target/prod_sim_hvmaps.C",
        "data/PndLmdAcceptance.cxx",
        "model/PndLmdModelFactory.cxx",
    ]
    assert b2.FROZEN_RETIREMENT_MASKS["root_macro_usage"]["symbols_retired"] == [
        "Running/Macros.html", "tools/MasterTasks/PndMasterRunSim.cxx",
    ]
    assert b2.FROZEN_RETIREMENT_MASKS["model_factory_theory"]["symbols_retired"] == [
        "model/PndLmdDPMAngModel1D.cxx",
        "model/PndLmdDPMAngModel2D.cxx",
        "model/PndLmdModelFactory.cxx",
    ]
    assert b2.FROZEN_RETIREMENT_MASKS["model_factory_theory"]["paper_page_hints_retired"] == {
        "pflueger_2017": [51, 57, 65],
    }


def test_04_effective_acceptance_page_hints_83_86_89_preserved():
    mask = b2.FROZEN_RETIREMENT_MASKS["effective_acceptance_pipeline"]
    assert mask["paper_page_hints_retired"] == {}
    assert mask["paper_page_hints_preserved"] == {"li_2026": [83, 86, 89]}
    # The preserved hints never appear in any mask entry.
    entries = a5.build_batch2_mask_entries(
        "g052", ["effective_acceptance_pipeline"]
    )
    assert all(not (e["source_id"] == "li_2026") for e in entries)
    assert all(e["kind"] == "symbol" for e in entries)


def test_05_four_control_cases_receive_empty_retirement_masks():
    for cid in ("g055", "n003", "g007", "g060"):
        attribution = a5.CASE_ATTRIBUTION[cid]
        assert attribution["matched_retirement_rules"] == []
        assert a5.build_batch2_mask_entries(cid, []) == []
        assert a5.SCHEDULE_14 is not None
    mask_cells = [c for c in a5.SCHEDULE_14 if c["batch2_retirement_mask_applied"]]
    assert [(c["case_id"], c["retirement_rule_ids"]) for c in mask_cells] == [
        ("g052", ["effective_acceptance_pipeline"]),
        ("n004", ["root_macro_usage"]),
        ("n014", ["model_factory_theory"]),
    ]


def test_05b_masks_derived_only_from_frozen_d4_a4_module():
    for cid in a5.CASE_ORDER:
        matched = a5.CASE_ATTRIBUTION[cid]["matched_retirement_rules"]
        entries = a5.build_batch2_mask_entries(cid, matched)
        for entry in entries:
            frozen = b2.FROZEN_RETIREMENT_MASKS[entry["rule_id"]]
            if entry["kind"] == "symbol":
                assert entry["value"] in frozen["symbols_retired"]
            else:
                assert entry["pdf_page"] in frozen["paper_page_hints_retired"][entry["source_id"]]


# ---------------------------------------------------------------------------
# 6-12: ledger and projection semantics
# ---------------------------------------------------------------------------


def _ledger_for(plan: dict[str, Any], matched: list[str]) -> list[dict[str, Any]]:
    return a5.build_contribution_ledger(plan, _rules_by_id(), matched)


def test_06_multi_origin_locator_survives_when_one_origin_retired():
    plan = _synthetic_canonical_plan(
        matched_rules=["effective_acceptance_pipeline"],
        symbols=["macro/target/prod_sim_hvmaps.C", "data/PndLmdAcceptance.cxx",
                 "model/PndLmdModelFactory.cxx"],
    )
    # Give the first symbol an additional independent origin via the analyzer delta.
    plan["analysis_diagnostics"]["analyzer_accepted_semantic_delta"] = {
        "symbols": [{"value": "macro/target/prod_sim_hvmaps.C", "support_spans": [1]}],
        "concepts": [],
    }
    ledger = _ledger_for(plan, ["effective_acceptance_pipeline"])
    mask_entries = a5.build_batch2_mask_entries("g052", ["effective_acceptance_pipeline"])
    projected, receipts = a5.build_retirement_projection(
        plan, ledger, mask_entries, ["effective_acceptance_pipeline"]
    )
    assert "macro/target/prod_sim_hvmaps.C" in projected["symbols"]
    assert set(receipts["effective_removed_symbols"]) == {
        "data/PndLmdAcceptance.cxx", "model/PndLmdModelFactory.cxx",
    }
    survivor = next(
        e for e in receipts["surviving_independent_origin_entries"]
        if e["value"] == "macro/target/prod_sim_hvmaps.C"
    )
    assert a5.ORIGIN_ACCEPTED_ANALYZER_DELTA in survivor["surviving_independent_origins"]


def test_06b_multi_origin_via_second_rule_survives():
    # Synthetic second rule contributing the same symbol, both rules matched.
    plan = _synthetic_canonical_plan(
        matched_rules=["effective_acceptance_pipeline", "restgas_profile_workflow"],
        symbols=["macro/target/prod_sim_hvmaps.C", "data/PndLmdAcceptance.cxx",
                 "model/PndLmdModelFactory.cxx"],
    )
    rules = _rules_by_id()
    rules["synthetic_second_rule"] = {
        "rule_id": "synthetic_second_rule",
        "triggers": ["synthetic"],
        "repositories": [],
        "symbols": ["macro/target/prod_sim_hvmaps.C"],
        "concepts": [],
        "paper_page_hints": {},
    }
    matched = ["effective_acceptance_pipeline", "synthetic_second_rule"]
    ledger = a5.build_contribution_ledger(plan, rules, matched)
    mask_entries = a5.build_batch2_mask_entries("g052", ["effective_acceptance_pipeline"])
    projected, receipts = a5.build_retirement_projection(
        plan, ledger, mask_entries, ["effective_acceptance_pipeline"]
    )
    assert "macro/target/prod_sim_hvmaps.C" in projected["symbols"]
    survivor = next(
        e for e in receipts["surviving_independent_origin_entries"]
        if e["value"] == "macro/target/prod_sim_hvmaps.C"
    )
    assert survivor["surviving_independent_origins"] == ["synthetic_second_rule"]
    # The other two symbols are sole-origin and must be removed.
    assert set(receipts["effective_removed_symbols"]) == {
        "data/PndLmdAcceptance.cxx", "model/PndLmdModelFactory.cxx",
    }


def test_07_sole_selected_rule_origin_is_removed():
    plan = _synthetic_canonical_plan(
        matched_rules=["model_factory_theory"],
        symbols=_full_mask_symbols("model_factory_theory"),
        hints={"pflueger_2017": [51, 57, 65]},
    )
    ledger = _ledger_for(plan, ["model_factory_theory"])
    mask_entries = a5.build_batch2_mask_entries("n014", ["model_factory_theory"])
    projected, receipts = a5.build_retirement_projection(
        plan, ledger, mask_entries, ["model_factory_theory"]
    )
    assert projected["symbols"] == []
    assert projected["paper_page_hints"] == {}
    assert set(receipts["effective_removed_symbols"]) == set(_full_mask_symbols("model_factory_theory"))
    assert receipts["effective_removed_paper_page_hints"] == {"pflueger_2017": [51, 57, 65]}
    assert receipts["effective_removal_count"] == 6


def test_07b_page_hint_partial_survival_via_second_rule():
    plan = _synthetic_canonical_plan(
        matched_rules=["model_factory_theory"],
        symbols=_full_mask_symbols("model_factory_theory"),
        hints={"pflueger_2017": [51, 57, 65]},
    )
    rules = _rules_by_id()
    rules["synthetic_hint_rule"] = {
        "rule_id": "synthetic_hint_rule",
        "triggers": ["synthetic"],
        "repositories": [],
        "symbols": [],
        "concepts": [],
        "paper_page_hints": {"pflueger_2017": [57]},
    }
    matched = ["model_factory_theory", "synthetic_hint_rule"]
    ledger = a5.build_contribution_ledger(plan, rules, matched)
    mask_entries = a5.build_batch2_mask_entries("n014", ["model_factory_theory"])
    projected, receipts = a5.build_retirement_projection(
        plan, ledger, mask_entries, ["model_factory_theory"]
    )
    assert projected["paper_page_hints"]["pflueger_2017"] == [57]
    assert receipts["effective_removed_paper_page_hints"] == {"pflueger_2017": [51, 65]}


def test_08_canonical_plan_remains_unchanged_across_arms():
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"],
        symbols=_full_mask_symbols("root_macro_usage"),
    )
    snapshot = copy.deepcopy(plan)
    ledger = _ledger_for(plan, ["root_macro_usage"])
    mask_entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    projected, receipts = a5.build_retirement_projection(
        plan, ledger, mask_entries, ["root_macro_usage"]
    )
    assert plan == snapshot
    assert projected != plan
    assert receipts["canonical_plan_unchanged"] is True
    # CURRENT_COMPAT projection is a deep copy equal to canonical.
    current_compat = copy.deepcopy(plan)
    assert current_compat == plan


def test_09_plan_inequality_is_detected():
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"], symbols=["Running/Macros.html"],
    )
    drifted = copy.deepcopy(plan)
    drifted["concepts"] = ["unexpected extra concept"]
    ok, error = a5.verify_projection_diff(
        plan, drifted,
        {"effective_removed_symbols": [], "effective_removed_paper_page_hints": {}},
    )
    assert ok is False
    assert error is not None


def test_10_missing_provenance_is_invalid():
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"], symbols=["Running/Macros.html"],
    )
    ledger = _ledger_for(plan, ["root_macro_usage"])
    # Remove the masked contribution from the ledger entirely.
    ledger = [e for e in ledger if e["value"] != "Running/Macros.html"]
    mask_entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    with pytest.raises(ValueError, match="not identified in canonical plan ledger"):
        a5.build_retirement_projection(plan, ledger, mask_entries, ["root_macro_usage"])


def test_11_ambiguous_provenance_is_invalid():
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"], symbols=["Running/Macros.html"],
    )
    ledger = _ledger_for(plan, ["root_macro_usage"])
    for entry in ledger:
        if entry["value"] == "Running/Macros.html":
            entry["provenance_origin_ids"] = []
    mask_entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    with pytest.raises(ValueError, match="Ambiguous provenance"):
        a5.build_retirement_projection(plan, ledger, mask_entries, ["root_macro_usage"])


def test_11b_missing_rule_origin_provenance_is_invalid():
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"], symbols=["Running/Macros.html"],
    )
    ledger = _ledger_for(plan, ["root_macro_usage"])
    for entry in ledger:
        if entry["value"] == "Running/Macros.html":
            entry["provenance_origin_ids"] = [a5.ORIGIN_ACCEPTED_ANALYZER_DELTA]
    mask_entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    with pytest.raises(ValueError, match="lacks selected-rule origin provenance"):
        a5.build_retirement_projection(plan, ledger, mask_entries, ["root_macro_usage"])


def test_12_non_mask_projection_drift_is_invalid():
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"], symbols=_full_mask_symbols("root_macro_usage"),
    )
    ledger = _ledger_for(plan, ["root_macro_usage"])
    mask_entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    projected, receipts = a5.build_retirement_projection(
        plan, ledger, mask_entries, ["root_macro_usage"]
    )
    assert a5.verify_projection_diff(plan, projected, receipts)[0] is True
    # Any tampering with a non-mask field is detected.
    tampered = copy.deepcopy(projected)
    tampered["required_source_types"] = ["documentation"]
    ok, error = a5.verify_projection_diff(plan, tampered, receipts)
    assert ok is False and "required_source_types" in (error or "")


def test_12b_ledger_coverage_gaps_are_invalid():
    plan = _synthetic_canonical_plan(
        matched_rules=[], symbols=["mystery/symbol.cxx"],
    )
    ledger = a5.build_contribution_ledger(plan, _rules_by_id(), [])
    # A plan symbol with no identifiable origin has empty provenance.
    ok, error = a5.validate_ledger_coverage(plan, ledger)
    assert ok is False
    assert "mystery/symbol.cxx" in (error or "")


def test_12c_runtime_override_origin_is_identifiable():
    plan = _synthetic_canonical_plan(
        matched_rules=[], symbols=[], hints={"li_2026": [141, 149, 151]},
    )
    ledger = a5.build_contribution_ledger(plan, _rules_by_id(), [])
    ok, error = a5.validate_ledger_coverage(plan, ledger)
    assert ok is True, error
    entry = next(e for e in ledger if e["pdf_page"] == 141)
    assert a5.ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE in entry["provenance_origin_ids"]


# ---------------------------------------------------------------------------
# 13-15: Batch-1 invariance and no Batch-2 replacement
# ---------------------------------------------------------------------------


def test_13_batch1_diagnostics_invariant_across_projection():
    plan = _synthetic_canonical_plan(
        matched_rules=["effective_acceptance_pipeline", "restgas_profile_workflow"],
        symbols=["macro/target/prod_sim_hvmaps.C", "data/PndLmdAcceptance.cxx",
                 "model/PndLmdModelFactory.cxx"],
    )
    ledger = _ledger_for(plan, ["effective_acceptance_pipeline", "restgas_profile_workflow"])
    mask_entries = a5.build_batch2_mask_entries("g052", ["effective_acceptance_pipeline"])
    projected, _ = a5.build_retirement_projection(
        plan, ledger, mask_entries, ["effective_acceptance_pipeline"]
    )
    assert (
        projected["analysis_diagnostics"]["matched_expansion_rules"]
        == plan["analysis_diagnostics"]["matched_expansion_rules"]
    )
    assert (
        projected["analysis_diagnostics"]["structured_replacement_rules"]
        == plan["analysis_diagnostics"]["structured_replacement_rules"]
    )
    assert projected["analysis_diagnostics"] == plan["analysis_diagnostics"]


def test_14_g052_attribution_retains_batch1_rule():
    assert a5.CASE_ATTRIBUTION["g052"]["matched_batch1_rule_ids"] == ["restgas_profile_workflow"]
    assert PREREG["exact_paired_cell_schedule"][0]["matched_batch1_rule_ids"] == [
        "restgas_profile_workflow"
    ]
    assert PREREG["exact_paired_cell_schedule"][0]["batch1_replacement_expected_to_invoke"] is True


def test_15_no_batch2_structured_replacement():
    for rid, mask in b2.FROZEN_RETIREMENT_MASKS.items():
        assert mask["structured_replacement_after_retirement"] is False
    # The retirement projection never adds structured replacement fields.
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"], symbols=_full_mask_symbols("root_macro_usage"),
    )
    ledger = _ledger_for(plan, ["root_macro_usage"])
    mask_entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    projected, _ = a5.build_retirement_projection(
        plan, ledger, mask_entries, ["root_macro_usage"]
    )
    assert projected["analysis_diagnostics"].get("structured_replacement_rules") == []
    # Diagnostics are untouched by the projection (no Batch-2 replacement added).
    assert projected["analysis_diagnostics"] == plan["analysis_diagnostics"]
    for rid in b2.CANDIDATE_RULE_IDS:
        assert rid not in projected["analysis_diagnostics"].get(
            "structured_replacement_rules", []
        )


# ---------------------------------------------------------------------------
# 16-19: pair phenotypes (frozen D4-A4 function)
# ---------------------------------------------------------------------------


def test_16_ff_is_pair_unresolved_both():
    assert b2.classify_pair(False, False) == "PAIR_UNRESOLVED_BOTH"


def test_17_ft_is_pair_retirement_recovery():
    assert b2.classify_pair(False, True) == "PAIR_RETIREMENT_RECOVERY"


def test_18_tf_is_pair_retirement_regression():
    assert b2.classify_pair(True, False) == "PAIR_RETIREMENT_REGRESSION"


def test_19_tt_is_pair_preserved():
    assert b2.classify_pair(True, True) == "PAIR_PRESERVED"


def test_19b_ff_is_never_a_regression():
    for _ in range(1):
        assert b2.classify_pair(False, False) != "PAIR_RETIREMENT_REGRESSION"


# ---------------------------------------------------------------------------
# 20-24: per-rule dispositions (frozen D4-A4 function)
# ---------------------------------------------------------------------------


def test_20_attributable_tf_causes_dependency_observed_retain():
    assert b2.classify_rule(
        protocol_valid=True, baseline_reproduced=True, attributable_loss=True
    ) == "DEPENDENCY_OBSERVED_RETAIN"


def test_21_dependency_precedes_baseline_inconclusive():
    assert b2.classify_rule(
        protocol_valid=True, baseline_reproduced=False, attributable_loss=True
    ) == "DEPENDENCY_OBSERVED_RETAIN"


def test_22_baseline_miss_without_tf_is_inconclusive():
    assert b2.classify_rule(
        protocol_valid=True, baseline_reproduced=False, attributable_loss=False
    ) == "INCONCLUSIVE_BASELINE_NOT_REPRODUCED"


def test_23_valid_complete_rule_with_no_loss_is_retirement_validated():
    assert b2.classify_rule(
        protocol_valid=True, baseline_reproduced=True, attributable_loss=False
    ) == "RETIREMENT_VALIDATED"


def test_24_invalid_rule_protocol_is_invalid_protocol():
    assert b2.classify_rule(
        protocol_valid=False, baseline_reproduced=True, attributable_loss=False
    ) == "INVALID_PROTOCOL"


# ---------------------------------------------------------------------------
# 25-30: batch verdict levels (frozen D4-A4 verdict function)
# ---------------------------------------------------------------------------


def _verdict_kwargs(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "execution_valid": True,
        "protocol_violation": False,
        "missing_inputs": False,
        "plan_equality_all_verified": True,
        "analyzer_provider_calls_downstream": 0,
        "reference_baseline_valid": True,
        "per_rule_dispositions": {
            "effective_acceptance_pipeline": "RETIREMENT_VALIDATED",
            "root_macro_usage": "RETIREMENT_VALIDATED",
            "model_factory_theory": "RETIREMENT_VALIDATED",
        },
        "critical_retirement_regressions": 0,
        "grounding_regressions": 0,
        "wrong_version_regressions": 0,
        "invalid_provenance_recoveries": 0,
        "metric_deltas": {
            "recall_at_5": 0.0,
            "recall_at_10": 0.0,
            "recall_at_20": 0.0,
            "combined_candidate_recall": 0.0,
            "final_evidence_recall": 0.0,
            "critical_final_evidence_recall": 0.0,
        },
    }
    base.update(overrides)
    return base


def test_25_level1_incomplete_inputs_cannot_pass():
    for key in ("execution_valid", "reference_baseline_valid", "plan_equality_all_verified"):
        kwargs = _verdict_kwargs()
        kwargs[key] = None
        verdict = b2.evaluate_batch2_verdict(**kwargs)
        assert verdict["verdict_level"] == 1
    kwargs = _verdict_kwargs()
    kwargs["metric_deltas"] = {"recall_at_5": 0.0}
    verdict = b2.evaluate_batch2_verdict(**kwargs)
    assert verdict["verdict_level"] == 1
    kwargs = _verdict_kwargs()
    kwargs["per_rule_dispositions"] = {"effective_acceptance_pipeline": "RETIREMENT_VALIDATED"}
    verdict = b2.evaluate_batch2_verdict(**kwargs)
    assert verdict["verdict_level"] == 1


def test_25b_level1_invalid_execution():
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(execution_valid=False))
    assert verdict["verdict_level"] == 1
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(analyzer_provider_calls_downstream=1))
    assert verdict["verdict_level"] == 1


def test_26_level2_baseline_not_reproduced():
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(reference_baseline_valid=False))
    assert verdict["verdict_level"] == 2
    dispositions = _verdict_kwargs()["per_rule_dispositions"]
    dispositions["root_macro_usage"] = "INCONCLUSIVE_BASELINE_NOT_REPRODUCED"
    verdict = b2.evaluate_batch2_verdict(
        **_verdict_kwargs(per_rule_dispositions=dispositions)
    )
    assert verdict["verdict_level"] == 2


def test_27_level3_partial_dependency_without_safety_failure():
    dispositions = _verdict_kwargs()["per_rule_dispositions"]
    dispositions["model_factory_theory"] = "DEPENDENCY_OBSERVED_RETAIN"
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(per_rule_dispositions=dispositions))
    assert verdict["verdict_level"] == 3


def test_28_level4_safety_failure():
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(critical_retirement_regressions=1))
    assert verdict["verdict_level"] == 4
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(grounding_regressions=1))
    assert verdict["verdict_level"] == 4
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(wrong_version_regressions=1))
    assert verdict["verdict_level"] == 4
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(invalid_provenance_recoveries=1))
    assert verdict["verdict_level"] == 4
    # Safety failure takes precedence over partial dependency.
    dispositions = _verdict_kwargs()["per_rule_dispositions"]
    dispositions["model_factory_theory"] = "DEPENDENCY_OBSERVED_RETAIN"
    verdict = b2.evaluate_batch2_verdict(
        **_verdict_kwargs(per_rule_dispositions=dispositions, critical_retirement_regressions=1)
    )
    assert verdict["verdict_level"] == 4


def test_29_level5_bounded_aggregate_failure():
    deltas = _verdict_kwargs()["metric_deltas"]
    deltas["final_evidence_recall"] = -0.06
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(metric_deltas=deltas))
    assert verdict["verdict_level"] == 5
    # Exactly at tolerance passes down to Level 6.
    deltas["final_evidence_recall"] = -0.05
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs(metric_deltas=deltas))
    assert verdict["verdict_level"] == 6


def test_30_level6_clean_pass():
    verdict = b2.evaluate_batch2_verdict(**_verdict_kwargs())
    assert verdict["verdict_level"] == 6
    assert verdict["verdict_status"] == "PASS"


# ---------------------------------------------------------------------------
# 31-36: metric semantics, denominators, active groups
# ---------------------------------------------------------------------------


def _synthetic_question(qid: str, group_ids: list[str], *, answered: bool) -> GoldQuestion:
    groups = [
        {
            "group_id": gid,
            "role": f"role_{gid}",
            "critical": True,
            "any_of": [{"object_id": f"obj::{gid}"}],
        }
        for gid in group_ids
    ]
    return GoldQuestion.model_validate({
        "id": qid,
        "split": "dev" if qid.startswith("g") else "novel_dev",
        "language": "en",
        "intent": "algorithm_theory",
        "query": f"Synthetic question for {qid} used by unit fixtures only?",
        "expected_status": "answered" if answered else "insufficient_evidence",
        "allowed_source_versions": ["src_x@ver_1"],
        "required_evidence_groups": groups,
        "required_answer_points": ["synthetic answer point"],
    })


def _synthetic_object_lookup() -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for gid in (
        "g052.e1", "g055.e1", "g055.e2", "n003.e1", "n003.e2", "n004.e1",
        "g007.e1", "n014.e1", "n014.e2", "g060.e1", "g060.e2", "g060.e3",
    ):
        lookup[f"obj::{gid}"] = {
            "object_id": f"obj::{gid}",
            "source_id": "src_x",
            "source_version_id": "ver_1",
            "object_type": "source_file",
            "title": f"object {gid}",
            "text": "synthetic text",
            "locator": {"path": f"synthetic/{gid}.cxx"},
        }
    return lookup


def test_31_incomplete_metric_input_cannot_pass():
    question = _synthetic_question("g052", ["g052.e1"], answered=True)
    lookup = _synthetic_object_lookup()
    empty_slot = {"ranked_object_ids": [], "final_evidence_object_ids": [], "channel_rankings": {}}
    with pytest.raises(ValueError, match="Incomplete metric inputs"):
        a5._case_metric_value(question, empty_slot, lookup)


def test_32_mrr_cannot_alter_verdict():
    kwargs = _verdict_kwargs()
    assert "mrr" not in kwargs["metric_deltas"]
    assert set(kwargs["metric_deltas"]) == set(a5.PRIMARY_METRIC_KEYS)
    assert b2.DEFAULT_METRIC_BOUNDED_TOLERANCES.get("mrr") is None


def test_33_negative_control_excluded_from_answered_denominators():
    assert "g007" not in a5.ANSWERED_CASES
    assert a5.NEGATIVE_CONTROL_CASES == ["g007"]
    assert len(a5.ANSWERED_CASES) == 6


def test_34_six_answered_case_macro_denominator():
    assert a5.ANSWERED_CASES == ["g052", "g055", "n003", "n004", "n014", "g060"]
    assert len(a5.ANSWERED_CASES) == 6
    assert PREREG["evidence_group_applicability_and_denominators"]["case_macro_denominator"] == 6


def test_35_answered_evidence_group_count_is_11():
    details = PREREG["evidence_group_applicability_and_denominators"]["evidence_group_details"]
    answered_groups = [
        gid for cid in a5.ANSWERED_CASES for gid in [g["group_id"] for g in details[cid]]
    ]
    assert len(answered_groups) == 11
    control_groups = [g["group_id"] for g in details["g007"]]
    assert control_groups == ["g007.e1"]
    assert PREREG["evidence_group_applicability_and_denominators"][
        "answered_evidence_groups_count"
    ] == 11


def test_36_active_per_rule_groups_match_frozen_contract():
    frozen = PREREG["per_rule_decision_contract"]["active_case_groups"]
    assert a5.ACTIVE_RULE_CASE_GROUPS == frozen
    total = sum(len(gids) for mapping in a5.ACTIVE_RULE_CASE_GROUPS.values() for gids in mapping.values())
    assert total == 4


# ---------------------------------------------------------------------------
# 37: evaluator performs zero provider calls (synthetic end-to-end)
# ---------------------------------------------------------------------------


def _write_synthetic_project(tmp_path: Path) -> Path:
    """Synthetic evaluation project: frozen plans + raw paired results with
    synthetic cases/objects; no provider, no DB, no real cohort outcomes."""
    project = tmp_path
    (project / "evaluation").mkdir(parents=True, exist_ok=True)
    for authority in ("d4_a4_batch2_retirement_preregistration.json",):
        (project / "evaluation" / authority).write_bytes(
            (_REPO_ROOT / "evaluation" / authority).read_bytes()
        )

    questions = {
        "g052": _synthetic_question("g052", ["g052.e1"], answered=True),
        "g055": _synthetic_question("g055", ["g055.e1", "g055.e2"], answered=True),
        "n003": _synthetic_question("n003", ["n003.e1", "n003.e2"], answered=True),
        "n004": _synthetic_question("n004", ["n004.e1"], answered=True),
        "g007": _synthetic_question("g007", ["g007.e1"], answered=False),
        "n014": _synthetic_question("n014", ["n014.e1", "n014.e2"], answered=True),
        "g060": _synthetic_question("g060", ["g060.e1", "g060.e2", "g060.e3"], answered=True),
    }

    active_rule_for = a5.CASE_ATTRIBUTION

    def _evidence_ids(cid: str) -> list[str]:
        return [f"obj::{g.group_id}" for g in questions[cid].required_evidence_groups]

    def _ranked_ids(cid: str) -> list[str]:
        return _evidence_ids(cid) + ["obj::filler"]

    def _channel_rankings(cid: str) -> dict[str, list[str]]:
        ids = _ranked_ids(cid)
        return {"exact": ids, "dense": ids, "sparse": ids, "workflow": ids, "graph": ids}

    plans = []
    for cid in a5.CASE_ORDER:
        attribution = active_rule_for[cid]
        matched = ["restgas_profile_workflow"] if cid == "g052" else []
        matched_batch2 = list(attribution["matched_retirement_rules"])
        matched_rules = matched + matched_batch2
        symbols = []
        hints: dict[str, list[int]] = {}
        for rid in matched_batch2:
            symbols.extend(_full_mask_symbols(rid))
            for src, pages in b2.FROZEN_RETIREMENT_MASKS[rid].get(
                "paper_page_hints_retired", {}
            ).items():
                hints.setdefault(src, []).extend(pages)
        canonical = _synthetic_canonical_plan(matched_rules, symbols, hints)
        ledger = a5.build_contribution_ledger(canonical, _rules_by_id(), matched_rules)
        mask_entries = a5.build_batch2_mask_entries(cid, matched_batch2)
        projected, receipts = a5.build_retirement_projection(
            canonical, ledger, mask_entries, matched_batch2
        )
        gate = a5.build_provenance_gate_receipt(
            cid, attribution, matched_rules, canonical, ledger,
            copy.deepcopy(canonical), projected, receipts,
        )
        assert gate["pass"], (cid, gate)
        plans.append({
            "plan_id": f"prospective_{cid}",
            "case_id": cid,
            "question": questions[cid].query,
            "canonical_plan": canonical,
            "current_compat_execution_projection": copy.deepcopy(canonical),
            "batch2_retirement_execution_projection": projected,
            "projection_diff_receipts": receipts,
            "contribution_ledger": ledger,
            "matched_batch2_rule_ids": matched_batch2,
            "provenance_gate": gate,
            "plan_signature": {"synthetic": True},
        })

    slots = []
    for cell in a5.SCHEDULE_14:
        cid = cell["case_id"]
        slots.append({
            "cell_index": cell["cell_index"],
            "cell_id": cell["cell_id"],
            "case_id": cid,
            "arm": cell["arm"],
            "role": cell["role"],
            "status": "COMPLETED",
            "question": questions[cid].query,
            "frozen_canonical_plan": plans[a5.CASE_ORDER.index(cid)]["canonical_plan"],
            "plan_equality_arm_projection_verified": True,
            "batch2_retirement_mask_applied": cell["batch2_retirement_mask_applied"],
            "retirement_rule_ids": cell["retirement_rule_ids"],
            "channel_rankings": _channel_rankings(cid),
            "fusion_scores_top30": {oid: 0.1 for oid in _ranked_ids(cid)},
            "rerank_pool_object_ids": _ranked_ids(cid),
            "reranked_object_ids": _ranked_ids(cid),
            "ranked_object_ids": _ranked_ids(cid),
            "final_evidence_object_ids": _evidence_ids(cid),
            "final_evidence_entries": [
                {
                    "object_id": f"obj::{g.group_id}",
                    "source_id": "src_x",
                    "source_version_id": "ver_1",
                    "locator": {"path": f"synthetic/{g.group_id}.cxx"},
                    "object_type": "source_file",
                    "title": f"object {g.group_id}",
                }
                for g in questions[cid].required_evidence_groups
            ],
            "batch1_activation_receipt": None,
            "batch1_structured_replacement_active": cid == "g052",
            "batch1_active_rule_ids": ["restgas_profile_workflow"] if cid == "g052" else [],
            "provider_accounting": {
                "analyzer_calls": 0, "embedding_calls": 1, "reranker_calls": 1,
                "provider_internal_attempts": 2, "token_usage": 10,
            },
        })

    manifest = a5.build_initial_manifest(_REPO_ROOT)
    manifest["outcome_exposure_state"] = {
        "D4_A5_OUTCOME_EXPOSURE": "RAW_RETRIEVAL_COMPLETE",
        "executor_freeze_head": "0" * 40,
        "plan_freeze_head": "1" * 40,
        "plans_completed": 7,
        "formal_cells_completed": 14,
        "formal_cells_failed": 0,
        "evaluator_executed": False,
        "scientific_verdict_computed": False,
    }
    a5._save_json(project / "evaluation" / "d4_a5_execution_manifest.json", manifest)

    plans_artifact = {
        "schema_version": "1.0.0",
        "plans_planned": 7,
        "plans_completed": 7,
        "plans_failed": 0,
        "plans": plans,
        "accounting": {"analyzer_calls": 7, "token_usage": 70},
    }
    a5._save_json(project / "evaluation" / "d4_a5_raw_prospective_plans.json", plans_artifact)

    raw = {
        "schema_version": "1.0.0",
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "cells_planned": 14,
        "cells_completed": 14,
        "cells_failed": 0,
        "model_contract": {
            "generation_model_id": a5.EXPECTED_MODEL,
            "embedding_model_id": a5.EXPECTED_EMBEDDING_MODEL,
        },
        "accounting": {
            "FORMAL_CELLS_COMPLETED": 14,
            "FORMAL_CELLS_FAILED": 0,
            "ANALYZER_CALLS": 0,
            "EMBEDDING_CALLS": 14,
            "RERANKER_CALLS": 14,
            "LOGICAL_MODEL_CALLS": 28,
            "PROVIDER_INTERNAL_ATTEMPTS": 28,
            "TOTAL_TOKEN_USAGE": 140,
            "RETRIES": 0,
            "QA_CALLS": 0,
            "VERIFIER_CALLS": 0,
            "JUDGE_CALLS": 0,
            "NOVEL_VALIDATION_RUNS": 0,
            "NOVEL_HOLDOUT_RUNS": 0,
            "PROTECTED_DATASET_ACCESS": 0,
        },
        "slots": slots,
    }
    a5._save_json(project / "evaluation" / "d4_a5_raw_paired_retirement_results.json", raw)
    return project


def test_37_evaluator_runs_with_zero_provider_calls(tmp_path, monkeypatch):
    project = _write_synthetic_project(tmp_path)

    def _forbidden(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("Provider construction is forbidden in the evaluator")

    monkeypatch.setattr(a5, "Retriever", _forbidden)
    import panda_agent.llm.vertex as vertex_module

    monkeypatch.setattr(vertex_module, "VertexAIClient", _forbidden)
    monkeypatch.setattr(a5, "verify_raw_freeze_gate", lambda *_a, **_k: {"head": "synthetic"})

    real_load_gold = load_gold_dataset

    def _synthetic_dataset(path: Path) -> GoldDataset:
        questions = []
        for cid in a5.CASE_ORDER:
            answered = cid != "g007"
            group_count = {
                "g052": 1, "g055": 2, "n003": 2, "n004": 1, "g007": 1, "n014": 2, "g060": 3,
            }[cid]
            questions.append(_synthetic_question(
                cid, [f"{cid}.e{i + 1}" for i in range(group_count)], answered=answered,
            ))
        return GoldDataset.model_validate({
            "schema_version": "1.0.0",
            "benchmark_version": "synthetic",
            "questions": questions,
        })

    monkeypatch.setattr(a5, "load_gold_dataset", _synthetic_dataset)
    monkeypatch.setattr(a5, "load_object_lookup", lambda *_a, **_k: _synthetic_object_lookup())

    results = a5.evaluate_d4_a5(project)

    # All dispositions validated; clean Level 6 PASS on the synthetic fixture.
    assert results["per_rule_dispositions"] == {
        "effective_acceptance_pipeline": "RETIREMENT_VALIDATED",
        "root_macro_usage": "RETIREMENT_VALIDATED",
        "model_factory_theory": "RETIREMENT_VALIDATED",
    }
    assert results["verdict_level"] == 6
    assert results["verdict_status"] == "PASS"
    assert results["answered_case_denominator"] == 6
    assert results["answered_evidence_group_denominator"] == 11
    # Six primary metrics present with zero deltas on the identical-synthesis fixture;
    # MRR is diagnostic-only and cannot enter the verdict inputs.
    assert set(results["verdict_inputs"]["metric_deltas"]) == set(a5.PRIMARY_METRIC_KEYS)
    assert all(delta == 0.0 for delta in results["verdict_inputs"]["metric_deltas"].values())
    # Evaluator artifacts written deterministically.
    assert (project / "evaluation" / "d4_a5_evaluator_results.json").exists()
    result = json.loads((project / "evaluation" / "d4_a5_result.json").read_text(encoding="utf-8"))
    assert result["production_activation"] is False
    assert result["batch2_production_active"] is False
    assert result["batch1_production_active"] is True


def test_37b_evaluator_counts_control_divergence_as_safety_finding(tmp_path, monkeypatch):
    project = _write_synthetic_project(tmp_path)
    raw_path = project / "evaluation" / "d4_a5_raw_paired_retirement_results.json"
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    # Remove g055.e1 from the retirement arm's final evidence in the no-op control.
    for slot in raw["slots"]:
        if slot["cell_id"] == "g055_batch2_retirement":
            slot["final_evidence_object_ids"] = [
                oid for oid in slot["final_evidence_object_ids"] if oid != "obj::g055.e1"
            ]
            slot["final_evidence_entries"] = [
                e for e in slot["final_evidence_entries"] if e["object_id"] != "obj::g055.e1"
            ]
    a5._save_json(raw_path, raw)

    def _forbidden(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("Provider construction is forbidden in the evaluator")

    monkeypatch.setattr(a5, "Retriever", _forbidden)
    monkeypatch.setattr(a5, "verify_raw_freeze_gate", lambda *_a, **_k: {"head": "synthetic"})

    def _synthetic_dataset(_path: Path) -> GoldDataset:
        questions = []
        for cid in a5.CASE_ORDER:
            answered = cid != "g007"
            group_count = {
                "g052": 1, "g055": 2, "n003": 2, "n004": 1, "g007": 1, "n014": 2, "g060": 3,
            }[cid]
            questions.append(_synthetic_question(
                cid, [f"{cid}.e{i + 1}" for i in range(group_count)], answered=answered,
            ))
        return GoldDataset.model_validate({
            "schema_version": "1.0.0",
            "benchmark_version": "synthetic",
            "questions": questions,
        })

    monkeypatch.setattr(a5, "load_gold_dataset", _synthetic_dataset)
    monkeypatch.setattr(a5, "load_object_lookup", lambda *_a, **_k: _synthetic_object_lookup())

    results = a5.evaluate_d4_a5(project)
    safety = results["safety"]
    # The answered no-op control T/F critical loss is a batch safety finding.
    assert safety["critical_retirement_regressions"] == 1
    assert any(d["case_id"] == "g055" for d in safety["critical_regression_details"])
    # ...and it is NOT attributable to any Batch-2 rule.
    assert results["per_rule_dispositions"]["effective_acceptance_pipeline"] == "RETIREMENT_VALIDATED"
    assert results["verdict_level"] == 4


def test_37c_structural_validation_rejects_incomplete_artifacts(tmp_path):
    project = _write_synthetic_project(tmp_path)
    plans = json.loads(
        (project / "evaluation" / "d4_a5_raw_prospective_plans.json").read_text(encoding="utf-8")
    )
    raw = json.loads(
        (project / "evaluation" / "d4_a5_raw_paired_retirement_results.json").read_text(encoding="utf-8")
    )
    ok, error = a5.validate_raw_artifact_structural_validity(raw, plans)
    assert ok is True, error

    original_slots = copy.deepcopy(raw["slots"])
    raw["slots"] = original_slots[:13]
    ok, error = a5.validate_raw_artifact_structural_validity(raw, plans)
    assert ok is False and "14" in (error or "")

    raw["slots"] = copy.deepcopy(original_slots)
    raw["slots"][0]["provider_accounting"]["analyzer_calls"] = 1
    ok, error = a5.validate_raw_artifact_structural_validity(raw, plans)
    assert ok is False and "Analyzer" in (error or "")


# ---------------------------------------------------------------------------
# 38-40: production immutability, no shortcut, protected boundary
# ---------------------------------------------------------------------------


def test_38_production_query_expansions_not_mutated_by_treatment_construction():
    from panda_agent.config import load_query_expansions

    config_path = _REPO_ROOT / "configs" / "query_expansions.yaml"
    before = config_path.read_bytes()
    qe = load_query_expansions(config_path)
    rules_by_id = {r["rule_id"]: r for r in qe.model_dump(mode="python")["rules"]}
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"], symbols=_full_mask_symbols("root_macro_usage"),
    )
    ledger = a5.build_contribution_ledger(plan, rules_by_id, ["root_macro_usage"])
    mask_entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    a5.build_retirement_projection(plan, ledger, mask_entries, ["root_macro_usage"])
    assert config_path.read_bytes() == before
    # The live production rule objects are untouched.
    live_rule = next(r for r in qe.rules if r.rule_id == "root_macro_usage")
    assert "Running/Macros.html" in live_rule.symbols


def test_38b_projection_never_mutates_input_plan():
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"],
        symbols=_full_mask_symbols("root_macro_usage"),
    )
    snapshot = copy.deepcopy(plan)
    ledger = a5.build_contribution_ledger(plan, _rules_by_id(), ["root_macro_usage"])
    mask_entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    projected, _ = a5.build_retirement_projection(plan, ledger, mask_entries, ["root_macro_usage"])
    assert plan == snapshot
    assert projected["symbols"] == []


def test_39_projection_has_no_benchmark_or_case_shortcut():
    import inspect

    source = inspect.getsource(a5.build_retirement_projection)
    assert "gold" not in source.casefold()
    assert "novel" not in source.casefold()
    assert "required_evidence" not in source.casefold()
    source = inspect.getsource(a5.build_contribution_ledger)
    assert "gold" not in source.casefold()
    assert "novel" not in source.casefold()
    # Mask inputs come exclusively from the frozen D4-A4 module.
    source = inspect.getsource(a5.build_batch2_mask_entries)
    assert "b2.FROZEN_RETIREMENT_MASKS" in source


def test_40_no_protected_dataset_access(tmp_path_factory):
    text = Path(a5.__file__).read_text(encoding="utf-8")
    assert "novel_validation" not in text.replace("novel_validation_runs", "").replace(
        "NOVEL_VALIDATION_RUNS", ""
    )
    assert "novel_holdout" not in text.replace("novel_holdout_runs", "").replace(
        "NOVEL_HOLDOUT_RUNS", ""
    )
    manifest = a5.build_initial_manifest(_REPO_ROOT)
    assert manifest["pre_exposure_accounting"]["novel_validation_runs"] == 0
    assert manifest["pre_exposure_accounting"]["novel_holdout_runs"] == 0
    assert manifest["pre_exposure_accounting"]["protected_dataset_access"] == 0
    # Structural validation rejects protected-dataset access counters.
    project = _write_synthetic_project(tmp_path_factory.mktemp("d4_a5_test40"))
    plans = json.loads(
        (project / "evaluation" / "d4_a5_raw_prospective_plans.json").read_text(encoding="utf-8")
    )
    raw = json.loads(
        (project / "evaluation" / "d4_a5_raw_paired_retirement_results.json").read_text(encoding="utf-8")
    )
    raw["accounting"]["NOVEL_VALIDATION_RUNS"] = 1
    ok, error = a5.validate_raw_artifact_structural_validity(raw, plans)
    assert ok is False and "Protected dataset" in (error or "")


# ---------------------------------------------------------------------------
# Boundary and manifest integrity
# ---------------------------------------------------------------------------


def test_41_manifest_schedule_and_slots():
    manifest = a5.build_initial_manifest(_REPO_ROOT)
    assert len(manifest["phase_p_slots_7"]) == 7
    assert [s["case_id"] for s in manifest["phase_p_slots_7"]] == a5.CASE_ORDER
    assert len(manifest["phase_r_cells_14"]) == 14
    assert manifest["production_activation"] is False
    assert manifest["batch2_production_active"] is False
    assert manifest["batch1_production_active"] is True
    assert all(s["status"] == "NOT_EXECUTED" for s in manifest["phase_p_slots_7"])
    assert all(c["status"] == "NOT_EXECUTED" for c in manifest["phase_r_cells_14"])
    assert all(v == 0 for v in manifest["pre_exposure_accounting"].values())


def test_42_expected_accounting_contract():
    assert a5.EXPECTED_ACCOUNTING == {
        "analyzer_phase_p": 7,
        "analyzer_phase_r": 0,
        "embedding_downstream": 14,
        "reranker_downstream": 14,
        "total_logical_model_calls": 35,
        "qa_verifier_judge": 0,
    }
    assert a5.MAX_PROVIDER_ATTEMPTS_PER_CASE == 1


def test_43_production_immutable_paths_cover_the_frozen_boundary():
    for rel in (
        "configs/query_expansions.yaml",
        "src/panda_agent/config.py",
        "src/panda_agent/retrieval.py",
        "src/panda_agent/d3_structured.py",
        "evaluation/benchmarks/v2_6/gold_questions.yaml",
        "evaluation/novel/v1/novel_dev.yaml",
        "evaluation/d4_a4_batch2_retirement_preregistration.json",
    ):
        assert rel in a5.PRODUCTION_IMMUTABLE_PATHS
