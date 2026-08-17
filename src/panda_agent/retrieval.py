"""M4 multi-channel retrieval with version filtering, RRF, and quotas."""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from qdrant_client import models

from panda_agent.config import load_query_expansions, load_retrieval_policies
from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.models import AuthorityLevel, Evidence, RetrievalPlan, SourceLocator, stable_id
from panda_agent.prompts import QUERY_ANALYZER_SYSTEM_PROMPT, RERANK_SYSTEM_PROMPT
from panda_agent.sparse import create_sparse_encoder
from panda_agent.storage import Storage


ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": ["installation", "usage", "algorithm_theory", "algorithm_implementation", "api", "data_flow", "module_structure", "troubleshooting"]},
        "target_repositories": {"type": "array", "items": {"type": "string", "enum": ["luminosityfit", "pandaroot", "restgas_determination"]}},
        "concepts": {"type": "array", "items": {"type": "string"}},
        "symbols": {"type": "array", "items": {"type": "string"}},
        "requested_versions": {"type": "object", "additionalProperties": {"type": "string"}},
        "concept_scopes": {"type": "object", "additionalProperties": {"type": "string"}},
    },
    "required": ["intent", "target_repositories", "concepts", "symbols", "requested_versions", "concept_scopes"],
    "additionalProperties": False,
}


def _analysis_schema(*, intent_is_fixed: bool) -> dict[str, Any]:
    """Return the smallest response contract for the remaining analyzer work."""
    properties = dict(ANALYSIS_SCHEMA["properties"])
    required = list(ANALYSIS_SCHEMA["required"])
    if intent_is_fixed:
        properties.pop("intent")
        required.remove("intent")
    return {**ANALYSIS_SCHEMA, "properties": properties, "required": required}


def _has_explicit_repository_reference(question: str, repository: str) -> bool:
    """Match a manifest repository ID without accepting a larger containing token."""
    parts = [re.escape(part) for part in repository.split("_")]
    pattern = rf"(?<![a-z0-9]){'[\\s_-]?'.join(parts)}(?![a-z0-9])"
    return re.search(pattern, question, re.IGNORECASE) is not None


@dataclass
class DeterministicQueryParse:
    """Known query facts extracted without semantic inference."""

    intent: str | None = None
    target_repositories: list[str] = field(default_factory=list)
    requested_versions: dict[str, str] = field(default_factory=dict)
    explicit_shas: list[str] = field(default_factory=list)
    version_repositories: list[str] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    fixed_concept_scopes: dict[str, str] = field(default_factory=dict)
    fallback_concept_scopes: dict[str, str] = field(default_factory=dict)
    resolved_aliases: dict[str, str] = field(default_factory=dict)
    premise_corrections: list[str] = field(default_factory=list)
    paper_page_hints: dict[str, list[int]] = field(default_factory=dict)
    matched_expansion_rules: list[str] = field(default_factory=list)
    provenance: dict[str, list[dict[str, str]]] = field(default_factory=dict)

    def record(
        self, field_name: str, *, source: str, rule: str, value: str | None = None,
        ownership: str | None = None,
    ) -> None:
        entry = {"source": source, "rule": rule}
        if value is not None:
            entry["value"] = value
        if ownership is not None:
            entry["ownership"] = ownership
        self.provenance.setdefault(field_name, []).append(entry)

    def analyzer_context(self, semantic_output_fields: list[str]) -> dict[str, Any]:
        fixed: dict[str, Any] = {}
        if self.intent is not None:
            fixed["intent"] = self.intent
        if self.fixed_concept_scopes:
            fixed["concept_scopes"] = self.fixed_concept_scopes
        for field_name, value in {
            "requested_versions": self.requested_versions,
            "explicit_sha_tokens": self.explicit_shas,
            "resolved_aliases": self.resolved_aliases,
            "premise_corrections": self.premise_corrections,
            "matched_expansion_rules": self.matched_expansion_rules,
            "paper_page_hints": self.paper_page_hints,
        }.items():
            if value:
                fixed[field_name] = value
        known_partial = {
            "target_repositories": self.target_repositories,
            "symbols": self.symbols,
            "concepts": self.concepts,
        }
        known_partial = {key: value for key, value in known_partial.items() if value}
        unresolved_semantics: dict[str, str] = {}
        for field_name in semantic_output_fields:
            if field_name in known_partial:
                unresolved_semantics[field_name] = "augment_known_partial"
            elif field_name == "requested_versions" and self.requested_versions:
                unresolved_semantics[field_name] = "augment_fixed_keys"
            elif field_name == "concept_scopes" and self.fixed_concept_scopes:
                unresolved_semantics[field_name] = "resolve_remaining_scope_keys_after_fixed_constraints"
            elif field_name == "concept_scopes" and self.fallback_concept_scopes:
                unresolved_semantics[field_name] = "resolve_remaining_scope_keys_with_fallback"
            else:
                unresolved_semantics[field_name] = "resolve"
        return {
            "fixed": fixed,
            "fallback": {"concept_scopes": self.fallback_concept_scopes},
            "known_partial": known_partial,
            "semantic_output_fields": semantic_output_fields,
            "unresolved_semantics": unresolved_semantics,
            "provenance": self.provenance,
        }


def route_high_confidence_intent(
    question: str, routes: dict[str, list[str]] | None = None
) -> str | None:
    """Route explicit operational wording before asking the LLM classifier."""
    lowered = question.casefold()
    if re.search(
        r"(?:recover|reconstruct|restore).*\b(?:deleted|removed)\b|"
        r"\b(?:deleted|removed)\b.*(?:recover|reconstruct|restore)",
        lowered,
    ):
        return "troubleshooting"
    routes = routes or {
        "troubleshooting": [r"\btroubleshoot", r"\bdebug\b", r"\berror\b", r"\bfail(?:s|ed|ure)?\b", r"\bmissing\b", r"\bcannot\b", r"\bwrong\b", r"\bwhy might\b", "what should i inspect", "排查", "报错", "失败", "缺失"],
        "installation": [r"\binstall", "environment variable", "pandaroot environment", "cernvm-fs", "cvmfs", "cmake error", "docker", "安装", "环境变量"],
        "data_flow": [r"\btrace\b", "data flow", r"\bproduces\b", r"\bconsumes\b", "into pid_final", "passed to", "read into", "写出", "读入", "数据流", "谁产生", "谁消费", "如何进入", "如何连接"],
        "api": [r"\bwhere (?:is|does|can)\b", r"\bdefined\b", r"\bsignature\b", r"\bapi\b", r"\bwhich (?:macro|source|file|class|method|function)\b", r"\blocate\b", "哪个宏", "哪个类", "哪个函数"],
        "algorithm_implementation": [r"\bhow is .+ implemented\b", r"\bhow does .+ (?:form|create|work|use)\b", r"\bimplementation\b", r"event_poca.*(?:event|事件).*(?:read|读)", r"extrapolat.*event.?poca", "如何实现", "由哪些类实现", "如何回传", "如何形成", "如何用于", "实现层面", "代码实现"],
        "algorithm_theory": [r"\btheoretical\b", r"\bconceptual\b", r"\bwhy does\b", r"\bwhy is\b", "理论", "原理", "为什么需要", "物理意义"],
        "module_structure": [r"\bmodule structure\b", r"\bmodule boundary\b", r"\bmodule.*connect", r"\bcomponents?\b", r"\blayers?\b", "模块结构", "模块边界", "模块如何连接", "由哪些模块"],
        "usage": [r"\bhow (?:do|can) i (?:run|use|invoke|start|select)\b", r"\bhow is .+ (?:supplied|provided|documented)\b", r"\bwhat is the documented .+ sequence\b", r"\busage\b", "如何运行", "如何使用", "怎么运行", "如何提供", "如何供给"],
    }
    priority = (
        "troubleshooting", "installation", "algorithm_implementation", "api",
        "usage", "module_structure", "data_flow", "algorithm_theory",
    )
    for intent in priority:
        patterns = [
            *routes.get(intent, []),
            *routes.get(f"{intent}_extra", []),
        ]
        if any(re.search(pattern, lowered) for pattern in patterns):
            return intent
    return None


def _evidence(payload: dict[str, Any], score: float, channels: list[str]) -> Evidence:
    return Evidence(
        evidence_id=stable_id(payload["object_id"], *sorted(channels), prefix="evidence"),
        object_id=payload["object_id"], source_id=payload["source_id"],
        source_version_id=payload["source_version_id"], text=payload.get("text", ""),
        locator=SourceLocator.model_validate(payload.get("locator") or {}),
        retrieval_channels=channels, score=score,
        authority_level=AuthorityLevel(payload.get("authority_level", "primary")),
    )


def _source_type_of(item: dict[str, Any]) -> str:
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


def select_final_evidence(
    ordered: list[str],
    payloads: dict[str, dict[str, Any]],
    scores: dict[str, float],
    channels: dict[str, list[str]],
    plan: RetrievalPlan,
    final_evidence_limit: int,
    mandatory_symbol_ids: set[str],
) -> tuple[list[Evidence], list[dict[str, Any]], list[dict[str, Any]]]:
    """Select final evidence with a two-pass hard-budget plus required backfill.

    Pass 1 applies the original hard budgets (duplicate locator, per-source cap,
    per-type cap, mandatory exact-symbol exemption) without any soft admission.
    Pass 2 runs only when the hard pass left unused evidence capacity; it backfills
    Pass-1 budget-rejected candidates in original canonical order if they are
    high-ranked, distinct, and from a required source type.  Backfill count is
    naturally bounded by ``final_evidence_limit - hard_pass_selected_count``.
    """
    selected: list[Evidence] = []
    per_source: dict[str, int] = defaultdict(int)
    per_type: dict[str, int] = defaultdict(int)
    max_per_source = max(2, math.ceil(final_evidence_limit / 3))
    type_caps = {
        key: max(1, math.ceil(value * final_evidence_limit))
        for key, value in plan.source_budgets.items()
    }
    required_types = set(plan.required_source_types)
    seen_locator: set[str] = set()
    hard_rejected: list[dict[str, Any]] = []
    duplicate_rejected: list[dict[str, Any]] = []

    # Pass 1: hard-budget allocation only.
    for rank, object_id in enumerate(ordered, 1):
        item = payloads[object_id]
        raw_locator = item.get("locator") or {}
        locator = json.dumps(raw_locator, sort_keys=True)
        if not any(value not in (None, "", [], {}) for value in raw_locator.values()):
            locator = f"object:{object_id}"
        source_type = _source_type_of(item)
        if locator in seen_locator:
            duplicate_rejected.append({"object_id": object_id, "reason": "duplicate_locator"})
            continue
        source_violated = (
            object_id not in mandatory_symbol_ids
            and per_source[item["source_id"]] >= max_per_source
        )
        type_violated = (
            object_id not in mandatory_symbol_ids
            and per_type[source_type] >= type_caps.get(source_type, final_evidence_limit)
        )
        if source_violated or type_violated:
            reason = (
                "source_diversity_cap_and_source_budget_cap"
                if source_violated and type_violated
                else "source_diversity_cap"
                if source_violated
                else "source_budget_cap"
            )
            hard_rejected.append(
                {
                    "object_id": object_id,
                    "canonical_rank": rank,
                    "original_block_reason": reason,
                    "source_id": item["source_id"],
                    "source_type": source_type,
                }
            )
            continue
        seen_locator.add(locator)
        per_source[item["source_id"]] += 1
        per_type[source_type] += 1
        selected.append(_evidence(item, scores[object_id], channels[object_id]))
        if len(selected) >= final_evidence_limit:
            break

    # Pass 2: required-source backfill using only unused total evidence capacity.
    backfill_admissions: list[dict[str, Any]] = []
    if len(selected) < final_evidence_limit:
        backfill_admitted_ids: set[str] = set()
        for rejected in hard_rejected:
            if len(selected) >= final_evidence_limit:
                break
            object_id = rejected["object_id"]
            if rejected["canonical_rank"] > final_evidence_limit:
                continue
            if rejected["source_type"] not in required_types:
                continue
            item = payloads[object_id]
            raw_locator = item.get("locator") or {}
            locator = json.dumps(raw_locator, sort_keys=True)
            if not any(value not in (None, "", [], {}) for value in raw_locator.values()):
                locator = f"object:{object_id}"
            if locator in seen_locator:
                continue
            seen_locator.add(locator)
            per_source[item["source_id"]] += 1
            per_type[rejected["source_type"]] += 1
            selected.append(_evidence(item, scores[object_id], channels[object_id]))
            backfill_admitted_ids.add(object_id)
            backfill_admissions.append(
                {
                    "object_id": object_id,
                    "canonical_rank": rejected["canonical_rank"],
                    "original_block_reason": rejected["original_block_reason"],
                    "source_id": item["source_id"],
                    "source_type": rejected["source_type"],
                    "admission_phase": "required_source_backfill",
                }
            )

    final_excluded = duplicate_rejected + [
        rejected
        for rejected in hard_rejected
        if rejected["object_id"] not in {admission["object_id"] for admission in backfill_admissions}
    ]
    return selected, final_excluded, backfill_admissions


class Retriever:
    def __init__(self, project_root: Path, *, storage: Storage | None = None, vertex: VertexAIClient | None = None) -> None:
        self.project_root = Path(project_root).resolve()
        self.storage = storage or Storage()
        self.vertex = vertex or VertexAIClient(VertexSettings.from_env())
        self.policies = load_retrieval_policies(self.project_root / "configs" / "retrieval_policies.yaml")
        self.query_expansions = load_query_expansions(self.project_root / "configs" / "query_expansions.yaml")
        self.sparse, self.sparse_receipt = create_sparse_encoder(self.project_root)
        self.storage.require_sparse_receipt(self.sparse_receipt)
        self.sparse_vector_name = self.sparse_receipt.vector_name
        manifest = json.loads((self.project_root / "data" / "manifests" / "source_manifest.json").read_text(encoding="utf-8"))
        self.fixed_versions = {item["repo_id"]: item["commit_sha"] for item in manifest["repositories"]}
        self.fixed_refs = {item["repo_id"]: item["ref"] for item in manifest["repositories"]}
        self._paper_versions = {item["doc_id"]: item["sha256"] for item in manifest["papers"]}
        self.context_sources = [item["doc_id"] for item in [*manifest["papers"], *manifest["web_documents"]]]
        self.web_version_tokens = {
            match.group(0).lower()
            for item in manifest["web_documents"]
            for match in re.finditer(r"\b\d{4}(?:-\d{2}-\d{2})?-dev\b", item["entry_url"], re.IGNORECASE)
        }

    def _preparse(self, question: str) -> DeterministicQueryParse:
        """Collect only existing raw-query and reviewed knowledge before analysis."""
        parsed = DeterministicQueryParse()
        lowered = question.casefold()

        routed_intent = route_high_confidence_intent(
            question, getattr(self.policies, "intent_routes", None)
        )
        if routed_intent is not None:
            parsed.intent = routed_intent
            parsed.record("intent", source="deterministic_route", rule=routed_intent, value=routed_intent, ownership="fixed")

        named_repositories = [
            repo for repo in self.fixed_versions
            if _has_explicit_repository_reference(question, repo)
        ]
        for repo in named_repositories:
            parsed.target_repositories.append(repo)
            parsed.record("target_repositories", source="explicit_query_reference", rule="manifest_repo_id", value=repo, ownership="known_partial")

        if any(term in lowered for term in ("event_poca", "poca_vertex_file", "restgas_profile")):
            parsed.target_repositories.append("restgas_determination")
            parsed.record("target_repositories", source="legacy_query_rule", rule="restgas_event_poca_terms", value="restgas_determination", ownership="known_partial")

        if "back propagation" in lowered or "回传" in question or "反向传播" in question:
            value = "lmd_to_ip" if "lmd" in lowered else "target_track_to_event_poca"
            parsed.fallback_concept_scopes["back_propagation"] = value
            parsed.record("concept_scopes", source="deterministic_scope", rule="back_propagation", value=value, ownership="fallback")
        if "efficiency" in lowered or "效率" in question:
            value = "longitudinal_profile" if any(term in lowered for term in ("restgas", "profile", "pvz")) else "angular_acceptance"
            parsed.fallback_concept_scopes["efficiency"] = value
            parsed.record("concept_scopes", source="deterministic_scope", rule="efficiency", value=value, ownership="fallback")
        if "angular acceptance" in lowered and "longitudinal efficiency" in lowered:
            parsed.fixed_concept_scopes["efficiency"] = "angular_acceptance_vs_longitudinal_profile"
            parsed.record("concept_scopes", source="deterministic_scope", rule="acceptance_efficiency_comparison", value="angular_acceptance_vs_longitudinal_profile", ownership="fixed")
        if "point-like acceptance" in lowered and "restgas effective acceptance" in lowered:
            parsed.fixed_concept_scopes["acceptance"] = "point_like_vs_restgas_effective"
            parsed.record("concept_scopes", source="deterministic_scope", rule="point_like_restgas_comparison", value="point_like_vs_restgas_effective", ownership="fixed")
        if "lmd-to-ip" in lowered and "event-poca" in lowered:
            parsed.fixed_concept_scopes["back_propagation"] = "lmd_to_ip_vs_target_track_to_event_poca"
            parsed.record("concept_scopes", source="deterministic_scope", rule="back_propagation_comparison", value="lmd_to_ip_vs_target_track_to_event_poca", ownership="fixed")

        try:
            with self.storage.connect() as connection:
                alias_rows = connection.execute(
                    "SELECT alias_text,target_object_id,payload FROM knowledge_aliases WHERE review_status='accepted'"
                ).fetchall()
            for alias_text, target_object_id, payload in alias_rows:
                if alias_text.casefold() in lowered:
                    parsed.resolved_aliases[alias_text] = target_object_id
                    parsed.record("resolved_aliases", source="accepted_alias", rule="review_status=accepted", value=alias_text, ownership="fixed")
                    if payload.get("correction_message"):
                        parsed.premise_corrections.append(payload["correction_message"])
                        parsed.record("premise_corrections", source="accepted_alias", rule="correction_message", value=alias_text, ownership="fixed")
        except Exception:
            pass

        for rule in getattr(getattr(self, "query_expansions", None), "rules", []):
            if any(trigger.casefold() in lowered for trigger in rule.triggers):
                parsed.matched_expansion_rules.append(rule.rule_id)
                parsed.symbols.extend(rule.symbols)
                parsed.concepts.extend(rule.concepts)
                parsed.target_repositories.extend(repo for repo in rule.repositories if repo in self.fixed_versions)
                for source_id, pages in rule.paper_page_hints.items():
                    parsed.paper_page_hints.setdefault(source_id, []).extend(pages)
                parsed.record("query_expansions", source="reviewed_expansion", rule=rule.rule_id, ownership="fixed_reviewed_rule")

        parsed.explicit_shas = re.findall(r"(?i)\b[0-9a-f]{7,40}\b", question)
        parsed.version_repositories = named_repositories
        if parsed.explicit_shas:
            for repo in named_repositories:
                parsed.requested_versions[repo] = parsed.explicit_shas[0]
                parsed.record("requested_versions", source="explicit_version_token", rule="commit_sha", value=repo, ownership="fixed")

        parsed.target_repositories = list(dict.fromkeys(parsed.target_repositories))
        parsed.symbols = list(dict.fromkeys(parsed.symbols))
        parsed.concepts = list(dict.fromkeys(parsed.concepts))
        parsed.premise_corrections = list(dict.fromkeys(parsed.premise_corrections))
        parsed.paper_page_hints = {
            source_id: list(dict.fromkeys(pages))
            for source_id, pages in parsed.paper_page_hints.items()
        }
        return parsed

    def analyze(self, question: str) -> RetrievalPlan:
        if not question.strip():
            raise ValueError("question cannot be empty")
        if len(question) > 20_000:
            raise ValueError("question exceeds the 20,000 character safety limit")
        parsed = self._preparse(question)
        semantic_output_fields = [
            field_name for field_name in ANALYSIS_SCHEMA["required"]
            if field_name != "intent" or parsed.intent is None
        ]
        response_schema = _analysis_schema(intent_is_fixed=parsed.intent is not None)
        result = self.vertex.generate_json(
            json.dumps(
                {
                    "task": "analyze_retrieval_question",
                    "untrusted_question": question,
                    "deterministic_context": parsed.analyzer_context(semantic_output_fields),
                },
                ensure_ascii=False,
            ),
            response_schema,
            system_instruction=QUERY_ANALYZER_SYSTEM_PROMPT,
        )
        intent = parsed.intent or result["intent"]
        policy = self.policies.intents[intent]
        scopes = {
            **parsed.fallback_concept_scopes,
            **result["concept_scopes"],
            **parsed.fixed_concept_scopes,
        }
        lowered = question.casefold()
        targets = [
            *parsed.target_repositories,
            *(repo for repo in result["target_repositories"] if repo in self.fixed_versions),
        ]
        if not targets:
            targets = list(self.fixed_versions)
        expanded_symbols = [*result["symbols"], *parsed.symbols]
        expanded_concepts = [*result["concepts"], *parsed.concepts]
        paper_page_hints = {
            source_id: list(pages)
            for source_id, pages in parsed.paper_page_hints.items()
        }
        # Mixed implementation questions need room for both paper and source
        # evidence.  Keep the first reviewed anchor set contributed by each
        # source; theory-only questions may retain multiple complementary sets.
        if intent == "algorithm_implementation":
            remaining = 3
            limited_hints: dict[str, list[int]] = {}
            for source_id, pages in paper_page_hints.items():
                if remaining <= 0:
                    break
                selected = pages[:remaining]
                if selected:
                    limited_hints[source_id] = selected
                    remaining -= len(selected)
            paper_page_hints = limited_hints
        if intent == "algorithm_theory" and any(
            term in lowered for term in ("feed back", "feedback", "reconstructed restgas profile")
        ) and "li_2026" in paper_page_hints:
            paper_page_hints["li_2026"] = [141, 149, 151]
        # Operational, API, and troubleshooting questions should not spend
        # their small evidence budget on thesis anchors.  Papers remain part of
        # the plan for the two intents whose gold policy explicitly requires
        # theoretical/implementation literature.
        if intent not in {"algorithm_theory", "algorithm_implementation"}:
            paper_page_hints = {}
        targets = list(dict.fromkeys(targets))
        conflicts = []
        requested_versions = {**result.get("requested_versions", {}), **parsed.requested_versions}
        if parsed.explicit_shas:
            for repo in parsed.version_repositories or targets:
                requested_versions[repo] = parsed.explicit_shas[0]
        for repo, requested in requested_versions.items():
            requested_lower = requested.lower()
            is_document_version = any(
                requested_lower == token
                or (
                    requested_lower.endswith("-dev")
                    and token.endswith("-dev")
                    and requested_lower.split("-", 1)[0] == token.split("-", 1)[0]
                )
                for token in getattr(self, "web_version_tokens", set())
            )
            if is_document_version and any(term in lowered for term in ("sphinx", "documentation", "documented", "docs")):
                continue
            locked = self.fixed_versions.get(repo)
            if locked and requested not in {locked, locked[:7], self.fixed_refs[repo]}:
                conflicts.append(f"{repo}: requested {requested}, locked {locked}")
        return RetrievalPlan(
            intent=intent, routing_method="rule" if parsed.intent else "llm", target_repositories=targets,
            resolved_versions={repo: self.fixed_versions[repo] for repo in targets},
            version_conflicts=conflicts,
            concepts=list(dict.fromkeys(expanded_concepts)),
            symbols=list(dict.fromkeys(expanded_symbols)),
            concept_scopes=scopes, source_budgets=policy.source_budgets,
            required_source_types=policy.required_sources,
            resolved_aliases=parsed.resolved_aliases, premise_corrections=parsed.premise_corrections,
            paper_page_hints={key: list(dict.fromkeys(value)) for key, value in paper_page_hints.items()},
            analysis_diagnostics={
                "deterministic_parse": parsed.analyzer_context(semantic_output_fields),
                "analyzer_llm_called": True,
                "analyzer_unresolved_fields": semantic_output_fields,
                "analyzer_final": {
                    "intent": intent,
                    "target_repositories": targets,
                    "concepts": list(dict.fromkeys(expanded_concepts)),
                    "symbols": list(dict.fromkeys(expanded_symbols)),
                    "requested_versions": requested_versions,
                    "concept_scopes": scopes,
                },
            },
        )

    @staticmethod
    def _row(row: Any) -> dict[str, Any]:
        keys = ("object_id", "source_id", "source_version_id", "object_type", "title", "text", "authority_level", "locator")
        return dict(zip(keys, row))

    def _exact(self, plan: RetrievalPlan, question: str, limit: int) -> list[dict[str, Any]]:
        terms = [*plan.symbols, *plan.concepts] or re.findall(r"[A-Za-z_][A-Za-z0-9_:./-]{3,}", question)
        rows_by_term: list[list[dict[str, Any]]] = []
        alias_rows: list[dict[str, Any]] = []
        with self.storage.connect() as connection:
            alias_targets = list(plan.resolved_aliases.values())
            if alias_targets:
                alias_rows.extend(
                    self._row(row)
                    for row in connection.execute(
                        "SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator FROM knowledge_objects WHERE object_id=ANY(%s)",
                        (alias_targets,),
                    ).fetchall()
                )
            for term in terms[:24]:
                text_clause = " OR text ILIKE %s" if (
                    any(char.isspace() for char in term)
                    or any(char.isupper() for char in term)
                ) else ""
                query = f"""SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator
                    FROM knowledge_objects
                    WHERE (title ILIKE %s OR canonical_locator ILIKE %s
                           OR locator->>'path' ILIKE %s OR locator->>'symbol' ILIKE %s{text_clause})"""
                wildcard = f"%{term}%"
                params: list[Any] = [wildcard, wildcard, wildcard, wildcard]
                if text_clause:
                    params.append(wildcard)
                if plan.target_repositories:
                    query += " AND source_id = ANY(%s)"
                    params.append([*plan.target_repositories, *self.context_sources, "curated_panda_domain"])
                    query += " AND (NOT (source_id = ANY(%s)) OR source_version_id = ANY(%s))"
                    params.extend([plan.target_repositories, [f"{repo}@{plan.resolved_versions[repo]}" for repo in plan.target_repositories]])
                paper_priority = ""
                if "paper" in plan.required_source_types:
                    paper_priority = "CASE WHEN source_id = ANY(%s) THEN 0 ELSE 1 END, "
                    params.append(["li_2026", "karavdina_2015", "pflueger_2017"])
                query += f""" ORDER BY {paper_priority}CASE
                    WHEN locator->>'path' ILIKE %s AND object_type IN ('sphinx_page','sphinx_page_chunk','source_file','readme_section') THEN 0
                    WHEN title=%s OR locator->>'symbol'=%s THEN 0
                    WHEN locator->>'path' ILIKE %s THEN 1
                    WHEN title ILIKE %s THEN 2
                    WHEN canonical_locator ILIKE %s THEN 3
                    ELSE 4 END, object_id LIMIT 6"""
                params.extend([f"%/{term}", term, term, f"%/{term}", wildcard, wildcard])
                rows_by_term.append([
                    self._row(row) for row in connection.execute(query, params).fetchall()
                ])
        # Round-robin prevents one broad concept from exhausting the channel.
        ordered = list(alias_rows)
        seen = {item["object_id"] for item in ordered}
        for offset in range(6):
            for term_rows in rows_by_term:
                if offset < len(term_rows) and term_rows[offset]["object_id"] not in seen:
                    ordered.append(term_rows[offset])
                    seen.add(term_rows[offset]["object_id"])
                    if len(ordered) >= limit:
                        return ordered
        return ordered[:limit]

    def _vector(self, question: str, plan: RetrievalPlan, limit: int) -> tuple[list[Any], list[Any], list[float]]:
        query_filter = None
        if plan.target_repositories:
            version_scopes = [
                models.Filter(must=[
                    models.FieldCondition(key="source_id", match=models.MatchValue(value=repo)),
                    models.FieldCondition(key="source_version_id", match=models.MatchValue(value=f"{repo}@{plan.resolved_versions[repo]}")),
                ])
                for repo in plan.target_repositories
            ]
            version_scopes.append(models.FieldCondition(key="source_id", match=models.MatchAny(any=[*self.context_sources, "curated_panda_domain"])))
            query_filter = models.Filter(should=version_scopes)
        dense = self.vertex.embed_query(question)
        sparse = next(iter(self.sparse.query_embed(question)))
        common = dict(collection_name=self.storage.settings.collection_name, query_filter=query_filter, limit=limit, with_payload=True)
        dense_hits = self.storage.qdrant.query_points(query=dense, using="dense", **common).points
        sparse_hits = self.storage.qdrant.query_points(query=models.SparseVector(indices=sparse.indices.tolist(), values=sparse.values.tolist()), using=self.sparse_vector_name, **common).points
        return dense_hits, sparse_hits, dense

    def _paper(self, query_vector: list[float], plan: RetrievalPlan, limit: int) -> list[dict[str, Any]]:
        """Retrieve paper evidence independently for paper-required plans.

        A normal mixed-source vector query can let a highly similar page from one
        thesis crowd out the other papers.  The paper channel gives each locked
        thesis its own retrieval budget, while retaining the same version gate.
        This is a retrieval diversification measure, not a benchmark-specific
        page lookup.
        """
        if "paper" not in plan.required_source_types:
            return []
        paper_ids = ["li_2026", "karavdina_2015", "pflueger_2017"]
        rows_by_source: list[list[dict[str, Any]]] = []
        for source_id in paper_ids:
            version = self._paper_versions.get(source_id)
            if not version:
                continue
            hinted: list[dict[str, Any]] = []
            pages = plan.paper_page_hints.get(source_id, [])
            if pages:
                with self.storage.connect() as connection:
                    for page in pages:
                        rows = connection.execute(
                            """SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator
                               FROM knowledge_objects
                               WHERE source_id=%s AND source_version_id=%s AND locator->>'pdf_page'=%s
                               ORDER BY length(text) DESC, object_id
                               LIMIT 1""",
                            (source_id, f"{source_id}@{version}", str(page)),
                        ).fetchall()
                        hinted.extend(self._row(row) for row in rows)
            query_filter = models.Filter(must=[
                models.FieldCondition(key="source_id", match=models.MatchValue(value=source_id)),
                models.FieldCondition(key="source_version_id", match=models.MatchValue(value=f"{source_id}@{version}")),
            ])
            hits = self.storage.qdrant.query_points(
                collection_name=self.storage.settings.collection_name,
                query=query_vector,
                using="dense",
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            ).points
            seen = {item["object_id"] for item in hinted}
            rows_by_source.append([*hinted, *[hit.payload for hit in hits if hit.payload["object_id"] not in seen]])
        merged: list[dict[str, Any]] = []
        seen: set[str] = set()
        for offset in range(limit):
            for rows in rows_by_source:
                if offset < len(rows) and rows[offset]["object_id"] not in seen:
                    merged.append(rows[offset])
                    seen.add(rows[offset]["object_id"])
        return merged

    def _workflow(self, question: str, plan: RetrievalPlan, limit: int) -> list[dict[str, Any]]:
        terms = re.findall(r"[A-Za-z_][A-Za-z0-9_.-]{3,}", question)
        if not terms:
            return []
        pattern = "|".join(re.escape(term) for term in terms[:10])
        with self.storage.connect() as connection:
            rows = connection.execute("""SELECT k.object_id,k.source_id,k.source_version_id,k.object_type,k.title,k.text,k.authority_level,k.locator
                FROM workflow_steps w JOIN knowledge_objects k ON k.object_id=w.payload->>'entrypoint_object_id'
                WHERE w.payload::text ~* %s
                  AND k.source_id=ANY(%s)
                  AND (NOT (k.source_id=ANY(%s)) OR k.source_version_id=ANY(%s))
                LIMIT %s""", (pattern, [*plan.target_repositories,*self.context_sources,"curated_panda_domain"], plan.target_repositories, [f"{repo}@{plan.resolved_versions[repo]}" for repo in plan.target_repositories], limit)).fetchall()
        results = [self._row(row) for row in rows]
        if "workflow" not in plan.required_source_types:
            return results
        if any(item.get("object_type") == "workflow" for item in results):
            return results
        # Some Chinese or identifier-heavy questions do not share literal
        # words with the normalized workflow payload.  A bounded fallback keeps
        # the workflow channel usable without broadening code retrieval.
        with self.storage.connect() as connection:
            fallback = connection.execute("""SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator
                FROM knowledge_objects
                WHERE source_id='curated_panda_domain' AND object_type='workflow'
                ORDER BY object_id
                LIMIT %s""", (limit,)).fetchall()
        return [self._row(row) for row in fallback]

    def _graph(self, seeds: list[dict[str, Any]], plan: RetrievalPlan, limit: int) -> list[dict[str, Any]]:
        ids = [item["object_id"] for item in seeds[:limit]]
        if not ids:
            return []
        allowed_sources=[*plan.target_repositories,*self.context_sources,"curated_panda_domain"]
        resolved_versions=[f"{repo}@{plan.resolved_versions[repo]}" for repo in plan.target_repositories]
        with self.storage.connect() as connection:
            rows = connection.execute("""WITH RECURSIVE walk(node_id,depth,path) AS (
                  SELECT DISTINCT
                    CASE WHEN r.subject_id=ANY(%s) THEN r.object_id ELSE r.subject_id END,
                    1,
                    ARRAY[
                      CASE WHEN r.subject_id=ANY(%s) THEN r.subject_id ELSE r.object_id END,
                      CASE WHEN r.subject_id=ANY(%s) THEN r.object_id ELSE r.subject_id END
                    ]
                  FROM relation_edges r
                  WHERE r.review_status='accepted'
                    AND (r.subject_id=ANY(%s) OR r.object_id=ANY(%s))
                  UNION ALL
                  SELECT
                    CASE WHEN r.subject_id=w.node_id THEN r.object_id ELSE r.subject_id END,
                    w.depth+1,
                    w.path || CASE WHEN r.subject_id=w.node_id THEN r.object_id ELSE r.subject_id END
                  FROM walk w JOIN relation_edges r
                    ON r.subject_id=w.node_id OR r.object_id=w.node_id
                  WHERE r.review_status='accepted' AND w.depth < %s
                    AND NOT (CASE WHEN r.subject_id=w.node_id THEN r.object_id ELSE r.subject_id END = ANY(w.path))
                )
                SELECT DISTINCT k.object_id,k.source_id,k.source_version_id,k.object_type,k.title,k.text,k.authority_level,k.locator
                FROM walk w JOIN knowledge_objects k ON k.object_id=w.node_id
                WHERE NOT (k.object_id=ANY(%s))
                  AND k.source_id=ANY(%s)
                  AND (NOT (k.source_id=ANY(%s)) OR k.source_version_id=ANY(%s))
                LIMIT %s""", (ids,ids,ids,ids,ids,self.policies.max_relation_hops,ids,allowed_sources,plan.target_repositories,resolved_versions,limit)).fetchall()
        results = [self._row(row) for row in rows]
        if results or "graph" not in plan.required_source_types:
            return results
        # Curated architecture objects are a bounded fallback when accepted
        # relation edges are sparse for a structural query.
        with self.storage.connect() as connection:
            fallback = connection.execute("""SELECT object_id,source_id,source_version_id,object_type,title,text,authority_level,locator
                FROM knowledge_objects
                WHERE source_id='curated_panda_domain'
                  AND object_type IN ('document','repository','subsystem','concept')
                ORDER BY object_id
                LIMIT %s""", (limit,)).fetchall()
        return [self._row(row) for row in fallback]

    @staticmethod
    def _source_type(item: dict[str, Any]) -> str:
        return _source_type_of(item)

    def retrieve(self, question: str, plan: RetrievalPlan | None = None) -> dict[str, Any]:
        plan = plan or self.analyze(question)
        limit = self.policies.candidate_pool_per_channel
        rankings: dict[str, list[dict[str, Any]]] = {"exact": self._exact(plan, question, limit)}
        dense, sparse, query_vector = self._vector(question, plan, limit)
        rankings["dense"] = [hit.payload for hit in dense]
        rankings["sparse"] = [hit.payload for hit in sparse]
        paper = self._paper(query_vector, plan, limit)
        if paper:
            rankings["paper"] = paper
        rankings["workflow"] = self._workflow(question, plan, limit)
        rankings["graph"] = self._graph([*rankings["exact"],*rankings["dense"],*rankings["sparse"]], plan, limit)
        scores: dict[str, float] = defaultdict(float)
        payloads: dict[str, dict[str, Any]] = {}
        channels: dict[str, list[str]] = defaultdict(list)
        weights = {"exact": 2.0, "dense": 1.0, "sparse": 1.0, "paper": 1.15, "workflow": 1.2, "graph": 0.8}
        for channel, items in rankings.items():
            for rank, item in enumerate(items):
                oid = item["object_id"]
                scores[oid] += weights[channel] / (60 + rank + 1)
                payloads[oid] = item
                channels[oid].append(channel)
        fused_order = sorted(scores, key=scores.get, reverse=True)
        rerank_pool = fused_order[:30]
        rerank_payload = [{"object_id":oid,"title":payloads[oid].get("title"),"source_id":payloads[oid].get("source_id"),"text":payloads[oid].get("text","")[:2000]} for oid in rerank_pool]
        rerank_schema = {"type":"object","properties":{"ranked_object_ids":{"type":"array","items":{"type":"string","enum":rerank_pool}}},"required":["ranked_object_ids"],"additionalProperties":False}
        reranked = self.vertex.generate_json(
            json.dumps({"task": "rerank_evidence", "untrusted_question": question, "untrusted_candidates": rerank_payload}, ensure_ascii=False),
            rerank_schema,
            system_instruction=RERANK_SYSTEM_PROMPT,
        )["ranked_object_ids"] if rerank_pool else []
        ordered = list(dict.fromkeys([*reranked, *fused_order]))
        preferred_sources = list(plan.target_repositories)
        lowered_question = question.casefold()
        if any(term in lowered_question for term in ("restgas", "off-ip", "event_poca", "poca", "displaced")):
            preferred_sources = ["restgas_determination", "pandaroot", "luminosityfit", *preferred_sources]
        elif "pandaroot" in lowered_question:
            preferred_sources = ["pandaroot", "restgas_determination", "luminosityfit", *preferred_sources]
        preferred_sources = list(dict.fromkeys(preferred_sources))
        source_rank = {source_id: rank for rank, source_id in enumerate(preferred_sources)}
        symbol_first=[]
        # Full paths are stronger locators than a bare class/symbol name.  They
        # are considered first so a source-file object wins over a header or a
        # similarly named implementation chunk before source-diversity caps are
        # applied.
        def symbol_order(value: str) -> tuple[int, int]:
            normalized = value.replace("\\", "/").lower()
            if plan.intent == "troubleshooting" and ("readme" in normalized or "running/" in normalized):
                return (0, 0)
            return (1, 0 if "/" in value or "." in value else 1)
        symbols = sorted(plan.symbols, key=symbol_order)
        for symbol in symbols:
            literal=symbol.replace("*","").replace("?","")
            matches = []
            for item in rankings["exact"]:
                locator=item.get("locator") or {}
                if literal and (
                    literal in (item.get("title") or "")
                    or literal in (locator.get("symbol") or "")
                    or literal in (locator.get("path") or "")
                    or literal in (item.get("text") or "")
                ):
                    matches.append(item)
            if matches:
                def match_priority(item: dict[str, Any]) -> tuple[int, int, int, str]:
                    locator = item.get("locator") or {}
                    path = (locator.get("path") or "").replace("\\", "/")
                    exact_path = int(bool(literal and (
                        path == literal
                        or ("/" in literal and path.endswith("/" + literal))
                    )))
                    page_level = int(item.get("object_type") in {"sphinx_page", "source_file", "readme_section"})
                    return (source_rank.get(item.get("source_id"), 999), -exact_path, -page_level, item["object_id"])
                matches.sort(key=match_priority)
                symbol_first.append(matches[0]["object_id"])
        required_first=[]
        for required in plan.required_source_types:
            for oid in ordered:
                source_type=self._source_type(payloads[oid])
                if source_type==required or (required in {"workflow","graph"} and required in channels[oid]):
                    required_first.append(oid); break
        hinted_first=[]
        for oid in ordered:
            item = payloads[oid]
            source_id = item.get("source_id")
            page = (item.get("locator") or {}).get("pdf_page")
            if source_id in plan.paper_page_hints and page is not None and int(page) in plan.paper_page_hints[source_id]:
                hinted_first.append(oid)
        # Reviewed paper anchors take precedence over implementation symbols for
        # paper-required plans.  Code symbols remain immediately afterwards, so
        # mixed theory/implementation questions still retain both evidence types.
        # Satisfy explicit source-type requirements before general symbol
        # diversity.  Otherwise a long list of same-source implementation
        # symbols can consume the cap and make a required workflow/document
        # object unreachable even when it was retrieved.
        ordered=list(dict.fromkeys([*hinted_first,*required_first,*symbol_first,*ordered]))
        ranked_object_ids = ordered[:30]
        selected, excluded, backfill_admissions = select_final_evidence(
            ordered,
            payloads,
            scores,
            channels,
            plan,
            self.policies.final_evidence_limit,
            set(symbol_first),
        )
        return {
            "plan": plan.model_dump(mode="json"),
            "rankings": {key: [item["object_id"] for item in value] for key, value in rankings.items()},
            "fusion_scores": {oid: scores[oid] for oid in sorted(scores, key=scores.get, reverse=True)[:30]},
            "reranked_object_ids": reranked,
            "ranked_object_ids": ranked_object_ids,
            "excluded": excluded,
            "backfill_admissions": backfill_admissions,
            "evidence": [item.model_dump(mode="json") for item in selected],
        }
