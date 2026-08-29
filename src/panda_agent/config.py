"""Typed configuration loading for the PANDA QA agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import os
from dataclasses import dataclass

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


FASTEMBED_MODEL_PATH_ENV = "PANDA_FASTEMBED_MODEL_PATH"
DEFAULT_FASTEMBED_MODEL_PATH = Path("data/runtime/fastembed/bm25")
SPARSE_VECTOR_NAME = "sparse"
SPARSE_VECTOR_MODIFIER = "idf"
BM25_MODEL_NAME = "Qdrant/bm25"
BM25_LANGUAGE = "english"
BM25_K = 1.2
BM25_B = 0.75
BM25_AVG_LEN = 256.0
BM25_TOKEN_MAX_LENGTH = 40
BM25_DISABLE_STEMMER = False
BM25_TOKENIZER = "SimpleTokenizer"
BM25_STEMMER = "SnowballStemmer"
BM25_HASH = "mmh3.hash"


class FastEmbedConfigurationError(ValueError):
    """Raised when the local FastEmbed runtime asset is unavailable."""


def resolve_fastembed_model_path(project_root: str | Path) -> Path:
    """Resolve the configured BM25 model directory from the project root.

    Relative values are intentionally joined to ``project_root`` rather than
    the process working directory.  The runtime is local-only, so a missing
    model directory is a configuration error instead of a signal to download
    or fall back to another model.
    """
    root = Path(project_root).expanduser().resolve()
    configured = os.getenv(FASTEMBED_MODEL_PATH_ENV)
    raw_path = Path(configured).expanduser() if configured else DEFAULT_FASTEMBED_MODEL_PATH
    model_path = raw_path if raw_path.is_absolute() else root / raw_path
    model_path = model_path.resolve()
    if not model_path.is_dir():
        raise FastEmbedConfigurationError(
            f"FastEmbed model path does not exist or is not a directory: {model_path}"
        )
    return model_path


@dataclass(frozen=True)
class FastEmbedSettings:
    """Typed, fail-closed settings for the local FastEmbed BM25 model."""

    model_path: Path
    model_name: str = BM25_MODEL_NAME
    language: str = BM25_LANGUAGE
    vector_name: str = SPARSE_VECTOR_NAME
    local_files_only: bool = True
    k: float = BM25_K
    b: float = BM25_B
    avg_len: float = BM25_AVG_LEN
    token_max_length: int = BM25_TOKEN_MAX_LENGTH
    disable_stemmer: bool = BM25_DISABLE_STEMMER

    @classmethod
    def from_env(cls, project_root: str | Path) -> "FastEmbedSettings":
        return cls(model_path=resolve_fastembed_model_path(project_root))


class RepositoryConfig(StrictModel):
    repo_id: str
    name: str
    url: str
    ref: str
    commit_sha: str | None = None
    role: str
    base_repo_id: str | None = None
    feature_start_commit: str | None = None


class PaperConfig(StrictModel):
    doc_id: str
    title: str
    path: str
    sha256: str | None = None
    related_repositories: list[str] = Field(default_factory=list)


class WebDocumentConfig(StrictModel):
    doc_id: str
    name: str
    url: str
    snapshot_date: str | None = None
    expected_snapshot_hash: str
    expected_html_page_count: int = Field(ge=1)
    expected_asset_count: int = Field(ge=0)
    required_paths: list[str] = Field(default_factory=list)
    role: str
    authoritative_for_refs: list[str] = Field(default_factory=list)
    not_authoritative_for_refs: list[str] = Field(default_factory=list)


class CorporaConfig(StrictModel):
    schema_version: str
    repositories: list[RepositoryConfig]
    papers: list[PaperConfig]
    web_documents: list[WebDocumentConfig]

    @model_validator(mode="after")
    def validate_references(self) -> "CorporaConfig":
        repo_ids = [item.repo_id for item in self.repositories]
        if len(repo_ids) != len(set(repo_ids)):
            raise ValueError("repository IDs must be unique")
        doc_ids = [item.doc_id for item in [*self.papers, *self.web_documents]]
        if len(doc_ids) != len(set(doc_ids)):
            raise ValueError("document IDs must be unique")
        unknown = {
            repo_id
            for paper in self.papers
            for repo_id in paper.related_repositories
            if repo_id not in repo_ids
        }
        if unknown:
            raise ValueError(f"papers reference unknown repositories: {sorted(unknown)}")
        return self


class RelationDefinition(StrictModel):
    name: str
    description: str


class RelationOntology(StrictModel):
    schema_version: str
    predicates: list[RelationDefinition]

    @model_validator(mode="after")
    def validate_unique_predicates(self) -> "RelationOntology":
        names = [item.name for item in self.predicates]
        if len(names) != len(set(names)):
            raise ValueError("relation predicates must be unique")
        return self


class KnowledgeSchema(StrictModel):
    schema_version: str
    object_types: dict[str, list[str]]
    required_base_fields: list[str]
    stable_id_components: list[str]
    derived_type_suffixes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_object_types(self) -> "KnowledgeSchema":
        values = [value for group in self.object_types.values() for value in group]
        if len(values) != len(set(values)):
            raise ValueError("knowledge object types must be unique across groups")
        mandatory = {"object_id", "object_type", "source_id", "source_version_id"}
        missing = mandatory - set(self.required_base_fields)
        if missing:
            raise ValueError(f"knowledge schema is missing mandatory fields: {sorted(missing)}")
        return self


class SeedRelationConfig(StrictModel):
    subject_id: str
    predicate: str
    object_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    creation_method: str
    review_status: str
    evidence_note: str
    source_version_ids: list[str] = Field(default_factory=list)
    evidence_object_ids: list[str] = Field(default_factory=list)
    evidence_paths: list[str] = Field(default_factory=list)
    evidence_source_ids: list[str] = Field(default_factory=list)
    deferred_requirement: str | None = None


class SeedRelationsConfig(StrictModel):
    schema_version: str
    relations: list[SeedRelationConfig]


class SeedObjectConfig(StrictModel):
    object_id: str
    object_type: str
    title: str
    text: str
    source_id: str = "curated_panda_domain"
    source_version_id: str = "curated_panda_domain@1.0"
    authority_level: str = "derived"
    embedding_eligible: bool = True
    identity_role: str | None = None
    parent_object_id: str | None = None

    @model_validator(mode="after")
    def validate_identity_role(self) -> "SeedObjectConfig":
        allowed = {"canonical", "source_native"}
        if self.identity_role is not None and self.identity_role not in allowed:
            raise ValueError(
                f"seed identity_role must be one of {sorted(allowed)} or omitted: "
                f"{self.object_id}={self.identity_role!r}"
            )
        return self


class SeedObjectsConfig(StrictModel):
    schema_version: str
    objects: list[SeedObjectConfig]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "SeedObjectsConfig":
        values = [item.object_id for item in self.objects]
        if len(values) != len(set(values)):
            raise ValueError("seed object IDs must be unique")
        return self


class SeedWorkflowConfig(StrictModel):
    workflow_id: str
    step_id: str
    name: str
    entrypoint_object_id: str | None = None
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    predecessor_step_ids: list[str] = Field(default_factory=list)
    successor_step_ids: list[str] = Field(default_factory=list)


class SeedWorkflowsConfig(StrictModel):
    schema_version: str
    steps: list[SeedWorkflowConfig]

    @model_validator(mode="after")
    def validate_unique_step_ids(self) -> "SeedWorkflowsConfig":
        values = [item.step_id for item in self.steps]
        if len(values) != len(set(values)):
            raise ValueError("seed workflow step IDs must be unique")
        return self


class AliasConfig(StrictModel):
    alias_text: str
    target_object_id: str
    alias_kind: str
    source_id: str
    source_version_id: str
    review_status: str = "accepted"
    provenance_paths: list[str] = Field(min_length=1)
    correction_message: str | None = None


class AliasesConfig(StrictModel):
    schema_version: str
    aliases: list[AliasConfig]

    @model_validator(mode="after")
    def validate_unique_aliases(self) -> "AliasesConfig":
        values = [(item.source_version_id, item.alias_text.casefold()) for item in self.aliases]
        if len(values) != len(set(values)):
            raise ValueError("aliases must be unique within a source version")
        return self


class IntentPolicy(StrictModel):
    source_budgets: dict[str, float]
    required_sources: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_budgets(self) -> "IntentPolicy":
        if any(value < 0 for value in self.source_budgets.values()):
            raise ValueError("source budgets cannot be negative")
        if abs(sum(self.source_budgets.values()) - 1.0) > 1e-6:
            raise ValueError("source budgets must sum to 1.0")
        return self


class RetrievalPolicies(StrictModel):
    schema_version: str
    candidate_pool_per_channel: int = Field(gt=0)
    final_evidence_limit: int = Field(gt=0)
    max_relation_hops: int = Field(ge=0, le=3)
    max_targeted_retrievals: int = Field(ge=0, le=2)
    fusion_method: str
    intent_routes: dict[str, list[str]] = Field(default_factory=dict)
    intents: dict[str, IntentPolicy]


class QueryExpansionRule(StrictModel):
    """Reviewed domain vocabulary used to make implicit identifiers explicit."""

    rule_id: str
    triggers: list[str] = Field(min_length=1)
    symbols: list[str] = Field(default_factory=list)
    concepts: list[str] = Field(default_factory=list)
    repositories: list[str] = Field(default_factory=list)
    paper_page_hints: dict[str, list[int]] = Field(default_factory=dict)


class QueryExpansions(StrictModel):
    schema_version: str
    rules: list[QueryExpansionRule]

    @model_validator(mode="after")
    def validate_unique_rule_ids(self) -> "QueryExpansions":
        values = [item.rule_id for item in self.rules]
        if len(values) != len(set(values)):
            raise ValueError("query expansion rule IDs must be unique")
        return self


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"configuration must be a mapping: {path}")
    return value


def load_corpora(path: str | Path) -> CorporaConfig:
    return CorporaConfig.model_validate(load_yaml(path))


def load_relation_ontology(path: str | Path) -> RelationOntology:
    return RelationOntology.model_validate(load_yaml(path))


def load_knowledge_schema(path: str | Path) -> KnowledgeSchema:
    return KnowledgeSchema.model_validate(load_yaml(path))


def load_seed_relations(path: str | Path) -> SeedRelationsConfig:
    return SeedRelationsConfig.model_validate(load_yaml(path))


def load_seed_objects(path: str | Path) -> SeedObjectsConfig:
    return SeedObjectsConfig.model_validate(load_yaml(path))


def load_seed_workflows(path: str | Path) -> SeedWorkflowsConfig:
    return SeedWorkflowsConfig.model_validate(load_yaml(path))


def load_aliases(path: str | Path) -> AliasesConfig:
    return AliasesConfig.model_validate(load_yaml(path))


def load_retrieval_policies(path: str | Path) -> RetrievalPolicies:
    return RetrievalPolicies.model_validate(load_yaml(path))


def load_query_expansions(path: str | Path) -> QueryExpansions:
    return QueryExpansions.model_validate(load_yaml(path))


def corpora_config_hash(config: CorporaConfig) -> str:
    """Hash the validated corpus contract, independent of YAML formatting."""
    canonical = json.dumps(
        config.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_seed_predicates(
    seeds: SeedRelationsConfig, ontology: RelationOntology
) -> None:
    allowed = {item.name for item in ontology.predicates}
    unknown = sorted({item.predicate for item in seeds.relations} - allowed)
    if unknown:
        raise ValueError(f"seed relations use unknown predicates: {unknown}")
