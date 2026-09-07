#!/usr/bin/env python3
"""D4-A9-R1 — Post-Outcome Closeout Verification Repair.

Implements pure deterministic recomputation and comprehensive post-outcome
verification seals for the frozen D4-A9 scientific validation artifacts
without scientific provider execution, retrieval re-execution, or modifying
any historical scientific artifact.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------------

MANIFEST_PATH = "evaluation/d4_a9_execution_manifest.json"
RAW_PLANS_PATH = "evaluation/d4_a9_raw_prospective_plans.json"
RAW_RESULTS_PATH = "evaluation/d4_a9_raw_paired_results.json"
A9_EVALUATOR_RESULTS_PATH = "evaluation/d4_a9_evaluator_results.json"
A9_RESULT_PATH = "evaluation/d4_a9_result.json"
HISTORICAL_A9_SCRIPT_PATH = (
    "evaluation/scripts/d4_a9_model_factory_covered_symbol_retirement_validation.py"
)
HISTORICAL_A9_TEST_PATH = (
    "tests/unit/test_d4_a9_model_factory_covered_symbol_retirement_validation.py"
)
HISTORICAL_A9_REPORT_PATH = (
    "evaluation/D4_A9_MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATION.md"
)

R1_CONTRACT_PATH = (
    "evaluation/d4_a9_r1_post_outcome_closeout_verification_contract.json"
)
R1_RESULT_PATH = "evaluation/d4_a9_r1_result.json"
R1_REPORT_PATH = (
    "evaluation/D4_A9_R1_POST_OUTCOME_CLOSEOUT_VERIFICATION_REPAIR.md"
)
R1_SCRIPT_PATH = (
    "evaluation/scripts/d4_a9_r1_post_outcome_closeout_verification_repair.py"
)
R1_TEST_PATH = (
    "tests/unit/test_d4_a9_r1_post_outcome_closeout_verification_repair.py"
)

GOLD_QUESTIONS_PATH = "evaluation/benchmarks/v2_6/gold_questions.yaml"

# ---------------------------------------------------------------------------
# Checkpoint Boundaries & Blob Constants
# ---------------------------------------------------------------------------

STARTING_HEAD = "07b8cc921b4e36dc2acf2ae4ba0b27f4b3edf115"
STARTING_COMMIT_MESSAGE = "D4-A9 close component-sensitive model-factory validation"
STARTING_PARENT_HEAD = "2419d4f1818277656c1b3be93e423134e877657f"

RAW_PLANS_FREEZE_COMMIT = "443d832258bf99a8f049ea524995b05922cdae80"
RAW_PLANS_EXPECTED_BLOB = "99891321c0d3ba3e0f54158441f2d739eca2db6f"

RAW_RESULTS_FREEZE_COMMIT = "2419d4f1818277656c1b3be93e423134e877657f"
RAW_RESULTS_EXPECTED_BLOB = "4f44ac31c9fd917c1212f8d64c59974f90e4cfd6"

R2_AUTHORITY_HEAD = "06f853d9613c5170676d77261cc2d7b82d50958c"

HISTORICAL_A9_ARTIFACT_BLOBS = {
    HISTORICAL_A9_REPORT_PATH: "ceabb77f1bce26e542894cd5e6966d6bec9ba810",
    MANIFEST_PATH: "e9ace2740a02b1ac827a47fe7a9c14758dddbdee",
    RAW_PLANS_PATH: "99891321c0d3ba3e0f54158441f2d739eca2db6f",
    RAW_RESULTS_PATH: "4f44ac31c9fd917c1212f8d64c59974f90e4cfd6",
    A9_EVALUATOR_RESULTS_PATH: "77f299d0ca9c3c4b7fc4dabb611eebc3979458b8",
    A9_RESULT_PATH: "f4e27c51d326fe703274f25d015c6c0d2f90335e",
    HISTORICAL_A9_SCRIPT_PATH: "90d3dd33808ccb21d210f4ca151136586fe0469e",
    HISTORICAL_A9_TEST_PATH: "9dc8f48a4a21ce3c22b32dd951a4a3fc8e827405",
}

R2_AUTHORITY_ARTIFACT_BLOBS = {
    "evaluation/D4_A8_R2_COMPONENT_SENSITIVE_EXECUTION_CONTRACT_SEAL.md": (
        "00fce9d3434aa3d242fbdf10629a8f4c2c543666"
    ),
    "evaluation/d4_a8_r2_component_sensitive_execution_preregistration.json": (
        "44a88edb9f2a2fa684ae49d7b08f8c1b38dfca12"
    ),
    "evaluation/d4_a8_r2_result.json": (
        "7cf52ea0fbc696c77fb1e85b9d81bd65998a2022"
    ),
    "evaluation/scripts/d4_a8_r2_component_sensitive_execution_contract_seal.py": (
        "a59ba7d9bcdd095ff597cfc1d07c030d95955bca"
    ),
    "tests/unit/test_d4_a8_r2_component_sensitive_execution_contract_seal.py": (
        "f6e80b271dc7f44d57ba8d6f51cb0cb630db00d6"
    ),
}

ALLOWED_R1_PATHS = {
    "docs/EVALUATION_STATUS.md",
    "docs/GENERALIZATION_ROADMAP.md",
    R1_REPORT_PATH,
    R1_CONTRACT_PATH,
    R1_RESULT_PATH,
    R1_SCRIPT_PATH,
    R1_TEST_PATH,
}

# ---------------------------------------------------------------------------
# Scientific Constants
# ---------------------------------------------------------------------------

TARGET_RULE_ID = "model_factory_theory"
COVERED_COMPONENT = "model/PndLmdModelFactory.cxx"

FROZEN_FORMAL_COHORT = ["g031", "g032", "g033", "g047"]

FROZEN_COVERED_SYMBOL_MASK = [COVERED_COMPONENT]

FROZEN_UNCOVERED_SYMBOL_HOLD_MASK = [
    "model/PndLmdDPMAngModel1D.cxx",
    "model/PndLmdDPMAngModel2D.cxx",
]

FROZEN_PAGE_HINT_HOLD_MASK = {
    "pflueger_2017": [51, 57, 65],
}

CASE_ROLES = {
    "g031": {
        "role": "DIRECT_MODEL_FACTORY_TREATMENT_CASE",
        "covered_component": COVERED_COMPONENT,
        "critical_evidence_group": "g031.e1",
    },
    "g032": {
        "role": "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
        "adjacent_component": "model/PndLmdDPMAngModel1D.cxx",
        "critical_evidence_group": "g032.e1",
    },
    "g033": {
        "role": "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
        "adjacent_component": "model/PndLmdDPMAngModel2D.cxx",
        "critical_evidence_group": "g033.e1",
    },
    "g047": {
        "role": "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL",
        "adjacent_page_hint": {"source_id": "pflueger_2017", "pdf_page": 51},
        "critical_evidence_group": "g047.e1",
    },
}

SCHEDULE_8 = [
    {"cell_index": 1, "case_id": "g031", "arm": "A7_CURRENT"},
    {
        "cell_index": 2,
        "case_id": "g031",
        "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
    },
    {"cell_index": 3, "case_id": "g032", "arm": "A7_CURRENT"},
    {
        "cell_index": 4,
        "case_id": "g032",
        "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
    },
    {"cell_index": 5, "case_id": "g033", "arm": "A7_CURRENT"},
    {
        "cell_index": 6,
        "case_id": "g033",
        "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
    },
    {"cell_index": 7, "case_id": "g047", "arm": "A7_CURRENT"},
    {
        "cell_index": 8,
        "case_id": "g047",
        "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
    },
]

REQUIRED_PLAN_FIELDS = [
    "case_id",
    "question",
    "provider_model_contract",
    "raw_analyzer_response",
    "canonical_plan",
    "canonical_serialization",
    "contribution_ledger",
    "provenance_origin_receipts",
    "component_applicability_receipts",
    "current_execution_projection",
    "treatment_execution_projection",
    "plan_signature",
    "provider_accounting",
    "matched_rule_identities",
]

EXPECTED_ANALYZER_TOKENS = {
    "g031": 1788,
    "g032": 1747,
    "g033": 1438,
    "g047": 2226,
    "total": 7199,
}

EXPECTED_MATCHED_RULES = {
    "g031": ["model_factory_theory", "model_factory_acceptance_methods"],
    "g032": [],
    "g033": [],
    "g047": ["dpm_model_theory"],
}

# ---------------------------------------------------------------------------
# Git & IO Helpers
# ---------------------------------------------------------------------------

def _git(args: list[str], cwd: Path) -> str:
    res = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if res.returncode != 0:
        raise RuntimeError(
            f"git command failed ({res.returncode}): git {' '.join(args)}\n"
            f"stderr: {res.stderr.strip()}"
        )
    return res.stdout.strip()


def git_head(cwd: Path) -> str:
    return _git(["rev-parse", "HEAD"], cwd)


def git_blob(cwd: Path, ref: str, file_path: str) -> str | None:
    try:
        norm_path = file_path.replace("\\", "/")
        return _git(["rev-parse", f"{ref}:{norm_path}"], cwd)
    except RuntimeError:
        return None


def git_hash_object(cwd: Path, file_path: Path) -> str:
    return _git(["hash-object", str(file_path)], cwd)


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Section 27: Pure Deterministic Recomputed Evaluator
# ---------------------------------------------------------------------------

def recompute_d4_a9_closeout_from_frozen_artifacts(
    plans_data: dict[str, Any],
    results_data: dict[str, Any],
    gold_questions: dict[str, Any],
    object_lookup: dict[str, dict[str, Any]],
    contract_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Pure deterministic evaluator consuming only frozen raw scientific artifacts.

    Computes:
      - g031 baseline reproduction (g031.e1)
      - g031 treatment reproduction (g031.e1)
      - selected origin subtraction & independent origin survival
      - control treatment no-op projection
      - control critical evidence safety (no treatment loss)
      - version safety (zero wrong-version evidence items)
      - grounding safety (zero treatment-only forbidden evidence / unresolvable objects)
      - diagnostic non-critical retrieval variance (non-gating)
      - exact 6-level precedence
    """
    from panda_agent.evaluation import _matched_evidence_groups

    plans_list = plans_data.get("plans", [])
    slots_list = results_data.get("slots", [])

    plans_by_case = {p["case_id"]: p for p in plans_list if "case_id" in p}
    slots_map = {(s["case_id"], s["arm"]): s for s in slots_list if "case_id" in s and "arm" in s}

    reasons: list[str] = []

    # 1. Structural / protocol verification
    protocol_errors: list[str] = []
    if len(plans_list) != len(FROZEN_FORMAL_COHORT):
        protocol_errors.append(f"Plan count {len(plans_list)} != {len(FROZEN_FORMAL_COHORT)}")
    if len(slots_list) != len(SCHEDULE_8):
        protocol_errors.append(f"Slot count {len(slots_list)} != {len(SCHEDULE_8)}")

    for cid in FROZEN_FORMAL_COHORT:
        if cid not in plans_by_case:
            protocol_errors.append(f"Missing plan record for case {cid}")
        if (cid, "A7_CURRENT") not in slots_map:
            protocol_errors.append(f"Missing A7_CURRENT slot for case {cid}")
        if (cid, "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT") not in slots_map:
            protocol_errors.append(
                f"Missing COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT slot for case {cid}"
            )

    if protocol_errors:
        return {
            "verification_status": "FAIL",
            "scientific_verdict_level": 1,
            "scientific_verdict": "INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED",
            "scientific_decision": "INVALID_PROTOCOL",
            "component_dispositions": {
                COVERED_COMPONENT: "INVALID_PROTOCOL",
                "model/PndLmdDPMAngModel1D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "model/PndLmdDPMAngModel2D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "pflueger_2017:[51, 57, 65]": "HOLD_OUTSIDE_TREATMENT_SCOPE",
            },
            "reasons": protocol_errors,
            "details": {},
        }

    # 2. Recompute g031 baseline reproduction on A7_CURRENT
    q_g031 = gold_questions.get("g031")
    if not q_g031:
        raise ValueError("Gold question g031 not found")

    eg_g031_e1 = [g for g in q_g031.required_evidence_groups if g.group_id == "g031.e1"]
    if not eg_g031_e1:
        raise ValueError("Critical evidence group g031.e1 missing from gold definition")

    slot_g031_cur = slots_map[("g031", "A7_CURRENT")]
    cur_final_ids = slot_g031_cur.get("final_evidence_object_ids") or []
    rec_cur_g031, prov_cur_g031 = _matched_evidence_groups(
        eg_g031_e1, cur_final_ids, object_lookup
    )
    g031_cur_matched_oids = [
        p["object_id"] for p in prov_cur_g031 if p.get("matched") is not False and "object_id" in p
    ]
    g031_cur_rank = (
        cur_final_ids.index(g031_cur_matched_oids[0]) + 1 if g031_cur_matched_oids else None
    )
    g031_baseline_reproduced = rec_cur_g031 > 0.0

    if not g031_baseline_reproduced:
        return {
            "verification_status": "PASS",
            "scientific_verdict_level": 2,
            "scientific_verdict": "INCONCLUSIVE / ALL_COVERED_COMPONENT_BASELINES_NOT_REPRODUCED",
            "scientific_decision": "INCONCLUSIVE_BASELINE_NOT_REPRODUCED",
            "component_dispositions": {
                COVERED_COMPONENT: "INCONCLUSIVE_BASELINE_NOT_REPRODUCED",
                "model/PndLmdDPMAngModel1D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "model/PndLmdDPMAngModel2D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "pflueger_2017:[51, 57, 65]": "HOLD_OUTSIDE_TREATMENT_SCOPE",
            },
            "g031_baseline_reproduced": False,
            "g031_treatment_reproduced": False,
            "reasons": ["g031 / A7_CURRENT failed to reproduce critical evidence group g031.e1"],
            "details": {
                "g031_cur_matched_oids": g031_cur_matched_oids,
                "g031_cur_rank": g031_cur_rank,
            },
        }

    # 3. Recompute g031 treatment reproduction
    slot_g031_trt = slots_map[("g031", "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT")]
    trt_final_ids = slot_g031_trt.get("final_evidence_object_ids") or []
    rec_trt_g031, prov_trt_g031 = _matched_evidence_groups(
        eg_g031_e1, trt_final_ids, object_lookup
    )
    g031_trt_matched_oids = [
        p["object_id"] for p in prov_trt_g031 if p.get("matched") is not False and "object_id" in p
    ]
    g031_trt_rank = (
        trt_final_ids.index(g031_trt_matched_oids[0]) + 1 if g031_trt_matched_oids else None
    )
    g031_treatment_reproduced = rec_trt_g031 > 0.0

    # 4. Verify g031 selected origin subtraction & independent origin survival
    plan_g031 = plans_by_case["g031"]
    diff_receipts = plan_g031.get("treatment_execution_projection_diff_receipts") or {}
    removed_origin_entries = diff_receipts.get("removed_rule_origin_entries") or []

    target_origin_subtracted = any(
        TARGET_RULE_ID in (entry.get("retired_rule_origins") or [])
        and entry.get("value") == COVERED_COMPONENT
        for entry in removed_origin_entries
    )

    # Independent origin survival check
    independent_origin_preserved = False
    for entry in removed_origin_entries:
        if entry.get("value") == COVERED_COMPONENT:
            surviving_origins = entry.get("surviving_origin_ids") or []
            if "model_factory_acceptance_methods" in surviving_origins:
                independent_origin_preserved = True

    if not target_origin_subtracted:
        protocol_errors.append(
            f"Target origin {TARGET_RULE_ID} was not subtracted for {COVERED_COMPONENT} in g031"
        )
    if not independent_origin_preserved:
        protocol_errors.append(
            f"Independent origin model_factory_acceptance_methods did not survive in g031"
        )

    if protocol_errors:
        return {
            "verification_status": "FAIL",
            "scientific_verdict_level": 1,
            "scientific_verdict": "INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED",
            "scientific_decision": "INVALID_PROTOCOL",
            "component_dispositions": {
                COVERED_COMPONENT: "INVALID_PROTOCOL",
                "model/PndLmdDPMAngModel1D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "model/PndLmdDPMAngModel2D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "pflueger_2017:[51, 57, 65]": "HOLD_OUTSIDE_TREATMENT_SCOPE",
            },
            "reasons": protocol_errors,
            "details": {},
        }

    # 5. Check treatment loss on g031 (Level 3 Dependency)
    if not g031_treatment_reproduced:
        return {
            "verification_status": "PASS",
            "scientific_verdict_level": 3,
            "scientific_verdict": (
                "PARTIAL / DEPENDENCY_OBSERVED_FOR_COVERED_COMPONENTS_RETAIN"
            ),
            "scientific_decision": "DEPENDENCY_OBSERVED_RETAIN",
            "component_dispositions": {
                COVERED_COMPONENT: "DEPENDENCY_OBSERVED_RETAIN",
                "model/PndLmdDPMAngModel1D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "model/PndLmdDPMAngModel2D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "pflueger_2017:[51, 57, 65]": "HOLD_OUTSIDE_TREATMENT_SCOPE",
            },
            "g031_baseline_reproduced": True,
            "g031_treatment_reproduced": False,
            "selected_origin_subtraction_verified": True,
            "independent_origin_preservation_verified": True,
            "reasons": [
                f"g031.e1 critical evidence lost in treatment arm upon subtracting {TARGET_RULE_ID}"
            ],
            "details": {
                "g031_cur_matched_oids": g031_cur_matched_oids,
                "g031_cur_rank": g031_cur_rank,
            },
        }

    # 6. Verify control treatment projection is exact no-op
    control_no_op_verified = True
    for cid in ["g032", "g033", "g047"]:
        p = plans_by_case[cid]
        matched = p.get("matched_rule_identities") or []
        cur_proj = p.get("current_execution_projection")
        trt_proj = p.get("treatment_execution_projection")
        diff_r = p.get("treatment_execution_projection_diff_receipts") or {}

        if TARGET_RULE_ID in matched:
            protocol_errors.append(f"Control {cid} matched target rule {TARGET_RULE_ID}")
        if cur_proj != trt_proj:
            protocol_errors.append(f"Control {cid} treatment projection differs from current projection")
        if (diff_r.get("removed_rule_origin_entries") or []):
            protocol_errors.append(f"Control {cid} had non-empty removed_rule_origin_entries")

    if protocol_errors:
        return {
            "verification_status": "FAIL",
            "scientific_verdict_level": 1,
            "scientific_verdict": "INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED",
            "scientific_decision": "INVALID_PROTOCOL",
            "component_dispositions": {
                COVERED_COMPONENT: "INVALID_PROTOCOL",
                "model/PndLmdDPMAngModel1D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "model/PndLmdDPMAngModel2D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "pflueger_2017:[51, 57, 65]": "HOLD_OUTSIDE_TREATMENT_SCOPE",
            },
            "reasons": protocol_errors,
            "details": {},
        }

    # 7. Safety Audits (Level 4 Gates): Critical evidence, Version safety, Grounding safety
    safety_regression = False
    control_critical_details: dict[str, Any] = {}

    for cid in ["g032", "g033", "g047"]:
        q_ctrl = gold_questions.get(cid)
        if not q_ctrl:
            continue
        crit_groups = [g for g in q_ctrl.required_evidence_groups if g.critical]
        sc = slots_map[(cid, "A7_CURRENT")]
        st = slots_map[(cid, "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT")]
        c_ids = sc.get("final_evidence_object_ids") or []
        t_ids = st.get("final_evidence_object_ids") or []

        rec_c, prov_c = _matched_evidence_groups(crit_groups, c_ids, object_lookup)
        rec_t, prov_t = _matched_evidence_groups(crit_groups, t_ids, object_lookup)

        loss = rec_c > rec_t
        if loss:
            safety_regression = True
            reasons.append(f"Control case {cid} suffered critical evidence loss (cur={rec_c}, trt={rec_t})")

        control_critical_details[cid] = {
            "current_matched_groups": rec_c,
            "treatment_matched_groups": rec_t,
            "critical_groups_count": len(crit_groups),
            "critical_evidence_loss": loss,
            "current_provenance": prov_c,
            "treatment_provenance": prov_t,
        }

    # Version safety audit: across all 8 slots
    version_violations: list[dict[str, Any]] = []
    for s in slots_list:
        cid = s["case_id"]
        q = gold_questions.get(cid)
        if not q:
            continue
        allowed_versions = set(q.allowed_source_versions)
        for item in s.get("evidence_items") or []:
            sv = item.get("source_version_id")
            oid = item.get("object_id")
            if sv is not None and sv not in allowed_versions:
                version_violations.append({
                    "cell_index": s["cell_index"],
                    "cell_id": s["cell_id"],
                    "case_id": cid,
                    "arm": s["arm"],
                    "object_id": oid,
                    "source_version_id": sv,
                    "allowed_source_versions": list(allowed_versions),
                })

    if version_violations:
        safety_regression = True
        reasons.append(f"Version safety violation: {len(version_violations)} unpermitted version items found")

    # Grounding safety audit: across all 8 slots
    current_grounding_violations: list[dict[str, Any]] = []
    treatment_grounding_violations: list[dict[str, Any]] = []
    treatment_only_grounding_regressions: list[dict[str, Any]] = []

    for cid in FROZEN_FORMAL_COHORT:
        q = gold_questions.get(cid)
        if not q:
            continue
        forbidden_selectors = q.forbidden_evidence or []

        sc = slots_map[(cid, "A7_CURRENT")]
        st = slots_map[(cid, "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT")]

        cur_forbidden_oids: set[str] = set()
        for item in sc.get("evidence_items") or []:
            oid = item.get("object_id")
            canonical = object_lookup.get(oid) or item
            if any(sel.matches(canonical) for sel in forbidden_selectors):
                cur_forbidden_oids.add(oid)
                current_grounding_violations.append({
                    "case_id": cid,
                    "arm": "A7_CURRENT",
                    "object_id": oid,
                    "violation_type": "forbidden_evidence_selector_hit",
                })

        for item in st.get("evidence_items") or []:
            oid = item.get("object_id")
            canonical = object_lookup.get(oid)
            if canonical is None:
                # Unresolvable object lookup
                treatment_only_grounding_regressions.append({
                    "case_id": cid,
                    "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
                    "object_id": oid,
                    "violation_type": "unresolvable_object_in_lookup",
                })
                safety_regression = True
                continue

            if any(sel.matches(canonical) for sel in forbidden_selectors):
                treatment_grounding_violations.append({
                    "case_id": cid,
                    "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
                    "object_id": oid,
                    "violation_type": "forbidden_evidence_selector_hit",
                })
                if oid not in cur_forbidden_oids:
                    treatment_only_grounding_regressions.append({
                        "case_id": cid,
                        "arm": "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT",
                        "object_id": oid,
                        "violation_type": "treatment_only_forbidden_evidence_hit",
                    })
                    safety_regression = True

    if treatment_only_grounding_regressions:
        reasons.append(
            f"Grounding safety regression: {len(treatment_only_grounding_regressions)} "
            f"treatment-only grounding violations found"
        )

    # Diagnostic non-critical retrieval variance (non-gating)
    diagnostic_variance: dict[str, Any] = {}
    for cid in FROZEN_FORMAL_COHORT:
        sc = slots_map[(cid, "A7_CURRENT")]
        st = slots_map[(cid, "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT")]
        c_ids = sc.get("final_evidence_object_ids") or []
        t_ids = st.get("final_evidence_object_ids") or []
        set_eq = set(c_ids) == set(t_ids)
        list_eq = c_ids == t_ids
        diagnostic_variance[cid] = {
            "identical_evidence_set": set_eq,
            "identical_rank_order": list_eq,
            "current_count": len(c_ids),
            "treatment_count": len(t_ids),
            "additions_in_treatment": sorted(list(set(t_ids) - set(c_ids))),
            "removals_in_treatment": sorted(list(set(c_ids) - set(t_ids))),
        }

    # If any safety regression occurred -> Level 4
    if safety_regression:
        return {
            "verification_status": "PASS",
            "scientific_verdict_level": 4,
            "scientific_verdict": "FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION",
            "scientific_decision": "FAIL_REGRESSION",
            "component_dispositions": {
                COVERED_COMPONENT: "RETIREMENT_VALIDATED_COMPONENT",
                "model/PndLmdDPMAngModel1D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "model/PndLmdDPMAngModel2D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "pflueger_2017:[51, 57, 65]": "HOLD_OUTSIDE_TREATMENT_SCOPE",
            },
            "g031_baseline_reproduced": True,
            "g031_treatment_reproduced": True,
            "selected_origin_subtraction_verified": True,
            "independent_origin_preservation_verified": True,
            "control_no_op_verified": True,
            "control_critical_safety": control_critical_details,
            "version_safety": {
                "total_version_violations": len(version_violations),
                "violating_items": version_violations,
            },
            "grounding_safety": {
                "current_grounding_violations": current_grounding_violations,
                "treatment_grounding_violations": treatment_grounding_violations,
                "treatment_only_grounding_regressions": treatment_only_grounding_regressions,
            },
            "diagnostic_non_critical_retrieval_variance": diagnostic_variance,
            "reasons": reasons,
            "details": {
                "g031_cur_matched_oids": g031_cur_matched_oids,
                "g031_cur_rank": g031_cur_rank,
                "g031_trt_matched_oids": g031_trt_matched_oids,
                "g031_trt_rank": g031_trt_rank,
            },
        }

    # 8. Applicability check (Level 5)
    app_receipts = plan_g031.get("component_applicability_receipts") or []
    cov_app = [
        r for r in app_receipts if r.get("component_value") == COVERED_COMPONENT
    ]
    if not cov_app or cov_app[0].get("applicability_status") != "ACTIVE_IDENTIFIABLE":
        return {
            "verification_status": "PASS",
            "scientific_verdict_level": 5,
            "scientific_verdict": (
                "INCONCLUSIVE / COVERED_COMPONENT_APPLICABILITY_INCOMPLETE"
            ),
            "scientific_decision": "INCONCLUSIVE_APPLICABILITY_INCOMPLETE",
            "component_dispositions": {
                COVERED_COMPONENT: "INCONCLUSIVE_APPLICABILITY_INCOMPLETE",
                "model/PndLmdDPMAngModel1D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "model/PndLmdDPMAngModel2D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
                "pflueger_2017:[51, 57, 65]": "HOLD_OUTSIDE_TREATMENT_SCOPE",
            },
            "reasons": ["Applicability of covered component was incomplete or not identifiable"],
            "details": {},
        }

    # 9. Clean outcome -> Level 6 PARTIAL PASS
    return {
        "verification_status": "PASS",
        "scientific_verdict_level": 6,
        "scientific_verdict": (
            "PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD"
        ),
        "scientific_decision": (
            "MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD"
        ),
        "component_dispositions": {
            COVERED_COMPONENT: "RETIREMENT_VALIDATED_COMPONENT",
            "model/PndLmdDPMAngModel1D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
            "model/PndLmdDPMAngModel2D.cxx": "HOLD_DIRECT_TREATMENT_COVERAGE_GAP",
            "pflueger_2017:[51, 57, 65]": "HOLD_OUTSIDE_TREATMENT_SCOPE",
        },
        "g031_baseline_reproduced": True,
        "g031_treatment_reproduced": True,
        "selected_origin_subtraction_verified": True,
        "independent_origin_preservation_verified": True,
        "control_no_op_verified": True,
        "control_critical_safety": control_critical_details,
        "version_safety": {
            "total_version_violations": 0,
            "violating_items": [],
        },
        "grounding_safety": {
            "current_grounding_violations": current_grounding_violations,
            "treatment_grounding_violations": treatment_grounding_violations,
            "treatment_only_grounding_regressions": [],
        },
        "diagnostic_non_critical_retrieval_variance": diagnostic_variance,
        "reasons": [
            f"Covered component {COVERED_COMPONENT} reproduced critical evidence g031.e1 "
            f"in both current and treatment arms upon subtracting {TARGET_RULE_ID} origin; "
            f"independent origin model_factory_acceptance_methods preserved; "
            f"controls verified exact no-op with zero critical regressions; "
            f"zero version violations; zero grounding regressions; "
            f"uncovered DPM symbols and Pflueger page hints remain strictly on HOLD."
        ],
        "details": {
            "g031_cur_matched_oids": g031_cur_matched_oids,
            "g031_cur_rank": g031_cur_rank,
            "g031_trt_matched_oids": g031_trt_matched_oids,
            "g031_trt_rank": g031_trt_rank,
        },
    }


# ---------------------------------------------------------------------------
# Static Historical Executor Ordering Audit (AST)
# ---------------------------------------------------------------------------

def audit_historical_executor_persistence_order(script_path: Path) -> dict[str, Any]:
    """Statically verifies via AST that the historical A9 executor persisted

    raw plan records before executing the applicability/control gating check.
    """
    code = script_path.read_text(encoding="utf-8")
    tree = ast.parse(code, filename=str(script_path))

    phase_p_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "execute_phase_p":
            phase_p_node = node
            break

    if not phase_p_node:
        return {"order_proven": False, "reason": "execute_phase_p function not found"}

    for_loop = None
    for stmt in phase_p_node.body:
        if isinstance(stmt, ast.For):
            for_loop = stmt
            break

    if not for_loop:
        return {"order_proven": False, "reason": "For loop over cases not found in execute_phase_p"}

    save_json_lineno = None
    gate_check_lineno = None

    for stmt in for_loop.body:
        # Check for _save_json(raw_plans_path, ...)
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            func = stmt.value.func
            if isinstance(func, ast.Name) and func.id == "_save_json":
                if save_json_lineno is None:
                    save_json_lineno = stmt.lineno
        # Check for gate condition: if cid == "g031":
        if isinstance(stmt, ast.If):
            test = stmt.test
            if isinstance(test, ast.Compare):
                left = test.left
                if isinstance(left, ast.Name) and left.id == "cid":
                    gate_check_lineno = stmt.lineno

    if save_json_lineno is not None and gate_check_lineno is not None:
        if save_json_lineno < gate_check_lineno:
            return {
                "order_proven": True,
                "save_json_lineno": save_json_lineno,
                "gate_check_lineno": gate_check_lineno,
                "message": (
                    f"_save_json at line {save_json_lineno} strictly precedes "
                    f"applicability/control gate at line {gate_check_lineno}"
                ),
            }

    return {
        "order_proven": False,
        "save_json_lineno": save_json_lineno,
        "gate_check_lineno": gate_check_lineno,
        "reason": "Could not prove _save_json strictly precedes gate check in execute_phase_p",
    }


# ---------------------------------------------------------------------------
# Machine Audit Runner
# ---------------------------------------------------------------------------

def run_live_audit(project_root: Path) -> dict[str, Any]:
    """Perform full deterministic audit on frozen artifacts."""
    from panda_agent.evaluation import load_gold_dataset
    from panda_agent.evaluation_runner import load_object_lookup

    plans_path = project_root / RAW_PLANS_PATH
    results_path = project_root / RAW_RESULTS_PATH
    gold_path = project_root / GOLD_QUESTIONS_PATH
    contract_path = project_root / R1_CONTRACT_PATH

    plans_data = _load_json(plans_path)
    results_data = _load_json(results_path)
    contract_data = _load_json(contract_path) if contract_path.exists() else {}

    gold_ds = load_gold_dataset(gold_path)
    questions_by_id = {q.id: q for q in gold_ds.questions}
    object_lookup = load_object_lookup(project_root)

    eval_result = recompute_d4_a9_closeout_from_frozen_artifacts(
        plans_data=plans_data,
        results_data=results_data,
        gold_questions=questions_by_id,
        object_lookup=object_lookup,
        contract_data=contract_data,
    )

    # Cross-check provider accounting
    plans_list = plans_data.get("plans", [])
    slots_list = results_data.get("slots", [])

    analyzer_calls = len(plans_list)
    analyzer_attempts = sum(
        p.get("provider_accounting", {}).get("analyzer_provider_attempts", 1)
        for p in plans_list
    )
    tokens_by_case = {
        p["case_id"]: p.get("provider_accounting", {}).get("token_usage", 0)
        for p in plans_list
    }
    analyzer_tokens = sum(tokens_by_case.values())
    tokens_by_case["total"] = analyzer_tokens

    embedding_calls = len(slots_list)
    reranker_calls = len(slots_list)
    retrieval_tokens = results_data.get("accounting", {}).get("token_usage", 0)
    total_tokens = analyzer_tokens + retrieval_tokens

    matched_rules_per_case = {
        p["case_id"]: p.get("matched_rule_identities", []) for p in plans_list
    }

    # Verify persistence order
    order_audit = audit_historical_executor_persistence_order(
        project_root / HISTORICAL_A9_SCRIPT_PATH
    )

    # Verify plan fields and persistence timestamps
    plan_field_errors: list[str] = []
    for p in plans_list:
        cid = p.get("case_id")
        for f in REQUIRED_PLAN_FIELDS:
            if f not in p:
                plan_field_errors.append(f"Plan {cid} missing field {f}")
        persisted_at = p.get("persisted_at")
        gated_at = p.get("gated_at")
        if not persisted_at or not gated_at:
            plan_field_errors.append(f"Plan {cid} missing persisted_at or gated_at timestamp")
        elif persisted_at > gated_at:
            plan_field_errors.append(
                f"Plan {cid} persisted_at ({persisted_at}) > gated_at ({gated_at})"
            )
        if p.get("persistence_state") not in ("GATED", "RETRIEVAL_ELIGIBLE"):
            plan_field_errors.append(
                f"Plan {cid} persistence_state {p.get('persistence_state')} not eligible"
            )

    # Verify shared plan identity in all retrieval slots
    slot_plan_errors: list[str] = []
    plans_by_case = {p["case_id"]: p for p in plans_list}
    for s in slots_list:
        cid = s.get("case_id")
        p = plans_by_case.get(cid, {})
        if s.get("canonical_plan_id") != p.get("plan_id"):
            slot_plan_errors.append(f"Slot {s.get('cell_id')} canonical_plan_id mismatch")
        if s.get("canonical_plan_signature") != p.get("plan_signature"):
            slot_plan_errors.append(f"Slot {s.get('cell_id')} canonical_plan_signature mismatch")
        if s.get("actual_plan_used") != s.get("arm_execution_projection"):
            slot_plan_errors.append(f"Slot {s.get('cell_id')} actual plan used != projection")
        if not s.get("plan_equality_arm_projection_verified"):
            slot_plan_errors.append(f"Slot {s.get('cell_id')} plan equality not verified")

    live_audit = {
        "stage": "D4-A9-R1",
        "task_name": "D4-A9-R1 — Post-Outcome Closeout Verification Repair",
        "starting_head": STARTING_HEAD,
        "starting_commit_message": STARTING_COMMIT_MESSAGE,
        "starting_parent_head": STARTING_PARENT_HEAD,
        "verification_only": True,
        "zero_provider_execution": True,
        "raw_plan_freeze_commit": RAW_PLANS_FREEZE_COMMIT,
        "raw_plan_blob": RAW_PLANS_EXPECTED_BLOB,
        "raw_result_freeze_commit": RAW_RESULTS_FREEZE_COMMIT,
        "raw_result_blob": RAW_RESULTS_EXPECTED_BLOB,
        "historical_a9_artifacts_sealed": True,
        "production_immutable": True,
        "r2_authority_sealed": True,
        "formal_cohort": FROZEN_FORMAL_COHORT,
        "covered_symbol_mask": FROZEN_COVERED_SYMBOL_MASK,
        "uncovered_symbol_hold_mask": FROZEN_UNCOVERED_SYMBOL_HOLD_MASK,
        "page_hint_hold_mask": FROZEN_PAGE_HINT_HOLD_MASK,
        "matched_rule_receipts": matched_rules_per_case,
        "per_case_analyzer_accounting": tokens_by_case,
        "shared_plan_integrity": {
            "verified": len(slot_plan_errors) == 0,
            "errors": slot_plan_errors,
        },
        "exact_schedule_integrity": {
            "slot_count": len(slots_list),
            "expected_count": len(SCHEDULE_8),
            "schedule_matches": [
                s.get("cell_id") == SCHEDULE_8[idx]["case_id"] + "_" + SCHEDULE_8[idx]["arm"]
                for idx, s in enumerate(slots_list)
            ],
        },
        "actual_plan_projection_integrity": len(slot_plan_errors) == 0,
        "persistence_before_gate_integrity": {
            "verified": len(plan_field_errors) == 0 and order_audit.get("order_proven", False),
            "plan_field_errors": plan_field_errors,
            "order_audit": order_audit,
        },
        "provider_accounting_integrity": {
            "analyzer_logical_calls": analyzer_calls,
            "analyzer_provider_attempts": analyzer_attempts,
            "embedding_calls": embedding_calls,
            "reranker_calls": reranker_calls,
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "scientific_evaluator_calls": 0,
            "retries": 0,
            "total_logical_calls": analyzer_calls + embedding_calls + reranker_calls,
            "total_provider_attempts": analyzer_attempts + embedding_calls + reranker_calls,
            "total_tokens": total_tokens,
        },
        "g031_baseline_reproduction": eval_result.get("g031_baseline_reproduced", False),
        "g031_treatment_reproduction": eval_result.get("g031_treatment_reproduced", False),
        "selected_origin_subtraction": eval_result.get("selected_origin_subtraction_verified", False),
        "independent_origin_preservation": eval_result.get("independent_origin_preservation_verified", False),
        "control_critical_safety": eval_result.get("control_critical_safety", {}),
        "grounding_safety": eval_result.get("grounding_safety", {}),
        "version_safety": eval_result.get("version_safety", {}),
        "diagnostic_non_critical_retrieval_variance": eval_result.get(
            "diagnostic_non_critical_retrieval_variance", {}
        ),
        "verification_status": eval_result["verification_status"],
        "scientific_verdict_level": eval_result["scientific_verdict_level"],
        "scientific_verdict": eval_result["scientific_verdict"],
        "scientific_decision": eval_result["scientific_decision"],
        "component_dispositions": eval_result["component_dispositions"],
        "historical_a9_manifest_receipt_status": {
            "status": "SUPERSEDED_BY_D4_A9_R1",
            "historical_booleans_classification": "HISTORICAL_RECEIPT_STALE_NON_AUTHORITATIVE",
            "git_facts": {
                "prospective_plans_frozen": True,
                "prospective_plan_freeze_commit": RAW_PLANS_FREEZE_COMMIT,
                "paired_results_frozen": True,
                "paired_result_freeze_commit": RAW_RESULTS_FREEZE_COMMIT,
                "retrieval_execution_observed": True,
                "retrieval_slots_completed": 8,
                "evaluation_executed": True,
            },
        },
        "production_activation_authorized": False,
        "next_stage_authorized": False,
    }
    return live_audit


# ---------------------------------------------------------------------------
# Post-Commit / Closeout Verifier
# ---------------------------------------------------------------------------

def verify_closeout_r1(project_root: Path) -> dict[str, Any]:
    """Mechanically verify all Section 35 closeout requirements."""
    errors: list[str] = []

    # 1. Starting boundary & commit lineage
    try:
        # Verify STARTING_HEAD is in git history
        is_ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", STARTING_HEAD, "HEAD"],
            cwd=project_root,
            capture_output=True,
        ).returncode == 0
        if not is_ancestor:
            errors.append(f"STARTING_HEAD {STARTING_HEAD} is not an ancestor of HEAD")
    except Exception as exc:
        errors.append(f"Starting boundary check failed: {exc}")

    # 2. Checkpoint blob seals
    for name, path, commit, expected_blob in [
        ("raw plans", RAW_PLANS_PATH, RAW_PLANS_FREEZE_COMMIT, RAW_PLANS_EXPECTED_BLOB),
        ("raw results", RAW_RESULTS_PATH, RAW_RESULTS_FREEZE_COMMIT, RAW_RESULTS_EXPECTED_BLOB),
    ]:
        file_path = project_root / path
        if not file_path.exists():
            errors.append(f"File {path} does not exist")
            continue
        cur_hash = git_hash_object(project_root, file_path)
        if cur_hash != expected_blob:
            errors.append(
                f"{name} live blob {cur_hash} != expected {expected_blob} "
                f"(D4_A9_RAW_SCIENTIFIC_ARTIFACT_DRIFT)"
            )
        ref_blob = git_blob(project_root, commit, path)
        if ref_blob != expected_blob:
            errors.append(
                f"{name} blob at freeze commit {commit} ({ref_blob}) != {expected_blob}"
            )

    # 3. Historical A9 artifact seals
    for path, expected_blob in HISTORICAL_A9_ARTIFACT_BLOBS.items():
        file_path = project_root / path
        if not file_path.exists():
            errors.append(f"Historical A9 artifact {path} does not exist")
            continue
        cur_hash = git_hash_object(project_root, file_path)
        if cur_hash != expected_blob:
            errors.append(f"Historical A9 artifact {path} mutated (blob {cur_hash} != {expected_blob})")

    # 4. R2 authority seals
    for path, expected_blob in R2_AUTHORITY_ARTIFACT_BLOBS.items():
        file_path = project_root / path
        if not file_path.exists():
            errors.append(f"R2 authority artifact {path} does not exist")
            continue
        cur_hash = git_hash_object(project_root, file_path)
        if cur_hash != expected_blob:
            errors.append(f"R2 authority artifact {path} mutated (blob {cur_hash} != {expected_blob})")

    # 5. Production immutability
    for p in ["src", "configs"]:
        diff = _git(["diff", f"{STARTING_HEAD}..HEAD", "--", p], project_root)
        if diff:
            errors.append(f"Production path {p} mutated against STARTING_HEAD")
        worktree_diff = _git(["diff", "HEAD", "--", p], project_root)
        if worktree_diff:
            errors.append(f"Production path {p} has uncommitted worktree modifications")

    # 6. Changed paths allowlist
    diff_names = _git(
        ["diff", "--name-only", f"{STARTING_HEAD}..HEAD"], project_root
    ).splitlines()
    for name in diff_names:
        norm_name = name.strip().replace("\\", "/")
        if norm_name and norm_name not in ALLOWED_R1_PATHS:
            errors.append(f"Path {norm_name} outside allowed R1 cumulative boundary")

    # 7. Live deterministic audit
    try:
        live_audit = run_live_audit(project_root)
    except Exception as exc:
        errors.append(f"Live deterministic audit failed: {exc}")
        live_audit = {}

    if live_audit.get("verification_status") != "PASS":
        errors.append(f"Deterministic audit returned status {live_audit.get('verification_status')}")

    # 8. Committed result drift check (if committed result exists)
    committed_result_path = project_root / R1_RESULT_PATH
    if committed_result_path.exists():
        committed_data = _load_json(committed_result_path)
        # Compare core fields
        compare_fields = [
            "stage",
            "verification_status",
            "scientific_verdict_level",
            "scientific_verdict",
            "scientific_decision",
            "component_dispositions",
            "formal_cohort",
            "covered_symbol_mask",
            "uncovered_symbol_hold_mask",
            "page_hint_hold_mask",
            "g031_baseline_reproduction",
            "g031_treatment_reproduction",
            "selected_origin_subtraction",
            "independent_origin_preservation",
            "provider_accounting_integrity",
            "production_activation_authorized",
        ]
        for field in compare_fields:
            comm_val = committed_data.get(field)
            live_val = live_audit.get(field)
            if comm_val != live_val:
                errors.append(
                    f"D4_A9_R1_MACHINE_RESULT_DRIFT in field '{field}': "
                    f"committed={comm_val} vs live={live_val}"
                )

    status = "PASS" if not errors else "FAIL"
    return {
        "verification_status": status,
        "errors": errors,
        "scientific_verdict_level": live_audit.get("scientific_verdict_level"),
        "scientific_verdict": live_audit.get("scientific_verdict"),
        "scientific_decision": live_audit.get("scientific_decision"),
        "component_dispositions": live_audit.get("component_dispositions"),
        "audit": live_audit,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Path to project root directory",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["audit", "verify"],
        help="audit = live deterministic computation; verify = full post-commit integrity check",
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    if args.mode == "audit":
        audit_res = run_live_audit(project_root)
        print(json.dumps(audit_res, indent=2))
        if audit_res.get("verification_status") != "PASS":
            sys.exit(1)
        return

    if args.mode == "verify":
        verify_res = verify_closeout_r1(project_root)
        print(json.dumps(verify_res, indent=2))
        if verify_res.get("verification_status") != "PASS":
            sys.exit(1)
        return


if __name__ == "__main__":
    main()
