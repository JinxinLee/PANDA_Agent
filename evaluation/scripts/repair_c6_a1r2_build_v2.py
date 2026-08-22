"""C6-A1R2 provenance repair stage 3: build replay v2 and run all verifications.

Assembles phase_c_c6_current_plan_candidate_replay_v2.jsonl (28 reused v1 rows
in original order with repaired g113/g114/g115 in place, then supplemental
g039/g040/g055 appended), then verifies: 28 rows unchanged, core cohort
unchanged, P0 integrity 30/30, unaffected-core parity 27/27, semantic cohort
derivation, and the no-Gold static scan.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from panda_agent.fusion_replay import current_policy, replay_case_from_mapping  # noqa: E402

V1 = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "replay"
    / "phase_c_c6_current_plan_candidate_replay_v1.jsonl"
)
V2 = (
    PROJECT_ROOT
    / "evaluation"
    / "baselines"
    / "replay"
    / "phase_c_c6_current_plan_candidate_replay_v2.jsonl"
)
FROZEN_REPAIR = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_repair_frozen_v1.json"
CAPTURED_ROWS = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_repair_captured_rows_v1.json"
A1R2_FROZEN = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_preregistration_frozen_v1.json"
OUT_RESULTS = PROJECT_ROOT / "data" / "tmp" / "c6_a1r2_repair_verification_v1.json"

REPAIRED_CORE = ["g113", "g114", "g115"]
SUPPLEMENTAL = ["g039", "g040", "g055"]


def to_replay_payload(row: dict, role: str) -> dict:
    payload = dict(row)
    payload["row_role"] = role
    return payload


def p0_metrics(row: dict) -> dict:
    case = replay_case_from_mapping(
        {
            "case_id": row["case_id"],
            "question": row["question"],
            "intent": row["intent"],
            "channels": {
                ch: {
                    "availability_state": s["availability_state"],
                    "candidates": [
                        {
                            "object_id": c["object_id"],
                            "rank": c["channel_rank"],
                            "original_score": c.get("original_channel_score"),
                            "source_id": c.get("source_id"),
                            "source_version_id": c.get("source_version_id"),
                            "locator": c.get("locator"),
                        }
                        for c in s.get("candidates", [])
                    ],
                }
                for ch, s in row["channels"].items()
            },
        }
    )
    receipt = current_policy().apply(case)
    receipt2 = current_policy().apply(case)
    deterministic = receipt.as_dict() == receipt2.as_dict()
    contrib_ok = all(
        abs(c.fused_score - sum(i.contribution for i in c.contributions)) < 1e-9
        for c in receipt.fused
    )
    no_semantic = all(
        "semantic_dense" not in i.channel for c in receipt.fused for i in c.contributions
    )
    dedup_ok = len({c.object_id for c in receipt.fused}) == len(receipt.fused)
    return {
        "fused": [(c.object_id, round(c.fused_score, 12)) for c in receipt.fused],
        "deterministic": deterministic,
        "contrib_ok": contrib_ok,
        "no_semantic": no_semantic,
        "dedup_ok": dedup_ok,
    }


def main() -> None:
    v1_rows = [json.loads(l) for l in V1.read_text(encoding="utf-8").splitlines() if l.strip()]
    frozen_repair = json.loads(FROZEN_REPAIR.read_text(encoding="utf-8"))
    captured = {row["case_id"]: row for row in json.loads(CAPTURED_ROWS.read_text(encoding="utf-8"))}
    a1r2 = json.loads(A1R2_FROZEN.read_text(encoding="utf-8"))
    core_ids = a1r2["core_capture_cohort"]

    # --- build v2 ---
    v2_rows: list[dict] = []
    reused = 0
    for row in v1_rows:
        if row["case_id"] in REPAIRED_CORE:
            v2_rows.append(to_replay_payload(captured[row["case_id"]], "repaired_core"))
        else:
            v2_rows.append(to_replay_payload(row, "reused_v1"))
            reused += 1
    for case_id in sorted(SUPPLEMENTAL):
        v2_rows.append(to_replay_payload(captured[case_id], "supplemental_coverage"))
    with V2.open("w", encoding="utf-8") as handle:
        for row in v2_rows:
            handle.write(json.dumps(row, default=str) + "\n")

    # --- verification 1: reused rows unchanged (ignoring row_role) ---
    v1_by_id = {row["case_id"]: row for row in v1_rows}
    unchanged = 0
    for row in v2_rows:
        if row["row_role"] != "reused_v1":
            continue
        original = v1_by_id[row["case_id"]]
        compare = {k: v for k, v in row.items() if k != "row_role"}
        if compare == original:
            unchanged += 1
    reused_unchanged = unchanged == reused

    # --- verification 2: core cohort unchanged ---
    core_now = [row["case_id"] for row in v2_rows if row["case_id"] in set(core_ids)]
    core_ids_identical = sorted(core_now) == sorted(core_ids)
    supplemental_not_core = not (set(r["case_id"] for r in v2_rows if r["row_role"] == "supplemental_coverage") & set(core_ids))

    # --- verification 3: P0 integrity over the 30 core cases from v2 ---
    v2_by_id = {row["case_id"]: row for row in v2_rows}
    integrity_ok = 0
    integrity_fail = []
    p0_v2 = {}
    for case_id in core_ids:
        m = p0_metrics(v2_by_id[case_id])
        p0_v2[case_id] = m["fused"]
        if m["deterministic"] and m["contrib_ok"] and m["no_semantic"] and m["dedup_ok"]:
            integrity_ok += 1
        else:
            integrity_fail.append(case_id)

    # --- verification 4: unaffected-core parity 27/27 vs v1 ---
    parity_ok = 0
    parity_fail = []
    p0_v1 = {}
    for case_id in core_ids:
        if case_id in REPAIRED_CORE:
            continue
        m1 = p0_metrics(v1_by_id[case_id])
        p0_v1[case_id] = m1["fused"]
        if m1["fused"] == p0_v2[case_id]:
            parity_ok += 1
        else:
            parity_fail.append(case_id)

    # --- verification 5: semantic cohort per the original C6-A1 rule
    # (all structural semantic-active cases up to 20; global live-cohort
    # membership and row_role are NOT semantic eligibility conditions) ---
    intent_by_case = {**a1r2["intent_by_case"]}
    for row in v2_rows:
        intent_by_case.setdefault(row["case_id"], row["intent"])
    semantic_cohort = sorted(
        row["case_id"]
        for row in v2_rows
        if row["channels"]["semantic_dense"].get("semantic_view_active") is True
        and row["channels"]["semantic_dense"]["availability_state"] in {"PRESENT_NONEMPTY", "PRESENT_EMPTY"}
        and row["channels"]["semantic_dense"].get("execution_status") == "OK"
        and all(
            row["channels"][ch]["availability_state"] in {"PRESENT_NONEMPTY", "PRESENT_EMPTY"}
            for ch in ("exact", "raw_dense", "sparse", "paper", "workflow", "graph")
        )
    )
    semantic_intents = sorted({intent_by_case[c] for c in semantic_cohort})
    semantic_eligible = len(semantic_cohort) >= 8 and len(semantic_intents) >= 2

    # --- verification 6: no-Gold scan ---
    banned = ["relevance", "expected_evidence", "required_evidence", "critical_evidence", "answer_requirement", "gold_label", "evidence_group"]
    text = V2.read_text(encoding="utf-8").casefold()
    banned_hits = [b for b in banned if b in text]

    results = {
        "v2_row_count": len(v2_rows),
        "reused_v1_rows": reused,
        "repaired_core_rows": 3,
        "supplemental_rows": 3,
        "reused_rows_unchanged": reused_unchanged,
        "core_count_original": len(core_ids),
        "core_count_v2": len(core_now),
        "core_ids_identical": core_ids_identical,
        "supplemental_not_in_core": supplemental_not_core,
        "p0_core_integrity": {"ok": integrity_ok, "fail": integrity_fail},
        "p0_unaffected_parity": {"ok": parity_ok, "fail": parity_fail},
        "semantic_cohort": semantic_cohort,
        "semantic_intents": semantic_intents,
        "semantic_a2_evidence_eligible": semantic_eligible,
        "banned_field_hits": banned_hits,
    }
    OUT_RESULTS.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
