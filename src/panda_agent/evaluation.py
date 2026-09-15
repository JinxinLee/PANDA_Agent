"""Crash-safe, resumable evaluation result storage."""

from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from typing import Any, Literal

import yaml
from pydantic import Field, field_validator, model_validator

from panda_agent.evaluation_finalization import (
    RETRY_CATEGORY_TRANSPORT_PROVIDER,
    RETRY_CATEGORY_UNPARSABLE_RESPONSE,
    classify_evaluation_exception,
    evaluate_cohort_decision,
    evaluation_record_state,
)
from panda_agent.models import QAStatus, StrictModel
from panda_agent.source import sha256_file


INTENTS = {
    "installation",
    "usage",
    "api",
    "algorithm_theory",
    "algorithm_implementation",
    "data_flow",
    "module_structure",
    "troubleshooting",
}
EXPECTED_INTENT_COUNTS = {
    "installation": 12,
    "usage": 14,
    "api": 16,
    "algorithm_theory": 16,
    "algorithm_implementation": 20,
    "data_flow": 18,
    "module_structure": 12,
    "troubleshooting": 12,
}
# Legacy v1 draft-contract counts.  Reviewed benchmark v2 supplies its own
# ``expected_split_counts`` in YAML and is validated from that manifest; these
# constants are retained only so the archived ``m6-draft-1`` schema remains
# reproducible and cannot silently redefine v2 acceptance semantics.
EXPECTED_SPLIT_COUNTS = {"dev": 80, "acceptance": 40}
EXPECTED_INTENT_SPLIT_COUNTS = {
    ("installation", "dev"): 8,
    ("installation", "acceptance"): 4,
    ("usage", "dev"): 9,
    ("usage", "acceptance"): 5,
    ("api", "dev"): 11,
    ("api", "acceptance"): 5,
    ("algorithm_theory", "dev"): 11,
    ("algorithm_theory", "acceptance"): 5,
    ("algorithm_implementation", "dev"): 13,
    ("algorithm_implementation", "acceptance"): 7,
    ("data_flow", "dev"): 12,
    ("data_flow", "acceptance"): 6,
    ("module_structure", "dev"): 8,
    ("module_structure", "acceptance"): 4,
    ("troubleshooting", "dev"): 8,
    ("troubleshooting", "acceptance"): 4,
}
EXPECTED_LANGUAGE_COUNTS = {"en": 60, "zh": 40, "mixed": 20}
EXPECTED_STATUS_COUNTS = {
    QAStatus.ANSWERED.value: 102,
    QAStatus.INSUFFICIENT_EVIDENCE.value: 10,
    QAStatus.VERSION_CONFLICT.value: 8,
}


IdentifierKind = Literal[
    "code_symbol",
    "path",
    "glob",
    "type_expression",
    "root_branch",
    "shell_pattern",
    "regex",
]

_PATH_INDEX_CACHE: dict[int, tuple[dict[str, dict[str, Any]], dict[tuple[str, str, str], list[dict[str, Any]]]]] = {}
_IDENTIFIER_CATALOG_CACHE: dict[tuple[int, tuple[str, ...]], dict[str, set[str]]] = {}


def classify_identifier_mention(token: str) -> tuple[IdentifierKind | None, str]:
    """Classify a code-like token before deciding whether it can hallucinate.

    Globs, regular expressions, pointer/reference syntax, and shell patterns are
    valid technical notation.  They are reported separately and are not treated
    as invented API identifiers merely because the literal decorated form is
    absent from a source excerpt.
    """
    raw = token.strip().rstrip(".,;:)")
    if not raw:
        return None, raw
    if ".*" in raw:
        return "regex", raw
    if any(char in raw for char in ("*", "?", "[", "]")):
        if raw.endswith((".root", ".txt", ".json", ".C", ".py")) or "/" in raw:
            return "glob", raw
        if raw.startswith("Pnd") and raw.endswith("*"):
            return "type_expression", raw[:-1]
        return "shell_pattern", raw
    if raw.startswith("const ") or raw.endswith(("&", "*")):
        normalized = raw.removeprefix("const ").rstrip("&*").strip()
        return "type_expression", normalized
    path_prefixes = (
        "macro/",
        "src/",
        "data/",
        "docs/",
        "doc/",
        "model/",
        "fit/",
        "pgenerators/",
        "pid/",
        "tools/",
        "apps/",
        "ui/",
    )
    if raw.startswith(path_prefixes) or raw.endswith(
        (".C", ".py", ".root", ".h", ".hpp", ".cpp", ".cxx", ".json", ".txt", ".yaml", ".yml")
    ):
        return "path", raw
    if "::" in raw or (raw.startswith("Pnd") and len(raw) > 3):
        return "code_symbol", raw
    return None, raw


def _looks_like_identifier(token: str) -> bool:
    kind, _ = classify_identifier_mention(token)
    return kind in {"code_symbol", "path"}


def _required_identifier_present(identifier: str, answer: str) -> bool:
    """Match exact code identifiers and a small set of reviewed concept aliases."""
    if identifier in answer:
        return True
    if identifier == "DPMGenerator":
        normalized = answer.casefold()
        return "dpm" in normalized and "generator" in normalized
    return False


class GoldEvidenceSelector(StrictModel):
    object_id: str | None = None
    source_id: str | None = None
    source_version_id: str | None = None
    object_type: str | None = None
    path: str | None = None
    symbol: str | None = None
    start_line: int | None = Field(default=None, ge=1)
    end_line: int | None = Field(default=None, ge=1)
    pdf_page: int | None = Field(default=None, ge=1)
    pdf_page_end: int | None = Field(default=None, ge=1)
    title_contains: str | None = None
    section_contains: str | None = None

    @model_validator(mode="after")
    def require_selector(self) -> "GoldEvidenceSelector":
        if not any(
            (
                self.object_id,
                self.source_id,
                self.source_version_id,
                self.object_type,
                self.path,
                self.symbol,
                self.start_line,
                self.end_line,
                self.pdf_page,
                self.pdf_page_end,
                self.title_contains,
                self.section_contains,
            )
        ):
            raise ValueError("gold evidence selector cannot be empty")
        if self.start_line and self.end_line and self.end_line < self.start_line:
            raise ValueError("selector end_line must be >= start_line")
        if self.pdf_page and self.pdf_page_end and self.pdf_page_end < self.pdf_page:
            raise ValueError("selector pdf_page_end must be >= pdf_page")
        return self

    def matches(self, item: dict[str, Any]) -> bool:
        locator = item.get("locator") or {}
        item_start = locator.get("start_line")
        item_end = locator.get("end_line")
        line_overlap = True
        if self.start_line is not None:
            selector_end = self.end_line or self.start_line
            line_overlap = bool(
                item_start
                and item_end
                and int(item_start) <= selector_end
                and int(item_end) >= self.start_line
            )
        page_match = True
        if self.pdf_page is not None:
            page = locator.get("pdf_page")
            page_match = bool(page and self.pdf_page <= int(page) <= (self.pdf_page_end or self.pdf_page))
        section_text = " / ".join(locator.get("section_path") or [])
        checks = (
            self.object_id is None or item.get("object_id") == self.object_id,
            self.source_id is None or item.get("source_id") == self.source_id,
            self.source_version_id is None
            or item.get("source_version_id") == self.source_version_id,
            self.object_type is None or item.get("object_type") == self.object_type,
            self.path is None or (locator.get("path") or "").replace("\\", "/") == self.path,
            self.symbol is None or locator.get("symbol") == self.symbol,
            line_overlap,
            page_match,
            self.title_contains is None
            or self.title_contains.casefold()
            in " ".join(
                [
                    item.get("title") or "",
                    *[str(value) for value in (locator.get("section_path") or [])],
                    item.get("text") or "",
                ]
            ).casefold(),
            self.section_contains is None
            or self.section_contains.casefold() in section_text.casefold(),
        )
        return all(checks)


class GoldEvidenceGroup(StrictModel):
    group_id: str
    role: str | None = None
    critical: bool = True
    any_of: list[GoldEvidenceSelector] = Field(min_length=1)


class GoldAnswerPoint(StrictModel):
    point_id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]*$")
    text: str = Field(min_length=3)
    weight: float = Field(default=1.0, gt=0)
    critical: bool = True


class GoldIdentifierRequirement(StrictModel):
    text: str = Field(min_length=1)
    kind: IdentifierKind = "code_symbol"
    critical: bool = True


class GoldQuestion(StrictModel):
    id: str = Field(pattern=r"^[gn]\d{3}$")
    split: Literal[
        "dev",
        "challenge",
        "regression",
        "acceptance",
        "novel_dev",
        "novel_validation",
        "novel_holdout",
    ]
    language: Literal["en", "zh", "mixed"]
    intent: str
    accepted_intents: list[str] = Field(default_factory=list)
    query: str = Field(min_length=3, max_length=20_000)
    expected_status: QAStatus
    allowed_source_versions: list[str] = Field(min_length=1)
    required_evidence_groups: list[GoldEvidenceGroup] = Field(min_length=1)
    required_source_types: list[str] = Field(default_factory=list)
    required_answer_points: list[GoldAnswerPoint] = Field(min_length=1)
    required_identifiers: list[GoldIdentifierRequirement] = Field(default_factory=list)
    forbidden_evidence: list[GoldEvidenceSelector] = Field(default_factory=list)
    concept_scopes: dict[str, str] = Field(default_factory=dict)
    cluster_id: str | None = None
    challenge_tags: list[str] = Field(default_factory=list)
    review_status: Literal["draft", "approved", "rejected"] = "draft"
    reviewer: str | None = None
    reviewed_at: datetime | None = None

    @field_validator("required_answer_points", mode="before")
    @classmethod
    def normalize_answer_points(cls, value: Any) -> Any:
        return [
            {"point_id": f"p{index}", "text": item, "weight": 1.0, "critical": True}
            if isinstance(item, str)
            else item
            for index, item in enumerate(value or [], 1)
        ]

    @field_validator("required_identifiers", mode="before")
    @classmethod
    def normalize_identifiers(cls, value: Any) -> Any:
        return [
            {"text": item, "kind": classify_identifier_mention(item)[0] or "code_symbol", "critical": True}
            if isinstance(item, str)
            else item
            for item in (value or [])
        ]

    @model_validator(mode="after")
    def validate_review(self) -> "GoldQuestion":
        if self.intent not in INTENTS:
            raise ValueError(f"unsupported intent: {self.intent}")
        if any(value not in INTENTS for value in self.accepted_intents):
            raise ValueError(
                f"unsupported accepted intents: {sorted(set(self.accepted_intents) - INTENTS)}"
            )
        if len(self.accepted_intents) != len(set(self.accepted_intents)):
            raise ValueError("accepted intents must be unique")
        if self.intent in self.accepted_intents:
            raise ValueError("accepted intents must not repeat the primary intent")
        allowed_source_types = {
            "paper",
            "documentation",
            "readme",
            "code",
            "workflow",
            "graph",
        }
        unknown_source_types = set(self.required_source_types) - allowed_source_types
        if unknown_source_types:
            raise ValueError(
                f"unsupported required source types: {sorted(unknown_source_types)}"
            )
        if len(self.allowed_source_versions) != len(set(self.allowed_source_versions)):
            raise ValueError("allowed source versions must be unique")
        group_ids = [item.group_id for item in self.required_evidence_groups]
        if len(group_ids) != len(set(group_ids)):
            raise ValueError("gold evidence group IDs must be unique within a question")
        point_ids = [item.point_id for item in self.required_answer_points]
        if len(point_ids) != len(set(point_ids)):
            raise ValueError("answer point IDs must be unique within a question")
        if self.review_status == "approved" and not (self.reviewer and self.reviewed_at):
            raise ValueError("approved gold questions require reviewer and reviewed_at")
        return self


class GoldDataset(StrictModel):
    schema_version: str
    benchmark_version: str
    questions: list[GoldQuestion] = Field(min_length=1)
    release_eligible: bool = True
    acceptance_exposed: bool = False
    expected_split_counts: dict[str, int] = Field(default_factory=dict)
    expected_status_counts: dict[str, int] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_distribution(self) -> "GoldDataset":
        ids = [item.id for item in self.questions]
        if len(ids) != len(set(ids)):
            raise ValueError("gold question IDs must be unique")
        if self.benchmark_version == "m6-draft-1":
            expected_ids = {f"g{index:03d}" for index in range(1, 121)}
            if set(ids) != expected_ids:
                raise ValueError("gold question IDs must be exactly g001 through g120")
        else:
            cluster_splits: dict[str, set[str]] = defaultdict(set)
            for item in self.questions:
                if item.cluster_id:
                    cluster_splits[item.cluster_id].add(item.split)
            leaked = sorted(key for key, splits in cluster_splits.items() if len(splits) > 1)
            if leaked:
                raise ValueError(f"knowledge clusters cross benchmark splits: {leaked[:20]}")
            if self.expected_split_counts:
                actual_splits = dict(Counter(item.split for item in self.questions))
                if actual_splits != self.expected_split_counts:
                    raise ValueError(
                        f"invalid split distribution: {actual_splits} != {self.expected_split_counts}"
                    )
            if self.expected_status_counts:
                actual_status = dict(Counter(item.expected_status.value for item in self.questions))
                if actual_status != self.expected_status_counts:
                    raise ValueError(
                        f"invalid status distribution: {actual_status} != {self.expected_status_counts}"
                    )
            return self
        checks = {
            "intent": (Counter(item.intent for item in self.questions), EXPECTED_INTENT_COUNTS),
            "split": (Counter(item.split for item in self.questions), EXPECTED_SPLIT_COUNTS),
            "intent_split": (
                Counter((item.intent, item.split) for item in self.questions),
                EXPECTED_INTENT_SPLIT_COUNTS,
            ),
            "language": (Counter(item.language for item in self.questions), EXPECTED_LANGUAGE_COUNTS),
            "status": (
                Counter(item.expected_status.value for item in self.questions),
                EXPECTED_STATUS_COUNTS,
            ),
        }
        for label, (actual, expected) in checks.items():
            if dict(actual) != expected:
                raise ValueError(f"invalid {label} distribution: {dict(actual)} != {expected}")
        return self

    def require_approved(self, split: str | None = None) -> None:
        pending = [
            item.id
            for item in self.questions
            if (split is None or item.split == split) and item.review_status != "approved"
        ]
        if pending:
            raise ValueError(f"gold questions require human approval: {pending[:20]}")


# Closed RC3e v2.5 contract: these are not a general-purpose gate override.
_V25_SIGNED_ADJUDICATIONS: dict[str, dict[str, Any]] = {
    "g001": {"type": "answer_point_and_provenance", "metric_overrides": {"unsupported_claim_ids": [], "major_unsupported_claim_ids": [], "minor_unsupported_claim_ids": []}},
    "g005": {"type": "answer_point", "metric_overrides": {}},
    "g007": {"type": "refusal_citation_waiver", "waiver_id": "rc3e-g007-accepted-diagnostic", "waive_metrics": ["refusal_evidence_recall"], "metric_overrides": {}},
    "g011": {"type": "final_evidence_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0}},
    "g028": {"type": "answer_point", "metric_overrides": {}},
    "g060": {"type": "final_evidence_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0}},
    "g068": {"type": "final_evidence_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0}},
    "g073": {"type": "final_evidence_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0}},
    "g079": {"type": "final_evidence_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0}},
    "g081": {"type": "final_evidence_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0}},
    "g089": {"type": "final_evidence_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True}},
    "g105": {"type": "identifier_path_normalization_waiver", "waiver_id": "rc3e-g105-accepted-diagnostic", "metric_overrides": {"hallucinated_identifiers": [], "major_identifier_hallucinations": []}},
}
_V25_SOURCE_REVIEW_SHA256 = "6124C6937F72FA085C42815B60309B2B20F631E461B4DDFF5BF83514FAB6A999"

# Closed RC3f regression-review contract.  It extends, rather than rewrites,
# the signed v2.5 Dev adjudications and deliberately excludes the three real
# regression failures (g087, g097, and g116).
_V26_SIGNED_ADJUDICATIONS: dict[str, dict[str, Any]] = {
    **_V25_SIGNED_ADJUDICATIONS,
    "g090": {"type": "final_evidence_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0}},
    "g092": {"type": "workflow_document_equivalence", "metric_overrides": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True}},
    "g093": {"type": "code_dataflow_equivalence", "metric_overrides": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True}},
    "g094": {"type": "intent_and_evidence_equivalence", "metric_overrides": {"intent_correct": True, "gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True}},
    "g099": {"type": "source_entity_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True}},
    "g100": {"type": "workflow_object_equivalence", "metric_overrides": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True}},
    "g101": {"type": "answer_point_and_evidence", "covered_point_ids": ["p1", "p2"], "critical_answer_points_missing": [], "metric_overrides": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0}},
    "g103": {"type": "workflow_object_equivalence", "metric_overrides": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True}},
    "g104": {"type": "final_evidence_equivalence", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True}},
    "g106": {"type": "answer_point_and_evidence", "covered_point_ids": ["p1", "p2", "p3"], "critical_answer_points_missing": [], "metric_overrides": {"gold_recall_at_10": 1.0, "final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "required_source_coverage": True}},
    "g109": {"type": "relative_path_shorthand_waiver", "waiver_id": "rc3f-g109-relative-path-shorthand", "metric_overrides": {"final_evidence_recall": 1.0, "critical_final_evidence_recall": 1.0, "hallucinated_identifiers": [], "major_identifier_hallucinations": []}},
}
_V26_SOURCE_REVIEW_SHA256 = "5A42E46CCE0E7AB3E0E84DAF11B5F664DF3266206A7797FBDF158E93B7D59B43"


def validate_v25_adjudication_document(
    benchmark_version: str, payload: dict[str, Any]
) -> None:
    """Fail closed unless the complete signed review overlay is present."""
    if benchmark_version not in {"m6-benchmark-v2.5", "m6-benchmark-v2.6"}:
        return
    revision = "2.6" if benchmark_version.endswith("2.6") else "2.5"
    contract = _V26_SIGNED_ADJUDICATIONS if revision == "2.6" else _V25_SIGNED_ADJUDICATIONS
    if payload.get("schema_version") != revision:
        raise ValueError(f"v{revision} adjudication schema_version must be {revision}")
    if revision == "2.6":
        source_hashes = {
            str(item.get("sha256") or "")
            for item in payload.get("source_reviews", [])
        }
        if source_hashes != {_V25_SOURCE_REVIEW_SHA256, _V26_SOURCE_REVIEW_SHA256}:
            raise ValueError("v2.6 adjudication source review hashes are not authorized")
    elif payload.get("source_review_sha256") != _V25_SOURCE_REVIEW_SHA256:
        raise ValueError("v2.5 adjudication source review hash is not authorized")
    case_ids = [str(item.get("case_id", "")) for item in payload.get("adjudications", [])]
    if len(case_ids) != len(set(case_ids)) or set(case_ids) != set(contract):
        raise ValueError(f"v{revision} adjudication cases must exactly match the signed contract")


def apply_signed_rescore_adjudication(
    benchmark_version: str,
    case: GoldQuestion,
    metrics: dict[str, Any],
    adjudication: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Apply answer-point adjudications plus the closed signed v2.5 contract."""
    updated = dict(metrics)
    applied: list[str] = []
    points = {item.point_id: item for item in case.required_answer_points}
    covered = [value for value in adjudication.get("covered_point_ids", []) if value in points]
    if covered or "critical_answer_points_missing" in adjudication:
        total = sum(point.weight for point in points.values())
        updated.update({
            "answer_point_coverage": sum(points[value].weight for value in covered) / total if total else 1.0,
            "covered_point_ids": covered,
            "critical_answer_points_missing": list(adjudication.get("critical_answer_points_missing", [])),
        })
        applied.extend(["answer_point_coverage", "covered_point_ids", "critical_answer_points_missing"])
    if benchmark_version not in {"m6-benchmark-v2.5", "m6-benchmark-v2.6"}:
        return updated, applied
    revision = "2.6" if benchmark_version.endswith("2.6") else "2.5"
    contracts = _V26_SIGNED_ADJUDICATIONS if revision == "2.6" else _V25_SIGNED_ADJUDICATIONS
    contract = contracts.get(case.id)
    if contract is None or adjudication.get("type") != contract["type"]:
        raise ValueError(f"v{revision} adjudication is not authorized for {case.id}")
    if adjudication.get("metric_overrides", {}) != contract["metric_overrides"]:
        raise ValueError(f"v{revision} metric overrides are not authorized for {case.id}")
    for field in ("covered_point_ids", "critical_answer_points_missing"):
        if field in contract and adjudication.get(field) != contract[field]:
            raise ValueError(f"v{revision} {field} is not authorized for {case.id}")
    if contract.get("waiver_id") and adjudication.get("waiver_id") != contract["waiver_id"]:
        raise ValueError(f"v{revision} waiver ID is not authorized for {case.id}")
    if contract.get("waive_metrics") and adjudication.get("waive_metrics") != contract["waive_metrics"]:
        raise ValueError(f"v{revision} waived metrics are not authorized for {case.id}")
    updated.update(contract["metric_overrides"])
    applied.extend(contract["metric_overrides"])
    for field in contract.get("waive_metrics", []):
        applicability = dict(updated.get("metric_applicability") or {})
        denominators = dict(updated.get("metric_denominators") or {})
        updated[field] = None
        applicability[field] = False
        denominators[field] = 0
        updated["metric_applicability"] = applicability
        updated["metric_denominators"] = denominators
        applied.extend([field, "metric_applicability", "metric_denominators"])
    return updated, sorted(set(applied))


def load_gold_dataset(path: Path) -> GoldDataset:
    return GoldDataset.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def ranked_object_ids(bundle: dict[str, Any], limit: int = 10) -> list[str]:
    if bundle.get("ranked_object_ids"):
        return list(dict.fromkeys(bundle["ranked_object_ids"]))[:limit]
    return list(
        dict.fromkeys(
            [
                *bundle.get("reranked_object_ids", []),
                *bundle.get("fusion_scores", {}).keys(),
            ]
        )
    )[:limit]


def stage_trace_for_object(
    diagnostics: dict[str, Any],
    result: dict[str, Any],
    object_id: str,
    *,
    fused_candidates: list[Any] | None = None,
) -> dict[str, Any]:
    """Return explicit stage positions for one object from an immutable trace.

    Stages are intentionally distinct:
      - combined/fused candidate pool: union of channel rankings;
      - fused order: only an authoritative frozen ordered ``fused_candidates``
        list may provide fused rank; persisted ``fusion_scores`` dict key order
        is NOT valid historical rank after key-sorted serialization;
      - LLM reranker order: ``reranked_object_ids``;
      - final deterministic ranked order: ``ranked_object_ids`` (the same
        stage the evaluator uses for Recall@K);
      - final evidence selection: ``result.evidence`` object IDs.
    """
    rankings = diagnostics.get("rankings") or {}
    combined_candidate_ids = list(
        dict.fromkeys(
            object_id
            for object_ids in rankings.values()
            for object_id in object_ids
        )
    )
    fused_ids: list[str] = []
    fused_rank_source = "unavailable"
    if fused_candidates is not None:
        fused_ids = [
            str(candidate.get("object_id") if isinstance(candidate, dict) else candidate.object_id)
            for candidate in fused_candidates
        ]
        fused_rank_source = "retrieval_trace_fused_candidates"
    reranked_ids = diagnostics.get("reranked_object_ids") or []
    final_ranked_ids = diagnostics.get("ranked_object_ids") or []
    final_evidence_ids = [
        item.get("object_id")
        for item in (result.get("evidence") or [])
        if item.get("object_id")
    ]

    def index_of(values: list[str]) -> int | None:
        try:
            return values.index(object_id)
        except ValueError:
            return None

    fused_idx = index_of(fused_ids)
    reranked_idx = index_of(reranked_ids)
    final_ranked_idx = index_of(final_ranked_ids)
    final_ranked_rank = None if final_ranked_idx is None else final_ranked_idx + 1
    return {
        "object_id": object_id,
        "combined_candidate_present": object_id in combined_candidate_ids,
        "fused_rank_1based": None if fused_idx is None else fused_idx + 1,
        "fused_rank_source": fused_rank_source,
        "reranker_index_0based": reranked_idx,
        "reranker_rank_1based": None if reranked_idx is None else reranked_idx + 1,
        "final_ranked_index_0based": final_ranked_idx,
        "final_ranked_rank_1based": final_ranked_rank,
        "final_top5": final_ranked_rank is not None and final_ranked_rank <= 5,
        "final_top10": final_ranked_rank is not None and final_ranked_rank <= 10,
        "final_top20": final_ranked_rank is not None and final_ranked_rank <= 20,
        "final_selected": object_id in final_evidence_ids,
    }


def _lineage(
    item: dict[str, Any], object_lookup: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    values = [item]
    seen = {item.get("object_id")}
    current = item
    while True:
        locator = current.get("locator") or {}
        parent_id = (
            current.get("parent_object_id")
            or current.get("chunk_parent_id")
            or locator.get("parent_object_id")
            or locator.get("chunk_parent_id")
        )
        if not parent_id or parent_id in seen or parent_id not in object_lookup:
            return values
        current = object_lookup[parent_id]
        values.append(current)
        seen.add(parent_id)


def _same_source_path(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_locator = left.get("locator") or {}
    right_locator = right.get("locator") or {}
    left_path = str(left_locator.get("path") or "").replace("\\", "/")
    right_path = str(right_locator.get("path") or "").replace("\\", "/")
    return bool(
        left_path
        and left_path == right_path
        and left.get("source_id") == right.get("source_id")
        and left.get("source_version_id") == right.get("source_version_id")
    )


def _is_descendant(
    candidate: dict[str, Any],
    ancestor: dict[str, Any],
    object_lookup: dict[str, dict[str, Any]],
) -> bool:
    ancestor_id = ancestor.get("object_id")
    current = candidate
    seen: set[str | None] = set()
    while current.get("object_id") not in seen:
        current_id = current.get("object_id")
        seen.add(current_id)
        parent_id = (
            current.get("parent_object_id")
            or current.get("chunk_parent_id")
            or (current.get("locator") or {}).get("parent_object_id")
            or (current.get("locator") or {}).get("chunk_parent_id")
        )
        if not parent_id:
            return False
        if parent_id == ancestor_id:
            return True
        current = object_lookup.get(parent_id)
        if current is None:
            return False
    return False


def _path_index(
    object_lookup: dict[str, dict[str, Any]],
) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    cached = _PATH_INDEX_CACHE.get(id(object_lookup))
    if cached is not None and cached[0] is object_lookup:
        return cached[1]
    index: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for candidate in object_lookup.values():
        locator = candidate.get("locator") or {}
        path = str(locator.get("path") or "").replace("\\", "/")
        if path:
            index[
                (
                    str(candidate.get("source_id") or ""),
                    str(candidate.get("source_version_id") or ""),
                    path,
                )
            ].append(candidate)
    _PATH_INDEX_CACHE[id(object_lookup)] = (object_lookup, index)
    return index


def _selector_match_provenance(
    selector: GoldEvidenceSelector,
    item: dict[str, Any],
    object_lookup: dict[str, dict[str, Any]],
    path_index: dict[tuple[str, str, str], list[dict[str, Any]]] | None = None,
) -> str | None:
    """Return the deterministic evidence-matching tier, if any.

    Gold v2.1 keeps every equivalence explicit in ``any_of``.  The matcher is
    still structure-aware: a cited chunk may satisfy a parent file selector,
    and a cited file object may satisfy a function/class selector when the
    selector's path and source version contain the function/class object.
    """
    if selector.matches(item):
        return "direct"
    for ancestor in _lineage(item, object_lookup)[1:]:
        if selector.matches(ancestor):
            return "ancestor"
    if path_index is None:
        path_index = _path_index(object_lookup)
    locator = item.get("locator") or {}
    path = str(locator.get("path") or "").replace("\\", "/")
    candidates_for_path = path_index.get(
        (
            str(item.get("source_id") or ""),
            str(item.get("source_version_id") or ""),
            path,
        ),
        [],
    )
    for candidate in candidates_for_path:
        if candidate.get("object_id") == item.get("object_id"):
            continue
        if not _same_source_path(candidate, item):
            continue
        if not _is_descendant(candidate, item, object_lookup):
            continue
        if selector.matches(candidate):
            return "path_descendant_containment"
    return None


def _matched_evidence_groups(
    groups: list[GoldEvidenceGroup],
    object_ids: list[str],
    object_lookup: dict[str, dict[str, Any]],
) -> tuple[float, list[dict[str, Any]]]:
    if not groups:
        return 1.0, []
    matched_count = 0
    provenance: list[dict[str, Any]] = []
    path_index = _path_index(object_lookup)
    items = [object_lookup[value] for value in object_ids if value in object_lookup]
    for group in groups:
        match: dict[str, Any] | None = None
        for item in items:
            for selector_index, selector in enumerate(group.any_of):
                tier = _selector_match_provenance(selector, item, object_lookup, path_index)
                if tier:
                    match = {
                        "group_id": group.group_id,
                        "object_id": item.get("object_id"),
                        "selector_index": selector_index,
                        "provenance": tier,
                    }
                    break
            if match:
                break
        if match:
            matched_count += 1
            provenance.append(match)
        else:
            provenance.append({"group_id": group.group_id, "matched": False})
    return matched_count / len(groups), provenance


def evidence_group_recall(
    groups: list[GoldEvidenceGroup],
    object_ids: list[str],
    object_lookup: dict[str, dict[str, Any]],
) -> float:
    return _matched_evidence_groups(groups, object_ids, object_lookup)[0]


def build_identifier_catalog(
    object_lookup: dict[str, dict[str, Any]],
    allowed_source_versions: list[str] | None = None,
) -> dict[str, set[str]]:
    """Build a deterministic identifier/path catalog for locked source versions."""
    allowed = set(allowed_source_versions or [])
    cache_key = (id(object_lookup), tuple(sorted(allowed)))
    if cache_key in _IDENTIFIER_CATALOG_CACHE:
        return _IDENTIFIER_CATALOG_CACHE[cache_key]
    symbols: set[str] = set()
    paths: set[str] = set()
    for item in object_lookup.values():
        if allowed and item.get("source_version_id") not in allowed:
            continue
        locator = item.get("locator") or {}
        symbol = str(locator.get("symbol") or "")
        if symbol:
            symbols.add(symbol)
        path = str(locator.get("path") or "").replace("\\", "/")
        if path:
            paths.add(path)
            paths.add(path.rsplit("/", 1)[-1])
        text = str(item.get("text") or "")
        for match in re.finditer(
            r"(?<![A-Za-z0-9_./-])(?:[A-Za-z0-9_.-]+\.(?:root|txt|json|yaml|yml|C|cxx|cpp|h|hpp|py))(?![A-Za-z0-9_./-])",
            text,
        ):
            paths.add(match.group(0))
        for match in re.finditer(
            r"\b(?:macro|src|data|docs?|model|fit|pgenerators|pid|apps|ui|tools)/[A-Za-z0-9_./-]+",
            text,
        ):
            paths.add(match.group(0).rstrip(".,;:)") )
        for match in re.finditer(
            r"\b(?:class|struct|enum)\s+([A-Za-z_][A-Za-z0-9_]*)", str(item.get("text") or "")
        ):
            symbols.add(match.group(1))
    result = {"symbols": symbols, "paths": paths}
    _IDENTIFIER_CATALOG_CACHE[cache_key] = result
    return result


def deterministic_case_metrics(
    case: GoldQuestion,
    result: dict[str, Any],
    diagnostics: dict[str, Any],
    object_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ranked_ids = ranked_object_ids(diagnostics, 20)
    top5_ids = ranked_ids[:5]
    top_ids = ranked_ids[:10]
    top20_ids = ranked_ids[:20]
    combined_candidate_ids = list(
        dict.fromkeys(
            object_id
            for object_ids in (diagnostics.get("rankings") or {}).values()
            for object_id in object_ids
        )
    )
    evidence = result.get("evidence", [])
    final_ids = [item["object_id"] for item in evidence if item.get("object_id")]
    # A rescore must be able to reproduce a frozen record even if the active
    # normalized corpus has since been rebuilt.  Keep the current locked
    # lookup authoritative, but retain immutable final-evidence snapshots for
    # IDs that only exist in the stored record.  This is an exact-object
    # fallback, not a semantic or embedding-based expansion.
    final_evidence_lookup = dict(object_lookup)
    for item in evidence:
        object_id = item.get("object_id")
        if object_id and object_id not in final_evidence_lookup:
            final_evidence_lookup[object_id] = item
    source_types: set[str] = set()
    wrong_versions: list[str] = []

    def source_type(item: dict[str, Any]) -> set[str]:
        canonical = object_lookup.get(item.get("object_id"), item)
        source_id = str(canonical.get("source_id", ""))
        object_type = str(canonical.get("object_type", ""))
        path = str((canonical.get("locator") or {}).get("path") or "").replace("\\", "/")
        values: set[str] = set()
        if source_id in {"li_2026", "karavdina_2015", "pflueger_2017"}:
            values.add("paper")
        elif "sphinx" in source_id or object_type.startswith("sphinx") or path.lower().startswith(("docs/", "doc/")):
            values.add("documentation")
        elif object_type in {"readme_section", "readme_section_chunk"} or path.lower().split("/")[-1].startswith("readme"):
            # README is a distinct source type, and is also operational
            # documentation. It must not masquerade as implementation code.
            values.update({"readme", "documentation"})
        elif object_type in {"workflow", "python_script", "shell_script"}:
            values.add("workflow")
        elif object_type == "relation" or "graph" in item.get("retrieval_channels", []):
            values.add("graph")
        else:
            values.add("code")
        values.update(
            channel
            for channel in item.get("retrieval_channels", [])
            if channel in {"workflow", "graph"}
        )
        return values

    for item in evidence:
        source_types.update(source_type(item))
        if item.get("source_version_id") not in case.allowed_source_versions:
            wrong_versions.append(item.get("evidence_id", ""))

    status_correct = result.get("status") == case.expected_status.value
    correct_refusal = case.expected_status != QAStatus.ANSWERED and status_correct
    # Metric applicability must be determined by Gold semantics, not by whether
    # the system happened to predict the correct status.  Ordinary answer-
    # oriented retrieval metrics apply only to Gold answered questions.
    ordinary_applicable = case.expected_status == QAStatus.ANSWERED
    refusal_applicable = (
        case.expected_status == QAStatus.INSUFFICIENT_EVIDENCE and status_correct
    )
    answer = result.get("answer", "")
    missing_identifiers = [
        value.text
        for value in case.required_identifiers
        if value.critical and not _required_identifier_present(value.text, answer)
    ]
    identifier_mentions: set[str] = set()
    identifier_exists: set[str] = set()
    identifier_supported: set[str] = set()
    hallucinated_identifiers: set[str] = set()
    unsupported_identifiers: set[str] = set()
    identifier_mentions_by_kind: dict[str, set[str]] = defaultdict(set)
    catalog = build_identifier_catalog(object_lookup, case.allowed_source_versions)
    catalog_values = catalog["symbols"] | catalog["paths"]
    for claim in result.get("claims", []):
        claim_text = claim.get("claim_text", "")
        cited_parts: list[str] = []
        for item in evidence:
            if item.get("evidence_id") not in claim.get("evidence_ids", []):
                continue
            locator = item.get("locator") or {}
            cited_parts.extend(
                [
                    item.get("text", ""),
                    locator.get("path") or "",
                    locator.get("symbol") or "",
                    locator.get("url") or "",
                    " / ".join(locator.get("section_path") or []),
                ]
            )
        cited_text = " ".join(cited_parts)
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_:./*-]+", claim_text):
            token = token.rstrip(".,;:)")
            kind, normalized = classify_identifier_mention(token)
            if not kind:
                continue
            identifier_mentions.add(token)
            identifier_mentions_by_kind[kind].add(token)
            if kind not in {"code_symbol", "path"}:
                continue
            if kind == "path" and normalized.endswith("/"):
                continue
            exists = normalized in catalog_values
            if kind == "code_symbol" and "::" in normalized:
                exists = exists or normalized.rsplit("::", 1)[-1] in catalog["symbols"]
            supported = normalized in cited_text or (
                kind == "code_symbol"
                and "::" in normalized
                and normalized.rsplit("::", 1)[-1] in cited_text
            )
            if exists:
                identifier_exists.add(normalized)
            else:
                hallucinated_identifiers.add(normalized)
            if supported:
                identifier_supported.add(normalized)
            elif exists:
                unsupported_identifiers.add(normalized)

    cited = {eid for claim in result.get("claims", []) for eid in claim.get("evidence_ids", [])}
    evidence_ids = {item.get("evidence_id") for item in evidence}
    forbidden_hits = [
        item.get("evidence_id")
        for item in evidence
        if any(selector.matches(item) for selector in case.forbidden_evidence)
    ]
    critical_groups = [group for group in case.required_evidence_groups if group.critical]
    top5_recall, top5_provenance = _matched_evidence_groups(
        case.required_evidence_groups, top5_ids, object_lookup
    )
    top_recall, top_provenance = _matched_evidence_groups(
        case.required_evidence_groups, top_ids, object_lookup
    )
    top20_recall, top20_provenance = _matched_evidence_groups(
        case.required_evidence_groups, top20_ids, object_lookup
    )
    combined_recall, combined_provenance = _matched_evidence_groups(
        case.required_evidence_groups, combined_candidate_ids, object_lookup
    )
    rank_by_object_id = {object_id: rank for rank, object_id in enumerate(ranked_ids, 1)}
    relevant_ranks = [
        rank_by_object_id[item["object_id"]]
        for item in top20_provenance
        if item.get("object_id") in rank_by_object_id
    ]
    reciprocal_rank = 1.0 / min(relevant_ranks) if relevant_ranks else 0.0
    final_recall, final_provenance = _matched_evidence_groups(
        case.required_evidence_groups, final_ids, final_evidence_lookup
    )
    critical_recall, critical_provenance = _matched_evidence_groups(
        critical_groups, final_ids, final_evidence_lookup
    )
    refusal_recall = (
        max(
            (
                1.0
                if item.get("matched") or item.get("provenance")
                else 0.0
            )
            for item in final_provenance
        )
        if refusal_applicable and final_provenance
        else (1.0 if refusal_applicable and not case.required_evidence_groups else 0.0)
        if refusal_applicable
        else None
    )
    metric_applicability = {
        "gold_recall_at_5": ordinary_applicable,
        "gold_recall_at_10": ordinary_applicable,
        "gold_recall_at_20": ordinary_applicable,
        "mrr": ordinary_applicable,
        "combined_candidate_recall": ordinary_applicable,
        "final_evidence_recall": ordinary_applicable,
        "critical_final_evidence_recall": ordinary_applicable,
        "required_source_coverage": ordinary_applicable,
        "required_identifiers": ordinary_applicable,
        "identifier_hallucination_rate": ordinary_applicable,
        "paper_code_dual_source": ordinary_applicable,
        "refusal_evidence_recall": refusal_applicable,
        "expected_status_correct": True,
    }
    metric_denominators = {
        key: int(value) for key, value in metric_applicability.items()
    }
    return {
        "intent_correct": diagnostics.get("plan", {}).get("intent")
        in {case.intent, *case.accepted_intents},
        "expected_status_correct": status_correct,
        "correct_refusal": correct_refusal,
        "gold_recall_at_5": top5_recall if ordinary_applicable else None,
        "gold_recall_at_10": top_recall if ordinary_applicable else None,
        "gold_recall_at_20": top20_recall if ordinary_applicable else None,
        "mrr": reciprocal_rank if ordinary_applicable else None,
        "combined_candidate_recall": combined_recall if ordinary_applicable else None,
        "final_evidence_recall": final_recall if ordinary_applicable else None,
        "critical_final_evidence_recall": critical_recall if ordinary_applicable else None,
        "refusal_evidence_recall": refusal_recall,
        "required_source_coverage": (
            all(value in source_types for value in case.required_source_types)
            if ordinary_applicable
            else None
        ),
        "wrong_version_evidence": wrong_versions,
        "forbidden_evidence": forbidden_hits,
        "citation_integrity": cited.issubset(evidence_ids) and all(
            claim.get("evidence_ids") for claim in result.get("claims", [])
        ),
        "missing_identifiers": missing_identifiers if ordinary_applicable else None,
        "identifier_mentions": sorted(identifier_mentions),
        "identifier_mentions_by_kind": {
            key: sorted(values) for key, values in sorted(identifier_mentions_by_kind.items())
        },
        "identifier_exists_in_locked_corpus": sorted(identifier_exists),
        "identifier_supported_by_claim_evidence": sorted(identifier_supported),
        "unsupported_identifiers": sorted(unsupported_identifiers),
        "hallucinated_identifiers": (
            sorted(hallucinated_identifiers) if ordinary_applicable else []
        ),
        "major_identifier_hallucinations": (
            sorted(hallucinated_identifiers) if ordinary_applicable else []
        ),
        "paper_code_dual_source": (
            {"paper", "code"}.issubset(source_types)
            if ordinary_applicable
            else None
        ),
        "evidence_match_provenance": {
            "gold_recall_at_5": top5_provenance,
            "gold_recall_at_10": top_provenance,
            "gold_recall_at_20": top20_provenance,
            "combined_candidate_recall": combined_provenance,
            "final_evidence_recall": final_provenance,
            "critical_final_evidence_recall": critical_provenance,
        },
        "metric_applicability": metric_applicability,
        "metric_denominators": metric_denominators,
    }


JUDGE_METRIC_FIELDS = (
    "answer_point_coverage",
    "covered_point_ids",
    "critical_answer_points_missing",
    "contradictions",
    "unsupported_claim_ids",
    "major_unsupported_claim_ids",
    "minor_unsupported_claim_ids",
    "claim_verdicts",
)

ANSWER_STAGE_METRIC_FIELDS = (
    "citation_integrity",
    "missing_identifiers",
    "identifier_mentions",
    "identifier_mentions_by_kind",
    "identifier_exists_in_locked_corpus",
    "identifier_supported_by_claim_evidence",
    "unsupported_identifiers",
    "hallucinated_identifiers",
    "major_identifier_hallucinations",
)


def apply_mode_metric_semantics(
    metrics: dict[str, Any],
    *,
    mode: Literal["retrieval", "qa", "full"],
    external_judge: bool,
) -> dict[str, Any]:
    """Mark only metrics produced by stages that actually ran as applicable."""
    updated = dict(metrics)
    applicability = dict(updated.get("metric_applicability") or {})
    denominators = dict(updated.get("metric_denominators") or {})

    def set_applicable(field: str, applicable: bool) -> None:
        applicability[field] = applicable
        denominators[field] = int(applicable)

    answer_stage_ran = mode in {"qa", "full"}
    set_applicable("citation_integrity", answer_stage_ran)
    set_applicable(
        "required_identifiers",
        answer_stage_ran and applicability.get("required_identifiers", True),
    )
    set_applicable(
        "identifier_hallucination_rate",
        answer_stage_ran and applicability.get("identifier_hallucination_rate", True),
    )
    # Retrieval mode does not run the production sufficiency/refusal decision,
    # so it must not claim a QA expected-status measurement.  QA/full preserve
    # expected-status measurement and gating.
    set_applicable("expected_status_correct", answer_stage_ran)
    # Refusal evidence recall is a downstream sufficiency metric; in retrieval
    # mode it is not measured.  QA/full keep their existing semantics.
    set_applicable(
        "refusal_evidence_recall",
        answer_stage_ran and applicability.get("refusal_evidence_recall", False),
    )
    if not answer_stage_ran:
        for field in ANSWER_STAGE_METRIC_FIELDS:
            updated.pop(field, None)

    for field in JUDGE_METRIC_FIELDS:
        set_applicable(field, external_judge)
        if not external_judge:
            updated.pop(field, None)

    updated["metric_applicability"] = applicability
    updated["metric_denominators"] = denominators
    return updated


def normalize_run_records(
    records: list[dict[str, Any]], manifest: dict[str, Any]
) -> list[dict[str, Any]]:
    """Apply current applicability semantics without mutating source records."""
    mode = manifest.get("mode")
    if mode not in {"retrieval", "qa", "full"}:
        raise ValueError(f"unsupported evaluation mode: {mode}")
    boundaries = manifest.get("pipeline_boundaries") or {}
    external_judge = (
        bool(boundaries.get("external_judge"))
        if "external_judge" in boundaries
        else mode in {"qa", "full"}
    )
    normalized: list[dict[str, Any]] = []
    for record in records:
        updated = dict(record)
        if record.get("metrics"):
            updated["metrics"] = apply_mode_metric_semantics(
                record["metrics"],
                mode=mode,
                external_judge=external_judge,
            )
        normalized.append(updated)
    return normalized


def offline_rescore_records(
    records: list[dict[str, Any]],
    dataset: GoldDataset,
    object_lookup: dict[str, dict[str, Any]],
    *,
    mode: Literal["retrieval", "qa", "full"] = "retrieval",
) -> list[dict[str, Any]]:
    """Recompute evaluator metrics from immutable records with zero model calls.

    Source ``result``/``diagnostics`` are not modified; only per-record metrics
    are rebuilt under the current evaluator semantics.
    """
    questions = {str(item.id): item for item in dataset.questions}
    rescored: list[dict[str, Any]] = []
    for record in records:
        question = questions.get(str(record.get("id")))
        if question is None:
            continue
        metrics = deterministic_case_metrics(
            question,
            record.get("result") or {},
            record.get("diagnostics") or {},
            object_lookup,
        )
        metrics = apply_mode_metric_semantics(
            metrics,
            mode=mode,
            external_judge=False,
        )
        updated = dict(record)
        updated["metrics"] = metrics
        updated["intent"] = question.intent
        updated["expected_status"] = question.expected_status.value
        rescored.append(updated)
    return rescored


def aggregate_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [item for item in records if item.get("metrics")]
    if not scored:
        return {"cases_completed": len(records), "scored_cases": 0}
    intents: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in scored:
        intents[item["intent"]].append(item["metrics"])

    def applicable(field: str, item: dict[str, Any]) -> bool:
        legacy_fields = {
            "required_identifiers": ("missing_identifiers",),
            "identifier_hallucination_rate": (
                "identifier_mentions",
                "hallucinated_identifiers",
            ),
        }
        inferred = field in item and item.get(field) is not None
        if field in legacy_fields:
            inferred = any(value in item for value in legacy_fields[field])
        return bool(
            (item.get("metric_applicability") or {}).get(
                field, inferred
            )
        )

    def mean(field: str, values: list[dict[str, Any]]) -> float | None:
        defined = [
            item.get(field)
            for item in values
            if applicable(field, item) and item.get(field) is not None
        ]
        return sum(float(value) for value in defined) / len(defined) if defined else None

    def denominator(field: str, values: list[dict[str, Any]]) -> int:
        return sum(
            int(
                applicable(field, item)
            )
            for item in values
        )

    def list_count(
        field: str,
        values: list[dict[str, Any]],
        *,
        fallback_field: str | None = None,
    ) -> tuple[int | None, int]:
        measured = [
            item
            for item in values
            if applicable(field, item)
            or (fallback_field is not None and applicable(fallback_field, item))
        ]
        if not measured:
            return None, 0
        return (
            sum(
                len(
                    item.get(field)
                    if item.get(field) is not None
                    else item.get(fallback_field, []) if fallback_field else []
                )
                for item in measured
            ),
            len(measured),
        )

    all_metrics = [item["metrics"] for item in scored]
    per_intent = {
        intent: {
            "cases": len(values),
            "intent_accuracy": mean("intent_correct", values),
            "gold_recall_at_5": mean("gold_recall_at_5", values),
            "gold_recall_at_10": mean("gold_recall_at_10", values),
            "gold_recall_at_20": mean("gold_recall_at_20", values),
            "mrr": mean("mrr", values),
            "combined_candidate_recall": mean("combined_candidate_recall", values),
            "gold_recall_at_10_denominator": denominator("gold_recall_at_10", values),
            "final_evidence_recall": mean("final_evidence_recall", values),
            "final_evidence_recall_denominator": denominator("final_evidence_recall", values),
        }
        for intent, values in sorted(intents.items())
    }
    identifier_applicable = [
        item for item in all_metrics if applicable("identifier_hallucination_rate", item)
    ]
    identifier_mentions = sum(len(item.get("identifier_mentions", [])) for item in identifier_applicable)
    hallucinated_identifiers = sum(
        len(item.get("hallucinated_identifiers", [])) for item in identifier_applicable
    )
    dual_source_cases = [
        item["metrics"]
        for item in scored
        if item.get("expected_status") == QAStatus.ANSWERED.value
        if (item.get("metrics") or {}).get("metric_applicability", {}).get(
            "paper_code_dual_source", True
        )
        if {"paper", "code"}.issubset(set(item.get("required_source_types", [])))
    ]
    answered_cases = [
        item["metrics"]
        for item in scored
        if item.get("expected_status") == QAStatus.ANSWERED.value
    ]
    latencies = sorted(
        float(item.get("duration_ms", 0))
        for item in scored
        if item.get("duration_ms") is not None
    )
    contradiction_count, contradiction_denominator = list_count(
        "contradictions", all_metrics
    )
    unsupported_claim_count, unsupported_claim_denominator = list_count(
        "unsupported_claim_ids", all_metrics
    )
    major_unsupported_claim_count, major_unsupported_claim_denominator = list_count(
        "major_unsupported_claim_ids",
        all_metrics,
        fallback_field="unsupported_claim_ids",
    )
    minor_unsupported_claim_count, minor_unsupported_claim_denominator = list_count(
        "minor_unsupported_claim_ids", all_metrics
    )
    critical_answer_point_miss_count, critical_answer_point_denominator = list_count(
        "critical_answer_points_missing", all_metrics
    )
    answer_point_denominator = denominator("answer_point_coverage", all_metrics)
    citation_denominator = denominator("citation_integrity", all_metrics)
    identifier_miss_denominator = denominator("required_identifiers", all_metrics)
    return {
        "cases_completed": len(records),
        "scored_cases": len(scored),
        "intent_accuracy": mean("intent_correct", all_metrics),
        "gold_recall_at_5": mean("gold_recall_at_5", all_metrics),
        "gold_recall_at_5_denominator": denominator("gold_recall_at_5", all_metrics),
        "gold_recall_at_10": mean("gold_recall_at_10", all_metrics),
        "gold_recall_at_10_denominator": denominator("gold_recall_at_10", all_metrics),
        "gold_recall_at_20": mean("gold_recall_at_20", all_metrics),
        "gold_recall_at_20_denominator": denominator("gold_recall_at_20", all_metrics),
        "mrr": mean("mrr", all_metrics),
        "mrr_denominator": denominator("mrr", all_metrics),
        "combined_candidate_recall": mean("combined_candidate_recall", all_metrics),
        "combined_candidate_recall_denominator": denominator(
            "combined_candidate_recall", all_metrics
        ),
        "final_evidence_recall": mean("final_evidence_recall", all_metrics),
        "final_evidence_recall_denominator": denominator("final_evidence_recall", all_metrics),
        "critical_final_evidence_recall": mean(
            "critical_final_evidence_recall", all_metrics
        ),
        "critical_final_evidence_recall_denominator": denominator(
            "critical_final_evidence_recall", all_metrics
        ),
        "refusal_evidence_recall": mean("refusal_evidence_recall", all_metrics),
        "refusal_evidence_recall_denominator": denominator(
            "refusal_evidence_recall", all_metrics
        ),
        "expected_status_accuracy": mean("expected_status_correct", all_metrics),
        "expected_status_accuracy_denominator": denominator(
            "expected_status_correct", all_metrics
        ),
        "citation_integrity": mean("citation_integrity", all_metrics),
        "citation_integrity_denominator": citation_denominator,
        "required_source_coverage": mean("required_source_coverage", all_metrics),
        "required_source_coverage_denominator": denominator(
            "required_source_coverage", all_metrics
        ),
        "required_source_coverage_answered": (
            mean("required_source_coverage", answered_cases) if answered_cases else None
        ),
        "required_source_coverage_answered_denominator": denominator(
            "required_source_coverage", answered_cases
        ),
        "wrong_version_evidence_count": sum(
            len(item.get("wrong_version_evidence", [])) for item in all_metrics
        ),
        "forbidden_evidence_count": sum(
            len(item.get("forbidden_evidence", [])) for item in all_metrics
        ),
        "identifier_miss_count": (
            sum(len(item.get("missing_identifiers") or []) for item in identifier_applicable)
            if identifier_applicable
            else None
        ),
        "identifier_miss_denominator": identifier_miss_denominator,
        "identifier_mentions": identifier_mentions,
        "identifier_hallucination_count": hallucinated_identifiers,
        "identifier_hallucination_denominator": identifier_mentions,
        "identifier_hallucination_rate": (
            hallucinated_identifiers / identifier_mentions
            if identifier_mentions
            else 0.0 if identifier_applicable else None
        ),
        "answer_point_coverage": mean("answer_point_coverage", all_metrics),
        "answer_point_coverage_denominator": answer_point_denominator,
        "contradiction_count": contradiction_count,
        "contradiction_count_denominator": contradiction_denominator,
        "unsupported_claim_count": unsupported_claim_count,
        "unsupported_claim_count_denominator": unsupported_claim_denominator,
        "major_unsupported_claim_count": major_unsupported_claim_count,
        "major_unsupported_claim_count_denominator": major_unsupported_claim_denominator,
        "minor_unsupported_claim_count": minor_unsupported_claim_count,
        "minor_unsupported_claim_count_denominator": minor_unsupported_claim_denominator,
        "critical_answer_point_miss_count": critical_answer_point_miss_count,
        "critical_answer_point_miss_count_denominator": critical_answer_point_denominator,
        "paper_code_dual_source_rate": (
            mean("paper_code_dual_source", dual_source_cases)
            if dual_source_cases
            else 1.0
        ),
        "paper_code_dual_source_denominator": len(dual_source_cases),
        "unhandled_exception_count": sum(bool(item.get("exception")) for item in records),
        "latency_ms": {
            "mean": sum(latencies) / len(latencies) if latencies else 0.0,
            "p95": latencies[
                min(len(latencies) - 1, int(len(latencies) * 0.95))
            ]
            if latencies
            else 0.0,
        },
        "model_calls": sum(int(item.get("model_calls", 0)) for item in records),
        "token_usage": sum(int(item.get("token_usage", 0)) for item in records),
        "model_usage_by_role": {
            "runtime": {
                "model_calls": sum(
                    int(
                        item.get("model_call_breakdown", {})
                        .get("runtime", {})
                        .get("model_calls", 0)
                    )
                    for item in records
                ),
                "token_usage": sum(
                    int(
                        item.get("model_call_breakdown", {})
                        .get("runtime", {})
                        .get("token_usage", 0)
                    )
                    for item in records
                ),
            },
            "evaluation_judge": {
                "model_calls": sum(
                    int(
                        item.get("model_call_breakdown", {})
                        .get("judge", {})
                        .get("model_calls", 0)
                    )
                    for item in records
                ),
                "token_usage": sum(
                    int(
                        item.get("model_call_breakdown", {})
                        .get("judge", {})
                        .get("token_usage", 0)
                    )
                    for item in records
                ),
            },
        },
        "metric_applicability": {
            "citation_integrity": citation_denominator > 0,
            "required_identifiers": identifier_miss_denominator > 0,
            "identifier_hallucination_rate": bool(identifier_applicable),
            "answer_point_coverage": answer_point_denominator > 0,
            "contradictions": contradiction_denominator > 0,
            "unsupported_claim_ids": unsupported_claim_denominator > 0,
            "major_unsupported_claim_ids": major_unsupported_claim_denominator > 0,
            "minor_unsupported_claim_ids": minor_unsupported_claim_denominator > 0,
            "critical_answer_points_missing": critical_answer_point_denominator > 0,
        },
        "per_intent": per_intent,
    }


def _metric_at_least(metrics: dict[str, Any], field: str, threshold: float) -> bool:
    value = metrics.get(field)
    return value is not None and float(value) >= threshold


def _metric_below(metrics: dict[str, Any], field: str, threshold: float) -> bool:
    value = metrics.get(field)
    return value is not None and float(value) < threshold


def evaluate_quality_gate(
    metrics: dict[str, Any],
    records: list[dict[str, Any]],
    *,
    official: bool,
    all_questions_approved: bool,
) -> dict[str, Any]:
    """Evaluate frozen M6 acceptance thresholds.

    A complete approved development run is assessed by
    :func:`evaluate_development_gate`; it is intentionally not a formal M6
    acceptance run.
    """
    version_cases = [
        item
        for item in records
        if item.get("expected_status") == QAStatus.VERSION_CONFLICT.value
    ]
    checks = {
        "official_run": official,
        "all_questions_approved": all_questions_approved,
        "gold_recall_at_10": _metric_at_least(metrics, "gold_recall_at_10", 0.95),
        "final_evidence_recall": _metric_at_least(
            metrics, "final_evidence_recall", 0.90
        ),
        "critical_evidence_coverage": _metric_at_least(
            metrics, "critical_final_evidence_recall", 1.0
        ),
        "intent_accuracy": _metric_at_least(metrics, "intent_accuracy", 0.90),
        "per_intent_recall": all(
            _metric_at_least(item, "gold_recall_at_10", 0.75)
            for item in metrics.get("per_intent", {}).values()
        ),
        "per_intent_accuracy": all(
            _metric_at_least(item, "intent_accuracy", 0.80)
            for item in metrics.get("per_intent", {}).values()
        ),
        "expected_status_accuracy": _metric_at_least(
            metrics, "expected_status_accuracy", 0.975
        ),
        "all_version_conflicts_rejected": bool(version_cases) and all(
            item.get("metrics", {}).get("expected_status_correct")
            for item in version_cases
        ),
        "citation_integrity": metrics.get("citation_integrity", 0.0) == 1.0,
        "wrong_version_evidence": metrics.get("wrong_version_evidence_count", 0) == 0,
        "forbidden_evidence": metrics.get("forbidden_evidence_count", 0) == 0,
        "required_source_coverage": _metric_at_least(
            metrics, "required_source_coverage_answered", 0.97
        ),
        "required_identifiers": metrics.get("identifier_miss_count", 0) == 0,
        "identifier_hallucination_rate": _metric_below(
            metrics, "identifier_hallucination_rate", 0.03
        ),
        "paper_code_dual_source": metrics.get("paper_code_dual_source_rate", 0.0)
        == 1.0,
        "answer_point_coverage": _metric_at_least(
            metrics, "answer_point_coverage", 0.90
        ),
        "critical_answer_points": metrics.get("critical_answer_point_miss_count")
        is not None
        and metrics["critical_answer_point_miss_count"] == 0,
        "no_contradictions": metrics.get("contradiction_count") is not None
        and metrics["contradiction_count"] == 0,
        "no_major_unsupported_claims": metrics.get("major_unsupported_claim_count")
        is not None
        and metrics["major_unsupported_claim_count"] == 0,
        "unhandled_exceptions": metrics.get("unhandled_exception_count", 0) == 0,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "note": (
            "Formal M6 gate result."
            if official and all_questions_approved
            else (
                "Formal M6 release requires one complete approved hidden acceptance run; "
                "dev, focused, draft, regression, and partial runs cannot pass it."
            )
        ),
    }


def evaluate_development_gate(
    metrics: dict[str, Any],
    records: list[dict[str, Any]],
    *,
    mode: Literal["retrieval", "qa", "full"],
    complete_full_dev: bool,
    all_questions_approved: bool,
) -> dict[str, Any]:
    """Evaluate an 80-case development run without acceptance rules.

    The formal M6 release gate remains acceptance-only.  This separate gate is
    intentionally mode-aware: retrieval changes are not forced through answer
    generation metrics, while QA candidates inherit the retrieval checks and
    add deterministic answer checks. Only ``full`` adds external-judge checks.
    Focused runs can report metrics, but can never pass the complete gate.
    """
    version_cases = [
        item
        for item in records
        if item.get("expected_status") == QAStatus.VERSION_CONFLICT.value
    ]
    checks = {
        "complete_full_dev": complete_full_dev,
        "all_questions_approved": all_questions_approved,
        "gold_recall_at_10": _metric_at_least(metrics, "gold_recall_at_10", 0.95),
        "final_evidence_recall": _metric_at_least(
            metrics, "final_evidence_recall", 0.90
        ),
        "critical_evidence_coverage": _metric_at_least(
            metrics, "critical_final_evidence_recall", 1.0
        ),
        "intent_accuracy": _metric_at_least(metrics, "intent_accuracy", 0.90),
        "per_intent_recall": all(
            _metric_at_least(item, "gold_recall_at_10", 0.75)
            for item in metrics.get("per_intent", {}).values()
        ),
        "per_intent_accuracy": all(
            _metric_at_least(item, "intent_accuracy", 0.80)
            for item in metrics.get("per_intent", {}).values()
        ),
        "dev_version_conflicts_rejected": bool(version_cases) and all(
            item.get("metrics", {}).get("expected_status_correct")
            for item in version_cases
        ),
        "wrong_version_evidence": metrics.get("wrong_version_evidence_count", 0) == 0,
        "forbidden_evidence": metrics.get("forbidden_evidence_count", 0) == 0,
        "required_source_coverage": _metric_at_least(
            metrics, "required_source_coverage_answered", 0.97
        ),
        "unhandled_exceptions": metrics.get("unhandled_exception_count", 0) == 0,
    }
    if mode in {"qa", "full"}:
        checks.update(
            {
                "expected_status_accuracy": _metric_at_least(
                    metrics, "expected_status_accuracy", 0.975
                ),
                "citation_integrity": metrics.get("citation_integrity", 0.0) == 1.0,
                "required_identifiers": metrics.get("identifier_miss_count", 0) == 0,
                "identifier_hallucination_rate": _metric_below(
                    metrics, "identifier_hallucination_rate", 0.03
                ),
                "paper_code_dual_source": metrics.get(
                    "paper_code_dual_source_rate", 0.0
                )
                == 1.0,
            }
        )
    if mode == "full":
        checks.update(
            {
                "answer_point_coverage": _metric_at_least(
                    metrics, "answer_point_coverage", 0.90
                ),
                "critical_answer_points": metrics.get(
                    "critical_answer_point_miss_count"
                )
                is not None
                and metrics["critical_answer_point_miss_count"] == 0,
                "no_contradictions": metrics.get("contradiction_count") is not None
                and metrics["contradiction_count"] == 0,
                "no_major_unsupported_claims": metrics.get(
                    "major_unsupported_claim_count"
                )
                is not None
                and metrics["major_unsupported_claim_count"] == 0,
            }
        )
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "note": (
            "Complete declared development gate."
            if complete_full_dev
            else "Focused or incomplete run: it can diagnose a layer but cannot pass the development gate."
        ),
    }


def effective_product_language(
    question: GoldQuestion, calibration: dict[str, Any] | None
) -> str:
    """Return reviewed effective product language, falling back to raw Gold."""
    if calibration:
        for override in calibration.get("reviewed_overrides", []):
            if str(override.get("case_id")) == str(question.id):
                value = override.get("effective_product_language")
                if value in {"en", "non_en"}:
                    return value
    return question.language


def english_product_case_ids(
    dataset: GoldDataset,
    split: str = "dev",
    calibration: dict[str, Any] | None = None,
) -> list[str]:
    """Return the deterministic approved English product-scope IDs for a split.

    Effective product language comes from the reviewed calibration when an
    override exists; otherwise raw Gold language is used.
    """
    return [
        str(item.id)
        for item in dataset.questions
        if item.split == split
        and item.review_status == "approved"
        and effective_product_language(item, calibration) == "en"
    ]


def validate_product_language_calibration(calibration: dict[str, Any]) -> None:
    """Validate the reviewed product-language calibration artifact structure."""
    required = {
        "calibration_id",
        "source_gold",
        "source_t3_manifest",
        "source_run_id",
        "scope",
        "classification_rule",
        "raw_language_distribution",
        "reviewed_overrides",
        "formal_english_ids",
        "non_english_ids",
        "counts",
    }
    missing = sorted(required - set(calibration))
    if missing:
        raise ValueError(f"product-language calibration missing fields: {missing}")
    overrides = calibration.get("reviewed_overrides", [])
    if not isinstance(overrides, list):
        raise ValueError("reviewed_overrides must be a list")
    ids = [str(item.get("case_id")) for item in overrides]
    if len(ids) != len(set(ids)):
        raise ValueError("reviewed_overrides must have unique case IDs")
    for item in overrides:
        if item.get("effective_product_language") not in {"en", "non_en"}:
            raise ValueError(
                f"invalid effective_product_language for {item.get('case_id')}"
            )
    english_ids = [str(item) for item in calibration.get("formal_english_ids", [])]
    non_english_ids = [
        str(item) for item in calibration.get("non_english_ids", [])
    ]
    if len(english_ids) != len(set(english_ids)):
        raise ValueError("formal_english_ids must be unique")
    if len(non_english_ids) != len(set(non_english_ids)):
        raise ValueError("non_english_ids must be unique")
    if set(english_ids) & set(non_english_ids):
        raise ValueError("formal_english_ids and non_english_ids must be disjoint")
    if int(calibration.get("counts", {}).get("formal_english")) != len(english_ids):
        raise ValueError("counts.formal_english does not match formal_english_ids")
    if int(calibration.get("counts", {}).get("non_english")) != len(non_english_ids):
        raise ValueError("counts.non_english does not match non_english_ids")


def newest_signed_exposed_gold_dir(project_root: Path) -> Path:
    """Resolve the newest signed exposed benchmark directory.

    Candidate directories are discovered from ``evaluation/benchmarks/v2_N``
    names, so adding a successor benchmark requires no resolver change.  A
    directory qualifies only when its manifest dataset hash matches the
    dataset file and both official-validation flags are true; the highest
    version number wins.  Raises FileNotFoundError when no directory
    qualifies (old checkouts fall back to the historical resolver chain in
    ``evaluation_runner.default_gold_dataset_path``).
    """
    benchmarks_dir = project_root / "evaluation" / "benchmarks"
    qualified: list[tuple[int, Path]] = []
    if benchmarks_dir.is_dir():
        for child in benchmarks_dir.iterdir():
            match = re.fullmatch(r"v2_(\d+)", child.name)
            if not match or not child.is_dir():
                continue
            manifest_path = child / "benchmark_manifest.json"
            dataset_path = child / "gold_questions.yaml"
            if not manifest_path.is_file() or not dataset_path.is_file():
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            official = manifest.get("project_official_validation") or {}
            if (
                manifest.get("dataset_sha256") == sha256_file(dataset_path)
                and official.get("official_ready") is True
                and official.get("structurally_valid") is True
            ):
                qualified.append((int(match.group(1)), child))
    if not qualified:
        raise FileNotFoundError(
            "no signed exposed benchmark with a consistent official manifest found"
        )
    return max(qualified, key=lambda entry: entry[0])[1]


def newest_product_language_calibration_path(project_root: Path) -> Path | None:
    """Return the newest reviewed product-language calibration artifact path.

    Mechanical successor discovery over
    ``phase_b_t3_product_language_scope_vN.json``; the highest version number
    is authoritative (GOLD-9).
    """
    manifests_dir = project_root / "evaluation" / "baselines" / "manifests"
    versions = sorted(
        int(match.group(1))
        for candidate in manifests_dir.glob("phase_b_t3_product_language_scope_v*.json")
        if (match := re.search(r"_v(\d+)\.json$", candidate.name))
    ) if manifests_dir.is_dir() else []
    if not versions:
        return None
    return manifests_dir / f"phase_b_t3_product_language_scope_v{versions[-1]}.json"


def load_product_language_calibration(
    project_root: Path,
    path: Path | None = None,
) -> dict[str, Any] | None:
    """Load and validate the reviewed product-language calibration artifact.

    The newest ``phase_b_t3_product_language_scope_vN.json`` in the manifests
    directory is authoritative (GOLD-9), so the resolution advances with each
    reviewed successor instead of stopping at an older hard-coded one.
    Compatibility with the active Gold is validated by the caller; an older
    calibration is never silently substituted for the newest one.
    """
    if path is not None:
        calibration_path = path
    else:
        calibration_path = newest_product_language_calibration_path(project_root)
        if calibration_path is None:
            return None
    if not calibration_path.is_file():
        return None
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    validate_product_language_calibration(calibration)
    return calibration


def derive_product_language_ids(
    dataset: GoldDataset, calibration: dict[str, Any]
) -> tuple[list[str], list[str]]:
    """Derive formal/non-English IDs from raw Gold + reviewed overrides."""
    split = calibration.get("scope", {}).get("split", "dev")
    scope_ids = {
        str(item.id)
        for item in dataset.questions
        if item.split == split and item.review_status == "approved"
    }
    english: list[str] = []
    non_english: list[str] = []
    for item in dataset.questions:
        if str(item.id) not in scope_ids:
            continue
        if effective_product_language(item, calibration) == "en":
            english.append(str(item.id))
        else:
            non_english.append(str(item.id))
    return sorted(english), sorted(non_english)


def calibration_compatibility(
    calibration: dict[str, Any],
    dataset: GoldDataset,
    dataset_path: Path | None = None,
) -> dict[str, Any]:
    """Verify a reviewed calibration is compatible with the active dataset."""
    result: dict[str, Any] = {
        "calibration_id": calibration.get("calibration_id"),
        "compatible": True,
        "reason": None,
    }
    cal_gold = calibration.get("source_gold") or {}
    cal_version = cal_gold.get("version")
    cal_sha = cal_gold.get("sha256")
    if cal_version != dataset.benchmark_version:
        result.update(compatible=False, reason="calibration Gold version does not match active dataset")
        return result
    if dataset_path is not None:
        active_sha = sha256_file(dataset_path)
        if cal_sha != active_sha:
            result.update(compatible=False, reason="calibration Gold SHA-256 does not match active dataset file")
            return result
    split = calibration.get("scope", {}).get("split")
    if split != "dev":
        result.update(compatible=False, reason="calibration scope split is not dev")
        return result
    question_by_id = {str(item.id): item for item in dataset.questions}
    for override in calibration.get("reviewed_overrides", []):
        case_id = str(override.get("case_id"))
        question = question_by_id.get(case_id)
        if question is None or question.split != split or question.review_status != "approved":
            result.update(compatible=False, reason=f"override references unknown/out-of-scope ID {case_id}")
            return result
        if question.language != override.get("raw_language"):
            result.update(
                compatible=False,
                reason=f"override raw_language for {case_id} disagrees with Gold",
            )
            return result
    derived_en, derived_non = derive_product_language_ids(dataset, calibration)
    declared_en = sorted(str(item) for item in calibration.get("formal_english_ids", []))
    declared_non = sorted(str(item) for item in calibration.get("non_english_ids", []))
    if set(declared_en) != set(derived_en):
        result.update(compatible=False, reason="declared formal_english_ids differ from derived IDs")
        return result
    if set(declared_non) != set(derived_non):
        result.update(compatible=False, reason="declared non_english_ids differ from derived IDs")
        return result
    scope_ids = {
        str(item.id)
        for item in dataset.questions
        if item.split == split and item.review_status == "approved"
    }
    union = set(declared_en) | set(declared_non)
    if union != scope_ids:
        result.update(compatible=False, reason="calibration IDs do not exactly partition approved scope")
        return result
    return result


def evaluate_product_development_gate(
    metrics: dict[str, Any],
    records: list[dict[str, Any]],
    dataset: GoldDataset,
    *,
    mode: Literal["retrieval", "qa", "full"] = "retrieval",
    calibration: dict[str, Any] | None = None,
    dataset_path: Path | None = None,
) -> dict[str, Any]:
    """Evaluate a formal English product-scope development gate.

    Completeness is derived from the reviewed calibration + approved dataset
    selector, not from a hard-coded question count or an arbitrary caller-
    supplied case list.  A hand-picked subset therefore cannot masquerade as a
    complete product gate.
    """
    compatibility: dict[str, Any] | None = None
    if calibration is not None:
        compatibility = calibration_compatibility(
            calibration, dataset, dataset_path=dataset_path
        )
        if not compatibility["compatible"]:
            raise ValueError(
                f"incompatible product-language calibration: {compatibility['reason']}"
            )
        derived_en, _ = derive_product_language_ids(dataset, calibration)
        expected_ids = derived_en
    else:
        expected_ids = english_product_case_ids(
            dataset, split="dev", calibration=None
        )
    actual_ids = [str(record.get("id")) for record in records]
    complete = (
        len(actual_ids) == len(set(actual_ids))
        and set(actual_ids) == set(expected_ids)
    )
    gate = evaluate_development_gate(
        metrics,
        records,
        mode=mode,
        complete_full_dev=complete,
        all_questions_approved=True,
    )
    gate["product_scope"] = {
        "selector": {
            "split": "dev",
            "review_status": "approved",
            "effective_product_language": "en",
        },
        "calibration_id": (calibration or {}).get("calibration_id"),
        "calibration_compatibility": compatibility,
        "expected_ids": expected_ids,
        "actual_ids": sorted(actual_ids),
        "complete": complete,
    }
    return gate


def evaluate_regression_gate(
    metrics: dict[str, Any],
    records: list[dict[str, Any]],
    *,
    complete_full_regression: bool,
    all_questions_approved: bool,
) -> dict[str, Any]:
    """Evaluate the exposed 16-case regression set without release semantics."""
    checks = {
        "complete_full_regression": complete_full_regression,
        "all_questions_approved": all_questions_approved,
        "gold_recall_at_10": _metric_at_least(metrics, "gold_recall_at_10", 0.95),
        "final_evidence_recall": _metric_at_least(
            metrics, "final_evidence_recall", 0.90
        ),
        "citation_integrity": metrics.get("citation_integrity", 0.0) == 1.0,
        "required_source_coverage": _metric_at_least(
            metrics, "required_source_coverage_answered", 0.97
        ),
        "required_identifiers": metrics.get("identifier_miss_count", 0) == 0,
        "identifier_hallucination_rate": _metric_below(
            metrics, "identifier_hallucination_rate", 0.03
        ),
        "wrong_version_evidence": metrics.get("wrong_version_evidence_count", 0) == 0,
        "forbidden_evidence": metrics.get("forbidden_evidence_count", 0) == 0,
        "answer_point_coverage": _metric_at_least(
            metrics, "answer_point_coverage", 0.90
        ),
        "critical_answer_points": metrics.get("critical_answer_point_miss_count")
        is not None
        and metrics["critical_answer_point_miss_count"] == 0,
        "no_contradictions": metrics.get("contradiction_count") is not None
        and metrics["contradiction_count"] == 0,
        "no_major_unsupported_claims": metrics.get("major_unsupported_claim_count")
        is not None
        and metrics["major_unsupported_claim_count"] == 0,
        "unhandled_exceptions": metrics.get("unhandled_exception_count", 0) == 0,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "note": (
            "Supporting 16-case exposed regression gate. It does not authorize acceptance or release."
        ),
    }


def _load_jsonl_with_partial_tail(path: Path) -> list[dict[str, Any]]:
    """Read JSONL while treating only an invalid final line as an interrupted write."""
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    values: list[dict[str, Any]] = []
    repair_tail = False
    for index, line in enumerate(lines):
        try:
            values.append(json.loads(line))
        except json.JSONDecodeError:
            if index != len(lines) - 1:
                raise
            repair_tail = True
    if repair_tail:
        path.write_text(
            "".join(
                json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n"
                for item in values
            ),
            encoding="utf-8",
        )
    return values


def verify_candidate_identity(project_root: Path, candidate_id: str) -> dict[str, Any]:
    from panda_agent.candidate import verify_candidate
    return verify_candidate(project_root, candidate_id)


class EvaluationRunStore:
    def __init__(
        self,
        root: Path,
        run_id: str,
        manifest: dict[str, Any],
        *,
        resume: bool = False,
        project_root: Path | None = None,
    ) -> None:
        self.run_dir = root / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.run_dir / "manifest.json"
        self.results_path = self.run_dir / "results.jsonl"
        self.attempts_path = self.run_dir / "attempts.jsonl"
        self.records_dir = self.run_dir / "records"
        self.records_dir.mkdir(exist_ok=True)
        self.project_root = project_root
        if self.manifest_path.exists():
            existing = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if not resume:
                raise FileExistsError(f"evaluation run already exists: {run_id}")
            if existing != manifest:
                self._verify_resumable_manifest_compatibility(existing, manifest)
        else:
            temporary_manifest = self.run_dir / ".manifest.json.tmp"
            temporary_manifest.write_text(
                json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            os.replace(temporary_manifest, self.manifest_path)

        self.successful_ids: set[str] = set()
        self.retryable_ids: set[str] = set()
        self.terminal_exception_ids: set[str] = set()
        self.completed_ids: set[str] = set()
        self.current_records: dict[str, dict[str, Any]] = {}

        for path in sorted(self.records_dir.glob("*.json")):
            try:
                rec = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                raise ValueError(f"corrupted or malformed evaluation record: {path}: {exc}") from exc
            if not isinstance(rec, dict) or "id" not in rec or not str(rec["id"]).strip():
                raise ValueError(f"malformed evaluation record missing valid id: {path}")
            self.current_records[str(rec["id"])] = rec

        if self.results_path.exists():
            for item in _load_jsonl_with_partial_tail(self.results_path):
                cid = str(item["id"])
                if cid not in self.current_records:
                    self.current_records[cid] = item

        # Canonical recovery from attempts ledger: replay durable ledger entries
        # so a crash after ledger append preserves the actual latest attempt
        if self.attempts_path.exists():
            for item in _load_jsonl_with_partial_tail(self.attempts_path):
                if isinstance(item, dict) and "id" in item and str(item["id"]).strip():
                    cid = str(item["id"])
                    self.current_records[cid] = item

        # Sync disk records with canonical ledger recovery state
        for cid, rec in self.current_records.items():
            record_path = self.records_dir / f"{cid}.json"
            needs_write = False
            if not record_path.exists():
                needs_write = True
            else:
                try:
                    on_disk = json.loads(record_path.read_text(encoding="utf-8"))
                    if on_disk != rec:
                        needs_write = True
                except Exception:
                    needs_write = True
            if needs_write:
                temp_path = self.records_dir / f".{cid}.json.tmp"
                temp_path.write_text(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
                os.replace(temp_path, record_path)

        self._sync_results_file()

        if resume and not self.attempts_path.exists() and self.current_records:
            self._seed_attempts_ledger_if_needed()

        for cid, rec in self.current_records.items():
            state = evaluation_record_state(rec)
            if state == "completed":
                self.successful_ids.add(cid)
                self.completed_ids.add(cid)
            elif state == "terminal_exception":
                self.terminal_exception_ids.add(cid)
                self.completed_ids.add(cid)
            elif state == "retryable_exception":
                self.retryable_ids.add(cid)

    def _seed_attempts_ledger_if_needed(self) -> None:
        """Seed attempts.jsonl with prior records if mutating/resuming a legacy run without an attempts ledger."""
        if not self.attempts_path.exists() and self.current_records:
            temp_path = self.run_dir / ".attempts.jsonl.tmp"
            with temp_path.open("w", encoding="utf-8", newline="\n") as stream:
                for cid in sorted(self.current_records.keys()):
                    attempt_record = dict(self.current_records[cid])
                    stream.write(
                        json.dumps(attempt_record, ensure_ascii=False, sort_keys=True) + "\n"
                    )
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_path, self.attempts_path)

    def _verify_resumable_manifest_compatibility(
        self, existing: dict[str, Any], manifest: dict[str, Any]
    ) -> None:
        """Permit ONLY lifecycle commit advance under verified candidate; fail closed on other drift."""
        if existing.get("official") and not (existing.get("candidate_id") or manifest.get("candidate_id")):
            raise ValueError(
                "unbound official lifecycle run cannot be resumed; candidate_id is required"
            )

        if existing.get("candidate_manifest_sha256") and manifest.get("candidate_manifest_sha256"):
            if existing["candidate_manifest_sha256"] != manifest["candidate_manifest_sha256"]:
                raise ValueError(
                    f"resumable run candidate manifest sha256 drifted: {existing['candidate_manifest_sha256']} != {manifest['candidate_manifest_sha256']}"
                )

        diff_keys = set()
        for k in existing.keys() | manifest.keys():
            if k in ("run_started_at",):
                continue
            if existing.get(k) != manifest.get(k):
                diff_keys.add(k)

        if not diff_keys:
            return

        if diff_keys != {"repository_identity"}:
            raise ValueError(
                f"evaluation manifest does not match the resumable run; drifted fields: {sorted(diff_keys)}"
            )

        existing_repo = existing.get("repository_identity") or {}
        new_repo = manifest.get("repository_identity") or {}

        if existing_repo.keys() != new_repo.keys():
            raise ValueError(
                f"resumable run repository identity fields drifted: {sorted(existing_repo.keys() ^ new_repo.keys())}"
            )

        if existing_repo.get("dirty") != new_repo.get("dirty") or new_repo.get("dirty"):
            raise ValueError("resumable run repository is dirty or dirty state changed")

        for k in existing_repo.keys() | new_repo.keys():
            if k in ("commit", "dirty"):
                continue
            if existing_repo.get(k) != new_repo.get(k):
                raise ValueError(
                    f"resumable run repository identity field '{k}' drifted: {existing_repo.get(k)!r} != {new_repo.get(k)!r}"
                )

        existing_commit = existing_repo.get("commit")
        new_commit = new_repo.get("commit")
        project_root = self.project_root or Path.cwd()

        if existing_commit != new_commit:
            if not existing_commit or not new_commit:
                raise ValueError("missing commit in repository identity for resumable run")
            ancestor = subprocess.run(
                ["git", "merge-base", "--is-ancestor", existing_commit, new_commit],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
            )
            if ancestor.returncode != 0:
                raise ValueError(
                    f"resumable run commit {existing_commit} is not an ancestor of current commit {new_commit}"
                )

        candidate_id = manifest.get("candidate_id") or existing.get("candidate_id")
        if not candidate_id:
            raise ValueError(
                "evaluation manifest commit changed, but no candidate identity could be resolved to verify immutability"
            )

        verification = verify_candidate_identity(project_root, candidate_id)
        if not verification.get("valid"):
            raise ValueError(
                f"evaluation resume failed: candidate {candidate_id} verification failed: {verification.get('mismatches')}"
            )

    def _sync_results_file(self) -> None:
        """Atomically sync one current result per case to results.jsonl."""
        temp_path = self.run_dir / ".results.jsonl.tmp"
        with temp_path.open("w", encoding="utf-8", newline="\n") as stream:
            for cid in sorted(self.current_records.keys()):
                stream.write(
                    json.dumps(self.current_records[cid], ensure_ascii=False, sort_keys=True)
                    + "\n"
                )
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, self.results_path)

    def record(self, record: dict[str, Any]) -> None:
        case_id = str(record["id"])
        if case_id in self.successful_ids:
            raise ValueError(f"evaluation case already successfully completed: {case_id}")
        if case_id in self.terminal_exception_ids:
            raise ValueError(f"evaluation case already terminal: {case_id}")

        self._seed_attempts_ledger_if_needed()

        attempt_record = dict(record)
        attempt_record.setdefault("attempted_at", datetime.now(timezone.utc).isoformat())
        record = attempt_record
        with self.attempts_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(
                json.dumps(attempt_record, ensure_ascii=False, sort_keys=True) + "\n"
            )
            stream.flush()
            os.fsync(stream.fileno())

        record_text = json.dumps(record, ensure_ascii=False, sort_keys=True)
        record_path = self.records_dir / f"{case_id}.json"
        temporary_path = self.records_dir / f".{case_id}.json.tmp"
        temporary_path.write_text(record_text + "\n", encoding="utf-8")
        os.replace(temporary_path, record_path)

        self.current_records[case_id] = record
        self._sync_results_file()

        state = evaluation_record_state(record)
        if state == "completed":
            self.successful_ids.add(case_id)
            self.completed_ids.add(case_id)
            self.retryable_ids.discard(case_id)
        elif state == "terminal_exception":
            self.terminal_exception_ids.add(case_id)
            self.completed_ids.add(case_id)
            self.retryable_ids.discard(case_id)
        elif state == "retryable_exception":
            self.retryable_ids.add(case_id)
            self.completed_ids.discard(case_id)

    def cumulative_usage(self) -> tuple[int, int]:
        """Return total (model_calls, token_usage) across all attempts in attempts.jsonl."""
        if self.attempts_path.exists():
            attempts = _load_jsonl_with_partial_tail(self.attempts_path)
            calls = sum(int(a.get("model_calls", 0)) for a in attempts)
            tokens = sum(int(a.get("token_usage", 0)) for a in attempts)
            return calls, tokens
        calls = sum(int(r.get("model_calls", 0)) for r in self.current_records.values())
        tokens = sum(int(r.get("token_usage", 0)) for r in self.current_records.values())
        return calls, tokens


def load_run_records(run_dir: Path) -> list[dict[str, Any]]:
    """Load atomic per-case records, with JSONL fallback for legacy runs."""
    merged: dict[str, dict[str, Any]] = {}
    results_path = run_dir / "results.jsonl"
    if results_path.exists():
        for item in _load_jsonl_with_partial_tail(results_path):
            merged[str(item["id"])] = item
    records_dir = run_dir / "records"
    record_paths = sorted(records_dir.glob("*.json")) if records_dir.is_dir() else []
    for path in record_paths:
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ValueError(f"corrupted or malformed evaluation record: {path}: {exc}") from exc
        if not isinstance(item, dict) or "id" not in item or not str(item["id"]).strip():
            raise ValueError(f"malformed evaluation record missing valid id: {path}")
        merged[str(item["id"])] = item
    return [merged[key] for key in sorted(merged)]
