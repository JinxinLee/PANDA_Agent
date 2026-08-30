"""D3 experimental structured shortcut-replacement plumbing.

The module is deliberately independent from evaluation artifacts.  It accepts
ordinary query/runtime inputs plus an explicit experimental arm, consumes the
existing D2 shadow receipt conservatively, and traverses only accepted D1
relations and curated workflow structure.  It never maps a selected rule or an
evaluation case to semantic targets.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from panda_agent.entity_resolution import (
    AMBIGUOUS,
    RESOLVED_MULTIPLE,
    RESOLVED_UNIQUE,
    UNRESOLVED,
    EntityResolver,
)


SELECTED_D3_RULE_IDS = (
    "lmd_fit_data_chain",
    "event_poca_handoff",
    "pid_two_pass_files",
    "model_factory_theory",
    "effective_acceptance_pipeline",
    "restgas_profile_workflow",
    "root_macro_usage",
)

_TIER_PRIORITY = {"G": 0, "S": 1, "D": 2, "corrective": 3, "N": 4}
class D3Arm(str, Enum):
    LEGACY = "LEGACY"
    ABLATION = "ABLATION"
    STRUCTURED = "STRUCTURED"


@dataclass(frozen=True)
class D3ExperimentConfig:
    """Small nonsemantic D3 treatment configuration."""

    arm: D3Arm
    selected_rule_ids: tuple[str, ...] = SELECTED_D3_RULE_IDS
    structured_treatment_enabled: bool = False

    def __post_init__(self) -> None:
        arm = self.arm if isinstance(self.arm, D3Arm) else D3Arm(self.arm)
        object.__setattr__(self, "arm", arm)
        selected = tuple(self.selected_rule_ids)
        object.__setattr__(self, "selected_rule_ids", selected)
        if len(selected) != len(set(selected)):
            raise ValueError("D3 selected rule IDs must be unique")
        if set(selected) != set(SELECTED_D3_RULE_IDS):
            raise ValueError("D3 experimental modes must suppress exactly the frozen seven rules")
        expected_structured = arm is D3Arm.STRUCTURED
        if self.structured_treatment_enabled is not expected_structured:
            raise ValueError(
                "D3 structured treatment must be enabled only for the STRUCTURED arm"
            )

    @classmethod
    def for_arm(cls, arm: D3Arm | str) -> "D3ExperimentConfig":
        normalized = arm if isinstance(arm, D3Arm) else D3Arm(arm)
        return cls(
            arm=normalized,
            structured_treatment_enabled=normalized is D3Arm.STRUCTURED,
        )

    @property
    def selected_legacy_rules_suppressed(self) -> bool:
        return self.arm in {D3Arm.ABLATION, D3Arm.STRUCTURED}


@dataclass(frozen=True)
class D3ExpansionDecision:
    active_matching_rules: tuple[Any, ...]
    matched_rule_ids: tuple[str, ...]
    selected_matched_rule_ids: tuple[str, ...]
    suppressed_selected_rule_ids: tuple[str, ...]

    def diagnostics(self, config: D3ExperimentConfig) -> dict[str, Any]:
        return {
            "d3_arm": config.arm.value,
            "selected_rule_ids": list(config.selected_rule_ids),
            "structured_treatment_enabled": config.structured_treatment_enabled,
            "selected_legacy_rules_suppressed": config.selected_legacy_rules_suppressed,
            "matched_active_rule_ids": [
                str(rule.rule_id) for rule in self.active_matching_rules
            ],
            "suppressed_selected_rule_ids": list(self.suppressed_selected_rule_ids),
            "diagnostic_counters": {
                "legacy_shortcut_hit_count": len(self.matched_rule_ids),
                "selected_legacy_shortcut_hit_count": len(
                    self.selected_matched_rule_ids
                ),
                "structured_resolution_attempt_count": 0,
                "structured_resolution_status_counts": {},
                "structured_resolution_hit_count": 0,
                "structured_seed_count": 0,
                "structured_relation_traversal_count": 0,
                "structured_workflow_traversal_count": 0,
                "structured_candidate_injection_count": 0,
                "migration_specific_direct_answer_location_injection_count": 0,
                "prohibited_fallback_use_count": 0,
                "evaluation_metadata_runtime_use_count": 0,
                "selected_legacy_payload_reuse_count": 0,
                "same_as_activation_count": 0,
            },
        }


def select_matching_query_expansions(
    question: str,
    rules: Iterable[Any],
    config: D3ExperimentConfig | None,
) -> D3ExpansionDecision:
    """Match rules once and suppress by exact ID before payload access."""

    lowered = question.casefold()
    matched: list[Any] = []
    selected_matches: list[str] = []
    suppressed: list[str] = []
    active: list[Any] = []
    selected = set(config.selected_rule_ids) if config is not None else set()
    should_suppress = bool(config and config.selected_legacy_rules_suppressed)
    for rule in rules:
        if not any(str(trigger).casefold() in lowered for trigger in rule.triggers):
            continue
        matched.append(rule)
        rule_id = str(rule.rule_id)
        if rule_id in selected:
            selected_matches.append(rule_id)
            if should_suppress:
                suppressed.append(rule_id)
                continue
        active.append(rule)
    return D3ExpansionDecision(
        active_matching_rules=tuple(active),
        matched_rule_ids=tuple(str(rule.rule_id) for rule in matched),
        selected_matched_rule_ids=tuple(selected_matches),
        suppressed_selected_rule_ids=tuple(suppressed),
    )


class D3StructuredGraphReader(Protocol):
    def load_objects(self, object_ids: Sequence[str]) -> list[dict[str, Any]]: ...

    def load_accepted_relations(
        self, object_ids: Sequence[str]
    ) -> list[dict[str, Any]]: ...

    def load_curated_workflow_steps(
        self, object_ids: Sequence[str]
    ) -> list[dict[str, Any]]: ...


_OBJECT_COLUMNS = (
    "object_id,source_id,source_version_id,object_type,title,text,"
    "authority_level,locator,metadata,canonical_locator"
)


class PostgresD3StructuredGraphReader:
    """Read-only accepted D1 graph/workflow boundary."""

    def __init__(self, storage: Any) -> None:
        self.storage = storage

    def load_objects(self, object_ids: Sequence[str]) -> list[dict[str, Any]]:
        ids = list(dict.fromkeys(str(value) for value in object_ids if value))
        if not ids:
            return []
        with self.storage.connect() as connection:
            rows = connection.execute(
                f"SELECT {_OBJECT_COLUMNS} FROM knowledge_objects "
                "WHERE object_id=ANY(%s) ORDER BY object_id",
                (ids,),
            ).fetchall()
        columns = _OBJECT_COLUMNS.split(",")
        return [dict(zip(columns, row)) for row in rows]

    def load_accepted_relations(
        self, object_ids: Sequence[str]
    ) -> list[dict[str, Any]]:
        ids = list(dict.fromkeys(str(value) for value in object_ids if value))
        if not ids:
            return []
        with self.storage.connect() as connection:
            rows = connection.execute(
                "SELECT edge_id,subject_id,predicate,object_id,review_status,payload "
                "FROM relation_edges WHERE review_status='accepted' "
                "AND predicate<>'SAME_AS' "
                "AND (subject_id=ANY(%s) OR object_id=ANY(%s)) "
                "ORDER BY subject_id,predicate,object_id,edge_id",
                (ids, ids),
            ).fetchall()
        return [
            {
                "edge_id": row[0],
                "subject_id": row[1],
                "predicate": row[2],
                "object_id": row[3],
                "review_status": row[4],
                "payload": row[5] or {},
            }
            for row in rows
        ]

    def load_curated_workflow_steps(
        self, object_ids: Sequence[str]
    ) -> list[dict[str, Any]]:
        ids = {str(value) for value in object_ids if value}
        if not ids:
            return []
        with self.storage.connect() as connection:
            rows = connection.execute(
                "SELECT step_id,workflow_id,name,payload FROM workflow_steps "
                "WHERE payload->'metadata'->>'curated_seed'='true' "
                "ORDER BY workflow_id,step_id"
            ).fetchall()
        result: list[dict[str, Any]] = []
        for step_id, workflow_id, name, raw_payload in rows:
            payload = dict(raw_payload or {})
            participants = _workflow_participants(
                {"step_id": step_id, "workflow_id": workflow_id, "payload": payload}
            )
            if ids.intersection(participants):
                result.append(
                    {
                        "step_id": str(step_id),
                        "workflow_id": str(workflow_id),
                        "name": str(name),
                        "payload": payload,
                    }
                )
        return result


@dataclass(frozen=True)
class _Seed:
    object_id: str
    mention_text: str
    support_span: str
    resolution_status: str
    tier: str
    authority_class: str
    matched_object_id: str | None
    canonical_object_id: str | None
    allow_traversal: bool = True


@dataclass
class D3StructuredContribution:
    candidates: list[dict[str, Any]] = field(default_factory=list)
    candidate_provenance: list[dict[str, Any]] = field(default_factory=list)
    resolution_receipt: dict[str, Any] = field(default_factory=dict)
    diagnostic_counters: dict[str, Any] = field(default_factory=dict)
    excluded_resolution_reasons: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "resolution_receipt": self.resolution_receipt,
            "structured_candidate_provenance": self.candidate_provenance,
            "excluded_resolution_reasons": self.excluded_resolution_reasons,
            "diagnostic_counters": self.diagnostic_counters,
        }


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "as_dict"):
        return value.as_dict()
    raise TypeError(f"value does not expose a mapping receipt: {type(value).__name__}")


def _evidence_dicts(resolution: Any) -> list[dict[str, Any]]:
    return [_as_dict(item) for item in (_field(resolution, "evidence", []) or [])]


def _candidate_dicts(resolution: Any) -> list[dict[str, Any]]:
    return [dict(item) for item in (_field(resolution, "candidates", []) or [])]


def _is_whole_question_fallback(
    resolution: Any, question: str, plan: Mapping[str, Any]
) -> bool:
    if str(_field(resolution, "mention_kind", "")) != "descriptive":
        return False
    if str(_field(resolution, "mention_text", "")).strip() != question.strip():
        return False
    diagnostics = plan.get("analysis_diagnostics", {}) or {}
    delta = diagnostics.get("analyzer_accepted_semantic_delta", {}) or {}
    grounded = {
        str(item.get("value", "")).strip()
        for item in delta.get("concepts", []) or []
        if isinstance(item, Mapping)
    }
    return question.strip() not in grounded


def _resolution_tier(resolution: Any) -> str:
    tiers = [
        str(item.get("tier", "N"))
        for item in _evidence_dicts(resolution)
        if item.get("kind") != "same_as"
    ]
    tiers.extend(str(item.get("tier", "N")) for item in _candidate_dicts(resolution))
    return min(tiers or ["N"], key=lambda value: _TIER_PRIORITY.get(value, 99))


def _seed_authority(tier: str) -> str:
    if tier == "G":
        return "AUTHORITATIVE_BOUNDED_IDENTITY"
    if tier == "S":
        return "AUTHORITATIVE_BOUNDED_MATCHED_RECORD"
    return "NONAUTHORITATIVE_ADVISORY"


def _derive_seeds(
    receipt: Any,
    question: str,
    plan: Mapping[str, Any],
) -> tuple[list[_Seed], list[dict[str, Any]], Counter[str]]:
    seeds: dict[str, _Seed] = {}
    excluded: list[dict[str, Any]] = []
    statuses: Counter[str] = Counter()
    for resolution in _field(receipt, "resolutions", []) or []:
        status = str(_field(resolution, "status", UNRESOLVED))
        statuses[status] += 1
        mention = str(_field(resolution, "mention_text", ""))
        if _is_whole_question_fallback(resolution, question, plan):
            excluded.append({"mention": mention, "reason": "whole_question_fallback_prohibited"})
            continue
        if status == RESOLVED_MULTIPLE:
            excluded.append({"mention": mention, "reason": "resolved_multiple_inactive"})
            continue

        diagnostics = _field(resolution, "diagnostics", {}) or {}
        candidates = _candidate_dicts(resolution)
        corrective = bool(diagnostics.get("corrective"))
        if corrective:
            for candidate in candidates:
                object_id = str(candidate.get("object_id", ""))
                if not object_id:
                    continue
                seeds.setdefault(
                    object_id,
                    _Seed(
                        object_id=object_id,
                        mention_text=mention,
                        support_span=str(_field(resolution, "support_span", mention)),
                        resolution_status=status,
                        tier="corrective",
                        authority_class="NONAUTHORITATIVE_ADVISORY",
                        matched_object_id=None,
                        canonical_object_id=None,
                        allow_traversal=False,
                    ),
                )
            continue

        tier = _resolution_tier(resolution)
        if status == RESOLVED_UNIQUE:
            object_id = str(_field(resolution, "matched_object_id", "") or "")
            if not object_id or tier not in {"G", "S", "D"}:
                continue
            canonical = _field(resolution, "canonical_object_id") if tier == "G" else None
            seeds.setdefault(
                object_id,
                _Seed(
                    object_id=object_id,
                    mention_text=mention,
                    support_span=str(_field(resolution, "support_span", mention)),
                    resolution_status=status,
                    tier=tier,
                    authority_class=_seed_authority(tier),
                    matched_object_id=object_id,
                    canonical_object_id=str(canonical) if canonical else None,
                ),
            )
            continue
        if status == AMBIGUOUS:
            for candidate in candidates:
                object_id = str(candidate.get("object_id", ""))
                candidate_tier = str(candidate.get("tier", tier))
                if not object_id or candidate_tier != "D":
                    continue
                seeds.setdefault(
                    object_id,
                    _Seed(
                        object_id=object_id,
                        mention_text=mention,
                        support_span=str(_field(resolution, "support_span", mention)),
                        resolution_status=status,
                        tier="D",
                        authority_class="NONAUTHORITATIVE_ADVISORY",
                        matched_object_id=None,
                        canonical_object_id=None,
                    ),
                )
            continue
        if status == UNRESOLVED:
            excluded.append({"mention": mention, "reason": "unresolved_no_negative_filter"})
    return [seeds[key] for key in sorted(seeds)], excluded, statuses


def _workflow_participants(step: Mapping[str, Any]) -> list[str]:
    payload = step.get("payload", {}) or {}
    values: list[str] = [
        str(step.get("workflow_id", "")),
        str(step.get("step_id", "")),
        str(payload.get("entrypoint_object_id", "") or ""),
    ]
    for field_name in (
        "inputs",
        "outputs",
        "predecessor_step_ids",
        "successor_step_ids",
    ):
        values.extend(str(value) for value in payload.get(field_name, []) or [])
    return list(dict.fromkeys(value for value in values if value))


def _object_in_scope(
    row: Mapping[str, Any],
    plan: Mapping[str, Any],
    context_sources: Sequence[str],
) -> bool:
    source_id = str(row.get("source_id", ""))
    targets = [str(value) for value in plan.get("target_repositories", []) or []]
    allowed = {*targets, *context_sources, "curated_panda_domain"}
    if targets and source_id not in allowed:
        return False
    locked = plan.get("resolved_versions", {}) or {}
    if source_id in targets and source_id in locked:
        return str(row.get("source_version_id", "")) == f"{source_id}@{locked[source_id]}"
    return True


def build_structured_contribution(
    question: str,
    plan: Mapping[str, Any] | Any,
    *,
    resolver: Any,
    graph_reader: D3StructuredGraphReader,
    context_sources: Sequence[str] = (),
    max_relation_hops: int = 2,
    max_candidates: int = 64,
) -> D3StructuredContribution:
    """Build one bounded, additive, provenance-rich D3 candidate stream."""

    if not isinstance(question, str):
        raise TypeError("question must be a string")
    if max_relation_hops < 0 or max_relation_hops > 2:
        raise ValueError("D3 relation traversal must stay within zero to two hops")
    if max_candidates < 1:
        raise ValueError("max_candidates must be positive")
    plan_mapping = plan.model_dump(mode="json") if hasattr(plan, "model_dump") else dict(plan)
    receipt = resolver.resolve_shadow(question, plan_mapping)
    seeds, excluded, statuses = _derive_seeds(receipt, question, plan_mapping)

    seed_by_id = {seed.object_id: seed for seed in seeds}
    seed_rows = {
        str(row["object_id"]): row
        for row in graph_reader.load_objects(sorted(seed_by_id))
        if _object_in_scope(row, plan_mapping, context_sources)
    }
    candidates: dict[str, dict[str, Any]] = {}
    provenance: dict[str, dict[str, Any]] = {}
    path_by_id: dict[str, list[dict[str, Any]]] = {}
    workflow_by_id: dict[str, dict[str, Any] | None] = {}
    root_seed_by_id: dict[str, str] = {}
    traversable: set[str] = set()

    def add_candidate(
        object_id: str,
        row: dict[str, Any],
        *,
        seed: _Seed,
        relation_path: list[dict[str, Any]],
        workflow_step: dict[str, Any] | None,
        reason: str,
    ) -> bool:
        if object_id in candidates or len(candidates) >= max_candidates:
            return False
        candidates[object_id] = row
        provenance[object_id] = {
            "treatment": "d3_structured",
            "query_grounded_support": {
                "mention": seed.mention_text,
                "support_span": seed.support_span,
            },
            "resolution_status": seed.resolution_status,
            "evidence_tier": seed.tier,
            "authority_class": seed.authority_class,
            "matched_object_id": seed.matched_object_id,
            "canonical_object_id": seed.canonical_object_id,
            "seed_object_id": seed.object_id,
            "relation_path": relation_path,
            "workflow_step": workflow_step,
            "candidate_object_id": object_id,
            "candidate_source_id": row.get("source_id"),
            "candidate_source_version_id": row.get("source_version_id"),
            "candidate_locator": row.get("locator") or {},
            "candidate_identity_authority": (
                seed.authority_class if not relation_path and workflow_step is None else "NONE"
            ),
            "reason_included": reason,
        }
        path_by_id[object_id] = list(relation_path)
        workflow_by_id[object_id] = workflow_step
        root_seed_by_id[object_id] = seed.object_id
        return True

    for object_id in sorted(seed_rows):
        seed = seed_by_id[object_id]
        add_candidate(
            object_id,
            seed_rows[object_id],
            seed=seed,
            relation_path=[],
            workflow_step=None,
            reason="query-grounded D2 seed included without legacy shortcut payload",
        )
        if seed.allow_traversal:
            traversable.add(object_id)

    frontier = sorted(traversable)
    relation_traversals = 0
    workflow_traversals = 0
    for _depth in range(max_relation_hops):
        if not frontier or len(candidates) >= max_candidates:
            break
        new_ids: dict[str, tuple[str, list[dict[str, Any]], dict[str, Any] | None, str]] = {}
        for edge in graph_reader.load_accepted_relations(frontier):
            if edge.get("review_status") != "accepted" or edge.get("predicate") == "SAME_AS":
                continue
            subject = str(edge.get("subject_id", ""))
            obj = str(edge.get("object_id", ""))
            for current, neighbor, direction in (
                (subject, obj, "forward"),
                (obj, subject, "reverse"),
            ):
                if (
                    current not in frontier
                    or not neighbor
                    or neighbor in candidates
                    or neighbor in new_ids
                ):
                    continue
                path = [
                    *path_by_id.get(current, []),
                    {
                        "edge_id": edge.get("edge_id"),
                        "predicate": edge.get("predicate"),
                        "subject_id": subject,
                        "object_id": obj,
                        "traversal_direction": direction,
                    },
                ]
                new_ids[neighbor] = (
                    current,
                    path,
                    workflow_by_id.get(current),
                    "accepted D1 relation traversal",
                )

        for step in graph_reader.load_curated_workflow_steps(frontier):
            participants = _workflow_participants(step)
            anchors = sorted(set(frontier).intersection(participants))
            if not anchors:
                continue
            current = anchors[0]
            step_receipt = {
                "workflow_id": step.get("workflow_id"),
                "step_id": step.get("step_id"),
                "name": step.get("name"),
                "participants": participants,
            }
            for neighbor in sorted(participants):
                if not neighbor or neighbor in candidates or neighbor in new_ids:
                    continue
                new_ids[neighbor] = (
                    current,
                    list(path_by_id.get(current, [])),
                    step_receipt,
                    "accepted curated workflow-step participant",
                )

        rows = {
            str(row["object_id"]): row
            for row in graph_reader.load_objects(sorted(new_ids))
            if _object_in_scope(row, plan_mapping, context_sources)
        }
        next_frontier: list[str] = []
        for object_id in sorted(rows):
            current, path, workflow_step, reason = new_ids[object_id]
            root_seed_id = root_seed_by_id.get(current, current)
            seed = seed_by_id[root_seed_id]
            added = add_candidate(
                object_id,
                rows[object_id],
                seed=seed,
                relation_path=path,
                workflow_step=workflow_step,
                reason=reason,
            )
            if not added:
                continue
            root_seed_by_id[object_id] = root_seed_id
            if reason == "accepted D1 relation traversal":
                relation_traversals += 1
            else:
                workflow_traversals += 1
            next_frontier.append(object_id)
        frontier = next_frontier

    counters = {
        "structured_resolution_attempt_count": 1,
        "structured_resolution_status_counts": dict(sorted(statuses.items())),
        "structured_resolution_hit_count": sum(
            1 for seed in seeds if seed.object_id in seed_rows
        ),
        "structured_seed_count": len(seed_rows),
        "structured_relation_traversal_count": relation_traversals,
        "structured_workflow_traversal_count": workflow_traversals,
        "structured_candidate_injection_count": len(candidates),
        "migration_specific_direct_answer_location_injection_count": 0,
        "prohibited_fallback_use_count": 0,
        "evaluation_metadata_runtime_use_count": 0,
        "selected_legacy_payload_reuse_count": 0,
        "same_as_activation_count": 0,
    }
    return D3StructuredContribution(
        candidates=list(candidates.values()),
        candidate_provenance=list(provenance.values()),
        resolution_receipt=_as_dict(receipt),
        diagnostic_counters=counters,
        excluded_resolution_reasons=excluded,
    )


def build_structured_contribution_from_storage(
    question: str,
    plan: Mapping[str, Any] | Any,
    *,
    storage: Any,
    context_sources: Sequence[str] = (),
    max_relation_hops: int = 2,
) -> D3StructuredContribution:
    resolver = EntityResolver(storage, context_sources=context_sources)
    reader = PostgresD3StructuredGraphReader(storage)
    return build_structured_contribution(
        question,
        plan,
        resolver=resolver,
        graph_reader=reader,
        context_sources=context_sources,
        max_relation_hops=max_relation_hops,
    )


__all__ = [
    "SELECTED_D3_RULE_IDS",
    "D3Arm",
    "D3ExperimentConfig",
    "D3ExpansionDecision",
    "D3StructuredContribution",
    "D3StructuredGraphReader",
    "PostgresD3StructuredGraphReader",
    "select_matching_query_expansions",
    "build_structured_contribution",
    "build_structured_contribution_from_storage",
]
