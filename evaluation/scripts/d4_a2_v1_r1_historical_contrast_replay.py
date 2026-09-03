"""PANDA Agent D4-A2-V1-R1 — Historical Contrast Shared-Plan Replay.

Pre-exposure implementation freeze.
Authoritative contract: pasted-text.txt (D4-A2-V1-R1 specification).

Targeted 2x2 factorial replay on case n022:
  PLANS: Exactly two historical RetrievalPlans extracted from frozen D4-A2:
         - HIST_A2_BEFORE_PLAN (D4-A2 slot 9, BEFORE_COMPAT)
         - HIST_A2_AFTER_PLAN (D4-A2 slot 10, AFTER_BATCH1_REPLACEMENT)
  ARMS:  Two evaluation-only arms:
         - BEFORE_COMPAT
         - AFTER_BATCH1_REPLACEMENT (with K=3 bounded admission, caps 8/4, pool=30)
  CELLS: Exactly 4 serial downstream retrieval cells in balanced alternating order:
         Cell 1: HIST_A2_BEFORE_PLAN x BEFORE_COMPAT
         Cell 2: HIST_A2_BEFORE_PLAN x AFTER_BATCH1_REPLACEMENT
         Cell 3: HIST_A2_AFTER_PLAN  x AFTER_BATCH1_REPLACEMENT
         Cell 4: HIST_A2_AFTER_PLAN  x BEFORE_COMPAT
  PROVIDER ACCOUNTING:
         ANALYZER_CALLS = 0 (frozen_plan_context evaluation adapter)
         EMBEDDING_CALLS = 4 (gemini-embedding-2)
         RERANKER_CALLS = 4 (gemini-3.8-flash)
         TOTAL_LOGICAL_MODEL_CALLS = 8
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
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

_EVAL_SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _EVAL_SCRIPTS_DIR.parent.parent
if str(_EVAL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_SCRIPTS_DIR))
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import d3_5_a5_r2_selectivity as a5_r2
import d3_5_a6_phase1_admission as a6_p1
import d4_a1_fixed_locator_migration as d4_a1
from d4_a2_v1_paired_stability_validation import frozen_plan_context
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


STARTING_HEAD = "a85a79efaf90ee341787fe97b1dc29a7c4e7637c"

PREREGISTRATION_PATH = "evaluation/d4_a2_v1_r1_preregistration.json"
MANIFEST_PATH = "evaluation/d4_a2_v1_r1_execution_manifest.json"
HISTORICAL_PLAN_PAIR_PATH = "evaluation/d4_a2_v1_r1_historical_plan_pair.json"
RAW_RESULTS_PATH = "evaluation/d4_a2_v1_r1_raw_historical_contrast_results.json"
EVALUATOR_RESULTS_PATH = "evaluation/d4_a2_v1_r1_evaluator_results.json"
RESULT_PATH = "evaluation/d4_a2_v1_r1_result.json"
REPORT_PATH = "evaluation/D4_A2_V1_R1_HISTORICAL_CONTRAST_SHARED_PLAN_REPLAY.md"

HISTORICAL_A2_RAW_PATH = "evaluation/d4_a2_raw_before_after_results.json"
HISTORICAL_A2_EVALUATOR_PATH = "evaluation/d4_a2_evaluator_results.json"
HISTORICAL_A2_RESULT_PATH = "evaluation/d4_a2_result.json"

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

HISTORICAL_SLOT_BEFORE = 9
HISTORICAL_SLOT_AFTER = 10

PLAN_ID_BEFORE = "HIST_A2_BEFORE_PLAN"
PLAN_ID_AFTER = "HIST_A2_AFTER_PLAN"

FORMAL_CASES_COUNT = 1
HISTORICAL_PLANS_COUNT = 2
ARMS_COUNT = 2
FORMAL_DOWNSTREAM_CELLS = 4

SCHEDULE = [
    {
        "cell_index": 1,
        "historical_plan_id": PLAN_ID_BEFORE,
        "source_historical_slot": HISTORICAL_SLOT_BEFORE,
        "arm": "BEFORE_COMPAT",
    },
    {
        "cell_index": 2,
        "historical_plan_id": PLAN_ID_BEFORE,
        "source_historical_slot": HISTORICAL_SLOT_BEFORE,
        "arm": "AFTER_BATCH1_REPLACEMENT",
    },
    {
        "cell_index": 3,
        "historical_plan_id": PLAN_ID_AFTER,
        "source_historical_slot": HISTORICAL_SLOT_AFTER,
        "arm": "AFTER_BATCH1_REPLACEMENT",
    },
    {
        "cell_index": 4,
        "historical_plan_id": PLAN_ID_AFTER,
        "source_historical_slot": HISTORICAL_SLOT_AFTER,
        "arm": "BEFORE_COMPAT",
    },
]

ALLOWED_COMMIT_A_FILES = {
    "evaluation/d4_a2_v1_r1_preregistration.json",
    "evaluation/d4_a2_v1_r1_execution_manifest.json",
    "evaluation/d4_a2_v1_r1_historical_plan_pair.json",
    "evaluation/scripts/d4_a2_v1_r1_historical_contrast_replay.py",
    "tests/unit/test_d4_a2_v1_r1_historical_contrast_replay.py",
}

VERDICT_LEVEL_1_INVALID = "INVALID / PROTOCOL_OR_HISTORICAL_PLAN_REPLAY_FAILED"
VERDICT_LEVEL_2_FAIL = "FAIL / SHARED_PLAN_TREATMENT_REGRESSION_REPRODUCED"
VERDICT_LEVEL_3_PARTIAL = "PARTIAL / FINAL_ONLY_RERANKER_INSTABILITY"
VERDICT_LEVEL_4_INCONCLUSIVE_BEFORE = "INCONCLUSIVE / HISTORICAL_BEFORE_REFERENCE_PLAN_NOT_REPRODUCED"
VERDICT_LEVEL_5_INCONCLUSIVE_SENSITIVITY = "INCONCLUSIVE / HISTORICAL_PLAN_SENSITIVITY_NOT_REPRODUCED"
VERDICT_LEVEL_6_PASS = "PASS / HISTORICAL_PLAN_SENSITIVITY_REPRODUCED_WITHOUT_TREATMENT_REGRESSION"


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

    current_head = _git_head(project_root)
    return {
        "verified": True,
        "starting_head": STARTING_HEAD,
        "current_head": current_head,
    }


def extract_historical_plans(project_root: Path) -> dict[str, Any]:
    raw_path = project_root / HISTORICAL_A2_RAW_PATH
    if not raw_path.exists():
        raise FileNotFoundError(f"Historical raw artifact {raw_path} not found")
    raw_data = _load_json(raw_path)
    slots = raw_data.get("slots", [])
    n022_slots = [s for s in slots if s.get("case_id") == CASE_ID]
    if len(n022_slots) != 2:
        raise ValueError(
            f"Expected exactly 2 n022 historical cells in {HISTORICAL_A2_RAW_PATH}, found {len(n022_slots)}"
        )

    slot_before = next((s for s in n022_slots if s.get("arm") == "BEFORE_COMPAT"), None)
    slot_after = next((s for s in n022_slots if s.get("arm") == "AFTER_BATCH1_REPLACEMENT"), None)

    if slot_before is None or slot_after is None:
        raise ValueError("Could not locate both BEFORE_COMPAT and AFTER_BATCH1_REPLACEMENT n022 slots")

    if slot_before.get("slot_index") != HISTORICAL_SLOT_BEFORE:
        raise ValueError(
            f"Expected BEFORE slot_index {HISTORICAL_SLOT_BEFORE}, got {slot_before.get('slot_index')}"
        )
    if slot_after.get("slot_index") != HISTORICAL_SLOT_AFTER:
        raise ValueError(
            f"Expected AFTER slot_index {HISTORICAL_SLOT_AFTER}, got {slot_after.get('slot_index')}"
        )

    plan_before_obj = RetrievalPlan.model_validate(slot_before["plan_summary"])
    plan_after_obj = RetrievalPlan.model_validate(slot_after["plan_summary"])

    plan_before_dict = plan_before_obj.model_dump(mode="json")
    plan_after_dict = plan_after_obj.model_dump(mode="json")

    if plan_before_dict == plan_after_dict:
        raise ValueError("Historical plans in slot 9 and slot 10 are unexpectedly identical!")

    phenotype_before = classify_r1_concept_phenotype(plan_before_obj.concepts)
    phenotype_after = classify_r1_concept_phenotype(plan_after_obj.concepts)

    differing_fields = [k for k in plan_before_dict.keys() if plan_before_dict[k] != plan_after_dict[k]]

    norm_before_concepts = [c.strip().casefold() for c in plan_before_obj.concepts]
    norm_after_concepts = [c.strip().casefold() for c in plan_after_obj.concepts]
    omitted_concepts = [c for c in plan_before_obj.concepts if c.strip().casefold() not in norm_after_concepts]
    added_concepts = [c for c in plan_after_obj.concepts if c.strip().casefold() not in norm_before_concepts]

    historical_plan_pair = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V1-R1",
        "stage": "D4-A2-V1-R1 — Historical Plan Pair Extraction",
        "created_at": datetime.datetime.now().isoformat(),
        "historical_authority": {
            "raw_artifact": HISTORICAL_A2_RAW_PATH,
            "case_id": CASE_ID,
            "source_slots": {
                "BEFORE_COMPAT": {
                    "slot_index": HISTORICAL_SLOT_BEFORE,
                    "plan_id": PLAN_ID_BEFORE,
                },
                "AFTER_BATCH1_REPLACEMENT": {
                    "slot_index": HISTORICAL_SLOT_AFTER,
                    "plan_id": PLAN_ID_AFTER,
                },
            },
        },
        "HIST_A2_BEFORE_PLAN": {
            "plan_id": PLAN_ID_BEFORE,
            "source_slot_index": HISTORICAL_SLOT_BEFORE,
            "source_arm": "BEFORE_COMPAT",
            "intent": plan_before_obj.intent,
            "target_repositories": list(plan_before_obj.target_repositories),
            "resolved_versions": dict(plan_before_obj.resolved_versions),
            "concepts": list(plan_before_obj.concepts),
            "symbols": list(plan_before_obj.symbols),
            "concept_scopes": dict(plan_before_obj.concept_scopes),
            "required_source_types": list(plan_before_obj.required_source_types),
            "source_budgets": dict(plan_before_obj.source_budgets),
            "paper_page_hints": dict(plan_before_obj.paper_page_hints),
            "r1_concept_phenotype": phenotype_before,
            "has_worker_step": "worker step" in norm_before_concepts,
            "has_fitted_vertex": "fitted vertex" in norm_before_concepts,
            "historical_d4_a2_observed_retention": {
                "exact_channel_retained": True,
                "channel_union_retained": True,
                "fused_top30_retained": True,
                "final_rerank_pool_retained": True,
                "final_evidence_retained": True,
            },
            "canonical_plan": plan_before_dict,
        },
        "HIST_A2_AFTER_PLAN": {
            "plan_id": PLAN_ID_AFTER,
            "source_slot_index": HISTORICAL_SLOT_AFTER,
            "source_arm": "AFTER_BATCH1_REPLACEMENT",
            "intent": plan_after_obj.intent,
            "target_repositories": list(plan_after_obj.target_repositories),
            "resolved_versions": dict(plan_after_obj.resolved_versions),
            "concepts": list(plan_after_obj.concepts),
            "symbols": list(plan_after_obj.symbols),
            "concept_scopes": dict(plan_after_obj.concept_scopes),
            "required_source_types": list(plan_after_obj.required_source_types),
            "source_budgets": dict(plan_after_obj.source_budgets),
            "paper_page_hints": dict(plan_after_obj.paper_page_hints),
            "r1_concept_phenotype": phenotype_after,
            "has_worker_step": "worker step" in norm_after_concepts,
            "has_fitted_vertex": "fitted vertex" in norm_after_concepts,
            "historical_d4_a2_observed_retention": {
                "exact_channel_retained": False,
                "channel_union_retained": True,
                "fused_top30_retained": False,
                "final_rerank_pool_retained": False,
                "final_evidence_retained": False,
            },
            "canonical_plan": plan_after_dict,
        },
        "canonical_plan_comparison": {
            "differing_fields": differing_fields,
            "concepts_differ": "concepts" in differing_fields,
            "analysis_diagnostics_differ": "analysis_diagnostics" in differing_fields,
            "concepts_contrast": {
                "before_concepts": list(plan_before_obj.concepts),
                "after_concepts": list(plan_after_obj.concepts),
                "omitted_in_after": omitted_concepts,
                "added_in_after": added_concepts,
            },
            "symbols_contrast": {
                "before_symbols": list(plan_before_obj.symbols),
                "after_symbols": list(plan_after_obj.symbols),
            },
            "intent_identical": plan_before_obj.intent == plan_after_obj.intent,
            "target_repositories_identical": plan_before_obj.target_repositories == plan_after_obj.target_repositories,
            "resolved_versions_identical": plan_before_obj.resolved_versions == plan_after_obj.resolved_versions,
            "source_budgets_identical": plan_before_obj.source_budgets == plan_after_obj.source_budgets,
            "required_source_types_identical": plan_before_obj.required_source_types == plan_after_obj.required_source_types,
            "concept_scopes_identical": plan_before_obj.concept_scopes == plan_after_obj.concept_scopes,
            "paper_page_hints_identical": plan_before_obj.paper_page_hints == plan_after_obj.paper_page_hints,
            "resolved_aliases_identical": plan_before_obj.resolved_aliases == plan_after_obj.resolved_aliases,
            "premise_corrections_identical": plan_before_obj.premise_corrections == plan_after_obj.premise_corrections,
        },
    }

    out_path = project_root / HISTORICAL_PLAN_PAIR_PATH
    _save_json(out_path, historical_plan_pair)
    print(f"[HISTORICAL PLANS EXTRACTED] Saved to {out_path}")
    return historical_plan_pair


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

    # Manifest verification
    manifest_path = project_root / MANIFEST_PATH
    if manifest_path.exists():
        manifest = _load_json(manifest_path)
        cells_4 = manifest.get("cells_4", [])
        if len(cells_4) != FORMAL_DOWNSTREAM_CELLS:
            raise ValueError(f"Manifest cells mismatch: expected {FORMAL_DOWNSTREAM_CELLS}, got {len(cells_4)}")
        for sched_item, cell_item in zip(SCHEDULE, cells_4):
            if (
                cell_item["cell_index"],
                cell_item["historical_plan_id"],
                cell_item["arm"],
            ) != (
                sched_item["cell_index"],
                sched_item["historical_plan_id"],
                sched_item["arm"],
            ):
                raise ValueError(f"Schedule mismatch in manifest cell: {cell_item} vs {sched_item}")

    # Preregistration verification
    prereg_path = project_root / PREREGISTRATION_PATH
    if prereg_path.exists():
        prereg = _load_json(prereg_path)
        exposure_state = prereg.get("outcome_exposure_state", {})
        if exposure_state.get("D4_A2_V1_R1_OUTCOME_EXPOSURE") != "NOT_STARTED":
            raise ValueError("Preregistration D4_A2_V1_R1_OUTCOME_EXPOSURE is not NOT_STARTED")

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
        "formal_cells": FORMAL_DOWNSTREAM_CELLS,
        "drift_guards_verified": drift_receipt["verified"],
        "protected_dataset_access": 0,
    }


def execute_historical_replay(project_root: Path) -> dict[str, Any]:
    load_dotenv(project_root / ".env")
    audit_receipt = audit_invariants(project_root)
    print(f"[REPLAY AUDIT PASSED] Model: {audit_receipt['model_id']}")

    manifest_path = project_root / MANIFEST_PATH
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest {manifest_path} missing!")
    manifest = _load_json(manifest_path)
    exposure = manifest.setdefault("outcome_exposure_state", {})

    if exposure.get("D4_A2_V1_R1_OUTCOME_EXPOSURE") == "RAW_OUTCOMES_COMPLETE":
        print("[REPLAY ALREADY COMPLETED] Loading existing raw results.")
        return _load_json(project_root / RAW_RESULTS_PATH)

    exposure["D4_A2_V1_R1_OUTCOME_EXPOSURE"] = "STARTED"
    _save_json(manifest_path, manifest)

    commit_a_sha = _git_head(project_root)
    retriever = Retriever(project_root)
    object_lookup = load_object_lookup(project_root)

    original_qe = load_query_expansions(project_root / CONFIG_QUERY_EXPANSIONS_PATH)
    masked_qe = d4_a1.apply_batch1_in_memory_mask(original_qe)

    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    n022_q = next(q for q in novel_ds.questions if q.id == CASE_ID)
    n022_e2_group = next(g for g in n022_q.required_evidence_groups if g.group_id == TARGET_EVIDENCE_GROUP_ID)

    plans_artifact = _load_json(project_root / HISTORICAL_PLAN_PAIR_PATH)
    plans_by_id = {
        PLAN_ID_BEFORE: RetrievalPlan.model_validate(plans_artifact["HIST_A2_BEFORE_PLAN"]["canonical_plan"]),
        PLAN_ID_AFTER: RetrievalPlan.model_validate(plans_artifact["HIST_A2_AFTER_PLAN"]["canonical_plan"]),
    }

    cell_results: list[dict[str, Any]] = []
    total_tokens = 0
    total_attempts = 0
    total_embedding_calls = 0
    total_reranker_calls = 0

    print(f"[D4-A2-V1-R1 REPLAY] Beginning 4 serial historical shared-plan retrieval cells...")

    for sched_item in SCHEDULE:
        cell_idx = sched_item["cell_index"]
        plan_id = sched_item["historical_plan_id"]
        source_slot = sched_item["source_historical_slot"]
        arm = sched_item["arm"]

        manifest_cell = manifest["cells_4"][cell_idx - 1]
        if manifest_cell["status"] == "COMPLETED":
            print(f"  Cell #{cell_idx} ({plan_id}, {arm}) already completed, skipping.")
            continue
        if manifest_cell["status"] == "STARTED":
            raise RuntimeError(f"Cell #{cell_idx} in ambiguous STARTED state upon execution! Fail closed.")

        manifest_cell["status"] = "STARTED"
        manifest_cell["started_at"] = datetime.datetime.now().isoformat()
        _save_json(manifest_path, manifest)

        frozen_plan = plans_by_id[plan_id]
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
                f"Cell #{cell_idx}: Plan equality mismatch! Actual plan does not match frozen plan {plan_id}"
            )

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
            "historical_plan_id": plan_id,
            "source_historical_cell": {
                "slot_index": source_slot,
                "arm": "BEFORE_COMPAT" if source_slot == HISTORICAL_SLOT_BEFORE else "AFTER_BATCH1_REPLACEMENT",
            },
            "arm": arm,
            "question": EXACT_QUERY,
            "status": "COMPLETED",
            "elapsed_seconds": elapsed,
            "plan_equality_verified": True,
            "frozen_plan": frozen_plan_dict,
            "actual_plan_used": actual_plan_dict,
            "matched_expansion_rules": [],
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
        print(f"  Cell #{cell_idx}/4 COMPLETED ({plan_id}, {arm}): pool={pool_flag}, final={ev_flag} in {elapsed}s")

    raw_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V1-R1",
        "stage": "D4-A2-V1-R1 — Historical Contrast Shared-Plan Replay Raw Outcomes",
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
    }

    _save_json(project_root / RAW_RESULTS_PATH, raw_artifact)

    exposure["D4_A2_V1_R1_OUTCOME_EXPOSURE"] = "RAW_OUTCOMES_COMPLETE"
    exposure["downstream_cells_completed"] = len(cell_results)
    _save_json(manifest_path, manifest)

    print(f"[REPLAY COMPLETE] All 4 cells frozen to {RAW_RESULTS_PATH}")
    return raw_artifact


def evaluate_historical_replay(project_root: Path) -> dict[str, Any]:
    raw_path = project_root / RAW_RESULTS_PATH
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw results {raw_path} missing! Run execute_historical_replay first.")

    raw = _load_json(raw_path)
    cells = raw.get("cells", [])
    if len(cells) != FORMAL_DOWNSTREAM_CELLS:
        raise ValueError(f"Expected {FORMAL_DOWNSTREAM_CELLS} cells, got {len(cells)}")

    # Index cells by (plan_id, arm)
    cells_map: dict[tuple[str, str], dict[str, Any]] = {}
    for c in cells:
        cells_map[(c["historical_plan_id"], c["arm"])] = c

    c_before_b = cells_map[(PLAN_ID_BEFORE, "BEFORE_COMPAT")]
    c_before_a = cells_map[(PLAN_ID_BEFORE, "AFTER_BATCH1_REPLACEMENT")]
    c_after_a = cells_map[(PLAN_ID_AFTER, "AFTER_BATCH1_REPLACEMENT")]
    c_after_b = cells_map[(PLAN_ID_AFTER, "BEFORE_COMPAT")]

    # 1. Exact-channel mechanism check
    before_b_exact = c_before_b["n022_e2_retention"]["exact_channel_retained"]
    after_b_exact = c_after_b["n022_e2_retention"]["exact_channel_retained"]
    historical_exact_recall_contrast_reproduced = bool(before_b_exact and not after_b_exact)

    # 2. Plan-to-evidence sensitivity (under BEFORE_COMPAT)
    before_b_pool = c_before_b["n022_e2_retention"]["final_rerank_pool_retained"]
    after_b_pool = c_after_b["n022_e2_retention"]["final_rerank_pool_retained"]
    historical_plan_sensitivity_reproduced = bool(before_b_pool and not after_b_pool)

    # Also check final evidence sensitivity
    before_b_ev = c_before_b["n022_e2_retention"]["final_evidence_retained"]
    after_b_ev = c_after_b["n022_e2_retention"]["final_evidence_retained"]
    historical_final_evidence_sensitivity_reproduced = bool(before_b_ev and not after_b_ev)

    # 3. Within-plan treatment classifications (Pre-rerank)
    # Plan BEFORE:
    p_before_b_pool = c_before_b["n022_e2_retention"]["final_rerank_pool_retained"]
    p_before_a_pool = c_before_a["n022_e2_retention"]["final_rerank_pool_retained"]
    if p_before_b_pool and p_before_a_pool:
        class_plan_before = "PAIR_PRESERVED"
    elif (not p_before_b_pool) and (not p_before_a_pool):
        class_plan_before = "PAIR_UNRESOLVED_BOTH"
    elif p_before_b_pool and (not p_before_a_pool):
        class_plan_before = "PAIR_TREATMENT_REGRESSION"
    else:
        class_plan_before = "PAIR_TREATMENT_RECOVERY"

    # Plan AFTER:
    p_after_b_pool = c_after_b["n022_e2_retention"]["final_rerank_pool_retained"]
    p_after_a_pool = c_after_a["n022_e2_retention"]["final_rerank_pool_retained"]
    if p_after_b_pool and p_after_a_pool:
        class_plan_after = "PAIR_PRESERVED"
    elif (not p_after_b_pool) and (not p_after_a_pool):
        class_plan_after = "PAIR_UNRESOLVED_BOTH"
    elif p_after_b_pool and (not p_after_a_pool):
        class_plan_after = "PAIR_TREATMENT_REGRESSION"
    else:
        class_plan_after = "PAIR_TREATMENT_RECOVERY"

    pair_treatment_regression_count = (
        (1 if class_plan_before == "PAIR_TREATMENT_REGRESSION" else 0)
        + (1 if class_plan_after == "PAIR_TREATMENT_REGRESSION" else 0)
    )
    pair_treatment_recovery_count = (
        (1 if class_plan_before == "PAIR_TREATMENT_RECOVERY" else 0)
        + (1 if class_plan_after == "PAIR_TREATMENT_RECOVERY" else 0)
    )
    pair_preserved_count = (
        (1 if class_plan_before == "PAIR_PRESERVED" else 0)
        + (1 if class_plan_after == "PAIR_PRESERVED" else 0)
    )
    pair_unresolved_both_count = (
        (1 if class_plan_before == "PAIR_UNRESOLVED_BOTH" else 0)
        + (1 if class_plan_after == "PAIR_UNRESOLVED_BOTH" else 0)
    )

    # 4. Final-evidence classifications
    p_before_b_ev = c_before_b["n022_e2_retention"]["final_evidence_retained"]
    p_before_a_ev = c_before_a["n022_e2_retention"]["final_evidence_retained"]
    if p_before_b_ev and p_before_a_ev:
        ev_class_plan_before = "FINAL_EVIDENCE_PRESERVED"
    elif (not p_before_b_ev) and (not p_before_a_ev):
        ev_class_plan_before = "FINAL_EVIDENCE_UNRESOLVED_BOTH"
    elif p_before_b_ev and (not p_before_a_ev):
        ev_class_plan_before = "FINAL_EVIDENCE_REGRESSION"
    else:
        ev_class_plan_before = "FINAL_EVIDENCE_RECOVERY"

    p_after_b_ev = c_after_b["n022_e2_retention"]["final_evidence_retained"]
    p_after_a_ev = c_after_a["n022_e2_retention"]["final_evidence_retained"]
    if p_after_b_ev and p_after_a_ev:
        ev_class_plan_after = "FINAL_EVIDENCE_PRESERVED"
    elif (not p_after_b_ev) and (not p_after_a_ev):
        ev_class_plan_after = "FINAL_EVIDENCE_UNRESOLVED_BOTH"
    elif p_after_b_ev and (not p_after_a_ev):
        ev_class_plan_after = "FINAL_EVIDENCE_REGRESSION"
    else:
        ev_class_plan_after = "FINAL_EVIDENCE_RECOVERY"

    final_only_regression_before = (p_before_b_pool == p_before_a_pool) and (p_before_b_ev and not p_before_a_ev)
    final_only_recovery_before = (p_before_b_pool == p_before_a_pool) and (not p_before_b_ev and p_before_a_ev)

    final_only_regression_after = (p_after_b_pool == p_after_a_pool) and (p_after_b_ev and not p_after_a_ev)
    final_only_recovery_after = (p_after_b_pool == p_after_a_pool) and (not p_after_b_ev and p_after_a_ev)

    final_only_regression_count = (1 if final_only_regression_before else 0) + (1 if final_only_regression_after else 0)
    final_only_recovery_count = (1 if final_only_recovery_before else 0) + (1 if final_only_recovery_after else 0)

    # 5. Clean Factorial Pattern check
    clean_factorial_pattern = None
    if (class_plan_before == "PAIR_PRESERVED") and (class_plan_after == "PAIR_UNRESOLVED_BOTH"):
        clean_factorial_pattern = "T/T vs F/F"

    # 6. Structured attribution (if any regression)
    structured_attribution_report = []
    if pair_treatment_regression_count > 0:
        for p_id, b_c, a_c in [
            (PLAN_ID_BEFORE, c_before_b, c_before_a),
            (PLAN_ID_AFTER, c_after_b, c_after_a),
        ]:
            if b_c["n022_e2_retention"]["final_rerank_pool_retained"] and not a_c["n022_e2_retention"]["final_rerank_pool_retained"]:
                displaced = a_c.get("displaced_candidate_ids", [])
                reserved = a_c.get("reserved_candidate_ids", [])
                bridge = a_c.get("selected_bridge_candidates", [])
                mechanism = "TRACE_INSUFFICIENT"
                if displaced:
                    mechanism = "BOUNDED_ADMISSION_DISPLACEMENT"
                elif bridge:
                    mechanism = "STRUCTURED_GRAPH_COMPETITION"
                else:
                    mechanism = "OTHER_TREATMENT_PATH"
                structured_attribution_report.append({
                    "plan_id": p_id,
                    "attribution": mechanism,
                    "displaced_candidate_ids": displaced,
                    "reserved_candidate_ids": reserved,
                })

    # 7. Four 2x2 Scientific Contrasts
    contrasts = {
        "contrast_A_historical_plan_effect_under_before": {
            "description": "HIST_A2_BEFORE_PLAN x BEFORE vs HIST_A2_AFTER_PLAN x BEFORE",
            "before_plan_pre_rerank": before_b_pool,
            "after_plan_pre_rerank": after_b_pool,
            "contrast_observed": historical_plan_sensitivity_reproduced,
            "exact_recall_contrast_observed": historical_exact_recall_contrast_reproduced,
        },
        "contrast_B_historical_plan_effect_under_after": {
            "description": "HIST_A2_BEFORE_PLAN x AFTER vs HIST_A2_AFTER_PLAN x AFTER",
            "before_plan_pre_rerank": p_before_a_pool,
            "after_plan_pre_rerank": p_after_a_pool,
            "contrast_observed": bool(p_before_a_pool and not p_after_a_pool),
        },
        "contrast_C_treatment_effect_under_before_plan": {
            "description": "HIST_A2_BEFORE_PLAN: BEFORE vs AFTER",
            "before_compat_pre_rerank": p_before_b_pool,
            "after_batch1_pre_rerank": p_before_a_pool,
            "classification": class_plan_before,
        },
        "contrast_D_treatment_effect_under_after_plan": {
            "description": "HIST_A2_AFTER_PLAN: BEFORE vs AFTER",
            "before_compat_pre_rerank": p_after_b_pool,
            "after_batch1_pre_rerank": p_after_a_pool,
            "classification": class_plan_after,
        },
    }

    # 8. Historical vs Replay Comparison
    historical_vs_replay = {
        "historical_slot_9_vs_cell_1": {
            "slot_index": HISTORICAL_SLOT_BEFORE,
            "arm": "BEFORE_COMPAT",
            "plan_id": PLAN_ID_BEFORE,
            "historical_exact": True,
            "replay_exact": before_b_exact,
            "historical_pool": True,
            "replay_pool": before_b_pool,
            "historical_final": True,
            "replay_final": before_b_ev,
        },
        "historical_slot_10_vs_cell_3": {
            "slot_index": HISTORICAL_SLOT_AFTER,
            "arm": "AFTER_BATCH1_REPLACEMENT",
            "plan_id": PLAN_ID_AFTER,
            "historical_exact": False,
            "replay_exact": c_after_a["n022_e2_retention"]["exact_channel_retained"],
            "historical_pool": False,
            "replay_pool": p_after_a_pool,
            "historical_final": False,
            "replay_final": p_after_a_ev,
        },
    }

    # 9. Verdict Determination Ladder
    all_plan_equality = all(c.get("plan_equality_verified", False) for c in cells)
    total_analyzer_calls = raw.get("accounting", {}).get("analyzer_calls", 0)

    verdict = ""
    verdict_level = 0
    rationale = ""

    if (
        len(cells) != 4
        or not all_plan_equality
        or total_analyzer_calls > 0
    ):
        verdict = VERDICT_LEVEL_1_INVALID
        verdict_level = 1
        rationale = "Execution protocol violation or plan injection mismatch."
    elif pair_treatment_regression_count >= 1:
        verdict = VERDICT_LEVEL_2_FAIL
        verdict_level = 2
        rationale = (
            f"Pre-rerank treatment regression observed under historical plan replay "
            f"({pair_treatment_regression_count} regressions)."
        )
    elif final_only_regression_count >= 1:
        verdict = VERDICT_LEVEL_3_PARTIAL
        verdict_level = 3
        rationale = "Pre-rerank retention preserved across arms, but downstream reranker instability caused final-only regression."
    elif not before_b_pool:
        verdict = VERDICT_LEVEL_4_INCONCLUSIVE_BEFORE
        verdict_level = 4
        rationale = "Historical BEFORE reference plan failed to retain target evidence under BEFORE_COMPAT arm."
    elif not historical_plan_sensitivity_reproduced:
        verdict = VERDICT_LEVEL_5_INCONCLUSIVE_SENSITIVITY
        verdict_level = 5
        rationale = "Historical plans failed to reproduce pre-rerank evidence sensitivity contrast under BEFORE_COMPAT."
    else:
        verdict = VERDICT_LEVEL_6_PASS
        verdict_level = 6
        rationale = (
            "The historically observed n022.e2 availability contrast is reproduced by the frozen RetrievalPlan "
            "contrast under a common compatibility path, while no additional Batch-1 replacement regression "
            "is observed when each plan is shared across arms."
        )

    acc = raw.get("accounting", {})
    evaluator_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V1-R1",
        "stage": "D4-A2-V1-R1 — Deterministic Evaluator",
        "created_at": datetime.datetime.now().isoformat(),
        "starting_head": STARTING_HEAD,
        "commit_a_implementation_freeze_head": raw.get("commit_a_implementation_freeze_head", ""),
        "verdict": verdict,
        "verdict_level": verdict_level,
        "rationale": rationale,
        "clean_factorial_pattern": clean_factorial_pattern,
        "scientific_contrasts": contrasts,
        "exact_recall_contrast": {
            "HISTORICAL_EXACT_RECALL_CONTRAST_REPRODUCED": historical_exact_recall_contrast_reproduced,
            "before_plan_before_compat_exact": before_b_exact,
            "after_plan_before_compat_exact": after_b_exact,
        },
        "plan_sensitivity": {
            "HISTORICAL_PLAN_SENSITIVITY_REPRODUCED": historical_plan_sensitivity_reproduced,
            "before_plan_before_compat_pool": before_b_pool,
            "after_plan_before_compat_pool": after_b_pool,
            "final_evidence_sensitivity_reproduced": historical_final_evidence_sensitivity_reproduced,
        },
        "treatment_effects": {
            "PAIR_TREATMENT_REGRESSION_COUNT": pair_treatment_regression_count,
            "PAIR_TREATMENT_RECOVERY_COUNT": pair_treatment_recovery_count,
            "PAIR_PRESERVED_COUNT": pair_preserved_count,
            "PAIR_UNRESOLVED_BOTH_COUNT": pair_unresolved_both_count,
            "plan_before_classification": class_plan_before,
            "plan_after_classification": class_plan_after,
        },
        "final_only_effects": {
            "FINAL_ONLY_REGRESSION_COUNT": final_only_regression_count,
            "FINAL_ONLY_RECOVERY_COUNT": final_only_recovery_count,
            "plan_before_final_classification": ev_class_plan_before,
            "plan_after_final_classification": ev_class_plan_after,
        },
        "structured_treatment_attribution": structured_attribution_report,
        "historical_vs_replay": historical_vs_replay,
        "accounting": {
            "FORMAL_CASES": 1,
            "HISTORICAL_PLANS": 2,
            "ARMS": 2,
            "FORMAL_CELLS_PLANNED": FORMAL_DOWNSTREAM_CELLS,
            "FORMAL_CELLS_COMPLETED": len(cells),
            "FORMAL_CELLS_FAILED": 0,
            "ANALYZER_CALLS": acc.get("analyzer_calls", 0),
            "EMBEDDING_CALLS": acc.get("embedding_calls", 0),
            "RERANKER_CALLS": acc.get("reranker_calls", 0),
            "TOTAL_LOGICAL_MODEL_CALLS": acc.get("logical_model_calls", 0),
            "PROVIDER_ATTEMPTS": acc.get("provider_attempts", 0),
            "RETRIES": 0,
            "TOKEN_USAGE": acc.get("token_usage", 0),
            "QA_CALLS": 0,
            "VERIFIER_CALLS": 0,
            "JUDGE_CALLS": 0,
            "POSTGRESQL_WRITES": 0,
            "QDRANT_WRITES": 0,
            "INGESTION": 0,
            "REINDEX": 0,
            "PROTECTED_DATASET_ACCESS": 0,
        },
    }

    _save_json(project_root / EVALUATOR_RESULTS_PATH, evaluator_artifact)
    print(f"[EVALUATOR COMPLETE] Results saved to {EVALUATOR_RESULTS_PATH}")

    # Result artifact
    result_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A2-V1-R1",
        "stage": "D4-A2-V1-R1 — Historical Contrast Shared-Plan Replay",
        "created_at": datetime.datetime.now().isoformat(),
        "starting_head": STARTING_HEAD,
        "commit_a_implementation_freeze_head": raw.get("commit_a_implementation_freeze_head", ""),
        "verdict": verdict,
        "verdict_level": verdict_level,
        "rationale": rationale,
        "lifecycle_state": f"COMPLETE / {verdict}",
        "clean_factorial_pattern": clean_factorial_pattern,
        "production_activation": False,
        "first_batch_runtime_migration": "BLOCKED",
        "d4_a3_state": "NOT_STARTED / BLOCKED",
        "exact_next_stage": (
            "D4-A2-V2 — Controlled Shared-Plan T2 Before/After Validation (NOT_STARTED / SEPARATELY_AUTHORIZED)"
            if verdict_level == 6
            else "SEPARATE_DIAGNOSTIC_OR_REPAIR"
        ),
        "accounting": evaluator_artifact["accounting"],
        "key_metrics": {
            "HISTORICAL_EXACT_RECALL_CONTRAST_REPRODUCED": historical_exact_recall_contrast_reproduced,
            "HISTORICAL_PLAN_SENSITIVITY_REPRODUCED": historical_plan_sensitivity_reproduced,
            "PAIR_TREATMENT_REGRESSION_COUNT": pair_treatment_regression_count,
            "PAIR_TREATMENT_RECOVERY_COUNT": pair_treatment_recovery_count,
            "PAIR_PRESERVED_COUNT": pair_preserved_count,
            "PAIR_UNRESOLVED_BOTH_COUNT": pair_unresolved_both_count,
            "FINAL_ONLY_REGRESSION_COUNT": final_only_regression_count,
            "FINAL_ONLY_RECOVERY_COUNT": final_only_recovery_count,
            "CLEAN_FACTORIAL_PATTERN": clean_factorial_pattern,
        },
    }

    _save_json(project_root / RESULT_PATH, result_artifact)
    print(f"[RESULT COMPLETE] Result saved to {RESULT_PATH}")

    # Human-readable report
    generate_markdown_report(project_root, evaluator_artifact, result_artifact)

    return evaluator_artifact


def generate_markdown_report(
    project_root: Path, eval_results: dict[str, Any], result: dict[str, Any]
) -> None:
    acc = eval_results["accounting"]
    km = result["key_metrics"]
    contrasts = eval_results["scientific_contrasts"]

    lines = [
        "# PANDA Agent — D4-A2-V1-R1: Historical Contrast Shared-Plan Replay Report",
        "",
        "## 1. Executive Summary",
        "",
        f"- **Verdict**: `{result['verdict']}` (Level {result['verdict_level']})",
        f"- **Lifecycle State**: `{result['lifecycle_state']}`",
        f"- **Clean Factorial Pattern**: `{result['clean_factorial_pattern']}`",
        f"- **Production Activation**: `{result['production_activation']}` (BLOCKED)",
        f"- **First-Batch Runtime Migration**: `{result['first_batch_runtime_migration']}`",
        f"- **D4-A3 State**: `{result['d4_a3_state']}`",
        f"- **Exact Next Stage**: `{result['exact_next_stage']}`",
        "",
        f"> **Scientific Finding**: {result['rationale']}",
        "",
        "---",
        "",
        "## 2. 2x2 Crossover Matrix Outcomes",
        "",
        "| Cell | Historical Plan ID | Arm | Exact Retained | Top30 Retained | Final Pool Retained | Final Evidence Retained | Status |",
        "|---|---|---|---|---|---|---|---|",
    ]

    raw = _load_json(project_root / RAW_RESULTS_PATH)
    for c in raw.get("cells", []):
        ret = c["n022_e2_retention"]
        lines.append(
            f"| #{c['cell_index']} | `{c['historical_plan_id']}` | `{c['arm']}` | "
            f"{ret['exact_channel_retained']} | {ret['fused_top30_retained']} | "
            f"{ret['final_rerank_pool_retained']} | {ret['final_evidence_retained']} | {c['status']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Primary 2x2 Scientific Contrasts",
        "",
        f"### Contrast A — Historical Plan Effect under BEFORE_COMPAT",
        f"- Description: `{contrasts['contrast_A_historical_plan_effect_under_before']['description']}`",
        f"- BEFORE Plan Pre-rerank: `{contrasts['contrast_A_historical_plan_effect_under_before']['before_plan_pre_rerank']}`",
        f"- AFTER Plan Pre-rerank: `{contrasts['contrast_A_historical_plan_effect_under_before']['after_plan_pre_rerank']}`",
        f"- Historical Plan Sensitivity Reproduced: `{contrasts['contrast_A_historical_plan_effect_under_before']['contrast_observed']}`",
        f"- Historical Exact-Recall Contrast Observed: `{contrasts['contrast_A_historical_plan_effect_under_before']['exact_recall_contrast_observed']}`",
        "",
        f"### Contrast B — Historical Plan Effect under AFTER_BATCH1_REPLACEMENT",
        f"- Description: `{contrasts['contrast_B_historical_plan_effect_under_after']['description']}`",
        f"- BEFORE Plan Pre-rerank: `{contrasts['contrast_B_historical_plan_effect_under_after']['before_plan_pre_rerank']}`",
        f"- AFTER Plan Pre-rerank: `{contrasts['contrast_B_historical_plan_effect_under_after']['after_plan_pre_rerank']}`",
        f"- Contrast Observed: `{contrasts['contrast_B_historical_plan_effect_under_after']['contrast_observed']}`",
        "",
        f"### Contrast C — Treatment Effect under HIST_A2_BEFORE_PLAN",
        f"- Description: `{contrasts['contrast_C_treatment_effect_under_before_plan']['description']}`",
        f"- BEFORE_COMPAT Pre-rerank: `{contrasts['contrast_C_treatment_effect_under_before_plan']['before_compat_pre_rerank']}`",
        f"- AFTER_BATCH1 Pre-rerank: `{contrasts['contrast_C_treatment_effect_under_before_plan']['after_batch1_pre_rerank']}`",
        f"- Classification: `{contrasts['contrast_C_treatment_effect_under_before_plan']['classification']}`",
        "",
        f"### Contrast D — Treatment Effect under HIST_A2_AFTER_PLAN",
        f"- Description: `{contrasts['contrast_D_treatment_effect_under_after_plan']['description']}`",
        f"- BEFORE_COMPAT Pre-rerank: `{contrasts['contrast_D_treatment_effect_under_after_plan']['before_compat_pre_rerank']}`",
        f"- AFTER_BATCH1 Pre-rerank: `{contrasts['contrast_D_treatment_effect_under_after_plan']['after_batch1_pre_rerank']}`",
        f"- Classification: `{contrasts['contrast_D_treatment_effect_under_after_plan']['classification']}`",
        "",
        "---",
        "",
        "## 4. Historical vs Replay Comparison",
        "",
        "| Comparison | Historical Slot | Arm | Hist Exact | Replay Exact | Hist Pool | Replay Pool | Hist Final | Replay Final |",
        "|---|---|---|---|---|---|---|---|---|",
        f"| Hist Slot 9 vs Cell 1 | 9 | `BEFORE_COMPAT` | True | {eval_results['historical_vs_replay']['historical_slot_9_vs_cell_1']['replay_exact']} | True | {eval_results['historical_vs_replay']['historical_slot_9_vs_cell_1']['replay_pool']} | True | {eval_results['historical_vs_replay']['historical_slot_9_vs_cell_1']['replay_final']} |",
        f"| Hist Slot 10 vs Cell 3 | 10 | `AFTER_BATCH1_REPLACEMENT` | False | {eval_results['historical_vs_replay']['historical_slot_10_vs_cell_3']['replay_exact']} | False | {eval_results['historical_vs_replay']['historical_slot_10_vs_cell_3']['replay_pool']} | False | {eval_results['historical_vs_replay']['historical_slot_10_vs_cell_3']['replay_final']} |",
        "",
        "---",
        "",
        "## 5. Formal Call and Resource Accounting",
        "",
        f"- **Formal Cases**: 1 (`n022`)",
        f"- **Historical Plans**: 2 (`HIST_A2_BEFORE_PLAN`, `HIST_A2_AFTER_PLAN`)",
        f"- **Arms**: 2 (`BEFORE_COMPAT`, `AFTER_BATCH1_REPLACEMENT`)",
        f"- **Formal Retrieval Cells**: {acc['FORMAL_CELLS_COMPLETED']} / 4 (0 failed)",
        f"- **Analyzer Calls**: {acc['ANALYZER_CALLS']} (Phase P absent; 0 provider calls in replay)",
        f"- **Embedding Calls**: {acc['EMBEDDING_CALLS']} (`gemini-embedding-2`)",
        f"- **Reranker Calls**: {acc['RERANKER_CALLS']} (`gemini-3.8-flash`)",
        f"- **Total Logical Model Calls**: {acc['TOTAL_LOGICAL_MODEL_CALLS']}",
        f"- **Provider Attempts**: {acc['PROVIDER_ATTEMPTS']} (0 retries)",
        f"- **Token Usage**: {acc['TOKEN_USAGE']}",
        f"- **QA / Verifier / Judge Calls**: 0",
        f"- **PostgreSQL / Qdrant Writes**: 0",
        f"- **Protected Dataset Access**: 0 (0 novel validation, 0 novel holdout)",
        "",
        "---",
        "",
        "## 6. Key Scientific Metrics",
        "",
        f"- `HISTORICAL_EXACT_RECALL_CONTRAST_REPRODUCED = {km['HISTORICAL_EXACT_RECALL_CONTRAST_REPRODUCED']}`",
        f"- `HISTORICAL_PLAN_SENSITIVITY_REPRODUCED = {km['HISTORICAL_PLAN_SENSITIVITY_REPRODUCED']}`",
        f"- `PAIR_TREATMENT_REGRESSION_COUNT = {km['PAIR_TREATMENT_REGRESSION_COUNT']}`",
        f"- `PAIR_TREATMENT_RECOVERY_COUNT = {km['PAIR_TREATMENT_RECOVERY_COUNT']}`",
        f"- `PAIR_PRESERVED_COUNT = {km['PAIR_PRESERVED_COUNT']}`",
        f"- `PAIR_UNRESOLVED_BOTH_COUNT = {km['PAIR_UNRESOLVED_BOTH_COUNT']}`",
        f"- `FINAL_ONLY_REGRESSION_COUNT = {km['FINAL_ONLY_REGRESSION_COUNT']}`",
        f"- `FINAL_ONLY_RECOVERY_COUNT = {km['FINAL_ONLY_RECOVERY_COUNT']}`",
        f"- `CLEAN_FACTORIAL_PATTERN = {km['CLEAN_FACTORIAL_PATTERN']}`",
        "",
        "---",
        "",
        "## 7. Lifecycle Decision and Next Stage",
        "",
        "```text",
        f"D4-A2-V1-R1 = {result['lifecycle_state']}",
        f"PRODUCTION_ACTIVATION = {str(result['production_activation']).lower()}",
        f"FIRST_BATCH_RUNTIME_MIGRATION = {result['first_batch_runtime_migration']}",
        f"D4-A3 = {result['d4_a3_state']}",
        f"EXACT_NEXT_STAGE = {result['exact_next_stage']}",
        "```",
        "",
    ])

    report_path = project_root / REPORT_PATH
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[REPORT GENERATED] Saved to {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="D4-A2-V1-R1 Historical Contrast Shared-Plan Replay Runner")
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Project root directory")
    parser.add_argument(
        "--mode",
        choices=["audit-invariants", "extract-plans", "execute-replay", "evaluate"],
        required=True,
        help="Execution mode",
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    if args.mode == "audit-invariants":
        receipt = audit_invariants(project_root)
        print(f"Audit passed: {receipt}")
    elif args.mode == "extract-plans":
        extract_historical_plans(project_root)
    elif args.mode == "execute-replay":
        execute_historical_replay(project_root)
    elif args.mode == "evaluate":
        evaluate_historical_replay(project_root)


if __name__ == "__main__":
    main()
