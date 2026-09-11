"""Deterministic tests for the E3-A2 mechanical cohort selector.

Pure dataset/logic tests: zero provider calls, zero product-node execution.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EV = ROOT / "evaluation"
_spec = importlib.util.spec_from_file_location(
    "e3_a2_cohort_selector", EV / "e3_a2_cohort_selector.py"
)
selector = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = selector
_spec.loader.exec_module(selector)


def make_question(**overrides):
    base = {
        "id": "n900",
        "language": "en",
        "expected_status": "answered",
        "review_status": "approved",
        "required_answer_points": [
            {"point_id": "p1", "text": "a", "critical": True},
            {"point_id": "p2", "text": "b", "critical": True},
        ],
        "required_evidence_groups": [
            {"group_id": "e1", "critical": True},
            {"group_id": "e2", "critical": True},
        ],
    }
    base.update(overrides)
    return base


def make_curation(
    *,
    representativeness="representative",
    evidence_topology="multi_hop",
    source_scope="single_source",
    repository_scope="single_repository",
):
    return {
        "question_id": "n900",
        "representativeness": {"class": representativeness},
        "coverage": {
            "evidence_topology": evidence_topology,
            "source_scope": source_scope,
            "repository_scope": repository_scope,
            "difficulty": "moderate",
        },
    }


def test_fully_qualifying_case_is_selected():
    assert selector.is_selected(make_question(), make_curation())


def test_review_status_language_and_expected_status_boundaries():
    assert not selector.is_selected(
        make_question(review_status="pending"), make_curation()
    )
    assert not selector.is_selected(make_question(language="zh"), make_curation())
    assert not selector.is_selected(
        make_question(expected_status="insufficient_evidence"), make_curation()
    )


def test_representativeness_and_criticality_boundaries():
    assert not selector.is_selected(
        make_question(), make_curation(representativeness="filler")
    )
    one_point = make_question()
    one_point["required_answer_points"] = [{"point_id": "p1", "text": "a", "critical": True}]
    assert not selector.is_selected(one_point, make_curation())
    non_critical_second = make_question()
    non_critical_second["required_answer_points"] = [
        {"point_id": "p1", "text": "a", "critical": True},
        {"point_id": "p2", "text": "b", "critical": False},
    ]
    assert not selector.is_selected(non_critical_second, make_curation())
    one_group = make_question()
    one_group["required_evidence_groups"] = [{"group_id": "e1", "critical": True}]
    assert not selector.is_selected(one_group, make_curation())


def test_topology_scope_disjunction_boundaries():
    assert selector.is_selected(
        make_question(), make_curation(evidence_topology="multi_hop")
    )
    assert selector.is_selected(
        make_question(), make_curation(source_scope="cross_source")
    )
    assert selector.is_selected(
        make_question(), make_curation(repository_scope="cross_repository")
    )
    assert not selector.is_selected(
        make_question(),
        make_curation(
            evidence_topology="single_hop",
            source_scope="single_source",
            repository_scope="single_repository",
        ),
    )


def test_real_dataset_selection_is_mechanical_and_guarded():
    dataset, curation = selector.load_novel_dev()
    assert dataset["benchmark_version"] == selector.DATASET_BENCHMARK_VERSION
    assert curation["benchmark_version"] == selector.DATASET_BENCHMARK_VERSION
    assert len(dataset["questions"]) == selector.EXPECTED_DATASET_COUNT
    entries = selector.select_cohort(dataset, curation)
    ids = selector.cohort_ids(entries)
    assert len(ids) >= 8 and len(ids) <= 20
    assert ids == sorted(ids, key=lambda q: int(q[1:]))
    for entry in entries:
        assert entry["representativeness_class"] == "representative"
        assert entry["critical_answer_points"] >= 2
        assert entry["critical_evidence_groups"] >= 2
        assert (
            entry["evidence_topology"] != "single_hop"
            or entry["source_scope"] == "cross_source"
            or entry["repository_scope"] == "cross_repository"
        )


def test_selector_matches_frozen_manifest():
    manifest_path = EV / "e3_a2_targeted_recovery_manifest.json"
    if not manifest_path.exists():
        pytest.fail("frozen E3-A2 manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = selector.select_cohort()
    assert selector.cohort_ids(entries) == manifest["cohort_ids"]
    assert entries == manifest["cohort"]
