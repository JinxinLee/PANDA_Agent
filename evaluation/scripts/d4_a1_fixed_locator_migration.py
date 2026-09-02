"""PANDA Agent D4-A1 — First-Batch Fixed-Locator Migration Prototype.

Pre-exposure implementation freeze only.
Authoritative contract: evaluation/d4_a0_batch1_migration_preregistration.json
plus D4-A1 specification.

Isolates and migrates the fixed-location dependency (file paths, source paths,
macros, paper-page hints) of the two confirmed legacy-dependent rules:
  1. event_poca_handoff (4 symbols + li_2026:131,138 page hints)
  2. restgas_profile_workflow (5 symbols)
while preserving domain terminology (triggers), generic repository scope, and
domain concepts. Replaces them with the generic structured bridge path
(D2 governed resolution -> D1 accepted graph -> provenance materialization ->
d3_5_selectivity_v2 with caps 8/4 -> K=3 reserved rerank admission).

CLI (run with PYTHONPATH=src):
    python evaluation/scripts/d4_a1_fixed_locator_migration.py --project-root . --mode audit-invariants
    python evaluation/scripts/d4_a1_fixed_locator_migration.py --project-root . --mode execute-21
    python evaluation/scripts/d4_a1_fixed_locator_migration.py --project-root . --mode evaluate
"""

from __future__ import annotations

import argparse
import copy
from collections import defaultdict
from collections.abc import Sequence
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

from dotenv import load_dotenv

# Ensure evaluation/scripts and src are on sys.path
_EVAL_SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _EVAL_SCRIPTS_DIR.parent.parent
if str(_EVAL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_SCRIPTS_DIR))
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import d3_5_a5_r2_selectivity as a5_r2
import d3_5_a6_phase1_admission as a6_p1
from panda_agent.config import QueryExpansions, load_query_expansions
from panda_agent.d3_structured import (
    build_structured_contribution_from_storage,
)
from panda_agent.evaluation import _matched_evidence_groups, load_gold_dataset
from panda_agent.evaluation_runner import load_object_lookup
from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.prompts import QUERY_ANALYZER_SYSTEM_PROMPT, RERANK_SYSTEM_PROMPT
from panda_agent.retrieval import Retriever, select_final_evidence


STARTING_HEAD = "feecfdbebd933fbcf679b65432bd54d699594ecb"

MANIFEST_PATH = "evaluation/d4_a1_execution_manifest.json"
PREREGISTRATION_PATH = "evaluation/d4_a0_batch1_migration_preregistration.json"
RAW_RESULTS_PATH = "evaluation/d4_a1_raw_three_arm_results.json"
EVALUATOR_RESULTS_PATH = "evaluation/d4_a1_evaluator_results.json"

GOLD_QUESTIONS_PATH = "evaluation/benchmarks/v2_6/gold_questions.yaml"
NOVEL_DEV_PATH = "evaluation/novel/v1/novel_dev.yaml"
CONFIG_QUERY_EXPANSIONS_PATH = "configs/query_expansions.yaml"

EXPECTED_MODEL = "gemini-3.8-flash"
EXPECTED_TEMPERATURE = 0.0

CASE_ORDER = ["g036", "g021", "n006", "g041", "g020", "n004", "n022"]
ARMS = ["LEGACY_CONTROL", "BATCH1_ABLATION", "BATCH1_REPLACEMENT"]
TOTAL_FORMAL_SLOTS = 21

FROZEN_A6_SAFETY_GROUPS = [
    "n006.e1",
    "g041.e1",
    "g020.e1",
    "g020.e2",
    "n004.e1",
]

ELIGIBLE_BRIDGE_STATUSES = {
    "BRIDGED_CANDIDATE_INJECTED",
    "BRIDGED_CANDIDATE_RANKED_OUT",
}
NON_CANDIDATE_BRIDGE_STATUSES = {
    "GOVERNED_PROVENANCE_NOT_FOUND",
    "GOVERNED_PROVENANCE_INVALID",
    "PROVENANCE_SOURCE_OBJECT_NOT_FOUND",
    "PROVENANCE_SOURCE_OBJECT_AMBIGUOUS",
    "VERSION_SCOPE_CONFLICT",
}

ALLOWED_COMMIT_A_FILES = {
    "evaluation/scripts/d4_a1_fixed_locator_migration.py",
    "tests/unit/test_d4_a1_fixed_locator_migration.py",
    "evaluation/d4_a1_execution_manifest.json",
}

# Exact Batch-1 targeted components for suppression
SUPPRESSED_SYMBOLS_EVENT_POCA = [
    "macro/target/ana_dpm.C",
    "macro/target/prod_aod_complete.C",
    "POCA_VERTEX_FILE",
    "PndPidCorrelator",
]
SUPPRESSED_PAGE_HINTS_EVENT_POCA = {"li_2026": [131, 138]}

SUPPRESSED_SYMBOLS_RESTGAS = [
    "pgenerators/Target/PndTargetGenerator.cxx",
    "macro/target/prod_sim_hvmaps.C",
    "macro/target/reco_complete.C",
    "macro/target/ana_complete.C",
    "macro/target/correction/efficiency_correction_2.C",
]
SUPPRESSED_PAGE_HINTS_RESTGAS: dict[str, list[int]] = {}

# Exact preserved components
PRESERVED_TRIGGERS_EVENT_POCA = [
    "event_poca",
    "poca_vertex_file",
    "second-pass pid",
    "第二遍 pid",
]
PRESERVED_REPOS_EVENT_POCA = ["restgas_determination", "pandaroot"]
PRESERVED_CONCEPTS_EVENT_POCA = [
    "event POCA handoff",
    "event-aligned second-pass propagation",
]

PRESERVED_TRIGGERS_RESTGAS = [
    "restgas_profile",
    "restgas profile",
    "corrected rho",
    "修正后的 rho",
]
PRESERVED_REPOS_RESTGAS = ["restgas_determination", "pandaroot"]
PRESERVED_CONCEPTS_RESTGAS = [
    "distributed target generation",
    "longitudinal profile correction",
]

# Per-rule vocabulary constants (exact user contract)
DECISION_REPLACEMENT_VALIDATED = "REPLACEMENT_VALIDATED"
DECISION_LEGACY_DEPENDENCY_NOT_REPRODUCED = "LEGACY_DEPENDENCY_NOT_REPRODUCED"
DECISION_REPLACEMENT_FAILED = "REPLACEMENT_FAILED"
DECISION_LEGACY_CONTROL_REFERENCE_NOT_REPRODUCED = (
    "LEGACY_CONTROL_REFERENCE_NOT_REPRODUCED"
)
FROZEN_DECISION_VOCABULARY = {
    DECISION_REPLACEMENT_VALIDATED,
    DECISION_LEGACY_DEPENDENCY_NOT_REPRODUCED,
    DECISION_REPLACEMENT_FAILED,
    DECISION_LEGACY_CONTROL_REFERENCE_NOT_REPRODUCED,
}

# 7-level batch verdict constants (exact user contract)
VERDICT_INVALID_PROTOCOL = "INVALID / PROTOCOL_OR_TREATMENT_CONSTRUCTION_FAILED"
VERDICT_FAIL_SAFETY_REGRESSION = "FAIL / MATERIAL_SAFETY_REGRESSION"
VERDICT_PASS = "PASS / FIRST_BATCH_FIXED_LOCATOR_REPLACEMENT_VALIDATED_FOR_DEVELOPMENT"
VERDICT_PARTIAL_MIXED_EVIDENCE = "PARTIAL / MIXED_TARGET_REPLACEMENT_EVIDENCE"
VERDICT_PARTIAL_LEGACY_DEP_NOT_REPRODUCED = (
    "PARTIAL / LEGACY_DEPENDENCY_NOT_REPRODUCED_IN_CURRENT_PROTOTYPE"
)
VERDICT_FAIL_REPLACEMENT_FAILED = (
    "FAIL / FIXED_LOCATOR_REPLACEMENT_DID_NOT_RECOVER_CONFIRMED_DEPENDENCY"
)
VERDICT_INCONCLUSIVE_LEGACY_CONTROL = (
    "INCONCLUSIVE / LEGACY_CONTROL_REFERENCE_NOT_REPRODUCED"
)

FROZEN_BATCH_VERDICTS = [
    VERDICT_INVALID_PROTOCOL,
    VERDICT_FAIL_SAFETY_REGRESSION,
    VERDICT_PASS,
    VERDICT_PARTIAL_MIXED_EVIDENCE,
    VERDICT_PARTIAL_LEGACY_DEP_NOT_REPRODUCED,
    VERDICT_FAIL_REPLACEMENT_FAILED,
    VERDICT_INCONCLUSIVE_LEGACY_CONTROL,
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_head(project_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip()
    except Exception as exc:
        return f"UNKNOWN ({exc})"


def verify_drift_guards(
    project_root: Path, *, require_clean_worktree: bool = False
) -> dict[str, Any]:
    """Enforces implementation/config drift guards:
    - Protected src/ and configs/ are completely unchanged from STARTING_HEAD.
    - Only the three allowed Commit-A files are modified between STARTING_HEAD and HEAD.
    - Worktree is clean for all frozen implementation/config paths (when require_clean_worktree=True).
    """
    diff_protected = subprocess.run(
        ["git", "diff", "--name-only", STARTING_HEAD, "--", "src", "configs"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    changed_protected = [
        f.strip().replace("\\", "/")
        for f in diff_protected.stdout.splitlines()
        if f.strip()
    ]
    if changed_protected:
        raise RuntimeError(
            f"Protected src/ or configs/ modified relative to STARTING_HEAD: {changed_protected}"
        )

    diff_head = subprocess.run(
        ["git", "diff", "--name-only", f"{STARTING_HEAD}..HEAD"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    changed_head = [
        f.strip().replace("\\", "/")
        for f in diff_head.stdout.splitlines()
        if f.strip()
    ]
    disallowed_head = [f for f in changed_head if f not in ALLOWED_COMMIT_A_FILES]
    if disallowed_head:
        raise RuntimeError(
            f"Disallowed files modified in Commit-A: {disallowed_head}. "
            f"Only {ALLOWED_COMMIT_A_FILES} are allowed."
        )

    status_proc = subprocess.run(
        [
            "git", "status", "--porcelain",
            "src", "configs",
            *ALLOWED_COMMIT_A_FILES,
        ],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    dirty_files = [line.strip() for line in status_proc.stdout.splitlines() if line.strip()]
    if require_clean_worktree and dirty_files:
        raise RuntimeError(
            f"Worktree is dirty for frozen implementation/config paths: {dirty_files}"
        )

    current_head = _git_head(project_root)
    return {
        "verified": True,
        "starting_head": STARTING_HEAD,
        "current_head": current_head,
        "dirty_frozen_paths": dirty_files,
    }


# ===========================================================================
# 1. In-Memory Component Mask
# ===========================================================================

def apply_batch1_in_memory_mask(query_expansions: QueryExpansions) -> QueryExpansions:
    """Evaluation-only in-memory component mask mechanically deep-copied from
    the current parsed query_expansions config.

    Suppresses exactly:
      - 4 symbols in event_poca_handoff: macro/target/ana_dpm.C, macro/target/prod_aod_complete.C,
        POCA_VERTEX_FILE, PndPidCorrelator
      - paper_page_hints li_2026: [131, 138] in event_poca_handoff
      - 5 symbols in restgas_profile_workflow: pgenerators/Target/PndTargetGenerator.cxx,
        macro/target/prod_sim_hvmaps.C, macro/target/reco_complete.C, macro/target/ana_complete.C,
        macro/target/correction/efficiency_correction_2.C

    Preserves:
      - Target triggers, repositories, and concepts in both target rules
      - Source object immutability (original QueryExpansions remains byte/field unchanged)
      - All non-target rules untouched
      - Double application deterministic (idempotent)
    """
    dumped = query_expansions.model_dump(mode="python")
    target_symbols_event_poca = set(SUPPRESSED_SYMBOLS_EVENT_POCA)
    target_symbols_restgas = set(SUPPRESSED_SYMBOLS_RESTGAS)
    target_pages_event_poca = set(SUPPRESSED_PAGE_HINTS_EVENT_POCA.get("li_2026", []))

    for rule in dumped.get("rules", []):
        rid = rule.get("rule_id")
        if rid == "event_poca_handoff":
            # Filter symbols
            rule["symbols"] = [
                s for s in rule.get("symbols", []) if s not in target_symbols_event_poca
            ]
            # Filter page hints
            hints = dict(rule.get("paper_page_hints") or {})
            if "li_2026" in hints:
                hints["li_2026"] = [
                    p for p in hints["li_2026"] if p not in target_pages_event_poca
                ]
                if not hints["li_2026"]:
                    del hints["li_2026"]
            rule["paper_page_hints"] = hints
        elif rid == "restgas_profile_workflow":
            # Filter symbols
            rule["symbols"] = [
                s for s in rule.get("symbols", []) if s not in target_symbols_restgas
            ]
            # Page hints already empty

    return QueryExpansions.model_validate(dumped)


# ===========================================================================
# 2. A0 Overlap Revalidation
# ===========================================================================

def revalidate_a0_overlaps(project_root: Path) -> dict[str, Any]:
    """Revalidate A0 overlap findings on the current query_expansions config.
    Fails closed on any drift or active overlap on migration target cases.
    """
    config_path = project_root / CONFIG_QUERY_EXPANSIONS_PATH
    query_expansions = load_query_expansions(config_path)
    rules = query_expansions.rules

    # Load preregistration authority to check overlap registry
    prereg_path = project_root / PREREGISTRATION_PATH
    prereg = _load_json(prereg_path)
    expected_findings = prereg["batch1"]["overlap_accounting"]["target_case_activity_findings"]

    target_cases_queries = {
        "g036": "Which macro produces event_poca?",
        "g021": "How is restgas_profile supplied to distributed-target simulation?",
        "n022": (
            "The restgas analysis determines the event vertex through a two-step POCA workflow. "
            "What does the first worker step leave behind for the second analysis step, and how is "
            "the fitted vertex fed into the reprocessing?"
        ),
    }

    # Audit the 10 targeted locators
    targeted_locators = [
        "macro/target/ana_dpm.C",
        "macro/target/prod_aod_complete.C",
        "POCA_VERTEX_FILE",
        "PndPidCorrelator",
        ("li_2026", [131, 138]),
        "pgenerators/Target/PndTargetGenerator.cxx",
        "macro/target/prod_sim_hvmaps.C",
        "macro/target/reco_complete.C",
        "macro/target/ana_complete.C",
        "macro/target/correction/efficiency_correction_2.C",
    ]

    locator_overlapping_rules: dict[str, list[str]] = {}
    for loc in targeted_locators:
        key = loc if isinstance(loc, str) else "paper_page_hints: li_2026 [131, 138]"
        overlapping: list[str] = []
        for r in rules:
            if r.rule_id in ("event_poca_handoff", "restgas_profile_workflow"):
                continue
            if isinstance(loc, str):
                if loc in r.symbols:
                    overlapping.append(r.rule_id)
            else:
                hints = r.paper_page_hints.get(loc[0], [])
                if any(p in hints for p in loc[1]):
                    overlapping.append(r.rule_id)
        locator_overlapping_rules[key] = overlapping

    # Check case activity
    case_activity: dict[str, dict[str, Any]] = {}
    for cid, query in target_cases_queries.items():
        lowered = query.casefold()
        triggered_rules: list[str] = []
        overlapping_rules_triggered: list[str] = []

        for r in rules:
            if any(str(tr).casefold() in lowered for tr in r.triggers):
                triggered_rules.append(r.rule_id)
                # Check if this rule is an overlapping locator rule
                is_overlap = any(
                    r.rule_id in rules_list
                    for rules_list in locator_overlapping_rules.values()
                )
                if is_overlap:
                    overlapping_rules_triggered.append(r.rule_id)

        overlap_active = len(overlapping_rules_triggered) > 0
        expected = expected_findings.get(cid, {})
        if overlap_active != expected.get("overlap_active", False):
            raise ValueError(
                f"Overlap drift detected on case {cid}: expected overlap_active="
                f"{expected.get('overlap_active')}, got {overlap_active} "
                f"({overlapping_rules_triggered})"
            )

        case_activity[cid] = {
            "query": query,
            "triggered_rules": triggered_rules,
            "overlapping_rules_triggered": overlapping_rules_triggered,
            "overlap_active": overlap_active,
            "identifiability_action": "NO_ACTION_NOT_ACTIVE" if not overlap_active else "TREATMENT_MASK_EQUIVALENT_LOCATOR_ON_TARGET_CASE",
        }

    return {
        "verified": True,
        "rules_audited_count": len(rules),
        "target_case_activity": case_activity,
        "locator_overlapping_rules_counts": {
            k: len(v) for k, v in locator_overlapping_rules.items()
        },
    }


# ===========================================================================
# 3. Deterministic Pre-Exposure Audit
# ===========================================================================

def audit_invariants(project_root: Path) -> dict[str, Any]:
    """Mandatory deterministic pre-exposure verification:
    - Environment model selection resolves to gemini-3.8-flash per frozen contract.
    - Revalidates A0 overlaps on current query_expansions config (fails closed).
    - Verifies in-memory component mask immutability, suppression, and determinism.
    - Verifies execution manifest: 21 slots in case-major order, NOT_EXECUTED state, 0 pre-exposure accounting.
    - Absolutely no provider or retrieval calls.
    """
    load_dotenv(project_root / ".env")
    settings = VertexSettings.from_env()
    if settings.generation_model != EXPECTED_MODEL:
        raise ValueError(
            f"QA_GENERATION_MODEL_ID mismatch: expected '{EXPECTED_MODEL}', got '{settings.generation_model}'"
        )

    # 1. Overlap revalidation
    overlap_receipt = revalidate_a0_overlaps(project_root)

    # 2. In-memory component mask verification
    original_qe = load_query_expansions(project_root / CONFIG_QUERY_EXPANSIONS_PATH)
    masked_qe = apply_batch1_in_memory_mask(original_qe)
    masked_twice = apply_batch1_in_memory_mask(masked_qe)

    # Check immutability: original must still have target symbols and page hints
    orig_ep = next(r for r in original_qe.rules if r.rule_id == "event_poca_handoff")
    orig_rg = next(r for r in original_qe.rules if r.rule_id == "restgas_profile_workflow")
    if orig_ep.symbols != SUPPRESSED_SYMBOLS_EVENT_POCA:
        raise ValueError("Source QueryExpansions event_poca_handoff symbols were mutated!")
    if orig_ep.paper_page_hints != SUPPRESSED_PAGE_HINTS_EVENT_POCA:
        raise ValueError("Source QueryExpansions event_poca_handoff page hints were mutated!")
    if orig_rg.symbols != SUPPRESSED_SYMBOLS_RESTGAS:
        raise ValueError("Source QueryExpansions restgas_profile_workflow symbols were mutated!")

    # Check suppression in masked object
    mask_ep = next(r for r in masked_qe.rules if r.rule_id == "event_poca_handoff")
    mask_rg = next(r for r in masked_qe.rules if r.rule_id == "restgas_profile_workflow")
    if mask_ep.symbols != []:
        raise ValueError(f"Masked event_poca_handoff symbols not empty: {mask_ep.symbols}")
    if mask_ep.paper_page_hints != {}:
        raise ValueError(f"Masked event_poca_handoff page hints not empty: {mask_ep.paper_page_hints}")
    if mask_rg.symbols != []:
        raise ValueError(f"Masked restgas_profile_workflow symbols not empty: {mask_rg.symbols}")

    # Check preservation in masked object
    if mask_ep.triggers != PRESERVED_TRIGGERS_EVENT_POCA:
        raise ValueError("Masked event_poca_handoff triggers not preserved!")
    if mask_ep.repositories != PRESERVED_REPOS_EVENT_POCA:
        raise ValueError("Masked event_poca_handoff repositories not preserved!")
    if mask_ep.concepts != PRESERVED_CONCEPTS_EVENT_POCA:
        raise ValueError("Masked event_poca_handoff concepts not preserved!")
    if mask_rg.triggers != PRESERVED_TRIGGERS_RESTGAS:
        raise ValueError("Masked restgas_profile_workflow triggers not preserved!")
    if mask_rg.repositories != PRESERVED_REPOS_RESTGAS:
        raise ValueError("Masked restgas_profile_workflow repositories not preserved!")
    if mask_rg.concepts != PRESERVED_CONCEPTS_RESTGAS:
        raise ValueError("Masked restgas_profile_workflow concepts not preserved!")

    # Check determinism (idempotence)
    if masked_qe.model_dump() != masked_twice.model_dump():
        raise ValueError("In-memory component mask double application is not deterministic!")

    # 3. Execution manifest verification
    manifest_path = project_root / MANIFEST_PATH
    if not manifest_path.exists():
        raise FileNotFoundError(f"Execution manifest {manifest_path} missing")
    manifest = _load_json(manifest_path)

    slots = manifest.get("formal_slots_21", [])
    if len(slots) != TOTAL_FORMAL_SLOTS:
        raise ValueError(f"Manifest formal slots mismatch: expected {TOTAL_FORMAL_SLOTS}, got {len(slots)}")

    # Check exact case-major schedule
    idx = 0
    for cid in CASE_ORDER:
        for arm in ARMS:
            idx += 1
            s = slots[idx - 1]
            if (s["slot_index"], s["case_id"], s["arm"]) != (idx, cid, arm):
                raise ValueError(f"Schedule mismatch at slot {idx}: got {s}")
            if s["outcome_status"] != "NOT_EXECUTED":
                raise ValueError(f"Slot {idx} status is not NOT_EXECUTED: {s['outcome_status']}")

    # Check outcome exposure state
    exposure_state = manifest.get("outcome_exposure_state", {})
    if exposure_state.get("D4_A1_OUTCOME_EXPOSURE") != "NOT_STARTED":
        raise ValueError("Manifest D4_A1_OUTCOME_EXPOSURE is not NOT_STARTED")
    if exposure_state.get("formal_slots_completed") != 0:
        raise ValueError("Manifest formal_slots_completed != 0")
    if exposure_state.get("evaluator_executed") is not False:
        raise ValueError("Manifest evaluator_executed is not False")
    if exposure_state.get("migration_verdict_computed") is not False:
        raise ValueError("Manifest migration_verdict_computed is not False")

    # Check pre-exposure accounting
    accounting = manifest.get("pre_exposure_accounting", {})
    for counter, val in accounting.items():
        if val != 0:
            raise ValueError(f"Pre-exposure accounting counter {counter} != 0: {val}")

    # 4. Drift guards verification
    drift_receipt = verify_drift_guards(project_root, require_clean_worktree=False)

    return {
        "verified": True,
        "qa_generation_model_id": settings.generation_model,
        "rules_audited": len(original_qe.rules),
        "target_cases_revalidated": list(CASE_ORDER[:2]) + ["n022"],
        "formal_slots_count": len(slots),
        "pre_exposure_exposure_state": exposure_state.get("D4_A1_OUTCOME_EXPOSURE"),
        "pre_exposure_accounting_zero": True,
        "drift_guards_verified": drift_receipt["verified"],
    }


# ===========================================================================
# 4. Generic Structured Replacement & K=3 Admission Helpers
# ===========================================================================

def build_eligible_bridge_candidates(
    bridge_receipts: list[dict[str, Any]],
    reachability_receipts: list[dict[str, Any]],
    object_lookup: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Constructs the eligible governed candidate universe from structured
    bridge receipts and reachability receipts.

    Filters eligible bridge receipts to ELIGIBLE_BRIDGE_STATUSES (INJECTED and
    RANKED_OUT candidate statuses), aggregates all provenance origins across
    duplicate receipts, and uses the complete normalized object lookup.
    """
    reach_by_id = {
        r.get("reachability_receipt_id"): r for r in reachability_receipts
    }
    candidates_acc: dict[str, dict[str, Any]] = {}
    for receipt in bridge_receipts:
        status = receipt.get("bridge_status")
        if status not in ELIGIBLE_BRIDGE_STATUSES:
            continue
        candidate_id = receipt.get("source_native_candidate_object_id")
        if not candidate_id:
            continue
        origin_id = receipt.get("evidence_provenance_origin_id")
        reach = reach_by_id.get(receipt.get("reachability_receipt_id")) or {}
        distance = reach.get("budget_consumed")
        locator = receipt.get("locator") if isinstance(receipt.get("locator"), dict) else {}
        locator_path = locator.get("path")

        cand_obj = object_lookup.get(candidate_id) or {}
        entry = candidates_acc.get(candidate_id)
        if entry is None:
            candidates_acc[candidate_id] = {
                "candidate_object_id": candidate_id,
                "provenance_origin_ids": [origin_id] if origin_id else [],
                "origin_types": (
                    [receipt.get("evidence_provenance_origin_type")]
                    if receipt.get("evidence_provenance_origin_type")
                    else []
                ),
                "source_id": receipt.get("source_id") or cand_obj.get("source_id"),
                "source_version_id": receipt.get("source_version_id") or cand_obj.get("source_version_id"),
                "locator_path": locator_path or (cand_obj.get("locator") or {}).get("path"),
                "min_structural_distance_transitions": distance if distance is not None else 1_000_000,
                "object_type": receipt.get("object_type") or cand_obj.get("object_type"),
                "locator": locator or cand_obj.get("locator") or {},
            }
        else:
            if origin_id and origin_id not in entry["provenance_origin_ids"]:
                entry["provenance_origin_ids"].append(origin_id)
            orig_type = receipt.get("evidence_provenance_origin_type")
            if orig_type and orig_type not in entry["origin_types"]:
                entry["origin_types"].append(orig_type)
            if distance is not None:
                entry["min_structural_distance_transitions"] = min(
                    entry["min_structural_distance_transitions"], distance
                )

    return sorted(candidates_acc.values(), key=lambda item: item["candidate_object_id"])


def build_candidate_payload_registry(
    eligible_candidates: list[dict[str, Any]],
    object_lookup: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    payload_registry: dict[str, dict[str, Any]] = {}
    for cand in eligible_candidates:
        oid = cand["candidate_object_id"]
        cand_obj = object_lookup.get(oid) or {}
        payload_registry[oid] = {
            "object_id": oid,
            "title": cand_obj.get("title", ""),
            "source_id": cand_obj.get("source_id", ""),
            "text_payload_2000": (cand_obj.get("text") or "")[:2000],
            "object_type": cand_obj.get("object_type", ""),
            "locator": cand_obj.get("locator") or {},
        }
    return payload_registry


def execute_cell_retrieval(
    retriever: Retriever,
    case_id: str,
    arm: str,
    question_text: str,
    original_expansions: QueryExpansions,
    masked_expansions: QueryExpansions,
    object_lookup: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generic single-cell retrieval executor for all three arms.

    Ensures ABLATION and REPLACEMENT differ only by the generic structured
    replacement plus K=3 admission.
    """
    if object_lookup is None:
        object_lookup = load_object_lookup(retriever.project_root)

    stats_before = retriever.vertex.stats_snapshot()
    t0 = time.time()

    # Configure query expansions for the arm
    if arm == "LEGACY_CONTROL":
        retriever.query_expansions = original_expansions
    else:
        # Both BATCH1_ABLATION and BATCH1_REPLACEMENT share the identical masked query_expansions
        retriever.query_expansions = masked_expansions

    limit = retriever.policies.candidate_pool_per_channel

    # 1. Deterministic Query Analysis
    plan = retriever.analyze(question_text)

    # 2. Retrieval Channels
    rankings: dict[str, list[dict[str, Any]]] = {
        "exact": retriever._exact(plan, question_text, limit)
    }
    dense, sparse, query_vector, semantic_query = retriever._vector(question_text, plan, limit)
    rankings["dense"] = [hit.payload for hit in dense]
    rankings["sparse"] = [hit.payload for hit in sparse]
    paper = retriever._paper(query_vector, plan, limit)
    if paper:
        rankings["paper"] = paper
    rankings["workflow"] = retriever._workflow(question_text, plan, limit)
    rankings["graph"] = retriever._graph(
        [*rankings["exact"], *rankings["dense"], *rankings["sparse"]], plan, limit
    )

    channel_rankings = {
        channel: [item["object_id"] for item in items]
        for channel, items in rankings.items()
    }

    # 3. RRF Fusion
    scores: dict[str, float] = defaultdict(float)
    payloads: dict[str, dict[str, Any]] = {}
    channels_membership: dict[str, list[str]] = defaultdict(list)
    weights = {"exact": 2.0, "dense": 1.0, "sparse": 1.0, "paper": 1.15, "workflow": 1.2, "graph": 0.8}
    for channel, items in rankings.items():
        w = weights.get(channel, 1.0)
        for rank, item in enumerate(items):
            oid = item["object_id"]
            scores[oid] += w / (60 + rank + 1)
            payloads[oid] = item
            channels_membership[oid].append(channel)

    baseline_fused_ordering = sorted(scores, key=scores.get, reverse=True)
    baseline_pool = baseline_fused_ordering[:30]

    structured_receipts: dict[str, Any] | None = None
    v2_selected_order: list[str] = []
    reserved_bridge_candidate_ids: list[str] = []
    displaced_object_ids: list[str] = []

    # 4. Treatment-Arm Selection & Admission (Only for BATCH1_REPLACEMENT)
    if arm == "BATCH1_REPLACEMENT":
        # Run generic D1/D2 structured bridge
        contribution = build_structured_contribution_from_storage(
            question_text,
            plan,
            storage=retriever.storage,
            context_sources=retriever.context_sources,
            max_relation_hops=min(2, retriever.policies.max_relation_hops),
            bridge_enabled=True,
        )

        for c in contribution.bridged_candidates:
            if c["object_id"] not in payloads:
                payloads[c["object_id"]] = c

        eligible_candidates = build_eligible_bridge_candidates(
            contribution.bridge_receipts,
            contribution.reachability_receipts,
            object_lookup,
        )

        payload_registry = build_candidate_payload_registry(
            eligible_candidates, object_lookup
        )

        for cand in eligible_candidates:
            oid = cand["candidate_object_id"]
            if oid not in payloads and oid in object_lookup:
                payloads[oid] = object_lookup[oid]

        # Apply d3_5_selectivity_v2 with caps 8/4
        v2_case = {
            "case_id": case_id,
            "frozen_plan_fields": plan.model_dump(mode="json"),
            "question": {"query": question_text},
            "arms": {"STRUCTURED_BRIDGED": {"channel_rankings": channel_rankings}},
            "unbridged_graph_ordering": channel_rankings.get("graph", []),
            "eligible_governed_bridge_candidates": eligible_candidates,
        }
        v2_result = a5_r2.select_v2(v2_case, payload_registry)
        # select_v2 returns selected_object_ids
        v2_selected_order = v2_result.get("selected_object_ids", [])

        # Apply K=3 bounded reserved admission
        reservable = a6_p1.reservable_bridge(v2_selected_order, baseline_pool)
        treatment_pool = a6_p1.build_treatment_pool(baseline_pool, reservable, k=3)
        rerank_pool = treatment_pool["treatment_pool_object_ids"]
        reserved_bridge_candidate_ids = treatment_pool["reserved_bridge_candidate_ids"]
        displaced_object_ids = treatment_pool["displaced_object_ids"]

        resolved_d2_seeds = (
            contribution.resolution_receipt.get("resolved_seeds")
            or [contribution.resolution_receipt]
        )
        reached_structures = contribution.reachability_receipts
        reachability_receipts = contribution.reachability_receipts
        actual_bridge_receipts = contribution.bridge_receipts
        eligible_candidates_record = eligible_candidates
        selected_bridge_candidates_record = v2_selected_order
        v2_diagnostics = {
            "candidate_receipts": v2_result.get("candidate_receipts", []),
            "selected_rank_keys": v2_result.get("selected_rank_keys", []),
            "eligible_count": len(eligible_candidates),
            "selected_count": len(v2_selected_order),
            "gate_passing_count": v2_result.get("gate_passing_candidate_count", 0),
            "gate_rejected_count": v2_result.get("gate_rejected_candidate_count", 0),
        }

        structured_receipts = {
            "structured_resolution": contribution.resolution_receipt,
            "reachability_receipts_count": len(contribution.reachability_receipts),
            "bridge_receipts_count": len(contribution.bridge_receipts),
            "eligible_bridge_candidates_count": len(eligible_candidates),
            "v2_selected_bridge_candidates": v2_selected_order,
            "v2_selection_receipts": v2_result.get("candidate_receipts"),
            "reservable_bridge_ids": reservable,
            "reserved_bridge_candidate_ids": reserved_bridge_candidate_ids,
            "displaced_object_ids": displaced_object_ids,
        }
    else:
        rerank_pool = baseline_pool
        resolved_d2_seeds = []
        reached_structures = []
        reachability_receipts = []
        actual_bridge_receipts = []
        eligible_candidates_record = []
        selected_bridge_candidates_record = []
        v2_diagnostics = {}

    # 5. Formal Reranker Execution
    rerank_payload = [
        {
            "object_id": oid,
            "title": payloads[oid].get("title"),
            "source_id": payloads[oid].get("source_id"),
            "text": payloads[oid].get("text", "")[:2000],
        }
        for oid in rerank_pool
    ]
    prompt_payload = json.dumps(
        {
            "task": "rerank_evidence",
            "untrusted_question": question_text,
            "untrusted_candidates": rerank_payload,
        },
        ensure_ascii=False,
    )
    response_schema = {
        "type": "object",
        "properties": {
            "ranked_object_ids": {
                "type": "array",
                "items": {"type": "string", "enum": rerank_pool},
            }
        },
        "required": ["ranked_object_ids"],
        "additionalProperties": False,
    }

    raw_response = retriever.vertex.generate_json(
        prompt_payload,
        response_schema,
        system_instruction=RERANK_SYSTEM_PROMPT,
        temperature=EXPECTED_TEMPERATURE,
    )
    reranked = raw_response.get("ranked_object_ids", [])

    # 6. Post-Rerank Selection (Production select_final_evidence)
    # Post-rerank ordered list mirrors production retrieval
    symbol_first: list[str] = []
    # Build match priority
    preferred_sources = list(plan.target_repositories)
    lowered_question = question_text.casefold()
    if any(term in lowered_question for term in ("restgas", "off-ip", "event_poca", "poca", "displaced")):
        preferred_sources = ["restgas_determination", "pandaroot", "luminosityfit", *preferred_sources]
    elif "pandaroot" in lowered_question:
        preferred_sources = ["pandaroot", "restgas_determination", "luminosityfit", *preferred_sources]
    preferred_sources = list(dict.fromkeys(preferred_sources))
    source_rank = {src: r for r, src in enumerate(preferred_sources)}

    def symbol_order(val: str) -> tuple[int, int]:
        norm = val.replace("\\", "/").lower()
        if plan.intent == "troubleshooting" and ("readme" in norm or "running/" in norm):
            return (0, 0)
        return (1, 0 if "/" in val or "." in val else 1)

    symbols = sorted(plan.symbols, key=symbol_order)
    for sym in symbols:
        literal = sym.replace("*", "").replace("?", "")
        matches = []
        for item in rankings["exact"]:
            loc = item.get("locator") or {}
            if literal and (
                literal in (item.get("title") or "")
                or literal in (loc.get("symbol") or "")
                or literal in (loc.get("path") or "")
                or literal in (item.get("text") or "")
            ):
                matches.append(item)
        if matches:
            def match_priority(item: dict[str, Any]) -> tuple[int, int, int, str]:
                loc = item.get("locator") or {}
                path = (loc.get("path") or "").replace("\\", "/")
                exact_p = int(bool(literal and (path == literal or ("/" in literal and path.endswith("/" + literal)))))
                page_lvl = int(item.get("object_type") in {"sphinx_page", "source_file", "readme_section"})
                return (source_rank.get(item.get("source_id"), 999), -exact_p, -page_lvl, item["object_id"])
            matches.sort(key=match_priority)
            symbol_first.append(matches[0]["object_id"])

    # Post-rerank fallback must include the complete actual treatment pool so a reserved
    # candidate is not silently dropped if the schema returns an incomplete ranking;
    # keeps ordinary fused fallback and production selector semantics.
    ordered = list(dict.fromkeys([*reranked, *rerank_pool, *baseline_fused_ordering]))
    required_first: list[str] = []
    for req in plan.required_source_types:
        for oid in ordered:
            stype = retriever._source_type(payloads[oid])
            if stype == req or (req in {"workflow", "graph"} and req in channels_membership[oid]):
                required_first.append(oid)
                break

    hinted_first: list[str] = []
    for oid in ordered:
        item = payloads[oid]
        sid = item.get("source_id")
        page = (item.get("locator") or {}).get("pdf_page")
        if sid in plan.paper_page_hints and page is not None and int(page) in plan.paper_page_hints[sid]:
            hinted_first.append(oid)

    ordered = list(dict.fromkeys([*hinted_first, *required_first, *symbol_first, *ordered]))
    ranked_object_ids = ordered[:30]

    selected, excluded, backfill = select_final_evidence(
        ordered,
        payloads,
        scores,
        channels_membership,
        plan,
        retriever.policies.final_evidence_limit,
        set(symbol_first),
    )
    final_evidence_ids = [item.object_id for item in selected]

    elapsed = time.time() - t0
    stats_delta = retriever.vertex.stats_delta(stats_before)

    # Calculate matched query expansion rules
    lowered_q = question_text.casefold()
    active_qe = retriever.query_expansions
    matched_rules = [
        r.rule_id
        for r in active_qe.rules
        if any(str(tr).casefold() in lowered_q for tr in r.triggers)
    ]

    effective_preserved: dict[str, Any] = {}
    effective_suppressed: dict[str, Any] = {}
    if "event_poca_handoff" in matched_rules:
        effective_preserved["event_poca_handoff"] = {
            "triggers": PRESERVED_TRIGGERS_EVENT_POCA,
            "repositories": PRESERVED_REPOS_EVENT_POCA,
            "concepts": PRESERVED_CONCEPTS_EVENT_POCA,
        }
        if arm in ("BATCH1_ABLATION", "BATCH1_REPLACEMENT"):
            effective_suppressed["event_poca_handoff"] = {
                "symbols": SUPPRESSED_SYMBOLS_EVENT_POCA,
                "paper_page_hints": SUPPRESSED_PAGE_HINTS_EVENT_POCA,
            }
    if "restgas_profile_workflow" in matched_rules:
        effective_preserved["restgas_profile_workflow"] = {
            "triggers": PRESERVED_TRIGGERS_RESTGAS,
            "repositories": PRESERVED_REPOS_RESTGAS,
            "concepts": PRESERVED_CONCEPTS_RESTGAS,
        }
        if arm in ("BATCH1_ABLATION", "BATCH1_REPLACEMENT"):
            effective_suppressed["restgas_profile_workflow"] = {
                "symbols": SUPPRESSED_SYMBOLS_RESTGAS,
                "paper_page_hints": SUPPRESSED_PAGE_HINTS_RESTGAS,
            }

    inputs = {
        "repository_inputs": list(plan.target_repositories),
        "symbol_inputs": list(plan.symbols),
        "concept_inputs": list(plan.concepts),
        "page_inputs": {k: list(v) for k, v in plan.paper_page_hints.items()},
    }

    final_evidence_locators = {
        oid: payloads.get(oid, {}).get("locator") for oid in final_evidence_ids
    }
    logical_calls = {
        "analyzer_calls": 1,
        "embedding_calls": 1,
        "reranker_calls": 1,
    }
    provider_attempts = stats_delta.get(
        "model_calls", stats_delta.get("generation_calls", 1)
    )
    token_usage = stats_delta.get("token_usage", 0)

    return {
        "case_id": case_id,
        "arm": arm,
        "question": question_text,
        "matched_query_expansion_rules": matched_rules,
        "exact_effective_preserved_components": effective_preserved,
        "exact_effective_suppressed_components": effective_suppressed,
        "inputs": inputs,
        "resolved_d2_seeds": resolved_d2_seeds,
        "reached_structures": reached_structures,
        "reachability_receipts": reachability_receipts,
        "actual_bridge_receipts": actual_bridge_receipts,
        "eligible_bridge_candidates": eligible_candidates_record,
        "selected_bridge_candidates": selected_bridge_candidates_record,
        "v2_diagnostics": v2_diagnostics,
        "ordinary_fused_ordering": baseline_fused_ordering,
        "ordinary_fused_top30": baseline_pool,
        "reserved_candidate_ids": reserved_bridge_candidate_ids,
        "displaced_candidate_ids": displaced_object_ids,
        "final_pool_object_ids": rerank_pool,
        "reranked_object_ids": reranked,
        "final_evidence_object_ids": final_evidence_ids,
        "final_evidence_locators": final_evidence_locators,
        "logical_calls": logical_calls,
        "provider_internal_attempts": provider_attempts,
        "token_usage": token_usage,
        "status": "COMPLETED",
        "formal_call_status": "SUCCESS",
        "elapsed_seconds": round(elapsed, 3),
        "stats_delta": stats_delta,
        "plan_summary": plan.model_dump(mode="json"),
        "channel_rankings": channel_rankings,
        "fusion_scores_top30": {oid: scores[oid] for oid in baseline_pool},
        "baseline_fused_ordering": baseline_pool,
        "ordered_pool_object_ids": rerank_pool,
        "reserved_bridge_candidate_ids": reserved_bridge_candidate_ids,
        "displaced_object_ids": displaced_object_ids,
        "ranked_object_ids": ranked_object_ids,
        "excluded": excluded,
        "backfill_admissions": backfill,
        "structured_receipts": structured_receipts,
    }


# ===========================================================================
# 5. Formal Execution Mode (`execute-21`)
# ===========================================================================

def execute_21_formal_cells(project_root: Path) -> dict[str, Any]:
    """Executes exactly the 21 formal cells in strict case-major order:
    g036, g021, n006, g041, g020, n004, n022 over LEGACY_CONTROL -> BATCH1_ABLATION -> BATCH1_REPLACEMENT.

    Journal semantics:
      NOT_EXECUTED -> STARTED (persisted before call) -> COMPLETED or FAILED
      COMPLETED slots are never rerun.
      Ambiguous STARTED or FAILED stops immediately.
      Parallelism prohibited.

    Generates evaluation/d4_a1_raw_three_arm_results.json with
    EVALUATOR_EXECUTED = false and MIGRATION_VERDICT_COMPUTED = false.
    """
    load_dotenv(project_root / ".env")
    audit_receipt = audit_invariants(project_root)
    print(f"[PRE-EXPOSURE AUDIT PASSED] Model: {audit_receipt['qa_generation_model_id']}")

    # Enforce implementation/config drift guards and require clean worktree
    drift_receipt = verify_drift_guards(project_root, require_clean_worktree=True)
    current_head = drift_receipt["current_head"]
    print(f"[HEAD IDENTITY] Current clean HEAD: {current_head}")

    manifest = _load_json(project_root / MANIFEST_PATH)
    prereg = _load_json(project_root / PREREGISTRATION_PATH)

    # Validate and assert manifest questions/roles/order against preregistration
    manifest_cases = manifest.get("cases", [])
    prereg_cases = prereg.get("future_D4_A1", {}).get("exact_cases", [])
    if [c["case_id"] for c in manifest_cases] != CASE_ORDER:
        raise ValueError(
            f"Manifest case order mismatch: {[c['case_id'] for c in manifest_cases]} vs {CASE_ORDER}"
        )

    prereg_by_id = {c["case_id"]: c for c in prereg_cases}
    manifest_by_id: dict[str, dict[str, Any]] = {}
    for c in manifest_cases:
        cid = c["case_id"]
        manifest_by_id[cid] = c
        pc = prereg_by_id.get(cid)
        if not pc:
            raise ValueError(f"Case {cid} in manifest not found in preregistration")
        if c.get("role") != pc.get("role"):
            raise ValueError(f"Case {cid} role mismatch: {c.get('role')} vs {pc.get('role')}")
        if c.get("query") != pc.get("query"):
            raise ValueError(f"Case {cid} query mismatch vs preregistration")

    # Formal execute mode does NOT load gold/novel datasets or evidence selectors
    object_lookup = load_object_lookup(project_root)

    original_qe = load_query_expansions(project_root / CONFIG_QUERY_EXPANSIONS_PATH)
    masked_qe = apply_batch1_in_memory_mask(original_qe)

    raw_path = project_root / RAW_RESULTS_PATH
    completed_slots: dict[int, dict[str, Any]] = {}

    if raw_path.exists():
        existing_data = _load_json(raw_path)
        recorded_head = existing_data.get("authority", {}).get("implementation_freeze_head")
        if recorded_head and recorded_head != current_head:
            print(
                f"[FATAL RESUME MISMATCH] Recorded freeze HEAD {recorded_head} does not match "
                f"current HEAD {current_head}. Halting immediately."
            )
            sys.exit(3)

        for slot in existing_data.get("slots", []):
            f_idx = slot["slot_index"]
            status = slot.get("outcome_status")
            if status == "STARTED":
                print(f"[FATAL AMBIGUOUS JOURNAL] Slot #{f_idx} is in STARTED state. Halting immediately.")
                sys.exit(3)
            elif status == "FAILED":
                print(f"[FATAL JOURNAL] Slot #{f_idx} is in FAILED state. Halting immediately.")
                sys.exit(3)
            elif status == "COMPLETED":
                completed_slots[f_idx] = slot

        print(f"[RESUME CHECKPOINT] Found {len(completed_slots)} completed slots in existing raw artifact")

    if len(completed_slots) == TOTAL_FORMAL_SLOTS:
        print("[ALREADY COMPLETE] All 21 formal slots have already completed.")
        return _load_json(raw_path)

    retriever = Retriever(project_root)
    execution_start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    total_provider_attempts = 0
    total_tokens_consumed = 0

    slots_list: list[dict[str, Any]] = []

    slot_idx = 0
    for cid in CASE_ORDER:
        q_text = manifest_by_id[cid]["query"]
        for arm in ARMS:
            slot_idx += 1
            if slot_idx in completed_slots:
                s_rec = completed_slots[slot_idx]
                slots_list.append(s_rec)
                total_provider_attempts += s_rec.get("provider_internal_attempts", s_rec.get("provider_attempts", 1))
                total_tokens_consumed += s_rec.get("token_usage", 0)
                continue

            # Formal journal transition: NOT_EXECUTED -> STARTED persisted before call
            print(f"Executing slot {slot_idx}/{TOTAL_FORMAL_SLOTS}: case={cid}, arm={arm}...", flush=True)

            current_slot_record: dict[str, Any] = {
                "slot_index": slot_idx,
                "case_id": cid,
                "arm": arm,
                "outcome_status": "STARTED",
                "started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "completed_at_utc": None,
                "error": None,
            }

            # Write journal update to disk
            raw_artifact = {
                "schema_version": "1.0.0",
                "checkpoint": "D4-A1-RAW-THREE-ARM-OUTCOME-FREEZE",
                "stage": "d4_a1_raw_three_arm_results",
                "authority": {
                    "manifest": MANIFEST_PATH,
                    "preregistration": PREREGISTRATION_PATH,
                    "implementation_freeze_head": current_head,
                },
                "model_contract": {
                    "generation_model_id": EXPECTED_MODEL,
                    "temperature": EXPECTED_TEMPERATURE,
                    "system_prompt": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT",
                },
                "outcome_exposure_state": {
                    "D4_A1_OUTCOME_EXPOSURE": "STARTED" if len(slots_list) < TOTAL_FORMAL_SLOTS else "COMPLETE",
                    "execution_started_at_utc": execution_start_time,
                    "execution_completed_at_utc": None,
                    "formal_slots_total": TOTAL_FORMAL_SLOTS,
                    "formal_slots_completed": sum(1 for s in slots_list if s.get("outcome_status") == "COMPLETED"),
                    "formal_slots_failed": sum(1 for s in slots_list if s.get("outcome_status") == "FAILED"),
                },
                "evaluation_boundary": {
                    "EVALUATOR_EXECUTED": False,
                    "MIGRATION_VERDICT_COMPUTED": False,
                },
                "accounting": {
                    "FORMAL_CELLS_TOTAL": TOTAL_FORMAL_SLOTS,
                    "FORMAL_CELLS_COMPLETED": len(slots_list),
                    "FORMAL_CELLS_FAILED": 0,
                    "PROVIDER_INTERNAL_ATTEMPTS": total_provider_attempts,
                    "TOTAL_TOKEN_USAGE": total_tokens_consumed,
                },
                "slots": slots_list + [current_slot_record],
            }
            raw_path.write_text(json.dumps(raw_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

            # Execute slot call
            try:
                cell_result = execute_cell_retrieval(
                    retriever=retriever,
                    case_id=cid,
                    arm=arm,
                    question_text=q_text,
                    original_expansions=original_qe,
                    masked_expansions=masked_qe,
                    object_lookup=object_lookup,
                )
                attempts = cell_result.get("provider_internal_attempts", 1)
                tokens = cell_result.get("token_usage", 0)
                total_provider_attempts += attempts
                total_tokens_consumed += tokens

                current_slot_record.update(cell_result)
                current_slot_record["outcome_status"] = "COMPLETED"
                current_slot_record["completed_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                current_slot_record["error"] = None
                slots_list.append(current_slot_record)
            except Exception as exc:
                current_slot_record["outcome_status"] = "FAILED"
                current_slot_record["formal_call_status"] = "FAILED"
                current_slot_record["error"] = f"{type(exc).__name__}: {exc}"
                slots_list.append(current_slot_record)

                raw_artifact["slots"] = slots_list
                raw_artifact["outcome_exposure_state"]["formal_slots_failed"] += 1
                raw_path.write_text(json.dumps(raw_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                print(f"[FATAL CALL FAILURE] Slot #{slot_idx} failed: {exc}")
                sys.exit(3)

            # Persist completed slot
            raw_artifact["slots"] = slots_list
            raw_artifact["outcome_exposure_state"]["formal_slots_completed"] = sum(
                1 for s in slots_list if s.get("outcome_status") == "COMPLETED"
            )
            raw_artifact["accounting"]["FORMAL_CELLS_COMPLETED"] = len(slots_list)
            raw_artifact["accounting"]["PROVIDER_INTERNAL_ATTEMPTS"] = total_provider_attempts
            raw_artifact["accounting"]["TOTAL_TOKEN_USAGE"] = total_tokens_consumed
            if len(slots_list) == TOTAL_FORMAL_SLOTS:
                raw_artifact["outcome_exposure_state"]["D4_A1_OUTCOME_EXPOSURE"] = "COMPLETE"
                raw_artifact["outcome_exposure_state"]["execution_completed_at_utc"] = datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat()
            raw_path.write_text(json.dumps(raw_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("[EXECUTE-21 SUCCESS] All 21 formal slots completed successfully and frozen in raw results.")
    return raw_artifact


# ===========================================================================
# 6. Evaluator Mode (`evaluate`) & Pure Verdict Precedence Logic
# ===========================================================================

def compute_migration_verdict(
    target_results: dict[str, dict[str, Any]],
    safety_results: dict[str, Any],
    diagnostic_results: dict[str, Any] | None = None,
    structural_fail: bool = False,
) -> dict[str, Any]:
    """Pure deterministic decision logic for D4-A1 migration verdict.

    Exact 7-level verdict precedence:
      1. INVALID / PROTOCOL_OR_TREATMENT_CONSTRUCTION_FAILED
      2. FAIL / MATERIAL_SAFETY_REGRESSION
      3. PASS / FIRST_BATCH_FIXED_LOCATOR_REPLACEMENT_VALIDATED_FOR_DEVELOPMENT
      4. PARTIAL / MIXED_TARGET_REPLACEMENT_EVIDENCE
      5. PARTIAL / LEGACY_DEPENDENCY_NOT_REPRODUCED_IN_CURRENT_PROTOTYPE
      6. FAIL / FIXED_LOCATOR_REPLACEMENT_DID_NOT_RECOVER_CONFIRMED_DEPENDENCY
      7. INCONCLUSIVE / LEGACY_CONTROL_REFERENCE_NOT_REPRODUCED
    """
    g036 = target_results.get("g036", {})
    e1_leg = bool(g036.get("LEGACY_CONTROL", False))
    e1_abl = bool(g036.get("BATCH1_ABLATION", False))
    e1_rep = bool(g036.get("BATCH1_REPLACEMENT", False))
    e1_wit = bool(g036.get("witness", False))

    g021 = target_results.get("g021", {})
    e2_leg = bool(g021.get("LEGACY_CONTROL", False))
    e2_abl = bool(g021.get("BATCH1_ABLATION", False))
    e2_rep = bool(g021.get("BATCH1_REPLACEMENT", False))
    e2_wit = bool(g021.get("witness", False))

    def _eval_rule(leg: bool, abl: bool, rep: bool, wit: bool) -> str:
        if not leg:
            return DECISION_LEGACY_CONTROL_REFERENCE_NOT_REPRODUCED
        if abl:
            return DECISION_LEGACY_DEPENDENCY_NOT_REPRODUCED
        if rep and wit:
            return DECISION_REPLACEMENT_VALIDATED
        return DECISION_REPLACEMENT_FAILED

    dec_ep = _eval_rule(e1_leg, e1_abl, e1_rep, e1_wit)
    dec_rg = _eval_rule(e2_leg, e2_abl, e2_rep, e2_wit)

    per_rule_decisions = {
        "event_poca_handoff": dec_ep,
        "restgas_profile_workflow": dec_rg,
    }

    # Precedence level 1: Protocol or treatment construction failure
    if structural_fail:
        return {
            "per_rule_decisions": per_rule_decisions,
            "batch_verdict": VERDICT_INVALID_PROTOCOL,
            "verdict_reason": "Structural or protocol/treatment construction violation occurred.",
        }

    # Precedence level 2: Material safety regression (only replacement regression gates)
    reg_replacement = safety_results.get(
        "REGRESSION_REPLACEMENT", safety_results.get("regression_count", 0)
    )
    if reg_replacement > 0:
        return {
            "per_rule_decisions": per_rule_decisions,
            "batch_verdict": VERDICT_FAIL_SAFETY_REGRESSION,
            "verdict_reason": (
                f"Material safety regression detected under replacement arm on "
                f"{reg_replacement} safety group(s)."
            ),
        }

    # Precedence level 3: PASS - Both target rules validated
    if dec_ep == DECISION_REPLACEMENT_VALIDATED and dec_rg == DECISION_REPLACEMENT_VALIDATED:
        return {
            "per_rule_decisions": per_rule_decisions,
            "batch_verdict": VERDICT_PASS,
            "verdict_reason": (
                "Both target rules REPLACEMENT_VALIDATED with confirmed legacy dependency, "
                "truthful admission witness, and zero replacement regression."
            ),
        }

    # Precedence level 4: PARTIAL - Mixed target replacement evidence
    if (dec_ep == DECISION_REPLACEMENT_VALIDATED) or (dec_rg == DECISION_REPLACEMENT_VALIDATED):
        return {
            "per_rule_decisions": per_rule_decisions,
            "batch_verdict": VERDICT_PARTIAL_MIXED_EVIDENCE,
            "verdict_reason": (
                f"Mixed target replacement evidence across target rules: "
                f"event_poca_handoff={dec_ep}, restgas_profile_workflow={dec_rg}."
            ),
        }

    # Precedence level 5: PARTIAL - Legacy dependency not reproduced in current prototype
    if (dec_ep == DECISION_LEGACY_DEPENDENCY_NOT_REPRODUCED) or (
        dec_rg == DECISION_LEGACY_DEPENDENCY_NOT_REPRODUCED
    ):
        return {
            "per_rule_decisions": per_rule_decisions,
            "batch_verdict": VERDICT_PARTIAL_LEGACY_DEP_NOT_REPRODUCED,
            "verdict_reason": (
                f"Fixed locator ablation did not weaken target evidence on at least one rule: "
                f"event_poca_handoff={dec_ep}, restgas_profile_workflow={dec_rg}."
            ),
        }

    # Precedence level 6: FAIL - Replacement did not recover confirmed dependency
    if (dec_ep == DECISION_REPLACEMENT_FAILED) or (dec_rg == DECISION_REPLACEMENT_FAILED):
        return {
            "per_rule_decisions": per_rule_decisions,
            "batch_verdict": VERDICT_FAIL_REPLACEMENT_FAILED,
            "verdict_reason": (
                f"Fixed locator replacement failed to restore confirmed legacy dependency: "
                f"event_poca_handoff={dec_ep}, restgas_profile_workflow={dec_rg}."
            ),
        }

    # Precedence level 7: INCONCLUSIVE - Legacy control reference not reproduced
    return {
        "per_rule_decisions": per_rule_decisions,
        "batch_verdict": VERDICT_INCONCLUSIVE_LEGACY_CONTROL,
        "verdict_reason": (
            f"Target evidence was not retained under LEGACY_CONTROL baseline: "
            f"event_poca_handoff={dec_ep}, restgas_profile_workflow={dec_rg}."
        ),
    }


def check_admission_witness(
    group_id: str,
    slot: dict[str, Any],
    object_lookup: dict[str, dict[str, Any]],
    required_group: Any,
) -> dict[str, Any]:
    """Evaluates truthful admission witness for an evidence group in a slot:
    Records:
      - selected-by-v2
      - ordinary-top30 membership before reservation
      - reserved-under-K3
      - displaced candidate
      - final pool membership/position
      - competed in reranker
      - final evidence retained
      - full structured path
    A valid structured admission witness requires governed path + v2 selection +
    final-pool competition + final retention; it may record ordinary-top30/no-reservation
    truthfully if reservation was not needed.
    """
    final_evidence_ids = slot.get("final_evidence_object_ids", [])
    rec, matched_candidates = _matched_evidence_groups([required_group], final_evidence_ids, object_lookup)
    retained_in_final = rec > 0

    eligible_candidates = slot.get("eligible_bridge_candidates", [])
    selected_by_v2_ids = slot.get("selected_bridge_candidates", [])
    ordinary_top30 = slot.get("ordinary_fused_top30", [])
    reserved_ids = slot.get("reserved_candidate_ids", [])
    displaced_ids = slot.get("displaced_candidate_ids", [])
    final_pool = slot.get("final_pool_object_ids", [])

    candidate_witnesses: list[dict[str, Any]] = []
    matched_oids = [
        m["object_id"]
        for m in matched_candidates
        if isinstance(m, dict) and m.get("object_id")
    ]
    for oid in matched_oids:
        cand_meta = next(
            (c for c in eligible_candidates if c.get("candidate_object_id") == oid),
            None,
        )
        governed_path = cand_meta is not None
        selected_v2 = oid in selected_by_v2_ids
        in_top30 = oid in ordinary_top30
        reserved_k3 = oid in reserved_ids
        in_pool = oid in final_pool
        pool_pos = final_pool.index(oid) if in_pool else -1
        competed = in_pool
        in_final = oid in final_evidence_ids

        structured_path = {}
        if cand_meta:
            structured_path = {
                "candidate_object_id": oid,
                "provenance_origin_ids": cand_meta.get("provenance_origin_ids", []),
                "origin_types": cand_meta.get("origin_types", []),
                "source_id": cand_meta.get("source_id"),
                "source_version_id": cand_meta.get("source_version_id"),
                "locator_path": cand_meta.get("locator_path"),
                "min_structural_distance_transitions": cand_meta.get(
                    "min_structural_distance_transitions"
                ),
                "locator": cand_meta.get("locator", {}),
            }

        valid = bool(governed_path and selected_v2 and competed and in_final)

        candidate_witnesses.append(
            {
                "candidate_object_id": oid,
                "governed_path": governed_path,
                "selected_by_v2": selected_v2,
                "ordinary_top30_before_reservation": in_top30,
                "reserved_under_k3": reserved_k3,
                "displaced_candidates": displaced_ids if reserved_k3 else [],
                "final_pool_membership": in_pool,
                "final_pool_position": pool_pos,
                "competed_in_reranker": competed,
                "final_evidence_retained": in_final,
                "full_structured_path": structured_path,
                "is_valid_witness": valid,
            }
        )

    has_valid_witness = any(w["is_valid_witness"] for w in candidate_witnesses)
    return {
        "group_id": group_id,
        "retained_in_final": retained_in_final,
        "has_valid_witness": has_valid_witness,
        "candidate_witnesses": candidate_witnesses,
    }


def evaluate_d4_a1(project_root: Path, *, require_git_frozen: bool = True) -> dict[str, Any]:
    """Deterministic evaluator mode.
    Refuses until raw artifact is committed/frozen (Commit B).
    Loads governed Gold/dev evidence selectors only after raw freeze verification.
    Computes target retention, A6 safety groups, and batch verdict precedence.
    """
    raw_path = project_root / RAW_RESULTS_PATH
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw results artifact {raw_path} does not exist. Run --mode execute-21 first."
        )

    # Check git cleanliness if required
    if require_git_frozen:
        try:
            diff_proc = subprocess.run(
                ["git", "status", "--porcelain", str(RAW_RESULTS_PATH)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                check=True,
            )
            if diff_proc.stdout.strip():
                raise RuntimeError(
                    f"Refusing to evaluate: raw results artifact {RAW_RESULTS_PATH} is not committed in git. "
                    "Commit B must be frozen first before evaluator execution."
                )
        except Exception as exc:
            if "Refusing to evaluate" in str(exc):
                raise
            print(f"[GIT AUDIT WARNING] Could not verify git status: {exc}")

    raw_data = _load_json(raw_path)
    exposure_state = raw_data.get("outcome_exposure_state", {})
    if exposure_state.get("formal_slots_completed") != TOTAL_FORMAL_SLOTS:
        raise ValueError(
            f"Cannot evaluate: raw results contain {exposure_state.get('formal_slots_completed')} "
            f"completed slots, expected {TOTAL_FORMAL_SLOTS}."
        )

    # Load governed evidence selectors ONLY after raw freeze verification
    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_questions = {q.id: q for q in gold_ds.questions + novel_ds.questions}
    object_lookup = load_object_lookup(project_root)

    slots_map: dict[tuple[str, str], dict[str, Any]] = {}
    for slot in raw_data.get("slots", []):
        slots_map[(slot["case_id"], slot["arm"])] = slot

    group_retention: dict[str, dict[str, bool]] = {}

    for cid in CASE_ORDER:
        q = all_questions[cid]
        for grp in q.required_evidence_groups:
            gid = grp.group_id
            group_retention[gid] = {}
            for arm in ARMS:
                slot = slots_map[(cid, arm)]
                ev_ids = slot.get("final_evidence_object_ids", [])
                rec, _ = _matched_evidence_groups([grp], ev_ids, object_lookup)
                group_retention[gid][arm] = rec > 0

    # 1. Target case evaluation with truthful admission witness
    wit_g036 = check_admission_witness(
        "g036.e1",
        slots_map[("g036", "BATCH1_REPLACEMENT")],
        object_lookup,
        next(g for g in all_questions["g036"].required_evidence_groups if g.group_id == "g036.e1"),
    )
    wit_g021 = check_admission_witness(
        "g021.e1",
        slots_map[("g021", "BATCH1_REPLACEMENT")],
        object_lookup,
        next(g for g in all_questions["g021"].required_evidence_groups if g.group_id == "g021.e1"),
    )

    target_results: dict[str, dict[str, Any]] = {
        "g036": {
            "target_evidence": "g036.e1",
            "LEGACY_CONTROL": group_retention.get("g036.e1", {}).get("LEGACY_CONTROL", False),
            "BATCH1_ABLATION": group_retention.get("g036.e1", {}).get("BATCH1_ABLATION", False),
            "BATCH1_REPLACEMENT": group_retention.get("g036.e1", {}).get("BATCH1_REPLACEMENT", False),
            "witness": wit_g036["has_valid_witness"],
            "witness_record": wit_g036,
        },
        "g021": {
            "target_evidence": "g021.e1",
            "LEGACY_CONTROL": group_retention.get("g021.e1", {}).get("LEGACY_CONTROL", False),
            "BATCH1_ABLATION": group_retention.get("g021.e1", {}).get("BATCH1_ABLATION", False),
            "BATCH1_REPLACEMENT": group_retention.get("g021.e1", {}).get("BATCH1_REPLACEMENT", False),
            "witness": wit_g021["has_valid_witness"],
            "witness_record": wit_g021,
        },
    }

    # 2. Safety control cases: n006, g041, g020, n004 over FROZEN_A6_SAFETY_GROUPS
    safety_cases = ["n006", "g041", "g020", "n004"]
    safety_population: list[str] = []
    ablation_regressions: list[str] = []
    replacement_regressions: list[str] = []

    for gid in FROZEN_A6_SAFETY_GROUPS:
        if group_retention.get(gid, {}).get("LEGACY_CONTROL", False):
            safety_population.append(gid)
            if not group_retention.get(gid, {}).get("BATCH1_ABLATION", False):
                ablation_regressions.append(gid)
            if not group_retention.get(gid, {}).get("BATCH1_REPLACEMENT", False):
                replacement_regressions.append(gid)

    regression_ablation = len(ablation_regressions)
    regression_replacement = len(replacement_regressions)

    safety_results = {
        "safety_cases": safety_cases,
        "frozen_a6_safety_groups": FROZEN_A6_SAFETY_GROUPS,
        "safety_population": safety_population,
        "ablation_regressions": ablation_regressions,
        "replacement_regressions": replacement_regressions,
        "REGRESSION_ABLATION": regression_ablation,
        "REGRESSION_REPLACEMENT": regression_replacement,
        "regression_count": regression_replacement,  # Only replacement regression gates
    }

    # 3. Non-gating diagnostic case: n022 (all three arms)
    diagnostic_groups = ["n022.e1", "n022.e2", "n022.e3"]
    n022_witnesses = {
        gid: check_admission_witness(
            gid,
            slots_map[("n022", "BATCH1_REPLACEMENT")],
            object_lookup,
            next(g for g in all_questions["n022"].required_evidence_groups if g.group_id == gid),
        )
        for gid in diagnostic_groups
        if any(g.group_id == gid for g in all_questions["n022"].required_evidence_groups)
    }
    diagnostic_results = {
        "case_id": "n022",
        "gating": False,
        "arms_evaluated": ARMS,
        "group_retention": {
            gid: group_retention.get(gid, {}) for gid in diagnostic_groups
        },
        "witness_records": n022_witnesses,
    }

    # 4. Compute overall verdict
    verdict_outcome = compute_migration_verdict(
        target_results=target_results,
        safety_results=safety_results,
        diagnostic_results=diagnostic_results,
    )

    eval_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A1-EVALUATOR-RESULTS",
        "stage": "d4_a1_evaluator_results",
        "raw_artifact_authority": RAW_RESULTS_PATH,
        "evaluator_executed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target_results": target_results,
        "safety_results": safety_results,
        "diagnostic_results": diagnostic_results,
        "group_retention_complete": group_retention,
        "per_rule_decisions": verdict_outcome["per_rule_decisions"],
        "batch_verdict": verdict_outcome["batch_verdict"],
        "verdict_reason": verdict_outcome["verdict_reason"],
        "production_activation": False,
    }

    eval_out_path = project_root / EVALUATOR_RESULTS_PATH
    eval_out_path.write_text(json.dumps(eval_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("\n==========================================")
    print("D4-A1 Evaluation Complete")
    print(f"event_poca_handoff: {verdict_outcome['per_rule_decisions']['event_poca_handoff']}")
    print(f"restgas_profile_workflow: {verdict_outcome['per_rule_decisions']['restgas_profile_workflow']}")
    print(f"Safety population: {safety_population}")
    print(f"REGRESSION_ABLATION: {regression_ablation} ({ablation_regressions})")
    print(f"REGRESSION_REPLACEMENT: {regression_replacement} ({replacement_regressions})")
    print(f"BATCH VERDICT: {verdict_outcome['batch_verdict']}")
    print(f"Reason: {verdict_outcome['verdict_reason']}")
    print("==========================================\n")

    return eval_artifact


# ===========================================================================
# 7. Main CLI
# ===========================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--mode",
        required=True,
        choices=["audit-invariants", "execute-21", "evaluate"],
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    root = args.project_root.resolve()

    if args.mode == "audit-invariants":
        receipt = audit_invariants(root)
        print(json.dumps(receipt, ensure_ascii=False, indent=1))
    elif args.mode == "execute-21":
        execute_21_formal_cells(root)
    elif args.mode == "evaluate":
        evaluate_d4_a1(root)


if __name__ == "__main__":
    main()
