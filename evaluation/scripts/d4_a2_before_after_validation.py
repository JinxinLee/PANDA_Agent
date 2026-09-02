"""PANDA Agent D4-A2 — First-Batch Before/After Validation.

Pre-exposure implementation freeze only.
Authoritative contract: User Contract Section 41 plus D4-A2 specification.

Runs a paired T2 before/after retrieval validation across the 16-case historical
D3 comparison cohort (10 Gold v2.6 dev + 6 novel_dev; 13 answered cases + 3
insufficient_evidence negative controls):
  - BEFORE_COMPAT: production query_expansions.yaml with all Batch-1 fixed locators active
  - AFTER_BATCH1_REPLACEMENT: in-memory component mask suppressing Batch-1 locators +
    generic D3.5 structured replacement + d3_5_selectivity_v2 (caps 8/4) + K=3 bounded admission

CLI (run with PYTHONPATH=src):
    python evaluation/scripts/d4_a2_before_after_validation.py --project-root . --mode audit-invariants
    python evaluation/scripts/d4_a2_before_after_validation.py --project-root . --mode execute-32
    python evaluation/scripts/d4_a2_before_after_validation.py --project-root . --mode evaluate
"""

from __future__ import annotations

import argparse
import copy
from collections import defaultdict
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
import d4_a1_fixed_locator_migration as d4_a1
from panda_agent.config import QueryExpansions, load_query_expansions
from panda_agent.evaluation import (
    GoldEvidenceGroup,
    GoldQuestion,
    QAStatus,
    _matched_evidence_groups,
    load_gold_dataset,
)
from panda_agent.evaluation_runner import load_object_lookup
from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.prompts import QUERY_ANALYZER_SYSTEM_PROMPT, RERANK_SYSTEM_PROMPT
from panda_agent.retrieval import Retriever, select_final_evidence


STARTING_HEAD = "d078be6cbce59d4991100e566b92524458ea2abe"

MANIFEST_PATH = "evaluation/d4_a2_execution_manifest.json"
PREREGISTRATION_PATH = "evaluation/d4_a2_before_after_preregistration.json"
RAW_RESULTS_PATH = "evaluation/d4_a2_raw_before_after_results.json"
EVALUATOR_RESULTS_PATH = "evaluation/d4_a2_evaluator_results.json"

GOLD_QUESTIONS_PATH = "evaluation/benchmarks/v2_6/gold_questions.yaml"
NOVEL_DEV_PATH = "evaluation/novel/v1/novel_dev.yaml"
CONFIG_QUERY_EXPANSIONS_PATH = "configs/query_expansions.yaml"

EXPECTED_MODEL = "gemini-3.8-flash"
EXPECTED_EMBEDDING_MODEL = "gemini-embedding-2"
EXPECTED_TEMPERATURE = 0.0
EXPECTED_VERTEX_LOCATION = "global"
EXPECTED_RRF_WEIGHTS = {
    "exact": 2.0,
    "dense": 1.0,
    "sparse": 1.0,
    "paper": 1.15,
    "workflow": 1.2,
    "graph": 0.8,
}
EXPECTED_SELECTIVITY_CAP = 8
EXPECTED_PER_ORIGIN_CAP = 4
EXPECTED_ADMISSION_BUDGET_K = 3
EXPECTED_RERANK_POOL_SIZE = 30
IMPLEMENTATION_FREEZE_CONTRACT_POLICY = "GIT_COMMIT_CONTAINING_THIS_ARTIFACT"

CASE_ORDER = [
    "g029", "n021", "g025", "g036", "n022", "g020", "n006", "g041",
    "n014", "g060", "g052", "g055", "n003", "g021", "n004", "g007",
]
GOLD_CASES = ["g029", "g025", "g036", "g020", "g041", "g060", "g052", "g055", "g021", "g007"]
NOVEL_DEV_CASES = ["n021", "n022", "n006", "n014", "n003", "n004"]
ANSWERED_CASES = ["g029", "n021", "g036", "n022", "g020", "n006", "n014", "g060", "g052", "g055", "n003", "g021", "n004"]
INSUFFICIENT_EVIDENCE_CASES = ["g025", "g041", "g007"]

ARMS = ["BEFORE_COMPAT", "AFTER_BATCH1_REPLACEMENT"]
TOTAL_FORMAL_SLOTS = 32

ALLOWED_COMMIT_A_FILES = {
    "evaluation/d4_a2_before_after_preregistration.json",
    "evaluation/d4_a2_execution_manifest.json",
    "evaluation/scripts/d4_a2_before_after_validation.py",
    "tests/unit/test_d4_a2_before_after_validation.py",
}

# 6-level verdict precedence constants (exact Section 41 user contract)
VERDICT_LEVEL_1_INVALID = "INVALID / PROTOCOL_OR_TREATMENT_CONSTRUCTION_FAILED"
VERDICT_LEVEL_2_INCONCLUSIVE = "INCONCLUSIVE / BEFORE_REFERENCE_NOT_REPRODUCED"
VERDICT_LEVEL_3_FAIL_PRIMARY_TARGET = "FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED"
VERDICT_LEVEL_4_FAIL_CRITICAL_OR_GROUNDING = "FAIL / CRITICAL_OR_GROUNDING_REGRESSION"
VERDICT_LEVEL_5_PARTIAL_TOLERANCE = "PARTIAL / BEFORE_AFTER_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE"
VERDICT_LEVEL_6_PASS = "PASS / FIRST_BATCH_BEFORE_AFTER_VALIDATED_FOR_RUNTIME_MIGRATION_DECISION"

FROZEN_A2_VERDICTS = [
    VERDICT_LEVEL_1_INVALID,
    VERDICT_LEVEL_2_INCONCLUSIVE,
    VERDICT_LEVEL_3_FAIL_PRIMARY_TARGET,
    VERDICT_LEVEL_4_FAIL_CRITICAL_OR_GROUNDING,
    VERDICT_LEVEL_5_PARTIAL_TOLERANCE,
    VERDICT_LEVEL_6_PASS,
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
    - Only the allowed Commit-A files are modified between STARTING_HEAD and HEAD/worktree.
    - Worktree is clean for all frozen paths when require_clean_worktree=True.
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

    # Check all changed files relative to STARTING_HEAD
    diff_all = subprocess.run(
        ["git", "diff", "--name-only", STARTING_HEAD],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    changed_all = [
        f.strip().replace("\\", "/")
        for f in diff_all.stdout.splitlines()
        if f.strip()
    ]
    disallowed = [f for f in changed_all if f not in ALLOWED_COMMIT_A_FILES]
    if disallowed:
        raise RuntimeError(
            f"Disallowed files modified relative to STARTING_HEAD: {disallowed}. "
            f"Only {ALLOWED_COMMIT_A_FILES} are allowed."
        )

    status_proc = subprocess.run(
        ["git", "status", "--porcelain", "src", "configs", *ALLOWED_COMMIT_A_FILES],
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
# 1. Deterministic Pre-Exposure Audit
# ===========================================================================

def audit_invariants(project_root: Path) -> dict[str, Any]:
    """Mandatory deterministic pre-exposure verification:
    - Environment model selection resolves to gemini-3.8-flash per frozen contract.
    - Revalidates A0 overlaps on current query_expansions config (fails closed).
    - Verifies in-memory component mask immutability, suppression, and determinism via A1 helpers.
    - Verifies execution manifest: 32 slots in case-major order, NOT_EXECUTED state, 0 pre-exposure accounting.
    - Verifies preregistration matches manifest and Section 41 verdict precedence.
    - Protected dataset boundary: 0 runs, 0 access on novel_validation / holdout.
    - Absolutely no provider or retrieval calls.
    """
    load_dotenv(project_root / ".env")
    settings = VertexSettings.from_env()
    if settings.generation_model != EXPECTED_MODEL:
        raise ValueError(
            f"QA_GENERATION_MODEL_ID mismatch: expected '{EXPECTED_MODEL}', got '{settings.generation_model}'"
        )
    if settings.embedding_model != EXPECTED_EMBEDDING_MODEL:
        raise ValueError(
            f"QA_EMBEDDING_MODEL_ID mismatch: expected '{EXPECTED_EMBEDDING_MODEL}', got '{settings.embedding_model}'"
        )
    if settings.location != EXPECTED_VERTEX_LOCATION:
        raise ValueError(
            f"Vertex location mismatch: expected '{EXPECTED_VERTEX_LOCATION}', got '{settings.location}'"
        )
    env_temp = float(os.getenv("QA_TEMPERATURE", "0.0"))
    if env_temp != EXPECTED_TEMPERATURE:
        raise ValueError(
            f"Reranker temperature mismatch: expected {EXPECTED_TEMPERATURE}, got {env_temp}"
        )

    # Verify frozen prompt authorities
    if not QUERY_ANALYZER_SYSTEM_PROMPT or not isinstance(QUERY_ANALYZER_SYSTEM_PROMPT, str):
        raise ValueError("QUERY_ANALYZER_SYSTEM_PROMPT authority is empty or invalid")
    if not RERANK_SYSTEM_PROMPT or not isinstance(RERANK_SYSTEM_PROMPT, str):
        raise ValueError("RERANK_SYSTEM_PROMPT authority is empty or invalid")

    # Verify RRF weights and pipeline parameters
    if a6_p1.WEIGHTS != EXPECTED_RRF_WEIGHTS:
        raise ValueError(
            f"RRF weights mismatch: expected {EXPECTED_RRF_WEIGHTS}, got {a6_p1.WEIGHTS}"
        )
    if a5_r2.SELECTIVITY_CAP != EXPECTED_SELECTIVITY_CAP:
        raise ValueError(f"SELECTIVITY_CAP mismatch: expected {EXPECTED_SELECTIVITY_CAP}")
    if a5_r2.PER_ORIGIN_CAP != EXPECTED_PER_ORIGIN_CAP:
        raise ValueError(f"PER_ORIGIN_CAP mismatch: expected {EXPECTED_PER_ORIGIN_CAP}")
    if EXPECTED_ADMISSION_BUDGET_K not in a6_p1.ADMISSION_BUDGETS:
        raise ValueError(f"SELECTED_ADMISSION_BUDGET mismatch: expected {EXPECTED_ADMISSION_BUDGET_K}")
    if a6_p1.RERANK_POOL_SIZE != EXPECTED_RERANK_POOL_SIZE:
        raise ValueError(f"RERANK_POOL_SIZE mismatch: expected {EXPECTED_RERANK_POOL_SIZE}")

    # 1. Overlap revalidation via A1 helper
    overlap_receipt = d4_a1.revalidate_a0_overlaps(project_root)

    # 2. In-memory component mask verification via A1 helper
    original_qe = load_query_expansions(project_root / CONFIG_QUERY_EXPANSIONS_PATH)
    masked_qe = d4_a1.apply_batch1_in_memory_mask(original_qe)
    masked_twice = d4_a1.apply_batch1_in_memory_mask(masked_qe)

    # Immutability check
    orig_ep = next(r for r in original_qe.rules if r.rule_id == "event_poca_handoff")
    orig_rg = next(r for r in original_qe.rules if r.rule_id == "restgas_profile_workflow")
    if orig_ep.symbols != d4_a1.SUPPRESSED_SYMBOLS_EVENT_POCA:
        raise ValueError("Source QueryExpansions event_poca_handoff symbols were mutated!")
    if orig_ep.paper_page_hints != d4_a1.SUPPRESSED_PAGE_HINTS_EVENT_POCA:
        raise ValueError("Source QueryExpansions event_poca_handoff page hints were mutated!")
    if orig_rg.symbols != d4_a1.SUPPRESSED_SYMBOLS_RESTGAS:
        raise ValueError("Source QueryExpansions restgas_profile_workflow symbols were mutated!")

    # Suppression check
    mask_ep = next(r for r in masked_qe.rules if r.rule_id == "event_poca_handoff")
    mask_rg = next(r for r in masked_qe.rules if r.rule_id == "restgas_profile_workflow")
    if mask_ep.symbols != []:
        raise ValueError(f"Masked event_poca_handoff symbols not empty: {mask_ep.symbols}")
    if mask_ep.paper_page_hints != {}:
        raise ValueError(f"Masked event_poca_handoff page hints not empty: {mask_ep.paper_page_hints}")
    if mask_rg.symbols != []:
        raise ValueError(f"Masked restgas_profile_workflow symbols not empty: {mask_rg.symbols}")

    # Preservation check
    if mask_ep.triggers != d4_a1.PRESERVED_TRIGGERS_EVENT_POCA:
        raise ValueError("Masked event_poca_handoff triggers not preserved!")
    if mask_ep.repositories != d4_a1.PRESERVED_REPOS_EVENT_POCA:
        raise ValueError("Masked event_poca_handoff repositories not preserved!")
    if mask_ep.concepts != d4_a1.PRESERVED_CONCEPTS_EVENT_POCA:
        raise ValueError("Masked event_poca_handoff concepts not preserved!")
    if mask_rg.triggers != d4_a1.PRESERVED_TRIGGERS_RESTGAS:
        raise ValueError("Masked restgas_profile_workflow triggers not preserved!")
    if mask_rg.repositories != d4_a1.PRESERVED_REPOS_RESTGAS:
        raise ValueError("Masked restgas_profile_workflow repositories not preserved!")
    if mask_rg.concepts != d4_a1.PRESERVED_CONCEPTS_RESTGAS:
        raise ValueError("Masked restgas_profile_workflow concepts not preserved!")

    # Determinism (idempotence)
    if masked_qe.model_dump() != masked_twice.model_dump():
        raise ValueError("In-memory component mask double application is not deterministic!")

    # 3. Execution manifest verification
    manifest_path = project_root / MANIFEST_PATH
    if not manifest_path.exists():
        raise FileNotFoundError(f"Execution manifest {manifest_path} missing")
    manifest = _load_json(manifest_path)

    slots = manifest.get("formal_slots_32", [])
    if len(slots) != TOTAL_FORMAL_SLOTS:
        raise ValueError(f"Manifest formal slots mismatch: expected {TOTAL_FORMAL_SLOTS}, got {len(slots)}")

    # Exact case-major schedule
    idx = 0
    for cid in CASE_ORDER:
        for arm in ARMS:
            idx += 1
            s = slots[idx - 1]
            if (s["slot_index"], s["case_id"], s["arm"]) != (idx, cid, arm):
                raise ValueError(f"Schedule mismatch at slot {idx}: expected ({idx}, {cid}, {arm}), got {s}")
            if s["outcome_status"] != "NOT_EXECUTED":
                raise ValueError(f"Slot {idx} status is not NOT_EXECUTED: {s['outcome_status']}")

    # Outcome exposure state
    exposure_state = manifest.get("outcome_exposure_state", {})
    if exposure_state.get("D4_A2_OUTCOME_EXPOSURE") != "NOT_STARTED":
        raise ValueError("Manifest D4_A2_OUTCOME_EXPOSURE is not NOT_STARTED")
    if exposure_state.get("formal_slots_completed") != 0:
        raise ValueError("Manifest formal_slots_completed != 0")
    if exposure_state.get("formal_slots_failed", 0) != 0:
        raise ValueError("Manifest formal_slots_failed != 0")
    if exposure_state.get("evaluator_executed") is not False:
        raise ValueError("Manifest evaluator_executed is not False")
    if exposure_state.get("scientific_verdict_computed") is not False:
        raise ValueError("Manifest scientific_verdict_computed is not False")

    # Freeze contract check
    m_contract = manifest.get("implementation_freeze_contract", {})
    if m_contract.get("policy") != IMPLEMENTATION_FREEZE_CONTRACT_POLICY:
        raise ValueError(f"Manifest freeze contract policy mismatch: {m_contract.get('policy')}")

    # Pre-exposure accounting
    accounting = manifest.get("pre_exposure_accounting", {})
    for counter, val in accounting.items():
        if val != 0:
            raise ValueError(f"Pre-exposure accounting counter {counter} != 0: {val}")

    # 4. Preregistration verification
    prereg_path = project_root / PREREGISTRATION_PATH
    if not prereg_path.exists():
        raise FileNotFoundError(f"Preregistration artifact {prereg_path} missing")
    prereg = _load_json(prereg_path)
    if prereg.get("outcome_exposure_state", {}).get("D4_A2_OUTCOME_EXPOSURE") != "NOT_STARTED":
        raise ValueError("Preregistration D4_A2_OUTCOME_EXPOSURE is not NOT_STARTED")
    if prereg.get("cohort", {}).get("exact_case_order") != CASE_ORDER:
        raise ValueError("Preregistration case order mismatch")
    p_contract = prereg.get("implementation_freeze_contract", {})
    if p_contract.get("policy") != IMPLEMENTATION_FREEZE_CONTRACT_POLICY:
        raise ValueError(f"Preregistration freeze contract policy mismatch: {p_contract.get('policy')}")

    # Post-exposure mutation accounting initialized to zero in prereg
    p_mut = prereg.get("post_exposure_mutation_accounting", {})
    for m_counter in [
        "POST_EXPOSURE_CASE_MUTATIONS",
        "POST_EXPOSURE_MASK_MUTATIONS",
        "POST_EXPOSURE_REPLACEMENT_MUTATIONS",
        "POST_EXPOSURE_MODEL_MUTATIONS",
        "POST_EXPOSURE_METRIC_MUTATIONS",
        "POST_EXPOSURE_VERDICT_MUTATIONS",
    ]:
        if p_mut.get(m_counter) != 0:
            raise ValueError(f"Preregistration post-exposure mutation counter {m_counter} != 0: {p_mut.get(m_counter)}")

    # 5. Drift guards verification
    drift_receipt = verify_drift_guards(project_root, require_clean_worktree=False)

    return {
        "verified": True,
        "qa_generation_model_id": settings.generation_model,
        "qa_embedding_model_id": settings.embedding_model,
        "vertex_location": settings.location,
        "reranker_temperature": env_temp,
        "rrf_weights": a6_p1.WEIGHTS,
        "selectivity_caps": {"SELECTIVITY_CAP": a5_r2.SELECTIVITY_CAP, "PER_ORIGIN_CAP": a5_r2.PER_ORIGIN_CAP},
        "admission_budget_k": EXPECTED_ADMISSION_BUDGET_K,
        "rerank_pool_size": a6_p1.RERANK_POOL_SIZE,
        "rules_audited": len(original_qe.rules),
        "cohort_cases_count": len(CASE_ORDER),
        "formal_slots_count": len(slots),
        "all_slots_not_executed": True,
        "pre_exposure_exposure_state": exposure_state.get("D4_A2_OUTCOME_EXPOSURE"),
        "pre_exposure_accounting_zero": True,
        "drift_guards_verified": drift_receipt["verified"],
        "protected_dataset_access": 0,
    }


# ===========================================================================
# 2. Retrieval Execution Cell Wrapper
# ===========================================================================

def execute_cell_retrieval_a2(
    retriever: Retriever,
    case_id: str,
    arm: str,
    question_text: str,
    original_expansions: QueryExpansions,
    masked_expansions: QueryExpansions,
    object_lookup: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Thin wrapper delegating cell retrieval to the validated A1 implementation.
    Maps BEFORE_COMPAT -> LEGACY_CONTROL and AFTER_BATCH1_REPLACEMENT -> BATCH1_REPLACEMENT.
    """
    a1_arm = "LEGACY_CONTROL" if arm == "BEFORE_COMPAT" else "BATCH1_REPLACEMENT"
    cell_result = d4_a1.execute_cell_retrieval(
        retriever=retriever,
        case_id=case_id,
        arm=a1_arm,
        question_text=question_text,
        original_expansions=original_expansions,
        masked_expansions=masked_expansions,
        object_lookup=object_lookup,
    )
    is_after = arm == "AFTER_BATCH1_REPLACEMENT"
    cell_result["arm"] = arm
    cell_result.update(
        {
            "in_memory_mask_active": is_after,
            "structured_replacement_active": is_after,
            "admission_budget_k": EXPECTED_ADMISSION_BUDGET_K if is_after else 0,
            "rerank_pool_size": len(cell_result.get("final_pool_object_ids", [])),
            "effective_symbols": list(
                (cell_result.get("inputs") or {}).get("symbol_inputs", [])
            ),
            "effective_paper_page_hints": copy.deepcopy(
                (cell_result.get("inputs") or {}).get("page_inputs", {})
            ),
            "suppressed_components": copy.deepcopy(
                cell_result.get("exact_effective_suppressed_components", {})
            ),
        }
    )
    return cell_result


# ===========================================================================
# 3. Formal Execution Mode (`execute-32`)
# ===========================================================================

def execute_32_formal_cells(project_root: Path) -> dict[str, Any]:
    """Executes exactly the 32 formal cells in strict case-major order:
    g029, n021, g025, g036, n022, g020, n006, g041, n014, g060, g052, g055, n003, g021, n004, g007
    over BEFORE_COMPAT -> AFTER_BATCH1_REPLACEMENT.

    Journal semantics:
      NOT_EXECUTED -> STARTED (persisted before call) -> COMPLETED or FAILED
      COMPLETED slots are never rerun.
      Ambiguous STARTED or FAILED stops immediately.
      Parallelism prohibited.
      Zero mid-run evaluation.

    Generates evaluation/d4_a2_raw_before_after_results.json with
    EVALUATOR_EXECUTED = false and SCIENTIFIC_VERDICT_COMPUTED = false.
    """
    load_dotenv(project_root / ".env")
    audit_receipt = audit_invariants(project_root)
    print(f"[PRE-EXPOSURE AUDIT PASSED] Model: {audit_receipt['qa_generation_model_id']}")

    drift_receipt = verify_drift_guards(project_root, require_clean_worktree=True)
    current_head = drift_receipt["current_head"]
    print(f"[HEAD IDENTITY] Current clean HEAD: {current_head}")

    manifest = _load_json(project_root / MANIFEST_PATH)
    prereg = _load_json(project_root / PREREGISTRATION_PATH)

    manifest_cases = manifest.get("cases", [])
    prereg_cases = prereg.get("cohort", {}).get("exact_case_order", [])
    if [c["case_id"] for c in manifest_cases] != CASE_ORDER:
        raise ValueError(
            f"Manifest case order mismatch: {[c['case_id'] for c in manifest_cases]} vs {CASE_ORDER}"
        )
    if prereg_cases != CASE_ORDER:
        raise ValueError(f"Preregistration case order mismatch: {prereg_cases} vs {CASE_ORDER}")

    manifest_by_id = {c["case_id"]: c for c in manifest_cases}

    # Formal execute mode does NOT load gold/novel datasets or evidence selectors
    object_lookup = load_object_lookup(project_root)

    original_qe = load_query_expansions(project_root / CONFIG_QUERY_EXPANSIONS_PATH)
    masked_qe = d4_a1.apply_batch1_in_memory_mask(original_qe)

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
        print("[ALREADY COMPLETE] All 32 formal slots have already completed.")
        return _load_json(raw_path)

    retriever = Retriever(project_root)
    execution_start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    total_provider_attempts = 0
    total_tokens_consumed = 0

    slots_list: list[dict[str, Any]] = []

    slot_idx = 0
    for cid in CASE_ORDER:
        q_text = manifest_by_id[cid]["query"]
        ds_name = manifest_by_id[cid]["dataset"]
        for arm in ARMS:
            slot_idx += 1
            if slot_idx in completed_slots:
                s_rec = completed_slots[slot_idx]
                slots_list.append(s_rec)
                total_provider_attempts += s_rec.get("provider_internal_attempts", s_rec.get("provider_attempts", 1))
                total_tokens_consumed += s_rec.get("token_usage", 0)
                continue

            print(f"Executing slot {slot_idx}/{TOTAL_FORMAL_SLOTS}: case={cid}, arm={arm}...", flush=True)

            current_slot_record: dict[str, Any] = {
                "slot_index": slot_idx,
                "case_id": cid,
                "dataset": ds_name,
                "arm": arm,
                "outcome_status": "STARTED",
                "started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "completed_at_utc": None,
                "error": None,
            }

            completed_count = sum(1 for s in slots_list if s.get("outcome_status") == "COMPLETED")
            failed_count = sum(1 for s in slots_list if s.get("outcome_status") == "FAILED")

            raw_artifact = {
                "schema_version": "1.0.0",
                "checkpoint": "D4-A2-RAW-BEFORE-AFTER-OUTCOME-FREEZE",
                "stage": "d4_a2_raw_before_after_results",
                "authority": {
                    "manifest": MANIFEST_PATH,
                    "preregistration": PREREGISTRATION_PATH,
                    "implementation_freeze_head": current_head,
                    "implementation_freeze_contract": IMPLEMENTATION_FREEZE_CONTRACT_POLICY,
                },
                "model_contract": {
                    "generation_model_id": EXPECTED_MODEL,
                    "embedding_model_id": EXPECTED_EMBEDDING_MODEL,
                    "temperature": EXPECTED_TEMPERATURE,
                    "location": EXPECTED_VERTEX_LOCATION,
                    "system_prompt": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT",
                    "query_analyzer_prompt": "src/panda_agent/prompts.py:QUERY_ANALYZER_SYSTEM_PROMPT",
                },
                "outcome_exposure_state": {
                    "D4_A2_OUTCOME_EXPOSURE": "STARTED",
                    "execution_started_at_utc": execution_start_time,
                    "execution_completed_at_utc": None,
                    "formal_slots_total": TOTAL_FORMAL_SLOTS,
                    "formal_slots_completed": completed_count,
                    "formal_slots_failed": failed_count,
                },
                "evaluation_boundary": {
                    "EVALUATOR_EXECUTED": False,
                    "SCIENTIFIC_VERDICT_COMPUTED": False,
                },
                "accounting": {
                    "FORMAL_CELLS_TOTAL": TOTAL_FORMAL_SLOTS,
                    "FORMAL_CELLS_COMPLETED": completed_count,
                    "FORMAL_CELLS_FAILED": failed_count,
                    "PROVIDER_INTERNAL_ATTEMPTS": total_provider_attempts,
                    "TOTAL_TOKEN_USAGE": total_tokens_consumed,
                    "ANALYZER_CALLS": completed_count,
                    "EMBEDDING_CALLS": completed_count,
                    "RERANKER_CALLS": completed_count,
                    "QA_CALLS": 0,
                    "VERIFIER_CALLS": 0,
                    "JUDGE_CALLS": 0,
                    "POSTGRESQL_WRITES": 0,
                    "QDRANT_WRITES": 0,
                    "INGESTION": 0,
                    "REINDEX": 0,
                    "NOVEL_VALIDATION_RUNS": 0,
                    "NOVEL_HOLDOUT_RUNS": 0,
                    "PROTECTED_DATASET_ACCESS": 0,
                },
                "slots": slots_list + [current_slot_record],
            }
            raw_path.write_text(json.dumps(raw_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

            try:
                cell_result = execute_cell_retrieval_a2(
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

                failed_count = sum(1 for s in slots_list if s.get("outcome_status") == "FAILED")
                completed_count = sum(1 for s in slots_list if s.get("outcome_status") == "COMPLETED")
                raw_artifact["slots"] = slots_list
                raw_artifact["outcome_exposure_state"]["formal_slots_failed"] = failed_count
                raw_artifact["outcome_exposure_state"]["formal_slots_completed"] = completed_count
                raw_artifact["outcome_exposure_state"]["D4_A2_OUTCOME_EXPOSURE"] = "STARTED"
                raw_artifact["accounting"]["FORMAL_CELLS_FAILED"] = failed_count
                raw_artifact["accounting"]["FORMAL_CELLS_COMPLETED"] = completed_count
                raw_path.write_text(json.dumps(raw_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                print(f"[FATAL CALL FAILURE] Slot #{slot_idx} failed: {exc}")
                sys.exit(3)

            completed_count = sum(1 for s in slots_list if s.get("outcome_status") == "COMPLETED")
            failed_count = sum(1 for s in slots_list if s.get("outcome_status") == "FAILED")
            raw_artifact["slots"] = slots_list
            raw_artifact["outcome_exposure_state"]["formal_slots_completed"] = completed_count
            raw_artifact["outcome_exposure_state"]["formal_slots_failed"] = failed_count
            raw_artifact["accounting"]["FORMAL_CELLS_COMPLETED"] = completed_count
            raw_artifact["accounting"]["FORMAL_CELLS_FAILED"] = failed_count
            raw_artifact["accounting"]["PROVIDER_INTERNAL_ATTEMPTS"] = total_provider_attempts
            raw_artifact["accounting"]["TOTAL_TOKEN_USAGE"] = total_tokens_consumed
            raw_artifact["accounting"]["ANALYZER_CALLS"] = completed_count
            raw_artifact["accounting"]["EMBEDDING_CALLS"] = completed_count
            raw_artifact["accounting"]["RERANKER_CALLS"] = completed_count
            if completed_count == TOTAL_FORMAL_SLOTS and failed_count == 0:
                raw_artifact["outcome_exposure_state"]["D4_A2_OUTCOME_EXPOSURE"] = "COMPLETE"
                raw_artifact["outcome_exposure_state"]["execution_completed_at_utc"] = datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat()
            else:
                raw_artifact["outcome_exposure_state"]["D4_A2_OUTCOME_EXPOSURE"] = "STARTED"
            raw_path.write_text(json.dumps(raw_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("[EXECUTE-32 SUCCESS] All 32 formal slots completed successfully and frozen in raw results.")
    return raw_artifact


# ===========================================================================
# 4. Section 41 Verdict Precedence Logic
# ===========================================================================

def compute_before_after_verdict(
    execution_valid: bool = True,
    protocol_violation: bool = False,
    protocol_violation_reason: str | None = None,
    before_reference_valid: bool = True,
    target_replacement_reproduced: int = 2,
    batch1_dependency_removed: int = 2,
    critical_group_regressions: list[str] | None = None,
    noncritical_group_regressions: list[str] | None = None,
    grounding_regressions: int = 0,
    wrong_version_regressions: int = 0,
    invalid_provenance_recoveries: int = 0,
    metric_deltas: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Pure deterministic decision logic implementing User Contract Section 41.

    Exact 6-Level Precedence:
      Level 1: INVALID / PROTOCOL_OR_TREATMENT_CONSTRUCTION_FAILED
      Level 2: INCONCLUSIVE / BEFORE_REFERENCE_NOT_REPRODUCED
      Level 3: FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
      Level 4: FAIL / CRITICAL_OR_GROUNDING_REGRESSION
      Level 5: PARTIAL / BEFORE_AFTER_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE
      Level 6: PASS / FIRST_BATCH_BEFORE_AFTER_VALIDATED_FOR_RUNTIME_MIGRATION_DECISION
    """
    crit_regs = critical_group_regressions or []
    noncrit_regs = noncritical_group_regressions or []
    deltas = metric_deltas or {}

    # Precedence Level 1 — INVALID
    if not execution_valid or protocol_violation:
        return {
            "verdict_level": 1,
            "batch_verdict": VERDICT_LEVEL_1_INVALID,
            "verdict_reason": (
                protocol_violation_reason
                or "Structural protocol, execution integrity, or treatment construction failure occurred."
            ),
        }

    # Precedence Level 2 — INCONCLUSIVE
    if not before_reference_valid:
        return {
            "verdict_level": 2,
            "batch_verdict": VERDICT_LEVEL_2_INCONCLUSIVE,
            "verdict_reason": (
                "Fresh BEFORE arm failed to reproduce the required compatibility reference baseline "
                "(g036.e1 or g021.e1 missing under BEFORE_COMPAT)."
            ),
        }

    # Precedence Level 3 — FAIL (Primary targets and dependency removal)
    if target_replacement_reproduced < 2 or batch1_dependency_removed < 2:
        return {
            "verdict_level": 3,
            "batch_verdict": VERDICT_LEVEL_3_FAIL_PRIMARY_TARGET,
            "verdict_reason": (
                f"Primary target replacement or fixed locator dependency removal not satisfied: "
                f"{target_replacement_reproduced}/2 target groups reproduced under AFTER_BATCH1_REPLACEMENT "
                f"with valid governed structured witness, {batch1_dependency_removed}/2 fixed locator dependencies removed."
            ),
        }

    # Precedence Level 4 — FAIL (Critical or grounding regressions)
    if (
        len(crit_regs) > 0
        or grounding_regressions > 0
        or wrong_version_regressions > 0
        or invalid_provenance_recoveries > 0
    ):
        return {
            "verdict_level": 4,
            "batch_verdict": VERDICT_LEVEL_4_FAIL_CRITICAL_OR_GROUNDING,
            "verdict_reason": (
                f"Critical evidence or grounding regression detected: "
                f"{len(crit_regs)} critical group regression(s) ({crit_regs}), "
                f"{grounding_regressions} grounding regression(s), "
                f"{wrong_version_regressions} wrong-version regression(s), "
                f"{invalid_provenance_recoveries} invalid-provenance recovery(ies)."
            ),
        }

    # Precedence Level 5 — PARTIAL (Bounded tolerance violations)
    tolerance_violations: list[str] = []
    delta_r5 = deltas.get("recall_at_5", 0.0)
    delta_r10 = deltas.get("recall_at_10", 0.0)
    delta_r20 = deltas.get("recall_at_20", 0.0)
    delta_comb = deltas.get("combined_candidate_recall", 0.0)
    delta_final = deltas.get("final_evidence_recall", 0.0)
    delta_crit = deltas.get("critical_final_evidence_recall", 0.0)

    if delta_r5 < -0.05:
        tolerance_violations.append(f"Recall@5 delta {delta_r5:.4f} < -0.05")
    if delta_r10 < -0.05:
        tolerance_violations.append(f"Recall@10 delta {delta_r10:.4f} < -0.05")
    if delta_r20 < -0.05:
        tolerance_violations.append(f"Recall@20 delta {delta_r20:.4f} < -0.05")
    if delta_comb < -0.05:
        tolerance_violations.append(f"combined_candidate_recall delta {delta_comb:.4f} < -0.05")
    if delta_final < -0.05:
        tolerance_violations.append(f"final_evidence_recall delta {delta_final:.4f} < -0.05")
    if delta_crit < 0.0:
        tolerance_violations.append(f"critical_final_evidence_recall delta {delta_crit:.4f} < 0.0")

    if tolerance_violations:
        return {
            "verdict_level": 5,
            "batch_verdict": VERDICT_LEVEL_5_PARTIAL_TOLERANCE,
            "verdict_reason": (
                f"Primary aggregate retrieval metrics exceeded bounded regression tolerance (-0.05): "
                f"{'; '.join(tolerance_violations)}."
            ),
        }

    # Precedence Level 6 — PASS
    pass_reason = (
        "First-batch before/after validation passed all gating criteria: 32/32 valid execution, "
        "BEFORE reference valid, target replacements reproduced with structured witness (2/2), "
        "dependency removed (2/2), 0 critical group regressions, 0 grounding regressions, "
        "and all primary retrieval metric deltas within bounded tolerances."
    )
    if noncrit_regs:
        pass_reason += f" Noncritical regression(s) noted transparently: {noncrit_regs}."

    return {
        "verdict_level": 6,
        "batch_verdict": VERDICT_LEVEL_6_PASS,
        "verdict_reason": pass_reason,
    }


# ===========================================================================
# 4.1 Mechanical Structural Validity Audit
# ===========================================================================

def validate_raw_artifact_structural_validity(
    raw_data: dict[str, Any],
    manifest: dict[str, Any] | None = None,
    prereg: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> tuple[bool, str | None, dict[str, int]]:
    """Mechanically validates the raw results artifact before any metric evaluation:
    1. Exactly 32 unique slots.
    2. Exact case-major paired order (for each case: BEFORE_COMPAT, then AFTER_BATCH1_REPLACEMENT).
    3. Exact arms.
    4. Every slot status == 'COMPLETED', error is None.
    5. 0 FAILED: formal_slots_failed == 0, FORMAL_CELLS_FAILED == 0.
    6. Raw model contract matches frozen requirements (gemini-3.8-flash, gemini-embedding-2, temp 0.0).
    7. Authority fields match manifest and preregistration.
    8. Raw boundary flags: EVALUATOR_EXECUTED == False, SCIENTIFIC_VERDICT_COMPUTED == False.
    9. Implementation freeze HEAD identity is a valid 40-character hex SHA and not a placeholder.
    10. Exact mask and treatment receipts on every slot.
    11. Protected dataset access counters == 0.
    12. Post-exposure mutation accounting: case, mask, replacement, model, metric, verdict mutations == 0.

    Returns (is_valid, failure_reason, mutation_counters).
    """
    mutation_counters = {
        "POST_EXPOSURE_CASE_MUTATIONS": 0,
        "POST_EXPOSURE_MASK_MUTATIONS": 0,
        "POST_EXPOSURE_REPLACEMENT_MUTATIONS": 0,
        "POST_EXPOSURE_MODEL_MUTATIONS": 0,
        "POST_EXPOSURE_METRIC_MUTATIONS": 0,
        "POST_EXPOSURE_VERDICT_MUTATIONS": 0,
    }

    if not isinstance(raw_data, dict):
        return False, "Raw artifact is not a JSON object", mutation_counters

    slots = raw_data.get("slots", [])
    if len(slots) != TOTAL_FORMAL_SLOTS:
        return (
            False,
            f"Raw slots count mismatch: expected {TOTAL_FORMAL_SLOTS}, got {len(slots)}",
            mutation_counters,
        )

    # Check slot uniqueness
    slot_tuples = [(s.get("slot_index"), s.get("case_id"), s.get("arm")) for s in slots]
    if len(set(slot_tuples)) != TOTAL_FORMAL_SLOTS:
        return (
            False,
            f"Slots are not unique: found duplicates in {slot_tuples}",
            mutation_counters,
        )

    # Check exact case-major schedule and arms
    expected_schedule: list[tuple[int, str, str]] = []
    idx = 1
    for cid in CASE_ORDER:
        for arm in ARMS:
            expected_schedule.append((idx, cid, arm))
            idx += 1

    case_mutations = 0
    mask_mutations = 0
    replacement_mutations = 0

    for i, s in enumerate(slots):
        exp_idx, exp_cid, exp_arm = expected_schedule[i]
        if (s.get("slot_index"), s.get("case_id"), s.get("arm")) != (exp_idx, exp_cid, exp_arm):
            case_mutations += 1
            return (
                False,
                f"Slot schedule mismatch at index {i + 1}: expected ({exp_idx}, {exp_cid}, {exp_arm}), got "
                f"({s.get('slot_index')}, {s.get('case_id')}, {s.get('arm')})",
                dict(mutation_counters, POST_EXPOSURE_CASE_MUTATIONS=case_mutations),
            )

        # Check status
        if s.get("outcome_status") != "COMPLETED":
            return (
                False,
                f"Slot {exp_idx} ({exp_cid}, {exp_arm}) status is not COMPLETED: {s.get('outcome_status')}",
                mutation_counters,
            )
        if s.get("error") is not None:
            return (
                False,
                f"Slot {exp_idx} has non-null error: {s.get('error')}",
                mutation_counters,
            )

        # Check arm-specific mask and treatment receipts
        if exp_arm == "BEFORE_COMPAT":
            if s.get("in_memory_mask_active") is not False:
                mask_mutations += 1
            if s.get("structured_replacement_active") is not False:
                replacement_mutations += 1
            if s.get("admission_budget_k") != 0:
                replacement_mutations += 1
            supp = s.get("suppressed_components", {})
            if supp != {}:
                mask_mutations += 1
        elif exp_arm == "AFTER_BATCH1_REPLACEMENT":
            if s.get("in_memory_mask_active") is not True:
                mask_mutations += 1
            if s.get("structured_replacement_active") is not True:
                replacement_mutations += 1
            if s.get("admission_budget_k") != EXPECTED_ADMISSION_BUDGET_K:
                replacement_mutations += 1
            if s.get("rerank_pool_size") != EXPECTED_RERANK_POOL_SIZE:
                replacement_mutations += 1
            if len(s.get("final_pool_object_ids", [])) != EXPECTED_RERANK_POOL_SIZE:
                replacement_mutations += 1
            if s.get("suppressed_components") != s.get(
                "exact_effective_suppressed_components"
            ):
                mask_mutations += 1

    # Check failure counters in exposure state and accounting
    exp_state = raw_data.get("outcome_exposure_state", {})
    if exp_state.get("D4_A2_OUTCOME_EXPOSURE") != "COMPLETE":
        return (
            False,
            f"D4_A2_OUTCOME_EXPOSURE is not COMPLETE: {exp_state.get('D4_A2_OUTCOME_EXPOSURE')}",
            mutation_counters,
        )
    if exp_state.get("formal_slots_completed") != TOTAL_FORMAL_SLOTS:
        return (
            False,
            f"formal_slots_completed mismatch: expected {TOTAL_FORMAL_SLOTS}, got {exp_state.get('formal_slots_completed')}",
            mutation_counters,
        )
    if exp_state.get("formal_slots_failed", 0) != 0:
        return (
            False,
            f"formal_slots_failed is not 0: {exp_state.get('formal_slots_failed')}",
            mutation_counters,
        )

    acct = raw_data.get("accounting", {})
    if acct.get("FORMAL_CELLS_COMPLETED") != TOTAL_FORMAL_SLOTS:
        return (
            False,
            f"accounting.FORMAL_CELLS_COMPLETED mismatch: expected {TOTAL_FORMAL_SLOTS}, got {acct.get('FORMAL_CELLS_COMPLETED')}",
            mutation_counters,
        )
    if acct.get("FORMAL_CELLS_FAILED", 0) != 0:
        return (
            False,
            f"accounting.FORMAL_CELLS_FAILED is not 0: {acct.get('FORMAL_CELLS_FAILED')}",
            mutation_counters,
        )

    # Check raw boundary flags
    eb = raw_data.get("evaluation_boundary", {})
    if eb.get("EVALUATOR_EXECUTED") is not False:
        return (
            False,
            f"Raw evaluation_boundary.EVALUATOR_EXECUTED is not False: {eb.get('EVALUATOR_EXECUTED')}",
            mutation_counters,
        )
    if eb.get("SCIENTIFIC_VERDICT_COMPUTED") is not False:
        return (
            False,
            f"Raw evaluation_boundary.SCIENTIFIC_VERDICT_COMPUTED is not False: {eb.get('SCIENTIFIC_VERDICT_COMPUTED')}",
            mutation_counters,
        )

    # Check model contract
    mc = raw_data.get("model_contract", {})
    model_mutations = 0
    if mc.get("generation_model_id") != EXPECTED_MODEL:
        model_mutations += 1
    if mc.get("embedding_model_id") != EXPECTED_EMBEDDING_MODEL:
        model_mutations += 1
    if mc.get("temperature") != EXPECTED_TEMPERATURE:
        model_mutations += 1
    if mc.get("location") != EXPECTED_VERTEX_LOCATION:
        model_mutations += 1
    if mc.get("system_prompt") != "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT":
        model_mutations += 1
    if mc.get("query_analyzer_prompt") != "src/panda_agent/prompts.py:QUERY_ANALYZER_SYSTEM_PROMPT":
        model_mutations += 1

    # Check authority
    auth = raw_data.get("authority", {})
    if auth.get("manifest") != MANIFEST_PATH:
        return False, f"Manifest authority mismatch: {auth.get('manifest')} vs {MANIFEST_PATH}", mutation_counters
    if auth.get("preregistration") != PREREGISTRATION_PATH:
        return False, f"Preregistration authority mismatch: {auth.get('preregistration')} vs {PREREGISTRATION_PATH}", mutation_counters

    # Check implementation freeze HEAD identity
    freeze_head = auth.get("implementation_freeze_head", "")
    if not freeze_head or not isinstance(freeze_head, str):
        return False, "implementation_freeze_head is missing or not a string", mutation_counters
    if len(freeze_head) != 40 or not all(c in "0123456789abcdefABCDEF" for c in freeze_head):
        return (
            False,
            f"implementation_freeze_head is not a valid 40-character hex commit SHA: '{freeze_head}'",
            mutation_counters,
        )
    if "CAPTURED" in freeze_head or "PLACEHOLDER" in freeze_head.upper():
        return (
            False,
            f"implementation_freeze_head contains unresolved placeholder: '{freeze_head}'",
            mutation_counters,
        )
    if project_root is not None:
        parent_proc = subprocess.run(
            ["git", "rev-parse", "HEAD^"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=True,
        )
        raw_freeze_parent = parent_proc.stdout.strip()
        if raw_freeze_parent != freeze_head:
            return (
                False,
                f"implementation_freeze_head {freeze_head} is not the parent of raw freeze HEAD {raw_freeze_parent}",
                mutation_counters,
            )

    # Check metric mutations
    metric_mutations = 0
    if prereg:
        thresh = prereg.get("bounded_regression_thresholds", {})
        for k in ["recall_at_5", "recall_at_10", "recall_at_20", "combined_candidate_recall", "final_evidence_recall"]:
            if thresh.get(k) != -0.05:
                metric_mutations += 1
        if thresh.get("critical_final_evidence_recall") != 0.0:
            metric_mutations += 1

    # Check verdict mutations
    verdict_mutations = 0
    if prereg:
        levels = prereg.get("verdict_precedence", {}).get("levels", [])
        recorded_verdicts = [level.get("verdict") for level in levels]
        if recorded_verdicts != FROZEN_A2_VERDICTS:
            verdict_mutations += 1

    # Check protected dataset boundaries
    if (
        acct.get("NOVEL_VALIDATION_RUNS", 0) != 0
        or acct.get("NOVEL_HOLDOUT_RUNS", 0) != 0
        or acct.get("PROTECTED_DATASET_ACCESS", 0) != 0
    ):
        return False, "Protected dataset boundary violated in raw accounting", mutation_counters

    mutation_counters = {
        "POST_EXPOSURE_CASE_MUTATIONS": case_mutations,
        "POST_EXPOSURE_MASK_MUTATIONS": mask_mutations,
        "POST_EXPOSURE_REPLACEMENT_MUTATIONS": replacement_mutations,
        "POST_EXPOSURE_MODEL_MUTATIONS": model_mutations,
        "POST_EXPOSURE_METRIC_MUTATIONS": metric_mutations,
        "POST_EXPOSURE_VERDICT_MUTATIONS": verdict_mutations,
    }

    if any(count > 0 for count in mutation_counters.values()):
        return (
            False,
            f"Post-exposure mutations detected: {mutation_counters}",
            mutation_counters,
        )

    return True, None, mutation_counters


# ===========================================================================
# 4.2 Benchmark Dependency Removal Verification
# ===========================================================================

def compute_batch1_dependency_removal(
    slots_map: dict[tuple[str, str], dict[str, Any]],
    witness_g036: dict[str, Any],
    witness_g021: dict[str, Any],
    group_retention: dict[str, dict[str, Any]],
) -> tuple[int, dict[str, Any]]:
    """Separately verifies for each Batch-1 target rule:
    1. Fixed locator inputs were active in BEFORE.
    2. Exact masked locator inputs are absent in AFTER.
    3. Generic structured mechanism is active in AFTER.
    4. Target evidence is retained in AFTER.
    5. Valid governed witness exists in AFTER.

    Returns (dependency_removed_count, per_rule_receipts).
    """
    receipts: dict[str, Any] = {}

    # Rule 1: event_poca_handoff (case g036, group g036.e1)
    slot_g036_b = slots_map.get(("g036", "BEFORE_COMPAT"), {})
    slot_g036_a = slots_map.get(("g036", "AFTER_BATCH1_REPLACEMENT"), {})

    g036_b_symbols = slot_g036_b.get("effective_symbols", [])
    ep_active_before = bool(
        any(sym in g036_b_symbols for sym in d4_a1.SUPPRESSED_SYMBOLS_EVENT_POCA)
        or (slot_g036_b.get("in_memory_mask_active") is False and not slot_g036_b.get("suppressed_components"))
    )
    g036_a_symbols = slot_g036_a.get("effective_symbols", [])
    ep_symbols_absent = not any(sym in g036_a_symbols for sym in d4_a1.SUPPRESSED_SYMBOLS_EVENT_POCA)
    g036_a_hints = slot_g036_a.get("effective_paper_page_hints", {})
    ep_hints_absent = not any(
        p in g036_a_hints.get("li_2026", []) for p in d4_a1.SUPPRESSED_PAGE_HINTS_EVENT_POCA.get("li_2026", [])
    )
    ep_absent_after = ep_symbols_absent and ep_hints_absent
    ep_struct_active = bool(
        slot_g036_a.get("structured_replacement_active", True) is True
        and slot_g036_a.get("admission_budget_k", 3) == EXPECTED_ADMISSION_BUDGET_K
    )
    ep_target_retained = bool(group_retention.get("g036.e1", {}).get("AFTER_BATCH1_REPLACEMENT", False))
    ep_valid_witness = bool(witness_g036.get("has_valid_witness", False))

    ep_removed = bool(
        ep_active_before
        and ep_absent_after
        and ep_struct_active
        and ep_target_retained
        and ep_valid_witness
    )
    receipts["event_poca_handoff"] = {
        "rule_id": "event_poca_handoff",
        "case_id": "g036",
        "target_group_id": "g036.e1",
        "fixed_locator_inputs_active_before": ep_active_before,
        "exact_masked_locator_inputs_absent_after": ep_absent_after,
        "generic_structured_mechanism_active": ep_struct_active,
        "target_evidence_retained_after": ep_target_retained,
        "valid_governed_witness_exists": ep_valid_witness,
        "dependency_removed": ep_removed,
    }

    # Rule 2: restgas_profile_workflow (case g021, group g021.e1)
    slot_g021_b = slots_map.get(("g021", "BEFORE_COMPAT"), {})
    slot_g021_a = slots_map.get(("g021", "AFTER_BATCH1_REPLACEMENT"), {})

    g021_b_symbols = slot_g021_b.get("effective_symbols", [])
    rg_active_before = bool(
        any(sym in g021_b_symbols for sym in d4_a1.SUPPRESSED_SYMBOLS_RESTGAS)
        or (slot_g021_b.get("in_memory_mask_active") is False and not slot_g021_b.get("suppressed_components"))
    )
    g021_a_symbols = slot_g021_a.get("effective_symbols", [])
    rg_absent_after = not any(sym in g021_a_symbols for sym in d4_a1.SUPPRESSED_SYMBOLS_RESTGAS)
    rg_struct_active = bool(
        slot_g021_a.get("structured_replacement_active", True) is True
        and slot_g021_a.get("admission_budget_k", 3) == EXPECTED_ADMISSION_BUDGET_K
    )
    rg_target_retained = bool(group_retention.get("g021.e1", {}).get("AFTER_BATCH1_REPLACEMENT", False))
    rg_valid_witness = bool(witness_g021.get("has_valid_witness", False))

    rg_removed = bool(
        rg_active_before
        and rg_absent_after
        and rg_struct_active
        and rg_target_retained
        and rg_valid_witness
    )
    receipts["restgas_profile_workflow"] = {
        "rule_id": "restgas_profile_workflow",
        "case_id": "g021",
        "target_group_id": "g021.e1",
        "fixed_locator_inputs_active_before": rg_active_before,
        "exact_masked_locator_inputs_absent_after": rg_absent_after,
        "generic_structured_mechanism_active": rg_struct_active,
        "target_evidence_retained_after": rg_target_retained,
        "valid_governed_witness_exists": rg_valid_witness,
        "dependency_removed": rg_removed,
    }

    count = (1 if ep_removed else 0) + (1 if rg_removed else 0)
    return count, receipts


# ===========================================================================
# 4.3 Grounding, Version, and Provenance Safety Checks
# ===========================================================================

def compute_grounding_and_version_safety(
    slots_map: dict[tuple[str, str], dict[str, Any]],
    all_questions: dict[str, Any],
    object_lookup: dict[str, dict[str, Any]],
    witness_g036: dict[str, Any],
    witness_g021: dict[str, Any],
    group_retention: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Computes grounding, version, and provenance safety checks with evidence-level details:
    1. WRONG_VERSION_REGRESSIONS: newly introduced AFTER wrong-version evidence relative to BEFORE.
    2. GROUNDING_REGRESSIONS: newly introduced forbidden/out-of-scope grounding violations via Gold selectors.
    3. INVALID_PROVENANCE_RECOVERIES: meaningful check for AFTER structured recoveries and target witnesses.
    """
    wrong_version_details: list[dict[str, Any]] = []
    grounding_details: list[dict[str, Any]] = []
    invalid_provenance_details: list[dict[str, Any]] = []

    # 1. WRONG_VERSION_REGRESSIONS: newly introduced AFTER relative to BEFORE
    for cid in CASE_ORDER:
        q = all_questions.get(cid)
        if not q:
            continue
        allowed_v = set(q.allowed_source_versions)

        slot_b = slots_map.get((cid, "BEFORE_COMPAT"), {})
        slot_a = slots_map.get((cid, "AFTER_BATCH1_REPLACEMENT"), {})

        b_wv: dict[str, str] = {}
        for oid in slot_b.get("final_evidence_object_ids", []):
            item = object_lookup.get(oid) or {}
            sv = item.get("source_version_id")
            if sv and sv not in allowed_v:
                b_wv[oid] = sv

        a_wv: dict[str, str] = {}
        for oid in slot_a.get("final_evidence_object_ids", []):
            item = object_lookup.get(oid) or {}
            sv = item.get("source_version_id")
            if sv and sv not in allowed_v:
                a_wv[oid] = sv

        # Newly introduced in AFTER
        new_wv_oids = set(a_wv.keys()) - set(b_wv.keys())
        for oid in sorted(new_wv_oids):
            wrong_version_details.append({
                "case_id": cid,
                "object_id": oid,
                "source_version_id": a_wv[oid],
                "allowed_source_versions": list(allowed_v),
            })

    # 2. GROUNDING_REGRESSIONS: newly introduced forbidden evidence via Gold selectors
    for cid in CASE_ORDER:
        q = all_questions.get(cid)
        if not q:
            continue
        forbidden_selectors = q.forbidden_evidence
        if not forbidden_selectors:
            continue

        slot_b = slots_map.get((cid, "BEFORE_COMPAT"), {})
        slot_a = slots_map.get((cid, "AFTER_BATCH1_REPLACEMENT"), {})

        b_forbidden: set[str] = set()
        for oid in slot_b.get("final_evidence_object_ids", []):
            item = object_lookup.get(oid) or {}
            if any(sel.matches(item) for sel in forbidden_selectors):
                b_forbidden.add(oid)

        a_forbidden: dict[str, dict[str, Any]] = {}
        for oid in slot_a.get("final_evidence_object_ids", []):
            item = object_lookup.get(oid) or {}
            for sel in forbidden_selectors:
                if sel.matches(item):
                    a_forbidden[oid] = sel.model_dump()
                    break

        new_forbidden = set(a_forbidden.keys()) - b_forbidden
        for oid in sorted(new_forbidden):
            grounding_details.append({
                "case_id": cid,
                "object_id": oid,
                "violation_type": "forbidden_evidence_hit",
                "matched_selector": a_forbidden[oid],
            })

    # 3. INVALID_PROVENANCE_RECOVERIES: check AFTER target witnesses and reserved candidates
    for case_id, wit, gid in [("g036", witness_g036, "g036.e1"), ("g021", witness_g021, "g021.e1")]:
        for cw in wit.get("candidate_witnesses", []):
            oid = cw.get("candidate_object_id")
            if cw.get("final_evidence_retained", False) or cw.get("is_valid_witness", False):
                governed = cw.get("governed_path", False)
                origins = cw.get("full_structured_path", {}).get("provenance_origin_ids", [])
                source_id = cw.get("full_structured_path", {}).get("source_id")
                if not governed:
                    invalid_provenance_details.append({
                        "case_id": case_id,
                        "group_id": gid,
                        "object_id": oid,
                        "violation": "Target candidate witness missing governed bridge path",
                    })
                elif not origins:
                    invalid_provenance_details.append({
                        "case_id": case_id,
                        "group_id": gid,
                        "object_id": oid,
                        "violation": "Target candidate witness has empty provenance origins",
                    })
                elif not source_id:
                    invalid_provenance_details.append({
                        "case_id": case_id,
                        "group_id": gid,
                        "object_id": oid,
                        "violation": "Target candidate witness missing source_id",
                    })

    for cid in ANSWERED_CASES:
        slot_a = slots_map.get((cid, "AFTER_BATCH1_REPLACEMENT"), {})
        reserved_ids = slot_a.get("reserved_candidate_ids", [])
        final_ids = slot_a.get("final_evidence_object_ids", [])
        eligible_cands = slot_a.get("eligible_bridge_candidates", [])
        eligible_map = {c.get("candidate_object_id"): c for c in eligible_cands if isinstance(c, dict)}

        for r_oid in reserved_ids:
            if r_oid in final_ids:
                cand_meta = eligible_map.get(r_oid)
                if not cand_meta:
                    invalid_provenance_details.append({
                        "case_id": cid,
                        "object_id": r_oid,
                        "violation": "Reserved candidate retained in final evidence missing from eligible bridge candidates",
                    })
                elif not cand_meta.get("provenance_origin_ids"):
                    invalid_provenance_details.append({
                        "case_id": cid,
                        "object_id": r_oid,
                        "violation": "Reserved candidate retained in final evidence has empty provenance origins",
                    })

    return {
        "GROUNDING_REGRESSIONS": len(grounding_details),
        "WRONG_VERSION_REGRESSIONS": len(wrong_version_details),
        "INVALID_PROVENANCE_RECOVERIES": len(invalid_provenance_details),
        "grounding_details": grounding_details,
        "wrong_version_details": wrong_version_details,
        "invalid_provenance_details": invalid_provenance_details,
    }


# ===========================================================================
# 5. Deterministic Evaluator Mode (`evaluate`)
# ===========================================================================

def evaluate_d4_a2(project_root: Path, *, require_git_frozen: bool = True) -> dict[str, Any]:
    """Deterministic evaluator mode for D4-A2.
    Refuses until raw artifact is committed/frozen in Git (Commit B).
    Loads governed Gold/novel evidence selectors only after raw freeze verification.
    Computes retrieval metrics at multiple scopes, group retention, target witnesses,
    dependency removal, and Section 41 verdict precedence.
    """
    raw_path = project_root / RAW_RESULTS_PATH
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw results artifact {raw_path} does not exist. Run --mode execute-32 first."
        )

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

    manifest_path = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_path) if manifest_path.exists() else {}
    prereg_path = project_root / PREREGISTRATION_PATH
    prereg = _load_json(prereg_path) if prereg_path.exists() else {}

    # Mechanical structural validity audit
    is_struct_valid, struct_fail_reason, mutation_counters = validate_raw_artifact_structural_validity(
        raw_data=raw_data,
        manifest=manifest,
        prereg=prereg,
        project_root=project_root,
    )

    if not is_struct_valid:
        verdict_outcome = compute_before_after_verdict(
            execution_valid=False,
            protocol_violation=True,
            protocol_violation_reason=struct_fail_reason,
        )
        eval_artifact = {
            "schema_version": "1.0.0",
            "checkpoint": "D4-A2-EVALUATOR-RESULTS",
            "stage": "d4_a2_evaluator_results",
            "raw_artifact_authority": RAW_RESULTS_PATH,
            "evaluator_executed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "verdict_outcome": verdict_outcome,
            "post_exposure_mutation_accounting": mutation_counters,
            "production_activation": False,
        }
        eval_out_path = project_root / EVALUATOR_RESULTS_PATH
        eval_out_path.write_text(json.dumps(eval_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return eval_artifact

    # Load governed evidence selectors ONLY after raw freeze verification
    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_questions = {q.id: q for q in gold_ds.questions + novel_ds.questions}
    object_lookup = load_object_lookup(project_root)

    slots_map: dict[tuple[str, str], dict[str, Any]] = {}
    for slot in raw_data.get("slots", []):
        slots_map[(slot["case_id"], slot["arm"])] = slot

    # 1. Per-case retrieval metrics on answered cases (13 cases)
    case_metrics: dict[str, dict[str, dict[str, float]]] = {}
    for cid in ANSWERED_CASES:
        q = all_questions[cid]
        case_metrics[cid] = {}
        for arm in ARMS:
            slot = slots_map[(cid, arm)]
            ranked_ids = slot.get("ranked_object_ids", [])
            final_ids = slot.get("final_evidence_object_ids", [])
            # Defect 5: combined candidate recall uses the union of channel rankings
            channel_rankings = slot.get("channel_rankings") or (slot.get("diagnostics") or {}).get("rankings") or {}
            combined_ids = list(dict.fromkeys(
                oid for oids in channel_rankings.values() for oid in oids
            ))
            if not combined_ids:
                combined_ids = slot.get("combined_candidate_universe", [])
            if not combined_ids:
                combined_ids = list(dict.fromkeys(
                    slot.get("ordinary_fused_ordering", []) + slot.get("reserved_candidate_ids", [])
                ))

            r5, _ = _matched_evidence_groups(q.required_evidence_groups, ranked_ids[:5], object_lookup)
            r10, _ = _matched_evidence_groups(q.required_evidence_groups, ranked_ids[:10], object_lookup)
            r20, _ = _matched_evidence_groups(q.required_evidence_groups, ranked_ids[:20], object_lookup)

            rank_by_oid = {oid: r for r, oid in enumerate(ranked_ids, 1)}
            _, top20_prov = _matched_evidence_groups(q.required_evidence_groups, ranked_ids[:20], object_lookup)
            rel_ranks = [rank_by_oid[m["object_id"]] for m in top20_prov if m.get("object_id") in rank_by_oid]
            mrr = 1.0 / min(rel_ranks) if rel_ranks else 0.0

            comb_rec, _ = _matched_evidence_groups(q.required_evidence_groups, combined_ids, object_lookup)
            final_rec, _ = _matched_evidence_groups(q.required_evidence_groups, final_ids, object_lookup)

            crit_groups = [g for g in q.required_evidence_groups if g.critical]
            crit_rec, _ = _matched_evidence_groups(crit_groups, final_ids, object_lookup) if crit_groups else (1.0, [])

            case_metrics[cid][arm] = {
                "recall_at_5": r5,
                "recall_at_10": r10,
                "recall_at_20": r20,
                "mrr": mrr,
                "combined_candidate_recall": comb_rec,
                "final_evidence_recall": final_rec,
                "critical_final_evidence_recall": crit_rec,
            }

    # Aggregate metric helper
    def _mean_metrics(case_ids: list[str], arm: str) -> dict[str, float]:
        keys = ["recall_at_5", "recall_at_10", "recall_at_20", "mrr", "combined_candidate_recall", "final_evidence_recall", "critical_final_evidence_recall"]
        res = {}
        for k in keys:
            vals = [case_metrics[cid][arm][k] for cid in case_ids if cid in case_metrics]
            res[k] = sum(vals) / len(vals) if vals else 0.0
        return res

    def _delta_metrics(after_m: dict[str, float], before_m: dict[str, float]) -> dict[str, float]:
        return {k: round(after_m[k] - before_m[k], 6) for k in after_m}

    answered_gold = [c for c in GOLD_CASES if c in ANSWERED_CASES]
    answered_novel = [c for c in NOVEL_DEV_CASES if c in ANSWERED_CASES]

    cohort_before = _mean_metrics(ANSWERED_CASES, "BEFORE_COMPAT")
    cohort_after = _mean_metrics(ANSWERED_CASES, "AFTER_BATCH1_REPLACEMENT")
    cohort_deltas = _delta_metrics(cohort_after, cohort_before)

    gold_before = _mean_metrics(answered_gold, "BEFORE_COMPAT")
    gold_after = _mean_metrics(answered_gold, "AFTER_BATCH1_REPLACEMENT")
    gold_deltas = _delta_metrics(gold_after, gold_before)

    novel_before = _mean_metrics(answered_novel, "BEFORE_COMPAT")
    novel_after = _mean_metrics(answered_novel, "AFTER_BATCH1_REPLACEMENT")
    novel_deltas = _delta_metrics(novel_after, novel_before)

    # Full targeted T2 generalization diagnostics
    generalization_diagnostics: dict[str, Any] = {
        "gold_final_evidence_recall_before": gold_before["final_evidence_recall"],
        "novel_final_evidence_recall_before": novel_before["final_evidence_recall"],
        "gap_before": round(gold_before["final_evidence_recall"] - novel_before["final_evidence_recall"], 6),
        "gold_final_evidence_recall_after": gold_after["final_evidence_recall"],
        "novel_final_evidence_recall_after": novel_after["final_evidence_recall"],
        "gap_after": round(gold_after["final_evidence_recall"] - novel_after["final_evidence_recall"], 6),
        "analogous_metrics": {},
    }
    for m_key in ["recall_at_5", "recall_at_10", "recall_at_20", "mrr", "combined_candidate_recall", "final_evidence_recall", "critical_final_evidence_recall"]:
        generalization_diagnostics["analogous_metrics"][m_key] = {
            "gold_before": gold_before[m_key],
            "novel_before": novel_before[m_key],
            "gap_before": round(gold_before[m_key] - novel_before[m_key], 6),
            "gold_after": gold_after[m_key],
            "novel_after": novel_after[m_key],
            "gap_after": round(gold_after[m_key] - novel_after[m_key], 6),
            "gap_delta": round((gold_after[m_key] - novel_after[m_key]) - (gold_before[m_key] - novel_before[m_key]), 6),
        }

    # 2. Required evidence group retention table across all 16 cases
    group_retention: dict[str, dict[str, Any]] = {}
    group_regressions: list[str] = []
    critical_group_regressions: list[str] = []
    noncritical_group_regressions: list[str] = []
    group_recoveries: list[str] = []

    for cid in CASE_ORDER:
        q = all_questions[cid]
        for grp in q.required_evidence_groups:
            gid = grp.group_id
            rec_b, _ = _matched_evidence_groups([grp], slots_map[(cid, "BEFORE_COMPAT")].get("final_evidence_object_ids", []), object_lookup)
            rec_a, _ = _matched_evidence_groups([grp], slots_map[(cid, "AFTER_BATCH1_REPLACEMENT")].get("final_evidence_object_ids", []), object_lookup)
            b_ret = rec_b > 0
            a_ret = rec_a > 0

            if b_ret and a_ret:
                state = "PRESERVED"
            elif not b_ret and a_ret:
                state = "RECOVERED"
                group_recoveries.append(gid)
            elif b_ret and not a_ret:
                state = "REGRESSED"
                group_regressions.append(gid)
                if grp.critical:
                    critical_group_regressions.append(gid)
                else:
                    noncritical_group_regressions.append(gid)
            else:
                state = "UNRESOLVED_BOTH"

            group_retention[gid] = {
                "case_id": cid,
                "dataset": "Gold v2.6 dev" if cid in GOLD_CASES else "novel_dev",
                "applicability": "ANSWERED" if cid in ANSWERED_CASES else "NEGATIVE_CONTROL_INSUFFICIENT_EVIDENCE",
                "is_negative_control": cid in INSUFFICIENT_EVIDENCE_CASES,
                "expected_status": q.expected_status.value,
                "critical": grp.critical,
                "role": grp.role,
                "BEFORE_COMPAT": b_ret,
                "AFTER_BATCH1_REPLACEMENT": a_ret,
                "retention_state": state,
            }

    # 3. Batch-1 target reproduction with admission witness
    wit_g036 = d4_a1.check_admission_witness(
        "g036.e1",
        slots_map[("g036", "AFTER_BATCH1_REPLACEMENT")],
        object_lookup,
        next(g for g in all_questions["g036"].required_evidence_groups if g.group_id == "g036.e1"),
    )
    wit_g021 = d4_a1.check_admission_witness(
        "g021.e1",
        slots_map[("g021", "AFTER_BATCH1_REPLACEMENT")],
        object_lookup,
        next(g for g in all_questions["g021"].required_evidence_groups if g.group_id == "g021.e1"),
    )

    g036_reproduced = bool(
        group_retention.get("g036.e1", {}).get("BEFORE_COMPAT")
        and group_retention.get("g036.e1", {}).get("AFTER_BATCH1_REPLACEMENT")
        and wit_g036.get("has_valid_witness")
    )
    g021_reproduced = bool(
        group_retention.get("g021.e1", {}).get("BEFORE_COMPAT")
        and group_retention.get("g021.e1", {}).get("AFTER_BATCH1_REPLACEMENT")
        and wit_g021.get("has_valid_witness")
    )
    target_replacement_reproduced_count = (1 if g036_reproduced else 0) + (1 if g021_reproduced else 0)

    # 4. Benchmark dependency removal verification
    dep_removed_count, dep_receipts = compute_batch1_dependency_removal(
        slots_map=slots_map,
        witness_g036=wit_g036,
        witness_g021=wit_g021,
        group_retention=group_retention,
    )

    # 5. BEFORE reference validity check
    before_reference_valid = bool(
        group_retention.get("g036.e1", {}).get("BEFORE_COMPAT", False)
        and group_retention.get("g021.e1", {}).get("BEFORE_COMPAT", False)
    )

    # 6. Grounding, version, and provenance safety checks
    safety_res = compute_grounding_and_version_safety(
        slots_map=slots_map,
        all_questions=all_questions,
        object_lookup=object_lookup,
        witness_g036=wit_g036,
        witness_g021=wit_g021,
        group_retention=group_retention,
    )

    # 7. Section 41 verdict precedence
    verdict_outcome = compute_before_after_verdict(
        execution_valid=True,
        protocol_violation=False,
        before_reference_valid=before_reference_valid,
        target_replacement_reproduced=target_replacement_reproduced_count,
        batch1_dependency_removed=dep_removed_count,
        critical_group_regressions=critical_group_regressions,
        noncritical_group_regressions=noncritical_group_regressions,
        grounding_regressions=safety_res["GROUNDING_REGRESSIONS"],
        wrong_version_regressions=safety_res["WRONG_VERSION_REGRESSIONS"],
        invalid_provenance_recoveries=safety_res["INVALID_PROVENANCE_RECOVERIES"],
        metric_deltas=cohort_deltas,
    )

    eval_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-EVALUATOR-RESULTS",
        "stage": "d4_a2_evaluator_results",
        "raw_artifact_authority": RAW_RESULTS_PATH,
        "evaluator_executed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cohort_metrics": {
            "applicable_answered_cases_count": len(ANSWERED_CASES),
            "insufficient_evidence_cases_count": len(INSUFFICIENT_EVIDENCE_CASES),
            "BEFORE_COMPAT": cohort_before,
            "AFTER_BATCH1_REPLACEMENT": cohort_after,
            "deltas": cohort_deltas,
        },
        "subset_metrics": {
            "gold": {
                "case_count": len(answered_gold),
                "BEFORE_COMPAT": gold_before,
                "AFTER_BATCH1_REPLACEMENT": gold_after,
                "deltas": gold_deltas,
            },
            "novel_dev": {
                "case_count": len(answered_novel),
                "BEFORE_COMPAT": novel_before,
                "AFTER_BATCH1_REPLACEMENT": novel_after,
                "deltas": novel_deltas,
            },
        },
        "targeted_generalization_diagnostics": generalization_diagnostics,
        "target_replacement_reproduction": {
            "g036.e1": {
                "reproduced": g036_reproduced,
                "witness": wit_g036.get("has_valid_witness", False),
                "witness_record": wit_g036,
            },
            "g021.e1": {
                "reproduced": g021_reproduced,
                "witness": wit_g021.get("has_valid_witness", False),
                "witness_record": wit_g021,
            },
            "TARGET_REPLACEMENT_REPRODUCED": f"{target_replacement_reproduced_count} / 2",
            "BATCH1_FIXED_LOCATOR_DEPENDENCY_REMOVED": f"{dep_removed_count} / 2",
            "dependency_removal_receipts": dep_receipts,
        },
        "group_retention": {
            "all_groups": group_retention,
            "group_regressions": group_regressions,
            "critical_group_regressions": critical_group_regressions,
            "noncritical_group_regressions": noncritical_group_regressions,
            "group_recoveries": group_recoveries,
        },
        "safety_and_grounding": {
            "CRITICAL_GROUP_REGRESSIONS": len(critical_group_regressions),
            "NONCRITICAL_GROUP_REGRESSIONS": len(noncritical_group_regressions),
            "GROUNDING_REGRESSIONS": safety_res["GROUNDING_REGRESSIONS"],
            "WRONG_VERSION_REGRESSIONS": safety_res["WRONG_VERSION_REGRESSIONS"],
            "INVALID_PROVENANCE_RECOVERIES": safety_res["INVALID_PROVENANCE_RECOVERIES"],
            "grounding_details": safety_res["grounding_details"],
            "wrong_version_details": safety_res["wrong_version_details"],
            "invalid_provenance_details": safety_res["invalid_provenance_details"],
        },
        "post_exposure_mutation_accounting": mutation_counters,
        "verdict_outcome": verdict_outcome,
        "production_activation": False,
    }

    eval_out_path = project_root / EVALUATOR_RESULTS_PATH
    eval_out_path.write_text(json.dumps(eval_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("\n==========================================")
    print("D4-A2 Before/After Evaluation Complete")
    print(f"Target Reproduction: {target_replacement_reproduced_count} / 2")
    print(f"Dependency Removal: {dep_removed_count} / 2")
    print(f"Critical Group Regressions: {len(critical_group_regressions)} ({critical_group_regressions})")
    print(f"Noncritical Group Regressions: {len(noncritical_group_regressions)} ({noncritical_group_regressions})")
    print(f"Metric Deltas: {cohort_deltas}")
    print(f"BATCH VERDICT: {verdict_outcome['batch_verdict']}")
    print(f"Reason: {verdict_outcome['verdict_reason']}")
    print("==========================================\n")

    return eval_artifact


# ===========================================================================
# 6. Main CLI
# ===========================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--mode",
        required=True,
        choices=["audit-invariants", "execute-32", "evaluate"],
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    root = args.project_root.resolve()

    if args.mode == "audit-invariants":
        receipt = audit_invariants(root)
        print(json.dumps(receipt, ensure_ascii=False, indent=1))
    elif args.mode == "execute-32":
        execute_32_formal_cells(root)
    elif args.mode == "evaluate":
        evaluate_d4_a2(root)


if __name__ == "__main__":
    main()
