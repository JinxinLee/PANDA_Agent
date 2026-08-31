"""D3-A2 analysis digest (evaluation-only, post-execution aggregation).

Reads the immutable runner records and emits a compact digest for mechanism
analysis: per-case three-arm metric matrix, paired deltas, D3 counters, and
match provenance.  It never recomputes or redefines frozen metrics.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

METRIC_FIELDS = (
    "gold_recall_at_5",
    "gold_recall_at_10",
    "gold_recall_at_20",
    "mrr",
    "combined_candidate_recall",
    "final_evidence_recall",
    "critical_final_evidence_recall",
    "refusal_evidence_recall",
)


def load_records(run_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in (run_dir / "records.jsonl").read_text(encoding="utf-8").splitlines():
        if line:
            records.append(json.loads(line))
    return records


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    records = load_records(args.run_dir)

    by_case: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        by_case[record["case_id"]][record["arm"]] = record

    errors = [
        (record["case_id"], record["arm"], record["error"])
        for record in records
        if record.get("error")
    ]
    print(f"records={len(records)} cases={len(by_case)} errors={len(errors)}")
    for case_id, arm, error in errors:
        print(f"  ERROR {arm} {case_id}: {error}")

    # Aggregate per-arm metric means over applicable (answered) cases.
    applicability: dict[str, list[bool]] = {}
    for case_id, arms in sorted(by_case.items()):
        legacy = arms.get("LEGACY") or {}
        metrics = ((legacy.get("metrics") or {}).get("metric_applicability") or {})
        applicability[case_id] = [metrics.get(f) for f in METRIC_FIELDS]

    print("\n=== per-arm aggregates (applicable answered cases only) ===")
    for field_index, field in enumerate(METRIC_FIELDS):
        row = []
        for arm in ("LEGACY", "ABLATION", "STRUCTURED"):
            values, n = [], 0
            for case_id, arms in by_case.items():
                record = arms.get(arm)
                if not record:
                    continue
                metric = (record.get("metrics") or {}).get(field)
                if metric is None:
                    continue
                values.append(metric)
                n += 1
            mean = sum(values) / len(values) if values else None
            row.append(f"{arm}={fmt(mean)} (n={n})")
        print(f"{field:32} " + "  ".join(row))

    print("\n=== per-case three-arm final-evidence-recall / recall@10 matrix ===")
    for case_id, arms in sorted(by_case.items()):
        cells = []
        for arm in ("LEGACY", "ABLATION", "STRUCTURED"):
            record = arms.get(arm)
            if not record:
                cells.append(f"{arm[:4]}=MISSING")
                continue
            metrics = record.get("metrics") or {}
            cells.append(
                f"{arm[:4]}:fer={fmt(metrics.get('final_evidence_recall'))}"
                f"/r10={fmt(metrics.get('gold_recall_at_10'))}"
                f"/crit={fmt(metrics.get('critical_final_evidence_recall'))}"
                f"/ref={fmt(metrics.get('refusal_evidence_recall'))}"
            )
        print(f"{case_id} {' | '.join(cells)}")

    print("\n=== paired deltas per case (LEGACY-ABLATION / STRUCTURED-ABLATION / STRUCTURED-LEGACY), final_evidence_recall ===")
    for case_id, arms in sorted(by_case.items()):
        def fer(arm: str) -> Any:
            record = arms.get(arm)
            return None if not record else (record.get("metrics") or {}).get("final_evidence_recall")
        la = fer("LEGACY")
        ab = fer("ABLATION")
        st = fer("STRUCTURED")
        if None in (la, ab, st):
            print(f"{case_id} incomplete (L={la}, A={ab}, S={st})")
            continue
        print(
            f"{case_id} L-A={la - ab:+.3f} S-A={st - ab:+.3f} S-L={st - la:+.3f}"
        )

    print("\n=== D3 counters per case (STRUCTURED arm) ===")
    for case_id, arms in sorted(by_case.items()):
        record = arms.get("STRUCTURED")
        if not record:
            continue
        receipt = record.get("d3_experiment") or {}
        counters = receipt.get("diagnostic_counters") or {}
        statuses = counters.get("structured_resolution_status_counts") or {}
        legacy_receipt = (arms.get("LEGACY") or {}).get("d3_experiment") or {}
        legacy_counters = legacy_receipt.get("diagnostic_counters") or {}
        print(
            f"{case_id} legacy_hits={legacy_counters.get('legacy_shortcut_hit_count')}"
            f" selected_hits={legacy_counters.get('selected_legacy_shortcut_hit_count')}"
            f" struct_hits={counters.get('structured_resolution_hit_count')}"
            f" seeds={counters.get('structured_seed_count')}"
            f" rel_trav={counters.get('structured_relation_traversal_count')}"
            f" wf_trav={counters.get('structured_workflow_traversal_count')}"
            f" inj={counters.get('structured_candidate_injection_count')}"
            f" statuses={statuses}"
        )

    print("\n=== safety zero counters (STRUCTURED arm) ===")
    violations = 0
    for case_id, arms in sorted(by_case.items()):
        record = arms.get("STRUCTURED")
        if not record:
            continue
        counters = ((record.get("d3_experiment") or {}).get("diagnostic_counters") or {})
        nonzero = {
            key: value
            for key, value in counters.items()
            if key in {
                "migration_specific_direct_answer_location_injection_count",
                "prohibited_fallback_use_count",
                "evaluation_metadata_runtime_use_count",
                "selected_legacy_payload_reuse_count",
                "same_as_activation_count",
            }
            and value != 0
        }
        if nonzero:
            violations += 1
            print(f"  {case_id} VIOLATION: {nonzero}")
    print(f"safety_zero_violations={violations}")

    print("\n=== STRUCTURED resolution receipts (seeds + candidates) ===")
    for case_id, arms in sorted(by_case.items()):
        record = arms.get("STRUCTURED")
        if not record:
            continue
        receipt = record.get("d3_experiment") or {}
        prov = receipt.get("structured_candidate_provenance") or []
        seeds = sorted({p.get("seed_object_id") for p in prov if p.get("seed_object_id")})
        cands = [p.get("candidate_object_id") for p in prov]
        resolved = receipt.get("resolution_receipt") or {}
        print(f"{case_id} seeds={seeds}")
        print(f"    candidates({len(cands)})={cands}")
        excluded = receipt.get("excluded_resolution_reasons") or []
        if excluded:
            print(f"    excluded={excluded}")
        resolutions = resolved.get("resolutions") or []
        for res in resolutions:
            print(
                f"    res: status={res.get('status')} tier_evidence="
                f"{[(e.get('kind'), e.get('tier')) for e in (res.get('evidence') or [])][:3]}"
                f" mention={str(res.get('mention_text'))[:50]!r}"
            )

    print("\n=== matched groups provenance (per arm, per case) ===")
    for case_id, arms in sorted(by_case.items()):
        print(f"--- {case_id}")
        for arm in ("LEGACY", "ABLATION", "STRUCTURED"):
            record = arms.get(arm)
            if not record:
                continue
            metrics = record.get("metrics") or {}
            final_prov = ((metrics.get("evidence_match_provenance") or {}).get("final_evidence_recall")) or []
            top20_prov = ((metrics.get("evidence_match_provenance") or {}).get("gold_recall_at_20")) or []
            def brief(prov: list[dict[str, Any]]) -> str:
                parts = []
                for item in prov:
                    if item.get("matched") is False or (not item.get("object_id") and not item.get("provenance")):
                        parts.append(f"{item.get('group_id')}:MISS")
                    else:
                        parts.append(f"{item.get('group_id')}:{item.get('object_id')}({item.get('provenance')})")
                return " ".join(parts)
            print(f"  {arm:9} final: {brief(final_prov)}")
            print(f"  {arm:9} top20: {brief(top20_prov)}")

    print("\n=== call accounting totals ===")
    totals: Counter[str] = Counter()
    for record in records:
        for key, value in (record.get("call_accounting") or {}).items():
            totals[key] += value
    print(dict(totals))
    durations = [record["execution"]["duration_seconds"] for record in records]
    print(f"total_duration_s={sum(durations):.1f}")


if __name__ == "__main__":
    main()
