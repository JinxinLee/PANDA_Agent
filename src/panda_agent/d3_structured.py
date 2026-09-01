"""D3 and D3.5 experimental structured shortcut-replacement and evidence-link bridging plumbing.

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
import re
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

SHARED_SEED_CAP = 8
MAX_CONTAINMENT_TRANSITIONS_PER_SEED = 1
MAX_NONTERMINAL_TRANSITIONS_PER_PATH = 2
GLOBAL_REACHABLE_STRUCTURE_CAP = 32
GLOBAL_BRIDGED_CANDIDATE_CAP = 20

# Predicate allowlist and direction policy (D3.5-A0 Section 9)
# Default is DENY unless explicitly listed.
_ALLOWED_PREDICATES: dict[str, dict[str, Any]] = {
    # Dataflow
    "PRODUCES": {"forward": True, "reverse": True, "class": "DATAFLOW"},
    "CONSUMES": {"forward": True, "reverse": True, "class": "DATAFLOW"},
    "PRODUCES_INPUT_FOR": {"forward": True, "reverse": True, "class": "DATAFLOW"},
    # Implementation / Formalization
    "IMPLEMENTS": {"forward": True, "reverse": True, "class": "IMPLEMENTATION_AND_FORMALIZATION"},
    "FORMALIZES": {"forward": True, "reverse": True, "class": "IMPLEMENTATION_AND_FORMALIZATION"},
    "IMPLEMENTED_AS_PIPELINE": {"forward": True, "reverse": True, "class": "IMPLEMENTATION_AND_FORMALIZATION"},
    "THEORETICAL_BASIS_FOR": {"forward": True, "reverse": True, "class": "IMPLEMENTATION_AND_FORMALIZATION"},
    # Workflow / Parameterization
    "PRODUCES_PROFILE_FOR": {"forward": True, "reverse": True, "class": "WORKFLOW_AND_PARAMETERIZATION"},
    "PARAMETERIZES": {"forward": True, "reverse": True, "class": "WORKFLOW_AND_PARAMETERIZATION"},
    "CORRECTS": {"forward": True, "reverse": True, "class": "WORKFLOW_AND_PARAMETERIZATION"},
    # Documentation
    "OPERATIONALLY_DOCUMENTS": {"forward": True, "reverse": True, "class": "DOCUMENTATION"},
    # Repository Provenance (Forward only; reverse prohibited)
    "FORKED_FROM": {"forward": True, "reverse": False, "class": "REPOSITORY_PROVENANCE"},
}

_FILE_LEVEL_TYPES = {
    "source_file",
    "macro",
    "python_script",
    "shell_script",
    "readme_section",
    "sphinx_page",
    "document",
    "document_reference",
}

_PROCESS_TYPES = {
    "workflow",
    "subsystem",
    "process",
    "pipeline",
    "macro",
    "python_script",
    "shell_script",
    "source_file",
}

_DATA_PRODUCT_TYPES = {
    "data_product",
    "root_tree",
    "file_pattern",
    "configuration_key",
    "source_file",
    "macro",
}

_CONCEPT_TYPES = {
    "physics_concept",
    "concept",
    "theory",
    "model",
}

_DOCUMENT_TYPES = {
    "document_reference",
    "document",
    "paper",
    "readme_section",
    "sphinx_page",
}

_REPOSITORY_TYPES = {
    "repository_version",
    "repository",
}

_CONFIGURATION_TYPES = {
    "configuration_key",
    "configuration",
    "file_pattern",
}

_CURATED_DOMAIN_TYPES = {
    "workflow",
    "physics_concept",
    "concept",
    "theory",
    "model",
    "configuration_key",
    "configuration",
    "subsystem",
    "repository_version",
    "repository",
    "file_pattern",
    "data_product",
    "root_tree",
}

_PREDICATE_ENDPOINT_RULES: dict[str, tuple[set[str], set[str]]] = {
    "PRODUCES": (
        _PROCESS_TYPES | _DATA_PRODUCT_TYPES,
        _DATA_PRODUCT_TYPES | _CONFIGURATION_TYPES,
    ),
    "CONSUMES": (
        _PROCESS_TYPES | _DATA_PRODUCT_TYPES,
        _DATA_PRODUCT_TYPES | _CONFIGURATION_TYPES | _PROCESS_TYPES,
    ),
    "PRODUCES_INPUT_FOR": (
        _DATA_PRODUCT_TYPES | _CONFIGURATION_TYPES | _PROCESS_TYPES,
        _PROCESS_TYPES,
    ),
    "IMPLEMENTS": (
        _PROCESS_TYPES | _CONCEPT_TYPES,
        _CONCEPT_TYPES | _PROCESS_TYPES,
    ),
    "FORMALIZES": (
        _DOCUMENT_TYPES | _CONCEPT_TYPES,
        _CONCEPT_TYPES | _PROCESS_TYPES,
    ),
    "IMPLEMENTED_AS_PIPELINE": (
        _CONCEPT_TYPES | _PROCESS_TYPES,
        _PROCESS_TYPES,
    ),
    "THEORETICAL_BASIS_FOR": (
        _DOCUMENT_TYPES | _CONCEPT_TYPES,
        _PROCESS_TYPES | _CONCEPT_TYPES,
    ),
    "PRODUCES_PROFILE_FOR": (
        _PROCESS_TYPES,
        _PROCESS_TYPES | _DATA_PRODUCT_TYPES,
    ),
    "PARAMETERIZES": (
        _CONFIGURATION_TYPES | _DATA_PRODUCT_TYPES,
        _PROCESS_TYPES,
    ),
    "CORRECTS": (
        _CONCEPT_TYPES | _PROCESS_TYPES,
        _DATA_PRODUCT_TYPES | _PROCESS_TYPES,
    ),
    "OPERATIONALLY_DOCUMENTS": (
        _DOCUMENT_TYPES,
        _PROCESS_TYPES | _REPOSITORY_TYPES | _DATA_PRODUCT_TYPES | _CONCEPT_TYPES,
    ),
    "FORKED_FROM": (
        _REPOSITORY_TYPES,
        _REPOSITORY_TYPES,
    ),
}

_CONTAINMENT_CHILD_TYPES = (
    _DATA_PRODUCT_TYPES | _PROCESS_TYPES | _CONCEPT_TYPES | _DOCUMENT_TYPES | _CONFIGURATION_TYPES | _REPOSITORY_TYPES
)
_CONTAINMENT_PARENT_TYPES = (
    _DATA_PRODUCT_TYPES | _PROCESS_TYPES | _CONCEPT_TYPES | _DOCUMENT_TYPES | _CONFIGURATION_TYPES | _REPOSITORY_TYPES
)


def _is_endpoint_compatible(predicate: str, subject_type: str, object_type: str) -> bool:
    rule = _PREDICATE_ENDPOINT_RULES.get(predicate)
    if not rule:
        return False
    subj_allowed, obj_allowed = rule
    return subject_type in subj_allowed and object_type in obj_allowed


def _is_containment_compatible(child_type: str, parent_type: str) -> bool:
    return child_type in _CONTAINMENT_CHILD_TYPES and parent_type in _CONTAINMENT_PARENT_TYPES


def _is_source_native_object(cand_obj: Mapping[str, Any]) -> bool:
    source_id = str(cand_obj.get("source_id", ""))
    obj_type = str(cand_obj.get("object_type", ""))
    if source_id == "curated_panda_domain":
        return False
    if obj_type in _FILE_LEVEL_TYPES:
        return True
    if obj_type in _CURATED_DOMAIN_TYPES:
        return False
    return True


class D3Arm(str, Enum):
    LEGACY = "LEGACY"
    ABLATION = "ABLATION"
    STRUCTURED = "STRUCTURED"  # historical synonym for STRUCTURED_UNBRIDGED
    STRUCTURED_UNBRIDGED = "STRUCTURED_UNBRIDGED"
    STRUCTURED_BRIDGED = "STRUCTURED_BRIDGED"


@dataclass(frozen=True)
class D3ExperimentConfig:
    """Small nonsemantic D3/D3.5 treatment configuration."""

    arm: D3Arm
    selected_rule_ids: tuple[str, ...] = SELECTED_D3_RULE_IDS
    structured_treatment_enabled: bool = False
    bridge_enabled: bool = False

    def __post_init__(self) -> None:
        arm = self.arm if isinstance(self.arm, D3Arm) else D3Arm(self.arm)
        object.__setattr__(self, "arm", arm)
        selected = tuple(self.selected_rule_ids)
        object.__setattr__(self, "selected_rule_ids", selected)
        if len(selected) != len(set(selected)):
            raise ValueError("D3 selected rule IDs must be unique")
        if set(selected) != set(SELECTED_D3_RULE_IDS):
            raise ValueError("D3 experimental modes must suppress exactly the frozen seven rules")
        expected_structured = arm in {
            D3Arm.STRUCTURED,
            D3Arm.STRUCTURED_UNBRIDGED,
            D3Arm.STRUCTURED_BRIDGED,
        }
        if self.structured_treatment_enabled is not expected_structured:
            raise ValueError(
                "D3 structured treatment must be enabled only for structured arms"
            )
        expected_bridged = arm is D3Arm.STRUCTURED_BRIDGED
        if self.bridge_enabled is not expected_bridged:
            raise ValueError(
                "D3 bridge must be enabled only for the STRUCTURED_BRIDGED arm"
            )

    @classmethod
    def for_arm(cls, arm: D3Arm | str) -> "D3ExperimentConfig":
        normalized = arm if isinstance(arm, D3Arm) else D3Arm(arm)
        is_structured = normalized in {
            D3Arm.STRUCTURED,
            D3Arm.STRUCTURED_UNBRIDGED,
            D3Arm.STRUCTURED_BRIDGED,
        }
        is_bridged = normalized is D3Arm.STRUCTURED_BRIDGED
        return cls(
            arm=normalized,
            structured_treatment_enabled=is_structured,
            bridge_enabled=is_bridged,
        )

    @property
    def selected_legacy_rules_suppressed(self) -> bool:
        return self.arm in {
            D3Arm.ABLATION,
            D3Arm.STRUCTURED,
            D3Arm.STRUCTURED_UNBRIDGED,
            D3Arm.STRUCTURED_BRIDGED,
        }


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
            "bridge_enabled": config.bridge_enabled,
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
                "structured_parent_traversal_count": 0,
                "structured_candidate_injection_count": 0,
                "bridged_candidate_injection_count": 0,
                "bridged_candidate_ranked_out_count": 0,
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

    def find_source_objects_by_path(
        self, source_id: str, path: str
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

    def find_source_objects_by_path(
        self, source_id: str, path: str
    ) -> list[dict[str, Any]]:
        with self.storage.connect() as connection:
            rows = connection.execute(
                f"SELECT {_OBJECT_COLUMNS} FROM knowledge_objects "
                "WHERE source_id=%s AND (locator->>'path'=%s OR canonical_locator=%s) "
                "ORDER BY object_id",
                (source_id, path, path),
            ).fetchall()
        columns = _OBJECT_COLUMNS.split(",")
        return [dict(zip(columns, row)) for row in rows]


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


@dataclass(frozen=True)
class StructuredReachabilityReceipt:
    reachability_receipt_id: str
    query_grounded_seed_mention: str
    D2_resolution_status: str
    seed_authority_tier: str
    seed_object_id: str
    root_seed_rank: int
    structural_path: dict[str, Any]
    budget_consumed: int
    budget_remaining: int
    reachability_status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "reachability_receipt_id": self.reachability_receipt_id,
            "query_grounded_seed_mention": self.query_grounded_seed_mention,
            "D2_resolution_status": self.D2_resolution_status,
            "seed_authority_tier": self.seed_authority_tier,
            "seed_object_id": self.seed_object_id,
            "root_seed_rank": self.root_seed_rank,
            "structural_path": self.structural_path,
            "budget_consumed": self.budget_consumed,
            "budget_remaining": self.budget_remaining,
            "reachability_status": self.reachability_status,
        }


@dataclass(frozen=True)
class StructuredEvidenceBridgeReceipt:
    bridge_receipt_id: str
    reachability_receipt_id: str
    evidence_provenance_origin_type: str
    evidence_provenance_origin_id: str
    evidence_field_used: str
    governance_review_status: str
    creation_or_review_metadata: dict[str, Any]
    lookup_source_ids: list[str]
    lookup_source_version_ids: list[str]
    lookup_locator: dict[str, Any] | str
    lookup_match_count: int
    source_native_candidate_object_id: str | None
    source_id: str | None
    source_version_id: str | None
    locator: dict[str, Any] | None
    object_type: str | None
    candidate_authority_role: str
    reason_included: str
    bridge_status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "bridge_receipt_id": self.bridge_receipt_id,
            "reachability_receipt_id": self.reachability_receipt_id,
            "evidence_provenance_origin_type": self.evidence_provenance_origin_type,
            "evidence_provenance_origin_id": self.evidence_provenance_origin_id,
            "evidence_field_used": self.evidence_field_used,
            "governance_review_status": self.governance_review_status,
            "creation_or_review_metadata": self.creation_or_review_metadata,
            "lookup_source_ids": self.lookup_source_ids,
            "lookup_source_version_ids": self.lookup_source_version_ids,
            "lookup_locator": self.lookup_locator,
            "lookup_match_count": self.lookup_match_count,
            "source_native_candidate_object_id": self.source_native_candidate_object_id,
            "source_id": self.source_id,
            "source_version_id": self.source_version_id,
            "locator": self.locator,
            "object_type": self.object_type,
            "candidate_authority_role": self.candidate_authority_role,
            "reason_included": self.reason_included,
            "bridge_status": self.bridge_status,
        }


@dataclass
class D3StructuredContribution:
    candidates: list[dict[str, Any]] = field(default_factory=list)
    bridged_candidates: list[dict[str, Any]] = field(default_factory=list)
    candidate_provenance: list[dict[str, Any]] = field(default_factory=list)
    reachability_receipts: list[dict[str, Any]] = field(default_factory=list)
    bridge_receipts: list[dict[str, Any]] = field(default_factory=list)
    displacement_diagnostics: dict[str, Any] = field(default_factory=dict)
    resolution_receipt: dict[str, Any] = field(default_factory=dict)
    diagnostic_counters: dict[str, Any] = field(default_factory=dict)
    excluded_resolution_reasons: list[dict[str, Any]] = field(default_factory=list)

    def compute_displacement_diagnostics(
        self,
        before_graph: Sequence[dict[str, Any]],
        after_graph: Sequence[dict[str, Any]],
        bridged_candidates: Sequence[dict[str, Any]],
    ) -> dict[str, Any]:
        before_ids = [item["object_id"] for item in before_graph]
        after_ids = [item["object_id"] for item in after_graph]
        bridged_ids = [item["object_id"] for item in bridged_candidates]
        displaced = [oid for oid in before_ids if oid not in after_ids and oid not in bridged_ids]
        dedup_overlap = len(set(bridged_ids).intersection(before_ids))
        self.displacement_diagnostics = {
            "bridged_candidate_count": len(bridged_candidates),
            "graph_candidates_before_bridge": len(before_graph),
            "graph_candidates_after_bridge": len(after_graph),
            "graph_candidates_displaced_by_prefix": len(displaced),
            "displaced_object_ids": displaced,
            "bridged_candidate_ids": bridged_ids,
            "deduplicated_overlap_count": dedup_overlap,
        }
        return self.displacement_diagnostics

    def as_dict(self) -> dict[str, Any]:
        return {
            "resolution_receipt": self.resolution_receipt,
            "structured_candidate_provenance": self.candidate_provenance,
            "reachability_receipts": self.reachability_receipts,
            "bridge_receipts": self.bridge_receipts,
            "displacement_diagnostics": self.displacement_diagnostics,
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
    """Derive seeds under frozen authority and atomic Tier-D ambiguity rules.

    Shared seed cap is 8. Independent Tier-G, Tier-S, and Tier-D-unique seeds
    are admitted first in authority order. Complete Tier-D ambiguity sets are
    then admitted atomically only if size <= 8 and fits the remaining seed
    budget; otherwise none from that branch are traversed and
    AMBIGUITY_SET_EXCEEDS_SAFE_SEED_BUDGET is emitted.
    """
    independent_seeds: dict[str, _Seed] = {}
    ambiguity_sets: list[tuple[str, str, list[_Seed]]] = []
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
                independent_seeds.setdefault(
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
            independent_seeds.setdefault(
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
            current_amb_seeds: list[_Seed] = []
            for candidate in candidates:
                object_id = str(candidate.get("object_id", ""))
                candidate_tier = str(candidate.get("tier", tier))
                if not object_id or candidate_tier != "D":
                    continue
                current_amb_seeds.append(
                    _Seed(
                        object_id=object_id,
                        mention_text=mention,
                        support_span=str(_field(resolution, "support_span", mention)),
                        resolution_status=status,
                        tier="D",
                        authority_class="NONAUTHORITATIVE_ADVISORY",
                        matched_object_id=None,
                        canonical_object_id=None,
                    )
                )
            if current_amb_seeds:
                ambiguity_sets.append((mention, str(_field(resolution, "support_span", mention)), current_amb_seeds))
            continue

        if status == UNRESOLVED:
            excluded.append({"mention": mention, "reason": "unresolved_no_negative_filter"})

    # Process independent seeds in authority order
    sorted_independent = sorted(
        independent_seeds.values(),
        key=lambda seed: (_TIER_PRIORITY.get(seed.tier, 99), seed.object_id),
    )
    admitted_seeds = sorted_independent[:SHARED_SEED_CAP]
    remaining_seed_budget = SHARED_SEED_CAP - len(admitted_seeds)

    # Process Tier-D ambiguity sets atomically
    final_seeds: dict[str, _Seed] = {seed.object_id: seed for seed in admitted_seeds}
    for mention, span, amb_seeds in ambiguity_sets:
        set_size = len(amb_seeds)
        if set_size <= SHARED_SEED_CAP and set_size <= remaining_seed_budget:
            for seed in amb_seeds:
                final_seeds.setdefault(seed.object_id, seed)
            remaining_seed_budget -= set_size
        else:
            excluded.append({
                "mention": mention,
                "reason": "AMBIGUITY_SET_EXCEEDS_SAFE_SEED_BUDGET",
                "diagnostic": "STRUCTURAL_PATH_AMBIGUOUS",
                "set_size": set_size,
                "remaining_budget": remaining_seed_budget,
            })

    return [final_seeds[key] for key in sorted(final_seeds)], excluded, statuses


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
        expected_version = f"{source_id}@{locked[source_id]}"
        actual_version = str(row.get("source_version_id", ""))
        return actual_version == expected_version or actual_version == str(locked[source_id])
    return True


def _normalize_evidence_path(raw_path: str) -> str | None:
    """Strict canonical repository-relative path normalization.

    Converts separators to '/', removes a single leading './', preserves case.
    Rejects absolute paths (starts with '/' or drive letter) and '..' traversal.
    """
    if not raw_path or not isinstance(raw_path, str):
        return None
    normalized = raw_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("/") or bool(re.match(r"^[A-Za-z]:", normalized)):
        return None  # Absolute path rejected
    if ".." in normalized.split("/"):
        return None  # Directory traversal rejected
    return normalized


def _validate_forked_from(
    edge: Mapping[str, Any],
    subject_row: Mapping[str, Any],
    object_row: Mapping[str, Any],
    plan_mapping: Mapping[str, Any],
    context_sources: Sequence[str],
) -> bool:
    """Exact explicit scope check for FORKED_FROM repository endpoints."""
    if not _object_in_scope(subject_row, plan_mapping, context_sources):
        return False
    if not _object_in_scope(object_row, plan_mapping, context_sources):
        return False

    targets = [str(v) for v in (plan_mapping.get("target_repositories") or []) if v]
    allowed_sources = set(targets) | {str(s) for s in context_sources if s}

    subj_src = str(subject_row.get("source_id", ""))
    obj_src = str(object_row.get("source_id", ""))

    if allowed_sources:
        subj_ok = subj_src in allowed_sources or any(t in str(subject_row.get("object_id", "")) for t in allowed_sources)
        obj_ok = obj_src in allowed_sources or any(t in str(object_row.get("object_id", "")) for t in allowed_sources)
        if not (subj_ok and obj_ok):
            return False

    edge_payload = edge.get("payload") or {}
    edge_versions = list(edge.get("source_version_ids") or edge_payload.get("source_version_ids") or [])
    resolved_versions = plan_mapping.get("resolved_versions", {}) or {}

    if resolved_versions and edge_versions:
        for repo, locked_ver in resolved_versions.items():
            if repo in allowed_sources:
                matching = [v for v in edge_versions if v == str(locked_ver) or v == f"{repo}@{locked_ver}"]
                if not matching and any(repo in v for v in edge_versions):
                    return False

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
    bridge_enabled: bool = False,
) -> D3StructuredContribution:
    """Build one bounded, additive, provenance-rich D3/D3.5 candidate stream."""

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
    candidate_provenance: dict[str, dict[str, Any]] = {}
    path_by_id: dict[str, list[dict[str, Any]]] = {}
    workflow_by_id: dict[str, dict[str, Any] | None] = {}
    root_seed_by_id: dict[str, str] = {}
    traversable: set[str] = set()

    reachability_receipts: list[dict[str, Any]] = []
    bridge_receipts: list[dict[str, Any]] = []
    bridged_candidates: dict[str, dict[str, Any]] = {}

    parent_traversals = 0
    relation_traversals = 0
    workflow_traversals = 0
    bridged_injections = 0
    bridged_ranked_out = 0

    def add_governed_candidate(
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
        candidate_provenance[object_id] = {
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

    # Materialize seeds as governed candidates
    for root_rank, object_id in enumerate(sorted(seed_rows)):
        seed = seed_by_id[object_id]
        add_governed_candidate(
            object_id,
            seed_rows[object_id],
            seed=seed,
            relation_path=[],
            workflow_step=None,
            reason="query-grounded D2 seed included without legacy shortcut payload",
        )
        if seed.allow_traversal:
            traversable.add(object_id)

    if not bridge_enabled:
        # Pre-D3.5 legacy/unbridged traversal path
        frontier = sorted(traversable)
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
                added = add_governed_candidate(
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

    else:
        # D3.5 Bounded Structured Evidence-Link Bridging
        # Mechanism A: Phased Typed Transition Budget per root-to-provenance path
        # Phase 1: Seed (up to 8)
        # Phase 2: Containment Context (0 or 1 upward child->parent per seed)
        # Phase 3: Semantic Reachability (0 or 1 accepted relation OR 1 curated workflow step per path)
        # Phase 4: Mechanism B Terminal Evidence Provenance Materialization

        reachable_structure_count = len(candidates)
        reachability_counter = 0
        bridge_counter = 0

        if not seed_rows:
            reachability_receipts.append(
                StructuredReachabilityReceipt(
                    reachability_receipt_id="reach_0001",
                    query_grounded_seed_mention="",
                    D2_resolution_status="UNRESOLVED",
                    seed_authority_tier="N",
                    seed_object_id="",
                    root_seed_rank=0,
                    structural_path={
                        "node_ids": [],
                        "transition_types": [],
                        "edge_ids": [],
                        "edge_predicates": [],
                        "directions": [],
                        "parent_transitions": [],
                        "workflow_ids": [],
                        "workflow_step_ids": [],
                    },
                    budget_consumed=0,
                    budget_remaining=MAX_NONTERMINAL_TRANSITIONS_PER_PATH,
                    reachability_status="NO_ELIGIBLE_STRUCTURED_SEED",
                ).as_dict()
            )

        for root_rank, root_seed_id in enumerate(sorted(seed_rows)):
            root_seed = seed_by_id[root_seed_id]
            if not root_seed.allow_traversal:
                continue

            seed_row = seed_rows[root_seed_id]
            seed_type = str(seed_row.get("object_type", ""))

            candidate_paths: list[dict[str, Any]] = []

            # 1. Base path: [root_seed_id]
            candidate_paths.append({
                "nodes": [(root_seed_id, seed_row)],
                "transition_types": ["SEED"],
                "edge_ids": [],
                "edge_predicates": [],
                "directions": [],
                "parent_transitions": [],
                "workflow_ids": [],
                "workflow_step_ids": [],
                "budget_consumed": 0,
                "provenance_origins": [("governed_object", root_seed_id, seed_row)],
                "target_node_id": None,
                "target_row": None,
                "target_reason": "",
                "relation_path": [],
                "workflow_step_receipt": None,
                "step_type": "BASE",
            })

            # Check upward parent containment
            metadata = seed_row.get("metadata") or {}
            parent_id = metadata.get("parent_object_id") or seed_row.get("parent_object_id")
            parent_row = None
            if parent_id:
                p_rows = graph_reader.load_objects([parent_id])
                if p_rows and _object_in_scope(p_rows[0], plan_mapping, context_sources):
                    cand_p_row = p_rows[0]
                    p_type = str(cand_p_row.get("object_type", ""))
                    if _is_containment_compatible(seed_type, p_type):
                        parent_row = cand_p_row
                        candidate_paths.append({
                            "nodes": [(root_seed_id, seed_row), (parent_id, parent_row)],
                            "transition_types": ["SEED", "CONTAINMENT_PARENT"],
                            "edge_ids": [],
                            "edge_predicates": [],
                            "directions": [],
                            "parent_transitions": [{"child_id": root_seed_id, "parent_id": parent_id}],
                            "workflow_ids": [],
                            "workflow_step_ids": [],
                            "budget_consumed": 1,
                            "provenance_origins": [("governed_object", parent_id, parent_row)],
                            "target_node_id": parent_id,
                            "target_row": parent_row,
                            "target_reason": "governed upward parent containment context",
                            "relation_path": [],
                            "workflow_step_receipt": None,
                            "step_type": "PARENT",
                        })

            # Origins for semantic transitions
            frontier_origins = [
                (root_seed_id, seed_row, [(root_seed_id, seed_row)], ["SEED"], [], 0)
            ]
            if parent_row is not None:
                frontier_origins.append(
                    (
                        parent_id,
                        parent_row,
                        [(root_seed_id, seed_row), (parent_id, parent_row)],
                        ["SEED", "CONTAINMENT_PARENT"],
                        [{"child_id": root_seed_id, "parent_id": parent_id}],
                        1,
                    )
                )

            for curr_id, curr_row, base_nodes, base_trans, base_parent_trans, base_budget in frontier_origins:
                curr_type = str(curr_row.get("object_type", ""))

                # Accepted relations
                raw_edges = graph_reader.load_accepted_relations([curr_id])
                sorted_edges = sorted(
                    raw_edges,
                    key=lambda e: (
                        str(e.get("subject_id", "")),
                        str(e.get("predicate", "")),
                        str(e.get("object_id", "")),
                        str(e.get("edge_id", "")),
                    ),
                )
                for edge in sorted_edges:
                    if edge.get("review_status") != "accepted":
                        continue
                    predicate = str(edge.get("predicate", ""))
                    if predicate not in _ALLOWED_PREDICATES:
                        continue
                    policy = _ALLOWED_PREDICATES[predicate]
                    subject = str(edge.get("subject_id", ""))
                    obj = str(edge.get("object_id", ""))

                    for origin_endpoint, neighbor_endpoint, direction in (
                        (subject, obj, "forward"),
                        (obj, subject, "reverse"),
                    ):
                        if origin_endpoint != curr_id or not neighbor_endpoint:
                            continue
                        if direction == "reverse" and not policy.get("reverse", False):
                            continue

                        neigh_rows = graph_reader.load_objects([neighbor_endpoint])
                        if not neigh_rows or not _object_in_scope(neigh_rows[0], plan_mapping, context_sources):
                            continue
                        neighbor_row = neigh_rows[0]
                        neighbor_type = str(neighbor_row.get("object_type", ""))

                        subj_t = curr_type if direction == "forward" else neighbor_type
                        obj_t = neighbor_type if direction == "forward" else curr_type
                        if not _is_endpoint_compatible(predicate, subj_t, obj_t):
                            continue

                        if predicate == "FORKED_FROM":
                            subj_r = curr_row if direction == "forward" else neighbor_row
                            obj_r = neighbor_row if direction == "forward" else curr_row
                            if not _validate_forked_from(edge, subj_r, obj_r, plan_mapping, context_sources):
                                continue

                        edge_id = str(edge.get("edge_id", f"edge_{len(candidate_paths)}"))
                        rel_path_item = [{
                            "edge_id": edge_id,
                            "predicate": predicate,
                            "subject_id": subject,
                            "object_id": obj,
                            "traversal_direction": direction,
                        }]

                        candidate_paths.append({
                            "nodes": [*base_nodes, (neighbor_endpoint, neighbor_row)],
                            "transition_types": [*base_trans, "ACCEPTED_RELATION"],
                            "edge_ids": [edge_id],
                            "edge_predicates": [predicate],
                            "directions": [direction],
                            "parent_transitions": list(base_parent_trans),
                            "workflow_ids": [],
                            "workflow_step_ids": [],
                            "budget_consumed": base_budget + 1,
                            "provenance_origins": [
                                ("relation_edge", edge_id, edge),
                                ("governed_object", neighbor_endpoint, neighbor_row),
                            ],
                            "target_node_id": neighbor_endpoint,
                            "target_row": neighbor_row,
                            "target_reason": "accepted D1 relation traversal",
                            "relation_path": rel_path_item,
                            "workflow_step_receipt": None,
                            "step_type": "RELATION",
                        })

                # Curated workflow steps
                raw_steps = graph_reader.load_curated_workflow_steps([curr_id])
                sorted_steps = sorted(
                    raw_steps,
                    key=lambda s: (str(s.get("workflow_id", "")), str(s.get("step_id", ""))),
                )
                for step in sorted_steps:
                    step_id = str(step.get("step_id", ""))
                    wf_id = str(step.get("workflow_id", ""))
                    participants = _workflow_participants(step)
                    step_receipt = {
                        "workflow_id": wf_id,
                        "step_id": step_id,
                        "name": step.get("name"),
                        "participants": participants,
                    }
                    for neighbor_endpoint in sorted(participants):
                        if neighbor_endpoint == curr_id:
                            continue
                        neigh_rows = graph_reader.load_objects([neighbor_endpoint])
                        if not neigh_rows or not _object_in_scope(neigh_rows[0], plan_mapping, context_sources):
                            continue
                        neighbor_row = neigh_rows[0]

                        candidate_paths.append({
                            "nodes": [*base_nodes, (neighbor_endpoint, neighbor_row)],
                            "transition_types": [*base_trans, "WORKFLOW_STEP"],
                            "edge_ids": [],
                            "edge_predicates": [],
                            "directions": [],
                            "parent_transitions": list(base_parent_trans),
                            "workflow_ids": [wf_id],
                            "workflow_step_ids": [step_id],
                            "budget_consumed": base_budget + 1,
                            "provenance_origins": [
                                ("workflow_step", step_id, step),
                                ("governed_object", neighbor_endpoint, neighbor_row),
                            ],
                            "target_node_id": neighbor_endpoint,
                            "target_row": neighbor_row,
                            "target_reason": "accepted curated workflow-step participant",
                            "relation_path": [],
                            "workflow_step_receipt": step_receipt,
                            "step_type": "WORKFLOW",
                        })

            # Process candidate paths deterministically
            for p in candidate_paths:
                target_id = p["target_node_id"]
                target_row = p["target_row"]
                budget_c = p["budget_consumed"]
                budget_rem = max(0, MAX_NONTERMINAL_TRANSITIONS_PER_PATH - budget_c)

                if target_id is not None and target_id not in candidates:
                    if reachable_structure_count >= GLOBAL_REACHABLE_STRUCTURE_CAP:
                        reachability_counter += 1
                        r_id = f"reach_{reachability_counter:04d}"
                        reachability_receipts.append(
                            StructuredReachabilityReceipt(
                                reachability_receipt_id=r_id,
                                query_grounded_seed_mention=root_seed.mention_text,
                                D2_resolution_status=root_seed.resolution_status,
                                seed_authority_tier=root_seed.tier,
                                seed_object_id=root_seed.object_id,
                                root_seed_rank=root_rank,
                                structural_path={
                                    "node_ids": [nid for nid, _ in p["nodes"]],
                                    "transition_types": p["transition_types"],
                                    "edge_ids": p["edge_ids"],
                                    "edge_predicates": p["edge_predicates"],
                                    "directions": p["directions"],
                                    "parent_transitions": p["parent_transitions"],
                                    "workflow_ids": p["workflow_ids"],
                                    "workflow_step_ids": p["workflow_step_ids"],
                                },
                                budget_consumed=budget_c,
                                budget_remaining=budget_rem,
                                reachability_status="TRAVERSAL_BUDGET_EXHAUSTED",
                            ).as_dict()
                        )
                        continue

                    added = add_governed_candidate(
                        target_id,
                        target_row,
                        seed=root_seed,
                        relation_path=p["relation_path"],
                        workflow_step=p["workflow_step_receipt"],
                        reason=p["target_reason"],
                    )
                    if added:
                        reachable_structure_count += 1
                        if p["step_type"] == "PARENT":
                            parent_traversals += 1
                        elif p["step_type"] == "RELATION":
                            relation_traversals += 1
                        elif p["step_type"] == "WORKFLOW":
                            workflow_traversals += 1

                reachability_counter += 1
                r_id = f"reach_{reachability_counter:04d}"
                reachability_receipts.append(
                    StructuredReachabilityReceipt(
                        reachability_receipt_id=r_id,
                        query_grounded_seed_mention=root_seed.mention_text,
                        D2_resolution_status=root_seed.resolution_status,
                        seed_authority_tier=root_seed.tier,
                        seed_object_id=root_seed.object_id,
                        root_seed_rank=root_rank,
                        structural_path={
                            "node_ids": [nid for nid, _ in p["nodes"]],
                            "transition_types": p["transition_types"],
                            "edge_ids": p["edge_ids"],
                            "edge_predicates": p["edge_predicates"],
                            "directions": p["directions"],
                            "parent_transitions": p["parent_transitions"],
                            "workflow_ids": p["workflow_ids"],
                            "workflow_step_ids": p["workflow_step_ids"],
                        },
                        budget_consumed=budget_c,
                        budget_remaining=budget_rem,
                        reachability_status="REACHED",
                    ).as_dict()
                )

                # Phase 4: Mechanism B Terminal Evidence Provenance Materialization
                origins_with_provenance = []
                for origin_type, origin_id, origin_record in p["provenance_origins"]:
                    payload = origin_record.get("payload") if origin_type in {"relation_edge", "workflow_step"} else origin_record.get("metadata") or {}
                    if not isinstance(payload, dict):
                        payload = {}
                    evidence_obj_ids = list(
                        origin_record.get("evidence_object_ids")
                        or payload.get("evidence_object_ids")
                        or []
                    )
                    evidence_paths = list(
                        origin_record.get("evidence_paths")
                        or payload.get("evidence_paths")
                        or []
                    )
                    if evidence_obj_ids or evidence_paths:
                        origins_with_provenance.append((origin_type, origin_id, origin_record, evidence_obj_ids, evidence_paths, payload))

                if not origins_with_provenance:
                    bridge_counter += 1
                    b_id = f"bridge_{bridge_counter:04d}"
                    bridge_receipts.append(
                        StructuredEvidenceBridgeReceipt(
                            bridge_receipt_id=b_id,
                            reachability_receipt_id=r_id,
                            evidence_provenance_origin_type=p["provenance_origins"][-1][0],
                            evidence_provenance_origin_id=p["provenance_origins"][-1][1],
                            evidence_field_used="none",
                            governance_review_status="accepted",
                            creation_or_review_metadata={},
                            lookup_source_ids=[],
                            lookup_source_version_ids=[],
                            lookup_locator={},
                            lookup_match_count=0,
                            source_native_candidate_object_id=None,
                            source_id=None,
                            source_version_id=None,
                            locator=None,
                            object_type=None,
                            candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                            reason_included=f"reached origin carries no evidence provenance",
                            bridge_status="GOVERNED_PROVENANCE_NOT_FOUND",
                        ).as_dict()
                    )
                    continue

                for origin_type, origin_id, origin_record, evidence_obj_ids, evidence_paths, payload in origins_with_provenance:
                    evidence_source_ids = list(
                        origin_record.get("evidence_source_ids")
                        or payload.get("evidence_source_ids")
                        or []
                    )
                    source_version_ids = list(
                        origin_record.get("source_version_ids")
                        or payload.get("source_version_ids")
                        or []
                    )
                    review_status = str(origin_record.get("review_status", "accepted"))
                    creation_metadata = {
                        "creation_method": origin_record.get("creation_method") or payload.get("creation_method", "curated"),
                        "evidence_note": origin_record.get("evidence_note") or payload.get("evidence_note", ""),
                    }

                    # Materialize evidence_object_ids
                    for target_obj_id in evidence_obj_ids:
                        bridge_counter += 1
                        b_id = f"bridge_{bridge_counter:04d}"
                        loaded = graph_reader.load_objects([target_obj_id])
                        if not loaded:
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_object_ids",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator={"object_id": target_obj_id},
                                    lookup_match_count=0,
                                    source_native_candidate_object_id=None,
                                    source_id=None,
                                    source_version_id=None,
                                    locator=None,
                                    object_type=None,
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included="evidence object not found in indexed corpus",
                                    bridge_status="PROVENANCE_SOURCE_OBJECT_NOT_FOUND",
                                ).as_dict()
                            )
                            continue

                        cand_obj = loaded[0]
                        if not _object_in_scope(cand_obj, plan_mapping, context_sources):
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_object_ids",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator={"object_id": target_obj_id},
                                    lookup_match_count=1,
                                    source_native_candidate_object_id=target_obj_id,
                                    source_id=cand_obj.get("source_id"),
                                    source_version_id=cand_obj.get("source_version_id"),
                                    locator=cand_obj.get("locator") or {},
                                    object_type=cand_obj.get("object_type"),
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included="evidence object conflicts with plan scope/version",
                                    bridge_status="VERSION_SCOPE_CONFLICT",
                                ).as_dict()
                            )
                            continue

                        if not _is_source_native_object(cand_obj):
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_object_ids",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator={"object_id": target_obj_id},
                                    lookup_match_count=1,
                                    source_native_candidate_object_id=None,
                                    source_id=cand_obj.get("source_id"),
                                    source_version_id=cand_obj.get("source_version_id"),
                                    locator=cand_obj.get("locator") or {},
                                    object_type=cand_obj.get("object_type"),
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included="curated domain semantic object rejected as bridged candidate (remains anchor only)",
                                    bridge_status="GOVERNED_PROVENANCE_INVALID",
                                ).as_dict()
                            )
                            continue

                        if target_obj_id in bridged_candidates:
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_object_ids",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator={"object_id": target_obj_id},
                                    lookup_match_count=1,
                                    source_native_candidate_object_id=target_obj_id,
                                    source_id=cand_obj.get("source_id"),
                                    source_version_id=cand_obj.get("source_version_id"),
                                    locator=cand_obj.get("locator") or {},
                                    object_type=cand_obj.get("object_type"),
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included=f"duplicate reference to already-injected candidate from {origin_type} {origin_id}",
                                    bridge_status="BRIDGED_CANDIDATE_INJECTED",
                                ).as_dict()
                            )
                            continue

                        if len(bridged_candidates) >= GLOBAL_BRIDGED_CANDIDATE_CAP:
                            bridged_ranked_out += 1
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_object_ids",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator={"object_id": target_obj_id},
                                    lookup_match_count=1,
                                    source_native_candidate_object_id=target_obj_id,
                                    source_id=cand_obj.get("source_id"),
                                    source_version_id=cand_obj.get("source_version_id"),
                                    locator=cand_obj.get("locator") or {},
                                    object_type=cand_obj.get("object_type"),
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included="bridged candidate cap reached (20)",
                                    bridge_status="BRIDGED_CANDIDATE_RANKED_OUT",
                                ).as_dict()
                            )
                            continue

                        bridged_candidates[target_obj_id] = cand_obj
                        bridged_injections += 1
                        bridge_receipts.append(
                            StructuredEvidenceBridgeReceipt(
                                bridge_receipt_id=b_id,
                                reachability_receipt_id=r_id,
                                evidence_provenance_origin_type=origin_type,
                                evidence_provenance_origin_id=origin_id,
                                evidence_field_used="evidence_object_ids",
                                governance_review_status=review_status,
                                creation_or_review_metadata=creation_metadata,
                                lookup_source_ids=evidence_source_ids,
                                lookup_source_version_ids=source_version_ids,
                                lookup_locator={"object_id": target_obj_id},
                                lookup_match_count=1,
                                source_native_candidate_object_id=target_obj_id,
                                source_id=cand_obj.get("source_id"),
                                source_version_id=cand_obj.get("source_version_id"),
                                locator=cand_obj.get("locator") or {},
                                object_type=cand_obj.get("object_type"),
                                candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                reason_included=f"governed evidence object materialized from {origin_type} {origin_id}",
                                bridge_status="BRIDGED_CANDIDATE_INJECTED",
                            ).as_dict()
                        )

                    # Materialize evidence_paths
                    for raw_path in evidence_paths:
                        bridge_counter += 1
                        b_id = f"bridge_{bridge_counter:04d}"
                        normalized_path = _normalize_evidence_path(raw_path)
                        if normalized_path is None:
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_paths",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator=raw_path,
                                    lookup_match_count=0,
                                    source_native_candidate_object_id=None,
                                    source_id=None,
                                    source_version_id=None,
                                    locator=None,
                                    object_type=None,
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included="invalid path format rejected by strict path contract",
                                    bridge_status="GOVERNED_PROVENANCE_INVALID",
                                ).as_dict()
                            )
                            continue

                        plan_targets = [str(v) for v in (plan_mapping.get("target_repositories") or []) if v]
                        allowed_sources = set(plan_targets) | {str(s) for s in context_sources if s}
                        if evidence_source_ids:
                            if allowed_sources:
                                candidate_sources = [s for s in evidence_source_ids if s in allowed_sources]
                                if not candidate_sources:
                                    bridge_receipts.append(
                                        StructuredEvidenceBridgeReceipt(
                                            bridge_receipt_id=b_id,
                                            reachability_receipt_id=r_id,
                                            evidence_provenance_origin_type=origin_type,
                                            evidence_provenance_origin_id=origin_id,
                                            evidence_field_used="evidence_paths",
                                            governance_review_status=review_status,
                                            creation_or_review_metadata=creation_metadata,
                                            lookup_source_ids=evidence_source_ids,
                                            lookup_source_version_ids=source_version_ids,
                                            lookup_locator=normalized_path,
                                            lookup_match_count=0,
                                            source_native_candidate_object_id=None,
                                            source_id=None,
                                            source_version_id=None,
                                            locator=None,
                                            object_type=None,
                                            candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                            reason_included="explicit evidence sources do not intersect plan/context scope",
                                            bridge_status="VERSION_SCOPE_CONFLICT",
                                        ).as_dict()
                                    )
                                    continue
                            else:
                                candidate_sources = list(evidence_source_ids)
                        else:
                            candidate_sources = list(allowed_sources) if allowed_sources else []

                        resolved_versions = plan_mapping.get("resolved_versions", {}) or {}
                        version_conflict = False
                        for src in candidate_sources:
                            if src in resolved_versions and source_version_ids:
                                exp_ver = str(resolved_versions[src])
                                if not any(v == exp_ver or v == f"{src}@{exp_ver}" for v in source_version_ids):
                                    if any(v.startswith(f"{src}@") for v in source_version_ids):
                                        version_conflict = True
                                        break

                        if version_conflict:
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_paths",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator=normalized_path,
                                    lookup_match_count=0,
                                    source_native_candidate_object_id=None,
                                    source_id=None,
                                    source_version_id=None,
                                    locator=None,
                                    object_type=None,
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included="explicit source_version_ids conflict with plan-locked versions",
                                    bridge_status="VERSION_SCOPE_CONFLICT",
                                ).as_dict()
                            )
                            continue

                        all_matches: list[dict[str, Any]] = []
                        for src in candidate_sources:
                            matches = graph_reader.find_source_objects_by_path(src, normalized_path)
                            for m in matches:
                                if _object_in_scope(m, plan_mapping, context_sources):
                                    if _is_source_native_object(m):
                                        all_matches.append(m)

                        non_derived = [
                            m for m in all_matches
                            if not (
                                str(m.get("object_type", "")).endswith("_chunk")
                                or (m.get("metadata") or {}).get("chunk_parent_id")
                            )
                        ]
                        file_level = [
                            m for m in non_derived
                            if str(m.get("object_type", "")) in _FILE_LEVEL_TYPES
                        ]
                        resolved_matches = file_level or non_derived or all_matches

                        if not resolved_matches:
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_paths",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator=normalized_path,
                                    lookup_match_count=0,
                                    source_native_candidate_object_id=None,
                                    source_id=None,
                                    source_version_id=None,
                                    locator=None,
                                    object_type=None,
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included="no matching source-native object found in indexed corpus",
                                    bridge_status="PROVENANCE_SOURCE_OBJECT_NOT_FOUND",
                                ).as_dict()
                            )
                            continue

                        if len(resolved_matches) > 1:
                            matched_ids = [str(m["object_id"]) for m in resolved_matches]
                            ambiguous_locator = {
                                "path": normalized_path,
                                "matched_object_ids": matched_ids,
                            }
                            creation_meta = {
                                **creation_metadata,
                                "matched_object_ids": matched_ids,
                            }
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_paths",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_meta,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator=ambiguous_locator,
                                    lookup_match_count=len(resolved_matches),
                                    source_native_candidate_object_id=None,
                                    source_id=None,
                                    source_version_id=None,
                                    locator=None,
                                    object_type=None,
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included=f"ambiguous path resolution ({len(resolved_matches)} matches: {', '.join(matched_ids)})",
                                    bridge_status="PROVENANCE_SOURCE_OBJECT_AMBIGUOUS",
                                ).as_dict()
                            )
                            continue

                        target_obj = resolved_matches[0]
                        target_id = str(target_obj["object_id"])

                        if target_id in bridged_candidates:
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_paths",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator=normalized_path,
                                    lookup_match_count=1,
                                    source_native_candidate_object_id=target_id,
                                    source_id=target_obj.get("source_id"),
                                    source_version_id=target_obj.get("source_version_id"),
                                    locator=target_obj.get("locator") or {},
                                    object_type=target_obj.get("object_type"),
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included=f"duplicate reference to already-injected candidate from {origin_type} {origin_id}",
                                    bridge_status="BRIDGED_CANDIDATE_INJECTED",
                                ).as_dict()
                            )
                            continue

                        if len(bridged_candidates) >= GLOBAL_BRIDGED_CANDIDATE_CAP:
                            bridged_ranked_out += 1
                            bridge_receipts.append(
                                StructuredEvidenceBridgeReceipt(
                                    bridge_receipt_id=b_id,
                                    reachability_receipt_id=r_id,
                                    evidence_provenance_origin_type=origin_type,
                                    evidence_provenance_origin_id=origin_id,
                                    evidence_field_used="evidence_paths",
                                    governance_review_status=review_status,
                                    creation_or_review_metadata=creation_metadata,
                                    lookup_source_ids=evidence_source_ids,
                                    lookup_source_version_ids=source_version_ids,
                                    lookup_locator=normalized_path,
                                    lookup_match_count=1,
                                    source_native_candidate_object_id=target_id,
                                    source_id=target_obj.get("source_id"),
                                    source_version_id=target_obj.get("source_version_id"),
                                    locator=target_obj.get("locator") or {},
                                    object_type=target_obj.get("object_type"),
                                    candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                    reason_included="bridged candidate cap reached (20)",
                                    bridge_status="BRIDGED_CANDIDATE_RANKED_OUT",
                                ).as_dict()
                            )
                            continue

                        bridged_candidates[target_id] = target_obj
                        bridged_injections += 1
                        bridge_receipts.append(
                            StructuredEvidenceBridgeReceipt(
                                bridge_receipt_id=b_id,
                                reachability_receipt_id=r_id,
                                evidence_provenance_origin_type=origin_type,
                                evidence_provenance_origin_id=origin_id,
                                evidence_field_used="evidence_paths",
                                governance_review_status=review_status,
                                creation_or_review_metadata=creation_metadata,
                                lookup_source_ids=evidence_source_ids,
                                lookup_source_version_ids=source_version_ids,
                                lookup_locator=normalized_path,
                                lookup_match_count=1,
                                source_native_candidate_object_id=target_id,
                                source_id=target_obj.get("source_id"),
                                source_version_id=target_obj.get("source_version_id"),
                                locator=target_obj.get("locator") or {},
                                object_type=target_obj.get("object_type"),
                                candidate_authority_role="GOVERNED_PROVENANCE_BACKED_ADDITIVE_RETRIEVAL_CANDIDATE",
                                reason_included=f"exact path resolution from {origin_type} {origin_id}",
                                bridge_status="BRIDGED_CANDIDATE_INJECTED",
                            ).as_dict()
                        )

    counters = {
        "structured_resolution_attempt_count": 1,
        "structured_resolution_status_counts": dict(sorted(statuses.items())),
        "structured_resolution_hit_count": sum(
            1 for seed in seeds if seed.object_id in seed_rows
        ),
        "structured_seed_count": len(seed_rows),
        "structured_relation_traversal_count": relation_traversals,
        "structured_workflow_traversal_count": workflow_traversals,
        "structured_parent_traversal_count": parent_traversals,
        "structured_candidate_injection_count": len(candidates),
        "bridged_candidate_injection_count": len(bridged_candidates),
        "bridged_candidate_ranked_out_count": bridged_ranked_out,
        "migration_specific_direct_answer_location_injection_count": 0,
        "prohibited_fallback_use_count": 0,
        "evaluation_metadata_runtime_use_count": 0,
        "selected_legacy_payload_reuse_count": 0,
        "same_as_activation_count": 0,
    }
    return D3StructuredContribution(
        candidates=list(candidates.values()),
        bridged_candidates=list(bridged_candidates.values()),
        candidate_provenance=list(candidate_provenance.values()),
        reachability_receipts=reachability_receipts,
        bridge_receipts=bridge_receipts,
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
    bridge_enabled: bool = False,
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
        bridge_enabled=bridge_enabled,
    )


__all__ = [
    "SELECTED_D3_RULE_IDS",
    "D3Arm",
    "D3ExperimentConfig",
    "D3ExpansionDecision",
    "StructuredReachabilityReceipt",
    "StructuredEvidenceBridgeReceipt",
    "D3StructuredContribution",
    "D3StructuredGraphReader",
    "PostgresD3StructuredGraphReader",
    "select_matching_query_expansions",
    "build_structured_contribution",
    "build_structured_contribution_from_storage",
]
