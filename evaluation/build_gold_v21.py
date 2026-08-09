"""Build the signed Gold v2.1 rubric from an explicit review patch.

This script is intentionally deterministic.  It only applies selectors and
source/rubric changes listed in ``benchmarks/v2_1/gold_v2_1_patch.yaml``; it
never derives selectors from embeddings, model output, or fuzzy text matches.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from panda_agent.evaluation import GoldDataset
from panda_agent.evaluation import _selector_match_provenance  # type: ignore[attr-defined]
from panda_agent.evaluation_runner import load_object_lookup


ROOT = Path(__file__).resolve().parents[1]
V21 = ROOT / "evaluation" / "benchmarks" / "v2_1"
DATASET = V21 / "gold_questions.yaml"
PATCH = V21 / "gold_v2_1_patch.yaml"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selector_key(selector: dict[str, Any]) -> str:
    return json.dumps(selector, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def apply_patch(dataset: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    by_id = {item["id"]: item for item in dataset["questions"]}
    for operation in patch["operations"]:
        question = by_id[operation["case_id"]]
        if "accepted_intents" in operation:
            question["accepted_intents"] = list(operation["accepted_intents"])
        if "required_source_types" in operation:
            question["required_source_types"] = list(operation["required_source_types"])
        remove_groups = set(operation.get("remove_groups", []))
        if remove_groups:
            question["required_evidence_groups"] = [
                group
                for group in question["required_evidence_groups"]
                if group["group_id"] not in remove_groups
            ]
        for group_id, selectors in (operation.get("add_selectors") or {}).items():
            group = next(
                group
                for group in question["required_evidence_groups"]
                if group["group_id"] == group_id
            )
            existing = {_selector_key(item) for item in group["any_of"]}
            for selector in selectors:
                if _selector_key(selector) not in existing:
                    group["any_of"].append(selector)
                    existing.add(_selector_key(selector))
    dataset["benchmark_version"] = patch["benchmark_version"]
    return dataset


def audit(dataset: GoldDataset, object_lookup: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    for question in dataset.questions:
        for group in question.required_evidence_groups:
            for index, selector in enumerate(group.any_of):
                matches = []
                for object_id, item in object_lookup.items():
                    if selector.matches(item):
                        matches.append({"object_id": object_id, "provenance": "direct"})
                # Direct canonical objects are the audit authority.  Relation
                # tiers are evaluated during scoring; only selectors that have
                # no canonical direct object need the slower structural check.
                if not matches:
                    for object_id, item in object_lookup.items():
                        provenance = _selector_match_provenance(selector, item, object_lookup)
                        if provenance:
                            matches.append({"object_id": object_id, "provenance": provenance})
                row = {
                    "case_id": question.id,
                    "group_id": group.group_id,
                    "selector_index": index,
                    "selector": selector.model_dump(mode="json", exclude_none=True),
                    "match_count": len(matches),
                    "sample_matches": matches[:5],
                }
                rows.append(row)
                if not matches:
                    unmatched.append(row)
    widths = [row["match_count"] for row in rows]
    return {
        "benchmark_version": dataset.benchmark_version,
        "question_count": len(dataset.questions),
        "selector_count": len(rows),
        "unmatched_selectors": unmatched,
        "selector_match_width": {
            "min": min(widths, default=0),
            "max": max(widths, default=0),
            "mean": sum(widths) / len(widths) if widths else 0.0,
        },
        "selectors": rows,
    }


def main() -> None:
    base = yaml.safe_load(DATASET.read_text(encoding="utf-8")) or {}
    base_hash = sha256(DATASET)
    patch = yaml.safe_load(PATCH.read_text(encoding="utf-8")) or {}
    result = apply_patch(base, patch)
    # Pydantic validates the exact output before it is written.
    dataset = GoldDataset.model_validate(result)
    dataset.require_approved()
    DATASET.write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    objects = load_object_lookup(ROOT)
    selector_audit = audit(dataset, objects)
    (V21 / "selector_match_count_audit.json").write_text(
        json.dumps(selector_audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if selector_audit["unmatched_selectors"]:
        raise SystemExit(
            f"Gold v2.1 has unmatched selectors: {len(selector_audit['unmatched_selectors'])}"
        )
    patch_hash = sha256(PATCH)
    source_review_hash = patch["source_review_sha256"]
    report = {
        "benchmark_version": dataset.benchmark_version,
        "base_dataset_sha256": base_hash,
        "dataset_sha256": sha256(DATASET),
        "patch_sha256": patch_hash,
        "source_review_sha256": source_review_hash,
        "question_count": len(dataset.questions),
        "approved_count": sum(item.review_status == "approved" for item in dataset.questions),
        "split_counts": {split: sum(item.split == split for item in dataset.questions) for split in sorted({item.split for item in dataset.questions})},
        "status_counts": {status: sum(item.expected_status.value == status for item in dataset.questions) for status in sorted({item.expected_status.value for item in dataset.questions})},
        "accepted_intent_cases": [item.id for item in dataset.questions if item.accepted_intents],
        "operations": patch["operations"],
        "selector_audit_sha256": sha256(V21 / "selector_match_count_audit.json"),
    }
    (V21 / "gold_v2_1_change_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    manifest_path = V21 / "benchmark_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "benchmark_version": dataset.benchmark_version,
            "dataset_sha256": report["dataset_sha256"],
            "gold_v2_1_patch_sha256": patch_hash,
            "source_review_sha256": source_review_hash,
            "selector_match_audit_sha256": report["selector_audit_sha256"],
            "status": "approved_exposed_development_benchmark_v2_1",
        }
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
