"""Generic, offline normalization of Gold evidence groups for C7-A3."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from evaluation.scripts.capture_c7_a2_post_reranker import EXPECTED_COHORT_IDS
from panda_agent.evaluation import GoldEvidenceGroup, _matched_evidence_groups


MATCHER_IDENTITY = "panda_agent.evaluation._matched_evidence_groups"


def validate_exact_cohort(
    case_ids: Sequence[str],
    *,
    expected_case_ids: Sequence[str] = EXPECTED_COHORT_IDS,
) -> tuple[str, ...]:
    """Require the preregistered case order without encoding case outcomes."""
    actual = tuple(case_ids)
    expected = tuple(expected_case_ids)
    if actual != expected:
        raise ValueError("case IDs must equal the exact preregistered cohort order")
    return actual


def _normalized_payloads(candidate_payloads: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Copy object-style payloads and make the mapping key the fallback object ID."""
    normalized: dict[str, dict[str, Any]] = {}
    for object_id, payload in candidate_payloads.items():
        if not isinstance(payload, Mapping):
            raise TypeError(f"candidate payload for {object_id!r} must be a mapping")
        payload_id = payload.get("object_id")
        if payload_id is not None and payload_id != str(object_id):
            raise ValueError(f"candidate payload object_id conflicts with mapping key: {object_id!r}")
        normalized[str(object_id)] = {**dict(payload), "object_id": str(object_id)}
    return normalized


def project_case_annotations(
    case: Any,
    candidate_payloads: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Project a case's authoritative evidence groups onto frozen payloads.

    Unsupported group forms and matcher errors are recorded and produce no
    mapping.  ``forbidden_evidence`` is deliberately not treated as complete
    negative labeling.
    """
    groups = tuple(getattr(case, "required_evidence_groups", ()))
    object_lookup = _normalized_payloads(candidate_payloads)
    relevant_groups: list[str] = []
    critical_groups: list[str] = []
    relevant_by_object: dict[str, list[str]] = {}
    unsupported_conditions: list[dict[str, str]] = []
    unmatched_group_ids: list[str] = []

    for group in groups:
        if not isinstance(group, GoldEvidenceGroup):
            unsupported_conditions.append(
                {"condition": repr(group), "reason": "unsupported_evidence_group_type"}
            )
            continue
        group_id = group.group_id
        relevant_groups.append(group_id)
        if group.critical:
            critical_groups.append(group_id)
        matched_object_ids: list[str] = []
        matcher_failed = False
        for object_id in sorted(object_lookup):
            try:
                _, provenance = _matched_evidence_groups([group], [object_id], object_lookup)
            except (AttributeError, KeyError, TypeError, ValueError) as error:
                unsupported_conditions.append(
                    {"condition": group_id, "reason": f"matcher_unsupported:{type(error).__name__}"}
                )
                matcher_failed = True
                break
            if provenance and provenance[0].get("object_id") == object_id:
                matched_object_ids.append(object_id)
        if matcher_failed:
            continue
        for object_id in matched_object_ids:
            relevant_by_object.setdefault(object_id, []).append(group_id)
        if not matched_object_ids:
            unmatched_group_ids.append(group_id)

    critical_set = set(critical_groups)
    critical_by_object = {
        object_id: [group_id for group_id in group_ids if group_id in critical_set]
        for object_id, group_ids in relevant_by_object.items()
        if any(group_id in critical_set for group_id in group_ids)
    }
    return {
        "case_id": str(case.id),
        "relevant_groups": relevant_groups,
        "critical_groups": critical_groups,
        "relevant_groups_by_object": relevant_by_object,
        "critical_groups_by_object": critical_by_object,
        "negative_completeness": False,
        "matcher_identity": MATCHER_IDENTITY,
        "unmatched_group_ids": unmatched_group_ids,
        "unsupported_conditions": unsupported_conditions,
        "no_manual_case_specific_mapping": True,
    }


def build_annotations(
    cases: Sequence[Any],
    payloads_by_case: Mapping[str, Mapping[str, Mapping[str, Any]]],
    *,
    expected_case_ids: Sequence[str] = EXPECTED_COHORT_IDS,
) -> dict[str, dict[str, Any]]:
    """Build deterministic case annotations from injected Gold cases and payloads."""
    case_ids = validate_exact_cohort([str(case.id) for case in cases], expected_case_ids=expected_case_ids)
    if set(payloads_by_case) != set(case_ids):
        raise ValueError("candidate payload cases must exactly match the preregistered cohort")
    return {
        case_id: project_case_annotations(case, payloads_by_case[case_id])
        for case_id, case in zip(case_ids, cases, strict=True)
    }
