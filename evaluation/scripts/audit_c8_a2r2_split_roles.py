"""Audit C8-A2R2 screening split roles using safe Gold metadata only.

This preparation-only helper parses the source YAML structurally, retaining
only ``id``, ``split``, and ``intent`` from each question.  It must not be used
by a future A2R2 scientific execution, which consumes a committed projection.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


A2R1_RESULT_COMMIT = "5f2b4b78e8cc98b297fcc38f2cdba8491cecf04c"
PRIOR_SCREENED_CASE_IDS = (
    "g001", "g007", "g012", "g013", "g025", "g026", "g027", "g038",
    "g041", "g042", "g043", "g044", "g057", "g058", "g059", "g060",
    "g002", "g003", "g014", "g015", "g028", "g029", "g045", "g047",
)
TARGETED_CASE_IDS = ("g007", "g025", "g041", "g057")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _safe_source_records(source_path: Path) -> dict[str, dict[str, str]]:
    parsed = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    questions = parsed.get("questions") if isinstance(parsed, dict) else None
    _require(isinstance(questions, list), "Gold source questions must be a list")
    safe: dict[str, dict[str, str]] = {}
    for item in questions:
        _require(isinstance(item, dict), "Gold question records must be mappings")
        case_id = str(item.get("id") or "")
        _require(case_id, "Gold question record has no id")
        _require(case_id not in safe, f"duplicate Gold question id: {case_id}")
        split = item.get("split")
        intent = item.get("intent")
        _require(isinstance(split, str) and split, f"missing split for {case_id}")
        _require(isinstance(intent, str) and intent, f"missing intent for {case_id}")
        # Deliberately retain only the three audit-safe metadata fields.
        safe[case_id] = {"id": case_id, "split": split, "intent": intent}
    return safe


def build_audit(source_path: Path) -> dict[str, Any]:
    source = _safe_source_records(source_path)
    _require(
        all(case_id in source for case_id in PRIOR_SCREENED_CASE_IDS),
        "one or more prior screened IDs are missing from Gold",
    )
    prior = [
        {
            "screening_position": position,
            "case_id": case_id,
            "split": source[case_id]["split"],
            "intent": source[case_id]["intent"],
        }
        for position, case_id in enumerate(PRIOR_SCREENED_CASE_IDS, 1)
    ]
    targeted = [
        {
            "case_id": case_id,
            "split": source[case_id]["split"],
            "intent": source[case_id]["intent"],
        }
        for case_id in TARGETED_CASE_IDS
    ]
    all_ids = set(source)
    dev_ids = sorted(case_id for case_id, item in source.items() if item["split"] == "dev")
    screened_set = set(PRIOR_SCREENED_CASE_IDS)
    prior_dev_ids = sorted(screened_set & set(dev_ids))
    remaining_dev_ids = [case_id for case_id in dev_ids if case_id not in screened_set]
    prior_counts = Counter(item["split"] for item in prior)
    targeted_counts = Counter(item["split"] for item in targeted)
    split_counts = Counter(item["split"] for item in source.values())
    non_dev = {
        split: [item for item in prior if item["split"] == split]
        for split in sorted({item["split"] for item in prior if item["split"] != "dev"})
    }

    return {
        "schema_version": "1.0",
        "artifact_role": "C8_A2R2_SPLIT_ROLE_AUDIT",
        "task": "C8-A2R2-S0",
        "a2r1_result_commit": A2R1_RESULT_COMMIT,
        "provenance": {
            "original_a2_preregistration_source_anchor": "5d19a5d18b7f13c163b1d6c03284158a78b88f70",
            "a2_failed_recovery_execution_commit": "07594b9b6f2857796115bc9cfe00d3426676084b",
            "a2r1_result_commit": A2R1_RESULT_COMMIT,
            "note": "Older artifact naming may be ambiguous; this audit uses explicit field names.",
        },
        "split_inventory": [
            {"split": split, "count": split_counts[split]}
            for split in sorted(split_counts)
        ],
        "prior_screened_case_count": len(prior),
        "prior_screened_cases": prior,
        "prior_screened_counts_by_split": dict(sorted(prior_counts.items())),
        "targeted_case_count": len(targeted),
        "targeted_cases": targeted,
        "targeted_counts_by_split": dict(sorted(targeted_counts.items())),
        "exposure_model": {
            "QUERY_EXPOSED": {"count": 24, "all_prior_screened": True},
            "TARGETED_RUNTIME_EXPOSED": {"count": 4, "case_ids": list(TARGETED_CASE_IDS)},
            "GOLD_RELEVANCE_EXPOSED": {"count": 0, "all_prior_screened": False},
        },
        "gold_relevance_exposure": False,
        "dev_inventory": {
            "total": len(dev_ids),
            "already_screened": prior_dev_ids,
            "already_screened_count": len(prior_dev_ids),
            "remaining": len(remaining_dev_ids),
            "remaining_case_ids": remaining_dev_ids,
        },
        "non_dev_prior_screened_by_split": non_dev,
        "split_role_policy": [
            {
                "split": "dev",
                "role": "development-visible benchmark population",
                "development_visibility": "allowed",
                "reuse_eligibility": "eligible for deterministic repeated development diagnostics, subject to fixed IDs and no question-specific tuning",
                "protection_status": "not a protected holdout",
                "authoritative_source_path": "docs/EVALUATION_POLICY.md",
                "source_section": "§4 Evaluation pyramid / §4 A3 bootstrap default",
                "uncertainty": "none for development visibility; current Gold source identity must still be recorded per run",
            },
            {
                "split": "acceptance",
                "role": "historically exposed acceptance/final-candidate validation population",
                "development_visibility": "not authorized for new applicability-extension selection",
                "reuse_eligibility": "not eligible as a fresh development or final holdout population after query/runtime exposure",
                "protection_status": "already exposed; not a pristine protected holdout",
                "authoritative_source_path": "docs/M6_EVALUATION_RETROSPECTIVE.md",
                "source_section": "§4 acceptance isolation; acceptance is for frozen-candidate final acceptance and must not drive tuning",
                "uncertainty": "current source file still names 40 records acceptance, while current v2 policy/state describes the former acceptance split as retired and current v2 as dev/challenge/regression",
            },
        ],
        "policy_conflicts": [
            {
                "source_path": "evaluation/gold_questions.yaml",
                "finding": "safe metadata inventory contains split names acceptance and dev",
            },
            {
                "source_path": "docs/M6_EVALUATION_RETROSPECTIVE.md",
                "finding": "current policy history describes the old acceptance split as retired and separates development from final acceptance",
            },
            {
                "source_path": "docs/EVALUATION_STATUS.md",
                "finding": "current status identifies Gold v2.6 and C8 A2/A2R1 state, but does not reconcile the root source split naming",
            },
        ],
        "independence_impact_by_split": {
            "dev": {
                "query_exposure": "QUERY_EXPOSED",
                "targeted_runtime_exposure": "one targeted case is runtime-exposed",
                "gold_relevance_exposure": "none",
                "classification": "QUERY_EXPOSED_BUT_LABELS_UNSEEN",
                "later_use": "permitted for exposed-development applicability diagnostics; not strictly unseen query evidence",
            },
            "acceptance": {
                "query_exposure": "QUERY_EXPOSED",
                "targeted_runtime_exposure": "three targeted cases are runtime-exposed",
                "gold_relevance_exposure": "none",
                "classification": "SHOULD_NOT_BE_USED_AS_FINAL_HOLDOUT",
                "later_use": "do not extend A2R2 from acceptance; preserve as historical exposure only",
            },
        },
        "future_extension_population_outcome": "DEV_ONLY_EXTENSION_SUPPORTED",
        "allowed_extension_splits": ["dev"],
        "TARGETED_CHARACTERISTICS_USED_FOR_POPULATION_SELECTION": False,
        "scientific_rules_changed": False,
        "live_work": {
            "ANALYZER_CALLS": 0,
            "RETRIEVAL_CALLS": 0,
            "TARGETED_RETRIEVAL_CALLS": 0,
            "EMBEDDING_CALLS": 0,
            "SPARSE_ENCODING_CALLS": 0,
            "QDRANT_READS": 0,
            "SQL_CANDIDATE_READS": 0,
            "RERANKER_CALLS": 0,
            "G1_EXECUTIONS": 0,
            "QA_CALLS": 0,
            "VERIFIER_CALLS": 0,
            "JUDGE_CALLS": 0,
            "DB_INDEX_WRITES": 0,
        },
        "audit_checks": {
            "prior_ids_unique": len(PRIOR_SCREENED_CASE_IDS) == len(screened_set),
            "targeted_subset_of_prior": set(TARGETED_CASE_IDS) <= screened_set,
            "split_counts_sum_to_source_count": sum(split_counts.values()) == len(all_ids),
            "prior_counts_sum_to_24": sum(prior_counts.values()) == 24,
            "targeted_counts_sum_to_4": sum(targeted_counts.values()) == 4,
            "dev_partition_complete": set(prior_dev_ids) | set(remaining_dev_ids) == set(dev_ids),
            "dev_partition_intersection_empty": not (set(prior_dev_ids) & set(remaining_dev_ids)),
            "relevance_bearing_gold_serialized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("evaluation/gold_questions.yaml"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evaluation/baselines/manifests/phase_c_c8_a2r2_split_role_audit_v1.json"),
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    audit = build_audit(args.source)
    if args.write:
        args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "split_inventory": audit["split_inventory"],
                "prior_screened_counts_by_split": audit["prior_screened_counts_by_split"],
                "targeted_counts_by_split": audit["targeted_counts_by_split"],
                "dev_total": audit["dev_inventory"]["total"],
                "dev_already_screened": audit["dev_inventory"]["already_screened_count"],
                "dev_remaining": audit["dev_inventory"]["remaining"],
                "future_extension_population_outcome": audit["future_extension_population_outcome"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
