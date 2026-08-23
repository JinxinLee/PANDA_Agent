"""C7-A1 shadow-only explicit evidence-selection contract.

This module deliberately consumes frozen plain data and is not imported by the
production retrieval path.  It makes post-reranker M/P/S decisions inspectable
without issuing retrieval, database, model, or reranker calls.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
import math
from typing import Any, Mapping, Sequence


POLICY_ID = "c7.explicit_selection.v1"


class ConstraintType(str, Enum):
    PROTECTED = "PROTECTED"
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"
    MAXIMUM = "MAXIMUM"


class ConstraintDimension(str, Enum):
    SOURCE_ID = "SOURCE_ID"
    SOURCE_TYPE = "SOURCE_TYPE"
    RETRIEVAL_CHANNEL = "RETRIEVAL_CHANNEL"
    OBJECT_ID = "OBJECT_ID"


@dataclass(frozen=True)
class SelectionConstraint:
    identity: str
    constraint_type: ConstraintType
    dimension: ConstraintDimension
    value: str
    provenance: str
    reason: str
    limit: int | None = None
    not_question_required: bool = False

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["constraint_type"] = self.constraint_type.value
        data["dimension"] = self.dimension.value
        return data


@dataclass(frozen=True)
class ShadowSelectionPolicy:
    policy_id: str
    final_evidence_limit: int
    constraints: tuple[SelectionConstraint, ...]
    duplicate_policy: str = "serialized_locator_or_object_id_fallback"
    priority_policy: str = "rank_first:paper_hint,required,protected,preferred,stage_m_rank"

    def as_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "final_evidence_limit": self.final_evidence_limit,
            "constraints": [constraint.as_dict() for constraint in self.constraints],
            "duplicate_policy": self.duplicate_policy,
            "priority_policy": self.priority_policy,
        }


@dataclass(frozen=True)
class FrozenShadowInput:
    """Complete, read-free post-reranker state expected from future C7-A2."""

    plan: Mapping[str, Any] | Any
    stage_r_order: tuple[str, ...]
    stage_f_order: tuple[str, ...]
    payloads: Mapping[str, Mapping[str, Any]]
    retrieval_channels: Mapping[str, Sequence[str]]
    mandatory_symbol_ids: frozenset[str] = frozenset()


@dataclass(frozen=True)
class ShadowSelectionResult:
    policy: dict[str, Any]
    stage_m_order: list[str]
    stage_p_order: list[str]
    selected_object_ids: list[str]
    candidate_receipts: list[dict[str, Any]]
    constraint_receipts: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _source_type_of(item: Mapping[str, Any]) -> str:
    """Behavior-equivalent copy of production retrieval._source_type_of."""
    if item["source_id"] in {"li_2026", "karavdina_2015", "pflueger_2017"}:
        return "paper"
    if "sphinx" in item["source_id"]:
        return "documentation"
    locator = item.get("locator") or {}
    path = (locator.get("path") or "").replace("\\", "/").lower()
    if path.startswith(("docs/", "doc/")):
        return "documentation"
    if item.get("object_type") in {"workflow", "python_script", "shell_script"}:
        return "workflow"
    if item.get("object_type") == "readme_section":
        return "readme"
    if item.get("object_type") == "python_script":
        return "workflow"
    return "code"


def stage_m_merge(stage_r_order: Sequence[str], stage_f_order: Sequence[str]) -> list[str]:
    """Raw Stage R followed by remaining Stage F, deduplicated by object ID."""
    return list(dict.fromkeys([*stage_r_order, *stage_f_order]))


def _plan_value(plan: Mapping[str, Any] | Any, name: str, default: Any) -> Any:
    return plan.get(name, default) if isinstance(plan, Mapping) else getattr(plan, name, default)


def _locator_identity(item: Mapping[str, Any], object_id: str) -> str:
    locator = item.get("locator") or {}
    if not any(value not in (None, "", [], {}) for value in locator.values()):
        return f"object:{object_id}"
    return json.dumps(locator, sort_keys=True, separators=(",", ":"))


def _constraint(identity: int, kind: ConstraintType, dimension: ConstraintDimension,
                value: str, provenance: str, reason: str, limit: int | None = None,
                not_question_required: bool = False) -> SelectionConstraint:
    return SelectionConstraint(
        identity=f"{POLICY_ID}:{identity:02d}", constraint_type=kind,
        dimension=dimension, value=value, provenance=provenance, reason=reason,
        limit=limit, not_question_required=not_question_required,
    )


def _explicit_target_repositories(plan: Mapping[str, Any] | Any) -> set[str]:
    diagnostics = _plan_value(plan, "analysis_diagnostics", {}) or {}
    parsed = diagnostics.get("deterministic_parse", {}) if isinstance(diagnostics, Mapping) else {}
    provenance = parsed.get("provenance", {}) if isinstance(parsed, Mapping) else {}
    records = provenance.get("target_repositories", []) if isinstance(provenance, Mapping) else []
    targets = set(_plan_value(plan, "target_repositories", []) or [])
    return {
        str(record.get("value")) for record in records if isinstance(record, Mapping)
        and record.get("source") == "explicit_query_reference"
        and record.get("value") in targets
    }


def translate_current_policy(
    plan: Mapping[str, Any] | Any,
    final_evidence_limit: int = 12,
    mandatory_symbol_ids: Sequence[str] = (),
) -> ShadowSelectionPolicy:
    """Translate existing plan fields without creating new query inference."""
    constraints: list[SelectionConstraint] = []
    next_identity = 1
    constraints.append(_constraint(
        next_identity, ConstraintType.MAXIMUM, ConstraintDimension.SOURCE_ID, "*",
        "current_selector_compatibility", "current max_per_source",
        max(2, math.ceil(final_evidence_limit / 3)),
    ))
    next_identity += 1
    for source_type, fraction in sorted((_plan_value(plan, "source_budgets", {}) or {}).items()):
        if source_type == "graph":
            constraints.append(_constraint(
                next_identity, ConstraintType.MAXIMUM, ConstraintDimension.RETRIEVAL_CHANNEL,
                "graph", "reviewed_static_intent_policy", "graph source_budgets channel normalization",
                max(1, math.ceil(float(fraction) * final_evidence_limit)),
            ))
            next_identity += 1
            continue
        constraints.append(_constraint(
            next_identity, ConstraintType.MAXIMUM, ConstraintDimension.SOURCE_TYPE,
            str(source_type), "current_selector_compatibility", "source_budgets",
            max(1, math.ceil(float(fraction) * final_evidence_limit)),
        ))
        next_identity += 1
    for source_type in _plan_value(plan, "required_source_types", []) or []:
        dimensions = ([ConstraintDimension.RETRIEVAL_CHANNEL] if source_type == "graph"
                      else ([ConstraintDimension.SOURCE_TYPE, ConstraintDimension.RETRIEVAL_CHANNEL]
                            if source_type == "workflow" else [ConstraintDimension.SOURCE_TYPE]))
        for dimension in dimensions:
            constraints.append(_constraint(
                next_identity, ConstraintType.PREFERRED, dimension, str(source_type),
                "reviewed_static_intent_policy", "intent required_sources default",
                not_question_required=True,
            ))
            next_identity += 1
    for source_id in sorted(_explicit_target_repositories(plan)):
        constraints.append(_constraint(
            next_identity, ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            source_id, "explicit_query_reference", "explicit target repository",
        ))
        next_identity += 1
    for object_id in sorted(set(mandatory_symbol_ids)):
        constraints.append(_constraint(
            next_identity, ConstraintType.PROTECTED, ConstraintDimension.OBJECT_ID,
            object_id, "exact_symbol", "mandatory exact-symbol evidence",
        ))
        next_identity += 1
    return ShadowSelectionPolicy(POLICY_ID, final_evidence_limit, tuple(constraints))


def _matches(constraint: SelectionConstraint, object_id: str, item: Mapping[str, Any],
             channels: Sequence[str], source_type: str) -> bool:
    if constraint.dimension is ConstraintDimension.OBJECT_ID:
        return object_id == constraint.value
    if constraint.dimension is ConstraintDimension.SOURCE_ID:
        return constraint.value == "*" or item.get("source_id") == constraint.value
    if constraint.dimension is ConstraintDimension.SOURCE_TYPE:
        return source_type == constraint.value
    return constraint.value in channels


def shadow_select(frozen: FrozenShadowInput, policy: ShadowSelectionPolicy | None = None) -> ShadowSelectionResult:
    """Run explicit M/P/S selection over frozen inputs only."""
    policy = policy or translate_current_policy(
        frozen.plan, mandatory_symbol_ids=tuple(frozen.mandatory_symbol_ids)
    )
    stage_m = stage_m_merge(frozen.stage_r_order, frozen.stage_f_order)
    missing = [object_id for object_id in stage_m if object_id not in frozen.payloads]
    if missing:
        raise ValueError(f"frozen shadow input lacks payloads for: {', '.join(missing)}")
    facets = {
        object_id: (
            frozen.payloads[object_id], list(frozen.retrieval_channels.get(object_id, ())),
            _source_type_of(frozen.payloads[object_id]),
        )
        for object_id in stage_m
    }
    matched = {
        object_id: [constraint for constraint in policy.constraints if _matches(
            constraint, object_id, *facets[object_id]
        )]
        for object_id in stage_m
    }
    hints = _plan_value(frozen.plan, "paper_page_hints", {}) or {}
    def priority(object_id: str) -> tuple[int, int, int, int, int]:
        item, _channels, _source_type = facets[object_id]
        page = (item.get("locator") or {}).get("pdf_page")
        hinted = item.get("source_id") in hints and page is not None and int(page) in hints[item["source_id"]]
        constraints = matched[object_id]
        return (
            0 if hinted else 1,
            0 if any(c.constraint_type is ConstraintType.REQUIRED for c in constraints) else 1,
            0 if any(c.constraint_type is ConstraintType.PROTECTED for c in constraints) else 1,
            0 if any(c.constraint_type is ConstraintType.PREFERRED for c in constraints) else 1,
            stage_m.index(object_id),
        )
    stage_p = sorted(stage_m, key=priority)
    selected: list[str] = []
    selected_locator: set[str] = set()
    selected_counts: dict[tuple[ConstraintDimension, str], int] = {}
    candidate_receipts: list[dict[str, Any]] = []
    for p_index, object_id in enumerate(stage_p, 1):
        item, channels, source_type = facets[object_id]
        constraints = matched[object_id]
        protected = any(c.constraint_type is ConstraintType.PROTECTED for c in constraints)
        required = any(c.constraint_type is ConstraintType.REQUIRED for c in constraints)
        locator = _locator_identity(item, object_id)
        maximum_checks: list[dict[str, Any]] = []
        violated: list[SelectionConstraint] = []
        for constraint in policy.constraints:
            if constraint.constraint_type is not ConstraintType.MAXIMUM or not _matches(
                constraint, object_id, item, channels, source_type
            ):
                continue
            count_key = (constraint.dimension, item["source_id"] if constraint.dimension is ConstraintDimension.SOURCE_ID else constraint.value)
            count = selected_counts.get(count_key, 0)
            maximum_checks.append({"constraint_id": constraint.identity, "limit": constraint.limit, "selected_count": count, "would_exceed": count >= (constraint.limit or 0)})
            if count >= (constraint.limit or 0):
                violated.append(constraint)
        receipt = {
            "object_id": object_id,
            "stage_m_rank": stage_m.index(object_id) + 1,
            "stage_p_rank": p_index,
            "final_decision": "EXCLUDED",
            "decision_reason": "",
            "source_id": item["source_id"],
            "source_type": source_type,
            "retrieval_channels": channels,
            "locator_identity": locator,
            "matched_constraints": [constraint.identity for constraint in constraints],
            "priority_reasons": [
                *(["paper_page_hint"] if priority(object_id)[0] == 0 else []),
                *(["required"] if required else []),
                *(["protected"] if protected else []),
                *(["preferred"] if any(c.constraint_type is ConstraintType.PREFERRED for c in constraints) else []),
                "stage_m_rank",
            ],
            "protected": protected,
            "required": required,
            "maximum_checks": maximum_checks,
            "duplicate_status": "UNIQUE",
            "admission_phase": "stage_s",
            "displaced_by": None,
            "blocking_constraint": None,
        }
        valid = item.get("valid", True) and item.get("source_version_valid", True)
        if not valid:
            receipt.update(decision_reason="invalid_candidate", blocking_constraint="candidate_validity")
        elif locator in selected_locator:
            receipt.update(decision_reason="duplicate_locator", duplicate_status="DUPLICATE", blocking_constraint="duplicate_locator")
        elif len(selected) >= policy.final_evidence_limit:
            receipt.update(decision_reason="final_evidence_limit", blocking_constraint="final_evidence_limit")
        elif violated and not protected:
            ids = [constraint.identity for constraint in violated]
            receipt.update(decision_reason="maximum", blocking_constraint=ids[0], displaced_by=ids)
        else:
            selected.append(object_id)
            selected_locator.add(locator)
            for constraint in policy.constraints:
                if constraint.constraint_type is ConstraintType.MAXIMUM and _matches(
                    constraint, object_id, item, channels, source_type
                ):
                    key = (constraint.dimension, item["source_id"] if constraint.dimension is ConstraintDimension.SOURCE_ID else constraint.value)
                    selected_counts[key] = selected_counts.get(key, 0) + 1
            receipt.update(final_decision="SELECTED", decision_reason=("protected_override" if protected and violated else "admitted"))
        candidate_receipts.append(receipt)
    constraint_receipts: list[dict[str, Any]] = []
    for constraint in policy.constraints:
        matched_ids = [object_id for object_id in stage_p if constraint in matched[object_id]]
        selected_ids = [object_id for object_id in selected if constraint in matched[object_id]]
        if constraint.constraint_type is ConstraintType.REQUIRED:
            status = "satisfied" if selected_ids else "unsatisfied"
        elif not matched_ids:
            status = "not_applicable"
        elif constraint.constraint_type is ConstraintType.MAXIMUM:
            ordinary_selected = [
                object_id for object_id in selected_ids
                if not any(candidate.constraint_type is ConstraintType.PROTECTED for candidate in matched[object_id])
            ]
            if constraint.dimension is ConstraintDimension.SOURCE_ID and constraint.value == "*":
                counts: dict[str, int] = {}
                for object_id in ordinary_selected:
                    source_id = facets[object_id][0]["source_id"]
                    counts[source_id] = counts.get(source_id, 0) + 1
                status = "satisfied" if all(count <= (constraint.limit or 0) for count in counts.values()) else "unsatisfied"
            else:
                status = "satisfied" if len(ordinary_selected) <= (constraint.limit or 0) else "unsatisfied"
        else:
            status = "satisfied" if selected_ids else "unsatisfied"
        constraint_receipts.append({
            "constraint_id": constraint.identity,
            "constraint_type": constraint.constraint_type.value,
            "dimension": constraint.dimension.value,
            "value": constraint.value,
            "provenance": constraint.provenance,
            "matched_candidate_ids": matched_ids,
            "status": status,
            "selected_candidate_ids": selected_ids,
        })
    return ShadowSelectionResult(policy.as_dict(), stage_m, stage_p, selected, candidate_receipts, constraint_receipts)
