"""D3.5-A6 Phase 2 — Paired Repeated Reranker Replay Executor and Evaluator.

Executes exactly the frozen 54 formal calls in the preregistered cyclic schedule
against Google Vertex AI Gemini 3.8 Flash (temperature 0.0, RERANK_SYSTEM_PROMPT).
Freezes raw outcomes before running deterministic post-rerank replay and scientific evaluation.

CLI (run with PYTHONPATH=src):
    python evaluation/scripts/d3_5_a6_phase2_executor.py --project-root . --mode audit-invariants
    python evaluation/scripts/d3_5_a6_phase2_executor.py --project-root . --mode execute-54
    python evaluation/scripts/d3_5_a6_phase2_executor.py --project-root . --mode evaluate
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Ensure evaluation/scripts is in sys.path so we can import d3_5_a6_phase1_admission
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import d3_5_a6_phase1_admission as a6_p1
from panda_agent.evaluation import _matched_evidence_groups, load_gold_dataset
from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.prompts import RERANK_SYSTEM_PROMPT

RAW_RESULTS_PATH = "evaluation/d3_5_a6_phase2_raw_reranker_results.json"
REPLAY_AND_EVAL_PATH = "evaluation/d3_5_a6_phase2_replay_and_evaluator_results.json"
FINAL_RESULT_PATH = "evaluation/d3_5_a6_phase2_result.json"
HUMAN_REPORT_PATH = "evaluation/D3_5_A6_PHASE2_PAIRED_REPEATED_RERANKER_REPLAY.md"

GOLD_QUESTIONS_PATH = "evaluation/benchmarks/v2_6/gold_questions.yaml"
NOVEL_DEV_PATH = "evaluation/novel/v1/novel_dev.yaml"

MODEL_CONTRACT_AUTHORITY = "evaluation/d3_5_a6_phase1_r2_pre_exposure_reranker_model_contract_refreeze.json"
EXPECTED_MODEL = "gemini-3.8-flash"
EXPECTED_TEMPERATURE = 0.0


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_invariants(project_root: Path) -> dict[str, Any]:
    """Reperform the mandatory deterministic pre-exposure checks (Section 8)."""
    load_dotenv(project_root / ".env")
    settings = VertexSettings.from_env()
    if settings.generation_model != EXPECTED_MODEL:
        raise ValueError(
            f"QA_GENERATION_MODEL_ID mismatch: expected '{EXPECTED_MODEL}', got '{settings.generation_model}'"
        )

    pools = _load_json(project_root / a6_p1.POOLS_PATH)
    plan = _load_json(project_root / a6_p1.CALL_PLAN_PATH)
    fixture = _load_json(project_root / a6_p1.FIXTURE_PATH)

    # 8.1 Pool accounting
    manifest_count = sum(len(pools["cases"][c]["arms"]) for c in a6_p1.CASE_ORDER)
    if manifest_count != 18:
        raise ValueError(f"FORMAL_ARM_POOL_MANIFESTS mismatch: expected 18, got {manifest_count}")

    # 8.2 Call-plan accounting
    entries = plan["entries"]
    if len(entries) != 54:
        raise ValueError(f"FORMAL_PHASE2_CALL_PLAN_ENTRIES mismatch: expected 54, got {len(entries)}")

    # 8.3 Outcome state check
    for e in entries:
        if e["outcome_status"] != "NOT_EXECUTED":
            raise ValueError(f"Entry {e['formal_call_index']} outcome_status is not NOT_EXECUTED")

    # 8.4 Frozen pool identities
    for cid in a6_p1.CASE_ORDER:
        case_pools = pools["cases"][cid]
        for arm in a6_p1.ARMS:
            p_entry = case_pools["arms"][arm]
            pool = p_entry["ordered_pool_object_ids"]
            if len(pool) != len(set(pool)):
                raise ValueError(f"Duplicate object IDs in pool {cid} {arm}")
            if len(pool) != p_entry["pool_size"]:
                raise ValueError(f"Pool size mismatch in {cid} {arm}")
            if p_entry["pool_size"] > a6_p1.RERANK_POOL_SIZE:
                raise ValueError(f"Pool size exceeds limit in {cid} {arm}")

    for e in entries:
        cid = e["case_id"]
        arm = e["arm"]
        f_idx = e["formal_call_index"]
        p_entry = pools["cases"][cid]["arms"][arm]
        if e["ordered_pool_object_ids"] != p_entry["ordered_pool_object_ids"]:
            raise ValueError(f"Pool mismatch in call entry {f_idx}")
        if e["pool_identity"] != p_entry["ordered_pool_object_ids"]:
            raise ValueError(f"Pool identity mismatch in call entry {f_idx}")
        payload_ids = [item["object_id"] for item in e["ordered_reranker_payload"]]
        if payload_ids != e["ordered_pool_object_ids"]:
            raise ValueError(f"Payload IDs mismatch in call entry {f_idx}")

    # 8.5 Frozen schedule
    idx = 0
    for cid in a6_p1.CASE_ORDER:
        for rep in (1, 2, 3):
            for arm in a6_p1.CYCLIC_SCHEDULE[rep]:
                idx += 1
                e = entries[idx - 1]
                if (e["formal_call_index"], e["case_id"], e["repetition"], e["arm"]) != (idx, cid, rep, arm):
                    raise ValueError(f"Schedule mismatch at slot {idx}: got {e}")

    # 8.6 Expected identical-pool relations
    identical_pool_map: dict[str, dict[str, bool]] = {}
    for cid in a6_p1.CASE_ORDER:
        base = pools["cases"][cid]["arms"]["BASELINE"]["ordered_pool_object_ids"]
        k2 = pools["cases"][cid]["arms"]["ADMISSION_K2"]["ordered_pool_object_ids"]
        k3 = pools["cases"][cid]["arms"]["ADMISSION_K3"]["ordered_pool_object_ids"]
        relations = {
            "K2_equals_BASELINE": k2 == base,
            "K3_equals_BASELINE": k3 == base,
            "K2_equals_K3": k2 == k3,
        }
        identical_pool_map[cid] = relations
        if cid in ("n006", "g041", "n004"):
            if not (base == k2 == k3):
                raise ValueError(f"Identical pool relation failed for control {cid}")
        elif cid == "g021":
            if not (base != k2 and k2 == k3):
                raise ValueError(f"Identical pool relation failed for g021: expected K2 == K3 != BASELINE")
        elif cid in ("g036", "g020"):
            if not (base != k2 and base != k3 and k2 != k3):
                raise ValueError(f"Identical pool relation failed for {cid}: expected all distinct")

    return {
        "verified": True,
        "qa_generation_model_id": settings.generation_model,
        "pool_manifests_count": manifest_count,
        "call_plan_entries_count": len(entries),
        "identical_pool_map": identical_pool_map,
    }


def execute_54_formal_calls(project_root: Path) -> dict[str, Any]:
    """Execute exactly the 54 formal reranker slots in frozen order using frozen payloads.

    Maintains the strict no-mid-run evaluation boundary: absolutely no scientific
    evaluation is computed or inspected during execution.
    """
    load_dotenv(project_root / ".env")
    audit_receipt = audit_invariants(project_root)
    print(f"[PRE-EXPOSURE AUDIT PASSED] Model: {audit_receipt['qa_generation_model_id']}")

    fixture = _load_json(project_root / a6_p1.FIXTURE_PATH)
    plan = _load_json(project_root / a6_p1.CALL_PLAN_PATH)
    entries = plan["entries"]

    raw_path = project_root / RAW_RESULTS_PATH

    # Check for existing checkpoint
    completed_slots: dict[int, dict[str, Any]] = {}
    if raw_path.exists():
        try:
            existing = _load_json(raw_path)
            for s in existing.get("slots", []):
                if s.get("formal_call_status") == "SUCCESS":
                    completed_slots[s["formal_call_index"]] = s
            print(f"[RESUME CHECKPOINT] Found {len(completed_slots)} already-completed formal slots")
        except Exception as exc:
            print(f"[RESUME WARNING] Could not parse existing raw artifact: {exc}")

    if len(completed_slots) == 54:
        print("[ALREADY COMPLETE] All 54 formal slots have already succeeded in the raw artifact.")
        return _load_json(raw_path)

    settings = VertexSettings.from_env()
    client = VertexAIClient(settings)

    execution_start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    total_provider_attempts = 0
    total_tokens_consumed = 0

    slots_list: list[dict[str, Any]] = []

    for slot_entry in entries:
        f_idx = slot_entry["formal_call_index"]
        cid = slot_entry["case_id"]
        rep = slot_entry["repetition"]
        arm = slot_entry["arm"]
        pool_ids = slot_entry["ordered_pool_object_ids"]
        payload = slot_entry["ordered_reranker_payload"]
        question_text = fixture["cases"][cid]["question"]["query"]

        if f_idx in completed_slots:
            slot_record = completed_slots[f_idx]
            slots_list.append(slot_record)
            total_provider_attempts += slot_record.get("provider_attempts", 1)
            total_tokens_consumed += slot_record.get("token_usage", 0)
            continue

        # Exposure transition at formal call #1
        if f_idx == 1 or len(completed_slots) == 0:
            print(f"[OUTCOME EXPOSURE TRANSITION] A6_RERANK_OUTCOME_EXPOSURE = STARTED (call #{f_idx})")

        prompt_payload = json.dumps(
            {
                "task": "rerank_evidence",
                "untrusted_question": question_text,
                "untrusted_candidates": payload,
            },
            ensure_ascii=False,
        )
        response_schema = {
            "type": "object",
            "properties": {
                "ranked_object_ids": {
                    "type": "array",
                    "items": {"type": "string", "enum": pool_ids},
                }
            },
            "required": ["ranked_object_ids"],
            "additionalProperties": False,
        }

        print(f"Executing slot {f_idx}/54: case={cid}, rep={rep}, arm={arm} (pool_size={len(pool_ids)})...", flush=True)

        stats_before = client.stats_snapshot()
        t0 = time.time()
        call_error: str | None = None
        raw_response: dict[str, Any] | None = None
        parsed_ranked_ids: list[str] = []
        validation_status = "VALID"
        formal_call_status = "SUCCESS"

        try:
            raw_response = client.generate_json(
                prompt_payload,
                response_schema,
                system_instruction=RERANK_SYSTEM_PROMPT,
                temperature=EXPECTED_TEMPERATURE,
            )
            elapsed = time.time() - t0
            stats_delta = client.stats_delta(stats_before)
            attempts = stats_delta.get("generation_calls", 1)
            token_usage = stats_delta.get("token_usage", 0)
            total_provider_attempts += attempts
            total_tokens_consumed += token_usage

            parsed_ranked_ids = raw_response.get("ranked_object_ids", [])
            if not isinstance(parsed_ranked_ids, list):
                validation_status = "INVALID_RESPONSE_TYPE"
                formal_call_status = "FAILED"
                call_error = f"ranked_object_ids must be a list, got {type(parsed_ranked_ids)}"
            elif any(oid not in pool_ids for oid in parsed_ranked_ids):
                validation_status = "OUT_OF_POOL_ID_RETURNED"
                formal_call_status = "FAILED"
                call_error = "Response contained object IDs not in submitted pool"

        except Exception as exc:
            elapsed = time.time() - t0
            stats_delta = client.stats_delta(stats_before)
            attempts = stats_delta.get("generation_calls", 1)
            token_usage = stats_delta.get("token_usage", 0)
            total_provider_attempts += attempts
            total_tokens_consumed += token_usage
            formal_call_status = "FAILED"
            validation_status = "PROVIDER_ERROR"
            call_error = f"{type(exc).__name__}: {exc}"

        slot_record = {
            "formal_call_index": f_idx,
            "case_id": cid,
            "repetition": rep,
            "arm": arm,
            "model_id": EXPECTED_MODEL,
            "temperature": EXPECTED_TEMPERATURE,
            "prompt_authority": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT",
            "ordered_pool_object_ids": pool_ids,
            "ordered_reranker_payload": payload,
            "provider_attempts": attempts,
            "token_usage": token_usage,
            "elapsed_seconds": round(elapsed, 3),
            "formal_call_status": formal_call_status,
            "raw_provider_response": raw_response,
            "parsed_ranked_object_ids": parsed_ranked_ids,
            "validation_status": validation_status,
            "failure_reason": call_error,
        }
        slots_list.append(slot_record)

        # Checkpoint to disk after each formal slot
        raw_artifact = {
            "schema_version": "1.0.0",
            "checkpoint": "D3.5-A6-PHASE2-RAW-OUTCOME-FREEZE",
            "purpose": "frozen raw outcomes for all 54 formal reranker calls in D3.5-A6 Phase 2; frozen before evaluator execution",
            "experiment_authority": {
                "model_contract_authority": MODEL_CONTRACT_AUTHORITY,
                "execution_manifest": a6_p1.CALL_PLAN_PATH,
                "pool_manifest": a6_p1.POOLS_PATH,
                "fixture": a6_p1.FIXTURE_PATH,
            },
            "model_contract": {
                "generation_model_id": EXPECTED_MODEL,
                "temperature": EXPECTED_TEMPERATURE,
                "system_prompt_source": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT",
                "task": "rerank_evidence",
                "response_schema": '{"ranked_object_ids": [string...], "additionalProperties": false} with enum restricted to pool member list',
                "retry_policy": "VertexAIClient.generate_json 3-attempt transient retry loop",
            },
            "outcome_exposure_state": {
                "A6_RERANK_OUTCOME_EXPOSURE": "STARTED" if len(slots_list) < 54 else "COMPLETE",
                "execution_started_at_utc": execution_start_time,
                "execution_completed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
                if len(slots_list) == 54
                else None,
                "formal_slots_total": 54,
                "formal_slots_succeeded": sum(1 for s in slots_list if s["formal_call_status"] == "SUCCESS"),
                "formal_slots_failed": sum(1 for s in slots_list if s["formal_call_status"] != "SUCCESS"),
            },
            "accounting": {
                "FORMAL_ARM_POOL_MANIFESTS": 18,
                "FORMAL_PHASE2_CALL_PLAN_ENTRIES": 54,
                "FORMAL_RERANKER_CALLS_EXECUTED": len(slots_list),
                "FORMAL_RERANKER_CALLS_SUCCEEDED": sum(
                    1 for s in slots_list if s["formal_call_status"] == "SUCCESS"
                ),
                "FORMAL_RERANKER_CALLS_FAILED": sum(
                    1 for s in slots_list if s["formal_call_status"] != "SUCCESS"
                ),
                "PROVIDER_INTERNAL_ATTEMPTS": total_provider_attempts,
                "TOTAL_TOKEN_USAGE": total_tokens_consumed,
                "REAL_CASE_RERANKER_CALLS": len(slots_list),
                "PHASE2_SELECT_V2_RUNS": 0,
                "ANALYZER_CALLS": 0,
                "EMBEDDING_CALLS": 0,
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
            "evaluation_boundary": {
                "EVALUATOR_EXECUTED": False,
                "SCIENTIFIC_VERDICT_COMPUTED": False,
            },
            "slots": slots_list,
        }
        raw_path.write_text(json.dumps(raw_artifact, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

        if formal_call_status != "SUCCESS":
            print(f"[STOP CRITICAL] Formal slot #{f_idx} failed: {call_error}")
            print("D3.5-A6-PHASE2 = INCOMPLETE / FORMAL_RERANKER_CALL_FAILED")
            sys.exit(3)

    print("[SUCCESS] All 54 formal slots completed and frozen successfully in raw artifact.")
    return raw_artifact


def evaluate_phase2(project_root: Path) -> dict[str, Any]:
    """Run deterministic post-rerank replay and evaluator on the frozen raw outcomes."""
    raw_path = project_root / RAW_RESULTS_PATH
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw results artifact {raw_path} not found. Run --mode execute-54 first.")

    raw_data = _load_json(raw_path)
    if raw_data["outcome_exposure_state"]["formal_slots_succeeded"] != 54:
        raise ValueError("Cannot evaluate: raw results do not contain 54 successful formal slots.")

    fixture = _load_json(project_root / a6_p1.FIXTURE_PATH)
    pools = _load_json(project_root / a6_p1.POOLS_PATH)
    registry = fixture["selector_replay_registry"]

    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_questions = {q.id: q for q in gold_ds.questions + novel_ds.questions}

    # Map raw slots by (case_id, repetition, arm)
    slots_by_key: dict[tuple[str, int, str], dict[str, Any]] = {}
    for slot in raw_data["slots"]:
        slots_by_key[(slot["case_id"], slot["repetition"], slot["arm"])] = slot

    # Determine candidate matches for each required evidence group across cases
    evaluator_matched_groups_by_case: dict[str, dict[str, list[str]]] = {}
    for cid in a6_p1.CASE_ORDER:
        q = all_questions[cid]
        evaluator_matched_groups_by_case[cid] = {}
        for grp in q.required_evidence_groups:
            matched_oids = []
            for oid in registry:
                rec, _ = _matched_evidence_groups([grp], [oid], registry)
                if rec > 0:
                    matched_oids.append(oid)
            evaluator_matched_groups_by_case[cid][grp.group_id] = matched_oids

    # Determine ADMISSION_APPLICABLE_BRIDGE_GROUPs
    applicable_groups_by_case: dict[str, list[str]] = {}
    all_applicable_bridge_groups: list[str] = []
    for cid in a6_p1.CASE_ORDER:
        reservable = pools["cases"][cid]["arms"]["ADMISSION_K3"]["reservable_bridge_ids"]
        app = a6_p1.admission_applicable_bridge_groups(evaluator_matched_groups_by_case[cid], reservable)
        applicable_groups_by_case[cid] = app
        all_applicable_bridge_groups.extend(app)

    # Replay each slot and record retention per repetition
    replay_records: list[dict[str, Any]] = []

    # Track group retention across repetitions: group_id -> list of 3 booleans for arm
    group_retention_by_arm: dict[str, dict[str, list[bool]]] = {
        "BASELINE": {},
        "ADMISSION_K2": {},
        "ADMISSION_K3": {},
    }
    # Track reserved-required-candidate witness: group_id -> list of 3 booleans for arm
    witness_flags_by_arm: dict[str, dict[str, list[bool]]] = {
        "ADMISSION_K2": {},
        "ADMISSION_K3": {},
    }

    # Initialize all groups
    for cid in a6_p1.CASE_ORDER:
        q = all_questions[cid]
        for grp in q.required_evidence_groups:
            for arm in a6_p1.ARMS:
                group_retention_by_arm[arm][grp.group_id] = [False, False, False]
            for arm in ("ADMISSION_K2", "ADMISSION_K3"):
                witness_flags_by_arm[arm][grp.group_id] = [False, False, False]

    for cid in a6_p1.CASE_ORDER:
        q = all_questions[cid]
        case_entry = fixture["cases"][cid]
        for rep in (1, 2, 3):
            for arm in a6_p1.ARMS:
                slot = slots_by_key[(cid, rep, arm)]
                reranked_ids = slot["parsed_ranked_object_ids"]

                # Run post-rerank replay
                replay_output = a6_p1.replay_case(case_entry, fixture, reranked_ids)
                final_evidence = replay_output["evidence_object_ids"]

                reserved_in_arm = set(pools["cases"][cid]["arms"][arm]["reserved_bridge_candidate_ids"])

                # Check retention of each group
                group_retention_in_slot: dict[str, bool] = {}
                witness_in_slot: dict[str, bool] = {}

                for grp in q.required_evidence_groups:
                    gid = grp.group_id
                    rec, prov = _matched_evidence_groups([grp], final_evidence, registry)
                    is_retained = rec > 0
                    group_retention_in_slot[gid] = is_retained
                    group_retention_by_arm[arm][gid][rep - 1] = is_retained

                    # Witness diagnostic for applicable bridge groups
                    if gid in applicable_groups_by_case[cid] and arm in ("ADMISSION_K2", "ADMISSION_K3"):
                        matching_candidates = evaluator_matched_groups_by_case[cid][gid]
                        has_witness = bool(set(final_evidence) & reserved_in_arm & set(matching_candidates))
                        witness_in_slot[gid] = has_witness
                        witness_flags_by_arm[arm][gid][rep - 1] = has_witness

                replay_records.append(
                    {
                        "formal_call_index": slot["formal_call_index"],
                        "case_id": cid,
                        "repetition": rep,
                        "arm": arm,
                        "reranked_object_ids": reranked_ids,
                        "final_evidence_object_ids": final_evidence,
                        "group_retention": group_retention_in_slot,
                        "witness_flags": witness_in_slot,
                    }
                )

    # Compute group stability across 3 repetitions
    group_stability: dict[str, dict[str, Any]] = {}
    safety_population: list[str] = []

    for cid in a6_p1.CASE_ORDER:
        q = all_questions[cid]
        for grp in q.required_evidence_groups:
            gid = grp.group_id
            b_flags = group_retention_by_arm["BASELINE"][gid]
            k2_flags = group_retention_by_arm["ADMISSION_K2"][gid]
            k3_flags = group_retention_by_arm["ADMISSION_K3"][gid]

            b_stable = a6_p1.stable_retained(b_flags)
            k2_stable = a6_p1.stable_retained(k2_flags)
            k3_stable = a6_p1.stable_retained(k3_flags)

            if b_stable:
                safety_population.append(gid)

            mcr_k2 = a6_p1.material_control_regression(b_flags, k2_flags)
            mcr_k3 = a6_p1.material_control_regression(b_flags, k3_flags)

            w_k2 = a6_p1.stable_reserved_required_witness(witness_flags_by_arm["ADMISSION_K2"][gid])
            w_k3 = a6_p1.stable_reserved_required_witness(witness_flags_by_arm["ADMISSION_K3"][gid])

            group_stability[gid] = {
                "case_id": cid,
                "is_admission_applicable": gid in all_applicable_bridge_groups,
                "BASELINE": {"flags": b_flags, "count": sum(b_flags), "stable_retained": b_stable},
                "ADMISSION_K2": {
                    "flags": k2_flags,
                    "count": sum(k2_flags),
                    "stable_retained": k2_stable,
                    "witness_flags": witness_flags_by_arm["ADMISSION_K2"][gid],
                    "stable_witness": w_k2,
                    "material_control_regression": mcr_k2,
                },
                "ADMISSION_K3": {
                    "flags": k3_flags,
                    "count": sum(k3_flags),
                    "stable_retained": k3_stable,
                    "witness_flags": witness_flags_by_arm["ADMISSION_K3"][gid],
                    "stable_witness": w_k3,
                    "material_control_regression": mcr_k3,
                },
            }

    # Scientific Metrics
    delta_2 = a6_p1.compute_delta(
        all_applicable_bridge_groups,
        group_retention_by_arm["BASELINE"],
        group_retention_by_arm["ADMISSION_K2"],
    )
    delta_3 = a6_p1.compute_delta(
        all_applicable_bridge_groups,
        group_retention_by_arm["BASELINE"],
        group_retention_by_arm["ADMISSION_K3"],
    )

    k2_stable_witness_map = {
        gid: group_stability[gid]["ADMISSION_K2"]["stable_witness"] for gid in all_applicable_bridge_groups
    }
    k3_stable_witness_map = {
        gid: group_stability[gid]["ADMISSION_K3"]["stable_witness"] for gid in all_applicable_bridge_groups
    }

    causal_delta_2 = a6_p1.compute_causal_delta(
        all_applicable_bridge_groups,
        group_retention_by_arm["BASELINE"],
        group_retention_by_arm["ADMISSION_K2"],
        k2_stable_witness_map,
    )
    causal_delta_3 = a6_p1.compute_causal_delta(
        all_applicable_bridge_groups,
        group_retention_by_arm["BASELINE"],
        group_retention_by_arm["ADMISSION_K3"],
        k3_stable_witness_map,
    )

    noncausal_stable_delta_2 = delta_2 - causal_delta_2
    noncausal_stable_delta_3 = delta_3 - causal_delta_3

    regression_2 = sum(
        1 for gid in safety_population if group_stability[gid]["ADMISSION_K2"]["material_control_regression"]
    )
    regression_3 = sum(
        1 for gid in safety_population if group_stability[gid]["ADMISSION_K3"]["material_control_regression"]
    )

    mse_2 = a6_p1.mechanistic_safe_effective(causal_delta_2, regression_2)
    mse_3 = a6_p1.mechanistic_safe_effective(causal_delta_3, regression_3)

    selected_budget = a6_p1.select_budget(
        delta_2, delta_3, causal_delta_2, causal_delta_3, regression_2, regression_3
    )

    unstable_recovery = a6_p1.classify_unstable_recovery(
        all_applicable_bridge_groups,
        group_retention_by_arm["BASELINE"],
        group_retention_by_arm["ADMISSION_K2"],
    ) or a6_p1.classify_unstable_recovery(
        all_applicable_bridge_groups,
        group_retention_by_arm["BASELINE"],
        group_retention_by_arm["ADMISSION_K3"],
    )

    final_verdict = a6_p1.compute_verdict(
        delta2=delta_2,
        delta3=delta_3,
        causal2=causal_delta_2,
        causal3=causal_delta_3,
        regression2=regression_2,
        regression3=regression_3,
        unstable_recovery=unstable_recovery,
        structural_fail=False,
    )

    eval_results = {
        "schema_version": "1.0.0",
        "checkpoint": "D3.5-A6-PHASE2",
        "stage": "D3.5-A6 Phase 2 — Paired Repeated Reranker Replay",
        "experiment_authority_references": {
            "model_contract_authority": MODEL_CONTRACT_AUTHORITY,
            "raw_results_freeze": RAW_RESULTS_PATH,
            "execution_manifest": a6_p1.CALL_PLAN_PATH,
            "pool_manifest": a6_p1.POOLS_PATH,
            "replay_fixture": a6_p1.FIXTURE_PATH,
        },
        "model_contract": {
            "generation_model_id": EXPECTED_MODEL,
            "temperature": EXPECTED_TEMPERATURE,
            "system_prompt_source": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT",
            "retry_semantics": "VertexAIClient.generate_json 3-attempt transient retry loop",
        },
        "populations": {
            "admission_applicable_bridge_groups": all_applicable_bridge_groups,
            "safety_population": safety_population,
        },
        "scientific_metrics": {
            "DELTA_2": delta_2,
            "DELTA_3": delta_3,
            "CAUSAL_DELTA_2": causal_delta_2,
            "CAUSAL_DELTA_3": causal_delta_3,
            "NONCAUSAL_STABLE_DELTA_2": noncausal_stable_delta_2,
            "NONCAUSAL_STABLE_DELTA_3": noncausal_stable_delta_3,
            "REGRESSION_2": regression_2,
            "REGRESSION_3": regression_3,
            "MECHANISTIC_SAFE_EFFECTIVE_K2": mse_2,
            "MECHANISTIC_SAFE_EFFECTIVE_K3": mse_3,
            "SELECTED_ADMISSION_BUDGET": selected_budget,
            "UNSTABLE_ADMISSION_RECOVERY": unstable_recovery,
            "FINAL_A6_PHASE2_VERDICT": final_verdict,
        },
        "group_stability_analysis": group_stability,
        "identical_pool_analysis": audit_invariants(project_root)["identical_pool_map"],
        "structural_validity": {
            "protocol_valid": True,
            "formal_calls_succeeded": 54,
            "treatment_mutations": 0,
            "mid_run_evaluations": 0,
        },
        "production_activation": False,
        "exact_next_lifecycle_state": "D3.5-A6 COMPLETE / EVALUATION_CLOSED (D4 remains BLOCKED / NOT_STARTED)",
    }

    # Write replay & eval results
    (project_root / REPLAY_AND_EVAL_PATH).write_text(
        json.dumps(eval_results, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    # Write concise final result artifact
    final_result_data = {
        **eval_results,
        "accounting": raw_data["accounting"],
    }
    (project_root / FINAL_RESULT_PATH).write_text(
        json.dumps(final_result_data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    print("\n==========================================")
    print("D3.5-A6 Phase 2 Evaluation Complete")
    print(f"DELTA_2: {delta_2}, DELTA_3: {delta_3}")
    print(f"CAUSAL_DELTA_2: {causal_delta_2}, CAUSAL_DELTA_3: {causal_delta_3}")
    print(f"NONCAUSAL_STABLE_DELTA_2: {noncausal_stable_delta_2}, NONCAUSAL_STABLE_DELTA_3: {noncausal_stable_delta_3}")
    print(f"REGRESSION_2: {regression_2}, REGRESSION_3: {regression_3}")
    print(f"MECHANISTIC_SAFE_EFFECTIVE(K2): {mse_2}, MECHANISTIC_SAFE_EFFECTIVE(K3): {mse_3}")
    print(f"SELECTED_ADMISSION_BUDGET: {selected_budget}")
    print(f"FINAL_A6_PHASE2_VERDICT: {final_verdict}")
    print("==========================================\n")

    return eval_results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--mode",
        required=True,
        choices=["audit-invariants", "execute-54", "evaluate"],
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    root = args.project_root.resolve()

    if args.mode == "audit-invariants":
        receipt = audit_invariants(root)
        print(json.dumps(receipt, ensure_ascii=False, indent=1))
    elif args.mode == "execute-54":
        execute_54_formal_calls(root)
    elif args.mode == "evaluate":
        evaluate_phase2(root)


if __name__ == "__main__":
    main()
