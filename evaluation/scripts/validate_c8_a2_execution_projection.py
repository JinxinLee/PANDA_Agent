"""Validate the C8-A2 sanitized execution projection against parsed Gold input."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


PRIMARY_CASE_IDS = (
    "g001", "g007", "g012", "g013", "g025", "g026", "g027", "g038",
    "g041", "g042", "g043", "g044", "g057", "g058", "g059", "g060",
)
EXPANSION_CASE_IDS = (
    "g002", "g003", "g014", "g015", "g028", "g029", "g045", "g047",
)
FROZEN_CASE_IDS = (*PRIMARY_CASE_IDS, *EXPANSION_CASE_IDS)
ALLOWED_RECORD_KEYS = frozenset({"case_id", "query", "intent"})
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
        "critical",
        "expected_evidence",
        "answer_rubrics",
    }
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


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


def validate_projection(source_path: Path, projection_path: Path) -> dict[str, Any]:
    source = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    projection = json.loads(projection_path.read_text(encoding="utf-8"))

    source_questions = source.get("questions") if isinstance(source, dict) else None
    _require(isinstance(source_questions, list), "source questions must be a list")
    source_by_id = {str(item["id"]): item for item in source_questions}
    _require(
        all(case_id in source_by_id for case_id in FROZEN_CASE_IDS),
        "source is missing one or more frozen case IDs",
    )

    _require(projection.get("schema_version") == "1.0", "unexpected schema version")
    _require(
        projection.get("artifact_role") == "C8_A2_SANITIZED_EXECUTION_PROJECTION",
        "unexpected artifact role",
    )
    _require(
        projection.get("source") == {"path": "evaluation/gold_questions.yaml"},
        "source metadata must contain only the approved path",
    )
    _require(
        projection.get("primary_case_ids") == list(PRIMARY_CASE_IDS),
        "primary case order differs from the frozen cohort",
    )
    _require(
        projection.get("expansion_case_ids") == list(EXPANSION_CASE_IDS),
        "expansion case order differs from the frozen cohort",
    )

    records = projection.get("records")
    _require(isinstance(records, list), "projection records must be a list")
    _require(len(records) == 24, "projection must contain exactly 24 records")
    _require(
        [record.get("case_id") for record in records] == list(FROZEN_CASE_IDS),
        "record order differs from the frozen primary-plus-expansion sequence",
    )
    _require(len({record.get("case_id") for record in records}) == 24, "case IDs must be unique")

    for record in records:
        _require(isinstance(record, dict), "each projection record must be an object")
        _require(set(record) == ALLOWED_RECORD_KEYS, "record keys violate the exact allowlist")
        _require(not (set(record) & FORBIDDEN_KEYS), "record contains a forbidden Gold key")
        case_id = record["case_id"]
        _require(isinstance(record["query"], str) and record["query"].strip(), "query must be non-empty")
        _require(isinstance(record["intent"], str) and record["intent"].strip(), "intent must be non-empty")
        _require(record["query"] == source_by_id[case_id]["query"], f"query mismatch for {case_id}")
        _require(record["intent"] == source_by_id[case_id]["intent"], f"intent mismatch for {case_id}")

    _require(
        not (_mapping_keys(projection) & FORBIDDEN_KEYS),
        "projection contains forbidden Gold structure outside execution records",
    )
    return {
        "record_count": len(records),
        "primary_count": len(PRIMARY_CASE_IDS),
        "expansion_count": len(EXPANSION_CASE_IDS),
        "allowed_record_keys": sorted(ALLOWED_RECORD_KEYS),
        "query_exact_match_count": len(records),
        "intent_exact_match_count": len(records),
        "case_order_exact_match": True,
        "relevance_bearing_fields_in_projection": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("evaluation/gold_questions.yaml"),
    )
    parser.add_argument(
        "--projection",
        type=Path,
        default=Path(
            "evaluation/baselines/manifests/phase_c_c8_a2_execution_projection_v1.json"
        ),
    )
    args = parser.parse_args()
    print(json.dumps(validate_projection(args.source, args.projection), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
