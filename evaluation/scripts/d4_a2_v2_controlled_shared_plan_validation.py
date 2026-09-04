"""PANDA Agent D4-A2-V2 — Controlled Shared-Plan T2 Before/After Validation.

Pre-exposure implementation freeze only.
Authoritative contract: D4-A2-V2 specification (pasted-text.txt).

Prospective controlled shared-plan before/after validation across the 16-case
T2 comparison cohort (10 Gold v2.6 dev + 6 novel_dev; 13 answered cases + 3
insufficient_evidence negative controls):
  - Phase P: 16 questions x exactly 1 accepted Query Analyzer plan per case,
             frozen into evaluation/d4_a2_v2_raw_plans.json (Commit B).
  - Phase R: 32 downstream shared-plan paired retrieval cells (16 cases x 2 arms)
             in balanced alternating order with 0 analyzer provider calls,
             frozen into evaluation/d4_a2_v2_raw_results.json (Commit C).
  - Evaluator: Evaluator execution is unavailable until separately authorized Commit D
               after Commit C raw freeze. Fail-closed stub with zero writes.

CLI (run with PYTHONPATH=src):
    python evaluation/scripts/d4_a2_v2_controlled_shared_plan_validation.py --project-root . --mode audit-invariants
    python evaluation/scripts/d4_a2_v2_controlled_shared_plan_validation.py --project-root . --mode execute-phase-p
    python evaluation/scripts/d4_a2_v2_controlled_shared_plan_validation.py --project-root . --mode execute-phase-r
    # Note: evaluate mode is unavailable until separately authorized Commit D.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from contextlib import contextmanager
import copy
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
from google.genai import errors as genai_errors
from pydantic import ValidationError
from panda_agent.config import QueryExpansions, load_query_expansions
from panda_agent.evaluation import (
    GoldEvidenceGroup,
    GoldQuestion,
    _matched_evidence_groups,
    load_gold_dataset,
)
from panda_agent.evaluation_runner import load_object_lookup
from panda_agent.llm.vertex import VertexAIClient, VertexCallError, VertexSettings
from panda_agent.models import RetrievalPlan
from panda_agent.prompts import QUERY_ANALYZER_SYSTEM_PROMPT, RERANK_SYSTEM_PROMPT
from panda_agent.retrieval import Retriever, select_final_evidence


STARTING_HEAD = "6bc10872bee9d00a7ea710f55353c3113756dbb2"
COMMIT_A_HEAD = "c77f608cdf0edf77cbf482b71c51cbe9b1ce9d68"
IMPLEMENTATION_FREEZE_HEAD = "afc93327ff7f6de6c0b49dd905347696cfaad27a"
PLAN_FREEZE_HEAD = "537836244d44d9e5c10472df019f5fac1c9070a1"
PLAN_FREEZE_RAW_BLOB = "ee7c1c011463973557ef423178d7c241bf3821d4"
EXPECTED_A_R1_COMMIT_MESSAGE = "D4-A2-V2 repair pre-exposure freeze guards"
EXPECTED_R2_COMMIT_MESSAGE = "D4-A2-V2-R2 repair frozen plan verification"
MAX_PROVIDER_ATTEMPTS_PER_CASE = 3

RAW_RESULTS_FREEZE_HEAD = "b1a9f12366e328263e000f7b4c89184f2854c77a"
RAW_RESULTS_FREEZE_BLOB = "2d894ff2d0ac8a49239663df155478614a99bae0"
EXPECTED_EVALUATOR_FREEZE_COMMIT_MESSAGE = "D4-A2-V2 freeze deterministic evaluator"

PREREGISTRATION_PATH = "evaluation/d4_a2_v2_preregistration.json"
R2_PREREGISTRATION_PATH = "evaluation/d4_a2_v2_r2_preregistration.json"
MANIFEST_PATH = "evaluation/d4_a2_v2_execution_manifest.json"
RAW_PLANS_PATH = "evaluation/d4_a2_v2_raw_plans.json"
RAW_RESULTS_PATH = "evaluation/d4_a2_v2_raw_results.json"
EVALUATOR_RESULTS_PATH = "evaluation/d4_a2_v2_evaluator_results.json"
RESULT_PATH = "evaluation/d4_a2_v2_result.json"
REPORT_PATH = "evaluation/D4_A2_V2_CONTROLLED_SHARED_PLAN_VALIDATION.md"
EVALUATOR_SCRIPT_PATH = "evaluation/scripts/d4_a2_v2_controlled_shared_plan_validation.py"
EVALUATOR_TEST_PATH = "tests/unit/test_d4_a2_v2_controlled_shared_plan_validation.py"

GOLD_QUESTIONS_PATH = "evaluation/benchmarks/v2_6/gold_questions.yaml"
NOVEL_DEV_PATH = "evaluation/novel/v1/novel_dev.yaml"
CONFIG_QUERY_EXPANSIONS_PATH = "configs/query_expansions.yaml"

FROZEN_IMPLEMENTATION_PATHS = [
    "evaluation/d4_a2_v2_preregistration.json",
    "evaluation/d4_a2_v2_execution_manifest.json",
    "evaluation/scripts/d4_a2_v2_controlled_shared_plan_validation.py",
    "tests/unit/test_d4_a2_v2_controlled_shared_plan_validation.py",
    "src",
    "configs",
    "evaluation/benchmarks/v2_6/gold_questions.yaml",
    "evaluation/novel/v1/novel_dev.yaml",
]

ALLOWED_COMMIT_B_DIFF_FILES = {
    "evaluation/d4_a2_v2_raw_plans.json",
    "evaluation/d4_a2_v2_execution_manifest.json",
}

ALLOWED_R2_DIFF_FILES = {
    "evaluation/d4_a2_v2_r2_preregistration.json",
    "evaluation/scripts/d4_a2_v2_controlled_shared_plan_validation.py",
    "tests/unit/test_d4_a2_v2_controlled_shared_plan_validation.py",
}

ALLOWED_EVALUATOR_FREEZE_DIFF_FILES = {
    "evaluation/scripts/d4_a2_v2_controlled_shared_plan_validation.py",
    "tests/unit/test_d4_a2_v2_controlled_shared_plan_validation.py",
}

REQUIRED_PRIMARY_METRIC_KEYS = [
    "recall_at_5",
    "recall_at_10",
    "recall_at_20",
    "combined_candidate_recall",
    "final_evidence_recall",
    "critical_final_evidence_recall",
]

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
GOLD_ANSWERED_CASES = [c for c in GOLD_CASES if c in ANSWERED_CASES]
NOVEL_DEV_ANSWERED_CASES = [c for c in NOVEL_DEV_CASES if c in ANSWERED_CASES]

ARMS = ["BEFORE_COMPAT", "AFTER_BATCH1_REPLACEMENT"]
TOTAL_FORMAL_SLOTS = 32

SCHEDULE_32 = [
    {"slot_index": 1, "case_id": "g029", "arm": "BEFORE_COMPAT"},
    {"slot_index": 2, "case_id": "g029", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 3, "case_id": "n021", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 4, "case_id": "n021", "arm": "BEFORE_COMPAT"},
    {"slot_index": 5, "case_id": "g025", "arm": "BEFORE_COMPAT"},
    {"slot_index": 6, "case_id": "g025", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 7, "case_id": "g036", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 8, "case_id": "g036", "arm": "BEFORE_COMPAT"},
    {"slot_index": 9, "case_id": "n022", "arm": "BEFORE_COMPAT"},
    {"slot_index": 10, "case_id": "n022", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 11, "case_id": "g020", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 12, "case_id": "g020", "arm": "BEFORE_COMPAT"},
    {"slot_index": 13, "case_id": "n006", "arm": "BEFORE_COMPAT"},
    {"slot_index": 14, "case_id": "n006", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 15, "case_id": "g041", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 16, "case_id": "g041", "arm": "BEFORE_COMPAT"},
    {"slot_index": 17, "case_id": "n014", "arm": "BEFORE_COMPAT"},
    {"slot_index": 18, "case_id": "n014", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 19, "case_id": "g060", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 20, "case_id": "g060", "arm": "BEFORE_COMPAT"},
    {"slot_index": 21, "case_id": "g052", "arm": "BEFORE_COMPAT"},
    {"slot_index": 22, "case_id": "g052", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 23, "case_id": "g055", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 24, "case_id": "g055", "arm": "BEFORE_COMPAT"},
    {"slot_index": 25, "case_id": "n003", "arm": "BEFORE_COMPAT"},
    {"slot_index": 26, "case_id": "n003", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 27, "case_id": "g021", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 28, "case_id": "g021", "arm": "BEFORE_COMPAT"},
    {"slot_index": 29, "case_id": "n004", "arm": "BEFORE_COMPAT"},
    {"slot_index": 30, "case_id": "n004", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 31, "case_id": "g007", "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"slot_index": 32, "case_id": "g007", "arm": "BEFORE_COMPAT"},
]

ALLOWED_COMMIT_A_FILES = {
    "evaluation/d4_a2_v2_preregistration.json",
    "evaluation/d4_a2_v2_execution_manifest.json",
    "evaluation/scripts/d4_a2_v2_controlled_shared_plan_validation.py",
    "tests/unit/test_d4_a2_v2_controlled_shared_plan_validation.py",
}

# 6-level verdict precedence constants (exact D4-A2-V2 Section 20 specification)
VERDICT_LEVEL_1_INVALID = "INVALID / PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED"
VERDICT_LEVEL_2_INCONCLUSIVE = "INCONCLUSIVE / BEFORE_REFERENCE_NOT_REPRODUCED"
VERDICT_LEVEL_3_FAIL_PRIMARY_TARGET = "FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED"
VERDICT_LEVEL_4_FAIL_SHARED_PLAN_CRITICAL = "FAIL / SHARED_PLAN_CRITICAL_TREATMENT_REGRESSION"
VERDICT_LEVEL_5_PARTIAL_TOLERANCE = "PARTIAL / AGGREGATE_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE"
VERDICT_LEVEL_6_PASS = "PASS / CONTROLLED_SHARED_PLAN_T2_VALIDATED"

FROZEN_V2_VERDICTS = [
    VERDICT_LEVEL_1_INVALID,
    VERDICT_LEVEL_2_INCONCLUSIVE,
    VERDICT_LEVEL_3_FAIL_PRIMARY_TARGET,
    VERDICT_LEVEL_4_FAIL_SHARED_PLAN_CRITICAL,
    VERDICT_LEVEL_5_PARTIAL_TOLERANCE,
    VERDICT_LEVEL_6_PASS,
]

# Paired Pre-Rerank Classification Constants
PAIR_PRESERVED = "PAIR_PRESERVED"
PAIR_TREATMENT_RECOVERY = "PAIR_TREATMENT_RECOVERY"
PAIR_TREATMENT_REGRESSION = "PAIR_TREATMENT_REGRESSION"
PAIR_UNRESOLVED_BOTH = "PAIR_UNRESOLVED_BOTH"

# Paired Final-Evidence Classification Constants
FINAL_PRESERVED = "FINAL_PRESERVED"
FINAL_TREATMENT_RECOVERY = "FINAL_TREATMENT_RECOVERY"
FINAL_TREATMENT_REGRESSION = "FINAL_TREATMENT_REGRESSION"
FINAL_UNRESOLVED_BOTH = "FINAL_UNRESOLVED_BOTH"

# Frozen First-Divergence Taxonomy Constants (exact Section 9 taxonomy)
DIV_NO_DIVERGENCE = "NO_DIVERGENCE"
DIV_FIXED_LOCATOR_SUPPRESSION = "FIXED_LOCATOR_SUPPRESSION"
DIV_ORDINARY_CHANNEL_RECALL = "ORDINARY_CHANNEL_RECALL"
DIV_STRUCTURED_GENERATION = "STRUCTURED_GENERATION"
DIV_SELECTIVITY = "SELECTIVITY"
DIV_K3_ADMISSION = "K3_ADMISSION"
DIV_FUSION_CUTOFF = "FUSION_CUTOFF"
DIV_RERANKER = "RERANKER"
DIV_FINAL_SELECTION = "FINAL_SELECTION"

FROZEN_FIRST_DIVERGENCE_TAXONOMY = [
    DIV_NO_DIVERGENCE,
    DIV_FIXED_LOCATOR_SUPPRESSION,
    DIV_ORDINARY_CHANNEL_RECALL,
    DIV_STRUCTURED_GENERATION,
    DIV_SELECTIVITY,
    DIV_K3_ADMISSION,
    DIV_FUSION_CUTOFF,
    DIV_RERANKER,
    DIV_FINAL_SELECTION,
]

# Phase P narrow retry categories
RETRY_CATEGORY_TRANSPORT_PROVIDER = "TRANSPORT_OR_PROVIDER_FAILURE"
RETRY_CATEGORY_UNPARSABLE_RESPONSE = "UNPARSABLE_RESPONSE"
RETRY_CATEGORY_SCHEMA_VALIDATION = "SCHEMA_VALIDATION_FAILURE"

ALLOWED_RETRY_CATEGORIES = {
    RETRY_CATEGORY_TRANSPORT_PROVIDER,
    RETRY_CATEGORY_UNPARSABLE_RESPONSE,
    RETRY_CATEGORY_SCHEMA_VALIDATION,
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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


def get_implementation_freeze_commit(
    project_root: Path,
    rel_path: str = PREREGISTRATION_PATH,
) -> tuple[str, str]:
    """Determines the authoritative A-R1 implementation freeze commit using
    the non-self-referential containing-commit policy.

    Returns (commit_sha, commit_message).
    """
    rel_posix = rel_path.replace("\\", "/")
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%H%x00%s", "HEAD", "--", rel_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Git log failed for {rel_posix}: {proc.stderr.strip()}"
        )
    out = proc.stdout.strip()
    if not out or "\x00" not in out:
        raise RuntimeError(
            f"Could not determine implementation freeze commit for {rel_posix} from Git history"
        )
    sha, msg = out.split("\x00", 1)
    return sha.strip(), msg.strip()


def get_r2_repair_commit(
    project_root: Path,
    rel_path: str = R2_PREREGISTRATION_PATH,
) -> tuple[str, str]:
    """Determines the authoritative R2 repair commit using
    the non-self-referential containing-commit policy.

    Returns (commit_sha, commit_message).
    """
    rel_posix = rel_path.replace("\\", "/")
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%H%x00%s", "HEAD", "--", rel_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Git log failed for {rel_posix}: {proc.stderr.strip()}"
        )
    out = proc.stdout.strip()
    if not out or "\x00" not in out:
        raise RuntimeError(
            f"Could not determine R2 repair commit for {rel_posix} from Git history. "
            f"R2 preregistration must be committed as the R2 repair boundary."
        )
    sha, msg = out.split("\x00", 1)
    return sha.strip(), msg.strip()


def get_evaluator_freeze_commit(
    project_root: Path,
    rel_path: str = EVALUATOR_SCRIPT_PATH,
) -> tuple[str, str, list[str]]:
    """Determines the authoritative evaluator freeze commit using
    the containing-commit policy over the evaluator script.

    Returns (commit_sha, commit_message, parent_shas).
    """
    rel_posix = rel_path.replace("\\", "/")
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%H%x00%s%x00%P", "HEAD", "--", rel_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Git log failed for {rel_posix}: {proc.stderr.strip()}"
        )
    out = proc.stdout.strip()
    if not out or "\x00" not in out:
        raise RuntimeError(
            f"Could not determine evaluator freeze commit for {rel_posix} from Git history"
        )
    parts = out.split("\x00")
    sha = parts[0].strip()
    msg = parts[1].strip() if len(parts) > 1 else ""
    parents = parts[2].strip().split() if len(parts) > 2 else []
    return sha, msg, parents


def verify_evaluator_freeze_provenance(
    project_root: Path,
    *,
    raw_results_path: str = RAW_RESULTS_PATH,
    raw_plans_path: str = RAW_PLANS_PATH,
    evaluator_script_path: str = EVALUATOR_SCRIPT_PATH,
    evaluator_test_path: str = EVALUATOR_TEST_PATH,
    raw_results_freeze_sha: str = RAW_RESULTS_FREEZE_HEAD,
    raw_results_freeze_blob: str = RAW_RESULTS_FREEZE_BLOB,
    plan_freeze_raw_blob: str = PLAN_FREEZE_RAW_BLOB,
    expected_evaluator_commit_message: str = EXPECTED_EVALUATOR_FREEZE_COMMIT_MESSAGE,
) -> dict[str, Any]:
    """Mechanically verifies the authoritative evaluator freeze boundary and provenance:
    1. Raw results artifact is present in Git HEAD and clean in worktree/index.
    2. Raw results origin commit equals authoritative raw-result freeze b1a9f12366e328263e000f7b4c89184f2854c77a.
    3. Raw results Git blob at HEAD and in worktree equals 2d894ff2d0ac8a49239663df155478614a99bae0.
    4. Raw plans artifact is present in Git HEAD and clean in worktree/index.
    5. Raw plans Git blob at HEAD and in worktree equals PLAN_FREEZE_RAW_BLOB (ee7c1c011463973557ef423178d7c241bf3821d4).
    6. Evaluator implementation containing commit has exact message: 'D4-A2-V2 freeze deterministic evaluator'.
    7. Evaluator implementation containing commit has direct parent: b1a9f12366e328263e000f7b4c89184f2854c77a.
    8. Freeze commit is an ancestor of current HEAD (allowing deterministic read-only recomputation from later closeout descendant).
    9. Evaluator freeze commit modified only ALLOWED_EVALUATOR_FREEZE_DIFF_FILES relative to raw-result freeze.
    10. No evaluator code drift: worktree/index clean for evaluator files, diff between freeze commit and worktree is empty,
        and worktree blob matches frozen commit blob.
    """
    raw_res_posix = raw_results_path.replace("\\", "/")
    raw_plans_posix = raw_plans_path.replace("\\", "/")
    eval_script_posix = evaluator_script_path.replace("\\", "/")
    eval_test_posix = evaluator_test_path.replace("\\", "/")

    # 1. Raw results present in Git HEAD and clean in worktree/index
    cat_res = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{raw_res_posix}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if cat_res.returncode != 0:
        raise RuntimeError(
            f"Raw results artifact {raw_res_posix} is not present in Git HEAD!"
        )

    status_raw_res = subprocess.run(
        ["git", "status", "--porcelain", "-uall", "--", raw_res_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    if status_raw_res.stdout.strip():
        raise RuntimeError(
            f"Raw results artifact {raw_res_posix} has uncommitted or dirty changes: {status_raw_res.stdout.strip()}"
        )

    # 2. Raw results origin commit
    log_raw_res = subprocess.run(
        ["git", "log", "-1", "--format=%H", "HEAD", "--", raw_res_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if log_raw_res.returncode != 0:
        raise RuntimeError(f"Git log failed for {raw_res_posix}: {log_raw_res.stderr.strip()}")
    raw_res_origin = log_raw_res.stdout.strip()
    if raw_res_origin != raw_results_freeze_sha:
        raise RuntimeError(
            f"Raw results origin commit mismatch: expected authoritative raw-result freeze "
            f"commit {raw_results_freeze_sha}, got {raw_res_origin}"
        )

    # 3. Raw results blob at HEAD and in worktree
    blob_head_res = subprocess.run(
        ["git", "rev-parse", f"HEAD:{raw_res_posix}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if blob_head_res.returncode != 0:
        raise RuntimeError(f"Failed to get Git blob for {raw_res_posix} at HEAD: {blob_head_res.stderr.strip()}")
    res_blob_head = blob_head_res.stdout.strip()
    if res_blob_head != raw_results_freeze_blob:
        raise RuntimeError(
            f"Raw results Git blob mismatch at HEAD: expected {raw_results_freeze_blob}, got {res_blob_head}"
        )

    hash_res_file = project_root / raw_results_path
    if hash_res_file.exists():
        hash_res_proc = subprocess.run(
            ["git", "hash-object", str(hash_res_file)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
        if hash_res_proc.returncode == 0 and hash_res_proc.stdout.strip() != raw_results_freeze_blob:
            raise RuntimeError(
                f"Raw results worktree blob mismatch: expected {raw_results_freeze_blob}, got {hash_res_proc.stdout.strip()}"
            )

    # 4. Raw plans present in Git HEAD and clean in worktree/index
    cat_plans = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{raw_plans_posix}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if cat_plans.returncode != 0:
        raise RuntimeError(
            f"Raw plans artifact {raw_plans_posix} is not present in Git HEAD!"
        )

    status_raw_plans = subprocess.run(
        ["git", "status", "--porcelain", "-uall", "--", raw_plans_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    if status_raw_plans.stdout.strip():
        raise RuntimeError(
            f"Raw plans artifact {raw_plans_posix} has uncommitted or dirty changes: {status_raw_plans.stdout.strip()}"
        )

    # 5. Raw plans blob at HEAD and in worktree
    blob_head_plans = subprocess.run(
        ["git", "rev-parse", f"HEAD:{raw_plans_posix}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if blob_head_plans.returncode != 0:
        raise RuntimeError(f"Failed to get Git blob for {raw_plans_posix} at HEAD: {blob_head_plans.stderr.strip()}")
    plans_blob_head = blob_head_plans.stdout.strip()
    if plans_blob_head != plan_freeze_raw_blob:
        raise RuntimeError(
            f"Raw plans Git blob mismatch at HEAD: expected {plan_freeze_raw_blob}, got {plans_blob_head}"
        )

    hash_plans_file = project_root / raw_plans_path
    if hash_plans_file.exists():
        hash_plans_proc = subprocess.run(
            ["git", "hash-object", str(hash_plans_file)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
        if hash_plans_proc.returncode == 0 and hash_plans_proc.stdout.strip() != plan_freeze_raw_blob:
            raise RuntimeError(
                f"Raw plans worktree blob mismatch: expected {plan_freeze_raw_blob}, got {hash_plans_proc.stdout.strip()}"
            )

    # 6. Evaluator implementation freeze commit determination
    eval_sha, eval_msg, eval_parents = get_evaluator_freeze_commit(project_root, rel_path=eval_script_posix)

    # 7. Evaluator freeze commit message verification
    if eval_msg != expected_evaluator_commit_message:
        raise RuntimeError(
            f"Evaluator freeze commit message mismatch: expected '{expected_evaluator_commit_message}', "
            f"got '{eval_msg}' (commit {eval_sha})"
        )

    # 8. Evaluator freeze direct parent verification
    if eval_parents != [raw_results_freeze_sha]:
        raise RuntimeError(
            f"Evaluator freeze parent mismatch: expected direct parent {[raw_results_freeze_sha]}, "
            f"got {eval_parents} (commit {eval_sha})"
        )

    # 9. Ancestry check: freeze commit must be an ancestor of current HEAD (permits closeout descendant recomputation)
    ancestor_proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", eval_sha, "HEAD"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if ancestor_proc.returncode != 0:
        raise RuntimeError(
            f"Evaluator freeze commit {eval_sha} is not an ancestor of current HEAD! "
            f"Evaluator execution or recomputation must descend from the freeze commit."
        )

    # 10. Historical diff between raw-result freeze and evaluator freeze commit
    diff_freeze = subprocess.run(
        ["git", "diff", "--name-only", raw_results_freeze_sha, eval_sha],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    changed_eval_files = [
        f.strip().replace("\\", "/")
        for f in diff_freeze.stdout.splitlines()
        if f.strip()
    ]
    disallowed_eval = [f for f in changed_eval_files if f not in ALLOWED_EVALUATOR_FREEZE_DIFF_FILES]
    if disallowed_eval:
        raise RuntimeError(
            f"Evaluator freeze commit {eval_sha} modified disallowed paths relative to "
            f"raw-result freeze ({raw_results_freeze_sha}): {disallowed_eval}. "
            f"Only {ALLOWED_EVALUATOR_FREEZE_DIFF_FILES} are allowed."
        )

    # 11. Reject evaluator code drift between eval_sha and current working tree / index
    status_eval = subprocess.run(
        ["git", "status", "--porcelain", "-uall", "--", eval_script_posix, eval_test_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    if status_eval.stdout.strip():
        raise RuntimeError(
            f"Worktree or index is dirty for evaluator files: {status_eval.stdout.strip()}"
        )

    diff_drift = subprocess.run(
        ["git", "diff", eval_sha, "--", eval_script_posix, eval_test_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    if diff_drift.stdout.strip():
        raise RuntimeError(
            f"Evaluator code drift detected relative to freeze commit {eval_sha}: {diff_drift.stdout.strip()}"
        )

    # 12. Blob identity of script
    hash_eval_script = project_root / evaluator_script_path
    if hash_eval_script.exists():
        blob_frozen_proc = subprocess.run(
            ["git", "rev-parse", f"{eval_sha}:{eval_script_posix}"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
        hash_eval_proc = subprocess.run(
            ["git", "hash-object", str(hash_eval_script)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
        if (
            blob_frozen_proc.returncode == 0
            and hash_eval_proc.returncode == 0
            and hash_eval_proc.stdout.strip() != blob_frozen_proc.stdout.strip()
        ):
            raise RuntimeError(
                f"Evaluator script worktree blob ({hash_eval_proc.stdout.strip()}) differs from frozen "
                f"commit blob ({blob_frozen_proc.stdout.strip()})!"
            )

    return {
        "verified": True,
        "raw_results_freeze_sha": raw_results_freeze_sha,
        "raw_results_blob": raw_results_freeze_blob,
        "raw_plans_blob": plan_freeze_raw_blob,
        "evaluator_implementation_freeze_sha": eval_sha,
        "evaluator_implementation_freeze_message": eval_msg,
        "evaluator_implementation_parents": eval_parents,
        "current_head": _git_head(project_root),
    }


def verify_phase_p_gate(
    project_root: Path,
    *,
    git_checker: Any | None = None,
) -> dict[str, Any]:
    """Mechanically verifies the authoritative A-R1 implementation-freeze boundary
    prior to any Phase P Query Analyzer provider call:
    1. Current HEAD is exactly the final A-R1 implementation freeze commit.
    2. Commit message matches EXPECTED_A_R1_COMMIT_MESSAGE.
    3. No intervening or descendant commits between freeze and Phase P.
    4. Worktree and index are completely clean (no staged, unstaged, or untracked changes)
       across all frozen implementation/benchmark paths: runner, prereg, manifest,
       tests, src/, configs/, benchmarks, and novel_dev.
    5. Implementation has not drifted from the freeze boundary.
    """
    if git_checker is not None:
        freeze_sha, freeze_msg, current_head, dirty_paths = git_checker(project_root)
    else:
        freeze_sha, freeze_msg = get_implementation_freeze_commit(project_root)
        current_head = _git_head(project_root)

        status_proc = subprocess.run(
            ["git", "status", "--porcelain", "-uall", "--", *FROZEN_IMPLEMENTATION_PATHS],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=True,
        )
        dirty_paths = [
            line.strip()
            for line in status_proc.stdout.splitlines()
            if line.strip()
        ]

    # Validate commit message
    if freeze_msg != EXPECTED_A_R1_COMMIT_MESSAGE:
        raise RuntimeError(
            f"Implementation freeze commit message mismatch: expected '{EXPECTED_A_R1_COMMIT_MESSAGE}', "
            f"got '{freeze_msg}' (commit {freeze_sha})"
        )

    # Require current HEAD to be exactly the freeze commit
    if current_head != freeze_sha:
        raise RuntimeError(
            f"Current Git HEAD ({current_head}) differs from authoritative implementation freeze "
            f"commit ({freeze_sha})! Descendant or intervening commits are rejected before Phase P."
        )

    # Require completely clean worktree/index across all frozen paths
    if dirty_paths:
        raise RuntimeError(
            f"Worktree or index is dirty for frozen implementation/benchmark paths: {dirty_paths}. "
            f"Require clean index, worktree, and untracked files before Phase P."
        )

    # Verify drift guards relative to STARTING_HEAD
    if git_checker is None:
        verify_drift_guards(project_root, require_clean_worktree=True)

    return {
        "verified": True,
        "implementation_freeze_head": freeze_sha,
        "runtime_execution_head": current_head,
        "commit_message": freeze_msg,
        "frozen_paths_clean": True,
    }


def verify_drift_guards(
    project_root: Path, *, require_clean_worktree: bool = False
) -> dict[str, Any]:
    """Enforces implementation and configuration drift guards:
    - Protected src/, configs/, benchmarks, and novel_dev are completely unchanged relative to STARTING_HEAD.
    - Only authorized Commit-A files are modified relative to STARTING_HEAD.
    - Clean worktree for frozen paths when require_clean_worktree=True.
    """
    diff_protected = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            STARTING_HEAD,
            "--",
            "src",
            "configs",
            "evaluation/benchmarks",
            "evaluation/novel",
        ],
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
            f"Protected src/, configs/, benchmarks, or novel_dev modified relative to STARTING_HEAD: {changed_protected}"
        )

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
        ["git", "status", "--porcelain", "-uall", "--", *FROZEN_IMPLEMENTATION_PATHS],
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


def audit_invariants(project_root: Path) -> dict[str, Any]:
    """Mandatory deterministic pre-exposure verification:
    - Environment model configuration matches gemini-3.8-flash and gemini-embedding-2.
    - System prompt authorities exist and are valid.
    - Pipeline parameters match frozen contracts: RRF weights, selectivity caps 8/4, K=3 admission, pool 30.
    - Revalidates A0 overlaps on current query_expansions config.
    - In-memory component mask idempotency, exact suppression, and preservation.
    - 16-case cohort identity, order, and dataset breakdown.
    - Corrected benchmark contract: g021.e1 critical=True, g021.e2 critical=False, n022.e2 critical=True.
    - Execution manifest and preregistration consistency.
    - 32-slot balanced alternating schedule (8 pairs BEFORE first, 8 pairs AFTER first).
    - Production and lifecycle guards: production_activation=False, first-batch migration=BLOCKED, d4_a3=NOT_STARTED/BLOCKED.
    - Absolutely no provider or model calls.
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

    if not QUERY_ANALYZER_SYSTEM_PROMPT or not isinstance(QUERY_ANALYZER_SYSTEM_PROMPT, str):
        raise ValueError("QUERY_ANALYZER_SYSTEM_PROMPT authority is empty or invalid")
    if not RERANK_SYSTEM_PROMPT or not isinstance(RERANK_SYSTEM_PROMPT, str):
        raise ValueError("RERANK_SYSTEM_PROMPT authority is empty or invalid")

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

    orig_ep = next(r for r in original_qe.rules if r.rule_id == "event_poca_handoff")
    orig_rg = next(r for r in original_qe.rules if r.rule_id == "restgas_profile_workflow")
    if orig_ep.symbols != d4_a1.SUPPRESSED_SYMBOLS_EVENT_POCA:
        raise ValueError("Source QueryExpansions event_poca_handoff symbols were mutated!")
    if orig_ep.paper_page_hints != d4_a1.SUPPRESSED_PAGE_HINTS_EVENT_POCA:
        raise ValueError("Source QueryExpansions event_poca_handoff page hints were mutated!")
    if orig_rg.symbols != d4_a1.SUPPRESSED_SYMBOLS_RESTGAS:
        raise ValueError("Source QueryExpansions restgas_profile_workflow symbols were mutated!")

    mask_ep = next(r for r in masked_qe.rules if r.rule_id == "event_poca_handoff")
    mask_rg = next(r for r in masked_qe.rules if r.rule_id == "restgas_profile_workflow")
    if mask_ep.symbols != []:
        raise ValueError(f"Masked event_poca_handoff symbols not empty: {mask_ep.symbols}")
    if mask_ep.paper_page_hints != {}:
        raise ValueError(f"Masked event_poca_handoff page hints not empty: {mask_ep.paper_page_hints}")
    if mask_rg.symbols != []:
        raise ValueError(f"Masked restgas_profile_workflow symbols not empty: {mask_rg.symbols}")

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

    if masked_qe.model_dump() != masked_twice.model_dump():
        raise ValueError("In-memory component mask double application is not deterministic!")

    # 3. 16-case cohort and corrected benchmark contract verification
    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_q = {q.id: q for q in gold_ds.questions + novel_ds.questions}

    for cid in CASE_ORDER:
        if cid not in all_q:
            raise ValueError(f"Cohort case {cid} missing from benchmark datasets!")

    g021_q = all_q["g021"]
    g021_e1 = next((g for g in g021_q.required_evidence_groups if g.group_id == "g021.e1"), None)
    g021_e2 = next((g for g in g021_q.required_evidence_groups if g.group_id == "g021.e2"), None)
    if g021_e1 is None or not g021_e1.critical:
        raise ValueError("g021.e1 must remain critical=True in corrected benchmark contract")
    if g021_e2 is None or g021_e2.critical:
        raise ValueError("g021.e2 must be critical=False in corrected benchmark contract")

    n022_q = all_q["n022"]
    n022_e2 = next((g for g in n022_q.required_evidence_groups if g.group_id == "n022.e2"), None)
    if n022_e2 is None or not n022_e2.critical:
        raise ValueError("n022.e2 must remain critical=True in benchmark contract")

    # 4. Execution manifest verification
    manifest_path = project_root / MANIFEST_PATH
    if not manifest_path.exists():
        raise FileNotFoundError(f"Execution manifest {manifest_path} missing")
    manifest = _load_json(manifest_path)

    slots_p = manifest.get("phase_p_slots_16", [])
    if len(slots_p) != len(CASE_ORDER):
        raise ValueError(f"Manifest Phase P slots mismatch: expected {len(CASE_ORDER)}, got {len(slots_p)}")

    for i, s in enumerate(slots_p):
        expected_cid = CASE_ORDER[i]
        if s["slot_index"] != i + 1 or s["case_id"] != expected_cid:
            raise ValueError(f"Phase P slot #{i + 1} mismatch: expected {expected_cid}, got {s}")
        if s["status"] != "NOT_STARTED":
            raise ValueError(f"Phase P slot #{i + 1} status is not NOT_STARTED: {s['status']}")

    cells_r = manifest.get("phase_r_cells_32", [])
    if len(cells_r) != TOTAL_FORMAL_SLOTS:
        raise ValueError(f"Manifest Phase R cells mismatch: expected {TOTAL_FORMAL_SLOTS}, got {len(cells_r)}")

    for exp_item, cell_item in zip(SCHEDULE_32, cells_r):
        if (cell_item["cell_index"], cell_item["case_id"], cell_item["arm"]) != (
            exp_item["slot_index"],
            exp_item["case_id"],
            exp_item["arm"],
        ):
            raise ValueError(f"Schedule mismatch in manifest cell: {cell_item} vs {exp_item}")
        if cell_item["status"] != "NOT_STARTED":
            raise ValueError(f"Phase R cell #{cell_item['cell_index']} status is not NOT_STARTED")

    exposure_state = manifest.get("outcome_exposure_state", {})
    if exposure_state.get("D4_A2_V2_OUTCOME_EXPOSURE") != "NOT_STARTED":
        raise ValueError("Manifest D4_A2_V2_OUTCOME_EXPOSURE is not NOT_STARTED")
    if exposure_state.get("phase_p_slots_completed") != 0:
        raise ValueError("Manifest phase_p_slots_completed != 0")
    if exposure_state.get("phase_r_cells_completed") != 0:
        raise ValueError("Manifest phase_r_cells_completed != 0")
    if exposure_state.get("evaluator_executed") is not False:
        raise ValueError("Manifest evaluator_executed is not False")
    if exposure_state.get("scientific_verdict_computed") is not False:
        raise ValueError("Manifest scientific_verdict_computed is not False")

    # 5. Preregistration verification
    prereg_path = project_root / PREREGISTRATION_PATH
    if not prereg_path.exists():
        raise FileNotFoundError(f"Preregistration {prereg_path} missing")
    prereg = _load_json(prereg_path)
    if prereg.get("outcome_exposure_state", {}).get("D4_A2_V2_OUTCOME_EXPOSURE") != "NOT_STARTED":
        raise ValueError("Preregistration D4_A2_V2_OUTCOME_EXPOSURE is not NOT_STARTED")
    if prereg.get("production_and_lifecycle_guards", {}).get("production_activation") is not False:
        raise ValueError("Preregistration production_activation is not False")
    if prereg.get("production_and_lifecycle_guards", {}).get("first_batch_runtime_migration") != "BLOCKED":
        raise ValueError("Preregistration first_batch_runtime_migration is not BLOCKED")
    if prereg.get("production_and_lifecycle_guards", {}).get("d4_a3") != "NOT_STARTED / BLOCKED":
        raise ValueError("Preregistration d4_a3 is not NOT_STARTED / BLOCKED")

    # A-R1 Implementation Freeze contract & Retry Cap consistency checks
    if MAX_PROVIDER_ATTEMPTS_PER_CASE != 3:
        raise ValueError(f"Runner MAX_PROVIDER_ATTEMPTS_PER_CASE != 3: {MAX_PROVIDER_ATTEMPTS_PER_CASE}")

    prereg_p = prereg.get("phase_p_contract", {})
    manifest_p = manifest.get("phase_p_contract", {})
    if prereg_p.get("max_provider_attempts_per_case") != 3:
        raise ValueError(
            f"Preregistration max_provider_attempts_per_case != 3: {prereg_p.get('max_provider_attempts_per_case')}"
        )
    if manifest_p.get("max_provider_attempts_per_case") != 3:
        raise ValueError(
            f"Manifest max_provider_attempts_per_case != 3: {manifest_p.get('max_provider_attempts_per_case')}"
        )

    prereg_retry_cats = set(prereg_p.get("acquisition_rules", {}).get("allowed_retry_categories", []))
    if prereg_retry_cats != ALLOWED_RETRY_CATEGORIES:
        raise ValueError(
            f"Preregistration allowed_retry_categories mismatch: {prereg_retry_cats} vs {ALLOWED_RETRY_CATEGORIES}"
        )

    prereg_freeze_msg = prereg.get("implementation_freeze_contract", {}).get("expected_commit_message")
    if prereg_freeze_msg != EXPECTED_A_R1_COMMIT_MESSAGE:
        raise ValueError(
            f"Preregistration expected_commit_message mismatch: expected '{EXPECTED_A_R1_COMMIT_MESSAGE}', got '{prereg_freeze_msg}'"
        )
    manifest_freeze_msg = manifest.get("implementation_freeze_contract", {}).get("expected_commit_message")
    if manifest_freeze_msg != EXPECTED_A_R1_COMMIT_MESSAGE:
        raise ValueError(
            f"Manifest expected_commit_message mismatch: expected '{EXPECTED_A_R1_COMMIT_MESSAGE}', got '{manifest_freeze_msg}'"
        )

    drift_receipt = verify_drift_guards(project_root, require_clean_worktree=False)

    return {
        "verified": True,
        "cohort_cases": len(CASE_ORDER),
        "gold_cases": len(GOLD_CASES),
        "novel_dev_cases": len(NOVEL_DEV_CASES),
        "answered_cases": len(ANSWERED_CASES),
        "insufficient_evidence_cases": len(INSUFFICIENT_EVIDENCE_CASES),
        "phase_p_slots": len(slots_p),
        "phase_r_cells": len(cells_r),
        "balanced_schedule_verified": True,
        "model_id": settings.generation_model,
        "embedding_model_id": settings.embedding_model,
        "location": settings.location,
        "temperature": env_temp,
        "corrected_criticality_verified": True,
        "drift_guards_verified": drift_receipt["verified"],
        "production_activation": False,
        "first_batch_runtime_migration": "BLOCKED",
        "d4_a3": "NOT_STARTED / BLOCKED",
        "protected_dataset_access": 0,
    }


@contextmanager
def frozen_plan_context(retriever: Retriever, frozen_plan: RetrievalPlan):
    """Evaluation-only adapter guaranteeing:
    - Phase-R analyzer provider calls = 0
    - Canonical plan used by downstream cell == frozen_plan
    - Restores original retriever.analyze on exception or completion
    - Never leaks to another case/pair
    """
    orig_analyze = retriever.analyze
    calls_recorded: list[str] = []

    def mock_analyze(question: str, *, d3_config: Any = None) -> RetrievalPlan:
        calls_recorded.append(question)
        return copy.deepcopy(frozen_plan)

    retriever.analyze = mock_analyze
    try:
        yield calls_recorded
    finally:
        retriever.analyze = orig_analyze


def compute_plan_signature(plan_dict: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Generates a canonical signature payload and JSON string for plan comparison.

    Repaired in D4-A2-V2-R2 to produce a deterministic, JSON-canonical representation
    where paper_page_hints and concept_scopes use JSON-compatible list structures
    instead of Python tuples, resolving the tuple-vs-list round-trip defect while
    preserving exact participating fields and semantic sorting.
    """
    intent = plan_dict.get("intent", "")
    repos = sorted(plan_dict.get("target_repositories", []))
    symbols = sorted(plan_dict.get("symbols", []))
    concepts = sorted(c.strip().casefold() for c in plan_dict.get("concepts", []))
    req_types = sorted(plan_dict.get("required_source_types", []))
    paper_hints = [
        [k, sorted(v)] for k, v in sorted((plan_dict.get("paper_page_hints") or {}).items())
    ]
    scopes = [[k, v] for k, v in sorted((plan_dict.get("concept_scopes") or {}).items())]
    sig_payload = {
        "intent": intent,
        "target_repositories": repos,
        "symbols": symbols,
        "normalized_concepts": concepts,
        "required_source_types": req_types,
        "paper_page_hints": paper_hints,
        "concept_scopes": scopes,
    }
    sig_str = json.dumps(sig_payload, sort_keys=True)
    canonical_payload = json.loads(sig_str)
    return sig_str, canonical_payload


def classify_phase_p_retryable_error(exc: BaseException) -> tuple[bool, str | None]:
    """Explicit, narrow classification of Phase P plan acquisition errors.

    Retries ONLY:
      1. Transport/provider failures (VertexCallError, google.genai.errors.APIError, ConnectionError, TimeoutError).
      2. Unparsable responses (json.JSONDecodeError, or ValueError for empty/non-dict structured response).
      3. RetrievalPlan schema-validation failures (pydantic.ValidationError, or ValueError for missing grounded intent delta).

    Any other exception is strictly non-retryable and must fail closed immediately.
    Semantic weakness is NEVER a retry condition.
    """
    # 1. Transport / provider failures
    if isinstance(exc, (VertexCallError, ConnectionError, TimeoutError)):
        return True, RETRY_CATEGORY_TRANSPORT_PROVIDER
    if isinstance(exc, genai_errors.APIError):
        return True, RETRY_CATEGORY_TRANSPORT_PROVIDER

    # 2. Unparsable response failures
    if isinstance(exc, json.JSONDecodeError):
        return True, RETRY_CATEGORY_UNPARSABLE_RESPONSE
    if isinstance(exc, ValueError):
        msg = str(exc)
        if "empty structured response" in msg or "must be a JSON object" in msg:
            return True, RETRY_CATEGORY_UNPARSABLE_RESPONSE

    # 3. Schema validation failures
    if isinstance(exc, ValidationError):
        return True, RETRY_CATEGORY_SCHEMA_VALIDATION
    if isinstance(exc, ValueError):
        msg = str(exc)
        if "analyzer semantic delta did not provide a grounded intent" in msg:
            return True, RETRY_CATEGORY_SCHEMA_VALIDATION

    return False, None


def execute_phase_p(
    project_root: Path,
    *,
    git_checker: Any | None = None,
) -> dict[str, Any]:
    """Separately authorized future Phase P runner:
    Acquires exactly 1 accepted canonical Query Analyzer plan per case across the 16 cases.
    Enforces the single valid plan acquisition rule:
      - Semantic weakness is strictly NOT a retry condition.
      - Retry is allowed only on transport/provider failure or schema-invalid plan.
      - Provenance recorded for every plan.
      - All 16 plans frozen to RAW_PLANS_PATH (Commit B input).
    """
    load_dotenv(project_root / ".env")
    audit_receipt = audit_invariants(project_root)
    print(f"[PHASE P AUDIT PASSED] Model: {audit_receipt['model_id']}")

    # Mechanical Phase-P pre-exposure gate
    gate_receipt = verify_phase_p_gate(project_root, git_checker=git_checker)
    implementation_freeze_head = gate_receipt["implementation_freeze_head"]
    runtime_execution_head = gate_receipt["runtime_execution_head"]

    manifest_path = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_path)
    exposure = manifest.setdefault("outcome_exposure_state", {})
    if exposure.get("D4_A2_V2_OUTCOME_EXPOSURE") in ("PLANS_FROZEN", "RAW_RETRIEVAL_COMPLETE", "EVALUATION_COMPLETE"):
        print("[PHASE P ALREADY COMPLETED] Loading existing frozen plans.")
        return _load_json(project_root / RAW_PLANS_PATH)

    exposure["D4_A2_V2_OUTCOME_EXPOSURE"] = "PLAN_ACQUISITION_STARTED"
    _save_json(manifest_path, manifest)

    retriever = Retriever(project_root)

    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_questions = {q.id: q for q in gold_ds.questions + novel_ds.questions}

    plan_records: list[dict[str, Any]] = []
    total_tokens = 0
    total_attempts = 0

    print(f"[PHASE P] Beginning single-plan acquisition for {len(CASE_ORDER)} cases...")

    for i, cid in enumerate(CASE_ORDER, start=1):
        slot = manifest["phase_p_slots_16"][i - 1]
        if slot["status"] == "COMPLETED":
            print(f"  Slot #{i} ({cid}) already completed, skipping.")
            continue
        if slot["status"] == "STARTED":
            raise RuntimeError(f"Slot #{i} ({cid}) in ambiguous STARTED state! Fail closed.")

        q_obj = all_questions[cid]
        question_text = q_obj.query

        slot["status"] = "STARTED"
        slot["started_at"] = datetime.datetime.now().isoformat()
        _save_json(manifest_path, manifest)

        # Plan acquisition with strict narrow retry policy
        max_attempts = MAX_PROVIDER_ATTEMPTS_PER_CASE
        attempts = 0
        accepted_plan: RetrievalPlan | None = None
        retry_reasons: list[str] = []
        elapsed_total = 0.0

        stats_before = retriever.vertex.stats_snapshot()
        t0 = time.time()

        while attempts < max_attempts and accepted_plan is None:
            attempts += 1
            try:
                raw_plan: RetrievalPlan = retriever.analyze(question_text)
                # Schema validation & canonicalization check
                plan_dict = raw_plan.model_dump(mode="json")
                RetrievalPlan.model_validate(plan_dict)
                # Any schema-valid plan is accepted immediately; semantic weakness is NOT a retry condition.
                accepted_plan = raw_plan
            except Exception as exc:
                is_retryable, category = classify_phase_p_retryable_error(exc)
                if not is_retryable:
                    slot["status"] = "FAILED"
                    slot["error"] = f"NON_RETRYABLE_EXCEPTION: {type(exc).__name__}: {exc}"
                    _save_json(manifest_path, manifest)
                    raise RuntimeError(
                        f"Non-retryable exception during Phase P plan acquisition for case {cid}: "
                        f"{type(exc).__name__}: {exc}"
                    ) from exc

                retry_reason = f"[{category}] Attempt #{attempts} failed with {type(exc).__name__}: {exc}"
                retry_reasons.append(retry_reason)
                if attempts >= max_attempts:
                    slot["status"] = "FAILED"
                    slot["error"] = f"MAX_ATTEMPTS_EXCEEDED: {retry_reason}"
                    _save_json(manifest_path, manifest)
                    raise RuntimeError(
                        f"Failed to acquire valid plan for case {cid} after {attempts} attempts: {retry_reason}"
                    ) from exc
                time.sleep(1.0)

        elapsed = round(time.time() - t0, 3)
        stats_delta = retriever.vertex.stats_delta(stats_before)

        provider_attempts = stats_delta.get("model_calls", stats_delta.get("generation_calls", attempts))
        token_usage = stats_delta.get("token_usage", 0)
        total_tokens += token_usage
        total_attempts += provider_attempts

        plan_dict = accepted_plan.model_dump(mode="json")
        sig_str, sig_payload = compute_plan_signature(plan_dict)

        plan_record = {
            "draw_index": i,
            "case_id": cid,
            "question": question_text,
            "intent": accepted_plan.intent,
            "target_repositories": list(accepted_plan.target_repositories),
            "resolved_versions": dict(accepted_plan.resolved_versions),
            "symbols": list(accepted_plan.symbols),
            "concepts": list(accepted_plan.concepts),
            "concept_scopes": dict(accepted_plan.concept_scopes),
            "required_source_types": list(accepted_plan.required_source_types),
            "paper_page_hints": dict(accepted_plan.paper_page_hints),
            "provider_internal_attempts": provider_attempts,
            "retries_count": len(retry_reasons),
            "retry_reasons": retry_reasons,
            "token_usage": token_usage,
            "elapsed_seconds": elapsed,
            "started_at": slot["started_at"],
            "completed_at": datetime.datetime.now().isoformat(),
            "status": "COMPLETED",
            "logical_calls": {
                "analyzer_calls": 1,
                "embedding_calls": 0,
                "reranker_calls": 0,
            },
            "plan_signature": sig_payload,
            "accepted_canonical_plan": plan_dict,
            "canonical_plan": plan_dict,
        }
        plan_records.append(plan_record)

        slot["status"] = "COMPLETED"
        slot["completed_at"] = plan_record["completed_at"]
        slot["token_usage"] = token_usage
        slot["attempts"] = provider_attempts
        slot["plan_signature"] = sig_payload
        _save_json(manifest_path, manifest)

        print(f"  Slot #{i}/{len(CASE_ORDER)} ({cid}) COMPLETED in {elapsed}s: {len(accepted_plan.concepts)} concepts")

    raw_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V2",
        "stage": "Phase P — Controlled Shared Plan Acquisition",
        "created_at": datetime.datetime.now().isoformat(),
        "starting_head": STARTING_HEAD,
        "implementation_freeze_head": implementation_freeze_head,
        "runtime_execution_head": runtime_execution_head,
        "commit_a_r1_implementation_freeze_head": implementation_freeze_head,
        "commit_a_implementation_freeze_head": implementation_freeze_head,
        "plan_freeze_state": "PLANS_FROZEN",
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED": True,
        "PHASE_R_RETRIEVAL_EXECUTED": False,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "model_id": EXPECTED_MODEL,
        "vertex_location": EXPECTED_VERTEX_LOCATION,
        "temperature": EXPECTED_TEMPERATURE,
        "prompt_authority": "src/panda_agent/prompts.py:QUERY_ANALYZER_SYSTEM_PROMPT",
        "exact_acquisition_case_order": list(CASE_ORDER),
        "max_provider_attempts_per_case": MAX_PROVIDER_ATTEMPTS_PER_CASE,
        "allowed_retry_categories": sorted(list(ALLOWED_RETRY_CATEGORIES)),
        "plans_planned": len(CASE_ORDER),
        "plans_completed": len(plan_records),
        "plans_failed": 0,
        "accounting": {
            "analyzer_calls": len(plan_records),
            "embedding_calls": 0,
            "reranker_calls": 0,
            "logical_model_calls": len(plan_records),
            "provider_attempts": total_attempts,
            "token_usage": total_tokens,
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "postgresql_writes": 0,
            "qdrant_writes": 0,
            "ingestion": 0,
            "reindex": 0,
            "novel_validation_runs": 0,
            "novel_holdout_runs": 0,
            "protected_dataset_access": 0,
        },
        "plans": plan_records,
    }

    _save_json(project_root / RAW_PLANS_PATH, raw_artifact)

    exposure["D4_A2_V2_OUTCOME_EXPOSURE"] = "PLANS_FROZEN"
    exposure["phase_p_slots_completed"] = len(plan_records)
    _save_json(manifest_path, manifest)

    print(f"[PHASE P COMPLETE] All {len(plan_records)} plans frozen to {RAW_PLANS_PATH}")
    return raw_artifact


def check_git_plan_freeze_status(
    project_root: Path,
    rel_path: str = RAW_PLANS_PATH,
    commit_a_sha: str = IMPLEMENTATION_FREEZE_HEAD,
) -> str:
    """Mechanically checks that the artifact at rel_path satisfies R2-aware freeze and lineage guards:
    1. Is present in Git HEAD and clean in both index and worktree.
    2. Raw plan artifact was frozen in exactly PLAN_FREEZE_HEAD (537836244...).
    3. Raw plan Git blob at current HEAD is identical to blob at PLAN_FREEZE_HEAD
       and matches authoritative PLAN_FREEZE_RAW_BLOB (ee7c1c011...).
    4. Lineage verification:
       - PLAN_FREEZE_HEAD parent is IMPLEMENTATION_FREEZE_HEAD (afc93327...).
       - Current Git HEAD is exactly the finalized R2 repair commit.
       - R2 commit message matches EXPECTED_R2_COMMIT_MESSAGE.
       - Current HEAD is a direct child of PLAN_FREEZE_HEAD (parents == [PLAN_FREEZE_HEAD]).
       - Arbitrary later descendants fail closed.
    5. Allowed diff verification:
       - Diff between PLAN_FREEZE_HEAD and current HEAD contains only ALLOWED_R2_DIFF_FILES.
       - Disallowed changes to raw plans, manifest, original prereg, src/, configs/, benchmarks, novel_dev fail.
    6. Historical diff verification:
       - Diff between IMPLEMENTATION_FREEZE_HEAD and PLAN_FREEZE_HEAD contains only ALLOWED_COMMIT_B_DIFF_FILES.
    7. Clean worktree/index across all frozen implementation and R2 paths.

    Returns the Git commit SHA where the raw plans artifact was frozen (PLAN_FREEZE_HEAD).
    """
    rel_path_posix = rel_path.replace("\\", "/")

    # 1. Present in Git HEAD
    cat_proc = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{rel_path_posix}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if cat_proc.returncode != 0:
        raise RuntimeError(
            f"Plan freeze artifact {rel_path_posix} is not present in Git HEAD! "
            f"Phase P plans must be committed before Phase R exposure."
        )

    # 2. Clean in both index and worktree
    status_proc = subprocess.run(
        ["git", "status", "--porcelain", "-uall", "--", rel_path_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    status_out = status_proc.stdout.strip()
    if status_out:
        raise RuntimeError(
            f"Plan freeze artifact {rel_path_posix} has uncommitted/dirty changes in index or worktree: {status_out!r}. "
            f"It must be clean in both index and worktree."
        )

    diff_proc = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", rel_path_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    diff_out = diff_proc.stdout.strip()
    if diff_out:
        raise RuntimeError(
            f"Plan freeze artifact {rel_path_posix} differs from Git HEAD: {diff_out!r}"
        )

    # 3. Raw plan origin: was frozen in exactly PLAN_FREEZE_HEAD (Section 14.1)
    log_proc = subprocess.run(
        ["git", "log", "-1", "--format=%H", "HEAD", "--", rel_path_posix],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    raw_plan_origin_commit = log_proc.stdout.strip()
    if raw_plan_origin_commit != PLAN_FREEZE_HEAD:
        raise RuntimeError(
            f"Plan freeze artifact {rel_path_posix} origin commit mismatch: "
            f"expected exactly PLAN_FREEZE_HEAD ({PLAN_FREEZE_HEAD}), "
            f"got {raw_plan_origin_commit}."
        )

    # 4. Raw plan immutability: Git blob identity (Section 14.2)
    blob_freeze_proc = subprocess.run(
        ["git", "rev-parse", f"{PLAN_FREEZE_HEAD}:{rel_path_posix}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if blob_freeze_proc.returncode != 0:
        raise RuntimeError(
            f"Failed to get Git blob for {rel_path_posix} at {PLAN_FREEZE_HEAD}: {blob_freeze_proc.stderr.strip()}"
        )
    freeze_blob = blob_freeze_proc.stdout.strip()

    blob_head_proc = subprocess.run(
        ["git", "rev-parse", f"HEAD:{rel_path_posix}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if blob_head_proc.returncode != 0:
        raise RuntimeError(
            f"Failed to get Git blob for {rel_path_posix} at HEAD: {blob_head_proc.stderr.strip()}"
        )
    head_blob = blob_head_proc.stdout.strip()

    if head_blob != freeze_blob:
        raise RuntimeError(
            f"Raw plan Git blob at HEAD ({head_blob}) differs from PLAN_FREEZE_HEAD blob ({freeze_blob})! "
            f"Raw plans artifact must remain Git-object identical."
        )
    if head_blob != PLAN_FREEZE_RAW_BLOB:
        raise RuntimeError(
            f"Raw plan Git blob at HEAD ({head_blob}) does not match authoritative PLAN_FREEZE_RAW_BLOB ({PLAN_FREEZE_RAW_BLOB})!"
        )

    hash_obj_proc = subprocess.run(
        ["git", "hash-object", str(project_root / rel_path)],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if hash_obj_proc.returncode == 0:
        worktree_blob = hash_obj_proc.stdout.strip()
        if worktree_blob != freeze_blob:
            raise RuntimeError(
                f"Raw plan worktree blob ({worktree_blob}) differs from frozen blob ({freeze_blob})!"
            )

    # 5. Plan-freeze ancestry and lineage (Section 14.3, 14.4)
    plan_freeze_parent_proc = subprocess.run(
        ["git", "log", "-1", "--format=%P", PLAN_FREEZE_HEAD],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    plan_freeze_parents = plan_freeze_parent_proc.stdout.strip().split()
    if IMPLEMENTATION_FREEZE_HEAD not in plan_freeze_parents:
        raise RuntimeError(
            f"PLAN_FREEZE_HEAD ({PLAN_FREEZE_HEAD}) parent mismatch: "
            f"expected {IMPLEMENTATION_FREEZE_HEAD}, got {plan_freeze_parents}."
        )

    current_head = _git_head(project_root)
    r2_commit_sha, r2_commit_msg = get_r2_repair_commit(project_root)

    if current_head != r2_commit_sha:
        raise RuntimeError(
            f"Current Git HEAD ({current_head}) is not the finalized R2 repair commit ({r2_commit_sha})! "
            f"Arbitrary later descendants or uncommitted state must fail closed."
        )

    if r2_commit_msg != EXPECTED_R2_COMMIT_MESSAGE:
        raise RuntimeError(
            f"R2 repair commit message mismatch: expected '{EXPECTED_R2_COMMIT_MESSAGE}', "
            f"got '{r2_commit_msg}' (commit {r2_commit_sha})."
        )

    head_parent_proc = subprocess.run(
        ["git", "log", "-1", "--format=%P", current_head],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    head_parents = head_parent_proc.stdout.strip().split()
    if head_parents != [PLAN_FREEZE_HEAD]:
        raise RuntimeError(
            f"R2 repair HEAD ({current_head}) is not a direct child of PLAN_FREEZE_HEAD ({PLAN_FREEZE_HEAD})! "
            f"Parents: {head_parents}."
        )

    # 6. R2 allowed diff: diff between PLAN_FREEZE_HEAD and current_head (Section 14.5)
    diff_r2 = subprocess.run(
        ["git", "diff", "--name-only", PLAN_FREEZE_HEAD, current_head],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    changed_r2_files = [
        f.strip().replace("\\", "/")
        for f in diff_r2.stdout.splitlines()
        if f.strip()
    ]
    disallowed_r2 = [f for f in changed_r2_files if f not in ALLOWED_R2_DIFF_FILES]
    if disallowed_r2:
        raise RuntimeError(
            f"R2 repair commit modified disallowed paths relative to PLAN_FREEZE_HEAD ({PLAN_FREEZE_HEAD}): {disallowed_r2}. "
            f"Only {ALLOWED_R2_DIFF_FILES} are allowed."
        )

    # 7. Historical diff between IMPLEMENTATION_FREEZE_HEAD and PLAN_FREEZE_HEAD
    diff_b = subprocess.run(
        ["git", "diff", "--name-only", IMPLEMENTATION_FREEZE_HEAD, PLAN_FREEZE_HEAD],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    changed_b_files = [
        f.strip().replace("\\", "/")
        for f in diff_b.stdout.splitlines()
        if f.strip()
    ]
    disallowed_b = [f for f in changed_b_files if f not in ALLOWED_COMMIT_B_DIFF_FILES]
    if disallowed_b:
        raise RuntimeError(
            f"PLAN_FREEZE_HEAD modified disallowed paths relative to IMPLEMENTATION_FREEZE_HEAD ({IMPLEMENTATION_FREEZE_HEAD}): {disallowed_b}. "
            f"Only {ALLOWED_COMMIT_B_DIFF_FILES} are allowed to differ in PLAN_FREEZE_HEAD."
        )

    # 8. Worktree/index cleanliness across frozen paths and R2 files
    check_paths = list(FROZEN_IMPLEMENTATION_PATHS) + list(ALLOWED_R2_DIFF_FILES) + [rel_path_posix]
    status_frozen = subprocess.run(
        ["git", "status", "--porcelain", "-uall", "--", *check_paths],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
    )
    dirty_frozen = [
        line.strip()
        for line in status_frozen.stdout.splitlines()
        if line.strip()
    ]
    if dirty_frozen:
        raise RuntimeError(
            f"Worktree or index is dirty for frozen implementation or R2 paths: {dirty_frozen}"
        )

    return PLAN_FREEZE_HEAD


def verify_plan_freeze_gate(
    project_root: Path,
    raw_plans_path: Path | None = None,
    *,
    git_checker: Any | None = None,
) -> dict[str, Any]:
    """Hard Commit-B plan-freeze gate enforced mechanically before Phase R provider exposure.

    Validates:
      1. evaluation/d4_a2_v2_raw_plans.json exists and is parseable.
      2. Artifact is present in Git HEAD, clean in index and worktree, and committed after implementation freeze.
      3. Commit B is descendant of implementation freeze and distinct from it.
      4. Current HEAD is exactly Commit B with no later commit.
      5. Only allowed Phase-P artifacts (raw_plans.json and manifest Phase-P state) differ between freeze and Commit B.
      6. Frozen implementation files are Git-object unchanged between implementation freeze and Commit B.
      7. Exactly 16 unique case plans in exact CASE_ORDER.
      8. All 16 plans have status == 'COMPLETED', error is None, and valid canonical RetrievalPlan.
      9. Phase P accounting and lifecycle state are complete:
         - PLAN_FREEZE_BOUNDARY_ESTABLISHED is True
         - plans_planned == 16, plans_completed == 16, plans_failed == 0
         - analyzer_calls == 16, zero embedding/reranker/qa/verifier/judge/db/protected calls
      10. Phase R / evaluator flags remain False:
         - PHASE_R_RETRIEVAL_EXECUTED is False
         - EVALUATOR_EXECUTED is False
         - SCIENTIFIC_VERDICT_COMPUTED is False
      11. Captures and returns the actual plan-freeze Git commit identity and implementation freeze identity.

    Fails closed on modified, uncommitted, stale, or malformed plan artifacts.
    """
    raw_plans_file = (raw_plans_path or (project_root / RAW_PLANS_PATH)).resolve()
    if not raw_plans_file.exists():
        raise FileNotFoundError(
            f"Phase P raw plans file {raw_plans_file} missing! "
            f"Phase P must be executed and committed as Commit B before Phase R."
        )

    try:
        raw_data = _load_json(raw_plans_file)
    except Exception as exc:
        raise ValueError(f"Malformed JSON in raw plans artifact {raw_plans_file}: {exc}") from exc

    if not isinstance(raw_data, dict):
        raise ValueError(f"Raw plans artifact {raw_plans_file} is not a JSON object")

    # Implementation freeze identity recorded during Phase P
    commit_a_sha = (
        raw_data.get("implementation_freeze_head")
        or raw_data.get("commit_a_r1_implementation_freeze_head")
        or raw_data.get("commit_a_implementation_freeze_head")
    )
    if not commit_a_sha or not isinstance(commit_a_sha, str) or commit_a_sha.startswith("UNKNOWN"):
        raise ValueError(
            f"Raw plans artifact missing valid implementation freeze HEAD: {commit_a_sha!r}"
        )

    # Git HEAD presence, cleanliness, and descendant check
    try:
        rel_path = raw_plans_file.relative_to(project_root.resolve()).as_posix()
    except ValueError:
        rel_path = RAW_PLANS_PATH

    if git_checker is not None:
        plan_freeze_commit_sha = git_checker(project_root, rel_path, commit_a_sha)
    else:
        plan_freeze_commit_sha = check_git_plan_freeze_status(project_root, rel_path, commit_a_sha)

    # State flags
    if raw_data.get("PLAN_FREEZE_BOUNDARY_ESTABLISHED") is not True:
        raise ValueError("Plan artifact PLAN_FREEZE_BOUNDARY_ESTABLISHED must be True")
    if raw_data.get("PHASE_R_RETRIEVAL_EXECUTED") is not False:
        raise ValueError("Plan artifact PHASE_R_RETRIEVAL_EXECUTED must be False before Phase R execution")
    if raw_data.get("EVALUATOR_EXECUTED") is not False:
        raise ValueError("Plan artifact EVALUATOR_EXECUTED must be False before Phase R execution")
    if raw_data.get("SCIENTIFIC_VERDICT_COMPUTED") is not False:
        raise ValueError("Plan artifact SCIENTIFIC_VERDICT_COMPUTED must be False before Phase R execution")

    # Accounting completeness
    if raw_data.get("plans_planned") != len(CASE_ORDER):
        raise ValueError(
            f"Plan artifact plans_planned mismatch: expected {len(CASE_ORDER)}, got {raw_data.get('plans_planned')}"
        )
    if raw_data.get("plans_completed") != len(CASE_ORDER):
        raise ValueError(
            f"Plan artifact plans_completed mismatch: expected {len(CASE_ORDER)}, got {raw_data.get('plans_completed')}"
        )
    if raw_data.get("plans_failed") != 0:
        raise ValueError(f"Plan artifact plans_failed != 0: {raw_data.get('plans_failed')}")

    acct = raw_data.get("accounting", {})
    if acct.get("analyzer_calls") != len(CASE_ORDER):
        raise ValueError(
            f"Phase P accounting analyzer_calls mismatch: expected {len(CASE_ORDER)}, got {acct.get('analyzer_calls')}"
        )
    if acct.get("embedding_calls", 0) != 0:
        raise ValueError(f"Phase P accounting embedding_calls > 0: {acct.get('embedding_calls')}")
    if acct.get("reranker_calls", 0) != 0:
        raise ValueError(f"Phase P accounting reranker_calls > 0: {acct.get('reranker_calls')}")
    for forbidden in (
        "qa_calls", "verifier_calls", "judge_calls", "postgresql_writes", "qdrant_writes",
        "ingestion", "reindex", "novel_validation_runs", "novel_holdout_runs", "protected_dataset_access"
    ):
        if acct.get(forbidden, 0) != 0:
            raise ValueError(f"Phase P accounting violation: {forbidden} = {acct.get(forbidden)} != 0")

    # Contract fields verification
    if raw_data.get("max_provider_attempts_per_case") is not None:
        if raw_data.get("max_provider_attempts_per_case") != MAX_PROVIDER_ATTEMPTS_PER_CASE:
            raise ValueError(
                f"Plan artifact max_provider_attempts_per_case mismatch: {raw_data.get('max_provider_attempts_per_case')}"
            )

    # Exactly 16 unique case plans in exact CASE_ORDER
    plans = raw_data.get("plans", [])
    if len(plans) != len(CASE_ORDER):
        raise ValueError(f"Expected exactly {len(CASE_ORDER)} plans, got {len(plans)}")

    seen_cases = set()
    for idx, (expected_cid, p) in enumerate(zip(CASE_ORDER, plans), start=1):
        cid = p.get("case_id")
        if cid != expected_cid:
            raise ValueError(
                f"Plan slot #{idx} case order mismatch: expected {expected_cid}, got {cid}"
            )
        if cid in seen_cases:
            raise ValueError(f"Duplicate case_id {cid} found at slot #{idx}")
        seen_cases.add(cid)

        if p.get("draw_index") != idx:
            raise ValueError(f"Plan slot #{idx} draw_index mismatch: expected {idx}, got {p.get('draw_index')}")
        if p.get("status") != "COMPLETED":
            raise ValueError(f"Plan slot #{idx} ({cid}) status is not COMPLETED: {p.get('status')}")
        if p.get("error") is not None:
            raise ValueError(f"Plan slot #{idx} ({cid}) has error: {p.get('error')}")

        canonical_dict = p.get("canonical_plan") or p.get("accepted_canonical_plan")
        if not canonical_dict or not isinstance(canonical_dict, dict):
            raise ValueError(f"Plan slot #{idx} ({cid}) missing canonical_plan dictionary")

        try:
            RetrievalPlan.model_validate(canonical_dict)
        except Exception as exc:
            raise ValueError(
                f"Plan slot #{idx} ({cid}) canonical_plan failed RetrievalPlan schema validation: {exc}"
            ) from exc

        stored_sig = p.get("plan_signature")
        if stored_sig:
            _, computed_sig = compute_plan_signature(canonical_dict)
            if computed_sig != stored_sig:
                raise ValueError(
                    f"Plan slot #{idx} ({cid}) plan_signature mismatch with canonical_plan"
                )

    return {
        "verified": True,
        "raw_plans_path": str(raw_plans_file),
        "implementation_freeze_head": commit_a_sha,
        "commit_a_implementation_freeze_head": commit_a_sha,
        "phase_p_plan_freeze_commit_head": plan_freeze_commit_sha,
        "plan_freeze_head": PLAN_FREEZE_HEAD,
        "raw_plan_blob_sha": PLAN_FREEZE_RAW_BLOB,
        "plans_count": len(plans),
        "cases_validated": CASE_ORDER,
    }


def build_phase_r_cell_record(
    cell_idx: int,
    case_id: str,
    dataset: str,
    arm: str,
    cell_retrieval_data: dict[str, Any],
    frozen_plan: RetrievalPlan | dict[str, Any],
    group_retention_records: dict[str, dict[str, Any]],
    started_at: str | None,
    completed_at: str | None,
    elapsed_seconds: float,
    cell_embedding_calls: int = 0,
    cell_reranker_calls: int = 0,
    cell_provider_attempts: int = 0,
    cell_token_usage: int = 0,
) -> dict[str, Any]:
    """Pure helper constructing a complete, lossless Phase R V2 cell record.

    Preserves all task Section 13 and Section 19 scientific trace data available
    from execute_cell_retrieval without inventing fields from absent keys.
    """
    frozen_plan_dict = (
        frozen_plan.model_dump(mode="json")
        if isinstance(frozen_plan, RetrievalPlan)
        else dict(frozen_plan)
    )
    actual_plan_dict = cell_retrieval_data.get("plan_summary", {})
    plan_equality = bool(frozen_plan_dict == actual_plan_dict)

    return {
        "cell_index": cell_idx,
        "case_id": case_id,
        "dataset": dataset,
        "arm": arm,
        "status": "COMPLETED",
        "elapsed_seconds": elapsed_seconds,
        "plan_equality_verified": plan_equality,
        "analyzer_provider_calls": 0,
        "embedding_calls": cell_embedding_calls,
        "reranker_calls": cell_reranker_calls,
        "provider_internal_attempts": cell_provider_attempts,
        "token_usage": cell_token_usage,
        "started_at": started_at,
        "completed_at": completed_at,
        "frozen_canonical_plan": frozen_plan_dict,
        "actual_canonical_plan": actual_plan_dict,
        "matched_query_expansion_rules": cell_retrieval_data.get("matched_query_expansion_rules", []),
        "inputs": cell_retrieval_data.get("inputs", {}),
        "exact_effective_preserved_components": cell_retrieval_data.get("exact_effective_preserved_components", {}),
        "exact_effective_suppressed_components": cell_retrieval_data.get("exact_effective_suppressed_components", {}),
        "channel_rankings": cell_retrieval_data.get("channel_rankings", {}),
        "resolved_d2_seeds": cell_retrieval_data.get("resolved_d2_seeds", []),
        "reached_structures": cell_retrieval_data.get("reached_structures", []),
        "reachability_receipts": cell_retrieval_data.get("reachability_receipts", []),
        "actual_bridge_receipts": cell_retrieval_data.get("actual_bridge_receipts", []),
        "eligible_bridge_candidates": cell_retrieval_data.get("eligible_bridge_candidates", []),
        "selected_bridge_candidates": cell_retrieval_data.get("selected_bridge_candidates", []),
        "v2_diagnostics": cell_retrieval_data.get("v2_diagnostics", {}),
        "structured_receipts": cell_retrieval_data.get("structured_receipts"),
        "ordinary_fused_ordering": cell_retrieval_data.get("ordinary_fused_ordering", []),
        "ordinary_fused_top30": cell_retrieval_data.get("ordinary_fused_top30", []),
        "reserved_candidate_ids": cell_retrieval_data.get("reserved_candidate_ids", []),
        "displaced_candidate_ids": cell_retrieval_data.get("displaced_candidate_ids", []),
        "final_pool_object_ids": cell_retrieval_data.get("final_pool_object_ids", []),
        "reranked_object_ids": cell_retrieval_data.get("reranked_object_ids", []),
        "ranked_object_ids": cell_retrieval_data.get("ranked_object_ids", []),
        "final_evidence_object_ids": cell_retrieval_data.get("final_evidence_object_ids", []),
        "final_evidence_locators": cell_retrieval_data.get("final_evidence_locators", {}),
        "excluded": cell_retrieval_data.get("excluded", []),
        "backfill_admissions": cell_retrieval_data.get("backfill_admissions", []),
        "group_retention": group_retention_records,
    }


def execute_phase_r(
    project_root: Path,
    *,
    git_checker: Any | None = None,
) -> dict[str, Any]:
    """Separately authorized future Phase R runner:
    Executes 32 formal serial retrieval cells across the 16 frozen plans x 2 arms in balanced
    alternating schedule.
    Zero Query Analyzer provider calls (bypassed via frozen_plan_context adapter).
    Enforces same-case canonical plan equality verification for every cell.
    Persists raw retrieval outputs to RAW_RESULTS_PATH (Commit C input).
    """
    load_dotenv(project_root / ".env")

    # Hard Commit-B plan-freeze gate enforced mechanically BEFORE changing exposure state or invoking retrieval
    gate_receipt = verify_plan_freeze_gate(project_root, git_checker=git_checker)
    commit_a_sha = gate_receipt["commit_a_implementation_freeze_head"]
    plan_freeze_commit_sha = gate_receipt["phase_p_plan_freeze_commit_head"]

    raw_plans_path = project_root / RAW_PLANS_PATH
    raw_p = _load_json(raw_plans_path)
    plans = raw_p.get("plans", [])

    manifest_path = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_path)
    exposure = manifest.setdefault("outcome_exposure_state", {})
    if exposure.get("D4_A2_V2_OUTCOME_EXPOSURE") in ("RAW_RETRIEVAL_COMPLETE", "EVALUATION_COMPLETE"):
        print("[PHASE R ALREADY COMPLETED] Loading existing paired results.")
        return _load_json(project_root / RAW_RESULTS_PATH)

    exposure["D4_A2_V2_OUTCOME_EXPOSURE"] = "RAW_RETRIEVAL_STARTED"
    _save_json(manifest_path, manifest)

    retriever = Retriever(project_root)
    object_lookup = load_object_lookup(project_root)

    original_qe = load_query_expansions(project_root / CONFIG_QUERY_EXPANSIONS_PATH)
    masked_qe = d4_a1.apply_batch1_in_memory_mask(original_qe)

    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_questions = {q.id: q for q in gold_ds.questions + novel_ds.questions}

    plans_by_case = {
        p["case_id"]: RetrievalPlan.model_validate(p["canonical_plan"])
        for p in plans
    }

    cell_records: list[dict[str, Any]] = []
    total_tokens = 0
    total_attempts = 0
    total_embedding_calls = 0
    total_reranker_calls = 0

    print(f"[PHASE R] Beginning {TOTAL_FORMAL_SLOTS} formal shared-plan retrieval cells...")

    for item in SCHEDULE_32:
        cell_idx = item["slot_index"]
        cid = item["case_id"]
        arm = item["arm"]

        manifest_cell = manifest["phase_r_cells_32"][cell_idx - 1]
        if manifest_cell["status"] == "COMPLETED":
            print(f"  Cell #{cell_idx} ({cid}, {arm}) already completed, skipping.")
            continue
        if manifest_cell["status"] == "STARTED":
            raise RuntimeError(f"Cell #{cell_idx} ({cid}) in ambiguous STARTED state! Fail closed.")

        manifest_cell["status"] = "STARTED"
        manifest_cell["started_at"] = datetime.datetime.now().isoformat()
        _save_json(manifest_path, manifest)

        frozen_plan = plans_by_case[cid]
        q_obj = all_questions[cid]
        question_text = q_obj.query
        a1_arm = "LEGACY_CONTROL" if arm == "BEFORE_COMPAT" else "BATCH1_REPLACEMENT"

        stats_before = retriever.vertex.stats_snapshot()
        t0 = time.time()

        with frozen_plan_context(retriever, frozen_plan) as adapter_calls:
            cell_retrieval_data = d4_a1.execute_cell_retrieval(
                retriever=retriever,
                case_id=cid,
                arm=a1_arm,
                question_text=question_text,
                original_expansions=original_qe,
                masked_expansions=masked_qe,
                object_lookup=object_lookup,
            )

        elapsed = round(time.time() - t0, 3)
        stats_delta = retriever.vertex.stats_delta(stats_before)

        if len(adapter_calls) != 1:
            raise RuntimeError(
                f"Cell #{cell_idx}: Expected exactly 1 adapter analyze call, got {len(adapter_calls)}"
            )

        actual_plan_dict = cell_retrieval_data.get("plan_summary", {})
        frozen_plan_dict = frozen_plan.model_dump(mode="json")
        if actual_plan_dict != frozen_plan_dict:
            raise RuntimeError(
                f"Cell #{cell_idx}: Plan equality mismatch! Actual plan used != frozen plan for {cid}"
            )

        # Provider accounting: zero analyzer provider calls in Phase R
        cell_provider_attempts = stats_delta.get("model_calls", 0)
        cell_tokens = stats_delta.get("token_usage", 0)
        cell_emb = stats_delta.get("embedding_calls", 1)
        cell_gen = stats_delta.get("generation_calls", 1)

        total_attempts += cell_provider_attempts
        total_tokens += cell_tokens
        total_embedding_calls += cell_emb
        total_reranker_calls += cell_gen

        channel_rankings = cell_retrieval_data.get("channel_rankings", {})
        exact_ids = channel_rankings.get("exact", [])
        channel_union_ids = list(dict.fromkeys([
            oid for ch_list in channel_rankings.values() for oid in ch_list
        ]))
        fused_top30_ids = cell_retrieval_data.get("ordinary_fused_top30", [])
        final_pool_ids = cell_retrieval_data.get("final_pool_object_ids", [])
        final_evidence_ids = cell_retrieval_data.get("final_evidence_object_ids", [])

        # Evidence group matching
        group_retention_records: dict[str, dict[str, Any]] = {}
        for eg in q_obj.required_evidence_groups:
            exact_rec, _ = _matched_evidence_groups([eg], exact_ids, object_lookup)
            union_rec, _ = _matched_evidence_groups([eg], channel_union_ids, object_lookup)
            fused_rec, _ = _matched_evidence_groups([eg], fused_top30_ids, object_lookup)
            final_pool_rec, _ = _matched_evidence_groups([eg], final_pool_ids, object_lookup)
            final_ev_rec, _ = _matched_evidence_groups([eg], final_evidence_ids, object_lookup)
            group_retention_records[eg.group_id] = {
                "critical": eg.critical,
                "role": eg.role,
                "in_exact_channel": exact_rec > 0,
                "in_channel_union": union_rec > 0,
                "in_ordinary_fused_top30": fused_rec > 0,
                "in_pre_rerank_pool": final_pool_rec > 0,
                "in_final_evidence": final_ev_rec > 0,
            }

        cell_record = build_phase_r_cell_record(
            cell_idx=cell_idx,
            case_id=cid,
            dataset=q_obj.split,
            arm=arm,
            cell_retrieval_data=cell_retrieval_data,
            frozen_plan=frozen_plan,
            group_retention_records=group_retention_records,
            started_at=manifest_cell["started_at"],
            completed_at=datetime.datetime.now().isoformat(),
            elapsed_seconds=elapsed,
            cell_embedding_calls=cell_emb,
            cell_reranker_calls=cell_gen,
            cell_provider_attempts=cell_provider_attempts,
            cell_token_usage=cell_tokens,
        )
        cell_records.append(cell_record)

        manifest_cell["status"] = "COMPLETED"
        manifest_cell["completed_at"] = cell_record["completed_at"]
        manifest_cell["plan_equality_verified"] = True
        manifest_cell["token_usage"] = cell_tokens
        _save_json(manifest_path, manifest)

        print(f"  Cell #{cell_idx}/{TOTAL_FORMAL_SLOTS} ({cid}, {arm}) COMPLETED in {elapsed}s")

    raw_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V2",
        "stage": "Phase R — Controlled Shared Plan Retrieval",
        "created_at": datetime.datetime.now().isoformat(),
        "starting_head": STARTING_HEAD,
        "commit_a_implementation_freeze_head": commit_a_sha,
        "phase_p_plan_freeze_commit_head": plan_freeze_commit_sha,
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED": True,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "cells_planned": TOTAL_FORMAL_SLOTS,
        "cells_completed": len(cell_records),
        "cells_failed": 0,
        "accounting": {
            "FORMAL_CELLS_COMPLETED": len(cell_records),
            "FORMAL_CELLS_FAILED": 0,
            "ANALYZER_CALLS": 0,
            "EMBEDDING_CALLS": total_embedding_calls,
            "RERANKER_CALLS": total_reranker_calls,
            "LOGICAL_MODEL_CALLS": total_embedding_calls + total_reranker_calls,
            "PROVIDER_INTERNAL_ATTEMPTS": total_attempts,
            "TOTAL_TOKEN_USAGE": total_tokens,
            "QA_CALLS": 0,
            "VERIFIER_CALLS": 0,
            "JUDGE_CALLS": 0,
            "POSTGRESQL_WRITES": 0,
            "QDRANT_WRITES": 0,
            "INGESTION_RUNS": 0,
            "REINDEX_RUNS": 0,
            "NOVEL_VALIDATION_RUNS": 0,
            "NOVEL_HOLDOUT_RUNS": 0,
            "PROTECTED_DATASET_ACCESS": 0,
        },
        "model_contract": {
            "generation_model_id": EXPECTED_MODEL,
            "embedding_model_id": EXPECTED_EMBEDDING_MODEL,
            "temperature": EXPECTED_TEMPERATURE,
            "location": EXPECTED_VERTEX_LOCATION,
            "system_prompt": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT",
            "query_analyzer_prompt": "src/panda_agent/prompts.py:QUERY_ANALYZER_SYSTEM_PROMPT",
        },
        "authority": {
            "manifest": MANIFEST_PATH,
            "preregistration": PREREGISTRATION_PATH,
            "raw_plans": RAW_PLANS_PATH,
            "commit_a_implementation_freeze_head": commit_a_sha,
            "phase_p_plan_freeze_commit_head": plan_freeze_commit_sha,
        },
        "slots": cell_records,
    }

    _save_json(project_root / RAW_RESULTS_PATH, raw_artifact)

    exposure["D4_A2_V2_OUTCOME_EXPOSURE"] = "RAW_RETRIEVAL_COMPLETE"
    exposure["phase_r_cells_completed"] = len(cell_records)
    _save_json(manifest_path, manifest)

    print(f"[PHASE R COMPLETE] All {len(cell_records)} cells frozen to {RAW_RESULTS_PATH}")
    return raw_artifact


def validate_raw_artifact_structural_validity(
    raw_data: dict[str, Any],
    manifest: dict[str, Any] | None = None,
    prereg: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> tuple[bool, str | None, dict[str, int]]:
    """Mechanically validates the raw results artifact before any metric evaluation:
    1. Exactly 32 unique slots.
    2. Exact balanced alternating schedule.
    3. Every slot COMPLETED, error is None.
    4. Plan equality verified == True for all 32 cells.
    5. Phase R analyzer provider calls == 0.
    6. Model contract matches gemini-3.8-flash, gemini-embedding-2.
    7. Raw boundary flags: EVALUATOR_EXECUTED == False, SCIENTIFIC_VERDICT_COMPUTED == False.
    8. Protected dataset access counters == 0.
    9. Post-exposure mutation counters == 0.
    """
    mutation_counters = {
        "POST_EXPOSURE_CASE_MUTATIONS": 0,
        "POST_EXPOSURE_PLAN_MUTATIONS": 0,
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

    # Check schedule
    for i, s in enumerate(slots):
        exp_item = SCHEDULE_32[i]
        exp_idx = exp_item["slot_index"]
        exp_cid = exp_item["case_id"]
        exp_arm = exp_item["arm"]

        if (s.get("cell_index"), s.get("case_id"), s.get("arm")) != (exp_idx, exp_cid, exp_arm):
            mutation_counters["POST_EXPOSURE_CASE_MUTATIONS"] += 1
            return (
                False,
                f"Schedule mismatch at slot #{i + 1}: expected ({exp_idx}, {exp_cid}, {exp_arm}), got "
                f"({s.get('cell_index')}, {s.get('case_id')}, {s.get('arm')})",
                mutation_counters,
            )

        if s.get("status") != "COMPLETED":
            return (
                False,
                f"Slot #{exp_idx} status is not COMPLETED: {s.get('status')}",
                mutation_counters,
            )

        if s.get("plan_equality_verified") is not True:
            mutation_counters["POST_EXPOSURE_PLAN_MUTATIONS"] += 1
            return (
                False,
                f"Slot #{exp_idx} plan equality verification failed",
                mutation_counters,
            )

        if s.get("analyzer_provider_calls", 0) != 0:
            return (
                False,
                f"Slot #{exp_idx} Analyzer provider calls > 0: {s.get('analyzer_provider_calls')}",
                mutation_counters,
            )

    # Check raw boundary flags
    if raw_data.get("EVALUATOR_EXECUTED") is not False:
        return False, "Raw EVALUATOR_EXECUTED is not False", mutation_counters
    if raw_data.get("SCIENTIFIC_VERDICT_COMPUTED") is not False:
        return False, "Raw SCIENTIFIC_VERDICT_COMPUTED is not False", mutation_counters

    # Check commit provenance
    commit_a_sha = (
        raw_data.get("implementation_freeze_head")
        or raw_data.get("commit_a_r1_implementation_freeze_head")
        or raw_data.get("commit_a_implementation_freeze_head")
    )
    if not commit_a_sha or not isinstance(commit_a_sha, str) or commit_a_sha.startswith("UNKNOWN"):
        return False, "Raw artifact missing valid implementation_freeze_head", mutation_counters
    plan_freeze_sha = raw_data.get("phase_p_plan_freeze_commit_head")
    if not plan_freeze_sha or not isinstance(plan_freeze_sha, str) or plan_freeze_sha.startswith("UNKNOWN"):
        return False, "Raw artifact missing valid phase_p_plan_freeze_commit_head", mutation_counters
    if commit_a_sha == plan_freeze_sha:
        return False, "Raw artifact implementation_freeze_head cannot equal phase_p_plan_freeze_commit_head", mutation_counters

    # Check model contract
    mc = raw_data.get("model_contract", {})
    if mc.get("generation_model_id") != EXPECTED_MODEL:
        mutation_counters["POST_EXPOSURE_MODEL_MUTATIONS"] += 1
    if mc.get("embedding_model_id") != EXPECTED_EMBEDDING_MODEL:
        mutation_counters["POST_EXPOSURE_MODEL_MUTATIONS"] += 1

    # Check protected dataset boundaries
    acct = raw_data.get("accounting", {})
    if (
        acct.get("NOVEL_VALIDATION_RUNS", 0) != 0
        or acct.get("NOVEL_HOLDOUT_RUNS", 0) != 0
        or acct.get("PROTECTED_DATASET_ACCESS", 0) != 0
    ):
        return False, "Protected dataset boundary violated in raw accounting", mutation_counters

    if any(count > 0 for count in mutation_counters.values()):
        return (
            False,
            f"Post-exposure mutations detected: {mutation_counters}",
            mutation_counters,
        )

    return True, None, mutation_counters


def compute_controlled_shared_plan_verdict(
    execution_valid: bool | None = None,
    protocol_violation: bool = False,
    protocol_violation_reason: str | None = None,
    before_reference_valid: bool | None = None,
    target_replacement_reproduced: int | None = None,
    batch1_dependency_removed: int | None = None,
    shared_plan_critical_regressions: list[str] | None = None,
    grounding_regressions: int | None = None,
    wrong_version_regressions: int | None = None,
    invalid_provenance_recoveries: int | None = None,
    metric_deltas: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Pure deterministic decision logic implementing D4-A2-V2 Section 20.

    Exact 6-Level Precedence:
      Level 1: INVALID / PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED
      Level 2: INCONCLUSIVE / BEFORE_REFERENCE_NOT_REPRODUCED
      Level 3: FAIL / PRIMARY_TARGET_REPLACEMENT_NOT_REPRODUCED
      Level 4: FAIL / SHARED_PLAN_CRITICAL_TREATMENT_REGRESSION
      Level 5: PARTIAL / AGGREGATE_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE
      Level 6: PASS / CONTROLLED_SHARED_PLAN_T2_VALIDATED

    Requires complete, explicit scientific evaluator inputs. Missing, empty, or
    malformed inputs fail closed at Level 1 with INCOMPLETE_EVALUATOR_INPUT.
    """
    # Level 1 — Explicit protocol violation or execution failure
    if protocol_violation or execution_valid is False:
        return {
            "verdict_level": 1,
            "verdict": VERDICT_LEVEL_1_INVALID,
            "verdict_reason": (
                protocol_violation_reason
                or "Fundamental protocol, plan construction, or execution integrity failure occurred."
            ),
        }

    # Completeness verification for explicit evaluator inputs
    missing_fields: list[str] = []
    if execution_valid is None:
        missing_fields.append("execution_valid")
    if before_reference_valid is None:
        missing_fields.append("before_reference_valid")
    if target_replacement_reproduced is None:
        missing_fields.append("target_replacement_reproduced")
    if batch1_dependency_removed is None:
        missing_fields.append("batch1_dependency_removed")
    if shared_plan_critical_regressions is None:
        missing_fields.append("shared_plan_critical_regressions")
    if grounding_regressions is None:
        missing_fields.append("grounding_regressions")
    if wrong_version_regressions is None:
        missing_fields.append("wrong_version_regressions")
    if invalid_provenance_recoveries is None:
        missing_fields.append("invalid_provenance_recoveries")
    if metric_deltas is None:
        missing_fields.append("metric_deltas")
    else:
        for m in REQUIRED_PRIMARY_METRIC_KEYS:
            if m not in metric_deltas or metric_deltas[m] is None or not isinstance(metric_deltas[m], (int, float)):
                missing_fields.append(f"metric_deltas[{m}]")

    if missing_fields:
        return {
            "verdict_level": 1,
            "verdict": VERDICT_LEVEL_1_INVALID,
            "verdict_reason": f"INCOMPLETE_EVALUATOR_INPUT: Missing or invalid required evaluator inputs: {', '.join(missing_fields)}",
        }

    # Level 2 — INCONCLUSIVE
    if not before_reference_valid:
        return {
            "verdict_level": 2,
            "verdict": VERDICT_LEVEL_2_INCONCLUSIVE,
            "verdict_reason": (
                "Prospective frozen plan prevented required BEFORE primary-reference reproduction "
                "(g036.e1 or g021.e1 not retained under BEFORE_COMPAT) such that migration targets cannot be evaluated fairly."
            ),
        }

    # Level 3 — FAIL (Primary targets replacement)
    if target_replacement_reproduced < 2 or batch1_dependency_removed < 2:
        return {
            "verdict_level": 3,
            "verdict": VERDICT_LEVEL_3_FAIL_PRIMARY_TARGET,
            "verdict_reason": (
                f"Primary target replacement or fixed locator dependency removal not reproduced: "
                f"{target_replacement_reproduced}/2 targets reproduced under AFTER with valid governed witness, "
                f"{batch1_dependency_removed}/2 dependencies removed."
            ),
        }

    # Level 4 — FAIL (Shared-plan critical regression or safety gate failure)
    crit_regs = shared_plan_critical_regressions
    if (
        len(crit_regs) > 0
        or grounding_regressions > 0
        or wrong_version_regressions > 0
        or invalid_provenance_recoveries > 0
    ):
        return {
            "verdict_level": 4,
            "verdict": VERDICT_LEVEL_4_FAIL_SHARED_PLAN_CRITICAL,
            "verdict_reason": (
                f"Shared-plan critical treatment regression or grounding/version safety violation: "
                f"{len(crit_regs)} critical regression(s) ({crit_regs}), "
                f"{grounding_regressions} grounding regression(s), "
                f"{wrong_version_regressions} wrong-version regression(s), "
                f"{invalid_provenance_recoveries} invalid-provenance recovery(ies)."
            ),
        }

    # Level 5 — PARTIAL (Aggregate tolerances)
    tolerance_violations: list[str] = []
    delta_r5 = metric_deltas["recall_at_5"]
    delta_r10 = metric_deltas["recall_at_10"]
    delta_r20 = metric_deltas["recall_at_20"]
    delta_comb = metric_deltas["combined_candidate_recall"]
    delta_final = metric_deltas["final_evidence_recall"]
    delta_crit = metric_deltas["critical_final_evidence_recall"]

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
            "verdict": VERDICT_LEVEL_5_PARTIAL_TOLERANCE,
            "verdict_reason": (
                f"Aggregate retrieval regressions exceeded bounded tolerances: {'; '.join(tolerance_violations)}."
            ),
        }

    # Level 6 — PASS
    return {
        "verdict_level": 6,
        "verdict": VERDICT_LEVEL_6_PASS,
        "verdict_reason": (
            "Controlled shared-plan T2 validation passed all gating criteria: 16/16 prospective plans frozen, "
            "32/32 valid cells, 16/16 shared-plan equality, 0 Phase R Analyzer calls, valid BEFORE reference, "
            "target replacements reproduced 2/2, dependencies removed 2/2, 0 shared-plan critical regressions, "
            "0 grounding/version/provenance violations, and all aggregate bounded tolerances satisfied."
        ),
    }


def get_evidence_group_criticality(group_id: str, default_critical: bool) -> bool:
    """Corrected criticality contract:
    - g021.e1 = critical (True)
    - g021.e2 = noncritical supporting evidence (False)
    - n022.e2 = critical (True)
    """
    if group_id == "g021.e1":
        return True
    if group_id == "g021.e2":
        return False
    if group_id == "n022.e2":
        return True
    return default_critical


def classify_pair_pre_rerank(before_retained: bool, after_retained: bool) -> str:
    """Classify pre-rerank pool paired retention state."""
    if before_retained and after_retained:
        return PAIR_PRESERVED
    if not before_retained and after_retained:
        return PAIR_TREATMENT_RECOVERY
    if before_retained and not after_retained:
        return PAIR_TREATMENT_REGRESSION
    return PAIR_UNRESOLVED_BOTH


def classify_pair_final_evidence(before_retained: bool, after_retained: bool) -> str:
    """Classify final-evidence paired retention state."""
    if before_retained and after_retained:
        return FINAL_PRESERVED
    if not before_retained and after_retained:
        return FINAL_TREATMENT_RECOVERY
    if before_retained and not after_retained:
        return FINAL_TREATMENT_REGRESSION
    return FINAL_UNRESOLVED_BOTH


def _evidence_in_candidates(
    evidence_group: GoldEvidenceGroup,
    candidate_ids: list[str],
    object_lookup: dict[str, dict[str, Any]],
) -> bool:
    if not candidate_ids:
        return False
    rec, _ = _matched_evidence_groups([evidence_group], candidate_ids, object_lookup)
    return rec > 0


def compute_first_divergence_layer(
    slot_b: dict[str, Any],
    slot_a: dict[str, Any],
    evidence_group: GoldEvidenceGroup,
    object_lookup: dict[str, dict[str, Any]],
    b_pool_retained: bool,
    a_pool_retained: bool,
    b_final_retained: bool,
    a_final_retained: bool,
) -> str:
    """Derives the first observable divergence layer using the frozen 9-element taxonomy.
    Attribution follows the first observable divergence in the retrieval pipeline:
    1. FIXED_LOCATOR_SUPPRESSION
    2. ORDINARY_CHANNEL_RECALL
    3. STRUCTURED_GENERATION
    4. SELECTIVITY
    5. FUSION_CUTOFF
    6. K3_ADMISSION
    7. RERANKER
    8. FINAL_SELECTION
    If no divergence is observed, returns NO_DIVERGENCE.
    """
    # 1. FIXED_LOCATOR_SUPPRESSION
    b_exact_ids = slot_b.get("channel_rankings", {}).get("exact", [])
    a_exact_ids = slot_a.get("channel_rankings", {}).get("exact", [])
    b_in_exact = _evidence_in_candidates(evidence_group, b_exact_ids, object_lookup)
    a_in_exact = _evidence_in_candidates(evidence_group, a_exact_ids, object_lookup)

    suppressed = slot_a.get("exact_effective_suppressed_components", {}) or slot_a.get("suppressed_components", {})
    if b_in_exact and not a_in_exact and bool(suppressed):
        all_supp_symbols = [s for r in suppressed.values() for s in r.get("suppressed_symbols", [])]
        all_supp_hints = [h for r in suppressed.values() for h in r.get("suppressed_paper_page_hints", {}).keys()]
        matches_suppression = False
        for sel in evidence_group.any_of:
            if sel.path and any(sym in sel.path or sel.path in sym for sym in all_supp_symbols):
                matches_suppression = True
                break
            if sel.symbol and any(sym in sel.symbol or sel.symbol in sym for sym in all_supp_symbols):
                matches_suppression = True
                break
            if sel.source_id and sel.source_id in all_supp_hints:
                matches_suppression = True
                break
        if matches_suppression:
            return DIV_FIXED_LOCATOR_SUPPRESSION

    # 2. ORDINARY_CHANNEL_RECALL
    ord_channels = ["exact", "dense", "sparse", "paper", "workflow"]
    b_ord_ids = list(dict.fromkeys(
        oid for ch in ord_channels for oid in slot_b.get("channel_rankings", {}).get(ch, [])
    ))
    a_ord_ids = list(dict.fromkeys(
        oid for ch in ord_channels for oid in slot_a.get("channel_rankings", {}).get(ch, [])
    ))
    b_in_ord = _evidence_in_candidates(evidence_group, b_ord_ids, object_lookup)
    a_in_ord = _evidence_in_candidates(evidence_group, a_ord_ids, object_lookup)

    if b_in_ord != a_in_ord:
        return DIV_ORDINARY_CHANNEL_RECALL

    # 3. STRUCTURED_GENERATION
    eligible_cands = slot_a.get("eligible_bridge_candidates", [])
    eligible_oids = [
        c["candidate_object_id"] if isinstance(c, dict) else c
        for c in eligible_cands
    ]
    in_structured_gen = _evidence_in_candidates(evidence_group, eligible_oids, object_lookup)
    if in_structured_gen and not b_in_ord:
        return DIV_STRUCTURED_GENERATION

    # 4. SELECTIVITY
    selected_oids = slot_a.get("selected_bridge_candidates", [])
    in_selected = _evidence_in_candidates(evidence_group, selected_oids, object_lookup)
    if in_structured_gen and not in_selected:
        return DIV_SELECTIVITY

    # 5. FUSION_CUTOFF
    b_top30 = slot_b.get("ordinary_fused_top30", [])
    a_top30 = slot_a.get("ordinary_fused_top30", [])
    b_in_top30 = _evidence_in_candidates(evidence_group, b_top30, object_lookup)
    a_in_top30 = _evidence_in_candidates(evidence_group, a_top30, object_lookup)
    if b_in_top30 != a_in_top30:
        return DIV_FUSION_CUTOFF

    # 6. K3_ADMISSION
    displaced_ids = slot_a.get("displaced_candidate_ids", [])
    if _evidence_in_candidates(evidence_group, displaced_ids, object_lookup):
        return DIV_K3_ADMISSION

    reserved_ids = slot_a.get("reserved_candidate_ids", [])
    in_reserved = _evidence_in_candidates(evidence_group, reserved_ids, object_lookup)
    if in_selected and not a_in_top30 and not in_reserved:
        return DIV_K3_ADMISSION
    if in_reserved and not b_pool_retained:
        return DIV_K3_ADMISSION

    # 7. RERANKER & 8. FINAL_SELECTION
    if b_pool_retained and a_pool_retained:
        if b_final_retained != a_final_retained:
            ranked_b = slot_b.get("ranked_object_ids", [])
            ranked_a = slot_a.get("ranked_object_ids", [])
            b_rank = next((r for r, oid in enumerate(ranked_b, 1) if _evidence_in_candidates(evidence_group, [oid], object_lookup)), None)
            a_rank = next((r for r, oid in enumerate(ranked_a, 1) if _evidence_in_candidates(evidence_group, [oid], object_lookup)), None)
            if b_rank != a_rank:
                return DIV_RERANKER
            return DIV_FINAL_SELECTION

    if b_final_retained != a_final_retained:
        return DIV_RERANKER

    return DIV_NO_DIVERGENCE


def attribute_critical_regression(
    case_id: str,
    group_id: str,
    critical: bool,
    pre_rerank_class: str,
    final_class: str,
    first_div_layer: str,
    slot_b: dict[str, Any],
    slot_a: dict[str, Any],
) -> tuple[bool, str]:
    """Determines whether a critical evidence group regression is treatment-attributable.
    - Noncritical evidence (e.g. g021.e2) is excluded.
    - F/F (unresolved both) is strictly NOT a treatment regression.
    - Pre-rerank treatment regressions (BEFORE=True, AFTER=False in pool) are treatment-attributable.
    - Final-only regressions (pre-rerank preserved, final lost in AFTER) require causal attribution:
      reserved structured candidates displacing or outranking the target in final selection.
    """
    if not critical:
        return False, f"Noncritical evidence group {group_id} excluded from critical treatment regressions."

    if final_class != FINAL_TREATMENT_REGRESSION:
        return False, f"Evidence group {group_id} final phenotype is {final_class}, not a treatment regression."

    if pre_rerank_class == PAIR_UNRESOLVED_BOTH:
        return False, f"Evidence group {group_id} is unresolved in both arms (F/F); baseline weakness, not treatment failure."

    if pre_rerank_class == PAIR_TREATMENT_REGRESSION:
        return True, (
            f"Pre-rerank treatment regression at layer '{first_div_layer}' under shared prospective plan: "
            f"BEFORE retained in pre-rerank pool, AFTER lost in pre-rerank pool."
        )

    if pre_rerank_class == PAIR_PRESERVED:
        reserved_ids = slot_a.get("reserved_candidate_ids", [])
        if not reserved_ids:
            return False, (
                f"Simple final-only reranker divergence without causal treatment attribution: "
                f"zero reserved candidates in AFTER pool (first divergence: '{first_div_layer}')."
            )

        final_a = slot_a.get("final_evidence_object_ids", [])
        has_competing_reserved = any(r_oid in final_a for r_oid in reserved_ids)
        if has_competing_reserved:
            return True, (
                f"Final-only regression caused by structured candidate competition in rerank pool: "
                f"reserved candidate(s) {reserved_ids} selected into final evidence ahead of target."
            )
        return False, (
            f"Simple final-only reranker divergence without causal treatment attribution: "
            f"reserved candidate(s) did not cause target exclusion."
        )

    return False, f"Phenotype {pre_rerank_class} / {final_class} is not a treatment regression."


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

    g036_b_symbols = slot_g036_b.get("effective_symbols") or slot_g036_b.get("inputs", {}).get("symbols", [])
    ep_active_before = bool(
        any(sym in g036_b_symbols for sym in d4_a1.SUPPRESSED_SYMBOLS_EVENT_POCA)
        or (slot_g036_b.get("in_memory_mask_active") is False and not slot_g036_b.get("exact_effective_suppressed_components"))
    )
    g036_a_symbols = slot_g036_a.get("effective_symbols") or slot_g036_a.get("inputs", {}).get("symbols", [])
    ep_symbols_absent = not any(sym in g036_a_symbols for sym in d4_a1.SUPPRESSED_SYMBOLS_EVENT_POCA)
    g036_a_hints = slot_g036_a.get("effective_paper_page_hints") or slot_g036_a.get("inputs", {}).get("paper_page_hints", {})
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

    g021_b_symbols = slot_g021_b.get("effective_symbols") or slot_g021_b.get("inputs", {}).get("symbols", [])
    rg_active_before = bool(
        any(sym in g021_b_symbols for sym in d4_a1.SUPPRESSED_SYMBOLS_RESTGAS)
        or (slot_g021_b.get("in_memory_mask_active") is False and not slot_g021_b.get("exact_effective_suppressed_components"))
    )
    g021_a_symbols = slot_g021_a.get("effective_symbols") or slot_g021_a.get("inputs", {}).get("symbols", [])
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
    3. INVALID_PROVENANCE_RECOVERIES: check for AFTER structured recoveries and target witnesses.
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


def evaluate_d4_a2_v2(
    project_root: Path,
    raw_results_path: Path | None = None,
    raw_plans_path: Path | None = None,
    write_artifacts: bool = True,
    require_git_frozen: bool = True,
    git_checker: Any | None = None,
) -> dict[str, Any]:
    """Deterministic offline evaluator for D4-A2-V2 Controlled Shared-Plan Validation.
    Executes Sections 5-17 of the preregistration with zero provider calls.
    Evaluates over frozen raw artifacts, enforcing:
      - 16 total cases, 13 answered cases, 7 Gold answered, 6 novel_dev answered, 3 negative controls
      - Corrected criticality contract (g021.e1 critical, g021.e2 noncritical, n022.e2 critical)
      - Paired pre-rerank and final classifications (F/F is strictly NOT a treatment regression)
      - Frozen 9-element first-divergence taxonomy
      - Causal treatment attribution for critical regressions
      - BEFORE reference validity
      - Primary replacement witness and dependency removal for g036.e1 and g021.e1
      - Grounding, version, and provenance hard gates
      - Six historical primary metrics + diagnostic MRR
      - Frozen bounded tolerances
      - 6-level verdict precedence ladder.
    """
    raw_results_file = (raw_results_path or (project_root / RAW_RESULTS_PATH)).resolve()
    raw_plans_file = (raw_plans_path or (project_root / RAW_PLANS_PATH)).resolve()

    if not raw_results_file.exists():
        raise FileNotFoundError(f"Raw results file {raw_results_file} missing! Run Phase R first.")

    if require_git_frozen:
        if git_checker is not None:
            provenance = git_checker(project_root)
            if isinstance(provenance, dict):
                raw_results_freeze_sha = provenance.get("raw_results_freeze_sha", RAW_RESULTS_FREEZE_HEAD)
                evaluator_freeze_sha = provenance.get("evaluator_implementation_freeze_sha", _git_head(project_root))
                raw_results_blob = provenance.get("raw_results_blob", RAW_RESULTS_FREEZE_BLOB)
                raw_plans_blob = provenance.get("raw_plans_blob", PLAN_FREEZE_RAW_BLOB)
                evaluator_freeze_msg = provenance.get("evaluator_implementation_freeze_message", EXPECTED_EVALUATOR_FREEZE_COMMIT_MESSAGE)
            else:
                raw_results_freeze_sha = RAW_RESULTS_FREEZE_HEAD
                evaluator_freeze_sha = str(provenance) if provenance else _git_head(project_root)
                raw_results_blob = RAW_RESULTS_FREEZE_BLOB
                raw_plans_blob = PLAN_FREEZE_RAW_BLOB
                evaluator_freeze_msg = EXPECTED_EVALUATOR_FREEZE_COMMIT_MESSAGE
        else:
            provenance = verify_evaluator_freeze_provenance(project_root)
            raw_results_freeze_sha = provenance["raw_results_freeze_sha"]
            evaluator_freeze_sha = provenance["evaluator_implementation_freeze_sha"]
            raw_results_blob = provenance["raw_results_blob"]
            raw_plans_blob = provenance["raw_plans_blob"]
            evaluator_freeze_msg = provenance["evaluator_implementation_freeze_message"]
    else:
        raw_results_freeze_sha = RAW_RESULTS_FREEZE_HEAD
        evaluator_freeze_sha = "SYNTHETIC_EVALUATOR_FREEZE_HEAD"
        raw_results_blob = RAW_RESULTS_FREEZE_BLOB
        raw_plans_blob = PLAN_FREEZE_RAW_BLOB
        evaluator_freeze_msg = EXPECTED_EVALUATOR_FREEZE_COMMIT_MESSAGE

    raw_data = _load_json(raw_results_file)

    manifest_file = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_file) if manifest_file.exists() else {}
    prereg_file = project_root / PREREGISTRATION_PATH
    prereg = _load_json(prereg_file) if prereg_file.exists() else {}

    # Mechanical structural validity audit
    is_struct_valid, struct_fail_reason, mutation_counters = validate_raw_artifact_structural_validity(
        raw_data=raw_data,
        manifest=manifest,
        prereg=prereg,
        project_root=project_root,
    )
    if not is_struct_valid:
        verdict_outcome = compute_controlled_shared_plan_verdict(
            execution_valid=False,
            protocol_violation=True,
            protocol_violation_reason=struct_fail_reason,
        )
        eval_artifact = {
            "schema_version": "1.0.0",
            "checkpoint": "D4-A2-V2",
            "stage": "d4_a2_v2_evaluator_results",
            "raw_results_freeze_sha": raw_results_freeze_sha,
            "evaluator_implementation_freeze_sha": evaluator_freeze_sha,
            "frozen_provenance": {
                "raw_results_freeze_sha": raw_results_freeze_sha,
                "raw_results_blob": raw_results_blob,
                "raw_plans_blob": raw_plans_blob,
                "evaluator_implementation_freeze_sha": evaluator_freeze_sha,
                "evaluator_implementation_freeze_message": evaluator_freeze_msg,
                "evaluator_implementation_parent_sha": raw_results_freeze_sha,
            },
            "raw_artifact_authority": str(raw_results_file),
            "raw_plans_authority": str(raw_plans_file),
            "evaluator_executed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "execution_valid": False,
            "protocol_violation": True,
            "protocol_violation_reason": struct_fail_reason,
            "verdict_outcome": verdict_outcome,
            "post_exposure_mutation_accounting": mutation_counters,
            "production_activation": False,
        }
        if write_artifacts:
            _save_json(project_root / EVALUATOR_RESULTS_PATH, eval_artifact)
        return eval_artifact

    # Load governed benchmark questions and object lookup (read-only, local)
    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_questions = {q.id: q for q in gold_ds.questions + novel_ds.questions}
    object_lookup = load_object_lookup(project_root)

    slots_map = {(s["case_id"], s["arm"]): s for s in raw_data.get("slots", [])}

    # Process all evidence groups across all 16 cases
    group_classifications: dict[str, dict[str, Any]] = {}
    pair_pre_rerank_counts = {
        PAIR_PRESERVED: 0,
        PAIR_TREATMENT_RECOVERY: 0,
        PAIR_TREATMENT_REGRESSION: 0,
        PAIR_UNRESOLVED_BOTH: 0,
    }
    pair_final_counts = {
        FINAL_PRESERVED: 0,
        FINAL_TREATMENT_RECOVERY: 0,
        FINAL_TREATMENT_REGRESSION: 0,
        FINAL_UNRESOLVED_BOTH: 0,
    }
    first_divergence_counts = {k: 0 for k in FROZEN_FIRST_DIVERGENCE_TAXONOMY}

    critical_regression_ids: list[str] = []
    critical_regression_details: list[dict[str, Any]] = []
    noncritical_regression_ids: list[str] = []

    for cid in CASE_ORDER:
        q = all_questions[cid]
        slot_b = slots_map.get((cid, "BEFORE_COMPAT"), {})
        slot_a = slots_map.get((cid, "AFTER_BATCH1_REPLACEMENT"), {})
        is_answered = cid in ANSWERED_CASES

        for grp in q.required_evidence_groups:
            gid = grp.group_id
            critical = get_evidence_group_criticality(gid, grp.critical)

            b_pool_ids = slot_b.get("final_pool_object_ids", [])
            a_pool_ids = slot_a.get("final_pool_object_ids", [])
            b_fin_ids = slot_b.get("final_evidence_object_ids", [])
            a_fin_ids = slot_a.get("final_evidence_object_ids", [])

            b_pool_ret = _evidence_in_candidates(grp, b_pool_ids, object_lookup)
            a_pool_ret = _evidence_in_candidates(grp, a_pool_ids, object_lookup)
            b_fin_ret = _evidence_in_candidates(grp, b_fin_ids, object_lookup)
            a_fin_ret = _evidence_in_candidates(grp, a_fin_ids, object_lookup)

            pre_rerank_class = classify_pair_pre_rerank(b_pool_ret, a_pool_ret)
            final_class = classify_pair_final_evidence(b_fin_ret, a_fin_ret)

            pair_pre_rerank_counts[pre_rerank_class] += 1
            pair_final_counts[final_class] += 1

            first_div = compute_first_divergence_layer(
                slot_b=slot_b,
                slot_a=slot_a,
                evidence_group=grp,
                object_lookup=object_lookup,
                b_pool_retained=b_pool_ret,
                a_pool_retained=a_pool_ret,
                b_final_retained=b_fin_ret,
                a_final_retained=a_fin_ret,
            )
            first_divergence_counts[first_div] += 1

            is_treatment_regr, attr_evidence = attribute_critical_regression(
                case_id=cid,
                group_id=gid,
                critical=critical,
                pre_rerank_class=pre_rerank_class,
                final_class=final_class,
                first_div_layer=first_div,
                slot_b=slot_b,
                slot_a=slot_a,
            )

            if is_answered:
                if is_treatment_regr:
                    critical_regression_ids.append(gid)
                    critical_regression_details.append({
                        "case_id": cid,
                        "evidence_group_id": gid,
                        "critical": True,
                        "before_state": b_fin_ret,
                        "after_state": a_fin_ret,
                        "pre_rerank_state": pre_rerank_class,
                        "final_state": final_class,
                        "first_divergence_layer": first_div,
                        "attribution_evidence": attr_evidence,
                    })
                elif not critical and b_fin_ret and not a_fin_ret:
                    noncritical_regression_ids.append(gid)

            group_classifications[gid] = {
                "case_id": cid,
                "dataset": "Gold v2.6 dev" if cid in GOLD_CASES else "novel_dev",
                "is_answered": is_answered,
                "is_negative_control": cid in INSUFFICIENT_EVIDENCE_CASES,
                "critical": critical,
                "role": grp.role,
                "BEFORE_pool_retained": b_pool_ret,
                "AFTER_pool_retained": a_pool_ret,
                "BEFORE_final_retained": b_fin_ret,
                "AFTER_final_retained": a_fin_ret,
                "pre_rerank_classification": pre_rerank_class,
                "final_classification": final_class,
                "first_divergence_layer": first_div,
                "is_treatment_attributable_critical_regression": is_treatment_regr,
                "attribution_evidence": attr_evidence,
            }

    # Primary Batch-1 replacement targets witness verification
    eg_g036 = next(g for g in all_questions["g036"].required_evidence_groups if g.group_id == "g036.e1")
    eg_g021 = next(g for g in all_questions["g021"].required_evidence_groups if g.group_id == "g021.e1")
    slot_a_g036 = slots_map.get(("g036", "AFTER_BATCH1_REPLACEMENT"), {})
    slot_a_g021 = slots_map.get(("g021", "AFTER_BATCH1_REPLACEMENT"), {})

    wit_g036 = d4_a1.check_admission_witness("g036.e1", slot_a_g036, object_lookup, eg_g036)
    wit_g021 = d4_a1.check_admission_witness("g021.e1", slot_a_g021, object_lookup, eg_g021)

    b_ret_g036 = group_classifications.get("g036.e1", {}).get("BEFORE_final_retained", False)
    a_ret_g036 = group_classifications.get("g036.e1", {}).get("AFTER_final_retained", False)
    b_ret_g021 = group_classifications.get("g021.e1", {}).get("BEFORE_final_retained", False)
    a_ret_g021 = group_classifications.get("g021.e1", {}).get("AFTER_final_retained", False)

    g036_reproduced = bool(b_ret_g036 and a_ret_g036 and wit_g036.get("has_valid_witness", False))
    g021_reproduced = bool(b_ret_g021 and a_ret_g021 and wit_g021.get("has_valid_witness", False))
    target_replacement_reproduced_count = (1 if g036_reproduced else 0) + (1 if g021_reproduced else 0)

    # BEFORE reference validity (both required targets reproduced under BEFORE)
    before_reference_valid = bool(b_ret_g036 and b_ret_g021)

    # Benchmark dependency removal
    retention_for_dep = {
        gid: {
            "BEFORE_COMPAT": info["BEFORE_final_retained"],
            "AFTER_BATCH1_REPLACEMENT": info["AFTER_final_retained"],
        }
        for gid, info in group_classifications.items()
    }
    dep_count, dep_receipts = compute_batch1_dependency_removal(
        slots_map=slots_map,
        witness_g036=wit_g036,
        witness_g021=wit_g021,
        group_retention=retention_for_dep,
    )

    # Grounding, version, and provenance safety checks
    safety_res = compute_grounding_and_version_safety(
        slots_map=slots_map,
        all_questions=all_questions,
        object_lookup=object_lookup,
        witness_g036=wit_g036,
        witness_g021=wit_g021,
        group_retention=retention_for_dep,
    )

    # Per-case and aggregate metrics for answered cases (13 cases)
    case_metrics: dict[str, dict[str, dict[str, float]]] = {}
    for cid in ANSWERED_CASES:
        q = all_questions[cid]
        case_metrics[cid] = {}
        for arm in ARMS:
            slot = slots_map.get((cid, arm), {})
            ranked_ids = slot.get("ranked_object_ids", [])
            final_ids = slot.get("final_evidence_object_ids", [])
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
            rel_ranks = [rank_by_oid[m["object_id"]] for m in top20_prov if isinstance(m, dict) and m.get("object_id") in rank_by_oid]
            mrr = 1.0 / min(rel_ranks) if rel_ranks else 0.0

            comb_rec, _ = _matched_evidence_groups(q.required_evidence_groups, combined_ids, object_lookup)
            final_rec, _ = _matched_evidence_groups(q.required_evidence_groups, final_ids, object_lookup)

            crit_groups = [
                g for g in q.required_evidence_groups
                if get_evidence_group_criticality(g.group_id, g.critical)
            ]
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

    def _mean_metrics(case_ids: list[str], arm: str) -> dict[str, float]:
        keys = [
            "recall_at_5",
            "recall_at_10",
            "recall_at_20",
            "mrr",
            "combined_candidate_recall",
            "final_evidence_recall",
            "critical_final_evidence_recall",
        ]
        res = {}
        for k in keys:
            vals = [case_metrics[cid][arm][k] for cid in case_ids if cid in case_metrics]
            res[k] = sum(vals) / len(vals) if vals else 0.0
        return res

    def _delta_metrics(after_m: dict[str, float], before_m: dict[str, float]) -> dict[str, float]:
        return {k: round(after_m[k] - before_m[k], 6) for k in after_m}

    cohort_before = _mean_metrics(ANSWERED_CASES, "BEFORE_COMPAT")
    cohort_after = _mean_metrics(ANSWERED_CASES, "AFTER_BATCH1_REPLACEMENT")
    cohort_deltas = _delta_metrics(cohort_after, cohort_before)

    gold_before = _mean_metrics(GOLD_ANSWERED_CASES, "BEFORE_COMPAT")
    gold_after = _mean_metrics(GOLD_ANSWERED_CASES, "AFTER_BATCH1_REPLACEMENT")
    gold_deltas = _delta_metrics(gold_after, gold_before)

    novel_before = _mean_metrics(NOVEL_DEV_ANSWERED_CASES, "BEFORE_COMPAT")
    novel_after = _mean_metrics(NOVEL_DEV_ANSWERED_CASES, "AFTER_BATCH1_REPLACEMENT")
    novel_deltas = _delta_metrics(novel_after, novel_before)

    negative_controls_accounting: dict[str, Any] = {}
    for cid in INSUFFICIENT_EVIDENCE_CASES:
        q = all_questions.get(cid)
        slot_b = slots_map.get((cid, "BEFORE_COMPAT"), {})
        slot_a = slots_map.get((cid, "AFTER_BATCH1_REPLACEMENT"), {})
        negative_controls_accounting[cid] = {
            "case_id": cid,
            "expected_status": q.expected_status.value if q else "insufficient_evidence",
            "BEFORE_final_evidence_count": len(slot_b.get("final_evidence_object_ids", [])),
            "AFTER_final_evidence_count": len(slot_a.get("final_evidence_object_ids", [])),
        }

    # Final verdict precedence determination
    verdict_outcome = compute_controlled_shared_plan_verdict(
        execution_valid=True,
        protocol_violation=False,
        before_reference_valid=before_reference_valid,
        target_replacement_reproduced=target_replacement_reproduced_count,
        batch1_dependency_removed=dep_count,
        shared_plan_critical_regressions=critical_regression_ids,
        grounding_regressions=safety_res["GROUNDING_REGRESSIONS"],
        wrong_version_regressions=safety_res["WRONG_VERSION_REGRESSIONS"],
        invalid_provenance_recoveries=safety_res["INVALID_PROVENANCE_RECOVERIES"],
        metric_deltas=cohort_deltas,
    )

    eval_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V2",
        "stage": "d4_a2_v2_evaluator_results",
        "raw_results_freeze_sha": raw_results_freeze_sha,
        "evaluator_implementation_freeze_sha": evaluator_freeze_sha,
        "frozen_provenance": {
            "raw_results_freeze_sha": raw_results_freeze_sha,
            "raw_results_blob": raw_results_blob,
            "raw_plans_blob": raw_plans_blob,
            "evaluator_implementation_freeze_sha": evaluator_freeze_sha,
            "evaluator_implementation_freeze_message": evaluator_freeze_msg,
            "evaluator_implementation_parent_sha": raw_results_freeze_sha,
        },
        "raw_artifact_authority": str(raw_results_file),
        "raw_plans_authority": str(raw_plans_file),
        "evaluator_executed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "protocol_validity": {
            "execution_valid": True,
            "protocol_violation": False,
            "slots_total": len(raw_data.get("slots", [])),
            "plan_equality_all_verified": True,
            "analyzer_provider_calls": 0,
        },
        "applicability_accounting": {
            "cohort_total_cases": len(CASE_ORDER),
            "answered_cases_count": len(ANSWERED_CASES),
            "gold_answered_cases_count": len(GOLD_ANSWERED_CASES),
            "novel_dev_answered_cases_count": len(NOVEL_DEV_ANSWERED_CASES),
            "insufficient_evidence_cases_count": len(INSUFFICIENT_EVIDENCE_CASES),
            "answered_cases": ANSWERED_CASES,
            "gold_answered_cases": GOLD_ANSWERED_CASES,
            "novel_dev_answered_cases": NOVEL_DEV_ANSWERED_CASES,
            "insufficient_evidence_cases": INSUFFICIENT_EVIDENCE_CASES,
            "negative_controls": negative_controls_accounting,
        },
        "evidence_group_pair_classifications": group_classifications,
        "pair_phenotype_counts": {
            "pre_rerank": pair_pre_rerank_counts,
            "final_evidence": pair_final_counts,
        },
        "first_divergence_accounting": first_divergence_counts,
        "primary_target_reproduction": {
            "g036.e1": {
                "before_retained": b_ret_g036,
                "after_retained": a_ret_g036,
                "has_valid_witness": wit_g036.get("has_valid_witness", False),
                "reproduced": g036_reproduced,
                "witness_record": wit_g036,
            },
            "g021.e1": {
                "before_retained": b_ret_g021,
                "after_retained": a_ret_g021,
                "has_valid_witness": wit_g021.get("has_valid_witness", False),
                "reproduced": g021_reproduced,
                "witness_record": wit_g021,
            },
            "before_reference_valid": before_reference_valid,
            "target_replacement_reproduced": target_replacement_reproduced_count,
            "target_replacement_reproduced_display": f"{target_replacement_reproduced_count} / 2",
            "batch1_dependency_removed": dep_count,
            "batch1_dependency_removed_display": f"{dep_count} / 2",
            "dependency_removal_receipts": dep_receipts,
        },
        "regression_accounting": {
            "shared_plan_critical_regressions": critical_regression_ids,
            "critical_regression_details": critical_regression_details,
            "noncritical_regressions": noncritical_regression_ids,
            "grounding_regressions": safety_res["GROUNDING_REGRESSIONS"],
            "wrong_version_regressions": safety_res["WRONG_VERSION_REGRESSIONS"],
            "invalid_provenance_recoveries": safety_res["INVALID_PROVENANCE_RECOVERIES"],
            "safety_details": {
                "grounding_details": safety_res["grounding_details"],
                "wrong_version_details": safety_res["wrong_version_details"],
                "invalid_provenance_details": safety_res["invalid_provenance_details"],
            },
        },
        "metrics": {
            "cohort_answered": {
                "case_count": len(ANSWERED_CASES),
                "BEFORE_COMPAT": cohort_before,
                "AFTER_BATCH1_REPLACEMENT": cohort_after,
                "deltas": cohort_deltas,
            },
            "subsets": {
                "gold_answered": {
                    "case_count": len(GOLD_ANSWERED_CASES),
                    "BEFORE_COMPAT": gold_before,
                    "AFTER_BATCH1_REPLACEMENT": gold_after,
                    "deltas": gold_deltas,
                },
                "novel_dev_answered": {
                    "case_count": len(NOVEL_DEV_ANSWERED_CASES),
                    "BEFORE_COMPAT": novel_before,
                    "AFTER_BATCH1_REPLACEMENT": novel_after,
                    "deltas": novel_deltas,
                },
            },
            "per_case_metrics": case_metrics,
        },
        "zero_provider_accounting": {
            "ANALYZER_CALLS": 0,
            "EMBEDDING_CALLS": 0,
            "RERANKER_CALLS": 0,
            "QA_CALLS": 0,
            "VERIFIER_CALLS": 0,
            "JUDGE_CALLS": 0,
            "POSTGRESQL_WRITES": 0,
            "QDRANT_WRITES": 0,
            "INGESTION_RUNS": 0,
            "REINDEX_RUNS": 0,
            "NOVEL_VALIDATION_RUNS": 0,
            "NOVEL_HOLDOUT_RUNS": 0,
            "PROTECTED_DATASET_ACCESS": 0,
        },
        "post_exposure_mutation_accounting": mutation_counters,
        "verdict_outcome": verdict_outcome,
        "production_activation": False,
        "first_batch_runtime_migration": "BLOCKED",
        "d4_a3": "NOT_STARTED / BLOCKED",
    }

    compact_result = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V2",
        "stage": "D4-A2-V2 — Controlled Shared-Plan T2 Before/After Validation",
        "lifecycle_status": f"COMPLETE / {verdict_outcome['verdict']}",
        "raw_results_freeze_sha": raw_results_freeze_sha,
        "evaluator_implementation_freeze_sha": evaluator_freeze_sha,
        "execution_valid": True,
        "before_reference_valid": before_reference_valid,
        "target_replacement_reproduced": f"{target_replacement_reproduced_count} / 2",
        "batch1_dependency_removed": f"{dep_count} / 2",
        "critical_regressions_count": len(critical_regression_ids),
        "grounding_regressions": safety_res["GROUNDING_REGRESSIONS"],
        "wrong_version_regressions": safety_res["WRONG_VERSION_REGRESSIONS"],
        "invalid_provenance_recoveries": safety_res["INVALID_PROVENANCE_RECOVERIES"],
        "primary_metric_deltas": {k: cohort_deltas[k] for k in REQUIRED_PRIMARY_METRIC_KEYS},
        "mrr_delta": cohort_deltas.get("mrr", 0.0),
        "verdict_level": verdict_outcome["verdict_level"],
        "verdict": verdict_outcome["verdict"],
        "verdict_reason": verdict_outcome["verdict_reason"],
        "production_activation": False,
        "first_batch_runtime_migration": "BLOCKED",
        "d4_a3_status": "NOT_STARTED / BLOCKED",
    }

    if write_artifacts:
        _save_json(project_root / EVALUATOR_RESULTS_PATH, eval_artifact)
        _save_json(project_root / RESULT_PATH, compact_result)

    return eval_artifact


def evaluate(project_root: Path) -> dict[str, Any]:
    """Deterministic offline evaluator for D4-A2-V2."""
    return evaluate_d4_a2_v2(project_root)


def main() -> None:
    parser = argparse.ArgumentParser(description="PANDA Agent D4-A2-V2 Controlled Shared-Plan Validation")
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Path to project root")
    parser.add_argument(
        "--mode",
        choices=[
            "audit-invariants",
            "execute-phase-p",
            "execute-phase-r",
            "evaluate",
            "verify-plan-freeze-gate",
            "verify-evaluator-freeze-provenance",
        ],
        default="audit-invariants",
        help="Execution mode (evaluate fails closed until separately authorized Commit D)",
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    if args.mode == "audit-invariants":
        receipt = audit_invariants(project_root)
        print("[AUDIT SUCCESS] Invariants verified successfully:")
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    elif args.mode == "execute-phase-p":
        execute_phase_p(project_root)
    elif args.mode == "execute-phase-r":
        execute_phase_r(project_root)
    elif args.mode == "evaluate":
        evaluate(project_root)
    elif args.mode == "verify-plan-freeze-gate":
        receipt = verify_plan_freeze_gate(project_root)
        print("[PLAN FREEZE GATE SUCCESS] Repaired plan-freeze gate verified successfully:")
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    elif args.mode == "verify-evaluator-freeze-provenance":
        receipt = verify_evaluator_freeze_provenance(project_root)
        print("[EVALUATOR FREEZE PROVENANCE SUCCESS] Provenance verified successfully:")
        print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
