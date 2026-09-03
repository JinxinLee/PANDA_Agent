"""Unit tests for PANDA Agent D4-A2-R1 Critical-Regression Diagnosis & Repair Decision.

All tests are deterministic, offline, and self-contained.
Zero model calls, zero retrieval runs, zero live database writes.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))
if str(_PROJECT_ROOT / "evaluation" / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "evaluation" / "scripts"))

from panda_agent.evaluation import load_gold_dataset
import d4_a2_r1_static_diagnosis as r1


def test_g021_forward_contract_consistency():
    """Verify that g021 forward contract correction is internally consistent:
    - g021.e1 remains critical: true
    - g021.e2 becomes critical: false
    - answer point p1 remains critical: true
    - answer point p2 remains critical: true
    - answer point p3 becomes critical: false
    - identifier PndTargetGenerator becomes critical: false
    - elements are preserved, not deleted
    """
    gold_bench_path = _PROJECT_ROOT / "evaluation/benchmarks/v2_6/gold_questions.yaml"
    gold_ds = load_gold_dataset(gold_bench_path)
    g021 = next(q for q in gold_ds.questions if q.id == "g021")

    # Evidence groups
    eg_map = {g.group_id: g for g in g021.required_evidence_groups}
    assert "g021.e1" in eg_map
    assert "g021.e2" in eg_map
    assert eg_map["g021.e1"].critical is True
    assert eg_map["g021.e2"].critical is False

    # Answer points
    ap_map = {p.point_id: p for p in g021.required_answer_points}
    assert "p1" in ap_map and ap_map["p1"].critical is True
    assert "p2" in ap_map and ap_map["p2"].critical is True
    assert "p3" in ap_map and ap_map["p3"].critical is False

    # Identifiers
    id_map = {i.text: i for i in g021.required_identifiers}
    assert "PndTargetGenerator" in id_map
    assert id_map["PndTargetGenerator"].critical is False


def test_n021_and_n022_evidence_requirements_preserved():
    """Verify n021 and n022 in novel_dev.yaml:
    - n021.e2 is REQUIRED_CRITICAL (detectors/lmd/CMakeLists.txt)
    - n022.e2 is REQUIRED_CRITICAL (macro/target/poca_step2_analysis.py)
    - novel_dev.yaml is byte-unchanged
    """
    novel_bench_path = _PROJECT_ROOT / "evaluation/novel/v1/novel_dev.yaml"
    novel_ds = load_gold_dataset(novel_bench_path)
    questions = {q.id: q for q in novel_ds.questions}

    n021 = questions["n021"]
    n021_e2 = next(g for g in n021.required_evidence_groups if g.group_id == "n021.e2")
    assert n021_e2.critical is True
    assert n021_e2.role == "pandaroot_lmd_implementation_ownership"

    n022 = questions["n022"]
    n022_e2 = next(g for g in n022.required_evidence_groups if g.group_id == "n022.e2")
    assert n022_e2.critical is True
    assert n022_e2.role == "step2_artifact_consumption"


def test_historical_d4_a2_artifacts_immutable():
    """Historical D4-A2 verdict and raw artifacts must be preserved."""
    res_path = _PROJECT_ROOT / "evaluation/d4_a2_result.json"
    raw_path = _PROJECT_ROOT / "evaluation/d4_a2_raw_before_after_results.json"
    eval_path = _PROJECT_ROOT / "evaluation/d4_a2_evaluator_results.json"

    with open(res_path, "r", encoding="utf-8") as f:
        res = json.load(f)
    with open(raw_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    with open(eval_path, "r", encoding="utf-8") as f:
        ev = json.load(f)

    assert res["lifecycle_state"] == "COMPLETE / FAIL / CRITICAL_OR_GROUNDING_REGRESSION"
    assert res["scientific_evaluation"]["group_retention"]["critical_group_regressions"] == ["n022.e2", "g021.e2"]
    assert len(raw["slots"]) == 32
    assert ev["verdict_outcome"]["batch_verdict"] == "FAIL / CRITICAL_OR_GROUNDING_REGRESSION"


def test_r1_static_diagnosis_artifact_contents():
    """Verify machine artifact evaluation/d4_a2_r1_critical_regression_diagnosis.json."""
    diag_path = _PROJECT_ROOT / "evaluation/d4_a2_r1_critical_regression_diagnosis.json"
    assert diag_path.exists()
    with open(diag_path, "r", encoding="utf-8") as f:
        diag = json.load(f)

    # Core metadata
    assert diag["checkpoint"] == "D4-A2-R1"
    assert diag["starting_head"] == r1.STARTING_HEAD
    assert diag["historical_d4_a2_authority"]["historical_verdict"] == "FAIL / CRITICAL_OR_GROUNDING_REGRESSION"
    assert diag["D4_A2_R1_DECISION"] == "PASS / BENCHMARK_CORRECTION_AND_REGRESSION_ATTRIBUTION_COMPLETE"
    assert diag["production_activation"] is False

    # Execution boundary
    eb = diag["execution_boundary"]
    assert eb["model_calls"] == 0
    assert eb["retrieval_runs"] == 0
    assert eb["protected_dataset_access"] == 0

    # Layer divergence
    fd = diag["n022_first_divergence"]
    assert fd["layer0_treatment_applicability"]["did_batch1_component_mask_directly_change_n022_expansion_inputs"] is False
    assert fd["layer1_analyzer_retrieval_plan"]["classification"] == "PLAN_DIVERGENCE"
    assert fd["first_divergence_layer"] == "Layer 1 — Analyzer / retrieval plan"

    # Offline counterfactual
    cf = diag["offline_counterfactual"]
    assert cf["identifiable"] is True
    assert cf["target_main_reenters_top30"] is False
    assert cf["target_worker_present_in_after_channels"] is False

    # Attribution & repair owner
    assert diag["n022_attribution_class"] == "ORDINARY_FRESH_RUN_VARIANCE_DOMINATED"
    assert diag["n022_repair_owner"] == "QUERY_ANALYZER"

    # Forward diagnostic
    fdiag = diag["forward_corrected_contract_diagnostic"]
    assert fdiag["FORWARD_CRITICAL_GROUP_REGRESSIONS"] == ["n022.e2"]
    assert fdiag["FORWARD_NONCRITICAL_GROUP_REGRESSIONS"] == ["g021.e2"]
    assert fdiag["gold_critical_final_evidence_regressions_count"] == 0
    assert fdiag["gold_critical_final_evidence_recall"]["delta"] == 0.0
    assert fdiag["cohort_critical_final_evidence_recall"]["delta"] == pytest.approx(-0.025641, abs=1e-5)
    assert fdiag["cohort_final_evidence_recall"]["delta"] == pytest.approx(-0.064103, abs=1e-5)
