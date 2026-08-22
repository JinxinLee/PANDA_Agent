"""C6-A1R2 semantic-cohort eligibility correction (static derivation).

Re-derives SEMANTIC_POLICY_COHORT from the authoritative replay v2 using the
original C6-A1 preregistered rule ("all SEMANTIC_REPLAY cases up to 20,
deterministic by intent + case ID"). The A1R2 repair verification had
accidentally added two global-core bookkeeping conditions — original
live-cohort membership and supplemental_coverage exclusion — that the
preregistered semantic rule does not contain.

Static only: parses frozen JSON/JSONL artifacts, performs no model, retrieval,
embedding, SQL, or Qdrant calls, and never touches relevance data.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PREREG = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "manifests"
    / "phase_c_c6_a0_a1_fusion_replay_preregistration_v1.json"
)
REPAIR = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "manifests"
    / "phase_c_c6_a1r2_provenance_repair_v1.json"
)
REPLAY_V2 = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "replay"
    / "phase_c_c6_current_plan_candidate_replay_v2.jsonl"
)
A1R2_FROZEN = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_preregistration_frozen_v1.json"
OUT = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "manifests"
    / "phase_c_c6_a1r2_semantic_cohort_correction_v1.json"
)

SIX_CHANNELS = ("exact", "raw_dense", "sparse", "paper", "workflow", "graph")
FUSING = ("PRESENT_NONEMPTY", "PRESENT_EMPTY")
MIN_CASES = 8
MIN_INTENTS = 2
MAX_SEMANTIC_CASES = 20

BANNED_FIELDS = [
    "relevance",
    "expected_evidence",
    "required_evidence",
    "critical_evidence",
    "answer_requirement",
    "gold_label",
    "evidence_group",
]


def main() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    repair = json.loads(REPAIR.read_text(encoding="utf-8"))
    a1r2 = json.loads(A1R2_FROZEN.read_text(encoding="utf-8"))
    v2_text = REPLAY_V2.read_text(encoding="utf-8")
    rows = [json.loads(line) for line in v2_text.splitlines() if line.strip()]

    # --- original preregistered semantic rule (authoritative source) ---
    semantic_rule = prereg["preregistered_cohort_rules"]["SEMANTIC_POLICY_COHORT"]
    rule_text = semantic_rule["rule"]
    prereg_min_cases = semantic_rule["minimum_for_substantive_semanticdense_evidence"]
    prereg_min_intents = semantic_rule["minimum_represented_intents"]
    assert rule_text == "all SEMANTIC_REPLAY cases up to 20, deterministic by intent + case ID"
    assert prereg_min_cases == MIN_CASES and prereg_min_intents == MIN_INTENTS
    coverage_expansion_allowance = semantic_rule["current_status"]

    # --- replay v2 structural checks ---
    assert len(rows) == 34, f"expected 34 replay-v2 rows, got {len(rows)}"
    banned_hits = [b for b in BANNED_FIELDS if b in v2_text.casefold()]

    # --- global core preservation ---
    core_ids = sorted(a1r2["core_capture_cohort"])
    assert len(core_ids) == 30, f"expected 30 core cases, got {len(core_ids)}"
    v2_core = sorted(r["case_id"] for r in rows if r["case_id"] in set(core_ids))
    core_ids_identical = v2_core == core_ids
    supplemental = {"g039", "g040", "g055"}
    supplemental_not_in_core = not (supplemental & set(core_ids))

    # --- identity gate carried over from the repair (condition 8) ---
    identity_gate_status = repair["identity_gate"]["result"]

    # --- structural semantic eligibility over replay-v2 rows ---
    intent_by_case = {**a1r2["intent_by_case"]}
    eligible: list[dict] = []
    exclusions: dict[str, str] = {}
    for row in rows:
        case_id = row["case_id"]
        sd = row["channels"].get("semantic_dense") or {}
        if sd.get("semantic_view_active") is not True:
            exclusions[case_id] = "semantic view inactive (semantic_view_active=false)"
            continue
        if sd.get("execution_status") != "OK":
            exclusions[case_id] = f"semantic_dense execution {sd.get('execution_status')}"
            continue
        if sd.get("availability_state") not in FUSING:
            exclusions[case_id] = f"semantic_dense availability {sd.get('availability_state')}"
            continue
        incomplete = [
            ch
            for ch in SIX_CHANNELS
            if row["channels"][ch]["availability_state"] not in FUSING
        ]
        if incomplete:
            exclusions[case_id] = f"production channels not complete: {incomplete}"
            continue
        if row.get("formal_english_scope") is not True:
            exclusions[case_id] = "not in inherited formal-English product scope"
            continue
        if row.get("frozen_plan_prompt_version") != "3.7.0":
            exclusions[case_id] = f"plan prompt {row.get('frozen_plan_prompt_version')}"
            continue
        if not row.get("frozen_plan_source"):
            exclusions[case_id] = "no faithful frozen plan source"
            continue
        intent = row["intent"]
        if case_id in intent_by_case and intent_by_case[case_id] != intent:
            exclusions[case_id] = "intent label conflicts with frozen A1R2 metadata"
            continue
        eligible.append({"case_id": case_id, "intent": intent, "row_role": row["row_role"]})

    # --- deterministic ordering: intent ascending, then case ID ascending ---
    cohort = sorted(eligible, key=lambda c: (c["intent"], c["case_id"]))
    cohort = cohort[:MAX_SEMANTIC_CASES]
    cohort_ids = [c["case_id"] for c in cohort]
    intent_counts = Counter(c["intent"] for c in cohort)
    represented_intents = sorted(intent_counts)
    semantic_eligible = len(cohort_ids) >= MIN_CASES and len(represented_intents) >= MIN_INTENTS

    # --- replay v2 unchanged (git working tree must not modify it) ---
    v2_changed = bool(
        subprocess.run(
            ["git", "status", "--porcelain", "--", str(REPLAY_V2.relative_to(PROJECT_ROOT))],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        ).stdout.strip()
    )

    artifact = {
        "schema_version": 1,
        "task": "C6-A1R2 semantic-cohort eligibility correction",
        "artifact_id": "phase_c_c6_a1r2_semantic_cohort_correction_v1",
        "phase": "C6",
        "recorded_on": datetime.now(timezone.utc).isoformat(),
        "source_head": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=PROJECT_ROOT
        ).stdout.strip(),
        "correction_timing": "before any C6-A2 relevance outcome (C6-A2 was never executed)",
        "references": {
            "original_preregistration": PREREG.relative_to(PROJECT_ROOT).as_posix(),
            "provenance_repair": REPAIR.relative_to(PROJECT_ROOT).as_posix(),
            "authoritative_replay": REPLAY_V2.relative_to(PROJECT_ROOT).as_posix(),
        },
        "original_semantic_preregistration_rule": {
            "rule": rule_text,
            "minimum_for_substantive_semanticdense_evidence": prereg_min_cases,
            "minimum_represented_intents": prereg_min_intents,
            "separately_authorized_coverage_expansion_allowance": coverage_expansion_allowance,
        },
        "accidental_a1r2_restriction": {
            "conditions": [
                "case_id in original_live_capture_cohort",
                "row_role != supplemental_coverage",
            ],
            "introduced_in": "repair_c6_a1r2_build_v2.py verification 5",
            "why_not_authoritative": (
                "Both conditions belong to global A2 core bookkeeping "
                "(CORE_POLICY_COHORT membership for P0-P3). The original C6-A1 "
                "semantic rule contains neither; its current_status explicitly "
                "allows a separately authorized candidate-coverage task to "
                "expand the frozen semantic cohort, and the A1R2 refresh plus "
                "provenance repair was such a task. A replay-v2 case can be "
                "supplemental for the global cohort while remaining eligible "
                "for the independent Semantic Policy Cohort."
            ),
        },
        "semantic_eligibility_structural_rule": [
            "formal_english_scope = true (inherited formal-English product scope)",
            "faithful current C2 prompt-3.7 plan provenance (frozen_plan_prompt_version = 3.7.0 with an explicit frozen_plan_source)",
            "authoritative structurally valid replay-v2 row",
            "semantic_view_active = true",
            "semantic_dense execution_status = OK",
            "semantic_dense availability PRESENT_NONEMPTY or PRESENT_EMPTY",
            "all six CURRENT production channels (exact, raw_dense, sparse, paper, workflow, graph) PRESENT_NONEMPTY or PRESENT_EMPTY",
            "source/index identity compatible (identity gate MATCH from the provenance repair)",
            "captured before any C6-A2 relevance outcome",
            "no relevance information used for membership",
        ],
        "mechanically_derived_eligible_case_ids": cohort_ids,
        "deterministic_semantic_cohort_order": {
            "rule": "intent ascending, then case ID ascending (all eligible cases up to 20)",
            "ordered_ids": cohort_ids,
        },
        "semantic_cohort_count": len(cohort_ids),
        "semantic_intent_distribution": dict(sorted(intent_counts.items())),
        "represented_intent_count": len(represented_intents),
        "case_exclusions": {k: v for k, v in sorted(exclusions.items()) if k == "g040"},
        "g040_exclusion_reason": exclusions.get(
            "g040", "g040 was not excluded unexpectedly"
        ),
        "minimum_case_threshold": MIN_CASES,
        "minimum_intent_threshold": MIN_INTENTS,
        "gate": {
            "case_count_ge_8": len(cohort_ids) >= MIN_CASES,
            "represented_intents_ge_2": len(represented_intents) >= MIN_INTENTS,
        },
        "semantic_a2_evidence_eligible": semantic_eligible,
        "global_core_count": 30,
        "global_core_ids_unchanged": core_ids_identical,
        "supplemental_not_added_to_global_core": supplemental_not_in_core,
        "replay_v2_unchanged": not v2_changed,
        "candidate_recapture": 0,
        "relevance_outcomes_inspected": 0,
        "live_retrieval_calls": 0,
        "banned_field_hits_in_replay_v2": banned_hits,
        "production_behavior_unchanged": True,
        "novel_replay_status": "ABSENT",
        "semantic_eligibility_scope_note": (
            "semantic_a2_evidence_eligible = true only authorizes substantive "
            "P4/P5 evaluation coverage in C6-A2; it does not mean SemanticDense "
            "is beneficial or production-bound, and novel corroboration remains "
            "required for any new production fusion policy"
        ),
        "historical_record_preserved": {
            "phase_c_c6_a1r2_provenance_repair_v1.semantic_a2": repair["semantic_a2"],
            "note": (
                "The repair artifact's six-case derivation "
                "(semantic_a2_evidence_eligible = false) remains an auditable "
                "historical record; this correction supersedes only the "
                "Semantic Policy Cohort membership/eligibility interpretation "
                "for future C6-A2 use"
            ),
        },
        "global_vs_semantic_cohort_contract": {
            "GLOBAL_POLICY_COHORT": {
                "count": 30,
                "used_for": ["P0 CURRENT", "P1 RAW_DENSE_CENTERED", "P2 EXACT_HEAVY", "P3 SPARSE_HEAVY"],
                "membership": "frozen original 30-case core; unchanged",
            },
            "SEMANTIC_POLICY_COHORT": {
                "count": len(cohort_ids),
                "used_for": ["P4 SEMANTIC_AUXILIARY_25", "P5 SEMANTIC_EXPANSION_ONLY"],
                "membership": "mechanically derived current faithful semantic cases; independent of global-core membership",
            },
        },
        "c6_a2_execution_eligibility": {
            "global_policy_evidence_eligible": True,
            "semantic_policy_evidence_eligible": semantic_eligible,
        },
    }

    # --- focused static assertions ---
    assert not banned_hits, f"banned relevance fields present: {banned_hits}"
    assert core_ids_identical and supplemental_not_in_core
    assert identity_gate_status == "MATCH"
    assert not v2_changed
    assert len(cohort_ids) == 8, f"expected 8 semantic cases, got {len(cohort_ids)}: {cohort_ids}"
    assert set(cohort_ids) == {"g008", "g039", "g050", "g055", "g110", "g113", "g114", "g115"}
    assert cohort_ids == ["g050", "g055", "g039", "g008", "g110", "g113", "g114", "g115"]
    assert exclusions["g040"] == "semantic view inactive (semantic_view_active=false)"

    OUT.write_text(json.dumps(artifact, indent=1), encoding="utf-8")
    print(json.dumps({
        "semantic_cohort": cohort_ids,
        "count": len(cohort_ids),
        "intent_distribution": dict(sorted(intent_counts.items())),
        "represented_intents": len(represented_intents),
        "semantic_a2_evidence_eligible": semantic_eligible,
        "global_core_count": 30,
        "core_ids_identical": core_ids_identical,
        "replay_v2_unchanged": not v2_changed,
        "artifact": str(OUT.relative_to(PROJECT_ROOT)),
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
