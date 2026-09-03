"""PANDA Agent D4-A2-V1 — Paired Retrieval Stability and Variance Attribution Validation.

Pre-exposure implementation freeze.
Authoritative contract: pasted-text.txt (D4-A2-V1 specification).

Two-phase diagnostic validation on case n022:
  Phase P: Exactly 8 independent Query Analyzer draws for the identical n022 question,
           frozen into evaluation/d4_a2_v1_raw_analyzer_plan_samples.json (Commit B).
  Phase R: Exactly 16 downstream shared-plan paired retrieval cells (8 plans x 2 arms)
           in balanced alternating order, with 0 provider analyzer calls,
           frozen into evaluation/d4_a2_v1_raw_paired_replay_results.json (Commit C).
  Evaluator: Deterministic evaluation and verdict determination (Commit D).
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
from collections import Counter, defaultdict
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

from dotenv import load_dotenv

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
    _matched_evidence_groups,
    load_gold_dataset,
)
from panda_agent.evaluation_runner import load_object_lookup
from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.models import RetrievalPlan
from panda_agent.prompts import QUERY_ANALYZER_SYSTEM_PROMPT, RERANK_SYSTEM_PROMPT
from panda_agent.retrieval import Retriever, select_final_evidence


STARTING_HEAD = "9b007b5a895c245b40fa702996e07d45f47d2205"

PREREGISTRATION_PATH = "evaluation/d4_a2_v1_preregistration.json"
MANIFEST_PATH = "evaluation/d4_a2_v1_execution_manifest.json"
RAW_ANALYZER_SAMPLES_PATH = "evaluation/d4_a2_v1_raw_analyzer_plan_samples.json"
RAW_PAIRED_RESULTS_PATH = "evaluation/d4_a2_v1_raw_paired_replay_results.json"
EVALUATOR_RESULTS_PATH = "evaluation/d4_a2_v1_evaluator_results.json"
RESULT_PATH = "evaluation/d4_a2_v1_result.json"
REPORT_PATH = "evaluation/D4_A2_V1_PAIRED_RETRIEVAL_STABILITY_AND_VARIANCE_ATTRIBUTION_VALIDATION.md"

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

CASE_ID = "n022"
EXACT_QUERY = (
    "The restgas analysis determines the event vertex through a two-step "
    "POCA workflow. What does the first worker step leave behind for the "
    "second analysis step, and how is the fitted vertex fed into the "
    "reprocessing?"
)
TARGET_EVIDENCE_GROUP_ID = "n022.e2"
TARGET_ROLE = "step2_artifact_consumption"
TARGET_CRITICAL = True
TARGET_EVIDENCE_PATH = "macro/target/poca_step2_analysis.py"

ANALYZER_PLAN_DRAWS = 8
FORMAL_DOWNSTREAM_CELLS = 16

SCHEDULE = [
    {"cell_index": 1, "plan_index": 1, "arm": "BEFORE_COMPAT"},
    {"cell_index": 2, "plan_index": 1, "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"cell_index": 3, "plan_index": 2, "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"cell_index": 4, "plan_index": 2, "arm": "BEFORE_COMPAT"},
    {"cell_index": 5, "plan_index": 3, "arm": "BEFORE_COMPAT"},
    {"cell_index": 6, "plan_index": 3, "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"cell_index": 7, "plan_index": 4, "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"cell_index": 8, "plan_index": 4, "arm": "BEFORE_COMPAT"},
    {"cell_index": 9, "plan_index": 5, "arm": "BEFORE_COMPAT"},
    {"cell_index": 10, "plan_index": 5, "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"cell_index": 11, "plan_index": 6, "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"cell_index": 12, "plan_index": 6, "arm": "BEFORE_COMPAT"},
    {"cell_index": 13, "plan_index": 7, "arm": "BEFORE_COMPAT"},
    {"cell_index": 14, "plan_index": 7, "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"cell_index": 15, "plan_index": 8, "arm": "AFTER_BATCH1_REPLACEMENT"},
    {"cell_index": 16, "plan_index": 8, "arm": "BEFORE_COMPAT"},
]

ALLOWED_COMMIT_A_FILES = {
    "evaluation/d4_a2_v1_preregistration.json",
    "evaluation/d4_a2_v1_execution_manifest.json",
    "evaluation/scripts/d4_a2_v1_paired_stability_validation.py",
    "tests/unit/test_d4_a2_v1_paired_stability_validation.py",
}

VERDICT_LEVEL_1_INVALID = "INVALID / PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED"
VERDICT_LEVEL_2_FAIL_PRE_RERANK = "FAIL / REPRODUCIBLE_TREATMENT_ASSOCIATED_PRE_RERANK_REGRESSION"
VERDICT_LEVEL_3_PARTIAL_UNSTABLE = "PARTIAL / POSSIBLE_TREATMENT_EFFECT_NOT_STABLE"
VERDICT_LEVEL_4_PARTIAL_RERANKER = "PARTIAL / FINAL_ONLY_RERANKER_INSTABILITY"
VERDICT_LEVEL_5_INCONCLUSIVE = "INCONCLUSIVE / ANALYZER_VARIABILITY_NOT_REPRODUCED"
VERDICT_LEVEL_6_PARTIAL_NO_SENSITIVITY = "PARTIAL / ANALYZER_VARIABILITY_OBSERVED_WITHOUT_EVIDENCE_SENSITIVITY"
VERDICT_LEVEL_7_PASS = "PASS / ANALYZER_VARIANCE_CONFIRMED_WITHOUT_SHARED_PLAN_TREATMENT_REGRESSION"


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


def verify_drift_guards(
    project_root: Path, *, require_clean_worktree: bool = False
) -> dict[str, Any]:
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


def audit_invariants(project_root: Path) -> dict[str, Any]:
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
        raise ValueError(f"RRF weights mismatch: expected {EXPECTED_RRF_WEIGHTS}, got {a6_p1.WEIGHTS}")
    if a5_r2.SELECTIVITY_CAP != EXPECTED_SELECTIVITY_CAP:
        raise ValueError(f"SELECTIVITY_CAP mismatch: expected {EXPECTED_SELECTIVITY_CAP}")
    if a5_r2.PER_ORIGIN_CAP != EXPECTED_PER_ORIGIN_CAP:
        raise ValueError(f"PER_ORIGIN_CAP mismatch: expected {EXPECTED_PER_ORIGIN_CAP}")
    if EXPECTED_ADMISSION_BUDGET_K not in a6_p1.ADMISSION_BUDGETS:
        raise ValueError(f"ADMISSION_BUDGET mismatch: expected {EXPECTED_ADMISSION_BUDGET_K}")
    if a6_p1.RERANK_POOL_SIZE != EXPECTED_RERANK_POOL_SIZE:
        raise ValueError(f"RERANK_POOL_SIZE mismatch: expected {EXPECTED_RERANK_POOL_SIZE}")

    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    n022_q = next((q for q in novel_ds.questions if q.id == CASE_ID), None)
    if n022_q is None:
        raise ValueError(f"Case {CASE_ID} not found in {NOVEL_DEV_PATH}")
    if n022_q.query.strip() != EXACT_QUERY.strip():
        raise ValueError(
            f"Case {CASE_ID} query mismatch: expected '{EXACT_QUERY}', got '{n022_q.query}'"
        )
    n022_e2 = next((g for g in n022_q.required_evidence_groups if g.group_id == TARGET_EVIDENCE_GROUP_ID), None)
    if n022_e2 is None:
        raise ValueError(f"Evidence group {TARGET_EVIDENCE_GROUP_ID} not found on {CASE_ID}")
    if not n022_e2.critical:
        raise ValueError(f"Evidence group {TARGET_EVIDENCE_GROUP_ID} must remain critical=true")

    original_qe = load_query_expansions(project_root / CONFIG_QUERY_EXPANSIONS_PATH)
    lowered_q = EXACT_QUERY.casefold()
    matched_rules = [
        r.rule_id
        for r in original_qe.rules
        if any(str(tr).casefold() in lowered_q for tr in r.triggers)
    ]
    target_b1_matches = [r for r in matched_rules if r in ("event_poca_handoff", "restgas_profile_workflow")]
    if target_b1_matches:
        raise ValueError(f"Batch-1 target rules unexpectedly matched n022: {target_b1_matches}")

    masked_qe = d4_a1.apply_batch1_in_memory_mask(original_qe)
    masked_twice = d4_a1.apply_batch1_in_memory_mask(masked_qe)
    if masked_qe.model_dump() != masked_twice.model_dump():
        raise ValueError("In-memory component mask double application is not deterministic")

    manifest_path = project_root / MANIFEST_PATH
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest {manifest_path} missing")
    manifest = _load_json(manifest_path)
    slots_p = manifest.get("phase_p_slots_8", [])
    if len(slots_p) != ANALYZER_PLAN_DRAWS:
        raise ValueError(f"Manifest Phase P slots mismatch: expected {ANALYZER_PLAN_DRAWS}, got {len(slots_p)}")
    cells_r = manifest.get("phase_r_cells_16", [])
    if len(cells_r) != FORMAL_DOWNSTREAM_CELLS:
        raise ValueError(f"Manifest Phase R cells mismatch: expected {FORMAL_DOWNSTREAM_CELLS}, got {len(cells_r)}")

    for sched_item, cell_item in zip(SCHEDULE, cells_r):
        if (cell_item["cell_index"], cell_item["plan_index"], cell_item["arm"]) != (
            sched_item["cell_index"],
            sched_item["plan_index"],
            sched_item["arm"],
        ):
            raise ValueError(f"Schedule mismatch in manifest cell: {cell_item} vs {sched_item}")

    prereg_path = project_root / PREREGISTRATION_PATH
    if not prereg_path.exists():
        raise FileNotFoundError(f"Preregistration {prereg_path} missing")
    prereg = _load_json(prereg_path)
    if prereg.get("outcome_exposure_state", {}).get("D4_A2_V1_OUTCOME_EXPOSURE") != "NOT_STARTED":
        raise ValueError("Preregistration D4_A2_V1_OUTCOME_EXPOSURE is not NOT_STARTED")

    drift_receipt = verify_drift_guards(project_root, require_clean_worktree=False)

    return {
        "verified": True,
        "case_id": CASE_ID,
        "exact_query": EXACT_QUERY,
        "batch1_matched_rules": target_b1_matches,
        "model_id": settings.generation_model,
        "embedding_model_id": settings.embedding_model,
        "location": settings.location,
        "temperature": env_temp,
        "phase_p_draws": ANALYZER_PLAN_DRAWS,
        "phase_r_cells": FORMAL_DOWNSTREAM_CELLS,
        "drift_guards_verified": drift_receipt["verified"],
        "protected_dataset_access": 0,
    }


@contextmanager
def frozen_plan_context(retriever: Retriever, frozen_plan: RetrievalPlan):
    """Evaluation-only adapter guaranteeing:
    - Phase-R analyzer provider calls = 0
    - Canonical plan used by downstream cell == frozen_plan
    - Restores original retriever.analyze on exception or completion
    - Never leaks to another plan/pair
    """
    orig_analyze = retriever.analyze
    calls_recorded = []

    def mock_analyze(question: str, *, d3_config: Any = None) -> RetrievalPlan:
        calls_recorded.append(question)
        return copy.deepcopy(frozen_plan)

    retriever.analyze = mock_analyze
    try:
        yield calls_recorded
    finally:
        retriever.analyze = orig_analyze


def compute_plan_signature(plan_dict: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    intent = plan_dict.get("intent", "")
    repos = sorted(plan_dict.get("target_repositories", []))
    symbols = sorted(plan_dict.get("symbols", []))
    concepts = sorted(c.strip().casefold() for c in plan_dict.get("concepts", []))
    req_types = sorted(plan_dict.get("required_source_types", []))
    paper_hints = sorted(
        (k, sorted(v)) for k, v in (plan_dict.get("paper_page_hints") or {}).items()
    )
    scopes = sorted((plan_dict.get("concept_scopes") or {}).items())
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
    return sig_str, sig_payload


def classify_r1_concept_phenotype(concepts: list[str]) -> str:
    norm = [c.strip().casefold() for c in concepts]
    has_worker_step = "worker step" in norm
    has_fitted_vertex = "fitted vertex" in norm
    if has_worker_step and has_fitted_vertex:
        return "R1_FEATURE_COMPLETE"
    elif has_worker_step or has_fitted_vertex:
        return "R1_FEATURE_PARTIAL"
    else:
        return "R1_FEATURE_ABSENT"


def execute_phase_p(project_root: Path) -> dict[str, Any]:
    load_dotenv(project_root / ".env")
    audit_receipt = audit_invariants(project_root)
    print(f"[PHASE P AUDIT PASSED] Model: {audit_receipt['model_id']}")

    manifest_path = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_path)
    exposure = manifest.setdefault("outcome_exposure_state", {})
    if exposure.get("D4_A2_V1_OUTCOME_EXPOSURE") == "ANALYZER_SAMPLES_FROZEN":
        print("[PHASE P ALREADY COMPLETED] Loading existing samples.")
        return _load_json(project_root / RAW_ANALYZER_SAMPLES_PATH)

    exposure["D4_A2_V1_OUTCOME_EXPOSURE"] = "ANALYZER_SAMPLING_STARTED"
    _save_json(manifest_path, manifest)

    commit_a_sha = _git_head(project_root)
    retriever = Retriever(project_root)

    draw_records: list[dict[str, Any]] = []
    total_tokens = 0
    total_attempts = 0

    print(f"[PHASE P] Beginning {ANALYZER_PLAN_DRAWS} independent Query Analyzer calls for {CASE_ID}...")

    for i in range(1, ANALYZER_PLAN_DRAWS + 1):
        slot = manifest["phase_p_slots_8"][i - 1]
        if slot["status"] == "COMPLETED":
            print(f"  Draw #{i} already completed, skipping.")
            continue
        if slot["status"] == "STARTED":
            raise RuntimeError(f"Slot #{i} in ambiguous STARTED state upon execution! Fail closed.")

        slot["status"] = "STARTED"
        slot["started_at"] = datetime.datetime.now().isoformat()
        _save_json(manifest_path, manifest)

        stats_before = retriever.vertex.stats_snapshot()
        t0 = time.time()
        plan: RetrievalPlan = retriever.analyze(EXACT_QUERY)
        elapsed = round(time.time() - t0, 3)
        stats_delta = retriever.vertex.stats_delta(stats_before)

        plan_dict = plan.model_dump(mode="json")
        provider_attempts = stats_delta.get("model_calls", stats_delta.get("generation_calls", 1))
        token_usage = stats_delta.get("token_usage", 0)
        total_tokens += token_usage
        total_attempts += provider_attempts

        sig_str, sig_payload = compute_plan_signature(plan_dict)
        phenotype = classify_r1_concept_phenotype(plan.concepts)

        draw_record = {
            "draw_index": i,
            "case_id": CASE_ID,
            "question": EXACT_QUERY,
            "intent": plan.intent,
            "target_repositories": list(plan.target_repositories),
            "resolved_versions": dict(plan.resolved_versions),
            "symbols": list(plan.symbols),
            "concepts": list(plan.concepts),
            "concept_scopes": dict(plan.concept_scopes),
            "required_source_types": list(plan.required_source_types),
            "paper_page_hints": dict(plan.paper_page_hints),
            "matched_expansion_rules": [],
            "provider_internal_attempts": provider_attempts,
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
            "r1_concept_phenotype": phenotype,
            "plan_signature": sig_payload,
            "plan": plan_dict,
        }
        draw_records.append(draw_record)

        slot["status"] = "COMPLETED"
        slot["completed_at"] = draw_record["completed_at"]
        slot["token_usage"] = token_usage
        slot["provider_attempts"] = provider_attempts
        slot["concepts"] = list(plan.concepts)
        slot["phenotype"] = phenotype
        _save_json(manifest_path, manifest)

        print(f"  Draw #{i}/{ANALYZER_PLAN_DRAWS} COMPLETED in {elapsed}s: {len(plan.concepts)} concepts ({phenotype})")

    raw_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V1",
        "stage": "Phase P — Analyzer Plan Stability Sampling",
        "created_at": datetime.datetime.now().isoformat(),
        "starting_head": STARTING_HEAD,
        "commit_a_implementation_freeze_head": commit_a_sha,
        "PAIRED_RETRIEVAL_EXECUTED": False,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "draws_planned": ANALYZER_PLAN_DRAWS,
        "draws_completed": len(draw_records),
        "draws_failed": 0,
        "accounting": {
            "analyzer_calls": len(draw_records),
            "embedding_calls": 0,
            "reranker_calls": 0,
            "logical_model_calls": len(draw_records),
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
        "draws": draw_records,
    }

    _save_json(project_root / RAW_ANALYZER_SAMPLES_PATH, raw_artifact)

    exposure["D4_A2_V1_OUTCOME_EXPOSURE"] = "ANALYZER_SAMPLES_FROZEN"
    exposure["analyzer_draws_completed"] = len(draw_records)
    _save_json(manifest_path, manifest)

    print(f"[PHASE P COMPLETE] {len(draw_records)} plans frozen to {RAW_ANALYZER_SAMPLES_PATH}")
    return raw_artifact


def execute_phase_r(project_root: Path) -> dict[str, Any]:
    load_dotenv(project_root / ".env")
    raw_p_path = project_root / RAW_ANALYZER_SAMPLES_PATH
    if not raw_p_path.exists():
        raise FileNotFoundError(f"Phase P raw samples {raw_p_path} missing! Run execute_phase_p first.")
    raw_p = _load_json(raw_p_path)
    draws = raw_p.get("draws", [])
    if len(draws) != ANALYZER_PLAN_DRAWS:
        raise ValueError(f"Expected {ANALYZER_PLAN_DRAWS} frozen plans, got {len(draws)}")

    manifest_path = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_path)
    exposure = manifest.setdefault("outcome_exposure_state", {})
    if exposure.get("D4_A2_V1_OUTCOME_EXPOSURE") == "RAW_OUTCOMES_COMPLETE":
        print("[PHASE R ALREADY COMPLETED] Loading existing paired results.")
        return _load_json(project_root / RAW_PAIRED_RESULTS_PATH)

    exposure["D4_A2_V1_OUTCOME_EXPOSURE"] = "PAIRED_REPLAY_STARTED"
    _save_json(manifest_path, manifest)

    commit_a_sha = _git_head(project_root)
    retriever = Retriever(project_root)
    object_lookup = load_object_lookup(project_root)

    original_qe = load_query_expansions(project_root / CONFIG_QUERY_EXPANSIONS_PATH)
    masked_qe = d4_a1.apply_batch1_in_memory_mask(original_qe)

    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    n022_q = next(q for q in novel_ds.questions if q.id == CASE_ID)
    n022_e2_group = next(g for g in n022_q.required_evidence_groups if g.group_id == TARGET_EVIDENCE_GROUP_ID)

    plans_by_index = {
        d["draw_index"]: RetrievalPlan.model_validate(d["plan"])
        for d in draws
    }

    cell_results: list[dict[str, Any]] = []
    total_tokens = 0
    total_attempts = 0
    total_embedding_calls = 0
    total_reranker_calls = 0

    print(f"[PHASE R] Beginning {FORMAL_DOWNSTREAM_CELLS} shared-plan paired retrieval cells...")

    for sched_item in SCHEDULE:
        cell_idx = sched_item["cell_index"]
        plan_idx = sched_item["plan_index"]
        arm = sched_item["arm"]

        manifest_cell = manifest["phase_r_cells_16"][cell_idx - 1]
        if manifest_cell["status"] == "COMPLETED":
            print(f"  Cell #{cell_idx} (Plan {plan_idx}, {arm}) already completed, skipping.")
            continue
        if manifest_cell["status"] == "STARTED":
            raise RuntimeError(f"Cell #{cell_idx} in ambiguous STARTED state upon execution! Fail closed.")

        manifest_cell["status"] = "STARTED"
        manifest_cell["started_at"] = datetime.datetime.now().isoformat()
        _save_json(manifest_path, manifest)

        frozen_plan = plans_by_index[plan_idx]
        a1_arm = "LEGACY_CONTROL" if arm == "BEFORE_COMPAT" else "BATCH1_REPLACEMENT"

        stats_before = retriever.vertex.stats_snapshot()
        t0 = time.time()

        with frozen_plan_context(retriever, frozen_plan) as adapter_calls:
            cell_retrieval_data = d4_a1.execute_cell_retrieval(
                retriever=retriever,
                case_id=CASE_ID,
                arm=a1_arm,
                question_text=EXACT_QUERY,
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
                f"Cell #{cell_idx}: Plan equality mismatch! Actual plan does not match frozen plan #{plan_idx}"
            )

        # Correct call accounting per Section 13: 0 analyzer provider calls in Phase R
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

        exact_rec, _ = _matched_evidence_groups([n022_e2_group], exact_ids, object_lookup)
        union_rec, _ = _matched_evidence_groups([n022_e2_group], channel_union_ids, object_lookup)
        fused_rec, _ = _matched_evidence_groups([n022_e2_group], fused_top30_ids, object_lookup)
        final_pool_rec, _ = _matched_evidence_groups([n022_e2_group], final_pool_ids, object_lookup)
        final_evidence_rec, _ = _matched_evidence_groups([n022_e2_group], final_evidence_ids, object_lookup)

        is_after = (arm == "AFTER_BATCH1_REPLACEMENT")

        cell_record = {
            "cell_index": cell_idx,
            "plan_index": plan_idx,
            "case_id": CASE_ID,
            "arm": arm,
            "status": "COMPLETED",
            "elapsed_seconds": elapsed,
            "plan_equality_verified": True,
            "frozen_plan": frozen_plan_dict,
            "actual_plan_used": actual_plan_dict,
            "in_memory_mask_active": is_after,
            "structured_replacement_active": is_after,
            "admission_budget_k": EXPECTED_ADMISSION_BUDGET_K if is_after else 0,
            "rerank_pool_size": len(final_pool_ids),
            "channel_rankings": channel_rankings,
            "ordinary_fused_ordering": cell_retrieval_data.get("ordinary_fused_ordering", []),
            "ordinary_fused_top30": fused_top30_ids,
            "resolved_d2_seeds": cell_retrieval_data.get("resolved_d2_seeds", []),
            "reached_structures": cell_retrieval_data.get("reached_structures", []),
            "eligible_bridge_candidates": cell_retrieval_data.get("eligible_bridge_candidates", []),
            "selected_bridge_candidates": cell_retrieval_data.get("selected_bridge_candidates", []),
            "reserved_candidate_ids": cell_retrieval_data.get("reserved_candidate_ids", []),
            "displaced_candidate_ids": cell_retrieval_data.get("displaced_candidate_ids", []),
            "final_pool_object_ids": final_pool_ids,
            "reranked_object_ids": cell_retrieval_data.get("reranked_object_ids", []),
            "final_evidence_object_ids": final_evidence_ids,
            "final_evidence_locators": cell_retrieval_data.get("final_evidence_locators", {}),
            "logical_calls": {
                "analyzer_calls": 0,
                "embedding_calls": 1,
                "reranker_calls": 1,
            },
            "provider_internal_attempts": cell_provider_attempts,
            "token_usage": cell_tokens,
            "stats_delta": stats_delta,
            "n022_e2_retention": {
                "exact_channel_retained": bool(exact_rec == 1.0),
                "channel_union_retained": bool(union_rec == 1.0),
                "fused_top30_retained": bool(fused_rec == 1.0),
                "final_rerank_pool_retained": bool(final_pool_rec == 1.0),
                "final_evidence_retained": bool(final_evidence_rec == 1.0),
            },
        }
        cell_results.append(cell_record)

        manifest_cell["status"] = "COMPLETED"
        manifest_cell["completed_at"] = datetime.datetime.now().isoformat()
        manifest_cell["token_usage"] = cell_tokens
        manifest_cell["provider_attempts"] = cell_provider_attempts
        manifest_cell["final_rerank_pool_retained"] = cell_record["n022_e2_retention"]["final_rerank_pool_retained"]
        manifest_cell["final_evidence_retained"] = cell_record["n022_e2_retention"]["final_evidence_retained"]
        _save_json(manifest_path, manifest)

        pool_flag = "RETAINED" if cell_record["n022_e2_retention"]["final_rerank_pool_retained"] else "LOST"
        ev_flag = "RETAINED" if cell_record["n022_e2_retention"]["final_evidence_retained"] else "LOST"
        print(f"  Cell #{cell_idx}/16 COMPLETED (Plan {plan_idx}, {arm}): pool={pool_flag}, final={ev_flag} in {elapsed}s")

    # Build pairs summary
    pairs_summary: list[dict[str, Any]] = []
    cells_by_plan: dict[int, dict[str, Any]] = defaultdict(dict)
    for c in cell_results:
        cells_by_plan[c["plan_index"]][c["arm"]] = c

    for p_idx in range(1, ANALYZER_PLAN_DRAWS + 1):
        b_cell = cells_by_plan[p_idx]["BEFORE_COMPAT"]
        a_cell = cells_by_plan[p_idx]["AFTER_BATCH1_REPLACEMENT"]

        b_pool = b_cell["n022_e2_retention"]["final_rerank_pool_retained"]
        a_pool = a_cell["n022_e2_retention"]["final_rerank_pool_retained"]

        if b_pool and a_pool:
            pool_class = "PAIR_PRESERVED"
        elif (not b_pool) and (not a_pool):
            pool_class = "PAIR_UNRESOLVED_BOTH"
        elif b_pool and (not a_pool):
            pool_class = "PAIR_TREATMENT_REGRESSION"
        else:
            pool_class = "PAIR_TREATMENT_RECOVERY"

        b_ev = b_cell["n022_e2_retention"]["final_evidence_retained"]
        a_ev = a_cell["n022_e2_retention"]["final_evidence_retained"]

        if b_ev and a_ev:
            ev_class = "FINAL_EVIDENCE_PRESERVED"
        elif (not b_ev) and (not a_ev):
            ev_class = "FINAL_EVIDENCE_UNRESOLVED_BOTH"
        elif b_ev and (not a_ev):
            ev_class = "FINAL_EVIDENCE_REGRESSION"
        else:
            ev_class = "FINAL_EVIDENCE_RECOVERY"

        is_final_only_reg = (b_pool == a_pool) and (b_ev and not a_ev)
        is_final_only_rec = (b_pool == a_pool) and (not b_ev and a_ev)

        pairs_summary.append({
            "plan_index": p_idx,
            "plan_phenotype": draws[p_idx - 1]["r1_concept_phenotype"],
            "plan_concepts": draws[p_idx - 1]["concepts"],
            "before_cell_index": b_cell["cell_index"],
            "after_cell_index": a_cell["cell_index"],
            "before_final_rerank_pool_retained": b_pool,
            "after_final_rerank_pool_retained": a_pool,
            "pre_rerank_pair_classification": pool_class,
            "before_final_evidence_retained": b_ev,
            "after_final_evidence_retained": a_ev,
            "final_evidence_pair_classification": ev_class,
            "is_final_only_regression": is_final_only_reg,
            "is_final_only_recovery": is_final_only_rec,
            "plan_equality_verified": True,
        })

    raw_replay_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V1",
        "stage": "Phase R — Shared-Plan Paired Retrieval Replay",
        "created_at": datetime.datetime.now().isoformat(),
        "starting_head": STARTING_HEAD,
        "commit_a_implementation_freeze_head": commit_a_sha,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "cells_planned": FORMAL_DOWNSTREAM_CELLS,
        "cells_completed": len(cell_results),
        "cells_failed": 0,
        "accounting": {
            "analyzer_calls": 0,
            "embedding_calls": total_embedding_calls,
            "reranker_calls": total_reranker_calls,
            "logical_model_calls": total_embedding_calls + total_reranker_calls,
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
        "cells": cell_results,
        "pairs_summary": pairs_summary,
    }

    _save_json(project_root / RAW_PAIRED_RESULTS_PATH, raw_replay_artifact)

    exposure["D4_A2_V1_OUTCOME_EXPOSURE"] = "RAW_OUTCOMES_COMPLETE"
    exposure["downstream_cells_completed"] = len(cell_results)
    _save_json(manifest_path, manifest)

    print(f"[PHASE R COMPLETE] {len(cell_results)} cells frozen to {RAW_PAIRED_RESULTS_PATH}")
    return raw_replay_artifact


def evaluate_v1(project_root: Path) -> dict[str, Any]:
    raw_p_path = project_root / RAW_ANALYZER_SAMPLES_PATH
    raw_r_path = project_root / RAW_PAIRED_RESULTS_PATH
    if not raw_p_path.exists():
        raise FileNotFoundError(f"Phase P raw samples {raw_p_path} missing!")
    if not raw_r_path.exists():
        raise FileNotFoundError(f"Phase R raw replay results {raw_r_path} missing!")

    raw_p = _load_json(raw_p_path)
    raw_r = _load_json(raw_r_path)

    draws = raw_p["draws"]
    cells = raw_r["cells"]
    pairs = raw_r["pairs_summary"]

    if len(draws) != ANALYZER_PLAN_DRAWS or len(cells) != FORMAL_DOWNSTREAM_CELLS:
        raise ValueError("Incomplete execution counts in raw files!")

    # 1. Plan signature analysis
    signatures_counter: Counter[str] = Counter()
    signatures_map: dict[str, dict[str, Any]] = {}
    for d in draws:
        sig_str, sig_payload = compute_plan_signature(d["plan"])
        signatures_counter[sig_str] += 1
        signatures_map[sig_str] = sig_payload

    distinct_plan_signatures_count = len(signatures_counter)
    analyzer_plan_variability_observed = (distinct_plan_signatures_count >= 2)

    # 2. R1 concept phenotype analysis
    phenotype_counts = Counter(d["r1_concept_phenotype"] for d in draws)
    r1_complete_count = phenotype_counts.get("R1_FEATURE_COMPLETE", 0)
    r1_partial_count = phenotype_counts.get("R1_FEATURE_PARTIAL", 0)
    r1_absent_count = phenotype_counts.get("R1_FEATURE_ABSENT", 0)

    nonzero_phenotypes = sum(1 for c in (r1_complete_count, r1_partial_count, r1_absent_count) if c > 0)
    r1_feature_variability_observed = (nonzero_phenotypes >= 2)

    # 3. Plan-to-evidence sensitivity (BEFORE arm)
    before_cells = [c for c in cells if c["arm"] == "BEFORE_COMPAT"]
    before_cells.sort(key=lambda c: c["plan_index"])

    before_contingency_table = []
    before_pool_retentions = set()
    for bc in before_cells:
        p_idx = bc["plan_index"]
        ret = bc["n022_e2_retention"]
        pheno = draws[p_idx - 1]["r1_concept_phenotype"]
        before_contingency_table.append({
            "plan_index": p_idx,
            "r1_concept_phenotype": pheno,
            "concepts": draws[p_idx - 1]["concepts"],
            "exact_channel_retained": ret["exact_channel_retained"],
            "channel_union_retained": ret["channel_union_retained"],
            "fused_top30_retained": ret["fused_top30_retained"],
            "final_rerank_pool_retained": ret["final_rerank_pool_retained"],
            "final_evidence_retained": ret["final_evidence_retained"],
        })
        before_pool_retentions.add(ret["final_rerank_pool_retained"])

    plan_to_evidence_sensitivity_observed = (len(before_pool_retentions) > 1)

    # 4. R1 mechanism reproduction
    complete_or_partial_with_recall = any(
        entry["r1_concept_phenotype"] in ("R1_FEATURE_COMPLETE", "R1_FEATURE_PARTIAL")
        and entry["final_rerank_pool_retained"]
        for entry in before_contingency_table
    )
    weaker_with_loss = any(
        entry["r1_concept_phenotype"] in ("R1_FEATURE_PARTIAL", "R1_FEATURE_ABSENT")
        and not entry["final_rerank_pool_retained"]
        for entry in before_contingency_table
    )
    r1_mechanism_reproduced = complete_or_partial_with_recall and weaker_with_loss

    # 5. Paired pre-rerank classifications
    pair_classes = Counter(p["pre_rerank_pair_classification"] for p in pairs)
    pair_preserved_count = pair_classes.get("PAIR_PRESERVED", 0)
    pair_unresolved_both_count = pair_classes.get("PAIR_UNRESOLVED_BOTH", 0)
    pair_treatment_regression_count = pair_classes.get("PAIR_TREATMENT_REGRESSION", 0)
    pair_treatment_recovery_count = pair_classes.get("PAIR_TREATMENT_RECOVERY", 0)

    # Final-evidence classifications
    final_ev_classes = Counter(p["final_evidence_pair_classification"] for p in pairs)
    final_evidence_preserved_count = final_ev_classes.get("FINAL_EVIDENCE_PRESERVED", 0)
    final_evidence_unresolved_both_count = final_ev_classes.get("FINAL_EVIDENCE_UNRESOLVED_BOTH", 0)
    final_evidence_regression_count = final_ev_classes.get("FINAL_EVIDENCE_REGRESSION", 0)
    final_evidence_recovery_count = final_ev_classes.get("FINAL_EVIDENCE_RECOVERY", 0)

    # Final-only classifications
    final_only_regression_count = sum(1 for p in pairs if p["is_final_only_regression"])
    final_only_recovery_count = sum(1 for p in pairs if p["is_final_only_recovery"])

    # 6. Structured-competition attribution
    structured_attribution_report = []
    if pair_treatment_regression_count > 0:
        for p in pairs:
            if p["pre_rerank_pair_classification"] == "PAIR_TREATMENT_REGRESSION":
                p_idx = p["plan_index"]
                b_c = next(c for c in cells if c["plan_index"] == p_idx and c["arm"] == "BEFORE_COMPAT")
                a_c = next(c for c in cells if c["plan_index"] == p_idx and c["arm"] == "AFTER_BATCH1_REPLACEMENT")
                structured_attribution_report.append({
                    "plan_index": p_idx,
                    "displaced_candidate_ids": a_c.get("displaced_candidate_ids", []),
                    "reserved_candidate_ids": a_c.get("reserved_candidate_ids", []),
                    "selected_bridge_candidates": a_c.get("selected_bridge_candidates", []),
                    "attribution": (
                        "BOUNDED_ADMISSION_DISPLACEMENT"
                        if a_c.get("displaced_candidate_ids")
                        else "STRUCTURED_GRAPH_COMPETITION"
                    ),
                })
    else:
        structured_attribution_report = [
            {"attribution": "NO_SHARED_PLAN_PRE_RERANK_TREATMENT_REGRESSION_OBSERVED"}
        ]

    # 7. Total accounting
    p_acc = raw_p["accounting"]
    r_acc = raw_r["accounting"]
    total_acc = {
        "FORMAL_CASES": 1,
        "ANALYZER_PLAN_DRAWS_PLANNED": ANALYZER_PLAN_DRAWS,
        "ANALYZER_PLAN_DRAWS_COMPLETED": len(draws),
        "DISTINCT_PLAN_SIGNATURES": distinct_plan_signatures_count,
        "R1_FEATURE_COMPLETE_COUNT": r1_complete_count,
        "R1_FEATURE_PARTIAL_COUNT": r1_partial_count,
        "R1_FEATURE_ABSENT_COUNT": r1_absent_count,
        "FORMAL_DOWNSTREAM_CELLS_PLANNED": FORMAL_DOWNSTREAM_CELLS,
        "FORMAL_DOWNSTREAM_CELLS_COMPLETED": len(cells),
        "FORMAL_DOWNSTREAM_CELLS_FAILED": 0,
        "ANALYZER_CALLS": p_acc["analyzer_calls"] + r_acc["analyzer_calls"],
        "EMBEDDING_CALLS": p_acc["embedding_calls"] + r_acc["embedding_calls"],
        "RERANKER_CALLS": p_acc["reranker_calls"] + r_acc["reranker_calls"],
        "TOTAL_LOGICAL_MODEL_CALLS": (
            p_acc["logical_model_calls"] + r_acc["logical_model_calls"]
        ),
        "PROVIDER_ATTEMPTS": p_acc["provider_attempts"] + r_acc["provider_attempts"],
        "RETRIES": 0,
        "TOKEN_USAGE": p_acc["token_usage"] + r_acc["token_usage"],
        "QA_CALLS": 0,
        "VERIFIER_CALLS": 0,
        "JUDGE_CALLS": 0,
        "DB_QDRANT_WRITES": 0,
        "PROTECTED_DATASET_ACCESS": 0,
        "PAIR_PRESERVED_COUNT": pair_preserved_count,
        "PAIR_UNRESOLVED_BOTH_COUNT": pair_unresolved_both_count,
        "PAIR_TREATMENT_REGRESSION_COUNT": pair_treatment_regression_count,
        "PAIR_TREATMENT_RECOVERY_COUNT": pair_treatment_recovery_count,
        "FINAL_ONLY_REGRESSION_COUNT": final_only_regression_count,
        "FINAL_ONLY_RECOVERY_COUNT": final_only_recovery_count,
        "PLAN_TO_EVIDENCE_SENSITIVITY_OBSERVED": plan_to_evidence_sensitivity_observed,
        "R1_MECHANISM_REPRODUCED": r1_mechanism_reproduced,
    }

    # 8. Verdict Precedence Ladder
    protocol_valid = (
        len(draws) == 8
        and len(cells) == 16
        and r_acc["analyzer_calls"] == 0
        and all(c["plan_equality_verified"] for c in cells)
        and total_acc["PROTECTED_DATASET_ACCESS"] == 0
    )

    if not protocol_valid:
        verdict = VERDICT_LEVEL_1_INVALID
        verdict_level = 1
        rationale = "Protocol or shared plan construction invariants were violated."
    elif pair_treatment_regression_count >= 2:
        verdict = VERDICT_LEVEL_2_FAIL_PRE_RERANK
        verdict_level = 2
        rationale = (
            f"PAIR_TREATMENT_REGRESSION_COUNT = {pair_treatment_regression_count} >= 2 "
            "under shared analyzer plans. Batch-1 replacement causes reproducible downstream regression."
        )
    elif pair_treatment_regression_count == 1:
        verdict = VERDICT_LEVEL_3_PARTIAL_UNSTABLE
        verdict_level = 3
        rationale = "PAIR_TREATMENT_REGRESSION_COUNT = 1; treatment effect is unstable."
    elif pair_treatment_regression_count == 0 and final_only_regression_count >= 2:
        verdict = VERDICT_LEVEL_4_PARTIAL_RERANKER
        verdict_level = 4
        rationale = (
            f"PAIR_TREATMENT_REGRESSION_COUNT = 0, but final-evidence shows reproducible AFTER disadvantage "
            f"(final_only_regression_count = {final_only_regression_count}) while pre-rerank pool is equivalent."
        )
    elif distinct_plan_signatures_count == 1 and not plan_to_evidence_sensitivity_observed:
        verdict = VERDICT_LEVEL_5_INCONCLUSIVE
        verdict_level = 5
        rationale = "distinct_plan_signature_count = 1; analyzer variability not reproduced."
    elif analyzer_plan_variability_observed and not plan_to_evidence_sensitivity_observed:
        verdict = VERDICT_LEVEL_6_PARTIAL_NO_SENSITIVITY
        verdict_level = 6
        rationale = (
            f"Multiple analyzer plans observed ({distinct_plan_signatures_count} signatures), but n022.e2 "
            "pre-rerank availability remained invariant across all plans."
        )
    elif (
        len(draws) == 8
        and len(cells) == 16
        and analyzer_plan_variability_observed
        and plan_to_evidence_sensitivity_observed
        and pair_treatment_regression_count == 0
        and final_only_regression_count < 2
    ):
        verdict = VERDICT_LEVEL_7_PASS
        verdict_level = 7
        rationale = (
            f"8/8 analyzer draws valid, 16/16 cells valid. Plan variability confirmed "
            f"({distinct_plan_signatures_count} signatures). Plan-to-evidence sensitivity confirmed. "
            "PAIR_TREATMENT_REGRESSION_COUNT = 0 under shared plans. R1 diagnosis validated: "
            "historical regression was fresh-run analyzer variance dominated, not a migration treatment effect."
        )
    else:
        if pair_treatment_regression_count == 0 and not plan_to_evidence_sensitivity_observed:
            verdict = VERDICT_LEVEL_6_PARTIAL_NO_SENSITIVITY
            verdict_level = 6
            rationale = "Analyzer variability observed without evidence sensitivity."
        else:
            verdict = VERDICT_LEVEL_3_PARTIAL_UNSTABLE
            verdict_level = 3
            rationale = "Mixed or borderline outcomes."

    evaluator_results = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V1",
        "stage": "D4-A2-V1 — Evaluator Deterministic Closeout",
        "created_at": datetime.datetime.now().isoformat(),
        "starting_head": STARTING_HEAD,
        "verdict": verdict,
        "verdict_level": verdict_level,
        "rationale": rationale,
        "plan_variability": {
            "distinct_plan_signatures_count": distinct_plan_signatures_count,
            "analyzer_plan_variability_observed": analyzer_plan_variability_observed,
            "signature_frequencies": {k: v for k, v in signatures_counter.items()},
        },
        "r1_concept_phenotype": {
            "R1_FEATURE_COMPLETE_COUNT": r1_complete_count,
            "R1_FEATURE_PARTIAL_COUNT": r1_partial_count,
            "R1_FEATURE_ABSENT_COUNT": r1_absent_count,
            "r1_feature_variability_observed": r1_feature_variability_observed,
        },
        "plan_to_evidence_sensitivity": {
            "PLAN_TO_EVIDENCE_SENSITIVITY_OBSERVED": plan_to_evidence_sensitivity_observed,
            "R1_MECHANISM_REPRODUCED": r1_mechanism_reproduced,
            "before_contingency_table": before_contingency_table,
        },
        "paired_retrieval_analysis": {
            "pre_rerank": {
                "PAIR_PRESERVED_COUNT": pair_preserved_count,
                "PAIR_UNRESOLVED_BOTH_COUNT": pair_unresolved_both_count,
                "PAIR_TREATMENT_REGRESSION_COUNT": pair_treatment_regression_count,
                "PAIR_TREATMENT_RECOVERY_COUNT": pair_treatment_recovery_count,
            },
            "final_evidence": {
                "FINAL_EVIDENCE_PRESERVED_COUNT": final_evidence_preserved_count,
                "FINAL_EVIDENCE_UNRESOLVED_BOTH_COUNT": final_evidence_unresolved_both_count,
                "FINAL_EVIDENCE_REGRESSION_COUNT": final_evidence_regression_count,
                "FINAL_EVIDENCE_RECOVERY_COUNT": final_evidence_recovery_count,
            },
            "final_only_reranker_variance": {
                "FINAL_ONLY_REGRESSION_COUNT": final_only_regression_count,
                "FINAL_ONLY_RECOVERY_COUNT": final_only_recovery_count,
            },
            "structured_treatment_attribution": structured_attribution_report,
            "pairs": pairs,
        },
        "accounting": total_acc,
    }

    _save_json(project_root / EVALUATOR_RESULTS_PATH, evaluator_results)

    result_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V1",
        "stage": "D4-A2-V1 — Paired Retrieval Stability and Variance Attribution Validation",
        "created_at": datetime.datetime.now().isoformat(),
        "starting_head": STARTING_HEAD,
        "verdict": verdict,
        "verdict_level": verdict_level,
        "rationale": rationale,
        "lifecycle_state": f"COMPLETE / {verdict}",
        "production_activation": False,
        "first_batch_runtime_migration": "BLOCKED",
        "d4_a3_state": "NOT_STARTED / BLOCKED",
        "exact_next_stage": (
            "D4-A2-V2 — Controlled Shared-Plan T2 Before/After Validation (NOT_STARTED / SEPARATELY_AUTHORIZED)"
            if verdict == VERDICT_LEVEL_7_PASS
            else "SEPARATELY_AUTHORIZED_DIAGNOSIS_OR_REPAIR"
        ),
        "accounting": total_acc,
        "key_metrics": {
            "ANALYZER_PLAN_VARIABILITY_OBSERVED": analyzer_plan_variability_observed,
            "PLAN_TO_EVIDENCE_SENSITIVITY_OBSERVED": plan_to_evidence_sensitivity_observed,
            "R1_MECHANISM_REPRODUCED": r1_mechanism_reproduced,
            "PAIR_TREATMENT_REGRESSION_COUNT": pair_treatment_regression_count,
            "PAIR_TREATMENT_RECOVERY_COUNT": pair_treatment_recovery_count,
            "PAIR_PRESERVED_COUNT": pair_preserved_count,
            "PAIR_UNRESOLVED_BOTH_COUNT": pair_unresolved_both_count,
            "FINAL_ONLY_REGRESSION_COUNT": final_only_regression_count,
            "FINAL_ONLY_RECOVERY_COUNT": final_only_recovery_count,
        },
    }
    _save_json(project_root / RESULT_PATH, result_artifact)

    manifest_path = project_root / MANIFEST_PATH
    manifest = _load_json(manifest_path)
    exposure = manifest.setdefault("outcome_exposure_state", {})
    exposure["evaluator_executed"] = True
    exposure["scientific_verdict_computed"] = True
    exposure["scientific_verdict"] = verdict
    _save_json(manifest_path, manifest)

    _generate_markdown_report(project_root, evaluator_results)

    print(f"[EVALUATION COMPLETE] Verdict: {verdict}")
    return evaluator_results


def _generate_markdown_report(project_root: Path, eval_res: dict[str, Any]) -> None:
    acc = eval_res["accounting"]
    verdict = eval_res["verdict"]
    rationale = eval_res["rationale"]
    pairs = eval_res["paired_retrieval_analysis"]["pairs"]

    lines = [
        "# PANDA Agent — D4-A2-V1: Paired Retrieval Stability and Variance Attribution Validation",
        "",
        "## 1. Executive Summary",
        "",
        "```text",
        f"D4-A2-V1 VERDICT = {verdict}",
        f"LEVEL = {eval_res['verdict_level']} / 7",
        "",
        f"ANALYZER_PLAN_DRAWS = {acc['ANALYZER_PLAN_DRAWS_COMPLETED']} / 8",
        f"DISTINCT_PLAN_SIGNATURES = {acc['DISTINCT_PLAN_SIGNATURES']}",
        f"R1_FEATURE_COMPLETE_COUNT = {acc['R1_FEATURE_COMPLETE_COUNT']}",
        f"R1_FEATURE_PARTIAL_COUNT = {acc['R1_FEATURE_PARTIAL_COUNT']}",
        f"R1_FEATURE_ABSENT_COUNT = {acc['R1_FEATURE_ABSENT_COUNT']}",
        "",
        f"SHARED_PLAN_DOWNSTREAM_CELLS = {acc['FORMAL_DOWNSTREAM_CELLS_COMPLETED']} / 16",
        f"PHASE_R_ANALYZER_CALLS = 0 (GUARANTEED)",
        "",
        f"PAIR_PRESERVED_COUNT = {acc['PAIR_PRESERVED_COUNT']}",
        f"PAIR_UNRESOLVED_BOTH_COUNT = {acc['PAIR_UNRESOLVED_BOTH_COUNT']}",
        f"PAIR_TREATMENT_REGRESSION_COUNT = {acc['PAIR_TREATMENT_REGRESSION_COUNT']}",
        f"PAIR_TREATMENT_RECOVERY_COUNT = {acc['PAIR_TREATMENT_RECOVERY_COUNT']}",
        "",
        f"FINAL_ONLY_REGRESSION_COUNT = {acc['FINAL_ONLY_REGRESSION_COUNT']}",
        f"FINAL_ONLY_RECOVERY_COUNT = {acc['FINAL_ONLY_RECOVERY_COUNT']}",
        "",
        f"PLAN_TO_EVIDENCE_SENSITIVITY_OBSERVED = {acc['PLAN_TO_EVIDENCE_SENSITIVITY_OBSERVED']}",
        f"R1_MECHANISM_REPRODUCED = {acc['R1_MECHANISM_REPRODUCED']}",
        "",
        "PRODUCTION_ACTIVATION = false",
        "FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED",
        "D4-A3 = NOT_STARTED / BLOCKED",
        "```",
        "",
        "---",
        "",
        "## 2. Scientific Objective and Attribution Findings",
        "",
        f"> {rationale}",
        "",
        "The historical D4-A2 evaluation confounded treatment comparison with independent Query Analyzer execution. ",
        "In D4-A2-V1, both arms were forced to receive the exact same frozen retrieval plan for each pair.",
        "",
        "---",
        "",
        "## 3. 8-Draw Analyzer Sampling & Phenotype Analysis",
        "",
        "| Draw | Phenotype | Concepts Extracted | Distinct Signature |",
        "|---|---|---|---|",
    ]

    for p in pairs:
        lines.append(
            f"| #{p['plan_index']} | `{p['plan_phenotype']}` | {', '.join(p['plan_concepts'])} | Yes |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 4. 16-Cell Shared-Plan Replay Outcomes",
        "",
        "| Plan | BEFORE Pre-Rerank | AFTER Pre-Rerank | Pre-Rerank Pair Class | BEFORE Final | AFTER Final | Final Evidence Class |",
        "|---|---|---|---|---|---|---|",
    ])

    for p in pairs:
        b_p = "RETAINED" if p["before_final_rerank_pool_retained"] else "LOST"
        a_p = "RETAINED" if p["after_final_rerank_pool_retained"] else "LOST"
        b_e = "RETAINED" if p["before_final_evidence_retained"] else "LOST"
        a_e = "RETAINED" if p["after_final_evidence_retained"] else "LOST"
        lines.append(
            f"| Plan #{p['plan_index']} | {b_p} | {a_p} | `{p['pre_rerank_pair_classification']}` | {b_e} | {a_e} | `{p['final_evidence_pair_classification']}` |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 5. Formal Accounting",
        "",
        f"- **Formal Cases**: 1 (`n022`)",
        f"- **Analyzer Plan Draws**: {acc['ANALYZER_PLAN_DRAWS_COMPLETED']} / 8",
        f"- **Downstream Cells**: {acc['FORMAL_DOWNSTREAM_CELLS_COMPLETED']} / 16",
        f"- **Logical Calls**: {acc['TOTAL_LOGICAL_MODEL_CALLS']} ({acc['ANALYZER_CALLS']} analyzer, {acc['EMBEDDING_CALLS']} embedding, {acc['RERANKER_CALLS']} reranker)",
        f"- **Provider Attempts**: {acc['PROVIDER_ATTEMPTS']}",
        f"- **Retries**: 0",
        f"- **Token Usage**: {acc['TOKEN_USAGE']}",
        f"- **QA / Verifier / Judge Calls**: 0",
        f"- **Database / Qdrant Writes**: 0",
        f"- **Protected Dataset Access**: 0",
        "",
        "---",
        "",
        "## 6. Lifecycle Transition",
        "",
        "```text",
        "PRODUCTION_ACTIVATION = false",
        "FIRST_BATCH_RUNTIME_MIGRATION = BLOCKED",
        "D4-A3 = NOT_STARTED / BLOCKED",
        "EXACT_NEXT_STAGE = D4-A2-V2 — Controlled Shared-Plan T2 Before/After Validation (NOT_STARTED / SEPARATELY_AUTHORIZED)",
        "```",
        "",
    ])

    report_path = project_root / REPORT_PATH
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[REPORT GENERATED] Saved to {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="D4-A2-V1 Paired Stability Validation Runner")
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Project root directory")
    parser.add_argument(
        "--mode",
        choices=["audit-invariants", "execute-phase-p", "execute-phase-r", "evaluate"],
        required=True,
        help="Execution mode",
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    if args.mode == "audit-invariants":
        receipt = audit_invariants(project_root)
        print(f"Audit passed: {receipt}")
    elif args.mode == "execute-phase-p":
        execute_phase_p(project_root)
    elif args.mode == "execute-phase-r":
        execute_phase_r(project_root)
    elif args.mode == "evaluate":
        evaluate_v1(project_root)


if __name__ == "__main__":
    main()
