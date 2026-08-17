"""Canonical M0 data contracts shared by ingestion, retrieval, and generation."""

from __future__ import annotations

import hashlib
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceKind(StrEnum):
    GIT_REPOSITORY = "git_repository"
    PDF = "pdf"
    WEB_DOCUMENTATION = "web_documentation"


class AuthorityLevel(StrEnum):
    PRIMARY = "primary"
    OPERATIONAL = "operational"
    DERIVED = "derived"
    CANDIDATE = "candidate"


class ReviewStatus(StrEnum):
    ACCEPTED = "accepted"
    PENDING = "pending"
    REJECTED = "rejected"


class CreationMethod(StrEnum):
    CURATED = "curated"
    STATIC_ANALYSIS = "static_analysis"
    EXPLICIT_REFERENCE = "explicit_reference"
    LLM_PROPOSAL = "llm_proposal"


class ResolutionStatus(StrEnum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED_EXTERNAL = "unresolved_external"
    UNRESOLVED_INTERNAL = "unresolved_internal"


class QAStatus(StrEnum):
    ANSWERED = "answered"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    VERSION_CONFLICT = "version_conflict"
    CLARIFICATION_REQUIRED = "clarification_required"


class SourceVersion(StrictModel):
    source_version_id: str
    source_id: str
    source_kind: SourceKind
    version_label: str
    content_hash: str
    captured_at: datetime
    parser_name: str | None = None
    parser_version: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceLocator(StrictModel):
    path: str | None = None
    symbol: str | None = None
    start_line: int | None = Field(default=None, ge=1)
    end_line: int | None = Field(default=None, ge=1)
    pdf_page: int | None = Field(default=None, ge=1)
    printed_page: str | None = None
    section_path: list[str] = Field(default_factory=list)
    url: str | None = None
    snapshot_date: str | None = None

    @model_validator(mode="after")
    def validate_line_range(self) -> "SourceLocator":
        if self.start_line and self.end_line and self.end_line < self.start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return self


class KnowledgeObject(StrictModel):
    object_id: str
    object_type: str
    source_id: str
    source_version_id: str
    title: str
    text: str
    authority_level: AuthorityLevel
    locator: SourceLocator
    parent_object_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    canonical_locator: str | None = None
    chunk_parent_id: str | None = None
    token_count: int = Field(default=0, ge=0)
    embedding_eligible: bool = True


class RelationEdge(StrictModel):
    edge_id: str
    subject_id: str
    predicate: str
    object_id: str
    source_version_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    creation_method: CreationMethod
    review_status: ReviewStatus
    evidence_object_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RelationCandidate(StrictModel):
    candidate_id: str
    subject_id: str
    predicate: str
    raw_target: str
    source_version_ids: list[str] = Field(default_factory=list)
    resolution_scope: str
    candidate_object_ids: list[str] = Field(default_factory=list)
    resolution_status: ResolutionStatus = ResolutionStatus.UNRESOLVED_INTERNAL
    confidence: float = Field(ge=0.0, le=1.0)
    creation_method: CreationMethod = CreationMethod.STATIC_ANALYSIS
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeAlias(StrictModel):
    alias_id: str
    alias_text: str
    normalized_alias: str
    target_object_id: str
    alias_kind: str
    source_version_id: str
    review_status: ReviewStatus
    provenance_object_ids: list[str] = Field(min_length=1)
    correction_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowStep(StrictModel):
    workflow_id: str
    step_id: str
    name: str
    entrypoint_object_id: str | None = None
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    predecessor_step_ids: list[str] = Field(default_factory=list)
    successor_step_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalPlan(StrictModel):
    intent: str
    secondary_intents: list[str] = Field(default_factory=list)
    routing_method: str = "llm"
    target_repositories: list[str] = Field(default_factory=list)
    resolved_versions: dict[str, str] = Field(default_factory=dict)
    version_conflicts: list[str] = Field(default_factory=list)
    concepts: list[str] = Field(default_factory=list)
    symbols: list[str] = Field(default_factory=list)
    concept_scopes: dict[str, str] = Field(default_factory=dict)
    source_budgets: dict[str, float]
    required_source_types: list[str] = Field(default_factory=list)
    resolved_aliases: dict[str, str] = Field(default_factory=dict)
    premise_corrections: list[str] = Field(default_factory=list)
    paper_page_hints: dict[str, list[int]] = Field(default_factory=dict)
    analysis_diagnostics: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_source_budgets(self) -> "RetrievalPlan":
        if not self.source_budgets:
            raise ValueError("source_budgets cannot be empty")
        if any(value < 0 for value in self.source_budgets.values()):
            raise ValueError("source budgets cannot be negative")
        if abs(sum(self.source_budgets.values()) - 1.0) > 1e-6:
            raise ValueError("source budgets must sum to 1.0")
        return self


class Evidence(StrictModel):
    evidence_id: str
    object_id: str
    source_id: str
    source_version_id: str
    text: str
    locator: SourceLocator
    retrieval_channels: list[str]
    score: float
    authority_level: AuthorityLevel


class ClaimCitation(StrictModel):
    claim_id: str
    claim_text: str
    evidence_ids: list[str] = Field(min_length=1)


class QAResult(StrictModel):
    status: QAStatus
    answer: str
    claims: list[ClaimCitation] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    resolved_versions: dict[str, str] = Field(default_factory=dict)
    verification_errors: list[str] = Field(default_factory=list)


class IngestionReport(StrictModel):
    manifest_hash: str
    object_count: int
    relation_count: int
    relation_candidate_count: int = 0
    alias_count: int = 0
    workflow_count: int
    parse_errors: list[dict[str, Any]] = Field(default_factory=list)
    output_hashes: dict[str, str] = Field(default_factory=dict)


def stable_id(*components: str, prefix: str) -> str:
    normalized = "\x1f".join(component.strip() for component in components)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}.{digest}"
