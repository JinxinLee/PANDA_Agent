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
        component_receipts, applicability_summary = a5.classify_component_applicability(
            canonical, ledger, mask_entries
        )
        gate = a5.build_provenance_gate_receipt(
            cid, attribution, matched_rules, canonical, ledger,
            copy.deepcopy(canonical), projected, receipts,
            component_receipts=component_receipts,
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
            "component_applicability_receipts": component_receipts,
            "component_applicability_summary": applicability_summary,
            "provenance_gate": gate,
            "plan_signature": {"synthetic": True},
            "status": "COMPLETED",
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
    manifest["checkpoint"] = "D4-A5-CONTINUATION"
    manifest["outcome_exposure_state"] = {
        "D4_A5_OUTCOME_EXPOSURE": "RAW_RETRIEVAL_COMPLETE",
        "continuation_implementation_freeze_head": "0" * 40,
        "plan_freeze_head": "1" * 40,
        "plans_completed": 7,
        "formal_cells_completed": 14,
        "formal_cells_failed": 0,
        "evaluator_executed": False,
        "scientific_verdict_computed": False,
    }
    a5._save_json(
        project / "evaluation" / "d4_a5_continuation_execution_manifest.json", manifest
    )

    plans_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5-CONTINUATION",
        "plans_planned": 7,
        "plans_completed": 7,
        "plans_failed": 0,
        "plans": plans,
        "accounting": {"analyzer_calls": 7, "token_usage": 70},
    }
    a5._save_json(
        project / "evaluation" / "d4_a5_continuation_raw_prospective_plans.json",
        plans_artifact,
    )

    raw = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5-CONTINUATION",
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
    a5._save_json(
        project / "evaluation" / "d4_a5_continuation_raw_paired_retirement_results.json", raw
    )
    return project


def test_37_evaluator_runs_with_zero_provider_calls(tmp_path, monkeypatch):
    project = _write_synthetic_project(tmp_path)

    def _forbidden(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("Provider construction is forbidden in the evaluator")

    monkeypatch.setattr(a5, "Retriever", _forbidden)
    import panda_agent.llm.vertex as vertex_module

    monkeypatch.setattr(vertex_module, "VertexAIClient", _forbidden)
    monkeypatch.setattr(
        a5,
        "verify_continuation_evaluator_preflight",
        lambda *_a, **_k: {
            "continuation_implementation_freeze_head": "0" * 40,
            "continuation_plan_freeze_head": "1" * 40,
            "continuation_raw_freeze_head": "synthetic",
            "evaluator_integrity_sealed": True,
        },
    )

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
    assert results["verdict_level"] == 7
    assert results["verdict_status"] == "PASS"
    # Every synthetic mask component is ACTIVE_IDENTIFIABLE -> full validation.
    for rid, acct in results["per_rule_component_accounting"].items():
        assert acct["inactive_component_count"] == 0
        assert acct["active_component_count"] == acct["frozen_component_count"] > 0
    assert results["answered_case_denominator"] == 6
    assert results["answered_evidence_group_denominator"] == 11
    # Six primary metrics present with zero deltas on the identical-synthesis fixture;
    # MRR is diagnostic-only and cannot enter the verdict inputs.
    assert set(results["verdict_inputs"]["metric_deltas"]) == set(a5.PRIMARY_METRIC_KEYS)
    assert all(delta == 0.0 for delta in results["verdict_inputs"]["metric_deltas"].values())
    # Evaluator artifacts written deterministically.
    assert (project / "evaluation" / "d4_a5_continuation_evaluator_results.json").exists()
    result = json.loads(
        (project / "evaluation" / "d4_a5_continuation_result.json").read_text(encoding="utf-8")
    )
    assert result["production_activation"] is False
    assert result["batch2_production_active"] is False
    assert result["batch1_production_active"] is True


def test_37b_evaluator_counts_control_divergence_as_safety_finding(tmp_path, monkeypatch):
    project = _write_synthetic_project(tmp_path)
    raw_path = project / "evaluation" / "d4_a5_continuation_raw_paired_retirement_results.json"
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
    monkeypatch.setattr(
        a5,
        "verify_continuation_evaluator_preflight",
        lambda *_a, **_k: {
            "continuation_implementation_freeze_head": "0" * 40,
            "continuation_plan_freeze_head": "1" * 40,
            "continuation_raw_freeze_head": "synthetic",
            "evaluator_integrity_sealed": True,
        },
    )

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
        (project / "evaluation" / "d4_a5_continuation_raw_prospective_plans.json").read_text(encoding="utf-8")
    )
    raw = json.loads(
        (project / "evaluation" / "d4_a5_continuation_raw_paired_retirement_results.json").read_text(encoding="utf-8")
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
        (project / "evaluation" / "d4_a5_continuation_raw_prospective_plans.json").read_text(encoding="utf-8")
    )
    raw = json.loads(
        (project / "evaluation" / "d4_a5_continuation_raw_paired_retirement_results.json").read_text(encoding="utf-8")
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


# ===========================================================================
# D4-A5-R1 — Retirement Applicability and Provenance-Contract Repair tests
# ===========================================================================


def _r1_component(receipts: list[dict[str, Any]], value: str) -> dict[str, Any]:
    return next(r for r in receipts if r["component_value"] == value)


def test_r1_01_active_when_selected_rule_origin_present():
    plan = _synthetic_canonical_plan(
        matched_rules=["effective_acceptance_pipeline"],
        symbols=_full_mask_symbols("effective_acceptance_pipeline"),
    )
    ledger = _ledger_for(plan, ["effective_acceptance_pipeline"])
    entries = a5.build_batch2_mask_entries("g052", ["effective_acceptance_pipeline"])
    receipts, summary = a5.classify_component_applicability(plan, ledger, entries)
    assert summary == {"active": 3, "inactive": 0, "ambiguous": 0}
    for receipt in receipts:
        assert receipt["applicability_status"] == a5.APPLICABILITY_ACTIVE
        assert receipt["selected_rule_origin_present"] is True
        assert receipt["retirement_projection_action"] == (
            "remove_selected_rule_origin_preserve_independent_origins"
        )


def test_r1_02_inactive_when_selected_rule_origin_absent_via_analyzer_only():
    plan = _synthetic_canonical_plan(
        matched_rules=["effective_acceptance_pipeline"],
        symbols=["data/PndLmdAcceptance.cxx"],
    )
    # The token is present but contributed only by the accepted analyzer delta;
    # the selected rule did not contribute it after normal plan construction.
    plan["analysis_diagnostics"]["analyzer_accepted_semantic_delta"] = {
        "symbols": [{"value": "data/PndLmdAcceptance.cxx", "support_spans": [1]}],
        "concepts": [{"value": "synthetic concept", "support_spans": [0]}],
    }
    rules = _rules_by_id()
    rules["effective_acceptance_pipeline"] = {
        "rule_id": "effective_acceptance_pipeline",
        "triggers": ["effective acceptance"],
        "repositories": [],
        "symbols": [],
        "concepts": [],
        "paper_page_hints": {},
    }
    ledger = a5.build_contribution_ledger(
        plan, rules, ["effective_acceptance_pipeline"]
    )
    entries = a5.build_batch2_mask_entries("g052", ["effective_acceptance_pipeline"])
    receipts, summary = a5.classify_component_applicability(plan, ledger, entries)
    receipt = _r1_component(receipts, "data/PndLmdAcceptance.cxx")
    assert receipt["applicability_status"] == a5.APPLICABILITY_INACTIVE
    assert receipt["selected_rule_origin_present"] is False
    assert receipt["final_canonical_plan_presence"] is True
    assert receipt["held_reason"]
    assert summary["inactive"] == 3


def test_r1_03_token_only_from_another_rule_is_inactive_for_selected_rule():
    plan = _synthetic_canonical_plan(
        matched_rules=["effective_acceptance_pipeline", "synthetic_other_rule"],
        symbols=["data/PndLmdAcceptance.cxx"],
    )
    rules = _rules_by_id()
    rules["synthetic_other_rule"] = {
        "rule_id": "synthetic_other_rule",
        "triggers": ["other"],
        "repositories": [],
        "symbols": ["data/PndLmdAcceptance.cxx"],
        "concepts": [],
        "paper_page_hints": {},
    }
    rules["effective_acceptance_pipeline"] = dict(
        rules["effective_acceptance_pipeline"], symbols=[]
    )
    ledger = a5.build_contribution_ledger(
        plan, rules, ["effective_acceptance_pipeline", "synthetic_other_rule"]
    )
    entries = a5.build_batch2_mask_entries("g052", ["effective_acceptance_pipeline"])
    receipts, _ = a5.classify_component_applicability(plan, ledger, entries)
    receipt = _r1_component(receipts, "data/PndLmdAcceptance.cxx")
    assert receipt["applicability_status"] == a5.APPLICABILITY_INACTIVE
    assert receipt["independent_origins"] == ["synthetic_other_rule"]


def test_r1_04_multi_origin_token_removes_selected_rule_origin_only():
    plan = _synthetic_canonical_plan(
        matched_rules=["effective_acceptance_pipeline"],
        symbols=_full_mask_symbols("effective_acceptance_pipeline"),
    )
    plan["analysis_diagnostics"]["analyzer_accepted_semantic_delta"] = {
        "symbols": [{"value": "macro/target/prod_sim_hvmaps.C", "support_spans": [1]}],
        "concepts": [{"value": "synthetic concept", "support_spans": [0]}],
    }
    ledger = _ledger_for(plan, ["effective_acceptance_pipeline"])
    entries = a5.build_batch2_mask_entries("g052", ["effective_acceptance_pipeline"])
    receipts, _ = a5.classify_component_applicability(plan, ledger, entries)
    receipt = _r1_component(receipts, "macro/target/prod_sim_hvmaps.C")
    assert receipt["applicability_status"] == a5.APPLICABILITY_ACTIVE
    assert receipt["independent_origins"] == [a5.ORIGIN_ACCEPTED_ANALYZER_DELTA]
    projected, diff = a5.build_retirement_projection_r1(
        plan, ledger, receipts, ["effective_acceptance_pipeline"]
    )
    # Selected-rule origin retired; the token itself survives via the delta origin.
    assert "macro/target/prod_sim_hvmaps.C" in projected["symbols"]
    removed = next(
        e for e in diff["removed_rule_origin_entries"]
        if e["value"] == "macro/target/prod_sim_hvmaps.C"
    )
    assert removed["effectively_removed"] is False
    assert removed["surviving_independent_origins"] == [a5.ORIGIN_ACCEPTED_ANALYZER_DELTA]


def test_r1_05_independent_origin_survives_treatment():
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"],
        symbols=_full_mask_symbols("root_macro_usage"),
    )
    plan["analysis_diagnostics"]["analyzer_accepted_semantic_delta"] = {
        "symbols": [{"value": "Running/Macros.html", "support_spans": [1]}],
        "concepts": [{"value": "synthetic concept", "support_spans": [0]}],
    }
    ledger = _ledger_for(plan, ["root_macro_usage"])
    entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    receipts, _ = a5.classify_component_applicability(plan, ledger, entries)
    projected, diff = a5.build_retirement_projection_r1(
        plan, ledger, receipts, ["root_macro_usage"]
    )
    assert "Running/Macros.html" in projected["symbols"]
    assert diff["applicability_summary"]["inactive"] == 0


def test_r1_06_ambiguous_provenance_is_invalid():
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"],
        symbols=_full_mask_symbols("root_macro_usage"),
    )
    ledger = _ledger_for(plan, ["root_macro_usage"])
    for entry in ledger:
        if entry["value"] == "Running/Macros.html":
            entry["provenance_origin_ids"] = []
    entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    receipts, summary = a5.classify_component_applicability(plan, ledger, entries)
    receipt = _r1_component(receipts, "Running/Macros.html")
    assert receipt["applicability_status"] == a5.APPLICABILITY_AMBIGUOUS
    assert receipt["provenance_ambiguity_reason"]
    assert summary["ambiguous"] == 1
    with pytest.raises(ValueError, match="AMBIGUOUS_INVALID"):
        a5.build_retirement_projection_r1(
            plan, ledger, receipts, ["root_macro_usage"]
        )


def test_r1_07_inactive_component_is_not_protocol_invalid():
    plan = _synthetic_canonical_plan(
        matched_rules=["model_factory_theory"],
        symbols=[],
        hints={},
    )
    ledger = _ledger_for(plan, ["model_factory_theory"])
    entries = a5.build_batch2_mask_entries("n014", ["model_factory_theory"])
    assert len(entries) == 6  # 3 symbols + 3 page hints configured
    receipts, summary = a5.classify_component_applicability(plan, ledger, entries)
    assert summary == {"active": 0, "inactive": 6, "ambiguous": 0}
    projected, diff = a5.build_retirement_projection_r1(
        plan, ledger, receipts, ["model_factory_theory"]
    )
    gate = a5.build_provenance_gate_receipt(
        "n014", a5.CASE_ATTRIBUTION["n014"], ["model_factory_theory"],
        plan, ledger, copy.deepcopy(plan), projected, diff,
        component_receipts=receipts,
    )
    assert gate["pass"] is True
    assert gate["checks"]["component_applicability"]["inactive"] == 6
    assert gate["checks"]["component_applicability"]["ambiguous"] == 0


def test_r1_08_inactive_component_is_never_retirement_validated():
    for active, frozen in ((1, 2), (0, 3), (2, 3)):
        assert a5.classify_rule_r1(
            protocol_valid=True,
            baseline_reproduced=True,
            attributable_loss=False,
            active_component_count=active,
            frozen_component_count=frozen,
        ) != a5.DISPOSITION_RETIREMENT_VALIDATED


def test_r1_09_inactive_component_is_never_dependency_observed():
    # No effective removal of any active contribution -> no attributable loss.
    assert a5.classify_rule_r1(
        protocol_valid=True,
        baseline_reproduced=True,
        attributable_loss=False,
        active_component_count=0,
        frozen_component_count=3,
    ) == a5.DISPOSITION_NO_ACTIVE_COMPONENT


def test_r1_10_zero_active_components_is_inconclusive_no_active():
    assert a5.classify_rule_r1(
        protocol_valid=True,
        baseline_reproduced=True,
        attributable_loss=False,
        active_component_count=0,
        frozen_component_count=3,
    ) == a5.DISPOSITION_NO_ACTIVE_COMPONENT


def test_r1_11_partial_active_subset_is_component_hold():
    assert a5.classify_rule_r1(
        protocol_valid=True,
        baseline_reproduced=True,
        attributable_loss=False,
        active_component_count=2,
        frozen_component_count=3,
    ) == a5.DISPOSITION_PARTIAL_COMPONENT_HOLD


def test_r1_12_full_active_mask_with_no_loss_is_validated():
    assert a5.classify_rule_r1(
        protocol_valid=True,
        baseline_reproduced=True,
        attributable_loss=False,
        active_component_count=3,
        frozen_component_count=3,
    ) == a5.DISPOSITION_RETIREMENT_VALIDATED


def test_r1_13_attributable_tf_is_dependency_observed():
    assert a5.classify_rule_r1(
        protocol_valid=True,
        baseline_reproduced=True,
        attributable_loss=True,
        active_component_count=3,
        frozen_component_count=3,
    ) == a5.DISPOSITION_DEPENDENCY


def test_r1_14_dependency_precedes_another_groups_baseline_miss():
    assert a5.classify_rule_r1(
        protocol_valid=True,
        baseline_reproduced=False,
        attributable_loss=True,
        active_component_count=1,
        frozen_component_count=2,
    ) == a5.DISPOSITION_DEPENDENCY


def test_r1_15_baseline_miss_without_tf_is_baseline_inconclusive():
    assert a5.classify_rule_r1(
        protocol_valid=True,
        baseline_reproduced=False,
        attributable_loss=False,
        active_component_count=3,
        frozen_component_count=3,
    ) == a5.DISPOSITION_BASELINE_INCONCLUSIVE


def test_r1_16_protocol_ambiguity_is_invalid_protocol():
    assert a5.classify_rule_r1(
        protocol_valid=False,
        baseline_reproduced=True,
        attributable_loss=False,
        active_component_count=3,
        frozen_component_count=3,
    ) == a5.DISPOSITION_INVALID_PROTOCOL
    assert a5.classify_rule_r1(
        protocol_valid=True,
        baseline_reproduced=True,
        attributable_loss=False,
        active_component_count=4,
        frozen_component_count=3,
    ) == a5.DISPOSITION_INVALID_PROTOCOL


def _r1_verdict(dispositions: dict[str, str], **overrides: Any) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "execution_valid": True,
        "protocol_violation": False,
        "missing_inputs": False,
        "plan_equality_all_verified": True,
        "analyzer_provider_calls_downstream": 0,
        "reference_baseline_valid": not any(
            d == a5.DISPOSITION_BASELINE_INCONCLUSIVE for d in dispositions.values()
        ),
        "per_rule_dispositions": dispositions,
        "critical_retirement_regressions": 0,
        "grounding_regressions": 0,
        "wrong_version_regressions": 0,
        "invalid_provenance_recoveries": 0,
        "metric_deltas": {k: 0.0 for k in a5.DEFAULT_METRIC_TOLERANCES_KEYS},
    }
    kwargs.update(overrides)
    return a5.evaluate_batch2_verdict_r1(**kwargs)


def test_r1_17_safety_and_dependency_coexist_is_level4_not_level3():
    dispositions = {
        "effective_acceptance_pipeline": a5.DISPOSITION_RETIREMENT_VALIDATED,
        "root_macro_usage": a5.DISPOSITION_DEPENDENCY,
        "model_factory_theory": a5.DISPOSITION_RETIREMENT_VALIDATED,
    }
    verdict = _r1_verdict(dispositions, critical_retirement_regressions=1)
    assert verdict["verdict_level"] == 4
    assert verdict["verdict_status"] == "FAIL"


def test_r1_18_applicability_incomplete_is_level5():
    for d in (a5.DISPOSITION_NO_ACTIVE_COMPONENT, a5.DISPOSITION_PARTIAL_COMPONENT_HOLD):
        dispositions = {
            "effective_acceptance_pipeline": a5.DISPOSITION_RETIREMENT_VALIDATED,
            "root_macro_usage": a5.DISPOSITION_RETIREMENT_VALIDATED,
            "model_factory_theory": d,
        }
        verdict = _r1_verdict(dispositions)
        assert verdict["verdict_level"] == 5
        assert verdict["verdict"] == a5.R1_VERDICT_LEVEL_5_APPLICABILITY


def test_r1_19_aggregate_failure_only_after_full_component_validation():
    full = {rid: a5.DISPOSITION_RETIREMENT_VALIDATED for rid in b2.CANDIDATE_RULE_IDS}
    deltas = {k: 0.0 for k in a5.DEFAULT_METRIC_TOLERANCES_KEYS}
    deltas["final_evidence_recall"] = -0.06
    verdict = _r1_verdict(full, metric_deltas=deltas)
    assert verdict["verdict_level"] == 6
    # Same aggregate failure with an incomplete mask is Level 5 instead.
    partial = dict(full)
    partial["model_factory_theory"] = a5.DISPOSITION_PARTIAL_COMPONENT_HOLD
    verdict = _r1_verdict(partial, metric_deltas=deltas)
    assert verdict["verdict_level"] == 5


def test_r1_20_clean_full_validation_is_level7_pass():
    full = {rid: a5.DISPOSITION_RETIREMENT_VALIDATED for rid in b2.CANDIDATE_RULE_IDS}
    verdict = _r1_verdict(full)
    assert verdict["verdict_level"] == 7
    assert verdict["verdict"] == a5.R1_VERDICT_LEVEL_7_PASS


def test_r1_21_truth_space_is_exhaustive_without_gaps():
    import itertools

    disposition_values = list(a5.R1_PER_RULE_DISPOSITIONS)
    rules = list(b2.CANDIDATE_RULE_IDS)
    for combo in itertools.product(disposition_values, repeat=len(rules)):
        dispositions = dict(zip(rules, combo))
        for safety in (False, True):
            for metrics_pass in (False, True):
                kwargs: dict[str, Any] = {
                    "execution_valid": True,
                    "protocol_violation": False,
                    "missing_inputs": False,
                    "plan_equality_all_verified": True,
                    "analyzer_provider_calls_downstream": 0,
                    "reference_baseline_valid": not any(
                        d == a5.DISPOSITION_BASELINE_INCONCLUSIVE for d in combo
                    ),
                    "per_rule_dispositions": dispositions,
                    "critical_retirement_regressions": 1 if safety else 0,
                    "grounding_regressions": 0,
                    "wrong_version_regressions": 0,
                    "invalid_provenance_recoveries": 0,
                    "metric_deltas": {
                        k: (0.0 if metrics_pass else -0.5)
                        for k in a5.DEFAULT_METRIC_TOLERANCES_KEYS
                    },
                }
                verdict = a5.evaluate_batch2_verdict_r1(**kwargs)
                if any(d == a5.DISPOSITION_INVALID_PROTOCOL for d in combo):
                    expected = 1
                elif any(d == a5.DISPOSITION_BASELINE_INCONCLUSIVE for d in combo):
                    expected = 2
                elif safety:
                    expected = 4
                elif any(d == a5.DISPOSITION_DEPENDENCY for d in combo):
                    expected = 3
                elif any(
                    d in (a5.DISPOSITION_NO_ACTIVE_COMPONENT, a5.DISPOSITION_PARTIAL_COMPONENT_HOLD)
                    for d in combo
                ):
                    expected = 5
                elif not metrics_pass:
                    expected = 6
                else:
                    expected = 7
                assert verdict["verdict_level"] == expected, (combo, safety, metrics_pass, verdict)
                assert verdict["verdict_level"] in a5.R1_BATCH_VERDICT_LEVELS
    # classify_rule_r1 precedence table over its full input space.
    for protocol in (True, False):
        for baseline in (True, False):
            for loss in (True, False):
                for active, frozen in ((0, 0), (0, 3), (1, 3), (2, 3), (3, 3)):
                    d = a5.classify_rule_r1(
                        protocol_valid=protocol,
                        baseline_reproduced=baseline,
                        attributable_loss=loss,
                        active_component_count=active,
                        frozen_component_count=frozen,
                    )
                    assert d in a5.R1_PER_RULE_DISPOSITIONS
                    if (
                        not protocol
                        or (active, frozen) == (0, 0)
                        or active > frozen
                        or (loss and active == 0)
                    ):
                        assert d == a5.DISPOSITION_INVALID_PROTOCOL
                    elif loss:
                        assert d == a5.DISPOSITION_DEPENDENCY
                    elif not baseline:
                        assert d == a5.DISPOSITION_BASELINE_INCONCLUSIVE
                    elif active == 0:
                        assert d == a5.DISPOSITION_NO_ACTIVE_COMPONENT
                    elif active < frozen:
                        assert d == a5.DISPOSITION_PARTIAL_COMPONENT_HOLD
                    else:
                        assert d == a5.DISPOSITION_RETIREMENT_VALIDATED


def test_r1_22_mrr_cannot_affect_verdict():
    full = {rid: a5.DISPOSITION_RETIREMENT_VALIDATED for rid in b2.CANDIDATE_RULE_IDS}
    kwargs = {
        "execution_valid": True,
        "protocol_violation": False,
        "missing_inputs": False,
        "plan_equality_all_verified": True,
        "analyzer_provider_calls_downstream": 0,
        "reference_baseline_valid": True,
        "per_rule_dispositions": full,
        "critical_retirement_regressions": 0,
        "grounding_regressions": 0,
        "wrong_version_regressions": 0,
        "invalid_provenance_recoveries": 0,
        "metric_deltas": {k: -0.5 for k in a5.DEFAULT_METRIC_TOLERANCES_KEYS},
    }
    verdict = a5.evaluate_batch2_verdict_r1(**kwargs)
    assert verdict["verdict_level"] == 6  # primary metrics fail, MRR not consulted
    kwargs["metric_deltas"]["mrr"] = -1.0  # even a catastrophic MRR changes nothing
    verdict2 = a5.evaluate_batch2_verdict_r1(**kwargs)
    assert verdict2["verdict_level"] == 6


def test_r1_23_six_primary_metrics_and_thresholds_unchanged():
    assert a5.DEFAULT_METRIC_TOLERANCES_KEYS == (
        "recall_at_5", "recall_at_10", "recall_at_20",
        "combined_candidate_recall", "final_evidence_recall",
        "critical_final_evidence_recall",
    )
    assert b2.DEFAULT_METRIC_BOUNDED_TOLERANCES == {
        "recall_at_5": -0.05,
        "recall_at_10": -0.05,
        "recall_at_20": -0.05,
        "combined_candidate_recall": -0.05,
        "final_evidence_recall": -0.05,
        "critical_final_evidence_recall": 0.0,
    }
    assert a5.PRIMARY_METRIC_KEYS == list(a5.DEFAULT_METRIC_TOLERANCES_KEYS)


def test_r1_24_original_a4_masks_unchanged():
    for rid, mask in b2.FROZEN_RETIREMENT_MASKS.items():
        prereg_mask = PREREG["exact_component_masks"][rid]
        shared = {k: v for k, v in prereg_mask.items() if k in mask}
        assert mask == shared
    assert a5.build_initial_manifest(_REPO_ROOT)["frozen_retirement_masks"] == b2.FROZEN_RETIREMENT_MASKS


def test_r1_25_pflueger_page_hints_remain_configured_in_mask():
    mask = b2.FROZEN_RETIREMENT_MASKS["model_factory_theory"]
    assert mask["paper_page_hints_retired"] == {"pflueger_2017": [51, 57, 65]}
    assert len(mask["symbols_retired"]) == 3
    assert PREREG["exact_component_masks"]["model_factory_theory"]["paper_page_hints_retired"] == {
        "pflueger_2017": [51, 57, 65]
    }


def test_r1_26_applicability_is_generic_not_case_tailored():
    import inspect

    for func in (
        a5.classify_component_applicability,
        a5.build_retirement_projection_r1,
        a5.classify_rule_r1,
        a5.evaluate_batch2_verdict_r1,
        a5.build_provenance_gate_receipt,
        a5.audit_historical_plan_reusability,
    ):
        lowered = inspect.getsource(func).casefold()
        assert "n014" not in lowered, func.__name__
        assert "pflueger" not in lowered, func.__name__
        assert "model_factory_theory" not in lowered, func.__name__
        assert "effective_acceptance" not in lowered, func.__name__
        assert "root_macro" not in lowered, func.__name__


# --- persistence-before-gate behavioral tests (Sections 16/27/28) -------------


class _FakeVertex:
    def __init__(self) -> None:
        self.calls = 0
        self.tokens = 0

    def stats_snapshot(self) -> dict[str, int]:
        return {"model_calls": self.calls, "token_usage": self.tokens,
                "generation_calls": 0, "embedding_calls": 0}

    def stats_delta(self, previous: dict[str, int]) -> dict[str, int]:
        current = self.stats_snapshot()
        return {k: current.get(k, 0) - previous.get(k, 0) for k in set(current) | set(previous)}


class _FakeQueryExpansions:
    """Real 54-rule config, with selected-rule symbols/hints stripped from the
    dump so configured components simulate inactive contributions."""

    def __init__(self, qe: Any, stripped: bool) -> None:
        self.rules = qe.rules
        self._stripped = stripped
        self._qe = qe

    def model_dump(self, mode: str | None = None) -> dict[str, Any]:
        dumped = self._qe.model_dump(mode="python")
        if self._stripped:
            for rule in dumped["rules"]:
                if rule["rule_id"] in b2.CANDIDATE_RULE_IDS:
                    rule["symbols"] = []
                    rule["paper_page_hints"] = {}
        return dumped


class _FakeRetriever:
    def __init__(self, plans_by_question: dict[str, dict[str, Any]], qe: Any) -> None:
        self.plans_by_question = plans_by_question
        self.query_expansions = qe
        self.vertex = _FakeVertex()

    def analyze(self, question: str) -> Any:
        self.vertex.calls += 1
        self.vertex.tokens += 123
        return a5.RetrievalPlan.model_validate(self.plans_by_question[question])


def _phase_p_question_index() -> dict[str, str]:
    gold = load_gold_dataset(_REPO_ROOT / a5.GOLD_QUESTIONS_PATH)
    novel = load_gold_dataset(_REPO_ROOT / a5.NOVEL_DEV_PATH)
    return {
        q.query: q.id
        for q in gold.questions + novel.questions
        if q.id in a5.CASE_ORDER
    }


def _fake_plans_all_inactive(questions: dict[str, str]) -> dict[str, dict[str, Any]]:
    plans: dict[str, dict[str, Any]] = {}
    for question, cid in questions.items():
        matched_batch1 = ["restgas_profile_workflow"] if cid == "g052" else []
        matched_batch2 = list(a5.CASE_ATTRIBUTION[cid]["matched_retirement_rules"])
        plans[question] = _synthetic_canonical_plan(
            matched_batch1 + matched_batch2, [], {}
        )
    return plans


def _real_query_expansions() -> Any:
    from panda_agent.config import load_query_expansions

    return load_query_expansions(_REPO_ROOT / a5.CONFIG_QUERY_EXPANSIONS_PATH)


def _real_dataset_loader(path: Path):
    name = Path(path).name
    real = a5.GOLD_QUESTIONS_PATH if name == "gold_questions.yaml" else a5.NOVEL_DEV_PATH
    return load_gold_dataset(_REPO_ROOT / real)


def _prepare_tmp_continuation(tmp_path: Path) -> Path:
    reuse_audit = a5.audit_historical_plan_reusability(_REPO_ROOT)
    manifest = a5.build_continuation_manifest(_REPO_ROOT, reuse_audit)
    (tmp_path / "evaluation").mkdir(parents=True, exist_ok=True)
    a5._save_json(tmp_path / a5.CONTINUATION_MANIFEST_PATH, manifest)
    return tmp_path


def _patch_phase_p_env(monkeypatch, fake: _FakeRetriever) -> None:
    monkeypatch.setattr(
        a5, "verify_continuation_start", lambda *_a, **_k: {"head": "r2fake", "parent": "r1fake"}
    )
    monkeypatch.setattr(a5, "Retriever", lambda *_a, **_k: fake)
    monkeypatch.setattr(a5, "load_gold_dataset", _real_dataset_loader)


def test_r1_27_28_phase_p_persists_before_gate_and_preserves_accounting(
    tmp_path, monkeypatch
):
    """A gate-stopped acquisition must leave a durable record with full provider
    accounting written BEFORE the gate raises (Sections 16/27/28-27/28)."""
    project = _prepare_tmp_continuation(tmp_path)
    questions = _phase_p_question_index()
    # g052 plan contains a masked symbol the (stripped) selected rule did not
    # contribute and no delta origin exists -> empty provenance -> AMBIGUOUS.
    plans = _fake_plans_all_inactive(questions)
    plans[next(q for q, c in questions.items() if c == "g052")] = _synthetic_canonical_plan(
        ["restgas_profile_workflow", "effective_acceptance_pipeline"],
        ["data/PndLmdAcceptance.cxx"],
    )
    fake = _FakeRetriever(plans, _FakeQueryExpansions(_real_query_expansions(), stripped=True))
    _patch_phase_p_env(monkeypatch, fake)

    with pytest.raises(RuntimeError, match="applicability gate STOPPED after durable persistence"):
        a5.execute_phase_p(project)

    artifact = json.loads(
        (project / a5.CONTINUATION_RAW_PLANS_PATH).read_text(encoding="utf-8")
    )
    assert artifact["plans_recorded"] == 1
    record = artifact["plans"][0]
    assert record["case_id"] == "g052"
    assert record["status"] == "GATE_STOPPED_AMBIGUOUS_INVALID"
    # Provider accounting survived the gate stop.
    assert record["provider_accounting"]["analyzer_logical_calls"] == 1
    assert record["provider_accounting"]["token_usage"] == 123
    assert artifact["accounting"]["analyzer_calls"] == 1
    assert artifact["accounting"]["token_usage"] == 123
    manifest = json.loads(
        (project / a5.CONTINUATION_MANIFEST_PATH).read_text(encoding="utf-8")
    )
    slot = manifest["phase_p_slots_7"][0]
    assert slot["status"] == "GATE_STOPPED_AMBIGUOUS_INVALID"
    assert slot["token_usage"] == 123


def test_r1_27b_phase_p_completes_with_inactive_components_hold(tmp_path, monkeypatch):
    """When every configured component is INACTIVE_NOT_IDENTIFIABLE the run
    completes: no ambiguity, projections equal canonical, receipts recorded
    as HOLD."""
    project = _prepare_tmp_continuation(tmp_path)
    questions = _phase_p_question_index()
    plans = _fake_plans_all_inactive(questions)
    fake = _FakeRetriever(plans, _FakeQueryExpansions(_real_query_expansions(), stripped=True))
    _patch_phase_p_env(monkeypatch, fake)

    artifact = a5.execute_phase_p(project)

    assert artifact["plans_completed"] == 7
    assert artifact["plans_gate_stopped"] == 0
    assert artifact["accounting"]["analyzer_calls"] == 7
    assert artifact["accounting"]["token_usage"] == 7 * 123
    by_case = {r["case_id"]: r for r in artifact["plans"]}
    g052 = by_case["g052"]
    assert g052["component_applicability_summary"] == {"active": 0, "inactive": 3, "ambiguous": 0}
    assert all(
        r["applicability_status"] == a5.APPLICABILITY_INACTIVE
        for r in g052["component_applicability_receipts"]
    )
    assert g052["batch2_retirement_execution_projection"] == g052["canonical_plan"]
    n014 = by_case["n014"]
    assert n014["component_applicability_summary"] == {"active": 0, "inactive": 6, "ambiguous": 0}


def test_r1_29_30_reuse_requires_complete_plan_not_signature_alone(tmp_path):
    manifest = a5.build_initial_manifest(_REPO_ROOT)
    (tmp_path / "evaluation").mkdir(parents=True, exist_ok=True)
    # Case A: signature-only slot (as the real stopped manifest has).
    manifest["phase_p_slots_7"][0].update({
        "status": "COMPLETED", "plan_signature": {"intent": "x"}, "token_usage": 100,
    })
    # Case B: slot pretending a complete frozen record exists.
    manifest["phase_p_slots_7"][1].update({
        "status": "COMPLETED", "plan_signature": {"intent": "y"}, "token_usage": 100,
        "canonical_plan": {"intent": "y"},
        "canonical_serialization": "{}",
        "contribution_ledger": [],
        "provenance_origin_receipts": [],
        "current_compat_execution_projection": {},
        "batch2_retirement_execution_projection": {},
        "provider_accounting": {"analyzer_logical_calls": 1},
    })
    a5._save_json(tmp_path / a5.HISTORICAL_MANIFEST_PATH, manifest)
    audit = a5.audit_historical_plan_reusability(tmp_path)
    assert audit["per_case"]["g052"]["classification"] == a5.REUSE_NOT_REUSABLE
    assert "plan_signature" in audit["per_case"]["g052"]["reason"]
    assert audit["per_case"]["g055"]["classification"] == a5.REUSE_REUSABLE
    assert audit["per_case"]["g055"]["reacquisition_required"] is False
    # A signature alone never qualifies: strip the complete record -> not reusable.
    manifest["phase_p_slots_7"][1].pop("canonical_plan")
    a5._save_json(tmp_path / a5.HISTORICAL_MANIFEST_PATH, manifest)
    audit = a5.audit_historical_plan_reusability(tmp_path)
    assert audit["per_case"]["g055"]["classification"] == a5.REUSE_NOT_REUSABLE


def test_r1_31_historical_and_continuation_accounting_kept_separate():
    historical = a5.HISTORICAL_ATTEMPT_ACCOUNTING
    assert historical["analyzer_logical_calls"] == 6
    assert historical["analyzer_provider_attempts"] == 6
    assert historical["recorded_token_usage"] == 10303
    assert historical["unknown_token_usage"]["case_id"] == "n014"
    reuse_audit = a5.audit_historical_plan_reusability(_REPO_ROOT)
    manifest = a5.build_continuation_manifest(_REPO_ROOT, reuse_audit)
    accounting = manifest["attempt_accounting"]
    assert accounting["historical_attempt"] == historical
    assert accounting["continuation_attempt"]["analyzer_logical_calls"] == 0
    assert accounting["cumulative"]["analyzer_logical_calls"] == 6
    assert accounting["cumulative"]["token_usage_recorded"] == 10303
    assert accounting["cumulative"]["token_usage_unknown_components"] == 1


def test_r1_32_reuse_audit_performs_zero_provider_calls(monkeypatch):
    def _forbidden(*_a: Any, **_k: Any) -> None:
        raise AssertionError("No provider construction is allowed in R1 flows")

    monkeypatch.setattr(a5, "Retriever", _forbidden)
    audit = a5.audit_historical_plan_reusability(_REPO_ROOT)
    assert set(audit["reusable_cases"]) == set()
    assert len(audit["non_reusable_cases"]) == 6
    assert audit["never_executed_cases"] == ["g060"]


# ===========================================================================
# D4-A5-R2 — Continuation Freeze and Accounting Contract Repair tests
# ===========================================================================


def _git(tmp_path: Path, *args: str, cwd: Path | None = None) -> str:
    import subprocess

    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd or tmp_path),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {args} failed: {proc.stderr}")
    return proc.stdout.strip()


def _temp_repo_commit(tmp_path: Path, files: dict[str, str], message: str) -> str:
    for rel, content in files.items():
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", message)
    return _git(tmp_path, "rev-parse", "HEAD")


@pytest.fixture()
def continuation_git_repo(tmp_path, monkeypatch):
    """Temporary Git repository exercising the REAL continuation-start gate
    logic (expected-SHA constants are remapped to local fixture SHAs; the gate
    itself is never monkeypatched). Chain: base(R1) -> R2 -> R3 freeze."""
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    r1_sha = _temp_repo_commit(tmp_path, {"base.txt": "base"}, "base commit")
    monkeypatch.setattr(a5, "R1_HEAD", r1_sha)
    monkeypatch.setattr(a5, "A5_STOP_HEAD", r1_sha)
    monkeypatch.setattr(a5, "STARTING_HEAD", r1_sha)
    r2_sha = _temp_repo_commit(tmp_path, {"r2.txt": "r2"}, a5.R2_COMMIT_MESSAGE)
    monkeypatch.setattr(a5, "R2_HEAD", r2_sha)
    _temp_repo_commit(tmp_path, {"r3.txt": "r3"}, a5.R3_COMMIT_MESSAGE)
    r3_sha = _git(tmp_path, "rev-parse", "HEAD")
    monkeypatch.setattr(a5, "R3_HEAD", r3_sha)
    manifest = a5.build_continuation_manifest(_REPO_ROOT, a5.audit_historical_plan_reusability(_REPO_ROOT))
    r5_sha = _temp_repo_commit(
        tmp_path,
        {a5.CONTINUATION_MANIFEST_PATH: json.dumps(manifest, ensure_ascii=False, indent=2)},
        a5.R5_COMMIT_MESSAGE,
    )
    return tmp_path, r1_sha, r2_sha, r3_sha, r5_sha


def test_r2_02_clean_r2_head_passes_continuation_start(continuation_git_repo):
    tmp_path, r1_sha, r2_sha, r3_sha, r5_sha = continuation_git_repo
    receipt = a5.verify_continuation_start(tmp_path)
    assert receipt["head"] == r5_sha
    assert receipt["parent"] == r3_sha
    assert receipt["manifest_contract_matches_runner"] is True
    assert receipt["provider_calls"] == 0
    assert receipt["continuation_state"] == "NOT_STARTED"


def test_r2_03_uncommitted_drift_fails(continuation_git_repo):
    tmp_path, *_ = continuation_git_repo
    (tmp_path / "stray.txt").write_text("drift", encoding="utf-8")
    with pytest.raises(RuntimeError, match="not clean"):
        a5.verify_continuation_start(tmp_path)


def test_r2_04_descendant_head_fails(continuation_git_repo):
    tmp_path, *_ = continuation_git_repo
    _temp_repo_commit(tmp_path, {"later.txt": "later"}, "later commit")
    with pytest.raises(RuntimeError, match="R5 implementation-freeze commit"):
        a5.verify_continuation_start(tmp_path)


def test_r2_05_wrong_direct_parent_fails(tmp_path, monkeypatch):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    base = _temp_repo_commit(tmp_path, {"base.txt": "base"}, "base commit")
    _temp_repo_commit(tmp_path, {"r2.txt": "r2"}, a5.R2_COMMIT_MESSAGE)
    _temp_repo_commit(tmp_path, {"r3.txt": "r3"}, a5.R3_COMMIT_MESSAGE)
    manifest = a5.build_continuation_manifest(_REPO_ROOT, a5.audit_historical_plan_reusability(_REPO_ROOT))
    _temp_repo_commit(
        tmp_path,
        {a5.CONTINUATION_MANIFEST_PATH: json.dumps(manifest, ensure_ascii=False, indent=2)},
        a5.R5_COMMIT_MESSAGE,
    )
    # Point the expected R3 parent at a nonexistent commit so the mechanical
    # parent check (not the message check) is what fires.
    monkeypatch.setattr(a5, "R1_HEAD", base)
    monkeypatch.setattr(a5, "A5_STOP_HEAD", base)
    monkeypatch.setattr(a5, "STARTING_HEAD", base)
    monkeypatch.setattr(a5, "R2_HEAD", _git(tmp_path, "rev-parse", "HEAD~2"))
    monkeypatch.setattr(a5, "R3_HEAD", "0" * 40)
    with pytest.raises(RuntimeError, match="parent must be"):
        a5.verify_continuation_start(tmp_path)


def test_r2_06_wrong_r2_commit_message_fails(continuation_git_repo):
    tmp_path, *_ = continuation_git_repo
    # Amend the R3 freeze commit with a wrong message; the gate must reject it.
    _git(tmp_path, "commit", "-q", "--amend", "-m", "wrong message")
    with pytest.raises(RuntimeError, match="R5 implementation-freeze commit"):
        a5.verify_continuation_start(tmp_path)


def test_r2_07_missing_committed_manifest_fails(tmp_path, monkeypatch):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    r1_sha = _temp_repo_commit(tmp_path, {"base.txt": "base"}, "base commit")
    _temp_repo_commit(tmp_path, {"r2.txt": "x"}, a5.R2_COMMIT_MESSAGE)
    _temp_repo_commit(tmp_path, {"r3.txt": "x"}, a5.R3_COMMIT_MESSAGE)
    _temp_repo_commit(tmp_path, {"other.txt": "x"}, a5.R5_COMMIT_MESSAGE)
    monkeypatch.setattr(a5, "R1_HEAD", r1_sha)
    monkeypatch.setattr(a5, "A5_STOP_HEAD", r1_sha)
    monkeypatch.setattr(a5, "STARTING_HEAD", r1_sha)
    monkeypatch.setattr(a5, "R2_HEAD", _git(tmp_path, "rev-parse", "HEAD~2"))
    monkeypatch.setattr(a5, "R3_HEAD", _git(tmp_path, "rev-parse", "HEAD~1"))
    with pytest.raises(RuntimeError, match="not committed at HEAD"):
        a5.verify_continuation_start(tmp_path)


def test_r2_08_protected_historical_drift_fails(tmp_path, monkeypatch):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    r1_sha = _temp_repo_commit(
        tmp_path, {a5.RESULT_PATH: '{"verdict": "historical"}'}, "base commit"
    )
    monkeypatch.setattr(a5, "R1_HEAD", r1_sha)
    monkeypatch.setattr(a5, "A5_STOP_HEAD", r1_sha)
    monkeypatch.setattr(a5, "STARTING_HEAD", r1_sha)
    r2_sha = _temp_repo_commit(tmp_path, {"r2.txt": "r2"}, a5.R2_COMMIT_MESSAGE)
    monkeypatch.setattr(a5, "R2_HEAD", r2_sha)
    _temp_repo_commit(tmp_path, {"r3.txt": "r3"}, a5.R3_COMMIT_MESSAGE)
    monkeypatch.setattr(a5, "R3_HEAD", _git(tmp_path, "rev-parse", "HEAD"))
    manifest = a5.build_continuation_manifest(_REPO_ROOT, a5.audit_historical_plan_reusability(_REPO_ROOT))
    _temp_repo_commit(
        tmp_path,
        {
            a5.CONTINUATION_MANIFEST_PATH: json.dumps(manifest, ensure_ascii=False, indent=2),
            a5.RESULT_PATH: '{"verdict": "rewritten"}',
        },
        a5.R5_COMMIT_MESSAGE,
    )
    with pytest.raises(RuntimeError, match="Historical A5 attempt artifacts"):
        a5.verify_continuation_start(tmp_path)


def test_r2_01_real_manifest_committed_in_r2_freeze_commit():
    """Real-repo bootstrap contract: the committed continuation manifest was
    introduced by the R2 freeze commit and matches runner constants."""
    assert a5.verify_freeze is not None  # module sanity
    head_blob = a5.git_blob(_REPO_ROOT, a5.CONTINUATION_MANIFEST_PATH, "HEAD")
    assert head_blob is not None, "continuation manifest must be committed"
    parent_blob = a5.git_blob(
        _REPO_ROOT, a5.CONTINUATION_MANIFEST_PATH, a5.R1_HEAD
    )
    assert parent_blob is None, "manifest must be introduced by the R2 commit"
    last_touch = _git(
        _REPO_ROOT, "log", "-1", "--format=%s", "--", a5.CONTINUATION_MANIFEST_PATH
    )
    assert last_touch == a5.R5_COMMIT_MESSAGE
    manifest = json.loads(
        (_REPO_ROOT / a5.CONTINUATION_MANIFEST_PATH).read_text(encoding="utf-8")
    )
    assert manifest["implementation_freeze_contract"]["expected_commit_message"] == (
        a5.R5_COMMIT_MESSAGE
    )
    assert manifest["implementation_freeze_contract"]["expected_parent"] == a5.R3_HEAD
    assert manifest["continuation_lineage"]["historical_r1_head"] == a5.R1_HEAD
    assert manifest["continuation_lineage"]["historical_r2_head"] == a5.R2_HEAD
    assert manifest["continuation_lineage"]["historical_r3_head"] == a5.R3_HEAD
    assert manifest["continuation_lineage"][
        "continuation_implementation_freeze_message"
    ] == a5.R5_COMMIT_MESSAGE
    assert manifest["raw_freeze_gate_contract"]["strict_diff_allowlist"] == list(
        a5.RAW_FREEZE_DIFF_ALLOWLIST
    )
    assert manifest["plan_freeze_gate_contract"]["expected_commit_message"] == (
        a5.CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE
    )
    assert manifest["raw_freeze_gate_contract"]["expected_commit_message"] == (
        a5.CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE
    )
    assert manifest["closeout_gate_contract"]["expected_commit_message"] == (
        a5.CONTINUATION_CLOSEOUT_COMMIT_MESSAGE
    )
    # The old first-attempt messages appear only as labeled historical references.
    assert manifest["historical_first_attempt_freeze_messages"]["status"].startswith(
        "HISTORICAL ONLY"
    )
    assert manifest["artifact_paths"]["raw_plans"] == a5.CONTINUATION_RAW_PLANS_PATH
    assert manifest["repair_lineage"]["r1_parent_boundary"] == a5.R1_HEAD
    decision = manifest["reusability_decision"]
    for key, expected in a5.CONTINUATION_EXPECTED_REUSABILITY.items():
        assert decision[key] == expected, key
    assert decision["signature_alone_insufficient"] is True


# --- Accounting (Sections 9/16-10..14) ---------------------------------------


def _fresh_manifest() -> dict[str, Any]:
    return a5.build_continuation_manifest(
        _REPO_ROOT, a5.audit_historical_plan_reusability(_REPO_ROOT)
    )


def test_r2_10_one_acquisition_updates_attempt_and_cumulative():
    manifest = _fresh_manifest()
    a5.apply_continuation_accounting(
        manifest, analyzer_calls=1, analyzer_attempts=1, token_usage=100
    )
    cont = manifest["attempt_accounting"]["continuation_attempt"]
    cumulative = manifest["attempt_accounting"]["cumulative"]
    assert cont["analyzer_logical_calls"] == 1
    assert cumulative["analyzer_logical_calls"] == 7  # historical 6 + continuation 1


def test_r2_11_seven_acquisitions_produce_cumulative_13():
    manifest = _fresh_manifest()
    for _ in range(7):
        a5.apply_continuation_accounting(
            manifest, analyzer_calls=1, analyzer_attempts=1, token_usage=10
        )
    cont = manifest["attempt_accounting"]["continuation_attempt"]
    cumulative = manifest["attempt_accounting"]["cumulative"]
    assert cont["analyzer_logical_calls"] == 7
    assert cumulative["analyzer_logical_calls"] == 13  # historical 6 + continuation 7


def test_r2_12_continuation_tokens_add_to_historical_recorded_tokens():
    manifest = _fresh_manifest()
    a5.apply_continuation_accounting(manifest, analyzer_calls=1, token_usage=250)
    cumulative = manifest["attempt_accounting"]["cumulative"]
    assert cumulative["token_usage_recorded"] == 10303 + 250
    assert manifest["attempt_accounting"]["historical_attempt"]["recorded_token_usage"] == 10303


def test_r2_13_historical_unknown_n014_tokens_stay_explicitly_unknown():
    manifest = _fresh_manifest()
    hist = manifest["attempt_accounting"]["historical_attempt"]
    assert hist["unknown_token_usage"]["case_id"] == "n014"
    assert hist["unknown_token_usage"]["note"]
    cumulative = manifest["attempt_accounting"]["cumulative"]
    assert cumulative["token_usage_unknown_components"] == 1
    # Unknown history is never silently collapsed into zero recorded tokens.
    assert cumulative["token_usage_recorded"] == 10303


def test_r2_14_reload_recompute_does_not_double_count():
    manifest = _fresh_manifest()
    for _ in range(3):
        a5.apply_continuation_accounting(
            manifest, analyzer_calls=1, analyzer_attempts=1, token_usage=33
        )
    serialized = json.dumps(manifest, ensure_ascii=False)
    reloaded = json.loads(serialized)
    cont = reloaded["attempt_accounting"]["continuation_attempt"]
    cumulative = reloaded["attempt_accounting"]["cumulative"]
    hist = reloaded["attempt_accounting"]["historical_attempt"]
    # Applying zero further events keeps every counter stable.
    a5.apply_continuation_accounting(reloaded)
    assert reloaded["attempt_accounting"]["continuation_attempt"] == cont
    assert reloaded["attempt_accounting"]["cumulative"] == cumulative
    # Cumulative remains the exact mechanical sum of the two layers.
    assert cumulative["analyzer_logical_calls"] == (
        hist["analyzer_logical_calls"] + cont["analyzer_logical_calls"]
    )
    assert cumulative["token_usage_recorded"] == (
        hist["recorded_token_usage"] + cont["token_usage"]
    )


# --- Provider-failure persistence (Sections 10/16-15..20) --------------------


class _ExplodingRetriever(_FakeRetriever):
    def __init__(self, qe: Any, fail_on_call: int = 1) -> None:
        super().__init__({}, qe)
        self._fail_on_call = fail_on_call
        self.call_count = 0

    def analyze(self, question: str) -> Any:
        self.call_count += 1
        self.vertex.calls += 1
        self.vertex.tokens += 123
        if self.call_count >= self._fail_on_call:
            raise RuntimeError("simulated provider transport failure")
        return a5.RetrievalPlan.model_validate(self.plans_by_question[question])


def test_r2_15_20_provider_failure_persists_receipt_and_stops(tmp_path, monkeypatch):
    project = _prepare_tmp_continuation(tmp_path)
    questions = _phase_p_question_index()
    plans = _fake_plans_all_inactive(questions)
    fake = _ExplodingRetriever(_FakeQueryExpansions(_real_query_expansions(), stripped=True))
    fake.plans_by_question = plans
    _patch_phase_p_env(monkeypatch, fake)

    with pytest.raises(RuntimeError, match="provider call failed"):
        a5.execute_phase_p(project)

    # No retry: exactly one analyze call was made.
    assert fake.call_count == 1
    artifact = json.loads(
        (project / a5.CONTINUATION_RAW_PLANS_PATH).read_text(encoding="utf-8")
    )
    assert artifact["plans_provider_failed"] == 1
    record = artifact["plans"][0]
    assert record["status"] == "PROVIDER_FAILED"
    receipt = record["provider_failure_receipt"]
    assert receipt["retries_performed"] == 0
    assert receipt["retry_policy"] == {"max_retries": 0, "max_provider_attempts_per_case": 1}
    assert receipt["exception_type"] == "RuntimeError"
    # Available provider accounting is preserved, not fabricated.
    assert record["provider_accounting"]["analyzer_provider_attempts"] == 1
    assert record["provider_accounting"]["token_usage"] == 123
    assert record["provider_accounting"]["token_usage_unknown"] is False
    # Terminal slot state is explicit, not an ambiguous STARTED.
    manifest = json.loads(
        (project / a5.CONTINUATION_MANIFEST_PATH).read_text(encoding="utf-8")
    )
    slot = manifest["phase_p_slots_7"][0]
    assert slot["status"] == "PROVIDER_FAILED"
    assert slot["token_usage"] == 123
    # The continuation stopped: only the failed slot was processed.
    assert len(artifact["plans"]) == 1
    # Attempt-local and cumulative accounting were updated exactly once.
    cont = manifest["attempt_accounting"]["continuation_attempt"]
    assert cont["analyzer_provider_attempts"] == 1
    assert cont["token_usage"] == 123
    # A failed-but-invoked Analyzer acquisition counts as ONE logical acquisition.
    assert cont["analyzer_logical_calls"] == 1
    assert cont["unknown_provider_attempt_events"] == 0
    cumulative = manifest["attempt_accounting"]["cumulative"]
    assert cumulative["analyzer_provider_attempts"] == 7  # historical 6 + continuation 1
    assert cumulative["analyzer_logical_calls"] == 7  # historical 6 + continuation 1
    assert cumulative["token_usage_recorded"] == 10303 + 123
    assert cumulative["provider_attempt_unknown_components"] == 0


def test_r2_15b_provider_failure_with_unavailable_stats_marks_unknown(
    tmp_path, monkeypatch
):
    project = _prepare_tmp_continuation(tmp_path)
    questions = _phase_p_question_index()
    plans = _fake_plans_all_inactive(questions)

    class _BrokenStatsVertex(_FakeVertex):
        def stats_delta(self, previous: dict[str, int]) -> dict[str, int]:
            raise RuntimeError("stats unavailable")

    fake = _ExplodingRetriever(_FakeQueryExpansions(_real_query_expansions(), stripped=True))
    fake.plans_by_question = plans
    fake.vertex = _BrokenStatsVertex()
    _patch_phase_p_env(monkeypatch, fake)

    with pytest.raises(RuntimeError, match="provider call failed"):
        a5.execute_phase_p(project)

    artifact = json.loads(
        (project / a5.CONTINUATION_RAW_PLANS_PATH).read_text(encoding="utf-8")
    )
    record = artifact["plans"][0]
    receipt = record["provider_failure_receipt"]
    assert receipt["provider_attempts_recoverable"] is False
    assert receipt["provider_attempts"] == "unknown"
    assert receipt["token_usage"] == "unknown"
    assert record["provider_accounting"]["token_usage_unknown"] is True
    manifest = json.loads(
        (project / a5.CONTINUATION_MANIFEST_PATH).read_text(encoding="utf-8")
    )
    slot = manifest["phase_p_slots_7"][0]
    assert slot["attempts"] == "unknown"
    assert slot["token_usage"] == "unknown"
    cont = manifest["attempt_accounting"]["continuation_attempt"]
    assert cont["unknown_token_usage_events"] == 1
    assert cont["unknown_provider_attempt_events"] == 1
    # The failed invocation still counts one logical Analyzer acquisition, but
    # the unknown provider attempts never pretend to be a known numeric zero.
    assert cont["analyzer_logical_calls"] == 1
    assert cont["analyzer_provider_attempts"] == 0
    cumulative = manifest["attempt_accounting"]["cumulative"]
    assert cumulative["token_usage_unknown_components"] == 2
    assert cumulative["provider_attempt_unknown_components"] == 1
    assert cumulative["analyzer_logical_calls"] == 7


# --- R1 scientific logic unchanged (Sections 7/16-21..23) --------------------


def test_r2_21_applicability_semantics_unchanged():
    assert a5.APPLICABILITY_STATUSES == (
        "ACTIVE_IDENTIFIABLE", "INACTIVE_NOT_IDENTIFIABLE", "AMBIGUOUS_INVALID",
    )
    plan = _synthetic_canonical_plan(
        matched_rules=["root_macro_usage"], symbols=_full_mask_symbols("root_macro_usage")
    )
    ledger = _ledger_for(plan, ["root_macro_usage"])
    entries = a5.build_batch2_mask_entries("n004", ["root_macro_usage"])
    receipts, summary = a5.classify_component_applicability(plan, ledger, entries)
    assert summary == {"active": 2, "inactive": 0, "ambiguous": 0}
    # INACTIVE-by-absence semantics unchanged.
    empty_plan = _synthetic_canonical_plan(matched_rules=["root_macro_usage"], symbols=[])
    receipts2, summary2 = a5.classify_component_applicability(
        empty_plan, _ledger_for(empty_plan, ["root_macro_usage"]), entries
    )
    assert summary2 == {"active": 0, "inactive": 2, "ambiguous": 0}


def test_r2_22_partial_applicability_still_blocks_full_batch2_pass():
    assert a5.classify_rule_r1(
        protocol_valid=True, baseline_reproduced=True, attributable_loss=False,
        active_component_count=2, frozen_component_count=3,
    ) == a5.DISPOSITION_PARTIAL_COMPONENT_HOLD
    dispositions = {
        "effective_acceptance_pipeline": a5.DISPOSITION_RETIREMENT_VALIDATED,
        "root_macro_usage": a5.DISPOSITION_RETIREMENT_VALIDATED,
        "model_factory_theory": a5.DISPOSITION_PARTIAL_COMPONENT_HOLD,
    }
    verdict = a5.evaluate_batch2_verdict_r1(
        execution_valid=True, protocol_violation=False, missing_inputs=False,
        plan_equality_all_verified=True, analyzer_provider_calls_downstream=0,
        reference_baseline_valid=True, per_rule_dispositions=dispositions,
        critical_retirement_regressions=0, grounding_regressions=0,
        wrong_version_regressions=0, invalid_provenance_recoveries=0,
        metric_deltas={k: 0.0 for k in a5.DEFAULT_METRIC_TOLERANCES_KEYS},
    )
    assert verdict["verdict_level"] == 5
    assert verdict["verdict_status"] == "PARTIAL"


def test_r2_23_no_case_specific_shortcut_in_r2_code():
    import inspect

    for func in (a5.verify_continuation_start, a5.apply_continuation_accounting):
        lowered = inspect.getsource(func).casefold()
        assert "n014" not in lowered, func.__name__
        assert "pflueger" not in lowered, func.__name__
        assert "model_factory_theory" not in lowered, func.__name__
        assert "g052" not in lowered, func.__name__
    # The manifest builder may name cohort ids only inside the frozen reusability
    # decision; it must never reference mask component values.
    lowered = inspect.getsource(a5.build_continuation_manifest).casefold()
    assert "pflueger" not in lowered
    assert "symbols_retired" not in lowered
    assert "paper_page_hints_retired" not in lowered


def test_r2_24_frozen_scientific_constants_unchanged():
    assert list(b2.CANDIDATE_RULE_IDS) == [
        "effective_acceptance_pipeline", "root_macro_usage", "model_factory_theory",
    ]
    assert b2.FROZEN_RETIREMENT_MASKS["model_factory_theory"]["paper_page_hints_retired"] == {
        "pflueger_2017": [51, 57, 65]
    }
    assert a5.CASE_ORDER == ["g052", "g055", "n003", "n004", "g007", "n014", "g060"]
    assert len(a5.SCHEDULE_14) == 14
    assert a5.R1_PER_RULE_DISPOSITIONS == (
        "INVALID_PROTOCOL", "DEPENDENCY_OBSERVED_RETAIN",
        "INCONCLUSIVE_BASELINE_NOT_REPRODUCED",
        "INCONCLUSIVE_NO_ACTIVE_RETIREMENT_COMPONENT",
        "PARTIAL_RETIREMENT_VALIDATED_COMPONENT_HOLD", "RETIREMENT_VALIDATED",
    )
    assert a5.R1_BATCH_VERDICT_LEVELS[5] == (
        "PARTIAL / RETIREMENT_COMPONENT_APPLICABILITY_INCOMPLETE"
    )
    assert a5.R1_BATCH_VERDICT_LEVELS[7] == "PASS / SECOND_BATCH_LOW_RISK_RETIREMENT_VALIDATED"


# ===========================================================================
# D4-A5-R3 — Continuation Lineage and End-to-End Accounting tests
# ===========================================================================


def test_r3_07_phase_p_writes_r3_lineage_not_stale_heads(tmp_path, monkeypatch):
    """Phase P must freeze continuation_implementation_freeze_head from the
    preflight receipt and must not write misleading current r1/r2 freeze heads."""
    project = _prepare_tmp_continuation(tmp_path)
    questions = _phase_p_question_index()
    plans = _fake_plans_all_inactive(questions)
    fake = _FakeRetriever(plans, _FakeQueryExpansions(_real_query_expansions(), stripped=True))
    monkeypatch.setattr(
        a5, "verify_continuation_start",
        lambda *_a, **_k: {"head": "r3fake", "parent": "r2fake", "message": a5.R3_COMMIT_MESSAGE},
    )
    monkeypatch.setattr(a5, "Retriever", lambda *_a, **_k: fake)
    monkeypatch.setattr(a5, "load_gold_dataset", _real_dataset_loader)

    a5.execute_phase_p(project)

    manifest = json.loads(
        (project / a5.CONTINUATION_MANIFEST_PATH).read_text(encoding="utf-8")
    )
    exposure = manifest["outcome_exposure_state"]
    assert exposure["continuation_implementation_freeze_head"] == "r3fake"
    assert "r1_freeze_head" not in exposure
    assert "r2_freeze_head" not in exposure


def test_r3_08_no_current_gate_depends_on_stale_r1_lineage():
    import inspect

    for func in (
        a5.execute_phase_r,
        a5.evaluate_d4_a5,
        a5.verify_phase_r_preflight,
        a5.verify_continuation_plan_freeze_gate,
        a5.verify_continuation_start,
    ):
        source = inspect.getsource(func)
        assert '.get("r1_freeze_head")' not in source, func.__name__
        assert 'r1_freeze_head = ' not in source, func.__name__
        assert 'freeze["r1_freeze_head"]' not in source, func.__name__


def _synthetic_completed_plans_artifact() -> dict[str, Any]:
    plans = []
    for cid in a5.CASE_ORDER:
        plans.append({
            "plan_id": f"prospective_{cid}",
            "case_id": cid,
            "canonical_plan": {"intent": "algorithm_theory", "synthetic": cid},
            "provenance_gate": {"pass": True},
            "status": "COMPLETED",
            "provider_accounting": {"analyzer_logical_calls": 1},
        })
    return {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5-CONTINUATION",
        "plans_planned": 7,
        "plans_completed": 7,
        "plans_failed": 0,
        "plan_freeze_state": "PLANS_FROZEN",
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED": True,
        "plans": plans,
    }


def test_r3_09_10_synthetic_handoff_plan_freeze_then_phase_r_preflight(
    tmp_path, monkeypatch
):
    """Real-lineage synthetic flow: clean R3 freeze -> completed Phase-P state ->
    continuation plan-freeze commit -> plan-freeze gate -> Phase-R preflight.
    Phase R consumes continuation_implementation_freeze_head; no stale
    r1_freeze_head is required. No provider or retrieval call occurs."""
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    r1_sha = _temp_repo_commit(tmp_path, {"base.txt": "base"}, "base commit")
    monkeypatch.setattr(a5, "R1_HEAD", r1_sha)
    monkeypatch.setattr(a5, "A5_STOP_HEAD", r1_sha)
    monkeypatch.setattr(a5, "STARTING_HEAD", r1_sha)
    r2_sha = _temp_repo_commit(tmp_path, {"r2.txt": "r2"}, a5.R2_COMMIT_MESSAGE)
    monkeypatch.setattr(a5, "R2_HEAD", r2_sha)
    _temp_repo_commit(tmp_path, {"r3.txt": "r3"}, a5.R3_COMMIT_MESSAGE)
    r3_sha = _git(tmp_path, "rev-parse", "HEAD")
    monkeypatch.setattr(a5, "R3_HEAD", r3_sha)

    manifest = a5.build_continuation_manifest(_REPO_ROOT, a5.audit_historical_plan_reusability(_REPO_ROOT))
    r5_sha = _temp_repo_commit(
        tmp_path,
        {a5.CONTINUATION_MANIFEST_PATH: json.dumps(manifest, ensure_ascii=False, indent=2)},
        a5.R5_COMMIT_MESSAGE,
    )

    # Simulate a completed 7-plan Phase-P state and freeze it as a direct child
    # of the R5 implementation freeze.
    manifest["outcome_exposure_state"]["D4_A5_OUTCOME_EXPOSURE"] = "PLANS_FROZEN"
    plan_freeze_sha = _temp_repo_commit(
        tmp_path,
        {
            a5.CONTINUATION_MANIFEST_PATH: json.dumps(manifest, ensure_ascii=False, indent=2),
            a5.CONTINUATION_RAW_PLANS_PATH: json.dumps(
                _synthetic_completed_plans_artifact(), ensure_ascii=False, indent=2
            ),
        },
        a5.CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE,
    )
    assert _git(tmp_path, "rev-parse", f"{plan_freeze_sha}^") == r5_sha

    preflight = a5.verify_phase_r_preflight(tmp_path, r5_sha)
    assert preflight["continuation_implementation_freeze_head"] == r5_sha
    assert preflight["continuation_plan_freeze_head"] == plan_freeze_sha
    gate = a5.verify_continuation_plan_freeze_gate(tmp_path, r5_sha)
    assert gate["continuation_plan_freeze_head"] == plan_freeze_sha


def test_r3_11_wrong_plan_freeze_parent_fails(tmp_path, monkeypatch):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    r1_sha = _temp_repo_commit(tmp_path, {"base.txt": "base"}, "base commit")
    monkeypatch.setattr(a5, "R1_HEAD", r1_sha)
    monkeypatch.setattr(a5, "A5_STOP_HEAD", r1_sha)
    monkeypatch.setattr(a5, "STARTING_HEAD", r1_sha)
    r2_sha = _temp_repo_commit(tmp_path, {"r2.txt": "r2"}, a5.R2_COMMIT_MESSAGE)
    monkeypatch.setattr(a5, "R2_HEAD", r2_sha)
    _temp_repo_commit(tmp_path, {"r3.txt": "r3"}, a5.R3_COMMIT_MESSAGE)
    r3_sha = _git(tmp_path, "rev-parse", "HEAD")
    monkeypatch.setattr(a5, "R3_HEAD", r3_sha)
    manifest = a5.build_continuation_manifest(_REPO_ROOT, a5.audit_historical_plan_reusability(_REPO_ROOT))
    r5_sha = _temp_repo_commit(
        tmp_path,
        {a5.CONTINUATION_MANIFEST_PATH: json.dumps(manifest, ensure_ascii=False, indent=2)},
        a5.R5_COMMIT_MESSAGE,
    )
    _temp_repo_commit(
        tmp_path,
        {
            a5.CONTINUATION_MANIFEST_PATH: json.dumps(manifest, ensure_ascii=False, indent=2),
            a5.CONTINUATION_RAW_PLANS_PATH: json.dumps(
                _synthetic_completed_plans_artifact(), ensure_ascii=False, indent=2
            ),
        },
        a5.CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE,
    )
    # A stale implementation-freeze input (e.g. the historical R1 or R3 head)
    # must not satisfy the plan-freeze gate: the actual parent is the R5 freeze.
    with pytest.raises(RuntimeError, match="parent"):
        a5.verify_phase_r_preflight(tmp_path, r1_sha)
    with pytest.raises(RuntimeError, match="parent"):
        a5.verify_phase_r_preflight(tmp_path, r3_sha)


def test_r3_13_provenance_schemas_retain_historical_r1_r2_separately(tmp_path):
    freeze = {
        "continuation_implementation_freeze_head": "r3head",
        "head": "planfreezehead",
    }
    (tmp_path / "evaluation").mkdir(parents=True, exist_ok=True)
    artifact = a5._write_raw_results(
        tmp_path, [], freeze, 0, 0, 0, 0, final=False
    )
    assert artifact["historical_r1_head"] == a5.R1_HEAD
    assert artifact["historical_r2_head"] == a5.R2_HEAD
    assert artifact["historical_r3_head"] == a5.R3_HEAD
    assert artifact["continuation_implementation_freeze_head"] == "r3head"
    assert artifact["continuation_plan_freeze_head"] == "planfreezehead"
    assert artifact["historical_r1_head"] != artifact[
        "continuation_implementation_freeze_head"
    ]
    # The probe write landed in the temporary project only.
    assert not (_REPO_ROOT / a5.CONTINUATION_RAW_RESULTS_PATH).exists()
    import inspect

    source = inspect.getsource(a5.evaluate_d4_a5)
    for key in (
        "historical_a5_starting_head", "historical_a5_stop_head",
        "historical_r1_head", "historical_r2_head",
        "continuation_implementation_freeze_head",
        "continuation_plan_freeze_head", "continuation_raw_freeze_head",
    ):
        assert key in source


def test_r3_14_17_end_to_end_accounting_over_plans_and_cells():
    manifest = _fresh_manifest()
    # Seven successful Analyzer acquisitions.
    for _ in range(7):
        a5.apply_continuation_accounting(
            manifest, analyzer_calls=1, analyzer_attempts=1, token_usage=20
        )
    cont = manifest["attempt_accounting"]["continuation_attempt"]
    cumulative = manifest["attempt_accounting"]["cumulative"]
    assert cont["analyzer_logical_calls"] == 7
    assert cumulative["analyzer_logical_calls"] == 13  # historical 6 + continuation 7
    assert cumulative["token_usage_recorded"] == 10303 + 7 * 20
    # Fourteen synthetic retrieval cells with KNOWN recorded values.
    for _ in range(14):
        a5.apply_continuation_accounting(
            manifest,
            embedding_calls=1,
            reranker_calls=1,
            retrieval_provider_attempts=2,
            token_usage=10,
        )
    assert cont["embedding_calls"] == 14
    assert cont["reranker_calls"] == 14
    assert cont["retrieval_provider_attempts"] == 28
    assert cont["token_usage"] == 7 * 20 + 14 * 10
    # Historical embedding/reranker are 0, so cumulative equals continuation.
    assert cumulative["embedding_calls"] == 14
    assert cumulative["reranker_calls"] == 14
    assert cumulative["retrieval_provider_attempts"] == 28


def test_r3_18_19_reload_does_not_double_count_plans_or_cells():
    manifest = _fresh_manifest()
    for _ in range(7):
        a5.apply_continuation_accounting(
            manifest, analyzer_calls=1, analyzer_attempts=1, token_usage=5
        )
    for _ in range(14):
        a5.apply_continuation_accounting(
            manifest,
            embedding_calls=1, reranker_calls=1,
            retrieval_provider_attempts=2, token_usage=10,
        )
    before = json.dumps(manifest["attempt_accounting"], sort_keys=True)
    reloaded = json.loads(json.dumps(manifest))
    # Applying zero further events (the reload/restart path with all terminal
    # slot/cell states skipped) keeps every counter stable.
    a5.apply_continuation_accounting(reloaded)
    assert json.dumps(reloaded["attempt_accounting"], sort_keys=True) == before
    # Cumulative remains the deterministic function of the two layers.
    acct = reloaded["attempt_accounting"]
    assert acct["cumulative"]["analyzer_logical_calls"] == (
        acct["historical_attempt"]["analyzer_logical_calls"]
        + acct["continuation_attempt"]["analyzer_logical_calls"]
    )
    assert acct["cumulative"]["embedding_calls"] == (
        acct["historical_attempt"]["embedding_calls"]
        + acct["continuation_attempt"]["embedding_calls"]
    )


def test_r3_20_26_provider_failure_unknown_accounting_contract():
    # Known-attempts failure: one logical acquisition, known attempts numeric.
    manifest = _fresh_manifest()
    a5.apply_continuation_accounting(
        manifest,
        analyzer_calls=1,
        analyzer_attempts=1,
        unknown_provider_attempt_events=0,
        token_usage=123,
        unknown_token_events=0,
    )
    cont = manifest["attempt_accounting"]["continuation_attempt"]
    assert cont["analyzer_logical_calls"] == 1
    assert cont["analyzer_provider_attempts"] == 1
    assert cont["unknown_provider_attempt_events"] == 0
    cumulative = manifest["attempt_accounting"]["cumulative"]
    assert cumulative["analyzer_logical_calls"] == 7
    assert cumulative["provider_attempt_unknown_components"] == 0
    # Unknown-attempts failure: logical acquisition counts, the numeric attempt
    # total does NOT pretend the unknown value is zero-known, and the unknown
    # event is counted separately.
    a5.apply_continuation_accounting(
        manifest,
        analyzer_calls=1,
        analyzer_attempts=0,
        unknown_provider_attempt_events=1,
        token_usage=0,
        unknown_token_events=1,
    )
    assert cont["analyzer_logical_calls"] == 2
    assert cont["analyzer_provider_attempts"] == 1  # only the known attempt
    assert cont["unknown_provider_attempt_events"] == 1
    assert cont["unknown_token_usage_events"] == 1
    cumulative = manifest["attempt_accounting"]["cumulative"]
    assert cumulative["analyzer_logical_calls"] == 8
    assert cumulative["provider_attempt_unknown_components"] == 1
    assert cumulative["token_usage_unknown_components"] == 2
    assert cumulative["token_usage_recorded"] == 10303 + 123
    # Frozen retry policy unchanged.
    assert a5.MAX_PROVIDER_ATTEMPTS_PER_CASE == 1


def test_r3_31_no_benchmark_or_case_specific_shortcut_in_r3_code():
    import inspect

    for func in (
        a5.verify_phase_r_preflight,
        a5.verify_continuation_plan_freeze_gate,
        a5.apply_continuation_accounting,
    ):
        lowered = inspect.getsource(func).casefold()
        assert "n014" not in lowered, func.__name__
        assert "pflueger" not in lowered, func.__name__
        assert "g052" not in lowered, func.__name__
        assert "required_evidence" not in lowered, func.__name__


# ===========================================================================
# D4-A5-R5 — Raw-Freeze Evaluator Integrity Seal tests
# ===========================================================================


def _r5_synthetic_manifest() -> dict[str, Any]:
    return a5.build_continuation_manifest(
        _REPO_ROOT, a5.audit_historical_plan_reusability(_REPO_ROOT)
    )


def _r5_synthetic_raw_results(*, with_slots: bool) -> dict[str, Any]:
    artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5-CONTINUATION",
        "stage": "Phase R — Paired Shared-Plan Batch2 Retirement Retrieval (Continuation Attempt)",
        "attempt_id": "D4-A5_ATTEMPT_2_CONTINUATION",
        "starting_head": a5.STARTING_HEAD,
        "historical_a5_stop_head": a5.A5_STOP_HEAD,
        "historical_r1_head": a5.R1_HEAD,
        "historical_r2_head": a5.R2_HEAD,
        "historical_r3_head": a5.R3_HEAD,
        "continuation_implementation_freeze_head": "r5head",
        "continuation_plan_freeze_head": "planfreezehead",
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED": True,
        "PHASE_R_RETRIEVAL_EXECUTED": True,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "cells_planned": 14,
        "cells_completed": 14,
        "cells_failed": 0,
        "final": True,
        "model_contract": {
            "generation_model_id": a5.EXPECTED_MODEL,
            "embedding_model_id": a5.EXPECTED_EMBEDDING_MODEL,
            "temperature": a5.EXPECTED_TEMPERATURE,
            "location": a5.EXPECTED_VERTEX_LOCATION,
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
            "DB_WRITES": 0,
            "QDRANT_WRITES": 0,
            "INGESTION_RUNS": 0,
            "REINDEX_RUNS": 0,
            "NOVEL_VALIDATION_RUNS": 0,
            "NOVEL_HOLDOUT_RUNS": 0,
            "PROTECTED_DATASET_ACCESS": 0,
        },
        "authority": {"continuation_plan_freeze_head": "planfreezehead"},
        "slots": [],
    }
    if with_slots:
        for cell in a5.SCHEDULE_14:
            artifact["slots"].append({
                "cell_index": cell["cell_index"],
                "cell_id": cell["cell_id"],
                "case_id": cell["case_id"],
                "arm": cell["arm"],
                "status": "COMPLETED",
                "plan_equality_arm_projection_verified": True,
                "batch2_retirement_mask_applied": cell["batch2_retirement_mask_applied"],
                "channel_rankings": {"exact": ["obj::x"], "dense": ["obj::x"]},
                "ranked_object_ids": ["obj::x", "obj::y"],
                "final_evidence_object_ids": ["obj::x"],
                "final_evidence_entries": [{
                    "object_id": "obj::x", "source_id": "src_x",
                    "source_version_id": "ver_1", "locator": {},
                }],
                "provider_accounting": {
                    "analyzer_calls": 0, "embedding_calls": 1, "reranker_calls": 1,
                    "provider_internal_attempts": 2, "token_usage": 10,
                },
            })
    return artifact


def _r5_lifecycle_repo(tmp_path: Path, monkeypatch) -> tuple[Path, str, str, str]:
    """Synthetic Git lifecycle: base(R1) -> R2 -> R3 -> R5(manifest) ->
    plan-freeze(manifest PLANS_FROZEN + raw plans). Returns
    (tmp_path, r3_sha, r5_sha, plan_freeze_sha). Real gates, real Git."""
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    r1_sha = _temp_repo_commit(
        tmp_path,
        {"base.txt": "base", a5.PREREGISTRATION_PATH: "{}"},
        "base commit",
    )
    monkeypatch.setattr(a5, "R1_HEAD", r1_sha)
    monkeypatch.setattr(a5, "A5_STOP_HEAD", r1_sha)
    monkeypatch.setattr(a5, "STARTING_HEAD", r1_sha)
    _temp_repo_commit(tmp_path, {"r2.txt": "r2"}, a5.R2_COMMIT_MESSAGE)
    r3_sha = _temp_repo_commit(tmp_path, {"r3.txt": "r3"}, a5.R3_COMMIT_MESSAGE)
    monkeypatch.setattr(a5, "R2_HEAD", _git(tmp_path, "rev-parse", "HEAD~1"))
    monkeypatch.setattr(a5, "R3_HEAD", r3_sha)
    manifest = _r5_synthetic_manifest()
    r5_sha = _temp_repo_commit(
        tmp_path,
        {a5.CONTINUATION_MANIFEST_PATH: json.dumps(manifest, ensure_ascii=False, indent=2)},
        a5.R5_COMMIT_MESSAGE,
    )
    manifest["outcome_exposure_state"]["D4_A5_OUTCOME_EXPOSURE"] = "PLANS_FROZEN"
    manifest["outcome_exposure_state"]["continuation_implementation_freeze_head"] = r5_sha
    manifest["outcome_exposure_state"]["plan_freeze_head"] = "TO_BE_FILLED"
    plan_freeze_sha = _temp_repo_commit(
        tmp_path,
        {
            a5.CONTINUATION_MANIFEST_PATH: json.dumps(manifest, ensure_ascii=False, indent=2),
            a5.CONTINUATION_RAW_PLANS_PATH: json.dumps(
                _synthetic_completed_plans_artifact(), ensure_ascii=False, indent=2
            ),
        },
        a5.CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE,
    )
    manifest["outcome_exposure_state"]["plan_freeze_head"] = plan_freeze_sha
    manifest["outcome_exposure_state"]["D4_A5_OUTCOME_EXPOSURE"] = "RAW_RETRIEVAL_COMPLETE"
    # Rewrite the manifest with the real plan-freeze head before the raw freeze.
    (tmp_path / a5.CONTINUATION_MANIFEST_PATH).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return tmp_path, r3_sha, r5_sha, plan_freeze_sha


def _r5_raw_freeze_commit(
    tmp_path: Path, extra_files: dict[str, str] | None = None
) -> str:
    files = {
        a5.CONTINUATION_MANIFEST_PATH: (tmp_path / a5.CONTINUATION_MANIFEST_PATH).read_text(
            encoding="utf-8"
        ),
        a5.CONTINUATION_RAW_RESULTS_PATH: json.dumps(
            _r5_synthetic_raw_results(with_slots=False), ensure_ascii=False, indent=2
        ),
    }
    files.update(extra_files or {})
    return _temp_repo_commit(tmp_path, files, a5.CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE)


def test_r5_13a_valid_raw_freeze_passes_strict_allowlist(tmp_path, monkeypatch):
    tmp_path, r3_sha, r5_sha, plan_freeze_sha = _r5_lifecycle_repo(tmp_path, monkeypatch)
    raw_freeze_sha = _r5_raw_freeze_commit(tmp_path)
    receipt = a5.verify_continuation_raw_freeze_gate(tmp_path, plan_freeze_sha, r5_sha)
    assert receipt["continuation_raw_freeze_head"] == raw_freeze_sha
    assert receipt["plan_freeze_head"] == plan_freeze_sha
    assert receipt["raw_freeze_diff_allowlist_respected"] is True


def test_r5_13b_runner_mutation_in_raw_freeze_rejected(tmp_path, monkeypatch):
    tmp_path, r3_sha, r5_sha, plan_freeze_sha = _r5_lifecycle_repo(tmp_path, monkeypatch)
    runner = (_REPO_ROOT / a5.RUNNER_PATH).read_text(encoding="utf-8")
    _r5_raw_freeze_commit(tmp_path, {a5.RUNNER_PATH: runner + "\n# drifted\n"})
    with pytest.raises(RuntimeError, match="strict evaluator-integrity allowlist"):
        a5.verify_continuation_raw_freeze_gate(tmp_path, plan_freeze_sha, r5_sha)


def test_r5_13c_test_mutation_in_raw_freeze_rejected(tmp_path, monkeypatch):
    tmp_path, r3_sha, r5_sha, plan_freeze_sha = _r5_lifecycle_repo(tmp_path, monkeypatch)
    test_src = (_REPO_ROOT / a5.TEST_PATH).read_text(encoding="utf-8")
    _r5_raw_freeze_commit(tmp_path, {a5.TEST_PATH: test_src + "\n# drifted\n"})
    with pytest.raises(RuntimeError, match="strict evaluator-integrity allowlist"):
        a5.verify_continuation_raw_freeze_gate(tmp_path, plan_freeze_sha, r5_sha)


def test_r5_13d_raw_plan_mutation_in_raw_freeze_rejected(tmp_path, monkeypatch):
    tmp_path, r3_sha, r5_sha, plan_freeze_sha = _r5_lifecycle_repo(tmp_path, monkeypatch)
    plans = json.loads(
        (tmp_path / a5.CONTINUATION_RAW_PLANS_PATH).read_text(encoding="utf-8")
    )
    plans["plans"][0]["case_id"] = "g999"
    _r5_raw_freeze_commit(
        tmp_path,
        {a5.CONTINUATION_RAW_PLANS_PATH: json.dumps(plans, ensure_ascii=False, indent=2)},
    )
    with pytest.raises(RuntimeError, match="strict evaluator-integrity allowlist"):
        a5.verify_continuation_raw_freeze_gate(tmp_path, plan_freeze_sha, r5_sha)


def test_r5_13e_unrelated_file_in_raw_freeze_rejected(tmp_path, monkeypatch):
    tmp_path, r3_sha, r5_sha, plan_freeze_sha = _r5_lifecycle_repo(tmp_path, monkeypatch)
    _r5_raw_freeze_commit(tmp_path, {"notes.txt": "unrelated"})
    with pytest.raises(RuntimeError, match="strict evaluator-integrity allowlist"):
        a5.verify_continuation_raw_freeze_gate(tmp_path, plan_freeze_sha, r5_sha)


def test_r5_13f_wrong_raw_freeze_parent_rejected(tmp_path, monkeypatch):
    tmp_path, r3_sha, r5_sha, plan_freeze_sha = _r5_lifecycle_repo(tmp_path, monkeypatch)
    # Commit the raw results directly on top of the plan-freeze commit's SIBLING
    # (an intervening commit), so the raw-freeze commit is not the direct child
    # of the plan-freeze commit.
    intervening = _temp_repo_commit(tmp_path, {"between.txt": "x"}, "intervening commit")
    files = {
        a5.CONTINUATION_MANIFEST_PATH: (tmp_path / a5.CONTINUATION_MANIFEST_PATH).read_text(
            encoding="utf-8"
        ),
        a5.CONTINUATION_RAW_RESULTS_PATH: json.dumps(
            _r5_synthetic_raw_results(with_slots=False), ensure_ascii=False, indent=2
        ),
    }
    raw_freeze_sha = _temp_repo_commit(tmp_path, files, a5.CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE)
    assert _git(tmp_path, "rev-parse", f"{raw_freeze_sha}^") == intervening
    with pytest.raises(RuntimeError, match="parent"):
        a5.verify_continuation_raw_freeze_gate(tmp_path, plan_freeze_sha, r5_sha)


def test_r5_14a_evaluator_preflight_passes_on_valid_chain(tmp_path, monkeypatch):
    tmp_path, r3_sha, r5_sha, plan_freeze_sha = _r5_lifecycle_repo(tmp_path, monkeypatch)
    # Full 14-slot raw results so the structural validation also passes.
    (tmp_path / a5.CONTINUATION_MANIFEST_PATH).write_text(
        json.dumps(_r5_synthetic_manifest_updated_for_raw_freeze(plan_freeze_sha, r5_sha), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    files = {
        a5.CONTINUATION_MANIFEST_PATH: (tmp_path / a5.CONTINUATION_MANIFEST_PATH).read_text(
            encoding="utf-8"
        ),
        a5.CONTINUATION_RAW_RESULTS_PATH: json.dumps(
            _r5_synthetic_raw_results(with_slots=True), ensure_ascii=False, indent=2
        ),
    }
    raw_freeze_sha = _temp_repo_commit(tmp_path, files, a5.CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE)
    receipt = a5.verify_continuation_evaluator_preflight(tmp_path, plan_freeze_sha, r5_sha)
    assert receipt["continuation_raw_freeze_head"] == raw_freeze_sha
    assert receipt["evaluator_integrity_sealed"] is True
    assert receipt["provider_calls"] == 0


def _r5_synthetic_manifest_updated_for_raw_freeze(
    plan_freeze_sha: str, r5_sha: str
) -> dict[str, Any]:
    manifest = _r5_synthetic_manifest()
    manifest["outcome_exposure_state"]["D4_A5_OUTCOME_EXPOSURE"] = "RAW_RETRIEVAL_COMPLETE"
    manifest["outcome_exposure_state"]["continuation_implementation_freeze_head"] = r5_sha
    manifest["outcome_exposure_state"]["plan_freeze_head"] = plan_freeze_sha
    return manifest


def test_r5_14b_evaluator_preflight_rejects_runner_drift_before_outcomes(
    tmp_path, monkeypatch
):
    tmp_path, r3_sha, r5_sha, plan_freeze_sha = _r5_lifecycle_repo(tmp_path, monkeypatch)
    (tmp_path / a5.CONTINUATION_MANIFEST_PATH).write_text(
        json.dumps(_r5_synthetic_manifest_updated_for_raw_freeze(plan_freeze_sha, r5_sha), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    runner = (_REPO_ROOT / a5.RUNNER_PATH).read_text(encoding="utf-8")
    files = {
        a5.CONTINUATION_MANIFEST_PATH: (tmp_path / a5.CONTINUATION_MANIFEST_PATH).read_text(
            encoding="utf-8"
        ),
        a5.CONTINUATION_RAW_RESULTS_PATH: json.dumps(
            _r5_synthetic_raw_results(with_slots=True), ensure_ascii=False, indent=2
        ),
        a5.RUNNER_PATH: runner + "\n# post-retrieval drift\n",
    }
    _temp_repo_commit(tmp_path, files, a5.CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE)

    class _Sentinel(RuntimeError):
        pass

    def _sentinel(*_a: Any, **_k: Any):
        raise _Sentinel("deterministic evaluation body reached")

    def _forbidden(*_a: Any, **_k: Any) -> None:
        raise AssertionError("provider construction forbidden")

    monkeypatch.setattr(a5, "Retriever", _forbidden)
    monkeypatch.setattr(a5, "load_gold_dataset", _sentinel)
    # The runner drift is rejected by the strict raw-freeze allowlist inside the
    # preflight chain, before any retrieval outcome is consumed.
    with pytest.raises(RuntimeError, match="strict evaluator-integrity allowlist"):
        a5.evaluate_d4_a5(tmp_path)


def test_r5_14c_evaluator_reaches_deterministic_boundary_after_real_gate(
    tmp_path, monkeypatch
):
    """Valid R5 -> valid plan freeze -> valid raw freeze -> the evaluator passes
    the REAL raw-freeze integrity gate and reaches the deterministic evaluation
    body (proven by a sentinel), with provider construction forbidden and no
    scientific result produced."""
    tmp_path, r3_sha, r5_sha, plan_freeze_sha = _r5_lifecycle_repo(tmp_path, monkeypatch)
    (tmp_path / a5.CONTINUATION_MANIFEST_PATH).write_text(
        json.dumps(_r5_synthetic_manifest_updated_for_raw_freeze(plan_freeze_sha, r5_sha), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    files = {
        a5.CONTINUATION_MANIFEST_PATH: (tmp_path / a5.CONTINUATION_MANIFEST_PATH).read_text(
            encoding="utf-8"
        ),
        a5.CONTINUATION_RAW_RESULTS_PATH: json.dumps(
            _r5_synthetic_raw_results(with_slots=True), ensure_ascii=False, indent=2
        ),
    }
    _temp_repo_commit(tmp_path, files, a5.CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE)

    class _Sentinel(RuntimeError):
        pass

    def _sentinel(*_a: Any, **_k: Any):
        raise _Sentinel("deterministic evaluation body reached")

    def _forbidden(*_a: Any, **_k: Any) -> None:
        raise AssertionError("provider construction forbidden")

    monkeypatch.setattr(a5, "Retriever", _forbidden)
    monkeypatch.setattr(a5, "load_gold_dataset", _sentinel)
    # The REAL evaluator preflight (not monkeypatched) must pass first; the
    # sentinel then proves the deterministic body was entered.
    with pytest.raises(_Sentinel):
        a5.evaluate_d4_a5(tmp_path)
