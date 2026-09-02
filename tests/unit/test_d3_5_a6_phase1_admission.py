"""D3.5-A6 Phase 1 synthetic tests: pool construction, post-rerank replay
parity, and decision logic truth tables.

Purely synthetic — no real case data, no model calls, no evaluator outcome
computation.  The replay uses the imported production ``select_final_evidence``
unchanged; the wrapper logic mirrors ``src/panda_agent/retrieval.py``.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_SCRIPTS = Path(__file__).resolve().parents[2] / "evaluation" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import d3_5_a6_phase1_admission as admission  # noqa: E402
from panda_agent.retrieval import select_final_evidence  # noqa: E402


def make_record(oid, source="src_a", otype="source_file", text="plain text", locator=None,
                authority="primary", sv="ver-1", title=None):
    return {
        "object_id": oid,
        "source_id": source,
        "source_version_id": sv,
        "object_type": otype,
        "title": title or oid,
        "text": text,
        "authority_level": authority,
        "locator": locator or {},
    }


def make_case_entry(nongraph, graph, plan_fields, question, records):
    ordered, scores, membership = admission.compute_fused_ordering(nongraph, graph)
    universe = list(ordered)
    registry = {oid: records[oid] for oid in universe}
    return {
        "case_id": "synthetic",
        "question": {"query": question},
        "frozen_plan_fields": plan_fields,
        "nongraph_channel_rankings": nongraph,
        "exact_channel_ordering": list(nongraph.get("exact", [])),
        "full_fused_ordering": [[oid, scores[oid]] for oid in ordered],
        "channel_membership": membership,
        "post_rerank_replay_required_object_universe": universe,
    }, registry


def run_replay(case_entry, registry, reranked):
    return admission.replay_case_with_registry(case_entry, registry, reranked)


# ---------------------------------------------------------------------------
# pool construction (task card section 38)
# ---------------------------------------------------------------------------

def test_zero_reservable_pools_equal_baseline():
    baseline = [f"o{i:02d}" for i in range(30)]
    assert admission.reservable_bridge([], baseline) == []
    k2 = admission.build_treatment_pool(baseline, [], 2)
    k3 = admission.build_treatment_pool(baseline, [], 3)
    assert k2["treatment_pool_object_ids"] == baseline
    assert k3["treatment_pool_object_ids"] == baseline
    assert k2["reserved_slot_count"] == 0 and k3["reserved_slot_count"] == 0


def test_one_reservable_both_arms_reserve_one_and_k2_equals_k3():
    baseline = [f"o{i:02d}" for i in range(30)]
    reservable = ["b1"]
    k2 = admission.build_treatment_pool(baseline, reservable, 2)
    k3 = admission.build_treatment_pool(baseline, reservable, 3)
    for built in (k2, k3):
        assert built["reserved_bridge_candidate_ids"] == ["b1"]
        assert built["treatment_pool_object_ids"] == baseline[:29] + ["b1"]
        assert built["displaced_object_ids"] == ["o29"]
    assert k2["treatment_pool_object_ids"] == k3["treatment_pool_object_ids"]


def test_exactly_k_reservable():
    baseline = [f"o{i:02d}" for i in range(30)]
    k2 = admission.build_treatment_pool(baseline, ["b1", "b2"], 2)
    k3 = admission.build_treatment_pool(baseline, ["b1", "b2", "b3"], 3)
    assert k2["reserved_bridge_candidate_ids"] == ["b1", "b2"]
    assert k3["reserved_bridge_candidate_ids"] == ["b1", "b2", "b3"]
    assert k2["displaced_object_ids"] == ["o28", "o29"]
    assert k3["displaced_object_ids"] == ["o27", "o28", "o29"]


def test_more_than_k_reservable_takes_first_k_in_v2_order():
    baseline = [f"o{i:02d}" for i in range(30)]
    reservable = ["b5", "b1", "b4", "b2", "b3"]
    k2 = admission.build_treatment_pool(baseline, reservable, 2)
    k3 = admission.build_treatment_pool(baseline, reservable, 3)
    assert k2["reserved_bridge_candidate_ids"] == ["b5", "b1"]
    assert k3["reserved_bridge_candidate_ids"] == ["b5", "b1", "b4"]


def test_baseline_overlap_consumes_zero_slots():
    baseline = [f"o{i:02d}" for i in range(30)]
    baseline[5] = "bridge_here"  # selected bridge candidate already in baseline
    reservable = admission.reservable_bridge(["bridge_here", "b1"], baseline)
    assert reservable == ["b1"]  # overlap removed, no reservation spent on it
    built = admission.build_treatment_pool(baseline, reservable, 2)
    assert "bridge_here" not in built["reserved_bridge_candidate_ids"]
    assert built["treatment_pool_object_ids"].count("bridge_here") == 1


def test_no_duplicate_ids_in_treatment_pool():
    baseline = [f"o{i:02d}" for i in range(30)]
    built = admission.build_treatment_pool(baseline, ["b1", "b2"], 2)
    pool = built["treatment_pool_object_ids"]
    assert len(pool) == len(set(pool)) == 30


@pytest.mark.parametrize("k", [1, 2, 3])
def test_bottom_first_displacement(k):
    baseline = [f"o{i:02d}" for i in range(30)]
    reservable = [f"b{i}" for i in range(3)]
    built = admission.build_treatment_pool(baseline, reservable, k)
    assert built["displaced_object_ids"] == baseline[-k:]
    assert built["reserved_slot_count"] == k
    assert built["ordinary_rerank_candidates_displaced"] == k


def test_surviving_relative_order_and_reserved_append_order():
    baseline = ["a01", "a02", "a03", "a04", "a05", "a06"]
    reservable = ["z2", "z1"]
    built = admission.build_treatment_pool(baseline, reservable, 2)
    assert built["treatment_pool_object_ids"] == ["a01", "a02", "a03", "a04", "z2", "z1"]


def test_universe_below_30_all_arms_get_max_available():
    universe = [f"u{i:02d}" for i in range(20)]
    baseline = admission.build_baseline_pool(universe)
    assert baseline == universe and len(baseline) == 20
    built = admission.build_treatment_pool(baseline, ["u00", "u01"], 2)
    assert built["pool_size"] == 20


def test_validate_pool_flags_violations():
    baseline = [f"o{i:02d}" for i in range(30)]
    good = admission.build_treatment_pool(baseline, ["b1"], 1)
    good["ordered_pool_object_ids"] = good["treatment_pool_object_ids"]
    assert admission.validate_pool(good, baseline) == []
    bad = dict(good)
    bad["reserved_bridge_candidate_ids"] = ["o00"]  # reserved candidate already in baseline
    assert "duplicate_admission_of_baseline_present_candidate" in admission.validate_pool(bad, baseline)
    bad2 = dict(good)
    bad2["ordered_pool_object_ids"] = ["x", "x"]
    bad2["pool_size"] = 2
    bad2["displaced_object_ids"] = []
    bad2["reserved_bridge_candidate_ids"] = []
    assert "duplicate_object_ids_in_pool" in admission.validate_pool(bad2, baseline)
    bad3 = dict(good)
    bad3["displaced_object_ids"] = baseline[:1]  # not bottom-first
    assert "displacement_not_bottom_first" in admission.validate_pool(bad3, baseline)


# ---------------------------------------------------------------------------
# post-rerank replay (task card section 39)
# ---------------------------------------------------------------------------

def _standard_case(extra_plan=None, records=None, question="What does the macro compute?"):
    o1 = make_record("doc1", source="docs_src", otype="sphinx_page", text="documentation body")
    o2 = make_record("code1", source="src_a", otype="source_file",
                     text="void run restgas_profile helper", locator={"path": "macro/target/run.C"})
    o3 = make_record("readme1", source="src_a", otype="readme_section", text="readme section body")
    o4 = make_record("wf1", source="src_a", otype="workflow", text="workflow step")
    o5 = make_record("code2", source="src_a", otype="source_file",
                     text="second source file with restgas_profile in text")
    recs = records or {"doc1": o1, "code1": o2, "readme1": o3, "wf1": o4, "code2": o5}
    plan = {
        "intent": "troubleshooting",
        "target_repositories": ["restgas_determination"],
        "symbols": ["restgas_profile"],
        "required_source_types": ["code"],
        "source_budgets": {},
        "paper_page_hints": {},
    }
    if extra_plan:
        plan.update(extra_plan)
    nongraph = {"exact": ["code2", "code1"], "dense": ["doc1", "readme1"], "sparse": ["doc1"], "workflow": ["wf1"]}
    graph = ["code1", "readme1"]
    return make_case_entry(nongraph, graph, plan, question, recs)


def test_full_pool_ordering_returned_then_fused_fallback():
    case_entry, registry = _standard_case()
    pool = [oid for oid, _ in case_entry["full_fused_ordering"]]
    result = run_replay(case_entry, registry, pool)
    assert result["ordered_object_ids"] == pool
    assert result["ranked_object_ids"] == pool[:30]
    assert result["evidence_object_ids"]  # non-empty selection


def test_partial_ordering_fallback_appends_missing():
    case_entry, registry = _standard_case()
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    result = run_replay(case_entry, registry, full[:2])
    # every fused candidate still appears exactly once after the fallback merge
    assert result["ordered_object_ids"][:2] == full[:2]
    assert sorted(result["ordered_object_ids"]) == sorted(full)
    assert len(result["ordered_object_ids"]) == len(set(result["ordered_object_ids"]))


def test_repeated_ids_are_deduplicated():
    case_entry, registry = _standard_case()
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    result = run_replay(case_entry, registry, [full[0], full[0], full[1]])
    assert result["ordered_object_ids"].count(full[0]) == 1


def test_symbol_first_movement():
    case_entry, registry = _standard_case()
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    result = run_replay(case_entry, registry, full)
    # both exact items match the plan symbol; match_priority prefers code1 by
    # object_id, so symbol_first promotes code1 ahead of the fused leader code2
    assert result["ranked_object_ids"][0] == "code1"


def test_preferred_source_movement_decides_symbol_winner():
    winner = make_record("s_restgas", source="restgas_determination", otype="source_file",
                         text="restgas_profile lives here")
    loser = make_record("s_other", source="unrelated_repo", otype="source_file",
                        text="restgas_profile lives here too")
    recs = {"s_restgas": winner, "s_other": loser}
    plan = {"intent": "troubleshooting", "target_repositories": [], "symbols": ["restgas_profile"],
            "required_source_types": [], "source_budgets": {}, "paper_page_hints": {}}
    nongraph = {"exact": ["s_other", "s_restgas"], "dense": [], "sparse": [], "workflow": []}
    case_entry, registry = make_case_entry(nongraph, [], plan, "How is the restgas determined?", recs)
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    result = run_replay(case_entry, registry, full)
    assert result["ranked_object_ids"][0] == "s_restgas"  # source_rank prefers restgas


def test_required_first_movement():
    """A required 'code' candidate that is NOT the fused leader gets promoted."""
    doc = make_record("doc1", source="sphinx_src", otype="sphinx_page", text="documentation body")
    code = make_record("code1", source="src_a", otype="source_file", text="plain code")
    recs = {"doc1": doc, "code1": code}
    plan = {"intent": "troubleshooting", "target_repositories": [], "symbols": [],
            "required_source_types": ["code"], "source_budgets": {}, "paper_page_hints": {}}
    nongraph = {"exact": ["doc1"], "dense": ["code1"], "sparse": [], "workflow": []}
    case_entry, registry = make_case_entry(nongraph, [], plan, "neutral question", recs)
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    assert full[0] == "doc1"  # fused leader is the doc (higher exact weight)
    result = run_replay(case_entry, registry, full)
    assert result["ranked_object_ids"][0] == "code1"  # required_first promotion


def test_hinted_first_movement():
    paper = make_record("paper_obj", source="li_2026", otype="thesis_section",
                        text="theory", locator={"pdf_page": 3})
    recs = {"paper_obj": paper}
    plan = {"intent": "troubleshooting", "target_repositories": [], "symbols": [],
            "required_source_types": [], "source_budgets": {}, "paper_page_hints": {"li_2026": [3]}}
    nongraph = {"exact": [], "dense": ["doc_dummy", "paper_obj"], "sparse": [], "workflow": []}
    recs["doc_dummy"] = make_record("doc_dummy", source="src_a", otype="sphinx_page", text="other")
    case_entry, registry = make_case_entry(nongraph, [], plan, "neutral question", recs)
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    assert full[0] == "doc_dummy"  # without hints the dense leader wins
    result = run_replay(case_entry, registry, full)
    assert result["ranked_object_ids"][0] == "paper_obj"  # hinted_first promotion


def test_final_dedup_and_select_final_evidence_is_production():
    case_entry, registry = _standard_case()
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    result = run_replay(case_entry, registry, full)
    ordered = result["ordered_object_ids"]
    assert len(ordered) == len(set(ordered))
    assert select_final_evidence.__module__ == "panda_agent.retrieval"


def test_duplicate_locator_suppression():
    shared = {"path": "macro/target/run.C", "symbol": "run"}
    a = make_record("dup_a", text="alpha", locator=shared)
    b = make_record("dup_b", text="beta", locator=shared)
    recs = {"dup_a": a, "dup_b": b}
    plan = {"intent": "troubleshooting", "target_repositories": [], "symbols": [],
            "required_source_types": [], "source_budgets": {}, "paper_page_hints": {}}
    nongraph = {"exact": ["dup_a", "dup_b"], "dense": [], "sparse": [], "workflow": []}
    case_entry, registry = make_case_entry(nongraph, [], plan, "neutral question", recs)
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    result = run_replay(case_entry, registry, full)
    evidence_ids = result["evidence_object_ids"]
    assert "dup_a" in evidence_ids and "dup_b" not in evidence_ids
    reasons = {e["object_id"]: e["reason"] for e in result["excluded"]}
    assert reasons.get("dup_b") == "duplicate_locator"


def test_source_diversity_budget_cap():
    records = {f"same{i}": make_record(f"same{i}", text=f"body {i}") for i in range(6)}
    other = make_record("other_src", source="src_b", text="other body")
    records["other_src"] = other
    plan = {"intent": "troubleshooting", "target_repositories": [], "symbols": [],
            "required_source_types": [], "source_budgets": {}, "paper_page_hints": {}}
    nongraph = {"exact": [f"same{i}" for i in range(6)] + ["other_src"], "dense": [], "sparse": [], "workflow": []}
    case_entry, registry = make_case_entry(nongraph, [], plan, "neutral question", records)
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    result = run_replay(case_entry, registry, full)
    from collections import Counter
    per_source = Counter(registry[oid]["source_id"] for oid in result["evidence_object_ids"])
    assert per_source["src_a"] <= 4  # max_per_source = ceil(12 / 3)


def test_final_evidence_limit_twelve():
    records = {f"c{i:02d}": make_record(f"c{i:02d}", source=f"s{i // 4}", text=f"body {i}")
               for i in range(15)}
    plan = {"intent": "troubleshooting", "target_repositories": [], "symbols": [],
            "required_source_types": [], "source_budgets": {}, "paper_page_hints": {}}
    nongraph = {"exact": [f"c{i:02d}" for i in range(15)], "dense": [], "sparse": [], "workflow": []}
    case_entry, registry = make_case_entry(nongraph, [], plan, "neutral question", records)
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    result = run_replay(case_entry, registry, full)
    assert len(result["evidence_object_ids"]) == 12


def test_replay_deterministic_double_execution():
    case_entry, registry = _standard_case()
    full = [oid for oid, _ in case_entry["full_fused_ordering"]]
    first = run_replay(case_entry, registry, list(reversed(full)))
    second = run_replay(case_entry, registry, list(reversed(full)))
    assert first == second


def test_production_wrapper_expressions_still_present():
    """Source-anchor parity: the mirrored wrapper logic must keep matching the
    production block in src/panda_agent/retrieval.py."""
    source = (Path(__file__).resolve().parents[2] / "src" / "panda_agent" / "retrieval.py").read_text(encoding="utf-8")
    assert "list(dict.fromkeys([*reranked, *fused_order]))" in source
    assert "list(dict.fromkeys([*hinted_first,*required_first,*symbol_first,*ordered]))" in source
    assert "ranked_object_ids = ordered[:30]" in source
    assert 'preferred_sources = ["restgas_determination", "pandaroot", "luminosityfit", *preferred_sources]' in source
    assert "final_evidence_limit" in source and "select_final_evidence(" in source


# ---------------------------------------------------------------------------
# decision logic truth tables (task card sections 44-45)
# ---------------------------------------------------------------------------

PASS = admission.PASS_VERDICT
FAIL = admission.FAIL_VERDICT
P_REG = admission.P_REGRESSION
P_POOL = admission.P_POOL_PERTURBATION
P_UNST = admission.P_UNSTABLE
P_NONE = admission.P_NO_RECOVERY


def test_truth_table_cases():
    assert admission.compute_verdict(1, 2, 1, 0, 0, 0, False, False) == PASS  # K2 causal-safe, K3 larger noncausal
    assert admission.compute_verdict(1, 2, 1, 1, 1, 0, False, False) == PASS  # K2 unsafe, K3 causal-safe
    assert admission.compute_verdict(1, 1, 1, 1, 0, 0, False, False) == PASS  # equal causal deltas -> K2
    assert admission.compute_verdict(1, 2, 1, 2, 0, 0, False, False) == PASS  # K3 causal delta larger
    assert admission.compute_verdict(1, 1, 0, 0, 0, 0, True, False) == P_POOL
    assert admission.compute_verdict(1, 0, 1, 0, 1, 0, False, False) == P_REG
    assert admission.compute_verdict(0, 0, 0, 0, 0, 0, True, False) == P_UNST
    assert admission.compute_verdict(0, 0, 0, 0, 0, 0, False, False) == P_NONE
    assert admission.compute_verdict(1, 0, 1, 0, 0, 0, False, True) == FAIL
    assert admission.compute_verdict(0, 0, 0, 0, 1, 1, False, False) == P_NONE


def test_budget_selection_hierarchy():
    assert admission.select_budget(1, 2, 1, 0, 0, 0) == 2  # task card 16 critical example
    assert admission.select_budget(1, 2, 1, 1, 1, 0) == 3  # K2 unsafe, K3 causal-safe
    assert admission.select_budget(1, 1, 1, 1, 0, 0) == 2
    assert admission.select_budget(1, 2, 1, 2, 0, 0) == 3
    assert admission.select_budget(1, 1, 0, 0, 0, 0) is None
    assert admission.select_budget(2, 2, 0, 0, 1, 0) is None


def test_mcr_never_auto_fails():
    """One or more MATERIAL_CONTROL_REGRESSION groups must not produce FAIL."""
    verdict = admission.compute_verdict(2, 2, 2, 1, 1, 0, False, False)
    assert verdict in {PASS, P_REG} and verdict != FAIL
    # unsafe causal recovery under K2 with no other recovery -> regression PARTIAL, not FAIL
    assert admission.compute_verdict(1, 0, 1, 0, 1, 0, False, False) == P_REG


def test_causal_delta_bounds_and_exhaustive_uniqueness():
    d2 = c2 = None
    count = 0
    for delta2, delta3 in itertools.product((0, 1, 2), repeat=2):
        for causal2 in range(delta2 + 1):
            for causal3 in range(delta3 + 1):
                assert 0 <= causal2 <= delta2 and 0 <= causal3 <= delta3
                for r2, r3, unstable, sf in itertools.product((0, 1), repeat=4):
                    verdict = admission.compute_verdict(delta2, delta3, causal2, causal3, r2, r3, bool(unstable), bool(sf))
                    assert verdict == FAIL if sf else verdict in admission.OUTCOME_VERDICTS
                    count += 1
    assert count > 500


def test_stable_retention_semantics():
    assert admission.stable_retained([True, True, False]) is True
    assert admission.stable_retained([True, False, False]) is False
    assert admission.stable_lost([True, False, False]) is True
    assert admission.stable_lost([True, True, False]) is False
    assert admission.material_control_regression([True, True, False], [True, False, False]) is True
    assert admission.material_control_regression([True, True, False], [True, True, False]) is False
    assert admission.material_control_regression([True, False, False], [False, False, False]) is False


def test_admission_applicable_bridge_group_classification():
    groups = admission.admission_applicable_bridge_groups(
        {"g1": ["r1", "o9"], "g2": ["o8"], "g3": []}, ["r1"]
    )
    assert groups == ["g1"]  # g2 matched but nothing reservable; g3 unmatched


def test_stable_reserved_required_witness():
    assert admission.stable_reserved_required_witness([True, True, False]) is True
    assert admission.stable_reserved_required_witness([True, False, False]) is False


# ---------------------------------------------------------------------------
# per-arm origin diagnostics (Phase1-R1)
# ---------------------------------------------------------------------------

def test_per_arm_origin_summary_synthetic():
    assert admission.per_arm_origin_summary([]) == {
        "reserved_bridge_origin_count": 0, "reserved_bridge_per_origin_counts": {},
        "reserved_candidate_origin_ids": []}
    assert admission.per_arm_origin_summary(["A", "A"]) == {
        "reserved_bridge_origin_count": 1, "reserved_bridge_per_origin_counts": {"A": 2},
        "reserved_candidate_origin_ids": ["A", "A"]}
    assert admission.per_arm_origin_summary(["A", "A", "B"]) == {
        "reserved_bridge_origin_count": 2, "reserved_bridge_per_origin_counts": {"A": 2, "B": 1},
        "reserved_candidate_origin_ids": ["A", "A", "B"]}


def test_per_arm_origin_summary_is_pure_diagnostic():
    """Deriving the summary must never mutate the frozen arm identities."""
    baseline = [f"o{i:02d}" for i in range(30)]
    built = admission.build_treatment_pool(baseline, ["b1", "b2", "b3"], 3)
    reserved_ids = ["e1", "e1", "e2"]  # attributed origins of the three reserved candidates
    summary = admission.per_arm_origin_summary(reserved_ids)
    assert built["reserved_bridge_candidate_ids"] == ["b1", "b2", "b3"]
    assert built["treatment_pool_object_ids"] == baseline[:27] + ["b1", "b2", "b3"]
    assert summary["reserved_bridge_origin_count"] == 2
    assert summary["reserved_bridge_per_origin_counts"] == {"e1": 2, "e2": 1}


def test_build_case_pools_reports_explicit_per_arm_origin_summaries():
    """g036-like case: K2 reserves two candidates from one origin, K3 adds a
    second origin — the summaries must be arm-specific, never collapsed."""
    records = {}
    for i in range(40):
        records[f"o{i:02d}"] = make_record(f"o{i:02d}", text=f"body {i}")
    records["b1"] = make_record("b1", text="bridge one")
    records["b2"] = make_record("b2", text="bridge two")
    records["b3"] = make_record("b3", text="bridge three")
    plan = {"intent": "troubleshooting", "target_repositories": [], "symbols": [],
            "required_source_types": [], "source_budgets": {}, "paper_page_hints": {}}
    nongraph = {"exact": [], "dense": [f"o{i:02d}" for i in range(30)], "sparse": [], "workflow": []}
    case_entry = {
        "case_id": "synthetic-origin",
        "question": {"query": "neutral question"},
        "frozen_plan_fields": plan,
        "nongraph_channel_rankings": nongraph,
        "exact_channel_ordering": [],
        "full_fused_ordering": [[f"o{i:02d}", 0.01 * i] for i in range(30)],
        "channel_membership": {f"o{i:02d}": ["dense"] for i in range(30)},
        "post_rerank_replay_required_object_universe": [f"o{i:02d}" for i in range(30)],
        "v2_selected_bridge_order": ["b1", "b2", "b3"],
        "selected_rank_keys": [
            {"candidate_object_id": "b1", "attributed_origin_id": "e1"},
            {"candidate_object_id": "b2", "attributed_origin_id": "e1"},
            {"candidate_object_id": "b3", "attributed_origin_id": "e2"},
        ],
        "selected_bridge_origin_count": 2,
        "selected_bridge_per_origin_counts": {"e1": 2, "e2": 1},
    }
    registry = {**records}
    case_pools = admission.build_case_pools(case_entry)
    diag = case_pools["origin_concentration_diagnostics"]
    k2 = diag["reserved_by_arm"]["ADMISSION_K2"]
    k3 = diag["reserved_by_arm"]["ADMISSION_K3"]
    assert k2["reserved_bridge_origin_count"] == 1
    assert k2["reserved_bridge_per_origin_counts"] == {"e1": 2}
    assert k3["reserved_bridge_origin_count"] == 2
    assert k3["reserved_bridge_per_origin_counts"] == {"e1": 2, "e2": 1}
    assert k2["reserved_candidate_origin_ids"] == ["e1", "e1"]
    assert k3["reserved_candidate_origin_ids"] == ["e1", "e1", "e2"]
    # identities untouched by diagnostic derivation
    assert case_pools["arms"]["ADMISSION_K2"]["reserved_bridge_candidate_ids"] == ["b1", "b2"]
    assert case_pools["arms"]["ADMISSION_K3"]["ordered_pool_object_ids"] == case_pools["baseline_pool_object_ids"][:27] + ["b1", "b2", "b3"]
