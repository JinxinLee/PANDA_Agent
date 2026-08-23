"""Static integrity audit for the C7-A0 selection-boundary inventory.

This script reads repository text and JSON only.  It intentionally does not
import production modules or instantiate a Retriever.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE = "c4510bd4f09f6dfaab47ef87260b4c1ce9843f8a"
INVENTORY = ROOT / "evaluation/baselines/manifests/phase_c_c7_a0_selection_boundary_replay_inventory_v1.json"
RETRIEVAL = ROOT / "src/panda_agent/retrieval.py"
ROADMAP = ROOT / "docs/GENERALIZATION_ROADMAP.md"
STATUS = ROOT / "docs/EVALUATION_STATUS.md"
ALLOWED_CHANGED = {
    "evaluation/scripts/audit_c7_a0_selection_boundary_replay.py",
    "evaluation/baselines/manifests/phase_c_c7_a0_selection_boundary_replay_inventory_v1.json",
    "docs/EVALUATION_STATUS.md",
    "docs/GENERALIZATION_ROADMAP.md",
}
TRACE_PROVENANCE_FIELDS = {
    "retrieval_or_query_analyzer_prompt_version",
    "current_pipeline_fidelity",
    "retrieval_plan_presence_and_completeness",
    "exact_stream_metadata",
    "scores_and_channels_metadata",
    "full_payload_metadata",
    "full_selector_consideration_order",
    "selector_implementation_generation",
    "source_and_index_identity",
    "reranker_presence",
    "trace_schema_compatibility",
    "external_read_free_replay",
    "can_reproduce_current_selector",
    "classification_evidence",
}


def run(*args: str) -> str:
    return subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=True).stdout


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    source = RETRIEVAL.read_text(encoding="utf-8")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    required = {
        "schema_version", "task", "source_head", "audit_timing", "authoritative_inputs",
        "c6_lifecycle_prerequisite", "c7_ownership_boundary", "held_constant_components",
        "c7_owned_deterministic_operations", "pipeline_stage_map", "current_selector_semantics",
        "current_source_budget_semantics", "constraint_dimension_findings",
        "required_source_provenance_findings", "mandatory_protected_exact_behavior",
        "current_production_trace_fields", "minimum_faithful_selector_replay_state",
        "minimum_attribution_state", "hypotheses", "trace_family_inventory",
        "current_pipeline_full_replay_case_count", "post_reranker_replay_capability",
        "C7_A2_FROZEN_CAPTURE_REQUIRED", "reranker_quality_evaluated",
        "selector_outcome_evaluated", "production_behavior_changed", "c7_a0_verdict",
        "c7_a1_eligibility",
    }
    require(required <= set(inventory), "inventory required fields missing")
    require(inventory["source_head"] == BASELINE, "inventory source head differs from accepted baseline")
    subprocess.run(["git", "cat-file", "-e", f"{BASELINE}^{{commit}}"], cwd=ROOT, check=True)
    subprocess.run(["git", "merge-base", "--is-ancestor", BASELINE, "HEAD"], cwd=ROOT, check=True)
    require(inventory["post_reranker_replay_capability"] in {"FULL", "PARTIAL", "INSUFFICIENT"}, "invalid replay capability")
    require(inventory["c7_a0_verdict"] in {"PASS", "INCONCLUSIVE"}, "invalid A0 verdict")
    require(inventory["reranker_quality_evaluated"] is False, "reranker must not be evaluated")
    require(inventory["selector_outcome_evaluated"] is False, "selector outcome must not be evaluated")
    require(inventory["production_behavior_changed"] is False, "production behavior must remain unchanged")
    require(len(inventory["hypotheses"]) == 8, "all eight hypotheses are required")
    for hypothesis in inventory["hypotheses"]:
        require(hypothesis["verdict"] in {"CONFIRMED", "REFUTED", "PARTIALLY_TRUE"}, "invalid hypothesis verdict")
        require(bool(hypothesis.get("code_evidence")), "hypothesis lacks code evidence")
    stages = inventory["pipeline_stage_map"]
    require(set(stages) == {"F", "R", "M", "P", "S"}, "five pipeline stages are required")
    require("ordered = list(dict.fromkeys([*reranked, *fused_order]))" in source, "missing Stage-M R-plus-F fallback construction")
    require("ordered=list(dict.fromkeys([*hinted_first,*required_first,*symbol_first,*ordered]))" in source, "missing policy reorder")
    require("ranked_object_ids = ordered[:30]" in source, "ranked_object_ids must remain a P prefix")
    require("select_final_evidence(" in source and "for rank, object_id in enumerate(ordered, 1):" in source, "selector must consume full P order")
    require("math.ceil(value * final_evidence_limit)" in source, "source budgets must be mechanically tied to caps")
    require("object_id not in mandatory_symbol_ids" in source, "mandatory exact cap exemption missing")
    classifications = {item["classification"] for item in inventory["trace_family_inventory"]}
    require(classifications <= {"FULL_SELECTOR_REPLAY", "PARTIAL_ATTRIBUTION_ONLY", "HISTORICAL_ONLY", "INSUFFICIENT"}, "invalid trace classification")
    for item in inventory["trace_family_inventory"]:
        require(TRACE_PROVENANCE_FIELDS <= set(item), f"trace provenance fields missing for {item.get('identity')}")
        for field in TRACE_PROVENANCE_FIELDS:
            require(isinstance(item[field], (str, bool)) or item[field] is None, f"invalid {field} for {item['identity']}")
        require(isinstance(item["case_count"], int) and item["case_count"] >= 0, "invalid trace case count")
        if item["classification"] == "FULL_SELECTOR_REPLAY":
            require(item["frozen_only"] is True and item["external_payload_lookup_required"] is False, "FULL requires frozen payloads")
            require(all(item["stages"].get(stage) is True for stage in ("F", "R", "M", "P", "S")), "FULL requires every stage")
            require(item["full_selector_consideration_order"] is True, "FULL requires full consideration order")
    receipts = next(item for item in inventory["trace_family_inventory"] if item["identity"] == "phase_c_c6_a2_policy_receipts_v1.jsonl")
    require(receipts["case_count"] == 33 and receipts["record_count"] == 144, "C6 receipt cases/records mismatch")
    require(receipts["policy_row_counts"] == {"CURRENT": 38, "EXACT_HEAVY": 30, "RAW_DENSE_CENTERED": 30, "SPARSE_HEAVY": 30, "SEMANTIC_AUX25": 8, "SEMANTIC_EXPANSION_ONLY": 8}, "C6 receipt policy rows mismatch")
    novel = next(item for item in inventory["trace_family_inventory"] if item["identity"] == "empty novel_retrieval_traces.jsonl families")
    require(novel["case_count"] == 0 and novel["record_count"] == 0, "empty novel traces must have zero records")
    require(novel["classification"] == "INSUFFICIENT" and all(value is False for value in novel["stages"].values()), "empty novel traces cannot inherit stage capability")
    require(novel["paths"] == ["evaluation/baselines/generalization-a3-bootstrap-20260813-limited/novel_retrieval_traces.jsonl", "evaluation/baselines/english-gold-stratified-bootstrap-v1-20260813/novel_retrieval_traces.jsonl"], "empty novel trace paths mismatch")
    require(inventory["current_pipeline_full_replay_case_count"] == 0, "FULL case count must be zero")
    require(inventory["C7_A2_FROZEN_CAPTURE_REQUIRED"] is True, "capture must be required when replay is not FULL")
    require("phase_c_c6_current_plan_candidate_replay_v2.jsonl" in json.dumps(inventory), "C6 replay boundary missing")
    changed = {line for line in run("git", "diff", "--name-only", BASELINE).splitlines() if line}
    changed.update(line for line in run("git", "ls-files", "--others", "--exclude-standard").splitlines() if line)
    require(changed <= ALLOWED_CHANGED, f"out-of-scope changed paths: {sorted(changed - ALLOWED_CHANGED)}")
    subprocess.run(["git", "diff", "--quiet", BASELINE, "--", "src", "configs/retrieval_policies.yaml", "evaluation/baselines/replay"], cwd=ROOT, check=True)
    require("C7-A0" in ROADMAP.read_text(encoding="utf-8") and "C7-A0" in STATUS.read_text(encoding="utf-8"), "C7-A0 documentation missing")
    print(json.dumps({"status": "PASS", "source_head": BASELINE, "baseline_ancestor_or_equal": True, "replay_capability": inventory["post_reranker_replay_capability"], "full_replay_cases": 0, "trace_families": len(inventory["trace_family_inventory"]), "changed_paths": sorted(changed)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"C7-A0 static audit failed: {error}", file=sys.stderr)
        raise SystemExit(1)
