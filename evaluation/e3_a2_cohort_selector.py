"""Mechanical cohort selector for E3-A2 targeted missing-point recovery validation.

The selector is dataset-driven only. No PANDA Agent outcome may be inspected
before the cohort is frozen; the selector must not be tuned after outputs are
observed (evaluation/E3_A2_TARGETED_MISSING_POINT_RECOVERY_PROTOCOL.md).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "evaluation" / "novel" / "v1" / "novel_dev.yaml"
CURATION_PATH = ROOT / "evaluation" / "novel" / "v1" / "curation_metadata.yaml"

DATASET_BENCHMARK_VERSION = "novel-v1-dev-0.3.0"
EXPECTED_DATASET_COUNT = 28

SELECTOR_DEFINITION: dict[str, Any] = {
    "review_status": "approved",
    "language": "en",
    "expected_status": "answered",
    "curation_representativeness_class": "representative",
    "min_critical_required_answer_points": 2,
    "min_critical_required_evidence_groups": 2,
    "at_least_one_of": [
        "coverage.evidence_topology != single_hop",
        "coverage.source_scope == cross_source",
        "coverage.repository_scope == cross_repository",
    ],
    "ordering": "dataset question order (numeric question id)",
}


def load_novel_dev() -> tuple[dict[str, Any], dict[str, Any]]:
    dataset = yaml.safe_load(DATASET_PATH.read_text(encoding="utf-8"))
    curation = yaml.safe_load(CURATION_PATH.read_text(encoding="utf-8"))
    return dataset, curation


def critical_answer_points(question: dict[str, Any]) -> list[dict[str, Any]]:
    return [p for p in question.get("required_answer_points", []) if p.get("critical")]


def critical_evidence_groups(question: dict[str, Any]) -> list[dict[str, Any]]:
    return [g for g in question.get("required_evidence_groups", []) if g.get("critical")]


def is_selected(question: dict[str, Any], curation_record: dict[str, Any]) -> bool:
    if question.get("review_status") != "approved":
        return False
    if question.get("language") != "en":
        return False
    if question.get("expected_status") != "answered":
        return False
    representativeness = curation_record.get("representativeness", {})
    if representativeness.get("class") != "representative":
        return False
    if len(critical_answer_points(question)) < 2:
        return False
    if len(critical_evidence_groups(question)) < 2:
        return False
    coverage = curation_record.get("coverage", {})
    return (
        coverage.get("evidence_topology") != "single_hop"
        or coverage.get("source_scope") == "cross_source"
        or coverage.get("repository_scope") == "cross_repository"
    )


def cohort_entry(question: dict[str, Any], curation_record: dict[str, Any]) -> dict[str, Any]:
    coverage = curation_record.get("coverage", {})
    representativeness = curation_record.get("representativeness", {})
    return {
        "question_id": question["id"],
        "curation_family_id": curation_record.get("curation_family_id"),
        "intent": question.get("intent"),
        "representativeness_class": representativeness.get("class"),
        "difficulty": coverage.get("difficulty"),
        "evidence_topology": coverage.get("evidence_topology"),
        "source_scope": coverage.get("source_scope"),
        "repository_scope": coverage.get("repository_scope"),
        "critical_answer_points": len(critical_answer_points(question)),
        "critical_evidence_groups": len(critical_evidence_groups(question)),
    }


def select_cohort(
    dataset: dict[str, Any] | None = None,
    curation: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if dataset is None or curation is None:
        dataset, curation = load_novel_dev()
    records = {r["question_id"]: r for r in curation.get("records", [])}
    entries: list[dict[str, Any]] = []
    for question in dataset.get("questions", []):
        record = records.get(question.get("id"))
        if record is None:
            continue
        if is_selected(question, record):
            entries.append(cohort_entry(question, record))
    return entries


def cohort_ids(entries: list[dict[str, Any]]) -> list[str]:
    return [entry["question_id"] for entry in entries]
