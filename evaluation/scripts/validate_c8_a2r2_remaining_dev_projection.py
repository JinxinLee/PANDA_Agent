"""Validate the C8-A2R2 remaining-dev projection in the P0 context only.

This validator performs structural checks against the split-role audit and the
mechanically parsed Gold source.  It must not be run or imported by a future
C8-A2R2 scientific execution, which consumes the committed projection without
opening Gold.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


AUDIT_COMMIT = "dedaef5a8216201781628fbccf28e5823adab513"
AUDIT_ARTIFACT_ROLE = "C8_A2R2_SPLIT_ROLE_AUDIT"
EXPECTED_POPULATION_OUTCOME = "DEV_ONLY_EXTENSION_SUPPORTED"
AUTHORIZED_SPLITS = ["dev"]
PRIOR_SCREENED_COUNT = 24
PRIOR_SCREENED_DEV_COUNT = 16
TOTAL_DEV_COUNT = 80
REMAINING_DEV_COUNT = 64
ALLOWED_RECORD_KEYS = frozenset({"case_id", "query", "intent"})
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "artifact_role",
        "split_role_audit",
        "source",
        "existing_targeted_complete_count",
        "required_total_targeted_complete_count",
        "additional_targeted_complete_needed",
        "extension_case_ids",
        "extension_count",
        "records",
    }
)
FORBIDDEN_KEYS = frozenset(
    {
        "split",
        "language",
        "expected_status",
        "allowed_source_versions",
        "required_evidence_groups",
        "required_source_types",
        "required_answer_points",
        "required_identifiers",
        "forbidden_evidence",
        "concept_scopes",
        "review_status",
        "reviewer",
        "reviewed_at",
        "gold_correctness",
        "answer_rubrics",
        "relevance",
        "gold_relevance",
        "relevance_identity",
    }
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load_json(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(parsed, dict), f"JSON artifact must be an object: {path}")
    return parsed


def _safe_gold_records(source_path: Path) -> dict[str, dict[str, str]]:
    """Parse only the fields permitted for this preparation task."""

    parsed = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    questions = parsed.get("questions") if isinstance(parsed, dict) else None
    _require(isinstance(questions, list), "Gold source questions must be a list")

    source_by_id: dict[str, dict[str, str]] = {}
    for item in questions:
        _require(isinstance(item, dict), "Gold question records must be mappings")
        case_id = item.get("id")
        query = item.get("query")
        intent = item.get("intent")
        split = item.get("split")
        _require(isinstance(case_id, str) and case_id, "Gold record id must be non-empty")
        _require(case_id not in source_by_id, f"duplicate Gold question id: {case_id}")
        _require(isinstance(query, str), f"query must be a string for {case_id}")
        _require(isinstance(intent, str) and intent, f"intent must be non-empty for {case_id}")
        _require(isinstance(split, str) and split, f"split must be non-empty for {case_id}")
        # Deliberately retain only id/query/intent/split for source integrity.
        source_by_id[case_id] = {
            "id": case_id,
            "query": query,
            "intent": intent,
            "split": split,
        }
    return source_by_id


def _mapping_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = {str(key) for key in value}
        for nested in value.values():
            keys.update(_mapping_keys(nested))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for nested in value:
            keys.update(_mapping_keys(nested))
        return keys
    return set()


def validate_projection(
    audit_path: Path,
    source_path: Path,
    projection_path: Path,
) -> dict[str, Any]:
    audit = _load_json(audit_path)
    source_by_id = _safe_gold_records(source_path)
    projection = _load_json(projection_path)

    _require(audit.get("artifact_role") == AUDIT_ARTIFACT_ROLE, "unexpected audit role")
    _require(audit.get("a2r1_result_commit") == "5f2b4b78e8cc98b297fcc38f2cdba8491cecf04c", "unexpected A2R1 commit")
    _require(audit.get("future_extension_population_outcome") == EXPECTED_POPULATION_OUTCOME, "audit population outcome is not authorized")
    _require(audit.get("allowed_extension_splits") == AUTHORIZED_SPLITS, "audit authorized split differs")

    dev_inventory = audit.get("dev_inventory")
    _require(isinstance(dev_inventory, dict), "audit dev inventory must be an object")
    audit_remaining_ids = dev_inventory.get("remaining_case_ids")
    _require(isinstance(audit_remaining_ids, list), "audit remaining IDs must be a list")
    _require(dev_inventory.get("total") == TOTAL_DEV_COUNT, "audit total dev count differs")
    _require(dev_inventory.get("already_screened_count") == PRIOR_SCREENED_DEV_COUNT, "audit prior dev count differs")
    _require(dev_inventory.get("remaining") == REMAINING_DEV_COUNT, "audit remaining dev count differs")
    _require(len(audit_remaining_ids) == REMAINING_DEV_COUNT, "audit remaining ID count differs")
    _require(len(set(audit_remaining_ids)) == REMAINING_DEV_COUNT, "audit remaining IDs must be unique")

    prior_cases = audit.get("prior_screened_cases")
    _require(isinstance(prior_cases, list), "audit prior screened cases must be a list")
    prior_ids = [case.get("case_id") for case in prior_cases if isinstance(case, dict)]
    _require(len(prior_cases) == PRIOR_SCREENED_COUNT, "audit prior screened count differs")
    _require(len(prior_ids) == PRIOR_SCREENED_COUNT, "audit prior screened records are malformed")
    _require(len(set(prior_ids)) == PRIOR_SCREENED_COUNT, "audit prior screened IDs must be unique")

    _require(set(projection) == TOP_LEVEL_KEYS, "projection top-level keys violate the allowlist")
    _require(projection.get("schema_version") == "1.0", "unexpected projection schema version")
    _require(
        projection.get("artifact_role") == "C8_A2R2_SANITIZED_EXECUTION_PROJECTION_EXTENSION",
        "unexpected projection artifact role",
    )
    _require(
        projection.get("split_role_audit")
        == {
            "path": "evaluation/baselines/manifests/phase_c_c8_a2r2_split_role_audit_v1.json",
            "commit": AUDIT_COMMIT,
            "population_outcome": EXPECTED_POPULATION_OUTCOME,
        },
        "projection split-role provenance differs",
    )
    _require(
        projection.get("source")
        == {"path": "evaluation/gold_questions.yaml", "authorized_split": "dev"},
        "projection source metadata differs",
    )
    _require(projection.get("existing_targeted_complete_count") == 4, "existing targeted count differs")
    _require(projection.get("required_total_targeted_complete_count") == 6, "required targeted count differs")
    _require(projection.get("additional_targeted_complete_needed") == 2, "additional targeted count differs")

    extension_ids = projection.get("extension_case_ids")
    _require(extension_ids == audit_remaining_ids, "projection IDs/order differ from the audit")
    _require(projection.get("extension_count") == REMAINING_DEV_COUNT, "projection extension count differs")

    records = projection.get("records")
    _require(isinstance(records, list), "projection records must be a list")
    _require(len(records) == REMAINING_DEV_COUNT, "projection record count differs")
    _require(
        [record.get("case_id") if isinstance(record, dict) else None for record in records]
        == audit_remaining_ids,
        "projection record order differs from the audit",
    )
    _require(len({record.get("case_id") for record in records if isinstance(record, dict)}) == REMAINING_DEV_COUNT, "projection IDs must be unique")

    for record in records:
        _require(isinstance(record, dict), "each projection record must be an object")
        _require(set(record) == ALLOWED_RECORD_KEYS, "execution record keys violate the exact allowlist")
        case_id = record["case_id"]
        _require(case_id in source_by_id, f"source record missing for {case_id}")
        source = source_by_id[case_id]
        _require(source["split"] == "dev", f"extension source is not dev: {case_id}")
        _require(isinstance(record["query"], str), f"query must be a string for {case_id}")
        _require(isinstance(record["intent"], str) and record["intent"], f"intent must be non-empty for {case_id}")
        _require(record["query"] == source["query"], f"query mismatch for {case_id}")
        _require(record["intent"] == source["intent"], f"intent mismatch for {case_id}")

    forbidden_projection_keys = _mapping_keys(projection) & FORBIDDEN_KEYS
    _require(not forbidden_projection_keys, "projection contains forbidden Gold fields")

    all_dev_ids = {case_id for case_id, item in source_by_id.items() if item["split"] == "dev"}
    prior_dev_ids = dev_inventory.get("already_screened")
    _require(isinstance(prior_dev_ids, list), "audit prior dev IDs must be a list")
    _require(len(prior_dev_ids) == PRIOR_SCREENED_DEV_COUNT, "audit prior dev ID count differs")
    _require(set(prior_dev_ids) <= all_dev_ids, "audit prior dev IDs are not all dev")
    _require(len(all_dev_ids) == TOTAL_DEV_COUNT, "source total dev count differs")
    _require(set(prior_dev_ids).isdisjoint(set(audit_remaining_ids)), "dev partition overlaps")
    _require(set(prior_dev_ids) | set(audit_remaining_ids) == all_dev_ids, "dev partition is incomplete")
    _require(set(extension_ids).isdisjoint(set(prior_ids)), "extension overlaps prior screened IDs")

    return {
        "audit_commit": AUDIT_COMMIT,
        "artifact_role": projection["artifact_role"],
        "record_count": len(records),
        "extension_count": projection["extension_count"],
        "source_dev_count": len(records),
        "query_exact_match_count": len(records),
        "intent_exact_match_count": len(records),
        "extension_order_exact": True,
        "prior_screened_intersection_count": 0,
        "dev_partition": {
            "total": TOTAL_DEV_COUNT,
            "already_screened": PRIOR_SCREENED_DEV_COUNT,
            "remaining": REMAINING_DEV_COUNT,
            "union_complete": True,
            "intersection_empty": True,
        },
        "forbidden_projection_keys": [],
        "gold_relevance_fields_copied": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audit",
        type=Path,
        default=Path("evaluation/baselines/manifests/phase_c_c8_a2r2_split_role_audit_v1.json"),
    )
    parser.add_argument("--source", type=Path, default=Path("evaluation/gold_questions.yaml"))
    parser.add_argument(
        "--projection",
        type=Path,
        default=Path("evaluation/baselines/manifests/phase_c_c8_a2r2_execution_projection_extension_v1.json"),
    )
    args = parser.parse_args()
    print(json.dumps(validate_projection(args.audit, args.source, args.projection), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
